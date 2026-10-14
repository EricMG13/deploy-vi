"""`report.md` (Plan 07, 07.6): the same run, blocks and charts as the page, in Markdown.

Figures and `[C<n>]`/`calc:` text are kept as served. The file ends with the run document in a
fenced `json rbot-run` block (spec 11.6), so a later `rbot diff` needs no HTML.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence

from rbotlib.model.layout import BANDS
from rbotlib.report.blocks import GAP, join_capital_structure
from rbotlib.report.html_parts import Record
from rbotlib.report.html_views import (
    FOLDED,
    HOSTED,
    Ctx,
    build_citations,
    limitation_groups,
    nav_status,
)

JOINED = ("snapshot.instrument_levels", "snapshot.instrument_recommendation")
HEADING = re.compile(r"^(#{3,5}) ", re.MULTILINE)


def _cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _table(columns: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    width = len(columns)
    lines = ["| " + " | ".join(_cell(c) for c in columns) + " |", "|" + "---|" * width]
    for row in rows:
        cells = [row[i] if i < len(row) else GAP for i in range(width)]
        lines.append("| " + " | ".join(_cell(c) for c in cells) + " |")
    return "\n".join(lines)


def _prose(md: str) -> str:
    """A Handoff section with its sub-heads pushed below the module heads."""
    return HEADING.sub(lambda m: "##" + m.group(1) + " ", md.strip())


def _titled(title: str, body: str) -> str:
    return f"**{_cell(title)}**\n\n{body}"


def _figure(entry: Record) -> str:
    data = entry["data"]
    if data is None:
        return f"*{entry['chart_id']}: n/a, not drawn. {entry['note']}*"
    twin = _table(entry["twin"]["columns"], entry["twin"]["rows"])
    return f"{_titled(data['title'], entry['summary'])}\n\n{twin}\n\nSource: {data['source']}"


def _figures(charts: list[Record], where: str, prefixes: Sequence[str] | None) -> list[str]:
    return [
        _figure(e)
        for e in charts
        if e["where"] == where
        and (prefixes is None or any(e["chart_id"].startswith(p) for p in prefixes))
    ]


def _block(ctx: Ctx, b: Record) -> str:
    out = [f"### {b['title']}"]
    if not b["shown"]:
        return "\n\n".join([*out, b["reason"]])
    if b["line"]:
        out.append(b["line"])
    by_id = {t["table_id"]: t for t in b["tables"]}
    joined = "snapshot.capital_structure" in by_id
    for t in b["tables"]:
        if joined and t["table_id"] in JOINED:
            continue
        columns, rows = t["columns"], t["rows"]
        if t["table_id"] == "snapshot.capital_structure":
            columns, rows = join_capital_structure(t, by_id.get(JOINED[0]), by_id.get(JOINED[1]))
        out.append(_titled(ctx.title(t["owner"], t["table_id"]), _table(columns, rows)))
    return "\n\n".join(out + _figures(ctx.charts, "front_page", b["charts"]))


def _module(ctx: Ctx, module: str, mark: str) -> str:
    run = ctx.run
    step, info = run["steps"][module], run["modules"].get(module, {})
    entry, reason = run["handoffs"].get(module), str(step.get("reason") or "")
    status = f"Status: {nav_status(run, module)}" + (f" ({reason})" if reason else "")
    out = [f"{mark} {info.get('title', module)} ({module})", status]
    if entry is None:
        return "\n\n".join([*out, f"{module} {step['status']}: no tables."])
    out += [f"{mark}# Analysis", _prose(entry["analysis_md"])]
    if figures := _figures(ctx.charts, module, None):
        out += [f"{mark}# Figures", *figures]
    for tid, table in entry["tables"].items():
        if tid != "citations":
            out += [f"{mark}# {ctx.title(module, tid)}", _table(table["columns"], table["rows"])]
    return "\n\n".join([*out, f"{mark}# Gaps", _prose(entry["gaps_md"]) or "No gap is raised."])


def _model(ctx: Ctx) -> str:
    model = ctx.run["model"]
    if model is None:
        why = ctx.run["steps"].get("MODEL", {}).get("reason") or "not in this run"
        return f"## Model\n\nModel: {why}"
    out = ["## Model", *_figures(ctx.charts, "front_page", ["chart.model_strip"])]
    labels = [c["label"] for c in model["columns"]]
    ids = [c["column_id"] for c in model["columns"]]
    for band in sorted({x["band"] for x in model["lines"]}):
        rows = []
        for line in (x for x in model["lines"] if x["band"] == band):
            cells = {c["column_id"]: c["value"] for c in line["cells"]}
            rows.append([line["label"], line["unit_label"], *(cells.get(i) or GAP for i in ids)])
        out += [f"### {band}. {BANDS[band - 1]}", _table(["Line", "Unit", *labels], rows)]
    if house := ctx.run["handoffs"].get("MODEL", {}).get("tables", {}).get("model.house"):
        out += ["### House figures", _table(house["columns"], house["rows"])]
    notes = "\n".join(f"- {d['message']}" for d in model["limitation_details"]) or "None."
    return "\n\n".join([*out, "### Limitations", notes])


def _fit(ctx: Ctx) -> str:
    run = ctx.run
    pf = run["handoffs"].get("FIT", {}).get("tables", {}).get("snapshot.portfolio_fit")
    out = ["## Portfolio Fit"]
    if pf is None:
        why = run["steps"].get("FIT", {}).get("reason") or "no portfolio attached"
        out.append(f"Portfolio Fit: not in this run ({why}).")
    else:
        brief = run["run_brief"]["tables"].get("brief.portfolios", {"rows": []})
        names = {r[0]: r[1] for r in brief["rows"]}
        for pid in dict.fromkeys(r[0] for r in pf["rows"]):
            rows = [r for r in pf["rows"] if r[0] == pid]
            out += [f"### {names.get(pid, pid)}", _table(pf["columns"], rows)]
    out += _figures(ctx.charts, "FIT", None)
    if "CP-6" in run["steps"]:
        out.append(_module(ctx, "CP-6", "###"))
    return "\n\n".join(out)


def _evidence(ctx: Ctx) -> str:
    out = ["## Evidence"]
    if "CP-5" in ctx.run["steps"]:
        out.append(_module(ctx, "CP-5", "###"))
    shown = {True: "Yes", False: "No", None: "Unverified"}
    rows = [
        [cid, module, c["source"], c["locator"], c["excerpt"], shown[c.get("anchored")]]
        for module, found in ctx.citations.items()
        for cid, c in found.items()
    ]
    columns = ["Id", "Module", "Source", "Locator", "Excerpt", "Anchored"]
    return "\n\n".join([*out, "### Citations", _table(columns, rows)])


def _limitations(run: Record) -> str:
    out = ["## Limitations"]
    for _sid, title, entries in limitation_groups(run["limitations"]):
        out += [f"### {title}", "\n".join(f"- {e}" for e in entries) or "None."]
    return "\n\n".join(out)


def render_markdown(run: Record, blocks: list[Record], charts: list[Record]) -> str:
    """`report.md`: Snapshot blocks in catalog order, then the views, then the run JSON."""
    ctx = Ctx(run, charts, build_citations(run))
    issuer = run["run_brief"]["front_matter"].get("issuer_id", "")
    mods = [m for m in run["plan"] if m in run["modules"] and m not in FOLDED and m not in HOSTED]
    parts = [f"# Credit Snapshot — {issuer}", "## Snapshot", *(_block(ctx, b) for b in blocks)]
    parts += ["## Analysis", *(_module(ctx, m, "###") for m in mods)]
    parts += [_model(ctx), _fit(ctx)]
    parts += ["## Deep Research\n\nNot in this run: not approved."]
    parts += ["## What changed\n\nNot in this run: no prior case."]
    parts += [_evidence(ctx), _limitations(run)]
    doc = {**run, "charts": charts, "front_page_blocks": blocks}
    text = json.dumps(doc, ensure_ascii=False, sort_keys=True)
    text = text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return "\n\n".join(parts) + f"\n\n```json rbot-run\n{text}\n```\n"
