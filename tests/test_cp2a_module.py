"""Downside relationship, source and method witnesses; no invented numerical stress."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from test_cp1c_module import permission_message
from test_modules import _blocked, contract, fixture

from rbotlib.catalog import _order, load_catalog, load_contracts
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check


def test_restricted_and_positive_paths_keep_unknown_axes(rules: Rules) -> None:
    text = fixture("CP-2A")
    assert check(text, contract("CP-2A", rules), rules) == (0, [])
    assert check(
        text.replace("qa_status: Restricted", "qa_status: Pass"), contract("CP-2A", rules), rules
    ) == (0, [])
    h = parse(text)
    assert not h.tables["cp2a.sensitivities"].rows
    assert "Unknown | Unknown" in text and "closing timing unavailable" in text
    assert "Quantitative threshold not available" in text


@pytest.mark.parametrize("table", ["cp2a.downside_paths", "cp2a.triggers"])
@pytest.mark.parametrize("status", ["Restricted", "Blocked"])
def test_duplicate_ids_refuse_even_in_blocked(table: str, status: str, rules: Rules) -> None:
    text = fixture("CP-2A").replace("qa_status: Restricted", f"qa_status: {status}")
    row = "| " + " | ".join(parse(text).tables[table].rows[0]) + " |"
    # Case/space aliases are the same identity, not a fresh path/trigger.
    text = text.replace(row, row + "\n" + row.replace("CP-2A-", "cp-2a-", 1))
    code, found = check(text, contract("CP-2A", rules), rules)
    assert code == 2 and any(f.code == "duplicate_row_key" for f in found)


def test_unknown_link_is_malformed_and_gap_link_remains_blocked(rules: Rules) -> None:
    text = fixture("CP-2A").replace("| CP-2A-DP-001 | Reassess", "| missing-path | Reassess")
    code, found = check(text, contract("CP-2A", rules), rules)
    assert code == 2 and any(f.code == "unknown_linked_path" for f in found)
    blocked = _blocked(fixture("CP-2A"), contract("CP-2A", rules))
    assert check(blocked, contract("CP-2A", rules), rules) == (3, [])
    head, tail = blocked.split("<!-- table: cp2a.triggers -->", 1)
    malformed = (
        head
        + "<!-- table: cp2a.triggers -->"
        + tail.replace(
            "| — | — | — | — | — | — | — |", "| — | — | — | — | unknown-path | — | — |", 1
        )
    )
    assert check(malformed, contract("CP-2A", rules), rules)[0] == 2


@pytest.mark.parametrize("change", ["column", "row", "tag", "critical"])
def test_structural_critical_gates_remain_strict(change: str, rules: Rules) -> None:
    text = fixture("CP-2A")
    if change == "column":
        text = text.replace("| linked_path |", "| wrong_column |")
    elif change == "row":
        text = text.replace("| CP-2A-DP-001 | Reassess", "| CP-2A-DP-001 | extra | Reassess")
    elif change == "tag":
        text = text.replace("<!-- table: cp2a.downside_paths -->", "<!-- table: missing -->")
    else:
        text = text.replace("| CP-2A-DP-001 | Reassess", "| — | Reassess")
    assert check(text, contract("CP-2A", rules), rules)[0] == 2


def test_links_follow_same_normalisation_as_identities(rules: Rules) -> None:
    text = fixture("CP-2A").replace("| CP-2A-DP-001 | Reassess", "| cp-2a-dp-001 | Reassess")
    assert check(text, contract("CP-2A", rules), rules) == (0, [])


@pytest.mark.corpus
def test_current_source_anchoring_is_required(
    prepared_run: Callable[[str], Path], rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    text = fixture("CP-2A")
    assert check(text, contract("CP-2A", rules), rules, run) == (0, [])
    text = text.replace(
        "lower city-wide leisure customer visitation", "fabricated source stress witness"
    )
    code, found = check(text, contract("CP-2A", rules), rules, run)
    assert code == 2 and any(f.code == "citation_unanchored" for f in found)
    assert check(fixture("CP-2A"), contract("CP-2A", rules), rules, run / "absent")[0] == 1


def test_catalog_orders_real_producers_and_quick_excludes_downside(rules: Rules) -> None:
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    full = pathway.depths["full"]
    assert full[full.index("CP-2") + 1] == "CP-2A"
    assert "CP-2A" not in pathway.depths["quick"]
    contracts = load_contracts(RBOT_ROOT, rules, [])
    assert _order(pathway, full, contracts, rules.host_producers) == []
    bad = tuple(s for s in full if s != "CP-2A")
    bad = (*bad[:2], "CP-2A", *bad[2:])
    assert any(
        "CP-2A runs before its input CP-2" in p
        for p in _order(pathway, bad, contracts, rules.host_producers)
    )


def test_dispatch_has_no_calculator_or_fetch_grant(tmp_path: Path, rules: Rules) -> None:
    message = permission_message(tmp_path, "CP-2A", rules)
    assert message["Allowed calculator"] is None
    assert message["May write only"] == [str(tmp_path / "handoffs/CP-2A.md")]


def test_retained_method_covers_source_steps_and_absorbed_events() -> None:
    prompt = (RBOT_ROOT / "modules/CP-2A/MODULE.md").read_text()
    for retained in (
        "all 12 credit-sensitive dimensions",
        "eight driver groups",
        "11 analytical pathway labels",
        "First-Break Discipline",
        "Cash-Flow Conversion Discipline",
        "never recompute them",
        "Unknown",
        "Undated events belong in Gaps",
        "never infer a closing date",
        "High/High is Critical",
        "Leading or Lagging",
        "exactly one existing linked_path",
        "Critical/High events",
        "what would make it win",
        "both citations",
        "no fetching authority",
        "No missing-to-zero",
        "source-supported observation frequency",
    ):
        assert retained in prompt
