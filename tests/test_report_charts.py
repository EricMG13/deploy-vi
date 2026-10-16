"""The ten v1 charts: specs, twins and origins (Plan 07 task 07.4)."""

from __future__ import annotations

import copy
import json
import shutil
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.fit import HEADROOM_COLUMNS
from rbotlib.handoff import Handoff, parse
from rbotlib.report import ReportError
from rbotlib.report.charts import CHART_IDS, REGISTRY, build_all
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]
HANDOFFS = FIXTURES / "handoffs"
GAP = "\N{EM DASH}"


def _tables(h: Handoff) -> Record:
    return {k: {"columns": t.columns, "rows": t.rows} for k, t in h.tables.items()}


def _limit(who: str, lid: str, figures: tuple[str, str, str], status: str) -> list[str]:
    pid, fid = who.split("/")
    value, current, room = figures
    cells = [pid, fid, lid, "Issuer", f"Param {lid}", "Hard", value, "pct_nav", current, room]
    return [*cells, GAP, "USD", "MILLIONS", status, "file"]


@pytest.fixture(scope="module")
def base(tmp_path_factory: pytest.TempPathFactory) -> Record:
    run = tmp_path_factory.mktemp("pack") / "rbot-runs" / "20261011-czr-full-credit-assessment"
    (run / "handoffs").mkdir(parents=True)
    for module in ("CP-0", "CP-1", "CP-1D"):
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["model", "--run", str(run)]) == 0
    handoffs = {
        n: {"tables": _tables(parse((HANDOFFS / f"{n}.md").read_text(encoding="utf-8")))}
        for n in ("CP-1D", "CP-3", "CP-5", "CP-L10")
    }
    handoffs["MODEL"] = {"tables": _tables(parse((run / "handoffs/MODEL.md").read_text("utf-8")))}
    limits = [
        _limit("P1/F1", "L1", ("10", "9.5", "0.5"), "Within"),
        _limit("P1/F1", "L2", ("20", "12", "8"), "Within"),
        _limit("P1/F1", "L3", ("5", "6", "-1"), "Breached"),
        _limit("P1/F1", "L4", ("5", GAP, GAP), "Not computed"),
        _limit("P2/F1", "L1", ("10", "1", "9"), "Within"),
    ]
    handoffs["FIT"] = {
        "tables": {"fit.limit_headroom": {"columns": list(HEADROOM_COLUMNS), "rows": limits}}
    }
    brief = parse((run / "run-brief.md").read_text(encoding="utf-8"))
    return {
        "steps": {n: {"status": "accepted"} for n in handoffs},
        "handoffs": handoffs,
        "model": json.loads((run / "model.json").read_text(encoding="utf-8")),
        "run_brief": {"tables": _tables(brief)},
    }


@pytest.fixture
def run(base: Record) -> Record:
    return copy.deepcopy(base)


def _one(doc: Record, chart_id: str, run_dir: Path | None = None) -> Record:
    return build_all(doc, [chart_id], run_dir)[0]


def _datums(node: object) -> Iterator[Record]:
    if isinstance(node, dict):
        if "prov" in node and "v" in node:
            yield node
        else:
            for value in node.values():
                yield from _datums(value)
    elif isinstance(node, list):
        for value in node:
            yield from _datums(value)


def _shown(d: Record) -> str:
    return f"n/a: {d['reason']}" if d["v"] is None else str(d["v"])


@pytest.mark.parametrize("chart_id", sorted(REGISTRY))
def test_every_registered_chart_builds_on_fixture_handoffs(run: Record, chart_id: str) -> None:
    entries = build_all(run, [chart_id])
    assert entries and set(REGISTRY) == set(CHART_IDS)
    for entry in entries:
        assert entry["chart_id"].startswith(chart_id) and entry["origin"] in ("host", "model")
        if entry["data"] is not None:
            assert entry["summary"] and entry["data"]["source"] and entry["twin"]["rows"]
            assert all(len(r) == len(entry["twin"]["columns"]) for r in entry["twin"]["rows"])
        else:
            assert entry["note"]


def test_the_registry_is_the_catalog_charts_plus_the_analysis_charts() -> None:
    text = Path("rbot/catalog.json").read_text(encoding="utf-8")
    named = {c for c in CHART_IDS if f'"{c}"' in text}
    analysis = {"chart.adjusted_debt_bridge", "chart.issue_counts", "chart.topic_counts"}
    assert named | analysis == set(CHART_IDS)


