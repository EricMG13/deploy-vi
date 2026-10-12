"""`rbot approve` and `rbot plan`: the analyst's Approval and the run's ordered steps.

`approve` checks the choice against `grading.json` (a Blocked Pathway needs
`--acknowledge-blocked`; a Run Brief changed since grading needs a new `rbot grade`),
refuses a Run Brief with a required field still a gap and a Primary run without a new
tranche, then writes `brief.approval` into `run-brief.md`, the plan and the Approval into
`run-state.json` (interfaces spec section 8.2), and renames the run folder from
`<YYYYMMDD>-<issuer>-pending` to `<YYYYMMDD>-<issuer>-<pathway>` (section 8.1). Steps that
Approval switches off are `skipped` with the fixed reasons of section 8.3; every other step
is `pending`, except CP-0, whose Handoff is recorded as it stands. `plan` prints the steps.

The files are written through a temporary file and `os.replace`; the folder is renamed last.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rbotlib import brief as rb
from rbotlib.catalog import load_catalog
from rbotlib.contract import load_contract
from rbotlib.fsio import write_atomic
from rbotlib.grade import BLOCKED, GRADING
from rbotlib.handoff import HandoffError, parse
from rbotlib.rules import Rules, load_rules
from rbotlib.validate import EXIT_VALID, check

STATE = "run-state.json"
PENDING_NAME = re.compile(r"(\d{8})-.+-pending(-\d+)?")
SKIPS = {
    "CP-DR": "not approved",
    "CP-8": "no prior case",
    "PROJECTION": "CP-2G not run",
    "FIT": "no portfolio context",
}


class ApprovalError(ValueError):
    """The Approval is refused; the message says what to change."""


@dataclass(frozen=True)
class Choice:
    pathway: str
    depth: str
    primary: bool
    analyst: str
    deep_research: bool
    untick: tuple[str, ...]
    prior_case: bool
    acknowledge_blocked: bool


def _load(path: Path, what: str) -> dict[str, Any]:
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ApprovalError(f"{path}: no readable {what} ({exc})") from exc
    return data


def _state(path: Path) -> dict[str, Any]:
    return _load(path, f"{STATE}; the run was not created with rbot new-run")


def _grading(path: Path) -> dict[str, Any]:
    return _load(path, "grading.json; run rbot grade first")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _graded(grading: dict[str, Any], choice: Choice) -> dict[str, Any]:
    pathways = {p["id"]: p for p in grading["pathways"]}
    if choice.pathway not in pathways:
        raise ApprovalError(f"unknown Pathway {choice.pathway!r}; graded: {', '.join(pathways)}")
    depths = pathways[choice.pathway]["depths"]
    if choice.depth not in depths:
        raise ApprovalError(f"{choice.pathway} has no {choice.depth} depth: {', '.join(depths)}")
    graded: dict[str, Any] = depths[choice.depth]
    if graded["status"] == BLOCKED and not choice.acknowledge_blocked:
        blocking = ", ".join(graded["blocking_modules"])
        raise ApprovalError(
            f"{choice.pathway} at {choice.depth} depth is Blocked by {blocking}: "
            + "; ".join(graded["limitations"])
            + ". It starts only after the analyst names the blocking modules back"
            " (--acknowledge-blocked)."
        )
    return graded


def _confirm(brief: rb.Brief, choice: Choice) -> None:
    """Apply the Approval to the Run Brief's fields, questions and Prior Case rows."""
    rb.apply_edit(brief.fields["analyst"], choice.analyst)
    missing = [n for n in rb.REQUIRED if brief.fields[n].status == rb.GAP]
    if missing:
        raise ApprovalError(f"the Run Brief still has gaps: {', '.join(missing)}; rbot brief --set")
    if choice.primary and not brief.tranches:
        raise ApprovalError(
            "a Primary run needs a new tranche: rbot brief --set-tranche NEW-1 <field>=<value>"
        )
    flag = "Yes" if choice.primary else "No"
    primary = brief.fields["primary"]
    if primary.value != flag:
        brief.fields["primary"] = rb.Entry(flag, rb.ASSERTED, flag, primary.cite)
    for name, value in (("pathway", choice.pathway), ("depth", choice.depth)):
        brief.fields[name] = rb.Entry(value, rb.ASSERTED, value, "")
    _confirm_rows(brief, choice)


def _confirm_rows(brief: rb.Brief, choice: Choice) -> None:
    """Tick the research questions and accept the newest Prior Case, as approved."""
    ids = [q[0] for q in brief.questions]
    unknown = [q for q in choice.untick if q not in ids]
    if unknown:
        raise ApprovalError(f"no research question {', '.join(unknown)}; questions: {ids}")
    for q in brief.questions:
        q[-1] = "No" if q[0] in choice.untick else "Yes"
    if choice.prior_case and not brief.prior:
        raise ApprovalError("no Prior Case was offered: the pack holds no earlier RBOT Report")
    newest = max(brief.prior, key=lambda r: r[1]) if choice.prior_case else None
    for row in brief.prior:
        row[-1] = "Yes" if row is newest else "No"


