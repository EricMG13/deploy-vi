"""`rbot calc bond_analytics` (interfaces spec §12.5 row 05: ten hand-computed instruments).

Every expected figure below is computed independently of the module: a loan DM by the formula
in the docstring by hand, and a bond yield on a coupon date from the closed-form annuity price
(`annuity_price`, `annuity_yield` here), which has no fractional period and no accrued interest.
The one off-coupon case (CZR 6.50% 2032 at 93.25) was checked with a separate float
implementation; FINRA's own yield for the same bond is the corpus test below.
"""

from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any

import pytest

from rbotlib.calc import bond_analytics as ba
from rbotlib.calc.bond_analytics import compute
from rbotlib.cli import main

AS_OF = "2026-10-02"
COUPON_DAY = "2026-08-15"
CALLS = [
    {"date": "2027-02-15", "price": "104"},
    {"date": "2028-02-15", "price": "102"},
    {"date": "2029-02-15", "price": "100"},
]


def annuity_price(coupon: Decimal, yield_: Decimal, periods: int, redemption: Decimal) -> Decimal:
    """Price per 100 on a coupon date: coupons plus redemption at a semi-annual yield."""
    with localcontext() as ctx:
        ctx.prec = 40
        rate = yield_ / 2
        v = 1 / (1 + rate)
        return coupon / 2 * (1 - v**periods) / rate + redemption * v**periods


def one(instrument: dict[str, Any], **top: str) -> dict[str, Any]:
    result = compute({"as_of": top.get("as_of", AS_OF), "instruments": [instrument], **top})
    rows: list[dict[str, Any]] = result["levels"] + result["talk"]
    return rows[0]


def loan(price: str, margin: str, **extra: str) -> dict[str, Any]:
    return {"facility_id": "L", "kind": "loan", "price": price, "margin_bps": margin, **extra}


def bond(price: str | Decimal, coupon: str, maturity: str, **extra: object) -> dict[str, Any]:
    item = {"facility_id": "B", "kind": "bond", "price": str(price), "coupon_pct": coupon}
    return item | {"maturity_date": maturity, **extra}


KNOWN = [
    # 1. CZR TL B at its Bloomberg mid: 225 + (100 - 99.5625) / 3 x 100 = 239.583...; floor 50
    #    with no reference rate in the pack: benefit not computed.
    (loan("99.5625", "225", floor_bps="50", maturity_date="2030-02-06"), {}, "239.58"),
    # 2. The same with a 4.20% reference rate: the 0.50% floor is out of the money.
    (loan("99.5625", "225", floor_bps="50"), {"reference_rate_pct": "4.20"}, "239.58"),
    # 3. Floor in the money: 300 + (100 - 50) + (100 - 98) / 3 x 100 = 416.666...
    (loan("98", "300", floor_bps="100"), {"reference_rate_pct": "0.50"}, "416.67"),
    # 4. Under three years to maturity: 547 days, 250 + 1 / (547 / 365) x 100 = 316.7276...
    (loan("99", "250", maturity_date="2028-04-01"), {}, "316.73"),
    # 5. A par bond on a coupon date yields its coupon.
    (bond("100", "6.50", "2032-02-15"), {"as_of": COUPON_DAY}, "6.500000"),
    # 6. The closed-form price at 8% (11 periods) solves back to 8%.
    (
        bond(annuity_price(Decimal("6.5"), Decimal("0.08"), 11, Decimal(100)), "6.5", "2032-02-15"),
        {"as_of": COUPON_DAY},
        "8.000000",
    ),
    # 7. Premium callable at 104: to 2027-02-15 at 104 = 7.6923%, 2028 at 102 = 6.4507%,
    #    2029 at 100 = 6.2470%, maturity = 6.9497%: the worst is the 2029 call.
    (bond("104", "8", "2031-02-15", call_schedule=CALLS), {"as_of": COUPON_DAY}, "6.246999"),
    # 8. CZR 6.50% senior secured notes due 2032 at the Bloomberg mid 93.25 on 2026-10-02
    #    (accrued 47 days, 30/360): a discount bond, so the worst is maturity.
    (
        bond(
            "93.25", "6.50", "2032-02-15", call_schedule=[{"date": "2027-02-15", "price": "103.25"}]
        ),
        {},
        "8.071057",
    ),
]


