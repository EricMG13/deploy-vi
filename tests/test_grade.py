from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import prepared_pack
from conftest import CORPUS
from cp0_fixture import Classification, cp0_handoff, registry_classification
from rbotlib.cli import main
from rbotlib.corpus import Pack
from rbotlib.grade import AVAILABLE as A
from rbotlib.grade import BLOCKED as B
from rbotlib.grade import LIMITED as L
from rbotlib.rules import Rules
from spec_fixture import SOURCES, build_tree

ACME = ("Acme Holdings, Inc.", "ACME")
FILES = {
    "acme_10k.txt": ("issuer", "Annual report", "Acme Holdings, Inc.", "Yes"),
    "acme_credit_agreement.txt": ("issuer", "Credit agreement", "Acme Holdings, Inc.", "Yes"),
    "levels.csv": ("market", "Market levels export", "Acme Holdings, Inc.", "Yes"),
}
SYNTHETIC = Path(__file__).parent / "corpus" / "synthetic" / "czr-2026q2-primary"
CLO = {
    "SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv": "Portfolio positions",
    "SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv": "Portfolio limits",
}


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


def _prepare(tmp_path: Path, files: dict[str, str], *, managed: bool = False) -> Path:
    content: dict[str, str | bytes] = dict(files)
    return prepared_pack(tmp_path, content, managed=managed)


def _graded(
    root: Path, run: Path, classes: Classification, *, primary: bool = False
) -> dict[str, Any]:
    (run / "handoffs").mkdir(exist_ok=True)
    text = cp0_handoff(run, ACME, "2026-10-02", classes, primary=primary)
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    grading: dict[str, Any] = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    return grading


def _depth(grading: dict[str, Any], pathway: str, depth: str) -> dict[str, Any]:
    entry = next(p for p in grading["pathways"] if p["id"] == pathway)
    graded: dict[str, Any] = entry["depths"][depth]
    return graded


def _acme(tmp_path: Path, extra: dict[str, str] | None = None, *, managed: bool = False) -> Path:
    files = {name: f"{name}: Acme Holdings, Inc. as of 2026-10-02\n" for name in FILES}
    return _prepare(tmp_path, files | (extra or {}), managed=managed)


def test_a_complete_pack_grades_available_except_where_fit_is_needed(
    root: Path, tmp_path: Path
) -> None:
    grading = _graded(root, _acme(tmp_path), FILES)
    full = _depth(grading, "FULL_CREDIT_ASSESSMENT", "full")
    assert full["status"] == "With limitations"
    assert (full["blocking_modules"], full["limited_modules"]) == ([], ["FIT"])
    assert full["limitations"] == ["FIT: no portfolio in the Portfolio Context"]
    assert full["lifting_sources"] == [
        "Portfolio positions and Portfolio limits (Portfolio Context)"
    ]
    decision = _depth(grading, "PORTFOLIO_DECISION", "quick")
    assert (decision["status"], decision["blocking_modules"]) == ("Blocked", ["FIT"])
    assert _depth(grading, "EARNINGS_UPDATE", "full")["status"] == "Available"
    assert _depth(grading, "RELATIVE_VALUE", "full")["status"] == "With limitations"
    by_id = {p["id"]: p["recommended_depth"] for p in grading["pathways"]}
    assert by_id["EARNINGS_UPDATE"] == "full" and by_id["PORTFOLIO_DECISION"] is None


def test_portfolio_context_lifts_fit(root: Path, tmp_path: Path) -> None:
    classes = dict(FILES)
    extra = {}
    for name, kind in CLO.items():
        classes[name] = ("portfolio", kind, "Test CLO I Ltd", "Yes")
        extra[name] = (SYNTHETIC / name).read_text(encoding="utf-8")
    grading = _graded(root, _acme(tmp_path, extra), classes)
    statuses = {
        (p["id"], d): g["status"] for p in grading["pathways"] for d, g in p["depths"].items()
    }
    assert set(statuses.values()) == {"Available"}


