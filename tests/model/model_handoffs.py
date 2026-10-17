"""Write CP-1, CP-1D and Run Brief Handoffs from typed rows, for the Model's tests.

`cp1_handoff` writes CP-1's Model-input tables (interfaces spec §2.2) from a
`Cp1Registers`; each `SourceRef` id `S<n>` becomes the marker `[C<n>]` with a
citations row. `run_folder` lays a run folder out as `rbot model` reads it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from pathlib import Path

from rbotlib.model.frame import SourceRef
from rbotlib.model.registers import Cp1Registers

GAP = "\N{EM DASH}"
_SOURCE = re.compile(r"^S(\d+)$")

PERIOD_COLUMNS = ["period_id", "fiscal_year", "fiscal_quarter", "period_type", "start_date"]
PERIOD_COLUMNS += ["end_date", "day_count", "currency", "unit", "component_period_ids"]
ACCOUNT_COLUMNS = ["metric_id", "period_id", "value", "calculation_status"]
ADDBACK_COLUMNS = ["addback_id", "addback_label", "addback_classification", "realization_status"]
ADDBACK_COLUMNS += ["display_priority", "period_id", "value"]
SEGMENT_COLUMNS = ["segment_id", "segment_name", "segment_type", "display_priority"]
SEGMENT_COLUMNS += ["period_id", "revenue"]
KPI_COLUMNS = ["kpi_id", "kpi_label", "display_priority", "period_id", "value", "unit"]
KPI_COLUMNS += ["value_type"]
FACILITY_COLUMNS = ["facility_id", "facility_name", "period_id", "facility_type", "currency"]
FACILITY_COLUMNS += ["carrying_value", "drawn_amount", "commitment", "secured_status"]
FACILITY_COLUMNS += ["seniority", "margin_or_coupon", "maturity_date", "lease_classification"]
FACILITY_COLUMNS += ["rate_type", "reference_rate", "spread_bps", "floor_bps", "fixed_rate"]
FACILITY_COLUMNS += ["annual_amortisation"]
PRO_FORMA_COLUMNS = ["adjustment_id", "label", "period_id", "effective_date", "classification"]
PRO_FORMA_COLUMNS += ["metric_id", "value"]
SOURCE_COLUMNS = ["source_id", "source_locator"]


def _text(value: object) -> str:
    if value is None:
        return GAP
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _marker(source: SourceRef | None, cited: dict[str, SourceRef]) -> list[str]:
    if source is None:
        return [GAP, GAP]
    found = _SOURCE.match(source.source_id)
    marker = f"[C{found.group(1)}]" if found else source.source_id
    cited.setdefault(marker, source)
    return [marker, source.source_locator or GAP]


def table(table_id: str, columns: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    lines = [f"<!-- table: {table_id} -->", "", "| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return [*lines, ""]


def handoff(
    module_id: str, tables: Sequence[list[str]], citations: Mapping[str, tuple[str, str, str]]
) -> str:
    """A Handoff: front matter, the four sections, the tables and citations
    (`[C<n>]` -> (source, locator, excerpt)), every citation cited in a cell."""
    lines = ["---", f"module_id: {module_id}", "run_id: 20261011-egc-full-credit-assessment"]
    lines += ["issuer_id: EGC", "analysis_date: 2026-10-02", "qa_status: Pass"]
    lines += ["inputs: CP-0", "---", "", "## Analysis", "", f"{module_id} fixture.", ""]
    lines += ["## Tables", ""]
    for block in tables:
        lines += block
    lines += ["## Gaps", "", "- None.", "", "## Citations", ""]
    rows = [[m.strip("[]"), *citations[m]] for m in citations]
    lines += table("citations", ["id", "source", "locator", "excerpt"], rows)
    return "\n".join(lines)


def cp1_handoff(regs: Cp1Registers, extra: Sequence[list[str]] = ()) -> str:
    cited: dict[str, SourceRef] = {}
    periods = [
        [
            p.period_id,
            p.fiscal_year,
            p.fiscal_quarter or GAP,
            p.period_type,
            _text(p.start_date),
            _text(p.end_date),
            _text(p.day_count),
            p.currency,
            p.unit,
            "; ".join(p.component_period_ids) or GAP,
        ]
        for p in regs.periods
    ]
    accounts = [
        [a.metric_id, a.period_id, _text(a.value), a.calculation_status, *_marker(a.source, cited)]
        for a in regs.accounts
    ]
    addbacks = [
        [
            b.addback_id,
            b.label,
            b.classification,
            b.realization_status,
            str(b.display_priority),
            b.period_id,
            _text(b.value),
            *_marker(b.source, cited),
        ]
        for b in regs.addbacks
    ]
    segments = [
        [
            s.segment_id,
            s.segment_name,
            s.segment_type,
            str(s.display_priority),
            s.period_id,
            _text(s.revenue),
            *_marker(s.source, cited),
        ]
        for s in regs.segments
    ]
    kpis = [
        [
            k.kpi_id,
            k.kpi_label,
            str(k.display_priority),
            k.period_id,
            _text(k.value),
            k.unit,
            k.value_type,
            *_marker(k.source, cited),
        ]
        for k in regs.kpis
    ]
    facilities = [
        [
            f.facility_id,
            f.facility_name,
            f.period_id,
            f.facility_type,
            f.currency,
            _text(f.carrying_value),
            _text(f.drawn_amount),
            _text(f.commitment),
            f.secured_status,
            f.seniority,
            f.margin_or_coupon or GAP,
            _text(f.maturity_date),
            f.lease_classification,
            f.rate_type,
            f.reference_rate,
            _text(f.spread_bps),
            _text(f.floor_bps),
            _text(f.fixed_rate),
            _text(f.annual_amortisation),
            *_marker(f.source, cited),
        ]
        for f in regs.facilities
    ]
    pro_forma = [
        [
            a.adjustment_id,
            a.label,
            a.period_id,
            "2026-07-01",
            a.classification,
            a.metric_id,
            _text(a.value),
            *_marker(a.source, cited),
        ]
        for a in regs.pro_forma
    ]
    blocks = [
        table("cp1.model_period_register", PERIOD_COLUMNS, periods),
        table("cp1.model_account_register", ACCOUNT_COLUMNS + SOURCE_COLUMNS, accounts),
        table("cp1.adjusted_ebitda_bridge", ADDBACK_COLUMNS + SOURCE_COLUMNS, addbacks),
        table("cp1.segment_revenue_schedule", SEGMENT_COLUMNS + SOURCE_COLUMNS, segments),
        table("cp1.operating_kpi_schedule", KPI_COLUMNS + SOURCE_COLUMNS, kpis),
        table("cp1.debt_facility_register", FACILITY_COLUMNS + SOURCE_COLUMNS, facilities),
        table("cp1.pro_forma_adjustment_register", PRO_FORMA_COLUMNS + SOURCE_COLUMNS, pro_forma),
        *extra,
    ]
    citations = {
        m: (f"fixture-{s.source_id}.txt", s.source_locator, s.cell_text) for m, s in cited.items()
    }
    return handoff("CP-1", blocks, citations)


def run_brief(ssim_ev_multiple: str = "8.5x", tranches: Sequence[str] = ()) -> str:
    header = ["run_id", "issuer", "issuer_id", "as_of_date", "objective", "analyst", "pathway"]
    header += ["depth", "primary", "currency", "unit", "morningstar_issuer_id"]
    header += ["ssim_ev_multiple_x", "report_date"]
    row = [
        "20261011-egc-full-credit-assessment",
        "Example Gaming Co.",
        "EGC",
        "2026-10-02",
        "Full credit assessment",
        "Analyst",
        "FULL_CREDIT_ASSESSMENT",
        "full",
        "Yes" if tranches else "No",
        "USD",
        "MILLIONS",
        GAP,
        ssim_ev_multiple,
        "2026-10-11",
    ]
    summary = [
        [
            t,
            "Example Gaming Co.",
            GAP,
            "Term loan",
            "1L Term Loan",
            "Acquisition",
            "600",
            "USD",
            "MILLIONS",
            "S+300-325",
            "Initial talk",
            "99.0",
            "2033-06-30",
            GAP,
            GAP,
            GAP,
            "Sourced",
            GAP,
            "[C1]",
        ]
        for t in tranches
    ]
    columns = ["tranche_id", "borrower", "bloomberg_id", "instrument", "debt_type"]
    columns += ["use_of_proceeds", "size", "currency", "unit", "price_talk", "talk_stage", "oid"]
    columns += ["maturity_date", "expected_ratings", "cr_score", "commitment_date", "status"]
    columns += ["analyst_value", "cite"]
    blocks = [
        table("snapshot.run_header", header, [row]),
        table("snapshot.transaction_summary", columns, summary),
    ]
    citations = {"[C1]": ("term-sheet.txt", "p.1", "S+300-325")} if tranches else {}
    return handoff("RUN_BRIEF", blocks, citations)


def run_folder(root: Path, cp1: str, brief: str, cp1d: str | None = None) -> Path:
    run = root / "rbot-runs" / "20261011-egc-full-credit-assessment"
    (run / "handoffs").mkdir(parents=True)
    (run / "handoffs" / "CP-1.md").write_text(cp1, encoding="utf-8")
    (run / "run-brief.md").write_text(brief, encoding="utf-8")
    if cp1d is not None:
        (run / "handoffs" / "CP-1D.md").write_text(cp1d, encoding="utf-8")
    return run
