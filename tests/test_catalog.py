from __future__ import annotations

import json
from pathlib import Path

from conftest import fixture_json, write_catalog, write_module
from rbotlib.catalog import check_tree, load_catalog, load_contracts
from rbotlib.rules import Rules


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
    write_catalog(tree, host_tables={"snapshot.view": "MODEL"})
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
