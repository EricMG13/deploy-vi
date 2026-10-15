"""The assembled Model: columns, ranks, limitations and reconciliation faults."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

import pytest
from assemble_cases import _LTM, _PF, _cell, _line, _model, _nudged, _value, _with_cell
from credit_model_fixture import example_registers

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import (
    NO_PROJECTIONS,
    reconciliation_faults,
)
from rbotlib.model.frame import Cell, Column
from rbotlib.model.layout import (
    layout,
)


def test_the_worked_example_reconciles_with_no_faults() -> None:
    model = _model()
    assert reconciliation_faults(model) == ()
    assert model.currency == "USD"
    assert model.unit == "MILLIONS"
    assert model.rate_deck_id is None


def test_columns_run_history_then_the_pf_ltm() -> None:
    model = _model()
    assert [c.column_id for c in model.columns] == [
        *(f"Q:Q{q}_{y}" for y in (2024, 2025) for q in (1, 2, 3, 4)),
        "Q:Q1_2026",
        "Q:Q2_2026",
        "PYTD:H1_2025",
        "YTD:H1_2026",
        "FY:FY2023",
        "FY:FY2024",
        "FY:FY2025",
        _LTM,
        _PF,
    ]


def test_a_rank_with_one_facility_has_no_subtotal() -> None:
    model = _model()
    subtotals = [line.line_id for line in model.lines if line.line_id.startswith("rank:")]
    assert subtotals == ["rank:Senior secured", "rank:Senior unsecured"]
    regs = example_registers()
    regs = replace(regs, facilities=tuple(f for f in regs.facilities if f.facility_id != "sun32"))
    model = _model(regs=regs)
    subtotals = [line.line_id for line in model.lines if line.line_id.startswith("rank:")]
    assert subtotals == ["rank:Senior secured"]
    assert reconciliation_faults(model) == ()


def test_a_rank_subtotal_sums_its_facilities_on_every_column() -> None:
    model = _model()
    for column in model.columns:
        if column.kind in ("PROJECTED", "PF_LTM"):
            continue
        secured = sum(
            _value(model, key, column.column_id) for key in ("fac:tlb", "fac:ssn29", "fac:ssn31")
        )
        assert _value(model, "rank:Senior secured", column.column_id) == secured
    assert _value(model, "rank:Senior secured", _PF) == 2316 + 2000 + 1600
    assert _cell(model, "rank:Senior secured", _LTM).basis == "CALCULATED"


def test_a_model_has_no_projection_columns_until_the_projection_port() -> None:
    model = _model()
    assert all(column.kind != "PROJECTED" for column in model.columns)
    assert model.columns[-1].column_id == _PF
    assert model.limitations[0] == NO_PROJECTIONS
    assert model.rate_deck_id is None
    assert _line(model, "reference_rate").label == "Reference rate"
    for key in ("reference_rate", "interest_bearing_debt_opening", "wa_rate"):
        assert {cell.reason for cell in _line(model, key).cells} == {"NOT_APPLICABLE"}
    assert reconciliation_faults(model) == ()


def test_limitations_list_each_note_once() -> None:
    model = _model()
    notes = [text.split(": ")[0] for text in model.limitations]
    assert len(notes) == len(set(notes))
    for note in {cell.note for line in model.lines for cell in line.cells} - {None}:
        assert note in notes
    on = dict(text.split(": ", 1) for text in model.limitations)
    assert on["residual"].split(", ")[0] == "Q:Q1_2024"
    # On the PF-LTM only the roll-forward's residual, the LTM's, is shown.
    assert _PF in on["residual"].split(", ")
    residuals = [line.line_id for line in model.lines if _cell(model, line.line_id, _PF).note]
    assert residuals == ["debt_non_cash"]
    assert len(model.limitations) == len(notes)


@pytest.mark.parametrize("addback", ["addback:run_rate_cost_savings"])
def test_exclude_unrealised_drops_unrealised_addbacks_from_adjusted_ebitda_everywhere(
    addback: str,
) -> None:
    included = _model()
    excluded = _model(exclude_unrealised=True)
    assert _line(included, addback).kind == "ACCOUNT"
    assert _line(excluded, addback).kind == "MEMO"
    assert _line(excluded, addback).label == (
        "Add-back: Run-rate cost savings (unrealised), excluded if positive"
    )
    dropped = 0
    for column in excluded.columns:
        savings = _value(included, addback, column.column_id)
        dropped += savings != 0
        assert _value(excluded, "adjusted_ebitda", column.column_id) == (
            _value(included, "adjusted_ebitda", column.column_id) - savings
        )
    assert dropped > 0
    # The quarters' leverage reads the LTM ending them, dropped there too.
    with localcontext(CONTEXT):
        leverage = _value(excluded, "total_debt", "Q:Q2_2026") / Decimal(4089 - 40)
    assert _value(excluded, "metric:total_leverage_adjusted", "Q:Q2_2026") == leverage
    assert reconciliation_faults(excluded) == ()
    assert any(text.startswith("excluded: ") for text in excluded.limitations)


_BRIDGES = (
    ("ebitda", "FY:FY2024", "ebitda"),
    ("ebit", _LTM, "ebitda"),
    ("adjusted_ebitda", "YTD:H1_2026", "adjusted_ebitda"),
    ("addback:restructuring", _PF, "adjusted_ebitda"),
    ("pf:silverlake_ebitda", _PF, "adjusted_ebitda"),
    ("ffo", "Q:Q3_2025", "ffo"),
    ("lease_cash_not_in_ebitda", "FY:FY2025", "ffo"),
    ("cfo_adjusted", "PYTD:H1_2025", "cfo"),
    ("capex", "Q:Q2_2024", "fcf"),
    ("other_investing_financing", "FY:FY2023", "ncf"),
    ("fx_and_other_cash", "Q:Q4_2025", "cash"),
    ("liquidity", _PF, "liquidity"),
    ("rank:Senior secured", "Q:Q1_2026", "rank:Senior secured"),
    ("fac:sun32", "Q:Q1_2026", "rank:Senior unsecured"),
    ("total_debt", _PF, "total_debt"),
    ("pf:silverlake_notes", _PF, "rank:Senior secured"),
    ("pf:silverlake_cash", _PF, "liquidity"),
    ("fac:sub27", "FY:FY2025", "total_debt"),
    ("debt_opening", "Q:Q2_2026", "debt_rollforward"),
    ("rollforward:debt_raised_net", "Q:Q2_2026", "debt_rollforward"),
)


@pytest.mark.parametrize(("line_id", "column_id", "bridge"), _BRIDGES)
def test_each_bridge_reports_a_figure_that_breaks_it(
    line_id: str, column_id: str, bridge: str
) -> None:
    faults = reconciliation_faults(_nudged(_model(), line_id, column_id))
    assert f"{column_id}:{bridge}" in faults


def test_a_fault_names_only_the_bridges_the_figure_is_in() -> None:
    faults = reconciliation_faults(_nudged(_model(), "da", "Q:Q1_2024"))
    assert faults == ("Q:Q1_2024:ebitda",)
    faults = reconciliation_faults(_nudged(_model(), "fcf", "Q:Q1_2024"))
    assert faults == ("Q:Q1_2024:fcf", "Q:Q1_2024:ncf")


def test_a_bridge_with_a_line_without_a_figure_is_not_checked() -> None:
    model = _nudged(_model(), "ebitda", "FY:FY2024")
    unchecked = _with_cell(model, "ebit", "FY:FY2024", Cell(None, "NOT_STATED"))
    assert "FY:FY2024:ebitda" not in reconciliation_faults(unchecked)
    missing = _with_cell(
        model, "addback:restructuring", "FY:FY2024", Cell(None, "COMPONENT_MISSING")
    )
    assert "FY:FY2024:adjusted_ebitda" not in reconciliation_faults(missing)
    absent = _with_cell(_model(), "addback:restructuring", "FY:FY2024", Cell(None, "NOT_SOURCED"))
    assert reconciliation_faults(absent) == ("FY:FY2024:adjusted_ebitda",)
    total = _with_cell(model, "ebitda", "FY:FY2024", Cell(None, "NOT_STATED"))
    assert "FY:FY2024:ebitda" not in reconciliation_faults(total)


def test_unallocated_movements_are_not_applicable_on_history() -> None:
    model = _model()
    line = _line(model, "debt:unallocated")
    assert (line.label, line.kind, line.rank) == (
        "Unallocated movements (CP-CF)",
        "ACCOUNT",
        None,
    )
    ids = [line.line_id for line in model.lines]
    assert ids.index("debt:unallocated") + 1 == ids.index("total_debt")
    for column in model.columns:
        cell = _cell(model, "debt:unallocated", column.column_id)
        assert cell.reason == "NOT_APPLICABLE"
    assert reconciliation_faults(model) == ()


def test_pf_ltm_accounts_show_the_ltm_with_pf_rows_beneath() -> None:
    model = _model()
    for key in ("fac:ssn31", "cash_interest", "cash_closing", "fac:tlb"):
        assert _cell(model, key, _PF) == _cell(model, key, _LTM), key
    assert _value(model, "fac:ssn31", _PF) == 1000
    assert _value(model, "pf:silverlake_notes", _PF) == 600
    assert _value(model, "rank:Senior secured", _PF) == 2316 + 2000 + 1600
    assert _value(model, "total_debt", _PF) == (_value(model, "total_debt", _LTM) + 600)
    assert _value(model, "cash_closing", _PF) == 1000
    assert _value(model, "liquidity", _PF) == 950 + 2200
    assert _value(model, "less_cash", _PF) == -950
    assert _value(model, "adjusted_ebitda", _PF) == (_value(model, "adjusted_ebitda", _LTM) + 45)
    assert _value(model, "cash_interest", _PF) == -862
    assert reconciliation_faults(model) == ()


def test_business_units_that_do_not_sum_to_revenue_are_noted() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        segments=tuple(
            replace(s, revenue=Decimal(3000))
            if s.segment_id == "digital" and s.period_id == "Q1_2024"
            else s
            for s in regs.segments
        ),
    )
    model = _model(regs=regs)
    note = "business units do not sum to revenue"
    assert _cell(model, "revenue", "Q:Q1_2024").note == note
    assert _cell(model, "revenue", "FY:FY2024").note is None
    assert f"{note}: Q:Q1_2024" in model.limitations
    assert reconciliation_faults(model) == ()
    assert all(cell.note != note for cell in _line(_model(), "revenue").cells)
    rounded = replace(
        regs,
        segments=tuple(
            replace(s, revenue=Decimal("270.4"))
            if s.segment_id == "digital" and s.period_id == "Q1_2024"
            else s
            for s in example_registers().segments
        ),
    )
    assert _cell(_model(regs=rounded), "revenue", "Q:Q1_2024").note is None


def test_a_note_on_revenue_keeps_cp1s_own() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        accounts=tuple(
            replace(a, value=Decimal(5000))
            if a.metric_id == "revenue" and a.period_id == "H1_2026"
            else a
            for a in regs.accounts
        ),
        segments=tuple(
            replace(s, revenue=Decimal(1))
            if s.segment_id == "digital" and s.period_id == "Q1_2026"
            else s
            for s in regs.segments
        ),
    )
    cell = _cell(_model(regs=regs), "revenue", "YTD:H1_2026")
    assert cell.note == ("differs from CP-1 stated; business units do not sum to revenue")


def test_cells_a_column_has_not_say_why() -> None:
    model = _model()
    assert _cell(model, "wa_rate", _LTM).reason == "NOT_APPLICABLE"
    assert _cell(model, "reference_rate", "Q:Q1_2024").reason == "NOT_APPLICABLE"
    assert _cell(model, "pf:silverlake_cash", _LTM).reason == "NOT_APPLICABLE"
    assert _value(model, "pf:silverlake_cash", _PF) == -50
    regs = example_registers()
    regs = replace(regs, kpis=tuple(k for k in regs.kpis if k.period_id != "FY2023"))
    assert _cell(_model(regs=regs), "kpi:lv_occupancy", "FY:FY2023").reason == ("NOT_SOURCED")
    assert _cell(model, "rank:Senior secured", _LTM).value is not None


def test_a_rank_subtotal_without_any_facility_at_a_date_says_why() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        facilities=tuple(
            f
            for f in regs.facilities
            if not (f.facility_id in {"sun29", "sun32"} and f.period_id == "FY2023")
        ),
    )
    model = _model(regs=regs)
    assert _cell(model, "rank:Senior unsecured", "FY:FY2023").reason == "NOT_SOURCED"
    assert _value(model, "rank:Senior unsecured", "FY:FY2024") == 7100
    base = "BASE:2026"
    projected = Column(base, "PROJECTED", "FY26E", "FY2026", "2026", None, 365, "BASE")
    lines = layout(regs, (projected,), {base: {}}, False, None)
    subtotal = next(line for line in lines if line.line_id == "rank:Senior unsecured")
    assert subtotal.cells == (Cell(None, "NOT_PROJECTED"),)
