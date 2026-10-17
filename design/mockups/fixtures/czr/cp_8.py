"""CZR CP-8: Prior Case (Earnings Update run only).

The prior Report is the synthetic Q1 2026 Earnings Update dated 2026-08-05 (`czr.prior_case`). `what_changed` is built from
the run's own `prior/diff` (`run.diff_tables`), so every row ties to a diff change; the prior values come from the facts
file, the current values from the run's handoffs. Prior LTM revenue and Adjusted EBITDA (to 31 March 2026) are real
figures calculated from the filings. The Earnings Update plan has no CP-6, so `recommendation_change` carries the prior
Recommendations against `N/A`: CP-8 does not issue a Recommendation.
"""

from __future__ import annotations

from core import Ctx, D, Handoff, compute, plain
from czr.cp_3 import AS_OF, num
from czr.prior_case import PRIOR, PV, current_tables, prior_ltm
from czr.prior_case import build as build_prior
from helpers import join_marks
from run import diff_tables

BLOCK = {
    "snapshot.credit_view": "Credit view",
    "snapshot.financials": "Financials",
    "cp2.watch_items": "Watch items",
    "snapshot.strengths_weaknesses": "Strengths and weaknesses",
}
LINE_LABEL = {
    "revenue": "Revenue, LTM (US$ m)",
    "adjusted_ebitda": "Adjusted EBITDA, LTM (US$ m)",
    "metric:adjusted_ebitda_margin": "Adjusted EBITDA margin, LTM (%)",
    "metric:net_leverage_adjusted": "Net leverage, LTM (x)",
}
HIGHER_IS_BETTER = {
    "revenue": True,
    "adjusted_ebitda": True,
    "metric:adjusted_ebitda_margin": True,
    "metric:net_leverage_adjusted": False,
}
ORDER = {
    "credit_direction": ["Improving", "Stable", "Deteriorating"],
    "sector_outlook": ["Positive", "Neutral", "Negative"],
    "credit_score": ["1 - Strong", "2 - Good", "3 - Fair", "4 - Weak", "5 - Stressed"],
}


def _kind(order: list[str], prior: str, cur: str) -> str:
    """Improved when the current word sits earlier (better) in `order`, else Deteriorated."""
    pi, ci = order.index(prior), order.index(cur)
    return "Unchanged" if pi == ci else ("Improved" if ci < pi else "Deteriorated")


