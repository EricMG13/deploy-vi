"""The registered synthetic150 source, added to the filing-only CZR input for A14."""

from pathlib import Path

from model_handoffs import handoff, table
from run_cases import CP1D_COLUMNS

FIXTURES = Path(__file__).parent / "fixtures"
SOURCE = "SYNTHETIC_CZR_2026_PF_Capitalisation.md"
EXCERPT = "Run-rate cost synergies identified by Fertitta Entertainment, not yet realised | 150"


def czr_with_synergies() -> str:
    cp1 = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
    anchor = "<!-- table: cp1.debt_facility_register -->"
    row = (
        "| run_rate_synergies | Run-rate cost synergies | RUN_RATE | UNREALIZED | 4 "
        "| LTM_Q2_2026 | 150 | [C34] | Earnings and interest |\n\n"
    )
    cp1 = cp1.replace("\n\n" + anchor, "\n" + row + anchor, 1)
    escaped = EXCERPT.replace("|", "\\|")
    return cp1 + f"| C34 | {SOURCE} | Earnings and interest | {escaped} |\n"


def synergy_assessment(status: str, verdict: str) -> str:
    row = ["run_rate_synergies", "LTM_Q2_2026", "150", "USD", "MILLIONS", "Synergies"]
    row += [
        status,
        verdict,
        "current registered-LTM judgment for the A14 control",
        "LTM only",
        "[C1]",
    ]
    return handoff(
        "CP-1D",
        [table("cp1d.addback_assessment", CP1D_COLUMNS, [row])],
        {"[C1]": (SOURCE, "Earnings and interest", EXCERPT.replace("|", "\\|"))},
    )
