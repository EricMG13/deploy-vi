"""The worked-example Model and cell edits shared by the Model tests (split from
caos `tests/test_credit_model_assemble.py`)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers

from rbotlib.model.assemble import (
    CreditModel,
    ModelInputs,
    credit_model,
)
from rbotlib.model.frame import Cell
from rbotlib.model.layout import (
    Line,
)
from rbotlib.model.registers import Cp1Registers

_PF = "PF:LTM_Q2_2026"


_LTM = "LTM:LTM_Q2_2026"


def _model(regs: Cp1Registers | None = None, *, exclude_unrealised: bool = False) -> CreditModel:
    inputs = ModelInputs(regs or example_registers(), exclude_unrealised=exclude_unrealised)
    return credit_model(inputs)


def _line(model: CreditModel, line_id: str) -> Line:
    return next(line for line in model.lines if line.line_id == line_id)


def _cell(model: CreditModel, line_id: str, column_id: str) -> Cell:
    index = [c.column_id for c in model.columns].index(column_id)
    return _line(model, line_id).cells[index]


def _value(model: CreditModel, line_id: str, column_id: str) -> Decimal:
    value = _cell(model, line_id, column_id).value
    assert value is not None, (line_id, column_id)
    return value


def _with_cell(model: CreditModel, line_id: str, column_id: str, cell: Cell) -> CreditModel:
    """The model with one cell replaced."""
    index = [c.column_id for c in model.columns].index(column_id)
    lines = tuple(
        replace(
            line,
            cells=tuple(
                cell if i == index and line.line_id == line_id else old
                for i, old in enumerate(line.cells)
            ),
        )
        for line in model.lines
    )
    return replace(model, lines=lines)


def _nudged(model: CreditModel, line_id: str, column_id: str) -> CreditModel:
    """The model with one cell's figure one higher."""
    cell = _cell(model, line_id, column_id)
    assert cell.value is not None, (line_id, column_id)
    return _with_cell(model, line_id, column_id, replace(cell, value=cell.value + 1))


def _signed_zeros(model: CreditModel) -> list[tuple[str, str]]:
    return [
        (line.line_id, column.column_id)
        for line in model.lines
        for column, cell in zip(model.columns, line.cells, strict=True)
        for figure in (cell.value, cell.stated)
        if figure is not None and figure.is_zero() and figure.is_signed()
    ]
