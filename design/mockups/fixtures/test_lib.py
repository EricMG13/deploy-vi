"""Tests for the fixture generator core: spec parsing, formatting, table validation, citations, Fit, Model, runs."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import core  # noqa: E402
import lib  # noqa: E402
from core import CORPUS_DIR, check_calc_string, compute, fbps, fpct, fx, plain  # noqa: E402

CTX = lib.load_ctx() if CORPUS_DIR.is_dir() else None
needs_corpus = unittest.skipUnless(CTX, "corpus not available")


def czr_handoffs(primary: bool = False):
    """The CZR Run Brief and CP-1. Non-Primary by default (no merger tranches, so no PF-LTM column); the Primary flag is
    the run's own, set on the context the way `Run.build` sets it."""
    from czr import cp_1, run_brief

    CTX.primary_runs["T1"] = primary
    rb = run_brief.build(CTX, "T1", "rv")
    return rb, cp_1.build(CTX, "T1", "rv")


class TestFormatting(unittest.TestCase):
    def test_plain_and_suffixes(self):
        self.assertEqual(plain(Decimal("-0.001"), 2), "0.00")
        self.assertEqual(plain("(1,264)"), "-1264")
        self.assertEqual(plain(Decimal("2.50")), "2.5")
        self.assertEqual(fx(Decimal("3.2870267")), "3.29x")
        self.assertEqual(fpct(Decimal("12.45"), 1), "12.5%")  # half up
        self.assertEqual(fbps(Decimal("450.4")), "450")

    def test_compute_roundtrip_and_tamper(self):
        v, s = compute("leverage", "debt / ebitda", 2, "x", debt=11807, ebitda=3592)
        self.assertEqual(v, Decimal("3.29"))
        self.assertIsNone(check_calc_string(s))
        self.assertIn("recomputes", check_calc_string(s.replace("= 3.29x", "= 3.30x")))
        v, s = compute("neg", "a + b", 0, "", a=-5, b=2)
        self.assertIn("(-5)", s)
        self.assertIsNone(check_calc_string(s))

    def test_safe_eval_refuses_code(self):
        from core import FixtureError, safe_eval

        with self.assertRaises(FixtureError):
            safe_eval("__import__('os')")


@needs_corpus
class TestSpec(unittest.TestCase):
    def test_catalogue_counts_and_shape(self):
        t = CTX.spec["tables"]
        self.assertEqual(len(t), 125)
        self.assertEqual(sum(1 for x in t.values() if x["host"]), 22)
        c = t["cp1.model_period_register"]
        self.assertEqual(
            [x["name"] for x in c["columns"]][:3], ["period_id", "fiscal_year", "fiscal_quarter"]
        )
        self.assertTrue(c["columns"][0]["critical"])
        self.assertFalse(c["columns"][2]["critical"])
        self.assertEqual(
            next(x for x in c["columns"] if x["name"] == "period_type")["scale"], "period_type"
        )
        self.assertEqual(t["snapshot.credit_view"]["owners"], ["CP-2", "CP-L10"])
        self.assertEqual(len(t["snapshot.credit_view"]["columns"]), 8)
        self.assertEqual(t["cp2d.runway"]["min_rows"], 4)

    def test_pathways_front_pages_and_charts(self):
        self.assertEqual(len(CTX.spec["pathways"]["FULL_CREDIT_ASSESSMENT"]["depths"]["full"]), 24)
        self.assertEqual(len(CTX.spec["front_pages"]["credit_snapshot"]["blocks"]), 19)
        self.assertEqual(len(CTX.spec["charts"]), 35)
        self.assertIn("model.projection_summary", CTX.spec["charts"]["chart.model_strip"]["reads"])


