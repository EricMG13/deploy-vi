"""CZR Prior Case (interfaces §11.6): the earlier Earnings Update dated 2026-08-05 and its `prior/diff`.

`build(ctx)` returns the run's Prior Case block `{report, report_date, run_id, pathway, depth, tables}`; the generator
diffs `tables` against the current run with `diff_tables`. The prior Report is synthetic (no earlier RBOT Report
exists), so its tables are *derived* from the current run's tables at diff time with the prior values from
`synthetic-facts.json -> czr.prior_case` applied, plus a few rows the current run adds or drops. Prior LTM revenue and
Adjusted EBITDA are real figures: LTM to 31 March 2026 = FY2025 + (H1 2026 - Q2 2026) - (H1 2025 - Q2 2025).

Everything not overridden is identical to the current run, so the diff lists only the intended changes.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from core import GAP, Ctx, Handoff, compute, plain
from czr.cp_3 import FACTS
from helpers import join_marks
from run import DIFF_KEYS

PRIOR = FACTS["prior_case"]
PV = PRIOR["prior_values"]
PRIOR_FILE = "../20260805-czr-earnings-update/report.html"


def prior_ltm(
    ctx: Ctx, h: Handoff | None = None, stem: str = "adj_ebitda"
) -> tuple[Decimal, str, str]:
    """(LTM to 31 March 2026, calc string, markers) for a flow stem, from real figures."""
    keys = [f"{stem}_{k}" for k in ("fy2025", "h1_2026", "q2_2026", "h1_2025", "q2_2025")]
    v = {k: ctx.val(k) for k in keys}
    val, calc = compute(
        f"LTM {stem} to 31 March 2026",
        "fy + (h1 - q2) - (ph1 - pq2)",
        0,
        "",
        fy=v[keys[0]],
        h1=v[keys[1]],
        q2=v[keys[2]],
        ph1=v[keys[3]],
        pq2=v[keys[4]],
    )
    marks = ""
    if h is not None:
        marks = join_marks(*(h.cite_fig(k) for k in keys))
    return val, calc, marks


def current_tables(ctx: Ctx, run_id: str) -> dict[str, dict]:
    """Every table built so far for the run (run brief, modules, host steps), excluding CP-8 itself."""
    out: dict[str, dict] = {}
    for (rid, step), hd in ctx.built.items():
        if rid == run_id and step != "CP-8":
            out.update(hd.tables)
    return out


def _latest_run(ctx: Ctx) -> str | None:
    runs = [rid for (rid, step) in ctx.built if step == "RUN_BRIEF"]
    return runs[-1] if runs else None


def _copy(t: dict) -> dict:
    return {"columns": list(t["columns"]), "rows": [list(r) for r in t["rows"]]}


def derive_tables(ctx: Ctx) -> dict[str, dict]:
    """The prior Report's Front Page tables, derived from the current run (see the module docstring)."""
    rid = _latest_run(ctx)
    if rid is None:
        return {}
    cur = current_tables(ctx, rid)
    out: dict[str, dict] = {}
    # credit view: the three words from the facts file
    if "snapshot.credit_view" in cur:
        t = _copy(cur["snapshot.credit_view"])
        cols = t["columns"]
        for r in t["rows"]:
            r[cols.index("credit_score")] = PV["credit_score"]
            r[cols.index("credit_direction")] = PV["credit_direction"]
            r[cols.index("sector_outlook")] = PV["sector_outlook"]
        out["snapshot.credit_view"] = t
    # financials: LTM revenue, Adjusted EBITDA (real, to 31 March 2026), margin, net leverage (facts)
    if "snapshot.financials" in cur:
        t = _copy(cur["snapshot.financials"])
        cols = t["columns"]
        li, ci = cols.index("line_id"), cols.index("ltm")
        rev, _, _ = prior_ltm(ctx, None, "net_revenues")
        ebitda, _, _ = prior_ltm(ctx, None, "adj_ebitda")
        margin = plain(ebitda / rev * 100, 1)
        override = {
            "revenue": plain(rev),
            "adjusted_ebitda": plain(ebitda),
            "metric:adjusted_ebitda_margin": margin,
            "metric:net_leverage_adjusted": PV["net_leverage_x"],
        }
        for r in t["rows"]:
            if r[li] in override:
                r[ci] = override[r[li]]
        out["snapshot.financials"] = t
    # watch items: the prior Report did not list cash conversion and did list the merger-financing catalyst
    if "cp2.watch_items" in cur:
        t = _copy(cur["cp2.watch_items"])
        cols = t["columns"]
        ti = cols.index("trigger")
        gone = [r for r in t["rows"] if r[ti] == "Cash conversion"]
        t["rows"] = [r for r in t["rows"] if r[ti] != "Cash conversion"]
        if gone:
            row = [GAP] * len(cols)
            row[ti] = "Merger financing terms disclosed by Q3 2026"
            row[cols.index("threshold_or_signal")] = "Amount and ranking of the committed financing"
            row[cols.index("why_it_matters")] = "Sets post-close leverage"
            row[cols.index("credit_impact")] = "Could move leverage and ratings"
            t["rows"].append(row)
        out["cp2.watch_items"] = t
    # strengths and weaknesses: a weakness the prior Report carried is gone, a strength is new
    if "snapshot.strengths_weaknesses" in cur:
        t = _copy(cur["snapshot.strengths_weaknesses"])
        cols = t["columns"]
        ki, li2 = cols.index("kind"), cols.index("label")
        dropped = [r for r in t["rows"] if r[ki] == "Strength"][-1:]
        t["rows"] = [r for r in t["rows"] if r not in dropped]
        row = [GAP] * len(cols)
        row[ki], row[li2] = "Weakness", "Merger financing terms unknown"
        row[cols.index("text")] = "The merger adds debt of unknown size."
        t["rows"].append(row)
        out["snapshot.strengths_weaknesses"] = t
    for tid in DIFF_KEYS:  # every other Front Page table is the same as in the current run
        if tid in cur and tid not in out:
            out[tid] = _copy(cur[tid])
    return out


class LazyPrior(dict):
    """A dict whose `tables` entry is derived from the current run each time it is read."""

    def __init__(self, ctx: Ctx, base: dict[str, Any]) -> None:
        super().__init__(base)
        self._ctx = ctx

    def __getitem__(self, key: str) -> Any:
        if key == "tables":
            return derive_tables(self._ctx)
        return super().__getitem__(key)


def build(ctx: Ctx) -> dict:
    """The Prior Case block for the Earnings Update run (named in `RUNS` as `czr.prior_case:build`)."""
    return LazyPrior(
        ctx,
        {
            "report": PRIOR_FILE,
            "report_date": PRIOR["report_date"],
            "run_id": PRIOR["prior_run_id"],
            "pathway": PRIOR["pathway"],
            "depth": PRIOR["depth"],
        },
    )
