"""Parse a Deploy VI Handoff.

A Handoff is Markdown: flat `key: value` front matter between `---` lines,
H2 sections, tagged tables (`<!-- table: <id> -->` then a GitHub table, blank
lines allowed between) and citation markers `[C<n>]`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_TABLE_TAG = re.compile(r"^<!--\s*table:\s*([A-Za-z0-9_.\-]+)\s*-->$")
_H2 = re.compile(r"^##\s+(.+?)\s*$")
_MARKER = re.compile(r"\[C(\d+)\]")
_SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")


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
        if not sep:
            raise HandoffError(f"front matter line is not key: value: {line!r}")
        front_matter[key.strip()] = value.strip()
    return front_matter, "\n".join(lines[end + 1 :])


def cells(line: str) -> list[str]:
    # ponytail: an escaped pipe (\|) inside a cell splits it; no module needs one.
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _read_table(lines: list[str], start: int) -> Table | None:
    """The table whose header is the first non-blank line at or after `start`."""
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i + 1 >= len(lines) or not lines[i].lstrip().startswith("|"):
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
    lines = body.splitlines()
    sections = [m.group(1) for line in lines if (m := _H2.match(line))]
    tables: dict[str, Table] = {}
    duplicates: list[str] = []
    orphans: list[str] = []
    for i, line in enumerate(lines):
        tag = _TABLE_TAG.match(line.strip())
        if not tag:
            continue
        table_id = tag.group(1)
        table = _read_table(lines, i + 1)
        if table is None:
            orphans.append(table_id)
        elif table_id in tables:
            duplicates.append(table_id)
        else:
            tables[table_id] = table
    return Handoff(front_matter, sections, tables, duplicates, orphans, body)


def markers(text: str) -> set[str]:
    """Every citation id a `[C<n>]` marker in `text` points to."""
    return {f"C{n}" for n in _MARKER.findall(text)}
