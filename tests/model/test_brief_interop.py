"""The run-brief.md `rbot brief` writes (Plan 02) reads into the Model's Run
Brief fields: the SSIM EV multiple, Primary and the new tranches."""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.model.house_inputs import BriefFields, brief_fields


def test_a_run_brief_from_rbot_brief_reads_into_brief_fields(tmp_path: Path) -> None:
    run = make_run(tmp_path / "pack", "20261011-czr-pending")
    (run / "handoffs").mkdir()
    shutil.copy(FIXTURES / "handoffs" / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["brief", "--run", str(run), "--set", "ssim_ev_multiple=8.5"]) == 0
    brief = parse((run / "run-brief.md").read_text(encoding="utf-8"))
    fields = brief_fields(brief.front_matter, brief.tables)
    assert fields == BriefFields("20261011-czr-pending", Decimal("8.5"), True, frozenset({"NEW-1"}))
