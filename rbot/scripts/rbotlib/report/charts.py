"""The ten v1 charts: RBOTCharts specs, table twins, summaries and honest origins (07.4).

A builder reads the `rbot-run/1` document and returns a chart entry `{chart_id, where, kind,
origin, tables, data, twin, summary, note}`; `data` is the spec `rbot/report/charts.js` draws,
`twin` the same values as text, and an undrawable chart has `data: None` and a `note`. A chart
that splits (three strips; one bullet chart per unit) returns `parts`, which `build_all`
flattens. Figures print as served; a sum is an exact `Decimal`; a blank or gap cell is a gap
datum with its reason, never `0`.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from decimal import Decimal, InvalidOperation
from functools import cache
from pathlib import Path
from typing import Any

from rbotlib.calc import bond_analytics, read_input
from rbotlib.calc.bond_analytics import CalcError
from rbotlib.report import ReportError
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]
ChartBuilder = Callable[[Record], Record]

CHART_IDS = (
    "chart.model_strip",
    "chart.maturity_wall",
    "chart.capital_structure",
    "chart.ebitda_bridge",
    "chart.adjusted_debt_bridge",
    "chart.rv_loan",
    "chart.rv_hy",
    "chart.talk_range",
    "chart.fit_bullets",
    "chart.issue_counts",
    "chart.topic_counts",
)
CITE = re.compile(r"\[(C\d+)\]")
CALC_INPUT = "calc/CP-3-bond_analytics.json"
TOPICS = "cpl10.screen_topics"
FIT_UNITS = {"pct_nav": "% NAV", "pct_par": "% par", "count": "count", "years": "years"}


@cache
def gap_marker() -> str:
    return load_rules(RBOT_ROOT).gap_marker


def gap(reason: str) -> Record:
    """A figure the source does not state; drawn as n/a with its reason."""
    return {"v": None, "prov": "gap", "ref": None, "reason": reason}


def _figure(value: str | None) -> Decimal | None:
    text = (value or "").strip()
    if text in ("", gap_marker()):
        return None
    try:
        found = Decimal(text)
    except InvalidOperation:
        return None
    return found if found.is_finite() else None


def _datum(value: str | None, prov: str, ref: str | None, why: str) -> Record:
    if _figure(value) is None:
        return gap(why)
    return {"v": (value or "").strip(), "prov": prov, "ref": ref, "reason": None}


def host(value: str | None, ref: str | None, why: str = "not stated in the Model") -> Record:
    """A figure the host calculated (a Model cell when `ref` names it)."""
    return _datum(value, "calculated", ref, why)


def cited(value: str | None, module: str, cite_cell: str, why: str = "not stated") -> Record:
    """A module's table figure: cited by its first `[Cn]`, calculated by `calc:`, else Model."""
    found = CITE.search(cite_cell)
    if found:
        return _datum(value, "cited", f"{module}:{found.group(1)}", why)
    if cite_cell.strip().startswith("calc:"):
        return _datum(value, "calculated", None, why)
    return _datum(value, "model", None, why)


def _text(d: Record | None) -> str:
    if d is None:
        return gap_marker()
    return f"n/a: {d['reason']}" if d["v"] is None else str(d["v"])


def _total(values: Iterable[Record | None]) -> str:
    sums = [d["v"] for d in values if d is not None and d["v"] is not None]
    return format(sum((Decimal(v) for v in sums), Decimal(0)), "f") if sums else gap_marker()


def _grid(kind: str, data: Record) -> Record:
    """Series by category (line strip, stacked columns); stacked columns add exact totals."""
    stacked = kind == "stackedColumns"
    head = [data["categoryLabel"], *(s["label"] for s in data["series"]), *(["Total"] * stacked)]
    rows = []
    for i, category in enumerate(data["categories"]):
        cells = [s["values"][i] for s in data["series"]]
        rows.append([category, *(_text(c) for c in cells), *([_total(cells)] * stacked)])
    return {"columns": head, "rows": rows}


def _texts(*datums: Record | None) -> list[str]:
    return [_text(d) for d in datums]


ROW_TWINS: dict[str, tuple[str, Callable[[Record], list[str]], Callable[[Record], list[str]]]] = {
    "waterfall": ("steps", lambda d: ["Kind", "Value"], lambda s: [s["kind"], *_texts(s["d"])]),
    "bullet": (
        "rows",
        lambda d: ["Threshold", "Current", "Headroom"],
        lambda r: _texts(r["threshold"], r["current"], r["headroom"]),
    ),
    "rangeStrip": (
        "rows",
        lambda d: ["Min", "Median", "Max", d["markerLabel"]],
        lambda r: _texts(r["min"], r["median"], r["max"], r["marker"]),
    ),
    "dumbbell": (
        "rows",
        lambda d: [d["fromLabel"], d["toLabel"]],
        lambda r: _texts(r["from"], r["to"]),
    ),
}


