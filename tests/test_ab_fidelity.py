"""Narrow native-map fidelity and probability-domain regressions from scoped re-review."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from test_p05_review_followup import _a_evidence

import ab_grade


def _write_map(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data))


@pytest.mark.parametrize("field,shortened", [("excerpt", "Revenue"), ("locator", "p.")])
def test_native_values_cannot_be_shortened_to_manufacture_anchoring(
    tmp_path: Path, field: str, shortened: str
) -> None:
    text, run, path = _a_evidence(tmp_path)
    text = text.replace("Revenue 100.", "Revenue 999.")
    data = json.loads(path.read_text())
    data["evidence_trace"].update(locator="Locator", excerpt="Excerpt")
    data["citations"][0]["excerpt"] = "Revenue 999."
    (run / "prepared/SYNTHETIC_annual.txt").write_text(
        "<<< page 1 >>>\nSYNTHETIC Revenue 100.\n<<< page 2 >>>\nRevenue 999.\n"
    )
    _write_map(path, data)
    assert ab_grade.measure_a(text, run, path)["C"] == "0/1"
    data["citations"][0][field] = shortened
    _write_map(path, data)
    with pytest.raises(ab_grade.ABError, match="not faithful"):
        ab_grade.measure_a(text, run, path)


def test_native_fields_must_be_explicit_not_inferred_by_containment(tmp_path: Path) -> None:
    text, run, path = _a_evidence(tmp_path)
    data = json.loads(path.read_text())
    data["evidence_trace"].pop("locator", None)
    data["evidence_trace"].pop("excerpt", None)
    _write_map(path, data)
    with pytest.raises(ab_grade.ABError, match="column names"):
        ab_grade.measure_a(text, run, path)


def _multi_fields(tmp_path: Path) -> tuple[str, Path, Path, dict[str, Any]]:
    text, run, path = _a_evidence(tmp_path, "S1, S2")
    text = text.replace("Locator | Excerpt |", "Locator | Excerpt | Other page | Other quote |")
    text = text.replace("|---|---|---|---|", "|---|---|---|---|---|---|")
    text = text.replace("| p. 1 | Revenue 100. |", "| p. 1 | Revenue 999. | p. 2 | Revenue 100. |")
    prepared = run / "prepared"
    (prepared / "SYNTHETIC_missing.txt").write_text(
        "<<< page 1 >>>\nSYNTHETIC other source\n<<< page 2 >>>\nRevenue 100.\n"
    )
    index = json.loads((prepared / "index.json").read_text())
    index["files"].append(
        dict(
            index["files"][0],
            path="SYNTHETIC_missing.txt",
            prepared="prepared/SYNTHETIC_missing.txt",
        )
    )
    (prepared / "index.json").write_text(json.dumps(index))
    data = json.loads(path.read_text())
    data["evidence_trace"].update(locator="Locator", excerpt="Excerpt")
    data["source_fields"] = [
        {"evidence_id": "E1", "source_id": "S2", "locator": "Other page", "excerpt": "Other quote"}
    ]
    data["citations"][0]["excerpt"] = "Revenue 999."
    data["citations"].append(
        dict(data["citations"][0], source_id="S2", locator="p. 2", excerpt="Revenue 100.")
    )
    _write_map(path, data)
    return text, run, path, data


def test_lossless_per_source_fields_keep_both_actual_quotations(tmp_path: Path) -> None:
    text, run, path, _ = _multi_fields(tmp_path)
    measured = ab_grade.measure_a(text, run, path)
    assert measured["C"] == "1/2" and measured["evidence_references"] == 2
    assert measured["findings"] == ["citation_unanchored"]


def test_quote_from_another_source_field_cannot_replace_a_bad_native_quote(tmp_path: Path) -> None:
    text, run, path, data = _multi_fields(tmp_path)
    data["citations"][0]["excerpt"] = "Revenue 100."
    _write_map(path, data)
    with pytest.raises(ab_grade.ABError, match="not faithful"):
        ab_grade.measure_a(text, run, path)


@pytest.mark.parametrize(
    "ratio", ["-1", "1.1", "-1/-1", "0/-1", "1/0", "2/1", "-1/2", "0/Infinity", "1/", "NaN/1"]
)
def test_impossible_coverage_is_bad_input(ratio: str) -> None:
    with pytest.raises(ab_grade.ABError, match="not a ratio"):
        ab_grade._ratio(ratio, "--c-a")


@pytest.mark.parametrize(
    "ratio,value", [("0", "0"), ("1", "1"), ("0/20", "0"), ("19/20", ".95"), ("20/20", "1")]
)
def test_real_coverage_boundaries_remain_valid(ratio: str, value: str) -> None:
    from decimal import Decimal

    assert ab_grade._ratio(ratio, "--c-a") == Decimal(value)


@pytest.mark.parametrize(
    "change,error",
    [
        ("duplicate", "selector"),
        ("unknown", "selector"),
        ("missing_column", "column"),
        ("malformed", "nonempty"),
        ("shape", "source_fields"),
    ],
)
def test_source_specific_selectors_refuse_unverifiable_shapes(
    tmp_path: Path, change: str, error: str
) -> None:
    text, run, path, data = _multi_fields(tmp_path)
    fields = data["source_fields"]
    if change == "duplicate":
        fields.append(dict(fields[0]))
    elif change == "unknown":
        fields[0]["source_id"] = "S3"
    elif change == "missing_column":
        fields[0]["excerpt"] = "Missing native quote"
    elif change == "malformed":
        fields[0]["excerpt"] = ""
    else:
        data["source_fields"] = {}
    _write_map(path, data)
    with pytest.raises(ab_grade.ABError, match=error):
        ab_grade.measure_a(text, run, path)


def test_only_cell_edge_whitespace_is_ignored(tmp_path: Path) -> None:
    text, run, path = _a_evidence(tmp_path)
    data = json.loads(path.read_text())
    data["citations"][0]["excerpt"] = "  Revenue 100.  "
    data["citations"][0]["locator"] = " p. 1 "
    _write_map(path, data)
    assert ab_grade.measure_a(text, run, path)["C"] == "1/1"
    data["citations"][0]["excerpt"] = "revenue 100."
    _write_map(path, data)
    with pytest.raises(ab_grade.ABError, match="not faithful"):
        ab_grade.measure_a(text, run, path)
