"""The assembled Model reconciles exactly past the 28 digits of Python's
default decimal context (its bridges are checked at `CONTEXT`'s 38)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers

from rbotlib.model.assemble import ModelInputs, credit_model, reconciliation_faults


def test_a_model_of_29_digit_debt_has_no_reconciliation_fault() -> None:
    big = Decimal("512345678901234567.0123456789")  # the largest the reader takes
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=big) if f.facility_id in {"tlb", "ssn29"} else f
        for f in regs.facilities
    )
    model = credit_model(ModelInputs(replace(regs, facilities=facilities)))
    assert reconciliation_faults(model) == ()
