"""Admitted-input regressions from the independent final review, 2026-10-12."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, handoff, run_brief, run_folder, table
from run_cases import DEBT_LIKE

from rbotlib.cli import main
from rbotlib.model.registers import Cp1Registers


def _execute(path: Path, regs: Cp1Registers, cp1d: str | None = None) -> dict[str, Any]:
    run = run_folder(path, cp1_handoff(regs), run_brief(), cp1d)
    assert main(["model", "--run", str(run)]) == 0
    data: dict[str, Any] = json.loads((run / "model.json").read_text())
    return data


def _memo(data: dict[str, Any]) -> dict[str, Any]:
    line = next(x for x in data["lines"] if x["line_id"] == "debt_like:pension_deficit")
    return next(c for c in line["cells"] if c["column_id"] == data["snapshot_columns"]["LTM"])


def test_period_end_debt_like_matches_the_ltm_balance_date(tmp_path: Path) -> None:
    regs = example_registers()
    ltm = next(p for p in regs.periods if p.period_id == "LTM_Q2_2026")
    balance = replace(
        ltm,
        period_id="BALANCE_2026_06_30",
        period_type="PERIOD_END",
        start_date=None,
        day_count=None,
        component_period_ids=(),
    )
    regs = replace(regs, periods=(*regs.periods, balance))
    outputs = []
    for period in (ltm.period_id, balance.period_id):
        row = [
            "Pension deficit",
            "120",
            "USD",
            "MILLIONS",
            period,
            "Debt-like",
            "unfunded obligation",
            "[C1]",
        ]
        cp1d = handoff(
            "CP-1D",
            [table("cp1d.debt_like_items", DEBT_LIKE, [row])],
            {"[C1]": ("pension.txt", "p.1", "120")},
        )
        data = _execute(tmp_path / period, regs, cp1d)
        assert data["house"]["adjusted_debt"]["value"] == "14826"
        assert data["house"]["adjusted_debt"]["components"] == [
            "total_debt",
            "debt_like:pension_deficit",
        ]
        assert _memo(data)["value"] == "120" and _memo(data)["reason"] is None
        assert "DEBT_LIKE_NOT_ON_SNAPSHOT" not in data["limitations"]
        outputs.append(data)
    assert outputs[0]["house"]["adjusted_debt"] == outputs[1]["house"]["adjusted_debt"]
    assert _memo(outputs[0]) == _memo(outputs[1])


@pytest.mark.parametrize("days", [184, 364, 371])
def test_dated_fy_has_the_same_annual_guard_without_day_count(tmp_path: Path, days: int) -> None:
    regs = example_registers()
    fy = next(p for p in regs.periods if p.period_id == "FY2025")
    start = (date(2025, 12, 31) - timedelta(days=days - 1)).isoformat()
    rows = {
        key: tuple(r for r in getattr(regs, key) if r.period_id == fy.period_id)
        for key in ("accounts", "addbacks", "segments", "kpis", "facilities")
    }
    outputs = []
    for count in (days, None):
        only = replace(
            regs,
            periods=(replace(fy, start_date=start, day_count=count),),
            pro_forma=(),
            accounts=rows["accounts"],
            addbacks=rows["addbacks"],
            segments=rows["segments"],
            kpis=rows["kpis"],
            facilities=rows["facilities"],
        )
        data = _execute(tmp_path / str(count), only)
        if days == 184:
            assert data["house"]["ssim_ebitda"]["reason"] == "COMPONENT_MISSING"
            assert data["house"]["ssim_multiple"]["reason"] == "NOT_APPLICABLE"
            assert data["house"]["ev"]["value"] is None
            assert "SNAPSHOT_NOT_TWELVE_MONTHS" in data["limitations"]
        else:
            assert data["house"]["ssim_ebitda"]["value"] is not None
            assert data["house"]["ssim_multiple"]["value"] is not None
            assert "SNAPSHOT_NOT_TWELVE_MONTHS" not in data["limitations"]
        outputs.append(data)
    assert outputs[0]["house"] == outputs[1]["house"]


def test_rolling_dated_fy_ytd_pytd_cannot_hide_a_short_span(tmp_path: Path) -> None:
    regs = example_registers()
    periods = tuple(
        replace(p, start_date="2025-07-01", day_count=184)
        if p.period_id == "FY2025"
        else replace(p, start_date="2025-07-01", end_date="2025-09-30", day_count=92)
        if p.period_id == "H1_2025"
        else p
        for p in regs.periods
        if p.period_type != "LTM"
    )
    allowed = {p.period_id for p in periods}
    rows = {
        key: tuple(r for r in getattr(regs, key) if r.period_id in allowed)
        for key in ("accounts", "addbacks", "segments", "kpis", "facilities")
    }
    outputs = []
    for omitted in (False, True):
        selected = tuple(replace(p, day_count=None) for p in periods) if omitted else periods
        data = _execute(
            tmp_path / str(omitted),
            replace(
                regs,
                periods=selected,
                pro_forma=(),
                accounts=rows["accounts"],
                addbacks=rows["addbacks"],
                segments=rows["segments"],
                kpis=rows["kpis"],
                facilities=rows["facilities"],
            ),
        )
        assert data["house"]["ssim_ebitda"]["reason"] == "COMPONENT_MISSING"
        assert data["house"]["ssim_multiple"]["reason"] == "NOT_APPLICABLE"
        assert "SNAPSHOT_NOT_TWELVE_MONTHS" in data["limitations"]
        outputs.append(data)
    assert outputs[0]["house"] == outputs[1]["house"]


def test_unrealized_adjustment_exactly_negates_the_admitted_derived_sum(tmp_path: Path) -> None:
    regs = example_registers()
    source = Decimal("999999999999999999.1234567891")
    addbacks = tuple(
        replace(b, value=source if b.period_id in ("FY2025", "H1_2026") else Decimal(0))
        if b.addback_id == "run_rate_cost_savings"
        else b
        for b in regs.addbacks
    )
    data = _execute(tmp_path, replace(regs, addbacks=addbacks))
    line = next(x for x in data["lines"] if x["line_id"] == "addback:run_rate_cost_savings")
    value = next(
        c["value"] for c in line["cells"] if c["column_id"] == data["snapshot_columns"]["LTM"]
    )
    assert value == "1999999999999999998.2469135782"
    rows = [r for r in data["ebitda_adjustments"] if "cost savings" in r["line"].casefold()]
    assert [r["amount"] for r in rows] == [value, "-1999999999999999998.2469135782"]
