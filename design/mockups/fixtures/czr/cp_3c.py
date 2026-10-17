"""CZR CP-3C: refinancing and LME risk.

Real: the 10-Q maturity schedule and liquidity table, the covenant extraction (incremental tests, Non-Covenant Term B-1,
cure right) and the real CAOS CP-3C finding (ordinary refinancing is the most credible path; LME vulnerability Low, not
zero). Calculated: cumulative maturities against accessible liquidity (the funding gap), the pari capacity and the
creditor exposure by case. Synthetic and marked: the restricted-payment and investment baskets
(`czr.rp_investment_baskets`) and, in Primary runs, the three merger tranches (`czr.merger_tranches`).
"""

from __future__ import annotations

from decimal import Decimal

from core import Ctx, D, Handoff, compute, plain
from czr.cp_3 import (
    AS_OF,
    FACTS,
    FOLDER,
    cite_fact,
    is_primary,
    mk_fig,
    num,
    tranche_rows,
)
from helpers import caos_text, join_marks

YEARS = [
    ("2026 (rest)", "debt_maturity_remaining_2026"),
    ("2027", "debt_maturity_2027"),
    ("2028", "debt_maturity_2028"),
    ("2029", "debt_maturity_2029"),
    ("2030", "debt_maturity_2030"),
    ("Thereafter", "debt_maturity_thereafter"),
]
PRESSURE = {
    "2026 (rest)": "Low",
    "2027": "Low",
    "2028": "High",
    "2029": "High",
    "2030": "High",
    "Thereafter": "Medium",
}