def _twin(kind: str, data: Record) -> Record:
    if kind in ("lineStrip", "stackedColumns"):
        return _grid(kind, data)
    key, head, cells = ROW_TWINS[kind]
    rows = [[x["label"], *cells(x)] for x in data[key]]
    return {"columns": [data["categoryLabel"], *head(data)], "rows": rows}


def _entry(chart_id: str, where: str, kind: str, origin: str, tables: list[str]) -> Record:
    return {
        "chart_id": chart_id,
        "where": where,
        "kind": kind,
        "origin": origin,
        "tables": tables,
        "data": None,
        "twin": {"columns": [], "rows": []},
        "summary": "",
        "note": None,
    }


def _drawn(entry: Record, data: Record, title: str, summary: str, source: str) -> Record:
    data |= {"title": title, "summary": summary, "source": source, "number": None}
    entry |= {"data": data, "summary": summary, "twin": _twin(entry["kind"], data)}
    return entry


def _undrawable(entry: Record, note: str) -> Record:
    entry["note"] = note
    return entry


def _rows(view: Record, module: str, table_id: str) -> tuple[list[Record], str | None]:
    """The table's rows as records, or the reason the chart cannot draw from it."""
    run = view["run"]
    step = run["steps"].get(module)
    if step is None:
        return [], f"{module} is not in this run"
    if step["status"] not in ("accepted", "blocked") or module not in run["handoffs"]:
        why = step.get("reason") or step["status"]
        return [], f"{module} {step['status']}: {why}"
    table = run["handoffs"][module]["tables"].get(table_id)
    if table is None or not table["rows"]:
        return [], f"{module}: {table_id} has no rows"
    return [dict(zip(table["columns"], r, strict=False)) for r in table["rows"]], None


def _model(view: Record) -> tuple[Record | None, str | None]:
    model = view["run"]["model"]
    if model is None:
        step = view["run"]["steps"].get("MODEL")
        return None, f"MODEL {step['status'] if step else 'is not in this run'}: no model.json"
    return model, None


def _money_unit(model: Record) -> str:
    return next((x["unit_label"] for x in model["lines"] if x["unit"] == "MONEY"), "")


def _model_cell(model: Record, line_id: str, column_id: str) -> Record:
    for line in model["lines"]:
        if line["line_id"] == line_id:
            return next((c for c in line["cells"] if c["column_id"] == column_id), {})
    return {}


def _strip_slots(model: Record) -> list[tuple[str, str, str | None]]:
    """(table column, label, Model column id) for each category the strip can draw."""
    taken, columns = model["snapshot_columns"], {c["column_id"]: c for c in model["columns"]}
    found = [(k, columns.get(taken[s], {}).get("label") or s, taken[s]) for k, s in SLOTS]
    for key, kind in (("ltm", "LTM"), ("pf_ltm", "PF_LTM")):
        column = next((c for c in columns.values() if c["kind"] == kind), None)
        if column is not None:
            found.append((key, column["label"], column["column_id"]))
    return found


def _strip_values(model: Record, row: Record, line_id: str) -> list[Record]:
    values = []
    for key, _label, column_id in _strip_slots(model):
        cell = _model_cell(model, line_id, column_id or "")
        why = cell.get("reason") or "not in the Model"
        ref = f"MODEL:{line_id}:{column_id}" if column_id else None
        datum = host(row.get(key), ref, why)
        if datum["v"] is None and column_id:
            datum["ref"] = f"MODEL:gap:{line_id}:{column_id}"
        values.append(datum)
    return values


SLOTS = (("fy_2", "FY-2"), ("fy_1", "FY-1"), ("fy", "FY"))
METRICS = "model.metrics"
STRIPS = (
    ("leverage", "Net leverage, adjusted", "x", METRICS, "metric:net_leverage_adjusted"),
    ("coverage", "Interest cover, adjusted", "x", METRICS, "metric:interest_coverage_adjusted"),
    ("liquidity", "Liquidity", "", "model.summary", "liquidity"),
)


