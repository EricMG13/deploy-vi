"""Interfaces spec sections 1 and 2 for the modules Plan 05 ships, as test data.

`TABLES[module]` lists each table in section 2 order: id, minimum rows, columns (`name*` is
critical, `name:scale` names a rules.json scale) and section 2's consumers. `INPUTS[module]`
is section 1: required and optional Handoff inputs, source classes and Run Brief fields. A
consumer or input that has no contract yet (a later plan's module) is left out of the
contract until that plan lands (Plan 04 Decision 5); `present_consumers` applies that rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rbotlib.catalog import REPORT
from rbotlib.contract import Contract
from rbotlib.rules import Rules


@dataclass(frozen=True)
class TableSpec:
    id: str
    min_rows: int
    columns: str
    consumers: str

    def column_tuples(self) -> list[tuple[str, bool, str | None]]:
        out = []
        for spec in self.columns.split():
            name, _, scale = spec.partition(":")
            out.append((name.rstrip("*"), name.endswith("*"), scale or None))
        return out


@dataclass(frozen=True)
class Inputs:
    required: str
    optional: str
    sources: str
    run_brief: str


TABLES: dict[str, list[TableSpec]] = {}
INPUTS: dict[str, Inputs] = {}


def present_consumers(spec: TableSpec, modules: Path, rules: Rules) -> list[str]:
    """Section 2's consumers that exist now: a module with a folder, a host step, the Report."""
    readers = {p.name for p in modules.iterdir() if p.is_dir()}
    readers |= set(rules.host_producers) | {REPORT}
    return [c for c in spec.consumers.split() if c in readers]


def handoff_inputs(contract: Contract) -> tuple[list[str], list[str]]:
    required = contract.handoff_inputs(required_only=True)
    optional = [h for h in contract.handoff_inputs() if h not in required]
    return required, optional


TABLES["CP-6"] = [
    TableSpec(
        "snapshot.recommendation",
        3,
        "strategy*:strategy recommendation*:recommendation basis*:depth_basis rationale* cite*",
        "REPORT CP-8",
    ),
    TableSpec(
        "snapshot.instrument_recommendation",
        1,
        (
            "facility_id* instrument* recommendation*:recommendation valuation*:valuation "
            "rationale* cite*"
        ),
        "REPORT CP-8",
    ),
    TableSpec("snapshot.thesis", 1, "thesis* cite*", "REPORT CP-8"),
    TableSpec(
        "snapshot.catalysts",
        1,
        "date_or_window* event* direction*:delta_direction watch_trigger* cite*",
        "REPORT CP-8",
    ),
    TableSpec(
        "cp6.challenge",
        2,
        "claim* counter_evidence* resolution* what_would_change_view* cite*",
        "REPORT CP-8",
    ),
    TableSpec(
        "cp6.portfolio_recommendation",
        0,
        (
            "portfolio_id* strategy*:strategy instrument* uncapped*:recommendation "
            "cap*:recommendation final*:recommendation fit_verdict*:portfolio_fit reason*"
        ),
        "REPORT CP-8",
    ),
]
INPUTS["CP-6"] = Inputs(
    "CP-0 CP-3 CP-5",
    (
        "CP-2 CP-L10 FIT CP-1A CP-1B CP-1C CP-1D CP-2A CP-2D CP-2E CP-2G PROJECTION CP-2H CP-3C "
        "CP-3D CP-4 CP-4C CP-DR"
    ),
    "",
    "analyst as_of_date depth portfolios",
)


TABLES["CP-5"] = [
    TableSpec(
        "cp5.findings",
        0,
        (
            "finding_id* severity*:severity module_id* kind*:finding_kind description* "
            "required_fix* status*:finding_status"
        ),
        "CP-6 CP-8 REPORT",
    ),
    TableSpec(
        "cp5.limitations",
        0,
        "module_id* limitation* effect_on_decision* source_that_would_lift*",
        "REPORT CP-6 CP-8",
    ),
    TableSpec(
        "cp5.module_status",
        1,
        "module_id* qa_status*:qa_status traceability*:traceability note",
        "REPORT CP-6 CP-8",
    ),
]
INPUTS["CP-5"] = Inputs(
    "CP-0",
    (
        "CP-1 CP-1A CP-1B CP-1C CP-1D CP-2 CP-2A CP-2D CP-2E CP-2G CP-2H CP-3 CP-3C CP-3D CP-4 "
        "CP-4C CP-L10 CP-DR MODEL PROJECTION FIT"
    ),
    "issuer market portfolio",
    "pathway depth",
)


TABLES["CP-0"] = [
    TableSpec(
        "cp0.source_inventory",
        1,
        (
            "file* class*:source_class document_type*:document_type entity_named* "
            "entity_match*:yes_no period_covered document_date readable*:yes_no image_read*:yes_no "
            "pages sha256* note"
        ),
        "CP-1 CP-1A CP-DR CP-5 RUN_BRIEF REPORT",
    ),
    TableSpec(
        "cp0.run_brief_prefill",
        1,
        "field* tranche_id value status*:brief_status cite",
        "RUN_BRIEF REPORT",
    ),
    TableSpec(
        "cp0.research_questions",
        0,
        "question_id* question* why_it_matters* consumer_module* evidence_needed*",
        "RUN_BRIEF CP-DR REPORT",
    ),
    TableSpec(
        "cp0.prior_case",
        0,
        "file* report_date* run_id* pathway* depth* offered*:yes_no",
        "RUN_BRIEF CP-8 REPORT",
    ),
    TableSpec(
        "cp0.portfolios",
        0,
        (
            "portfolio_id* portfolio_name* strategy*:strategy positions_file* limits_file* "
            "as_of_date"
        ),
        "RUN_BRIEF FIT REPORT",
    ),
]
INPUTS["CP-0"] = Inputs("", "", "issuer market portfolio", "")
