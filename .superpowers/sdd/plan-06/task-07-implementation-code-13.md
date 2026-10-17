# Task06.7 exact replay file 13

Source: `tests/test_model_completion.py`; complete executed bytes, SHA256 `0e60cb9050f3c9bb4b68a7b0605cb6349bd294fda73b1fc98d1a32c1699cceeb`, 11652 bytes, 307 LF. Baseline1094a76; final source tree/proof is recorded separately. This ordinary whole file receives no cap exemption.

```python
"""Causal managed lifecycle failures through actual logger and filesystem seams."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from test_model_host import eligible

from rbotlib import cli, runlog, state
from rbotlib.model import qualification
from rbotlib.model import run as writer
from rbotlib.rules import RBOT_ROOT


def invoke(run: Path) -> int:
    return cli.main(["model", "--run", str(run)])


def failed(run: Path, prefix: bytes) -> state.Record:
    current: state.Record = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed" and current["host_exit"] == 1
    assert current["attempts"] == 1 and current["host_execution"]["token"]
    assert current["finished_at"] and current["started_at"]
    raw = (run / "log/rbot.log").read_bytes()
    assert raw.startswith(prefix)
    assert len(raw[len(prefix) :].splitlines()) == 1 and raw.endswith(b"\t1\n")
    assert not (run / state.LOCK).exists() and not (run / runlog.LOCK).exists()
    return current


@pytest.mark.parametrize("mode", ["before", "partial", "close"])
def test_real_logger_failure_resolves_one_owned_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    logger = cli._log

    def broken(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        assert receipt is not None and (run / state.LOCK).exists()
        assert state.read(run)["steps"]["MODEL"]["status"] == "running"
        if mode == "partial":
            with (run / "log/rbot.log").open("ab") as stream:
                stream.write(receipt.row[:17])
        elif mode == "close":
            logger(selected, argv, code, receipt=receipt)
        raise OSError(f"fixture log {mode} failure")

    monkeypatch.setattr(cli, "_log", broken)
    assert invoke(run) == 1
    assert "log" in failed(run, prefix)["reason"]


@pytest.mark.parametrize(
    "phase", ["stage1", "stage2", "stage3", "replace1", "replace2", "replace3"]
)
def test_each_output_io_failure_is_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    stage, replace = writer.stage_file, os.replace
    stages: list[str] = []
    replacements: list[str] = []

    def staged(target: Path, raw: bytes) -> Path:
        if target.name in ("model.json", "model.xlsx", "MODEL.md"):
            stages.append(target.name)
            if phase == f"stage{len(stages)}":
                raise OSError(f"fixture {phase} denied")
        return stage(target, raw)

    def replaced(source: Path, target: Path) -> None:
        if target.name in ("model.json", "model.xlsx", "MODEL.md"):
            assert stages == ["model.json", "model.xlsx", "MODEL.md"]
            replacements.append(target.name)
            if phase == f"replace{len(replacements)}":
                raise OSError(f"fixture {phase} denied")
        replace(source, target)

    monkeypatch.setattr(writer, "stage_file", staged)
    monkeypatch.setattr(os, "replace", replaced)
    assert invoke(run) == 1
    assert phase in failed(run, prefix)["reason"]
    if phase.startswith("stage"):
        assert not any((run / name).exists() for name in qualification.OUTPUTS)
    assert not list(run.glob(".model*")) and not list((run / "handoffs").glob(".MODEL*"))


@pytest.mark.parametrize("name", qualification.OUTPUTS)
def test_each_output_readback_failure_is_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    read = Path.read_bytes

    def broken(path: Path) -> bytes:
        if path == run / name:
            raise OSError("fixture readback denied")
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", broken)
    assert invoke(run) == 1
    assert "readback" in failed(run, prefix)["reason"]


@pytest.mark.parametrize("mode", ["candidate", "accepted-once", "persistent", "failed"])
def test_state_failure_does_not_leave_accepted_public_one_or_log_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    commit, stage = state._Locked.commit, state._Locked.stage
    calls = 0

    def broken(owner: state._Locked, staged: Path) -> None:
        nonlocal calls
        calls += 1
        if mode == "persistent" or (mode == "accepted-once" and calls == 1):
            raise OSError("fixture state publication denied")
        commit(owner, staged)

    def staging(owner: state._Locked, record: state.Record) -> Path:
        if record["steps"]["MODEL"]["status"] == ("failed" if mode == "failed" else "accepted"):
            if mode in ("candidate", "failed"):
                raise OSError("fixture state staging denied")
        return stage(owner, record)

    monkeypatch.setattr(state._Locked, "commit", broken)
    monkeypatch.setattr(state._Locked, "stage", staging)
    if mode == "failed":
        monkeypatch.setattr(
            writer, "build", lambda *args: (_ for _ in ()).throw(ValueError("build cause"))
        )
    assert invoke(run) == 1
    current = state.read(run)["steps"]["MODEL"]
    if mode in ("persistent", "failed"):
        assert current["status"] == "running" and current["host_execution"]["token"]
        assert "failure attribution refused" in capsys.readouterr().err
        before = (run / state.STATE).read_bytes()
        assert invoke(run) == 1 and (run / state.STATE).read_bytes() == before
    else:
        assert "state" in failed(run, prefix)["reason"]
    raw = (run / "log/rbot.log").read_bytes()
    assert raw.startswith(prefix) and raw.endswith(b"\t1\n")


def test_state_replace_oserror_after_log_zero_corrects_exact_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    replace = os.replace
    calls = 0

    def once(source: Path, target: Path) -> None:
        nonlocal calls
        if target == run / state.STATE:
            calls += 1
            if calls == 2:  # registration is the first; accepted publication is the second
                assert (run / "log/rbot.log").read_bytes().endswith(b"\t0\n")
                raise OSError("actual accepted state replace denied")
        replace(source, target)

    monkeypatch.setattr(os, "replace", once)
    assert invoke(run) == 1
    assert "replace denied" in failed(run, prefix)["reason"]
    assert calls == 3


def test_failed_log_correction_exposes_actual_integrity_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    logger = cli._log

    def closed(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        logger(selected, argv, code, receipt=receipt)
        raise OSError("fixture log close denied")

    def refused(receipt: runlog.Receipt) -> None:
        raise OSError("fixture correction denied")

    monkeypatch.setattr(cli, "_log", closed)
    monkeypatch.setattr(runlog.Receipt, "fail", refused)
    assert invoke(run) == 1
    assert state.read(run)["steps"]["MODEL"]["status"] == "failed"
    assert (run / "log/rbot.log").read_bytes().endswith(b"\t0\n")
    assert "log resolution failed" in capsys.readouterr().err


@pytest.mark.parametrize("lock", [state.LOCK, runlog.LOCK])
def test_postcommit_cleanup_failure_preserves_public_zero_and_fenced_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], lock: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    unlink = Path.unlink

    def refused(path: Path, missing_ok: bool = False) -> None:
        if path == run / lock and state.read(run)["steps"]["MODEL"]["status"] == "accepted":
            raise OSError("fixture cleanup denied")
        unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", refused)
    assert invoke(run) == 0
    current = state.read(run)
    assert current["steps"]["MODEL"]["host_exit"] == 0
    qualification.qualify(run, RBOT_ROOT, current)
    assert (run / lock).exists() and "cleanup" in capsys.readouterr().err


def test_required_stdout_failure_precedes_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()

    original_flush = sys.stdout.flush
    once = False

    def refused() -> None:
        nonlocal once
        if not once:
            once = True
            raise OSError("fixture stdout flush denied")
        original_flush()

    monkeypatch.setattr(sys.stdout, "flush", refused)
    assert invoke(run) == 1
    assert "stdout" in failed(run, prefix)["reason"]


def test_build_failure_retains_actual_failed_outcome_logger_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()

    def build_error(*args: object) -> None:
        raise ValueError("actual build cause")

    def log_error(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        raise OSError("actual failed-outcome logger denied")

    monkeypatch.setattr(writer, "build", build_error)
    monkeypatch.setattr(cli, "_log", log_error)
    assert invoke(run) == 1
    reason = failed(run, prefix)["reason"]
    assert "actual build cause" in reason and "logger denied" in reason


def test_closed_stderr_after_proven_commit_cannot_change_public_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    unlink = Path.unlink

    def cleanup(path: Path, missing_ok: bool = False) -> None:
        if path == run / state.LOCK and state.read(run)["steps"]["MODEL"]["status"] == "accepted":
            raise OSError("actual postcommit cleanup denied")
        unlink(path, missing_ok=missing_ok)

    def closed(text: str) -> int:
        raise ValueError("actual stderr is closed")

    monkeypatch.setattr(Path, "unlink", cleanup)
    monkeypatch.setattr(sys.stderr, "write", closed)
    assert invoke(run) == 0
    assert state.read(run)["steps"]["MODEL"]["status"] == "accepted"


def test_uncorrectable_partial_log_retains_observed_partial_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    replace = os.replace

    def partial(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        assert receipt is not None
        with (run / "log/rbot.log").open("ab") as stream:
            stream.write(receipt.row[:17])
        raise OSError("actual partial logger failure")

    def denied(source: Path, target: Path) -> None:
        if target == run / "log/rbot.log":
            raise OSError("actual correction replace denied")
        replace(source, target)

    monkeypatch.setattr(cli, "_log", partial)
    monkeypatch.setattr(os, "replace", denied)
    assert invoke(run) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed"
    assert current["completion_failure"]["log_state"] == "partial"
    assert "actual correction replace denied" in current["reason"]
```

Not verified: independent acceptance, whole06.16 branch gates, later06, live/provider/platform/crash behavior.
