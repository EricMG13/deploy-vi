"""02G fix round 1: unit decided after linking, stacked tables, counts, commas, notes."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from builders import make_run
from rbotlib.cli import main
from rbotlib.portfolio import Table, _limit_row, _position_values, number, parse_limit
from rbotlib.prepare import load_index

POS = (
    "Portfolio ID,P1\nStrategy,CLO\nAs of,2026-05-29\n{unit}Total NAV,630.9\nTotal Par,634.0\n\n"
    "Issuer ID,Issuer,Par,% NAV\nCZR,Caesars,6.0,0.95%\n"
)
LIM_HEAD = "ID,Constraint Category,Parameter,Limit,Breach Type,Current Value\n"
LIM = "Portfolio ID,P1\n{unit}\n" + LIM_HEAD
AMOUNT = 'C-01,Single Name,Max single issuer,"≤ $25,000,000",Hard,"$6,000,000"\n'


def _json(tmp_path: Path, files: dict[str, str]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    pack = tmp_path / "pack"
    pack.mkdir(parents=True)
    for name, text in files.items():
        (pack / name).write_text(text, encoding="utf-8")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    out = {}
    for item in load_index(run)["portfolios"]:
        out[item["portfolio_id"]] = json.loads((run / item["json"]).read_text(encoding="utf-8"))
    return out, load_index(run)["portfolio_notes"]


def _unit(text: str | None) -> str:
    return "" if text is None else f"Unit,{text}\n"


@pytest.mark.parametrize("order", [("a_pos.csv", "b_lim.csv"), ("b_pos.csv", "a_lim.csv")])
@pytest.mark.parametrize(
    ("pos_unit", "lim_unit", "kept"),
    [
        ("MILLIONS", None, False),
        ("USD millions", None, False),
        ("$mm", None, False),
        ("USD 000s", None, False),
        ("in thousands", None, False),
        ("MILLIONS", "USD", False),
        ("USD", "MILLIONS", False),
        ("USD", "EUR", False),
        ("USD", None, True),
        ("units", "usd", False),
        (None, None, False),
        (None, "GBP", True),
    ],
)
def test_c1_amount_limit_is_decided_after_linking_whatever_the_file_order(
    tmp_path: Path, order: tuple[str, str], pos_unit: str | None, lim_unit: str | None, kept: bool
) -> None:
    files = {
        order[0]: POS.format(unit=_unit(pos_unit)),
        order[1]: LIM.format(unit=_unit(lim_unit)) + AMOUNT,
    }
    data, _ = _json(tmp_path, files)
    d = data["P1"]
    assert [x["limit_id"] for x in d["limits"]] == (["C-01"] if kept else [])
    reasons = [u["reason"] for u in d["unparsed"] if u["row"].startswith(order[1])]
    assert bool(reasons) is not kept
    expected = (
        "more than one Unit row"
        if pos_unit is not None and lim_unit is not None
        else "amount unit not stated"
        if pos_unit is None and lim_unit is None
        else "amount limit under Unit"
    )
    assert all(expected in r for r in reasons)


def test_c1_the_synthetic_pack_with_an_amount_limit_is_refused_in_either_order(
    tmp_path: Path,
) -> None:
    src = Path(__file__).parent / "corpus/synthetic/czr-2026q2-primary"
    lim = (src / "SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv").read_text(encoding="utf-8")
    pos = (src / "SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv").read_text(encoding="utf-8")
    lim += (
        'C-18,Single Name,Max single obligor par,"≤ $25,000,000",Hard,Indenture,"$14,950,000",,\n'
    )
    first, _ = _json(tmp_path / "x", {"A_Limits.csv": lim, "B_Positions.csv": pos})
    second, _ = _json(tmp_path / "y", {"Z_Limits.csv": lim, "A_Positions.csv": pos})
    assert first.keys() == second.keys()
    for d in (first["TEST_CLO_I"], second["TEST_CLO_I"]):
        assert "C-18" not in [x["limit_id"] for x in d["limits"]]
        assert any("millions" in u["reason"] for u in d["unparsed"])


def test_c1_a_unit_row_with_three_cells_keeps_every_value_and_is_noted(tmp_path: Path) -> None:
    pos = POS.format(unit="Unit,MILLIONS,USD\n")
    data, notes = _json(tmp_path, {"a_pos.csv": pos, "b_lim.csv": LIM.format(unit="") + AMOUNT})
    assert data["P1"]["unit"] == "MILLIONS, USD" and data["P1"]["limits"] == []
    assert any("Unit row has extra cells" in n for n in data["P1"]["notes"]) and notes


STACK_POS = "Portfolio ID,{}\nStrategy,CLO\nAs of,2026-05-29\nTotal NAV,100\nTotal Par,100\n\n"
STACK_HEAD = "Issuer ID,Issuer,Par,% NAV\n"


def test_i1_separate_files_give_each_portfolio_its_own_json(tmp_path: Path) -> None:
    def lim(pid: str, value: str) -> str:
        return f"Portfolio ID,{pid}\n\n{LIM_HEAD}C-01,Single Name,Max x,≤ {value} NAV,Hard,0.4%\n"

    pos = STACK_POS.format("P1") + STACK_HEAD + "CZR,Caesars,1,1%\n"
    files = {"a.csv": pos, "b.csv": lim("P1", "2.5%"), "c.csv": lim("P2", "0.5%")}
    data, _ = _json(tmp_path, files)
    assert [x["limit_value"] for x in data["P1"]["limits"]] == ["2.5"]
    assert [x["limit_value"] for x in data["P2"]["limits"]] == ["0.5"]


@pytest.mark.parametrize(
    ("param", "limit", "current", "kept"),
    [
        ("Aggregate top 10 issuers", "≤ 15.0", "11.05", False),
        ("Largest 5 positions", "≤ 12", "9.8", False),
        ("Top 3 obligors", "≤ 0.075", "0.061", False),
        ("Max number of issuers", "≤ 25", "12", True),
        ("Max number of issuers", "≤ 25.5", "12", False),
        ("Max number of issuers", "≤ 25", "12.5", False),
        ("Count of names", "≤ 25", "12", True),
        ("Maximum names", "≤ 25", "12", True),
    ],
)
def test_i2_a_bare_limit_is_a_count_only_when_the_parameter_says_so(
    param: str, limit: str, current: str, kept: bool
) -> None:
    item = {"breach type": "Hard", "limit": limit, "parameter": param, "current value": current}
    result = _limit_row(Table("t", [], 0, {}), 5, item, [])
    assert isinstance(result, dict) is kept
    if isinstance(result, dict):
        assert result["unit"] == "count"


@pytest.mark.parametrize("text", ["0,95%", "2,5%", "$1,00", "1,2,3", "14,95", "1,23,456", ",5"])
def test_i3_a_comma_that_is_not_a_thousands_group_is_ambiguous(text: str) -> None:
    assert number(text) is None
    assert isinstance(parse_limit(f"≤ {text} NAV"), str)


def test_i3_the_reason_names_the_decimal_comma(tmp_path: Path) -> None:
    pos = POS.replace("0.95%", "0,95%")
    data, _ = _json(tmp_path, {"p.csv": pos.replace("6.0,", '"6,0",')})
    assert any("ambiguous decimal comma" in u["reason"] for u in data["P1"]["unparsed"])
    lim = LIM.format(unit="") + 'C-02,Single Name,Max x,"≤ 2,5% NAV",Hard,1%\n'
    data, _ = _json(tmp_path / "b", {"l.csv": lim})
    assert any("ambiguous decimal comma" in u["reason"] for u in data["P1"]["unparsed"])


@given(n=st.integers(0, 10**12), k=st.integers(0, 6))
def test_i3_valid_thousands_groups_round_trip(n: int, k: int) -> None:
    d = Decimal(n).scaleb(-k)
    assert number(f"{d:,f}") == (format(d, "f"), "")


@pytest.mark.parametrize("total", ["0", "-5", "0.0"])
def test_m3_a_total_that_is_not_above_zero_is_unparsed(tmp_path: Path, total: str) -> None:
    text = POS.format(unit="").replace("Total NAV,630.9", f"Total NAV,{total}")
    d = _json(tmp_path, {"p.csv": text})[0]["P1"]
    assert d["nav"] == "" and d["par"] == "634.0"
    assert [u["row"] for u in d["unparsed"]] == ["Total NAV"]


def test_m5_the_portfolio_notes_are_in_the_json(tmp_path: Path) -> None:
    pos = POS.format(unit="")
    data, notes = _json(tmp_path, {"a.csv": pos, "b.csv": pos})
    assert data == {} and "positions for P1 are in more than one table" in notes[0]


@given(
    par=st.sampled_from(["6.0", "$6.0", "6,000,000", "6%", "6 bps"]),
    pct=st.sampled_from(["0.95", "0.0095", "95 bps", "0.95 yrs", "$0.95", "0.95%", "95%"]),
)
def test_i7_positions_accept_only_a_plain_par_and_a_percent_nav(par: str, pct: str) -> None:
    result = _position_values({"par": par, "pct_nav": pct})
    assert (not isinstance(result, str)) is (pct.endswith("%") and par[-1].isdigit())


def test_i7_every_reason_and_note_is_worded_exactly(tmp_path: Path) -> None:
    comma = " (ambiguous decimal comma)"
    for par, pct, why in [("6,0", "1%", comma), ("6", "1,5%", comma), ("x", "1%", "")]:
        item = {"par": par, "pct_nav": pct}
        assert _position_values(item) == f"par or % NAV is not a number{why}"
    pos = POS.format(unit="Unit,MILLIONS,USD,GBP\n")
    data, notes = _json(tmp_path, {"a.csv": pos})
    expected = "a.csv: Unit row has extra cells ['USD', 'GBP']; read 'MILLIONS'"
    assert data["P1"]["notes"] == notes == [expected]
    assert _limit_row(Table("t", [], 0, {}), 5, _item("≤ 2,5% NAV", "1%"), []) == (
        "limit '≤ 2,5% NAV' is not a number" + comma + " with a unit"
    )
    assert _limit_row(Table("t", [], 0, {}), 5, _item("≤ 2.5% NAV", "1,5%"), []) == (
        "current value '1,5%' is not a number" + comma
    )


def _item(limit: str, current: str, param: str = "Max x") -> dict[str, str]:
    return {"breach type": "Hard", "limit": limit, "parameter": param, "current value": current}


@pytest.mark.parametrize(
    ("limit", "current", "param", "kept"),
    [("≤ 25", "13.0", "Max number of issuers", True), ("≤ 25", "13.5", "Count of names", False)],
)
def test_i7_a_whole_count_written_with_a_decimal_point_is_kept(
    limit: str, current: str, param: str, kept: bool
) -> None:
    result = _limit_row(Table("t", [], 0, {}), 5, _item(limit, current, param), [])
    assert isinstance(result, dict) is kept


def test_i7_totals_of_one_and_less_than_one_are_read_and_reasons_are_exact(tmp_path: Path) -> None:
    for total in ("1", "0.5"):
        assert (
            _json(tmp_path / total, {"p.csv": POS.format(unit="").replace("630.9", total)})[0][
                "P1"
            ]["nav"]
            == total
        )
    text = POS.format(unit="").replace("630.9", "0")
    unparsed = _json(tmp_path / "z", {"p.csv": text})[0]["P1"]["unparsed"]
    assert unparsed == [
        {"row": "Total NAV", "reason": "'0' is not a plain amount above zero", "kind": "meta"}
    ]


def test_i7_conflicting_units_are_named_in_the_reason(tmp_path: Path) -> None:
    files = {
        "a.csv": POS.format(unit="Unit,MILLIONS\n"),
        "b.csv": LIM.format(unit="Unit,USD\n") + AMOUNT,
    }
    reason = _json(tmp_path, files)[0]["P1"]["unparsed"][-1]["reason"]
    assert reason == "more than one Unit row"


def test_i7_a_note_row_below_the_table_is_an_unparsed_row(tmp_path: Path) -> None:
    text = STACK_POS.format("P1") + STACK_HEAD + "CZR,Caesars,6.0,6%\nNote,two cells\n"
    data, _ = _json(tmp_path, {"two.csv": text})
    assert data == {}
