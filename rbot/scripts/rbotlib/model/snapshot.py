"""The MODEL host step's tables (spec §3.2) from the Model and its house view.

Each table is an `rbotlib.handoff.Table` of display strings. A figure is shown
as served by the Model except where the Model's own figure is a ratio: a
multiple is shown to two decimals, a percentage (a fraction times 100) to one,
days to one, each rounded half-even here and only here. A figure cell is a
`Fig`: the display string that also carries the exact value and the reason
there is none: `model.json` retains exact figures, while `MODEL.md` displays
the formatted text. A
cell without a figure is `—`. Columns ending `_x` carry `x`, `_pct` carry `%`.

On the PF-LTM, cash interest, closing cash and a facility are shown with the
PF rows that adjust them (the Model's lines show the LTM's figure there, the
PF rows beneath).
"""

from __future__ import annotations

import calendar
from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from typing import Self

from rbotlib.handoff import Table
from rbotlib.model._cells import CONTEXT, calc
from rbotlib.model.assemble import CreditModel
from rbotlib.model.citations import Citations
from rbotlib.model.debt import SECURED_RANKS
from rbotlib.model.frame import Cell, Column
from rbotlib.model.house import HouseView, cell, cumulative, percent_of, ratio, secured, with_pf
from rbotlib.model.house_inputs import HouseInputs
from rbotlib.model.layout import Line
from rbotlib.model.registers import Cp1Registers, iso_date

GAP = "\N{EM DASH}"
SLOTS = ("FY-2", "FY-1", "FY", "PYTD", "YTD", "LTM")
_SCALE_LABEL = {"UNITS": "", "THOUSANDS": " k", "MILLIONS": " m"}
_PLACES = {"PERCENT": Decimal("0.1"), "RATE": Decimal("0.01"), "MULTIPLE": Decimal("0.01")}
_PLACES |= {"DAYS": Decimal("0.1"), "SHARE": Decimal("0.1")}  # SHARE: a percentage already
_HUNDREDFOLD = frozenset({"PERCENT", "RATE"})
# The PF rows a line the PF-LTM shows unadjusted takes, by the metric they adjust.
_PF_METRIC = {"cash_interest": "cash_interest_paid", "cash_closing": "cash_and_equivalents"}
FINANCIALS = (
    ("Financials", "Revenue", "revenue"),
    ("Financials", "Revenue %Δ", "revenue_growth"),
    ("Financials", "Gross Profit", "gross_profit"),
    ("Financials", "Gross Profit %Δ", "gross_profit_growth"),
    ("Financials", "Gross Profit % margin", "metric:gross_margin"),
    ("Financials", "Reported EBITDA", "ebitda"),
    ("Financials", "EBITDA (SSIM basis)", "adjusted_ebitda"),
    ("Financials", "EBITDA (SSIM basis) %Δ", "adjusted_ebitda_growth"),
    ("Financials", "EBITDA (SSIM basis) % margin", "metric:adjusted_ebitda_margin"),
    ("Financials", "Cash Interest", "cash_interest"),
    ("Financials", "Leases", "lease_cash_not_in_ebitda"),
    ("Financials", "Cash tax", "cash_taxes"),
    ("Financials", "Other", "other_operating"),
    ("Financials", "FFO", "ffo"),
    ("Financials", "WC", "working_capital_change"),
    ("Financials", "CFO", "cfo_adjusted"),
    ("Financials", "Capex", "capex"),
    ("Financials", "FCF", "fcf"),
    ("Financials", "M&A", "acquisitions_net"),
    ("Financials", "Δ in debt", "debt_raised_net"),
    ("Financials", "Δ in equity", "equity_raised_net"),
    ("Financials", "Dividends", "dividends"),
    ("Financials", "Other investing and financing", "other_investing_financing"),
    ("Financials", "Net Δ in cash", "ncf"),
    ("Balance sheet", "Cash", "cash_closing"),
    ("Balance sheet", "Senior debt", "secured_debt"),
    ("Balance sheet", "Total debt", "total_debt"),
    ("Balance sheet", "Net debt", "net_debt"),
    ("Credit metrics", "Senior Leverage", "metric:senior_secured_leverage"),
    ("Credit metrics", "Total Leverage", "metric:total_leverage_adjusted"),
    ("Credit metrics", "Net Leverage", "metric:net_leverage_adjusted"),
    ("Credit metrics", "Interest Cover", "metric:interest_coverage_adjusted"),
)
_SUMMARY_FIXED = (
    "revenue",
    "revenue_growth",
    "gross_profit",
    "ebitda",
    "adjusted_ebitda",
    "cash_interest",
    "cash_taxes",
    "ffo",
    "cfo_adjusted",
    "capex",
    "fcf",
    "ncf",
    "cash_closing",
    "undrawn_rcf",
    "liquidity",
    "total_debt",
    "net_debt",
    "lease_adjusted_debt",
)


