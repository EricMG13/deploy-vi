"""Model edge cases: foreign facilities, PF registers, negative zeros and bridges."""

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

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import (
    CreditModel,
    reconciliation_faults,
)

_EXCLUDES_FOREIGN = "excludes facility in another currency"


_DOUBLE_COUNT = (
    "PF register states both ebitda and adjusted_ebitda adjustments; check for double counting"
)


def _on(model: CreditModel) -> dict[str, str]:
    """Each limitation's note and the columns it is on."""
    return dict(text.split(": ", 1) for text in model.limitations if ": " in text)


_BU_NOT_SUMMED = "business units do not sum to revenue"


def test_a_foreign_facility_is_noted_on_debt_interest_and_their_metrics() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        accounts=tuple(a for a in regs.accounts if a.metric_id != "total_debt"),
        facilities=tuple(
            replace(f, currency="EUR") if f.facility_id == "sun29" else f for f in regs.facilities
        ),
    )
    model = _model(regs=regs)

    for column_id, line_id in (
        (_LTM, "total_debt"),
        (_LTM, "net_debt"),
        (_LTM, "metric:total_leverage_adjusted"),
        (_LTM, "metric:liquidity_to_debt"),
        (_PF, "total_debt"),
        (_PF, "metric:net_leverage_adjusted"),
    ):
        assert _EXCLUDES_FOREIGN in (_cell(model, line_id, column_id).note or ""), (
            column_id,
            line_id,
        )
    # Historical interest is CP-1's own: nothing is left out of it.
    assert _cell(model, "metric:interest_coverage_adjusted", _LTM).note is None
    on = _on(model)
    assert _LTM in on[_EXCLUDES_FOREIGN].split(", ")
    assert reconciliation_faults(model) == ()


def test_a_pf_register_with_ebitda_and_adjusted_ebitda_rows_is_a_limitation() -> None:
    regs = example_registers()
    adjusted = next(a for a in regs.pro_forma if a.metric_id == "adjusted_ebitda")
    both = replace(
        regs,
        pro_forma=(
            *regs.pro_forma,
            replace(adjusted, adjustment_id="silverlake_reported", metric_id="ebitda"),
        ),
    )

    assert _DOUBLE_COUNT in _model(regs=both).limitations
    assert _DOUBLE_COUNT not in _model().limitations
    # Rows for another period than the LTM's are not on the PF-LTM.
    elsewhere = replace(
        both,
        pro_forma=(
            *regs.pro_forma,
            replace(
                adjusted,
                adjustment_id="silverlake_reported",
                metric_id="ebitda",
                period_id="FY2025",
            ),
        ),
    )
    assert _DOUBLE_COUNT not in _model(regs=elsewhere).limitations


def test_no_cell_is_a_negative_zero() -> None:
    regs = with_figures(
        example_registers(),
        "FY2025",
        {"dividends_paid": Decimal(0), "capex_and_intangible_investment": Decimal(0)},
    )
    model = _model(regs=regs)

    assert _signed_zeros(model) == []
    assert _value(model, "dividends", "FY:FY2025") == 0


def test_the_pf_ltm_debt_roll_forward_foots() -> None:
    model = _model()
    assert _cell(model, "debt_opening", _PF) == _cell(model, "debt_opening", _LTM)
    assert _cell(model, "debt_non_cash", _PF) == _cell(model, "debt_non_cash", _LTM)
    assert _cell(model, "rollforward:debt_raised_net", _PF) == _cell(
        model, "rollforward:debt_raised_net", _LTM
    )
    assert _value(model, "debt_closing", _PF) == _value(model, "total_debt", _PF)
    assert reconciliation_faults(model) == ()
    assert reconciliation_faults(_nudged(model, "debt_closing", _PF)) == (
        f"{_PF}:debt_rollforward",
    )


def test_a_debt_adjustment_classified_as_an_operating_lease_is_in_the_stack() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        facilities=tuple(
            replace(f, lease_classification="OPERATING_LEASE") if f.facility_id == "disc" else f
            for f in regs.facilities
        ),
    )
    model = _model(regs=regs)

    line = _line(model, "fac:disc")
    assert (line.kind, line.rank) == ("ACCOUNT", "Debt adjustments")
    assert reconciliation_faults(model) == ()


def test_the_unallocated_line_has_no_payment_rank() -> None:
    assert _line(_model(), "debt:unallocated").rank is None


def test_an_add_back_label_shows_the_status_that_excludes_it() -> None:
    regs = example_registers()
    rows = [a for a in regs.addbacks if a.addback_id == "restructuring"]
    regs = replace(
        regs,
        addbacks=tuple(
            replace(a, realization_status="UNREALIZED") if a is rows[0] else a
            for a in regs.addbacks
        ),
    )
    assert rows[-1].realization_status == "REALIZED"

    line = _line(_model(regs=regs, exclude_unrealised=True), "addback:restructuring")
    assert (line.label, line.kind) == (
        "Add-back: Restructuring (unrealised), excluded if positive",
        "MEMO",
    )
    line = _line(_model(regs=regs), "addback:restructuring")
    assert (line.label, line.kind) == (
        "Add-back: Restructuring (unrealised)",
        "ACCOUNT",
    )


