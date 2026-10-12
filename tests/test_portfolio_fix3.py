"""02G round 3 refuses table boundaries and contradictory metadata."""

from pathlib import Path

import pytest
from test_portfolio_fixes import AMOUNT, LIM, POS, _json


@pytest.mark.parametrize(
    "footer",
    ["Portfolio ID,P2", "Note,other table", "Unit,USD", "Total NAV,7", "Total NAV,Label,1,1%"],
)
def test_footer_refuses_sheet(tmp_path: Path, footer: str) -> None:
    data, notes = _json(tmp_path, {"p.csv": POS.format(unit="") + footer + "\nB,Beta,2,2%\n"})
    assert data == {} and "more than one table" in notes[0]


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("", "amount unit not stated"),
        ("Unit,\n", "amount unit not stated"),
        ("Unit,MILLIONS\nUnit,USD\n", "more than one Unit row"),
        ("Units,MILLIONS\n", "unit evidence RBOT cannot read"),
        ("Unit:,MILLIONS\n", "unit evidence RBOT cannot read"),
        ("Currency,USD,millions\n", "unit evidence RBOT cannot read"),
        ("Unit,USD\nTotal NAV,100,USD millions\n", "unit evidence RBOT cannot read"),
    ],
)
def test_amount_requires_single_explicit_unit(tmp_path: Path, row: str, reason: str) -> None:
    d = _json(tmp_path, {"p.csv": POS.format(unit=row), "l.csv": LIM.format(unit="") + AMOUNT})[0][
        "P1"
    ]
    assert d["limits"] == [] and any(reason in x["reason"] for x in d["unparsed"])


@pytest.mark.parametrize("row", ["Portfolio ID,P2", "Portfolio ID,P1,P2", "As of,2025-12-31"])
def test_duplicate_identity_or_date_refuses_sheet(tmp_path: Path, row: str) -> None:
    data, notes = _json(tmp_path, {"p.csv": row + "\n" + POS.format(unit="")})
    assert data == {} and notes


@pytest.mark.parametrize(
    ("row", "key"),
    [("Total NAV,9", "nav"), ("Total Par,9", "par"), ("As of,2026-05-29,2025-12-31", "as_of")],
)
def test_repeated_total_or_multi_date_is_unparsed(tmp_path: Path, row: str, key: str) -> None:
    text = POS.format(unit="")
    if key == "as_of":
        text = text.replace("As of,2026-05-29", row)
    else:
        text = row + "\n" + text
    d = _json(tmp_path, {"p.csv": text})[0]["P1"]
    assert d[key] == "" and d["unparsed"]


@pytest.mark.parametrize("kind", ["positions", "limits"])
def test_split_tables_emit_no_json(tmp_path: Path, kind: str) -> None:
    text = POS.format(unit="") if kind == "positions" else LIM.format(unit="") + AMOUNT
    data, notes = _json(tmp_path, {"a.csv": text, "b.csv": text})
    assert data == {}
    assert any(
        f"{kind} for P1 are in more than one table (a.csv, b.csv); combine them into one table" in n
        for n in notes
    )


def test_refused_positions_trace_in_limits_json(tmp_path: Path) -> None:
    pos = POS.format(unit="") + "Note,other\n"
    d = _json(tmp_path, {"a.csv": pos, "b.csv": LIM.format(unit="") + AMOUNT})[0]["P1"]
    assert d["positions"] == [] and any(
        "a.csv" in n and "more than one table" in n for n in d["notes"]
    )


def test_summary_unit_evidence_blocks_amount(tmp_path: Path) -> None:
    files = {
        "a.csv": POS.format(unit="Unit,USD\n"),
        "b.csv": LIM.format(unit="") + AMOUNT,
        "c.csv": "Portfolio ID,P1\nUnit,MILLIONS\n",
    }
    d = _json(tmp_path, files)[0]["P1"]
    assert d["limits"] == [] and any(
        "unit evidence RBOT cannot read" in u["reason"] for u in d["unparsed"]
    )


@pytest.mark.parametrize("source", ["footer", "summary", "total"])
def test_unscaled_unit_outside_metadata_cannot_authorize_amount(
    tmp_path: Path, source: str
) -> None:
    pos = POS.format(unit="Unit,USD\n" if source == "total" else "")
    files = {"a.csv": pos, "b.csv": LIM.format(unit="") + AMOUNT}
    if source == "footer":
        files["a.csv"] += "Unit,USD\n"
    elif source == "summary":
        files["c.csv"] = "Portfolio ID,P1\nUnit,USD\n"
    else:
        files["a.csv"] = pos.replace("Total NAV,630.9", "Total NAV,630.9 USD millions")
    d = _json(tmp_path, files)[0]["P1"]
    assert d["limits"] == []
    assert any("unit evidence RBOT cannot read" in u["reason"] for u in d["unparsed"])


