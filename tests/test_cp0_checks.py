from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from builders import make_pdf, prepared_pack
from conftest import FIXTURES
from cp0_fixture import cp0_handoff
from rbotlib.contract import Contract, load_contract
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import EXIT_MALFORMED, check

CP0 = (FIXTURES / "handoffs" / "CP-0.md").read_text(encoding="utf-8")
QUESTION = "| Q1 | How is Las Vegas Strip visitation trending into 2027? |"
CLASSES = {
    "acme_10k.txt": ("issuer", "Annual report", "Acme Holdings, Inc.", "Yes"),
    "acme_ca.txt": ("issuer", "Credit agreement", "Acme Holdings, Inc.", "Yes"),
    "scan.pdf": ("issuer", "Rating report", "Not identified", "Yes"),
}


@pytest.fixture
def cp0(rules: Rules) -> Contract:
    return load_contract(RBOT_ROOT / "modules" / "CP-0" / "contract.json", rules)


def _codes(text: str, cp0: Contract, rules: Rules, run: Path | None = None) -> list[str]:
    code, findings = check(text, cp0, rules, run)
    assert code == (EXIT_MALFORMED if findings else 0)
    return [f"{f.code}: {f.message}" for f in findings]


# Every constraint CP-0's MODULE.md states for the pre-fill and the questions, broken once.
PREFILL = [
    (
        "| debt_type | NEW-1 | 1L Term Loan |",
        "| debt_type | Tranche A | 1L Term Loan |",
        "prefill_invalid: cp0.run_brief_prefill: tranche id 'Tranche A' is not NEW-<n>",
    ),
    (
        "| debt_type | NEW-1 | 1L Term Loan |",
        "| debt_type | NEW-1 | Senior secured notes |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 debt_type: debt_type must be one of",
    ),
    (
        "| use_of_proceeds | NEW-1 | Acquisition |",
        "| use_of_proceeds | NEW-1 | M&A |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 use_of_proceeds: use_of_proceeds must be",
    ),
    (
        "| size | NEW-1 | 3000 |",
        "| size | NEW-1 | 1,000 million |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 size: size must be a plain decimal",
    ),
    (
        "| currency | NEW-1 | USD |",
        "| currency | NEW-1 | US dollars |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 currency: currency must be a three-letter",
    ),
    (
        "| unit | NEW-1 | MILLIONS |",
        "| unit | NEW-1 | USD m |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 unit: unit must be one of",
    ),
    (
        "| talk_stage | NEW-1 | Initial talk |",
        "| talk_stage | NEW-1 | IPT |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 talk_stage: talk_stage must be one of",
    ),
    (
        "| maturity_date | NEW-1 | 2033-12-15 |",
        "| maturity_date | NEW-1 | Dec 2033 |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 maturity_date: maturity_date must be",
    ),
    (
        "| commitment_date | NEW-1 | 2026-10-08 |",
        "| commitment_date | NEW-1 | 8 Oct |",
        "prefill_invalid: cp0.run_brief_prefill NEW-1 commitment_date: commitment_date must be",
    ),
    (
        "| as_of_date | | 2026-10-02 |",
        "| as_of_date | | 2 October 2026 |",
        "prefill_invalid: cp0.run_brief_prefill as_of_date: as_of_date must be YYYY-MM-DD",
    ),
    (
        "| primary | | Yes |",
        "| primary | | Probably |",
        "prefill_invalid: cp0.run_brief_prefill primary: primary must be one of",
    ),
    (
        "| issuer_id | | CZR |",
        "| ticker | | CZR |",
        "prefill_invalid: cp0.run_brief_prefill: unknown field 'ticker'",
    ),
    (
        "| oid | NEW-1 | 99.0\u201399.5 |",
        "| margin | NEW-1 | 99.0\u201399.5 |",
        "prefill_invalid: cp0.run_brief_prefill: 'margin' is not a tranche field",
    ),
    (
        "| issuer | | Caesars Entertainment, Inc. | Sourced | [C1] |",
        "| issuer | | Caesars Entertainment, Inc. | Sourced | |",
        "prefill_status: cp0.run_brief_prefill issuer: Sourced without a citation",
    ),
    (
        "| objective | | — | Gap | |",
        "| objective | | Review | Gap | |",
        "prefill_status: cp0.run_brief_prefill objective: Gap with a value",
    ),
    (
        "| analyst | | — | Gap | |",
        "| analyst | | A. Analyst | Analyst-asserted | [C2] |",
        "prefill_status: cp0.run_brief_prefill analyst: Analyst-asserted with a citation",
    ),
    (
        f"{QUESTION} Las Vegas drives the largest segment's Adjusted EBITDA | CP-2 |",
        f"{QUESTION} Las Vegas drives the largest segment's Adjusted EBITDA | CP-4 |",
        "research_questions: Q1: consumer_module 'CP-4' is not CP-2, CP-3 or CP-6",
    ),
    (
        f"{QUESTION} Las Vegas drives the largest segment's Adjusted EBITDA | CP-2 |",
        f"{QUESTION} Las Vegas drives the largest segment's Adjusted EBITDA | CP-1A |",
        "research_questions: Q1: consumer_module 'CP-1A' is not CP-2, CP-3 or CP-6",
    ),
]


