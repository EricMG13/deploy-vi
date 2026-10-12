# Executed Plan06.3 exact bootstrap replay

Source predecessor `7fd60911e68d2fa8b0705476978c4d92cad4b006`; runtime scopes `845c18a4558acf8600898f74e986d0d46fb44fee` (735lines/tree b596468109f3e65a14eef8bb251962613976ec23) and `defd6335f5c5e983a6922fce3b111d1145f70287` (107lines/tree e21e7a1b7e94c29ab24b63bfe568a6ab9bf17201). Their aggregate842 is not a single cap-compliant PR. No dependency/lock change.

Exact replay uses complete verified Git patches, never a hand assembly from snippets. Main staging `task-03-proof.py` executes this algorithm for each immediate-parent scope: obtain `git diff --binary --full-index <parent> <head>`; create a temporary `GIT_INDEX_FILE`; `git read-tree <parent>`; `git apply --cached --check -` then `git apply --cached -` with actual complete patch bytes; `git write-tree`; assert equality with `<head>^{tree}`; record ordinary numstat, patch SHA256 and uv.lock blob. It preserves the real index/worktree. `task-03-proof.json` records the actual reconstruction, docs scopes and final head/tree/lock. Any mismatch stops replay; no hand repair is authorized.

The new module below is exact executed source bytes. Existing `approve.py`/`state.py` and retained tests are fully included in the verified runtime commits/patches; this block is not a claim to contain all those unchanged files. The canonical orchestrator plan declares the actual bounded signatures, caller/lineage rule, required tests, observed-vs-unknown evidence and future owner boundary. Required roots are exactly those in main task-03-report.md. Causal tests precede repairs; confidence review then complete capped tournament precede local commits. Independent reviews are still pending.

## New executed file: rbot/scripts/rbotlib/bootstrap.py

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


def checked_cp0(run: Path, root: Path, rules: Rules, record: state.Record) -> QualifiedCP0:
    """Qualify actual bytes and return CP-0 metadata; no publication or lock acquisition.

    The caller must hold the shared writer lock to publish this result. Read-only
    callers receive an observation, not a lease against later filesystem changes.
    """
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

## Mechanical closure and limits

No public dispatch/accept/next/retry is implemented here. Validated CP-0 waits for actual analyst Approval; accepted/Blocked metadata and Handoff bytes survive rename; stale qualified bytes refuse and belong to later05/09 revalidation. `phase` is phase observation, not terminal retry entitlement or a filesystem lease. State/Approval share `.approve.lock`; no missing worker timestamp/model/physical attempt is manufactured. Approved missing readiness identity can retain an explicit placeholder lineage while the analyst supplies real required brief identity.

Existing proxy source layout and print-only Approval remain the bounded12 migration. A malformed old record is not repaired by inventing timestamps/identity. Fixture `_seed` now publishes actual production bootstrap fields at its observed fixture creation time. stderr preflight refusal names causes before any source logging, while owned valid failures still log. Sources/frozen/private corpus/global settings/main WIP stay unchanged; no push/merge/publication or work-desktop use.

Not verified: independent03 approval,04–16 generic orchestration/proxy/resume/scorecard and full branch closure; whole Plan06 coverage/security dependency/duplication/corpus closure; hostile directory replacement/ABA/crash consistency; Python3.11-floor/Windows/PowerShell execution; model-written proxy/A-B/fetch qualification;07rendering;08installed Claude/GPT Copilot, pip/tool capability and measured context budget.
