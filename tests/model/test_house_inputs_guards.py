"""CP-1D, equity and Run Brief refusals and the per add-back house status
(up-front money review, 2026-10-11): each test starts from the reviewer's
probe input and fails on the code before the fix."""

from __future__ import annotations

import re
from contextlib import AbstractContextManager
from dataclasses import replace

import pytest
from credit_model_fixture import example_registers

from rbotlib.handoff import Table
from rbotlib.model.house_inputs import (
    AddbackAssessment,
    assessment_limitations,
    brief_fields,
    debt_like_items,
    effective_registers,
    equity_value,
)
from rbotlib.model.reader import ModelInputError

DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]
LTM = "LTM_Q2_2026"


def _debt_like(*rows: tuple[str, str]) -> Table:
    """Debt-like rows from (item, period_id) pairs."""
    return Table(
        DEBT_LIKE,
        [
            [item, "120", "USD", "MILLIONS", period, "Debt-like", "b", "[C3]"]
            for item, period in rows
        ],
    )


def _refused(match: str) -> AbstractContextManager[pytest.ExceptionInfo[ModelInputError]]:
    return pytest.raises(ModelInputError, match=re.escape(match))


def test_two_names_for_one_debt_like_line_are_refused() -> None:
    # Probe p2_debtlike D: "Pension deficit" and "pension-deficit" in one period.
    table = _debt_like(("Pension deficit", LTM), ("pension-deficit", "FY2025"))
    with _refused("cp1d.debt_like_items row 2 column item: 'pension-deficit' and"):
        debt_like_items({"cp1d.debt_like_items": table}, example_registers())


def test_one_debt_like_item_twice_on_one_balance_date_is_refused() -> None:
    table = _debt_like(("Pension deficit", "Q2_2026"), ("Pension deficit", "H1_2026"))
    with _refused("row 2: debt_like:pension_deficit / 2026-06-30 written twice"):
        debt_like_items({"cp1d.debt_like_items": table}, example_registers())


def test_a_debt_like_item_in_an_unknown_period_is_refused() -> None:
    table = _debt_like(("Pension deficit", "Q2_2O26"))
    with _refused("row 1 column period_id: Q2_2O26 is not a CP-1 period"):
        debt_like_items({"cp1d.debt_like_items": table}, example_registers())


def test_a_listed_equity_value_and_an_ev_multiple_must_be_above_zero() -> None:
    columns = ["market_cap", "value_date", "currency", "unit", "cite"]
    table = Table(columns, [["0", "2026-10-02", "USD", "MILLIONS", "[C9]"]])
    with _refused("cp1.equity_value row 1 column market_cap: 0 is not above zero"):
        equity_value({"cp1.equity_value": table})
    # Probe p5_ev: a Run Brief multiple of -3.
    header = Table(["run_id", "primary", "ssim_ev_multiple_x"], [["R1", "No", "-3x"]])
    with _refused("snapshot.run_header row 1 column ssim_ev_multiple_x: -3 is not above zero"):
        brief_fields({}, {"snapshot.run_header": header})


def test_an_assessment_of_an_add_back_cp1_does_not_have_is_refused() -> None:
    # Probe p4_assess: the typo `restructuring_costs`.
    typo = AddbackAssessment("restructuring_costs", "FY2025", "REALIZED", "Rejected", "[C1]")
    with _refused("cp1d.addback_assessment row 1 column addback_id: restructuring_costs"):
        effective_registers(example_registers(), (typo,))


def test_an_excluding_assessment_applies_to_the_add_back_as_a_whole() -> None:
    # Probe p4_assess: CP-1 states no add-back row for the LTM; CP-1D rejects
    # restructuring for the LTM.
    regs = example_registers()
    regs = replace(regs, addbacks=tuple(b for b in regs.addbacks if b.period_id != LTM))
    rejected = AddbackAssessment("restructuring", LTM, "REALIZED", "Rejected", "[C1]")
    found = effective_registers(regs, (rejected,))
    statuses = {b.realization_status for b in found.addbacks if b.addback_id == "restructuring"}
    assert statuses == {"UNREALIZED"}
    others = [b for b in found.addbacks if b.addback_id != "restructuring"]
    assert others == [b for b in regs.addbacks if b.addback_id != "restructuring"]


