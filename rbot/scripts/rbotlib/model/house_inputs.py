"""What the house view reads besides CP-1's registers (spec §6.6).

From CP-1: `cp1.instrument_identity` (identifiers and ratings per facility),
`cp1.equity_value` (one listed equity value at most) and
`cp1.entity_profile` (its currency and unit must be the period register's).
From CP-1D, when its Handoff exists: `cp1d.addback_assessment` (the house
realization status and verdict per add-back and period) and
`cp1d.debt_like_items`. From the Run Brief: the SSIM EV multiple, the
Primary flag and the new tranches' ids. Every refusal is a
`ModelInputError` naming table, row and column.

`effective_registers` applies D19's house view to the add-backs: the latest LTM
CP-1D judgment replaces CP-1 statuses throughout (owner ruling 2026-10-12);
a `Rejected` verdict counts as `UNREALIZED` (spec §6.5).

Pure: no I/O.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from decimal import Decimal

from rbotlib.handoff import Table
from rbotlib.model.reader import (
    ModelInputError,
    Row,
    cite,
    date_cell,
    decimal,
    distinct,
    enum,
    optional,
    read,
    required_decimal,
    required_text,
    rows,
)
from rbotlib.model.registers import REALIZATION_STATUSES, Cp1Registers, PeriodRow

IDENTITY = "cp1.instrument_identity"
EQUITY = "cp1.equity_value"
ENTITY = "cp1.entity_profile"
ASSESSMENT = "cp1d.addback_assessment"
DEBT_LIKE = "cp1d.debt_like_items"
RUN_HEADER = "snapshot.run_header"
TRANCHES = "snapshot.transaction_summary"
VERDICTS = frozenset({"Supported", "Challenged", "Rejected"})
TREATMENTS = frozenset({"Debt-like", "Not debt-like", "Unclear"})
UNITS = frozenset({"UNITS", "THOUSANDS", "MILLIONS"})
_YES_NO = frozenset({"Yes", "No"})
_SLUG = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class Identity:
    facility_id: str
    instrument_name: str
    bloomberg_id: str | None
    ratings: str | None  # "Moody's / S&P / Fitch", a missing agency as —
    cite: str


@dataclass(frozen=True, slots=True)
class EquityValue:
    market_cap: Decimal
    value_date: str
    currency: str
    unit: str
    cite: str


@dataclass(frozen=True, slots=True)
class AddbackAssessment:
    addback_id: str
    period_id: str
    house_realization_status: str
    verdict: str
    cite: str


@dataclass(frozen=True, slots=True)
class DebtLikeItem:
    item: str
    amount: Decimal
    currency: str
    unit: str
    period_id: str
    treatment: str
    basis: str
    cite: str


def debt_like_key(item: DebtLikeItem) -> str:
    """The item's memo line id: `debt_like:` and its name in lower case,
    every run of other characters one `_`."""
    return f"debt_like:{_SLUG.sub('_', item.item.casefold()).strip('_')}"


@dataclass(frozen=True, slots=True)
class BriefFields:
    run_id: str
    ssim_ev_multiple: Decimal | None
    primary: bool
    tranche_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class HouseInputs:
    identities: Mapping[str, Identity]
    equity: EquityValue | None
    assessments: tuple[AddbackAssessment, ...]
    debt_like: tuple[DebtLikeItem, ...]
    brief: BriefFields


def _identity(row: Row) -> Identity:
    agencies = [optional(row, f"rating_{a}") for a in ("moodys", "sp", "fitch")]
    ratings = " / ".join(a or "\N{EM DASH}" for a in agencies) if any(agencies) else None
    return Identity(
        facility_id=required_text(row, "facility_id"),
        instrument_name=required_text(row, "instrument_name"),
        bloomberg_id=optional(row, "bloomberg_id"),
        ratings=ratings,
        cite=cite(row, "cite"),
    )


def identities(tables: Mapping[str, Table]) -> dict[str, Identity]:
    columns = frozenset({"facility_id", "instrument_name", "cite"})
    found = distinct(IDENTITY, read(tables, IDENTITY, columns, _identity), _facility_key)
    return {i.facility_id: i for i in found}


def _facility_key(identity: Identity) -> tuple[str, ...]:
    return (identity.facility_id,)


def _equity(row: Row) -> EquityValue:
    day = date_cell(row, "value_date")
    if day is None:
        raise row.refuse("value_date", "required, found null")
    return EquityValue(
        market_cap=_positive(row, "market_cap"),
        value_date=day.isoformat(),
        currency=enum(row, "currency", frozenset(), closed=False),
        unit=enum(row, "unit", UNITS),
        cite=cite(row, "cite"),
    )


def _positive(row: Row, column: str) -> Decimal:
    value = required_decimal(row, column)
    if value <= 0:
        raise row.refuse(column, f"{value} is not above zero")
    return value


def equity_value(tables: Mapping[str, Table]) -> EquityValue | None:
    columns = frozenset({"market_cap", "value_date", "currency", "unit", "cite"})
    found = read(tables, EQUITY, columns, _equity)
    if len(found) > 1:
        raise ModelInputError(f"{EQUITY} row 2: one listed equity value per run")
    return found[0] if found else None


def check_entity_profile(tables: Mapping[str, Table], regs: Cp1Registers) -> None:
    """Refused where an entity row reports in another currency or unit than
    the period register's."""
    columns = frozenset({"reporting_currency", "reporting_unit"})
    for row in rows(tables, ENTITY, columns):
        currency = enum(row, "reporting_currency", frozenset(), closed=False)
        if currency != regs.currency:
            raise row.refuse("reporting_currency", f"{currency} is not {regs.currency}")
        unit = enum(row, "reporting_unit", UNITS)
        if unit != regs.unit:
            raise row.refuse("reporting_unit", f"{unit} is not {regs.unit}")


