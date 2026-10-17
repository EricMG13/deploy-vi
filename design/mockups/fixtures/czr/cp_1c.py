"""CZR CP-1C: peer benchmark. MGM and PENN figures are real (Q2 2026 releases); Peer C, D and E are anonymised
synthetic operators added so the range strip has meaningful quartiles; every peer EV/EBITDA multiple is synthetic
because the pack has no market capitalisation or EV data. CZR is shown at the real merger value."""

from __future__ import annotations

from decimal import Decimal

from core import GAP, Ctx, D, Handoff, compute, plain, q
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
SYN = {
    # peer: (Q2 2026 revenue, Q2 2025 revenue, Q2 2026 Adjusted EBITDA, EV/EBITDA multiple), all invented
    "Peer C (synthetic)": (D("1120.0"), D("1081.0"), D("353.0"), D("7.0")),
    "Peer D (synthetic)": (D("960.0"), D("913.5"), D("353.0"), D("9.6")),
    "Peer E (synthetic)": (D("1640.0"), D("1612.3"), D("367.0"), D("8.1")),
}
MULT = {
    "MGM Resorts International": D("7.4"),
    "PENN Entertainment, Inc.": D("8.9"),
    **{k: v[3] for k, v in SYN.items()},
}
BASIS = {
    "Peer C (synthetic)": "Regional gaming operator",
    "Peer D (synthetic)": "Las Vegas locals gaming operator",
    "Peer E (synthetic)": "Las Vegas Strip resort operator",
}


def _peer_data(ctx: Ctx) -> dict[str, dict]:
    """Per peer: revenue and Adjusted EBITDA for Q2 2026, revenue Q2 2025 (US$ m)."""
    out = {
        "MGM Resorts International": {
            "rev": ctx.val("mgm_revenues_q2_2026") / 1000,
            "rev0": ctx.val("mgm_revenues_q2_2025") / 1000,
            "ebitda": ctx.val("mgm_adj_ebitda_q2_2026") / 1000,
            "real": True,
            "keys": ("mgm_revenues_q2_2026", "mgm_revenues_q2_2025", "mgm_adj_ebitda_q2_2026"),
        },
        "PENN Entertainment, Inc.": {
            "rev": ctx.val("penn_revenues_q2_2026"),
            "rev0": ctx.val("penn_revenues_q2_2025"),
            "ebitda": ctx.val("penn_adj_ebitda_q2_2026"),
            "real": True,
            "keys": ("penn_revenues_q2_2026", "penn_revenues_q2_2025", "penn_adj_ebitda_q2_2026"),
        },
    }
    for name, (r, r0, e, _m) in SYN.items():
        out[name] = {"rev": r, "rev0": r0, "ebitda": e, "real": False, "keys": ()}
    for v in out.values():
        v["margin"], v["margin_calc"] = compute(
            "Adjusted EBITDA margin", "e / r * 100", 1, "%", e=v["ebitda"], r=v["rev"]
        )
        v["growth"], v["growth_calc"] = compute(
            "revenue growth", "r / r0 * 100 - 100", 1, "%", r=v["rev"], r0=v["rev0"]
        )
    return out


def _quartile(vals: list[Decimal], p: Decimal) -> Decimal:
    """Linear-interpolation percentile (the 'inclusive' method)."""
    s = sorted(vals)
    pos = (len(s) - 1) * p
    lo = int(pos)
    frac = pos - lo
    return s[lo] if frac == 0 else s[lo] + (s[lo + 1] - s[lo]) * frac


