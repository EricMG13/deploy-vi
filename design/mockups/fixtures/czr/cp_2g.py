"""CZR CP-2G: forward credit model drivers. The real CAOS run found no supported numeric forecast assumptions (no
guidance, G13), so every driver here is a SYNTHETIC test value from `synthetic-facts.json -> czr.projection_drivers`
and `czr.rate_deck`, stated as such. Real inputs: contractual amortisation (CP-1 facility terms) and the LTM base.

The Run builds PROJECTION from `h.meta["projection"]`. To make these tables carry exactly the values PROJECTION will
show, this module runs the same projection on a throwaway ModelBuilder built from the same handoffs."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from core import Ctx, D, Handoff, compute, fx, plain, q
from helpers import caos_text, join_marks
from model import ModelBuilder

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]
YEARS = [2026, 2027, 2028]
CASES = [("BASE", "base"), ("DOWNSIDE", "downside")]
DAYS = {2026: "365", 2027: "365", 2028: "366"}
AMORT_FACILITIES = ["cei_term_a", "cei_term_b", "cei_term_b1"]


def _amort(cp1: Handoff) -> dict[str, dict[int, Decimal]]:
    """Scheduled annual amortisation from CP-1's facility register; Term Loan A matures 31 January 2028, so it stops
    after 2027 (the Model then flags the 2028 maturity as assumed refinanced)."""
    ann = {
        r["facility_id"]: r["annual_amortisation"]
        for r in cp1.rows("cp1.debt_facility_register")
        if r["period_id"] == "JUN30_2026"
    }
    out: dict[str, dict[int, Decimal]] = {}
    for f in AMORT_FACILITIES:
        a = D(ann[f])
        out[f] = {y: a for y in YEARS if not (f == "cei_term_a" and y == 2028)}
    return out


def _drivers(case: str, rev0: Decimal, amort: dict) -> dict:
    pd, rd = FACTS["projection_drivers"][case], FACTS["rate_deck"][case]
    growth = {y: D(pd["revenue_growth_pct"][f"FY{y}"]) for y in YEARS}
    rev, capex_pct = rev0, {}
    for (
        y
    ) in YEARS:  # the capex amount in the facts becomes the percentage of revenue the Model applies
        rev = rev * (1 + growth[y] / 100)
        capex_pct[y] = D(pd["capex"][f"FY{y}"]) / rev * 100
    return {
        "revenue_growth_pct": growth,
        "adjusted_ebitda_margin_pct": {
            y: D(pd["adjusted_ebitda_margin_pct"][f"FY{y}"]) for y in YEARS
        },
        "capex_pct_revenue": capex_pct,
        "cash_taxes": {y: D(pd["cash_taxes"][f"FY{y}"]) for y in YEARS},
        "wc_change": {y: D(pd["working_capital_change"][f"FY{y}"]) for y in YEARS},
        "reference_rate_pct": {y: D(rd[f"FY{y}"]) for y in YEARS},
        "mandatory_amortisation": amort,
    }


def _throwaway(ctx: Ctx, run_id: str, projection: list) -> ModelBuilder:
    mb = ModelBuilder(
        ctx.get(run_id, "CP-1"),
        ctx.get(run_id, "RUN_BRIEF"),
        ctx.built.get((run_id, "CP-1D")),
        run_id,
    )
    for case, years, drivers in projection:
        mb.add_projection(case, years, drivers)
    return mb


def _lev(r: dict) -> Decimal:
    v, _ = compute(
        "total debt / EBITDA", "debt / ebitda", 2, "x", debt=r["total_debt"], ebitda=r["ebitda"]
    )
    return v


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2G",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "CP-2", "MODEL"],
        fixture_file="czr/cp_2g.py",
    )
    h.qa("Restricted")
    cp1 = ctx.get(run_id, "CP-1")
    cm, c, fig = h.cite_caos, h.cite_data, h.cite_fig
    syn_drv = h.cite_synthetic(
        "projection_drivers",
        "No company guidance exists (G13), so the Base keeps FY2025's shape and the Downside is a Las Vegas downturn with Regional flat, as invented test drivers.",
        "Caesars",
        file="synthetic-facts.json",
    )
    syn_rate = h.cite_synthetic(
        "rate_deck",
        "No forward SOFR curve is in the pack (G30), so the deck is a plausible flat-to-falling Base path and a higher Downside path.",
        "Caesars",
        file="synthetic-facts.json",
    )

    amort = _amort(cp1)
    probe = ModelBuilder(
        cp1, ctx.get(run_id, "RUN_BRIEF"), ctx.built.get((run_id, "CP-1D")), run_id
    )
    rev0 = probe.L("revenue", probe.snapshot_base_col()).value
    projection = [(case, list(YEARS), _drivers(key, rev0, amort)) for case, key in CASES]
    h.meta["projection"] = projection
    mb = _throwaway(ctx, run_id, projection)
    res = mb.projection_rows  # {case: {year: row}}

    # ---- drivers (CAOS interface table, group level)
    rows = []
    for case, key in CASES:
        pd = FACTS["projection_drivers"][key]
        for y in YEARS:
            for did, val, unit, status in (
                ("revenue_growth_pct", pd["revenue_growth_pct"][f"FY{y}"], "PERCENT", "SYNTHETIC"),
                (
                    "adjusted_ebitda_margin_pct",
                    pd["adjusted_ebitda_margin_pct"][f"FY{y}"],
                    "PERCENT",
                    "SYNTHETIC",
                ),
                (
                    "capex_pct_revenue",
                    plain(q(projection[0 if key == "base" else 1][2]["capex_pct_revenue"][y], 4)),
                    "PERCENT",
                    "DERIVED",
                ),
                ("cash_taxes", pd["cash_taxes"][f"FY{y}"], "CURRENCY_MM", "SYNTHETIC"),
                (
                    "working_capital_change",
                    pd["working_capital_change"][f"FY{y}"],
                    "CURRENCY_MM",
                    "SYNTHETIC",
                ),
                ("dividends_paid", "0", "CURRENCY_MM", "SYNTHETIC"),
            ):
                rows.append(
                    {
                        "driver_id": did,
                        "slot_id": "GROUP",
                        "case": case,
                        "fiscal_year": str(y),
                        "value": str(val),
                        "unit": unit,
                        "status": status,
                    }
                )
    h.table("cp2g.cp_model_forecast_drivers", rows)
    h.table(
        "cp2g.forecast_periods",
        [
            {"case": case, "period_id": f"FY{y}E_{case}", "fiscal_year": str(y), "days": DAYS[y]}
            for case, _ in CASES
            for y in YEARS
        ],
    )
    mv = []
    for case, _ in CASES:
        for y in YEARS:
            r = res[case][y]
            mv.append(
                {
                    "case": case,
                    "period_id": f"FY{y}E_{case}",
                    "status": "Projected",
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
                    "currency": "USD",
                    "unit": "MILLIONS",
                }
            )
    h.table("cp2g.forecast_movements", mv)

    term_marks = join_marks(*(cm(FOLDER, "CP-2G", i) for i in (9,)))
    am = []
    for case, _ in CASES:
        for f in AMORT_FACILITIES:
            for y, a in amort[f].items():
                am.append(
                    {
                        "case": case,
                        "period_id": f"FY{y}E_{case}",
                        "facility_id": f,
                        "amount": plain(-a),
                        "currency": "USD",
                        "unit": "MILLIONS",
                        "cite": join_marks(
                            c("C134")
                            if f == "cei_term_a"
                            else c("C140")
                            if f == "cei_term_b"
                            else c("C142"),
                            term_marks,
                        ),
                    }
                )
    h.table("cp2g.forecast_amortisation", am)
    h.table(
        "cp2g.rate_deck",
        [
            {
                "reference_rate": FACTS["rate_deck"]["reference_rate"],
                "fiscal_year_offset": str(i),
                "base_rate": FACTS["rate_deck"]["base"][f"FY{y}"],
                "downside_rate": FACTS["rate_deck"]["downside"][f"FY{y}"],
                "deck_date": FACTS["rate_deck"]["deck_date"],
                "cite": syn_rate,
            }
            for i, y in enumerate(YEARS)
        ],
    )

    # ---- assumptions, one row per driver and case
    def three(key: str, case: str, name: str) -> str:
        return ", ".join(FACTS["projection_drivers"][case][name][f"FY{y}"] for y in YEARS)

    ass = []
    n = 0
    for case, key in CASES:
        label = "Base" if key == "base" else "Downside"
        why = {
            "revenue_growth_pct": "Keeps FY2025's shape"
            if key == "base"
            else "A Las Vegas downturn with Regional flat",
            "adjusted_ebitda_margin_pct": "Near the LTM margin of 30.8%"
            if key == "base"
            else "Below the LTM margin as Las Vegas loses margin and costs are sticky",
            "capex": "Above the 2026 guide of US$645m to US$725m (H1 US$335m plus US$310m to US$390m), a conservative Base"
            if key == "base"
            else "Within the 2026 guide, then cut as growth projects are deferred",
            "cash_taxes": "Low as losses and interest shelter income"
            if key == "base"
            else "Lower still on lower income",
            "working_capital_change": "A modest outflow, as in FY2025 (US$79m)"
            if key == "base"
            else "A larger outflow as deposits unwind",
        }
        for name, unit, lab in (
            ("revenue_growth_pct", "%", "Revenue growth"),
            ("adjusted_ebitda_margin_pct", "%", "Adjusted EBITDA margin"),
            ("capex", "US$ m", "Capex"),
            ("cash_taxes", "US$ m", "Cash taxes"),
            ("working_capital_change", "US$ m", "Working capital change"),
        ):
            n += 1
            ass.append(
                {
                    "assumption_id": f"A-{n:02d}",
                    "driver": lab,
                    "case": case,
                    "period": "FY2026 to FY2028",
                    "value": three(name, key, name),
                    "unit_label": unit,
                    "basis_class": "Analyst assumption",
                    "rationale": f"Synthetic test value. {why[name]}.",
                    "cite": syn_drv,
                }
            )
        n += 1
        ass.append(
            {
                "assumption_id": f"A-{n:02d}",
                "driver": "Term SOFR deck",
                "case": case,
                "period": "FY2026 to FY2028",
                "value": ", ".join(FACTS["rate_deck"][key][f"FY{y}"] for y in YEARS),
                "unit_label": "%",
                "basis_class": "Analyst assumption",
                "rationale": f"Synthetic test value. {label} path; no forward curve in the pack.",
                "cite": syn_rate,
            }
        )
    lease_ltm = ctx.val("ltm_cash_interest_rent_q2_2026")
    for case, _ in CASES:
        n += 1
        ass.append(
            {
                "assumption_id": f"A-{n:02d}",
                "driver": "Lease cash (VICI and GLPI)",
                "case": case,
                "period": "FY2026 to FY2028",
                "value": f"{plain(lease_ltm)} a year",
                "unit_label": "US$ m",
                "basis_class": "Derived",
                "rationale": "Held at the real LTM cash interest paid for rent; no escalator is modelled.",
                "cite": fig("ltm_cash_interest_rent_q2_2026"),
            }
        )
        n += 1
        ass.append(
            {
                "assumption_id": f"A-{n:02d}",
                "driver": "Scheduled amortisation",
                "case": case,
                "period": "FY2026 to FY2028",
                "value": "Term Loan A 37.5 to January 2028; Term Loans B and B-1 25.0 and 29.0 a year",
                "unit_label": "US$ m",
                "basis_class": "Sourced",
                "rationale": "Contractual quarterly amortisation per the credit agreement terms in CP-1.",
                "cite": join_marks(c("C134"), c("C140"), c("C142")),
            }
        )
        n += 1
        ass.append(
            {
                "assumption_id": f"A-{n:02d}",
                "driver": "Maturities and distributions",
                "case": case,
                "period": "FY2028",
                "value": "Revolver and Term Loan A (31 January 2028) assumed refinanced on the same terms; no dividends",
                "unit_label": "text",
                "basis_class": "Analyst assumption",
                "rationale": "No refinancing plan or dividend is disclosed; the merger agreement restricts distributions while pending.",
                "cite": join_marks(c("C162"), syn_drv),
            }
        )
    h.table("cp2g.assumptions", ass)

    # ---- break points from the projection
    def k(x: Decimal) -> str:
        return f"{int(q(x, 0)):,}"

    def usd(x: Decimal) -> str:
        return f"{'-' if x < 0 else ''}US${k(abs(x))}m"

    def move(x: Decimal) -> str:
        return f"turns negative at US${k(abs(x))}m" if x < 0 else f"falls to US${k(x)}m"

    b26, d26, d27, d28 = (
        res["BASE"][2026],
        res["DOWNSIDE"][2026],
        res["DOWNSIDE"][2027],
        res["DOWNSIDE"][2028],
    )
    cash0 = mb.L("cash_closing", mb.snapshot_base_col()).value
    f26, c_f26 = compute(
        "FY2026 Downside FCF", "cfo + capex", 1, "", cfo=q(d26["cfo"], 3), capex=q(d26["capex"], 3)
    )
    f27, c_f27 = compute(
        "FY2027 Downside FCF", "cfo + capex", 1, "", cfo=q(d27["cfo"], 3), capex=q(d27["capex"], 3)
    )
    f28, _ = compute(
        "FY2028 Downside FCF", "cfo + capex", 1, "", cfo=q(d28["cfo"], 3), capex=q(d28["capex"], 3)
    )
    cum, c_cum = compute(
        "cumulative Downside FCF, FY2026 to FY2028", "a + b + c", 1, "", a=f26, b=f27, c=f28
    )
    lev_b, lev_d = _lev(b26), _lev(d27)
    bp = [
        (
            "Downside FY2026: revenue -3.0% and margin 29.0%",
            f"Free cash flow {move(f26)}, against {usd(b26['fcf'])} in the Base",
            "FY2026",
            f"Cash goes from US${k(cash0)}m to US${k(d26['cash'])}m and EBITDA to US${k(d26['ebitda'])}m; total debt to EBITDA {fx(_lev(d26))}.",
            "Defer growth and digital capex (already cut to US$700m) and hold dividends at zero.",
            f"{syn_drv} {c_f26}",
        ),
        (
            "Downside FY2027: revenue -4.0% and margin 28.0%",
            f"Free cash flow {move(f27)} and cash of US${k(d27['cash'])}m",
            "FY2027",
            f"Total debt to EBITDA reaches {fx(lev_d)} against {fx(lev_b)} in the FY2026 Base; interest cover thins as SOFR rises to 4.90%.",
            "Draw the revolver (US$1,963m available), extend the 2028 maturities early, and seek covenant relief if tests are triggered.",
            f"{syn_drv} {c_f27}",
        ),
        (
            "Downside through FY2028: cumulative cash",
            f"Cumulative free cash flow of {usd(cum)} over three years",
            "FY2028",
            f"Cash is US${k(d28['cash'])}m at the end of FY2028 with no revolver draw modelled; the January 2028 maturities are assumed refinanced.",
            "A refinancing of the revolver and Term Loan A before 2028 becomes necessary rather than optional.",
            f"{syn_drv} {c_cum}",
        ),
        (
            "Revolver and Term Loan A maturity on 31 January 2028",
            "US$767m of 2028 maturities (revolver and Term Loan A) fall due with no extension announced",
            "FY2028",
            "If not refinanced, the revolver's US$2,130m of net capacity leaves accessible liquidity and the funding gap is US$138m before any operating cash flow.",
            "Extend before the maturity falls inside twelve months; the Model assumes the same terms.",
            join_marks(c("C162"), c("C180"), fig("cr_gap_2028")),
        ),
    ]
    h.table(
        "cp2g.break_points",
        [
            {
                "shock": s,
                "first_break": fb,
                "period": p,
                "consequence": co,
                "recovery_action": ra,
                "cite": ck,
            }
            for s, fb, p, co, ra, ck in bp
        ],
    )

    primary = mb.snapshot_base_col().kind == "PF_LTM"
    text = (
        "All forecast drivers in this module are synthetic test values. The real CAOS run found no supported numeric assumptions, because the sources hold no guidance, forecast, cash-tax or working-capital schedule, and it left every FY2026 to FY2028 driver blank. "
        "The fixture fills them so the Model can project; none is a fact about Caesars or a forecast.\n\n"
        f"Base case. Revenue grows 2.0%, 2.5% and 2.5% at a 31.0% to 31.5% margin from the real LTM base (US$11,648m of revenue, US$3,592m of Adjusted EBITDA). FY2026E EBITDA is US${k(b26['ebitda'])}m, free cash flow US${k(b26['fcf'])}m and total debt to EBITDA {fx(lev_b)}"
        f"{', with the synthetic merger tranches in the opening debt' if primary else ''}. Capex of US$760m is above the 2026 guide of US$645m to US$725m, a conservative Base. {{3, 4, 6, 12}}\n\n"
        f"Downside case. A Las Vegas downturn takes revenue down 3.0% and 4.0% and the margin to 29.0% and 28.0%. Free cash flow is {usd(d26['fcf'])} in FY2026 and {usd(d27['fcf'])} in FY2027 against {usd(b26['fcf'])} in the FY2026 Base, cash ends FY2027 at {usd(d27['cash'])} and total debt to EBITDA reaches {fx(lev_d)}. "
        "The first inflection is cash conversion, before interest, rent and capex adjust, as the real run's qualitative downside also found. {21, 22}\n\n"
        "Rates and amortisation. The SOFR deck is synthetic (Base 4.30%, 3.90% and 3.70%; Downside 4.80%, 4.90% and 4.70%). Scheduled amortisation of Term Loans A, B and B-1 is real: US$91.5m a year, less Term Loan A after its January 2028 maturity. The revolver and Term Loan A are assumed refinanced on the same terms in FY2028, which the Model flags. {10, 13}\n\n"
        "Liquidity and the contrary view. June liquidity was US$2,928m, and management expected liquidity and cash flow to cover the next twelve months and beyond; covenant compliance is reported but headroom is not. That would outweigh the Downside if cash after capex and rent held. "
        "The observable triggers are cash decline, revolver draws, weaker operating cash flow and lower Las Vegas results. {8, 17, 20}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-2G", text))
    h.gaps(
        "- Every numeric forecast driver (revenue growth, margin, capex, cash taxes, working capital, SOFR deck) is synthetic; the sources hold no guidance (G13) or forward curve (G30). Effect: PROJECTION shows a design case, not a view. Source: a company forecast and a rate deck.\n"
        "- Division-level growth: the real driver table is by segment slot; the fixture drivers are group-level. Effect: no segment forecast. Source: segment guidance.\n"
        "- Refinancing: the 2028 maturities are assumed refinanced on the same terms. Source: a refinancing plan.\n"
        "- Covenant headroom is not projected; current definitions and headroom are undisclosed (G34)."
    )
    return h
