"""Unsafe state is never standalone authority; no-state ownership remains original."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pytest
from test_legacy_ownership import legacy, observe, snapshot
from test_state import seeded

from rbotlib import cli, grade, inventory, ownership, runlog, runs, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("phase", ["pre-Approval", "empty-plan", "renamed"])
@pytest.mark.parametrize(
    "lock_bytes", [None, b"", b"foreign sentinel\n", ownership.MAGIC + b"a" * 32 + b"\n"]
)
@pytest.mark.parametrize("existing_log", [False, True])
def test_legacy_variants_never_grant_mutation_or_logging(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    phase: str,
    lock_bytes: bytes | None,
    existing_log: bool,
) -> None:
    run, record = seeded(tmp_path, approved=phase == "renamed")
    record.pop("ownership")
    (run / state.LOCK).unlink()
    (run / runlog.LOCK).unlink()
    if phase == "empty-plan":
        record.update(plan=[], steps={})
    if phase == "renamed":
        target = run.with_name("20261012-acme-full-credit-assessment")
        run.rename(target)
        run = target
        record["run_id"] = run.name
    (run / state.STATE).write_text(json.dumps(record))
    if lock_bytes is not None:
        (run / state.LOCK).write_bytes(lock_bytes)
        (run / runlog.LOCK).write_bytes(lock_bytes)
    if existing_log:
        (run / "log/rbot.log").write_bytes(b"old output exists\t0\n")
    before = snapshot(run)
    events = observe(run, monkeypatch)
    for operation in (
        lambda: state.update(run, lambda record: None),
        lambda: runlog.Receipt(run, ["probe"]),
    ):
        with pytest.raises(RunError, match=r"legacy.*ownership"):
            operation()
    assert cli.main(["inventory", "--run", str(run)]) == 1
    assert grade.run_command(argparse.Namespace(run_dir=str(run), root=RBOT_ROOT)) == 1
    assert cli._finish_log(argparse.Namespace(run_dir=str(run)), run, ["probe"], 1) == 1
    assert snapshot(run) == before and events == []
    assert runs.discover_unfinished(run.parents[1]) == run
    with pytest.raises(RunError, match=r"unfinished legacy.*ownership"):
        runs.create_run(run.parents[1])
    assert snapshot(run) == before and events == []


@pytest.mark.parametrize(
    "kind", ["malformed", "null ownership", "directory", "fifo", "broken link"]
)
def test_direct_publication_unsafe_state_cannot_fall_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    run = legacy(tmp_path)
    marker = run / state.STATE
    record = state.read(run)
    marker.unlink()
    if kind == "directory":
        marker.mkdir()
    elif kind == "fifo":
        os.mkfifo(marker)
    elif kind == "broken link":
        marker.symlink_to(tmp_path / "missing")
    elif kind == "null ownership":
        record["ownership"] = None
        marker.write_text(json.dumps(record))
    else:
        marker.write_bytes(b"{")
    before = snapshot(run)
    events = observe(run, monkeypatch)
    for operation in (lambda: inventory.write(run), lambda: runlog.Receipt(run, ["probe"])):
        with pytest.raises((OSError, ValueError)):
            operation()
    assert cli.main(["inventory", "--run", str(run)]) == 1
    assert snapshot(run) == before and events == []


def test_original_standalone_receipt_outside_state_envelope(tmp_path: Path) -> None:
    receipt = runlog.Receipt(tmp_path, ["standalone"])
    assert (tmp_path / runlog.LOCK).read_bytes() == b""
    with pytest.raises(RunError, match="holds"):
        runlog.Receipt(tmp_path, ["contender"])
    receipt.append(0)
    receipt.close()
    runlog.append(tmp_path, ["next"], 1)
    assert len((tmp_path / "log/rbot.log").read_text().splitlines()) == 2
    assert not (tmp_path / runlog.LOCK).exists()
    assert not (tmp_path / state.LOCK).exists()


def test_marker_shaped_standalone_lock_is_not_entitlement(tmp_path: Path) -> None:
    (tmp_path / "log").mkdir()
    marker = tmp_path / runlog.LOCK
    raw = ownership.MAGIC + b"a" * 32 + b"\n"
    marker.write_bytes(raw)
    with pytest.raises(RunError, match="holds"):
        runlog.append(tmp_path, ["probe"], 0)
    assert marker.read_bytes() == raw and not (tmp_path / "log/rbot.log").exists()


def test_brief_publication_borrows_shared_state_owner(tmp_path: Path) -> None:
    from rbotlib import brief

    run = runs.create_run(tmp_path)
    owner = state._Locked(run)
    before = snapshot(run)
    try:
        with pytest.raises(RunError, match="holds"):
            brief._record(run, state.read(run), "new brief\n")
        assert snapshot(run) == before
    finally:
        assert owner.close() == []
    brief._record(run, None, "new brief\n")
    assert (run / "run-brief.md").read_text() == "new brief\n"
    assert state.read(run)["run_brief_sha256"] is not None
