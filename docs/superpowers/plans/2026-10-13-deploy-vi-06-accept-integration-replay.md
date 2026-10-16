# Plan06.5 executed accept-integration source/test replay

Approved predecessor: `6fa314d6b8edb786aa1dbeba65f5a350a811930f`, tree `6733ba323f00b8b69621ddf965a483842e2a0e45`. This document records locally executed05 awaiting fresh ordinary/sensitive reviews. Exact binary/full-index per-boundary patches/tree/lock/cap proof are in main staging task-05-proof.json. These complete AST-parsable blocks match current source bytes; the patches replay integration without inferred manual edits.

Consume the existing checked state/Approval lock and Task04 pure qualification, actual selected-root contracts/rules/catalog/source context, and reported dispatch events. Preparation never sends. Receipts are trusted caller reports, not signed/network proof. attempts counts validation slots1/2; distinct reported interruption resends remain individually attributable within a slot. Latest validation retains the prescribed four fields; immutable relative history keeps exact messages and raw-byte Handoff snapshots plus code/QA/receipt links. Strict base64 length/canonical decode/hash checks are local encoding checks, not authenticity. Missing bytes have null hash; unknown worker/model evidence stays unknown. Approved CP0 uses only registered pending lineage. Orphan/latest mismatch refuses for owner09. Python3.11 primary base64 docs were read after selection before commit;3.11/Windows remain unexercised.

## `rbot/scripts/rbotlib/state.py`

<!-- replay-path: rbot/scripts/rbotlib/state.py -->
```python
"""Checked run state. Acceptance/dispatch owners use update; public edits only fail/skip.

The shared Approval lock prevents cooperating writers from losing fields or racing
Approval's rename. Destination guards are rechecked after staging; hostile directory
replacement and abrupt-crash consistency are not guaranteed by this path-based API.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

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
    _completed(record, checks, label)


def _completed(record: Record, checks: dict[str, Check], label: str) -> None:
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
    cp0 = record["steps"].get("CP-0", {})
    if (
        set(lineage) != {"pending_run_id", "issuer_id", "sha256"}
        or record["approval"] is None
        or lineage["pending_run_id"] == record["run_id"]
        or cp0.get("status") not in ("accepted", "blocked")
        or lineage["sha256"] != cp0.get("sha256")
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
    record: Record = json.loads(
        _destination(run).read_text(encoding="utf-8"), object_pairs_hook=_pairs
    )
    validate(record, run)
    json.dumps(record, allow_nan=False)  # also rejects non-finite extension metadata
    return record


def update(
    run: Path, change: Callable[[Record], None], publish: Callable[[], None] | None = None
) -> Record:
    """Change is pure; optional guarded evidence publication precedes state under the lock.

    Evidence owners must detect a published orphan if state publication is interrupted.
    This is not a multi-file crash transaction; no evidence is deleted on failure.
    """
    run = run_path(run)
    lock = output_path(run, LOCK)
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    except FileExistsError as exc:
        raise RunError(f"another state update or Approval holds this run ({LOCK})") from exc
    stage: Path | None = None
    try:
        record = read(run)
        change(record)
        record["updated_at"] = datetime.now(UTC).isoformat(timespec="seconds")
        validate(record, run)
        fd, name = tempfile.mkstemp(dir=run, prefix=".state-")
        os.close(fd)
        stage = Path(name)
        write_atomic(
            stage, json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        )
        _destination(run)  # preflight before related evidence publication
        if publish is not None:
            publish()
        os.replace(stage, _destination(run))
        return record
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


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
```

## `rbot/scripts/rbotlib/bootstrap.py`

