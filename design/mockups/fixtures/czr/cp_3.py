"""CZR CP-3: relative value and security selection.

Real first: the two 2032 notes and the MGM and PENN comparables are real FINRA TRACE last trades (base data C228-C263);
the secured and unsecured yield difference, the CAOS wording and the "Requires More Work" outcome are real. Synthetic
and marked: the term-loan dealer marks (`synthetic-facts.json -> czr.loan_marks`), the Treasury used for spreads
(`czr.spreads`), the SOFR deck, the index rows and two anonymised loan comparables, and the new merger tranches at
Price Talk (`czr.merger_tranches`, Primary runs only). Valuation, compensation and preference are the illustrative
layer (the real CAOS CP-3 reached Requires More Work for both priced notes and marked no instrument Preferred).

This module also holds the small shared helpers the other part-2 modules import (facts file, markers, dates, 3Y DM).
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from core import GAP, Ctx, D, Handoff, compute, plain, q
from helpers import caos_text, join_marks
from run import years_between

FOLDER = "full-credit-assessment-2026-10-06"
RV_FOLDER = "relative-value-2026-10-12"
FACTS_PATH = Path(__file__).resolve().parent.parent / "synthetic-facts.json"
FACTS: dict = json.loads(FACTS_PATH.read_text(encoding="utf-8"))["czr"]
TRANCHES: dict[str, dict] = {t["tranche_id"]: t for t in FACTS["merger_tranches"]["tranches"]}
AS_OF = "2026-10-02"
LEVEL_DATE = "2026-10-01"  # the TRACE last-trade date and the loan-mark date
TREASURY = D(FACTS["spreads"]["treasury_6y_pct"])
SOFR = D(FACTS["rate_deck"]["base"]["FY2026"])

# Real TRACE notes: facility id -> (figure-key stem, short name, seniority text)
NOTES = {
    "cei_secured_2032": (
        "trace_czr_12769gac4",
        "CEI 6.50% Senior Secured Notes due 2032",
        "Senior secured",
    ),
    "cei_unsecured_2032": (
        "trace_czr_12769gad2",
        "CEI 6.00% Senior Notes due 2032",
        "Senior unsecured",
    ),
}
PEERS = {
    "mgm": ("trace_mgm_552953ck5", "MGM Resorts 6.125% Senior Notes due 2029", "Senior unsecured"),
    "penn": (
        "trace_penn_707569av1",
        "PENN Entertainment 4.125% Senior Notes due 2029",
        "Not established",
    ),
}
# Loans with a synthetic dealer mark: facility id -> (marks key, short name, margin bps, floor)
LOANS = {
    "cei_term_b": ("CEI Term Loan B", "CEI Term Loan B", Decimal(225)),
    "cei_term_b1": ("CEI Term Loan B-1", "CEI Term Loan B-1", Decimal(225)),
    "cei_term_a": ("CEI Term Loan A", "CEI Term Loan A", Decimal(235)),
}

# Synthetic values introduced here (everything else synthetic is read from synthetic-facts.json).
SYNTHETIC: dict[str, tuple[str, str]] = {
    "loan_index_bb_dm": (
        "235",
        "A BB-rated leveraged-loan index sits near SOFR + 235 bps of 3-year discount margin in a stable market.",
    ),
    "loan_index_b_dm": (
        "340",
        "A B-rated leveraged-loan index trades about 100 bps wider than the BB index.",
    ),
    "hy_index_bb_yield": (
        "6.55",
        "A BB high-yield index yields about 245 bps over a 4.10% Treasury, in line with the synthetic benchmark.",
    ),
    "hy_index_b_yield": (
        "7.75",
        "A B high-yield index sits about 120 bps wider than the BB index.",
    ),
    "hy_index_ccc_yield": (
        "12.10",
        "A CCC high-yield index yields roughly 800 bps over Treasuries in a firm market.",
    ),
    "loan_comp_1": (
        "99.60",
        "An anonymised BB- gaming term loan priced near par at SOFR + 225 bps, matching the CEI term loans' margin.",
    ),
    "loan_comp_2": (
        "98.90",
        "An anonymised B+ gaming term loan priced a point under par at SOFR + 300 bps, a notch weaker than Caesars.",
    ),
}


# ---------------------------------------------------------------------------------------------- helpers
def num(d: Decimal | int | str, places: int | None = None) -> str:
    """Prose number with thousands separators ('2,928', '125.4878'); tables use `plain()`."""
    v = D(d)
    if places is not None:
        v = q(v, places)
    t = f"{v:,f}"
    if places is None and "." in t:
        t = t.rstrip("0").rstrip(".")
    return t


def carry(h: Handoff, src: Handoff, text: str) -> str:
    """Re-cite in `h` every [C<n>] marker of a cell taken from another handoff `src` (the other text is kept)."""

    def sub(m: re.Match[str]) -> str:
        c = src.citations[int(m.group(1)) - 1]
        return h.cite_from_source({**c, "module": src.module_id, "citation_id": c["id"]})

    return re.sub(r"\[C(\d+)\]", sub, text)


def markers(*cites: str) -> str:
    """The distinct [C<n>] markers inside any cite strings (a calc: string keeps its inputs' markers)."""
    return join_marks(*cites)


def mk_fig(h: Handoff, key: str) -> str:
    """Markers only of the citation behind a base/Front Pages figure key."""
    return markers(h.cite_fig(key))


def fig(ctx: Ctx, key: str) -> Decimal:
    return ctx.val(key)


def us_date(s: str) -> str:
    """'2/15/2032' -> '2032-02-15'."""
    return datetime.strptime(s.strip(), "%m/%d/%Y").date().isoformat()


def coupon_txt(d: Decimal) -> str:
    """'6.50' / '4.625' / '7.00': at least two decimals, no padding beyond the figure."""
    t = plain(d)
    if "." not in t:
        return t + ".00"
    return t + "0" if len(t.split(".")[1]) == 1 else t


def cite_fact(h: Handoff, section: str, sub: str | None = None, text: str | None = None) -> str:
    """A synthetic citation for `synthetic-facts.json -> czr.<section>[.<sub>]` (rationale from the facts file)."""
    rationale = text or FACTS[section]["rationale"]
    key = f"czr.{section}" + (f".{sub}" if sub else "")
    return h.cite_synthetic(key, rationale, "Caesars", file="synthetic-facts.json")


def cite_syn(h: Handoff, key: str) -> str:
    """A synthetic citation for a value in this module's SYNTHETIC dict."""
    return h.cite_synthetic(key, SYNTHETIC[key][1], "Caesars", file="czr/cp_3.py")


def is_primary(ctx: Ctx, run_id: str) -> bool:
    """Whether the run is Primary: the run's own flag (set from `RUNS` by the Run), not its variant name."""
    return ctx.primary_runs[run_id]


def merger_debt_tail(ctx: Ctx, run_id: str) -> str:
    """The one sentence that follows every statement that the merger debt is not stated (G8): Primary runs add that
    the run uses three synthetic tranches in its place; other runs add nothing."""
    return (
        " This test run uses three synthetic tranches in its place."
        if is_primary(ctx, run_id)
        else ""
    )


def post_close_leverage(ctx: Ctx, run_id: str) -> str:
    """How post-close leverage stands: unknown without the tranches, a test value with them."""
    if is_primary(ctx, run_id):
        return "post-close leverage rests on the synthetic tranches"
    return "post-close leverage unknown"


def tranche_rows(ctx: Ctx, run_id: str) -> list[dict]:
    """The Run Brief's transaction summary rows (empty unless the run is Primary)."""
    return ctx.get(run_id, "RUN_BRIEF").rows("snapshot.transaction_summary")


def cp1_facilities(ctx: Ctx, run_id: str) -> dict[str, dict]:
    """CP-1 facility register rows at the latest balance-sheet period, by facility id."""
    return {
        r["facility_id"]: r
        for r in ctx.get(run_id, "CP-1").rows("cp1.debt_facility_register")
        if r["period_id"] == "JUN30_2026"
    }


def loan_mark(h: Handoff, name: str) -> dict:
    """Mid and cite of a synthetic loan mark from the facts file."""
    m = FACTS["loan_marks"]["facilities"][name]
    bid, ask = D(m["bid"]), D(m["ask"])
    mid, mid_s = compute(f"{name} mid", "(bid + ask) / 2", 3, bid=bid, ask=ask)
    return {
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "mid_calc": mid_s,
        "floor": m["floor_pct"],
        "cite": cite_fact(h, "loan_marks", name),
    }


def loan_dm(name: str, margin_bps: Decimal, mid: Decimal) -> tuple[Decimal, str]:
    """3-year discount margin (bps) from margin and mid price: margin + (100 - mid) / 3 years x 100."""
    return compute(
        f"{name} 3Y discount margin",
        "margin + (100 - mid) / 3 * 100",
        0,
        margin=margin_bps,
        mid=mid,
    )


def spread_to_treasury(label: str, yield_pct: Decimal) -> tuple[Decimal, str]:
    """Spread-to-worst proxy in bps: (yield - synthetic 6-year Treasury) x 100."""
    return compute(
        f"{label} spread over the synthetic Treasury", "(y - t) * 100", 0, y=yield_pct, t=TREASURY
    )


def approx_ytm(label: str, coupon: Decimal, oid: Decimal, years: Decimal) -> tuple[Decimal, str]:
    """Approximate yield to maturity (percent): (coupon + (100 - oid) / years) / ((100 + oid) / 2) x 100."""
    return compute(
        f"{label} approximate yield to maturity",
        "(coupon + (100 - oid) / years) / ((100 + oid) / 2) * 100",
        3,
        "",
        coupon=coupon,
        oid=oid,
        years=years,
    )


def verdict_for(pickup_bps: Decimal) -> str:
    """Valuation word from the pickup (bps) of a level over its comparable: the rule is stated in the module text."""
    if pickup_bps >= 50:
        return "V2 - Attractive"
    if pickup_bps > -50:
        return "V3 - Fair"
    if pickup_bps > -150:
        return "V4 - Unattractive"
    return "V5 - Very unattractive"


def talk_valuation(ctx: Ctx, h: Handoff, tr: dict, comps: dict) -> dict:
    """Calculated talk valuation of one new tranche (low, mid, high with OID) against its comparable level."""
    t = TRANCHES[tr["tranche_id"]]
    oid = D(t["oid"])
    syn = cite_fact(h, "merger_tranches", t["tranche_id"])
    if t["debt_type"] == "Term loan":
        basis, scale = "3Y DM", 1
        talk = [t["talk_low_bps"], t["talk_mid_bps"], t["talk_high_bps"]]
        implied = [loan_dm_talk(D(x), oid) for x in talk]
        comp_level = comps["loan"][0]
        comp_basis = "CEI Term Loan B-1 3Y DM (synthetic dealer mark)"
        comp_cite = comps["loan_cite"]
    else:
        basis, scale = "YTW", 100
        talk = [t["talk_low_pct"], t["talk_mid_pct"], t["talk_high_pct"]]
        years = years_between(AS_OF, t["maturity_date"])
        implied = [approx_ytm(f"{t['tranche_id']} talk", D(x), oid, years) for x in talk]
        key = "cei_unsecured_2032" if "unsecured" in t["debt_type"].lower() else "cei_secured_2032"
        comp_level = comps[key][0]
        comp_basis = f"{NOTES[key][1]} TRACE last-trade yield"
        comp_cite = comps[key + "_cite"]
    mid = implied[1][0]
    pk, pk_calc = compute(
        f"{t['tranche_id']} pickup over its comparable (bps)",
        "(mid - comp) * scale",
        0,
        "",
        mid=mid,
        comp=comp_level,
        scale=scale,
    )
    return {
        "tranche_id": t["tranche_id"],
        "basis": basis,
        "talk": talk,
        "oid": oid,
        "implied": implied,
        "comparable": plain(comp_level),
        "comp_basis": comp_basis,
        "comp_cite": comp_cite,
        "pickup": pk,
        "pickup_calc": pk_calc,
        "verdict": verdict_for((mid - comp_level) * scale),
        "syn": syn,
    }


def loan_dm_talk(margin_bps: Decimal, oid: Decimal) -> tuple[Decimal, str]:
    """3Y DM at a talk margin and OID: margin + (100 - OID) / 3 x 100."""
    return compute(
        "3Y discount margin at talk",
        "margin + (100 - oid) / 3 * 100",
        0,
        margin=margin_bps,
        oid=oid,
    )


# ---------------------------------------------------------------------------------------------- builders
class Levels:
    """Everything the tables share: the real TRACE reads, the synthetic loan marks, derived DMs and spreads."""

    def __init__(self, ctx: Ctx, h: Handoff, run_id: str) -> None:
        self.ctx, self.h, self.run_id = ctx, h, run_id
        self.cp1 = cp1_facilities(ctx, run_id)
        self.notes: dict[str, dict] = {}
        for fid, (stem, name, sen) in NOTES.items():
            self.notes[fid] = self._trace(stem, name, sen, fid)
        self.peers = {
            k: self._trace(stem, name, sen, None) for k, (stem, name, sen) in PEERS.items()
        }
        self.loans: dict[str, dict] = {}
        for fid, (marks_key, name, margin) in LOANS.items():
            lm = loan_mark(h, marks_key)
            dm, dm_calc = loan_dm(name, margin, lm["mid"])
            y, y_calc = compute(f"{name} yield", "sofr + dm / 100", 2, sofr=SOFR, dm=dm)
            self.loans[fid] = {
                **lm,
                "name": name,
                "margin": margin,
                "dm": dm,
                "dm_calc": dm_calc,
                "yield": y,
                "yield_calc": y_calc,
                "maturity": self.cp1[fid]["maturity_date"],
                "sofr_cite": cite_fact(h, "rate_deck"),
            }

    def _trace(self, stem: str, name: str, seniority: str, fid: str | None) -> dict:
        ctx, h = self.ctx, self.h
        price = ctx.val(f"{stem}_last_price")
        yld = ctx.val(f"{stem}_last_yield")
        spread, spread_calc = spread_to_treasury(name, yld)
        out = {
            "name": name,
            "seniority": seniority,
            "price": price,
            "price_cite": markers(h.cite_fig(f"{stem}_last_price")),
            "yield": yld,
            "yield_cite": markers(h.cite_fig(f"{stem}_last_yield")),
            "date": us_date(ctx.figure(f"{stem}_last_date")["raw"]),
            "date_cite": markers(h.cite_fig(f"{stem}_last_date")),
            "maturity": us_date(ctx.figure(f"{stem}_maturity")["raw"]),
            "maturity_cite": markers(h.cite_fig(f"{stem}_maturity")),
            "coupon": ctx.val(f"{stem}_coupon"),
            "coupon_cite": markers(h.cite_fig(f"{stem}_coupon")),
            "moodys": ctx.figure(f"{stem}_moodys")["raw"],
            "sp": ctx.figure(f"{stem}_sp")["raw"],
            "spread": spread,
            "spread_calc": spread_calc,
            "treasury_cite": cite_fact(h, "spreads"),
        }
        if fid:
            out["size"] = self.cp1[fid]["drawn_amount"]
        return out


# valuation, preference and compensation: the illustrative layer (base/Front Pages mock), one entry per priced instrument
VIEW: dict[str, dict] = {
    "cei_secured_2032": dict(
        valuation="V2 - Attractive",
        preference="Preferred",
        compensation="Attractive",
        rank="1 (first lien, pari with the term loans)",
        sensitivity="Low",
        reason="Secured, priced at 93.28 to yield 8.06% with a first-lien claim.",
        trigger="Merger debt that ranks pari passu (G8).",
    ),
    "cei_unsecured_2032": dict(
        valuation="V4 - Unattractive",
        preference="Avoid",
        compensation="Inadequate",
        rank="3 (senior unsecured, behind all secured debt)",
        sensitivity="High",
        reason="Unsecured and the likely fulcrum in the illustrative downside.",
        trigger="Disclosure of the merger debt (G8).",
    ),
    "cei_term_b": dict(
        valuation="V3 - Fair",
        preference="Neutral",
        compensation="Adequate",
        rank="1 (first lien, pari with the secured notes)",
        sensitivity="Low",
        reason="First-lien loan quoted near par at a discount margin in line with the BB loan index.",
        trigger="A mark below 98 or a wider margin on new Term Loan B paper.",
    ),
    "cei_term_b1": dict(
        valuation="V3 - Fair",
        preference="Neutral",
        compensation="Adequate",
        rank="1 (first lien; a Non-Covenant Facility)",
        sensitivity="Low",
        reason="First-lien loan with no maintenance covenant, priced a few basis points wider than Term Loan B.",
        trigger="A Term Loan B-1 amendment or a covenant package change.",
    ),
    "cei_term_a": dict(
        valuation="V3 - Fair",
        preference="Neutral",
        compensation="Adequate",
        rank="1 (first lien; amortising, matures January 2028)",
        sensitivity="Low",
        reason="Amortising pro-rata loan with a maintenance test, near par.",
        trigger="No extension announced before January 2028.",
    ),
    "NEW-1": dict(
        sensitivity="Low",
        rank="1 (first lien, pari with the existing term loans)",
        preference_by_verdict={"V2": "Preferred", "V3": "Neutral", "V4": "Avoid", "V5": "Avoid"},
        compensation_by_verdict={
            "V2": "Attractive",
            "V3": "Adequate",
            "V4": "Inadequate",
            "V5": "Inadequate",
        },
        trigger="Final pricing inside the low end of the talk range.",
    ),
    "NEW-2": dict(
        sensitivity="Low",
        rank="1 (first lien, pari with the existing secured notes)",
        preference_by_verdict={"V2": "Preferred", "V3": "Neutral", "V4": "Avoid", "V5": "Avoid"},
        compensation_by_verdict={
            "V2": "Attractive",
            "V3": "Adequate",
            "V4": "Inadequate",
            "V5": "Inadequate",
        },
        trigger="Revised guidance wider than 7.50%.",
    ),
    "NEW-3": dict(
        sensitivity="High",
        rank="3 (senior unsecured, behind all secured debt)",
        preference_by_verdict={"V2": "Preferred", "V3": "Neutral", "V4": "Avoid", "V5": "Avoid"},
        compensation_by_verdict={
            "V2": "Attractive",
            "V3": "Adequate",
            "V4": "Inadequate",
            "V5": "Inadequate",
        },
        trigger="Revised guidance wider than 9.00%.",
    ),
}


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-3", "CZR", run_id, AS_OF, ["CP-0", "CP-1", "MODEL"], fixture_file="czr/cp_3.py"
    )
    h.qa("Restricted")
    primary = is_primary(ctx, run_id)
    lv = Levels(ctx, h, run_id)
    tranches = tranche_rows(ctx, run_id) if primary else []

    # ---- comparables for the talk rows (real TRACE yields; the TLB-1 DM is the synthetic mark)
    tlb1 = lv.loans["cei_term_b1"]
    comps = {
        "loan": (tlb1["dm"], tlb1["dm_calc"]),
        "loan_cite": join_marks(tlb1["cite"], tlb1["sofr_cite"]),
        "cei_secured_2032": (lv.notes["cei_secured_2032"]["yield"], ""),
        "cei_secured_2032_cite": lv.notes["cei_secured_2032"]["yield_cite"],
        "cei_unsecured_2032": (lv.notes["cei_unsecured_2032"]["yield"], ""),
        "cei_unsecured_2032_cite": lv.notes["cei_unsecured_2032"]["yield_cite"],
    }
    talk = {tr["tranche_id"]: talk_valuation(ctx, h, tr, comps) for tr in tranches}

    # ---- snapshot.instrument_levels
    levels: list[dict] = []
    for fid, n in lv.notes.items():
        view = VIEW[fid]
        levels.append(
            {
                "facility_id": fid,
                "instrument": n["name"],
                "level_basis": "Market",
                "level_date": n["date"],
                "bid": GAP,
                "ask": GAP,
                "mid": plain(n["price"]),
                "spread_or_coupon": f"{coupon_txt(n['coupon'])}% coupon",
                "metric_basis": "YTW",
                "yield_or_dm": plain(n["yield"]),
                "oid": GAP,
                "valuation": view["valuation"],
                "rationale": f"FINRA last trade, not a quote (the mid column carries the last-trade price; the vendor yield convention is not verified). {view['reason']} Illustrative Valuation: the real CAOS CP-3 reached Requires More Work.",
                "cite": join_marks(
                    n["price_cite"], n["yield_cite"], n["date_cite"], n["coupon_cite"]
                ),
            }
        )
    for fid, ln in lv.loans.items():
        view = VIEW[fid]
        levels.append(
            {
                "facility_id": fid,
                "instrument": ln["name"],
                "level_basis": "Market",
                "level_date": LEVEL_DATE,
                "bid": plain(ln["bid"], 3),
                "ask": plain(ln["ask"], 3),
                "mid": plain(ln["mid"], 3),
                "spread_or_coupon": f"SOFR + {plain(ln['margin'])} bps",
                "metric_basis": "3Y DM",
                "yield_or_dm": plain(ln["dm"]),
                "oid": GAP,
                "valuation": view["valuation"],
                "rationale": f"Synthetic dealer mark (no loan price is in the pack, G18); 3-year discount margin from margin and mid. {view['reason']}",
                "cite": join_marks(ln["cite"], ln["sofr_cite"])
                + " "
                + ln["mid_calc"]
                + " "
                + ln["dm_calc"],
            }
        )
    for tid, tv in talk.items():
        view = VIEW[tid]
        t = TRANCHES[tid]
        levels.append(
            {
                "facility_id": tid,
                "instrument": t["instrument"],
                "level_basis": "Talk",
                "level_date": AS_OF,
                "bid": GAP,
                "ask": GAP,
                "mid": GAP,
                "spread_or_coupon": t["price_talk"],
                "metric_basis": tv["basis"],
                "yield_or_dm": plain(tv["implied"][1][0], 0 if tv["basis"] == "3Y DM" else 3),
                "oid": plain(tv["oid"], 2),
                "valuation": tv["verdict"],
                "rationale": f"Price Talk, not a market level: the yield or margin is the talk-mid implied figure ({tv['basis']}) with OID {plain(tv['oid'], 2)}; the Valuation compares it with {tv['comp_basis']}.",
                "cite": join_marks(tv["syn"], tv["comp_cite"]) + " " + tv["implied"][1][1],
            }
        )
    h.table("snapshot.instrument_levels", levels)

    # ---- snapshot.relative_value
    rv: list[dict] = []
    ref_cite = {
        "loan_index_bb_dm": cite_syn(h, "loan_index_bb_dm"),
        "loan_index_b_dm": cite_syn(h, "loan_index_b_dm"),
    }
    for key, label, rating in (
        ("loan_index_bb_dm", "BB loan index (synthetic)", "BB"),
        ("loan_index_b_dm", "B loan index (synthetic)", "B"),
    ):
        dm = D(SYNTHETIC[key][0])
        y, y_calc = compute(f"{label} yield", "sofr + dm / 100", 2, sofr=SOFR, dm=dm)
        rv.append(
            {
                "block": "Loan index",
                "name": label,
                "ratings": rating,
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": f"SOFR + {plain(dm)} bps",
                "yield_pct": plain(y, 2) + "%",
                "spread_or_dm_bps": plain(dm),
                "level_date": LEVEL_DATE,
                "cite": join_marks(ref_cite[key], cite_fact(h, "rate_deck")) + " " + y_calc,
            }
        )
    for fid, ln in lv.loans.items():
        rv.append(
            {
                "block": "Loan comparable",
                "name": ln["name"],
                "ratings": FACTS["issue_ratings_other"][LOANS[fid][0]],
                "size": plain(D(lv.cp1[fid]["drawn_amount"])),
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": f"SOFR + {plain(ln['margin'])} bps",
                "maturity_date": ln["maturity"],
                "seniority": "Senior secured",
                "price": plain(ln["mid"], 3),
                "yield_pct": plain(ln["yield"], 2) + "%",
                "spread_or_dm_bps": plain(ln["dm"]),
                "level_date": LEVEL_DATE,
                "cite": join_marks(ln["cite"], ln["sofr_cite"], cite_fact(h, "issue_ratings_other"))
                + " "
                + ln["dm_calc"]
                + " "
                + ln["yield_calc"],
            }
        )
    for key, label, rating, margin, mat in (
        (
            "loan_comp_1",
            "Gaming term loan comp 1 (synthetic)",
            "Ba3 / BB-",
            Decimal(225),
            "2030-09-30",
        ),
        (
            "loan_comp_2",
            "Gaming term loan comp 2 (synthetic)",
            "B1 / B+",
            Decimal(300),
            "2031-03-31",
        ),
    ):
        price = D(SYNTHETIC[key][0])
        dm, dm_calc = loan_dm(label, margin, price)
        y, y_calc = compute(f"{label} yield", "sofr + dm / 100", 2, sofr=SOFR, dm=dm)
        rv.append(
            {
                "block": "Loan comparable",
                "name": label,
                "ratings": rating,
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": f"SOFR + {plain(margin)} bps",
                "maturity_date": mat,
                "seniority": "Senior secured",
                "price": plain(price, 2),
                "yield_pct": plain(y, 2) + "%",
                "spread_or_dm_bps": plain(dm),
                "level_date": LEVEL_DATE,
                "cite": join_marks(cite_syn(h, key), cite_fact(h, "rate_deck"))
                + " "
                + dm_calc
                + " "
                + y_calc,
            }
        )
    for key, label, rating in (
        ("hy_index_bb_yield", "BB high-yield index (synthetic)", "BB"),
        ("hy_index_b_yield", "B high-yield index (synthetic)", "B"),
        ("hy_index_ccc_yield", "CCC high-yield index (synthetic)", "CCC"),
    ):
        y = D(SYNTHETIC[key][0])
        sp, sp_calc = spread_to_treasury(label, y)
        rv.append(
            {
                "block": "HY index",
                "name": label,
                "ratings": rating,
                "currency": "USD",
                "unit": "MILLIONS",
                "yield_pct": plain(y, 2) + "%",
                "spread_or_dm_bps": plain(sp),
                "level_date": LEVEL_DATE,
                "cite": join_marks(cite_syn(h, key), cite_fact(h, "spreads")) + " " + sp_calc,
            }
        )
    for n in lv.notes.values():
        mv, mv_calc = compute(
            f"{n['name']} market value",
            "size * price / 100",
            1,
            size=D(n["size"]),
            price=n["price"],
        )
        rv.append(
            {
                "block": "HY comparable",
                "name": n["name"],
                "bloomberg_id": GAP,
                "ratings": f"{n['moodys']} / {n['sp']}",
                "size": plain(D(n["size"])),
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": f"{coupon_txt(n['coupon'])}%",
                "maturity_date": n["maturity"],
                "seniority": n["seniority"],
                "price": plain(n["price"]),
                "yield_pct": plain(n["yield"]) + "%",
                "spread_or_dm_bps": plain(n["spread"]),
                "market_value": plain(mv, 1),
                "level_date": n["date"],
                "cite": join_marks(
                    n["price_cite"],
                    n["yield_cite"],
                    n["date_cite"],
                    n["maturity_cite"],
                    n["coupon_cite"],
                    n["treasury_cite"],
                )
                + " "
                + n["spread_calc"]
                + " "
                + mv_calc,
            }
        )
    for p in lv.peers.values():
        rv.append(
            {
                "block": "HY comparable",
                "name": p["name"],
                "ratings": f"{p['moodys']} / {p['sp']}",
                "currency": "USD",
                "unit": "MILLIONS",
                "margin_or_coupon": f"{coupon_txt(p['coupon'])}%",
                "maturity_date": p["maturity"],
                "seniority": p["seniority"],
                "price": plain(p["price"]),
                "yield_pct": plain(p["yield"]) + "%",
                "spread_or_dm_bps": plain(p["spread"]),
                "level_date": p["date"],
                "cite": join_marks(
                    p["price_cite"],
                    p["yield_cite"],
                    p["date_cite"],
                    p["maturity_cite"],
                    p["coupon_cite"],
                    p["treasury_cite"],
                )
                + " "
                + p["spread_calc"],
            }
        )
    h.table("snapshot.relative_value", rv)

    # ---- cp3.talk_valuation
    h.table(
        "cp3.talk_valuation",
        [
            {
                "facility_id": tid,
                "talk_stage": TRANCHES[tid]["talk_stage"],
                "talk_low": plain(D(tv["talk"][0]), 0 if tv["basis"] == "3Y DM" else 3),
                "talk_mid": plain(D(tv["talk"][1]), 0 if tv["basis"] == "3Y DM" else 3),
                "talk_high": plain(D(tv["talk"][2]), 0 if tv["basis"] == "3Y DM" else 3),
                "oid": plain(tv["oid"], 2),
                "metric_basis": tv["basis"],
                "implied_low": plain(tv["implied"][0][0], 0 if tv["basis"] == "3Y DM" else 3),
                "implied_mid": plain(tv["implied"][1][0], 0 if tv["basis"] == "3Y DM" else 3),
                "implied_high": plain(tv["implied"][2][0], 0 if tv["basis"] == "3Y DM" else 3),
                "comparable_level": tv["comparable"],
                "comparable_basis": tv["comp_basis"]
                + (
                    " (talk in bps of margin; implied 3Y DM adds OID / 3)"
                    if tv["basis"] == "3Y DM"
                    else " (talk in percent; implied yield from coupon and OID)"
                ),
                "verdict": tv["verdict"],
                "cite": join_marks(tv["syn"], tv["comp_cite"])
                + " "
                + " ".join(i[1] for i in tv["implied"])
                + " "
                + tv["pickup_calc"],
            }
            for tid, tv in talk.items()
        ],
    )

    # ---- cp3.compensation and cp3.security_preference
    comp_rows, pref_rows = [], []
    comps_text = {
        "cei_secured_2032": f"MGM 6.125% 2029 at {plain(lv.peers['mgm']['yield'])}% and PENN 4.125% 2029 at {plain(lv.peers['penn']['yield'])}% (2029 maturities, context only)",
        "cei_unsecured_2032": "Yield pickup over the secured 2032s of 1.25 percentage points for a fulcrum-risk claim",
        "cei_term_b": "BB loan index at SOFR + 235 bps (synthetic); anonymised comp 1 at the same margin",
        "cei_term_b1": "BB loan index at SOFR + 235 bps (synthetic); Term Loan B at a similar margin",
        "cei_term_a": "BB loan index at SOFR + 235 bps (synthetic)",
    }
    comp_cite = {
        "cei_secured_2032": join_marks(
            lv.peers["mgm"]["yield_cite"], lv.peers["penn"]["yield_cite"]
        ),
        "cei_unsecured_2032": mk_fig(h, "rv_yield_pickup"),
        "cei_term_b": join_marks(cite_syn(h, "loan_index_bb_dm"), cite_syn(h, "loan_comp_1")),
        "cei_term_b1": join_marks(cite_syn(h, "loan_index_bb_dm")),
        "cei_term_a": join_marks(cite_syn(h, "loan_index_bb_dm")),
    }
    for fid in (
        "cei_secured_2032",
        "cei_unsecured_2032",
        "cei_term_b",
        "cei_term_b1",
        "cei_term_a",
    ):
        v = VIEW[fid]
        c0 = join_marks(next(r["cite"] for r in levels if r["facility_id"] == fid))
        comp_rows.append(
            {
                "facility_id": fid,
                "structural_rank": v["rank"],
                "recovery_sensitivity": v["sensitivity"],
                "compensation_vs_risk": v["compensation"],
                "comparables": comps_text[fid],
                "cite": join_marks(c0, comp_cite[fid]),
            }
        )
        pref_rows.append(
            {
                "facility_id": fid,
                "preference": v["preference"],
                "key_reason": v["reason"],
                "monitoring_trigger": v["trigger"],
                "cite": join_marks(c0),
            }
        )
    for tid, tv in talk.items():
        v = VIEW[tid]
        code = tv["verdict"][:2]
        reason = f"Talk-mid implied {tv['basis']} of {plain(tv['implied'][1][0], 0 if tv['basis'] == '3Y DM' else 3)} is {plain(abs(tv['pickup']))} bps {'over' if tv['pickup'] >= 0 else 'under'} the comparable level ({tv['verdict']})."
        c0 = join_marks(tv["syn"], tv["comp_cite"])
        comp_rows.append(
            {
                "facility_id": tid,
                "structural_rank": v["rank"],
                "recovery_sensitivity": v["sensitivity"],
                "compensation_vs_risk": v["compensation_by_verdict"][code],
                "comparables": tv["comp_basis"],
                "cite": c0 + " " + tv["pickup_calc"],
            }
        )
        pref_rows.append(
            {
                "facility_id": tid,
                "preference": v["preference_by_verdict"][code],
                "key_reason": reason,
                "monitoring_trigger": v["trigger"],
                "cite": c0 + " " + tv["pickup_calc"],
            }
        )
    h.table("cp3.compensation", comp_rows)
    h.table("cp3.security_preference", pref_rows)

    # ---- analysis
    sec, uns = lv.notes["cei_secured_2032"], lv.notes["cei_unsecured_2032"]
    diff, diff_calc = compute(
        "unsecured less secured last-trade yield",
        "(u - s) * 100",
        4,
        u=uns["yield"],
        s=sec["yield"],
    )
    cc = lambda s: caos_text(h, FOLDER, "CP-3", s)  # noqa: E731
    tlb, tlb1m = lv.loans["cei_term_b"], lv.loans["cei_term_b1"]
    cm = h.cite_doc_find(
        "CZR_2024_Credit_Agreement_Fifth_Amendment.txt",
        "2.25% per annum in the case of any Term Benchmark Loan",
    )
    para = [
        f"No instrument can be called best compensated on the delivered record, and the real CAOS run says so: it reached Requires More Work for both priced 2032 notes, marked relative value Unclear and named no instrument Preferred {cc('{11,12,13,14}')}. "
        f"Everything below that reads as a view, that is each Valuation (V1 to V5), compensation word and preference, is the fixture's illustrative layer and is not a finding; confidence is Low and QA is Restricted.",
        f"The only dated market levels in the pack are FINRA last trades on 1 October 2026: the 6.50% secured notes at {num(sec['price'])} to yield {num(sec['yield'])}% {sec['price_cite']}{sec['yield_cite']} and the 6.00% unsecured notes at {num(uns['price'])} to yield {num(uns['yield'])}% {uns['price_cite']}{uns['yield_cite']}. "
        f"The yield difference is {num(diff, 4)} basis points ({diff_calc}). It is arithmetic, not a credit spread: coupons, maturities and call dates differ, and a last trade is not an executable quote {cc('{9,10}')}. "
        f"Spreads in the tables use a synthetic 6-year Treasury of {num(TREASURY, 2)}% {uns['treasury_cite']}, so a secured spread of {num(sec['spread'])} bps and an unsecured spread of {num(uns['spread'])} bps are test values, not market spreads.",
        f"The term loans carry synthetic dealer marks because no loan price is in the pack {tlb['cite']}: Term Loan B at {num(tlb['bid'], 3)} / {num(tlb['ask'], 3)}, which gives a 3-year discount margin of {num(tlb['dm'])} bps ({tlb['dm_calc']}), and Term Loan B-1 at {num(tlb1m['bid'], 3)} / {num(tlb1m['ask'], 3)} for {num(tlb1m['dm'])} bps. "
        f"Both loans carry a margin of SOFR + 2.25% in the real credit agreement {cm}; the BB loan index row (SOFR + 235 bps) and the two gaming loan comparables are synthetic and labelled. The comparables for the notes are real: MGM's 6.125% 2029s yield {num(lv.peers['mgm']['yield'])}% and PENN's 4.125% 2029s {num(lv.peers['penn']['yield'])}% {lv.peers['mgm']['yield_cite']}{lv.peers['penn']['yield_cite']}, but both mature in 2029 and are context only.",
    ]
    if primary:
        t1, t2, t3 = (talk[x] for x in ("NEW-1", "NEW-2", "NEW-3"))
        para.append(
            f"The merger's three new tranches are valued at Price Talk, not at a market level {t1['syn']}. At the talk mid, NEW-1 (the incremental Term Loan B) implies a 3-year discount margin of {num(t1['implied'][1][0])} bps against {t1['comparable']} bps on Term Loan B-1, a pickup of {num(t1['pickup'])} bps ({t1['verdict']}). "
            f"NEW-2 (the secured notes due 2033) implies a yield of {num(t2['implied'][1][0], 3)}% against {t2['comparable']}% on the secured 2032s, {num(abs(t2['pickup']))} bps inside it ({t2['verdict']}), and NEW-3 (the unsecured notes due 2034) {num(t3['implied'][1][0], 3)}% against {t3['comparable']}%, {num(abs(t3['pickup']))} bps inside it ({t3['verdict']}). "
            f"The rule for the illustrative verdict is stated here: a pickup of 50 bps or more over the comparable is V2, within 50 bps is V3, 50 to 149 bps under is V4, and 150 or more under is V5."
        )
    para.append(
        f"On compensation, the illustrative view is that the secured 2032s are the best paid for a first-lien claim and the unsecured 2032s the worst paid for a claim that sits behind all the secured debt; the 125 bp gap above is a research question, not a recommended switch. "
        f"What would change this view: a two-sided quote and size on the notes, a real benchmark curve and loan marks, the disclosed merger debt (G8) and the full collateral and intercreditor package {cc('{18,19}')}. Confidence in this module: Low."
    )
    h.analysis("\n\n".join(para))
    gaps = [
        "- Loan prices and margins: not in the pack (G18). The term-loan marks are synthetic, so the loan rows and the BB loan index are test values. Effect: loan Valuations are illustrative. Lifted by: loan marks or a dealer run.",
        "- Benchmark curve: not in the pack (G19). Spreads use a synthetic 6-year Treasury of 4.10%. Effect: spread columns are proxies. Lifted by: a Treasury or swap curve at 2 October 2026.",
        "- Index and comparable loan rows: synthetic and labelled; no Sector RV Workbook was delivered. Lifted by: the maintained Sector RV Workbook.",
        "- FINRA gives last trades only: no bid, ask, size, benchmark, seniority or intraday time. The mid column carries the last-trade price for the two notes. Lifted by: two-sided quotes.",
        "- Recovery inputs for compensation are not quantified; collateral and intercreditor documents are incomplete (real CAOS limitation).",
        "- Valuation, preference and compensation words are the illustrative layer; the real CAOS CP-3 did not assign them.",
    ]
    if primary:
        gaps.append(
            "- New tranches: size, talk, OID, maturity and expected ratings are synthetic (the merger's committed debt is unstated, G8). Lifted by: the commitment papers or a lender presentation."
        )
    h.gaps("\n".join(gaps))
    return h
