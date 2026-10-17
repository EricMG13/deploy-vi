"""Tests for the CZR part-2 modules (CP-3, CP-3C, CP-3D, CP-4, CP-4C, CP-5, CP-6, CP-8, CP-DR, CP-L10), the Prior Case,
the Indexed HY portfolio and the three hooks in `run_brief.py` and `cp_1.py`.

Each run is built through the generator's own `Run.build` (the real pipeline, so the hooks and the Model are exercised)
and the figures introduced here (pro forma debt and interest, discount margins, talk valuation, funding gap, creditor
exposure, covenant headroom, capacity, implied hazard, Fit caps, the prior LTM) are recomputed from their inputs."""

from __future__ import annotations

import importlib
import importlib.util
import sys
import unittest
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import lib  # noqa: E402
from core import CORPUS_DIR, D, q  # noqa: E402
from fit import weaker  # noqa: E402

CTX = lib.load_ctx() if CORPUS_DIR.is_dir() else None
needs_corpus = unittest.skipUnless(CTX, "corpus not available")

MINE = ["CP-3", "CP-3C", "CP-3D", "CP-4", "CP-4C", "CP-5", "CP-6", "CP-8", "CP-DR", "CP-L10"]
RUN_NAMES = [
    "czr-full-credit-assessment",
    "czr-full-credit-assessment-quick",
    "czr-earnings-update",
    "czr-relative-value",
    "czr-relative-value-blocked",
    "czr-covenant-refinancing",
    "czr-portfolio-decision",
]
RUNS: dict[str, lib.Run] = {}
NON_PRIMARY_RV = (
    "relative-value-non-primary"  # the Relative Value plan built without the Primary flag
)


def _load_bf():
    spec = importlib.util.spec_from_file_location("build_fixtures_p2", HERE / "build-fixtures.py")
    bf = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(bf)  # type: ignore[union-attr]
    return bf


def build_run(name: str, primary: bool | None = None) -> lib.Run:
    """The Run after `Run.build` (the generator's own assembly), without serialising other agents' handoffs."""
    bf = _load_bf()
    cfg = bf.RUNS[name]
    portfolios = [bf._load(p)(CTX) for p in cfg.get("portfolios", [])]
    prior = bf._load(cfg["prior"])(CTX) if cfg.get("prior") else None
    plan = CTX.spec["pathways"][cfg["pathway"]]["depths"][cfg["depth"]]
    builders = {}
    for step in plan:
        if step not in ("MODEL", "PROJECTION", "FIT"):
            builders[step] = importlib.import_module(f"czr.{lib.slug(step)}").build
    rb = importlib.import_module("czr.run_brief")
    run = lib.Run(
        CTX,
        name,
        cfg["run_id"],
        cfg["pathway"],
        cfg["depth"],
        cfg["issuer"],
        primary=cfg.get("primary", False) if primary is None else primary,
        variant=cfg["variant"],
        portfolios=portfolios,
        fit_exclude=tuple(cfg.get("fit_exclude", ())),
        deep_research=cfg.get("deep_research", True),
        prior_case=prior,
        n_a_charts=dict(cfg.get("n_a_charts", {})),
    )
    run.build(
        builders,
        lambda c, rid, var: rb.build(c, rid, var, pathway=cfg["pathway"], depth=cfg["depth"]),
    )
    return run


def setUpModule() -> None:
    if CTX:
        for n in RUN_NAMES:
            RUNS[n] = build_run(n)
        RUNS[NON_PRIMARY_RV] = build_run("czr-relative-value", primary=False)


def rows(run: lib.Run, step: str, table: str) -> list[dict]:
    return run.handoffs[step].rows(table)


