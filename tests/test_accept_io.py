"""Attempted own-byte I/O failures are terminal, with honest retained snapshots."""

from __future__ import annotations

import base64
import errno
import hashlib
import json
import shutil
from pathlib import Path

import pytest
from state_receipt_assertions import artifact_bytes, outcome_bytes
from test_accept import accept, send
from test_bootstrap import pending

from rbotlib import attempts, dispatch, state
from rbotlib.accept import accept as library_accept
from rbotlib.contract import Contract
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import Finding, check


def _assert_evidence(
    run: Path, result: state.Record, receipt: state.Record, raw: bytes, observation: str
) -> None:
    record = state.read(run)
    step = record["steps"]["CP-0"]
    assert step["status"] == "failed" and step["attempts"] == 1
    assert result["exit"] == step["validate_exit"] == 1
    assert result["findings"][0]["code"] == "execution_error"
    assert str(run / "handoffs/CP-0.md") in result["findings"][0]["message"]
    assert "fixture own-byte read failure" in step["reason"]
    assert record["extension"] == {"keep": [None, "actual"]}
    assert step["model"] == receipt["model"]
    assert step["started_at"] == receipt["observed_at"]
    assert step["started_at_basis"] == "controller_dispatch_report"
    assert step["finished_at"] == step["validated_at"] == result["at"]
    assert step["finished_at_basis"] == "controller_validation"
    events = attempts.read_history(run, "CP-0", step)
    assert len(events) == 2 and events[0] == receipt
    event = events[-1]
    assert event["result"] == result and event["qa_status"] is None
    assert event["dispatch_sequence"] == receipt["sequence"] and event["slot"] == 1
    assert event["run_id"] == record["run_id"] and event["module"] == "CP-0"
    if observation == "first":
        assert result["sha256"] is event["handoff_base64"] is event["handoff_bytes"] is None
        assert "sha256" not in step and "handoff" not in step
    else:
        assert result["sha256"] == step["sha256"] == hashlib.sha256(raw).hexdigest()
        assert event["handoff_bytes"] == len(raw)
        assert base64.b64decode(event["handoff_base64"], validate=True) == raw


@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("public", [False, True])
@pytest.mark.parametrize(
    "fault",
    [(phase, error) for phase in ("first", "verification") for error in (errno.EACCES, errno.EIO)],
)
def test_attempted_owned_read_failure_is_terminal_and_immutable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected: bool,
    public: bool,
    fault: tuple[str, int],
) -> None:
    observation, error = fault
    root = shutil.copytree(RBOT_ROOT, tmp_path / "selected ' root") if selected else RBOT_ROOT
    run = pending(tmp_path, root)
    state.update(run, lambda record: record.update(extension={"keep": [None, "actual"]}))
    message = dispatch.prepare_message(run, root, "CP-0")
    receipt = attempts.register_dispatch(
        run,
        root,
        "CP-0",
        attempts.DispatchReceipt(
            "fixture-io-send",
            "fixture-controller",
            hashlib.sha256(message.encode()).hexdigest(),
            "fixture-reported-model",
            "2026-10-01T12:00:00+00:00",
        ),
    )
    own = run / "handoffs/CP-0.md"
    raw = own.read_bytes()
    sources = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    real = Path.read_bytes
    reads = 0

    def denied(path: Path) -> bytes:
        nonlocal reads
        if path == own:
            reads += 1
            if observation == "first" or reads % 2 == 0:
                raise OSError(error, "fixture own-byte read failure", str(path))
        return real(path)

    def invoke() -> state.Record:
        if public:
            assert accept(run, root) == 1
            latest: state.Record = json.loads((run / "validate/CP-0.json").read_text())
            return latest
        return library_accept(run, root, "CP-0")

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", denied)
        result = invoke()
        _assert_evidence(run, result, receipt, raw, observation)
        assert reads == (1 if observation == "first" else 2)
        preserved = {
            str(p.relative_to(run)): outcome_bytes(run) if p.name == state.STATE else real(p)
            for p in [run / state.STATE, *(run / "validate").rglob("*.json")]
        }
        assert invoke() == result
        assert preserved == {name: artifact_bytes(run, name) for name in preserved}
        assert (run / state.LOCK).exists()
    assert own.read_bytes() == raw
    with pytest.raises(RunError, match="validated bytes changed"):
        library_accept(run, root, "CP-0")
    assert accept(run, root) == 1
    assert preserved == {name: artifact_bytes(run, name) for name in preserved}
    with pytest.raises(RunError, match="pending/running"):
        send(run, root, name="fixture-illegal-retry", retry=True)
    assert preserved == {name: artifact_bytes(run, name) for name in preserved}
    assert (run / state.LOCK).exists()
    assert {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()} == sources
    if public:
        assert "\t1\n" in (run / "log/rbot.log").read_text()


def test_initial_read_error_cannot_be_erased_by_a_readable_second_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    real = Path.read_bytes
    reads = 0

    def first_only(path: Path) -> bytes:
        nonlocal reads
        if path == own:
            reads += 1
            if reads == 1:
                raise PermissionError(errno.EACCES, "fixture transient denial", str(path))
        return real(path)

    monkeypatch.setattr(Path, "read_bytes", first_only)
    result = library_accept(run, RBOT_ROOT, "CP-0")
    assert result["exit"] == 1 and result["sha256"] is None and reads == 1
    assert state.read(run)["steps"]["CP-0"]["status"] == "failed"


