"""Larchmere CP-4C: restructuring and fulcrum (synthetic EV scenarios; waterfall computed from the claims)."""

from __future__ import annotations

from core import Ctx, D, Handoff, compute, fpct, fx, plain

from . import derived as X
from . import facts as F
from .facts import syn


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-4C",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "CP-4", "MODEL"],
        fixture_file="larchmere/cp_4c.py",
    )
    h.qa("Restricted")
    cov = X.covenant()
    cd = ctx.get(run_id, "CP-2D").rows("cp2d.runway")
    runway = {r["item"]: r["value"] for r in cd}
    m_dist, m_cov, m_terms, m_claims, m_evm, m_liq, m_prob, m_new, m_own, m_lp = (
        syn(h, k)
        for k in (
            "distress_events",
            "covenants",
            "facility_terms",
            "claims_other",
            "ev_multiples",
            "liquidation",
            "ev_probabilities",
            "new_money",
            "ownership_terms",
            "legal_provisions",
        )
    )
    m_fwd = syn(h, "forward_12m")
    coupon, coupon_s = compute(
        "missed coupon",
        "notes * rate / 100 / 2",
        2,
        "",
        notes=X.facility_balance("llg_notes", "JUN30_2026"),
        rate=F.val("debt_like_inputs")["coupon_pct"],
    )
    h.table(
        "cp4c.distress_gate",
        [
            {
                "trigger": "Missed interest payment, grace period running",
                "evidence": f"The 15 September 2026 coupon of {plain(coupon)} on the 8.25% notes is unpaid; the 30-day grace period ends 15 October 2026.",
                "event_date": "2026-09-15",
                "status": "Met",
                "cite": f"{m_dist}{m_terms} {coupon_s}",
            },
            {
                "trigger": "Financial covenant breach",
                "evidence": f"First-lien net leverage {plain(cov['lev'], 2)}x against 6.50x at 30 June 2026; certificate delivered late on 21 September; equity cure window to 19 October.",
                "event_date": "2026-09-21",
                "status": "Met",
                "cite": f"{m_cov} {cov['lev_s']}",
            },
            {
                "trigger": "Liquidity under 12 months of mandatory uses",
                "evidence": f"Accessible liquidity {runway['Accessible liquidity']} against mandatory uses of {runway['Mandatory uses 12m']}, a headroom of {runway['Headroom']} (CP-2D).",
                "event_date": F.AS_OF,
                "status": "Met",
                "cite": m_fwd,
            },
            {
                "trigger": "Going-concern language in the Q2 report",
                "evidence": "The 14 August 2026 quarterly report added going-concern language and named a 2028 refinancing risk.",
                "event_date": "2026-08-14",
                "status": "Met",
                "cite": m_dist,
            },
            {
                "trigger": "Court or formal insolvency process commenced",
                "evidence": "No filing, receivership or standstill is evidenced; the company remains in negotiations.",
                "event_date": "—",
                "status": "Not met",
                "cite": m_dist,
            },
            {
                "trigger": "Overall: distress gate",
                "evidence": "Three independent triggers are Met (missed coupon in grace, covenant breach, liquidity under 12 months); the gate is Met.",
                "event_date": F.AS_OF,
                "status": "Met",
                "cite": f"{m_dist}{m_cov}",
            },
        ],
    )
    claims = X.claims()
    cl_meta = {
        "C1-ADMIN": (
            "Administrative and priority claims",
            "Debtors in a filing",
            "Statutory priority",
            m_claims,
        ),
        "C2-1L": (
            "First-lien claims (revolver 200 and term loan B 1,050)",
            F.OPCO,
            "First lien on substantially all assets",
            m_terms,
        ),
        "C3-2L": ("Second-lien term loan", F.OPCO, "Second lien on the same collateral", m_terms),
        "C4-NOTES": ("8.25% Senior Notes due 2029", F.ISSUER, "Unsecured", m_terms),
        "C5-TRADE": (
            "Trade and other unsecured claims",
            "Operating subsidiaries",
            "Unsecured",
            m_claims,
        ),
    }
    h.table(
        "cp4c.claims_register",
        [
            {
                "class_id": cid,
                "claim": cl_meta[cid][0],
                "obligor": cl_meta[cid][1],
                "amount": plain(claims[cid]),
                "currency": "USD",
                "unit": "MILLIONS",
                "security": cl_meta[cid][2],
                "priority_rank": str(i),
                "cite": cl_meta[cid][3],
            }
            for i, (cid, _) in enumerate(X.CLASSES, 1)
        ],
    )
    evs = X.enterprise_values()
    h.table(
        "cp4c.ev_scenarios",
        [
            {
                "scenario": sc,
                "valuation_basis": "LTM SSIM EBITDA times a going-concern multiple"
                if sc != "Liquidation"
                else "Appraised property, equipment and licences less a forced-sale discount",
                "metric_value": plain(m),
                "multiple_x": fx(x) if sc != "Liquidation" else None,
                "ev": plain(ev),
                "currency": "USD",
                "unit": "MILLIONS",
                "cite": f"{m_evm if sc != 'Liquidation' else m_liq} {s}",
            }
            for sc, (m, x, ev, s) in evs.items()
        ],
    )
    rec_rows = []
    wfs = {}
    for sc, (_m, _x, ev, _s) in evs.items():
        wfs[sc] = X.waterfall(ev)
        for r in wfs[sc]:
            pct, s = compute(
                f"recovery of {r['class_id']}",
                "alloc / claim * 100",
                0 if r["allocation"] == r["claim"] else 1,
                "%",
                alloc=r["allocation"],
                claim=r["claim"],
            )
            rec_rows.append(
                {
                    "scenario": sc,
                    "class_id": r["class_id"],
                    "allowed_claim": plain(r["claim"]),
                    "available_value": plain(r["available"]),
                    "allocation": plain(r["allocation"]),
                    "residual": plain(r["residual"]),
                    "recovery_pct": fpct(pct, 0 if pct == 100 else 1),
                    "fulcrum": "Yes" if r["fulcrum"] else "No",
                    "currency": "USD",
                    "unit": "MILLIONS",
                    "cite": s,
                }
            )
    h.table("cp4c.recoveries", rec_rows)
    h.table(
        "cp4c.paths",
        [
            {
                "path": "Amend-and-extend with an uptier",
                "process": "Out of court: Required Lender amendment, 150 new-money first-out loan, maturities extended to 2030",
                "consent": "50.1% of first-lien lenders; no second-lien or notes vote",
                "new_money": f"{F.val('new_money')['size']} first-out term loan at SOFR + 950-1,050, OID 96",
                "class_treatment": "Participating first-lien lenders exchange into the new tranche; the rest, the second lien and the notes are primed",
                "milestones": "Term sheet and lender group in October; closing before the 2026 year-end; extension to 2030",
                "blockers": "Excluded lenders may litigate; the landlord must consent; liquidity still short without new money",
                "likelihood_class": "Medium",
                "cite": f"{m_new}{m_lp}",
            },
            {
                "path": "Pre-packaged Chapter 11",
                "process": "Court: plan solicited before filing, with a debt-for-equity exchange",
                "consent": "Two thirds in amount and a majority in number of each impaired class",
                "new_money": "Debtor-in-possession loan sized to the 12-month gap",
                "class_treatment": "First lien paid in full or reinstated in the base case; second lien takes most of the equity as fulcrum; notes receive warrants or nothing",
                "milestones": "Gaming-regulator pre-clearance in four states; filing before the grace period lapses; confirmation within 90 days",
                "blockers": "Regulatory approvals; the landlord's lease assumption; sponsor opposition to losing equity",
                "likelihood_class": "High",
                "cite": f"{m_dist}{m_own}",
            },
            {
                "path": "Out-of-court exchange of the notes",
                "process": "Exchange offer for second-lien or equity-linked securities",
                "consent": "Each holder; minimum participation of 90%",
                "new_money": "None",
                "class_treatment": "Notes holders exchange 200 of claims for equity or a junior security",
                "milestones": "Launch within the grace period; settle in 30 days",
                "blockers": "Does not solve liquidity or the 2028 maturities; holdouts",
                "likelihood_class": "Low",
                "cite": f"{m_dist}{m_terms}",
            },
        ],
    )
    base, stress, high = (
        wfs["Going concern: base"],
        wfs["Going concern: low"],
        wfs["Going concern: high"],
    )
    exp = X.expected_recovery()
    h.analysis(
        f"The distress gate is Met: the coupon on the notes is unpaid inside its grace period, the covenant is breached and liquidity covers less than 12 months of mandatory uses {m_dist}{m_cov}. "
        f"The most credible path is a pre-packaged Chapter 11, with an amend-and-extend with an uptier as the sponsor's first try. In the base case ({fx(D(F.val('ev_multiples')['base']))} of SSIM EBITDA, EV {plain(evs['Going concern: base'][2])}) the fulcrum is the second lien, recovering {plain(base[2]['pct'], 1)}%; "
        f"in the stress case the fulcrum is the first lien at {plain(stress[1]['pct'], 1)}% {m_evm}. Confidence is Medium-Low, because the EV rests on analyst multiples.\n\n"
        f"Recoveries by class: first lien {plain(base[1]['pct'], 0)}% base, {plain(stress[1]['pct'], 1)}% stress; second lien {plain(base[2]['pct'], 1)}% base and {plain(high[2]['pct'], 0)}% in the high case; notes {plain(base[3]['pct'], 0)}% base and {plain(high[3]['pct'], 1)}% high (the notes are the fulcrum there). "
        f"The liquidation case, at {plain(evs['Liquidation'][2])}, leaves the first lien with {plain(wfs['Liquidation'][1]['pct'], 1)}% {m_liq}.\n\n"
        f"Weighted {F.val('ev_probabilities')['low']}/{F.val('ev_probabilities')['base']}/{F.val('ev_probabilities')['high']}/{F.val('ev_probabilities')['liquidation']} across stress, base, high and liquidation {m_prob}, the expected recoveries are {plain(exp['C2-1L'][0], 1)}% on the first lien, {plain(exp['C3-2L'][0], 1)}% on the second lien and {plain(exp['C4-NOTES'][0], 1)}% on the notes ({exp['C3-2L'][1]}). "
        "Against dealer prices of 74, 41 and 23, the market is more bearish than this view on the first lien and more hopeful on the notes.\n\n"
        f"The master lease is assumed rather than rejected in every scenario, so rent is an operating cost and the landlord is not in the waterfall; a rejection claim would reduce every recovery. A {plain(D(F.val('new_money')['size']))} priming loan would take its full amount off the value available to the existing classes {m_new}."
    )
    h.gaps(
        "- Independent valuation: none; the multiples are analyst-set. Effect: every recovery moves one-for-one with EV. Lifted by: an adviser's valuation.\n"
        "- Master-lease treatment: assumed rather than rejected; no lessor term sheet. Effect: a rejection claim would be additional and senior in practice. Lifted by: the landlord's position.\n"
        "- Intercreditor and plan mechanics: not in the pack; classes are assumed to follow strict priority."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