@needs_corpus
class TestHandoffs(unittest.TestCase):
    def test_every_part2_handoff_validates(self):
        for name, run in RUNS.items():
            for step in MINE:
                if step in run.handoffs:
                    self.assertEqual(run.handoffs[step].problems(), [], f"{name} {step}")

    def test_modules_present_in_the_expected_runs(self):
        self.assertIn("CP-8", RUNS["czr-earnings-update"].handoffs)
        self.assertNotIn("CP-8", RUNS["czr-full-credit-assessment"].handoffs)
        self.assertIn("CP-L10", RUNS["czr-full-credit-assessment-quick"].handoffs)
        self.assertEqual(RUNS["czr-relative-value-blocked"].handoffs["CP-3D"].qa_status, "Blocked")
        for n in ("czr-relative-value", "czr-full-credit-assessment"):
            self.assertEqual(RUNS[n].handoffs["CP-3D"].qa_status, "Restricted")


@needs_corpus
class TestHooks(unittest.TestCase):
    def test_primary_runs_carry_the_three_synthetic_tranches(self):
        primary_runs = (
            "czr-full-credit-assessment",
            "czr-full-credit-assessment-quick",
            "czr-relative-value",
            "czr-relative-value-blocked",
            "czr-covenant-refinancing",
            "czr-portfolio-decision",
        )
        for n in primary_runs:
            ts = RUNS[n].run_brief.rows("snapshot.transaction_summary")
            self.assertEqual([t["tranche_id"] for t in ts], ["NEW-1", "NEW-2", "NEW-3"])
            self.assertEqual(sum(D(t["size"]) for t in ts), Decimal(5000))
            self.assertEqual(RUNS[n].run_brief.rows("snapshot.run_header")[0]["primary"], "Yes")
        for n in ("czr-earnings-update", NON_PRIMARY_RV):
            self.assertEqual(RUNS[n].run_brief.rows("snapshot.transaction_summary"), [], n)
            self.assertEqual(RUNS[n].run_brief.rows("snapshot.run_header")[0]["primary"], "No")

    def test_merger_debt_wording_follows_the_primary_flag(self):
        stale = "PF-LTM equals LTM"
        for n in ("czr-full-credit-assessment", "czr-relative-value", "czr-portfolio-decision"):
            self.assertNotIn(stale, RUNS[n].handoffs["CP-1"].gaps_md, n)
            self.assertIn("three synthetic tranches", RUNS[n].handoffs["CP-1"].gaps_md, n)
            self.assertIn("(G8, G21)", RUNS[n].handoffs["CP-1"].gaps_md, n)
        self.assertIn(stale, RUNS[NON_PRIMARY_RV].handoffs["CP-1"].gaps_md)
        self.assertNotIn("three synthetic tranches", RUNS[NON_PRIMARY_RV].handoffs["CP-1"].gaps_md)

    def test_pro_forma_debt_and_interest_tie_into_the_model(self):
        run = RUNS["czr-full-credit-assessment"]
        pf = rows(run, "CP-1", "cp1.pro_forma_adjustment_register")
        self.assertEqual(
            sum(D(r["value"]) for r in pf if r["metric_id"].startswith("facility:")), Decimal(5000)
        )
        interest = sum(D(r["value"]) for r in pf if r["metric_id"] == "cash_interest_paid")
        self.assertEqual(interest, Decimal("-381.9"))  # 182.5 + 110.6 + 88.8 at the talk mid
        tot = {r["line"]: r for r in rows(run, "MODEL", "snapshot.capital_structure_totals")}
        self.assertEqual(tot["Total debt"]["amount"], "16807")
        self.assertEqual(tot["Senior secured debt"]["amount"], "13468")
        self.assertEqual(tot["PF interest"]["amount"], "1157.9")  # 776 LTM + 381.9
        self.assertEqual(
            rows(RUNS[NON_PRIMARY_RV], "CP-1", "cp1.pro_forma_adjustment_register"), []
        )

    def test_variant_handling_in_the_run_brief(self):
        eu = RUNS["czr-earnings-update"].run_brief
        self.assertEqual(len(eu.rows("brief.prior_case")), 1)
        self.assertEqual(eu.rows("brief.approval")[0]["prior_case"], "Yes")
        self.assertEqual(RUNS["czr-covenant-refinancing"].run_brief.rows("brief.prior_case"), [])
        self.assertEqual(
            [
                r["portfolio_id"]
                for r in RUNS["czr-portfolio-decision"].run_brief.rows("brief.portfolios")
            ],
            ["TEST_CLO_I", "TEST_HY_I"],
        )
        self.assertEqual(RUNS["czr-earnings-update"].run_brief.rows("brief.portfolios"), [])
        full = RUNS["czr-full-credit-assessment"].run_brief
        self.assertEqual(
            [r["question_id"] for r in full.rows("brief.research_questions")], ["RQ1", "RQ2", "RQ3"]
        )
        self.assertEqual(
            RUNS["czr-full-credit-assessment-quick"].run_brief.rows("brief.research_questions"), []
        )


