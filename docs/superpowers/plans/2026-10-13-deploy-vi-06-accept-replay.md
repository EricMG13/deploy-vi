# Plan06.5 executed accept source/test replay

Approved predecessor: `6fa314d6b8edb786aa1dbeba65f5a350a811930f`, tree `6733ba323f00b8b69621ddf965a483842e2a0e45`. This document records repaired locally executed05 awaiting NEW ordinary/sensitive reviews; the rejected53d12fb/tree69a21fff history remains retained. Repair1 proof/evidence is task-05-fix-proof.json; old task-05-proof.json describes only rejected-tree history. Exact binary/full-index per-boundary patches/tree/lock/cap proof are in main staging task-05-proof.json. These complete AST-parsable blocks match current source bytes; the patches replay integration without inferred manual edits.

Consume the existing checked state/Approval lock and Task04 pure qualification, actual selected-root contracts/rules/catalog/source context, and reported dispatch events. Preparation never sends. Receipts are trusted caller reports, not signed/network proof. attempts counts validation slots1/2; distinct reported interruption resends remain individually attributable within a slot. Latest validation retains the prescribed four fields; immutable relative history keeps exact messages and raw-byte Handoff snapshots plus code/QA/receipt links. Strict base64 length/canonical decode/hash checks are local encoding checks, not authenticity. Missing/unreadable first-observation bytes have null hash/body/length; verification I/O1 retains actually observed first bytes and prior findings with QA None, never a verified current hash; unknown worker/model evidence stays unknown. Approved CP0 uses only registered pending lineage. Orphan/latest mismatch refuses for owner09. Python3.11 primary base64 docs were read after selection before commit;3.11/Windows remain unexercised.

## `rbot/scripts/rbotlib/accept.py`

