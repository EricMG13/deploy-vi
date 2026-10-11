"""Parse a Deploy VI Handoff.

A Handoff is Markdown: flat `key: value` front matter between `---` lines,
H2 sections, tagged tables (`<!-- table: <id> -->` then a GitHub table, blank
lines allowed between) and citation markers `[C<n>]`. A literal pipe inside
a cell is written as a backslash and a pipe (amendment A8). Fenced code blocks
hold no sections or tags (A9); a table indented 4+ spaces is code, not a table.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_TABLE_TAG = re.compile(r"^<!--\s*table:\s*(.*?)\s*-->$")
_TABLE_ID = re.compile(r"[A-Za-z0-9_.\-]+")
_FENCE = re.compile(r"^(`{3,}|~{3,})")
_H2 = re.compile(r"^##\s+(.+?)\s*$")
_MARKER = re.compile(r"\[C(\d+)\]")
_SEPARATOR = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$")
_PIPE = re.compile(r"(?<!\\)\|")
_CODE_INDENT = re.compile(r"^(?: {4}| {0,3}\t)")  # an indented code line, never a table (M5)


class HandoffError(ValueError):
    """The text has no readable front matter, so it is not a Handoff."""


@dataclass(frozen=True)
class Table:
    columns: list[str]
    rows: list[list[str]]


@dataclass(frozen=True)
class Handoff:
    front_matter: dict[str, str]
    sections: list[str]
    tables: dict[str, Table]
    duplicate_tags: list[str]
    orphan_tags: list[str]
    body: str
    invalid_tags: list[str] = field(default_factory=list)


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise HandoffError("missing front matter: the first line must be ---")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), 0)
    if not end:
        raise HandoffError("front matter is not closed with ---")
    front_matter: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            raise HandoffError(f"front matter line is not key: value: {line!r}")
        if key.strip() in front_matter:
            raise HandoffError(f"front matter key {key.strip()!r} appears twice")
        front_matter[key.strip()] = value.strip()
    return front_matter, "\n".join(lines[end + 1 :])


def cells(line: str) -> list[str]:
    """The cells of a table row; `\\|` is a literal pipe inside a cell (A8).

    Unlike GFM, `\\|` is an escaped pipe even outside a code span, and a cell
    that ends in `\\|` keeps it as a literal pipe, not a closing delimiter.
    """
    text = line.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
    return [cell.strip().replace("\\|", "|") for cell in _PIPE.split(text)]


def _unfenced(lines: list[str]) -> list[str]:
    """The lines with every fenced code block blanked, so it holds no section or tag.

    A fence indented 4 or more spaces is indented code, not a fence (A4).
    """
    out, fence = [], ""
    for line in lines:
        opener = None if _CODE_INDENT.match(line) else _FENCE.match(line.lstrip())
        if fence:
            fence = "" if opener and opener.group(1).startswith(fence) else fence
            out.append("")
        elif opener:
            fence = opener.group(1)
            out.append("")
        else:
            out.append(line)
    return out


def unfenced(text: str) -> str:
    """The text with every fenced code block blanked (A5)."""
    return "\n".join(_unfenced(text.splitlines()))


def _read_table(lines: list[str], start: int) -> Table | None:
    """The table whose header is the first non-blank line at or after `start`."""
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i + 1 >= len(lines) or not lines[i].lstrip().startswith("|"):
        return None
    if any(_CODE_INDENT.match(line) for line in lines[i : i + 2]):
        return None
    if not _SEPARATOR.match(lines[i + 1].strip()):
        return None
    rows = []
    for line in lines[i + 2 :]:
        if not line.lstrip().startswith("|"):
            break
        rows.append(cells(line))
    return Table(cells(lines[i]), rows)


def parse(text: str) -> Handoff:
    front_matter, body = _split_front_matter(text)
    lines = _unfenced(body.splitlines())
    sections = [m.group(1) for line in lines if (m := _H2.match(line))]
    tables: dict[str, Table] = {}
    duplicates: list[str] = []
    orphans: list[str] = []
    invalid: list[str] = []
    for i, line in enumerate(lines):
        tag = None if _CODE_INDENT.match(line) else _TABLE_TAG.match(line.strip())
        if not tag:
            continue
        table_id = tag.group(1)
        table = _read_table(lines, i + 1)
        if not _TABLE_ID.fullmatch(table_id):
            invalid.append(table_id)
        elif table is None:
            orphans.append(table_id)
        elif table_id in tables:
            duplicates.append(table_id)
        else:
            tables[table_id] = table
    return Handoff(front_matter, sections, tables, duplicates, orphans, body, invalid)


def markers(text: str) -> set[str]:
    """Every citation id a `[C<n>]` marker in `text` points to."""
    return {f"C{n}" for n in _MARKER.findall(text)}
