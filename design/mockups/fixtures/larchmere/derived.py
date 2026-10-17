"""Figures derived from the Larchmere inputs in facts.py, computed once with the lib's Decimal helpers.

Every function returns Decimals (and the 'calc:' string where a table cell needs one), so the modules and the tests
share one definition of LTM, covenant EBITDA, forward interest, enterprise value and the recovery waterfall.
"""

from __future__ import annotations

from decimal import Decimal
from functools import lru_cache

from core import D, compute, plain, q

from . import facts as F

ADDBACKS = [
    (
        "restructuring_costs",
        "Restructuring and advisory costs",
        "TRANSACTION_COSTS",
        "addback_restructuring",
        "REALIZED",
    ),
    ("sponsor_fee", "Sponsor monitoring fee", "OTHER_EXPLICIT", "addback_sponsor_fee", "REALIZED"),
    (
        "run_rate_savings",
        "Run-rate cost savings",
        "OTHER_EXPLICIT",
        "addback_run_rate_savings",
        "NOT_STATED",
    ),
]
PERIOD_TAG = {
    "FY2023": "FY2023",
    "FY2024": "FY2024",
    "FY2025": "FY2025",
    "H1_2025": "H1_2025",
    "H1_2026": "H1_2026",
}


def ltm(key: str, places: int = 0, label: str | None = None) -> tuple[Decimal, str]:
    """FY2025 + H1 2026 - H1 2025 of a flow series."""
    s = F.val(key)
    return compute(
        label or f"LTM {key.replace('_', ' ')}",
        "fy + h1 - ph1",
        places,
        "",
        fy=s["FY2025"],
        h1=s["H1_2026"],
        ph1=s["H1_2025"],
    )


def flow(key: str, period: str) -> Decimal:
    return D(F.val(key)[period]) if period != "LTM_Q2_2026" else ltm(key)[0]


def addback_total(period: str) -> Decimal:
    return sum((flow(k, period) for _, _, _, k, _ in ADDBACKS), Decimal(0))


def reported_ebitda(period: str) -> Decimal:
    return flow("adjusted_ebitda", period) - addback_total(period)


def ebit(period: str) -> Decimal:
    return reported_ebitda(period) - flow("d_and_a", period)


def total_debt(bp: str) -> Decimal:
    return D(F.val("rcf_drawn")[bp]) + sum(
        (D(v) for v in F.val("term_debt_face").values()), Decimal(0)
    )


def facility_balance(fid: str, bp: str) -> Decimal:
    return D(F.val("rcf_drawn")[bp]) if fid == "llg_rcf" else D(F.val("term_debt_face")[fid])


def cash(bp: str) -> Decimal:
    return D(F.val("cash_balance")[bp])


def liquidity(bp: str) -> Decimal:
    return cash(bp) + D(F.val("undrawn_rcf")[bp])


def segment_ltm(sid: str) -> Decimal:
    v = F.val("segment_revenue")[sid][2]
    return D(v[2]) + D(v[4]) - D(v[3])


@lru_cache(maxsize=1)
def covenant() -> dict:
    """Last-test covenant figures: covenant EBITDA (stated Adjusted EBITDA less cash rent), net first-lien leverage, cure."""
    adj, adj_s = ltm("adjusted_ebitda")
    rent, rent_s = ltm("lease_cash")
    cov_ebitda, cov_s = compute("covenant EBITDA", "adj - rent", 0, "", adj=adj, rent=rent)
    fl = facility_balance("llg_rcf", "JUN30_2026") + facility_balance("llg_tlb", "JUN30_2026")
    cash_ = cash("JUN30_2026")
    net_fl, net_s = compute(
        "first-lien net debt",
        "rcf + tlb - cash",
        0,
        "",
        rcf=facility_balance("llg_rcf", "JUN30_2026"),
        tlb=facility_balance("llg_tlb", "JUN30_2026"),
        cash=cash_,
    )
    lev, lev_s = compute(
        "first-lien net leverage", "net / ebitda", 2, "x", net=net_fl, ebitda=cov_ebitda
    )
    thr = D(F.val("covenants")["fl_threshold"])
    head, head_s = compute("headroom", "threshold - current", 2, "x", threshold=thr, current=lev)
    cure_ebitda, cure_s = compute(
        "EBITDA cure",
        "net / threshold - ebitda",
        1,
        "",
        net=net_fl,
        threshold=thr,
        ebitda=cov_ebitda,
    )
    liq = liquidity("JUN30_2026")
    floor = D(F.val("covenants")["min_liquidity"])
    liq_head, liq_s = compute(
        "liquidity headroom", "liquidity - floor", 0, "", liquidity=liq, floor=floor
    )
    min_e = D(F.val("covenants")["min_ebitda"])
    e_head, e_s = compute(
        "EBITDA headroom", "ebitda - floor", 0, "", ebitda=cov_ebitda, floor=min_e
    )
    return dict(
        adj=adj,
        adj_s=adj_s,
        rent=rent,
        rent_s=rent_s,
        cov_ebitda=cov_ebitda,
        cov_s=cov_s,
        first_lien=fl,
        net_fl=net_fl,
        net_s=net_s,
        lev=lev,
        lev_s=lev_s,
        thr=thr,
        head=head,
        head_s=head_s,
        cure=cure_ebitda,
        cure_s=cure_s,
        liq=liq,
        floor=floor,
        liq_head=liq_head,
        liq_s=liq_s,
        min_e=min_e,
        e_head=e_head,
        e_s=e_s,
    )


