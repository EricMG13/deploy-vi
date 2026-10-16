"""`rbot grade`: grade every Pathway and Depth of the catalog on this Source Pack (design D10).

Reads `run-brief.md`, `handoffs/CP-0.md` (validated against the CP-0 contract and the run),
each module contract's `sources` inputs and their `document_types` (amendment A4) and the
catalog's Pathway lists and Front Page blocks. Writes `grading.json` and prints the Approval
menu (interfaces spec section 10.2). No Pathway is hidden.

A file is usable evidence when CP-0 classified it readable and about this issuer
(`entity_match` Yes). A step cannot run when a required `sources` input finds no usable file
of its classes and document types, when it is FIT and the pack holds no Portfolio Context
file (limited when no sheet could be read into `brief.portfolios`), or when a required input
in the list cannot run. A step that cannot run blocks the Pathway when it owns a table of an
unconditional Front Page block (or one of those steps needs it); otherwise it limits it, as
does a missing optional document type. Deep Research, Prior Case and the projection are
add-ons that Approval switches on or off, so they never lower a grade.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rbotlib.brief import (
    BRIEF,
    CP0,
    REQUIRED,
    TRANCHE,
    TRANCHE_OPTIONAL,
    BriefError,
    refuse_if_approved,
)
from rbotlib.catalog import ALWAYS, Catalog, Pathway, load_catalog, load_contracts
from rbotlib.contract import Contract, load_contract
from rbotlib.fsio import write_atomic
from rbotlib.handoff import Handoff, HandoffError, Table, parse
from rbotlib.inventory import RunError, output_path
from rbotlib.rules import Rules, load_rules
from rbotlib.validate import EXIT_BLOCKED, EXIT_VALID, check

SCHEMA = "rbot-grading/1"
GRADING = "grading.json"
AVAILABLE, LIMITED, BLOCKED = "Available", "With limitations", "Blocked"
RANK = {AVAILABLE: 0, LIMITED: 1, BLOCKED: 2}
HOST_INPUTS = {"MODEL": ("CP-1",), "PROJECTION": ("CP-2G",), "FIT": ("CP-3",)}
ADD_ONS = frozenset({"CP-DR", "CP-8", "PROJECTION"})
CLASS_LABEL = {
    "issuer": "Issuer Sources",
    "market": "Market Context",
    "portfolio": "Portfolio Context",
}
PORTFOLIO_FILES = ("Portfolio positions", "Portfolio limits")
FETCH_NOTE = (
    "Deep Research fetches public sources only when this host offers a fetch tool; "
    "without one it works from the Source Pack alone (ADR 0004)."
)


class GradeError(ValueError):
    """The run cannot be graded; the message names the missing or invalid input."""


@dataclass(frozen=True)
class Evidence:
    usable: dict[str, frozenset[str]]  # source class -> document types of usable files
    excluded: list[dict[str, str]]  # files CP-0 classified as not usable, with the reason
    portfolios: int


@dataclass
class StepGrade:
    can_run: bool = True
    limitations: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)  # document types
    lifts: list[str] = field(default_factory=list)  # what the analyst could add


def _records(table: Table | None) -> list[dict[str, str]]:
    if table is None:
        return []
    return [dict(zip(table.columns, row, strict=False)) for row in table.rows]


def _exclusion(row: dict[str, str]) -> str | None:
    if row.get("entity_match") != "Yes":
        return f"not about this issuer (names {row.get('entity_named', '—')})"
    if row.get("readable") == "Yes":
        return None
    return "Image-Read only" if row.get("image_read") == "Yes" else "unreadable"


def evidence(cp0: Handoff, brief: Handoff) -> Evidence:
    usable: dict[str, set[str]] = {c: set() for c in CLASS_LABEL}
    excluded = []
    for row in _records(cp0.tables.get("cp0.source_inventory")):
        reason = _exclusion(row)
        if reason:
            excluded.append({"file": row.get("file", ""), "reason": reason})
        else:
            usable.setdefault(row.get("class", ""), set()).add(row.get("document_type", ""))
    frozen = {c: frozenset(types) for c, types in usable.items()}
    return Evidence(frozen, excluded, len(_records(brief.tables.get("brief.portfolios"))))


def _labels(classes: tuple[str, ...]) -> str:
    return " or ".join(CLASS_LABEL.get(c, c) for c in classes)


def _sources(step: str, contract: Contract, ev: Evidence, grade: StepGrade) -> None:
    for need in (i for i in contract.inputs if i.kind == "sources"):
        present = frozenset().union(*(ev.usable.get(c, frozenset()) for c in need.values))
        wanted = frozenset(need.document_types) or present
        if present & wanted:
            continue
        kinds = ", ".join(need.document_types) or "readable file about the issuer"
        lift = f"{kinds} ({_labels(need.values)})"
        grade.limitations.append(f"{step}: no {lift} in the Source Pack")
        grade.missing += list(need.document_types)
        grade.lifts.append(lift)
        grade.can_run = grade.can_run and not need.required


def _fit(ev: Evidence) -> StepGrade:
    """FIT reads prepared portfolio JSON; without a Portfolio Context file it cannot run (spec
    section 5), and with files but no readable positions and limits sheet it is limited."""
    label = CLASS_LABEL["portfolio"]
    if ev.portfolios:
        return StepGrade()
    if ev.usable.get("portfolio"):
        text = f"FIT: the {label} holds no positions and limits sheet RBOT can read"
        lift = f"{' and '.join(PORTFOLIO_FILES)} as CSV or xlsx sheets ({label})"
        return StepGrade(True, [text], [], [lift])
    lift = f"{' and '.join(PORTFOLIO_FILES)} ({label})"
    return StepGrade(False, [f"FIT: no portfolio in the {label}"], list(PORTFOLIO_FILES), [lift])


def _own(step: str, contracts: dict[str, Contract], ev: Evidence) -> StepGrade:
    """What a step's own sources allow, before its inputs are considered."""
    if step == "FIT":
        return _fit(ev)
    grade = StepGrade()
    if step in contracts:
        _sources(step, contracts[step], ev, grade)
    return grade


