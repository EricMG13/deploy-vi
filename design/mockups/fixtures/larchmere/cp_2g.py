"""Larchmere CP-2G: forward model drivers (synthetic). The Run projects BASE and DOWNSIDE from `h.meta["projection"]`;
the movements here come from a scratch ModelBuilder fed the same drivers, so they equal PROJECTION's values."""

from __future__ import annotations

import re
from decimal import Decimal

from core import MCTX, Ctx, D, Handoff, compute, plain, q
from lib import ModelBuilder

from . import derived as X
from . import facts as F
from .facts import syn

YEARS = F.val("projection_floor")["years"]
CASES = ("BASE", "DOWNSIDE")


def consolidated_growth(case: str, gulf_coast_flat: bool = False) -> dict[int, Decimal]:
    """Consolidated revenue growth (percent) by year, chained from LTM segment revenue and the segment growth drivers."""
    sg = F.val("segment_growth")[case]
    rev = {k: X.segment_ltm(k) for k in F.val("segment_revenue")}
    out: dict[int, Decimal] = {}
    prev = sum(rev.values(), Decimal(0))
    for i, y in enumerate(YEARS):
        for k in rev:
            g = Decimal(0) if (gulf_coast_flat and k == "seg_gulf_coast") else D(sg[k][i])
            rev[k] = MCTX.multiply(rev[k], 1 + MCTX.divide(g, Decimal(100)))
        tot = sum(rev.values(), Decimal(0))
        out[y] = MCTX.multiply(MCTX.divide(tot, prev) - 1, Decimal(100))
        prev = tot
    return out


def rent_path() -> dict[int, Decimal]:
    rent = X.ltm("lease_cash")[0]
    esc = D(F.val("forward_12m")["rent_escalator_pct"])
    out = {}
    for y in YEARS:
        rent = q(MCTX.multiply(rent, 1 + MCTX.divide(esc, Decimal(100))), 2)
        out[y] = rent
    return out


def drivers(case: str, gulf_coast_flat: bool = False) -> dict:
    pd = F.val("projection_drivers")[case]
    pf = F.val("projection_floor")
    return dict(
        revenue_growth_pct=consolidated_growth(case, gulf_coast_flat),
        adjusted_ebitda_margin_pct={y: D(pd["margin"][i]) for i, y in enumerate(YEARS)},
        capex_pct_revenue={y: D(pd["capex_pct"][i]) for i, y in enumerate(YEARS)},
        cash_taxes={y: D(pd["taxes"][i]) for i, y in enumerate(YEARS)},
        wc_change={y: D(pd["wc"][i]) for i, y in enumerate(YEARS)},
        lease_cash=rent_path(),
        reference_rate_pct={y: D(F.val("rate_deck")[case][i]) for i, y in enumerate(YEARS)},
        mandatory_amortisation={"llg_tlb": {y: D(v) for y, v in pf["tlb_amort"].items()}},
        min_cash=pf["min_cash"],
    )


def scratch(ctx: Ctx, run_id: str, flat: bool = False) -> ModelBuilder:
    mb = ModelBuilder(
        ctx.get(run_id, "CP-1"), ctx.get(run_id, "RUN_BRIEF"), ctx.get(run_id, "CP-1D"), run_id
    )
    for case in CASES:
        mb.add_projection(case, YEARS, drivers(case, flat))
    return mb


