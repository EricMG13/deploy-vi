from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from conftest import FIXTURES, fixture_json
from rbotlib import validate
from rbotlib.contract import Contract, contract_from_dict
from rbotlib.rules import Rules, load_rules
from rbotlib.validate import EXIT_BLOCKED, EXIT_IDENTITY, EXIT_MALFORMED, EXIT_VALID, check


@pytest.fixture
def contract(rules: Rules) -> Contract:
    return contract_from_dict(fixture_json("contract_cp_x.json"), rules)


def codes(text: str, contract: Contract, rules: Rules) -> tuple[int, set[str]]:
    exit_code, findings = check(text, contract, rules)
    return exit_code, {f.code for f in findings}


def test_the_example_handoff_is_valid(handoff_text: str, contract: Contract, rules: Rules) -> None:
    assert check(handoff_text, contract, rules) == (EXIT_VALID, [])


def test_blocked_status_exits_3(handoff_text: str, contract: Contract, rules: Rules) -> None:
    text = handoff_text.replace("qa_status: Pass", "qa_status: Blocked")
    assert codes(text, contract, rules) == (EXIT_BLOCKED, set())


def test_another_modules_handoff_exits_4(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    text = handoff_text.replace("module_id: CP-X", "module_id: CP-Y")
    assert codes(text, contract, rules) == (EXIT_IDENTITY, {"identity"})


@pytest.mark.parametrize(
    "case",
    [
        ("qa_status: Pass", "qa_status: Fine", "qa_status"),
        ("issuer_id: TEST\n", "", "front_matter_missing"),
        ("## Gaps", "## Holes", "sections"),
        ("| revenue | 100 | — |", "| revenue | TBD | — |", "critical_placeholder"),
        ("| revenue | 100 | — |", "| revenue | — | — |", "critical_placeholder"),
        ("| 3 - Fair | Stable |", "| Fair | Stable |", "off_scale"),
        ("| 3 - Fair | Stable |", "| 3 - Fair | Flat |", "off_scale"),
        ("| revenue | 100 | — |", "| revenue | 100 |", "row_shape"),
        (
            "| fact | value | note |\n|---|---|---|",
            "| fact | amount | note |\n|---|---|---|",
            "column_missing",
        ),
        ("| revenue | 100 | — |\n", "", "too_few_rows"),
        ("<!-- table: snapshot.view -->", "<!-- table: snapshot.other -->", "table_missing"),
        ("<!-- table: snapshot.view -->", "<!-- table: snapshot.other -->", "undeclared_table"),
        ("[C1]", "[C2]", "unresolved_citation"),
        ("[C1]", "", "unused_citation"),
        ("| C1 | TEST_10Q.txt | p.3 |", "| C1 | TEST_10Q.txt |  |", "citation_incomplete"),
        (
            "| id | source | locator | excerpt |",
            "| id | file | locator | excerpt |",
            "column_missing",
        ),
        ("<!-- table: citations -->", "<!-- table: cites -->", "table_missing"),
        ("## Gaps", "<!-- table: nothing -->\n\n## Gaps", "orphan_tag"),
    ],
)
def test_each_defect_is_named(
    handoff_text: str, contract: Contract, rules: Rules, case: tuple[str, str, str]
) -> None:
    old, new, code = case
    assert old in handoff_text
    exit_code, found = codes(handoff_text.replace(old, new, 1), contract, rules)
    assert exit_code == EXIT_MALFORMED
    assert code in found


def test_a_duplicated_table_is_named(handoff_text: str, contract: Contract, rules: Rules) -> None:
    block = (
        "<!-- table: snapshot.view -->\n"
        "| credit_score | direction |\n|---|---|\n| 3 - Fair | Stable |\n"
    )
    text = handoff_text.replace("## Gaps", block + "\n## Gaps")
    assert "duplicate_table" in codes(text, contract, rules)[1]


def test_a_non_critical_gap_marker_is_fine(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    text = handoff_text.replace("| 3 - Fair | Stable |", "| 3 - Fair | — |")
    assert check(text, contract, rules) == (EXIT_VALID, [])


def test_a_scale_value_that_reads_like_a_placeholder_is_valid(
    handoff_text: str, rules: Rules
) -> None:
    data = fixture_json("contract_cp_x.json")
    data["tables"][1]["columns"][0]["scale"] = "recommendation"
    contract = contract_from_dict(data, rules)
    text = handoff_text.replace("| 3 - Fair | Stable |", "| N/A | Stable |")
    assert check(text, contract, rules) == (EXIT_VALID, [])


def test_a_handoff_over_the_upstream_cap_is_too_large(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    padding = "x" * (validate.MAX_HANDOFF_BYTES - len(handoff_text.encode("utf-8")) + 1)
    text = handoff_text.replace("None.", "None. " + padding)
    assert codes(text, contract, rules) == (EXIT_MALFORMED, {"too_large"})
    at_cap = handoff_text.replace("None.", "None." + padding[:-2])
    assert check(at_cap, contract, rules) == (EXIT_VALID, [])


def test_text_without_front_matter_is_malformed(contract: Contract, rules: Rules) -> None:
    assert codes("# just prose", contract, rules) == (EXIT_MALFORMED, {"not_a_handoff"})


_RULES = load_rules()
_cell = st.text(
    alphabet=st.characters(categories=("L", "N"), include_characters=" .,%$()-"),
    min_size=1,
    max_size=30,
).filter(lambda s: not _RULES.is_placeholder(s))


_HANDOFF = (FIXTURES / "handoff_cp_x.md").read_text(encoding="utf-8")


@given(fact=_cell, value=_cell)
def test_any_real_critical_values_validate(fact: str, value: str) -> None:
    # Property: whatever non-placeholder text fills the critical cells, the
    # Handoff stays valid; only placeholders and structure are refused.
    contract = contract_from_dict(fixture_json("contract_cp_x.json"), _RULES)
    text = _HANDOFF.replace("| revenue | 100 |", f"| {fact} | {value} |")
    assert check(text, contract, _RULES) == (EXIT_VALID, [])


def test_a_repeated_citation_id_is_named(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    row = "| C1 | TEST_10Q.txt | p.3 | revenue was 100 |"
    text = handoff_text.replace(row, row + "\n| C1 | OTHER.txt | p.9 | other |")
    exit_code, found = codes(text, contract, rules)
    assert exit_code == EXIT_MALFORMED
    assert "duplicate_citation" in found


def test_a_citation_that_cites_itself_is_unused(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    text = handoff_text.replace("period [C1].", "period.").replace(
        "revenue was 100 |", "revenue was 100 [C1] |"
    )
    exit_code, found = codes(text, contract, rules)
    assert exit_code == EXIT_MALFORMED
    assert "unused_citation" in found


def test_a_marker_inside_another_table_still_counts(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    text = handoff_text.replace("period [C1].", "period.").replace(
        "| revenue | 100 | — |", "| revenue | 100 | see [C1] |"
    )
    assert check(text, contract, rules) == (EXIT_VALID, [])


def test_blocked_with_a_structural_defect_is_malformed(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    text = handoff_text.replace("qa_status: Pass", "qa_status: Blocked").replace(
        "<!-- table: snapshot.view -->", "<!-- table: snapshot.other -->"
    )
    assert codes(text, contract, rules)[0] == EXIT_MALFORMED


def test_identity_mismatch_wins_over_other_findings(
    handoff_text: str, contract: Contract, rules: Rules
) -> None:
    text = handoff_text.replace("module_id: CP-X", "module_id: CP-Y").replace("## Gaps", "## Holes")
    exit_code, found = codes(text, contract, rules)
    assert exit_code == EXIT_IDENTITY
    assert {"identity", "sections"} <= found