@pytest.mark.parametrize(("instrument", "top", "expected"), KNOWN)
def test_bond_analytics_known_values(
    instrument: dict[str, Any], top: dict[str, Any], expected: str
) -> None:
    row = one(instrument, **top)
    assert row["status"] == "Calculated"
    assert abs(Decimal(row["yield_or_dm"]) - Decimal(expected)) <= Decimal("0.0001")


def test_known_talk_values_for_a_loan_and_a_bond() -> None:
    """9. NEW-1 at SOFR + 300-325, OID 99.0-99.5: 300 + 50/3, 312.5 + 75/3, 325 + 100/3.
    10. A bond at 7.25-7.50% coupon talk, OID 98.5-99.0, 14 periods on a coupon date."""
    talk = {"facility_id": "NEW-1", "kind": "loan_talk", "talk_low_bps": "300"}
    talk |= {"talk_high_bps": "325", "oid_low": "99.0", "oid_high": "99.5", "floor_bps": "50"}
    row = one(talk | {"maturity_date": "2033-12-15"})
    assert (row["implied_low"], row["implied_mid"], row["implied_high"]) == (
        "316.67",
        "337.50",
        "358.33",
    )
    assert (row["talk_mid"], row["oid"], row["metric_basis"]) == ("312.5", "99.25", "3Y DM")
    assert row["note"].startswith("floor benefit not computed")
    hy = {"facility_id": "NEW-2", "kind": "bond_talk", "coupon_low_pct": "7.25"}
    hy |= {"coupon_high_pct": "7.50", "oid_low": "98.5", "oid_high": "99.0"}
    row = one(hy | {"maturity_date": "2033-10-15"}, as_of="2026-10-15")
    assert (row["implied_low"], row["implied_mid"], row["implied_high"]) == (
        "7.435829",
        "7.608625",
        "7.781967",
    )


def test_spread_to_worst_needs_a_benchmark() -> None:
    row = one(bond("100", "6.50", "2032-02-15", benchmark_yield_pct="4.10"), as_of=COUPON_DAY)
    assert (row["yield_or_dm"], row["stw_bps"], row["note"]) == ("6.500000", "240.00", "—")
    row = one(bond("100", "6.50", "2032-02-15"), as_of=COUPON_DAY)
    assert row["stw_bps"] is None and row["note"] == "STW not computed: no benchmark yield"


def test_a_call_in_force_is_tested_at_the_next_coupon_date() -> None:
    row = one(
        bond("106", "8", "2031-02-15", call_schedule=[{"date": "2026-02-15", "price": "104"}])
    )
    assert (row["worst_date"], row["worst_price"]) == ("2027-02-15", "104")
    assert Decimal(row["yield_or_dm"]) < Decimal(row["ytm_pct"])


def test_the_floor_benefit_is_reported() -> None:
    row = one(loan("100", "300", floor_bps="100"), reference_rate_pct="0.25")
    assert (row["yield_or_dm"], row["floor_benefit_bps"]) == ("375.00", "75.00")
    row = one(loan("100", "300"))
    assert (row["floor_benefit_bps"], row["note"]) == ("0.00", "—")


def test_a_price_no_yield_reaches_is_not_computable() -> None:
    row = one(bond("200", "0", "2027-02-15"))
    assert (row["status"], row["yield_or_dm"]) == ("Not computable", None)


def test_rbot_calc_prints_the_tables_and_writes_the_result(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "in.json"
    document = {"as_of": AS_OF, "instruments": [loan("99.5625", "225", floor_bps="50")]}
    source.write_text(json.dumps(document | {"reference_rate_pct": 4.2}), encoding="utf-8")
    out = tmp_path / "out.json"
    assert main(["calc", "bond_analytics", "--in", str(source), "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "| L | 3Y DM | 99.5625 | 239.58 | Calculated | — |" in printed
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["schema"] == ba.SCHEMA and written["reference_rate_pct"] == "4.2"


def test_rbot_calc_exits_1_naming_the_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "in.json"
    source.write_text('{"as_of": "2026-10-02", "instruments": [{"kind": "loan"}]}', "utf-8")
    assert main(["calc", "bond_analytics", "--in", str(source)]) == 1
    assert "instruments[0].facility_id: required" in capsys.readouterr().out
    source.write_text("{", "utf-8")
    assert main(["calc", "bond_analytics", "--in", str(source)]) == 1
    assert "not valid JSON" in capsys.readouterr().out