@needs_corpus
class TestCp3(unittest.TestCase):
    def test_loan_discount_margins_recompute_from_the_marks(self):
        levels = {
            r["facility_id"]: r
            for r in rows(RUNS["czr-relative-value"], "CP-3", "snapshot.instrument_levels")
        }
        for fid, margin in (("cei_term_b", 225), ("cei_term_b1", 225), ("cei_term_a", 235)):
            r = levels[fid]
            mid = (D(r["bid"]) + D(r["ask"])) / 2
            self.assertEqual(D(r["mid"]), mid)
            self.assertEqual(D(r["yield_or_dm"]), q(margin + (100 - mid) / 3 * 100, 0))
        self.assertEqual(levels["cei_term_b"]["yield_or_dm"], "242")

    def test_trace_levels_are_the_real_last_trades(self):
        levels = {
            r["facility_id"]: r
            for r in rows(RUNS[NON_PRIMARY_RV], "CP-3", "snapshot.instrument_levels")
        }
        self.assertEqual(
            (levels["cei_secured_2032"]["mid"], levels["cei_secured_2032"]["yield_or_dm"]),
            ("93.28", "8.06352"),
        )
        self.assertEqual(
            (levels["cei_unsecured_2032"]["mid"], levels["cei_unsecured_2032"]["yield_or_dm"]),
            ("84.94", "9.318398"),
        )
        self.assertTrue(all(r["level_basis"] == "Market" for r in levels.values()))

    def test_talk_valuation_is_calculated_and_primary_only(self):
        run = RUNS["czr-full-credit-assessment"]
        tv = {r["facility_id"]: r for r in rows(run, "CP-3", "cp3.talk_valuation")}
        self.assertEqual(
            [tv["NEW-1"][k] for k in ("implied_low", "implied_mid", "implied_high")],
            ["308", "333", "358"],
        )
        self.assertEqual(
            [tv["NEW-2"][k] for k in ("implied_low", "implied_mid", "implied_high")],
            ["7.250", "7.375", "7.500"],
        )
        self.assertEqual(tv["NEW-1"]["verdict"], "V2 - Attractive")
        self.assertEqual(tv["NEW-2"]["verdict"], "V4 - Unattractive")
        self.assertEqual(tv["NEW-3"]["verdict"], "V3 - Fair")
        lv = {r["facility_id"]: r for r in rows(run, "CP-3", "snapshot.instrument_levels")}
        for tid in tv:
            self.assertEqual(lv[tid]["level_basis"], "Talk")
            self.assertEqual(
                lv[tid]["yield_or_dm"],
                tv[tid]["implied_mid"].rstrip("0").rstrip(".")
                if "." in tv[tid]["implied_mid"]
                else tv[tid]["implied_mid"],
            )
        self.assertEqual(rows(RUNS[NON_PRIMARY_RV], "CP-3", "cp3.talk_valuation"), [])
        for n in ("czr-relative-value", "czr-relative-value-blocked", "czr-portfolio-decision"):
            self.assertEqual(
                [r["facility_id"] for r in rows(RUNS[n], "CP-3", "cp3.talk_valuation")],
                ["NEW-1", "NEW-2", "NEW-3"],
                n,
            )

    def test_verdict_thresholds(self):
        from czr.cp_3 import verdict_for

        self.assertEqual(verdict_for(Decimal(50)), "V2 - Attractive")
        self.assertEqual(verdict_for(Decimal(49)), "V3 - Fair")
        self.assertEqual(verdict_for(Decimal(-49)), "V3 - Fair")
        self.assertEqual(verdict_for(Decimal(-50)), "V4 - Unattractive")
        self.assertEqual(verdict_for(Decimal(-150)), "V5 - Very unattractive")

    def test_relative_value_blocks_fill_every_chart_series(self):
        rv = rows(RUNS["czr-relative-value"], "CP-3", "snapshot.relative_value")
        blocks = {r["block"] for r in rv}
        self.assertEqual(blocks, {"Loan index", "Loan comparable", "HY index", "HY comparable"})
        hy = [r for r in rv if r["block"] == "HY comparable"]
        self.assertEqual(
            {r["spread_or_dm_bps"] for r in hy if "MGM" in r["name"]}, {"262"}
        )  # (6.722997 - 4.10) x 100
        self.assertEqual(
            next(r for r in hy if "Secured" in r["name"])["market_value"], "1399.2"
        )  # 1,500 x 93.28 / 100


