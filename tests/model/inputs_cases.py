"""CP-1 tables built cell by cell, shared by the input tests."""

from __future__ import annotations

import re

import pytest

from rbotlib.handoff import Table
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.reader import ModelInputError

PERIOD_COLUMNS = [
    "period_id",
    "fiscal_year",
    "fiscal_quarter",
    "period_type",
    "start_date",
    "end_date",
    "day_count",
    "currency",
    "unit",
    "component_period_ids",
]


FY2025 = ["FY2025", "FY2025", "—", "FY", "2025-01-01", "2025-12-31", "365", "USD", "MILLIONS", "—"]


def _periods(*rows: list[str]) -> Table:
    return Table(PERIOD_COLUMNS, [list(r) for r in rows])


def _tables(**extra: Table) -> dict[str, Table]:
    tables = {"cp1.model_period_register": _periods(FY2025)}
    tables.update({f"cp1.{k}": v for k, v in extra.items()})
    return tables


def _refused(tables: dict[str, Table], match: str) -> None:
    with pytest.raises(ModelInputError, match=re.escape(match)):
        cp1_registers(tables)