def new_name(run: Path, issuer_id: str, pathway: str) -> Path:
    """`<YYYYMMDD>-<issuer_slug>-<pathway_slug>`, with -2, -3, ... when taken (spec 8.1)."""
    match = PENDING_NAME.fullmatch(run.name)
    if not match:
        raise ApprovalError(f"{run.name} is not a pending run folder (<YYYYMMDD>-<issuer>-pending)")
    issuer = re.sub(r"[^a-z0-9]+", "-", issuer_id.lower()).strip("-")
    stem = f"{match.group(1)}-{issuer}-{pathway.lower().replace('_', '-')}"
    n, candidate = 1, run.parent / stem
    while candidate.exists():
        n += 1
        candidate = run.parent / f"{stem}-{n}"
    return candidate


def _cp0_step(run: Path, root: Path, rules: Rules) -> dict[str, Any]:
    text = (run / rb.CP0).read_text(encoding="utf-8")
    contract = load_contract(root / "modules" / "CP-0" / "contract.json", rules)
    code, _ = check(text, contract, rules, run)
    qa = parse(text).front_matter.get("qa_status", "")
    status = "accepted" if code == EXIT_VALID else "blocked"
    record = {"kind": "module", "status": status, "qa_status": qa, "handoff": rb.CP0}
    return record | {"sha256": _sha(run / rb.CP0), "validate_exit": code, "attempts": 1}


def _steps(
    plan: tuple[str, ...], state: dict[str, Any], brief: rb.Brief, choice: Choice, rules: Rules
) -> dict[str, dict[str, Any]]:
    off = {
        "CP-DR": not choice.deep_research,
        "CP-8": not choice.prior_case,
        "PROJECTION": "CP-2G" not in plan,
        "FIT": not brief.portfolios,
    }
    steps: dict[str, dict[str, Any]] = {}
    for step in plan:
        kind = "host" if step in rules.host_producers else "module"
        if step in state["steps"]:
            steps[step] = state["steps"][step]
        elif off.get(step):
            steps[step] = {"kind": kind, "status": "skipped", "reason": SKIPS[step]}
        else:
            steps[step] = {"kind": kind, "status": "pending", "reason": ""}
    return steps


def _approval_row(brief: rb.Brief, choice: Choice, graded: dict[str, Any], sha: str) -> list[str]:
    acknowledged = graded["blocking_modules"] if graded["status"] == BLOCKED else []
    flags = [
        "Yes" if f else "No" for f in (choice.primary, choice.deep_research, choice.prior_case)
    ]
    at = datetime.now(UTC).isoformat(timespec="seconds")
    head = [at, choice.analyst, choice.pathway, choice.depth, *flags, graded["status"]]
    return [*head, ", ".join(acknowledged) or rb.MISSING, sha]


@dataclass(frozen=True)
class Commit:
    """What Approval writes: the new Run Brief and state, and the folder's new name."""

    target: Path
    brief: str
    state: str


def _checked(run: Path, root: Path, grading: dict[str, Any]) -> None:
    """The run and the RBOT folder are as `rbot grade` saw them."""
    rb.refuse_if_approved(run)
    if _sha(run / rb.BRIEF) != grading["brief_sha256"]:
        raise ApprovalError(f"{rb.BRIEF} changed after rbot grade; run rbot grade again")
    if _sha(run / rb.CP0) != grading["cp0_sha256"]:
        raise ApprovalError(f"{rb.CP0} changed after rbot grade; run rbot grade again")


def _rebuilt(run: Path, rules: Rules) -> rb.Brief:
    """The Run Brief rebuilt from CP-0 and its edits."""
    return rb.build(run, run / rb.CP0, [], rules)


def _new_state(
    state: dict[str, Any], brief: rb.Brief, choice: Choice, graded: dict[str, Any]
) -> dict[str, Any]:
    accepted = next((r for r in brief.prior if r[-1] == "Yes"), None)
    blocked = graded["status"] == BLOCKED
    state = dict(state)
    state |= {"run_id": brief.run_id, "updated_at": brief.approval[0][0]}
    state |= {"run_brief": rb.BRIEF, "issuer_id": brief.fields["issuer_id"].value}
    state |= {"as_of_date": brief.fields["as_of_date"].value, "pathway": choice.pathway}
    state |= {"depth": choice.depth, "primary": choice.primary}
    state |= {"deep_research": choice.deep_research}
    state["prior_case"] = {
        "offered": bool(brief.prior),
        "accepted": accepted is not None,
        "report": accepted[0] if accepted else None,
    }
    state["approval"] = {
        "approved_at": brief.approval[0][0],
        "analyst": brief.approval[0][1],
        "pathway_grade": graded["status"],
        "acknowledged_blocked_modules": graded["blocking_modules"] if blocked else [],
        "limitations_shown": graded["limitations"],
    }
    return state


