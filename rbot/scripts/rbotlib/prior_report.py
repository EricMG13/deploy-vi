"""Read exactly one original Report payload as inert data; no paths or external I/O."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from math import isfinite
from typing import Any

from rbotlib.inventory import RunError

Record = dict[str, Any]
GAPS = ("", "—")

KEYS = {
    **dict.fromkeys(
        (
            "snapshot." + n
            for n in (
                "run_header company_profile credit_view business_description "
                "historical_performance thesis"
            ).split()
        ),
        (),
    ),
    **dict.fromkeys(
        (
            "snapshot." + n
            for n in "instrument_recommendation instrument_levels capital_structure".split()
        ),
        ("facility_id",),
    ),
    **dict.fromkeys(
        ("snapshot." + n for n in "capital_structure_totals ebitda_adjustments".split()), ("line",)
    ),
    **dict.fromkeys(("snapshot.financials", "model.summary"), ("line_id",)),
    "snapshot.recommendation": ("strategy",),
    "cp3.talk_valuation": ("facility_id",),
    "snapshot.financial_columns": ("slot",),
    "snapshot.strengths_weaknesses": ("kind", "label"),
    "snapshot.catalysts": ("event",),
    "snapshot.portfolio_fit": ("portfolio_id", "facility_id"),
    "snapshot.transaction_summary": ("tranche_id",),
    "snapshot.relative_value": ("block", "name"),
    "cp6.portfolio_recommendation": ("portfolio_id", "strategy", "instrument"),
    "model.house": ("item",),
    "model.metrics": ("metric_id",),
    "model.maturity_wall": ("fiscal_year", "facility_id"),
    "model.projection_summary": ("case", "fiscal_year"),
    "cp2.watch_items": ("trigger",),
    "cp4.covenant_tests": ("test",),
    "cp2h.rating_triggers": ("agency", "metric"),
}


class _Payloads(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.payloads: list[str] = []
        self.active = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if ("id", "rbot-run") not in attrs:
            return
        if tag != "script" or dict(attrs).get("type") != "application/json":
            raise RunError("Report rbot-run: expected application/json script")
        if len(dict(attrs)) != len(attrs):
            raise RunError("Report rbot-run: duplicate attributes")
        self.payloads.append("")
        self.active = True

    def handle_data(self, data: str) -> None:
        if self.active:
            self.payloads[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.active = False


def _pairs(pairs: list[tuple[str, Any]]) -> Record:
    result: Record = {}
    for key, value in pairs:
        if key in result:
            raise RunError(f"Report: duplicate JSON key {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise RunError(f"Report: nonfinite JSON number {value}")


def _object(value: object, label: str) -> Record:
    if not isinstance(value, dict):
        raise RunError(f"Report {label}: expected object")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or value.strip() in GAPS:
        raise RunError(f"Report {label}: expected nonempty string")
    return value


def rows(table: Record, label: str) -> list[dict[str, str]]:
    """Validate the actual embedded Handoff table shape without coercing cells."""
    columns, values = table.get("columns"), table.get("rows")
    if not isinstance(columns, list) or not columns:
        raise RunError(f"Report {label}: missing columns")
    for column in columns:
        _text(column, f"{label} column")
    if len(set(columns)) != len(columns) or not isinstance(values, list):
        raise RunError(f"Report {label}: duplicate columns or invalid rows")
    result = []
    for row in values:
        if not isinstance(row, list) or len(row) != len(columns):
            raise RunError(f"Report {label}: row width differs from columns")
        if not all(isinstance(cell, str) for cell in row):
            raise RunError(f"Report {label}: cells must be strings")
        result.append(dict(zip(columns, row, strict=True)))
    return result


class ComparisonKeyError(RunError):
    """The preserved table has no unambiguous canonical comparison identity."""


def keyed_rows(name: str, table: Record) -> dict[str, dict[str, str]]:
    keys = KEYS[name]
    if not set(keys).issubset(table["columns"]):
        raise ComparisonKeyError(f"Report {name}: missing comparison key columns {keys}")
    result = {}
    for row in rows(table, name):
        if any(row.get(k, "").strip() in GAPS for k in keys):
            raise ComparisonKeyError(f"Report {name}: blank/gap comparison key {keys}")
        key = json.dumps({k: row[k] for k in keys}, sort_keys=True, ensure_ascii=False)
        if key in result:
            raise ComparisonKeyError(f"Report {name}: duplicate comparison key {key}")
        result[key] = row
    return result


def _comparability(name: str, table: Record) -> list[str]:
    if name in KEYS:
        try:
            keyed_rows(name, table)
        except ComparisonKeyError as exc:
            return [f"table {name} not comparable: {exc}"]
    return []


def _pending_cp0(entry: Record, meta: Record, brief: Record, step: Record) -> bool:
    pending = entry["front_matter"].get("run_id")
    # Approval/state preserve this pending name, including unknown issuer slugs.
    match = (
        re.fullmatch(r"(\d{8})-.+-pending(?:-\d+)?", pending) if isinstance(pending, str) else None
    )
    if match is None or not meta["run_id"].startswith(match[1] + "-"):
        return False
    try:
        date.fromisoformat(match[1])
    except ValueError:
        return False
    digests = [entry.get("sha256"), step.get("sha256"), brief["front_matter"].get("cp0_sha256")]
    return (
        all(isinstance(d, str) and re.fullmatch(r"[0-9a-f]{64}", d) for d in digests)
        and len(set(digests)) == 1
    )


def _identity(entry: Record, owner: str, meta: Record, brief: Record, steps: Record) -> bool:
    identity = _object(entry.get("front_matter"), f"{owner} front_matter")
    if "module_id" in identity and identity["module_id"] != owner:
        raise RunError(f"Report {owner}: conflicting module_id")
    if identity.get("issuer_id") != meta["issuer_id"]:
        raise RunError(f"Report {owner}: conflicting issuer_id")
    if identity.get("run_id") == meta["run_id"]:
        return False
    if (
        owner == "CP-0"
        and identity.get("module_id") == "CP-0"
        and _pending_cp0(entry, meta, brief, _object(steps.get(owner), f"{owner} step"))
    ):
        return True
    raise RunError(f"Report {owner}: conflicting run_id")


def _tables(
    brief: Record, handoffs: Record, meta: Record, steps: Record
) -> tuple[Record, list[str]]:
    tables: Record = {}
    limitations: list[str] = []
    if "RUN_BRIEF" in handoffs:
        raise RunError("Report handoffs: reserved RUN_BRIEF owner")
    entries = {"RUN_BRIEF": brief, **handoffs}
    for owner, raw in entries.items():
        entry = _object(raw, owner)
        if _identity(entry, owner, meta, brief, steps):
            limitations.append(
                "CP-0 original state/origin lineage cannot be independently "
                "reconstructed from Report"
            )
        for name, value in _object(entry.get("tables"), f"{owner} tables").items():
            rows(_object(value, name), name)
            if name == "citations":
                continue  # Source-local provenance stays under its original owner.
            if name in tables:
                raise RunError(f"Report {name}: duplicate table ownership")
            limitations += _comparability(name, value)
            tables[name] = {**value, "owner": owner}
    return tables, limitations


def _report_date(meta: Record, tables: Record, timestamp: datetime) -> None:
    header = rows(tables.get("snapshot.run_header", {}), "snapshot.run_header")
    if len(header) != 1:
        raise RunError("Report snapshot.run_header: expected one row")
    for key in ("run_id", "issuer_id", "pathway", "depth"):
        if (key in ("run_id", "issuer_id") or key in header[0]) and header[0].get(key) != meta[key]:
            raise RunError(f"Report snapshot.run_header: conflicting {key}")
    report_date = header[0].get("report_date", "—")
    meta["date_basis"] = "report_date" if report_date not in GAPS else "generated_at"
    meta["report_date"] = report_date if report_date not in GAPS else timestamp.date().isoformat()
    iso_date(meta["report_date"])


def inspect_report(doc: Record) -> tuple[Record, Record, list[str]]:
    """Validate detached documents too; return metadata, unique tables and omissions."""
    if doc.get("schema") != "rbot-run/1":
        raise RunError("Report schema: expected rbot-run/1")
    meta = {k: _text(doc.get(k), k) for k in ("run_id", "pathway", "depth")}
    try:
        timestamp = datetime.fromisoformat(_text(doc.get("generated_at"), "generated_at"))
    except ValueError as exc:
        raise RunError("Report generated_at: expected ISO timestamp") from exc
    if timestamp.utcoffset() is None:
        raise RunError("Report generated_at: timezone missing")
    brief = _object(doc.get("run_brief"), "run_brief")
    front = _object(brief.get("front_matter"), "run_brief front_matter")
    meta["issuer_id"] = _text(front.get("issuer_id"), "issuer_id")
    handoffs = _object(doc.get("handoffs"), "handoffs")
    steps = _object(doc.get("steps"), "steps")
    tables, limitations = _tables(brief, handoffs, meta, steps)
    _report_date(meta, tables, timestamp)
    for owner, entry in handoffs.items():
        step = _object(steps.get(owner), f"{owner} step")
        if entry.get("status") != step.get("status"):
            raise RunError(f"Report {owner}: conflicting status")
    limitations += [f"older Report omits {k}" for k in ("modules", "fetched") if k not in doc]
    return meta, tables, limitations


def iso_date(value: str) -> str:
    try:
        parsed = date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise RunError(f"Report: invalid ISO date {value}") from exc
    if parsed != value:
        raise RunError(f"Report: noncanonical ISO date {value}")
    return value


def _finite(value: str) -> float:
    number = float(value)
    if not isfinite(number):
        raise RunError("Report: nonfinite JSON number")
    return number


def _markdown(text: str) -> list[str]:
    payloads, fence, tagged = [], "", False
    for line in text.split("\n"):
        mark = re.fullmatch(r" {0,3}(`{3,}|~{3,})([^\n]*)\n?", line)
        if not fence and mark:
            fence, tagged = mark[1], mark[2].strip() == "json rbot-run"
            if tagged:
                payloads.append("")
        elif (
            fence
            and mark
            and mark[1][0] == fence[0]
            and len(mark[1]) >= len(fence)
            and not mark[2].strip()
        ):
            fence, tagged = "", False
        elif tagged:
            payloads[-1] += line + "\n"
    if tagged:
        raise RunError("Report rbot-run: unterminated fence")
    return payloads


def parse_report(text: str, kind: str) -> Record:
    """Parse HTML or generated Markdown and refuse malformed or ambiguous payloads."""
    if kind == "html":
        parser = _Payloads()
        parser.feed(text)
        parser.close()
        payloads = parser.payloads
        if parser.active:
            raise RunError("Report rbot-run: unterminated script")
    elif kind in ("md", "markdown"):
        payloads = _markdown(text)
    else:
        raise RunError(f"Report kind: unsupported {kind}")
    if len(payloads) != 1:
        raise RunError("Report: expected exactly one rbot-run payload")
    try:
        doc = _object(
            json.loads(
                payloads[0], object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_finite
            ),
            "payload",
        )
    except (ValueError, RecursionError) as exc:
        raise RunError(f"Report payload: invalid JSON ({exc})") from exc
    inspect_report(doc)
    return doc