def _strip_part(view: Record, model: Record, spec: tuple[str, str, str, str, str]) -> Record:
    name, title, unit, table_id, line_id = spec
    entry = _entry(f"chart.model_strip.{name}", "front_page", "lineStrip", "host", [table_id])
    rows, why = _rows(view, "MODEL", table_id)
    key = "metric_id" if table_id == METRICS else "line_id"
    row = next((r for r in rows if r.get(key) == line_id), None)
    if row is None:
        return _undrawable(entry, why or f"{table_id}: no {line_id} row")
    values = _strip_values(model, row, line_id)
    if all(v["v"] is None for v in values):
        return _undrawable(entry, f"{title}: no figure in the Model ({values[0]['reason']})")
    unit = unit or row.get("unit_label") or _money_unit(model)
    labels = [label for _k, label, _c in _strip_slots(model)]
    series = [{"key": line_id, "label": title, "values": values}]
    data = {"categories": labels, "series": series, "unit": unit, "labels": "last"}
    data["categoryLabel"] = "Period"
    return _drawn(
        entry, data, title, f"{title} by period, as the Model computes it.", f"Model, {table_id}"
    )


def model_strip(view: Record) -> Record:
    model, why = _model(view)
    parent = _entry("chart.model_strip", "front_page", "lineStrip", "host", ["model.metrics"])
    if model is None:
        return _undrawable(parent, why or "no Model")
    parent["parts"] = [_strip_part(view, model, spec) for spec in STRIPS]
    return parent


def maturity_wall(view: Record) -> Record:
    entry = _entry(
        "chart.maturity_wall", "front_page", "stackedColumns", "host", ["model.maturity_wall"]
    )
    model, why = _model(view)
    if model is None:
        return _undrawable(entry, why or "no Model")
    rows = model["maturity_wall"]
    if not rows:
        return _undrawable(entry, "model.maturity_wall has no rows")
    years = sorted({r["fiscal_year"] for r in rows})
    ranks = list(dict.fromkeys(r["rank"] for r in rows))
    series = [
        {"label": rank, "values": [_wall_cell(rows, rank, y) for y in years]} for rank in ranks
    ]
    unit = _money_unit(model)
    data = {"categories": years, "series": series, "unit": unit, "categoryLabel": "Fiscal year"}
    summary = f"Debt maturing in each of {len(years)} fiscal years, split by rank."
    return _drawn(entry, data, "Maturity wall", summary, "Model, model.maturity_wall")


def _wall_cell(rows: list[Record], rank: str, year: str) -> Record | None:
    here = [r for r in rows if r["rank"] == rank and r["fiscal_year"] == year]
    if not here:
        return None
    missing = [r for r in here if r["amount"] is None]
    if missing:
        reason = missing[0]["reasons"].get("amount", "not stated")
        return gap(f"{missing[0]['facility_id']}: {reason}")
    return host(_total({"v": r["amount"]} for r in here), None)


def capital_structure(view: Record) -> Record:
    tables = ["snapshot.capital_structure_totals"]
    entry = _entry("chart.capital_structure", "front_page", "waterfall", "host", tables)
    model, _ = _model(view)
    found, why = _rows(view, "MODEL", tables[0])
    rows = {r["line"]: r for r in found}
    names = ("Senior secured debt", "Unsecured debt", "Total debt")
    if why or not all(n in rows for n in names):
        return _undrawable(entry, why or "snapshot.capital_structure_totals lacks a debt row")
    column = (model or {}).get("house", {}).get("ssim_ebitda", {}).get("column_id")
    refs = [None, None, f"MODEL:total_debt:{column}" if column else None]
    kinds = ("delta", "delta", "total")
    steps = [
        {"label": n, "kind": k, "d": host(rows[n]["amount"], ref, f"{n}: not stated")}
        for n, k, ref in zip(names, kinds, refs, strict=True)
    ]
    total = rows["Total debt"]
    multiples = [
        f"{total[k]} {label}"
        for k, label in (("structuring_multiple_x", "Structuring"), ("ssim_multiple_x", "SSIM"))
        if _figure(total[k].rstrip("x")) is not None
    ]
    summary = "Senior secured and unsecured debt add to total debt"
    summary += f" ({'; '.join(multiples)} EBITDA)." if multiples else "."
    unit = _money_unit(model) if model else ""
    data = {"steps": steps, "unit": unit, "totalLabel": "Total debt", "categoryLabel": "Step"}
    return _drawn(
        entry, data, "Capital structure", summary, "Model, snapshot.capital_structure_totals"
    )


