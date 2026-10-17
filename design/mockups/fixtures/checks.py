"""`check(run)`: every FIXTURES §6 check on a finished `rbot-run/1` dict. Returns a list of failure messages."""

from __future__ import annotations

import json
import re
from decimal import Decimal

import spec as spec_mod
from core import (
    GAP,
    MCTX,
    Ctx,
    D,
    FixtureError,
    check_calc_string,
    distress_gate_not_met,
    load_ctx,
    markers_in,
    plain,
    q,
    table_problems,
)
from fit import fit, weaker

DENY_NAMES = [
    "Caesars",
    "CZR",
    "Eldorado",
    "Harrah",
    "Fertitta",
    "Landry",
    "MGM",
    "PENN Entertainment",
    "PENN",
    "VICI",
    "GLPI",
    "Empire Merger",
    "Hospitality Headquarters",
    "PJT Partners",
    "FHSUHY",
    "Wynn",
    "Boyd Gaming",
    "Station Casinos",
    "Red Rock",
    "Churchill Downs",
    "Bally",
    "Hard Rock",
    "Las Vegas Sands",
    "Golden Nugget",
    "Circus Circus",
    "Treasure Island",
    "Foxwoods",
    "Mohegan",
    "Scientific Games",
]


def _close(actual: str, expected: Decimal) -> bool:
    try:
        a = D(actual)
    except FixtureError:
        return False
    places = max(0, -a.as_tuple().exponent)  # type: ignore[operator]
    return q(expected, places) == a


def _rows(h: dict, tid: str) -> list[dict]:
    t = h["tables"].get(tid)
    return [dict(zip(t["columns"], r, strict=True)) for r in t["rows"]] if t else []


def _num(s: str) -> Decimal | None:
    try:
        return None if s in (GAP, "") else D(s)
    except FixtureError:
        return None


# ------------------------------------------------------------------------------ handoffs
def check_handoff(ctx: Ctx, step: str, h: dict, run: dict) -> list[str]:
    out: list[str] = []
    fm = h["front_matter"]
    mid = fm["module_id"]
    if mid != step:
        out.append(f"{step}: front matter says {mid}")
    for k in ("module_id", "run_id", "issuer_id", "analysis_date", "qa_status", "inputs"):
        if k not in fm:
            out.append(f"{step}: front matter lacks {k}")
    if fm.get("run_id") != run["run_id"]:
        out.append(f"{step}: run_id differs from the run")
    blocked = h["qa_status"] == "Blocked"
    for tid in ctx.spec["module_tables"][mid]:
        if tid not in h["tables"]:
            out.append(f"{step}: missing table {tid}")
        else:
            out += table_problems(
                ctx.spec, step, tid, h["tables"][tid], blocked, distress_gate_not_met(h["tables"])
            )
    for tid in h["tables"]:
        if tid not in ctx.spec["tables"] or mid not in ctx.spec["tables"][tid]["owners"]:
            out.append(f"{step}: table {tid} is not owned by {mid}")
    out += check_citations(ctx, step, h, run)
    for t in h["tables"].values():
        for r in t["rows"]:
            for c in r:
                if "calc:" in c:
                    msg = check_calc_string(c[c.index("calc:") :])
                    if msg:
                        out.append(f"{step}: {msg}")
    return out


