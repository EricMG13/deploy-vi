from __future__ import annotations

import json
from pathlib import Path

from conftest import fixture_json, write_catalog, write_module
from rbotlib.catalog import check_tree, load_catalog, load_contracts
from rbotlib.rules import RBOT_ROOT, Rules
from spec_fixture import build_tree


def test_a_consistent_tree_has_no_problems(tree: Path, rules: Rules) -> None:
    assert check_tree(tree, rules) == []


def test_load_catalog_reads_pathways(tree: Path) -> None:
    catalog = load_catalog(tree)
    assert catalog.pathways[0].depths["full"] == ("CP-X", "CP-Y")
    assert catalog.front_pages["fp"] == ("snapshot.view",)


def test_a_hand_edited_module_md_is_stale(tree: Path, rules: Rules) -> None:
    path = tree / "modules" / "CP-X" / "MODULE.md"
    path.write_text(path.read_text(encoding="utf-8") + "extra\n", encoding="utf-8")
    assert check_tree(tree, rules) == [
        "CP-X: MODULE.md is missing or stale; run render-module --write"
    ]


def test_a_module_over_budget_is_named(tree: Path, rules: Rules) -> None:
    write_catalog(tree, size_budget_bytes=100)
    problems = check_tree(tree, rules)
    assert "CP-X: MODULE.md + canon.md exceed 100 bytes" in problems


def test_a_reader_that_does_not_take_the_handoff_is_named(tree: Path, rules: Rules) -> None:
    data = fixture_json("contract_cp_y.json")
    data["inputs"] = [{"sources": ["issuer"], "why": "filings"}]
    write_module(tree, data, rules)
    problems = check_tree(tree, rules)
    assert "CP-X.cpx.facts: CP-Y does not take CP-X's Handoff" in problems


def test_an_unknown_consumer_is_named(tree: Path, rules: Rules) -> None:
    data = fixture_json("contract_cp_x.json")
    data["tables"][0]["consumers"] = ["CP-NOPE"]
    write_module(tree, data, rules)
    assert "CP-X.cpx.facts: unknown consumer CP-NOPE" in check_tree(tree, rules)


def test_a_consumer_before_its_producer_is_named(tree: Path, rules: Rules) -> None:
    pathway = {
        "id": "EXAMPLE",
        "label": "Example",
        "front_page": "fp",
        "depths": {"full": ["CP-Y", "CP-X"]},
    }
    write_catalog(tree, pathways=[pathway])
    assert "EXAMPLE: CP-Y runs before its input CP-X" in check_tree(tree, rules)


def test_a_required_input_missing_from_the_pathway_is_named(tree: Path, rules: Rules) -> None:
    pathway = {
        "id": "EXAMPLE",
        "label": "Example",
        "front_page": "fp",
        "depths": {"full": ["CP-Y"]},
    }
    write_catalog(tree, pathways=[pathway])
    problems = check_tree(tree, rules)
    assert "EXAMPLE: CP-Y runs before its input CP-X" in problems
    assert "EXAMPLE: front-page table snapshot.view has 0 owners" in problems


def test_an_optional_input_outside_the_pathway_is_fine(tree: Path, rules: Rules) -> None:
    data = fixture_json("contract_cp_y.json")
    data["inputs"].append({"handoff": "CP-X2", "required": False, "why": "context"})
    write_module(tree, data, rules)
    assert check_tree(tree, rules) == []


def test_a_front_page_table_owned_twice_is_named(tree: Path, rules: Rules) -> None:
    pathway = {
        "id": "EXAMPLE",
        "label": "Example",
        "front_page": "fp",
        "depths": {"full": ["CP-X", "CP-Y", "MODEL"]},
    }
    write_catalog(tree, host_tables={"snapshot.view": "MODEL"}, pathways=[pathway])
    problems = check_tree(tree, rules)
    assert "EXAMPLE: front-page table snapshot.view has 2 owners" in problems
    assert "host table snapshot.view is also a module table" in problems


def test_unknown_modules_and_front_pages_are_named(tree: Path, rules: Rules) -> None:
    pathway = {
        "id": "EXAMPLE",
        "label": "Example",
        "front_page": "nope",
        "depths": {"full": ["CP-X", "CP-Q"]},
    }
    write_catalog(tree, pathways=[pathway])
    problems = check_tree(tree, rules)
    assert "EXAMPLE: unknown front page nope" in problems
    assert "EXAMPLE: unknown module CP-Q" in problems


