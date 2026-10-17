"""ModelBuilder: `rbot-model/1` (interfaces §6) built from a CP-1 handoff (and CP-1D, Run Brief).

Reads the CP-1 registers exactly as `rbot model` would: nothing is taken from the base data directly, so
content modules for any issuer feed it the same way. Pure Decimal; model.json values carry at most 10 decimals.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from core import GAP, MCTX, D, FixtureError, Handoff, compute, fpct, fx, plain, q, ratio

REASONS = (
    "NOT_PROJECTED",
    "NOT_APPLICABLE",
    "NOT_SOURCED",
    "COMPONENT_MISSING",
    "ZERO_OR_NEGATIVE_DENOMINATOR",
    "NOT_STATED",
)
UNIT_SUFFIX = {"MILLIONS": " m", "THOUSANDS": " k", "UNITS": ""}
SUB_ANNUAL = ("YTD", "PYTD", "QUARTER")


class ModelInputError(ValueError):
    """CP-1's registers are malformed (names the table, row and column)."""


@dataclass
class Col:
    column_id: str
    kind: str
    label: str
    period_id: str
    fiscal_year: str | None
    end_date: str
    days: int
    case: str | None = None
    start_date: str | None = None

    def to_json(self) -> dict:
        return {
            "column_id": self.column_id,
            "kind": self.kind,
            "label": self.label,
            "period_id": self.period_id,
            "fiscal_year": self.fiscal_year,
            "end_date": self.end_date,
            "days": self.days,
            "case": self.case,
        }


@dataclass
class Cell:
    value: Decimal | None = None
    reason: str | None = None
    basis: str | None = None
    stated: Decimal | None = None
    note: str | None = None
    sources: list[dict] = field(default_factory=list)

    def to_json(self, column_id: str) -> dict:
        out: dict[str, Any] = {"column_id": column_id}
        if self.value is not None:
            out["value"] = plain(q(self.value, 10))
        else:
            out["reason"] = self.reason
        out["basis"] = self.basis
        if self.stated is not None:
            out["stated"] = plain(q(self.stated, 10))
        if self.note:
            out["note"] = self.note
        out["sources"] = self.sources[:8]
        return out


@dataclass
class Line:
    line_id: str
    band: int
    label: str
    kind: str
    unit: str
    unit_label: str
    fn: Callable[[Col], Cell]
    rank: int | None = None
    terms: dict | None = None
    formula: str | None = None
    cells: dict[str, Cell] = field(default_factory=dict)

    def to_json(self, cols: list[Col]) -> dict:
        return {
            "line_id": self.line_id,
            "band": self.band,
            "label": self.label,
            "kind": self.kind,
            "unit": self.unit,
            "unit_label": self.unit_label,
            "rank": self.rank,
            "terms": self.terms,
            "formula": self.formula,
            "cells": [
                self.cells[c.column_id].to_json(c.column_id)
                for c in cols
                if c.column_id in self.cells
            ],
        }


def rank_of(seniority: str, secured: str) -> int:
    t = f"{seniority} {secured}".lower()
    if "second lien" in t or "junior secured" in t or "2l" in t.split():
        return 2
    if "unsecured" in t and "senior" in t:
        return 3
    if "subordinat" in t:
        return 4
    if "unsecured" in t:
        return 3
    if "secured" in t or "first lien" in t or "super" in t or "dip" in t:
        return 1
    return 9


def is_revolver(ftype: str, fid: str = "") -> bool:
    t = ftype.upper().strip()
    return t.startswith("REVOLV") or t == "RCF" or fid.lower().endswith("rcf")


def parse_rate(text: str) -> Decimal | None:
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", text or "")
    return D(m.group(1)) if m else None


def fixed_rate_of(t: dict) -> Decimal | None:
    """Coupon (percent) of a fixed-rate facility row, or None for a floating one."""
    if t.get("reference_rate", GAP) != GAP:
        return None
    if t.get("fixed_rate", GAP) != GAP:
        return D(t["fixed_rate"].rstrip("%"))
    return parse_rate(t.get("margin_or_coupon", ""))


