# Plan06.5 executed receipts source/test replay

Approved predecessor: `6fa314d6b8edb786aa1dbeba65f5a350a811930f`, tree `6733ba323f00b8b69621ddf965a483842e2a0e45`. This document records locally executed05 awaiting fresh ordinary/sensitive reviews. Exact binary/full-index per-boundary patches/tree/lock/cap proof are in main staging task-05-proof.json. These complete AST-parsable blocks match current source bytes; the patches replay integration without inferred manual edits.

Consume the existing checked state/Approval lock and Task04 pure qualification, actual selected-root contracts/rules/catalog/source context, and reported dispatch events. Preparation never sends. Receipts are trusted caller reports, not signed/network proof. attempts counts validation slots1/2; distinct reported interruption resends remain individually attributable within a slot. Latest validation retains the prescribed four fields; immutable relative history keeps exact messages and raw-byte Handoff snapshots plus code/QA/receipt links. Strict base64 length/canonical decode/hash checks are local encoding checks, not authenticity. Missing bytes have null hash; unknown worker/model evidence stays unknown. Approved CP0 uses only registered pending lineage. Orphan/latest mismatch refuses for owner09. Python3.11 primary base64 docs were read after selection before commit;3.11/Windows remain unexercised.

## `rbot/scripts/rbotlib/attempts.py`