def ssim_ltm() -> Decimal:
    """Adjusted EBITDA on the house (SSIM) basis: stated less the unrealized run-rate savings."""
    return ltm("adjusted_ebitda")[0] - ltm("addback_run_rate_savings")[0]


def enterprise_values() -> dict[str, tuple[Decimal, Decimal, Decimal, str]]:
    """scenario -> (metric, multiple, EV, calc string): the EBITDA and multiple, or the asset value and a zero multiple (liquidation)."""
    m = ssim_ltm()
    out = {}
    for k, label in (
        ("low", "Going concern: low"),
        ("base", "Going concern: base"),
        ("high", "Going concern: high"),
    ):
        x = D(F.val("ev_multiples")[k])
        ev, s = compute(f"EV {k}", "ebitda * multiple", 1, "", ebitda=m, multiple=x)
        out[label] = (m, x, ev, s)
    liq = F.val("liquidation")
    ev, s = compute(
        "liquidation value",
        "assets * (100 - haircut) / 100",
        1,
        "",
        assets=liq["asset_value"],
        haircut=liq["haircut_pct"],
    )
    out["Liquidation"] = (D(liq["asset_value"]), Decimal(0), ev, s)
    return out


CLASSES = [
    ("C1-ADMIN", "Administrative and priority claims"),
    ("C2-1L", "First-lien claims (revolver and term loan B)"),
    ("C3-2L", "Second-lien term loan"),
    ("C4-NOTES", "Senior unsecured notes"),
    ("C5-TRADE", "Trade and other unsecured claims"),
]


def claims() -> dict[str, Decimal]:
    c = F.val("claims_other")
    return {
        "C1-ADMIN": D(c["admin"]),
        "C2-1L": facility_balance("llg_rcf", "JUN30_2026")
        + facility_balance("llg_tlb", "JUN30_2026"),
        "C3-2L": facility_balance("llg_2l", "JUN30_2026"),
        "C4-NOTES": facility_balance("llg_notes", "JUN30_2026"),
        "C5-TRADE": D(c["trade"]),
    }


def waterfall(ev: Decimal, extra_senior: Decimal = Decimal(0)) -> list[dict]:
    """Class rows for one scenario: available value, allocation, residual, recovery, fulcrum flag (all Decimal)."""
    avail = ev - extra_senior
    rows = []
    fulcrum_done = False
    for cid, _ in CLASSES:
        claim = claims()[cid]
        alloc = min(avail, claim) if avail > 0 else Decimal(0)
        resid = avail - alloc
        is_f = (not fulcrum_done) and alloc < claim
        fulcrum_done = fulcrum_done or is_f
        rows.append(
            dict(
                class_id=cid,
                claim=claim,
                available=max(avail, Decimal(0)),
                allocation=alloc,
                residual=max(resid, Decimal(0)),
                pct=alloc / claim * 100,
                fulcrum=is_f,
            )
        )
        avail = resid if resid > 0 else Decimal(0)
    return rows


def forward_interest(case: str = "BASE") -> tuple[Decimal, str]:
    """12-month cash interest on June 2026 balances at the first deck rate: sum of balance x rate per facility."""
    sofr = D(F.val("rate_deck")[case][0])
    names: dict[str, Decimal] = {}
    terms = []
    for i, fid in enumerate(F.FACILITY_IDS, 1):
        t = F.val("facility_terms")[fid]
        rate = (
            D(t["fixed"]) if "fixed" in t else max(sofr, D(t["floor"]) / 100) + D(t["spread"]) / 100
        )
        names[f"b{i}"], names[f"r{i}"] = facility_balance(fid, "JUN30_2026"), rate
        terms.append(f"b{i} * r{i} / 100")
    return compute(
        f"forward cash interest at SOFR {plain(sofr)}%", " + ".join(terms), 1, "", **names
    )


