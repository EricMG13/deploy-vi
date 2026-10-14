"""The Report A page parts and views (Plan 07 task 07.5), from a complete fixture run."""

from __future__ import annotations

import copy
import dataclasses
import html as stdlib_html
import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import pytest
from hypothesis import given
from hypothesis import strategies as st
from report_run import complete_run

from rbotlib.catalog import load_catalog, load_contracts
from rbotlib.report import ReportError, run_json
from rbotlib.report import blocks as blk
from rbotlib.report.assets import Assets, load
from rbotlib.report.charts import build_all
from rbotlib.report.html import render_html
from rbotlib.report.html_parts import cite_html, embed_json, table_html
from rbotlib.report.html_views import Ctx, build_citations, model_view, module_view, slug
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]
CATALOG = load_catalog(RBOT_ROOT)
CONTRACTS = load_contracts(RBOT_ROOT, load_rules(RBOT_ROOT), [])
BLOCK_IDS = [b.id for b in CATALOG.blocks["credit_snapshot"]]
NOW = "2026-10-14T00:00:00+00:00"
SEPARATOR = chr(0x2028)
ENDS = (("snapshot", "Snapshot"), ("model", "Model"))


class Page(NamedTuple):
    run: Path
    doc: Record


@pytest.fixture(scope="module")
def page(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Page:
    run = complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))
    return Page(run, run_json.build(run, RBOT_ROOT, NOW))


@pytest.fixture(scope="module")
def assets(tmp_path_factory: pytest.TempPathFactory) -> Assets:
    """The shipped assets with a placeholder `report.js` (the real one arrives in 07.7)."""
    root = shutil.copytree(RBOT_ROOT / "report", tmp_path_factory.mktemp("assets") / "report")
    (root / "report.js").write_text("window.RBOT_REPORT = true;\n", encoding="utf-8")
    return load(root)


def render(page: Page, assets: Assets, doc: Record | None = None) -> str:
    doc = doc or page.doc
    blocks = blk.front_page_blocks(doc, CATALOG, CONTRACTS)
    return render_html(doc, blocks, build_all(doc, run_dir=page.run), assets)


def ctx_of(page: Page, doc: Record | None = None) -> Ctx:
    doc = doc or page.doc
    return Ctx(doc, build_all(doc, run_dir=page.run), build_citations(doc))


def test_calc_text_renders_abbr() -> None:
    got = cite_html("see [C1]; calc: CP-3 NEW-1 (x) now", "M", {"C1": {"excerpt": "a<b"}})
    assert 'title="a&lt;b"' in got
    assert '<abbr class="calc" title="CP-3 NEW-1 (x) now">calc</abbr>' in got
    assert 'class="cite--unknown">[C99]' in cite_html("[C99]", "M", {})


def test_failed_module_view_has_chip_reason_no_tables(page: Page) -> None:
    doc = copy.deepcopy(page.doc)
    doc["steps"]["CP-1D"] |= {"status": "failed", "reason": "model returned nothing"}
    del doc["handoffs"]["CP-1D"]
    got = module_view(ctx_of(page, doc), "CP-1D", *ENDS)
    assert "status--na" in got and "model returned nothing" in got and "<table" not in got


def test_blocked_module_tables_have_gap_cells(page: Page) -> None:
    doc = copy.deepcopy(page.doc)
    doc["steps"]["CP-3"]["status"] = "blocked"
    doc["handoffs"]["CP-3"]["qa_status"] = "Blocked"
    doc["handoffs"]["CP-3"]["tables"]["cp3.compensation"]["rows"][0][2] = "—"
    got = module_view(ctx_of(page, doc), "CP-3", *ENDS)
    assert "status--blocked" in got and '<span class="gap">n/a</span>' in got


def test_model_cells_carry_passport_refs(page: Page) -> None:
    ctx = ctx_of(page)
    model = model_view(ctx)
    datums = [
        json.loads(stdlib_html.unescape(d.split('"', 1)[0]))
        for d in model.split('data-datum="')[1:]
    ]
    assert datums and all(d["ref"].startswith("MODEL:") for d in datums)
    assert any(d["ref"].startswith("MODEL:gap:") and d["prov"] == "gap" for d in datums)
    assert any(d["prov"] == "cited" and not d["ref"].startswith("MODEL:gap:") for d in datums)
    assert 'data-col-kind="PF_LTM"' in model
    assert ctx.numbers["chart.model_strip.leverage"] == "Fig. M.1"


def test_figure_twin_and_na_frame(page: Page) -> None:
    ctx = ctx_of(page)
    got = ctx.figures(["chart.model_strip"], "front_page")
    assert got.count("<figure") == 3
    assert 'class="chart-twin"' in got and 'class="chart chart--na"' in got
    assert "n/a: not drawn" in got
    again = ctx.figures(["chart.model_strip.leverage"], "front_page")
    assert "Fig. S.1" in again and ctx.counts["S"] == 3


