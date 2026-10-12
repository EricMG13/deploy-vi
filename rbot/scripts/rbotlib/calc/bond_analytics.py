"""`rbot calc bond_analytics`: loan 3-year discount margin, bond yields and talk valuation.

Design D16: loans price on margin, floor and OID to a 3-year DM; bonds on coupon and price to
YTW and STW with the call schedule. CP-3 writes the input to `calc/CP-3-bond_analytics.json`
from its tables' input columns and copies the output into `snapshot.instrument_levels`
(`yield_or_dm`) and `cp3.talk_valuation` (`implied_*`); the Report recomputes the same
figures to mark them host-verified (interfaces spec section 11.4).

Input (`--in`), every figure a JSON string or number (read as Decimal, never float):

    {"as_of": "2026-10-02", "reference_rate_pct": "4.20" or null,
     "instruments": [
       {"facility_id": "CEI-TLB", "kind": "loan", "price": "99.5625", "margin_bps": "225",
        "floor_bps": "50", "maturity_date": "2030-02-06"},
       {"facility_id": "CEI-SSN-2032", "kind": "bond", "price": "93.25", "coupon_pct": "6.50",
        "maturity_date": "2032-02-15", "benchmark_yield_pct": null,
        "call_schedule": [{"date": "2027-02-15", "price": "103.25"}]},
       {"facility_id": "NEW-1", "kind": "loan_talk", "talk_low_bps": "300",
        "talk_high_bps": "325", "oid_low": "99.0", "oid_high": "99.5", "floor_bps": "50",
        "maturity_date": "2033-12-15"},
       {"facility_id": "NEW-2", "kind": "bond_talk", "coupon_low_pct": "7.25",
        "coupon_high_pct": "7.50", "oid_low": "98.5", "oid_high": "99.0",
        "maturity_date": "2033-10-15"}]}

Conventions, stated in every output:
- Settlement is the `as_of` date (the level date), with no settlement lag.
- Loan 3Y DM (bps) = margin + floor benefit + (100 - price) / horizon x 100, where the horizon
  is three years, or the years to maturity (actual/365) when shorter, and the floor benefit is
  max(0, floor - reference rate). With a floor above zero and no reference rate the benefit
  is not computed: the DM excludes it and the row says so.
- Bonds: semi-annual coupons dated back from the redemption date, 30/360 (US) accrual, clean
  price plus accrued interest discounted at the yield compounded semi-annually, with the
  first period fractional. YTW is the lowest of the yield to maturity and the yields to each
  call date at its call price; a call price already in force is tested at the next coupon
  date. STW (bps) = YTW less the benchmark yield the input states (none: STW not computed).
- Talk: low = the low margin or coupon at the high OID, mid = the mid margin or coupon at the
  mid OID, high = the high margin or coupon at the low OID.

Pure: no I/O. Results are exact Decimals quantized for display: DMs and spreads to 0.01 bp,
yields to 0.000001%.
"""

from __future__ import annotations

import calendar
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Context, Decimal, InvalidOperation, localcontext
from typing import Any

SCHEMA = "rbot-calc-bond-analytics/1"
CONTEXT = Context(prec=38, rounding=ROUND_HALF_EVEN)
BP = Decimal("0.01")
YIELD_PLACES = Decimal("0.000001")
HUNDRED = Decimal(100)
HORIZON_YEARS = Decimal(3)
DAYS_PER_YEAR = Decimal(365)
PERIOD_DAYS = Decimal(180)
LOW_YIELD, HIGH_YIELD = Decimal("-0.5"), Decimal(5)
TOLERANCE = Decimal("1e-14")
MAX_PRICE = Decimal(200)
MAX_COUPON = Decimal(30)
CALCULATED, NOT_COMPUTABLE = "Calculated", "Not computable"
DM_BASIS, YTW_BASIS = "3Y DM", "YTW"
KINDS = ("loan", "bond", "loan_talk", "bond_talk")
CONVENTIONS = {
    "settlement": "the as_of date, no settlement lag",
    "loan_dm": "margin + max(0, floor - reference rate) + (100 - price) / min(3, years to "
    "maturity, actual/365) x 100, in bps",
    "bond_yield": "semi-annual, 30/360 US accrual, clean price plus accrued, first period "
    "fractional",
    "ytw": "lowest of maturity and each call date at its call price",
    "talk": "low margin at high OID, mid at mid OID, high margin at low OID",
}


class CalcError(ValueError):
    """The input cannot be calculated; the message names the field."""


