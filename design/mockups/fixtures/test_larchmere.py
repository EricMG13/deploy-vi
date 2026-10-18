"""Tests for the Larchmere fixture (fictional issuer): the derived figures, the Fit result and the whole Run."""

from __future__ import annotations

import importlib
import importlib.util
import sys
import unittest
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lib  # noqa: E402
from core import D, slug  # noqa: E402
from larchmere import cp_2d, cp_3, cp_3c, cp_4c  # noqa: E402
from larchmere import derived as X  # noqa: E402
from larchmere import facts as F  # noqa: E402

CTX = lib.load_ctx()
_RUN: dict = {}


def _runs() -> dict:
    spec = importlib.util.spec_from_file_location("bf", HERE / "build-fixtures.py")
    assert spec is not None and spec.loader is not None
    bf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bf)
    return bf.RUNS


def built() -> tuple[lib.Run, dict]:
    """The Larchmere Run built with CP-DR skipped (no research question approved), and its JSON."""
    if not _RUN:
        cfg = _runs()["larchmere-distressed-restructuring"]
        plan = CTX.spec["pathways"][cfg["pathway"]]["depths"][cfg["depth"]]
        builders = {
            s: importlib.import_module(f"larchmere.{slug(s)}").build
            for s in plan
            if s not in ("MODEL", "PROJECTION", "FIT", "CP-DR", "CP-8")
        }
        mod, _, attr = cfg["portfolios"][0].partition(":")
        portfolios = [getattr(importlib.import_module(mod), attr)(CTX)]
        rb = importlib.import_module("larchmere.run_brief")
        run = lib.Run(
            CTX, "larchmere-test", cfg["run_id"], cfg["pathway"], cfg["depth"], cfg["issuer"],
            primary=cfg["primary"], variant=cfg["variant"], issuer_fictional=True,
            notes=list(cfg["notes"]), portfolios=portfolios, fit_exclude=(),
            deep_research=cfg["deep_research"], prior_case=None,
            n_a_charts=dict(cfg["n_a_charts"]), skip_reasons=dict(cfg["skip_reasons"]),
        )  # fmt: skip
        run.build(
            builders,
            lambda c, rid, var: rb.build(c, rid, var, pathway=cfg["pathway"], depth=cfg["depth"]),
        )
        _RUN["run"], _RUN["json"] = run, run.to_json()
    return _RUN["run"], _RUN["json"]


def rows(data: dict, step: str, tid: str) -> list[dict]:
    t = data["handoffs"][step]["tables"][tid]
    return [dict(zip(t["columns"], r, strict=True)) for r in t["rows"]]


class TestFacts(unittest.TestCase):
    def test_every_fact_has_a_one_sentence_rationale(self):
        for k, f in F.FACTS.items():
            self.assertTrue(f.why.strip().endswith("."), k)
            self.assertNotIn("\n", f.why, k)

    def test_prose_adds_separators_but_not_to_years(self):
        self.assertEqual(
            F.prose("debt 1700 and 1744.25 in 2026, FY2028E, 3.5"),
            "debt 1,700 and 1,744.25 in 2026, FY2028E, 3.5",
        )


