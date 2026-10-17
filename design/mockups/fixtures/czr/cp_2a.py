"""CZR CP-2A: downside pathways. Paths, fragility and triggers are the real CAOS CP-2A findings; probability and impact
words are analyst judgements (the real run left them Unknown). Sensitivities are calculated from the real LTM base and
FY2025 segment EBITDA, with the downside revenue and margin drivers from the synthetic Downside case."""

from __future__ import annotations

import json
from pathlib import Path

from core import Ctx, D, Handoff, compute, plain
from czr.cp_3 import merger_debt_tail
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]
DOWN = FACTS["projection_drivers"]["downside"]


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2A",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "CP-2", "MODEL"],
        fixture_file="czr/cp_2a.py",
    )
    h.qa("Restricted")
    cm, c, fig = h.cite_caos, h.cite_data, h.cite_fig

    def m(*n: int) -> str:
        return join_marks(*(cm(FOLDER, "CP-2A", i) for i in n))

    syn_drv = h.cite_synthetic(
        "projection_drivers",
        "The sources give no guidance (G13), so the Downside case is a plausible Las Vegas downturn with Regional flat.",
        "Caesars",
        file="synthetic-facts.json",
    )
    syn_judge = h.cite_synthetic(
        "path_probabilities",
        "The real run left probability Unknown, so the ordinal probability and impact words are the analyst's illustrative judgement.",
        "Caesars",
    )

    paths = [
        (
            "DP-1",
            "Las Vegas demand, volume and hold",
            "Q2 Las Vegas revenue US$1,017m against US$1,054m and table-games hold 16.6% against 21.1%.",
            "Lower visitation, table drop or hold cuts casino and hotel receipts; labour and property costs lag; less cash after capex, interest and rent.",
            "Slower debt reduction and higher refinancing sensitivity.",
            "Next four quarters",
            "Medium",
            "High",
            "High",
            join_marks(m(17, 18), syn_judge),
        ),
        (
            "DP-2",
            "Gaming taxes and cost rigidity",
            "Gaming tax rates rose in certain states and Q2 Digital Adjusted EBITDA fell 15.0%.",
            "Higher taxes and labour costs outrun revenue, so margin falls faster than revenue.",
            "Weaker FCF durability and less liquidity flexibility.",
            "Next four quarters",
            "Medium",
            "Medium",
            "Medium",
            join_marks(m(19), syn_judge),
        ),
        (
            "DP-3",
            "Capex and lease burden",
            "H1 capex was US$335m, the rest-of-2026 estimate US$310m to US$390m, and 2026 rent about US$1.4bn.",
            "Cash uses persist while receipts soften; the operating-cash proxy of US$340m excludes interest and rent.",
            "Lower optional repayment capacity; liquidity and refinancing sensitivity rise.",
            "2026 to 2027",
            "Medium",
            "High",
            "Medium",
            join_marks(m(5, 6, 11), syn_judge),
        ),
        (
            "DP-4",
            "Floating-rate burden",
            "About US$6.0bn of variable-rate borrowings and no derivatives held.",
            "Higher Term SOFR lifts cash interest and cuts residual cash.",
            "About US$60m a year per +100 bps, slowing deleveraging.",
            "Next 12 months",
            "Medium",
            "Medium",
            "High",
            join_marks(m(10, 20), syn_judge),
        ),
        (
            "DP-5",
            "Revolver and Term A maturity",
            "The CEI revolver and Term Loan A mature on 31 January 2028 and the revolver is 72.7% of accessible liquidity.",
            "If not extended, accessible liquidity falls by the revolver's net capacity while the merger financing is unsettled.",
            "Funding gap of US$138m by the end of 2028 before any refinancing.",
            "2027 to 2028",
            "Medium",
            "High",
            "Medium",
            join_marks(c("C162"), fig("cr_rcf_share"), fig("cr_gap_2028"), syn_judge),
        ),
        (
            "DP-6",
            "Layered take-private",
            "New committed debt of unstated size (G8) arrives at close on top of US$11.9bn of assumed debt."
            + merger_debt_tail(ctx, run_id),
            "New debt ranking pari passu or ahead dilutes existing secured and unsecured creditors and raises leverage.",
            "Unsecured recovery falls to 72.9% in the illustrative downside waterfall.",
            "At close",
            "Medium",
            "High",
            "Low",
            join_marks(c("C12"), c("C213"), fig("dr_rec_downside_unsecured"), syn_judge),
        ),
        (
            "DP-7",
            "Covenant inflection",
            "Compliance is reported at 30 June but no headroom or current definitions are disclosed.",
            "Falling EBITDA and cash would narrow the maintenance-test cushion on the revolver and Term A.",
            "Restricted flexibility; a monitoring item, not an asserted breach.",
            "Beyond 12 months",
            "Low",
            "High",
            "Low",
            join_marks(m(13), syn_judge),
        ),
        (
            "DP-8",
            "Merger delay and ticking fee",
            "End Date of 27 May 2027 with extensions to August and November, and a ticking fee from 26 June 2027.",
            "Approval delay prolongs uncertainty and adds transaction cost; the fee adds to the price Parent pays.",
            "Management distraction and added cash cost; no failure probability is inferred.",
            "2027",
            "Medium",
            "Low",
            "Medium",
            join_marks(m(14, 15), c("C219"), syn_judge),
        ),
    ]
    h.table(
        "cp2a.downside_paths",
        [
            {
                "path_id": pid,
                "driver": d,
                "first_break": fb,
                "transmission": tr,
                "consequence": co,
                "time_horizon": th,
                "probability": pr,
                "impact": im,
                "confidence": cf,
                "cite": ck,
            }
            for pid, d, fb, tr, co, th, pr, im, cf, ck in paths
        ],
    )

    # ---- sensitivities
    ltm_rev, ltm_ebitda = ctx.val("ltm_net_revenues_q2_2026"), ctx.val("ltm_adj_ebitda_q2_2026")
    g_down, m_down = (
        D(DOWN["revenue_growth_pct"]["FY2026"]),
        D(DOWN["adjusted_ebitda_margin_pct"]["FY2026"]),
    )
    ltm_marks = join_marks(fig("ltm_net_revenues_q2_2026"), fig("ltm_adj_ebitda_q2_2026"))
    s_rev, c_rev = compute(
        "EBITDA effect of revenue at the LTM margin",
        "ebitda * g / 100",
        1,
        "",
        ebitda=ltm_ebitda,
        g=g_down,
    )
    s_mar, c_mar = compute(
        "EBITDA effect of the Downside margin on LTM revenue",
        "rev * (m - ebitda / rev * 100) / 100",
        1,
        "",
        rev=ltm_rev,
        m=m_down,
        ebitda=ltm_ebitda,
    )
    e_down, c_ed = compute(
        "FY2026 Downside EBITDA less LTM",
        "rev * (1 + g / 100) * m / 100 - ebitda",
        1,
        "",
        rev=ltm_rev,
        g=g_down,
        m=m_down,
        ebitda=ltm_ebitda,
    )
    lv_ebitda = ctx.val("opm_seg_ebitda_las_vegas_fy2025")
    lv_pct = ctx.val("eu_seg_ebitda_pct_las_vegas")
    s_lv, c_lv = compute(
        "Las Vegas EBITDA at the Q2 rate of decline",
        "ebitda * pct / 100",
        1,
        "",
        ebitda=lv_ebitda,
        pct=lv_pct,
    )
    dg_ebitda = ctx.val("opm_seg_ebitda_caesars_digital_fy2025")
    dg_pct = ctx.val("eu_seg_ebitda_pct_caesars_digital")
    s_dg, c_dg = compute(
        "Digital EBITDA at the Q2 rate of decline",
        "ebitda * pct / 100",
        1,
        "",
        ebitda=dg_ebitda,
        pct=dg_pct,
    )
    bank = ctx.val("bank_debt_2026_06_30")
    s_rate, c_rate = compute(
        "cash interest on bank debt for +100 bps", "-debt * 1 / 100", 1, "", debt=bank
    )
    rent = ctx.val("ltm_cash_interest_rent_q2_2026")
    s_rent, c_rent = compute(
        "cash rent for +1% CPI escalation", "-rent * 1 / 100", 1, "", rent=rent
    )
    sens = [
        (
            "FY2026 Downside case (revenue -3.0%, margin 29.0%)",
            "LTM revenue and Adjusted EBITDA; synthetic Downside drivers",
            "Downside EBITDA less LTM Adjusted EBITDA",
            e_down,
            "US$ m, annual EBITDA",
            "Both drivers together; the FY2026E Downside projection reproduces this EBITDA.",
            join_marks(ltm_marks, syn_drv) + f" {c_ed}",
        ),
        (
            "Margin to the Downside level",
            "LTM revenue; Downside margin of 29.0%",
            "Revenue x (Downside margin less LTM margin)",
            s_mar,
            "US$ m, annual EBITDA",
            "The margin fall alone costs more than the revenue fall.",
            join_marks(ltm_marks, syn_drv) + f" {c_mar}",
        ),
        (
            "Las Vegas EBITDA falls at the Q2 rate (-12.6%)",
            "FY2025 Las Vegas Adjusted EBITDA of US$1,728m",
            "FY2025 segment EBITDA x Q2 rate of decline",
            s_lv,
            "US$ m, annual EBITDA",
            "The largest single-segment exposure; the Q2 decline repeated for a year.",
            join_marks(fig("opm_seg_ebitda_las_vegas_fy2025"), fig("eu_seg_ebitda_pct_las_vegas"))
            + f" {c_lv}",
        ),
        (
            "Revenue falls 3.0% at the LTM margin",
            "LTM Adjusted EBITDA; Downside revenue driver",
            "LTM EBITDA x revenue change",
            s_rev,
            "US$ m, annual EBITDA",
            "Smaller than the margin effect because costs fall with revenue.",
            join_marks(ltm_marks, syn_drv) + f" {c_rev}",
        ),
        (
            "+100 bps Term SOFR on bank debt",
            "US$5,968m of bank debt, all floating, no derivatives",
            "Bank debt x 1.00%",
            s_rate,
            "US$ m, annual cash interest",
            "Issuer's own December 2025 sensitivity was about US$61m.",
            join_marks(fig("bank_debt_2026_06_30"), m(10)) + f" {c_rate}",
        ),
        (
            "Digital EBITDA falls at the Q2 rate (-15.0%)",
            "FY2025 Caesars Digital Adjusted EBITDA of US$236m",
            "FY2025 segment EBITDA x Q2 rate of decline",
            s_dg,
            "US$ m, annual EBITDA",
            "Small against the group, but Digital is the fastest-growing segment.",
            join_marks(
                fig("opm_seg_ebitda_caesars_digital_fy2025"),
                fig("eu_seg_ebitda_pct_caesars_digital"),
            )
            + f" {c_dg}",
        ),
        (
            "+1% CPI escalation on VICI and GLPI cash rent",
            "LTM cash interest paid for rent of US$1,363m",
            "LTM rent x 1.00%",
            s_rent,
            "US$ m, annual cash rent",
            "Rent is indexed to CPI; a small percentage on a large fixed claim.",
            join_marks(fig("ltm_cash_interest_rent_q2_2026")) + f" {c_rent}",
        ),
    ]
    h.table(
        "cp2a.sensitivities",
        [
            {
                "sensitivity": s,
                "input_basis": ib,
                "method": me,
                "result": plain(r, 1),
                "unit_label": ul,
                "interpretation": it,
                "status": "Calculated",
                "cite": ck,
            }
            for s, ib, me, r, ul, it, ck in sens
        ],
    )

    trig = [
        (
            "TR-1",
            "Las Vegas Adjusted EBITDA margin",
            "Leading",
            "Below 40.3% (the Q2 2026 level) for a second quarter, or table-games hold below 16.6%",
            "DP-1",
            "Reassess operating cash conversion, liquidity and refinancing sensitivity.",
            join_marks(fig("eu_seg_margin_las_vegas_q2_2026"), m(18)),
        ),
        (
            "TR-2",
            "Gaming tax and labour cost trend",
            "Leading",
            "A new state tax-rate rise, or Adjusted EBITDA falling while revenue grows for a third quarter",
            "DP-2",
            "Refresh margin and cash conversion; recompute debt-service sensitivity.",
            m(19),
        ),
        (
            "TR-3",
            "Operating cash flow after capex, cash interest and rent",
            "Leading",
            "Operating cash flow below capex plus cash interest and rent for a half-year",
            "DP-3",
            "Escalate the liquidity review; obtain a current cash and debt schedule.",
            m(5, 11),
        ),
        (
            "TR-4",
            "Term SOFR and floating balances",
            "Leading",
            "Term SOFR above 4.80%, the Downside deck level for FY2026",
            "DP-4",
            "Recompute cash interest on updated debt and rates.",
            join_marks(m(10, 20), syn_drv),
        ),
        (
            "TR-5",
            "CEI revolver use and availability",
            "Leading",
            "Revolver use above 25% of commitments, the maintenance-test condition",
            "DP-5",
            "Extension talks become urgent; liquidity is falling toward the 2028 maturity.",
            join_marks(c("C341"), c("C162")),
        ),
        (
            "TR-6",
            "Merger financing disclosure",
            "Leading",
            "Disclosure of new debt above US$5.0bn, or ranking ahead of the unsecured notes",
            "DP-6",
            "Refresh leverage, rank and recovery waterfall.",
            join_marks(c("C12"), c("C213")),
        ),
        (
            "TR-7",
            "Reported covenant calculation",
            "Lagging",
            "Any waiver, testing-condition trigger or reported headroom below 1.0x on the 6.50x test",
            "DP-7",
            "Refer for covenant and legal review; do not infer breach from operations alone.",
            join_marks(c("C338"), m(13)),
        ),
        (
            "TR-8",
            "Merger milestones",
            "Leading",
            "Closing not achieved by 26 June 2027, the ticking-fee date",
            "DP-8",
            "Refresh transaction cost and permitted-action review.",
            join_marks(c("C219"), m(14, 15)),
        ),
    ]
    h.table(
        "cp2a.triggers",
        [
            {
                "trigger_id": t,
                "indicator": i,
                "lead_lag": ll,
                "threshold": th,
                "linked_path": lp,
                "consequence": co,
                "cite": ck,
            }
            for t, i, ll, th, lp, co, ck in trig
        ],
    )

    base_lev, _ = compute(
        "debt / ebitda",
        "debt / ebitda",
        2,
        "x",
        debt=ctx.val("total_debt_face_2026_06_30"),
        ebitda=ltm_ebitda,
    )
    ebitda_after, _ = compute(
        "FY2026 Downside EBITDA",
        "rev * (1 + g / 100) * m / 100",
        0,
        "",
        rev=ltm_rev,
        g=g_down,
        m=m_down,
    )
    down_lev, c_dl = compute(
        "debt / Downside EBITDA",
        "debt / ebitda",
        2,
        "x",
        debt=ctx.val("total_debt_face_2026_06_30"),
        ebitda=ebitda_after,
    )
    text = (
        "What breaks first is Las Vegas: the Q2 filing shows lower segment revenue and table-games hold of 16.6% against 21.1%, and lower gaming and hotel receipts would cut cash while debt service, rent and capex stay. "
        "That transmits to slower deleveraging and higher refinancing sensitivity; it is not a forecast of covenant breach. Confidence in the path is High, in its size Low. {17, 18}\n\n"
        f"Size of the stress. In the synthetic Downside case (FY2026 revenue -3.0% and margin 29.0%, test drivers) EBITDA would be US${int(ebitda_after):,}m, US${plain(abs(e_down), 1)}m below the LTM figure, taking debt to EBITDA from {plain(base_lev, 2)}x to {plain(down_lev, 2)}x on face debt. "
        f"The margin fall costs more than the revenue fall, and a repeat of the Q2 Las Vegas decline over a year would cost about US${plain(abs(s_lv), 1)}m. A +100 bps move in Term SOFR on US$5,968m of bank debt adds about US${plain(abs(s_rate), 1)}m of cash interest, in line with the issuer's own December 2025 estimate of about US$61m. {{3, 4, 10, 20}}\n\n"
        "Fixed claims frame everything: US$11.9bn of debt at December 2025, about US$1.4bn of 2026 VICI and GLPI rent, US$425m of debt service and US$687m of rent for the rest of 2026, and capex of US$310m to US$390m. Cash plus borrowing capacity was US$2,928m at 30 June. These are dated resources and requirements, not a runway. {6, 7, 8, 9, 11}\n\n"
        "Contrary evidence: H1 revenue grew 2.8%, operating cash flow was US$675m, liquidity was US$2,928m and covenants were reported complied with. The downside weakens if later filings show cash after capex and rent holding, stable Las Vegas indicators and falling debt. No post-June financials or covenant calculation exist in the pack. {3, 5, 7, 13}\n\n"
        "Catalysts are mostly the merger's dates: End Date 27 May 2027, ticking fee from 26 June 2027, extensions to 27 August and 27 November 2027, and the 31 January 2028 revolver and Term A maturity. Probability and impact words in the paths are the analyst's illustrative judgement. {14, 15, 22}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-2A", text))
    h.gaps(
        "- Probability and impact: the real run left both Unknown; the words in the paths are illustrative judgements, cited to a synthetic row. Source: an agreed scoring basis.\n"
        "- Trigger thresholds: the real run gave none; each is an analyst-set level anchored on a reported figure (the Q2 margin, the Testing Condition, the Downside rate deck), not an issuer or agency level.\n"
        "- Downside drivers: no guidance or stress case in the sources (G13), so the revenue and margin shocks are synthetic test drivers. Effect: the combined stress is illustrative. Source: a management or agency stress case.\n"
        "- Covenant headroom and definitions: not disclosed (G34). Effect: no covenant sensitivity can be calculated. Source: the compliance certificate.\n"
        "- Recovery and collateral: complete collateral and intercreditor papers absent. Effect: no recovery sensitivity. Source: the security documents."
    )
    return h
