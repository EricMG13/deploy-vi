"""An issuer reporting expenses by nature has no `cogs` row: EBIT is revenue
plus total operating expenses including D&A, gross profit stays blank."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers, with_figures
from hypothesis import given
from hypothesis import strategies as st
from statements_cases import _cells, _values, _without

_PERIOD = "Q2_2026"
_LABEL = "Q2 26"


def test_without_cogs_ebit_is_revenue_plus_opex_and_ebitda_follows() -> None:
    regs = example_registers()
    with_cogs = _cells(regs, _LABEL)
    opex, cogs = with_cogs["opex_total"].value, with_cogs["cogs"].value
    assert opex is not None and cogs is not None
    # Nature of expense: the lines CP-1 registers as opex_including_da cover
    # the whole cost base, so the cost of revenue joins them.
    nature = with_figures(
        regs,
        _PERIOD,
        {"opex_including_da": opex + cogs},
    )
    cells = _cells(_without(nature, "cogs"), _LABEL, exclude=True)
    assert cells["gross_profit"].value is None
    assert cells["gross_profit"].reason == "COMPONENT_MISSING"
    assert _values(cells, "revenue", "opex_total", "ebit") == (3008, -2310, 698)
    assert cells["ebit"].value == with_cogs["ebit"].value
    assert _values(cells, "da", "ebitda") == (-310, 1008)
    assert cells["adjusted_ebitda"].value is not None
    assert (
        cells["adjusted_ebitda"].value
        == _cells(regs, _LABEL, exclude=True)["adjusted_ebitda"].value
    )


def test_a_missing_opex_still_blanks_ebit_without_cogs() -> None:
    cells = _cells(_without(_without(example_registers(), "cogs"), "opex_including_da"), _LABEL)
    assert cells["ebit"].value is None
    assert cells["ebit"].reason == "COMPONENT_MISSING"
    assert cells["adjusted_ebitda"].value is None


def test_a_cogs_row_without_a_figure_still_blanks_ebit() -> None:
    regs = example_registers()
    unstated = replace(
        regs,
        accounts=tuple(
            replace(a, value=None) if a.metric_id == "cogs" and a.period_id == _PERIOD else a
            for a in regs.accounts
        ),
    )
    cells = _cells(unstated, _LABEL)
    assert cells["cogs"].reason != "NOT_SOURCED"
    assert cells["ebit"].value is None


@given(
    cogs=st.integers(min_value=-10_000, max_value=0),
    opex=st.integers(min_value=-10_000, max_value=0),
)
def test_the_cogs_and_nature_paths_agree_when_opex_is_consistent(cogs: int, opex: int) -> None:
    regs = with_figures(
        example_registers(), _PERIOD, {"cogs": Decimal(cogs), "opex_including_da": Decimal(opex)}
    )
    nature = with_figures(regs, _PERIOD, {"opex_including_da": Decimal(cogs + opex)})
    split = _cells(regs, _LABEL)
    whole = _cells(_without(nature, "cogs"), _LABEL)
    for key in ("ebit", "ebitda", "adjusted_ebitda", "adjusted_ebitdar"):
        assert whole[key].value == split[key].value, key
