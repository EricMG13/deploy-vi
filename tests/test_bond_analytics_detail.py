"""`bond_analytics` in detail: the whole output for the CZR instruments, boundaries and messages.

`tests/fixtures/calc/CP-3-bond_analytics.json` is the input CP-3's fixture Handoff was written
from (the Bloomberg mids of `czr-2026q2-primary` and the new tranche's talk); the `.out.json`
and `.md` beside it are the calculator's output for it. Its yields agree with an independent
float implementation to 0.0001 bp (8.071057% for the 6.50% 2032 notes, 9.333010% for the 6.00%
2032 notes) and its DMs are the formula by hand (225 + 0.437 / 3 x 100 = 239.5667).
"""

from __future__ import annotations

import json
from datetime import date
from decimal import ROUND_DOWN, Decimal, localcontext
from pathlib import Path
from typing import Any

import pytest

from conftest import FIXTURES
from rbotlib.calc import bond_analytics as ba
from rbotlib.calc.bond_analytics import CalcError, compute, markdown
from rbotlib.cli import main

CALC = FIXTURES / "calc"
AS_OF = "2026-10-02"


def _input() -> dict[str, Any]:
    data: dict[str, Any] = json.loads((CALC / "CP-3-bond_analytics.json").read_text("utf-8"))
    return data


def test_the_czr_output_is_the_committed_one() -> None:
    result = compute(_input())
    assert result == json.loads((CALC / "CP-3-bond_analytics.out.json").read_text("utf-8"))
    assert markdown(result) == (CALC / "CP-3-bond_analytics.md").read_text("utf-8")


def test_markdown_prints_a_talk_table_without_levels() -> None:
    data = _input()
    data["instruments"] = [i for i in data["instruments"] if i["kind"] == "loan_talk"]
    text = markdown(compute(data))
    assert text.startswith("<!-- cp3.talk_valuation (calculator columns) -->\n| facility_id |")
    assert "| NEW-1 | 300 | 312.5 | 325 | 99.25 | 3Y DM | 316.67 | 337.50 | 358.33 |" in text


@pytest.mark.parametrize(
    ("start", "end", "days"),
    [
        (date(2026, 1, 31), date(2026, 3, 15), 45),  # day 31 counts as 30
        (date(2026, 1, 30), date(2026, 3, 31), 60),  # end 31 after a start on the 30th
        (date(2026, 1, 30), date(2026, 3, 15), 45),
        (date(2026, 1, 15), date(2026, 3, 31), 76),  # end 31 after a start before the 30th
        (date(2025, 1, 15), date(2026, 1, 15), 360),
    ],
)
def test_days_360_follows_the_bond_basis(start: date, end: date, days: int) -> None:
    assert ba.days_360(start, end) == days


def test_boundaries_that_are_valid() -> None:
    assert one_loan("0.5", "10")["status"] == "Calculated"  # a price above 0, the least margin
    row = one(
        {"facility_id": "B", "kind": "bond", "price": "100", "coupon_pct": "30"}
        | {"maturity_date": "2027-08-15"},
        as_of="2026-08-15",
    )
    assert row["yield_or_dm"] == "30.000000"  # the highest coupon accepted


def test_a_call_on_the_settlement_date_is_in_force_and_one_at_maturity_is_ignored() -> None:
    bond: dict[str, Any] = {"facility_id": "B", "kind": "bond", "price": "106", "coupon_pct": "8"}
    bond |= {"maturity_date": "2031-02-15", "call_schedule": [{"date": AS_OF, "price": "104"}]}
    row = one(bond)
    assert (row["worst_date"], row["worst_price"]) == ("2027-02-15", "104")
    bond["call_schedule"] = [{"date": "2031-02-15", "price": "99"}]
    assert one(bond)["worst_date"] == "2031-02-15" and one(bond)["worst_price"] == "100"


def test_a_tie_goes_to_the_earliest_date() -> None:
    bond: dict[str, Any] = {"facility_id": "B", "kind": "bond", "price": "100", "coupon_pct": "8"}
    bond |= {
        "maturity_date": "2031-02-15",
        "call_schedule": [{"date": "2028-02-15", "price": "100"}],
    }
    row = one(bond, as_of="2026-08-15")
    assert (row["yield_or_dm"], row["worst_date"]) == ("8.000000", "2028-02-15")


