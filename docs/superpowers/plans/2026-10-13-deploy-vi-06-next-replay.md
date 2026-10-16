# Plan06.6 executed whole-source replay — next

Exact final owned source/test bytes below. Sources are complete AST-parsable files; prose is outside each block. Apply only against the recorded exact Task06.6 boundary, preserve existing index/WIP, stop a tree/lock mismatch. Fixture outputs/receipts are controller tests, never physical sends. Ordinary lines count; this is one measured packaging scope, not an exemption.

## rbot/scripts/rbotlib/next.py
SHA256 b3b26d06d930489d3955c1a5ee1d3714ae5a9f4e5b0b83944996207dc6f255ab; bytes7315; physical_lines180.
```python
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
            record["pathway"] != "FULL_CREDIT_ASSESSMENT"
            or record["depth"] != "full"
            or pathway is None
            or list(pathway.depths.get("full", ())) != plan
        ):
            raise RunError("selected root: unsupported or corrupt approved plan")
    checked: list[str] = plan
    return checked


def _dependencies(root: Path, record: state.Record, rules: Rules) -> dict[str, tuple[str, ...]]:
    """Use selected contracts; host reader edges also require the approved Run Brief."""
    for name in ("rules.json", "catalog.json", "canon.md", "scripts/rbot.py"):
        dispatch._file(root, name)
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
        if current["status"] == "running" and current.get("accept_history"):
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
        argv = [
            sys.executable,
            str(root / "scripts/rbot.py"),
            "--root",
            str(root),
            module.lower(),
            "--run",
            str(run),
        ]
        selection["command"] = shlex.join(argv)
    elif kind == "module" and module is not None:
        validations = [e for e in histories[module] if e["event"] == "validation"]
        findings = f"validate/{module}.json" if validations else None
        message = dispatch.qualified_message(run, root, module, record, findings)
        selection["dispatch"] = f"dispatch/{module}.md"
        dispatch._target(run, selection["dispatch"])
    return selection, message


def select(run: Path, root: Path) -> state.Record:
    """One cooperating-writer transaction owns skips, selected bytes and checked state."""
    run, root = state.run_path(run), dispatch._root(root)
    state.read(run)
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
```

