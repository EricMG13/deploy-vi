"""Actual native CP8 lifecycle with fixture reports; no live worker qualification."""

from __future__ import annotations

import copy
import hashlib
import json
import shlex
from pathlib import Path

import proxy_continue
import proxy_isolated
import pytest
from test_diff_cli import pair, publish
from test_next import blocked
from test_prior_approval import snapshot
from test_prior_context import native as native

from rbotlib import accept, attempts, current, dispatch, resume, state
from rbotlib import next as next_step
from rbotlib.inventory import RunError


def grants(text: str) -> list[dict[str, str]]:
    value: list[dict[str, str]] = json.loads(
        next(
            s.split(": ", 1)[1]
            for s in text.splitlines()
            if s.startswith("Qualified prior artifacts (read-only): ")
        )
    )
    return value


def receipt(run: Path, text: str, name: str = "fixture-cp8") -> attempts.DispatchReceipt:
    return attempts.DispatchReceipt(
        name, "fixture-controller", hashlib.sha256(text.encode()).hexdigest()
    )


def test_missing_pair_refuses_direct_selection_and_dispatch(native: tuple[Path, Path]) -> None:
    run, root = native
    before = snapshot(run)
    command = shlex.join(["rbot", "diff", "--run", str(run), "--prior", "prior.html"])
    for call in (
        lambda: next_step.select(run, root),
        lambda: dispatch.prepare_message(run, root, "CP-8"),
    ):
        with pytest.raises(RunError, match="Prior comparison unavailable") as stop:
            call()
        assert command in str(stop.value)
        assert snapshot(run) == before
    assert not (run / "prior").exists()


def test_exact_read_only_grants_and_actual_receipt_accept(native: tuple[Path, Path]) -> None:
    run, root = native
    assert publish(run, root) == 0
    before = pair(run)
    selected = next_step.select(run, root)
    assert selected["step"] == "CP-8" and selected["kind"] == "module"
    text = (run / selected["dispatch"]).read_text()
    expected = [run.parent.parent / "prior.html", run / "prior/diff.json", run / "prior/diff.md"]
    assert grants(text) == [
        dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in expected
    ]
    assert "May write only: " + json.dumps([str(run / "handoffs/CP-8.md")]) in text
    assert "No fetching is authorized" in text
    saved = snapshot(run)
    with state.publication(run) as checked:
        assert dispatch.qualified_message(run, root, "CP-8", state.read(run)) == text
        checked()
    assert snapshot(run) == saved
    event = attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
    assert event["message"] == text and state.read(run)["steps"]["CP-8"]["attempts"] == 1
    blocked(run, root, "CP-8")
    assert state.read(run)["steps"]["CP-8"]["status"] == "blocked"
    assert pair(run) == before
    state.update(run, lambda r: r.update(volatile_counter=42))
    with (run / "log/rbot.log").open("ab") as stream:
        stream.write(b"unrelated later row\n")
    assert grants(dispatch.qualified_message(run, root, "CP-8", state.read(run))) == grants(text)


@pytest.mark.parametrize("phase", ["prepare", "send", "accept"])
@pytest.mark.parametrize("damage", ["json", "md", "missing", "prior", "current", "source"])
def test_changed_inputs_refuse_without_erasing_evidence(
    native: tuple[Path, Path], phase: str, damage: str
) -> None:
    run, root = native
    assert publish(run, root) == 0
    text = dispatch.prepare_message(run, root, "CP-8")
    if phase == "accept":
        attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
    paths = {
        "json": run / "prior/diff.json",
        "md": run / "prior/diff.md",
        "missing": run / "prior/diff.md",
        "prior": run.parent.parent / "prior.html",
        "current": run / "handoffs/CP-1C.md",
        "source": run.parent.parent / "acme_10k.txt",
    }
    target = paths[damage]
    if damage == "missing":
        target.unlink()
    else:
        target.write_bytes(target.read_bytes() + b"\nchanged\n")
    before = snapshot(run)
    cp8 = state.read(run)["steps"]["CP-8"]
    with pytest.raises(RunError):
        if phase == "prepare":
            dispatch.prepare_message(run, root, "CP-8")
        elif phase == "send":
            attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
        else:
            accept.accept(run, root, "CP-8")
    after = snapshot(run)
    assert state.read(run)["steps"]["CP-8"] == cp8
    if damage == "current":
        before.pop(state.STATE)
        after.pop(state.STATE)  # current owner registers the real predecessor edit
    assert after == before


def test_caller_record_must_equal_owned_state(native: tuple[Path, Path]) -> None:
    run, root = native
    assert publish(run, root) == 0
    stale = copy.deepcopy(state.read(run))
    stale["volatile_counter"] = 123
    with state.publication(run), pytest.raises(RunError, match="caller state differs"):
        dispatch.qualified_message(run, root, "CP-8", stale)


