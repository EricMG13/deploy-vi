"""A complete quick-depth run renders the Screening report (Plan 09, task 09.6)."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from report_run import RunShape, complete_run
from test_report_js import _chrome, _visible_views

from rbotlib.catalog import load_catalog, load_contracts
from rbotlib.report import blocks as blk
from rbotlib.report import run_json
from rbotlib.report.assets import load
from rbotlib.report.charts import build_all
from rbotlib.report.html import render_html
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]


def _render(
    corpus_pack: Callable[[str], Path], tmp_path: Path, shape: RunShape
) -> tuple[Path, Record, str]:
    run = complete_run(corpus_pack, tmp_path / "run", shape=shape)
    doc = run_json.build(run, RBOT_ROOT, "2026-10-16T00:00:00+00:00")
    contracts = load_contracts(RBOT_ROOT, load_rules(RBOT_ROOT), [])
    blocks = blk.front_page_blocks(doc, load_catalog(RBOT_ROOT), contracts)
    page = render_html(doc, blocks, build_all(doc, run_dir=run), load(RBOT_ROOT / "report"))
    path = tmp_path / "report.html"
    path.write_text(page, encoding="utf-8")
    return path, doc, page


def _console(path: Path, fragment: str) -> str:
    done = subprocess.run(
        [_chrome(), "--headless=new", "--disable-gpu", "--enable-logging=stderr", "--v=0",
         "--virtual-time-budget=3000", "--dump-dom", f"{path.as_uri()}{fragment}"],
        capture_output=True, text=True, timeout=120,
    )  # fmt: skip
    return "\n".join(x for x in done.stderr.splitlines() if "CONSOLE" in x)


def _check(path: Path, doc: Record, page: str) -> None:
    assert doc["depth"] == "quick" and "Screening only" in page
    assert re.search(r"<span>Screening only</span>", page)
    assert "Deep Research: not in this depth" in page and "CP-DR" not in doc["plan"]
    assert doc["fetched"] == [] and "not approved" not in page
    assert 'id="view-module-cp-l10"' in page and "chart.topic_counts" in page
    assert _visible_views(path, "#module-cp-l10") == ["view-module-cp-l10"]
    assert _visible_views(path, "") == ["view-snapshot"]
    assert _console(path, "#module-cp-l10") == ""


@pytest.mark.corpus
def test_a_quick_run_renders_the_credit_view_the_title_band_and_the_topic_chart(
    corpus_pack: Callable[[str], Path], tmp_path: Path
) -> None:
    path, doc, page = _render(corpus_pack, tmp_path, RunShape("quick"))
    assert "CP-L10" in doc["steps"] and doc["steps"]["CP-L10"]["status"] == "accepted"
    assert "CP-2" not in doc["steps"]
    view = doc["handoffs"]["CP-L10"]["tables"]["snapshot.credit_view"]["rows"][0]
    assert view[0] in page and "Deteriorating" in page
    _check(path, doc, page)


@pytest.mark.corpus
def test_a_quick_run_with_no_portfolio_still_renders(
    corpus_pack: Callable[[str], Path], tmp_path: Path
) -> None:
    path, doc, page = _render(corpus_pack, tmp_path, RunShape("quick", portfolios=False))
    assert doc["steps"]["FIT"]["status"] == "skipped"
    assert doc["steps"]["CP-6"]["status"] in ("accepted", "blocked")
    assert doc["handoffs"]["CP-6"]["qa_status"] == "Restricted"
    assert "no portfolio context" in page
    _check(path, doc, page)
