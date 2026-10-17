"""Front Page blocks from catalog `blocks` (Plan 07 task 07.3); hand-built run documents."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rbotlib.catalog import Block, Catalog, load_catalog, load_contracts
from rbotlib.handoff import parse
from rbotlib.report import ReportError
from rbotlib.report import blocks as blk
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]
CATALOG = load_catalog(RBOT_ROOT)
CONTRACTS = load_contracts(RBOT_ROOT, load_rules(RBOT_ROOT), [])
PLAN = list(next(p for p in CATALOG.pathways if p.id == "FULL_CREDIT_ASSESSMENT").depths["full"])
BLOCKS = CATALOG.blocks["credit_snapshot"]
FIXTURES = Path(__file__).parent / "fixtures/handoffs"


def _table(table_id: str) -> Record:
    return {"columns": ["facility_id", "value"], "rows": [[f"{table_id}-1", "1"]]}


def make_run(*, primary: bool = True, portfolios: bool = True) -> Record:
    """A run document with one row for every block table whose owner is in the plan."""
    run: Record = {
        "front_page": "credit_snapshot",
        "plan": PLAN,
        "primary": primary,
        "steps": {m: {"status": "accepted"} for m in PLAN},
        "handoffs": {m: {"tables": {}} for m in PLAN},
        "run_brief": {
            "tables": {
                "brief.portfolios": {"columns": ["id"], "rows": [["P1"]] if portfolios else []}
            }
        },
    }
    for block in BLOCKS:
        for table_id in block.tables:
            owner = blk.owner_of(table_id, run, CATALOG, CONTRACTS)
            if owner == "RUN_BRIEF":
                run["run_brief"]["tables"].setdefault(table_id, _table(table_id))
            elif owner in run["handoffs"]:
                run["handoffs"][owner]["tables"][table_id] = _table(table_id)
    return run


def entry(entries: list[Record], block_id: str) -> Record:
    return next(e for e in entries if e["id"] == block_id)


def test_every_catalog_block_has_one_owner() -> None:
    run = make_run()
    for block in BLOCKS:
        for table_id in block.tables:
            assert blk.owner_of(table_id, run, CATALOG, CONTRACTS)
    entries = blk.front_page_blocks(run, CATALOG, CONTRACTS)
    assert [e["id"] for e in entries] == [b.id for b in BLOCKS]
    assert len(entries) == 18


def test_owner_of_refuses_zero_or_two_owners() -> None:
    run = make_run()
    with pytest.raises(ReportError, match="has 0 owners"):
        blk.owner_of("no.such_table", run, CATALOG, CONTRACTS)
    two = {"CP-2": CONTRACTS["CP-2"], "CP-6": CONTRACTS["CP-2"]}
    with pytest.raises(ReportError, match="has 2 owners"):
        blk.owner_of("snapshot.credit_view", {"plan": ["CP-2", "CP-6"]}, CATALOG, two)


@pytest.mark.parametrize("primary", [True, False])
def test_primary_condition_lines(primary: bool) -> None:
    got = entry(
        blk.front_page_blocks(make_run(primary=primary), CATALOG, CONTRACTS), "transaction_summary"
    )
    assert got["shown"] is primary
    if primary:
        assert got["reason"] is None and got["tables"]
    else:
        assert got["reason"] == "Transaction summary: not a Primary run"
        assert got["tables"] == [] and got["charts"] == []


@pytest.mark.parametrize("attached", [True, False])
def test_portfolios_condition(attached: bool) -> None:
    got = entry(
        blk.front_page_blocks(make_run(portfolios=attached), CATALOG, CONTRACTS), "portfolio_fit"
    )
    assert got["shown"] is attached
    assert (got["reason"] is None) is attached
    if not attached:
        assert got["reason"] == "Portfolio Fit: no portfolio attached"


def test_unsupported_condition_refuses() -> None:
    block = Block("b", "B", (), (), "pf_ltm")
    catalog = Catalog(1, {}, {"credit_snapshot": ()}, (), {"credit_snapshot": (block,)})
    with pytest.raises(ReportError, match="condition pf_ltm not supported by this renderer"):
        blk.front_page_blocks(make_run(), catalog, CONTRACTS)


def test_failed_owner_renders_one_line_with_reason() -> None:
    run = make_run()
    run["steps"]["CP-2"] = {"status": "failed", "reason": "model returned nothing"}
    got = entry(blk.front_page_blocks(run, CATALOG, CONTRACTS), "credit_view")
    assert got["tables"] == []
    assert (
        got["line"]
        == "Sector Outlook, Credit Score, Credit Direction: CP-2 failed — model returned nothing"
    )
    sibling = entry(blk.front_page_blocks(run, CATALOG, CONTRACTS), "recommendation")
    assert sibling["line"] is None and sibling["tables"]


def test_skipped_owner_line_names_input() -> None:
    run = make_run()
    run["steps"]["CP-6"] = {"status": "skipped", "reason": "needs CP-3 Handoff"}
    got = entry(blk.front_page_blocks(run, CATALOG, CONTRACTS), "recommendation")
    assert got["line"].endswith("CP-6 skipped — needs CP-3 Handoff")
    assert got["tables"] == []


def test_blocked_owner_keeps_tables() -> None:
    run = make_run()
    run["steps"]["CP-3"]["status"] = "blocked"
    got = entry(blk.front_page_blocks(run, CATALOG, CONTRACTS), "valuation")
    assert got["line"] == "CP-3 Blocked"
    assert {t["table_id"]: t["status"] for t in got["tables"]}["cp3.talk_valuation"] == "blocked"


def test_owner_outside_the_plan_adds_no_table() -> None:
    got = entry(blk.front_page_blocks(make_run(), CATALOG, CONTRACTS), "chart_strip")
    assert [t["table_id"] for t in got["tables"]] == ["model.metrics", "model.summary"]
    assert got["line"] == "Net leverage, interest cover and liquidity: PROJECTION not in this run"


def test_missing_table_in_accepted_handoff_refuses() -> None:
    run = make_run()
    del run["handoffs"]["CP-2"]["tables"]["snapshot.credit_view"]
    with pytest.raises(ReportError, match=r"snapshot\.credit_view missing"):
        blk.front_page_blocks(run, CATALOG, CONTRACTS)
    run = make_run()
    del run["handoffs"]["CP-2"]
    with pytest.raises(ReportError, match=r"handoffs/CP-2\.md"):
        blk.front_page_blocks(run, CATALOG, CONTRACTS)


def test_capital_structure_join_fills_dashes() -> None:
    cs = {
        "columns": ["facility_id", "outstanding"],
        "rows": [["A", "10"], ["B", "20"], ["C", "30"]],
    }
    levels = {
        "columns": ["facility_id", "bid", "ask", "mid", "yield_or_dm", "valuation"],
        "rows": [["A", "99", "100", "99.5", "7.1", "V3"]],
    }
    rec = {"columns": ["facility_id", "recommendation"], "rows": [["B", "3 - MW"]]}
    before = copy.deepcopy((cs, levels, rec))
    columns, rows = blk.join_capital_structure(cs, levels, rec)
    assert columns == [
        "facility_id",
        "outstanding",
        "bid",
        "ask",
        "mid",
        "yield_or_dm",
        "valuation",
        "recommendation",
    ]
    assert rows == [
        ["A", "10", "99", "100", "99.5", "7.1", "V3", "—"],
        ["B", "20", "—", "—", "—", "—", "—", "3 - MW"],
        ["C", "30", "—", "—", "—", "—", "—", "—"],
    ]
    assert (cs, levels, rec) == before
    assert blk.join_capital_structure(cs, None, None)[1][0][2:] == ["—"] * 6


def read_tables(module: str) -> Record:
    h = parse((FIXTURES / f"{module}.md").read_text(encoding="utf-8"))
    return {"tables": {k: {"columns": t.columns, "rows": t.rows} for k, t in h.tables.items()}}


def test_call_band_from_fixture_handoffs() -> None:
    run = {"handoffs": {"CP-2": read_tables("CP-2"), "CP-6": read_tables("CP-6")}}
    band = blk.call_band(run)
    assert list(band["recommendation"]) == ["CLO", "Indexed Loans", "Indexed HY"]
    assert band["recommendation"]["CLO"]["recommendation"] == "3 - MW"
    assert (band["credit_score"], band["credit_direction"], band["sector_outlook"]) == (
        "4 - Weak",
        "Deteriorating",
        "Neutral",
    )
    assert band["instrument_line"] and band["fit_line"] is None


def test_call_band_without_handoffs_invents_nothing() -> None:
    band = blk.call_band({"handoffs": {}})
    assert band["recommendation"] == {} and band["credit_score"] is None
    assert band["instrument_line"] == [] and band["fit_line"] is None
    fit = {"tables": {"snapshot.portfolio_fit": {"columns": ["portfolio_id"], "rows": [["P1"]]}}}
    assert blk.call_band({"handoffs": {"FIT": fit}})["fit_line"] == {
        "rows": [{"portfolio_id": "P1"}]
    }


def test_format_number_examples() -> None:
    assert blk.format_number("3592", True) == "3,592"
    assert blk.format_number("-1234567.8910", True) == "-1,234,567.8910"
    assert blk.format_number("999", True) == "999"
    assert blk.format_number("2032", False) == "2032"
    assert blk.format_number("1.5x", True) == "1.5x"
    assert blk.format_number("0012345", True) == "0,012,345"


@given(st.text(alphabet="0123456789.-,x ab", max_size=14), st.booleans())
def test_format_number_never_changes_digits(text: str, money: bool) -> None:
    out = blk.format_number(text, money)
    assert [c for c in out if c.isdigit()] == [c for c in text if c.isdigit()]
    if not money:
        assert out == text
