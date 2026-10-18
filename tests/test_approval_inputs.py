"""Actual public Approval input refusal; all packs are generated and isolated."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from state_receipt_assertions import artifact_bytes
from test_approval_authority import args
from test_bootstrap import pending, ready

from conftest import HANG_TIMEOUT
from rbotlib import state
from rbotlib.rules import load_rules

ROOT = Path(__file__).parents[1] / "rbot"
INPUTS = ("handoffs/CP-0.md", "run-brief.md", "grading.json")


def command(run: Path) -> list[str]:
    return [sys.executable, str(ROOT / "scripts/rbot.py"), "--root", str(ROOT), *args(run)]


def snapshot(run: Path, excluded: str) -> dict[str, bytes]:
    return {
        str(p.relative_to(run)): artifact_bytes(run, p.relative_to(run))
        for p in run.rglob("*")
        if p.is_file() and str(p.relative_to(run)) not in (excluded, "log/rbot.log")
    }


@pytest.mark.parametrize("name", INPUTS)
@pytest.mark.parametrize("kind", ["fifo", "symlink", "hardlink", "directory", "missing"])
def test_public_approval_refuses_unsupported_input_before_read(
    tmp_path: Path, name: str, kind: str
) -> None:
    run = pending(tmp_path, ROOT)
    ready(run, ROOT)
    before = snapshot(run, name)
    sources = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    log = run / "log/rbot.log"
    old_log = log.read_bytes()
    path = run / name
    original = path.read_bytes()
    external = tmp_path / "external-original"
    external.write_bytes(original)
    path.unlink()
    if kind == "fifo":
        os.mkfifo(path)
    elif kind == "symlink":
        path.symlink_to(external)
    elif kind == "hardlink":
        path.hardlink_to(external)
    elif kind == "directory":
        path.mkdir()
    process = subprocess.Popen(command(run), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = process.communicate(timeout=HANG_TIMEOUT)
    except subprocess.TimeoutExpired:
        lock_held = (run / state.LOCK).exists()
        process.kill()
        process.communicate()
        # Only this generated witness's killed process owns this lock.
        (run / state.LOCK).unlink(missing_ok=True)
        pytest.fail(f"Approval blocked reading {name} ({kind}); lock held={lock_held}")
    assert process.returncode == 1, (out, err)
    assert str(path).encode() in out + err
    expected = (
        "symlink" if kind == "symlink" else "hard link" if kind == "hardlink" else "regular file"
    )
    assert expected.encode() in out + err
    assert snapshot(run, name) == before
    assert sorted(run.parent.iterdir()) == [run]
    assert (run / state.LOCK).exists()
    assert not list(run.glob(".approve-*"))
    assert external.read_bytes() == original
    assert {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()} == sources
    assert log.read_bytes().startswith(old_log)
    assert len(log.read_bytes().splitlines()) == len(old_log.splitlines()) + 1
    assert log.read_bytes().splitlines()[-1].endswith(b"\t1")


def test_public_regular_control_preserves_cp0_and_reapproval_refuses(tmp_path: Path) -> None:
    run = pending(tmp_path, ROOT)
    ready(run, ROOT)
    cp0 = (run / INPUTS[0]).read_bytes()
    result = subprocess.run(command(run), capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout + result.stderr
    target = next(run.parent.iterdir())
    record = state.read(target)
    assert record["steps"]["CP-0"]["status"] == "accepted"
    assert record["steps"]["CP-1"]["status"] == "pending"
    assert (target / INPUTS[0]).read_bytes() == cp0
    before = snapshot(target, "")
    again = subprocess.run(command(target), capture_output=True, timeout=HANG_TIMEOUT)
    assert again.returncode == 1 and b"was approved" in again.stdout + again.stderr
    assert snapshot(target, "") == before
    assert (target / state.LOCK).exists()
    assert load_rules(ROOT).is_placeholder(record["cp0_lineage"]["issuer_id"]) is False
