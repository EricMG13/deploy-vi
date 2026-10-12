"""Grading Full Credit Assessment, full, with the real module contracts on every corpus pack.

Plan 04's grading rule (Decision 2) is provisional until the modules' own `document_types` and
`required` flags exist; these are Plan 05's. On each registry pack's hand-checked
classification (`tests/cp0_fixture.py`), the hand-checked grade follows from them: CP-1 needs
a readable Issuer Source and wants financial statements and a Market Levels or equity value
export; CP-1A wants a Market Context file for ratings; CP-3 wants a Market Levels export or
the Sector RV Workbook; FIT needs prepared positions and limits, but owns only the
conditional Portfolio Fit block, so a missing portfolio limits the grade rather than
blocking it. No pack is Blocked: every pack holds a readable Issuer Source about its issuer.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from conftest import CORPUS
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib.cli import main

# pack -> (status, blocking modules, limited modules) for FULL_CREDIT_ASSESSMENT full.
GRADES: dict[str, tuple[str, list[str], list[str]]] = {
    "czr-2026q2-primary": ("Available", [], []),
    "czr-2026q2-full-credit-assessment": ("With limitations", [], ["FIT"]),
    "czr-2026q2": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "czr-2026q2-earnings-update": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "czr-2026q2-covenant-refinancing": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "czr-2026q2-lite-covenant-refinancing": (
        "With limitations",
        [],
        ["CP-1", "CP-1A", "CP-3", "FIT"],
    ),
    "czr-2026q2-liquidity": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "czr-2026q2-lite-full-credit-screen": ("With limitations", [], ["FIT"]),
    "czr-2026q2-lite-portfolio": ("Available", [], []),
    "czr-2026q2-lite-relative-value": ("With limitations", [], ["FIT"]),
    "czr-2026q2-portfolio": ("Available", [], []),
    "czr-2026q2-relative-value": ("With limitations", [], ["FIT"]),
    "ccl-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "ccl-fy2025-covenant-refinancing": ("With limitations", [], ["FIT"]),
    "ccl-fy2025-earnings-update": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "ccl-fy2025-full-relative-value": ("With limitations", [], ["FIT"]),
    "ccl-fy2025-liquidity": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "ccl-fy2025-lite-covenant-refinancing": (
        "With limitations",
        [],
        ["CP-1", "CP-1A", "CP-3", "FIT"],
    ),
    "ccl-fy2025-lite-full-credit-screen": ("With limitations", [], ["CP-1", "CP-3", "FIT"]),
    "ccl-fy2025-market-dislocation": ("With limitations", [], ["FIT"]),
    "ccl-fy2025-portfolio": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "ccl-fy2025-relative-value": ("With limitations", [], ["CP-1", "CP-3", "FIT"]),
    "ba-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "f-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "save-2024-distressed-restructuring": (
        "With limitations",
        [],
        ["CP-1", "CP-1A", "CP-3", "FIT"],
    ),
    "save-2024-lite-distressed-restructuring": (
        "With limitations",
        [],
        ["CP-1", "CP-1A", "CP-3", "FIT"],
    ),
    "vmo2-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "vmo2-fy2025-deep-research": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "vmo2-fy2025-full-deep-research": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "vmo2-fy2025-portfolio": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "tid-ford": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "tid-six-flags": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "tid-vmo2-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "tid-vmo2-2026q1": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
}


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_full_credit_assessment_grades_on_the_corpus(
    pack_id: str, prepared_run: Callable[[str], Path], tmp_path: Path
) -> None:
    pack = CORPUS.pack(pack_id)
    run = tmp_path / "rbot-runs" / "20261011-grade-pending"
    shutil.copytree(prepared_run(pack_id), run)
    (run / "handoffs").mkdir(exist_ok=True)
    issuer = (pack.data["issuer"]["name"], pack.data["issuer"]["id"])
    classes = registry_classification(pack)
    text = cp0_handoff(run, issuer, pack.data["as_of"], classes, primary=pack.data["primary"])
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["grade", "--run", str(run)]) == 0
    grading = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    full = grading["pathways"][0]["depths"]["full"]
    assert (full["status"], full["blocking_modules"], full["limited_modules"]) == GRADES[pack_id]


def test_every_corpus_pack_has_a_hand_checked_grade() -> None:
    assert sorted(GRADES) == sorted(p.id for p in CORPUS.packs)
