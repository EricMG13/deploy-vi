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


def _cp_x_text(rules: Rules) -> str:
    return render_module(contract_from_dict(fixture_json("contract_cp_x.json"), rules), rules)


def test_a_scale_value_is_allowed_even_when_it_reads_like_a_placeholder(rules: Rules) -> None:
    data = fixture_json("contract_cp_x.json")
    data["tables"][1]["columns"][0] = {"name": "rec", "critical": True, "scale": "recommendation"}
    text = render_module(contract_from_dict(data, rules), rules)
    assert (
        "A listed scale value is always allowed, even one that reads like a placeholder "
        "(e.g. `N/A`)." in text
    )
    assert "`rec` takes exactly one of: 1 - Strong OW" in text


def test_the_gap_convention_is_not_listed_as_a_checked_rule(rules: Rules) -> None:
    text = _cp_x_text(rules)
    checked, _, rest = text.partition("## Rules the checker enforces")[2].partition(
        "## Conventions (not checked)"
    )
    assert rest.startswith("\n")
    gap = (
        f"Write `{rules.gap_marker}` for a missing non-critical value "
        "and explain it under `## Gaps`."
    )
    assert gap not in checked
    assert gap in rest.split("## Prohibited")[0]
    assert "## Conventions (not checked)" in text


def test_every_citation_cell_must_be_filled(rules: Rules) -> None:
    assert "Every cell of a citation row is filled." in _cp_x_text(rules)


def test_front_matter_rule_names_non_empty_values_and_the_module_id(rules: Rules) -> None:
    text = _cp_x_text(rules)
    assert "one non-empty `key: value` per line" in text
    assert "`module_id` is `CP-X`" in text


def test_tags_are_one_per_table_directly_above_it(rules: Rules) -> None:
    assert (
        "Tag each table exactly once, with its `<!-- table: <id> -->` line "
        "directly above the table." in _cp_x_text(rules)
    )


def test_scale_bullets_are_separated_from_the_table(rules: Rules) -> None:
    assert "|---|---|\n\n- `credit_score` takes exactly one of" in _cp_x_text(rules)
