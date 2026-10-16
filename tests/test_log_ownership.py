"""A replaced log fence cannot grant a managed command publication authority."""

from pathlib import Path

import pytest
from test_model_completion import invoke
from test_model_host import eligible

from rbotlib import cli, runlog, state
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("phase", ["before", "after"])
def test_replaced_log_owner_refuses_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    logger = cli._log

    def replaced(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        assert receipt is not None and code == 0
        if phase == "after":
            logger(selected, argv, code, receipt=receipt)
        lock = run / runlog.LOCK
        lock.rename(run / "displaced-log-owner")
        lock.write_bytes((run / "displaced-log-owner").read_bytes())
        if phase == "before":
            logger(selected, argv, code, receipt=receipt)

    monkeypatch.setattr(cli, "_log", replaced)
    assert invoke(run) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed" and "identity" in current["reason"]
    raw = (run / "log/rbot.log").read_bytes()
    if phase == "before":
        assert raw == prefix
    else:
        assert raw.startswith(prefix) and raw.endswith(b"\t0\n")
        assert current["completion_failure"]["log_state"] == "row0"
