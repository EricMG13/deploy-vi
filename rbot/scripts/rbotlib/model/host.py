"""Managed CLI outcome owner: token, pair, output, log, then state commit."""

from __future__ import annotations

import argparse
import copy
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Generic, Protocol, TypeVar
from uuid import uuid4

from rbotlib import dispatch, runlog, state
from rbotlib import next as next_step
from rbotlib.inventory import RunError
from rbotlib.model import qualification as proof
from rbotlib.model import run as writer

ERRORS = (OSError, ValueError, KeyError, TypeError, RecursionError)
Appender = Callable[[runlog.Receipt, int], None]


class Snapshot(Protocol):
    @property
    def missing(self) -> str: ...

    def hashes(self) -> dict[str, str | None]: ...


class Result(Protocol):
    @property
    def qa_status(self) -> str: ...


C = TypeVar("C", bound=Snapshot)
W = TypeVar("W", bound=Result)


class Backend(Protocol[C, W]):
    step: str
    origin: str
    handoff: str

    def inputs(self, run: Path, root: Path, record: state.Record) -> C: ...
    def outputs(self, captured: C) -> tuple[str, ...]: ...
    def build(self, captured: C, generated_at: str) -> tuple[W, dict[str, bytes]]: ...
    def validate(
        self, files: dict[str, bytes], captured: C, record: state.Record, generated_at: str
    ) -> W: ...
    def show(self, written: W) -> None: ...


@dataclass(frozen=True, slots=True)
class Execution(Generic[C, W]):
    run: Path
    root: Path
    token: str
    captured: C
    generated_at: str
    backend: Backend[C, W]


def _diagnostic(message: str) -> None:
    try:
        print(f"host: {message}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        return  # diagnostic failure cannot change the decided outcome


def _owned(record: state.Record, token: str, module: str) -> state.Record:
    current: state.Record = record["steps"][module]
    evidence = current.get("host_execution")
    if (
        current["status"] != "running"
        or not isinstance(evidence, dict)
        or evidence.get("token") != token
    ):
        raise RunError(f"{module}: execution no longer owns its running token; result preserved")
    return current


def _register(
    owner: state._Locked, root: Path, generated_at: str, token: str, backend: Backend[C, W]
) -> C:
    run = owner.run
    captured: C | None = None
    module = backend.step

    def start(record: state.Record) -> None:
        nonlocal captured
        current = record["steps"].get(module, {})
        if current.get("kind") != "host" or current.get("status") != "pending":
            raise RunError(f"{module}: execution requires pending; current {current.get('status')}")
        if current.get("attempts", 0) or "host_execution" in current:
            raise RunError(f"{module}: unexplained execution evidence; recovery required")
        captured = backend.inputs(run, root, record)
        if next_step._selection(run, root, record)[0]["step"] != module:
            raise RunError(f"{module}: not the first eligible approved step")
        if any(dispatch._target(run, name).exists() for name in backend.outputs(captured)):
            raise RunError(f"{module}: unregistered outputs require the recovery owner")
        current.update(
            status="running",
            attempts=1,
            started_at=generated_at,
            host_execution={
                "token": token,
                "origin": backend.origin,
                "generated_at": generated_at,
                "inputs": captured.hashes(),
                "optional_exclusion": captured.missing,
            },
        )

    try:
        record = state.read(run)
        start(record)
        owner.commit(owner.stage(record))
    except ERRORS as exc:
        raise _registration_error(run, token, module, exc) from exc
    if captured is None:
        raise RunError(f"{module} registration did not capture qualified inputs; token={token}")
    return captured


def _registration_error(run: Path, token: str, module: str, cause: Exception) -> RunError:
    try:
        current = state.read(run)["steps"].get(module, {})
        evidence = current.get("host_execution")
        persisted = isinstance(evidence, dict) and evidence.get("token") == token
    except ERRORS:
        persisted = None
    return RunError(
        f"registration refused/uncertain; token={token}; persisted={persisted}: {cause}"
    )


def _publish(run: Path, files: dict[str, bytes]) -> None:
    for name in files:
        dispatch._target(run, name).parent.mkdir(exist_ok=True)
    writer.write_all({dispatch._target(run, name): raw for name, raw in files.items()})
    readback = {name: dispatch._file(run, name).read_bytes() for name in files}
    if readback != files:
        raise RunError("host: published outputs differ from this execution")


def _show(written: writer.Written) -> None:
    print(f"model.json and handoffs/MODEL.md written; qa_status {written.qa_status}")
    for limitation in written.limitations:
        print(f"{limitation.code}: {limitation.message}")
    sys.stdout.flush()


def _failed(
    owner: state._Locked,
    execution: Execution[C, W],
    cause: Exception,
    phase: str,
    receipt: runlog.Receipt | None,
) -> str:
    """Build a separate failed candidate from fresh state under unchanged ownership."""
    token, module = execution.token, execution.backend.step
    message = f"token={token}; phase={phase}; {cause}"
    try:
        record = state.read(owner.run)
        current = _owned(record, token, module)
        current.update(
            status="failed",
            host_exit=1,
            reason=f"{module} execution: {message}",
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
    owner: state._Locked | None = None,
) -> tuple[runlog.Receipt | None, str]:
    try:
        if receipt is None:
            receipt = runlog.Receipt(run, argv, owner)
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
    execution: Execution[C, W],
    built: tuple[W, dict[str, bytes]] | Exception,
    argv: list[str],
    append_log: Appender,
    owner: state._Locked,
) -> int:
    run, root, token, captured = (
        execution.run,
        execution.root,
        execution.token,
        execution.captured,
    )
    backend, module = execution.backend, execution.backend.step
    receipt: runlog.Receipt | None = None
    result, phase = 1, "build"
    try:
        if isinstance(built, Exception):
            raise built
        written, files = built
        phase = "qualification"
        record = state.read(run)
        current = _owned(record, token, module)
        fresh = backend.inputs(run, root, record)
        if fresh != captured:
            raise RunError(f"{module}: qualified inputs changed during execution")
        checked = backend.validate(files, fresh, record, current["host_execution"]["generated_at"])
        candidate = copy.deepcopy(record)
        hashes = proof._hashes(files)
        candidate["steps"][module].update(
            status="accepted",
            host_exit=0,
            qa_status=checked.qa_status,
            handoff=backend.handoff,
            sha256=hashes[backend.handoff],
            outputs=hashes,
            reason="",
            finished_at=datetime.now(UTC).isoformat(),
        )
        phase = "candidate staging"
        staged = owner.stage(candidate)
        phase = "output publication/readback"
        _publish(run, files)
        phase = "required command output"
        backend.show(written)
        phase = "log"
        receipt = runlog.Receipt(run, argv, owner)
        append_log(receipt, 0)
        phase = "accepted state publication"
        owner.commit(staged)
        result = 0  # no fallible outcome-changing work follows this commit
    except ERRORS as exc:
        receipt, log_error = _resolve_log(run, argv, receipt, append_log, owner)
        cause = RunError(f"{exc}{log_error}") if log_error else exc
        message = _failed(owner, execution, cause, phase, receipt)
        _diagnostic(message)
    finally:
        if receipt is not None:
            try:
                receipt.close()
            except ERRORS as exc:
                _diagnostic(f"log cleanup; result={result}: {exc}")
    return result


