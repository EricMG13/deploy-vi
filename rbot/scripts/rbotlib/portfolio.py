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
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from rbotlib.inventory import write_atomic
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


_COUNT = re.compile(
    r"\b(count|number of|no\. of|issuers|obligors|names|positions|holdings)\b", re.I
)
_SCALED = frozenset({"thousands", "millions", "billions", "000s", "k", "m", "mm", "bn"})
_EXPECTED = {"pct_nav": "%", "pct_par": "%", "years": "years", "amount": "", "count": ""}
_DATES = ("%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y")
_NUMBER = re.compile(r"^\$?(-?\d[\d,]*(?:\.\d+)?)\s*(%|yrs?|years?|bps)?$", re.I)


@dataclass
class Table:
    """One positions or limits table: where it came from and what its sheet says about it."""

    source: str
    rows: list[list[str]]
    start: int
    bad: dict[int, str]  # 1-based row -> a formula cell there with no stored value
    unit: str = ""


@dataclass
class Portfolio:
    meta: dict[str, str] = field(default_factory=dict)
    positions: list[dict[str, str]] = field(default_factory=list)
    limits: list[dict[str, Any]] = field(default_factory=list)
    unparsed: list[dict[str, str]] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


_SAFE_ID = re.compile(r"(?!\.)[A-Za-z0-9_.-]+")  # becomes a file name: no path parts
_RESERVED = re.compile(r"(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?", re.I)  # Windows devices
MAX_ID = 100


def _id_problem(portfolio_id: str, found: dict[str, Portfolio]) -> str | None:
    """Why an id cannot name `<id>.json` on every disk; None when it can."""
    if not _SAFE_ID.fullmatch(portfolio_id):
        return "not a file name"
    if _RESERVED.fullmatch(portfolio_id):
        return "reserved Windows device name"
    if len(portfolio_id) > MAX_ID:
        return f"longer than {MAX_ID} characters"
    folded = portfolio_id.casefold()
    twin = next((k for k in found if k != portfolio_id and k.casefold() == folded), None)
    return f"differs only in case from {twin!r}" if twin else None


def _norm(cell: str) -> str:
    return " ".join(cell.casefold().split())


def number(text: str) -> tuple[str, str] | None:
    """(plain decimal, unit) from `$630,928,502`, `2.37%`, `4.82 yrs` or `313 bps`; else None.

    The unit is `""`, `%`, `years` or `bps`. Nothing is scaled: `313 bps` is `("313", "bps")`.
    """
    match = _NUMBER.match(text.strip())
    if not match:
        return None
    try:
        value = format(Decimal(match.group(1).replace(",", "")), "f")
    except InvalidOperation:
        return None
    suffix = (match.group(2) or "").lower()
    return value, "years" if suffix.startswith("y") else suffix


def _unit_problem(label: str, text: str, kind: str, suffix: str) -> str | None:
    """Why a value with unit `suffix` cannot stand for `kind`; None when it can."""
    expected = _EXPECTED[kind]
    if suffix == expected:
        return None
    shown = {"": "a bare number", "%": "a percent", "years": "years", "bps": "bps"}[suffix]
    return f"{label} {text!r} is {shown} but the limit is {kind}; not converted"


def iso_date(text: str) -> str | None:
    """An unambiguous date as `yyyy-mm-dd`; None otherwise (`05/29/2026` is never guessed)."""
    for pattern in _DATES:
        try:
            return datetime.strptime(text.strip(), pattern).date().isoformat()
        except ValueError:
            continue
    return None


def parse_limit(text: str, parameter: str = "") -> tuple[str, str] | str:
    """(`limit_value`, `unit`) for a maximum limit, or the reason it cannot be sized against."""
    match = _LIMIT.match(text.strip())
    if not match:
        return f"limit {text!r} is not a number with a unit"
    if match["op"] in ("≥", ">=", ">"):
        return "minimum limit: Portfolio Fit sizes against maximum limits only"
    unit = _norm(match["unit"] or "").replace(" ", "")
    units = {"%nav": "pct_nav", "%par": "pct_par", "year": "years", "years": "years"}
    kind = units.get(unit) or ("years" if unit.startswith("yr") else None)
    if kind is None and not match["cur"]:
        if not _COUNT.search(parameter):
            return f"limit {text!r}: unit not recognised"
        kind = "count"
    return format(Decimal(match["num"].replace(",", "")), "f"), kind or "amount"


def _scope(category: str, parameter: str) -> tuple[str, str | None]:
    c = _norm(category)
    named = re.search(r"(?:\(largest:[^)]*\)|sector:\s*(?P<s>.+)|\((?P<x>[^)]*)\))", parameter)
    if c in ("single name", "issuer"):
        return "issuer", None
    if c.startswith("rating"):
        bucket = category.split("—")[-1].strip() if "—" in category else ""
        return "rating_bucket", ("CCC" if "ccc" in bucket.casefold() else bucket) or None
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


def _uncached(t: Table, n: int, p: Portfolio) -> bool:
    """True (and the row recorded as unparsed) when the row holds a formula with no stored value."""
    if n not in t.bad:
        return False
    reason = f"formula {t.bad[n]} has no stored value"
    p.unparsed.append({"row": f"{t.source} row {n}", "reason": reason})
    return True


def _position_values(item: dict[str, str]) -> tuple[str, str] | str:
    """(par, % NAV) as plain decimals, or why the row cannot be used."""
    par, pct = number(item.get("par", "")), number(item.get("pct_nav", ""))
    if par is None or pct is None:
        return "par or % NAV is not a number"
    if par[1] != "" or pct[1] != "%":
        return f"par {item['par']!r} must be a plain amount and % NAV {item['pct_nav']!r} a percent"
    return par[0], pct[0]


