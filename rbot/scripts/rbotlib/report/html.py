"""The static Report A page (Plan 07, 07.5): one self-contained file in the frozen template.

`render_html(run, blocks, charts, assets)` writes every byte of content; the shipped `report.js`
only enhances it (shell behaviour, popovers, chart drawing). Without JavaScript the page is
still complete: tables, chart twins and anchors. Every catalog block of the Front Page is
rendered exactly once, in the grid of the template (ruling R5).
"""

from __future__ import annotations

import copy
from collections import Counter
from collections.abc import Callable
from html import escape

from rbotlib.report import ReportError
from rbotlib.report.assets import Assets
from rbotlib.report.blocks import call_band, join_capital_structure
from rbotlib.report.html_parts import (
    STATUS_LABEL,
    Record,
    TableOptions,
    cite_html,
    dir_html,
    embed_json,
    gap_html,
    h,
    scale_html,
    status_html,
    table_html,
)
from rbotlib.report.html_views import (
    FOLDED,
    HOSTED,
    MONEY,
    Ctx,
    build_citations,
    evidence_view,
    fit_view,
    limitations_view,
    model_view,
    module_view,
    nav_status,
    slug,
    view_of,
)

__all__ = ["cite_html", "embed_json", "render_html", "scale_html", "status_html", "table_html"]
STRATEGIES = ("CLO", "Indexed Loans", "Indexed HY")
ABSENT = "not in this run"


def _block(ctx: Ctx, b: Record, cls: str, body: str) -> str:
    """A Snapshot block: a collapsible bar, its body, a source line and the link to its owner."""
    owners = list(dict.fromkeys(t["owner"] for t in b["tables"]))
    link = next((view_of(o) for o in owners if view_of(o)), None)
    label = f"Full analysis of {b['title']}"
    full = (
        h("a", "Full analysis", cls="cb__full", href=f"#{link}", aria_label=label) if link else ""
    )
    source = h("p", escape("Source: " + ", ".join(owners)) if owners else "", cls="cb__src")
    summary = h("summary", h("h2", escape(b["title"]), cls="cb__t") + h("span", "", cls="cb__meta"))
    inner = h("div", _line(b) + body, cls="cb__body cb__body--flush")
    return h(
        "details",
        summary + inner + h("div", source + full, cls="cb__foot"),
        cls=f"cb {cls}",
        id=b["id"],
        data_block=b["id"],
        open="open",
    )


def _line(b: Record) -> str:
    return h("p", escape(b["line"]), cls="na-note") if b["line"] else ""


def _tables(ctx: Ctx, b: Record) -> str:
    return "".join(ctx.table(t["owner"], t["table_id"], t) for t in b["tables"])


def _charts(ctx: Ctx, b: Record) -> str:
    return ctx.figures(b["charts"], "front_page")


def _inner(ctx: Ctx, b: Record, body: str | None = None) -> str:
    """A block that shares a grid cell with another: a sub-head and its own tables."""
    head = h("h3", escape(b["title"]), cls="subh")
    return h(
        "div",
        head + _line(b) + (_tables(ctx, b) if body is None else body),
        cls="inner",
        data_block=b["id"],
    )


def _key_findings(ctx: Ctx, b: Record) -> str:
    out = ""
    for t in b["tables"]:
        cite = ctx.cite(t["owner"])
        for row in t["rows"]:
            r = dict(zip(t["columns"], row, strict=False))
            if t["table_id"] == "snapshot.thesis":
                out += h("p", f"{cite(r['thesis'])} {cite(r['cite'])}", cls="kf__thesis")
            else:
                text = f"{r['date_or_window']}: {r['event']} ({r['direction']}); "
                text += f"watch {r['watch_trigger']}"
                item = h("li", h("span", f"{cite(text)} {cite(r['cite'])}"))
                out += h("ol", item, cls="kf")
    return out


def _capital(ctx: Ctx, b: Record, totals: Record) -> str:
    by_id = {t["table_id"]: t for t in b["tables"]}
    body = ""
    if (cs := by_id.get("snapshot.capital_structure")) is not None:
        levels = by_id.get("snapshot.instrument_levels")
        columns, rows = join_capital_structure(
            cs, levels, by_id.get("snapshot.instrument_recommendation")
        )
        options = TableOptions(money_columns=MONEY, cite=ctx.cite("MODEL"))
        body = table_html(
            columns, rows, module="MODEL", caption="Capital structure", options=options
        )
    return body + _charts(ctx, b) + _inner(ctx, totals)