class Fig(str):
    """A table cell that holds a figure: the text shown, carrying the exact
    `value` (None for no figure) and, for none, the Model's `reason`."""

    value: Decimal | None
    unit: str
    reason: str | None

    def __new__(cls, text: str, value: Decimal | None, unit: str, reason: str | None) -> Self:
        found = super().__new__(cls, text)
        found.value, found.unit, found.reason = value, unit, reason
        return found


def fig(c: Cell, unit: str, suffix: str = "") -> Fig:
    """The Model cell as a table figure: `display`, then `suffix` for a figure."""
    shown = display(c.value, unit)
    return Fig(shown if c.value is None else f"{shown}{suffix}", c.value, unit, c.reason)


def gap(reason: str = "NOT_APPLICABLE") -> Fig:
    """A figure column that does not apply to the row: `—`, no value."""
    return Fig(GAP, None, "MONEY", reason)


@dataclass(frozen=True, slots=True)
class Context:
    model: CreditModel
    regs: Cp1Registers
    view: HouseView
    inputs: HouseInputs
    citations: Citations


def display(value: Decimal | None, unit: str) -> str:
    """The figure as the tables show it (module docstring); `—` for none."""
    if value is None:
        return GAP
    with localcontext(CONTEXT):
        shown = value * 100 if unit in _HUNDREDFOLD else value
        if unit in _PLACES:
            shown = shown.quantize(_PLACES[unit], rounding=ROUND_HALF_EVEN)
    if shown.is_zero():
        shown = shown.copy_abs()
    return format(shown, "f")


def money_label(regs: Cp1Registers) -> str:
    return f"{regs.currency}{_SCALE_LABEL.get(regs.unit, '')}"


def unit_label(line: Line, regs: Cp1Registers) -> str:
    labels = {"MONEY": money_label(regs), "PERCENT": "%", "RATE": "%", "MULTIPLE": "x"}
    labels |= {"DAYS": "days", "COUNT": "count", "KPI": line.unit_label or ""}
    return labels[line.unit]


def slots(model: CreditModel, view: HouseView) -> dict[str, Column | None]:
    """The Credit Snapshot's columns by slot (spec §6.4)."""
    fiscal = [c for c in model.columns if c.kind == "FY"]
    padded: list[Column | None] = [None, None, None, None, None, *fiscal]
    ytd = next((c for c in reversed(model.columns) if c.kind == "YTD"), None)
    pytd = next((c for c in model.columns if c.kind == "PYTD"), None)
    if ytd is None:
        pytd, ytd = padded[-5], padded[-4]
    return {
        "FY-2": padded[-3],
        "FY-1": padded[-2],
        "FY": padded[-1],
        "PYTD": pytd,
        "YTD": ytd,
        "LTM": view.column,
    }


def line_of(model: CreditModel, line_id: str) -> Line | None:
    return next((x for x in model.lines if x.line_id == line_id), None)


