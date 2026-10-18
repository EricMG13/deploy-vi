"""Synthetic CP4 arithmetic witnesses; metadata is an assertion, not source qualification."""

from __future__ import annotations

import json
from copy import deepcopy
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.calc import covenant_headroom as ch
from rbotlib.calc.bond_analytics import CalcError


def row(**changes: object) -> dict[str, Any]:
    return {
        "test": "Leverage",
        "test_type": "Maintenance",
        "direction": "Ceiling",
        "threshold": "6",
        "current_value": "5",
        "unit_label": "x",
        "basis": "Covenant EBITDA; legal clause 2",
        "cite": "[L1]",
        **changes,
    }


def debt(**changes: object) -> dict[str, Any]:
    return {
        "governing_ebitda": "100",
        "current_debt": "500",
        "ebitda_denominated": True,
        "basis": row()["basis"],
        "cite": "[L1]",
        "ebitda_cite": "[F1]",
        "debt_cite": "[F2]",
        "currency": "USD",
        "unit": "m",
        "perimeter": "Restricted group",
        "period": "LTM Q2",
        **changes,
    }


def basket(**changes: object) -> dict[str, Any]:
    return {
        "basket": "A",
        "capacity": "100",
        "used": "30",
        "currency": "USD",
        "unit": "m",
        "basis": "Clause 3",
        "cite": "[L2/F2]",
        "period": "Q2",
        "perimeter": "Group",
        "capacity_type": "Debt",
        "independence": "Independent",
        "independence_cite": "[L3]",
        **changes,
    }


def result(**changes: object) -> dict[str, Any]:
    return dict(ch.compute({"tests": [row(**changes)]})["tests"][0])


@pytest.mark.parametrize(
    ("direction", "threshold", "current", "value", "status"),
    [
        ("Ceiling", "6", "5", "1", "Headroom"),
        ("Floor", "2", "2.5", ".5", "Headroom"),
        ("Ceiling", "6", "6", "0", "Tight"),
        ("Floor", "2", "2", "0", "Tight"),
        ("Ceiling", "6", "6.000000000000000000000000000000000000001", "-1e-39", "Breached"),
        ("Floor", "2", "1.999999999999999999999999999999999999999", "-1e-39", "Breached"),
    ],
)
def test_signed_headroom(
    direction: str, threshold: str, current: str, value: str, status: str
) -> None:
    actual = result(direction=direction, threshold=threshold, current_value=current)
    assert Decimal(actual["headroom"]) == Decimal(value)
    assert actual["status"] == status


@pytest.mark.parametrize("key", ["threshold", "current_value"])
def test_null_is_not_zero(key: str) -> None:
    actual = result(**{key: None})
    assert actual["headroom"] is None and actual["status"] == "Not computable"
    assert key in actual["reason"]
    assert result(**{key: 0})["headroom"] is not None


def test_incremental_capacity_and_governing_basis() -> None:
    actual = result(incremental_debt=debt())
    assert actual["incremental_debt"]["capacity"] == "100"
    assert actual["incremental_debt"]["basis"] == row()["basis"]
    assert (
        result(incremental_debt=debt(current_debt="700"))["incremental_debt"]["capacity"] == "-100"
    )
    for changes in (
        {"governing_ebitda": "0"},
        {"governing_ebitda": "-1"},
        {"governing_ebitda": None},
        {"current_debt": None},
        {"ebitda_denominated": False},
        {"basis": "Reported EBITDA"},
    ):
        capacity = result(incremental_debt=debt(**changes))["incremental_debt"]
        assert capacity["capacity"] is None and capacity["reason"]
    assert (
        result(direction="Floor", incremental_debt=debt())["incremental_debt"]["capacity"] is None
    )
    assert result(threshold=None, incremental_debt=debt())["incremental_debt"]["capacity"] is None


def test_baskets_signed_remaining_and_no_hidden_total() -> None:
    actual = ch.compute({"tests": [], "baskets": [basket(), basket(basket="B", used="120")]})
    assert [b["remaining"] for b in actual["baskets"]] == ["70", "-20"]
    assert actual["baskets"][1]["status"] == "Breached"
    assert actual["aggregate"]["remaining"] == "50"
    assert actual["aggregate"]["currency"] == "USD"
    for changes in (
        {"independence": "Overlapping"},
        {"independence": "Unknown"},
        {"independence_cite": None},
        {"currency": "EUR"},
        {"unit": "bn"},
        {"basis": "Shared cap"},
        {"perimeter": "Subsidiary"},
        {"period": "Q1"},
        {"capacity_type": "RP"},
        {"used": None},
        {"capacity": None},
    ):
        aggregate = ch.compute({"tests": [], "baskets": [basket(), basket(basket="B", **changes)]})[
            "aggregate"
        ]
        assert aggregate["remaining"] is None and aggregate["reason"]
    assert ch.compute({"tests": []})["aggregate"]["remaining"] is None


