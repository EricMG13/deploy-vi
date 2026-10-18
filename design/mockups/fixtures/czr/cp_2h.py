"""CZR CP-2H: ratings migration and triggers. Issue ratings are real (FINRA); the agency thresholds, outlooks and
current agency-basis leverage are SYNTHETIC (`czr.agency`): the real run found no agency report or trigger (G31).
Projected values are scaled from the Model's PROJECTION where it ran; the cash-interest cover is calculated."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from core import GAP, Ctx, D, Handoff, compute, plain, q
from czr.cp_3 import merger_debt_tail
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]
AG = FACTS["agency"]
TIGHT_X = Decimal("0.5")  # headroom under half a turn is Tight


def _status(headroom: Decimal) -> str:
    return "Breached" if headroom < 0 else "Tight" if headroom < TIGHT_X else "Headroom"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2H",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1A", "MODEL"],
        fixture_file="czr/cp_2h.py",
    )
    h.qa("Restricted")
    cm, c, fig = h.cite_caos, h.cite_data, h.cite_fig

    def m(*n: int) -> str:
        return join_marks(*(cm(FOLDER, "CP-2H", i) for i in n))

    syn = h.cite_synthetic(
        "agency",
        "No agency report is in the pack (G31), so the thresholds and agency-basis leverage are typical of a B1 gaming credit under a pending take-private.",
        "Caesars",
        file="synthetic-facts.json",
    )

    syn_cov = h.cite_synthetic(
        "cover_floor",
        "The 3.0x cash-interest-cover floor is an invented agency threshold typical of a BB- gaming credit, added so a trigger with comfortable headroom is shown.",
        "Caesars",
    )

    # ---- projected values from PROJECTION, where it ran
    mb = ctx.models.get(run_id)
    rows_proj = getattr(mb, "projection_rows", {}) if mb is not None else {}
    scale = proj_cov = None
    c_cov = ""
    if rows_proj.get("DOWNSIDE", {}).get(2027):
        base = mb.snapshot_base_col()
        ltm_lev, _ = compute(
            "LTM total debt / EBITDA",
            "debt / ebitda",
            4,
            "x",
            debt=q(mb.L("total_debt", base).value, 3),
            ebitda=q(mb.L("adjusted_ebitda", base).value, 3),
        )
        d27 = rows_proj["DOWNSIDE"][2027]
        d_lev, _ = compute(
            "FY2027E Downside total debt / EBITDA",
            "debt / ebitda",
            4,
            "x",
            debt=q(d27["total_debt"], 3),
            ebitda=q(d27["ebitda"], 3),
        )
        scale = d_lev / ltm_lev
        proj_cov, c_cov = compute(
            "FY2027E Downside EBITDA / cash interest",
            "ebitda / interest",
            2,
            "x",
            ebitda=q(d27["ebitda"], 3),
            interest=q(d27["cash_interest"], 3),
        )

    def projected(cur: Decimal) -> tuple[str, str]:
        if scale is None:
            return GAP, ""
        v, calc = compute(
            "projected agency-basis leverage", "cur * scale", 1, "x", cur=cur, scale=q(scale, 4)
        )
        return plain(v, 1), calc

    def row(
        agency: str,
        rtype: str,
        metric: str,
        thr: Decimal,
        cur: Decimal,
        cites: str,
        proj: tuple[str, str],
    ) -> dict:
        head, c_h = compute(
            "headroom to the downgrade trigger", "thr - cur", 1, "x", thr=thr, cur=cur
        )
        return {
            "agency": agency,
            "rating_type": rtype,
            "direction": "Ceiling",
            "metric": metric,
            "unit_label": "x",
            "threshold": plain(thr, 1),
            "current_value": plain(cur, 1),
            "projected_value": proj[0],
            "headroom": plain(head, 1),
            "status": _status(head),
            "cite": f"{cites} {proj[1]}".strip(),
        }

    mo, sp = AG["moodys"], AG["sp"]
    mo_thr, mo_cur = D("6.0"), D(mo["current_moodys_leverage_x"])
    sp_thr, sp_cur = D("5.5"), D(sp["current_sp_leverage_x"])
    cov_cur, c_cc = compute(
        "EBITDA / cash interest paid for debt",
        "ebitda / interest",
        2,
        "x",
        ebitda=ctx.val("ltm_adj_ebitda_q2_2026"),
        interest=ctx.val("ltm_cash_interest_debt_q2_2026"),
    )
    cov_thr = D("3.0")
    cov_head, c_ch = compute("headroom", "cur - thr", 2, "x", cur=cov_cur, thr=cov_thr)
    trig = [
        row(
            "Moody's",
            f"Corporate family rating {mo['cfr']}, downgrade",
            "Debt/EBITDA (Moody's adjusted); projected: FY2027E Downside",
            mo_thr,
            mo_cur,
            syn,
            projected(mo_cur),
        ),
        row(
            "S&P",
            f"Issuer credit rating {sp['issuer_rating']}, downgrade",
            "Debt/EBITDA (S&P adjusted); projected: FY2027E Downside",
            sp_thr,
            sp_cur,
            syn,
            projected(sp_cur),
        ),
        {
            "agency": "S&P",
            "rating_type": f"Issuer credit rating {sp['issuer_rating']}, downgrade",
            "direction": "Floor",
            "metric": "EBITDA / cash interest paid for debt (house basis); projected: FY2027E Downside",
            "unit_label": "x",
            "threshold": plain(cov_thr, 1),
            "current_value": plain(cov_cur, 2),
            "projected_value": GAP if proj_cov is None else plain(proj_cov, 2),
            "headroom": plain(cov_head, 2),
            "status": "Headroom"
            if cov_head >= TIGHT_X
            else "Tight"
            if cov_head >= 0
            else "Breached",
            "cite": join_marks(
                fig("ltm_adj_ebitda_q2_2026"), fig("ltm_cash_interest_debt_q2_2026"), syn_cov
            )
            + f" {c_cc} {c_cov}".rstrip(),
        },
    ]
    h.table("cp2h.rating_triggers", trig)

    mig = [
        (
            "Moody's",
            "BASE",
            f"CFR {mo['cfr']} {mo['outlook'].lower()} outlook; unchanged until the terms of the new debt are known",
            "At merger close",
            "Terms and ranking of the committed financing (G8)" + merger_debt_tail(ctx, run_id),
            "Low",
            join_marks(syn, c("C12")),
        ),
        (
            "Moody's",
            "DOWNSIDE",
            f"Downgrade to B2 if Debt/EBITDA passes {plain(mo_thr, 1)}x or the new debt ranks ahead of the unsecured notes",
            "At merger close or on FY2027 results",
            "New debt terms, or a second quarter of Las Vegas margin below 40.3%",
            "Low",
            join_marks(syn, fig("eu_seg_margin_las_vegas_q2_2026")),
        ),
        (
            "S&P",
            "BASE",
            f"Issuer rating {sp['issuer_rating']} stays on CreditWatch negative until financing is disclosed",
            "At merger close",
            "Terms and ranking of the committed financing (G8)" + merger_debt_tail(ctx, run_id),
            "Low",
            join_marks(syn, c("C13")),
        ),
        (
            "S&P",
            "DOWNSIDE",
            f"Downgrade one notch to B+ if Debt/EBITDA passes {plain(sp_thr, 1)}x; the unsecured notes, rated B- by S&P today, are most exposed",
            "On resolution of the CreditWatch, or FY2027 results",
            "Leverage after the merger debt; cash interest cover below 3.0x",
            "Low",
            join_marks(syn, m(9, 10)),
        ),
    ]
    h.table(
        "cp2h.migration_view",
        [
            {
                "agency": a,
                "case": cs,
                "likely_transition": t,
                "earliest_timing": tm,
                "catalyst": ca,
                "confidence": cf,
                "cite": ck,
            }
            for a, cs, t, tm, ca, cf, ck in mig
        ],
    )

    nearest = min(trig[:2], key=lambda r: D(r["headroom"]))
    text = (
        f"The nearest rating trigger is S&P's leverage ceiling: current Debt/EBITDA of {plain(sp_cur, 1)}x against {plain(sp_thr, 1)}x leaves {nearest['headroom']}x of headroom (Tight), with Moody's at {plain(mo_cur, 1)}x against {plain(mo_thr, 1)}x. "
        "Both the thresholds and the agency-basis current values are synthetic test values: the real CAOS run found no agency report, outlook or trigger (G31), so the nearest real trigger was not identifiable. "
        f"On the Downside projection{', scaled from the Model,' if scale is not None else ''} FY2027E leverage "
        f"{'moves to ' + trig[0]['projected_value'] + 'x (Moody' + chr(39) + 's) and ' + trig[1]['projected_value'] + 'x (S&P), above both ceilings' if scale is not None else 'cannot be projected because PROJECTION did not run'}.\n\n"
        "What is real: FINRA shows Moody's B1 and S&P BB- on the 6.50% secured 2032 notes and Caa1 and B- on the 6.00% unsecured 2032 notes. Moody's rating dates are 28 September 2026, while S&P's displayed dates are from 2024 and are stale. "
        "These are issue-level ratings, not issuer ratings or agency actions, and no outlook is shown; the issuer-level B1 and BB- and the outlooks in the register are synthetic. The two agencies' symbols are not averaged or notched against each other. {2, 3, 4, 5, 7, 8, 9, 10}\n\n"
        "The 6.50x net leverage test in the credit agreement is a covenant, not an agency trigger, and the Q2 filing reports compliance without headroom. The synthetic cash-interest-cover floor of 3.0x is for display; "
        f"current cover is {plain(cov_cur, 2)}x on the real LTM figures. {{23, 25}}\n\n"
        "Transmission and challenge. Lower Las Vegas visitation and hold would cut EBITDA while interest, rent and capex stay; with the merger debt of unstated size added, leverage on any agency basis moves toward the ceilings. "
        "The strongest contrary evidence is H1 revenue growth and reported covenant compliance, which would weigh more if later filings show stable EBITDA and falling debt, and if the agencies affirm after the financing is disclosed. {15, 16, 17, 23}\n\n"
        "Migration view. In the Base case ratings hold until the new debt is disclosed; in the Downside a one-notch downgrade is likely at each agency, with the unsecured notes most exposed. Confidence is Low."
    )
    h.analysis(caos_text(h, FOLDER, "CP-2H", text))
    h.gaps(
        "- Agency thresholds, outlooks and issuer ratings: no agency report in the pack (G31, G11); every threshold, outlook and issuer-level rating shown is synthetic. Source: current agency reports and criteria.\n"
        "- Agency-basis leverage: the current values are synthetic; the pack cannot reproduce agency adjustments for leases and debt perimeter. Source: agency adjusted-debt schedules.\n"
        "- Projected values: scaled from the house-basis projection, itself built on synthetic drivers; they show direction, not an agency forecast.\n"
        "- S&P rating dates are 2024, so the S&P issue ratings are stale. Source: a current S&P action."
    )
    return h
