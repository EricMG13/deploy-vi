"""`rbot-run/1` assembly and its refusals (Plan 07 task 07.2)."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from report_run import complete_run, save_fetched

from rbotlib import state
from rbotlib.report import ReportError, run_json
from rbotlib.rules import RBOT_ROOT

Record = dict[str, Any]
PLAN = [
    "CP-0",
    "CP-1",
    "CP-1A",
    "CP-DR",
    "CP-1B",
    "CP-1D",
    "MODEL",
    "CP-2",
    "CP-3",
    "FIT",
    "CP-5",
    "CP-6",
]
NOW = "2026-10-14T00:00:00+00:00"


@pytest.fixture(scope="module")
def finished(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Path:
    return complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))


@pytest.fixture
def patched(monkeypatch: pytest.MonkeyPatch, finished: Path) -> Callable[..., Record]:
    """Serve a changed copy of the run's state record; the run folder itself is untouched."""

    def make(change: Callable[[Record], None]) -> Record:
        record = copy.deepcopy(state.read(finished))
        change(record)
        monkeypatch.setattr(run_json, "_owned", lambda _run: record)
        return record

    return make


@pytest.fixture
def restored(finished: Path) -> Iterator[Callable[[str], Path]]:
    """Edit a run file in a test; its original bytes return afterwards."""
    saved: dict[Path, bytes] = {}

    def edit(relative: str) -> Path:
        path = finished / relative
        saved.setdefault(path, path.read_bytes())
        return path

    yield edit
    for path, raw in saved.items():
        path.write_bytes(raw)


@pytest.mark.corpus
def test_build_matches_schema_on_complete_fixture_run(finished: Path) -> None:
    first = run_json.build(finished, RBOT_ROOT, NOW)
    second = run_json.build(finished, RBOT_ROOT, "2026-10-15T00:00:00+00:00")
    assert first.pop("generated_at") != second.pop("generated_at")
    assert first == second
    assert first["schema"] == "rbot-run/1" and first["run_id"] == finished.name
    assert first["plan"] == PLAN and list(first["steps"]) == PLAN
    assert list(first["handoffs"]) == PLAN
    assert first["front_page"] == "credit_snapshot" and first["pathway"] == "FULL_CREDIT_ASSESSMENT"
    assert first["primary"] is True and first["prior_case"]["diff"] is None
    assert first["model"]["schema"] == "rbot-model/1" and first["fit"]
    assert "snapshot.run_header" in first["run_brief"]["tables"]
    assert first["modules"]["CP-1"]["tables"] and "MODEL" not in first["modules"]
    cp3 = first["handoffs"]["CP-3"]
    assert cp3["sha256"] == hashlib.sha256((finished / "handoffs/CP-3.md").read_bytes()).hexdigest()
    assert cp3["analysis_md"] and cp3["tables"]["cp3.talk_valuation"]["rows"]
    assert all(c["anchored"] is True for c in cp3["citations"])
    assert set(first["limitations"]) == {"approval", "cp5", "unforeseen"}
    assert first["limitations"]["cp5"]
    json.dumps(first, allow_nan=False)


