"""Portfolio Fit (interfaces §7): exposure, touched limits, headroom, max size, verdict, cap, final.

All arithmetic is Decimal with ROUND_HALF_UP. `fit()` is the only place a verdict or cap is decided.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from core import GAP, Ctx, D, FixtureError, Handoff, fpct, plain, q

REC_ORDER = ["1 - Strong OW", "2 - Modest OW", "3 - MW", "4 - Modest UW", "5 - Strong UW", "Avoid"]
CAP_FOR = {"Breaches": "Avoid", "Watch": "3 - MW", "Fits": "1 - Strong OW"}
PLACES = {"UNITS": 0, "THOUSANDS": 1, "MILLIONS": 3}


def weaker(a: str, b: str) -> str:
    """The weaker of two recommendations (1 - Strong OW strongest, Avoid weakest); N/A stays N/A."""
    if "N/A" in (a, b):
        return "N/A"
    return max(a, b, key=REC_ORDER.index)


def rating_bucket(assigned: str | None) -> str:
    """Rating bucket of an assigned rating; no rating (an expected rating is not assigned) is Unrated."""
    if not assigned:
        return "Unrated"
    r = assigned.strip().removeprefix("(P)").strip()
    if re.match(r"^(Caa|Ca$|C$)", r) or re.match(r"^(CCC|CC$|C$|D$|SD$)", r):
        return "CCC"
    m = re.match(r"^(Aaa|Aa|A|Baa|Ba|B|AAA|AA|A|BBB|BB|B)", r)
    return m.group(1).upper() if m else "Unrated"


@dataclass
class FitResult:
    portfolio_id: str
    rows: list[dict] = field(default_factory=list)
    limit_rows: list[dict] = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        return {"portfolio_id": self.portfolio_id, **self.detail}


def _headroom_amount(unit: str, headroom: Decimal, nav: Decimal, par: Decimal) -> Decimal | None:
    """Headroom converted to the run unit; None means unlimited."""
    if unit == "pct_nav":
        return headroom * nav / 100
    if unit == "pct_par":
        return headroom * par / 100
    if unit == "amount":
        return headroom
    if unit == "count":
        return None if headroom >= 1 else Decimal(0)
    if unit == "years":
        return None if headroom > 0 else Decimal(0)
    raise FixtureError(f"limit unit {unit!r} not recognised")


def fit(portfolio: dict, instruments: list[dict], issuer_id: str) -> FitResult:
    """§7 arithmetic for one portfolio against each instrument.

    Instrument keys: facility_id, instrument, rating (assigned or None), expected_rating (optional), and any
    attribute a limit scopes on (sector, country, asset_type, seniority, currency, maturity = tenor in years).
    Limits: limit_id, category, parameter, scope, scope_value (str | list | None), limit_value, unit, limit_kind,
    current_value, direction ('max' default or 'min'), source; scope 'other' limits are shown From file.
    """
    nav, par = D(portfolio["nav"]), D(portfolio["par"])
    places = PLACES[portfolio["unit"]]
    pid = portfolio["portfolio_id"]
    exposure = sum(
        (D(p["par"]) for p in portfolio["positions"] if p["issuer_id"] == issuer_id), Decimal(0)
    )
    exp_pct = exposure / nav * 100 if nav else Decimal(0)
    unparsed = {u["limit_id"] for u in portfolio.get("unparsed", []) if "limit_id" in u}
    one_pct = nav / 100
    res = FitResult(pid)
    detail: list[dict] = []
    for inst in instruments:
        inst = dict(inst)
        inst["rating_bucket"] = rating_bucket(inst.get("rating"))
        touched: list[dict] = []
        for lim in portfolio["limits"]:
            scope, sv = lim["scope"], lim.get("scope_value")
            status, current, headroom, amount = "Within", None, None, None
            if scope == "other":
                touches = True
                status = "From file"
                current = lim.get("current_value")
                headroom = lim.get("headroom")
            elif scope == "issuer":
                touches = True
            else:
                attr = inst.get(scope)
                if attr is None:
                    touches, status = True, "Not computed"
                else:
                    vals = sv if isinstance(sv, list) else [sv]
                    touches = attr in vals if scope != "maturity" else True
            if not touches:
                continue
            kind = lim["limit_kind"]
            if status == "Within":
                unit = lim["unit"]
                if lim["limit_id"] in unparsed or (
                    lim.get("current_value") is None and scope != "issuer"
                ):
                    status = "Not computed"
                else:
                    if scope == "issuer":
                        cur = {
                            "pct_nav": exp_pct,
                            "pct_par": exposure / par * 100,
                            "amount": exposure,
                            "count": Decimal(1 if exposure else 0),
                        }[unit]
                    elif scope == "maturity":
                        cur = D(inst["maturity"])
                    else:
                        cur = D(lim["current_value"])
                    lv = D(lim["limit_value"])
                    h = (cur - lv) if lim.get("direction") == "min" else (lv - cur)
                    amount = _headroom_amount(unit, h, nav, par)
                    current, headroom = cur, h
                    if h < 0:
                        status = "Breached"
            touched.append(
                {
                    "lim": lim,
                    "status": status,
                    "current": current,
                    "headroom": headroom,
                    "amount": amount,
                    "kind": kind,
                }
            )
        hard = [
            t
            for t in touched
            if t["kind"] == "Hard"
            and t["status"] in ("Within", "Breached")
            and t["lim"]["scope"] != "other"
        ]
        capped = [(max(t["amount"], Decimal(0)), t) for t in hard if t["amount"] is not None]
        if capped:
            max_size, binding = min(capped, key=lambda x: x[0])
            binding_id = binding["lim"]["limit_id"]
        else:
            max_size, binding_id = nav, "None (NAV)"
        hard_breach = any(t["headroom"] < 0 for t in hard)
        soft_breach = any(t["kind"] == "Soft" and t["status"] == "Breached" for t in touched)
        uncomputed = any(t["status"] == "Not computed" for t in touched)
        if hard_breach or max_size == 0:
            verdict = "Breaches"
        elif soft_breach or max_size < one_pct or uncomputed:
            verdict = "Watch"
        else:
            verdict = "Fits"
        cap = CAP_FOR[verdict]
        note = []
        if inst["rating_bucket"] == "Unrated":
            note.append(
                "Unrated (no assigned rating"
                + (
                    f"; expected {inst['expected_rating']} is not assigned"
                    if inst.get("expected_rating")
                    else ""
                )
                + ")"
            )
        why = {
            "Breaches": "a Hard limit is breached or the maximum size is zero",
            "Watch": "a Soft limit is breached, the maximum size is under 1% of NAV, or a limit could not be computed",
            "Fits": "every touched limit has room and the maximum size is at least 1% of NAV",
        }[verdict]
        reason = f"{verdict}: {why}; binding limit {binding_id}" + (
            f"; {'; '.join(note)}" if note else ""
        )
        rnd = lambda d: plain(q(d, places))  # noqa: E731
        res.rows.append(
            {
                "portfolio_id": pid,
                "strategy": portfolio["strategy"],
                "facility_id": inst["facility_id"],
                "instrument": inst["instrument"],
                "current_exposure": rnd(exposure),
                "current_exposure_pct_nav_pct": fpct(exp_pct, 2),
                "max_size": rnd(max_size),
                "currency": portfolio["currency"],
                "unit": portfolio["unit"],
                "binding_limit": binding_id,
                "verdict": verdict,
                "recommendation_cap": cap,
                "reason": reason,
            }
        )
        for t in touched:
            lim = t["lim"]
            amt = t["amount"]
            res.limit_rows.append(
                {
                    "portfolio_id": pid,
                    "facility_id": inst["facility_id"],
                    "limit_id": lim["limit_id"],
                    "category": lim["category"],
                    "parameter": lim["parameter"],
                    "limit_kind": t["kind"],
                    "limit_value": plain(D(lim["limit_value"]))
                    if lim.get("limit_value") is not None
                    else GAP,
                    "limit_unit": lim["unit"],
                    "current_value": "Not computed"
                    if t["status"] == "Not computed"
                    else (
                        str(t["current"])
                        if t["status"] == "From file"
                        else plain(q(t["current"], 4))
                    ),
                    "headroom": "Not computed"
                    if t["status"] == "Not computed"
                    else (
                        str(t["headroom"])
                        if t["status"] == "From file"
                        else plain(q(t["headroom"], 4))
                    ),
                    "headroom_amount": GAP
                    if (amt is None or t["status"] in ("Not computed", "From file"))
                    else rnd(max(amt, Decimal(0)) if amt >= 0 else amt),
                    "currency": portfolio["currency"],
                    "unit": portfolio["unit"],
                    "status": t["status"],
                    "source": lim["source"],
                }
            )
        detail.append(
            {
                "facility_id": inst["facility_id"],
                "rating_bucket": inst["rating_bucket"],
                "exposure": rnd(exposure),
                "exposure_pct_nav": plain(q(exp_pct, 6)),
                "max_size": rnd(max_size),
                "binding_limit": binding_id,
                "verdict": verdict,
                "cap": cap,
                "touched": [t["lim"]["limit_id"] for t in touched],
            }
        )
    res.detail = {
        "inputs": {"portfolio": portfolio, "instruments": instruments, "issuer_id": issuer_id},
        "instruments": detail,
    }
    return res


def cp6_rows(
    result: FitResult, uncapped: dict[str, str], strategy: str | None = None
) -> list[dict]:
    """`cp6.portfolio_recommendation` rows: final = weaker of the uncapped recommendation and the Fit cap."""
    rows = []
    for r in result.rows:
        un = uncapped[r["facility_id"]]
        cap = r["recommendation_cap"]
        rows.append(
            {
                "portfolio_id": r["portfolio_id"],
                "strategy": strategy or r["strategy"],
                "instrument": r["instrument"],
                "uncapped": un,
                "cap": cap,
                "final": weaker(un, cap),
                "fit_verdict": r["verdict"],
                "reason": f"Fit {r['verdict']} caps at {cap}; the final is the weaker of {un} and {cap}",
            }
        )
    return rows


def fit_handoff(
    ctx: Ctx, run_id: str, issuer_id: str, analysis_date: str, results: list[FitResult]
) -> Handoff:
    h = Handoff(
        ctx,
        "FIT",
        issuer_id,
        run_id,
        analysis_date,
        ["CP-3", "CP-1", "RUN_BRIEF"],
        fixture_file="lib.py (fit)",
    )
    rows = [r for res in results for r in res.rows]
    limits = [r for res in results for r in res.limit_rows]
    h.table("snapshot.portfolio_fit", rows)
    h.table("fit.limit_headroom", limits)
    if not results:
        h.qa("Restricted")
        h.analysis("No portfolio is attached to this run, so Portfolio Fit has nothing to compute.")
        h.gaps("- No Portfolio Context file was present; the Fit tables are empty.")
        return h
    nv = {v: sum(1 for r in rows if r["verdict"] == v) for v in ("Fits", "Watch", "Breaches")}
    h.analysis(
        f"Fit evaluated {len(rows)} instrument(s) across {len(results)} portfolio(s): {nv['Fits']} Fits, {nv['Watch']} Watch, {nv['Breaches']} Breaches. "
        "Headroom is the limit less the current value in the limit's own unit; the maximum size is the smallest Hard headroom in amount terms, floored at zero."
    )
    h.gaps(
        "- Book-level statistics the portfolio file states but RBOT cannot recompute are shown from the file (status From file) and never bind the maximum size."
    )
    return h


# ------------------------------------------------------------------ Test CLO I (synthetic) for CZR runs
def _pct(text: str) -> Decimal:
    m = re.search(r"([\d.]+)\s*%", text)
    if not m:
        raise FixtureError(f"no percentage in {text!r}")
    return D(m.group(1))


def test_clo_i(ctx: Ctx) -> dict[str, Any]:
    """Prepared `rbot-portfolio/1` for the synthetic Test CLO I, built from the mock data's constraints."""
    base = ctx.base
    nav = D(re.search(r"\$([\d,]+)", base["citations"]["S18"]["excerpt"]).group(1))  # type: ignore[union-attr]
    par = D(re.search(r"\$([\d,]+)", base["citations"]["S19"]["excerpt"]).group(1))  # type: ignore[union-attr]
    cons = {c["id"]: c for c in base["portfolio"]["constraints"]}

    def lim(cid: str, scope: str, scope_value: Any, limit_id: str | None = None, **kw: Any) -> dict:
        c = cons[cid]
        return {
            "limit_id": limit_id or cid,
            "category": c["category"],
            "parameter": kw.pop("parameter", c["parameter"]),
            "scope": scope,
            "scope_value": scope_value,
            "limit_value": plain(_pct(c["limit"])) if "%" in c["limit"] else None,
            "unit": "pct_nav",
            "limit_kind": c["breachType"],
            "current_value": plain(_pct(c["current"])) if "%" in c["current"] else None,
            "source": f"{c['ref']}: {c['sourceDocument']}",
            **kw,
        }

    sector = lim(
        "C-06",
        "sector",
        "Leisure Facilities & Services",
        "C-06-LEISURE",
        parameter="Max single sector: Leisure Facilities & Services",
    )
    sector["current_value"] = plain(
        _pct(base["citations"]["S32"]["excerpt"].split("Leisure Facilities & Services")[1])
    )
    sector["source"] = "S32: Exposure Report section C; S6: Indenture §7.11"
    limits = [
        lim("C-01", "issuer", None, parameter="Max single issuer exposure (Caesars' own exposure)"),
        lim("C-04", "rating_bucket", ["CCC", "Unrated"]),
        lim("C-05", "rating_bucket", ["Unrated"]),
        lim("C-10", "seniority", ["Second lien", "Unsecured"]),
        sector,
        {
            **lim("C-03", "other", None),
            "limit_value": "17",
            "unit": "pct_nav",
            "current_value": cons["C-03"]["current"],
            "headroom": cons["C-03"]["headroom"],
        },
        {
            **lim("C-11", "other", None),
            "limit_value": "8.0",
            "current_value": cons["C-11"]["current"],
            "headroom": cons["C-11"]["headroom"],
        },
    ]
    return {
        "schema": "rbot-portfolio/1",
        "portfolio_id": "TEST_CLO_I",
        "portfolio_name": "Test CLO I Ltd",
        "strategy": "CLO",
        "as_of": "2026-05-29",
        "nav": plain(nav),
        "par": plain(par),
        "currency": "USD",
        "unit": "UNITS",
        "positions": [],
        "limits": limits,
        "unparsed": [],
        "notes": [
            "Synthetic test portfolio. Existing Caesars exposure: none (S46). C-01 is tested on Caesars' own exposure, not the book's largest issuer."
        ],
    }
