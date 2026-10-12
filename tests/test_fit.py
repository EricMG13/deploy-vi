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
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from builders import make_run
from conftest import CORPUS, FIXTURES
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib.cli import main
from rbotlib.fit import FIT_COLUMNS, HEADROOM_COLUMNS, FitError, instruments
from rbotlib.handoff import Handoff, parse

HANDOFFS = FIXTURES / "handoffs"
TEST_CLO_I: dict[str, Any] = {
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
            "largest": False,
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
            "largest": False,
            "limit_value": "7.5",
            "unit": "pct_nav",
            "limit_kind": "Hard",
            "current_value": "7.36",
            "source": "limits.csv row 9",
        },
    ],
    "unparsed": [{"row": "limits.csv row 14", "reason": "minimum limit", "kind": "minimum"}],
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
    assert (tlb["max_size"], tlb["binding_limit"], tlb["verdict"]) == ("15.7725", "C-01", "Watch")
    assert (tlb["current_exposure"], tlb["current_exposure_pct_nav_pct"]) == ("0", "0.0%")
    notes = fits["CEI-SN-2029"]
    assert (notes["max_size"], notes["binding_limit"], notes["verdict"]) == (
        "0.88326",
        "C-04",
        "Watch",
    )
    assert notes["recommendation_cap"] == "3 - MW"
    assert "- TEST_CLO_I: limits.csv row 14: minimum limit" in h.body
    assert (
        "- TEST_CLO_I: no position matched issuer_id CZR or issuer name Caesars Entertainment, "
        "Inc.; current exposure 0 assumes the issuer is not held." in h.body
    )
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


def test_a_portfolio_without_nav_is_a_watch_with_the_reason(tmp_path: Path) -> None:
    run = _run(tmp_path, TEST_CLO_I | {"nav": ""})
    assert main(["fit", "--run", str(run)]) == 0
    tlb = _fits(run)["CEI-TLB"]
    assert (tlb["verdict"], tlb["max_size"], tlb["current_exposure_pct_nav_pct"]) == (
        "Watch",
        "\N{EM DASH}",  # a Hard limit that could cap the size was not computed
        "\N{EM DASH}",
    )
    assert "limit C-01 could not be computed" in tlb["reason"]


def _two_portfolios(tmp_path: Path, second: dict[str, Any]) -> Path:
    run = _run(tmp_path)
    brief = run / "run-brief.md"
    line = next(x for x in brief.read_text("utf-8").splitlines() if x.startswith("| TEST_CLO_I"))
    other = line.replace("TEST_CLO_I", str(second["portfolio_id"]))
    brief.write_text(brief.read_text("utf-8").replace(line, f"{line}\n{other}"), encoding="utf-8")
    name = f"{second['portfolio_id']}.json"
    (run / "prepared" / "portfolios" / name).write_text(json.dumps(second), encoding="utf-8")
    return run


def test_one_bad_portfolio_does_not_stop_the_others(tmp_path: Path) -> None:
    """Money review I8: the good portfolio is computed, the bad one is a Watch with the reason."""
    run = _two_portfolios(tmp_path, TEST_CLO_I | {"portfolio_id": "BAD_NAV", "nav": ""})
    assert main(["fit", "--run", str(run)]) == 0
    assert sorted(p.name for p in (run / "fit").iterdir()) == ["BAD_NAV.json", "TEST_CLO_I.json"]
    h = parse((run / "handoffs" / "FIT.md").read_text(encoding="utf-8"))
    rows = [r for r in _rows(h, "snapshot.portfolio_fit") if r["facility_id"] == "CEI-TLB"]
    by_portfolio = {r["portfolio_id"]: r["verdict"] for r in rows}
    assert by_portfolio == {"TEST_CLO_I": "Watch", "BAD_NAV": "Watch"}


def test_an_unreadable_limit_row_lowers_the_verdict_end_to_end(tmp_path: Path) -> None:
    """Money review C1: a Hard maximum that could not be read is a Watch, not a silent Fits."""
    lost = {"row": "limits.csv row 23", "reason": "amount limit under Unit 'millions'"}
    run = _run(tmp_path, TEST_CLO_I | {"unparsed": [lost | {"kind": "limit"}]})
    assert main(["fit", "--run", str(run)]) == 0
    tlb = _fits(run)["CEI-TLB"]
    assert (tlb["verdict"], tlb["recommendation_cap"]) == ("Watch", "3 - MW")
    assert (
        tlb["reason"] == "limits.csv row 23 could not be read (amount limit under Unit 'millions')"
    )


