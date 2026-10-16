"""The fixture Handoffs of Full Credit Assessment, full, agree with each other and the hosts.

CP-6 follows its contract's decision rules: per instrument, Credit Score number + Valuation
number (2-3 -> 1 - Strong OW, 4-5 -> 2 - Modest OW, 6 -> 3 - MW, 7-8 -> 4 - Modest UW, 9-10 ->
5 - Strong UW); per Strategy, the strongest instrument it can own (loans for CLO and Indexed
Loans, bonds for Indexed HY); per portfolio, the weaker of the uncapped Recommendation and
FIT's cap, which `rbot fit` on the same fixtures produces. CP-5 traces every step the Pathway
runs before it, and the Model figures CP-2 cites are the Model's.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from conftest import FIXTURES
from rbotlib.catalog import load_catalog
from rbotlib.cli import main
from rbotlib.handoff import Handoff, parse
from rbotlib.rules import RBOT_ROOT

HANDOFFS = FIXTURES / "handoffs"
ORDER = ["1 - Strong OW", "2 - Modest OW", "3 - MW", "4 - Modest UW", "5 - Strong UW", "Avoid"]
BY_SUM = {2: 0, 3: 0, 4: 1, 5: 1, 6: 2, 7: 3, 8: 3, 9: 4, 10: 4}
LOANS = {"RCF", "1L Term Loan", "2L Term Loan"}


def _handoff(module_id: str) -> Handoff:
    return parse((HANDOFFS / f"{module_id}.md").read_text(encoding="utf-8"))


def _rows(h: Handoff, table_id: str) -> list[dict[str, str]]:
    table = h.tables[table_id]
    return [dict(zip(table.columns, r, strict=True)) for r in table.rows]


def _number(grade: str) -> int:
    return int(grade.lstrip("V").split(" ")[0])


def test_cp6_recommendations_follow_the_matrix() -> None:
    cp6 = _handoff("CP-6")
    score = _number(_rows(_handoff("CP-2"), "snapshot.credit_view")[0]["credit_score"])
    levels = {r["facility_id"]: r for r in _rows(_handoff("CP-3"), "snapshot.instrument_levels")}
    recs = {r["facility_id"]: r for r in _rows(cp6, "snapshot.instrument_recommendation")}
    assert set(recs) == set(levels)
    for facility_id, rec in recs.items():
        assert rec["valuation"] == levels[facility_id]["valuation"]
        assert rec["recommendation"] == ORDER[BY_SUM[score + _number(rec["valuation"])]]
    identity = _rows(_handoff("CP-1"), "cp1.instrument_identity")
    loans = {r["facility_id"] for r in identity if r["debt_type"] in LOANS}
    owns = {"CLO": loans, "Indexed Loans": loans, "Indexed HY": set(recs) - loans}
    for row in _rows(cp6, "snapshot.recommendation"):
        best = min(
            ORDER.index(recs[f]["recommendation"]) for f in owns[row["strategy"]] & set(recs)
        )
        assert row["recommendation"] == ORDER[best], row["strategy"]


@pytest.mark.corpus
def test_cp6_caps_are_fits(prepared_run: Callable[[str], Path], tmp_path: Path) -> None:
    run = tmp_path / "pack" / "rbot-runs" / "20261011-czr-full-credit-assessment"
    shutil.copytree(prepared_run("czr-2026q2-primary"), run)
    (run / "handoffs").mkdir(exist_ok=True)
    for module in ("CP-0", "CP-1", "CP-1A", "CP-3"):
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["fit", "--run", str(run)]) == 0
    fits = {
        (r["portfolio_id"], r["facility_id"]): r
        for r in _rows(
            parse((run / "handoffs" / "FIT.md").read_text("utf-8")), "snapshot.portfolio_fit"
        )
    }
    cp6 = _handoff("CP-6")
    recs = {
        r["facility_id"]: r["recommendation"]
        for r in _rows(cp6, "snapshot.instrument_recommendation")
    }
    rows = _rows(cp6, "cp6.portfolio_recommendation")
    assert rows
    for row in rows:
        fit = fits[(row["portfolio_id"], row["instrument"])]
        assert (row["cap"], row["fit_verdict"]) == (fit["recommendation_cap"], fit["verdict"])
        assert row["uncapped"] == recs[row["instrument"]]
        assert row["final"] == ORDER[max(ORDER.index(row["uncapped"]), ORDER.index(row["cap"]))]


def test_cp5_traces_every_step_before_it() -> None:
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    steps = list(pathway.depths["full"])
    traced = [r["module_id"] for r in _rows(_handoff("CP-5"), "cp5.module_status")]
    assert traced == steps[: steps.index("CP-5")]


def test_the_model_figures_cp2_cites_are_the_models(tmp_path: Path) -> None:
    run = tmp_path / "pack" / "rbot-runs" / "20261011-czr-full-credit-assessment"
    (run / "handoffs").mkdir(parents=True)
    for module in ("CP-0", "CP-1", "CP-1D"):
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["model", "--run", str(run)]) == 0
    house = {
        r["item"]: r
        for r in _rows(parse((run / "handoffs" / "MODEL.md").read_text("utf-8")), "model.house")
    }
    text = (HANDOFFS / "CP-2.md").read_text(encoding="utf-8")
    cited = set(re.findall(r"calc: MODEL model\.house ([A-Za-z ]+?)(?=[)|;\n]| \||$)", text))
    assert cited == {"SSIM Multiple", "Adjusted leverage", "PF interest", "PF interest cover"}
    assert cited <= set(house)
    assert (house["SSIM Multiple"]["value"], house["Adjusted leverage"]["value"]) == (
        "4.06",
        "7.72",
    )
    assert (house["PF interest"]["value"], house["PF interest cover"]["value"]) == ("989", "3.63")
