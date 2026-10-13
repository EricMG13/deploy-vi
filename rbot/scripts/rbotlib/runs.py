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

from rbotlib import __version__, ownership, state
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
            if "ownership" not in state.read(unfinished):
                raise RunError(
                    f"unfinished legacy run exists: {unfinished}; "
                    "checked ownership missing; preserve read-only run"
                )
            raise RunError(f"unfinished run exists: {unfinished}; use next --run {unfinished}")
        slug = re.sub(r"[^a-z0-9]+", "-", (issuer or "").lower()).strip("-")[:80] or "unknown"
        run = _allocate(envelope, f"{datetime.now(UTC):%Y%m%d}-{slug}-pending")
        try:
            record = _bootstrap(run, pack, issuer, objective)
            owner = ownership.provision(run, state.LOCK, record)
            try:
                write_atomic(output_path(run, state.STATE), json.dumps(record, indent=2) + "\n")
            finally:
                owner.close()
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
