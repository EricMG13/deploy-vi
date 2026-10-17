"""Deploy VI's additions to the ported model: gross profit growth (spec §6.3)."""

from __future__ import annotations

from decimal import Decimal, localcontext

from credit_model_fixture import example_registers

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.frame import Cell
from rbotlib.model.layout import BANDS
from rbotlib.model.metrics import unit_of


def _model() -> CreditModel:
    return credit_model(ModelInputs(example_registers()))


def _cell(model: CreditModel, line_id: str, column_id: str) -> Cell:
    index = [c.column_id for c in model.columns].index(column_id)
    return next(line for line in model.lines if line.line_id == line_id).cells[index]


def _value(model: CreditModel, line_id: str, column_id: str) -> Decimal:
    value = _cell(model, line_id, column_id).value
    assert value is not None, (line_id, column_id)
    return value


def test_gross_profit_growth_is_a_growth_line_after_gross_margin() -> None:
    model = _model()
    ids = [line.line_id for line in model.lines]
    assert ids.index("gross_profit_growth") == ids.index("metric:gross_margin") + 1
    line = model.lines[ids.index("gross_profit_growth")]
    assert (line.band, line.kind, line.unit) == (BANDS[2], "GROWTH", "PERCENT")
    assert line.label == "Gross profit growth YoY"
    assert unit_of("gross_profit_growth") == "PERCENT"


def test_gross_profit_growth_compares_like_periods() -> None:
    model = _model()

    def growth(column_id: str, prior_id: str) -> Decimal:
        with localcontext(CONTEXT):
            current = _value(model, "gross_profit", column_id)
            return current / _value(model, "gross_profit", prior_id) - 1

    assert _value(model, "gross_profit_growth", "FY:FY2025") == growth("FY:FY2025", "FY:FY2024")
    ytd = growth("YTD:H1_2026", "PYTD:H1_2025")
    assert _value(model, "gross_profit_growth", "YTD:H1_2026") == ytd
    assert _cell(model, "gross_profit_growth", "FY:FY2023") == Cell(None, "NOT_APPLICABLE")
    assert _cell(model, "gross_profit_growth", "PF:LTM_Q2_2026").reason == "NOT_APPLICABLE"
