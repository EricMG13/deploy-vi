"""One-shot public host child boundaries with real backend execution."""

from __future__ import annotations

import os
import select
import subprocess
import sys
from pathlib import Path

from conftest import HANG_TIMEOUT
from rbotlib.rules import RBOT_ROOT

CHILD = """
import json, os, sys
from pathlib import Path
from rbotlib import cli, state
from rbotlib.model.host import Model
from rbotlib.fit_host import Fit
kind, run, phase, root = sys.argv[1:]
backend = Model if kind == 'model' else Fit
build, replace = backend.build, os.replace
paused = False
def pause():
    global paused
    if not paused:
        paused = True
        print('BOUNDARY', flush=True)
        assert sys.stdin.readline().strip() == 'continue'
def building(*args):
    if phase == 'build': pause()
    result = build(*args)
    print('BUILT', flush=True)
    if phase == 'built': pause()
    if phase == 'failure': raise OSError('controlled caught build failure')
    return result
def replaced(source, target):
    replace(source, target)
    target = Path(target)
    if phase == 'output' and target.name == backend.step + '.md': pause()
    if phase == 'output-' + target.name: pause()
    if phase == 'log' and target.name == 'rbot.log': pause()
    if target.name == state.STATE:
        current = json.loads(target.read_text())['steps'].get(backend.step, {})
        invocation = current.get('host_execution', {}).get('invocations', [{}])[-1]
        if phase == 'intent' and invocation.get('receipt'): pause()
        if phase == 'commit' and current.get('status') == 'accepted': pause()
        if phase == 'failure' and invocation.get('failure'): pause()
        if phase == 'correction' and invocation.get('receipt', {}).get('code') == 1: pause()
backend.build = staticmethod(building)
os.replace = replaced
logger = cli._log
def correction(*args, **kwargs):
    logger(*args, **kwargs)
    if args[2] == 0: raise OSError('controlled caught logger failure')
if phase == 'correction': cli._log = correction
sys.exit(cli.main(['--root', root, kind, '--run', run]))
"""


def start(run: Path, kind: str, phase: str, root: Path = RBOT_ROOT) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [sys.executable, "-c", CHILD, kind, str(run), phase, str(root)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONPATH": os.pathsep.join([str(RBOT_ROOT / "scripts")])},
    )
    assert process.stdout is not None
    assert select.select([process.stdout], [], [], HANG_TIMEOUT)[0], "host missed target boundary"
    # Required command output can precede a later boundary.
    while process.stdout.readline().strip() != "BOUNDARY":
        assert process.poll() is None, "host exited before target boundary"
    return process


def finish(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.kill()
        process.communicate(timeout=HANG_TIMEOUT)


def command(run: Path, kind: str, root: Path = RBOT_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(root / "scripts/rbot.py"),
            "--root",
            str(root),
            kind,
            "--run",
            str(run),
        ],
        capture_output=True,
        text=True,
        timeout=HANG_TIMEOUT,
        check=False,
    )