@needs_corpus
class TestCp3cAndCp3d(unittest.TestCase):
    def test_funding_gap_recomputes_and_ties_to_the_front_pages_figures(self):
        mp = rows(RUNS["czr-covenant-refinancing"], "CP-3C", "cp3c.maturity_pressure")
        for r in mp:
            self.assertEqual(
                D(r["funding_gap"]),
                max(D(r["maturing_amount"]) - D(r["sources_available"]), Decimal(0)),
            )
        gaps = {r["fiscal_year"]: r["funding_gap"] for r in mp}
        self.assertEqual((gaps["2028"], gaps["2029"], gaps["2030"]), ("138", "1712", "5674"))
        self.assertEqual(
            mp[-1]["maturing_amount"], "16807"
        )  # 11,807 scheduled plus the 5,000 merger tranches

    def test_creditor_exposure_by_case(self):
        ce = {
            (r["creditor_class"], r["case_name"]): D(r["exposure"])
            for r in rows(RUNS["czr-covenant-refinancing"], "CP-3C", "cp3c.creditor_exposure")
        }
        self.assertEqual(ce[("Senior secured", "Base")], 9468)
        self.assertEqual(ce[("Senior secured", "Stress")], 9468 + 2500 + 1500)
        self.assertEqual(ce[("Senior secured", "LME")], 9468 + 6696)
        self.assertEqual(ce[("Senior unsecured", "Base")], 9468 + 2300)
        self.assertEqual(ce[("Senior unsecured", "Stress")], 9468 + 2300 + 5000)
        self.assertEqual(ce[("Senior unsecured", "LME")], 9468 + 2300 + 6696)

    def test_implied_hazard_is_the_credit_triangle(self):
        ob = {
            r["security_id"]: r
            for r in rows(RUNS["czr-relative-value"], "CP-3D", "cp3d.observations")
        }
        for r in rows(RUNS["czr-relative-value"], "CP-3D", "cp3d.implied_risk"):
            spread = D(ob[r["security_id"]]["spread_or_dm_bps"])
            self.assertEqual(
                D(r["implied_pd_pct"].rstrip("%")), q(spread / 100 / (1 - D("0.4")), 1)
            )
            self.assertEqual(r["recovery_assumption_pct"], "40%")
        secured = next(
            r
            for r in ob.values()
            if "6.50% secured" in r["security_id"] and r["freshness"] == "Current"
        )
        self.assertEqual(secured["spread_or_dm_bps"], "396")

    def test_the_stale_fund_valuation_is_kept_but_flagged(self):
        fund = next(
            r
            for r in rows(RUNS["czr-relative-value"], "CP-3D", "cp3d.observations")
            if r["freshness"] == "Stale"
        )
        self.assertEqual(
            (fund["price"], fund["quote_type"], fund["level_date"]),
            ("97.623", "Evaluated", "2026-06-30"),
        )
        self.assertEqual(fund["spread_or_dm_bps"], "—")

    def test_blocked_variant_keeps_every_table_with_blank_critical_cells(self):
        h = RUNS["czr-relative-value-blocked"].handoffs["CP-3D"]
        self.assertEqual(h.qa_status, "Blocked")
        for tid in ("cp3d.observations", "cp3d.implied_risk", "cp3d.market_vs_fundamental"):
            self.assertEqual(len(h.tables[tid]["rows"]), 1)
            self.assertTrue(all(c == "—" for c in h.tables[tid]["rows"][0]))
        self.assertIn("Blocked", h.analysis_md)


