"""Amendment A14: an add-back stated only for the LTM period counts (Structuring
EBITDA is every add-back the issuer markets) instead of reading `NOT_SOURCED`.

The CZR CP-1 fixture plus 150 of run-rate synergies on `LTM_Q2_2026` alone:
Structuring EBITDA 3,592 + 150 = 3,742; SSIM EBITDA stays 3,592 while the
synergies are unrealized and becomes 3,742 when they are realized."""

from __future__ import annotations

from pathlib import Path

import pytest
from model_handoffs import run_folder
from run_cases import _model

from rbotlib.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
ROW = (
    "| run_rate_synergies | Run-rate synergies | RUN_RATE | {status} | 4 | LTM_Q2_2026 | 150 "
    "| [C17] | Adjusted EBITDA reconciliation, run-rate |"
)
LAST = (
    "| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | H1_2026 |"
)


def _house(tmp_path: Path, status: str) -> dict[str, str]:
    cp1 = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
    lines = cp1.splitlines()
    at = next(n for n, line in enumerate(lines) if line.startswith(LAST))
    lines.insert(at + 1, ROW.format(status=status))
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, "\n".join(lines), brief)
    assert main(["model", "--run", str(run)]) == 0
    house = _model(run)["house"]
    return {k: house[k]["value"] for k in ("structuring_ebitda", "ssim_ebitda")}


@pytest.mark.parametrize(
    ("status", "structuring", "ssim"),
    [("UNREALIZED", "3742", "3592"), ("REALIZED", "3742", "3742")],
)
def test_an_ltm_only_add_back_counts(
    tmp_path: Path, status: str, structuring: str, ssim: str
) -> None:
    assert _house(tmp_path, status) == {"structuring_ebitda": structuring, "ssim_ebitda": ssim}
