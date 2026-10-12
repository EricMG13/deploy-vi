"""`rbot model` at its edges: limits, a Model without an LTM, listed equity,
uncited sources, foreign facilities and the limitation codes (the mutation
gate's findings on `run`, `output` and `snapshot`)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from credit_model_fixture import example_registers
from history_cases import _regs
from model_handoffs import cp1_handoff, run_brief, run_folder, table
from run_cases import _model

from rbotlib.cli import main
from rbotlib.handoff import Table, parse
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.citations import Citation, Citations
from rbotlib.model.frame import Cell, SourceRef
from rbotlib.model.output import sources_cut
from rbotlib.model.registers import Cp1Registers, KpiRow
from rbotlib.model.run import _model_limitations

EQUITY = ["market_cap", "value_date", "currency", "unit", "cite"]


def _run(
    tmp_path: Path, regs: Cp1Registers, cp1: str | None = None, multiple: str = "8.5x"
) -> Path:
    return run_folder(tmp_path, cp1 or cp1_handoff(regs), run_brief(multiple))


def _tables(run: Path) -> dict[str, Table]:
    return dict(parse((run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")).tables)


def _rows(found: Table) -> list[dict[str, str]]:
    return [dict(zip(found.columns, row, strict=True)) for row in found.rows]


def test_the_column_and_line_limits_are_inclusive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plain = [y for y in range(1901, 2100) if y % 4]  # 365-day years only (history_cases)
    years = _regs(fy={f"FY{y}": {"revenue": 1} for y in plain[:63]})
    assert len(credit_model(ModelInputs(years)).columns) == 64
    assert main(["model", "--run", str(_run(tmp_path / "a", years))]) == 0
    more = _regs(fy={f"FY{y}": {"revenue": 1} for y in plain[:64]})
    assert main(["model", "--run", str(_run(tmp_path / "b", more))]) == 1
    assert "the Model has 65 columns and" in capsys.readouterr().err
    regs = example_registers()
    kpis = tuple(
        KpiRow(f"k{n}", f"K {n}", 1, "FY2025", Decimal(1), "UNITS", "PERIOD_END", None)
        for n in range(290)
    )
    full = replace(regs, kpis=(*regs.kpis, *kpis))
    assert len(credit_model(ModelInputs(full)).lines) == 400
    assert main(["model", "--run", str(_run(tmp_path / "c", full))]) == 0
    over = replace(full, kpis=(*full.kpis, replace(kpis[0], kpi_id="k_over")))
    assert main(["model", "--run", str(_run(tmp_path / "d", over))]) == 1


def test_a_model_without_an_ltm_still_writes_every_file(tmp_path: Path) -> None:
    regs = example_registers()
    fy = next(p for p in regs.periods if p.period_id == "FY2025")
    undated = replace(fy, start_date=None, end_date=None, day_count=None)  # so no LTM column
    own: dict[str, Any] = {  # a row naming another period is refused
        name: tuple(r for r in getattr(regs, name) if r.period_id == "FY2025")
        for name in ("accounts", "addbacks", "segments", "kpis", "facilities")
    }
    run = _run(tmp_path, replace(regs, periods=(undated,), pro_forma=(), **own))
    assert main(["model", "--run", str(run)]) == 0
    data = _model(run)
    assert data["house"]["ev"]["reason"] == "NOT_APPLICABLE"
    assert data["generated_at"].endswith("+00:00")
    text = (run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")
    assert "\nHost-computed Model (`rbot model`): no LTM column, so no house view.\n" in text
    tables = _tables(run)
    assert tables["snapshot.capital_structure_totals"].columns[0] == "line"
    assert tables["snapshot.ebitda_adjustments"].columns[0] == "line"


def test_without_a_ytd_the_pytd_and_ytd_slots_show_older_years(tmp_path: Path) -> None:
    years = _regs(fy={f"FY{y}": {"revenue": 100 + y} for y in (2017, 2018, 2019, 2021, 2022)})
    run = _run(tmp_path, years)
    assert main(["model", "--run", str(run)]) == 0
    rows = _rows(_tables(run)["snapshot.financial_columns"])
    slots = {r["slot"]: r["column_id"] for r in rows}
    assert (slots["PYTD"], slots["YTD"], slots["FY"]) == ("FY:FY2017", "FY:FY2018", "FY:FY2022")


def test_an_add_back_with_no_row_on_the_column_is_not_in_the_adjustments(
    tmp_path: Path,
) -> None:
    regs = example_registers()
    old = next(b for b in regs.addbacks if b.addback_id == "run_rate_cost_savings")
    new = replace(old, addback_id="synergies", label="Synergies")  # a FY2023 row only
    run = _run(tmp_path, replace(regs, addbacks=(*regs.addbacks, new)))
    assert main(["model", "--run", str(run)]) == 0
    lines = [r["line"] for r in _rows(_tables(run)["snapshot.ebitda_adjustments"])]
    assert not any("Synergies" in x for x in lines)
    assert any("Run-rate cost savings" in x for x in lines)


def test_listed_equity_and_no_ev_basis_in_the_totals(tmp_path: Path) -> None:
    equity = table(
        "cp1.equity_value", EQUITY, [["12,000", "2026-10-02", "USD", "MILLIONS", "[C1]"]]
    )
    cp1 = cp1_handoff(example_registers(), [equity])
    run = _run(tmp_path / "a", example_registers(), cp1)
    assert main(["model", "--run", str(run)]) == 0
    assert _model(run)["house"]["ev"]["inputs"]["market_cap"] == "12000"
    totals = {r["line"]: r for r in _rows(_tables(run)["snapshot.capital_structure_totals"])}
    assert totals["Equity"]["basis"] == "listed"
    bare = _run(tmp_path / "b", example_registers(), multiple="—")
    assert main(["model", "--run", str(bare)]) == 0
    totals = {r["line"]: r for r in _rows(_tables(bare)["snapshot.capital_structure_totals"])}
    assert totals["Equity"]["basis"] == "—"


def test_an_uncited_source_is_kept_as_written(tmp_path: Path) -> None:
    lines = cp1_handoff(example_registers()).splitlines()
    lines = [line.replace("| [C3] |", "| S3 |") for line in lines]
    run = _run(tmp_path, example_registers(), "\n".join(lines))
    assert main(["model", "--run", str(run)]) == 0
    revenue = next(x for x in _model(run)["lines"] if x["line_id"] == "revenue")
    fy = next(c for c in revenue["cells"] if c["column_id"] == "FY:FY2025")
    assert fy["sources"] == [
        {"module": "CP-1", "citation_id": None, "source": "S3",
         "locator": "10-K FY2025, Item 8 and quarterly data", "excerpt": None}
    ]  # fmt: skip


def test_missing_front_matter_shows_a_gap_and_the_run_is_required(tmp_path: Path) -> None:
    text = cp1_handoff(example_registers())
    text = text.replace("issuer_id: EGC\n", "").replace("analysis_date: 2026-10-02\n", "")
    run = _run(tmp_path, example_registers(), text)
    assert main(["model", "--run", str(run)]) == 0
    front = parse((run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")).front_matter
    assert (front["issuer_id"], front["analysis_date"]) == ("—", "—")
    with pytest.raises(SystemExit):
        main(["model"])


def test_pf_limitations_carry_their_codes(tmp_path: Path) -> None:
    regs = example_registers()
    pf = regs.pro_forma[0]
    odd = replace(pf, adjustment_id="odd", metric_id="goodwill")  # `rbot model` refuses it
    both = replace(pf, adjustment_id="both", metric_id="ebitda")
    run = _run(tmp_path, replace(regs, pro_forma=(*regs.pro_forma, both)))
    assert main(["model", "--run", str(run)]) == 0
    codes = {row["code"] for row in _rows(_tables(run)["model.limitations"])}
    assert "PF_DOUBLE_COUNT" in codes
    model = credit_model(ModelInputs(replace(regs, pro_forma=(*regs.pro_forma, odd))))
    assert "PF_NOT_APPLIED" in {x.code for x in _model_limitations(model)}


def test_the_maturity_wall_sorts_a_year_by_facility(tmp_path: Path) -> None:
    regs = example_registers()
    facilities = tuple(
        replace(f, maturity_date="2029-06-30") if f.facility_id == "tlb" else f
        for f in regs.facilities
    )
    run = _run(tmp_path, replace(regs, facilities=facilities))
    assert main(["model", "--run", str(run)]) == 0
    rows = _rows(_tables(run)["model.maturity_wall"])
    assert [r["facility_id"] for r in rows if r["fiscal_year"] == "2029"] == [
        "ssn29",
        "sun29",
        "tlb",
    ]


def test_sources_are_cut_only_past_eight() -> None:
    model = credit_model(ModelInputs(example_registers()))
    first = model.lines[0]

    def with_sources(count: int) -> CreditModel:
        sources = tuple(SourceRef(f"[C{n}]", "", "1") for n in range(count))
        line = replace(first, cells=(Cell(Decimal(1), sources=sources), *first.cells[1:]))
        return replace(model, lines=(line,))

    cited = Citations(
        {"CP-1": {f"C{n}": Citation("CP-1", f"C{n}", "f", "p", "x") for n in range(9)}}
    )
    assert sources_cut(with_sources(8), cited) == []
    assert [x.code for x in sources_cut(with_sources(9), cited)] == ["SOURCES_CUT"]
