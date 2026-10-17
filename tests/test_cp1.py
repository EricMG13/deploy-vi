"""CP-1's fixture feeds the Model, and every figure it reports is on its cited line.

`rbot model` on the fixture (the Run Brief from CP-0's fixture; no SSIM EV multiple) gives, on
the PF-LTM to June 30, 2026: total debt 11,705 + 3,000 (NEW-1) - 120 (the revolver repaid) =
14,585; SSIM EBITDA 3,624 + 1,807 - 1,839 = 3,592; PF interest 776 + 213 = 989 and its cover
3,592 / 989 = 3.63x; the SSIM Multiple 14,585 / 3,592 = 4.06x; no EV (no listed equity value).
With CP-1D, adjusted debt adds the 13,157 of financing obligations: 27,742 and 7.72x. The
arranger's 150 of run-rate synergies is registered on the LTM period itself; the Model builds
the LTM from FY2025 and the half-years, then carries this explicitly sourced LTM-only
add-back into Structuring EBITDA (3,742) while SSIM EBITDA excludes it (3,592).
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.contract import load_contract
from rbotlib.handoff import parse
from rbotlib.model.snapshot import display
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check

HANDOFFS = FIXTURES / "handoffs"
CHECKED = {"VERIFIED"}


def _model(tmp_path: Path, *modules: str) -> dict[str, Any]:
    run = make_run(tmp_path / "pack", "20261011-czr-full-credit-assessment")
    (run / "handoffs").mkdir()
    shutil.copy(HANDOFFS / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    for module in modules:
        shutil.copy(HANDOFFS / f"{module}.md", run / "handoffs" / f"{module}.md")
    assert main(["model", "--run", str(run)]) == 0
    data: dict[str, Any] = json.loads((run / "model.json").read_text(encoding="utf-8"))
    return data


def test_the_cp1_fixture_feeds_the_model(tmp_path: Path) -> None:
    data = _model(tmp_path, "CP-1")
    assert data["snapshot_columns"]["LTM"] == "PF:LTM_Q2_2026"
    house = data["house"]
    values = {k: house[k]["value"] for k in ("ssim_ebitda", "pf_interest", "adjusted_debt")}
    assert values == {"ssim_ebitda": "3592", "pf_interest": "989", "adjusted_debt": "14585"}
    assert display(Decimal(house["pf_interest_cover"]["value"]), "MULTIPLE") == "3.63"
    assert display(Decimal(house["ssim_multiple"]["value"]), "MULTIPLE") == "4.06"
    assert (house["ev"]["value"], house["ev"]["reason"]) == (None, "NOT_SOURCED")
    lines = {line["line_id"]: line for line in data["lines"]}
    pf = {c["column_id"]: c for c in lines["addback:run_rate_synergies"]["cells"]}["PF:LTM_Q2_2026"]
    assert (pf["value"], pf["reason"], pf["stated"]) == ("150", None, None)
    assert house["structuring_ebitda"]["value"] == "3742"
    assert data["reconciliation_faults"] == []


def test_cp1d_adds_the_financing_obligations_to_adjusted_debt(tmp_path: Path) -> None:
    house = _model(tmp_path, "CP-1", "CP-1D")["house"]
    assert house["adjusted_debt"]["value"] == "27742"
    assert display(Decimal(house["adjusted_leverage"]["value"]), "MULTIPLE") == "7.72"


def test_downstream_fixtures_use_cp1s_figures() -> None:
    cp1 = parse((HANDOFFS / "CP-1.md").read_text(encoding="utf-8"))
    accounts = cp1.tables["cp1.model_account_register"]
    figure = {(r[0], r[1]): r[2] for r in accounts.rows}
    bridge = cp1.tables["cp1.adjusted_ebitda_bridge"]
    addbacks = {(r[0], r[5]): r[6] for r in bridge.rows}
    cp1b = parse((HANDOFFS / "CP-1B.md").read_text(encoding="utf-8"))
    table = cp1b.tables["cp1b.period_comparison"]
    for row in (dict(zip(table.columns, r, strict=True)) for r in table.rows):
        assert row["current_value"] == figure[(row["metric_id"], row["current_period_id"])]
        assert row["reference_value"] == figure[(row["metric_id"], row["reference_period_id"])]
    cp1d = parse((HANDOFFS / "CP-1D.md").read_text(encoding="utf-8"))
    table = cp1d.tables["cp1d.addback_assessment"]
    for row in (dict(zip(table.columns, r, strict=True)) for r in table.rows):
        assert row["amount"] == addbacks[(row["addback_id"], row["period_id"])]


def _shown(value: str) -> str:
    """A register figure as the filings print it: thousands separated, unsigned."""
    return f"{abs(Decimal(value)):,f}"


def _on(shown: str, line: str) -> bool:
    """`shown` is a whole figure of the line: 807 is not found in 1,807 or 8,070."""
    return re.search(rf"(?<![\d,.]){re.escape(shown)}(?![\d,])", line) is not None


@pytest.mark.corpus
def test_cp1_figures_are_on_their_cited_lines(corpus_pack: Callable[[str], Path]) -> None:
    folder = corpus_pack("czr-2026q2-primary")
    cp1 = parse((HANDOFFS / "CP-1.md").read_text(encoding="utf-8"))
    citations = {r[0]: r for r in cp1.tables["citations"].rows}
    texts = {c[1]: (folder / c[1]).read_text(encoding="utf-8") for c in citations.values()}
    rows = [
        dict(zip(t.columns, r, strict=True))
        for key in ("cp1.model_account_register", "cp1.adjusted_ebitda_bridge")
        for t in [cp1.tables[key]]
        for r in t.rows
    ]
    figures = [
        (r["source_id"], r["value"])
        for r in rows
        if r.get("calculation_status", "VERIFIED") in CHECKED and r["value"] != "\N{EM DASH}"
    ]
    facilities = cp1.tables["cp1.debt_facility_register"]
    figures += [(r[19], r[5]) for r in facilities.rows if r[0] != "NEW-1"]
    assert len(figures) == 73
    for marker, value in figures:
        _, source, _, excerpt = citations[marker.strip("[]")]
        cells = excerpt.replace("\\|", "|")
        lines = [line for line in texts[source].splitlines() if cells in line]
        assert lines and any(_on(_shown(value), line) for line in lines), (marker, value)


def test_a_debt_adjustment_row_reconciles_in_the_model(tmp_path: Path) -> None:
    """Rest review I2: face value on a facility plus the aggregate discount as a DEBT ADJUSTMENT
    row (r14's rule) is the one negative row the Model accepts, and the totals do not move."""
    text = (HANDOFFS / "CP-1.md").read_text(encoding="utf-8")
    tla = "| CEI-TLA | CEI Term Loan A | H1_2026 | Term loan | USD | 618 |"
    assert tla in text
    adjustment = (
        "| DEBT-ADJ | Unamortized discount and debt issuance costs | H1_2026 | DEBT ADJUSTMENT "
        "| USD | -87 | — | — | NOT_STATED | NOT_STATED | Not stated | — | NOT_LEASE "
        "| NOT_STATED | NOT_STATED | — | — | — | — | [C25] | Note 6. Long-Term Debt |\n"
    )
    row = next(line for line in text.splitlines() if line.startswith(tla))
    changed = text.replace(row, row.replace("| 618 |", "| 705 |") + "\n" + adjustment.rstrip("\n"))
    run = tmp_path / "pack" / "rbot-runs" / "20261011-czr-full-credit-assessment"
    (run / "handoffs").mkdir(parents=True)
    shutil.copy(HANDOFFS / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    (run / "handoffs" / "CP-1.md").write_text(changed, encoding="utf-8")
    assert main(["model", "--run", str(run)]) == 0
    data = json.loads((run / "model.json").read_text(encoding="utf-8"))
    assert data["house"]["adjusted_debt"]["value"] == "14585"  # 705 - 87 = 618: unchanged
    assert data["reconciliation_faults"] == []


def test_the_cp1_prompt_names_the_debt_adjustment_row_and_the_lease_metrics() -> None:
    """Rest review I2: the words r14 gave CP-1 and the Model's spelling are in the prompt."""
    prompt = (Path(__file__).parent.parent / "rbot" / "modules" / "CP-1" / "MODULE.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "`DEBT ADJUSTMENT` row (`facility_type` `DEBT ADJUSTMENT`",
        "Only that adjustment row may be negative",
        "plus any `DEBT ADJUSTMENT` row, equals `total_debt`",
        "`operating_lease_cost` is the lease cost recognised inside operating expenses",
        "under IFRS 16 only short-term and variable lease expense",
        "`interest_paid_in_financing` the interest paid that the issuer classified in financing",
    ):
        assert phrase in prompt, phrase


def test_a_figure_is_found_only_as_a_whole_number() -> None:
    assert _on("807", "Revenue 807 1,001") and not _on("807", "Revenue 1,807")
    assert not _on("807", "Revenue 8,070") and not _on("807", "rate 0.807")


def _without_rows(text: str, table_id: str) -> str:
    """The Handoff with every data row of one table removed (header and separator stay)."""
    out, inside, seen = [], False, 0
    for line in text.splitlines():
        if line.startswith("<!-- table:"):
            inside, seen = line == f"<!-- table: {table_id} -->", 0
        elif inside and line.startswith("|"):
            seen += 1
            if seen > 2:
                continue
        out.append(line)
    return "\n".join(out) + "\n"


def test_an_empty_cp1_bridge_gives_an_empty_assessment_that_validates_and_runs(
    tmp_path: Path, rules: Rules
) -> None:
    """Rest review I4: no `NONE` row with an invented verdict and amount."""
    cp1 = _without_rows((HANDOFFS / "CP-1.md").read_text("utf-8"), "cp1.adjusted_ebitda_bridge")
    cp1d = _without_rows((HANDOFFS / "CP-1D.md").read_text("utf-8"), "cp1d.addback_assessment")
    contract = load_contract(RBOT_ROOT / "modules" / "CP-1D" / "contract.json", rules)
    assert check(cp1d, contract, rules) == (0, [])
    run = tmp_path / "pack" / "rbot-runs" / "20261011-czr-full-credit-assessment"
    (run / "handoffs").mkdir(parents=True)
    shutil.copy(HANDOFFS / "CP-0.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    (run / "handoffs" / "CP-1.md").write_text(cp1, encoding="utf-8")
    (run / "handoffs" / "CP-1D.md").write_text(cp1d, encoding="utf-8")
    assert main(["model", "--run", str(run)]) == 0


def _followup_null(text: str, table_id: str, column: str, value: str) -> str:
    table = parse(text).tables[table_id]
    old = list(table.rows[0])
    new = list(old)
    new[table.columns.index(column)] = value
    return text.replace("| " + " | ".join(old) + " |", "| " + " | ".join(new) + " |", 1)


def test_cp1d_can_carry_a_null_amount_with_a_gap(tmp_path: Path) -> None:
    from rbotlib.model.house_inputs import assessments
    from rbotlib.rules import load_rules

    rules = load_rules()
    cp1 = (FIXTURES / "handoffs/CP-1.md").read_text("utf-8")
    cp1 = _followup_null(cp1, "cp1.adjusted_ebitda_bridge", "value", "—")
    cp1d = (FIXTURES / "handoffs/CP-1D.md").read_text("utf-8")
    cp1d = _followup_null(cp1d, "cp1d.addback_assessment", "amount", "—")
    cp1d = cp1d.replace(
        "## Gaps", "## Gaps\n\n- The first add-back amount is not disclosed; it is not zero."
    )
    for module, text in (("CP-1", cp1), ("CP-1D", cp1d)):
        contract = load_contract(RBOT_ROOT / "modules" / module / "contract.json", rules)
        assert check(text, contract, rules) == (0, [])
    h = parse(cp1d)
    assert h.tables["cp1d.addback_assessment"].rows[0][2] == "—"
    assert len(assessments(h.tables)) > 0
    from test_fit import _run

    from rbotlib.cli import main

    folder = _run(tmp_path)
    for module, text in (("CP-1", cp1), ("CP-1D", cp1d)):
        (folder / "handoffs" / f"{module}.md").write_text(text, "utf-8")
    assert main(["model", "--run", str(folder)]) == 0
    data = json.loads((folder / "model.json").read_text())
    bridge = parse(cp1).tables["cp1.adjusted_ebitda_bridge"]
    first = dict(zip(bridge.columns, bridge.rows[0], strict=True))
    row = next(
        line for line in data["lines"] if line["line_id"] == "addback:" + first["addback_id"]
    )
    cell = next(
        cell for cell in row["cells"] if cell["column_id"].endswith(":" + first["period_id"])
    )
    assert (cell["value"], cell["reason"]) == (None, "NOT_STATED")
