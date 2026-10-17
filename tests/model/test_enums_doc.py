"""docs/model/enums.md lists exactly the vocabularies the Model reads with."""

from __future__ import annotations

import re
from pathlib import Path

from rbotlib.model import house_inputs, inputs, registers

DOC = Path(__file__).parents[2] / "docs" / "model" / "enums.md"
CLOSED = {
    "period_type": registers.PERIOD_TYPES,
    "unit": registers.PERIOD_UNITS,
    "calculation_status": registers.CALCULATION_STATUSES,
    "addback_classification": registers.ADDBACK_CLASSIFICATIONS,
    "realization_status": registers.REALIZATION_STATUSES,
    "segment_type": registers.SEGMENT_TYPES,
    "value_type": registers.KPI_VALUE_TYPES,
    "secured_status": registers.SECURED_STATUSES,
    "seniority": registers.SENIORITIES,
    "lease_classification": registers.LEASE_CLASSIFICATIONS,
    "rate_type": registers.RATE_TYPES,
    "reference_rate": registers.REFERENCE_RATES,
    "classification": registers.PF_CLASSIFICATIONS,
    "house_realization_status": registers.REALIZATION_STATUSES,
    "verdict": house_inputs.VERDICTS,
    "treatment": house_inputs.TREATMENTS,
    "metric_id": inputs.PF_METRICS | {"facility:<id>"},
}


def _rows() -> list[tuple[str, str, frozenset[str], str]]:
    rows = []
    for line in DOC.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0].startswith("`cp1"):
            values = frozenset(re.findall(r"`([^`]+)`", cells[2]))
            rows.append((cells[0].strip("`"), cells[1].strip("`"), values, cells[3]))
    return rows


def test_every_closed_vocabulary_is_documented_as_the_code_has_it() -> None:
    documented = {(column, values) for _, column, values, kind in _rows() if kind == "closed"}
    expected = {(column, frozenset(values)) for column, values in CLOSED.items()}
    assert expected <= documented
    assert {column for column, _ in documented} == set(CLOSED)


def test_the_open_columns_are_documented_as_open() -> None:
    open_columns = {(table, column) for table, column, _, kind in _rows() if kind == "open"}
    assert open_columns == {
        ("cp1.model_period_register", "currency"),
        ("cp1.operating_kpi_schedule", "unit"),
        ("cp1.debt_facility_register", "facility_type"),
        ("cp1.debt_facility_register", "currency"),
    }
