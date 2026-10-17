"""CZR CP-4C: restructuring and fulcrum.

The real outcome: the distress gate is Not met. The real CAOS CP-4C ran as "Not Applicable, no named distress trigger"
on the delivered record: covenant compliance reported at 30 June 2026, positive first-half operating cash flow and
US$2.928bn of liquidity. No claims, EV scenarios, recoveries or paths are constructed. Per the interfaces spec (§2.17)
the four register tables still carry one row each, with `Gate not met` in the critical cells.

`recoveries.recovery_pct` is a critical `_pct` column; the library's table validation lets the four register tables hold
`Gate not met` in critical cells when the distress gate is Not met, so that cell reads `Gate not met` too. The Distressed Front Page hides these tables when the gate is not met, and the Larchmere run shows the full waterfall.
"""

from __future__ import annotations

from decimal import Decimal

from core import GAP, Ctx, D, Handoff, compute
from czr.cp_3 import AS_OF, cite_fact, is_primary, num, tranche_rows
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
GN = "Gate not met"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-4C",
        "CZR",
        run_id,
        AS_OF,
        ["CP-0", "CP-1", "CP-4", "MODEL"],
        fixture_file="czr/cp_4c.py",
    )
    h.qa("Restricted")
    cc = lambda ids: join_marks(*(h.cite_caos(FOLDER, "CP-4C", i) for i in ids))  # noqa: E731
    c = lambda key: join_marks(h.cite_fig(key))  # noqa: E731
    primary = is_primary(ctx, run_id)

    cfr = join_marks(c("trace_czr_12769gad2_moodys"), c("trace_czr_12769gac4_moodys"))
    pf_calc, pf_cite = "", ""
    if primary:
        new_all = sum((D(t["size"]) for t in tranche_rows(ctx, run_id)), Decimal(0))
        pf_lev, pf_calc = compute(
            "pro forma total leverage with the synthetic merger tranches",
            "(debt + new) / ebitda",
            2,
            "x",
            debt=ctx.val("total_debt_check_2026_06_30"),
            new=new_all,
            ebitda=ctx.val("ltm_adj_ebitda_q2_2026"),
        )
        pf_cite = cite_fact(h, "merger_tranches")
    gate = [
        (
            "Market prices debt at distressed levels",
            f"Unsecured 2032s at {num(ctx.val('trace_czr_12769gad2_last_price'))}, yield {num(ctx.val('trace_czr_12769gad2_last_yield'), 2)}%; secured 2032s at {num(ctx.val('trace_czr_12769gac4_last_price'))} {c('trace_czr_12769gad2_last_price')}{c('trace_czr_12769gad2_last_yield')}{c('trace_czr_12769gac4_last_price')}",
            GAP,
            "Not met",
            join_marks(
                c("trace_czr_12769gad2_last_price"),
                c("trace_czr_12769gad2_last_yield"),
                c("trace_czr_12769gac4_last_price"),
            ),
        ),
        (
            "Rating in Caa or below",
            f"The pack has no issuer-level rating (G25). Only the unsecured 2032 notes carry a Caa-category issue rating ({ctx.figure('trace_czr_12769gad2_moodys')['raw']} from Moody's) and the secured 2032s are {ctx.figure('trace_czr_12769gac4_moodys')['raw']}, so the issuer-level trigger is not met {cfr}",
            GAP,
            "Not met",
            cfr,
        ),
        (
            "Liquidity runway under 12 months",
            f"{num(ctx.val('cr_runway_months'), 1)} months of runway on mandatory uses {c('cr_runway_months')}",
            GAP,
            "Not met",
            c("cr_runway_months"),
        ),
        (
            "Maturity within 24 months without a path",
            f"The CEI revolver and Term Loan A mature on 31 January 2028, about 16 months from the analysis date, but the revolver is {num(ctx.val('cr_rcf_util_pct'), 1)}% drawn, liquidity is {num(ctx.val('liq_total'))} and CP-3C finds consensual refinancing credible, so a maturity without a path is not shown {c('cei_rcf_maturity')}{c('cr_rcf_util_pct')}{c('liq_total')}",
            "2028-01-31",
            "Not met",
            join_marks(c("cei_rcf_maturity"), c("cr_rcf_util_pct"), c("liq_total")),
        ),
        (
            "Leverage after the merger debt",
            (
                f"Total leverage is {num(ctx.val('total_leverage_ltm'), 2)}x today {c('total_leverage_ltm')}, and {num(pf_lev, 2)}x pro forma for the synthetic merger tranches {pf_cite}, well below a stress level ({pf_calc})"
                if primary
                else "The merger debt is unstated (G8), so the pro forma leverage cannot be computed"
            ),
            GAP,
            "Not met" if primary else "Unclear",
            join_marks(c("total_leverage_ltm"), pf_cite),
        ),
        (
            "Missed payment, covenant breach or LME announced",
            f"The Q2 10-Q reports compliance with the applicable financial covenants at 30 June 2026 and the sources show no missed payment, failed refinancing, exchange or LME {cc([2])}",
            "2026-06-30",
            "Not met",
            cc([2]),
        ),
        (
            "Overall",
            "No named distress trigger is documented in the sources; the real CAOS CP-4C was Not Applicable on the same evidence",
            GAP,
            "Not met",
            cc([1, 2, 3, 4]),
        ),
    ]
    h.table(
        "cp4c.distress_gate",
        [
            {"trigger": t, "evidence": e, "event_date": d, "status": s, "cite": ci}
            for t, e, d, s, ci in gate
        ],
    )
    base = h.cite_caos(FOLDER, "CP-4C", 1)
    h.table(
        "cp4c.claims_register",
        [
            {
                "class_id": GN,
                "claim": GN,
                "obligor": GN,
                "amount": GN,
                "currency": "USD",
                "unit": "MILLIONS",
                "security": GN,
                "priority_rank": GN,
                "cite": base,
            }
        ],
    )
    h.table(
        "cp4c.ev_scenarios",
        [
            {
                "scenario": GN,
                "valuation_basis": GN,
                "metric_value": GN,
                "multiple_x": GAP,
                "ev": GN,
                "currency": "USD",
                "unit": "MILLIONS",
                "cite": base,
            }
        ],
    )
    h.table(
        "cp4c.recoveries",
        [
            {
                "scenario": GN,
                "class_id": GN,
                "allowed_claim": GN,
                "available_value": GN,
                "allocation": GN,
                "residual": GN,
                "recovery_pct": GN,
                "fulcrum": "No",
                "currency": "USD",
                "unit": "MILLIONS",
                "cite": GAP,
            }
        ],
    )
    h.table(
        "cp4c.paths",
        [
            {
                "path": GN,
                "process": GN,
                "consent": GN,
                "new_money": GN,
                "class_treatment": GN,
                "milestones": GN,
                "blockers": GN,
                "likelihood_class": "Unknown",
                "cite": base,
            }
        ],
    )
    cc2 = lambda s: caos_text(h, FOLDER, "CP-4C", s)  # noqa: E731
    h.analysis(
        "The distress gate is Not met, so no restructuring path, enterprise value, waterfall, fulcrum or recovery is constructed. "
        + cc2(
            "On the supplied record there is no named distress trigger: the Q2 filing reports compliance with the applicable financial covenants {2}, first-half operating cash flow of 675 {3} and cash plus reported borrowing capacity of 2,928 {4}. "
        )
        + "This is the real CAOS CP-4C outcome (Not Applicable), reached at confidence 54 of 100 with QA Restricted.\n\n"
        + cc2(
            "Those dated facts do not prove the company's condition on 2 October: the latest filing covers the quarter ended 30 June {1}, and a missed or likely missed payment, failed refinancing, distressed exchange, covenant or enforcement event, adviser engagement or creditor-group formation is not documented in the sources. The absence of a trigger is not a conclusion that no distress exists outside the delivered source set. "
        )
        + cc2(
            "Management's FY2025 expectation that liquidity and operating cash flow would cover needs for twelve months and beyond {7} is the strongest counterevidence, and it would carry more weight if later filings confirmed liquidity and compliance.\n\n"
        )
        + cc2(
            "Las Vegas revenue declined {5} and the pending merger {6} merit monitoring, but neither satisfies the gate by itself. The FY2025 filing reports 11.9 billion of indebtedness and about 1.4 billion of estimated 2026 lease rent to VICI and GLPI {9}, and the Q2 debt note reports face and book debt as distinct figures {10}; these obligations warrant ongoing credit monitoring, not a recovery estimate.\n\n"
        )
        + "The four register tables carry one row each reading Gate not met, as the interfaces spec requires; the Distressed Front Page does not render them. "
        "What would change this view: a subsequent filing showing a covenant breach, a missed payment, a liquidity runway under twelve months, an LME announcement or a downgrade into Caa at the issuer level. Confidence in this module: Low."
    )
    h.gaps(
        "- Post-June evidence: the latest financials are for 30 June 2026, so the absence of a trigger after that date is not established. Lifted by: Q3 2026 results and current debt, liquidity and covenant updates.\n"
        "- Claims, EV, waterfall, fulcrum and paths are not constructed because the gate is not met (the register rows read Gate not met, including the recovery percentage cell).\n"
        "- Lease claims (GLPI and VICI) are outside reported debt and would need a treatment if the gate were ever met. Lifted by: the master lease terms."
    )
    return h
