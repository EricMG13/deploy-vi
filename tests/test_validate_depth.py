"""The depth rules of the validator: `screen_policy` (§2.20 LITE) and `basis_depth` (R4a)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_state import seeded

from conftest import FIXTURES
from rbotlib.contract import Contract, load_contract
from rbotlib.rules import Rules
from rbotlib.validate import EXIT_MALFORMED, EXIT_VALID, check

MODULES = Path(__file__).resolve().parents[1] / "rbot" / "modules"
HANDOFFS = FIXTURES / "handoffs"
TOPIC_ROW = "| SOURCE_BASIS | Financial change | Source, period and perimeter basis | Medium |"


def _contract(module_id: str, rules: Rules) -> Contract:
    return load_contract(MODULES / module_id / "contract.json", rules)


def _text(module_id: str) -> str:
    return (HANDOFFS / f"{module_id}.md").read_text(encoding="utf-8")


def _codes(text: str, module_id: str, rules: Rules, run: Path | None = None) -> list[str]:
    return [f.code for f in check(text, _contract(module_id, rules), rules, run)[1]]


def _run(tmp_path: Path, depth: str) -> Path:
    run, data = seeded(tmp_path)
    data["depth"] = depth
    (run / "run-state.json").write_text(json.dumps(data), encoding="utf-8")
    (run / "prepared").mkdir()  # no sources: citation findings appear, the depth rules still run
    (run / "prepared" / "index.json").write_text('{"files": []}', encoding="utf-8")
    return run


def _row(text: str, topic: str, **cells: str) -> str:
    """The fixture with one screen_topics row's named cells replaced."""
    names = ["topic_id", "family", "topic", "materiality", "evidence_status", "disposition"]
    out, done = [], False
    for line in text.splitlines():
        parts = line.split(" | ")
        if line.startswith(f"| {topic} |") and not done:  # the triggers table reuses topic ids
            done = True
            for key, value in cells.items():
                parts[names.index(key)] = value
            line = " | ".join(parts)
        out.append(line)
    return "\n".join(out) + "\n"


def test_the_fixture_is_clean_without_a_run(rules: Rules) -> None:
    assert check(_text("CP-L10"), _contract("CP-L10", rules), rules)[0] == EXIT_VALID


@pytest.mark.parametrize("evidence", ["Missing", "Conflicted"])
def test_a_high_topic_without_sound_evidence_must_be_gap_only(rules: Rules, evidence: str) -> None:
    text = _row(
        _text("CP-L10"),
        "EARNINGS_MARGIN_CHANGE",
        evidence_status=evidence,
        disposition="Summarize",
    )
    exit_code, findings = check(text, _contract("CP-L10", rules), rules)
    assert exit_code == EXIT_MALFORMED
    assert [f.code for f in findings] == ["screen_policy"]
    assert "EARNINGS_MARGIN_CHANGE" in findings[0].message


def test_a_high_topic_with_missing_evidence_may_be_gap_only(rules: Rules) -> None:
    text = _row(
        _text("CP-L10"), "EARNINGS_MARGIN_CHANGE", evidence_status="Missing", disposition="Gap only"
    )
    assert _codes(text, "CP-L10", rules) == []


def test_immaterial_needs_sufficient_evidence(rules: Rules) -> None:
    text = _row(_text("CP-L10"), "KPI_COMPARABILITY", disposition="Immaterial")
    assert _codes(text, "CP-L10", rules) == ["screen_policy"]


def test_a_family_without_a_row_is_named(rules: Rules) -> None:
    text = _text("CP-L10")
    kept = [ln for ln in text.splitlines() if not ln.startswith("| ") or "| Distress |" not in ln]
    assert len(kept) < len(text.splitlines())
    found = check("\n".join(kept) + "\n", _contract("CP-L10", rules), rules)[1]
    assert any(f.code == "screen_policy" and "'Distress'" in f.message for f in found)


@pytest.mark.parametrize(
    ("module_id", "depth", "wrong"),
    [("CP-L10", "full", "Screening"), ("CP-2", "quick", "Full")],
)
def test_basis_must_match_the_run_depth(
    tmp_path: Path, rules: Rules, module_id: str, depth: str, wrong: str
) -> None:
    run, right = _run(tmp_path, depth), {"Full": "Screening", "Screening": "Full"}[wrong]
    text = _text(module_id)
    assert "basis_depth" in _codes(text, module_id, rules, run)
    fixed = text.replace(f"| {wrong} | [C", f"| {right} | [C")
    assert fixed != text
    assert "basis_depth" not in _codes(fixed, module_id, rules, run)


def test_basis_depth_covers_the_cp6_recommendation(tmp_path: Path, rules: Rules) -> None:
    run = _run(tmp_path, "quick")
    findings = check(_text("CP-6"), _contract("CP-6", rules), rules, run)[1]
    messages = [f.message for f in findings if f.code == "basis_depth"]
    assert messages
    assert "snapshot.recommendation" in messages[0]


def test_basis_depth_is_skipped_without_a_run_or_an_approved_depth(
    tmp_path: Path, rules: Rules
) -> None:
    assert _codes(_text("CP-2"), "CP-2", rules) == []
    bare = tmp_path / "pack" / "rbot-runs" / "r1"
    bare.mkdir(parents=True)
    assert "basis_depth" not in _codes(_text("CP-L10"), "CP-L10", rules, bare)
    unapproved, _ = seeded(tmp_path / "u", approved=False)
    assert "basis_depth" not in _codes(_text("CP-2"), "CP-2", rules, unapproved)


def test_an_unreadable_state_file_is_not_swallowed(tmp_path: Path, rules: Rules) -> None:
    run = _run(tmp_path, "full")
    (run / "run-state.json").write_text("{", encoding="utf-8")
    with pytest.raises(ValueError):
        check(_text("CP-2"), _contract("CP-2", rules), rules, run)


def test_a_blocked_screen_may_leave_a_family_without_a_row(rules: Rules) -> None:
    text = _text("CP-L10").replace("qa_status: Restricted", "qa_status: Blocked", 1)
    kept = [ln for ln in text.splitlines() if "| Distress |" not in ln]
    assert check("\n".join(kept) + "\n", _contract("CP-L10", rules), rules)[1] == []
