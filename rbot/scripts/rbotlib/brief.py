"""`rbot brief`: the Run Brief, `<RUN>/run-brief.md` (interfaces spec section 3.1).

`--from handoffs/CP-0.md` builds it from CP-0's `cp0.run_brief_prefill`, `cp0.portfolios`,
`cp0.research_questions` and `cp0.prior_case`, keeping the analyst's earlier edits.
`--set <field>=<value>` records an analyst edit and `--set-tranche <id> <field>=<value>` an
edit of one new tranche's Transaction Summary field (Plan 04); each rebuilds from
`handoffs/CP-0.md`, so the brief always reflects the CP-0 Handoff plus every edit. Every
tranche field is a Run Brief field too: `brief.run_brief_fields` lists it as
`<tranche_id>.<field>` with its own status and citation, which is how an edit survives a
rebuild. Source wins (design D8): a
Sourced value stays and the edit is kept as `analyst_value`; a gap or an earlier assertion
takes the edit as Analyst-asserted. Pathway, depth and Primary are confirmed by
`rbot approve` (`rbotlib.approve`), which also writes the `brief.approval` table; an
approved brief takes no further edit (a changed brief is a new run). The file is
Handoff-format with module id RUN_BRIEF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from rbotlib.brief_schema import COLUMNS as COLUMNS
from rbotlib.brief_schema import FIELDS as FIELDS
from rbotlib.brief_schema import TRANCHE as TRANCHE
from rbotlib.fsio import write_atomic
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
REQUIRED = ("issuer", "issuer_id", "as_of_date", "objective", "analyst")
TRANCHE_OPTIONAL = frozenset(
    {"bloomberg_id", "oid", "expected_ratings", "cr_score", "commitment_date"}
)
TRANCHE_ID = re.compile(r"NEW-[1-9][0-9]*")
TRANCHE_SCALES = {
    "debt_type": "debt_type",
    "use_of_proceeds": "use_of_proceeds",
    "talk_stage": "price_talk_stage",
    "unit": "unit",
}
TRANCHE_DATES = ("maturity_date", "commitment_date")
CURRENCY = re.compile(r"[A-Z]{3}")
PLAIN_DECIMAL = re.compile(r"\d+(\.\d+)?")
CONTROL = re.compile(r"[\x00-\x1f\x7f\u2028\u2029]")


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
    approval: list[list[str]] = field(default_factory=list)
    citations: list[list[str]] = field(default_factory=list)
    cp0_sha256: str = ""


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


def free_text(name: str, value: str) -> str:
    """A value stripped of outer spaces; empty or holding a line break, BriefError."""
    value = value.strip()
    if not value:
        raise BriefError(f"{name} is empty")
    if any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in value):
        raise BriefError(f"{name} holds a line break or control character")
    return value


def normalise_value(name: str, value: str, rules: Rules) -> str:
    """The edit as stored, or BriefError naming why it is refused."""
    value = free_text(name, value)
    if name == "primary":
        match = [v for v in rules.scales["yes_no"] if v.casefold() == value.casefold()]
        if not match:
            raise BriefError(f"primary must be one of {rules.scales['yes_no']}, not {value!r}")
        return match[0]
    if name == "ssim_ev_multiple":
        return _multiple(name, value)
    if name == "as_of_date":
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError as exc:
            raise BriefError(f"{name} must be YYYY-MM-DD, not {value!r}") from exc
    return value


def normalise_tranche(name: str, value: str, rules: Rules) -> str:
    """A tranche edit as stored, or BriefError naming why it is refused."""
    value = free_text(name, value)
    if name in TRANCHE_SCALES:
        values = rules.scales[TRANCHE_SCALES[name]]
        match = [v for v in values if v.casefold() == value.casefold()]
        if not match:
            raise BriefError(f"{name} must be one of {values}, not {value!r}")
        return match[0]
    if name == "currency" and not CURRENCY.fullmatch(value.upper()):
        raise BriefError(f"currency must be a three-letter ISO code, not {value!r}")
    if name == "size" and not PLAIN_DECIMAL.fullmatch(value):
        raise BriefError(f"size must be a plain decimal, not {value!r}")
    if name in TRANCHE_DATES:
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError as exc:
            raise BriefError(f"{name} must be YYYY-MM-DD, not {value!r}") from exc
    return value.upper() if name == "currency" else value


def apply_edit(entry: Entry, value: str) -> None:
    """Source wins: a Sourced value stays; otherwise the edit becomes Analyst-asserted."""
    entry.analyst_value = value
    if entry.status != SOURCED:
        entry.value, entry.status = value, ASSERTED


def prefill_value(row: dict[str, str], rules: Rules) -> str:
    """A pre-fill value held to the rules an analyst's edit of that field meets (MODULE.md)."""
    name, tranche_id, value = row["field"], row["tranche_id"], row["value"]
    if tranche_id and not TRANCHE_ID.fullmatch(tranche_id):
        raise BriefError(f"cp0.run_brief_prefill: tranche id {tranche_id!r} is not NEW-<n>")
    if not value:
        return MISSING
    where = " ".join(p for p in ("cp0.run_brief_prefill", tranche_id, name) if p)
    try:
        if tranche_id and name in TRANCHE:
            return normalise_tranche(name, value, rules)
        if name in ("as_of_date", "primary", "ssim_ev_multiple"):
            return normalise_value(name, value, rules)
        return free_text(name, value)
    except BriefError as exc:
        raise BriefError(f"{where}: {exc} ({name} {value!r})") from exc


