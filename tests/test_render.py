from __future__ import annotations

import re

from conftest import fixture_json
from rbotlib.contract import contract_from_dict
from rbotlib.render import GENERATED, render_module
from rbotlib.rules import Rules
from rbotlib.validate import check


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
    assert "- Write a literal pipe inside any cell, excerpts included, as `\\|`." in text
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


def test_the_inputs_key_lists_handoff_ids_or_none(rules: Rules) -> None:
    assert "- `inputs: <Handoff ids comma-separated, or none>`." in _cp_x_text(rules)


def test_the_rules_block_says_not_to_indent_a_table(rules: Rules) -> None:
    assert "- Do not indent a table or put it in a code block." in _cp_x_text(rules)


def test_tags_are_one_per_table_directly_above_it(rules: Rules) -> None:
    assert (
        "Tag each table exactly once, with its `<!-- table: <id> -->` line "
        "directly above the table." in _cp_x_text(rules)
    )


def test_scale_bullets_are_separated_from_the_table(rules: Rules) -> None:
    assert "|---|---|\n\n- `credit_score` takes exactly one of" in _cp_x_text(rules)


def test_the_rules_say_the_asterisk_is_not_part_of_the_column_name(rules: Rules) -> None:
    contract = contract_from_dict(fixture_json("contract_cp_x.json"), rules)
    assert (
        "- Column names exactly as printed, without the `*` that marks a critical column."
        in render_module(contract, rules)
    )


def test_the_printed_headers_pass_the_checker_once_the_asterisk_is_stripped(
    rules: Rules, handoff_text: str
) -> None:
    """Seam: the generator's header rows and the validator's column check must agree."""
    contract = contract_from_dict(fixture_json("contract_cp_x.json"), rules)
    printed = re.findall(r"<!-- table: (\S+) -->\n\| (.*) \|\n", render_module(contract, rules))
    headers = {tid: [c.strip().removesuffix("*") for c in row.split("|")] for tid, row in printed}
    assert {"cpx.facts", "snapshot.view"} <= headers.keys()
    scales = {c.name: c.scale for t in contract.tables for c in t.columns if c.scale}
    text = handoff_text
    for table in contract.tables:
        cols = headers[table.id]
        row = [rules.scales[scales[c]][0] if c in scales else "x" for c in cols]
        block = f"<!-- table: {table.id} -->\n| " + " | ".join(cols) + " |\n"
        block += "|" + "---|" * len(cols) + "\n| " + " | ".join(row) + " |\n"
        old = re.search(rf"<!-- table: {re.escape(table.id)} -->\n+(?:\|.*\n?)+", text)
        assert old
        text = text[: old.start()] + block + text[old.end() :]
    _, findings = check(text, contract, rules)
    assert [f for f in findings if f.code == "column_missing"] == []


def test_document_types_print_beside_their_source_class(rules: Rules) -> None:
    data = fixture_json("contract_cp_x.json")
    data["inputs"][0]["document_types"] = ["Credit agreement", "Indenture"]
    text = render_module(contract_from_dict(data, rules), rules)
    assert "| Sources: issuer (Credit agreement, Indenture) | the filings |" in text
