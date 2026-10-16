"""A module's citations table is read strictly (up-front review of the
non-money modules, 2026-10-11, I7): a repeated id or a ragged row is refused,
never overwritten."""

from __future__ import annotations

import re

import pytest

from rbotlib.handoff import Table
from rbotlib.model.citations import citation_rows
from rbotlib.model.reader import ModelInputError

COLUMNS = ["id", "source", "locator", "excerpt"]


def _refused(table: Table, match: str) -> None:
    with pytest.raises(ModelInputError, match=re.escape(match)):
        citation_rows("CP-1", table)


def test_an_id_written_twice_is_refused() -> None:
    # I7: the second C3 row won, so every figure citing C3 showed `other-file.txt`.
    rows = [["C3", "a.txt", "p.1", "x"], ["C3", "other-file.txt", "p.1", "different"]]
    _refused(Table(COLUMNS, rows), "CP-1 citations row 2: id C3 written twice")


def test_a_ragged_row_and_a_missing_id_column_are_refused() -> None:
    _refused(
        Table(COLUMNS, [["C1", "a.txt", "p.1"]]), "CP-1 citations row 1: 3 cells, header has 4"
    )
    _refused(Table(["source", "locator"], [["a.txt", "p.1"]]), "CP-1 citations: missing column id")
    _refused(Table(COLUMNS, [["", "a.txt", "p.1", "x"]]), "CP-1 citations row 1: id is empty")


def test_a_column_written_twice_is_refused() -> None:
    _refused(
        Table(["id", "id", "source"], [["C1", "C2", "a"]]),
        "CP-1 citations: column id appears twice",
    )


def test_a_clean_table_reads_and_its_control_characters_are_refused() -> None:
    found = citation_rows("CP-1", Table(COLUMNS, [["C1", "a.txt", "p.1", "x"]]))
    assert found["C1"].excerpt == "x"
    _refused(
        Table(COLUMNS, [["C1", "a.txt", "p.1", "bad\x01"]]),
        "CP-1 citations row 1 column excerpt: control character",
    )