def check_citations(ctx: Ctx, step: str, h: dict, run: dict) -> list[str]:
    out: list[str] = []
    cits = {c["id"]: c for c in h["citations"]}
    texts = [h["analysis_md"], h["gaps_md"]] + [
        c for t in h["tables"].values() for r in t["rows"] for c in r
    ]
    used: set[int] = set()
    for tx in texts:
        for m in markers_in(tx):
            used.add(m)
            if f"C{m}" not in cits:
                out.append(f"{step}: [C{m}] does not resolve")
    for cid, c in cits.items():
        if int(cid[1:]) not in used:
            out.append(f"{step}: {cid} is never cited")
        syn = c["source"].startswith("TEST DATA")
        if c["synthetic"] != syn:
            out.append(f"{step} {cid}: synthetic flag disagrees with its source")
        if not c.get("anchored"):
            out.append(f"{step} {cid}: not anchored")
        origin = c.get("origin", "")
        if c["synthetic"]:
            if not c["locator"].startswith("fixtures/") or not c["excerpt"].strip():
                out.append(
                    f"{step} {cid}: synthetic citation lacks a fixtures/ locator or rationale"
                )
            continue
        try:
            if origin.startswith("data:"):
                d = ctx.data_citation(origin[5:])
                if d["excerpt"] != c["excerpt"] or d["file"] != c["source"]:
                    out.append(f"{step} {cid}: differs from base data {origin}")
                ln = int(re.search(r"line (\d+)", c["locator"]).group(1))  # type: ignore[union-attr]
                if ctx.anchor_line(c["source"], ln, c["excerpt"]) != ln:
                    out.append(
                        f"{step} {cid}: line {ln} of {c['source']} does not hold the excerpt"
                    )
            elif origin.startswith("caos:"):
                folder, rest = origin[5:].split("/", 1)
                module, marker = rest.split("#")
                _, cc = ctx.caos(folder, module)
                hit = next(x for x in cc if x["marker"] == int(marker))
                if hit["line_text"] != c["excerpt"] or hit["source"] != c["source"]:
                    out.append(f"{step} {cid}: differs from CAOS {origin}")
            elif origin.startswith("doc:"):
                _, file, line = origin.split(":")
                ctx.verify_line(file, int(line), c["excerpt"])
            elif re.match(r"^(CP-[0-9A-Z]+):C\d+$", origin):
                mod, cid2 = origin.split(":")
                src = next(
                    (
                        x
                        for x in run["handoffs"].get(mod, {}).get("citations", [])
                        if x["id"] == cid2
                    ),
                    None,
                )
                if src is None or src["excerpt"] != c["excerpt"] or src["source"] != c["source"]:
                    out.append(f"{step} {cid}: not a copy of {origin}")
            else:
                out.append(f"{step} {cid}: real citation with unknown origin {origin!r}")
        except (FixtureError, StopIteration, AttributeError) as exc:
            out.append(f"{step} {cid}: citation does not verify ({exc})")
    return out


# ------------------------------------------------------------------------------ derived figures
def _model_cells(model: dict) -> dict[str, dict[str, dict]]:
    return {ln["line_id"]: {c["column_id"]: c for c in ln["cells"]} for ln in model["lines"]}


def check_model(model: dict) -> list[str]:
    out: list[str] = []
    cells = _model_cells(model)
    val = lambda lid, col: None if "value" not in cells[lid][col] else D(cells[lid][col]["value"])  # noqa: E731

    def eq(name: str, col: str, got: Decimal | None, want: Decimal | None) -> None:
        if got is None or want is None:
            return
        if q(got, 6) != q(want, 6):
            out.append(f"model {col} {name}: {plain(q(got, 6))} != recomputed {plain(q(want, 6))}")

    facs = [k for k in cells if k.startswith("fac:")]
    for col in [c["column_id"] for c in model["columns"]]:
        parts = [val(f, col) for f in facs]
        if all(p is not None for p in parts):
            eq("total_debt", col, val("total_debt", col), sum(parts, Decimal(0)))  # type: ignore[arg-type]
        td, cash, nd = val("total_debt", col), val("cash_closing", col), val("net_debt", col)
        if td is not None and cash is not None:
            eq("net_debt", col, nd, td - cash)
        a, ci, lc, tx, ffo = (
            val(x, col)
            for x in (
                "adjusted_ebitda",
                "cash_interest",
                "lease_cash_not_in_ebitda",
                "cash_taxes",
                "ffo",
            )
        )
        if None not in (a, ci, lc, tx):
            eq("ffo", col, ffo, a + ci + lc + tx)  # type: ignore[operator]
        cfo, wc, capex, fcf = (
            val(x, col) for x in ("cfo_adjusted", "working_capital_change", "capex", "fcf")
        )
        if None not in (ffo, wc):
            eq("cfo", col, cfo, ffo + wc)  # type: ignore[operator]
        if None not in (cfo, capex):
            eq("fcf", col, fcf, cfo + capex)  # type: ignore[operator]
        li, ur = val("liquidity", col), val("undrawn_rcf", col)
        if None not in (cash, ur):
            eq("liquidity", col, li, cash + ur)  # type: ignore[operator]
        if (
            a
            and td is not None
            and a > 0
            and "value" in cells["metric:total_leverage_adjusted"][col]
        ):
            eq(
                "total_leverage_adjusted",
                col,
                val("metric:total_leverage_adjusted", col),
                MCTX.divide(td, a),
            )
        if a and nd is not None and a > 0 and "value" in cells["metric:net_leverage_adjusted"][col]:
            eq(
                "net_leverage_adjusted",
                col,
                val("metric:net_leverage_adjusted", col),
                MCTX.divide(nd, a),
            )
    return out


