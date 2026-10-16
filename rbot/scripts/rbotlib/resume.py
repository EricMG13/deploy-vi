"""Prospective Module publication recovery under the existing process-held owner.

An exact checked intent precedes evidence publication. A naked orphan grants no
right to finish an operation; recovery preserves original observation times and
never claims that an interrupted command returned its validation exit.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path

from rbotlib import attempts, dispatch, host_evidence, state
from rbotlib.fsio import write_atomic
from rbotlib.inventory import RunError, output_path

KEY = "module_publication"


def baseline(record: state.Record) -> str:
    return host_evidence.digest(
        {k: v for k, v in record.items() if k not in (KEY, "updated_at", "command_receipts")}
    )


def fingerprint(run: Path, root: Path, record: state.Record, event: state.Record) -> str:
    from rbotlib.current import _proof

    dispatch._prepared(run, record)  # verifies actual source bytes, not only index digests
    names = ["run-brief.md"] if record["approval"] is not None else []
    for folder in ("handoffs", "fetched", "dispatch"):
        names += [str(p.relative_to(run)) for p in (run / folder).rglob("*") if p.is_file()]
    failed_own = (
        f"handoffs/{event['module']}.md"
        if event["event"] == "validation" and event["result"]["exit"] == 1
        else None
    )
    artifacts = {n: dispatch._sha(dispatch._file(run, n)) for n in sorted(names) if n != failed_own}
    if failed_own is not None:
        dispatch._target(run, failed_own)  # metadata safety still precedes publication
        artifacts[failed_own] = event["result"]["sha256"]
    return host_evidence.digest(
        {
            "inputs": _proof(run, root, record),
            "artifacts": artifacts,
            "modules": {
                str(p.relative_to(root)): dispatch._sha(
                    dispatch._file(root, str(p.relative_to(root)))
                )
                for p in sorted((root / "modules").glob("*/MODULE.md"))
            },
        }
    )


def checked(record: state.Record) -> state.Record | None:
    if KEY not in record:
        return None
    intent = record[KEY]
    if (
        not isinstance(intent, dict)
        or set(intent) != {"schema", "module", "baseline", "proof", "event", "after", "binding"}
        or intent["schema"] != "rbot-module-publication/1"
        or not isinstance(intent["module"], str)
        or not all(state._sha(intent[k]) for k in ("baseline", "proof", "binding"))
        or not isinstance(intent["event"], dict)
        or not isinstance(intent["after"], dict)
        or intent["binding"]
        != host_evidence.digest({k: v for k, v in intent.items() if k != "binding"})
        or intent["baseline"] != baseline(record)
    ):
        raise RunError("Module recovery: malformed or changed prospective intent/state")
    module = intent["module"]
    step = attempts.declared(record, module)
    if step["status"] not in ("pending", "running") or step.get("current_edits"):
        raise RunError("Module recovery: terminal/current-edited step cannot publish")
    event = intent["event"]
    attempts._event(event, module, len(step.get("accept_history", [])) + 1)
    if event["run_id"] != record["run_id"]:
        raise RunError("Module recovery: prospective run identity differs")
    state._step(module, intent["after"])
    return intent


def _projection(
    step: state.Record, events: list[state.Record], event: state.Record
) -> state.Record:
    from rbotlib.accept import _completion

    after = copy.deepcopy(step)
    after.setdefault("accept_history", []).append(
        hashlib.sha256(attempts.encode(event).encode()).hexdigest()
    )
    if event["event"] == "dispatch_report":
        after.update(status="running", attempts=event["slot"])
        after.setdefault("started_at", event["observed_at"])
        after.setdefault("started_at_basis", "controller_dispatch_report")
    else:
        _completion(after, event["result"], event)
        if event["result"]["exit"] in (0, 3):
            after["qa_status"] = event["qa_status"]
        model = events[event["dispatch_sequence"] - 1]["model"]
        if model is not None:
            after["model"] = model
        else:
            after.pop("model", None)
    attempts._ordered([*events, event], after)
    return after


def _prefix(run: Path, module: str, step: state.Record, event: state.Record) -> list[state.Record]:
    names = {f"{n:06d}.json" for n in range(1, len(step.get("accept_history", [])) + 1)}
    folder = output_path(run, f"validate/history/{module}")
    found = {p.name for p in folder.iterdir()} if folder.exists() else set()
    pending = f"{event['sequence']:06d}.json"
    if found not in (names, names | {pending}):
        raise RunError("Module recovery: extra/missing immutable history")
    events = []
    for n, digest in enumerate(step.get("accept_history", []), 1):
        raw = dispatch._file(run, f"validate/history/{module}/{n:06d}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise RunError("Module recovery: registered immutable evidence changed")
        value = json.loads(raw, object_pairs_hook=state._pairs)
        attempts._event(value, module, n)
        events.append(value)
    attempts._ordered(events, step)
    return events


def _evidence(run: Path, module: str, events: list[state.Record], event: state.Record) -> None:
    target = attempts.event_path(run, module, event["sequence"])
    if (
        target.exists()
        and dispatch._file(run, str(target.relative_to(run))).read_bytes()
        != attempts.encode(event).encode()
    ):
        raise RunError("Module recovery: prospective immutable event differs")
    latest = dispatch._target(run, f"validate/{module}.json")
    validations = [e["result"] for e in events if e["event"] == "validation"]
    allowed = validations[-1:] + ([event["result"]] if event["event"] == "validation" else [])
    if latest.exists():
        value = json.loads(
            dispatch._file(run, str(latest.relative_to(run))).read_text(),
            object_pairs_hook=state._pairs,
        )
        if value not in allowed:
            raise RunError("Module recovery: conflicting latest validation")
        if not target.exists() and event["event"] == "validation" and value == event["result"]:
            raise RunError("Module recovery: latest validation without its immutable event")
    elif validations:
        raise RunError("Module recovery: registered latest validation missing")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(target, attempts.encode(event))
    if event["event"] == "validation":
        write_atomic(latest, attempts.encode(event["result"]))


def _readback(run: Path, root: Path, record: state.Record, intent: state.Record) -> None:
    module, event = intent["module"], intent["event"]
    current = state.read(run)
    if checked(current) != intent:
        raise RunError("Module recovery: staged prospective state/intent changed")
    _prefix(run, module, current["steps"][module], event)
    published = dispatch._file(
        run, str(attempts.event_path(run, module, event["sequence"]).relative_to(run))
    )
    if (
        published.read_bytes() != attempts.encode(event).encode()
        or fingerprint(run, root, record, event) != intent["proof"]
    ):
        raise RunError("Module recovery: publication readback/context changed")
    if event["event"] == "validation":
        attempts._latest(run, module, [event])


def recover(owner: state._Locked, root: Path) -> None:
    record = state.read(owner.run)
    from rbotlib.command_receipts import verify

    verify(owner.run, record)
    intent = checked(record)
    if intent is None:
        return
    owner.owner.check()
    module, event = intent["module"], intent["event"]
    step = attempts.target(record, module, root)
    events = _prefix(owner.run, module, step, event)
    attempts._history_identity(record, module, [*events, event])
    after = _projection(step, events, event)
    if after != intent["after"] or fingerprint(owner.run, root, record, event) != intent["proof"]:
        raise RunError("Module recovery: prospective projection/current context or inputs changed")
    owner.owner.check()
    _evidence(owner.run, module, events, event)
    _readback(owner.run, root, record, intent)
    record["steps"][module] = after
    record.pop(KEY)
    staged = owner.stage(record)
    _readback(owner.run, root, state.read(owner.run), intent)
    owner.owner.check()
    owner.commit(staged)
    attempts.read_history(owner.run, module, after)


def publish(
    run: Path, root: Path, module: str, change: Callable[[state.Record], state.Record]
) -> state.Record:
    owner = state._Locked(run)
    try:
        recover(owner, root)
        record = state.read(run)
        before = copy.deepcopy(record)
        event = change(record)
        intent = dict(
            schema="rbot-module-publication/1",
            module=module,
            baseline=baseline(before),
            proof=fingerprint(run, root, before, event),
            event=event,
            after=record["steps"][module],
        )
        intent["binding"] = host_evidence.digest(intent)
        before[KEY] = intent
        owner.commit(owner.stage(before))
        recover(owner, root)
        return event
    finally:
        warnings = owner.close()
        if warnings:
            raise RunError("; ".join(warnings))
