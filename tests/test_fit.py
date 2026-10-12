"""`rbot fit`, the FIT host step (interfaces spec sections 3.4 and 7; section 12.5 row 05).

The run reads the fixture Handoffs of `czr-2026q2-primary` (CP-0's Run Brief, CP-1's
instruments, CP-1A's sector and country, CP-3) and a prepared portfolio. On Test CLO I
(NAV 630.9, no Caesars position) the hand-computed fits are: the issuer limit C-01 (Hard,
2.5% of NAV) leaves 2.5 x 630.9 / 100 = 15.7725 for every instrument; the senior notes
(Caa1 / B-) fall in the CCC bucket, whose Hard limit C-04 (7.5%, at 7.36%) leaves
0.14 x 6.309 = 0.88326, under 1% of NAV (6.309), so they are Watch and capped at 3 - MW.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import make_run
from conftest import CORPUS, FIXTURES
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib.cli import main
from rbotlib.fit import FIT_COLUMNS, HEADROOM_COLUMNS
from rbotlib.handoff import Handoff, parse

HANDOFFS = FIXTURES / "handoffs"
TEST_CLO_I = {
    "schema": "rbot-portfolio/1",
    "portfolio_id": "TEST_CLO_I",
    "portfolio_name": "Test CLO I Ltd",
    "strategy": "CLO",
    "as_of": "2026-05-29",
    "nav": "630.9",
    "par": "634.0",
    "currency": "USD",
    "unit": "MILLIONS",
    "positions_file": "SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv",
    "limits_file": "SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv",
    "positions": [{"issuer_id": "ASURION", "par": "15.0", "pct_nav": "2.37"}],
    "limits": [
        {
            "limit_id": "C-01",
            "category": "Single Name",
            "parameter": "Max single issuer",
            "scope": "issuer",
            "scope_value": None,
            "limit_value": "2.5",
            "unit": "pct_nav",
            "limit_kind": "Hard",
            "current_value": "2.37",
            "source": "limits.csv row 6",
        },
        {
            "limit_id": "C-04",
            "category": "Rating — CCC Bucket",
            "parameter": "Max CCC",
            "scope": "rating_bucket",
            "scope_value": "CCC",
            "limit_value": "7.5",
            "unit": "pct_nav",
            "limit_kind": "Hard",
            "current_value": "7.36",
            "source": "limits.csv row 9",
        },
    ],
    "unparsed": [{"row": "limits.csv row 14", "reason": "minimum limit"}],
}


def _rows(h: Handoff, table_id: str) -> list[dict[str, str]]:
    table = h.tables[table_id]
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def _run(tmp_path: Path, portfolio: dict[str, Any] | None = TEST_CLO_I) -> Path:
    run = make_run(tmp_path / "pack", "20261011-czr-full-credit-assessment")
    (run / "handoffs").mkdir()
    cp0 = (HANDOFFS / "CP-0.md").read_text(encoding="utf-8")
    if portfolio is None:
        cp0 = "\n".join(line for line in cp0.splitlines() if not line.startswith("| TEST_CLO_I"))
    (run / "handoffs" / "CP-0.md").write_text(cp0, encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    for module in ("CP-1", "CP-1A", "CP-3"):
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    if portfolio is not None:
        (run / "prepared" / "portfolios").mkdir(parents=True)
        text = json.dumps(portfolio, indent=2)
        (run / "prepared" / "portfolios" / "TEST_CLO_I.json").write_text(text, encoding="utf-8")
    return run


def _fits(run: Path) -> dict[str, dict[str, str]]:
    h = parse((run / "handoffs" / "FIT.md").read_text(encoding="utf-8"))
    return {r["facility_id"]: r for r in _rows(h, "snapshot.portfolio_fit")}


def test_rbot_fit_writes_the_handoff_and_the_json(tmp_path: Path) -> None:
    run = _run(tmp_path)
    assert main(["fit", "--run", str(run)]) == 0
    h = parse((run / "handoffs" / "FIT.md").read_text(encoding="utf-8"))
    assert h.sections == ["Analysis", "Tables", "Gaps", "Citations"]
    assert h.front_matter["inputs"] == "CP-1, CP-1A, CP-3, RUN_BRIEF"
    assert h.front_matter["qa_status"] == "Restricted"  # one limit is not sized against
    assert h.tables["snapshot.portfolio_fit"].columns == FIT_COLUMNS
    assert h.tables["fit.limit_headroom"].columns == HEADROOM_COLUMNS
    fits = _fits(run)
    assert len(fits) == 12
    tlb = fits["CEI-TLB"]
    assert (tlb["max_size"], tlb["binding_limit"], tlb["verdict"]) == ("15.7725", "C-01", "Fits")
    assert (tlb["current_exposure"], tlb["current_exposure_pct_nav_pct"]) == ("0", "0.0%")
    notes = fits["CEI-SN-2029"]
    assert (notes["max_size"], notes["binding_limit"], notes["verdict"]) == (
        "0.88326",
        "C-04",
        "Watch",
    )
    assert notes["recommendation_cap"] == "3 - MW"
    assert "- TEST_CLO_I: limits.csv row 14: minimum limit" in h.body
    data = json.loads((run / "fit" / "TEST_CLO_I.json").read_text(encoding="utf-8"))
    assert data["schema"] == "rbot-fit/1" and len(data["instruments"]) == 12
    sn = next(i for i in data["instruments"] if i["row"]["facility_id"] == "CEI-SN-2029")
    assert [r["limit_id"] for r in sn["limits"]] == ["C-01", "C-04"] and sn["breached"] == []


def test_without_a_portfolio_fit_writes_empty_tables(tmp_path: Path) -> None:
    run = _run(tmp_path, None)
    assert main(["fit", "--run", str(run)]) == 0
    h = parse((run / "handoffs" / "FIT.md").read_text(encoding="utf-8"))
    assert h.front_matter["qa_status"] == "Restricted"
    assert h.tables["snapshot.portfolio_fit"].rows == []
    assert "No portfolio in the Portfolio Context" in h.body


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda run: (run / "handoffs" / "CP-3.md").unlink(), "handoffs/CP-3.md: missing"),
        (
            lambda run: (run / "handoffs" / "CP-3.md").write_text("no front matter", "utf-8"),
            "handoffs/CP-3.md does not validate (exit 2)",
        ),
        (lambda run: (run / "handoffs" / "CP-1.md").unlink(), "CP-1.md: missing; FIT needs it"),
        (
            lambda run: (run / "prepared" / "portfolios" / "TEST_CLO_I.json").unlink(),
            "prepared/portfolios/TEST_CLO_I.json: missing",
        ),
    ],
)
def test_fit_exits_1_naming_the_input(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    change: Callable[[Path], object],
    message: str,
) -> None:
    run = _run(tmp_path)
    change(run)
    assert main(["fit", "--run", str(run)]) == 1
    assert message in capsys.readouterr().out


def test_a_portfolio_without_nav_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path, TEST_CLO_I | {"nav": ""})
    assert main(["fit", "--run", str(run)]) == 1
    assert "NAV and par must be positive figures" in capsys.readouterr().out


@pytest.mark.corpus
def test_fit_arithmetic_test_clo_i(prepared_run: Callable[[str], Path], tmp_path: Path) -> None:
    """Interfaces spec section 12.5 row 05: the Test CLO I files of the primary pack."""
    run = tmp_path / "pack" / "rbot-runs" / "20261011-czr-full-credit-assessment"
    shutil.copytree(prepared_run("czr-2026q2-primary"), run)
    (run / "handoffs").mkdir(exist_ok=True)
    shutil.copy(HANDOFFS / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    for module in ("CP-1", "CP-1A", "CP-3"):
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["fit", "--run", str(run)]) == 0
    fits = _fits(run)
    assert {k: (v["max_size"], v["verdict"]) for k, v in fits.items()} == {
        **{k: ("15.7725", "Watch") for k in ("CEI-TLB", "CEI-TLB-1", "NEW-1")},
        **{k: ("15.7725", "Watch") for k in ("CEI-SSN-2030", "CEI-SSN-2032")},
        # C-04 (7.36% of 7.5%) counts the unrated instruments with the CCC bucket (money review I1)
        **{k: ("0.88326", "Watch") for k in ("CEI-RCF", "CEI-TLA", "CVA-DDTL")},
        **{k: ("0.88326", "Watch") for k in ("SID-BONDS", "OTHER-PAYABLES")},
        "CEI-SN-2029": ("0.88326", "Watch"),
        "CEI-SN-2032": ("0.88326", "Watch"),
    }
    h = parse((run / "handoffs" / "FIT.md").read_text(encoding="utf-8"))
    rows = {(r["facility_id"], r["limit_id"]): r for r in _rows(h, "fit.limit_headroom")}
    assert rows[("CEI-TLB", "C-17")]["status"] == "Not computed"
    assert rows[("CEI-TLB", "C-06")]["headroom_amount"] == "17.91756"  # (10 - 7.16) x 6.309
    assert rows[("CEI-RCF", "C-05")]["status"] == "Within"  # unrated: C-05 at 3.73%
    assert rows[("CEI-RCF", "C-04")]["headroom_amount"] == "0.88326"  # unrated counts toward CCC
    assert ("CEI-TLB", "C-04") not in rows and ("CEI-TLB", "C-05") not in rows
    assert rows[("CEI-SN-2029", "C-10")]["headroom"] == "9.39"  # 2nd lien / unsecured
    assert ("CEI-TLB", "C-10") not in rows
    assert rows[("CEI-TLB", "C-02")]["status"] == "From file"
    assert "row 8: minimum limit" in h.body  # the WAR floor "≥ Caa1" is a minimum, Gaps only


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", ["czr-2026q2-portfolio", "czr-2026q2-lite-portfolio"])
def test_fit_runs_on_the_czr_portfolio_packs(
    pack_id: str, prepared_run: Callable[[str], Path], tmp_path: Path
) -> None:
    """Amendment A12: the Test CLO I positions and limits files are in these packs' registry
    entries (SYNTHETIC, shared with the primary pack), so `rbot prepare` builds the portfolio
    and FIT computes it."""
    pack = CORPUS.pack(pack_id)
    run = tmp_path / "pack" / "rbot-runs" / "20261011-czr-portfolio-decision"
    shutil.copytree(prepared_run(pack_id), run)
    (run / "handoffs").mkdir(exist_ok=True)
    issuer = (pack.data["issuer"]["name"], pack.data["issuer"]["id"])
    text = cp0_handoff(
        run, issuer, pack.data["as_of"], registry_classification(pack), primary=False
    )
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    for module in ("CP-1", "CP-1A", "CP-3"):
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["fit", "--run", str(run)]) == 0
    fits = _fits(run)
    assert fits["CEI-TLB"]["verdict"] == "Watch" and fits["CEI-SN-2032"]["verdict"] == "Watch"
    assert fits["CEI-TLB"]["max_size"] == "15.7725" and fits["CEI-SN-2032"]["max_size"] == "0.88326"