def _stats(vals: list[Decimal], places: int) -> dict[str, Decimal]:
    return {
        "min": q(min(vals), places),
        "q1": q(_quartile(vals, Decimal("0.25")), places),
        "median": q(_quartile(vals, Decimal("0.5")), places),
        "q3": q(_quartile(vals, Decimal("0.75")), places),
        "max": q(max(vals), places),
    }


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-1C", "CZR", run_id, "2026-10-02", ["CP-0", "CP-1"], fixture_file="czr/cp_1c.py"
    )
    h.qa("Restricted")
    syn_peers = h.cite_synthetic(
        "peers_c_to_e",
        "The pack holds only MGM and PENN, so three anonymised regional and Las Vegas operators with plausible Q2 results were invented to give the range strip real quartiles.",
        "Caesars",
    )
    syn_mult = h.cite_synthetic(
        "peer_multiples",
        "The pack has no market capitalisation or EV for any peer, so each EV/EBITDA multiple is a plausible lease-inclusive trading multiple for a US gaming operator.",
        "Caesars",
    )
    data = _peer_data(ctx)
    names = list(data)

    # ---- peer set
    avail = {
        "MGM Resorts International": (
            "Partial",
            "Large US operator with Las Vegas Strip and regional assets",
            "Q2 2026 revenue, Adjusted EBITDA and operating income; no cash-flow or EV data.",
        ),
        "PENN Entertainment, Inc.": (
            "Partial",
            "US regional casino and online operator",
            "Q2 2026 revenue, Adjusted EBITDA, capex and liquidity; triple-net rent reported separately.",
        ),
        "Peer C (synthetic)": (
            "Close",
            "Regional gaming operator of similar margin profile (invented)",
            "Synthetic Q2 revenue and Adjusted EBITDA.",
        ),
        "Peer D (synthetic)": (
            "Partial",
            "Las Vegas locals operator, higher margin (invented)",
            "Synthetic Q2 revenue and Adjusted EBITDA.",
        ),
        "Peer E (synthetic)": (
            "Partial",
            "Las Vegas Strip operator, lease-heavy (invented)",
            "Synthetic Q2 revenue and Adjusted EBITDA.",
        ),
    }
    rows = []
    for n in names:
        comp, basis, av = avail[n]
        marks = (
            join_marks(*(h.cite_fig(k) for k in data[n]["keys"])) if data[n]["real"] else syn_peers
        )
        rows.append(
            {
                "peer": n,
                "selection_basis": basis,
                "comparability": comp,
                "data_availability": av,
                "cite": marks,
            }
        )
    h.table("cp1c.peer_set", rows)

    # ---- peer metrics
    rows = []
    for n in names:
        v = data[n]
        real = v["real"]
        base = join_marks(*(h.cite_fig(k) for k in v["keys"])) if real else syn_peers
        note_e = (
            "Issuer-defined Adjusted EBITDA; definitions and lease treatment are not harmonised."
            if real
            else "Invented; definition mirrors the issuer-defined measure."
        )
        rows += [
            {
                "peer": n,
                "metric_id": "revenue",
                "value": plain(q(v["rev"], 1)),
                "unit_label": "US$ m",
                "period": "Q2 2026",
                "currency": "USD",
                "definition_note": "Reported consolidated revenue." if real else "Invented.",
                "cite": base,
            },
            {
                "peer": n,
                "metric_id": "adjusted_ebitda",
                "value": plain(q(v["ebitda"], 1)),
                "unit_label": "US$ m",
                "period": "Q2 2026",
                "currency": "USD",
                "definition_note": note_e,
                "cite": base,
            },
            {
                "peer": n,
                "metric_id": "adjusted_ebitda_margin_pct",
                "value": plain(v["margin"], 1),
                "unit_label": "%",
                "period": "Q2 2026",
                "currency": "USD",
                "definition_note": "Adjusted EBITDA over revenue.",
                "cite": f"{base} {v['margin_calc']}",
            },
            {
                "peer": n,
                "metric_id": "revenue_growth_pct",
                "value": plain(v["growth"], 1),
                "unit_label": "%",
                "period": "Q2 2026",
                "currency": "USD",
                "definition_note": "Against Q2 2025.",
                "cite": f"{base} {v['growth_calc']}",
            },
        ]
    h.table("cp1c.peer_metrics", rows)

    # ---- borrower and positioning
    czr_margin, c_m = compute(
        "Adjusted EBITDA margin",
        "e / r * 100",
        1,
        "%",
        e=ctx.val("adj_ebitda_q2_2026"),
        r=ctx.val("net_revenues_q2_2026"),
    )
    czr_growth, c_g = compute(
        "revenue growth",
        "r / r0 * 100 - 100",
        1,
        "%",
        r=ctx.val("net_revenues_q2_2026"),
        r0=ctx.val("net_revenues_q2_2025"),
    )
    ltm = ctx.val("ltm_adj_ebitda_q2_2026")
    ev_merger = ctx.val("ev_merger_usdm")
    fin = ctx.val("lt_financing_obligations_2026_06_30")
    ev_lease, c_ev = compute(
        "EV including lease financing obligations", "ev + fin", 0, "", ev=ev_merger, fin=fin
    )
    czr_mult, c_mult = compute(
        "lease-inclusive EV / LTM Adjusted EBITDA", "ev / ebitda", 2, "x", ev=ev_lease, ebitda=ltm
    )
    czr_marks = join_marks(
        h.cite_fig("adj_ebitda_q2_2026"),
        h.cite_fig("net_revenues_q2_2026"),
        h.cite_fig("net_revenues_q2_2025"),
    )
    mult_vals = [MULT[n] for n in names]
    pos = []
    spec = [
        (
            "adjusted_ebitda_margin_pct",
            "%",
            czr_margin,
            [data[n]["margin"] for n in names],
            1,
            f"{czr_marks} {c_m}",
            "Caesars' reported margin is above the peer median, but issuer definitions and lease treatment differ: a screening signal, not a ranking.",
        ),
        (
            "revenue_growth_pct",
            "%",
            czr_growth,
            [data[n]["growth"] for n in names],
            1,
            f"{czr_marks} {c_g}",
            "Growth is below the peer median and includes the Windsor consolidation, so organic growth is lower still.",
        ),
        (
            "ev_ebitda_x",
            "x",
            czr_mult,
            mult_vals,
            2,
            f"{h.cite_fig('merger_transaction_value')} {h.cite_fig('lt_financing_obligations_2026_06_30')} {c_ev} {c_mult} {syn_mult}",
            "Counting the lease financing obligations, the take-private is priced above the peer median; peer multiples are synthetic.",
        ),
    ]
    for mid, unit, bv, vals, places, cite, impl in spec:
        st = _stats(vals, places)
        pos.append(
            {
                "metric_id": mid,
                "unit_label": unit,
                "borrower_value": plain(bv, places),
                "peer_min": plain(st["min"], places),
                "peer_q1": plain(st["q1"], places),
                "peer_median": plain(st["median"], places),
                "peer_q3": plain(st["q3"], places),
                "peer_max": plain(st["max"], places),
                "n": str(len(vals)),
                "position": "Above"
                if bv > st["median"]
                else "Below"
                if bv < st["median"]
                else "In line",
                "credit_implication": impl,
                "cite": f"{cite} {syn_peers}" if mid != "ev_ebitda_x" else cite,
            }
        )
    h.table("cp1c.positioning", pos)
    mstats = _stats(mult_vals, 2)

    # ---- valuation multiples
    czr_ev_rev, c_evr = compute(
        "EV / LTM revenue",
        "ev / rev",
        2,
        "x",
        ev=ev_merger,
        rev=ctx.val("ltm_net_revenues_q2_2026"),
    )
    czr_ev_x, c_evx = compute(
        "EV / LTM Adjusted EBITDA", "ev / ebitda", 2, "x", ev=ev_merger, ebitda=ltm
    )
    low, c_lo = compute(
        "implied EV at peer Q1", "mult * ebitda", 0, "", mult=mstats["q1"], ebitda=ltm
    )
    med, c_me = compute(
        "implied EV at peer median", "mult * ebitda", 0, "", mult=mstats["median"], ebitda=ltm
    )
    high, c_hi = compute(
        "implied EV at peer Q3", "mult * ebitda", 0, "", mult=mstats["q3"], ebitda=ltm
    )
    vm = [
        {
            "entity": "Caesars Entertainment, Inc. (merger value)",
            "basis": "Transaction",
            "ev": plain(ev_merger),
            "ev_ebitda_x": plain(czr_ev_x, 2) + "x",
            "ev_revenue_x": plain(czr_ev_rev, 2) + "x",
            "implied_ev_low": GAP,
            "implied_ev_median": GAP,
            "implied_ev_high": GAP,
            "currency": "USD",
            "unit": "MILLIONS",
            "period": "LTM Q2 2026",
            "cite": join_marks(
                h.cite_fig("merger_transaction_value"),
                h.cite_fig("ltm_adj_ebitda_q2_2026"),
                h.cite_fig("ltm_net_revenues_q2_2026"),
            )
            + f" {c_evx}",
        },
        {
            "entity": "Caesars Entertainment, Inc. (including lease financing obligations)",
            "basis": "Analyst",
            "ev": plain(ev_lease),
            "ev_ebitda_x": plain(czr_mult, 2) + "x",
            "ev_revenue_x": GAP,
            "implied_ev_low": plain(low),
            "implied_ev_median": plain(med),
            "implied_ev_high": plain(high),
            "currency": "USD",
            "unit": "MILLIONS",
            "period": "LTM Q2 2026",
            "cite": join_marks(
                h.cite_fig("merger_transaction_value"),
                h.cite_fig("lt_financing_obligations_2026_06_30"),
                h.cite_fig("ltm_adj_ebitda_q2_2026"),
                syn_mult,
            )
            + f" {c_mult}",
        },
    ]
    for n in names:
        e4, c_e4 = compute(
            "EV from the synthetic multiple",
            "mult * 4 * ebitda",
            0,
            "",
            mult=MULT[n],
            ebitda=data[n]["ebitda"],
        )
        vm.append(
            {
                "entity": n,
                "basis": "Trading",
                "ev": plain(e4),
                "ev_ebitda_x": plain(MULT[n], 2) + "x",
                "ev_revenue_x": GAP,
                "implied_ev_low": GAP,
                "implied_ev_median": GAP,
                "implied_ev_high": GAP,
                "currency": "USD",
                "unit": "MILLIONS",
                "period": "Q2 2026 annualised",
                "cite": f"{syn_mult} {c_e4}",
            }
        )
    h.table("cp1c.valuation_multiples", vm)

    text = (
        "Caesars sits above the peer median on reported Adjusted EBITDA margin and below it on revenue growth, but the peer set is small and the measures are not aligned, so this is a screening comparison and not a ranking. "
        f"Caesars' Q2 2026 margin was {plain(czr_margin, 1)}% on US$2,993m of revenue and US$920m of Adjusted EBITDA; MGM reported US$4,451m and US$610m (13.7%) {{1, 2}} and PENN US$1,857m and US$313m (16.8%) {{4, 5}}. "
        "Peers C, D and E are invented, labelled synthetic, and added so the ranges have quartiles.\n\n"
        "A higher margin is not evidence of better debt service. Caesars' Adjusted EBITDA is before rent on its financing-obligation leases, MGM and PENN treat leases and EBITDAR differently, and no matched cash-flow or leverage data exist for the peers. "
        "MGM reported Q2 operating income of US$503.6m {3}; PENN reported capex of US$97.5m {6} and total liquidity of US$1.9bn at 30 June {7}. Relative leverage cannot be inferred from these isolated amounts.\n\n"
        "Market context is limited to 1 October last-trade yields: 9.32% on the Caesars 6.00% unsecured 2032s {10}, 8.06% on the secured 2032s {11}, 6.72% on MGM's 6.125% 2029s {9} and 6.64% on PENN's 4.125% 2029s {8}. They are not spreads and differ in maturity, security and rating, so they are context only.\n\n"
        f"Valuation. At the merger's stated US$17.6bn the take-private is {plain(czr_ev_x, 2)}x LTM Adjusted EBITDA. That figure leaves out the US$13.2bn of lease financing obligations; counting them gives {plain(czr_mult, 2)}x, above the synthetic peer median of {plain(mstats['median'], 2)}x. "
        "The peer multiples are synthetic test values because no peer market capitalisation or EV is in the pack (and no transaction comparables), so the implied EV range is illustrative."
    )
    h.analysis(caos_text(h, FOLDER, "CP-1C", text))
    h.gaps(
        "- Peer universe: the pack supports only MGM and PENN; Peers C, D and E are invented. Effect: quartiles are test values for the layout. Source: a researched peer set with filings.\n"
        "- Peer EV and multiples: no market capitalisation or transaction comparables for any peer; every peer multiple is synthetic. Effect: implied EV is illustrative. Source: an equity value export for the peers.\n"
        "- Definitions: Adjusted EBITDA and lease treatment differ across issuers and no bridge is supplied. Effect: margins are directional.\n"
        "- Cash flow: no matched peer FCF, working capital or leverage. Effect: cash conversion and leverage are not compared."
    )
    return h
