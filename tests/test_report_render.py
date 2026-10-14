"""`render`: files, state fields, refusals and the `rbot render` command (Plan 07 task 07.6)."""

from __future__ import annotations

import copy
import hashlib
import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from report_run import complete_run

from rbotlib import state
from rbotlib.cli import main
from rbotlib.report import ReportError, run_json
from rbotlib.report import render as rr
from rbotlib.report.assets import Assets, load
from rbotlib.rules import RBOT_ROOT

Record = dict[str, Any]
T1 = "2026-10-14T00:00:00+00:00"
T2 = "2026-10-15T00:00:00+00:00"
KEPT = ("run-state.json", "handoffs/CP-5.md", "log/rbot.log")


@pytest.fixture(scope="module")
def finished(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Path:
    return complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))


@pytest.fixture
def run(finished: Path) -> Iterator[Path]:
    """The finished run for one test; its state, Handoff and log bytes return afterwards."""
    saved = {n: (finished / n).read_bytes() for n in KEPT if (finished / n).exists()}
    yield finished
    for name in (*KEPT, "report.md", "report.html"):
        (finished / name).unlink(missing_ok=True)
    for name, raw in saved.items():
        (finished / name).write_bytes(raw)


@pytest.fixture(autouse=True)
def placeholder_js(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """The shipped assets with a placeholder `report.js` (the real one arrives in 07.7)."""
    root = shutil.copytree(RBOT_ROOT / "report", tmp_path_factory.mktemp("assets") / "report")
    (root / "report.js").write_text("window.RBOT_REPORT = true;\n", encoding="utf-8")
    assets: Assets = load(root)
    monkeypatch.setattr(rr, "load_assets", lambda _root: assets)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(run: Path) -> int:
    log = run / "log/rbot.log"
    return len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0


def test_render_writes_files_and_state_fields(run: Path) -> None:
    before = state.read(run)
    after = rr.render(run, RBOT_ROOT, md_only=False, generated_at=T1)
    assert after["report"] == {
        "written_at": T1,
        "html_sha256": sha(run / "report.html"),
        "md_sha256": sha(run / "report.md"),
    }
    assert state.read(run) == after
    assert after["steps"] == before["steps"] and after["plan"] == before["plan"]


def test_md_only_sets_md_hash_only(run: Path) -> None:
    after = rr.render(run, RBOT_ROOT, md_only=True, generated_at=T1)
    assert not (run / "report.html").exists()
    assert after["report"] == {
        "written_at": None,
        "html_sha256": None,
        "md_sha256": sha(run / "report.md"),
    }


def test_render_is_rerunnable_and_idempotent_but_generated_at(run: Path) -> None:
    rr.render(run, RBOT_ROOT, md_only=False, generated_at=T1)
    first = {n: (run / n).read_text(encoding="utf-8") for n in ("report.md", "report.html")}
    again = rr.render(run, RBOT_ROOT, md_only=False, generated_at=T2)
    assert again["report"]["written_at"] == T2
    for name, text in first.items():
        now = (run / name).read_text(encoding="utf-8")
        assert now == text.replace(T1, T2) and T1 not in now


def served(run: Path, monkeypatch: pytest.MonkeyPatch, change: Callable[[Record], None]) -> None:
    """Serve the renderer a changed state record; state validation forbids storing it."""
    record = copy.deepcopy(state.read(run))
    change(record)
    monkeypatch.setattr(run_json, "_owned", lambda _run: record)


def unapproved(run: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    served(run, monkeypatch, lambda r: r.update(approval=None))


def non_terminal(run: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    served(run, monkeypatch, lambda r: r["steps"]["CP-6"].update(status="pending"))


def changed_handoff(run: Path, _monkeypatch: pytest.MonkeyPatch | None = None) -> None:
    path = run / "handoffs/CP-5.md"
    path.write_bytes(path.read_bytes() + b"\n")


@pytest.mark.parametrize("damage", [unapproved, non_terminal, changed_handoff])
def test_render_refuses_and_leaves_state_untouched(
    run: Path, monkeypatch: pytest.MonkeyPatch, damage: Callable[[Path, pytest.MonkeyPatch], None]
) -> None:
    damage(run, monkeypatch)
    saved, count = (run / "run-state.json").read_bytes(), rows(run)
    with pytest.raises(ReportError):
        rr.render(run, RBOT_ROOT, md_only=False, generated_at=T1)
    assert (run / "run-state.json").read_bytes() == saved
    assert rows(run) == count
    assert not (run / "report.md").exists() and not (run / "report.html").exists()


def test_render_logs_one_row(run: Path) -> None:
    count = rows(run)
    assert main(["--root", str(RBOT_ROOT), "render", "--run", str(run)]) == 0
    assert rows(run) == count + 1


def test_render_cli_exit_codes_and_summary_text(
    run: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = ["--root", str(RBOT_ROOT), "render", "--run", str(run)]
    assert main(args) == 0
    out = capsys.readouterr().out
    assert f"report.html: {run / 'report.html'}" in out
    assert f"report.md: {run / 'report.md'}" in out
    assert "Recommendation:" in out and "CLO: 3 - MW" in out
    assert "Limitations: " in out and "Blocked/failed/skipped: none" in out
    assert main([*args, "--md-only"]) == 0
    assert "report.html" not in capsys.readouterr().out
    changed_handoff(run)
    assert main(args) == 1
    err = capsys.readouterr().err
    assert err.startswith(f"error: {run}: handoffs/CP-5.md changed since acceptance")


def doc(**changes: Record) -> Record:
    base: Record = {
        "handoffs": {},
        "limitations": {"approval": [], "cp5": [], "unforeseen": []},
        "steps": {},
    }
    return base | changes


def test_summary_counts_limitations() -> None:
    lim = {
        "approval": [{"kind": "limitation", "text": "shown"}],
        "cp5": [{"limitation": "a"}, {"limitation": "b"}],
        "unforeseen": [
            {"kind": "failed", "step": "CP-3"},
            {"kind": "skipped", "step": "FIT"},
            {"kind": "blocked", "step": "CP-1D"},
            {"kind": "unanchored_citation", "ref": "CP-2:C1"},
        ],
    }
    steps = {
        "CP-3": {"status": "failed"},
        "FIT": {"status": "skipped"},
        "CP-1D": {"status": "blocked"},
        "CP-2": {"status": "accepted"},
    }
    got = rr.summary(doc(limitations=lim, steps=steps))
    assert got.splitlines() == [
        "no Recommendation in this Pathway",
        "Limitations: 4",
        "Blocked/failed/skipped: CP-3 (failed), FIT (skipped), CP-1D (blocked)",
    ]
    table = {"columns": ["strategy", "recommendation"], "rows": [["CLO", "3 - MW"]]}
    handoffs = {"CP-6": {"tables": {"snapshot.recommendation": table}}}
    got = rr.summary(doc(handoffs=handoffs))
    assert got.splitlines()[:2] == ["Recommendation:", "  CLO: 3 - MW"]
