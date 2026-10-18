"""Tests for the CZR content modules CP-0, CP-1A, CP-1B, CP-1C, CP-1D, CP-2, CP-2A, CP-2D, CP-2E, CP-2G and CP-2H:
every handoff validates, passes the generator's per-handoff checks, and the figures introduced here (sums, bridge,
quartiles, sensitivities, projection) recompute from their inputs."""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import checks  # noqa: E402
import lib  # noqa: E402
from core import CORPUS_DIR, D, q  # noqa: E402
from model import ModelBuilder  # noqa: E402

CTX = lib.load_ctx() if CORPUS_DIR.is_dir() else None
needs_corpus = unittest.skipUnless(CTX, "corpus not available")

BEFORE_MODEL = ["run_brief", "cp_0", "cp_1", "cp_1a", "cp_1b", "cp_1d"]
AFTER_MODEL = ["cp_1c", "cp_2", "cp_2a", "cp_2e", "cp_2d", "cp_2g"]
MINE = [
    "CP-0",
    "CP-1A",
    "CP-1B",
    "CP-1C",
    "CP-1D",
    "CP-2",
    "CP-2A",
    "CP-2D",
    "CP-2E",
    "CP-2G",
    "CP-2H",
]


def build_chain(variant: str, primary: bool = False) -> dict:
    """Build my modules in plan order, with the Model and PROJECTION added the way the Run does."""
    rid = f"T-{variant}"
    CTX.primary_runs[rid] = primary
    out: dict = {"rid": rid, "h": {}}

    def go(mod: str) -> None:
        m = importlib.import_module("czr." + mod)
        h = m.build(CTX, rid, variant)
        key = "RUN_BRIEF" if mod == "run_brief" else mod.upper().replace("_", "-")
        CTX.built[(rid, key)] = h
        out["h"][key] = h

    for mod in BEFORE_MODEL:
        go(mod)
    mb = ModelBuilder(
        CTX.built[(rid, "CP-1")], CTX.built[(rid, "RUN_BRIEF")], CTX.built[(rid, "CP-1D")], rid
    )
    CTX.models[rid] = mb
    for mod in AFTER_MODEL:
        go(mod)
    for case, years, drivers in out["h"]["CP-2G"].meta["projection"]:
        mb.add_projection(case, years, drivers)
    go("cp_2h")
    out["model"] = mb
    return out


def rows(h, tid: str) -> list[dict]:
    return h.rows(tid)