def test_a_pf_facility_issued_after_the_ltm_sums_in_its_rank() -> None:
    regs = example_registers()
    ssn31 = next(f for f in regs.facilities if f.facility_id == "ssn31")
    later = next(p for p in regs.periods if p.period_id == "LTM_Q2_2026")
    post = replace(later, period_id="PE_2026_09", end_date="2026-09-30")
    new = replace(
        ssn31,
        facility_id="ssn33",
        facility_name="New 2033 notes",
        period_id="PE_2026_09",
        carrying_value=Decimal(600),
    )
    notes = next(a for a in regs.pro_forma if a.metric_id == "facility:ssn31")
    regs = replace(
        regs,
        periods=(*regs.periods, post),
        facilities=(*regs.facilities, new),
        pro_forma=(
            *(a for a in regs.pro_forma if a is not notes),
            replace(notes, adjustment_id="ssn33_pf", metric_id="facility:ssn33"),
        ),
    )
    model = _model(regs=regs)

    assert _value(model, "rank:Senior secured", _PF) == 2316 + 2000 + 1000 + 600
    assert reconciliation_faults(model) == ()


def test_business_unit_growth_reads_the_like_period() -> None:
    model = _model()
    with localcontext(CONTEXT):
        las_vegas = (
            _value(model, "bu:las_vegas", "FY:FY2025") / _value(model, "bu:las_vegas", "FY:FY2024")
            - 1
        )
    assert _value(model, "bu_growth:las_vegas", "FY:FY2025") == las_vegas


def test_an_acquisition_reconciles_through_the_net_cash_flow() -> None:
    regs = with_figures(example_registers(), "FY2025", {"acquisitions_disposals": Decimal(-120)})
    model = _model(regs=regs)
    assert _value(model, "acquisitions_net", "FY:FY2025") == -120
    assert reconciliation_faults(model) == ()


def _interest_at(gap: Decimal) -> tuple[str, ...]:
    """The interest faults with a base of 1 at 5% and interest `gap` more
    negative than minus their product: the check allows a unit of the rate
    times the base (1E-39), the interest's rounding (about 5E-39) and a unit
    of the interest (1E-39), about 7E-39. Until the projection port, the
    three cells are set by hand on a historical column."""
    model = _model()
    base = "FY:FY2025"
    for line_id, value in (
        ("interest_bearing_debt_opening", Decimal(1)),
        ("wa_rate", Decimal("0.05")),
        ("cash_interest", Decimal("-0.05") - gap),
    ):
        cell = replace(_cell(model, line_id, base), value=value)
        model = _with_cell(model, line_id, base, cell)
    return tuple(f for f in reconciliation_faults(model) if f.endswith(":interest"))


def test_the_interest_bridge_allows_exactly_its_last_digits() -> None:
    with localcontext(CONTEXT):
        assert _interest_at(Decimal(0)) == ()
        assert _interest_at(Decimal("6E-39")) == ()
        assert _interest_at(Decimal("8E-39")) == ("FY:FY2025:interest",)


def test_a_pf_register_of_only_ebitda_and_adjusted_ebitda_rows_is_noted() -> None:
    regs = example_registers()
    adjusted = next(a for a in regs.pro_forma if a.metric_id == "adjusted_ebitda")
    only = replace(
        regs,
        pro_forma=(
            adjusted,
            replace(adjusted, adjustment_id="silverlake_reported", metric_id="ebitda"),
        ),
    )
    assert _DOUBLE_COUNT in _model(regs=only).limitations


def test_a_pf_refinancing_that_cuts_interest_raises_pf_coverage() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        pro_forma=tuple(
            replace(a, value=Decimal(30)) if a.metric_id == "cash_interest_paid" else a
            for a in regs.pro_forma
        ),
    )
    model = _model(regs=regs)

    coverage = "metric:interest_coverage_adjusted"
    assert _value(model, coverage, _PF) > _value(model, coverage, _LTM)
    assert _value(model, "pf:silverlake_interest", _PF) == 30


def test_a_parenthesised_zero_is_never_a_negative_zero() -> None:
    zero = Decimal("-0")  # how the host reads "(0)"
    regs = with_figures(
        example_registers(),
        "FY2025",
        {"revenue": zero, "dividends_paid": zero},
    )
    regs = with_figures(regs, "Q2_2026", {"dividends_paid": zero})
    regs = replace(
        regs,
        pro_forma=tuple(
            replace(a, value=zero) if a.metric_id == "cash_interest_paid" else a
            for a in regs.pro_forma
        ),
    )
    model = _model(regs=regs)

    assert _signed_zeros(model) == []
    assert str(_value(model, "pf:silverlake_interest", _PF)) == "0"
