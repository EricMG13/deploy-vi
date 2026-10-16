"""Real exported-runtime installation; destinations and source bytes stay protected."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from test_runtime import build, git, invoke

from rbotlib.rules import RBOT_ROOT

REPO = RBOT_ROOT.parent


@pytest.fixture(scope="module")
def export(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("installer-export") / "rbot"
    build(REPO, "HEAD", root)
    return root


@pytest.fixture
def source(export: Path, tmp_path: Path) -> Path:
    root = tmp_path / "transferred package" / "rbot"
    shutil.copytree(export, root)
    return root


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and not p.is_symlink() and "__pycache__" not in p.parts
    }


def install(source: Path, destination: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(REPO / "install.sh"), str(source), str(destination), sys.executable],
        cwd=source.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_real_quoted_install_and_repeat(source: Path, tmp_path: Path) -> None:
    before = snapshot(source)
    destination = tmp_path / "personal skills with spaces" / "rbot"
    for _ in range(2):
        result = install(source, destination)
        assert result.returncode == 0, result.stderr
        assert snapshot(destination) == before
    assert snapshot(source) == before
    assert set(destination.parent.iterdir()) == {destination}
    metadata = json.loads(before["runtime.json"])
    assert invoke(destination, "version").stdout == f"rbot 0.1.0 {metadata['git_sha']}\n"
    checked = invoke(destination, "check")
    assert checked.returncode == 0 and checked.stdout == "0 problem(s)\n"
    assert not any(
        part in path.split("/")
        for path in before
        for part in ("tests", "reference", ".git", "proxy", "corpus-runs")
    )


@pytest.mark.parametrize("change", ["missing", "malformed", "duplicate", "version", "hash"])
def test_invalid_metadata_refuses_before_destination(
    source: Path, tmp_path: Path, change: str
) -> None:
    path = source / "runtime.json"
    data = json.loads(path.read_bytes())
    if change == "missing":
        path.unlink()
    elif change == "malformed":
        path.write_text("{")
    elif change == "duplicate":
        path.write_text('{"schema": 1, "schema": 2}')
    else:
        if change == "version":
            data["version"] = "conflicting"
        else:
            data["files"]["canon.md"]["sha256"] = "0" * 64
        path.write_text(json.dumps(data))
    before = snapshot(source)
    destination = tmp_path / "fresh parent" / "rbot"
    result = install(source, destination)
    assert result.returncode == 1 and "error: install:" in result.stderr
    assert not destination.parent.exists() and snapshot(source) == before


@pytest.mark.parametrize("target", ["scripts/rbot.py", "scripts/rbotlib/cli.py", "extra.txt"])
def test_unverified_source_never_executes(source: Path, tmp_path: Path, target: str) -> None:
    marker = tmp_path / "payload executed"
    (source / target).write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
    before = snapshot(source)
    destination = tmp_path / "skills" / "rbot"
    result = install(source, destination)
    assert result.returncode == 1 and not destination.exists() and not marker.exists()
    assert snapshot(source) == before


@pytest.mark.parametrize("target", ["canon.md", "runtime.json", "modules", "__pycache__"])
def test_source_links_refuse(source: Path, tmp_path: Path, target: str) -> None:
    protected = tmp_path / "private source"
    protected.write_bytes(b"preserve")
    path = source / target
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
    path.symlink_to(protected)
    destination = tmp_path / "skills" / "rbot"
    result = install(source, destination)
    assert result.returncode == 1 and "unsafe" in result.stderr
    assert not destination.exists() and path.is_symlink()
    assert protected.read_bytes() == b"preserve"


def test_special_source_refuses_before_read(source: Path, tmp_path: Path) -> None:
    os.mkfifo(source / "blocked fifo")
    result = install(source, tmp_path / "rbot")
    assert result.returncode == 1 and "unsafe" in result.stderr


@pytest.mark.parametrize("kind", ["same", "child", "ancestor", "file", "empty", "changed", "link"])
def test_destination_collisions_preserve_sources(source: Path, tmp_path: Path, kind: str) -> None:
    destination = tmp_path / "destination"
    if kind == "same":
        destination = source
    elif kind == "child":
        destination = source / "child"
    elif kind == "ancestor":
        destination = source.parent
    elif kind == "file":
        destination.write_bytes(b"keep existing file")
    elif kind == "link":
        destination.symlink_to(source, target_is_directory=True)
    elif kind == "changed":
        shutil.copytree(source, destination)
        (destination / "canon.md").write_bytes(b"keep my edited runtime")
    else:
        destination.mkdir()
    before = snapshot(source)
    old = (
        snapshot(destination)
        if destination.is_dir()
        else (destination.read_bytes() if destination.exists() else None)
    )
    result = install(source, destination)
    assert result.returncode == 1 and snapshot(source) == before
    current = (
        snapshot(destination)
        if destination.is_dir()
        else (destination.read_bytes() if destination.exists() else None)
    )
    assert current == old
    assert not (source / "child").exists()


@pytest.mark.parametrize("side", ["source", "destination"])
def test_linked_ancestor_refuses(source: Path, tmp_path: Path, side: str) -> None:
    alias = tmp_path / "alias"
    alias.symlink_to(source.parent, target_is_directory=True)
    selected = alias / source.name if side == "source" else source
    destination = alias / "new" if side == "destination" else tmp_path / "rbot"
    result = install(selected, destination)
    assert result.returncode == 1 and "unsafe" in result.stderr
    assert not destination.exists()


def test_lock_collision_preserved(source: Path, tmp_path: Path) -> None:
    lock = tmp_path / ".rbot-install.lock"
    lock.mkdir()
    (lock / "owner").write_bytes(b"another installer")
    result = install(source, tmp_path / "rbot")
    assert result.returncode == 1 and not (tmp_path / "rbot").exists()
    assert (lock / "owner").read_bytes() == b"another installer"


def payload() -> str:
    shell = (REPO / "install.sh").read_text().split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
    powershell = (REPO / "install.ps1").read_text().split("@'\n", 1)[1].split("\n'@", 1)[0]
    assert powershell == shell
    return shell


def test_corrupt_staging_refuses_before_publication(source: Path, tmp_path: Path) -> None:
    program = """
