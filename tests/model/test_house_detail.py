"""The house view in detail: what each item states, the cells' bases and
sources, the limitations' wording and exactness past 28 digits (the mutation
gate's findings on `rbotlib.model.house`)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers

from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.frame import Cell, SourceRef
from rbotlib.model.house import (
    HouseView,
    Position,
    cumulative,
    house_view,
    ratio,
    with_debt_like_lines,
)
from rbotlib.model.house_inputs import (
    BriefFields,
    DebtLikeItem,
    EquityValue,
    HouseInputs,
    debt_like_key,
)
from rbotlib.model.registers import Cp1Registers

PF = "PF:LTM_Q2_2026"
A, B = SourceRef("S1", "p.1", "1"), SourceRef("S2", "p.2", "2")


def _inputs(equity: EquityValue | None = None, multiple: str | None = None) -> HouseInputs:
    brief = BriefFields("R", None if multiple is None else Decimal(multiple), False, frozenset())
    return HouseInputs({}, equity, (), (), brief)


def _view(regs: Cp1Registers | None = None, inputs: HouseInputs | None = None) -> HouseView:
    regs = regs or example_registers()
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    return house_view(model, regs, inputs or _inputs())


def test_every_item_states_its_unit_formula_components_and_basis() -> None:
    view = _view()
    assert [(i.key, i.unit, i.formula, i.components, i.cell.basis) for i in view.items] == [
        ("structuring_ebitda", "MONEY", "adjusted_ebitda + excluded (unrealized) add-backs",
         ("adjusted_ebitda", "addback:run_rate_cost_savings"), "CALCULATED"),
        ("ssim_ebitda", "MONEY", "adjusted_ebitda, unrealized add-backs excluded",
         ("adjusted_ebitda",), "PRO_FORMA"),
        ("pf_interest", "MONEY", "-(cash_interest + its PF rows)", ("cash_interest",),
         "CALCULATED"),
        ("pf_interest_cover", "MULTIPLE", "SSIM EBITDA / PF interest",
         ("adjusted_ebitda", "cash_interest"), "CALCULATED"),
        ("structuring_multiple", "MULTIPLE", "total_debt / Structuring EBITDA",
         ("total_debt", "adjusted_ebitda", "addback:run_rate_cost_savings"), "CALCULATED"),
        ("ssim_multiple", "MULTIPLE", "total_debt / SSIM EBITDA",
         ("total_debt", "adjusted_ebitda"), "CALCULATED"),
        ("ev", "MONEY", "listed equity value + net_debt, else SSIM EV multiple x SSIM EBITDA",
         ("net_debt", "adjusted_ebitda"), None),
        ("adjusted_debt", "MONEY", "total_debt + CP-1D debt-like items", ("total_debt",),
         "CALCULATED"),
        ("adjusted_leverage", "MULTIPLE", "Adjusted debt / SSIM EBITDA",
         ("total_debt", "adjusted_ebitda"), "CALCULATED"),
    ]  # fmt: skip
    ev = view.item("ev").cell
    why = "no listed equity value and no SSIM EV multiple (or no SSIM EBITDA)"
    assert (ev.reason, ev.note, view.equity.note) == ("NOT_SOURCED", why, why)


def test_a_ratio_is_exact_calculated_and_keeps_both_sources() -> None:
    half = ratio(Cell(Decimal(1), sources=(A,)), Cell(Decimal("0.5"), sources=(B,)))
    assert (half.value, half.basis, half.sources) == (Decimal(2), "CALCULATED", (A, B))


def test_cumulative_debt_is_exact_past_28_digits() -> None:
    view = _view()
    line = next(p.line for p in view.positions if p.facility_id == "tlb")
    big = (Position("a", line, Cell(Decimal(10) ** 30)), Position("b", line, Cell(Decimal(1))))
    assert cumulative(replace(view, positions=big), "Senior secured").value == 10**30 + 1


def test_a_facility_with_no_balance_at_the_date_is_out_unless_pf_rows_add_it() -> None:
    regs = example_registers()
    tlb = next(f for f in regs.facilities if f.facility_id == "tlb" and f.period_id == "FY2024")
    notes = next(a for a in regs.pro_forma if a.metric_id == "facility:ssn31")
    regs = replace(
        regs,
        facilities=(
            *regs.facilities,
            replace(tlb, facility_id="old"),
            replace(tlb, facility_id="add"),
        ),
        pro_forma=(*regs.pro_forma, replace(notes, adjustment_id="a1", metric_id="facility:add")),
    )
    outstanding = {p.facility_id: p.outstanding.value for p in _view(regs).positions}
    assert "old" not in outstanding
    assert outstanding["add"] == 600


def test_an_excluded_add_back_without_a_row_on_the_column_is_no_component() -> None:
    regs = example_registers()
    old = next(b for b in regs.addbacks if b.addback_id == "run_rate_cost_savings")
    regs = replace(regs, addbacks=(*regs.addbacks, replace(old, addback_id="synergies")))
    structuring = _view(regs).item("structuring_ebitda")
    assert structuring.components == ("adjusted_ebitda", "addback:run_rate_cost_savings")
    assert structuring.cell.value == 4134


def test_pf_interest_drops_the_sign_note_of_the_interest_it_negates() -> None:
    regs = example_registers()
    positive = tuple(
        replace(a, value=abs(a.value)) if a.metric_id == "cash_interest_paid" and a.value else a
        for a in regs.accounts
    )
    view = _view(replace(regs, accounts=positive, pro_forma=()))
    interest = view.item("pf_interest").cell
    assert (interest.value, interest.note) == (Decimal(862), None)


def test_a_debt_like_line_follows_the_debt_band_with_its_cited_amount() -> None:
    item = DebtLikeItem(" Pension (deficit)! ", Decimal(120), "USD", "MILLIONS", "LTM_Q2_2026",
                        "Debt-like", "unfunded", "[C1]")  # fmt: skip
    assert debt_like_key(item) == "debt_like:pension_deficit"
    regs = example_registers()
    model = with_debt_like_lines(credit_model(ModelInputs(regs)), regs, (item,))
    ids = [line.line_id for line in model.lines]
    at = ids.index("debt_like:pension_deficit")
    assert ids[at - 1] == "lease_adjusted_net_debt"
    assert model.lines[at + 1].band != model.lines[at].band
    on_pf = model.lines[at].cells[[c.column_id for c in model.columns].index(PF)]
    assert (on_pf.basis, on_pf.sources) == ("REPORTED", (SourceRef("[C1]", "", "120"),))


def test_listed_equity_is_reported_cited_and_exact() -> None:
    cap = Decimal("1234567890123456789012345.6789")
    listed = _view(inputs=_inputs(EquityValue(cap, "2026-10-02", "USD", "THOUSANDS", "[C9]")))
    assert listed.equity.value == Decimal("1234567890123456789012.3456789")
    assert listed.equity.basis == "REPORTED"
    assert listed.equity.sources == (SourceRef("[C9]", "", f"{cap:f}"),)
    assert listed.item("ev").formula == "listed equity value + net_debt"
    euro = _view(inputs=_inputs(EquityValue(cap, "2026-10-02", "EUR", "THOUSANDS", "[C9]")))
    assert euro.item("ev").cell.note == "equity value in EUR, the run is in USD"


def test_the_ssim_multiple_ev_is_calculated_from_ssim_ebitda_exactly() -> None:
    view = _view(inputs=_inputs(multiple="8.123456789012345678901234567"))
    ev, ssim = view.item("ev"), view.item("ssim_ebitda").cell
    assert ev.cell.value == Decimal("33257.432094216543209421654317298")
    assert (ev.cell.basis, ev.cell.sources) == ("CALCULATED", ssim.sources)
    assert ev.formula == "SSIM EV multiple x SSIM EBITDA"


def test_limitations_say_why_and_pf_interest_drops_the_stated_figure() -> None:
    regs = example_registers()
    plain = _view(replace(regs, pro_forma=()))
    assert plain.limitations[0] == (
        "PF_LTM_EQUALS_LTM",
        "no pro forma adjustments for the LTM: every PF figure is the LTM's",
    )
    interest = plain.item("pf_interest").cell
    assert (interest.value, interest.stated, interest.note) == (Decimal(862), None, None)
    rows = tuple(a for a in regs.pro_forma if a.metric_id != "cash_interest_paid")
    assert _view(replace(regs, pro_forma=rows)).limitations[0] == (
        "PF_INTEREST_NOT_SOURCED",
        "no sourced PF cash interest: PF interest is the LTM's cash interest",
    )
    assert _view(replace(regs, periods=())).equity.reason == "NOT_APPLICABLE"
