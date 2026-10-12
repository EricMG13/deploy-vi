"""CP-1's Model-input tables read into the credit model's typed registers
(`rbotlib.model.registers`).

Port of caos `caos/methodology/model_inputs.py` at `5c3cd52f`, CP-1 part only
(CP-2G's drivers arrive with the projection port), reading
`rbotlib.handoff.Table`s keyed by table id through `rbotlib.model.reader`,
which refuses with `ModelInputError` naming table, row and column.

Every enumerated column is closed (`docs/model/enums.md`) except
`facility_type`, `currency` and a KPI's `unit`, which read in upper case
(`DEBT ADJUSTMENT` is the one facility type the Model acts on). A table the
Handoff does not carry reads as no rows, except the period register.
Refused, besides what `reader` refuses: a null in a required column; two
currencies or two units across the period register; one register id twice in
one period; two periods for one fiscal quarter, YTD or year; a fiscal year
without a four-digit year, outside 1900-2200 or more than a year from its end
date's year; more than `MAX_PERIODS` periods; a period naming a component
twice or nesting components past `MAX_NESTING` (or in a cycle); a start after
its end; a day count that is not end - start + 1 or not positive; a negative
facility carrying value other than a `DEBT ADJUSTMENT` row's; a negative
commitment, drawing, RCF commitment or RCF drawing; a pro forma row
without a figure; a row of any register naming a period the period register
lacks; and a pro forma row on a period that is not an LTM period, or naming
a metric a pro forma row cannot adjust (`PF_METRICS`, or `facility:<id>` of a
facility the register has). An account metric no Model line reads is not
refused (CP-1 also feeds other modules): `rbotlib.model.run` names it. A rate
term written in the wrong unit (a spread or floor with `%` or not whole basis
points, a fixed coupon outside 0.5-30 percent) is kept, the row flagged
`terms_out_of_range`; the rate columns are absent from an older register and
read as `NOT_STATED`.

Pure: no I/O.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from decimal import Decimal
from typing import Any

from rbotlib.handoff import Table
from rbotlib.model.reader import (
    FIRST_YEAR,
    LAST_YEAR,
    ModelInputError,
    Row,
    date_cell,
    decimal,
    distinct,
    enum,
    ids,
    integer,
    optional,
    read,
    required_decimal,
    required_text,
    source,
    text,
)
from rbotlib.model.registers import (
    ADDBACK_CLASSIFICATIONS,
    CALCULATION_STATUSES,
    FACILITY_TYPES,
    KPI_VALUE_TYPES,
    LEASE_CLASSIFICATIONS,
    PERIOD_TYPES,
    PERIOD_UNITS,
    PF_CLASSIFICATIONS,
    RATE_TYPES,
    REALIZATION_STATUSES,
    REFERENCE_RATES,
    SECURED_STATUSES,
    SEGMENT_TYPES,
    SENIORITIES,
    AccountRow,
    AddbackRow,
    Cp1Registers,
    FacilityRow,
    KpiRow,
    PeriodRow,
    PfAdjustmentRow,
    SegmentRow,
    fiscal_year_number,
)

PERIODS = "cp1.model_period_register"
ACCOUNTS = "cp1.model_account_register"
ADDBACKS = "cp1.adjusted_ebitda_bridge"
SEGMENTS = "cp1.segment_revenue_schedule"
KPIS = "cp1.operating_kpi_schedule"
FACILITIES = "cp1.debt_facility_register"
PRO_FORMA = "cp1.pro_forma_adjustment_register"

_OPEN: frozenset[str] = frozenset()
_MAX_DAYS = (date(LAST_YEAR, 12, 31) - date(FIRST_YEAR, 1, 1)).days + 1
MAX_PERIODS = 200
MAX_NESTING = 4
_COUPON_RANGE = (Decimal("0.5"), Decimal(30))
_BPS_TERMS = ("spread_bps", "floor_bps")
_DEBT_ADJUSTMENT = "DEBT ADJUSTMENT"
_RCF_BALANCES = frozenset({"rcf_drawn", "rcf_commitment"})
# What a pro forma row adjusts (spec §6.5; `layout._PF_PLACES`), besides `facility:<id>`.
PF_METRICS = frozenset(
    {"revenue", "ebitda", "adjusted_ebitda", "cash_interest_paid", "cash_and_equivalents"}
    | {"total_debt"}
)


def _rate_term(row: Row, column: str, vocabulary: frozenset[str]) -> str:
    if optional(row, column) is None:
        return "NOT_STATED"
    return enum(row, column, vocabulary)


def _priority(row: Row) -> int:
    priority = integer(row, "display_priority")
    if priority is None:
        raise row.refuse("display_priority", "required, found null")
    return priority


def _span(row: Row) -> tuple[date | None, date | None, int | None]:
    start, end = date_cell(row, "start_date"), date_cell(row, "end_date")
    days = integer(row, "day_count")
    if start is not None and end is not None:
        if start > end:
            raise row.refuse("start_date", "after end_date")
        actual = (end - start).days + 1
        if days is None:
            days = actual
        elif days != actual:
            raise row.refuse("day_count", f"{days} is not end - start + 1")
    if days is not None and not 1 <= days <= _MAX_DAYS:
        raise row.refuse("day_count", f"{days} is out of range")
    return start, end, days


def _components(row: Row) -> tuple[str, ...]:
    found = ids(row, "component_period_ids")
    if len(set(found)) != len(found):
        raise row.refuse("component_period_ids", "names a component twice")
    return found


def _fiscal_year(row: Row, end: date | None) -> str:
    value = text(row, "fiscal_year")
    year = fiscal_year_number(value)
    if year is None or not FIRST_YEAR <= year <= LAST_YEAR:
        raise row.refuse("fiscal_year", f"{value!r} has no four-digit year in 1900-2200")
    if end is not None and abs(year - end.year) > 1:
        raise row.refuse("fiscal_year", f"{value!r} is more than a year from end_date")
    return value


_PERIOD_COLUMNS = frozenset(
    {
        "period_id",
        "fiscal_year",
        "fiscal_quarter",
        "period_type",
        "start_date",
        "end_date",
        "day_count",
        "currency",
        "unit",
        "component_period_ids",
    }
)


def _period(row: Row) -> PeriodRow:
    start, end, days = _span(row)
    return PeriodRow(
        period_id=required_text(row, "period_id"),
        fiscal_year=_fiscal_year(row, end),
        fiscal_quarter=optional(row, "fiscal_quarter"),
        period_type=enum(row, "period_type", PERIOD_TYPES),
        start_date=None if start is None else start.isoformat(),
        end_date=None if end is None else end.isoformat(),
        day_count=days,
        currency=enum(row, "currency", _OPEN, closed=False),
        unit=enum(row, "unit", PERIOD_UNITS),
        component_period_ids=_components(row),
    )


_ACCOUNT_COLUMNS = frozenset(
    {"metric_id", "period_id", "value", "calculation_status", "source_id", "source_locator"}
)


def _account(row: Row) -> AccountRow:
    metric_id = required_text(row, "metric_id")
    value = decimal(row, "value")
    if metric_id in _RCF_BALANCES and value is not None and value < 0:
        raise row.refuse("value", f"{metric_id} is a balance and cannot be negative")
    return AccountRow(
        metric_id=metric_id,
        period_id=required_text(row, "period_id"),
        value=value,
        calculation_status=enum(row, "calculation_status", CALCULATION_STATUSES),
        source=source(row, "value"),
    )


_ADDBACK_COLUMNS = frozenset(
    {
        "addback_id",
        "addback_label",
        "addback_classification",
        "realization_status",
        "display_priority",
        "period_id",
        "value",
        "source_id",
        "source_locator",
    }
)


def _addback(row: Row) -> AddbackRow:
    return AddbackRow(
        addback_id=required_text(row, "addback_id"),
        label=required_text(row, "addback_label"),
        classification=enum(row, "addback_classification", ADDBACK_CLASSIFICATIONS),
        realization_status=enum(row, "realization_status", REALIZATION_STATUSES),
        display_priority=_priority(row),
        period_id=required_text(row, "period_id"),
        value=decimal(row, "value"),
        source=source(row, "value"),
    )


_SEGMENT_COLUMNS = frozenset(
    {
        "segment_id",
        "segment_name",
        "segment_type",
        "display_priority",
        "period_id",
        "revenue",
        "source_id",
        "source_locator",
    }
)


def _segment(row: Row) -> SegmentRow:
    return SegmentRow(
        segment_id=required_text(row, "segment_id"),
        segment_name=required_text(row, "segment_name"),
        segment_type=enum(row, "segment_type", SEGMENT_TYPES),
        display_priority=_priority(row),
        period_id=required_text(row, "period_id"),
        revenue=decimal(row, "revenue"),
        source=source(row, "revenue"),
    )


_KPI_COLUMNS = frozenset(
    {
        "kpi_id",
        "kpi_label",
        "display_priority",
        "period_id",
        "value",
        "unit",
        "value_type",
        "source_id",
        "source_locator",
    }
)


def _kpi(row: Row) -> KpiRow:
    return KpiRow(
        kpi_id=required_text(row, "kpi_id"),
        kpi_label=required_text(row, "kpi_label"),
        display_priority=_priority(row),
        period_id=required_text(row, "period_id"),
        value=decimal(row, "value"),
        unit=enum(row, "unit", _OPEN, closed=False),
        value_type=enum(row, "value_type", KPI_VALUE_TYPES),
        source=source(row, "value"),
    )


# Not the rate and amortisation columns: an older register has none.
_FACILITY_COLUMNS = frozenset(
    {
        "facility_id",
        "facility_name",
        "period_id",
        "facility_type",
        "currency",
        "carrying_value",
        "drawn_amount",
        "commitment",
        "secured_status",
        "seniority",
        "margin_or_coupon",
        "maturity_date",
        "lease_classification",
        "source_id",
        "source_locator",
    }
)


def _non_negative(row: Row, column: str) -> Decimal | None:
    value = decimal(row, column)
    if value is not None and value < 0:
        raise row.refuse(column, "cannot be negative")
    return value


def _out_of_range(row: Row) -> bool:
    for column in _BPS_TERMS:
        value = decimal(row, column)
        if value is None:
            continue
        if "%" in text(row, column) or value != value.to_integral_value():
            return True
    coupon = decimal(row, "fixed_rate")
    low, high = _COUPON_RANGE
    return coupon is not None and not low <= coupon <= high


def _facility(row: Row) -> FacilityRow:
    facility_type = enum(row, "facility_type", FACILITY_TYPES, closed=False)
    carrying = decimal(row, "carrying_value")
    if carrying is not None and carrying < 0 and facility_type != _DEBT_ADJUSTMENT:
        raise row.refuse("carrying_value", "negative outside a DEBT ADJUSTMENT row")
    return FacilityRow(
        facility_id=required_text(row, "facility_id"),
        facility_name=required_text(row, "facility_name"),
        period_id=required_text(row, "period_id"),
        facility_type=facility_type,
        currency=enum(row, "currency", _OPEN, closed=False),
        carrying_value=carrying,
        commitment=_non_negative(row, "commitment"),
        drawn_amount=_non_negative(row, "drawn_amount"),
        secured_status=enum(row, "secured_status", SECURED_STATUSES),
        seniority=enum(row, "seniority", SENIORITIES),
        lease_classification=enum(row, "lease_classification", LEASE_CLASSIFICATIONS),
        maturity_date=optional(row, "maturity_date"),
        margin_or_coupon=text(row, "margin_or_coupon"),
        rate_type=_rate_term(row, "rate_type", RATE_TYPES),
        reference_rate=_rate_term(row, "reference_rate", REFERENCE_RATES),
        spread_bps=decimal(row, "spread_bps"),
        floor_bps=decimal(row, "floor_bps"),
        fixed_rate=decimal(row, "fixed_rate"),
        annual_amortisation=decimal(row, "annual_amortisation"),
        source=source(row, "carrying_value"),
        terms_out_of_range=_out_of_range(row),
    )


_PRO_FORMA_COLUMNS = frozenset(
    {
        "adjustment_id",
        "label",
        "period_id",
        "effective_date",
        "classification",
        "metric_id",
        "value",
        "source_id",
        "source_locator",
    }
)


def _pro_forma(row: Row) -> PfAdjustmentRow:
    return PfAdjustmentRow(
        adjustment_id=required_text(row, "adjustment_id"),
        label=required_text(row, "label"),
        period_id=required_text(row, "period_id"),
        classification=enum(row, "classification", PF_CLASSIFICATIONS),
        metric_id=required_text(row, "metric_id"),
        value=required_decimal(row, "value"),
        source=source(row, "value"),
    )


def _one(values: Sequence[str], column: str) -> str:
    found = sorted(set(values))
    if len(found) != 1:
        raise ModelInputError(f"{PERIODS} column {column}: states {', '.join(found)}; need one")
    return found[0]


def _fiscal_period(period: PeriodRow) -> tuple[str, int | None, str] | None:
    year = fiscal_year_number(period.fiscal_year)
    if period.period_type == "FY":
        return "FY", year, ""
    if period.period_type in {"QUARTER", "YTD"} and period.fiscal_quarter:
        return period.period_type, year, period.fiscal_quarter.upper().removeprefix("Q")
    return None


def _one_each(periods: tuple[PeriodRow, ...]) -> tuple[PeriodRow, ...]:
    seen: set[tuple[str, int | None, str]] = set()
    for number, period in enumerate(periods, 1):
        covered = _fiscal_period(period)
        if covered is None:
            continue
        if covered in seen:
            raise ModelInputError(f"{PERIODS} row {number}: a second period for {covered}")
        seen.add(covered)
    return periods


def _depth(
    period_id: str,
    components: Mapping[str, tuple[str, ...]],
    depths: dict[str, int],
    open_ids: frozenset[str],
) -> int:
    if period_id in depths:
        return depths[period_id]
    if period_id in open_ids:
        raise ModelInputError(f"{PERIODS} period {period_id}: components form a cycle")
    inner = open_ids | {period_id}
    parts = components.get(period_id, ())
    depth = max((_depth(p, components, depths, inner) + 1 for p in parts), default=0)
    if depth > MAX_NESTING:
        raise ModelInputError(f"{PERIODS} period {period_id}: nested past {MAX_NESTING}")
    depths[period_id] = depth
    return depth


def _bounded(periods: tuple[PeriodRow, ...]) -> tuple[PeriodRow, ...]:
    if len(periods) > MAX_PERIODS:
        raise ModelInputError(f"{PERIODS}: more than {MAX_PERIODS} periods")
    components = {p.period_id: p.component_period_ids for p in periods}
    depths: dict[str, int] = {}
    for period in periods:
        _depth(period.period_id, components, depths, frozenset())
    return periods


def _on_known_periods(table_id: str, found: Sequence[Any], known: frozenset[str]) -> None:
    for number, row in enumerate(found, 1):
        if row.period_id not in known:
            where = f"{table_id} row {number} column period_id"
            raise ModelInputError(f"{where}: {row.period_id} is not in {PERIODS}")


def _pro_forma_placed(regs: Cp1Registers) -> None:
    """Every pro forma row sits on an LTM period and adjusts a metric the
    Model places, so none is dropped without a word."""
    ltm = {p.period_id for p in regs.periods if p.period_type == "LTM"}
    facilities = {f.facility_id for f in regs.facilities}
    for number, row in enumerate(regs.pro_forma, 1):
        where = f"{PRO_FORMA} row {number} column"
        if row.period_id not in ltm:
            raise ModelInputError(f"{where} period_id: {row.period_id} is not an LTM period")
        facility = row.metric_id.startswith("facility:")
        if facility and row.metric_id.removeprefix("facility:") not in facilities:
            raise ModelInputError(f"{where} metric_id: {row.metric_id!r} names no facility")
        if not facility and row.metric_id not in PF_METRICS:
            why = "is not a metric a pro forma row adjusts"
            raise ModelInputError(f"{where} metric_id: {row.metric_id!r} {why}")


def _placed(regs: Cp1Registers) -> Cp1Registers:
    """`regs`, refused when a row names a period the register lacks or a
    pro forma row cannot be placed."""
    known = frozenset(p.period_id for p in regs.periods)
    for table_id, found in (
        (ACCOUNTS, regs.accounts),
        (ADDBACKS, regs.addbacks),
        (SEGMENTS, regs.segments),
        (KPIS, regs.kpis),
        (FACILITIES, regs.facilities),
        (PRO_FORMA, regs.pro_forma),
    ):
        _on_known_periods(table_id, found, known)
    _pro_forma_placed(regs)
    return regs


def cp1_registers(tables: Mapping[str, Table]) -> Cp1Registers:
    """CP-1's period, account, add-back, segment, KPI, debt and pro forma
    registers as typed rows, in the one currency and unit of the period
    register."""
    periods = _bounded(
        distinct(
            PERIODS,
            _one_each(read(tables, PERIODS, _PERIOD_COLUMNS, _period)),
            lambda p: (p.period_id,),
        )
    )
    if not periods:
        raise ModelInputError(f"{PERIODS}: no rows; the Model needs at least one period")
    return _placed(_registers(tables, periods))


def _registers(tables: Mapping[str, Table], periods: tuple[PeriodRow, ...]) -> Cp1Registers:
    return Cp1Registers(
        periods=periods,
        accounts=distinct(
            ACCOUNTS,
            read(tables, ACCOUNTS, _ACCOUNT_COLUMNS, _account),
            lambda a: (a.metric_id, a.period_id),
        ),
        addbacks=distinct(
            ADDBACKS,
            read(tables, ADDBACKS, _ADDBACK_COLUMNS, _addback),
            lambda b: (b.addback_id, b.period_id),
        ),
        segments=distinct(
            SEGMENTS,
            read(tables, SEGMENTS, _SEGMENT_COLUMNS, _segment),
            lambda g: (g.segment_id, g.period_id),
        ),
        kpis=distinct(
            KPIS, read(tables, KPIS, _KPI_COLUMNS, _kpi), lambda k: (k.kpi_id, k.period_id)
        ),
        facilities=distinct(
            FACILITIES,
            read(tables, FACILITIES, _FACILITY_COLUMNS, _facility),
            lambda f: (f.facility_id, f.period_id),
        ),
        pro_forma=distinct(
            PRO_FORMA,
            read(tables, PRO_FORMA, _PRO_FORMA_COLUMNS, _pro_forma),
            lambda a: (a.adjustment_id, a.period_id),
        ),
        currency=_one([p.currency for p in periods], "currency"),
        unit=_one([p.unit for p in periods], "unit"),
    )