def _assessment(row: Row) -> AddbackAssessment:
    return AddbackAssessment(
        addback_id=required_text(row, "addback_id"),
        period_id=required_text(row, "period_id"),
        house_realization_status=enum(row, "house_realization_status", REALIZATION_STATUSES),
        verdict=enum(row, "verdict", VERDICTS),
        cite=cite(row, "cite"),
    )


def assessments(tables: Mapping[str, Table]) -> tuple[AddbackAssessment, ...]:
    columns = frozenset({"addback_id", "period_id", "house_realization_status", "verdict", "cite"})
    found = read(tables, ASSESSMENT, columns, _assessment)
    return distinct(ASSESSMENT, found, lambda a: (a.addback_id, a.period_id))


def _debt_like(row: Row, regs: Cp1Registers) -> DebtLikeItem:
    currency = enum(row, "currency", frozenset(), closed=False)
    if currency != regs.currency:
        raise row.refuse("currency", f"{currency} is not the run's {regs.currency}")
    unit = enum(row, "unit", UNITS)
    if unit != regs.unit:
        raise row.refuse("unit", f"{unit} is not the run's {regs.unit}")
    return DebtLikeItem(
        item=required_text(row, "item"),
        amount=required_decimal(row, "amount"),
        currency=currency,
        unit=unit,
        period_id=required_text(row, "period_id"),
        treatment=enum(row, "treatment", TREATMENTS),
        basis=required_text(row, "basis"),
        cite=cite(row, "cite"),
    )


def debt_like_items(tables: Mapping[str, Table], regs: Cp1Registers) -> tuple[DebtLikeItem, ...]:
    columns = frozenset({"item", "amount", "currency", "unit", "period_id", "treatment", "cite"})
    columns |= {"basis"}
    found = read(tables, DEBT_LIKE, columns, lambda row: _debt_like(row, regs))
    ends = {p.period_id: p.end_date or p.period_id for p in regs.periods}
    names: dict[str, str] = {}
    for number, d in enumerate(found, 1):
        where = f"{DEBT_LIKE} row {number}"
        if d.period_id not in ends:
            raise ModelInputError(f"{where} column period_id: {d.period_id} is not a CP-1 period")
        first = names.setdefault(debt_like_key(d), d.item)
        if first != d.item:
            raise ModelInputError(f"{where} column item: {d.item!r} and {first!r} are one line")
    return distinct(DEBT_LIKE, found, lambda d: (debt_like_key(d), ends[d.period_id]))


