"""The house view on the PF-LTM (spec D19, §6.5), hand-checked on the caos
Example Gaming Co. registers and property-tested.

The example's PF-LTM (`PF:LTM_Q2_2026`): adjusted EBITDA with the run-rate
cost savings (40, unrealised) excluded is 4,049 + the Silverlake PF 45 =
4,094 (SSIM EBITDA); Structuring EBITDA adds the 40 back: 4,134. Total debt
is the LTM's 14,106 + the 600 add-on notes = 14,706; closing cash 1,000 - 50
= 950, so net debt is 13,756; cash interest -862 - 42 = -904, so PF interest
is 904.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

from credit_model_fixture import example_registers
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.frame import Cell
from rbotlib.model.house import (
    HouseView,
    cell,
    cumulative,
    house_view,
    percent_of,
    ratio,
    secured,
    snapshot_column,
    with_debt_like_lines,
)
from rbotlib.model.house_inputs import (
    AddbackAssessment,
    BriefFields,
    DebtLikeItem,
    EquityValue,
    HouseInputs,
    effective_registers,
)
from rbotlib.model.registers import Cp1Registers

PF = "PF:LTM_Q2_2026"
LTM_PERIOD = "LTM_Q2_2026"


def _inputs(
    *,
    equity: EquityValue | None = None,
    assessed: tuple[AddbackAssessment, ...] = (),
    debt_like: tuple[DebtLikeItem, ...] = (),
    multiple: Decimal | None = Decimal("8.5"),
) -> HouseInputs:
    return HouseInputs(
        {}, equity, assessed, debt_like, BriefFields("R", multiple, False, frozenset())
    )


def _view(regs: Cp1Registers | None = None, inputs: HouseInputs | None = None) -> HouseView:
    inputs = inputs or _inputs()
    regs = effective_registers(regs or example_registers(), inputs.assessments)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    return house_view(with_debt_like_lines(model, regs, inputs.debt_like), regs, inputs)


def _value(view: HouseView, key: str) -> Decimal:
    value = view.item(key).cell.value
    assert value is not None, key
    return value


def _div(a: Decimal, b: Decimal) -> Decimal:
    with localcontext(CONTEXT):
        return a / b


def test_the_house_items_on_the_pf_ltm() -> None:
    view = _view()
    assert view.column is not None and view.column.column_id == PF
    assert _value(view, "ssim_ebitda") == 4094
    assert _value(view, "structuring_ebitda") == 4134
    assert view.item("structuring_ebitda").components == (
        "adjusted_ebitda",
        "addback:run_rate_cost_savings",
    )
    assert _value(view, "pf_interest") == 904
    assert _value(view, "pf_interest_cover") == _div(Decimal(4094), Decimal(904))
    assert _value(view, "structuring_multiple") == _div(Decimal(14706), Decimal(4134))
    assert _value(view, "ssim_multiple") == _div(Decimal(14706), Decimal(4094))
    assert _value(view, "adjusted_debt") == 14706
    assert _value(view, "adjusted_leverage") == _div(Decimal(14706), Decimal(4094))
    assert [i.item for i in view.items] == [
        "Structuring EBITDA",
        "SSIM EBITDA",
        "PF interest",
        "PF interest cover",
        "Structuring Multiple",
        "SSIM Multiple",
        "EV",
        "Adjusted debt",
        "Adjusted leverage",
    ]


def test_ev_from_the_ssim_multiple_and_from_listed_equity() -> None:
    view = _view()
    assert view.ev_basis == "ssim_multiple"
    assert _value(view, "ev") == Decimal("8.5") * 4094
    assert view.equity.value == Decimal("8.5") * 4094 - 13756
    equity = EquityValue(Decimal(12_000_000), "2026-10-02", "USD", "THOUSANDS", "[C9]")
    listed = _view(inputs=_inputs(equity=equity))
    assert listed.ev_basis == "listed"
    assert listed.equity.value == 12000
    assert _value(listed, "ev") == 12000 + 13756
    euro = _view(inputs=_inputs(equity=replace(equity, currency="EUR")))
    assert euro.item("ev").cell.reason == "NOT_APPLICABLE"
    assert (
        "EQUITY_CURRENCY_MISMATCH",
        "equity value in EUR, the run is in USD",
    ) in euro.limitations
    none = _view(inputs=_inputs(multiple=None))
    assert none.item("ev").cell.reason == "NOT_SOURCED"
    assert none.ev_basis is None
    assert any(code == "EV_NOT_AVAILABLE" for code, _ in none.limitations)


def test_a_facility_on_the_pf_ltm_carries_its_pf_rows() -> None:
    view = _view()
    outstanding = {p.facility_id: p.outstanding.value for p in view.positions}
    assert outstanding["ssn31"] == 1000 + 600
    assert outstanding["tlb"] == 2316
    assert outstanding["disc"] == -170
    assert secured(view).value == 0 + 2316 + 2000 + 1600
    assert cumulative(view, "Senior unsecured").value == 5916 + 3600 + 3500
    share = percent_of(Cell(Decimal(1600)), view.item("ev").cell).value
    with localcontext(CONTEXT):
        assert share == Decimal(1600) / (Decimal("8.5") * 4094) * 100


def test_a_new_facility_with_only_pf_rows_starts_from_nothing() -> None:
    regs = example_registers()
    notes = next(a for a in regs.pro_forma if a.metric_id == "facility:ssn31")
    tlb = next(f for f in regs.facilities if f.facility_id == "tlb" and f.period_id == "Q2_2026")
    new = replace(tlb, facility_id="NEW-1", facility_name="New TLB", carrying_value=Decimal(0))
    regs = replace(
        regs,
        facilities=(*regs.facilities, new),
        pro_forma=(
            *regs.pro_forma,
            replace(notes, adjustment_id="new1", metric_id="facility:NEW-1"),
        ),
    )
    outstanding = {p.facility_id: p.outstanding.value for p in _view(regs).positions}
    assert outstanding["NEW-1"] == 600


def test_cp1d_statuses_move_add_backs_between_ssim_and_structuring() -> None:
    rejected = AddbackAssessment("restructuring", LTM_PERIOD, "REALIZED", "Rejected", "[C1]")
    view = _view(inputs=_inputs(assessed=(rejected,)))
    assert _value(view, "ssim_ebitda") == 4094 - 32
    assert _value(view, "structuring_ebitda") == 4134
    supported = AddbackAssessment(
        "run_rate_cost_savings", LTM_PERIOD, "REALIZED", "Supported", "[C1]"
    )
    view = _view(inputs=_inputs(assessed=(supported,)))
    # Owner ruling 2026-10-12: latest LTM judgment governs older rows too.
    assert _value(view, "ssim_ebitda") == 4134


def test_debt_like_items_add_to_adjusted_debt_and_show_as_memo_lines() -> None:
    pension = DebtLikeItem(
        "Pension deficit",
        Decimal(120),
        "USD",
        "MILLIONS",
        LTM_PERIOD,
        "Debt-like",
        "unfunded",
        "[C1]",
    )
    unclear = replace(pension, item="Guarantee", treatment="Unclear")
    inputs = _inputs(debt_like=(pension, unclear))
    view = _view(inputs=inputs)
    assert _value(view, "adjusted_debt") == 14706 + 120
    assert view.item("adjusted_debt").components == ("total_debt", "debt_like:pension_deficit")
    assert _value(view, "adjusted_leverage") == _div(Decimal(14826), Decimal(4094))
    regs = example_registers()
    model = with_debt_like_lines(
        credit_model(ModelInputs(regs, exclude_unrealised=True)), regs, (pension, unclear)
    )
    ids = [line.line_id for line in model.lines]
    assert "debt_like:guarantee" not in ids
    line = model.lines[ids.index("debt_like:pension_deficit")]
    assert (line.kind, line.band, line.label) == (
        "MEMO",
        model.lines[ids.index("total_debt")].band,
        "Memo: debt-like, Pension deficit",
    )
    assert ids.index("debt_like:pension_deficit") > ids.index("lease_adjusted_net_debt")
    on = {c.column_id: x for c, x in zip(model.columns, line.cells, strict=True)}
    assert on[PF].value == 120 and on["LTM:LTM_Q2_2026"].value == 120
    assert on["FY:FY2025"].reason == "NOT_SOURCED"
    assert with_debt_like_lines(model, regs, (unclear,)) is model


def test_without_pf_rows_the_snapshot_column_is_the_ltm() -> None:
    view = _view(replace(example_registers(), pro_forma=()))
    assert view.column is not None and view.column.column_id == "LTM:LTM_Q2_2026"
    assert _value(view, "pf_interest") == 862
    assert [code for code, _ in view.limitations] == ["PF_LTM_EQUALS_LTM"]
    regs = example_registers()
    no_interest = replace(
        regs, pro_forma=tuple(a for a in regs.pro_forma if a.metric_id != "cash_interest_paid")
    )
    view = _view(no_interest)
    assert _value(view, "pf_interest") == 862
    assert [code for code, _ in view.limitations] == ["PF_INTEREST_NOT_SOURCED"]


def test_no_ltm_means_no_house_view() -> None:
    regs = replace(example_registers(), periods=())
    view = _view(regs)
    assert view.column is None and view.items == () and view.positions == ()
    assert view.limitations == (("NO_LTM", "the Model has no LTM column, so no house view"),)


def test_a_denominator_at_or_below_zero_gives_no_figure() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        pro_forma=tuple(
            replace(a, value=Decimal(904)) if a.metric_id == "cash_interest_paid" else a
            for a in regs.pro_forma
        ),
    )
    view = _view(regs)
    assert _value(view, "pf_interest") == -42
    assert view.item("pf_interest_cover").cell.reason == "ZERO_OR_NEGATIVE_DENOMINATOR"
    assert ratio(Cell(Decimal(1)), Cell(Decimal(0))).reason == "ZERO_OR_NEGATIVE_DENOMINATOR"
    missing = ratio(Cell(None, "NOT_STATED", note="a"), Cell(None, "NOT_SOURCED", note="b"))
    assert (missing.reason, missing.note) == ("NOT_STATED", "a; b")
    assert percent_of(Cell(Decimal(1)), Cell(None, "NOT_SOURCED")).reason == "NOT_SOURCED"


def test_snapshot_column_and_cell_lookups() -> None:
    model: CreditModel = credit_model(ModelInputs(example_registers(), exclude_unrealised=True))
    column = snapshot_column(model)
    assert column is not None and column.kind == "PF_LTM"
    assert cell(model, "no_such_line", column).reason == "NOT_SOURCED"


_FIGURES = st.integers(min_value=-500, max_value=500).map(Decimal)
_STATUS = st.sampled_from(("REALIZED", "UNREALIZED", "NOT_STATED"))


@st.composite
def _addbacks(draw: st.DrawFn) -> Cp1Registers:
    """The example with every add-back figure and status redrawn per add-back."""
    regs = example_registers()
    status = {b.addback_id: draw(_STATUS) for b in regs.addbacks}
    figure = {b.addback_id: draw(_FIGURES) for b in regs.addbacks}
    addbacks = tuple(
        replace(b, realization_status=status[b.addback_id], value=figure[b.addback_id])
        for b in regs.addbacks
    )
    return replace(regs, addbacks=addbacks)


@settings(max_examples=30, deadline=None)
@given(regs=_addbacks())
def test_structuring_less_ssim_is_the_excluded_positive_add_backs(regs: Cp1Registers) -> None:
    view = _view(regs)
    column = view.column
    assert column is not None
    excluded = {b.addback_id for b in regs.addbacks if b.realization_status != "REALIZED"}
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    # A negative amount stays in SSIM EBITDA (F11): only the positive ones differ.
    total = sum(
        (
            max(cell(model, f"addback:{a}", column).value or Decimal(0), Decimal(0))
            for a in excluded
        ),
        Decimal(0),
    )
    with localcontext(CONTEXT):
        assert _value(view, "structuring_ebitda") - _value(view, "ssim_ebitda") == total


@settings(max_examples=30, deadline=None)
@given(regs=_addbacks())
def test_a_multiple_times_its_ebitda_is_total_debt(regs: Cp1Registers) -> None:
    view = _view(regs)
    for key, ebitda in (
        ("ssim_multiple", "ssim_ebitda"),
        ("structuring_multiple", "structuring_ebitda"),
    ):
        multiple, earnings = view.item(key).cell, view.item(ebitda).cell
        if earnings.value is None or earnings.value <= 0:
            assert multiple.value is None
            continue
        assert multiple.value is not None
        with localcontext(CONTEXT):
            back = multiple.value * earnings.value
        assert abs(back - 14706) <= Decimal("1e-30")


@settings(max_examples=30, deadline=None)
@given(debt=st.lists(_FIGURES, max_size=4))
def test_adjusted_debt_is_total_debt_plus_the_debt_like_items(debt: list[Decimal]) -> None:
    items = tuple(
        DebtLikeItem(f"Item {n}", amount, "USD", "MILLIONS", LTM_PERIOD, "Debt-like", "b", "[C1]")
        for n, amount in enumerate(debt)
    )
    view = _view(inputs=_inputs(debt_like=items))
    assert _value(view, "adjusted_debt") == 14706 + sum(debt, Decimal(0))
