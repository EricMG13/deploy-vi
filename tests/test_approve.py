from __future__ import annotations

import json
import shutil
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from state_receipt_assertions import outcome_bytes

import rbotlib.approve as ap
from builders import make_run
from conftest import FIXTURES, HANG_TIMEOUT
from rbotlib.approve import ApprovalError, new_name
from rbotlib.bootstrap import QualifiedCP0
from rbotlib.cli import main
from rbotlib.handoff import Handoff, parse
from rbotlib.rules import Rules
from rbotlib.validate import run_findings
from spec_fixture import SOURCES, build_tree
from test_grade import FILES, _acme, _graded

FCA_FULL = (
    "CP-0 CP-1 CP-1A CP-DR CP-1B CP-1D MODEL CP-1C CP-2 CP-2A CP-2E CP-4 CP-2D CP-2G "
    "PROJECTION CP-2H CP-3D CP-3C CP-4C CP-3 FIT CP-5 CP-6 CP-8"
).split()
QUESTION = "| RQ-1 | Is demand recovering? | Sets the Sector Outlook | CP-2 | Industry data |"
PRIOR = (
    "| old/report.html | 2026-07-15 | 20260715-acme-earnings-update"
    " | EARNINGS_UPDATE | full | Yes |"
)
OTHER = (
    "| old/other.html | 2026-07-15 | 20260715-zeta-earnings-update | EARNINGS_UPDATE | full | No |"
)
REPORT = (
    "<html><body><h1>RBOT Report</h1></body>"
    '<script type="application/json" id="rbot-run">{}</script></html>\n'
)
REPORTS = {"old/report.html": REPORT, "old/other.html": REPORT}
REPORT_CLASSES = {
    "old/report.html": ("issuer", "RBOT Report", "Acme Holdings, Inc.", "Yes"),
    "old/other.html": ("issuer", "RBOT Report", "Zeta Corp", "No"),
}


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


def _seed(run: Path) -> None:
    """The fixture started from a genuine fresh new-run allocation."""
    from rbotlib import state as rs

    assert "ownership" in rs.read(run)


