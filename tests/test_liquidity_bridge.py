"""Synthetic, hand-computed CP2D witnesses; metadata never proves source authority."""

from __future__ import annotations

import json
from copy import deepcopy
from decimal import Decimal, localcontext
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.calc import liquidity_bridge as lb
from rbotlib.calc.bond_analytics import CalcError

ALIGN = {
    "currency": "USD",
    "unit": "m",
    "perimeter": "Group",
    "as_of_date": "2026-06-30",
    "horizon_end": "2027-06-30",
}


def payload() -> dict[str, Any]:
    common = {**ALIGN, "cite": "[S1]", "basis": "Source-supported synthetic witness"}
    sources = [
        {
            **common,
            "id": "cash",
            "amount": "250",
            "component": "Cash",
            "availability": "Opening",
            "accessible": "Yes",
        },
        {
            **common,
            "id": "commitment",
            "amount": "0",
            "component": "Committed inflow",
            "availability": "Future",
            "accessible": "Yes",
        },
    ]
    amounts = ("60", "-20", "30", "5", "40", "25", "10")
    components = [
        {
            **common,
            "id": field,
            "component": field,
            "amount": amount,
            "timing": "Within next12 months; exact schedule unavailable",
            "mandatory": "Yes",
        }
        for field, amount in zip(lb.COMPONENTS, amounts, strict=True)
    ]
    return {
        **ALIGN,
        "period_months": 12,
        "burn_basis": "12-month forecast; seasonal caveat",
        "ocf_includes": [],
        "liquidity_sources": sources,
        "components": components,
    }


def changed(field: str, amount: object) -> dict[str, Any]:
    data = payload()
    next(r for r in data["components"] if r["component"] == field)["amount"] = amount
    return data


def test_known_values_and_order() -> None:
    data = payload()
    before = deepcopy(data)
    out = lb.compute(data)
    assert data == before
    assert out["net_movement"] == {"value": "-70", "reason": None}
    assert out["ending_accessible_liquidity"] == {"value": "180", "reason": None}
    assert [r["value"] for r in out["runway"][:3]] == ["250", "110", "140"]
    assert [r["item"] for r in out["runway"]] == [
        "Accessible liquidity",
        "Mandatory uses 12m",
        "Headroom",
        "Months of runway",
        "Pinch point",
    ]
    assert [r["kind"] for r in out["bridge"]] == [
        "Opening total",
        "Delta",
        "Delta",
        "Use",
        "Use",
        "Use",
        "Use",
        "Use",
        "Delta",
        "Closing total",
    ]
    assert out["bridge"][3]["amount"] == "-30"
    assert out["average_monthly_burn"]["value"].startswith(
        "5.8333333333333333333333333333333333333"
    )
    assert out["months_to_empty"]["value"].startswith("42.85714285714285714285714285714285714")
    assert "Timing unknown" in out["runway"][-1]["value"]
    assert "independent source" in out["limitation"]
    json.dumps(out)
    text = lb.markdown(out)
    assert "<!-- cp2d.bridge -->" in text and "<!-- cp2d.runway -->" in text
    assert "| cash_interest | Use | -30 | USD | m |" in text


@pytest.mark.parametrize("field", lb.COMPONENTS)
def test_each_null_poison_and_zero_is_real(field: str) -> None:
    out = lb.compute(changed(field, None))
    assert out["net_movement"] == {"value": None, "reason": "missing " + field}
    assert out["ending_accessible_liquidity"]["value"] is None
    assert out["months_to_empty"]["value"] is None
    assert "missing " + field in lb.markdown(out)
    zero = lb.compute(changed("cash_taxes", "0"))
    assert zero["ending_accessible_liquidity"]["value"] == "185"


@pytest.mark.parametrize(("ocf", "note"), [("130", "flat"), ("200", "cash-generative")])
def test_nonpositive_burn(ocf: str, note: str) -> None:
    out = lb.compute(changed("operating_cash_flow", ocf))
    assert out["months_to_empty"]["value"] is None
    assert note in out["months_to_empty"]["reason"]


def test_sources_access_future_zero_unknown_and_deficit() -> None:
    data = payload()
    data["liquidity_sources"].append(
        {
            **data["liquidity_sources"][0],
            "id": "restricted",
            "amount": "999",
            "availability": "Restricted",
            "accessible": "No",
        }
    )
    data["liquidity_sources"][1]["amount"] = "50"
    out = lb.compute(data)
    assert out["runway"][0]["value"] == "250"
    assert out["ending_accessible_liquidity"]["value"] == "230"
    data["liquidity_sources"][0]["accessible"] = "No"
    assert lb.compute(data)["runway"][0]["value"] == "0"
    data["liquidity_sources"][0]["accessible"] = "Yes"
    data["liquidity_sources"][0]["amount"] = "0"
    out = lb.compute(data)
    assert out["months_to_empty"]["value"] == "0"
    assert "Closing deficit" in out["runway"][-1]["value"]
    data["liquidity_sources"][0]["amount"] = None
    out = lb.compute(data)
    assert out["net_movement"]["value"] == "-20"
    assert out["ending_accessible_liquidity"]["reason"] == "missing cash"
    data = payload()
    data["liquidity_sources"][1]["amount"] = None
    assert lb.compute(data)["net_movement"]["reason"] == "missing commitment"


