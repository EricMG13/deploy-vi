"""Larchmere CP-2D: 12-month liquidity bridge (synthetic forward inputs, computed bridge and runway)."""

from __future__ import annotations

from core import Ctx, D, Handoff, compute, plain

from . import derived as X
from . import facts as F
from .facts import syn


def figures() -> dict:
    """The 12-month sources, uses and bridge as Decimals with their calc strings (shared with the tests)."""
    fwd = F.val("forward_12m")
    opening, op_s = compute(
        "opening accessible liquidity",
        "cash + undrawn",
        0,
        "",
        cash=X.cash("JUN30_2026"),
        undrawn=F.val("undrawn_rcf")["JUN30_2026"],
    )
    interest, int_s = X.forward_interest("BASE")
    rent_ltm = X.ltm("lease_cash")[0]
    rent, rent_s = compute(
        "forward cash rent",
        "rent * (100 + esc) / 100",
        1,
        "",
        rent=rent_ltm,
        esc=fwd["rent_escalator_pct"],
    )
    amort, am_s = compute(
        "term loan B amortisation",
        "pct / 100 * original",
        1,
        "",
        pct=F.val("facility_terms")["llg_tlb"]["amort_pct"],
        original=F.val("facility_terms")["llg_tlb"]["original"],
    )
    op_inflow, oi_s = compute(
        "operating cash inflow",
        "ebitda + wc",
        0,
        "",
        ebitda=fwd["adjusted_ebitda"],
        wc=fwd["wc_change"],
    )
    accessible, acc_s = compute(
        "accessible liquidity",
        "cash + undrawn + inflow",
        1,
        "",
        cash=X.cash("JUN30_2026"),
        undrawn=F.val("undrawn_rcf")["JUN30_2026"],
        inflow=op_inflow,
    )
    uses = {
        "interest": interest,
        "rent": rent,
        "taxes": D(fwd["cash_taxes"]),
        "capex": D(fwd["maintenance_capex"]),
        "amort": amort,
        "advisers": D(fwd["advisers"]),
    }
    mand, mand_s = compute(
        "mandatory uses",
        "i + r + t + c + a + f",
        1,
        "",
        i=uses["interest"],
        r=uses["rent"],
        t=uses["taxes"],
        c=uses["capex"],
        a=uses["amort"],
        f=uses["advisers"],
    )
    head, head_s = compute(
        "headroom", "accessible - mandatory", 1, "", accessible=accessible, mandatory=mand
    )
    closing, cl_s = compute(
        "closing accessible liquidity",
        "open + ebitda + wc - i - r - t - c - a - f",
        1,
        "",
        open=opening,
        ebitda=fwd["adjusted_ebitda"],
        wc=-D(fwd["wc_change"]).copy_abs(),
        i=uses["interest"],
        r=uses["rent"],
        t=uses["taxes"],
        c=uses["capex"],
        a=uses["amort"],
        f=uses["advisers"],
    )
    burn, burn_s = compute(
        "monthly net burn", "(mandatory - inflow) / 12", 2, "", mandatory=mand, inflow=op_inflow
    )
    months, mo_s = compute(
        "months of runway", "cash / burn", 1, "", cash=X.cash("JUN30_2026"), burn=burn
    )
    floor_months, fm_s = compute(
        "months to the liquidity floor",
        "(cash - floor) / burn",
        1,
        "",
        cash=X.cash("JUN30_2026"),
        floor=F.val("covenants")["min_liquidity"],
        burn=burn,
    )
    return dict(
        opening=opening,
        op_s=op_s,
        interest=interest,
        int_s=int_s,
        rent=rent,
        rent_s=rent_s,
        amort=amort,
        am_s=am_s,
        op_inflow=op_inflow,
        oi_s=oi_s,
        accessible=accessible,
        acc_s=acc_s,
        uses=uses,
        mand=mand,
        mand_s=mand_s,
        head=head,
        head_s=head_s,
        closing=closing,
        cl_s=cl_s,
        burn=burn,
        burn_s=burn_s,
        months=months,
        mo_s=mo_s,
        floor_months=floor_months,
        fm_s=fm_s,
    )


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2D",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "CP-4", "MODEL"],
        fixture_file="larchmere/cp_2d.py",
    )
    h.qa("Restricted")
    f = figures()
    fwd = F.val("forward_12m")
    m_fwd, m_cash, m_rcf, m_und, m_deck, m_terms, m_lease, m_cov = (
        syn(h, k)
        for k in (
            "forward_12m",
            "cash_balance",
            "rcf_drawn",
            "undrawn_rcf",
            "rate_deck",
            "facility_terms",
            "lease_cash",
            "covenants",
        )
    )
    u = f["uses"]
    h.table(
        "cp2d.liquidity_sources",
        [
            {
                "component": "Unrestricted cash",
                "amount": plain(X.cash("JUN30_2026")),
                "currency": "USD",
                "unit": "MILLIONS",
                "accessible": "Yes",
                "restriction": "Subject to the 50 minimum liquidity covenant",
                "cite": f"{m_cash}{m_cov}",
            },
            {
                "component": "Undrawn revolver availability",
                "amount": plain(D(F.val("undrawn_rcf")["JUN30_2026"])),
                "currency": "USD",
                "unit": "MILLIONS",
                "accessible": "Yes",
                "restriction": "Revolver fully drawn at 200; no availability",
                "cite": f"{m_rcf}{m_und}",
            },
            {
                "component": "Forecast operating cash flow before interest, rent and capex, next 12 months",
                "amount": plain(f["op_inflow"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "accessible": "Yes",
                "restriction": "Earned over the year, not cash in hand; falls with EBITDA",
                "cite": f"{m_fwd} {f['oi_s']}",
            },
            {
                "component": "Cage cash held as player bankroll",
                "amount": plain(D(fwd["cage_cash"])),
                "currency": "USD",
                "unit": "MILLIONS",
                "accessible": "No",
                "restriction": "Regulatory minimum bankroll across four states",
                "cite": m_fwd,
            },
        ],
    )
    h.table(
        "cp2d.cash_uses_12m",
        [
            {
                "use": "Cash interest on debt",
                "amount": plain(u["interest"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Quarterly; notes semi-annual (15 March and 15 September)",
                "mandatory": "Yes",
                "cite": f"{m_terms}{m_deck} {f['int_s']}",
            },
            {
                "use": "Master-lease cash rent",
                "amount": plain(u["rent"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Monthly",
                "mandatory": "Yes",
                "cite": f"{m_lease}{m_fwd} {f['rent_s']}",
            },
            {
                "use": "Cash taxes",
                "amount": plain(u["taxes"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Quarterly",
                "mandatory": "Yes",
                "cite": m_fwd,
            },
            {
                "use": "Maintenance capital expenditure",
                "amount": plain(u["capex"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Spread evenly",
                "mandatory": "Yes",
                "cite": m_fwd,
            },
            {
                "use": "Term loan B scheduled amortisation",
                "amount": plain(u["amort"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Quarterly from 30 September 2026",
                "mandatory": "Yes",
                "cite": f"{m_terms} {f['am_s']}",
            },
            {
                "use": "Restructuring advisers and fees",
                "amount": plain(u["advisers"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Monthly retainers and success fees",
                "mandatory": "Yes",
                "cite": m_fwd,
            },
            {
                "use": "Growth capital expenditure (deferrable)",
                "amount": plain(D(fwd["growth_capex"])),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": "Discretionary",
                "mandatory": "No",
                "cite": m_fwd,
            },
        ],
    )
    bridge = [
        (
            "Beginning accessible liquidity (cash and undrawn revolver)",
            "Opening total",
            f["opening"],
            f"Cash {plain(X.cash('JUN30_2026'))} plus undrawn availability",
            f"{m_cash}{m_und} {f['op_s']}",
        ),
        (
            "SSIM EBITDA, next 12 months (base)",
            "Delta",
            D(fwd["adjusted_ebitda"]),
            "Forward base-case EBITDA before interest, rent and capex",
            m_fwd,
        ),
        (
            "Working capital",
            "Delta",
            D(fwd["wc_change"]),
            "Suppliers shorten terms as the credit weakens",
            m_fwd,
        ),
        (
            "Cash interest on debt",
            "Use",
            -u["interest"],
            "Balance x rate on the first deck year",
            f"{m_terms}{m_deck} {f['int_s']}",
        ),
        (
            "Master-lease cash rent",
            "Use",
            -u["rent"],
            "LTM rent plus the 1.5% escalator",
            f"{m_lease}{m_fwd} {f['rent_s']}",
        ),
        ("Cash taxes", "Use", -u["taxes"], "State and gaming taxes", m_fwd),
        (
            "Maintenance capital expenditure",
            "Use",
            -u["capex"],
            "Deferrable growth capex excluded",
            m_fwd,
        ),
        (
            "Term loan B scheduled amortisation",
            "Use",
            -u["amort"],
            "1.00% of 1,050 a year",
            f"{m_terms} {f['am_s']}",
        ),
        (
            "Restructuring advisers and fees",
            "Use",
            -u["advisers"],
            "Retainers and expected fees",
            m_fwd,
        ),
        (
            "Closing accessible liquidity (shortfall)",
            "Closing total",
            f["closing"],
            "Opening plus deltas less uses",
            f"{m_fwd} {f['cl_s']}",
        ),
    ]
    h.table(
        "cp2d.bridge",
        [
            {
                "step": s,
                "kind": k,
                "amount": plain(a),
                "currency": "USD",
                "unit": "MILLIONS",
                "basis": b,
                "cite": c,
            }
            for s, k, a, b, c in bridge
        ],
    )
    pinch = f"Liquidity falls below the 50 covenant floor after {plain(f['floor_months'])} months (November 2026) and cash is exhausted after {plain(f['months'])} months (April 2027)"
    h.table(
        "cp2d.runway",
        [
            {
                "item": "Accessible liquidity",
                "value": plain(f["accessible"]),
                "unit_label": "USD millions",
                "basis": "Cash, undrawn revolver and 12-month operating cash inflow",
                "cite": f["acc_s"],
            },
            {
                "item": "Mandatory uses 12m",
                "value": plain(f["mand"]),
                "unit_label": "USD millions",
                "basis": "Interest, rent, taxes, maintenance capex, amortisation and adviser fees",
                "cite": f["mand_s"],
            },
            {
                "item": "Headroom",
                "value": plain(f["head"]),
                "unit_label": "USD millions",
                "basis": "Accessible liquidity less mandatory uses",
                "cite": f["head_s"],
            },
            {
                "item": "Months of runway",
                "value": plain(f["months"]),
                "unit_label": "months",
                "basis": "Opening cash divided by the monthly net burn",
                "cite": f["mo_s"],
            },
            {
                "item": "Pinch point",
                "value": pinch,
                "unit_label": "text",
                "basis": "Monthly net burn applied to opening cash",
                "cite": f"{f['fm_s']}",
            },
        ],
    )
    h.analysis(
        f"No. Accessible liquidity of {plain(f['accessible'])} does not cover the {plain(f['mand'])} of mandatory uses over the next 12 months, a shortfall of {plain(-f['head'])} ({f['head_s']}) {m_fwd}. "
        f"Opening cash of 62 lasts {plain(f['months'])} months at a net burn of {plain(f['burn'])} a month ({f['mo_s']}). The pinch point is early: the 50 minimum liquidity floor is reached after {plain(f['floor_months'])} months, in November 2026 {m_cov}. "
        "Module view: a liquidity shortfall in the first half of 2027 is the base case, not a stress case. Confidence is Medium, because the forward EBITDA is the analyst's, not management's.\n\n"
        f"The bridge starts with {plain(f['opening'])} of cash and no undrawn revolver {m_cash}{m_und}. It adds {plain(D(fwd['adjusted_ebitda']))} of SSIM EBITDA and takes away {plain(u['interest'])} of cash interest {m_terms}{m_deck}, {plain(u['rent'])} of rent {m_lease} and {plain(u['capex'])} of maintenance capex, "
        f"{plain(u['amort'])} of term loan B amortisation and {plain(u['advisers'])} of adviser fees, closing at {plain(f['closing'])} ({f['cl_s']}).\n\n"
        f"The cage cash of {fwd['cage_cash']} is held as player bankroll and is not counted. Growth capex of {fwd['growth_capex']} is deferrable and sits outside mandatory uses. "
        "The revolver is fully drawn, so there is no committed source to close the gap: it has to come from the sponsor, a new-money lender or the creditors' agreement to defer interest."
    )
    h.gaps(
        "- Management's monthly cash forecast: not in the pack; the bridge uses the analyst's base case. Effect: the pinch month is an estimate. Lifted by: the 13-week cash flow.\n"
        "- Cage cash minimums by state: not in the pack; 41 is the analyst's estimate of regulatory minimums. Lifted by: gaming-board filings."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