@needs_corpus
class TestCp4AndCp4c(unittest.TestCase):
    def test_covenant_headroom_status_and_pro_forma(self):
        from czr.cp_4 import status_of

        run = RUNS["czr-covenant-refinancing"]
        tests = {r["test"]: r for r in rows(run, "CP-4", "cp4.covenant_tests")}
        self.assertEqual(len(tests), 9)  # six current tests and three pro forma
        for r in tests.values():
            thr, cur = D(r["threshold"]), D(r["current_value"])
            want = thr - cur if r["direction"] == "Ceiling" else cur - thr
            self.assertEqual(D(r["headroom"]), want)
            self.assertEqual(r["status"], status_of(thr, want))
        tl = tests["Total Leverage Ratio (revolver and Term Loan A)"]
        self.assertEqual(
            (tl["threshold"], tl["current_value"], tl["headroom"]), ("6.50", "3.02", "3.48")
        )
        pf = tests["Pari secured incremental test, pro forma for the merger tranches"]
        self.assertEqual(pf["current_value"], "3.75")  # (9,468 + 2,500 + 1,500) / 3,592
        self.assertEqual(status_of(Decimal(10), Decimal("0.9")), "Tight")
        self.assertEqual(status_of(Decimal(10), Decimal("-0.1")), "Breached")

    def test_capacity_remaining_is_size_less_used(self):
        cap = {
            r["basket"]: r
            for r in rows(RUNS["czr-covenant-refinancing"], "CP-4", "cp4.capacity_register")
        }
        b = cap["Builder basket (cumulative credit)"]
        self.assertEqual((b["used"], b["remaining"]), ("300", "1150"))
        self.assertEqual(cap["Pari secured to 4.50x"]["remaining"], "6696")  # 4.50 x 3,592 - 9,468
        self.assertEqual(cap["Free-and-clear"]["status"], "Not computable")
        for r in cap.values():
            if r["status"] == "Calculated" and r["capacity_type"] != "Debt":
                self.assertEqual(D(r["remaining"]) + D(r["used"]) > 0, True)

    def test_protection_score_overall_reads_as_two(self):
        ps = {
            r["area"]: r["score"]
            for r in rows(RUNS["czr-covenant-refinancing"], "CP-4", "cp4.protection_score")
        }
        self.assertEqual(ps["Overall"], "2")
        self.assertTrue(all(v in "12345" for v in ps.values()))

    def test_cp4c_gate_is_not_met_and_the_registers_say_so(self):
        run = RUNS["czr-full-credit-assessment"]
        h = run.handoffs["CP-4C"]
        gate = {r["trigger"]: r["status"] for r in h.rows("cp4c.distress_gate")}
        self.assertEqual(gate["Overall"], "Not met")
        self.assertNotIn("Met", gate.values())
        for tid in ("cp4c.claims_register", "cp4c.ev_scenarios", "cp4c.recoveries", "cp4c.paths"):
            rs = h.rows(tid)
            self.assertEqual(len(rs), 1)
            self.assertEqual(next(iter(rs[0].values())), "Gate not met")
        block = next(b for b in run.blocks() if b["id"] == "credit_snapshot.1")
        self.assertTrue(block["shown"])


