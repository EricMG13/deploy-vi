"""`report.md` content and its embedded run JSON (Plan 07 task 07.6)."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from report_run import complete_run, save_fetched

from rbotlib.catalog import load_catalog, load_contracts
from rbotlib.report import blocks as blk
from rbotlib.report import run_json
from rbotlib.report.charts import build_all
from rbotlib.report.markdown import render_markdown
from rbotlib.rules import RBOT_ROOT, load_rules

Record = dict[str, Any]
CATALOG = load_catalog(RBOT_ROOT)
BLOCK_TITLES = [b.title for b in CATALOG.blocks["credit_snapshot"]]
NOW = "2026-10-14T00:00:00+00:00"


@pytest.fixture(scope="module")
def built(
    corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory
) -> tuple[Record, list[Record], list[Record], str]:
    run = complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))
    doc = run_json.build(run, RBOT_ROOT, NOW)
    contracts = load_contracts(RBOT_ROOT, load_rules(RBOT_ROOT), [])
    blocks = blk.front_page_blocks(doc, CATALOG, contracts)
    charts = build_all(doc, run_dir=run)
    return doc, blocks, charts, render_markdown(doc, blocks, charts)


def test_markdown_has_every_tab_and_block_in_order(
    built: tuple[Record, list[Record], list[Record], str],
) -> None:
    text = built[3]
    body = text.split("```json rbot-run")[0]
    assert body.startswith("# Credit Snapshot — ")
    h2 = re.findall(r"^## (.+)$", body, re.MULTILINE)
    assert h2 == [
        "Snapshot",
        "Analysis",
        "Model",
        "Portfolio Fit",
        "What changed",
        "Evidence",
        "Limitations",
    ]
    snapshot = body.split("\n## Analysis")[0]
    at = [snapshot.index(f"### {t}\n") for t in BLOCK_TITLES]
    assert at == sorted(at)
    analysis = body.split("\n## Analysis")[1].split("\n## Model")[0]
    for module in ("CP-1", "CP-2", "CP-3"):
        assert f"({module})" in analysis
    assert "Deep Research: not in" not in body and "Not in this run: not approved" not in body
    cpdr = analysis.split("(CP-DR)\n\n")[1].split("\n### ")[0]
    assert "#### Fetched sources\n\nFetched sources: none" in cpdr
    assert "[C1]" in body and "calc: " in body
    assert "| --- " not in body and "|---|" in body


def test_markdown_json_block_round_trips(
    built: tuple[Record, list[Record], list[Record], str],
) -> None:
    doc, blocks, charts, text = built
    assert text.endswith("\n```\n")
    head, _, rest = text.partition("```json rbot-run\n")
    embedded = json.loads(rest.removesuffix("\n```\n"))
    assert embedded == json.loads(
        json.dumps({**doc, "charts": charts, "front_page_blocks": blocks})
    )
    assert "```" not in head


def test_markdown_lists_fetched_sources_under_the_cp_dr_section(
    corpus_pack: Callable[[str], Path], tmp_path: Path
) -> None:
    run = complete_run(corpus_pack, tmp_path)
    save_fetched(run, "01-example.com.md", "https://example.com/a", "RQ-1")
    doc = run_json.build(run, RBOT_ROOT, NOW)
    text = render_markdown(doc, [], build_all(doc, run_dir=run))
    cpdr = text.split("(CP-DR)\n\n")[1].split("\n### ")[0]
    fetched = cpdr.split("#### Fetched sources")[1]
    assert "https://example.com/a" in fetched and "2026-10-10" in fetched
    assert "RQ-1" in fetched and "fetched/01-example.com.md" in fetched
    assert "none" not in fetched.split("\n\n")[1]


def test_markdown_names_the_reason_when_deep_research_was_skipped(
    built: tuple[Record, list[Record], list[Record], str],
) -> None:
    doc, blocks, charts, _ = built
    skipped = {"status": "skipped", "reason": "not approved"}
    doc = {**doc, "steps": {**doc["steps"], "CP-DR": skipped}}
    doc["handoffs"] = {k: v for k, v in doc["handoffs"].items() if k != "CP-DR"}
    text = render_markdown(doc, blocks, charts)
    assert "## Deep Research\n\nNot in this run: not approved." in text
    assert "- Deep Research: not in this run: not approved" in text
