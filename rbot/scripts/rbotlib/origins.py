"""Exact completion and Approval bytes, bound to existing checked state facts."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from rbotlib import attempts, brief, state
from rbotlib.handoff import parse
from rbotlib.inventory import RunError
from rbotlib.validate import MAX_HANDOFF_BYTES

BRIEF_LIMIT = 1_048_576
KEYS = {
    "schema",
    "basis",
    "artifact",
    "path",
    "sha256",
    "size",
    "bytes",
    "run_id",
    "issuer_id",
    "at",
    "history",
}
BASES = {"completion", "approval", "registered_validation", "restored", "reconstructed"}


def capture(
    raw: bytes, artifact: str, basis: str, history: state.Record | None = None
) -> state.Record:
    front = parse(raw.decode("utf-8")).front_matter
    return dict(
        schema="rbot-artifact-origin/1",
        basis=basis,
        artifact=artifact,
        path="handoffs/CP-0.md" if artifact == "CP-0" else "run-brief.md",
        sha256=hashlib.sha256(raw).hexdigest(),
        size=len(raw),
        bytes=base64.b64encode(raw).decode(),
        run_id=front["run_id"],
        issuer_id=front["issuer_id"],
        at=attempts.stamp(),
        history=history,
    )


def decoded(origin: state.Record, artifact: str) -> bytes:
    limit = MAX_HANDOFF_BYTES if artifact == "CP-0" else BRIEF_LIMIT
    if not isinstance(origin, dict) or set(origin) != KEYS:
        raise RunError("artifact origin: unexpected/missing envelope fields")
    state._fields(
        origin,
        {
            "schema": lambda v: v == "rbot-artifact-origin/1",
            "basis": lambda v: isinstance(v, str) and v in BASES,
            "artifact": lambda v: v == artifact,
            "path": lambda v: v == ("handoffs/CP-0.md" if artifact == "CP-0" else "run-brief.md"),
            "sha256": state._sha,
            "size": lambda v: type(v) is int and 0 < v <= limit,
            "bytes": lambda v: isinstance(v, str) and len(v) <= 4 * ((limit + 2) // 3),
            "run_id": state._text,
            "issuer_id": state._text,
            "at": state._stamp,
        },
        "artifact origin",
    )
    try:
        raw = base64.b64decode(origin["bytes"], validate=True)
        if (
            len(raw) != origin["size"]
            or base64.b64encode(raw).decode() != origin["bytes"]
            or hashlib.sha256(raw).hexdigest() != origin["sha256"]
        ):
            raise RunError("artifact origin: canonical bytes/size/hash differ")
        front = parse(raw.decode("utf-8")).front_matter
    except (ValueError, UnicodeDecodeError) as exc:
        raise RunError(f"artifact origin: unreadable exact bytes ({exc})") from exc
    if any(
        front.get(k) != v
        for k, v in {
            "module_id": artifact,
            "run_id": origin["run_id"],
            "issuer_id": origin["issuer_id"],
        }.items()
    ) or front.get("qa_status") not in ("Pass", "Restricted", "Blocked"):
        raise RunError("artifact origin: Handoff identity/QA differs")
    _reference(origin)
    return raw


def _reference(origin: state.Record) -> None:
    ref = origin["history"]
    if origin["basis"] != "registered_validation":
        if ref is not None:
            raise RunError("artifact origin: capture has no registered history reference")
        return
    if not isinstance(ref, dict) or set(ref) != {"sequence", "sha256"}:
        raise RunError("artifact origin: missing registered history reference")
    state._fields(
        ref,
        {"sequence": lambda v: type(v) is int and v > 0, "sha256": state._sha},
        "artifact origin history",
    )


def cp0_anchor(record: state.Record) -> str:
    from rbotlib.current import original

    return str(
        record.get("cp0_lineage", {}).get("sha256", original(record["steps"]["CP-0"])["sha256"])
    )


def brief_digest(record: state.Record) -> str:
    observations = record.get("brief_edits", [])
    return str(observations[-1]["sha256"] if observations else record["run_brief_sha256"])


def validate(record: state.Record) -> None:
    from rbotlib.current import checked

    for module, step in record["steps"].items():
        checked(step, module)
        _current_identity(record, module, step)
    _completion(record)
    approved = record.get("approved_origins")
    if "approved_origins" in record:
        if (
            record["approval"] is None
            or not isinstance(approved, dict)
            or set(approved) != {"CP-0", "RUN_BRIEF"}
        ):
            raise RunError("approved origin: requires exact CP-0 and RUN_BRIEF pair")
        cp0 = approved["CP-0"]
        final = approved["RUN_BRIEF"]
        _selected_cp0(record, cp0)
        parsed = parse(decoded(final, "RUN_BRIEF").decode())
        if cp0["basis"] not in ("approval", "restored", "registered_validation") or final[
            "basis"
        ] not in ("approval", "restored", "reconstructed"):
            raise RunError("approved origin: observation basis differs")
        lineage = record["cp0_lineage"]
        if (
            cp0["sha256"] != lineage["sha256"]
            or cp0["run_id"] != lineage["pending_run_id"]
            or cp0["issuer_id"] != lineage["issuer_id"]
            or final["sha256"] != record["run_brief_sha256"]
            or final["run_id"] != record["run_id"]
            or final["issuer_id"] != record["issuer_id"]
        ):
            raise RunError("approved origin: frozen identity/digest binding differs")
        from rbotlib.host_validate import brief_shape

        brief_shape(parsed, record)
        row = parsed.tables["brief.approval"].rows
        approval = record["approval"]
        if len(row) != 1 or row[0][:2] != [approval["approved_at"], approval["analyst"]]:
            raise RunError("approved origin: Approval facts differ")
    _brief_edits(record)


def _completion(record: state.Record) -> None:
    from rbotlib.current import checked

    completion = record.get("completion_origin", {})
    if "completion_origin" in record:
        raw = decoded(completion, "CP-0")
        if completion["basis"] not in ("completion", "restored", "registered_validation"):
            raise RunError("completion origin: observation basis differs")
        base = checked(record["steps"]["CP-0"], "CP-0")
        front = parse(raw.decode()).front_matter
        pending = record.get("cp0_lineage", {}).get("pending_run_id", record["run_id"])
        if (
            completion["sha256"] != base.get("sha256")
            or completion["run_id"] != pending
            or front["qa_status"] != base.get("qa_status")
        ):
            raise RunError("completion origin: original completion binding differs")


def _selected_cp0(record: state.Record, origin: state.Record) -> None:
    from rbotlib.current import original

    raw = decoded(origin, "CP-0")
    step = record["steps"]["CP-0"]
    base = original(step)
    if origin["sha256"] == base.get("sha256"):
        if parse(raw.decode()).front_matter["qa_status"] != base.get("qa_status"):
            raise RunError("approved origin: completion QA differs")
        return
    candidates = [
        e
        for e in step.get("current_edits", [])
        if e["kind"] == "artifact"
        and e["result"]["exit"] in (0, 3)
        and e["result"]["sha256"] == origin["sha256"]
    ]
    if not candidates or base64.b64decode(candidates[-1]["snapshot"], validate=True) != raw:
        raise RunError("approved origin: selected CP-0 lacks checked current lineage")


def _current_identity(record: state.Record, module: str, step: state.Record) -> None:
    pending = record.get("cp0_lineage", {}).get("pending_run_id", record["run_id"])
    issuer = (
        record.get("cp0_lineage", {}).get("issuer_id") if module == "CP-0" else record["issuer_id"]
    )
    issuer = issuer or record["issuer_id"]
    for entry in step.get("current_edits", []):
        if entry["kind"] == "artifact" and entry["result"]["exit"] in (0, 3):
            front = parse(base64.b64decode(entry["snapshot"], validate=True).decode()).front_matter
            if front.get("run_id") != (pending if module == "CP-0" else record["run_id"]) or (
                issuer is not None and front.get("issuer_id") != issuer
            ):
                raise RunError("current artifact origin: qualified run/issuer differs")
        if entry["kind"] == "dependency":
            _current_cause(record, module, entry)


def _current_cause(record: state.Record, module: str, entry: state.Record) -> None:
    producer = record["steps"].get(entry["producer"], {})
    from rbotlib.current import dependency_reason

    message = dependency_reason(record, entry["producer"]) if producer else "invalid"
    if (
        entry["producer"] == module
        or producer.get("status") not in ("failed", "skipped")
        or entry["result"]["findings"] != [dict(code="current_qualification", message=message)]
    ):
        raise RunError("current artifact origin: invalid producer/cause")


def _brief_edits(record: state.Record) -> None:
    edits = record.get("brief_edits", [])
    if not isinstance(edits, list) or len(edits) > 64:
        raise RunError("brief origin: bounded current observations required")
    previous = record["run_brief_sha256"]
    for entry in edits:
        if not isinstance(entry, dict) or set(entry) != {"previous", "sha256", "at"}:
            raise RunError("brief origin: malformed current observation")
        state._fields(
            entry,
            {"previous": state._sha, "sha256": state._sha, "at": state._stamp},
            "brief origin",
        )
        if entry["previous"] != previous:
            raise RunError("brief origin: current predecessor differs")
        previous = entry["sha256"]
    if edits and "approved_origins" not in record:
        raise RunError("brief origin: current observation lacks frozen Approval bytes")


def _history(run: Path, record: state.Record, anchor: str) -> state.Record | None:
    events = attempts.read_history(run, "CP-0", record["steps"]["CP-0"])
    for event in events:
        if event["event"] == "validation" and event["result"]["sha256"] == anchor:
            raw = base64.b64decode(event["handoff_base64"], validate=True)
            ref = dict(
                sequence=event["sequence"],
                sha256=record["steps"]["CP-0"]["accept_history"][event["sequence"] - 1],
            )
            return capture(raw, "CP-0", "registered_validation", ref)
    return None


def checked_history(run: Path, record: state.Record) -> None:
    for origin in [record.get("completion_origin"), *record.get("approved_origins", {}).values()]:
        if origin is None or origin["basis"] != "registered_validation":
            continue
        events = attempts.read_history(run, "CP-0", record["steps"]["CP-0"])
        ref = origin["history"]
        event = next((e for e in events if e["sequence"] == ref["sequence"]), None)
        if (
            event is None
            or event["event"] != "validation"
            or record["steps"]["CP-0"]["accept_history"][ref["sequence"] - 1] != ref["sha256"]
            or event["result"]["sha256"] != origin["sha256"]
        ):
            raise RunError("artifact origin: registered validation binding differs")


def resolve(run: Path, root: Path, record: state.Record) -> None:
    """Resolve both exact anchors before publishing any current projection."""
    from rbotlib import dispatch
    from rbotlib.rules import load_rules

    validate(record)
    checked_history(run, record)
    if record["approval"] is None or "approved_origins" in record:
        return
    anchor = cp0_anchor(record)
    cp0 = _history(run, record, anchor)
    if cp0 is None:
        candidate = dispatch._file(run, "handoffs/CP-0.md").read_bytes()
        if hashlib.sha256(candidate).hexdigest() != anchor:
            raise RunError(
                "frozen approved CP0 bytes unavailable; "
                "cannot establish unchanged approved decisions"
            )
        cp0 = capture(candidate, "CP-0", "restored")
    candidate = dispatch._file(run, "run-brief.md").read_bytes()
    basis = "restored"
    if hashlib.sha256(candidate).hexdigest() != record["run_brief_sha256"]:
        carried = parse(candidate.decode())
        rebuilt = brief.build(run, dispatch._file(run, "handoffs/CP-0.md"), [], load_rules(root))
        rebuilt.cp0_sha256, rebuilt.run_id = anchor, record["run_id"]
        rebuilt.approval = carried.tables["brief.approval"].rows
        rebuilt.questions = carried.tables["brief.research_questions"].rows
        rebuilt.prior = carried.tables["brief.prior_case"].rows
        candidate, basis = brief.render(rebuilt).encode(), "reconstructed"
    if hashlib.sha256(candidate).hexdigest() != record["run_brief_sha256"]:
        raise RunError("RUN_BRIEF: approved origin cannot be reconstructed; decisions preserved")
    record["approved_origins"] = {"CP-0": cp0, "RUN_BRIEF": capture(candidate, "RUN_BRIEF", basis)}
    validate(record)


def current_semantics(run: Path, record: state.Record) -> None:
    from rbotlib import dispatch

    approved = record.get("approved_origins")
    if approved is None:
        raise RunError("approved origin: exact bytes require the current qualification owner")
    for artifact, origin in approved.items():
        raw = dispatch._file(run, origin["path"]).read_bytes()
        limit = MAX_HANDOFF_BYTES if artifact == "CP-0" else BRIEF_LIMIT
        if len(raw) > limit:
            raise RunError("approved origin: current artifact exceeds its supported bound")
        current = parse(raw.decode())
        frozen = parse(decoded(origin, artifact).decode())
        if current.front_matter != frozen.front_matter or current.tables != frozen.tables:
            raise RunError(
                f"{artifact}: approved decisions/classifications changed; new run required"
            )