def check_derived(ctx: Ctx, run: dict) -> list[str]:
    out: list[str] = []
    hs = run["handoffs"]
    if run.get("model"):
        out += check_model(run["model"])
    if "PROJECTION" in hs:
        for r in _rows(hs["PROJECTION"], "model.forecast_checks"):
            if r["status"] == "FAIL":
                out.append(
                    f"projection identity failed: {r['check']} {r['case']} {r['period_id']} ({r['detail']})"
                )
        cases = {r["case"] for r in _rows(hs["PROJECTION"], "model.projection_summary")}
        if cases != {"BASE", "DOWNSIDE"}:
            out.append(f"projection cases are {sorted(cases)}, expected BASE and DOWNSIDE")
    if "MODEL" in hs:
        tot = {r["line"]: r for r in _rows(hs["MODEL"], "snapshot.capital_structure_totals")}
        try:
            s, u, t = (
                D(tot[k]["amount"]) for k in ("Senior secured debt", "Unsecured debt", "Total debt")
            )
            if s + u != t:
                out.append(f"capital structure totals: {s} + {u} != {t}")
        except (KeyError, FixtureError):
            pass
        cs = _rows(hs["MODEL"], "snapshot.capital_structure")
        try:
            if sum((D(r["outstanding"]) for r in cs), Decimal(0)) != D(tot["Total debt"]["amount"]):
                out.append("capital structure rows do not sum to Total debt")
        except (KeyError, FixtureError):
            pass
    # table-level identities
    for step, h in hs.items():
        for fn in _TABLE_CHECKS:
            out += [f"{step}: {m}" for m in fn(h)]
    out += check_fit(ctx, run)
    out += check_cp5(run)
    return out


def _chk_period_comparison(h: dict) -> list[str]:
    out = []
    for r in _rows(h, "cp1b.period_comparison"):
        cur, ref = _num(r["current_value"]), _num(r["reference_value"])
        if cur is None or ref is None:
            continue
        if r["abs_change"] != GAP and not _close(r["abs_change"], cur - ref):
            out.append(
                f"period_comparison {r['metric_id']}: abs_change {r['abs_change']} != {plain(cur - ref)}"
            )
        if (
            r["pct_change_pct"] != GAP
            and ref != 0
            and not _close(r["pct_change_pct"], (cur - ref) / abs(ref) * 100)
        ):
            out.append(
                f"period_comparison {r['metric_id']}: pct_change {r['pct_change_pct']} does not recompute"
            )
    return out


def _chk_cash_conversion(h: dict) -> list[str]:
    out = []
    for r in _rows(h, "cp1d.cash_conversion"):
        a, c = _num(r["adjusted_ebitda"]), _num(r["cfo"])
        if a and c is not None and a > 0 and not _close(r["conversion_pct"], c / a * 100):
            out.append(
                f"cash_conversion {r['period_id']}: {r['conversion_pct']} does not recompute"
            )
    return out


def _chk_bridge(h: dict) -> list[str]:
    rows = _rows(h, "cp2d.bridge")
    if not rows or any(_num(r["amount"]) is None for r in rows):
        return []
    out = []
    if rows[0]["kind"] != "Opening total" or rows[-1]["kind"] != "Closing total":
        out.append("bridge must start with Opening total and end with Closing total")
        return out
    mid = sum((D(r["amount"]) for r in rows[1:-1]), Decimal(0))
    if D(rows[0]["amount"]) + mid != D(rows[-1]["amount"]):
        out.append(
            f"bridge does not reconcile: {rows[0]['amount']} + {plain(mid)} != {rows[-1]['amount']}"
        )
    return out


