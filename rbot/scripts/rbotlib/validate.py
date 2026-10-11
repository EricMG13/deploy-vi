"""Check a Handoff against its module's contract and the shared rules.

Exit codes follow Deploy V: 0 valid, 2 malformed, 3 blocked (valid but
qa_status Blocked), 4 identity mismatch. A Handoff over the upstream cap
(spec section 7, caos MAX_UPSTREAM_HANDOFF_BYTES) is malformed: `too_large`.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from rbotlib.contract import Column, Contract, TableSpec
from rbotlib.handoff import Handoff, HandoffError, Table, cells, markers, parse
from rbotlib.rules import Rules

EXIT_VALID, EXIT_MALFORMED, EXIT_BLOCKED, EXIT_IDENTITY = 0, 2, 3, 4
MAX_HANDOFF_BYTES = 98_304


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _front_matter(h: Handoff, contract: Contract, rules: Rules) -> list[Finding]:
    found = [
        Finding("front_matter_missing", f"front matter has no {key!r}")
        for key in rules.front_matter
        if not h.front_matter.get(key)
    ]
    module_id = h.front_matter.get("module_id")
    if module_id and module_id != contract.module_id:
        found.append(Finding("identity", f"module_id {module_id!r} is not {contract.module_id!r}"))
    status = h.front_matter.get("qa_status")
    if status and status not in rules.qa_status:
        found.append(Finding("qa_status", f"qa_status {status!r} not in {rules.qa_status}"))
    return found


def _sections(h: Handoff, rules: Rules) -> list[Finding]:
    if tuple(h.sections) == rules.sections:
        return []
    expected = list(rules.sections)
    return [Finding("sections", f"H2 sections are {h.sections}, expected {expected}")]


def _cell(column: Column, cell: str, where: str, rules: Rules) -> Finding | None:
    # A scale value is valid even when it reads like a placeholder ("N/A" is a
    # Recommendation); only then do the placeholder and scale rules apply.
    if column.scale and cell in rules.scales[column.scale]:
        return None
    if rules.is_placeholder(cell):
        return Finding("critical_placeholder", f"{where}: {cell!r}") if column.critical else None
    if column.scale:
        return Finding("off_scale", f"{where}: {cell!r}")
    return None


def _cell_findings(spec: TableSpec, table: Table, rules: Rules) -> list[Finding]:
    found: list[Finding] = []
    index = {name.casefold(): i for i, name in enumerate(table.columns)}
    present = [(c, index[c.name.casefold()]) for c in spec.columns if c.name.casefold() in index]
    for n, row in enumerate(table.rows, 1):
        if len(row) != len(table.columns):
            found.append(Finding("row_shape", f"{spec.id} row {n} has {len(row)} cells"))
            continue
        for column, i in present:
            finding = _cell(column, row[i], f"{spec.id} row {n} {column.name}", rules)
            if finding:
                found.append(finding)
    return found


def _table(spec: TableSpec, h: Handoff, rules: Rules) -> list[Finding]:
    table = h.tables.get(spec.id)
    if table is None:
        return [Finding("table_missing", f"no table tagged {spec.id}")]
    have = {c.casefold() for c in table.columns}
    found = [
        Finding("column_missing", f"{spec.id} has no column {c.name!r}")
        for c in spec.columns
        if c.name.casefold() not in have
    ]
    if len(table.rows) < spec.min_rows:
        found.append(
            Finding("too_few_rows", f"{spec.id} has {len(table.rows)} rows, needs {spec.min_rows}")
        )
    return found + _cell_findings(spec, table, rules)


def _tags(h: Handoff, contract: Contract) -> list[Finding]:
    declared = {t.id for t in contract.tables} | {"citations"}
    found = [Finding("duplicate_table", f"table {t} is tagged twice") for t in h.duplicate_tags]
    found += [Finding("orphan_tag", f"tag {t} has no table under it") for t in h.orphan_tags]
    found += [
        Finding("undeclared_table", f"table {t} is not in the contract")
        for t in h.tables
        if t not in declared
    ]
    return found


def _outside_citation_rows(body: str, table: Table) -> str:
    """The body without the citations table's own rows, so a row cannot cite itself."""
    rows = {tuple(row) for row in table.rows}
    kept = [line for line in body.splitlines() if tuple(cells(line)) not in rows]
    return "\n".join(kept)


def _citations(h: Handoff, rules: Rules) -> list[Finding]:
    table = h.tables.get("citations")
    if table is None:
        return [Finding("table_missing", "no table tagged citations")]
    if [c.casefold() for c in table.columns] != list(rules.citation_columns):
        expected = list(rules.citation_columns)
        return [Finding("column_missing", f"citations columns must be {expected}")]
    found: list[Finding] = []
    seen: Counter[str] = Counter()
    for row in table.rows:
        if len(row) != len(table.columns) or any(not cell.strip() for cell in row):
            found.append(Finding("citation_incomplete", f"citation row {row} has an empty cell"))
            continue
        seen[row[0]] += 1
    ids = set(seen)
    found += [
        Finding("duplicate_citation", f"citation id {c} appears on {n} rows")
        for c, n in seen.items()
        if n > 1
    ]
    used = markers(_outside_citation_rows(h.body, table))
    found += [
        Finding("unresolved_citation", f"[{c}] has no citation row") for c in sorted(used - ids)
    ]
    found += [Finding("unused_citation", f"{c} is never cited") for c in sorted(ids - used)]
    return found


def check(text: str, contract: Contract, rules: Rules) -> tuple[int, list[Finding]]:
    try:
        h = parse(text)
    except HandoffError as exc:
        return EXIT_MALFORMED, [Finding("not_a_handoff", str(exc))]
    findings = _front_matter(h, contract, rules) + _sections(h, rules) + _tags(h, contract)
    size = len(text.encode("utf-8"))
    if size > MAX_HANDOFF_BYTES:
        findings.append(Finding("too_large", f"{size} bytes; the cap is {MAX_HANDOFF_BYTES}"))
    for spec in contract.tables:
        findings += _table(spec, h, rules)
    findings += _citations(h, rules)
    if any(f.code == "identity" for f in findings):
        return EXIT_IDENTITY, findings
    if findings:
        return EXIT_MALFORMED, findings
    if h.front_matter.get("qa_status") == "Blocked":
        return EXIT_BLOCKED, findings
    return EXIT_VALID, findings
