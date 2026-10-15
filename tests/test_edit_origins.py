"""Exact origins are captured by supported native completion and Approval flows."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from state_receipt_assertions import artifact_bytes, outcome_bytes
from test_accept import send
from test_bootstrap import approve, pending, ready

from rbotlib import accept, bootstrap, dispatch, state
from rbotlib import next as selection
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, load_rules


@pytest.mark.parametrize("route", ["direct", "complete", "receipt"])
@pytest.mark.parametrize("qa", ["Restricted", "Blocked"])
def test_native_origins_and_multiple_narrative_edits(tmp_path: Path, route: str, qa: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    path = run / bootstrap.CP0
    path.write_text(path.read_text().replace("qa_status: Restricted", f"qa_status: {qa}"))
    if route == "complete":
        bootstrap.complete_cp0(run, RBOT_ROOT, load_rules(RBOT_ROOT))
    elif route == "receipt":
        send(run, RBOT_ROOT)
        assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == (3 if qa == "Blocked" else 0)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    before = copy.deepcopy(state.read(run))
    assert "approved_origins" in before
    for index in range(2):
        for name in (bootstrap.CP0, "run-brief.md"):
            own = run / name
            own.write_bytes(own.read_bytes() + f"\nNarrative {index}.\n".encode())
        assert selection.select(run, RBOT_ROOT)["step"] == "CP-1"
        now = state.read(run)
        assert now["approval"] == before["approval"]
        assert now["approved_origins"] == before["approved_origins"]
        assert now["cp0_lineage"] == before["cp0_lineage"]
        assert now["steps"]["CP-0"]["attempts"] == before["steps"]["CP-0"]["attempts"]
        assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == (3 if qa == "Blocked" else 0)
        assert dispatch.prepare_message(run, RBOT_ROOT, "CP-1")
        frozen = outcome_bytes(run)
        selection.select(run, RBOT_ROOT)
        assert outcome_bytes(run) == frozen


@pytest.mark.parametrize("route", ["complete", "receipt"])
def test_approval_selects_current_cp0_preserving_first_completion(
    tmp_path: Path, route: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    if route == "complete":
        bootstrap.complete_cp0(run, RBOT_ROOT, load_rules(RBOT_ROOT))
    else:
        send(run, RBOT_ROOT)
        accept.accept(run, RBOT_ROOT, "CP-0")
    first = copy.deepcopy(state.read(run)["steps"]["CP-0"])
    path = run / bootstrap.CP0
    path.write_bytes(path.read_bytes() + b"\nSelected before Approval.\n")
    # A real current observation precedes grading; no accepted-state seeding.
    with pytest.raises(RunError, match="waiting for analyst"):
        selection.select(run, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    now = state.read(run)
    assert now["steps"]["CP-0"]["current_origin"] == first
    assert now["cp0_lineage"]["sha256"] != first["sha256"]
    assert selection.select(run, RBOT_ROOT)["step"] == "CP-1"
    assert dispatch.prepare_message(run, RBOT_ROOT, "CP-1")


@pytest.mark.parametrize("change", ["classification", "objective", "citation", "front"])
def test_changed_approved_semantics_refuse_without_publication(tmp_path: Path, change: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    name = "run-brief.md" if change == "objective" else bootstrap.CP0
    path = run / name
    text = path.read_text()
    substitutions = {
        "classification": ("| acme_10k.txt | issuer |", "| acme_10k.txt | market |"),
        "objective": ("Annual review", "Changed objective"),
        "citation": ("p. 1", "page 1"),
        "front": ("qa_status: Restricted", "qa_status: Pass"),
    }
    old, new = substitutions[change]
    assert old in text
    path.write_text(text.replace(old, new))
    before = outcome_bytes(run)
    with pytest.raises(RunError, match=r"decisions|classification|validat|origin"):
        selection.select(run, RBOT_ROOT)
    assert outcome_bytes(run) == before


@pytest.mark.parametrize("damage", ["hash", "base64", "size", "identity", "extra"])
def test_unchanged_artifacts_still_validate_origin_envelopes(tmp_path: Path, damage: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    record = state.read(run)
    origin = record["approved_origins"]["CP-0"]
    if damage == "extra":
        origin["unexpected"] = True
    else:
        key, value = {
            "hash": ("sha256", "0" * 64),
            "base64": ("bytes", "???"),
            "size": ("size", True),
            "identity": ("issuer_id", "FORGED"),
        }[damage]
        origin[key] = value
    (run / state.STATE).write_text(json.dumps(record))
    before = outcome_bytes(run)
    with pytest.raises(RunError, match=r"origin|lineage"):
        selection.select(run, RBOT_ROOT)
    assert outcome_bytes(run) == before


@pytest.mark.parametrize("route", ["direct", "receipt"])
@pytest.mark.parametrize("changed", [False, True])
def test_uncaptured_requires_exact_candidate_and_restoration(
    tmp_path: Path, route: str, changed: bool
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    if route == "receipt":
        send(run, RBOT_ROOT)
        accept.accept(run, RBOT_ROOT, "CP-0")
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    original = (run / bootstrap.CP0).read_bytes()
    record = state.read(run)
    # Removing only prospective evidence simulates an already-entitled old run.
    record.pop("approved_origins")
    record.pop("completion_origin", None)
    (run / state.STATE).write_text(json.dumps(record))
    if changed:
        (run / bootstrap.CP0).write_bytes(original + b"\nChanged narrative.\n")
    before = outcome_bytes(run)
    if changed and route == "direct":
        with pytest.raises(RunError, match="frozen approved CP0 bytes unavailable"):
            selection.select(run, RBOT_ROOT)
        assert outcome_bytes(run) == before
        (run / bootstrap.CP0).write_bytes(original)
    assert selection.select(run, RBOT_ROOT)["step"] == "CP-1"
    origin = state.read(run)["approved_origins"]["CP-0"]
    assert origin["basis"] == ("registered_validation" if route == "receipt" else "restored")
    if route == "receipt":
        reference = origin["history"]
        registered = state.read(run)["steps"]["CP-0"]["accept_history"]
        assert reference["sha256"] == registered[reference["sequence"] - 1]


@pytest.mark.parametrize("change", ["narrative", "objective"])
def test_uncaptured_brief_reconstruction_is_exact(tmp_path: Path, change: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    record = state.read(run)
    record.pop("approved_origins")
    (run / state.STATE).write_text(json.dumps(record))
    own = run / "run-brief.md"
    text = own.read_text()
    own.write_text(
        text + "\nNarrative.\n"
        if change == "narrative"
        else text.replace("Annual review", "Changed objective")
    )
    before = outcome_bytes(run)
    if change == "objective":
        with pytest.raises(RunError, match="origin cannot be reconstructed"):
            selection.select(run, RBOT_ROOT)
        assert outcome_bytes(run) == before
    else:
        assert selection.select(run, RBOT_ROOT)["step"] == "CP-1"
        assert state.read(run)["approved_origins"]["RUN_BRIEF"]["basis"] == "reconstructed"


@pytest.mark.parametrize(
    "damage", ["entry", "snapshot", "identity", "cause", "original", "history"]
)
def test_current_lineage_corruption_refuses(tmp_path: Path, damage: str) -> None:
    from test_model_host import eligible

    run = eligible(tmp_path, RBOT_ROOT, "Pass")
    own = run / "handoffs/CP-1.md"
    own.write_bytes(own.read_bytes() + b"\nNarrative.\n")
    selection.select(run, RBOT_ROOT)
    record = state.read(run)
    step = record["steps"]["CP-1"]
    entry = step["current_edits"][-1]
    if damage == "entry":
        step["current_edits"] = [None]
    elif damage == "snapshot":
        entry["snapshot"] = 123
    elif damage == "identity":
        import base64
        import hashlib

        raw = base64.b64decode(entry["snapshot"]).replace(b"issuer_id: ACME", b"issuer_id: FORGED")
        entry["snapshot"] = base64.b64encode(raw).decode()
        entry["result"]["sha256"] = step["sha256"] = hashlib.sha256(raw).hexdigest()
    elif damage == "cause":
        entry["producer"] = "CP-3"
    elif damage == "original":
        step["current_origin"]["attempts"] = 0
    else:
        (run / "validate/history/CP-1/000002.json").write_text("{}")
    (run / state.STATE).write_text(json.dumps(record))
    before = outcome_bytes(run)
    with pytest.raises(RunError):
        selection.select(run, RBOT_ROOT)
    assert outcome_bytes(run) == before


@pytest.mark.parametrize("boundary", ["stage", "brief", "state", "rename"])
@pytest.mark.parametrize("abrupt", [False, True])
def test_approval_publication_interruptions_preserve_bound_evidence(
    tmp_path: Path, boundary: str, abrupt: bool
) -> None:
    import subprocess
    import sys

    from rbotlib import approve as approval

    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    before = {name: artifact_bytes(run, name) for name in ("run-brief.md", state.STATE)}
    target = approval.new_name(run, "ACME", "FULL_CREDIT_ASSESSMENT")
    script = """
