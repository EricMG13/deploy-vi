"""Larchmere CP-2A: downside pathways, sensitivities and triggers (synthetic)."""

from __future__ import annotations

from core import Ctx, D, Handoff, compute, plain

from . import derived as X
from . import facts as F
from .facts import syn


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2A",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "CP-2", "MODEL"],
        fixture_file="larchmere/cp_2a.py",
    )
    h.qa("Restricted")
    si = F.val("sensitivity_inputs")
    fwd = F.val("forward_12m")
    m_si, m_fwd, m_dist, m_cov, m_seg, m_terms = (
        syn(h, k)
        for k in (
            "sensitivity_inputs",
            "forward_12m",
            "distress_events",
            "covenants",
            "segment_revenue",
            "facility_terms",
        )
    )
    floating = sum(
        (X.facility_balance(f, "JUN30_2026") for f in ("llg_rcf", "llg_tlb", "llg_2l")), D(0)
    )
    rent = X.ltm("lease_cash")[0]
    sens = [
        (
            "Adjusted EBITDA 10% below forecast",
            "Forward 12-month SSIM EBITDA",
            "Shock x forward EBITDA",
            "-ebitda * shock / 100",
            dict(ebitda=fwd["adjusted_ebitda"], shock=si["ebitda_shock_pct"]),
            "Costs are largely fixed, so EBITDA misses go straight to liquidity.",
            m_fwd,
        ),
        (
            "Gulf Coast revenue 5% lower",
            "LTM Gulf Coast revenue 685",
            "Shock x revenue x flow-through",
            "-seg * shock / 100 * flow / 100",
            dict(
                seg=X.segment_ltm("seg_gulf_coast"),
                shock=si["revenue_shock_pct"],
                flow=si["flow_through_pct"],
            ),
            "The largest segment is also the weakest market.",
            m_seg,
        ),
        (
            "Mid-South revenue 5% lower",
            "LTM Mid-South revenue 556",
            "Shock x revenue x flow-through",
            "-seg * shock / 100 * flow / 100",
            dict(
                seg=X.segment_ltm("seg_mid_south"),
                shock=si["revenue_shock_pct"],
                flow=si["flow_through_pct"],
            ),
            "A second competitor opening would have a similar effect.",
            m_seg,
        ),
        (
            "Term SOFR 100 bps higher",
            "Floating-rate debt 1,500 above the floors",
            "Shock x floating debt",
            "-debt * bps / 10000",
            dict(debt=floating, bps=si["sofr_shock_bps"]),
            "All three loans float and no hedge is in place.",
            m_terms,
        ),
        (
            "Rent escalator 1 pp higher",
            "LTM cash rent",
            "Shock x rent",
            "-rent * pp / 100",
            dict(rent=rent, pp=si["rent_shock_pp"]),
            "The lease escalator is contractual, so rent is the least sensitive line.",
            m_si,
        ),
        (
            "Maintenance capex cut by 25%",
            "Forward maintenance capex",
            "Cut x capex",
            "capex * cut / 100",
            dict(capex=fwd["maintenance_capex"], cut=si["capex_cut_pct"]),
            "A mitigant, at the cost of property quality and revenue.",
            m_fwd,
        ),
    ]
    srows = []
    for name, basis, method, expr, vals, interp, mark in sens:
        v, s = compute(name, expr, 1, "", **vals)
        srows.append(
            {
                "sensitivity": name,
                "input_basis": basis,
                "method": method,
                "result": plain(v, 1),
                "unit_label": "USD millions, 12-month liquidity",
                "interpretation": interp,
                "status": "Calculated",
                "cite": f"{mark} {s}",
            }
        )
    h.table("cp2a.sensitivities", srows)
    worst = min(srows, key=lambda r: D(r["result"]))
    sofr_r = next(r for r in srows if "SOFR" in r["sensitivity"])["result"]
    capex_r = next(r for r in srows if "capex" in r["sensitivity"])["result"]
    gc_share, _ = compute(
        "Gulf Coast share of LTM revenue",
        "seg / total * 100",
        1,
        "",
        seg=X.segment_ltm("seg_gulf_coast"),
        total=X.ltm("revenue")[0],
    )
    h.table(
        "cp2a.downside_paths",
        [
            {
                "path_id": "P1",
                "driver": "Missed notes coupon becomes an event of default",
                "first_break": "15 October 2026 grace expiry",
                "transmission": "Notes default cross-defaults the credit agreement after 30 days and the master lease after 30 days.",
                "consequence": "Acceleration rights over 1,700 of debt and lessor remedies over seven properties.",
                "time_horizon": "Weeks",
                "probability": "High",
                "impact": "High",
                "confidence": "High",
                "cite": m_dist,
            },
            {
                "path_id": "P2",
                "driver": "Gulf Coast revenue keeps falling",
                "first_break": "Liquidity below the 50 covenant floor",
                "transmission": "Each 5% of Gulf Coast revenue removes about 15 of liquidity.",
                "consequence": "Second maintenance covenant breached; no room to negotiate.",
                "time_horizon": "1-2 quarters",
                "probability": "High",
                "impact": "Medium",
                "confidence": "Medium",
                "cite": f"{m_seg}{m_si}",
            },
            {
                "path_id": "P3",
                "driver": "Landlord reserves rights under the master lease",
                "first_break": "Reservation-of-rights notice",
                "transmission": "A funded-debt default not cured in 30 days is a lease event of default.",
                "consequence": "Loss of seven leased properties or a rent concession demanded in the restructuring.",
                "time_horizon": "1-3 months",
                "probability": "Medium",
                "impact": "High",
                "confidence": "Medium",
                "cite": syn(h, "ownership_terms"),
            },
            {
                "path_id": "P4",
                "driver": "Gaming regulators condition a filing or change of control",
                "first_break": "Regulatory approval timetable in four states",
                "transmission": "Licences cannot transfer without approval, delaying a prepack.",
                "consequence": "Longer, costlier process with a value leak in administrative claims.",
                "time_horizon": "3-6 months",
                "probability": "Low",
                "impact": "High",
                "confidence": "Low",
                "cite": m_cov,
            },
            {
                "path_id": "P5",
                "driver": "2028 maturities cannot be refinanced",
                "first_break": "15 March 2028 revolver maturity",
                "transmission": "With EBITDA near 168 forward, market access is closed and a going-concern warning is outstanding.",
                "consequence": "Maturity default on 1,250 of first-lien debt.",
                "time_horizon": "12-18 months",
                "probability": "Medium",
                "impact": "High",
                "confidence": "Medium",
                "cite": m_terms,
            },
            {
                "path_id": "P6",
                "driver": "Floating-rate shock",
                "first_break": "Cash interest above 150",
                "transmission": "No hedge on 1,500 of floating debt.",
                "consequence": "A further 15 of annual cash interest per 100 bps.",
                "time_horizon": "6-12 months",
                "probability": "Low",
                "impact": "Medium",
                "confidence": "Medium",
                "cite": f"{m_terms}{m_si}",
            },
        ],
    )
    h.table(
        "cp2a.triggers",
        [
            {
                "trigger_id": "T1",
                "indicator": "Cash plus undrawn availability",
                "lead_lag": "Leading",
                "threshold": "Below 50 (covenant floor)",
                "linked_path": "P2",
                "consequence": "Second covenant breach and no room to negotiate.",
                "cite": m_cov,
            },
            {
                "trigger_id": "T2",
                "indicator": "Notes coupon paid by 15 October 2026",
                "lead_lag": "Lagging",
                "threshold": "Not paid",
                "linked_path": "P1",
                "consequence": "Event of default; cross-default clocks start.",
                "cite": m_dist,
            },
            {
                "trigger_id": "T3",
                "indicator": "Landlord notice of reservation of rights",
                "lead_lag": "Leading",
                "threshold": "Any notice",
                "linked_path": "P3",
                "consequence": "Lease becomes a negotiating lever for the landlord.",
                "cite": syn(h, "ownership_terms"),
            },
            {
                "trigger_id": "T4",
                "indicator": "Monthly Gulf Coast gaming revenue",
                "lead_lag": "Leading",
                "threshold": "More than 12% below the same month of 2025",
                "linked_path": "P2",
                "consequence": "Forward EBITDA below 168.",
                "cite": m_seg,
            },
        ],
    )
    h.analysis(
        f"The first thing to break under stress is the notes' grace period on 15 October 2026, followed within weeks by the cross-defaults that link the credit agreement and the master lease (P1, P3) {m_dist}. "
        f"Of the quantified shocks, the largest is {worst['sensitivity']} at {worst['result']} of 12-month liquidity {worst['cite'].split(' ')[0]}, followed by a 100 bps rise in Term SOFR on 1,500 of floating debt at {sofr_r}. "
        "Module view: Gulf Coast revenue and EBITDA misses matter more than rates, but time matters most. Confidence is Medium.\n\n"
        f"Six paths are listed with probability and impact. P1 (default on the notes) and P5 (the 2028 maturities) both carry High impact because they put 1,700 and 1,250 of debt in play {m_terms}. "
        f"The Gulf Coast path (P2) is the most likely to arrive first because that segment is {gc_share}% of revenue and falling {m_seg}.\n\n"
        f"The only sizeable mitigant is capex: cutting 25% of maintenance capex adds {capex_r} of liquidity {m_fwd}. It cannot offset an EBITDA miss and risks revenue. Triggers T1 to T4 give the early warnings."
    )
    h.gaps(
        "- Hedging: the pack states no rate hedge, so the rate sensitivity assumes none. Lifted by: the debt note's derivative disclosure.\n"
        "- Revenue flow-through: a 45% flow-through is an analyst assumption, not a disclosed figure. Lifted by: segment cost data."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
