"""Envelope support is consistency evidence; it never qualifies a Module itself."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from test_bootstrap import pending

from rbotlib import origins
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("artifact", ["CP-0", "RUN_BRIEF"])
def test_exact_utf8_canonical_roundtrip(tmp_path: Path, artifact: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    raw = (run / "handoffs/CP-0.md").read_bytes()
    raw = raw.replace(b"module_id: CP-0", f"module_id: {artifact}".encode())
    envelope = origins.capture(raw, artifact, "approval")
    assert origins.decoded(envelope, artifact) == raw
    assert envelope["history"] is None
    assert envelope["run_id"] == run.name


@pytest.mark.parametrize(
    "field,value",
    [
        ("size", True),
        ("size", 98305),
        ("size", 0),
        ("bytes", "???"),
        ("sha256", "0" * 64),
        ("basis", "backdated"),
        ("at", "yesterday"),
        ("issuer_id", "FORGED"),
        ("path", "../CP-0.md"),
        ("history", {}),
    ],
)
def test_untrusted_envelope_is_refused(tmp_path: Path, field: str, value: object) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    raw = (run / "handoffs/CP-0.md").read_bytes()
    envelope = origins.capture(raw, "CP-0", "completion")
    candidate = copy.deepcopy(envelope)
    candidate[field] = value
    with pytest.raises(RunError, match="origin"):
        origins.decoded(candidate, "CP-0")
    assert origins.decoded(envelope, "CP-0") == raw