<!-- replay-path: rbot/scripts/rbotlib/accept.py -->
```python
"""Independently validate the own Handoff snapshot, never a claimed DONE code.

Receipt evidence is caller-reported; validation/finished timestamps are controller
observations. Terminal edits and interrupted evidence publication require owner09.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
from dataclasses import asdict
from pathlib import Path

from rbotlib import attempts, bootstrap, dispatch, state
from rbotlib.contract import load_contract
from rbotlib.handoff import HandoffError, parse
from rbotlib.inventory import RunError
from rbotlib.rules import Rules, load_rules
from rbotlib.validate import Finding, check


def _identity(
    run: Path, module: str, text: str, rules: Rules, record: state.Record
) -> list[Finding]:
    try:
        front = parse(text).front_matter
    except HandoffError:
        return []
    lineage = record.get("cp0_lineage") if module == "CP-0" else None
    expected = lineage["pending_run_id"] if lineage else record["run_id"]
    if front.get("run_id") and front["run_id"] != expected:
        return [Finding("identity", "Handoff run_id differs from this qualified run")]
    issuer = lineage["issuer_id"] if lineage else record["issuer_id"]
    if issuer is not None and front.get("issuer_id") and front["issuer_id"] != issuer:
        return [Finding("identity", "Handoff issuer_id differs from this qualified issuer")]
    return []


def _citation_guard(text: str) -> None:
    try:
        dispatch._pack_citations(text)
    except HandoffError:
        return  # the independent checker returns malformed2 for unreadable structure


def _observe(
    run: Path, root: Path, module: str, record: state.Record
) -> tuple[state.Record, str | None, bytes | None]:
    path = dispatch._target(run, f"handoffs/{module}.md")
    raw = None
    qa = None
    code = 1
    findings: list[Finding] = []
    try:
        raw = dispatch._file(run, f"handoffs/{module}.md").read_bytes()
        text = raw.decode("utf-8")
        rules = load_rules(root)
        contract = load_contract(dispatch._file(root, f"modules/{module}/contract.json"), rules)
        _citation_guard(text)
        code, findings = check(text, contract, rules, run)
        identity = _identity(run, module, text, rules, record)
        if module == "CP-0" and code in (0, 3) and not identity:
            try:
                bootstrap._identity(run, text, rules, record)
            except RunError as exc:
                identity = [Finding("identity", str(exc))]
        if identity:
            code, findings = 4, [*findings, *identity]
        if code in (0, 3):
            qa = parse(text).front_matter["qa_status"]
    except (OSError, UnicodeDecodeError) as exc:
        code, findings = 1, [Finding("execution_error", f"{path}: {exc}")]
    except RunError as exc:
        code, findings = 1, [Finding("execution_error", str(exc))]
    return (
        {
            "exit": code,
            "findings": [asdict(f) for f in findings],
            "sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None,
            "at": attempts.stamp(),
        },
        qa,
        raw,
    )


def _verified_observation(
    run: Path, root: Path, module: str, record: state.Record
) -> tuple[state.Record, str | None, bytes | None]:
    result, qa, raw = _observe(run, root, module, record)
    # No bytes were validated: retain the attempted execution1 without another read.
    if raw is None:
        return result, qa, raw
    path = dispatch._target(run, f"handoffs/{module}.md")
    try:
        current = path.read_bytes()
    except OSError as exc:
        # Retain the actual first snapshot, but failed verification cannot grant success.
        result.update(
            exit=1,
            findings=[*result["findings"], asdict(Finding("execution_error", f"{path}: {exc}"))],
        )
        return result, None, raw
    if current != raw:
        raise RunError(f"{module}: Handoff changed during independent validation")
    return result, qa, raw


def _completion(step: state.Record, result: state.Record, event: state.Record) -> None:
    code = result["exit"]
    terminal = code != 2 or event["slot"] == 2
    status = (
        "accepted" if code == 0 else "blocked" if code == 3 else "failed" if terminal else "running"
    )
    reason = "; ".join(f["message"] for f in result["findings"])
    step.update(status=status, validate_exit=code, validated_at=result["at"], reason=reason)
    if result["sha256"] is not None:
        step.update(sha256=result["sha256"], handoff=f"handoffs/{event['module']}.md")
    else:
        step.pop("sha256", None)
        step.pop("handoff", None)
    if terminal:
        step["finished_at"] = result["at"]
        step["finished_at_basis"] = "controller_validation"


def _accept_event(run: Path, root: Path, module: str, record: state.Record) -> state.Record:
    step = attempts.target(record, module)
    events = attempts.read_history(run, module, step)
    if not events:
        raise RunError(f"{module}: acceptance requires reported dispatch evidence")
    if step["status"] == "skipped":
        raise RunError(f"{module}: skipped step cannot accept")
    # Shared source/context/dependency qualification guards the checker's transitive reads.
    dispatch.qualified_message(run, root, module, record)
    result, qa, raw = _verified_observation(run, root, module, record)
    latest = events[-1]
    if latest["event"] == "validation":
        if all(result[k] == latest["result"][k] for k in ("exit", "findings", "sha256")):
            raise attempts.Duplicate(latest)
        raise RunError(
            f"{module}: validated bytes changed; a new dispatch or recovery owner is required"
        )
    if step["status"] != "running":
        raise RunError(f"{module}: terminal state cannot be resurrected")
    event = dict(
        event="validation",
        slot=latest["slot"],
        run_id=record["run_id"],
        dispatch_sequence=latest["sequence"],
        result=result,
        qa_status=qa,
        handoff_base64=base64.b64encode(raw).decode() if raw is not None else None,
        handoff_bytes=len(raw) if raw is not None else None,
    )
    attempts.append_event(run, module, step, events, event)
    _completion(step, result, event)
    if result["exit"] in (0, 3):
        # QA and stored digest describe the independently observed same snapshot.
        step["qa_status"] = qa
    if latest["model"] is not None:
        step["model"] = latest["model"]
    else:
        step.pop("model", None)
    attempts._ordered([*events, event], step)
    return event


def accept(run: Path, root: Path, module: str) -> state.Record:
    """Return latest prescribed result, publishing immutable event plus checked state."""
    run, root = state.run_path(run), dispatch._root(root)
    state.read(run)
    dispatch._target(run, "log/rbot.log")
    event: state.Record = {}

    def change(record: state.Record) -> None:
        event.update(_accept_event(run, root, module, record))

    try:
        state.update(run, change, lambda: attempts.publish_event(run, module, event))
    except attempts.Duplicate as duplicate:
        result: state.Record = duplicate.event["result"]
        return result
    result = event["result"]
    return result


def run_command(args: argparse.Namespace) -> int:
    try:
        result = accept(Path(args.run_dir), args.root, args.module)
        for finding in result["findings"]:
            print(f"{finding['code']}: {finding['message']}")
        print(f"exit {result['exit']}")
        return int(result["exit"])
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print(f"error: accept: {exc}")
        return 1


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser("accept", help="independently validate dispatched Module bytes")
    parser.add_argument("--run", dest="run_dir", required=True)
    parser.add_argument("--module", required=True)
    parser.set_defaults(run=run_command, log_run_guard=state.log_run_path)
```

