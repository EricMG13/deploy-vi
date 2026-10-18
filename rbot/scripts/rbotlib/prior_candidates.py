"""Read inventory-bound original Reports; no ownership, publication or Approval writes."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rbotlib.inventory import RUNS, SCHEMA, RunError, kind_of, output_path
from rbotlib.isolation_capture import Capture, admit
from rbotlib.prior_report import inspect_report, parse_report

Record = dict[str, Any]


@dataclass(frozen=True)
class PriorCandidate:
    """Detached original payload and exact provenance; issue means metadata is unusable."""

    source: str
    source_path: Path
    sha256: str
    kind: str
    offered: bool = False
    metadata: Record | None = None
    payload: Record | None = None
    tables: Record = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    issue: str | None = None


def _relative(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise RunError("Prior Report: expected canonical relative path")
    path = Path(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or path.as_posix() != value
        or any(ord(c) < 32 or ord(c) == 127 or c in "\\:" for c in value)
    ):
        raise RunError(f"Prior Report: unsafe relative path {value!r}")
    return value


def _pairs(pairs: list[tuple[str, Any]]) -> Record:
    result: Record = {}
    for key, value in pairs:
        if key in result:
            raise RunError(f"Prior Report inventory: duplicate JSON key {key}")
        result[key] = value
    return result


def _json(path: Path, capture: Capture) -> Record:
    try:
        data = json.loads(capture.read(path).decode("utf-8"), object_pairs_hook=_pairs)
    except (ValueError, RecursionError) as exc:
        raise RunError(f"Prior Report inventory {path}: invalid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise RunError(f"Prior Report inventory {path}: expected object")
    return data


def _registration(entry: object) -> Record:
    if not isinstance(entry, dict):
        raise RunError("Prior Report inventory: expected file object")
    name = _relative(entry.get("path"))
    digest = entry.get("sha256")
    if (
        not isinstance(digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        or entry.get("kind") != kind_of(Path(name))
        or type(entry.get("size")) is not int
        or entry["size"] < 0
        or type(entry.get("rbot_report")) is not bool
    ):
        raise RunError(f"Prior Report inventory: invalid file registration {name}")
    if entry["rbot_report"] and entry["kind"] not in ("html", "md"):
        raise RunError(f"Prior Report inventory: unsupported Report kind {name}")
    return entry


def _inventory(run: Path, pack: Path, capture: Capture) -> list[Record]:
    admit(run, directory=True)
    admit(pack, directory=True)
    state = output_path(run, "run-state.json")
    if state.exists():
        if _json(state, capture).get("pack_root") != str(pack):
            raise RunError("Prior Report: run-state pack_root differs from Source Pack")
    elif run.parent.name != RUNS or run.parent.parent != pack:
        raise RunError("Prior Report: run has no bound pack_root")
    data = _json(output_path(run, "inventory.json"), capture)
    if data.get("schema") != SCHEMA or data.get("pack_root") != str(pack):
        raise RunError("Prior Report inventory: wrong schema or pack_root")
    if not isinstance(data.get("files"), list):
        raise RunError("Prior Report inventory: expected files list")
    entries = [_registration(entry) for entry in data["files"]]
    names = [entry["path"] for entry in entries]
    if len(names) != len(set(names)):
        raise RunError("Prior Report inventory: duplicate source path")
    return entries


def _candidate(
    pack: Path, entry: Record, identity: tuple[str, str], now: datetime, capture: Capture
) -> PriorCandidate:
    name, digest, kind = entry["path"], entry["sha256"], entry["kind"]
    path = output_path(pack, name)
    raw = capture.read(path)
    if hashlib.sha256(raw).hexdigest() != digest or len(raw) != entry["size"]:
        raise RunError(f"Prior Report {name}: original source sha256/size changed")
    try:
        payload = parse_report(raw.decode("utf-8"), kind)
        meta, tables, limitations = inspect_report(payload)
    except (RunError, UnicodeDecodeError) as exc:
        return PriorCandidate(name, path, digest, kind, issue=f"Prior Report {name}: {exc}")
    if meta["run_id"] == identity[1]:
        raise RunError(f"Prior Report {name}: current run cannot be its own prior")
    if datetime.fromisoformat(payload["generated_at"]) > now:
        raise RunError(f"Prior Report {name}: future generated_at")
    return PriorCandidate(
        name,
        path,
        digest,
        kind,
        meta["issuer_id"] == identity[0],
        meta,
        payload,
        tables,
        tuple(limitations),
    )


def _qualified(
    run: Path, pack: Path, identity: tuple[str, str], source: str | None, now: datetime | None
) -> tuple[PriorCandidate, ...]:
    instant = datetime.now(UTC) if now is None else now
    if instant.utcoffset() is None:
        raise RunError("Prior Report: qualification time requires timezone")
    try:
        capture = Capture()
        entries = _inventory(run, pack, capture)
        reports = {entry["path"]: entry for entry in entries if entry["rbot_report"]}
        if source is not None:
            name = _relative(source)
            if name not in reports:
                raise RunError(f"Prior Report {name}: no registered Report source")
            reports = {name: reports[name]}
        candidates = tuple(
            _candidate(pack, reports[n], identity, instant, capture) for n in sorted(reports)
        )
        capture.verify()
    except OSError as exc:
        raise RunError(f"Prior Report source qualification: {exc}") from exc
    return candidates


def qualify_candidates(
    run: Path, pack: Path, issuer_id: str, current_run_id: str, *, now: datetime | None = None
) -> tuple[PriorCandidate, ...]:
    """Qualify every flagged original source; protected-source failures always refuse."""
    return _qualified(run, pack, (issuer_id, current_run_id), None, now)


def qualify_candidate(
    run: Path, pack: Path, source: str, identity: tuple[str, str], *, now: datetime | None = None
) -> PriorCandidate:
    """Qualify one registered path; identity is (current issuer_id, current run_id)."""
    return _qualified(run, pack, identity, source, now)[0]


def _unique_runs(candidates: Iterable[PriorCandidate]) -> dict[str, PriorCandidate]:
    runs: dict[str, PriorCandidate] = {}
    for candidate in sorted(candidates, key=lambda c: (c.kind != "html", c.source)):
        if not candidate.offered or candidate.metadata is None or candidate.payload is None:
            continue
        run_id = candidate.metadata["run_id"]
        if run_id in runs:
            previous = runs[run_id]
            if json.dumps(candidate.payload, sort_keys=True) != json.dumps(
                previous.payload, sort_keys=True
            ):
                raise RunError(f"Prior Report: conflicting payloads for run {run_id}")
        else:
            runs[run_id] = candidate
    return runs


def select_newest(candidates: Iterable[PriorCandidate], *, accepted: bool) -> PriorCandidate | None:
    """Decline selects nothing; acceptance refuses every same-run conflict/newest tie."""
    if not accepted:
        return None
    runs = _unique_runs(candidates)
    if not runs:
        return None
    newest = max(c.metadata["report_date"] for c in runs.values() if c.metadata is not None)
    latest = [
        c for c in runs.values() if c.metadata is not None and c.metadata["report_date"] == newest
    ]
    if len(latest) != 1:
        raise RunError(f"Prior Report: tied newest report date {newest}")
    return latest[0]
