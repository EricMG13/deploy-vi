"""Checks on a CP-0 Handoff that its tables alone cannot express (`rbot validate`).

Every rule CP-0's MODULE.md states for the Run Brief pre-fill and the research questions
is checked here, with the same normalisers `rbot brief` applies to an analyst's edit, so
the prompt and the checker agree. With a run folder, every claim CP-0 makes about the
run's own files is compared with `inventory.json` and `prepared/index.json`: the file
list, sha256, pages, the readable and Image-Read flags, the portfolios and the earlier
Reports. A mismatch is a finding (exit 2), so `rbot accept` re-dispatches CP-0 with it
and `rbot grade` never grades on a claim the run disproves.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from rbotlib.brief import ASSERTED, FIELDS, GAP, SOURCED, TRANCHE, BriefError, prefill_value
from rbotlib.handoff import Handoff, Table, markers
from rbotlib.rules import Rules
from rbotlib.validate import Finding

CONSUMERS = ("CP-1A", "CP-1B", "CP-2")
MAX_QUESTIONS = 5
_PAGE_LINE = re.compile(r"^<<< (page \d+|sheet .*) >>>$", re.M)


def _records(table: Table | None) -> list[dict[str, str]]:
    if table is None:
        return []
    return [dict(zip(table.columns, row, strict=False)) for row in table.rows]


def _status(row: dict[str, str], where: str) -> Finding | None:
    status, value, cite = row.get("status", ""), row.get("value", ""), row.get("cite", "")
    if status == SOURCED and not markers(cite):
        return Finding("prefill_status", f"{where}: Sourced without a citation")
    if status == ASSERTED and markers(cite):
        return Finding("prefill_status", f"{where}: Analyst-asserted with a citation")
    if status == GAP and value:
        return Finding("prefill_status", f"{where}: Gap with a value")
    return None


def _row(row: dict[str, str], rules: Rules) -> list[Finding]:
    cells = {k: ("" if v == "—" else v) for k, v in row.items()}
    name, tranche_id = cells.get("field", ""), cells.get("tranche_id", "")
    if tranche_id and name not in TRANCHE:
        message = f"cp0.run_brief_prefill: {name!r} is not a tranche field"
        return [Finding("prefill_invalid", message)]
    if not tranche_id and name not in FIELDS:
        return [Finding("prefill_invalid", f"cp0.run_brief_prefill: unknown field {name!r}")]
    try:
        prefill_value(cells, rules)
    except BriefError as exc:
        return [Finding("prefill_invalid", str(exc))]
    where = " ".join(p for p in ("cp0.run_brief_prefill", tranche_id, name) if p)
    status = _status(cells, where)
    return [status] if status else []


def prefill_findings(h: Handoff, rules: Rules) -> list[Finding]:
    """The pre-fill and research-question rules MODULE.md states, row by row."""
    found = [f for row in _records(h.tables.get("cp0.run_brief_prefill")) for f in _row(row, rules)]
    questions = _records(h.tables.get("cp0.research_questions"))
    if len(questions) > MAX_QUESTIONS:
        message = f"{len(questions)} questions; MODULE.md allows at most {MAX_QUESTIONS}"
        found.append(Finding("research_questions", message))
    allowed = ", ".join(CONSUMERS[:-1]) + f" or {CONSUMERS[-1]}"
    for q in (q for q in questions if q.get("consumer_module") not in CONSUMERS):
        message = f"consumer_module {q.get('consumer_module')!r} is not {allowed}"
        found.append(Finding("research_questions", f"{q.get('question_id')}: {message}"))
    return found


def empty_text(run: Path, record: dict[str, Any]) -> bool:
    if not record.get("prepared"):
        return True
    text = (run / str(record["prepared"])).read_text(encoding="utf-8")
    return not _PAGE_LINE.sub("", text).strip()


def _readable(run: Path, name: str, row: dict[str, str], record: dict[str, Any]) -> list[Finding]:
    if record["unreadable"]:
        why = "prepared/index.json lists it unreadable"
    elif record["image_read"]:
        why = "it is Image-Read only"
    elif empty_text(run, record):
        why = "its prepared text is empty"
    else:
        why = ""
    if row.get("readable") == "Yes" and why:
        return [Finding("inventory_mismatch", f"{name}: readable Yes, but {why}")]
    if row.get("readable") == "No" and not why:
        return [Finding("inventory_mismatch", f"{name}: readable No, but its prepared text reads")]
    return []


def _file(run: Path, name: str, row: dict[str, str], record: dict[str, Any]) -> list[Finding]:
    found = []
    if row.get("sha256") != record["sha256"]:
        found.append(
            Finding("inventory_mismatch", f"{name}: sha256 differs from prepared/index.json")
        )
    if row.get("pages") != str(record["pages"]):
        message = f"{name}: pages {row.get('pages')}, prepared/index.json says {record['pages']}"
        found.append(Finding("inventory_mismatch", message))
    if (row.get("image_read") == "Yes") != bool(record["image_read"]):
        message = f"{name}: image_read {row.get('image_read')} differs from prepared/index.json"
        found.append(Finding("inventory_mismatch", message))
    return found + _readable(run, name, row, record)


def _inventory(h: Handoff, run: Path, index: dict[str, Any]) -> list[Finding]:
    inventory = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    listed = {f["path"] for f in inventory["files"]}
    records = {r["path"]: r for r in index["files"]}
    rows = {r.get("file", ""): r for r in _records(h.tables.get("cp0.source_inventory"))}
    found = [
        Finding("inventory_mismatch", f"{p} is in inventory.json but not in cp0.source_inventory")
        for p in sorted(listed - set(rows))
    ]
    found += [
        Finding("inventory_mismatch", f"{p} is in cp0.source_inventory but not in inventory.json")
        for p in sorted(set(rows) - listed)
    ]
    for name in sorted(set(rows) & listed & set(records)):
        found += _file(run, name, rows[name], records[name])
    reports = {f["path"] for f in inventory["files"] if f.get("rbot_report")}
    found += [
        Finding(
            "prior_case_mismatch", f"{r.get('file')} is not flagged rbot_report in inventory.json"
        )
        for r in _records(h.tables.get("cp0.prior_case"))
        if r.get("file") not in reports
    ]
    return found


def run_findings(h: Handoff, run: Path) -> list[Finding]:
    """Every claim CP-0 makes about the run's files, against inventory.json and the index."""
    index = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
    found = _inventory(h, run, index)
    prepared = {p["portfolio_id"] for p in index["portfolios"]}
    claimed = {r.get("portfolio_id", "") for r in _records(h.tables.get("cp0.portfolios"))}
    found += [
        Finding(
            "portfolio_mismatch",
            f"{p} is in cp0.portfolios but rbot prepare found no such portfolio",
        )
        for p in sorted(claimed - prepared)
    ]
    found += [
        Finding("portfolio_mismatch", f"{p} was found by rbot prepare but is not in cp0.portfolios")
        for p in sorted(prepared - claimed)
    ]
    return found


def findings(h: Handoff, rules: Rules, run: Path | None) -> list[Finding]:
    return prefill_findings(h, rules) + (run_findings(h, run) if run is not None else [])