def brief_fields(front_matter: Mapping[str, str], tables: Mapping[str, Table]) -> BriefFields:
    """The Run Brief fields the Model reads: `ssim_ev_multiple_x` and
    `primary` from `snapshot.run_header`, the tranche ids from
    `snapshot.transaction_summary`."""
    columns = frozenset({"run_id", "primary", "ssim_ev_multiple_x"})
    header = rows(tables, RUN_HEADER, columns)
    if len(header) != 1:
        raise ModelInputError(f"{RUN_HEADER}: needs exactly one row, found {len(header)}")
    row = header[0]
    tranches = rows(tables, TRANCHES, frozenset({"tranche_id"}))
    return BriefFields(
        run_id=front_matter.get("run_id") or required_text(row, "run_id"),
        ssim_ev_multiple=None
        if decimal(row, "ssim_ev_multiple_x") is None
        else _positive(row, "ssim_ev_multiple_x"),
        primary=enum(row, "primary", _YES_NO) == "Yes",
        tranche_ids=frozenset(required_text(t, "tranche_id") for t in tranches),
    )


def _status(a: AddbackAssessment) -> str:
    return "UNREALIZED" if a.verdict == "Rejected" else a.house_realization_status


def _assessment_periods(
    regs: Cp1Registers, found: tuple[AddbackAssessment, ...]
) -> dict[str, PeriodRow]:
    known = {b.addback_id for b in regs.addbacks}
    periods = {p.period_id: p for p in regs.periods}
    for number, judgment in enumerate(found, 1):
        where = f"{ASSESSMENT} row {number} column"
        if judgment.addback_id not in known:
            why = f"{judgment.addback_id} is not a CP-1 add-back"
            raise ModelInputError(f"{where} addback_id: {why}")
        if judgment.period_id not in periods:
            raise ModelInputError(f"{where} period_id: {judgment.period_id} is not a CP-1 period")
        period = periods[judgment.period_id]
        if period.period_type == "LTM" and period.end_date is None:
            raise ModelInputError(f"{where} period_id: {judgment.period_id} has no end date")
    return periods


def _ltm_judgments(regs: Cp1Registers, found: tuple[AddbackAssessment, ...]) -> dict[str, str]:
    periods = _assessment_periods(regs, found)
    newest = max(
        (p.end_date for p in periods.values() if p.period_type == "LTM" and p.end_date is not None),
        default=None,
    )
    latest: dict[str, str] = {}
    for judgment in found:
        period = periods[judgment.period_id]
        if period.period_type != "LTM" or period.end_date != newest:
            continue
        key, status = judgment.addback_id, _status(judgment)
        if key in latest and latest[key] != status:
            raise ModelInputError(f"{ASSESSMENT}: {key}: contradictory LTM judgments on {newest}")
        latest[key] = status
    return latest


def effective_registers(regs: Cp1Registers, found: tuple[AddbackAssessment, ...]) -> Cp1Registers:
    """Owner ruling 2026-10-12: the newest dated registered LTM judgment controls each add-back
    throughout, in both directions; Rejected is UNREALIZED. Without an LTM
    judgment retain exact-period statuses and conservative exclusions, with
    mixed statuses named by assessment_limitations. Contradictions refuse."""
    latest = _ltm_judgments(regs, found)
    status = {(a.addback_id, a.period_id): _status(a) for a in found}
    excluding: dict[str, str] = {}
    for a in found:
        if _status(a) != "REALIZED":
            excluding.setdefault(a.addback_id, _status(a))
    addbacks = tuple(
        replace(
            b,
            realization_status=latest.get(
                b.addback_id,
                status.get(
                    (b.addback_id, b.period_id), excluding.get(b.addback_id, b.realization_status)
                ),
            ),
        )
        for b in regs.addbacks
    )
    return replace(regs, addbacks=addbacks)


def assessment_limitations(
    regs: Cp1Registers, found: tuple[AddbackAssessment, ...]
) -> list[tuple[str, str]]:
    """`ADDBACK_STATUS_MIXED` for an add-back CP-1D assesses `REALIZED` that
    another period's row (in `regs`, the effective registers) still
    excludes. Without a judgment for the newest registered LTM, exact-period
    fallback leaves a source gap; caos conservatively excludes mixed statuses."""
    limits = []
    for a in found:
        if _status(a) != "REALIZED":
            continue
        others = sorted(
            b.period_id
            for b in regs.addbacks
            if b.addback_id == a.addback_id and b.realization_status != "REALIZED"
        )
        if others:
            why = (
                f"{a.addback_id}: CP-1D assesses REALIZED for {a.period_id} but "
                f"{', '.join(others)} stays unrealized; the add-back is excluded on every column"
            )
            limits.append(("ADDBACK_STATUS_MIXED", why))
    return limits
