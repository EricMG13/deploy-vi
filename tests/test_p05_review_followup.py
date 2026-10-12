"""Independent Plan05 review regressions, with real arithmetic and Handoff paths."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

import ab_grade
from conftest import FIXTURES
from rbotlib.contract import load_contract
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import check


def _changed_first(text: str, table_id: str, column: str, value: str) -> str:
    table = parse(text).tables[table_id]
    row = table.rows[0]
    changed = list(row)
    changed[table.columns.index(column)] = value

    def shown(values: list[str]) -> str:
        return "| " + " | ".join(c.replace("|", "\\|") for c in values) + " |"

    return text.replace(shown(row), shown(changed), 1)


def test_duplicate_strategy_rows_do_not_certify_coverage() -> None:
    rules = load_rules()
    contract = load_contract(RBOT_ROOT / "modules/CP-6/contract.json", rules)
    text = (FIXTURES / "handoffs/CP-6.md").read_text("utf-8")
    table = parse(text).tables["snapshot.recommendation"]
    for row in table.rows[1:]:
        text = text.replace(
            "| " + " | ".join(row) + " |", "| " + " | ".join(table.rows[0]) + " |", 1
        )
    assert (
        ab_grade.front_page_fill(
            contract,
            parse(text),
            FIXTURES.parent / "corpus/expectations/czr-2026q2-primary.json",
            rules,
        )
        != "15/15"
    )
    code, findings = check(text, contract, rules)
    assert code == 2 and any(f.code == "duplicate_row_key" for f in findings)


def test_wrong_instrument_id_does_not_fill_the_expected_identity() -> None:
    rules = load_rules()
    contract = load_contract(RBOT_ROOT / "modules/CP-3/contract.json", rules)
    text = (FIXTURES / "handoffs/CP-3.md").read_text("utf-8")
    text = _changed_first(text, "snapshot.instrument_levels", "facility_id", "CEI-OTHER-2039")
    assert (
        ab_grade.front_page_fill(
            contract,
            parse(text),
            FIXTURES.parent / "corpus/expectations/czr-2026q2-primary.json",
            rules,
        )
        == "120/129"
    )


def test_scoring_refuses_an_absent_a_citation_measurement(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    order = tmp_path / "order.json"
    order.write_text('{"X":"A","Y":"B"}', "utf-8")
    args = [
        "score",
        "--module",
        "CP-1",
        "--expectations",
        str(FIXTURES.parent / "corpus/expectations/czr-2026q2-primary.json"),
        "--order",
        str(order),
        "--sheets",
        str(FIXTURES / "ab/grader-1.md"),
        str(FIXTURES / "ab/grader-2.md"),
        "--c-b",
        "0.96",
    ]
    assert ab_grade.main(args) == 2
    assert "--c-a is required" in capsys.readouterr().out


def _a_evidence(tmp_path: Path, sources: str = "S1") -> tuple[str, Path, Path]:
    run = tmp_path / "run"
    prepared = run / "prepared"
    prepared.mkdir(parents=True)
    filename = "SYNTHETIC_annual.txt"
    (prepared / filename).write_text(
        "<<< page 1 >>>\nSYNTHETIC qualification source\nRevenue 100.\n", "utf-8"
    )
    (prepared / "index.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": filename,
                        "prepared": "prepared/" + filename,
                        "unreadable": None,
                        "image_read": False,
                        "kind": "txt",
                    }
                ]
            }
        ),
        "utf-8",
    )
    text = f"""---
