from __future__ import annotations

from conftest import fixture_json
from rbotlib.contract import contract_from_dict
from rbotlib.render import GENERATED, render_module
from rbotlib.rules import Rules


def test_module_md_carries_the_contract_and_the_checked_rules(rules: Rules) -> None:
    contract = contract_from_dict(fixture_json("contract_cp_x.json"), rules)
    text = render_module(contract, rules)
    assert text.startswith("# CP-X — Example Producer\n")
    assert GENERATED in text
    assert "| Sources: issuer | the filings |" in text
    assert "| Run Brief: issuer, as_of_date | entity and period anchor |" in text
    assert "1. Read the filings.\n2. Fill every table from them." in text
    assert "<!-- table: cpx.facts -->\n| fact* | value* | note |" in text
    assert "`credit_score` takes exactly one of: 1 - Strong; 2 - Good" in text
    assert "read by CP-Y." in text
    assert "<!-- table: citations -->\n| id | source | locator | excerpt |" in text
    assert "Each citation id appears on exactly one row." in text
    assert "- No investment opinion." in text
    assert "rbot.py validate handoffs/CP-X.md --module CP-X" in text
    for placeholder in rules.placeholders:
        assert placeholder in text


def test_handoff_inputs_render_with_their_requirement(rules: Rules) -> None:
    data = fixture_json("contract_cp_y.json")
    data["inputs"].append({"handoff": "CP-Z", "required": False, "why": "context"})
    text = render_module(contract_from_dict(data, rules), rules)
    assert "| Handoff `CP-X` (required) | the facts |" in text
    assert "| Handoff `CP-Z` (optional) | context |" in text
    assert "## Prohibited" not in text


def test_rendering_is_deterministic(rules: Rules) -> None:
    contract = contract_from_dict(fixture_json("contract_cp_x.json"), rules)
    assert render_module(contract, rules) == render_module(contract, rules)
