"""Larchmere CP-3D: market-implied risk (synthetic dealer quotes; implied default from the credit triangle)."""

from __future__ import annotations

from core import Ctx, Handoff, fpct, plain

from . import derived as X
from . import facts as F
from .facts import syn

SENIORITY = {"llg_tlb": "First lien", "llg_2l": "Second lien", "llg_notes": "Senior unsecured"}


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-3D",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1"],
        fixture_file="larchmere/cp_3d.py",
    )
    h.qa("Restricted")
    mk = X.market()
    m_q, m_rec, m_terms, m_rf, m_rat = (
        syn(h, k)
        for k in ("quotes", "recoveries_market", "facility_terms", "risk_free_3y", "ratings")
    )
    obs = []
    for fid in ("llg_tlb", "llg_2l", "llg_notes"):
        r = mk[fid]
        t = F.val("facility_terms")[fid]
        notes = fid == "llg_notes"
        obs.append(
            {
                "security_id": fid,
                "price": plain(r["price"]),
                "yield_pct": fpct(r["yld"], 1) if notes else None,
                "spread_or_dm_bps": plain(r["spread"]),
                "metric_basis": "STW" if notes else "3Y DM",
                "quote_type": "Dealer quote",
                "maturity_or_call_date": t["maturity"],
                "seniority": SENIORITY[fid],
                "level_date": "2026-10-01",
                "freshness": "Current",
                "cite": f"{m_q}{m_terms}{m_rf if notes else ''} {r['yld_s'] + ' ' + r['spread_s'] if notes else r['spread_s']}",
            }
        )
    h.table("cp3d.observations", obs)
    risk = []
    for fid in ("llg_tlb", "llg_2l", "llg_notes"):
        r = mk[fid]
        risk.append(
            {
                "security_id": fid,
                "model": "Credit triangle (reduced form)",
                "horizon_years": "3",
                "recovery_assumption_pct": fpct(r["recovery"], 0),
                "implied_pd_pct": fpct(r["pd"], 1),
                "implied_loss_pct": fpct(r["loss"], 1),
                "break_even_spread_bps": plain(r["be"]),
                "formula": "hazard = spread / (1 - recovery); PD(3y) = 1 - (1 - hazard)^3; loss = PD x (1 - recovery)",
                "limitation": "Single-dealer quote; ignores accrued interest, liquidity premium and the timing of default.",
                "cite": f"{m_q}{m_rec} {r['pd_s']}",
            }
        )
    h.table("cp3d.implied_risk", risk)
    wf = {r["class_id"]: r for r in X.waterfall(X.enterprise_values()["Going concern: base"][2])}
    stress = {r["class_id"]: r for r in X.waterfall(X.enterprise_values()["Going concern: low"][2])}
    high = {r["class_id"]: r for r in X.waterfall(X.enterprise_values()["Going concern: high"][2])}
    m_ev = syn(h, "ev_multiples")
    h.table(
        "cp3d.market_vs_fundamental",
        [
            {
                "implication": "The market prices the first-lien loan at 74, a 26-point discount to par",
                "fundamental_evidence": f"Analyst recoveries for the first lien are {plain(stress['C2-1L']['pct'], 1)}% in the stress case and {plain(wf['C2-1L']['pct'], 0)}% in the base case, so the market is more bearish than the fundamentals.",
                "alignment": "Divergent",
                "basis": "Analyst enterprise-value scenarios at 5.5x and 7.25x SSIM EBITDA",
                "open_question": "Is the discount a liquidity and timing premium for a priming risk the scenarios do not capture?",
                "cite": f"{m_q}{m_ev}",
            },
            {
                "implication": "The second-lien loan at 41 prices near the base-case recovery",
                "fundamental_evidence": f"The base-case recovery for the second lien is {plain(wf['C3-2L']['pct'], 1)}%, against a price of 41.",
                "alignment": "Aligned",
                "basis": "Analyst base-case waterfall",
                "open_question": "Does the market expect the second lien to be the fulcrum?",
                "cite": f"{m_q}{m_ev}",
            },
            {
                "implication": "The notes at 23 price above the base-case recovery of zero",
                "fundamental_evidence": f"The base-case recovery for the notes is {plain(wf['C4-NOTES']['pct'], 0)}% and the high case {plain(high['C4-NOTES']['pct'], 1)}%, so the price is an option on a better outcome.",
                "alignment": "Divergent",
                "basis": "Analyst base-case and high-case waterfalls",
                "open_question": "What probability of the high case is implied by a price of 23?",
                "cite": f"{m_q}{m_ev}",
            },
        ],
    )
    t, n = mk["llg_tlb"], mk["llg_notes"]
    haz_t, haz_s = (plain(mk[k]["hazard"] * 100, 1) for k in ("llg_tlb", "llg_2l"))
    h.analysis(
        f"The market is pricing a high chance of default and heavy losses across the structure: the first-lien loan at 74 implies a {plain(t['pd'], 1)}% three-year default probability and a loss of {plain(t['loss'], 1)}% ({t['pd_s']}), "
        f"and the unsecured notes at 23 imply {plain(n['pd'], 1)}% and a loss of {plain(n['loss'], 1)}% {m_q}{m_rec}. "
        f"The levels are consistent with the Caa2 / CCC corporate ratings and negative outlooks recorded in CP-1A {m_rat}. "
        "Module view: the quotes are Current (1 October 2026) but are single-dealer, so they are indicative, not tradable. Confidence is Medium-Low.\n\n"
        f"Loan levels translate to a three-year discount margin of {plain(t['spread'])} bps for the first lien and {plain(mk['llg_2l']['spread'])} bps for the second lien; the notes yield {plain(n['yld'], 1)}% and trade {plain(n['spread'])} bps over the three-year reference {m_rf}. "
        f"The first and second lien imply almost the same hazard rate ({haz_t}% and {haz_s}% a year), which is consistent: the market prices the same default event and differs only in recoveries.\n\n"
        "Against the fundamentals the market is more bearish than the analyst on the first lien and more hopeful on the notes. What remains unpriced is the sponsor's priming proposal, which would move value from the existing first lien to new money."
    )
    h.gaps(
        "- Single dealer: only one dealer file is in the pack. Effect: quotes are not corroborated and bid-ask is not shown here. Lifted by: a second dealer or TRACE-type prints.\n"
        "- Recovery assumptions: the 65%, 25% and 10% are market-convention inputs, not extracted. Effect: the implied PD scales with them. Lifted by: the recovery waterfall in CP-4C."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
