"""CP-2E hand arithmetic, explicit qualification and independent algebraic properties."""

from __future__ import annotations

import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.calc import rate_fx_sensitivity as rf
from rbotlib.calc.bond_analytics import CONTEXT, CalcError

EXPONENT_FAILURES = [
    ("1e1000000", "1e1000000", "unhedged_floating_rate_debt.*Overflow"),
    ("1e-1000100", "1", "unhedged_debt_percentage.*Underflow"),
    ("1e999999999999999999", "1e999999999999999999", "unhedged_floating_rate_debt.*ValueError"),
]


def exposure(
    identity: str, amount: str, value: str, move: str, basis: dict[str, str]
) -> dict[str, Any]:
    return {"exposure_id": identity, amount: value, "adverse_move_pct": move, "basis": dict(basis)}


def payload(**changes: object) -> dict[str, Any]:
    basis = {
        "currency": "USD",
        "unit": "m",
        "perimeter": "Group",
        "period_start": "2026-01-01",
        "period_end": "2026-12-31",
        "cite": "[C1]",
    }
    return {
        "basis": basis,
        "rate_exposure_id": "Debt",
        "gross_floating_rate_debt": "500",
        "hedged_floating_rate_debt": "300",
        "total_debt": "1000",
        "hedge_qualification": {
            "qualified": True,
            "hedge_ids": ["Swap1"],
            "covered_instruments": ["Debt"],
            "instrument_type": "Interest-rate swap",
            "notional": "400",
            "rate_or_strike": "3%",
            "linear_protection": True,
            "coverage_start": "2025-01-01",
            "coverage_end": "2027-12-31",
            "maturity_date": "2027-12-31",
            "basis": dict(basis),
        },
        "fx_exposures": [exposure("FX", "net_exposure", "120", ".1", basis)],
        "cost_exposures": [exposure("Energy", "annual_spend", "80", ".25", basis)],
        "channels_nonoverlapping": True,
        **changes,
    }


def rate_only(gross: str = "0", total: str = "0") -> dict[str, Any]:
    return payload(
        gross_floating_rate_debt=gross,
        total_debt=total,
        hedged_floating_rate_debt="0",
        fx_exposures=[],
        cost_exposures=[],
    )


def impacts(data: object) -> list[Decimal | None]:
    return [
        None if r["cash_impact"] is None else Decimal(r["cash_impact"])
        for r in rf.compute(data)["sensitivities"]
    ]


def test_hand_calculated_results_metadata_and_markdown() -> None:
    data = payload()
    before = copy.deepcopy(data)
    result = rf.compute(data)
    assert impacts(data) == [Decimal(2), Decimal(12), Decimal(20), Decimal(34)]
    assert result["unhedged_floating_rate_debt"] == "200"
    assert result["unhedged_debt_percentage"] == "0.2"
    assert data == before
    assert result["inputs"]["hedge_qualification"]["notional"] == "400"
    assert result["inputs"]["hedge_qualification"]["qualified"] is True
    assert "sources not host-verified" in result["provenance"]
    text = rf.markdown(result)
    assert "cp2e.sensitivities" in text and "| cash_impact |" in text
    assert "positive = adverse" in text and "[C1]" in text
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("hedged,rate", [("0", "5"), ("500", "0")])
def test_explicit_zero_and_full_protection(hedged: str, rate: str) -> None:
    data = payload(hedged_floating_rate_debt=hedged, fx_exposures=[], cost_exposures=[])
    data["hedge_qualification"]["notional"] = "500"
    if hedged == "0":
        data.pop("hedge_qualification")
    assert impacts(data) == [Decimal(rate), Decimal(rate)]
    zero = rf.compute(rate_only())
    assert zero["unhedged_debt_percentage"] is None and zero["fraction_reason"]
    assert zero["sensitivities"][0]["cash_impact"] == "0.00"


@pytest.mark.parametrize("key", rf.DEBT)
def test_missing_debt_only_poisons_dependents(key: str) -> None:
    data = payload()
    data.pop(key)
    result = rf.compute(data)
    assert result["unhedged_debt_percentage"] is None
    assert result["fraction_reason"]
    assert impacts(data)[1:3] == [Decimal(12), Decimal(20)]
    assert (impacts(data)[0] is None) == (key != "total_debt")
    assert (impacts(data)[-1] is None) == (key != "total_debt")