def test_a_misfiled_file_is_not_evidence(root: Path, tmp_path: Path) -> None:
    classes = FILES | {"acme_10k.txt": ("issuer", "Annual report", "Other Corp", "No")}
    grading = _graded(root, _acme(tmp_path), classes)
    assert grading["excluded_files"] == [
        {"file": "acme_10k.txt", "reason": "not about this issuer (names Other Corp)"}
    ]
    update = _depth(grading, "EARNINGS_UPDATE", "full")
    assert (update["status"], update["limited_modules"]) == ("With limitations", ["CP-1"])
    assert update["missing_document_types"] == [
        "Annual report",
        "Bond report",
        "Earnings release",
        "Quarterly report",
    ]


def test_no_issuer_source_blocks_the_model_and_names_the_cause(root: Path, tmp_path: Path) -> None:
    run = _prepare(tmp_path, {"levels.csv": "Acme levels\n"})
    grading = _graded(root, run, {"levels.csv": FILES["levels.csv"]})
    full = _depth(grading, "FULL_CREDIT_ASSESSMENT", "full")
    assert (full["status"], full["blocking_modules"]) == ("Blocked", ["CP-1", "MODEL"])
    assert "CP-2: needs CP-1, which cannot run" in full["limitations"]
    assert (
        "CP-1: no readable file about the issuer (Issuer Sources) in the Source Pack"
        in (full["limitations"])
    )


def test_the_menu_shows_every_pathway_and_the_approval_flags(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES, primary=True)
    out = capsys.readouterr().out
    assert "# Approval menu — Acme Holdings, Inc. (ACME), as of 2026-10-02" in out
    assert "| Earnings Update | full (recommended) | Available | — | — | — |" in out
    assert "| Portfolio Decision | quick | Blocked | FIT | — | Portfolio limits, Portfolio" in out
    assert "  - would lift: Portfolio positions and Portfolio limits (Portfolio Context)" in out
    assert "not pre-ticked: the Run Brief has no new tranche" in out
    assert "- `objective` is a gap" in out and "Fetch: Deep Research fetches" in out
    assert out.count("\n| ") == 13


def test_grading_is_deterministic_and_pins_its_inputs(root: Path, tmp_path: Path) -> None:
    run = _acme(tmp_path)
    first = _graded(root, run, FILES)
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    second = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    first.pop("graded_at")
    second.pop("graded_at")
    assert first == second
    assert first["run_id"] == "20261011-acme-pending" and len(first["brief_sha256"]) == 64


def test_the_shipped_catalog_grades_full_credit_assessment(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _acme(tmp_path)
    (run / "handoffs").mkdir()
    text = cp0_handoff(run, ACME, "2026-10-02", FILES, primary=False)
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["grade", "--run", str(run)]) == 0
    assert "| Full Credit Assessment | full (recommended) | With limitations | — | FIT |" in (
        capsys.readouterr().out
    )
    pathways = json.loads((run / "grading.json").read_text(encoding="utf-8"))["pathways"]
    assert [p["id"] for p in pathways] == ["FULL_CREDIT_ASSESSMENT"]


