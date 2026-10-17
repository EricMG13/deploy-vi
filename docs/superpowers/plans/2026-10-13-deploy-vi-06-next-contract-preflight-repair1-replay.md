# Plan06.6 executed contract-preflight repair1 replay

Base:549cac1b3eebbeda3317a490152876d4b079daa7/treefe06fcd91598a89fd79ede905653e3c21f65c34f. This separate repaired replay preserves the original rejected replay documents unchanged. Root required fresh implementation and reviews; this record is local execution/reproduction, not approval.

Execution: causal prepatch36unsupported failures/6regular passes5.70s; narrow complete lexical _file preflight in next._dependencies before context under state.update. Confidence review and one-function post-edit tournament kept incumbent. Tests below use generated copies and real receipt/accept/grade/Approval APIs; nonregular sentinel prevents opening. Regular extras remain in unchanged contracts_sha256. No dependency, cap exemption or upstream hash change.

Reproduction: create a separate index from the exact base, apply the recorded binary/full-index repair patch with git apply --cached, write-tree and require exact final recorded tree/uv.lock blob; compare both complete Python blocks below to their current files. Stop a mismatch. Main repair proof records actual executed command/patch/index/tree/lock evidence. Full06 gates remain06.16; fresh ordinary/sensitive review/root approval before06.7.

## rbot/scripts/rbotlib/next.py

Complete exact bytes:sha256 6dadedba1e41baae3e04b0129b8eda123856115f1b186bbf45c4dcb9c8d6c200.

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

## tests/test_next_contract_preflight.py

Complete exact bytes:sha256 5c3a3e0a47b4711d3404f3292fc47d62dbad17ea57899d453d5376ef66f9c6fb.

```python
"""Generated contract replacements prove preflight order without nonregular opens."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from test_next import approved, blocked

from rbotlib import dispatch, state
from rbotlib import next as next_step
from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, Rules


def extra_contract(root: Path, name: str = "EXTRA") -> Path:
    target = root / "modules" / name / "contract.json"
    target.parent.mkdir()
    data = json.loads((root / "modules/CP-5/contract.json").read_text())
    data["module_id"] = name
    target.write_text(json.dumps(data))
    return target


def branch_run(tmp_path: Path, root: Path, branch: str) -> Path:
    run = approved(tmp_path, root)
    if branch == "host":
        blocked(run, root, "CP-1")
        for module in ("CP-1A", "CP-1B", "CP-1D"):
            state.set_status(run, module, "failed", "generated optional failure")
    elif branch == "done":
        for module in state.read(run)["plan"][1:]:
            if state.read(run)["steps"][module]["status"] == "pending":
                state.set_status(run, module, "failed", "generated terminal failure")
    return run


@pytest.mark.parametrize("branch", ["module", "host", "done"])
@pytest.mark.parametrize("public", [False, True], ids=["library", "public"])
def test_regular_extra_contract_keeps_exact_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], branch: str, public: bool
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    extra_contract(root)
    run = branch_run(tmp_path, root, branch)
    before = state.read(run)["steps"]
    if public:
        capsys.readouterr()
        assert main(["--root", str(root), "next", "--run", str(run)]) == 0
        out = capsys.readouterr()
        assert not out.err
        selected = json.loads(out.out)
    else:
        selected = next_step.select(run, root)
    assert selected["kind"] == branch
    assert selected["step"] == {"module": "CP-1", "host": "MODEL", "done": None}[branch]
    after = state.read(run)["steps"]
    assert all(after[m] == s for m, s in before.items() if s["status"] != "pending")
    if selected["step"] is not None:
        assert after[selected["step"]] == before[selected["step"]]
    assert not (run / state.LOCK).exists()


def replace_contract(target: Path, external: Path, kind: str) -> Path:
    tmp_path = external.parent
    root = target.parents[2]
    if kind == "late":
        target = root / "modules/LATE/contract.json"
        target.parent.mkdir()
    elif kind == "parent":
        folder = target.parent
        folder.rename(tmp_path / "generated-module")
        folder.symlink_to(tmp_path / "generated-module", target_is_directory=True)
    else:
        target.unlink()
    if kind in ("symlink", "internal", "late"):
        target.symlink_to(external)
    elif kind == "hardlink":
        target.hardlink_to(external)
    elif kind == "directory":
        target.mkdir()
    elif kind == "fifo":
        os.mkfifo(target)
    return target


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param((b, p), id=f"{name}-{b}")
        for b in ("module", "host", "done")
        for p, name in ((False, "library"), (True, "public"))
    ],
)
@pytest.mark.parametrize(
    "kind", ["symlink", "internal", "hardlink", "parent", "directory", "fifo", "late"]
)
def test_unsupported_extra_contract_refuses_before_content_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    scenario: tuple[str, bool],
    kind: str,
) -> None:
    branch, public = scenario
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    target = extra_contract(root)
    run = branch_run(tmp_path, root, branch)
    external = (root if kind == "internal" else tmp_path) / "generated-contract.json"
    external_bytes = target.read_bytes()
    external.write_bytes(external_bytes)
    target = replace_contract(target, external, kind)
    before = (run / state.STATE).read_bytes()
    sources = {p: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    evidence = {p: p.read_bytes() for p in run.rglob("*") if p.is_file() and "log" not in p.parts}
    reads: list[Path] = []
    actual_read = Path.read_bytes

    def guarded_read(path: Path) -> bytes:
        if path == target:
            reads.append(path)
            if kind in ("directory", "fifo"):
                raise AssertionError("unsupported read sentinel: refused before opening")
        return actual_read(path)

    capsys.readouterr()
    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", guarded_read)
        try:
            if public:
                assert main(["--root", str(root), "next", "--run", str(run)]) == 1
                out = capsys.readouterr()
                assert not out.out and str(target.parent) in out.err
            else:
                with pytest.raises(RunError, match=r"symlink|hard link|regular file"):
                    next_step.select(run, root)
        finally:
            assert not reads, "contract content reached before safe regular-file refusal"
    assert (run / state.STATE).read_bytes() == before
    assert all(p.read_bytes() == data for p, data in evidence.items())
    assert {p for p in run.rglob("*") if p.is_file() and "log" not in p.parts} == set(evidence)
    assert not (run / state.LOCK).exists()
    assert all(p.read_bytes() == data for p, data in sources.items())
    assert external.read_bytes() == external_bytes


@pytest.mark.parametrize("branch", ["module", "host", "done"])
def test_complete_lexical_preflight_precedes_phase_under_writer_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, branch: str
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    extra_contract(root)
    run = branch_run(tmp_path, root, branch)
    candidates = {str(p.relative_to(root)) for p in (root / "modules").glob("*/contract.json")}
    guarded: set[str] = set()
    actual_file, actual_phase = dispatch._file, next_step._phase

    def observe_file(folder: Path, name: str) -> Path:
        if folder == root and name in candidates:
            assert (run / state.LOCK).exists()
            guarded.add(name)
        return actual_file(folder, name)

    def observe_phase(run: Path, root: Path, record: state.Record, rules: Rules) -> None:
        assert guarded == candidates and (run / state.LOCK).exists()
        actual_phase(run, root, record, rules)

    monkeypatch.setattr(dispatch, "_file", observe_file)
    monkeypatch.setattr(next_step, "_phase", observe_phase)
    assert next_step.select(run, root)["kind"] == branch
    assert not (run / state.LOCK).exists()
```

Not verified: independent approval/root acceptance; later06.7–16/Plans07–08, whole06/floor/platform/live Copilot/provider/A-B/fetch; hostile replacement/ABA/leases/crash recovery. No push, merge, publication or paused-desktop inspection.
