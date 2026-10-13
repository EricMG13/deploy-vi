from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rbotlib.cli import main
from rbotlib.fsio import write_atomic

STAMP = "2026-10-12T10:00:00+00:00"


def seeded(tmp_path: Path, approved: bool = True) -> tuple[Path, dict[str, Any]]:
    pack = tmp_path / "pack"
    pack.mkdir(parents=True)
    from rbotlib import runs, state

    run = runs.create_run(pack)
    (pack / "source.md").write_bytes(b"unaltered source evidence\n")
    data: dict[str, Any] = {
        "schema": "rbot-run-state/1",
        "rbot_version": "0.1.0",
        "run_id": run.name,
        "pack_root": str(pack),
        "created_at": STAMP,
        "updated_at": STAMP,
        "run_brief": "run-brief.md",
        "run_brief_sha256": None,
        "issuer_id": None,
        "as_of_date": None,
        "pathway": None,
        "depth": None,
        "primary": None,
        "deep_research": None,
        "prior_case": None,
        "approval": None,
        "plan": ["CP-0"],
        "steps": {"CP-0": {"kind": "module", "status": "pending"}},
        "report": {"written_at": None, "html_sha256": None, "md_sha256": None},
        "hints": {"objective": "annual review"},
    }
    if approved:
        data.update(
            issuer_id="ACME",
            as_of_date="2026-10-02",
            pathway="FULL_CREDIT_ASSESSMENT",
            depth="full",
            primary=False,
            deep_research=False,
            prior_case={"offered": False, "accepted": False, "report": None},
            approval={
                "approved_at": STAMP,
                "analyst": "A. Analyst",
                "pathway_grade": "Available",
                "acknowledged_blocked_modules": [],
                "limitations_shown": [],
            },
        )
        data["plan"] = ["CP-0", "MODEL"]
        data["steps"]["MODEL"] = {
            "kind": "host",
            "status": "running",
            "attempts": 1,
            "started_at": STAMP,
            "model": "qualified-worker",
        }
    data["ownership"] = state.read(run)["ownership"]
    (run / "run-state.json").write_text(json.dumps(data), encoding="utf-8")
    return run, data


def invoke(run: Path, *args: str) -> int:
    try:
        return main(["state", "--run", str(run), *args])
    except SystemExit as exc:
        assert isinstance(exc.code, int)
        return exc.code


def test_public_state_prints_complete_bootstrap_and_preserves_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run, data = seeded(tmp_path, approved=False)
    assert invoke(run) == 0
    assert json.loads(capsys.readouterr().out) == data
    assert invoke(run, "--set", "CP-0=failed", "--reason", "terminal unavailable") == 0
    changed = json.loads(capsys.readouterr().out)
    assert changed["hints"] == data["hints"] and changed["issuer_id"] is None
    assert changed["steps"]["CP-0"]["reason"] == "terminal unavailable"
    assert changed["steps"]["CP-0"]["finished_at"]
    assert (run.parent.parent / "source.md").read_bytes() == b"unaltered source evidence\n"


@pytest.mark.parametrize(
    "assignment",
    [
        "NOPE=failed",
        "MODEL=accepted",
        "MODEL=blocked",
        "MODEL=pending",
        "MODEL=running",
        "MODEL=nonsense",
    ],
)
def test_public_state_cannot_forge_acceptance_or_resurrect_steps(
    tmp_path: Path, assignment: str
) -> None:
    run, _ = seeded(tmp_path)
    before = (run / "run-state.json").read_bytes()
    assert invoke(run, "--set", assignment, "--reason", "manual claim") == 1
    assert (run / "run-state.json").read_bytes() == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "other"),
        ("steps", []),
        ("report", {}),
        ("created_at", "yesterday"),
        ("run_brief", "../source.md"),
        ("plan", ["CP-0", "CP-0"]),
    ],
)
def test_bad_schema_is_named_without_state_or_source_mutation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], field: str, value: object
) -> None:
    run, data = seeded(tmp_path)
    data[field] = value
    (run / "run-state.json").write_text(json.dumps(data), encoding="utf-8")
    before = (run / "run-state.json").read_bytes()
    assert invoke(run) == 1
    captured = capsys.readouterr()
    assert field in captured.out + captured.err
    assert (run / "run-state.json").read_bytes() == before
    assert (run.parent.parent / "source.md").read_bytes() == b"unaltered source evidence\n"


