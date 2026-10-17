"""Run a host's own input qualification over a candidate Handoff at `validate --run`.

MODEL reads CP-1 (required) and CP-1D (optional); FIT reads CP-1 (required) and CP-1A
(optional). A Handoff that validates but then wedges its host step is accepted for
nothing, so the validator calls the very functions the host calls, with the candidate
in place of its own module and the run's currently accepted upstream Handoffs beside it.
CP-3, the other FIT input, is already checked in full by the validator itself.

A Blocked candidate is not checked: a module that cannot proceed may leave critical cells
at `—` (validate.py), which the host would refuse as null, and rewriting cannot fix that.

An upstream counts only when the run state records it accepted (or blocked) and the
bytes in the run still hash to the recorded digest; an upstream that is not so, or a
run without readable state, skips that cross-check only: the host refuses later with
its own reason, and no upstream is invented. Each host's input error is one
`host_input` finding carrying the host's message.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from rbotlib import fit, state
from rbotlib.handoff import Handoff, parse
from rbotlib.inventory import RunError
from rbotlib.model.house_inputs import (
    assessments,
    check_entity_profile,
    debt_like_items,
    effective_registers,
    equity_value,
    identities,
)
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.reader import ModelInputError
from rbotlib.validate import Finding

MODEL_INPUTS = ("CP-1", "CP-1D")
FIT_INPUTS = ("CP-1", "CP-1A")


def _record(run: Path) -> state.Record | None:
    try:
        return state.read(run)
    except (RunError, OSError, ValueError):
        return None  # not a governed run: no host step is known to read this Handoff


def _accepted(run: Path, record: state.Record, module: str) -> Handoff | None:
    """The module's Handoff when the run state has it accepted or blocked at these bytes."""
    step = record["steps"].get(module, {})
    if step.get("status") not in ("accepted", "blocked"):
        return None
    try:
        raw = (run / "handoffs" / f"{module}.md").read_bytes()
        found = parse(raw.decode("utf-8"))
    except (OSError, ValueError):
        return None  # no usable upstream: the host will say why
    if hashlib.sha256(raw).hexdigest() != step.get("sha256"):
        return None
    return None if found.orphan_tags or found.invalid_tags or found.duplicate_tags else found


def _model(cp1: Handoff, cp1d: Handoff | None) -> None:
    """`rbotlib.model.run._inputs` up to the Model: the checks that refuse a table."""
    regs = cp1_registers(cp1.tables)
    check_entity_profile(cp1.tables, regs)
    identities(cp1.tables)
    equity_value(cp1.tables)
    if cp1d is not None:
        judged = assessments(cp1d.tables)
        debt_like_items(cp1d.tables, regs)
        effective_registers(regs, judged)


def _upstream(
    module: str, h: Handoff, run: Path, record: state.Record, names: tuple[str, str]
) -> tuple[Handoff, Handoff | None] | None:
    """(required, optional) with the candidate in its own place; None when the required
    one is the other module and is not accepted."""
    required, optional = names
    if module == required:
        return h, _accepted(run, record, optional)
    other = _accepted(run, record, required)
    return None if other is None else (other, h)


def _runs(record: state.Record, host: str) -> bool:
    """The host step is in the run's plan (FIT is skipped without a portfolio context)."""
    return record["steps"].get(host, {}).get("status") not in (None, "skipped")


def _model_finding(module: str, h: Handoff, run: Path, record: state.Record) -> list[Finding]:
    if module not in MODEL_INPUTS or not _runs(record, "MODEL"):
        return []
    if not (pair := _upstream(module, h, run, record, MODEL_INPUTS)):
        return []
    try:
        _model(*pair)
    except ModelInputError as exc:
        return [Finding("host_input", f"MODEL: {exc}")]
    return []


def _fit_finding(module: str, h: Handoff, run: Path, record: state.Record) -> list[Finding]:
    if module not in FIT_INPUTS or not _runs(record, "FIT"):
        return []
    if not (pair := _upstream(module, h, run, record, FIT_INPUTS)):
        return []
    try:
        fit.instruments(*pair)
    except fit.FitError as exc:
        return [Finding("host_input", f"FIT: {exc}")]
    return []


def findings(h: Handoff, module: str, run: Path) -> list[Finding]:
    """`host_input` findings for the hosts that read `module`; empty for any other module."""
    record = _record(run)
    if record is None or h.front_matter.get("qa_status") == "Blocked":
        return []
    return _model_finding(module, h, run, record) + _fit_finding(module, h, run, record)