# --- reading the input -----------------------------------------------------------------------


def figure(raw: object, field: str) -> Decimal:
    """A finite Decimal from a JSON string or number; a float, bool or text is refused."""
    if isinstance(raw, bool) or not isinstance(raw, str | int | Decimal):
        raise CalcError(f"{field}: needs a number as a string or integer, found {raw!r}")
    try:
        value = Decimal(str(raw).strip())
    except InvalidOperation:
        raise CalcError(f"{field}: {raw!r} is not a number") from None
    if not value.is_finite():
        raise CalcError(f"{field}: {raw!r} is not a finite number")
    return value


def optional_figure(item: Mapping[str, Any], key: str, where: str) -> Decimal | None:
    raw = item.get(key)
    return None if raw is None else figure(raw, f"{where}.{key}")


def day(raw: object, field: str) -> date:
    if not isinstance(raw, str):
        raise CalcError(f"{field}: needs an ISO date YYYY-MM-DD, found {raw!r}")
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise CalcError(f"{field}: {raw!r} is not an ISO date YYYY-MM-DD") from None


def _in_range(value: Decimal, low: Decimal, high: Decimal, field: str) -> Decimal:
    if not low <= value <= high:
        raise CalcError(f"{field}: {value} is outside {low} to {high}")
    return value


def _price(item: Mapping[str, Any], key: str, where: str) -> Decimal:
    value = figure(item.get(key), f"{where}.{key}")
    if value <= 0 or value > MAX_PRICE:
        raise CalcError(f"{where}.{key}: a price per 100 must be above 0 and at most {MAX_PRICE}")
    return value


# --- loans -----------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LoanDM:
    dm_bps: Decimal
    horizon_years: Decimal
    floor_benefit_bps: Decimal | None  # None: a floor with no reference rate


def horizon(as_of: date, maturity: date | None) -> Decimal:
    """Three years, or the actual/365 years to maturity when shorter."""
    if maturity is None:
        return HORIZON_YEARS
    if maturity <= as_of:
        raise CalcError(f"maturity_date {maturity} is not after as_of {as_of}")
    years = CONTEXT.divide(Decimal((maturity - as_of).days), DAYS_PER_YEAR)
    return min(HORIZON_YEARS, years)


def floor_benefit(floor_bps: Decimal | None, reference_pct: Decimal | None) -> Decimal | None:
    """max(0, floor - reference rate) in bps; 0 without a floor; None when it needs the rate."""
    if floor_bps is None or floor_bps == 0:
        return Decimal(0)
    if reference_pct is None:
        return None
    return max(Decimal(0), CONTEXT.subtract(floor_bps, CONTEXT.multiply(reference_pct, HUNDRED)))


def loan_dm(margin_bps: Decimal, price: Decimal, years: Decimal, benefit: Decimal | None) -> LoanDM:
    """The 3-year discount margin of a loan at `price` (exact; quantize for display)."""
    with localcontext(CONTEXT):
        discount = (HUNDRED - price) / years * HUNDRED
        dm = margin_bps + (benefit or Decimal(0)) + discount
    return LoanDM(dm, years, benefit)


# --- bonds -----------------------------------------------------------------------------------


def add_months(d: date, months: int, day_of_month: int) -> date:
    """`d` moved by whole months, on `day_of_month` clamped to the month's length."""
    index = d.year * 12 + d.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(day_of_month, calendar.monthrange(year, month)[1]))


def schedule(settle: date, redemption: date) -> tuple[date, list[date]]:
    """The coupon date on or before `settle` and the coupon dates after it up to `redemption`,
    dated back from `redemption` every six months."""
    dates = [redemption]
    while dates[-1] > settle:
        dates.append(add_months(redemption, -6 * len(dates), redemption.day))
    previous = dates.pop()
    return previous, sorted(dates)


def days_360(start: date, end: date) -> int:
    """30/360 US (bond basis) days from `start` to `end`."""
    d1 = min(start.day, 30)
    d2 = 30 if end.day == 31 and d1 == 30 else end.day
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)


@dataclass(frozen=True, slots=True)
class Cashflows:
    accrued: Decimal  # per 100
    first: Decimal  # fraction of a period to the first coupon
    amounts: tuple[Decimal, ...]  # per 100, one per remaining coupon date