def test_talk_uses_the_horizon_and_the_floor_benefit() -> None:
    talk = {"facility_id": "N", "kind": "loan_talk", "talk_low_bps": "300", "talk_high_bps": "300"}
    talk |= {"oid_low": "99", "oid_high": "99", "floor_bps": "100", "maturity_date": "2028-04-01"}
    row = one(talk, reference_rate_pct="0.25")
    # 300 + (100 - 25) + 1 / (547 / 365) x 100 = 441.7276...
    assert (row["implied_low"], row["implied_mid"], row["implied_high"]) == ("441.73",) * 3
    assert row["note"] == "—"


def one(instrument: dict[str, Any], **top: str) -> dict[str, Any]:
    result = compute({"as_of": top.pop("as_of", AS_OF), "instruments": [instrument], **top})
    rows: list[dict[str, Any]] = result["levels"] + result["talk"]
    return rows[0]


def one_loan(price: str, margin: str) -> dict[str, Any]:
    return one({"facility_id": "L", "kind": "loan", "price": price, "margin_bps": margin})


def _talk(**fields: str) -> dict[str, Any]:
    talk = {"facility_id": "N", "kind": "loan_talk", "talk_low_bps": "300", "talk_high_bps": "325"}
    return talk | {"oid_low": "99", "oid_high": "99.5"} | fields


def _hy(**fields: str) -> dict[str, Any]:
    hy = {"facility_id": "H", "kind": "bond_talk", "coupon_low_pct": "7", "coupon_high_pct": "8"}
    return hy | {"oid_low": "98", "oid_high": "99", "maturity_date": "2033-10-15"} | fields


def _bond(**fields: object) -> dict[str, Any]:
    bond = {"facility_id": "B", "kind": "bond", "price": "99", "coupon_pct": "5"}
    return bond | {"maturity_date": "2030-01-15"} | fields


MESSAGES = [
    (_talk(oid_high="300"), "instruments[0].oid_high: a price per 100 must be above 0"),
    (_hy(coupon_low_pct="9"), "instruments[0]: coupon_low_pct 9 is above coupon_high_pct 8"),
    (_hy(oid_low="99.5"), "instruments[0]: oid_low 99.5 is above oid_high 99"),
    (_hy(coupon_high_pct="40"), "instruments[0].coupon_high_pct: 40 is outside 0 to 30"),
    (
        {"facility_id": "X", "kind": "swap"},
        "instruments[0].kind: 'swap' is not one of loan, bond, loan_talk, bond_talk",
    ),
    (_talk(oid_low="0"), "instruments[0].oid_low: a price per 100 must be above 0 and at most 200"),
    (_talk(talk_low_bps="x"), "instruments[0].talk_low_bps: 'x' is not a number"),
    (_talk(oid_high="y"), "instruments[0].oid_high: 'y' is not a number"),
    (_talk(floor_bps="-5"), "instruments[0].floor_bps: -5 is negative"),
    (_talk(maturity_date="soon"), "instruments[0].maturity_date: 'soon' is not an ISO date"),
    (_talk(maturity_date=AS_OF), "maturity_date 2026-10-02 is not after as_of 2026-10-02"),
    (_hy(coupon_low_pct="-1"), "instruments[0].coupon_low_pct: -1 is outside 0 to 30"),
    (_hy(oid_high="300"), "instruments[0].oid_high: a price per 100 must be above 0"),
    (_hy(maturity_date=AS_OF), "instruments[0].maturity_date: 2026-10-02 is not after as_of"),
    (_hy(maturity_date="x"), "instruments[0].maturity_date: 'x' is not an ISO date"),
    (
        _hy(
            oid_low="200",
            oid_high="200",
            coupon_low_pct="0",
            coupon_high_pct="0",
            maturity_date="2027-01-15",
        ),
        "instruments[0]: no yield solves at the talk and OID given",
    ),
    (_bond(price="-1"), "instruments[0].price: a price per 100 must be above 0"),
    (_bond(coupon_pct="40"), "instruments[0]: 40 is outside 0 to 30"),
    (_bond(coupon_pct="z"), "instruments[0].coupon_pct: 'z' is not a number"),
    (_bond(maturity_date=AS_OF), "instruments[0].maturity_date: 2026-10-02 is not after as_of"),
    (_bond(maturity_date=None), "instruments[0].maturity_date: needs an ISO date"),
    (_bond(benchmark_yield_pct="b"), "instruments[0].benchmark_yield_pct: 'b' is not a number"),
    (
        _bond(call_schedule=[{"date": "x", "price": "100"}]),
        "instruments[0].call_schedule[0].date: 'x' is not an ISO date",
    ),
    (
        _bond(call_schedule=[{"date": "2028-01-15", "price": "0"}]),
        "instruments[0].call_schedule[0].price: a price per 100 must be above 0",
    ),
    (
        {
            "facility_id": "L",
            "kind": "loan",
            "price": "99",
            "margin_bps": "100",
            "maturity_date": "x",
        },
        "instruments[0].maturity_date: 'x' is not an ISO date",
    ),
]


