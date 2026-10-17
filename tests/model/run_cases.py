"""Run folders and CP-1D Handoffs shared by the `rbot model` tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, handoff, run_brief, run_folder, table

from rbotlib.model.registers import Cp1Registers

CP1D_COLUMNS = ["addback_id", "period_id", "amount", "currency", "unit", "category"]
CP1D_COLUMNS += ["house_realization_status", "verdict", "rationale", "recurrence", "cite"]
DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]


def cp1d_handoff() -> str:
    """A CP-1D Handoff: restructuring Rejected, a 120 pension deficit Debt-like."""
    assessed = ["restructuring", "LTM_Q2_2026", "32", "USD", "MILLIONS", "Restructuring"]
    assessed += ["REALIZED", "Rejected", "recurring every year", "Yes", "[C1]"]
    pension = ["Pension deficit", "120", "USD", "MILLIONS", "LTM_Q2_2026", "Debt-like"]
    pension += ["unfunded obligation", "[C2]"]
    blocks = [
        table("cp1d.addback_assessment", CP1D_COLUMNS, [assessed]),
        table("cp1d.debt_like_items", DEBT_LIKE, [pension]),
    ]
    citations = {
        "[C1]": ("10-K.txt", "p.70", "restructuring charges recur"),
        "[C2]": ("10-K.txt", "p.95", "pension deficit of $120 million"),
    }
    return handoff("CP-1D", blocks, citations)


def _run(tmp_path: Path, regs: Cp1Registers | None = None, cp1d: str | None = None) -> Path:
    return run_folder(tmp_path, cp1_handoff(regs or example_registers()), run_brief(), cp1d)


def _model(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "model.json").read_text(encoding="utf-8"))
    return data