def _prefill(h: Handoff, brief: Brief, rules: Rules) -> None:
    columns = ("field", "tranche_id", "value", "status", "cite")
    seen: set[tuple[str, str]] = set()
    for row in _rows(h.tables.get("cp0.run_brief_prefill"), columns):
        key = (row["tranche_id"], row["field"])
        if key in seen:
            raise BriefError(
                f"cp0.run_brief_prefill: {row['field']!r} appears twice for {key[0]!r}"
            )
        seen.add(key)
        if row["tranche_id"] and row["field"] not in TRANCHE:
            raise BriefError(f"cp0.run_brief_prefill: {row['field']!r} is not a tranche field")
        if not row["tranche_id"] and row["field"] not in FIELDS:
            raise BriefError(f"cp0.run_brief_prefill: unknown field {row['field']!r}")
        if row["status"] not in rules.scales["brief_status"]:
            raise BriefError(
                f"cp0.run_brief_prefill: {row['field']!r} has status {row['status']!r}"
            )
        entry = Entry(prefill_value(row, rules), row["status"], "", row["cite"])
        if row["tranche_id"]:
            brief.tranches.setdefault(row["tranche_id"], {})[row["field"]] = entry
        else:
            brief.fields[row["field"]] = entry


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
    prior = ("file", "report_date", "run_id", "offered")
    offered = [p for p in _rows(h.tables.get("cp0.prior_case"), prior) if p["offered"] == "Yes"]
    brief.prior = [[p["file"], p["report_date"], p["run_id"], "No"] for p in offered]
    brief.citations = h.tables["citations"].rows if "citations" in h.tables else []
    _check_cites(brief)
    return brief


def approval(run: Path) -> dict[str, str] | None:
    """The `brief.approval` row of the Run Brief, or None before Approval."""
    if not (run / BRIEF).is_file():
        return None
    h = parse(_read(run / BRIEF))
    rows = _rows(h.tables.get("brief.approval"), COLUMNS["brief.approval"])
    return rows[0] if rows else None


def refuse_if_approved(run: Path) -> None:
    """BriefError once Approval has been given: one Run Brief per run (design D11)."""
    if approved := approval(run):
        done = f"{approved['pathway']} at {approved['depth']} depth on {approved['approved_at']}"
        raise BriefError(f"{BRIEF} was approved ({done}); a changed Run Brief needs a new run")


def previous(run: Path) -> dict[str, Entry]:
    """The fields of the Run Brief as last written (empty when there is none yet)."""
    if not (run / BRIEF).is_file():
        return {}
    h = parse(_read(run / BRIEF))
    rows = _rows(h.tables.get("brief.run_brief_fields"), COLUMNS["brief.run_brief_fields"])
    return {
        r["field"]: Entry(r["value"] or MISSING, r["status"], r["analyst_value"], r["cite"])
        for r in rows
    }


def carry(old: dict[str, Entry], new: Brief) -> None:
    """Re-apply the analyst's earlier edits, and Approval's fields, to a fresh pre-fill."""
    for name, entry in old.items():
        tranche_id, dot, field_name = name.partition(".")
        if dot and entry.analyst_value:
            fields = new.tranches.setdefault(tranche_id, {})
            apply_edit(fields.setdefault(field_name, Entry()), entry.analyst_value)
        elif name in EDITABLE and entry.analyst_value:
            apply_edit(new.fields[name], entry.analyst_value)
        elif name in FIELDS and name not in EDITABLE and entry.status != GAP:
            new.fields[name] = entry


