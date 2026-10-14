"""Immutable export and installed-only provenance, refusal and source preservation."""

from __future__ import annotations

import json
import marshal
import os
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from rbot import METADATA, files, git_hash, verify
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def build(repo: Path, commit: str, output: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "bash",
            str(RBOT_ROOT.parent / "scripts/build_runtime.sh"),
            sys.executable,
            str(repo),
            commit,
            str(output),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    return metadata(output)


def test_unstamped_version_refuses(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 1
    output = capsys.readouterr()
    assert output.out == "" and "runtime provenance" in output.err


@pytest.fixture(scope="module")
def committed(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    repo = tmp_path_factory.mktemp("runtime-source")
    shutil.copytree(RBOT_ROOT, repo / "rbot", ignore=shutil.ignore_patterns("__pycache__"))
    git(repo, "init", "-q")
    git(repo, "add", "rbot")
    git(
        repo,
        "-c",
        "user.name=Eric Guei",
        "-c",
        "user.email=ericsea1990@googlemail.com",
        "commit",
        "-qm",
        "Committed runtime fixture; no provider claim",
    )
    sha = git(repo, "rev-parse", "HEAD").decode().strip()
    return repo, sha


@pytest.fixture
def installed(committed: tuple[Path, str], tmp_path: Path) -> Path:
    root = tmp_path / "installed rbot"
    build(*committed, root)
    return root


def invoke(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, str(root / "scripts/rbot.py"), *argv],
        cwd=root.parent,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )


def metadata(root: Path) -> dict[str, Any]:
    value: dict[str, Any] = json.loads((root / METADATA).read_bytes())
    return value


def save(root: Path, data: dict[str, Any]) -> None:
    (root / METADATA).write_text(json.dumps(data))


def test_installed_only_version_and_contracts(
    installed: Path, committed: tuple[Path, str], tmp_path: Path
) -> None:
    data, _ = verify(installed)
    assert data["git_sha"] == committed[1]
    assert data["source_tree"] == git(committed[0], "rev-parse", "HEAD^{tree}").decode().strip()
    assert data["runtime_tree"] == git(committed[0], "rev-parse", "HEAD:rbot").decode().strip()
    assert invoke(installed, "version").stdout == f"rbot 0.1.0 {committed[1]}\n"
    checked = invoke(installed, "check")
    assert checked.returncode == 0 and checked.stdout == "0 problem(s)\n"
    forbidden = ("tests/", "reference/", ".git", "pyproject", "proxy", "build_runtime")
    assert not any(part in name for name in data["files"] for part in forbidden)
    assert set(p.name for p in installed.parent.iterdir()) == {installed.name}
    # Exact copies remain usable at a quoted path, without any repository files.
    copied = tmp_path / "personal skills" / "rbot"
    shutil.copytree(installed, copied)
    assert invoke(copied, "version").returncode == 0
    assert metadata(copied) == data


def test_no_repository_reads_or_imports(installed: Path, committed: tuple[Path, str]) -> None:
    forbidden = [str(committed[0]), str(RBOT_ROOT), str(RBOT_ROOT.parent / "tests")]
    program = """
import sys
sys.path.insert(0, sys.argv[1])
denied = sys.argv[2:]
def audit(event, args):
    if event == 'open' and isinstance(args[0], str) and any(
        args[0].startswith(p) for p in denied
    ):
        raise RuntimeError('repository read: ' + args[0])
sys.addaudithook(audit)
from rbotlib.cli import main
sys.exit(main(['version']))
"""
    result = subprocess.run(
        [sys.executable, "-B", "-I", "-c", program, str(installed / "scripts"), *forbidden],
        cwd=installed.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"rbot 0.1.0 {committed[1]}\n"


@pytest.mark.parametrize("key", ["version", "git_sha", "source_tree", "runtime_tree", "schema"])
def test_conflicting_provenance_refuses(installed: Path, key: str) -> None:
    data = metadata(installed)
    data[key] = "conflict"
    save(installed, data)
    result = invoke(installed, "version")
    assert result.returncode == 1 and not result.stdout
    assert "runtime provenance" in result.stderr


def test_source_root_must_bind_actual_runtime_tree(installed: Path) -> None:
    data = metadata(installed)
    root = bytes.fromhex(data["root_object"])
    old_tree = data["source_tree"]
    root = root.replace(bytes.fromhex(data["runtime_tree"]), bytes(20))
    data["source_tree"] = git_hash("tree", root)
    data["root_object"] = root.hex()
    commit = bytes.fromhex(data["commit_object"]).replace(
        f"tree {old_tree}".encode(), f"tree {data['source_tree']}".encode()
    )
    data["commit_object"] = commit.hex()
    data["git_sha"] = git_hash("commit", commit)
    save(installed, data)
    with pytest.raises(ValueError, match="source root does not bind"):
        verify(installed)


@pytest.mark.parametrize("raw", [b"", b"{", b"[]", b"null", b'{"schema":1,"schema":2}', b"\xff"])
def test_corrupt_metadata_refuses(installed: Path, raw: bytes) -> None:
    (installed / METADATA).write_bytes(raw)
    result = invoke(installed, "version")
    assert result.returncode == 1 and not result.stdout
    assert "runtime provenance" in result.stderr and "Traceback" not in result.stderr


@pytest.mark.parametrize("change", ["missing", "extra", "altered", "metadata-missing", "manifest"])
def test_changed_installed_files_refuse(installed: Path, change: str) -> None:
    path = installed / "canon.md"
    if change == "missing":
        path.unlink()
    elif change == "extra":
        (installed / "untracked.txt").write_text("unexpected")
    elif change == "altered":
        path.write_text("altered")
    elif change == "metadata-missing":
        (installed / METADATA).unlink()
    else:
        data = metadata(installed)
        data["files"]["canon.md"]["sha256"] = "0" * 64
        save(installed, data)
    before = files(installed)
    result = invoke(installed, "version")
    assert result.returncode == 1 and not result.stdout
    assert files(installed) == before


@pytest.mark.parametrize("target", ["canon.md", "runtime.json", "modules", "__pycache__"])
def test_linked_files_and_directories_refuse_without_source_reads(
    installed: Path, target: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "protected-source"
    source.write_bytes(b"do not read or write")
    path = installed / target
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
    path.symlink_to(source)
    original = Path.read_bytes

    def read(selected: Path) -> bytes:
        assert selected != path and selected != source
        return original(selected)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", read)
        with pytest.raises(ValueError, match=r"unsafe|regular"):
            verify(installed)
    assert source.read_bytes() == b"do not read or write"


def test_special_file_refuses_before_read(installed: Path) -> None:
    (installed / "canon.md").unlink()
    os.mkfifo(installed / "canon.md")
    with pytest.raises(ValueError, match="unsafe"):
        verify(installed)


def test_alternate_root_cannot_claim_other_code(installed: Path) -> None:
    other = installed.parent / "other runtime"
    shutil.copytree(installed, other)
    result = invoke(installed, "--root", str(other), "version")
    assert result.returncode == 1 and "executing installed runtime" in result.stderr


@pytest.mark.parametrize("module", ["inventory", "calc/__init__"])
@pytest.mark.parametrize("legacy", [False, True])
def test_poisoned_cache_cannot_replace_executing_source(
    installed: Path, module: str, legacy: bool
) -> None:
    source = installed / f"scripts/rbotlib/{module}.py"
    cache_path = py_compile.compile(str(source), doraise=True)
    assert cache_path is not None
    cached = Path(cache_path)
    payload = compile(
        "print('unverified cache executed'); raise SystemExit(0)", str(source), "exec"
    )
    cached.write_bytes(cached.read_bytes()[:16] + marshal.dumps(payload))
    if legacy:
        cached.rename(source.with_suffix(".pyc"))
        source.unlink()
    argv = ["version"] if module == "runtime" else [module.split("/")[0], "--help"]
    for _ in range(2):
        result = invoke(installed, *argv)
        assert result.returncode == (1 if legacy else 0)
        assert not result.stdout if legacy else "rbot" in result.stdout
        assert "unverified cache executed" not in result.stdout


def test_extra_python_cannot_shadow_stdlib_before_refusal(installed: Path) -> None:
    (installed / "scripts/pathlib.py").write_text(
        "print('unverified shadow executed'); raise SystemExit(0)\n"
    )
    result = invoke(installed, "version")
    assert result.returncode == 1 and not result.stdout
    assert "missing or extra installed files" in result.stderr


@pytest.mark.parametrize("module", ["cli", "__init__", "inventory"])
@pytest.mark.parametrize("argv", [["version"], ["inventory", "--help"]])
def test_package_source_is_bound_before_execution(
    installed: Path, module: str, argv: list[str]
) -> None:
    path = installed / f"scripts/rbotlib/{module}.py"
    path.write_text("print('unverified package source executed'); raise SystemExit(0)\n")
    result = invoke(installed, *argv)
    assert result.returncode == 1 and not result.stdout


def test_build_ignores_uncommitted_bytes_and_preserves_sources(
    committed: tuple[Path, str], tmp_path: Path
) -> None:
    repo, sha = committed
    source = repo / "rbot/canon.md"
    original = source.read_bytes()
    try:
        source.write_bytes(b"uncommitted bytes never belong to the old SHA")
        data = build(repo, sha, tmp_path / "export")
        assert (tmp_path / "export/canon.md").read_bytes() == original
        assert data["git_sha"] == sha
        assert source.read_bytes() != original
    finally:
        source.write_bytes(original)


@pytest.mark.parametrize("destination", ["repo", "subdir", "existing", "link"])
def test_build_guard_preserves_existing_and_source_paths(
    committed: tuple[Path, str], tmp_path: Path, destination: str
) -> None:
    repo, sha = committed
    protected = tmp_path / "protected"
    protected.mkdir()
    (protected / "source.txt").write_text("keep")
    if destination in ("repo", "subdir"):
        target = repo / "rbot/new-build"
    elif destination == "link":
        target = tmp_path / "alias"
        target.symlink_to(protected)
    else:
        target = protected
    with pytest.raises(ValueError, match="fresh directory outside"):
        build(repo / "rbot" if destination == "subdir" else repo, sha, target)
    assert (protected / "source.txt").read_text() == "keep"
    assert not (repo / "rbot/new-build").exists()


def test_runtime_prompt_budget_and_actual_menu(installed: Path) -> None:
    data = json.loads((installed / "catalog.json").read_bytes())
    budget = data["size_budget_bytes"]
    assert budget == 51200
    for path in [
        installed / "SKILL.md",
        installed / "canon.md",
        *installed.glob("modules/*/MODULE.md"),
    ]:
        assert len(path.read_bytes()) <= budget
    assert [(p["id"], list(p["depths"])) for p in data["pathways"]] == [
        ("FULL_CREDIT_ASSESSMENT", ["full"])
    ]


def test_installed_controller_outside_repo_preserves_source(
    installed: Path, tmp_path: Path
) -> None:
    # An unrelated enclosing repository must never provide the installed identity.
    (installed.parent / ".git").mkdir()
    (installed.parent / "pyproject.toml").write_text('version = "wrong"')
    pack = tmp_path / "source pack"
    pack.mkdir()
    source = pack / "issuer.txt"
    source.write_text("Issuer ACME. FY2025 financial evidence. No fabricated figure.\n")
    original = source.read_bytes()
    created = invoke(installed, "new-run", "--pack", str(pack), "--issuer", "ACME")
    assert created.returncode == 0, created.stderr
    run = Path(created.stdout.strip())
    for command in ("inventory", "prepare"):
        result = invoke(installed, command, "--run", str(run))
        assert result.returncode == 0, result.stdout + result.stderr
    selected = invoke(installed, "next", "--run", str(run))
    assert selected.returncode == 0, selected.stderr
    choice = json.loads(selected.stdout)
    assert choice == dict(step="CP-0", kind="module", command=None, dispatch="dispatch/CP-0.md")
    dispatch = (run / choice["dispatch"]).read_bytes()
    assert str(installed).encode() in dispatch and str(RBOT_ROOT).encode() not in dispatch
    assert len(dispatch) <= 51200
    assert not (run / "handoffs/CP-0.md").exists()
    record = json.loads((run / "run-state.json").read_bytes())
    assert record["rbot_version"] == metadata(installed)["version"]
    assert record["steps"]["CP-0"]["attempts"] == 0
    assert record["approval"] is None
    assert record["report"] == dict(written_at=None, html_sha256=None, md_sha256=None)
    assert source.read_bytes() == original
    assert invoke(installed, "version").returncode == 0