def maturity_pressure(
    ctx: Ctx, h: Handoff, tranches: list[dict]
) -> tuple[list[dict], dict[str, str]]:
    """Cumulative scheduled maturities against accessible liquidity; the CEI revolver's net capacity drops out from 2028
    (it matures 31 January 2028). gap = max(maturing - sources, 0) on each row."""
    liq, rcf = ctx.val("liq_total"), ctx.val("liq_cei_rcf_net")
    liq_c, rcf_c = h.cite_fig("liq_total"), h.cite_fig("liq_cei_rcf_net")
    after, after_s = compute(
        "accessible liquidity once the CEI revolver matures", "liq - rcf", 0, liq=liq, rcf=rcf
    )
    rows: list[dict] = []
    gap_calcs: dict[str, str] = {}
    cum = Decimal(0)
    for label, key in YEARS:
        amount = ctx.val(key)
        m_c = h.cite_fig(key)
        cum, cum_s = compute(
            f"cumulative scheduled maturities to {label}", "prev + m", 0, prev=cum, m=amount
        )
        cites = [m_c]
        if label == "Thereafter" and tranches:
            new = sum((D(t["size"]) for t in tranches), Decimal(0))
            cum, cum_s = compute(
                "cumulative scheduled maturities including the merger tranches due 2033 and 2034",
                "prev + new",
                0,
                prev=cum,
                new=new,
            )
            cites.append(cite_fact(h, "merger_tranches"))
        src = liq if label in ("2026 (rest)", "2027") else after
        src_c = (
            liq_c if label in ("2026 (rest)", "2027") else join_marks(liq_c, rcf_c) + " " + after_s
        )
        gap_raw = cum - src
        gap = gap_raw if gap_raw > 0 else Decimal(0)
        gap_s = (
            compute("funding gap", "maturing - sources", 0, maturing=cum, sources=src)[1]
            if gap_raw > 0
            else f"calc: funding gap = max({plain(cum)} - {plain(src)}, 0) = 0, sources cover the cumulative maturities"
        )
        gap_calcs[label] = gap_s
        rows.append(
            {
                "fiscal_year": label,
                "maturing_amount": plain(cum),
                "sources_available": plain(src),
                "funding_gap": plain(gap),
                "currency": "USD",
                "unit": "MILLIONS",
                "pressure": PRESSURE[label],
                "cite": join_marks(*cites, src_c) + " " + cum_s + " " + gap_s,
            }
        )
    return rows, gap_calcs


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-3C",
        "CZR",
        run_id,
        AS_OF,
        ["CP-0", "CP-1", "CP-4", "MODEL"],
        fixture_file="czr/cp_3c.py",
    )
    h.qa("Restricted")
    primary = is_primary(ctx, run_id)
    tranches = tranche_rows(ctx, run_id) if primary else []
    cc = lambda s: caos_text(h, FOLDER, "CP-3C", s)  # noqa: E731
    bk = FACTS["rp_investment_baskets"]

    # ------------------------------------------------------------------ maturity pressure
    mp, gap_calcs = maturity_pressure(ctx, h, tranches)
    h.table("cp3c.maturity_pressure", mp)
    by = {r["fiscal_year"]: r for r in mp}

    # ------------------------------------------------------------------ capacity and exposure inputs
    sec = ctx.val("senior_secured_debt_2026_06_30")
    uns = ctx.val("unsecured_debt_2026_06_30")
    pari = ctx.val("cap_pari_secured")
    pari_c, jr_c = h.cite_fig("cap_pari_secured"), h.cite_fig("cap_junior_secured")
    jr = ctx.val("cap_junior_secured")
    ratio_c = h.cite_fig("cov_incr_pari_sslr")
    pari_m, jr_m = join_marks(pari_c), join_marks(jr_c)
    b1_c = join_marks(h.cite_fig("cov_tlb1_non_covenant"))
    cure_c = join_marks(h.cite_fig("cov_equity_cure"))
    rp_c = cite_fact(h, "rp_investment_baskets")
    sec_rows = [
        t
        for t in tranches
        if "unsecured" not in t["debt_type"].lower() and t["debt_type"] != "SU Notes"
    ]
    new_sec = sum((D(t["size"]) for t in sec_rows), Decimal(0))
    new_all = sum((D(t["size"]) for t in tranches), Decimal(0))
    lme_sec, lme_sec_s = compute(
        "senior secured claims after drawing the pari capacity", "sec + pari", 0, sec=sec, pari=pari
    )
    lme_uns, lme_uns_s = compute(
        "claims at or ahead of the unsecured notes after drawing the pari capacity",
        "sec + uns + pari",
        0,
        sec=sec,
        uns=uns,
        pari=pari,
    )
    base_uns, base_uns_s = compute(
        "claims at or ahead of the unsecured notes, base", "sec + uns", 0, sec=sec, uns=uns
    )
    if primary:
        st_sec, st_sec_s = compute(
            "senior secured claims with the merger tranches layered on",
            "sec + new",
            0,
            sec=sec,
            new=new_sec,
        )
        st_uns, st_uns_s = compute(
            "claims at or ahead of the unsecured notes with the merger tranches",
            "sec + uns + new",
            0,
            sec=sec,
            uns=uns,
            new=new_all,
        )
        st_c = cite_fact(h, "merger_tranches")
    else:
        rcf = ctx.val("liq_cei_rcf_net")
        st_sec, st_sec_s = compute(
            "senior secured claims with the CEI revolver fully drawn",
            "sec + rcf",
            0,
            sec=sec,
            rcf=rcf,
        )
        st_uns, st_uns_s = compute(
            "claims at or ahead of the unsecured notes with the revolver drawn",
            "sec + uns + rcf",
            0,
            sec=sec,
            uns=uns,
            rcf=rcf,
        )
        st_c = mk_fig(h, "liq_cei_rcf_net")

    # ------------------------------------------------------------------ cp3c.lme_capacity
    uns_sub = D(bk["unrestricted_sub_capacity"])
    inv_rem, inv_s = compute(
        "general investment basket remaining",
        "size - used",
        0,
        size=D(bk["general_investment_basket"]),
        used=D(bk["investment_used"]),
    )
    lme = [
        {
            "indicator": "Pari secured incremental to 4.50x",
            "available": "Available",
            "evidence": f"US${num(pari)}m indicative under the {num(ctx.val('cov_incr_pari_sslr'), 2)}x test on RBOT's basis {pari_m}",
            "paths_enabled": "Priming by dilution",
            "cite": join_marks(pari_c, ratio_c),
        },
        {
            "indicator": "Junior secured incremental to 4.75x",
            "available": "Available",
            "evidence": f"US${num(jr)}m indicative under the {num(ctx.val('cov_incr_junior_tslr'), 2)}x test, an alternative to the pari amount {jr_m}",
            "paths_enabled": "Secured debt behind the first lien",
            "cite": join_marks(jr_c, h.cite_fig("cov_incr_junior_tslr")),
        },
        {
            "indicator": "Non-covenant Term Loan B-1",
            "available": "Available",
            "evidence": f"Term Loan B-1 is a Non-Covenant Facility, so its holders can amend and extend without a maintenance test {b1_c}",
            "paths_enabled": "Amend-and-extend without a maintenance test",
            "cite": b1_c,
        },
        {
            "indicator": "Unrestricted subsidiary and drop-down capacity",
            "available": "Available",
            "evidence": f"Synthetic baskets: US${num(uns_sub)}m of unrestricted-subsidiary capacity and a US${num(D(bk['general_investment_basket']))}m general investment basket with US${num(D(bk['investment_used']))}m used ({num(inv_rem)} left) {rp_c}; the real extraction did not find the baskets (G32)",
            "paths_enabled": "Asset transfers outside the credit group",
            "cite": join_marks(rp_c) + " " + inv_s,
        },
        {
            "indicator": "Restricted payments and builder basket",
            "available": "Available",
            "evidence": f"Synthetic: general basket US${num(D(bk['general_rp_basket']))}m unused and a builder basket of US${num(D(bk['builder_basket']))}m with US${num(D(bk['builder_used']))}m used {rp_c}",
            "paths_enabled": "Value leakage to the sponsor ahead of creditors",
            "cite": rp_c,
        },
        {
            "indicator": "Non-pro-rata uptier",
            "available": "Unclear",
            "evidence": cc(
                "Current credit agreement, security package and intercreditor agreement are not in the pack, so no uptier route or open-market purchase language can be confirmed {28,35}"
            ),
            "paths_enabled": "Priming by non-pro-rata exchange",
            "cite": join_marks(h.cite_caos(FOLDER, "CP-3C", 28), h.cite_caos(FOLDER, "CP-3C", 35)),
        },
        {
            "indicator": "Equity cure for the maintenance tests",
            "available": "Available",
            "evidence": f"A Cure Right exists for the revolver and Term Loan A tests {cure_c}",
            "paths_enabled": "Cures a maintenance breach with cash",
            "cite": cure_c,
        },
    ]
    h.table("cp3c.lme_capacity", lme)

    # ------------------------------------------------------------------ cp3c.refinancing_paths
    liq_c = join_marks(h.cite_fig("liq_total"))
    rcf_date = join_marks(h.cite_fig("cei_rcf_maturity"))
    util_c = mk_fig(h, "cr_rcf_util_pct")
    sl_c = mk_fig(h, "senior_leverage_ltm")
    m2030 = join_marks(h.cite_fig("debt_maturity_2030"))
    paths = [
        {
            "path": "Merger closes with committed financing",
            "feasibility": "High",
            "likelihood_direction": "Negative",
            "evidence_for": f"Committed financing from ten banks {join_marks(h.cite_fig('issuer.merger.financing'))}, not subject to a financing condition {join_marks(h.cite_fig('issuer.merger.financing_condition'))}",
            "evidence_against": (
                f"The new debt adds {num(new_all)} to a funding gap that already opens in 2028 {st_c}"
                if primary
                else "The size of the new debt is unstated (G8)"
            ),
            "creditor_impact": "Existing secured and unsecured creditors may rank behind new debt or be diluted",
            "cite": join_marks(
                h.cite_fig("issuer.merger.financing"),
                h.cite_fig("issuer.merger.financing_condition"),
            )
            + (" " + st_c if primary else ""),
        },
        {
            "path": "Revolver and Term Loan A extended before 2028",
            "feasibility": "Medium",
            "likelihood_direction": "Neutral",
            "evidence_for": f"The revolver is {num(ctx.val('cr_rcf_util_pct'), 1)}% drawn and total liquidity is {num(ctx.val('liq_total'))} {util_c}{liq_c}",
            "evidence_against": f"Maturity on 31 January 2028 falls while the merger financing is unsettled {rcf_date}",
            "creditor_impact": "Neutral to secured lenders if terms are unchanged",
            "cite": join_marks(util_c, liq_c, rcf_date),
        },
        {
            "path": "Amend-and-extend of Term Loan B 2030",
            "feasibility": "Medium",
            "likelihood_direction": "Neutral",
            "evidence_for": f"Senior secured leverage of {num(ctx.val('senior_leverage_ltm'), 2)}x is inside the {num(ctx.val('cov_incr_pari_sslr'), 2)}x test {sl_c}{join_marks(ratio_c)}",
            "evidence_against": f"2030 is the heaviest scheduled maturity year at {num(ctx.val('debt_maturity_2030'))} {m2030}",
            "creditor_impact": "Longer tenor for lenders, usually at a higher margin",
            "cite": join_marks(sl_c, ratio_c, m2030),
        },
        {
            "path": "Exchange of the unsecured notes into secured debt",
            "feasibility": "Low",
            "likelihood_direction": "Negative",
            "evidence_for": f"Pari capacity of {num(pari)} could take part of the exchange {pari_m}",
            "evidence_against": f"Unsecured 2032s at {num(ctx.val('trace_czr_12769gad2_last_price'))} give holders little reason to exchange down in claim {mk_fig(h, 'trace_czr_12769gad2_last_price')}",
            "creditor_impact": "Unsecured holders move up in rank; existing secured creditors are diluted",
            "cite": join_marks(pari_c, h.cite_fig("trace_czr_12769gad2_last_price")),
        },
    ]
    h.table("cp3c.refinancing_paths", paths)

    # ------------------------------------------------------------------ cp3c.creditor_exposure
    sec_c = h.cite_fig("senior_secured_debt_2026_06_30")
    uns_c = h.cite_fig("unsecured_debt_2026_06_30")
    exp_rows = [
        ("Senior secured", "Base", sec, "Low", join_marks(sec_c)),
        ("Senior secured", "Stress", st_sec, "Medium", join_marks(sec_c, st_c) + " " + st_sec_s),
        ("Senior secured", "LME", lme_sec, "Medium", join_marks(sec_c, pari_c) + " " + lme_sec_s),
        (
            "Senior unsecured",
            "Base",
            base_uns,
            "Medium",
            join_marks(sec_c, uns_c) + " " + base_uns_s,
        ),
        (
            "Senior unsecured",
            "Stress",
            st_uns,
            "High",
            join_marks(sec_c, uns_c, st_c) + " " + st_uns_s,
        ),
        (
            "Senior unsecured",
            "LME",
            lme_uns,
            "High",
            join_marks(sec_c, uns_c, pari_c) + " " + lme_uns_s,
        ),
    ]
    h.table(
        "cp3c.creditor_exposure",
        [
            {
                "creditor_class": cls,
                "case_name": case,
                "exposure": plain(val),
                "currency": "USD",
                "unit": "MILLIONS",
                "priming_risk": risk,
                "cite": cite,
            }
            for cls, case, val, risk, cite in exp_rows
        ],
    )

    # ------------------------------------------------------------------ analysis
    first_gap = by["2028"]
    paras = [
        f"Refinancing pressure is concentrated in 2028 to 2030, and the most credible path is ordinary consensual refinancing of the CEI revolver and Term Loan A before 31 January 2028; coercive LME vulnerability is Low, not zero. That is the real CAOS finding, reached at confidence 55 of 100 with QA Restricted {cc('{22,23,28,35}')}. "
        f"Cash and revolver capacity were {num(ctx.val('liq_total'))} at 30 June 2026 {mk_fig(h, 'liq_total')} and no final maturity falls inside twelve months, so the buffer is real but dated.",
        f"On the 10-Q schedule the pressure shows from 2028. Cumulative scheduled maturities reach {num(D(by['2028']['maturing_amount']))} by the end of 2028 against {num(D(by['2028']['sources_available']))} of liquidity once the revolver's {num(ctx.val('liq_cei_rcf_net'))} of net capacity matures, a funding gap of {first_gap['funding_gap']} ({gap_calcs['2028']}). "
        f"The gap then reaches {num(D(by['2029']['funding_gap']))} in 2029 and {num(D(by['2030']['funding_gap']))} in 2030, before any operating cash flow or refinancing. The schedule includes amortisation, so it differs from the final-maturity wall in the Model; 2030 carries the heaviest year at {num(ctx.val('debt_maturity_2030'))} {mk_fig(h, 'debt_maturity_2030')}.",
        f"Legal flexibility is wide on paper and unconfirmed in practice. The pari secured test allows about {num(pari)} of further first-lien debt and the junior test about {num(jr)} {pari_m}{jr_m}; Term Loan B-1 is a Non-Covenant Facility {b1_c}. "
        f"The restricted-payment and investment baskets were not extracted (G32), so the fixture fills them with synthetic values: {num(uns_sub)} of unrestricted-subsidiary capacity and a general investment basket of {num(D(bk['general_investment_basket']))} with {num(D(bk['investment_used']))} used {rp_c}. The real credit agreement, security package and intercreditor agreement are incomplete, so no uptier route is inferred {cc('{28}')}.",
        (
            f"By creditor class the secured claims rise from {num(sec)} in the Base case to {num(st_sec)} when the three synthetic merger tranches are layered on and {num(lme_sec)} when the pari capacity is drawn; claims at or ahead of the unsecured notes rise from {num(base_uns)} to {num(st_uns)} and {num(lme_uns)} {st_c}. "
            f"The unsecured holders carry the higher priming risk in every case."
        )
        if primary
        else f"By creditor class the secured claims rise from {num(sec)} in the Base case to {num(st_sec)} with the revolver fully drawn and {num(lme_sec)} when the pari capacity is drawn; the unsecured notes carry the higher priming risk in every case.",
        f"What would change this view: an extension of the revolver and Term Loan A, the disclosed merger debt and ranking, and the current credit agreement with basket usage. The 2024 Term Loan B repricing shows ordinary amendment execution, not distressed intent {cc('{29,30}')}. Confidence in this module: Low.",
    ]
    h.analysis("\n\n".join(paras))
    gaps = [
        "- Current covenant headroom and basket usage: not disclosed (G32, G33, G34); the restricted-payment and investment baskets in the LME table are synthetic. Effect: LME capacity is indicative. Lifted by: the compliance certificate and a basket tracker.",
        "- Market access: no current quote, spread or primary refinancing terms in the pack (G18, G19). Lifted by: dealer indications and a benchmark curve.",
        "- Sponsor willingness: the filings do not show Fertitta's intent toward the existing debt. Lifted by: a lender presentation.",
        "- Funding gap is cumulative scheduled maturities against accessible liquidity with no operating cash flow and no refinancing; it is not a 12-month cash bridge (see CP-2D).",
    ]
    if primary:
        gaps.append(
            "- Merger tranches: the new debt in the Stress case and the 'Thereafter' maturities is synthetic (G8). Lifted by: the commitment papers."
        )
    h.gaps("\n".join(gaps))
    return h
