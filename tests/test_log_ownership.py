"""A replaced log fence cannot grant a managed command publication authority."""

from pathlib import Path

import pytest
from test_model_completion import invoke
from test_model_host import eligible

from rbotlib import cli, runlog, state
from rbotlib.rules import RBOT_ROOT


def test_replaced_log_owner_refuses_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    prefix = (run / "log/rbot.log").read_bytes()
    logger = cli._log

    def replaced(
        selected: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None
    ) -> None:
        assert receipt is not None and code == 0
        lock = run / runlog.LOCK
        lock.rename(run / "displaced-log-owner")
        lock.write_bytes((run / "displaced-log-owner").read_bytes())
        logger(selected, argv, code, receipt=receipt)

    monkeypatch.setattr(cli, "_log", replaced)
    assert invoke(run) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed" and "identity" in current["reason"]
    assert (run / "log/rbot.log").read_bytes() == prefix