## `tests/test_accept.py`

<!-- replay-path: tests/test_accept.py -->
```python
"""Independent acceptance of fixture bytes; no live Module qualification."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from test_bootstrap import approve, pending, ready

from rbotlib import attempts, dispatch, state
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT


def send(
    run: Path, root: Path, module: str = "CP-0", name: str = "fixture-send", retry: bool = False
) -> None:
    findings = f"validate/{module}.json" if retry else None
    text = dispatch.prepare_message(run, root, module, findings)
    receipt = attempts.DispatchReceipt(
        name, "fixture-controller", hashlib.sha256(text.encode()).hexdigest()
    )
    attempts.register_dispatch(run, root, module, receipt)


def accept(run: Path, root: Path = RBOT_ROOT, module: str = "CP-0") -> int:
    return main(["--root", str(root), "accept", "--run", str(run), "--module", module])


@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize(
    "qa,code,status",
    [("Pass", 0, "accepted"), ("Restricted", 0, "accepted"), ("Blocked", 3, "blocked")],
)
def test_accept_exact_current_bytes_and_cp0_approval_lineage(
    tmp_path: Path, selected: bool, qa: str, code: int, status: str
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "selected ' root") if selected else RBOT_ROOT
    run = pending(tmp_path, root)
    source = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    own = run / "handoffs/CP-0.md"
    own.write_text(own.read_text().replace("qa_status: Restricted", f"qa_status: {qa}"))
    send(run, root)
    own.write_text(own.read_text() + "\nDONE 4\n")  # worker claim is never acceptance authority
    raw = own.read_bytes()
    assert accept(run, root) == code
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == status and step["qa_status"] == qa and step["attempts"] == 1
    assert step["sha256"] == hashlib.sha256(raw).hexdigest()
    assert "model" not in step and "finished_at" in step
    latest = json.loads((run / "validate/CP-0.json").read_text())
    assert set(latest) == {"exit", "findings", "sha256", "at"} and latest["exit"] == code
    history = {p.name: p.read_bytes() for p in (run / "validate/history/CP-0").iterdir()}
    before = (run / state.STATE).read_bytes()
    assert accept(run, root) == code and (run / state.STATE).read_bytes() == before
    ready(run, root)
    target = approve(run, root)
    assert state.read(target)["steps"]["CP-0"] == step
    assert {p.name: p.read_bytes() for p in (target / "validate/history/CP-0").iterdir()} == history
    assert accept(target, root) == code
    assert (target / "handoffs/CP-0.md").read_bytes() == raw
    assert {p.name: p.read_bytes() for p in target.parent.parent.iterdir() if p.is_file()} == source


def test_no_reported_dispatch_or_seeded_attempts_cannot_accept(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    before = (run / state.STATE).read_bytes()
    assert accept(run) == 1 and (run / state.STATE).read_bytes() == before
    state.update(run, lambda record: record["steps"]["CP-0"].update(status="running", attempts=1))
    before = (run / state.STATE).read_bytes()
    assert accept(run) == 1 and (run / state.STATE).read_bytes() == before
    assert not (run / "validate").exists()


def test_malformed_retry_survives_resends_and_duplicate_accept(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    own.write_text("DONE 0")
    assert accept(run) == 2
    first = (run / "validate/CP-0.json").read_bytes()
    before = (run / state.STATE).read_bytes()
    assert accept(run) == 2 and (run / state.STATE).read_bytes() == before
    assert (run / "validate/CP-0.json").read_bytes() == first
    send(run, RBOT_ROOT, name="fixture-retry", retry=True)
    send(run, RBOT_ROOT, name="fixture-retry-interrupted", retry=True)
    assert state.read(run)["steps"]["CP-0"]["attempts"] == 2
    assert accept(run) == 2
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "failed" and step["validate_exit"] == 2
    events = attempts.read_history(run, "CP-0", step)
    assert [e["slot"] for e in events] == [1, 1, 2, 2, 2]
    assert events[1]["result"] == json.loads(first)
    assert accept(run) == 2
    with pytest.raises(ValueError, match="pending/running"):
        send(run, RBOT_ROOT, name="third")


@pytest.mark.parametrize(
    "field,value", [("module_id", "CP-1"), ("run_id", "wrong-run"), ("issuer_id", "WRONG")]
)
def test_wrong_identity_fails_immediately_even_with_claimed_done(
    tmp_path: Path, field: str, value: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    text = own.read_text()
    old = next(line for line in text.splitlines() if line.startswith(field + ":"))
    own.write_text(text.replace(old, f"{field}: {value}") + "\nDONE 0\n")
    assert accept(run) == 4
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "failed" and step["attempts"] == 1
    assert step["sha256"] == hashlib.sha256(own.read_bytes()).hexdigest()


@pytest.mark.parametrize("missing", [True, False])
def test_io_one_is_terminal_and_missing_has_no_invented_hash(tmp_path: Path, missing: bool) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    if missing:
        own.unlink()
    else:
        own.write_bytes(b"\xff")
    assert accept(run) == 1
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "failed" and "CP-0.md" in step["reason"]
    result = json.loads((run / "validate/CP-0.json").read_text())
    assert result["exit"] == 1
    assert result["sha256"] == (None if missing else hashlib.sha256(b"\xff").hexdigest())
    assert not (run / state.LOCK).exists()


def test_terminal_edit_refuses_without_erasing_validation(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    own = run / "handoffs/CP-0.md"
    own.write_bytes(own.read_bytes() + b"\nchanged")
    before = (run / state.STATE).read_bytes(), (run / "validate/CP-0.json").read_bytes()
    assert accept(run) == 1
    assert before == ((run / state.STATE).read_bytes(), (run / "validate/CP-0.json").read_bytes())


@pytest.mark.parametrize("target", ["MODEL", "CP-DR", "CP-8", "CP-1", "../CP-0"])
def test_unsupported_or_unplanned_accept_is_preflight_refusal(tmp_path: Path, target: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    before = (run / state.STATE).read_bytes()
    assert accept(run, module=target) == 1
    assert (run / state.STATE).read_bytes() == before and not (run / "validate").exists()
```

