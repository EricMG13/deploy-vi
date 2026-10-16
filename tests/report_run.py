"""A complete native run driven from the fixture Handoffs (Plan 07; corpus-marked callers).

Every step goes through the real native commands: `new-run`, `inventory`, `prepare`, `send`
and `accept` of the fixture bytes, `brief`/`grade`/`approve`, then `next` until it reports
`done`. The Handoffs are hand-written fixtures, never live model evidence.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import proxy_isolated
from test_accept import accept, send
from test_bootstrap import ready

from rbotlib import next as next_step
from rbotlib import state
from rbotlib.cli import main
from rbotlib.rules import RBOT_ROOT

PACK = "czr-2026q2-primary"


@dataclass(frozen=True)
class RunShape:
    """The depth a run is approved at, and whether its pack holds a Portfolio Context."""

    depth: str = "full"
    portfolios: bool = True


FULL = RunShape()


def fixture_text(module: str, run: Path, depth: str = "full") -> str:
    """The module's fixture Handoff at `depth` with its `run_id` rewritten to `run`."""
    path = proxy_isolated.fixture_path(module, depth)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(f"run_id: {run.name}\n" if x.startswith("run_id: ") else x for x in lines)


def _approve(run: Path, primary: bool, depth: str) -> Path:
    args = ["--root", str(RBOT_ROOT), "approve", "--run", str(run)]
    args += ["--pathway", "FULL_CREDIT_ASSESSMENT", "--depth", depth]
    args += ["--primary", "yes" if primary else "no", "--analyst", "Approver"]
    assert main(args) == 0
    return next(run.parent.iterdir())


def complete_run(
    corpus_pack: Callable[[str], Path],
    tmp_path: Path,
    *,
    primary: bool = True,
    fail: str | None = None,
    shape: RunShape = FULL,
) -> Path:
    """A finished run of the czr synthetic pack; `fail` sets that pending step failed."""
    depth, portfolios = shape.depth, shape.portfolios
    pack = shutil.copytree(
        corpus_pack(PACK), tmp_path / "working pack", ignore=shutil.ignore_patterns("rbot-runs")
    )
    if not portfolios:
        for held in pack.rglob("*TEST_CLO_I*"):
            held.unlink()
    assert main(["new-run", "--pack", str(pack)]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    (run / "handoffs").mkdir()
    read = fixture_text if depth == "full" else partial(fixture_text, depth=depth)
    cp0 = read("CP-0", run)
    if not portfolios:  # no Portfolio Context in the pack or in CP-0: FIT is skipped
        kept = [x for x in cp0.splitlines(keepends=True) if "TEST_CLO_I" not in x[:60]]
        cp0 = re.sub(r" ?\[C1[67]\]", "", "".join(kept))
    (run / "handoffs/CP-0.md").write_text(cp0, encoding="utf-8")
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    run = _approve(run, primary, depth)
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
            (run / f"handoffs/{step}.md").write_text(read(step, run), encoding="utf-8")
            send(run, RBOT_ROOT, step)
            code = accept(run, module=step)
            assert code in (0, 3), f"{step}: acceptance exit {code}"
    raise AssertionError("the run did not reach done")
