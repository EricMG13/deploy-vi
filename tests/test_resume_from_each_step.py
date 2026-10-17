"""Native controller flow through every v1 step; generated financial gaps, no provider claim."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_resume import receipt

from cp0_fixture import cp0_handoff
from rbotlib import cli, runs, state
from rbotlib import next as selection
from rbotlib.contract import load_contract
from rbotlib.rules import RBOT_ROOT, load_rules
from test_grade import ACME, FILES

STEPS = [
    "CP-0",
    "CP-1",
    "CP-1A",
    "CP-DR",
    "CP-1B",
    "CP-1D",
    "MODEL",
    "CP-2",
    "CP-3",
    "FIT",
    "CP-5",
    "CP-6",
]
RUN_STEPS = [s for s in STEPS if s != "CP-DR"]  # Deep Research is not approved here: skipped
CONTROLLER = [
    "new-run",
    "inventory",
    "prepare",
    "CP-0",
    "brief",
    "brief-edits",
    "grade",
    "Approval",
    *RUN_STEPS[1:],
]
CHILD = (
    "from rbotlib.cli import main; import os, sys; code=main(sys.argv[1:]); "
    "sys.exit(code) if code not in (0, 3) else os._exit(73)"
)


def invoke(argv: list[str], killed: bool) -> None:
    if killed:
        child = subprocess.run(
            [sys.executable, "-c", CHILD, *argv],
            env=os.environ | {"PYTHONPATH": str(RBOT_ROOT / "scripts")},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert child.returncode == 73, child.stderr
    else:
        assert cli.main(argv) in (0, 3)


def handoff(run: Path, module: str) -> None:
    contract = load_contract(RBOT_ROOT / f"modules/{module}/contract.json", load_rules(RBOT_ROOT))
    text = (
        f"---\nmodule_id: {module}\nrun_id: {run.name}\nissuer_id: ACME\n"
        f"analysis_date: 2026-10-02\nqa_status: Blocked\ninputs: "
        + ", ".join(contract.handoff_inputs(required_only=True))
        + "\n---\n\n"
        "## Analysis\nGenerated native controller fixture.\n\n## Tables\n"
    )
    for table in contract.tables:
        text += f"\n<!-- table: {table.id} -->\n| " + " | ".join(c.name for c in table.columns)
        text += " |\n|" + "---|" * len(table.columns) + "\n"
        if table.id == "cp1.model_period_register":
            text += (
                "| FY2025 | FY2025 | — | FY | 2025-01-01 | 2025-12-31 | "
                "365 | USD | MILLIONS | — |\n"
            )
        if table.id == "cp1.instrument_identity":
            text += (
                "| FIXTURE | Generated unknown facility | Other | — | — | — | "
                "Acme Holdings, Inc. | — | — | — | — | No | [C1] |\n"
            )
        if table.id == "cp1.entity_profile":
            text += (
                "| Acme Holdings, Inc. | Fixture | December | USD | MILLIONS | "
                "Fixture | Fixture | [C1] |\n"
            )
    text += (
        "\n## Gaps\nGenerated fixture: no financial figures.\n\n## Citations\n"
        "<!-- table: citations -->\n| id | source | locator | excerpt |\n|---|---|---|---|\n"
    )
    if module == "CP-1":
        text += "| C1 | acme_10k.txt | p. 1 | Acme Holdings, Inc. |\n"
    (run / f"handoffs/{module}.md").write_text(text)


def flow(path: Path, stop: str) -> tuple[list[str], dict[str, tuple[str, int]]]:
    pack = path / "pack"
    pack.mkdir(parents=True)
    for name in FILES:
        (pack / name).write_text(f"{name}: Acme Holdings, Inc. as of 2026-10-02\n")
    meta = (
        "Portfolio ID,FUND\nPortfolio,Generated fund\nStrategy,CLO\nAs of,2026-05-29\n"
        "Currency,USD\nUnit,USD\nTotal NAV,1000000\nTotal Par,1000000\n"
    )
    (pack / "positions.csv").write_text(
        meta + "Issuer ID,Issuer,Par,% NAV\nACME,Acme Holdings Inc.,10000,1%\n"
    )
    (pack / "limits.csv").write_text(
        meta + "ID,Constraint Category,Parameter,Limit,Breach Type,Current Value\n"
        "L1,Issuer,Max issuer,2.5% NAV,Hard,1%\n"
    )
    original = {p.name: p.read_bytes() for p in pack.iterdir()}
    invoke(["new-run", "--pack", str(pack), "--issuer", "fixture"], stop == "new-run")
    run = runs.discover_unfinished(pack)
    assert run is not None
    for command in ("inventory", "prepare"):
        invoke([command, "--run", str(run)], stop == command)
    classes = FILES | {
        name: ("portfolio", kind, "FUND", "Yes")
        for name, kind in (
            ("positions.csv", "Portfolio positions"),
            ("limits.csv", "Portfolio limits"),
        )
    }
    (run / "handoffs").mkdir()
    (run / "handoffs/CP-0.md").write_text(
        cp0_handoff(run, ACME, "2026-10-02", classes, primary=False)
    )
    assert cli.main(receipt(run, "CP-0")) == 0
    invoke(["accept", "--run", str(run), "--module", "CP-0"], stop == "CP-0")
    invoke(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"], stop == "brief")
    invoke(
        [
            "brief",
            "--run",
            str(run),
            "--set",
            "objective=Fixture annual review",
            "--set",
            "analyst=Generated controller",
        ],
        stop == "brief-edits",
    )
    invoke(["grade", "--run", str(run)], stop == "grade")
    invoke(
        [
            "approve",
            "--run",
            str(run),
            "--pathway",
            "FULL_CREDIT_ASSESSMENT",
            "--depth",
            "full",
            "--primary",
            "no",
            "--analyst",
            "Generated controller",
        ],
        stop == "Approval",
    )
    renamed = runs.discover_unfinished(pack)
    assert renamed is not None and renamed != run
    run = renamed
    assert state.read(run)["plan"] == STEPS
    visited = []
    while True:
        selected = selection.select(run, RBOT_ROOT)
        if selected["kind"] == "done":
            break
        module = selected["step"]
        visited.append(module)
        if selected["kind"] == "host":
            invoke([module.lower(), "--run", str(run)], stop == module)
        else:
            handoff(run, module)
            assert cli.main(receipt(run, module)) == 0
            invoke(["accept", "--run", str(run), "--module", module], stop == module)
        assert runs.discover_unfinished(pack) == run
    assert {p.name: p.read_bytes() for p in pack.iterdir() if p.is_file()} == original
    record = state.read(run)
    assert record["approval"]["analyst"] == "Generated controller"
    assert not (run / "model.xlsx").exists()
    # a skipped step was never attempted, so it has no attempts count
    return visited, {m: (s["status"], s.get("attempts")) for m, s in record["steps"].items()}


@pytest.mark.parametrize("stop", CONTROLLER)
def test_resume_after_every_native_controller_step(tmp_path: Path, stop: str) -> None:
    expected = flow(tmp_path / "uninterrupted", "none")
    assert flow(tmp_path / "interrupted", stop) == expected
    assert expected[0] == RUN_STEPS[1:]
    assert expected[1]["CP-DR"] == ("skipped", None)
    assert json.dumps(expected[1])  # all terminal outcomes are compared, not accepted-state seeds
