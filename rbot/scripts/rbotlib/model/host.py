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

from rbotlib import dispatch, host_evidence, runlog, state
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
    captured: C | None
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
    host_evidence.checked(record, module, f"host-{module.lower()}/1")
    return current


def _initial(execution: Execution[C, W], captured: C, record: state.Record) -> state.Record:
    module = execution.backend.step
    current = record["steps"][module]
    if current.get("attempts", 0) or "host_execution" in current:
        raise RunError(f"{module}: unexplained execution evidence; recovery required")
    if any(
        dispatch._target(execution.run, name).exists()
        for name in execution.backend.outputs(captured)
    ):
        raise RunError(f"{module}: unregistered outputs require the recovery owner")
    evidence = {
        "schema": host_evidence.SCHEMA,
        "token": execution.token,
        "origin": execution.backend.origin,
        "generated_at": execution.generated_at,
        "inputs": captured.hashes(),
        "optional_exclusion": captured.missing,
        "ownership": record["ownership"],
        "context": host_evidence.context(execution.root, record),
        "invocations": [],
    }
    evidence["binding"] = host_evidence.binding(evidence)
    return evidence


def _register(
    owner: state._Locked, root: Path, generated_at: str, token: str, backend: Backend[C, W]
) -> C | None:
    run, module = owner.run, backend.step
    record = state.read(run)
    current = record["steps"].get(module, {})
    if current.get("kind") != "host" or current.get("status") not in ("pending", "running"):
        raise RunError(
            f"{module}: execution requires pending/running; status {current.get('status')}"
        )
    if current["status"] == "running":
        previous = host_evidence.checked(record, module, backend.origin)
        if any("failure" in i for i in previous["invocations"]):
            host_evidence.invocation(record, module, run)
            owner.commit(owner.stage(record))
            return None  # resolve known terminal failure; never reread/rebuild corrected inputs
    captured = backend.inputs(run, root, record)
    if next_step._selection(run, root, record)[0]["step"] != module:
        raise RunError(f"{module}: not the first eligible approved step")
    if current["status"] == "pending":
        execution = Execution(run, root, token, captured, generated_at, backend)
        evidence = _initial(execution, captured, record)
        current.update(
            status="running", attempts=1, started_at=generated_at, host_execution=evidence
        )
    else:
        evidence = host_evidence.checked(record, module, backend.origin)
        host_evidence.match_inputs(
            evidence, captured.hashes(), captured.missing, host_evidence.context(root, record)
        )
    host_evidence.invocation(record, module, run)
    try:
        owner.commit(owner.stage(record))
    except ERRORS as exc:
        raise _registration_error(run, token, module, exc) from exc
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


def _reconcile(run: Path, files: dict[str, bytes]) -> None:
    for name, raw in files.items():
        target = dispatch._target(run, name)
        if target.exists() and dispatch._file(run, name).read_bytes() != raw:
            raise RunError(f"host: conflicting output {name}; preserved")


def _publish(owner: state._Locked, files: dict[str, bytes]) -> None:
    run = owner.run
    owner.owner.check()
    for name in files:
        dispatch._target(run, name).parent.mkdir(exist_ok=True)
    writer.write_all(
        {dispatch._target(run, name): raw for name, raw in files.items()}, owner.owner.check
    )
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
        invocation = current["host_execution"]["invocations"][-1]
        invocation.update(exit=1, completion="completed", finished_at=datetime.now(UTC).isoformat())
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
        receipt.owner.check()
        actual = runlog.path(run).read_bytes() if runlog.path(run).exists() else b""
        if receipt.state == "missing" and actual == receipt.prefix:
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


def _candidate(
    owner: state._Locked, module: str, receipt: runlog.Receipt, candidate: state.Record
) -> Path:
    host_evidence.intent(owner, module, receipt, 0)
    candidate["steps"][module]["host_execution"] = copy.deepcopy(
        state.read(owner.run)["steps"][module]["host_execution"]
    )
    invocation = candidate["steps"][module]["host_execution"]["invocations"][-1]
    invocation.update(exit=0, completion="completed", finished_at=datetime.now(UTC).isoformat())
    return owner.stage(candidate)


