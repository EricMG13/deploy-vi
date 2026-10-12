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
    args = ["score", "--sheets", *map(str, SHEETS[:2]), "--c-b", "25/25", "--f-b", "0.95"]
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
    two = ["score", "--order", order, "--sheets", str(SHEETS[0]), str(SHEETS[2]), "--c-b", "1"]
    assert ab_grade.main(two) == 3
    assert json.loads(capsys.readouterr().out) == {"third_grader_needed": ["D1", "D2", "D5", "G"]}
    three = ["score", "--order", order, "--sheets", *map(str, SHEETS), "--c-b", "0.96"]
    assert ab_grade.main(three) == 0
    assert json.loads(capsys.readouterr().out)["scores"]["B"]["D1"] == "3"


@pytest.mark.parametrize(
    ("c_b", "c_a", "f_b", "passes"),
    [("0.96", None, None, True), ("0.94", None, None, False), ("0.96", "0.98", None, False)],
)
def test_the_citation_and_front_page_bars(
    c_b: str, c_a: str | None, f_b: str | None, passes: bool
) -> None:
    from decimal import Decimal

    even = {c: Fraction(2) for c in ab_grade.CRITERIA}
    verdict = ab_grade.verdict(
        {"A": even, "B": even}, Decimal(c_b), Decimal(c_a) if c_a else None, None
    )
    assert verdict["pass"] is passes
    low = ab_grade.verdict({"A": even, "B": even}, Decimal(1), None, Decimal("0.89"))
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
        ab_grade.main(["score", "--order", order, "--sheets", str(bad), str(bad), "--c-b", "1"])
        == 2
    )
    assert "criterion D1: scores '2', 'x' are not 0-3" in capsys.readouterr().out
    bad.write_text(
        "| criterion | X | Y | reason |\n|---|---|---|---|\n| D1 | 2 | 3 | - |\n", "utf-8"
    )
    assert (
        ab_grade.main(["score", "--order", order, "--sheets", str(bad), str(bad), "--c-b", "1"])
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
