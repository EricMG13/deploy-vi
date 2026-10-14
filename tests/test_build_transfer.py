"""Transfer builder: offline, with a temp git repo, temp lock, local wheels and temp registry."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

import build_transfer
from rbotlib.rules import RBOT_ROOT

REAL = Path(__file__).resolve().parents[1]
WHEEL = {"pypdf-1.0-py3-none-any.whl": b"pypdf bytes", "openpyxl-1.0-py3-none-any.whl": b"opx"}


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
    return done.stdout.decode().strip()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _lock(corrupt: bool = False) -> str:
    def pkg(name: str, deps: str = "") -> str:
        wheel = f"{name}-1.0-py3-none-any.whl"
        digest = "0" * 64 if corrupt and name == "pypdf" else _sha(WHEEL[wheel])
        return (
            f'[[package]]\nname = "{name}"\nversion = "1.0"\n{deps}'
            f'wheels = [{{ url = "https://example.invalid/{wheel}", hash = "sha256:{digest}" }}]\n'
        )

    return pkg("openpyxl") + pkg("pypdf")


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "src"
    shutil.copytree(RBOT_ROOT, root / "rbot", ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("install.sh", "install.ps1", "docs/acceptance/work-pc-checklist.md"):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REAL / name, root / name)
    shutil.copytree(REAL / "spike", root / "spike")
    pack = root / "tests/corpus/synthetic/czr-2026q2-primary"
    pack.mkdir(parents=True)
    (pack / "a.txt").write_text("registered\n")
    registry = {
        "schema": "rbot-corpus/1",
        "roots": {"synthetic": "tests/corpus/synthetic"},
        "packs": [
            {
                "id": "czr-2026q2-primary",
                "root": "synthetic",
                "path": "czr-2026q2-primary",
                "issuer": {"id": "CZR", "name": "Caesars"},
                "period": "2026Q2",
                "pathways": [],
                "files": [
                    {
                        "path": "a.txt",
                        "sha256": _sha(b"registered\n"),
                        "class": "issuer",
                        "document_type": "Note",
                        "entity": "CZR",
                    }
                ],
            }
        ],
    }
    (root / "tests/corpus/corpus.json").write_text(json.dumps(registry))
    _git(root, "init", "-q")
    _git(root, "add", ".")
    _git(root, "-c", "user.name=T", "-c", "user.email=t@example.invalid", "commit", "-qm", "rc")
    return root, _git(root, "rev-parse", "HEAD")


@pytest.fixture
def wheels(tmp_path: Path) -> Path:
    folder = tmp_path / "wheels"
    folder.mkdir()
    for name, data in WHEEL.items():
        (folder / name).write_bytes(data)
    return folder


def _args(repo: tuple[Path, str], tmp_path: Path, wheels: Path, out: str = "out") -> list[str]:
    lock = tmp_path / "uv.lock"
    lock.write_text(_lock())
    return [
        *("--repo", str(repo[0]), "--commit", repo[1], "--out", str(tmp_path / out)),
        *("--wheels", str(wheels), "--lock", str(lock)),
        *("--registry", str(repo[0] / "tests/corpus/corpus.json")),
    ]


def test_manifest_round_trip(
    repo: tuple[Path, str],
    wheels: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RBOT_CORPUS_ROOTS", raising=False)
    assert build_transfer.main(_args(repo, tmp_path, wheels)) == 0
    archive = tmp_path / f"out/rbot-v1-{repo[1][:12]}.zip"
    assert f"sha256 {_sha(archive.read_bytes())}" in capsys.readouterr().out
    with zipfile.ZipFile(archive) as zf:
        manifest = json.loads(zf.read("MANIFEST.json"))
        names = set(zf.namelist())
        assert manifest["commit"] == repo[1]
        assert manifest["runtime_tree"] == _git(repo[0], "rev-parse", f"{repo[1]}:rbot")
        assert set(manifest["files"]) == names - {"MANIFEST.json"}
        assert all(_sha(zf.read(n)) == h for n, h in manifest["files"].items())
        assert {
            "install.sh",
            "install.ps1",
            "CHECKLIST.md",
            "evidence/checklist.txt",
            "rbot/runtime.json",
            "spike/rbot-probe/SKILL.md",
            "spike/probe-workspace/probe/input.txt",
            "pack/czr-2026q2-primary/a.txt",
            "wheels/pypdf-1.0-py3-none-any.whl",
        } <= names
        blank = zf.read("evidence/checklist.txt").decode().splitlines()
        assert "package_sha256:" in blank and "claude_resume_ok:" in blank
        assert not any(line.startswith("gpt_resume") for line in blank)
        assert all(line.endswith(":") for line in blank)


def test_hash_mismatch_refuses(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _args(repo, tmp_path, wheels)
    (tmp_path / "uv.lock").write_text(_lock(corrupt=True))
    assert build_transfer.main(args) == 1
    assert "pypdf-1.0-py3-none-any.whl does not match uv.lock" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_missing_local_wheel_refuses(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (wheels / "openpyxl-1.0-py3-none-any.whl").unlink()
    assert build_transfer.main(_args(repo, tmp_path, wheels)) == 1
    assert "openpyxl-1.0-py3-none-any.whl is not in" in capsys.readouterr().err


def test_output_inside_repo_refuses(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _args(repo, tmp_path, wheels)
    args[args.index("--out") + 1] = str(repo[0] / "fresh")
    assert build_transfer.main(args) == 1
    assert "outside the repository" in capsys.readouterr().err
    assert not (repo[0] / "fresh").exists()


def test_existing_output_and_unknown_commit_refuse(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "out").mkdir()
    assert build_transfer.main(_args(repo, tmp_path, wheels)) == 1
    assert "fresh directory" in capsys.readouterr().err
    args = _args(repo, tmp_path, wheels, "other")
    args[args.index("--commit") + 1] = "deadbeef" * 5
    assert build_transfer.main(args) == 1
    assert "unknown commit" in capsys.readouterr().err


def test_unresolved_corpus_root_refuses(
    repo: tuple[Path, str],
    wheels: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RBOT_CORPUS_ROOTS", raising=False)
    path = repo[0] / "tests/corpus/corpus.json"
    data = json.loads(path.read_text())
    data["roots"]["private"] = "external"
    data["packs"][0]["files"][0]["external"] = "private/a.txt"
    path.write_text(json.dumps(data))
    assert build_transfer.main(_args(repo, tmp_path, wheels)) == 1
    assert "unresolved" in capsys.readouterr().err


def test_uncommitted_checklist_refuses(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git(repo[0], "rm", "-q", "install.ps1")
    _git(repo[0], "-c", "user.name=T", "-c", "user.email=t@e.invalid", "commit", "-qm", "x")
    args = _args(repo, tmp_path, wheels)
    args[args.index("--commit") + 1] = _git(repo[0], "rev-parse", "HEAD")
    assert build_transfer.main(args) == 1
    assert "not committed" in capsys.readouterr().err


def test_shipped_lock_pins_pure_wheels_and_checklist_block_is_complete() -> None:
    plan = build_transfer._wheel_plan((REAL / "uv.lock").read_text())
    assert any(n.startswith("pypdf-6.19.0") for n in plan)
    assert any(n.startswith("openpyxl-3.1.5") for n in plan)
    blank = build_transfer._blank_checklist(
        (REAL / "docs/acceptance/work-pc-checklist.md").read_text()
    )
    assert len(blank.splitlines()) == 10 + 2 * 10 + 1