def test_uncached_footer_does_not_join_table() -> None:
    import csv
    import io

    from rbotlib.portfolio import Portfolio, read_sheet

    rows = list(csv.reader(io.StringIO(POS.format(unit="") + "Total NAV,\n")))
    found: dict[str, Portfolio] = {}
    notes = read_sheet("p.csv", rows, found, {len(rows): "B10"})
    assert notes == [
        "p.csv: more than one table in this sheet; "
        "put each portfolio table on its own sheet or file"
    ]
    assert found["P1"].positions == []


def test_meta_preserves_duplicate_and_blank_evidence() -> None:
    from rbotlib.portfolio import _meta

    notes: list[str] = []
    values, extras = _meta([["Total NAV", "5"], ["Total NAV"], ["Unit"]], notes, "p.csv")
    assert values == {"nav": "5", "unit": ""}
    assert extras == {"nav": ["5", ""]}
    assert notes == ["p.csv: more than one Total NAV row; not read"]
    values, extras = _meta([["Total Par", "5"], ["Total Par", "9"]], [], "p.csv")
    assert values == {"par": "5"} and extras == {"par": ["5", "9"]}


def test_multi_value_identity_is_not_a_portfolio(tmp_path: Path) -> None:
    text = POS.format(unit="").replace("Portfolio ID,P1", "Portfolio ID,P1,P2")
    data, notes = _json(tmp_path, {"p.csv": text})
    assert data == {}
    assert notes == ["p.csv: Portfolio ID row does not have exactly one value; sheet refused"]


@pytest.mark.parametrize("unit", ["USD", "EUR", "GBP", "units"])
def test_one_unscaled_unit_keeps_amount(tmp_path: Path, unit: str) -> None:
    d = _json(
        tmp_path,
        {"p.csv": POS.format(unit=f"Unit,{unit}\n"), "l.csv": LIM.format(unit="") + AMOUNT},
    )[0]["P1"]
    assert [x["limit_id"] for x in d["limits"]] == ["C-01"]


@pytest.mark.parametrize(
    "row", ["Amounts in,USD millions", "Currency,USD millions", "Unit,USD,EUR", "Total NAV,100,200"]
)
def test_unit_evidence_reason_names_full_row(tmp_path: Path, row: str) -> None:
    d = _json(
        tmp_path, {"p.csv": POS.format(unit=row + "\n"), "l.csv": LIM.format(unit="") + AMOUNT}
    )[0]["P1"]
    reason = next(u["reason"] for u in d["unparsed"] if u["row"].startswith("l.csv"))
    expected = (
        "ambiguous Unit row: USD, EUR"
        if row.startswith("Unit,")
        else "unit evidence RBOT cannot read: " + row.replace(",", ", ")
    )
    assert reason == expected


def test_blank_unit_reason_is_exact(tmp_path: Path) -> None:
    d = _json(tmp_path, {"p.csv": POS.format(unit=""), "l.csv": LIM.format(unit="") + AMOUNT})[0][
        "P1"
    ]
    assert d["unparsed"][-1]["reason"] == "amount unit not stated"


def test_summary_unit_at_first_row_is_not_evidence_for_amount(tmp_path: Path) -> None:
    d = _json(
        tmp_path,
        {
            "p.csv": POS.format(unit=""),
            "l.csv": LIM.format(unit="") + AMOUNT,
            "s.csv": "Unit,USD\nPortfolio ID,P1\n",
        },
    )[0]["P1"]
    assert d["unparsed"][-1]["reason"] == "unit evidence RBOT cannot read: Unit, USD"


def test_blocked_portfolio_does_not_prevent_other_json(tmp_path: Path) -> None:
    text = POS.format(unit="")
    data, _ = _json(tmp_path, {"a.csv": text, "b.csv": text, "c.csv": text.replace("P1", "P2")})
    assert list(data) == ["P2"]


@pytest.mark.parametrize("first", [["Note"], ["A", "Acme", "1"]])
def test_first_nondata_row_refuses_sheet(first: list[str]) -> None:
    from rbotlib.portfolio import Portfolio, read_sheet

    rows = [
        ["Portfolio ID", "P1"],
        ["Issuer ID", "Issuer", "Par", "% NAV"],
        first,
        ["B", "Beta", "2", "2%"],
    ]
    found: dict[str, Portfolio] = {}
    assert "more than one table" in read_sheet("p.csv", rows, found, {})[0]


def test_uncached_data_row_keeps_its_row_number() -> None:
    from rbotlib.portfolio import Portfolio, read_sheet

    rows = [["Portfolio ID", "P1"], ["Issuer ID", "Issuer", "Par", "% NAV"], ["A", "Acme", "1"]]
    found: dict[str, Portfolio] = {}
    assert read_sheet("p.csv", rows, found, {3: "D3"}) == []
    assert found["P1"].unparsed == [
        {"row": "p.csv row 3", "reason": "formula D3 has no stored value"}
    ]
