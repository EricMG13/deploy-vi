"""The Report's views: modules, Model, Portfolio Fit, Evidence and Limitations (Plan 07, 07.5).

`Ctx` carries the run, the charts and the citation index while the page is built in document
order, so figure numbers (Fig. CP-1.2) and the back-links from an Evidence row to every place a
citation is used come out of one pass.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from html import escape

from rbotlib.model.layout import BANDS
from rbotlib.report.blocks import GAP
from rbotlib.report.html_parts import Record, TableOptions, cite_html, h, status_html, table_html

MONEY = "outstanding amount size max_size current_exposure headroom_amount market_value".split()
MONEY += "fy_2 fy_1 fy pytd ytd ltm pf_ltm".split()
FOLDED = {"CP-5": "evidence", "CP-6": "portfolio-fit"}
HOSTED = {"MODEL": "model", "FIT": "portfolio-fit"}
BASIS = {"REPORTED": "cited", "CALCULATED": "calculated"}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def view_of(step: str) -> str | None:
    """The view that owns `step`: a module's own, the Model, Portfolio Fit, Evidence."""
    if step == "RUN_BRIEF":
        return None
    return HOSTED.get(step) or FOLDED.get(step) or f"module-{slug(step)}"


@dataclass
class Ctx:
    run: Record
    charts: list[Record]
    citations: dict[str, dict[str, Record]]
    refs: dict[str, list[str]] = field(default_factory=dict)
    numbers: dict[str, str] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    pre: str = "S"
    view: str = "snapshot"

    def cite(self, module: str) -> Callable[[str], str]:
        found = self.citations.get(module, {})
        return lambda text: cite_html(text, module, found, self.refs)

    def title(self, owner: str, table_id: str) -> str:
        for t in self.run["modules"].get(owner, {}).get("tables", []):
            if t["id"] == table_id:
                return str(t["title"])
        return table_id.split(".", 1)[-1].replace("_", " ").capitalize()

    def table(self, owner: str, table_id: str, table: Record) -> str:
        options = TableOptions(money_columns=MONEY, cite=self.cite(owner))
        caption = self.title(owner, table_id)
        rows = table["rows"]
        return table_html(table["columns"], rows, module=owner, caption=caption, options=options)

    def figure(self, entry: Record) -> str:
        """`figure[data-chart]` with its number, summary, table twin (or n/a frame) and source."""
        cid, data = entry["chart_id"], entry["data"]
        if cid not in self.numbers:
            self.counts[self.pre] = self.counts.get(self.pre, 0) + 1
            self.numbers[cid] = f"Fig. {self.pre}.{self.counts[self.pre]}"
        name = cid.removeprefix("chart.").replace("_", " ").capitalize()
        title = data["title"] if data else name
        note = escape(str(entry["note"] or (data and data["summary"]) or ""))
        head = h("span", self.numbers[cid], cls="chart__num") + h(
            "h4", escape(title), cls="chart__title"
        )
        head = h("div", head + h("p", note, cls="chart__summary"), cls="chart__head")
        if data is None:
            na = h("p", h("b", "n/a: not drawn") + note, cls="chart__na")
            body, klass = head + h("div", na, cls="chart__plot"), "chart chart--na"
        else:
            twin = table_html(
                entry["twin"]["columns"], entry["twin"]["rows"], module="chart", caption=title
            )
            source = h("p", "Source: " + escape(str(data["source"])), cls="chart__source")
            body, klass = head + h("div", twin, cls="chart-twin") + source, "chart"
        return h(
            "figure",
            body,
            cls=klass,
            id=f"{self.view}--{cid}",
            data_chart=cid,
            data_origin=entry["origin"],
        )

    def figures(self, prefixes: list[str] | None, where: str) -> str:
        """The charts placed at `where` whose id is, or starts with, one of `prefixes`."""

        def wanted(chart_id: str) -> bool:
            return prefixes is None or any(chart_id.startswith(p) for p in prefixes)

        return "".join(
            self.figure(e) for e in self.charts if e["where"] == where and wanted(e["chart_id"])
        )


