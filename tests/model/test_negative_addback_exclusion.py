"""Owner decision F11 (2026-10-15): excluding an add-back leaves out only its
positive amounts. A negative amount is a deduction (a net gain, say) and stays
in adjusted EBITDA, so exclusion never raises it. The newest-LTM judgment still
decides which add-backs are excluded, on every column."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers, with_figures
from hypothesis import given, settings
from hypothesis import strategies as st
from statements_cases import _cells, _columns, _frame

from rbotlib.model._cells import DIFFERS
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.statements import pro_forma_column

_KEY = "addback:run_rate_cost_savings"
_NEGATIVE_PERIODS = {"Q3_2025", "Q4_2025", "FY2025"}


def _mixed(regs: Cp1Registers, negative: set[str]) -> Cp1Registers:
    """The unrealised run-rate savings negative in `negative` periods."""
    rows = tuple(
        replace(b, value=-(b.value or Decimal(0)))
        if b.addback_id == "run_rate_cost_savings" and b.period_id in negative
        else b
        for b in regs.addbacks
    )
    return replace(regs, addbacks=rows)


def _with_stated(regs: Cp1Registers, period: str, figure: Decimal) -> Cp1Registers:
    return with_figures(regs, period, {"adjusted_ebitda": figure})


def test_a_negative_amount_stays_and_a_positive_one_goes_on_each_column() -> None:
    regs = _mixed(example_registers(), _NEGATIVE_PERIODS)
    for label, sign in (("Q3 25", -1), ("FY25", -1), ("Q2 26", 1)):
        kept, excluded = _cells(regs, label), _cells(regs, label, exclude=True)
        amount = kept[_KEY].value
        assert amount is not None and amount * sign > 0, label
        removed = amount if amount > 0 else Decimal(0)
        all_in, all_in_r = kept["adjusted_ebitda"].value, kept["adjusted_ebitdar"].value
        assert all_in is not None and all_in_r is not None
        assert excluded["adjusted_ebitda"].value == all_in - removed
        assert excluded["adjusted_ebitdar"].value == all_in_r - removed
    # Q3 25: the -10 stays, so exclusion changes nothing; Q2 26: the +10 goes.
    assert _cells(regs, "Q3 25", exclude=True)["adjusted_ebitda"].value == 1002
    assert _cells(regs, "Q2 26", exclude=True)["adjusted_ebitda"].value == 1043


@pytest.mark.parametrize("negative", [True, False])
def test_the_ltm_and_pf_columns_follow_the_same_rule(negative: bool) -> None:
    regs = example_registers()
    if negative:
        regs = _mixed(
            regs, {"LTM_Q2_2026", "FY2025", "H1_2026", "Q3_2025", "Q4_2025", "Q1_2026", "Q2_2026"}
        )
    ltm = _columns(regs)["LTM Q2 26"]
    frame = _frame(regs, True)
    kept = _cells(regs, "LTM Q2 26")
    assert kept[_KEY].value == (-40 if negative else 40)
    removed = 0 if negative else 40
    adjusted = frame[ltm.column_id]["adjusted_ebitda"].value
    all_in = kept["adjusted_ebitda"].value
    assert all_in is not None
    assert adjusted == all_in - removed
    found = pro_forma_column(regs, ltm, frame)
    assert found is not None
    pf = next(iter(found[1].values()))["adjusted_ebitda"].value
    assert pf is not None and adjusted is not None
    # The PF row adds to the LTM figure only; the kept negative stays in both.
    assert pf - adjusted == sum(
        a.value for a in regs.pro_forma if a.metric_id in {"ebitda", "adjusted_ebitda"}
    )


def test_the_note_claims_excluded_only_where_something_was_removed() -> None:
    regs = _mixed(example_registers(), _NEGATIVE_PERIODS)
    assert _cells(regs, "Q3 25", exclude=True)[_KEY].note != "excluded"
    assert _cells(regs, "FY25", exclude=True)[_KEY].note != "excluded"
    assert _cells(regs, "Q2 26", exclude=True)[_KEY].note == "excluded"


def test_cp1_stated_is_compared_exactly_where_nothing_was_left_out() -> None:
    base = _mixed(example_registers(), _NEGATIVE_PERIODS)
    # Negative column: the negative is kept, nothing left out, so it is compared.
    figure = _cells(base, "Q3 25")["adjusted_ebitda"].value
    assert figure is not None
    agree = _cells(_with_stated(base, "Q3_2025", figure), "Q3 25", exclude=True)
    assert agree["adjusted_ebitda"].note is None
    assert agree["adjusted_ebitda"].stated == figure
    apart = _cells(_with_stated(base, "Q3_2025", figure + 500), "Q3 25", exclude=True)
    assert apart["adjusted_ebitda"].note == DIFFERS
    # Positive column: the 10 was left out, so CP-1's figure is kept, not compared.
    out = _cells(_with_stated(base, "Q2_2026", Decimal(9999)), "Q2 26", exclude=True)
    assert out["adjusted_ebitda"].note is None
    assert out["adjusted_ebitda"].stated == 9999


@given(
    amounts=st.lists(st.integers(-60, 60), min_size=4, max_size=4),
    flags=st.lists(st.booleans(), min_size=4, max_size=4),
)
@settings(max_examples=60, deadline=None)
def test_excluding_add_backs_never_raises_adjusted_ebitda(
    amounts: list[int], flags: list[bool]
) -> None:
    """For any amounts and any excluded subset on a reported column:
    adjusted(excluded) == EBITDA + included add-backs + negative excluded
    amounts == all-included adjusted - positive excluded amounts, hence
    adjusted(excluded) <= all-included adjusted, and <= EBITDA + included +
    negative excluded."""
    regs = example_registers()
    ids = [
        "restructuring",
        "stock_based_compensation",
        "transaction_costs",
        "run_rate_cost_savings",
    ]
    value = dict(zip(ids, map(Decimal, amounts), strict=True))
    out = dict(zip(ids, flags, strict=True))
    regs = replace(
        regs,
        addbacks=tuple(
            replace(
                b,
                value=value[b.addback_id] if b.period_id == "Q2_2026" else b.value,
                realization_status="UNREALIZED" if out[b.addback_id] else "REALIZED",
            )
            for b in regs.addbacks
        ),
    )
    everything = _cells(regs, "Q2 26")
    result = _cells(regs, "Q2 26", exclude=True)
    positive = sum((value[i] for i in ids if out[i] and value[i] > 0), Decimal(0))
    negative = sum((value[i] for i in ids if out[i] and value[i] < 0), Decimal(0))
    included = sum((value[i] for i in ids if not out[i]), Decimal(0))
    adjusted, ebitda = result["adjusted_ebitda"].value, result["ebitda"].value
    assert adjusted is not None and ebitda is not None
    all_in = everything["adjusted_ebitda"].value
    assert all_in is not None
    assert adjusted == all_in - positive
    assert adjusted == ebitda + included + negative
    assert adjusted <= all_in
    assert adjusted <= ebitda + included + negative


def test_a_zero_excluded_amount_leaves_nothing_out_so_cp1_is_compared() -> None:
    # Q2 25 has the savings at zero: noted as excluded, but nothing is left out.
    base = example_registers()
    zero = _cells(base, "Q2 25", exclude=True)
    assert zero[_KEY].value == 0 and zero[_KEY].note == "excluded"
    stated = with_figures(base, "Q2_2025", {"adjusted_ebitda": Decimal(9999)})
    assert _cells(stated, "Q2 25", exclude=True)["adjusted_ebitda"].note == DIFFERS
