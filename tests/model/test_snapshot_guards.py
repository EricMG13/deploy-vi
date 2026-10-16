"""The MODEL step's tables, guarded (up-front review of the non-money
modules, 2026-10-11): totals that foot, spec vocabulary, fiscal-year
maturities, statuses and the no-LTM gap."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from credit_model_fixture import example_registers
from test_snapshot import _by, _context, _rows

from rbotlib.model.frame import Cell
from rbotlib.model.snapshot import Fig, build_tables, fig, fiscal_year_of, gap, slots

GAP = "\N{EM DASH}"


def test_senior_secured_plus_unsecured_foots_to_the_facilities() -> None:
    # M4: Finance leases, `Not stated` and the debt adjustments were in neither total.
    tables, _ = build_tables(_context())
    totals = _by(tables["snapshot.capital_structure_totals"], "line")
    every = sum((Decimal(r["outstanding"]) for r in _rows(tables["snapshot.capital_structure"])), 0)
    secured, unsecured = (
        Decimal(totals[k]["amount"]) for k in ("Senior secured debt", "Unsecured debt")
    )
    assert secured + unsecured == every
    assert unsecured == Decimal(3600 + 3500 + 1600 + 260 - 170)  # + finl and disc


def test_the_equity_basis_is_the_spec_vocabulary() -> None:
    # M3: `listed equity value` and `EV - net_debt` where spec §3.2 says `listed` / `ssim_multiple`.
    tables, _ = build_tables(_context())
    assert _by(tables["snapshot.capital_structure_totals"], "line")["Equity"]["basis"] == (
        "ssim_multiple"
    )


def test_figure_cells_carry_their_exact_value_and_reason() -> None:
    tables, _ = build_tables(_context())
    cell = tables["snapshot.capital_structure_totals"].rows[2][5]
    assert isinstance(cell, Fig) and cell.value is not None and cell.reason is None
    assert str(cell) == f"{cell.value:.2f}x" and len(str(cell.value)) > 6
    for row in tables["snapshot.ebitda_adjustments"].rows:
        amount = row[2]
        assert isinstance(amount, Fig) and amount.unit == "MONEY"
    none = gap()
    assert (str(none), none.value, none.reason) == ("\N{EM DASH}", None, "NOT_APPLICABLE")
    missing = fig(Cell(None, "NOT_SOURCED"), "MONEY")
    assert (missing.value, missing.reason, str(missing)) == (None, "NOT_SOURCED", "\N{EM DASH}")


@pytest.mark.parametrize(
    ("day", "year_end", "year"),
    [
        (date(2031, 6, 30), date(2025, 12, 31), 2031),
        (date(2031, 12, 31), date(2025, 12, 31), 2031),
        (date(2031, 6, 30), date(2025, 6, 30), 2031),
        (date(2031, 7, 1), date(2025, 6, 30), 2032),
        (date(2031, 2, 28), date(2024, 2, 29), 2031),  # a leap-day year end in a plain year
        (date(2031, 3, 1), date(2024, 2, 29), 2032),
        (date(2031, 7, 1), None, 2031),
    ],
)
def test_a_maturity_falls_in_the_fiscal_year_it_ends_in(
    day: date, year_end: date | None, year: int
) -> None:
    # M7: the wall used the calendar year; a June year end puts July 2031 in FY2032.
    assert fiscal_year_of(day, year_end) == year


def test_the_maturity_wall_names_a_facility_with_no_outstanding_amount() -> None:
    # M7: a null outstanding was skipped without a word.
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=None) if f.facility_id == "ssn29" else f for f in regs.facilities
    )
    _, limits = build_tables(_context(replace(regs, facilities=facilities)))
    assert [x for x in limits if x[0] == "MATURITY_AMOUNT_NOT_STATED"] == [
        ("MATURITY_AMOUNT_NOT_STATED", "ssn29: no outstanding amount at the snapshot date")
    ]


def test_an_add_back_not_stated_shows_its_status_not_unrealized() -> None:
    # M8: the Model excludes a `NOT_STATED` add-back; the table said UNREALIZED.
    regs = example_registers()
    addbacks = tuple(
        replace(b, realization_status="NOT_STATED")
        if b.addback_id == "run_rate_cost_savings"
        else b
        for b in regs.addbacks
    )
    tables, _ = build_tables(_context(replace(regs, addbacks=addbacks)))
    rows = _rows(tables["snapshot.ebitda_adjustments"])
    statuses = [r["realization_status"] for r in rows if "Run-rate" in r["line"]]
    assert statuses == ["NOT_STATED", "NOT_STATED"]


def test_without_an_ltm_the_empty_tables_are_noted() -> None:
    # M9: two tables are written below their minimum rows and said nothing.
    _, limits = build_tables(_context(replace(example_registers(), periods=())))
    assert [x[0] for x in limits if x[0] == "TABLES_EMPTY_NO_LTM"] == ["TABLES_EMPTY_NO_LTM"]


def test_snapshot_slots_and_the_no_ytd_fallback() -> None:
    ctx = _context()
    taken = {s: (c.column_id if c else None) for s, c in slots(ctx.model, ctx.view).items()}
    assert taken == {
        "FY-2": "FY:FY2023",
        "FY-1": "FY:FY2024",
        "FY": "FY:FY2025",
        "PYTD": "PYTD:H1_2025",
        "YTD": "YTD:H1_2026",
        "LTM": "PF:LTM_Q2_2026",
    }
    tables, _ = build_tables(ctx)
    rows = _by(tables["snapshot.financial_columns"], "slot")
    assert rows["LTM"] == {
        "slot": "LTM",
        "column_id": "PF:LTM_Q2_2026",
        "label": "PF-LTM",
        "period_id": "LTM_Q2_2026",
        "kind": "PF_LTM",
        "end_date": "2026-06-30",
    }
    regs = example_registers()
    years = replace(regs, periods=tuple(p for p in regs.periods if p.period_type == "FY"))
    kept = {p.period_id for p in years.periods}  # a row naming another period is refused
    names = ("accounts", "addbacks", "segments", "kpis", "facilities")
    only: dict[str, Any] = {
        name: tuple(r for r in getattr(regs, name) if r.period_id in kept) for name in names
    }
    fallback = _context(replace(years, pro_forma=(), **only))
    rows = _by(build_tables(fallback)[0]["snapshot.financial_columns"], "slot")
    assert [rows[s]["column_id"] for s in ("FY-2", "FY-1", "FY", "PYTD", "YTD")] == [
        "FY:FY2023",
        "FY:FY2024",
        "FY:FY2025",
        GAP,
        GAP,
    ]
    assert rows["PYTD"]["label"] == "n/a"
    assert rows["LTM"]["column_id"] == "LTM:FY2025"


def test_the_pf_cover_in_both_total_columns_is_ssim_cover() -> None:
    ctx = _context()
    row = _by(build_tables(ctx)[0]["snapshot.capital_structure_totals"], "line")[
        "PF interest cover"
    ]
    cover = ctx.view.item("pf_interest_cover").cell
    for key in ("structuring_multiple_x", "ssim_multiple_x"):
        shown = row[key]
        assert isinstance(shown, Fig)
        assert (shown.value, shown.reason) == (cover.value, cover.reason)