<!-- replay-path: rbot/scripts/rbotlib/attempts.py -->
```python
"""Attributable caller reports, not network proof. attempts counts validation slots.

Every distinct dispatch receipt is immutable evidence, including interruption resends
within a slot. A first malformed validation opens exactly one findings-bearing retry.
Publication is evidence then latest validation then checked state; orphan/mismatch
refuses further work pending the recovery owner. No automatic evidence deletion.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from rbotlib import dispatch, state
from rbotlib.fsio import write_atomic
from rbotlib.handoff import parse
from rbotlib.inventory import RunError, output_path


@dataclass(frozen=True)
class DispatchReceipt:
    receipt: str
    reporter: str
    message_sha256: str
    model: str | None = None
    worker_started_at: str | None = None


class Duplicate(RunError):
    """A checked unchanged result; unwinds state.update without rewriting state."""

    def __init__(self, event: state.Record) -> None:
        super().__init__("identical evidence already registered")
        self.event = event


def stamp() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def encode(event: state.Record) -> str:
    return json.dumps(event, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def event_path(run: Path, module: str, sequence: int) -> Path:
    return dispatch._target(run, f"validate/history/{module}/{sequence:06d}.json")


def _result(value: object) -> None:
    state._fields(
        value,
        {
            "exit": lambda v: type(v) is int and v in range(5),
            "sha256": state._nullable(state._sha),
            "at": state._stamp,
            "findings": lambda v: (
                isinstance(v, list)
                and all(
                    isinstance(f, dict)
                    and set(f) == {"code", "message"}
                    and all(state._text(f[k]) for k in f)
                    for f in v
                )
            ),
        },
        "validation evidence",
    )
    if not isinstance(value, dict) or set(value) != {"exit", "sha256", "at", "findings"}:
        raise RunError("validation evidence: unexpected fields")
    if bool(value["findings"]) != (value["exit"] in (1, 2, 4)):
        raise RunError("validation evidence: findings differ from exit taxonomy")


def _event(event: state.Record, module: str, sequence: int) -> None:
    state._fields(
        event,
        {
            "schema": lambda v: v == "rbot-attempt-event/1",
            "module": lambda v: v == module,
            "sequence": lambda v: type(v) is int and v == sequence,
            "slot": lambda v: type(v) is int and v in (1, 2),
            "run_id": state._text,
            "observed_at": state._stamp,
            "event": lambda v: v in ("dispatch_report", "validation"),
        },
        "attempt evidence",
    )
    common = {"schema", "module", "sequence", "slot", "run_id", "observed_at", "event"}
    extra = (
        {"receipt", "reporter", "message_sha256", "message", "model", "worker_started_at"}
        if event["event"] == "dispatch_report"
        else {"result", "qa_status", "handoff_base64", "handoff_bytes", "dispatch_sequence"}
    )
    if set(event) != common | extra:
        raise RunError("attempt evidence: unexpected fields")
    if event["event"] == "dispatch_report":
        state._fields(
            event,
            {
                "receipt": state._text,
                "reporter": state._text,
                "message_sha256": state._sha,
                "message": state._text,
                "model": state._nullable(state._text),
                "worker_started_at": state._nullable(state._stamp),
            },
            "dispatch evidence",
        )
        if hashlib.sha256(event["message"].encode()).hexdigest() != event["message_sha256"]:
            raise RunError("dispatch evidence: exact message hash differs")
    else:
        _validation_event(event, sequence)


def _validation_event(event: state.Record, sequence: int) -> None:
    _result(event.get("result"))
    _snapshot(event)
    state._fields(
        event,
        {"qa_status": lambda v: v in (None, "Pass", "Restricted", "Blocked")},
        "validation evidence",
    )
    code = event["result"]["exit"]
    expected = ("Pass", "Restricted") if code == 0 else ("Blocked",) if code == 3 else (None,)
    if event["qa_status"] not in expected:
        raise RunError("validation evidence: QA differs from the exit taxonomy")
    state._fields(
        event,
        {"dispatch_sequence": lambda v: type(v) is int and 0 < v < sequence},
        "validation evidence",
    )


def _snapshot(event: state.Record) -> None:
    value = event.get("handoff_base64")
    size = event.get("handoff_bytes")
    sha = event["result"]["sha256"]
    if sha is None:
        if value is not None or size is not None or event["result"]["exit"] != 1:
            raise RunError("validation evidence: missing Handoff cannot have a snapshot/hash")
        return
    if not isinstance(value, str) or type(size) is not int or size < 0:
        raise RunError("validation evidence: exact Handoff snapshot is required")
    if len(value) != 4 * ((size + 2) // 3):
        raise RunError("validation evidence: encoded snapshot length differs")
    try:
        raw = base64.b64decode(value, validate=True)
    except ValueError as exc:
        raise RunError(f"validation evidence: malformed base64 snapshot ({exc})") from exc
    if len(raw) != size or base64.b64encode(raw).decode() != value:
        raise RunError("validation evidence: decoded snapshot length/canonical encoding differs")
    if hashlib.sha256(raw).hexdigest() != sha:
        raise RunError("validation evidence: exact Handoff snapshot hash differs")
    _snapshot_front(event, raw)


def _snapshot_front(event: state.Record, raw: bytes) -> None:
    if event["result"]["exit"] not in (0, 3):
        return
    front = parse(raw.decode("utf-8")).front_matter
    expected = {
        "module_id": event["module"],
        "run_id": event["run_id"],
        "qa_status": event["qa_status"],
    }
    if any(front.get(k) != v for k, v in expected.items()):
        raise RunError("validation evidence: successful snapshot identity/QA differs")


def _dispatch_slot(
    event: state.Record, slot: int, validation: state.Record | None, receipts: set[str]
) -> int:
    expected = slot + 1 if slot == 0 or validation is not None else slot
    if validation is not None and validation["exit"] != 2:
        raise RunError("attempt evidence: dispatch after terminal validation")
    if event["slot"] != expected or event["receipt"] in receipts:
        raise RunError("attempt evidence: invalid retry slot or duplicate receipt")
    return expected


def _ordered(events: list[state.Record], step: state.Record) -> None:
    slot, validation = 0, None
    receipts: set[str] = set()
    dispatch_sequence = 0
    for event in events:
        if event["event"] == "dispatch_report":
            slot = _dispatch_slot(event, slot, validation, receipts)
            validation = None
            dispatch_sequence = event["sequence"]
            receipts.add(event["receipt"])
        else:
            if (
                validation is not None
                or event["slot"] != slot
                or event["dispatch_sequence"] != dispatch_sequence
            ):
                raise RunError("attempt evidence: validation has no current dispatch")
            validation = event["result"]
    if slot != step.get("attempts", 0):
        raise RunError("attempt evidence: state attempts differ from immutable slots")
    if events and (
        step.get("started_at") != events[0]["observed_at"]
        or step.get("started_at_basis") != "controller_dispatch_report"
    ):
        raise RunError("attempt evidence: start observation differs from first dispatch report")
    if validation is not None:
        _consistent(step, events[-1], events[dispatch_sequence - 1])


def _consistent(step: state.Record, event: state.Record, receipt: state.Record) -> None:
    result = event["result"]
    code = result["exit"]
    status = (
        "accepted"
        if code == 0
        else "blocked"
        if code == 3
        else "running"
        if code == 2 and event["slot"] == 1
        else "failed"
    )
    expected = {
        "status": status,
        "validate_exit": code,
        "sha256": result["sha256"],
        "validated_at": result["at"],
        "reason": "; ".join(f["message"] for f in result["findings"]),
        "model": receipt["model"],
    }
    if status != "running":
        expected["finished_at"] = result["at"]
        expected["finished_at_basis"] = "controller_validation"
    if code in (0, 3):
        expected["qa_status"] = event["qa_status"]
    if any(step.get(k) != v for k, v in expected.items()):
        raise RunError("attempt evidence: latest validation differs from checked state")


def _load_history(run: Path, module: str, hashes: list[str]) -> list[state.Record]:
    folder = output_path(run, f"validate/history/{module}")
    if folder.exists() and not folder.is_dir():
        raise RunError(f"{folder}: history must be a directory")
    names = {p.name for p in folder.iterdir()} if folder.exists() else set()
    if names != {f"{n:06d}.json" for n in range(1, len(hashes) + 1)}:
        raise RunError("attempt evidence: orphan/missing event; recovery owner required")
    events = []
    for n, sha in enumerate(hashes, 1):
        path = dispatch._file(run, f"validate/history/{module}/{n:06d}.json")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise RunError(f"{path}: immutable evidence hash changed")
        event = json.loads(raw, object_pairs_hook=state._pairs)
        _event(event, module, n)
        events.append(event)
    return events


def _history_identity(record: state.Record, module: str, events: list[state.Record]) -> None:
    lineage = record.get("cp0_lineage") if module == "CP-0" else None
    identities = {record["run_id"]}
    if lineage:
        identities.add(lineage["pending_run_id"])
    if any(e["run_id"] not in identities for e in events):
        raise RunError("attempt evidence: event run identity is not registered")


def _latest(run: Path, module: str, events: list[state.Record]) -> None:
    validations = [e["result"] for e in events if e["event"] == "validation"]
    latest = dispatch._target(run, f"validate/{module}.json")
    if validations and (
        not latest.is_file()
        or json.loads(latest.read_text(), object_pairs_hook=state._pairs) != validations[-1]
    ):
        raise RunError("attempt evidence: latest validation mismatch; recovery owner required")
    if not validations and latest.exists():
        raise RunError("attempt evidence: unregistered latest validation; recovery owner required")


def read_history(run: Path, module: str, step: state.Record) -> list[state.Record]:
    """Read every guarded hash-bound event; refuse corrupt/extra/interrupted publication."""
    run = state.run_path(run)
    record = state.read(run)
    if target(record, module) != step:
        raise RunError("attempt evidence: supplied step differs from current owned state")
    hashes = step.get("accept_history", [])
    if not isinstance(hashes, list) or not all(state._sha(h) for h in hashes):
        raise RunError("attempt evidence: invalid state hash list")
    events = _load_history(run, module, hashes)
    _history_identity(record, module, events)
    _ordered(events, step)
    _latest(run, module, events)
    return events


def append_event(
    run: Path, module: str, step: state.Record, events: list[state.Record], event: state.Record
) -> None:
    """Preflight all evidence destinations; change metadata without publishing."""
    sequence = len(events) + 1
    event.update(
        schema="rbot-attempt-event/1", module=module, sequence=sequence, observed_at=stamp()
    )
    _event(event, module, sequence)
    target = event_path(run, module, sequence)
    if target.exists():
        raise RunError(f"{target}: immutable evidence already exists")
    dispatch._target(run, f"validate/{module}.json")
    step.setdefault("accept_history", []).append(hashlib.sha256(encode(event).encode()).hexdigest())


def publish_event(run: Path, module: str, event: state.Record) -> None:
    target = event_path(run, module, event["sequence"])
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RunError(f"{target}: immutable evidence already exists")
    write_atomic(event_path(run, module, event["sequence"]), encode(event))
    if event["event"] == "validation":
        write_atomic(dispatch._target(run, f"validate/{module}.json"), encode(event["result"]))


def target(record: state.Record, module: str) -> state.Record:
    if module not in ("CP-0", "CP-1", "CP-1A", "CP-1B", "CP-1D", "CP-2", "CP-3", "CP-5", "CP-6"):
        raise RunError(f"unsupported module target {module!r}")
    step = record["steps"].get(module)
    if step is None or step["kind"] != "module":
        raise RunError(f"{module}: undeclared module target")
    checked: state.Record = step
    return checked


def _duplicate(events: list[state.Record], values: state.Record) -> None:
    for event in events:
        if event["event"] == "dispatch_report" and event["receipt"] == values["receipt"]:
            if any(event[k] != v for k, v in values.items()):
                raise RunError("dispatch receipt: conflicting duplicate")
            raise Duplicate(event)


def _receipt_event(
    run: Path, root: Path, module: str, record: state.Record, receipt: DispatchReceipt
) -> state.Record:
    step = target(record, module)
    events = read_history(run, module, step)
    values = asdict(receipt)
    _duplicate(events, values)
    if step["status"] not in ("pending", "running"):
        raise RunError(f"{module}: terminal step cannot dispatch")
    retry = bool(events and events[-1]["event"] == "validation")
    validations = [e for e in events if e["event"] == "validation"]
    findings = f"validate/{module}.json" if validations else None
    text = dispatch.qualified_message(run, root, module, record, findings)
    raw = dispatch._file(run, f"dispatch/{module}.md").read_bytes()
    if raw != text.encode() or hashlib.sha256(raw).hexdigest() != receipt.message_sha256:
        raise RunError("dispatch receipt: current qualified message/hash differs")
    slot = step.get("attempts", 0) + (1 if retry or not events else 0)
    event = dict(values, event="dispatch_report", slot=slot, run_id=record["run_id"], message=text)
    append_event(run, module, step, events, event)
    step.update(status="running", attempts=slot)
    step.setdefault("started_at", event["observed_at"])
    step.setdefault("started_at_basis", "controller_dispatch_report")
    _ordered([*events, event], step)
    return event


def register_dispatch(run: Path, root: Path, module: str, receipt: DispatchReceipt) -> state.Record:
    """Register an authorized controller's report; duplicate identical receipts count once.

    observed_at/started_at are controller observations; provider timing is unknown
    unless the caller supplies worker_started_at. Caller labels are not authenticated.
    """
    run, root = state.run_path(run), dispatch._root(root)
    state.read(run)
    dispatch._target(run, "log/rbot.log")
    event: state.Record = {}

    def change(record: state.Record) -> None:
        event.update(_receipt_event(run, root, module, record, receipt))

    try:
        state.update(run, change, lambda: publish_event(run, module, event))
    except Duplicate as duplicate:
        return duplicate.event
    return event


def run_command(args: argparse.Namespace) -> int:
    try:
        event = register_dispatch(
            Path(args.run_dir),
            args.root,
            args.module,
            DispatchReceipt(
                args.receipt, args.reporter, args.message_sha256, args.model, args.worker_started_at
            ),
        )
        print(encode(event), end="")
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print(f"error: dispatch receipt: {exc}")
        return 1
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser(
        "dispatch-receipt", help="record a trusted caller's dispatch report, not network proof"
    )
    parser.add_argument("--run", dest="run_dir", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--reporter", required=True)
    parser.add_argument("--message-sha256", required=True)
    parser.add_argument("--model")
    parser.add_argument("--worker-started-at")
    parser.set_defaults(run=run_command, log_run_guard=state.log_run_path)
```

