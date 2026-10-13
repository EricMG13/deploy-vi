"""Checked run state. Acceptance/dispatch owners use update; public edits only fail/skip.

The shared Approval lock prevents cooperating writers from losing fields or racing
Approval's rename. Destination guards are rechecked after staging; hostile directory
replacement and abrupt-crash consistency are not guaranteed by this path-based API.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from rbotlib import ownership
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
        "validated_at": _stamp,
        "reason": lambda v: isinstance(v, str),
        "model": _text,
    }
    _fields(record, {k: checks[k] for k in checks if k in record}, label)
    if record["status"] in ("failed", "skipped"):
        _fields(record, {"reason": _text}, label)
    from rbotlib.current import checked

    checked(record, step)
    _completed(record, checks, label)


def _completed(record: Record, checks: dict[str, Check], label: str) -> None:
    from rbotlib.current import result

    record = record | ({"validate_exit": result(record)["exit"]} if result(record) else {})
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
    _lineage(record)
    _ownership(record)
    from rbotlib.origins import validate as validate_origins

    validate_origins(record)


def _ownership(record: Record) -> None:
    if "ownership" not in record:
        return
    protocol = _fields(
        record["ownership"],
        {
            "schema": lambda v: v == "rbot-process-owner/1",
            "state": lambda v: isinstance(v, dict),
            "log": lambda v: isinstance(v, dict),
        },
        "state ownership",
    )
    for name in ("state", "log"):
        _fields(
            protocol[name],
            {
                "bytes": lambda v: (
                    isinstance(v, str)
                    and re.fullmatch(r"rbot-owner/1 [0-9a-f]{32}\n", v) is not None
                ),
                "device": lambda v: type(v) is int and v >= 0,
                "inode": lambda v: type(v) is int and v >= 0,
            },
            f"state ownership.{name}",
        )


def _lineage(record: Record) -> None:
    if "cp0_lineage" not in record:
        return
    lineage = _fields(
        record["cp0_lineage"],
        {
            "pending_run_id": lambda v: (
                isinstance(v, str) and re.fullmatch(r"\d{8}-.+-pending(?:-\d+)?", v) is not None
            ),
            "issuer_id": _text,
            "sha256": _sha,
        },
        f"{STATE}.cp0_lineage",
    )
    from rbotlib.current import original

    cp0 = original(record["steps"].get("CP-0", {}))
    approved = record.get("approved_origins", {})
    if not isinstance(approved, dict) or not isinstance(approved.get("CP-0", {}), dict):
        raise RunError("approved origin: malformed CP-0 binding")
    if (
        set(lineage) != {"pending_run_id", "issuer_id", "sha256"}
        or record["approval"] is None
        or lineage["pending_run_id"] == record["run_id"]
        or cp0.get("status") not in ("accepted", "blocked")
        or lineage["sha256"] != (approved.get("CP-0", {}).get("sha256", cp0.get("sha256")))
    ):
        raise RunError(f"{STATE}.cp0_lineage: requires approved, hash-bound pending CP-0")


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
    try:
        text = _destination(run).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RunError(f"{run / STATE}: no readable run state ({exc})") from exc
    record: Record = json.loads(text, object_pairs_hook=_pairs)
    validate(record, run)
    json.dumps(record, allow_nan=False)  # also rejects non-finite extension metadata
    return record


def write_guard(run: Path) -> Record | None:
    """Read-only classification: no-state standalone or checked prospective ownership."""
    try:
        _physical(run)
    except FileNotFoundError as exc:
        raise RunError(f"{run}: no such run folder ({exc})") from exc
    marker = output_path(run, STATE)
    if not marker.exists():
        if output_path(run, LOCK).exists():
            raise RunError(
                "run-state.json: state must be an existing regular file; "
                "legacy/initialization ownership unresolved; run preserved"
            )
        return None
    record = read(run)
    protocol = record.get("ownership")
    if protocol is None:
        raise RunError(
            "legacy run: checked process ownership missing; read-only compatibility limitation"
        )
    for key, name in (("state", LOCK), ("log", ownership.LOG)):
        if ownership.existing(run, name) != protocol[key]:
            raise RunError(f"{name}: owned lock identity/protocol changed; publication refused")
    return record


@contextmanager
def publication(run: Path) -> Iterator[Callable[[], None]]:
    """Direct publishers retain the same state owner as host/state writers."""
    owner = _Locked(run) if write_guard(run) is not None else None
    try:
        yield owner.owner.check if owner is not None else lambda: None
        if owner is not None:
            owner.owner.check()
    finally:
        if owner is not None:
            warnings = owner.close()
            if warnings:
                raise RunError("; ".join(warnings))


def update(
    run: Path, change: Callable[[Record], None], publish: Callable[[], None] | None = None
) -> Record:
    """Change is pure; optional guarded evidence publication precedes state under the lock.

    Evidence owners must detect a published orphan if state publication is interrupted.
    This is not a multi-file crash transaction; no evidence is deleted on failure.
    """
    owner = _Locked(run)
    try:
        record = read(owner.run)
        before = copy.deepcopy(record)
        change(record)
        staged = owner.stage(record) if record != before else None
        if publish is not None:
            owner.owner.check()
            publish()
        if staged is not None:
            owner.commit(staged)
        return record
    finally:
        warnings = owner.close()
        if warnings:
            raise RunError("; ".join(warnings))


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


class _Locked:
    """Private host completion boundary; caller keeps state ownership through failures.

    Staging is separate from evidence publication and replacement. Cleanup is
    reported independently so a committed host outcome cannot be downgraded.
    """

    def __init__(self, run: Path) -> None:
        self.run = run_path(run)
        record = write_guard(self.run)
        if record is None:
            raise RunError("run-state.json: state ownership requires a published new run")
        self.owner = ownership.Owner(self.run, LOCK, record["ownership"]["state"])
        self.lock = output_path(self.run, LOCK)
        self.identity = os.fstat(self.owner.fd)
        self.stages: list[Path] = []

    def stage(self, record: Record) -> Path:
        self.owner.check()
        record["updated_at"] = datetime.now(UTC).isoformat(timespec="seconds")
        validate(record, self.run)
        fd, name = tempfile.mkstemp(dir=self.run, prefix=".state-")
        os.close(fd)
        staged = Path(name)
        self.stages.append(staged)
        write_atomic(
            staged, json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        )
        _destination(self.run)
        return staged

    def commit(self, staged: Path) -> None:
        self.owner.check()
        os.replace(staged, _destination(self.run))

    def close(self) -> list[str]:
        warnings = []
        for staged in self.stages:
            try:
                staged.unlink(missing_ok=True)
            except OSError as exc:
                warnings.append(f"state stage cleanup: {exc}")
        try:
            self.owner.close()
        except (OSError, ValueError) as exc:
            warnings.append(f"state lock cleanup: {exc}")
        return warnings
