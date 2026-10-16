"""CP-1's registers must name periods, metrics and facilities that exist
(up-front review of the non-money modules, 2026-10-11, I8; money review I1):
a typo no longer drops a figure silently."""

from __future__ import annotations

import re
from collections.abc import Callable

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff

from rbotlib.handoff import Table, parse
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.reader import ModelInputError


def _tables() -> dict[str, Table]:
    return dict(parse(cp1_handoff(example_registers())).tables)


def _edit(
    tables: dict[str, Table], table_id: str, test: Callable[[list[str]], bool], column: str, to: str
) -> None:
    table = tables[table_id]
    at = table.columns.index(column)
    for row in table.rows:
        if test(row):
            row[at] = to
            return
    raise AssertionError("no row to edit")


def _refused(tables: dict[str, Table], match: str) -> None:
    with pytest.raises(ModelInputError, match=re.escape(match)):
        cp1_registers(tables)


@pytest.mark.parametrize(
    "table_id",
    [
        "cp1.model_account_register",
        "cp1.adjusted_ebitda_bridge",
        "cp1.segment_revenue_schedule",
        "cp1.operating_kpi_schedule",
        "cp1.debt_facility_register",
        "cp1.pro_forma_adjustment_register",
    ],
)
def test_a_row_naming_a_period_the_register_lacks_is_refused(table_id: str) -> None:
    # I8: `FY2O25` (a letter O) made the revenue FY2025 `NOT_SOURCED` and the run exited 0.
    tables = _tables()
    _edit(tables, table_id, lambda row: True, "period_id", "FY2O25")
    _refused(
        tables, f"{table_id} row 1 column period_id: FY2O25 is not in cp1.model_period_register"
    )


def test_a_pro_forma_row_must_sit_on_an_ltm_period() -> None:
    # Money I1: a PF row keyed to H1_2026 never applied, and the LTM said it had no PF rows.
    tables = _tables()
    _edit(tables, "cp1.pro_forma_adjustment_register", lambda row: True, "period_id", "H1_2026")
    _refused(
        tables,
        "cp1.pro_forma_adjustment_register row 1 column period_id: H1_2026 is not an LTM period",
    )


def test_a_pro_forma_row_naming_a_metric_the_model_cannot_place_is_refused() -> None:
    # I8: `cash_interest_payd` changed PF interest from 904 to 862 without a word.
    tables = _tables()
    _edit(
        tables,
        "cp1.pro_forma_adjustment_register",
        lambda row: True,
        "metric_id",
        "cash_interest_payd",
    )
    _refused(
        tables,
        "cp1.pro_forma_adjustment_register row 1 column metric_id: 'cash_interest_payd' "
        "is not a metric a pro forma row adjusts",
    )
    tables = _tables()
    _edit(
        tables, "cp1.pro_forma_adjustment_register", lambda row: True, "metric_id", "facility:nope"
    )
    _refused(
        tables,
        "cp1.pro_forma_adjustment_register row 1 column metric_id: 'facility:nope' "
        "names no facility",
    )