def test_controller_diff_before_first_selection_and_read_only_reuse(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    run, root = native
    monkeypatch.setattr(proxy_continue, "RBOT_ROOT", root)
    commands: list[str] = []

    def native_call(run: Path, command: str, flags: list[str] | None) -> str:
        commands.append(command)
        if command == "diff":
            assert flags == ["--prior", state.read(run)["prior_case"]["report"]]
            assert publish(run, root) == 0
            return ""
        return json.dumps(next_step.select(run, root))

    proxy_continue.advance(run, None, native_call)
    assert commands == ["diff", "next"]
    original = pair(run)
    commands.clear()
    proxy_continue.advance(run, None, native_call)
    assert commands == ["next"] and pair(run) == original


@pytest.mark.parametrize("damage", ["stale", "missing-after-selection", "mixed"])
def test_controller_never_rewrites_selected_or_incomplete_pair(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    run, root = native
    monkeypatch.setattr(proxy_continue, "RBOT_ROOT", root)
    assert publish(run, root) == 0
    next_step.select(run, root)
    if damage == "missing-after-selection":
        for name in ("json", "md"):
            (run / f"prior/diff.{name}").unlink()
    elif damage == "mixed":
        (run / "prior/diff.md").unlink()
    else:
        target = run / "prior/diff.json"
        target.write_bytes(target.read_bytes() + b" ")
    before = snapshot(run)

    def forbidden(run: Path, command: str, flags: list[str] | None) -> str:
        pytest.fail(f"native {command} must not rewrite/refetch/transport")

    with pytest.raises(RunError, match="regenerate with rbot diff"):
        proxy_continue.advance(run, None, forbidden)
    assert snapshot(run) == before


def test_isolated_cp8_refuses_before_dependency_or_source_reads() -> None:
    with pytest.raises(ValueError, match="actual approved prior"):
        proxy_isolated.plan_dependencies("CP-8", "anything", "full")


@pytest.mark.parametrize("action", ["dispatch", "accept"])
@pytest.mark.parametrize("phase", ["intent", "event"])
def test_interrupted_prospective_publication_recovers_actual_owned_record(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, action: str, phase: str
) -> None:
    run, root = native
    assert publish(run, root) == 0
    text = dispatch.prepare_message(run, root, "CP-8")
    if action == "accept":
        attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
        (run / "handoffs/CP-8.md").write_text("DONE 2")
    original = resume._evidence

    def interrupt(run: Path, module: str, events: list[state.Record], event: state.Record) -> None:
        if phase == "event":
            original(run, module, events, event)
        raise OSError("fixture interruption after checked prospective intent")

    with monkeypatch.context() as patch:
        patch.setattr(resume, "_evidence", interrupt)
        with pytest.raises(OSError, match="fixture interruption"):
            if action == "dispatch":
                attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
            else:
                accept.accept(run, root, "CP-8")
    intent = state.read(run)[resume.KEY]
    before = pair(run)
    owner = state._Locked(run)
    try:
        with pytest.raises(RunError, match="busy"):
            current.reconcile(run, root)
        resume.recover(owner, root)
    finally:
        assert owner.close() == []
    assert resume.KEY not in state.read(run) and pair(run) == before
    step = state.read(run)["steps"]["CP-8"]
    assert step == intent["after"] and step["attempts"] == 1
    assert attempts.read_history(run, "CP-8", step)[-1] == intent["event"]


@pytest.mark.parametrize("damage", ["json", "md", "prior"])
def test_resume_readback_rejects_substitution_after_validation(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    run, root = native
    assert publish(run, root) == 0
    text = dispatch.prepare_message(run, root, "CP-8")
    attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
    (run / "handoffs/CP-8.md").write_text("DONE 2")
    original = resume._evidence

    def substitute(run: Path, module: str, events: list[state.Record], event: state.Record) -> None:
        original(run, module, events, event)
        path = (
            run.parent.parent / "prior.html" if damage == "prior" else run / f"prior/diff.{damage}"
        )
        path.write_bytes(path.read_bytes() + b" ")

    with monkeypatch.context() as patch:
        patch.setattr(resume, "_evidence", substitute)
        with pytest.raises(RunError):
            accept.accept(run, root, "CP-8")
    before = snapshot(run)
    with pytest.raises(RunError):
        current.reconcile(run, root)
    assert snapshot(run) == before
    assert state.read(run)["steps"]["CP-8"]["attempts"] == 1
    assert len(state.read(run)["steps"]["CP-8"]["accept_history"]) == 1


@pytest.mark.parametrize("name", ["diff.json", "diff.md"])
@pytest.mark.parametrize("link", ["symlink", "hardlink"])
def test_linked_pair_never_granted(
    native: tuple[Path, Path], tmp_path: Path, name: str, link: str
) -> None:
    run, root = native
    assert publish(run, root) == 0
    target, foreign = run / "prior" / name, tmp_path / "foreign"
    foreign.write_bytes(target.read_bytes())
    target.unlink()
    if link == "symlink":
        target.symlink_to(foreign)
    else:
        target.hardlink_to(foreign)
    saved = foreign.read_bytes()
    with pytest.raises(RunError):
        dispatch.prepare_message(run, root, "CP-8")
    assert foreign.read_bytes() == saved


@pytest.mark.parametrize("choice", ["declined", "absent", "unapproved"])
def test_no_prior_authorization_never_grants_or_writes(tmp_path: Path, choice: str) -> None:
    from test_approve import TARGET, _approve
    from test_prior_approval import doc, ready

    from rbotlib.rules import RBOT_ROOT

    run = ready(RBOT_ROOT, tmp_path, {} if choice == "absent" else {"prior.html": doc()})
    if choice != "unapproved":
        assert _approve(RBOT_ROOT, run, "--prior-case", "no") == 0
        run = run.parent / TARGET
    before = snapshot(run)
    with pytest.raises(RunError, match="accepted offered Prior Case"):
        dispatch.qualified_message(run, RBOT_ROOT, "CP-8", state.read(run))
    assert snapshot(run) == before and not (run / "prior").exists()


def test_retry_reuses_binding_and_preserves_native_findings(native: tuple[Path, Path]) -> None:
    run, root = native
    assert publish(run, root) == 0
    text = dispatch.prepare_message(run, root, "CP-8")
    attempts.register_dispatch(run, root, "CP-8", receipt(run, text))
    (run / "handoffs/CP-8.md").write_text("DONE 2")
    assert accept.accept(run, root, "CP-8")["exit"] == 2
    before = pair(run)
    next_step.select(run, root)
    retry = (run / "dispatch/CP-8.md").read_text()
    assert grants(retry) == grants(text) and '"exit": 2' in retry
    attempts.register_dispatch(run, root, "CP-8", receipt(run, retry, "fixture-retry"))
    (run / "handoffs/CP-8.md").write_text(
        f"---\nmodule_id: CP-8\nrun_id: {run.name}\nissuer_id: ACME\n"
        "analysis_date: 2026-10-02\nqa_status: Blocked\ninputs: CP-0\n---\n\n"
        "## Analysis\nFixture gap.\n\n## Tables\n\n## Gaps\nFixture gap.\n\n"
        "## Citations\n<!-- table: citations -->\n"
        "| id | source | locator | excerpt |\n|---|---|---|---|\n"
    )
    assert accept.accept(run, root, "CP-8")["exit"] == 3
    final = state.read(run)["steps"]["CP-8"]
    assert final["attempts"] == 2 and final["status"] == "blocked" and pair(run) == before


def test_controller_keeps_native_age_guard_before_diff(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, timedelta

    from rbotlib import runs

    run, _ = native
    point = datetime.fromisoformat(state.read(run)["created_at"]) + timedelta(days=31)
    monkeypatch.setattr(runs, "_clock", lambda now: point)
    before = snapshot(run)

    def forbidden(run: Path, command: str, flags: list[str] | None) -> str:
        pytest.fail(f"ineligible run reached {command}")

    with pytest.raises(RunError, match="30 days"):
        proxy_continue.advance(run, None, forbidden)
    assert snapshot(run) == before


def test_digest_collection_rechecks_canonical_bytes_before_grant(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    run, root = native
    assert publish(run, root) == 0
    original = dispatch._sha

    def substitute(path: Path) -> str:
        digest = original(path)
        if path == run / "prior/diff.md":
            path.write_bytes(path.read_bytes() + b" ")
        return digest

    monkeypatch.setattr(dispatch, "_sha", substitute)
    with pytest.raises(RunError, match="canonical bytes differ"):
        dispatch.prepare_message(run, root, "CP-8")
    assert not (run / "dispatch/CP-8.md").exists()


def test_controller_reconciles_dependency_failures_before_first_cp8_selection(
    native: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from test_approve import TARGET, _approve
    from test_prior_approval import doc, ready

    _, root = native
    folder = tmp_path / "failure"
    folder.mkdir()
    run = ready(root, folder, {"prior.html": doc()})
    assert _approve(root, run, "--prior-case", "yes") == 0
    run = run.parent / TARGET
    for name, status in (("CP-1", "failed"), ("CP-1A", "skipped"), ("CP-5", "skipped")):
        state.set_status(run, name, status, "explicit fixture unavailable producer")
    monkeypatch.setattr(proxy_continue, "RBOT_ROOT", root)
    commands: list[str] = []

    def native_call(run: Path, command: str, flags: list[str] | None) -> str:
        commands.append(command)
        if command == "diff":
            assert publish(run, root) == 0
            return ""
        return json.dumps(next_step.select(run, root))

    proxy_continue.advance(run, None, native_call)
    assert commands == ["diff", "next"]
    assert state.read(run)["steps"]["CP-8"]["status"] == "pending"


def test_controller_source_refusal_precedes_diff_writes(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    run, root = native
    monkeypatch.setattr(proxy_continue, "RBOT_ROOT", root)
    (run.parent.parent / "acme_10k.txt").write_text("changed source")
    before = snapshot(run)

    def forbidden(run: Path, command: str, flags: list[str] | None) -> str:
        pytest.fail(f"changed source reached {command}")

    with pytest.raises(RunError, match="source sha256 changed"):
        proxy_continue.advance(run, None, forbidden)
    assert snapshot(run) == before and not (run / "prior").exists()
