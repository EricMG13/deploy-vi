# Task06.7 exact replay file 05

Source: `rbot/scripts/rbotlib/model/qualification.py`; complete executed bytes, SHA256 `266a2565121a391fbd7a7845d1388f986854bb9d47f9097b3162d7288ff1453f`, 9245 bytes, 227 LF. Baseline1094a76; final source tree/proof is recorded separately. This ordinary whole file receives no cap exemption.

```python
"""Managed MODEL execution owns attempts and validates the entire published trio.

Registration and completion use separate checked cooperating-writer transactions.
A running token refuses re-execution; interrupted completion requires recovery.
Standalone Model computation remains available when no state entry exists.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from rbotlib import attempts, dispatch, state
from rbotlib import next as next_step
from rbotlib.handoff import parse
from rbotlib.inventory import RunError
from rbotlib.model import run as writer
from rbotlib.model.house_inputs import assessments, debt_like_items, effective_registers
from rbotlib.model.inputs import cp1_registers
from rbotlib.rules import load_rules

OUTPUTS = ("model.json", "model.xlsx", "handoffs/MODEL.md")


@dataclass(frozen=True, slots=True)
class Inputs:
    cp1: writer.Read
    brief: writer.Read
    cp1d: writer.Read | None
    missing: str

    def hashes(self) -> dict[str, str | None]:
        return {
            "CP-1": self.cp1.sha256,
            "RUN_BRIEF": self.brief.sha256,
            "CP-1D": self.cp1d.sha256 if self.cp1d else None,
            "CP-2G": None,
        }


def managed(run: Path) -> bool:
    """An existing state entry, including a broken link, must prove ownership."""
    try:
        (run / state.STATE).lstat()
    except FileNotFoundError:
        return False
    state.read(run)
    return True


def inputs(run: Path, root: Path, record: state.Record) -> Inputs:
    rules = load_rules(dispatch._file(root, "rules.json").parent)
    next_step._dependencies(root, record, rules)
    dispatch._target(run, "log/rbot.log")
    for name in OUTPUTS:
        dispatch._target(run, name)
    dispatch._prepared(run, record)
    if record["approval"] is None:
        raise RunError("MODEL requires analyst Approval")
    dispatch._context(run, root, record, rules)
    required = record["steps"].get("CP-1", {})
    if required.get("status") not in ("accepted", "blocked"):
        raise RunError(f"required input CP-1: {required.get('status', 'missing')}")
    attempts.read_history(run, "CP-1", required)
    dispatch._qualified_module(run, root, "CP-1", record, rules)
    cp1 = _capture(run, "handoffs/CP-1.md", required["sha256"])
    if cp1.handoff.front_matter.get("analysis_date") != record["as_of_date"]:
        raise RunError("CP-1: analysis_date differs from approved state")
    brief = _capture(run, "run-brief.md", record["run_brief_sha256"])
    cp1d, missing = _optional(run, root, record, cp1)
    return Inputs(cp1, brief, cp1d, missing)


def _capture(run: Path, name: str, digest: str) -> writer.Read:
    captured = writer.captured_handoff(dispatch._file(run, name).read_bytes(), name)
    if captured.sha256 != digest:
        raise RunError(f"{name}: captured bytes differ from registered qualified digest")
    return captured


def _optional(
    run: Path, root: Path, record: state.Record, cp1: writer.Read
) -> tuple[writer.Read | None, str]:
    rules = load_rules(root)
    cp1d, missing = None, "CP-1D: missing; excluded; CP-1 realization statuses retained"
    optional = record["steps"].get("CP-1D", {})
    status = optional.get("status", "missing")
    if status in ("accepted", "blocked"):
        regs = cp1_registers(cp1.handoff.tables)
        try:
            attempts.read_history(run, "CP-1D", optional)
            dispatch._qualified_module(run, root, "CP-1D", record, rules)
            cp1d = _capture(run, "handoffs/CP-1D.md", optional["sha256"])
            if cp1d.handoff.front_matter.get("analysis_date") != record["as_of_date"]:
                raise RunError("analysis_date differs from approved state")
            assessments(cp1d.handoff.tables)
            debt_like_items(cp1d.handoff.tables, regs)
            missing = ""
        except (OSError, ValueError, KeyError, TypeError) as exc:
            cp1d = None
            missing = f"CP-1D: unqualified ({exc}); excluded; CP-1 statuses retained"
    else:
        missing = f"CP-1D: {status}; excluded; CP-1 realization statuses retained"
    if cp1d is None:
        return None, missing
    # Financial contradictions remain outside the optional-exclusion catch.
    effective_registers(regs, assessments(cp1d.handoff.tables))
    return cp1d, missing


def _hashes(files: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()}


def _workbook(raw: bytes) -> list[tuple[str, list[list[tuple[Any, str, str]]]]]:
    """Read real cells, retaining type/format and refusing active spreadsheet content."""
    try:
        with ZipFile(BytesIO(raw)) as archive:
            if any(
                "externallinks/" in name.lower() or "vbaproject" in name.lower()
                for name in archive.namelist()
            ):
                raise RunError("MODEL workbook: macros/external links are forbidden")
        book = load_workbook(BytesIO(raw), keep_links=True)
    except (BadZipFile, SyntaxError, InvalidFileException) as exc:
        raise RunError(f"MODEL workbook: malformed ({exc})") from exc
    try:
        return _cells(book)
    finally:
        book.close()


def _cells(book: Workbook) -> list[tuple[str, list[list[tuple[Any, str, str]]]]]:
    result = []
    for sheet in book.worksheets:
        rows = []
        for row in sheet.iter_rows():
            if any(cell.data_type == "f" or cell.hyperlink is not None for cell in row):
                raise RunError("MODEL workbook: formula/hyperlink is forbidden")
            rows.append([(cell.value, cell.data_type, cell.number_format) for cell in row])
        result.append((sheet.title, rows))
    return result


def validate(
    files: dict[str, bytes], captured: Inputs, record: state.Record, generated_at: str
) -> writer.Written:
    """Independent completion readback recomputes source origin and trio consistency."""
    import json

    if set(files) != set(OUTPUTS):
        raise RunError("MODEL completion requires all three outputs")
    data = json.loads(files["model.json"], object_pairs_hook=state._pairs)
    if not isinstance(data, dict):
        raise RunError("MODEL JSON: expected an object")
    handoff = parse(files["handoffs/MODEL.md"].decode("utf-8"))
    front = handoff.front_matter
    expected = {
        "module_id": "MODEL",
        "run_id": record["run_id"],
        "issuer_id": record["issuer_id"],
        "analysis_date": record["as_of_date"],
    }
    if (
        data.get("schema") != "rbot-model/1"
        or data.get("run_id") != record["run_id"]
        or data.get("generated_at") != generated_at
        or data.get("inputs") != captured.hashes()
        or any(front.get(k) != v for k, v in expected.items())
        or handoff.sections != ["Analysis", "Tables", "Gaps", "Citations"]
        or handoff.invalid_tags
        or handoff.orphan_tags
        or handoff.duplicate_tags
    ):
        raise RunError("MODEL completion: identity/input fingerprints/Handoff structure differ")
    written, rebuilt = writer.build(
        captured.cp1,
        captured.brief,
        captured.cp1d,
        generated_at,
        writer.Options(captured.missing, True),
    )
    if (
        front.get("qa_status") != written.qa_status
        or files["model.json"] != rebuilt["model.json"]
        or files["handoffs/MODEL.md"] != rebuilt["handoffs/MODEL.md"]
        or _workbook(files["model.xlsx"]) != _workbook(rebuilt["model.xlsx"])
    ):
        raise RunError("MODEL completion: JSON/Handoff/workbook differs from current host origin")
    return written


def qualify(run: Path, root: Path, record: state.Record) -> None:
    current = record["steps"].get("MODEL", {})
    evidence = current.get("host_execution", {})
    if (
        not isinstance(evidence, dict)
        or current.get("status") != "accepted"
        or current.get("host_exit") != 0
        or current.get("attempts") != 1
        or evidence.get("origin") != "host-model/1"
        or not isinstance(evidence.get("token"), str)
        or not evidence.get("token")
        or not state._stamp(current.get("started_at"))
        or not state._stamp(current.get("finished_at"))
        or not state._stamp(evidence.get("generated_at"))
    ):
        raise RunError("MODEL: accepted checked host execution required")
    captured = inputs(run, root, record)
    if evidence.get("inputs") != captured.hashes():
        raise RunError("MODEL: current inputs differ from its execution")
    files = {name: dispatch._file(run, name).read_bytes() for name in OUTPUTS}
    written = validate(files, captured, record, evidence["generated_at"])
    if (
        _hashes(files) != current.get("outputs")
        or current.get("sha256") != _hashes(files)["handoffs/MODEL.md"]
        or current.get("qa_status") != written.qa_status
        or current.get("handoff") != "handoffs/MODEL.md"
    ):
        raise RunError("MODEL: current outputs/hash/QA differ from accepted execution")
```

Not verified: independent acceptance, whole06.16 branch gates, later06, live/provider/platform/crash behavior.
