"""The layout on the worked example, read straight from the metric frame (the
way `assemble` calls it): bands in order, one cell per column, rank
subtotals, the unallocated line, terms and the port additions."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

from credit_model_fixture import example_registers

from rbotlib.model._cells import CONTEXT
from rbotlib.model.frame import Column
from rbotlib.model.history import account_frame, historical_columns, ltm_frames
from rbotlib.model.inputs import PF_METRICS
from rbotlib.model.layout import _PF_PLACES, BANDS, UNALLOCATED, Line, facility_terms, layout
from rbotlib.model.metrics import metric_frame
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.statements import pro_forma_column, statement_frame

PF = "PF:LTM_Q2_2026"


def _lines(
    exclude: bool = False, regs: Cp1Registers | None = None
) -> tuple[tuple[Column, ...], dict[str, Line]]:
    regs = regs or example_registers()
    historical = historical_columns(regs)
    frame = dict(statement_frame(account_frame(regs, historical), historical, regs, exclude))
    ltm = next(c for c in historical if c.kind == "LTM")
    pf = pro_forma_column(regs, ltm, frame)
    assert pf is not None
    columns = (*historical, pf[0])
    frame.update(pf[1])
    quarters = tuple(c for c in historical if c.kind == "QUARTER")
    ltm_ending = statement_frame(ltm_frames(regs, historical), quarters, regs, exclude)
    lines = layout(regs, columns, metric_frame(columns, frame, ltm_ending), exclude, None)
    assert all(len(line.cells) == len(columns) for line in lines)
    runs = [b for n, b in enumerate(x.band for x in lines) if n == 0 or b != lines[n - 1].band]
    assert runs == list(BANDS)  # every band, each once, in the layout's order
    return columns, {line.line_id: line for line in lines}


def _on(columns: tuple[Column, ...], line: Line, column_id: str) -> Decimal | None:
    return line.cells[[c.column_id for c in columns].index(column_id)].value


def test_the_port_additions_sit_in_their_bands() -> None:
    columns, lines = _lines()
    ids = list(lines)
    assert lines["gross_profit_growth"].band == BANDS[2]
    assert ids.index("secured_debt") == ids.index("total_debt") + 1
    assert lines["secured_debt"].kind == "MEMO"
    assert _on(columns, lines["revenue"], "FY:FY2025") == 11519


def test_a_rank_subtotal_sums_its_facilities_and_unallocated_is_history_free() -> None:
    columns, lines = _lines()
    secured = [x for x in lines.values() if x.rank == "Senior secured" and x.kind == "ACCOUNT"]
    values = [_on(columns, x, "FY:FY2025") for x in secured]
    total = sum((v for v in values if v is not None), Decimal(0))
    assert _on(columns, lines["rank:Senior secured"], "FY:FY2025") == total
    assert {c.reason for c in lines[UNALLOCATED].cells} == {"NOT_APPLICABLE"}
    regs = example_registers()
    tlb = next(f for f in regs.facilities if f.facility_id == "tlb" and f.period_id == "Q2_2026")
    assert lines["fac:tlb"].terms == facility_terms(tlb)


def test_a_rank_subtotal_is_exact_past_28_digits() -> None:
    big = Decimal("512345678901234567.0123456789")  # the largest the reader takes
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=big) if f.facility_id in {"tlb", "ssn29"} else f
        for f in regs.facilities
    )
    columns, lines = _lines(regs=replace(regs, facilities=facilities))
    secured = [x for x in lines.values() if x.rank == "Senior secured" and x.kind == "ACCOUNT"]
    values = [_on(columns, x, "FY:FY2025") for x in secured]
    with localcontext(CONTEXT):
        total = sum((v for v in values if v is not None), Decimal(0))
    assert _on(columns, lines["rank:Senior secured"], "FY:FY2025") == total


def test_excluded_add_backs_are_memos() -> None:
    _, lines = _lines(exclude=True)
    assert lines["addback:run_rate_cost_savings"].kind == "MEMO"
    assert lines["addback:restructuring"].kind == "ACCOUNT"


def test_the_pro_forma_vocabulary_of_inputs_is_the_layouts() -> None:
    assert PF_METRICS == frozenset(_PF_PLACES)
