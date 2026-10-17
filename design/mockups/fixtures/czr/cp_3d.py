"""CZR CP-3D: market-implied risk.

Real: the four FINRA last trades (CZR 6.50% secured 2032, CZR 6.00% unsecured 2032, MGM 6.125% 2029, PENN 4.125% 2029)
and the 30 June 2026 fund valuation of the secured 2032s (a real, stale observation). Calculated: spreads over a
synthetic Treasury (`czr.spreads`), the implied hazard (credit triangle) and the 3-year discount margins of the
synthetic loan marks (`czr.loan_marks`). Synthetic and marked: the single recovery assumption (40%).

Variant `rv_blocked`: the CP-3D handoff is Blocked, no observation is admitted and every table keeps its columns with
`—` in the critical cells; the gaps explain why.
"""

from __future__ import annotations

from decimal import Decimal

from core import GAP, Ctx, D, Handoff, compute, plain
from czr.cp_3 import (
    AS_OF,
    FOLDER,
    TREASURY,
    Levels,
    cite_fact,
    is_primary,
    num,
    tranche_rows,
)
from helpers import caos_text, join_marks
from run import years_between

NPORT = "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt"
SYNTHETIC = {
    "recovery_assumption_pct": (
        "40",
        "A single 40% recovery is the market convention for senior unsecured credit-default pricing, applied to every security so that the implied hazards rank by spread.",
    ),
}