def _chk_runway(h: dict) -> list[str]:
    run_ = {r["item"]: r for r in _rows(h, "cp2d.runway")}
    out = []
    try:
        acc, mand, head = (
            _num(run_[k]["value"])
            for k in ("Accessible liquidity", "Mandatory uses 12m", "Headroom")
        )
    except KeyError:
        return out
    if None not in (acc, mand, head) and acc - abs(mand) != head:  # type: ignore[operator]
        out.append(f"runway: {acc} - {mand} != headroom {head}")
    srcs = _rows(h, "cp2d.liquidity_sources")
    if acc is not None and srcs:
        tot = sum(
            (
                D(r["amount"])
                for r in srcs
                if r["accessible"] == "Yes" and _num(r["amount"]) is not None
            ),
            Decimal(0),
        )
        if tot != acc:
            out.append(f"runway accessible liquidity {acc} != sum of accessible sources {tot}")
    uses = _rows(h, "cp2d.cash_uses_12m")
    if mand is not None and uses:
        tm = sum(
            (
                abs(D(r["amount"]))
                for r in uses
                if r["mandatory"] == "Yes" and _num(r["amount"]) is not None
            ),
            Decimal(0),
        )
        if tm != abs(mand):
            out.append(f"runway mandatory uses {mand} != sum of mandatory uses {tm}")
    return out


def _chk_pressure(h: dict) -> list[str]:
    out = []
    for r in _rows(h, "cp3c.maturity_pressure"):
        m, s, g = _num(r["maturing_amount"]), _num(r["sources_available"]), _num(r["funding_gap"])
        if None not in (m, s, g) and max(m - s, Decimal(0)) != g:  # type: ignore[operator]
            out.append(f"maturity_pressure {r['fiscal_year']}: gap {g} != max({m} - {s}, 0)")
    return out


def _headroom_rows(rows: list[dict], label: str) -> list[str]:
    out = []
    for r in rows:
        th, cur, hd = _num(r["threshold"]), _num(r["current_value"]), _num(r["headroom"])
        if None in (th, cur, hd):
            continue
        want = th - cur if r["direction"] == "Ceiling" else cur - th  # type: ignore[operator]
        if want != hd and not _close(r["headroom"], want):
            out.append(
                f"{label} {r.get('test') or r.get('metric')}: headroom {hd} != {plain(want)}"
            )
        if r["status"] == "Headroom" and hd < 0:  # type: ignore[operator]
            out.append(f"{label}: negative headroom marked Headroom")
        if r["status"] == "Breached" and hd >= 0:  # type: ignore[operator]
            out.append(f"{label}: non-negative headroom marked Breached")
    return out


def _chk_covenants(h: dict) -> list[str]:
    return _headroom_rows(_rows(h, "cp4.covenant_tests"), "covenant_tests")


def _chk_triggers(h: dict) -> list[str]:
    return _headroom_rows(_rows(h, "cp2h.rating_triggers"), "rating_triggers")


def _chk_recoveries(h: dict) -> list[str]:
    out = []
    rows = _rows(h, "cp4c.recoveries")
    by_sc: dict[str, list[dict]] = {}
    for r in rows:
        by_sc.setdefault(r["scenario"], []).append(r)
    for sc, rs in by_sc.items():
        fulcrum_seen = False
        for r in rs:
            claim, alloc, avail, res, pct = (
                _num(r[k])
                for k in (
                    "allowed_claim",
                    "allocation",
                    "available_value",
                    "residual",
                    "recovery_pct",
                )
            )
            if None in (claim, alloc, avail, res):
                continue
            if alloc > avail + Decimal("0.0000001"):  # type: ignore[operator]
                out.append(f"recoveries {sc}/{r['class_id']}: allocation exceeds available value")
            if avail - alloc != res:  # type: ignore[operator]
                out.append(f"recoveries {sc}/{r['class_id']}: residual {res} != {avail} - {alloc}")
            if (
                claim
                and claim > 0
                and pct is not None
                and not _close(r["recovery_pct"], alloc / claim * 100)
            ):  # type: ignore[operator]
                out.append(f"recoveries {sc}/{r['class_id']}: recovery_pct does not recompute")
            is_f = r["fulcrum"] == "Yes"
            should = (not fulcrum_seen) and claim > 0 and alloc < claim  # type: ignore[operator]
            if should:
                fulcrum_seen = True
            if is_f != should:
                out.append(
                    f"recoveries {sc}/{r['class_id']}: fulcrum flag disagrees with the waterfall"
                )
    ev = {r["scenario"]: r for r in _rows(h, "cp4c.ev_scenarios")}
    for r in ev.values():
        m, x, e = _num(r["metric_value"]), _num(r["multiple_x"]), _num(r["ev"])
        if None not in (m, x, e) and not _close(r["ev"], m * x):  # type: ignore[operator]
            out.append(f"ev_scenarios {r['scenario']}: ev != metric x multiple")
    return out


