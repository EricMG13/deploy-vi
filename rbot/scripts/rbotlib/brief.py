"""`rbot brief`: the Run Brief, `<RUN>/run-brief.md` (interfaces spec section 3.1).

`--from handoffs/CP-0.md` builds it from CP-0's `cp0.run_brief_prefill`, `cp0.portfolios`,
`cp0.research_questions` and `cp0.prior_case`, keeping the analyst's earlier edits.
`--set <field>=<value>` records an analyst edit and rebuilds from `handoffs/CP-0.md`, so
the brief always reflects the CP-0 Handoff plus every edit. Source wins (design D8): a
Sourced value stays and the edit is kept as `analyst_value`; a gap or an earlier assertion
takes the edit as Analyst-asserted. Pathway, depth and Primary are confirmed by
`rbot approve` (Plan 04), which also writes the approval table. The file is
Handoff-format with module id RUN_BRIEF.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from rbotlib.handoff import Handoff, HandoffError, Table, markers, parse
from rbotlib.rules import Rules, load_rules

BRIEF = "run-brief.md"
CP0 = "handoffs/CP-0.md"
MISSING = "—"
GAP, SOURCED, ASSERTED = "Gap", "Sourced", "Analyst-asserted"
EDITABLE = (
    "issuer",
    "issuer_id",
    "as_of_date",
    "objective",
    "analyst",
    "primary",
    "morningstar_issuer_id",
    "ssim_ev_multiple",
)
FIELDS = (*EDITABLE, "pathway", "depth")
REQUIRED = ("issuer", "issuer_id", "as_of_date", "objective", "analyst")
TRANCHE = (
    "borrower",
    "bloomberg_id",
    "instrument",
    "debt_type",
    "use_of_proceeds",
    "size",
    "currency",
    "unit",
    "price_talk",
    "talk_stage",
    "oid",
    "maturity_date",
    "expected_ratings",
    "cr_score",
    "commitment_date",
)
TRANCHE_OPTIONAL = frozenset(
    {"bloomberg_id", "oid", "expected_ratings", "cr_score", "commitment_date"}
)
COLUMNS = {
    "snapshot.run_header": (
        "run_id",
        "issuer",
        "issuer_id",
        "as_of_date",
        "objective",
        "analyst",
        "pathway",
        "depth",
        "primary",
        "currency",
        "unit",
        "morningstar_issuer_id",
        "ssim_ev_multiple_x",
        "report_date",
    ),
    "snapshot.transaction_summary": ("tranche_id", *TRANCHE, "status", "analyst_value", "cite"),
    "brief.run_brief_fields": ("field", "value", "status", "analyst_value", "cite"),
    "brief.portfolios": (
        "portfolio_id",
        "portfolio_name",
        "strategy",
        "positions_file",
        "limits_file",
        "as_of_date",
        "prepared_json",
    ),
    "brief.research_questions": ("question_id", "question", "consumer_module", "approved"),
    "brief.prior_case": ("file", "report_date", "run_id", "accepted"),
}


class BriefError(ValueError):
    """An edit or input the Run Brief refuses; the message names it."""


@dataclass
class Entry:
    value: str = MISSING
    status: str = GAP
    analyst_value: str = ""
    cite: str = ""


@dataclass
class Brief:
    run_id: str
    fields: dict[str, Entry] = field(default_factory=lambda: {f: Entry() for f in FIELDS})
    tranches: dict[str, dict[str, Entry]] = field(default_factory=dict)
    portfolios: list[list[str]] = field(default_factory=list)
    questions: list[list[str]] = field(default_factory=list)
    prior: list[list[str]] = field(default_factory=list)
    citations: list[list[str]] = field(default_factory=list)


def _rows(table: Table | None, columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Each row as a dict of the named columns; a cell holding only the gap marker is empty."""
    if table is None:
        return []
    index = {c.casefold(): i for i, c in enumerate(table.columns)}
    rows = []
    for row in table.rows:
        cells = {c: row[index[c]] if index.get(c, len(row)) < len(row) else "" for c in columns}
        rows.append({c: "" if v == MISSING else v for c, v in cells.items()})
    return rows


def normalise_value(name: str, value: str, rules: Rules) -> str:
    """The edit as stored, or BriefError naming why it is refused."""
    value = value.strip()
    if name == "primary":
        match = [v for v in rules.scales["yes_no"] if v.casefold() == value.casefold()]
        if not match:
            raise BriefError(f"primary must be one of {rules.scales['yes_no']}, not {value!r}")
        return match[0]
    try:
        if name == "as_of_date":
            return date.fromisoformat(value).isoformat()
        if name == "ssim_ev_multiple":
            return str(Decimal(value.removesuffix("x")))
    except (ValueError, InvalidOperation) as exc:
        kind = "YYYY-MM-DD" if name == "as_of_date" else "a number"
        raise BriefError(f"{name} must be {kind}, not {value!r}") from exc
    return value