import os, sys
from pathlib import Path
from rbotlib import approve, cli
boundary, abrupt = sys.argv[1:3]
replace, rename, write = os.replace, Path.rename, approve.write_atomic

def stop():
    if abrupt == "True": os._exit(73)
    raise OSError("causal Approval publication failure")

def replacement(source, dest):
    if Path(source).name.startswith(".approve-") and Path(dest).name == {
        "brief": "run-brief.md", "state": "run-state.json"
    }.get(boundary):
        if abrupt == "True": replace(source, dest)
        stop()
    return replace(source, dest)

def renamed(source, dest):
    if boundary == "rename": stop()
    return rename(source, dest)

def written(path, text):
    if boundary == "stage" and Path(path).name.startswith(".approve-"): stop()
    return write(path, text)

os.replace, Path.rename, approve.write_atomic = replacement, renamed, written
sys.exit(cli.main(sys.argv[3:]))
"""
    command = [
        "--root",
        str(RBOT_ROOT),
        "approve",
        "--run",
        str(run),
        "--pathway",
        "FULL_CREDIT_ASSESSMENT",
        "--depth",
        "full",
        "--primary",
        "no",
        "--analyst",
        "Approver",
    ]
    import os

    environment = dict(os.environ, PYTHONPATH=str(RBOT_ROOT / "scripts"))
    process = subprocess.run(
        [sys.executable, "-c", script, boundary, str(abrupt), *command],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == (73 if abrupt else 1), process.stdout + process.stderr
    assert not target.exists()
    if not abrupt or boundary == "stage":
        assert {name: artifact_bytes(run, name) for name in before} == before
        assert state.read(run)["approval"] is None
    else:
        with pytest.raises(RunError):
            selection.select(run, RBOT_ROOT)
        assert (run / bootstrap.CP0).is_file()
        if boundary in ("state", "rename"):
            raw = json.loads((run / state.STATE).read_text())
            assert raw["approved_origins"]["CP-0"]["sha256"] == raw["cp0_lineage"]["sha256"]


def test_invalid_citation_is_auditable_current_failure(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    original = copy.deepcopy(state.read(run))
    own = run / bootstrap.CP0
    own.write_text(
        own.read_text().replace("Acme Holdings, Inc. |\n", "Acme Holdings, Inc. 123 |\n")
    )
    with pytest.raises(RunError):
        selection.select(run, RBOT_ROOT)
    now = state.read(run)
    assert now["steps"]["CP-0"]["status"] == "failed"
    assert now["steps"]["CP-0"]["current_edits"][-1]["result"]["findings"]
    assert now["approved_origins"] == original["approved_origins"]


def test_approval_readback_precedes_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from collections.abc import Iterator
    from contextlib import contextmanager

    from rbotlib import approve as approval

    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    before = outcome_bytes(run)
    staged = approval._staged

    @contextmanager
    def changed(run: Path, contents: list[str]) -> Iterator[list[Path]]:
        with staged(run, contents) as paths:
            own = run / bootstrap.CP0
            own.write_bytes(own.read_bytes() + b"\nConcurrent edit.\n")
            yield paths

    monkeypatch.setattr(approval, "_staged", changed)
    choice = approval.Choice(
        "FULL_CREDIT_ASSESSMENT", "full", False, "Approver", False, (), False, False
    )
    with pytest.raises(RunError, match="changed during Approval"):
        approval.approve(run, RBOT_ROOT, load_rules(RBOT_ROOT), choice)
    assert outcome_bytes(run) == before


def test_completion_readback_binds_captured_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    before = outcome_bytes(run)
    from rbotlib.contract import Contract
    from rbotlib.rules import Rules
    from rbotlib.validate import Finding, check

    def changed(
        text: str, contract: Contract, rules: Rules, run_dir: Path | None = None
    ) -> tuple[int, list[Finding]]:
        result = check(text, contract, rules, run_dir)
        own = run / bootstrap.CP0
        own.write_bytes(own.read_bytes() + b"\nConcurrent completion edit.\n")
        return result

    monkeypatch.setattr(bootstrap, "check", changed)
    with pytest.raises(RunError, match="changed during CP-0 completion"):
        bootstrap.complete_cp0(run, RBOT_ROOT, load_rules(RBOT_ROOT))
    assert outcome_bytes(run) == before


def test_registered_latest_is_checked_before_origin_recovery(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    accept.accept(run, RBOT_ROOT, "CP-0")
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    record = state.read(run)
    record.pop("approved_origins")
    (run / state.STATE).write_text(json.dumps(record))
    (run / "validate/CP-0.json").write_text("{}")
    before = outcome_bytes(run)
    with pytest.raises(RunError, match="latest validation mismatch"):
        selection.select(run, RBOT_ROOT)
    assert outcome_bytes(run) == before


def test_repeated_selection_preserves_state_after_clock_advances(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import UTC, datetime, timedelta

    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    selection.select(run, RBOT_ROOT)
    before = outcome_bytes(run)
    later = datetime.now(UTC) + timedelta(hours=1)

    class Clock(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Clock:
            return cls(
                later.year,
                later.month,
                later.day,
                later.hour,
                later.minute,
                later.second,
                tzinfo=UTC,
            )

    monkeypatch.setattr(state, "datetime", Clock)
    selection.select(run, RBOT_ROOT)
    assert outcome_bytes(run) == before


def test_completion_origin_is_not_captured_over_registered_accept_history(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == 0
    record = state.read(run)
    assert record["steps"]["CP-0"]["accept_history"]
    assert "completion_origin" not in record
    bootstrap.complete_cp0(run, RBOT_ROOT, load_rules(RBOT_ROOT))
    assert "completion_origin" not in state.read(run)
