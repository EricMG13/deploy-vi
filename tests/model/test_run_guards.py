"""`rbot model`'s input and output guards (up-front review of the non-money
modules, 2026-10-11): each test fails on `run.py` before its fix."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, handoff, run_brief, run_folder, table
from run_cases import CP1D_COLUMNS, _model, _run

import rbotlib.model.run as run_module
from rbotlib.cli import main

OUTPUTS = ("model.json", "handoffs/MODEL.md")


def _error(capsys: pytest.CaptureFixture[str]) -> str:
    captured = capsys.readouterr()
    assert captured.out == ""
    return captured.err


def _snapshot(run: Path) -> dict[str, bytes | None]:
    return {n: (run / n).read_bytes() if (run / n).is_file() else None for n in OUTPUTS}


def _separator_broken(text: str, table_id: str) -> str:
    lines = text.splitlines()
    at = next(n for n, line in enumerate(lines) if line == f"<!-- table: {table_id} -->")
    sep = next(n for n in range(at, len(lines)) if lines[n].startswith("|---"))
    lines[sep] = lines[sep].replace("|---|", "|-- -|", 1)
    return "\n".join(lines)


def _table_twice(text: str, table_id: str) -> str:
    lines = text.splitlines()
    at = next(n for n, line in enumerate(lines) if line == f"<!-- table: {table_id} -->")
    end = next(n for n in range(at + 4, len(lines)) if not lines[n].startswith("|"))
    return "\n".join([*lines[:end], "", *lines[at:end], *lines[end:]])


@pytest.mark.parametrize("table_id", ["cp1.debt_facility_register", "cp1.model_account_register"])
def test_a_malformed_cp1_table_is_refused_not_read_as_no_rows(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], table_id: str
) -> None:
    # C1: the orphaned tag read as "no rows" and the run exited 0 with qa_status Pass.
    text = _separator_broken(cp1_handoff(example_registers()), table_id)
    run = run_folder(tmp_path, text, run_brief())
    assert main(["model", "--run", str(run)]) == 1
    assert f"model: CP-1.md: table {table_id} is tagged but malformed" in _error(capsys)
    assert _snapshot(run) == {n: None for n in OUTPUTS}


def test_a_cp1_table_tagged_twice_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = _table_twice(cp1_handoff(example_registers()), "cp1.model_account_register")
    run = run_folder(tmp_path, text, run_brief())
    assert main(["model", "--run", str(run)]) == 1
    assert "model: CP-1.md: table cp1.model_account_register tagged twice" in _error(capsys)
    assert _snapshot(run) == {n: None for n in OUTPUTS}


def test_a_malformed_run_brief_table_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    brief = _separator_broken(run_brief(), "snapshot.run_header")
    run = run_folder(tmp_path, cp1_handoff(example_registers()), brief)
    assert main(["model", "--run", str(run)]) == 1
    assert "model: run-brief.md: table snapshot.run_header is tagged but malformed" in _error(
        capsys
    )


def test_a_table_id_outside_the_handoff_alphabet_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = cp1_handoff(example_registers()).replace(
        "<!-- table: cp1.model_account_register -->", "<!-- table: cp1.model account -->"
    )
    run = run_folder(tmp_path, text, run_brief())
    assert main(["model", "--run", str(run)]) == 1
    assert "table cp1.model account is tagged but malformed" in _error(capsys)


def test_an_unreadable_handoff_exits_1_naming_the_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # I3: UnicodeDecodeError was a traceback.
    run = _run(tmp_path)
    with (run / "handoffs" / "CP-1.md").open("ab") as handle:
        handle.write(b"\xff\xfe")
    assert main(["model", "--run", str(run)]) == 1
    assert _error(capsys).startswith("model: CP-1.md: ")
    (run / "handoffs" / "CP-1.md").unlink()
    (run / "handoffs" / "CP-1.md").mkdir()
    assert main(["model", "--run", str(run)]) == 1
    assert _error(capsys).startswith("model: CP-1.md: ")


def test_a_control_character_in_cp1_exits_1_before_anything_is_written(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # I3: openpyxl's IllegalCharacterError was a traceback after model.json was written.
    text = cp1_handoff(example_registers()).replace("Term loan B", "Term\x01loan B", 1)
    assert "\x01" in text
    run = run_folder(tmp_path, text, run_brief())
    assert main(["model", "--run", str(run)]) == 1
    assert "control character" in _error(capsys)
    assert _snapshot(run) == {n: None for n in OUTPUTS}


def test_an_unwritable_output_exits_1_and_leaves_the_others_as_they_were(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Required outputs are preflighted before any publication.
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    capsys.readouterr()
    before = {"model.json": (run / "model.json").read_bytes()}
    (run / "handoffs/MODEL.md").unlink()
    (run / "handoffs/MODEL.md").mkdir()
    (run / "handoffs" / "CP-1.md").write_text(
        cp1_handoff(example_registers()).replace("| 11519 |", "| 11518 |", 1), encoding="utf-8"
    )
    assert main(["model", "--run", str(run)]) == 1
    assert _error(capsys).startswith("model: cannot write ")
    assert {n: (run / n).read_bytes() for n in before} == before
    assert sorted(p.name for p in run.iterdir() if p.name.startswith(".")) == []
    assert sorted(p.name for p in (run / "handoffs").iterdir() if p.name.startswith(".")) == []


def test_a_failure_staging_the_last_file_replaces_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    capsys.readouterr()
    before = _snapshot(run)
    stage = run_module.stage_file
    calls = []

    def failing(target: Path, data: bytes) -> Path:
        calls.append(target.name)
        if len(calls) == 2:
            raise OSError("disk full")
        return stage(target, data)

    monkeypatch.setattr(run_module, "stage_file", failing)
    (run / "handoffs" / "CP-1.md").write_text(
        cp1_handoff(example_registers()).replace("| 11519 |", "| 11518 |", 1), encoding="utf-8"
    )
    assert main(["model", "--run", str(run)]) == 1
    assert _error(capsys) == "model: cannot write the outputs: disk full\n"
    assert len(calls) == 2
    assert _snapshot(run) == before


def test_a_symlinked_output_is_replaced_not_followed(tmp_path: Path) -> None:
    # I2: the Model was written through the link to a file outside the run.
    victim = tmp_path / "elsewhere" / "victim.json"
    victim.parent.mkdir()
    victim.write_text("keep me", encoding="utf-8")
    run = _run(tmp_path / "r")
    (run / "model.json").symlink_to(victim)
    assert main(["model", "--run", str(run)]) == 0
    assert victim.read_text(encoding="utf-8") == "keep me"
    assert not (run / "model.json").is_symlink()
    assert json.loads((run / "model.json").read_text(encoding="utf-8"))["schema"]


def test_a_handoffs_folder_that_leaves_the_run_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path / "r")
    outside = tmp_path / "elsewhere"
    (run / "handoffs").rename(outside)
    (run / "handoffs").symlink_to(outside)
    assert main(["model", "--run", str(run)]) == 1
    assert "model: handoffs resolves outside the run folder" in _error(capsys)
    assert not (outside / "MODEL.md").exists() and not (run / "model.json").exists()


def test_a_malformed_input_is_reported_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # M6: cli._fail writes to stderr; the Model wrote to stdout.
    run = run_folder(tmp_path, "no front matter", run_brief())
    assert main(["model", "--run", str(run)]) == 1
    assert _error(capsys).startswith("model: CP-1.md: missing front matter")


def test_a_figure_without_a_citation_is_a_limitation(tmp_path: Path) -> None:
    # I10: the cell had `sources: []` and nothing said so.
    text = cp1_handoff(example_registers())
    lines = text.splitlines()
    at = next(n for n, line in enumerate(lines) if "| revenue | FY2025 |" in line)
    lines[at] = lines[at].replace("[C3]", "—")
    run = run_folder(tmp_path, "\n".join(lines), run_brief())
    assert main(["model", "--run", str(run)]) == 0
    found = [x for x in _model(run)["limitation_details"] if x["code"] == "UNCITED_FIGURE"]
    revenue = [x for x in found if x["line_id"] == "revenue"]
    assert [x["message"] for x in revenue] == [
        "Total revenue: no cited source for the figure on FY:FY2025"
    ]


def test_an_account_metric_the_model_does_not_read_is_named(tmp_path: Path) -> None:
    # I8: `revenu` for `revenue` left the figure out without a trace.
    text = cp1_handoff(example_registers())
    lines = text.splitlines()
    at = next(n for n, line in enumerate(lines) if "| revenue | FY2025 |" in line)
    lines[at] = lines[at].replace("| revenue |", "| revenu |", 1)
    run = run_folder(tmp_path, "\n".join(lines), run_brief())
    assert main(["model", "--run", str(run)]) == 0
    found = [x for x in _model(run)["limitation_details"] if x["code"] == "UNKNOWN_METRIC"]
    assert [x["message"] for x in found] == ["revenu: no Model line reads this account metric"]
    clean = _run(tmp_path / "clean")
    assert main(["model", "--run", str(clean)]) == 0
    assert "UNKNOWN_METRIC" not in _model(clean)["limitations"]


def test_a_non_ltm_cp1d_realized_status_left_excluded_elsewhere_is_a_limitation(
    tmp_path: Path,
) -> None:
    # Money M2 fallback: CP-1D calls the add-back realized for FY2025 while other
    # periods stay unrealized; the add-back stays excluded and the Model says so.
    row = ["run_rate_cost_savings", "FY2025", "40", "USD", "MILLIONS", "Cost savings"]
    row += ["REALIZED", "Supported", "contracted", "Yes", "[C1]"]
    cp1d = handoff(
        "CP-1D",
        [table("cp1d.addback_assessment", CP1D_COLUMNS, [row])],
        {"[C1]": ("10-K.txt", "p.70", "savings are contracted")},
    )
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief(), cp1d)
    assert main(["model", "--run", str(run)]) == 0
    found = [x for x in _model(run)["limitation_details"] if x["code"] == "ADDBACK_STATUS_MIXED"]
    assert len(found) == 1 and found[0]["message"].startswith("run_rate_cost_savings: CP-1D")


def test_a_stage_fsync_failure_cleans_its_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def full(descriptor: int) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "fsync", full)
    with pytest.raises(OSError, match="disk full"):
        run_module.stage_file(tmp_path / "model.json", b"new")
    assert list(tmp_path.iterdir()) == []


def test_a_publish_failure_exits_one_and_cleans_remaining_temporary_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    capsys.readouterr()
    before = _snapshot(run)
    prefix = (run / "log/rbot.log").read_bytes()
    replace_file = os.replace
    calls = []

    def failed(source: Path, target: Path) -> None:
        if target.name in ("model.json", "MODEL.md"):
            calls.append(target.name)
            if len(calls) == 2:
                raise OSError("publication refused")
        replace_file(source, target)

    monkeypatch.setattr(os, "replace", failed)
    assert main(["model", "--run", str(run)]) == 1
    assert _error(capsys) == "model: cannot write the outputs: publication refused\n"
    assert calls == ["model.json", "MODEL.md"]
    log = (run / "log/rbot.log").read_bytes()
    assert log.startswith(prefix) and len(log[len(prefix) :].splitlines()) == 1
    assert log.endswith(b"\t1\n")
    assert (run / "handoffs" / "MODEL.md").read_bytes() == before["handoffs/MODEL.md"]
    assert not list(run.glob(".*")) and not list((run / "handoffs").glob(".*"))