<!-- replay-path: rbot/scripts/rbotlib/bootstrap.py -->
```python
"""Checked CP-0 completion shared by Approval and later dispatch/accept owners.

Validation is an observed controller event, not evidence that a worker was sent.
No missing worker timestamps, model labels or physical attempts are synthesized.
Accepted bytes cannot be replaced here: edited acceptance belongs to the later
revalidation owner. Approval's hash-bound pending lineage permits only that
original CP-0 identity after rename; it never changes the accepted Handoff.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from rbotlib import brief as rb
from rbotlib import state
from rbotlib.contract import load_contract
from rbotlib.handoff import parse
from rbotlib.inventory import RunError, output_path
from rbotlib.rules import Rules
from rbotlib.validate import EXIT_BLOCKED, EXIT_VALID, check

CP0 = "handoffs/CP-0.md"


@dataclass(frozen=True)
class QualifiedCP0:
    """Identity and step from the same independently validated byte snapshot."""

    step: state.Record
    run_id: str
    issuer_id: str


def _identity(run: Path, text: str, rules: Rules, record: state.Record) -> tuple[str, str]:
    """Front identity must agree with validated readiness; gaps remain explicit."""
    front = parse(text).front_matter
    readiness = rb.from_cp0(run, text, rules).fields["issuer_id"].value
    known = not rules.is_placeholder(readiness)
    if (known and front["issuer_id"] != readiness) or (
        not known and not rules.is_placeholder(front["issuer_id"])
    ):
        raise RunError(f"{CP0}: identity differs from CP-0 issuer readiness")
    if known and record["issuer_id"] is not None and record["issuer_id"] != readiness:
        raise RunError(f"{CP0}: identity differs from the confirmed issuer")
    lineage = record.get("cp0_lineage")
    expected = lineage["pending_run_id"] if lineage else record["run_id"]
    if front["run_id"] != expected or (lineage and front["issuer_id"] != lineage["issuer_id"]):
        raise RunError(f"{CP0}: identity does not match the qualified run/issuer")
    return front["run_id"], front["issuer_id"]


def _accept_evidence(run: Path, record: state.Record) -> None:
    from rbotlib import attempts

    current = record["steps"].get("CP-0", {})
    if "accept_history" in current:
        events = attempts.read_history(run, "CP-0", current)
        if (
            not events
            or events[-1]["event"] != "validation"
            or current["status"] not in ("accepted", "blocked")
        ):
            raise RunError("CP-0 has reported dispatch evidence; run accept before Approval")


def checked_cp0(run: Path, root: Path, rules: Rules, record: state.Record) -> QualifiedCP0:
    """Qualify actual bytes and return CP-0 metadata; no publication or lock acquisition.

    The caller must hold the shared writer lock to publish this result. Read-only
    callers receive an observation, not a lease against later filesystem changes.
    """
    _accept_evidence(run, record)
    path = output_path(run, CP0)
    if not path.is_file():
        raise RunError(f"{path}: CP-0 Handoff must be an existing regular file")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunError(f"{path}: no readable CP-0 Handoff ({exc})") from exc
    contract = load_contract(root / "modules/CP-0/contract.json", rules)
    code, findings = check(text, contract, rules, run)
    if code not in (EXIT_VALID, EXIT_BLOCKED):
        detail = "; ".join(f.message for f in findings)
        raise RunError(f"{CP0} no longer validates (exit {code}); run rbot grade: {detail}")
    front = parse(text).front_matter
    identity = _identity(run, text, rules, record)
    sha = hashlib.sha256(raw).hexdigest()
    current = record["steps"].get("CP-0")
    if current is None or current["status"] not in ("pending", "running", "accepted", "blocked"):
        raise RunError(f"{CP0}: completion requires pending/running or qualified CP-0")
    if current["status"] in ("accepted", "blocked"):
        if (
            current["sha256"] != sha
            or current["validate_exit"] != code
            or current["qa_status"] != front["qa_status"]
        ):
            raise RunError(
                f"{CP0} changed after completion; use the CP-0 completion owner to revalidate"
            )
        return QualifiedCP0(dict(current), *identity)
    step = dict(current) | {
        "status": "accepted" if code == EXIT_VALID else "blocked",
        "qa_status": front["qa_status"],
        "handoff": CP0,
        "sha256": sha,
        "validate_exit": code,
        "validated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    return QualifiedCP0(step, *identity)


def complete_cp0(run: Path, root: Path, rules: Rules) -> state.Record:
    """Independently qualify CP-0 and publish through the existing state engine."""

    def change(record: state.Record) -> None:
        if record["approval"] is not None:
            raise RunError("CP-0 bootstrap is already approved; use the revalidation owner")
        record["steps"]["CP-0"] = checked_cp0(run, root, rules, record).step

    return state.update(run, change)


def phase(run: Path, root: Path, rules: Rules) -> str:
    """Return cp0/approval/analysis; pre-Approval waiting is never terminal done."""
    record = state.read(run)
    cp0 = record["steps"].get("CP-0", {})
    if cp0.get("status") not in ("accepted", "blocked"):
        if record["approval"] is not None:
            raise RunError("Approval has no qualified CP-0")
        return "cp0"
    checked_cp0(run, root, rules, record)
    return "approval" if record["approval"] is None else "analysis"
```

## `rbot/scripts/rbotlib/cli.py`

