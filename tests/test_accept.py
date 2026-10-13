"""Independent acceptance of fixture bytes; no live Module qualification."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from test_bootstrap import approve, pending, ready

from rbotlib import attempts, dispatch, state
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT


def send(
    run: Path, root: Path, module: str = "CP-0", name: str = "fixture-send", retry: bool = False
) -> None:
    findings = f"validate/{module}.json" if retry else None
    text = dispatch.prepare_message(run, root, module, findings)
    receipt = attempts.DispatchReceipt(
        name, "fixture-controller", hashlib.sha256(text.encode()).hexdigest()
    )
    attempts.register_dispatch(run, root, module, receipt)


def accept(run: Path, root: Path = RBOT_ROOT, module: str = "CP-0") -> int:
    return main(["--root", str(root), "accept", "--run", str(run), "--module", module])


@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize(
    "qa,code,status",
    [("Pass", 0, "accepted"), ("Restricted", 0, "accepted"), ("Blocked", 3, "blocked")],
)
def test_accept_exact_current_bytes_and_cp0_approval_lineage(
    tmp_path: Path, selected: bool, qa: str, code: int, status: str
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "selected ' root") if selected else RBOT_ROOT
    run = pending(tmp_path, root)
    source = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    own = run / "handoffs/CP-0.md"
    own.write_text(own.read_text().replace("qa_status: Restricted", f"qa_status: {qa}"))
    send(run, root)
    own.write_text(own.read_text() + "\nDONE 4\n")  # worker claim is never acceptance authority
    raw = own.read_bytes()
    assert accept(run, root) == code
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == status and step["qa_status"] == qa and step["attempts"] == 1
    assert step["sha256"] == hashlib.sha256(raw).hexdigest()
    assert "model" not in step and "finished_at" in step
    latest = json.loads((run / "validate/CP-0.json").read_text())
    assert set(latest) == {"exit", "findings", "sha256", "at"} and latest["exit"] == code
    history = {p.name: p.read_bytes() for p in (run / "validate/history/CP-0").iterdir()}
    before = (run / state.STATE).read_bytes()
    assert accept(run, root) == code and (run / state.STATE).read_bytes() == before
    ready(run, root)
    target = approve(run, root)
    assert state.read(target)["steps"]["CP-0"] == step
    assert {p.name: p.read_bytes() for p in (target / "validate/history/CP-0").iterdir()} == history
    assert accept(target, root) == code
    assert (target / "handoffs/CP-0.md").read_bytes() == raw
    assert {p.name: p.read_bytes() for p in target.parent.parent.iterdir() if p.is_file()} == source


def test_no_reported_dispatch_or_seeded_attempts_cannot_accept(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    before = (run / state.STATE).read_bytes()
    assert accept(run) == 1 and (run / state.STATE).read_bytes() == before
    state.update(run, lambda record: record["steps"]["CP-0"].update(status="running", attempts=1))
    before = (run / state.STATE).read_bytes()
    assert accept(run) == 1 and (run / state.STATE).read_bytes() == before
    assert not (run / "validate").exists()


def test_malformed_retry_survives_resends_and_duplicate_accept(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    own.write_text("DONE 0")
    assert accept(run) == 2
    first = (run / "validate/CP-0.json").read_bytes()
    before = (run / state.STATE).read_bytes()
    assert accept(run) == 2 and (run / state.STATE).read_bytes() == before
    assert (run / "validate/CP-0.json").read_bytes() == first
    send(run, RBOT_ROOT, name="fixture-retry", retry=True)
    send(run, RBOT_ROOT, name="fixture-retry-interrupted", retry=True)
    assert state.read(run)["steps"]["CP-0"]["attempts"] == 2
    assert accept(run) == 2
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "failed" and step["validate_exit"] == 2
    events = attempts.read_history(run, "CP-0", step)
    assert [e["slot"] for e in events] == [1, 1, 2, 2, 2]
    assert events[1]["result"] == json.loads(first)
    assert accept(run) == 2
    with pytest.raises(ValueError, match="pending/running"):
        send(run, RBOT_ROOT, name="third")


@pytest.mark.parametrize(
    "field,value", [("module_id", "CP-1"), ("run_id", "wrong-run"), ("issuer_id", "WRONG")]
)
def test_wrong_identity_fails_immediately_even_with_claimed_done(
    tmp_path: Path, field: str, value: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    text = own.read_text()
    old = next(line for line in text.splitlines() if line.startswith(field + ":"))
    own.write_text(text.replace(old, f"{field}: {value}") + "\nDONE 0\n")
    assert accept(run) == 4
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "failed" and step["attempts"] == 1
    assert step["sha256"] == hashlib.sha256(own.read_bytes()).hexdigest()


@pytest.mark.parametrize("missing", [True, False])
def test_io_one_is_terminal_and_missing_has_no_invented_hash(tmp_path: Path, missing: bool) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    own = run / "handoffs/CP-0.md"
    if missing:
        own.unlink()
    else:
        own.write_bytes(b"\xff")
    assert accept(run) == 1
    step = state.read(run)["steps"]["CP-0"]
    assert step["status"] == "failed" and "CP-0.md" in step["reason"]
    result = json.loads((run / "validate/CP-0.json").read_text())
    assert result["exit"] == 1
    assert result["sha256"] == (None if missing else hashlib.sha256(b"\xff").hexdigest())
    assert (run / state.LOCK).exists()


def test_terminal_edit_refuses_without_erasing_validation(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    own = run / "handoffs/CP-0.md"
    own.write_bytes(own.read_bytes() + b"\nchanged")
    before = (run / state.STATE).read_bytes(), (run / "validate/CP-0.json").read_bytes()
    assert accept(run) == 1
    assert before == ((run / state.STATE).read_bytes(), (run / "validate/CP-0.json").read_bytes())


@pytest.mark.parametrize("target", ["MODEL", "CP-DR", "CP-8", "CP-1", "../CP-0"])
def test_unsupported_or_unplanned_accept_is_preflight_refusal(tmp_path: Path, target: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    before = (run / state.STATE).read_bytes()
    assert accept(run, module=target) == 1
    assert (run / state.STATE).read_bytes() == before and not (run / "validate").exists()