@pytest.mark.corpus
def test_refuses_unapproved(finished: Path, patched: Callable[..., Record]) -> None:
    patched(lambda r: r.update(approval=None))
    with pytest.raises(ReportError, match="render requires Approval"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
@pytest.mark.parametrize("status", ["pending", "running"])
def test_refuses_non_terminal(finished: Path, patched: Callable[..., Record], status: str) -> None:
    patched(lambda r: r["steps"]["CP-6"].update(status=status))
    with pytest.raises(ReportError, match=r"every step terminal: \['CP-6'\]"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
def test_refuses_changed_handoff_bytes(finished: Path, restored: Callable[[str], Path]) -> None:
    path = restored("handoffs/CP-5.md")
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ReportError, match=r"handoffs/CP-5.md changed since acceptance"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
@pytest.mark.parametrize("damage", ["missing", "not_json", "schema"])
def test_refuses_missing_model_json_when_model_accepted(
    finished: Path, restored: Callable[[str], Path], damage: str
) -> None:
    path = restored("model.json")
    if damage == "missing":
        path.unlink()
    else:
        path.write_text("{" if damage == "not_json" else '{"schema": "rbot-model/2"}')
    with pytest.raises(ReportError, match=r"model\.json"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
def test_refuses_fit_without_a_portfolio_json(
    finished: Path, restored: Callable[[str], Path]
) -> None:
    path = restored("fit/TEST_CLO_I.json")
    path.unlink()
    with pytest.raises(ReportError, match=r"fit/TEST_CLO_I.json: missing"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
def test_refuses_unparseable_brief(finished: Path, restored: Callable[[str], Path]) -> None:
    restored("run-brief.md").write_text("no front matter\n")
    with pytest.raises(ReportError, match=r"run-brief\.md"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
def test_refuses_unparseable_handoff(
    finished: Path, patched: Callable[..., Record], restored: Callable[[str], Path]
) -> None:
    text = b"no front matter\n"
    restored("handoffs/CP-6.md").write_bytes(text)
    patched(lambda r: r["steps"]["CP-6"].update(sha256=hashlib.sha256(text).hexdigest()))
    with pytest.raises(ReportError, match=r"handoffs/CP-6.md: not a readable Handoff"):
        run_json.build(finished, RBOT_ROOT, NOW)


@pytest.mark.corpus
def test_failed_and_skipped_steps_carry_reason_only(
    finished: Path, patched: Callable[..., Record]
) -> None:
    def fail(record: Record) -> None:
        record["steps"]["CP-1B"] = {"kind": "module", "status": "failed", "reason": "no worker"}
        record["steps"]["CP-1D"] = {"kind": "module", "status": "skipped", "reason": "CP-1B failed"}

    patched(fail)
    built = run_json.build(finished, RBOT_ROOT, NOW)
    assert "CP-1B" not in built["handoffs"] and "CP-1D" not in built["handoffs"]
    assert built["steps"]["CP-1B"] == {"kind": "module", "status": "failed", "reason": "no worker"}
    unforeseen = built["limitations"]["unforeseen"]
    assert {"kind": "skipped", "step": "CP-1D", "reason": "CP-1B failed"} in unforeseen


@pytest.mark.parametrize(
    "validation,expected",
    [
        (
            {"exit": 1, "findings": [{"code": "citation_unanchored", "message": "C2: excerpt"}]},
            False,
        ),
        (
            {"exit": 1, "findings": [{"code": "source_unknown", "message": "'a.csv' is not in x"}]},
            False,
        ),
        ({"exit": 0, "findings": [{"code": "table_short", "message": "C2: rows"}]}, True),
        ({"exit": 0, "findings": []}, True),
        (None, None),
    ],
    ids=["unanchored", "source_unknown", "unrelated_finding", "found", "no_validation"],
)
def test_anchored_flags(validation: Record | None, expected: bool | None) -> None:
    assert run_json.anchored(validation, "C2", "a.csv") is expected
    assert run_json.anchored(validation, "C9") is (None if validation is None else True)


def test_public_step_strips_evidence_keys() -> None:
    step: Record = {
        "kind": "module",
        "status": "accepted",
        "qa_status": "Pass",
        "handoff": "handoffs/CP-1.md",
        "sha256": "0" * 64,
        "validate_exit": 0,
        "attempts": 1,
        "started_at": "a",
        "finished_at": "b",
        "reason": "",
        "model": "m",
        "note": "edited",
        "accept_history": [{"x": 1}],
        "current_edits": [{"y": 2}],
        "evidence": "QUJD",
        "host_execution": {"z": 3},
    }
    assert set(run_json.public_step(step)) == set(run_json.PUBLIC_STEP)
    assert len(run_json.PUBLIC_STEP) == 12


def test_blocked_handoff_embeds_gap_cells(tmp_path: Path) -> None:
    text = (
        "---\nmodule_id: CP-X\nrun_id: r\nqa_status: Blocked\n---\n\n## Analysis\n"
        "Cannot proceed.\n\n```\n## Not a section\n```\n\n## Tables\n\n"
        "<!-- table: x.t -->\n| a | b |\n|---|---|\n| — | — |\n\n## Gaps\n\n- No source.\n\n"
        "## Citations\n\n<!-- table: citations -->\n| id | source | locator | excerpt |\n"
        "|---|---|---|---|\n| C1 | s.txt | p. 1 | some text here |\n"
    )
    (tmp_path / "handoffs").mkdir()
    raw = text.encode()
    (tmp_path / "handoffs/CP-X.md").write_bytes(raw)
    step = {"status": "blocked", "qa_status": "Blocked", "sha256": hashlib.sha256(raw).hexdigest()}
    entry = run_json.handoff_entry(tmp_path, "CP-X", step, None)
    assert entry["tables"]["x.t"] == {"columns": ["a", "b"], "rows": [["—", "—"]]}
    assert entry["analysis_md"] == "Cannot proceed.\n\n```\n## Not a section\n```"
    assert entry["gaps_md"] == "- No source."
    assert entry["qa_status"] == "Blocked" and entry["status"] == "blocked"
    assert entry["citations"] == [
        {
            "id": "C1",
            "source": "s.txt",
            "locator": "p. 1",
            "excerpt": "some text here",
            "anchored": None,
        }
    ]


def test_refuses_a_folder_that_is_not_a_native_run(tmp_path: Path) -> None:
    run = tmp_path / "rbot-runs/20261014-x"
    run.mkdir(parents=True)
    with pytest.raises(ReportError, match=r"run-state\.json: missing"):
        run_json.build(run, RBOT_ROOT, NOW)
    with pytest.raises(ReportError, match="No such file"):
        run_json.build(tmp_path / "nowhere", RBOT_ROOT, NOW)


def _restricted_case() -> tuple[Record, Record]:
    record: Record = {
        "approval": {"limitations_shown": []},
        "steps": {n: {"status": "accepted"} for n in ("CP-2", "CP-5", "CP-6")},
    }
    handoffs: Record = {
        n: {"qa_status": "Restricted", "status": "accepted", "citations": []}
        for n in ("CP-2", "CP-5", "CP-6")
    }
    handoffs["CP-5"]["tables"] = {"cp5.limitations": {"columns": ["module_id"], "rows": [["CP-2"]]}}
    return record, handoffs


def test_restricted_step_no_one_names_is_listed_without_an_invented_reason() -> None:
    record, handoffs = _restricted_case()
    got = run_json.limitations(record, {}, handoffs, None, ["CP-5"])
    restricted = [x for x in got["unforeseen"] if x["kind"] == "restricted"]
    # CP-2 is named by a cp5 row and CP-5 by an Approval limited_module: only CP-6 is new.
    assert restricted == [{"kind": "restricted", "step": "CP-6"}]


def test_pass_handoff_is_not_listed_as_restricted() -> None:
    record, handoffs = _restricted_case()
    handoffs["CP-6"]["qa_status"] = "Pass"
    got = run_json.limitations(record, {}, handoffs, None)
    assert [x["step"] for x in got["unforeseen"] if x["kind"] == "restricted"] == ["CP-5"]


def test_anchored_ignores_findings_naming_another_citation_and_source() -> None:
    other = {
        "exit": 1,
        "findings": [
            {"code": "citation_unanchored", "message": "C3: excerpt"},
            {"code": "source_unknown", "message": "'b.csv' is not in x"},
        ],
    }
    assert run_json.anchored(other, "C2", "a.csv") is True


def test_fit_is_read_only_for_an_accepted_step(tmp_path: Path) -> None:
    from rbotlib.handoff import Handoff, Table

    (tmp_path / "fit").mkdir()
    (tmp_path / "fit/FUND.json").write_text('{"schema": "rbot-fit/1"}', encoding="utf-8")
    table = Table(["portfolio_id"], [["FUND"]])
    brief = Handoff({}, [], {"brief.portfolios": table}, [], [], "")
    assert run_json._fit(tmp_path, None, brief) == []
    assert run_json._fit(tmp_path, {"status": "failed"}, brief) == []
    assert run_json._fit(tmp_path, {"status": "accepted"}, brief) == [{"schema": "rbot-fit/1"}]


@pytest.fixture
def fetched_pages(finished: Path) -> Iterator[Path]:
    """One qualified page and one for an unticked question, removed after the test."""
    first = save_fetched(finished, "01-example.com.md", "https://example.com/a", "RQ-1")
    other = save_fetched(finished, "02-other.org.md", "https://other.org/b", "RQ-9")
    yield finished
    first.unlink()
    other.unlink()
    first.parent.rmdir()


@pytest.mark.corpus
def test_fetched_lists_each_qualified_file_and_omits_the_unqualified(
    finished: Path, fetched_pages: Path
) -> None:
    got = run_json.build(finished, RBOT_ROOT, NOW)["fetched"]
    assert got == [
        {
            "file": "fetched/01-example.com.md",
            "url": "https://example.com/a",
            "retrieved": "2026-10-10",
            "question": "RQ-1",
        }
    ]


@pytest.mark.corpus
def test_fetched_is_an_empty_list_for_a_pack_only_run(finished: Path) -> None:
    assert run_json.build(finished, RBOT_ROOT, NOW)["fetched"] == []
