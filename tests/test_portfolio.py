from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from builders import make_run
from rbotlib.cli import main
from rbotlib.portfolio import Portfolio, number, parse_limit, read_sheet, to_json
from rbotlib.prepare import load_index
from rbotlib.rules import Rules

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
    [
        ("$630,928,502", ("630928502", "")),
        ("2.37%", ("2.37", "%")),
        ("4.82 yrs", ("4.82", "years")),
        ("8 Years", ("8", "years")),
        ("313 bps", ("313", "bps")),
    ],
)
def test_numbers_lose_their_symbols_but_keep_their_digits(
    text: str, expected: tuple[str, str]
) -> None:
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


@pytest.mark.parametrize("unsafe", ["../x", "a/b", ".hidden", ".."])
def test_an_unsafe_portfolio_id_is_a_note_and_writes_no_file(tmp_path: Path, unsafe: str) -> None:
    run, notes = _prepare(tmp_path, {"positions.csv": POSITIONS.replace("TEST_CLO_I", unsafe)})
    assert len(notes) == 1 and f"unsafe Portfolio ID {unsafe!r}" in notes[0]
    assert not (run / "prepared" / "portfolios").exists() or not any(
        (run / "prepared" / "portfolios").iterdir()
    )
    assert not (run / "prepared" / "x.json").exists()


HEADER = [
    "ID",
    "Constraint Category",
    "Parameter",
    "Limit",
    "Breach Type",
    "Source",
    "Current Value",
]


def _read(*limits: list[str], meta: list[list[str]] | None = None) -> tuple[Portfolio, list[str]]:
    rows = [["Portfolio ID", "P1"], *(meta or []), [], HEADER, *limits]
    found: dict[str, Portfolio] = {}
    notes = read_sheet("l.csv", rows, found, {})
    return found["P1"], notes


def _limit(
    limit: str, current: str, category: str = "Single Name", name: str = "Max x"
) -> list[str]:
    return ["C1", category, name, limit, "Hard", "", current]


@pytest.mark.parametrize(
    ("limit", "current", "why"),
    [
        ("≤ 2.5% NAV", "313 bps", "bps"),
        ("≤ 2.5% NAV", "2.37 yrs", "years"),
        ("≤ 2.5% NAV", "0.0237", "bare"),
        ("≤ 8.0 years", "4.8%", "%"),
        ("≤ 8.0 years", "4.8", "bare"),
        ("≤ $5,000,000", "2.0%", "%"),
        ("≤ 25", "2.0%", "%"),
    ],
)
def test_e2_a_current_value_unit_that_disagrees_with_the_limit_is_unparsed(
    limit: str, current: str, why: str
) -> None:
    name = "Max number of issuers" if limit == "≤ 25" else "Max x"
    p, _ = _read(_limit(limit, current, name=name))
    assert p.limits == [] and len(p.unparsed) == 1
    assert why in p.unparsed[0]["reason"] and "not converted" in p.unparsed[0]["reason"]


def test_e2_an_amount_limit_under_a_scaled_unit_is_never_scaled_silently(rules: Rules) -> None:
    row = _limit("≤ $25,000,000", "$1,000,000")
    scaled = to_json(_read(row, meta=[["Unit", "MILLIONS"]])[0], rules)
    assert scaled["limits"] == [] and "MILLIONS" in scaled["unparsed"][0]["reason"].upper()
    plain = to_json(_read(row, meta=[["Unit", "USD"]])[0], rules)
    assert plain["limits"][0]["limit_value"] == "25000000"
    assert not any("amount limit" in u["reason"] for u in plain["unparsed"])


def test_e3_a_bare_limit_number_needs_a_count_parameter() -> None:
    assert parse_limit("≤ 25") == "limit '≤ 25': unit not recognised"
    assert parse_limit("≤ 25", "Max number of issuers") == ("25", "count")