def ebitda_bridge(view: Record) -> Record:
    entry = _entry(
        "chart.ebitda_bridge", "front_page", "waterfall", "host", ["snapshot.ebitda_adjustments"]
    )
    rows, why = _rows(view, "MODEL", "snapshot.ebitda_adjustments")
    if why:
        return _undrawable(entry, why)
    steps = []
    for r in rows:
        step = {"label": r["line"], "kind": "total" if r["kind"] == "Total" else "delta"}
        step["d"] = cited(r["amount"], "MODEL", r["cite"], f"{r['line']}: not stated")
        status = r.get("realization_status", "")
        step["short"] = status if status != gap_marker() else None
        steps.append(step)
    model, _ = _model(view)
    data = {"steps": steps, "unit": _money_unit(model) if model else "", "categoryLabel": "Step"}
    summary = "Reported EBITDA to Structuring EBITDA to SSIM EBITDA, every add-back shown."
    return _drawn(entry, data, "EBITDA bridge", summary, "Model, snapshot.ebitda_adjustments")


def adjusted_debt_bridge(view: Record) -> Record:
    tables = ["model.house", "cp1d.debt_like_items"]
    entry = _entry("chart.adjusted_debt_bridge", "CP-1D", "waterfall", "host", tables)
    model, why = _model(view)
    rows, why_items = _rows(view, "CP-1D", "cp1d.debt_like_items")
    items = [r for r in rows if r["treatment"].casefold() == "debt-like"]
    house = (model or {}).get("house", {}).get("adjusted_debt", {})
    totals = {r["line"]: r for r in (model or {}).get("capital_structure", {}).get("totals", [])}
    total = _figure((totals.get("Total debt") or {}).get("amount"))
    adjusted = _figure(house.get("value"))
    if model is None or total is None or adjusted is None:
        return _undrawable(entry, why or why_items or "no Model total debt or adjusted debt")
    steps: list[Record] = [
        {"label": "Total debt", "kind": "total", "d": host(format(total, "f"), None)}
    ]
    for r in items:
        d = cited(r["amount"], "CP-1D", r["cite"], f"{r['item']}: not quantified")
        steps.append({"label": r["item"], "kind": "delta", "d": d})
    explained = total + sum((Decimal(s["d"]["v"]) for s in steps[1:] if s["d"]["v"]), Decimal(0))
    if explained != adjusted:
        residual = format(adjusted - explained, "f")
        steps.append({"label": "Unexplained", "kind": "residual", "d": host(residual, None)})
    steps.append(
        {"label": "Adjusted debt", "kind": "total", "d": host(format(adjusted, "f"), None)}
    )
    data = {"steps": steps, "unit": _money_unit(model), "categoryLabel": "Step"}
    summary = "Total debt plus the debt-like items CP-1D supports gives the Model's adjusted debt."
    return _drawn(entry, data, "Adjusted debt bridge", summary, "Model, model.house; CP-1D")


def _index_row(rows: list[Record], prefix: str) -> Record | None:
    wanted = f"{prefix} index"
    return next(
        (r for r in rows if r["block"].casefold() == wanted and _figure(r["yield_pct"])), None
    )


def _rv(view: Record, chart_id: str, prefix: str, label: str) -> Record:
    entry = _entry(chart_id, "front_page", "dumbbell", "model", ["snapshot.relative_value"])
    rows, why = _rows(view, "CP-3", "snapshot.relative_value")
    if why:
        return _undrawable(entry, why)
    index = _index_row(rows, prefix)
    comps = [r for r in rows if r["block"].casefold() == f"{prefix} comparable"]
    if index is None or not comps:
        return _undrawable(entry, f"{label}: no index row with a yield, or no comparable")
    issuer = _issuer(view)
    start = cited(index["yield_pct"], "CP-3", index["cite"])
    out = []
    for r in comps:
        end = cited(r["yield_pct"], "CP-3", r["cite"], f"{r['name']}: yield not stated")
        row = {"key": r["name"], "label": r["name"], "from": start, "to": end}
        if issuer and issuer in r["name"].casefold():
            row["sub"] = "issuer"
        out.append(row)
    data = {
        "rows": out,
        "unit": "%",
        "fromLabel": f"Index: {index['name']}",
        "toLabel": "Comparable",
    }
    data["categoryLabel"] = "Comparable"
    summary = f"{len(out)} {label} comparables against {index['name']}, yield to the level date."
    return _drawn(entry, data, f"{label} relative value", summary, "CP-3, snapshot.relative_value")


