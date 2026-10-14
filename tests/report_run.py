"""A complete native run driven from the fixture Handoffs (Plan 07; corpus-marked callers).

Every step goes through the real native commands: `new-run`, `inventory`, `prepare`, `send`
and `accept` of the fixture bytes, `brief`/`grade`/`approve`, then `next` until it reports
`done`. The Handoffs are hand-written fixtures, never live model evidence.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from test_accept import accept, send
from test_bootstrap import ready

from rbotlib import next as next_step
from rbotlib import state
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT

FIXTURES = Path(__file__).parent / "fixtures/handoffs"
PACK = "czr-2026q2-primary"


def fixture_text(module: str, run: Path) -> str:
    """The module's fixture Handoff with its `run_id` rewritten to `run`."""
    lines = (FIXTURES / f"{module}.md").read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(f"run_id: {run.name}\n" if x.startswith("run_id: ") else x for x in lines)


def _approve(run: Path, primary: bool) -> Path:
    args = ["--root", str(RBOT_ROOT), "approve", "--run", str(run)]
    args += ["--pathway", "FULL_CREDIT_ASSESSMENT", "--depth", "full"]
    args += ["--primary", "yes" if primary else "no", "--analyst", "Approver"]
    assert main(args) == 0
    return next(run.parent.iterdir())


def complete_run(
    corpus_pack: Callable[[str], Path],
    tmp_path: Path,
    *,
    primary: bool = True,
    fail: str | None = None,
) -> Path:
    """A finished run of the czr synthetic pack; `fail` sets that pending step failed."""
    pack = shutil.copytree(corpus_pack(PACK), tmp_path / "working pack")
    assert main(["new-run", "--pack", str(pack)]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    (run / "handoffs").mkdir()
    (run / "handoffs/CP-0.md").write_text(fixture_text("CP-0", run), encoding="utf-8")
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    run = _approve(run, primary)
    for _ in range(len(state.read(run)["plan"]) + 1):
        chosen = next_step.select(run, RBOT_ROOT)
        step = chosen["step"]
        if chosen["kind"] == "done":
            return run
        if step == fail:
            state_args = ["state", "--run", str(run), "--set", f"{step}=failed", "--reason"]
            assert main([*state_args, "fixture failure"]) == 0
        elif chosen["kind"] == "host":
            assert main([step.lower(), "--run", str(run)]) == 0
        else:
            (run / f"handoffs/{step}.md").write_text(fixture_text(step, run), encoding="utf-8")
            send(run, RBOT_ROOT, step)
            code = accept(run, module=step)
            assert code in (0, 3), f"{step}: acceptance exit {code}"
    raise AssertionError("the run did not reach done")
