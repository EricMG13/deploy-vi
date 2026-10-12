"""model.json's guards (up-front review of the non-money modules,
2026-10-11): every figure in it is exact, a gap is a null with its reason."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, run_brief, run_folder
from run_cases import _model, _run

from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.citations import Citation, Citations
from rbotlib.model.frame import SourceRef
from rbotlib.model.output import sources_cut


def _built(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    return run, _model(run)


def _shown(run: Path, table_id: str) -> list[dict[str, str]]:
    table = parse((run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")).tables[table_id]
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def test_capital_structure_rows_hold_exact_figures_not_display_text(tmp_path: Path) -> None:
    # I5: the rows held "1.43x", "6.7%" and "—" copied from MODEL.md.
    run, data = _built(tmp_path)
    rows = {r["facility_id"]: r for r in data["capital_structure"]["rows"]}
    shown = {r["facility_id"]: r for r in _shown(run, "snapshot.capital_structure")}
    tlb = rows["tlb"]
    exact = Decimal(tlb["ssim_multiple_x"])
    assert len(tlb["ssim_multiple_x"].split(".")[1]) > 2 and "x" not in tlb["ssim_multiple_x"]
    assert f"{exact:.2f}x" == shown["tlb"]["ssim_multiple_x"]
    assert "%" not in tlb["pct_ev_pct"]
    assert f"{Decimal(tlb['pct_ev_pct']):.1f}%" == shown["tlb"]["pct_ev_pct"]
    assert tlb["outstanding"] == str(Decimal(tlb["outstanding"]))
    assert tlb["reasons"] == {}


def test_the_totals_hold_exact_ratios_and_a_gap_holds_its_reason(tmp_path: Path) -> None:
    _, data = _built(tmp_path)
    totals = {r["line"]: r for r in data["capital_structure"]["totals"]}
    house = data["house"]
    assert totals["Total debt"]["ssim_multiple_x"] == house["ssim_multiple"]["value"]
    assert totals["Total debt"]["structuring_multiple_x"] == house["structuring_multiple"]["value"]
    cash = totals["Cash"]
    assert cash["structuring_multiple_x"] is None
    assert cash["reasons"]["structuring_multiple_x"] == "NOT_APPLICABLE"
    cover = totals["PF interest cover"]
    assert cover["ssim_multiple_x"] == house["pf_interest_cover"]["value"]


def test_a_figure_that_is_not_there_is_null_with_its_reason(tmp_path: Path) -> None:
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief("—"))
    assert main(["model", "--run", str(run)]) == 0
    data = _model(run)
    row = data["capital_structure"]["rows"][0]
    assert row["pct_ev_pct"] is None
    assert row["reasons"]["pct_ev_pct"] == "NOT_SOURCED"
    assert all(x["pct"] is None for x in data["house"]["pct_ev_by_facility"])
    assert all(x["reason"] == "NOT_SOURCED" for x in data["house"]["pct_ev_by_facility"])


def test_the_maturity_wall_and_adjustments_hold_exact_amounts(tmp_path: Path) -> None:
    _, data = _built(tmp_path)
    wall = data["maturity_wall"]
    assert wall and all(Decimal(r["amount"]) == Decimal(r["amount"]) for r in wall)
    assert all(not r["amount"].endswith("%") for r in wall)
    bridge = {r["line"]: r for r in data["ebitda_adjustments"]}
    assert bridge["SSIM EBITDA"]["amount"] == data["house"]["ssim_ebitda"]["value"]
    assert bridge["Structuring EBITDA"]["amount"] == data["house"]["structuring_ebitda"]["value"]


def test_limitations_are_bare_codes_with_details_beside_them(tmp_path: Path) -> None:
    # M2: spec §6.2 shows ["GROWTH_UNAVAILABLE", ...]; the strings held "CODE: message".
    _, data = _built(tmp_path)
    assert all(":" not in code and " " not in code for code in data["limitations"])
    assert len(set(data["limitations"])) == len(data["limitations"])
    details = data["limitation_details"]
    assert {d["code"] for d in details} == set(data["limitations"])
    assert all(set(d) == {"code", "message", "line_id", "column_id"} for d in details)


def test_sources_cut_counts_citations_not_source_refs() -> None:
    # M1: one source_id naming nine markers showed eight citations and recorded no cut.
    model = credit_model(ModelInputs(example_registers(), exclude_unrealised=True))
    nine = SourceRef(" ".join(f"[C{n}]" for n in range(1, 10)), "", "1")
    column = next(n for n, c in enumerate(model.columns) if c.column_id == "FY:FY2025")
    line = next(x for x in model.lines if x.line_id == "revenue")
    cells = tuple(
        replace(c, sources=(nine,)) if n == column else replace(c, sources=())
        for n, c in enumerate(line.cells)
    )
    only = replace(model, lines=(replace(line, cells=cells),))
    cited = {f"C{n}": Citation("CP-1", f"C{n}", "f.txt", "p.1", "x") for n in range(1, 10)}
    assert [x.code for x in sources_cut(only, Citations({"CP-1": cited}))] == ["SOURCES_CUT"]
    one = replace(only, lines=(replace(line, cells=tuple(replace(c, sources=()) for c in cells)),))
    assert sources_cut(one, Citations({"CP-1": cited})) == []


def test_without_projection_the_forecast_schema_reports_incomplete(tmp_path: Path) -> None:
    _, data = _built(tmp_path)
    assert data["forecast"] == {"status": "incomplete", "rows": {}}
    assert "NO_PROJECTIONS" in data["limitations"]
