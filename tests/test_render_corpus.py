"""Plan 07 closure (interfaces spec section 12.5 row 07): the Report of a finished czr run.

The runs are driven by `report_run.complete_run` from hand-written fixture Handoffs, never
live model evidence. Each takes minutes, so the two runs are built once per module.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import proxy_continue
import pytest
from report_run import complete_run

import proxy_run
from rbotlib import state
from rbotlib.catalog import load_catalog
from rbotlib.cli import main
from rbotlib.report import ReportError
from rbotlib.report import render as rr
from rbotlib.rules import RBOT_ROOT

pytestmark = pytest.mark.corpus
Record = dict[str, Any]
T1, T2 = "2026-10-14T00:00:00+00:00", "2026-10-15T00:00:00+00:00"
CALC = "calc/CP-3-bond_analytics.json"
FIXTURE_CALC = Path(__file__).parent / "fixtures" / CALC


@pytest.fixture(scope="module")
def finished(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Path:
    return complete_run(corpus_pack, tmp_path_factory.mktemp("finished"))


@pytest.fixture(scope="module")
def failed(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Path:
    return complete_run(corpus_pack, tmp_path_factory.mktemp("failed"), fail="CP-1B")


def _restoring(run: Path) -> Iterator[Path]:
    """The run for one test; its state and log bytes return and its outputs go afterwards."""
    kept = {n: (run / n).read_bytes() for n in ("run-state.json", "log/rbot.log")}
    yield run
    for name in ("report.md", "report.html", CALC):
        (run / name).unlink(missing_ok=True)
    for name, raw in kept.items():
        (run / name).write_bytes(raw)


@pytest.fixture
def run(finished: Path) -> Iterator[Path]:
    yield from _restoring(finished)


@pytest.fixture
def failing(failed: Path) -> Iterator[Path]:
    yield from _restoring(failed)


def rendered(run: Path, stamp: str = T1) -> tuple[Record, str, str]:
    """Render the run; return its embedded JSON with the page and the Markdown."""
    rr.render(run, RBOT_ROOT, md_only=False, generated_at=stamp)
    md = (run / "report.md").read_text(encoding="utf-8")
    page = (run / "report.html").read_text(encoding="utf-8")
    doc: Record = json.loads(md.split("```json rbot-run\n", 1)[1].split("\n```", 1)[0])
    return doc, page, md


def charts(doc: Record) -> dict[str, Record]:
    return {c["chart_id"]: c for c in doc["charts"]}


def test_render_is_deterministic(run: Path) -> None:
    _, page1, md1 = rendered(run, T1)
    _, page2, md2 = rendered(run, T2)
    assert page1.replace(T1, "") == page2.replace(T2, "")
    assert md1.replace(T1, "") == md2.replace(T2, "")


def data_points(node: object) -> Iterator[Record]:
    """Every datum (a dict with `prov`) inside a chart spec."""
    if isinstance(node, dict):
        if "prov" in node:
            yield node
        for value in node.values():
            yield from data_points(value)
    elif isinstance(node, list):
        for value in node:
            yield from data_points(value)


def test_front_page_blocks_render(run: Path) -> None:
    doc, page, _ = rendered(run)
    ids = [b["id"] for b in doc["front_page_blocks"]]
    assert ids == [b.id for b in load_catalog(RBOT_ROOT).blocks["credit_snapshot"]]
    assert len(set(ids)) == len(ids)
    for block in ids:
        assert f'data-block="{block}"' in page, block
    drawn = [c for c in doc["charts"] if c["data"]]
    assert drawn
    for chart in doc["charts"]:
        assert f'data-chart="{chart["chart_id"]}"' in page, chart["chart_id"]
        assert chart["data"] or chart["note"]
    for chart in drawn:
        assert chart["data"]["title"] and chart["data"]["summary"]
        assert chart["twin"]["rows"] and chart["origin"] in ("host", "model")
        for datum in data_points(chart["data"]):
            assert "v" in datum and "reason" in datum
            assert datum["v"] is not None or datum["reason"]
    assert any(c["origin"] == "host" for c in drawn)


def test_chart_recompute_marks_origin(run: Path) -> None:
    assert charts(rendered(run)[0])["chart.talk_range"]["origin"] == "model"
    (run / "calc").mkdir(exist_ok=True)
    shutil.copy(FIXTURE_CALC, run / CALC)
    same = charts(rendered(run)[0])["chart.talk_range"]
    assert (same["origin"], same["note"]) == ("host", None)
    planted = json.loads((run / CALC).read_text(encoding="utf-8"))
    new = next(i for i in planted["instruments"] if i["facility_id"] == "NEW-1")
    new["talk_high_bps"] = "350"  # the recompute no longer gives the Handoff's implied levels
    (run / CALC).write_text(json.dumps(planted), encoding="utf-8")
    doc, page, md = rendered(run)
    altered = charts(doc)["chart.talk_range"]
    assert (altered["origin"], altered["note"]) == ("model", "differs from calculator")
    assert "differs from calculator" in md and 'data-origin="model"' in page


def test_failed_module_marks_block_and_view(failing: Path) -> None:
    doc, page, md = rendered(failing)
    line = "Credit summary: historical performance: CP-1B failed — fixture failure"
    block = next(b for b in doc["front_page_blocks"] if b["id"] == "historical_performance")
    assert block["line"] == line and line in md and line in page
    chip = r'href="#module-cp-1b"[^>]*>.*?data-status="Failed"'
    assert re.search(chip, page, re.S)
    assert {"kind": "failed", "step": "CP-1B", "reason": "fixture failure"} in (
        doc["limitations"]["unforeseen"]
    )
    assert "failed CP-1B fixture failure" in md


def test_done_branch_renders(run: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = state.read(run)["report"]
    assert before["written_at"] is None
    proxy_continue.advance(run, None, proxy_run._native)
    out = capsys.readouterr().out
    assert f"report.html: {run / 'report.html'}" in out and "Blocked/failed/skipped:" in out
    assert state.read(run)["report"]["written_at"] and (run / "report.md").is_file()
    proxy_continue.advance(run, None, proxy_run._native)
    assert f"report already written: {run / 'report.html'}" in capsys.readouterr().out


def test_render_refuses_an_unfinished_run(run: Path) -> None:
    def pending(record: Record) -> None:
        record["steps"]["CP-5"]["status"] = "pending"

    state.update(run, pending)
    with pytest.raises(ReportError):
        rr.render(run, RBOT_ROOT, md_only=False, generated_at=T1)
    assert main(["render", "--run", str(run)]) == 1
    assert not (run / "report.html").exists()
