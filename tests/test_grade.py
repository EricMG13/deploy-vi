from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import make_run
from conftest import CORPUS
from cp0_fixture import Classification, cp0_handoff, registry_classification
from rbotlib.cli import main
from rbotlib.corpus import Pack
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


def _prepare(tmp_path: Path, files: dict[str, str]) -> Path:
    pack = tmp_path / "pack"
    pack.mkdir()
    for name, text in files.items():
        (pack / name).write_text(text, encoding="utf-8")
    run = make_run(pack, "20261011-acme-pending")
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run


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


def _acme(tmp_path: Path, extra: dict[str, str] | None = None) -> Path:
    files = {name: f"{name}: Acme Holdings, Inc. as of 2026-10-02\n" for name in FILES}
    return _prepare(tmp_path, files | (extra or {}))


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


def test_the_shipped_catalog_grades_nothing_yet(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _acme(tmp_path)
    (run / "handoffs").mkdir()
    text = cp0_handoff(run, ACME, "2026-10-02", FILES, primary=False)
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["grade", "--run", str(run)]) == 0
    assert "The catalog lists no Pathway yet, so nothing can be approved." in (
        capsys.readouterr().out
    )
    assert json.loads((run / "grading.json").read_text(encoding="utf-8"))["pathways"] == []


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


def _expected(pack: Pack, fit: str) -> set[str]:
    """Interfaces spec section 12.5 row 04: the grade a pack's `pathways[].fit` implies."""
    if fit in ("primary", "exercises"):
        return {"Available", "With limitations"}
    if any(t["kind"] == "missing_document_type" for t in pack.data["traps"]):
        return {"Blocked"}
    return {"Available", "With limitations"}


# Hand-checked grades: (pack, Pathway, Depth) -> (status, blocking, limited).
KNOWN = {
    ("czr-2026q2-primary", "FULL_CREDIT_ASSESSMENT", "full"): ("Available", [], []),
    ("czr-2026q2-primary", "PORTFOLIO_DECISION", "full"): ("Available", [], []),
    ("ccl-fy2025-portfolio", "PORTFOLIO_DECISION", "quick"): ("Blocked", ["FIT"], ["CP-3"]),
    ("vmo2-fy2025-portfolio", "PORTFOLIO_DECISION", "quick"): ("Blocked", ["FIT"], ["CP-3"]),
    ("tid-ford", "COVENANT_REFINANCING", "full"): ("With limitations", [], ["CP-1"]),
    ("tid-six-flags", "COVENANT_REFINANCING", "full"): ("With limitations", [], ["CP-1"]),
    ("save-2024-distressed-restructuring", "DISTRESSED_RESTRUCTURING", "full"): (
        "With limitations",
        [],
        ["CP-1", "CP-4", "CP-3", "FIT"],
    ),
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
        known = KNOWN.get((pack_id, entry["id"], entry["depth"]))
        if known:
            assert (got["status"], got["blocking_modules"], got["limited_modules"]) == known