@needs_corpus
class TestGateNotMet(unittest.TestCase):
    """Interfaces §2.17: `Gate not met` may fill the critical cells of the four CP-4C register tables, only when the
    module's distress gate is Not met."""

    @staticmethod
    def gate(status: str) -> dict:
        t = CTX.spec["tables"]["cp4c.distress_gate"]
        row = {
            "trigger": "Overall",
            "evidence": "e",
            "event_date": "—",
            "status": status,
            "cite": "calc: x",
        }
        return {
            "columns": [c["name"] for c in t["columns"]],
            "rows": [[row.get(c["name"], "—") for c in t["columns"]]],
        }

    @staticmethod
    def recoveries_row(pct: str) -> dict:
        t = CTX.spec["tables"]["cp4c.recoveries"]
        vals = {"recovery_pct": pct, "currency": "USD", "unit": "MILLIONS", "fulcrum": "No"}
        return {
            "columns": [c["name"] for c in t["columns"]],
            "rows": [
                [
                    vals.get(c["name"], "Gate not met" if c["critical"] else "—")
                    for c in t["columns"]
                ]
            ],
        }

    def test_detects_the_gate_from_the_overall_row(self):
        self.assertTrue(core.distress_gate_not_met({"cp4c.distress_gate": self.gate("Not met")}))
        self.assertFalse(core.distress_gate_not_met({"cp4c.distress_gate": self.gate("Met")}))
        self.assertFalse(core.distress_gate_not_met({}))

    def test_literal_is_allowed_only_when_the_gate_is_not_met(self):
        table = self.recoveries_row("Gate not met")
        args = (CTX.spec, "CP-4C", "cp4c.recoveries", table, False)
        self.assertEqual(core.table_problems(*args, gate_not_met=True), [])
        self.assertTrue(
            any("recovery_pct" in p for p in core.table_problems(*args, gate_not_met=False))
        )

    def test_literal_is_not_allowed_in_other_tables_or_non_critical_cells(self):
        col_pct = {"name": "recovery_pct", "critical": True, "scale": None}
        self.assertTrue(core.gate_statement("cp4c.paths", col_pct, "Gate not met"))
        self.assertFalse(core.gate_statement("cp4.covenant_tests", col_pct, "Gate not met"))
        self.assertFalse(
            core.gate_statement("cp4c.paths", {**col_pct, "critical": False}, "Gate not met")
        )
        self.assertFalse(core.gate_statement("cp4c.paths", col_pct, "0%"))
        # a true percentage is still checked when the gate is not met
        bad = self.recoveries_row("12")
        self.assertTrue(core.table_problems(CTX.spec, "CP-4C", "cp4c.recoveries", bad, False, True))


@needs_corpus
class TestFictionalFigures(unittest.TestCase):
    def test_trivial_values_and_digests_are_not_real_figures(self):
        import checks

        toks = checks._czr_figure_tokens(CTX)
        for trivial in ("100.0", "1.0", "0.0"):
            self.assertNotIn(trivial, toks)
        run = {"fixture": {"issuer_fictional": True}, "x": "100.0% " + "ab12" * 16 + " 1,000.0"}
        fails = checks.check_fictional(CTX, run)
        self.assertFalse([f for f in fails if "100.0" in f or "ab12" in f], fails)
        # a real, non-trivial figure is still caught
        real = checks.check_fictional(CTX, {"fixture": {"issuer_fictional": True}, "x": "1487"})
        self.assertTrue([f for f in real if "1487" in f], real)


@needs_corpus
class TestHandoff(unittest.TestCase):
    def mk(self, mod="CP-2"):
        return lib.Handoff(CTX, mod, "CZR", "T1", "2026-10-02")

    def test_scale_format_and_placeholder_rules(self):
        h = self.mk("CP-1B")
        base = {
            "metric_id": "m",
            "current_period_id": "a",
            "reference_period_id": "b",
            "comparison_basis": "YoY",
            "current_value": "1",
            "reference_value": "2",
            "currency": "USD",
            "unit": "MILLIONS",
            "restatement": "No",
            "perimeter_change": "No",
            "cite": "calc: x",
        }
        h.table("cp1b.period_comparison", [base])
        for bad in (
            {"comparison_basis": "Year on year"},
            {"pct_change_pct": "12.5"},
            {"current_value": "1,234"},
            {"current_value": "(5)"},
            {"metric_id": "tbd"},
            {"cite": "no marker"},
        ):
            with self.assertRaises(lib.FixtureError, msg=str(bad)):
                h.table("cp1b.period_comparison", [{**base, **bad}])
        with self.assertRaises(lib.FixtureError):
            h.table("cp1b.period_comparison", [{**base, "nonsense": "1"}])
        with self.assertRaises(lib.FixtureError):
            self.mk("CP-2").table("cp1b.period_comparison", [base])  # owned by CP-1B

    def test_critical_blank_min_rows_and_blocked(self):
        h = self.mk("CP-2")
        h.table(
            "snapshot.credit_view",
            [
                {
                    "credit_score": "3 - Fair",
                    "credit_direction": "Stable",
                    "sector_outlook": "Neutral",
                    "primary_support": "x",
                    "primary_downside": "—",
                    "confidence": "Medium",
                    "basis": "Full",
                    "cite": "calc: x",
                }
            ],
        )
        h.table(
            "snapshot.strengths_weaknesses",
            [{"kind": "Strength", "label": "a", "text": "b", "cite": "calc: c"}],
        )
        h.table("cp2.drivers", [])
        h.table("cp2.watch_items", [])
        h.analysis("text")
        joined = " ".join(h.problems())
        self.assertIn("critical primary_downside is blank", joined)
        self.assertIn("snapshot.strengths_weaknesses: 1 rows, minimum 2", joined)
        self.assertIn("cp2.drivers: 0 rows, minimum 3", joined)
        h.qa("Blocked")
        self.assertEqual(
            h.problems(), []
        )  # Blocked keeps the tables but may blank critical cells and rows

    def test_missing_table_is_reported(self):
        h = self.mk("CP-2")
        h.analysis("x")
        self.assertTrue(any("missing table snapshot.credit_view" in p for p in h.problems()))

    def test_citations_real_synthetic_and_dedupe(self):
        h = self.mk("CP-1")
        m = h.cite_data("C51")
        self.assertEqual(m, h.cite_data("C51"))
        c = h.citations[0]
        self.assertTrue(c["anchored"])
        self.assertFalse(c["synthetic"])
        self.assertIn("Net revenues | 11,486", c["excerpt"])
        s = h.cite_synthetic(
            "tranche-1", "Invented to exercise the pro forma arithmetic.", "Caesars"
        )
        row = h.citations[-1]
        self.assertTrue(row["synthetic"])
        self.assertTrue(
            row["source"].startswith("TEST DATA — invented for design, not a fact about Caesars")
        )
        self.assertTrue(row["locator"].startswith("fixtures/"))
        self.assertNotEqual(m, s)
        with self.assertRaises(lib.FixtureError):
            h.cite_doc("CZR_FY2025_10K.txt", 1, "this text is not on line one")
        with self.assertRaises(lib.FixtureError):
            h.cite_caos("full-credit-assessment-2026-10-06", "CP-1", 999)
        mk = h.cite_caos("full-credit-assessment-2026-10-06", "CP-1", 3)
        self.assertEqual(h.citations[-1]["source"], "CZR_FY2025_10K.txt")
        self.assertIn(mk, h.analysis("see " + mk).analysis_md)

    def test_unresolved_marker_and_unused_citation(self):
        h = self.mk("CP-2")
        h.cite_data("C51")
        h.analysis("claim [C9]")
        joined = " ".join(h.problems())
        self.assertIn("[C9] in text does not resolve", joined)
        self.assertIn("citations never cited", joined)

    def test_base_citations_all_anchor(self):
        for src in (CTX.base["citations"], CTX.fp["citations"]):
            for k, c in src.items():
                if c.get("synthetic") or k.startswith("S"):
                    continue
                CTX.anchor_line(c["file"], c["line"], c["excerpt"])