@pytest.mark.parametrize(
    "figure",
    [
        True,
        False,
        1.0,
        "NaN",
        "Infinity",
        "1,000",
        "5,2",
        "",
        "n/a",
        "1e1001",
        "1e-1001",
        "1" * 101,
        {},
        [],
        "1e99999999999999999999",
    ],
)
def test_invalid_figures(figure: object) -> None:
    with pytest.raises(CalcError, match=r"cash_taxes\.amount"):
        lb.compute(changed("cash_taxes", figure))


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("typo",), 1),
        ((3,), None),
        (("schedule",), []),
        (("components", 0, "id"), "cash"),
        (("components", 0, "component"), "cash_interest"),
        (("ocf_includes",), ["cash_interest"]),
        (("period_months",), 0),
        (("period_months",), 6),
        (("period_months",), True),
        (("horizon_end",), "2028-06-30"),
        (("as_of_date",), "2026-02-30"),
        (("components", 0, "unit"), "different"),
        (("components", 0, "currency"), "different"),
        (("components", 0, "perimeter"), "different"),
        (("components", 0, "as_of_date"), "2026-07-01"),
        (("liquidity_sources", 0, "availability"), "Restricted"),
        (("liquidity_sources", 1, "availability"), "Opening"),
        (("components", 2, "amount"), "-1"),
        (("liquidity_sources", 0, "amount"), "-1"),
        (("components", 2, "mandatory"), "No"),
    ],
)
def test_structural_refusals(path: tuple[str | int, ...], value: object) -> None:
    data = payload()
    target: Any = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(CalcError):
        lb.compute(data)


def test_missing_component_is_not_zero() -> None:
    data = payload()
    del data["components"][3]["amount"]
    with pytest.raises(CalcError, match="missing"):
        lb.compute(data)


def test_tiny_exact_burn_and_hostile_ambient_context() -> None:
    data = payload()
    for row in data["components"]:
        row["amount"] = "0"
    data["components"][2]["amount"] = "1e-1000"
    with localcontext() as ctx:
        ctx.prec, ctx.Emin, ctx.Emax = 2, -2, 2
        ctx.clear_traps()
        out = lb.compute(data)
    assert Decimal(out["average_monthly_burn"]["value"]) > 0
    assert Decimal(out["months_to_empty"]["value"]) > Decimal("1e1000")
    assert out["net_movement"]["value"] == "-1E-1000"
    data["components"][2]["amount"] = "1e1000"
    assert lb.compute(data)["ending_accessible_liquidity"]["value"].startswith("-999")


@settings(max_examples=50, deadline=None)
@given(scale=st.integers(1, 10000), extra_use=st.integers(0, 10000), reverse=st.booleans())
def test_independent_money_properties(scale: int, extra_use: int, reverse: bool) -> None:
    data = payload()
    for row in data["liquidity_sources"] + data["components"]:
        row["amount"] = str(Decimal(row["amount"]) * scale)
    base = lb.compute(data)
    if reverse:
        data["liquidity_sources"].reverse()
        data["components"].reverse()
    assert lb.compute(data) == base
    assert Decimal(base["ending_accessible_liquidity"]["value"]) == 180 * scale
    opening = Decimal(base["runway"][0]["value"])
    net = Decimal(base["net_movement"]["value"])
    assert Decimal(base["ending_accessible_liquidity"]["value"]) == opening + net
    next(r for r in data["components"] if r["component"] == "cash_taxes")["amount"] = str(
        5 * scale + extra_use
    )
    updated = lb.compute(data)
    assert Decimal(updated["runway"][2]["value"]) == 140 * scale - extra_use
    assert Decimal(updated["runway"][2]["value"]) <= Decimal(base["runway"][2]["value"])


def test_final_display_does_not_round_intermediate_runway_numerator() -> None:
    data = payload()
    data["liquidity_sources"][0]["amount"] = "12345678901234567890123456789012345678901234567890"
    for row in data["components"]:
        row["amount"] = "0"
    data["components"][2]["amount"] = "3"
    assert (
        lb.compute(data)["months_to_empty"]["value"]
        == "4.9382715604938271560493827156049382716E+49"
    )


def test_multiple_dependent_gaps_are_all_named() -> None:
    data = changed("cash_taxes", None)
    data["liquidity_sources"][0]["amount"] = None
    out = lb.compute(data)
    for metric in (out["ending_accessible_liquidity"], out["months_to_empty"], out["runway"][2]):
        assert "cash" in metric["reason"] and "cash_taxes" in metric["reason"]
