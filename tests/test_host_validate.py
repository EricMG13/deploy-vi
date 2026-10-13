"""Public host validation proves actual checked origin and current complete shapes."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_host_fit import fit_run

from rbotlib import cli, dispatch, state


@pytest.mark.parametrize("module", ["MODEL", "FIT", "RUN_BRIEF"])
def test_actual_host_validate_and_forged_shape_refusal(tmp_path: Path, module: str) -> None:
    run = fit_run(tmp_path)
    assert cli.main(["fit", "--run", str(run)]) == 0
    path = run / ("run-brief.md" if module == "RUN_BRIEF" else f"handoffs/{module}.md")
    command = ["validate", str(path), "--module", module, "--run", str(run)]
    assert cli.main(command) == 0
    original = path.read_bytes()
    path.write_bytes(original.replace(b"## Tables", b"## Wrong"))

    def forge(record: state.Record) -> None:
        if module == "RUN_BRIEF":
            record["run_brief_sha256"] = dispatch._sha(path)
        else:
            current = record["steps"][module]
            current["sha256"] = dispatch._sha(path)
            current["outputs"][str(path.relative_to(run))] = current["sha256"]

    state.update(run, forge)
    assert cli.main(command) == 1
    assert cli.main(["validate", str(path), "--module", module]) == 1


def test_brief_header_origin_is_required_even_with_current_fingerprint(tmp_path: Path) -> None:
    run = fit_run(tmp_path)
    path = run / "run-brief.md"
    text = path.read_text()
    path.write_text(text.replace("| ACME | 2026-10-02 |", "| OTHER | 2026-10-02 |", 1))
    assert path.read_text() != text
    state.update(run, lambda record: record.update(run_brief_sha256=dispatch._sha(path)))
    assert cli.main(["validate", str(path), "--module", "RUN_BRIEF", "--run", str(run)]) == 1
