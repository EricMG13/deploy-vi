"""Module citations and MODEL.md's own numbering (`rbotlib.model.citations`)."""

from __future__ import annotations

import pytest

from rbotlib.handoff import Table
from rbotlib.model.citations import Citation, Citations, citation_rows
from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import ModelInputError

ROWS = [["C1", "10-K.txt", "p.4", "Revenue"], ["C2", "10-Q.txt", "p.9", "Total debt"]]
CITED = Table(["id", "source", "locator", "excerpt"], ROWS)


def test_markers_resolve_and_are_numbered_in_first_use_order() -> None:
    citations = Citations({"CP-1": citation_rows("CP-1", CITED)})
    second = SourceRef("[C2]", "p.9", "11,705")
    both = SourceRef("[C1] [C2]", "p.4", "x")
    assert citations.cite("CP-1", [second]) == "[C1]"
    assert citations.cite("CP-1", [both, second]) == "[C2] [C1]"
    assert citations.cite("CP-1", [SourceRef("S3", "", "1")]) == "\N{EM DASH}"
    assert citations.table().rows == [
        ["C1", "10-Q.txt", "p.9", "Total debt"],
        ["C2", "10-K.txt", "p.4", "Revenue"],
    ]
    assert citations.resolve("CP-1", both) == [
        Citation("CP-1", "C1", "10-K.txt", "p.4", "Revenue"),
        Citation("CP-1", "C2", "10-Q.txt", "p.9", "Total debt"),
    ]


def test_a_marker_without_its_citation_is_refused() -> None:
    citations = Citations({"CP-1": citation_rows("CP-1", CITED)})
    with pytest.raises(ModelInputError, match=r"CP-1 source_id \[C9\]: no citation C9"):
        citations.cite("CP-1", [SourceRef("[C9]", "", "1")])
    assert citation_rows("CP-1", None) == {}


def test_citation_rows_read_absent_columns_as_empty_and_header_case_alike() -> None:
    upper = Table(["ID", "Source", "locator"], [["C1", "10-K.txt", "p.1"]])
    assert citation_rows("CP-1", upper) == {"C1": Citation("CP-1", "C1", "10-K.txt", "p.1", "")}
    sourceless = Table(["id"], [["C2"]])
    assert citation_rows("CP-1", sourceless) == {"C2": Citation("CP-1", "C2", "", "", "")}
