"""CZR CP-2E: macro, FX, commodity and hedging sensitivity. Exposures and hedges are the real findings (about US$6.0bn
floating, no derivatives held, CPI-linked rent, no FX detail); sensitivities are calculated from the real balances.
The only synthetic input is the Downside rate deck used for the +50 bps row."""

from __future__ import annotations

import json
from pathlib import Path

from core import Ctx, D, Handoff, compute, plain
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2E",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "MODEL"],
        fixture_file="czr/cp_2e.py",
    )
    h.qa("Restricted")
    cm, fig = h.cite_caos, h.cite_fig

    def m(*n: int) -> str:
        return join_marks(*(cm(FOLDER, "CP-2E", i) for i in n))

    syn = h.cite_synthetic(
        "rate_deck",
        "No forward SOFR curve is in the pack (G30), so the Downside deck is a plausible rise from the Base path.",
        "Caesars",
        file="synthetic-facts.json",
    )
    bank = ctx.val("bank_debt_2026_06_30")
    notes = ctx.val("notes_2026_06_30")
    rent = ctx.val("ltm_cash_interest_rent_q2_2026")
    ex = [
        (
            "Floating-rate bank debt",
            "Rates",
            bank,
            "Unhedged: no derivatives held at 30 June 2026",
            "Higher Term SOFR lifts cash interest on the revolver, Term Loans A, B and B-1 and the CVA delayed draw term loan.",
            "Lower FCF and liquidity; deleveraging slows.",
            join_marks(fig("bank_debt_2026_06_30"), m(8, 9, 10)),
        ),
        (
            "Fixed-rate senior notes",
            "Rates",
            notes,
            "Fixed coupons of 4.625% to 7.00%; not a hedge of the floating debt",
            "No repricing before maturity, but refinancing risk is separate.",
            "Limits rate sensitivity to the floating tranches.",
            join_marks(fig("notes_2026_06_30"), m(6, 7)),
        ),
        (
            "CPI-linked VICI and GLPI rent",
            "Inflation",
            rent,
            "No hedge disclosed",
            "The VICI leases escalate each November with CPI; about US$687m of rent remained for 2026.",
            "Higher fixed cash rent competes with debt service and capex.",
            join_marks(fig("ltm_cash_interest_rent_q2_2026"), m(12, 13)),
        ),
        (
            "Canadian dollar (Caesars Windsor)",
            "FX",
            None,
            "No hedge disclosed",
            "Windsor's operations and lease are in Canada, but revenue, cost and debt currency splits are not disclosed; the translation line was US$(3)m for six months.",
            "Not sized: the sources do not show a material mismatch, and none is inferred.",
            join_marks(m(15), h.cite_data("C301")),
        ),
        (
            "Labour and gaming taxes",
            "Inflation",
            None,
            "No hedge",
            "Q2 Regional margin was flat on higher labour costs and gaming taxes; Digital hit by higher tax rates.",
            "Margin and FCF pressure; no pass-through is quantified.",
            m(19, 20),
        ),
        (
            "Energy and water",
            "Commodity",
            None,
            "No hedge disclosed",
            "The issuer is a large consumer of electricity and water; no spend or pass-through is given.",
            "Potential property-cost pressure; not sized.",
            m(26),
        ),
        (
            "Climate and environmental",
            "Sustainability",
            None,
            "No hedge",
            "Scope 1 and 2 reduction goals and severe-weather risk are disclosed; no funded liability or site-level exposure is quantified.",
            "A watch item for operations and insurance, not a quantified credit cost.",
            m(16, 17, 18, 22),
        ),
    ]
    h.table(
        "cp2e.exposures",
        [
            {
                "exposure": e,
                "kind": k,
                "amount": None if a is None else plain(a),
                "currency": "USD",
                "unit": "MILLIONS",
                "hedge_status": hs,
                "transmission": tr,
                "credit_implication": ci,
                "cite": ck,
            }
            for e, k, a, hs, tr, ci, ck in ex
        ],
    )

    up, c_up = compute("cash interest for +100 bps", "-debt * 100 / 10000", 1, "", debt=bank)
    dn, c_dn = compute("cash interest for -100 bps", "debt * 100 / 10000", 1, "", debt=bank)
    deck_b, deck_d = (
        D(FACTS["rate_deck"]["base"]["FY2026"]),
        D(FACTS["rate_deck"]["downside"]["FY2026"]),
    )
    bps = (deck_d - deck_b) * 100
    dk, c_dk = compute(
        "cash interest for the Downside deck against the Base deck, FY2026",
        "-debt * (down - base) / 100",
        1,
        "",
        debt=bank,
        down=deck_d,
        base=deck_b,
    )
    cpi, c_cpi = compute("cash rent for +1% CPI", "-rent * 1 / 100", 1, "", rent=rent)
    tax, c_tax = compute(
        "gaming tax for +1 percentage point on Digital revenue",
        "-rev * 1 / 100",
        1,
        "",
        rev=ctx.val("opm_seg_rev_caesars_digital_fy2025"),
    )
    sens = [
        (
            "Term SOFR +100 bps",
            "+100 bps on all floating bank debt",
            "Unhedged floating debt x 1.00%",
            up,
            "Calculated",
            join_marks(fig("bank_debt_2026_06_30"), m(9)) + f" {c_up}",
        ),
        (
            "Term SOFR -100 bps",
            "-100 bps on all floating bank debt",
            "Unhedged floating debt x 1.00%",
            dn,
            "Calculated",
            join_marks(fig("bank_debt_2026_06_30"), m(9)) + f" {c_dn}",
        ),
        (
            f"Downside rate deck, FY2026 (+{plain(bps, 0)} bps on Base)",
            "Downside deck 4.80% against Base 4.30%",
            "Floating debt x (Downside less Base deck)",
            dk,
            "Calculated",
            join_marks(fig("bank_debt_2026_06_30"), syn) + f" {c_dk}",
        ),
        (
            "CPI +1% on VICI and GLPI cash rent",
            "+1% on LTM cash interest paid for rent",
            "LTM rent x 1.00%",
            cpi,
            "Calculated",
            join_marks(fig("ltm_cash_interest_rent_q2_2026"), m(13)) + f" {c_cpi}",
        ),
        (
            "Gaming tax +1 percentage point on Digital revenue",
            "+1 pp on FY2025 Caesars Digital revenue of US$1,408m",
            "Digital revenue x 1.00%",
            tax,
            "Calculated",
            join_marks(fig("opm_seg_rev_caesars_digital_fy2025"), m(19)) + f" {c_tax}",
        ),
        (
            "Foreign-currency translation, six months to June 2026",
            "As reported, not a shock",
            "Foreign currency and other, other comprehensive income",
            D(-3),
            "Directional",
            m(15),
        ),
    ]
    h.table(
        "cp2e.sensitivities",
        [
            {
                "sensitivity": s,
                "shock": sh,
                "formula": fo,
                "cash_impact": plain(v, 1),
                "currency": "USD",
                "unit": "MILLIONS",
                "status": st,
                "cite": ck,
            }
            for s, sh, fo, v, st, ck in sens
        ],
    )
    h.table("cp2e.hedges", [])

    pct_float, c_pf = compute(
        "floating share of face debt",
        "bank / total * 100",
        1,
        "%",
        bank=bank,
        total=ctx.val("total_debt_face_2026_06_30"),
    )
    text = (
        f"The exposure that can move cash flow most is floating-rate debt: about US$6.0bn of borrowings, {plain(pct_float, 1)}% of face debt ({c_pf.replace('calc: ', '')}), with no derivatives held at 30 June 2026. "
        f"A +100 bps move in Term SOFR costs about US${plain(abs(up), 0)}m a year in cash interest if balances are unchanged; the issuer's own December 2025 sensitivity was about US$61m. Macro risk is Moderate. {{8, 9, 11}}\n\n"
        "Rate path and downside. Higher base rates first raise interest on the five floating facilities, then cut the operating cash left after rent and capex, then raise revolver use and refinancing sensitivity. "
        f"The synthetic Downside deck (SOFR 4.80% against 4.30% in the Base for FY2026) adds about US${plain(abs(dk), 0)}m. The estimate is annual, not a forecast, and ignores amortisation, covenants and new borrowing. "
        "Contrary evidence: interest expense fell in Q2 on lower debt and lower variable rates, which would continue if rates stay low. {14, 10}\n\n"
        "Other macro channels are directional. VICI rent escalates each November with CPI, on about US$687m of 2026 rent still to pay, which is indexed with no hedge. Labour costs and gaming taxes held the Regional margin flat and cut Digital's. "
        f"A one-point tax rise on Digital revenue would cost about US${plain(abs(tax), 0)}m. Energy and water are significant inputs with no quantified pass-through. {{12, 13, 19, 26}}\n\n"
        f"FX is not sized. Caesars Windsor is leased from the Ontario Lottery and Gaming Corporation {h.cite_data('C301')} and aggregate foreign-currency translation was US$(3)m for six months, but there is no split of revenue, cost, debt or cash by currency, so no mismatch is inferred and none is ruled out. {{15}}\n\n"
        "Credit implication: the unhedged floating exposure is the priority macro factor, and the cash effect is modest against US$3.6bn of Adjusted EBITDA but additive to rent and capex. "
        "Climate and environmental items are Watch only; the company reports no material remediation cost. Monitor Term SOFR, variable balances, cash interest, the November rent reset and state tax changes. {16, 17, 18, 22}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-2E", text))
    h.gaps(
        "- Hedges: none held at 30 June 2026, so the hedge table is empty. Absence at the reporting date does not show later status. Source: the next 10-Q.\n"
        "- Floating balance: the issuer rounds to US$6.0bn; the table uses the debt-table face amounts (US$5,968m). Effect: sensitivities differ by about US$0.3m. Source: instrument-level balances.\n"
        "- FX: no currency-level revenue, cost, debt or cash schedule. Effect: no FX sensitivity can be calculated; the translation row is as reported.\n"
        "- Forward curve: none in the pack (G30); the Downside rate deck is synthetic.\n"
        "- Commodity and labour: no cost base or pass-through, so these exposures are directional only."
    )
    return h