def test_a_position_matched_by_name_alone_is_counted_and_a_watch(tmp_path: Path) -> None:
    held = {"issuer_id": "CAESARS", "issuer_name": "Caesars Entertainment Inc", "par": "5.0"}
    run = _run(tmp_path, TEST_CLO_I | {"positions": [held]})
    assert main(["fit", "--run", str(run)]) == 0
    tlb = _fits(run)["CEI-TLB"]
    assert (tlb["current_exposure"], tlb["verdict"]) == ("5", "Watch")
    assert "matched the issuer by name only" in tlb["reason"]


def test_every_instrument_takes_its_terms_from_the_latest_period() -> None:
    """Rest review I9: the register lists H1_2026 first and FY2025 after it."""
    text = (HANDOFFS / "CP-1.md").read_text(encoding="utf-8")
    changed = text.replace(
        "CEI-RCF | CEI Revolving Credit Facility | FY2025 | Revolving credit facility | USD | 160 "
        "| 160 | 2250 | SECURED | SENIOR | Adjusted Term SOFR + 2.25% | 2028-01-31",
        "CEI-RCF | CEI Revolving Credit Facility | FY2025 | Revolving credit facility | USD | 160 "
        "| 160 | 2250 | SECURED | SENIOR | Adjusted Term SOFR + 2.25% | 2026-12-31",
    )
    assert changed != text
    rcf = next(i for i in instruments(parse(changed), None) if i.facility_id == "CEI-RCF")
    assert rcf.maturity == date(2028, 1, 31)  # the H1_2026 row, not the older FY2025 one


def test_a_facility_in_two_currencies_is_refused() -> None:
    text = (HANDOFFS / "CP-1.md").read_text(encoding="utf-8")
    row = "CEI-TLA | CEI Term Loan A | FY2025 | Term loan | USD"
    assert row in text
    with pytest.raises(FitError, match="CEI-TLA has rows in USD and EUR"):
        instruments(parse(text.replace(row, row.replace("USD", "EUR"))), None)


def test_a_hard_limit_that_is_not_computed_is_named_in_the_reason(tmp_path: Path) -> None:
    exclusion = {
        **TEST_CLO_I["limits"][0],
        "limit_id": "C-17",
        "scope": "sector",
        "scope_value": "Tobacco, Thermal Coal",
        "limit_value": "0",
    }
    portfolio = TEST_CLO_I | {"limits": [TEST_CLO_I["limits"][0], exclusion]}
    run = _run(tmp_path, portfolio)
    assert main(["fit", "--run", str(run)]) == 0
    tlb = _fits(run)["CEI-TLB"]
    assert (tlb["max_size"], tlb["verdict"]) == ("15.7725", "Watch")
    assert (
        tlb["reason"] == "limit C-17 could not be computed; max_size is an upper bound without it"
    )


# --- the rest review: nothing is read or written outside the run, all or nothing, no traceback


def test_a_prepared_json_outside_the_run_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    outside = tmp_path / "pack" / "outside.json"
    outside.write_text(json.dumps(TEST_CLO_I | {"portfolio_id": "ESCAPED"}), encoding="utf-8")
    brief = run / "run-brief.md"
    brief.write_text(
        brief.read_text("utf-8").replace(
            "prepared/portfolios/TEST_CLO_I.json", "../../outside.json"
        ),
        encoding="utf-8",
    )
    assert main(["fit", "--run", str(run)]) == 1
    assert "is outside the run folder" in capsys.readouterr().out
    assert not (run / "handoffs" / "FIT.md").exists() and not (run / "fit").exists()
    assert not (tmp_path / "pack" / "ESCAPED.json").exists()


@pytest.mark.parametrize("portfolio_id", ["../../ESCAPED", "..", ".hidden", "a/b", ""])
def test_a_portfolio_id_that_is_not_a_file_name_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], portfolio_id: str
) -> None:
    run = _run(tmp_path, TEST_CLO_I | {"portfolio_id": portfolio_id})
    assert main(["fit", "--run", str(run)]) == 1
    assert "is not a file name" in capsys.readouterr().out
    assert not (run / "fit").exists()
    assert not (tmp_path / "pack" / "ESCAPED.json").exists()


