"""CZR CP-L10: quick-depth screen (Screening basis).

Real: the two LITE CAOS CP-L10 outputs (`lite-portfolio-screen-2026-10-06`, `lite-screen-with-recovery-2026-10-05`):
the topics, the dispositions (Deepen, Summarize, Gap only), the overall posture MIXED and the structured outcome
FULL_UPGRADE_REQUIRED, with their citations. The credit-view words repeat the illustrative view of the Full run at Low
confidence (the real LITE run assigns none). No value here is synthetic except that view.
"""

from __future__ import annotations

from core import Ctx, Handoff
from czr.cp_3 import AS_OF, merger_debt_tail
from helpers import join_marks

PORT = "lite-portfolio-screen-2026-10-06"
REC = "lite-screen-with-recovery-2026-10-05"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-L10",
        "CZR",
        run_id,
        AS_OF,
        ["CP-0", "CP-1", "CP-1A", "MODEL"],
        fixture_file="czr/cp_l10.py",
    )
    h.qa("Restricted")
    p = lambda *n: join_marks(*(h.cite_caos(PORT, "CP-L10", i) for i in n))  # noqa: E731
    r = lambda *n: join_marks(*(h.cite_caos(REC, "CP-L10", i) for i in n))  # noqa: E731
    syn = h.cite_synthetic(
        "credit_view",
        "The real LITE run assigned no Credit Score, Direction or Sector Outlook, so these words repeat the illustrative view of the Full run at Screening basis.",
        "Caesars",
        file="synthetic-facts.json",
    )
    h.table(
        "snapshot.credit_view",
        [
            {
                "credit_score": "3 - Fair",
                "credit_direction": "Deteriorating",
                "sector_outlook": "Neutral",
                "primary_support": f"Revenue growth and Regional EBITDA growth, positive first-half operating cash flow of 675 and 2,928 of cash and borrowing capacity {r(4, 6, 8)}{p(6)}",
                "primary_downside": f"A Las Vegas Adjusted EBITDA decline with material lease, interest and capex demands on cash, and a merger of unstated financing {r(5, 12, 13, 22)}.{merger_debt_tail(ctx, run_id)}",
                "confidence": "Low",
                "basis": "Screening",
                "cite": join_marks(r(4, 5, 6, 8, 12, 13, 22), p(6), syn),
            }
        ],
    )
    h.table(
        "snapshot.strengths_weaknesses",
        [
            {
                "kind": "Strength",
                "label": "Revenue and Regional growth",
                "text": "Q2 revenue rose 3.0% and Regional Adjusted EBITDA rose 11.2%, partly offsetting Las Vegas.",
                "cite": r(4, 6),
            },
            {
                "kind": "Strength",
                "label": "Reported liquidity",
                "text": "Cash of 965 plus borrowing capacity gave 2,928 at 30 June, and management expects it to fund twelve months and beyond.",
                "cite": join_marks(p(6), r(31)),
            },
            {
                "kind": "Weakness",
                "label": "Adjusted EBITDA down on higher revenue",
                "text": "Q2 Adjusted EBITDA fell to 920 from 955 and the Las Vegas segment fell 12.6%.",
                "cite": join_marks(p(3), r(5)),
            },
            {
                "kind": "Weakness",
                "label": "Heavy fixed claims",
                "text": "Estimated debt service of 425 and lease payments of 687 for the rest of 2026, with 6.0 billion of unhedged variable-rate debt.",
                "cite": r(12, 13, 14, 16),
            },
        ],
    )
    topics = [
        (
            "SOURCE_BASIS",
            "Financial change",
            "Source and basis",
            "High",
            "Partial",
            "Gap only",
            5,
            "The referenced FY2025 10-K and the complete current credit and lease documents are not in the delivered evidence.",
            "CP-1",
            r(2, 30),
        ),
        (
            "EARNINGS_MARGIN_CHANGE",
            "Financial change",
            "Earnings and margin change",
            "High",
            "Sufficient",
            "Deepen",
            3,
            "Q2 revenue rose 3.0% but consolidated Adjusted EBITDA fell; Regional rose and Las Vegas and Digital declined.",
            "CP-1B",
            r(3, 4, 5, 6),
        ),
        (
            "CASH_CONVERSION",
            "Financial change",
            "Cash conversion",
            "High",
            "Partial",
            "Deepen",
            4,
            "Six-month operating cash flow was 675 against 680 and capex was 335 against 453; a normalized series is not established.",
            "CP-1B",
            p(4, 5),
        ),
        (
            "LEVERAGE_COVERAGE",
            "Financial change",
            "Leverage and coverage",
            "High",
            "Partial",
            "Deepen",
            2,
            "Debt and estimated debt service are material; no consistent leverage and coverage trend on one definition is available.",
            "CP-1B",
            r(12, 20),
        ),
        (
            "KPI_COMPARABILITY",
            "Financial change",
            "KPI and comparability quality",
            "Medium",
            "Partial",
            "Summarize",
            11,
            "Adjusted EBITDA is a non-GAAP measure and Windsor affects comparability; its definition should not be assumed to match debt-agreement definitions.",
            "—",
            r(17, 18, 19),
        ),
        (
            "SHAREHOLDER_RETURNS",
            "Financial change",
            "Shareholder returns",
            "Low",
            "Sufficient",
            "Immaterial",
            12,
            "No share repurchases were made in the three and six months ended 30 June 2026, so capital returns are not a creditor issue this period.",
            "—",
            r(23),
        ),
        (
            "LIQUIDITY_MATURITIES",
            "Liquidity",
            "Liquidity and maturities",
            "High",
            "Partial",
            "Gap only",
            1,
            "A current, fully reconciled liquidity and maturity assessment is not available: 2,928 of cash and capacity and 767 of 2028 maturities are stated, but no 12-month bridge.",
            "CP-2D",
            join_marks(p(6), r(20, 31)),
        ),
        (
            "COVENANT_COMPLIANCE",
            "Covenant and refinancing",
            "Covenant compliance and headroom",
            "High",
            "Partial",
            "Deepen",
            6,
            "Compliance with the applicable financial covenants is reported at 30 June 2026; headroom is not.",
            "CP-4",
            join_marks(p(19), r(21)),
        ),
        (
            "CREDITOR_DOCUMENTS",
            "Covenant and refinancing",
            "Creditor documents and capacity",
            "High",
            "Missing",
            "Gap only",
            7,
            "The current credit agreement, security package and intercreditor agreement are absent; no capacity, compliance or recovery conclusion follows.",
            "CP-4",
            r(26, 27, 30),
        ),
        (
            "DISTRESS_GATE",
            "Distress",
            "Distress gate",
            "Medium",
            "Partial",
            "Summarize",
            9,
            "No named distress trigger is documented, but the evidence stops at 30 June 2026.",
            "CP-4C",
            join_marks(p(19, 20), r(21, 31)),
        ),
        (
            "MARKET_LEVELS",
            "Relative value",
            "Market levels and compensation",
            "Medium",
            "Partial",
            "Deepen",
            8,
            "One dated last trade of 93.28 on the secured 2032 notes; no quote, spread or comparable.",
            "CP-3",
            p(10, 11, 12),
        ),
        (
            "PORTFOLIO_FIT",
            "Portfolio",
            "Portfolio fit",
            "Medium",
            "Partial",
            "Deepen",
            10,
            "A fund position snapshot dated 30 June 2026 and the proposed trade exist; current holdings and limits need the Portfolio Context.",
            "CP-6",
            p(13, 14),
        ),
    ]
    h.table(
        "cpl10.screen_topics",
        [
            {
                "topic_id": t,
                "family": f,
                "topic": tp,
                "materiality": m,
                "evidence_status": e,
                "disposition": d,
                "priority_rank": str(rk),
                "summary": s,
                "upgrade_module": u,
                "cite": ci,
            }
            for t, f, tp, m, e, d, rk, s, u, ci in topics
        ],
    )
    items = [
        (
            "OVERALL",
            "MIXED",
            f"Q2 revenue rose 3.0% to 2,993 while Adjusted EBITDA fell to 920, six-month operating cash flow was slightly lower and debt remained substantial {p(1, 3, 4)}",
            "Earnings resilience, leverage and policy changes can affect debt service and refinancing capacity",
            "Track cash conversion, debt service and transaction developments; complete Full work before relying on a directional credit conclusion",
            "Medium",
            p(1, 3, 4),
        ),
        (
            "FINANCIAL_CHANGE",
            "MIXED",
            f"Regional EBITDA rose to 488 from 439 while Las Vegas fell to 410 from 469 {r(5, 6)}",
            "A weaker highest-margin segment cuts cash available after rent and debt service",
            "Primary support is revenue and Regional growth; the primary risk is Las Vegas with material cash obligations",
            "Medium",
            r(5, 6),
        ),
        (
            "LIQUIDITY_FORWARD_RISK",
            "WATCH",
            f"Cash of 965 and 1.9 billion of revolver capacity; 425 of debt service and 687 of lease payments for the rest of 2026; 6.0 billion of unhedged variable-rate debt {r(10, 11, 12, 13, 14, 16)}",
            "Cash generation, rent, maturities and refinancing availability decide the pinch point",
            "Escalate to the Full liquidity, rates and forecast owners before treating the stated outlook as a bridge",
            "Low",
            r(10, 11, 12, 13, 14, 16),
        ),
        (
            "SECURITY_OPPORTUNITY",
            "INSUFFICIENT_INFORMATION",
            f"One FINRA last trade of 93.28 on the secured 2032 notes; no quote, spread, curve or comparable {p(10, 11, 12)}",
            "Compensation cannot be judged without a benchmark and matched comparables",
            "Not a security recommendation; obtain a dated two-sided snapshot",
            "Low",
            p(10, 11, 12),
        ),
        (
            "CREDITOR_DOCUMENTS",
            "INSUFFICIENT_INFORMATION",
            f"The base indenture and two supplements are delivered; the security documents, collateral schedule and intercreditor agreement are not {r(26, 27, 28, 29)}",
            "Capacity, entity coverage and priming risk need the full documents",
            "Obtain and review the operative documents under the Full owners",
            "Low",
            r(26, 27, 28, 29),
        ),
    ]
    h.table(
        "cpl10.screen_items",
        [
            {
                "item": i,
                "assessment": a,
                "evidence": e,
                "transmission": t,
                "implication": im,
                "confidence": c,
                "cite": ck,
            }
            for i, a, e, t, im, c, ck in items
        ],
    )
    triggers = [
        (
            "SOURCE_BASIS",
            "Current position and source perimeter",
            "Determines whether the dated issuer and holding evidence still apply",
            "Current portfolio holdings and the complete underwriting pack",
            "CP-1",
            "Yes",
        ),
        (
            "EARNINGS_MARGIN_CHANGE",
            "Full earnings normalization",
            "Could change the assessment of recurring earnings and margin trend",
            "Filed financial history and applicable debt definitions",
            "CP-1B",
            "Yes",
        ),
        (
            "CASH_CONVERSION",
            "Cash conversion",
            "Affects free cash flow durability and debt-service capacity",
            "Filed cash-flow history and supporting schedules",
            "CP-1B",
            "Yes",
        ),
        (
            "LIQUIDITY_MATURITIES",
            "Material liquidity gap",
            "Required to assess near-term liquidity and refinancing pressure",
            "Current issuer liquidity and debt schedules and facility documents",
            "CP-2D",
            "Yes",
        ),
        (
            "CREDITOR_DOCUMENTS",
            "Capacity and priming",
            "Sizes baskets, leakage and recovery",
            "The current credit agreement, security package and intercreditor agreement",
            "CP-4",
            "Yes",
        ),
        (
            "MARKET_LEVELS",
            "Two-sided pricing",
            "Lets compensation and relative value be judged",
            "A dated bid and ask with size and a benchmark curve",
            "CP-3",
            "No",
        ),
    ]
    h.table(
        "cpl10.upgrade_triggers",
        [
            {
                "topic_id": t,
                "trigger": tr,
                "decision_impact": d,
                "required_source": rs,
                "target_full_module": tm,
                "blocking": b,
            }
            for t, tr, d, rs, tm, b in triggers
        ],
    )
    h.analysis(
        f"The screen is MIXED and a Full upgrade is required: operating and liquidity indicators do not move together, and the evidence is not enough for a full credit or instrument decision. That is the real CAOS LITE outcome (FULL_UPGRADE_REQUIRED) at confidence 59 of 100 with QA Restricted {p(1, 3, 4, 6)}. "
        f"The credit view words shown (Credit Score 3 - Fair, Direction Deteriorating, Sector Outlook Neutral) are the illustrative view carried from the Full run at Screening basis {syn}.\n\n"
        f"Financial change: Q2 revenue rose 3.0% to 2,993 and Adjusted EBITDA fell to 920 from 955; six-month operating cash flow was 675 against 680 and capex 335 against 453 {p(1, 3, 4, 5)}. Regional Adjusted EBITDA rose 11.2% while Las Vegas fell 12.6% {r(5, 6)}. Net revenues and EBITDA are not fully comparable after the Caesars Windsor acquisition {r(17)}.\n\n"
        f"Liquidity and forward risk: cash was 965 and total cash and borrowing capacity 2,928 {p(6)}, against 425 of estimated debt service and 687 of lease payments for the rest of 2026 {r(12, 13)} and 6.0 billion of unhedged variable-rate borrowings {r(14, 16)}. Management expects liquidity and operating cash flow to cover twelve months and beyond {r(31)}, but this is an issuer statement, not a bridge.\n\n"
        f"Security and documents: the only market evidence is one dated last trade of 93.28 on the secured 2032 notes {p(10, 11, 12)}, and the security documents and intercreditor agreement are absent {r(26, 27)}. Both screens are Insufficient Information, not a recommendation. "
        "What would change this view: two-sided quotes, the complete creditor documents, a 12-month liquidity bridge and post-June results. Confidence in this module: Low."
    )
    h.gaps(
        "- Credit view words: the real LITE run assigned no Credit Score, Direction or Sector Outlook; the words are the illustrative view at Low confidence. Lifted by: the Full run.\n"
        "- Liquidity and maturities: no reconciled 12-month bridge. Lifted by: the Full liquidity module (CP-2D).\n"
        "- Creditor documents: the current credit agreement, collateral schedule and intercreditor agreement are not in the pack. Lifted by: those documents.\n"
        "- Market evidence: one last trade, no quote or benchmark. Lifted by: a dated two-sided snapshot and a benchmark curve.\n"
        "- Post-June events: none delivered; the Alberta launch on 13 July 2026 is a flagged subsequent event."
    )
    return h
