"""Preserve every semantic/original field while separately proving native row metadata."""

from __future__ import annotations

import json
from pathlib import Path

from rbotlib import command_receipts, state


def outcome_bytes(run: Path) -> bytes:
    raw = (run / state.STATE).read_bytes()
    try:
        record = json.loads(raw)
    except ValueError:
        return raw  # corrupt-state refusal continues to require exact bytes
    if not isinstance(record, dict):
        return raw
    try:
        command_receipts.verify(run, record)
    except (OSError, ValueError):
        return raw  # unsafe/corrupt row evidence retains the strict byte no-write oracle
    record.pop(command_receipts.KEY, None)
    record.pop("updated_at", None)  # native state stages timestamp real receipt observations
    return json.dumps(record, sort_keys=True).encode()


def artifact_bytes(run: Path, name: str | Path) -> bytes:
    return outcome_bytes(run) if str(name) == state.STATE else (run / name).read_bytes()
