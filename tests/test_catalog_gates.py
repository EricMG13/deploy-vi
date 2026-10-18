"""The module-id and depth gates read the installed catalog, not a hard-coded list."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from test_bootstrap import approve, pending, ready

from conftest import write_module
from rbotlib import attempts, dispatch, state
from rbotlib import isolation_code_roots as code
from rbotlib import next as next_step
from rbotlib.catalog import module_ids
from rbotlib.inventory import RunError
from rbotlib.isolation_capture import Capture
from rbotlib.rules import RBOT_ROOT, Rules
from spec_fixture import SOURCES, build_tree, stand_in

SHIPPED = {
    "CP-0",
    "CP-1",
    "CP-1A",
    "CP-1B",
    "CP-1C",
    "CP-1D",
    "CP-DR",
    "CP-2",
    "CP-2A",
    "CP-3",
    "CP-5",
    "CP-6",
    "CP-L10",
}
QUICK = "CP-0 CP-1 CP-1A CP-1B MODEL CP-L10 CP-3 FIT CP-5 CP-6 CP-8".split()


@pytest.fixture
def stand_root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


def with_cpl10(tmp_path: Path, rules: Rules, name: str) -> Path:
    root = Path(
        shutil.copytree(RBOT_ROOT, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
    )
    write_module(root, stand_in("CP-L10", [], ()), rules)
    return root


def declared_record(module: str) -> state.Record:
    return {"steps": {module: {"kind": "module", "status": "pending"}}}


def test_module_ids_are_the_shipped_module_folders(stand_root: Path) -> None:
    assert module_ids(RBOT_ROOT) == SHIPPED
    assert "CP-L10" in module_ids(stand_root) and "CP-99" not in module_ids(stand_root)
    assert module_ids(stand_root / "absent") == frozenset()


def test_prepare_message_passes_the_gate_for_cpl10(tmp_path: Path, rules: Rules) -> None:
    root = with_cpl10(tmp_path, rules, "root")
    run = pending(tmp_path, root)
    ready(run, root)
    run = approve(run, root)
    # CP-L10 is a module now; the refusal comes from the run's own plan, not the id gate.
    with pytest.raises(RunError, match=r"CP-L10: undeclared; dispatch requires"):
        dispatch.prepare_message(run, root, "CP-L10")


@pytest.mark.parametrize("module", ["CP-99", "CP-L", "MODEL", "../CP-0"])
def test_prepare_message_refuses_non_modules(tmp_path: Path, module: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    with pytest.raises(RunError, match="undeclared module target"):
        dispatch.prepare_message(run, RBOT_ROOT, module)


def test_attempt_target_accepts_cpl10_for_accept_and_resume(stand_root: Path) -> None:
    record = declared_record("CP-L10")
    assert attempts.target(record, "CP-L10", stand_root) == record["steps"]["CP-L10"]
    assert attempts.declared(record, "CP-L10") == record["steps"]["CP-L10"]


@pytest.mark.parametrize("module", ["CP-99", "CP-L"])
def test_attempt_target_refuses_non_modules(module: str) -> None:
    with pytest.raises(RunError, match="unsupported module target"):
        attempts.target(declared_record(module), module, RBOT_ROOT)


def test_isolation_check_accepts_cpl10(tmp_path: Path, rules: Rules) -> None:
    roots = (with_cpl10(tmp_path, rules, "source"), with_cpl10(tmp_path, rules, "target"))
    assert code.observe(*roots, "CP-L10", Capture()).identity.target == "CP-L10"


@pytest.mark.parametrize("target", ["CP-99", "CP-L", "CP-8"])
def test_isolation_check_refuses_non_modules(tmp_path: Path, target: str) -> None:
    roots = (RBOT_ROOT, RBOT_ROOT)
    with pytest.raises(RunError, match="canonical installed"):
        code.observe(*roots, target, Capture())


def approved_record(depth: str, plan: list[str]) -> state.Record:
    return {
        "approval": {"analyst": "A"},
        "pathway": "FULL_CREDIT_ASSESSMENT",
        "depth": depth,
        "plan": plan,
    }


def test_next_plan_accepts_the_quick_list(stand_root: Path) -> None:
    assert next_step._plan(stand_root, approved_record("quick", QUICK)) == QUICK


@pytest.mark.parametrize(
    ("pathway", "depth", "plan"),
    [
        ("FULL_CREDIT_ASSESSMENT", "standard", QUICK),
        ("FULL_CREDIT_ASSESSMENT", "quick", QUICK[::-1]),
        ("NO_SUCH_PATHWAY", "quick", QUICK),
        ("FULL_CREDIT_ASSESSMENT", "standard", []),
    ],
)
def test_next_plan_refuses_unknown_or_divergent(
    stand_root: Path, pathway: str, depth: str, plan: list[str]
) -> None:
    record = approved_record(depth, plan) | {"pathway": pathway}
    with pytest.raises(RunError, match="unsupported or corrupt approved plan"):
        next_step._plan(stand_root, record)