def _chk_positioning(h: dict) -> list[str]:
    out = []
    for r in _rows(h, "cp1c.positioning"):
        v = [_num(r[k]) for k in ("peer_min", "peer_q1", "peer_median", "peer_q3", "peer_max")]
        if None not in v and v != sorted(v):  # type: ignore[type-var]
            out.append(f"positioning {r['metric_id']}: quartiles are not ordered")
        b = _num(r["borrower_value"])
        if None not in v and b is not None:
            want = "Above" if b > v[2] else "Below" if b < v[2] else "In line"  # type: ignore[operator]
            if r["position"] != want:
                out.append(
                    f"positioning {r['metric_id']}: position {r['position']} but borrower vs median says {want}"
                )
    return out


def _chk_reconciliation(h: dict) -> list[str]:
    out = []
    for r in _rows(h, "cp1.reconciliation_checks"):
        a, b, d = _num(r["reported_value"]), _num(r["calculated_value"]), _num(r["difference"])
        if None not in (a, b, d) and a - b != d:  # type: ignore[operator]
            out.append(f"reconciliation {r['check_id']}: difference does not recompute")
    return out


_TABLE_CHECKS = [
    _chk_period_comparison,
    _chk_cash_conversion,
    _chk_bridge,
    _chk_runway,
    _chk_pressure,
    _chk_covenants,
    _chk_triggers,
    _chk_recoveries,
    _chk_positioning,
    _chk_reconciliation,
]


def check_fit(ctx: Ctx, run: dict) -> list[str]:
    out: list[str] = []
    hs = run["handoffs"]
    if "FIT" not in hs:
        if run.get("fit"):
            out.append("fit results present without a FIT handoff")
        return out
    pf, lh = _rows(hs["FIT"], "snapshot.portfolio_fit"), _rows(hs["FIT"], "fit.limit_headroom")
    rows, lrows = [], []
    for f in run["fit"]:
        inp = f["inputs"]
        res = fit(inp["portfolio"], inp["instruments"], inp["issuer_id"])
        rows += res.rows
        lrows += res.limit_rows
    if pf != rows:
        out.append("snapshot.portfolio_fit differs from the §7 recomputation")
    if lh != lrows:
        out.append("fit.limit_headroom differs from the §7 recomputation")
    if "CP-6" in hs and "cp6.portfolio_recommendation" in hs["CP-6"]["tables"]:
        by = {(r["portfolio_id"], r["instrument"]): r for r in pf}
        for r in _rows(hs["CP-6"], "cp6.portfolio_recommendation"):
            k = (r["portfolio_id"], r["instrument"])
            fr = by.get(k)
            if fr is None:
                out.append(f"cp6.portfolio_recommendation {k}: no Fit row")
                continue
            if r["cap"] != fr["recommendation_cap"] or r["fit_verdict"] != fr["verdict"]:
                out.append(f"cp6.portfolio_recommendation {k}: cap/verdict differ from FIT")
            if r["final"] != weaker(r["uncapped"], r["cap"]):
                out.append(
                    f"cp6.portfolio_recommendation {k}: final is not the weaker of uncapped and cap"
                )
    return out


def check_cp5(run: dict) -> list[str]:
    h = run["handoffs"].get("CP-5")
    if not h or "cp5.module_status" not in h["tables"]:
        return []
    out = []
    for r in _rows(h, "cp5.module_status"):
        m = run["handoffs"].get(r["module_id"])
        if m and m["qa_status"] != r["qa_status"]:
            out.append(
                f"cp5.module_status {r['module_id']}: says {r['qa_status']}, handoff is {m['qa_status']}"
            )
    return out


# ------------------------------------------------------------------------------ real CZR figures
BASE_ROWS = {
    "financials": {
        "Revenue": "revenue",
        "EBITDA (Adjusted, company-defined)": "adjusted_ebitda",
        "FFO": "ffo",
        "CFO": "cfo_adjusted",
        "FCF": "fcf",
        "WC and other (plug)": "working_capital_change",
    },
}


