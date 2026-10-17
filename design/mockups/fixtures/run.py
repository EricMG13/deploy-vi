"""Assemble `rbot-run/1` from content modules and host steps, plus the Prior Case diff and the chart builder."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

import spec as spec_mod
from core import GAP, MCTX, Ctx, D, FixtureError, Handoff, plain, q
from fit import FitResult, fit, fit_handoff
from model import ModelBuilder, model_handoff, projection_handoff

HOST_STEPS = ("MODEL", "PROJECTION", "FIT")
GENERATED_AT = "2026-10-17T00:00:00Z"

CHART_KINDS = {
    "chart.model_strip": "lineStrip",
    "chart.maturity_wall": "stackedColumns",
    "chart.capital_structure": "stackedBar",
    "chart.ebitda_bridge": "waterfall",
    "chart.adjusted_debt_bridge": "waterfall",
    "chart.headline_results": "columns",
    "chart.kpi_changes": "dumbbell",
    "chart.peer_ranges": "rangeStrip",
    "chart.implied_ev": "rangeStrip",
    "chart.liquidity_sources": "stackedColumns",
    "chart.cash_uses": "stackedColumns",
    "chart.liquidity_bridge": "waterfall",
    "chart.rate_fx_tornado": "tornado",
    "chart.downside_tornado": "tornado",
    "chart.risk_matrix": "riskMatrix",
    "chart.forecast_lines": "lines",
    "chart.credit_path": "lines",
    "chart.rating_triggers": "bullet",
    "chart.rv_loan": "dumbbell",
    "chart.rv_hy": "dumbbell",
    "chart.talk_range": "rangeStrip",
    "chart.factor_scores": "bar",
    "chart.spread_curve": "scatter",
    "chart.implied_pd": "bar",
    "chart.lme_exposure": "columns",
    "chart.funding_gap": "stackedColumns",
    "chart.covenant_headroom": "bullet",
    "chart.basket_capacity": "stackedColumns",
    "chart.value_allocation": "waterfall",
    "chart.recovery_by_class": "columns",
    "chart.issue_counts": "stackedColumns",
    "chart.topic_counts": "stackedColumns",
    "chart.expected_realised": "dumbbell",
    "chart.what_changed": "dumbbell",
    "chart.fit_bullets": "bullet",
}

# Prior Case diff keys (interfaces §11.6): table -> key columns
DIFF_KEYS = {
    "snapshot.company_profile": [],
    "snapshot.credit_view": [],
    "snapshot.recommendation": ["strategy"],
    "snapshot.instrument_recommendation": ["facility_id"],
    "snapshot.instrument_levels": ["facility_id"],
    "snapshot.capital_structure": ["facility_id"],
    "snapshot.capital_structure_totals": ["line"],
    "snapshot.ebitda_adjustments": ["line"],
    "snapshot.financials": ["line_id"],
    "snapshot.strengths_weaknesses": ["kind", "label"],
    "snapshot.catalysts": ["event"],
    "snapshot.portfolio_fit": ["portfolio_id", "facility_id"],
    "cp2.watch_items": ["trigger"],
    "cp4.covenant_tests": ["test"],
    "cp2h.rating_triggers": ["agency", "metric"],
}


class IncompleteRun(FixtureError):
    """Content modules are missing; the run is not written."""

    def __init__(self, missing: list[str]) -> None:
        super().__init__("incomplete: missing " + ", ".join(missing))
        self.missing = missing


def is_number(s: str) -> bool:
    try:
        D(s)
        return s not in (GAP, "")
    except FixtureError:
        return False


def _index(t: dict | None, keys: list[str]) -> dict[tuple, dict]:
    if not t:
        return {}
    rows = [dict(zip(t["columns"], r, strict=True)) for r in t["rows"]]
    return {tuple(r.get(k, "") for k in keys): r for r in rows}


def diff_tables(prior: dict[str, dict], cur: dict[str, dict]) -> dict:
    """§11.6 `prior/diff.json` changes between two {table_id: {columns, rows}} maps."""
    changes: list[dict] = []
    for tid, keys in DIFF_KEYS.items():
        if tid not in prior and tid not in cur:
            continue

        a, b = _index(prior.get(tid), keys), _index(cur.get(tid), keys)
        for key in list(dict.fromkeys(list(a) + list(b))):
            kstr = " | ".join(key) if key else "(single row)"
            if key not in b:
                changes.append(
                    {
                        "table": tid,
                        "key": kstr,
                        "field": "*",
                        "prior": "present",
                        "current": GAP,
                        "kind": "removed",
                        "numeric": False,
                    }
                )
            elif key not in a:
                changes.append(
                    {
                        "table": tid,
                        "key": kstr,
                        "field": "*",
                        "prior": GAP,
                        "current": "present",
                        "kind": "added",
                        "numeric": False,
                    }
                )
            else:
                for f, cv in b[key].items():
                    if f in ("cite", "rationale", "reason") or f in keys:
                        continue
                    pv = a[key].get(f, GAP)
                    kind = "unchanged" if pv == cv else "changed"
                    changes.append(
                        {
                            "table": tid,
                            "key": kstr,
                            "field": f,
                            "prior": pv,
                            "current": cv,
                            "kind": kind,
                            "numeric": is_number(pv) and is_number(cv),
                        }
                    )
    return {"changes": changes}


@dataclass
class Run:
    ctx: Ctx
    name: str
    run_id: str
    pathway: str
    depth: str
    issuer: dict  # name, id, ticker
    primary: bool = False
    variant: str = ""
    analysis_date: str = "2026-10-02"
    report_date: str = "2026-10-17"
    issuer_fictional: bool = False
    notes: list[str] = field(default_factory=list)
    portfolios: list[dict] = field(default_factory=list)
    fit_exclude: tuple[str, ...] = ()
    deep_research: bool = True
    prior_case: dict | None = None  # {report, report_date, run_id, pathway, depth, tables}
    n_a_charts: dict[str, str] = field(
        default_factory=dict
    )  # chart_id -> reason a state variant blanks it
    approval_limitations: list[str] = field(default_factory=list)
    skip_reasons: dict[str, str] = field(
        default_factory=dict
    )  # step -> reason shown when the plan skips it (default: the generic wording)

    def __post_init__(self) -> None:
        self.plan = list(self.ctx.spec["pathways"][self.pathway]["depths"][self.depth])
        self.front_page = self.ctx.spec["pathways"][self.pathway]["front_page"]
        self.handoffs: dict[str, Handoff] = {}
        self.skips: dict[str, str] = {}
        self.run_brief: Handoff | None = None
        self.model: ModelBuilder | None = None
        self.fits: list[FitResult] = []
        self.missing: list[str] = []

    # -------------------------------------------------------------- building
    def build(
        self, builders: dict[str, Callable[..., Handoff]], run_brief_builder: Callable[..., Handoff]
    ) -> None:
        ctx = self.ctx
        ctx.built = getattr(ctx, "built", {})
        ctx.models = getattr(ctx, "models", {})
        ctx.fits = getattr(ctx, "fits", {})
        ctx.primary_runs[self.run_id] = self.primary
        self.run_brief = run_brief_builder(ctx, self.run_id, self.variant)
        ctx.built[(self.run_id, "RUN_BRIEF")] = self.run_brief
        for step in self.plan:
            if step in HOST_STEPS:
                self._host(step)
            elif step == "CP-DR" and not self.deep_research:
                self.skips[step] = self.skip_reasons.get(step, "not approved")
            elif step == "CP-8" and self.prior_case is None:
                self.skips[step] = self.skip_reasons.get(step, "no prior case")
            elif step in builders:
                h = builders[step](ctx, self.run_id, self.variant)
                self.handoffs[step] = h
                ctx.built[(self.run_id, step)] = h
            else:
                self.missing.append(step)
        if self.missing:
            raise IncompleteRun(self.missing)

    def _host(self, step: str) -> None:
        ctx = self.ctx
        if self.missing:
            self.skips[step] = "inputs missing"
            return
        if step == "MODEL":
            cp1 = self.handoffs.get("CP-1")
            if cp1 is None:
                self.skips[step] = "CP-1 not run"
                return
            self.model = ModelBuilder(cp1, self.run_brief, self.handoffs.get("CP-1D"), self.run_id)  # type: ignore[arg-type]
            ctx.models[self.run_id] = self.model
            h = model_handoff(self.model, self.run_id)
        elif step == "PROJECTION":
            cp2g = self.handoffs.get("CP-2G")
            if cp2g is None or self.model is None:
                self.skips[step] = "CP-2G not run"
                return
            for case, years, drivers in cp2g.meta.get("projection", []):
                self.model.add_projection(case, years, drivers)
            h = projection_handoff(self.model, self.run_id)
            ctx.models[self.run_id] = self.model
            # the Model handoff must show the projected columns' limitations too
            self.handoffs["MODEL"] = model_handoff(self.model, self.run_id)
            ctx.built[(self.run_id, "MODEL")] = self.handoffs["MODEL"]
        else:
            if not self.portfolios:
                self.skips[step] = "no portfolio context"
                return
            from fit_inputs import fit_instruments  # local: needs built handoffs

            insts = fit_instruments(
                ctx, self.run_id, self.handoffs, self.run_brief, self.fit_exclude
            )  # type: ignore[arg-type]
            self.fits = [fit(p, insts, self.issuer["id"]) for p in self.portfolios]
            ctx.fits[self.run_id] = self.fits
            h = fit_handoff(ctx, self.run_id, self.issuer["id"], self.analysis_date, self.fits)
        self.handoffs[step] = h
        ctx.built[(self.run_id, step)] = h

    # -------------------------------------------------------------- tables view
    def all_tables(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        if self.run_brief:
            out.update(self.run_brief.tables)
        for h in self.handoffs.values():
            out.update(h.tables)
        return out

    def table_owner_present(self, tid: str) -> bool:
        owners = self.ctx.spec["tables"][tid]["owners"]
        return any(o in self.handoffs or o == "RUN_BRIEF" for o in owners)

    # -------------------------------------------------------------- front page blocks
    def blocks(self) -> list[dict]:
        tables = self.all_tables()
        gate = None
        if "cp4c.distress_gate" in tables:
            rows = [
                dict(zip(tables["cp4c.distress_gate"]["columns"], r, strict=True))
                for r in tables["cp4c.distress_gate"]["rows"]
            ]
            overall = [r for r in rows if r["trigger"].lower().startswith("overall")]
            sts = [r["status"] for r in (overall or rows)]
            gate = "Met" if "Met" in sts else "Unclear" if "Unclear" in sts else "Not met"
        out = []
        for b in self.ctx.spec["front_pages"][self.front_page]["blocks"]:
            present = [t for t in b["tables"] if t in tables]
            shown, reason = True, None
            cond = b["condition"]
            if cond == "primary" and not self.primary:
                shown, reason = False, "not a Primary run"
            elif cond == "portfolios" and not self.fits:
                shown, reason = False, "no portfolio attached"
            elif cond == "prior_case" and self.prior_case is None:
                shown, reason = False, "no Prior Case accepted"
            elif cond == "gate_met" and gate not in ("Met", "Unclear"):
                shown, reason = False, f"distress gate {'not met' if gate else 'not assessed'}"
            elif cond == "rows_present" and not any(tables[t]["rows"] for t in present):
                shown, reason = False, "no rows to show"
            elif cond == "pf_ltm" and not (self.model and self.model.pf_col):
                reason = "PF interest rows hidden: no PF-LTM column"
            elif cond == "projection" and "PROJECTION" not in self.handoffs:
                reason = "projected series hidden: PROJECTION did not run"
            elif cond == "unsecured_present" and not self._has_unsecured():
                reason = "unsecured rows hidden: none in the capital structure"
            if shown and not present:
                owners = sorted(
                    {o for t in b["tables"] for o in self.ctx.spec["tables"][t]["owners"]}
                )
                skipped = [(o, self.skips[o]) for o in owners if o in self.skips]
                if skipped:
                    shown, reason = False, f"{skipped[0][0]} skipped — {skipped[0][1]}"
                else:
                    shown, reason = False, "no producer in this Pathway depth"
            out.append(
                {
                    "id": b["id"],
                    "title": b["title"],
                    "shown": shown,
                    "reason": reason,
                    "line": None if shown else f"{b['title']}: {reason}",
                    "tables": b["tables"],
                }
            )
        return out

    def _has_unsecured(self) -> bool:
        t = self.all_tables().get("snapshot.capital_structure")
        if not t:
            return False
        i = t["columns"].index("secured")
        return any(r[i] == "No" for r in t["rows"])

    # -------------------------------------------------------------- charts
    def charts(self) -> list[dict]:
        tables = self.all_tables()
        spec = self.ctx.spec
        in_set = spec["chart_sets"][self.front_page]
        out = []
        for cid, ch in spec["charts"].items():
            owners = (
                set(self.handoffs) | {"RUN_BRIEF"} | ({"PRIOR_CASE"} if self.prior_case else set())
            )
            need = spec_mod.chart_tables(ch, spec["tables"], owners)
            if need is None:
                continue
            reads = {t: ch["reads"][t] for t in need}
            where = self._where(cid, ch)
            data, note = self._chart_data(cid, reads, tables)
            if cid in self.n_a_charts:
                data = {"unavailable": self.n_a_charts[cid]}
            out.append(
                {
                    "chart_id": cid,
                    "where": where,
                    "kind": CHART_KINDS[cid],
                    "origin": "host" if ch["origin_text"].lower().startswith("host") else "model",
                    "front_page_set": cid in in_set,
                    "tables": list(reads),
                    "data": data,
                    "summary": note,
                }
            )
        return out

    def _where(self, cid: str, ch: dict) -> str:
        n = spec_mod.chart_block(ch["where_text"], self.front_page)
        if n is not None:
            return f"front_page:{n}"
        m = re.search(r"Analysis › (CP-[0-9A-Z]+)", ch["where_text"])
        if m:
            return f"analysis:{m.group(1)}"
        if "Model tab" in ch["where_text"]:
            return "model_tab"
        if "What changed tab" in ch["where_text"]:
            return "what_changed_tab"
        if "Portfolio Fit tab" in ch["where_text"]:
            return "portfolio_fit_tab"
        return "analysis"

    def _chart_data(
        self, cid: str, reads: dict[str, list[str]], tables: dict[str, dict]
    ) -> tuple[dict, str]:
        data: dict[str, Any] = {}
        total_rows = 0
        for tid, cols in reads.items():
            if tid == "prior/diff.json":
                ch = (
                    diff_tables(self.prior_case["tables"], tables)["changes"]
                    if self.prior_case
                    else []
                )  # type: ignore[index]
                num = [
                    [c["table"], c["key"], c["field"], c["prior"], c["current"]]
                    for c in ch
                    if c["numeric"] and c["kind"] == "changed"
                ]
                data[tid] = {"columns": ["table", "key", "field", "prior", "current"], "rows": num}
                total_rows += len(num)
                continue
            t = tables.get(tid)
            if t is None:
                data[tid] = {"columns": [], "rows": []}
                continue
            names = t["columns"]
            rows = t["rows"]
            if tid == "model.metrics" and cols:
                wanted = {c.removesuffix("_x") for c in cols}
                rows = [r for r in rows if r[0] in wanted]
            if tid == "snapshot.relative_value" and cid in ("chart.rv_loan", "chart.rv_hy"):
                prefix = "Loan" if cid == "chart.rv_loan" else "HY"
                rows = [x for x in rows if x[names.index("block")].startswith(prefix)]
            if tid == "model.house":
                rows = [x for x in rows if x[0] == "Adjusted debt"]
            if tid == "model.summary":
                lines = {
                    "chart.model_strip": {"liquidity"},
                    "chart.forecast_lines": {"revenue", "adjusted_ebitda", "fcf"},
                }.get(cid)
                if lines:
                    rows = [r for r in rows if r[0] in lines]
            use = [c for c in cols if c in names] or names
            if tid in ("model.metrics", "model.summary"):
                use = names
            if tid == "model.projection_summary":  # a series needs its case and year
                use = ["case", "fiscal_year"] + [c for c in use if c not in ("case", "fiscal_year")]
            idx = [names.index(c) for c in use]
            proj = [[r[i] for i in idx] for r in rows]
            data[tid] = {"columns": use, "rows": proj}
            total_rows += sum(1 for r in proj if any(c != GAP for c in r))
        return data, f"{total_rows} populated row(s) from {', '.join(reads)}"

    # -------------------------------------------------------------- limitations
    def limitations(self) -> dict:
        t = self.handoffs.get("CP-5")
        cp5 = t.rows("cp5.limitations") if t and "cp5.limitations" in t.tables else []
        named = (
            " ".join(r["module_id"] + " " + r["limitation"] for r in cp5)
            + " "
            + " ".join(self.approval_limitations)
        )
        unforeseen = [
            f"{s}: skipped — {r}"
            for s, r in self.skips.items()
            if s not in ("CP-DR", "CP-8", "PROJECTION", "FIT")
        ]
        for s, h in self.handoffs.items():
            if h.qa_status == "Blocked":
                unforeseen.append(f"{s}: Blocked handoff")
            elif h.qa_status == "Restricted" and s not in named:
                unforeseen.append(
                    f"{s}: accepted Restricted, named by no cp5 limitation or approval entry"
                )
        if self.model:
            unforeseen += [
                f"MODEL {c}: {m}" for c, m, _, _ in self.model.limits if c != "PF_EQUALS_LTM"
            ]
        return {"approval": self.approval_limitations, "cp5": cp5, "unforeseen": unforeseen}

    # -------------------------------------------------------------- output
    def to_json(self) -> dict:
        rb = self.run_brief.to_json()  # type: ignore[union-attr]
        handoffs, steps = {}, {}
        for step in self.plan:
            kind = "host" if step in HOST_STEPS else "module"
            if step in self.handoffs:
                hj = self.handoffs[step].to_json()
                handoffs[step] = hj
                steps[step] = {
                    "kind": kind,
                    "status": hj["status"],
                    "qa_status": hj["qa_status"],
                    "handoff": f"handoffs/{step}.md",
                    "sha256": hj["sha256"],
                    "attempts": 1,
                    "reason": "",
                }
            else:
                steps[step] = {"kind": kind, "status": "skipped", "reason": self.skips[step]}
        charts = self.charts()
        applied = [c["chart_id"] for c in charts if "unavailable" not in c["data"]]
        blank = [
            f"{c['chart_id']} ({c['data']['unavailable']})"
            for c in charts
            if "unavailable" in c["data"]
        ]
        notes = (
            list(self.notes)
            + [f"charts with data: {', '.join(applied)}"]
            + ([f"charts drawn as n/a frames: {'; '.join(blank)}"] if blank else [])
        )
        prior = None
        if self.prior_case is not None:
            diff = diff_tables(self.prior_case["tables"], self.all_tables())
            prior = {
                "report": self.prior_case["report"],
                "report_date": self.prior_case["report_date"],
                "diff": {
                    "prior": {
                        k: self.prior_case[k] for k in ("run_id", "report_date", "pathway", "depth")
                    },
                    **diff,
                },
            }
        return {
            "schema": "rbot-run/1",
            "fixture": {
                "kind": "design",
                "real_first": not self.issuer_fictional,
                "issuer_fictional": self.issuer_fictional,
                "variant": self.variant,
                "n_a_charts": self.n_a_charts,
                "notes": notes,
            },
            "rbot_version": "design-fixture",
            "run_id": self.run_id,
            "generated_at": GENERATED_AT,
            "run_brief": {"front_matter": rb["front_matter"], "tables": rb["tables"]},
            "pathway": self.pathway,
            "depth": self.depth,
            "primary": self.primary,
            "front_page": self.front_page,
            "plan": self.plan,
            "steps": steps,
            "handoffs": handoffs,
            "model": self.model.to_json() if self.model else None,
            "fit": [f.to_json() for f in self.fits],
            "charts": charts,
            "front_page_blocks": self.blocks(),
            "limitations": self.limitations(),
            "prior_case": prior,
        }


def years_between(d0: str, d1: str) -> Decimal:
    return q(
        MCTX.divide(
            Decimal((date.fromisoformat(d1) - date.fromisoformat(d0)).days), Decimal("365.25")
        ),
        2,
    )


__all__ = ["CHART_KINDS", "Run", "IncompleteRun", "diff_tables", "plain", "years_between"]
