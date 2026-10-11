"""Exact outputs of portfolio.py internals: messages, defaults and row handling (mutation)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rbotlib.portfolio import (
    Portfolio,
    Table,
    _id_problem,
    _limit_row,
    _scope,
    _unit_problem,
    parse_limit,
    read_sheet,
    to_json,
    write_all,
)
from rbotlib.rules import Rules

T = Table("t", [], 0, {})
POS = ["Issuer ID", "Issuer", "Par", "% NAV"]
LIM = ["ID", "Constraint Category", "Parameter", "Limit", "Breach Type", "Current Value"]


def _limit(row: dict[str, str]) -> dict[str, object] | str:
    return _limit_row(T, 2, {"breach type": "Hard"} | row, [])


def test_sparse_limit_rows_give_exact_reasons() -> None:
    assert _limit_row(T, 2, {}, []) == "no Hard or Soft breach type (info only)"
    assert _limit({}) == "limit '' is not a number with a unit"
    assert _limit({"limit": "≤ 25"}) == "limit '≤ 25': unit not recognised"
    assert _limit({"limit": "≤ 2% NAV"}) == "current value '' is not a number"
    assert _limit({"limit": "≤ 2% NAV", "current value": "5"}) == (
        "current value '5' is a bare number but the limit is pct_nav; not converted"
    )
    assert _limit({"limit": "≤ 2% NAV", "current value": "5 bps"}) == (
        "current value '5 bps' is bps but the limit is pct_nav; not converted"
    )
    assert _limit({"limit": "≤ 2 years", "current value": "5%"}) == (
        "current value '5%' is a percent but the limit is years; not converted"
    )
    assert _limit({"limit": "≤ 2% NAV", "current value": "5 yrs"}) == (
        "current value '5 yrs' is years but the limit is pct_nav; not converted"
    )


def test_a_limit_row_with_only_the_required_columns_has_empty_defaults() -> None:
    row = {"limit": "≤ 2% NAV", "current value": "1%", "breach type": "Soft"}
    assert _limit_row(T, 7, row, []) == {
        "limit_id": "",
        "category": "",
        "parameter": "",
        "scope": "other",
        "scope_value": None,
        "limit_value": "2",
        "unit": "pct_nav",
        "limit_kind": "Soft",
        "current_value": "1",
        "source": "t row 7",
    }
    named = _limit(row | {"parameter": "Max x"})
    assert isinstance(named, dict) and named["parameter"] == "Max x"
    inst = _limit(row | {"constraint category": "Instrument"})
    assert isinstance(inst, dict) and inst["scope_value"] == "" and inst["parameter"] == ""


@pytest.mark.parametrize(
    ("category", "parameter", "expected"),
    [
        ("Issuer", "", ("issuer", None)),
        ("Country", "", ("country", None)),
        ("Currency", "", ("currency", None)),
        ("Asset Type", "", ("asset_type", None)),
        ("Seniority", "", ("seniority", None)),
        ("Instrument", "MAX 2nd Lien", ("seniority", "2nd Lien")),
        ("Rating — B Bucket", "", ("rating_bucket", "B Bucket")),
        ("Rating — X — B", "", ("rating_bucket", "B")),
        ("Rating", "", ("rating_bucket", None)),
    ],
)
def test_scopes(category: str, parameter: str, expected: tuple[str, str | None]) -> None:
    assert _scope(category, parameter) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (">= 5% NAV", "minimum limit: Portfolio Fit sizes against maximum limits only"),
        ("> 5% NAV", "minimum limit: Portfolio Fit sizes against maximum limits only"),
        ("≤ 8 year", ("8", "years")),
        ("≤ 8 yrs", ("8", "years")),
        ("≤ 8 yr", ("8", "years")),
        ("≤ 8 % par", ("8", "pct_par")),
    ],
)
def test_parse_limit_operators_and_year_spellings(text: str, expected: object) -> None:
    assert parse_limit(text) == expected


def test_unit_labels_and_id_problems_are_exact() -> None:
    assert (
        _unit_problem("v", "1", "years", "")
        == "v '1' is a bare number but the limit is years; not converted"
    )
    assert (
        _unit_problem("v", "1", "pct_nav", "years")
        == "v '1' is years but the limit is pct_nav; not converted"
    )
    assert (
        _unit_problem("v", "1", "amount", "bps")
        == "v '1' is bps but the limit is amount; not converted"
    )
    assert _unit_problem("v", "1", "amount", "") is None
    assert _id_problem("a/b", {}) == "not a file name"
    assert _id_problem("NUL", {}) == "reserved Windows device name"
    assert _id_problem("a" * 100, {}) is None
    assert _id_problem("a" * 101, {}) == "longer than 100 characters"
    assert _id_problem("P1", {"p1": Portfolio()}) == "differs only in case from 'p1'"
    assert _id_problem("P1", {"P1": Portfolio()}) is None


def _table(kind: str, *rows: list[str], unit: str | None = None) -> list[list[str]]:
    meta = [["Portfolio ID", "P1"]] + ([["Unit", unit]] if unit else [])
    return [*meta, [], POS if kind == "positions" else LIM, *rows]


def test_short_and_blank_rows_and_uncached_cells() -> None:
    found: dict[str, Portfolio] = {}
    rows = _table(
        "positions",
        ["A", "Acme", "5"],
        [],
        ["B", "Beta", "6", "2%"],
        ["C", "Gamma", "7", "3%"],
        ["Z"],
    )
    assert read_sheet("p.csv", rows, found, {6: "B6"}) == []
    p = found["P1"]
    assert [x["issuer_id"] for x in p.positions] == ["C"]
    assert p.unparsed == [
        {"row": "p.csv row 4", "reason": "par or % NAV is not a number"},
        {"row": "p.csv row 6", "reason": "formula B6 has no stored value"},
        {"row": "p.csv row 8", "reason": "par or % NAV is not a number"},
    ]
    good = ["C1", "Single Name", "x", "≤ 2% NAV", "Hard", "1%"]
    limits = _table("limits", good, [], ["C2", "Single Name"])
    assert read_sheet("l.csv", limits, found, {4: "F4"}) == []
    assert p.limits == [] and p.unparsed[3:] == [
        {"row": "l.csv row 4", "reason": "formula F4 has no stored value"},
        {"row": "l.csv row 6", "reason": "no Hard or Soft breach type (info only)"},
    ]
    second = ["C2", "Single Name", "y", "≤ 3% NAV", "Hard", "2%"]
    other: dict[str, Portfolio] = {}
    assert read_sheet("m.csv", _table("limits", good, [], second), other, {}) == []
    assert [x["limit_id"] for x in other["P1"].limits] == ["C1", "C2"]
    assert other["P1"].unparsed == []


def test_mixed_units_in_a_position_are_unparsed() -> None:
    for par, pct in (("5%", "1%"), ("5", "1")):
        found: dict[str, Portfolio] = {}
        read_sheet("p.csv", _table("positions", ["A", "Acme", par, pct]), found, {})
        assert found["P1"].unparsed == [
            {
                "row": "p.csv row 4",
                "reason": f"par {par!r} must be a plain amount and % NAV {pct!r} a percent",
            }
        ]


def test_a_scaled_unit_in_either_table_refuses_the_amount_limit(rules: Rules) -> None:
    row = ["C1", "Single Name", "x", "≤ $5", "Hard", "$1"]
    found: dict[str, Portfolio] = {}
    read_sheet("p.csv", _table("positions", unit="USD"), found, {})
    read_sheet("l.csv", _table("limits", row, unit="MILLIONS"), found, {})
    data = to_json(found["P1"], rules)
    assert data["limits"] == [] and "MILLIONS" in data["unparsed"][0]["reason"].upper()
    other: dict[str, Portfolio] = {}
    read_sheet("p.csv", _table("positions", unit="MILLIONS"), other, {})
    read_sheet("l.csv", _table("limits", row), other, {})
    data = to_json(other["P1"], rules)
    assert data["limits"] == [] and "MILLIONS" in data["unparsed"][0]["reason"].upper()


def test_notes_come_back_once_per_sheet_and_all_of_them() -> None:
    found: dict[str, Portfolio] = {}
    rating = ["C1", "Rating", "x", "≤ 2% NAV", "Hard", "1%"]
    both = [*_table("positions"), *_table("limits", rating)[1:]]
    first = read_sheet("a.csv", both, found, {})
    assert len(first) == 1 and "Rating limit 'Rating' names no bucket" in first[0]
    assert read_sheet("b.csv", both, found, {}) == [
        "b.csv: second positions table for 'P1' not merged (a.csv kept)",
        "b.csv: second limits table for 'P1' not merged (a.csv kept)",
    ]


def test_the_json_of_a_bare_portfolio_has_exact_defaults(rules: Rules) -> None:
    found: dict[str, Portfolio] = {}
    read_sheet("p.csv", _table("positions"), found, {})
    assert to_json(found["P1"], rules) == {
        "schema": "rbot-portfolio/1",
        "portfolio_id": "P1",
        "portfolio_name": "",
        "strategy": "",
        "as_of": "",
        "nav": "",
        "par": "",
        "currency": "",
        "unit": "",
        "positions_file": "p.csv",
        "limits_file": "",
        "positions": [],
        "limits": [],
        "unparsed": [
            {"row": "Total NAV", "reason": "missing or not a number"},
            {"row": "Total PAR", "reason": "missing or not a number"},
            {"row": "As of", "reason": "'' is not a date I can read as yyyy-mm-dd"},
            {"row": "Strategy", "reason": "None is not a Strategy"},
        ],
        "notes": [],
    }


def test_portfolio_files_are_indented_utf8_json_in_a_new_folder(
    tmp_path: Path, rules: Rules
) -> None:
    found = {"P1": Portfolio(meta={"portfolio_name": "Café"})}
    assert write_all(tmp_path, found, rules) == [
        {"portfolio_id": "P1", "json": "prepared/portfolios/P1.json"}
    ]
    text = (tmp_path / "prepared" / "portfolios" / "P1.json").read_text(encoding="utf-8")
    assert text == json.dumps(to_json(found["P1"], rules), indent=2, ensure_ascii=False) + "\n"
    assert "Café" in text and text.startswith('{\n  "schema"')


def test_a_limits_only_portfolio_and_a_bad_as_of_report_exactly(rules: Rules) -> None:
    found: dict[str, Portfolio] = {}
    rows = [["Portfolio ID", "P1"], ["As of", "05/29/2026"], [], LIM]
    read_sheet("l.csv", rows, found, {})
    data = to_json(found["P1"], rules)
    assert (data["positions_file"], data["limits_file"], data["as_of"]) == ("", "l.csv", "")
    assert {"row": "As of", "reason": "'05/29/2026' is not a date I can read as yyyy-mm-dd"} in (
        data["unparsed"]
    )


def test_the_portfolio_folder_names_are_exact(tmp_path: Path, rules: Rules) -> None:
    write_all(tmp_path, {"P1": Portfolio()}, rules)
    assert [p.name for p in tmp_path.iterdir()] == ["prepared"]
    assert [p.name for p in (tmp_path / "prepared").iterdir()] == ["portfolios"]
