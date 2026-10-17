"""History read through the whole Model (needs `rbotlib.model.assemble`)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers
from history_frames import _without_ltm_rows, _written_positive

from rbotlib.model import history
from rbotlib.model._cells import (
    SIGN_NORMALISED,
)
from rbotlib.model.assemble import (
    CreditModel,
    ModelInputs,
    credit_model,
)
from rbotlib.model.frame import Cell
from rbotlib.model.registers import (
    Cp1Registers,
)


def _model_inputs(regs: Cp1Registers) -> ModelInputs:
    return ModelInputs(registers=regs, exclude_unrealised=False)


def _line_cell(model: CreditModel, line_id: str, column_id: str) -> Cell:
    columns = [c.column_id for c in model.columns]
    line = next(x for x in model.lines if x.line_id == line_id)
    return line.cells[columns.index(column_id)]


def test_the_audits_h1_2026_written_positive_keeps_the_ltm_coverage() -> None:
    # The audit's C1 probe: Q1 and Q2 2026 capex and cash interest written
    # positive read 681.5x interest coverage before the fix.
    regs = _without_ltm_rows(example_registers())
    flows = {"capex_and_intangible_investment", "cash_interest_paid"}
    hostile = _written_positive(regs, {"Q1_2026", "Q2_2026"}, flows)
    base = credit_model(_model_inputs(regs))
    model = credit_model(_model_inputs(hostile))
    ltm = "LTM:LTM_Q2_2026"
    interest = _line_cell(model, "cash_interest", ltm)
    assert (interest.value, interest.note) == (Decimal(-862), SIGN_NORMALISED)
    for line_id in (
        "capex",
        "fcf",
        "metric:interest_coverage_adjusted",
        "metric:capex_adjusted_coverage",
        "metric:fcf_to_debt",
    ):
        assert _line_cell(model, line_id, ltm).value == _line_cell(base, line_id, ltm).value, (
            line_id
        )
    coverage = _line_cell(model, "metric:interest_coverage_adjusted", ltm).value
    assert coverage is not None and Decimal("4.74") < coverage < Decimal("4.75")


def test_a_one_sided_interim_leaves_the_ltm_cash_flow_missing() -> None:
    regs = _without_ltm_rows(example_registers())
    ltm = "LTM:LTM_Q2_2026"
    base = credit_model(_model_inputs(regs))
    prior = {"Q1_2025", "Q2_2025", "H1_2025"}
    one_sided = replace(
        regs,
        accounts=tuple(
            a
            for a in regs.accounts
            if not (a.metric_id == "interest_paid_in_financing" and a.period_id in prior)
        ),
    )
    model = credit_model(_model_inputs(one_sided))
    for line_id in ("cfo_adjusted", "fcf", "metric:fcf_to_debt"):
        assert _line_cell(base, line_id, ltm).value is not None, line_id
        assert _line_cell(model, line_id, ltm).value is None, line_id
    # Interest in financing has no line of its own: every figure built from
    # it names why it is missing, and the limitation is served through them.
    for line_id in ("cfo_adjusted", "fcf", "metric:fcf_to_debt"):
        cell = _line_cell(model, line_id, ltm)
        assert (cell.reason, cell.note) == (
            "COMPONENT_MISSING",
            history.PARTLY_STATED,
        ), line_id
    assert f"{history.PARTLY_STATED}: {ltm}" in model.limitations
    leases = replace(
        regs,
        accounts=tuple(
            a
            for a in regs.accounts
            if not (a.metric_id == "lease_payments_in_financing" and a.period_id in prior)
        ),
    )
    model_leases = credit_model(_model_inputs(leases))
    lease = _line_cell(model_leases, "lease_cash_not_in_ebitda", ltm)
    assert (lease.reason, lease.note) == ("COMPONENT_MISSING", history.PARTLY_STATED)
    assert f"{history.PARTLY_STATED}: {ltm}" in model_leases.limitations
    assert _line_cell(model_leases, "fcf", ltm).value is None
    # The fully stated lines are untouched.
    for line_id in ("revenue", "cash_interest", "capex"):
        assert _line_cell(model, line_id, ltm) == _line_cell(base, line_id, ltm)

    neither = replace(
        one_sided,
        accounts=tuple(
            a
            for a in one_sided.accounts
            if not (
                a.metric_id == "interest_paid_in_financing"
                and a.period_id in {"Q1_2026", "Q2_2026", "H1_2026"}
            )
        ),
    )
    model = credit_model(_model_inputs(neither))
    assert _line_cell(model, "fcf", ltm).value is not None