@pytest.mark.parametrize(("instrument", "message"), MESSAGES)
def test_messages_name_the_field_exactly(instrument: dict[str, Any], message: str) -> None:
    with pytest.raises(CalcError) as caught:
        compute({"as_of": AS_OF, "instruments": [instrument]})
    assert str(caught.value).startswith(message)


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ([], "the input must be a JSON object"),
        ({"as_of": AS_OF, "instruments": []}, "instruments: needs a non-empty list"),
        (
            {"as_of": AS_OF, "reference_rate_pct": "r", "instruments": [1]},
            "input.reference_rate_pct: 'r' is not a number",
        ),
    ],
)
def test_document_messages_are_exact(data: object, message: str) -> None:
    with pytest.raises(CalcError) as caught:
        compute(data)
    assert str(caught.value) == message


def test_a_loan_without_a_maturity_runs_three_years() -> None:
    assert one_loan("97", "100")["horizon_years"] == "3.000000"
    assert ba.horizon(date(2026, 1, 1), None) == Decimal(3)


def test_a_bond_talk_row_and_a_bond_no_yield_reaches() -> None:
    row = one(_hy(), as_of="2026-10-15")
    assert {k: row[k] for k in ("metric_basis", "note", "talk_mid", "oid")} == {
        "metric_basis": "YTW",
        "note": "—",
        "talk_mid": "7.5",
        "oid": "98.5",
    }
    result = compute(
        {
            "as_of": AS_OF,
            "instruments": [_bond(price="200", coupon_pct="0", maturity_date="2027-02-15")],
        }
    )
    assert result["levels"] == [
        {
            "facility_id": "B",
            "metric_basis": "YTW",
            "price": "200",
            "yield_or_dm": None,
            "status": "Not computable",
            "note": "no yield solves",
        }
    ]
    assert "| B | YTW | 200 | — | Not computable | no yield solves |" in markdown(result)


def test_results_do_not_depend_on_the_callers_decimal_context() -> None:
    short = {"facility_id": "S", "kind": "loan", "price": "99", "margin_bps": "250"}
    short |= {"floor_bps": "100", "maturity_date": "2028-04-01"}
    stw = {"facility_id": "T", "kind": "bond", "price": "93.25", "coupon_pct": "6.50"}
    stw |= {"maturity_date": "2032-02-15", "benchmark_yield_pct": "-1234.567891"}
    deep = {"facility_id": "D", "kind": "loan", "price": "50", "margin_bps": "225"}
    talk = {"facility_id": "N", "kind": "loan_talk", "talk_low_bps": "300.123457"}
    talk |= {"talk_high_bps": "325.123456", "oid_low": "99.0000001", "oid_high": "99.5"}
    data = _input()
    added = [short, stw, deep, talk]
    data |= {"reference_rate_pct": "0.2512345", "instruments": [*data["instruments"], *added]}
    expected = compute(data)
    with localcontext() as caller:
        caller.prec, caller.rounding = 6, ROUND_DOWN
        assert compute(data) == expected


# --- the up-front review of Plan 05 (money): every case below failed before its fix ------------


def test_an_in_force_call_on_a_coupon_date_settlement_is_tested_at_the_next_coupon() -> None:
    """I4 (mutant `schedule` 4, `>=`): settlement on a coupon date, a call already in force."""
    bond: dict[str, Any] = {"facility_id": "B", "kind": "bond", "price": "103", "coupon_pct": "8"}
    bond |= {
        "maturity_date": "2031-02-15",
        "call_schedule": [{"date": "2026-02-15", "price": "102"}],
    }
    row = one(bond, as_of="2026-08-15")
    assert (row["yield_or_dm"], row["worst_date"], row["status"]) == (
        "5.825243",
        "2027-02-15",
        "Calculated",
    )