@needs_corpus
class TestCp5Cp6(unittest.TestCase):
    def test_module_status_matches_the_handoffs_and_names_every_restricted_module(self):
        for name, run in RUNS.items():
            status = {
                r["module_id"]: r["qa_status"] for r in rows(run, "CP-5", "cp5.module_status")
            }
            for step, h in run.handoffs.items():
                if step in status:
                    self.assertEqual(status[step], h.qa_status, f"{name} {step}")
            unforeseen = [u for u in run.limitations()["unforeseen"] if "named by no cp5" in u]
            self.assertEqual(unforeseen, [], name)

    def test_findings_are_present_in_every_run(self):
        for name, run in RUNS.items():
            self.assertGreaterEqual(len(rows(run, "CP-5", "cp5.findings")), 3, name)

    def test_blocked_run_reports_the_cross_module_disagreement(self):
        fs = rows(RUNS["czr-relative-value-blocked"], "CP-5", "cp5.findings")
        self.assertTrue(
            any(
                f["module_id"] == "CP-3" and f["kind"] == "Consistency" and f["severity"] == "High"
                for f in fs
            )
        )

    def test_final_recommendation_is_the_weaker_of_uncapped_and_cap(self):
        for name in ("czr-full-credit-assessment", "czr-portfolio-decision", "czr-relative-value"):
            for r in rows(RUNS[name], "CP-6", "cp6.portfolio_recommendation"):
                self.assertEqual(r["final"], weaker(r["uncapped"], r["cap"]))

    def test_the_breaches_state_in_the_portfolio_run(self):
        run = RUNS["czr-portfolio-decision"]
        fit = {
            (r["portfolio_id"], r["facility_id"]): r
            for r in run.handoffs["FIT"].rows("snapshot.portfolio_fit")
        }
        br = fit[("TEST_HY_I", "cei_unsecured_2032")]
        self.assertEqual(
            (br["verdict"], br["recommendation_cap"], br["binding_limit"]),
            ("Breaches", "Avoid", "H-02"),
        )
        self.assertEqual(
            [k for k, r in fit.items() if r["verdict"] == "Breaches"],
            [("TEST_HY_I", "cei_unsecured_2032")],
        )
        rec = next(
            r
            for r in rows(run, "CP-6", "cp6.portfolio_recommendation")
            if r["fit_verdict"] == "Breaches"
        )
        self.assertEqual((rec["uncapped"], rec["final"]), ("4 - Modest UW", "Avoid"))

    def test_indexed_hy_book_exposure_and_headroom(self):
        from czr.portfolios import indexed_hy

        p = indexed_hy(CTX)
        self.assertEqual(sum(D(x["market_value_usd"]) for x in p["positions"]), Decimal(2891593))
        r = next(
            x
            for x in RUNS["czr-portfolio-decision"].handoffs["FIT"].rows("snapshot.portfolio_fit")
            if x["portfolio_id"] == "TEST_HY_I" and x["facility_id"] == "cei_secured_2032"
        )
        self.assertEqual(
            (r["current_exposure"], r["current_exposure_pct_nav_pct"], r["max_size"]),
            ("2.892", "0.59%", "2.024"),
        )

    def test_strategy_recommendations_and_basis(self):
        full = {
            r["strategy"]: r
            for r in rows(RUNS["czr-full-credit-assessment"], "CP-6", "snapshot.recommendation")
        }
        self.assertEqual(
            [full[s]["recommendation"] for s in ("CLO", "Indexed Loans", "Indexed HY")],
            ["3 - MW", "3 - MW", "2 - Modest OW"],
        )
        self.assertTrue(all(r["basis"] == "Full" for r in full.values()))
        quick = rows(RUNS["czr-full-credit-assessment-quick"], "CP-6", "snapshot.recommendation")
        self.assertTrue(all(r["basis"] == "Screening" for r in quick))


