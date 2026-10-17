"""CZR CP-4: legal and covenant interpreter.

Real: the document register (dates, trustee, parties, governing law from the corpus), the covenant thresholds and the
incremental/ratio tests extracted from the credit agreement and the 2032 indenture (Front Pages data C338-C363), the
current ratios on RBOT's basis and the real CAOS CP-4 reading (principally incurrence covenants; overall
aggressiveness provisionally 4 of 5). Calculated: headroom, pari and junior capacity, remaining basket capacity.
Synthetic and marked: restricted-payment and investment basket sizes and usage (`czr.rp_investment_baskets`, the real
extraction did not find them, G32) and, in Primary runs, the pro forma tests for the three merger tranches.

The protection score is on a protection scale (5 is the most lender-protective). The real CAOS CP-4 scored the package
4 of 5 for aggressiveness (5 the most creditor-adverse), which reads as 2 of 5 here.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from core import GAP, Ctx, D, Handoff, compute, plain
from czr.cp_3 import AS_OF, FACTS, cite_fact, is_primary, num, tranche_rows
from helpers import join_marks

FOLDER = "full-credit-assessment-2026-10-06"
Q10 = "CZR_Q2_2026_10Q.txt"
NPORT_NOTE = "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt"
FIFTH = "CZR_2024_Credit_Agreement_Fifth_Amendment.txt"
FOURTH = "CZR_2024_Credit_Agreement_Fourth_Amendment.txt"
INCR3 = "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt"
SUPP1 = "CZR_2024_650_Notes_First_Supplemental_Indenture.txt"
SUPP2 = "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt"
MERGER = "CZR_2026_Merger_Agreement.txt"


def status_of(threshold: Decimal, headroom: Decimal) -> str:
    """Covenant status rule (Front Pages): Breached below zero, Tight under 10% of the threshold, else Headroom."""
    if headroom < 0:
        return "Breached"
    return "Tight" if headroom < threshold / 10 else "Headroom"


def _iso(figure_raw: str) -> str:
    return datetime.strptime(figure_raw.strip(), "%B %d, %Y").date().isoformat()


def covenant_rows(ctx: Ctx, h: Handoff, tranches: list[dict]) -> list[dict]:
    """Covenant tests with headroom on RBOT's basis (company LTM Adjusted EBITDA, face debt)."""
    ebitda = ctx.val("ltm_adj_ebitda_q2_2026")
    basis = "RBOT basis: company LTM Adjusted EBITDA and face debt; the agreement's EBITDA and debt definitions are not reconciled (G34)"
    rows: list[dict] = []

    def add(test, ttype, direction, thr, cur, thr_c, cur_c, basis_txt, extra_calc=""):
        thr_d, cur_d = D(thr), D(cur)
        hd, hd_s = compute(
            f"{test} headroom",
            "thr - cur" if direction == "Ceiling" else "cur - thr",
            2,
            "x",
            thr=thr_d,
            cur=cur_d,
        )
        h.meta.setdefault("calc", {})[test] = hd_s
        rows.append(
            {
                "test": test,
                "test_type": ttype,
                "direction": direction,
                "threshold": plain(thr_d, 2),
                "current_value": plain(cur_d, 2),
                "unit_label": "x",
                "basis": basis_txt,
                "headroom": plain(hd, 2),
                "status": status_of(thr_d, hd),
                "cite": join_marks(thr_c, cur_c)
                + " "
                + (extra_calc + " " if extra_calc else "")
                + hd_s,
            }
        )

    c_tlr, c_fccr = h.cite_fig("cov_max_total_leverage"), h.cite_fig("cov_min_fccr")
    c_sslr, c_jr, c_ind = (
        h.cite_fig("cov_incr_pari_sslr"),
        h.cite_fig("cov_incr_junior_tslr"),
        h.cite_fig("ind_ratio_debt_fccr"),
    )
    nl, ci, sl, tl = (
        h.cite_fig(k)
        for k in (
            "net_leverage_ltm",
            "cash_interest_cover_ltm",
            "senior_leverage_ltm",
            "total_leverage_ltm",
        )
    )
    add(
        "Total Leverage Ratio (revolver and Term Loan A)",
        "Maintenance",
        "Ceiling",
        ctx.val("cov_max_total_leverage"),
        ctx.val("net_leverage_ltm"),
        c_tlr,
        nl,
        basis,
    )
    add(
        "Fixed Charge Coverage Ratio (revolver and Term Loan A)",
        "Maintenance",
        "Floor",
        ctx.val("cov_min_fccr"),
        ctx.val("cash_interest_cover_ltm"),
        c_fccr,
        ci,
        basis,
    )
    add(
        "Pari secured incremental test",
        "Incurrence",
        "Ceiling",
        ctx.val("cov_incr_pari_sslr"),
        ctx.val("senior_leverage_ltm"),
        c_sslr,
        sl,
        basis,
    )
    add(
        "Junior secured incremental test",
        "Incurrence",
        "Ceiling",
        ctx.val("cov_incr_junior_tslr"),
        ctx.val("senior_leverage_ltm"),
        c_jr,
        sl,
        basis + "; all secured debt is first lien, so total secured equals senior secured leverage",
    )
    add(
        "Ratio debt test (2032 secured notes indenture)",
        "Incurrence",
        "Floor",
        ctx.val("ind_ratio_debt_fccr"),
        ctx.val("cash_interest_cover_ltm"),
        c_ind,
        ci,
        basis,
    )
    add(
        "Restricted payments permitted below 4.75x leverage",
        "Incurrence",
        "Ceiling",
        D("4.75"),
        ctx.val("total_leverage_ltm"),
        h.cite_caos(FOLDER, "CP-4", 4),
        tl,
        basis,
    )
    if tranches:
        syn = cite_fact(h, "merger_tranches")
        new_all = sum((D(t["size"]) for t in tranches), Decimal(0))
        new_sec = sum((D(t["size"]) for t in tranches if t["debt_type"] != "SU Notes"), Decimal(0))
        debt, cash, sec = (
            ctx.val("total_debt_check_2026_06_30"),
            ctx.val("cash_2026_06_30"),
            ctx.val("senior_secured_debt_2026_06_30"),
        )
        pf_rows = ctx.get(h.run_id, "CP-1").rows("cp1.pro_forma_adjustment_register")
        new_int = -sum(
            (D(r["value"]) for r in pf_rows if r["metric_id"] == "cash_interest_paid"), Decimal(0)
        )
        pf_net, pf_net_s = compute(
            "pro forma net leverage",
            "(debt + new - cash) / ebitda",
            2,
            "x",
            debt=debt,
            new=new_all,
            cash=cash,
            ebitda=ebitda,
        )
        pf_sec, pf_sec_s = compute(
            "pro forma senior secured leverage",
            "(sec + new) / ebitda",
            2,
            "x",
            sec=sec,
            new=new_sec,
            ebitda=ebitda,
        )
        base_int = ctx.val("ltm_cash_interest_debt_q2_2026")
        pf_cov, pf_cov_s = compute(
            "pro forma debt cash interest cover",
            "ebitda / (base + new)",
            2,
            "x",
            ebitda=ebitda,
            base=base_int,
            new=new_int,
        )
        pf_basis = "Pro forma for the three synthetic merger tranches at the talk mid; " + basis
        add(
            "Total Leverage Ratio, pro forma for the merger tranches",
            "Maintenance",
            "Ceiling",
            ctx.val("cov_max_total_leverage"),
            pf_net,
            c_tlr,
            join_marks(syn, nl),
            pf_basis,
            pf_net_s,
        )
        add(
            "Pari secured incremental test, pro forma for the merger tranches",
            "Incurrence",
            "Ceiling",
            ctx.val("cov_incr_pari_sslr"),
            pf_sec,
            c_sslr,
            join_marks(syn, sl),
            pf_basis,
            pf_sec_s,
        )
        add(
            "Fixed Charge Coverage Ratio, pro forma for the merger tranches",
            "Maintenance",
            "Floor",
            ctx.val("cov_min_fccr"),
            pf_cov,
            c_fccr,
            join_marks(syn, ci),
            pf_basis,
            pf_cov_s,
        )
    return rows


