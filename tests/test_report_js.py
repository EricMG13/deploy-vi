"""`rbot/report/report.js` (Plan 07, 07.7): the static checks. Behaviour is checked in a browser."""

from __future__ import annotations

import html as stdlib_html
import json
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from report_run import complete_run

from rbotlib.catalog import load_catalog, load_contracts
from rbotlib.report import blocks as blk
from rbotlib.report import run_json
from rbotlib.report.assets import load
from rbotlib.report.charts import build_all
from rbotlib.report.html import render_html
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]
REPORT = RBOT_ROOT / "report"
FORBIDDEN = (r"http", r"fetch\(", r"XMLHttpRequest", r"innerHTML", r"import\(")


def test_report_js_has_no_network_or_innerhtml() -> None:
    text = (REPORT / "report.js").read_text(encoding="utf-8")
    for pattern in FORBIDDEN:
        assert not re.search(pattern, text), pattern


@pytest.mark.parametrize("name", ["report.js", "charts.js"])
def test_report_js_parses_under_node(name: str) -> None:
    """Fails, never skips, without node: CI has Node 24 and the owner's machine has it."""
    node = shutil.which("node")
    assert node is not None, "node is required to check the report scripts"
    done = subprocess.run([node, "--check", str(REPORT / name)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def data_keys(doc: Record) -> set[str]:
    """The `RBOT_DATA` keys report.js derives from the run JSON (citations, calcs, gaps)."""
    keys = {f"{m}:{c['id']}" for m, e in doc["handoffs"].items() for c in e["citations"]}
    brief = doc["run_brief"]["tables"].get("citations")
    if brief:
        keys |= {f"RUN_BRIEF:{r[brief['columns'].index('id')]}" for r in brief["rows"]}
    for line in (doc["model"] or {"lines": []})["lines"]:
        for cell in line["cells"]:
            gap = "gap:" if cell["value"] is None else ""
            keys.add(f"MODEL:{gap}{line['line_id']}:{cell['column_id']}")
    return keys


def test_every_data_ref_in_html_resolves(
    corpus_pack: Callable[[str], Any], tmp_path_factory: pytest.TempPathFactory
) -> None:
    run = complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))
    doc = run_json.build(run, RBOT_ROOT, "2026-10-14T00:00:00+00:00")
    contracts = load_contracts(RBOT_ROOT, load_rules(RBOT_ROOT), [])
    blocks = blk.front_page_blocks(doc, load_catalog(RBOT_ROOT), contracts)
    page = render_html(doc, blocks, build_all(doc, run_dir=run), load(REPORT))
    keys = data_keys(doc)
    cites = re.findall(r'<a [^>]*class="cite"[^>]*data-ref="([^"]+)"', page)
    datums = re.findall(r'data-datum="([^"]+)"', page)
    refs = [stdlib_html.unescape(r) for r in cites]
    refs += re.findall(r'"ref": "([^"]+)"', stdlib_html.unescape("".join(datums)))
    assert cites and datums
    assert not [r for r in refs if r not in keys]


def _chrome() -> str:
    names = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    found = next((p for p in (*map(shutil.which, names), mac) if p and Path(p).exists()), None)
    assert found is not None, "a Chrome or Chromium binary is required to run the report router"
    return found


def _visible_views(page: Path, fragment: str) -> list[str]:
    """Open the page in headless Chrome at `fragment`; return the view ids left unhidden."""
    done = subprocess.run(
        [
            _chrome(),
            "--headless=new",
            "--disable-gpu",
            "--virtual-time-budget=3000",
            "--dump-dom",
            f"{page.as_uri()}{fragment}",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0, done.stderr
    assert 'data-ready="1"' in done.stdout, "report.js did not finish its first route"
    tags = re.findall(r'<section\b[^>]*\bclass="view[ "][^>]*>', done.stdout)
    ids = [re.search(r'\bid="(view-[^"]+)"', t) for t in tags if " hidden" not in t]
    return [m.group(1) for m in ids if m]


def _report_page(
    corpus_pack: Callable[[str], Any], tmp_path_factory: pytest.TempPathFactory
) -> Path:
    run = complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))
    doc = run_json.build(run, RBOT_ROOT, "2026-10-14T00:00:00+00:00")
    contracts = load_contracts(RBOT_ROOT, load_rules(RBOT_ROOT), [])
    blocks = blk.front_page_blocks(doc, load_catalog(RBOT_ROOT), contracts)
    page = render_html(doc, blocks, build_all(doc, run_dir=run), load(REPORT))
    path = tmp_path_factory.mktemp("page") / "report.html"
    path.write_text(page, encoding="utf-8")
    return path


PRINT_PROBE = """<script>(function () {
  var snap = document.getElementById("view-snapshot"), root = document.documentElement;
  function look() {
    var blocks = [].slice.call(snap.querySelectorAll("[data-block]"));
    var shut = [].slice.call(document.querySelectorAll("details"));
    return {
      zoom: snap.style.zoom,
      width: snap.getBoundingClientRect().width,
      scrollWidth: snap.scrollWidth,
      printing: root.classList.contains("printing"),
      blocks: blocks.length,
      whole: blocks.filter(function (b) {
        return getComputedStyle(b).breakInside === "avoid";
      }).length,
      closed: shut.filter(function (d) { return !d.open; }).length
    };
  }
  var before = look(); window.RBOTPrint.prepare(); var during = look(); window.RBOTPrint.restore();
  var seen = { before: before, during: during, after: look() };
  root.setAttribute("data-f10", JSON.stringify(seen));
})();</script></body>"""


def test_print_keeps_the_snapshot_at_full_scale_with_whole_blocks(
    corpus_pack: Callable[[str], Any], tmp_path_factory: pytest.TempPathFactory
) -> None:
    path = _report_page(corpus_pack, tmp_path_factory)
    probed = path.with_name("probe.html")
    probed.write_text(
        path.read_text(encoding="utf-8").replace("</body>", PRINT_PROBE), encoding="utf-8"
    )
    done = subprocess.run(
        [
            _chrome(),
            "--headless=new",
            "--disable-gpu",
            "--virtual-time-budget=3000",
            "--dump-dom",
            probed.as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0, done.stderr
    found = re.search(r"data-f10=\"([^\"]+)\"", done.stdout)
    assert found, "the print probe did not run"
    seen = json.loads(stdlib_html.unescape(found.group(1)))
    during, after = seen["during"], seen["after"]
    assert during["printing"] and during["closed"] == 0
    assert during["zoom"] in ("", "1")
    assert during["width"] <= 985 and during["scrollWidth"] <= 985
    assert during["blocks"] > 0 and during["whole"] == during["blocks"]
    assert (after["printing"], after["zoom"], after["width"]) == (
        False,
        "",
        seen["before"]["width"],
    )
    assert after["whole"] < after["blocks"]
    assert after["closed"] == seen["before"]["closed"]


def test_opening_with_a_hash_shows_only_the_target_view(
    corpus_pack: Callable[[str], Any], tmp_path_factory: pytest.TempPathFactory
) -> None:
    path = _report_page(corpus_pack, tmp_path_factory)
    shown = {f: _visible_views(path, f) for f in ("#model", "#nosuchview", "")}
    snapshot = ["view-snapshot"]
    assert shown == {"#model": ["view-model"], "#nosuchview": snapshot, "": snapshot}