def shown_cell(ctx: Context, line_id: str, column: Column | None) -> Cell:
    """The line's cell on the column, PF rows added on the PF-LTM where the
    line shows the LTM's figure there."""
    if column is None:
        return Cell(None, "NOT_APPLICABLE")
    if line_id.startswith("fac:"):
        metric = f"facility:{line_id.removeprefix('fac:')}"
        return with_pf(ctx.model, ctx.regs, column, line_id, metric)
    if line_id in _PF_METRIC:
        return with_pf(ctx.model, ctx.regs, column, line_id, _PF_METRIC[line_id])
    return cell(ctx.model, line_id, column)


def financial_columns(ctx: Context) -> Table:
    rows = []
    for slot, column in slots(ctx.model, ctx.view).items():
        if column is None:
            rows.append([slot, GAP, "n/a", GAP, GAP, GAP])
            continue
        kind = "PF_LTM" if column.kind == "PF_LTM" else column.kind
        rows.append(
            [
                slot,
                column.column_id,
                column.label,
                column.period_id or GAP,
                kind,
                column.end_date or GAP,
            ]
        )
    return Table(["slot", "column_id", "label", "period_id", "kind", "end_date"], rows)


def _values(ctx: Context, line: Line, columns: Iterable[Column | None]) -> list[Fig]:
    return [fig(shown_cell(ctx, line.line_id, c), line.unit) for c in columns]


def financials(ctx: Context) -> Table:
    columns = list(slots(ctx.model, ctx.view).values())
    rows = []
    for section, label, line_id in FINANCIALS:
        line = line_of(ctx.model, line_id)
        if line is None:
            rows.append(
                [section, label, line_id, GAP, *([gap()] * 6), f"calc: no Model line {line_id}"]
            )
            continue
        values = _values(ctx, line, columns)
        rows.append(
            [
                section,
                label,
                line_id,
                unit_label(line, ctx.regs),
                *values,
                f"calc: model.json line {line_id}",
            ]
        )
    names = ["section", "line", "line_id", "unit_label", "fy_2", "fy_1", "fy", "pytd", "ytd"]
    return Table([*names, "ltm", "cite"], rows)


def _host_ltm(model: CreditModel) -> Column | None:
    return next((c for c in model.columns if c.kind == "LTM"), None)


def _pf(model: CreditModel) -> Column | None:
    return next((c for c in model.columns if c.kind == "PF_LTM"), None)


def summary(ctx: Context) -> Table:
    taken = slots(ctx.model, ctx.view)
    columns = [*(taken[s] for s in SLOTS[:5]), _host_ltm(ctx.model), _pf(ctx.model)]
    wanted = [
        *_SUMMARY_FIXED[:5],
        *(x.line_id for x in ctx.model.lines if x.line_id.startswith("addback:")),
        *_SUMMARY_FIXED[5:15],
        *(x.line_id for x in ctx.model.lines if x.line_id.startswith(("rank:", "fac:"))),
        *_SUMMARY_FIXED[15:],
    ]
    rows = []
    for line_id in wanted:
        line = line_of(ctx.model, line_id)
        if line is None:
            continue
        rows.append(
            [
                line_id,
                line.label,
                line.band,
                unit_label(line, ctx.regs),
                *_values(ctx, line, columns),
            ]
        )
    names = ["line_id", "label", "band", "unit_label", "fy_2", "fy_1", "fy", "pytd", "ytd"]
    return Table([*names, "ltm", "pf_ltm"], rows)


def metrics(ctx: Context) -> Table:
    taken = slots(ctx.model, ctx.view)
    columns = [taken["FY-2"], taken["FY-1"], taken["FY"], _host_ltm(ctx.model), _pf(ctx.model)]
    rows = [
        [line.line_id, line.label, *_values(ctx, line, columns)]
        for line in ctx.model.lines
        if line.band == ctx.model.lines[-1].band
    ]
    return Table(["metric_id", "label", "fy_2", "fy_1", "fy", "ltm", "pf_ltm"], rows)


def _basis(ctx: Context) -> str:
    column = ctx.view.column
    return "PF-LTM" if column is not None and column.kind == "PF_LTM" else "LTM"