def cashflows(coupon_pct: Decimal, settle: date, redemption: date, price: Decimal) -> Cashflows:
    """Coupons and the redemption at `price` (per 100) from `settle` to `redemption`."""
    previous, dates = schedule(settle, redemption)
    with localcontext(CONTEXT):
        elapsed = Decimal(days_360(previous, settle))
        half = coupon_pct / 2
        accrued = half * elapsed / PERIOD_DAYS
        first = (PERIOD_DAYS - elapsed) / PERIOD_DAYS
        amounts = tuple(half + (price if d == dates[-1] else 0) for d in dates)
    return Cashflows(accrued, first, amounts)


def present_value(flows: Cashflows, yield_: Decimal) -> Decimal:
    """Dirty price per 100 at an annual yield compounded semi-annually, in the caller's
    Decimal context (`solve_yield` runs it in `CONTEXT`)."""
    base = 1 + yield_ / 2
    return sum(
        (amount / base ** (flows.first + k) for k, amount in enumerate(flows.amounts)),
        Decimal(0),
    )


def solve_yield(flows: Cashflows, clean: Decimal) -> Decimal | None:
    """The yield at which the cash flows are worth `clean` plus accrued; None outside
    -50% to 500%. Bisection: the value falls as the yield rises, so it cannot diverge."""
    with localcontext(CONTEXT):
        target = clean + flows.accrued
        low, high = LOW_YIELD, HIGH_YIELD
        if not present_value(flows, high) <= target <= present_value(flows, low):
            return None
        while high - low > TOLERANCE:
            middle = (low + high) / 2
            if present_value(flows, middle) > target:
                low = middle
            else:
                high = middle
        return (low + high) / 2


@dataclass(frozen=True, slots=True)
class Call:
    on: date
    price: Decimal


@dataclass(frozen=True, slots=True)
class BondYield:
    ytm: Decimal
    ytw: Decimal
    worst_date: date
    worst_price: Decimal


def redemptions(settle: date, maturity: date, calls: list[Call]) -> list[Call]:
    """Maturity at par and each call tested where it can first apply."""
    _, coupon_dates = schedule(settle, maturity)
    found = [Call(maturity, HUNDRED)]
    for call in calls:
        if call.on <= settle:
            found.append(Call(coupon_dates[0], call.price))
        elif call.on < maturity:
            if call.on not in coupon_dates:
                raise CalcError(f"call date {call.on} is not a coupon date of the bond")
            found.append(Call(call.on, call.price))
    return found


def bond_yield(
    coupon_pct: Decimal, clean: Decimal, settle: date, maturity: date, calls: list[Call]
) -> BondYield | None:
    """YTM and YTW (the lowest yield over maturity and the calls); None when no yield solves."""
    yields = []
    for r in redemptions(settle, maturity, calls):
        solved = solve_yield(cashflows(coupon_pct, settle, r.on, r.price), clean)
        if solved is None:
            return None
        yields.append((solved, r))
    worst, at = min(yields, key=lambda pair: (pair[0], pair[1].on))
    return BondYield(yields[0][0], worst, at.on, at.price)


# --- the command's rows ----------------------------------------------------------------------


def bps(value: Decimal) -> str:
    """Basis points to 0.01, half to even, whatever the caller's Decimal context."""
    return str(value.quantize(BP, context=CONTEXT))


def pct(value: Decimal) -> str:
    """A yield fraction as a percent to 0.000001, half to even."""
    return str(CONTEXT.multiply(value, HUNDRED).quantize(YIELD_PLACES, context=CONTEXT))


@dataclass(frozen=True, slots=True)
class Run:
    as_of: date
    reference_pct: Decimal | None


def _maturity(item: Mapping[str, Any], where: str) -> date:
    return day(item.get("maturity_date"), f"{where}.maturity_date")


def _optional_maturity(item: Mapping[str, Any], where: str) -> date | None:
    return None if item.get("maturity_date") is None else _maturity(item, where)


def _margin_floor(item: Mapping[str, Any], key: str, where: str) -> Decimal | None:
    value = optional_figure(item, key, where)
    if value is not None and value < 0:
        raise CalcError(f"{where}.{key}: {value} is negative")
    return value


def _loan(item: Mapping[str, Any], where: str, run: Run) -> dict[str, Any]:
    price = _price(item, "price", where)
    margin = _margin_floor(item, "margin_bps", where)
    if margin is None:
        raise CalcError(f"{where}.margin_bps: required for a loan")
    floor = _margin_floor(item, "floor_bps", where)
    years = horizon(run.as_of, _optional_maturity(item, where))
    result = loan_dm(margin, price, years, floor_benefit(floor, run.reference_pct))
    note = "" if result.floor_benefit_bps is not None else "floor benefit not computed: no "
    note += "reference rate; the DM excludes it" if note else ""
    return {
        "facility_id": item["facility_id"],
        "metric_basis": DM_BASIS,
        "price": str(price),
        "yield_or_dm": bps(result.dm_bps),
        "horizon_years": str(result.horizon_years.quantize(YIELD_PLACES, context=CONTEXT)),
        "floor_benefit_bps": None
        if result.floor_benefit_bps is None
        else bps(result.floor_benefit_bps),
        "status": CALCULATED,
        "note": note or "—",
    }


