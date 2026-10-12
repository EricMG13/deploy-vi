"""Plan 02's hand-checked CZR expectations use the Model's ids (amendment A10).

Every CP-1 account expectation is read into registers of its own and must
come out on the Model line its metric feeds, on the column of its period, as
the line's figure or as CP-1's stated figure the line is compared with. Pro
forma expectations name a metric the PF-LTM adjusts, and every facility
expectation sits on a period the account expectations also use.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.registers import AccountRow, Cp1Registers, PeriodRow

EXPECTATIONS = Path(__file__).parents[1] / "corpus/expectations/czr-2026q2-primary.json"
LINE_OF = {
    "revenue": "revenue",
    "depreciation_amortization": "da",
    "adjusted_ebitda": "adjusted_ebitda",
    "cash_interest_paid": "cash_interest",
    "cash_and_equivalents": "cash_closing",
    "total_debt": "total_debt",
}
PF_METRICS = {"revenue", "ebitda", "adjusted_ebitda", "cash_interest_paid"}
PF_METRICS |= {"cash_and_equivalents", "total_debt"}


def _values(table: str) -> list[dict[str, Any]]:
    data = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
    return [v for v in data["values"] if v["table"] == table]


def _period(period_id: str) -> PeriodRow:
    """`FY<yyyy>` is the calendar year; `H1_<yyyy>` its first six months."""
    if period_id.startswith("FY"):
        year, quarter, kind, end = period_id[2:], None, "FY", "12-31"
    else:
        head, _, year = period_id.partition("_")
        assert head == "H1", period_id
        quarter, kind, end = "Q2", "YTD", "06-30"
    start = f"{year}-01-01"
    return PeriodRow(period_id, f"FY{year}", quarter, kind, start, f"{year}-{end}", None, "USD",
                     "MILLIONS", ())  # fmt: skip


def test_every_account_expectation_lands_on_its_model_line() -> None:
    expected = _values("cp1.model_account_register")
    assert len(expected) == 12
    pids = sorted({v["where"]["period_id"] for v in expected})
    accounts = tuple(
        AccountRow(v["where"]["metric_id"], v["where"]["period_id"], Decimal(v["value"]),
                   "VERIFIED", None)
        for v in expected
    )  # fmt: skip
    regs = Cp1Registers(
        tuple(_period(p) for p in pids), accounts, (), (), (), (), (), "USD", "MILLIONS"
    )
    model = credit_model(ModelInputs(regs))
    lines = {line.line_id: line for line in model.lines}
    for v in expected:
        line = lines[LINE_OF[v["where"]["metric_id"]]]
        index = next(
            n
            for n, c in enumerate(model.columns)
            if c.period_id == v["where"]["period_id"] and c.kind in {"FY", "YTD", "PYTD"}
        )
        cell = line.cells[index]
        shown = {abs(x) for x in (cell.value, cell.stated) if x is not None}
        assert abs(Decimal(v["value"])) in shown, v


def test_pro_forma_and_facility_expectations_use_model_ids() -> None:
    for v in _values("cp1.pro_forma_adjustment_register"):
        metric = v["where"]["metric_id"]
        assert metric in PF_METRICS or metric.startswith("facility:"), v
    interest = next(
        v
        for v in _values("cp1.pro_forma_adjustment_register")
        if v["where"]["metric_id"] == "cash_interest_paid"
    )
    assert Decimal(interest["value"]) < 0
    periods = {v["where"]["period_id"] for v in _values("cp1.model_account_register")}
    facilities = _values("cp1.debt_facility_register")
    assert len(facilities) == 6
    assert {v["where"]["period_id"] for v in facilities} <= periods


def _figures(excerpt: str) -> list[Decimal]:
    return [Decimal(f.strip().strip("$").replace(",", "")) for f in excerpt.split("|")[-3:]]


def test_carrying_values_are_book_never_face() -> None:
    """The debt notes cite `Face Value | Book Value | Book Value (prior)`: a
    carrying value (and CP-1's total debt) is the book value, never the face."""
    carried = [v for v in _values("cp1.debt_facility_register") if v["column"] == "carrying_value"]
    carried += [
        v for v in _values("cp1.model_account_register") if v["where"]["metric_id"] == "total_debt"
    ]
    assert len(carried) == 6
    for v in carried:
        face, book, _ = _figures(v["excerpt"])
        assert Decimal(v["value"]) == book != face, v
