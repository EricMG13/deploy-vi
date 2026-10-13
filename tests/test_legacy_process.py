"""Whole original state/host/logger processes retain successful outcomes after refusal."""

from __future__ import annotations

import json
import os
import select
import subprocess
import sys
from pathlib import Path

import pytest
from test_host_fit import fit_run
from test_legacy_ownership import legacy, observe, snapshot
from test_model_host import eligible

from rbotlib import cli, runlog, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT

OLD = r"""
import argparse, subprocess, sys, types
from pathlib import Path
from rbotlib.rules import RBOT_ROOT
def frozen(name, path):
    module = types.ModuleType(name)
    sys.modules[name] = module
    raw = subprocess.check_output(['git', 'show', 'aff1ee9:' + path])
    exec(compile(raw, path, 'exec'), module.__dict__)
    return module
oldstate = frozen('old_state', 'rbot/scripts/rbotlib/state.py')
oldlog = frozen('old_log', 'rbot/scripts/rbotlib/runlog.py')
kind, run = sys.argv[1], Path(sys.argv[2])
if kind == 'logger':
    assert all(s['status'] != 'running' for s in oldstate.read(run)['steps'].values())
    print('BOUNDARY', flush=True)
    assert sys.stdin.readline().strip() == 'continue'
    oldlog.append(run, ['old-logged-reader'], 0)
    sys.exit(0)
oldhost = frozen('old_host', 'rbot/scripts/rbotlib/model/host.py')
oldhost.state, oldhost.runlog = oldstate, oldlog
from rbotlib.fit_host import Fit
backend = oldhost.Model if kind == 'model' else Fit
build = backend.build
first = True
def paused(*args):
    global first
    if first:
        first = False
        print('BOUNDARY', flush=True)
        assert sys.stdin.readline().strip() == 'continue'
    return build(*args)
backend.build = staticmethod(paused)
args = argparse.Namespace(run_dir=str(run), root=RBOT_ROOT)
sys.exit(oldhost.execute(args, [kind, '--run', str(run)],
    lambda receipt, code: receipt.append(code), backend()))
"""

NEW = r"""
import sys
from rbotlib import cli
from rbotlib.model.host import Model
from rbotlib.fit_host import Fit
kind, run = sys.argv[1:]
backend = Model if kind == 'model' else Fit
build, first = backend.build, True
def paused(*args):
    global first
    if first:
        first = False
        print('BOUNDARY', flush=True)
        assert sys.stdin.readline().strip() == 'continue'
    return build(*args)
backend.build = staticmethod(paused)
sys.exit(cli.main([kind, '--run', run]))
"""


def old_start(run: Path, kind: str, script: str = OLD) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [sys.executable, "-c", script, kind, str(run)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONPATH": str(RBOT_ROOT / "scripts")},
    )
    assert process.stdout is not None
    assert select.select([process.stdout], [], [], 20)[0], "original missed boundary"
    assert process.stdout.readline() == "BOUNDARY\n"
    return process


def finish(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.kill()
        process.communicate(timeout=10)


def release(process: subprocess.Popen[str]) -> None:
    assert process.stdin is not None
    process.stdin.write("continue\n")
    process.stdin.flush()
    stdout, stderr = process.communicate(timeout=20)
    assert process.returncode == 0, stdout + stderr


@pytest.mark.parametrize("kind", ["model", "fit"])
@pytest.mark.parametrize("late_registration", [False, True])
def test_original_owner_finishes_after_new_no_write_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str, late_registration: bool
) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    record = state.read(run)
    record.pop("ownership")
    (run / state.STATE).write_text(json.dumps(record))
    (run / state.LOCK).unlink()
    (run / runlog.LOCK).unlink()
    process: subprocess.Popen[str] | None = None
    read = state.read
    first = True

    def raced(selected: Path) -> state.Record:
        nonlocal process, first
        pending = read(selected)
        if first:
            first = False
            process = old_start(run, kind)
        return pending

    try:
        if late_registration:
            monkeypatch.setattr(state, "read", raced)
            with pytest.raises(RunError, match=r"legacy.*ownership"):
                state._Locked(run)
        else:
            process = old_start(run, kind)
        assert process is not None
        monkeypatch.setattr(state, "read", read)
        before = snapshot(run)
        events = observe(run, monkeypatch)
        assert cli.main([kind, "--run", str(run)]) == 1
        assert snapshot(run) == before and events == []
        release(process)
        assert read(run)["steps"][kind.upper()]["status"] == "accepted"
        assert not (run / state.LOCK).exists() and not (run / runlog.LOCK).exists()
    finally:
        if process is not None:
            finish(process)


def test_original_logger_after_terminal_snapshot_still_finishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = legacy(tmp_path, "failed")
    process = old_start(run, "logger")
    try:
        before = snapshot(run)
        events = observe(run, monkeypatch)
        assert cli.main(["inventory", "--run", str(run)]) == 1
        assert snapshot(run) == before and events == []
        release(process)
        assert (run / "log/rbot.log").read_text().endswith("old-logged-reader\t0\n")
        assert not (run / runlog.LOCK).exists()
    finally:
        finish(process)


@pytest.mark.parametrize("kind", ["model", "fit"])
def test_new_active_owner_finishes_after_contender_refusal(tmp_path: Path, kind: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    process = old_start(run, kind, NEW)
    try:
        before = snapshot(run)
        contender = subprocess.run(
            [sys.executable, str(RBOT_ROOT / "scripts/rbot.py"), kind, "--run", str(run)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert contender.returncode == 1
        assert snapshot(run) == before
        release(process)
        assert state.read(run)["steps"][kind.upper()]["status"] == "accepted"
    finally:
        finish(process)