def _calls(item: Mapping[str, Any], where: str) -> list[Call]:
    raw = item.get("call_schedule") or []
    if not isinstance(raw, list):
        raise CalcError(f"{where}.call_schedule: needs a list of {{date, price}}")
    calls = []
    for n, entry in enumerate(raw):
        at = f"{where}.call_schedule[{n}]"
        if not isinstance(entry, dict):
            raise CalcError(f"{at}: needs an object with date and price")
        calls.append(Call(day(entry.get("date"), f"{at}.date"), _price(entry, "price", at)))
    return calls


def _coupon(item: Mapping[str, Any], key: str, where: str) -> Decimal:
    return _in_range(figure(item.get(key), f"{where}.{key}"), Decimal(0), MAX_COUPON, where)


def _bond(item: Mapping[str, Any], where: str, run: Run) -> dict[str, Any]:
    price = _price(item, "price", where)
    coupon = _coupon(item, "coupon_pct", where)
    maturity = _maturity(item, where)
    if maturity <= run.as_of:
        raise CalcError(f"{where}.maturity_date: {maturity} is not after as_of {run.as_of}")
    benchmark = optional_figure(item, "benchmark_yield_pct", where)
    solved = bond_yield(coupon, price, run.as_of, maturity, _calls(item, where))
    row: dict[str, Any] = {"facility_id": item["facility_id"], "metric_basis": YTW_BASIS}
    row["price"] = str(price)
    if solved is None:
        return row | {"yield_or_dm": None, "status": NOT_COMPUTABLE, "note": "no yield solves"}
    stw = None
    if benchmark is not None:
        with localcontext(CONTEXT):
            stw = (solved.ytw * HUNDRED - benchmark) * HUNDRED
    return row | {
        "yield_or_dm": pct(solved.ytw),
        "ytm_pct": pct(solved.ytm),
        "worst_date": solved.worst_date.isoformat(),
        "worst_price": str(solved.worst_price),
        "stw_bps": None if stw is None else bps(stw),
        "status": CALCULATED,
        "note": "—" if stw is not None else "STW not computed: no benchmark yield",
    }


def _range(item: Mapping[str, Any], low: str, high: str, where: str) -> tuple[Decimal, Decimal]:
    first, last = figure(item.get(low), f"{where}.{low}"), figure(item.get(high), f"{where}.{high}")
    if first > last:
        raise CalcError(f"{where}: {low} {first} is above {high} {last}")
    return first, last


def _talk_row(
    item: Mapping[str, Any], talk: tuple[Decimal, Decimal], oid: tuple[Decimal, Decimal]
) -> dict[str, Any]:
    with localcontext(CONTEXT):
        mid, oid_mid = (talk[0] + talk[1]) / 2, (oid[0] + oid[1]) / 2
    return {
        "facility_id": item["facility_id"],
        "talk_low": str(talk[0]),
        "talk_mid": str(mid),
        "talk_high": str(talk[1]),
        "oid": str(oid_mid),
        "oid_low": str(oid[0]),
        "oid_high": str(oid[1]),
    }


def _loan_talk(item: Mapping[str, Any], where: str, run: Run) -> dict[str, Any]:
    talk = _range(item, "talk_low_bps", "talk_high_bps", where)
    oid = _range(item, "oid_low", "oid_high", where)
    for value, key in ((oid[0], "oid_low"), (oid[1], "oid_high")):
        _price({key: value}, key, where)
    years = horizon(run.as_of, _optional_maturity(item, where))
    benefit = floor_benefit(_margin_floor(item, "floor_bps", where), run.reference_pct)
    row = _talk_row(item, talk, oid)
    margins = (talk[0], Decimal(row["talk_mid"]), talk[1])
    prices = (oid[1], Decimal(row["oid"]), oid[0])
    low, mid, high = (
        loan_dm(m, p, years, benefit).dm_bps for m, p in zip(margins, prices, strict=True)
    )
    note = "—" if benefit is not None else "floor benefit not computed: no reference rate"
    return row | {
        "metric_basis": DM_BASIS,
        "implied_low": bps(low),
        "implied_mid": bps(mid),
        "implied_high": bps(high),
        "note": note,
    }


