# Plan06.2 executed replay bytes

Exact original task predecessor `013a274d22f8e74f41a0f5351418109a0f237805`, tree `2b42ed0148703c3d0c8e84800363e4fa4f35fcc7`. Historical original runtime commit `ea81e8dd6ee007d9368fa81dc021fae6fffaa36e`, tree `3346d8746096cdb9b9ee2c53d9768380536d99ec`, and rejected task head `e237107cf36b667f468f189386bab19b1eb6ba74` remain preserved in Git and original main reports. Repaired executed runtime commit `ab064c4d790a7581d43ca0e7b2e8cb680b763033`, tree `9d1d8d7a045e1016d2968b8db1e4fcc848862b81`. Each block below now equals repaired executed source; they do not establish independent repair approval. uv.lock blob `35bf2e7e741576c67c5e2908add759111dd8fabf`, SHA256 `cea4c0f2021ff0048c47e643c828baee104062e64400fb314493ece76fe6cf30`. Restore only against the stated original task predecessor, preserve sources/WIP, compare every source block/lock and use separate actual capped scopes. Final docs identity is recorded in main task-02-fix-report.md. No push/merge or03 continuation implied.

## `rbot/scripts/rbotlib/runs.py`

```python
"""Create checked CP-0 runs and discover unfinished state without changing it.

An omitted/empty non-sluggable issuer uses folder-only ``unknown``; hints never
establish identity. Discovery includes exactly 30 days, refuses future dates,
and breaks equal creation timestamps by run name. Markerless directories are
reserved collisions, not resumable runs. Vanished entries or changed directory
listings refuse discovery; retry to obtain the effective renamed run. Creation
holds a pack-level exclusive lock through discovery and publication, waits at
most 5 seconds, and never forces a stale lock away. Like state.py, static path
guards do not guarantee safety against hostile directory replacement or abrupt-crash consistency.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from rbotlib import __version__, state
from rbotlib.fsio import write_atomic
from rbotlib.inventory import RUNS, RunError, output_path

LOCK = ".new-run.lock"
LOCK_WAIT = 5.0


def _pack_path(pack: Path) -> Path:
    selected = pack.absolute()
    try:
        pack = selected.resolve(strict=True)
    except RuntimeError as exc:
        raise RunError(f"cannot resolve pack: {selected} ({exc})") from exc
    if not pack.is_dir():
        raise RunError(f"pack must be a directory: {pack}")
    for path in (selected, *selected.parents):
        if path.is_symlink() and path.resolve().is_relative_to(pack):
            raise RunError(f"pack path is a symlink: {path}")
    return pack


def _envelope(pack: Path) -> Path:
    path = output_path(pack, RUNS)
    if path.exists() and not path.is_dir():
        raise RunError(f"runs envelope must be a directory: {path}")
    return path


def _clock(now: datetime | None) -> datetime:
    now = datetime.now(UTC) if now is None else now
    if now.utcoffset() is None:
        raise RunError("run discovery requires a timezone-aware clock")
    return now


def _candidate_directory(candidate: Path) -> bool:
    try:
        return stat.S_ISDIR(candidate.stat().st_mode)
    except FileNotFoundError as exc:
        raise RunError(f"discovery changed: {candidate} disappeared; retry discovery") from exc


def _candidate_entry(candidate: Path, now: datetime) -> tuple[datetime, str, Path] | None:
    marker = output_path(candidate, state.STATE)
    if not marker.exists():
        _candidate_directory(candidate)  # original markerless reservation or vanished run?
        return None
    try:
        record = state.read(candidate)
    except (OSError, ValueError, RecursionError) as exc:
        raise RunError(f"{marker}: {exc}") from exc
    created = datetime.fromisoformat(record["created_at"])
    if created > now:
        raise RunError(f"{marker}: created_at is in the future")
    if record["report"]["written_at"] is not None or now - created > timedelta(days=30):
        return None
    return created, candidate.name, candidate


def discover_unfinished(pack: Path, *, now: datetime | None = None) -> Path | None:
    """Newest checked unfinished <=30-day run; hints/status/name do not filter identity."""
    pack, now = _pack_path(pack), _clock(now)
    envelope = _envelope(pack)
    newest: tuple[datetime, str, Path] | None = None
    if not envelope.exists():
        return None
    candidates = sorted(envelope.iterdir())
    for candidate in candidates:
        candidate = output_path(envelope, candidate.name)
        if _candidate_directory(candidate):
            entry = _candidate_entry(candidate, now)
            if entry is not None and (newest is None or entry > newest):
                newest = entry
    if sorted(envelope.iterdir()) != candidates:
        raise RunError(f"discovery changed: entries in {envelope} changed; retry discovery")
    return newest[2] if newest else None


@contextmanager
def _creation_lock(envelope: Path) -> Iterator[None]:
    deadline = time.monotonic() + LOCK_WAIT
    while True:
        lock = output_path(envelope, LOCK)
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
            break
        except FileExistsError as exc:
            if time.monotonic() >= deadline:
                raise RunError(
                    f"{lock}: creation lock is busy or stale; inspect before retrying"
                ) from exc
            time.sleep(0.02)
    try:
        yield
    finally:
        output_path(envelope, LOCK).unlink()


def _allocate(envelope: Path, name: str) -> Path:
    suffix = 1
    while True:
        run = output_path(envelope, name if suffix == 1 else f"{name}-{suffix}")
        try:
            run.mkdir()
        except FileExistsError:
            suffix += 1
        else:
            return run


def _bootstrap(run: Path, pack: Path, issuer: str | None, objective: str | None) -> state.Record:
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    record: state.Record = {
        "schema": "rbot-run-state/1",
        "rbot_version": __version__,
        "run_id": run.name,
        "pack_root": str(pack),
        "created_at": stamp,
        "updated_at": stamp,
        "run_brief": "run-brief.md",
        "run_brief_sha256": None,
        "issuer_id": None,
        "as_of_date": None,
        "pathway": None,
        "depth": None,
        "primary": None,
        "deep_research": None,
        "prior_case": None,
        "approval": None,
        "plan": ["CP-0"],
        "steps": {"CP-0": {"kind": "module", "status": "pending", "attempts": 0}},
        "report": {"written_at": None, "html_sha256": None, "md_sha256": None},
        "hints": {"issuer": issuer, "objective": objective},
    }
    state.validate(record, run)
    return record


def create_run(pack: Path, issuer: str | None = None, objective: str | None = None) -> Path:
    """Allocate/publish one checked run; refuse a resumable run while holding ownership."""
    pack = _pack_path(pack)
    envelope = _envelope(pack)
    envelope.mkdir(exist_ok=True)
    with _creation_lock(envelope):
        unfinished = discover_unfinished(pack)
        if unfinished is not None:
            raise RunError(f"unfinished run exists: {unfinished}; use next --run {unfinished}")
        slug = re.sub(r"[^a-z0-9]+", "-", (issuer or "").lower()).strip("-")[:80] or "unknown"
        run = _allocate(envelope, f"{datetime.now(UTC):%Y%m%d}-{slug}-pending")
        try:
            record = _bootstrap(run, pack, issuer, objective)
            write_atomic(output_path(run, state.STATE), json.dumps(record, indent=2) + "\n")
            state.read(run)
        except (OSError, ValueError, RecursionError) as exc:
            try:
                run.rmdir()  # remove only our empty allocation; never remove user content
            except OSError:
                raise RunError(f"{run}: incomplete run retained ({exc})") from exc
            raise
        return run


def new_run_command(args: argparse.Namespace) -> int:
    try:
        run = create_run(Path(args.pack), args.issuer, args.objective)
    except (OSError, ValueError, RecursionError) as exc:
        print(f"error: {exc}")
        return 1
    args.created_run_dir = str(run)  # grants only post-creation, checked logging ownership
    print(run)
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser("new-run", help="create a checked CP-0 run inside a Source Pack")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--issuer")
    parser.add_argument("--objective")
    parser.set_defaults(run=new_run_command)
```

## `rbot/scripts/rbotlib/cli.py`

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

from rbotlib import approve, brief, calc, corpus, fit, grade, inventory, prepare, runs, state
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

Not verified: independent task06.2 approval, whole Plan06 integration gates/coverage/corpus closure,06.3–16 behavior, live Copilot/model qualification.
