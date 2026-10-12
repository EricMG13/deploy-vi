"""The cell reader's guards (up-front review of the non-money modules,
2026-10-11): each case fails on the reader before the fix."""

from __future__ import annotations

from decimal import Decimal

import pytest

from rbotlib.handoff import Table
from rbotlib.model.reader import ModelInputError, rows
from rbotlib.model.reader import figure as read_figure


@pytest.mark.parametrize(
    "cell",
    ["(-5)", "(+5)", "1 2", "2024 2025", "5%x", "5x%", "12 34", "1 2345", "1  234", "5 x y"],
)
def test_text_that_is_not_a_figure_is_refused(cell: str) -> None:
    # I9: `(-5)` read as 5 (a flipped sign), `1 2` as 12, `5%x` as 5.
    assert read_figure(cell) is None


@pytest.mark.parametrize(
    ("cell", "value"),
    [
        ("1 234", "1234"),
        ("12 345 678", "12345678"),
        ("1 234.5", "1234.5"),
        ("-1 234", "-1234"),
        ("(1 234)", "-1234"),
        ("$ 5", "5"),
        ("5 %", "5"),
        ("4.2 x", "4.2"),
    ],
)
def test_digit_groups_of_three_are_read(cell: str, value: str) -> None:
    assert read_figure(cell) == Decimal(value)


def _table(columns: list[str], *rows_: list[str]) -> dict[str, Table]:
    return {"t": Table(columns, [list(r) for r in rows_])}


def test_a_column_written_twice_is_refused() -> None:
    # I9/I7: the second `value` column silently won.
    tables = _table(["id", "value", "value"], ["a", "1", "999999"])
    with pytest.raises(ModelInputError, match="t: column value appears twice"):
        rows(tables, "t", frozenset({"id"}))


@pytest.mark.parametrize("bad", ["\x01", "a\x0bb", "\x1f", "x\x08"])
def test_a_control_character_in_a_cell_is_refused_naming_where(bad: str) -> None:
    # I3: openpyxl refuses such text at the end of the run, after the other files.
    tables = _table(["id", "name"], ["a", "fine"], ["b", f"has {bad} in it"])
    with pytest.raises(ModelInputError, match="t row 2 column name: control character"):
        rows(tables, "t", frozenset({"id"}))


def test_tab_and_ordinary_text_pass_the_control_character_check() -> None:
    tables = _table(["id", "name"], ["a", "café\t—"])
    assert [r.cells["name"] for r in rows(tables, "t", frozenset({"id"}))] == ["café\t—"]
