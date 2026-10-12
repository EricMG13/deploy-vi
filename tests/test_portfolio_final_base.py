"""Plan05 classification survives the final02 parser's refusal and unit guards."""

from typing import Any

import pytest
from test_portfolio_exact import _table

from rbotlib.portfolio import Portfolio, read_sheet, to_json
from rbotlib.rules import Rules


@pytest.mark.parametrize(
    ("limit", "current", "breach", "expected"),
    [
        ("≥ Caa1", "B2", "Hard", "minimum"),
        ("Info only", "4", "—", "info"),
        ("≤ 5% NAV", "5 bps", "Hard", "limit"),
        ("≤ 5% NAV", "1,5%", "Hard", "limit"),
        ("≤ $25", "12", "Hard", "limit"),
    ],
)
def test_loss_kind_is_explicit_without_guessing_units(
    rules: Rules, limit: str, current: str, breach: str, expected: str
) -> None:
    found: dict[str, Portfolio] = {}
    row = ["C1", "Single Name", "Max issuer", limit, breach, current]
    read_sheet("limits.csv", _table("limits", row, unit="MILLIONS"), found, {})
    data = to_json(found["P1"], rules)
    lost = [r for r in data["unparsed"] if r["row"].startswith("limits.csv")]
    assert len(lost) == 1 and lost[0]["kind"] == expected
    assert data["limits"] == []


@pytest.mark.parametrize("kind,expected", [("positions", "position"), ("limits", "limit")])
def test_uncached_data_row_has_the_correct_loss_kind(kind: str, expected: str) -> None:
    found: dict[str, Portfolio] = {}
    row = (
        ["CZR", "Caesars", "6", "1%"]
        if kind == "positions"
        else ["C1", "Single Name", "Max issuer", "≤ 5% NAV", "Hard", "1%"]
    )
    rows = _table(kind, row)
    read_sheet("data.csv", rows, found, {len(rows): "C4"})
    assert found["P1"].unparsed == [
        {
            "row": f"data.csv row {len(rows)}",
            "reason": "formula C4 has no stored value",
            "kind": expected,
        }
    ]


def test_largest_flag_is_explicit_and_other_parser_refusals_stay(rules: Rules) -> None:
    found: dict[str, Portfolio] = {}
    row = ["C1", "Sector", "2nd largest sector: Gaming", "≤ 5% NAV", "Hard", "1%"]
    read_sheet("limits.csv", _table("limits", row), found, {})
    limit: dict[str, Any] = to_json(found["P1"], rules)["limits"][0]
    assert limit["largest"] is True and limit["scope_value"] is None
    repeated = _table("limits", row) + _table("positions", ["A", "Acme", "1", "1%"])
    other: dict[str, Portfolio] = {}
    notes = read_sheet("bad.csv", repeated, other, {})
    assert "more than one table" in notes[0] and not other["P1"].files


def test_missing_metadata_is_an_explicit_metadata_loss(rules: Rules) -> None:
    data = to_json(Portfolio(meta={"portfolio_id": "P1"}), rules)
    assert {row["row"] for row in data["unparsed"]} == {
        "Total NAV",
        "Total PAR",
        "As of",
        "Strategy",
    }
    assert {row["kind"] for row in data["unparsed"]} == {"meta"}
