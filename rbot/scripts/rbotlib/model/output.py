"""`model.json` (`rbot-model/1`, spec §6.2) and `handoffs/MODEL.md` (§3.2).

`model.json` keeps every figure exact (`format(value, "f")`, a null with its
reason, never zero; the snapshot blocks are built from the tables' exact `Fig`
values, a row's `reasons` naming why a figure is null) and each cell's sources
resolved through the module's citations (at most `MAX_SOURCES` per cell; a cell
with more shows its first `MAX_SOURCES` and the Model notes `SOURCES_CUT`). It is deterministic: the
same inputs give the same bytes except `generated_at`. `MODEL.md` is a
Handoff (front matter, the four H2 sections, the §3.2 tables, a citations
table in its own numbering) whose `qa_status` is `Restricted` when a bridge
does not close or there is no LTM, else `Pass`.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from rbotlib import __version__
from rbotlib.handoff import Table
from rbotlib.model.assemble import CreditModel
from rbotlib.model.citations import Citations
from rbotlib.model.frame import Cell, Column, SourceRef
from rbotlib.model.house import HouseView
from rbotlib.model.house_inputs import HouseInputs
from rbotlib.model.layout import BANDS, Line
from rbotlib.model.snapshot import GAP, Fig, slots

SCHEMA = "rbot-model/1"
MAX_SOURCES = 8
MAX_COLUMNS = 64
MAX_LINES = 400
RESTRICTING = frozenset({"RECONCILIATION_FAULT", "NO_LTM"})


@dataclass(frozen=True, slots=True)
class Limitation:
    code: str
    message: str
    line_id: str = GAP
    column_id: str = GAP


def _decimal(cell_value: object) -> str | None:
    return None if cell_value is None else format(cell_value, "f")


def _all_sources(
    module: str, sources: Sequence[SourceRef], citations: Citations
) -> list[dict[str, str | None]]:
    found: list[dict[str, str | None]] = []
    for source in sources:
        resolved = citations.resolve(module, source)
        if not resolved:
            found.append(
                {
                    "module": module,
                    "citation_id": None,
                    "source": source.source_id,
                    "locator": source.source_locator,
                    "excerpt": None,
                }
            )
        for c in resolved:
            found.append(
                {
                    "module": c.module,
                    "citation_id": c.citation_id,
                    "source": c.source,
                    "locator": c.locator,
                    "excerpt": c.excerpt,
                }
            )
    return found


def _sources(
    module: str, sources: Sequence[SourceRef], citations: Citations
) -> list[dict[str, str | None]]:
    return _all_sources(module, sources, citations)[:MAX_SOURCES]


def _module(line: Line) -> str:
    return "CP-1D" if line.line_id.startswith("debt_like:") else "CP-1"


def _cell(column: Column, cell: Cell, module: str, citations: Citations) -> dict[str, Any]:
    return {
        "column_id": column.column_id,
        "value": _decimal(cell.value),
        "reason": cell.reason,
        "basis": cell.basis,
        "stated": _decimal(cell.stated),
        "note": cell.note,
        "sources": _sources(module, cell.sources, citations),
    }


def _line(line: Line, model: CreditModel, unit_label: str, citations: Citations) -> dict[str, Any]:
    terms = line.terms
    return {
        "line_id": line.line_id,
        "band": BANDS.index(line.band) + 1,
        "label": line.label,
        "kind": line.kind,
        "unit": line.unit,
        "unit_label": unit_label,
        "rank": line.rank,
        "terms": None
        if terms is None
        else {
            "reference_rate": terms.reference_rate,
            "spread_or_coupon": terms.spread_or_coupon,
            "floor": terms.floor,
            "maturity": terms.maturity,
            "amortisation": terms.amortisation,
        },
        "cells": [
            _cell(column, cell, _module(line), citations)
            for column, cell in zip(model.columns, line.cells, strict=True)
        ],
    }


def sources_cut(model: CreditModel, citations: Citations) -> list[Limitation]:
    """`SOURCES_CUT` when a cell resolves to more than `MAX_SOURCES` citations."""
    cut = any(
        len(_all_sources(_module(line), c.sources, citations)) > MAX_SOURCES
        for line in model.lines
        for c in line.cells
    )
    why = f"some cells name more than {MAX_SOURCES} sources; each shows its first {MAX_SOURCES}"
    return [Limitation("SOURCES_CUT", why)] if cut else []


def uncited_figures(model: CreditModel, citations: Citations) -> list[Limitation]:
    """`UNCITED_FIGURE` for each line with a reported or pro forma figure
    none of whose sources resolves to a citation (the cell's passport would
    show no source), naming its columns."""
    found = []
    for line in model.lines:
        columns = [
            column.column_id
            for column, cell in zip(model.columns, line.cells, strict=True)
            if cell.value is not None
            and cell.basis in {"REPORTED", "PRO_FORMA"}
            and not any(citations.resolve(_module(line), s) for s in cell.sources)
        ]
        if columns:
            why = f"{line.label}: no cited source for the figure on {', '.join(columns)}"
            found.append(Limitation("UNCITED_FIGURE", why, line.line_id))
    return found


def _exact(table: Table) -> list[dict[str, Any]]:
    """The table's rows with each figure exact (`format(value, "f")`, no
    suffix), a null where there is none, and `reasons` naming why."""
    found = []
    for row in table.rows:
        entry: dict[str, Any] = {}
        reasons: dict[str, str] = {}
        for name, cell in zip(table.columns, row, strict=True):
            if isinstance(cell, Fig):
                entry[name] = _decimal(cell.value)
                if cell.value is None and cell.reason is not None:
                    reasons[name] = cell.reason
            else:
                entry[name] = cell
        found.append({**entry, "reasons": reasons})
    return found


def _house(view: HouseView, inputs: HouseInputs, tables: Mapping[str, Table]) -> dict[str, Any]:
    column_id = view.column.column_id if view.column else None
    house: dict[str, Any] = {}
    for item in view.items:
        house[item.key] = {
            "column_id": column_id,
            "value": _decimal(item.cell.value),
            "formula": item.formula,
            "components": list(item.components),
            "reason": item.cell.reason,
        }
    ev = view.item("ev").cell if view.items else Cell(None, "NOT_APPLICABLE")
    multiple = inputs.brief.ssim_ev_multiple
    house["ev"] = {
        "value": _decimal(ev.value),
        "basis": view.ev_basis,
        "inputs": {
            "market_cap": _decimal(inputs.equity.market_cap) if inputs.equity else None,
            "ssim_ev_multiple": _decimal(multiple),
        },
        "reason": ev.reason,
    }
    house["pct_ev_by_facility"] = [
        {
            "facility_id": row["facility_id"],
            "pct": row["pct_ev_pct"],
            "reason": row["reasons"].get("pct_ev_pct"),
        }
        for row in _exact(tables["snapshot.capital_structure"])
    ]
    return house


@dataclass(frozen=True, slots=True)
class Built:
    """Everything `model.json` is written from."""

    model: CreditModel
    view: HouseView
    inputs: HouseInputs
    tables: Mapping[str, Table]
    citations: Citations
    unit_labels: Mapping[str, str]
    shas: Mapping[str, str | None]
    limitations: tuple[Limitation, ...]
    faults: tuple[str, ...]


def model_json(built: Built, generated_at: str) -> dict[str, Any]:
    model, view, inputs, tables = built.model, built.view, built.inputs, built.tables
    citations, unit_labels = built.citations, built.unit_labels
    taken = slots(model, view)
    return {
        "schema": SCHEMA,
        "run_id": inputs.brief.run_id,
        "generated_at": generated_at,
        "rbot_version": __version__,
        "currency": model.currency,
        "unit": model.unit,
        "exclude_unrealised": True,
        "inputs": dict(built.shas),
        "columns": [
            {
                "column_id": c.column_id,
                "kind": c.kind,
                "label": c.label,
                "period_id": c.period_id,
                "fiscal_year": c.fiscal_year,
                "end_date": c.end_date,
                "days": c.days,
                "case": c.case,
            }
            for c in model.columns
        ],
        "snapshot_columns": {s: (c.column_id if c else None) for s, c in taken.items()},
        "lines": [_line(x, model, unit_labels[x.line_id], citations) for x in model.lines],
        "house": _house(view, inputs, tables),
        "capital_structure": {
            "column_id": view.column.column_id if view.column else None,
            "rows": _exact(tables["snapshot.capital_structure"]),
            "totals": _exact(tables["snapshot.capital_structure_totals"]),
        },
        "ebitda_adjustments": _exact(tables["snapshot.ebitda_adjustments"]),
        "maturity_wall": _exact(tables["model.maturity_wall"]),
        "rate_deck": None,
        "forecast": {"status": "incomplete", "rows": {}},
        "limitations": list(dict.fromkeys(x.code for x in built.limitations)),
        "limitation_details": [
            {
                "code": x.code,
                "message": x.message,
                "line_id": None if x.line_id == GAP else x.line_id,
                "column_id": None if x.column_id == GAP else x.column_id,
            }
            for x in built.limitations
        ],
        "reconciliation_faults": list(built.faults),
    }


def dumps(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def _row(cells: Sequence[str]) -> str:
    """A table row; a literal pipe is written `\\|` (amendment A8)."""
    return "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"


def _markdown(table_id: str, table: Table) -> list[str]:
    for row in (table.columns, *table.rows):
        if any("\n" in cell for cell in row):
            raise ValueError(f"{table_id}: a cell holds a line break: {row}")
    lines = [f"<!-- table: {table_id} -->", "", _row(table.columns)]
    lines.append("|" + "|".join("---" for _ in table.columns) + "|")
    lines += [_row(row) for row in table.rows]
    return [*lines, ""]


def qa_status(limitations: Sequence[Limitation]) -> str:
    return "Restricted" if any(x.code in RESTRICTING for x in limitations) else "Pass"


def model_md(
    front_matter: Mapping[str, str],
    tables: Mapping[str, Table],
    citations: Citations,
    limitations: Sequence[Limitation],
    analysis: str,
) -> str:
    """MODEL.md: `front_matter` (every rules.json key but `qa_status`, which
    the limitations set), the analysis text, the tables, the limitations as
    gaps and the citations table."""
    lines = ["---", *(f"{k}: {v}" for k, v in front_matter.items())]
    lines += [f"qa_status: {qa_status(limitations)}", "---", "", "## Analysis", "", analysis, ""]
    lines += ["## Tables", ""]
    for table_id, table in tables.items():
        lines += _markdown(table_id, table)
    lines += ["## Gaps", ""]
    lines += [f"- {x.code}: {x.message}" for x in limitations] or ["- None."]
    lines += ["", "## Citations", ""]
    lines += _markdown("citations", citations.table())
    return "\n".join(lines)
