"""`rbot/report/report.js` (Plan 07, 07.7): the static checks. Behaviour is checked in a browser."""

from __future__ import annotations

import html as stdlib_html
import re
import shutil
import subprocess
from collections.abc import Callable
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
