"""Read-only native prior/current qualification, reusable under a caller's held lock.

Callers reconcile current observations first. Capture is a cooperating-reader
readback, not a snapshot or a guarantee against hostile filesystem replacement.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rbotlib import attempts, current, dispatch, fetched, host_evidence, state
from rbotlib.catalog import load_catalog
from rbotlib.contract import Input
from rbotlib.inventory import RunError
from rbotlib.isolation_capture import Capture, admit
from rbotlib.prior_candidates import PriorCandidate, _relative, qualify_candidate
from rbotlib.prior_report import inspect_report
from rbotlib.report import run_json
from rbotlib.rules import Rules, load_rules

Record = dict[str, Any]


@dataclass(frozen=True)
class PriorContext:
    """Detached original Report, current comparison payload, and serializable binding."""

    prior: PriorCandidate
    current: Record
    binding: Record


def _selected(run: Path, record: Record, requested: str | None) -> str:
    choice = record.get("prior_case") or {}
    if record["approval"] is None or not choice.get("accepted") or not choice.get("offered"):
        raise RunError("Prior comparison requires Approval with an accepted offered Prior Case")
    name = _relative(choice.get("report"))
    if requested is not None and requested not in (name, str(Path(record["pack_root"]) / name)):
        raise RunError("Prior comparison: requested path differs from approved original Report")
    return name


def _root_files(root: Path) -> list[Path]:
    # This is the existing host evidence context's actual backend/contract read set.
    return [root / n for n in ("rules.json", "catalog.json", "canon.md")] + sorted(
        [*(root / "scripts").rglob("*.py"), *(root / "modules").glob("*/contract.json")]
    )


def _inputs(run: Path, root: Path, record: Record, captured: Capture) -> None:
    for name in (
        state.STATE,
        "inventory.json",
        "prepared/index.json",
        "grading.json",
        "run-brief.md",
        "handoffs/CP-0.md",
    ):
        captured.read(dispatch._file(run, name))
    for path in _root_files(root):
        captured.read(path)
    rows = dispatch._prepared(run, record)
    for row in rows:
        captured.read(dispatch._file(Path(record["pack_root"]), row["path"]))
        if row.get("prepared") is not None:
            captured.read(dispatch._file(run, row["prepared"]))
    index = dispatch._json(dispatch._file(run, "prepared/index.json"))
    for row in dispatch._records(run / "prepared/index.json", index, "portfolios"):
        captured.read(dispatch._file(run, row["json"]))


def _fetched_paths(run: Path) -> tuple[Path, ...]:
    folder = run / "fetched"
    if not folder.exists() and not folder.is_symlink():
        return ()
    admit(folder, directory=True)
    return tuple(sorted(p for p in folder.iterdir() if fetched.NAME.fullmatch(p.name)))


def _history(run: Path, module: str, step: Record, captured: Capture) -> None:
    current.checked(step, module)
    for sequence in range(1, len(step.get("accept_history", [])) + 1):
        captured.read(attempts.event_path(run, module, sequence))
    events = attempts.read_history(run, module, step)
    if module != "CP-0" and step["status"] in ("accepted", "blocked") and not events:
        raise RunError(f"{module}: committed Module requires reported dispatch/validation evidence")
    if any(event["event"] == "validation" for event in events):
        captured.read(dispatch._file(run, f"validate/{module}.json"))


def _handoffs(run: Path, root: Path, record: Record, rules: Rules, captured: Capture) -> Record:
    handoffs: Record = {}
    for module, step in record["steps"].items():
        if module == "CP-8":
            continue
        if step["status"] in ("pending", "running"):
            raise RunError(
                f"Prior comparison requires terminal predecessor {module}: {step['status']}"
            )
        if step["kind"] == "module":
            _history(run, module, step, captured)
        if step["status"] not in ("accepted", "blocked"):
            continue
        need = Input("handoff", (module,), True, "native comparison predecessor")
        dispatch._handoff_permission(run, root, need, record, rules)
        captured.read(dispatch._file(run, f"handoffs/{module}.md"))
        # Citations retain owner-local provenance. Native validation was just re-run.
        handoffs[module] = run_json.handoff_entry(run, module, step, None)
        if step["kind"] == "host":
            for name in step.get("outputs", {}):
                captured.read(dispatch._file(run, name))
            captured.read(dispatch._file(run, "log/rbot.log"))
    return handoffs


def _document(run: Path, root: Path, record: Record, handoffs: Record) -> Record:
    cp0 = handoffs.get("CP-0")
    if cp0 is not None and cp0["front_matter"].get("run_id") != record["run_id"]:
        cp0["original_front_matter"] = dict(cp0["front_matter"])
        cp0["native_cp0_lineage"] = dict(record["cp0_lineage"])
        cp0["front_matter"] = dict(cp0["front_matter"], run_id=record["run_id"])
    brief, brief_h = run_json._brief(run)
    plan = [name for name in record["plan"] if name != "CP-8"]
    projected = dict(record, steps={n: record["steps"][n] for n in plan})
    model = run_json._model(run, projected["steps"].get("MODEL"))
    fit = run_json._fit(run, projected["steps"].get("FIT"), brief_h)
    pathway = load_catalog(root).pathway(record["pathway"])
    if pathway is None:
        raise RunError("Prior comparison: approved pathway missing")
    document = dict(
        schema="rbot-run/1",
        rbot_version=record["rbot_version"],
        run_id=record["run_id"],
        generated_at=record["approval"]["approved_at"],
        generated_at_basis="current Approval approved_at; not Report publication",
        run_brief=brief,
        pathway=record["pathway"],
        depth=record["depth"],
        primary=record["primary"],
        front_page=pathway.front_page,
        plan=plan,
        steps={n: run_json.public_step(s) for n, s in projected["steps"].items()},
        handoffs=handoffs,
        model=model,
        fit=fit,
        modules=run_json._modules(root, plan),
        fetched=run_json._fetched(run),
        limitations=run_json.limitations(projected, brief, handoffs, model),
        prior_case=dict(record["prior_case"]),
    )
    _, _, omissions = inspect_report(document)
    if cp0 is not None and "native_cp0_lineage" in cp0:
        omissions.append(
            "Native qualified pending CP-0 identity projected to current run; "
            "authored front matter, hash and registered lineage retained"
        )
    document["limitations"]["unforeseen"] += [dict(kind="comparison", text=t) for t in omissions]
    return document


def _binding(
    run: Path, root: Path, record: Record, prior: PriorCandidate, captured: Capture
) -> Record:
    fields = (
        "rbot_version",
        "run_id",
        "pack_root",
        "issuer_id",
        "as_of_date",
        "approval",
        "prior_case",
        "plan",
        "pathway",
        "depth",
        "primary",
        "deep_research",
        "ownership",
        "run_brief_sha256",
        "approved_origins",
        "completion_origin",
        "cp0_lineage",
        "brief_edits",
    )
    authority = {k: record[k] for k in fields if k in record}
    authority["steps"] = {n: s for n, s in record["steps"].items() if n != "CP-8"}
    excluded = {run / state.STATE, run / "log/rbot.log"}
    return dict(
        schema="rbot-prior-context/1",
        run=str(run),
        root=str(root),
        prior=dict(path=prior.source, sha256=prior.sha256),
        authority=host_evidence.digest(authority),
        files={
            str(p): hashlib.sha256(raw).hexdigest()
            for p, raw in captured.inventory()
            if p not in excluded
        },
    )


def capture(run: Path, root: Path, requested_prior: str | None = None) -> PriorContext:
    """Qualify exact owned inputs without locking, writing, logging, or recursive dispatch."""
    run = state.run_path(run)
    admit(root, directory=True)
    root = dispatch._root(root)
    record = state.write_guard(run)
    if record is None:
        raise RunError("Prior comparison requires an owned native run")
    selected = _selected(run, record, requested_prior)
    captured = Capture()
    _inputs(run, root, record, captured)
    rules = load_rules(root)
    dispatch._context(run, root, record, rules)
    prior = qualify_candidate(
        run, Path(record["pack_root"]), selected, (record["issuer_id"], run.name)
    )
    if not prior.offered or prior.payload is None or prior.metadata is None:
        raise RunError(
            f"Prior comparison: approved original is not eligible: {prior.issue or selected}"
        )
    current._host_origins(run, root, record)
    fetched_paths = _fetched_paths(run)
    for path in fetched_paths:
        captured.read(path)
    handoffs = _handoffs(run, root, record, rules, captured)
    document = _document(run, root, record, handoffs)
    # Re-qualify source hashes and guarded bytes after every transitive reader.
    dispatch._prepared(run, record)
    _handoffs(run, root, record, rules, captured)
    if _fetched_paths(run) != fetched_paths:
        raise RunError("Prior comparison: fetched input set changed during capture")
    captured.verify()
    if state.write_guard(run) != record:
        raise RunError("Prior comparison: owned state changed during capture")
    binding = _binding(run, root, record, prior, captured)
    # Detach nested state references and reject non-finite extension metadata.
    return PriorContext(prior, document, json.loads(json.dumps(binding, allow_nan=False)))


def requalify(run: Path, root: Path, binding: Record) -> PriorContext:
    """Recapture all authority and bytes; refuse stale or caller-altered input bindings."""
    fresh = capture(run, root)
    if fresh.binding != binding:
        raise RunError("Prior comparison: input binding changed; regenerate the diff")
    return fresh
