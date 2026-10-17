"""Larchmere CP-3: relative value and security selection (synthetic quotes, peers and talk; yields and discount margins computed)."""

from __future__ import annotations

from core import GAP, Ctx, D, Handoff, compute, fpct, plain

from . import derived as X
from . import facts as F
from .facts import syn

NAMES = {
    "llg_tlb": "First-Lien Term Loan B",
    "llg_2l": "Second-Lien Term Loan",
    "llg_notes": "8.25% Senior Notes due 2029",
}
VAL = {
    "llg_tlb": "V3 - Fair",
    "llg_2l": "V3 - Fair",
    "llg_notes": "V4 - Unattractive",
    "NEW-1": "V2 - Attractive",
}


def talk() -> dict:
    nm = F.val("new_money")
    out = {}
    for k in ("low", "mid", "high"):
        dm, s = compute(
            f"implied 3-year DM at {k} talk",
            "spread + (100 - oid) / 3 * 100",
            0,
            "",
            spread=nm[f"spread_{k}"],
            oid=nm["oid"],
        )
        out[k] = (dm, s)
    return out


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-3",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1", "MODEL", "CP-2H", "CP-3C", "CP-3D", "CP-4", "CP-4C"],
        fixture_file="larchmere/cp_3.py",
    )
    h.qa("Restricted")
    mk = X.market()
    cp3d = ctx.get(run_id, "CP-3D")
    assert cp3d.rows("cp3d.observations")
    m_q, m_w, m_terms, m_new, m_peers, m_hist, m_ev, m_rec = (
        syn(h, k)
        for k in (
            "quotes",
            "bid_ask_width",
            "facility_terms",
            "new_money",
            "peers",
            "quote_history",
            "ev_multiples",
            "recoveries_market",
        )
    )
    exp = X.expected_recovery()
    cls = {"llg_tlb": "C2-1L", "llg_2l": "C3-2L", "llg_notes": "C4-NOTES"}
    tk = talk()
    levels = []
    for fid in ("llg_tlb", "llg_2l", "llg_notes"):
        t = F.val("facility_terms")[fid]
        r = mk[fid]
        w = D(F.val("bid_ask_width")[fid])
        bid, _ = compute("bid", "mid - w / 2", 1, "", mid=r["price"], w=w)
        ask, _ = compute("ask", "mid + w / 2", 1, "", mid=r["price"], w=w)
        e = exp[cls[fid]][0]
        notes = fid == "llg_notes"
        levels.append(
            {
                "facility_id": fid,
                "instrument": NAMES[fid],
                "level_basis": "Market",
                "level_date": "2026-10-01",
                "bid": plain(bid),
                "ask": plain(ask),
                "mid": plain(r["price"]),
                "spread_or_coupon": "8.25%" if notes else f"S+{t['spread']}",
                "metric_basis": "STW" if notes else "3Y DM",
                "yield_or_dm": plain(r["spread"]),
                "oid": None,
                "valuation": VAL[fid],
                "rationale": f"Price {plain(r['price'])} against a probability-weighted recovery of {plain(e, 1)}%: "
                + (
                    "the market pays for more upside than the scenarios support."
                    if e < r["price"]
                    else "the market discount is wider than the expected loss."
                ),
                "cite": f"{m_q}{m_w}{m_terms}{m_ev} {exp[cls[fid]][1]}",
            }
        )
    nm = F.val("new_money")
    levels.append(
        {
            "facility_id": "NEW-1",
            "instrument": "Proposed new-money first-out term loan (indicative)",
            "level_basis": "Talk",
            "level_date": nm["talk_date"],
            "bid": None,
            "ask": None,
            "mid": None,
            "spread_or_coupon": f"S+{nm['spread_low']}-{nm['spread_high']}",
            "metric_basis": "3Y DM",
            "yield_or_dm": plain(tk["mid"][0]),
            "oid": plain(nm["oid"]),
            "valuation": VAL["NEW-1"],
            "rationale": "Talk of S+950-1,050 at 96 ranks ahead of 1,250 of first-lien debt and prices inside the existing term loan B.",
            "cite": f"{m_new} {tk['mid'][1]}",
        }
    )
    h.table("snapshot.instrument_levels", levels)
    sofr = D(F.val("sofr_spot"))
    rf = D(F.val("risk_free_3y"))
    hist = F.val("quote_history")
    rv = []
    for p in F.val("peers").values():
        loan = p["block"].startswith("Loan")
        yld, ys = compute(
            "yield", "base + spread / 100", 1, "", base=sofr if loan else rf, spread=p["spread"]
        )
        rv.append(
            {
                "block": p["block"],
                "name": p["name"],
                "bloomberg_id": GAP,
                "ratings": p["ratings"],
                "size": GAP,
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": p["coupon"],
                "maturity_date": p["maturity"],
                "seniority": "First lien" if loan else "Senior unsecured",
                "price": plain(p["price"]),
                "chg_1m": plain(p["chg_1m"]),
                "chg_ytd": plain(p["chg_ytd"]),
                "yield_pct": fpct(yld, 1),
                "spread_or_dm_bps": plain(p["spread"]),
                "market_value": GAP,
                "level_date": "2026-10-01",
                "cite": f"{m_peers} {ys}",
            }
        )
    for fid, block in (("llg_tlb", "Loan comparable"), ("llg_notes", "HY comparable")):
        r, t = mk[fid], F.val("facility_terms")[fid]
        notes = fid == "llg_notes"
        size = X.facility_balance(fid, "JUN30_2026")
        mv, mvs = compute("market value", "size * price / 100", 1, "", size=size, price=r["price"])
        c1, c1s = compute(
            "one-month change",
            "price - prior",
            1,
            "",
            price=r["price"],
            prior=hist[fid]["one_month"],
        )
        cy, cys = compute(
            "year-to-date change",
            "price - open",
            1,
            "",
            price=r["price"],
            open=hist[fid]["ytd_open"],
        )
        yld, yls = (
            (r["yld"], r["yld_s"])
            if notes
            else compute("yield", "base + spread / 100", 1, "", base=sofr, spread=r["spread"])
        )
        rv.append(
            {
                "block": block,
                "name": NAMES[fid] + " (Larchmere)",
                "bloomberg_id": F.val("identifiers")[fid][0],
                "ratings": " / ".join(F.val("ratings")["facility"][fid]),
                "size": plain(size),
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": "8.25%" if notes else f"S+{t['spread']}",
                "maturity_date": t["maturity"],
                "seniority": "Senior unsecured" if notes else "First lien",
                "price": plain(r["price"]),
                "chg_1m": plain(c1),
                "chg_ytd": plain(cy),
                "yield_pct": fpct(yld, 1),
                "spread_or_dm_bps": plain(r["spread"]),
                "market_value": plain(mv),
                "level_date": "2026-10-01",
                "cite": f"{m_q}{m_hist}{m_terms} {mvs} {yls}",
            }
        )
    h.table("snapshot.relative_value", rv)
    comp_ = talk()
    tlb_dm = mk["llg_tlb"]["spread"]
    h.table(
        "cp3.talk_valuation",
        [
            {
                "facility_id": "NEW-1",
                "talk_stage": "Initial talk",
                "talk_low": plain(nm["spread_low"]),
                "talk_mid": plain(nm["spread_mid"]),
                "talk_high": plain(nm["spread_high"]),
                "oid": plain(nm["oid"]),
                "metric_basis": "3Y DM",
                "implied_low": plain(comp_["low"][0]),
                "implied_mid": plain(comp_["mid"][0]),
                "implied_high": plain(comp_["high"][0]),
                "comparable_level": plain(tlb_dm),
                "comparable_basis": "Existing first-lien term loan B at 74 (3Y DM, dealer quote)",
                "verdict": VAL["NEW-1"],
                "cite": f"{m_new}{m_q} {comp_['mid'][1]}",
            }
        ],
    )
    comp = {
        "llg_tlb": (
            "Senior secured first lien, 1 of 4",
            "Medium",
            "Adequate",
            "CCC loan index and Peer C, Peer D loans",
        ),
        "llg_2l": ("Second lien, 2 of 4", "High", "Inadequate", "CCC loan index"),
        "llg_notes": (
            "Senior unsecured, 3 of 4",
            "High",
            "Inadequate",
            "CCC high-yield index, Peer E and Peer F notes",
        ),
        "NEW-1": (
            "Super-priority first-out, ahead of all existing debt",
            "Low",
            "Attractive",
            "Existing term loan B",
        ),
    }
    h.table(
        "cp3.compensation",
        [
            {
                "facility_id": f,
                "structural_rank": r_,
                "recovery_sensitivity": s,
                "compensation_vs_risk": c,
                "comparables": cp,
                "cite": f"{m_peers}{m_q}{m_rec}",
            }
            for f, (r_, s, c, cp) in comp.items()
        ],
    )
    pref = {
        "llg_tlb": (
            "Preferred",
            "The best compensated existing instrument: expected recovery above the price and the first claim on the base-case fulcrum.",
            "A second maintenance covenant breach or a priming loan that is not offered to all lenders.",
        ),
        "llg_2l": (
            "Avoid",
            "Fulcrum in the base case but priced above its probability-weighted recovery; binary outcome.",
            "Evidence the sponsor will fund the cure or that the lessor concedes rent.",
        ),
        "llg_notes": (
            "Avoid",
            "Zero recovery in the base case; the price is an option on the high case.",
            "A change in plan class or a standstill that preserves value for the notes.",
        ),
        "NEW-1": (
            "Requires more work",
            "Terms are talk only, with no commitment papers and no sponsor equity alongside.",
            "Final terms, security package and lender-group support.",
        ),
    }
    h.table(
        "cp3.security_preference",
        [
            {
                "facility_id": f,
                "preference": p_,
                "key_reason": r_,
                "monitoring_trigger": t_,
                "cite": f"{m_q}{m_new}{m_rec}",
            }
            for f, (p_, r_, t_) in pref.items()
        ],
    )
    t, n2 = exp["C2-1L"][0], exp["C3-2L"][0]
    upside, up_s = compute(
        "expected recovery above price",
        "recovery - price",
        1,
        "",
        recovery=t,
        price=mk["llg_tlb"]["price"],
    )
    h.analysis(
        f"The first-lien term loan B at 74 is the best-compensated existing instrument: its probability-weighted recovery is {plain(t, 1)}% ({exp['C2-1L'][1]}), {plain(upside, 1)} points above the price ({up_s}), while the second lien at 41 is worth {plain(n2, 1)}% and the notes at 23 are worth {plain(exp['C4-NOTES'][0], 1)}% {m_q}. "
        f"The new-money first-out loan at talk of S+950-1,050 with a 96 OID implies a 3-year discount margin of {plain(comp_['low'][0])} to {plain(comp_['high'][0])} bps, inside the existing term loan B at {plain(tlb_dm)} bps despite ranking ahead of it ({comp_['mid'][1]}) {m_new}. "
        "Module view: the term loan B is preferred among the existing debt and the new money looks attractive at talk, but the talk is not a market level. Confidence is Medium-Low.\n\n"
        f"The Valuations are V3 - Fair for the term loan B and second lien and V4 - Unattractive for the notes, because the notes price on the option value of the high case and the second lien at 41 pays for upside the scenarios do not give it. Dealer quotes are from one file dated 1 October 2026 and are Current {m_w}.\n\n"
        f"The relative-value blocks place the Larchmere loan against a CCC loan index at 72.5 and two synthetic loan peers at 78.5 and 69.0, and the notes against a CCC high-yield index at 64 and two synthetic bonds at 52 and 37 {m_peers}. Larchmere's notes at 23 are the cheapest and the weakest in the set."
    )
    h.gaps(
        "- Talk is not a market level: NEW-1 has no commitment papers, so its Valuation is conditional. Lifted by: final terms from the sponsor.\n"
        "- Revolver: no quote exists for the fully drawn revolver, so no priced row is shown.\n"
        "- Peers: the index levels and Peers C to F are synthetic; they are labelled and not traced to a vendor file."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