def test_verification_unsafe_replacement_is_preflight_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import rbotlib.accept as owner

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    external = tmp_path / "external"
    external.write_bytes(own.read_bytes())
    before = outcome_bytes(run), external.read_bytes()
    real = check

    def linked(
        text: str, contract: Contract, rules: Rules, selected: Path | None = None
    ) -> tuple[int, list[Finding]]:
        result = real(text, contract, rules, selected)
        own.unlink()
        own.symlink_to(external)
        return result

    monkeypatch.setattr(owner, "check", linked)
    assert accept(run) == 1
    assert before == (outcome_bytes(run), external.read_bytes())
    assert len(list((run / "validate/history/CP-0").iterdir())) == 1
    assert (run / state.LOCK).exists()


def test_missing_verification_retains_actual_initial_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import rbotlib.accept as owner

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    raw = own.read_bytes()

    def removed(
        text: str, contract: Contract, rules: Rules, selected: Path | None = None
    ) -> tuple[int, list[Finding]]:
        result = check(text, contract, rules, selected)
        own.unlink()
        return result

    try:
        with monkeypatch.context() as patch:
            patch.setattr(owner, "check", removed)
            result = library_accept(run, RBOT_ROOT, "CP-0")
        step = state.read(run)["steps"]["CP-0"]
        event = attempts.read_history(run, "CP-0", step)[-1]
        assert result["exit"] == 1 and step["status"] == "failed"
        assert result["sha256"] == hashlib.sha256(raw).hexdigest()
        assert base64.b64decode(event["handoff_base64"], validate=True) == raw
        assert event["qa_status"] is None and "No such file" in step["reason"]
    finally:
        own.write_bytes(raw)
    assert accept(run) == 1 and state.read(run)["steps"]["CP-0"] == step


def test_read_denial_after_malformed_retry_preserves_prior_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    own.write_bytes(b"failed first\r\nDONE 0")
    assert accept(run) == 2
    before = {p.name: p.read_bytes() for p in (run / "validate/history/CP-0").iterdir()}
    send(run, RBOT_ROOT, name="fixture-second", retry=True)
    real = Path.read_bytes

    def denied(path: Path) -> bytes:
        if path == own:
            raise PermissionError(errno.EACCES, "fixture retry denial", str(path))
        return real(path)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", denied)
        assert accept(run) == 1 and accept(run) == 1
        step = state.read(run)["steps"]["CP-0"]
        events = attempts.read_history(run, "CP-0", step)
    assert step["status"] == "failed" and step["attempts"] == 2
    assert "sha256" not in step and "handoff" not in step
    assert [e["slot"] for e in events] == [1, 1, 2, 2]
    assert all(
        (run / "validate/history/CP-0" / name).read_bytes() == raw for name, raw in before.items()
    )
    assert base64.b64decode(events[1]["handoff_base64"]) == own.read_bytes()
    assert events[-1]["result"]["sha256"] is None
    assert (run / state.LOCK).exists()


@pytest.mark.parametrize("observed", [0, 3, 2, 4, 1])
def test_verification_io_retains_already_observed_findings_and_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, observed: int
) -> None:
    import rbotlib.accept as owner

    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    if observed == 3:
        own.write_bytes(own.read_bytes().replace(b"qa_status: Restricted", b"qa_status: Blocked"))
    elif observed == 2:
        own.write_bytes(b"malformed observed first")
    elif observed == 4:
        own.write_bytes(own.read_bytes().replace(run.name.encode(), b"wrong-run"))
    elif observed == 1:
        own.write_bytes(b"\xff")
    original, _, raw = owner._observe(run, RBOT_ROOT, "CP-0", state.read(run))
    assert original["exit"] == observed
    real = Path.read_bytes
    reads = 0

    def denied(path: Path) -> bytes:
        nonlocal reads
        if path == own:
            reads += 1
            if reads % 2 == 0:
                raise PermissionError(errno.EACCES, "fixture verification denial", str(path))
        return real(path)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", denied)
        result = library_accept(run, RBOT_ROOT, "CP-0")
        assert result["exit"] == 1
        assert result["findings"][:-1] == original["findings"]
        assert result["findings"][-1]["code"] == "execution_error"
        assert "fixture verification denial" in result["findings"][-1]["message"]
        step = state.read(run)["steps"]["CP-0"]
        event = attempts.read_history(run, "CP-0", step)[-1]
        assert step["status"] == "failed" and step["attempts"] == 1
        assert event["result"] == result and event["qa_status"] is None
        assert result["sha256"] == original["sha256"]
        assert base64.b64decode(event["handoff_base64"], validate=True) == raw
        assert step["validated_at"] == step["finished_at"] == result["at"]
        before = outcome_bytes(run), (run / "validate/CP-0.json").read_bytes()
        assert library_accept(run, RBOT_ROOT, "CP-0") == result
        assert before == (
            outcome_bytes(run),
            (run / "validate/CP-0.json").read_bytes(),
        )
    assert (run / state.LOCK).exists()
    assert accept(run) == 1 and state.read(run)["steps"]["CP-0"] == step
    with pytest.raises(RunError, match="pending/running"):
        send(run, RBOT_ROOT, name="fixture-illegal-outcome-retry", retry=True)
