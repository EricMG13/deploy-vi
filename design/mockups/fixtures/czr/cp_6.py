"""CZR CP-6: challenge and decision.

The real CAOS runs never reached CP-6 and issued no Recommendation. Every Recommendation, Valuation word, thesis and
challenge resolution here is the module's decision as the illustrative layer (the Front Pages mock's views, kept
consistent with the Valuations CP-3 states) and says so. The Portfolio Fit caps are not illustrative: they come from the
Fit step (`ctx.fits`, interfaces §7) through `fit.cp6_rows`, and `final` is the weaker of the uncapped Recommendation and
the cap. Basis is Full, and Screening in the quick run.
"""

from __future__ import annotations

from decimal import Decimal

from core import Ctx, D, Handoff, compute
from czr.cp_3 import AS_OF, FACTS, carry, cite_fact, is_primary, num
from fit import FitResult, cp6_rows
from helpers import join_marks

# Recommendation per instrument (illustrative layer); the Valuation word is read from CP-3
INSTR_REC = {
    "cei_secured_2032": (
        "2 - Modest OW",
        "Secured and priced below par with a first-lien claim; the best paid instrument in the illustrative view.",
    ),
    "cei_unsecured_2032": (
        "4 - Modest UW",
        "Unsecured, the likely fulcrum in a downside, and priced as if for stress.",
    ),
    "cei_term_b": (
        "3 - MW",
        "First-lien loan near par at a discount margin in line with the loan index; fairly valued.",
    ),
    "cei_term_b1": (
        "3 - MW",
        "First-lien Non-Covenant loan, priced a few basis points wider than Term Loan B; fairly valued.",
    ),
    "cei_term_a": (
        "N/A",
        "Amortising pro-rata term loan outside the buy lists of the three Strategies.",
    ),
    "NEW-1": (
        "2 - Modest OW",
        "Incremental first-lien loan whose talk-mid discount margin pays well over Term Loan B-1.",
    ),
    "NEW-2": (
        "4 - Modest UW",
        "Secured notes whose talk-mid yield sits inside the secured 2032s' secondary level.",
    ),
    "NEW-3": (
        "3 - MW",
        "Unsecured notes priced close to the existing unsecured 2032s; fair for the risk.",
    ),
}
BONDS = {"cei_secured_2032", "cei_unsecured_2032", "NEW-2", "NEW-3"}
LOANS = {"cei_term_b", "cei_term_b1", "cei_term_a", "NEW-1"}
STRATEGY_ASSETS = {"CLO": BONDS | LOANS, "Indexed Loans": LOANS, "Indexed HY": BONDS}