def fmt(d: Decimal, places: int | None = None) -> str:
    return plain(d, places)


def market() -> dict[str, dict]:
    """Per-security market figures at 2026-10-01: price, DM or YTM/STW, credit-triangle hazard, 3-year PD and loss (Decimals)."""
    from run import years_between

    out: dict[str, dict] = {}
    quotes = F.val("quotes")
    rec = F.val("recoveries_market")
    rf = D(F.val("risk_free_3y"))
    for fid in ("llg_tlb", "llg_2l", "llg_notes"):
        t = F.val("facility_terms")[fid]
        price = D(quotes[fid])
        r = dict(price=price, recovery=D(rec[fid]))
        if fid == "llg_notes":
            n = years_between("2026-10-01", t["maturity"])
            ytm, ytm_s = compute(
                "approximate yield to maturity",
                "(coupon + (100 - price) / n) / ((100 + price) / 2) * 100",
                1,
                "%",
                coupon=t["fixed"],
                price=price,
                n=n,
            )
            spread, sp_s = compute("spread to worst", "(ytm - rf) * 100", 0, "", ytm=ytm, rf=rf)
            r.update(years=n, yld=ytm, yld_s=ytm_s, spread=spread, spread_s=sp_s)
        else:
            dm, dm_s = compute(
                "3-year discount margin",
                "spread + (100 - price) / 3 * 100",
                0,
                "",
                spread=t["spread"],
                price=price,
            )
            r.update(spread=dm, spread_s=dm_s, yld=None)
        haz, hz_s = compute(
            "annual hazard (credit triangle)",
            "spread / 10000 / (1 - rec / 100)",
            4,
            "",
            spread=r["spread"],
            rec=r["recovery"],
        )
        cum, cum_s = compute(
            "3-year cumulative default probability",
            "(1 - (1 - hazard) * (1 - hazard) * (1 - hazard)) * 100",
            1,
            "%",
            hazard=haz,
        )
        loss, loss_s = compute(
            "3-year implied loss", "pd * (100 - rec) / 100", 1, "%", pd=cum, rec=r["recovery"]
        )
        be, be_s = compute(
            "break-even spread",
            "hazard * (100 - rec) / 100 * 10000",
            0,
            "",
            hazard=haz,
            rec=r["recovery"],
        )
        r.update(
            hazard=haz, hz_s=hz_s, pd=cum, pd_s=cum_s, loss=loss, loss_s=loss_s, be=be, be_s=be_s
        )
        out[fid] = r
    return out


SCENARIO_KEYS = {
    "Going concern: low": "low",
    "Going concern: base": "base",
    "Going concern: high": "high",
    "Liquidation": "liquidation",
}


def expected_recovery() -> dict[str, tuple[Decimal, str]]:
    """Probability-weighted recovery (percent) by class across the four scenarios, with its calc string."""
    probs = F.val("ev_probabilities")
    evs = enterprise_values()
    rec = {sc: {r["class_id"]: r["pct"] for r in waterfall(evs[sc][2])} for sc in SCENARIO_KEYS}
    out = {}
    for cid, _ in CLASSES:
        names = {f"p{i}": D(probs[SCENARIO_KEYS[sc]]) for i, sc in enumerate(SCENARIO_KEYS)}
        names.update({f"r{i}": q(rec[sc][cid], 1) for i, sc in enumerate(SCENARIO_KEYS)})
        expr = "(" + " + ".join(f"p{i} * r{i}" for i in range(4)) + ") / 100"
        out[cid] = compute(f"expected recovery of {cid}", expr, 1, "%", **names)
    return out


def require(ctx, run_id: str, *steps: str) -> None:
    """Raise IncompleteRun (reported by the build as 'incomplete') when an upstream host step did not run.

    The Larchmere run has no CP-DR (no research question approved); until RUNS sets deep_research=False for it, the Run
    skips MODEL as 'inputs missing', and every module that reads the Model would otherwise crash with a KeyError."""
    from run import IncompleteRun

    miss = [s for s in steps if (run_id, s) not in ctx.built]
    if miss:
        raise IncompleteRun(
            [
                f"{', '.join(miss)} (not built: RUNS must set deep_research=False for this run, since CP-DR is skipped)"
            ]
        )