class ModelBuilder:
    def __init__(
        self,
        cp1: Handoff,
        run_brief: Handoff,
        cp1d: Handoff | None = None,
        run_id: str | None = None,
        generated_at: str = "2026-10-17T00:00:00Z",
    ) -> None:
        self.cp1, self.rb, self.cp1d = cp1, run_brief, cp1d
        self.run_id = run_id or cp1.run_id
        self.generated_at = generated_at
        self.limitations: list[tuple[str, str, str | None, str | None]] = []
        self.projection_rows: dict[str, dict[int, dict]] = {}
        self.projection_interest: list[dict] = []
        self.forecast_checks: list[dict] = []
        self.forecast_status = "none"
        self.proj_acct: dict[tuple[str, str], Decimal] = {}
        self.lines: dict[str, Line] = {}
        self.cols: list[Col] = []
        self._read()
        self._build_columns()
        self._pf_rows = self._pf_from_cp1()
        self._finish_pf()
        self._register_lines()
        self.evaluate()

    # ------------------------------------------------------------ reading CP-1
    def _need(self, table_id: str, cols: list[str]) -> list[dict]:
        if table_id not in self.cp1.tables:
            raise ModelInputError(f"CP-1 table {table_id} is missing")
        rows = self.cp1.rows(table_id)
        for i, r in enumerate(rows):
            for c in cols:
                if c not in r:
                    raise ModelInputError(f"CP-1 {table_id} row {i}: column {c} is missing")
        return rows

    def _sources(self, source_id: str, locator: str = "") -> list[dict]:
        out = []
        for m in re.findall(r"\[(C\d+)\]", source_id or ""):
            c = self.cp1.citation(m)
            out.append(
                {
                    "module": "CP-1",
                    "citation_id": c["id"],
                    "source": c["source"],
                    "locator": c["locator"],
                    "excerpt": c["excerpt"],
                }
            )
        return out

    def _read(self) -> None:
        self.periods = self._need(
            "cp1.model_period_register", ["period_id", "period_type", "end_date"]
        )
        cur = {(p["currency"], p["unit"]) for p in self.periods}
        if len(cur) != 1:
            raise ModelInputError(
                f"CP-1 model_period_register: one currency and unit per run, found {cur}"
            )
        self.currency, self.unit = next(iter(cur))
        ent = self.cp1.rows("cp1.entity_profile") if "cp1.entity_profile" in self.cp1.tables else []
        for e in ent:
            if (e["reporting_currency"], e["reporting_unit"]) != (self.currency, self.unit):
                raise ModelInputError(
                    "CP-1 entity_profile currency/unit differ from the period register"
                )
        self.perimeter = ent[0]["perimeter"] if ent else ""
        self.acct: dict[tuple[str, str], dict] = {}
        for i, r in enumerate(
            self._need("cp1.model_account_register", ["metric_id", "period_id", "value"])
        ):
            key = (r["metric_id"], r["period_id"])
            if key in self.acct:
                raise ModelInputError(f"CP-1 model_account_register row {i}: duplicate {key}")
            self.acct[key] = {
                "value": None if r["value"] == GAP else D(r["value"]),
                "status": r["calculation_status"],
                "sources": self._sources(r["source_id"]),
                "locator": r["source_locator"],
            }
        self.bridge = self.cp1.rows("cp1.adjusted_ebitda_bridge")
        self.segments = self.cp1.rows("cp1.segment_revenue_schedule")
        self.kpis = self.cp1.rows("cp1.operating_kpi_schedule")
        self.facilities = self._need(
            "cp1.debt_facility_register", ["facility_id", "period_id", "drawn_amount"]
        )
        self.identity = (
            self.cp1.rows("cp1.instrument_identity")
            if "cp1.instrument_identity" in self.cp1.tables
            else []
        )
        self.equity = (
            self.cp1.rows("cp1.equity_value") if "cp1.equity_value" in self.cp1.tables else []
        )
        hdr = self.rb.rows("snapshot.run_header")[0]
        mult = hdr.get("ssim_ev_multiple_x", GAP)
        self.ssim_ev_multiple = None if mult == GAP else D(mult)
        self.primary = hdr.get("primary") == "Yes"
        self.assess = self.cp1d.rows("cp1d.addback_assessment") if self.cp1d else []
        self.debt_like = self.cp1d.rows("cp1d.debt_like_items") if self.cp1d else []

    def _pf_from_cp1(self) -> list[dict]:
        t = "cp1.pro_forma_adjustment_register"
        return self.cp1.rows(t) if t in self.cp1.tables else []

    def add_pro_forma(self, rows: list[dict]) -> None:
        """Replace the PF rows (register format) and rebuild; normally they come from CP-1."""
        self._pf_rows = rows
        self._finish_pf()
        self.lines.clear()
        self._register_lines()
        self.evaluate()

    # ------------------------------------------------------------ columns
    def _build_columns(self) -> None:
        flows = [p for p in self.periods if p["period_type"] != "PERIOD_END"]
        ytds = sorted((p for p in flows if p["period_type"] == "YTD"), key=lambda p: p["end_date"])
        cols: list[Col] = []

        def mk(p: dict, kind: str, prefix: str) -> Col:
            label = p["period_id"] if kind == "FY" else p["period_id"].replace("_", " ")
            return Col(
                f"{prefix}:{p['period_id']}",
                kind,
                label,
                p["period_id"],
                p["fiscal_year"],
                p["end_date"],
                int(p["day_count"]),
                None,
                p["start_date"],
            )

        for p in sorted(
            (p for p in flows if p["period_type"] == "FY"), key=lambda p: p["end_date"]
        ):
            cols.append(mk(p, "FY", "FY"))
        if ytds:
            for p in ytds[:-1]:
                cols.append(mk(p, "PYTD", "PYTD"))
            cols.append(mk(ytds[-1], "YTD", "YTD"))
        for p in flows:
            if p["period_type"] == "LTM":
                cols.append(mk(p, "LTM", "LTM"))
        for p in sorted(
            (p for p in flows if p["period_type"] == "QUARTER"), key=lambda p: p["end_date"]
        ):
            cols.append(mk(p, "QUARTER", "Q"))
        self.cols = cols
        self.period_ends = {
            p["end_date"]: p["period_id"] for p in self.periods if p["period_type"] == "PERIOD_END"
        }
        self.ltm_col = next((c for c in cols if c.kind == "LTM"), None)

    def _finish_pf(self) -> None:
        self.cols = [c for c in self.cols if c.kind != "PF_LTM"]
        self.pf_adj: dict[str, Decimal] = {}
        ltm = self.ltm_col
        if ltm is None or not self._pf_rows:
            self.pf_col = None
            return
        adj: dict[str, Decimal] = {}
        self.pf_sources: dict[str, list[dict]] = {}
        for i, r in enumerate(self._pf_rows):
            if r["period_id"] != ltm.period_id:
                continue
            m = r["metric_id"]
            if m == "total_debt" and any(
                k.startswith("facility:") for k in (x["metric_id"] for x in self._pf_rows)
            ):
                raise ModelInputError(
                    f"pro_forma_adjustment_register row {i}: total_debt double counts facility rows"
                )
            adj[m] = adj.get(m, Decimal(0)) + D(r["value"])
            self.pf_sources.setdefault(m, []).extend(self._sources(r["source_id"]))
        if not adj:
            self.pf_col = None
            return
        self.pf_adj = adj
        self.pf_col = Col(
            f"PF:{ltm.period_id}",
            "PF_LTM",
            "PF-LTM",
            ltm.period_id,
            ltm.fiscal_year,
            ltm.end_date,
            ltm.days,
        )
        idx = self.cols.index(ltm)
        self.cols.insert(idx + 1, self.pf_col)
        if "cash_interest_paid" not in adj and any(
            k.startswith("facility:") and v > 0 for k, v in adj.items()
        ):
            self.limitations.append(
                (
                    "PF_INTEREST_NOT_SOURCED",
                    "Pro forma interest on the new tranches is not sourced; PF cash interest equals LTM.",
                    None,
                    self.pf_col.column_id,
                )
            )

    @property
    def snapshot_col(self) -> Col | None:
        return self.pf_col or self.ltm_col

    def snapshot_columns(self) -> dict[str, str | None]:
        fys = [c for c in self.cols if c.kind == "FY"][-3:]
        slots: dict[str, str | None] = {"FY-2": None, "FY-1": None, "FY": None}
        for name, c in zip(["FY-2", "FY-1", "FY"][3 - len(fys) :], fys, strict=True):
            slots[name] = c.column_id
        slots["PYTD"] = next((c.column_id for c in self.cols if c.kind == "PYTD"), None)
        slots["YTD"] = next((c.column_id for c in self.cols if c.kind == "YTD"), None)
        sc = self.snapshot_col
        slots["LTM"] = sc.column_id if sc else None
        return slots

    # ------------------------------------------------------------ account access
    def _bal_period(self, col: Col) -> str | None:
        return self.period_ends.get(col.end_date)

    def acct_cell(self, metric: str, col: Col, basis_hint: str | None = None) -> Cell:
        if col.kind == "PROJECTED":
            v = self.proj_acct.get((metric, col.column_id))
            if v is None:
                return Cell(None, "NOT_PROJECTED", "PROJECTED")
            return Cell(v, None, "PROJECTED")
        if col.kind == "PF_LTM":
            base = self.acct_cell(metric, self.ltm_col)  # type: ignore[arg-type]
            keys = {
                "revenue": ["revenue"],
                "ebitda": ["ebitda"],
                "adjusted_ebitda": ["adjusted_ebitda", "ebitda"],
                "cash_interest_paid": ["cash_interest_paid"],
                "cash_and_equivalents": ["cash_and_equivalents"],
            }
            delta = Decimal(0)
            touched = False
            srcs = list(base.sources)
            for k, v in self.pf_adj.items():
                if metric in keys and (
                    k in keys[metric] and (k != "ebitda" or metric in ("ebitda", "adjusted_ebitda"))
                ):
                    if k == "ebitda" or k == metric:
                        delta += v
                        touched = True
                        srcs += self.pf_sources.get(k, [])
            if metric == "undrawn_rcf":
                for k, v in self.pf_adj.items():
                    if k.startswith("facility:") and self._fac_is_revolver(k.split(":", 1)[1]):
                        delta -= v
                        touched = True
                        srcs += self.pf_sources.get(k, [])
            if base.value is None:
                return Cell(None, base.reason, base.basis, note=base.note)
            if not touched:
                return Cell(base.value, None, base.basis, base.stated, base.note, base.sources)
            return Cell(
                base.value + delta,
                None,
                "PRO_FORMA",
                note="LTM plus pro forma adjustments",
                sources=srcs[:8],
            )
        row = self.acct.get((metric, col.period_id))
        if row is None:
            pe = self._bal_period(col)
            row = self.acct.get((metric, pe)) if pe else None
        if row is None:
            return Cell(None, "NOT_SOURCED", None)
        if row["value"] is None:
            return Cell(None, "NOT_STATED", None, sources=row["sources"])
        basis = "REPORTED" if row["status"] in ("Verified", "Reported") else "CALCULATED"
        return Cell(row["value"], None, basis, note=None, sources=row["sources"])

    def _fac_is_revolver(self, fid: str) -> bool:
        r = self._fac_rows(fid)
        return bool(r) and is_revolver(r[-1].get("facility_type", ""), fid)

    def _fac_rows(self, fid: str) -> list[dict]:
        return [r for r in self.facilities if r["facility_id"] == fid]

    # ------------------------------------------------------------ line engine
    def L(self, line_id: str, col: Col) -> Cell:
        line = self.lines[line_id]
        if col.column_id not in line.cells:
            line.cells[col.column_id] = line.fn(col)
        return line.cells[col.column_id]

    def add_line(
        self,
        line_id: str,
        band: int,
        label: str,
        kind: str,
        unit: str,
        fn: Callable[[Col], Cell],
        **kw: Any,
    ) -> None:
        ul = {
            "MONEY": self.currency + UNIT_SUFFIX.get(self.unit, ""),
            "PERCENT": "%",
            "MULTIPLE": "x",
            "DAYS": "days",
            "COUNT": "count",
            "RATE": "%",
        }.get(unit, kw.pop("unit_label", ""))
        kw.pop("unit_label", None)
        self.lines[line_id] = Line(line_id, band, label, kind, unit, ul, fn, **kw)

    def _basis(self, col: Col) -> str:
        return {"PF_LTM": "PRO_FORMA", "PROJECTED": "PROJECTED"}.get(col.kind, "CALCULATED")

    def calc(
        self,
        col: Col,
        ids: list[str],
        func: Callable[..., Decimal | None],
        *,
        den: str | None = None,
        annual: bool = False,
        note: str | None = None,
        extra_srcs: bool = True,
    ) -> Cell:
        if annual and col.kind in SUB_ANNUAL:
            return Cell(None, "NOT_APPLICABLE", None, note="period shorter than twelve months")
        cells = {i: self.L(i, col) for i in ids}
        missing = [i for i, c in cells.items() if c.value is None]
        if missing:
            reasons = {cells[i].reason for i in missing}
            if reasons == {"NOT_PROJECTED"}:
                return Cell(None, "NOT_PROJECTED", self._basis(col))
            return Cell(None, "COMPONENT_MISSING", None, note="missing: " + ", ".join(missing))
        vals = {i: c.value for i, c in cells.items()}
        if den is not None and (vals[den] is None or vals[den] <= 0):
            return Cell(None, "ZERO_OR_NEGATIVE_DENOMINATOR", None, note=f"{den} is not positive")
        out = func(vals)
        srcs: list[dict] = []
        seen = set()
        for c in cells.values():
            for s in c.sources:
                k = (s["module"], s["citation_id"])
                if k not in seen:
                    seen.add(k)
                    srcs.append(s)
        return Cell(out, None, self._basis(col), note=note, sources=srcs[:8] if extra_srcs else [])

    def prior_col(self, col: Col) -> Col | None:
        if col.kind == "FY":
            fys = [c for c in self.cols if c.kind == "FY"]
            i = fys.index(col)
            return fys[i - 1] if i else None
        if col.kind == "YTD":
            return next((c for c in self.cols if c.kind == "PYTD"), None)
        if col.kind == "QUARTER":
            want = (
                date.fromisoformat(col.end_date)
                .replace(year=date.fromisoformat(col.end_date).year - 1)
                .isoformat()
            )
            return next((c for c in self.cols if c.kind == "QUARTER" and c.end_date == want), None)
        if col.kind == "PROJECTED":
            sibs = [c for c in self.cols if c.kind == "PROJECTED" and c.case == col.case]
            i = sibs.index(col)
            return sibs[i - 1] if i else self.snapshot_base_col()
        return None

    def snapshot_base_col(self) -> Col | None:
        return next((c for c in self.cols if c.kind == "PF_LTM"), self.ltm_col)

    def growth_fn(self, base_id: str) -> Callable[[Col], Cell]:
        def fn(col: Col) -> Cell:
            p = self.prior_col(col)
            if p is None:
                return Cell(None, "NOT_APPLICABLE", None, note="no comparable prior period")
            a, b = self.L(base_id, col), self.L(base_id, p)
            if a.value is None or b.value is None:
                return Cell(None, "COMPONENT_MISSING", None, note=f"missing: {base_id}")
            if b.value <= 0:
                return Cell(
                    None,
                    "ZERO_OR_NEGATIVE_DENOMINATOR",
                    None,
                    note=f"{base_id} prior period not positive",
                )
            v = (a.value / b.value - 1) * 100
            return Cell(MCTX.plus(v), None, self._basis(col), sources=(a.sources + b.sources)[:8])

        return fn

    def acct_fn(self, metric: str) -> Callable[[Col], Cell]:
        return lambda col: self.acct_cell(metric, col)

    def _register_lines(self) -> None:
        A, add = self.acct_fn, self.add_line
        # band 1: operating KPIs
        seen: dict[str, dict] = {}
        for r in sorted(self.kpis, key=lambda r: int(r["display_priority"])):
            seen.setdefault(r["kpi_id"], r)
        self.kpi_vals: dict[tuple[str, str], dict] = {
            (r["kpi_id"], r["period_id"]): r for r in self.kpis
        }
        for kid, r in seen.items():

            def kfn(col: Col, kid: str = kid) -> Cell:
                row = self.kpi_vals.get((kid, col.period_id))
                if row is None or row["value"] == GAP:
                    return Cell(None, "NOT_SOURCED")
                return Cell(
                    D(row["value"]), None, "REPORTED", sources=self._sources(row["source_id"])
                )

            add(f"kpi:{kid}", 1, r["kpi_label"], "ACCOUNT", "KPI", kfn, unit_label=r["unit"])
        # band 2: revenue
        add("revenue", 2, "Revenue", "ACCOUNT", "MONEY", A("revenue"))
        add("revenue_growth", 2, "Revenue growth", "GROWTH", "PERCENT", self.growth_fn("revenue"))
        segs: dict[str, dict] = {}
        for r in sorted(self.segments, key=lambda r: int(r["display_priority"])):
            segs.setdefault(r["segment_id"], r)
        self.seg_vals = {(r["segment_id"], r["period_id"]): r for r in self.segments}
        for sid, r in segs.items():

            def sfn(col: Col, sid: str = sid) -> Cell:
                row = self.seg_vals.get((sid, col.period_id))
                if row is None or row["revenue"] == GAP:
                    return Cell(None, "NOT_SOURCED")
                return Cell(
                    D(row["revenue"]), None, "REPORTED", sources=self._sources(row["source_id"])
                )

            add(f"bu:{sid}", 2, r["segment_name"], "ACCOUNT", "MONEY", sfn)
            if r["segment_type"] == "OPERATING_SEGMENT":
                add(
                    f"bu_growth:{sid}",
                    2,
                    f"{r['segment_name']} growth",
                    "GROWTH",
                    "PERCENT",
                    self.growth_fn(f"bu:{sid}"),
                )
        # band 3: gross profit
        add("cogs", 3, "Cost of goods sold", "ACCOUNT", "MONEY", A("cogs"))
        add(
            "gross_profit",
            3,
            "Gross profit",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(c, ["revenue", "cogs"], lambda v: v["revenue"] - v["cogs"]),
            formula="revenue - cogs",
        )
        add(
            "gross_profit_growth",
            3,
            "Gross profit growth",
            "GROWTH",
            "PERCENT",
            self.growth_fn("gross_profit"),
        )
        # band 4
        add("d_and_a", 4, "Depreciation and amortisation", "ACCOUNT", "MONEY", A("d_and_a"))
        add("ebit", 4, "EBIT", "ACCOUNT", "MONEY", A("ebit"))
        add("ebitda", 4, "Reported EBITDA", "ACCOUNT", "MONEY", self._ebitda_fn)
        # band 5
        self.addback_ids = list(dict.fromkeys(r["addback_id"] for r in self.bridge))
        self.bridge_vals = {(r["addback_id"], r["period_id"]): r for r in self.bridge}
        for aid in self.addback_ids:
            r0 = next(r for r in self.bridge if r["addback_id"] == aid)
            add(
                f"addback:{aid}",
                5,
                r0["addback_label"],
                "ACCOUNT",
                "MONEY",
                lambda c, aid=aid: self._addback_cell(aid, c),
            )
        add(
            "adjusted_ebitda",
            5,
            "Adjusted EBITDA (SSIM basis)",
            "SUBTOTAL",
            "MONEY",
            self._adjusted_fn,
            formula="stated Adjusted EBITDA less positive unrealized add-backs",
        )
        add(
            "structuring_ebitda",
            5,
            "Structuring EBITDA",
            "SUBTOTAL",
            "MONEY",
            self._structuring_fn,
            formula="adjusted_ebitda + positive excluded add-backs",
        )
        add(
            "adjusted_ebitda_growth",
            5,
            "Adjusted EBITDA growth",
            "GROWTH",
            "PERCENT",
            self.growth_fn("adjusted_ebitda"),
        )
        # band 6
        add("cash_interest", 6, "Cash interest (debt)", "ACCOUNT", "MONEY", A("cash_interest_paid"))
        add(
            "lease_cash_not_in_ebitda",
            6,
            "Lease cash payments",
            "ACCOUNT",
            "MONEY",
            A("lease_cash_paid"),
        )
        add("cash_taxes", 6, "Cash taxes", "ACCOUNT", "MONEY", A("cash_taxes_paid"))
        add(
            "other_operating",
            6,
            "Other operating items",
            "ACCOUNT",
            "MONEY",
            lambda c: Cell(
                None, "NOT_APPLICABLE", None, note="carried in the working-capital and other plug"
            ),
        )
        add(
            "ffo",
            6,
            "Funds from operations",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(
                c,
                ["adjusted_ebitda", "cash_interest", "lease_cash_not_in_ebitda", "cash_taxes"],
                lambda v: (
                    v["adjusted_ebitda"]
                    + v["cash_interest"]
                    + v["lease_cash_not_in_ebitda"]
                    + v["cash_taxes"]
                ),
            ),
            formula="adjusted_ebitda + cash_interest + lease_cash + cash_taxes (outflows negative)",
        )
        add("cfo_adjusted", 6, "Cash flow from operations", "ACCOUNT", "MONEY", A("cfo"))
        add(
            "working_capital_change",
            6,
            "Working capital and other (plug)",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(c, ["cfo_adjusted", "ffo"], lambda v: v["cfo_adjusted"] - v["ffo"]),
            formula="cfo_adjusted - ffo",
        )
        add("capex", 6, "Capital expenditure", "ACCOUNT", "MONEY", A("capex"))
        add(
            "fcf",
            6,
            "Free cash flow",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(
                c, ["cfo_adjusted", "capex"], lambda v: v["cfo_adjusted"] + v["capex"]
            ),
            formula="cfo_adjusted + capex",
        )
        # band 7
        add(
            "acquisitions_net",
            7,
            "Acquisitions and disposals, net",
            "ACCOUNT",
            "MONEY",
            A("acquisitions_disposals"),
        )
        add(
            "debt_raised_net",
            7,
            "Net debt issued (repaid)",
            "ACCOUNT",
            "MONEY",
            A("net_debt_issue_repay"),
        )
        add(
            "equity_raised_net",
            7,
            "Net equity issued (repurchased)",
            "ACCOUNT",
            "MONEY",
            A("net_equity_issue_repay"),
        )
        add("dividends", 7, "Dividends", "ACCOUNT", "MONEY", A("dividends_paid"))
        add(
            "other_investing_financing",
            7,
            "Other investing and financing",
            "ACCOUNT",
            "MONEY",
            A("other_investing_financing"),
        )
        add("ncf", 7, "Net change in cash", "ACCOUNT", "MONEY", A("net_cash_change"))
        add(
            "cash_closing", 7, "Cash and equivalents", "ACCOUNT", "MONEY", A("cash_and_equivalents")
        )
        add("undrawn_rcf", 7, "Undrawn revolver availability", "ACCOUNT", "MONEY", A("undrawn_rcf"))
        add(
            "liquidity",
            7,
            "Liquidity",
            "SUBTOTAL",
            "MONEY",
            self._liquidity_fn,
            formula="cash_closing + undrawn_rcf",
        )
        # band 8
        self.fac_ids = list(dict.fromkeys(r["facility_id"] for r in self.facilities))
        for fid in self.fac_ids:
            last = self._fac_rows(fid)[-1]
            rk = rank_of(last["seniority"], last["secured_status"])
            terms = {
                "reference_rate": last.get("reference_rate", GAP),
                "spread_or_coupon": last["margin_or_coupon"],
                "floor": last.get("floor_bps", GAP),
                "maturity": last.get("maturity_date", GAP),
                "amortisation": last.get("annual_amortisation", GAP),
                "seniority": last["seniority"],
                "secured_status": last["secured_status"],
                "facility_type": last["facility_type"],
            }
            add(
                f"fac:{fid}",
                8,
                last["facility_name"],
                "ACCOUNT",
                "MONEY",
                lambda c, fid=fid: self._fac_cell(fid, c),
                rank=rk,
                terms=terms,
            )
        ranks = sorted({self.lines[f"fac:{f}"].rank for f in self.fac_ids})  # type: ignore[type-var]
        for rk in ranks:
            members = [f"fac:{f}" for f in self.fac_ids if self.lines[f"fac:{f}"].rank == rk]
            add(
                f"rank:{rk}",
                8,
                f"Payment rank {rk}",
                "SUBTOTAL",
                "MONEY",
                lambda c, m=members: self.calc(c, m, lambda v: sum(v.values(), Decimal(0))),
                rank=rk,
            )

        def by_status(st: str) -> list[str]:
            return [
                f"fac:{f}" for f in self.fac_ids if self._fac_rows(f)[-1]["secured_status"] == st
            ]

        sec, uns = by_status("SECURED"), by_status("UNSECURED")
        oth = [f"fac:{f}" for f in self.fac_ids if f"fac:{f}" not in sec + uns]
        add(
            "secured_debt",
            8,
            "Senior secured debt",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(c, sec, lambda v: sum(v.values(), Decimal(0))),
        )
        add(
            "unsecured_debt",
            8,
            "Unsecured debt",
            "SUBTOTAL",
            "MONEY",
            lambda c: (
                self.calc(c, uns, lambda v: sum(v.values(), Decimal(0)))
                if uns
                else Cell(Decimal(0), None, self._basis(c))
            ),
        )
        add(
            "other_debt",
            8,
            "Other debt (priority not stated)",
            "SUBTOTAL",
            "MONEY",
            lambda c: (
                self.calc(c, oth, lambda v: sum(v.values(), Decimal(0)))
                if oth
                else Cell(Decimal(0), None, self._basis(c))
            ),
        )
        self.sec_ids, self.uns_ids, self.oth_ids = sec, uns, oth
        add(
            "total_debt",
            8,
            "Total debt (face)",
            "SUBTOTAL",
            "MONEY",
            self._total_debt_fn,
            formula="sum of facility balances",
        )
        add(
            "net_debt",
            8,
            "Net debt",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(
                c, ["total_debt", "cash_closing"], lambda v: v["total_debt"] - v["cash_closing"]
            ),
            formula="total_debt - cash_closing",
        )
        add(
            "financing_obligations",
            8,
            "Financing obligations (leases)",
            "ACCOUNT",
            "MONEY",
            A("financing_obligations"),
        )
        add(
            "lease_adjusted_debt",
            8,
            "Lease-adjusted debt",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(
                c,
                ["total_debt", "financing_obligations"],
                lambda v: v["total_debt"] + v["financing_obligations"],
            ),
        )
        add(
            "lease_adjusted_net_debt",
            8,
            "Lease-adjusted net debt",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(
                c,
                ["net_debt", "financing_obligations"],
                lambda v: v["net_debt"] + v["financing_obligations"],
            ),
        )
        self.debt_like_names = [r["item"] for r in self.debt_like if r["treatment"] == "Debt-like"]
        self.debt_like_ids: list[str] = []
        for r in self.debt_like:
            lid = f"debt_like:{re.sub(r'[^a-z0-9]+', '_', r['item'].lower()).strip('_')}"
            self.debt_like_ids.append(lid)
            add(lid, 8, r["item"], "MEMO", "MONEY", lambda c, r=r: self._debt_like_cell(r, c))
        # band 9
        add("debt_opening", 9, "Debt, opening", "MEMO", "MONEY", self._debt_opening)
        add(
            "debt_net_change",
            9,
            "Debt, net change",
            "SUBTOTAL",
            "MONEY",
            lambda c: self.calc(
                c, ["total_debt", "debt_opening"], lambda v: v["total_debt"] - v["debt_opening"]
            ),
        )
        add("debt_closing", 9, "Debt, closing", "MEMO", "MONEY", lambda c: self.L("total_debt", c))
        # band 10
        add(
            "interest_expense",
            10,
            "Interest expense (P&L)",
            "ACCOUNT",
            "MONEY",
            A("interest_expense"),
        )
        # band 11
        for m, lab in (
            ("net_accounts_receivable", "Receivables"),
            ("inventory", "Inventory"),
            ("accounts_payable", "Accounts payable"),
        ):
            add(f"wc:{m}", 11, lab, "MEMO", "MONEY", A(m))
        # band 12: metrics
        self._register_metrics()

    def _ebitda_fn(self, col: Col) -> Cell:
        c = self.acct_cell("ebitda", col)
        if c.value is not None or col.kind in ("PROJECTED",):
            return c
        e, d = self.L("ebit", col), self.L("d_and_a", col)
        if e.value is not None and d.value is not None:
            return Cell(
                e.value + d.value, None, self._basis(col), sources=(e.sources + d.sources)[:8]
            )
        return Cell(None, "NOT_SOURCED")

    def _addback_cell(self, aid: str, col: Col) -> Cell:
        r = self.bridge_vals.get((aid, col.period_id))
        if r is None or r["value"] == GAP:
            return Cell(None, "NOT_SOURCED")
        return Cell(D(r["value"]), None, "REPORTED", sources=self._sources(r["source_id"]))

    def effective_status(self, aid: str, period_id: str) -> str:
        """House realization status (interfaces §6.5): CP-1D controls; NOT_STATED counts as unrealized."""
        ltm_pid = self.ltm_col.period_id if self.ltm_col else None
        mine = [a for a in self.assess if a["addback_id"] == aid]
        pick = next((a for a in mine if a["period_id"] == ltm_pid), None) or next(
            (a for a in mine if a["period_id"] == period_id), None
        )
        if pick:
            if pick["verdict"] == "Rejected":
                return "UNREALIZED"
            return pick["house_realization_status"]
        r = self.bridge_vals.get((aid, period_id))
        return r["realization_status"] if r else "NOT_STATED"

    def excluded_positive(self, col: Col) -> tuple[Decimal, list[str]]:
        tot, names = Decimal(0), []
        for aid in self.addback_ids:
            cell = self.L(f"addback:{aid}", col)
            if (
                cell.value is not None
                and cell.value > 0
                and self.effective_status(aid, col.period_id) in ("UNREALIZED", "NOT_STATED")
            ):
                tot += cell.value
                names.append(aid)
        return tot, names

    def _adjusted_fn(self, col: Col) -> Cell:
        if col.kind == "PF_LTM" and self.ltm_col is not None:
            # LTM on the SSIM basis (unrealized add-backs left out) plus the pro forma EBITDA adjustments
            pf = self.acct_cell("adjusted_ebitda", col)
            stated = self.acct_cell("adjusted_ebitda", self.ltm_col)
            ltm = self._adjusted_fn(self.ltm_col)
            if pf.value is None or stated.value is None or ltm.value is None:
                return pf
            delta = pf.value - stated.value
            if ltm.value == stated.value:
                return pf
            return Cell(
                ltm.value + delta,
                None,
                "PRO_FORMA" if delta else "CALCULATED",
                pf.value,
                ltm.note,
                pf.sources,
            )
        if col.kind == "PROJECTED":
            return self.acct_cell("adjusted_ebitda", col)
        st = self.acct_cell("adjusted_ebitda", col)
        if st.value is None:
            return st
        ex, names = self.excluded_positive(col)
        if not ex:
            return Cell(st.value, None, st.basis, st.value, None, st.sources)
        return Cell(
            st.value - ex,
            None,
            "CALCULATED",
            st.value,
            f"differs from CP-1 stated: unrealized add-backs left out ({', '.join(names)})",
            st.sources,
        )

    def _structuring_fn(self, col: Col) -> Cell:
        a = self.L("adjusted_ebitda", col)
        if a.value is None:
            return Cell(None, "COMPONENT_MISSING", None, note="missing: adjusted_ebitda")
        if col.kind == "PROJECTED":
            return Cell(a.value, None, self._basis(col), sources=a.sources)
        basis_col = self.ltm_col if col.kind == "PF_LTM" and self.ltm_col is not None else col
        ex, _ = self.excluded_positive(basis_col)
        return Cell(a.value + ex, None, "CALCULATED", sources=a.sources)

    def _liquidity_fn(self, col: Col) -> Cell:
        c = self.calc(
            col, ["cash_closing", "undrawn_rcf"], lambda v: v["cash_closing"] + v["undrawn_rcf"]
        )
        st = self.acct_cell("liquidity_total", col)
        if c.value is not None and st.value is not None:
            c.stated = st.value
            if c.value != st.value:
                c.note = "differs from CP-1 stated"
        return c

    def _fac_cell(self, fid: str, col: Col) -> Cell:
        if col.kind == "PROJECTED":
            v = self.proj_acct.get((f"fac:{fid}", col.column_id))
            return (
                Cell(v, None, "PROJECTED")
                if v is not None
                else Cell(None, "NOT_PROJECTED", "PROJECTED")
            )
        pid = col.period_id if col.kind == "PF_LTM" else None
        if col.kind == "PF_LTM":
            base_col = self.ltm_col
            base = self._fac_cell(fid, base_col)  # type: ignore[arg-type]
            adj = self.pf_adj.get(f"facility:{fid}")
            srcs = self.pf_sources.get(f"facility:{fid}", [])
            if base.value is None:
                return base
            if adj is None:
                return Cell(base.value, None, base.basis, sources=base.sources)
            return Cell(
                base.value + adj,
                None,
                "PRO_FORMA",
                note="LTM plus pro forma adjustments",
                sources=(base.sources + srcs)[:8],
            )
        pe = self._bal_period(col) or pid
        rows = [r for r in self._fac_rows(fid) if r["period_id"] == pe]
        if not rows:
            return Cell(None, "NOT_SOURCED")
        r = rows[0]
        if r["drawn_amount"] == GAP:
            return Cell(None, "NOT_STATED", sources=self._sources(r["source_id"]))
        return Cell(D(r["drawn_amount"]), None, "REPORTED", sources=self._sources(r["source_id"]))

    def _total_debt_fn(self, col: Col) -> Cell:
        ids = [f"fac:{f}" for f in self.fac_ids]
        c = self.calc(col, ids, lambda v: sum(v.values(), Decimal(0)))
        st = self.acct_cell("total_debt", col)
        if (
            c.value is not None
            and st.value is not None
            and col.kind in ("FY", "LTM", "YTD", "QUARTER")
        ):
            c.stated = st.value
            if c.value != st.value:
                c.note = "differs from CP-1 stated total debt"
        return c

    def _debt_like_cell(self, r: dict, col: Col) -> Cell:
        sc = self.snapshot_col
        if sc is None or col.column_id != sc.column_id:
            return Cell(
                None,
                "NOT_APPLICABLE",
                None,
                note="debt-like items are carried on the snapshot column",
            )
        return Cell(D(r["amount"]), None, "REPORTED", sources=[])

    def _debt_opening(self, col: Col) -> Cell:
        if col.kind == "PROJECTED":
            p = self.prior_col(col)
            return self.L("total_debt", p) if p else Cell(None, "NOT_SOURCED")
        if col.kind in ("PF_LTM", "LTM", "PYTD", "QUARTER"):
            return Cell(None, "NOT_APPLICABLE", None, note="no opening balance for this column")
        start = date.fromisoformat(col.start_date or col.end_date) - timedelta(days=1)
        pe = self.period_ends.get(start.isoformat())
        if pe is None:
            return Cell(None, "NOT_SOURCED")
        prior = next(
            (c for c in self.cols if c.kind == "FY" and c.end_date == start.isoformat()), None
        )
        if prior is None:
            return Cell(None, "NOT_SOURCED")
        return self.L("total_debt", prior)

    # -- metrics
    def _register_metrics(self) -> None:
        add = self.add_line

        def ratio_metric(
            mid: str,
            label: str,
            num: str,
            den: str,
            unit: str,
            annual: bool,
            pct: bool = False,
            neg: bool = False,
        ) -> None:
            def fn(col: Col) -> Cell:
                def f(v: dict) -> Decimal:
                    n = -v[num] if neg else v[num]
                    r = MCTX.divide(n, v[den])
                    return r * 100 if pct else r

                return self.calc(col, [num, den], f, den=den, annual=annual)

            add(
                f"metric:{mid}",
                12,
                label,
                "RATIO",
                unit,
                fn,
                formula=f"{num} / {den}" + (" x 100" if pct else ""),
            )

        rm = ratio_metric
        rm(
            "total_leverage_reported",
            "Total leverage, reported EBITDA",
            "total_debt",
            "ebitda",
            "MULTIPLE",
            True,
        )
        rm(
            "total_leverage_adjusted",
            "Total leverage, adjusted EBITDA",
            "total_debt",
            "adjusted_ebitda",
            "MULTIPLE",
            True,
        )
        rm(
            "net_leverage_reported",
            "Net leverage, reported EBITDA",
            "net_debt",
            "ebitda",
            "MULTIPLE",
            True,
        )
        rm(
            "net_leverage_adjusted",
            "Net leverage, adjusted EBITDA",
            "net_debt",
            "adjusted_ebitda",
            "MULTIPLE",
            True,
        )
        rm(
            "senior_secured_leverage",
            "Senior secured leverage",
            "secured_debt",
            "adjusted_ebitda",
            "MULTIPLE",
            True,
        )
        add(
            "metric:senior_secured_net_leverage",
            12,
            "Senior secured net leverage",
            "RATIO",
            "MULTIPLE",
            lambda c: self.calc(
                c,
                ["secured_debt", "cash_closing", "adjusted_ebitda"],
                lambda v: MCTX.divide(v["secured_debt"] - v["cash_closing"], v["adjusted_ebitda"]),
                den="adjusted_ebitda",
                annual=True,
            ),
            formula="(secured_debt - cash_closing) / adjusted_ebitda",
        )
        rm(
            "lease_adjusted_leverage",
            "Lease-adjusted leverage",
            "lease_adjusted_debt",
            "adjusted_ebitda",
            "MULTIPLE",
            True,
        )
        rm(
            "lease_adjusted_net_leverage",
            "Lease-adjusted net leverage",
            "lease_adjusted_net_debt",
            "adjusted_ebitda",
            "MULTIPLE",
            True,
        )
        rm(
            "interest_coverage_reported",
            "Interest cover, reported EBITDA",
            "ebitda",
            "interest_expense",
            "MULTIPLE",
            False,
        )
        rm(
            "interest_coverage_adjusted",
            "Interest cover, adjusted EBITDA",
            "adjusted_ebitda",
            "interest_expense",
            "MULTIPLE",
            False,
        )
        add(
            "metric:capex_adjusted_coverage",
            12,
            "Capex-adjusted interest cover",
            "RATIO",
            "MULTIPLE",
            lambda c: self.calc(
                c,
                ["adjusted_ebitda", "capex", "interest_expense"],
                lambda v: MCTX.divide(v["adjusted_ebitda"] + v["capex"], v["interest_expense"]),
                den="interest_expense",
            ),
            formula="(adjusted_ebitda + capex) / interest_expense",
        )
        add(
            "metric:ebitdar_coverage",
            12,
            "Cash fixed-charge cover",
            "RATIO",
            "MULTIPLE",
            lambda c: self.calc(
                c,
                ["adjusted_ebitda", "cash_interest", "lease_cash_not_in_ebitda"],
                lambda v: MCTX.divide(
                    v["adjusted_ebitda"], -(v["cash_interest"] + v["lease_cash_not_in_ebitda"])
                ),
                den=None,
            ),
            formula="adjusted_ebitda / (cash interest + lease cash)",
        )
        add(
            "metric:cash_interest_coverage",
            12,
            "Cash interest cover, debt only",
            "RATIO",
            "MULTIPLE",
            lambda c: self.calc(
                c,
                ["adjusted_ebitda", "cash_interest"],
                lambda v: MCTX.divide(v["adjusted_ebitda"], -v["cash_interest"]),
            ),
            formula="adjusted_ebitda / cash interest",
        )
        rm("ffo_to_debt", "FFO to debt", "ffo", "total_debt", "PERCENT", True, pct=True)
        rm(
            "ffo_to_lease_adjusted_debt",
            "FFO to lease-adjusted debt",
            "ffo",
            "lease_adjusted_debt",
            "PERCENT",
            True,
            pct=True,
        )
        rm("fcf_to_debt", "FCF to debt", "fcf", "total_debt", "PERCENT", True, pct=True)
        rm(
            "fcf_to_adjusted_ebitda",
            "FCF to adjusted EBITDA",
            "fcf",
            "adjusted_ebitda",
            "PERCENT",
            False,
            pct=True,
        )
        rm(
            "capex_to_revenue",
            "Capex to revenue",
            "capex",
            "revenue",
            "PERCENT",
            False,
            pct=True,
            neg=True,
        )
        rm(
            "liquidity_to_debt",
            "Liquidity to debt",
            "liquidity",
            "total_debt",
            "PERCENT",
            True,
            pct=True,
        )
        rm("gross_margin", "Gross margin", "gross_profit", "revenue", "PERCENT", False, pct=True)
        rm(
            "ebitda_margin",
            "EBITDA margin (reported)",
            "ebitda",
            "revenue",
            "PERCENT",
            False,
            pct=True,
        )
        rm(
            "adjusted_ebitda_margin",
            "Adjusted EBITDA margin",
            "adjusted_ebitda",
            "revenue",
            "PERCENT",
            False,
            pct=True,
        )

    def evaluate(self) -> None:
        for ln in self.lines.values():
            for c in self.cols:
                if c.column_id not in ln.cells:
                    ln.cells[c.column_id] = ln.fn(c)
        self._reconcile_notes()

    def _reconcile_notes(self) -> None:
        self.limits: list[tuple[str, str, str | None, str | None]] = [x for x in self.limitations]
        seen = {x[0] + str(x[3]) for x in self.limits}
        for c in self.cols:
            if c.kind == "PROJECTED":
                continue
            ebitda, adj = self.L("ebitda", c), self.acct_cell("adjusted_ebitda", c)
            adds = [self.L(f"addback:{a}", c) for a in self.addback_ids]
            if (
                ebitda.value is not None
                and adj.value is not None
                and adds
                and all(a.value is not None for a in adds)
            ):
                resid = (
                    adj.value
                    - ebitda.value
                    - sum((a.value for a in adds if a.value is not None), Decimal(0))
                )  # type: ignore[misc]
                if resid != 0 and "ADJ_EBITDA_BRIDGE_RESIDUAL" + c.column_id not in seen:
                    self.limits.append(
                        (
                            "ADJ_EBITDA_BRIDGE_RESIDUAL",
                            f"Reported EBITDA plus add-backs differs from stated Adjusted EBITDA by {plain(resid)}.",
                            "adjusted_ebitda",
                            c.column_id,
                        )
                    )
        if self.pf_col is None:
            self.limits.append(
                (
                    "PF_EQUALS_LTM",
                    "No pro forma adjustments in CP-1: every PF figure equals the LTM figure.",
                    None,
                    None,
                )
            )
        for fid in self.fac_ids:
            r = self._fac_rows(fid)[-1]
            if r.get("maturity_date", GAP) == GAP and self._fac_cell(fid, self.snapshot_col).value:  # type: ignore[arg-type]
                self.limits.append(
                    (
                        "MATURITY_NOT_DATED",
                        f"{r['facility_name']} has no maturity date in CP-1; it sits under Undated in the maturity wall.",
                        f"fac:{fid}",
                        None,
                    )
                )
        sc = self.snapshot_col
        if sc and self.house_ev(sc)[0] is None:
            self.limits.append(
                (
                    "EV_NOT_AVAILABLE",
                    self.house_ev(sc)[2] or "EV cannot be built.",
                    None,
                    sc.column_id,
                )
            )

    # ------------------------------------------------------------ house view
    def _unit_factor(self, unit: str) -> Decimal:
        f = {"UNITS": Decimal(1), "THOUSANDS": Decimal(1000), "MILLIONS": Decimal(1000000)}
        return MCTX.divide(f[unit], f[self.unit])

    def house_ev(self, col: Col) -> tuple[Decimal | None, str | None, str | None, dict]:
        """(EV, basis, reason, inputs)."""
        nd = self.L("net_debt", col)
        ssim = self.L("adjusted_ebitda", col)
        if self.equity:
            e = self.equity[0]
            if e["currency"] != self.currency:
                return None, None, "equity value currency differs from the run currency", {}
            if nd.value is not None and e["market_cap"] != GAP:
                mc = D(e["market_cap"]) * self._unit_factor(e["unit"])
                return mc + nd.value, "listed", None, {"market_cap": plain(mc)}
        if self.ssim_ev_multiple is not None and ssim.value is not None:
            return (
                self.ssim_ev_multiple * ssim.value,
                "ssim_multiple",
                None,
                {"ssim_ev_multiple": plain(self.ssim_ev_multiple)},
            )
        return None, None, "no listed equity value and no SSIM EV multiple in the Run Brief", {}

    def house(self) -> dict[str, dict]:
        col = self.snapshot_col
        out: dict[str, dict] = {}
        if col is None:
            return out
        cid = col.column_id

        def item(
            v: Decimal | None, formula: str, comps: list[str], reason: str | None = None
        ) -> dict:
            return {
                "column_id": cid,
                "value": None if v is None else plain(q(v, 10)),
                "formula": formula,
                "components": comps,
                "reason": None if v is not None else (reason or "COMPONENT_MISSING"),
            }

        st, ss = self.L("structuring_ebitda", col).value, self.L("adjusted_ebitda", col).value
        td = self.L("total_debt", col).value
        ci = self.L("cash_interest", col).value
        pf_int = -ci if ci is not None else None
        out["structuring_ebitda"] = item(
            st,
            "adjusted_ebitda + Σ positive excluded add-backs",
            ["adjusted_ebitda"] + [f"addback:{a}" for a in self.addback_ids],
        )
        out["ssim_ebitda"] = item(ss, "adjusted_ebitda", ["adjusted_ebitda"])
        out["quality_adjusted_ebitda"] = item(
            ss,
            "SSIM EBITDA (Rejected add-backs are already excluded as unrealized)",
            ["adjusted_ebitda"],
        )
        out["pf_interest"] = item(
            pf_int, "cash_interest on the snapshot column (magnitude)", ["cash_interest"]
        )
        out["pf_interest_cover"] = item(
            ratio(ss, pf_int),
            "ssim_ebitda / pf_interest",
            ["adjusted_ebitda", "cash_interest"],
            "ZERO_OR_NEGATIVE_DENOMINATOR",
        )
        out["structuring_multiple"] = item(
            ratio(td, st),
            "total_debt / structuring_ebitda",
            ["total_debt", "structuring_ebitda"],
            "ZERO_OR_NEGATIVE_DENOMINATOR",
        )
        out["ssim_multiple"] = item(
            ratio(td, ss),
            "total_debt / ssim_ebitda",
            ["total_debt", "adjusted_ebitda"],
            "ZERO_OR_NEGATIVE_DENOMINATOR",
        )
        ev, basis, reason, inputs = self.house_ev(col)
        out["ev"] = {
            "value": None if ev is None else plain(q(ev, 10)),
            "basis": basis,
            "inputs": inputs,
            "reason": None if ev is not None else reason,
        }
        like = sum(
            (D(r["amount"]) for r in self.debt_like if r["treatment"] == "Debt-like"), Decimal(0)
        )
        adj_debt = td + like if td is not None else None
        out["adjusted_debt"] = item(
            adj_debt, "total_debt + Σ debt-like items", ["total_debt"] + self.debt_like_ids
        )
        out["adjusted_leverage"] = item(
            ratio(adj_debt, ss),
            "adjusted_debt / ssim_ebitda",
            ["adjusted_debt", "adjusted_ebitda"],
            "ZERO_OR_NEGATIVE_DENOMINATOR",
        )
        pct = []
        for f in self.fac_ids:
            v = self._fac_cell(f, col).value
            pct.append(
                {
                    "facility_id": f,
                    "pct": None
                    if (ev is None or v is None or ev <= 0)
                    else plain(q(v / ev * 100, 10)),
                }
            )
        out["pct_ev_by_facility"] = pct  # type: ignore[assignment]
        return out

    # ------------------------------------------------------------ projection
    def add_projection(self, case: str, years: list[int], drivers: dict) -> None:
        """Project `years` for `case` (BASE or DOWNSIDE) from the snapshot column using `drivers`.

        drivers: revenue_growth_pct, adjusted_ebitda_margin_pct, capex_pct_revenue, cash_taxes (positive),
        wc_change (signed), each {year: value}; optional lease_cash {year}, reference_rate_pct {year},
        floating_rate_add_pct {year}, mandatory_amortisation / repayments {facility_id: {year: amount}},
        dividends {year}, min_cash (number). Identities are asserted into `forecast_checks`.
        """
        if case not in ("BASE", "DOWNSIDE"):
            raise FixtureError("projection case must be BASE or DOWNSIDE")
        base = self.snapshot_base_col()
        if base is None:
            raise FixtureError("no LTM column to project from")

        def g(k: str, y: int, default: Decimal | None = None) -> Decimal | None:
            return D(drivers[k][y]) if k in drivers and y in drivers[k] else default

        cash = self.L("cash_closing", base).value
        rev = self.L("revenue", base).value
        undrawn = self.L("undrawn_rcf", base).value
        lease0 = self.L("lease_cash_not_in_ebitda", base).value
        fin_obl = self.L("financing_obligations", base).value
        ltm_int_pl = self.L("interest_expense", self.ltm_col).value  # type: ignore[arg-type]
        ltm_cash_int = self.L("cash_interest", self.ltm_col).value  # type: ignore[arg-type]
        if None in (cash, rev, lease0, ltm_int_pl, ltm_cash_int):
            raise FixtureError(
                "projection needs cash, revenue, lease cash and interest on the snapshot column"
            )
        noncash = ltm_int_pl - (-ltm_cash_int) - (-lease0)  # type: ignore[operator]
        bal = {f: (self._fac_cell(f, base).value or Decimal(0)) for f in self.fac_ids}
        terms = {f: self._fac_rows(f)[-1] for f in self.fac_ids}
        deck = lambda y: g("reference_rate_pct", y)  # noqa: E731
        implied = self._implied_rate()
        prev_rev = rev
        min_cash = D(drivers.get("min_cash", 0))
        self.projection_rows.setdefault(case, {})
        for y in years:
            cid = f"PROJ:{case}:FY{y}"
            col = Col(
                cid,
                "PROJECTED",
                f"FY{y}E {case.title()}",
                f"FY{y}E_{case}",
                str(y),
                f"{y}-12-31",
                365,
                case,
                f"{y}-01-01",
            )
            if not any(c.column_id == cid for c in self.cols):
                self.cols.append(col)
            growth, margin = g("revenue_growth_pct", y), g("adjusted_ebitda_margin_pct", y)
            if growth is None or margin is None:
                raise FixtureError(f"drivers missing for {case} {y}")
            rev_y = prev_rev * (1 + growth / 100)
            ebitda = rev_y * margin / 100
            interest_total, rows_i = Decimal(0), []
            for f in self.fac_ids:
                t, b = terms[f], bal[f]
                if b == 0:
                    continue
                add_pct = g("floating_rate_add_pct", y, Decimal(0))
                fixed = fixed_rate_of(t)
                if fixed is not None:
                    rate, basis_ = fixed, "Fixed"
                elif (
                    t.get("reference_rate", GAP) != GAP
                    and t.get("spread_bps", GAP) != GAP
                    and deck(y) is not None
                ):
                    floor = (
                        D(t["floor_bps"]) / 100 if t.get("floor_bps", GAP) != GAP else Decimal(0)
                    )
                    rate, basis_ = (
                        max(deck(y), floor) + D(t["spread_bps"]) / 100 + add_pct,
                        "Deck plus spread",
                    )  # type: ignore[type-var]
                else:
                    if implied is None:
                        raise FixtureError(
                            f"{f}: no rate basis (no coupon, no deck plus spread, no implied rate)"
                        )
                    rate, basis_ = implied + add_pct, "Implied"
                intr = b * rate / 100
                interest_total += intr
                rows_i.append(
                    {
                        "case": case,
                        "fiscal_year": str(y),
                        "facility_id": f,
                        "opening_balance": plain(q(b, 3)),
                        "rate_pct": fpct(rate, 3),
                        "rate_basis": basis_,
                        "interest": plain(q(intr, 3)),
                        "currency": self.currency,
                        "unit": self.unit,
                    }
                )
            lease = g("lease_cash", y, -lease0 if lease0 < 0 else lease0)
            lease = abs(lease)  # type: ignore[arg-type]
            taxes = abs(g("cash_taxes", y))  # type: ignore[arg-type]
            wc = g("wc_change", y, Decimal(0))
            ffo = ebitda - interest_total - lease - taxes
            cfo = ffo + wc  # type: ignore[operator]
            capex = -rev_y * g("capex_pct_revenue", y) / 100  # type: ignore[operator]
            fcf = cfo + capex
            repay_total = Decimal(0)
            opening_total = sum(bal.values(), Decimal(0))
            for f in self.fac_ids:
                amt = Decimal(0)
                for k in ("mandatory_amortisation", "repayments"):
                    amt += D(drivers.get(k, {}).get(f, {}).get(y, 0))
                amt = min(amt, bal[f])
                bal[f] -= amt
                repay_total += amt
                mat = terms[f].get("maturity_date", GAP)
                if (
                    mat != GAP
                    and int(mat[:4]) <= y
                    and amt == 0
                    and bal[f] > 0
                    and terms[f].get("facility_type", "") != ""
                ):
                    self.forecast_checks.append(
                        {
                            "check": "maturity_assumed_refinanced",
                            "case": case,
                            "period_id": f"FY{y}E_{case}",
                            "status": "ASSUMED",
                            "detail": f"{f} matures {mat}; balance assumed refinanced on the same terms",
                        }
                    )
            div = abs(g("dividends", y, Decimal(0)))  # type: ignore[arg-type]
            cash_pre = cash + fcf - repay_total - div  # type: ignore[operator]
            draw = Decimal(0)
            if cash_pre < min_cash:
                need = min_cash - cash_pre
                rcfs = [f for f in self.fac_ids if is_revolver(terms[f]["facility_type"], f)]
                for f in rcfs:
                    take = min(need - draw, undrawn if undrawn is not None else Decimal(0))
                    if take > 0:
                        bal[f] += take
                        draw += take
                        undrawn = (undrawn or Decimal(0)) - take
                if draw < need:
                    self.forecast_checks.append(
                        {
                            "check": "liquidity_shortfall",
                            "case": case,
                            "period_id": f"FY{y}E_{case}",
                            "status": "SHORTFALL",
                            "detail": f"cash short of the {plain(min_cash)} floor by {plain(q(need - draw, 3))} after drawing the revolver",
                        }
                    )
            cash_close = cash_pre + draw
            total_debt = sum(bal.values(), Decimal(0))
            pl_int = interest_total + lease + noncash
            P = self.proj_acct
            P[("revenue", cid)] = rev_y
            P[("adjusted_ebitda", cid)] = ebitda
            P[("cash_interest_paid", cid)] = -interest_total
            P[("lease_cash_paid", cid)] = -lease
            P[("cash_taxes_paid", cid)] = -taxes
            P[("cfo", cid)] = cfo
            P[("capex", cid)] = capex
            P[("cash_and_equivalents", cid)] = cash_close
            P[("undrawn_rcf", cid)] = undrawn if undrawn is not None else Decimal(0)
            P[("net_debt_issue_repay", cid)] = draw - repay_total
            P[("interest_expense", cid)] = pl_int
            if fin_obl is not None:
                P[("financing_obligations", cid)] = fin_obl
            for f in self.fac_ids:
                P[(f"fac:{f}", cid)] = bal[f]
            self.projection_interest += rows_i
            self.projection_rows[case][y] = {
                "column_id": cid,
                "revenue": rev_y,
                "ebitda": ebitda,
                "cash_interest": interest_total,
                "lease": lease,
                "taxes": taxes,
                "wc": wc,
                "ffo": ffo,
                "cfo": cfo,
                "capex": capex,
                "fcf": fcf,
                "repay": repay_total,
                "draw": draw,
                "dividends": div,
                "opening_debt": opening_total,
                "total_debt": total_debt,
                "cash": cash_close,
            }
            self._projection_checks(
                case, y, growth, margin, prev_rev, self.projection_rows[case][y]
            )
            cash, prev_rev = cash_close, rev_y
        self.forecast_status = "complete"
        self.limitations.append(
            (
                "PROJECTION_OPENING_AT_LTM",
                "Projected years open from the snapshot (LTM or PF-LTM) balances and run to 31 December.",
                None,
                None,
            )
        )
        for ln in self.lines.values():
            for c in self.cols:
                if (
                    c.kind == "PROJECTED"
                    and c.column_id in ln.cells
                    and ln.cells[c.column_id].reason == "NOT_PROJECTED"
                ):
                    del ln.cells[c.column_id]
        self.evaluate()

    def _implied_rate(self) -> Decimal | None:
        """Floating rate implied by LTM cash interest after fixed-coupon and deck-based facilities."""
        base = self.ltm_col
        ci = self.L("cash_interest", base).value  # type: ignore[arg-type]
        if ci is None:
            return None
        fixed_int, implied_bal = Decimal(0), Decimal(0)
        for f in self.fac_ids:
            t = self._fac_rows(f)[-1]
            b = self._fac_cell(f, base).value or Decimal(0)  # type: ignore[arg-type]
            coupon = fixed_rate_of(t)
            if coupon is not None:
                fixed_int += b * coupon / 100
            else:
                implied_bal += b
        if implied_bal <= 0:
            return None
        return (-ci - fixed_int) / implied_bal * 100

    def _projection_checks(
        self, case: str, y: int, g: Decimal, m: Decimal, prev_rev: Decimal, r: dict
    ) -> None:
        pid = f"FY{y}E_{case}"
        tests = {
            "revenue_x_margin_equals_ebitda": (r["revenue"] * m / 100, r["ebitda"]),
            "revenue_growth_applied": (prev_rev * (1 + g / 100), r["revenue"]),
            "fcf_identity": (
                r["ebitda"] - r["cash_interest"] - r["lease"] - r["taxes"] + r["wc"] + r["capex"],
                r["fcf"],
            ),
            "debt_roll_forward": (r["opening_debt"] - r["repay"] + r["draw"], r["total_debt"]),
        }
        for name, (want, got) in tests.items():
            ok = q(want, 6) == q(got, 6)
            self.forecast_checks.append(
                {
                    "check": name,
                    "case": case,
                    "period_id": pid,
                    "status": "PASS" if ok else "FAIL",
                    "detail": f"expected {plain(q(want, 3))}, model {plain(q(got, 3))}",
                }
            )

    # ------------------------------------------------------------ output
    def to_json(self) -> dict:
        return {
            "schema": "rbot-model/1",
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "rbot_version": "design-fixture",
            "currency": self.currency,
            "unit": self.unit,
            "exclude_unrealised": True,
            "inputs": {
                "CP-1": self.cp1.to_json()["sha256"],
                "CP-1D": self.cp1d.to_json()["sha256"] if self.cp1d else None,
                "CP-2G": None,
                "RUN_BRIEF": self.rb.to_json()["sha256"],
            },
            "columns": [c.to_json() for c in self.cols],
            "snapshot_columns": self.snapshot_columns(),
            "lines": [ln.to_json(self.cols) for ln in self.lines.values()],
            "house": self.house(),
            "capital_structure": {
                "column_id": self.snapshot_col.column_id if self.snapshot_col else None,
                "rows": self.capital_structure_rows(),
                "totals": self.totals_rows(),
            },
            "ebitda_adjustments": self.ebitda_adjustment_rows(),
            "maturity_wall": self.maturity_wall_rows(),
            "rate_deck": None,
            "forecast": {
                "status": self.forecast_status,
                "rows": {
                    c: {
                        str(y): {
                            k: (plain(q(v, 6)) if isinstance(v, Decimal) else v)
                            for k, v in r.items()
                        }
                        for y, r in ys.items()
                    }
                    for c, ys in self.projection_rows.items()
                },
            },
            "limitations": [x[0] for x in self.limits],
            "reconciliation_faults": [
                f"{x[3]}:{x[2]}" for x in self.limits if x[0] == "ADJ_EBITDA_BRIDGE_RESIDUAL"
            ],
        }

    # -- table rows (strings) --------------------------------------------------
    def _srcs_cite(self, h: Handoff, cells: list[Cell]) -> str:
        marks: list[str] = []
        for c in cells:
            for s in c.sources:
                m = h.cite_from_source(s)
                if m not in marks:
                    marks.append(m)
        return " ".join(marks[:6]) or GAP

    def money(self, d: Decimal | None, places: int | None = None) -> str:
        if d is None:
            return GAP
        s = format(q(d, 0 if places is None else places), "f")
        return s.rstrip("0").rstrip(".") if "." in s else s

    def facility_ids_snapshot(self) -> list[str]:
        col = self.snapshot_col
        return [f for f in self.fac_ids if col and (self._fac_cell(f, col).value or 0) != 0]

    def capital_structure_rows(self, h: Handoff | None = None) -> list[dict]:
        col = self.snapshot_col
        if col is None:
            return []
        ev = self.house_ev(col)[0]
        st, ss = self.L("structuring_ebitda", col).value, self.L("adjusted_ebitda", col).value
        ident = {r["facility_id"]: r for r in self.identity}
        rows, cum = [], Decimal(0)
        for f in self.fac_ids:
            cell = self._fac_cell(f, col)
            if cell.value is None or cell.value == 0:
                if cell.value == 0:
                    continue
            t = self._fac_rows(f)[-1]
            cum += cell.value or Decimal(0)
            i = ident.get(f, {})
            ratings = (
                " / ".join(
                    x
                    for x in (
                        i.get("rating_moodys", GAP),
                        i.get("rating_sp", GAP),
                        i.get("rating_fitch", GAP),
                    )
                    if x != GAP
                )
                or GAP
            )
            coupon = t["margin_or_coupon"]
            rows.append(
                {
                    "facility_id": f,
                    "facility": t["facility_name"],
                    "bloomberg_id": i.get("bloomberg_id", GAP),
                    "facility_ratings": ratings,
                    "spread_or_coupon": coupon,
                    "currency": self.currency,
                    "unit": self.unit,
                    "maturity_date": t.get("maturity_date", GAP),
                    "outstanding": self.money(cell.value, 3 if self.unit != "UNITS" else 0),
                    "rank": t["seniority"],
                    "secured": "Yes" if t["secured_status"] == "SECURED" else "No",
                    "structuring_multiple_x": GAP if ratio(cum, st) is None else fx(ratio(cum, st)),  # type: ignore[arg-type]
                    "ssim_multiple_x": GAP if ratio(cum, ss) is None else fx(ratio(cum, ss)),  # type: ignore[arg-type]
                    "pct_ev_pct": GAP
                    if (ev is None or ev <= 0 or cell.value is None)
                    else fpct(cell.value / ev * 100, 1),
                    "column_basis": "PF-LTM" if col.kind == "PF_LTM" else "LTM",
                    "_cell": cell,
                }
            )
        return (
            rows if h is not None else [{k: v for k, v in r.items() if k != "_cell"} for r in rows]
        )

    def totals_rows(self, h: Handoff | None = None) -> list[dict]:
        col = self.snapshot_col
        if col is None:
            return []
        st, ss = self.L("structuring_ebitda", col).value, self.L("adjusted_ebitda", col).value
        ev, basis, reason, _ = self.house_ev(col)
        L = lambda i: self.L(i, col)  # noqa: E731
        sec = L("secured_debt")
        uns = self.calc(
            col, ["unsecured_debt", "other_debt"], lambda v: v["unsecured_debt"] + v["other_debt"]
        )
        td, cash = L("total_debt"), L("cash_closing")
        ci = L("cash_interest").value
        pfi = -ci if ci is not None else None

        def row(
            line: str, amount: Decimal | None, basis_: str, cells: list[Cell], mult: bool = True
        ) -> dict:
            return {
                "line": line,
                "amount": self.money(amount, 3 if self.unit != "UNITS" else 0),
                "currency": self.currency,
                "unit": self.unit,
                "structuring_multiple_x": GAP
                if (not mult or amount is None or ratio(amount, st) is None)
                else fx(ratio(amount, st)),  # type: ignore[arg-type]
                "ssim_multiple_x": GAP
                if (not mult or amount is None or ratio(amount, ss) is None)
                else fx(ratio(amount, ss)),  # type: ignore[arg-type]
                "pct_ev_pct": GAP
                if (ev is None or amount is None or ev <= 0 or not mult)
                else fpct(amount / ev * 100, 1),
                "basis": basis_,
                "_cells": cells,
            }

        eq_basis = {
            "listed": "listed (cp1.equity_value)",
            "ssim_multiple": "ssim_multiple (Run Brief multiple x SSIM EBITDA)",
        }.get(basis or "", f"— ({reason})")
        equity = (
            None
            if ev is None or basis is None
            else (
                ev - (td.value - cash.value)
                if td.value is not None and cash.value is not None
                else None
            )
        )
        r_cover = {
            "line": "PF interest cover",
            "amount": GAP,
            "currency": self.currency,
            "unit": self.unit,
            "structuring_multiple_x": GAP if ratio(st, pfi) is None else fx(ratio(st, pfi)),  # type: ignore[arg-type]
            "ssim_multiple_x": GAP if ratio(ss, pfi) is None else fx(ratio(ss, pfi)),  # type: ignore[arg-type]
            "pct_ev_pct": GAP,
            "basis": "adjusted EBITDA / PF cash interest",
            "_cells": [L("cash_interest")],
        }
        rows = [
            row("Senior secured debt", sec.value, "sum of secured facilities", [sec]),
            row(
                "Unsecured debt",
                uns.value,
                "unsecured facilities plus facilities of unstated priority",
                [uns],
            ),
            row("Total debt", td.value, "sum of facility face amounts", [td]),
            row("Cash", cash.value, "cash and equivalents", [cash], mult=False),
            row("Equity", equity, eq_basis, [], mult=False),
            row("EV", ev, eq_basis, [], mult=True),
            row(
                "PF interest",
                pfi,
                "cash interest on the snapshot column",
                [L("cash_interest")],
                mult=False,
            ),
            r_cover,
        ]
        rows[5]["pct_ev_pct"] = fpct(Decimal(100), 1) if ev else GAP
        return (
            rows
            if h is not None
            else [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
        )

    def ebitda_adjustment_rows(self, h: Handoff | None = None) -> list[dict]:
        col = self.snapshot_col
        if col is None:
            return []
        cur, unit = self.currency, self.unit

        def r(line: str, kind: str, cell: Cell, status: str = GAP, basis: str = "") -> dict:
            return {
                "line": line,
                "kind": kind,
                "amount": self.money(cell.value),
                "currency": cur,
                "unit": unit,
                "realization_status": status,
                "basis": basis or (cell.note or cell.basis or cell.reason or GAP),
                "_cell": cell,
            }

        rows = [
            r(
                "Reported EBITDA",
                "Total",
                self.L("ebitda", col),
                basis="Reported EBITDA on the snapshot column",
            )
        ]
        rows[0]["basis"] = (
            "Reported EBITDA (EBIT + D&A)"
            if rows[0]["amount"] != GAP
            else f"not built for this column ({self.L('ebitda', col).reason})"
        )
        for aid in self.addback_ids:
            c = self.L(f"addback:{aid}", col)
            if c.value is not None and self.effective_status(aid, col.period_id) not in (
                "UNREALIZED",
                "NOT_STATED",
            ):
                rows.append(
                    r(
                        self.lines[f"addback:{aid}"].label,
                        "Add-back",
                        c,
                        self.effective_status(aid, col.period_id),
                        "issuer add-back, realized",
                    )
                )
        rows.append(
            r(
                "Structuring EBITDA",
                "Total",
                self.L("structuring_ebitda", col),
                basis="Reported plus every issuer add-back",
            )
        )
        for aid in self.addback_ids:
            c = self.L(f"addback:{aid}", col)
            if (
                c.value is not None
                and c.value > 0
                and self.effective_status(aid, col.period_id) in ("UNREALIZED", "NOT_STATED")
            ):
                neg = Cell(-c.value, None, c.basis, sources=c.sources)
                rows.append(
                    r(
                        self.lines[f"addback:{aid}"].label,
                        "Unrealized add-back",
                        neg,
                        self.effective_status(aid, col.period_id),
                        "unrealized, left out of SSIM EBITDA",
                    )
                )
        rows.append(
            r(
                "SSIM EBITDA",
                "Total",
                self.L("adjusted_ebitda", col),
                basis="Structuring EBITDA less unrealized add-backs",
            )
        )
        return (
            rows
            if h is not None
            else [{k: v for k, v in x.items() if not k.startswith("_")} for x in rows]
        )

    def maturity_wall_rows(self) -> list[dict]:
        col = self.snapshot_col
        if col is None:
            return []
        out = []
        for f in self.fac_ids:
            cell = self._fac_cell(f, col)
            if not cell.value:
                continue
            t = self._fac_rows(f)[-1]
            mat = t.get("maturity_date", GAP)
            out.append(
                {
                    "fiscal_year": mat[:4] if mat != GAP else "Undated",
                    "facility_id": f,
                    "amount": self.money(cell.value, 3 if self.unit != "UNITS" else 0),
                    "currency": self.currency,
                    "unit": self.unit,
                    "rank": t["seniority"],
                }
            )
        out.sort(key=lambda r: (r["fiscal_year"] == "Undated", r["fiscal_year"]))
        return out

    def display(self, line_id: str, col: Col | None, places: int | None = None) -> str:
        if col is None:
            return GAP
        c = self.L(line_id, col)
        if c.value is None:
            return GAP
        ln = self.lines[line_id]
        p = (
            places
            if places is not None
            else {"MONEY": 0, "PERCENT": 1, "MULTIPLE": 2}.get(ln.unit, 2)
        )
        return plain(q(c.value, p))


# ---------------------------------------------------------------------------------------------
# Host handoffs: MODEL and PROJECTION
# ---------------------------------------------------------------------------------------------
FINANCIAL_LINES = [
    ("Financials", "Revenue", "revenue"),
    ("Financials", "Revenue growth", "revenue_growth"),
    ("Financials", "Gross profit", "gross_profit"),
    ("Financials", "Gross profit growth", "gross_profit_growth"),
    ("Financials", "Gross margin", "metric:gross_margin"),
    ("Financials", "Reported EBITDA", "ebitda"),
    ("Financials", "EBITDA (SSIM basis)", "adjusted_ebitda"),
    ("Financials", "EBITDA growth", "adjusted_ebitda_growth"),
    ("Financials", "EBITDA margin", "metric:adjusted_ebitda_margin"),
    ("Financials", "Cash interest", "cash_interest"),
    ("Financials", "Leases", "lease_cash_not_in_ebitda"),
    ("Financials", "Cash tax", "cash_taxes"),
    ("Financials", "Other", "other_operating"),
    ("Financials", "FFO", "ffo"),
    ("Financials", "Working capital and other", "working_capital_change"),
    ("Financials", "CFO", "cfo_adjusted"),
    ("Financials", "Capex", "capex"),
    ("Financials", "FCF", "fcf"),
    ("Financials", "M&A", "acquisitions_net"),
    ("Financials", "Change in debt", "debt_raised_net"),
    ("Financials", "Change in equity", "equity_raised_net"),
    ("Financials", "Dividends", "dividends"),
    ("Financials", "Other investing and financing", "other_investing_financing"),
    ("Financials", "Net change in cash", "ncf"),
    ("Balance sheet", "Cash", "cash_closing"),
    ("Balance sheet", "Senior debt", "secured_debt"),
    ("Balance sheet", "Total debt", "total_debt"),
    ("Balance sheet", "Net debt", "net_debt"),
    ("Credit metrics", "Senior leverage", "metric:senior_secured_leverage"),
    ("Credit metrics", "Total leverage", "metric:total_leverage_adjusted"),
    ("Credit metrics", "Net leverage", "metric:net_leverage_adjusted"),
    ("Credit metrics", "Interest cover", "metric:interest_coverage_adjusted"),
]
SUMMARY_FIXED = [
    "revenue",
    "revenue_growth",
    "gross_profit",
    "d_and_a",
    "ebit",
    "ebitda",
    "structuring_ebitda",
    "adjusted_ebitda",
    "adjusted_ebitda_growth",
    "cash_interest",
    "lease_cash_not_in_ebitda",
    "cash_taxes",
    "ffo",
    "working_capital_change",
    "cfo_adjusted",
    "capex",
    "fcf",
    "ncf",
    "cash_closing",
    "undrawn_rcf",
    "liquidity",
]
MATERIAL_LIMITS = {
    "EV_NOT_AVAILABLE",
    "ADJ_EBITDA_BRIDGE_RESIDUAL",
    "PF_INTEREST_NOT_SOURCED",
    "MATURITY_NOT_DATED",
}
METRIC_IDS = [
    "total_leverage_reported",
    "total_leverage_adjusted",
    "net_leverage_reported",
    "net_leverage_adjusted",
    "senior_secured_leverage",
    "senior_secured_net_leverage",
    "lease_adjusted_leverage",
    "lease_adjusted_net_leverage",
    "interest_coverage_reported",
    "interest_coverage_adjusted",
    "capex_adjusted_coverage",
    "ebitdar_coverage",
    "ffo_to_debt",
    "ffo_to_lease_adjusted_debt",
    "fcf_to_debt",
    "fcf_to_adjusted_ebitda",
    "capex_to_revenue",
    "liquidity_to_debt",
    "adjusted_ebitda_growth",
]


def model_handoff(mb: ModelBuilder, run_id: str | None = None) -> Handoff:
    ctx = mb.cp1.ctx
    h = Handoff(
        ctx,
        "MODEL",
        mb.cp1.issuer_id,
        run_id or mb.run_id,
        mb.cp1.analysis_date,
        ["CP-1"] + (["CP-1D"] if mb.cp1d else []) + ["RUN_BRIEF"],
        fixture_file="lib.py (ModelBuilder)",
    )
    sc = mb.snapshot_col
    qa = "Restricted" if any(x[0] in MATERIAL_LIMITS for x in mb.limits) else "Pass"
    h.qa(qa)
    gapcite = "calc: facility balance from cp1.debt_facility_register"

    def cite_cells(cells: list[Cell], fallback: str = gapcite) -> str:
        return mb._srcs_cite(h, cells) if any(c.sources for c in cells) else fallback

    cs = []
    for r in mb.capital_structure_rows(h):
        cell = r.pop("_cell")
        r["cite"] = cite_cells([cell])
        cs.append(r)
    h.table("snapshot.capital_structure", cs)
    tot = []
    for r in mb.totals_rows(h):
        cells = r.pop("_cells")
        r["cite"] = mb._srcs_cite(h, cells) if any(c.sources for c in cells) else GAP
        tot.append(r)
    h.table("snapshot.capital_structure_totals", tot)
    ea = []
    for r in mb.ebitda_adjustment_rows(h):
        cell = r.pop("_cell")
        r["cite"] = mb._srcs_cite(h, [cell]) if cell.sources else GAP
        ea.append(r)
    h.table("snapshot.ebitda_adjustments", ea)
    slots = mb.snapshot_columns()
    cols = {c.column_id: c for c in mb.cols}
    fc = []
    for slot in ("FY-2", "FY-1", "FY", "PYTD", "YTD", "LTM"):
        c = cols.get(slots[slot]) if slots[slot] else None
        if c is None:
            fc.append(
                {
                    "slot": slot,
                    "column_id": GAP,
                    "label": "n/a",
                    "period_id": GAP,
                    "kind": GAP,
                    "end_date": GAP,
                }
            )
        else:
            fc.append(
                {
                    "slot": slot,
                    "column_id": c.column_id,
                    "label": c.label,
                    "period_id": c.period_id,
                    "kind": c.kind,
                    "end_date": c.end_date,
                }
            )
    h.table("snapshot.financial_columns", fc)
    slot_cols = [
        cols.get(slots[s]) if slots[s] else None
        for s in ("FY-2", "FY-1", "FY", "PYTD", "YTD", "LTM")
    ]
    fin = []
    for section, label, lid in FINANCIAL_LINES:
        ln = mb.lines[lid]
        cells = [mb.L(lid, c) for c in slot_cols if c is not None]
        fin.append(
            {
                "section": section,
                "line": label,
                "line_id": lid,
                "unit_label": ln.unit_label,
                **dict(
                    zip(
                        ("fy_2", "fy_1", "fy", "pytd", "ytd", "ltm"),
                        [mb.display(lid, c) for c in slot_cols],
                        strict=True,
                    )
                ),
                "cite": mb._srcs_cite(h, [x for x in cells if x.sources][-1:] or [])
                if any(x.sources for x in cells)
                else GAP,
            }
        )
    h.table("snapshot.financials", fin)
    ltm, pf = mb.ltm_col, mb.pf_col or mb.ltm_col
    fy3 = slot_cols[:3]
    ids = list(SUMMARY_FIXED)
    ids += [f"addback:{a}" for a in mb.addback_ids]
    ids += [k for k in mb.lines if k.startswith("rank:")] + [f"fac:{f}" for f in mb.fac_ids]
    ids += [
        "secured_debt",
        "unsecured_debt",
        "total_debt",
        "net_debt",
        "financing_obligations",
        "lease_adjusted_debt",
        "interest_expense",
    ]
    summ = []
    for lid in ids:
        ln = mb.lines[lid]
        vals = [mb.display(lid, c) for c in slot_cols[:5]] + [
            mb.display(lid, ltm),
            mb.display(lid, pf),
        ]
        summ.append(
            {
                "line_id": lid,
                "label": ln.label,
                "band": str(ln.band),
                "unit_label": ln.unit_label,
                **dict(
                    zip(("fy_2", "fy_1", "fy", "pytd", "ytd", "ltm", "pf_ltm"), vals, strict=True)
                ),
            }
        )
    h.table("model.summary", summ)
    met = []
    for mid in METRIC_IDS:
        lid = mid if mid == "adjusted_ebitda_growth" else f"metric:{mid}"
        ln = mb.lines[lid]
        met.append(
            {
                "metric_id": mid,
                "label": f"{ln.label} ({ln.unit_label})",
                "fy_2": mb.display(lid, fy3[0]),
                "fy_1": mb.display(lid, fy3[1]),
                "fy": mb.display(lid, fy3[2]),
                "ltm": mb.display(lid, ltm),
                "pf_ltm": mb.display(lid, pf),
            }
        )
    h.table("model.metrics", met)
    names = {
        "structuring_ebitda": "Structuring EBITDA",
        "ssim_ebitda": "SSIM EBITDA",
        "quality_adjusted_ebitda": "Quality-adjusted EBITDA",
        "pf_interest": "PF interest",
        "pf_interest_cover": "PF interest cover",
        "structuring_multiple": "Structuring Multiple",
        "ssim_multiple": "SSIM Multiple",
        "ev": "EV",
        "adjusted_debt": "Adjusted debt",
        "adjusted_leverage": "Adjusted leverage",
    }
    unitl = {
        "pf_interest_cover": "x",
        "structuring_multiple": "x",
        "ssim_multiple": "x",
        "adjusted_leverage": "x",
    }
    house = mb.house()
    hr = []
    for k, label in names.items():
        it = house[k]
        v = it["value"]
        places = 2 if unitl.get(k) == "x" else 0
        hr.append(
            {
                "item": label,
                "value": GAP if v is None else plain(q(D(v), places)),
                "unit_label": unitl.get(k, mb.currency + UNIT_SUFFIX[mb.unit]),
                "column_id": it.get("column_id", sc.column_id if sc else GAP),
                "formula": it.get("formula", f"EV basis: {it.get('basis')}"),
                "components": ", ".join(
                    it.get(
                        "components",
                        list(it.get("inputs", {}).keys()) or ["adjusted_ebitda", "net_debt"],
                    )
                ),
                "reason": it.get("reason") or GAP,
            }
        )
    h.table("model.house", hr)
    h.table("model.maturity_wall", mb.maturity_wall_rows())
    h.table(
        "model.limitations",
        [{"code": c, "message": m, "line_id": ln, "column_id": co} for c, m, ln, co in mb.limits],
    )
    td, ssim = mb.L("total_debt", sc).value, mb.L("adjusted_ebitda", sc).value  # type: ignore[arg-type]
    v, calc_s = compute("total leverage", "debt / ebitda", 2, "x", debt=td, ebitda=ssim)
    h.analysis(
        f"The Model rebuilds the financial columns from the CP-1 registers without any figure of its own. On the snapshot column "
        f"({sc.label if sc else 'none'}) SSIM EBITDA is {plain(q(ssim, 0))} and total debt {plain(q(td, 0))}, so total leverage is {fx(v)} ({calc_s}). "
        f"Every cell in model.json carries its basis, sources and, where it is empty, a reason code; {len(mb.limits)} limitation(s) are listed in model.limitations."
    )
    h.gaps("\n".join(f"- {m} ({c})" for c, m, _, _ in mb.limits) or "- No Model limitations.")
    h._used |= set(range(1, len(h.citations) + 1))
    return h


def projection_handoff(mb: ModelBuilder, run_id: str | None = None) -> Handoff:
    ctx = mb.cp1.ctx
    h = Handoff(
        ctx,
        "PROJECTION",
        mb.cp1.issuer_id,
        run_id or mb.run_id,
        mb.cp1.analysis_date,
        ["CP-2G", "MODEL"],
        fixture_file="lib.py (ModelBuilder)",
    )
    if mb.forecast_status != "complete":
        raise FixtureError("no projection has been added")
    summ = []
    cols = [c for c in mb.cols if c.kind == "PROJECTED"]
    for c in cols:
        L = lambda i, c=c: mb.L(i, c)  # noqa: E731
        summ.append(
            {
                "case": c.case,
                "fiscal_year": c.fiscal_year,
                "column_id": c.column_id,
                "revenue": mb.display("revenue", c),
                "ebitda": mb.display("adjusted_ebitda", c),
                "adjusted_ebitda": mb.display("adjusted_ebitda", c),
                "cash_interest": mb.display("cash_interest", c),
                "fcf": mb.display("fcf", c),
                "total_debt": mb.display("total_debt", c),
                "net_debt": mb.display("net_debt", c),
                "cash": mb.display("cash_closing", c),
                "liquidity": mb.display("liquidity", c),
                "total_leverage_adjusted_x": fx(L("metric:total_leverage_adjusted").value)
                if L("metric:total_leverage_adjusted").value is not None
                else GAP,
                "net_leverage_adjusted_x": fx(L("metric:net_leverage_adjusted").value)
                if L("metric:net_leverage_adjusted").value is not None
                else GAP,
                "interest_coverage_adjusted_x": fx(L("metric:interest_coverage_adjusted").value)
                if L("metric:interest_coverage_adjusted").value is not None
                else GAP,
                "fcf_to_debt_pct": fpct(L("metric:fcf_to_debt").value)
                if L("metric:fcf_to_debt").value is not None
                else GAP,
                "currency": mb.currency,
                "unit": mb.unit,
            }
        )
    h.table("model.projection_summary", summ)
    h.table("model.projection_interest", mb.projection_interest)
    h.table("model.forecast_checks", mb.forecast_checks)
    fails = [c for c in mb.forecast_checks if c["status"] == "FAIL"]
    h.qa("Restricted" if any(c["status"] == "SHORTFALL" for c in mb.forecast_checks) else "Pass")
    h.analysis(
        f"PROJECTION projects {len(summ)} case-years from the snapshot balances using the CP-2G drivers; {len(mb.forecast_checks)} identity and "
        f"assumption checks ran and {len(fails)} failed. Outflows are negative, interest is opening balance times rate, and a cash shortfall draws the revolver before it is reported."
    )
    h.gaps(
        "- Projected years open from the snapshot (LTM or PF-LTM) balances; intra-year timing is not modelled."
    )
    return h