def _required(step: str, contracts: dict[str, Contract]) -> tuple[str, ...]:
    if step in contracts:
        return tuple(contracts[step].handoff_inputs(required_only=True))
    return HOST_INPUTS.get(step, ())


def _grades(
    steps: tuple[str, ...], contracts: dict[str, Contract], ev: Evidence
) -> dict[str, StepGrade]:
    grades: dict[str, StepGrade] = {}
    for step in steps:
        grade = _own(step, contracts, ev)
        for needed in _required(step, contracts):
            if needed in grades and not grades[needed].can_run:
                grade.can_run = False
                grade.limitations.append(f"{step}: needs {needed}, which cannot run")
        grades[step] = grade
    return grades


def unconditional_tables(catalog: Catalog, front_page: str) -> set[str]:
    """Front Page tables shown on every run: in an `always` block, or in no block at all."""
    blocks = catalog.blocks.get(front_page, ())
    in_blocks = {t for b in blocks for t in b.tables}
    always = {t for b in blocks if b.condition == ALWAYS for t in b.tables}
    return (set(catalog.front_pages.get(front_page, ())) - in_blocks) | always


def _owned(step: str, catalog: Catalog, contracts: dict[str, Contract]) -> set[str]:
    if step in contracts:
        return {t.id for t in contracts[step].tables}
    return {t for t, producer in catalog.host_tables.items() if producer == step}


def _blocking(
    steps: tuple[str, ...],
    grades: dict[str, StepGrade],
    essential: set[str],
    contracts: dict[str, Contract],
) -> list[str]:
    """Steps that cannot run and fill an unconditional block, with the inputs that stop them."""
    blocking = {s for s in steps if not grades[s].can_run and s in essential}
    frontier = list(blocking)
    while frontier:
        for needed in _required(frontier.pop(), contracts):
            if needed in grades and not grades[needed].can_run and needed not in blocking:
                blocking.add(needed)
                frontier.append(needed)
    return [s for s in steps if s in blocking]


def grade_depth(
    pathway: Pathway,
    steps: tuple[str, ...],
    catalog: Catalog,
    contracts: dict[str, Contract],
    ev: Evidence,
) -> dict[str, Any]:
    graded = tuple(s for s in steps if s not in ADD_ONS)
    grades = _grades(graded, contracts, ev)
    shown = unconditional_tables(catalog, pathway.front_page)
    essential = {s for s in graded if _owned(s, catalog, contracts) & shown}
    blocking = _blocking(graded, grades, essential, contracts)
    limited = [s for s in graded if s not in blocking and grades[s].limitations]
    status = BLOCKED if blocking else LIMITED if limited else AVAILABLE
    result = {"status": status, "blocking_modules": blocking, "limited_modules": limited}
    return result | _named([grades[s] for s in graded if s in blocking or s in limited])