def _num_kind(better_up: bool, prior: str, cur: str) -> str:
    p, c = D(prior), D(cur)
    if p == c:
        return "Unchanged"
    return "Improved" if (c > p) == better_up else "Deteriorated"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-8",
        "CZR",
        run_id,
        AS_OF,
        ["CP-0", "CP-1", "CP-1B", "CP-2", "MODEL", "CP-5"],
        fixture_file="czr/cp_8.py",
    )
    h.qa("Restricted")
    prior = build_prior(ctx)
    syn = h.cite_synthetic("prior_case", PRIOR["rationale"], "Caesars", file="synthetic-facts.json")
    diff = diff_tables(prior["tables"], current_tables(ctx, run_id))["changes"]
    fig = lambda k: join_marks(h.cite_fig(k))  # noqa: E731

    rev_p, rev_calc, rev_m = prior_ltm(ctx, h, "net_revenues")
    eb_p, eb_calc, eb_m = prior_ltm(ctx, h, "adj_ebitda")
    why_cites = {
        "revenue": (
            f"Q2 revenue rose {num(ctx.val('czr_rev_growth_q2_2026'), 1)}% year on year, {num(ctx.val('eu_rev_chg_q2'))} more than Q2 2025; the prior LTM is to 31 March 2026 ({rev_calc})",
            join_marks(fig("czr_rev_growth_q2_2026"), fig("eu_rev_chg_q2"), rev_m) + " " + rev_calc,
        ),
        "adjusted_ebitda": (
            f"Q2 Adjusted EBITDA fell {num(abs(ctx.val('eu_ebitda_pct_q2')), 1)}% ({num(ctx.val('eu_ebitda_chg_q2'))}); the prior LTM is to 31 March 2026 ({eb_calc})",
            join_marks(fig("eu_ebitda_pct_q2"), fig("eu_ebitda_chg_q2"), eb_m) + " " + eb_calc,
        ),
        "metric:adjusted_ebitda_margin": (
            f"Revenue grew while Adjusted EBITDA fell, so the LTM margin slipped; Q2 margin fell {num(abs(ctx.val('eu_margin_chg_pp')), 1)} pp year on year",
            join_marks(fig("eu_margin_chg_pp"), fig("ebitda_margin_ltm")),
        ),
        "metric:net_leverage_adjusted": (
            f"Net debt fell {num(abs(ctx.val('eu_netdebt_chg')))} between 31 December 2025 and 30 June 2026 while LTM EBITDA also fell, so net leverage moved {num(ctx.val('eu_netlev_chg'), 2)}x",
            join_marks(fig("eu_netdebt_chg"), fig("eu_netlev_chg"), fig("net_leverage_ltm")),
        ),
    }
    credit_why = {
        "credit_direction": (
            f"Las Vegas Q2 Adjusted EBITDA fell {num(abs(ctx.val('eu_seg_ebitda_pct_las_vegas')), 1)}% with the margin down {num(abs(ctx.val('eu_seg_margin_chg_las_vegas')), 1)} pp while the merger debt stays unstated (G8)",
            join_marks(fig("eu_seg_ebitda_pct_las_vegas"), fig("eu_seg_margin_chg_las_vegas")),
        ),
        "credit_score": (
            "Score unchanged: the cash and leverage figures did not move enough to change it",
            join_marks(fig("net_leverage_ltm")),
        ),
        "sector_outlook": ("No change in the sector view", join_marks(fig("net_leverage_ltm"))),
    }

    rows: list[dict] = []
    for c in diff:
        if c["kind"] == "unchanged":
            continue
        tid, key, field = c["table"], c["key"], c["field"]
        block = BLOCK.get(tid)
        if block is None:
            continue
        if c["kind"] == "changed":
            if tid == "snapshot.credit_view" and field in ORDER:
                why, ck = credit_why[field]
                rows.append(
                    {
                        "block": block,
                        "field": {
                            "credit_direction": "Credit Direction",
                            "credit_score": "Credit Score",
                            "sector_outlook": "Sector Outlook",
                        }[field],
                        "prior_value": c["prior"],
                        "current_value": c["current"],
                        "change": _kind(ORDER[field], c["prior"], c["current"]),
                        "why": why,
                        "cite": join_marks(ck, syn),
                    }
                )
            elif tid == "snapshot.financials" and field == "ltm" and key in LINE_LABEL:
                why, ck = why_cites[key]
                rows.append(
                    {
                        "block": block,
                        "field": LINE_LABEL[key],
                        "prior_value": c["prior"],
                        "current_value": c["current"],
                        "change": _num_kind(HIGHER_IS_BETTER[key], c["prior"], c["current"]),
                        "why": why,
                        "cite": join_marks(ck, syn)
                        if key == "metric:net_leverage_adjusted"
                        else ck,
                    }
                )
        elif c["kind"] == "added":
            rows.append(
                {
                    "block": block,
                    "field": f"{key} (new)",
                    "prior_value": "Not in the prior Report",
                    "current_value": "Now listed",
                    "change": "New",
                    "why": "The row is in this Report's table and was not in the prior Report's",
                    "cite": syn,
                }
            )
        elif c["kind"] == "removed":
            rows.append(
                {
                    "block": block,
                    "field": f"{key} (removed)",
                    "prior_value": "Listed in the prior Report",
                    "current_value": "No longer listed",
                    "change": "Removed",
                    "why": "The row was in the prior Report's table and is not in this Report's",
                    "cite": syn,
                }
            )
    # two operating facts the prior Report stated in text, not in a diffed table
    lv_now, liq_now = ctx.val("eu_seg_margin_las_vegas_q2_2026"), ctx.val("liq_total")
    lv_prior, liq_prior = (
        D(PV["las_vegas_adj_ebitda_margin_pct"]),
        D(PV["liquidity_usdm"].replace(",", "")),
    )
    lv_d, lv_s = compute(
        "Las Vegas margin change", "now - prior", 1, "%", now=lv_now, prior=lv_prior
    )
    liq_d, liq_s = compute("liquidity change", "now - prior", 0, "", now=liq_now, prior=liq_prior)
    rows.append(
        {
            "block": "Segments",
            "field": "Las Vegas Adjusted EBITDA margin (%)",
            "prior_value": plain(lv_prior, 1),
            "current_value": plain(lv_now, 1),
            "change": "Deteriorated",
            "why": f"The Q2 2026 margin is {num(abs(lv_d), 1)} pp under the prior Report's {plain(lv_prior, 1)}% ({lv_s})",
            "cite": join_marks(fig("eu_seg_margin_las_vegas_q2_2026"), syn) + " " + lv_s,
        }
    )
    rows.append(
        {
            "block": "Liquidity",
            "field": "Cash and revolver capacity (US$ m)",
            "prior_value": plain(liq_prior),
            "current_value": plain(liq_now),
            "change": "Deteriorated",
            "why": f"Liquidity fell {num(abs(liq_d))} to the 30 June 2026 figure ({liq_s})",
            "cite": join_marks(fig("liq_total"), syn) + " " + liq_s,
        }
    )
    h.table("cp8.what_changed", rows)

    # ---- thesis review: the prior Report's thesis and catalysts against what happened
    lv_c, liq_c = fig("eu_seg_margin_las_vegas_q2_2026"), fig("liq_total")
    review = [
        {
            "prior_item": PRIOR["prior_catalysts"][1],
            "expected": plain(lv_prior, 1) + "%",
            "realised": plain(lv_now, 1) + "%",
            "outcome": "Deteriorated",
            "lesson": f"One quarter did not explain it: Caesars Digital's margin also fell {num(abs(ctx.val('eu_seg_margin_chg_caesars_digital')), 1)} pp in the same quarter {fig('eu_seg_margin_chg_caesars_digital')}",
            "cite": join_marks(lv_c, syn, fig("eu_seg_margin_chg_caesars_digital")),
        },
        {
            "prior_item": PRIOR["prior_catalysts"][0],
            "expected": "Disclosed by 2026-09-30",
            "realised": "Not disclosed in the Source Pack (G8)",
            "outcome": "Unchanged",
            "lesson": "The thesis still rests on debt of unknown size; the catalyst date passed without disclosure",
            "cite": syn,
        },
        {
            "prior_item": "Net leverage holds near the prior level",
            "expected": PV["net_leverage_x"] + "x",
            "realised": plain(ctx.val("net_leverage_ltm"), 2) + "x",
            "outcome": "Unchanged",
            "lesson": "A two-hundredths move is inside the noise of one quarter's EBITDA",
            "cite": join_marks(fig("net_leverage_ltm"), syn),
        },
        {
            "prior_item": "Liquidity stays ample",
            "expected": plain(liq_prior),
            "realised": plain(liq_now),
            "outcome": "Deteriorated",
            "lesson": "Liquidity is still far above 2026 and 2027 maturities, but it fell "
            + num(abs(liq_d))
            + " in the quarter",
            "cite": join_marks(liq_c, syn) + " " + liq_s,
        },
        {
            "prior_item": PRIOR["prior_thesis"],
            "expected": "Secured outperforms unsecured",
            "realised": "Unsecured 2032 yield above the secured 2032 yield by 125 bps",
            "outcome": "Unchanged",
            "lesson": "The market still pays more for the unsecured claim, so the preference for secured stands",
            "cite": join_marks(fig("rv_yield_pickup"), syn),
        },
    ]
    h.table("cp8.thesis_review", review)

    # ---- recommendation change: no CP-6 in this plan, so no current Recommendation
    h.table(
        "cp8.recommendation_change",
        [
            {
                "strategy": strat,
                "prior": PV[f"recommendation_{strat}"],
                "current": "N/A",
                "reason": "The Earnings Update plan has no CP-6, so no current Recommendation is issued; the prior one is shown for reference",
            }
            for strat in ("CLO", "Indexed Loans", "Indexed HY")
        ],
    )

    # ---- analysis
    cd = next((r for r in rows if r["field"] == "Credit Direction"), None)
    nl = next((r for r in rows if r["field"] == "Net leverage, LTM (x)"), None)
    eb = next((r for r in rows if r["field"] == "Adjusted EBITDA, LTM (US$ m)"), None)
    paras = [
        (
            f"Since the 5 August 2026 Earnings Update the Credit Direction has moved from {cd['prior_value']} to {cd['current_value']}, and the thesis held in part: net leverage and the secured preference stand, the Las Vegas margin catalyst failed and the merger financing catalyst passed without disclosure. {cd['cite']}"
            if cd
            else "Since the 5 August 2026 Earnings Update the Credit Score, Direction and Sector Outlook are unchanged and the thesis held in part."
        ),
        f"LTM Adjusted EBITDA fell from {eb['prior_value']} to {eb['current_value']} while LTM revenue rose from {num(rev_p)} to {num(ctx.val('ltm_net_revenues_q2_2026'))}; the prior LTM is to 31 March 2026 and is calculated from the filings ({eb_calc}) {eb_m}. "
        f"Net leverage was {nl['prior_value']}x in the prior Report and is {nl['current_value']}x now, a move too small to change the view {nl['cite']}."
        if eb and nl
        else "The LTM comparison could not be built from the current run's tables.",
        f"Liquidity fell from {num(liq_prior)} to {num(liq_now)} ({liq_s}) {liq_c}. The Las Vegas Adjusted EBITDA margin was {plain(lv_now, 1)}% in Q2 against {plain(lv_prior, 1)}% in the prior Report {lv_c}. These are the two figures the prior thesis relied on and both moved the wrong way.",
        f"The earlier thesis was: {PRIOR['prior_thesis']} {syn} Five items are reviewed in the thesis table: two deteriorated, three are unchanged. "
        "No current Recommendation is issued here, because the Earnings Update plan has no CP-6; the prior Recommendations are shown against N/A.",
        "What would change this view: disclosure of the merger financing, a second quarter of lower Las Vegas margin, or a further fall in liquidity would move the Credit Direction again. Confidence in this module: Medium-Low. "
        f"The comparison rests on a synthetic prior Report {syn}; the current figures are real.",
    ]
    h.analysis("\n\n".join(paras))
    h.gaps(
        "- Prior Report: no earlier RBOT Report exists; the prior values are synthetic (czr.prior_case) except LTM revenue and Adjusted EBITDA, which are calculated from the filings. Lifted by: a real earlier Report.\n"
        "- Recommendation change: the Earnings Update plan has no CP-6, so the current Recommendation is N/A. Lifted by: a Full Credit Assessment or Relative Value run.\n"
        "- Liquidity and the Las Vegas margin are compared in text only; they are not in a diffed Front Page table.\n"
        "- Q1 2026 balance-sheet and cash-flow figures are not in the Source Pack, so the prior leverage and liquidity are taken from the prior Report."
    )
    return h
