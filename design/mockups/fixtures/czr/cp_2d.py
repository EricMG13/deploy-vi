"""CZR CP-2D: liquidity and the 12-month bridge (30 June 2026 to 30 June 2027). Sources and the remaining-2026 uses are
the real 10-Q figures; first-half 2027 uses are straight-line halves of the 10-Q's FY2027 estimates; 2027 capex is the
synthetic Base driver. The operating inflow in the bridge holds the real LTM level flat (a stated assumption).
Bridge and runway are calculated, never typed. Rent is counted here, so the runway differs from the Front Pages'
(which exclude it and run to December 2027)."""

from __future__ import annotations

import json
from pathlib import Path

from core import Ctx, D, Handoff, compute, plain
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]
CAPEX_2027 = D(FACTS["projection_drivers"]["base"]["capex"]["FY2027"])


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2D",
        "CZR",
        run_id,
        "2026-10-02",
        ["CP-0", "CP-1", "MODEL"],
        fixture_file="czr/cp_2d.py",
    )
    h.qa("Restricted")
    cm, c, fig = h.cite_caos, h.cite_data, h.cite_fig

    def m(*n: int) -> str:
        return join_marks(*(cm(FOLDER, "CP-2D", i) for i in n))

    syn = h.cite_synthetic(
        "capex_2027",
        "The sources give no capex beyond 2026 (G29), so the Base case's FY2027 capex is a plausible step up from the 2026 run rate.",
        "Caesars",
        file="synthetic-facts.json",
    )

    # ---- sources
    cash, cei_net, cva = ctx.val("liq_cash"), ctx.val("liq_cei_rcf_net"), ctx.val("liq_cva_rcf")
    lc, res, reg = -ctx.val("liq_lcs"), -ctx.val("liq_reserves"), -ctx.val("liq_regulatory")
    cei_avail, c_cei = compute(
        "CEI revolver available after letters of credit, reserves and regulatory commitment",
        "net - lc - res - reg",
        0,
        "",
        net=cei_net,
        lc=lc,
        res=res,
        reg=reg,
    )
    accessible, c_acc = compute(
        "accessible liquidity", "cash + cei + cva", 0, "", cash=cash, cei=cei_avail, cva=cva
    )
    assert accessible == ctx.val("liq_total"), "sources must sum to the issuer's US$2,928m"
    src = [
        (
            "Cash and cash equivalents",
            cash,
            "Yes",
            "Excludes restricted cash.",
            join_marks(m(1), c("C171")),
        ),
        (
            "CEI revolver capacity available",
            cei_avail,
            "Yes",
            "US$2,130m net of the drawn balance, less letters of credit, reserves and the regulatory commitment; matures 31 January 2028.",
            join_marks(m(3, 5, 6, 7), c("C172")) + f" {c_cei}",
        ),
        (
            "CVA revolver capacity",
            cva,
            "Yes",
            "A separate borrower; not interchangeable with parent capacity.",
            join_marks(m(4), c("C173")),
        ),
        (
            "Revolver capacity committed to letters of credit",
            lc,
            "No",
            "Already committed; deducted from the CEI revolver line.",
            join_marks(m(5), c("C174")),
        ),
        (
            "Revolver capacity committed to specific reserves",
            res,
            "No",
            "Available only for certain permitted uses.",
            join_marks(m(6), c("C175")),
        ),
        (
            "Revolver capacity committed as a regulatory requirement",
            reg,
            "No",
            "Held for regulatory purposes.",
            join_marks(m(7), c("C176")),
        ),
        (
            "Restricted cash",
            ctx.val("restricted_cash_bs_2026_06_30"),
            "No",
            "Restricted; outside accessible liquidity.",
            join_marks(m(8), c("C106")),
        ),
    ]
    h.table(
        "cp2d.liquidity_sources",
        [
            {
                "component": n,
                "amount": plain(a),
                "currency": "USD",
                "unit": "MILLIONS",
                "accessible": acc,
                "restriction": r,
                "cite": ck,
            }
            for n, a, acc, r, ck in src
        ],
    )

    # ---- uses (positive magnitudes), 1 July 2026 to 30 June 2027
    ds = ctx.val("guide_remaining_2026_debt_service")
    int27, c_int = compute(
        "H1 2027 interest as half of the FY2027 estimate",
        "x / 2",
        0,
        "",
        x=ctx.val("guide_2027_interest"),
    )
    mat27, c_mat = compute(
        "H1 2027 maturities as half of FY2027", "x / 2", 0, "", x=ctx.val("debt_maturity_2027")
    )
    rent26 = D("687")
    rent_ltm = ctx.val("ltm_cash_interest_rent_q2_2026")
    rent27, c_rent = compute("H1 2027 rent as half of LTM cash rent", "x / 2", 0, "", x=rent_ltm)
    mcap26 = ctx.val("guide_capex_remaining_2026_maintenance_high")
    gcap26 = ctx.val("guide_capex_remaining_2026_growth_high") + ctx.val(
        "guide_capex_remaining_2026_digital_high"
    )
    cap27, c_cap = compute("H1 2027 capex as half of FY2027", "x / 2", 0, "", x=CAPEX_2027)
    tot26 = ctx.val("guide_capex_remaining_2026_maintenance_high") + gcap26
    mcap27, c_m27 = compute(
        "H1 2027 maintenance capex at the 2026 maintenance share",
        "capex * m / total",
        0,
        "",
        capex=cap27,
        m=mcap26,
        total=tot26,
    )
    gcap27, c_g27 = compute(
        "H1 2027 growth and digital capex", "capex - m", 0, "", capex=cap27, m=mcap27
    )
    uses = [
        (
            "Debt service, second half of 2026",
            ds,
            "H2 2026",
            "Yes",
            join_marks(m(10, 11), c("C273")),
        ),
        (
            "Interest, first half of 2027",
            int27,
            "H1 2027",
            "Yes",
            join_marks(c("C275")) + f" {c_int}",
        ),
        (
            "Debt maturities, first half of 2027",
            mat27,
            "H1 2027",
            "Yes",
            join_marks(c("C179")) + f" {c_mat}",
        ),
        ("VICI and GLPI lease payments, second half of 2026", rent26, "H2 2026", "Yes", m(12)),
        (
            "VICI and GLPI lease payments, first half of 2027",
            rent27,
            "H1 2027",
            "Yes",
            join_marks(h.cite_fig("ltm_cash_interest_rent_q2_2026")) + f" {c_rent}",
        ),
        (
            "Maintenance capex, second half of 2026 (high end)",
            mcap26,
            "H2 2026",
            "Yes",
            join_marks(m(16), c("C283")),
        ),
        (
            "Maintenance capex, first half of 2027",
            mcap27,
            "H1 2027",
            "Yes",
            join_marks(c("C283"), syn) + f" {c_m27}",
        ),
        (
            "Growth and digital capex, second half of 2026 (high end)",
            gcap26,
            "H2 2026",
            "No",
            join_marks(m(14, 15), fig("cr_disc_uses")),
        ),
        (
            "Growth and digital capex, first half of 2027",
            gcap27,
            "H1 2027",
            "No",
            join_marks(syn) + f" {c_g27}",
        ),
    ]
    h.table(
        "cp2d.cash_uses_12m",
        [
            {
                "use": u,
                "amount": plain(a),
                "currency": "USD",
                "unit": "MILLIONS",
                "timing": t,
                "mandatory": mand,
                "cite": ck,
            }
            for u, a, t, mand, ck in uses
        ],
    )
    mand_total = sum((a for _, a, _, mand, _ in uses if mand == "Yes"), D(0))
    other_total = sum((a for _, a, _, mand, _ in uses if mand == "No"), D(0))

    # ---- bridge
    cfo, ci_debt = ctx.val("ltm_cfo_q2_2026"), ctx.val("ltm_cash_interest_debt_q2_2026")
    op_in, c_op = compute(
        "operating cash flow before cash interest and rent",
        "cfo + int + rent",
        0,
        "",
        cfo=cfo,
        int=ci_debt,
        rent=rent_ltm,
    )
    steps = [
        (
            "Beginning accessible liquidity, 30 June 2026",
            "Opening total",
            accessible,
            "Cash plus available revolver capacity per the 10-Q liquidity table.",
            join_marks(m(2), c("C177")),
        )
    ]
    steps.append(
        (
            "Operating cash flow before cash interest and rent, at the LTM level",
            "Delta",
            op_in,
            "Assumption: the real LTM level (cash from operations plus cash interest paid for debt and for rent) repeats for 12 months; no forward forecast exists in the sources.",
            join_marks(
                fig("ltm_cfo_q2_2026"),
                fig("ltm_cash_interest_debt_q2_2026"),
                fig("ltm_cash_interest_rent_q2_2026"),
            )
            + f" {c_op}",
        )
    )
    for u, a, t, mand, ck in uses:
        steps.append(
            (u, "Use", -a, f"{'Mandatory' if mand == 'Yes' else 'Discretionary'} use, {t}.", ck)
        )
    closing = accessible + op_in - mand_total - other_total
    steps.append(
        (
            "Ending accessible liquidity, 30 June 2027, before refinancing",
            "Closing total",
            closing,
            "Opening plus the operating inflow less every use; the 2028 maturities are outside the window.",
            "calc: ending liquidity = opening + operating cash flow - uses",
        )
    )
    # the closing cite must be a recomputable calc: opening + delta + signed uses
    expr = " + ".join(["o", "d"] + [f"u{i}" for i in range(len(uses))])
    vals = {"o": accessible, "d": op_in, **{f"u{i}": -a for i, (_, a, _, _, _) in enumerate(uses)}}
    closing_v, c_close = compute("ending accessible liquidity", expr, 0, "", **vals)
    assert closing_v == closing
    steps[-1] = steps[-1][:4] + (c_close,)
    h.table(
        "cp2d.bridge",
        [
            {
                "step": s,
                "kind": k,
                "amount": plain(a),
                "currency": "USD",
                "unit": "MILLIONS",
                "basis": b,
                "cite": ck,
            }
            for s, k, a, b, ck in steps
        ],
    )

    # ---- runway
    headroom, c_head = compute("headroom", "acc - mand", 0, "", acc=accessible, mand=mand_total)
    months, c_mon = compute(
        "months of runway", "acc / (mand / 12)", 1, "", acc=accessible, mand=mand_total
    )
    pinch = "31 January 2028: the CEI revolver and Term Loan A mature, and the revolver's net capacity of US$2,130m falls out of liquidity"
    run = [
        (
            "Accessible liquidity",
            accessible,
            "US$ m",
            "Cash plus available revolver capacity at 30 June 2026.",
            join_marks(c("C177")) + f" {c_acc}",
        ),
        (
            "Mandatory uses 12m",
            mand_total,
            "US$ m",
            "Debt service, interest, maturities, lease payments and maintenance capex, July 2026 to June 2027, before any operating cash flow.",
            "calc: sum of the mandatory rows in cash_uses_12m",
        ),
        (
            "Headroom",
            headroom,
            "US$ m",
            "Accessible liquidity less mandatory uses, a stress with no operating inflow.",
            c_head,
        ),
        (
            "Months of runway",
            months,
            "months",
            "Accessible liquidity over mandatory uses per month, before any operating cash flow; the bridge adds the LTM operating inflow.",
            c_mon,
        ),
        (
            "Pinch point",
            None,
            "text",
            "The first date a large source disappears.",
            join_marks(c("C162"), fig("cr_rcf_share")),
        ),
    ]
    mand_expr = " + ".join(f"u{i}" for i in range(sum(1 for u in uses if u[3] == "Yes")))
    mand_vals = {f"u{i}": a for i, a in enumerate(a for _, a, _, mm, _ in uses if mm == "Yes")}
    _, c_mand = compute("mandatory uses", mand_expr, 0, "", **mand_vals)
    h.table(
        "cp2d.runway",
        [
            {
                "item": it,
                "value": pinch if it == "Pinch point" else plain(v),
                "unit_label": ul,
                "basis": b,
                "cite": (c_mand if it == "Mandatory uses 12m" else ck),
            }
            for it, v, ul, b, ck in run
        ],
    )

    text = (
        f"Yes: accessible liquidity of US${int(accessible):,}m covers the mandatory uses of the next 12 months (US${int(mand_total):,}m) with US${int(headroom):,}m to spare even if no operating cash came in, about {plain(months, 1)} months of runway, and the bridge ends 30 June 2027 at US${int(closing):,}m once the LTM operating inflow is counted. "
        "The pinch point is not the 12-month window but 31 January 2028, when the CEI revolver and Term Loan A mature. Liquidity risk is not rated by the real run (Insufficient Information); the figures here are calculated from its inputs. {1, 2}\n\n"
        "Sources. Caesars reported US$965m of cash and US$2,928m of cash plus borrowing capacity at 30 June 2026, which is US$2,130m of CEI revolver capacity net of drawings and US$25m of CVA capacity, less US$96m of letters of credit, US$40m of reserves and US$56m committed as a regulatory requirement. "
        "That leaves about US$1,963m of revolver availability. Restricted cash of US$96m is excluded. {3, 4, 5, 6, 7, 8}\n\n"
        "Uses. For the rest of 2026 the 10-Q estimates US$425m of debt service (US$55m of principal and US$370m of interest), US$687m of VICI and GLPI lease payments and US$310m to US$390m of capex. "
        "For the first half of 2027 the module takes half of the 10-Q's FY2027 interest (US$750m) and maturities (US$114m), half of LTM cash rent, and half of the synthetic Base capex of US$800m, split by the 2026 maintenance share. These halves are straight-line derivations, not company estimates. {10, 11, 12, 13, 16}\n\n"
        "Working capital and conversion. H1 2026 operating cash flow was US$675m against capex of US$335m, with working-capital items netting to an outflow of about US$71m; customer deposits of US$545m are operating float and earn no liquidity credit. Cash conversion is weak (about 36% of Adjusted EBITDA reaches operating cash flow). {17, 18, 23, 24, 25, 26, 27}\n\n"
        "Counterweights and risks. Management expects current liquidity and operating cash flow to be sufficient for the next twelve months and beyond, and covenant compliance is reported. Against that, US$6.0bn of floating-rate debt raises interest if rates rise, and the sources give no forward cash flow, tax or working-capital estimate, so the operating inflow is an assumption. Merger costs of US$10m were recorded in Q2. {28, 9, 29, 30}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-2D", text))
    h.gaps(
        "- Forward operating cash flow, cash taxes and working capital: none in the sources. Effect: the bridge's operating inflow holds the real LTM level flat; it is an assumption, not a forecast. Source: a company forecast.\n"
        "- First-half 2027 uses: straight-line halves of FY2027 estimates and of LTM rent, not company schedules. Source: dated debt-service and lease schedules.\n"
        "- 2027 capex: synthetic Base driver (G29), and its maintenance share is assumed equal to 2026's. Source: a capex plan by project.\n"
        "- Revolver access: covenant headroom and borrowing conditions not disclosed (G34). Effect: availability is not unconditional. Source: the compliance certificate.\n"
        "- Definition: this runway counts lease payments and covers 12 months; the Front Pages' runway excludes rent and runs to December 2027."
    )
    return h
