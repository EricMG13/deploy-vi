"""A segment any of whose rows says `CORPORATE_ELIMINATION` is corporate on
every column (up-front money review M4, 2026-10-11: kills
`assemble.credit_model` mutants 63, 64 and 75, once recorded as equivalent)."""

from __future__ import annotations

from dataclasses import replace

from credit_model_fixture import example_registers

from rbotlib.model.assemble import ModelInputs, credit_model


def test_a_segment_corporate_in_any_row_has_no_growth() -> None:
    # Probe m_corporate: the corporate segment's LTM row says OPERATING_SEGMENT.
    regs = example_registers()
    segments = tuple(
        replace(s, segment_type="OPERATING_SEGMENT")
        if (s.segment_id, s.period_id) == ("corporate_eliminations", "LTM_Q2_2026")
        else s
        for s in regs.segments
    )
    model = credit_model(ModelInputs(replace(regs, segments=segments), exclude_unrealised=True))
    line = next(x for x in model.lines if x.line_id == "bu_growth:corporate_eliminations")
    fy = [c.column_id for c in model.columns].index("FY:FY2025")
    assert (line.cells[fy].value, line.cells[fy].reason) == (None, "NOT_APPLICABLE")
