"""`rbot render` (Plan 07, 07.6): a finished run to `report.md` and `report.html`, then the state.

The files are written atomically under the Approval lock by `state.update`'s `publish`, then
`report.md_sha256` (and with a full render `html_sha256`, `written_at`) are committed. Step
state is never changed, so a rendered run can be rendered again.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rbotlib import state
from rbotlib.catalog import load_catalog, load_contracts
from rbotlib.fsio import write_atomic
from rbotlib.inventory import RunError, output_path
from rbotlib.report import ReportError, run_json
from rbotlib.report.assets import load as load_assets
from rbotlib.report.blocks import call_band, front_page_blocks
from rbotlib.report.charts import build_all
from rbotlib.report.html import number_charts, render_html
from rbotlib.report.markdown import render_markdown
from rbotlib.rules import load_rules

Record = dict[str, Any]
BAD = ("blocked", "failed", "skipped")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render(
    run: Path, root: Path, *, md_only: bool, generated_at: str, doc: Record | None = None
) -> Record:
    """Build, write and record the Report; any refusal raises before a file or state changes.

    `doc` is the run JSON when the caller already built it (the command reuses it for its summary).
    """
    doc = doc or run_json.build(run, root, generated_at)
    run = state.run_path(run)
    contracts = load_contracts(root, load_rules(root), [])
    blocks = front_page_blocks(doc, load_catalog(root), contracts)
    charts = build_all(doc, run_dir=run)
    number_charts(doc, blocks, charts)
    texts = {"report.md": render_markdown(doc, blocks, charts)}
    if not md_only:
        texts["report.html"] = render_html(doc, blocks, charts, load_assets(root / "report"))
    targets = {name: output_path(run, name) for name in texts}

    def change(record: Record) -> None:
        report = record["report"]
        report["md_sha256"] = _sha(texts["report.md"])
        if "report.html" in texts:
            report["html_sha256"] = _sha(texts["report.html"])
            report["written_at"] = generated_at

    def publish() -> None:
        for name, text in texts.items():
            write_atomic(targets[name], text)

    return state.update(run, change, publish)


def summary(doc: Record) -> str:
    """The §10.4 console summary: Recommendation rows, limitation count, Blocked/failed/skipped."""
    rows = call_band(doc)["recommendation"].values()
    calls = [f"  {r['strategy']}: {r['recommendation']}" for r in rows]
    lines = ["Recommendation:", *calls] if calls else ["no Recommendation in this Pathway"]
    lim = doc["limitations"]
    unforeseen = [x for x in lim["unforeseen"] if x["kind"] in ("failed", "skipped")]
    lines.append(f"Limitations: {len(lim['cp5']) + len(unforeseen)}")
    bad = [f"{n} ({s['status']})" for n, s in doc["steps"].items() if s["status"] in BAD]
    lines.append("Blocked/failed/skipped: " + (", ".join(bad) if bad else "none"))
    return "\n".join(lines)


def run_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        doc = run_json.build(run, args.root, stamp)
        render(run, args.root, md_only=args.md_only, generated_at=stamp, doc=doc)
    except (ReportError, RunError, OSError, ValueError) as exc:
        print(f"error: {run}: {exc}", file=sys.stderr)
        return 1
    if not args.md_only:
        print(f"report.html: {run / 'report.html'}")
    print(f"report.md: {run / 'report.md'}")
    print(summary(doc))
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser("render", help="write report.html and report.md for a finished run")
    parser.add_argument("--run", dest="run_dir", required=True)
    parser.add_argument("--md-only", action="store_true", help="write report.md only")
    parser.set_defaults(run=run_command, log_run_guard=state.log_run_path)
