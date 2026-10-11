from __future__ import annotations

import json
from pathlib import Path

import pytest

from builders import make_run
from rbotlib.cli import main
from rbotlib.portfolio import number, parse_limit
from rbotlib.prepare import load_index

POSITIONS = """SYNTHETIC test positions
Portfolio ID,TEST_CLO_I
Portfolio,Test CLO I Ltd
Strategy,CLO
As of,2026-05-29
Currency,USD
Unit,MILLIONS
Total NAV,630.9
Total Par,634.0

Issuer ID,Issuer,Instrument ID,Par,% NAV,Sector,Rating,Country,Currency,Seniority,Asset Type
CZR,Caesars Entertainment,CZR TLB-B1,6.0,0.95%,Gaming,B1,US,USD,Senior secured,Loan
ASU,Asurion,ASU TL,"14.95",2.37%,Insurance,B3,US,USD,Senior secured,Loan
BAD,Broken row,X,n/a,1%,Software,B2,US,USD,Senior secured,Loan
"""
LIMITS = """SYNTHETIC test limits
Portfolio ID,TEST_CLO_I

ID,Constraint Category,Parameter,Limit,Breach Type,Source Document,Current Value
C-01,Single Name,Max single issuer exposure (largest: Asurion),≤ 2.5% NAV,Hard,Indenture,2.37%
C-04,Rating — CCC Bucket,Max CCC+ and below,≤ 7.5% NAV,Hard,Indenture,7.36%
C-07,Sector,2nd largest sector: Commercial Support Services,≤ 10.0% NAV,Soft,Indenture,6.74%
C-09,Instrument,Min 1st Lien / Senior Secured,≥ 90.0% NAV,Hard,Indenture,99.39%
C-10,Instrument,Max 2nd Lien / Unsecured,≤ 10.0% NAV,Soft,Indenture,0.61%
C-11,Duration / Maturity,Max WAL (weighted avg life),≤ 8.0 years,Soft,Indenture,4.82 yrs
C-15,Pricing,WA Mid Price,Info only,—,—,99.578
C-17,ESG / Exclusion,"Excluded sectors (Tobacco, Thermal Coal)",0% NAV,Hard,Indenture,0%
"""


MINIMUM = "minimum limit: Portfolio Fit sizes against maximum limits only"


def _prepare(tmp_path: Path, files: dict[str, str]) -> tuple[Path, list[str]]:
    pack = tmp_path / "pack"
    pack.mkdir()
    for name, text in files.items():
        (pack / name).write_text(text, encoding="utf-8")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run, load_index(run)["portfolio_notes"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("$630,928,502", "630928502"), ("2.37%", "2.37"), ("4.82 yrs", "4.82"), ("313 bps", "313")],
)
def test_numbers_lose_their_symbols_but_keep_their_digits(text: str, expected: str) -> None:
    assert number(text) == expected


def test_words_are_not_numbers() -> None:
    assert number("B1 (14.3)") is None
    assert number("n/a") is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("≤ 2.5% NAV", ("2.5", "pct_nav")),
        ("<= 15.0% par", ("15.0", "pct_par")),
        ("≤ 8.0 years", ("8.0", "years")),
        ("≤ $25,000,000", ("25000000", "amount")),
        ("≤ 25", ("25", "count")),
        ("0% NAV", ("0", "pct_nav")),
    ],
)
def test_maximum_limits_parse_to_value_and_unit(text: str, expected: tuple[str, str]) -> None:
    assert parse_limit(text) == expected


def test_minimum_and_wordy_limits_give_a_reason() -> None:
    assert (
        parse_limit("≥ 90.0% NAV")
        == "minimum limit: Portfolio Fit sizes against maximum limits only"
    )
    assert (
        parse_limit("≥ Caa1 (numeric ≤ 17)")
        == "limit '≥ Caa1 (numeric ≤ 17)' is not a number with a unit"
    )


def test_positions_and_limits_become_one_portfolio_json(tmp_path: Path) -> None:
    run, notes = _prepare(tmp_path, {"positions.csv": POSITIONS, "limits.csv": LIMITS})
    assert notes == []
    data = json.loads((run / "prepared" / "portfolios" / "TEST_CLO_I.json").read_text())
    assert data["schema"] == "rbot-portfolio/1"
    assert (data["portfolio_name"], data["strategy"], data["as_of"]) == (
        "Test CLO I Ltd",
        "CLO",
        "2026-05-29",
    )
    assert (data["nav"], data["par"], data["currency"], data["unit"]) == (
        "630.9",
        "634.0",
        "USD",
        "MILLIONS",
    )
    assert (data["positions_file"], data["limits_file"]) == ("positions.csv", "limits.csv")
    assert data["positions"][0] == {
        "issuer_id": "CZR",
        "issuer_name": "Caesars Entertainment",
        "instrument_id": "CZR TLB-B1",
        "par": "6.0",
        "pct_nav": "0.95",
        "sector": "Gaming",
        "rating": "B1",
        "country": "US",
        "currency": "USD",
        "seniority": "Senior secured",
        "asset_type": "Loan",
    }
    scopes = {lim["limit_id"]: (lim["scope"], lim["scope_value"]) for lim in data["limits"]}
    assert scopes == {
        "C-01": ("issuer", None),
        "C-04": ("rating_bucket", "CCC"),
        "C-07": ("sector", "Commercial Support Services"),
        "C-10": ("seniority", "2nd Lien / Unsecured"),
        "C-11": ("other", None),
        "C-17": ("sector", "Tobacco, Thermal Coal"),
    }
    first = data["limits"][0]
    assert (first["limit_value"], first["unit"], first["limit_kind"]) == ("2.5", "pct_nav", "Hard")
    assert (first["current_value"], first["source"]) == ("2.37", "limits.csv row 5")
    assert data["unparsed"] == [
        {"row": "limits.csv row 8", "reason": MINIMUM},
        {
            "row": "limits.csv row 11",
            "reason": "no Hard or Soft breach type (info only)",
        },
        {"row": "positions.csv row 14", "reason": "par or % NAV is not a number"},
    ]
    index = load_index(run)
    assert index["portfolios"] == [
        {"portfolio_id": "TEST_CLO_I", "json": "prepared/portfolios/TEST_CLO_I.json"}
    ]


def test_an_unlinked_table_is_a_note_and_bad_totals_are_unparsed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    orphan = LIMITS.replace("Portfolio ID,TEST_CLO_I\n", "")
    bad = POSITIONS.replace("Total NAV,630.9", "Total NAV,lots").replace(
        "Strategy,CLO", "Strategy,Hedge"
    )
    run, notes = _prepare(tmp_path, {"limits.csv": orphan, "positions.csv": bad})
    assert notes == ["limits.csv: limits table without a Portfolio ID row; not linked"]
    assert (
        "portfolio: limits.csv: limits table without a Portfolio ID row" in capsys.readouterr().out
    )
    data = json.loads((run / "prepared" / "portfolios" / "TEST_CLO_I.json").read_text())
    assert data["nav"] == "" and data["limits"] == []
    assert {"row": "Total NAV", "reason": "missing or not a number"} in data["unparsed"]
    assert {"row": "Strategy", "reason": "'Hedge' is not a Strategy"} in data["unparsed"]