<!-- replay-path: rbot/scripts/rbotlib/cli.py -->
```python
"""`rbot` command line. Each later command lives with its module (`add_command`).

A command given `--run <RUN>` appends one line to `<RUN>/log/rbot.log`.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from rbotlib import (
    accept,
    approve,
    attempts,
    brief,
    calc,
    corpus,
    dispatch,
    fit,
    grade,
    inventory,
    prepare,
    runs,
    state,
)
from rbotlib.catalog import check_tree
from rbotlib.contract import ContractError, load_contract
from rbotlib.model.run import add_command as add_model_command
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import check


def _fail(path: Path, exc: Exception) -> int:
    reason = exc.strerror if isinstance(exc, FileNotFoundError) and exc.strerror else exc
    print(f"error: {path}: {reason}", file=sys.stderr)
    return 1


def _validate(args: argparse.Namespace) -> int:
    rules = load_rules(args.root)
    path = args.root / "modules" / args.module / "contract.json"
    try:
        contract = load_contract(path, rules)
    except (FileNotFoundError, ContractError) as exc:
        return _fail(path, exc)
    try:
        text = Path(args.handoff).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        return _fail(Path(args.handoff), exc)
    run = Path(args.run_dir) if args.run_dir else None
    code, findings = check(text, contract, rules, run)
    for f in findings:
        if f.code == "run_error":
            print(f"error: {f.message}", file=sys.stderr)
            return code
        print(f"{f.code}: {f.message}")
    print(f"exit {code}")
    return code


def _render(args: argparse.Namespace) -> int:
    rules = load_rules(args.root)
    folder = args.root / "modules" / args.module
    try:
        text = render_module(load_contract(folder / "contract.json", rules), rules)
    except (FileNotFoundError, ContractError) as exc:
        return _fail(folder / "contract.json", exc)
    if args.write:
        (folder / "MODULE.md").write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def _check(args: argparse.Namespace) -> int:
    problems = check_tree(args.root, load_rules(args.root))
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


def _log_path(run: Path) -> Path:
    """Refuse pre-existing unsupported log kinds without opening or creating anything."""
    destination = inventory.output_path(run, "log/rbot.log")
    if destination.parent.exists() and not destination.parent.is_dir():
        raise inventory.RunError(f"{destination.parent}: log parent must be a directory")
    if destination.exists() and not destination.is_file():
        raise inventory.RunError(f"{destination}: log must be a regular file")
    return destination


def _log(run: Path, argv: list[str], code: int) -> None:
    """One line per command in <RUN>/log/rbot.log: time, command, exit (spec section 8.1)."""
    destination = _log_path(run)
    destination.parent.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    command = json.dumps(" ".join(argv), ensure_ascii=True)[1:-1]
    with destination.open("a", encoding="utf-8") as log:
        log.write(f"{stamp}\t{command}\t{code}\n")


def _finish_log(
    args: argparse.Namespace, log_run: Path | None, argv: list[str] | None, result: int
) -> int:
    created = getattr(args, "created_run_dir", None)
    if created is not None:
        try:
            log_run = state.log_run_path(Path(created))
            args.run_dir = str(log_run)
        except (OSError, ValueError, RecursionError) as exc:
            result = _fail(Path(created), exc)
    if log_run is not None:
        log_run = Path(args.run_dir)
        try:
            _log(log_run, sys.argv[1:] if argv is None else argv, result)
        except (inventory.RunError, OSError) as exc:
            result = _fail(log_run, exc)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rbot")
    parser.add_argument("--root", type=Path, default=RBOT_ROOT, help="the RBOT folder")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="check a Handoff against its module contract")
    v.add_argument("handoff")
    v.add_argument("--module", required=True)
    v.add_argument("--run", dest="run_dir", help="also check citations against this run folder")
    v.set_defaults(run=_validate)
    r = sub.add_parser("render-module", help="print or write a module's MODULE.md")
    r.add_argument("module")
    r.add_argument("--write", action="store_true")
    r.set_defaults(run=_render)
    c = sub.add_parser("check", help="contracts, generated modules, Pathways, Front Pages, budget")
    c.set_defaults(run=_check)
    corpus.add_command(sub)
    inventory.add_command(sub)
    prepare.add_command(sub)
    brief.add_command(sub)
    add_model_command(sub)
    grade.add_command(sub)
    approve.add_commands(sub)
    calc.add_command(sub)
    fit.add_command(sub)
    state.add_command(sub)
    runs.add_command(sub)
    dispatch.add_command(sub)
    attempts.add_command(sub)
    accept.add_command(sub)
    args = parser.parse_args(argv)
    run_dir = getattr(args, "run_dir", None)
    log_run = None
    if run_dir:
        selected = Path(run_dir)
        try:
            guard = getattr(args, "log_run_guard", None)
            if guard is not None:
                selected = guard(selected)
            if selected.is_dir():
                _log_path(selected)
                log_run = selected
        except (OSError, ValueError, RecursionError) as exc:
            return _fail(selected, exc)
    result = 1  # what the log records when the command raises
    try:
        result = int(args.run(args))
    finally:
        result = _finish_log(args, log_run, argv, result)
    return result
```

Not verified: physical sends, live Module/A-B/Copilot/fetch/tool/context-budget qualification, Python3.11/Windows/PowerShell, later next/host/resume/runtime/proxy/scorecard/report owners, fresh05 reviews and complete06 closure. No push/merge/publication.