def test_e4_a_second_table_or_conflicting_meta_is_a_note_not_a_merge() -> None:
    p, _ = _read(_limit("≤ 2.5% NAV", "1%"), meta=[["As of", "2026-05-29"]])
    found = {"P1": p}
    other = [["Portfolio ID", "P1"], ["As of", "2026-06-30"], [], HEADER, _limit("≤ 9% NAV", "1%")]
    notes = read_sheet("m.csv", other, found, {})
    assert [lim["limit_value"] for lim in p.limits] == ["2.5"] and p.meta["as_of"] == "2026-05-29"
    assert any("second limits table" in n for n in notes)
    assert any("as_of" in n and "2026-06-30" in n for n in notes)


def test_e5_a_rating_limit_without_a_bucket_has_no_scope_value() -> None:
    p, notes = _read(_limit("≤ 7.5% NAV", "1%", category="Rating"))
    assert p.limits[0]["scope"] == "rating_bucket" and p.limits[0]["scope_value"] is None
    assert any("Rating" in n and "bucket" in n for n in notes)


def test_e6_e8_totals_are_plain_amounts_and_as_of_is_iso(rules: Rules) -> None:
    rows = [
        ["Portfolio ID", "P1"],
        ["Total NAV", "5%"],
        ["Total Par", "$10"],
        ["As of", "05/29/2026"],
    ]
    found: dict[str, Portfolio] = {}
    read_sheet("p.csv", [*rows, [], ["Issuer ID", "Issuer", "Par", "% NAV"]], found, {})
    data = to_json(found["P1"], rules)
    reasons = {u["row"] for u in data["unparsed"]}
    assert {"Total NAV", "As of"} <= reasons and "Total Par" not in reasons
    assert (data["nav"], data["par"], data["as_of"]) == ("", "10", "")


@pytest.mark.parametrize("text", ["2026-05-29", "May 29, 2026", "29 May 2026", "29 may 2026"])
def test_e8_dates_are_normalised_to_iso(rules: Rules, text: str) -> None:
    found: dict[str, Portfolio] = {}
    rows: list[list[Any]] = [
        ["Portfolio ID", "P1"],
        ["As of", text],
        [],
        ["Issuer ID", "Issuer", "Par", "% NAV"],
    ]
    read_sheet("p.csv", rows, found, {})
    assert to_json(found["P1"], rules)["as_of"] == "2026-05-29"


def test_e7_a_positions_header_without_an_id_is_not_linked() -> None:
    found: dict[str, Portfolio] = {}
    notes = read_sheet("p.csv", [["Issuer ID", "Issuer", "Par", "% NAV"]], found, {})
    assert notes == ["p.csv: positions table without a Portfolio ID row; not linked"]
    assert found == {}


@pytest.mark.parametrize("bad", ["CON", "nul", "Com1", "LPT9", "aux", "PRN", "con.v2", "A" * 101])
def test_e1_reserved_and_overlong_ids_are_notes_and_write_no_file(tmp_path: Path, bad: str) -> None:
    run, notes = _prepare(tmp_path, {"positions.csv": POSITIONS.replace("TEST_CLO_I", bad)})
    assert len(notes) == 1 and "unsafe Portfolio ID" in notes[0]
    assert not (run / "prepared" / "portfolios").exists() or not any(
        (run / "prepared" / "portfolios").iterdir()
    )


def test_e4_ids_that_differ_only_in_case_never_overwrite_each_other(tmp_path: Path) -> None:
    files = {"a.csv": POSITIONS, "b.csv": LIMITS.replace("TEST_CLO_I", "Test_CLO_I")}
    run, notes = _prepare(tmp_path, files)
    assert len(notes) == 1 and "differs only in case" in notes[0] and "Test_CLO_I" in notes[0]
    assert [p["portfolio_id"] for p in load_index(run)["portfolios"]] == ["TEST_CLO_I"]
    data = json.loads((run / "prepared" / "portfolios" / "TEST_CLO_I.json").read_text())
    assert len(data["positions"]) == 2 and data["limits"] == []