def _issuer(view: Record) -> str:
    header = view["run"]["run_brief"]["tables"].get("snapshot.run_header")
    if not header or not header["rows"]:
        return ""
    row = dict(zip(header["columns"], header["rows"][0], strict=False))
    name = row.get("issuer", "").strip()
    return "" if name == gap_marker() else name.casefold()


def rv_loan(view: Record) -> Record:
    return _rv(view, "chart.rv_loan", "loan", "Loan")


def rv_hy(view: Record) -> Record:
    return _rv(view, "chart.rv_hy", "hy", "High-yield")


def _recomputed(view: Record, rows: list[Record]) -> tuple[str, str | None]:
    """`host` when the calculator re-run on the run's input gives the Handoff's implied levels."""
    run_dir: Path | None = view.get("run_dir")
    path = run_dir / CALC_INPUT if run_dir else None
    if path is None or path.is_symlink() or not path.is_file():
        return "model", "no calculator input in the run"
    try:
        talk = {t["facility_id"]: t for t in bond_analytics.compute(read_input(path))["talk"]}
    except (CalcError, OSError):
        return "model", "calculator input unreadable"
    for r in rows:
        got = talk.get(r["facility_id"], {})
        same = all(
            _figure(r[k]) is not None and _figure(r[k]) == _figure(got.get(k))
            for k in ("implied_low", "implied_mid", "implied_high")
        )
        if not same:
            return "model", "differs from calculator"
    return "host", None


def talk_range(view: Record) -> Record:
    entry = _entry("chart.talk_range", "front_page", "rangeStrip", "model", ["cp3.talk_valuation"])
    rows, why = _rows(view, "CP-3", "cp3.talk_valuation")
    if why:
        return _undrawable(entry, why)
    entry["origin"], entry["note"] = _recomputed(view, rows)
    out = []
    for r in rows:
        spec = {"key": r["facility_id"], "label": r["facility_id"], "sub": r["metric_basis"]}
        for stat, col in (
            ("min", "implied_low"),
            ("median", "implied_mid"),
            ("max", "implied_high"),
        ):
            spec[stat] = cited(r[col], "CP-3", r["cite"], f"{col}: not stated")
        spec["marker"] = cited(r["comparable_level"], "CP-3", r["cite"], "no comparable level")
        out.append(spec)
    unit = "bps" if all("DM" in r["metric_basis"].upper() for r in rows) else ""
    data = {
        "rows": out,
        "unit": unit,
        "markerLabel": "Comparable level",
        "categoryLabel": "Instrument",
    }
    summary = (
        f"{len(out)} instrument(s) valued at talk, implied low to high against the comparable."
    )
    return _drawn(entry, data, "Valuation at talk", summary, "CP-3, cp3.talk_valuation")


def _bullet_row(r: Record) -> Record:
    label = f"{r['portfolio_id']} / {r['facility_id']}: {r['parameter']} ({r['limit_kind']})"
    why = f"{r['status']}: the limit could not be computed"
    return {
        "key": f"{r['portfolio_id']}:{r['facility_id']}:{r['limit_id']}",
        "label": label,
        "direction": "max",
        "threshold": host(r["limit_value"], None, f"{r['parameter']}: limit not stated"),
        "current": host(r["current_value"], None, why),
        "headroom": host(r["headroom"], None, why),
    }


def _binding(rows: list[Record]) -> list[Record]:
    """Every Breached row, and per portfolio the Within row with the smallest headroom."""
    keep = [r for r in rows if r["status"] == "Breached"]
    for pid in dict.fromkeys(r["portfolio_id"] for r in rows):
        within = [r for r in rows if r["portfolio_id"] == pid and r["status"] == "Within"]
        within = [r for r in within if _figure(r["headroom"]) is not None]
        if within:
            keep.append(min(within, key=lambda r: _figure(r["headroom"]) or Decimal(0)))
    return [r for r in rows if r in keep]


def _bullet_part(chart_id: str, where: str, scope: str, unit: str, rows: list[Record]) -> Record:
    entry = _entry(chart_id, where, "bullet", "host", ["fit.limit_headroom"])
    out = [_bullet_row(r) for r in rows]
    data = {"rows": out, "unit": unit, "categoryLabel": "Limit"}
    summary = f"{len(out)} {scope} portfolio limit(s): current against the ceiling."
    return _drawn(entry, data, f"Portfolio limits ({unit})", summary, "FIT, fit.limit_headroom")


