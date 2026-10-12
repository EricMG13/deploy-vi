"""The Model on the local issuer corpus (interfaces spec §12.5, Plan 03).

`test_model_on_caos_fixture` runs the ported Model over the caos Example
Gaming Co. registers through `rbot model` and checks the house view the
caos figures give. `test_cp1_czr_fixture_is_anchored_in_the_corpus` checks
that every figure the hand-written CZR CP-1 Handoff reports is on the line
its citation names in the hash-checked corpus file (pack `czr-2026q2-primary`,
through the `corpus_pack` fixture, so RBOT_REQUIRE_CORPUS decides fail or
skip), and `test_model_from_cp1_handoff_fixture` runs `rbot model` on it.

CZR's LTM to 30 June 2026 is FY2025 + H1 2026 - H1 2025: revenue 11,486 +
5,863 - 5,701 = 11,648; EBITDA (operating income plus D&A) 3,275 + 1,715 -
1,735 = 3,255; add-backs impairment 182 (FY only), transaction costs 72 + 45
- 54 = 63 and stock-based compensation 95 + 47 - 50 = 92, so adjusted (SSIM,
all realized) EBITDA 3,592, as CZR states (3,624 + 1,807 - 1,839); cash
interest paid for debt 813 + 368 - 405 = 776; total debt 11,705 and cash 965
at 30 June 2026, net debt 10,740. No PF rows: the snapshot column is the LTM.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, run_brief, run_folder

from rbotlib.cli import main
from rbotlib.handoff import Table, parse
from rbotlib.model.snapshot import display

pytestmark = pytest.mark.corpus
FIXTURES = Path(__file__).parent / "fixtures"
CZR = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
CHECKED = {"VERIFIED"}
PACK = "czr-2026q2-primary"


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def _shown(value: str) -> str:
    """A register figure as the filings print it: thousands separated, unsigned."""
    return f"{abs(Decimal(value)):,f}"


def _model(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "model.json").read_text(encoding="utf-8"))
    return data


def test_model_on_caos_fixture(tmp_path: Path) -> None:
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief())
    assert main(["model", "--run", str(run)]) == 0
    house = _model(run)["house"]
    assert {k: house[k]["value"] for k in ("structuring_ebitda", "ssim_ebitda", "pf_interest")} == {
        "structuring_ebitda": "4134",
        "ssim_ebitda": "4094",
        "pf_interest": "904",
    }
    assert _model(run)["reconciliation_faults"] == []


def test_cp1_czr_fixture_is_anchored_in_the_corpus(corpus_pack: Callable[[str], Path]) -> None:
    folder = corpus_pack(PACK)
    handoff = parse(CZR)
    citations = {row["id"]: row for row in _rows(handoff.tables["citations"])}
    texts = {
        c["source"]: (folder / c["source"]).read_text(encoding="utf-8") for c in citations.values()
    }
    for c in citations.values():
        assert c["excerpt"] in texts[c["source"]], c["id"]
    figures = [
        (r["source_id"], r["value"])
        for r in _rows(handoff.tables["cp1.model_account_register"])
        if r["calculation_status"] in CHECKED
    ]
    figures += [
        (r["source_id"], r["value"]) for r in _rows(handoff.tables["cp1.adjusted_ebitda_bridge"])
    ]
    figures += [
        (r["source_id"], r["carrying_value"])
        for r in _rows(handoff.tables["cp1.debt_facility_register"])
    ]
    assert len(figures) == 51
    for marker, value in figures:
        cited = citations[marker.strip("[]")]
        lines = texts[cited["source"]].splitlines()
        assert any(cited["excerpt"] in line and _shown(value) in line for line in lines), (
            marker,
            value,
        )


def test_model_from_cp1_handoff_fixture(tmp_path: Path, corpus_pack: Callable[[str], Path]) -> None:
    corpus_pack(PACK)  # the fixture's figures stand on the corpus
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, CZR, brief)
    assert main(["model", "--run", str(run)]) == 0
    data = _model(run)
    assert data["snapshot_columns"]["LTM"] == "LTM:LTM_Q2_2026"
    lines = {line["line_id"]: line for line in data["lines"]}
    ltm = {
        line_id: {c["column_id"]: c["value"] for c in lines[line_id]["cells"]} for line_id in lines
    }
    assert ltm["revenue"]["LTM:LTM_Q2_2026"] == "11648"
    assert ltm["ebitda"]["LTM:LTM_Q2_2026"] == "3255"
    assert ltm["adjusted_ebitda"]["LTM:LTM_Q2_2026"] == "3592"
    assert ltm["total_debt"]["LTM:LTM_Q2_2026"] == "11705"
    assert ltm["net_debt"]["LTM:LTM_Q2_2026"] == "10740"
    house = data["house"]
    assert house["ssim_ebitda"]["value"] == house["structuring_ebitda"]["value"] == "3592"
    assert house["pf_interest"]["value"] == "776"
    assert display(Decimal(house["pf_interest_cover"]["value"]), "MULTIPLE") == "4.63"
    assert display(Decimal(house["ssim_multiple"]["value"]), "MULTIPLE") == "3.26"
    assert house["ev"]["value"] == "28736.0" and house["ev"]["basis"] == "ssim_multiple"
    totals = {r["line"]: r for r in data["capital_structure"]["totals"]}
    assert totals["Senior secured debt"]["amount"] == "9385"
    assert totals["Unsecured debt"]["amount"] == "2320"  # every position that is not senior secured
    assert totals["Equity"]["amount"] == "17996.0"
    wall = [(r["fiscal_year"], r["facility_id"], r["amount"]) for r in data["maturity_wall"]]
    assert wall[:2] == [("2028", "cei_rcf", "120"), ("2028", "cei_tla", "618")]
    assert wall[-1] == ("2037", "sid_bonds", "38")
    codes = set(data["limitations"])
    assert {"PF_LTM_EQUALS_LTM", "CP1D_NOT_READ", "NO_PROJECTIONS", "MATURITY_NOT_STATED"} <= codes
    assert data["reconciliation_faults"] == []
