"""The LTM spans twelve months or is not built (up-front money review I5,
2026-10-11; a caos gap): the reviewer's stub-year and mislabelled-interim
probes on the caos Example Gaming Co. registers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import date, timedelta

import pytest
from credit_model_fixture import example_registers

from rbotlib.model._cells import UNSPANNED
from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.registers import AccountRow, Cp1Registers, PeriodRow

DROPPED = ("LTM_Q2_2026", "H1_2026", "H1_2025")


def _stub_year() -> Cp1Registers:
    """Probe p8_stub: a six-month transition period registered as FY2026T."""
    regs = example_registers()

    def moved(rows: tuple[AccountRow, ...]) -> tuple[AccountRow, ...]:
        return tuple(
            replace(a, period_id="FY2026T") if a.period_id == "H1_2026" else a
            for a in rows
            if a.period_id != "LTM_Q2_2026"
        )

    stub = next(p for p in regs.periods if p.period_id == "H1_2026")
    periods = tuple(p for p in regs.periods if p.period_id not in DROPPED)
    periods += (replace(stub, period_id="FY2026T", period_type="FY", fiscal_quarter=None),)
    return replace(
        regs,
        periods=periods,
        accounts=moved(regs.accounts),
        addbacks=tuple(
            replace(b, period_id="FY2026T") if b.period_id == "H1_2026" else b
            for b in regs.addbacks
            if b.period_id != "LTM_Q2_2026"
        ),
        segments=(),
        kpis=(),
        facilities=tuple(
            replace(f, period_id="FY2026T") if f.period_id == "H1_2026" else f
            for f in regs.facilities
        ),
        pro_forma=(),
    )


def _nine_months_as_pytd() -> Cp1Registers:
    """Probe p7b_ltm: a 9M 2025 YTD labelled fiscal quarter 2, H1 2025's
    label dropped, and no CP-1 LTM row."""
    regs = example_registers()
    nine = PeriodRow(
        "M9_2025", "2025", "2", "YTD", "2025-01-01", "2025-09-30", 273, "USD", "MILLIONS", ()
    )
    periods = tuple(
        replace(p, fiscal_quarter=None) if p.period_id == "H1_2025" else p
        for p in regs.periods
        if p.period_id != "LTM_Q2_2026"
    )
    flows = {a.metric_id for a in regs.accounts if a.period_id == "Q3_2025"}
    extra = []
    for a in regs.accounts:
        h1 = next(
            (b for b in regs.accounts if (b.metric_id, b.period_id) == (a.metric_id, "H1_2025")),
            None,
        )
        if a.period_id == "Q3_2025" and a.metric_id in flows and h1 is not None:
            if h1.value is not None and a.value is not None:
                extra.append(replace(a, period_id="M9_2025", value=h1.value + a.value))
    return replace(
        regs,
        periods=(*periods, nine),
        accounts=tuple(a for a in regs.accounts if a.period_id != "LTM_Q2_2026") + tuple(extra),
        addbacks=tuple(b for b in regs.addbacks if b.period_id != "LTM_Q2_2026"),
        segments=tuple(g for g in regs.segments if g.period_id != "LTM_Q2_2026"),
        pro_forma=(),
    )


@pytest.mark.parametrize("build", [_stub_year, _nine_months_as_pytd])
def test_a_short_ltm_is_not_built(build: Callable[[], Cp1Registers]) -> None:
    model = credit_model(ModelInputs(build(), exclude_unrealised=True))
    ltm = next(c for c in model.columns if c.kind == "LTM")
    index = model.columns.index(ltm)
    cells = {x.line_id: x.cells[index] for x in model.lines}
    assert (cells["adjusted_ebitda"].value, cells["adjusted_ebitda"].reason) == (
        None,
        "COMPONENT_MISSING",
    )
    revenue = cells["revenue"]
    assert (revenue.value, revenue.reason, revenue.note) == (None, "COMPONENT_MISSING", UNSPANNED)


def test_the_example_ltm_spans_twelve_months_and_is_built() -> None:
    model = credit_model(ModelInputs(example_registers(), exclude_unrealised=True))
    ltm = next(c for c in model.columns if c.kind == "LTM")
    index = model.columns.index(ltm)
    assert next(x for x in model.lines if x.line_id == "adjusted_ebitda").cells[index].value


@pytest.mark.parametrize("days", [364, 371])
def test_a_fiscal_year_of_52_or_53_weeks_builds_the_ltm(days: int) -> None:
    regs = example_registers()
    end = date(2025, 12, 31)
    fy = next(p for p in regs.periods if p.period_id == "FY2025")
    fy = replace(fy, start_date=(end - timedelta(days=days - 1)).isoformat(), day_count=days)
    only = replace(regs, periods=(fy,), pro_forma=())
    model = credit_model(ModelInputs(only, exclude_unrealised=True))
    column = next(c for c in model.columns if c.kind == "LTM")
    index = model.columns.index(column)
    revenue = next(x for x in model.lines if x.line_id == "revenue").cells[index]
    assert column.days == days
    assert revenue.value == 11519 and revenue.reason is None