def apply_edit(entry: Entry, value: str) -> None:
    """Source wins: a Sourced value stays; otherwise the edit becomes Analyst-asserted."""
    entry.analyst_value = value
    if entry.status != SOURCED:
        entry.value, entry.status = value, ASSERTED


def _prefill(h: Handoff, brief: Brief, rules: Rules) -> None:
    columns = ("field", "tranche_id", "value", "status", "cite")
    for row in _rows(h.tables.get("cp0.run_brief_prefill"), columns):
        status = row["status"] if row["status"] in rules.scales["brief_status"] else GAP
        entry = Entry(row["value"] or MISSING, status, "", row["cite"])
        if row["tranche_id"] and row["field"] in TRANCHE:
            brief.tranches.setdefault(row["tranche_id"], {})[row["field"]] = entry
        elif row["tranche_id"]:
            raise BriefError(f"cp0.run_brief_prefill: {row['field']!r} is not a tranche field")
        elif row["field"] in FIELDS:
            brief.fields[row["field"]] = entry
        else:
            raise BriefError(f"cp0.run_brief_prefill: unknown field {row['field']!r}")


def from_cp0(run: Path, cp0_text: str, rules: Rules) -> Brief:
    h = parse(cp0_text)
    brief = Brief(run.name)
    _prefill(h, brief, rules)
    portfolio = COLUMNS["brief.portfolios"][:-1]
    for p in _rows(h.tables.get("cp0.portfolios"), portfolio):
        brief.portfolios.append([*p.values(), f"prepared/portfolios/{p['portfolio_id']}.json"])
    questions = COLUMNS["brief.research_questions"][:-1]
    brief.questions = [
        [*q.values(), "Yes"] for q in _rows(h.tables.get("cp0.research_questions"), questions)
    ]
    prior = COLUMNS["brief.prior_case"][:-1]
    brief.prior = [[*p.values(), "No"] for p in _rows(h.tables.get("cp0.prior_case"), prior)]
    brief.citations = h.tables["citations"].rows if "citations" in h.tables else []
    return brief


def previous(run: Path) -> dict[str, Entry]:
    """The fields of the Run Brief as last written (empty when there is none yet)."""
    if not (run / BRIEF).is_file():
        return {}
    h = parse((run / BRIEF).read_text(encoding="utf-8"))
    rows = _rows(h.tables.get("brief.run_brief_fields"), COLUMNS["brief.run_brief_fields"])
    return {
        r["field"]: Entry(r["value"] or MISSING, r["status"], r["analyst_value"], r["cite"])
        for r in rows
    }


def carry(old: dict[str, Entry], new: Brief) -> None:
    """Re-apply the analyst's earlier edits, and Approval's fields, to a fresh pre-fill."""
    for name, entry in old.items():
        if name in EDITABLE and entry.analyst_value:
            apply_edit(new.fields[name], entry.analyst_value)
        elif name in FIELDS and name not in EDITABLE and entry.status != GAP:
            new.fields[name] = entry


def _table(table_id: str, rows: list[list[str]]) -> list[str]:
    columns = COLUMNS.get(table_id, ("id", "source", "locator", "excerpt"))
    lines = [f"<!-- table: {table_id} -->", "| " + " | ".join(columns) + " |"]
    lines.append("|" + "---|" * len(columns))
    cells = [[(cell or MISSING).replace("|", "\\|") for cell in row] for row in rows]
    lines += ["| " + " | ".join(row) + " |" for row in cells]
    return [*lines, ""]


def _tranche_row(tranche_id: str, entries: dict[str, Entry]) -> list[str]:
    values = [entries.get(f, Entry()).value for f in TRANCHE]
    critical = [entries.get(f, Entry()) for f in TRANCHE if f not in TRANCHE_OPTIONAL]
    status = SOURCED
    if any(e.status == GAP or e.value == MISSING for e in critical):
        status = GAP
    elif any(e.status == ASSERTED for e in entries.values()):
        status = ASSERTED
    edits = "; ".join(f"{f}={e.analyst_value}" for f, e in entries.items() if e.analyst_value)
    cites = " ".join(dict.fromkeys(m for e in entries.values() for m in e.cite.split()))
    return [tranche_id, *values, status, edits, cites]


