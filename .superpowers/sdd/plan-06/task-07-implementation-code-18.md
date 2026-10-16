# Task06.7 exact replay file 18

Source: `tests/test_runlog.py`; complete executed bytes, SHA256 `a8d8115c24723d82532acfc73ecf6a7dd094085eb7e9ed08fa709d1461a07d3b`, 2070 bytes, 62 LF. Baseline1094a76; final source tree/proof is recorded separately. This ordinary whole file receives no cap exemption.

```python
"""Owned row correction preserves every preceding byte and refuses unowned edits."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_next import approved

from rbotlib import cli, runlog, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("suffix", ["missing", "partial", "full"])
def test_owned_receipt_correction_preserves_bytes_and_cardinality(
    tmp_path: Path, suffix: str
) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    path = run / "log/rbot.log"
    prefix = path.read_bytes() + b"uninterpreted prior bytes\xff\r\n"
    path.write_bytes(prefix)
    receipt = runlog.Receipt(run, ["model", "quoted ' argument\n"])
    try:
        if suffix == "partial":
            with path.open("ab") as stream:
                stream.write(receipt.row[:25])
        elif suffix == "full":
            cli._log(run, ["model"], 0, receipt=receipt)
        receipt.fail()
        assert path.read_bytes() == prefix + receipt.row + b"1\n"
    finally:
        receipt.close()


@pytest.mark.parametrize("change", ["prefix", "suffix"])
def test_receipt_refuses_unowned_correction(tmp_path: Path, change: str) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    path = run / "log/rbot.log"
    receipt = runlog.Receipt(run, ["model"])
    try:
        raw = (b"other prefix" if change == "prefix" else receipt.prefix) + b"someone else\n"
        path.write_bytes(raw)
        with pytest.raises(RunError, match="correction refused"):
            receipt.fail()
        assert path.read_bytes() == raw
    finally:
        receipt.close()


def test_state_owned_stage_is_serialized_before_publication_and_cleanup_is_separate(
    tmp_path: Path,
) -> None:
    run = approved(tmp_path, RBOT_ROOT)
    owner = state._Locked(run)
    record = state.read(run)
    record["extension"] = "staged"
    staged = owner.stage(record)
    record["extension"] = "later mutation"
    owner.commit(staged)
    assert state.read(run)["extension"] == "staged"
    assert owner.close() == []
```

Not verified: independent acceptance, whole06.16 branch gates, later06, live/provider/platform/crash behavior.