def test_a_non_ltm_realized_assessment_left_excluded_elsewhere_is_noted() -> None:
    regs = example_registers()
    supported = AddbackAssessment(
        "run_rate_cost_savings", "FY2025", "REALIZED", "Supported", "[C1]"
    )
    found = effective_registers(regs, (supported,))
    (code, why), *more = assessment_limitations(found, (supported,))
    assert (code, more) == ("ADDBACK_STATUS_MIXED", [])
    assert why.startswith("run_rate_cost_savings: CP-1D assesses REALIZED for FY2025")
    assert assessment_limitations(regs, ()) == []


def test_the_latest_ltm_judgment_reclassifies_every_period_realized() -> None:
    # Owner ruling 2026-10-12: latest LTM judgment governs each add-back throughout.
    regs = example_registers()
    latest = AddbackAssessment("run_rate_cost_savings", LTM, "REALIZED", "Supported", "[C1]")
    old = AddbackAssessment("run_rate_cost_savings", "FY2025", "UNREALIZED", "Challenged", "[C1]")
    effective = effective_registers(regs, (old, latest))
    rows = [b for b in effective.addbacks if b.addback_id == latest.addback_id]
    assert rows and {b.realization_status for b in rows} == {"REALIZED"}
    assert assessment_limitations(effective, (latest,)) == []


def test_conflicting_latest_ltm_judgments_are_refused() -> None:
    realized = AddbackAssessment("run_rate_cost_savings", LTM, "REALIZED", "Supported", "[C1]")
    rejected = replace(realized, verdict="Rejected")
    with _refused("contradictory LTM judgments"):
        effective_registers(example_registers(), (realized, rejected))


def test_an_assessment_in_an_unknown_period_is_refused() -> None:
    typo = AddbackAssessment("restructuring", "LTM_TYPO", "REALIZED", "Supported", "[C1]")
    with _refused("column period_id: LTM_TYPO is not a CP-1 period"):
        effective_registers(example_registers(), (typo,))


def test_a_newer_ltm_judgment_wins_over_an_older_ltm_in_any_order() -> None:
    regs = example_registers()
    old = replace(
        next(p for p in regs.periods if p.period_id == LTM),
        period_id="LTM_OLD",
        end_date="2025-06-30",
    )
    regs = replace(regs, periods=(*regs.periods, old))
    latest = AddbackAssessment("run_rate_cost_savings", LTM, "REALIZED", "Supported", "[C1]")
    older = replace(latest, period_id="LTM_OLD", verdict="Rejected")
    for judgments in ((latest, older), (older, latest)):
        rows = effective_registers(regs, judgments).addbacks
        assert {b.realization_status for b in rows if b.addback_id == latest.addback_id} == {
            "REALIZED"
        }


def test_an_ltm_judgment_with_no_date_is_refused() -> None:
    regs = example_registers()
    periods = tuple(replace(p, end_date=None) if p.period_id == LTM else p for p in regs.periods)
    judgment = AddbackAssessment("restructuring", LTM, "REALIZED", "Supported", "[C1]")
    with _refused("LTM_Q2_2026 has no end date"):
        effective_registers(replace(regs, periods=periods), (judgment,))


def test_an_older_ltm_judgment_does_not_upgrade_the_unassessed_latest_ltm() -> None:
    regs = example_registers()
    old = replace(
        next(p for p in regs.periods if p.period_id == LTM),
        period_id="LTM_OLD",
        end_date="2025-06-30",
    )
    regs = replace(regs, periods=(*regs.periods, old))
    older = AddbackAssessment("run_rate_cost_savings", "LTM_OLD", "REALIZED", "Supported", "[C1]")
    effective = effective_registers(regs, (older,))
    assert {
        b.realization_status for b in effective.addbacks if b.addback_id == older.addback_id
    } == {"UNREALIZED"}
    assert assessment_limitations(effective, (older,))[0][0] == "ADDBACK_STATUS_MIXED"


def test_contradictory_older_ltm_judgments_do_not_override_the_latest_date() -> None:
    regs = example_registers()
    old = replace(
        next(p for p in regs.periods if p.period_id == LTM),
        period_id="LTM_OLD",
        end_date="2025-06-30",
    )
    regs = replace(regs, periods=(*regs.periods, old))
    latest = AddbackAssessment("run_rate_cost_savings", LTM, "REALIZED", "Supported", "[C1]")
    older = replace(latest, period_id="LTM_OLD")
    rejected = replace(older, verdict="Rejected")
    effective = effective_registers(regs, (older, rejected, latest))
    assert {
        b.realization_status for b in effective.addbacks if b.addback_id == latest.addback_id
    } == {"REALIZED"}


