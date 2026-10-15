"""Ordinary command rows have prospective unique attribution, including real kills."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_bootstrap import pending

from rbotlib import cli, runlog, state
from rbotlib.rules import RBOT_ROOT

CHILD = r"""
from pathlib import Path
import json, os, sys
from rbotlib import cli
run, phase = Path(sys.argv[1]), sys.argv[2]
real = os.replace
def replace(source, destination):
    target = Path(destination)
    real(source, destination)
    if (phase == "row" and target == run / "log/rbot.log") or (
        phase == "intent" and target == run / "run-state.json"
        and json.loads(target.read_text()).get("command_receipts", [{}])[-1].get("end") is None
    ):
        os._exit(73)
os.replace = replace
sys.exit(cli.main(["state", "--run", str(run)]))
"""


@pytest.mark.parametrize("phase", ["intent", "row"])
def test_killed_ordinary_row_remains_attributed(tmp_path: Path, phase: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    child = subprocess.run(
        [sys.executable, "-c", CHILD, str(run), phase],
        env=os.environ | {"PYTHONPATH": str(RBOT_ROOT / "scripts")},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert child.returncode == 73, child.stderr
    original = state.read(run)["command_receipts"][-1]
    before = runlog.path(run).read_bytes()
    assert cli.main(["state", "--run", str(run)]) == 0
    entries = state.read(run)["command_receipts"]
    assert entries[-1]["intent"]["invocation"] != original["intent"]["invocation"]
    previous = entries[-2]
    assert previous["intent"] == original["intent"]
    assert previous["observation"] == (
        "missing row; exit unknown" if phase == "intent" else "candidate0; exit unknown"
    )
    assert runlog.path(run).read_bytes().startswith(before)
    assert len(runlog.path(run).read_bytes().splitlines()) == len(before.splitlines()) + 1


def test_same_second_identical_rows_keep_invocation_offsets(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    rows = []
    for _ in range(2):
        owned = runlog.Receipt(run, ["identical"])
        owned.row = b"2026-10-13T00:00:00+00:00\tidentical\t"
        try:
            owned.append(0)
        finally:
            owned.close()
        rows.append(state.read(run)["command_receipts"][-1])
    assert rows[0]["intent"]["row"] == rows[1]["intent"]["row"]
    assert rows[0]["intent"]["invocation"] != rows[1]["intent"]["invocation"]
    assert rows[0]["end"] == rows[1]["intent"]["prefix_size"]
    assert rows[0]["end"] < rows[1]["end"]


@pytest.mark.parametrize("damage", ["row", "prefix", "intent", "extra"])
def test_corrupt_ordinary_receipt_refuses_before_command(tmp_path: Path, damage: str) -> None:
    import json

    run = pending(tmp_path, RBOT_ROOT)
    record = state.read(run)
    entry = record["command_receipts"][-1]
    log = runlog.path(run)
    if damage == "intent":
        entry["intent"]["prefix_size"] = True
        (run / state.STATE).write_text(json.dumps(record))
    elif damage == "extra":
        entry["unexpected"] = True
        (run / state.STATE).write_text(json.dumps(record))
    elif damage == "prefix":
        log.write_bytes(b"changed\n" + log.read_bytes())
    else:
        raw = bytearray(log.read_bytes())
        raw[-2] = ord("4")
        log.write_bytes(raw)
    before, saved = (run / state.STATE).read_bytes(), log.read_bytes()
    assert (
        cli.main(["state", "--run", str(run), "--set", "CP-0=failed", "--reason", "must not run"])
        == 1
    )
    assert (run / state.STATE).read_bytes() == before and log.read_bytes() == saved


def test_active_owner_pauses_without_changing_outcome(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    owner = state._Locked(run)
    before, log = (run / state.STATE).read_bytes(), runlog.path(run).read_bytes()
    try:
        assert cli.main(["state", "--run", str(run)]) == 1
        assert (run / state.STATE).read_bytes() == before
        assert runlog.path(run).read_bytes() == log
    finally:
        assert owner.close() == []


def test_final_receipt_state_staging_rechecks_exact_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib import command_receipts

    run = pending(tmp_path, RBOT_ROOT)
    real = command_receipts.finish

    def changed(owner: state._Locked, receipt: runlog.Receipt) -> None:
        real(owner, receipt)
        path = runlog.path(run)
        path.write_bytes(path.read_bytes() + b"foreign suffix\n")

    monkeypatch.setattr(command_receipts, "finish", changed)
    assert cli.main(["state", "--run", str(run)]) == 1


def test_completed_frontier_foreign_suffix_refuses_before_command(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    log = runlog.path(run)
    log.write_bytes(log.read_bytes() + b"foreign\tunregistered\t0\n")
    before, raw = (run / state.STATE).read_bytes(), log.read_bytes()
    assert (
        cli.main(["state", "--run", str(run), "--set", "CP-0=failed", "--reason", "must not run"])
        == 1
    )
    assert (run / state.STATE).read_bytes() == before
    assert log.read_bytes() == raw


def test_pending_ordinary_then_registered_host_keeps_exact_frontiers(tmp_path: Path) -> None:
    from test_model_host import eligible

    run = eligible(tmp_path, RBOT_ROOT)
    child = subprocess.run(
        [sys.executable, "-c", CHILD, str(run), "intent"],
        env=os.environ | {"PYTHONPATH": str(RBOT_ROOT / "scripts")},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert child.returncode == 73, child.stderr
    original = state.read(run)["command_receipts"][-1]
    prefix = runlog.path(run).read_bytes()
    assert cli.main(["model", "--run", str(run)]) == 0
    observed = state.read(run)["command_receipts"][-1]
    assert observed["intent"] == original["intent"]
    assert observed["end"] == len(prefix)
    assert observed["observation"] == "missing row; exit unknown"
    assert cli.main(["state", "--run", str(run)]) == 0
    last = state.read(run)["command_receipts"][-1]
    assert last["intent"]["invocation"] != original["intent"]["invocation"]
    assert last["intent"]["prefix_size"] > len(prefix)
    assert runlog.path(run).read_bytes().startswith(prefix)
    assert len(runlog.path(run).read_bytes().splitlines()) == len(prefix.splitlines()) + 2


def test_registered_host_corrupt_row_refuses_without_traceback(tmp_path: Path) -> None:
    import json

    from test_model_host import eligible

    run = eligible(tmp_path, RBOT_ROOT)
    assert cli.main(["model", "--run", str(run)]) == 0
    record = state.read(run)
    record["steps"]["MODEL"]["host_execution"]["invocations"][-1]["receipt"]["row"] = None
    (run / state.STATE).write_text(json.dumps(record))
    before, raw = (run / state.STATE).read_bytes(), runlog.path(run).read_bytes()
    assert cli.main(["state", "--run", str(run)]) == 1
    assert (run / state.STATE).read_bytes() == before
    assert runlog.path(run).read_bytes() == raw


def _receipt_entry(invocation: str, end: int | None, observation: str) -> dict[str, object]:
    import hashlib

    from rbotlib import host_evidence

    intent = {
        "invocation": invocation,
        "code": 0,
        "prefix_size": 0,
        "prefix_sha256": hashlib.sha256(b"").hexdigest(),
        "row": b"2026-10-13T00:00:00+00:00\tx\t".hex(),
    }
    intent["binding"] = host_evidence.digest(intent)
    return {"intent": intent, "observation": observation, "end": end}


def test_pending_intent_must_be_latest_even_with_pending_text() -> None:
    from rbotlib import command_receipts
    from rbotlib.inventory import RunError

    pending_first = _receipt_entry("a" * 32, None, "pending")
    settled_last = _receipt_entry("b" * 32, 0, "missing row; exit unknown")
    with pytest.raises(RunError, match="only latest intent may be pending"):
        command_receipts.checked({"command_receipts": [pending_first, settled_last]})


def test_each_following_receipt_is_bounded_by_the_next_prefix() -> None:
    from rbotlib import command_receipts

    following = [{"prefix_size": 10}, {"prefix_size": 20}, {"prefix_size": 30}]
    invocation = {"id": "host-model/1", "following_receipts": following}
    bounds = [item[3] for item in command_receipts._invocation_intents(invocation, 99)]
    assert bounds == [20, 30, 99]
