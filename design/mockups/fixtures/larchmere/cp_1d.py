"""Larchmere CP-1D: earnings quality (synthetic): add-back verdicts, cash conversion, debt-like items."""

from __future__ import annotations

from decimal import Decimal

from core import Ctx, D, Handoff, compute, fpct, fx, plain

from . import derived as X
from . import facts as F
from .facts import syn

VERDICTS = {
    "restructuring_costs": (
        "REALIZED",
        "Challenged",
        "Advisory and restructuring costs were paid in cash and have recurred in each of the last three years, so they are a cost of running a levered business rather than a one-off.",
        "Third consecutive year; 22 LTM against 6 in FY2023",
    ),
    "sponsor_fee": (
        "REALIZED",
        "Supported",
        "The fee is a contractual cash payment to the sponsor and is excluded from operating cost in both the company's and the lenders' definition; it is realized but should be subordinated in distress.",
        "Annual and contractual at 5",
    ),
    "run_rate_savings": (
        "UNREALIZED",
        "Rejected",
        "Announced savings have not been delivered in any period reported and rely on closing capacity the company has not committed to close.",
        "Grows each period (8, 12, 16 LTM) without appearing in actual costs",
    ),
}


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-1D",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1"],
        fixture_file="larchmere/cp_1d.py",
    )
    h.qa("Restricted")
    rows = []
    for aid, _label, cls, key, _status in X.ADDBACKS:
        v, s = X.ltm(key, label=f"LTM {aid}")
        stat, verdict, why, rec = VERDICTS[aid]
        rows.append(
            {
                "addback_id": aid,
                "period_id": "LTM_Q2_2026",
                "amount": plain(v),
                "currency": "USD",
                "unit": "MILLIONS",
                "category": cls,
                "house_realization_status": stat,
                "verdict": verdict,
                "rationale": why,
                "recurrence": rec,
                "cite": f"{syn(h, key)} {s}",
            }
        )
    h.table("cp1d.addback_assessment", rows)
    conv = []
    m_cfo, m_adj = syn(h, "cfo"), syn(h, "adjusted_ebitda")
    for p in ("FY2023", "FY2024", "FY2025", "LTM_Q2_2026"):
        adj, cfo = X.flow("adjusted_ebitda", p), X.flow("cfo", p)
        c, cs = compute(
            f"{p} cash conversion", "cfo / adjusted * 100", 1, "%", cfo=cfo, adjusted=adj
        )
        conv.append(
            {
                "period_id": p,
                "adjusted_ebitda": plain(adj),
                "cfo": plain(cfo),
                "conversion_pct": fpct(c),
                "currency": "USD",
                "unit": "MILLIONS",
                "explanation": "Operating cash flow after cash interest, rent and taxes as a share of company-defined Adjusted EBITDA.",
                "credit_implication": "Conversion has fallen from a third of EBITDA to a negative figure, so earnings no longer fund the debt service."
                if p != "FY2023"
                else "Conversion was still positive and a third of EBITDA before interest costs rose.",
                "cite": f"{m_cfo}{m_adj} {cs}",
            }
        )
    h.table("cp1d.cash_conversion", conv)
    di = F.val("debt_like_inputs")
    coupon, coupon_s = compute(
        "accrued unpaid coupon",
        "notes * rate / 100 / 2",
        2,
        "",
        notes=X.facility_balance("llg_notes", "JUN30_2026"),
        rate=di["coupon_pct"],
    )
    m_di, m_notes, m_ev = (
        syn(h, "debt_like_inputs"),
        syn(h, "term_debt_face"),
        syn(h, "distress_events"),
    )
    items = [
        (
            "Accrued unpaid coupon on the 8.25% notes (grace period running)",
            coupon,
            "Debt-like",
            "Interest due 15 September 2026 and unpaid; a claim on the issuer ranking with the notes.",
            f"{m_notes}{m_ev} {coupon_s}",
        ),
        (
            "Deferred earn-out to the former owner of the online business",
            D(di["earn_out"]),
            "Debt-like",
            "A fixed purchase-price obligation payable in cash by 2027.",
            m_di,
        ),
        (
            "Multi-employer pension withdrawal liability",
            D(di["pension_withdrawal"]),
            "Debt-like",
            "A contingent but determinable claim on withdrawal from a union plan in a restructuring.",
            m_di,
        ),
        (
            "Customer deposits and unredeemed rewards",
            D(di["customer_deposits"]),
            "Not debt-like",
            "Operating float that funds itself and is settled in the ordinary course.",
            m_di,
        ),
    ]
    h.table(
        "cp1d.debt_like_items",
        [
            {
                "item": i,
                "amount": plain(a),
                "currency": "USD",
                "unit": "MILLIONS",
                "period_id": "JUN30_2026",
                "treatment": t,
                "basis": b,
                "cite": c,
            }
            for i, a, t, b, c in items
        ],
    )
    stated = X.ltm("adjusted_ebitda")[0]
    ssim = X.ssim_ltm()
    share, share_s = compute(
        "share of stated EBITDA supported", "ssim / stated * 100", 1, "%", ssim=ssim, stated=stated
    )
    challenged, ch_s = compute(
        "EBITDA if restructuring costs are recurring",
        "ssim - restructuring",
        0,
        "",
        ssim=ssim,
        restructuring=X.ltm("addback_restructuring")[0],
    )
    like = sum((a for _, a, t, _, _ in items if t == "Debt-like"), Decimal(0))
    adj_debt, ad_s = compute(
        "adjusted debt", "debt + debt_like", 2, "", debt=X.total_debt("JUN30_2026"), debt_like=like
    )
    lev, lev_s = compute(
        "adjusted leverage", "adjusted_debt / ssim", 2, "x", adjusted_debt=adj_debt, ssim=ssim
    )
    m_sav = syn(h, "addback_run_rate_savings")
    h.analysis(
        f"{share}% of the company's {plain(stated)} Adjusted EBITDA is supported by the evidence: SSIM EBITDA is {plain(ssim)} after rejecting the 16 of run-rate savings {m_sav} ({share_s}). "
        f"If the restructuring costs are treated as recurring, as the three-year pattern suggests, the supported figure falls to {plain(challenged)} ({ch_s}). "
        "The sponsor fee is realized and contractual. Confidence is Medium.\n\n"
        f"Cash conversion is the weakest part of earnings quality: operating cash flow was a fifth of Adjusted EBITDA in FY2024 and is negative LTM {m_cfo}{m_adj}. "
        "The company's EBITDA no longer funds its interest and rent.\n\n"
        f"Beyond face debt, the debt-like items are {plain(like)} (an accrued unpaid coupon, an earn-out and a pension withdrawal liability) {m_di}. "
        f"Adjusted debt is {plain(adj_debt)} ({ad_s}) and adjusted leverage {fx(lev)} ({lev_s}). The master-lease financing obligation of 1,149 is deliberately outside these figures and sits in the Model's lease-adjusted lines."
    )
    h.gaps(
        "- Savings programme detail: the company gave no plan, headcount or closure schedule behind the 16 of run-rate savings. Effect: the savings cannot be tested, so they are rejected. Lifted by: the management plan.\n"
        "- Quarterly cash conversion: only half-year cash flows are reported. Lifted by: quarterly cash-flow statements."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