@needs_corpus
class TestFit(unittest.TestCase):
    def setUp(self):
        self.pf = lib.test_clo_i(CTX)
        base = {
            "sector": "Leisure Facilities & Services",
            "country": "US",
            "asset_type": "Bond",
            "currency": "USD",
            "maturity": "5",
        }
        self.ins = [
            {
                "facility_id": "ssn32",
                "instrument": "6.50% SSN 2032",
                "rating": "B1",
                "seniority": "First lien",
                **base,
            },
            {
                "facility_id": "tlb",
                "instrument": "Term Loan B",
                "rating": None,
                "seniority": "First lien",
                **base,
            },
            {
                "facility_id": "sn32",
                "instrument": "6.00% SN 2032",
                "rating": "Caa1",
                "seniority": "Unsecured",
                **base,
            },
        ]

    def test_spec_values_for_test_clo_i(self):
        r = lib.fit(self.pf, self.ins, "CZR")
        by = {x["facility_id"]: x for x in r.rows}
        self.assertEqual(
            (by["ssn32"]["verdict"], by["ssn32"]["max_size"], by["ssn32"]["binding_limit"]),
            ("Fits", "15773213", "C-01"),
        )
        self.assertEqual(
            (
                by["tlb"]["verdict"],
                by["tlb"]["max_size"],
                by["tlb"]["binding_limit"],
                by["tlb"]["recommendation_cap"],
            ),
            ("Watch", "883300", "C-04", "3 - MW"),
        )
        self.assertEqual(by["sn32"]["max_size"], "883300")  # Caa1 sits in the CCC bucket
        self.assertIn("Unrated", by["tlb"]["reason"])
        lim = {(x["facility_id"], x["limit_id"]): x for x in r.limit_rows}
        self.assertEqual(lim[("tlb", "C-05")]["headroom_amount"], "8012792")
        self.assertEqual(lim[("ssn32", "C-06-LEISURE")]["headroom_amount"], "34259418")
        self.assertEqual(lim[("sn32", "C-10")]["headroom_amount"], "59244186")
        self.assertEqual(lim[("tlb", "C-03")]["status"], "From file")
        self.assertNotIn(("ssn32", "C-04"), lim)  # rated B1 does not touch the CCC bucket

    def test_breach_and_expected_rating_is_unrated(self):
        pf = copy.deepcopy(self.pf)
        pf["positions"] = [
            {"issuer_id": "CZR", "par": "17000000"}
        ]  # 2.69% of NAV against a 2.5% Hard limit
        inst = [{**self.ins[0], "rating": None, "expected_rating": "Ba3 (expected)"}]
        r = lib.fit(pf, inst, "CZR")
        self.assertEqual(r.rows[0]["verdict"], "Breaches")
        self.assertEqual(r.rows[0]["max_size"], "0")
        self.assertEqual(r.rows[0]["recommendation_cap"], "Avoid")
        self.assertIn("expected Ba3 (expected) is not assigned", r.rows[0]["reason"])
        self.assertEqual(lib.rating_bucket("Caa1"), "CCC")
        self.assertEqual(lib.rating_bucket("(P)B1"), "B")
        self.assertEqual(lib.rating_bucket(None), "Unrated")

    def test_soft_breach_and_uncomputed_limit_give_watch(self):
        pf = copy.deepcopy(self.pf)
        next(x for x in pf["limits"] if x["limit_id"] == "C-10")["current_value"] = "10.5"
        r = lib.fit(pf, [self.ins[2]], "CZR")
        self.assertEqual(r.rows[0]["verdict"], "Watch")
        pf2 = copy.deepcopy(self.pf)
        next(x for x in pf2["limits"] if x["limit_id"] == "C-05")["current_value"] = None
        r2 = lib.fit(pf2, [self.ins[1]], "CZR")
        row = next(x for x in r2.limit_rows if x["limit_id"] == "C-05")
        self.assertEqual(row["status"], "Not computed")
        self.assertEqual(r2.rows[0]["verdict"], "Watch")

    def test_headroom_monotone_and_hard_limit_never_improves_verdict(self):
        order = {"Fits": 0, "Watch": 1, "Breaches": 2}
        prev = None
        for lv in ("2.0", "2.5", "3.0", "4.0"):
            pf = copy.deepcopy(self.pf)
            next(x for x in pf["limits"] if x["limit_id"] == "C-04")["limit_value"] = lv
            r = lib.fit(pf, [self.ins[1]], "CZR")
            ha = Decimal(
                next(x for x in r.limit_rows if x["limit_id"] == "C-04")["headroom_amount"]
            )
            self.assertTrue(prev is None or ha >= prev)
            prev = ha
        base = lib.fit(self.pf, [self.ins[0]], "CZR").rows[0]["verdict"]
        pf = copy.deepcopy(self.pf)
        pf["limits"].append(
            {
                "limit_id": "X-1",
                "category": "Sector",
                "parameter": "extra",
                "scope": "sector",
                "scope_value": "Leisure Facilities & Services",
                "limit_value": "4",
                "unit": "pct_nav",
                "limit_kind": "Hard",
                "current_value": "4.57",
                "source": "test",
            }
        )
        self.assertGreaterEqual(
            order[lib.fit(pf, [self.ins[0]], "CZR").rows[0]["verdict"]], order[base]
        )

    def test_weaker_and_cp6_rows(self):
        self.assertEqual(lib.weaker("2 - Modest OW", "3 - MW"), "3 - MW")
        self.assertEqual(lib.weaker("Avoid", "1 - Strong OW"), "Avoid")
        self.assertEqual(lib.weaker("N/A", "3 - MW"), "N/A")
        r = lib.fit(self.pf, self.ins, "CZR")
        rows = lib.cp6_rows(
            r, {"ssn32": "2 - Modest OW", "tlb": "2 - Modest OW", "sn32": "4 - Modest UW"}
        )
        self.assertEqual([x["final"] for x in rows], ["2 - Modest OW", "3 - MW", "4 - Modest UW"])


