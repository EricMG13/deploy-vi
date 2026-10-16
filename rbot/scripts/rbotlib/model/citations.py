"""Citations for the Model's outputs (spec §3, §6.2).

A Model cell's `SourceRef.source_id` holds the `[C<n>]` markers of the module
row it came from (CP-1's registers, CP-1D's debt-like items). `Citations`
resolves each marker through that module's `citations` table and gives
`MODEL.md` its own numbering: the first module citation used is `C1`, the
next `C2`, and so on, each row copying the module's source, locator and
excerpt. A marker the module's citations table does not have is refused:
the module's own validator refuses that Handoff, so the Model never shows a
figure whose source cannot be followed.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import CONTROL as _CONTROL
from rbotlib.model.reader import ModelInputError

_MARKER = re.compile(r"\[(C\d+)\]")


@dataclass(frozen=True, slots=True)
class Citation:
    module: str
    citation_id: str
    source: str
    locator: str
    excerpt: str


def _header(where: str, table: Table) -> list[str]:
    columns = [c.casefold() for c in table.columns]
    if len(set(columns)) != len(columns):
        twice = sorted({c for c in columns if columns.count(c) > 1})
        raise ModelInputError(f"{where}: column {', '.join(twice)} appears twice")
    if "id" not in columns:
        raise ModelInputError(f"{where}: missing column id")
    return columns


def _cells(where: str, columns: list[str], number: int, row: list[str]) -> dict[str, str]:
    if len(row) != len(columns):
        width = f"{len(row)} cells, header has {len(columns)}"
        raise ModelInputError(f"{where} row {number}: {width}")
    cells = dict(zip(columns, row, strict=True))
    for column, cell in cells.items():
        if _CONTROL.search(cell):
            raise ModelInputError(f"{where} row {number} column {column}: control character")
    if not cells["id"]:
        raise ModelInputError(f"{where} row {number}: id is empty")
    return cells


def citation_rows(module: str, table: Table | None) -> dict[str, Citation]:
    """A module Handoff's citations by id; none when it has no table. Refused
    for a table with no `id` column, a column or an id written twice, a ragged
    row, an empty id or a control character."""
    if table is None:
        return {}
    where = f"{module} citations"
    columns = _header(where, table)
    found: dict[str, Citation] = {}
    for number, row in enumerate(table.rows, 1):
        cells = _cells(where, columns, number, row)
        if cells["id"] in found:
            raise ModelInputError(f"{where} row {number}: id {cells['id']} written twice")
        found[cells["id"]] = Citation(
            module,
            cells["id"],
            cells.get("source", ""),
            cells.get("locator", ""),
            cells.get("excerpt", ""),
        )
    return found


@dataclass
class Citations:
    """Module citations by module and id, and the local numbering in use."""

    modules: Mapping[str, Mapping[str, Citation]]
    used: dict[tuple[str, str], str] = field(default_factory=dict)

    def resolve(self, module: str, source: SourceRef) -> list[Citation]:
        """The module citations a source's markers name, in order."""
        found = []
        for marker in _MARKER.findall(source.source_id):
            citation = self.modules.get(module, {}).get(marker)
            if citation is None:
                raise ModelInputError(
                    f"{module} source_id {source.source_id}: no citation {marker}"
                )
            found.append(citation)
        return found

    def local(self, citation: Citation) -> str:
        key = (citation.module, citation.citation_id)
        if key not in self.used:
            self.used[key] = f"C{len(self.used) + 1}"
        return self.used[key]

    def cite(self, module: str, sources: Iterable[SourceRef]) -> str:
        """`[C<n>]` markers, in MODEL.md's numbering, for the sources; `—`
        when none names a citation."""
        ids = dict.fromkeys(
            self.local(c) for source in sources for c in self.resolve(module, source)
        )
        return " ".join(f"[{i}]" for i in ids) or "\N{EM DASH}"

    def table(self) -> Table:
        """MODEL.md's citations table, in local numbering order."""
        rows = []
        for (module, citation_id), local in self.used.items():
            c = self.modules[module][citation_id]
            rows.append([local, c.source, c.locator, c.excerpt])
        return Table(["id", "source", "locator", "excerpt"], rows)
