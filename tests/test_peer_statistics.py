"""Hand-calculated peer witnesses, strict boundaries and real CLI publication."""

from __future__ import annotations

import copy
import json
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.calc import peer_statistics as ps
from rbotlib.calc.bond_analytics import CalcError
from rbotlib.cli import main
from rbotlib.fsio import write_atomic


def payload(values: Sequence[object] | None = None, **extra: object) -> dict[str, Any]:
    return {
        "metric_id": "leverage",
        "unit_label": "x",
        "borrower_value": "5",
        "peers": [
            {
                "peer": f"P{i}",
                "value": v,
                "comparability": "Close",
                "calculation_status": "Reported",
                "period": "LTM2026-06",
                "currency": None,
            }
            for i, v in enumerate([2, 4, 6, 8] if values is None else values)
        ],
        **extra,
    }


def group(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = ps.compute(data)["groups"][0]
    return result


def test_type7_quartiles_and_equality_position() -> None:
    result = group(payload())
    stats = result["statistics_including_outliers"]
    assert [stats[k] for k in ("minimum", "q1", "median", "q3", "maximum")] == [
        "2",
        "3.50",
        "5.0",
        "6.50",
        "8",
    ]
    assert result["positioning"]["position"] == "In line"
    assert Decimal(result["positioning"]["delta_to_median"]) == 0
    assert "type 7" in ps.compute(payload())["convention"]


@pytest.mark.parametrize("n", range(6))
def test_each_statistic_has_its_own_floor(n: int) -> None:
    result = group(payload(list(range(n))))
    stats = result["statistics_including_outliers"]
    assert stats["n"] == n
    for key, floor in (
        ("minimum", 2),
        ("maximum", 2),
        ("range", 2),
        ("median", 3),
        ("q1", 4),
        ("q3", 4),
        ("average", 5),
    ):
        assert (stats[key] is not None) == (n >= floor)
        assert (key in stats["reasons"]) == (n < floor)
    assert (result["positioning"]["position"] is None) == (n < 3)
    if n == 5:
        assert Decimal(stats["average"]) == 2


def test_exclusions_outliers_zero_and_visible_metadata() -> None:
    data = payload([0, 4, 6, 100, 999, 999, None])
    data["peers"][1] |= {"comparability": "Partial", "cite": "S1 p.2", "age_months": 13}
    data["peers"][3] |= {"outlier": True, "outlier_reason": "One-off gain"}
    data["peers"][4]["comparability"] = "Weak"
    data["peers"][5]["calculation_status"] = "Provisional"
    result = ps.compute(data)
    included, excluded = (
        result["groups"][0][k]
        for k in ("statistics_including_outliers", "statistics_excluding_outliers")
    )
    assert included["n"] == 4 and included["minimum"] == "0"
    assert excluded["n"] == 3 and excluded["q1"] is None
    assert excluded["newly_suppressed_by_exclusion"] == ["q1", "q3"]
    assert result["peers"][1]["cite"] == "S1 p.2"
    assert all(result["peers"][i]["exclusion_reason"] for i in (4, 5, 6))
    text = ps.markdown(result)
    assert "Partial" in text and "stale" in text and "One-off gain" in text and "—" in text


@pytest.mark.parametrize(("borrower", "expected"), [("4.9", "Below"), ("5.1", "Above")])
def test_borrower_comparison_is_exact(borrower: str, expected: str) -> None:
    assert group(payload(borrower_value=borrower))["positioning"]["position"] == expected


def test_implied_ev_is_positive_metric_only_and_basis_separated() -> None:
    data = payload([2, 4, 6, 8, 10], borrower_metric="100", multiple_basis="Trading")
    data["peers"][-1]["outlier"] = True
    data["peers"] += [
        p | {"peer": p["peer"] + "T", "multiple_basis": "Transaction", "value": "20"}
        for p in data["peers"][:3]
    ]
    groups = ps.compute(data)["groups"]
    assert [g["multiple_basis"] for g in groups] == ["Trading", "Transaction"]
    assert Decimal(groups[0]["implied_ev"]["median"]) == 600
    assert Decimal(groups[0]["implied_ev_excluding_outliers"]["high"]) == 800
    assert Decimal(groups[1]["implied_ev"]["median"]) == 2000
    assert "indicative" in groups[0]["implied_ev"]["limitation"]
    for metric in ("0", "-1", None):
        ev = group(payload(borrower_metric=metric, multiple_basis="Trading"))["implied_ev"]
        assert ev["low"] is None and ev["reason"]


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("value", True),
        ("value", 1.5),
        ("value", "NaN"),
        ("value", "Infinity"),
        ("value", "5,2"),
        ("value", "5x"),
        ("comparability", "closeish"),
        ("calculation_status", "maybe"),
        ("outlier", "false"),
        ("age_months", -1),
        ("unit_label", "%"),
        ("currency", "EUR"),
        ("period", "FY2024"),
        ("definition_note", "net debt"),
        ("multiple_basis", "Blended"),
        ("typo", "5"),
    ],
)
def test_malformed_peer_and_unaligned_data_refuse(key: str, value: object) -> None:
    data = payload(currency="USD", definition_note="gross debt")
    for p in data["peers"]:
        p |= {"currency": "USD", "definition_note": "gross debt"}
    data["peers"][0][key] = value
    with pytest.raises(CalcError):
        ps.compute(data)


