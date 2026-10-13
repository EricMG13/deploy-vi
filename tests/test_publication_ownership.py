"""Shared writers recheck their held owner after computing and before publication."""

from collections.abc import Callable
from pathlib import Path

import pytest
from test_bootstrap import pending, ready
from test_legacy_ownership import snapshot

from rbotlib import approve, dispatch, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, load_rules


@pytest.mark.parametrize("kind", ["Approval", "dispatch"])
def test_replaced_owner_refuses_before_shared_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    if kind == "Approval":
        ready(run, RBOT_ROOT)
    before = snapshot(run)
    lock = run / state.LOCK
    original: Callable[..., object] = (
        approve.prepare if kind == "Approval" else dispatch.qualified_message
    )

    def replaced(*args: object, **kwargs: object) -> object:
        result = original(*args, **kwargs)
        lock.rename(run / "original-owner")
        lock.write_bytes((run / "original-owner").read_bytes())
        return result

    monkeypatch.setattr(
        approve if kind == "Approval" else dispatch,
        "prepare" if kind == "Approval" else "qualified_message",
        replaced,
    )
    with pytest.raises((RunError, approve.ApprovalError), match="identity"):
        if kind == "Approval":
            approve.approve(
                run,
                RBOT_ROOT,
                load_rules(RBOT_ROOT),
                approve.Choice(
                    "FULL_CREDIT_ASSESSMENT", "full", False, "Approver", False, (), False, False
                ),
            )
        else:
            dispatch.prepare_message(run, RBOT_ROOT, "CP-0")
    assert run.exists()
    after = snapshot(run)
    after.pop("original-owner")
    assert after == before