def test_grade_refuses_a_missing_or_invalid_input(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _acme(tmp_path)
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    assert "no run-brief.md; cp-start turn 1 writes it" in capsys.readouterr().out
    _graded(root, run, FILES)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(cp0.read_text(encoding="utf-8").replace("| Annual report |", "| 10-K |"))
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    assert "handoffs/CP-0.md does not validate (exit 2): off_scale" in capsys.readouterr().out
    (root / "modules" / "CP-1" / "MODULE.md").unlink()
    shutil.rmtree(root / "modules" / "CP-3")
    cp0.write_text(cp0.read_text(encoding="utf-8").replace("| 10-K |", "| Annual report |"))
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    assert "the RBOT folder does not check: ['CP-3'" in capsys.readouterr().out


def test_a_module_that_cannot_fill_an_unconditional_block_blocks(
    tmp_path: Path, rules: Rules
) -> None:
    """Decision 2 on a module's own table: CP-1A owns `snapshot.company_profile` (Credit
    Snapshot block 2, always shown) and needs a Rating report it cannot find."""
    sources = dict(SOURCES)
    need = {"sources": ["issuer"], "document_types": ["Rating report"], "required": True}
    sources["CP-1A"] = [need | {"why": "ratings"}]
    (tmp_path / "rbot").mkdir()
    root = build_tree(
        tmp_path / "rbot", rules, sources, tables={"CP-1A": ["snapshot.company_profile"]}
    )
    grading = _graded(root, _acme(tmp_path), FILES)
    full = _depth(grading, "FULL_CREDIT_ASSESSMENT", "full")
    assert (full["status"], full["blocking_modules"]) == ("Blocked", ["CP-1A"])
    assert "CP-1A: no Rating report (Issuer Sources) in the Source Pack" in full["limitations"]
    assert "CP-2: needs CP-1A, which cannot run" in full["limitations"]
    update = _depth(grading, "EARNINGS_UPDATE", "full")
    assert (update["status"], update["blocking_modules"]) == ("With limitations", [])


def test_grade_refuses_a_brief_built_from_another_cp0(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(cp0.read_text(encoding="utf-8").replace("Test fixture:", "Re-dispatched:"))
    capsys.readouterr()
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    assert "run-brief.md was built from another handoffs/CP-0.md; run rbot brief --from" in (
        capsys.readouterr().out
    )


BROKEN = [
    ("catalog.json", "{", "catalog.json is not readable"),
    ("catalog.json", "{}", "catalog.json is not readable: 'size_budget_bytes'"),
    ("modules/CP-0/contract.json", "{}", "modules/CP-0/contract.json is not readable"),
]


@pytest.mark.parametrize("case", BROKEN)
def test_grade_names_a_broken_rbot_folder(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], case: tuple[str, str, str]
) -> None:
    name, content, message = case
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    (root / name).write_text(content, encoding="utf-8")
    capsys.readouterr()
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    assert message in capsys.readouterr().out


def test_grading_pins_the_catalog_and_contracts(root: Path, tmp_path: Path) -> None:
    grading = _graded(root, _acme(tmp_path), FILES)
    assert (
        grading["catalog_sha256"]
        == hashlib.sha256((root / "catalog.json").read_bytes()).hexdigest()
    )
    assert len(grading["contracts_sha256"]) == 64


def _expected(pack: Pack, fit: str) -> set[str]:
    """Interfaces spec section 12.5 row 04: the grade a pack's `pathways[].fit` implies."""
    if fit in ("primary", "exercises"):
        return {"Available", "With limitations"}
    if any(t["kind"] == "missing_document_type" for t in pack.data["traps"]):
        return {"Blocked"}
    return {"Available", "With limitations"}


# Every graded (pack, Pathway, Depth) of the regression record: (grade, blocking, limited).
KNOWN = {
    ("czr-2026q2-primary", "FULL_CREDIT_ASSESSMENT", "full"): (A, [], []),
    ("czr-2026q2-primary", "PORTFOLIO_DECISION", "full"): (A, [], []),
    ("czr-2026q2-primary", "RELATIVE_VALUE", "full"): (A, [], []),
    ("czr-2026q2-full-credit-assessment", "FULL_CREDIT_ASSESSMENT", "full"): (L, [], ["FIT"]),
    ("czr-2026q2", "EARNINGS_UPDATE", "quick"): (A, [], []),
    ("czr-2026q2-earnings-update", "EARNINGS_UPDATE", "full"): (A, [], []),
    ("czr-2026q2-covenant-refinancing", "COVENANT_REFINANCING", "full"): (A, [], []),
    ("czr-2026q2-lite-covenant-refinancing", "COVENANT_REFINANCING", "quick"): (A, [], []),
    ("czr-2026q2-liquidity", "COVENANT_REFINANCING", "quick"): (A, [], []),
    ("czr-2026q2-lite-full-credit-screen", "FULL_CREDIT_ASSESSMENT", "quick"): (L, [], ["FIT"]),
    ("czr-2026q2-lite-portfolio", "PORTFOLIO_DECISION", "quick"): (A, [], []),  # A12
    ("czr-2026q2-lite-relative-value", "RELATIVE_VALUE", "quick"): (L, [], ["FIT"]),
    ("czr-2026q2-portfolio", "PORTFOLIO_DECISION", "full"): (A, [], []),  # A12
    ("czr-2026q2-relative-value", "RELATIVE_VALUE", "full"): (L, [], ["FIT"]),
    ("ccl-fy2025", "EARNINGS_UPDATE", "quick"): (A, [], []),
    ("ccl-fy2025-covenant-refinancing", "COVENANT_REFINANCING", "full"): (A, [], []),
    ("ccl-fy2025-earnings-update", "EARNINGS_UPDATE", "full"): (A, [], []),
    ("ccl-fy2025-full-relative-value", "RELATIVE_VALUE", "full"): (L, [], ["FIT"]),
    ("ccl-fy2025-liquidity", "COVENANT_REFINANCING", "quick"): (L, [], ["CP-4"]),
    ("ccl-fy2025-lite-covenant-refinancing", "COVENANT_REFINANCING", "quick"): (A, [], []),
    ("ccl-fy2025-lite-full-credit-screen", "FULL_CREDIT_ASSESSMENT", "quick"): (
        L,
        [],
        ["CP-3", "FIT"],
    ),
    ("ccl-fy2025-market-dislocation", "RELATIVE_VALUE", "quick"): (L, [], ["FIT"]),
    ("ccl-fy2025-portfolio", "PORTFOLIO_DECISION", "quick"): (B, ["FIT"], ["CP-3"]),
    ("ccl-fy2025-relative-value", "RELATIVE_VALUE", "quick"): (L, [], ["CP-3", "FIT"]),
    ("ba-fy2025", "EARNINGS_UPDATE", "quick"): (A, [], []),
    ("f-fy2025", "EARNINGS_UPDATE", "quick"): (A, [], []),
    ("save-2024-distressed-restructuring", "DISTRESSED_RESTRUCTURING", "full"): (
        L,
        [],
        ["CP-1", "CP-4", "CP-3", "FIT"],
    ),
    ("save-2024-lite-distressed-restructuring", "DISTRESSED_RESTRUCTURING", "quick"): (
        L,
        [],
        ["CP-1", "CP-4", "CP-3", "FIT"],
    ),
    ("vmo2-fy2025", "EARNINGS_UPDATE", "quick"): (A, [], []),
    ("vmo2-fy2025-deep-research", "EARNINGS_UPDATE", "quick"): (A, [], []),
    ("vmo2-fy2025-full-deep-research", "EARNINGS_UPDATE", "full"): (A, [], []),
    ("vmo2-fy2025-portfolio", "PORTFOLIO_DECISION", "quick"): (B, ["FIT"], ["CP-3"]),
    ("tid-ford", "COVENANT_REFINANCING", "full"): (L, [], ["CP-1"]),
    ("tid-six-flags", "COVENANT_REFINANCING", "full"): (L, [], ["CP-1"]),
    ("tid-vmo2-fy2025", "FULL_CREDIT_ASSESSMENT", "full"): (L, [], ["CP-4", "CP-3", "FIT"]),
    ("tid-vmo2-fy2025", "EARNINGS_UPDATE", "full"): (A, [], []),
    ("tid-vmo2-2026q1", "EARNINGS_UPDATE", "full"): (A, [], []),
}


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_grade_matches_expectations(
    pack_id: str,
    prepared_run: Callable[[str], Path],
    tmp_path: Path,
    rules: Rules,
) -> None:
    pack = CORPUS.pack(pack_id)
    run = tmp_path / "rbot-runs" / "20261011-grade-pending"
    shutil.copytree(prepared_run(pack_id), run)
    (tmp_path / "rbot").mkdir()
    root = build_tree(tmp_path / "rbot", rules, SOURCES)
    issuer = (pack.data["issuer"]["name"], pack.data["issuer"]["id"])
    classes = registry_classification(pack)
    (run / "handoffs").mkdir(exist_ok=True)
    text = cp0_handoff(run, issuer, pack.data["as_of"], classes, primary=pack.data["primary"])
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    grading = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    assert len(grading["pathways"]) == 6
    misfiled = {f for f, c in classes.items() if c[3] == "No"}
    assert {e["file"] for e in grading["excluded_files"]} >= misfiled
    for entry in pack.data["pathways"]:
        got = _depth(grading, entry["id"], entry["depth"])
        assert got["status"] in _expected(pack, entry["fit"]), (entry, got)
        expected = KNOWN[(pack_id, entry["id"], entry["depth"])]
        assert (got["status"], got["blocking_modules"], got["limited_modules"]) == expected
