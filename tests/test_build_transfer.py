"""Transfer builder: offline, with a temp git repo, temp lock, local wheels and temp registry."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import NamedTuple

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
    for name in ("install.sh", "install.ps1", "uv.lock", "docs/acceptance/work-pc-checklist.md"):
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


class Result(NamedTuple):
    code: int
    out: str
    err: str


def _build(
    repo: tuple[Path, str], tmp_path: Path, wheels: Path, out: str = "out", commit: str = ""
) -> Result:
    lock = tmp_path / "uv.lock"
    if not lock.exists():
        lock.write_text(_lock())
    argv = [
        *("bash", str(REAL / "scripts/build_transfer.sh"), sys.executable, str(repo[0])),
        commit or repo[1],
        str(tmp_path / out),
        *("--wheels", str(wheels), "--lock", str(lock)),
    ]
    env = {k: v for k, v in os.environ.items() if k != "RBOT_CORPUS_ROOTS"}
    done = subprocess.run(argv, capture_output=True, text=True, timeout=120, env=env)
    return Result(done.returncode, done.stdout, done.stderr)


def test_manifest_round_trip(repo: tuple[Path, str], wheels: Path, tmp_path: Path) -> None:
    result = _build(repo, tmp_path, wheels)
    assert result.code == 0, result.err
    archive = tmp_path / f"out/rbot-v1-{repo[1][:12]}.zip"
    assert f"sha256 {_sha(archive.read_bytes())}" in result.out
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
        assert all(line.endswith(":") for line in blank)


def test_hash_mismatch_refuses(repo: tuple[Path, str], wheels: Path, tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text(_lock(corrupt=True))
    result = _build(repo, tmp_path, wheels)
    assert result.code == 1
    assert "pypdf-1.0-py3-none-any.whl does not match uv.lock" in result.err
    assert not (tmp_path / "out").exists()


def test_missing_local_wheel_refuses(repo: tuple[Path, str], wheels: Path, tmp_path: Path) -> None:
    (wheels / "openpyxl-1.0-py3-none-any.whl").unlink()
    result = _build(repo, tmp_path, wheels)
    assert result.code == 1 and "openpyxl-1.0-py3-none-any.whl is not in" in result.err


def test_output_inside_repo_refuses(repo: tuple[Path, str], wheels: Path) -> None:
    result = _build(repo, repo[0], wheels, "fresh")
    assert result.code == 1 and "outside the repository" in result.err
    assert not (repo[0] / "fresh").exists()


def test_existing_output_and_unknown_commit_refuse(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path
) -> None:
    (tmp_path / "out").mkdir()
    result = _build(repo, tmp_path, wheels)
    assert result.code == 1 and "fresh directory" in result.err
    result = _build(repo, tmp_path, wheels, "other", "deadbeef" * 5)
    assert result.code == 1 and "unknown commit" in result.err


def test_unresolved_corpus_root_refuses(
    repo: tuple[Path, str], wheels: Path, tmp_path: Path
) -> None:
    path = repo[0] / "tests/corpus/corpus.json"
    data = json.loads(path.read_text())
    data["roots"]["private"] = "external"
    data["packs"][0]["files"][0]["external"] = "private/a.txt"
    path.write_text(json.dumps(data))
    _git(repo[0], "-c", "user.name=T", "-c", "user.email=t@e.invalid", "commit", "-qam", "x")
    result = _build(repo, tmp_path, wheels, commit="HEAD")
    assert result.code == 1 and "unresolved" in result.err


def test_uncommitted_input_refuses(repo: tuple[Path, str], wheels: Path, tmp_path: Path) -> None:
    _git(repo[0], "rm", "-q", "install.ps1")
    _git(repo[0], "-c", "user.name=T", "-c", "user.email=t@e.invalid", "commit", "-qm", "x")
    result = _build(repo, tmp_path, wheels, commit="HEAD")
    assert result.code == 1 and "not committed" in result.err


def test_shipped_lock_pins_pure_wheels_and_checklist_block_is_complete() -> None:
    plan = build_transfer._wheel_plan((REAL / "uv.lock").read_text())
    assert any(n.startswith("pypdf-6.19.0") for n in plan)
    assert any(n.startswith("openpyxl-3.1.5") for n in plan)
    blank = build_transfer._blank_checklist(
        (REAL / "docs/acceptance/work-pc-checklist.md").read_text()
    )
    assert len(blank.splitlines()) == 10 + 2 * 10 + 1