from pathlib import Path
original = Path.write_bytes
def corrupt(path, data):
    if path.name == 'canon.md' and '.rbot-install-' in str(path):
        data = b'interrupted/corrupt copy'
    return original(path, data)
Path.write_bytes = corrupt
""" + payload()
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(source), str(tmp_path / "rbot")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1 and not (tmp_path / "rbot").exists()
    assert not list(tmp_path.glob(".rbot-install*"))


def test_destination_appearing_before_publication_preserved(source: Path, tmp_path: Path) -> None:
    program = """
import runpy
from pathlib import Path
original = runpy.run_path
def load(path):
    module = original(path)
    verifier = module['verify']
    def verify(root):
        result = verifier(root)
        if root.name.startswith('.rbot-install-'):
            Path(__import__('sys').argv[2]).mkdir()
        return result
    module['verify'] = verify
    return module
runpy.run_path = load
""" + payload()
    destination = tmp_path / "rbot"
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(source), str(destination)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1 and "appeared" in result.stderr
    assert destination.is_dir() and list(destination.iterdir()) == []
    assert not list(tmp_path.glob(".rbot-install*"))


def test_transfer_defaults_use_package_not_cwd(source: Path, tmp_path: Path) -> None:
    shutil.copy2(REPO / "install.sh", source.parent / "install.sh")
    fake_home = tmp_path / "temporary home"
    fake_home.mkdir()
    environment = dict(os.environ, HOME=str(fake_home))
    result = subprocess.run(
        ["bash", str(source.parent / "install.sh")],
        cwd=fake_home,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert snapshot(fake_home / ".copilot/skills/rbot") == snapshot(source)
    assert "pip" not in payload()


def test_installed_imports_never_read_repository(source: Path, tmp_path: Path) -> None:
    destination = tmp_path / "rbot"
    assert install(source, destination).returncode == 0
    program = """
import sys
sys.path.insert(0, sys.argv[1])
def audit(event, args):
    if event == 'open' and isinstance(args[0], str) and any(
        args[0].startswith(sys.argv[2] + '/' + name)
        for name in ('rbot', 'scripts', 'tests', '.git', 'pyproject.toml')
    ):
        raise RuntimeError('repository read')
sys.addaudithook(audit)
from rbotlib.cli import main
sys.exit(main(['version']))
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(destination / "scripts"), str(REPO)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0 and result.stdout.startswith("rbot 0.1.0 ")