def _subset(res: FitResult, ids: set[str]) -> FitResult:
    return FitResult(res.portfolio_id, rows=[r for r in res.rows if r["facility_id"] in ids])


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-6", "CZR", run_id, AS_OF, ["CP-0", "CP-3", "CP-5"], fixture_file="czr/cp_6.py"
    )
    h.qa("Restricted")
    primary = is_primary(ctx, run_id)
    basis = "Screening" if variant == "quick" else "Full"
    cp3 = ctx.get(run_id, "CP-3")
    levels = {r["facility_id"]: r for r in cp3.rows("snapshot.instrument_levels")}
    fits: list[FitResult] = ctx.fits.get(run_id, [])
    syn = h.cite_synthetic(
        "decision",
        "The real CAOS runs never reached CP-6, so every Recommendation, thesis line and challenge resolution is the module's illustrative decision, grounded in the cited figures.",
        "Caesars",
        file="synthetic-facts.json",
    )
    fig = lambda k: join_marks(h.cite_fig(k))  # noqa: E731
    fit_cite = {}
    for res in fits:
        fit_cite[res.portfolio_id] = h.cite_synthetic(
            f"fit.{res.portfolio_id}",
            f"{res.portfolio_id} is a synthetic design portfolio; its limits, NAV and the Fit results on it are test data.",
            "Caesars",
            file="synthetic-facts.json",
        )

    # ---- instrument recommendations (only instruments CP-3 priced carry a Valuation)
    inst_rows = []
    for fid, lv in levels.items():
        rec, why = INSTR_REC[fid]
        inst_rows.append(
            {
                "facility_id": fid,
                "instrument": lv["instrument"],
                "recommendation": rec,
                "valuation": lv["valuation"],
                "rationale": f"{why} Illustrative decision; the Valuation is CP-3's {lv['level_basis']} level.",
                "cite": join_marks(carry(h, cp3, lv["cite"]), syn),
            }
        )
    h.table("snapshot.instrument_recommendation", inst_rows)
    rec_of = {r["facility_id"]: r["recommendation"] for r in inst_rows}

    # ---- recommendation per Strategy
    def fit_line(strategy: str) -> tuple[str, str]:
        for res in fits:
            if res.rows and res.rows[0]["strategy"] == strategy:
                v = {
                    k: sum(1 for r in res.rows if r["verdict"] == k)
                    for k in ("Fits", "Watch", "Breaches")
                }
                return (
                    f"; Fit on {res.portfolio_id} across {len(res.rows)} instruments: Fits {v['Fits']}, Watch {v['Watch']}, Breaches {v['Breaches']}",
                    fit_cite[res.portfolio_id],
                )
        return "; no portfolio is attached for this Strategy", ""

    strat_rows = []
    for strategy, rec, why, cites in (
        (
            "CLO",
            "3 - MW",
            "Loans are fairly valued and the secured notes attractive, but the book's CCC-bucket headroom is thin and the unsecured notes are weak",
            join_marks(fig("senior_leverage_ltm"), fig("fit_c04_room")),
        ),
        (
            "Indexed Loans",
            "3 - MW",
            "First-lien loans are fairly valued at a discount margin near the loan index and the merger leverage is unresolved",
            join_marks(fig("senior_leverage_ltm")),
        ),
        (
            "Indexed HY",
            "2 - Modest OW",
            "The secured 2032s are attractive against peers, while the unsecured notes are avoided until the merger debt is known",
            join_marks(fig("trace_czr_12769gac4_last_yield"), fig("rv_yield_pickup")),
        ),
    ):
        fl, fc = fit_line(strategy)
        strat_rows.append(
            {
                "strategy": strategy,
                "recommendation": rec,
                "basis": basis,
                "rationale": f"{why}{fl}. Illustrative decision.",
                "cite": join_marks(cites, fc, syn),
            }
        )
    h.table("snapshot.recommendation", strat_rows)

    # ---- thesis
    if primary:
        new_debt = sum((D(t["size"]) for t in FACTS["merger_tranches"]["tranches"]), Decimal(0))
        pf_rows = ctx.get(run_id, "CP-1").rows("cp1.pro_forma_adjustment_register")
        new_int = -sum(
            (D(r["value"]) for r in pf_rows if r["metric_id"] == "cash_interest_paid"), Decimal(0)
        )
        ebitda = ctx.val("ltm_adj_ebitda_q2_2026")
        pf_lev, pf_lev_s = compute(
            "pro forma total leverage",
            "(debt + new) / ebitda",
            2,
            "x",
            debt=ctx.val("total_debt_check_2026_06_30"),
            new=new_debt,
            ebitda=ebitda,
        )
        pf_cov, pf_cov_s = compute(
            "pro forma debt cash interest cover",
            "ebitda / (base + new)",
            2,
            "x",
            ebitda=ebitda,
            base=ctx.val("ltm_cash_interest_debt_q2_2026"),
            new=new_int,
        )
        pf_text = f" The synthetic merger tranches lift total leverage to {num(pf_lev, 2)}x and cut debt cash interest cover to {num(pf_cov, 2)}x, still inside every covenant test."
        pf_cite, pf_calcs = cite_fact(h, "merger_tranches"), " " + pf_lev_s + " " + pf_cov_s
    else:
        pf_text, pf_cite, pf_calcs = "", "", ""
    thesis = (
        "Caesars is a large, cash-generative operator whose secured debt is well covered today, but a pending take-private adds new debt on top of a lease-heavy structure. "
        "Prefer the secured 2032 notes, which trade below par, over the unsecured notes until the merger financing is known."
        + pf_text
    )
    h.table(
        "snapshot.thesis",
        [
            {
                "thesis": thesis,
                "cite": join_marks(
                    fig("ltm_adj_ebitda_q2_2026"),
                    fig("trace_czr_12769gac4_last_price"),
                    pf_cite,
                    syn,
                )
                + pf_calcs,
            }
        ],
    )

    # ---- catalysts
    cat = [
        (
            "2026-07-11 (passed)",
            "Go-shop period ended",
            "Flat",
            "A competing proposal, which did not appear",
            join_marks(h.cite_data("C223")),
        ),
        (
            "2027-05-27",
            "Merger End Date; extends to 27 August 2027 and 27 November 2027 if only regulatory conditions are open",
            "Down",
            "Extension of the End Date or a regulatory delay",
            join_marks(
                fig("merger_initial_end_date"),
                fig("merger_first_extended_end_date"),
                fig("merger_second_extended_end_date"),
            ),
        ),
        (
            "From 2027-06-26",
            "Ticking fee accrues",
            "Down",
            "Closing slips past the ticking-fee date",
            fig("merger_ticking_fee_date"),
        ),
        (
            "2028-01-31",
            "CEI revolver and Term Loan A mature",
            "Down",
            "No extension announced in the twelve months before",
            fig("cei_rcf_maturity"),
        ),
        (
            "Before closing",
            "Disclosure of the committed debt financing"
            if not primary
            else "Final terms of the new Term Loan B and notes against the synthetic talk",
            "Up" if primary else "Flat",
            "Amount, ranking and pricing of the new debt",
            syn,
        ),
    ]
    h.table(
        "snapshot.catalysts",
        [
            {"date_or_window": a, "event": b, "direction": c, "watch_trigger": d, "cite": e}
            for a, b, c, d, e in cat
        ],
    )

    # ---- challenge
    h.table(
        "cp6.challenge",
        [
            {
                "claim": "Secured 2032s are money-good after the merger",
                "counter_evidence": f"Pari capacity of {num(ctx.val('cap_pari_secured'))} dilutes them {fig('cap_pari_secured')}",
                "resolution": "Held, with the size of the new secured debt as the open risk",
                "what_would_change_view": "New secured debt larger than the pari capacity",
                "cite": join_marks(fig("cap_pari_secured"), syn),
            },
            {
                "claim": "The unsecured notes are the fulcrum in a downside",
                "counter_evidence": "No recovery waterfall exists: the distress gate is not met where CP-4C runs, and this run has no CP-4C otherwise"
                if (run_id, "CP-4C") in ctx.built
                else "This run has no CP-4C, so no recovery waterfall exists to show a fulcrum",
                "resolution": f"Held as a judgement only: unsecured claims sit behind {num(ctx.val('senior_secured_debt_2026_06_30'))} of secured debt {fig('senior_secured_debt_2026_06_30')}, but no recovery is computed",
                "what_would_change_view": "A met distress gate with a recovery waterfall",
                "cite": join_marks(fig("senior_secured_debt_2026_06_30"), syn),
            },
            {
                "claim": "Las Vegas weakness is cyclical",
                "counter_evidence": f"Two segments lost margin in the same quarter: Las Vegas {num(abs(ctx.val('eu_seg_margin_chg_las_vegas')), 1)} pp and Caesars Digital {num(abs(ctx.val('eu_seg_margin_chg_caesars_digital')), 1)} pp {fig('eu_seg_margin_chg_las_vegas')}{fig('eu_seg_margin_chg_caesars_digital')}",
                "resolution": "Not resolved: one quarter is not a trend",
                "what_would_change_view": "A second quarter of lower Las Vegas margin",
                "cite": join_marks(
                    fig("eu_seg_margin_chg_las_vegas"),
                    fig("eu_seg_margin_chg_caesars_digital"),
                    syn,
                ),
            },
        ],
    )

    # ---- per-portfolio recommendation after the Fit cap
    pr_rows = []
    for res in fits:
        strategy = res.rows[0]["strategy"] if res.rows else "CLO"
        ids = {
            fid
            for fid in rec_of
            if fid in STRATEGY_ASSETS.get(strategy, set()) and rec_of[fid] != "N/A"
        }
        sub = _subset(res, ids)
        pr_rows += cp6_rows(sub, {fid: rec_of[fid] for fid in ids}, strategy)
    h.table("cp6.portfolio_recommendation", pr_rows)

    # ---- analysis
    n_by = {
        k: sum(1 for r in pr_rows if r["fit_verdict"] == k) for k in ("Fits", "Watch", "Breaches")
    }
    capped = [r for r in pr_rows if r["final"] != r["uncapped"]]
    paras = [
        f"The Recommendations that survive the strongest challenge are CLO 3 - MW, Indexed Loans 3 - MW and Indexed HY 2 - Modest OW, at {basis} basis. "
        f"These are the module's decision as an illustrative layer: the real CAOS runs never reached CP-6 and issued no Recommendation, and the Valuations they rest on are CP-3's illustrative words {syn}. Confidence is Low.",
        f"By instrument, the secured 2032 notes are Modest OW (V2 - Attractive) at {num(ctx.val('trace_czr_12769gac4_last_price'))}, yielding {num(ctx.val('trace_czr_12769gac4_last_yield'), 2)}% {fig('trace_czr_12769gac4_last_yield')}, and the unsecured 2032 notes Modest UW (V4 - Unattractive) at {num(ctx.val('trace_czr_12769gad2_last_price'))}; the term loans are MW at synthetic marks. "
        + (
            "The three merger tranches are decided at talk: the incremental Term Loan B is Modest OW, the secured notes Modest UW and the unsecured notes MW, all provisional until final pricing."
            if primary
            else "No merger tranche is in this run, so no talk-based decision is made."
        ),
        f"The strongest challenge is to the secured thesis: the pari incremental capacity of {num(ctx.val('cap_pari_secured'))} could dilute the secured notes {fig('cap_pari_secured')}. It is held, because the Fit and covenant tests leave room today, and the open risk is a larger secured financing than the capacity allows. "
        "The fulcrum claim for the unsecured notes is held as a judgement only, since no distress gate is met and no waterfall exists.",
    ]
    if fits:
        paras.append(
            f"Portfolio Fit then caps the decision. Across {len(pr_rows)} instrument and portfolio pairs the Fit verdicts are Fits {n_by['Fits']}, Watch {n_by['Watch']} and Breaches {n_by['Breaches']}; the cap lowers {len(capped)} Recommendation{'s' if len(capped) != 1 else ''} (final is the weaker of the uncapped Recommendation and the cap)"
            + (
                ": "
                + "; ".join(
                    f"{r['instrument']} on {r['portfolio_id']} goes from {r['uncapped']} to {r['final']} ({r['fit_verdict']})"
                    for r in capped[:3]
                )
                + "."
                if capped
                else "."
            )
        )
    paras.append(
        "What would change this view: the disclosed merger financing, a second quarter of lower Las Vegas margin, an extension of the 2028 revolver and Term Loan A, or a distress trigger. Confidence in this module: Low."
    )
    h.analysis("\n\n".join(paras))
    h.gaps(
        "- Recommendations, Valuations, thesis and challenge resolutions are the illustrative layer: the real CAOS runs never reached CP-6 and the real CP-3 reached Requires More Work. Lifted by: a committee-ready run with supplied mandate and weights.\n"
        "- Instruments without a market or talk level (the revolver, 7.00% secured 2030s, 4.625% 2029s, CVA loan, improvement district bonds) carry no Valuation and so no Recommendation. Lifted by: market levels.\n"
        "- Portfolio Fit uses synthetic portfolios (Test CLO I and, in the Portfolio Decision run, the Indexed HY book); the caps are exact for those inputs only.\n"
        "- Loan marks and the spread benchmark are synthetic (G18, G19)."
        + (
            "\n- The three merger tranches are synthetic (G8); their Recommendations are provisional."
            if primary
            else ""
        )
    )
    return h
