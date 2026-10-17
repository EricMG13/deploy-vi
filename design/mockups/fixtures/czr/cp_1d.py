"""CZR CP-1D: earnings quality. Real amounts (CP-1's bridge), the real CAOS CP-1D findings, and calculated cash
conversion and adjusted debt. One deliberate softening: CAOS rejected the impairment and stock-compensation
exclusions as recurring; here they are Challenged and stay REALIZED so the Model ties to the issuer's
LTM Adjusted EBITDA of US$3,592m (the fixture check requires it). The leverage effect of rejecting them is shown in
the Analysis instead."""

from __future__ import annotations

from core import Ctx, D, Handoff, compute, plain
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"

PERIODS = [
    ("FY2023", "fy2023", "FY2023"),
    ("FY2024", "fy2024", "FY2024"),
    ("FY2025", "fy2025", "FY2025"),
    ("H1_2025", "h1_2025", "H1 2025"),
    ("H1_2026", "h1_2026", "H1 2026"),
]


def _bridge_amount(cp1: Handoff, addback: str, period: str) -> str:
    for r in cp1.rows("cp1.adjusted_ebitda_bridge"):
        if r["addback_id"] == addback and r["period_id"] == period:
            return r["value"]
    raise KeyError((addback, period))


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-1D",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "CP-1A", "CP-1B"],
        fixture_file="czr/cp_1d.py",
    )
    h.qa("Restricted")
    cp1 = ctx.get(run_id, "CP-1")
    cm = h.cite_caos

    # ---- add-back assessment: FY2025 and LTM for the three issuer add-backs
    spec = {
        "impairment": (
            "Impairment charges",
            cm(FOLDER, "CP-1D", 2),
            "Recurs every year (US$95m, US$302m and US$182m in FY2023 to FY2025). Non-cash, but it signals continuing property pressure, so the exclusion is Challenged.",
            "Recurring in three annual periods.",
        ),
        "transaction_costs": (
            "Transaction costs and other, net",
            join_marks(cm(FOLDER, "CP-1D", 3), cm(FOLDER, "CP-1D", 7)),
            "A grouped net line mixing costs, gains and legal reserves with no component split, so the amount cannot be supported; the US$10m of merger costs in Q2 are part of it.",
            "Recurs as a category in every period (US$6m, US$(285)m, US$72m in FY2023 to FY2025).",
        ),
        "sbc": (
            "Stock-based compensation expense",
            join_marks(cm(FOLDER, "CP-1D", 4), cm(FOLDER, "CP-1D", 8)),
            "Recurring compensation cost (US$104m, US$94m, US$95m): non-cash but not a one-off, so the exclusion is Challenged.",
            "Recurs every year and in both 2026 and 2025 interim periods.",
        ),
    }
    rows = []
    ltm_amt: dict[str, str] = {}
    for aid, (cat, marks, why, rec) in spec.items():
        for pid in ("FY2025", "LTM_Q2_2026"):
            amt = _bridge_amount(cp1, aid, pid)
            if pid == "LTM_Q2_2026":
                ltm_amt[aid] = amt
            rows.append(
                {
                    "addback_id": aid,
                    "period_id": pid,
                    "amount": amt,
                    "currency": "USD",
                    "unit": "MILLIONS",
                    "category": cat,
                    "house_realization_status": "REALIZED",
                    "verdict": "Challenged",
                    "rationale": why
                    + " Kept in house EBITDA (REALIZED) so the Model ties to the issuer's figure; see the Analysis for the effect of rejecting it.",
                    "recurrence": rec,
                    "cite": marks + ("" if pid == "FY2025" else " " + cp1_calc(cp1, aid)),
                }
            )
    h.table("cp1d.addback_assessment", rows)

    # ---- cash conversion
    cc = []
    for pid, suffix, _label in PERIODS:
        e, c_ = ctx.val(f"adj_ebitda_{suffix}"), ctx.val(f"cfo_{suffix}")
        cv, calc = compute("cash conversion", "cfo / ebitda * 100", 1, "%", cfo=c_, ebitda=e)
        cc.append(
            {
                "period_id": pid,
                "adjusted_ebitda": plain(e),
                "cfo": plain(c_),
                "conversion_pct": f"{plain(cv, 1)}%",
                "currency": "USD",
                "unit": "MILLIONS",
                "explanation": {
                    "FY2023": "Highest conversion of the period; before the 2024 working-capital outflow.",
                    "FY2024": "Trough: a US$240m working-capital outflow and higher cash interest.",
                    "FY2025": "CFO reconciles through cash taxes, working capital and other items; the filing does not attribute the gap to one cause.",
                    "H1_2025": "Six-month figure; discrete Q2 cash flows are not reported.",
                    "H1_2026": "Six-month figure; capex and cash interest are separate uses.",
                }[pid],
                "credit_implication": "Cash trails Adjusted EBITDA before capex, cash interest and rent, so earnings are not debt-paydown capacity.",
                "cite": join_marks(h.cite_fig(f"adj_ebitda_{suffix}"), h.cite_fig(f"cfo_{suffix}"))
                + f" {calc}",
            }
        )
    e, c_ = ctx.val("ltm_adj_ebitda_q2_2026"), ctx.val("ltm_cfo_q2_2026")
    cv, calc = compute("cash conversion", "cfo / ebitda * 100", 1, "%", cfo=c_, ebitda=e)
    cc.append(
        {
            "period_id": "LTM_Q2_2026",
            "adjusted_ebitda": plain(e),
            "cfo": plain(c_),
            "conversion_pct": f"{plain(cv, 1)}%",
            "currency": "USD",
            "unit": "MILLIONS",
            "explanation": "FY2025 plus H1 2026 less H1 2025; the filings give no LTM cash-flow statement.",
            "credit_implication": "About 36 cents of each dollar of Adjusted EBITDA reaches operating cash flow, before capex, cash interest and rent.",
            "cite": join_marks(h.cite_fig("ltm_adj_ebitda_q2_2026"), h.cite_fig("ltm_cfo_q2_2026"))
            + f" {calc}",
        }
    )
    h.table("cp1d.cash_conversion", cc)

    # ---- debt-like items
    fin = ctx.val("lt_financing_obligations_2026_06_30")
    dl = [
        {
            "item": "Long-term financing obligations (VICI and GLPI leases)",
            "amount": plain(fin),
            "currency": "USD",
            "unit": "MILLIONS",
            "period_id": "JUN30_2026",
            "treatment": "Debt-like",
            "basis": "Recognised failed sale-leaseback obligations with contractual cash rent; added once to reported debt. The 10-Q gives no lessor split for June.",
            "cite": h.cite_data("C184"),
        },
        {
            "item": "Operating lease liability",
            "amount": plain(ctx.val("operating_lease_liability_2025_12_31")),
            "currency": "USD",
            "unit": "MILLIONS",
            "period_id": "FY2025_END",
            "treatment": "Unclear",
            "basis": "Latest stated balance (31 December 2025); the June 2026 liability is not disclosed (G5), so it is not carried into June adjusted debt.",
            "cite": h.cite_data("C188"),
        },
        {
            "item": "Finance lease liability",
            "amount": plain(ctx.val("finance_lease_liability_2025_12_31")),
            "currency": "USD",
            "unit": "MILLIONS",
            "period_id": "FY2025_END",
            "treatment": "Unclear",
            "basis": "A fixed claim in principle, but the notes do not reconcile it to the financing-obligation line, so no increment is added.",
            "cite": h.cite_data("C191"),
        },
        {
            "item": "Customer deposits and other deferred revenue",
            "amount": "545",
            "currency": "USD",
            "unit": "MILLIONS",
            "period_id": "JUN30_2026",
            "treatment": "Not debt-like",
            "basis": "Operating float for wagers and future services, not borrowing; some cash could reverse in a demand shock.",
            "cite": cm(FOLDER, "CP-1D", 24),
        },
        {
            "item": "Sports sponsorship and partnership commitments",
            "amount": "309",
            "currency": "USD",
            "unit": "MILLIONS",
            "period_id": "JUN30_2026",
            "treatment": "Not debt-like",
            "basis": "Contractual purchases and services through 2040, outside the debt numerator; US$318m at FY2025.",
            "cite": cm(FOLDER, "CP-1D", 25),
        },
    ]
    h.table("cp1d.debt_like_items", dl)

    # ---- numbers used in the analysis
    debt_face = ctx.val("total_debt_face_2026_06_30")
    ltm = ctx.val("ltm_adj_ebitda_q2_2026")
    adj_debt, c_adj = compute("adjusted debt", "debt + fin", 0, "", debt=debt_face, fin=fin)
    adj_lev, c_lev = compute(
        "adjusted debt / LTM Adjusted EBITDA", "adj / ebitda", 2, "x", adj=adj_debt, ebitda=ltm
    )
    base_lev, c_base = compute(
        "debt / LTM Adjusted EBITDA", "debt / ebitda", 2, "x", debt=debt_face, ebitda=ltm
    )
    sbc, imp = D(ltm_amt["sbc"]), D(ltm_amt["impairment"])
    e1, _ = compute("EBITDA without SBC", "ebitda - sbc", 0, "", ebitda=ltm, sbc=sbc)
    l1, c_l1 = compute("leverage without SBC", "debt / e", 2, "x", debt=debt_face, e=e1)
    e2, _ = compute(
        "EBITDA without SBC and impairment",
        "ebitda - sbc - imp",
        0,
        "",
        ebitda=ltm,
        sbc=sbc,
        imp=imp,
    )
    l2, c_l2 = compute(
        "leverage without SBC and impairment", "debt / e", 2, "x", debt=debt_face, e=e2
    )
    conv = cc[-1]["conversion_pct"]

    text = (
        f"Only part of Adjusted EBITDA is supported by evidence: three exclusions are open and none can be fully accepted. Adjusted EBITDA is the issuer's own measure, and its reconciliation excludes impairment (US$182m in FY2025), a grouped transaction-and-other line (US$72m) and stock-based compensation (US$95m). "
        "CAOS found impairment and stock compensation recurring in every annual period and rejected them as exceptional; the transaction line recurs but mixes unlike items, so it stays unresolved. {2, 3, 4, 5}\n\n"
        f"This module records all three as Challenged and keeps them in house EBITDA so the Model ties to the issuer's US$3,592m LTM figure. If the impairment and stock-compensation exclusions were rejected, LTM EBITDA would be US${int(e2):,}m and debt-to-EBITDA {plain(l2, 2)}x against {plain(base_lev, 2)}x (US${int(e1):,}m and {plain(l1, 2)}x for stock compensation alone). {{6, 7, 8}}\n\n"
        f"Cash conversion is weak. FY2025 cash from operations was US$1,302m on US$3,624m of Adjusted EBITDA (35.9%), H1 2026 US$675m on US$1,807m (37.4%), and the LTM figure {conv}. Capex, H1 cash interest of US$368m and rent interest still come out of that cash. {{14, 15, 16}}\n\n"
        f"Debt-like items. The balance sheet carries US$13,157m of long-term financing obligations on the VICI and GLPI leases outside reported debt. Adding them once to face debt of US${int(debt_face):,}m gives US${int(adj_debt):,}m, or {plain(adj_lev, 2)}x LTM Adjusted EBITDA against {plain(base_lev, 2)}x on debt alone (the CAOS carrying-value basis gives at least 6.92x). "
        "The FY2025 operating-lease liability (US$742m) and finance-lease liability (US$147m) are shown but not added: June balances are not disclosed and the finance-lease overlap is unreconciled. {17, 18, 19, 20, 22}\n\n"
        "Counterweight and trigger: the reconciliation is transparent, impairment is non-cash and cash flow is positive. That would carry more weight if a component bridge showed the transaction costs were settled one-offs and conversion improved after capex and rent. Watch repeated impairment, stock compensation, conversion below 36% and rising revolver use. "
        "The H1 2026 tax line shows a dash in the 10-Q where CP-1 carries a zero; it is flagged for CP-1 to reconcile. {10}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-1D", text))
    h.gaps(
        "- Transaction-and-other components: no period-by-period split of costs, gains and reserves. Effect: this add-back cannot be accepted or rejected; quality-adjusted EBITDA stays unresolved. Source: a component bridge from the issuer.\n"
        "- June 2026 operating-lease liability: not disclosed (G5). Effect: adjusted debt is a floor. Source: the 10-Q lease note.\n"
        "- Finance leases: overlap with financing obligations not reconciled. Effect: no increment added. Source: the lease note reconciliation.\n"
        "- Agency conventions: no agency adjusted-debt schedule, so no divergence is claimed. Source: current agency reports.\n"
        "- H1 2026 tax bridge: source dash against a stored zero in CP-1. Effect: the H1 bridge is unreconciled. Source: CP-1 owner."
    )
    return h


def cp1_calc(cp1: Handoff, aid: str) -> str:
    """The LTM calc string CP-1 already holds for this add-back (its source_locator)."""
    for r in cp1.rows("cp1.adjusted_ebitda_bridge"):
        if r["addback_id"] == aid and r["period_id"] == "LTM_Q2_2026":
            return r["source_locator"]
    raise KeyError(aid)