@needs_corpus
class TestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rb, cls.cp1 = czr_handoffs()
        cls.mb = lib.ModelBuilder(cls.cp1, cls.rb)

    def val(self, line, col=None):
        c = col or self.mb.ltm_col
        return self.mb.L(line, c).value

    def test_ltm_against_base_data(self):
        self.assertEqual(self.val("adjusted_ebitda"), Decimal("3592"))
        self.assertEqual(self.val("total_debt"), Decimal("11807"))
        self.assertEqual(lib.q(self.val("metric:total_leverage_adjusted"), 2), Decimal("3.29"))
        self.assertEqual(lib.q(self.val("metric:net_leverage_adjusted"), 2), Decimal("3.02"))
        self.assertEqual(lib.q(self.val("metric:senior_secured_leverage"), 2), Decimal("2.64"))
        self.assertEqual(self.val("liquidity"), Decimal("2928"))
        ho = self.mb.house()
        self.assertEqual(lib.q(Decimal(ho["ssim_multiple"]["value"]), 2), Decimal("3.29"))
        self.assertEqual(lib.q(Decimal(ho["ev"]["value"]), 0), Decimal("17600"))

    def test_every_base_financial_cell_matches(self):
        run = {"model": self.mb.to_json()}
        self.assertEqual(lib.check.__module__, "checks")
        import checks

        self.assertEqual(checks.check_base(CTX, run), [])
        self.assertEqual(checks.check_model(run["model"]), [])

    def test_check_base_catches_a_changed_figure(self):
        import checks

        m = self.mb.to_json()
        cell = next(
            c
            for ln in m["lines"]
            if ln["line_id"] == "revenue"
            for c in ln["cells"]
            if c["column_id"] == "FY:FY2025"
        )
        cell["value"] = "11487"
        self.assertTrue(any("revenue FY2025" in f for f in checks.check_base(CTX, {"model": m})))

    def test_nulls_carry_reasons_never_zero(self):
        fy23 = next(c for c in self.mb.cols if c.period_id == "FY2023")
        c = self.mb.L("total_debt", fy23)
        self.assertIsNone(c.value)
        self.assertEqual(c.reason, "COMPONENT_MISSING")
        self.assertEqual(self.mb.L("gross_profit", self.mb.ltm_col).reason, "COMPONENT_MISSING")
        self.assertEqual(
            self.mb.L(
                "metric:total_leverage_adjusted", next(c for c in self.mb.cols if c.kind == "YTD")
            ).reason,
            "NOT_APPLICABLE",
        )
        for ln in self.mb.to_json()["lines"]:
            for cell in ln["cells"]:
                self.assertTrue(
                    ("value" in cell) != ("reason" in cell and cell["reason"] is not None),
                    (ln["line_id"], cell["column_id"]),
                )

    def test_bridge_reconciles_and_adjusted_is_stated(self):
        for p in ("FY2023", "FY2024", "FY2025", "H1_2026", "LTM_Q2_2026"):
            col = next(c for c in self.mb.cols if c.period_id == p)
            adj = self.mb.L("adjusted_ebitda", col)
            self.assertEqual(adj.value, adj.stated)
        self.assertEqual([x[0] for x in self.mb.limits if x[0] == "ADJ_EBITDA_BRIDGE_RESIDUAL"], [])

    def test_unrealized_addback_is_left_out_column_by_column(self):
        rows = self.cp1.rows("cp1.adjusted_ebitda_bridge")
        cp1d = lib.Handoff(CTX, "CP-1D", "CZR", "T1", "2026-10-02", ["CP-1"])
        m = cp1d.cite_synthetic("a1", "Invented rejection to test the house exclusion.", "Caesars")
        cp1d.table(
            "cp1d.addback_assessment",
            [
                {
                    "addback_id": "sbc",
                    "period_id": "LTM_Q2_2026",
                    "amount": "92",
                    "currency": "USD",
                    "unit": "MILLIONS",
                    "category": "SBC",
                    "house_realization_status": "UNREALIZED",
                    "verdict": "Rejected",
                    "rationale": "x",
                    "recurrence": "Recurring",
                    "cite": m,
                }
            ],
        )
        cp1d.table(
            "cp1d.debt_like_items",
            [
                {
                    "item": "Finance leases",
                    "amount": "147",
                    "currency": "USD",
                    "unit": "MILLIONS",
                    "period_id": "JUN30_2026",
                    "treatment": "Debt-like",
                    "basis": "x",
                    "cite": m,
                }
            ],
        )
        mb = lib.ModelBuilder(self.cp1, self.rb, cp1d)
        self.assertEqual(mb.L("adjusted_ebitda", mb.ltm_col).value, Decimal("3500"))  # 3,592 - 92
        self.assertEqual(mb.L("structuring_ebitda", mb.ltm_col).value, Decimal("3592"))
        self.assertEqual(mb.L("adjusted_ebitda", mb.ltm_col).stated, Decimal("3592"))
        fy25 = next(c for c in mb.cols if c.period_id == "FY2025")
        self.assertEqual(
            mb.L("adjusted_ebitda", fy25).value, Decimal("3529")
        )  # the newest-LTM assessment controls that add-back in every column (3,624 - 95)
        self.assertTrue(rows)
        self.assertEqual(Decimal(mb.house()["adjusted_debt"]["value"]), Decimal("11954"))

    def _with_pf(self):
        rb, h = czr_handoffs()
        m = h.cite_synthetic(
            "NEW-1", "Invented 1,000 term loan used only to test pro forma arithmetic.", "Caesars"
        )
        fac = h.rows("cp1.debt_facility_register")
        fac.append(
            {
                **fac[-1],
                "facility_id": "NEW-1",
                "facility_name": "New TLB (test)",
                "period_id": "JUN30_2026",
                "facility_type": "Term loan",
                "carrying_value": "0",
                "drawn_amount": "0",
                "secured_status": "SECURED",
                "seniority": "Senior secured",
                "margin_or_coupon": "Term SOFR + 3.50%",
                "reference_rate": "Term SOFR",
                "spread_bps": "350",
                "floor_bps": "50",
                "fixed_rate": "—",
                "maturity_date": "2032-06-30",
                "source_id": m,
                "source_locator": "test",
                "annual_amortisation": "—",
                "commitment": "—",
            }
        )
        h.table("cp1.debt_facility_register", fac)
        pf = [
            dict(
                adjustment_id="A1",
                label="New TLB",
                period_id="LTM_Q2_2026",
                effective_date="2026-10-01",
                classification="NEW_DEBT",
                metric_id="facility:NEW-1",
                value="1000",
                source_id=m,
                source_locator="t",
            ),
            dict(
                adjustment_id="A2",
                label="Interest",
                period_id="LTM_Q2_2026",
                effective_date="2026-10-01",
                classification="INTEREST",
                metric_id="cash_interest_paid",
                value="-70",
                source_id=m,
                source_locator="t",
            ),
            dict(
                adjustment_id="A3",
                label="Cash",
                period_id="LTM_Q2_2026",
                effective_date="2026-10-01",
                classification="CASH",
                metric_id="cash_and_equivalents",
                value="1000",
                source_id=m,
                source_locator="t",
            ),
        ]
        h.table("cp1.pro_forma_adjustment_register", pf)
        return rb, h

    def test_pro_forma_column(self):
        rb, h = self._with_pf()
        mb = lib.ModelBuilder(h, rb)
        pf = mb.pf_col
        self.assertEqual(pf.label, "PF-LTM")
        self.assertEqual(mb.L("total_debt", pf).value, Decimal("12807"))
        self.assertEqual(mb.L("cash_closing", pf).value, Decimal("1965"))
        self.assertEqual(mb.L("cash_interest", pf).value, Decimal("-846"))
        self.assertEqual(mb.L("net_debt", pf).value, Decimal("10842"))
        self.assertEqual(mb.snapshot_columns()["LTM"], pf.column_id)
        self.assertEqual(
            lib.q(Decimal(mb.house()["pf_interest_cover"]["value"]), 2),
            lib.q(Decimal(3592) / Decimal(846), 2),
        )
        self.assertEqual(mb.L("total_debt", pf).basis, "PRO_FORMA")
        mh = lib.model_handoff(mb)
        self.assertEqual(mh.problems(), [])
        rows = {r["facility_id"]: r for r in mh.rows("snapshot.capital_structure")}
        self.assertEqual(rows["NEW-1"]["outstanding"], "1000")
        self.assertEqual(rows["NEW-1"]["column_basis"], "PF-LTM")
        tot = {r["line"]: r for r in mh.rows("snapshot.capital_structure_totals")}
        self.assertEqual(tot["Total debt"]["amount"], "12807")

    def test_projection_identities_and_cases(self):
        rb, h = self._with_pf()
        mb = lib.ModelBuilder(h, rb)

        def drv(g, m, cap):
            yrs = (2026, 2027, 2028)
            return {
                "revenue_growth_pct": dict.fromkeys(yrs, g),
                "adjusted_ebitda_margin_pct": dict.fromkeys(yrs, m),
                "capex_pct_revenue": dict.fromkeys(yrs, cap),
                "cash_taxes": dict.fromkeys(yrs, "40"),
                "wc_change": dict.fromkeys(yrs, "-50"),
                "reference_rate_pct": {2026: "4.0", 2027: "3.8", 2028: "3.6"},
                "mandatory_amortisation": {"cei_term_a": dict.fromkeys(yrs, "37")},
                "min_cash": "500",
            }

        mb.add_projection("BASE", [2026, 2027, 2028], drv("2", "31", "6"))
        mb.add_projection("DOWNSIDE", [2026, 2027, 2028], drv("-4", "28", "6"))
        ph = lib.projection_handoff(mb)
        self.assertEqual(ph.problems(), [])
        self.assertFalse([c for c in mb.forecast_checks if c["status"] == "FAIL"])
        rows = ph.rows("model.projection_summary")
        self.assertEqual(
            {(r["case"], r["fiscal_year"]) for r in rows},
            {(c, y) for c in ("BASE", "DOWNSIDE") for y in ("2026", "2027", "2028")},
        )
        base26 = next(r for r in rows if r["case"] == "BASE" and r["fiscal_year"] == "2026")
        down26 = next(r for r in rows if r["case"] == "DOWNSIDE" and r["fiscal_year"] == "2026")
        self.assertLess(Decimal(down26["adjusted_ebitda"]), Decimal(base26["adjusted_ebitda"]))
        # revenue x margin = EBITDA, and FCF = EBITDA - interest - leases - taxes + WC + capex
        col = next(c for c in mb.cols if c.column_id == "PROJ:BASE:FY2026")
        rev, eb = mb.L("revenue", col).value, mb.L("adjusted_ebitda", col).value
        self.assertEqual(lib.q(rev * Decimal("0.31"), 6), lib.q(eb, 6))
        fcf = (
            eb
            + mb.L("cash_interest", col).value
            + mb.L("lease_cash_not_in_ebitda", col).value
            + mb.L("cash_taxes", col).value
            + Decimal(-50)
            + mb.L("capex", col).value
        )
        self.assertEqual(lib.q(fcf, 6), lib.q(mb.L("fcf", col).value, 6))
        self.assertEqual(mb.L("fcf", col).basis, "PROJECTED")
        import checks

        self.assertEqual(checks.check_model(mb.to_json()), [])
        interest = ph.rows("model.projection_interest")
        self.assertIn("Deck plus spread", {r["rate_basis"] for r in interest})
        self.assertIn("Fixed", {r["rate_basis"] for r in interest})
        self.assertIn("Implied", {r["rate_basis"] for r in interest})

    def test_projection_draws_the_revolver_before_a_shortfall(self):
        rb, h = czr_handoffs()
        mb = lib.ModelBuilder(h, rb)
        yrs = (2026,)
        mb.add_projection(
            "DOWNSIDE",
            [2026],
            {
                "revenue_growth_pct": dict.fromkeys(yrs, "-10"),
                "adjusted_ebitda_margin_pct": dict.fromkeys(yrs, "20"),
                "capex_pct_revenue": dict.fromkeys(yrs, "7"),
                "cash_taxes": dict.fromkeys(yrs, "10"),
                "wc_change": dict.fromkeys(yrs, "-100"),
                "min_cash": "900",
            },
        )
        col = next(c for c in mb.cols if c.kind == "PROJECTED")
        self.assertGreater(mb.L("fac:cei_rcf", col).value, Decimal(120))
        self.assertEqual(mb.L("cash_closing", col).value, Decimal(900))