def reproven(source: Path, tmp_path: Path, mutate: Callable[[Path], None]) -> tuple[Path, Path]:
    """Re-commit the exported tree after `mutate(rbot_folder)`; return the new export and target."""
    repo = tmp_path / "owned malformed repository"
    shutil.copytree(source, repo / "rbot")
    (repo / "rbot/runtime.json").unlink()
    mutate(repo / "rbot")
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
        "Owned incomplete runtime fixture; no provider claim",
    )
    export = tmp_path / "reproven export"
    build(repo, "HEAD", export)
    return export, tmp_path / "rbot"


@pytest.mark.parametrize("change", ["missing-contract", "missing-cli", "private-source"])
def test_reproven_incomplete_or_nonruntime_export_refuses(
    source: Path, tmp_path: Path, change: str
) -> None:
    def mutate(root: Path) -> None:
        if change == "missing-contract":
            (root / "modules/CP-6/contract.json").unlink()
        elif change == "missing-cli":
            (root / "scripts/rbotlib/cli.py").unlink()
        else:
            (root / "private-source.xlsx").write_bytes(b"owned private-data sentinel")

    malformed, destination = reproven(source, tmp_path, mutate)
    before = snapshot(malformed)
    result = install(malformed, destination)
    assert result.returncode == 1 and not destination.exists()
    assert snapshot(malformed) == before


@pytest.mark.parametrize(
    ("name", "accepted"),
    [
        ("report/extra.js", True),
        ("report/fonts/inter-400.woff2", True),
        ("report/page.html", False),
        ("report/inter-400.woff2", False),
        ("report/fonts/inter.css", False),
        ("report/deep/extra.css", False),
    ],
)
def test_install_accepts_report_assets_and_refuses_other_extensions(
    source: Path, tmp_path: Path, name: str, accepted: bool
) -> None:
    def mutate(root: Path) -> None:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_bytes(b"asset")

    export, destination = reproven(source, tmp_path, mutate)
    result = install(export, destination)
    assert (result.returncode == 0) == accepted, result.stderr
    assert destination.exists() == accepted


def test_valid_different_destination_refuses(source: Path, tmp_path: Path) -> None:
    def mutate(root: Path) -> None:
        (root / "report/extra.js").write_bytes(b"asset")

    export, destination = reproven(source, tmp_path, mutate)
    installed = install(export, destination)
    assert installed.returncode == 0, installed.stderr
    before = snapshot(destination)
    assert before["runtime.json"] != (source / "runtime.json").read_bytes()
    result = install(source, destination)
    assert result.returncode == 1 and "destination differs" in result.stderr
    assert snapshot(destination) == before


def test_simultaneous_installers_preserve_complete_result(source: Path, tmp_path: Path) -> None:
    destination = tmp_path / "rbot"
    before = snapshot(source)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: install(source, destination), range(2)))
    assert any(result.returncode == 0 for result in results)
    assert all(result.returncode in (0, 1) for result in results)
    assert snapshot(destination) == before == snapshot(source)
    assert not list(tmp_path.glob(".rbot-install*"))


@pytest.mark.parametrize("name", ["rbot", "modules"])
def test_reparse_attribute_guard_without_windows_claim(
    source: Path, tmp_path: Path, name: str
) -> None:
    program = f"""
from pathlib import Path
from types import SimpleNamespace
original = Path.lstat
def reparse(path):
    result = original(path)
    if path.name == {name!r}:
        return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
    return result
Path.lstat = reparse
""" + payload()
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(source), str(tmp_path / "destination")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1 and "unsafe" in result.stderr
    assert not (tmp_path / "destination").exists()


def test_oversized_entry_refuses_before_read(source: Path, tmp_path: Path) -> None:
    (source / "scripts/rbot.py").write_bytes(b"x" * 2_000_001)
    program = """
from pathlib import Path
original = Path.read_bytes
def limited(path):
    if path.name == 'rbot.py' and path.stat().st_size > 2_000_000:
        raise RuntimeError('oversized entry read before refusal')
    return original(path)
Path.read_bytes = limited
""" + payload()
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(source), str(tmp_path / "destination")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1 and "error: install: oversized entry" in result.stderr
    assert "before refusal" not in result.stderr and not (tmp_path / "destination").exists()