module_id: CP-1
issuer_id: CZR
qa_status: Passed
---
## Audit Summary
SYNTHETIC r14-format qualification Handoff.
## Analysis
Revenue is 100 [E1].
## Evidence Trace
| Evidence ID | Source IDs | Locator | Excerpt |
|---|---|---|---|
| E1 | {sources} | p. 1 | Revenue 100. |
## Source Registry
| Source ID | File |
|---|---|
| S1 | {filename} |
| S2 | SYNTHETIC_missing.txt |
## Gaps & Conflicts
None.
## QA Validation
Passed.
"""
    mapping = {
        "source_registry": {"id": "Source ID", "file": "File"},
        "evidence_trace": {"id": "Evidence ID", "sources": "Source IDs"},
        "citations": [
            {"evidence_id": "E1", "source_id": "S1", "locator": "p. 1", "excerpt": "Revenue 100."}
        ],
    }
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(mapping), "utf-8")
    return text, run, path


def test_a_citations_are_anchored_from_r14_evidence_and_registry(tmp_path: Path) -> None:
    text, run, mapping = _a_evidence(tmp_path)
    measured = ab_grade.measure_a(text, run, mapping)
    assert measured["C"] == "1/1" and measured["findings"] == []
    changed = text.replace("Revenue 100.", "Revenue 999.")
    data = json.loads(mapping.read_text("utf-8"))
    data["citations"][0]["excerpt"] = "Revenue 999."
    mapping.write_text(json.dumps(data), "utf-8")
    measured = ab_grade.measure_a(changed, run, mapping)
    assert measured["C"] == "0/1" and "citation_unanchored" in measured["findings"]


def test_a_mapping_covers_every_reference_on_a_trace_record(tmp_path: Path) -> None:
    text, run, mapping = _a_evidence(tmp_path, "S1, S2")
    with pytest.raises(ab_grade.ABError, match=r"missing evidence mapping.*S2"):
        ab_grade.measure_a(text, run, mapping)


@pytest.mark.parametrize(
    "change,error",
    [
        ("missing", "missing evidence mapping"),
        ("duplicate", "duplicate evidence mapping"),
        ("unknown", "unknown evidence mapping"),
        ("locator", "not declared by A"),
        ("malformed", "nonempty evidence_id"),
    ],
)
def test_a_map_refuses_unverifiable_qualification_inputs(
    tmp_path: Path, change: str, error: str
) -> None:
    text, run, path = _a_evidence(tmp_path)
    mapping = json.loads(path.read_text())
    entries = mapping["citations"]
    if change == "missing":
        entries.clear()
    elif change == "duplicate":
        entries.append(dict(entries[0]))
    elif change == "unknown":
        entries[0]["source_id"] = "S3"
    elif change == "locator":
        entries[0]["locator"] = "p. 77"
    else:
        del entries[0]["excerpt"]
    path.write_text(json.dumps(mapping))
    with pytest.raises(ab_grade.ABError, match=error):
        ab_grade.measure_a(text, run, path)


def test_every_source_on_a_trace_row_contributes_to_a_measurement(tmp_path: Path) -> None:
    text, run, path = _a_evidence(tmp_path, "[S1], [S2]")
    mapping = json.loads(path.read_text())
    mapping["citations"].append(dict(mapping["citations"][0], source_id="S2"))
    path.write_text(json.dumps(mapping))
    measured = ab_grade.measure_a(text, run, path)
    assert measured["C"] == "1/2"
    assert "source_unknown" in measured["findings"]


def test_overlapping_expected_identities_cannot_count_one_physical_row_twice() -> None:
    from rbotlib.handoff import Table

    entry = {
        "table": "snapshot.relative_value",
        "expected_rows": 2,
        "expected_identities": [{"block": "Loan peers"}, {"name": "Issuer"}],
    }
    table = Table(["block", "name", "value"], [["Loan peers", "Issuer", "100"]])
    assert ab_grade._filled(table, {"value"}, entry, load_rules()) == 0


@pytest.mark.parametrize("sources", ["S1; S3", "S1,S1", "S1,"])
def test_native_trace_refuses_unknown_or_duplicate_references(tmp_path: Path, sources: str) -> None:
    text, run, path = _a_evidence(tmp_path, sources)
    with pytest.raises(ab_grade.ABError, match="source reference"):
        ab_grade.measure_a(text, run, path)


@pytest.mark.corpus
@pytest.mark.parametrize(
    "module", ["CP-1", "CP-1A", "CP-1B", "CP-1D", "CP-2", "CP-3", "CP-5", "CP-6"]
)
def test_converted_stand_in_a_is_measured_against_the_same_sources(
    prepared_run: Callable[[str], Path], tmp_path: Path, module: str
) -> None:
    run = prepared_run("czr-2026q2-primary")
    text = (FIXTURES / f"handoffs/{module}.md").read_text("utf-8")
    rows = parse(text).tables["citations"].rows
    path = tmp_path / "map.json"
    path.write_text(
        json.dumps(
            {
                "source_registry": {"id": "id", "file": "source"},
                "evidence_trace": {"id": "id", "sources": "source_id"},
                "citations": [
                    {"evidence_id": r[0], "source_id": r[0], "locator": r[2], "excerpt": r[3]}
                    for r in rows
                ],
            }
        )
    )
    measured = ab_grade.measure_a(ab_grade.to_r14(text), run, path)
    assert measured["C"] == f"{len(rows)}/{len(rows)}" and measured["findings"] == []


def test_a_map_cannot_hide_an_unknown_bracket_reference_elsewhere_on_the_trace(
    tmp_path: Path,
) -> None:
    text, run, path = _a_evidence(tmp_path)
    text = text.replace("Revenue 100. |", "Revenue 100. [S3] |")
    with pytest.raises(ab_grade.ABError, match="outside the configured source column"):
        ab_grade.measure_a(text, run, path)


@pytest.mark.parametrize("reference", ["S2", "[S3]"])
def test_a_source_reference_in_a_trace_heading_cannot_be_ignored(
    tmp_path: Path, reference: str
) -> None:
    text, run, path = _a_evidence(tmp_path)
    text = text.replace(
        "## Evidence Trace", "## Evidence Trace\n### Additional evidence " + reference
    )
    with pytest.raises(ab_grade.ABError, match="heading is unverifiable"):
        ab_grade.measure_a(text, run, path)


@pytest.mark.parametrize("side", ["A", "B"])
@pytest.mark.parametrize("message", ["malformed prepared/index.json; no reference verified", ""])
def test_a_global_run_error_never_becomes_a_citation_ratio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, side: str, message: str
) -> None:
    import ab_evidence

    from rbotlib.handoff import Handoff
    from rbotlib.validate import Finding

    text, run, path = _a_evidence(tmp_path)
    data = json.loads(path.read_text())
    data["citations"] = [dict(data["citations"][0], evidence_id=f"E{i}") for i in range(1, 21)]
    path.write_text(json.dumps(data))
    text = text.replace(
        "| E1 | S1 | p. 1 | Revenue 100. |",
        "\n".join(f"| E{i} | S1 | p. 1 | Revenue 100. |" for i in range(1, 21)),
    )

    def failed_run(_h: Handoff, _run: Path) -> list[Finding]:
        return [Finding("run_error", message)]

    # Explicit final-Plan02 Finding contract; do not replace or rebase the frozen validator.
    monkeypatch.setattr(ab_evidence, "run_findings", failed_run)
    monkeypatch.setattr(ab_grade, "run_findings", failed_run)
    with pytest.raises(ab_grade.ABError, match=r"run_error.*unverifiable"):
        if side == "A":
            ab_grade.measure_a(text, run, path)
        else:
            b = (FIXTURES / "handoffs/CP-1.md").read_text()
            ab_grade.measure("CP-1", b, run, None)
