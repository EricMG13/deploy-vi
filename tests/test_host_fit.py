"""Real managed FIT command, source preparation and accepted controller receipts."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

import pytest
from test_accept import send
from test_bootstrap import approve, pending, ready
from test_model_host import with_cp1
from test_next import blocked

from cp0_fixture import cp0_handoff
from rbotlib import accept, cli, dispatch, prepare, state
from rbotlib import next as next_step
from rbotlib.fit import Written
from rbotlib.fit_host import Fit, Inputs, qualify
from rbotlib.model import run as writer
from rbotlib.rules import RBOT_ROOT
from test_grade import ACME, FILES


def fit_run(tmp_path: Path, *, unreadable: bool = False, profile: bool = False) -> Path:
    run = pending(tmp_path, RBOT_ROOT)
    pack = run.parent.parent
    meta = (
        "Portfolio ID,FUND\nPortfolio,Generated fund\nStrategy,CLO\nAs of,2026-05-29\n"
        "Currency,USD\nUnit,USD\nTotal NAV,1000000\nTotal Par,1000000\n"
    )
    (pack / "positions.csv").write_text(
        meta + "Issuer ID,Issuer,Par,% NAV\nACME,Acme Holdings Inc.,10000,1%\n"
    )
    (pack / "limits.csv").write_text(
        meta + "ID,Constraint Category,Parameter,Limit,Breach Type,Current Value\n"
        "L1,Issuer,Max issuer,2.5% NAV,Hard,1%\n"
    )
    if unreadable:
        (pack / "unrelated.xlsx").write_bytes(b"unreadable fixture workbook")
    for command in ("inventory", "prepare"):
        assert cli.main([command, "--run", str(run)]) == 0
    classes = FILES | {
        name: ("portfolio", kind, "FUND", "Yes")
        for name, kind in (
            ("positions.csv", "Portfolio positions"),
            ("limits.csv", "Portfolio limits"),
        )
    }
    if unreadable:
        classes["unrelated.xlsx"] = ("issuer", "Other", "ACME", "Yes")
    (run / "handoffs/CP-0.md").write_text(
        cp0_handoff(run, ACME, "2026-10-02", classes, primary=False)
    )
    send(run, RBOT_ROOT)
    assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == 0
    ready(run, RBOT_ROOT)
    run = with_cp1(approve(run, RBOT_ROOT), RBOT_ROOT, "Pass", variant="profile" if profile else "")
    if profile:
        blocked(run, RBOT_ROOT, "CP-1A")
    for module in ("CP-1C", "CP-2A", "CP-2E", "CP-4", "CP-2D"):
        state.set_status(run, module, "failed", f"FIT fixture: unavailable {module} analysis")
    assert cli.main(["model", "--run", str(run)]) == 0
    if profile:
        blocked(run, RBOT_ROOT, "CP-2")
    blocked(run, RBOT_ROOT, "CP-3")
    assert next_step.select(run, RBOT_ROOT)["step"] == "FIT"
    return run


def test_returned_public_fit_completes_and_qualifies_consumer(tmp_path: Path) -> None:
    run = fit_run(tmp_path)
    selected = next_step.select(run, RBOT_ROOT)
    result = subprocess.run(shlex.split(selected["command"]), capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    current = state.read(run)["steps"]["FIT"]
    assert current["status"] == "accepted" and current["attempts"] == 1
    assert current["host_exit"] == 0 and current["host_execution"]["token"]
    assert set(current["outputs"]) == {"fit/FUND.json", "handoffs/FIT.md"}
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-5"
    assert str(run / "handoffs/FIT.md") in dispatch.prepare_message(run, RBOT_ROOT, "CP-5")
    rows = [r for r in (run / "log/rbot.log").read_bytes().splitlines() if b" fit --run " in r]
    assert len(rows) == 1 and rows[0].endswith(b"\t0")


def test_public_fit_log_failure_cannot_accept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = fit_run(tmp_path)

    def denied(*args: object, **kwargs: object) -> None:
        raise OSError("actual FIT log append denied")

    monkeypatch.setattr(cli, "_log", denied)
    assert cli.main(["fit", "--run", str(run)]) == 1
    assert state.read(run)["steps"]["FIT"]["status"] == "failed"


@pytest.mark.parametrize("name", ["handoffs/CP-1.md", "handoffs/CP-3.md", "run-brief.md"])
def test_valid_current_narrative_qualifies_before_first_attempt(tmp_path: Path, name: str) -> None:
    run = fit_run(tmp_path)
    path = run / name
    before = state.read(run)["steps"]["FIT"]
    path.write_bytes(path.read_bytes() + b"\nchanged\n")
    assert before["status"] == "pending" and "attempts" not in before
    assert cli.main(["fit", "--run", str(run)]) == 0
    now = state.read(run)["steps"]["FIT"]
    assert now["status"] == "accepted" and now["attempts"] == 1
    inputs = now["host_execution"]["inputs"]
    key = "RUN_BRIEF" if name == "run-brief.md" else Path(name).stem
    assert inputs[key] == dispatch._sha(path)


def test_prepared_portfolio_cannot_override_source_limit(tmp_path: Path) -> None:
    run = fit_run(tmp_path)
    path = run / "prepared/portfolios/FUND.json"
    data = json.loads(path.read_bytes())
    data["limits"][0]["limit_value"] = "100"
    path.write_text(json.dumps(data))
    assert cli.main(["fit", "--run", str(run)]) == 1
    assert state.read(run)["steps"]["FIT"]["status"] == "pending"
    assert not (run / "handoffs/FIT.md").exists()


@pytest.mark.parametrize("kind", ["malformed", "symlink", "fifo"])
def test_failed_optional_leftover_never_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    run = fit_run(tmp_path)
    path = run / "handoffs/CP-1A.md"
    if kind == "malformed":
        path.write_bytes(b"\xff")
    elif kind == "symlink":
        path.symlink_to(run / "run-brief.md")
    else:
        os.mkfifo(path)
    read = Path.read_bytes

    def guarded(selected: Path) -> bytes:
        if selected == path:
            raise AssertionError("failed optional bytes opened")
        return read(selected)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    assert cli.main(["fit", "--run", str(run)]) == 0
    assert "CP-1A: failed; excluded" in (run / "handoffs/FIT.md").read_text()
    assert json.loads((run / "fit/FUND.json").read_bytes())["inputs"]["CP-1A"] is None


@pytest.mark.parametrize("phase", ["stage1", "stage2", "replace1", "replace2", "readback", "state"])
def test_partial_fit_publication_never_accepts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    run = fit_run(tmp_path)
    prefix = (run / "log/rbot.log").read_bytes()
    stage, replace, read = writer.stage_file, os.replace, Path.read_bytes
    stages, replacements = [], []

    def staging(target: Path, raw: bytes) -> Path:
        if target.name in ("FUND.json", "FIT.md"):
            stages.append(target.name)
            if phase == f"stage{len(stages)}":
                raise OSError(f"FIT {phase} denied")
        return stage(target, raw)

    def replacing(source: Path, target: Path) -> None:
        if target.name in ("FUND.json", "FIT.md"):
            assert stages == ["FUND.json", "FIT.md"]
            replacements.append(target.name)
            if phase == f"replace{len(replacements)}":
                raise OSError(f"FIT {phase} denied")
        if (
            phase == "state"
            and target == run / state.STATE
            and replacements
            and (run / "log/rbot.log").read_bytes().endswith(b"\t0\n")
        ):
            raise OSError("FIT accepted state denied")
        replace(source, target)

    def reading(path: Path) -> bytes:
        if phase == "readback" and path == run / "fit/FUND.json" and replacements:
            raise OSError("FIT readback denied")
        return read(path)

    monkeypatch.setattr(writer, "stage_file", staging)
    monkeypatch.setattr(os, "replace", replacing)
    monkeypatch.setattr(Path, "read_bytes", reading)
    assert cli.main(["fit", "--run", str(run)]) == 1
    current = state.read(run)["steps"]["FIT"]
    assert current["status"] == "failed" and current["host_exit"] == 1
    assert current["attempts"] == 1 and current["host_execution"]["token"]
    rows = (run / "log/rbot.log").read_bytes()[len(prefix) :].splitlines()
    assert len(rows) == 1 and rows[0].endswith(b"\t1")
    before = (run / state.STATE).read_bytes()
    assert cli.main(["fit", "--run", str(run)]) == 1
    assert (run / state.STATE).read_bytes() == before


@pytest.mark.parametrize("corruption", ["json", "handoff", "partial", "extra"])
def test_forged_built_set_refused_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str
) -> None:
    run = fit_run(tmp_path)
    build = Fit.build
    once = False

    def changed(captured: Inputs, generated_at: str) -> tuple[Written, dict[str, bytes]]:
        nonlocal once
        result = build(captured, generated_at)
        if not once:
            once = True
            files = result[1]
            if corruption == "partial":
                del files["fit/FUND.json"]
            elif corruption == "extra":
                files["model.xlsx"] = b"retired export"
            else:
                files["fit/FUND.json" if corruption == "json" else "handoffs/FIT.md"] += b"forged"
        return result

    monkeypatch.setattr(Fit, "build", staticmethod(changed))
    assert cli.main(["fit", "--run", str(run)]) == 1
    assert once  # prove the corruption seam ran, rather than an unrelated build error
    assert state.read(run)["steps"]["FIT"]["status"] == "failed"
    assert not (run / "handoffs/FIT.md").exists()


@pytest.mark.parametrize("name", ["fit/FUND.json", "handoffs/FIT.md"])
def test_current_forged_or_partial_output_refuses_consumer(tmp_path: Path, name: str) -> None:
    run = fit_run(tmp_path)
    assert cli.main(["fit", "--run", str(run)]) == 0
    path = run / name
    path.write_bytes(path.read_bytes() + b"\nforged\n")

    def forge(record: state.Record) -> None:
        current = record["steps"]["FIT"]
        current["outputs"][name] = dispatch._sha(path)
        current["sha256"] = current["outputs"]["handoffs/FIT.md"]

    state.update(run, forge)
    with pytest.raises(ValueError, match="origin"):
        qualify(run, RBOT_ROOT, state.read(run))
    assert cli.main(["dispatch-message", "--run", str(run), "--module", "CP-5"]) == 0
    assert state.read(run)["steps"]["FIT"]["status"] == "failed"
    assert "FIT: failed" in (run / "dispatch/CP-5.md").read_text()
    path.unlink()
    assert cli.main(["dispatch-message", "--run", str(run), "--module", "CP-5"]) == 0


def test_unrelated_unreadable_source_does_not_prevent_fit(tmp_path: Path) -> None:
    run = fit_run(tmp_path, unreadable=True)
    assert cli.main(["fit", "--run", str(run)]) == 0


def test_unreadable_declared_limits_cannot_hide_expected_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = fit_run(tmp_path)
    read = prepare.read

    def unreadable(path: Path, kind: str) -> prepare.Prepared:
        if path.name == "limits.csv":
            raise prepare.UnreadableError("declared limits no longer readable")
        return read(path, kind)

    monkeypatch.setattr(prepare, "read", unreadable)
    assert cli.main(["fit", "--run", str(run)]) == 1
    assert state.read(run)["steps"]["FIT"]["status"] == "pending"
    assert not (run / "handoffs/FIT.md").exists()


@pytest.mark.parametrize("changed", [False, True])
def test_qualified_blocked_profile_or_visible_exclusion(
    tmp_path: Path,
    changed: bool,
) -> None:
    run = fit_run(tmp_path, profile=True)
    path = run / "handoffs/CP-1A.md"
    if changed:
        path.write_bytes(path.read_bytes() + b"\nchanged\n")
    assert cli.main(["fit", "--run", str(run)]) == 0
    hashes = json.loads((run / "fit/FUND.json").read_bytes())["inputs"]
    assert hashes["CP-1A"] == dispatch._sha(path)
    if changed:
        assert state.read(run)["steps"]["CP-1A"]["note"] == "edited"


@pytest.mark.parametrize(
    "name", ["positions.csv", "prepared/portfolios/FUND.json", "handoffs/CP-3.md"]
)
def test_input_change_during_build_refuses_completion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    run = fit_run(tmp_path)
    path = run.parent.parent / name if name == "positions.csv" else run / name
    build = Fit.build

    def swap(captured: Inputs, generated_at: str) -> tuple[Written, dict[str, bytes]]:
        path.write_bytes(path.read_bytes() + b"\nchanged\n")
        return build(captured, generated_at)

    monkeypatch.setattr(Fit, "build", staticmethod(swap))
    assert cli.main(["fit", "--run", str(run)]) == 1
    assert path.read_bytes().endswith(b"\nchanged\n")
    assert state.read(run)["steps"]["FIT"]["status"] == "failed"
    assert not (run / "handoffs/FIT.md").exists()
