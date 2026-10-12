"""Gross margin on the PF-LTM (up-front money review M1, 2026-10-11; a caos
gap): gross profit has no PF target, so a PF revenue row leaves no margin."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers

from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.frame import Cell


def _cell(model: CreditModel, line_id: str, kind: str) -> Cell:
    column = next(c for c in model.columns if c.kind == kind)
    line = next(x for x in model.lines if x.line_id == line_id)
    return line.cells[model.columns.index(column)]


def test_pf_revenue_leaves_no_pf_gross_margin() -> None:
    # Probe p9_margin: a PF revenue row of +400.
    regs = example_registers()
    row = next(a for a in regs.pro_forma if a.metric_id == "adjusted_ebitda")
    revenue = replace(
        row, adjustment_id="silverlake_revenue", metric_id="revenue", value=Decimal(400)
    )
    model = credit_model(ModelInputs(replace(regs, pro_forma=(*regs.pro_forma, revenue))))
    margin = _cell(model, "metric:gross_margin", "PF_LTM")
    assert (margin.value, margin.reason) == (None, "NOT_APPLICABLE")
    assert _cell(model, "metric:gross_margin", "LTM").value is not None


def test_without_pf_revenue_the_pf_gross_margin_is_the_ltms() -> None:
    model = credit_model(ModelInputs(example_registers()))
    assert _cell(model, "metric:gross_margin", "PF_LTM") == _cell(
        model, "metric:gross_margin", "LTM"
    )
    assert isinstance(_cell(model, "metric:gross_margin", "LTM").value, Decimal)
