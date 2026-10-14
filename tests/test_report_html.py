"""The Report A page parts and views (Plan 07 task 07.5), from a complete fixture run."""

from __future__ import annotations

import copy
import html as stdlib_html
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import pytest
from hypothesis import given
from hypothesis import strategies as st
from report_run import complete_run

from rbotlib.report import run_json
from rbotlib.report.charts import build_all
from rbotlib.report.html_parts import cite_html, embed_json, table_html
from rbotlib.report.html_views import Ctx, build_citations, model_view, module_view
from rbotlib.rules import RBOT_ROOT

Record = dict[str, Any]
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