def capacity_rows(ctx: Ctx, h: Handoff) -> list[dict]:
    bk = FACTS["rp_investment_baskets"]
    rp = cite_fact(h, "rp_investment_baskets")
    pari_c, jr_c, fc_c = (
        h.cite_fig("cap_pari_secured"),
        h.cite_fig("cap_junior_secured"),
        h.cite_fig("cap_free_clear_size"),
    )
    sec_c = h.cite_fig("senior_secured_debt_2026_06_30")
    caos_debt = h.cite_caos(FOLDER, "CP-4", 3)
    caos_rp_gen, caos_rp_ratio = h.cite_caos(FOLDER, "CP-4", 5), h.cite_caos(FOLDER, "CP-4", 4)
    caos_inv = h.cite_caos(FOLDER, "CP-4", 6)

    def synth(label, size, used, ctype, basket, formula, severity, risk, impl, cite):
        size_d, used_d = D(size), D(used)
        rem, rem_s = compute(f"{label} remaining", "size - used", 0, size=size_d, used=used_d)
        return {
            "capacity_type": ctype,
            "basket": basket,
            "formula": formula,
            "used": plain(used_d),
            "remaining": plain(rem),
            "currency": "USD",
            "unit": "MILLIONS",
            "status": "Calculated",
            "severity": severity,
            "risk_mechanism": risk,
            "credit_implication": impl,
            "cite": join_marks(rp, cite) + " " + rem_s,
        }

    return [
        {
            "capacity_type": "Debt",
            "basket": "Pari secured to 4.50x",
            "formula": f"Ratio test: pro forma Senior Secured Leverage Ratio up to {plain(ctx.val('cov_incr_pari_sslr'), 2)}x on LTM Adjusted EBITDA, less senior secured debt",
            "used": plain(ctx.val("senior_secured_debt_2026_06_30")),
            "remaining": plain(ctx.val("cap_pari_secured")),
            "currency": "USD",
            "unit": "MILLIONS",
            "status": "Calculated",
            "severity": "High",
            "risk_mechanism": "New first-lien debt shares the collateral",
            "credit_implication": "Secured debt ahead of the unsecured notes could grow by this much without lender consent",
            "cite": join_marks(pari_c, sec_c, h.cite_fig("cov_incr_pari_sslr")),
        },
        {
            "capacity_type": "Debt",
            "basket": "Junior secured to 4.75x",
            "formula": f"Ratio test: pro forma Total Secured Leverage Ratio up to {plain(ctx.val('cov_incr_junior_tslr'), 2)}x on LTM Adjusted EBITDA, less senior secured debt",
            "used": plain(ctx.val("senior_secured_debt_2026_06_30")),
            "remaining": plain(ctx.val("cap_junior_secured")),
            "currency": "USD",
            "unit": "MILLIONS",
            "status": "Calculated",
            "severity": "Medium",
            "risk_mechanism": "Junior liens rank ahead of the unsecured notes",
            "credit_implication": "An alternative to the pari amount, not additive",
            "cite": join_marks(jr_c, sec_c, h.cite_fig("cov_incr_junior_tslr")),
        },
        {
            "capacity_type": "Debt",
            "basket": "Free-and-clear",
            "formula": f"The greater of US$2,600m and 1.00x EBITDA, size {plain(ctx.val('cap_free_clear_size'))}",
            "used": "Not computable",
            "remaining": "Not computable",
            "currency": "USD",
            "unit": "MILLIONS",
            "status": "Not computable",
            "severity": "Medium",
            "risk_mechanism": "Fixed-dollar and grower debt outside any ratio test",
            "credit_implication": "Size is known; the amount already used is not (G33)",
            "cite": join_marks(fc_c, h.cite_fig("cov_incr_free_clear")),
        },
        {
            "capacity_type": "Debt",
            "basket": "General debt basket",
            "formula": "The greater of US$750m and 32.5% of EBITDA",
            "used": "Not computable",
            "remaining": "Not computable",
            "currency": "USD",
            "unit": "MILLIONS",
            "status": "Not computable",
            "severity": "Medium",
            "risk_mechanism": "Debt and liens under the fixed/grower basket",
            "credit_implication": "Formula only; usage is not disclosed",
            "cite": join_marks(caos_debt),
        },
        synth(
            "General restricted-payment basket",
            bk["general_rp_basket"],
            bk["rp_used"],
            "Restricted payments",
            "General restricted-payment basket",
            "The greater of US$500m and 22.5% of EBITDA (the fixture uses the US$500m floor); synthetic usage",
            "Medium",
            "Cash leaves the restricted group to equity holders",
            "Leakage capacity is available and unused in the synthetic usage",
            join_marks(caos_rp_gen),
        ),
        synth(
            "Builder basket",
            bk["builder_basket"],
            bk["builder_used"],
            "Restricted payments",
            "Builder basket (cumulative credit)",
            "Cumulative credit route plus a 4.75x leverage-based permission; synthetic size and usage",
            "High",
            "Retained earnings can be paid out ahead of creditors",
            "A large builder balance is the main leakage route",
            join_marks(caos_rp_ratio),
        ),
        synth(
            "General investment basket",
            bk["general_investment_basket"],
            bk["investment_used"],
            "Investments",
            "General investment basket",
            "Fixed-dollar and grower basket for investments outside the credit group; synthetic size and usage",
            "Medium",
            "Value moves to entities that do not guarantee the debt",
            "Reduces the assets behind the guarantees",
            join_marks(caos_inv),
        ),
        {
            "capacity_type": "Investments",
            "basket": "Unrestricted subsidiary investments",
            "formula": "Investments in unrestricted subsidiaries; the fixture's synthetic capacity of US$900m, usage not stated",
            "used": "Not stated",
            "remaining": plain(D(bk["unrestricted_sub_capacity"])),
            "currency": "USD",
            "unit": "MILLIONS",
            "status": "Directional",
            "severity": "High",
            "risk_mechanism": "Drop-down of assets into an unrestricted subsidiary",
            "credit_implication": "The classic route for moving value out of the collateral",
            "cite": join_marks(rp, caos_inv),
        },
    ]


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-4", "CZR", run_id, AS_OF, ["CP-0", "CP-1", "MODEL"], fixture_file="czr/cp_4.py"
    )
    h.qa("Restricted")
    primary = is_primary(ctx, run_id)
    tranches = tranche_rows(ctx, run_id) if primary else []

    # ---- documents (real)
    def cite_line(file: str, needle: str) -> str:
        return h.cite_doc_find(file, needle)

    ca = cite_line(Q10, "CEI is party to a credit agreement, dated as of July 20, 2020")
    incr3 = cite_line(INCR3, "INCREMENTAL ASSUMPTION AGREEMENT NO. 3, dated as of February 6, 2024")
    fourth = cite_line(FOURTH, "FOURTH AMENDMENT TO CREDIT AGREEMENT, dated as of May 9, 2024")
    fifth = cite_line(FIFTH, "FIFTH AMENDMENT TO CREDIT AGREEMENT, dated as of November 25, 2024")
    supp1 = cite_line(SUPP1, "THIS FIRST SUPPLEMENTAL INDENTURE (this")
    supp2 = cite_line(SUPP2, "THIS SECOND SUPPLEMENTAL INDENTURE (this")
    law_ny_ind = cite_line(
        NPORT_NOTE,
        "THIS INDENTURE AND THE SECURITIES SHALL BE GOVERNED BY, AND CONSTRUED IN ACCORDANCE WITH, THE LAWS OF THE STATE OF NEW YORK.",
    )
    law_ny_supp1 = cite_line(
        SUPP1,
        "THIS SUPPLEMENTAL INDENTURE SHALL BE GOVERNED BY, AND CONSTRUED IN ACCORDANCE WITH, THE LAWS OF THE STATE OF NEW YORK.",
    )
    law_ny_supp2 = cite_line(
        SUPP2,
        "THIS SUPPLEMENTAL INDENTURE SHALL BE GOVERNED BY, AND CONSTRUED IN ACCORDANCE WITH, THE LAWS OF THE STATE OF NEW YORK.",
    )
    law_ny_4 = cite_line(FOURTH, "GOVERNED BY THE LAW OF THE STATE OF NEW YORK")
    law_ny_5 = cite_line(FIFTH, "GOVERNED BY THE LAW OF THE STATE OF NEW YORK")
    law_de = cite_line(
        MERGER,
        "shall be governed by and construed in accordance with the Laws of the State of Delaware",
    )
    d = lambda k: join_marks(h.cite_fig(k))  # noqa: E731
    f = lambda k: ctx.figure(k)["raw"]  # noqa: E731
    docs = [
        (
            "Credit Agreement (CEI)",
            "Credit agreement",
            _iso(f("doc_credit_agreement_date")),
            "CEI (borrower); JPMorgan Chase Bank, N.A. (administrative agent); U.S. Bank National Association (collateral agent)",
            GAP,
            "In force",
            join_marks(d("doc_credit_agreement_date"), ca),
        ),
        (
            "Incremental Assumption Agreement No. 3",
            "Credit agreement",
            _iso(f("doc_incr3_date")),
            "CEI and the lenders of the incremental Term B-1 loans",
            GAP,
            "In force",
            join_marks(d("doc_incr3_date"), incr3),
        ),
        (
            "Fourth Amendment to Credit Agreement",
            "Credit agreement",
            _iso(f("doc_amend4_date")),
            "CEI (borrower), Term B lenders and the administrative agent",
            "New York",
            "In force",
            join_marks(d("doc_amend4_date"), fourth, law_ny_4),
        ),
        (
            "Fifth Amendment to Credit Agreement",
            "Credit agreement",
            _iso(f("doc_amend5_date")),
            "CEI (borrower), Term B and Term B-1 lenders and the administrative agent",
            "New York",
            "In force",
            join_marks(d("doc_amend5_date"), fifth, law_ny_5),
        ),
        (
            "6.500% Senior Secured Notes due 2032 Indenture",
            "Indenture",
            _iso(f("doc_indenture_2032_date")),
            "CEI (issuer); subsidiary guarantors; "
            + f("doc_indenture_2032_trustee")
            + " (trustee)",
            "New York",
            "In force",
            join_marks(d("doc_indenture_2032_date"), d("doc_indenture_2032_trustee"), law_ny_ind),
        ),
        (
            "First Supplemental Indenture (2032 notes)",
            "Indenture",
            _iso(f("doc_suppl1_date")),
            "CEI; new guarantors Caesars Interactive Entertainment New Jersey, LLC and Tropicana Atlantic City Corp.; trustee and collateral agent",
            "New York",
            "In force",
            join_marks(d("doc_suppl1_date"), supp1, law_ny_supp1),
        ),
        (
            "Second Supplemental Indenture (2032 notes)",
            "Indenture",
            _iso(f("doc_suppl2_date")),
            "CEI; the new guarantors in Schedule A; U.S. Bank Trust Company, National Association (trustee); U.S. Bank National Association (collateral agent)",
            "New York",
            "In force",
            join_marks(d("doc_suppl2_date"), supp2, law_ny_supp2),
        ),
        (
            "Merger Agreement",
            "Other",
            _iso(f("issuer.merger.agreement_date")),
            f("issuer.merger.parent")
            + "; "
            + f("issuer.merger.merger_sub")
            + "; "
            + f("issuer.merger.parent_guarantor")
            + " (Parent Guarantor)",
            "Delaware",
            "Signed, pending close",
            join_marks(
                d("issuer.merger.agreement_date"),
                d("issuer.merger.parent"),
                d("issuer.merger.merger_sub"),
                d("issuer.merger.parent_guarantor"),
                law_de,
            ),
        ),
    ]
    h.table(
        "cp4.document_register",
        [
            {
                "document": a,
                "document_type": b,
                "document_date": c,
                "parties": e,
                "governing_law": g,
                "status": s,
                "cite": ci,
            }
            for a, b, c, e, g, s, ci in docs
        ],
    )

    cov = covenant_rows(ctx, h, tranches)
    h.table("cp4.covenant_tests", cov)
    h.table("cp4.capacity_register", capacity_rows(ctx, h))

    # ---- structure map (real roles; reachable value is not quantified)
    h.table(
        "cp4.structure_map",
        [
            {
                "entity": "Caesars Entertainment, Inc.",
                "role": "Borrower under the CEI facilities and issuer of the notes",
                "inside_credit_group": "Yes",
                "guarantees": "Borrower; guaranteed by material wholly owned domestic subsidiaries",
                "liens": "First-priority liens on substantially all assets, subject to exceptions",
                "reachable_value": "Not quantified (entity values are not supplied)",
                "cite": join_marks(d("issuer.name"), h.cite_caos(FOLDER, "CP-4", 16)),
            },
            {
                "entity": "Subsidiary Guarantors",
                "role": "Added by the supplemental indentures of March and August 2024",
                "inside_credit_group": "Yes",
                "guarantees": "Joint and several guarantee of the secured notes, subject to a fraudulent-transfer limit",
                "liens": "Pledged collateral under the security documents",
                "reachable_value": "Not quantified (the full guarantor schedule is missing)",
                "cite": join_marks(supp1, supp2, h.cite_caos(FOLDER, "CP-4", 16)),
            },
            {
                "entity": "Caesars Virginia (CVA)",
                "role": "Separate borrower of the delayed draw term loan and revolver",
                "inside_credit_group": "No",
                "guarantees": "CEI does not guarantee these facilities",
                "liens": "Secured by Virginia-entity assets",
                "reachable_value": "Not quantified (entity-level value and debt allocation not supplied)",
                "cite": join_marks(h.cite_caos(FOLDER, "CP-4", 18)),
            },
            {
                "entity": "GLPI and VICI",
                "role": "Landlords under the master leases",
                "inside_credit_group": "No",
                "guarantees": "Lease obligations sit outside reported debt",
                "liens": "Not stated",
                "reachable_value": f"Financing obligations of {num(ctx.val('lt_financing_obligations_2026_06_30'))} outside debt",
                "cite": join_marks(h.cite_fig("lt_financing_obligations_2026_06_30")),
            },
        ],
    )

    # ---- red flags (real provisions, severity is the module's view)
    sl_m = join_marks(h.cite_fig("senior_leverage_ltm"))
    flags = [
        (
            "Term Loan B-1 is a Non-Covenant Facility",
            d("cov_tlb1_non_covenant"),
            "Lenders of the largest loan have no maintenance test",
            "High",
            "PD up: no early trigger; LGD neutral",
            d("cov_tlb1_non_covenant"),
        ),
        (
            "Maintenance tests spring after Term A is repaid",
            d("cov_springing_after_tla"),
            "The only maintenance tests fall away once Term Loan A is repaid",
            "Medium",
            "PD up after Term A repayment",
            d("cov_springing_after_tla"),
        ),
        (
            "Asset-sale sweep falls away at 3.00x or below",
            f"{d('cov_asset_sale_stepdown_300')}; Caesars is at {num(ctx.val('senior_leverage_ltm'), 2)}x {sl_m}",
            "Less cash is swept to lenders as leverage falls",
            "High",
            "LGD up: asset-sale proceeds stay with the issuer",
            join_marks(d("cov_asset_sale_stepdown_300"), sl_m),
        ),
        (
            "Equity cure right for the maintenance tests",
            d("cov_equity_cure"),
            "A breach can be cured with sponsor cash",
            "Medium",
            "PD down short term; hides the trend",
            d("cov_equity_cure"),
        ),
        (
            "Pro forma synergies count in indenture EBITDA",
            d("ind_pro_forma_synergies"),
            "Reasonably expected savings raise EBITDA and debt capacity",
            "Medium",
            "PD up: capacity headroom is overstated",
            d("ind_pro_forma_synergies"),
        ),
        (
            "Pari secured capacity could rank ahead of the unsecured notes",
            f"{num(ctx.val('cap_pari_secured'))} of capacity under the 4.50x test {join_marks(h.cite_fig('cap_pari_secured'))}",
            "New first-lien debt dilutes the collateral and primes the unsecured notes",
            "High",
            "LGD up for unsecured, and for secured if the collateral is shared",
            join_marks(h.cite_fig("cap_pari_secured"), d("cov_incr_pari_sslr")),
        ),
        (
            "Change of control put (protective)",
            f"Put at {num(ctx.val('ind_change_of_control'))}% on the 2032 secured notes {d('ind_change_of_control')}",
            "Holders can put the notes if control changes",
            "Low",
            "LGD down: par-like exit on a change of control",
            d("ind_change_of_control"),
        ),
    ]
    h.table(
        "cp4.red_flags",
        [
            {
                "flag": a,
                "provision": b,
                "creditor_risk": c,
                "severity": s,
                "pd_lgd_effect": e,
                "cite": ci,
            }
            for a, b, c, s, e, ci in flags
        ],
    )

    # ---- EBITDA definition
    h.table(
        "cp4.ebitda_definition",
        [
            {
                "feature": "Pro forma cost savings and synergies",
                "clause": d("ind_pro_forma_synergies"),
                "cap_or_condition": "Reasonably expected; no numeric cap in the excerpt",
                "capacity_effect": "Raises EBITDA, so raises capacity",
                "cite": d("ind_pro_forma_synergies"),
            },
            {
                "feature": "Testing Condition carve-out",
                "clause": d("cov_testing_condition_pct"),
                "cap_or_condition": f"Revolver use above {num(ctx.val('cov_testing_condition_pct'))}% of commitments, after undrawn letters of credit {d('cov_testing_condition_pct')}",
                "capacity_effect": "Lets the revolver be drawn to the carve-out without testing",
                "cite": d("cov_testing_condition_pct"),
            },
            {
                "feature": "Asset-sale step-downs",
                "clause": join_marks(
                    d("cov_asset_sale_stepdown_350"), d("cov_asset_sale_stepdown_300")
                ),
                "cap_or_condition": f"50% of proceeds need not prepay at {num(ctx.val('cov_asset_sale_stepdown_350'), 2)}x; none at {num(ctx.val('cov_asset_sale_stepdown_300'), 2)}x",
                "capacity_effect": "Less cash is swept to lenders as leverage falls",
                "cite": join_marks(
                    d("cov_asset_sale_stepdown_350"), d("cov_asset_sale_stepdown_300")
                ),
            },
            {
                "feature": "Covenant EBITDA against company Adjusted EBITDA",
                "clause": join_marks(d("cov_tlr_definition"), d("cov_fccr_definition")),
                "cap_or_condition": "The covenants use Total Net Debt / EBITDA and EBITDA / Cash Interest Expense; the covenant EBITDA bridge is not in the pack (G34)",
                "capacity_effect": "Headroom here is on company Adjusted EBITDA and is indicative until the definitions are reconciled",
                "cite": join_marks(d("cov_tlr_definition"), d("cov_fccr_definition")),
            },
        ],
    )

    # ---- protection score (5 = most lender-protective; CAOS aggressiveness 4 of 5 reads as 2)
    ps = [
        (
            "Maintenance covenants",
            "2",
            f"Tests protect the revolver and Term Loan A only {d('cov_covenant_facilities')}; Term Loan B-1 has none {d('cov_tlb1_non_covenant')}",
            join_marks(d("cov_covenant_facilities"), d("cov_tlb1_non_covenant")),
        ),
        (
            "Debt and lien capacity",
            "2",
            f"Pari capacity of {num(ctx.val('cap_pari_secured'))} and a free-and-clear amount of {num(ctx.val('cap_free_clear_size'))} {join_marks(h.cite_fig('cap_pari_secured'))}{d('cov_incr_free_clear')}",
            join_marks(h.cite_fig("cap_pari_secured"), d("cov_incr_free_clear")),
        ),
        (
            "Restricted payments and leakage",
            "2",
            f"Builder basket, a general basket of the greater of US$500m and 22.5% of EBITDA and a 4.75x leverage-based permission {join_marks(h.cite_caos(FOLDER, 'CP-4', 4), h.cite_caos(FOLDER, 'CP-4', 5))}",
            join_marks(h.cite_caos(FOLDER, "CP-4", 4), h.cite_caos(FOLDER, "CP-4", 5)),
        ),
        (
            "Change of control",
            "4",
            f"Put at {num(ctx.val('ind_change_of_control'))}% on the 2032 secured notes {d('ind_change_of_control')}",
            d("ind_change_of_control"),
        ),
        (
            "Asset-sale protection",
            "2",
            f"Sweep steps down at {num(ctx.val('cov_asset_sale_stepdown_350'), 2)}x and ends at {num(ctx.val('cov_asset_sale_stepdown_300'), 2)}x {join_marks(d('cov_asset_sale_stepdown_350'), d('cov_asset_sale_stepdown_300'))}",
            join_marks(d("cov_asset_sale_stepdown_350"), d("cov_asset_sale_stepdown_300")),
        ),
        (
            "Disclosure",
            "3",
            "Agreement and indenture terms were extracted; restricted-payment and investment baskets were not (G32), and the full credit agreement and intercreditor agreement are missing",
            join_marks(h.cite_caos(FOLDER, "CP-4", 1), h.cite_caos(FOLDER, "CP-4", 13)),
        ),
        (
            "Overall",
            "2",
            "The real CAOS CP-4 scored overall aggressiveness 4 of 5 (5 the most creditor-adverse); on this protection scale that is 2 of 5",
            join_marks(h.cite_caos(FOLDER, "CP-4", 3), h.cite_caos(FOLDER, "CP-4", 4)),
        ),
    ]
    h.table(
        "cp4.protection_score",
        [{"area": a, "score": s, "evidence": e, "cite": c} for a, s, e, c in ps],
    )

    # ---- analysis
    tl, fc = cov[0], cov[1]
    cc = lambda ids: join_marks(*(h.cite_caos(FOLDER, "CP-4", i) for i in ids))  # noqa: E731
    pari_m = join_marks(h.cite_fig("cap_pari_secured"))
    paras = [
        f"The documented package protects creditors with guarantees, collateral and sacred-right thresholds, but it is mainly an incurrence-covenant structure: the notes carry no maintenance test, and the facility tests apply only to the revolver and Term Loan A {cc([1, 2])}. "
        f"The supported risk is potential incremental leverage and value leakage through contractual baskets, not a demonstrated breach or a completed priming event. The real CAOS CP-4 put overall aggressiveness at 4 of 5, which is a protection score of 2 of 5 here, at confidence 57 of 100 and QA Restricted.",
        f"On RBOT's basis (company LTM Adjusted EBITDA and face debt) every tested covenant has room. Net leverage is {num(tl['current_value'])}x against a maximum of {num(tl['threshold'], 2)}x, headroom {num(tl['headroom'])}x ({h.meta['calc'][tl['test']]}); cash interest cover is {num(fc['current_value'], 2)}x against a minimum of {num(fc['threshold'], 2)}x, headroom {num(fc['headroom'])}x. "
        f"The covenant EBITDA and net debt definitions are not reconciled to the company's Adjusted EBITDA (G34), so these are indicative, and compliance at 30 June is reported but headroom is not {cc([2])}.",
    ]
    if primary:
        pf_tl = next(r for r in cov if "Total Leverage Ratio, pro forma" in r["test"])
        pf_fc = next(r for r in cov if "Fixed Charge Coverage Ratio, pro forma" in r["test"])
        pf_sl = next(r for r in cov if "Pari secured incremental test, pro forma" in r["test"])
        paras.append(
            f"With the three synthetic merger tranches layered on {cite_fact(h, 'merger_tranches')}, net leverage rises to {num(pf_tl['current_value'])}x (headroom {num(pf_tl['headroom'])}x), senior secured leverage to {num(pf_sl['current_value'])}x against the 4.50x pari test (headroom {num(pf_sl['headroom'])}x) and cash interest cover falls to {num(pf_fc['current_value'], 2)}x (headroom {num(pf_fc['headroom'], 2)}x). All stay in Headroom, so the new debt is covenant-feasible while using most of the pari secured capacity."
        )
    paras += [
        f"Capacity is the central creditor risk. The pari secured test allows about {num(ctx.val('cap_pari_secured'))} of further first-lien debt and the junior test about {num(ctx.val('cap_junior_secured'))} {pari_m}; these are alternatives, not additive. "
        f"The restricted-payment and investment baskets were not extracted (G32), so the register fills them with synthetic sizes and usage: a builder basket of {num(D(FACTS['rp_investment_baskets']['builder_basket']))} with {num(D(FACTS['rp_investment_baskets']['builder_used']))} used, a general restricted-payment basket of {num(D(FACTS['rp_investment_baskets']['general_rp_basket']))} and a general investment basket of {num(D(FACTS['rp_investment_baskets']['general_investment_basket']))}. The free-and-clear and general debt baskets stay Not computable because usage is not disclosed (G33).",
        "What would change this view: the full current credit agreement, the intercreditor agreement and a compliance certificate with basket usage would let the headroom be recomputed on covenant definitions and the leakage capacity be sized. "
        "A Term Loan B-1 amendment, a drop-down into an unrestricted subsidiary or a new pari financing would deteriorate the view. Confidence in this module: Low.",
    ]
    h.analysis("\n\n".join(paras))
    gaps = [
        "- Covenant EBITDA and net debt definitions: not reconciled (G34); headroom is on RBOT's basis. Lifted by: the compliance certificate and the full credit agreement.",
        "- Restricted-payment and investment baskets: not extracted (G32); sizes and usage in the capacity register are synthetic. Lifted by: the indenture covenant extraction and a basket tracker.",
        "- Free-and-clear and general debt basket usage: not disclosed (G33). Lifted by: a basket tracker.",
        "- Entity-level guarantor and collateral schedules and the intercreditor agreement are missing (G36); reachable value is not quantified.",
        "- Parties to the Incremental Assumption Agreement No. 3 and the credit agreement governing law are not in the delivered text.",
    ]
    if primary:
        gaps.append(
            "- The pro forma tests use the three synthetic merger tranches (G8). Lifted by: the commitment papers."
        )
    h.gaps("\n".join(gaps))
    return h
