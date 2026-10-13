"""Bounded current-artifact observations; original execution evidence stays immutable.

Revisions live in the same atomic checked state publication. They do not open a
validation slot, send a worker, rebuild a terminal host or attribute a worker exit.
"""

from __future__ import annotations

import base64
import copy
import hashlib
from pathlib import Path

from rbotlib import accept, attempts, brief, dispatch, host_evidence, origins, state
from rbotlib.handoff import parse
from rbotlib.inventory import RunError
from rbotlib.rules import load_rules


def original(step: state.Record) -> state.Record:
    base = step.get("current_origin", step)
    if not isinstance(base, dict) or "current_origin" in base or "current_edits" in base:
        raise RunError("current artifact: malformed original projection")
    if base is not step and not step.get("current_edits"):
        raise RunError("current artifact: missing edit lineage")
    return dict(base)


def result(step: state.Record) -> state.Record:
    edits = step.get("current_edits", [])
    return edits[-1]["result"] if edits else {}


def _apply(step: state.Record, entry: state.Record) -> None:
    kind, observed = entry["kind"], entry["result"]
    reason = "; ".join(f["message"] for f in observed["findings"])
    if kind == "artifact":
        code = observed["exit"]
        step.update(status="accepted" if code == 0 else "blocked" if code == 3 else "failed")
        step.update(reason=reason, note="edited")
        if observed["sha256"] is None:
            step.pop("sha256", None)
            step.pop("handoff", None)
        else:
            step["sha256"] = observed["sha256"]
        if code in (0, 3):
            step["qa_status"] = entry["qa_status"]
    else:
        step.update(
            status="skipped"
            if kind == "dependency" and step["status"] in ("pending", "running")
            else "failed",
            reason=reason,
        )


def checked(step: state.Record, module: str) -> state.Record:
    """Derive only current fields from exact original plus bounded attributed observations."""
    base = original(step)
    edits = step.get("current_edits", [])
    if not isinstance(edits, list) or len(edits) > 64:
        raise RunError("current artifact: edit lineage must be a list")
    projected = dict(base)
    for entry in edits:
        _entry(entry, projected, module)
        _apply(projected, entry)
    if edits:
        projected.update(current_origin=base, current_edits=edits)
    if projected != step:
        raise RunError("current artifact: current state differs from bounded edit lineage")
    return base


def _entry(entry: state.Record, previous: state.Record, module: str) -> None:
    if (
        not isinstance(entry, dict)
        or set(entry)
        != {"kind", "previous", "proof", "result", "qa_status", "snapshot", "producer"}
        or entry["kind"] not in ("artifact", "dependency", "host")
        or entry["previous"] != host_evidence.digest(previous)
        or not state._sha(entry["proof"])
    ):
        raise RunError("current artifact: malformed or unbound edit observation")
    attempts._result(entry["result"])
    if entry["kind"] == "artifact":
        _artifact_entry(entry, previous, module)
    else:
        _nonartifact_entry(entry, previous)


def _artifact_entry(entry: state.Record, previous: state.Record, module: str) -> None:
    if previous["kind"] != "module" or previous["status"] not in ("accepted", "blocked"):
        raise RunError("current artifact: only committed Module bytes can be revalidated")
    snapshot = entry["snapshot"]
    event = dict(
        result=entry["result"],
        module=module,
        qa_status=entry["qa_status"],
        handoff_base64=snapshot,
        handoff_bytes=None,
    )
    if snapshot is not None:
        if not isinstance(snapshot, str) or len(snapshot) > 1_398_104:
            raise RunError("current artifact: bounded canonical snapshot required")
        try:
            raw = base64.b64decode(snapshot, validate=True)
        except ValueError as exc:
            raise RunError("current artifact: malformed snapshot") from exc
        event["handoff_bytes"] = len(raw)
        event["run_id"] = (
            parse(raw.decode()).front_matter.get("run_id")
            if entry["result"]["exit"] in (0, 3)
            else "invalid"
        )
    attempts._snapshot(event)
    code = entry["result"]["exit"]
    expected = ("Pass", "Restricted") if code == 0 else ("Blocked",) if code == 3 else (None,)
    if entry["qa_status"] not in expected or entry["producer"] is not None:
        raise RunError("current artifact: QA/cause differs from actual validation")


