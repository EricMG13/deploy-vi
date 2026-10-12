"""CP-1D, identity and equity rows read whole (the mutation gate's findings
on `rbotlib.model.house_inputs`)."""

from __future__ import annotations

import re
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers

from rbotlib.handoff import Table
from rbotlib.model.house_inputs import (
    DebtLikeItem,
    EquityValue,
    Identity,
    assessments,
    debt_like_items,
    equity_value,
    identities,
)
from rbotlib.model.reader import ModelInputError

IDENTITY = ["facility_id", "instrument_name", "rating_moodys", "rating_sp", "rating_fitch", "cite"]
DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]
PENSION = ["Pension deficit", "120", "USD", "MILLIONS", "LTM_Q2_2026", "Debt-like", "unfunded"]
ASSESSED = ["addback_id", "period_id", "house_realization_status", "verdict", "cite"]


def test_identity_equity_and_debt_like_rows_are_read_whole() -> None:
    rows = [["tlb", "Term Loan B", "—", "—", "BB+", "[C4]"]]
    found = identities({"cp1.instrument_identity": Table(IDENTITY, rows)})
    assert found["tlb"] == Identity("tlb", "Term Loan B", None, "— / — / BB+", "[C4]")
    columns = ["market_cap", "value_date", "currency", "unit", "cite"]
    equity = Table(columns, [["6,316", "2026-10-02", "usd", "MILLIONS", "[C9]"]])
    assert equity_value({"cp1.equity_value": equity}) == EquityValue(
        Decimal(6316), "2026-10-02", "USD", "MILLIONS", "[C9]"
    )
    table = Table(DEBT_LIKE, [[*PENSION, "[C3]"]])
    pension = DebtLikeItem(
        "Pension deficit", Decimal(120), "USD", "MILLIONS", "LTM_Q2_2026", "Debt-like",
        "unfunded", "[C3]",
    )  # fmt: skip
    assert debt_like_items({"cp1d.debt_like_items": table}, example_registers()) == (pension,)


def test_a_debt_like_item_needs_its_basis_and_is_listed_once() -> None:
    regs = example_registers()
    no_basis = Table([*DEBT_LIKE[:6], "cite"], [[*PENSION[:6], "[C3]"]])
    with pytest.raises(
        ModelInputError, match=re.escape("cp1d.debt_like_items: missing column basis")
    ):
        debt_like_items({"cp1d.debt_like_items": no_basis}, regs)
    no_item = Table(DEBT_LIKE[1:], [[*PENSION[1:], "[C3]"]])
    with pytest.raises(ModelInputError, match=re.escape("missing column item")):
        debt_like_items({"cp1d.debt_like_items": no_item}, regs)
    twice = Table(DEBT_LIKE, [[*PENSION, "[C3]"]] * 2)
    match = "cp1d.debt_like_items row 2: debt_like:pension_deficit / 2026-06-30 written twice"
    with pytest.raises(ModelInputError, match=re.escape(match)):
        debt_like_items({"cp1d.debt_like_items": twice}, regs)
    rows = [["restructuring", "FY2025", "REALIZED", "Rejected", "[C1]"]] * 2
    match = "cp1d.addback_assessment row 2: restructuring / FY2025 written twice"
    with pytest.raises(ModelInputError, match=re.escape(match)):
        assessments({"cp1d.addback_assessment": Table(ASSESSED, rows)})