@given(st.text().filter(lambda t: "[C" not in t and "calc:" not in t))
def test_escaping_round_trip(text: str) -> None:
    assert stdlib_html.unescape(cite_html(text, "M", {})) == text
    cell = table_html(["a|b"], [[text]], module="M", caption="c|<d>")
    assert "<script" not in cell and "<img" not in cell
    doc_text = embed_json({"x": text + "</script><!--" + SEPARATOR})
    inner = doc_text.split(">", 1)[1].rsplit("</script>", 1)[0]
    assert "</" not in inner and SEPARATOR not in inner
    assert json.loads(inner)["x"].startswith(text)


def section_of(text: str, vid: str) -> str:
    start = text.index(f'id="view-{vid}"')
    end = text.find('<section class="view', start + 10)
    return text[start : end if end > 0 else len(text)]


def test_page_is_self_contained(page: Page, assets: Assets) -> None:
    text = render(page, assets)
    assert "<link" not in text and 'src="http' not in text and 'href="http' not in text
    assert not re.search(r"\.(innerHTML|outerHTML)|insertAdjacentHTML", assets.charts_js)
    assert text.count('id="rbot-run"') == 1
    found = re.search(r'<script type="application/json" id="rbot-run">(.*?)</script>', text, re.S)
    assert found is not None
    embedded = json.loads(found.group(1))
    assert embedded["run_id"] == page.doc["run_id"]
    assert [b["id"] for b in embedded["front_page_blocks"]] == BLOCK_IDS
    assert all(e["data"] is None or e["data"]["number"] for e in embedded["charts"])


def test_every_block_renders_once_in_catalog_order_in_md_and_grid_in_html(
    page: Page, assets: Assets
) -> None:
    text = render(page, assets)
    for block_id in BLOCK_IDS:
        assert len(re.findall(f'data-block="{block_id}"', text)) == 1, block_id
    assert text.index('data-block="header"') < text.index('class="fp"')
    assert "PROJECTION not in this run" in text


def test_cite_anchors_and_evidence_rows_match(page: Page, assets: Assets) -> None:
    text = render(page, assets)
    refs = set(re.findall(r'class="cite" id="[^"]+" href="#ev-([^"]+)" data-ref="([^"]+)"', text))
    assert refs
    assert {ev for ev, _ in refs} <= set(re.findall(r'<tr id="ev-([^"]+)">', text))
    assert {ref.replace(":", "-") for _, ref in refs} == {ev for ev, _ in refs}
    ids = set(re.findall(r'class="cite" id="([^"]+)"', text))
    assert ids == set(re.findall(r'<a href="#(ref-[^"]+)">', section_of(text, "evidence")))
    assert '<abbr class="calc"' in text


def test_conditional_block_line(page: Page, assets: Assets) -> None:
    doc = copy.deepcopy(page.doc)
    doc["primary"] = False
    assert (
        '<p class="na-note span-12" data-block="transaction_summary">'
        "Transaction summary: not a Primary run</p>" in render(page, assets, doc)
    )


def test_figures_are_numbered_once_across_the_page(page: Page, assets: Assets) -> None:
    text = render(page, assets)
    head = r'data-chart="([^"]+)"[^>]*><div class="chart__head"><span class="chart__num">([^<]+)'
    first: dict[str, str] = {}
    for chart_id, number in re.findall(head, text):
        assert first.setdefault(chart_id, number) == number
    assert first["chart.model_strip.leverage"] == "Fig. S.1"
    assert first["chart.issue_counts"].startswith("Fig. E.")


def test_pane_lists_plan_modules_in_order(page: Page, assets: Assets) -> None:
    text = render(page, assets)
    nav = text[text.index('<nav class="nav"') : text.index("</nav>")]
    mods = [m for m in page.doc["plan"] if m in page.doc["modules"]]
    mods = [m for m in mods if m not in ("MODEL", "FIT", "CP-5", "CP-6")]
    expected = ["snapshot", *(f"module-{slug(m)}" for m in mods), "model", "portfolio-fit"]
    assert re.findall(r'data-view="([^"]+)"', nav) == [*expected, "evidence", "limitations"]
    assert "7 modules: 1 pass, 6 with limitations" in nav


def test_assets_that_would_close_the_inline_bundle_are_refused(page: Page, assets: Assets) -> None:
    for field in ("report_css", "report_js"):
        bad = dataclasses.replace(assets, **{field: "</style></script>"})
        with pytest.raises(ReportError, match="contains"):
            render_html(page.doc, [], [], bad)
