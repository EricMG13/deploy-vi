"""Larchmere CP-4: legal and covenant interpreter (synthetic documents, computed headroom and capacity)."""

from __future__ import annotations

from decimal import Decimal

from core import GAP, Ctx, D, Handoff, compute, plain
from helpers import join_marks as join

from . import derived as X
from . import facts as F
from .facts import syn


def _basket(
    floor: int, pct: int, ebitda: Decimal, used: int, label: str
) -> tuple[Decimal, Decimal, Decimal, str]:
    """(cap, used, remaining, calc string of the remaining capacity); the cap is the greater of the floor and pct of EBITDA."""
    pct_amt, _ = compute(
        f"{label} percentage limb", "pct * ebitda / 100", 1, "", pct=pct, ebitda=ebitda
    )
    cap = max(D(floor), pct_amt)
    rem, s = compute(f"{label} remaining", "cap - used", 1, "", cap=cap, used=used)
    return cap, D(used), rem, s


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-4",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "MODEL"],
        fixture_file="larchmere/cp_4.py",
    )
    h.qa("Restricted")
    cov = X.covenant()
    cv = F.val("covenants")
    b = F.val("baskets")
    lp = F.val("legal_provisions")
    m_cov, m_b, m_lp, m_terms, m_rent, m_own = (
        syn(h, k)
        for k in (
            "covenants",
            "baskets",
            "legal_provisions",
            "facility_terms",
            "rent_in_covenant_ebitda",
            "ownership_terms",
        )
    )
    m_adj, m_lease, m_cash, m_rcf = (
        syn(h, k) for k in ("adjusted_ebitda", "lease_cash", "cash_balance", "rcf_drawn")
    )
    h.table(
        "cp4.document_register",
        [
            {
                "document": "First-Lien Credit Agreement (revolver and term loan B), as amended",
                "document_type": "Credit agreement",
                "document_date": "2025-06-30",
                "parties": f"{F.OPCO}; {lp['agent']} as Agent",
                "governing_law": lp["law"],
                "status": "In force; amended 2025-06-30 (amortisation holiday, covenant reset)",
                "cite": m_terms,
            },
            {
                "document": "Second-Lien Term Loan Agreement",
                "document_type": "Credit agreement",
                "document_date": "2022-09-01",
                "parties": f"{F.OPCO}; {lp['agent']} as Agent",
                "governing_law": lp["law"],
                "status": "In force",
                "cite": m_terms,
            },
            {
                "document": "Indenture for the 8.25% Senior Notes due 2029",
                "document_type": "Indenture",
                "document_date": "2022-09-15",
                "parties": f"{F.ISSUER}; trustee",
                "governing_law": lp["law"],
                "status": "In force; 15 September 2026 coupon unpaid, grace period to 15 October",
                "cite": join(m_terms, syn(h, "distress_events")),
            },
            {
                "document": "Intercreditor Agreement (first lien and second lien)",
                "document_type": "Other",
                "document_date": "2022-09-01",
                "parties": "First-lien and second-lien agents",
                "governing_law": lp["law"],
                "status": "In force; second lien subordinated in lien priority and payment on enforcement",
                "cite": m_lp,
            },
            {
                "document": "Master Lease",
                "document_type": "Other",
                "document_date": "2022-09-01",
                "parties": f"{F.LANDLORD}; tenant subsidiaries",
                "governing_law": lp["law"],
                "status": "In force; cross-default with funded debt",
                "cite": m_own,
            },
            {
                "document": "Q2 2026 compliance certificate",
                "document_type": "Other",
                "document_date": cv["cert_delivered"],
                "parties": f"{F.OPCO}; Agent",
                "governing_law": GAP,
                "status": "Delivered 30 days late; shows the springing test breached",
                "cite": m_cov,
            },
        ],
    )
    h.table(
        "cp4.covenant_tests",
        [
            {
                "test": "First-lien net leverage (springing; revolver use above 35%)",
                "test_type": "Springing",
                "direction": "Ceiling",
                "threshold": plain(cov["thr"], 2),
                "current_value": plain(cov["lev"], 2),
                "unit_label": "x",
                "basis": f"(Revolver {plain(X.facility_balance('llg_rcf', 'JUN30_2026'))} + term loan B {plain(X.facility_balance('llg_tlb', 'JUN30_2026'))} - cash {plain(X.cash('JUN30_2026'))}) / covenant EBITDA {plain(cov['cov_ebitda'])}, tested at {cv['test_date']}",
                "headroom": plain(cov["head"], 2),
                "status": "Breached",
                "cite": f"{m_cov}{m_adj}{m_lease}{m_rent} {cov['lev_s']} {cov['head_s']}",
            },
            {
                "test": "Minimum liquidity",
                "test_type": "Maintenance",
                "direction": "Floor",
                "threshold": plain(cov["floor"], 0),
                "current_value": plain(cov["liq"], 0),
                "unit_label": "USD millions",
                "basis": f"Unrestricted cash {plain(X.cash('JUN30_2026'))} + undrawn revolver availability {plain(F.val('undrawn_rcf')['JUN30_2026'])} at {cv['test_date']}",
                "headroom": plain(cov["liq_head"], 0),
                "status": "Tight",
                "cite": f"{m_cov}{m_cash}{m_rcf} {cov['liq_s']}",
            },
            {
                "test": "Minimum covenant EBITDA",
                "test_type": "Maintenance",
                "direction": "Floor",
                "threshold": plain(cov["min_e"], 0),
                "current_value": plain(cov["cov_ebitda"], 0),
                "unit_label": "USD millions",
                "basis": f"Stated Adjusted EBITDA {plain(cov['adj'])} less cash rent {plain(cov['rent'])}, LTM to {cv['test_date']}",
                "headroom": plain(cov["e_head"], 0),
                "status": "Headroom",
                "cite": f"{m_cov}{m_adj}{m_lease}{m_rent} {cov['cov_s']} {cov['e_s']}",
            },
        ],
    )
    ebitda = cov["cov_ebitda"]
    caps = []
    fc_cap, fc_used, fc_rem, fc_s = _basket(
        b["free_and_clear_floor"], b["free_and_clear_pct"], ebitda, 0, "free-and-clear incremental"
    )
    li_cap, li_used, li_rem, li_s = _basket(
        b["lien_floor"], b["lien_pct"], ebitda, b["lien_used"], "general lien basket"
    )
    in_cap, in_used, in_rem, in_s = _basket(
        b["unrestricted_investment_floor"],
        b["unrestricted_investment_pct"],
        ebitda,
        b["unrestricted_investment_used"],
        "unrestricted-subsidiary investment",
    )
    rp_cap, rp_used, rp_rem, rp_s = _basket(
        b["rp_floor"], b["rp_pct"], ebitda, b["rp_used"], "restricted-payments"
    )
    nm = D(F.val("new_money")["size"])
    short, short_s = compute(
        "sponsor proposal beyond the free-and-clear basket",
        "new_money - basket",
        1,
        "",
        new_money=nm,
        basket=fc_rem,
    )
    caps = [
        (
            "Debt",
            "Free-and-clear incremental first lien",
            f"greater of {b['free_and_clear_floor']} and {b['free_and_clear_pct']}% x covenant EBITDA {plain(ebitda)}",
            fc_used,
            fc_rem,
            "Calculated",
            "High",
            "Capacity is available outside the ratio test, so new first-lien money can prime the existing lenders.",
            f"The 150 sponsor proposal exceeds the basket by {plain(short)}, so it needs a Required Lender amendment as well.",
            f"{m_b} {short_s}",
        ),
        (
            "Debt",
            "Ratio debt (first-lien net leverage at or below 6.50x)",
            "pro forma first-lien net leverage <= 6.50x",
            D(0),
            D(0),
            "Calculated",
            "Low",
            "The ratio test is failed at 8.03x, so ratio debt is unavailable.",
            "Debt capacity comes only from the fixed baskets and amendments.",
            f"{m_cov} {cov['lev_s']}",
        ),
        (
            "Liens",
            "General lien basket",
            f"greater of {b['lien_floor']} and {b['lien_pct']}% x covenant EBITDA {plain(ebitda)}",
            li_used,
            li_rem,
            "Calculated",
            "Medium",
            "Liens can be granted over unencumbered assets without lender consent.",
            "Owned property not yet in the collateral pool is the target.",
            f"{m_b} {li_s}",
        ),
        (
            "Investments",
            "Unrestricted-subsidiary investment (drop-down)",
            f"greater of {b['unrestricted_investment_floor']} and {b['unrestricted_investment_pct']}% x covenant EBITDA {plain(ebitda)}",
            in_used,
            in_rem,
            "Calculated",
            "High",
            f"Assets can be moved to an unrestricted subsidiary without a leverage test: {lp['designation']}.",
            "The online business is the likely target; value leaves the lenders' collateral and guarantee group.",
            f"{m_b}{m_lp} {in_s}",
        ),
        (
            "Restricted payments",
            "General restricted-payments basket",
            f"greater of {b['rp_floor']} and {b['rp_pct']}% x covenant EBITDA {plain(ebitda)}",
            rp_used,
            rp_rem,
            "Calculated",
            "Medium",
            "Distributions to the sponsor are permitted up to the remaining basket while the company is in default only if the default is cured.",
            "Remaining capacity is small relative to the claims, but sponsor fees run outside it.",
            f"{m_b} {rp_s}",
        ),
        (
            "Equity cure",
            "Equity cure of the springing test",
            "net first-lien debt / 6.50x - covenant EBITDA (deemed EBITDA)",
            D(0),
            cov["cure"],
            "Calculated",
            "Medium",
            f"The cure is available {lp['cure_frequency']}; the sponsor decides whether to fund it.",
            f"A cure of {plain(cov['cure'])} of deemed EBITDA restores the 6.50x test for one quarter only.",
            f"{m_cov} {cov['cure_s']}",
        ),
    ]
    h.table(
        "cp4.capacity_register",
        [
            {
                "capacity_type": t,
                "basket": bk,
                "formula": fm,
                "used": plain(u),
                "remaining": plain(r),
                "currency": "USD",
                "unit": "MILLIONS",
                "status": st,
                "severity": sv,
                "risk_mechanism": rm,
                "credit_implication": ci,
                "cite": c,
            }
            for t, bk, fm, u, r, st, sv, rm, ci, c in caps
        ],
    )
    h.table(
        "cp4.structure_map",
        [
            {
                "entity": F.ISSUER,
                "role": "Parent; issuer of the notes",
                "inside_credit_group": "Yes",
                "guarantees": "Guarantees the credit agreements",
                "liens": "Pledge of the operating company's equity",
                "reachable_value": "Equity in the operating company",
                "cite": m_terms,
            },
            {
                "entity": F.OPCO,
                "role": "Borrower of the revolver and both term loans",
                "inside_credit_group": "Yes",
                "guarantees": "Guaranteed by all restricted subsidiaries",
                "liens": "First lien on substantially all assets (second lien behind)",
                "reachable_value": "Four owned properties and equipment within the 1,180 appraised value",
                "cite": join(m_terms, syn(h, "liquidation")),
            },
            {
                "entity": "Larchmere Leased Properties, LLC (fictional)",
                "role": "Tenant under the master lease",
                "inside_credit_group": "Yes",
                "guarantees": "Guarantor",
                "liens": "Leasehold interests only; the landlord owns the real estate",
                "reachable_value": "Operating business of seven properties, subject to the lease",
                "cite": m_own,
            },
            {
                "entity": "Larchmere Digital Holdings, LLC (fictional)",
                "role": "Online sports-betting and iGaming business",
                "inside_credit_group": "Yes",
                "guarantees": "Guarantor",
                "liens": "First lien, but eligible for designation as unrestricted",
                "reachable_value": "Online licences and platform; at risk in a drop-down",
                "cite": join(m_lp, m_b),
            },
            {
                "entity": F.LANDLORD,
                "role": "Landlord under the master lease",
                "inside_credit_group": "No",
                "guarantees": "None",
                "liens": "Owns the seven leased properties",
                "reachable_value": "Not reachable by creditors",
                "cite": m_own,
            },
        ],
    )
    h.table(
        "cp4.red_flags",
        [
            {
                "flag": "Unrestricted-subsidiary drop-down",
                "provision": f"Designation: {lp['designation']}.",
                "creditor_risk": "Valuable assets, such as the online business, can leave the collateral package.",
                "severity": "High",
                "pd_lgd_effect": "Raises LGD for second-lien and unsecured creditors; leaves PD unchanged.",
                "cite": join(m_lp, m_b),
            },
            {
                "flag": "Non-pro-rata open-market purchases",
                "provision": f"Purchases: {lp['open_market']}.",
                "creditor_risk": "A group of lenders can be favoured over the others in a liability-management exercise.",
                "severity": "High",
                "pd_lgd_effect": "Raises LGD for lenders outside the group.",
                "cite": m_lp,
            },
            {
                "flag": "Weak sacred rights",
                "provision": f"Amendments: {lp['sacred']}.",
                "creditor_risk": "A majority of 50.1% can subordinate liens or payment priority of the rest.",
                "severity": "High",
                "pd_lgd_effect": "Raises LGD for minority lenders and makes an uptier executable.",
                "cite": m_lp,
            },
            {
                "flag": "Cure rights deemed as EBITDA",
                "provision": f"Equity cure: {lp['cure_frequency']}.",
                "creditor_risk": "A cure restores the covenant on paper without reducing debt.",
                "severity": "Medium",
                "pd_lgd_effect": "Delays default; PD effect is one quarter.",
                "cite": m_cov,
            },
            {
                "flag": "Cross-default to the master lease",
                "provision": "A funded-debt default not cured in 30 days is a lease event of default.",
                "creditor_risk": "The landlord can terminate on seven properties after a funded-debt default.",
                "severity": "High",
                "pd_lgd_effect": "Raises PD and LGD together because the leased EBITDA is lost on termination.",
                "cite": m_own,
            },
        ],
    )
    h.table(
        "cp4.ebitda_definition",
        [
            {
                "feature": "Rent deducted",
                "clause": "Consolidated EBITDA is stated after cash rent under the master lease.",
                "cap_or_condition": "None",
                "capacity_effect": f"Covenant EBITDA {plain(ebitda)} against stated {plain(cov['adj'])}: rent lowers the test EBITDA by {plain(cov['rent'])}.",
                "cite": f"{m_rent}{m_adj} {cov['cov_s']}",
            },
            {
                "feature": "Run-rate cost savings",
                "clause": "Projected savings may be added back for actions taken or expected within the period.",
                "cap_or_condition": f"Capped at {lp['savings_cap_pct']}% of Consolidated EBITDA over {lp['savings_months']} months",
                "capacity_effect": "The 16 LTM of savings fits well inside the cap, so the company can count savings RBOT rejects.",
                "cite": m_lp,
            },
            {
                "feature": "Equity cure amount",
                "clause": "Cure proceeds are deemed EBITDA for the test quarter.",
                "cap_or_condition": "Cannot exceed the amount needed to comply",
                "capacity_effect": f"A cure of {plain(cov['cure'])} restores 6.50x.",
                "cite": f"{m_cov} {cov['cure_s']}",
            },
        ],
    )
    scores = [
        (
            "Financial covenants",
            "2",
            "A springing leverage test and two maintenance floors are in force, and the leverage test has now sprung and been breached.",
            m_cov,
        ),
        (
            "Debt capacity",
            "4",
            f"{plain(fc_rem)} of free-and-clear first-lien capacity is available outside any ratio test.",
            f"{m_b} {fc_s}",
        ),
        (
            "Lien capacity",
            "3",
            f"A general lien basket of {plain(li_cap)} with {plain(li_rem)} remaining.",
            f"{m_b} {li_s}",
        ),
        (
            "Restricted payments",
            "3",
            f"A general basket of {plain(rp_cap)} with {plain(rp_rem)} remaining; no builder basket while earnings are negative.",
            f"{m_b} {rp_s}",
        ),
        (
            "Investments and unrestricted subsidiaries",
            "5",
            f"A drop-down basket of {plain(in_cap)} with no leverage test.",
            f"{m_b}{m_lp} {in_s}",
        ),
        (
            "Amendments and sacred rights",
            "5",
            "Priority and liens can be changed with 50.1% consent.",
            m_lp,
        ),
    ]
    h.table(
        "cp4.protection_score",
        [{"area": a, "score": sc, "evidence": ev, "cite": c} for a, sc, ev, c in scores],
    )
    h.analysis(
        f"The provisions weaken creditors most through amendment and asset-transfer capacity, and protect them least where it now matters. The first-lien springing test is Breached: net leverage is {plain(cov['lev'], 2)}x against 6.50x ({cov['lev_s']}) {m_cov}{m_adj}{m_lease}. "
        f"Covenant EBITDA is {plain(ebitda)} because the credit agreement deducts cash rent {m_rent}; the minimum liquidity floor of 50 is Tight with {plain(cov['liq_head'])} of headroom ({cov['liq_s']}) {m_cash}.\n\n"
        f"The sponsor's equity cure is available once and needs {plain(cov['cure'])} of deemed EBITDA ({cov['cure_s']}); a funded cure buys one quarter and does not reduce debt. "
        f"Three terms make the PD/LGD picture worse: the unrestricted-subsidiary basket of {plain(in_rem)} with no leverage test, open-market purchases that need not be offered to all lenders, and amendments of priority at 50.1% {m_lp}. "
        f"Free-and-clear capacity of {plain(fc_rem)} falls {plain(short)} short of the sponsor's 150 priming proposal, so the proposal relies on a majority-lender amendment ({short_s}) {m_b}.\n\n"
        "Module view: the documents give the borrower more room than the lenders to reshape the structure, and the lessor's cross-default adds a third party with a veto. Confidence is Medium because the summaries in the pack are not the executed documents."
    )
    h.gaps(
        "- Executed documents: the pack holds the amended credit agreement and the indenture but only a summary of the master lease and the intercreditor. Effect: lease termination mechanics and intercreditor standstill periods are read from summaries. Lifted by: the executed documents.\n"
        "- Intercreditor standstill and turnover terms: not in the pack. Lifted by: the intercreditor agreement."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