def test_twin_rows_equal_spec_values(run: Record) -> None:
    drawn = [e for e in build_all(run) if e["data"] is not None]
    assert len(drawn) >= 8
    for entry in drawn:
        cells = {c for row in entry["twin"]["rows"] for c in row}
        assert {_shown(d) for d in _datums(entry["data"])} <= cells


def test_gap_never_drawn_as_zero(run: Record) -> None:
    for row in run["handoffs"]["MODEL"]["tables"]["model.metrics"]["rows"]:
        if row[0] == "metric:net_leverage_adjusted":
            row[2:5] = [GAP] * 3
    strips = {e["chart_id"].rsplit(".", 1)[1]: e for e in build_all(run, ["chart.model_strip"])}
    first = strips["leverage"]["data"]["series"][0]["values"][0]
    assert (first["v"], first["prov"]) == (None, "gap") and first["reason"]
    assert first["ref"].startswith("MODEL:gap:metric:net_leverage_adjusted:")
    assert strips["leverage"]["twin"]["rows"][0][1].startswith("n/a: ")
    assert strips["liquidity"]["data"] is None and "no figure" in strips["liquidity"]["note"]
    fit = next(e for e in build_all(run, ["chart.fit_bullets"]) if ".all." in e["chart_id"])
    row = next(r for r in fit["data"]["rows"] if r["key"].endswith("L4"))
    assert row["current"]["v"] is None and row["headroom"]["v"] is None
    assert row["threshold"]["v"] == "5"


@given(st.lists(st.decimals(min_value=0, max_value=10**9, places=3), min_size=1, max_size=12))
def test_maturity_wall_sums_are_exact_decimal(amounts: list[Decimal]) -> None:
    rows: list[Record] = [
        {"fiscal_year": "2028", "facility_id": f"F{i}", "amount": format(a, "f"), "rank": "R"}
        | {"reasons": {}}
        for i, a in enumerate(amounts)
    ]
    doc = {"model": {"maturity_wall": rows, "lines": [], "columns": []}, "steps": {}}
    cell = _one(doc, "chart.maturity_wall")["data"]["series"][0]["values"][0]
    assert cell["v"] == format(sum(amounts, Decimal(0)), "f")


def test_maturity_wall_unstated_amount_is_a_gap_not_a_sum(run: Record) -> None:
    wall = run["model"]["maturity_wall"]
    wall[0]["amount"], wall[0]["reasons"] = None, {"amount": "NOT_SOURCED"}
    series = _one(run, "chart.maturity_wall")["data"]["series"]
    gaps = [d for s in series for d in s["values"] if d and d["v"] is None]
    assert gaps and "NOT_SOURCED" in gaps[0]["reason"]


def test_adjusted_debt_bridge_closes_and_flags_a_residual(run: Record) -> None:
    steps = _one(run, "chart.adjusted_debt_bridge")["data"]["steps"]
    assert steps[0]["kind"] == "total" and steps[-1]["label"] == "Adjusted debt"
    assert all(s["kind"] != "residual" for s in steps)
    parts = [Decimal(s["d"]["v"]) for s in steps]
    assert sum(parts[:-1], Decimal(0)) == parts[-1] and len(steps) > 2
    house = run["model"]["house"]["adjusted_debt"]
    house["value"] = str(Decimal(house["value"]) + 7)
    steps = _one(run, "chart.adjusted_debt_bridge")["data"]["steps"]
    residual = [s for s in steps if s["kind"] == "residual"]
    assert len(residual) == 1 and residual[0]["d"]["v"] == "7" and steps[-1]["kind"] == "total"


def test_talk_range_origin_follows_the_calculator_recompute(run: Record, tmp_path: Path) -> None:
    (tmp_path / "calc").mkdir()
    shutil.copy(FIXTURES / "calc/CP-3-bond_analytics.json", tmp_path / "calc")
    same = _one(run, "chart.talk_range", tmp_path)
    assert (same["origin"], same["note"]) == ("host", None)
    row = same["data"]["rows"][0]
    assert (row["min"]["v"], row["median"]["v"], row["max"]["v"]) == ("316.67", "337.50", "358.33")
    assert row["marker"]["v"] == "239.57"
    table = run["handoffs"]["CP-3"]["tables"]["cp3.talk_valuation"]
    table["rows"][0][table["columns"].index("implied_mid")] = "340.00"
    altered = _one(run, "chart.talk_range", tmp_path)
    assert (altered["origin"], altered["note"]) == ("model", "differs from calculator")
    assert altered["data"]["rows"][0]["median"]["v"] == "340.00"
    absent = _one(run, "chart.talk_range")
    assert (absent["origin"], absent["note"]) == ("model", "no calculator input in the run")
    (tmp_path / "calc/CP-3-bond_analytics.json").write_text("{", encoding="utf-8")
    assert _one(run, "chart.talk_range", tmp_path)["note"] == "calculator input unreadable"