def build_citations(run: Record) -> dict[str, dict[str, Record]]:
    found: dict[str, dict[str, Record]] = {}
    brief = run["run_brief"]["tables"].get("citations")
    if brief:
        rows = (dict(zip(brief["columns"], r, strict=False)) for r in brief["rows"])
        found["RUN_BRIEF"] = {r["id"]: {**r, "anchored": None} for r in rows}
    for name, entry in run["handoffs"].items():
        found[name] = {c["id"]: c for c in entry["citations"]}
    return found


def nav_status(run: Record, module: str) -> str:
    step = run["steps"][module]
    if step["status"] in ("failed", "skipped"):
        return str(step["status"]).capitalize()
    return str(run["handoffs"].get(module, {}).get("qa_status") or step["status"].capitalize())


def prose(ctx: Ctx, md: str, module: str) -> str:
    """Paragraphs, bullet lists and sub-heads of a Handoff section, citations linked."""
    cite, out = ctx.cite(module), []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        if lines and all(x.startswith("- ") for x in lines):
            out.append(h("ul", "".join(h("li", cite(x[2:])) for x in lines)))
        elif lines and lines[0].startswith("###"):
            out.append(h("h4", escape(lines[0].lstrip("# ")), cls="subh"))
        elif lines:
            out.append(h("p", cite(" ".join(lines))))
    return "".join(out)


FETCHED_COLUMNS = ("URL", "Retrieved", "Question", "File")


def fetched_rows(run: Record) -> list[list[str]]:
    return [[f["url"], f["retrieved"], f["question"], f["file"]] for f in run["fetched"]]


def section(title: str, body: str, sid: str = "") -> str:
    summary = h("summary", h("h3", escape(title), cls="cb__t"))
    return h(
        "details", summary + h("div", body, cls="cb__body"), cls="cb cb--paper", id=sid, open="open"
    )


def module_body(ctx: Ctx, module: str) -> str:
    """Question, status, analysis, charts, tables and gaps of one module (view or fold)."""
    step, info = ctx.run["steps"][module], ctx.run["modules"].get(module, {})
    entry, reason = ctx.run["handoffs"].get(module), str(step.get("reason") or "")
    ask = h("span", "Question: ") + escape(info.get("question", ""))
    chip = h("span", "Status " + status_html(nav_status(ctx.run, module), reason), cls="vfact__k")
    facts = h("div", ask, cls="vfact vfact__q") + h(
        "div", chip + h("p", escape(reason), cls="vfact__v"), cls="vfact"
    )
    facts = h("div", facts, cls="vfacts")
    if entry is None:
        return facts + h("p", escape(f"{module} {step['status']}: no tables."), cls="na-note")
    sid = slug(module)
    parts = [section("Analysis", prose(ctx, entry["analysis_md"], module), f"{sid}-analysis")]
    if figures := ctx.figures(None, module):
        parts.append(section("Figures", figures, f"{sid}-figures"))
    for tid, table in entry["tables"].items():
        if tid != "citations":
            parts.append(section(ctx.title(module, tid), ctx.table(module, tid, table)))
    if module == "CP-DR":
        rows = fetched_rows(ctx.run)
        shown = (
            table_html(FETCHED_COLUMNS, rows, module=module, caption="Fetched sources")
            if rows
            else h("p", "Fetched sources: none", cls="na-note")
        )
        parts.append(section("Fetched sources", shown, f"{sid}-fetched"))
    gaps = prose(ctx, entry["gaps_md"], module) or h("p", "No gap is raised.", cls="na-note")
    return facts + "".join(parts) + section("Gaps and limitations", gaps, f"{sid}-gaps")


def view(vid: str, title: str, body: str, code: str = "") -> str:
    tag = h("span", escape(code), cls="vhead__code", title="RBOT module code") if code else ""
    top = (
        h("h1", escape(title), cls="vtitle", id=f"view-{vid}-h", tabindex="-1")
        + tag
        + h("div", "", cls="vbar")
    )
    head = h("header", h("div", top, cls="vhead__top") + h("div", "", cls="toc-slot"), cls="vhead")
    attrs = {"id": f"view-{vid}", "data_view": vid, "aria_labelledby": f"view-{vid}-h"}
    return h("section", head + body, cls="view", hidden="hidden", **attrs)


