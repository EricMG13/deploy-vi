"""Public host validation proves actual checked origin and current complete shapes."""

from __future__ import annotations

from pathlib import Path

import pytest
from state_receipt_assertions import outcome_bytes
from test_host_fit import fit_run

from rbotlib import cli, dispatch, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


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

    if module == "RUN_BRIEF":
        with pytest.raises(RunError, match="approved origin"):
            state.update(run, forge)
    else:
        state.update(run, forge)
    assert cli.main(command) == 1
    assert cli.main(["validate", str(path), "--module", module]) == 1


def test_brief_header_origin_is_required_even_with_current_fingerprint(tmp_path: Path) -> None:
    run = fit_run(tmp_path)
    path = run / "run-brief.md"
    text = path.read_text()
    path.write_text(text.replace("| ACME | 2026-10-02 |", "| OTHER | 2026-10-02 |", 1))
    assert path.read_text() != text
    with pytest.raises(RunError, match="approved origin"):
        state.update(run, lambda record: record.update(run_brief_sha256=dispatch._sha(path)))
    assert cli.main(["validate", str(path), "--module", "RUN_BRIEF", "--run", str(run)]) == 1


@pytest.mark.parametrize(
    "location, field, value",
    [
        ("step", "host_exit", False),
        ("invocation", "exit", False),
        ("receipt", "code", False),
        ("receipt", "code", 0.0),
        ("receipt", "row", ""),
        ("receipt", "prefix_size", False),
        ("receipt", "prefix_size", 0.0),
        ("execution", "invocations", [[]]),
        ("invocation", "receipt", []),
        ("step", "host_execution", []),
        ("receipt", "invocation", "f" * 32),
        ("receipt", "binding", False),
        ("receipt", "prefix_sha256", False),
        ("invocation", "id", False),
        ("invocation", "completion", False),
        ("invocation", "finished_at", False),
        ("execution", "schema", False),
        ("execution", "origin", False),
        ("execution", "token", False),
        ("execution", "generated_at", False),
        ("step", "attempts", True),
    ],
)
def test_corrupt_receipt_refuses_public_validation(
    tmp_path: Path, location: str, field: str, value: object
) -> None:
    import hashlib
    import json

    from test_model_host import eligible

    from rbotlib import host_evidence

    run = eligible(tmp_path, RBOT_ROOT)
    assert cli.main(["model", "--run", str(run)]) == 0
    command = ["validate", str(run / "handoffs/MODEL.md"), "--module", "MODEL", "--run", str(run)]
    assert cli.main(command) == 0
    record = state.read(run)
    step = record["steps"]["MODEL"]
    execution = step["host_execution"]
    invocation = execution["invocations"][-1]
    receipt = invocation["receipt"]
    if field == "row":
        receipt["prefix_size"] += len(bytes.fromhex(receipt["row"]))
        receipt["prefix_sha256"] = hashlib.sha256(
            (run / "log/rbot.log").read_bytes()[: receipt["prefix_size"]]
        ).hexdigest()
    {"step": step, "execution": execution, "invocation": invocation, "receipt": receipt}[location][
        field
    ] = value
    if location == "receipt" and field != "binding":
        receipt["binding"] = host_evidence.digest(
            {k: v for k, v in receipt.items() if k != "binding"}
        )
    if location == "execution" and field != "invocations":
        execution["binding"] = host_evidence.binding(execution)
    (run / state.STATE).write_text(json.dumps(record))
    before = outcome_bytes(run)
    assert cli.main(command) == 1
    assert outcome_bytes(run) == before