def _positions(t: Table, p: Portfolio) -> None:
    columns = [POSITION_COLUMNS.get(_norm(c)) for c in t.rows[t.start]]
    for n, row in enumerate(t.rows[t.start + 1 :], t.start + 2):
        if not any(row) or _uncached(t, n, p):
            continue
        item = {key: cell for key, cell in zip(columns, row, strict=False) if key}
        values = _position_values(item)
        if isinstance(values, str):
            p.unparsed.append({"row": f"{t.source} row {n}", "reason": values})
        else:
            p.positions.append(item | {"par": values[0], "pct_nav": values[1]})


def _limit_row(t: Table, n: int, item: dict[str, str], notes: list[str]) -> dict[str, Any] | str:
    kind = item.get("breach type", "")
    if kind not in ("Hard", "Soft"):
        return "no Hard or Soft breach type (info only)"
    parsed = parse_limit(item.get("limit", ""), item.get("parameter", ""))
    if isinstance(parsed, str):
        return parsed
    if parsed[1] == "amount" and _norm(t.unit) in _SCALED:
        return f"amount limit under Unit {t.unit}: the scale is not applied"
    text = item.get("current value", "")
    current = number(text)
    if current is None:
        return f"current value {text!r} is not a number"
    if problem := _unit_problem("current value", text, parsed[1], current[1]):
        return problem
    category = item.get("constraint category", "")
    scope, scope_value = _scope(category, item.get("parameter", ""))
    if scope == "rating_bucket" and scope_value is None:
        notes.append(f"{t.source} row {n}: Rating limit {category!r} names no bucket")
    return {
        "limit_id": item.get("id", ""),
        "category": category,
        "parameter": item.get("parameter", ""),
        "scope": scope,
        "scope_value": scope_value,
        "limit_value": parsed[0],
        "unit": parsed[1],
        "limit_kind": kind,
        "current_value": current[0],
        "source": f"{t.source} row {n}",
    }


def _limits(t: Table, p: Portfolio) -> None:
    header = [_norm(c) for c in t.rows[t.start]]
    for n, row in enumerate(t.rows[t.start + 1 :], t.start + 2):
        if not any(row) or _uncached(t, n, p):
            continue
        result = _limit_row(t, n, dict(zip(header, row, strict=False)), p.notes)
        if isinstance(result, str):
            p.unparsed.append({"row": f"{t.source} row {n}", "reason": result})
        else:
            p.limits.append(result)


def _link(source: str, kind: str, meta: dict[str, str], p: Portfolio) -> bool:
    """Add the table's meta to the portfolio; False for a second table of a kind (a note)."""
    for key, value in meta.items():
        if key in p.meta and p.meta[key] != value:
            p.notes.append(f"{source}: {key} {value!r} conflicts with {p.meta[key]!r}; kept")
    if kind in p.files:
        who = meta["portfolio_id"]
        p.notes.append(
            f"{source}: second {kind} table for {who!r} not merged ({p.files[kind]} kept)"
        )
        return False
    for key, value in meta.items():
        p.meta.setdefault(key, value)
    p.files[kind] = source
    return True


def read_sheet(
    source: str, rows: list[list[str]], found: dict[str, Portfolio], bad: dict[int, str]
) -> list[str]:
    """Add a positions or limits sheet to its portfolio; the notes for what cannot be linked.

    `bad` maps a 1-based row number to a formula cell there that has no stored value.
    """
    notes: list[str] = []
    for kind, required in (("positions", POSITIONS), ("limits", LIMITS)):
        start = _header(rows, required)
        if start is None:
            continue
        meta = _meta(rows[:start])
        portfolio_id = meta.get("portfolio_id")
        if not portfolio_id:
            notes.append(f"{source}: {kind} table without a Portfolio ID row; not linked")
        elif problem := _id_problem(portfolio_id, found):
            who = f"unsafe Portfolio ID {portfolio_id!r} ({problem})"
            notes.append(f"{source}: {kind} table has {who}; not linked")
        else:
            p = found.setdefault(portfolio_id, Portfolio())
            before = len(p.notes)
            if _link(source, kind, meta, p):
                table = Table(source, rows, start, bad, meta.get("unit", p.meta.get("unit", "")))
                (_positions if kind == "positions" else _limits)(table, p)
            notes += p.notes[before:]
    return notes


def _total(meta: dict[str, str], key: str, unparsed: list[dict[str, str]]) -> str:
    """Total NAV or Total Par: a plain amount only (no %, years or bps)."""
    text = meta.get(key, "")
    parsed = number(text)
    if parsed is not None and parsed[1] == "":
        return parsed[0]
    reason = "missing or not a number" if parsed is None else f"{text!r} is not a plain amount"
    unparsed.append({"row": f"Total {key.upper()}", "reason": reason})
    return ""


def to_json(p: Portfolio, rules: Rules) -> dict[str, Any]:
    meta, unparsed = dict(p.meta), list(p.unparsed)
    for key in ("nav", "par"):
        meta[key] = _total(meta, key, unparsed)
    as_of = iso_date(meta.get("as_of", ""))
    if as_of is None:
        reason = f"{meta.get('as_of', '')!r} is not a date I can read as yyyy-mm-dd"
        unparsed.append({"row": "As of", "reason": reason})
    meta["as_of"] = as_of or ""
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
        write_atomic(run / name, text)
        written.append({"portfolio_id": portfolio_id, "json": name})
    return written