@pytest.mark.parametrize("folder", ["fit", "handoffs"])
def test_a_symlinked_output_folder_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], folder: str
) -> None:
    run = _run(tmp_path)
    target = tmp_path / "elsewhere"
    if folder == "handoffs":
        shutil.move(run / "handoffs", target)
    else:
        target.mkdir()
    (run / folder).symlink_to(target, target_is_directory=True)
    assert main(["fit", "--run", str(run)]) == 1
    assert f"{folder}/: a link or outside the run folder" in capsys.readouterr().out
    assert not (target / "TEST_CLO_I.json").exists() and not (target / "FIT.md").exists()


def test_a_malformed_second_portfolio_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Rest review I7: no new JSON beside a stale FIT.md; the old files stay as they were."""
    run = _two_portfolios(tmp_path, TEST_CLO_I | {"portfolio_id": "SECOND", "positions": "abc"})
    (run / "fit").mkdir()
    (run / "fit" / "TEST_CLO_I.json").write_text("old", encoding="utf-8")
    (run / "handoffs" / "FIT.md").write_text("old", encoding="utf-8")
    assert main(["fit", "--run", str(run)]) == 1
    assert "positions must be a list of objects" in capsys.readouterr().out
    assert (run / "fit" / "TEST_CLO_I.json").read_text("utf-8") == "old"
    assert (run / "handoffs" / "FIT.md").read_text("utf-8") == "old"


def test_the_json_of_a_portfolio_no_longer_attached_is_removed(tmp_path: Path) -> None:
    run = _run(tmp_path)
    (run / "fit").mkdir()
    (run / "fit" / "GONE.json").write_text("{}", encoding="utf-8")
    assert main(["fit", "--run", str(run)]) == 0
    assert [p.name for p in (run / "fit").iterdir()] == ["TEST_CLO_I.json"]


@pytest.mark.parametrize(
    ("portfolio", "message"),
    [
        ([], "not a JSON object"),
        (TEST_CLO_I | {"positions": "abc"}, "positions must be a list of objects"),
        (TEST_CLO_I | {"positions": [{"issuer_id": "X", "par": "n/a"}]}, "positions[1].par"),
        (
            TEST_CLO_I | {"limits": [{**TEST_CLO_I["limits"][0], "limit_value": "2,5"}]},
            "limits[1]: limit_value: '2,5' is not a number",
        ),
        (
            TEST_CLO_I | {"limits": [{**TEST_CLO_I["limits"][0], "limit_value": "NaN"}]},
            "is not a finite number",
        ),
        (
            TEST_CLO_I | {"limits": [{**TEST_CLO_I["limits"][0], "unit": "bps"}]},
            "unit or limit_kind is not one the spec names",
        ),
        (TEST_CLO_I | {"strategy": 3}, "strategy must be text"),
    ],
)
def test_a_hand_edited_portfolio_exits_1_naming_the_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], portfolio: object, message: str
) -> None:
    run = _run(tmp_path)
    text = json.dumps(portfolio)
    (run / "prepared" / "portfolios" / "TEST_CLO_I.json").write_text(text, encoding="utf-8")
    assert main(["fit", "--run", str(run)]) == 1
    assert message in capsys.readouterr().out
    assert not (run / "fit").exists()


def test_a_numeric_nav_is_read_as_a_number(tmp_path: Path) -> None:
    run = _run(tmp_path, TEST_CLO_I | {"nav": 630.9, "par": 634})
    assert main(["fit", "--run", str(run)]) == 0
    assert _fits(run)["CEI-TLB"]["max_size"] == "15.7725"


def test_a_handoff_that_is_not_utf8_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    (run / "handoffs" / "CP-1A.md").write_bytes(b"\xff\xfe not text")
    assert main(["fit", "--run", str(run)]) == 1
    assert "CP-1A.md: not UTF-8 text" in capsys.readouterr().out


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
    # C-17 excludes sectors in the CLO's words; CP-1A's "Casino-entertainment ..." is not one of
    # them and the book holds no Caesars position, so the answer is unknown, never Fits (C2)
    assert fits["CEI-TLB"]["reason"] == (
        "limit C-17 could not be computed; max_size is an upper bound without it"
    )
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
    assert "- TEST_CLO_I CEI-RCF: missing or unreadable rating, counted toward C-04" in h.body
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
