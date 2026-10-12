"""Every module Plan 05 ships against the interfaces spec, its generated prompt and its fixture.

`test_handoff_fixtures_validate[module]` is interfaces spec section 12.5 row 05: each module's
fixture Handoff under `tests/fixtures/handoffs/` validates with `--run` against the synthetic
Primary pack, so every citation names a pack file and its excerpt is in that file.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import pytest

from conftest import FIXTURES
from module_specs import INPUTS, TABLES, handoff_inputs, present_consumers
from rbotlib.catalog import load_catalog
from rbotlib.contract import Contract, load_contract
from rbotlib.handoff import cells
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


def _blocked(text: str, c: Contract) -> str:
    """The fixture as a Blocked module writes it: critical cells `—`, no citation, Blocked."""
    critical = {t.id: {col.name.casefold() for col in t.columns if col.critical} for t in c.tables}
    out, table_id, seen = [], "", 0  # `seen`: rows of the current table so far (header first)
    for line in text.splitlines():
        tag = re.match(r"<!-- table: (\S+) -->", line)
        if tag:
            table_id, seen, header = tag.group(1), 0, []
        elif line.startswith("|"):
            seen += 1
            if seen == 1:
                header = [h.casefold() for h in cells(line)]
            elif seen > 2 and table_id == "citations":
                continue  # a Blocked module cites nothing
            elif seen > 2 and table_id in critical:
                row = [
                    "—" if h in critical[table_id] else cell
                    for h, cell in zip(header, cells(line), strict=True)
                ]
                line = "| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |"
        out.append(line)
    blocked = re.sub(r" ?\[C\d+\]", "", "\n".join(out)) + "\n"
    return re.sub(r"qa_status: \w+", "qa_status: Blocked", blocked, count=1)


@pytest.mark.parametrize("module_id", [m for m in MODULES if m != "CP-0"])  # CP-0: Plan 04's checks
def test_a_blocked_module_can_write_a_handoff_that_exits_3(module_id: str, rules: Rules) -> None:
    """Rest review I1: every module's Blocked gate must be reachable through the checker."""
    c = contract(module_id, rules)
    blocked = _blocked(fixture(module_id), c)
    assert "qa_status: Blocked" in blocked and "—" in blocked
    assert check(blocked, c, rules) == (3, [])


def test_cp6_gate_names_only_handoffs_it_may_read(rules: Rules) -> None:
    """Rest review M4: CP-1 is not a CP-6 input (spec section 1) and the canon forbids reading
    it, so the gate may not ask for it."""
    c = contract("CP-6", rules)
    assert "CP-1" not in c.handoff_inputs()
    text = (FOLDERS / "CP-6" / "MODULE.md").read_text(encoding="utf-8")
    assert "Full Run when CP-2 (or CP-L10 at Quick depth) and CP-3" in text
    assert "Full Run when CP-1" not in text


def test_cp1b_builds_no_ltm_figure_of_its_own(rules: Rules) -> None:
    """Rest review M13: the Model owns LTM; CP-1B compares only what CP-1 registers."""
    text = (FOLDERS / "CP-1B" / "MODULE.md").read_text(encoding="utf-8")
    assert "never build an LTM by hand" in text
    assert "prior-year comparable stub" not in text
