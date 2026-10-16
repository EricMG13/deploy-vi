"""Model lines: terms, metrics, PF rows, growth and any consistent inputs."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

from assemble_cases import (
    _LTM,
    _PF,
    _cell,
    _line,
    _model,
    _nudged,
    _signed_zeros,
    _value,
    _with_cell,
)
from credit_model_fixture import example_registers, with_figures
from hypothesis import example, given, settings
from hypothesis import strategies as st

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import (
    NO_PROJECTIONS,
    NOT_APPLIED,
    reconciliation_faults,
)
from rbotlib.model.frame import Cell
from rbotlib.model.history import account_frame, historical_columns
from rbotlib.model.layout import (
    FacilityTerms,
    facility_terms,
    layout,
)
from rbotlib.model.metrics import metric_frame
from rbotlib.model.registers import Cp1Registers, PfAdjustmentRow
from rbotlib.model.statements import statement_frame


def test_less_cash_is_closing_cash_negated() -> None:
    model = _model()
    for column in model.columns:
        if column.kind == "PF_LTM":
            continue  # closing cash shows the LTM's there, its PF row beneath
        cash = _cell(model, "cash_closing", column.column_id)
        less = _cell(model, "less_cash", column.column_id)
        assert cash.value is not None
        with localcontext(CONTEXT):
            assert less == replace(cash, value=-cash.value)
    assert _value(model, "less_cash", _PF) == -950
    regs = example_registers()
    stated = Decimal("1000")
    cash = replace(_cell(model, "cash_closing", _LTM), value=Decimal(1000), stated=stated)
    assert cash.stated == stated
    columns = historical_columns(regs)
    frame = statement_frame(account_frame(regs, columns), columns, regs)
    frame[_LTM]["cash_closing"] = cash
    metrics = metric_frame(columns, frame, {k: frame[k] for k in frame})
    lines = layout(regs, columns, metrics, False, None)
    index = [c.column_id for c in columns].index(_LTM)
    less = next(line for line in lines if line.line_id == "less_cash").cells[index]
    assert (less.value, less.stated) == (Decimal(-1000), Decimal(-1000))


def test_facility_terms_are_shown_as_stated_never_rounded() -> None:
    model = _model()
    assert _line(model, "fac:rcf").terms == FacilityTerms(
        "SOFR", "+225 bp", "none", "2030-01-31", "bullet"
    )
    assert _line(model, "fac:tlb").terms == FacilityTerms(
        "SOFR", "+275 bp", "0.50%", "2030-02-28", "24 p.a."
    )
    assert _line(model, "fac:ssn29").terms == FacilityTerms(
        "none", "6.500%", "n.a.", "2029-02-15", "bullet"
    )
    assert _line(model, "fac:finl").terms == FacilityTerms(
        "not stated", "not stated", "n.a.", "not stated", "not stated"
    )
    assert _line(model, "revenue").terms is None
    row = next(f for f in example_registers().facilities if f.facility_id == "tlb")
    odd = replace(
        row,
        reference_rate="TERM_SOFR",
        spread_bps=Decimal("262.5"),
        floor_bps=Decimal("12.5"),
        annual_amortisation=Decimal("0.0001"),
    )
    assert facility_terms(odd) == FacilityTerms(
        "Term SOFR", "+262.5 bp", "0.125%", "2030-02-28", "0.0001 p.a."
    )
    assert facility_terms(replace(odd, reference_rate="LIBOR")).reference_rate == "LIBOR"
    assert facility_terms(replace(odd, spread_bps=None)).spread_or_coupon == "not stated"
    assert facility_terms(replace(odd, rate_type="FIXED")).spread_or_coupon == ("not stated")
    fixed = replace(odd, rate_type="FIXED", fixed_rate=Decimal("7.125"), floor_bps=None)
    assert (facility_terms(fixed).spread_or_coupon, facility_terms(fixed).floor) == (
        "7.125%",
        "n.a.",
    )
    assert facility_terms(replace(odd, rate_type="NOT_STATED", floor_bps=None)).floor == "n.a."
    assert (
        facility_terms(replace(odd, rate_type="FIXED", fixed_rate=Decimal("1E+1"))).spread_or_coupon
        == "10%"
    )


def test_every_metric_in_the_frame_has_one_line() -> None:
    model = _model()
    ids = [line.line_id for line in model.lines]
    assert len(ids) == len(set(ids))
    regs = example_registers()
    columns = historical_columns(regs)
    frame = statement_frame(account_frame(regs, columns), columns, regs)
    ltm_ending = {c.column_id: frame[c.column_id] for c in columns}
    keys = metric_frame(columns, frame, ltm_ending)[_LTM]
    metrics = {k for k in keys if k.startswith(("metric:", "bu_growth:")) or k.endswith("_growth")}
    assert metrics - set(ids) == {"bu_growth:corporate_eliminations"}


def test_a_foreign_facility_is_a_memo_outside_its_rank_total() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        facilities=tuple(
            replace(f, currency="EUR") if f.facility_id == "ssn29" else f for f in regs.facilities
        ),
    )
    regs = replace(regs, pro_forma=(*regs.pro_forma, _adjustment("eur", "facility:ssn29", 70)))
    model = _model(regs=regs)
    assert _line(model, "fac:ssn29").kind == "MEMO"
    assert _value(model, "pf:eur", _PF) == 70
    assert _line(model, "fac:ssn29").rank == "Senior secured"
    assert _value(model, "rank:Senior secured", _LTM) == 2316 + 1000
    assert _value(model, "rank:Senior secured", _PF) == 2316 + 1600
    assert reconciliation_faults(model) == ()
    one = replace(
        regs,
        facilities=tuple(
            replace(f, currency="EUR") if f.facility_id == "ssn31" else f for f in regs.facilities
        ),
    )
    assert "rank:Senior secured" not in {line.line_id for line in _model(regs=one).lines}


def _adjustment(adjustment_id: str, metric_id: str, value: int) -> PfAdjustmentRow:
    return PfAdjustmentRow(
        adjustment_id=adjustment_id,
        label=f"{adjustment_id} label",
        period_id="LTM_Q2_2026",
        classification="ACQUISITION",
        metric_id=metric_id,
        value=Decimal(value),
        source=None,
    )


def test_pf_rows_sit_by_the_line_they_adjust_and_reconcile() -> None:
    regs = example_registers()
    leases = tuple(
        replace(
            f,
            facility_id="opl",
            facility_name="Operating leases",
            lease_classification="OPERATING_LEASE",
        )
        for f in regs.facilities
        if f.facility_id == "finl"
    )
    regs = replace(
        regs,
        # Left out or placed nowhere first, so the rest are still read.
        facilities=(*leases, *regs.facilities),
        pro_forma=(
            replace(_adjustment("old", "revenue", 1), period_id="FY2025"),
            _adjustment("capex", "capex_and_intangible_investment", -5),
            *regs.pro_forma,
            _adjustment("rev", "revenue", 70),
            _adjustment("ebitda_pf", "ebitda", 20),
            _adjustment("new_loan", "facility:new_loan", 300),
            _adjustment("debt", "total_debt", 15),
            _adjustment("lease", "facility:opl", 9),
        ),
    )
    model = _model(regs=regs)
    ids = [line.line_id for line in model.lines]

    def before(first: str, second: str) -> bool:
        return ids.index(first) + 1 == ids.index(second)

    assert before("pf:rev", "revenue")
    assert before("pf:ebitda_pf", "ebitda")
    assert before("fac:disc", "debt:unallocated")
    assert before("debt:unallocated", "pf:new_loan")
    assert before("pf:new_loan", "pf:debt")
    assert before("pf:debt", "total_debt")
    assert before("lease_liabilities", "pf:lease")
    assert "fac:opl" not in ids
    assert _cell(model, "lease_liabilities", _PF) == _cell(model, "lease_liabilities", _LTM)
    assert _value(model, "lease_adjusted_debt", _PF) == (_value(model, "total_debt", _PF) + 260 + 9)
    assert "pf:capex" not in ids
    assert "pf:old" not in ids
    assert _line(model, "pf:new_loan").rank is None
    assert _line(model, "pf:silverlake_notes").rank == "Senior secured"
    assert [i for i in ids if i.startswith("rollforward:pf:")] == [
        "rollforward:pf:silverlake_notes",
        "rollforward:pf:new_loan",
        "rollforward:pf:debt",
    ]
    assert _value(model, "total_debt", _PF) == _value(model, "total_debt", _LTM) + 915
    assert reconciliation_faults(model) == ()
    assert f"{NOT_APPLIED}: capex label" in model.limitations
    assert not any("old label" in text for text in model.limitations)
    broken = _nudged(model, "pf:new_loan", _PF)
    assert reconciliation_faults(broken) == (f"{_PF}:total_debt",)
    assert _cell(model, "revenue", _PF).note is None
    broken = _nudged(model, "pf:ebitda_pf", _PF)
    assert reconciliation_faults(broken) == (f"{_PF}:ebitda",)
    broken = _nudged(model, "pf:lease", _PF)
    assert reconciliation_faults(broken) == ()


def test_a_model_without_segments_notes_nothing_on_revenue() -> None:
    regs = replace(example_registers(), segments=())
    model = _model(regs=regs)
    assert not any(line.line_id.startswith("bu") for line in model.lines)
    assert all(cell.note is None for cell in _line(model, "revenue").cells)
    broken = _nudged(model, "revenue", "FY:FY2024")
    assert reconciliation_faults(broken) == ()


def _figures(low: int = -30000) -> st.SearchStrategy[Decimal | None]:
    """A figure in tenths up to 3,000.0, from `low` tenths; about one in 33
    has none, and a zero is written "(0)" (negative zero) half the time.
    Hypothesis shrinks it."""
    return st.tuples(
        st.integers(min_value=0, max_value=32),
        st.integers(min_value=low, max_value=30000),
    ).map(_figure)


def _figure(drawn: tuple[int, int]) -> Decimal | None:
    flag, tenths = drawn
    if flag == 0:
        return None
    return Decimal("-0") if tenths == 0 and flag % 2 else Decimal(tenths) / 10


_STATUSES = st.sampled_from(("REALIZED", "UNREALIZED", "NOT_STATED"))


@st.composite
def _registers(draw: st.DrawFn) -> Cp1Registers:
    """The example's registers with every figure redrawn; each period's
    revenue is its business units' sum, as CP-1's segment check requires."""
    regs = example_registers()
    segments = tuple(replace(s, revenue=draw(_figures(0))) for s in regs.segments)
    sums: dict[str, Decimal | None] = {}
    for segment in segments:
        held = sums.get(segment.period_id, Decimal(0))
        sums[segment.period_id] = (
            None if held is None or segment.revenue is None else held + segment.revenue
        )
    accounts = tuple(
        replace(
            a,
            value=sums.get(a.period_id) if a.metric_id == "revenue" else draw(_figures()),
        )
        for a in regs.accounts
    )
    addbacks = tuple(
        replace(a, value=draw(_figures()), realization_status=draw(_STATUSES))
        for a in regs.addbacks
    )
    facilities = tuple(replace(f, carrying_value=draw(_figures(-2000))) for f in regs.facilities)
    pro_forma = tuple(replace(p, value=draw(_figures()) or Decimal(1)) for p in regs.pro_forma)
    return replace(
        regs,
        segments=segments,
        accounts=accounts,
        addbacks=addbacks,
        facilities=facilities,
        pro_forma=pro_forma,
    )


@settings(max_examples=40, deadline=None)
@given(regs=_registers(), exclude=st.booleans())
# Hypothesis's find: a year-end cash of "(0)" opened the next periods at -0.
@example(
    regs=with_figures(example_registers(), "FY2023", {"cash_and_equivalents": Decimal("-0")}),
    exclude=False,
)
def test_any_consistent_inputs_reconcile(regs: Cp1Registers, exclude: bool) -> None:
    model = _model(regs=regs, exclude_unrealised=exclude)
    assert reconciliation_faults(model) == ()
    assert _signed_zeros(model) == []


def test_growth_lines_read_their_growth() -> None:
    model = _model()
    with localcontext(CONTEXT):
        revenue = Decimal(11519) / Decimal(11165) - 1
        adjusted = Decimal(4019) / Decimal(3872) - 1
    assert _value(model, "revenue_growth", "FY:FY2025") == revenue
    assert _value(model, "adjusted_ebitda_growth", "FY:FY2025") == adjusted


def test_an_add_back_with_another_realisation_status_shows_it() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        addbacks=tuple(
            replace(a, realization_status="PARTIAL") if a.addback_id == "restructuring" else a
            for a in regs.addbacks
        ),
    )
    line = _line(_model(regs=regs, exclude_unrealised=True), "addback:restructuring")
    assert (line.label, line.kind) == ("Add-back: Restructuring (PARTIAL)", "ACCOUNT")


def test_registers_without_periods_give_a_model_without_columns() -> None:
    regs = replace(example_registers(), periods=())
    model = _model(regs=regs)
    assert model.columns == ()
    assert all(line.cells == () for line in model.lines)
    assert model.limitations == (NO_PROJECTIONS,)
    assert reconciliation_faults(model) == ()


def test_debt_bridges_count_a_facility_absent_at_a_date_as_nothing() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        facilities=tuple(
            f
            for f in regs.facilities
            if not (f.facility_id == "sun29" and f.period_id in {"Q4_2024", "FY2024"})
        ),
    )
    model = _model(regs=regs)
    assert _cell(model, "fac:sun29", "FY:FY2024").reason == "NOT_SOURCED"
    assert _value(model, "rank:Senior unsecured", "FY:FY2024") == 3500
    assert reconciliation_faults(model) == ()
    for line_id, bridge in (
        ("rank:Senior unsecured", "rank:Senior unsecured"),
        ("total_debt", "total_debt"),
    ):
        faults = reconciliation_faults(_nudged(model, line_id, "FY:FY2024"))
        assert f"FY:FY2024:{bridge}" in faults


def test_the_roll_forward_adds_its_pf_rows() -> None:
    model = _model()
    stray = _with_cell(model, "rollforward:pf:silverlake_notes", _LTM, Cell(Decimal(1)))
    assert reconciliation_faults(stray) == (f"{_LTM}:debt_rollforward",)


def test_a_period_without_revenue_notes_nothing() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        accounts=tuple(
            replace(a, value=None) if a.metric_id == "revenue" and a.period_id == "Q1_2024" else a
            for a in regs.accounts
        ),
    )
    cell = _cell(_model(regs=regs), "revenue", "Q:Q1_2024")
    assert (cell.value, cell.note) == (None, None)