def _ready(
    root: Path,
    tmp_path: Path,
    *,
    rows: str = "",
    tranche: bool = False,
    objective: bool = True,
) -> Path:
    """A graded Acme run with objective and analyst set; optionally a question with the
    Prior Case `rows` (the pack then holds two earlier RBOT Reports) and a new tranche."""
    run = _acme(tmp_path, REPORTS if rows else None, managed=True)
    _graded(root, run, FILES | (REPORT_CLASSES if rows else {}))
    if rows:
        cp0 = run / "handoffs" / "CP-0.md"
        text = cp0.read_text(encoding="utf-8")
        text = text.replace(
            "evidence_needed |\n|---|---|---|---|---|\n",
            f"evidence_needed |\n|---|---|---|---|---|\n{QUESTION}\n",
        )
        text = text.replace(
            "offered |\n|---|---|---|---|---|---|\n",
            f"offered |\n|---|---|---|---|---|---|\n{rows}\n",
        )
        cp0.write_text(text, encoding="utf-8")
        assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    edits = ["--set", "analyst=A. Analyst"] + (["--set", "objective=Annual review"] * objective)
    if tranche:
        edits += ["--set-tranche", "NEW-1", "instrument=Term Loan B"]
    assert main(["brief", "--run", str(run), *edits]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    _seed(run)
    return run


def _approve(root: Path, run: Path, *extra: str, pathway: str = "FULL_CREDIT_ASSESSMENT") -> int:
    argv = ["--root", str(root), "approve", "--run", str(run), "--pathway", pathway]
    return main([*argv, "--depth", "full", "--primary", "no", "--analyst", "B. Approver", *extra])


def _state(run: Path) -> dict[str, Any]:
    state: dict[str, Any] = json.loads((run / "run-state.json").read_text(encoding="utf-8"))
    return state


def _brief(run: Path) -> Handoff:
    return parse((run / "run-brief.md").read_text(encoding="utf-8"))


def test_approve_records_the_choice_and_renames_the_run(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    capsys.readouterr()
    assert _approve(root, run) == 0
    target = run.parent / "20261011-acme-full-credit-assessment"
    assert not run.exists() and target.is_dir()
    out = capsys.readouterr().out
    assert out.startswith(f"approved: {target}\n")
    assert "  1  CP-0        module  accepted\n" in out
    assert " 21  FIT         host    skipped (no portfolio context)\n" in out
    state = _state(target)
    assert state["run_id"] == target.name and state["plan"] == FCA_FULL
    assert (state["pathway"], state["depth"], state["primary"]) == (
        "FULL_CREDIT_ASSESSMENT",
        "full",
        False,
    )
    assert state["deep_research"] is False
    assert state["prior_case"] == {"offered": False, "accepted": False, "report": None}
    assert state["approval"]["pathway_grade"] == "With limitations"
    assert state["approval"]["limitations_shown"] == ["FIT: no portfolio in the Portfolio Context"]
    steps = state["steps"]
    assert steps["CP-0"]["status"] == "accepted" and steps["CP-0"]["qa_status"] == "Restricted"
    assert steps["CP-DR"] == {"kind": "module", "status": "skipped", "reason": "not approved"}
    assert steps["CP-8"]["reason"] == "no prior case" and steps["MODEL"]["kind"] == "host"
    assert steps["PROJECTION"]["status"] == "pending"
    h = _brief(target)
    approval = dict(
        zip(h.tables["brief.approval"].columns, h.tables["brief.approval"].rows[0], strict=True)
    )
    assert (approval["analyst"], approval["pathway_grade"], approval["primary"]) == (
        "B. Approver",
        "With limitations",
        "No",
    )
    assert h.front_matter["run_id"] == target.name and h.front_matter["qa_status"] == "Pass"
    header = dict(
        zip(
            h.tables["snapshot.run_header"].columns,
            h.tables["snapshot.run_header"].rows[0],
            strict=True,
        )
    )
    assert (header["run_id"], header["pathway"], header["depth"], header["analyst"]) == (
        target.name,
        "FULL_CREDIT_ASSESSMENT",
        "full",
        "B. Approver",
    )
    assert state["run_brief_sha256"] != approval["brief_sha256"]
    log = (target / "log" / "rbot.log").read_text(encoding="utf-8").splitlines()
    assert log[-1].endswith(
        f"approve --run {run} --pathway FULL_CREDIT_ASSESSMENT --depth full"
        " --primary no --analyst B. Approver\t0"
    )


def test_plan_prints_the_steps_after_approval(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    assert main(["plan", "--run", str(run)]) == 1
    assert "not approved yet" in capsys.readouterr().out
    _approve(root, run)
    target = run.parent / "20261011-acme-full-credit-assessment"
    capsys.readouterr()
    assert main(["plan", "--run", str(target)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == (
        "20261011-acme-full-credit-assessment: FULL_CREDIT_ASSESSMENT at full depth;"
        " Primary No, Deep Research No, Prior Case No"
    )
    assert len(lines) == 1 + len(FCA_FULL)
    assert lines[24] == " 24  CP-8        module  skipped (no prior case)"


def test_questions_prior_case_and_primary_follow_the_approval(root: Path, tmp_path: Path) -> None:
    run = _ready(root, tmp_path, rows=PRIOR, tranche=True)
    assert _approve(root, run, "--prior-case", "yes", "--primary", "yes") == 0
    target = run.parent / "20261011-acme-full-credit-assessment"
    state = _state(target)
    assert (state["primary"], state["deep_research"]) == (True, True)
    assert state["prior_case"] == {"offered": True, "accepted": True, "report": "old/report.html"}
    assert state["steps"]["CP-DR"]["status"] == "pending"
    assert state["steps"]["CP-8"]["status"] == "pending"
    h = _brief(target)
    assert h.tables["brief.prior_case"].rows[0][-1] == "Yes"
    assert h.tables["brief.research_questions"].rows[0][-1] == "Yes"
    fields = {r[0]: r[1:] for r in h.tables["brief.run_brief_fields"].rows}
    assert fields["primary"] == ["Yes", "Analyst-asserted", "Yes", "—"]


def test_an_unticked_question_switches_deep_research_off(root: Path, tmp_path: Path) -> None:
    run = _ready(root, tmp_path, rows=PRIOR)
    assert _approve(root, run, "--untick", "RQ-1") == 0
    state = _state(run.parent / "20261011-acme-full-credit-assessment")
    assert state["deep_research"] is False
    assert state["steps"]["CP-DR"]["reason"] == "not approved"
    assert state["steps"]["CP-8"]["reason"] == "no prior case"


def test_a_blocked_pathway_needs_the_acknowledgement(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    capsys.readouterr()
    argv = ["--root", str(root), "approve", "--run", str(run), "--pathway", "PORTFOLIO_DECISION"]
    argv += ["--depth", "quick", "--primary", "no", "--analyst", "B. Approver"]
    assert main(argv) == 1
    assert "PORTFOLIO_DECISION at quick depth is Blocked by FIT: FIT: no portfolio" in (
        capsys.readouterr().out
    )
    assert main([*argv, "--acknowledge-blocked"]) == 0
    state = _state(run.parent / "20261011-acme-portfolio-decision")
    assert state["approval"]["acknowledged_blocked_modules"] == ["FIT"]
    assert state["approval"]["pathway_grade"] == "Blocked"
    assert state["steps"]["FIT"]["reason"] == "no portfolio context"


REFUSALS = [
    (None, ["--pathway", "NOPE"], "unknown Pathway 'NOPE'; graded: FULL_CREDIT_ASSESSMENT"),
    ("objective", [], "the Run Brief still has gaps: objective"),
    ("brief", [], "run-brief.md changed after rbot grade; run rbot grade again"),
    ("run-state", [], "state must be an existing regular file"),
    ("grading", [], "grading.json; run rbot grade first"),
    (None, ["--primary", "yes"], "a Primary run needs a new tranche"),
    (None, ["--untick", "RQ-9"], "no research question RQ-9"),
    (None, ["--prior-case", "yes"], "no Prior Case was offered"),
]


@pytest.mark.parametrize("case", REFUSALS)
def test_refused_approvals_exit_1(
    root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    case: tuple[str | None, list[str], str],
) -> None:
    change, extra, message = case
    run = _ready(root, tmp_path, objective=change != "objective")
    if change == "brief":
        (run / "run-brief.md").write_text((run / "run-brief.md").read_text() + "\n")
    elif change in ("run-state", "grading"):
        (run / f"{change}.json").unlink()
    capsys.readouterr()
    assert _approve(root, run, *extra) == 1
    captured = capsys.readouterr()
    assert message in captured.out + captured.err
    assert run.is_dir()


def test_an_approved_brief_takes_no_edit_or_second_approval(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    _approve(root, run)
    target = run.parent / "20261011-acme-full-credit-assessment"
    capsys.readouterr()
    assert main(["brief", "--run", str(target), "--set", "objective=Other"]) == 1
    assert "run-brief.md was approved (FULL_CREDIT_ASSESSMENT at full depth on" in (
        capsys.readouterr().out
    )
    assert _approve(root, target) == 1
    assert "a changed Run Brief needs a new run" in capsys.readouterr().out


def test_the_new_name_counts_up_and_needs_a_pending_folder(tmp_path: Path) -> None:
    run = tmp_path / "20261011-acme-pending-2"
    (tmp_path / "20261011-acme-relative-value").mkdir()
    assert new_name(run, "ACME", "RELATIVE_VALUE").name == "20261011-acme-relative-value-2"
    assert new_name(run, "Six Flags/SIX", "EARNINGS_UPDATE").name == (
        "20261011-six-flags-six-earnings-update"
    )
    with pytest.raises(ApprovalError, match="not a pending run folder"):
        new_name(tmp_path / "acme", "ACME", "RELATIVE_VALUE")


@pytest.mark.corpus
def test_approval_on_the_primary_pack(
    prepared_run: Callable[[str], Path], tmp_path: Path, rules: Rules
) -> None:
    run = make_run(tmp_path, "20261011-czr-pending", managed=True)
    shutil.copytree(prepared_run("czr-2026q2-primary"), run, dirs_exist_ok=True)
    (tmp_path / "rbot").mkdir()
    root = build_tree(tmp_path / "rbot", rules, SOURCES)
    (run / "handoffs").mkdir(exist_ok=True)
    shutil.copy(FIXTURES / "handoffs" / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    edits = ["--set", "objective=New issue review", "--set", "analyst=A. Analyst"]
    assert main(["brief", "--run", str(run), *edits]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    grading = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    assert grading["primary_pretick"] is True and grading["tranches"] == ["NEW-1"]
    _seed(run)
    assert _approve(root, run, "--primary", "yes") == 0
    target = run.parent / "20261011-czr-full-credit-assessment"
    state = _state(target)
    assert state["approval"]["pathway_grade"] == "Available"
    assert {s: state["steps"][s]["status"] for s in ("CP-0", "CP-DR", "FIT", "CP-8")} == {
        "CP-0": "accepted",
        "CP-DR": "pending",
        "FIT": "pending",
        "CP-8": "skipped",
    }
    h = _brief(target)
    assert run_findings(h, target) == []
    assert h.tables["snapshot.transaction_summary"].rows[0][0] == "NEW-1"


TARGET = "20261011-acme-full-credit-assessment"


def test_a_failed_rename_leaves_the_run_unapproved_and_retryable(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    run = _ready(root, tmp_path)
    brief, state = (run / "run-brief.md").read_bytes(), outcome_bytes(run)

    def in_use(self: Path, target: object) -> Path:
        raise PermissionError(13, "The process cannot access the file", str(self))

    monkeypatch.setattr(Path, "rename", in_use)
    capsys.readouterr()
    assert _approve(root, run) == 1
    out = capsys.readouterr().out
    assert "could not rename the run folder" in out
    assert (
        "; nothing was approved: close any file open in the run folder and approve again\n" in out
    )
    monkeypatch.undo()
    assert (run / "run-brief.md").read_bytes() == brief
    assert outcome_bytes(run) == state
    assert sorted(p.name for p in run.iterdir() if p.name.startswith(".")) == [".approve.lock"]
    assert _approve(root, run) == 0
    assert (run.parent / TARGET / "run-state.json").is_file()


def test_a_concurrent_approve_is_refused_by_the_lock(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    run = _ready(root, tmp_path)
    inside, done = threading.Event(), threading.Event()
    real = ap._cp0_step

    def slow(run: Path, root: Path, rules: Rules) -> QualifiedCP0:
        inside.set()
        assert done.wait(HANG_TIMEOUT)
        return real(run, root, rules)

    monkeypatch.setattr(ap, "_cp0_step", slow)
    codes: dict[str, int] = {}
    first = threading.Thread(target=lambda: codes.update(fca=_approve(root, run)))
    first.start()
    assert inside.wait(HANG_TIMEOUT)
    codes["eu"] = _approve(root, run, pathway="EARNINGS_UPDATE")
    done.set()
    first.join()
    assert codes == {"fca": 0, "eu": 1}
    captured = capsys.readouterr()
    assert "holds this run" in captured.out + captured.err
    assert [p.name for p in run.parent.iterdir()] == [TARGET]
    state = _state(run.parent / TARGET)
    assert (state["pathway"], state["run_id"]) == ("FULL_CREDIT_ASSESSMENT", TARGET)
    assert (run.parent / TARGET / ".approve.lock").exists()


def test_a_report_cp0_did_not_offer_cannot_be_accepted(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path, rows=OTHER)
    capsys.readouterr()
    assert _approve(root, run, "--prior-case", "yes") == 1
    assert "no Prior Case was offered" in capsys.readouterr().out


def test_a_hand_edited_brief_is_refused(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path, rows=PRIOR)
    brief = run / "run-brief.md"
    row = "| RQ-1 | Is demand recovering? | CP-2 | Yes |\n"
    assert row in brief.read_text(encoding="utf-8")
    brief.write_text(brief.read_text(encoding="utf-8").replace(row, ""), encoding="utf-8")
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    capsys.readouterr()
    assert _approve(root, run) == 1
    assert "run-brief.md differs from the brief handoffs/CP-0.md and its edits give" in (
        capsys.readouterr().out
    )


@pytest.mark.parametrize(
    ("analyst", "message"),
    [("  ", "analyst is empty"), ("X\n## Gaps", "analyst holds a line break or control")],
)
def test_the_approving_analyst_is_checked(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], analyst: str, message: str
) -> None:
    run = _ready(root, tmp_path)
    argv = ["--root", str(root), "approve", "--run", str(run), "--pathway"]
    argv += ["FULL_CREDIT_ASSESSMENT", "--depth", "full", "--primary", "no", "--analyst", analyst]
    capsys.readouterr()
    assert main(argv) == 1
    captured = capsys.readouterr()
    assert message in captured.out + captured.err
    assert "brief.approval" not in (run / "run-brief.md").read_text(encoding="utf-8")


BAD_FILES = [
    ("grading.json", "{}", "grading.json is not a grading record"),
    ("grading.json", "[]", "grading.json is not a grading record"),
    ("run-state.json", "[]", "run-state.json: expected an object"),
    ("run-state.json", '{"steps": []}', "run-state.json.schema"),
]


@pytest.mark.parametrize("case", BAD_FILES)
def test_malformed_run_files_are_named(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], case: tuple[str, str, str]
) -> None:
    name, content, message = case
    run = _ready(root, tmp_path)
    (run / name).write_text(content, encoding="utf-8")
    capsys.readouterr()
    assert _approve(root, run) == 1
    captured = capsys.readouterr()
    assert message in captured.out + captured.err
    assert "brief.approval" not in (run / "run-brief.md").read_text(encoding="utf-8")


def test_a_grading_record_without_depths_is_named(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    grading = json.loads((run / "grading.json").read_text(encoding="utf-8"))
    grading["pathways"] = [{"id": "FULL_CREDIT_ASSESSMENT"}]
    (run / "grading.json").write_text(json.dumps(grading), encoding="utf-8")
    capsys.readouterr()
    assert _approve(root, run) == 1
    assert "grading.json is not a grading record (pathway FULL_CREDIT_ASSESSMENT" in (
        capsys.readouterr().out
    )


def test_plan_names_an_incomplete_state(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "run-state.json").write_text('{"plan": ["CP-0"], "steps": {}}', encoding="utf-8")
    assert main(["plan", "--run", str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "inside pack/rbot-runs" in captured.out + captured.err
    assert (tmp_path / "run-state.json").read_text() == '{"plan": ["CP-0"], "steps": {}}'
    assert not (tmp_path / "log").exists()


def test_a_cp0_that_no_longer_validates_is_refused(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    index = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
    index["files"][0]["sha256"] = "0" * 64
    (run / "prepared" / "index.json").write_text(json.dumps(index), encoding="utf-8")
    capsys.readouterr()
    assert _approve(root, run) == 1
    assert "handoffs/CP-0.md no longer validates (exit 2); run rbot grade" in (
        capsys.readouterr().out
    )


def test_a_catalog_change_after_grading_is_refused(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    update = next(p for p in catalog["pathways"] if p["id"] == "EARNINGS_UPDATE")
    update["depths"]["full"].insert(-2, "CP-4")
    (root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
    capsys.readouterr()
    assert _approve(root, run, pathway="EARNINGS_UPDATE") == 1
    assert "the catalog or a module contract changed after rbot grade" in capsys.readouterr().out


def test_grade_refuses_an_approved_run(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _ready(root, tmp_path)
    _approve(root, run)
    graded = (run.parent / TARGET / "grading.json").read_bytes()
    capsys.readouterr()
    assert main(["--root", str(root), "grade", "--run", str(run.parent / TARGET)]) == 1
    assert "run-brief.md was approved" in capsys.readouterr().out
    assert (run.parent / TARGET / "grading.json").read_bytes() == graded


def test_unapproved_analysis_steps_cannot_be_carried_into_approval(
    root: Path, tmp_path: Path
) -> None:
    run = _ready(root, tmp_path)
    state = _state(run)
    state["steps"]["FIT"] = {"kind": "host", "status": "accepted", "reason": ""}
    (run / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    original = outcome_bytes(run)
    assert _approve(root, run) == 1
    assert outcome_bytes(run) == original


def test_an_issuer_id_without_a_slug_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ApprovalError, match="issuer_id '株式' gives no folder name"):
        new_name(tmp_path / "20261011-x-pending", "株式", "RELATIVE_VALUE")


@pytest.mark.parametrize("damaged", ["brief", "cp0"])
def test_readback_refuses_when_only_one_published_file_differs(
    root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    damaged: str,
) -> None:
    from rbotlib import brief as rb
    from rbotlib import state as rs
    from rbotlib.inventory import output_path

    run = _ready(root, tmp_path)
    real = rs.read

    def read_then_damage(path: Path) -> dict[str, Any]:
        record = real(path)
        if path.name == TARGET:
            name = path / rb.BRIEF if damaged == "brief" else output_path(path, rb.CP0)
            name.write_bytes(name.read_bytes() + b"\ndamaged after publication\n")
        return record

    monkeypatch.setattr(rs, "read", read_then_damage)
    capsys.readouterr()
    assert _approve(root, run) == 1
    assert "Approval readback differs" in capsys.readouterr().out
