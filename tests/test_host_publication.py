"""Direct publishers must respect a genuine active MODEL owner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
from host_process import finish, start
from test_host_fit import fit_run
from test_model_host import eligible

from rbotlib import fit, grade, inventory, prepare, runlog, state
from rbotlib.model import run as writer
from rbotlib.rules import RBOT_ROOT, load_rules


def publish(run: Path, publisher: str) -> None:
    if publisher == "inventory":
        inventory.write(run)
    elif publisher == "prepare":
        prepare.write(run, load_rules(RBOT_ROOT))
    elif publisher == "prepare-file":
        record = json.loads((run / "inventory.json").read_text())
        prepare.prepare_file(run, Path(record["pack_root"]), record["files"][0])
    elif publisher == "model":
        writer.run_model(run, "2026-10-13T00:00:00+00:00")
    elif publisher == "fit":
        fit.run_fit(run, RBOT_ROOT)
    elif publisher == "fit-set":
        fit._write_all(run, {}, "foreign output")
    else:
        runlog.append(run, ["ordinary contender"], 0)


@pytest.mark.parametrize(
    "publisher", ["inventory", "prepare", "prepare-file", "grade", "model", "fit", "fit-set", "log"]
)
@pytest.mark.parametrize("kind", ["model", "fit"])
def test_direct_publisher_cannot_change_active_host(
    tmp_path: Path, publisher: str, kind: str, capsys: pytest.CaptureFixture[str]
) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    process = start(run, kind, "build")
    before = {str(p.relative_to(run)): p.read_bytes() for p in run.rglob("*") if p.is_file()}
    try:
        if publisher == "grade":
            capsys.readouterr()
            assert grade.run_command(argparse.Namespace(run_dir=run, root=RBOT_ROOT)) == 1
            assert "holds" in capsys.readouterr().out
        else:
            with pytest.raises(ValueError, match="holds"):
                publish(run, publisher)

        after = {str(p.relative_to(run)): p.read_bytes() for p in run.rglob("*") if p.is_file()}
        assert after == before
        assert process.stdin is not None
        process.stdin.write("continue\n")
        process.stdin.flush()
        stdout, stderr = process.communicate(timeout=20)
        assert process.returncode == 0, stderr
        assert "BUILT" in stdout and state.read(run)["steps"][kind.upper()]["status"] == "accepted"
    finally:
        finish(process)
