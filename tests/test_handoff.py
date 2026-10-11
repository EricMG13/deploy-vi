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


def _one_table(row: str, separator: str = "|---|---|") -> list[list[str]]:
    text = f"---\nk: v\n---\n<!-- table: t -->\n| a | b |\n{separator}\n{row}\n"
    return parse(text).tables["t"].rows


@pytest.mark.parametrize(
    ("row", "cells"),
    [
        (r"| Net revenues \| 11,486 | p.1 |", ["Net revenues | 11,486", "p.1"]),
        (r"| a\|b\|c | d |", ["a|b|c", "d"]),
        ("| C:\\ | d |", ["C:\\", "d"]),
        ("| x | ends with \\|", ["x", "ends with |"]),
    ],
)
def test_an_escaped_pipe_stays_inside_its_cell(row: str, cells: list[str]) -> None:
    assert _one_table(row) == [cells]


@pytest.mark.parametrize("separator", ["|-|-|", "| :- | -: |", "|---|:---:|", "-|-"])
def test_short_github_separators_are_accepted(separator: str) -> None:
    assert _one_table("| 1 | 2 |", separator) == [["1", "2"]]


@pytest.mark.parametrize("tag", ["cp1 model", "cp1/model", ""])
def test_a_tag_with_an_invalid_id_is_reported(tag: str) -> None:
    h = parse(f"---\nk: v\n---\n<!-- table: {tag} -->\n| x |\n|---|\n| 1 |\n")
    assert h.invalid_tags == [tag]
    assert h.tables == {}


@pytest.mark.parametrize("fence", ["```", "````markdown", "~~~"])
def test_fenced_blocks_hold_no_sections_or_tags(fence: str) -> None:
    close = fence.rstrip("markdown")
    text = (
        "---\nk: v\n---\n## Analysis\n"
        f"{fence}\n## Not a section\n<!-- table: hidden -->\n| x |\n|---|\n| 1 |\n{close}\n"
        "## Tables\n"
    )
    h = parse(text)
    assert h.sections == ["Analysis", "Tables"]
    assert h.tables == {} and h.orphan_tags == [] and h.invalid_tags == []


@pytest.mark.parametrize(
    ("front", "message"),
    [
        ("module_id: CP-X\nmodule_id: CP-Y", "front matter key 'module_id' appears twice"),
        (": no key", "front matter line is not key: value"),
    ],
)
def test_duplicate_or_empty_front_matter_keys_are_refused(front: str, message: str) -> None:
    with pytest.raises(HandoffError, match=message):
        parse(f"---\n{front}\n---\nbody\n")


@pytest.mark.parametrize(("indent", "orphans"), [("   ", []), ("    ", ["t"]), ("  \t", ["t"])])
def test_a_table_indented_four_spaces_is_a_code_block(indent: str, orphans: list[str]) -> None:
    h = parse(f"---\nk: v\n---\n<!-- table: t -->\n{indent}| x |\n{indent}|---|\n| 1 |\n")
    assert (h.orphan_tags, set(h.tables)) == (orphans, set() if orphans else {"t"})