def _grid(ctx: Ctx, by: dict[str, Record]) -> str:
    """The template's 12-column grid (R5); cells are built in page order so figures number so."""

    def block(bid: str, cls: str, body: Callable[[Record], str] | None = None) -> str:
        b = by[bid]
        if not b["shown"]:
            return h("p", escape(b["reason"]), cls="na-note span-12", data_block=bid)
        return _block(ctx, b, cls, body(b) if body else _tables(ctx, b) + _charts(ctx, b))

    def company(b: Record) -> str:
        return _tables(ctx, b) + _inner(ctx, by["business_description"])

    def financials(b: Record) -> str:
        wall = by["maturity_wall"]
        return _tables(ctx, b) + _inner(ctx, wall, _tables(ctx, wall) + _charts(ctx, wall))

    cells = [
        block("thesis_catalysts", "span-5 p-kf", lambda b: _key_findings(ctx, b)),
        block("company_profile", "span-7 p-co", company),
        block("chart_strip", "span-12 p-figs", lambda b: h("div", _charts(ctx, b), cls="figrow")),
        block(
            "capital_structure",
            "span-7 p-cap",
            lambda b: _capital(ctx, b, by["capital_structure_totals"]),
        ),
        block("ebitda_adjustments", "span-5 p-adj"),
        block("financials", "span-12 p-fin", financials),
        block("strengths_weaknesses", "span-12 p-sw"),
        block("historical_performance", "span-12"),
        block("relative_value", "span-12 p-rv"),
        block("valuation", "span-12"),
        block("portfolio_fit", "span-12"),
        block("transaction_summary", "span-12 p-tx"),
    ]
    return h("div", "".join(cells), cls="fp")


def _call(by: dict[str, Record], run: Record) -> str:
    call = call_band(run)

    def item(key: str, inner: str, block: str = "", extra: str = "") -> str:
        return h(
            "span",
            h("span", escape(key), cls="call__k") + inner,
            cls=f"call__item {extra}".strip(),
            data_block=block,
        )

    def pick(value: str | None, make: Callable[[str], str], block: str) -> str:
        return make(value) if value else gap_html(by[block]["line"] or ABSENT)

    cells = "".join(
        item(
            n,
            pick(
                (call["recommendation"].get(n) or {}).get("recommendation"),
                lambda v: scale_html("rec", v),
                "recommendation",
            ),
        )
        for n in STRATEGIES
    )
    cells += item(
        "Credit Score",
        pick(call["credit_score"], lambda v: scale_html("score", v), "credit_view"),
        "credit_view",
        "call__item--first",
    )
    cells += item("Credit Direction", pick(call["credit_direction"], dir_html, "credit_view"))
    cells += item("Sector Outlook", pick(call["sector_outlook"], dir_html, "credit_view"))
    lines = ""
    fit = Counter(
        (r["portfolio_id"], r["verdict"]) for r in (call["fit_line"] or {"rows": []})["rows"]
    )
    chips = "".join(
        h("span", f"{escape(p)}: {n} x {status_html(v)}", cls="call__lv")
        for (p, v), n in sorted(fit.items())
    )
    if chips:
        more = h("a", "Details in Portfolio Fit", cls="call__more", href="#portfolio-fit")
        lines += h("p", h("span", "Portfolio Fit", cls="call__lk") + chips + more, cls="call__line")
    if call["instrument_line"]:
        text = "; ".join(
            f"{r['instrument']}: {r['recommendation']}, {r['valuation']}"
            for r in call["instrument_line"]
        )
        lines += h(
            "p",
            h("span", "Instrument", cls="call__lk") + h("span", escape(text), cls="call__lv"),
            cls="call__line",
        )
    title = h("div", h("span", "Analyst recommendation", cls="call__title"), cls="call__label")
    body = title + h("div", cells, cls="call__cells") + h("div", lines, cls="call__lines")
    return h(
        "div",
        body,
        cls="call on-navy",
        role="group",
        aria_label="Analyst recommendation",
        data_block="recommendation",
    )


def _snapshot(ctx: Ctx, by: dict[str, Record], run: Record) -> str:
    header = by["header"]["tables"]
    row = dict(zip(header[0]["columns"], header[0]["rows"][0], strict=False)) if header else {}
    issuer = row.get("issuer") or run["run_brief"]["front_matter"].get("issuer_id", "")
    meta = [
        "Credit Snapshot",
        f"{run['pathway']}, {run['depth']} depth",
        "Primary" if run["primary"] else "",
    ]
    meta += [f"As of {row.get('as_of_date', '')}", f"Run {run['run_id']}"]
    spans = "".join(h("span", escape(m)) for m in meta if m)
    top = h("h1", escape(str(issuer)), cls="vtitle", id="view-snapshot-h", tabindex="-1") + h(
        "div", "", cls="vbar"
    )
    band = h(
        "header",
        h("div", top, cls="titleband__top")
        + h("p", spans, cls="titleband__meta")
        + h("div", "", cls="toc-slot")
        + _call(by, run),
        cls="titleband",
        data_block="header",
    )
    return h(
        "section",
        band + _grid(ctx, by),
        cls="view view--snapshot",
        id="view-snapshot",
        data_view="snapshot",
        aria_labelledby="view-snapshot-h",
    )


def _word(state: str) -> str:
    return STATUS_LABEL.get(state.lower(), state).lower()


def _link(vid: str, label: str, code: str = "", word: str = "") -> str:
    tag = h("span", escape(code), cls="nav__code", title="RBOT module code") if code else ""
    mark = ""
    if word:
        mark = h("span", status_html(word), cls="on-navy nav__st")
        mark += h("span", escape(word), cls="nav__stw", aria_hidden="true")
    name = h("span", escape(label), cls="nav__t")
    return h("li", h("a", name + tag + mark, cls="nav__a", href=f"#{vid}", data_view=vid))


