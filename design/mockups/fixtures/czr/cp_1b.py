"""CZR CP-1B: earnings delta. Entirely real: period comparisons from the base data's cited figures (derived changes
through compute()), 10-Q MD&A drivers, segment margin changes, signals from the real CAOS CP-1B findings.
There is no guidance in the sources (G13), so guidance_vs_delivery is empty."""

from __future__ import annotations

from decimal import Decimal

from core import Ctx, Handoff, compute, plain
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"

# metric_id, label, current key, reference key, current period, reference period, basis, perimeter change
COMPARISONS = [
    (
        "net_revenues_q2",
        "net_revenues_q2_2026",
        "net_revenues_q2_2025",
        "Q2_2026",
        "Q2_2025",
        "YoY",
        "Yes",
    ),
    (
        "adjusted_ebitda_q2",
        "adj_ebitda_q2_2026",
        "adj_ebitda_q2_2025",
        "Q2_2026",
        "Q2_2025",
        "YoY",
        "Yes",
    ),
    (
        "net_revenues_h1",
        "net_revenues_h1_2026",
        "net_revenues_h1_2025",
        "H1_2026",
        "H1_2025",
        "YoY",
        "Yes",
    ),
    (
        "adjusted_ebitda_h1",
        "adj_ebitda_h1_2026",
        "adj_ebitda_h1_2025",
        "H1_2026",
        "H1_2025",
        "YoY",
        "Yes",
    ),
    (
        "net_loss_attributable_q2",
        "net_income_attrib_q2_2026",
        "net_income_attrib_q2_2025",
        "Q2_2026",
        "Q2_2025",
        "YoY",
        "No",
    ),
    (
        "interest_expense_q2",
        "interest_expense_q2_2026",
        "interest_expense_q2_2025",
        "Q2_2026",
        "Q2_2025",
        "YoY",
        "No",
    ),
    ("operating_cash_flow_h1", "cfo_h1_2026", "cfo_h1_2025", "H1_2026", "H1_2025", "YoY", "No"),
    ("capex_h1", "capex_h1_2026", "capex_h1_2025", "H1_2026", "H1_2025", "YoY", "No"),
    (
        "cash_interest_paid_debt_h1",
        "cash_interest_debt_h1_2026",
        "cash_interest_debt_h1_2025",
        "H1_2026",
        "H1_2025",
        "YoY",
        "No",
    ),
    (
        "net_debt",
        "net_debt_calc_2026_06_30",
        "net_debt_calc_2025_12_31",
        "JUN30_2026",
        "FY2025_END",
        "LTM vs FY",
        "No",
    ),
]
OUTFLOW = {"cash_interest_paid_debt_h1": -1}


def _comparisons(ctx: Ctx, h: Handoff) -> list[dict]:
    rows = []
    for mid, ck, rk, cp, rp, basis, perim in COMPARISONS:
        sg = OUTFLOW.get(mid, 1)
        cur, ref = ctx.val(ck) * sg, ctx.val(rk) * sg
        absch, _ = compute("change", "cur - ref", 0, "", cur=cur, ref=ref)
        pct, calc = compute(
            "percentage change",
            "(cur - ref) / absref * 100",
            1,
            "%",
            cur=cur,
            ref=ref,
            absref=abs(ref),
        )
        rows.append(
            {
                "metric_id": mid,
                "current_period_id": cp,
                "reference_period_id": rp,
                "comparison_basis": basis,
                "current_value": plain(cur),
                "reference_value": plain(ref),
                "abs_change": plain(absch),
                "pct_change_pct": f"{plain(pct, 1)}%",
                "currency": "USD",
                "unit": "MILLIONS",
                "restatement": "No",
                "perimeter_change": perim,
                "cite": join_marks(h.cite_fig(ck), h.cite_fig(rk)) + f" {calc}",
            }
        )
    return rows


def _margin(num: Decimal, den: Decimal) -> tuple[Decimal, str]:
    return compute(
        "Adjusted EBITDA margin", "ebitda / revenue * 100", 1, "%", ebitda=num, revenue=den
    )