def fit_bullets(view: Record) -> Record:
    parent = _entry("chart.fit_bullets", "front_page", "bullet", "host", ["fit.limit_headroom"])
    rows, why = _rows(view, "FIT", "fit.limit_headroom")
    if why:
        return _undrawable(parent, why)
    model = view["run"]["model"]
    money = _money_unit(model) if model else ""
    parts = []
    for scope, where, chosen in (("binding", "front_page", _binding(rows)), ("all", "FIT", rows)):
        for code in dict.fromkeys(r["limit_unit"] for r in chosen):
            unit = FIT_UNITS.get(code, money)
            here = [r for r in chosen if r["limit_unit"] == code]
            parts.append(
                _bullet_part(f"chart.fit_bullets.{scope}.{code}", where, scope, unit, here)
            )
    parent["parts"] = parts
    return parent


def issue_counts(view: Record) -> Record:
    entry = _entry("chart.issue_counts", "CP-5", "stackedColumns", "host", ["cp5.findings"])
    rows, why = _rows(view, "CP-5", "cp5.findings")
    if why:
        return _undrawable(entry, why)
    modules = list(dict.fromkeys(r["module_id"] for r in rows))
    severities = list(dict.fromkeys(["High", "Medium", "Low", *(r["severity"] for r in rows)]))
    series = []
    for sev in severities:
        counts = [
            str(sum(1 for r in rows if r["module_id"] == m and r["severity"] == sev))
            for m in modules
        ]
        series.append({"label": sev, "values": [host(c, None) for c in counts]})
    opened = sum(1 for r in rows if r["status"].casefold() == "open")
    summary = f"{len(rows)} traceability finding(s), {opened} open, by the module that must act."
    data = {"categories": modules, "series": series, "unit": "findings", "categoryLabel": "Module"}
    return _drawn(entry, data, "Findings by module", summary, "CP-5, cp5.findings")


def _topic_part(family: str, topics: list[Record], scales: dict[str, tuple[str, ...]]) -> Record:
    slug = re.sub(r"[^a-z0-9]+", "_", family.casefold()).strip("_")
    entry = _entry(f"chart.topic_counts.{slug}", "CP-L10", "stackedColumns", "host", [TOPICS])
    levels = scales["materiality"]
    series = []
    for disposition in scales["disposition"]:
        counts = [
            sum(1 for t in topics if t["materiality"] == m and t["disposition"] == disposition)
            for m in levels
        ]
        series.append({"label": disposition, "values": [host(str(c), None) for c in counts]})
    summary = f"{len(topics)} {family} topic(s) by materiality and screening disposition."
    data = {"categories": list(levels), "series": series, "unit": "topics"}
    data["categoryLabel"] = "Materiality"
    return _drawn(entry, data, f"{family} topics", summary, f"CP-L10, {TOPICS}")


def topic_counts(view: Record) -> Record:
    parent = _entry("chart.topic_counts", "CP-L10", "stackedColumns", "host", [TOPICS])
    rows, why = _rows(view, "CP-L10", TOPICS)
    if why:
        return _undrawable(parent, why)
    scales = load_rules(RBOT_ROOT).scales
    families = list(dict.fromkeys(r["family"] for r in rows))
    parent["parts"] = [
        _topic_part(f, [r for r in rows if r["family"] == f], scales) for f in families
    ]
    return parent


REGISTRY: dict[str, ChartBuilder] = {
    "chart.model_strip": model_strip,
    "chart.maturity_wall": maturity_wall,
    "chart.capital_structure": capital_structure,
    "chart.ebitda_bridge": ebitda_bridge,
    "chart.adjusted_debt_bridge": adjusted_debt_bridge,
    "chart.rv_loan": rv_loan,
    "chart.rv_hy": rv_hy,
    "chart.talk_range": talk_range,
    "chart.fit_bullets": fit_bullets,
    "chart.issue_counts": issue_counts,
    "chart.topic_counts": topic_counts,
}


def build_all(
    run: Record, wanted: Iterable[str] | None = None, run_dir: Path | None = None
) -> list[Record]:
    """The chart entries for `wanted` ids (default: all eleven); split charts are flattened."""
    view = {"run": run, "run_dir": run_dir}
    out: list[Record] = []
    for chart_id in wanted if wanted is not None else CHART_IDS:
        if chart_id not in REGISTRY:
            raise ReportError(f"unknown chart {chart_id}")
        built = REGISTRY[chart_id](view)
        out.extend(built.pop("parts", None) or [built])
    return out