## `tests/test_attempts.py`

<!-- replay-path: tests/test_attempts.py -->
```python
"""Caller-reported dispatch events are fixtures, never physical send proof."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
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
    before = (run / state.STATE).read_bytes()
    text = dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    assert (run / state.STATE).read_bytes() == before
    event = receipt(run, RBOT_ROOT)
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "running" and step["attempts"] == 1
    assert event["slot"] == 1 and event["reporter"] == "fixture-controller"
    assert event["message_sha256"] == hashlib.sha256(text.encode()).hexdigest()
    assert event["model"] is None and event["worker_started_at"] is None
    before = (run / state.STATE).read_bytes()
    assert receipt(run, RBOT_ROOT) == event
    assert (run / state.STATE).read_bytes() == before
    other = receipt(run, RBOT_ROOT, "fixture-interruption-resend")
    assert other["slot"] == 1 and state.read(run)["steps"]["CP-0"]["attempts"] == 1
    assert len(attempts.read_history(run, "CP-0", state.read(run)["steps"]["CP-0"])) == 2


def test_receipt_requires_current_qualified_exact_message(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    before = (run / state.STATE).read_bytes()
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
    assert (run / state.STATE).read_bytes() == before
    assert not (run / state.LOCK).exists()


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
    before = (run / state.STATE).read_bytes()
    assert main([*argv, "--model", "fixture-model"]) == 1
    assert (run / state.STATE).read_bytes() == before


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
    before = (run / state.STATE).read_bytes()
    with pytest.raises(ValueError):
        attempts.register_dispatch(run, root, "CP-0", item)
    assert (run / state.STATE).read_bytes() == before and not (run / state.LOCK).exists()


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
```

Not verified: physical sends, live Module/A-B/Copilot/fetch/tool/context-budget qualification, Python3.11/Windows/PowerShell, later next/host/resume/runtime/proxy/scorecard/report owners, fresh05 reviews and complete06 closure. No push/merge/publication.