def _multiples(ctx: Context, amount: Cell) -> list[Fig]:
    structuring = ctx.view.item("structuring_ebitda").cell
    ssim = ctx.view.item("ssim_ebitda").cell
    return [
        fig(ratio(amount, structuring), "MULTIPLE", "x"),
        fig(ratio(amount, ssim), "MULTIPLE", "x"),
    ]


def _ev_share(ctx: Context, amount: Cell) -> Fig:
    return fig(percent_of(amount, ctx.view.item("ev").cell), "SHARE", "%")


def capital_structure(ctx: Context) -> Table:
    rows = []
    talk = ctx.inputs.brief.tranche_ids
    for position in ctx.view.positions:
        line, identity = position.line, ctx.inputs.identities.get(position.facility_id)
        terms = line.terms
        spread = terms.spread_or_coupon if terms is not None else GAP
        if position.facility_id in talk:
            spread = f"{spread} (talk)"
        rank = line.rank or GAP
        through = cumulative(ctx.view, rank) if line.rank else Cell(None, "NOT_APPLICABLE")
        cite = ctx.citations.cite("CP-1", position.outstanding.sources)
        rows.append(
            [
                position.facility_id,
                line.label,
                (identity.bloomberg_id if identity else None) or GAP,
                (identity.ratings if identity else None) or GAP,
                spread,
                ctx.regs.currency,  # a facility in another currency is a memo line
                ctx.regs.unit,
                terms.maturity if terms is not None else GAP,
                fig(position.outstanding, "MONEY"),
                rank,
                "Yes" if line.rank in SECURED_RANKS else "No",
                *_multiples(ctx, through),
                _ev_share(ctx, position.outstanding),
                _basis(ctx),
                cite,
            ]
        )
    columns = ["facility_id", "facility", "bloomberg_id", "facility_ratings", "spread_or_coupon"]
    columns += ["currency", "unit", "maturity_date", "outstanding", "rank", "secured"]
    columns += ["structuring_multiple_x", "ssim_multiple_x", "pct_ev_pct", "column_basis", "cite"]
    return Table(columns, rows)


def _total_row(ctx: Context, line: str, amount: Cell, basis: str, shown: str) -> list[str]:
    """A totals row; `shown` is `debt` (multiples of Structuring and SSIM
    EBITDA and the share of EV), `share` (the share of EV) or `amount`."""
    return [
        line,
        fig(amount, "MONEY"),
        ctx.regs.currency,
        ctx.regs.unit,
        *(_multiples(ctx, amount) if shown == "debt" else [gap(), gap()]),
        _ev_share(ctx, amount) if shown in {"debt", "share"} else gap(),
        basis,
        f"calc: {basis}",
    ]


def _unsecured(view: HouseView) -> Cell:
    """Every position that is not senior secured, so that senior secured plus
    unsecured foots to the positions (finance leases, `Not stated` and the
    debt adjustments included)."""
    if not view.positions:
        return Cell(None, "NOT_SOURCED")
    parts = [(p.outstanding, 1) for p in view.positions if p.line.rank not in SECURED_RANKS]
    with localcontext(CONTEXT):
        return calc(parts)


def capital_structure_totals(ctx: Context) -> Table:
    columns = ["line", "amount", "currency", "unit", "structuring_multiple_x", "ssim_multiple_x"]
    columns += ["pct_ev_pct", "basis", "cite"]
    view = ctx.view
    if view.column is None:
        return Table(columns, [])
    total = cell(ctx.model, "total_debt", view.column)
    cash = shown_cell(ctx, "cash_closing", view.column)
    interest = view.item("pf_interest").cell
    cover = fig(view.item("pf_interest_cover").cell, "MULTIPLE", "x")
    unsecured = _unsecured(view)
    equity_basis = view.ev_basis or GAP  # `listed`, `ssim_multiple` or `—` (spec §3.2)
    ev = view.item("ev")
    rows = [
        _total_row(ctx, "Senior secured debt", secured(view), "secured facilities", "debt"),
        _total_row(ctx, "Unsecured debt", unsecured, "unsecured facilities", "debt"),
        _total_row(ctx, "Total debt", total, "total_debt", "debt"),
        _total_row(ctx, "Cash", cash, "cash_closing with PF rows", "amount"),
        _total_row(ctx, "Equity", view.equity, equity_basis, "share"),
        _total_row(ctx, "EV", ev.cell, ev.formula, "debt"),
        _total_row(ctx, "PF interest", interest, "-(cash_interest + its PF rows)", "amount"),
        [
            "PF interest cover",
            gap(),
            ctx.regs.currency,
            ctx.regs.unit,
            cover,
            cover,
            gap(),
            "SSIM EBITDA / PF interest",
            "calc: SSIM EBITDA / PF interest",
        ],
    ]
    return Table(columns, rows)