@pytest.mark.parametrize(("old", "new", "message"), PREFILL)
def test_every_prefill_rule_of_module_md_is_checked(
    cp0: Contract, rules: Rules, old: str, new: str, message: str
) -> None:
    assert old in CP0
    found = _codes(CP0.replace(old, new), cp0, rules)
    assert any(f.startswith(message) for f in found), found


def test_at_most_five_research_questions(cp0: Contract, rules: Rules) -> None:
    row = next(line for line in CP0.splitlines() if line.startswith("| Q1 |"))
    more = "\n".join(row.replace("Q1", f"Q{n}") for n in range(1, 7))
    found = _codes(CP0.replace(row, more), cp0, rules)
    assert "research_questions: 6 questions; MODULE.md allows at most 5" in found


def _acme(tmp_path: Path) -> Path:
    files: dict[str, str | bytes] = {
        "acme_10k.txt": "Acme Holdings, Inc. annual report 2025\n",
        "acme_ca.txt": "Acme Holdings, Inc. credit agreement\n",
        "scan.pdf": make_pdf([""]),
    }
    return prepared_pack(tmp_path, files)


def _inventory_row(text: str, name: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(f"| {name} |"))


def test_a_handoff_true_to_the_run_has_no_finding(
    tmp_path: Path, cp0: Contract, rules: Rules
) -> None:
    run = _acme(tmp_path)
    text = cp0_handoff(run, ("Acme Holdings, Inc.", "ACME"), "2026-10-02", CLASSES, primary=False)
    assert _codes(text, cp0, rules, run) == []
    assert "| scan.pdf | issuer | Rating report | Not identified | Yes | — | — | No |" in text


def _broken(tmp_path: Path, change: str, cp0: Contract, rules: Rules) -> str:
    run = _acme(tmp_path)
    text = cp0_handoff(run, ("Acme Holdings, Inc.", "ACME"), "2026-10-02", CLASSES, primary=False)
    row = _inventory_row(text, "acme_ca.txt")
    cells = row.split(" | ")
    if change == "missing":
        text = text.replace(row + "\n", "")
    elif change == "ghost":
        ghost = row.replace("acme_ca.txt", "ghost.pdf")
        text = text.replace(row, row + "\n" + ghost)
    elif change == "sha":
        text = text.replace(cells[10], "0" * 64)
    elif change == "pages":
        text = text.replace(row, row.replace(f" | {cells[9]} | ", " | 7 | "))
    elif change == "readable":
        scan = _inventory_row(text, "scan.pdf")
        text = text.replace(scan, scan.replace("| Yes | — | — | No |", "| Yes | — | — | Yes |"))
    elif change == "portfolio":
        port = "as_of_date |\n|---|---|---|---|---|---|\n"
        fake = "| fake | Fake CLO | CLO | ghost.pdf | ghost.pdf | 2026-10-02 |\n"
        text = text.replace(port, port + fake)
    elif change == "prior":
        head = "offered |\n|---|---|---|---|---|---|\n"
        old = "| acme_10k.txt | 2026-07-15 | 20260715-acme-eu | EARNINGS_UPDATE | full | Yes |\n"
        text = text.replace(head, head + old)
    return "\n".join(_codes(text, cp0, rules, run))


RUN_CHECKS = [
    (
        "missing",
        "inventory_mismatch: acme_ca.txt is in inventory.json but not in cp0.source_inventory",
    ),
    ("ghost", "inventory_mismatch: ghost.pdf is in cp0.source_inventory but not in inventory.json"),
    ("sha", "inventory_mismatch: acme_ca.txt: sha256 differs from prepared/index.json"),
    ("pages", "inventory_mismatch: acme_ca.txt: pages 7, prepared/index.json says 1"),
    ("readable", "inventory_mismatch: scan.pdf: readable Yes, but it is Image-Read only"),
    (
        "portfolio",
        "portfolio_mismatch: fake is in cp0.portfolios but rbot prepare found no such portfolio",
    ),
    ("prior", "prior_case_mismatch: acme_10k.txt is not flagged rbot_report in inventory.json"),
]


@pytest.mark.parametrize(("change", "message"), RUN_CHECKS)
def test_cp0_claims_the_run_contradicts_are_findings(
    tmp_path: Path, cp0: Contract, rules: Rules, change: str, message: str
) -> None:
    assert message in _broken(tmp_path, change, cp0, rules)


@pytest.mark.corpus
def test_the_fixture_is_true_to_the_primary_pack(
    prepared_run: Callable[[str], Path], cp0: Contract, rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    assert _codes(CP0, cp0, rules, run) == []
    index = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
    assert [p["portfolio_id"] for p in index["portfolios"]] == ["TEST_CLO_I"]
