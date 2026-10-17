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
from rbotlib.inventory import RunError, output_path
from rbotlib.rules import Rules
from rbotlib.validate import Finding

CONSUMERS = ("CP-2", "CP-3", "CP-6")
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
    missing = sorted(set(("field", "tranche_id", "value", "status", "cite")) - row.keys())
    if missing:
        return [Finding("prefill_invalid", f"cp0.run_brief_prefill: missing {missing}")]
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
    found: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for row in _records(h.tables.get("cp0.run_brief_prefill")):
        found += _row(row, rules)
        if not all(k in row for k in ("tranche_id", "field")):
            continue
        tranche_id = row["tranche_id"]
        key = ("" if tranche_id == "—" else tranche_id, row["field"])
        if key in seen:
            found.append(Finding("prefill_invalid", f"cp0.run_brief_prefill: duplicate {key}"))
        seen.add(key)
    questions = _records(h.tables.get("cp0.research_questions"))
    if len(questions) > MAX_QUESTIONS:
        message = f"{len(questions)} questions; MODULE.md allows at most {MAX_QUESTIONS}"
        found.append(Finding("research_questions", message))
    allowed = ", ".join(CONSUMERS[:-1]) + f" or {CONSUMERS[-1]}"
    for q in (q for q in questions if q.get("consumer_module") not in CONSUMERS):
        message = f"consumer_module {q.get('consumer_module')!r} is not {allowed}"
        found.append(Finding("research_questions", f"{q.get('question_id')}: {message}"))
    return found


class _RunInputError(ValueError):
    """A CP-0 run input cannot support verification; the message names its path."""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _RunInputError(f"{path}: {exc}") from exc


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise _RunInputError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise _RunInputError(f"{path}: expected a JSON object")
    return data


def _objects(
    path: Path, data: dict[str, Any], key: str, fields: tuple[str, ...]
) -> list[dict[str, Any]]:
    rows = data.get(key)
    if not isinstance(rows, list) or any(
        not isinstance(row, dict) or not all(f in row for f in fields) for row in rows
    ):
        raise _RunInputError(f"{path}: {key} must list objects with {fields}")
    return rows


def _strings(path: Path, row: dict[str, Any], fields: tuple[str, ...]) -> None:
    if any(not isinstance(row.get(f), str) for f in fields):
        raise _RunInputError(f"{path}: expected string fields {fields}")


def _keyed(path: Path, rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    records = {}
    for row in rows:
        _strings(path, row, (key,))
        name = row[key]
        if not name or name in records:
            raise _RunInputError(f"{path}: empty or duplicate {key} {name!r}")
        records[name] = row
    return records


def _run_path(run: Path, relative: str) -> Path:
    try:
        return output_path(run, relative)
    except (RunError, OSError, ValueError) as exc:
        raise _RunInputError(f"{run / relative}: {exc}") from exc


def _prepared_records(path: Path, index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    keys = ("path", "sha256", "pages", "image_read", "unreadable", "prepared")
    records = _keyed(path, _objects(path, index, "files", keys), "path")
    for name, row in records.items():
        _strings(path, row, ("sha256",))
        good = type(row["pages"]) is int and row["pages"] >= 0
        good = good and isinstance(row["image_read"], bool)
        good = good and isinstance(row["unreadable"], (str, type(None)))
        good = good and isinstance(row["prepared"], (str, type(None)))
        if not good:
            raise _RunInputError(f"{path}: {name}: invalid preparation metadata")
    return records


def empty_text(run: Path, record: dict[str, Any]) -> bool:
    if not record.get("prepared"):
        return True
    text = _read(_run_path(run, str(record["prepared"])))
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
    path = run / "inventory.json"
    inventory = _load(path)
    entries = _objects(path, inventory, "files", ("path",))
    listed = set(_keyed(path, entries, "path"))
    records = _prepared_records(run / "prepared/index.json", index)
    missing = sorted(listed - set(records))
    if missing:
        raise _RunInputError(f"{run / 'prepared/index.json'}: no prepared record for {missing}")
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
    reports = {f["path"] for f in entries if f.get("rbot_report")}
    found += [
        Finding(
            "prior_case_mismatch", f"{r.get('file')} is not flagged rbot_report in inventory.json"
        )
        for r in _records(h.tables.get("cp0.prior_case"))
        if r.get("file") not in reports
    ]
    return found


PORTFOLIO_FIELDS = {
    "portfolio_name": "portfolio_name",
    "strategy": "strategy",
    "positions_file": "positions_file",
    "limits_file": "limits_file",
    "as_of_date": "as_of",
}


def _portfolio_row(portfolio_id: str, row: dict[str, str], data: dict[str, Any]) -> list[Finding]:
    found = []
    for field, source in PORTFOLIO_FIELDS.items():
        value = "" if row.get(field) == "—" else row.get(field, "")
        if value != data[source]:
            found.append(
                Finding("portfolio_mismatch", f"{portfolio_id}: {field} differs from prepared JSON")
            )
    return found


def _portfolios(h: Handoff, run: Path, index: dict[str, Any]) -> list[Finding]:
    path = run / "prepared/index.json"
    records = _keyed(
        path, _objects(path, index, "portfolios", ("portfolio_id", "json")), "portfolio_id"
    )
    rows = _records(h.tables.get("cp0.portfolios"))
    claimed = {r.get("portfolio_id", "") for r in rows}
    found = [
        Finding(
            "portfolio_mismatch",
            f"{p} is in cp0.portfolios but rbot prepare found no such portfolio",
        )
        for p in sorted(claimed - records.keys())
    ]
    found += [
        Finding("portfolio_mismatch", f"{p} was found by rbot prepare but is not in cp0.portfolios")
        for p in sorted(records.keys() - claimed)
    ]
    for portfolio_id, record in records.items():
        _strings(path, record, ("json",))
        data = _load(_run_path(run, record["json"]))
        _strings(run / record["json"], data, ("portfolio_id", *PORTFOLIO_FIELDS.values()))
        if data["portfolio_id"] != portfolio_id:
            raise _RunInputError(f"{run / record['json']}: portfolio_id differs from index")
        for row in (r for r in rows if r.get("portfolio_id") == portfolio_id):
            found += _portfolio_row(portfolio_id, row, data)
    return found


def run_findings(h: Handoff, run: Path) -> list[Finding]:
    """Verify run claims, or name expected input/read/shape failures as run_error."""
    try:
        index = _load(run / "prepared/index.json")
        return _inventory(h, run, index) + _portfolios(h, run, index)
    except _RunInputError as exc:
        return [Finding("run_error", str(exc))]


def findings(h: Handoff, rules: Rules, run: Path | None) -> list[Finding]:
    return prefill_findings(h, rules) + (run_findings(h, run) if run is not None else [])
