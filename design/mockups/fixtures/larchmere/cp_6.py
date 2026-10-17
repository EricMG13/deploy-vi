"""Larchmere CP-6: challenge and decision (synthetic). The portfolio rows apply the Portfolio Fit cap to the uncapped views."""

from __future__ import annotations

from core import Ctx, Handoff, compute
from fit import cp6_rows

from . import derived as X
from . import facts as F
from .facts import syn

UNCAPPED = {
    "llg_rcf": "N/A",
    "llg_tlb": "3 - MW",
    "llg_2l": "4 - Modest UW",
    "llg_notes": "5 - Strong UW",
    "NEW-1": "N/A",
}


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-6",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-3", "CP-5", "FIT"],
        fixture_file="larchmere/cp_6.py",
    )
    h.qa("Pass")
    X.require(ctx, run_id, "FIT")
    fit_res = ctx.fits[run_id][0]
    fit_row = next(r for r in fit_res.rows if r["facility_id"] == "llg_tlb")
    exp = X.expected_recovery()
    upside, upside_s = compute(
        "expected recovery above price",
        "recovery - price",
        1,
        "",
        recovery=exp["C2-1L"][0],
        price=F.val("quotes")["llg_tlb"],
    )
    m_dist, m_cov, m_q, m_new, m_fwd, m_prob, m_port, m_own = (
        syn(h, k)
        for k in (
            "distress_events",
            "covenants",
            "quotes",
            "new_money",
            "forward_12m",
            "ev_probabilities",
            "portfolio",
            "ownership_terms",
        )
    )
    h.table(
        "snapshot.recommendation",
        [
            {
                "strategy": "CLO",
                "recommendation": "3 - MW",
                "basis": "Full",
                "rationale": f"The first-lien loan is the best-compensated existing debt (expected recovery {exp['C2-1L'][0]}% against 74) but sits in a CCC credit with a fulcrum one tranche below; the CLO book's own limits cap the final at Avoid.",
                "cite": f"{m_q}{m_prob}",
            },
            {
                "strategy": "Indexed Loans",
                "recommendation": "3 - MW",
                "basis": "Full",
                "rationale": "Hold the first-lien loan at index weight only if the index requires it; do not add before the priming risk is resolved.",
                "cite": f"{m_q}{m_new}",
            },
            {
                "strategy": "Indexed HY",
                "recommendation": "5 - Strong UW",
                "basis": "Full",
                "rationale": f"The notes recover nothing in the base case and {exp['C4-NOTES'][0]}% on a probability-weighted basis against a price of 23.",
                "cite": f"{m_q}{m_prob}",
            },
        ],
    )
    h.table(
        "snapshot.instrument_recommendation",
        [
            {
                "facility_id": "llg_tlb",
                "instrument": "First-Lien Term Loan B",
                "recommendation": "3 - MW",
                "valuation": "V3 - Fair",
                "rationale": f"Preferred among the existing debt; {upside} points of expected-recovery upside over the price is offset by priming and timing risk.",
                "cite": f"{m_q}{m_prob} {upside_s}",
            },
            {
                "facility_id": "llg_2l",
                "instrument": "Second-Lien Term Loan",
                "recommendation": "4 - Modest UW",
                "valuation": "V3 - Fair",
                "rationale": "Base-case fulcrum, but at 41 the price already pays for upside the weighted scenarios do not give it.",
                "cite": f"{m_q}{m_prob}",
            },
            {
                "facility_id": "llg_notes",
                "instrument": "8.25% Senior Notes due 2029",
                "recommendation": "5 - Strong UW",
                "valuation": "V4 - Unattractive",
                "rationale": "Zero recovery in the base case; the price is an option on the high case.",
                "cite": f"{m_q}{m_prob}",
            },
            {
                "facility_id": "NEW-1",
                "instrument": "Proposed new-money first-out term loan (indicative)",
                "recommendation": "N/A",
                "valuation": "V2 - Attractive",
                "rationale": "Attractive at talk, but terms are indicative and no commitment exists; revisit on final terms.",
                "cite": m_new,
            },
        ],
    )
    h.table(
        "snapshot.thesis",
        [
            {
                "thesis": f"Larchmere cannot service its debt and rent from EBITDA, so a restructuring is the base case. The first lien is covered in every going-concern case and is the only existing instrument worth owning at 74; the second lien is the fulcrum and the notes are out of the money. Time is short: the grace period ends 15 October and the liquidity floor is reached in November {m_dist}{m_fwd}.",
                "cite": f"{m_dist}{m_fwd}",
            }
        ],
    )
    h.table(
        "snapshot.catalysts",
        [
            {
                "date_or_window": "2026-10-15",
                "event": "Grace period on the 15 September coupon ends",
                "direction": "Down",
                "watch_trigger": "Coupon not paid or not waived",
                "cite": m_dist,
            },
            {
                "date_or_window": "2026-10-19",
                "event": "Equity cure window closes",
                "direction": "Flat",
                "watch_trigger": "Sponsor notice and funding of the cure",
                "cite": m_cov,
            },
            {
                "date_or_window": "Q4 2026",
                "event": "Amend-and-extend with 150 of priming new money, or a Chapter 11 filing",
                "direction": "Up",
                "watch_trigger": "Signed support agreement among first-lien lenders",
                "cite": m_new,
            },
            {
                "date_or_window": "November 2026",
                "event": "Liquidity falls through the 50 covenant floor",
                "direction": "Down",
                "watch_trigger": "Month-end cash and revolver availability",
                "cite": m_fwd,
            },
            {
                "date_or_window": "2028-03-15",
                "event": "Revolver matures",
                "direction": "Down",
                "watch_trigger": "Extension or repayment",
                "cite": syn(h, "facility_terms"),
            },
        ],
    )
    h.table(
        "cp6.challenge",
        [
            {
                "claim": "Bull: the first lien is covered in every going-concern case, so 74 is cheap.",
                "counter_evidence": "Stress recovery is below par, the sponsor's priming loan would rank ahead, and a CLO cannot hold it above its limits.",
                "resolution": "Hold at MW for unconstrained strategies; Avoid for the CLO book.",
                "what_would_change_view": "A signed support agreement that excludes priming; or price below 65.",
                "cite": f"{m_q}{m_new}{m_port}",
            },
            {
                "claim": "Bear: the notes are worthless and the second lien is the fulcrum, so sell both.",
                "counter_evidence": "The high-case recovery is 54.5% for the notes and the sponsor may fund the cure.",
                "resolution": "Strong UW on the notes; Modest UW on the second lien, whose price already reflects the fulcrum.",
                "what_would_change_view": "A funded cure with a standstill from the notes holders.",
                "cite": f"{m_prob}{m_own}",
            },
            {
                "claim": "The sponsor will protect its equity with a cure and a rescue.",
                "counter_evidence": "The sponsor proposed priming debt, not equity, and the equity is out of the money in every case.",
                "resolution": "Treat the cure as unlikely; plan for a filing.",
                "what_would_change_view": "Sponsor notice of cure funding before 19 October.",
                "cite": f"{m_own}{m_cov}",
            },
        ],
    )
    h.table("cp6.portfolio_recommendation", cp6_rows(fit_res, UNCAPPED))
    h.analysis(
        f"The recommendation that survives the strongest challenge is 3 - MW on the first-lien loan, 4 - Modest UW on the second lien, 5 - Strong UW on the notes, and Avoid for the Fenwick Park CLO. "
        f"The CLO book holds {fit_row['current_exposure_pct_nav_pct']} of NAV in the first-lien loan against a 2.5% Hard single-issuer limit, so Portfolio Fit is {fit_row['verdict']} and caps the final at {fit_row['recommendation_cap']} {m_port}.\n\n"
        f"By Strategy the uncapped views are CLO 3 - MW, Indexed Loans 3 - MW and Indexed HY 5 - Strong UW. The decision rests on expected recoveries of {exp['C2-1L'][0]}%, {exp['C3-2L'][0]}% and {exp['C4-NOTES'][0]}% by class against prices of 74, 41 and 23 {m_prob}{m_q}.\n\n"
        f"The strongest challenge is the sponsor's priming proposal: 150 of first-out money would rank ahead of every existing class {m_new}. It is why the first lien is MW and not overweight. Catalysts begin on 15 October. Confidence is Medium-Low; the decision is conditional on the analyst-set enterprise values."
    )
    h.gaps(
        "- Position sizing: not part of the Recommendation; the CLO book's maximum size for the loan is zero under the Fit result.\n"
        "- Independent valuation and agency thresholds: not in the pack (CP-4C and CP-2H); both condition the view."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