def _table(table_id: str, rows: list[list[str]]) -> list[str]:
    columns = COLUMNS.get(table_id, ("id", "source", "locator", "excerpt"))
    lines = [f"<!-- table: {table_id} -->", "| " + " | ".join(columns) + " |"]
    lines.append("|" + "---|" * len(columns))
    if any(CONTROL.search(cell) for row in rows for cell in row):
        raise BriefError(f"{table_id}: a cell holds a line break or control character")
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
        " earlier Report(s). "
    ) + _approval_summary(brief)


def _approval_summary(brief: Brief) -> str:
    if not brief.approval:
        return "Pathway, depth and Primary are confirmed at Approval (`rbot approve`)."
    at, analyst, pathway, depth, primary = brief.approval[0][:5]
    return f"Approved {at} by {analyst}: {pathway} at {depth} depth, Primary {primary}."


def _tranche_gaps(brief: Brief) -> list[str]:
    hint = "not found in the Source Pack; set it with `rbot brief --set-tranche {0} {1}=<value>`."
    return [
        f"- `{t}.{f}`: " + hint.format(t, f)
        for t, entries in sorted(brief.tranches.items())
        for f in TRANCHE
        if f not in TRANCHE_OPTIONAL and entries.get(f, Entry()).status == GAP
    ]


def render(brief: Brief) -> str:
    gaps = [n for n in REQUIRED if brief.fields[n].status == GAP]
    field_rows = [[n, e.value, e.status, e.analyst_value, e.cite] for n, e in brief.fields.items()]
    for tranche_id, entries in sorted(brief.tranches.items()):
        for f in TRANCHE:
            e = entries.get(f, Entry())
            field_rows.append([f"{tranche_id}.{f}", e.value, e.status, e.analyst_value, e.cite])
    tranche_rows = [
        _tranche_row(t, e)
        for t, e in sorted(brief.tranches.items())
        if brief.fields["primary"].value == "Yes"
    ]
    used = markers(" ".join(cell for row in field_rows + tranche_rows for cell in row))
    front = ["---", "module_id: RUN_BRIEF", f"run_id: {brief.run_id}"]
    front += [f"issuer_id: {brief.fields['issuer_id'].value}"]
    front += [f"analysis_date: {brief.fields['as_of_date'].value}"]
    front += [f"qa_status: {'Restricted' if gaps else 'Pass'}", "inputs: CP-0"]
    front += [f"cp0_sha256: {brief.cp0_sha256}", "---", ""]
    hint = "not found in the Source Pack; set it with `rbot brief --set {0}=<value>`."
    gap_lines = [f"- `{n}`: " + hint.format(n) for n in gaps] + _tranche_gaps(brief)
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
            *(_table("brief.approval", brief.approval) if brief.approval else []),
            *("## Gaps", "", *(gap_lines or ["None."]), "", "## Citations", ""),
            *_table("citations", [r for r in brief.citations if r and r[0] in used]),
        ]
    )


def _edit_tranche(brief: Brief, tranche_id: str, assignment: str, rules: Rules) -> None:
    name, sep, value = assignment.partition("=")
    if not TRANCHE_ID.fullmatch(tranche_id):
        raise BriefError(f"tranche id {tranche_id!r} is not NEW-<n>")
    if not sep or name not in TRANCHE:
        raise BriefError(f"unknown tranche field {name!r}; fields are {', '.join(TRANCHE)}")
    fields = brief.tranches.setdefault(tranche_id, {})
    apply_edit(fields.setdefault(name, Entry()), normalise_tranche(name, value, rules))


def build(
    run: Path,
    source: Path,
    edits: list[str],
    rules: Rules,
    tranche_edits: list[list[str]] | None = None,
) -> Brief:
    """Pre-fill from the CP-0 Handoff, carry earlier edits, then apply the new edits in order."""
    brief = from_cp0(run, _read(source), rules)
    prefilled_tranches = bool(brief.tranches)
    brief.cp0_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    carry(previous(run), brief)
    for assignment in edits:
        name, sep, value = assignment.partition("=")
        if not sep or name not in FIELDS:
            raise BriefError(f"unknown field {name!r}; fields are {', '.join(EDITABLE)}")
        if name not in EDITABLE:
            raise BriefError(f"{name} is set by rbot approve")
        apply_edit(brief.fields[name], normalise_value(name, value, rules))
    for tranche_id, assignment in tranche_edits or []:
        _edit_tranche(brief, tranche_id, assignment, rules)
    if prefilled_tranches and brief.fields["primary"].value != "Yes":
        raise BriefError(
            f"CP-0 lists new tranche(s) {', '.join(sorted(brief.tranches))} but primary is "
            f"{brief.fields['primary'].value!r}; the transaction summary is for a Primary run"
        )
    return brief


