"""Portfolio Context to `prepared/portfolios/<portfolio_id>.json` (interfaces spec section 7).

A sheet (CSV or workbook tab) is a positions table when its header row names Issuer ID,
Issuer, Par and % NAV, and a limits table when it names the compliance-monitor columns
ID, Constraint Category, Parameter, Limit, Breach Type and Current Value. Key-value
rows above the header give the portfolio: Portfolio ID (required to link the two),
Portfolio, Strategy, As of, Currency, Unit, Total NAV and Total Par. Amounts keep the
file's unit. Rows RBOT cannot use are kept under `unparsed` with the reason, never dropped.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from rbotlib.rules import Rules

SCHEMA = "rbot-portfolio/1"
POSITIONS = ("issuer id", "issuer", "par", "% nav")
LIMITS = ("id", "constraint category", "parameter", "limit", "breach type", "current value")
META = {
    "portfolio id": "portfolio_id",
    "portfolio": "portfolio_name",
    "strategy": "strategy",
    "as of": "as_of",
    "currency": "currency",
    "unit": "unit",
    "total nav": "nav",
    "total par": "par",
}
POSITION_COLUMNS = {
    "issuer id": "issuer_id",
    "issuer": "issuer_name",
    "instrument id": "instrument_id",
    "par": "par",
    "% nav": "pct_nav",
    "sector": "sector",
    "rating": "rating",
    "country": "country",
    "currency": "currency",
    "seniority": "seniority",
    "asset type": "asset_type",
}
_LIMIT = re.compile(
    r"^(?P<op>≤|<=|<|≥|>=|>)?\s*(?P<cur>\$)?(?P<num>\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>%\s*nav|%\s*par|years?|yrs?)?$",
    re.I,
)


@dataclass
class Portfolio:
    meta: dict[str, str] = field(default_factory=dict)
    positions: list[dict[str, str]] = field(default_factory=list)
    limits: list[dict[str, Any]] = field(default_factory=list)
    unparsed: list[dict[str, str]] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)


def _norm(cell: str) -> str:
    return " ".join(cell.casefold().split())


def number(text: str) -> str | None:
    """A plain decimal from `$630,928,502`, `2.37%`, `4.82 yrs` or `313 bps`; else None."""
    match = re.match(r"^\$?(-?\d[\d,]*(?:\.\d+)?)\s*(%|yrs?|years?|bps)?$", text.strip(), re.I)
    if not match:
        return None
    try:
        return str(Decimal(match.group(1).replace(",", "")))
    except InvalidOperation:
        return None


def parse_limit(text: str) -> tuple[str, str] | str:
    """(`limit_value`, `unit`) for a maximum limit, or the reason it cannot be sized against."""
    match = _LIMIT.match(text.strip())
    if not match:
        return f"limit {text!r} is not a number with a unit"
    if match["op"] in ("≥", ">=", ">"):
        return "minimum limit: Portfolio Fit sizes against maximum limits only"
    unit = _norm(match["unit"] or "").replace(" ", "")
    units = {"%nav": "pct_nav", "%par": "pct_par", "year": "years", "years": "years"}
    kind = units.get(unit) or ("years" if unit.startswith("yr") else None)
    kind = kind or ("amount" if match["cur"] else "count")
    return str(Decimal(match["num"].replace(",", ""))), kind


def _scope(category: str, parameter: str) -> tuple[str, str | None]:
    c = _norm(category)
    named = re.search(r"(?:\(largest:[^)]*\)|sector:\s*(?P<s>.+)|\((?P<x>[^)]*)\))", parameter)
    if c in ("single name", "issuer"):
        return "issuer", None
    if c.startswith("rating"):
        bucket = category.split("—")[-1].strip()
        return "rating_bucket", "CCC" if "ccc" in bucket.casefold() else bucket
    if c.startswith("sector") or "exclusion" in c:
        value = named and (named["s"] or named["x"])
        return "sector", value.strip() if value else None
    if c.startswith("instrument"):
        return "seniority", re.sub(r"^(max|min)\s+", "", parameter, flags=re.I).strip()
    for scope in ("country", "currency", "asset_type", "seniority"):
        if c == scope.replace("_", " "):
            return scope, None
    return "other", None


def _header(rows: list[list[str]], required: tuple[str, ...]) -> int | None:
    for i, row in enumerate(rows):
        if set(required) <= {_norm(c) for c in row}:
            return i
    return None


def _meta(rows: list[list[str]]) -> dict[str, str]:
    found = {}
    for row in rows:
        cells = [c for c in row if c]
        if len(cells) == 2 and _norm(cells[0]) in META:
            found[META[_norm(cells[0])]] = cells[1]
    return found


def _positions(source: str, rows: list[list[str]], start: int, p: Portfolio) -> None:
    columns = [POSITION_COLUMNS.get(_norm(c)) for c in rows[start]]
    for n, row in enumerate(rows[start + 1 :], start + 2):
        if not any(row):
            continue
        item = {key: cell for key, cell in zip(columns, row, strict=False) if key}
        par, pct = number(item.get("par", "")), number(item.get("pct_nav", ""))
        if par is None or pct is None:
            p.unparsed.append(
                {"row": f"{source} row {n}", "reason": "par or % NAV is not a number"}
            )
            continue
        p.positions.append(item | {"par": par, "pct_nav": pct})


def _limit_row(source: str, n: int, item: dict[str, str]) -> dict[str, Any] | str:
    kind = item.get("breach type", "")
    if kind not in ("Hard", "Soft"):
        return "no Hard or Soft breach type (info only)"
    parsed = parse_limit(item.get("limit", ""))
    if isinstance(parsed, str):
        return parsed
    current = number(item.get("current value", ""))
    if current is None:
        return f"current value {item.get('current value', '')!r} is not a number"
    scope, scope_value = _scope(item.get("constraint category", ""), item.get("parameter", ""))
    return {
        "limit_id": item.get("id", ""),
        "category": item.get("constraint category", ""),
        "parameter": item.get("parameter", ""),
        "scope": scope,
        "scope_value": scope_value,
        "limit_value": parsed[0],
        "unit": parsed[1],
        "limit_kind": kind,
        "current_value": current,
        "source": f"{source} row {n}",
    }


def _limits(source: str, rows: list[list[str]], start: int, p: Portfolio) -> None:
    header = [_norm(c) for c in rows[start]]
    for n, row in enumerate(rows[start + 1 :], start + 2):
        if not any(row):
            continue
        result = _limit_row(source, n, dict(zip(header, row, strict=False)))
        if isinstance(result, str):
            p.unparsed.append({"row": f"{source} row {n}", "reason": result})
        else:
            p.limits.append(result)


def read_sheet(source: str, rows: list[list[str]], found: dict[str, Portfolio]) -> str | None:
    """Add a positions or limits sheet to its portfolio; a note when it cannot be linked."""
    for kind, required in (("positions", POSITIONS), ("limits", LIMITS)):
        start = _header(rows, required)
        if start is None:
            continue
        meta = _meta(rows[:start])
        portfolio_id = meta.get("portfolio_id")
        if not portfolio_id:
            return f"{source}: {kind} table without a Portfolio ID row; not linked"
        p = found.setdefault(portfolio_id, Portfolio())
        p.meta.update(meta)
        p.files[kind] = source
        (_positions if kind == "positions" else _limits)(source, rows, start, p)
    return None


def to_json(p: Portfolio, rules: Rules) -> dict[str, Any]:
    meta, unparsed = dict(p.meta), list(p.unparsed)
    for key in ("nav", "par"):
        value = number(meta.get(key, ""))
        if value is None:
            unparsed.append({"row": f"Total {key.upper()}", "reason": "missing or not a number"})
        meta[key] = value or ""
    if meta.get("strategy") not in rules.scales["strategy"]:
        unparsed.append(
            {"row": "Strategy", "reason": f"{meta.get('strategy')!r} is not a Strategy"}
        )
    data: dict[str, Any] = {"schema": SCHEMA}
    for key in ("portfolio_id", "portfolio_name", "strategy", "as_of", "nav", "par"):
        data[key] = meta.get(key, "")
    data |= {"currency": meta.get("currency", ""), "unit": meta.get("unit", "")}
    data["positions_file"] = p.files.get("positions", "")
    data["limits_file"] = p.files.get("limits", "")
    return data | {"positions": p.positions, "limits": p.limits, "unparsed": unparsed}


def write_all(run: Path, found: dict[str, Portfolio], rules: Rules) -> list[dict[str, str]]:
    folder = run / "prepared" / "portfolios"
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for portfolio_id in sorted(found):
        data = to_json(found[portfolio_id], rules)
        name = f"prepared/portfolios/{portfolio_id}.json"
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        (run / name).write_text(text, encoding="utf-8")
        written.append({"portfolio_id": portfolio_id, "json": name})
    return written