class TestDerived(unittest.TestCase):
    def test_ltm_and_house_ebitda(self):
        self.assertEqual(X.ltm("revenue")[0], 1412)
        self.assertEqual(X.ltm("adjusted_ebitda")[0], 210)
        self.assertEqual(X.ssim_ltm(), 194)

    def test_bridge_and_segments_close_every_period(self):
        for p in [*F.FLOW_PERIODS, "LTM_Q2_2026"]:
            self.assertEqual(
                X.reported_ebitda(p) + X.addback_total(p), X.flow("adjusted_ebitda", p)
            )
            seg = sum(
                (
                    D(v[2][F.FLOW_PERIODS.index(p)]) if p in F.FLOW_PERIODS else X.segment_ltm(k)
                    for k, v in F.val("segment_revenue").items()
                ),
                Decimal(0),
            )
            self.assertEqual(seg, X.flow("revenue", p), p)

    def test_story_figures(self):
        c = X.covenant()
        self.assertEqual(
            (c["cov_ebitda"], c["lev"], c["head"]), (148, Decimal("8.03"), Decimal("-1.53"))
        )
        self.assertEqual(c["liq_head"], 12)
        self.assertEqual(c["cure"], Decimal("34.8"))
        self.assertEqual(X.total_debt("JUN30_2026"), 1700)
        h1 = (D(F.val("adjusted_ebitda")["H1_2026"]) - D(F.val("adjusted_ebitda")["H1_2025"])) / D(
            F.val("adjusted_ebitda")["H1_2025"]
        )
        self.assertEqual(round(h1 * 100, 1), Decimal("-25.0"))

    def test_waterfall_fulcrum_migrates_by_scenario(self):
        evs = X.enterprise_values()
        for sc, (m, x, ev, _s) in evs.items():
            rows_ = X.waterfall(ev)
            self.assertEqual(
                sum((r["allocation"] for r in rows_), Decimal(0)) + rows_[-1]["residual"], ev
            )
            if sc != "Liquidation":
                self.assertEqual(ev, m * x)
        fulcrum = {
            sc: next(r["class_id"] for r in X.waterfall(v[2]) if r["fulcrum"])
            for sc, v in evs.items()
        }
        self.assertEqual(fulcrum["Going concern: base"], "C3-2L")
        self.assertEqual(fulcrum["Going concern: low"], "C2-1L")
        self.assertEqual(fulcrum["Going concern: high"], "C4-NOTES")

    def test_priming_loan_moves_value_to_new_money(self):
        ev = X.enterprise_values()["Going concern: base"][2]
        new_money = D(F.val("new_money")["size"])
        lme = X.waterfall(ev, new_money)
        self.assertEqual(lme[1]["allocation"], ev - new_money - D(F.val("claims_other")["admin"]))
        self.assertEqual(lme[2]["allocation"], 0)

    def test_market_implied_risk(self):
        mk = X.market()
        self.assertEqual(mk["llg_tlb"]["spread"], 1317)
        self.assertEqual(mk["llg_tlb"]["pd"], Decimal("75.7"))
        self.assertGreater(mk["llg_notes"]["pd"], mk["llg_tlb"]["pd"])

    def test_talk_is_inside_the_term_loan(self):
        tk = cp_3.talk()
        self.assertEqual((tk["low"][0], tk["mid"][0], tk["high"][0]), (1083, 1133, 1183))
        self.assertLess(tk["high"][0], X.market()["llg_tlb"]["spread"])

    def test_liquidity_runway(self):
        f = cp_2d.figures()
        self.assertEqual(f["head"], f["closing"])
        self.assertEqual(f["head"], f["accessible"] - f["mand"])
        self.assertEqual(f["accessible"], 225)
        self.assertLess(f["months"], 12)
        self.assertGreater(f["floor_months"], 1)

    def test_exposures_and_maturities(self):
        mat = cp_3c.maturities()
        self.assertEqual(sum(mat.values()), X.total_debt("JUN30_2026"))
        ex = cp_3c.exposure_cases()
        self.assertEqual(ex["Base"]["C2-1L"], 0)
        self.assertGreater(ex["LME"]["C2-1L"], ex["Base"]["C2-1L"])
        self.assertEqual(cp_4c.__name__.split(".")[-1], "cp_4c")