def run_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    edits = bool(args.set or args.set_tranche)
    if [bool(args.source), args.show, edits].count(True) != 1:
        print("give --from, or --show, or one or more --set / --set-tranche edits")
        return 1
    try:
        if args.show:
            if not (run / BRIEF).is_file():
                print(f"{run}: no {BRIEF}; run rbot brief --from {CP0} first")
                return 1
            print(_read(run / BRIEF), end="")
            return 0
        return _write(run, args)
    except (BriefError, HandoffError) as exc:
        print(exc)
        return 1
    except OSError as exc:
        print(f"error: {exc.filename or run}: {exc.strerror or exc}")
        return 1


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("brief", help="build, edit or show the Run Brief")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    mode = c.add_mutually_exclusive_group()
    mode.add_argument("--from", dest="source", help="the CP-0 Handoff, relative to the run")
    mode.add_argument("--show", action="store_true", help="print run-brief.md")
    c.add_argument("--set", action="append", help="an analyst edit <field>=<value>")
    c.add_argument(
        "--set-tranche",
        action="append",
        nargs=2,
        metavar=("TRANCHE_ID", "FIELD=VALUE"),
        help="an analyst edit of one new tranche's Transaction Summary field",
    )
    c.set_defaults(run=run_command)


def _reject_blank_or_control(name: str, value: str) -> None:
    if not value:
        raise BriefError(f"{name} needs a value; leave it unset to keep the gap")
    if any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in value):
        raise BriefError(f"{name} must be one line without control characters")


def _multiple(name: str, value: str) -> str:
    try:
        number = Decimal(value.removesuffix("x"))
    except InvalidOperation as exc:
        raise BriefError(f"{name} must be a number, not {value!r}") from exc
    if not number.is_finite() or number <= 0:
        raise BriefError(f"{name} must be a finite number above zero, not {value!r}")
    return format(number, "f")


def _check_cites(brief: Brief) -> None:
    """Every [C<n>] marker in the pre-fill has a row in the CP-0 citations table."""
    cells = [e.cite for e in brief.fields.values()]
    cells += [e.cite for entries in brief.tranches.values() for e in entries.values()]
    known = {row[0] for row in brief.citations if row}
    missing = sorted(markers(" ".join(cells)) - known)
    if missing:
        raise BriefError(
            f"cp0.run_brief_prefill cites {', '.join(missing)}, not in the citations table"
        )


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise BriefError(f"error: {path}: {getattr(exc, 'strerror', None) or exc}") from exc


def _state(run: Path) -> dict[str, Any] | None:
    path = run / "run-state.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(_read(path))
    except ValueError as exc:
        raise BriefError(f"error: {path}: not valid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise BriefError(f"error: {path}: not a JSON object")
    return data


def _approved(run: Path, state: dict[str, Any] | None) -> bool:
    if state and state.get("approval"):
        return True
    return (run / BRIEF).is_file() and "<!-- table: brief.approval -->" in _read(run / BRIEF)


def _record(run: Path, state: dict[str, Any] | None, text: str) -> None:
    """Write the brief and, when the run has a state file, its hash and time (spec 8.1)."""
    from rbotlib import state as rs
    from rbotlib.inventory import output_path

    if rs.write_guard(run) is None:
        write_atomic(output_path(run, BRIEF), text)
        return

    def change(record: rs.Record) -> None:
        if record["approval"] is not None:
            raise BriefError("the brief is approved; re-run rbot approve to change it")
        record["run_brief_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()

    rs.update(run, change, lambda: write_atomic(output_path(run, BRIEF), text))


def _write(run: Path, args: argparse.Namespace) -> int:
    from rbotlib import state as rs

    rs.write_guard(run)
    source = run / CP0
    if args.source and (run / args.source).resolve() != source.resolve():
        raise BriefError(f"--from must be {CP0} in the run; later edits rebuild from it")
    state = _state(run)
    refuse_if_approved(run)
    if _approved(run, state):
        raise BriefError("the brief is approved; re-run rbot approve to change it")
    brief = build(run, source, args.set or [], load_rules(args.root), args.set_tranche)
    _record(run, state, render(brief))
    print(f"{BRIEF}: written")
    return 0
