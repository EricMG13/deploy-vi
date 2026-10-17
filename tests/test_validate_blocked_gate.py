"""The CP-3 Blocked gate (MODULE.md step 12): Blocked only with no market level and no talk."""

from __future__ import annotations

import re
from pathlib import Path

from test_modules import _blocked

from conftest import FIXTURES
from rbotlib.contract import Contract, load_contract
from rbotlib.rules import Rules
from rbotlib.validate import EXIT_BLOCKED, EXIT_MALFORMED, check

MODULES = Path(__file__).resolve().parents[1] / "rbot" / "modules"
FIXTURE = (FIXTURES / "handoffs" / "CP-3.md").read_text(encoding="utf-8")


def _contract(rules: Rules) -> Contract:
    return load_contract(MODULES / "CP-3" / "contract.json", rules)


def _status(text: str, status: str) -> str:
    return re.sub(r"qa_status: \w+", f"qa_status: {status}", text, count=1)


def _without_rows(text: str, table_id: str) -> str:
    """The text with the data rows of one table removed (its header stays)."""
    out, in_table, seen = [], False, 0
    for line in text.splitlines():
        if line.startswith("<!-- table:"):
            in_table, seen = line == f"<!-- table: {table_id} -->", 0
        elif in_table and line.startswith("|"):
            seen += 1
            if seen > 2:
                continue
        out.append(line)
    return "\n".join(out) + "\n"


def _codes(text: str, rules: Rules) -> tuple[int, list[str]]:
    exit_code, found = check(text, _contract(rules), rules)
    return exit_code, [f.code for f in found]


def test_blocked_with_market_levels_is_malformed(rules: Rules) -> None:
    exit_code, codes = _codes(_status(FIXTURE, "Blocked"), rules)
    assert "blocked_gate" in codes
    assert exit_code == EXIT_MALFORMED


def test_blocked_with_talk_only_is_malformed(rules: Rules) -> None:
    text = _without_rows(_status(FIXTURE, "Blocked"), "snapshot.instrument_levels")
    exit_code, codes = _codes(text, rules)
    assert "blocked_gate" in codes
    assert exit_code == EXIT_MALFORMED


def test_blocked_message_names_the_facility_and_the_rule(rules: Rules) -> None:
    _, found = check(_status(FIXTURE, "Blocked"), _contract(rules), rules)
    message = next(f.message for f in found if f.code == "blocked_gate")
    assert "CEI-TLB" in message
    assert "Restricted" in message


def test_a_genuinely_blocked_handoff_still_exits_3(rules: Rules) -> None:
    text = _blocked(FIXTURE, _contract(rules))
    exit_code, codes = _codes(text, rules)
    assert "blocked_gate" not in codes
    assert exit_code == EXIT_BLOCKED


def test_restricted_with_levels_has_no_blocked_gate(rules: Rules) -> None:
    _, codes = _codes(_status(FIXTURE, "Restricted"), rules)
    assert "blocked_gate" not in codes