def _failure_intent(
    owner: state._Locked,
    execution: Execution[C, W],
    argv: list[str],
    receipt: runlog.Receipt | None,
    cause: Exception,
) -> runlog.Receipt | None:
    module, token = execution.backend.step, execution.token
    try:
        record = state.read(owner.run)
        current = _owned(record, token, module)
        current["host_execution"]["invocations"][-1]["failure"] = str(cause)
        owner.commit(owner.stage(record))
        if receipt is None:
            receipt = runlog.Receipt(owner.run, argv, owner)
        host_evidence.intent(owner, module, receipt, 1)
    except ERRORS as persistence:
        _diagnostic(f"failure attribution refused: {persistence}")
    return receipt


def _commit_accepted(
    owner: state._Locked,
    receipt: runlog.Receipt,
    staged: Path,
    candidate: state.Record,
    execution: Execution[C, W],
) -> None:
    run, root, backend = execution.run, execution.root, execution.backend
    current = state.read(run)
    _owned(current, execution.token, backend.step)
    fresh = backend.inputs(run, root, current)
    if fresh != execution.captured:
        raise RunError("host: qualified inputs changed before accepted commit")
    files = {name: dispatch._file(run, name).read_bytes() for name in backend.outputs(fresh)}
    backend.validate(files, fresh, current, execution.generated_at)
    host_evidence.accepted(candidate, backend.step, backend.origin, run, root)
    receipt.owner.check()
    owner.commit(staged)


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
        if captured is None:
            raise RunError("host: captured execution inputs missing")
        written, files = built
        phase = "qualification"
        record = state.read(run)
        current = _owned(record, token, module)
        fresh = backend.inputs(run, root, record)
        if fresh != captured or current["host_execution"]["context"] != host_evidence.context(
            root, record
        ):
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
        phase = "output publication/readback"
        _reconcile(run, files)
        _publish(owner, files)
        phase = "required command output"
        backend.show(written)
        phase = "log"
        _reconcile(run, files)
        final = state.read(run)
        if backend.inputs(run, root, final) != captured or current["host_execution"][
            "context"
        ] != host_evidence.context(root, final):
            raise RunError(f"{module}: qualified inputs changed before final publication")
        receipt = runlog.Receipt(run, argv, owner)
        staged = _candidate(owner, module, receipt, candidate)
        append_log(receipt, 0)
        phase = "accepted state publication"
        _commit_accepted(owner, receipt, staged, candidate, execution)
        result = 0  # no fallible outcome-changing work follows this commit
    except ERRORS as exc:
        receipt = _failure_intent(owner, execution, argv, receipt, exc)
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


def _current_before_host(owner: state._Locked, root: Path, module: str) -> None:
    from rbotlib.current import _reconcile_owned

    selected = state.read(owner.run)["steps"].get(module, {})
    evidence = selected.get("host_execution", {})
    invocations = evidence.get("invocations", []) if isinstance(evidence, dict) else []
    persisted = any(isinstance(i, dict) and "failure" in i for i in invocations)
    if selected.get("status") in ("pending", "running") and not persisted:
        _reconcile_owned(owner, root)


def execute(
    args: argparse.Namespace, argv: list[str], append_log: Appender, backend: Backend[C, W]
) -> int:
    """Keep each executing invocation attributable; ownership refusals never borrow a row."""
    selected = Path(args.run_dir)
    token = uuid4().hex
    owner = None
    try:
        run, root = state.run_path(selected), dispatch._root(args.root)
        owner = state._Locked(run)
        _current_before_host(owner, root, backend.step)
        generated_at = datetime.now(UTC).isoformat()
        captured = _register(owner, root, generated_at, token, backend)
        evidence = state.read(run)["steps"][backend.step]["host_execution"]
        token, generated_at = evidence["token"], evidence["generated_at"]
        execution = Execution(run, root, token, captured, generated_at, backend)
        previous = evidence["invocations"][:-1]
        failure = next((i["failure"] for i in previous if "failure" in i), None)
        try:
            built: tuple[W, dict[str, bytes]] | Exception
            if failure:
                built = RunError(f"persisted terminal failure: {failure}")
            elif captured is None:
                raise RunError("host: captured execution inputs missing")
            else:
                built = backend.build(captured, generated_at)
            if not isinstance(built, Exception):
                _reconcile(run, built[1])
        except ERRORS as exc:
            # Foreign existing output is a refusal, never an attributed build failure.
            if "conflicting output" in str(exc):
                raise
            built = exc
        return _complete(execution, built, argv, append_log, owner)
    except ERRORS as exc:
        _diagnostic(f"{exc}; token={token}; uncommitted outcome; recovery may be required")
        if owner is None:
            return 1  # refusal never acquires unrelated publication/log ownership
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