def fold(ctx: Ctx, module: str) -> str:
    """CP-5 inside Evidence, CP-6 inside Portfolio Fit: a titled section, its own anchor."""
    name = ctx.run["modules"].get(module, {}).get("title", module)
    top = h("h2", escape(name), cls="fold__t") + h("span", escape(module), cls="vhead__code")
    head = h("header", h("div", top, cls="vhead__top"), cls="vhead vhead--fold")
    return h("section", head + module_body(ctx, module), cls="fold", id=f"module-{slug(module)}")


def module_view(ctx: Ctx, module: str, prev: tuple[str, str], nxt: tuple[str, str]) -> str:
    ctx.pre, ctx.view = module, f"module-{slug(module)}"
    title = ctx.run["modules"].get(module, {}).get("title", module)

    def link(side: str, key: str, target: tuple[str, str]) -> str:
        label = h("span", key, cls="pager__k") + h("span", escape(target[1]), cls="pager__t")
        return h("a", label, cls=f"pager__a pager__a--{side}", href=f"#{target[0]}")

    both = link("prev", "Previous", prev) + link("next", "Next", nxt)
    pager = h("nav", both, cls="pager", aria_label="Previous and next module")
    return view(ctx.view, title, module_body(ctx, module) + pager, module)


def model_datum(line: Record, cell: Record) -> Record:
    ref = f"{line['line_id']}:{cell['column_id']}"
    if cell["value"] is None:
        return {"v": None, "prov": "gap", "ref": f"MODEL:gap:{ref}", "reason": cell["reason"]}
    prov = BASIS.get(cell["basis"], "model")
    return {"v": cell["value"], "prov": prov, "ref": f"MODEL:{ref}", "reason": None}


def model_band(model: Record, band: int, lines: list[Record]) -> str:
    cols = model["columns"]
    labels = [c["label"] for c in cols]
    rows, datums = [], {}
    for r, line in enumerate(lines):
        cells = {c["column_id"]: c for c in line["cells"]}
        rows.append([line["label"], line["unit_label"], *([GAP] * len(cols))])
        for c, col in enumerate(cols, 2):
            if col["column_id"] in cells:
                datums[(r, c)] = model_datum(line, cells[col["column_id"]])
    kinds = ["", "", *[c["kind"] for c in cols]]
    options = TableOptions(money_columns=labels, datums=datums, col_kinds=kinds)
    table = table_html(
        ["Line", "Unit", *labels], rows, module="MODEL", caption=BANDS[band - 1], options=options
    )
    return section(f"{band}. {BANDS[band - 1]}", table, f"model-band-{band}")


def model_view(ctx: Ctx) -> str:
    ctx.pre, ctx.view = "M", "model"
    model = ctx.run["model"]
    if model is None:
        why = ctx.run["steps"].get("MODEL", {}).get("reason") or "not in this run"
        return view("model", "Model", h("p", escape(f"Model: {why}"), cls="na-note"))
    body = ctx.figures(["chart.model_strip"], "front_page")
    for band in sorted({x["band"] for x in model["lines"]}):
        body += model_band(model, band, [x for x in model["lines"] if x["band"] == band])
    if house := ctx.run["handoffs"].get("MODEL", {}).get("tables", {}).get("model.house"):
        body += section("House figures", ctx.table("MODEL", "model.house", house), "model-house")
    notes = "".join(h("li", escape(d["message"])) for d in model["limitation_details"])
    return view("model", "Model", body + section("Limitations", h("ul", notes), "model-limits"))