class TestRun(unittest.TestCase):
    def test_run_passes_every_check_but_the_library_token(self):
        _run, data = built()
        fails = lib.check(data, CTX)
        # "100.0%" is the Model's own EV percentage (lib), also a CZR token; nothing in larchmere/ emits it.
        self.assertEqual([f for f in fails if "CZR figure 100.0" not in f], [])

    def test_skips_and_blocked_module(self):
        _run, data = built()
        self.assertEqual(data["steps"]["CP-8"]["status"], "skipped")
        self.assertEqual(data["steps"]["CP-DR"]["status"], "skipped")
        self.assertEqual(data["handoffs"]["CP-2H"]["qa_status"], "Blocked")
        for r in rows(data, "CP-2H", "cp2h.rating_triggers"):
            self.assertEqual(r["threshold"], "—")
        self.assertTrue(data["fixture"]["issuer_fictional"])

    def test_gate_and_covenant_states(self):
        _run, data = built()
        gate = {r["trigger"]: r["status"] for r in rows(data, "CP-4C", "cp4c.distress_gate")}
        self.assertEqual(gate["Overall: distress gate"], "Met")
        self.assertEqual(
            {r["status"] for r in rows(data, "CP-4", "cp4.covenant_tests")},
            {"Breached", "Tight", "Headroom"},
        )
        shown = {b["id"]: b["shown"] for b in data["front_page_blocks"]}
        self.assertTrue(shown["distressed_restructuring.9"])

    def test_projection_equals_cp2g_movements(self):
        _run, data = built()
        proj = {
            (r["case"], r["fiscal_year"]): r
            for r in rows(data, "PROJECTION", "model.projection_summary")
        }
        self.assertEqual({k[0] for k in proj}, {"BASE", "DOWNSIDE"})
        for m in rows(data, "CP-2G", "cp2g.forecast_movements"):
            year = m["period_id"][2:6]
            self.assertEqual(
                Decimal(m["revenue"]).quantize(Decimal(1)),
                Decimal(proj[(m["case"], year)]["revenue"]),
            )
        # NEW-1's net proceeds lift FY2026E above the 50 floor; both cases are below it from FY2027E
        for case in ("BASE", "DOWNSIDE"):
            self.assertGreater(Decimal(proj[(case, "2026")]["liquidity"]), 50)
            self.assertLess(Decimal(proj[(case, "2027")]["liquidity"]), 50)

    def test_forward_ebitda_lies_between_the_projected_years(self):
        _run, data = built()
        proj = {
            (r["case"], r["fiscal_year"]): D(r["adjusted_ebitda"])
            for r in rows(data, "PROJECTION", "model.projection_summary")
        }
        fwd = D(F.val("forward_12m")["adjusted_ebitda"])
        self.assertTrue(proj[("BASE", "2027")] < fwd < proj[("BASE", "2026")])

    def test_portfolio_fit_breaches_and_caps_at_avoid(self):
        _run, data = built()
        fit_rows = rows(data, "FIT", "snapshot.portfolio_fit")
        self.assertEqual({r["verdict"] for r in fit_rows}, {"Breaches"})
        self.assertEqual({r["recommendation_cap"] for r in fit_rows}, {"Avoid"})
        self.assertEqual({r["current_exposure_pct_nav_pct"] for r in fit_rows}, {"2.80%"})
        rec = {
            r["instrument"]: r["final"] for r in rows(data, "CP-6", "cp6.portfolio_recommendation")
        }
        self.assertEqual(rec["First-Lien Term Loan B"], "Avoid")

    def test_new_money_is_one_new_tranche_across_brief_model_talk_and_fit(self):
        _run, data = built()
        self.assertTrue(data["primary"])
        nm = F.val("new_money")
        t = data["run_brief"]["tables"]["snapshot.transaction_summary"]
        tr = [dict(zip(t["columns"], r, strict=True)) for r in t["rows"]]
        self.assertEqual([r["tranche_id"] for r in tr], ["NEW-1"])
        self.assertEqual(tr[0]["size"], str(nm["size"]))
        self.assertEqual(tr[0]["talk_stage"], "Initial talk")
        pf = {
            r["adjustment_id"]: r for r in rows(data, "CP-1", "cp1.pro_forma_adjustment_register")
        }
        self.assertEqual(pf["PF-NEW-1-DEBT"]["metric_id"], "facility:NEW-1")
        self.assertEqual(Decimal(pf["PF-NEW-1-DEBT"]["value"]), D(nm["size"]))
        self.assertEqual(Decimal(pf["PF-CASH"]["value"]), D(nm["size"]) * D(nm["oid"]) / 100)
        summary = {r["line_id"]: r for r in rows(data, "MODEL", "model.summary")}
        self.assertEqual(
            Decimal(summary["cash_closing"]["pf_ltm"]),
            Decimal(summary["cash_closing"]["ltm"]) + Decimal(pf["PF-CASH"]["value"]),
        )
        # PF-LTM Adjusted EBITDA stays on the SSIM basis (the rejected run-rate savings stay out)
        self.assertEqual(summary["adjusted_ebitda"]["pf_ltm"], summary["adjusted_ebitda"]["ltm"])
        self.assertEqual(
            [r["facility_id"] for r in rows(data, "CP-3", "cp3.talk_valuation")], ["NEW-1"]
        )
        self.assertIn(
            "NEW-1", {r["facility_id"] for r in rows(data, "FIT", "snapshot.portfolio_fit")}
        )

    def test_sources_cite_only_synthetic_rows(self):
        _run, data = built()
        for step, h in data["handoffs"].items():
            for c in h["citations"]:
                self.assertTrue(c["synthetic"], (step, c["id"]))
                self.assertTrue(c["source"].startswith("TEST DATA"))


if __name__ == "__main__":
    unittest.main()
