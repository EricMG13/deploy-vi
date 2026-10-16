"""The Front Page blocks: each catalog block resolved to its owners, tables, condition and lines.

`front_page_blocks` reads the `rbot-run/1` document (`run_json.build`) and the catalog's
`blocks` for the run's Front Page. A block is hidden by its condition, or shown with the tables
its owners handed over; an owner that failed or was skipped contributes one line with its reason
and no table, a Blocked owner keeps its tables (their gap cells stay `—`). Nothing is invented:
a table the owner's accepted Handoff lacks is a `ReportError`.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from typing import Any

from rbotlib.catalog import Block, Catalog
from rbotlib.contract import Contract
from rbotlib.report import ReportError

Record = dict[str, Any]
RUN_BRIEF = "RUN_BRIEF"
GAP = "—"
CONDITION_REASONS = {
    "primary": "Transaction summary: not a Primary run",
    "portfolios": "Portfolio Fit: no portfolio attached",
}
_PLAIN_DECIMAL = re.compile(r"^(-?)(\d{4,})(\.\d+)?$")
_GROUPS = re.compile(r"\B(?=(?:\d{3})+$)")
JOINED_LEVELS = ("bid", "ask", "mid", "yield_or_dm", "valuation")


def _primary(run: Record) -> bool:
    return run.get("primary") is True


def _portfolios(run: Record) -> bool:
    table = run["run_brief"]["tables"].get("brief.portfolios")
    return bool(table and table["rows"])


CONDITIONS: dict[str, Callable[[Record], bool]] = {
    "always": lambda _run: True,
    "primary": _primary,
    "portfolios": _portfolios,
}


def owner_of(
    table_id: str, record: Record, catalog: Catalog, contracts: Mapping[str, Contract]
) -> str:
    """The one step that produces `table_id`: a host step, else the one plan module listing it."""
    host = catalog.host_tables.get(table_id)
    if host is not None:
        return host
    owners = [
        m
        for m in record["plan"]
        if m in contracts and any(t.id == table_id for t in contracts[m].tables)
    ]
    if len(owners) != 1:
        raise ReportError(f"table {table_id} has {len(owners)} owners in the plan")
    return str(owners[0])


def _supported(block: Block) -> Callable[[Record], bool]:
    check = CONDITIONS.get(block.condition)
    if check is None:
        raise ReportError(f"condition {block.condition} not supported by this renderer")
    return check


def _table(run: Record, owner: str, table_id: str) -> Record:
    """The table's columns and rows, from the Run Brief or the owner's embedded Handoff."""
    if owner == RUN_BRIEF:
        found = run["run_brief"]["tables"].get(table_id)
    else:
        entry = run["handoffs"].get(owner)
        if entry is None:
            raise ReportError(f"handoffs/{owner}.md: not in the run document")
        found = entry["tables"].get(table_id)
    if found is None:
        raise ReportError(f"{owner}: table {table_id} missing from the Handoff")
    return {"columns": list(found["columns"]), "rows": [list(r) for r in found["rows"]]}


def _owner_status(run: Record, owner: str) -> str | None:
    """`accepted` for the Run Brief; the step's status; None when the plan does not run it."""
    if owner == RUN_BRIEF:
        return "accepted"
    step = run["steps"].get(owner)
    return None if step is None else str(step["status"])


def _block_entry(
    run: Record, block: Block, catalog: Catalog, contracts: Mapping[str, Contract]
) -> Record:
    tables: list[Record] = []
    seen: dict[str, str] = {}
    for table_id in block.tables:
        owner = owner_of(table_id, run, catalog, contracts)
        status = _owner_status(run, owner)
        if status is None:
            seen.setdefault(owner, f"{block.title}: {owner} not in this run")
            continue
        if status in ("failed", "skipped"):
            if owner not in seen:
                reason = run["steps"][owner].get("reason", "")
                seen[owner] = f"{block.title}: {owner} {status} — {reason}"
            continue
        if status == "blocked":
            seen.setdefault(owner, f"{owner} Blocked")
        tables.append(
            {"table_id": table_id, "owner": owner, "status": status, **_table(run, owner, table_id)}
        )
    lines = list(seen.values())
    return {
        "id": block.id,
        "title": block.title,
        "shown": True,
        "reason": None,
        "line": "; ".join(lines) if lines else None,
        "tables": tables,
        "charts": list(block.charts),
    }


def front_page_blocks(
    run: Record, catalog: Catalog, contracts: Mapping[str, Contract]
) -> list[Record]:
    """Every catalog block of the run's Front Page, in catalog order."""
    blocks = catalog.blocks.get(run["front_page"])
    if blocks is None:
        raise ReportError(f"front page {run['front_page']} has no blocks in the catalog")
    out: list[Record] = []
    for block in blocks:
        if not _supported(block)(run):
            out.append(
                {
                    "id": block.id,
                    "title": block.title,
                    "shown": False,
                    "reason": CONDITION_REASONS.get(block.condition, f"{block.title}: not shown"),
                    "line": None,
                    "tables": [],
                    "charts": [],
                }
            )
            continue
        out.append(_block_entry(run, block, catalog, contracts))
    return out


def join_capital_structure(
    cs: Record, levels: Record | None, rec: Record | None
) -> tuple[list[str], list[list[str]]]:
    """Left join of the capital structure with levels and recommendation on `facility_id`."""
    level_rows = _by_facility(levels)
    rec_rows = _by_facility(rec)
    key = cs["columns"].index("facility_id")
    columns = [*cs["columns"], *JOINED_LEVELS, "recommendation"]
    rows: list[list[str]] = []
    for row in cs["rows"]:
        level, recommendation = level_rows.get(row[key], {}), rec_rows.get(row[key], {})
        rows.append(
            [
                *row,
                *(level.get(c, GAP) for c in JOINED_LEVELS),
                recommendation.get("recommendation", GAP),
            ]
        )
    return columns, rows


def _by_facility(table: Record | None) -> dict[str, dict[str, str]]:
    """Rows keyed by `facility_id`, the first row of a repeated id winning."""
    found: dict[str, dict[str, str]] = {}
    if table is None or "facility_id" not in table["columns"]:
        return found
    for row in table["rows"]:
        cells = dict(zip(table["columns"], row, strict=False))
        found.setdefault(cells["facility_id"], cells)
    return found


def _rows(run: Record, table_id: str) -> list[dict[str, str]]:
    """The table's rows as column-keyed dicts, from the first Handoff that carries it."""
    for entry in run["handoffs"].values():
        table = entry["tables"].get(table_id)
        if table is not None:
            return [dict(zip(table["columns"], r, strict=False)) for r in table["rows"]]
    return []


def call_band(run: Record) -> Record:
    """The call band (R4): Recommendation per Strategy, Credit View and the per-instrument line."""
    view = next(iter(_rows(run, "snapshot.credit_view")), {})
    fit = _rows(run, "snapshot.portfolio_fit")
    return {
        "recommendation": {r["strategy"]: r for r in _rows(run, "snapshot.recommendation")},
        "credit_score": view.get("credit_score"),
        "credit_direction": view.get("credit_direction"),
        "sector_outlook": view.get("sector_outlook"),
        "instrument_line": _rows(run, "snapshot.instrument_recommendation"),
        "fit_line": {"rows": fit} if fit else None,
    }


def format_number(text: str, money: bool) -> str:
    """Thousands separators into a plain decimal string; digits are never changed."""
    if not money:
        return text
    match = _PLAIN_DECIMAL.match(text)
    if match is None:
        return text
    sign, whole, fraction = match.groups()
    return sign + _GROUPS.sub(",", whole) + (fraction or "")
