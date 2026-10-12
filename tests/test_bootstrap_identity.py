"""Real confirmed readiness identity, including initially missing issuer identity."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_bootstrap import approve, pending, ready

from rbotlib import bootstrap, state
from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.rules import Rules, load_rules
from spec_fixture import SOURCES, build_tree


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


def test_front_issuer_cannot_override_source_backed_readiness(root: Path, tmp_path: Path) -> None:
    run = pending(tmp_path, root)
    cp0 = run / "handoffs/CP-0.md"
    cp0.write_text(cp0.read_text().replace("issuer_id: ACME", "issuer_id: OTHER"))
    ready(run, root)
    before = (run / state.STATE).read_bytes()
    with pytest.raises(RunError, match="identity"):
        bootstrap.complete_cp0(run, root, load_rules(root))
    command = [
        "--root",
        str(root),
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
        "Approver",
    ]
    assert main(command) == 1
    assert (run / state.STATE).read_bytes() == before


def test_unknown_readiness_stays_honest_then_analyst_supplies_identity(
    root: Path, tmp_path: Path
) -> None:
    run = pending(tmp_path, root)
    cp0 = run / "handoffs/CP-0.md"
    text = cp0.read_text().replace("issuer_id: ACME", "issuer_id: —")
    text = text.replace(
        "| issuer_id | — | ACME | Analyst-asserted | — |", "| issuer_id | — | — | Gap | — |"
    )
    cp0.write_text(text)
    complete = bootstrap.complete_cp0(run, root, load_rules(root))
    assert complete["issuer_id"] is None
    assert bootstrap.phase(run, root, load_rules(root)) == "approval"
    ready(run, root)
    assert main(["brief", "--run", str(run), "--set", "issuer_id=ACME"]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    original = cp0.read_bytes()
    target = approve(run, root)
    assert state.read(target)["issuer_id"] == "ACME"
    assert state.read(target)["cp0_lineage"]["issuer_id"] == "—"
    assert (target / "handoffs/CP-0.md").read_bytes() == original
    assert bootstrap.phase(target, root, load_rules(root)) == "analysis"


def test_confirmed_known_issuer_change_needs_the_completion_owner(
    root: Path, tmp_path: Path
) -> None:
    run = pending(tmp_path, root)
    bootstrap.complete_cp0(run, root, load_rules(root))
    ready(run, root)
    assert main(["brief", "--run", str(run), "--set", "issuer_id=OTHER"]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0
    before = (run / state.STATE).read_bytes()
    command = [
        "--root",
        str(root),
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
        "Approver",
    ]
    assert main(command) == 1
    assert (run / state.STATE).read_bytes() == before
