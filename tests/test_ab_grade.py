"""`scripts/ab_grade.py`, the A/B harness's mechanical parts (interfaces spec section 12.7).

The grader sheets under `tests/fixtures/ab/` are stand-ins written for these tests: sheets 1
and 2 never differ by more than one point (mean of two); sheet 3 differs from sheet 1 by two
on D1, so with sheets 1 and 3 a third grader is needed and the median of three decides.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path

import pytest

import ab_grade
from conftest import CORPUS, FIXTURES
from rbotlib.handoff import parse

AB = FIXTURES / "ab"
SHEETS = [AB / f"grader-{n}.md" for n in (1, 2, 3)]
EXPECTATIONS = FIXTURES.parent / "corpus" / "expectations" / "czr-2026q2-primary.json"
WHO = [
    "--c-a",
    "0.95",
    "--module",
    "CP-1",
    "--expectations",
    str(EXPECTATIONS),
]  # CP-1 owns no Front Page table


def _order(tmp_path: Path, x: str) -> Path:
    out = tmp_path / f"order-{x}.json"
    out.write_text(json.dumps(ab_grade.draw(x)), encoding="utf-8")
    return out


def test_to_r14_keeps_every_table_under_r14s_sections(tmp_path: Path) -> None:
    source = FIXTURES / "handoffs" / "CP-0.md"
    out = tmp_path / "CP-0.r14.md"
    assert ab_grade.main(["to-r14", "--in", str(source), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    h = parse(text)
    assert h.sections == [*ab_grade.R14_SECTIONS, "QA Validation"]
    assert h.front_matter["qa_status"] == "Passed"
    assert "<!-- table-id: cp0.source_inventory -->" in text
    rows = [line for line in source.read_text("utf-8").splitlines() if line.startswith("|")]
    assert len(rows) > 50 and all(line in text.splitlines() for line in rows)


def test_the_order_is_drawn_or_fixed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "order.json"
    assert ab_grade.main(["order", "--out", str(out), "--x", "B"]) == 0
    assert json.loads(out.read_text("utf-8")) == {"X": "B", "Y": "A"}
    assert capsys.readouterr().out == "X=B Y=A\n"
    assert ab_grade.draw() in ({"X": "A", "Y": "B"}, {"X": "B", "Y": "A"})


def test_two_sheets_resolve_to_their_mean_and_map_back_to_a_and_b(tmp_path: Path) -> None:
    sheets = [ab_grade.sheet(p.read_text("utf-8")) for p in SHEETS[:2]]
    resolved = ab_grade.resolve(sheets, {"X": "B", "Y": "A"})["scores"]
    assert resolved["B"]["D1"] == Fraction(5, 2) and resolved["A"]["D1"] == 3
    assert resolved["A"]["D5"] == 3 and resolved["B"]["D5"] == Fraction(3, 2)


def test_score_applies_the_pass_bar(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    args = ["score", "--sheets", *map(str, SHEETS[:2]), "--c-b", "25/25", "--f-b", "0.95", *WHO]
    assert ab_grade.main([*args, "--order", str(_order(tmp_path, "A"))]) == 0  # B is Y
    result = json.loads(capsys.readouterr().out)
    assert result["pass"] and result["scores"]["B"]["D3"] == "2"
    assert ab_grade.main([*args, "--order", str(_order(tmp_path, "B"))]) == 1  # B is X
    lines = json.loads(capsys.readouterr().out)["lines"]
    assert lines == {
        "sum_depth": False,
        "no_criterion_below_a_minus_1": False,
        "citations": True,
        "gaps": False,
        "front_page": True,
    }


def test_a_third_grader_is_needed_then_the_median_decides(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    order = str(_order(tmp_path, "A"))
    two = [
        "score",
        "--order",
        order,
        "--sheets",
        str(SHEETS[0]),
        str(SHEETS[2]),
        "--c-b",
        "1",
        *WHO,
    ]
    assert ab_grade.main(two) == 3
    assert json.loads(capsys.readouterr().out) == {"third_grader_needed": ["D1", "D2", "D5", "G"]}
    three = ["score", "--order", order, "--sheets", *map(str, SHEETS), "--c-b", "0.96", *WHO]
    assert ab_grade.main(three) == 0
    assert json.loads(capsys.readouterr().out)["scores"]["B"]["D1"] == "3"


@pytest.mark.parametrize(
    ("c_b", "c_a", "f_b", "passes"),
    [("0.96", "0.95", None, True), ("0.94", "0.95", None, False), ("0.96", "0.98", None, False)],
)
def test_the_citation_and_front_page_bars(
    c_b: str, c_a: str, f_b: str | None, passes: bool
) -> None:
    from decimal import Decimal

    even = {c: Fraction(2) for c in ab_grade.CRITERIA}
    verdict = ab_grade.verdict({"A": even, "B": even}, Decimal(c_b), Decimal(c_a), None)
    assert verdict["pass"] is passes
    low = ab_grade.verdict({"A": even, "B": even}, Decimal(1), Decimal(1), Decimal("0.89"))
    assert low["lines"]["front_page"] is False


def test_bad_sheets_and_inputs_are_named(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text(
        "| criterion | X | Y | reason |\n|---|---|---|---|\n| D1 | 2 | x | - |\n", "utf-8"
    )
    order = str(_order(tmp_path, "A"))
    assert (
        ab_grade.main(
            ["score", "--order", order, "--sheets", str(bad), str(bad), "--c-b", "1", *WHO]
        )
        == 2
    )
    assert "criterion D1: scores '2', 'x' are not 0-3" in capsys.readouterr().out
    bad.write_text(
        "| criterion | X | Y | reason |\n|---|---|---|---|\n| D1 | 2 | 3 | - |\n", "utf-8"
    )
    assert (
        ab_grade.main(
            ["score", "--order", order, "--sheets", str(bad), str(bad), "--c-b", "1", *WHO]
        )
        == 2
    )
    assert "needs every criterion scored 0-3" in capsys.readouterr().out


@pytest.mark.corpus
def test_measure_on_the_cp3_fixture(
    prepared_run: Callable[[str], Path], capsys: pytest.CaptureFixture[str]
) -> None:
    run = prepared_run("czr-2026q2-primary")
    expectations = (
        FIXTURES.parent / "corpus" / CORPUS.pack("czr-2026q2-primary").data["expectations"]
    )
    handoff = FIXTURES / "handoffs" / "CP-3.md"
    args = ["measure", "--module", "CP-3", "--handoff", str(handoff), "--run", str(run)]
    capsys.readouterr()
    assert ab_grade.main([*args, "--expectations", str(expectations)]) == 0
    measured = json.loads(capsys.readouterr().out)
    assert (measured["validate_exit"], measured["findings"], measured["C"]) == (0, [], "25/25")
    assert measured["F"] == "129/129" and measured["gaps"] == 6  # levels 7 x 9, RV 11 x 6


# --- the up-front review of Plan 05 (rest, I11 I12 M8): every case below failed before its fix --


def _cp3_fill(handoff_text: str) -> str | None:
    from rbotlib.contract import load_contract
    from rbotlib.rules import RBOT_ROOT, load_rules

    rules = load_rules()
    contract = load_contract(RBOT_ROOT / "modules" / "CP-3" / "contract.json", rules)
    return ab_grade.front_page_fill(contract, parse(handoff_text), EXPECTATIONS, rules)


def test_f_counts_a_missing_row_as_unfilled() -> None:
    """I11: a CP-3 cut to one level and one RV row once scored 15/15."""
    text = (FIXTURES / "handoffs" / "CP-3.md").read_text("utf-8")
    assert _cp3_fill(text) == "129/129"
    keep = ("snapshot.instrument_levels", "snapshot.relative_value")
    out, table, seen = [], "", 0
    for line in text.splitlines():
        tag = line.startswith("<!-- table:") and line.removeprefix("<!-- table: ")[:-4]
        if tag:
            table, seen = tag, 0
        elif line.startswith("|") and table in keep:
            seen += 1
            if seen > 3:
                continue
        out.append(line)
    assert _cp3_fill("\n".join(out) + "\n") == "15/129"


def test_f_needs_expected_rows(tmp_path: Path) -> None:
    from rbotlib.contract import load_contract
    from rbotlib.rules import RBOT_ROOT, load_rules

    rules = load_rules()
    contract = load_contract(RBOT_ROOT / "modules" / "CP-3" / "contract.json", rules)
    bare = tmp_path / "e.json"
    bare.write_text(
        json.dumps(
            {"front_pages": {"p": {"supportable": [{"table": "snapshot.instrument_levels"}]}}}
        ),
        encoding="utf-8",
    )
    text = (FIXTURES / "handoffs" / "CP-3.md").read_text("utf-8")
    with pytest.raises(ab_grade.ABError, match=r"snapshot\.instrument_levels needs expected_rows"):
        ab_grade.front_page_fill(contract, parse(text), bare, rules)


def test_score_refuses_a_missing_f_for_a_module_that_owns_front_page_tables(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """I11: the dry run never passed --f-b, and a missing one passed silently."""
    order = str(_order(tmp_path, "A"))
    args = [
        "score",
        "--order",
        order,
        "--sheets",
        *map(str, SHEETS[:2]),
        "--c-b",
        "1",
        "--c-a",
        "1",
    ]
    cp3 = ["--module", "CP-3", "--expectations", str(EXPECTATIONS)]
    assert ab_grade.main([*args, *cp3]) == 2
    assert "--f-b is required: CP-3 owns Front Page tables (snapshot.instrument_levels" in (
        capsys.readouterr().out
    )
    assert ab_grade.main([*args, *cp3, "--f-b", "129/129"]) == 0


@pytest.mark.parametrize("bad", ["0/0", "abc", "1/x", "nan"])
def test_a_bad_ratio_is_named_not_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], bad: str
) -> None:
    order = str(_order(tmp_path, "A"))
    args = ["score", "--order", order, "--sheets", *map(str, SHEETS[:2]), *WHO, "--c-b", bad]
    assert ab_grade.main(args) == 2
    assert f"--c-b: {bad!r} is not a ratio" in capsys.readouterr().out


def test_a_criterion_scored_twice_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    twice = tmp_path / "twice.md"
    twice.write_text(SHEETS[0].read_text("utf-8") + "| D1 | 0 | 3 | extra |\n", encoding="utf-8")
    order = str(_order(tmp_path, "A"))
    args = ["score", "--order", order, "--sheets", str(twice), str(SHEETS[1]), "--c-b", "1", *WHO]
    assert ab_grade.main(args) == 2
    assert "criterion D1 is scored twice" in capsys.readouterr().out


@pytest.mark.corpus
def test_measure_names_a_handoff_it_cannot_read(
    prepared_run: Callable[[str], Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("no front matter", encoding="utf-8")
    run = prepared_run("czr-2026q2-primary")
    args = ["measure", "--module", "CP-3", "--handoff", str(bad), "--run", str(run)]
    assert ab_grade.main(args) == 2
    assert "CP-3: the Handoff cannot be read" in capsys.readouterr().out


def _steps(tmp_path: Path, x: str, folder: str = "cp-1d-earnings-quality") -> int:
    args = ["steps", "--module", "CP-1D", "--folder", folder, "--order", str(_order(tmp_path, x))]
    return ab_grade.main([*args, "--out", str(tmp_path)])


def test_steps_give_the_graders_each_sides_method_without_naming_the_side(tmp_path: Path) -> None:
    """I12: D1 asks whether every step of the method was done, so the graders need the steps."""
    assert _steps(tmp_path, "B") == 0  # X is the rewrite, Y the r14 original
    x = (tmp_path / "steps-X.md").read_text("utf-8")
    y = (tmp_path / "steps-Y.md").read_text("utf-8")
    assert x.startswith("# Method given to side X (CP-1D)") and "The add-back challenge." in x
    assert y.startswith("# Method given to side Y (CP-1D)") and "SKILL.md" in y
    assert _steps(tmp_path, "A") == 0  # the other way round
    assert "SKILL.md" in (tmp_path / "steps-X.md").read_text("utf-8")
    assert "The add-back challenge." in (tmp_path / "steps-Y.md").read_text("utf-8")


def test_steps_refuse_a_folder_outside_the_r14_skills(tmp_path: Path) -> None:
    assert _steps(tmp_path, "B", "../../rbot") == 2
    assert not (tmp_path / "steps-X.md").exists()


def test_r14_conversion_names_the_registers_its_methods_read() -> None:
    text = (FIXTURES / "handoffs" / "CP-1.md").read_text("utf-8")
    converted = ab_grade.to_r14(text)
    assert "#### T4.14 — Model Period Register" in converted
    assert "<!-- table-id: cp1.model_period_register -->" in converted
    assert "<!-- table-id: cp1.model_reconciliation_register -->" in converted
    assert all(line in converted for line in text.splitlines() if line.startswith("|"))
    cp3 = ab_grade.to_r14((FIXTURES / "handoffs" / "CP-3.md").read_text("utf-8"))
    assert "<!-- table-id: T3.5 -->" in cp3
    assert "#### T3.5 — RV Table" in cp3
    assert "<!-- table-id: T3B.8 -->" in cp3


# --- Task 10.7b: R5/F identity matching accepts listed aliases ---------------------------------


def _filled_rows(identities: list[dict[str, object]], rows: list[list[str]]) -> int:
    from rbotlib.handoff import Table
    from rbotlib.rules import load_rules

    entry = {"table": "t", "expected_rows": len(identities), "expected_identities": identities}
    table = Table(["facility_id", "value"], rows)
    return ab_grade._filled(table, {"value"}, entry, load_rules())


def test_a_listed_alias_matches_and_a_string_identity_is_unchanged() -> None:
    ids: list[dict[str, object]] = [
        {"facility_id": ["CEI-SSN-2030", "SSN-2030"]},
        {"facility_id": "B"},
    ]
    assert _filled_rows(ids, [["SSN_2030", "1"], ["b", "2"]]) == 2
    assert _filled_rows(ids, [["SSN30", "1"], ["b", "2"]]) == 1


def test_a_trailing_parenthetical_on_the_record_side_is_ignored() -> None:
    ids: list[dict[str, object]] = [{"facility_id": "Sector Average BB"}]
    assert _filled_rows(ids, [["Sector Average BB (includes Term Loan B)", "1"]]) == 1
    assert _filled_rows(ids, [["Sector (x) Average BB", "1"]]) == 0
    expected_with_paren: list[dict[str, object]] = [{"facility_id": "Sector Average (BB)"}]
    assert _filled_rows(expected_with_paren, [["Sector Average", "1"]]) == 0


def test_an_alias_list_cannot_cover_two_expected_rows_with_one_record() -> None:
    ids: list[dict[str, object]] = [
        {"facility_id": ["A", "SHARED"]},
        {"facility_id": ["B", "SHARED"]},
    ]
    assert _filled_rows(ids, [["SHARED", "1"]]) == 0
    assert _filled_rows(ids, [["SHARED", "1"], ["B", "2"]]) == 1


def test_alias_lists_validate_and_duplicates_use_the_first_spelling() -> None:
    ab_grade._check_identities([{"a": ["X", "Y"]}, {"a": "Z"}], 2, "t")
    for bad in ([{"a": []}, {"a": "Z"}], [{"a": ["X", ""]}, {"a": "Z"}], [{"a": 3}, {"a": "Z"}]):
        with pytest.raises(ab_grade.ABError, match="nonempty text"):
            ab_grade._check_identities(bad, 2, "t")
    with pytest.raises(ab_grade.ABError, match="duplicated"):
        ab_grade._check_identities([{"a": ["X", "Q"]}, {"a": ["x", "R"]}], 2, "t")


def test_f_counts_pre_rc_shaped_rows_against_the_alias_expectations() -> None:
    text = (FIXTURES / "handoffs" / "CP-3.md").read_text("utf-8")
    for old, new in (("CEI-SSN-2030", "SSN_2030"), ("CEI-SSN-2032", "SSN_2032")):
        text = text.replace(f"| {old} |", f"| {new} |")
    text = text.replace("| CEI-SN-2029 |", "| SN_2029 |").replace("| CEI-SN-2032 |", "| SN_2032 |")
    text = text.replace(
        "Gaming sector average, BB |",
        "Sector Ratings Average BB (includes CEI Term Loan B and B-1) |",
    )
    text = text.replace("Gaming sector average, B |", "Sector Ratings Average B |")
    assert "SSN_2030" in text and "Sector Ratings Average B |" in text
    assert _cp3_fill(text) == "129/129"