@needs_corpus
class TestRun(unittest.TestCase):
    def run_partial(self):
        from czr import cp_1, run_brief

        run = lib.Run(
            CTX,
            "t",
            "T1",
            "FULL_CREDIT_ASSESSMENT",
            "full",
            {"name": "Caesars", "id": "CZR"},
            primary=True,
            variant="primary",
        )
        run.plan = ["CP-1", "MODEL"]
        run.build({"CP-1": cp_1.build}, lambda c, r, v: run_brief.build(c, r, v))
        return run

    def test_partial_run_passes_every_check_and_has_charts(self):
        j = self.run_partial().to_json()
        fails = [f for f in lib.check(j, CTX) if "step status" not in f and "plan differs" not in f]
        self.assertEqual(fails, [])
        ids = [c["chart_id"] for c in j["charts"]]
        self.assertEqual(
            ids,
            [
                "chart.model_strip",
                "chart.maturity_wall",
                "chart.capital_structure",
                "chart.ebitda_bridge",
            ],
        )
        self.assertEqual(j["steps"]["MODEL"]["kind"], "host")
        self.assertIn("charts with data: chart.model_strip", " ".join(j["fixture"]["notes"]))
        b = {x["id"]: x for x in j["front_page_blocks"]}
        self.assertFalse(b["credit_snapshot.19"]["shown"])
        self.assertEqual(
            b["credit_snapshot.19"]["line"],
            "What changed since ⟨date⟩ (summary line linking to the tab): no Prior Case accepted".replace(
                "What changed since ⟨date⟩ (summary line linking to the tab)",
                b["credit_snapshot.19"]["title"],
            ),
        )

    def test_projection_feeds_the_three_projection_charts(self):
        from czr import cp_1, run_brief

        yrs = (2026, 2027, 2028)

        def drv(g, m):
            return {
                "revenue_growth_pct": dict.fromkeys(yrs, g),
                "adjusted_ebitda_margin_pct": dict.fromkeys(yrs, m),
                "capex_pct_revenue": dict.fromkeys(yrs, "6"),
                "cash_taxes": dict.fromkeys(yrs, "40"),
                "wc_change": dict.fromkeys(yrs, "-50"),
                "reference_rate_pct": dict.fromkeys(yrs, "4.0"),
                "min_cash": "500",
            }

        def cp2g(ctx, run_id, variant):
            h = lib.Handoff(ctx, "CP-2G", "CZR", run_id, "2026-10-02", ["CP-1"])
            h.qa("Blocked")
            for tid in ctx.spec["module_tables"]["CP-2G"]:
                h.table(tid, [])
            h.analysis("Blocked stand-in used only by this test to carry the drivers.")
            h.meta["projection"] = [
                ("BASE", list(yrs), drv("2", "31")),
                ("DOWNSIDE", list(yrs), drv("-4", "28")),
            ]
            return h

        run = lib.Run(
            CTX,
            "t",
            "T1",
            "FULL_CREDIT_ASSESSMENT",
            "full",
            {"name": "Caesars", "id": "CZR"},
            primary=True,
            variant="primary",
        )
        run.plan = ["CP-1", "CP-2G", "MODEL", "PROJECTION"]
        run.build({"CP-1": cp_1.build, "CP-2G": cp2g}, lambda c, r, v: run_brief.build(c, r, v))
        j = run.to_json()
        charts = {c["chart_id"]: c for c in j["charts"]}
        for cid in ("chart.model_strip", "chart.forecast_lines", "chart.credit_path"):
            ps = charts[cid]["data"]["model.projection_summary"]
            cases = {r[ps["columns"].index("case")] for r in ps["rows"]}
            self.assertEqual(cases, {"BASE", "DOWNSIDE"}, cid)
        self.assertEqual(charts["chart.forecast_lines"]["where"], "analysis:CP-2G")
        self.assertEqual(charts["chart.model_strip"]["where"], "front_page:15")
        fails = [
            f
            for f in lib.check(j, CTX)
            if "step status" not in f and "plan differs" not in f and "CP-2G" not in f
        ]
        self.assertEqual(fails, [])

    def test_check_catches_tampering(self):
        j = self.run_partial().to_json()
        h = j["handoffs"]["CP-1"]
        t = h["tables"]["cp1.model_account_register"]
        h["analysis_md"] += " [C9999]"
        t["rows"][0][2] = "1,234"
        j["charts"] = [c for c in j["charts"] if c["chart_id"] != "chart.maturity_wall"]
        j["model"]["lines"][0]["cells"][0]["value"] = "1"
        fails = " | ".join(lib.check(j, CTX))
        self.assertIn("[C9999] does not resolve", fails)
        self.assertIn("not a plain decimal", fails)
        self.assertIn("chart.maturity_wall applies to this run but is missing", fails)

    def test_incomplete_run_is_reported_not_written(self):
        """Remove one content module (CP-6) from the registry: the run is reported incomplete and no file is written."""
        import contextlib
        import io
        import tempfile
        from unittest import mock

        spec = importlib.util.spec_from_file_location("build_fixtures", HERE / "build-fixtures.py")
        bf = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(bf)  # type: ignore[union-attr]
        real_import = bf.importlib.import_module

        def without_cp6(name, *a, **k):
            if name == "czr.cp_6":
                raise ModuleNotFoundError(f"No module named {name!r}", name=name)
            return real_import(name, *a, **k)

        name = "czr-full-credit-assessment"
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(bf.importlib, "import_module", without_cp6),
            mock.patch.object(bf, "OUT_DIR", Path(tmp)),
            mock.patch.object(sys, "argv", ["build-fixtures.py", "--only", name]),
            contextlib.redirect_stdout(io.StringIO()) as out,
        ):
            data, why = bf.build_run(CTX, name, bf.RUNS[name])
            self.assertIsNone(data)
            self.assertEqual(why, "incomplete: missing CP-6")
            self.assertEqual(bf.main(), 1)
            self.assertEqual(list(Path(tmp).iterdir()), [])
        self.assertIn(f"{name}: incomplete: missing CP-6", out.getvalue())

    def test_diff_tables_marks_changed_added_removed(self):
        a = {
            "snapshot.credit_view": {
                "columns": ["credit_score", "confidence"],
                "rows": [["3 - Fair", "Medium"]],
            },
            "cp2.watch_items": {
                "columns": ["trigger", "threshold_or_signal"],
                "rows": [["A", "1"], ["B", "2"]],
            },
        }
        b = {
            "snapshot.credit_view": {
                "columns": ["credit_score", "confidence"],
                "rows": [["4 - Weak", "Medium"]],
            },
            "cp2.watch_items": {
                "columns": ["trigger", "threshold_or_signal"],
                "rows": [["A", "1.5"], ["C", "3"]],
            },
        }
        kinds = {
            (c["table"], c["key"], c["field"]): c["kind"] for c in lib.diff_tables(a, b)["changes"]
        }
        self.assertEqual(kinds[("snapshot.credit_view", "(single row)", "credit_score")], "changed")
        self.assertEqual(kinds[("snapshot.credit_view", "(single row)", "confidence")], "unchanged")
        self.assertEqual(kinds[("cp2.watch_items", "A", "threshold_or_signal")], "changed")
        self.assertEqual(kinds[("cp2.watch_items", "B", "*")], "removed")
        self.assertEqual(kinds[("cp2.watch_items", "C", "*")], "added")