def check_base(ctx: Ctx, run: dict) -> list[str]:
    """No real CZR figure differs from the base data (model cells against the base tables)."""
    out: list[str] = []
    model = run.get("model")
    if not model:
        return out
    cells = _model_cells(model)
    cols = {
        c["period_id"]: c["column_id"]
        for c in model["columns"]
        if c["kind"] != "PF_LTM" and c["kind"] != "PROJECTED"
    }
    names = {
        "FY2023": "FY2023",
        "FY2024": "FY2024",
        "FY2025": "FY2025",
        "H1 2025": "H1_2025",
        "H1 2026": "H1_2026",
        "LTM Q2 2026": "LTM_Q2_2026",
    }
    t = ctx.base["tables"]["financials"]
    sign = {
        "Cash Interest (debt)": ("cash_interest", -1),
        "Leases (cash interest for GLPI and VICI rent)": ("lease_cash_not_in_ebitda", -1),
        "Cash tax": ("cash_taxes", -1),
        "Capex": ("capex", 1),
    }
    for row in t["rows"]:
        lid, sg = (
            (BASE_ROWS["financials"].get(row["label"]), 1)
            if row["label"] in BASE_ROWS["financials"]
            else sign.get(row["label"], (None, 1))
        )
        if not lid or lid not in cells:
            continue
        for cname, cell in zip(t["columns"], row["cells"], strict=True):
            pid = names[cname]
            if cell["v"] is None or pid not in cols:
                continue
            got = cells[lid][cols[pid]]
            if "value" not in got:
                out.append(f"model {lid} {pid}: empty but the base data has {cell['v']}")
            elif q(D(got["value"]) * sg, 0) != q(D(cell["v"]), 0):
                out.append(f"model {lid} {pid}: {got['value']} differs from base {cell['v']}")
    ltm = cols.get("LTM_Q2_2026")
    if ltm:
        for lid, want in (
            ("adjusted_ebitda", "3592"),
            ("total_debt", "11807"),
            ("net_debt", "10842"),
            ("secured_debt", "9468"),
        ):
            v = cells[lid][ltm].get("value")
            if v is None or q(D(v), 0) != D(want):
                out.append(f"model {lid} LTM: {v} differs from base {want}")
        for lid, want in (
            ("metric:total_leverage_adjusted", "3.29"),
            ("metric:net_leverage_adjusted", "3.02"),
            ("metric:senior_secured_leverage", "2.64"),
            ("metric:interest_coverage_adjusted", "1.57"),
        ):
            v = cells[lid][ltm].get("value")
            if v is None or q(D(v), 2) != D(want):
                out.append(f"model {lid} LTM: {v} differs from base {want}")
    return out


# ------------------------------------------------------------------------------ Larchmere
# 0, 1 and 100 in any written form (0.0, 1.0, 100.0, 100.0%, 1.0x) are structural, not a repeated real figure
TRIVIAL_FIGURES = (Decimal(0), Decimal(1), Decimal(100))


def _czr_figure_tokens(ctx: Ctx) -> set[str]:
    toks: set[str] = set()
    for src in (ctx.base["figures"], ctx.fp["figures"]):
        for f in src.values():
            for key in ("raw", "v"):
                v = f.get(key)
                if isinstance(v, str) and re.fullmatch(r"\(?-?[\d,]*\d(\.\d+)?\)?", v):
                    n = re.sub(r"[(),-]", "", v)
                    digits = n.replace(".", "")
                    if (
                        len(digits) >= 4
                        and not re.fullmatch(r"(19|20)\d\d", n)
                        and not n.endswith("00")
                        and Decimal(n) not in TRIVIAL_FIGURES
                    ):
                        toks.add(n)
    return toks


def check_fictional(ctx: Ctx, run: dict) -> list[str]:
    text = json.dumps(run, ensure_ascii=False)
    out = []
    for name in DENY_NAMES:
        if re.search(
            r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text, re.I if len(name) > 5 else 0
        ):
            out.append(f"fictional issuer run contains the real name {name!r}")
    banned = _czr_figure_tokens(ctx)
    seen = set()
    figures_text = re.sub(r"\b[0-9a-f]{64}\b", "", text)  # sha256 digests are not figures
    for tok in re.findall(r"\d[\d,]*\.?\d*", figures_text):
        n = tok.replace(",", "").rstrip(".")
        if n in banned and n not in seen:
            seen.add(n)
            out.append(f"fictional issuer run repeats the real CZR figure {n}")
    if not run["fixture"]["issuer_fictional"]:
        out.append("fixture.issuer_fictional must be true")
    return out