@pytest.mark.parametrize(
    ("kind", "extra", "message"),
    [
        ("loan", {"floor_pct": "1.00"}, "instruments[0].floor_pct: unknown field for a loan"),
        ("bond", {"calls": []}, "instruments[0].calls: unknown field for a bond"),
        ("loan_talk", {"oid": "99"}, "instruments[0].oid: unknown field for a loan_talk"),
        ("bond_talk", {"coupon": "7"}, "instruments[0].coupon: unknown field for a bond_talk"),
        ("bond", {"margin_bps": "450"}, "instruments[0].margin_bps: a bond has a fixed coupon"),
        ("bond", {"floor_bps": "50"}, "a floating-rate note is not priced as a bond"),
        ("bond_talk", {"spread_bps": "450"}, "instruments[0].spread_bps: a bond_talk has a fixed"),
    ],
)
def test_a_key_the_kind_does_not_read_is_refused_by_name(
    kind: str, extra: dict[str, str], message: str
) -> None:
    base = {"loan": one_loan_item(), "bond": _bond(), "loan_talk": _talk(), "bond_talk": _hy()}
    with pytest.raises(CalcError) as caught:
        compute({"as_of": AS_OF, "instruments": [base[kind] | extra]})
    assert message in str(caught.value)


def one_loan_item() -> dict[str, Any]:
    return {"facility_id": "L", "kind": "loan", "price": "98", "margin_bps": "300"}


def test_an_unknown_top_level_key_is_refused() -> None:
    with pytest.raises(CalcError, match=r"input.reference_rate: unknown field \(reads as_of"):
        compute({"as_of": AS_OF, "reference_rate": "0.5", "instruments": [one_loan_item()]})


@pytest.mark.parametrize(
    ("instrument", "top", "message"),
    [
        ({"margin_bps": "3.25"}, {}, "instruments[0].margin_bps: 3.25 is below 10 bps"),
        ({"floor_bps": "0.5"}, {}, "instruments[0].floor_bps: 0.5 is below 5 bps"),
        ({}, {"reference_rate_pct": "0.042"}, "input.reference_rate_pct: 0.042 is below 0.2"),
    ],
)
def test_a_slip_of_unit_is_refused(
    instrument: dict[str, str], top: dict[str, str], message: str
) -> None:
    with pytest.raises(CalcError) as caught:
        compute({"as_of": AS_OF, "instruments": [one_loan_item() | instrument], **top})
    assert message in str(caught.value)


@pytest.mark.parametrize("value", ["-50", "3.25"])
def test_a_negative_or_slipped_talk_margin_is_refused(value: str) -> None:
    with pytest.raises(CalcError, match=f"instruments.0..talk_low_bps: {value} "):
        compute({"as_of": AS_OF, "instruments": [_talk(talk_low_bps=value)]})


def test_a_floor_of_zero_and_a_reference_rate_of_zero_are_valid() -> None:
    row = one(one_loan_item() | {"floor_bps": "0"}, reference_rate_pct="0")
    assert row["floor_benefit_bps"] == "0.00"


@pytest.mark.parametrize(
    ("start", "end", "days"),
    [
        (date(2026, 2, 28), date(2026, 8, 31), 180),  # a last day of February counts as the 30th
        (date(2026, 8, 31), date(2027, 2, 28), 178),  # the end of February is not moved alone
        (date(2027, 2, 28), date(2028, 2, 29), 360),  # both are February month-ends
        (date(2028, 2, 29), date(2028, 8, 31), 180),
        (date(2026, 2, 27), date(2026, 8, 30), 183),  # not a month-end: unchanged
    ],
)
def test_days_360_has_the_february_month_end_rule(start: date, end: date, days: int) -> None:
    assert ba.days_360(start, end) == days


def test_a_bond_maturing_on_the_last_day_of_february_has_month_end_coupons() -> None:
    previous, dates = ba.schedule(date(2026, 8, 1), date(2030, 2, 28))
    assert (previous, dates[:2]) == (date(2026, 2, 28), [date(2026, 8, 31), date(2027, 2, 28)])
    assert ba.schedule(date(2026, 3, 1), date(2032, 2, 29))[1][0] == date(2026, 8, 31)
    assert ba.schedule(date(2026, 3, 1), date(2030, 8, 30))[1][0] == date(2026, 8, 30)


