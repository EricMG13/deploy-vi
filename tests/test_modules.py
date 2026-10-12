"""Every module Plan 05 ships against the interfaces spec, its generated prompt and its fixture.

`test_handoff_fixtures_validate[module]` is interfaces spec section 12.5 row 05: each module's
fixture Handoff under `tests/fixtures/handoffs/` validates with `--run` against the synthetic
Primary pack, so every citation names a pack file and its excerpt is in that file.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from conftest import FIXTURES
from module_specs import INPUTS, TABLES, handoff_inputs, present_consumers
from rbotlib.catalog import load_catalog
from rbotlib.contract import Contract, load_contract
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check

MODULES = sorted(TABLES)
FOLDERS = RBOT_ROOT / "modules"


def contract(module_id: str, rules: Rules) -> Contract:
    return load_contract(FOLDERS / module_id / "contract.json", rules)


def fixture(module_id: str) -> str:
    return (FIXTURES / "handoffs" / f"{module_id}.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("module_id", MODULES)
def test_tables_are_those_of_the_interfaces_spec(module_id: str, rules: Rules) -> None:
    c = contract(module_id, rules)
    assert [t.id for t in c.tables] == [t.id for t in TABLES[module_id]]
    for table, spec in zip(c.tables, TABLES[module_id], strict=True):
        assert [
            (col.name, col.critical, col.scale) for col in table.columns
        ] == spec.column_tuples()
        assert table.min_rows == spec.min_rows, table.id
        assert list(table.consumers) == present_consumers(spec, FOLDERS, rules), table.id


@pytest.mark.parametrize("module_id", MODULES)
def test_inputs_are_those_of_the_interfaces_spec(module_id: str, rules: Rules) -> None:
    c, spec = contract(module_id, rules), INPUTS[module_id]
    assert handoff_inputs(c) == (spec.required.split(), spec.optional.split())
    classes = sorted({v for i in c.inputs if i.kind == "sources" for v in i.values})
    assert classes == sorted(spec.sources.split())
    brief = [v for i in c.inputs if i.kind == "run_brief" for v in i.values]
    assert brief == spec.run_brief.split()
    assert all(i.why for i in c.inputs)


@pytest.mark.parametrize("module_id", MODULES)
def test_module_md_is_generated_and_within_the_budget(module_id: str, rules: Rules) -> None:
    text = (FOLDERS / module_id / "MODULE.md").read_text(encoding="utf-8")
    assert text == render_module(contract(module_id, rules), rules)
    canon = (RBOT_ROOT / "canon.md").read_bytes()
    assert len(text.encode()) + len(canon) <= load_catalog(RBOT_ROOT).size_budget_bytes


@pytest.mark.parametrize("module_id", MODULES)
def test_the_fixture_handoff_validates(module_id: str, rules: Rules) -> None:
    assert check(fixture(module_id), contract(module_id, rules), rules) == (0, [])


@pytest.mark.corpus
@pytest.mark.parametrize("module_id", MODULES)
def test_handoff_fixtures_validate(
    module_id: str, prepared_run: Callable[[str], Path], rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    assert check(fixture(module_id), contract(module_id, rules), rules, run) == (0, [])