PANE = """<aside class="pane" id="pane" aria-label="Report navigation">
<div class="pane__bar"><img class="brand-logo" src="{logo}" alt="State Street Investment Management"
 width="176" height="22"><button type="button" class="pane__menu" id="pane-menu"
 aria-expanded="false" aria-controls="pane-sheet">Menu</button></div>
<div class="pane__sheet" id="pane-sheet"><div class="pane__id">
<span class="pane__issuer">{issuer}</span><span class="pane__meta">{when}</span></div>
<div class="pane__search" role="search"><label class="pane__search-l" for="pane-search">Search the
 Report <kbd>/</kbd></label><input class="pane__search-i" id="pane-search" type="search"
 autocomplete="off" placeholder="Search (press /)"><ul class="pane__results" id="pane-results"
 hidden></ul></div>
<nav class="nav" id="nav" aria-label="Report views"><ul class="nav__list">{items}</ul></nav>
</div></aside>"""
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Credit Snapshot: {issuer}, RBOT Report</title><style>{style}</style></head><body>
<a class="skip" href="#main">Skip to the Report</a>
<div class="app">{pane}<main class="main" id="main" tabindex="-1">{views}</main></div>
<div class="vh" id="route-live" role="status" aria-live="polite"></div>
{data}<script>{charts_js}</script><script>{report_js}</script></body></html>
"""
NAV_VIEWS = (("model", "Model"), ("portfolio-fit", "Portfolio Fit"), ("evidence", "Evidence"))


def _pane(run: Record, assets: Assets, mods: list[str]) -> str:
    states = Counter(nav_status(run, m) for m in mods)
    tally = ", ".join(f"{n} {_word(s)}" for s, n in sorted(states.items()))
    links = [
        _link(f"module-{slug(m)}", run["modules"][m]["title"], m, nav_status(run, m)) for m in mods
    ]
    group = h("span", "Analysis", cls="nav__gt", id="nav-analysis-h")
    group += h("span", escape(f"{len(mods)} modules: {tally}"), cls="nav__gm")
    group = h(
        "li", group + h("ul", "".join(links), aria_labelledby="nav-analysis-h"), cls="nav__grp"
    )
    rest = [_link(v, t) for v, t in (*NAV_VIEWS, ("limitations", "Limitations"))]
    brief = run["run_brief"]["front_matter"]
    when = f"{run['pathway']} · Analysis {brief.get('analysis_date', '')}"
    items = _link("snapshot", "Snapshot") + group + "".join(rest)
    issuer = escape(str(brief.get("issuer_id", "")))
    return PANE.format(logo=assets.logo_data_uri, issuer=issuer, when=escape(when), items=items)


def _check_assets(assets: Assets) -> None:
    if "</style" in (assets.tokens_css + assets.report_css + assets.fonts_css).lower():
        raise ReportError("report css asset contains </style>")
    if "</script" in (assets.charts_js + assets.report_js).lower():
        raise ReportError("report js asset contains </script>")


def _views(ctx: Ctx, charts: list[Record], blocks: list[Record]) -> tuple[str, list[str]]:
    """All views in document order (this numbers the figures) and the modules listed."""
    run = ctx.run
    by = {b["id"]: b for b in blocks}
    mods = [m for m in run["plan"] if m in run["modules"] and m not in FOLDED and m not in HOSTED]
    ends = [("snapshot", "Snapshot"), *((f"module-{slug(m)}", m) for m in mods), ("model", "Model")]
    views = [_snapshot(ctx, by, run)]
    views += [module_view(ctx, m, ends[i], ends[i + 2]) for i, m in enumerate(mods)]
    views += [model_view(ctx), fit_view(ctx), evidence_view(ctx), limitations_view(ctx)]
    for entry in charts:
        if entry["data"] is not None:
            entry["data"]["number"] = ctx.numbers.get(entry["chart_id"])
    return "".join(views), mods


def number_charts(run: Record, blocks: list[Record], charts: list[Record]) -> None:
    """Fill each drawn chart's `number` in place, as the page places them (no assets needed)."""
    _views(Ctx(run, charts, build_citations(run)), charts, blocks)


def render_html(run: Record, blocks: list[Record], charts: list[Record], assets: Assets) -> str:
    """The complete page. Chart entries are copied; their `number` is filled as they are placed."""
    _check_assets(assets)
    charts = copy.deepcopy(charts)
    views, mods = _views(Ctx(run, charts, build_citations(run)), charts, blocks)
    doc = {**run, "charts": charts, "front_page_blocks": blocks}
    issuer = escape(str(run["run_brief"]["front_matter"].get("issuer_id", "")))
    style = f"{assets.fonts_css}\n{assets.tokens_css}\n{assets.report_css}"
    return PAGE.format(
        issuer=issuer,
        style=style,
        pane=_pane(run, assets, mods),
        views=views,
        data=embed_json(doc),
        charts_js=assets.charts_js,
        report_js=assets.report_js,
    )
