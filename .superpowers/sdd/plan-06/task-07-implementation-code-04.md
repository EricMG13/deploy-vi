# Task06.7 exact replay file 04

Source: `rbot/scripts/rbotlib/model/house.py`; complete executed bytes, SHA256 `be7ef46a581d8659f9b40703c400643f7ff1dffdf188e7aadc4814ac5b691bd7`, 17661 bytes, 427 LF. Baseline1094a76; final source tree/proof is recorded separately. This ordinary whole file receives no cap exemption.

```python
"""The house view on the PF-LTM (spec D19, §6.5): Structuring and SSIM EBITDA,
PF interest and its cover, the Structuring and SSIM Multiples, EV and each
facility's share of it, adjusted debt and adjusted leverage. Quality-adjusted
EBITDA is not computed: a `Rejected` add-back counts as unrealized (§6.5), so
it would always equal SSIM EBITDA (controller ruling, 2026-10-11).

Every figure is read on the snapshot column: the PF-LTM where the Model has
one, else the host's LTM (the first LTM column, the one the PF-LTM adds to).
The Model runs with `exclude_unrealised`, so its adjusted EBITDA is SSIM
EBITDA; Structuring EBITDA adds back every excluded add-back (an add-back
with no row for the period adds nothing). PF interest is the column's cash
interest as a positive amount. A denominator at or below zero gives no figure
(`ZERO_OR_NEGATIVE_DENOMINATOR`); a missing input gives the first missing
input's reason noted with why each missing input is missing, as the Model's
metric lines do. EV is the listed equity value
(converted to the run's unit; another currency gives no EV) plus net debt,
else the Run Brief's SSIM EV multiple times SSIM EBITDA, else none.

A facility's outstanding on the PF-LTM is its LTM balance plus the PF rows
adjusting it; a facility with no balance at the date and no PF row is not in
the capital structure. CP-1D's debt-like items treated `Debt-like` become
`debt_like:<item>` memo lines in the debt band and add to adjusted debt.

Pure: Decimal only, no I/O; nothing is rounded.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from decimal import Decimal, localcontext
from typing import Literal

from rbotlib.model._cells import ABSENT, CONTEXT, calc, join_notes, refs
from rbotlib.model.assemble import CreditModel
from rbotlib.model.debt import PAYMENT_RANKS, SECURED_RANKS
from rbotlib.model.frame import Cell, Column, SourceRef
from rbotlib.model.house_inputs import DebtLikeItem, HouseInputs, debt_like_key
from rbotlib.model.layout import BANDS, Line
from rbotlib.model.periods import LTM_DAYS
from rbotlib.model.registers import Cp1Registers

Unit = Literal["MONEY", "MULTIPLE", "PERCENT"]
_SCALE = {"UNITS": Decimal(1), "THOUSANDS": Decimal(10) ** 3, "MILLIONS": Decimal(10) ** 6}
_FACILITY = "facility:"


@dataclass(frozen=True, slots=True)
class HouseItem:
    item: str  # a `house_item` scale value
    key: str  # its model.json key
    cell: Cell
    unit: Unit
    formula: str
    components: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Position:
    """A facility in the capital structure on the snapshot column."""

    facility_id: str
    line: Line
    outstanding: Cell


@dataclass(frozen=True, slots=True)
class HouseView:
    column: Column | None
    items: tuple[HouseItem, ...]
    positions: tuple[Position, ...]
    equity: Cell
    ev_basis: Literal["listed", "ssim_multiple"] | None
    limitations: tuple[tuple[str, str], ...]

    def item(self, key: str) -> HouseItem:
        return next(i for i in self.items if i.key == key)


def snapshot_column(model: CreditModel) -> Column | None:
    """The PF-LTM where it exists, else the host's LTM, else none."""
    pf = next((c for c in model.columns if c.kind == "PF_LTM"), None)
    return pf or next((c for c in model.columns if c.kind == "LTM"), None)


def cell(model: CreditModel, line_id: str, column: Column) -> Cell:
    """The line's cell on the column; `NOT_SOURCED` for a line the Model has not."""
    index = model.columns.index(column)
    line = next((x for x in model.lines if x.line_id == line_id), None)
    return ABSENT if line is None else line.cells[index]


def ratio(numerator: Cell, denominator: Cell) -> Cell:
    """`numerator / denominator`, exact at the Model's precision."""
    top, bottom = numerator.value, denominator.value
    if top is None or bottom is None:
        missing = [c for c in (numerator, denominator) if c.value is None]
        return Cell(None, missing[0].reason, note=join_notes(*(c.note for c in missing)))
    if bottom <= 0:
        return Cell(None, "ZERO_OR_NEGATIVE_DENOMINATOR")
    with localcontext(CONTEXT):
        value = top / bottom
    sources = refs([*numerator.sources, *denominator.sources])
    return Cell(value, basis="CALCULATED", sources=sources)


def _sum(parts: Iterable[tuple[Cell, int]]) -> Cell:
    with localcontext(CONTEXT):
        return calc(parts)


def _pf_rows(model: CreditModel, regs: Cp1Registers, column: Column, metric_id: str) -> list[Cell]:
    if column.kind != "PF_LTM":
        return []
    ids = [
        a.adjustment_id
        for a in regs.pro_forma
        if a.period_id == column.period_id and a.metric_id == metric_id
    ]
    return [cell(model, f"pf:{i}", column) for i in ids]


def with_pf(
    model: CreditModel, regs: Cp1Registers, column: Column, line_id: str, metric_id: str
) -> Cell:
    """A line the PF-LTM shows unadjusted (its PF rows beneath: a facility,
    cash interest, closing cash) with those rows added. A facility with no
    balance at the date (`NOT_SOURCED`) starts from zero when it has PF rows
    (a new tranche); any other line without a figure gives no figure
    (`COMPONENT_MISSING`), as the Model's own PF-LTM frame does."""
    own = cell(model, line_id, column)
    rows = _pf_rows(model, regs, column, metric_id)
    if not rows:
        return own
    if own.reason == "NOT_SOURCED" and line_id.startswith("fac:"):
        own = Cell(Decimal(0))
    elif own.value is None:
        label = line_id.replace("_", " ")
        return Cell(None, "COMPONENT_MISSING", note=f"LTM {label} not sourced")
    return _sum([(own, 1), *((r, 1) for r in rows)])


def _positions(model: CreditModel, regs: Cp1Registers, column: Column) -> tuple[Position, ...]:
    found = []
    for line in model.lines:
        if not line.line_id.startswith("fac:") or line.kind != "ACCOUNT":
            continue
        facility_id = line.line_id.removeprefix("fac:")
        outstanding = with_pf(model, regs, column, line.line_id, f"{_FACILITY}{facility_id}")
        if outstanding.reason != "NOT_SOURCED":
            found.append(Position(facility_id, line, outstanding))
    return tuple(found)


def _dates(regs: Cp1Registers) -> dict[str, str]:
    """Every registered period's known end date, including undisplayed balance dates."""
    return {p.period_id: p.end_date for p in regs.periods if p.end_date}


def _on(regs: Cp1Registers, column: Column, items: Iterable[DebtLikeItem]) -> list[DebtLikeItem]:
    """The `Debt-like` items whose period ends on the column's date (a balance)."""
    dates = _dates(regs)
    return [
        i
        for i in items
        if i.treatment == "Debt-like" and dates.get(i.period_id, "") == column.end_date
    ]


def with_debt_like_lines(
    model: CreditModel, regs: Cp1Registers, items: tuple[DebtLikeItem, ...]
) -> CreditModel:
    """The Model with one memo line per `Debt-like` item at the end of the
    debt band, each period's amount on the columns ending on its date."""
    keys = dict.fromkeys(debt_like_key(i) for i in items if i.treatment == "Debt-like")
    if not keys:
        return model
    lines = list(model.lines)
    band = BANDS[7]
    at = max(n for n, line in enumerate(lines) if line.band == band) + 1
    new = []
    for key in keys:
        own = [i for i in items if debt_like_key(i) == key]
        cells = []
        for column in model.columns:
            found = _on(regs, column, own)
            if not found:
                cells.append(Cell(None, "NOT_SOURCED"))
                continue
            source = SourceRef(found[0].cite, "", f"{found[0].amount:f}")
            cells.append(Cell(found[0].amount, basis="REPORTED", sources=(source,)))
        label = f"Memo: debt-like, {own[0].item}"
        new.append(Line(key, band, label, "MEMO", "MONEY", None, None, None, tuple(cells)))
    return replace(model, lines=(*lines[:at], *new, *lines[at:]))


def _structuring(model: CreditModel, column: Column, ssim: Cell) -> HouseItem:
    excluded = [x for x in model.lines if x.line_id.startswith("addback:") and x.kind == "MEMO"]
    cells = [(cell(model, x.line_id, column), x.line_id) for x in excluded]
    parts = [(c, 1) for c, _ in cells if c.reason != "NOT_SOURCED"]
    ids = tuple(i for c, i in cells if c.reason != "NOT_SOURCED")
    formula = "adjusted_ebitda + excluded (unrealized) add-backs"
    total = _sum([(ssim, 1), *parts])
    return HouseItem(
        "Structuring EBITDA",
        "structuring_ebitda",
        total,
        "MONEY",
        formula,
        ("adjusted_ebitda", *ids),
    )


def _adjusted_debt(
    regs: Cp1Registers, column: Column, total_debt: Cell, inputs: HouseInputs
) -> tuple[HouseItem, list[tuple[str, str]]]:
    counted = _on(regs, column, inputs.debt_like)
    parts = [(Cell(i.amount, basis="REPORTED"), 1) for i in counted]
    value = _sum([(total_debt, 1), *parts])
    formula = "total_debt + CP-1D debt-like items"
    components = ("total_debt", *dict.fromkeys(debt_like_key(i) for i in counted))
    item = HouseItem("Adjusted debt", "adjusted_debt", value, "MONEY", formula, components)
    left = [i for i in inputs.debt_like if i.treatment == "Debt-like" and i not in counted]
    if not left:
        return item, []
    named = ", ".join(f"{i.item} ({i.period_id})" for i in left)
    why = f"{named}: not at the {column.label} date {column.end_date}; adjusted debt leaves out"
    return item, [("DEBT_LIKE_NOT_ON_SNAPSHOT", why)]


def _equity(
    regs: Cp1Registers, inputs: HouseInputs, net_debt: Cell, ssim: Cell
) -> tuple[Cell, Cell, Literal["listed", "ssim_multiple"] | None, list[tuple[str, str]]]:
    """EV, equity, EV basis and limitations."""
    equity = inputs.equity
    if equity is not None:
        if equity.currency != regs.currency:
            why = f"equity value in {equity.currency}, the run is in {regs.currency}"
            none = Cell(None, "NOT_APPLICABLE", note=why)
            return none, none, None, [("EQUITY_CURRENCY_MISMATCH", why)]
        with localcontext(CONTEXT):
            converted = equity.market_cap * _SCALE[equity.unit] / _SCALE[regs.unit]
        source = SourceRef(equity.cite, "", f"{equity.market_cap:f}")
        listed = Cell(converted, basis="REPORTED", sources=(source,))
        return _sum([(listed, 1), (net_debt, 1)]), listed, "listed", []
    multiple = inputs.brief.ssim_ev_multiple
    if multiple is not None and ssim.value is not None and ssim.value <= 0:
        why = "SSIM EBITDA at or below zero: no EV from the SSIM EV multiple"
        none = Cell(None, "NOT_APPLICABLE", note=why)
        return none, none, None, [("EV_NOT_APPLICABLE", why)]
    if multiple is not None and ssim.value is not None:
        with localcontext(CONTEXT):
            ev = Cell(multiple * ssim.value, basis="CALCULATED", sources=ssim.sources)
        return ev, _sum([(ev, 1), (net_debt, -1)]), "ssim_multiple", []
    why = "no listed equity value and no SSIM EV multiple (or no SSIM EBITDA)"
    none = Cell(None, "NOT_SOURCED", note=why)
    return none, none, None, [("EV_NOT_AVAILABLE", why)]


def _pf_limitations(
    model: CreditModel, regs: Cp1Registers, column: Column
) -> list[tuple[str, str]]:
    found = []
    stray = sorted({a.period_id for a in regs.pro_forma if a.period_id != column.period_id})
    if stray:
        why = f"PF rows for {', '.join(stray)} apply to no LTM column ({column.label} is used)"
        found.append(("PF_ROWS_NOT_APPLIED", why))
    if column.kind != "PF_LTM":
        if not stray:
            why = "no pro forma adjustments for the LTM: every PF figure is the LTM's"
            found.append(("PF_LTM_EQUALS_LTM", why))
        return found
    if not _pf_rows(model, regs, column, "cash_interest_paid"):
        why = "no sourced PF cash interest: PF interest is the LTM's cash interest"
        found.append(("PF_INTEREST_NOT_SOURCED", why))
    return found


def _above_structuring(model: CreditModel, column: Column) -> list[tuple[str, str]]:
    """A negative excluded add-back puts SSIM EBITDA above Structuring EBITDA:
    more likely a CP-1 sign slip than a dis-synergy, so it is named."""
    negative = [
        f"{x.line_id} ({cell(model, x.line_id, column).value})"
        for x in model.lines
        if x.line_id.startswith("addback:") and x.kind == "MEMO"
        if (cell(model, x.line_id, column).value or 0) < 0
    ]
    if not negative:
        return []
    why = f"excluded add-backs below zero: {', '.join(negative)}"
    return [("SSIM_ABOVE_STRUCTURING", why)]


def twelve_months(column: Column | None) -> bool:
    """Whether a debt multiple reads on the column: it spans `LTM_DAYS` (or
    its days are not known)."""
    days = column.days if column is not None else None
    return days is None or LTM_DAYS[0] <= days <= LTM_DAYS[1]


def _annual(column: Column, items: tuple[HouseItem, ...]) -> tuple[HouseItem, ...]:
    """The debt multiples and an EV from the SSIM EV multiple not applicable
    on a column of other than twelve months (a stub year, a short LTM)."""
    if twelve_months(column):
        return items
    why = f"the {column.label} column spans {column.days} days, not twelve months"
    none = Cell(None, "NOT_APPLICABLE", note=why)
    shorter = ("structuring_multiple", "ssim_multiple", "adjusted_leverage")
    return tuple(
        replace(i, cell=none)
        if i.key in shorter or (i.key == "ev" and i.formula.startswith("SSIM"))
        else i
        for i in items
    )


def _negated(c: Cell) -> Cell:
    if c.value is None:
        return c
    return replace(c, value=c.value.copy_negate(), stated=None, note=None)


def house_view(model: CreditModel, regs: Cp1Registers, inputs: HouseInputs) -> HouseView:
    """The house items, the capital structure positions and the EV on the
    snapshot column; none of them without an LTM."""
    column = snapshot_column(model)
    if column is None:
        why = "the Model has no LTM column, so no house view"
        return HouseView(None, (), (), Cell(None, "NOT_APPLICABLE"), None, (("NO_LTM", why),))
    ssim = cell(model, "adjusted_ebitda", column)
    total_debt = cell(model, "total_debt", column)
    interest = _negated(with_pf(model, regs, column, "cash_interest", "cash_interest_paid"))
    structuring = _structuring(model, column, ssim)
    adjusted, debt_limits = _adjusted_debt(regs, column, total_debt, inputs)
    ev, equity, basis, ev_limits = _equity(regs, inputs, cell(model, "net_debt", column), ssim)
    ev_formula = {
        "listed": "listed equity value + net_debt",
        "ssim_multiple": "SSIM EV multiple x SSIM EBITDA",
        None: "listed equity value + net_debt, else SSIM EV multiple x SSIM EBITDA",
    }[basis]
    items = (
        structuring,
        HouseItem(
            "SSIM EBITDA",
            "ssim_ebitda",
            ssim,
            "MONEY",
            "adjusted_ebitda, unrealized add-backs excluded",
            ("adjusted_ebitda",),
        ),
        HouseItem(
            "PF interest",
            "pf_interest",
            interest,
            "MONEY",
            "-(cash_interest + its PF rows)",
            ("cash_interest",),
        ),
        HouseItem(
            "PF interest cover",
            "pf_interest_cover",
            ratio(ssim, interest),
            "MULTIPLE",
            "SSIM EBITDA / PF interest",
            ("adjusted_ebitda", "cash_interest"),
        ),
        HouseItem(
            "Structuring Multiple",
            "structuring_multiple",
            ratio(total_debt, structuring.cell),
            "MULTIPLE",
            "total_debt / Structuring EBITDA",
            ("total_debt", *structuring.components),
        ),
        HouseItem(
            "SSIM Multiple",
            "ssim_multiple",
            ratio(total_debt, ssim),
            "MULTIPLE",
            "total_debt / SSIM EBITDA",
            ("total_debt", "adjusted_ebitda"),
        ),
        HouseItem("EV", "ev", ev, "MONEY", ev_formula, ("net_debt", "adjusted_ebitda")),
        adjusted,
        HouseItem(
            "Adjusted leverage",
            "adjusted_leverage",
            ratio(adjusted.cell, ssim),
            "MULTIPLE",
            "Adjusted debt / SSIM EBITDA",
            (*adjusted.components, "adjusted_ebitda"),
        ),
    )
    if not twelve_months(column):
        why = f"the {column.label} column spans {column.days} days: no debt multiple"
        ev_limits.append(("SNAPSHOT_NOT_TWELVE_MONTHS", why))
        if basis == "ssim_multiple":
            equity = Cell(None, "NOT_APPLICABLE", note=why)
    limits = (
        *_pf_limitations(model, regs, column),
        *ev_limits,
        *debt_limits,
        *_above_structuring(model, column),
    )
    positions = _positions(model, regs, column)
    return HouseView(column, _annual(column, items), positions, equity, basis, limits)


def cumulative(view: HouseView, rank: str) -> Cell:
    """The outstanding of every position ranked at or above `rank`."""
    through = PAYMENT_RANKS[: PAYMENT_RANKS.index(rank) + 1]
    return _sum((p.outstanding, 1) for p in view.positions if p.line.rank in through)


def secured(view: HouseView) -> Cell:
    if not view.positions:
        return Cell(None, "NOT_SOURCED")
    return _sum((p.outstanding, 1) for p in view.positions if p.line.rank in SECURED_RANKS)


def percent_of(part: Cell, whole: Cell) -> Cell:
    """`part / whole x 100`."""
    share = ratio(part, whole)
    if share.value is None:
        return share
    with localcontext(CONTEXT):
        return replace(share, value=share.value * 100)
```

Not verified: independent acceptance, whole06.16 branch gates, later06, live/provider/platform/crash behavior.