def _adjustment_row(ctx: Context, label: str, kind: str, c: Cell, status: str) -> list[str]:
    cite = f"calc: {label}" if kind == "Total" else ctx.citations.cite("CP-1", c.sources)
    shown = c.value if kind != "Unrealized add-back" or c.value is None else c.value.copy_negate()
    unit = [ctx.regs.currency, ctx.regs.unit]
    amount = fig(replace(c, value=shown), "MONEY")
    return [label, kind, amount, *unit, status, _basis(ctx), cite]


def _status(ctx: Context, line: Line, column: Column, fixed: dict[str, str]) -> str:
    """The realization status a bridge row shows: an excluded add-back is
    `UNREALIZED`, or `NOT_STATED` where CP-1's (or CP-1D's) status is."""
    if line.kind != "MEMO":
        return fixed[line.kind]
    own = [b for b in ctx.regs.addbacks if f"addback:{b.addback_id}" == line.line_id]
    at = [b for b in own if b.period_id == column.period_id] or own
    return "NOT_STATED" if any(b.realization_status == "NOT_STATED" for b in at) else "UNREALIZED"


def ebitda_adjustments(ctx: Context) -> Table:
    """Reported EBITDA, every add-back (realized and not) and the PF rows to
    adjusted EBITDA, Structuring EBITDA, each unrealized add-back taken off
    again, SSIM EBITDA: a bridge that foots on the snapshot column (D19)."""
    column = ctx.view.column
    if column is None:
        return Table(_ADJUSTMENT_COLUMNS, [])
    band = _adjusted_band(ctx.model)
    shown = [
        (line, cell(ctx.model, line.line_id, column))
        for line in ctx.model.lines
        if line.band == band and (line.line_id.startswith("addback:") or line.kind == "PF")
    ]
    shown = [(line, c) for line, c in shown if c.reason != "NOT_SOURCED"]
    status = {"ACCOUNT": "REALIZED", "PF": GAP}
    reported = cell(ctx.model, "ebitda", column)
    rows = [_adjustment_row(ctx, "Reported EBITDA", "Total", reported, GAP)]
    rows += [
        _adjustment_row(ctx, x.label, "Add-back", c, _status(ctx, x, column, status))
        for x, c in shown
    ]
    structuring = ctx.view.item("structuring_ebitda").cell
    rows.append(_adjustment_row(ctx, "Structuring EBITDA", "Total", structuring, GAP))
    rows += [
        _adjustment_row(ctx, x.label, "Unrealized add-back", c, _status(ctx, x, column, status))
        for x, c in shown
        if x.kind == "MEMO"
    ]
    ssim = ctx.view.item("ssim_ebitda").cell
    rows.append(_adjustment_row(ctx, "SSIM EBITDA", "Total", ssim, GAP))
    return Table(_ADJUSTMENT_COLUMNS, rows)


_ADJUSTMENT_COLUMNS = ["line", "kind", "amount", "currency", "unit", "realization_status"]
_ADJUSTMENT_COLUMNS += ["basis", "cite"]


def _adjusted_band(model: CreditModel) -> str:
    return next(x.band for x in model.lines if x.line_id == "adjusted_ebitda")