# ------------------------------------------------------------------------------ charts (FIXTURES §5)
def check_charts(ctx: Ctx, run: dict) -> list[str]:
    out: list[str] = []
    owners_present = (
        set(run["handoffs"]) | {"RUN_BRIEF"} | ({"PRIOR_CASE"} if run.get("prior_case") else set())
    )
    got = {c["chart_id"]: c for c in run["charts"]}
    n_a = run["fixture"].get("n_a_charts", {})
    notes = " ".join(run["fixture"]["notes"])
    for cid, ch in ctx.spec["charts"].items():
        need = spec_mod.chart_tables(ch, ctx.spec["tables"], owners_present)
        if need is None:
            continue
        c = got.get(cid)
        if c is None:
            out.append(f"chart {cid} applies to this run but is missing")
            continue
        if "unavailable" in c["data"]:
            if cid not in n_a:
                out.append(f"chart {cid} is an n/a frame but is not a declared exception")
            continue
        for tid in need:
            t = c["data"].get(tid)
            if not t or not any(any(x != GAP for x in r) for r in t["rows"]):
                out.append(f"chart {cid}: no populated rows from {tid}")
        if cid not in notes:
            out.append(f"chart {cid} is not listed in fixture.notes")
        if (
            cid in ("chart.model_strip", "chart.forecast_lines", "chart.credit_path")
            and "PROJECTION" in run["handoffs"]
        ):
            ps = c["data"].get("model.projection_summary", {"rows": []})
            cases = (
                {r[ps["columns"].index("case")] for r in ps["rows"]}
                if "case" in ps.get("columns", [])
                else set()
            )
            if cases != {"BASE", "DOWNSIDE"}:
                out.append(
                    f"chart {cid}: projection series are {sorted(cases)}, expected BASE and DOWNSIDE"
                )
    for cid in n_a:
        if cid not in got:
            out.append(f"declared n/a chart {cid} is not in the run")
    return out


# ------------------------------------------------------------------------------ whole run
def check(run: dict, ctx: Ctx | None = None) -> list[str]:
    ctx = ctx or load_ctx()
    out: list[str] = []
    if run.get("schema") != "rbot-run/1":
        out.append("schema must be rbot-run/1")
    for k in (
        "fixture",
        "run_brief",
        "plan",
        "steps",
        "handoffs",
        "charts",
        "front_page_blocks",
        "limitations",
        "model",
        "fit",
        "prior_case",
    ):
        if k not in run:
            out.append(f"run lacks {k}")
    if out:
        return out
    plan = ctx.spec["pathways"][run["pathway"]]["depths"][run["depth"]]
    if run["plan"] != plan:
        out.append("plan differs from the interfaces §5 list")
    for step in plan:
        s = run["steps"].get(step)
        if s is None:
            out.append(f"plan step {step} has no step status")
        elif s["status"] in ("accepted", "blocked"):
            if step not in run["handoffs"]:
                out.append(f"step {step} is {s['status']} but has no handoff")
        elif s["status"] == "skipped":
            if not s.get("reason"):
                out.append(f"step {step} is skipped without a reason")
        else:
            out.append(f"step {step}: status {s['status']}")
    rb = run["run_brief"]
    for tid, t in rb["tables"].items():
        out += table_problems(ctx.spec, "RUN_BRIEF", tid, t, False)
    for tid in ctx.spec["module_tables"]["RUN_BRIEF"]:
        if tid not in rb["tables"]:
            out.append(f"run_brief lacks {tid}")
    for step, h in run["handoffs"].items():
        out += check_handoff(ctx, step, h, run)
    out += check_derived(ctx, run)
    n_blocks = len(ctx.spec["front_pages"][run["front_page"]]["blocks"])
    if len(run["front_page_blocks"]) != n_blocks:
        out.append(
            f"front_page_blocks has {len(run['front_page_blocks'])} blocks, the spec has {n_blocks}"
        )
    for b in run["front_page_blocks"]:
        if not b["shown"] and not b["reason"]:
            out.append(f"block {b['id']} hidden without a reason")
    out += check_charts(ctx, run)
    if run["fixture"]["issuer_fictional"]:
        out += check_fictional(ctx, run)
    else:
        out += check_base(ctx, run)
    return out
