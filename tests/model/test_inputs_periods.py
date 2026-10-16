"""CP-1's period register and register-wide rules: what is refused."""

from __future__ import annotations

import re

import pytest
from inputs_cases import FY2025, PERIOD_COLUMNS, _periods, _refused, _tables

from rbotlib.handoff import Table
from rbotlib.model.inputs import MAX_PERIODS, cp1_registers
from rbotlib.model.reader import ModelInputError


def _period(**cells: str) -> list[str]:
    row = dict(zip(PERIOD_COLUMNS, FY2025, strict=True))
    row.update(cells)
    return list(row.values())


@pytest.mark.parametrize(
    ("cells", "match"),
    [
        ({"day_count": "364"}, "column day_count: 364 is not end - start"),
        ({"start_date": "2026-01-01"}, "column start_date: after end_date"),
        ({"end_date": "2025-02-30"}, "column end_date: '2025-02-30' is not a YYYY-MM-DD"),
        ({"fiscal_year": "FY"}, "column fiscal_year: 'FY' has no four-digit year"),
        ({"fiscal_year": "FY2030"}, "more than a year from end_date"),
        ({"period_type": "HALF"}, "column period_type: 'HALF' is not one of"),
        ({"unit": "billions"}, "column unit: 'billions' is not one of"),
        ({"day_count": "1.5"}, "column day_count: not a whole number"),
        ({"start_date": "—", "end_date": "—", "day_count": "0"}, "day_count: 0 is out of range"),
        ({"component_period_ids": "Q1;Q1"}, "names a component twice"),
    ],
)
def test_a_bad_period_is_refused_naming_where(cells: dict[str, str], match: str) -> None:
    _refused({"cp1.model_period_register": _periods(_period(**cells))}, match)


def test_period_register_wide_checks() -> None:
    eur = _period(period_id="FY2024", fiscal_year="FY2024", currency="EUR")
    eur = _period(
        period_id="FY2024",
        fiscal_year="FY2024",
        start_date="2024-01-01",
        end_date="2024-12-31",
        day_count="366",
        currency="EUR",
    )
    _refused({"cp1.model_period_register": _periods(FY2025, eur)}, "states EUR, USD; need one")
    twice = _period(period_id="FY2025b")
    _refused({"cp1.model_period_register": _periods(FY2025, twice)}, "a second period")
    same_id = _period(period_type="LTM")
    _refused({"cp1.model_period_register": _periods(FY2025, same_id)}, "FY2025 written twice")
    cycle = [
        _period(period_id="A", period_type="LTM", component_period_ids="B"),
        _period(period_id="B", period_type="LTM", component_period_ids="A"),
    ]
    _refused({"cp1.model_period_register": _periods(*cycle)}, "components form a cycle")
    chain = [
        _period(period_id=f"P{i}", period_type="LTM", component_period_ids=f"P{i + 1}")
        for i in range(6)
    ]
    _refused({"cp1.model_period_register": _periods(*chain)}, "nested past 4")
    quarter = {"period_type": "QUARTER", "fiscal_quarter": "Q2", "start_date": "2025-04-01"}
    quarter |= {"end_date": "2025-06-30", "day_count": "91"}
    quarters = [_period(period_id="Q2", **quarter), _period(period_id="Q2b", **quarter)]
    _refused({"cp1.model_period_register": _periods(*quarters)}, "a second period for")
    shared = [
        _period(period_id="A", period_type="LTM", component_period_ids="C"),
        _period(period_id="B", period_type="LTM", component_period_ids="C"),
        _period(period_id="C", period_type="LTM", start_date="—", end_date="—", day_count="—"),
    ]
    periods = cp1_registers({"cp1.model_period_register": _periods(*shared)}).periods
    assert [(p.period_id, p.start_date, p.day_count) for p in periods][2] == ("C", None, None)
    many = [_period(period_id=f"P{i}", period_type="LTM") for i in range(MAX_PERIODS + 1)]
    _refused({"cp1.model_period_register": _periods(*many)}, "more than 200 periods")


def test_account_and_pro_forma_rules() -> None:
    columns = [
        "metric_id",
        "period_id",
        "value",
        "calculation_status",
        "source_id",
        "source_locator",
    ]
    rcf = Table(columns, [["rcf_drawn", "FY2025", "-1", "VERIFIED", "—", "—"]])
    _refused(_tables(model_account_register=rcf), "rcf_drawn is a balance")
    twice = Table(columns, [["revenue", "FY2025", "1", "VERIFIED", "—", "—"]] * 2)
    _refused(_tables(model_account_register=twice), "row 2: revenue / FY2025 written twice")
    status = Table(columns, [["revenue", "FY2025", "1", "GUESSED", "—", "—"]])
    _refused(_tables(model_account_register=status), "calculation_status: 'GUESSED'")
    pf_columns = [
        "adjustment_id",
        "label",
        "period_id",
        "effective_date",
        "classification",
        "metric_id",
        "value",
        "source_id",
        "source_locator",
    ]
    empty = Table(
        pf_columns,
        [["PF1", "x", "FY2025", "2026-01-01", "ACQUISITION", "revenue", "—", "[C1]", "p.1"]],
    )
    _refused(_tables(pro_forma_adjustment_register=empty), "column value: required, found null")


def test_display_priority_is_a_required_whole_number() -> None:
    columns = [
        "segment_id",
        "segment_name",
        "segment_type",
        "display_priority",
        "period_id",
        "revenue",
        "source_id",
        "source_locator",
    ]
    for priority, match in (("—", "required, found null"), ("1.5", "not a whole number")):
        table = Table(
            columns, [["lv", "LV", "OPERATING_SEGMENT", priority, "FY2025", "1", "—", "—"]]
        )
        _refused(_tables(segment_revenue_schedule=table), f"display_priority: {match}")


def test_absent_tables_read_as_no_rows() -> None:
    regs = cp1_registers(_tables())
    for rows in (regs.accounts, regs.addbacks, regs.segments, regs.kpis):
        assert rows == ()
    assert (regs.facilities, regs.pro_forma) == ((), ())


def test_the_period_register_is_required() -> None:
    with pytest.raises(ModelInputError, match=re.escape("cp1.model_period_register: no rows")):
        cp1_registers({})
    _refused({"cp1.model_period_register": _periods()}, "no rows")


def test_a_missing_column_or_a_ragged_row_is_refused() -> None:
    table = Table(PERIOD_COLUMNS[:-1], [FY2025[:-1]])
    _refused({"cp1.model_period_register": table}, "missing column component_period_ids")
    ragged = Table(PERIOD_COLUMNS, [FY2025[:-1]])
    _refused({"cp1.model_period_register": ragged}, "row 1: 9 cells, header has 10")
