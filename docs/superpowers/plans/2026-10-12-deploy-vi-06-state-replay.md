# Plan06.1 final state/test replay bytes

Consumes the canonical [Plan06 task06.1](2026-10-12-deploy-vi-06-orchestrator.md), approved05 base and its retained history. This separately counted documentation scope holds final actual files after fix round2. The additional public ownership regressions have their own counted [replay artifact](2026-10-12-deploy-vi-06-state-logging-replay.md). It is an executable byte contract, not independent review approval. Root replays verified commits only after both reviewers accept; no hand-patching on mismatch.

The original task7ad14b2 and planb0bb961 remain historical evidence of the failed logging/file-kind review. Do not replay either alone as a corrected task. CLI final bytes, commit/tree/lock boundary and gates are in the canonical plan; full causal/tournament evidence is in main staging task-01-report.md.

## tests/test_state.py
```python
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
    run = pack / "rbot-runs" / "20261012-acme-pending"
    run.mkdir(parents=True)
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
    assert not (run / ".approve.lock").exists()


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
    assert not (run / ".approve.lock").exists()
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
    log.parent.mkdir()
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
    assert not (run / ".approve.lock").exists()
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
```

## rbot/scripts/rbotlib/state.py
```python
"""Checked run state. Acceptance/dispatch owners use update; public edits only fail/skip.

The shared Approval lock prevents cooperating writers from losing fields or racing
Approval's rename. Destination guards are rechecked after staging; hostile directory
replacement and abrupt-crash consistency are not guaranteed by this path-based API.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from rbotlib.fsio import write_atomic
from rbotlib.inventory import RunError, output_path

STATE = "run-state.json"
LOCK = ".approve.lock"
STATUSES = {"pending", "running", "accepted", "blocked", "failed", "skipped"}
HOSTS = {"MODEL", "FIT", "PROJECTION"}
Record = dict[str, Any]
Check = Callable[[object], bool]


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nullable(check: Check) -> Check:
    return lambda value: value is None or check(value)


def _stamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def _date(value: object) -> bool:
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _strings(value: object) -> bool:
    return isinstance(value, list) and all(_text(v) for v in value)


def _fields(record: object, checks: dict[str, Check], label: str) -> Record:
    if not isinstance(record, dict):
        raise RunError(f"{label}: expected an object")
    for key, check in checks.items():
        if key not in record or not check(record[key]):
            raise RunError(f"{label}.{key}: missing or invalid value")
    return record


def _step(step: str, record: object) -> None:
    label = f"{STATE}.steps.{step}"
    record = _fields(
        record,
        {
            "kind": lambda v: v == ("host" if step in HOSTS else "module"),
            "status": lambda v: isinstance(v, str) and v in STATUSES,
        },
        label,
    )
    checks: dict[str, Check] = {
        "attempts": lambda v: type(v) is int and v >= 0,
        "validate_exit": lambda v: type(v) is int and v in range(5),
        "qa_status": lambda v: v in ("Pass", "Restricted", "Blocked"),
        "handoff": lambda v: v == f"handoffs/{step}.md",
        "sha256": _sha,
        "started_at": _stamp,
        "finished_at": _stamp,
        "reason": lambda v: isinstance(v, str),
        "model": _text,
    }
    _fields(record, {k: checks[k] for k in checks if k in record}, label)
    if record["status"] in ("failed", "skipped"):
        _fields(record, {"reason": _text}, label)
    _completed(record, checks, label)


def _completed(record: Record, checks: dict[str, Check], label: str) -> None:
    if record["status"] in ("accepted", "blocked"):
        _fields(record, {"handoff": checks["handoff"], "sha256": _sha}, label)
        if record["kind"] == "module":
            code = 0 if record["status"] == "accepted" else 3
            qa = ("Pass", "Restricted") if code == 0 else ("Blocked",)
            _fields(
                record,
                {
                    "validate_exit": lambda v: type(v) is int and v == code,
                    "qa_status": lambda v: v in qa,
                },
                label,
            )


def validate(record: Record, run: Path) -> None:
    """Validate schema/known fields; extension metadata is retained, never projected away."""
    _fields(
        record,
        {
            "schema": lambda v: v == "rbot-run-state/1",
            "rbot_version": _text,
            "run_id": lambda v: v == run.name,
            "pack_root": _text,
            "created_at": _stamp,
            "updated_at": _stamp,
            "run_brief": lambda v: v == "run-brief.md",
            "run_brief_sha256": _nullable(_sha),
            "issuer_id": _nullable(_text),
            "as_of_date": _nullable(_date),
            "pathway": _nullable(_text),
            "depth": lambda v: v in (None, "full", "quick"),
            "primary": lambda v: v is None or type(v) is bool,
            "deep_research": lambda v: v is None or type(v) is bool,
            "approval": lambda v: v is None or isinstance(v, dict),
            "prior_case": lambda v: v is None or isinstance(v, dict),
            "plan": _strings,
            "steps": lambda v: isinstance(v, dict),
            "report": lambda v: isinstance(v, dict),
        },
        STATE,
    )
    pack = Path(record["pack_root"])
    if (
        not pack.is_absolute()
        or run.parent.name != "rbot-runs"
        or run.parent.parent != _physical(pack)
    ):
        raise RunError(f"{STATE}.pack_root: run must be inside pack/rbot-runs/<run_id>")
    plan = record["plan"]
    if len(set(plan)) != len(plan) or set(plan) != set(record["steps"]):
        raise RunError(f"{STATE}.plan: duplicate step or steps do not match plan")
    for step in plan:
        if re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*", step) is None:
            raise RunError(f"{STATE}.plan: invalid step {step!r}")
        _step(step, record["steps"][step])
    _fields(
        record["report"],
        {
            "written_at": _nullable(_stamp),
            "html_sha256": _nullable(_sha),
            "md_sha256": _nullable(_sha),
        },
        f"{STATE}.report",
    )
    _approval(record)


def _approval(record: Record) -> None:
    if record["prior_case"] is not None:
        _fields(
            record["prior_case"],
            {
                "offered": lambda v: type(v) is bool,
                "accepted": lambda v: type(v) is bool,
                "report": _nullable(_text),
            },
            f"{STATE}.prior_case",
        )
    if record["approval"] is None:
        if record["plan"] not in ([], ["CP-0"]) or any(
            record[k] is not None for k in ("pathway", "depth", "primary", "deep_research")
        ):
            raise RunError(f"{STATE}.approval: unapproved analysis plan or flags")
        return
    _fields(
        record,
        {
            "prior_case": lambda v: isinstance(v, dict),
            "issuer_id": _text,
            "as_of_date": _date,
            "pathway": _text,
            "depth": lambda v: v in ("full", "quick"),
            "primary": lambda v: type(v) is bool,
            "deep_research": lambda v: type(v) is bool,
        },
        STATE,
    )
    _fields(
        record["approval"],
        {
            "approved_at": _stamp,
            "analyst": _text,
            "pathway_grade": lambda v: v in ("Available", "With limitations", "Blocked"),
            "acknowledged_blocked_modules": _strings,
            "limitations_shown": _strings,
        },
        f"{STATE}.approval",
    )


def _physical(path: Path) -> Path:
    """Require an existing traversal; Python 3.11 reports resolution loops as RuntimeError."""
    try:
        return path.resolve(strict=True)
    except RuntimeError as exc:
        raise RunError(f"cannot resolve path: {path} ({exc})") from exc


def run_path(run: Path) -> Path:
    """Normalize the effective envelope, refusing traversed links inside its pack."""
    selected = run.absolute()
    run = _physical(selected)
    if not run.is_dir():
        raise RunError(f"run folder does not exist: {run}")
    if run.parent.name != "rbot-runs":
        raise RunError(f"run must be inside pack/rbot-runs/<run_id>: {run}")
    pack = run.parent.parent
    for path in (selected, *selected.parents):
        if path.is_symlink() and (
            _physical(path).is_relative_to(pack) or _physical(path.parent).is_relative_to(pack)
        ):
            raise RunError(f"run path is a symlink: {path}")
    return run


def log_run_path(run: Path) -> Path:
    """Only checked state identity can grant this command ownership of a run log."""
    run = run_path(run)
    try:
        read(run)
    except (OSError, ValueError, RecursionError) as exc:
        raise RunError(f"{STATE}: cannot prove log ownership ({exc})") from exc
    return run


def _destination(run: Path) -> Path:
    target = output_path(run, STATE)
    if not target.is_file():
        raise RunError(f"{target}: state must be an existing regular file")
    return target


def _pairs(pairs: list[tuple[str, Any]]) -> Record:
    record: Record = {}
    for key, value in pairs:
        if key in record:
            raise RunError(f"{STATE}: duplicate key {key!r}")
        record[key] = value
    return record


def read(run: Path) -> Record:
    """Read strict JSON from a guarded production run; malformed/linked state refuses."""
    run = run_path(run)
    record: Record = json.loads(
        _destination(run).read_text(encoding="utf-8"), object_pairs_hook=_pairs
    )
    validate(record, run)
    json.dumps(record, allow_nan=False)  # also rejects non-finite extension metadata
    return record


def update(run: Path, change: Callable[[Record], None]) -> Record:
    """Read/change/check/publish under Approval's lock; callbacks must not publish files."""
    run = run_path(run)
    lock = output_path(run, LOCK)
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    except FileExistsError as exc:
        raise RunError(f"another state update or Approval holds this run ({LOCK})") from exc
    stage: Path | None = None
    try:
        record = read(run)
        change(record)
        record["updated_at"] = datetime.now(UTC).isoformat(timespec="seconds")
        validate(record, run)
        fd, name = tempfile.mkstemp(dir=run, prefix=".state-")
        os.close(fd)
        stage = Path(name)
        write_atomic(
            stage, json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        )
        os.replace(stage, _destination(run))
        return record
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def set_status(run: Path, step: str, status: str, reason: str) -> Record:
    """Public callers may record failure/skip; acceptance requires independent validation."""

    def change(record: Record) -> None:
        if step not in record["steps"]:
            raise RunError(f"unknown step {step!r}")
        current = record["steps"][step]
        allowed = {"failed": {"pending", "running"}, "skipped": {"pending"}}
        if status not in allowed or current["status"] not in allowed[status]:
            raise RunError(f"step {step}: cannot set {current['status']} to {status}")
        if not _text(reason):
            raise RunError("a failed/skipped step requires --reason")
        current.update(
            status=status,
            reason=reason,
            finished_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )

    return update(run, change)


def _selected(args: argparse.Namespace) -> Record:
    run = Path(args.run_dir)
    if args.set is None:
        if args.reason is not None:
            raise RunError("--reason requires --set")
        return read(run)
    step, separator, status = args.set.partition("=")
    if not separator:
        raise RunError("--set requires step=status")
    return set_status(run, step, status, args.reason or "")


def state_command(args: argparse.Namespace) -> int:
    try:
        print(json.dumps(_selected(args), indent=2, ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, RecursionError) as exc:
        print(f"error: {exc}")
        return 1
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser("state", help="print checked state or record a named failure/skip")
    parser.add_argument("--run", dest="run_dir", required=True)
    parser.add_argument("--set", metavar="STEP=STATUS")
    parser.add_argument("--reason")
    parser.set_defaults(run=state_command, log_run_guard=log_run_path)
```

Not verified: independent repaired-scope approval, full Plan06 integration/replay/corpus closure and live Copilot acceptance.