def test_fit_bullets_pick_binding_limits(run: Record) -> None:
    entries = build_all(run, ["chart.fit_bullets"])
    binding = [e for e in entries if ".binding." in e["chart_id"]]
    everything = [e for e in entries if ".all." in e["chart_id"]]
    assert (binding[0]["where"], everything[0]["where"]) == ("front_page", "FIT")
    rows = binding[0]["data"]["rows"]
    assert [r["key"] for r in rows] == ["P1:F1:L1", "P1:F1:L3", "P2:F1:L1"]
    assert len(everything[0]["data"]["rows"]) == 5 and binding[0]["data"]["unit"] == "% NAV"
    assert rows[0]["direction"] == "max" and rows[0]["headroom"]["v"] == "0.5"


def test_the_other_charts_read_their_tables_as_served(run: Record) -> None:
    findings = run["handoffs"]["CP-5"]["tables"]["cp5.findings"]["rows"]
    counts = _one(run, "chart.issue_counts")["data"]
    assert sum(int(d["v"]) for s in counts["series"] for d in s["values"]) == len(findings)
    cap = _one(run, "chart.capital_structure")["data"]
    assert [s["d"]["v"] for s in cap["steps"]] == ["12265", "2320", "14585"]
    assert "3.90x Structuring" in cap["summary"] and "4.06x SSIM" in cap["summary"]
    bridge = _one(run, "chart.ebitda_bridge")["data"]["steps"]
    assert [s["kind"] for s in bridge].count("total") == 3
    assert (bridge[1]["d"]["prov"], bridge[1]["d"]["ref"]) == ("cited", "MODEL:C15")
    assert bridge[0]["d"]["prov"] == "calculated" and bridge[1]["short"] == "REALIZED"
    loan = _one(run, "chart.rv_loan")
    issuer = [r["label"] for r in loan["data"]["rows"] if r.get("sub") == "issuer"]
    assert loan["origin"] == "model" and issuer
    assert {r["from"]["v"] for r in loan["data"]["rows"]} == {"8.11"}


def test_undrawable_chart_carries_reason(run: Record) -> None:
    hy = _one(run, "chart.rv_hy")
    assert hy["data"] is None and "High-yield" in hy["note"]
    run["steps"]["CP-3"] = {"status": "failed", "reason": "model refused"}
    assert _one(run, "chart.talk_range")["note"] == "CP-3 failed: model refused"
    del run["steps"]["FIT"]
    assert _one(run, "chart.fit_bullets")["note"] == "FIT is not in this run"
    run["model"], run["steps"]["MODEL"] = None, {"status": "skipped", "reason": "not approved"}
    assert "MODEL skipped" in _one(run, "chart.maturity_wall")["note"]
    with pytest.raises(ReportError):
        build_all(run, ["chart.nope"])


def test_topic_counts_gives_one_chart_per_family_with_exact_counts(run: Record) -> None:
    rows = run["handoffs"]["CP-L10"]["tables"]["cpl10.screen_topics"]
    cols = rows["columns"]
    topics = [dict(zip(cols, r, strict=True)) for r in rows["rows"]]
    entries = build_all(run, ["chart.topic_counts"])
    families = list(dict.fromkeys(t["family"] for t in topics))
    assert len(entries) == len(families) > 1
    scales = load_rules(RBOT_ROOT).scales
    for entry, family in zip(entries, families, strict=True):
        data = entry["data"]
        assert entry["kind"] == "stackedColumns" and entry["origin"] == "host"
        assert family in data["title"] and data["summary"] and entry["twin"]["rows"]
        assert data["categories"] == list(scales["materiality"])
        assert [s["label"] for s in data["series"]] == list(scales["disposition"])
        here = [t for t in topics if t["family"] == family]
        for s in data["series"]:
            want = [
                sum(1 for t in here if t["materiality"] == m and t["disposition"] == s["label"])
                for m in data["categories"]
            ]
            assert [d["v"] for d in s["values"]] == [str(n) for n in want]
            assert all(d["prov"] == "calculated" for d in s["values"])
        assert all(len(r) == len(entry["twin"]["columns"]) for r in entry["twin"]["rows"])


def test_topic_counts_is_undrawable_without_cpl10(run: Record) -> None:
    del run["steps"]["CP-L10"], run["handoffs"]["CP-L10"]
    (entry,) = build_all(run, ["chart.topic_counts"])
    assert entry["data"] is None and "CP-L10 is not in this run" in entry["note"]