## tests/test_next.py
SHA256 d966620a436c0e89b469c4b022fe1d5657e407e674dd5389a07f92b1250061aa; bytes15454; physical_lines358.
```python
"""Fixture receipts and byte checks exercise controllers, never live Module sends."""

from __future__ import annotations

import copy
import json
import shlex
import shutil
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from test_accept import send
from test_bootstrap import approve, pending, ready

from rbotlib import accept, attempts, dispatch, state
from rbotlib import next as next_step
from rbotlib.cli import main
from rbotlib.contract import load_contract
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, load_rules


def approved(tmp_path: Path, root: Path) -> Path:
    run = pending(tmp_path, root)
    send(run, root)
    assert accept.accept(run, root, "CP-0")["exit"] == 0
    ready(run, root)
    return approve(run, root)


def blocked(run: Path, root: Path, module: str) -> None:
    contract = load_contract(root / f"modules/{module}/contract.json", load_rules(root))
    inputs = ", ".join(contract.handoff_inputs(required_only=True))
    text = (
        f"---\nmodule_id: {module}\nrun_id: {run.name}\nissuer_id: ACME\n"
        f"analysis_date: 2026-10-02\nqa_status: Blocked\ninputs: {inputs}\n---\n\n"
        "## Analysis\nGenerated fixture gaps.\n\n## Tables\n"
    )
    for table in contract.tables:
        text += (
            f"\n<!-- table: {table.id} -->\n| "
            + " | ".join(c.name for c in table.columns)
            + " |\n|"
            + "---|" * len(table.columns)
            + "\n"
        )
    text += (
        "\n## Gaps\nGenerated fixture gaps.\n\n## Citations\n"
        "<!-- table: citations -->\n| id | source | locator | excerpt |\n|---|---|---|---|\n"
    )
    (run / f"handoffs/{module}.md").write_text(text)
    send(run, root, module, f"fixture-{module}")
    assert accept.accept(run, root, module)["exit"] == 3


def test_public_selected_root_message_json_and_no_send(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root ' $(literal)\nline")
    run = pending(tmp_path, root)
    before = copy.deepcopy(state.read(run)["steps"])
    capsys.readouterr()
    assert main(["--root", str(root), "next", "--run", str(run)]) == 0
    out = capsys.readouterr()
    assert not out.err
    assert json.loads(out.out) == {
        "step": "CP-0",
        "kind": "module",
        "command": None,
        "dispatch": "dispatch/CP-0.md",
    }
    text = (run / "dispatch/CP-0.md").read_text()
    assert text == dispatch.qualified_message(run, root, "CP-0", state.read(run))
    assert json.dumps(str(root / "canon.md")) in text
    assert state.read(run)["steps"] == before
    assert not (run / "validate").exists()


@pytest.mark.parametrize("qa", ["Restricted", "Blocked"])
def test_checked_readiness_waits_with_no_done(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], qa: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    own.write_text(own.read_text().replace("qa_status: Restricted", f"qa_status: {qa}"))
    send(run, RBOT_ROOT)
    assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] in (0, 3)
    before = (run / state.STATE).read_bytes()
    capsys.readouterr()
    assert main(["next", "--run", str(run)]) == 1
    out = capsys.readouterr()
    assert not out.out and "waiting for analyst Approval" in out.err
    assert (run / state.STATE).read_bytes() == before


@pytest.mark.parametrize("status", ["failed", "skipped"])
def test_readiness_terminal_names_reason(tmp_path: Path, status: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    state.set_status(run, "CP-0", status, "fixture readiness failure")
    with pytest.raises(RunError, match=f"CP-0 readiness {status}: fixture readiness failure"):
        next_step.select(run, RBOT_ROOT)


def test_failed_required_chain_optional_leftovers_and_fixed_fit_skip(tmp_path: Path) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    state.set_status(run, "CP-1", "failed", "fixture rejected producer")
    (run / "handoffs/CP-1.md").symlink_to(tmp_path / "must never read")
    before = state.read(run)["steps"]["CP-0"]
    selected = next_step.select(run, RBOT_ROOT)
    assert selected["step"] == "CP-1A"  # CP-1 is optional for this consumer
    record = state.read(run)
    assert record["steps"]["CP-0"] == before
    assert record["steps"]["FIT"]["reason"] == "no portfolio context"
    for module in ("CP-1B", "CP-1D", "MODEL", "CP-2", "CP-3", "CP-6"):
        assert record["steps"][module]["status"] == "skipped"
        assert "required input" in record["steps"][module]["reason"]
    assert "CP-1: failed" in (run / selected["dispatch"]).read_text()
    state.set_status(run, "CP-1A", "failed", "fixture failure")
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-5"
    state.set_status(run, "CP-5", "failed", "fixture failure")
    assert next_step.select(run, RBOT_ROOT) == {
        "step": None,
        "kind": "done",
        "command": None,
        "dispatch": None,
    }


def test_blocked_required_input_runs_and_host_command_is_exact(tmp_path: Path) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root ' $(literal)\nline")
    run = approved(tmp_path, root)
    blocked(run, root, "CP-1")
    assert next_step.select(run, root)["step"] == "CP-1A"
    state.set_status(run, "CP-1A", "failed", "fixture optional failure")
    assert next_step.select(run, root)["step"] == "CP-1B"
    assert 'Blocked inputs: ["CP-1"]' in (run / "dispatch/CP-1B.md").read_text()
    for module in ("CP-1B", "CP-1D"):
        state.set_status(run, module, "failed", "fixture failure")
    before = state.read(run)["steps"]["MODEL"]
    selected = next_step.select(run, root)
    assert (
        selected["kind"] == "host" and selected["step"] == "MODEL" and selected["dispatch"] is None
    )
    assert shlex.split(selected["command"]) == [
        sys.executable,
        str(root / "scripts/rbot.py"),
        "--root",
        str(root),
        "model",
        "--run",
        str(run),
    ]
    assert state.read(run)["steps"]["MODEL"] == before
    assert not (run / "model.json").exists()
    (run.parent.parent / "acme_10k.txt").write_text("changed generated source")
    with pytest.raises(RunError, match="source sha256 changed"):
        next_step.select(run, root)


def test_running_resend_retry_and_partial_slot2_use_real_ledger(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    first = state.read(run)["steps"]["CP-0"]
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-0"
    assert state.read(run)["steps"]["CP-0"] == first
    (run / "handoffs/CP-0.md").write_text("DONE 0")
    assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == 2
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-0"
    assert '"exit": 2' in (run / "dispatch/CP-0.md").read_text()
    send(run, RBOT_ROOT, name="fixture-retry", retry=True)
    (run / "handoffs/CP-0.md").write_text("partial retry bytes")
    before = copy.deepcopy(state.read(run)["steps"]["CP-0"])
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-0"
    assert state.read(run)["steps"]["CP-0"] == before and before["attempts"] == 2
    assert len(attempts.read_history(run, "CP-0", before)) == 3


def test_registered_running_failed_input_is_future_owner_boundary(tmp_path: Path) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    blocked(run, RBOT_ROOT, "CP-1")
    send(run, RBOT_ROOT, "CP-1B", "fixture-consumer")
    (run / "handoffs/CP-1B.md").write_text("DONE 0")
    assert accept.accept(run, RBOT_ROOT, "CP-1B")["exit"] == 2
    record = state.read(run)
    events = attempts.read_history(run, "CP-1B", record["steps"]["CP-1B"])
    with pytest.raises(RunError, match="cannot set blocked to failed"):
        state.set_status(run, "CP-1", "failed", "future invalid edit")
    projected = copy.deepcopy(record)  # future-owner fixture, not public revalidation evidence
    projected["steps"]["CP-1"]["status"] = "failed"
    projected["steps"]["CP-1"]["reason"] = "future invalid edit"
    required = next_step._dependencies(RBOT_ROOT, projected, load_rules(RBOT_ROOT))
    with pytest.raises(RunError, match="registered running evidence requires"):
        next_step._traverse(projected, required)
    candidate = copy.deepcopy(record["steps"]["CP-1B"])
    candidate.update(status="skipped", reason="required input CP-1: failed")
    with pytest.raises(RunError, match="latest validation differs"):
        attempts._ordered(events, candidate)
    assert attempts.read_history(run, "CP-1B", state.read(run)["steps"]["CP-1B"]) == events


@pytest.mark.parametrize(
    "unsafe",
    ["symlink", "hardlink", "directory", "fifo", "corrupt-plan", "wrong-root", "orphan-history"],
)
def test_refusal_has_no_false_selection_or_state_publication(tmp_path: Path, unsafe: str) -> None:
    import os

    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    run = approved(tmp_path, root)
    other = tmp_path / "other"
    other.write_text("preserve")
    target = run / "dispatch/CP-1.md"
    target.parent.mkdir(exist_ok=True)
    if unsafe == "symlink":
        target.symlink_to(other)
    elif unsafe == "hardlink":
        target.hardlink_to(other)
    elif unsafe == "directory":
        target.mkdir()
    elif unsafe == "fifo":
        os.mkfifo(target)
    elif unsafe == "corrupt-plan":
        record = state.read(run)
        record["plan"][1:3] = record["plan"][1:3][::-1]
        (run / state.STATE).write_text(json.dumps(record))
    elif unsafe == "wrong-root":
        (root / "modules/CP-1/contract.json").write_text("{}")
    else:
        history = run / "validate/history/CP-1"
        history.mkdir(parents=True)
        (history / "000001.json").write_text("{}")
    before = (run / state.STATE).read_bytes()
    with pytest.raises((OSError, ValueError, KeyError, TypeError)):
        next_step.select(run, root)
    assert (run / state.STATE).read_bytes() == before and other.read_text() == "preserve"
    assert not (run / state.LOCK).exists()
    if unsafe not in ("symlink", "hardlink", "directory", "fifo"):
        assert not target.exists()


@settings(deadline=None)
@given(statuses=st.lists(st.sampled_from(sorted(state.STATUSES)), min_size=3, max_size=3))
def test_transition_projection_preserves_terminal_and_order(statuses: list[str]) -> None:
    # Pure dependency projection; no receipt, model, validation or accepted bytes invented.
    plan = ["CP-0", "CP-1", "CP-1A"]
    required = {"CP-0": (), "CP-1": ("CP-0",), "CP-1A": ("CP-0",)}
    record: state.Record = {
        "plan": plan,
        "steps": {
            m: {"status": s, "reason": "fixture"} for m, s in zip(plan, statuses, strict=True)
        },
    }
    before = copy.deepcopy(record)
    selected = next_step._traverse(record, required)
    for module, original in before["steps"].items():
        if original["status"] not in ("pending", "running"):
            assert record["steps"][module] == original
    eligible = [
        m
        for m in plan
        if record["steps"][m]["status"] in ("pending", "running")
        and all(record["steps"][n]["status"] in ("accepted", "blocked") for n in required[m])
    ]
    assert selected == (eligible[0] if eligible else None)


def test_actual_failed1_evidence_is_not_retried_or_erased(tmp_path: Path) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT, "CP-1", "fixture-denied-output")
    (run / "handoffs/CP-1.md").write_bytes(b"\xff")
    assert accept.accept(run, RBOT_ROOT, "CP-1")["exit"] == 1
    before = copy.deepcopy(state.read(run)["steps"]["CP-1"])
    events = attempts.read_history(run, "CP-1", before)
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-1A"
    assert state.read(run)["steps"]["CP-1"] == before
    assert attempts.read_history(run, "CP-1", before) == events
    assert before["status"] == "failed" and before["attempts"] == 1


@pytest.mark.parametrize("cause", ["source", "brief", "state", "history", "lock", "log"])
def test_context_refusal_preserves_evidence_and_owned_lock(tmp_path: Path, cause: str) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    if cause == "source":
        (run.parent.parent / "acme_10k.txt").write_text("edited generated source")
    elif cause == "brief":
        (run / "run-brief.md").write_text("edited generated brief")
    elif cause == "state":
        (run / state.STATE).write_text("corrupt")
    elif cause == "history":
        (run / "validate/history/CP-0/000001.json").write_text("changed event")
    elif cause == "lock":
        (run / state.LOCK).write_text("other owner")
    else:
        target = run / "log/rbot.log"
        target.rename(tmp_path / "external log")
        target.hardlink_to(tmp_path / "external log")
    before = (run / state.STATE).read_bytes()
    with pytest.raises((OSError, ValueError)):
        next_step.select(run, RBOT_ROOT)
    assert (run / state.STATE).read_bytes() == before
    assert not (run / "dispatch/CP-1.md").exists()
    if cause == "lock":
        assert (run / state.LOCK).read_text() == "other owner"
    else:
        assert not (run / state.LOCK).exists()


def test_actual_host_reader_edges_are_required_without_invented_brief_step(tmp_path: Path) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    record = state.read(run)
    needs = next_step._dependencies(RBOT_ROOT, record, load_rules(RBOT_ROOT))
    assert needs["MODEL"] == ("CP-1",)
    assert needs["FIT"] == ("CP-1", "CP-3")
    assert "RUN_BRIEF" not in record["plan"]
    assert record["run_brief_sha256"] is not None


@settings(deadline=None, max_examples=30)
@given(exits=st.lists(st.integers(min_value=0, max_value=4), min_size=1, max_size=3))
def test_actual_exit_sequences_preserve_terminal_and_retry_lifetime(
    exits: list[int], tmp_path_factory: pytest.TempPathFactory
) -> None:
    run = pending(tmp_path_factory.mktemp("next-exits"), RBOT_ROOT)
    original = (run / "handoffs/CP-0.md").read_text()
    for index, code in enumerate(exits):
        current = state.read(run)["steps"]["CP-0"]
        if current["status"] not in ("pending", "running"):
            break
        send(run, RBOT_ROOT, name=f"fixture-exit-{index}", retry=index > 0)
        own = run / "handoffs/CP-0.md"
        if code == 1:
            own.write_bytes(b"\xff")
        elif code == 2:
            own.write_text("DONE 0")
        elif code == 4:
            own.write_text(original.replace("module_id: CP-0", "module_id: CP-1"))
        else:
            own.write_text(
                original.replace("qa_status: Restricted", "qa_status: Blocked")
                if code == 3
                else original
            )
        assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == code
        step = state.read(run)["steps"]["CP-0"]
        events = attempts.read_history(run, "CP-0", step)
        assert step["attempts"] in (1, 2)
        if step["status"] == "running":
            assert code == 2 and step["attempts"] == 1
            assert next_step.select(run, RBOT_ROOT)["step"] == "CP-0"
        else:
            before = (run / state.STATE).read_bytes()
            with pytest.raises(RunError, match="readiness"):
                next_step.select(run, RBOT_ROOT)
            assert (run / state.STATE).read_bytes() == before
        assert attempts.read_history(run, "CP-0", state.read(run)["steps"]["CP-0"]) == events
```

Not verified: independent Task06.6 reviews, host sequencing/qualification/revalidation/resume/render/runtime and whole06/live/platform acceptance.
