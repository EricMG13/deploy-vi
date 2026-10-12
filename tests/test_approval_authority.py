"""Actual public Approval refuses source and unsupported output envelopes before writes."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_approve import _ready

from rbotlib.approve import Choice, approve
from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.rules import Rules, load_rules
from spec_fixture import SOURCES, build_tree


def args(run: Path) -> list[str]:
    return [
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


@pytest.mark.parametrize("selected", ["source", "alias", "envelope", "markerless", "linked"])
def test_public_approval_never_logs_or_locks_an_unowned_source(
    tmp_path: Path, selected: str
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    source = pack / "evidence.md"
    source.write_bytes(b"Source evidence preserved\n")
    run = pack
    if selected == "alias":
        run = tmp_path / "alias"
        run.symlink_to(pack, target_is_directory=True)
    elif selected == "envelope":
        run = pack / "rbot-runs"
        run.mkdir()
    elif selected == "markerless":
        run = pack / "rbot-runs/20261012-acme-pending"
        run.mkdir(parents=True)
    elif selected == "linked":
        envelope = pack / "rbot-runs"
        envelope.mkdir()
        run = envelope / "20261012-acme-pending"
        run.symlink_to(pack, target_is_directory=True)
    before = sorted(str(p.relative_to(pack)) for p in pack.rglob("*"))
    assert main(args(run)) == 1
    assert sorted(str(p.relative_to(pack)) for p in pack.rglob("*")) == before
    assert source.read_bytes() == b"Source evidence preserved\n"
    choice = Choice("FULL_CREDIT_ASSESSMENT", "full", False, "Approver", False, (), False, False)
    with pytest.raises(RunError):
        approve(
            run,
            Path(__file__).parents[1] / "rbot",
            load_rules(Path(__file__).parents[1] / "rbot"),
            choice,
        )
    assert sorted(str(p.relative_to(pack)) for p in pack.rglob("*")) == before


def test_checked_approval_failure_logs_in_the_owned_run(tmp_path: Path, rules: Rules) -> None:
    root = tmp_path / "rbot"
    root.mkdir()
    build_tree(root, rules, SOURCES)
    run = _ready(root, tmp_path)
    command = args(run)
    command[command.index("FULL_CREDIT_ASSESSMENT")] = "UNKNOWN"
    assert main(["--root", str(root), *command]) == 1
    assert "approve --run" in (run / "log/rbot.log").read_text()
    assert not (run / ".approve.lock").exists()


def test_valid_alias_above_pack_keeps_effective_renamed_log(tmp_path: Path, rules: Rules) -> None:
    root = tmp_path / "rbot"
    root.mkdir()
    build_tree(root, rules, SOURCES)
    run = _ready(root, tmp_path)
    alias = tmp_path / "workspace-alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    selected = alias / run.relative_to(tmp_path)
    assert main(["--root", str(root), *args(selected)]) == 0
    target = run.parent / "20261011-acme-full-credit-assessment"
    assert (target / "log/rbot.log").is_file()
    assert not run.exists()