def _blocked(h: Handoff) -> Handoff:
    """Blocked state: no observation admitted; every table keeps its columns, critical cells are blank."""
    h.qa("Blocked")
    h.table("cp3d.observations", [{}])
    h.table("cp3d.implied_risk", [{}])
    h.table("cp3d.market_vs_fundamental", [{}])
    h.analysis(
        "CP-3D is Blocked: no market observation was admitted, so the market-implied risk cannot be stated. "
        "The module's admission rule needs a dated, sourced quote with a stated quote type for at least one security, and none passed. "
        "Prices, yields, spreads, implied hazards and the alignment of market pricing with fundamentals are therefore blank, not zero. "
        "Downstream modules read an empty market view: the spread curve and the implied default chart have nothing to draw. "
        "What would lift the block: at least one dated observation with a quote type, ideally two-sided quotes with size and a benchmark curve."
    )
    h.gaps(
        "- Market observations: none admitted (design state variant of the Relative Value run, shown to exercise the Blocked state). Effect: every CP-3D table is blank and the spread curve and implied-PD charts are n/a frames. Lifted by: a dated, sourced level for any security.\n"
        "- Implied risk: needs an admitted observation and a benchmark curve (G19). Lifted by: both.\n"
        "- Market against fundamentals: no basis for a comparison without an admitted level. Lifted by: an admitted observation."
    )
    return h


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(ctx, "CP-3D", "CZR", run_id, AS_OF, ["CP-0", "CP-1"], fixture_file="czr/cp_3d.py")
    if variant == "rv_blocked":
        return _blocked(h)
    h.qa("Restricted")
    primary = is_primary(ctx, run_id)
    lv = Levels(ctx, h, run_id)
    rec = D(SYNTHETIC["recovery_assumption_pct"][0])
    rec_c = h.cite_synthetic(
        "recovery_assumption_pct",
        SYNTHETIC["recovery_assumption_pct"][1],
        "Caesars",
        file="czr/cp_3d.py",
    )
    obs: list[dict] = []
    info: dict[str, dict] = {}

    def bond(sid: str, d: dict) -> None:
        info[sid] = d
        obs.append(
            {
                "security_id": sid,
                "price": plain(d["price"]),
                "yield_pct": plain(d["yield"]) + "%",
                "spread_or_dm_bps": plain(d["spread"]),
                "metric_basis": "STW",
                "quote_type": "Trade",
                "maturity_or_call_date": d["maturity"],
                "seniority": d["seniority"],
                "level_date": d["date"],
                "freshness": "Current",
                "cite": join_marks(
                    d["price_cite"],
                    d["yield_cite"],
                    d["date_cite"],
                    d["maturity_cite"],
                    d["coupon_cite"],
                    d["treasury_cite"],
                )
                + " "
                + d["spread_calc"],
            }
        )

    bond("CZR 6.50% secured notes 2032 (CUSIP 12769GAC4)", lv.notes["cei_secured_2032"])
    bond("CZR 6.00% unsecured notes 2032 (CUSIP 12769GAD2)", lv.notes["cei_unsecured_2032"])
    bond("MGM 6.125% senior notes 2029 (CUSIP 552953CK5)", lv.peers["mgm"])
    bond("PENN 4.125% senior notes 2029 (CUSIP 707569AV1)", lv.peers["penn"])
    # the stale fund valuation: real, 30 June 2026
    fund_line = ctx.find_line(NPORT, "6.500%, 2/15/2032 | 536,927")
    fund_c = h.cite_doc(NPORT, fund_line, "6.500%, 2/15/2032 | 536,927")
    par_line = ctx.find_line(
        NPORT, "550,000 | Caesars Entertainment, Inc., Sr. Secd. Note, 144A, 6.500%"
    )
    par_c = h.cite_doc(
        NPORT, par_line, "550,000 | Caesars Entertainment, Inc., Sr. Secd. Note, 144A, 6.500%"
    )
    fund_px, fund_s = compute(
        "secured 2032 fund valuation price", "value / par * 100", 3, value=536927, par=550000
    )
    live = lv.notes["cei_secured_2032"]["price"]
    drop, drop_s = compute(
        "price change from the fund valuation to the last trade",
        "live - fund",
        2,
        live=live,
        fund=fund_px,
    )
    obs.append(
        {
            "security_id": "CZR 6.50% secured notes 2032, fund valuation at 30 June 2026",
            "price": plain(fund_px, 3),
            "yield_pct": GAP,
            "spread_or_dm_bps": GAP,
            "metric_basis": "Price",
            "quote_type": "Evaluated",
            "maturity_or_call_date": lv.notes["cei_secured_2032"]["maturity"],
            "seniority": "Senior secured",
            "level_date": "2026-06-30",
            "freshness": "Stale",
            "cite": join_marks(fund_c, par_c) + " " + fund_s,
        }
    )
    # synthetic loan dealer quotes
    for ln in lv.loans.values():
        sid = ln["name"]
        info[sid] = ln
        obs.append(
            {
                "security_id": sid,
                "price": plain(ln["mid"], 3),
                "yield_pct": plain(ln["yield"], 2) + "%",
                "spread_or_dm_bps": plain(ln["dm"]),
                "metric_basis": "3Y DM",
                "quote_type": "Dealer quote",
                "maturity_or_call_date": ln["maturity"],
                "seniority": "Senior secured",
                "level_date": "2026-10-01",
                "freshness": "Current",
                "cite": join_marks(ln["cite"], ln["sofr_cite"])
                + " "
                + ln["mid_calc"]
                + " "
                + ln["dm_calc"]
                + " "
                + ln["yield_calc"],
            }
        )
    h.table("cp3d.observations", obs)

    # ---- implied risk: credit triangle, annual hazard = spread / (1 - recovery)
    risk: list[dict] = []
    pds: dict[str, Decimal] = {}
    for sid, d in [(k, v) for k, v in info.items() if "spread" in v and "price_cite" in v]:
        pd, pd_s = compute(
            f"{sid} annual hazard",
            "spread / 100 / (1 - rec / 100)",
            1,
            "%",
            spread=d["spread"],
            rec=rec,
        )
        loss, loss_s = compute(
            f"{sid} annual expected loss", "pd * (1 - rec / 100)", 2, "%", pd=pd, rec=rec
        )
        pds[sid] = pd
        risk.append(
            {
                "security_id": sid,
                "model": "Credit triangle: annual hazard = spread / (1 - recovery)",
                "horizon_years": plain(years_between(AS_OF, d["maturity"]), 2),
                "recovery_assumption_pct": plain(rec) + "%",
                "implied_pd_pct": plain(pd, 1) + "%",
                "implied_loss_pct": plain(loss, 2) + "%",
                "break_even_spread_bps": GAP,
                "formula": pd_s,
                "limitation": "Treasury-based spread proxy (synthetic Treasury) and one assumed recovery; a hazard-rate illustration, not a default-probability forecast",
                "cite": join_marks(d["price_cite"], d["yield_cite"], d["treasury_cite"], rec_c)
                + " "
                + d["spread_calc"]
                + " "
                + loss_s,
            }
        )
    h.table("cp3d.implied_risk", risk)

    # ---- market against fundamentals
    ud, ud_s = compute(
        "unsecured less secured last-trade yield",
        "(u - s) * 100",
        4,
        u=lv.notes["cei_unsecured_2032"]["yield"],
        s=lv.notes["cei_secured_2032"]["yield"],
    )
    net_lev = join_marks(h.cite_fig("net_leverage_ltm"))
    sen_lev = join_marks(h.cite_fig("senior_leverage_ltm"))
    pari_m = join_marks(h.cite_fig("cap_pari_secured"))
    ebitda_chg = join_marks(h.cite_fig("eu_ebitda_pct_q2"))
    sec_p, uns_p = lv.notes["cei_secured_2032"], lv.notes["cei_unsecured_2032"]
    if primary:
        new_debt = sum((D(t["size"]) for t in tranche_rows(ctx, run_id)), Decimal(0))
        debt = ctx.val("total_debt_check_2026_06_30")
        pf_lev, pf_s = compute(
            "pro forma total leverage with the synthetic merger tranches",
            "(debt + new) / ebitda",
            2,
            "x",
            debt=debt,
            new=new_debt,
            ebitda=ctx.val("ltm_adj_ebitda_q2_2026"),
        )
        syn_t = cite_fact(h, "merger_tranches")
        new_sec = sum(
            (D(t["size"]) for t in tranche_rows(ctx, run_id) if t["debt_type"] != "SU Notes"),
            Decimal(0),
        )
        first = {
            "implication": f"Unsecured notes priced for stress at {num(uns_p['price'])}, yield {num(uns_p['yield'])}% {uns_p['price_cite']}{uns_p['yield_cite']}",
            "fundamental_evidence": f"Net leverage {num(ctx.val('net_leverage_ltm'), 2)}x today {net_lev}, and {num(pf_lev, 2)}x total leverage pro forma for the synthetic merger tranches {syn_t}",
            "alignment": "Aligned",
            "basis": f"With the three synthetic tranches layered on, total leverage rises from {num(ctx.val('total_leverage_ltm'), 2)}x to {num(pf_lev, 2)}x and the unsecured notes sit behind {num(ctx.val('senior_secured_debt_2026_06_30') + new_sec)} of secured debt",
            "open_question": "Is the unsecured discount the merger debt or the ranking risk? Disclosure of the real terms (G8) decides.",
            "cite": join_marks(
                uns_p["price_cite"],
                uns_p["yield_cite"],
                net_lev,
                syn_t,
                h.cite_fig("total_leverage_ltm"),
            )
            + " "
            + pf_s,
        }
    else:
        first = {
            "implication": f"Unsecured notes priced for stress at {num(uns_p['price'])}, yield {num(uns_p['yield'])}% {uns_p['price_cite']}{uns_p['yield_cite']}",
            "fundamental_evidence": f"Net leverage {num(ctx.val('net_leverage_ltm'), 2)}x before any merger debt {net_lev}",
            "alignment": "Divergent",
            "basis": "The market prices the unstated merger debt (G8); today's leverage alone does not explain a 125 bp yield gap",
            "open_question": "What will the new debt be and where does it rank? (G8)",
            "cite": join_marks(uns_p["price_cite"], uns_p["yield_cite"], net_lev) + " " + ud_s,
        }
    mvf = [
        first,
        {
            "implication": f"Secured notes below par at {num(sec_p['price'])}, yield {num(sec_p['yield'])}% {sec_p['price_cite']}{sec_p['yield_cite']}",
            "fundamental_evidence": f"Senior secured leverage {num(ctx.val('senior_leverage_ltm'), 2)}x {sen_lev}",
            "alignment": "Aligned",
            "basis": f"Yield of {num(sec_p['yield'], 2)}% for a secured claim covered at this leverage",
            "open_question": f"Does pari capacity ({num(ctx.val('cap_pari_secured'))}) dilute the secured claim? {pari_m}",
            "cite": join_marks(sec_p["price_cite"], sec_p["yield_cite"], sen_lev, pari_m),
        },
        {
            "implication": f"The secured 2032s are {num(abs(drop))} points lower than the 30 June fund valuation of {num(fund_px, 2)}",
            "fundamental_evidence": f"Q2 Adjusted EBITDA fell {num(abs(ctx.val('eu_ebitda_pct_q2')), 1)}% year on year {ebitda_chg}, and the merger was announced in the quarter",
            "alignment": "Unclear",
            "basis": "The fund price is an evaluated price at a different date, so the move cannot be attributed",
            "open_question": "How much of the move is the merger and how much Las Vegas?",
            "cite": join_marks(fund_c, par_c, sec_p["price_cite"], ebitda_chg)
            + " "
            + fund_s
            + " "
            + drop_s,
        },
    ]
    h.table("cp3d.market_vs_fundamental", mvf)

    # ---- analysis
    cc = lambda s: caos_text(h, FOLDER, "CP-3D", s)  # noqa: E731
    secid = "CZR 6.50% secured notes 2032 (CUSIP 12769GAC4)"
    unsid = "CZR 6.00% unsecured notes 2032 (CUSIP 12769GAD2)"
    paras = [
        f"The market is pricing Caesars as a stressed-looking high-yield credit, but the signal has low diagnostic precision and no implied default probability should be quoted from it. The October 1 FINRA last trades put the secured 2032s at {num(sec_p['price'])} to yield {num(sec_p['yield'])}% and the unsecured 2032s at {num(uns_p['price'])} to yield {num(uns_p['yield'])}% {sec_p['price_cite']}{sec_p['yield_cite']}{uns_p['price_cite']}{uns_p['yield_cite']}. "
        f"The real CAOS run reached the same conclusion at confidence 44 of 100 {cc('{5,6,13,14,35}')}.",
        f"The unsecured yield is {num(ud, 4)} basis points higher ({ud_s}). That is arithmetic between two last trades, not a credit spread: coupons, maturities and call dates differ, and no trade size or quote was shown {cc('{35}')}. "
        f"MGM's 6.125% 2029s ({num(lv.peers['mgm']['yield'])}%) and PENN's 4.125% 2029s ({num(lv.peers['penn']['yield'])}%) {lv.peers['mgm']['yield_cite']}{lv.peers['penn']['yield_cite']} mature three years earlier and are context only.",
        f"To make the observations comparable the fixture converts each yield to a spread over a synthetic 6-year Treasury of {num(TREASURY, 2)}% {sec_p['treasury_cite']}: {num(sec_p['spread'])} bps for the secured and {num(uns_p['spread'])} bps for the unsecured notes. "
        f"A credit-triangle hazard with a single synthetic recovery of {num(rec)}% {rec_c} gives annual implied hazards of {num(pds[secid], 1)}% and {num(pds[unsid], 1)}%; these rank the securities by spread and are not forecasts. The term loans carry synthetic dealer quotes {lv.loans['cei_term_b']['cite']} and are shown on a 3-year discount margin basis.",
        f"One observation is stale and is kept for what it shows: the fund's 30 June valuation of the secured 2032s was {num(fund_px, 2)} {fund_c}, {num(abs(drop))} points above the October last trade. It is an evaluated price at another date, flagged Stale, and carries no spread.",
        (
            f"Against fundamentals the unsecured discount is Aligned with the pro forma leverage of the synthetic merger tranches, and the secured notes are Aligned with senior secured leverage of {num(ctx.val('senior_leverage_ltm'), 2)}x {sen_lev}. "
            if primary
            else f"Against fundamentals the unsecured discount is Divergent: today's net leverage is {num(ctx.val('net_leverage_ltm'), 2)}x {net_lev}, so the market is pricing something else, most likely the unstated merger debt (G8). "
        )
        + "What would change this view: two-sided executable quotes with size, a benchmark curve, and the disclosed merger financing. Confidence in this module: Low.",
    ]
    h.analysis("\n\n".join(paras))
    h.gaps(
        "- FINRA gives last trades only: no bid, ask, size, benchmark, seniority or intraday time, so the quote type is Trade and the metric basis a spread proxy. Lifted by: two-sided quotes and a benchmark curve.\n"
        "- Benchmark curve: not in the pack (G19). Spreads use a synthetic 6-year Treasury of 4.10%. Lifted by: a Treasury or swap curve at 2 October 2026.\n"
        "- Loan observations are synthetic dealer quotes (G18). Lifted by: loan marks.\n"
        "- Recovery assumption: one synthetic 40% for every security; break-even spreads are blank because no fundamental default probability is supplied. Lifted by: CP-4C recoveries and a fundamental PD.\n"
        "- The 30 June fund valuation is stale (Evaluated, a different date) and is not a pricing input.\n"
        "- Seniority of PENN's notes is not established in the extract."
    )
    return h