@pytest.mark.parametrize("destination", ["run-state.json", ".approve.lock", "log/rbot.log"])
@pytest.mark.parametrize("kind", ["symbolic", "hard"])
def test_linked_destinations_do_not_change_sources(
    tmp_path: Path, destination: str, kind: str
) -> None:
    run, _ = seeded(tmp_path)
    source = run.parent.parent / "source.md"
    target = run / destination
    target.parent.mkdir(exist_ok=True)
    target.unlink(missing_ok=True)
    target.symlink_to(source) if kind == "symbolic" else os.link(source, target)
    assert invoke(run, "--set", "MODEL=failed", "--reason", "unavailable") == 1
    assert source.read_bytes() == b"unaltered source evidence\n"


def test_shared_lock_refuses_overlap_then_reads_the_latest_state(tmp_path: Path) -> None:
    from rbotlib import state

    run, data = seeded(tmp_path)
    inside, release = threading.Event(), threading.Event()
    errors: list[Exception] = []

    def change(record: dict[str, Any]) -> None:
        record["worker_note"] = "first update"
        inside.set()
        assert release.wait(10)

    def first() -> None:
        try:
            state.update(run, change)
        except (ValueError, OSError) as exc:
            errors.append(exc)

    thread = threading.Thread(target=first)
    thread.start()
    assert inside.wait(10)
    try:
        child = subprocess.run(
            [
                sys.executable,
                "rbot/scripts/rbot.py",
                "state",
                "--run",
                str(run),
                "--set",
                "MODEL=failed",
                "--reason",
                "host command failed",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        assert child.returncode == 1 and ".approve.lock" in child.stdout
    finally:
        release.set()
        thread.join(10)
    assert not errors and not thread.is_alive()
    assert invoke(run, "--set", "MODEL=failed", "--reason", "host command failed") == 0
    record = state.read(run)
    assert record["worker_note"] == "first update" and record["hints"] == data["hints"]
    assert record["steps"]["MODEL"]["attempts"] == 1
    assert record["steps"]["MODEL"]["started_at"] == STAMP
    assert record["steps"]["MODEL"]["model"] == "qualified-worker"
    assert (run / ".approve.lock").exists()


@pytest.mark.parametrize("raw", ["[]", '{"schema": 1, "schema": 2}', "NaN"])
def test_strict_json_errors_are_named(tmp_path: Path, raw: str) -> None:
    run, _ = seeded(tmp_path)
    (run / "run-state.json").write_text(raw, encoding="utf-8")
    assert invoke(run) == 1


@pytest.mark.parametrize("change", ["boolean attempts", "nan metadata", "source collision"])
def test_untrusted_values_do_not_pass_checked_read(tmp_path: Path, change: str) -> None:
    run, data = seeded(tmp_path)
    if change == "boolean attempts":
        data["steps"]["MODEL"]["attempts"] = True
    elif change == "nan metadata":
        data["extra"] = float("nan")
    else:
        data["pack_root"] = str(run)
    (run / "run-state.json").write_text(json.dumps(data), encoding="utf-8")
    assert invoke(run) == 1


@pytest.mark.parametrize("event", ["staging fails", "target becomes linked"])
def test_publication_boundary_failure_preserves_old_state_and_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, event: str
) -> None:
    from rbotlib import state

    run, _ = seeded(tmp_path)
    before = (run / "run-state.json").read_bytes()
    source = run.parent.parent / "source.md"

    def at_stage(path: Path, text: str) -> None:
        if event == "staging fails":
            raise OSError("staging interrupted")
        write_atomic(path, text)
        (run / "run-state.json").rename(run / "original-state.json")
        (run / "run-state.json").symlink_to(source)

    monkeypatch.setattr(state, "write_atomic", at_stage)
    assert invoke(run, "--set", "MODEL=failed", "--reason", "host failed") == 1
    preserved = run / ("run-state.json" if event == "staging fails" else "original-state.json")
    assert preserved.read_bytes() == before
    assert source.read_bytes() == b"unaltered source evidence\n"
    assert (run / ".approve.lock").exists()
    assert not list(run.glob(".state-*"))


@pytest.mark.parametrize("component", ["ancestor", "pack", "rbot-runs", "run"])
def test_ordinary_aliases_above_pack_work_but_output_links_refuse(
    tmp_path: Path, component: str
) -> None:
    run, _ = seeded(tmp_path / "real")
    original = {
        "ancestor": run.parent.parent.parent,
        "pack": run.parent.parent,
        "rbot-runs": run.parent,
        "run": run,
    }[component]
    alias = original.parent / "alias"
    alias.symlink_to(original, target_is_directory=True)
    alias_run = alias / run.relative_to(original)
    log = run / "log/rbot.log"
    log.parent.mkdir(exist_ok=True)
    log.write_bytes(b"existing run log evidence\n")
    before = log.read_bytes()
    assert invoke(alias_run) == (0 if component == "ancestor" else 1)
    if component == "ancestor":
        assert log.read_bytes().startswith(before) and log.read_bytes().endswith(b"\t0\n")
    else:
        assert log.read_bytes() == before


@given(
    st.sampled_from(["accepted", "blocked", "failed", "skipped"]),
    st.sampled_from(["pending", "running", "accepted", "blocked", "failed", "skipped"]),
)
def test_public_terminal_transitions_are_absorbing(terminal: str, target: str) -> None:
    with tempfile.TemporaryDirectory() as folder:
        run, data = seeded(Path(folder))
        data["steps"]["MODEL"].update(
            status=terminal, reason="recorded result", handoff="handoffs/MODEL.md", sha256="a" * 64
        )
        before = json.dumps(data).encode()
        (run / "run-state.json").write_bytes(before)
        assert invoke(run, "--set", f"MODEL={target}", "--reason", "manual retry") == 1
        assert (run / "run-state.json").read_bytes() == before


def test_bootstrap_prior_case_cannot_hide_an_invalid_shape(tmp_path: Path) -> None:
    run, data = seeded(tmp_path, approved=False)
    data["prior_case"] = {"accepted": "yes"}
    (run / "run-state.json").write_text(json.dumps(data), encoding="utf-8")
    assert invoke(run) == 1


@pytest.mark.parametrize("alias", [False, True])
@pytest.mark.parametrize("existing_log", [False, True])
def test_rejected_source_run_has_no_logging_side_effect(
    tmp_path: Path, alias: bool, existing_log: bool
) -> None:
    source = tmp_path / "source-evidence"
    source.mkdir()
    (source / "original.md").write_bytes(b"protected source evidence\n")
    if existing_log:
        (source / "log").mkdir()
        (source / "log/rbot.log").write_bytes(b"protected source log evidence\n")
    selected = source
    if alias:
        selected = tmp_path / "pack/rbot-runs/selected"
        selected.parent.mkdir(parents=True)
        selected.symlink_to(source, target_is_directory=True)
    before = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    assert invoke(selected) == 1
    assert {
        p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()
    } == before
    assert (source / "log").exists() == existing_log


@pytest.mark.parametrize("kind", ["directory target", "file parent", "fifo target", "fifo parent"])
def test_malformed_log_refuses_before_terminal_state_publication(tmp_path: Path, kind: str) -> None:
    run, _ = seeded(tmp_path)
    target = run / ("log/rbot.log" if kind.endswith("target") else "log")
    target.parent.mkdir(exist_ok=True)
    if target.is_dir():
        (target / ".rbot-log.lock").unlink()
        target.rmdir()
    if kind.startswith("directory"):
        target.mkdir()
    elif kind.startswith("file"):
        target.write_bytes(b"source-like parent bytes\n")
    else:
        os.mkfifo(target)
    before = (run / "run-state.json").read_bytes()
    child = subprocess.run(
        [
            sys.executable,
            "rbot/scripts/rbot.py",
            "state",
            "--run",
            str(run),
            "--set",
            "MODEL=failed",
            "--reason",
            "host failed",
        ],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    assert child.returncode == 1
    assert (run / "run-state.json").read_bytes() == before
    diagnostic = child.stdout + child.stderr
    assert "log" in diagnostic and ("regular file" in diagnostic or "directory" in diagnostic)
    assert (run / ".approve.lock").exists()
    if kind == "file parent":
        assert target.read_bytes() == b"source-like parent bytes\n"


@pytest.mark.parametrize("kind", ["directory", "fifo"])
def test_nonregular_state_refuses_promptly_in_real_process(tmp_path: Path, kind: str) -> None:
    run, _ = seeded(tmp_path)
    target = run / "run-state.json"
    target.unlink()
    target.mkdir() if kind == "directory" else os.mkfifo(target)
    child = subprocess.run(
        [sys.executable, "rbot/scripts/rbot.py", "state", "--run", str(run)],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    assert child.returncode == 1
    diagnostic = child.stdout + child.stderr
    assert "run-state.json" in diagnostic and "regular file" in diagnostic
    assert target.is_dir() if kind == "directory" else not target.is_file()
    assert (run.parent.parent / "source.md").read_bytes() == b"unaltered source evidence\n"


def test_valid_run_failed_command_retains_honest_log(tmp_path: Path) -> None:
    run, _ = seeded(tmp_path)
    before = (run / "run-state.json").read_bytes()
    assert invoke(run, "--set", "NOPE=failed", "--reason", "host failed") == 1
    assert (run / "run-state.json").read_bytes() == before
    log = (run / "log/rbot.log").read_text().splitlines()
    assert len(log) == 1 and "NOPE=failed" in log[0] and log[0].endswith("\t1")