@needs_corpus
class TestCp8CpDrCpL10(unittest.TestCase):
    def test_prior_ltm_is_real_and_the_diff_ties_to_what_changed(self):
        run = RUNS["czr-earnings-update"]
        from run import diff_tables

        diff = diff_tables(run.prior_case["tables"], run.all_tables())["changes"]
        num = {
            (c["key"], c["field"]): c
            for c in diff
            if c["table"] == "snapshot.financials" and c["kind"] == "changed"
        }
        self.assertEqual(
            (num[("revenue", "ltm")]["prior"], num[("revenue", "ltm")]["current"]),
            ("11562", "11648"),
        )
        self.assertEqual(
            (num[("adjusted_ebitda", "ltm")]["prior"], num[("adjusted_ebitda", "ltm")]["current"]),
            ("3627", "3592"),
        )
        self.assertEqual(D("11648") - D("11562"), Decimal(86))  # equals the real Q2 revenue change
        self.assertEqual(
            D("3592") - D("3627"), Decimal(-35)
        )  # equals the real Q2 Adjusted EBITDA change
        wc = rows(run, "CP-8", "cp8.what_changed")
        by = {r["field"]: r for r in wc}
        self.assertEqual(
            (
                by["Credit Direction"]["prior_value"],
                by["Credit Direction"]["current_value"],
                by["Credit Direction"]["change"],
            ),
            ("Stable", "Deteriorating", "Deteriorated"),
        )
        self.assertEqual(by["Net leverage, LTM (x)"]["change"], "Improved")
        self.assertEqual(by["Adjusted EBITDA, LTM (US$ m)"]["change"], "Deteriorated")
        self.assertEqual(by["Cash and revolver capacity (US$ m)"]["prior_value"], "3050")
        self.assertEqual(
            {r["change"] for r in wc} - {"Improved", "Unchanged", "Deteriorated", "New", "Removed"},
            set(),
        )

    def test_thesis_review_has_parseable_expected_and_realised_pairs(self):
        tr = rows(RUNS["czr-earnings-update"], "CP-8", "cp8.thesis_review")
        nums = [
            r
            for r in tr
            if r["expected"].rstrip("%x").replace(".", "").isdigit()
            and r["realised"].rstrip("%x").replace(".", "").isdigit()
        ]
        self.assertGreaterEqual(len(nums), 3)
        self.assertEqual(
            {
                r["current"]
                for r in rows(RUNS["czr-earnings-update"], "CP-8", "cp8.recommendation_change")
            },
            {"N/A"},
        )

    def test_cp8_prior_case_block(self):
        pc = RUNS["czr-earnings-update"].prior_case
        self.assertEqual(
            (pc["report_date"], pc["pathway"], pc["depth"]),
            ("2026-08-05", "EARNINGS_UPDATE", "full"),
        )
        self.assertEqual(pc["run_id"], "FIX-CZR-EU-Q1-2026")

    def test_deep_research_states(self):
        h = RUNS["czr-full-credit-assessment"].handoffs["CP-DR"]
        st = {r["question_id"]: r["status"] for r in h.rows("cpdr.questions")}
        self.assertEqual(st, {"RQ1": "Answered", "RQ2": "Answered", "RQ3": "Unanswered"})
        ans = {r["question_id"]: r for r in h.rows("cpdr.answers")}
        self.assertTrue(ans["RQ3"]["answer"].startswith("Unresolved"))
        fetched = [r for r in h.rows("cpdr.evidence") if r["source_type"] == "Fetched"]
        self.assertTrue(fetched and all("(synthetic)" in r["claim"] for r in fetched))
        syn = [c for c in h.citations if c["synthetic"]]
        self.assertEqual(len(syn), 4)

    def test_screen_topics_cover_every_family_and_follow_the_rules(self):
        topics = rows(RUNS["czr-full-credit-assessment-quick"], "CP-L10", "cpl10.screen_topics")
        self.assertEqual({r["family"] for r in topics}, set(CTX.spec["scales"]["screen_family"]))
        for r in topics:
            if r["materiality"] == "High" and r["evidence_status"] in ("Missing", "Conflicted"):
                self.assertEqual(r["disposition"], "Gap only")
            if r["disposition"] == "Immaterial":
                self.assertEqual(r["evidence_status"], "Sufficient")
        self.assertEqual(len({r["priority_rank"] for r in topics}), len(topics))
        cv = rows(RUNS["czr-full-credit-assessment-quick"], "CP-L10", "snapshot.credit_view")[0]
        self.assertEqual((cv["basis"], cv["confidence"]), ("Screening", "Low"))


if __name__ == "__main__":
    unittest.main()
