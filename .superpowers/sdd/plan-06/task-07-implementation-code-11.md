# Task06.7 exact replay file 11

Source: `tests/model/test_rank_absence.py`; complete executed bytes, SHA256 `d37d668a8b4dd5218feb147de43b634cb2932be1a51b4b3177297bce62e64cc0`, 1972 bytes, 48 LF. Baseline1094a76; final source tree/proof is recorded separately. This ordinary whole file receives no cap exemption.

```python
"""No facility observations is a gap; populated opposite-rank absence remains zero."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest
from test_snapshot import _context

from rbotlib.model.debt import SECURED_RANKS
from rbotlib.model.frame import Cell
from rbotlib.model.house import secured
from rbotlib.model.snapshot import _unsecured, capital_structure_totals


def test_empty_position_observations_produce_missing_rank_amounts() -> None:
    view = replace(_context().view, positions=())
    assert secured(view) == Cell(None, "NOT_SOURCED")
    assert _unsecured(view) == Cell(None, "NOT_SOURCED")


@pytest.mark.parametrize("only_secured", [True, False])
def test_populated_single_rank_preserves_documented_opposite_rank_zero(only_secured: bool) -> None:
    view = _context().view
    positions = tuple(p for p in view.positions if (p.line.rank in SECURED_RANKS) == only_secured)
    assert positions
    view = replace(view, positions=positions)
    opposite = _unsecured(view) if only_secured else secured(view)
    assert opposite.value == Decimal(0) and opposite.reason is None


def test_observed_zero_and_missing_carrying_amount_are_distinct() -> None:
    view = _context().view
    position = next(p for p in view.positions if p.line.rank in SECURED_RANKS)
    known_zero = replace(
        position, outstanding=Cell(Decimal(0), sources=position.outstanding.sources)
    )
    assert secured(replace(view, positions=(known_zero,))).value == Decimal(0)
    missing = replace(position, outstanding=Cell(None, "COMPONENT_MISSING"))
    result = secured(replace(view, positions=(missing,)))
    assert result.value is None and result.reason == "COMPONENT_MISSING"


def test_no_ltm_capital_totals_still_have_no_rows() -> None:
    context = _context()
    context = replace(context, view=replace(context.view, column=None, positions=()))
    assert capital_structure_totals(context).rows == []
```

Not verified: independent acceptance, whole06.16 branch gates, later06, live/provider/platform/crash behavior.