def _nonartifact_entry(entry: state.Record, previous: state.Record) -> None:
    if (
        entry["snapshot"] is not None
        or entry["qa_status"] is not None
        or entry["result"]["exit"] != 1
    ):
        raise RunError("current artifact: invalid dependency/host observation")
    if entry["kind"] == "host" and (
        previous["kind"] != "host"
        or previous["status"] != "accepted"
        or entry["producer"] is not None
    ):
        raise RunError("current artifact: host failure requires accepted host origin")
    if entry["kind"] == "dependency" and not state._text(entry["producer"]):
        raise RunError("current artifact: dependency failure requires a producer")


def _append(
    step: state.Record,
    kind: str,
    proof: str,
    observed: state.Record,
    detail: tuple[str | None, bytes | None, str | None] = (None, None, None),
) -> None:
    qa, raw, producer = detail
    base = original(step)
    entries = step.get("current_edits", [])
    previous = dict(step)
    previous.pop("current_origin", None)
    previous.pop("current_edits", None)
    entry = dict(
        kind=kind,
        previous=host_evidence.digest(previous),
        proof=proof,
        result=observed,
        qa_status=qa,
        snapshot=base64.b64encode(raw).decode() if raw is not None else None,
        producer=producer,
    )
    _apply(step, entry)
    step.update(current_origin=base, current_edits=[*entries, entry])


def _failure(message: str) -> state.Record:
    return dict(
        exit=1,
        sha256=None,
        at=attempts.stamp(),
        findings=[dict(code="current_qualification", message=message)],
    )


def _proof(run: Path, root: Path, record: state.Record) -> str:
    paths = ["inventory.json", "prepared/index.json"]
    paths += [str(p.relative_to(run)) for p in (run / "prepared").rglob("*") if p.is_file()]
    return host_evidence.digest(
        dict(
            context=host_evidence.context(root, record),
            sources={p: dispatch._sha(dispatch._file(run, p)) for p in sorted(paths)},
        )
    )


def _approved_brief(run: Path, root: Path, record: state.Record) -> None:
    raw = dispatch._file(run, "run-brief.md").read_bytes()
    if len(raw) > origins.BRIEF_LIMIT:
        raise RunError("RUN_BRIEF: current artifact exceeds its supported bound")
    digest = hashlib.sha256(raw).hexdigest()
    handoff = parse(raw.decode())
    approved = parse(origins.decoded(record["approved_origins"]["RUN_BRIEF"], "RUN_BRIEF").decode())
    if handoff.front_matter != approved.front_matter or handoff.tables != approved.tables:
        raise RunError("RUN_BRIEF: approved decisions changed; new run required")
    from rbotlib.host_validate import brief_shape

    brief_shape(handoff, record)
    dispatch._pack_citations(raw.decode())
    if digest != origins.brief_digest(record):
        edits = record.get("brief_edits", [])
        record["brief_edits"] = [
            *edits,
            dict(previous=origins.brief_digest(record), sha256=digest, at=attempts.stamp()),
        ]


def _modules(run: Path, root: Path, record: state.Record, proof: str) -> None:
    for module in record["plan"]:
        step = record["steps"][module]
        if step["kind"] != "module" or step["status"] not in ("accepted", "blocked"):
            continue
        try:
            observed, qa, raw = accept._verified_observation(run, root, module, record)
        except (OSError, ValueError) as exc:
            observed, qa, raw = _failure(str(exc)), None, None
        prior = result(step)
        digest = prior.get("sha256", step.get("sha256"))
        if (
            observed["sha256"] == digest
            and observed["exit"] in (0, 3)
            and (not prior or step["current_edits"][-1]["proof"] == proof)
        ):
            continue
        _frozen_cp0(module, record, observed, raw)
        _append(step, "artifact", proof, observed, (qa, raw, None))


def _frozen_cp0(
    module: str, record: state.Record, observed: state.Record, raw: bytes | None
) -> None:
    if module != "CP-0" or record["approval"] is None or observed["exit"] not in (0, 3):
        return
    old = parse(origins.decoded(record["approved_origins"]["CP-0"], "CP-0").decode())
    edited = parse(raw.decode()) if raw is not None else None
    if edited is None or old.front_matter != edited.front_matter or old.tables != edited.tables:
        raise RunError("CP-0: approved decisions/classifications changed; new run required")