@pytest.mark.parametrize(
    "data",
    [
        [],
        {"metric_id": "x"},
        payload(peers=None),
        payload(extra=1),
        payload(borrower_value=True),
        payload(borrower_metric=1),
        payload(peers=[1]),
        payload(unit_label=" "),
        payload(multiple_basis="Trading", unit_label="USD m"),
    ],
)
def test_bad_documents_refuse(data: object) -> None:
    with pytest.raises(CalcError):
        ps.compute(data)


def test_missing_keys_duplicate_identities_and_unassessed_status_refuse() -> None:
    for key in ("peer", "value", "comparability", "calculation_status", "period", "currency"):
        data = payload()
        del data["peers"][0][key]
        with pytest.raises(CalcError, match=key):
            ps.compute(data)
    data = payload()
    data["peers"].append(copy.deepcopy(data["peers"][0]))
    with pytest.raises(CalcError, match="duplicate"):
        ps.compute(data)
    data["peers"][-1]["calculation_status"] = "typo"
    data["peers"][-1]["comparability"] = "Weak"
    with pytest.raises(CalcError, match="calculation_status"):
        ps.compute(data)


def test_source_metadata_is_preserved() -> None:
    data = payload(cite="S1 p.3", period="LTM2026-06", definition_note="gross debt")
    assert ps.compute(data)["input_basis"]["cite"] == "S1 p.3"


def test_stale_exclusion() -> None:
    data = payload()
    data["peers"][0]["age_months"] = "18.01"
    result = ps.compute(data)
    assert result["groups"][0]["statistics_including_outliers"]["n"] == 3
    assert "18 months" in result["peers"][0]["exclusion_reason"]


@pytest.mark.parametrize("value", ["1e-10000000", "1e10000000"])
def test_extreme_decimal_refusal(value: str) -> None:
    with pytest.raises(CalcError, match="Decimal38"):
        ps.compute(payload([value] * 4))


def test_nonstring_keys_refuse() -> None:
    with pytest.raises(CalcError, match="keys"):
        ps.compute(payload() | {1: None, "typo": None})


def test_cli_atomic_success_and_failure_preserves_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib import calc

    source, out = tmp_path / "in.json", tmp_path / "out.json"
    source.write_text(json.dumps(payload()))
    writes = []

    def observed(path: Path, text: str) -> None:
        writes.append(path)
        write_atomic(path, text)

    monkeypatch.setattr(calc, "write_atomic", observed)
    args = ["calc", "peer_statistics", "--in", str(source), "--out", str(out)]
    assert main(args) == 0 and writes == [out]
    before = out.read_bytes()
    assert json.loads(before)["groups"][0]["positioning"]["peer_q1"] == "3.50"
    assert "cp1c.positioning" in capsys.readouterr().out
    source.write_text(json.dumps(payload(borrower_value=True)))
    assert main(args) == 1 and out.read_bytes() == before and writes == [out]
    assert "borrower_value" in capsys.readouterr().out


@settings(max_examples=40, deadline=None)
@given(
    st.lists(st.integers(-10000, 10000), min_size=4, max_size=9),
    st.integers(1, 100),
    st.integers(-100, 100),
)
def test_permutation_positive_scaling_translation(
    values: list[int], scale: int, shift: int
) -> None:
    base = group(payload(values))["statistics_including_outliers"]
    assert base == group(payload(list(reversed(values))))["statistics_including_outliers"]
    transformed = group(payload([v * scale + shift for v in values]))[
        "statistics_including_outliers"
    ]
    for key in ("minimum", "q1", "median", "q3", "maximum"):
        assert Decimal(transformed[key]) == Decimal(base[key]) * scale + shift
    assert Decimal(transformed["range"]) == Decimal(base["range"]) * scale
