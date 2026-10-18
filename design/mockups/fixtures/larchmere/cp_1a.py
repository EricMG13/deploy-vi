"""Larchmere CP-1A: business and transaction fact pack (synthetic)."""

from __future__ import annotations

from core import GAP, Ctx, Handoff, compute, plain
from helpers import join_marks

from . import derived as X
from . import facts as F
from .facts import syn


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-1A",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1"],
        fixture_file="larchmere/cp_1a.py",
    )
    h.qa("Restricted")
    prof, bo = F.val("profile"), F.val("business_overview")
    own = F.val("ownership_terms")
    rat = F.val("ratings")
    m_prof, m_bo, m_own, m_rat, m_ev = (
        syn(h, k)
        for k in ("profile", "business_overview", "ownership_terms", "ratings", "event_history")
    )
    h.table(
        "snapshot.company_profile",
        [
            {
                "morningstar_issuer_id": GAP,
                "sector": prof["sector"],
                "country": prof["country"],
                "shareholders": prof["shareholders"],
                "management": prof["management"],
                "corp_rating_moodys": rat["moodys"][0],
                "corp_rating_sp": rat["sp"][0],
                "corp_rating_fitch": GAP,
                "outlook_moodys": rat["moodys"][1],
                "outlook_sp": rat["sp"][1],
                "outlook_fitch": GAP,
                "sponsor_quality": "Low",
                "listed": "No",
                "ticker": GAP,
                "cite": join_marks(m_prof, m_rat),
            }
        ],
    )
    h.table("snapshot.business_description", [{"description": bo["description"], "cite": m_bo}])
    shares = {}
    for sid in ("seg_gulf_coast", "seg_mid_south", "seg_online"):
        sh, s = compute(
            f"{sid} share of LTM revenue",
            "seg / total * 100",
            1,
            "%",
            seg=X.segment_ltm(sid),
            total=X.ltm("revenue")[0],
        )
        shares[sid] = (sh, s)
    m_seg = syn(h, "segment_revenue")
    h.table(
        "cp1a.business_facts",
        [
            {
                "item": "Segment mix",
                "fact": f"Gulf Coast {plain(shares['seg_gulf_coast'][0])}%, Mid-South {plain(shares['seg_mid_south'][0])}% and Online {plain(shares['seg_online'][0])}% of LTM revenue.",
                "risk_mechanism": "Two drive-in regional markets carry almost 90% of revenue and both are losing share to new competitors.",
                "credit_implication": "Revenue stabilisation depends on Gulf Coast, where hotel occupancy has fallen from 87% to 77%.",
                "evidence_quality": "Issuer-stated",
                "cite": m_seg + " " + " ".join(v[1] for v in shares.values()),
            },
            {
                "item": "Master lease",
                "fact": f"{bo['leased_properties']} of {F.val('operating_counts')['properties'][1]} properties are leased from {F.LANDLORD} under one master lease; cash rent is 62 LTM with a 1.5% escalator.",
                "risk_mechanism": "Rent is a fixed claim that ranks ahead of funded creditors in practice and cross-defaults with the funded debt.",
                "credit_implication": "The lessor is a pivotal party in any restructuring, and rent shrinks distributable value in every scenario.",
                "evidence_quality": "Audited",
                "cite": join_marks(m_bo, m_own, syn(h, "lease_cash")),
            },
            {
                "item": "Customer base and loyalty",
                "fact": f"About {bo['loyalty_share_pct']}% of gaming revenue comes from rated loyalty-programme players; gaming is {bo['gaming_share_pct']}% of revenue.",
                "risk_mechanism": "A discretionary, drive-in customer base trades down quickly when real incomes fall.",
                "credit_implication": "EBITDA is cyclical and operating deleverage is high, so a revenue decline of about 11% removes roughly a quarter of EBITDA.",
                "evidence_quality": "Issuer-stated",
                "cite": m_bo,
            },
            {
                "item": "Online business",
                "fact": "Online (sports betting and iGaming) is 12% of revenue and about 192 thousand monthly active players, flat to down on a year ago.",
                "risk_mechanism": "A sub-scale online arm without a growth case consumes marketing spend and adds little to cash flow.",
                "credit_implication": "Online has limited value in a sale and sits in a subsidiary that can be designated unrestricted, so it is a drop-down candidate.",
                "evidence_quality": "Issuer-stated",
                "cite": join_marks(m_seg, syn(h, "operating_kpis")),
            },
        ],
    )
    h.table(
        "cp1a.ownership_governance",
        [
            {
                "topic": "Sponsor control and support",
                "fact": f"{F.SPONSOR} holds {own['sponsor_stake_pct']}% and appoints four of {own['board']}; no equity support is committed.",
                "risk_direction": "Negative",
                "credit_implication": "Support depends on a negotiation; the equity cure is available but the sponsor has not committed to use it.",
                "cite": m_own,
            },
            {
                "topic": "Master-lease consent and cross-default",
                "fact": f"Under the master lease, {own['lease_cross_default']}, and {own['lessor_consent']}.",
                "risk_direction": "Negative",
                "credit_implication": "A funded-debt default can accelerate the lease, so the landlord holds a veto over any out-of-court or court path.",
                "cite": m_own,
            },
        ],
    )
    h.table(
        "cp1a.transactions_events",
        [
            {
                "event_date": d,
                "event": e,
                "status": st,
                "credit_relevance": rel,
                "perimeter_change": pc,
                "cite": m_ev,
            }
            for d, e, st, rel, pc in F.val("event_history")
        ],
    )
    h.table(
        "cp1a.ratings_register",
        [
            {
                "agency": "Moody's",
                "scope": "Corporate family rating",
                "rating": rat["moodys"][0],
                "outlook": rat["moodys"][1],
                "rating_date": rat["moodys"][2],
                "rationale": f"Lowered from {rat['moodys'][3]} on liquidity and covenant risk; outlook negative.",
                "cite": m_rat,
            },
            {
                "agency": "S&P",
                "scope": "Issuer credit rating",
                "rating": rat["sp"][0],
                "outlook": rat["sp"][1],
                "rating_date": rat["sp"][2],
                "rationale": f"Lowered from {rat['sp'][3]}; default seen as a near-term possibility absent a restructuring.",
                "cite": m_rat,
            },
        ],
    )
    h.analysis(
        f"The facts that matter most to a creditor are the rent burden, the sponsor's lack of committed support and the missed coupon. Larchmere is a sponsor-owned regional casino operator with eleven properties in four states, "
        f"seven of them on one master lease and four owned {m_bo}. Its ratings are Caa2 (negative) from Moody's since 21 July 2026 and CCC (negative) from S&P since 4 August 2026 {m_rat}.\n\n"
        f"Revenue is concentrated: Gulf Coast is {plain(shares['seg_gulf_coast'][0])}% and Mid-South {plain(shares['seg_mid_south'][0])}% of LTM revenue, with Online at {plain(shares['seg_online'][0])}% {m_seg}. "
        f"The sponsor holds {own['sponsor_stake_pct']}% of the equity and has committed no support {m_own}, and the landlord holds consent and cross-default rights over any restructuring.\n\n"
        f"The event sequence shows a company moving from a covenant reset in June 2025 to a missed coupon on 15 September 2026, a late compliance certificate showing a leverage breach on 21 September and a sponsor proposal for 150 of priming new-money debt on 22 September {m_ev}. "
        "Confidence in this module is Medium; every fact is from the company's own documents, which a Restricted pack cannot corroborate."
    )
    h.gaps(
        "- Morningstar issuer id and Fitch rating: none in the pack. Effect: blank cells in the profile. Lifted by: a Morningstar export.\n"
        "- Management biographies, tenure and compensation: not in the pack. Effect: governance view is limited to ownership and lease terms. Lifted by: the proxy-style disclosure in the annual report.\n"
        "- Competitor supply by market: not in the pack; the loss-of-share claim rests on the company's own statistics. Lifted by: Deep Research (not approved) or a gaming-board market report."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
