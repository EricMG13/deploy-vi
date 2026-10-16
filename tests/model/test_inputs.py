"""CP-1's tables read into registers, and what is refused."""

from __future__ import annotations

from decimal import Decimal

import pytest
from inputs_cases import FY2025, _periods, _refused, _tables

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef
from rbotlib.model.inputs import cp1_registers

FACILITY_COLUMNS = [
    "facility_id",
    "facility_name",
    "period_id",
    "facility_type",
    "currency",
    "carrying_value",
    "drawn_amount",
    "commitment",
    "secured_status",
    "seniority",
    "margin_or_coupon",
    "maturity_date",
    "lease_classification",
    "source_id",
    "source_locator",
]


TLB = [
    "TLB",
    "Term Loan B",
    "FY2025",
    "Term loan",
    "USD",
    "2,018",
    "2,018",
    "—",
    "SECURED",
    "SENIOR",
    "SOFR + 225",
    "2030-02-06",
    "NOT_LEASE",
    "[C4]",
    "p.12",
]


def _facility(**cells: str) -> Table:
    row = dict(zip(FACILITY_COLUMNS, TLB, strict=True))
    row.update(cells)
    return Table(list(row), [list(row.values())])


def test_reads_every_register_with_sources_kept_verbatim() -> None:
    accounts = Table(
        ["metric_id", "period_id", "value", "calculation_status", "source_id", "source_locator"],
        [["revenue", "FY2025", "11,245.0 [C3]", "verified", "[C3]", "p.61"]],
    )
    addbacks = Table(
        [
            "addback_id",
            "addback_label",
            "addback_classification",
            "realization_status",
            "display_priority",
            "period_id",
            "value",
            "source_id",
            "source_locator",
        ],
        [["A1", "Synergies", "synergy", "unrealized", "1", "FY2025", "40", "[C5]", "p.3"]],
    )
    segments = Table(
        [
            "segment_id",
            "segment_name",
            "segment_type",
            "display_priority",
            "period_id",
            "revenue",
            "source_id",
            "source_locator",
        ],
        [["lv", "Las Vegas", "operating segment", "1", "FY2025", "4,213", "[C6]", "p.70"]],
    )
    kpis = Table(
        [
            "kpi_id",
            "kpi_label",
            "display_priority",
            "period_id",
            "value",
            "unit",
            "value_type",
            "source_id",
            "source_locator",
        ],
        [["occ", "Occupancy", "1", "FY2025", "96.1%", "percent", "RATE", "—", "—"]],
    )
    pro_forma = Table(
        [
            "adjustment_id",
            "label",
            "period_id",
            "effective_date",
            "classification",
            "metric_id",
            "value",
            "source_id",
            "source_locator",
        ],
        [
            [
                "PF1",
                "New TLB",
                "LTM1",
                "2026-01-01",
                "refinancing",
                "facility:TLB",
                "500",
                "[C7]",
                "p.2",
            ]
        ],
    )
    tables = _tables(
        model_account_register=accounts,
        adjusted_ebitda_bridge=addbacks,
        segment_revenue_schedule=segments,
        operating_kpi_schedule=kpis,
        debt_facility_register=_facility(),
        pro_forma_adjustment_register=pro_forma,
    )
    ltm = ["LTM1", "FY2025", "—", "LTM", "2025-01-01", "2025-12-31", "365", "USD", "MILLIONS", "—"]
    tables["cp1.model_period_register"] = _periods(FY2025, ltm)
    regs = cp1_registers(tables)
    assert (regs.currency, regs.unit) == ("USD", "MILLIONS")
    assert regs.periods[0].day_count == 365
    assert regs.periods[0].fiscal_quarter is None
    account = regs.accounts[0]
    assert (account.value, account.calculation_status) == (Decimal("11245.0"), "VERIFIED")
    assert account.source == SourceRef("[C3]", "p.61", "11,245.0 [C3]")
    addback = regs.addbacks[0]
    assert (addback.classification, addback.realization_status) == ("SYNERGY", "UNREALIZED")
    assert regs.segments[0].segment_type == "OPERATING_SEGMENT"
    assert regs.segments[0].revenue == Decimal(4213)
    kpi = regs.kpis[0]
    assert (kpi.value, kpi.unit, kpi.source) == (Decimal("96.1"), "PERCENT", None)
    facility = regs.facilities[0]
    assert facility.facility_type == "TERM LOAN"
    assert (facility.carrying_value, facility.commitment) == (Decimal(2018), None)
    assert (facility.rate_type, facility.reference_rate) == ("NOT_STATED", "NOT_STATED")
    assert facility.terms_out_of_range is False
    assert regs.pro_forma[0].classification == "REFINANCING"
    assert regs.pro_forma[0].metric_id == "facility:TLB"


@pytest.mark.parametrize("null", ["—", "n/a", "null", "", "-"])
def test_null_text_is_no_figure(null: str) -> None:
    regs = cp1_registers(_tables(debt_facility_register=_facility(carrying_value=null)))
    assert regs.facilities[0].carrying_value is None


def test_text_that_is_not_a_figure_is_refused_naming_where() -> None:
    _refused(
        _tables(debt_facility_register=_facility(carrying_value="about 2bn")),
        "cp1.debt_facility_register row 1 column carrying_value: 'about 2bn' is not a figure",
    )


@pytest.mark.parametrize(
    ("cells", "match"),
    [
        ({"seniority": "Senior secured"}, "row 1 column seniority: 'Senior secured' is not one of"),
        ({"secured_status": "—"}, "row 1 column secured_status: required, found null"),
        ({"facility_id": "—"}, "row 1 column facility_id: required, found null"),
        ({"carrying_value": "-5"}, "column carrying_value: negative outside a DEBT ADJUSTMENT"),
        ({"commitment": "-1"}, "row 1 column commitment: cannot be negative"),
        ({"carrying_value": "1e18"}, "column carrying_value: figure out of range"),
        ({"carrying_value": "1e999999x"}, "column carrying_value: figure out of range"),
        ({"carrying_value": "0.12345678901"}, "column carrying_value: more than 10 decimals"),
    ],
)
def test_a_bad_facility_row_is_refused_naming_where(cells: dict[str, str], match: str) -> None:
    _refused(_tables(debt_facility_register=_facility(**cells)), match)


def test_enumerations_read_canonical_spellings_and_open_columns_upper_case() -> None:
    table = _facility(
        facility_type="debt-adjustment",
        carrying_value="(170)",
        currency="usd",
        seniority="super senior",
        lease_classification="finance lease",
    )
    row = cp1_registers(_tables(debt_facility_register=table)).facilities[0]
    assert row.facility_type == "DEBT ADJUSTMENT"
    assert row.carrying_value == Decimal(-170)
    assert (row.currency, row.seniority) == ("USD", "SUPER_SENIOR")
    assert row.lease_classification == "FINANCE_LEASE"


def test_rate_terms_read_not_stated_or_flag_a_wrong_unit() -> None:
    terms = {"rate_type": "floating", "reference_rate": "term sofr", "spread_bps": "225"}
    row = cp1_registers(_tables(debt_facility_register=_facility(**terms))).facilities[0]
    assert (row.rate_type, row.reference_rate) == ("FLOATING", "TERM_SOFR")
    assert (row.spread_bps, row.terms_out_of_range) == (Decimal(225), False)
    for wrong in ({"spread_bps": "2.25%"}, {"floor_bps": "0.5"}, {"fixed_rate": "0.065"}):
        row = cp1_registers(_tables(debt_facility_register=_facility(**wrong))).facilities[0]
        assert row.terms_out_of_range is True, wrong