@needs_corpus
class TestFictionalAndDeterminism(unittest.TestCase):
    def test_deny_list_and_copied_figures(self):
        import checks

        clean = {
            "fixture": {"issuer_fictional": True},
            "x": "Larchmere Leisure Group had 1,642 of debt and 8.25% notes due 2029.",
        }
        self.assertEqual(checks.check_fictional(CTX, clean), [])
        dirty = {
            "fixture": {"issuer_fictional": True},
            "x": "Quillon Ridge, MGM Resorts and Caesars with 11,486 of revenue and 3.29x leverage",
        }
        out = " | ".join(checks.check_fictional(CTX, dirty))
        self.assertIn("'Caesars'", out)
        self.assertIn("'MGM'", out)
        self.assertIn("11486", out)
        self.assertEqual(
            checks.check_fictional(CTX, {"fixture": {"issuer_fictional": False}, "x": "ok"})[-1],
            "fixture.issuer_fictional must be true",
        )

    def test_runs_are_deterministic(self):
        from czr import cp_1, run_brief

        def build():
            run = lib.Run(
                CTX,
                "t",
                "T1",
                "FULL_CREDIT_ASSESSMENT",
                "full",
                {"name": "Caesars", "id": "CZR"},
                primary=True,
                variant="primary",
            )
            run.plan = ["CP-1", "MODEL"]
            run.build({"CP-1": cp_1.build}, lambda c, r, v: run_brief.build(c, r, v))
            return run.to_json()

        self.assertEqual(build(), build())


if __name__ == "__main__":
    unittest.main()
