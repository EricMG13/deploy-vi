"""Native receipts and analyst edits qualify current bytes without a worker retry."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import pytest
from test_accept import send
from test_model_host import eligible
from test_next import approved, blocked

from rbotlib import accept, attempts, cli, dispatch, state
from rbotlib import next as next_step
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


def evidence(run: Path) -> dict[str, bytes]:
    return {str(p.relative_to(run)): p.read_bytes() for p in (run / "validate").rglob("*.json")}


@pytest.mark.parametrize("qa", ["Pass", "Blocked"])
def test_valid_repeated_edit_has_current_digest_and_original_receipts(
    tmp_path: Path, qa: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, qa)
    original = copy.deepcopy(state.read(run)["steps"]["CP-1"])
    history = evidence(run)
    own = run / "handoffs/CP-1.md"
    for index in range(2):
        own.write_bytes(own.read_bytes() + f"\nAnalyst note {index}.\n".encode())
        assert next_step.select(run, RBOT_ROOT)["step"] == "MODEL"
        current = state.read(run)["steps"]["CP-1"]
        assert current["sha256"] == hashlib.sha256(own.read_bytes()).hexdigest()
        assert current["note"] == "edited"
        for field in ("attempts", "accept_history", "started_at", "finished_at", "validated_at"):
            assert current[field] == original[field]
        events = attempts.read_history(run, "CP-1", current)
        assert events[-1]["result"]["sha256"] == original["sha256"]
        assert accept.accept(run, RBOT_ROOT, "CP-1")["exit"] == (3 if qa == "Blocked" else 0)
        unchanged = (run / state.STATE).read_bytes()
        next_step.select(run, RBOT_ROOT)
        assert (run / state.STATE).read_bytes() == unchanged
    assert evidence(run) == history
    assert cli.main(["model", "--run", str(run)]) == 0
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-1C"


@pytest.mark.parametrize("edit", ["wrong-issuer", "missing", "symlink", "malformed"])
def test_invalid_edit_fails_named_running_required_consumer_without_fake_exit(
    tmp_path: Path, edit: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, "Pass")
    assert cli.main(["model", "--run", str(run)]) == 0
    send(run, RBOT_ROOT, "CP-3", "actual-running-consumer")
    (run / "handoffs/CP-3.md").write_text("DONE 0")
    assert accept.accept(run, RBOT_ROOT, "CP-3")["exit"] == 2
    original = copy.deepcopy(state.read(run)["steps"])
    history = evidence(run)
    own = run / "handoffs/CP-1.md"
    if edit == "wrong-issuer":
        own.write_text(own.read_text().replace("issuer_id: ACME", "issuer_id: FORGED"))
    elif edit == "missing":
        own.unlink()
    elif edit == "symlink":
        outside = tmp_path / "outside"
        outside.write_bytes(own.read_bytes())
        own.unlink()
        own.symlink_to(outside)
    else:
        own.write_text("DONE 0")
    next_step.select(run, RBOT_ROOT)
    current = state.read(run)["steps"]
    assert current["CP-1"]["status"] == "failed"
    assert current["CP-1"]["current_edits"][-1]["result"]["findings"]
    assert current["CP-3"]["status"] == "skipped"
    assert "CP-1" in current["CP-3"]["reason"]
    assert current["MODEL"]["status"] == "failed"
    for module in ("CP-1", "CP-3", "MODEL"):
        for field in (
            "attempts",
            "started_at",
            "finished_at",
            "validate_exit",
            "host_exit",
            "host_execution",
        ):
            if field in original[module]:
                assert current[module][field] == original[module][field]
    assert evidence(run) == history
    attempts.read_history(run, "CP-3", current["CP-3"])
    before = (run / state.STATE).read_bytes()
    assert cli.main(["model", "--run", str(run)]) == 1
    assert (run / state.STATE).read_bytes() == before


@pytest.mark.parametrize("target", ["CP-0", "RUN_BRIEF"])
def test_approved_narrative_preserves_anchors_and_precise_context(
    tmp_path: Path, target: str
) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    original = copy.deepcopy(state.read(run))
    history = evidence(run)
    own = run / ("run-brief.md" if target == "RUN_BRIEF" else "handoffs/CP-0.md")
    own.write_bytes(own.read_bytes() + b"\nAnalyst narrative clarification.\n")
    assert next_step.select(run, RBOT_ROOT)["step"] == "CP-1"
    current = state.read(run)
    assert current["approval"] == original["approval"]
    assert current["cp0_lineage"] == original["cp0_lineage"]
    assert evidence(run) == history
    assert (
        cli.main(
            ["validate", str(run / "run-brief.md"), "--module", "RUN_BRIEF", "--run", str(run)]
        )
        == 0
    )
    if target == "CP-0":
        assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == 0
    assert dispatch.prepare_message(run, RBOT_ROOT, "CP-1")


def test_changed_approved_decision_cannot_reapprove(tmp_path: Path) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    own = run / "run-brief.md"
    own.write_text(own.read_text().replace("Annual review", "Changed approved objective"))
    before = (run / state.STATE).read_bytes()
    with pytest.raises(RunError, match=r"approved|Approval|origin"):
        next_step.select(run, RBOT_ROOT)
    assert (run / state.STATE).read_bytes() == before


def test_optional_invalid_edit_is_excluded_with_visible_limitation(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT, "Pass", optional=True)
    blocked(run, RBOT_ROOT, "CP-1D")
    own = run / "handoffs/CP-1D.md"
    own.write_text(own.read_text().replace("issuer_id: ACME", "issuer_id: FORGED"))
    assert next_step.select(run, RBOT_ROOT)["step"] == "MODEL"
    assert state.read(run)["steps"]["CP-1D"]["status"] == "failed"
    assert cli.main(["model", "--run", str(run)]) == 0
    assert "CP-1D: failed; excluded" in (run / "handoffs/MODEL.md").read_text()