def _kpis(ctx: Ctx, h: Handoff) -> list[dict]:
    segs = [
        ("las_vegas", "Las Vegas Adjusted EBITDA margin"),
        ("regional", "Regional Adjusted EBITDA margin"),
        ("caesars_digital", "Caesars Digital Adjusted EBITDA margin"),
        ("managed_branded", "Managed and Branded Adjusted EBITDA margin"),
    ]
    rows = []
    for seg, label in segs:
        v = {}
        marks = []
        for yr in ("2026", "2025"):
            e, r = ctx.val(f"seg_adj_ebitda_{seg}_q2_{yr}"), ctx.val(f"seg_rev_{seg}_q2_{yr}")
            v[yr], _ = _margin(e, r)
            marks += [
                h.cite_fig(f"seg_adj_ebitda_{seg}_q2_{yr}"),
                h.cite_fig(f"seg_rev_{seg}_q2_{yr}"),
            ]
        chg, calc = compute(
            "margin change in pp", "cur - ref", 1, "pp", cur=v["2026"], ref=v["2025"]
        )
        rows.append(
            {
                "kpi_id": label,
                "current_value": plain(v["2026"], 1),
                "reference_value": plain(v["2025"], 1),
                "change": plain(chg, 1),
                "unit": "% (change in pp)",
                "trend": "Up" if chg > 0 else "Down" if chg < 0 else "Flat",
                "cite": join_marks(*marks) + f" {calc}",
            }
        )
    cur, _ = _margin(ctx.val("adj_ebitda_q2_2026"), ctx.val("net_revenues_q2_2026"))
    ref, _ = _margin(ctx.val("adj_ebitda_q2_2025"), ctx.val("net_revenues_q2_2025"))
    chg, calc = compute("margin change in pp", "cur - ref", 1, "pp", cur=cur, ref=ref)
    rows.append(
        {
            "kpi_id": "Consolidated Adjusted EBITDA margin",
            "current_value": plain(cur, 1),
            "reference_value": plain(ref, 1),
            "change": plain(chg, 1),
            "unit": "% (change in pp)",
            "trend": "Down",
            "cite": join_marks(
                h.cite_fig("adj_ebitda_q2_2026"),
                h.cite_fig("net_revenues_q2_2026"),
                h.cite_fig("adj_ebitda_q2_2025"),
                h.cite_fig("net_revenues_q2_2025"),
            )
            + f" {calc}",
        }
    )
    return rows


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-1B",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "CP-1A"],
        fixture_file="czr/cp_1b.py",
    )
    h.qa("Restricted")
    c = h.cite_data

    rev_q, _ = compute(
        "revenue change",
        "cur / ref * 100 - 100",
        1,
        "%",
        cur=ctx.val("net_revenues_q2_2026"),
        ref=ctx.val("net_revenues_q2_2025"),
    )
    eb_q, _ = compute(
        "Adjusted EBITDA change",
        "cur / ref * 100 - 100",
        1,
        "%",
        cur=ctx.val("adj_ebitda_q2_2026"),
        ref=ctx.val("adj_ebitda_q2_2025"),
    )
    hist = (
        f"Q2 2026 net revenues rose {plain(rev_q, 1)}% to US$2,993m while Adjusted EBITDA fell {plain(abs(eb_q), 1)}% to US$920m; for six months revenue rose 2.8% and Adjusted EBITDA fell 1.7%. "
        "Regional and Digital (six-month) gains were offset by a weaker Las Vegas, and operating cash flow was nearly flat."
    )
    h.table(
        "snapshot.historical_performance",
        [
            {
                "text": hist,
                "cite": join_marks(c("C19"), c("C20"), c("C23"), c("C24"), c("C49"), c("C50")),
            }
        ],
    )
    h.table("cp1b.period_comparison", _comparisons(ctx, h))

    drivers = [
        (
            "las_vegas_adjusted_ebitda",
            "“declines in net revenues in our Las Vegas segment, attributable to lower table games volume and hold as well as lower city-wide leisure customer visitation”",
            "A major earnings contributor weakened: hold and volume, not price, so the fall is partly reversible, while fixed rent and debt service stay.",
            "Las Vegas is the higher-margin segment, so its decline costs more EBITDA than Regional adds; continued weakness would cut core cash generation.",
            join_marks(c("C366"), h.cite_fig("eu_seg_ebitda_pct_las_vegas")),
        ),
        (
            "regional_adjusted_ebitda",
            "“incremental revenues attributable to the consolidation of Caesars Windsor beginning March 3, 2026”",
            "Benefits are partly perimeter-related and coexist with higher labour and gaming-tax costs; reported growth is not like-for-like.",
            "A positive offset, but not yet evidence of broad organic acceleration.",
            join_marks(c("C365"), h.cite_fig("eu_seg_rev_pct_regional")),
        ),
        (
            "caesars_digital_adjusted_ebitda",
            "“This increase in casino revenues was primarily driven by significant growth in iGaming handle coupled with improved sports betting hold in our Caesars Digital segment.”",
            "Handle growth is not retained net win: Q2 Adjusted EBITDA fell on lower sports hold and higher gaming-tax rates, although the six-month figure rose.",
            "A negative quarterly signal; sustainability of the six-month gain is uncertain.",
            join_marks(c("C364"), h.cite_fig("eu_seg_ebitda_pct_caesars_digital")),
        ),
        (
            "interest_expense",
            "“primarily due to a reduction in outstanding debt and lower variable rate interest expense”",
            "Lower debt and floating rates cut interest in the quarter; the merger's new debt will reverse this.",
            "Supports near-term debt-service capacity; floating exposure remains.",
            join_marks(c("C368"), h.cite_fig("eu_int_pct_q2")),
        ),
        (
            "operating_cash_flow",
            "Management gives no discrete Q2 cash-flow discussion; the six-month statement shows near-flat operating cash flow.",
            "Near-flat cash flow is not cash retained after capex, cash interest and rent; lower capex flatters the proxy.",
            "Neutral to cautious: track cash after maintenance capex, interest and rent.",
            join_marks(c("C49"), c("C50"), h.cite_fig("eu_cfo_pct_h1")),
        ),
    ]
    h.table(
        "cp1b.variance_drivers",
        [
            {
                "metric_id": m,
                "management_driver": md,
                "analyst_driver": ad,
                "credit_implication": ci,
                "cite": ck,
            }
            for m, md, ad, ci, ck in drivers
        ],
    )
    h.table("cp1b.kpi_changes", _kpis(ctx, h))
    h.table("cp1b.guidance_vs_delivery", [])
    sig = [
        (
            "Las Vegas margin compression",
            "Adjusted EBITDA margin 40.3%, down 4.2pp on Q2 2025, on lower table-games hold and visitation.",
            "High",
            "The higher-margin segment is losing earnings faster than Regional adds them.",
            join_marks(
                h.cite_fig("eu_seg_margin_las_vegas_q2_2026"),
                h.cite_fig("eu_seg_margin_chg_las_vegas"),
            ),
        ),
        (
            "Regional growth flattered by the Windsor consolidation",
            "Regional revenue up 9.4% with Caesars Windsor consolidated from 3 March 2026.",
            "Medium",
            "Reported growth overstates the organic trend.",
            join_marks(h.cite_fig("eu_seg_rev_pct_regional"), c("C365")),
        ),
        (
            "Digital revenue up, Adjusted EBITDA down",
            "Digital revenue up 2.3% while Adjusted EBITDA fell 15.0% and margin fell 4.0pp.",
            "Medium",
            "Growth costs more than it earns this quarter.",
            join_marks(
                h.cite_fig("eu_seg_rev_pct_caesars_digital"),
                h.cite_fig("eu_seg_ebitda_pct_caesars_digital"),
                h.cite_fig("eu_seg_margin_chg_caesars_digital"),
            ),
        ),
        (
            "Unsecured 2032s priced for distress",
            "Last trade 84.94 on 1 October 2026, rated Caa1 by Moody's.",
            "High",
            "The market may be pricing unstated merger debt behind the secured notes (G8).",
            join_marks(c("C241"), c("C244")),
        ),
    ]
    h.table(
        "cp1b.signals",
        [
            {"signal": s, "evidence": e, "severity": sv, "credit_implication": ci, "cite": ck}
            for s, e, sv, ci, ck in sig
        ],
    )

    text = (
        "Revenue grew but earnings fell, and the mix is moving the wrong way. Q2 2026 net revenue rose 3.0% to US$2,993m while Adjusted EBITDA fell 3.7% to US$920m; for H1, revenue rose 2.8% to US$5,863m and Adjusted EBITDA fell 1.7% to US$1,807m. "
        "Regional and Digital (six-month) growth was offset by a weaker Las Vegas and by Digital tax and hold pressure. The signal is mixed to negative for earnings durability; it is not a finding of near-term payment default. Confidence is Low (59 of 100). {3, 4}\n\n"
        "Drivers. Las Vegas Adjusted EBITDA fell US$66m (7.3%) in H1 to US$836m on lower table-games volume and hold and weaker visitation, Regional rose US$44m (5.0%) to US$923m partly through Windsor, and Digital rose US$14m to US$137m in H1 although Q2 fell US$12m to US$68m. {14, 15, 16, 18, 19, 25}\n\n"
        "Cash. H1 operating cash flow was US$675m against US$680m, and property purchases US$335m against US$453m, a CFO-less-capex proxy of US$340m that is not free cash flow: H1 cash interest paid for debt was US$368m and cash interest paid for rent US$686m. "
        "At June, cash was US$965m and cash plus available borrowing capacity US$2,928m; the FY2025 filing estimated about US$1.4bn of 2026 VICI and GLPI rent. {5, 6, 9, 11, 12, 23, 32}\n\n"
        "Comparability. Windsor was consolidated from 3 March 2026 and Grand Bazaar bought on 1 May, so reported growth is not wholly organic; no pro forma adjustment is attempted. There is no management guidance, prior case or consensus (G13), so no beat or miss is stated. {26, 27}\n\n"
        "What would change the view: revenue growth, higher Regional and Digital earnings and flat operating cash flow are the counterweights, and they would win if later filings show cash after capex and rent holding up and Las Vegas margin stabilising. The first downside trigger is a second quarter of Las Vegas margin below 40.3%. {14, 5}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-1B", text))
    h.gaps(
        "- Guidance, consensus and prior case: none in the sources (G13), so the guidance table is empty and no beat or miss is stated. Source: a company outlook or a prior RBOT Report.\n"
        "- Quarterly cash flow: cash interest, cash taxes and operating cash flow are disclosed for six months only (G1, G2, G3), so the cash side of the delta is H1. Source: discrete quarterly cash-flow statements.\n"
        "- Post-June results: none delivered; Q2 is not an October estimate. Source: the next 10-Q.\n"
        "- Segment perimeter: no pro forma for Windsor or Grand Bazaar, so Regional growth is reported, not organic."
    )
    return h
