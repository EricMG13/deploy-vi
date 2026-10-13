"""Adversarial acceptance evidence and path preservation regressions."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from state_receipt_assertions import outcome_bytes
from test_accept import accept, send
from test_bootstrap import pending, ready

from rbotlib import attempts, state
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT


def test_qa_and_hash_use_same_snapshot_and_changed_bytes_refuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import rbotlib.accept as owner
    from rbotlib.contract import Contract
    from rbotlib.rules import Rules
    from rbotlib.validate import Finding

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    before = outcome_bytes(run)
    from rbotlib.validate import check

    real = check

    def changed(
        text: str, contract: Contract, rules: Rules, selected: Path | None = None
    ) -> tuple[int, list[Finding]]:
        result = real(text, contract, rules, selected)
        own.write_bytes(own.read_bytes().replace(b"qa_status: Restricted", b"qa_status: Pass"))
        return result

    monkeypatch.setattr(owner, "check", changed)
    assert accept(run) == 1
    assert outcome_bytes(run) == before
    assert len(list((run / "validate/history/CP-0").iterdir())) == 1


@pytest.mark.parametrize(
    "field,value",
    [("run_id", "wrong"), ("qa_status", "Pass"), ("sequence", True), ("dispatch_sequence", True)],
)
def test_malformed_existing_history_is_not_trusted(
    tmp_path: Path, field: str, value: object
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    target = run / "validate/history/CP-0/000002.json"
    data = json.loads(target.read_bytes())
    data[field] = value
    target.write_text(json.dumps(data))
    state.update(
        run,
        lambda record: record["steps"]["CP-0"]["accept_history"].__setitem__(
            1, hashlib.sha256(target.read_bytes()).hexdigest()
        ),
    )
    before = outcome_bytes(run), target.read_bytes()
    assert accept(run) == 1
    assert before == (outcome_bytes(run), target.read_bytes())


def test_state_hash_must_match_immutable_validation(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    state.update(run, lambda record: record["steps"]["CP-0"].update(sha256="0" * 64))
    before = outcome_bytes(run)
    assert accept(run) == 1
    assert outcome_bytes(run) == before


def test_interrupted_publication_preserves_exact_event_and_recovers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    real = os.replace

    def interrupted(source: Path, destination: Path) -> None:
        if Path(destination).name == state.STATE and "module_publication" not in json.loads(
            Path(source).read_text()
        ):
            raise OSError("fixture interruption at final state publication")
        real(source, destination)

    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", interrupted)
        assert accept(run) == 1
    event = run / "validate/history/CP-0/000002.json"
    assert event.exists() and state.read(run)["steps"]["CP-0"]["status"] == "running"
    assert "module_publication" in state.read(run)
    saved = event.read_bytes()
    assert accept(run) == 0 and event.read_bytes() == saved
    assert state.read(run)["steps"]["CP-0"]["attempts"] == 1
    assert (run / state.LOCK).exists()


@pytest.mark.parametrize(
    "relative",
    [
        "handoffs/CP-0.md",
        "validate/CP-0.json",
        "validate/history/CP-0/000002.json",
        "log/rbot.log",
        "prepared/index.json",
        "inventory.json",
    ],
)
@pytest.mark.parametrize("kind", ["symlink", "hardlink", "directory", "fifo"])
def test_unsafe_accept_paths_preserve_state_sources_and_history(
    tmp_path: Path, relative: str, kind: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    target = run / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    other = tmp_path / "external"
    other.write_bytes(target.read_bytes() if target.exists() else b"external original")
    target.unlink(missing_ok=True)
    if kind == "symlink":
        target.symlink_to(other)
    elif kind == "hardlink":
        target.hardlink_to(other)
    elif kind == "directory":
        target.mkdir()
    else:
        os.mkfifo(target)
    before = outcome_bytes(run), other.read_bytes()
    assert accept(run) == 1
    assert before == (outcome_bytes(run), other.read_bytes())
    assert (run / state.LOCK).exists()


def test_missing_after_malformed_does_not_reuse_previous_hash(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    own.write_text("DONE 0")
    assert accept(run) == 2
    send(run, RBOT_ROOT, name="fixture-retry", retry=True)
    own.unlink()
    assert accept(run) == 1
    step = state.read(run)["steps"]["CP-0"]
    assert "sha256" not in step and "handoff" not in step


def test_unowned_or_corrupt_call_creates_no_lock_or_log(tmp_path: Path) -> None:
    own = tmp_path / "source"
    own.mkdir()
    assert accept(own) == 1 and not list(own.iterdir())
    run = pending(tmp_path, RBOT_ROOT)
    log = (run / "log/rbot.log").read_bytes()
    (run / state.STATE).write_text("corrupt")
    assert accept(run) == 1
    assert (run / "log/rbot.log").read_bytes() == log and (run / state.LOCK).exists()


def test_malformed_closed_front_matter_is_two(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    (run / "handoffs/CP-0.md").write_text("---\nnot front matter\n---\n")
    assert accept(run) == 2


def test_retry_interruption_after_partial_output_keeps_findings_and_slot(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    own.write_text("bad first")
    assert accept(run) == 2
    send(run, RBOT_ROOT, name="fixture-retry", retry=True)
    own.write_text("partial retry output")
    send(run, RBOT_ROOT, name="fixture-retry-partial-resend", retry=True)
    step = state.read(run)["steps"]["CP-0"]
    assert step["attempts"] == 2
    assert accept(run) == 2 and state.read(run)["steps"]["CP-0"]["status"] == "failed"


def test_retry_retains_exact_failed_bytes_and_prior_dispatch_message(tmp_path: Path) -> None:
    import base64

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    message = (run / "dispatch/CP-0.md").read_bytes()
    own = run / "handoffs/CP-0.md"
    failed = b"DONE 0\r\nbad validated fixture bytes"
    own.write_bytes(failed)
    assert accept(run) == 2
    send(run, RBOT_ROOT, name="fixture-retry", retry=True)
    own.write_bytes(b"different retry body")
    events = attempts.read_history(run, "CP-0", state.read(run)["steps"]["CP-0"])
    assert base64.b64decode(events[1]["handoff_base64"]) == failed
    assert events[0]["message"].encode() == message
    assert hashlib.sha256(failed).hexdigest() == events[1]["result"]["sha256"]


def test_library_unsafe_log_refuses_before_evidence_publication(tmp_path: Path) -> None:
    import rbotlib.accept as owner

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    target = run / "log/rbot.log"
    other = tmp_path / "other"
    target.rename(other)
    target.symlink_to(other)
    before = outcome_bytes(run), other.read_bytes()
    with pytest.raises(ValueError):
        owner.accept(run, RBOT_ROOT, "CP-0")
    assert before == (outcome_bytes(run), other.read_bytes())


@pytest.mark.parametrize(
    "field,value",
    [
        ("validated_at", "2000-01-01T00:00:00+00:00"),
        ("finished_at", "2000-01-01T00:00:00+00:00"),
        ("reason", "forged reason"),
        ("model", "forged model"),
    ],
)
def test_step_attribution_must_match_recorded_result(
    tmp_path: Path, field: str, value: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    state.update(run, lambda record: record["steps"]["CP-0"].update({field: value}))
    before = outcome_bytes(run)
    assert accept(run) == 1 and outcome_bytes(run) == before


def test_safe_io_log_records_failure_and_shared_lock_stays_owned(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    lock = run / state.LOCK
    original_lock = lock.read_bytes()
    lock.write_text("fixture owner")
    before = outcome_bytes(run)
    assert accept(run) == 1
    assert lock.read_text() == "fixture owner" and outcome_bytes(run) == before
    lock.write_bytes(original_lock)
    (run / "handoffs/CP-0.md").unlink()
    assert accept(run) == 1
    assert "\t1\n" in (run / "log/rbot.log").read_text()


@pytest.mark.parametrize("orphan", [False, True])
def test_approval_requires_current_registered_acceptance_when_receipts_exist(
    tmp_path: Path, orphan: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    if orphan:
        real = os.replace

        def interrupted(source: Path, destination: Path) -> None:
            if Path(destination).name == state.STATE:
                raise OSError("fixture interrupted accept publication")
            real(source, destination)

        with monkeypatch.context() as patch:
            patch.setattr(os, "replace", interrupted)
            assert accept(run) == 1
    ready(run, RBOT_ROOT)
    before = outcome_bytes(run)
    args = [
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
        "Fixture",
    ]
    assert main(args) == 1
    assert run.exists() and outcome_bytes(run) == before
    assert (run / state.LOCK).exists()


@pytest.mark.parametrize("change", ["alphabet", "length", "qa"])
def test_persisted_snapshot_is_strictly_decoded_and_bound(tmp_path: Path, change: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    target = run / "validate/history/CP-0/000002.json"
    event = json.loads(target.read_bytes())
    if change == "alphabet":
        event["handoff_base64"] += "!"
    elif change == "length":
        event["handoff_bytes"] = 1
    else:
        event["qa_status"] = "Pass"
    target.write_text(json.dumps(event))

    def forged(record: state.Record) -> None:
        step = record["steps"]["CP-0"]
        step["accept_history"][1] = hashlib.sha256(target.read_bytes()).hexdigest()
        if change == "qa":
            step["qa_status"] = "Pass"

    state.update(run, forged)
    before = outcome_bytes(run), target.read_bytes()
    assert accept(run) == 1
    assert before == (outcome_bytes(run), target.read_bytes())


def test_oversize_failed_snapshot_keeps_all_bytes_and_checker_cap(tmp_path: Path) -> None:
    import base64

    from rbotlib.validate import MAX_HANDOFF_BYTES

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    raw = own.read_bytes() + b"\n" + b"x" * MAX_HANDOFF_BYTES
    own.write_bytes(raw)
    assert accept(run) == 2
    step = state.read(run)["steps"]["CP-0"]
    event = attempts.read_history(run, "CP-0", step)[-1]
    assert event["handoff_bytes"] == len(raw)
    assert base64.b64decode(event["handoff_base64"], validate=True) == raw
    assert any(f["code"] == "too_large" for f in event["result"]["findings"])


@pytest.mark.parametrize(
    "field,value", [("run_id", "wrong-run"), ("issuer_id", "WRONG"), ("module_id", "CP-1A")]
)
def test_analytical_identity_four_despite_checker_valid_blocked_bytes(
    tmp_path: Path, field: str, value: str
) -> None:
    from test_bootstrap import approve
    from test_modules import _blocked

    from rbotlib.contract import load_contract
    from rbotlib.rules import load_rules
    from rbotlib.validate import check

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    send(run, RBOT_ROOT, "CP-1")
    rules = load_rules(RBOT_ROOT)
    contract = load_contract(RBOT_ROOT / "modules/CP-1/contract.json", rules)
    text = (Path(__file__).parent / "fixtures/handoffs/CP-1.md").read_text()
    text = (
        _blocked(text, contract)
        .replace("run_id: 20261011-czr-full-credit-assessment", f"run_id: {run.name}")
        .replace("issuer_id: CZR", "issuer_id: ACME")
    )
    assert check(text, contract, rules, run) == (3, [])
    old = next(line for line in text.splitlines() if line.startswith(field + ":"))
    own = run / "handoffs/CP-1.md"
    own.write_text(text.replace(old, f"{field}: {value}"))
    assert accept(run, module="CP-1") == 4
    step = state.read(run)["steps"]["CP-1"]
    assert (
        step["status"] == "failed"
        and step["sha256"] == hashlib.sha256(own.read_bytes()).hexdigest()
    )


def test_immutable_event_bytes_hash_is_not_advisory(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    target = run / "validate/history/CP-0/000001.json"
    target.write_bytes(target.read_bytes() + b"\n ")
    before = outcome_bytes(run), target.read_bytes()
    assert accept(run) == 1
    assert before == (outcome_bytes(run), target.read_bytes())