def prepare(run: Path, root: Path, rules: Rules, choice: Choice) -> Commit:
    """Read and check everything, and compute every file Approval writes; write nothing."""
    grading = _grading(run / GRADING)
    state = _state(run / STATE)
    _checked(run, root, grading)
    graded = _graded(grading, choice)
    pathway = load_catalog(root).pathway(choice.pathway)
    if pathway is None or choice.depth not in pathway.depths:
        raise ApprovalError("the catalog changed after rbot grade; run rbot grade again")
    plan = pathway.depths[choice.depth]
    brief = _rebuilt(run, rules)
    _confirm(brief, choice)
    approved_q = any(q[-1] == "Yes" for q in brief.questions)
    choice = replace(choice, deep_research=choice.deep_research and "CP-DR" in plan and approved_q)
    target = new_name(run, brief.fields["issuer_id"].value, choice.pathway)
    brief.run_id = target.name
    brief.approval = [_approval_row(brief, choice, graded, grading["brief_sha256"])]
    brief.approval[0][1] = brief.fields["analyst"].analyst_value
    text = rb.render(brief)
    state = dict(state, steps={**state.get("steps", {})})
    state["steps"].setdefault("CP-0", _cp0_step(run, root, rules))
    new = _new_state(state, brief, choice, graded)
    new["run_brief_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    new |= {"plan": list(plan), "steps": _steps(plan, state, brief, choice, rules)}
    return Commit(target, text, json.dumps(new, indent=2, ensure_ascii=False) + "\n")


def approve(run: Path, root: Path, rules: Rules, choice: Choice) -> Path:
    """Record the Approval; return the renamed run folder."""
    commit = prepare(run, root, rules, choice)
    write_atomic(run / rb.BRIEF, commit.brief)
    write_atomic(run / STATE, commit.state)
    run.rename(commit.target)
    return commit.target


def plan_lines(state: dict[str, Any]) -> list[str]:
    if not state.get("plan"):
        raise ApprovalError("the run is not approved yet; rbot approve sets its plan")
    head = f"{state['run_id']}: {state['pathway']} at {state['depth']} depth"
    flags = f"Primary {'Yes' if state['primary'] else 'No'}"
    flags += f", Deep Research {'Yes' if state['deep_research'] else 'No'}"
    flags += f", Prior Case {'Yes' if state['prior_case']['accepted'] else 'No'}"
    lines = [f"{head}; {flags}"]
    for n, step in enumerate(state["plan"], 1):
        record = state["steps"].get(step, {})
        reason = f" ({record['reason']})" if record.get("reason") else ""
        kind, status = record.get("kind", "?"), record.get("status", "?")
        lines.append(f"{n:>3}  {step:<11} {kind:<7} {status}{reason}")
    return lines


def approve_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    choice = Choice(
        args.pathway,
        args.depth,
        args.primary == "yes",
        args.analyst,
        args.deep_research == "yes",
        tuple(args.untick),
        args.prior_case == "yes",
        args.acknowledge_blocked,
    )
    try:
        target = approve(run, args.root, load_rules(args.root), choice)
    except (ApprovalError, rb.BriefError, HandoffError, OSError) as exc:
        print(exc)
        return 1
    args.run_dir = str(target)  # the command's log line goes to the renamed folder
    print(f"approved: {target}")
    print("\n".join(plan_lines(_state(target / STATE))))
    return 0


def plan_command(args: argparse.Namespace) -> int:
    try:
        print("\n".join(plan_lines(_state(Path(args.run_dir) / STATE))))
    except ApprovalError as exc:
        print(exc)
        return 1
    return 0


def add_commands(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    a = sub.add_parser("approve", help="record the Approval: Pathway, Depth, Primary")
    a.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    a.add_argument("--pathway", required=True)
    a.add_argument("--depth", required=True, choices=["full", "quick"])
    a.add_argument("--primary", required=True, choices=["yes", "no"])
    a.add_argument("--analyst", required=True)
    a.add_argument("--deep-research", choices=["yes", "no"], default="yes")
    a.add_argument("--untick", nargs="+", action="extend", default=[], metavar="QUESTION_ID")
    a.add_argument("--prior-case", choices=["yes", "no"], default="no")
    a.add_argument("--acknowledge-blocked", action="store_true")
    a.set_defaults(run=approve_command)
    p = sub.add_parser("plan", help="print the run's ordered steps with their status")
    p.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    p.set_defaults(run=plan_command)