def test_positive_equity_and_ev_multiples_below_one_are_valid() -> None:
    # Mutation _positive 7 changed the financial boundary from 0 to 1.
    table = Table(
        ["market_cap", "value_date", "currency", "unit", "cite"],
        [["0.5", "2026-10-02", "USD", "MILLIONS", "[C9]"]],
    )
    equity = equity_value({"cp1.equity_value": table})
    assert equity is not None and str(equity.market_cap) == "0.5"
    header = Table(["run_id", "primary", "ssim_ev_multiple_x"], [["R1", "No", "0.5x"]])
    assert str(brief_fields({}, {"snapshot.run_header": header}).ssim_ev_multiple) == "0.5"


def test_distinct_debt_like_items_on_one_date_are_both_accepted() -> None:
    table = _debt_like(("Pension deficit", LTM), ("Environmental provisions", LTM))
    found = debt_like_items({"cp1d.debt_like_items": table}, example_registers())
    assert [d.item for d in found] == ["Pension deficit", "Environmental provisions"]


def test_a_rejected_assessment_does_not_hide_later_legacy_status_limitations() -> None:
    regs = example_registers()
    rejected = AddbackAssessment("restructuring", LTM, "REALIZED", "Rejected", "[C1]")
    supported = AddbackAssessment(
        "run_rate_cost_savings", "FY2025", "REALIZED", "Supported", "[C1]"
    )
    judgments = (rejected, supported)
    effective = effective_registers(regs, judgments)
    found = assessment_limitations(effective, judgments)
    assert len(found) == 1 and found[0][1].startswith("run_rate_cost_savings: CP-1D")


def test_a_legacy_status_limitation_names_all_excluded_periods() -> None:
    regs = example_registers()
    addbacks = tuple(
        b
        for b in regs.addbacks
        if b.addback_id == "run_rate_cost_savings" and b.period_id in {"FY2023", "FY2024", "FY2025"}
    )
    regs = replace(regs, addbacks=addbacks)
    supported = AddbackAssessment(
        "run_rate_cost_savings", "FY2025", "REALIZED", "Supported", "[C1]"
    )
    effective = effective_registers(regs, (supported,))
    assert assessment_limitations(effective, (supported,)) == [
        (
            "ADDBACK_STATUS_MIXED",
            "run_rate_cost_savings: CP-1D assesses REALIZED for FY2025 but FY2023, FY2024 "
            "stays unrealized; the add-back is excluded on every column",
        )
    ]


def test_ltm_judgment_selection_ignores_newer_non_ltm_periods() -> None:
    regs = example_registers()
    future = replace(
        next(p for p in regs.periods if p.period_id == "FY2025"),
        period_id="FY2027",
        fiscal_year="2027",
        start_date="2027-01-01",
        end_date="2027-12-31",
    )
    regs = replace(regs, periods=(*regs.periods, future))
    supported = AddbackAssessment("run_rate_cost_savings", LTM, "REALIZED", "Supported", "[C1]")
    rows = effective_registers(regs, (supported,)).addbacks
    assert {b.realization_status for b in rows if b.addback_id == supported.addback_id} == {
        "REALIZED"
    }


def test_the_latest_ltm_judgment_can_be_newer_than_every_other_period() -> None:
    regs = example_registers()
    latest = replace(
        next(p for p in regs.periods if p.period_id == LTM),
        period_id="LTM_NEW",
        fiscal_year="2027",
        start_date="2026-07-01",
        end_date="2027-06-30",
    )
    regs = replace(regs, periods=(*regs.periods, latest))
    supported = AddbackAssessment(
        "run_rate_cost_savings", "LTM_NEW", "REALIZED", "Supported", "[C1]"
    )
    rows = effective_registers(regs, (supported,)).addbacks
    assert {b.realization_status for b in rows if b.addback_id == supported.addback_id} == {
        "REALIZED"
    }


def test_a_legacy_exclusion_without_a_cp1_row_is_not_lost() -> None:
    regs = example_registers()
    regs = replace(regs, addbacks=tuple(b for b in regs.addbacks if b.period_id != "FY2025"))
    rejected = AddbackAssessment("restructuring", "FY2025", "REALIZED", "Rejected", "[C1]")
    rows = effective_registers(regs, (rejected,)).addbacks
    assert {b.realization_status for b in rows if b.addback_id == rejected.addback_id} == {
        "UNREALIZED"
    }
