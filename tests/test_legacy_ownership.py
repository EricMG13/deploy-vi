"""Legacy refusal precedes every publication; genuine old owners still finish."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest
from test_state import seeded

from rbotlib import (
    accept,
    approve,
    attempts,
    brief,
    cli,
    dispatch,
    fit,
    inventory,
    prepare,
    runlog,
    state,
)
from rbotlib import next as next_step
from rbotlib.model import run as model_run
from rbotlib.rules import RBOT_ROOT, load_rules


def legacy(tmp_path: Path, status: str = "pending") -> Path:
    run, record = seeded(tmp_path)
    record.pop("ownership")
    record["steps"]["MODEL"].update(status=status)
    if status in ("accepted", "blocked"):
        record["steps"]["MODEL"].update(handoff="handoffs/MODEL.md", sha256="a" * 64)
    if status in ("failed", "skipped"):
        record["steps"]["MODEL"]["reason"] = "original outcome"
    (run / state.STATE).write_text(json.dumps(record))
    (run / state.LOCK).unlink()
    (run / runlog.LOCK).unlink()
    (run / "log").rmdir()
    return run


def snapshot(run: Path) -> dict[str, bytes | None]:
    return {
        str(p.relative_to(run)): p.read_bytes() if p.is_file() else None for p in run.rglob("*")
    }


def observe(run: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    events: list[str] = []
    for name in ("mkdir", "unlink", "rename", "write_bytes", "write_text"):
        original = getattr(Path, name)

        def watched(
            path: Path,
            *args: object,
            _name: str = name,
            _original: Callable[..., object] = original,
            **kwargs: object,
        ) -> object:
            if path.is_relative_to(run):
                events.append(_name + ":" + str(path))
            return _original(path, *args, **kwargs)

        monkeypatch.setattr(Path, name, watched)
    opened = os.open

    def opening(
        path: str | os.PathLike[str], flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        if Path(path).is_relative_to(run) and flags & (
            os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_RDWR
        ):
            events.append("open:" + str(path))
        return opened(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", opening)
    return events


DIRECT: dict[str, Callable[[Path], object]] = {
    "state": lambda run: state.update(run, lambda record: record.update(probe=True)),
    "Approval": lambda run: approve.approve(
        run,
        RBOT_ROOT,
        load_rules(RBOT_ROOT),
        approve.Choice("FULL_CREDIT_ASSESSMENT", "full", False, "Analyst", False, (), False, False),
    ),
    "dispatch": lambda run: dispatch.prepare_message(run, RBOT_ROOT, "CP-0"),
    "next": lambda run: next_step.select(run, RBOT_ROOT),
    "accept": lambda run: accept.accept(run, RBOT_ROOT, "CP-0"),
    "event": lambda run: attempts.publish_event(run, "CP-0", {}),
    "receipt": lambda run: runlog.Receipt(run, ["probe"]),
    "append": lambda run: runlog.append(run, ["probe"], 0),
    "inventory": inventory.write,
    "prepare": lambda run: prepare.write(run, load_rules(RBOT_ROOT)),
    "brief": lambda run: brief._record(run, None, "new brief\n"),
    "MODEL direct": lambda run: model_run.run_model(run, "2026-10-13T00:00:00+00:00"),
    "FIT direct": lambda run: fit.run_fit(run, RBOT_ROOT),
    "FIT publication": lambda run: fit._write_all(run, {}, "new fit\n"),
    "prepare_file": lambda run: prepare.prepare_file(run, run.parents[1], {}),
}


@pytest.mark.parametrize("operation", DIRECT)
@pytest.mark.parametrize(
    "status", ["pending", "running", "accepted", "blocked", "failed", "skipped"]
)
def test_direct_legacy_refuses_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str, status: str
) -> None:
    run = legacy(tmp_path, status)
    before = snapshot(run)
    events = observe(run, monkeypatch)
    with pytest.raises(ValueError, match=r"legacy.*ownership|ownership.*legacy"):
        DIRECT[operation](run)
    assert snapshot(run) == before and events == []


@pytest.mark.parametrize(
    "command",
    ["next", "model", "fit", "inventory", "prepare", "grade", "brief", "validate", "state"],
)
def test_public_legacy_refuses_before_execution_or_finally_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    run = legacy(tmp_path)
    tail = {
        "brief": ["--set", "objective=edited"],
        "validate": ["missing.md", "--module", "CP-0"],
        "state": ["--set", "MODEL=failed", "--reason", "manual"],
    }.get(command, [])
    before = snapshot(run)
    events = observe(run, monkeypatch)
    assert cli.main([command, "--run", str(run), *tail]) == 1
    assert snapshot(run) == before and events == []


@pytest.mark.parametrize("command", ["state", "plan"])
def test_checked_legacy_inspection_is_unlogged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    run = legacy(tmp_path)
    before = snapshot(run)
    events = observe(run, monkeypatch)
    assert cli.main([command, "--run", str(run)]) == 0
    assert "ownership" not in state.read(run)
    assert snapshot(run) == before and events == []


def test_public_legacy_guard_precedes_logged_reader(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = legacy(tmp_path)
    called: list[bool] = []

    def reader(args: argparse.Namespace) -> int:
        called.append(True)
        return 0

    monkeypatch.setattr(cli, "_validate", reader)
    assert cli.main(["validate", "missing.md", "--module", "CP-0", "--run", str(run)]) == 1
    assert called == []
