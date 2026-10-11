from __future__ import annotations

import pytest

from rbotlib.handoff import HandoffError, markers, parse


def test_parse_reads_front_matter_sections_and_tables(handoff_text: str) -> None:
    h = parse(handoff_text)
    assert h.front_matter["module_id"] == "CP-X"
    assert h.sections == ["Analysis", "Tables", "Gaps", "Citations"]
    assert h.tables["cpx.facts"].columns == ["fact", "value", "note"]
    assert h.tables["cpx.facts"].rows == [["revenue", "100", "—"]]
    assert set(h.tables) == {"cpx.facts", "snapshot.view", "citations"}


def test_a_blank_line_between_tag_and_table_is_allowed(handoff_text: str) -> None:
    assert "<!-- table: cpx.facts -->\n\n| fact" in handoff_text
    assert parse(handoff_text).tables["cpx.facts"].rows


@pytest.mark.parametrize(
    "text",
    ["no front matter", "---\nmodule_id: CP-X\n", "---\nnot a pair\n---\n"],
)
def test_unreadable_front_matter_is_not_a_handoff(text: str) -> None:
    with pytest.raises(HandoffError):
        parse(text)


def test_orphan_and_duplicate_tags_are_reported() -> None:
    text = (
        "---\nmodule_id: CP-X\n---\n"
        "<!-- table: a -->\nprose, not a table\n"
        "<!-- table: b -->\n| x |\n|---|\n| 1 |\n"
        "<!-- table: b -->\n| x |\n|---|\n| 2 |\n"
    )
    h = parse(text)
    assert h.orphan_tags == ["a"]
    assert h.duplicate_tags == ["b"]
    assert h.tables["b"].rows == [["1"]]


def test_a_header_without_separator_is_not_a_table() -> None:
    h = parse("---\nk: v\n---\n<!-- table: a -->\n| x |\n| 1 |\n")
    assert h.orphan_tags == ["a"]


def test_markers_finds_every_citation_id() -> None:
    assert markers("a [C1] b [C12] c [C1] [X3]") == {"C1", "C12"}