def test_accrued_never_exceeds_a_coupon_and_the_first_period_is_never_negative() -> None:
    """M1: maturity 2030-08-31, settlement 2026-08-30 gave accrued 3.286 against a 3.25 coupon."""
    flows = ba.cashflows(Decimal("6.5"), date(2026, 8, 30), date(2030, 8, 31), Decimal(100))
    assert flows.accrued == Decimal("3.25") and flows.first == 0
    off = ba.cashflows(Decimal("6.5"), date(2026, 8, 29), date(2030, 8, 31), Decimal(100))
    assert 0 < off.accrued < Decimal("3.25") and 0 < off.first < 1


def test_a_calc_output_in_a_missing_folder_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "missing" / "out.json"
    code = main(
        [
            "calc",
            "bond_analytics",
            "--in",
            str(CALC / "CP-3-bond_analytics.json"),
            "--out",
            str(out),
        ]
    )
    assert code == 1 and "error:" in capsys.readouterr().out


def test_a_calc_input_that_is_not_utf8_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "in.json"
    bad.write_bytes(b"\xff\xfe{}")
    assert main(["calc", "bond_analytics", "--in", str(bad)]) == 1
    assert "not UTF-8 text" in capsys.readouterr().out


def test_a_calc_output_replaces_the_old_file_whole(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    out.write_text("old", encoding="utf-8")
    assert (
        main(
            [
                "calc",
                "bond_analytics",
                "--in",
                str(CALC / "CP-3-bond_analytics.json"),
                "--out",
                str(out),
            ]
        )
        == 0
    )
    assert json.loads(out.read_text("utf-8")) == compute(_input())
    assert [p.name for p in tmp_path.iterdir()] == ["out.json"]  # no temp file left


# --- mutation review: the bracket ends of the yield solver and the new checks' edges -----------


@pytest.mark.parametrize(
    ("divisor", "expected"),
    [("0.75", "-50.000000"), ("3.5", "500.000000")],  # the value at exactly -50% and +500%
)
def test_the_solver_brackets_include_their_end_points(divisor: str, expected: str) -> None:
    """A zero coupon one period from settlement priced to 38 digits at the bracket's end."""
    flows = ba.cashflows(Decimal(0), date(2026, 8, 15), date(2027, 2, 15), Decimal(100))
    price = ba.CONTEXT.divide(Decimal(100), Decimal(divisor))
    solved = ba.solve_yield(flows, price)
    assert solved is not None and ba.pct(solved) == expected


def test_a_floor_of_exactly_the_least_floor_and_a_reference_of_exactly_the_least_is_valid() -> None:
    row = one(one_loan_item() | {"floor_bps": "5"}, reference_rate_pct="0.2")
    assert row["floor_benefit_bps"] == "0.00"  # 5 bps less 20 bps of rate: no benefit
    row = one(one_loan_item() | {"floor_bps": "5"}, reference_rate_pct="-0.2")
    assert row["floor_benefit_bps"] == "25.00"


def test_the_refusal_messages_are_exact() -> None:
    expected = {
        (("kind", "bond"), ("key", "floor_bps")): (
            "instruments[0].floor_bps: a bond has a fixed coupon; a floating-rate note is not "
            "priced as a bond (give it as a loan, or leave it unpriced and say so under Gaps)"
        ),
        (("kind", "loan"), ("key", "floor_pct")): (
            "instruments[0].floor_pct: unknown field for a loan (reads facility_id, kind, price, "
            "margin_bps, floor_bps, maturity_date)"
        ),
    }
    for (kind, key), message in expected.items():
        base = {"loan": one_loan_item(), "bond": _bond()}[kind[1]]
        with pytest.raises(CalcError) as caught:
            compute({"as_of": AS_OF, "instruments": [base | {key[1]: "5"}]})
        assert str(caught.value) == message
    with pytest.raises(CalcError) as caught:
        compute({"as_of": AS_OF, "instruments": [one_loan_item()], "ref": "1"})
    assert (
        str(caught.value)
        == "input.ref: unknown field (reads as_of, reference_rate_pct, instruments)"
    )
    with pytest.raises(CalcError) as caught:
        compute({"as_of": AS_OF, "reference_rate_pct": "0.042", "instruments": [one_loan_item()]})
    assert str(caught.value) == (
        "input.reference_rate_pct: 0.042 is below 0.2 percent; a percent, not a fraction?"
    )
