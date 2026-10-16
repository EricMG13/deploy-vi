"""`rbot model --run`: model.json and the exits (spec §6.2, §6.8)."""

from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, run_brief, run_folder
from run_cases import _model, _run

from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.model._cells import CONTEXT
from rbotlib.model.output import MAX_SOURCES


def test_rbot_model_writes_the_pair_without_excel_export(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    out = capsys.readouterr().out
    assert "qa_status Pass" in out and "CP1D_NOT_READ" in out
    data = _model(run)
    assert data["schema"] == "rbot-model/1"
    assert (data["currency"], data["unit"], data["exclude_unrealised"]) == ("USD", "MILLIONS", True)
    assert data["inputs"]["CP-1D"] is None and data["inputs"]["CP-2G"] is None
    assert len(data["inputs"]["CP-1"]) == 64
    assert data["snapshot_columns"]["LTM"] == "PF:LTM_Q2_2026"
    assert data["house"]["structuring_ebitda"]["value"] == "4134"
    assert data["house"]["ev"] == {
        "value": "34799.0",
        "basis": "ssim_multiple",
        "inputs": {"market_cap": None, "ssim_ev_multiple": "8.5"},
        "reason": None,
    }
    assert data["rate_deck"] is None
    assert data["forecast"] == {"status": "incomplete", "rows": {}}
    assert data["reconciliation_faults"] == []
    assert (run / "handoffs" / "MODEL.md").exists()
    assert not (run / "model.xlsx").exists()


def test_model_json_cells_keep_figures_exact_and_name_their_sources(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["model", "--run", str(run)])
    data = _model(run)
    lines = {line["line_id"]: line for line in data["lines"]}
    revenue = {c["column_id"]: c for c in lines["revenue"]["cells"]}
    fy = revenue["FY:FY2025"]
    assert (fy["value"], fy["basis"], fy["reason"]) == ("11519", "REPORTED", None)
    assert fy["sources"] == [
        {
            "module": "CP-1",
            "citation_id": "C3",
            "source": "fixture-S3.txt",
            "locator": "10-K FY2025, Item 8 and quarterly data",
            "excerpt": "2873",  # the builder's C3 quotes the first S3 cell it wrote
        }
    ]
    assert lines["revenue"]["band"] == 2 and lines["revenue"]["unit_label"] == "USD m"
    margin = {c["column_id"]: c for c in lines["metric:gross_margin"]["cells"]}
    with localcontext(CONTEXT):
        assert Decimal(margin["FY:FY2025"]["value"]) == Decimal(6681) / Decimal(11519)
    growth = {c["column_id"]: c for c in lines["revenue_growth"]["cells"]}
    assert (growth["FY:FY2023"]["value"], growth["FY:FY2023"]["reason"]) == (None, "NOT_APPLICABLE")
    assert all(len(c["sources"]) <= MAX_SOURCES for x in data["lines"] for c in x["cells"])
    assert "SOURCES_CUT" in data["limitations"]
    assert {
        "code": "SOURCES_CUT",
        "message": "some cells name more than 8 sources; each shows its first 8",
        "line_id": None,
        "column_id": None,
    } in data["limitation_details"]
    tlb = lines["fac:tlb"]
    assert tlb["terms"]["spread_or_coupon"] == "+275 bp" and tlb["rank"] == "Senior secured"


def test_model_json_is_deterministic(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["model", "--run", str(run)])
    first = _model(run)
    main(["model", "--run", str(run)])
    second = _model(run)
    first.pop("generated_at"), second.pop("generated_at")
    assert first == second
    assert json.dumps(first, indent=1, ensure_ascii=False) == json.dumps(
        second, indent=1, ensure_ascii=False
    )


def test_a_malformed_input_exits_1_naming_where(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    regs = example_registers()
    text = cp1_handoff(regs).replace("| 11519 |", "| about 11.5bn |", 1)
    run = run_folder(tmp_path, text, run_brief())
    assert main(["model", "--run", str(run)]) == 1
    out = capsys.readouterr().err
    assert out.startswith("model: cp1.model_account_register row ")
    assert "column value: 'about 11.5bn' is not a figure" in out
    assert not (run / "model.json").exists()


def test_missing_or_unreadable_inputs_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    (run / "handoffs" / "CP-1.md").unlink()
    assert main(["model", "--run", str(run)]) == 1
    assert capsys.readouterr().err == "model: CP-1.md: missing; the Model needs it\n"
    (run / "handoffs" / "CP-1.md").write_text("no front matter", encoding="utf-8")
    assert main(["model", "--run", str(run)]) == 1
    assert "model: CP-1.md: missing front matter" in capsys.readouterr().err
    (run / "handoffs" / "CP-1.md").write_text(
        cp1_handoff(example_registers()).replace("[C3]", "[C99]"), encoding="utf-8"
    )
    assert main(["model", "--run", str(run)]) == 1
    assert "CP-1 source_id [C99]: no citation C99" in capsys.readouterr().err


def test_a_pipe_in_a_cited_excerpt_stays_escaped_in_model_md(tmp_path: Path) -> None:
    lines = cp1_handoff(example_registers()).splitlines()
    at = next(n for n, line in enumerate(lines) if line.startswith("| C3 |"))
    lines[at] = lines[at].removesuffix(" |") + r" \| 2,873 |"
    run = run_folder(tmp_path, "\n".join(lines), run_brief())
    assert main(["model", "--run", str(run)]) == 0
    text = (run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")
    assert r"| 2873 \| 2,873 |" in text
    excerpts = {row[1]: row[3] for row in parse(text).tables["citations"].rows}
    assert excerpts["fixture-S3.txt"] == "2873 | 2,873"


def test_model_md_is_a_handoff_with_the_four_sections_and_its_tables(tmp_path: Path) -> None:
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    h = parse((run / "handoffs" / "MODEL.md").read_text(encoding="utf-8"))
    assert h.sections == ["Analysis", "Tables", "Gaps", "Citations"]
    assert {"snapshot.capital_structure", "model.house", "model.limitations"} <= set(h.tables)
    assert (h.orphan_tags, h.duplicate_tags, h.invalid_tags) == ([], [], [])


@pytest.mark.parametrize("kind", ["file", "directory", "symlink"])
def test_retired_workbook_is_preserved_by_standalone_model(tmp_path: Path, kind: str) -> None:
    run = _run(tmp_path)
    legacy, supplied = run / "model.xlsx", run / "supplied.xlsx"
    supplied.write_bytes(b"analyst supplied input")
    if kind == "file":
        legacy.write_bytes(b"legacy workbook")
    elif kind == "directory":
        legacy.mkdir()
    else:
        legacy.symlink_to(supplied)
    assert main(["model", "--run", str(run)]) == 0
    assert (
        legacy.is_dir()
        if kind == "directory"
        else legacy.read_bytes()
        == (b"legacy workbook" if kind == "file" else b"analyst supplied input")
    )
    assert legacy.is_symlink() == (kind == "symlink")
    assert supplied.read_bytes() == b"analyst supplied input"
