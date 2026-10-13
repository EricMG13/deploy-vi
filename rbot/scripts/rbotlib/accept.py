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
