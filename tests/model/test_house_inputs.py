"""What the house view reads besides CP-1's registers (spec §6.6)."""

from __future__ import annotations

import re
from contextlib import AbstractContextManager
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers

from rbotlib.handoff import Table
from rbotlib.model.house_inputs import (
    AddbackAssessment,
    assessments,
    brief_fields,
    check_entity_profile,
    debt_like_items,
    effective_registers,
    equity_value,
    identities,
)
from rbotlib.model.reader import ModelInputError

GAP = "—"


def _refused(match: str) -> AbstractContextManager[pytest.ExceptionInfo[ModelInputError]]:
    return pytest.raises(ModelInputError, match=re.escape(match))


def test_identities_read_ratings_as_one_text() -> None:
    columns = ["facility_id", "instrument_name", "bloomberg_id", "rating_moodys", "rating_sp"]
    columns += ["rating_fitch", "cite"]
    rows = [
        ["tlb", "Term Loan B", "BL1234567", "Ba3", "BB", GAP, "[C4]"],
        ["sun29", "4.625% notes", GAP, GAP, GAP, GAP, "[C5]"],
    ]
    found = identities({"cp1.instrument_identity": Table(columns, rows)})
    assert found["tlb"].ratings == "Ba3 / BB / —"
    assert found["tlb"].bloomberg_id == "BL1234567"
    assert (found["sun29"].ratings, found["sun29"].bloomberg_id) == (None, None)
    assert identities({}) == {}
    twice = Table(columns, [rows[0], rows[0]])
    with _refused("cp1.instrument_identity row 2: tlb written twice"):
        identities({"cp1.instrument_identity": twice})


EQUITY = ["market_cap", "share_price", "shares_outstanding", "value_date", "currency", "unit"]
EQUITY += ["cite"]


def test_equity_value_reads_one_row_at_most() -> None:
    row = ["6,316", "31.00", "203.7", "2026-10-02", "USD", "MILLIONS", "[C9]"]
    found = equity_value({"cp1.equity_value": Table(EQUITY, [row])})
    assert found is not None
    assert (found.market_cap, found.value_date, found.unit) == (
        Decimal(6316),
        "2026-10-02",
        "MILLIONS",
    )
    assert equity_value({}) is None
    with _refused("cp1.equity_value row 2: one listed equity value per run"):
        equity_value({"cp1.equity_value": Table(EQUITY, [row, row])})
    undated = [*row[:3], GAP, *row[4:]]
    with _refused("cp1.equity_value row 1 column value_date: required, found null"):
        equity_value({"cp1.equity_value": Table(EQUITY, [undated])})


def test_entity_profile_must_report_in_the_run_currency_and_unit() -> None:
    regs = example_registers()
    columns = ["entity", "role", "reporting_currency", "reporting_unit", "cite"]
    good = Table(columns, [["EGC", "Borrower", "usd", "millions", "[C1]"]])
    check_entity_profile({"cp1.entity_profile": good}, regs)
    eur = Table(columns, [["EGC", "Borrower", "EUR", "MILLIONS", "[C1]"]])
    with _refused("cp1.entity_profile row 1 column reporting_currency: EUR is not USD"):
        check_entity_profile({"cp1.entity_profile": eur}, regs)
    thousands = Table(columns, [["EGC", "Borrower", "USD", "THOUSANDS", "[C1]"]])
    with _refused("column reporting_unit: THOUSANDS is not MILLIONS"):
        check_entity_profile({"cp1.entity_profile": thousands}, regs)


ASSESSMENT = ["addback_id", "period_id", "amount", "currency", "unit", "category"]
ASSESSMENT += ["house_realization_status", "verdict", "rationale", "recurrence", "cite"]


def _assessment(addback_id: str, period_id: str, status: str, verdict: str) -> list[str]:
    return [addback_id, period_id, "1", "USD", "MILLIONS", "x", status, verdict, "r", "No", "[C2]"]


def test_effective_registers_take_cp1d_status_and_reject_as_unrealized() -> None:
    rows = [
        _assessment("restructuring", "LTM_Q2_2026", "REALIZED", "Rejected"),
        _assessment("run_rate_cost_savings", "LTM_Q2_2026", "REALIZED", "Supported"),
        _assessment("transaction_costs", "FY2025", "UNREALIZED", "Challenged"),
    ]
    found = assessments({"cp1d.addback_assessment": Table(ASSESSMENT, rows)})
    assert found[0] == AddbackAssessment(
        "restructuring", "LTM_Q2_2026", "REALIZED", "Rejected", "[C2]"
    )
    regs = effective_registers(example_registers(), found)
    status = {(b.addback_id, b.period_id): b.realization_status for b in regs.addbacks}
    assert status[("restructuring", "LTM_Q2_2026")] == "UNREALIZED"
    assert status[("run_rate_cost_savings", "LTM_Q2_2026")] == "REALIZED"
    assert status[("transaction_costs", "FY2025")] == "UNREALIZED"
    # Not assessed: the add-back's excluding status (per add-back, spec §6.5).
    assert status[("restructuring", "FY2025")] == "UNREALIZED"
    bad = [_assessment("restructuring", "FY2025", "REALIZED", "Accepted")]
    with _refused("cp1d.addback_assessment row 1 column verdict: 'Accepted' is not one of"):
        assessments({"cp1d.addback_assessment": Table(ASSESSMENT, bad)})


DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]


def test_debt_like_items_must_be_in_the_run_currency_and_unit() -> None:
    regs = example_registers()
    row = [
        "Pension deficit",
        "120",
        "USD",
        "MILLIONS",
        "LTM_Q2_2026",
        "Debt-like",
        "unfunded",
        "[C3]",
    ]
    found = debt_like_items({"cp1d.debt_like_items": Table(DEBT_LIKE, [row])}, regs)
    assert (found[0].amount, found[0].treatment) == (Decimal(120), "Debt-like")
    eur = [*row[:2], "EUR", *row[3:]]
    with _refused("cp1d.debt_like_items row 1 column currency: EUR is not the run's USD"):
        debt_like_items({"cp1d.debt_like_items": Table(DEBT_LIKE, [eur])}, regs)
    units = [*row[:3], "UNITS", *row[4:]]
    with _refused("column unit: UNITS is not the run's MILLIONS"):
        debt_like_items({"cp1d.debt_like_items": Table(DEBT_LIKE, [units])}, regs)


HEADER = ["run_id", "primary", "ssim_ev_multiple_x"]


def test_brief_fields_read_the_multiple_primary_flag_and_tranches() -> None:
    tables = {
        "snapshot.run_header": Table(HEADER, [["R1", "Yes", "7.5x"]]),
        "snapshot.transaction_summary": Table(["tranche_id"], [["NEW-1"], ["NEW-2"]]),
    }
    found = brief_fields({"run_id": "R0"}, tables)
    assert (found.run_id, found.primary, found.ssim_ev_multiple) == ("R0", True, Decimal("7.5"))
    assert found.tranche_ids == frozenset({"NEW-1", "NEW-2"})
    plain = brief_fields({}, {"snapshot.run_header": Table(HEADER, [["R1", "No", GAP]])})
    assert (plain.run_id, plain.primary, plain.ssim_ev_multiple) == ("R1", False, None)
    with _refused("snapshot.run_header: needs exactly one row, found 0"):
        brief_fields({}, {})
    with _refused("snapshot.run_header row 1 column primary: 'Maybe' is not one of"):
        brief_fields({}, {"snapshot.run_header": Table(HEADER, [["R1", "Maybe", GAP]])})
