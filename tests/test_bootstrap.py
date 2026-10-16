"""Generated, source-backed CP-0 fixtures exercise the actual production bootstrap."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path

import pytest
from state_receipt_assertions import outcome_bytes

from cp0_fixture import cp0_handoff
from rbotlib import bootstrap, state
from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.rules import Rules, load_rules
from spec_fixture import SOURCES, build_tree
from test_grade import ACME, FILES


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


def pending(tmp_path: Path, root: Path) -> Path:
    pack = tmp_path / "pack"
    pack.mkdir()
    for name in FILES:
        (pack / name).write_text(f"{name}: Acme Holdings, Inc. as of 2026-10-02\n")
    assert main(["new-run", "--pack", str(pack), "--issuer", "untrusted hint"]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    (run / "handoffs").mkdir()
    text = cp0_handoff(run, ACME, "2026-10-02", FILES, primary=False)
    text = text.replace(
        "| issuer | — | Acme Holdings, Inc. | Analyst-asserted | — |",
        "| issuer | — | Acme Holdings, Inc. | Sourced | [C1] |",
    )
    text += "| C1 | acme_10k.txt | p. 1 | Acme Holdings, Inc. |\n"
    (run / "handoffs" / "CP-0.md").write_text(text)
    return run


def ready(run: Path, root: Path) -> None:
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    edits = ["--set", "objective=Annual review", "--set", "analyst=A. Analyst"]
    assert main(["brief", "--run", str(run), *edits]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0


def approve(run: Path, root: Path) -> Path:
    args = ["--root", str(root), "approve", "--run", str(run)]
    args += ["--pathway", "FULL_CREDIT_ASSESSMENT", "--depth", "full"]
    args += ["--primary", "no", "--analyst", "Approver"]
    assert main(args) == 0
    return next(run.parent.iterdir())


@pytest.mark.parametrize("shipped", [False, True])
def test_real_new_run_cp0_completion_wait_and_approval(
    root: Path, tmp_path: Path, shipped: bool
) -> None:
    if shipped:
        root = Path(__file__).parents[1] / "rbot"

    run = pending(tmp_path, root)
    rules = load_rules(root)
    source = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    assert bootstrap.phase(run, root, rules) == "cp0"
    assert state.read(run)["issuer_id"] is None
    before = (run / "handoffs/CP-0.md").read_bytes()
    complete = bootstrap.complete_cp0(run, root, rules)
    cp0 = complete["steps"]["CP-0"]
    assert cp0["status"] == "accepted" and cp0["validate_exit"] == 0
    assert cp0["attempts"] == 0 and "started_at" not in cp0 and "model" not in cp0
    assert "validated_at" in cp0 and "finished_at" not in cp0
    assert complete["plan"] == ["CP-0"] and complete["approval"] is None
    assert bootstrap.phase(run, root, rules) == "approval"
    ready(run, root)
    target = approve(run, root)
    final = state.read(target)
    assert final["steps"]["CP-0"] == cp0
    assert final["steps"]["CP-1"]["status"] == "pending"
    assert bootstrap.phase(target, root, rules) == "analysis"
    assert (target / "handoffs/CP-0.md").read_bytes() == before
    assert final["cp0_lineage"] == {
        "pending_run_id": run.name,
        "issuer_id": "ACME",
        "sha256": hashlib.sha256(before).hexdigest(),
    }
    assert (
        final["run_brief_sha256"]
        == hashlib.sha256((target / "run-brief.md").read_bytes()).hexdigest()
    )
    assert "approve --run" in (target / "log/rbot.log").read_text()
    assert {p.name: p.read_bytes() for p in target.parent.parent.iterdir() if p.is_file()} == source
    args = [
        "--root",
        str(root),
        "approve",
        "--run",
        str(target),
        "--pathway",
        "FULL_CREDIT_ASSESSMENT",
    ]
    assert main([*args, "--depth", "full", "--primary", "no", "--analyst", "Again"]) == 1


def test_approval_qualifies_pending_from_actual_validation(root: Path, tmp_path: Path) -> None:
    run = pending(tmp_path, root)
    ready(run, root)
    target = approve(run, root)
    assert state.read(target)["steps"]["CP-0"]["status"] == "accepted"


@pytest.mark.parametrize(
    "change,match",
    [
        (lambda text: text.replace("run_id: ", "run_id: unrelated-"), "identity"),
        (lambda text: text.replace("module_id: CP-0", "module_id: CP-1"), "exit 4"),
        (lambda text: text.replace("## Analysis", "## Wrong"), "exit 2"),
    ],
)
def test_invalid_handoff_cannot_complete(
    root: Path, tmp_path: Path, change: Callable[[str], str], match: str
) -> None:

    run = pending(tmp_path, root)
    cp0 = run / "handoffs/CP-0.md"
    cp0.write_text(change(cp0.read_text()))
    before = outcome_bytes(run)
    with pytest.raises(RunError, match=match):
        bootstrap.complete_cp0(run, root, load_rules(root))
    assert outcome_bytes(run) == before


def test_io_failure_and_shared_lock_refuse_without_changing_state(
    root: Path, tmp_path: Path
) -> None:

    run = pending(tmp_path, root)
    before = outcome_bytes(run)
    owner = state._Locked(run)
    try:
        with pytest.raises(RunError, match="holds"):
            bootstrap.complete_cp0(run, root, load_rules(root))
        assert outcome_bytes(run) == before
    finally:
        assert owner.close() == []
    (run / "prepared/index.json").unlink()
    with pytest.raises(RunError, match="exit 1"):
        bootstrap.complete_cp0(run, root, load_rules(root))
    assert outcome_bytes(run) == before


def test_accepted_metadata_preserved_and_stale_hash_requires_owner(
    root: Path, tmp_path: Path
) -> None:

    run = pending(tmp_path, root)
    rules = load_rules(root)
    bootstrap.complete_cp0(run, root, rules)

    def evidence(record: state.Record) -> None:
        record["steps"]["CP-0"].update(
            attempts=2, started_at=record["created_at"], history=[{"observed": "fixture"}]
        )
        record["extension"] = {"retain": True}

    complete = state.update(run, evidence)
    cp0 = complete["steps"]["CP-0"]
    handoff = run / "handoffs/CP-0.md"
    original = handoff.read_bytes()
    handoff.write_bytes(original + b"\n")
    ready(run, root)
    with pytest.raises(RunError, match=r"changed.*completion owner"):
        bootstrap.complete_cp0(run, root, rules)
    args = [
        "--root",
        str(root),
        "approve",
        "--run",
        str(run),
        "--pathway",
        "FULL_CREDIT_ASSESSMENT",
    ]
    assert main([*args, "--depth", "full", "--primary", "no", "--analyst", "Approver"]) == 1
    handoff.write_bytes(original)
    ready(run, root)
    target = approve(run, root)
    final = state.read(target)
    assert final["steps"]["CP-0"] == cp0 and final["extension"] == {"retain": True}
    handoff = target / "handoffs/CP-0.md"
    handoff.write_bytes(original.replace(run.name.encode(), b"20261012-unrelated-pending"))
    with pytest.raises(RunError, match="identity"):
        bootstrap.phase(target, root, rules)


def test_blocked_is_completed_but_waits_for_approval(root: Path, tmp_path: Path) -> None:

    run = pending(tmp_path, root)
    handoff = run / "handoffs/CP-0.md"
    handoff.write_text(handoff.read_text().replace("qa_status: Restricted", "qa_status: Blocked"))
    record = bootstrap.complete_cp0(run, root, load_rules(root))
    assert record["steps"]["CP-0"]["status"] == "blocked"
    assert bootstrap.phase(run, root, load_rules(root)) == "approval"


@pytest.mark.parametrize(
    "key,value", [("pending_run_id", "arbitrary"), ("sha256", "0" * 64), ("issuer_id", "OTHER")]
)
def test_lineage_tampering_refuses(root: Path, tmp_path: Path, key: str, value: str) -> None:

    run = pending(tmp_path, root)
    ready(run, root)
    target = approve(run, root)
    record = state.read(target)
    record["cp0_lineage"][key] = value
    (target / state.STATE).write_text(json.dumps(record))
    with pytest.raises(RunError):
        bootstrap.phase(target, root, load_rules(root))


def test_handoff_identity_and_hash_use_one_qualified_snapshot(
    root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import rbotlib.approve as ap

    run = pending(tmp_path, root)
    ready(run, root)
    real = ap._cp0_step

    def changed_after_validation(run: Path, root: Path, rules: Rules) -> bootstrap.QualifiedCP0:
        qualified = real(run, root, rules)
        cp0 = run / "handoffs/CP-0.md"
        cp0.write_text(cp0.read_text().replace(f"run_id: {run.name}", "run_id: unrelated"))
        return qualified

    monkeypatch.setattr(ap, "_cp0_step", changed_after_validation)
    args = [
        "--root",
        str(root),
        "approve",
        "--run",
        str(run),
        "--pathway",
        "FULL_CREDIT_ASSESSMENT",
    ]
    assert main([*args, "--depth", "full", "--primary", "no", "--analyst", "Approver"]) == 1
    assert run.exists() and state.read(run)["approval"] is None


@pytest.mark.parametrize("kind", ["symlink", "hardlink"])
def test_linked_handoff_never_becomes_accepted(root: Path, tmp_path: Path, kind: str) -> None:

    run = pending(tmp_path, root)
    cp0 = run / "handoffs/CP-0.md"
    other = tmp_path / "other.md"
    cp0.rename(other)
    if kind == "symlink":
        cp0.symlink_to(other)
    else:
        cp0.hardlink_to(other)
    before = outcome_bytes(run)
    with pytest.raises(RunError):
        bootstrap.complete_cp0(run, root, load_rules(root))
    assert outcome_bytes(run) == before


@pytest.mark.parametrize("status", ["failed", "skipped"])
def test_terminal_cp0_cannot_be_resurrected_by_approval(
    root: Path, tmp_path: Path, status: str
) -> None:

    run = pending(tmp_path, root)
    state.set_status(run, "CP-0", status, "observed refusal")
    before = outcome_bytes(run)
    with pytest.raises(RunError, match="completion requires"):
        bootstrap.complete_cp0(run, root, load_rules(root))
    assert outcome_bytes(run) == before
    ready(run, root)
    before = outcome_bytes(run)
    args = [
        "--root",
        str(root),
        "approve",
        "--run",
        str(run),
        "--pathway",
        "FULL_CREDIT_ASSESSMENT",
    ]
    assert main([*args, "--depth", "full", "--primary", "no", "--analyst", "Approver"]) == 1
    assert outcome_bytes(run) == before


def test_wrong_known_issuer_and_unanchored_citation_refuse(root: Path, tmp_path: Path) -> None:

    run = pending(tmp_path, root)
    state.update(run, lambda record: record.update(issuer_id="OTHER"))
    with pytest.raises(RunError, match="identity"):
        bootstrap.complete_cp0(run, root, load_rules(root))
    state.update(run, lambda record: record.update(issuer_id=None))
    cp0 = run / "handoffs/CP-0.md"
    cp0.write_text(
        cp0.read_text().replace("| p. 1 | Acme Holdings, Inc. |", "| p. 1 | Unanchored issuer |")
    )
    with pytest.raises(RunError, match="excerpt not found"):
        bootstrap.complete_cp0(run, root, load_rules(root))
    assert state.read(run)["steps"]["CP-0"]["status"] == "pending"


def test_completion_and_approval_share_actual_writer_lock(
    root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading

    import rbotlib.approve as ap

    run = pending(tmp_path, root)
    ready(run, root)
    inside, done = threading.Event(), threading.Event()
    real = ap._cp0_step

    def slow(run: Path, root: Path, rules: Rules) -> bootstrap.QualifiedCP0:
        inside.set()
        assert done.wait(10)
        return real(run, root, rules)

    monkeypatch.setattr(ap, "_cp0_step", slow)
    errors: list[AssertionError] = []

    def approve_in_thread() -> None:
        try:
            approve(run, root)
        except AssertionError as exc:
            errors.append(exc)

    thread = threading.Thread(target=approve_in_thread)
    thread.start()
    try:
        assert inside.wait(10)
        with pytest.raises(RunError, match="holds"):
            bootstrap.complete_cp0(run, root, load_rules(root))
    finally:
        done.set()
        thread.join(10)
    assert not thread.is_alive() and not errors
    target = next(run.parent.iterdir())
    assert state.read(target)["steps"]["CP-0"]["status"] == "accepted"
    with pytest.raises(RunError, match="already approved"):
        bootstrap.complete_cp0(target, root, load_rules(root))
    assert (target / state.LOCK).exists()


def test_fifo_handoff_refuses_before_opening_and_releases_writer_lock(
    root: Path, tmp_path: Path
) -> None:
    import os
    import subprocess
    import sys

    run = pending(tmp_path, root)
    cp0 = run / "handoffs/CP-0.md"
    cp0.unlink()
    os.mkfifo(cp0)
    before = outcome_bytes(run)
    code = (
        "from pathlib import Path; from rbotlib.bootstrap import complete_cp0; "
        "from rbotlib.rules import load_rules; import sys\n"
        "try: complete_cp0(Path(sys.argv[1]), Path(sys.argv[2]), load_rules(Path(sys.argv[2])))\n"
        "except (OSError, ValueError) as exc: print(exc); sys.exit(1)\n"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", code, str(run), str(root)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ | {"PYTHONPATH": str(Path(__file__).parents[1] / "rbot/scripts")},
    )
    try:
        out, err = process.communicate(timeout=2)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()
    assert process.returncode == 1 and "regular file" in out and not err
    assert outcome_bytes(run) == before
    assert (run / state.LOCK).exists()


def test_undecodable_handoff_names_the_input_and_preserves_state(
    root: Path, tmp_path: Path
) -> None:
    run = pending(tmp_path, root)
    (run / "handoffs/CP-0.md").write_bytes(b"\xff")
    before = outcome_bytes(run)
    with pytest.raises(RunError, match=r"CP-0.md.*readable"):
        bootstrap.complete_cp0(run, root, load_rules(root))
    assert outcome_bytes(run) == before
    assert (run / state.LOCK).exists()
