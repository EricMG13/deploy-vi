"""The figure and cell rules at their edges (the mutation gate's findings on
`rbotlib.model.reader`)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from rbotlib.handoff import Table
from rbotlib.model.reader import ModelInputError, Row, date_cell, decimal, figure, rows


@pytest.mark.parametrize(
    ("cell", "value"),
    [
        ("4[C1]55", None),  # a marker inside a figure splits it, whatever follows
        ("4[C1]x", Decimal(4)),  # a marker before a non-figure character only drops
        ("4 [C1]5", Decimal(45)),  # a spaced marker is dropped with its space
        ("12,3456", None),  # a comma that is neither thousands nor ambiguous
        ("(12", None),  # one parenthesis is not a negative
        ("Infinity", None),
        ("1" * 64, Decimal("1" * 64)),  # 64 characters is the longest figure
        ("1" * 65, None),
    ],
)
def test_figure_edges(cell: str, value: Decimal | None) -> None:
    assert figure(cell) == value


def _row(**cells: str) -> Row:
    return Row("t", 1, cells)


def test_ten_decimals_and_the_date_bounds_are_accepted() -> None:
    assert decimal(_row(v="0.0000000001"), "v") == Decimal("0.0000000001")
    with pytest.raises(ModelInputError, match="more than 10 decimals"):
        decimal(_row(v="0.00000000001"), "v")
    assert str(date_cell(_row(d="1900-01-01"), "d")) == "1900-01-01"
    assert str(date_cell(_row(d="2200-12-31"), "d")) == "2200-12-31"
    with pytest.raises(ModelInputError, match="column d: '1899-12-31'"):
        date_cell(_row(d="1899-12-31"), "d")


def test_every_missing_column_is_named() -> None:
    with pytest.raises(ModelInputError, match=r"t: missing column a, b$"):
        rows({"t": Table(["c"], [])}, "t", frozenset({"a", "b", "c"}))
