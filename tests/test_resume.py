"""Native killed controller publications; generated fixtures never prove live providers."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_bootstrap import approve, pending, ready
from test_modules import _blocked

from conftest import HANG_TIMEOUT
from rbotlib import cli, dispatch, state
from rbotlib.contract import load_contract
from rbotlib.rules import RBOT_ROOT, load_rules

CHILD = r"""
from pathlib import Path
import json, os, sys
from rbotlib import cli
run, phase = Path(sys.argv[1]), sys.argv[2]
real = os.replace
def replace(source, destination):
    target = Path(destination)
    real(source, destination)
    matches = (
        (phase == "event" and target.parent == run / "validate/history/CP-1") or
        (phase == "latest" and target == run / "validate/CP-1.json") or
        (phase == "intent" and target == run / "run-state.json"
         and "module_publication" in json.loads(target.read_text())) or
        (phase == "state" and target == run / "run-state.json"
         and "module_publication" not in json.loads(target.read_text())) or
        (phase == "row" and target == run / "log/rbot.log")
    )
    if matches:
        os._exit(73)
os.replace = replace
sys.exit(cli.main(sys.argv[3:]))
"""


def receipt(run: Path, module: str) -> list[str]:
    step = state.read(run)["steps"][module]
    findings = f"validate/{module}.json" if step.get("validate_exit") == 2 else None
    text = dispatch.prepare_message(run, RBOT_ROOT, module, findings)
    return [
        "dispatch-receipt",
        "--run",
        str(run),
        "--module",
        module,
        "--receipt",
        f"fixture-{module}",
        "--reporter",
        "generated-controller",
        "--message-sha256",
        hashlib.sha256(text.encode()).hexdigest(),
    ]


def prepared(tmp_path: Path, action: str) -> tuple[Path, list[str]]:
    run = pending(tmp_path, RBOT_ROOT)
    assert cli.main(receipt(run, "CP-0")) == 0
    assert cli.main(["accept", "--run", str(run), "--module", "CP-0"]) == 0
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    contract = load_contract(RBOT_ROOT / "modules/CP-1/contract.json", load_rules(RBOT_ROOT))
    fixture = (Path(__file__).parent / "fixtures/handoffs/CP-1.md").read_text()
    own = (
        _blocked(fixture, contract)
        .replace("run_id: 20261011-czr-full-credit-assessment", f"run_id: {run.name}")
        .replace("issuer_id: CZR", "issuer_id: ACME")
    )
    (run / "handoffs/CP-1.md").write_text(own)
    argv = receipt(run, "CP-1")
    if action == "accept":
        assert cli.main(argv) == 0
        argv = ["accept", "--run", str(run), "--module", "CP-1"]
    return run, argv


def killed(run: Path, phase: str, argv: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, "-c", CHILD, str(run), phase, *argv],
        env=os.environ | {"PYTHONPATH": str(RBOT_ROOT / "scripts")},
        capture_output=True,
        text=True,
        timeout=HANG_TIMEOUT,
    )
    assert result.returncode == 73, result.stderr
    return result


@pytest.mark.parametrize(
    "action,phase",
    [
        ("dispatch", "event"),
        ("accept", "event"),
        ("accept", "latest"),
    ],
)
def test_native_module_interruption_recovers(tmp_path: Path, action: str, phase: str) -> None:
    run, argv = prepared(tmp_path, action)
    source = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    killed(run, phase, argv)
    events = {p.name: p.read_bytes() for p in (run / "validate/history/CP-1").iterdir()}
    assert cli.main(["next", "--run", str(run)]) == 0
    step = state.read(run)["steps"]["CP-1"]
    assert step["status"] == ("running" if action == "dispatch" else "blocked")
    assert step["attempts"] == 1
    assert cli.main(argv) == (0 if action == "dispatch" else 3)
    assert state.read(run)["steps"]["CP-1"] == step
    assert {p.name: p.read_bytes() for p in (run / "validate/history/CP-1").iterdir()} == events
    assert {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()} == source


@pytest.mark.parametrize(
    "action,phase",
    [
        ("dispatch", "intent"),
        ("dispatch", "state"),
        ("accept", "intent"),
        ("accept", "state"),
        ("accept", "row"),
    ],
)
def test_native_intent_and_outcome_seams(tmp_path: Path, action: str, phase: str) -> None:
    run, argv = prepared(tmp_path, action)
    killed(run, phase, argv)
    assert cli.main(["next", "--run", str(run)]) == 0
    step = state.read(run)["steps"]["CP-1"]
    assert step["status"] == ("running" if action == "dispatch" else "blocked")
    assert step["attempts"] == 1
    assert "module_publication" not in state.read(run)
    assert cli.main(argv) == (0 if action == "dispatch" else 3)
    assert state.read(run)["steps"]["CP-1"] == step


@pytest.mark.parametrize(
    "damage",
    [
        "intent",
        "state",
        "event",
        "latest",
        "extra",
        "source",
        "handoff",
        "dispatch",
        "lost_event",
        "origin",
        "owner",
    ],
)
def test_prospective_recovery_refuses_changed_evidence(tmp_path: Path, damage: str) -> None:
    import json

    from rbotlib import current
    from rbotlib.inventory import RunError

    run, argv = prepared(tmp_path, "accept")
    killed(run, "latest" if damage == "lost_event" else "event", argv)
    target = run / state.STATE
    record = state.read(run)
    if damage in ("intent", "state", "origin"):
        if damage == "intent":
            record["module_publication"]["proof"] = "0" * 64
        elif damage == "origin":
            record["approved_origins"]["CP-0"]["sha256"] = "0" * 64
        else:
            record["steps"]["CP-1"]["attempts"] = 2
        target.write_text(json.dumps(record))
    elif damage == "event":
        (run / "validate/history/CP-1/000002.json").write_text("{}")
    elif damage == "latest":
        (run / "validate/CP-1.json").write_text("{}")
    elif damage == "extra":
        (run / "validate/history/CP-1/000003.json").write_text("{}")
    elif damage == "source":
        (run.parent.parent / "acme_10k.txt").write_text("changed")
    elif damage == "lost_event":
        (run / "validate/history/CP-1/000002.json").unlink()
    elif damage in ("dispatch", "handoff"):
        folder = {"dispatch": "dispatch", "handoff": "handoffs"}[damage]
        path = run / folder / "CP-1.md"
        path.write_bytes(path.read_bytes() + b"changed")
    else:
        path = run / state.LOCK
        path.unlink()
        path.write_text("replacement")
    before = target.read_bytes()
    evidence = {p.name: p.read_bytes() for p in (run / "validate/history/CP-1").iterdir()}
    with pytest.raises((RunError, ValueError)):
        current.reconcile(run, RBOT_ROOT)
    assert target.read_bytes() == before
    assert {p.name: p.read_bytes() for p in (run / "validate/history/CP-1").iterdir()} == evidence


@pytest.mark.parametrize("damage", ["event", "handoff"])
def test_publication_readback_precedes_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    from rbotlib import accept, fsio, resume
    from rbotlib.inventory import RunError

    run, _ = prepared(tmp_path, "accept")
    real = fsio.write_atomic

    def swap(path: Path, text: str) -> None:
        real(path, text)
        if path.parent == run / "validate/history/CP-1":
            target = path if damage == "event" else run / "handoffs/CP-1.md"
            target.write_bytes(target.read_bytes() + b"\nchanged\n")

    monkeypatch.setattr(resume, "write_atomic", swap)
    with pytest.raises((RunError, ValueError)):
        accept.accept(run, RBOT_ROOT, "CP-1")
    assert state.read(run)["steps"]["CP-1"]["status"] == "running"


@pytest.mark.parametrize("outcome", ["malformed", "identity", "missing"])
def test_interrupted_validation_preserves_taxonomy_and_retry(tmp_path: Path, outcome: str) -> None:
    run, argv = prepared(tmp_path, "accept")
    own = run / "handoffs/CP-1.md"
    code = {"malformed": 2, "identity": 4, "missing": 1}[outcome]
    if outcome == "missing":
        own.unlink()
    elif outcome == "identity":
        own.write_text(own.read_text().replace(f"run_id: {run.name}", "run_id: unrelated"))
    else:
        own.write_text("DONE 0")
    killed(run, "event", argv)
    assert cli.main(["next", "--run", str(run)]) == 0
    step = state.read(run)["steps"]["CP-1"]
    assert step["validate_exit"] == code and step["attempts"] == 1
    assert step["status"] == ("running" if code == 2 else "failed")
    assert cli.main(argv) == code
    if code == 2:
        retry = receipt(run, "CP-1")
        retry[retry.index("--receipt") + 1] = "fixture-retry"
        assert cli.main(retry) == 0
        assert cli.main(argv) == 2
        assert state.read(run)["steps"]["CP-1"]["status"] == "failed"
        assert state.read(run)["steps"]["CP-1"]["attempts"] == 2
        assert cli.main(retry) == 0  # duplicate registration never opens slot3


def test_orphan_without_prospective_authority_stays_preserved(tmp_path: Path) -> None:
    import json

    from rbotlib import current
    from rbotlib.inventory import RunError

    run, argv = prepared(tmp_path, "accept")
    killed(run, "event", argv)
    record = state.read(run)
    record.pop("module_publication")
    (run / state.STATE).write_text(json.dumps(record))
    before = (run / state.STATE).read_bytes()
    event = run / "validate/history/CP-1/000002.json"
    saved = event.read_bytes()
    with pytest.raises(RunError, match="orphan"):
        current.reconcile(run, RBOT_ROOT)
    assert (run / state.STATE).read_bytes() == before and event.read_bytes() == saved


@pytest.mark.parametrize("days", [30.000001, -0.000001])
def test_explicit_next_refuses_ineligible_age_before_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, days: float
) -> None:
    from datetime import datetime, timedelta

    from rbotlib import next as selection
    from rbotlib import runs
    from rbotlib.inventory import RunError

    run, _ = prepared(tmp_path, "dispatch")
    record = state.read(run)
    clock = datetime.fromisoformat(record["created_at"]) + timedelta(days=days)
    monkeypatch.setattr(runs, "_clock", lambda now: clock)
    before = (run / state.STATE).read_bytes()
    with pytest.raises(RunError, match=r"30 days|future"):
        selection.select(run, RBOT_ROOT)
    assert (run / state.STATE).read_bytes() == before


def test_final_staging_cannot_hide_changed_validation_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib import accept
    from rbotlib.inventory import RunError

    run, _ = prepared(tmp_path, "accept")
    real = state._Locked.stage

    def changed(owner: state._Locked, record: state.Record) -> Path:
        staged = real(owner, record)
        if "module_publication" not in record and record["steps"]["CP-1"]["status"] == "blocked":
            own = run / "handoffs/CP-1.md"
            own.write_bytes(own.read_bytes() + b"changed after final staging")
        return staged

    monkeypatch.setattr(state._Locked, "stage", changed)
    with pytest.raises(RunError, match=r"context|readback"):
        accept.accept(run, RBOT_ROOT, "CP-1")
    assert state.read(run)["steps"]["CP-1"]["status"] == "running"


def test_exact_thirty_day_native_renamed_run_remains_eligible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, timedelta

    from rbotlib import next as selection
    from rbotlib import runs

    run, _ = prepared(tmp_path, "dispatch")
    before = state.read(run)
    clock = datetime.fromisoformat(before["created_at"]) + timedelta(days=30)
    monkeypatch.setattr(runs, "_clock", lambda now: clock)
    assert runs.discover_unfinished(run.parent.parent) == run
    assert selection.select(run, RBOT_ROOT)["step"] == "CP-1"
    assert state.read(run)["approval"] == before["approval"]
    assert state.read(run)["steps"] == before["steps"]


def test_original_native_module_owner_finishes_after_refused_contender(tmp_path: Path) -> None:
    import time

    run, argv = prepared(tmp_path, "accept")
    child_code = CHILD.replace(
        "    if matches:\n        os._exit(73)",
        """    if matches:
        (run / ".held-fixture").touch()
        import time
        while not (run / ".continue-fixture").exists():
            time.sleep(0.01)""",
    )
    process = subprocess.Popen(
        [sys.executable, "-c", child_code, str(run), "event", *argv],
        env=os.environ | {"PYTHONPATH": str(RBOT_ROOT / "scripts")},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + HANG_TIMEOUT
        while not (run / ".held-fixture").exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert (run / ".held-fixture").exists()
        before, log = (run / state.STATE).read_bytes(), (run / "log/rbot.log").read_bytes()
        assert cli.main(["next", "--run", str(run)]) == 1
        assert (run / state.STATE).read_bytes() == before
        assert (run / "log/rbot.log").read_bytes() == log
        (run / ".continue-fixture").touch()
        _, error = process.communicate(timeout=HANG_TIMEOUT)
        assert process.returncode == 3, error
        assert state.read(run)["steps"]["CP-1"]["status"] == "blocked"
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()