def _bond_talk(item: Mapping[str, Any], where: str, run: Run) -> dict[str, Any]:
    talk = _range(item, "coupon_low_pct", "coupon_high_pct", where)
    oid = _range(item, "oid_low", "oid_high", where)
    for value, key in ((oid[0], "oid_low"), (oid[1], "oid_high")):
        _price({key: value}, key, where)
    for value, key in ((talk[0], "coupon_low_pct"), (talk[1], "coupon_high_pct")):
        _in_range(value, Decimal(0), MAX_COUPON, f"{where}.{key}")
    maturity = _maturity(item, where)
    if maturity <= run.as_of:
        raise CalcError(f"{where}.maturity_date: {maturity} is not after as_of {run.as_of}")
    row = _talk_row(item, talk, oid)
    coupons = (talk[0], Decimal(row["talk_mid"]), talk[1])
    prices = (oid[1], Decimal(row["oid"]), oid[0])
    solved = [
        bond_yield(c, p, run.as_of, maturity, []) for c, p in zip(coupons, prices, strict=True)
    ]
    if any(s is None for s in solved):
        raise CalcError(f"{where}: no yield solves at the talk and OID given")
    low, mid, high = (pct(s.ytm) for s in solved if s is not None)
    return row | {
        "metric_basis": YTW_BASIS,
        "implied_low": low,
        "implied_mid": mid,
        "implied_high": high,
        "note": "—",
    }


_LEVELS: dict[str, Callable[[Mapping[str, Any], str, Run], dict[str, Any]]] = {
    "loan": _loan,
    "bond": _bond,
}
_TALK: dict[str, Callable[[Mapping[str, Any], str, Run], dict[str, Any]]] = {
    "loan_talk": _loan_talk,
    "bond_talk": _bond_talk,
}


def _instrument(item: object, n: int, run: Run) -> tuple[str, dict[str, Any]]:
    where = f"instruments[{n}]"
    if not isinstance(item, dict):
        raise CalcError(f"{where}: needs an object")
    if not isinstance(item.get("facility_id"), str) or not item["facility_id"]:
        raise CalcError(f"{where}.facility_id: required")
    kind = item.get("kind")
    if kind not in KINDS:
        raise CalcError(f"{where}.kind: {kind!r} is not one of {', '.join(KINDS)}")
    if kind in _LEVELS:
        return "levels", _LEVELS[kind](item, where, run)
    return "talk", _TALK[kind](item, where, run)


def compute(data: object) -> dict[str, Any]:
    """The calculator's output for one input document; CalcError names the bad field."""
    if not isinstance(data, dict):
        raise CalcError("the input must be a JSON object")
    run = Run(day(data.get("as_of"), "as_of"), optional_figure(data, "reference_rate_pct", "input"))
    items = data.get("instruments")
    if not isinstance(items, list) or not items:
        raise CalcError("instruments: needs a non-empty list")
    out: dict[str, Any] = {"schema": SCHEMA, "as_of": run.as_of.isoformat()}
    out |= {"reference_rate_pct": None if run.reference_pct is None else str(run.reference_pct)}
    out |= {"conventions": CONVENTIONS, "levels": [], "talk": []}
    for n, item in enumerate(items):
        table, row = _instrument(item, n, run)
        out[table].append(row)
    return out


LEVEL_COLUMNS = ("facility_id", "metric_basis", "price", "yield_or_dm", "status", "note")
TALK_COLUMNS = (
    "facility_id",
    "talk_low",
    "talk_mid",
    "talk_high",
    "oid",
    "metric_basis",
    "implied_low",
    "implied_mid",
    "implied_high",
    "note",
)


def markdown(result: Mapping[str, Any]) -> str:
    """The output as the owning tables' columns, one Markdown table each."""
    lines: list[str] = []
    for title, columns, rows in (
        ("snapshot.instrument_levels", LEVEL_COLUMNS, result["levels"]),
        ("cp3.talk_valuation", TALK_COLUMNS, result["talk"]),
    ):
        if not rows:
            continue
        lines += [f"<!-- {title} (calculator columns) -->", "| " + " | ".join(columns) + " |"]
        lines.append("|" + "---|" * len(columns))
        for row in rows:
            cells = ["—" if row.get(c) is None else str(row[c]) for c in columns]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)
