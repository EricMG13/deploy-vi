"""Caller-reported dispatch events are fixtures, never physical send proof."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from state_receipt_assertions import outcome_bytes
from test_bootstrap import pending

from rbotlib import attempts, dispatch, state
from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


def receipt(run: Path, root: Path, name: str = "fixture-send") -> state.Record:
    text = dispatch.prepare_message(run, root, "CP-0")
    return attempts.register_dispatch(
        run,
        root,
        "CP-0",
        attempts.DispatchReceipt(
            name, "fixture-controller", hashlib.sha256(text.encode()).hexdigest()
        ),
    )


def test_preparation_is_not_dispatch_and_receipt_is_idempotent(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    before = outcome_bytes(run)
    text = dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    assert outcome_bytes(run) == before
    event = receipt(run, RBOT_ROOT)
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "running" and step["attempts"] == 1
    assert event["slot"] == 1 and event["reporter"] == "fixture-controller"
    assert event["message_sha256"] == hashlib.sha256(text.encode()).hexdigest()
    assert event["model"] is None and event["worker_started_at"] is None
    before = outcome_bytes(run)
    assert receipt(run, RBOT_ROOT) == event
    assert outcome_bytes(run) == before
    other = receipt(run, RBOT_ROOT, "fixture-interruption-resend")
    assert other["slot"] == 1 and state.read(run)["steps"]["CP-0"]["attempts"] == 1
    assert len(attempts.read_history(run, "CP-0", state.read(run)["steps"]["CP-0"])) == 2


def test_receipt_requires_current_qualified_exact_message(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    before = outcome_bytes(run)
    with pytest.raises(RunError, match=r"CP-0\.md"):
        attempts.register_dispatch(
            run, RBOT_ROOT, "CP-0", attempts.DispatchReceipt("id", "controller", "0" * 64)
        )
    text = dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    (run / "dispatch/CP-0.md").write_text(text + "changed")
    with pytest.raises(RunError, match="message"):
        attempts.register_dispatch(
            run,
            RBOT_ROOT,
            "CP-0",
            attempts.DispatchReceipt("id", "controller", hashlib.sha256(text.encode()).hexdigest()),
        )
    assert outcome_bytes(run) == before
    assert (run / state.LOCK).exists()


def test_public_receipt_command_and_duplicate_conflict(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    text = dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    argv = [
        "dispatch-receipt",
        "--run",
        str(run),
        "--module",
        "CP-0",
        "--receipt",
        "fixture-id",
        "--reporter",
        "controller",
        "--message-sha256",
        hashlib.sha256(text.encode()).hexdigest(),
    ]
    assert main(argv) == 0
    before = outcome_bytes(run)
    assert main([*argv, "--model", "fixture-model"]) == 1
    assert outcome_bytes(run) == before


@settings(deadline=None)
@given(names=st.lists(st.sampled_from(["one", "two", "three"]), min_size=1, max_size=8))
def test_interruption_receipts_keep_one_slot(
    names: list[str], tmp_path_factory: pytest.TempPathFactory
) -> None:
    run = pending(tmp_path_factory.mktemp("receipt-property"), RBOT_ROOT)
    for name in names:
        receipt(run, RBOT_ROOT, name)
    step = state.read(run)["steps"]["CP-0"]
    assert step["attempts"] == 1
    assert len(attempts.read_history(run, "CP-0", step)) == len(set(names))


@pytest.mark.parametrize("changed", ["source", "root", "log", "terminal"])
def test_receipt_refuses_changed_context_or_unsafe_publication(
    tmp_path: Path, changed: str
) -> None:
    import shutil

    root = shutil.copytree(RBOT_ROOT, tmp_path / "copied root")
    run = pending(tmp_path, root)
    text = dispatch.prepare_message(run, root, "CP-0")
    item = attempts.DispatchReceipt(
        "fixture", "controller", hashlib.sha256(text.encode()).hexdigest()
    )
    if changed == "source":
        (run.parent.parent / "acme_10k.txt").write_text("changed")
    elif changed == "root":
        (root / "modules/CP-0/contract.json").write_text("{}")
    elif changed == "log":
        target = run / "log/rbot.log"
        other = tmp_path / "other"
        target.rename(other)
        target.hardlink_to(other)
    else:
        state.set_status(run, "CP-0", "failed", "actual named executor failure")
    before = outcome_bytes(run)
    with pytest.raises(ValueError):
        attempts.register_dispatch(run, root, "CP-0", item)
    assert outcome_bytes(run) == before and (run / state.LOCK).exists()


def test_claimed_model_and_worker_time_are_attributed_only_to_receipt(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    text = dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    model = "fixture-reported-label"
    worker = "2026-10-01T12:00:00+00:00"
    item = attempts.DispatchReceipt(
        "fixture", "fixture-reporter", hashlib.sha256(text.encode()).hexdigest(), model, worker
    )
    event = attempts.register_dispatch(run, RBOT_ROOT, "CP-0", item)
    assert event["model"] == model and event["worker_started_at"] == worker
    step = state.read(run)["steps"]["CP-0"]
    assert step["started_at"] == event["observed_at"] and step["started_at"] != worker
    assert step["started_at_basis"] == "controller_dispatch_report"


def test_history_reader_proves_owned_state_before_any_event_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    event = receipt(run, RBOT_ROOT)
    step = state.read(run)["steps"]["CP-0"]
    (run / state.STATE).write_text("corrupt")
    reads: list[Path] = []
    real = Path.read_bytes

    def observed(path: Path) -> bytes:
        if path.name == f"{event['sequence']:06d}.json":
            reads.append(path)
        return real(path)

    monkeypatch.setattr(Path, "read_bytes", observed)
    with pytest.raises(ValueError):
        attempts.read_history(run, "CP-0", step)
    assert reads == []
