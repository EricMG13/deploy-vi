"""`research_policy` (Plan 10, ruling R16): the CP-DR table rules, with and without a run."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import FIXTURES
from rbotlib.contract import load_contract
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import EXIT_MALFORMED, EXIT_VALID, check

HANDOFF = (FIXTURES / "handoffs" / "CP-DR.md").read_text(encoding="utf-8")


def codes(text: str, rules: Rules, run: Path | None = None) -> tuple[int, list[str]]:
    contract = load_contract(RBOT_ROOT / "modules" / "CP-DR" / "contract.json", rules)
    code, findings = check(text, contract, rules, run)
    return code, [f"{f.code}: {f.message}" for f in findings if f.code == "research_policy"]


def test_the_committed_fixture_passes_the_policy(rules: Rules) -> None:
    assert codes(HANDOFF, rules) == (EXIT_VALID, [])


def swap(old: str, new: str) -> str:
    assert old in HANDOFF
    return HANDOFF.replace(old, new, 1)


@pytest.mark.parametrize(
    "text,message",
    [
        (swap("| Q3 | Not answered:", "| Q9 | Not answered:"), "Q3"),  # no answer row for Q3
        (swap("| E1; E2; E3 |", "| none |"), "Q1"),  # Partly answered with no evidence
        (swap("| E4; E5 |", "| E4; E9 |"), "E9"),  # an id with no evidence row
        (
            swap("| Pack | 2026-06-30 | Caesars Q2", "| Fetched | 2026-06-30 | Caesars Q2"),
            "Fetched",
        ),
    ],
)
def test_each_rule_is_a_finding(rules: Rules, text: str, message: str) -> None:
    code, found = codes(text, rules)
    assert code == EXIT_MALFORMED
    assert found and all(f.startswith("research_policy") for f in found) and message in found[0]


def test_a_pack_row_citing_fetched_and_a_fetched_row_citing_the_pack(rules: Rules) -> None:
    text = swap(
        "| CZR_Q2_2026_Earnings_Release.txt | Adjusted", "| fetched/01-pub.example.md | Adjusted"
    )
    code, found = codes(text, rules)
    assert code == EXIT_MALFORMED and "E1" in found[0] and "Pack" in found[0]


def test_an_unapproved_question_id_needs_a_run_brief(rules: Rules, tmp_path: Path) -> None:
    (tmp_path / "prepared").mkdir()
    (tmp_path / "prepared" / "index.json").write_text('{"files": []}', encoding="utf-8")
    brief = (
        "---\nrun: x\n---\n<!-- table: brief.research_questions -->\n"
        "| question_id | question | consumer_module | approved |\n| --- | --- | --- | --- |\n"
        "| Q1 | One? | CP-2 | Yes |\n| Q2 | Two? | CP-2 | Yes |\n| Q3 | Three? | CP-6 | No |\n"
    )
    (tmp_path / "run-brief.md").write_text(brief, encoding="utf-8")
    code, found = codes(HANDOFF, rules, tmp_path)
    assert code == EXIT_MALFORMED and len(found) == 1 and "Q3" in found[0]
    assert "not an approved" in found[0]
