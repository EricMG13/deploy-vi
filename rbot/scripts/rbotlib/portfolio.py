"""Portfolio Context to `prepared/portfolios/<portfolio_id>.json` (interfaces spec section 7).

A sheet (CSV or workbook tab) is a positions table when its header row names Issuer ID,
Issuer, Par and % NAV, and a limits table when it names the compliance-monitor columns
ID, Constraint Category, Parameter, Limit, Breach Type and Current Value. Key-value
rows above the header give the portfolio: Portfolio ID (required to link the two),
Portfolio, Strategy, As of, Currency, Unit, Total NAV and Total Par. A sheet may stack
several tables; each header row starts a new one. Amounts keep the file's unit, so an
amount limit is read only when every table's Unit is blank or an unscaled currency (USD,
EUR, GBP, units); decided after all tables are linked, never by file order. Rows RBOT
cannot use are kept under `unparsed` with the reason, never dropped. A `%` current value
cannot tell pct_nav from pct_par; the limit's unit decides.
"""

from __future__ import annotations

import itertools
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
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
_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"  # commas only as thousands groups
_LIMIT = re.compile(
    r"^(?P<op>≤|<=|<|≥|>=|>)?\s*(?P<cur>\$)?(?P<num>" + _NUM + r")\s*"
    r"(?P<unit>%\s*nav|%\s*par|years?|yrs?)?$",
    re.I,
)


_COUNT = re.compile(r"\b(count|number of|no\. of|maximum names)\b", re.I)
_UNSCALED = frozenset({"usd", "eur", "gbp"})  # a Unit that leaves amounts as written
_EXPECTED = {"pct_nav": "%", "pct_par": "%", "years": "years", "amount": "", "count": ""}
_DATES = ("%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y")
_NUMBER = re.compile(r"^\$?(-?" + _NUM + r")\s*(%|yrs?|years?|bps)?$", re.I)


@dataclass
class Table:
    """One positions or limits table: where it came from and what its sheet says about it."""

    source: str
    rows: list[list[str]]
    start: int
    bad: dict[int, str]  # 1-based row -> a formula cell there with no stored value
    end: int | None = None  # one past this table's last row; None = the end of the sheet


@dataclass
class Portfolio:
    meta: dict[str, str] = field(default_factory=dict)
    positions: list[dict[str, str]] = field(default_factory=list)
    limits: list[dict[str, Any]] = field(default_factory=list)
    unparsed: list[dict[str, str]] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    units: set[str] = field(default_factory=set)  # every table's Unit, normalised, non-blank


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
    value = format(Decimal(match.group(1).replace(",", "")), "f")
    suffix = (match.group(2) or "").lower()
    return value, "years" if suffix.startswith("y") else suffix


def _comma(*texts: str) -> str:
    """A reason suffix when a text holds a comma that is not a thousands separator."""
    return (
        " (ambiguous decimal comma)"
        if any(re.search(r"\d,\d{1,2}(?!\d)", t) for t in texts)
        else ""
    )


def _not_a_number(label: str, text: str) -> str:
    return f"{label} {text!r} is not a number{_comma(text)}"


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
        return _not_a_number("limit", text) + " with a unit"
    if match["op"] in ("≥", ">=", ">"):
        return "minimum limit: Portfolio Fit sizes against maximum limits only"
    unit = _norm(match["unit"] or "").replace(" ", "")
    units = {"%nav": "pct_nav", "%par": "pct_par", "year": "years", "years": "years"}
    kind = units.get(unit) or ("years" if unit.startswith("yr") else None)
    if kind is None and not match["cur"]:
        if not _COUNT.search(parameter):
            return f"limit {text!r}: unit not recognised"
        kind = "count"
    value = Decimal(match["num"].replace(",", ""))
    if kind == "count" and value != value.to_integral_value():
        return f"count limit {text!r} is not a whole number"
    return format(value, "f"), kind or "amount"


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


def _is_meta_line(row: list[str]) -> bool:
    cells = [c for c in row if c]
    return len(cells) <= 1 or _norm(cells[0]) in META