@pytest.mark.parametrize(
    "key,value",
    [
        ("qualified", False),
        ("notional", None),
        ("linear_protection", None),
        ("linear_protection", False),
        ("rate_or_strike", None),
        ("coverage_start", None),
        ("coverage_end", "2026-06-30"),
        ("maturity_date", "2025-12-31"),
        ("covered_instruments", ["OtherDebt"]),
    ],
)
def test_unqualified_coverage_never_invents_protection(key: str, value: object) -> None:
    data = payload()
    data["hedge_qualification"][key] = value
    result = rf.compute(data)
    assert impacts(data)[0] is None and impacts(data)[-1] is None
    assert result["sensitivities"][0]["reason"]
    assert result["inputs"]["hedge_qualification"][key] == value
    assert impacts(payload(hedge_qualification=None))[0] is None


def test_explicit_linear_evidenced_protection_not_limited_to_swap_label() -> None:
    data = payload()
    data["hedge_qualification"]["instrument_type"] = "Evidenced partial cap coverage"
    assert impacts(data)[0] == 2


@pytest.mark.parametrize(
    "channel,amount", [("fx_exposures", "net_exposure"), ("cost_exposures", "annual_spend")]
)
def test_signed_benefits_and_missing_channels(channel: str, amount: str) -> None:
    data = payload()
    data[channel][0]["adverse_move_pct"] = "-.1"
    result = rf.compute(data)
    index = 1 if channel == "fx_exposures" else 2
    assert Decimal(result["sensitivities"][index]["cash_impact"]) < 0
    assert result["sensitivities"][index]["effect"] == "Cash benefit"
    data[channel][0][amount] = "0"
    assert impacts(data)[index] == 0
    if channel == "fx_exposures":
        data[channel][0] |= {amount: "-120", "adverse_move_pct": ".1"}
        assert impacts(data)[index] == -12
    data[channel][0][amount] = None
    assert impacts(data)[index] is None and impacts(data)[-1] is None
    data.pop(channel)
    assert impacts(data)[-1] is None
    assert "unassessed" in rf.markdown(rf.compute(data))


@pytest.mark.parametrize("value", [True, 1.5, "NaN", "Infinity", "5,2", "not disclosed"])
def test_bad_figures_refused(value: object) -> None:
    with pytest.raises(CalcError, match="gross_floating_rate_debt"):
        rf.compute(payload(gross_floating_rate_debt=value))


@pytest.mark.parametrize(
    "path,value",
    [
        ("hedged_floating_rate_debt", "501"),
        ("total_debt", "499"),
        ("gross_floating_rate_debt", "-1"),
        ("typo", 0),
        ("channels_nonoverlapping", "yes"),
        ("fx_exposures", {}),
        ("basis", None),
        ("rate_exposure_id", " "),
        ("hedge_qualification.notional", "-1"),
        ("hedge_qualification.notional", "299"),
        ("hedge_qualification.hedge_ids", ["X", "X"]),
        ("hedge_qualification.qualified", "true"),
        ("hedge_qualification.linear_protection", "true"),
        ("hedge_qualification.coverage_start", "bad"),
        ("hedge_qualification.covered_instruments", []),
        ("hedge_qualification.typo", "X"),
        ("fx_exposures.0.basis.currency", "EUR"),
        ("fx_exposures.0.basis.unit", "bn"),
        ("fx_exposures.0.basis.period_end", "2027-01-01"),
        ("fx_exposures.0.basis.perimeter", "Subsidiary"),
        ("fx_exposures.0.adverse_move_pct", "10"),
        ("cost_exposures.0.annual_spend", "-80"),
        ("cost_exposures.0.exposure_id", "FX"),
        ("fx_exposures.0.exposure_id", "Debt"),
        ("fx_exposures.0.typo", "1"),
    ],
)
def test_malformed_fields_refused(path: str, value: object) -> None:
    data = payload()
    target: Any = data
    *parents, key = path.split(".")
    for parent in parents:
        target = target[int(parent) if parent.isdecimal() else parent]
    target[key] = value
    match = None if path.startswith("hedge_qualification.") else key
    with pytest.raises(CalcError, match=match):
        rf.compute(data)


def test_combined_requires_explicit_qualification() -> None:
    for qualification in (None, False):
        assert impacts(payload(channels_nonoverlapping=qualification))[-1] is None


