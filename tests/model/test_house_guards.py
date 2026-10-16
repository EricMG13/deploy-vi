"""The house view's guards (up-front money review, 2026-10-11): each test
starts from the reviewer's probe input on the caos Example Gaming Co.
registers and fails on the code before the fix."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.house import HouseView, cell, house_view, with_debt_like_lines
from rbotlib.model.house_inputs import (
    BriefFields,
    DebtLikeItem,
    EquityValue,
    HouseInputs,
    effective_registers,
)
from rbotlib.model.registers import Cp1Registers


def _inputs(debt_like: tuple[DebtLikeItem, ...] = ()) -> HouseInputs:
    brief = BriefFields("R", Decimal("8.5"), False, frozenset())
    return HouseInputs({}, None, (), debt_like, brief)


def _built(
    regs: Cp1Registers | None = None, inputs: HouseInputs | None = None
) -> tuple[CreditModel, HouseView]:
    inputs = inputs or _inputs()
    regs = effective_registers(regs or example_registers(), inputs.assessments)
    model = with_debt_like_lines(
        credit_model(ModelInputs(regs, exclude_unrealised=True)), regs, inputs.debt_like
    )
    return model, house_view(model, regs, inputs)


def _without_cash_interest(regs: Cp1Registers) -> Cp1Registers:
    accounts = tuple(a for a in regs.accounts if a.metric_id != "cash_interest_paid")
    return replace(regs, accounts=accounts)


def test_pf_interest_is_missing_when_the_ltm_cash_interest_is_not_sourced() -> None:
    # Probe p1_interest: no cash_interest_paid rows, the PF row -42 kept.
    model, view = _built(_without_cash_interest(example_registers()))
    interest = view.item("pf_interest").cell
    assert (interest.value, interest.reason) == (None, "COMPONENT_MISSING")
    assert interest.note is not None and "LTM cash interest not sourced" in interest.note
    cover = view.item("pf_interest_cover").cell
    assert (cover.value, cover.reason) == (None, "COMPONENT_MISSING")
    assert view.column is not None
    metric = cell(model, "metric:interest_coverage_adjusted", view.column)
    assert metric.reason == "COMPONENT_MISSING"


_INTEREST = st.one_of(st.none(), st.integers(min_value=-2000, max_value=300).map(Decimal))
_PF_ROWS = st.lists(st.integers(min_value=-300, max_value=300).map(Decimal), max_size=2)


def _interest_registers(ltm: Decimal | None, rows: list[Decimal]) -> Cp1Registers:
    """The example with computed LTM cash interest redrawn (FY + YTD - PYTD, or absent)
    and its cash interest PF rows replaced by up to two drawn rows."""
    regs = example_registers()
    if ltm is None:
        accounts = _without_cash_interest(regs).accounts
    else:
        accounts = tuple(
            replace(a, value=ltm if a.period_id == "FY2025" else Decimal(0))
            if a.metric_id == "cash_interest_paid"
            else a
            for a in regs.accounts
        )
    template = next(a for a in regs.pro_forma if a.metric_id == "cash_interest_paid")
    others = tuple(a for a in regs.pro_forma if a.metric_id != "cash_interest_paid")
    drawn = tuple(
        replace(template, adjustment_id=f"interest_{n}", value=value)
        for n, value in enumerate(rows)
    )
    return replace(regs, accounts=accounts, pro_forma=others + drawn)


@settings(max_examples=60, deadline=None)
@given(ltm=_INTEREST, rows=_PF_ROWS)
def test_pf_interest_cover_is_the_models_adjusted_interest_cover_on_the_pf_ltm(
    ltm: Decimal | None, rows: list[Decimal]
) -> None:
    model, view = _built(_interest_registers(ltm, rows))
    assert view.column is not None and view.column.kind == "PF_LTM"
    cover = view.item("pf_interest_cover").cell
    metric = cell(model, "metric:interest_coverage_adjusted", view.column)
    assert (cover.value, cover.reason) == (metric.value, metric.reason)


def _codes(view: HouseView) -> dict[str, str]:
    return dict(view.limitations)


def test_pf_rows_on_another_period_are_reported_not_applied() -> None:
    # Probe p6_pfperiod A: the four PF rows keyed to H1_2026.
    regs = example_registers()
    regs = replace(regs, pro_forma=tuple(replace(a, period_id="H1_2026") for a in regs.pro_forma))
    _, view = _built(regs)
    codes = _codes(view)
    assert "PF_LTM_EQUALS_LTM" not in codes
    assert "H1_2026" in codes["PF_ROWS_NOT_APPLIED"]
    _, plain = _built(replace(regs, pro_forma=()))
    assert "PF_ROWS_NOT_APPLIED" not in _codes(plain)
    assert "PF_LTM_EQUALS_LTM" in _codes(plain)


def _item(name: str, period: str, amount: int = 120) -> DebtLikeItem:
    return DebtLikeItem(
        name, Decimal(amount), "USD", "MILLIONS", period, "Debt-like", "unfunded", "[C1]"
    )


def test_a_debt_like_item_counts_on_the_column_ending_on_its_balance_date() -> None:
    # Probe p2_debtlike A and B: keyed to Q2_2026 or H1_2026, both ending 2026-06-30.
    for period in ("Q2_2026", "H1_2026"):
        model, view = _built(inputs=_inputs(debt_like=(_item("Pension deficit", period),)))
        assert view.item("adjusted_debt").cell.value == 14706 + 120
        assert view.column is not None
        memo = cell(model, "debt_like:pension_deficit", view.column)
        assert memo.value == 120


def test_a_debt_like_item_off_the_snapshot_date_is_noted() -> None:
    _, view = _built(inputs=_inputs(debt_like=(_item("Pension deficit", "FY2025"),)))
    assert view.item("adjusted_debt").cell.value == 14706
    assert "Pension deficit" in _codes(view)["DEBT_LIKE_NOT_ON_SNAPSHOT"]


def test_one_memo_line_per_debt_like_item_with_each_period_on_its_columns() -> None:
    # Probe p2_debtlike C: the same item at FY2025 and at the LTM.
    items = (_item("Pension deficit", "FY2025", 100), _item("Pension deficit", "LTM_Q2_2026"))
    model, view = _built(inputs=_inputs(debt_like=items))
    ids = [line.line_id for line in model.lines]
    assert len(ids) == len(set(ids))
    assert ids.count("debt_like:pension_deficit") == 1
    by_id = {c.column_id: c for c in model.columns}
    assert cell(model, "debt_like:pension_deficit", by_id["FY:FY2025"]).value == 100
    assert cell(model, "debt_like:pension_deficit", by_id["LTM:LTM_Q2_2026"]).value == 120
    assert view.item("adjusted_debt").components == ("total_debt", "debt_like:pension_deficit")


def test_ev_from_the_multiple_needs_positive_ssim_ebitda() -> None:
    # Probe p5_ev: a PF adjusted_ebitda row of -5,000 makes SSIM EBITDA -951.
    regs = example_registers()
    regs = replace(
        regs,
        pro_forma=tuple(
            replace(a, value=Decimal(-5000)) if a.metric_id == "adjusted_ebitda" else a
            for a in regs.pro_forma
        ),
    )
    _, view = _built(regs)
    ev = view.item("ev").cell
    assert (ev.value, ev.reason) == (None, "NOT_APPLICABLE")
    assert (view.equity.value, view.equity.reason) == (None, "NOT_APPLICABLE")
    assert "at or below zero" in _codes(view)["EV_NOT_APPLICABLE"]


def test_a_negative_excluded_add_back_stays_in_ssim_so_ssim_never_exceeds_structuring() -> None:
    # F11 (was probe p11_neg_addback): run_rate_cost_savings at -40 stays in SSIM
    # EBITDA, so Structuring EBITDA (every add-back in) equals it and no
    # SSIM-above-Structuring signal is needed.
    regs = example_registers()
    regs = replace(
        regs,
        addbacks=tuple(
            replace(b, value=-(b.value or Decimal(0)))
            if b.addback_id == "run_rate_cost_savings"
            else b
            for b in regs.addbacks
        ),
    )
    _, view = _built(regs)
    assert view.column is not None
    everything = cell(credit_model(ModelInputs(regs)), "adjusted_ebitda", view.column)
    ssim, structuring = view.item("ssim_ebitda").cell, view.item("structuring_ebitda").cell
    assert ssim.value == structuring.value == everything.value
    assert view.item("structuring_ebitda").components == ("adjusted_ebitda",)
    assert "SSIM_ABOVE_STRUCTURING" not in _codes(view)


def test_a_snapshot_column_other_than_twelve_months_gives_no_multiple() -> None:
    # Probe p8_stub's 181-day LTM, set on the example's PF-LTM column.
    regs = example_registers()
    model, _ = _built(regs)
    columns = tuple(replace(c, days=181) if c.kind == "PF_LTM" else c for c in model.columns)
    view = house_view(replace(model, columns=columns), regs, _inputs())
    for key in ("structuring_multiple", "ssim_multiple", "adjusted_leverage", "ev"):
        found = view.item(key).cell
        assert (found.value, found.reason) == (None, "NOT_APPLICABLE"), key
        if key != "ev":
            assert found.note == "the PF-LTM column spans 181 days, not twelve months"
    assert view.item("ssim_ebitda").cell.value == 4094
    assert view.equity.value is None and view.equity.reason == "NOT_APPLICABLE"
    assert view.equity.note == "the PF-LTM column spans 181 days: no debt multiple"
    assert "181 days" in _codes(view)["SNAPSHOT_NOT_TWELVE_MONTHS"]
    assert "SNAPSHOT_NOT_TWELVE_MONTHS" not in _codes(_built()[1])


def test_the_interest_property_varies_the_computed_ltm_not_only_its_stated_memo() -> None:
    _, view = _built(_interest_registers(Decimal(-100), []))
    assert view.item("pf_interest").cell.value == 100


@pytest.mark.parametrize(("ebitda", "ev"), [("0", None), ("0.5", Decimal("4.25"))])
def test_ev_uses_the_exact_zero_boundary(ebitda: str, ev: Decimal | None) -> None:
    regs = example_registers()
    pro_forma = tuple(
        replace(a, value=Decimal(ebitda) - 4049) if a.metric_id == "adjusted_ebitda" else a
        for a in regs.pro_forma
    )
    _, view = _built(replace(regs, pro_forma=pro_forma))
    cell = view.item("ev").cell
    assert cell.value == ev
    if ev is None:
        why = "SSIM EBITDA at or below zero: no EV from the SSIM EV multiple"
        assert cell.reason == "NOT_APPLICABLE" and cell.note == why
        assert _codes(view)["EV_NOT_APPLICABLE"] == why
    else:
        assert cell.reason is None and "EV_NOT_APPLICABLE" not in _codes(view)


def test_all_debt_like_items_off_the_snapshot_date_are_named() -> None:
    items = (_item("Pension deficit", "FY2025"), _item("Environmental provisions", "FY2024"))
    _, view = _built(inputs=_inputs(debt_like=items))
    assert _codes(view)["DEBT_LIKE_NOT_ON_SNAPSHOT"] == (
        "Pension deficit (FY2025), Environmental provisions (FY2024): not at the "
        "PF-LTM date 2026-06-30; adjusted debt leaves out"
    )


def test_all_unapplied_pf_periods_are_named() -> None:
    regs = example_registers()
    pro_forma = tuple(
        replace(a, period_id="FY2025" if n == 0 else "H1_2026")
        for n, a in enumerate(regs.pro_forma)
    )
    _, view = _built(replace(regs, pro_forma=pro_forma))
    assert _codes(view)["PF_ROWS_NOT_APPLIED"] == (
        "PF rows for FY2025, H1_2026 apply to no LTM column (LTM Q2 26 is used)"
    )


@pytest.mark.parametrize(("days", "annual"), [(363, False), (364, True), (371, True), (372, False)])
def test_snapshot_multiples_accept_52_and_53_week_years_with_exact_boundaries(
    days: int, annual: bool
) -> None:
    regs = example_registers()
    model, _ = _built(regs)
    columns = tuple(replace(c, days=days) if c.kind == "PF_LTM" else c for c in model.columns)
    view = house_view(replace(model, columns=columns), regs, _inputs())
    found = view.item("ssim_multiple").cell
    assert (found.value is not None) is annual
    assert ("SNAPSHOT_NOT_TWELVE_MONTHS" not in _codes(view)) is annual


def test_listed_equity_and_ev_do_not_require_annual_ebitda() -> None:
    regs = example_registers()
    listed = EquityValue(Decimal(20000), "2026-10-02", "USD", "MILLIONS", "[C1]")
    inputs = replace(_inputs(), equity=listed)
    model, before = _built(regs, inputs)
    columns = tuple(replace(c, days=181) if c.kind == "PF_LTM" else c for c in model.columns)
    view = house_view(replace(model, columns=columns), regs, inputs)
    assert view.equity.value == 20000 and view.equity.reason is None
    assert view.item("ev").cell.value == before.item("ev").cell.value


def test_a_debt_like_item_cannot_be_placed_on_an_unknown_balance_date() -> None:
    regs = example_registers()
    periods = tuple(
        replace(p, end_date=None) if p.period_id == "FY2025" else p for p in regs.periods
    )
    regs = replace(regs, periods=periods)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    item = _item("Pension deficit", "FY2025")
    model = with_debt_like_lines(model, regs, (item,))
    column = next(c for c in model.columns if c.column_id == "FY:FY2025")
    assert column.end_date is None
    found = cell(model, "debt_like:pension_deficit", column)
    assert found.value is None and found.reason == "NOT_SOURCED"