def _named(named: list[StepGrade]) -> dict[str, list[str]]:
    """What the blocking and limited steps lack, and what would lift it, in step order."""
    return {
        "missing_document_types": sorted({t for g in named for t in g.missing}),
        "lifting_sources": list(dict.fromkeys(lift for g in named for lift in g.lifts)),
        "limitations": [text for g in named for text in g.limitations],
    }


def recommended_depth(depths: dict[str, dict[str, Any]]) -> str | None:
    """The fullest depth with the best grade that is not Blocked; None when all are Blocked."""
    order = sorted(depths, key=lambda d: (RANK[depths[d]["status"]], d != "full"))
    best = next(iter(order), None)
    return best if best is not None and depths[best]["status"] != BLOCKED else None


def _brief_gaps(brief: Handoff) -> list[str]:
    rows = _records(brief.tables.get("brief.run_brief_fields"))
    critical = {f for f in TRANCHE if f not in TRANCHE_OPTIONAL}
    gaps = [r["field"] for r in rows if r.get("status") == "Gap" and r["field"] in REQUIRED]
    tranche = [r["field"] for r in rows if r.get("status") == "Gap" and "." in r["field"]]
    return gaps + [f for f in tranche if f.partition(".")[2] in critical]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_inputs(run: Path, root: Path, rules: Rules) -> tuple[Handoff, Handoff]:
    for name in (BRIEF, CP0):
        if not (run / name).is_file():
            raise GradeError(f"{run}: no {name}; cp-start turn 1 writes it")
    try:
        refuse_if_approved(run)  # the grading record an Approval points to stays as it was
    except (BriefError, HandoffError) as exc:
        raise GradeError(str(exc)) from exc
    text = (run / CP0).read_text(encoding="utf-8")
    try:
        contract = load_contract(root / "modules" / "CP-0" / "contract.json", rules)
    except (ValueError, KeyError, TypeError) as exc:
        raise GradeError(f"modules/CP-0/contract.json is not readable: {exc}") from exc
    code, findings = check(text, contract, rules, run)
    if code not in (EXIT_VALID, EXIT_BLOCKED):
        listed = "; ".join(f"{f.code}: {f.message}" for f in findings)
        raise GradeError(f"{CP0} does not validate (exit {code}): {listed}")
    try:
        brief = parse((run / BRIEF).read_text(encoding="utf-8"))
    except HandoffError as exc:
        raise GradeError(f"{BRIEF}: {exc}") from exc
    if brief.front_matter.get("cp0_sha256") != _sha(run / CP0):
        raise GradeError(f"{BRIEF} was built from another {CP0}; run rbot brief --from {CP0}")
    return brief, parse(text)


def _catalog(root: Path) -> Catalog:
    try:
        return load_catalog(root)
    except (ValueError, KeyError, TypeError) as exc:
        raise GradeError(f"catalog.json is not readable: {exc}") from exc