def first_shortfall(mb: ModelBuilder, case: str) -> tuple[str, str, str]:
    """(period, detail, shortfall amount) of the first liquidity-shortfall check of a case."""
    for c in mb.forecast_checks:
        if c["check"] == "liquidity_shortfall" and c["case"] == case:
            amount = re.search(r"by ([\d.]+)", c["detail"])
            return c["period_id"], c["detail"], amount.group(1) if amount else "0"
    return "none", "no shortfall in the projection", "0"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2G",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "CP-2", "MODEL"],
        fixture_file="larchmere/cp_2g.py",
    )
    h.qa("Restricted")
    h.meta["projection"] = [(case, YEARS, drivers(case)) for case in CASES]
    mb = scratch(ctx, run_id)
    m_sg, m_pd, m_deck, m_pf, m_rent, m_seg, m_terms = (
        syn(h, k)
        for k in (
            "segment_growth",
            "projection_drivers",
            "rate_deck",
            "projection_floor",
            "forward_12m",
            "segment_revenue",
            "facility_terms",
        )
    )
    cu = "USD"
    drv_rows = []
    for case in CASES:
        for slot, sid in (
            ("DIVISION_1", "seg_gulf_coast"),
            ("DIVISION_2", "seg_mid_south"),
            ("DIVISION_3", "seg_online"),
        ):
            for i, y in enumerate(YEARS):
                v, _ = compute(
                    "growth fraction", "pct / 100", 4, "", pct=F.val("segment_growth")[case][sid][i]
                )
                drv_rows.append(
                    {
                        "driver_id": "segment_revenue_growth",
                        "slot_id": slot,
                        "case": case,
                        "fiscal_year": str(y),
                        "value": plain(v),
                        "unit": "PERCENT_DECIMAL",
                        "status": "READY",
                    }
                )
        for i, y in enumerate(YEARS):
            v, _ = compute(
                "margin fraction",
                "pct / 100",
                4,
                "",
                pct=F.val("projection_drivers")[case]["margin"][i],
            )
            drv_rows.append(
                {
                    "driver_id": "adjusted_ebitda_margin",
                    "slot_id": "CONSOLIDATED",
                    "case": case,
                    "fiscal_year": str(y),
                    "value": plain(v),
                    "unit": "PERCENT_DECIMAL",
                    "status": "READY",
                }
            )
    h.table("cp2g.cp_model_forecast_drivers", drv_rows)
    h.table(
        "cp2g.forecast_periods",
        [
            {"case": c, "period_id": f"FY{y}E_{c}", "fiscal_year": str(y), "days": "365"}
            for c in CASES
            for y in YEARS
        ],
    )
    mov = []
    for c in CASES:
        for y in YEARS:
            r = mb.projection_rows[c][y]
            mov.append(
                {
                    "case": c,
                    "period_id": f"FY{y}E_{c}",
                    "status": "READY",
                    "revenue": plain(q(r["revenue"], 3)),
                    "ebitda": plain(q(r["ebitda"], 3)),
                    "cfo": plain(q(r["cfo"], 3)),
                    "cash_taxes": plain(q(-r["taxes"], 3)),
                    "capex": plain(q(r["capex"], 3)),
                    "acquisitions_disposals": "0",
                    "distributions": plain(q(-r["dividends"], 3)),
                    "issuance": plain(q(r["draw"], 3)),
                    "optional_repayment": "0",
                    "pik": "0",
                    "capitalised_interest": "0",
                    "fx_perimeter": "0",
                    "currency": cu,
                    "unit": "MILLIONS",
                }
            )
    h.table("cp2g.forecast_movements", mov)
    am_rows = []
    for c in CASES:
        for y, a in F.val("projection_floor")["tlb_amort"].items():
            if D(a) > 0:
                am_rows.append(
                    {
                        "case": c,
                        "period_id": f"FY{y}E_{c}",
                        "facility_id": "llg_tlb",
                        "amount": plain(-D(a)),
                        "currency": cu,
                        "unit": "MILLIONS",
                        "cite": f"{m_pf}{m_terms}",
                    }
                )
    h.table("cp2g.forecast_amortisation", am_rows)
    h.table(
        "cp2g.rate_deck",
        [
            {
                "reference_rate": "Term SOFR",
                "fiscal_year_offset": str(i),
                "base_rate": plain(F.val("rate_deck")["BASE"][i], 2),
                "downside_rate": plain(F.val("rate_deck")["DOWNSIDE"][i], 2),
                "deck_date": "2026-10-01",
                "cite": m_deck,
            }
            for i in range(3)
        ],
    )
    asm = []
    n = 0

    def add(
        driver: str, case: str, period: str, value: str, unit: str, basis: str, why: str, cite: str
    ) -> None:
        nonlocal n
        n += 1
        asm.append(
            {
                "assumption_id": f"A{n:02d}",
                "driver": driver,
                "case": case,
                "period": period,
                "value": value,
                "unit_label": unit,
                "basis_class": basis,
                "rationale": why,
                "cite": cite,
            }
        )

    for case in CASES:
        g = consolidated_growth(case)
        for y in YEARS:
            add(
                "Consolidated revenue growth",
                case,
                f"FY{y}E",
                plain(q(g[y], 1)),
                "%",
                "Derived",
                "Chained from the three segment growth drivers weighted by LTM revenue.",
                f"{m_sg}{m_seg}",
            )
        for i, y in enumerate(YEARS):
            add(
                "SSIM EBITDA margin",
                case,
                f"FY{y}E",
                plain(F.val("projection_drivers")[case]["margin"][i], 1),
                "%",
                "Analyst assumption",
                "Margin falls as fixed costs are spread over lower revenue; downside falls faster.",
                m_pd,
            )
        pd = F.val("projection_drivers")[case]
        add(
            "Capital expenditure",
            case,
            "FY2026E-FY2028E",
            plain(pd["capex_pct"][0], 1),
            "% of revenue",
            "Analyst assumption",
            "Maintenance level; the downside defers part of it.",
            m_pd,
        )
        add(
            "Working capital change",
            case,
            "FY2026E-FY2028E",
            "/".join(plain(v) for v in pd["wc"]),
            "USD millions a year",
            "Analyst assumption",
            "Suppliers shorten terms as the credit weakens; the downside is worse.",
            m_pd,
        )
        add(
            "Cash taxes",
            case,
            "FY2026E-FY2028E",
            "/".join(plain(v) for v in pd["taxes"]),
            "USD millions a year",
            "Analyst assumption",
            "State and gaming taxes only.",
            m_pd,
        )
        add(
            "Term SOFR",
            case,
            "FY2026E-FY2028E",
            "/".join(plain(v, 2) for v in F.val("rate_deck")[case]),
            "%",
            "Analyst assumption",
            "Forward deck from Market Context (synthetic); downside 50 bps higher.",
            m_deck,
        )
    rp = rent_path()
    add(
        "Master-lease cash rent",
        "BASE",
        "FY2026E-FY2028E",
        "/".join(plain(rp[y], 2) for y in YEARS),
        "USD millions a year",
        "Derived",
        "LTM rent of 62 escalated 1.5% a year.",
        m_rent,
    )
    add(
        "Master-lease cash rent",
        "DOWNSIDE",
        "FY2026E-FY2028E",
        "/".join(plain(rp[y], 2) for y in YEARS),
        "USD millions a year",
        "Derived",
        "The escalator is contractual, so it is the same in both cases.",
        m_rent,
    )
    add(
        "Term loan B amortisation",
        "BASE",
        "FY2026E-FY2028E",
        "/".join(plain(D(v), 2) for v in F.val("projection_floor")["tlb_amort"].values()),
        "USD millions a year",
        "Sourced",
        "1.00% a year from 30 September 2026; the 2028 balance is left outstanding.",
        f"{m_terms}{m_pf}",
    )
    h.table("cp2g.assumptions", asm)
    flat = scratch(ctx, run_id, flat=True)
    base_p, base_d, base_amt = first_shortfall(mb, "BASE")
    down_p, down_d, _down_amt = first_shortfall(mb, "DOWNSIDE")
    flat_p, flat_d, flat_amt = first_shortfall(flat, "BASE")
    gap_28 = plain(-q(mb.projection_rows["BASE"][2028]["cash"], 0))
    h.table(
        "cp2g.break_points",
        [
            {
                "shock": "Base case as projected",
                "first_break": f"Cash floor of 50 breached in {base_p.replace('_BASE', '')}: {base_d}",
                "period": base_p.replace("_BASE", ""),
                "consequence": f"An unfunded gap opens in {base_p.replace('_BASE', '')}, after the NEW-1 proceeds are spent, and reaches {gap_28} by FY2028E.",
                "recovery_action": "New money, a lender standstill on interest or a rent concession of the size of the gap.",
                "cite": f"{m_pd}{m_sg}",
            },
            {
                "shock": "Downside case as projected",
                "first_break": f"Cash floor of 50 breached in {down_p.replace('_DOWNSIDE', '')}: {down_d}",
                "period": down_p.replace("_DOWNSIDE", ""),
                "consequence": "The gap is larger every year and the 2028 maturities are not refinanceable.",
                "recovery_action": "A prepack with a debt-for-equity exchange rather than an out-of-court extension.",
                "cite": f"{m_pd}{m_sg}",
            },
            {
                "shock": "Base case with Gulf Coast revenue flat from 2026",
                "first_break": f"Cash floor of 50 breached in {flat_p.replace('_BASE', '')}: {flat_d}",
                "period": flat_p.replace("_BASE", ""),
                "consequence": f"Holding Gulf Coast flat narrows the first shortfall only from {base_amt} to {flat_amt}, because the extra revenue earns the 13% margin and fixed charges exceed EBITDA.",
                "recovery_action": "Operational recovery alone cannot solve the problem; the capital structure has to change.",
                "cite": f"{m_pd}{m_sg}",
            },
        ],
    )
    b = {y: mb.projection_rows["BASE"][y] for y in YEARS}
    d = {y: mb.projection_rows["DOWNSIDE"][y] for y in YEARS}
    gap_b = q(-b[2028]["cash"], 0)
    pf_cash = plain(
        q(
            D(
                next(
                    r["value"]
                    for r in ctx.get(run_id, "CP-1").rows("cp1.pro_forma_adjustment_register")
                    if r["adjustment_id"] == "PF-CASH"
                )
            ),
            0,
        )
    )
    h.analysis(
        f"The projection opens from the pro forma June balances, which include the sponsor's NEW-1 priming loan: {plain(F.val('new_money')['size'])} of new debt and {pf_cash} of cash net of OID. "
        f"Even so the company runs out of liquidity: the base case burns free cash flow of {plain(q(-b[2026]['fcf'], 0))} in FY2026E, {plain(q(-b[2027]['fcf'], 0))} in FY2027E and {plain(q(-b[2028]['fcf'], 0))} in FY2028E, "
        f"so cash ends FY2026E at {plain(q(b[2026]['cash'], 0))}, falls below the 50 floor in {base_p.replace('_BASE', '')} and an unfunded gap of {plain(gap_b)} accumulates by FY2028E {m_pd}. The downside burns {plain(q(-d[2026]['fcf'], 0))} in FY2026E, ends FY2026E at {plain(q(d[2026]['cash'], 0))}, breaches the floor in {down_p.replace('_DOWNSIDE', '')} and reaches an unfunded gap of {plain(q(-d[2028]['cash'], 0))} by FY2028E. "
        "Module view: no operating recovery closes the gap; the capital structure has to change. Confidence is Medium.\n\n"
        f"Revenue falls in every segment in the base case (Gulf Coast -6.0%, Mid-South -4.5% and Online -1.0% in FY2026E), giving consolidated growth of {plain(q(consolidated_growth('BASE')[2026], 1))}% {m_sg}. "
        f"SSIM EBITDA is {plain(q(b[2026]['ebitda'], 0))} in FY2026E and {plain(q(b[2028]['ebitda'], 0))} in FY2028E against {plain(X.ssim_ltm())} LTM, because margins fall 70 basis points a year as fixed costs are spread over fewer customers {m_pd}. "
        f"Interest is projected from the rate deck {m_deck} and the facility spreads {m_terms}.\n\n"
        "The 2028 revolver and term loan B maturities are left outstanding in the projection and flagged as assumed refinanced, which a real market would not do; the break-point table shows that even holding Gulf Coast flat leaves a gap, because cash interest and rent exceed EBITDA."
    )
    h.gaps(
        "- Management forecast: the lender presentation gives totals to 2028 only, so the segment drivers are the analyst's. Effect: the cases bracket rather than replicate management's plan. Lifted by: the management model.\n"
        "- Intra-year timing: projected years open from the June 2026 balances and run to 31 December, so FY2026E carries a full year of flows. Effect: the first-year gap is overstated against a half-year. Lifted by: a quarterly model.\n"
        "- Negative cash is the unfunded gap, not a balance: the projection does not assume new money."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
