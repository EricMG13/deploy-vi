"""The MODEL step's §3.2 tables from the Model and its house view."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff

from rbotlib.handoff import Table, parse
from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.citations import Citations, citation_rows
from rbotlib.model.house import house_view
from rbotlib.model.house_inputs import BriefFields, HouseInputs, Identity
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.snapshot import Context, build_tables, display, maturity_year

GAP = "—"


@pytest.mark.parametrize(
    ("text", "year"),
    [("2028-01-26", 2028), ("2028", 2028), ("not stated", None), (None, None), ("28", None)],
)
def test_a_maturity_falls_in_its_date_or_stated_year(text: str | None, year: int | None) -> None:
    assert maturity_year(text) == year


def _context(regs: Cp1Registers | None = None, tranches: frozenset[str] = frozenset()) -> Context:
    """The registers (the example's by default) read back from a CP-1
    Handoff, so each source is a `[C<n>]` marker; their Model and house view.
    Registers without periods are used as they are (no Handoff holds them)."""
    regs = regs or example_registers()
    citations = Citations({})
    if regs.periods:
        written = parse(cp1_handoff(regs))
        regs = cp1_registers(written.tables)
        citations = Citations({"CP-1": citation_rows("CP-1", written.tables["citations"])})
    identity = Identity("tlb", "Term Loan B", "BL0001", "Ba3 / BB / —", "[C4]")
    brief = BriefFields("R", Decimal("8.5"), bool(tranches), tranches)
    inputs = HouseInputs({"tlb": identity}, None, (), (), brief)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    return Context(model, regs, house_view(model, regs, inputs), inputs, citations)


def test_the_unsecured_total_is_exact_past_28_digits() -> None:
    big = Decimal("512345678901234567.0123456789")  # the largest the reader takes
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=big) if f.facility_id in {"sun29", "sun32"} else f
        for f in regs.facilities
    )
    ctx = _context(replace(regs, facilities=facilities))
    totals = _by(build_tables(ctx)[0]["snapshot.capital_structure_totals"], "line")
    assert totals["Unsecured debt"]["amount"] == "1024691357802470824.0246913578"  # + finl, disc


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def _by(table: Table, key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in _rows(table)}


@pytest.mark.parametrize(
    ("value", "unit", "shown"),
    [
        (Decimal("1234.5"), "MONEY", "1234.5"),
        (Decimal("0.123456"), "PERCENT", "12.3"),
        (Decimal("0.12350"), "PERCENT", "12.4"),
        (Decimal("0.12250"), "PERCENT", "12.2"),
        (Decimal("3.5920859794"), "MULTIPLE", "3.59"),
        (Decimal("-0.001"), "MULTIPLE", "0.00"),
        (Decimal("41.25"), "SHARE", "41.2"),
        (Decimal("45.06"), "DAYS", "45.1"),
        (Decimal("0.0380"), "RATE", "3.80"),
        (None, "MONEY", GAP),
    ],
)
def test_display_rounds_ratios_half_even_and_never_amounts(
    value: Decimal | None, unit: str, shown: str
) -> None:
    assert display(value, unit) == shown


def test_financials_follow_the_template_mapping() -> None:
    tables, _ = build_tables(_context())
    financials = tables["snapshot.financials"]
    assert len(financials.rows) == 32
    rows = _by(financials, "line")
    assert rows["Revenue"]["line_id"] == "revenue"
    assert rows["Revenue"]["unit_label"] == "USD m"
    assert (rows["Revenue"]["fy"], rows["Revenue"]["ltm"]) == ("11519", "11654")
    assert rows["Revenue %Δ"]["fy"] == display(Decimal(11519) / Decimal(11165) - 1, "PERCENT")
    assert rows["EBITDA (SSIM basis)"]["ltm"] == "4094"
    assert rows["Cash"]["ltm"] == "950"
    assert rows["Cash Interest"]["ltm"] == "-904"
    assert rows["Senior debt"]["line_id"] == "secured_debt"
    assert rows["Total Leverage"]["unit_label"] == "x"
    assert rows["FFO"]["ltm"] == GAP  # NOT_APPLICABLE on the PF-LTM
    assert rows["FFO"]["cite"] == "calc: model.json line ffo"


def test_capital_structure_rows_join_identity_and_label_talk() -> None:
    ctx = _context(tranches=frozenset({"tlb"}))
    tables, _ = build_tables(ctx)
    rows = _by(tables["snapshot.capital_structure"], "facility_id")
    tlb = rows["tlb"]
    assert (tlb["bloomberg_id"], tlb["facility_ratings"]) == ("BL0001", "Ba3 / BB / —")
    assert tlb["spread_or_coupon"] == "+275 bp (talk)"
    assert (tlb["outstanding"], tlb["rank"], tlb["secured"]) == ("2316", "Senior secured", "Yes")
    assert tlb["structuring_multiple_x"] == display(Decimal(5916) / Decimal(4134), "MULTIPLE") + "x"
    assert rows["ssn31"]["outstanding"] == "1600"
    assert rows["sun29"]["secured"] == "No"
    assert (
        rows["sun29"]["ssim_multiple_x"]
        == display(Decimal(13016) / Decimal(4094), "MULTIPLE") + "x"
    )
    assert tlb["column_basis"] == "PF-LTM"
    assert tlb["cite"] == "[C1]"
    assert rows["ssn31"]["cite"] == "[C1] [C2]"


def test_capital_structure_totals() -> None:
    tables, _ = build_tables(_context())
    rows = _by(tables["snapshot.capital_structure_totals"], "line")
    assert list(rows) == [
        "Senior secured debt",
        "Unsecured debt",
        "Total debt",
        "Cash",
        "Equity",
        "EV",
        "PF interest",
        "PF interest cover",
    ]
    assert rows["Total debt"]["amount"] == "14706"
    assert rows["Unsecured debt"]["amount"] == str(3600 + 3500 + 1600 + 260 - 170)  # + finl, disc
    assert rows["Cash"]["structuring_multiple_x"] == GAP
    assert rows["EV"]["pct_ev_pct"] == "100.0%"
    assert rows["PF interest"]["amount"] == "904"
    cover = rows["PF interest cover"]
    assert cover["ssim_multiple_x"] == display(Decimal(4094) / Decimal(904), "MULTIPLE") + "x"
    assert (
        cover["structuring_multiple_x"] == display(Decimal(4094) / Decimal(904), "MULTIPLE") + "x"
    )


def test_ebitda_adjustments_bridge_reported_to_ssim() -> None:
    tables, _ = build_tables(_context())
    rows = _rows(tables["snapshot.ebitda_adjustments"])
    assert [(r["line"], r["kind"], r["amount"], r["realization_status"]) for r in rows] == [
        ("Reported EBITDA", "Total", "3904", GAP),
        ("Add-back: Restructuring (realised)", "Add-back", "32", "REALIZED"),
        ("Add-back: Stock-based compensation (realised)", "Add-back", "92", "REALIZED"),
        ("Add-back: Transaction costs (realised)", "Add-back", "21", "REALIZED"),
        ("Add-back: Run-rate cost savings (unrealised), excluded", "Add-back", "40", "UNREALIZED"),
        ("PF adjustment: Silverlake Resort LTM adjusted EBITDA", "Add-back", "45", GAP),
        ("Structuring EBITDA", "Total", "4134", GAP),
        (
            "Add-back: Run-rate cost savings (unrealised), excluded",
            "Unrealized add-back",
            "-40",
            "UNREALIZED",
        ),
        ("SSIM EBITDA", "Total", "4094", GAP),
    ]
    amounts = [Decimal(r["amount"]) for r in rows]
    assert sum(amounts[:6], Decimal(0)) == amounts[6]
    assert amounts[6] + amounts[7] == amounts[8]


def test_house_summary_metrics_and_maturity_wall() -> None:
    tables, limits = build_tables(_context())
    house = _by(tables["model.house"], "item")
    assert house["Structuring EBITDA"]["value"] == "4134"
    assert house["SSIM Multiple"]["unit_label"] == "x"
    assert house["EV"]["components"] == "net_debt; adjusted_ebitda"
    metrics = tables["model.metrics"]
    assert len(metrics.rows) == 19 and metrics.rows[-1][0] == "adjusted_ebitda_growth"
    summary = _by(tables["model.summary"], "line_id")
    assert {"fac:tlb", "rank:Senior secured", "addback:restructuring"} <= set(summary)
    assert (summary["cash_closing"]["ltm"], summary["cash_closing"]["pf_ltm"]) == ("1000", "950")
    wall = _rows(tables["model.maturity_wall"])
    assert [(r["fiscal_year"], r["facility_id"]) for r in wall][:3] == [
        ("2027", "sub27"),
        ("2029", "ssn29"),
        ("2029", "sun29"),
    ]
    assert "rcf" not in {r["facility_id"] for r in wall}  # nothing outstanding
    assert ("MATURITY_NOT_STATED", "finl: no maturity date") in limits


def test_no_ltm_leaves_the_house_tables_empty() -> None:
    tables, _ = build_tables(_context(replace(example_registers(), periods=())))
    for table_id in (
        "snapshot.capital_structure",
        "snapshot.capital_structure_totals",
        "snapshot.ebitda_adjustments",
        "model.house",
        "model.maturity_wall",
    ):
        assert tables[table_id].rows == [], table_id
