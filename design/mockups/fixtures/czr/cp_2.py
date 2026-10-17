"""CZR CP-2: fundamental credit synthesis. Strengths, weaknesses, drivers and watch items are the real CAOS CP-2
findings ("adequate but cyclical"). The real run never produced a Credit Score, Direction or Sector Outlook (CP-6 did
not run), so those three words are the module's illustrative view, stated as such and cited to a synthetic row."""

from __future__ import annotations

from core import Ctx, Handoff, compute
from czr.cp_3 import is_primary, merger_debt_tail, post_close_leverage
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "CP-1A", "MODEL"],
        fixture_file="czr/cp_2.py",
    )
    h.qa("Restricted")
    cm, c, fig = h.cite_caos, h.cite_data, h.cite_fig

    def m(*n: int) -> str:
        return join_marks(*(cm(FOLDER, "CP-2", i) for i in n))

    syn = h.cite_synthetic(
        "credit_view",
        "The real CAOS run stopped before any Credit Score, Direction or Sector Outlook, so these words are the module's illustrative view, grounded in the cited figures.",
        "Caesars",
    )
    sec_lev = join_marks(fig("senior_leverage_ltm"))
    _, sec_calc = compute(
        "senior secured leverage",
        "debt / ebitda",
        2,
        "x",
        debt=ctx.val("senior_secured_debt_2026_06_30"),
        ebitda=ctx.val("ltm_adj_ebitda_q2_2026"),
    )
    liq = c("C177")
    h.table(
        "snapshot.credit_view",
        [
            {
                "credit_score": "3 - Fair",
                "credit_direction": "Deteriorating",
                "sector_outlook": "Neutral",
                "primary_support": f"Secured leverage of 2.64x LTM Adjusted EBITDA {sec_lev} and US$2,928m of cash and revolver capacity {liq}.",
                "primary_downside": f"Merger debt of unstated size (G8) {c('C213')} on top of falling Las Vegas earnings {m(5)}.{merger_debt_tail(ctx, run_id)}",
                "confidence": "Medium",
                "basis": "Full",
                "cite": join_marks(sec_lev, liq, c("C213"), m(5), syn),
            }
        ],
    )

    sw = [
        (
            "Strength",
            "Broad property and channel footprint",
            "Property, hospitality and digital activities diversify local revenue sources, though all share leisure-demand exposure.",
            m(1, 2),
        ),
        (
            "Strength",
            "Reported liquidity and covenant compliance",
            "US$2,928m of cash and revolver capacity and reported compliance at 30 June give a dated buffer; neither shows covenant headroom.",
            m(12, 16),
        ),
        (
            "Strength",
            "Regional and H1 Digital contribution",
            "Regional Adjusted EBITDA rose US$44m and Digital US$14m in H1, offsetting part of the Las Vegas decline.",
            m(6, 7),
        ),
        (
            "Weakness",
            "Adjusted EBITDA fell despite revenue growth",
            "Q2 revenue rose 3.0% while Adjusted EBITDA fell 3.7%, leaving less cash for debt service, capex and rent.",
            m(3, 4),
        ),
        (
            "Weakness",
            "Substantial debt and lease cash claims",
            "US$11.8bn of debt plus about US$1.4bn of 2026 VICI and GLPI rent consume cash and slow deleveraging.",
            m(9, 13, 14, 15),
        ),
        (
            "Weakness",
            "Cash conversion is unproven after fixed claims",
            "H1 operating cash flow less capex is a US$340m proxy, before cash interest, rent, taxes and principal.",
            m(10, 11, 12),
        ),
        (
            "Weakness",
            "Consumer, competition and hold sensitivity",
            "Weaker demand, hold or higher gaming tax cuts EBITDA while most costs and all rent stay.",
            m(5, 8, 17, 18),
        ),
    ]
    h.table(
        "snapshot.strengths_weaknesses",
        [{"kind": k, "label": lb, "text": t, "cite": ck} for k, lb, t, ck in sw],
    )

    drv = [
        (
            "1",
            "Consolidated EBITDA contraction despite revenue growth",
            "Q2 revenue rose to US$2,993m while Adjusted EBITDA fell to US$920m; H1 EBITDA fell to US$1,807m.",
            "Lower earnings conversion reduces cash after fixed debt and lease claims.",
            "Margin compression weakens debt-service cushion.",
            "Negative",
            "High",
            m(3, 4),
        ),
        (
            "2",
            "Large financing and rent burden",
            "The FY2025 filing estimates about US$1.4bn of 2026 VICI and GLPI rent on top of US$11.9bn of debt.",
            "Fixed payments persist through operating weakness.",
            "Refinancing risk rises; discretionary cash is limited.",
            "Negative",
            "High",
            m(9),
        ),
        (
            "3",
            "Discretionary demand, competition and hold volatility",
            "The company reports intense competition and sensitivity of leisure spending; Las Vegas visitation and Q2 Digital hold and tax pressure are reported.",
            "Lower visitation or hold cuts revenue and EBITDA before costs and rent reset.",
            "Revenue and cash-flow decline risk.",
            "Negative",
            "High",
            m(5, 8, 17, 18),
        ),
        (
            "4",
            "Take-private financing of unstated size",
            "10 banks arranged committed debt for the US$17.6bn deal, but the amount and ranking are not stated (G8)."
            + merger_debt_tail(ctx, run_id),
            "New debt could rank pari passu or ahead of existing creditors and raise leverage.",
            "Post-close leverage and the rank of the unsecured notes are "
            + ("test values only." if is_primary(ctx, run_id) else "unknown."),
            "Negative",
            "Medium",
            join_marks(c("C12"), c("C213"), c("C216")),
        ),
        (
            "5",
            "Variable-rate debt",
            "US$6.1bn of debt had variable rates at 31 December 2025.",
            "Higher reference rates raise cash interest and cut residual cash.",
            "Leverage and interest-cover pressure if rates rise.",
            "Negative",
            "High",
            m(19),
        ),
        (
            "6",
            "H1 revenue growth",
            "H1 revenue rose to US$5,863m from US$5,701m.",
            "Sustained growth can support earnings and liquidity if kept as margin and cash.",
            "A supportive revenue trend, partly from Windsor.",
            "Positive",
            "High",
            m(3),
        ),
        (
            "7",
            "Reported liquidity and covenant compliance",
            "US$2,928m of cash and revolver capacity; covenants reported as complied with at 30 June.",
            "Available liquidity can absorb volatility but is dated and shows no covenant cushion.",
            "A buffer, not headroom.",
            "Positive",
            "Medium",
            m(12, 16),
        ),
    ]
    h.table(
        "cp2.drivers",
        [
            {
                "rank": r,
                "driver": d,
                "evidence": e,
                "risk_mechanism": rm,
                "credit_implication": ci,
                "direction": di,
                "confidence": cf,
                "cite": ck,
            }
            for r, d, e, rm, ci, di, cf, ck in drv
        ],
    )

    watch = [
        (
            "Merger debt terms",
            "Amount and ranking of the committed financing (G8)." + merger_debt_tail(ctx, run_id),
            "Sets post-close leverage and where the unsecured notes rank.",
            "Could move leverage and the rating several notches.",
            join_marks(c("C12"), c("C213")),
        ),
        (
            "Las Vegas margin",
            "Adjusted EBITDA margin below 40.3% for a second quarter.",
            "It would confirm that the Q2 decline is not one quarter's hold.",
            "Further EBITDA and cash-flow erosion in the highest-margin segment.",
            join_marks(fig("eu_seg_margin_las_vegas_q2_2026"), m(5)),
        ),
        (
            "CEI revolver and Term Loan A maturity",
            "Maturity on 31 January 2028 with no extension announced.",
            "The revolver is 72.7% of accessible liquidity.",
            "Refinancing pressure and a liquidity cliff if not extended.",
            join_marks(c("C162"), fig("cr_rcf_share")),
        ),
        (
            "Merger timetable",
            "End Date of 27 May 2027 and ticking fee from 26 June 2027.",
            "Delay raises the cost of the deal and the time the new debt stays undisclosed.",
            "Prolonged uncertainty and transaction costs.",
            join_marks(c("C220"), c("C219")),
        ),
        (
            "Cash conversion",
            "Operating cash flow below capex plus cash interest and rent.",
            "CFO less capex is only a proxy and omits fixed claims.",
            "Rising revolver reliance and weaker refinancing capacity.",
            m(10, 11),
        ),
        (
            "Floating-rate exposure",
            "Term SOFR or variable balances rising.",
            "About US$6.0bn of floating debt is unhedged at 30 June; +100 bps costs about US$60m a year.",
            "Lower FCF and liquidity.",
            join_marks(cm(FOLDER, "CP-2E", 8), cm(FOLDER, "CP-2E", 9)),
        ),
    ]
    h.table(
        "cp2.watch_items",
        [
            {
                "trigger": t,
                "threshold_or_signal": s,
                "why_it_matters": w,
                "credit_impact": ci,
                "cite": ck,
            }
            for t, s, w, ci, ck in watch
        ],
    )

    text = (
        "Caesars is an adequate but cyclical credit: Credit Score 3 - Fair, Credit Direction Deteriorating, Sector Outlook Neutral, at Medium confidence. These three words are the module's illustrative view; the real CAOS run reached the overall view but not the labels. "
        f"A large multi-property, multi-channel footprint and US$2,928m of liquidity support the profile, secured leverage is moderate ({sec_calc}), and the weak point is cash flow after capex, cash interest and rent. {{12, 2}}\n\n"
        "Decision drivers. Support: 52 domestic properties in 18 states with casino, hospitality and digital operations give several sources of activity, though all share leisure-demand risk. Constraint: H1 revenue grew 2.8% to US$5,863m but Adjusted EBITDA fell 1.7% to US$1,807m, with Las Vegas weaker and Q2 Digital hurt by lower sports hold and higher gaming tax. "
        "Fixed claims: the FY2025 filing estimates about US$1.4bn of 2026 VICI and GLPI rent, and undrawn capacity is not cash flow or covenant headroom. {1, 2, 3, 4, 5, 8, 9}\n\n"
        "Financial profile. Carrying debt was US$11,699m (current portion plus long-term debt) against US$11,807m of face principal, with US$13,157m of lease financing obligations kept separate; cash was US$965m. Reported covenant compliance at 30 June is a positive fact, but no headroom is disclosed, so covenant capacity is not calculable. "
        "H1 operating cash flow was US$675m against US$680m, and operating cash flow less capex of US$340m is a proxy that excludes cash interest of US$368m, rent interest of US$686m and principal. {13, 14, 15, 16, 10, 11}\n\n"
        "The merger is the largest open variable. Parent has committed debt financing arranged by 10 banks and the deal is not subject to a financing condition, but the size and ranking of the new debt are unstated (G8)"
        + (
            "; this test run uses three synthetic tranches in its place, and no closing probability is assumed. {22, 21}\n\n"
            if is_primary(ctx, run_id)
            else "; no closing probability or pro forma leverage is assumed. {22, 21}\n\n"
        )
        + "Counterweights and downside. Revenue growth, Regional and Digital earnings, liquidity and covenant compliance would strengthen the view if sustained alongside lower debt and disclosed headroom. The downside path is lower Las Vegas visitation or hold cutting EBITDA and cash while rent and debt service persist, raising revolver reliance and refinancing sensitivity; the nearest hard date is the 31 January 2028 revolver maturity. "
        "Further work needs post-June financials, the current credit agreement and covenant calculations, and the terms of the merger debt. {5, 8, 12, 16, 25}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-2", text))
    h.gaps(
        "- Credit Score, Direction and Sector Outlook: the real run never produced them; the words shown are the module's illustrative view, cited to a synthetic row. Source: a committee-ready run.\n"
        "- Covenant headroom: compliance is reported at 30 June but not calculated (G34). Effect: covenant capacity is not calculable. Source: the compliance certificate and current agreement.\n"
        "- Merger debt: amount and ranking not stated (G8)."
        + merger_debt_tail(ctx, run_id)
        + f" Effect: {post_close_leverage(ctx, run_id)}. Source: the debt commitment letters.\n"
        "- Post-June results: none delivered. Effect: the view rests on June figures. Source: the next 10-Q."
    )
    return h
