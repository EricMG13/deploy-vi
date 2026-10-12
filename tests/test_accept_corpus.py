"""Required-root copies and hand-written fixture outputs, never live model evidence."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

import pytest
from test_accept import accept, send
from test_bootstrap import approve, ready
from test_modules import _blocked

from cp0_fixture import cp0_handoff, registry_classification
from rbotlib import state
from rbotlib.cli import main
from rbotlib.contract import load_contract
from rbotlib.corpus import load_registry
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import check


@pytest.mark.corpus
@pytest.mark.parametrize("qa", ["Restricted", "Blocked"])
def test_corpus_production_approval_and_module_accept(
    corpus_pack: Callable[[str], Path], tmp_path: Path, qa: str
) -> None:
    import shutil

    pack = shutil.copytree(corpus_pack("czr-2026q2-primary"), tmp_path / "working pack")
    files = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.iterdir() if p.is_file()
    }
    assert main(["new-run", "--pack", str(pack)]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    record = load_registry().pack("czr-2026q2-primary")
    (run / "handoffs").mkdir()
    (run / "handoffs/CP-0.md").write_text(
        cp0_handoff(
            run,
            ("Caesars Entertainment, Inc.", "CZR"),
            "2026-10-02",
            registry_classification(record),
            primary=False,
        )
    )
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    send(run, RBOT_ROOT, "CP-1")
    text = (
        (Path(__file__).parent / "fixtures/handoffs/CP-1.md")
        .read_text()
        .replace("run_id: 20261011-czr-full-credit-assessment", f"run_id: {run.name}")
    )
    rules = load_rules(RBOT_ROOT)
    contract = load_contract(RBOT_ROOT / "modules/CP-1/contract.json", rules)
    if qa == "Blocked":
        text = _blocked(text, contract)
    expected = 3 if qa == "Blocked" else 0
    assert check(text, contract, rules, run) == (expected, [])
    (run / "handoffs/CP-1.md").write_text(text)
    assert accept(run, module="CP-1") == expected
    assert state.read(run)["steps"]["CP-1"]["qa_status"] == qa
    assert {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.iterdir() if p.is_file()
    } == files