def fit_view(ctx: Ctx) -> str:
    ctx.pre, ctx.view = "PF", "portfolio-fit"
    pf = ctx.run["handoffs"].get("FIT", {}).get("tables", {}).get("snapshot.portfolio_fit")
    body = ""
    if pf is None:
        why = ctx.run["steps"].get("FIT", {}).get("reason") or "no portfolio attached"
        body = h("p", escape(f"Portfolio Fit: not in this run ({why})."), cls="na-note")
    brief = ctx.run["run_brief"]["tables"].get("brief.portfolios", {"rows": []})
    names = {r[0]: r[1] for r in brief["rows"]}
    for pid in dict.fromkeys(r[0] for r in (pf or {"rows": []})["rows"]):
        mine = {"columns": pf["columns"], "rows": [r for r in pf["rows"] if r[0] == pid]}
        body += section(names.get(pid, pid), ctx.table("FIT", "snapshot.portfolio_fit", mine))
    body += ctx.figures(None, "FIT")
    if "CP-6" in ctx.run["steps"]:
        body += fold(ctx, "CP-6")
    return view("portfolio-fit", "Portfolio Fit", body, "PF")


def evidence_rows(ctx: Ctx) -> str:
    rows = []
    for module, found in ctx.citations.items():
        for cid, c in found.items():
            state = {True: "Yes", False: "No", None: "Unverified"}[c.get("anchored")]
            used = ctx.refs.get(f"{module}:{cid}", [])
            back = " ".join(h("a", str(i), href=f"#{a}") for i, a in enumerate(used, 1))
            cells = [cid, module, c["source"], c["locator"], c["excerpt"], state]
            tds = "".join(h("td", escape(x)) for x in cells) + h("td", back)
            rows.append(h("tr", tds, id=f"ev-{module}-{cid}"))
    names = ("Id", "Module", "Source", "Locator", "Excerpt", "Anchored", "Used at")
    head = h("thead", h("tr", "".join(h("th", n, scope="col") for n in names)))
    table = h(
        "table",
        h("caption", "Citations", cls="vh") + head + h("tbody", "".join(rows)),
        cls="dt evid",
    )
    return h("div", table, cls="table-scroll")


def evidence_view(ctx: Ctx) -> str:
    ctx.pre, ctx.view = "E", "evidence"
    body = fold(ctx, "CP-5") if "CP-5" in ctx.run["steps"] else ""
    return view(
        "evidence", "Evidence", body + section("Citations", evidence_rows(ctx), "evidence-rows")
    )


def deep_research_absence(run: Record) -> str | None:
    """Why Deep Research is absent: not in the depth's plan, or skipped (with the step's reason)."""
    step = run["steps"].get("CP-DR")
    if step is None:
        return "not in this depth"
    if step["status"] == "skipped":
        return f"not in this run: {step.get('reason') or 'no reason recorded'}"
    return None


def limitation_groups(run: Record) -> list[tuple[str, str, list[str]]]:
    """(section id, title, entries) of the four Limitations groups, shared with `report.md`."""
    lim = run["limitations"]
    approval = [x.get("text") or f"{x['module']}: limited by grading" for x in lim["approval"]]
    cp5 = [f"{x['module_id']}: {x['limitation']} ({x['effect_on_decision']})" for x in lim["cp5"]]
    keys = ("kind", "step", "code", "message", "reason", "ref")
    other = [" ".join(str(x[k]) for k in keys if x.get(k)) for x in lim["unforeseen"]]
    why = deep_research_absence(run)
    absent = [f"Deep Research: {why}"] if why else []
    absent.append("What changed: not in this run: no prior case")
    return [
        ("limit-approval", "Shown at Approval", approval),
        ("limit-cp5", "Found at CP-5", cp5),
        ("limit-unforeseen", "Unforeseen", other),
        ("limit-absent", "Not in this run", absent),
    ]


def limitations_view(ctx: Ctx) -> str:
    def items(entries: list[str]) -> str:
        return h("ul", "".join(h("li", escape(x)) for x in entries)) if entries else h("p", "None.")

    body = "".join(
        section(title, items(entries), sid) for sid, title, entries in limitation_groups(ctx.run)
    )
    return view("limitations", "Limitations", body)
