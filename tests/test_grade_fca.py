"""Grading Full Credit Assessment, full, with the real module contracts on every corpus pack.

Plan 04's grading rule (Decision 2) is provisional until the modules' own `document_types` and
`required` flags exist; these are Plan 05's. On each registry pack's hand-checked
classification (`tests/cp0_fixture.py`), the hand-checked grade follows from them: CP-1 needs
a financial statement (an annual or quarterly report, an earnings release, a bond report, an
offering memorandum or a lender presentation) and wants a Market Levels or equity value
export; CP-1A wants a rating report or a Market Levels export for ratings; CP-3 wants a
Market Levels export or the Sector RV Workbook; FIT needs prepared positions and limits, but
owns only the conditional Portfolio Fit block, so a missing portfolio limits the grade rather
than blocking it. The Model needs CP-1, so a pack with no financial statement is Blocked:
`tid-ford` (a Ford credit agreement; its 10-K is a mis-filed Six Flags document),
`tid-six-flags` (the mirror case) and the two `save-2024` packs (an 8-K and a restructuring
support agreement, both `Other`). Every other pack holds one.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
from test_accept import accept, send
from test_bootstrap import ready

from conftest import CORPUS
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib import state
from rbotlib.catalog import load_catalog
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT

# pack -> (status, blocking modules, limited modules) for FULL_CREDIT_ASSESSMENT full.
NO_STATEMENTS = (
    "Blocked",
    ["CP-1", "CP-1B", "MODEL", "CP-2", "CP-3", "CP-6"],
    ["CP-1A", "CP-1D", "CP-1C", "CP-2A", "CP-2E", "CP-4", "CP-2D", "FIT"],
)
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
    "ccl-fy2025-relative-value": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "ba-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "f-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "save-2024-distressed-restructuring": NO_STATEMENTS,
    "save-2024-lite-distressed-restructuring": NO_STATEMENTS,
    "vmo2-fy2025": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "vmo2-fy2025-deep-research": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "vmo2-fy2025-full-deep-research": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "vmo2-fy2025-portfolio": ("With limitations", [], ["CP-1", "CP-1A", "CP-3", "FIT"]),
    "tid-ford": NO_STATEMENTS,
    "tid-six-flags": NO_STATEMENTS,
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


# pack -> (status, blocking modules, limited modules) for FULL_CREDIT_ASSESSMENT quick, the
# KNOWN values of tests/test_grade.py, except ccl: the real contracts also limit CP-1 there (as
# at full, above; the synthetic KNOWN tree has no such limit). CP-L10 adds no limit of its own.
QUICK_GRADES: dict[str, tuple[str, list[str], list[str]]] = {
    "czr-2026q2-lite-full-credit-screen": ("With limitations", [], ["FIT"]),
    "ccl-fy2025-lite-full-credit-screen": ("With limitations", [], ["CP-1", "CP-3", "FIT"]),
}


def _briefed(pack_id: str, prepared_run: Callable[[str], Path], tmp_path: Path) -> Path:
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
    return run


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", sorted(QUICK_GRADES))
def test_full_credit_assessment_grades_at_quick_on_the_corpus(
    pack_id: str, prepared_run: Callable[[str], Path], tmp_path: Path
) -> None:
    run = _briefed(pack_id, prepared_run, tmp_path)
    grading = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    quick = grading["pathways"][0]["depths"]["quick"]
    got = (quick["status"], quick["blocking_modules"], quick["limited_modules"])
    assert got == QUICK_GRADES[pack_id]


@pytest.mark.corpus
def test_approve_at_quick_plans_the_committed_quick_list(
    corpus_pack: Callable[[str], Path], tmp_path: Path
) -> None:
    pack = shutil.copytree(
        corpus_pack("czr-2026q2-lite-full-credit-screen"),
        tmp_path / "working pack",
        ignore=shutil.ignore_patterns("rbot-runs"),
    )
    assert main(["new-run", "--pack", str(pack)]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    (run / "handoffs").mkdir()
    cp0 = CORPUS.pack("czr-2026q2-lite-full-credit-screen")
    issuer = (cp0.data["issuer"]["name"], cp0.data["issuer"]["id"])
    text = cp0_handoff(
        run, issuer, cp0.data["as_of"], registry_classification(cp0), primary=cp0.data["primary"]
    )
    (run / "handoffs/CP-0.md").write_text(text, encoding="utf-8")
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    args = ["--root", str(RBOT_ROOT), "approve", "--run", str(run)]
    args += ["--pathway", "FULL_CREDIT_ASSESSMENT", "--depth", "quick"]
    args += ["--primary", "no", "--analyst", "Approver"]
    assert main(args) == 0
    plan = state.read(next(run.parent.iterdir()))["plan"]
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    assert plan == list(pathway.depths["quick"])
    assert "CP-L10" in plan and "CP-2" not in plan