def dependency_reason(record: state.Record, producer: str) -> str:
    step = record["steps"][producer]
    reason = f"required input {producer}: {step['status']}"
    return reason + (f" ({step['reason']})" if step.get("reason") else "")


def _dependencies(root: Path, record: state.Record, proof: str) -> None:
    from rbotlib import next as selection

    try:
        required = selection._dependencies(root, record, load_rules(root))
    except (KeyError, TypeError) as exc:
        raise RunError(f"selected catalog/contracts are malformed: {exc}") from exc
    for module in record["plan"]:
        step = record["steps"][module]
        producer = next(
            (p for p in required[module] if record["steps"][p]["status"] in ("failed", "skipped")),
            None,
        )
        if producer is not None and step["status"] in ("pending", "running", "accepted", "blocked"):
            message = dependency_reason(record, producer)
            _append(step, "dependency", proof, _failure(message), (None, None, producer))


def _hosts(run: Path, root: Path, record: state.Record, proof: str) -> None:
    from rbotlib import fit_host
    from rbotlib.model import qualification

    for module, qualify in (("MODEL", qualification.qualify), ("FIT", fit_host.qualify)):
        step = record["steps"].get(module, {})
        if step.get("status") != "accepted":
            continue
        try:
            qualify(run, root, record)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            _append(step, "host", proof, _failure(f"{module}: current qualification failed: {exc}"))


def _cause_contracts(root: Path, record: state.Record) -> None:
    from rbotlib import next as selection

    try:
        required = selection._dependencies(root, record, load_rules(root))
    except (KeyError, TypeError) as exc:
        raise RunError(f"selected catalog/contracts are malformed: {exc}") from exc
    for module, step in record["steps"].items():
        for entry in step.get("current_edits", []):
            if entry["kind"] == "dependency" and entry["producer"] not in required[module]:
                raise RunError("current artifact: producer is not a required contract input")


def _host_origins(run: Path, root: Path, record: state.Record) -> None:
    baseline = dict(record, steps={m: original(s) for m, s in record["steps"].items()})
    for module, origin in (("MODEL", "host-model/1"), ("FIT", "host-fit/1")):
        if baseline["steps"].get(module, {}).get("status") == "accepted":
            if module == "MODEL" and set(baseline["steps"][module].get("outputs", {})) != {
                "model.json",
                "handoffs/MODEL.md",
            }:
                raise RunError(
                    "MODEL: current outputs/hash/QA differ from registered complete output set"
                )
            host_evidence.accepted(baseline, module, origin, run, root)


def _partial_approval(run: Path, record: state.Record) -> None:
    if record["approval"] is None and dispatch._target(run, brief.BRIEF).exists():
        dispatch._file(run, brief.BRIEF)
        if brief.approval(run) is not None:
            raise RunError(
                "partial Approval: approved brief without matching state; preserve and pause"
            )


def _reconcile_owned(owner: state._Locked, root: Path) -> None:
    run = owner.run
    owner.owner.check()
    from rbotlib.resume import recover

    recover(owner, root)
    record = state.read(run)
    before = copy.deepcopy(record)
    for module, step in record["steps"].items():
        checked(step, module)
        if step["kind"] == "module":
            try:
                events = attempts.read_history(run, module, step)
            except RunError as exc:
                raise RunError(f"{module}: {exc}") from exc
            if module != "CP-0" and step["status"] in ("accepted", "blocked") and not events:
                raise RunError(
                    f"{module}: committed Module requires reported dispatch/validation evidence"
                )
    dispatch._prepared(run, record)
    _cause_contracts(root, record)
    _partial_approval(run, record)
    _host_origins(run, root, record)
    origins.resolve(run, root, record)
    if record["approval"] is not None:
        _approved_brief(run, root, record)
    proof = _proof(run, root, record)
    _modules(run, root, record, proof)
    _dependencies(root, record, proof)
    if record != before:
        owner.commit(owner.stage(record))
    # Precise host readers consult current committed Module projection.
    before = copy.deepcopy(record)
    _hosts(run, root, record, proof)
    if record != before:
        owner.commit(owner.stage(record))


def reconcile(run: Path, root: Path) -> None:
    """Hold checked ownership; publish current observations before any continuing caller."""
    run, root = state.run_path(run), dispatch._root(root)
    owner = state._Locked(run)
    try:
        _reconcile_owned(owner, root)
    finally:
        warnings = owner.close()
        if warnings:
            raise RunError("; ".join(warnings))