def house(ctx: Context) -> Table:
    column = ctx.view.column
    rows = []
    for item in ctx.view.items:
        label = money_label(ctx.regs) if item.unit == "MONEY" else "x"
        rows.append(
            [
                item.item,
                fig(item.cell, item.unit),
                label,
                column.column_id if column else GAP,
                item.formula,
                "; ".join(item.components),
                item.cell.reason or GAP,
            ]
        )
    columns = ["item", "value", "unit_label", "column_id", "formula", "components", "reason"]
    return Table(columns, rows)


def maturity_year(text: str | None) -> int | None:
    """The calendar year a maturity falls in: a `YYYY-MM-DD` date's, or a
    year written alone (`2028`, as a debt note's final-maturity column
    gives it); None otherwise."""
    day = iso_date(text)
    if day is not None:
        return day.year
    if text is not None and len(text) == 4 and text.isdigit():
        return int(text)
    return None


def fiscal_year_of(day: date, year_end: date | None) -> int:
    """The fiscal year (named by the calendar year it ends in) that `day`
    falls in, given a year end's month and day (a 52/53-week year uses the
    latest year end's); the calendar year where no year end is known."""
    if year_end is None:
        return day.year
    last = calendar.monthrange(day.year, year_end.month)[1]
    end = date(day.year, year_end.month, min(year_end.day, last))
    return day.year if day <= end else day.year + 1


def _year_end(model: CreditModel) -> date | None:
    ends = [iso_date(c.end_date) for c in model.columns if c.kind == "FY"]
    return max((d for d in ends if d is not None), default=None)


def maturity_wall(ctx: Context) -> tuple[Table, list[tuple[str, str]]]:
    rows, limits = [], []
    year_end = _year_end(ctx.model)
    if year_end is None:
        why = "no fiscal year in the register: maturities are by calendar year"
        limits.append(("MATURITY_CALENDAR_YEAR", why))
    for position in ctx.view.positions:
        terms = position.line.terms
        text = terms.maturity if terms is not None else None
        year = maturity_year(text)
        if year is None:
            limits.append(("MATURITY_NOT_STATED", f"{position.facility_id}: no maturity date"))
            continue
        if position.outstanding.value is None:
            why = f"{position.facility_id}: no outstanding amount at the snapshot date"
            limits.append(("MATURITY_AMOUNT_NOT_STATED", why))
            continue
        if position.outstanding.value == 0:
            continue
        day = iso_date(text)
        if day is not None:
            year = fiscal_year_of(day, year_end)
        rows.append(
            [
                str(year),
                position.facility_id,
                fig(position.outstanding, "MONEY"),
                ctx.regs.currency,
                ctx.regs.unit,
                position.line.rank or GAP,
            ]
        )
    rows.sort(key=lambda r: (r[0], r[1]))
    columns = ["fiscal_year", "facility_id", "amount", "currency", "unit", "rank"]
    return Table(columns, rows), limits


def limitation_rows(limits: Iterable[tuple[str, str, str, str]]) -> Table:
    return Table(["code", "message", "line_id", "column_id"], [list(x) for x in limits])


def build_tables(ctx: Context) -> tuple[dict[str, Table], list[tuple[str, str]]]:
    """Every §3.2 table by id but `model.limitations`, and the limitations the
    tables found (a facility without a maturity date)."""
    wall, wall_limits = maturity_wall(ctx)
    if ctx.view.column is None:
        why = "no LTM column: capital_structure_totals and ebitda_adjustments have no rows"
        wall_limits.append(("TABLES_EMPTY_NO_LTM", why))
    tables = {
        "snapshot.capital_structure": capital_structure(ctx),
        "snapshot.capital_structure_totals": capital_structure_totals(ctx),
        "snapshot.ebitda_adjustments": ebitda_adjustments(ctx),
        "snapshot.financial_columns": financial_columns(ctx),
        "snapshot.financials": financials(ctx),
        "model.summary": summary(ctx),
        "model.metrics": metrics(ctx),
        "model.house": house(ctx),
        "model.maturity_wall": wall,
    }
    return tables, wall_limits