## `tests/test_accept_corpus.py`

<!-- replay-path: tests/test_accept_corpus.py -->
```python
"""Required-root copies and hand-written fixture outputs, never live model evidence."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

import pytest
from test_accept import accept, send
from test_bootstrap import approve, ready
from test_modules import _blocked

from cp0_fixture import cp0_handoff, registry_classification
from rbotlib import state
from rbotlib.cli import main
from rbotlib.contract import load_contract
from rbotlib.corpus import load_registry
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import check


@pytest.mark.corpus
@pytest.mark.parametrize("qa", ["Restricted", "Blocked"])
def test_corpus_production_approval_and_module_accept(
    corpus_pack: Callable[[str], Path], tmp_path: Path, qa: str
) -> None:
    import shutil

    pack = shutil.copytree(corpus_pack("czr-2026q2-primary"), tmp_path / "working pack")
    files = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.iterdir() if p.is_file()
    }
    assert main(["new-run", "--pack", str(pack)]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    record = load_registry().pack("czr-2026q2-primary")
    (run / "handoffs").mkdir()
    (run / "handoffs/CP-0.md").write_text(
        cp0_handoff(
            run,
            ("Caesars Entertainment, Inc.", "CZR"),
            "2026-10-02",
            registry_classification(record),
            primary=False,
        )
    )
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    send(run, RBOT_ROOT, "CP-1")
    text = (
        (Path(__file__).parent / "fixtures/handoffs/CP-1.md")
        .read_text()
        .replace("run_id: 20261011-czr-full-credit-assessment", f"run_id: {run.name}")
    )
    rules = load_rules(RBOT_ROOT)
    contract = load_contract(RBOT_ROOT / "modules/CP-1/contract.json", rules)
    if qa == "Blocked":
        text = _blocked(text, contract)
    expected = 3 if qa == "Blocked" else 0
    assert check(text, contract, rules, run) == (expected, [])
    (run / "handoffs/CP-1.md").write_text(text)
    assert accept(run, module="CP-1") == expected
    assert state.read(run)["steps"]["CP-1"]["qa_status"] == qa
    assert {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.iterdir() if p.is_file()
    } == files
```

Not verified: physical sends, live Module/A-B/Copilot/fetch/tool/context-budget qualification, Python3.11/Windows/PowerShell, later next/host/resume/runtime/proxy/scorecard/report owners, fresh05 reviews and complete06 closure. No push/merge/publication.