@needs_corpus
class TestPart1(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rv = build_chain("rv")
        cls.pr = build_chain("primary", primary=True)

    def test_every_handoff_validates_and_passes_the_generator_checks(self):
        for chain in (self.rv, self.pr):
            run = {"run_id": chain["rid"], "handoffs": {}}
            for step in MINE:
                h = chain["h"][step]
                self.assertEqual(h.problems(), [], step)
                hj = h.to_json()
                run["handoffs"][step] = hj
                self.assertEqual(checks.check_handoff(CTX, step, hj, run), [], step)
                for fn in checks._TABLE_CHECKS:
                    self.assertEqual(fn(hj), [], f"{step} {fn.__name__}")

    def test_cp0_inventory_is_the_corpus(self):
        inv = rows(self.rv["h"]["CP-0"], "cp0.source_inventory")
        files = {p.name for p in CORPUS_DIR.iterdir() if p.is_file()}
        self.assertEqual({r["file"] for r in inv}, files)
        self.assertTrue(all(len(r["sha256"]) == 64 for r in inv))
        self.assertEqual(sum(1 for r in inv if r["pages"] != "—"), 3)

    def test_cp0_primary_prefill_carries_the_three_tranches(self):
        pre = rows(self.pr["h"]["CP-0"], "cp0.run_brief_prefill")
        self.assertEqual(
            [r["tranche_id"] for r in pre if r["tranche_id"] != "—"], ["NEW-1", "NEW-2", "NEW-3"]
        )
        self.assertEqual(rows(self.rv["h"]["CP-0"], "cp0.prior_case"), [])

    def test_cp1a_profile_matches_the_test_clo_sector_scope(self):
        prof = rows(self.rv["h"]["CP-1A"], "snapshot.company_profile")[0]
        self.assertEqual(prof["sector"], "Leisure Facilities & Services")
        reg = {
            (r["agency"], r["scope"]): r
            for r in rows(self.rv["h"]["CP-1A"], "cp1a.ratings_register")
        }
        self.assertEqual(
            reg[("Moody's", "Issue rating, 6.00% senior notes due 2032")]["rating"], "Caa1"
        )
        self.assertEqual(reg[("Moody's", "Corporate family rating")]["outlook"], "Negative")

    def test_cp1b_changes_recompute_and_margins_tie_to_the_base_data(self):
        h = self.rv["h"]["CP-1B"]
        pc = {r["metric_id"]: r for r in rows(h, "cp1b.period_comparison")}
        self.assertEqual(pc["adjusted_ebitda_q2"]["abs_change"], "-35")
        self.assertEqual(pc["adjusted_ebitda_q2"]["pct_change_pct"], "-3.7%")
        self.assertEqual(pc["net_loss_attributable_q2"]["pct_change_pct"], "24.4%")
        kp = {r["kpi_id"]: r for r in rows(h, "cp1b.kpi_changes")}
        self.assertEqual(kp["Las Vegas Adjusted EBITDA margin"]["change"], "-4.2")
        self.assertEqual(kp["Regional Adjusted EBITDA margin"]["trend"], "Up")
        self.assertEqual(rows(h, "cp1b.guidance_vs_delivery"), [])

    def test_cp1c_statistics_and_implied_ev(self):
        h = self.rv["h"]["CP-1C"]
        pos = {r["metric_id"]: r for r in rows(h, "cp1c.positioning")}
        m = pos["ev_ebitda_x"]
        self.assertEqual(
            [m[k] for k in ("peer_min", "peer_q1", "peer_median", "peer_q3", "peer_max")],
            ["7.00", "7.40", "8.10", "8.90", "9.60"],
        )
        self.assertEqual(m["borrower_value"], "8.56")
        self.assertEqual(m["position"], "Above")
        self.assertEqual(pos["revenue_growth_pct"]["position"], "Below")
        self.assertEqual(pos["adjusted_ebitda_margin_pct"]["n"], "5")
        vm = {r["entity"]: r for r in rows(h, "cp1c.valuation_multiples")}
        lease = vm["Caesars Entertainment, Inc. (including lease financing obligations)"]
        self.assertEqual(lease["ev"], "30757")
        self.assertEqual(lease["implied_ev_median"], str(int(q(D("8.1") * D("3592"), 0))))
        self.assertEqual(vm["Caesars Entertainment, Inc. (merger value)"]["ev_ebitda_x"], "4.90x")

    def test_cp1d_keeps_the_model_on_the_issuers_ltm_ebitda(self):
        h = self.rv["h"]["CP-1D"]
        a = rows(h, "cp1d.addback_assessment")
        self.assertNotIn("Rejected", {r["verdict"] for r in a})
        self.assertEqual({r["house_realization_status"] for r in a}, {"REALIZED"})
        ltm = {r["addback_id"]: r["amount"] for r in a if r["period_id"] == "LTM_Q2_2026"}
        self.assertEqual(ltm, {"impairment": "182", "transaction_costs": "63", "sbc": "92"})
        debt_like = [r for r in rows(h, "cp1d.debt_like_items") if r["treatment"] == "Debt-like"]
        self.assertEqual([r["amount"] for r in debt_like], ["13157"])
        cc = {r["period_id"]: r["conversion_pct"] for r in rows(h, "cp1d.cash_conversion")}
        self.assertEqual(cc["LTM_Q2_2026"], "36.1%")
        mb = self.rv["model"]
        ltm_col = mb.ltm_col
        self.assertEqual(q(mb.L("adjusted_ebitda", ltm_col).value, 0), D(3592))

    def test_cp2_view_and_lists(self):
        h = self.rv["h"]["CP-2"]
        v = rows(h, "snapshot.credit_view")[0]
        self.assertEqual(
            (v["credit_score"], v["credit_direction"], v["sector_outlook"]),
            ("3 - Fair", "Deteriorating", "Neutral"),
        )
        self.assertGreaterEqual(len(rows(h, "cp2.drivers")), 3)
        kinds = {r["kind"] for r in rows(h, "snapshot.strengths_weaknesses")}
        self.assertEqual(kinds, {"Strength", "Weakness"})

    def test_cp2a_sensitivities_and_paths(self):
        h = self.rv["h"]["CP-2A"]
        s = {r["sensitivity"]: r for r in rows(h, "cp2a.sensitivities")}
        down = D(11648) * D("0.97") * D("0.29") - D(3592)
        self.assertEqual(
            s["FY2026 Downside case (revenue -3.0%, margin 29.0%)"]["result"], str(q(down, 1))
        )
        self.assertEqual(s["+100 bps Term SOFR on bank debt"]["result"], "-59.7")
        paths = rows(h, "cp2a.downside_paths")
        self.assertGreaterEqual(len(paths), 5)
        self.assertTrue(
            {"Low", "Medium", "High"}
            <= {r["probability"] for r in paths} | {r["impact"] for r in paths}
        )
        ids = {r["path_id"] for r in paths}
        self.assertTrue(all(t["linked_path"] in ids for t in rows(h, "cp2a.triggers")))

    def test_cp2d_liquidity_bridge_and_runway_reconcile(self):
        h = self.rv["h"]["CP-2D"]
        src = rows(h, "cp2d.liquidity_sources")
        acc = sum(D(r["amount"]) for r in src if r["accessible"] == "Yes")
        self.assertEqual(acc, D(2928))
        uses = rows(h, "cp2d.cash_uses_12m")
        mand = sum(D(r["amount"]) for r in uses if r["mandatory"] == "Yes")
        run = {r["item"]: r for r in rows(h, "cp2d.runway")}
        self.assertEqual(D(run["Mandatory uses 12m"]["value"]), mand)
        self.assertEqual(D(run["Headroom"]["value"]), acc - mand)
        self.assertEqual(D(run["Months of runway"]["value"]), q(acc / (mand / 12), 1))
        br = rows(h, "cp2d.bridge")
        self.assertEqual((br[0]["kind"], br[-1]["kind"]), ("Opening total", "Closing total"))
        self.assertEqual(
            D(br[0]["amount"]) + sum(D(r["amount"]) for r in br[1:-1]), D(br[-1]["amount"])
        )
        capex27 = {
            r["use"]: D(r["amount"])
            for r in uses
            if "first half of 2027" in r["use"] and "capex" in r["use"]
        }
        self.assertEqual(sum(capex27.values()), D(400))  # half of the synthetic FY2027 Base capex

    def test_cp2e_sensitivities_are_signed_and_calculated(self):
        s = {r["sensitivity"]: r for r in rows(self.rv["h"]["CP-2E"], "cp2e.sensitivities")}
        self.assertEqual(s["Term SOFR +100 bps"]["cash_impact"], "-59.7")
        self.assertEqual(s["Term SOFR -100 bps"]["cash_impact"], "59.7")
        self.assertEqual(s["CPI +1% on VICI and GLPI cash rent"]["cash_impact"], "-13.6")
        self.assertEqual(rows(self.rv["h"]["CP-2E"], "cp2e.hedges"), [])

    def test_cp2g_tables_carry_exactly_the_projection(self):
        for chain in (self.rv, self.pr):
            h, mb = chain["h"]["CP-2G"], chain["model"]
            for r in rows(h, "cp2g.forecast_movements"):
                case, year = r["case"], int(r["period_id"][2:6])
                p = mb.projection_rows[case][year]
                self.assertEqual(D(r["revenue"]), q(p["revenue"], 3))
                self.assertEqual(D(r["ebitda"]), q(p["ebitda"], 3))
                self.assertEqual(D(r["cfo"]), q(p["cfo"], 3))
                self.assertEqual(D(r["capex"]), q(p["capex"], 3))
            self.assertEqual(
                [c for c in mb.forecast_checks if c["status"] in ("FAIL", "SHORTFALL")], []
            )
        # the synthetic capex amounts are reproduced exactly by the percentage of revenue
        cap = {
            (r["case"], r["period_id"]): D(r["capex"])
            for r in rows(self.rv["h"]["CP-2G"], "cp2g.forecast_movements")
        }
        self.assertEqual(cap[("BASE", "FY2026E_BASE")], D(-760))
        self.assertEqual(cap[("DOWNSIDE", "FY2027E_DOWNSIDE")], D(-600))
        deck = rows(self.rv["h"]["CP-2G"], "cp2g.rate_deck")
        self.assertEqual(
            [(r["base_rate"], r["downside_rate"]) for r in deck],
            [("4.30", "4.80"), ("3.90", "4.90"), ("3.70", "4.70")],
        )
        classes = {r["basis_class"] for r in rows(self.rv["h"]["CP-2G"], "cp2g.assumptions")}
        self.assertEqual(classes, {"Analyst assumption", "Derived", "Sourced"})

    def test_primary_projection_starts_from_the_pro_forma_debt(self):
        base = self.pr["model"].snapshot_base_col()
        self.assertEqual(base.kind, "PF_LTM")
        self.assertGreater(self.pr["model"].projection_rows["BASE"][2026]["opening_debt"], D(16000))
        self.assertLess(self.rv["model"].projection_rows["BASE"][2026]["opening_debt"], D(12000))

    def test_cp2h_headroom_and_projection(self):
        for chain in (self.rv, self.pr):
            trig = rows(chain["h"]["CP-2H"], "cp2h.rating_triggers")
            self.assertEqual([r["status"] for r in trig], ["Tight", "Tight", "Headroom"])
            self.assertEqual(trig[0]["headroom"], "0.4")
            self.assertEqual(trig[1]["headroom"], "0.3")
            self.assertTrue(all(r["projected_value"] != "—" for r in trig))
            self.assertGreater(D(trig[0]["projected_value"]), D(trig[0]["threshold"]))
        self.assertEqual(
            {r["case"] for r in rows(self.rv["h"]["CP-2H"], "cp2h.migration_view")},
            {"BASE", "DOWNSIDE"},
        )


if __name__ == "__main__":
    unittest.main()
