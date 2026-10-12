"""`rbot calc bond_analytics`: input validation and properties (money code).

Invalid input names the field that is wrong; the properties hold for every price, margin,
coupon and yield Hypothesis draws, and each is checked against an independent statement
(the DM formula, the closed-form annuity price) rather than the module's own output.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.calc import bond_analytics as ba
from rbotlib.calc.bond_analytics import CalcError, compute
from test_bond_analytics import AS_OF, CALLS, annuity_price, bond, loan, one


@pytest.mark.parametrize(
    ("instrument", "message"),
    [
        (loan("0", "225"), "instruments[0].price: a price per 100 must be above 0"),
        (loan("201", "225"), "instruments[0].price: a price per 100 must be above 0"),
        (loan("99", "-1"), "instruments[0].margin_bps: -1 is negative"),
        ({"facility_id": "L", "kind": "loan", "price": "99"}, "margin_bps: required for a loan"),
        (loan("99", "225", maturity_date="2026-10-01"), "is not after as_of"),
        (loan("99", "225", floor_bps="x"), "instruments[0].floor_bps: 'x' is not a number"),
        ({"facility_id": "L", "kind": "loan", "price": True}, "instruments[0].price: needs a"),
        (loan("NaN", "225"), "is not a finite number"),
        (bond("99", "31", "2030-01-01"), "is outside 0 to 30"),
        (bond("99", "5", "2026-01-01"), "is not after as_of"),
        (bond("99", "5", "1-1-2030"), "is not an ISO date"),
        (bond("99", "5", "2030-01-15", call_schedule=CALLS), "is not a coupon date"),
        (bond("99", "5", "2030-01-15", call_schedule={"d": 1}), "needs a list"),
        (bond("99", "5", "2030-01-15", call_schedule=[1]), "needs an object with date"),
        ({"facility_id": "", "kind": "loan"}, "instruments[0].facility_id: required"),
        ({"facility_id": "X", "kind": "swap"}, "kind: 'swap' is not one of"),
        ("loan", "instruments[0]: needs an object"),
    ],
)
def test_invalid_input_names_the_field(instrument: object, message: str) -> None:
    with pytest.raises(CalcError, match=message.replace("[", r"\[").replace("]", r"\]")):
        compute({"as_of": AS_OF, "instruments": [instrument]})


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ([], "the input must be a JSON object"),
        ({"as_of": AS_OF, "instruments": []}, "instruments: needs a non-empty list"),
        ({"as_of": None, "instruments": [1]}, "as_of: needs an ISO date"),
        ({"as_of": AS_OF, "reference_rate_pct": 1.5, "instruments": [1]}, "needs a number"),
    ],
)
def test_invalid_documents_are_refused(data: object, message: str) -> None:
    with pytest.raises(CalcError, match=message):
        compute(data)


def test_talk_ranges_must_be_ordered() -> None:
    talk = {"facility_id": "N", "kind": "loan_talk", "talk_low_bps": "325"}
    talk |= {"talk_high_bps": "300", "oid_low": "99", "oid_high": "99.5"}
    with pytest.raises(CalcError, match="talk_low_bps 325 is above talk_high_bps 300"):
        compute({"as_of": AS_OF, "instruments": [talk]})
    hy = {"facility_id": "N", "kind": "bond_talk", "coupon_low_pct": "7", "coupon_high_pct": "8"}
    hy |= {"oid_low": "0", "oid_high": "99", "maturity_date": "2033-10-15"}
    with pytest.raises(CalcError, match="oid_low: a price per 100"):
        compute({"as_of": AS_OF, "instruments": [hy]})


PRICES = st.decimals(min_value=Decimal(50), max_value=Decimal(150), places=3)
MARGINS = st.decimals(min_value=Decimal(0), max_value=Decimal(1500), places=1)
YIELDS = st.decimals(min_value=Decimal("0.001"), max_value=Decimal("0.4"), places=4)
COUPONS = st.decimals(min_value=Decimal(0), max_value=Decimal(15), places=3)


@settings(deadline=None)
@given(PRICES, PRICES, MARGINS)
def test_a_lower_loan_price_never_lowers_the_dm(a: Decimal, b: Decimal, margin: Decimal) -> None:
    low, high = sorted((a, b))
    years = Decimal(3)
    assert (
        ba.loan_dm(margin, low, years, Decimal(0)).dm_bps
        >= ba.loan_dm(margin, high, years, Decimal(0)).dm_bps
    )


@settings(deadline=None)
@given(MARGINS, st.decimals(min_value=0, max_value=500, places=0), st.decimals(0, 10, places=2))
def test_floor_benefit_is_never_negative_and_needs_the_rate(
    margin: Decimal, floor: Decimal, rate: Decimal
) -> None:
    benefit = ba.floor_benefit(floor, rate)
    assert benefit is not None and benefit >= 0
    assert ba.floor_benefit(floor, None) == (Decimal(0) if floor == 0 else None)
    assert ba.loan_dm(margin, Decimal(100), Decimal(3), benefit).dm_bps == margin + benefit


@settings(max_examples=40, deadline=None)
@given(COUPONS, YIELDS, st.integers(min_value=1, max_value=30))
def test_a_coupon_date_price_solves_back_to_its_yield(
    coupon: Decimal, yield_: Decimal, periods: int
) -> None:
    price = annuity_price(coupon, yield_, periods, Decimal(100))
    settle = date(2026, 8, 15)
    maturity = ba.add_months(settle, 6 * periods, 15)
    solved = ba.solve_yield(ba.cashflows(coupon, settle, maturity, Decimal(100)), price)
    assert solved is not None and abs(solved - yield_) < Decimal("1e-8")


@settings(max_examples=30, deadline=None)
@given(st.decimals(min_value=Decimal(85), max_value=Decimal(115), places=2), COUPONS)
def test_yield_to_worst_never_exceeds_yield_to_maturity(price: Decimal, coupon: Decimal) -> None:
    calls = [ba.Call(date(2028, 2, 15), Decimal("102")), ba.Call(date(2029, 2, 15), Decimal(100))]
    solved = ba.bond_yield(coupon, price, date(2026, 10, 2), date(2032, 2, 15), calls)
    assert solved is not None and solved.ytw <= solved.ytm


@settings(deadline=None)
@given(MARGINS, MARGINS, PRICES, PRICES)
def test_talk_implied_values_are_ordered(
    m1: Decimal, m2: Decimal, p1: Decimal, p2: Decimal
) -> None:
    low, high = sorted((m1, m2))
    cheap, rich = sorted((p1, p2))
    talk = {"facility_id": "N", "kind": "loan_talk", "talk_low_bps": str(low)}
    talk |= {"talk_high_bps": str(high), "oid_low": str(cheap), "oid_high": str(rich)}
    row = one(talk)
    assert (
        Decimal(row["implied_low"]) <= Decimal(row["implied_mid"]) <= Decimal(row["implied_high"])
    )
