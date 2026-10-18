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
# CP1C Primary lacks four aligned operating peers; its truthful fixture is Blocked.
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
    assert check(fixture(module_id), contract(module_id, rules), rules) == (
        3 if module_id in {"CP-1C", "CP-4"} else 0,
        [],
    )


@pytest.mark.corpus
@pytest.mark.parametrize("module_id", MODULES)
def test_handoff_fixtures_validate(
    module_id: str, prepared_run: Callable[[str], Path], rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    assert check(fixture(module_id), contract(module_id, rules), rules, run) == (
        3 if module_id in {"CP-1C", "CP-4"} else 0,
        [],
    )


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


def test_cp6_states_the_quick_screening_gate_and_bars_a_full_basis_claim() -> None:
    """R4b / r14 D2: at Quick depth CP-6 is Restricted and never committee-ready."""
    text = (FOLDERS / "CP-6" / "MODULE.md").read_text(encoding="utf-8")
    assert "Screening Run when CP-L10 and CP-3 are available" in text
    assert "each rationale opens" in text and "Screening basis:" in text
    assert "Claim committee-ready or Full-basis conviction at Quick depth" in text


def test_cp1b_builds_no_ltm_figure_of_its_own(rules: Rules) -> None:
    """Rest review M13: the Model owns LTM; CP-1B compares only what CP-1 registers."""
    text = (FOLDERS / "CP-1B" / "MODULE.md").read_text(encoding="utf-8")
    assert "never build an LTM by hand" in text
    assert "prior-year comparable stub" not in text


def test_cp3_omits_an_image_read_only_instrument_with_a_named_gap() -> None:
    text = (FOLDERS / "CP-3" / "MODULE.md").read_text("utf-8")
    assert "Image-Read-only instrument has no priced row" in text
    assert "name the instrument and the missing usable level under" in text


def test_cp1d_recurrence_evidence_reaches_the_addback_verdict() -> None:
    text = (FOLDERS / "CP-1D" / "MODULE.md").read_text("utf-8")
    assert "Carry the named prior periods and recurrence evidence into" in text
    assert "never treat a recurring cost as a supported non-recurring add-back" in text


def test_cp1_consumers_include_the_real_register_readers(rules: Rules) -> None:
    tables = {t.id: set(t.consumers) for t in contract("CP-1", rules).tables}
    assert {"FIT", "CP-1D", "CP-2"} <= tables["cp1.model_period_register"]
    assert {"CP-1D", "CP-2"} <= tables["cp1.debt_facility_register"]
    for table_id in (
        "cp1.model_account_register",
        "cp1.adjusted_ebitda_bridge",
        "cp1.segment_revenue_schedule",
        "cp1.operating_kpi_schedule",
    ):
        assert "CP-2" in tables[table_id]


def test_cp_dr_states_the_fetch_limits_and_bars_model_knowledge() -> None:
    """Plan 10 R2 and R15: a 3-page cap per question, the fetched locator, no model knowledge."""
    text = (FOLDERS / "CP-DR" / "MODULE.md").read_text("utf-8")
    assert "at most 3 pages per question" in text
    assert "<URL> retrieved <YYYY-MM-DD>" in text
    assert "fetched/<nn>-<host>.md" in text
    assert "Do not use model background knowledge" in text


def test_cp_dr_requires_contrary_search_dated_downside_chain_and_reconciliation() -> None:
    """Plan 10 task 10.8a: the A/B round 1 depth fixes sit in the CP-DR process text."""
    text = (FOLDERS / "CP-DR" / "MODULE.md").read_text("utf-8")
    assert "Before writing `none found`, search every pack source" in text
    assert "segment and period splits" in text and "name what was searched" in text
    for part in (
        "starting condition",
        "first break",
        "financial transmission",
        "consequence for creditors",
        "trigger with a date or a threshold",
    ):
        assert part in text
    assert "dated downside chain" in text
    assert "list every conflict across sources, periods, definitions and the upstream" in text
    assert "CP-0, CP-1A and CP-1" in text
    assert "signing and announcement dates" in text
    assert "when CP-1 is present, use it for the entity, period and perimeter" in text
    assert "say where it was used" in text


def test_cp0_research_prompt_names_the_ids_consumers_and_the_pack_silence_rule() -> None:
    """Plan 10 R11: Q1..Q5, consumers CP-2, CP-3, CP-6, a public source class, pack silence."""
    text = (FOLDERS / "CP-0" / "MODULE.md").read_text("utf-8")
    assert "`Q1` to `Q5`" in text
    assert "(`CP-2`, `CP-3` or `CP-6`)" in text
    assert "was checked and found silent" in text
    assert "whose answer is in the pack" in text and "names a confidential or non-public" in text


def test_cp2_cites_the_deep_research_sector_view_for_the_outlook() -> None:
    """Plan 10 R13: cpdr.sector_view.outlook is cited evidence; CP-2 may differ and says why."""
    text = (FOLDERS / "CP-2" / "MODULE.md").read_text("utf-8")
    assert "cpdr.sector_view" in text and "say why" in text
