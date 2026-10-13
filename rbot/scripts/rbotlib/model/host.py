"""Managed CLI outcome owner: token, trio, output, log, then state commit."""

from __future__ import annotations

import argparse
import copy
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rbotlib import dispatch, runlog, state
from rbotlib import next as next_step
from rbotlib.inventory import RunError
from rbotlib.model import qualification as proof
from rbotlib.model import run as writer

ERRORS = (OSError, ValueError, KeyError, TypeError, RecursionError)
Appender = Callable[[runlog.Receipt, int], None]


@dataclass(frozen=True, slots=True)
class Execution:
    run: Path
    root: Path
    token: str
    captured: proof.Inputs
    generated_at: str


def _diagnostic(message: str) -> None:
    try:
        print(f"model: {message}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        return  # diagnostic failure cannot change the decided outcome


def _owned(record: state.Record, token: str) -> state.Record:
    current: state.Record = record["steps"]["MODEL"]
    evidence = current.get("host_execution")
    if (
        current["status"] != "running"
        or not isinstance(evidence, dict)
        or evidence.get("token") != token
    ):
        raise RunError("MODEL: execution no longer owns its running token; result preserved")
    return current


def _register(run: Path, root: Path, generated_at: str, token: str) -> proof.Inputs:
    captured: proof.Inputs | None = None

    def start(record: state.Record) -> None:
        nonlocal captured
        current = record["steps"].get("MODEL", {})
        if current.get("kind") != "host" or current.get("status") != "pending":
            raise RunError(f"MODEL: execution requires pending; current {current.get('status')}")
        if current.get("attempts", 0) or "host_execution" in current:
            raise RunError("MODEL: unexplained execution evidence; recovery required")
        captured = proof.inputs(run, root, record)
        if next_step._selection(run, root, record)[0]["step"] != "MODEL":
            raise RunError("MODEL: not the first eligible approved step")
        if any(dispatch._target(run, name).exists() for name in proof.OUTPUTS):
            raise RunError("MODEL: unregistered outputs require the recovery owner")
        current.update(
            status="running",
            attempts=1,
            started_at=generated_at,
            host_execution={
                "token": token,
                "origin": "host-model/1",
                "generated_at": generated_at,
                "inputs": captured.hashes(),
                "optional_exclusion": captured.missing,
            },
        )

    try:
        state.update(run, start)
    except ERRORS as exc:
        raise _registration_error(run, token, exc) from exc
    if captured is None:
        raise RunError(f"MODEL registration did not capture qualified inputs; token={token}")
    return captured


def _registration_error(run: Path, token: str, cause: Exception) -> RunError:
    try:
        current = state.read(run)["steps"].get("MODEL", {})
        evidence = current.get("host_execution")
        persisted = isinstance(evidence, dict) and evidence.get("token") == token
    except ERRORS:
        persisted = None
    return RunError(
        f"registration refused/uncertain; token={token}; persisted={persisted}: {cause}"
    )


def _publish(run: Path, files: dict[str, bytes]) -> None:
    writer.write_all({dispatch._target(run, name): raw for name, raw in files.items()})
    readback = {name: dispatch._file(run, name).read_bytes() for name in proof.OUTPUTS}
    if readback != files:
        raise RunError("MODEL: published trio differs from this execution")


def _show(written: writer.Written) -> None:
    print(f"model.json, model.xlsx and handoffs/MODEL.md written; qa_status {written.qa_status}")
    for limitation in written.limitations:
        print(f"{limitation.code}: {limitation.message}")
    sys.stdout.flush()


def _failed(
    owner: state._Locked,
    token: str,
    cause: Exception,
    phase: str,
    receipt: runlog.Receipt | None,
) -> str:
    """Build a separate failed candidate from fresh state under unchanged ownership."""
    message = f"token={token}; phase={phase}; {cause}"
    try:
        record = state.read(owner.run)
        current = _owned(record, token)
        current.update(
            status="failed",
            host_exit=1,
            reason=f"MODEL execution: {message}",
            finished_at=datetime.now(UTC).isoformat(),
            completion_failure={
                "phase": phase,
                "log_state": receipt.state if receipt else "missing",
            },
        )
        owner.commit(owner.stage(record))
    except ERRORS as exc:
        message += f"; failure attribution refused (uncommitted/recovery required): {exc}"
    return message


def _resolve_log(
    run: Path,
    argv: list[str],
    receipt: runlog.Receipt | None,
    append_log: Appender,
) -> tuple[runlog.Receipt | None, str]:
    try:
        if receipt is None:
            receipt = runlog.Receipt(run, argv)
            try:
                append_log(receipt, 1)
            except ERRORS as append_error:
                try:
                    receipt.fail()
                except ERRORS as correction_error:
                    raise RunError(
                        f"log append failed: {append_error}; correction failed: {correction_error}"
                    ) from append_error
                return receipt, f"; log append failed (row1 corrected): {append_error}"
        else:
            receipt.fail()
    except ERRORS as exc:
        known = receipt.state if receipt else "unobserved"
        return receipt, f"; log resolution failed; known={known}: {exc}"
    else:
        return receipt, ""


def _complete(
    execution: Execution,
    built: tuple[writer.Written, dict[str, bytes]] | Exception,
    argv: list[str],
    append_log: Appender,
) -> int:
    run, root, token, captured = (
        execution.run,
        execution.root,
        execution.token,
        execution.captured,
    )
    owner = state._Locked(run)
    receipt: runlog.Receipt | None = None
    result, phase = 1, "build"
    try:
        if isinstance(built, Exception):
            raise built
        written, files = built
        phase = "qualification"
        record = state.read(run)
        current = _owned(record, token)
        fresh = proof.inputs(run, root, record)
        if fresh != captured:
            raise RunError("MODEL: qualified inputs changed during execution")
        checked = proof.validate(files, fresh, record, current["host_execution"]["generated_at"])
        candidate = copy.deepcopy(record)
        hashes = proof._hashes(files)
        candidate["steps"]["MODEL"].update(
            status="accepted",
            host_exit=0,
            qa_status=checked.qa_status,
            handoff="handoffs/MODEL.md",
            sha256=hashes["handoffs/MODEL.md"],
            outputs=hashes,
            reason="",
            finished_at=datetime.now(UTC).isoformat(),
        )
        phase = "candidate staging"
        staged = owner.stage(candidate)
        phase = "output publication/readback"
        _publish(run, files)
        phase = "required command output"
        _show(written)
        phase = "log"
        receipt = runlog.Receipt(run, argv)
        append_log(receipt, 0)
        phase = "accepted state publication"
        owner.commit(staged)
        result = 0  # no fallible outcome-changing work follows this commit
    except ERRORS as exc:
        receipt, log_error = _resolve_log(run, argv, receipt, append_log)
        cause = RunError(f"{exc}{log_error}") if log_error else exc
        message = _failed(owner, token, cause, phase, receipt)
        _diagnostic(message)
    finally:
        if receipt is not None:
            try:
                receipt.close()
            except ERRORS as exc:
                _diagnostic(f"log cleanup; result={result}: {exc}")
        for warning in owner.close():
            _diagnostic(f"{warning}; result={result}")
    return result


def run(args: argparse.Namespace, argv: list[str], append_log: Appender) -> int:
    """Selected before CLI execution; all exits here own their single command row."""
    selected = Path(args.run_dir)
    token = uuid4().hex
    try:
        run, root = state.run_path(selected), dispatch._root(args.root)
        generated_at = datetime.now(UTC).isoformat()
        captured = _register(run, root, generated_at, token)
        execution = Execution(run, root, token, captured, generated_at)
        try:
            built: tuple[writer.Written, dict[str, bytes]] | Exception = writer.build(
                captured.cp1,
                captured.brief,
                captured.cp1d,
                generated_at,
                writer.Options(captured.missing, managed=True),
            )
        except ERRORS as exc:
            built = exc
        return _complete(execution, built, argv, append_log)
    except ERRORS as exc:
        _diagnostic(f"{exc}; token={token}; uncommitted outcome; recovery may be required")
        receipt, error = _resolve_log(selected, argv, None, append_log)
        if error:
            _diagnostic(error)
        if receipt is not None:
            try:
                receipt.close()
            except ERRORS as cleanup:
                _diagnostic(f"log cleanup: {cleanup}")
        return 1
