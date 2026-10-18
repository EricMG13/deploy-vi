"""CP1C method/contract seam; numerical records below are test-only, never corpus evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from test_modules import contract, fixture

from rbotlib.calc import peer_statistics
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check


def synthetic_input() -> dict[str, Any]:
    return {
        "metric_id": "net_leverage",
        "unit_label": "x",
        "borrower_value": "5",
        "period": "FY2025",
        "currency": None,
        "definition_note": "TEST-ONLY aligned definition",
        "cite": "TEST-ONLY; no supplied-source provenance",
        "peers": [
            {
                "peer": f"TEST-{i}",
                "value": str(i),
                "comparability": "Close",
                "calculation_status": "Reported",
                "period": "FY2025",
                "currency": None,
                "definition_note": "TEST-ONLY aligned definition",
                "outlier": i == 4,
                "outlier_reason": "TEST-ONLY sensitivity",
                "age_months": "6",
                "cite": "TEST-ONLY; no supplied-source provenance",
            }
            for i in range(1, 5)
        ],
    }


def positive_handoff(result: dict[str, Any], rules: Rules) -> str:
    """A hand-computed four-peer numerical witness, not an accepted real-source Handoff."""
    text = fixture("CP-1C").replace("qa_status: Blocked", "qa_status: Restricted")
    start = text.index("<!-- table: cp1c.peer_set -->")
    end = text.index("## Gaps")
    lines = []
    for table in contract("CP-1C", rules).tables:
        names = [c.name for c in table.columns]
        lines += [
            f"<!-- table: {table.id} -->",
            "| " + " | ".join(names) + " |",
            "|" + "---|" * len(names),
        ]
        if table.id == "cp1c.peer_set":
            rows = [
                {
                    "peer": f"TEST-{i}",
                    "selection_basis": "TEST-ONLY",
                    "comparability": "Close",
                    "data_availability": "TEST-ONLY complete",
                    "cite": "calc: test-only input",
                }
                for i in range(1, result["n_supplied"] + 1)
            ]
        elif table.id == "cp1c.peer_metrics":
            rows = [
                {
                    "peer": f"TEST-{i}",
                    "metric_id": "net_leverage",
                    "value": str(i),
                    "unit_label": "x",
                    "period": "FY2025",
                    "definition_note": "TEST-ONLY",
                    "cite": "calc: test-only input",
                }
                for i in range(1, result["n_supplied"] + 1)
            ]
        elif table.id == "cp1c.positioning":
            rows = [
                {
                    **result["groups"][0]["positioning"],
                    "credit_implication": "TEST-ONLY higher debt burden",
                    "cite": "calc: peer_statistics test-only input",
                }
            ]
        else:
            rows = []
        lines += [
            "| " + " | ".join("—" if row.get(n) is None else str(row[n]) for n in names) + " |"
            for row in rows
        ]
        lines += [""]
    return text[:start] + "\n".join(lines) + "\n" + text[end:]


def test_calculator_columns_feed_contract_and_keep_outlier_sensitivity(rules: Rules) -> None:
    result = peer_statistics.compute(synthetic_input())
    group = result["groups"][0]
    row = group["positioning"]
    assert [row[k] for k in ("peer_min", "peer_q1", "peer_median", "peer_q3", "peer_max")] == [
        "1",
        "1.75",
        "2.5",
        "3.25",
        "4",
    ]
    assert row["n"] == 4 and row["position"] == "Above"
    assert group["positioning_excluding_outliers"]["n"] == 3
    assert group["positioning_excluding_outliers"]["peer_q1"] is None
    assert check(positive_handoff(result, rules), contract("CP-1C", rules), rules) == (0, [])


def test_small_n_cannot_be_promoted_by_a_module_status(rules: Rules) -> None:
    data = synthetic_input()
    data["peers"].pop()
    text = positive_handoff(peer_statistics.compute(data), rules)
    code, findings = check(text, contract("CP-1C", rules), rules)
    assert code == 2 and any("peer_q1" in f.message or "peer_q3" in f.message for f in findings)


def test_supplied_fixture_preserves_blocked_reachability_and_named_gaps(rules: Rules) -> None:
    text = fixture("CP-1C")
    assert check(text, contract("CP-1C", rules), rules) == (3, [])
    assert "four aligned operating peers" in text and "MGM/PENN" in text
    handoff = parse(text)
    assert not handoff.tables["cp1c.peer_metrics"].rows
    assert not handoff.tables["citations"].rows
    table = handoff.tables["cp1c.positioning"]
    assert table.rows[0][table.columns.index("peer_q1")] == "—"


def test_documented_sidecar_invocation_uses_actual_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    inputs = tmp_path / "CP-1C-peer_statistics.json"
    output = tmp_path / "CP-1C-peer_statistics.out.json"
    inputs.write_text(json.dumps(synthetic_input()))
    assert main(["calc", "peer_statistics", "--in", str(inputs), "--out", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["groups"][0]["positioning"]["peer_median"] == "2.5"
    assert "excluding_outliers" in capsys.readouterr().out
    assert result["input_basis"]["cite"].startswith("TEST-ONLY")


def test_method_retains_qualification_and_source_safeguards() -> None:
    prompt = (RBOT_ROOT / "modules/CP-1C/MODULE.md").read_text()
    for retained in (
        "16 dimensions",
        "13 exclusion triggers",
        "11 checks",
        "AP11",
        "No web discovery or fetching",
        "Exclude the borrower",
        "both including/excluding",
        ">18-month",
        ">12-month",
        "same period/definition/currency",
        "Trading and Transaction separate",
        "strongest supported counter-case",
        "Critical Q1/Q3",
        "not source evidence",
        "never recompute them",
    ):
        assert retained in prompt


def test_all_reference_comparability_dimensions_survive() -> None:
    reference = (
        RBOT_ROOT.parent / "reference/deploy-v-r14/skills/cp-1c-peer-benchmark/"
        "references/REF_CP-1C_STEPS.md"
    ).read_text()
    dimensions = reference.split("## 16 Comparability Dimensions", 1)[1].splitlines()[1]
    prompt = (RBOT_ROOT / "modules/CP-1C/MODULE.md").read_text().casefold()
    assert len(dimensions.split(" | ")) == 16
    for dimension in dimensions.split(" | "):
        assert dimension.casefold() in prompt


def permission_message(run: Path, module: str, rules: Rules) -> dict[str, Any]:
    """Exercise permission emission; upstream qualification has separate integration checks."""
    from dataclasses import replace

    from rbotlib import dispatch

    record = {
        "run_id": "TEST",
        "issuer_id": "TEST",
        "as_of_date": "2026-10-02",
        "pathway": "FULL_CREDIT_ASSESSMENT",
        "depth": "full",
        "steps": {},
    }
    text = dispatch._message(
        run, RBOT_ROOT, replace(contract(module, rules), inputs=()), record, ([], None, rules, {})
    )
    return {
        label: json.loads(value)
        for line in text.splitlines()
        if line.startswith(("Allowed calculator:", "May write only:"))
        for label, value in [line.split(": ", 1)]
    }


@pytest.mark.parametrize(
    "module,calculator", [("CP-3", "bond_analytics"), ("CP-1C", "peer_statistics")]
)
def test_dispatch_grants_only_the_module_calculator(
    tmp_path: Path, rules: Rules, module: str, calculator: str
) -> None:
    message = permission_message(tmp_path, module, rules)
    assert message["Allowed calculator"] == calculator
    expected = [
        f"handoffs/{module}.md",
        f"calc/{module}-{calculator}.json",
        f"calc/{module}-{calculator}.out.json",
    ]
    if module == "CP-1C":
        expected.append("calc/CP-1C")
    assert message["May write only"] == [str(tmp_path / p) for p in expected]
    assert permission_message(tmp_path, "CP-2", rules)["Allowed calculator"] is None
    assert permission_message(tmp_path, "CP-2", rules)["May write only"] == [
        str(tmp_path / "handoffs/CP-2.md")
    ]


@pytest.mark.parametrize(
    "name",
    [
        "calc",
        "calc/CP-1C-peer_statistics.json",
        "calc/CP-1C-peer_statistics.out.json",
        "calc/CP-1C",
    ],
)
def test_dispatch_refuses_symlink_in_calculator_grant(
    tmp_path: Path, rules: Rules, name: str
) -> None:
    from rbotlib.inventory import RunError

    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(tmp_path / "foreign")
    with pytest.raises(RunError, match="symlink"):
        permission_message(tmp_path, "CP-1C", rules)


@pytest.mark.parametrize("kind", ["file", "nested-symlink", "nested-hardlink", "fifo"])
def test_calculator_namespace_refuses_existing_unsafe_entry(
    tmp_path: Path, rules: Rules, kind: str
) -> None:
    import os

    from rbotlib.inventory import RunError

    folder = tmp_path / "calc/CP-1C"
    folder.parent.mkdir()
    if kind == "file":
        folder.write_text("not a directory")
    else:
        folder.mkdir()
        entry = folder / "metric.json"
        foreign = tmp_path / "foreign"
        foreign.write_text("foreign data")
        if kind == "nested-symlink":
            entry.symlink_to(foreign)
        elif kind == "nested-hardlink":
            entry.hardlink_to(foreign)
        else:
            os.mkfifo(entry)
    with pytest.raises(RunError):
        permission_message(tmp_path, "CP-1C", rules)


def test_module_calculator_namespace_retains_normal_metric_files(
    tmp_path: Path, rules: Rules
) -> None:
    folder = tmp_path / "calc/CP-1C"
    folder.mkdir(parents=True)
    source = folder / "revenue.json"
    source.write_text('{"metric_id":"TEST-ONLY"}')
    assert str(folder) in permission_message(tmp_path, "CP-1C", rules)["May write only"]
    assert source.read_text() == '{"metric_id":"TEST-ONLY"}'
