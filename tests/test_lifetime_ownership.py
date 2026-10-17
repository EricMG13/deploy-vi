"""Real process ownership survives rename and ends on process death."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from rbotlib import runlog, runs, state
from rbotlib.inventory import RunError


def child(run: Path, kind: str) -> subprocess.Popen[str]:
    script = """
import sys
from pathlib import Path
from rbotlib import state, runlog
run = Path(sys.argv[1])
owner = state._Locked(run) if sys.argv[2] == 'state' else runlog.Receipt(run, ['probe'])
print('owned', flush=True)
sys.stdin.readline()
owner.close()
"""
    process = subprocess.Popen(
        [sys.executable, "-c", script, str(run), kind],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path(state.__file__).parents[1])},
    )
    assert process.stdout is not None
    assert process.stdout.readline() == "owned\n"
    return process


@pytest.mark.parametrize("kind", ["state", "log"])
def test_owner_death_releases_real_lock(tmp_path: Path, kind: str) -> None:
    run = runs.create_run(tmp_path)
    process = child(run, kind)
    try:
        with pytest.raises(RunError, match=r"holds|busy"):
            if kind == "state":
                state.update(run, lambda record: record.update(probe=True))
            else:
                runlog.Receipt(run, ["contender"])
        process.kill()
        assert process.wait(timeout=10) == -9
        state.update(run, lambda record: record.update(probe=True))
        receipt = runlog.Receipt(run, ["after-death"])
        receipt.append(0)
        receipt.close()
        assert state.read(run)["probe"] is True
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)


def test_unknown_sentinel_refuses(tmp_path: Path) -> None:
    run = runs.create_run(tmp_path)
    lock = run / state.LOCK
    lock.write_bytes(b"")
    with pytest.raises(RunError, match=r"legacy|identity|protocol"):
        state.update(run, lambda record: record.update(probe=True))
    assert lock.read_bytes() == b""


def test_rename_keeps_inode_ownership(tmp_path: Path) -> None:
    run = runs.create_run(tmp_path)
    owner = state._Locked(run)
    target = run.with_name(run.name + "-renamed")
    record = state.read(run)
    try:
        run.rename(target)
        owner.run = target
        owner.owner.run = target
        record["run_id"] = target.name
        owner.commit(owner.stage(record))
        with pytest.raises(RunError, match="holds"):
            state.update(target, lambda candidate: candidate.update(probe=True))
    finally:
        assert owner.close() == []
    state.update(target, lambda candidate: candidate.update(probe=True))
    assert state.read(target)["probe"] is True


def test_replaced_lock_cannot_publish(tmp_path: Path) -> None:
    run = runs.create_run(tmp_path)
    owner = state._Locked(run)
    record = state.read(run)
    before = (run / state.STATE).read_bytes()
    try:
        lock = run / state.LOCK
        lock.rename(run / "displaced-owner")
        lock.write_bytes((run / "displaced-owner").read_bytes())
        with pytest.raises(RunError, match="identity"):
            owner.stage(record)
        assert (run / state.STATE).read_bytes() == before
    finally:
        assert "identity" in ";".join(owner.close())


def test_stale_pending_read_never_allocates_legacy_fence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import copy
    import json
    from datetime import UTC, datetime
    from uuid import uuid4

    from test_model_host import eligible

    from rbotlib.model import host
    from rbotlib.rules import RBOT_ROOT

    run = eligible(tmp_path, RBOT_ROOT)
    pending = copy.deepcopy(state.read(run))
    owner = state._Locked(run)
    token = uuid4().hex
    host._register(owner, RBOT_ROOT, datetime.now(UTC).isoformat(), token, host.Model())
    assert owner.close() == []
    registered = state.read(run)
    # An actual registered token in a throwaway legacy metadata fixture.
    for record in (pending, registered):
        record.pop("ownership")
    (run / state.LOCK).unlink()
    (run / runlog.LOCK).unlink()
    (run / state.STATE).write_text(json.dumps(registered))
    read, first = state.read, True

    def raced(selected: Path) -> state.Record:
        nonlocal first
        if first:
            first = False
            return copy.deepcopy(pending)
        return read(selected)

    monkeypatch.setattr(state, "read", raced)
    from test_legacy_ownership import observe

    events = observe(run, monkeypatch)
    with pytest.raises(RunError, match=r"legacy.*ownership"):
        state._Locked(run)
    assert read(run)["steps"]["MODEL"] == registered["steps"]["MODEL"]
    assert not (run / state.LOCK).exists()  # original legacy completion retains its fence
    assert events == []
