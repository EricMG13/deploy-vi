"""CP-1's fixture feeds the Model, and every figure it reports is on its cited line.

`rbot model` on the fixture (the Run Brief from CP-0's fixture; no SSIM EV multiple) gives, on
the PF-LTM to June 30, 2026: total debt 11,705 + 3,000 (NEW-1) - 120 (the revolver repaid) =
14,585; SSIM EBITDA 3,624 + 1,807 - 1,839 = 3,592; PF interest 776 + 213 = 989 and its cover
3,592 / 989 = 3.63x; the SSIM Multiple 14,585 / 3,592 = 4.06x; no EV (no listed equity value).
With CP-1D, adjusted debt adds the 13,157 of financing obligations: 27,742 and 7.72x. The
arranger's 150 of run-rate synergies is registered on the LTM period itself; the Model builds
the LTM from FY2025 and the half-years, so it reaches the Model as the LTM cell's `stated`
figure only (CP-5 finding F-1).
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.model.snapshot import display

HANDOFFS = FIXTURES / "handoffs"
CHECKED = {"VERIFIED"}


def _model(tmp_path: Path, *modules: str) -> dict[str, Any]:
    run = make_run(tmp_path / "pack", "20261011-czr-full-credit-assessment")
    (run / "handoffs").mkdir()
    shutil.copy(HANDOFFS / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    for module in modules:
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["model", "--run", str(run)]) == 0
    data: dict[str, Any] = json.loads((run / "model.json").read_text(encoding="utf-8"))
    return data


def test_the_cp1_fixture_feeds_the_model(tmp_path: Path) -> None:
    data = _model(tmp_path, "CP-1")
    assert data["snapshot_columns"]["LTM"] == "PF:LTM_Q2_2026"
    house = data["house"]
    values = {k: house[k]["value"] for k in ("ssim_ebitda", "pf_interest", "adjusted_debt")}
    assert values == {"ssim_ebitda": "3592", "pf_interest": "989", "adjusted_debt": "14585"}
    assert display(Decimal(house["pf_interest_cover"]["value"]), "MULTIPLE") == "3.63"
    assert display(Decimal(house["ssim_multiple"]["value"]), "MULTIPLE") == "4.06"
    assert (house["ev"]["value"], house["ev"]["reason"]) == (None, "NOT_SOURCED")
    lines = {line["line_id"]: line for line in data["lines"]}
    pf = {c["column_id"]: c for c in lines["addback:run_rate_synergies"]["cells"]}["PF:LTM_Q2_2026"]
    assert (pf["value"], pf["reason"], pf["stated"]) == (None, "NOT_SOURCED", "150")
    assert data["reconciliation_faults"] == []


def test_cp1d_adds_the_financing_obligations_to_adjusted_debt(tmp_path: Path) -> None:
    house = _model(tmp_path, "CP-1", "CP-1D")["house"]
    assert house["adjusted_debt"]["value"] == "27742"
    assert display(Decimal(house["adjusted_leverage"]["value"]), "MULTIPLE") == "7.72"


def test_downstream_fixtures_use_cp1s_figures() -> None:
    cp1 = parse((HANDOFFS / "CP-1.md").read_text(encoding="utf-8"))
    accounts = cp1.tables["cp1.model_account_register"]
    figure = {(r[0], r[1]): r[2] for r in accounts.rows}
    bridge = cp1.tables["cp1.adjusted_ebitda_bridge"]
    addbacks = {(r[0], r[5]): r[6] for r in bridge.rows}
    cp1b = parse((HANDOFFS / "CP-1B.md").read_text(encoding="utf-8"))
    table = cp1b.tables["cp1b.period_comparison"]
    for row in (dict(zip(table.columns, r, strict=True)) for r in table.rows):
        assert row["current_value"] == figure[(row["metric_id"], row["current_period_id"])]
        assert row["reference_value"] == figure[(row["metric_id"], row["reference_period_id"])]
    cp1d = parse((HANDOFFS / "CP-1D.md").read_text(encoding="utf-8"))
    table = cp1d.tables["cp1d.addback_assessment"]
    for row in (dict(zip(table.columns, r, strict=True)) for r in table.rows):
        assert row["amount"] == addbacks[(row["addback_id"], row["period_id"])]


def _shown(value: str) -> str:
    """A register figure as the filings print it: thousands separated, unsigned."""
    return f"{abs(Decimal(value)):,f}"


@pytest.mark.corpus
def test_cp1_figures_are_on_their_cited_lines(corpus_pack: Callable[[str], Path]) -> None:
    folder = corpus_pack("czr-2026q2-primary")
    cp1 = parse((HANDOFFS / "CP-1.md").read_text(encoding="utf-8"))
    citations = {r[0]: r for r in cp1.tables["citations"].rows}
    texts = {c[1]: (folder / c[1]).read_text(encoding="utf-8") for c in citations.values()}
    rows = [
        dict(zip(t.columns, r, strict=True))
        for key in ("cp1.model_account_register", "cp1.adjusted_ebitda_bridge")
        for t in [cp1.tables[key]]
        for r in t.rows
    ]
    figures = [
        (r["source_id"], r["value"])
        for r in rows
        if r.get("calculation_status", "VERIFIED") in CHECKED and r["value"] != "\N{EM DASH}"
    ]
    facilities = cp1.tables["cp1.debt_facility_register"]
    figures += [(r[19], r[5]) for r in facilities.rows if r[0] != "NEW-1"]
    assert len(figures) == 73
    for marker, value in figures:
        _, source, _, excerpt = citations[marker.strip("[]")]
        cells = excerpt.replace("\\|", "|")
        lines = [line for line in texts[source].splitlines() if cells in line]
        assert lines and any(_shown(value) in line for line in lines), (marker, value)