def contracts_sha256(root: Path) -> str:
    """One sha256 over every module contract (path and bytes), so Approval sees a change."""
    digest = hashlib.sha256()
    for path in sorted((root / "modules").glob("*/contract.json")):
        digest.update(path.parent.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def grade_run(run: Path, root: Path, rules: Rules) -> dict[str, Any]:
    brief, cp0 = _read_inputs(run, root, rules)
    catalog = _catalog(root)
    problems: list[str] = []
    contracts = load_contracts(root, rules, problems)
    unknown = [
        s for p in catalog.pathways for d in p.depths.values() for s in d if s not in contracts
    ]
    unknown = [s for s in unknown if s not in rules.host_producers]
    if problems or unknown:
        raise GradeError(f"the RBOT folder does not check: {problems or unknown}; run rbot check")
    ev = evidence(cp0, brief)
    pathways = []
    for p in catalog.pathways:
        depths = {d: grade_depth(p, steps, catalog, contracts, ev) for d, steps in p.depths.items()}
        entry: dict[str, Any] = {"id": p.id, "label": p.label, "front_page": p.front_page}
        pathways.append(entry | {"recommended_depth": recommended_depth(depths), "depths": depths})
    fields = {r["field"]: r for r in _records(brief.tables.get("brief.run_brief_fields"))}
    return {
        "schema": SCHEMA,
        "run_id": run.name,
        "graded_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "brief_sha256": _sha(run / BRIEF),
        "cp0_sha256": _sha(run / CP0),
        "catalog_sha256": _sha(root / "catalog.json"),
        "contracts_sha256": contracts_sha256(root),
        "issuer": fields.get("issuer", {}).get("value", "—"),
        "issuer_id": fields.get("issuer_id", {}).get("value", "—"),
        "as_of_date": fields.get("as_of_date", {}).get("value", "—"),
        "primary_pretick": bool(_records(brief.tables.get("snapshot.transaction_summary"))),
        "tranches": [
            r["tranche_id"] for r in _records(brief.tables.get("snapshot.transaction_summary"))
        ],
        "brief_gaps": _brief_gaps(brief),
        "excluded_files": ev.excluded,
        "research_questions": [
            {"question_id": r["question_id"], "question": r["question"]}
            for r in _records(brief.tables.get("brief.research_questions"))
        ],
        "prior_case": _records(brief.tables.get("brief.prior_case")),
        "fetch_note": FETCH_NOTE,
        "pathways": pathways,
    }


def _cell(values: list[str]) -> str:
    return ", ".join(values) or "—"


def _menu_rows(grading: dict[str, Any]) -> list[str]:
    lines = ["| Pathway | Depth | Grade | Blocking | Limited | Missing document types |"]
    lines.append("|---|---|---|---|---|---|")
    for p in grading["pathways"]:
        for depth, g in p["depths"].items():
            mark = " (recommended)" if depth == p["recommended_depth"] else ""
            cells = [p["label"], depth + mark, g["status"], _cell(g["blocking_modules"])]
            cells += [_cell(g["limited_modules"]), _cell(g["missing_document_types"])]
            lines.append("| " + " | ".join(cells) + " |")
    return lines


def _menu_notes(grading: dict[str, Any]) -> list[str]:
    lines = ["", "## Limitations and the sources that would lift them", ""]
    for p in grading["pathways"]:
        for depth, g in p["depths"].items():
            lines += [f"- {p['label']}, {depth}: {text}" for text in g["limitations"]]
            lines += [f"  - would lift: {lift}" for lift in g["lifting_sources"]]
    if len(lines) == 3:
        lines.append("- None.")
    excluded = [f"- `{f['file']}`: {f['reason']}" for f in grading["excluded_files"]]
    lines += ["", "## Files not used as evidence", "", *(excluded or ["- None."])]
    return lines


def _menu_flags(grading: dict[str, Any]) -> list[str]:
    tranches = grading["tranches"]
    primary = f"pre-ticked: the Run Brief has {len(tranches)} new tranche(s) ({_cell(tranches)})"
    questions = [f"- {q['question_id']}: {q['question']}" for q in grading["research_questions"]]
    prior = [f"- {r['file']} ({r['report_date']}, {r['run_id']})" for r in grading["prior_case"]]
    gaps = [f"- `{g}` is a gap" for g in grading["brief_gaps"]]
    return [
        "",
        "## Primary",
        "",
        primary if tranches else "not pre-ticked: the Run Brief has no new tranche",
        "",
        "## Deep Research questions (Full depth)",
        "",
        *(questions or ["- None."]),
        "",
        "## Prior Case",
        "",
        *(prior or ["- None offered: the pack holds no earlier RBOT Report."]),
        "",
        "## Run Brief gaps",
        "",
        *(gaps or ["- None."]),
        "",
        f"Fetch: {grading['fetch_note']}",
    ]


def menu(grading: dict[str, Any]) -> str:
    who = f"{grading['issuer']} ({grading['issuer_id']}), as of {grading['as_of_date']}"
    head = f"# Approval menu — {who}"
    if not grading["pathways"]:
        body = ["The catalog lists no Pathway yet, so nothing can be approved."]
    else:
        body = _menu_rows(grading) + _menu_notes(grading)
    return "\n".join([head, "", *body, *_menu_flags(grading), ""])


def run_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    try:
        from rbotlib import state

        with state.publication(run) as check:
            grading = grade_run(run, args.root, load_rules(args.root))
            check()
            write_atomic(
                output_path(run, GRADING), json.dumps(grading, indent=2, ensure_ascii=False) + "\n"
            )
    except (GradeError, RunError, OSError) as exc:
        print(exc)
        return 1
    print(menu(grading), end="")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("grade", help="grade every Pathway and Depth; print the Approval menu")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    c.set_defaults(run=run_command)
