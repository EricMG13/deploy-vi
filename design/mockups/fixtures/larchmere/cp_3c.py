"""Larchmere CP-3C: refinancing and LME risk (synthetic). Sources come from the Model's base-case projection."""

from __future__ import annotations

from decimal import Decimal

from core import Ctx, D, Handoff, compute, plain

from . import derived as X
from . import facts as F
from .facts import syn

YEARS = [2026, 2027, 2028, 2029]


def maturities() -> dict[int, Decimal]:
    """Principal falling due by calendar year: term loan B amortisation, 2028 revolver and TLB balance, 2029 second lien and notes."""
    am = F.val("projection_floor")["tlb_amort"]
    tlb = X.facility_balance("llg_tlb", "JUN30_2026")
    out = {2026: D(am[2026]), 2027: D(am[2027])}
    tlb_2028 = tlb - out[2026] - out[2027]
    out[2028] = X.facility_balance("llg_rcf", "JUN30_2026") + tlb_2028
    out[2029] = X.facility_balance("llg_2l", "JUN30_2026") + X.facility_balance(
        "llg_notes", "JUN30_2026"
    )
    return out


def exposure_cases() -> dict[str, dict[str, Decimal]]:
    """Loss exposure (claim less recovery) by class and case: Base, Stress, and LME (base EV after a 150 priming new-money loan)."""
    evs = X.enterprise_values()
    nm = D(F.val("new_money")["size"])
    cases = {
        "Base": X.waterfall(evs["Going concern: base"][2]),
        "Stress": X.waterfall(evs["Going concern: low"][2]),
        "LME": X.waterfall(evs["Going concern: base"][2], nm),
    }
    out = {}
    for case, rows in cases.items():
        out[case] = {r["class_id"]: r["claim"] - r["allocation"] for r in rows}
    return out


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-3C",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "CP-4", "MODEL", "PROJECTION"],
        fixture_file="larchmere/cp_3c.py",
    )
    h.qa("Restricted")
    X.require(ctx, run_id, "MODEL", "PROJECTION")
    mb = ctx.models[run_id]
    cp4 = ctx.get(run_id, "CP-4")
    caps = {r["basket"]: r for r in cp4.rows("cp4.capacity_register")}
    m_terms, m_pf, m_cash, m_lp, m_b, m_new, m_dist, m_own = (
        syn(h, k)
        for k in (
            "facility_terms",
            "projection_floor",
            "cash_balance",
            "legal_provisions",
            "baskets",
            "new_money",
            "distress_events",
            "ownership_terms",
        )
    )
    mat = maturities()
    rows, gaps = [], {}
    for y in YEARS:
        if y == 2026:
            src = X.cash("JUN30_2026")
            src_s = m_cash
        else:
            col = (
                next(c for c in mb.cols if c.column_id == f"PROJ:BASE:FY{y - 1}")
                if y - 1 <= 2028
                else None
            )
            cash = mb.L("cash_closing", col).value if col else Decimal(0)
            src = max(D(cash), Decimal(0))
            src_s = m_pf
        gap = max(mat[y] - src, Decimal(0))
        gaps[y] = gap
        calc = (
            compute(
                f"FY{y} funding gap", "maturing - sources", 2, "", maturing=mat[y], sources=src
            )[1]
            if mat[y] > src
            else "calc: sources exceed the maturing amount, so the gap is 0"
        )
        rows.append(
            {
                "fiscal_year": str(y),
                "maturing_amount": plain(mat[y], 2),
                "sources_available": plain(src, 2),
                "funding_gap": plain(gap, 2),
                "currency": "USD",
                "unit": "MILLIONS",
                "pressure": "Low" if gap == 0 else "Medium" if gap < 50 else "High",
                "cite": f"{m_terms}{src_s} {calc}",
            }
        )
    h.table("cp3c.maturity_pressure", rows)
    inv = caps["Unrestricted-subsidiary investment (drop-down)"]
    fcl = caps["Free-and-clear incremental first lien"]
    h.table(
        "cp3c.lme_capacity",
        [
            {
                "indicator": "Unrestricted-subsidiary drop-down",
                "available": "Available",
                "evidence": f"Investment basket with {inv['remaining']} remaining and no leverage test; designation of the online business is permitted.",
                "paths_enabled": "Amend-and-extend with an uptier; asset-backed new money",
                "cite": f"{m_lp}{m_b}",
            },
            {
                "indicator": "Non-pro-rata open-market purchases",
                "available": "Available",
                "evidence": "The Borrower and its affiliates may buy loans in open-market purchases that need not be offered to all lenders.",
                "paths_enabled": "Uptier by a participating group",
                "cite": m_lp,
            },
            {
                "indicator": "Weak sacred rights (Required Lender amendment of priority)",
                "available": "Available",
                "evidence": "Weak: lien and payment priority can be changed with 50.1% consent; only each lender's own amount, rate and maturity are protected.",
                "paths_enabled": "Amend-and-extend with an uptier; subordination of the second lien",
                "cite": m_lp,
            },
            {
                "indicator": "Free-and-clear priming capacity",
                "available": "Available",
                "evidence": f"{fcl['remaining']} of first-lien capacity outside the ratio test; the 150 sponsor proposal needs a majority amendment for the rest.",
                "paths_enabled": "New-money first-out loan",
                "cite": f"{m_b}{m_new}",
            },
            {
                "indicator": "Cooperation agreement among creditors",
                "available": "Unclear",
                "evidence": "No lender group or cooperation agreement is evidenced in the pack.",
                "paths_enabled": "Would block an uptier if the excluded lenders organised",
                "cite": m_own,
            },
        ],
    )
    h.table(
        "cp3c.refinancing_paths",
        [
            {
                "path": "Amend-and-extend with an uptier",
                "feasibility": "High",
                "likelihood_direction": "Positive",
                "evidence_for": "The sponsor has proposed it; documents allow it with Required Lender consent; 150 of new money is sized.",
                "evidence_against": "It buys perhaps 12 months while fixed charges still exceed EBITDA; excluded lenders may sue.",
                "creditor_impact": "Participating first-lien lenders improve; the second lien and notes are primed.",
                "cite": f"{m_lp}{m_new}",
            },
            {
                "path": "Pre-packaged Chapter 11",
                "feasibility": "Medium",
                "likelihood_direction": "Positive",
                "evidence_for": "Advisers retained in August; the grace period and cure window both close in October; the capital structure cannot be serviced.",
                "evidence_against": "Gaming-regulator approvals in four states and the landlord's consent slow it.",
                "creditor_impact": "Debt-for-equity exchange; the fulcrum is the second lien in the base case.",
                "cite": f"{m_dist}{m_own}",
            },
            {
                "path": "Out-of-court exchange of the notes",
                "feasibility": "Medium",
                "likelihood_direction": "Neutral",
                "evidence_for": "Notes are 200 and trade at 23, so holders may accept equity or a second-lien exchange.",
                "evidence_against": "It does not fix liquidity or the 2028 maturities, and needs 90% acceptance.",
                "creditor_impact": "Notes holders trade a claim for equity; senior lenders are unaffected.",
                "cite": f"{m_dist}{m_terms}",
            },
            {
                "path": "Sponsor equity injection and cure",
                "feasibility": "Low",
                "likelihood_direction": "Negative",
                "evidence_for": "The cure is available once and sized at 34.8 of deemed EBITDA.",
                "evidence_against": "The sponsor has proposed priming debt, not equity, and the equity is out of the money.",
                "creditor_impact": "A cure delays the breach by a quarter and does not reduce debt.",
                "cite": m_own,
            },
        ],
    )
    ex = exposure_cases()
    names = {
        "C2-1L": "First-lien (revolver and term loan B)",
        "C3-2L": "Second-lien term loan",
        "C4-NOTES": "Senior unsecured notes",
    }
    prim = {"C2-1L": "Medium", "C3-2L": "High", "C4-NOTES": "High"}
    exp_rows = []
    for case, cid_vals in ex.items():
        for cid, nm_ in names.items():
            v, s = compute(
                f"{case} loss exposure of {nm_}",
                "claim - recovery",
                1,
                "",
                claim=X.claims()[cid],
                recovery=X.claims()[cid] - cid_vals[cid],
            )
            exp_rows.append(
                {
                    "creditor_class": nm_,
                    "case_name": case,
                    "exposure": plain(v),
                    "currency": "USD",
                    "unit": "MILLIONS",
                    "priming_risk": prim[cid],
                    "cite": f"{m_new}{m_b} {s}",
                }
            )
    h.table("cp3c.creditor_exposure", exp_rows)
    h.analysis(
        f"Refinancing pressure is concentrated in 2028, when {plain(mat[2028], 2)} falls due (the revolver on 15 March and the term loan B on 30 September) against no projected source, a gap of {plain(gaps[2028], 2)} {m_terms}{m_pf}. "
        f"The earlier years are small: {plain(mat[2026], 2)} in 2026 and {plain(mat[2027], 2)} in 2027, but even these are unfunded from 2027 because the base case has no cash left. The most credible route is an amend-and-extend with an uptier in the short run and a pre-packaged Chapter 11 as the end state. Confidence is Medium.\n\n"
        f"The documents make the uptier executable: {inv['remaining']} of unrestricted-subsidiary investment capacity, non-pro-rata open-market purchases and 50.1% amendments {m_lp}{m_b}. The 150 sponsor proposal exceeds free-and-clear capacity of {fcl['remaining']}, so it needs a majority amendment {m_new}.\n\n"
        f"Creditor exposure splits by class and case. In the base case the second lien loses {plain(ex['Base']['C3-2L'])} and the notes {plain(ex['Base']['C4-NOTES'])}; in the stress case the first lien itself loses {plain(ex['Stress']['C2-1L'])}; and a 150 priming loan takes the first-lien loss from {plain(ex['Base']['C2-1L'])} to {plain(ex['LME']['C2-1L'])} while leaving the junior classes unchanged."
    )
    h.gaps(
        "- Creditor group composition: no holder list or cooperation agreement in the pack. Effect: the ability of excluded lenders to resist an uptier is unclear. Lifted by: lender-group filings or adviser disclosures.\n"
        "- Sponsor intent on equity: only the priming proposal is evidenced. Lifted by: sponsor correspondence."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