@settings(max_examples=35, deadline=None)
@given(st.integers(0, 500), st.integers(0, 100), st.integers(-100, 100))
def test_independent_monotonic_linearity_and_null_poison(
    hedged: int, step: int, shock: int
) -> None:
    data = payload(hedged_floating_rate_debt=hedged)
    data["hedge_qualification"]["notional"] = 500
    first = impacts(data)[0]
    next_hedge = min(500, hedged + step)
    protected = copy.deepcopy(data)
    protected["hedged_floating_rate_debt"] = next_hedge
    improved = impacts(protected)[0]
    assert first is not None and improved is not None
    assert first - improved == Decimal(next_hedge - hedged) / 100
    data["gross_floating_rate_debt"] = 500 + step
    second = impacts(data)[0]
    assert first is not None and second is not None
    assert second - first == Decimal(step) / 100
    data["fx_exposures"][0]["adverse_move_pct"] = str(Decimal(shock) / 100)
    assert impacts(data)[1] == Decimal("1.2") * shock
    data["cost_exposures"][0]["adverse_move_pct"] = None
    assert impacts(data)[-1] is None


def test_arithmetic_ignores_ambient_precision_and_keeps_money_digits() -> None:
    data = payload(hedged_floating_rate_debt="0")
    data["fx_exposures"][0] |= {
        "net_exposure": "12345678901234567890123456789.123456789",
        "adverse_move_pct": ".123456789",
    }
    with localcontext() as context:
        context.prec = 5
        result = impacts(data)
    assert result[1] == Decimal("1524157875171467887517146788.765432099750190521")


def test_fractional_shock_guard_survives_low_decimal_context() -> None:
    data = payload()
    data["fx_exposures"][0]["adverse_move_pct"] = "1.000001"
    with localcontext() as context:
        context.prec = 5
        with pytest.raises(CalcError, match="adverse_move_pct"):
            rf.compute(data)


def test_overhedge_guard_independent_of_notional_guard() -> None:
    data = payload(hedged_floating_rate_debt="501")
    data["hedge_qualification"]["notional"] = "600"
    with pytest.raises(CalcError, match="exceeds gross_floating_rate_debt"):
        rf.compute(data)


@pytest.mark.parametrize("failure", EXPONENT_FAILURES)
def test_cli_atomic_success_and_invalid_input_preserves_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    failure: tuple[str, str, str],
) -> None:
    from rbotlib import calc
    from rbotlib.cli import main
    from rbotlib.fsio import write_atomic

    gross, total, error = failure
    source, output = tmp_path / "input.json", tmp_path / "output.json"
    source.write_text(json.dumps(payload()))
    writes = []
    original = write_atomic

    def observed(path: Path, text: str) -> None:
        writes.append(path)
        original(path, text)

    monkeypatch.setattr(calc, "write_atomic", observed)
    args = ["calc", "rate_fx_sensitivity", "--in", str(source), "--out", str(output)]
    assert main(args) == 0 and writes == [output]
    before = output.read_bytes()
    assert json.loads(before)["sensitivities"][-1]["cash_impact"] == "34.00"
    assert "cp2e.sensitivities" in capsys.readouterr().out
    source.write_text(json.dumps(payload(hedged_floating_rate_debt=True)))
    assert main(args) == 1 and output.read_bytes() == before and writes == [output]
    assert "hedged_floating_rate_debt" in capsys.readouterr().out
    invalid = rate_only(gross, total)
    invalid["hedge_qualification"] = None
    with pytest.raises(CalcError, match=error):
        rf.compute(invalid)
    source.write_text(json.dumps(invalid))
    assert main(args) == 1 and output.read_bytes() == before and writes == [output]
    captured = capsys.readouterr()
    assert error.split(".*")[0] in captured.out and error.split(".*")[1] in captured.out
    assert "Traceback" not in captured.out + captured.err


def test_money_ignores_ambient_exponent_limits() -> None:
    with localcontext() as context:
        context.Emax = 1
        result = impacts(payload())
    assert result == [Decimal(2), Decimal(12), Decimal(20), Decimal(34)]


@pytest.mark.parametrize(
    "gross,total,fraction,rate",
    [("1e-1000036", "1", "1e-1000036", "1e-1000038"), ("1", "3", "0." + "3" * 38, "0.01")],
)
def test_supported_subnormal_and_recurring_fraction(
    gross: str, total: str, fraction: str, rate: str
) -> None:
    flags = dict(CONTEXT.flags)
    result = rf.compute(rate_only(gross, total))
    assert Decimal(result["unhedged_debt_percentage"]) == Decimal(fraction)
    assert Decimal(result["sensitivities"][0]["cash_impact"]) == Decimal(rate)
    assert CONTEXT.flags == flags