def test_bad_contracts_and_misfiled_modules_are_named(tree: Path, rules: Rules) -> None:
    bad = tree / "modules" / "CP-BAD"
    bad.mkdir()
    (bad / "contract.json").write_text(json.dumps({"module_id": "CP-BAD"}), encoding="utf-8")
    moved = tree / "modules" / "CP-W"
    moved.mkdir()
    (moved / "contract.json").write_text(
        (tree / "modules" / "CP-Y" / "contract.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    problems = check_tree(tree, rules)
    assert any(p.startswith("CP-BAD: CP-BAD: missing title") for p in problems)
    assert "CP-W: module_id is 'CP-Y'" in problems


def test_a_module_folder_without_a_contract_is_named(tree: Path, rules: Rules) -> None:
    ghost = tree / "modules" / "CP-GHOST"
    ghost.mkdir()
    (ghost / "MODULE.md").write_text("hand written\n", encoding="utf-8")
    assert "CP-GHOST: no contract.json" in check_tree(tree, rules)


def test_a_misfiled_contract_never_replaces_the_original(tree: Path, rules: Rules) -> None:
    moved = tree / "modules" / "CP-Z"
    moved.mkdir()
    data = fixture_json("contract_cp_y.json")
    data["title"] = "Impostor"
    (moved / "contract.json").write_text(json.dumps(data), encoding="utf-8")
    problems: list[str] = []
    contracts = load_contracts(tree, rules, problems)
    assert "CP-Z: module_id is 'CP-Y'" in problems
    assert contracts["CP-Y"].title == "Example Consumer"


def _depth_list(tree: Path, modules: list[str]) -> None:
    pathway = {"id": "EXAMPLE", "label": "Example", "front_page": "fp", "depths": {"full": modules}}
    write_catalog(tree, pathways=[pathway])


def _needs_model(tree: Path, rules: Rules, *, required: bool) -> None:
    data = fixture_json("contract_cp_y.json")
    data["inputs"].append({"handoff": "MODEL", "required": required, "why": "the Model"})
    write_module(tree, data, rules)


def test_host_steps_in_a_list_need_no_contract(tree: Path, rules: Rules) -> None:
    _depth_list(tree, ["CP-X", "MODEL", "CP-Y", "FIT"])
    assert check_tree(tree, rules) == []


def test_a_module_runs_after_the_host_step_it_reads(tree: Path, rules: Rules) -> None:
    _needs_model(tree, rules, required=True)
    _depth_list(tree, ["CP-X", "MODEL", "CP-Y"])
    assert check_tree(tree, rules) == []
    _depth_list(tree, ["CP-X", "CP-Y", "MODEL"])
    assert "EXAMPLE: CP-Y runs before its input MODEL" in check_tree(tree, rules)
    _depth_list(tree, ["CP-X", "CP-Y"])
    assert "EXAMPLE: CP-Y runs before its input MODEL" in check_tree(tree, rules)


def test_an_optional_host_input_is_ordered_only_when_present(tree: Path, rules: Rules) -> None:
    _needs_model(tree, rules, required=False)
    _depth_list(tree, ["CP-X", "CP-Y"])
    assert check_tree(tree, rules) == []
    _depth_list(tree, ["CP-X", "CP-Y", "MODEL"])
    assert check_tree(tree, rules) == ["EXAMPLE: CP-Y runs before its input MODEL"]


def test_a_host_id_outside_the_rules_is_named(tree: Path, rules: Rules) -> None:
    _depth_list(tree, ["CP-X", "MODELS", "CP-Y", "CP-Q"])
    assert check_tree(tree, rules) == [
        "EXAMPLE: MODELS is not a host producer (MODEL, RUN_BRIEF, PROJECTION, FIT)",
        "EXAMPLE: unknown module CP-Q",
    ]


def test_blocks_load_with_their_conditions(tree: Path, rules: Rules) -> None:
    blocks = [
        {"id": "view", "title": "View", "tables": ["snapshot.view"], "charts": []},
        {"id": "fit", "tables": ["snapshot.view"], "condition": "portfolios"},
    ]
    write_catalog(tree, front_pages={"fp": {"tables": ["snapshot.view"], "blocks": blocks}})
    catalog = load_catalog(tree)
    assert [(b.id, b.title, b.condition) for b in catalog.blocks["fp"]] == [
        ("view", "View", "always"),
        ("fit", "fit", "portfolios"),
    ]
    assert catalog.pathway("EXAMPLE") is catalog.pathways[0]
    assert catalog.pathway("NOPE") is None
    assert check_tree(tree, rules) == []
    blocks[1]["condition"] = "sometimes"
    write_catalog(tree, front_pages={"fp": {"tables": ["snapshot.view"], "blocks": blocks}})
    assert check_tree(tree, rules) == ["front page fp block fit: unknown condition 'sometimes'"]


def test_check_flags_block_table_not_in_tables(tree: Path, rules: Rules) -> None:
    blocks = [{"id": "view", "tables": ["snapshot.view", "snapshot.other"]}]
    write_catalog(tree, front_pages={"fp": {"tables": ["snapshot.view"], "blocks": blocks}})
    assert check_tree(tree, rules) == [
        "front page fp block view: table snapshot.other not in tables"
    ]


def test_check_flags_unknown_chart(tree: Path, rules: Rules) -> None:
    blocks = [{"id": "view", "tables": ["snapshot.view"], "charts": ["chart.rv_hy", "chart.nope"]}]
    write_catalog(tree, front_pages={"fp": {"tables": ["snapshot.view"], "blocks": blocks}})
    assert check_tree(tree, rules) == ["front page fp block view: unknown chart chart.nope"]


# Interfaces spec section 3: every host-produced table and its producer (amendment A7).
HOST_TABLES = {
    "RUN_BRIEF": "snapshot.run_header snapshot.transaction_summary brief.run_brief_fields "
    "brief.portfolios brief.research_questions brief.prior_case brief.approval",
    "MODEL": "snapshot.capital_structure snapshot.capital_structure_totals "
    "snapshot.ebitda_adjustments snapshot.financial_columns snapshot.financials model.summary "
    "model.metrics model.house model.maturity_wall model.limitations",
    "PROJECTION": "model.projection_summary model.projection_interest model.forecast_checks",
    "FIT": "snapshot.portfolio_fit fit.limit_headroom",
}
# Interfaces spec section 4.1: the Credit Snapshot's blocks in order, with their conditions.
SNAPSHOT_BLOCKS = [
    ("header", "always"),
    ("company_profile", "always"),
    ("credit_view", "always"),
    ("recommendation", "always"),
    ("transaction_summary", "primary"),
    ("capital_structure", "always"),
    ("capital_structure_totals", "always"),
    ("maturity_wall", "always"),
    ("business_description", "always"),
    ("ebitda_adjustments", "always"),
    ("thesis_catalysts", "always"),
    ("strengths_weaknesses", "always"),
    ("historical_performance", "always"),
    ("financials", "always"),
    ("chart_strip", "always"),
    ("relative_value", "always"),
    ("valuation", "always"),
    ("portfolio_fit", "portfolios"),
]  # block 19, What changed (cp8.what_changed), returns with CP-8 in Plan 11
SNAPSHOT_CHARTS = (
    "chart.model_strip chart.maturity_wall chart.capital_structure chart.ebitda_bridge "
    "chart.rv_loan chart.rv_hy chart.talk_range chart.fit_bullets"
)


def test_the_shipped_catalog_carries_the_host_tables_and_the_snapshot_blocks() -> None:
    catalog = load_catalog(RBOT_ROOT)
    expected = {t: host for host, tables in HOST_TABLES.items() for t in tables.split()}
    assert catalog.host_tables == expected
    blocks = catalog.blocks["credit_snapshot"]
    assert [(b.id, b.condition) for b in blocks] == SNAPSHOT_BLOCKS
    tables = catalog.front_pages["credit_snapshot"]
    assert len(tables) == len(set(tables)) == 25
    assert {t for b in blocks for t in b.tables} == set(tables)
    assert sorted(c for b in blocks for c in b.charts) == sorted(SNAPSHOT_CHARTS.split())
    assert [p.id for p in catalog.pathways] == ["FULL_CREDIT_ASSESSMENT"]


def test_the_section_5_lists_are_ordered_under_a2(tmp_path: Path, rules: Rules) -> None:
    root = build_tree(tmp_path, rules, {})
    ordering = ("runs before", "unknown module", "host producer", "MODULE.md", "consumer")
    problems = [p for p in check_tree(root, rules) if any(word in p for word in ordering)]
    assert problems == []
    assert len(load_catalog(root).pathways) == 6
