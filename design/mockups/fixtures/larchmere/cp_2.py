"""Larchmere CP-2: fundamental credit synthesis (synthetic)."""

from __future__ import annotations

from core import Ctx, Handoff, compute, fx, plain
from helpers import join_marks

from . import derived as X
from . import facts as F
from .facts import syn


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "CP-1A", "MODEL"],
        fixture_file="larchmere/cp_2.py",
    )
    h.qa("Restricted")
    ssim = X.ssim_ltm()
    cash_int, ci_s = X.ltm("cash_interest")
    rent, rent_s = X.ltm("lease_cash")
    fixed, fixed_s = compute(
        "fixed charges", "cash_interest + rent", 0, "", cash_interest=cash_int, rent=rent
    )
    cover, cover_s = compute("fixed-charge cover", "ssim / fixed", 2, "x", ssim=ssim, fixed=fixed)
    cfo, capex = X.ltm("cfo")[0], X.ltm("capex")[0]
    fcf, fcf_s = compute("LTM free cash flow", "cfo - capex", 0, "", cfo=cfo, capex=capex)
    net_lev, net_s = compute(
        "net leverage",
        "net / ssim",
        2,
        "x",
        net=X.total_debt("JUN30_2026") - X.cash("JUN30_2026"),
        ssim=ssim,
    )
    cov = X.covenant()
    rev_chg, rev_s = compute(
        "H1 2026 revenue change",
        "(h1 - ph1) / ph1 * 100",
        1,
        "",
        h1=F.val("revenue")["H1_2026"],
        ph1=F.val("revenue")["H1_2025"],
    )
    ebitda_chg, _ = compute(
        "H1 2026 Adjusted EBITDA change",
        "(h1 - ph1) / ph1 * 100",
        1,
        "",
        h1=F.val("adjusted_ebitda")["H1_2026"],
        ph1=F.val("adjusted_ebitda")["H1_2025"],
    )
    ratio_x, ratio_s = compute(
        "EBITDA decline per point of revenue",
        "ebitda_chg / rev_chg",
        1,
        "",
        ebitda_chg=ebitda_chg,
        rev_chg=rev_chg,
    )
    m = {
        k: syn(h, k)
        for k in (
            "adjusted_ebitda",
            "cash_interest",
            "lease_cash",
            "cfo",
            "capex",
            "cash_balance",
            "rcf_drawn",
            "facility_terms",
            "distress_events",
            "covenants",
            "business_overview",
            "ownership_terms",
            "revenue",
            "liquidation",
            "ev_multiples",
        )
    }
    h.table(
        "snapshot.credit_view",
        [
            {
                "credit_score": "5 - Stressed",
                "credit_direction": "Deteriorating",
                "sector_outlook": "Negative",
                "primary_support": f"Licensed regional gaming assets: appraised property, equipment and licences of 1,180 {m['liquidation']} and a base-case enterprise value above the first-lien claims {m['ev_multiples']}.",
                "primary_downside": f"Cash earnings no longer cover fixed charges: SSIM EBITDA of {plain(ssim)} against {plain(fixed)} of cash interest and rent {m['cash_interest']}{m['lease_cash']}, with 62 of cash, a covenant breach and a missed coupon {m['distress_events']}.",
                "confidence": "Medium",
                "basis": "Full",
                "cite": join_marks(
                    m["adjusted_ebitda"],
                    m["cash_interest"],
                    m["lease_cash"],
                    m["cash_balance"],
                    m["distress_events"],
                    m["liquidation"],
                    m["ev_multiples"],
                ),
            }
        ],
    )
    h.table(
        "snapshot.strengths_weaknesses",
        [
            {
                "kind": "Strength",
                "label": "Licensed, owned assets",
                "text": "Four of eleven properties are owned and all eleven hold gaming licences that are slow to replace; appraised assets of 1,180 give a recovery floor.",
                "cite": join_marks(m["business_overview"], m["liquidation"]),
            },
            {
                "kind": "Strength",
                "label": "Four-state diversification",
                "text": "No single state is more than about a quarter of revenue, which limits a regulatory or competitive shock in one market.",
                "cite": m["business_overview"],
            },
            {
                "kind": "Weakness",
                "label": "Fixed charges at EBITDA",
                "text": f"Cash interest of {plain(cash_int)} and cash rent of {plain(rent)} take {plain(fixed)} of {plain(ssim)} SSIM EBITDA; fixed-charge cover is {fx(cover)} ({cover_s}).",
                "cite": join_marks(m["cash_interest"], m["lease_cash"], m["adjusted_ebitda"])
                + " "
                + cover_s,
            },
            {
                "kind": "Weakness",
                "label": "No liquidity buffer",
                "text": "The revolver is fully drawn at 200, cash is 62 and the minimum liquidity covenant is 50.",
                "cite": join_marks(m["rcf_drawn"], m["cash_balance"], m["covenants"]),
            },
            {
                "kind": "Weakness",
                "label": "Sponsor support uncommitted",
                "text": "The sponsor owns 88% and has proposed priming new-money debt rather than committing equity.",
                "cite": m["ownership_terms"],
            },
        ],
    )
    h.table(
        "cp2.drivers",
        [
            {
                "rank": "1",
                "driver": "Operating deleverage on falling revenue",
                "evidence": f"H1 2026 revenue {plain(rev_chg)}% and Adjusted EBITDA {plain(ebitda_chg)}% on H1 2025 {m['revenue']}{m['adjusted_ebitda']}.",
                "risk_mechanism": f"A 71% gaming mix and a fixed cost base turn a {plain(-rev_chg)}% revenue decline into a {plain(-ebitda_chg)}% EBITDA decline.",
                "credit_implication": f"Every further 1% of revenue lost removes about {plain(ratio_x, 1)}% of EBITDA, so leverage rises faster than revenue falls.",
                "direction": "Negative",
                "confidence": "High",
                "cite": join_marks(m["revenue"], m["adjusted_ebitda"]) + " " + ratio_s,
            },
            {
                "rank": "2",
                "driver": "Fixed charges at or above EBITDA",
                "evidence": f"Fixed-charge cover of {fx(cover)} and LTM free cash flow of {plain(fcf)} ({fcf_s}).",
                "risk_mechanism": "Interest and rent are contractual; there is no cash left for amortisation, capex and fees.",
                "credit_implication": "The company must borrow, sell assets or restructure within a year.",
                "direction": "Negative",
                "confidence": "High",
                "cite": join_marks(m["cash_interest"], m["lease_cash"], m["cfo"], m["capex"])
                + " "
                + fcf_s,
            },
            {
                "rank": "3",
                "driver": "Covenant breach and missed coupon",
                "evidence": f"First-lien net leverage {cov['lev']}x against 6.50x and the 15 September coupon unpaid {m['covenants']}{m['distress_events']}.",
                "risk_mechanism": "Cross-default links the notes, the credit agreement and the master lease.",
                "credit_implication": "Defaults accelerate the timetable to weeks, not quarters.",
                "direction": "Negative",
                "confidence": "High",
                "cite": join_marks(m["covenants"], m["distress_events"]) + " " + cov["lev_s"],
            },
            {
                "rank": "4",
                "driver": "2028 maturity wall",
                "evidence": f"Revolver due 15 March 2028 and term loan B due 30 September 2028, 1,250 of first-lien debt {m['facility_terms']}.",
                "risk_mechanism": "A going-concern warning and a falling EBITDA make a market refinancing unlikely.",
                "credit_implication": "Refinancing is only possible through an amend-and-extend with creditor consent.",
                "direction": "Negative",
                "confidence": "Medium",
                "cite": m["facility_terms"],
            },
        ],
    )
    h.table(
        "cp2.watch_items",
        [
            {
                "trigger": "Notes grace period expires",
                "threshold_or_signal": "Coupon unpaid on 15 October 2026",
                "why_it_matters": "An event of default on the notes starts cross-default clocks on the credit agreement and the master lease.",
                "credit_impact": "Moves a negotiated path towards a filing within weeks.",
                "cite": m["distress_events"],
            },
            {
                "trigger": "Equity cure decision",
                "threshold_or_signal": "Cure notice by 19 October 2026 (about 35 of deemed EBITDA)",
                "why_it_matters": "The cure is available once and restores the springing test only if the sponsor funds it.",
                "credit_impact": "A funded cure buys one quarter; no cure leaves the breach uncured.",
                "cite": m["covenants"],
            },
            {
                "trigger": "Liquidity below the 50 floor",
                "threshold_or_signal": "Cash plus undrawn availability under 50",
                "why_it_matters": "The minimum liquidity covenant is a second maintenance test and sits 12 above current levels.",
                "credit_impact": "A second breach removes the sponsor's room to negotiate.",
                "cite": join_marks(m["covenants"], m["cash_balance"]),
            },
        ],
    )
    h.analysis(
        f"Larchmere is a Stressed credit on a Deteriorating direction in a Negative sector. The strongest support is hard assets: four owned properties and eleven licences with an appraised value of 1,180 {m['liquidation']}. "
        f"The primary downside is that cash earnings no longer cover fixed charges: SSIM EBITDA of {plain(ssim)} meets {plain(fixed)} of cash interest and rent, a cover of {fx(cover)} ({cover_s}) {m['adjusted_ebitda']}{m['cash_interest']}{m['lease_cash']}. "
        "The module view is a 5 - Stressed score with Medium confidence, because the pack has one set of company documents and a single dealer file.\n\n"
        f"Leverage is {net_lev}x net on SSIM EBITDA ({net_s}), with the revolver fully drawn {m['rcf_drawn']}. Revenue fell {plain(-rev_chg)}% and EBITDA {plain(-ebitda_chg, 1)}% in the first half of 2026 ({rev_s}), which is operating deleverage in action {m['revenue']}. "
        f"Free cash flow is {plain(fcf)} LTM ({fcf_s}), against cash of 62 {m['cash_balance']}.\n\n"
        f"The covenant and payment events make time the binding constraint: first-lien net leverage is {cov['lev']}x against 6.50x, the equity cure window closes on 19 October and the notes' grace period ends on 15 October {m['covenants']}{m['distress_events']}. "
        f"The sponsor holds 88% and has committed nothing, and the landlord can block any path through the master lease {m['ownership_terms']}.\n\n"
        "What would change the view: a funded equity cure with a standstill from the notes holders, evidence that Gulf Coast has stabilised, or a lessor concession on rent would move the direction to Stable; a lapsed grace period or a failed cure would move it to a filing case."
    )
    h.gaps(
        "- Competitor supply and market share by state: not in the pack, so the share-loss explanation rests on company statistics. Lifted by: gaming-board market reports (Deep Research was not approved).\n"
        "- Management forecast detail: the lender presentation gives totals only. Lifted by: the management model.\n"
        "- Independent valuation: none; the asset floor is the company's appraisal. Lifted by: an adviser's report."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