def execute(
    args: argparse.Namespace, argv: list[str], append_log: Appender, backend: Backend[C, W]
) -> int:
    """Selected before CLI execution; all exits here own their single command row."""
    selected = Path(args.run_dir)
    token = uuid4().hex
    owner = None
    try:
        run, root = state.run_path(selected), dispatch._root(args.root)
        owner = state._Locked(run)
        generated_at = datetime.now(UTC).isoformat()
        captured = _register(owner, root, generated_at, token, backend)
        execution = Execution(run, root, token, captured, generated_at, backend)
        try:
            built: tuple[W, dict[str, bytes]] | Exception = backend.build(captured, generated_at)
        except ERRORS as exc:
            built = exc
        return _complete(execution, built, argv, append_log, owner)
    except ERRORS as exc:
        _diagnostic(f"{exc}; token={token}; uncommitted outcome; recovery may be required")
        if owner is None:
            return 1  # refusal never acquires unrelated publication/log ownership
        receipt, error = _resolve_log(selected, argv, None, append_log, owner)
        if error:
            _diagnostic(error)
        if receipt is not None:
            try:
                receipt.close()
            except ERRORS as cleanup:
                _diagnostic(f"log cleanup: {cleanup}")
        return 1
    finally:
        if owner is not None:
            for warning in owner.close():
                _diagnostic(warning)


class Model:
    step, origin, handoff = "MODEL", "host-model/1", "handoffs/MODEL.md"
    inputs = staticmethod(proof.inputs)
    validate = staticmethod(proof.validate)
    show = staticmethod(_show)

    @staticmethod
    def outputs(captured: proof.Inputs) -> tuple[str, ...]:
        return proof.OUTPUTS

    @staticmethod
    def build(captured: proof.Inputs, generated_at: str) -> tuple[writer.Written, dict[str, bytes]]:
        return writer.build(
            captured.cp1,
            captured.brief,
            captured.cp1d,
            generated_at,
            writer.Options(captured.missing, managed=True),
        )


def run(args: argparse.Namespace, argv: list[str], append_log: Appender) -> int:
    return execute(args, argv, append_log, Model())
