"""Cooperating state/log ownership and explicitly projected later recovery."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from test_model_completion import invoke
from test_model_host import eligible

from rbotlib import cli, runlog, state
from rbotlib import next as next_step
from rbotlib.inventory import RunError
from rbotlib.model import qualification
from rbotlib.model import run as writer
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("event", ["competing", "failed", "token", "unrelated"])
def test_build_time_interleavings_preserve_fresh_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, event: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    build = writer.build
    once = False
    changed: state.Record = {}

    def interleaved(
        cp1: writer.Read,
        brief: writer.Read,
        cp1d: writer.Read | None,
        generated_at: str,
        missing: str | writer.Options = "",
    ) -> tuple[writer.Written, dict[str, bytes]]:
        nonlocal once, changed
        if not once:
            once = True
            if event == "competing":
                assert invoke(run) == 1
            elif event == "failed":
                state.set_status(run, "MODEL", "failed", "public execution cancellation")
            elif event == "token":
                state.update(
                    run, lambda r: r["steps"]["MODEL"]["host_execution"].update(token="other")
                )
            else:
                state.update(run, lambda r: r.update(extension={"fresh": "preserved"}))
            changed = copy.deepcopy(state.read(run)["steps"]["MODEL"])
        return build(cp1, brief, cp1d, generated_at, missing)

    monkeypatch.setattr(writer, "build", interleaved)
    code = invoke(run)
    current = state.read(run)
    if event in ("failed", "token"):
        assert code == 1 and current["steps"]["MODEL"] == changed
        assert not any((run / name).exists() for name in qualification.OUTPUTS)
    else:
        assert code == 0 and current["steps"]["MODEL"]["attempts"] == 1
        if event == "unrelated":
            assert current["extension"] == {"fresh": "preserved"}
    if event == "competing":
        rows = (run / "log/rbot.log").read_bytes().splitlines()
        assert rows[-2].endswith(b"\t1") and rows[-1].endswith(b"\t0")


@pytest.mark.parametrize("terminal", ["accepted", "failed", "skipped", "running"])
def test_duplicate_execution_cannot_build_or_change_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, terminal: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    if terminal == "accepted":
        assert invoke(run) == 0
    elif terminal == "running":
        state.update(
            run,
            lambda r: r["steps"]["MODEL"].update(
                status="running", host_execution={"token": "orphan"}, attempts=1
            ),
        )
    else:
        state.set_status(run, "MODEL", terminal, "fixture terminal cause")
    before = (run / state.STATE).read_bytes()

    def uncalled(*args: object) -> None:
        raise AssertionError("terminal command computed")

    monkeypatch.setattr(writer, "build", uncalled)
    assert invoke(run) == 1 and (run / state.STATE).read_bytes() == before


def test_managed_log_lock_is_shared_without_recursive_acquisition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    logger = cli._log
    prefix = (run / "log/rbot.log").read_bytes()

    def checked(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        assert (run / state.LOCK).exists() and (run / runlog.LOCK).exists()
        with pytest.raises(RunError, match="log lock"):
            logger(run, ["ordinary contender"], 1)
        with pytest.raises(RunError, match="holds"):
            state.set_status(run, "MODEL", "failed", "competing completion")
        assert (run / "log/rbot.log").read_bytes() == prefix
        logger(selected, argv, code, receipt=receipt)

    monkeypatch.setattr(cli, "_log", checked)
    assert invoke(run) == 0
    assert len((run / "log/rbot.log").read_bytes()[len(prefix) :].splitlines()) == 1


@pytest.mark.parametrize("lock", [state.LOCK, runlog.LOCK])
def test_lock_contention_keeps_other_owner_bytes(tmp_path: Path, lock: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    path = run / lock
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(b"other owner")
    before = (run / state.STATE).read_bytes()
    assert invoke(run) == 1 and path.read_bytes() == b"other owner"
    if lock == state.LOCK:
        assert (run / state.STATE).read_bytes() == before
    else:
        assert state.read(run)["steps"]["MODEL"]["status"] == "failed"


def test_projected_accepted_edit_required_failure_cannot_skip_running_host(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    # Current public CP-1 terminal edits refuse; this fixture projects the later06.9 owner.
    with pytest.raises(RunError, match="cannot set blocked to failed"):
        state.set_status(run, "CP-1", "failed", "future accepted-edit invalidation")

    def projection(record: state.Record) -> None:
        record["steps"]["CP-1"].update(status="failed", reason="projected06.9 invalidation")
        record["steps"]["MODEL"].update(
            status="running", attempts=1, host_execution={"token": "projected"}
        )

    state.update(run, projection)
    before = (run / state.STATE).read_bytes()
    with pytest.raises(RunError, match="latest validation differs"):
        next_step.select(run, RBOT_ROOT)
    projected = copy.deepcopy(state.read(run))
    needs = {"CP-0": (), "CP-1": ("CP-0",), "MODEL": ("CP-1",)}
    projected["plan"] = list(needs)
    with pytest.raises(RunError, match="registered running evidence"):
        next_step._traverse(projected, needs)
    assert (run / state.STATE).read_bytes() == before


def test_registration_cleanup_uncertainty_cannot_compute_or_create_another_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    unlink = Path.unlink

    def broken(path: Path, missing_ok: bool = False) -> None:
        if path == run / state.LOCK:
            raise OSError("registration lock cleanup failed")
        unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", broken)
    assert invoke(run) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "running" and current["attempts"] == 1
    assert not any((run / name).exists() for name in qualification.OUTPUTS)
    assert "persisted=True" in capsys.readouterr().err


def test_actual_completion_acquires_state_before_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    state_init, log_init = state._Locked.__init__, runlog.Receipt.__init__
    acquired = []

    def state_owned(owner: state._Locked, selected: Path) -> None:
        state_init(owner, selected)
        acquired.append("state")

    def log_owned(receipt: runlog.Receipt, selected: Path, argv: list[str]) -> None:
        log_init(receipt, selected, argv)
        acquired.append("log")

    monkeypatch.setattr(state._Locked, "__init__", state_owned)
    monkeypatch.setattr(runlog.Receipt, "__init__", log_owned)
    assert invoke(run) == 0
    assert acquired == ["state", "log"]
