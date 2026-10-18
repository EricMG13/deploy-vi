"""Pure keyed comparison: preserve source strings and decline uncertain numeric context."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from rbotlib.inventory import RunError
from rbotlib.prior_report import (
    GAPS,
    KEYS,
    ComparisonKeyError,
    inspect_report,
    iso_date,
    keyed_rows,
    rows,
)

Record = dict[str, Any]
SLOTS = {"FY-2": "fy_2", "FY-1": "fy_1", "FY": "fy", "PYTD": "pytd", "YTD": "ytd", "LTM": "ltm"}
PLAIN = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")
UNITS = re.compile(r"(?:[A-Z]{3}(?: [km])?|x|%|bps|days|count)")
GOVERNED = {
    "snapshot.financials": {"latest"},
    "model.summary": {*SLOTS.values(), "pf_ltm"},
    "model.metrics": {*SLOTS.values(), "pf_ltm"},
    "model.house": {"value"},
    "snapshot.capital_structure": {
        "outstanding",
        "structuring_multiple_x",
        "ssim_multiple_x",
        "pct_ev_pct",
    },
    "snapshot.capital_structure_totals": {
        "amount",
        "structuring_multiple_x",
        "ssim_multiple_x",
        "pct_ev_pct",
    },
    "snapshot.ebitda_adjustments": {"amount"},
}


def _available(doc: Record, table: Record | None) -> bool:
    return table is not None and (
        table["owner"] == "RUN_BRIEF"
        or doc["steps"].get(table["owner"], {}).get("status") == "accepted"
    )


def _periods(doc: Record, tables: Record) -> list[Record]:
    name = "snapshot.financial_columns"
    if not _available(doc, tables.get(name)):
        return []
    try:
        keyed_rows(name, tables[name])
    except ComparisonKeyError:
        return []
    return rows(tables[name], name)


def _latest(candidates: list[Record]) -> Record:
    def rank(p: Record) -> tuple[str, int]:
        return p["end_date"], {"LTM": 3, "PF_LTM": 3, "YTD": 2, "FY": 1}.get(p.get("kind", ""), 0)

    if not candidates:
        return {}
    newest = max(map(rank, candidates))
    selected = [p for p in candidates if rank(p) == newest]
    return selected[0] if len(selected) == 1 else {}


def _matches(name: str, row: Record, field: str, p: Record) -> bool:
    if row.get("column_id") is not None:
        return bool(p["column_id"] == row["column_id"])
    if name in ("model.summary", "model.metrics"):
        slot = next((s for s, f in SLOTS.items() if f == field), "LTM")
        kind = "PF_LTM" if field == "pf_ltm" else "LTM" if field == "ltm" else None
        return bool(p["slot"] == slot and (kind is None or p.get("kind") == kind))
    basis = row.get("column_basis", row.get("basis", ""))
    return bool(
        basis in ("LTM", "PF-LTM", "PF_LTM")
        and p["slot"] == "LTM"
        and p.get("kind") == basis.replace("-", "_")
    )


def _period(name: str, row: Record, field: str, periods: list[Record]) -> Record:
    candidates = [
        p
        for p in periods
        if p.get("slot") in SLOTS
        and p.get("column_id", "—") not in GAPS
        and p.get("end_date", "—") not in GAPS
    ]
    for p in candidates:
        iso_date(p["end_date"])
    if name == "snapshot.financials" and field == "latest":
        return _latest(candidates)
    matched = [p for p in candidates if _matches(name, row, field, p)]
    return matched[0] if len(matched) == 1 else {}


def _context(name: str, row: Record, field: str, periods: list[Record]) -> Record:
    period = _period(name, row, field, periods)
    unit = row.get("unit_label", "")
    if row.get("currency") and row.get("unit") in ("UNITS", "THOUSANDS", "MILLIONS"):
        unit = row["currency"] + {"UNITS": "", "THOUSANDS": " k", "MILLIONS": " m"}[row["unit"]]
    if field.endswith("_x"):
        unit = "x"
    elif field.endswith("_pct"):
        unit = "%"
    return {
        **period,
        "unit": unit,
        "basis": row.get("column_basis", row.get("basis", period.get("kind"))),
        "gap_reason": row.get("reason") if row.get("reason") not in GAPS else None,
    }


def _numeric(a: str | None, b: str | None, contexts: Record, governed: bool) -> str | None:
    if not governed:
        return "not a governed metric field"
    if a is None or b is None or not PLAIN.fullmatch(a) or not PLAIN.fullmatch(b):
        return "missing, gap or non-plain decimal"
    if not Decimal(a).is_finite() or not Decimal(b).is_finite():
        return "nonfinite decimal"
    x, y = contexts["prior"], contexts["current"]
    if not UNITS.fullmatch(x["unit"]) or x["unit"] != y["unit"]:
        return "unknown or mismatched currency/unit"
    if x.get("kind") not in ("FY", "PYTD", "YTD", "LTM", "PF_LTM"):
        return "unknown period kind"
    if any(
        x.get(k) in (None, *GAPS) or x.get(k) != y.get(k)
        for k in ("period_id", "end_date", "kind", "basis")
    ):
        return "missing or mismatched period/basis"
    return None


def _value(name: str, field: str, row: Record, context: Record) -> str | None:
    if name == "snapshot.financials" and field == "latest":
        value: str | None = row.get(SLOTS.get(context.get("slot", ""), ""))
        return value
    return row.get(field)


def _change(
    name: str,
    key: str,
    field: str,
    pair: tuple[Record, Record],
    periods: tuple[list[Record], list[Record]],
) -> Record:
    a, b = pair
    contexts = {
        side: _context(name, row, field, ps)
        for side, row, ps in zip(("prior", "current"), pair, periods, strict=True)
    }
    values = tuple(
        _value(name, field, row, contexts[side])
        for side, row in zip(("prior", "current"), pair, strict=True)
    )
    av, bv = values
    for side, value in zip(("prior", "current"), values, strict=True):
        if value is None or value in GAPS:
            contexts[side]["gap_reason"] = contexts[side]["gap_reason"] or (
                "missing selected value/context" if value is None else "source gap"
            )
    reason = _numeric(av, bv, contexts, field in GOVERNED.get(name, set()))
    return {
        "table": name,
        "key": json.loads(key),
        "field": field,
        "prior": av,
        "current": bv,
        "kind": "added"
        if not a
        else "removed"
        if not b
        else "unchanged"
        if av == bv
        else "changed",
        "numeric": reason is None,
        "context": contexts,
        "reason": reason,
    }


def _changes(
    name: str, before: Record, after: Record, periods: tuple[list[Record], list[Record]]
) -> list[Record]:
    out: list[Record] = []
    for key in sorted(before.keys() | after.keys()):
        pair = before.get(key, {}), after.get(key, {})
        fields = (pair[0].keys() | pair[1].keys()) - set(KEYS[name])
        if name == "snapshot.financials":
            fields = (fields - set(SLOTS.values())) | {"latest"}
        out.extend(_change(name, key, field, pair, periods) for field in sorted(fields))
    return out


def compare(prior: Record, current: Record, table_ids: Sequence[str]) -> Record:
    """Compare authoritative tables; unavailable or ambiguous rows never prove deletion."""
    pm, pt, pl = inspect_report(prior)
    cm, ct, cl = inspect_report(current)
    if pm["issuer_id"] != cm["issuer_id"]:
        raise RunError("Report issuer_id: prior and current differ")
    limitations = [f"{side}: {v}" for side, vs in (("prior", pl), ("current", cl)) for v in vs]
    changes = []
    periods = _periods(prior, pt), _periods(current, ct)
    for name in sorted(set(table_ids)):
        if name.startswith("cp8."):
            continue
        if name not in KEYS:
            raise RunError(f"Report {name}: unknown comparison key")
        if not _available(prior, pt.get(name)) or not _available(current, ct.get(name)):
            limitations.append(f"{name}: prior/current table missing or owner not accepted")
            continue
        try:
            before, after = keyed_rows(name, pt[name]), keyed_rows(name, ct[name])
        except ComparisonKeyError as exc:
            limitations.append(f"{name}: comparison declined: {exc}")
            continue
        changes.extend(_changes(name, before, after, periods))
    return {
        "prior": {k: pm[k] for k in ("run_id", "report_date", "pathway", "depth")},
        "date_basis": {"prior": pm["date_basis"], "current": cm["date_basis"]},
        "changes": changes,
        "limitations": limitations,
    }
