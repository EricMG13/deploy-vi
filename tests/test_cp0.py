from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from conftest import FIXTURES
from rbotlib.brief import EDITABLE, TRANCHE
from rbotlib.catalog import load_catalog
from rbotlib.contract import Contract, load_contract
from rbotlib.handoff import parse
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check

CP0_FIXTURE = FIXTURES / "handoffs" / "CP-0.md"
FOLDER = RBOT_ROOT / "modules" / "CP-0"

# Interfaces spec section 2.1: table id -> (column, critical, scale) in order.
SPEC = {
    "cp0.source_inventory": [
        ("file", True, None),
        ("class", True, "source_class"),
        ("document_type", True, "document_type"),
        ("entity_named", True, None),
        ("entity_match", True, "yes_no"),
        ("period_covered", False, None),
        ("document_date", False, None),
        ("readable", True, "yes_no"),
        ("image_read", True, "yes_no"),
        ("pages", False, None),
        ("sha256", True, None),
        ("note", False, None),
    ],
    "cp0.run_brief_prefill": [
        ("field", True, None),
        ("tranche_id", False, None),
        ("value", False, None),
        ("status", True, "brief_status"),
        ("cite", False, None),
    ],
    "cp0.research_questions": [
        ("question_id", True, None),
        ("question", True, None),
        ("why_it_matters", True, None),
        ("consumer_module", True, None),
        ("evidence_needed", True, None),
    ],
    "cp0.prior_case": [
        ("file", True, None),
        ("report_date", True, None),
        ("run_id", True, None),
        ("pathway", True, None),
        ("depth", True, None),
        ("offered", True, "yes_no"),
    ],
    "cp0.portfolios": [
        ("portfolio_id", True, None),
        ("portfolio_name", True, None),
        ("strategy", True, "strategy"),
        ("positions_file", True, None),
        ("limits_file", True, None),
        ("as_of_date", False, None),
    ],
}
MIN_ROWS = {"cp0.source_inventory": 1, "cp0.run_brief_prefill": 1}


@pytest.fixture
def cp0(rules: Rules) -> Contract:
    return load_contract(FOLDER / "contract.json", rules)


def test_cp0_tables_are_those_of_the_interfaces_spec(cp0: Contract) -> None:
    assert [t.id for t in cp0.tables] == list(SPEC)
    for spec in cp0.tables:
        assert [(c.name, c.critical, c.scale) for c in spec.columns] == SPEC[spec.id]
        assert spec.min_rows == MIN_ROWS.get(spec.id, 0)
        assert {"RUN_BRIEF", "REPORT"} <= set(spec.consumers)
    assert cp0.handoff_inputs() == []
    assert [(i.kind, i.values, i.required) for i in cp0.inputs] == [
        ("sources", ("issuer", "market", "portfolio"), True)
    ]


def test_module_md_is_generated_and_within_the_budget(cp0: Contract, rules: Rules) -> None:
    text = (FOLDER / "MODULE.md").read_text(encoding="utf-8")
    assert text == render_module(cp0, rules)
    canon = (RBOT_ROOT / "canon.md").read_bytes()
    assert len(text.encode()) + len(canon) <= load_catalog(RBOT_ROOT).size_budget_bytes


def test_the_process_names_every_run_brief_field_and_tranche_value(
    cp0: Contract, rules: Rules
) -> None:
    process = "\n".join(cp0.process)
    for name in (*EDITABLE, *TRANCHE):
        assert f"`{name}`" in process, name
    for scale in ("debt_type", "use_of_proceeds", "price_talk_stage", "unit"):
        for value in rules.scales[scale]:
            assert value in process, (scale, value)


def test_the_fixture_handoff_validates(cp0: Contract, rules: Rules) -> None:
    assert check(CP0_FIXTURE.read_text(encoding="utf-8"), cp0, rules) == (0, [])


def test_the_fixture_records_the_primary_pack_traps() -> None:
    h = parse(CP0_FIXTURE.read_text(encoding="utf-8"))
    table = h.tables["cp0.source_inventory"]
    rows = {r[0]: dict(zip(table.columns, r, strict=True)) for r in table.rows}
    assert len(rows) == 30
    vmo2 = rows["VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf"]
    assert (vmo2["class"], vmo2["entity_match"]) == ("issuer", "No")
    shot = rows["SYNTHETIC_Levels_Screenshot.png"]
    assert (shot["readable"], shot["image_read"]) == ("No", "Yes")
    assert rows["TRACE_12769GAC4_last_trade.txt"]["note"].startswith("duplicate of CZR_FINRA")


@pytest.mark.corpus
def test_the_fixture_validates_against_the_primary_pack(
    prepared_run: Callable[[str], Path], cp0: Contract, rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    text = CP0_FIXTURE.read_text(encoding="utf-8")
    assert check(text, cp0, rules, run) == (0, [])
    h = parse(text)
    table = h.tables["cp0.source_inventory"]
    files = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))["files"]
    index = {r["path"]: r for r in files}
    assert sorted(index) == sorted(r[0] for r in table.rows)
    for row in table.rows:
        record = dict(zip(table.columns, row, strict=True))
        assert record["sha256"] == index[record["file"]]["sha256"]
        assert int(record["pages"]) == index[record["file"]]["pages"]
        assert (record["image_read"] == "Yes") == index[record["file"]]["image_read"]


# ADR 0003 amendment (partial port): r14 CP-0 method sentences kept verbatim in the process.
R14 = RBOT_ROOT.parent / "reference" / "deploy-v-r14" / "skills" / "cp-0-source-readiness"
PORTED = (
    "Identify content from the document itself; filenames are hints only.",
    "Hash equality is duplicate evidence, not the only duplicate test.",
    "A base agreement and its amendment, waiver, supplement or release are distinct logical"
    " sources and remain separately active.",
    "Page count is never a value proxy: a short waiver may control while a long appendix does not.",
    "Surface material period, entity, definition, authority, coverage and source conflicts."
    " Never reconcile or choose a credit interpretation silently.",
    "State the minimum missing documents for the user's objective; never request every"
    " possible source by default.",
)


def test_the_process_keeps_the_r14_method_wording(cp0: Contract) -> None:
    r14 = " ".join(
        " ".join(p.read_text(encoding="utf-8").split()) for p in sorted(R14.rglob("*.md"))
    )
    process = " ".join(cp0.process)
    for sentence in PORTED:
        assert sentence in r14, sentence
        assert sentence in process, sentence


def test_module_md_asks_for_the_run_check(rules: Rules) -> None:
    text = (FOLDER / "MODULE.md").read_text(encoding="utf-8")
    assert "rbot.py validate <RUN>/handoffs/CP-0.md --module CP-0 --run <RUN>" in text
