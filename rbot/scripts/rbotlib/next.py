"""Select approved ordered work without sending workers or running host commands.

Accepted-edit recovery belongs to owner06.9. A registered running consumer whose
required input later fails needs that owner's auditable transition; preparation
cannot rewrite its immutable validation into a fabricated dependency result.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from datetime import datetime, timedelta
from pathlib import Path

from rbotlib import attempts, bootstrap, dispatch, state
from rbotlib.catalog import load_catalog
from rbotlib.contract import load_contract
from rbotlib.fsio import write_atomic
from rbotlib.inventory import RunError
from rbotlib.rules import Rules, load_rules

HOST_INPUTS = {"MODEL": ("CP-1",), "FIT": ("CP-1", "CP-3")}


def _plan(root: Path, record: state.Record) -> list[str]:
    catalog = load_catalog(root)
    plan = record["plan"]
    if record["approval"] is None:
        if plan != ["CP-0"]:
            raise RunError("bootstrap requires the declared CP-0 plan")
    else:
        pathway = catalog.pathway(record["pathway"])
        if (
            pathway is None
            or record["depth"] not in pathway.depths
            or list(pathway.depths[record["depth"]]) != plan
        ):
            raise RunError("selected root: unsupported or corrupt approved plan")
    checked: list[str] = plan
    return checked


def _dependencies(root: Path, record: state.Record, rules: Rules) -> dict[str, tuple[str, ...]]:
    """Use selected contracts; host reader edges also require the approved Run Brief."""
    for name in ("rules.json", "catalog.json", "canon.md", "scripts/rbot.py"):
        dispatch._file(root, name)
    # Context fingerprints every installed contract, including out-of-plan entries.
    for path in (root / "modules").glob("*/contract.json"):
        dispatch._file(root, str(path.relative_to(root)))
    plan = _plan(root, record)
    result: dict[str, tuple[str, ...]] = {}
    for position, module in enumerate(plan):
        if module in HOST_INPUTS:
            required = HOST_INPUTS[module]
        else:
            contract = load_contract(dispatch._file(root, f"modules/{module}/contract.json"), rules)
            if contract.module_id != module:
                raise RunError(f"{module}: selected contract identity differs")
            required = tuple(contract.handoff_inputs(required_only=True))
        if any(need not in plan[:position] for need in required):
            raise RunError(f"{module}: required input missing or out of order: {required}")
        result[module] = required
    return result


def _skip(record: state.Record, module: str, required: tuple[str, ...]) -> None:
    steps = record["steps"]
    current = steps[module]
    failed = next((n for n in required if steps[n]["status"] in ("failed", "skipped")), None)
    if failed is not None:
        if current["status"] == "running" and (
            current.get("accept_history") or current.get("host_execution")
        ):
            raise RunError(
                f"{module}: required input {failed} is {steps[failed]['status']}; "
                "registered running evidence requires the revalidation/recovery owner"
            )
        current.update(
            status="skipped", reason=f"required input {failed}: {steps[failed]['status']}"
        )


def _traverse(record: state.Record, required: dict[str, tuple[str, ...]]) -> str | None:
    """Propagate coherent failures before selecting the first eligible ordered step."""
    steps = record["steps"]
    for module in record["plan"]:
        if steps[module]["status"] in ("pending", "running"):
            _skip(record, module, required[module])
    plan: list[str] = record["plan"]
    for module in plan:
        if steps[module]["status"] in ("pending", "running") and all(
            steps[n]["status"] in ("accepted", "blocked") for n in required[module]
        ):
            return module
    if any(s["status"] in ("pending", "running") for s in steps.values()):
        raise RunError("approved plan has pending/running work without eligible required inputs")
    return None


def _phase(run: Path, root: Path, record: state.Record, rules: Rules) -> None:
    cp0 = record["steps"]["CP-0"]
    if record["approval"] is None:
        if cp0["status"] in ("accepted", "blocked"):
            bootstrap.checked_cp0(run, root, rules, record)
            raise RunError("CP-0 readiness completed; waiting for analyst Approval")
        if cp0["status"] in ("failed", "skipped"):
            raise RunError(f"CP-0 readiness {cp0['status']}: {cp0['reason']}")
    else:
        dispatch._context(run, root, record, rules)


def _continuation_inputs(
    run: Path, root: Path, record: state.Record, module: str, evidence: state.Record
) -> None:
    from rbotlib.fit_host import Fit
    from rbotlib.host_evidence import context
    from rbotlib.model.host import Model

    backend = Model() if module == "MODEL" else Fit()
    captured = backend.inputs(run, root, record)
    from rbotlib.host_evidence import match_inputs

    match_inputs(evidence, captured.hashes(), captured.missing, context(root, record))


def _host_command(run: Path, root: Path, record: state.Record, module: str) -> str:
    if record["steps"][module]["status"] == "running":
        from rbotlib.host_evidence import checked, observe

        evidence = checked(record, module, f"host-{module.lower()}/1")
        observe(run, evidence["invocations"][-1])
        if not any("failure" in i for i in evidence["invocations"]):
            _continuation_inputs(run, root, record, module, evidence)
    argv = [
        sys.executable,
        str(root / "scripts/rbot.py"),
        "--root",
        str(root),
        module.lower(),
        "--run",
        str(run),
    ]
    return shlex.join(argv)


def _selection(run: Path, root: Path, record: state.Record) -> tuple[state.Record, str]:
    rules = load_rules(dispatch._file(root, "rules.json").parent)
    required = _dependencies(root, record, rules)
    dispatch._prepared(run, record)
    histories = {
        m: attempts.read_history(run, m, record["steps"][m])
        for m in record["plan"]
        if record["steps"][m]["kind"] == "module"
    }
    _phase(run, root, record, rules)
    module = _traverse(record, required)
    kind = record["steps"][module]["kind"] if module else "done"
    selection: state.Record = dict(step=module, kind=kind, command=None, dispatch=None)
    message = ""
    if kind == "host" and module is not None:
        selection["command"] = _host_command(run, root, record, module)
    elif kind == "module" and module is not None:
        validations = [e for e in histories[module] if e["event"] == "validation"]
        findings = f"validate/{module}.json" if validations else None
        message = dispatch.qualified_message(run, root, module, record, findings)
        selection["dispatch"] = f"dispatch/{module}.md"
        dispatch._target(run, selection["dispatch"])
    return selection, message


def _eligible(record: state.Record) -> None:
    from rbotlib.runs import _clock

    now = _clock(None)
    created = datetime.fromisoformat(record["created_at"])
    if created > now:
        raise RunError("run created_at is in the future; resume refused")
    if now - created > timedelta(days=30):
        raise RunError("run older than 30 days; use new-run instead of resume")


def select(run: Path, root: Path) -> state.Record:
    """One cooperating-writer transaction owns skips, selected bytes and checked state."""
    run, root = state.run_path(run), dispatch._root(root)
    _eligible(state.read(run))
    from rbotlib.current import reconcile

    reconcile(run, root)
    dispatch._target(run, "log/rbot.log")
    selection: state.Record = {}
    message = ""

    def change(record: state.Record) -> None:
        nonlocal message
        chosen, message = _selection(run, root, record)
        selection.update(chosen)

    def publish() -> None:
        if selection["kind"] == "module":
            target = dispatch._target(run, selection["dispatch"])
            target.parent.mkdir(exist_ok=True)
            write_atomic(dispatch._target(run, selection["dispatch"]), message)

    state.update(run, change, publish)
    return selection


def run_command(args: argparse.Namespace) -> int:
    try:
        print(json.dumps(select(Path(args.run_dir), args.root), ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print(f"error: next: {exc}", file=sys.stderr)
        return 1
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser(
        "next", help="select checked ordered work; prepare, never send or execute"
    )
    parser.add_argument("--run", dest="run_dir", required=True)
    parser.set_defaults(run=run_command, log_run_guard=state.log_run_path)
