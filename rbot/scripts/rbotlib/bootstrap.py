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
    raw: bytes


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
    if output_path(run, CP0).read_bytes() != raw:
        raise RunError("Handoff changed during CP-0 completion; no completion published")
    sha = hashlib.sha256(raw).hexdigest()
    current = record["steps"].get("CP-0")
    from rbotlib.current import result

    observed = result(current) if current else {}
    if current is None or current["status"] not in ("pending", "running", "accepted", "blocked"):
        raise RunError(f"{CP0}: completion requires pending/running or qualified CP-0")
    if current["status"] in ("accepted", "blocked"):
        if (
            current["sha256"] != sha
            or observed.get("exit", current["validate_exit"]) != code
            or current["qa_status"] != front["qa_status"]
        ):
            raise RunError(
                f"{CP0} changed after completion; use the CP-0 completion owner to revalidate"
            )
        return QualifiedCP0(dict(current), *identity, raw)
    step = dict(current) | {
        "status": "accepted" if code == EXIT_VALID else "blocked",
        "qa_status": front["qa_status"],
        "handoff": CP0,
        "sha256": sha,
        "validate_exit": code,
        "validated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    return QualifiedCP0(step, *identity, raw)


def complete_cp0(run: Path, root: Path, rules: Rules) -> state.Record:
    """Independently qualify CP-0 and publish through the existing state engine."""

    def change(record: state.Record) -> None:
        if record["approval"] is not None:
            raise RunError("CP-0 bootstrap is already approved; use the revalidation owner")
        qualified = checked_cp0(run, root, rules, record)
        record["steps"]["CP-0"] = qualified.step
        if "completion_origin" not in record and not qualified.step.get("accept_history"):
            from rbotlib.origins import capture

            record["completion_origin"] = capture(qualified.raw, "CP-0", "completion")

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
