"""CP-1's registers written as a Handoff read back to the same figures."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers
from hypothesis import given, settings
from hypothesis import strategies as st
from model_handoffs import cp1_handoff

from rbotlib.handoff import parse
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.registers import Cp1Registers

_FIGURES = st.one_of(
    st.none(),
    st.decimals(min_value=Decimal("-1e12"), max_value=Decimal("1e12"), places=4),
)


@st.composite
def _registers(draw: st.DrawFn) -> Cp1Registers:
    regs = example_registers()
    accounts = tuple(replace(a, value=draw(_FIGURES)) for a in regs.accounts[:40])
    return replace(regs, accounts=accounts)


def _figures(regs: Cp1Registers) -> list[tuple[str, str, Decimal | None]]:
    return [(a.metric_id, a.period_id, a.value) for a in regs.accounts]


@settings(max_examples=25, deadline=None)
@given(regs=_registers())
def test_written_figures_read_back_exactly(regs: Cp1Registers) -> None:
    back = cp1_registers(parse(cp1_handoff(regs)).tables)
    assert _figures(back) == [
        (m, p, None if v is None else (v.copy_abs() if v.is_zero() else v))
        for m, p, v in _figures(regs)
    ]
    assert back.periods == regs.periods
    assert [f.carrying_value for f in back.facilities] == [
        f.carrying_value for f in regs.facilities
    ]
    assert [(a.metric_id, a.value) for a in back.pro_forma] == [
        (a.metric_id, a.value) for a in regs.pro_forma
    ]
    assert all(a.source is None or a.source.source_id.startswith("[C") for a in back.accounts)
