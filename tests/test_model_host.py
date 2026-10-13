"""Actual controller receipts and host execution; fixtures do not qualify workers."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
from test_accept import send
from test_next import approved

from rbotlib import accept, cli, state
from rbotlib import next as next_step
from rbotlib.contract import load_contract
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, load_rules


def eligible(
    tmp_path: Path,
    root: Path,
    qa: str = "Blocked",
    optional: bool = False,
    *,
    variant: str = "",
) -> Path:
    run = approved(tmp_path, root)
    contract = load_contract(root / "modules/CP-1/contract.json", load_rules(root))
    text = (
        f"---\nmodule_id: CP-1\nrun_id: {run.name}\nissuer_id: ACME\n"
        f"analysis_date: 2026-10-02\nqa_status: {qa}\ninputs: CP-0\n---\n"
        "\n## Analysis\nGenerated controller fixture; financial gaps.\n\n## Tables\n"
    )
    accepted_rows = {
        "cp1.model_account_register": "| revenue | FY2025 | — | NOT AVAILABLE | — | — |\n",
        "cp1.debt_facility_register": (
            "| FIXTURE | Generated unknown facility | FY2025 | TERM LOAN | USD | — | — | — | "
            "NOT_STATED | NOT_STATED | Not stated | — | NOT_LEASE | NOT_STATED | "
            "NOT_STATED | — | — | — | — | — | — |\n"
        ),
        "cp1.instrument_identity": (
            "| FIXTURE | Generated unknown facility | Other | — | — | — | Acme Holdings, Inc. | "
            "— | — | — | — | No | [C1] |\n"
        ),
        "cp1.reconciliation_checks": (
            "| fixture | FY2025 | Source gap | — | — | — | Missing | No figures | — |\n"
        ),
        "cp1.entity_profile": (
            "| Acme Holdings, Inc. | Fixture | December | USD | MILLIONS | Fixture | "
            "Fixture | [C1] |\n"
        ),
    }
    for table in contract.tables:
        text += (
            f"\n<!-- table: {table.id} -->\n| "
            + " | ".join(c.name for c in table.columns)
            + " |\n|"
            + "---|" * len(table.columns)
            + "\n"
        )
        if table.id == "cp1.model_period_register":
            text += (
                "| FY2025 | FY2025 | — | FY | 2025-01-01 | 2025-12-31 | "
                "365 | USD | MILLIONS | — |\n"
            )
        if variant == "judgment-gap" and table.id == "cp1.model_period_register":
            text += (
                "| LTM_CURRENT | FY2025 | — | LTM | 2025-01-01 | "
                "2025-12-31 | 365 | USD | MILLIONS | FY2025 |\n"
            )
        if variant == "judgment-gap" and table.id == "cp1.adjusted_ebitda_bridge":
            text += (
                "| fixture_addback | Generated gap | "
                "COST_SAVINGS | REALIZED | 1 | FY2025 | — | — | — |\n"
            )
        if qa != "Blocked":
            text += accepted_rows.get(table.id, "")
    text += (
        "\n## Gaps\nGenerated fixture: no figures.\n\n## Citations\n"
        "<!-- table: citations -->\n| id | source | locator | excerpt |\n|---|---|---|---|\n"
    )
    if qa != "Blocked":
        text += "| C1 | acme_10k.txt | p. 1 | Acme Holdings, Inc. |\n"
    if variant == "wrong-date":
        text = text.replace("analysis_date: 2026-10-02", "analysis_date: 2025-10-02")
    raw = text.encode("utf-8")
    (run / "handoffs/CP-1.md").write_bytes(
        raw.replace(b"\n", b"\r\n") if variant == "crlf" else raw
    )
    send(run, root, "CP-1", "fixture-host-input")
    assert accept.accept(run, root, "CP-1")["exit"] == (3 if qa == "Blocked" else 0)
    for module in ("CP-1A", "CP-1B") if optional else ("CP-1A", "CP-1B", "CP-1D"):
        state.set_status(run, module, "failed", "fixture optional producer failed")
    if not optional:
        assert next_step.select(run, root)["step"] == "MODEL"
    return run


def test_actual_returned_model_command_completes_and_advances(tmp_path: Path) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "selected ' root")
    run = eligible(tmp_path, root)
    selected = next_step.select(run, root)
    command = shlex.split(selected["command"])
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert all((run / name).is_file() for name in ("model.json", "model.xlsx", "handoffs/MODEL.md"))
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "accepted"
    assert current["attempts"] == 1
    assert "started_at" in current and "finished_at" in current
    assert current["host_exit"] == 0
    assert len(current["outputs"]) == 3
    assert json.loads((run / "model.json").read_text())["inputs"]["CP-1D"] is None
    assert next_step.select(run, root)["step"] == "CP-3"
    rows = (run / "log/rbot.log").read_bytes().splitlines()
    model_rows = [row for row in rows if b" model --run " in row]
    assert len(model_rows) == 1 and model_rows[0].endswith(b"\t0")
    assert str(run / "handoffs/MODEL.md") in (run / "dispatch/CP-3.md").read_text()


def test_public_log_failure_cannot_leave_model_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)

    def denied(run: Path, argv: list[str], code: int, **kwargs: object) -> None:
        raise OSError("fixture final log append denied")

    monkeypatch.setattr(cli, "_log", denied)
    assert cli.main(["model", "--run", str(run)]) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed"
    assert current["host_exit"] == 1
    assert "log" in current["reason"]


def test_successful_accepted_model_cannot_be_downgraded(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    assert cli.main(["model", "--run", str(run)]) == 0
    before = (run / state.STATE).read_bytes()
    with pytest.raises(RunError, match="cannot set accepted to failed"):
        state.set_status(run, "MODEL", "failed", "late caller failure")
    assert (run / state.STATE).read_bytes() == before