def _tables(rows: list[list[str]]) -> list[tuple[str, int, int, int]]:
    """(kind, header row, first meta row, end of data) of every table stacked in the sheet."""
    heads: dict[int, str] = {}
    for kind, required in (("limits", LIMITS), ("positions", POSITIONS)):
        heads |= {i: kind for i, row in enumerate(rows) if set(required) <= {_norm(c) for c in row}}
    if not heads:
        return []
    order, firsts = sorted(heads), [0]
    for prev, i in itertools.pairwise(order):
        first = i
        while first > prev + 1 and _is_meta_line(rows[first - 1]):
            first -= 1
        firsts.append(first)
    ends = [*firsts[1:], len(rows)]
    return [(heads[i], i, f, e) for i, f, e in zip(order, firsts, ends, strict=True)]


def _meta(rows: list[list[str]], notes: list[str], source: str) -> dict[str, str]:
    found = {}
    for row in rows:
        cells = [c for c in row if c]
        if len(cells) >= 2 and _norm(cells[0]) in META:
            found[META[_norm(cells[0])]] = cells[1]
            if len(cells) > 2:
                notes.append(
                    f"{source}: {cells[0]} row has extra cells {cells[2:]}; read {cells[1]!r}"
                )
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
        return "par or % NAV is not a number" + _comma(item.get("par", ""), item.get("pct_nav", ""))
    if par[1] != "" or pct[1] != "%":
        return f"par {item['par']!r} must be a plain amount and % NAV {item['pct_nav']!r} a percent"
    return par[0], pct[0]


def _positions(t: Table, p: Portfolio) -> None:
    columns = [POSITION_COLUMNS.get(_norm(c)) for c in t.rows[t.start]]
    for n, row in enumerate(t.rows[t.start + 1 : t.end], t.start + 2):
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
    text = item.get("current value", "")
    current = number(text)
    if current is None:
        return _not_a_number("current value", text)
    if parsed[1] == "count" and "." in current[0] and Decimal(current[0]) % 1:
        return f"count current value {text!r} is not a whole number"
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
    for n, row in enumerate(t.rows[t.start + 1 : t.end], t.start + 2):
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
    if meta.get("unit"):
        p.units.add(_norm(meta["unit"]))
    p.files[kind] = source
    return True


def read_sheet(
    source: str, rows: list[list[str]], found: dict[str, Portfolio], bad: dict[int, str]
) -> list[str]:
    """Add the positions and limits tables of a sheet to their portfolios; the notes for the rest.

    `bad` maps a 1-based row number to a formula cell there that has no stored value.
    """
    notes: list[str] = []
    meta: dict[str, str] = {}
    for kind, start, first, end in _tables(rows):
        found_notes: list[str] = []
        own = _meta(rows[first:start], found_notes, source)
        notes += found_notes
        meta = own if "portfolio_id" in own or not meta else meta  # no id of its own: same as above
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
                table = Table(source, rows, start, bad, end)
                (_positions if kind == "positions" else _limits)(table, p)
            notes += p.notes[before:]
            p.notes += found_notes
    return notes


def _total(meta: dict[str, str], key: str, unparsed: list[dict[str, str]]) -> str:
    """Total NAV or Total Par: a plain amount above zero only (no %, years or bps)."""
    text = meta.get(key, "")
    parsed = number(text)
    if parsed is not None and parsed[1] == "" and Decimal(parsed[0]) > 0:
        return parsed[0]
    if parsed is None:
        reason = "missing or not a number" + _comma(text)
    else:
        reason = f"{text!r} is not a plain amount above zero"
    unparsed.append({"row": f"Total {key.upper()}", "reason": reason})
    return ""


def _amount_limits(p: Portfolio) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Amount limits read only when every table's Unit leaves amounts as written (any order)."""
    units = p.units - {"units"}  # "units" says nothing about a scale
    if units <= _UNSCALED and len(units) <= 1:
        return p.limits, []
    shown = ", ".join(sorted(units))
    reason = f"amount limit under Unit {shown!r}: the scale is not applied"
    kept = [x for x in p.limits if x["unit"] != "amount"]
    return kept, [{"row": x["source"], "reason": reason} for x in p.limits if x["unit"] == "amount"]


def to_json(p: Portfolio, rules: Rules) -> dict[str, Any]:
    meta, unparsed = dict(p.meta), list(p.unparsed)
    limits, scaled = _amount_limits(p)
    unparsed += scaled
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
    return data | {
        "positions": p.positions,
        "limits": limits,
        "unparsed": unparsed,
        "notes": p.notes,
    }


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
    for stale in folder.glob("*.json"):  # a portfolio that is no longer in the pack
        if stale.name not in {f"{w['portfolio_id']}.json" for w in written}:
            stale.unlink()
    return written