def _header_row(brief: Brief) -> list[str]:
    f = {name: entry.value for name, entry in brief.fields.items()}
    multiple = f["ssim_ev_multiple"]
    head = [brief.run_id, *(f[n] for n in ("issuer", "issuer_id", "as_of_date", "objective"))]
    head += [f[n] for n in ("analyst", "pathway", "depth", "primary")]
    tail = [f["morningstar_issuer_id"], f"{multiple}x" if multiple != MISSING else MISSING]
    return [*head, MISSING, MISSING, *tail, MISSING]  # currency, unit (CP-1); report_date


def _analysis(brief: Brief) -> str:
    sourced = sum(e.status == SOURCED for e in brief.fields.values())
    asserted = sum(e.status == ASSERTED for e in brief.fields.values())
    return (
        f"Run Brief pre-filled from the CP-0 Handoff: {sourced} field(s) sourced, {asserted}"
        f" analyst-asserted; {len(brief.tranches)} new tranche(s), {len(brief.portfolios)}"
        f" portfolio(s), {len(brief.questions)} research question(s), {len(brief.prior)}"
        " earlier Report(s). Pathway, depth and Primary are confirmed at Approval"
        " (`rbot approve`)."
    )


def render(brief: Brief) -> str:
    gaps = [n for n in REQUIRED if brief.fields[n].status == GAP]
    field_rows = [[n, e.value, e.status, e.analyst_value, e.cite] for n, e in brief.fields.items()]
    tranche_rows = [_tranche_row(t, e) for t, e in sorted(brief.tranches.items())]
    used = markers(" ".join(cell for row in field_rows + tranche_rows for cell in row))
    front = ["---", "module_id: RUN_BRIEF", f"run_id: {brief.run_id}"]
    front += [f"issuer_id: {brief.fields['issuer_id'].value}"]
    front += [f"analysis_date: {brief.fields['as_of_date'].value}"]
    front += [f"qa_status: {'Restricted' if gaps else 'Pass'}", "inputs: CP-0", "---", ""]
    hint = "not found in the Source Pack; set it with `rbot brief --set {0}=<value>`."
    gap_lines = [f"- `{n}`: " + hint.format(n) for n in gaps] or ["None."]
    return "\n".join(
        [
            *front,
            *("## Analysis", "", _analysis(brief), "", "## Tables", ""),
            *_table("snapshot.run_header", [_header_row(brief)]),
            *_table("snapshot.transaction_summary", tranche_rows),
            *_table("brief.run_brief_fields", field_rows),
            *_table("brief.portfolios", brief.portfolios),
            *_table("brief.research_questions", brief.questions),
            *_table("brief.prior_case", brief.prior),
            *("## Gaps", "", *gap_lines, "", "## Citations", ""),
            *_table("citations", [r for r in brief.citations if r and r[0] in used]),
        ]
    )


def build(run: Path, source: Path, edits: list[str], rules: Rules) -> Brief:
    """Pre-fill from the CP-0 Handoff, carry earlier edits, then apply `edits` in order."""
    brief = from_cp0(run, source.read_text(encoding="utf-8"), rules)
    carry(previous(run), brief)
    for assignment in edits:
        name, sep, value = assignment.partition("=")
        if not sep or name not in FIELDS:
            raise BriefError(f"unknown field {name!r}; fields are {', '.join(EDITABLE)}")
        if name not in EDITABLE:
            raise BriefError(f"{name} is set by rbot approve")
        apply_edit(brief.fields[name], normalise_value(name, value, rules))
    return brief


def run_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    if args.show:
        if not (run / BRIEF).is_file():
            print(f"{run}: no {BRIEF}; run rbot brief --from {CP0} first")
            return 1
        print((run / BRIEF).read_text(encoding="utf-8"), end="")
        return 0
    source = Path(args.source or CP0)
    source = source if source.is_absolute() else run / source
    try:
        brief = build(run, source, args.set or [], load_rules(args.root))
    except (BriefError, HandoffError, OSError) as exc:
        print(exc)
        return 1
    (run / BRIEF).write_text(render(brief), encoding="utf-8")
    print(f"{BRIEF}: written")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("brief", help="build, edit or show the Run Brief")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    mode = c.add_mutually_exclusive_group(required=True)
    mode.add_argument("--from", dest="source", help="the CP-0 Handoff, relative to the run")
    mode.add_argument("--set", action="append", help="an analyst edit <field>=<value>")
    mode.add_argument("--show", action="store_true", help="print run-brief.md")
    c.set_defaults(run=run_command)
