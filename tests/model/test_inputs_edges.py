"""CP-1's tables at the edges of what `cp1_registers` accepts (the mutation
gate's findings on `rbotlib.model.inputs`)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers
from inputs_cases import FY2025, PERIOD_COLUMNS, _periods, _refused, _tables
from model_handoffs import cp1_handoff

from rbotlib.handoff import Table, parse
from rbotlib.model.inputs import MAX_PERIODS, cp1_registers
from rbotlib.model.registers import FacilityRow

FACILITY = {"facility_id": "TLB", "facility_name": "Term Loan B", "period_id": "FY2025"}
FACILITY |= {"facility_type": "Term loan", "currency": "USD", "carrying_value": "2,018"}
FACILITY |= {"drawn_amount": "2,018", "commitment": "—", "secured_status": "SECURED"}
FACILITY |= {"seniority": "SENIOR", "margin_or_coupon": "SOFR + 225", "maturity_date": "—"}
FACILITY |= {"lease_classification": "NOT_LEASE", "source_id": "—", "source_locator": "—"}


def _p(**cells: str) -> list[str]:
    row = dict(zip(PERIOD_COLUMNS, FY2025, strict=True))
    row.update(cells)
    return list(row.values())


def _facility(**cells: str) -> dict[str, Table]:
    row = FACILITY | cells
    return _tables(debt_facility_register=Table(list(row), [list(row.values())]))


def test_the_period_bounds_are_accepted() -> None:
    longest = (date(2200, 12, 31) - date(1900, 1, 1)).days + 1
    periods = [
        FY2025,
        _p(period_id="D", period_type="PERIOD_END", start_date="2025-12-31", day_count="1"),
        _p(period_id="O", period_type="LTM", end_date="—", day_count="—"),
        _p(period_id="FY1900", fiscal_year="FY1900", start_date="1900-01-01",
           end_date="1900-12-31", day_count="365"),
        _p(period_id="L", fiscal_year="FY2200", period_type="LTM", start_date="1900-01-01",
           end_date="2200-12-31", day_count=str(longest)),
        _p(period_id="FY2026", fiscal_year="FY2026"),  # a year from its end date's year
    ]  # fmt: skip
    found = cp1_registers({"cp1.model_period_register": _periods(*periods)}).periods
    assert [p.period_id for p in found] == ["FY2025", "D", "O", "FY1900", "L", "FY2026"]
    assert (found[1].day_count, found[2].end_date) == (1, None)


def test_a_refusal_names_its_column() -> None:
    far = _p(fiscal_year="FY2027")
    _refused({"cp1.model_period_register": _periods(far)},
             "column fiscal_year: 'FY2027' is more than a year from end_date")  # fmt: skip
    twice = _p(period_type="LTM", component_period_ids="A;A")
    _refused({"cp1.model_period_register": _periods(twice)},
             "column component_period_ids: names a component twice")  # fmt: skip
    columns = ["metric_id", "period_id", "value", "calculation_status", "source_id"]
    rcf = Table([*columns, "source_locator"], [["rcf_drawn", "FY2025", "-1", "VERIFIED", "—", "—"]])
    _refused(_tables(model_account_register=rcf), "row 1 column value: rcf_drawn is a balance")
    unit = _p(period_id="FY2024", fiscal_year="FY2024", start_date="2024-01-01",
              end_date="2024-12-31", day_count="366", unit="THOUSANDS")  # fmt: skip
    _refused({"cp1.model_period_register": _periods(FY2025, unit)},
             "cp1.model_period_register column unit: states MILLIONS, THOUSANDS")  # fmt: skip
    euro = _p(period_id="FY2024", fiscal_year="FY2024", start_date="2024-01-01",
              end_date="2024-12-31", day_count="366", currency="EUR")  # fmt: skip
    _refused({"cp1.model_period_register": _periods(FY2025, euro)},
             "cp1.model_period_register column currency: states EUR, USD")  # fmt: skip


def test_rate_terms_at_their_bounds_and_the_drawn_amount() -> None:
    def read(**cells: str) -> FacilityRow:
        return cp1_registers(_facility(**cells)).facilities[0]

    assert read(spread_bps="50%").terms_out_of_range is True
    low, high = read(fixed_rate="0.5"), read(fixed_rate="30")
    assert (low.terms_out_of_range, high.terms_out_of_range) == (False, False)
    tlb = cp1_registers(_facility()).facilities[0]
    assert (tlb.drawn_amount, tlb.margin_or_coupon) == (Decimal(2018), "SOFR + 225")
    _refused(_facility(drawn_amount="-1"), "row 1 column drawn_amount: cannot be negative")


@pytest.mark.parametrize(("kind", "first", "second"), [("YTD", "Q2", "2"), ("QUARTER", "q2", "Q2")])
def test_one_period_per_fiscal_quarter_however_the_quarter_is_written(
    kind: str, first: str, second: str
) -> None:
    ltm = _p(period_id="LTM", period_type="LTM", fiscal_quarter="Q2")
    a = _p(period_id="A", period_type=kind, fiscal_quarter=first)
    b = _p(period_id="B", period_type=kind, fiscal_quarter=second)
    _refused({"cp1.model_period_register": _periods(ltm, a, b)}, "row 3: a second period for")


def test_a_period_id_written_twice_is_refused_naming_the_period_register() -> None:
    twice = [_p(period_id="L", period_type="LTM"), _p(period_id="L", period_type="LTM")]
    _refused({"cp1.model_period_register": _periods(*twice)},
             "cp1.model_period_register row 2: L written twice")  # fmt: skip


def test_period_ends_may_share_a_quarter_and_nesting_four_deep_is_accepted() -> None:
    ends = [_p(period_id=f"E{i}", period_type="PERIOD_END", fiscal_quarter="Q4") for i in (1, 2)]
    chain = [
        _p(period_id=f"P{i}", period_type="LTM", component_period_ids=f"P{i + 1}" if i < 4 else "—")
        for i in range(5)
    ]
    periods = cp1_registers({"cp1.model_period_register": _periods(*ends, *chain)}).periods
    assert len(periods) == 7
    many = [_p(period_id=f"P{i}", period_type="LTM") for i in range(MAX_PERIODS)]
    assert len(cp1_registers({"cp1.model_period_register": _periods(*many)}).periods) == 200


@pytest.mark.parametrize(
    "table_id",
    [
        "cp1.model_period_register",
        "cp1.model_account_register",
        "cp1.adjusted_ebitda_bridge",
        "cp1.segment_revenue_schedule",
        "cp1.operating_kpi_schedule",
        "cp1.debt_facility_register",
        "cp1.pro_forma_adjustment_register",
    ],
)
def test_a_row_written_twice_is_refused_naming_its_table(table_id: str) -> None:
    tables = dict(parse(cp1_handoff(example_registers())).tables)
    table = tables[table_id]
    tables[table_id] = Table(table.columns, [*table.rows, table.rows[0]])
    _refused(tables, f"{table_id} row {len(table.rows) + 1}: ")