@pytest.mark.parametrize("key", ["direction", "test_type", "basis", "cite", "unit_label"])
def test_missing_metadata_refused(key: str) -> None:
    data = row()
    del data[key]
    with pytest.raises(CalcError, match=key):
        ch.compute({"tests": [data]})


@pytest.mark.parametrize(
    "changes",
    [
        {"direction": "max-ratio"},
        {"direction": None},
        {"test_type": "max-ratio"},
        {"basis": []},
        {"cite": " "},
        {"formula": "eval('6-5')"},
        {"direction": True},
        {"threshold": True},
        {"current_value": 1.0},
        {"threshold": "NaN"},
        {"threshold": "Infinity"},
        {"threshold": "oops"},
        {"threshold": []},
        {"threshold": "1e1001"},
        {"threshold": "1e-1001"},
        {"threshold": "1" * 101},
    ],
)
def test_invalid_row_refused(changes: dict[str, Any]) -> None:
    with pytest.raises(CalcError):
        result(**changes)


def test_shape_duplicates_and_nested_types_refused() -> None:
    cases: tuple[object, ...] = (
        None,
        [],
        {"tests": {}},
        {"tests": [], "unknown": 1},
        {"tests": [None]},
        {"tests": [row(), row()]},
        {"tests": [], "baskets": [basket(), basket()]},
        {"tests": [row(incremental_debt=debt(ebitda_denominated="yes"))]},
        {"tests": [], "baskets": [basket(independence="yes")]},
        {"tests": [], "baskets": [basket(independence_cite=False)]},
        {"tests": [], "baskets": [basket(used=True)]},
        {"tests": [], "baskets": [basket(capacity="-1")]},
        {"tests": [row(incremental_debt={**debt(), "reported_ebitda": "200"})]},
        {"tests": [], "baskets": "A"},
        {"tests": [], 1: "bad"},
    )
    for data in cases:
        with pytest.raises(CalcError):
            ch.compute(data)


def test_ambient_context_purity_and_visible_metadata() -> None:
    data = {"tests": [row(incremental_debt=debt())], "baskets": [basket()]}
    original = deepcopy(data)
    expected = ch.compute(data)
    assert json.loads(json.dumps(expected)) == expected
    with localcontext() as context:
        context.prec, context.Emax, context.Emin = 2, 3, -3
        assert ch.compute(data) == expected
        assert result(threshold="1e1000", current_value="1e-1000")["status"] == "Headroom"
        with pytest.raises(CalcError, match="threshold"):
            result(threshold="not numeric")
    assert data == original
    rendered = ch.markdown(expected)
    for value in (
        "cp4.covenant_tests",
        "Ceiling",
        "Covenant EBITDA",
        "[L1]",
        "70",
        "[L3]",
        "not verify",
        "not legal",
    ):
        assert value in rendered
    assert r"a\|b" in ch.markdown(ch.compute({"tests": [row(test="a|b\nc")]}))


@settings(max_examples=75)
@given(
    st.integers(-100000, 100000),
    st.integers(-100000, 100000),
    st.integers(-1000, 1000),
    st.integers(1, 100),
)
def test_independent_sign_translation_scaling(
    threshold: int, current: int, offset: int, scale: int
) -> None:
    ceiling = result(threshold=threshold, current_value=current)
    floor = result(direction="Floor", threshold=threshold, current_value=current)
    difference = threshold - current
    assert Decimal(ceiling["headroom"]) == difference
    assert Decimal(floor["headroom"]) == -difference
    assert ceiling["status"] == (
        "Headroom" if difference > 0 else "Breached" if difference < 0 else "Tight"
    )
    assert (
        Decimal(result(threshold=threshold + offset, current_value=current + offset)["headroom"])
        == difference
    )
    assert (
        Decimal(result(threshold=threshold * scale, current_value=current * scale)["headroom"])
        == difference * scale
    )


@given(st.integers(0, 100000), st.integers(0, 100000))
def test_basket_conservation_and_null_propagation(capacity: int, used: int) -> None:
    actual = ch.compute({"tests": [], "baskets": [basket(capacity=capacity, used=used)]})
    assert Decimal(actual["baskets"][0]["remaining"]) + used == capacity
    missing = ch.compute({"tests": [], "baskets": [basket(capacity=capacity, used=None)]})
    assert missing["baskets"][0]["remaining"] is None
    assert missing["aggregate"]["remaining"] is None


def test_exponent_overflow_preserves_field_error_under_any_context() -> None:
    with localcontext() as context:
        for trapped in (True, False):
            context.traps[InvalidOperation] = trapped
            with pytest.raises(CalcError, match="threshold"):
                result(threshold="1e9999999999999999999999999999")


def test_huge_integer_preserves_field_error() -> None:
    with pytest.raises(CalcError, match="threshold"):
        result(threshold=10**5000)


def test_explicit_covenant_period_must_match_capacity_inputs() -> None:
    actual = result(period="Q1", incremental_debt=debt(period="Q2"))["incremental_debt"]
    assert actual["capacity"] is None and "period" in actual["reason"]
