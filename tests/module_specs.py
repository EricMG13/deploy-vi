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


TABLES["CP-3"] = [
    TableSpec(
        "snapshot.instrument_levels",
        1,
        (
            "facility_id* instrument* level_basis*:level_basis level_date bid ask mid "
            "spread_or_coupon* metric_basis*:metric_basis yield_or_dm* oid valuation*:valuation "
            "rationale* cite*"
        ),
        "REPORT CP-6 FIT CP-8 CP-5",
    ),
    TableSpec(
        "snapshot.relative_value",
        1,
        (
            "block*:rv_block name* bloomberg_id ratings size currency unit:unit margin_or_coupon "
            "maturity_date seniority price chg_1m chg_ytd yield_pct* spread_or_dm_bps* "
            "market_value level_date* cite*"
        ),
        "REPORT CP-6 CP-8",
    ),
    TableSpec(
        "cp3.talk_valuation",
        0,
        (
            "facility_id* talk_stage*:price_talk_stage talk_low* talk_mid* talk_high* oid* "
            "metric_basis*:metric_basis implied_low* implied_mid* implied_high* comparable_level* "
            "comparable_basis* verdict*:valuation cite*"
        ),
        "CP-6 FIT REPORT CP-8",
    ),
    TableSpec(
        "cp3.compensation",
        1,
        (
            "facility_id* structural_rank* recovery_sensitivity*:ordinal "
            "compensation_vs_risk*:compensation comparables* cite*"
        ),
        "CP-6 REPORT CP-5",
    ),
    TableSpec(
        "cp3.security_preference",
        1,
        "facility_id* preference*:preference key_reason* monitoring_trigger* cite*",
        "CP-6 FIT REPORT CP-8",
    ),
]
INPUTS["CP-3"] = Inputs(
    "CP-0 CP-1 MODEL",
    "CP-1A CP-1C CP-1D CP-2 CP-L10 CP-2A CP-2E CP-2G PROJECTION CP-2H CP-3C CP-3D CP-4 CP-4C CP-DR",
    "issuer market",
    "as_of_date primary transaction_summary",
)


TABLES["CP-2"] = [
    TableSpec(
        "snapshot.credit_view",
        1,
        (
            "credit_score*:credit_score credit_direction*:credit_direction "
            "sector_outlook*:sector_outlook primary_support* primary_downside* "
            "confidence*:confidence basis*:depth_basis cite*"
        ),
        "REPORT CP-2A CP-2D CP-2E CP-2G CP-2H CP-3 CP-3C CP-3D CP-4 CP-4C CP-5 CP-6 CP-8",
    ),
    TableSpec(
        "snapshot.strengths_weaknesses",
        2,
        "kind*:sw_kind label* text* cite*",
        "REPORT CP-6 CP-8 CP-5",
    ),
    TableSpec(
        "cp2.drivers",
        3,
        (
            "rank* driver* evidence* risk_mechanism* credit_implication* direction*:risk_direction"
            " confidence*:confidence cite*"
        ),
        "CP-2A CP-2G CP-3 CP-6 CP-5 CP-3C CP-4C",
    ),
    TableSpec(
        "cp2.watch_items",
        1,
        "trigger* threshold_or_signal* why_it_matters* credit_impact* cite",
        "CP-6 CP-2A CP-2H CP-8 REPORT",
    ),
]
INPUTS["CP-2"] = Inputs(
    "CP-0 CP-1 CP-1A MODEL", "CP-1B CP-1C CP-1D CP-DR", "issuer", "issuer as_of_date objective"
)


TABLES["CP-1D"] = [
    TableSpec(
        "cp1d.addback_assessment",
        1,
        (
            "addback_id* period_id* amount* currency* unit*:unit category* "
            "house_realization_status*:realization_status verdict*:addback_verdict rationale* "
            "recurrence* cite*"
        ),
        "MODEL CP-2 CP-4 CP-6 REPORT",
    ),
    TableSpec(
        "cp1d.cash_conversion",
        1,
        (
            "period_id* adjusted_ebitda* cfo* conversion_pct* currency* unit*:unit explanation* "
            "credit_implication* cite*"
        ),
        "CP-2 CP-2G CP-6 REPORT",
    ),
    TableSpec(
        "cp1d.debt_like_items",
        0,
        "item* amount* currency* unit*:unit period_id* treatment*:debt_like_treatment basis* cite*",
        "MODEL CP-2 CP-3 CP-4C REPORT",
    ),
]
INPUTS["CP-1D"] = Inputs("CP-0 CP-1", "CP-1A CP-1B", "issuer", "as_of_date")


TABLES["CP-1B"] = [
    TableSpec("snapshot.historical_performance", 1, "text* cite*", "REPORT CP-2 CP-L10 CP-8"),
    TableSpec(
        "cp1b.period_comparison",
        3,
        (
            "metric_id* current_period_id* reference_period_id* comparison_basis*:comparison_basis"
            " current_value* reference_value* abs_change pct_change_pct currency* unit*:unit "
            "restatement*:yes_no perimeter_change*:yes_no cite*"
        ),
        "CP-2 CP-L10 CP-2G CP-8 REPORT",
    ),
    TableSpec(
        "cp1b.variance_drivers",
        1,
        "metric_id* management_driver* analyst_driver* credit_implication* cite*",
        "CP-2 CP-L10 CP-2G REPORT",
    ),
    TableSpec(
        "cp1b.kpi_changes",
        0,
        "kpi_id* current_value* reference_value* change* unit* trend*:delta_direction cite*",
        "CP-2 CP-2G REPORT",
    ),
    TableSpec(
        "cp1b.guidance_vs_delivery",
        0,
        (
            "metric_id* benchmark_source* benchmark_value* actual_value* variance* currency* "
            "unit*:unit credit_implication* cite*"
        ),
        "CP-2 CP-2G CP-6 REPORT",
    ),
    TableSpec(
        "cp1b.signals",
        0,
        "signal* evidence* severity*:severity credit_implication* cite*",
        "CP-2 CP-2A CP-6 REPORT",
    ),
]
INPUTS["CP-1B"] = Inputs("CP-0 CP-1", "CP-1A", "issuer", "as_of_date")


TABLES["CP-1A"] = [
    TableSpec(
        "snapshot.company_profile",
        1,
        (
            "morningstar_issuer_id sector* country* shareholders* management* corp_rating_moodys "
            "corp_rating_sp corp_rating_fitch outlook_moodys outlook_sp outlook_fitch "
            "sponsor_quality*:sponsor_quality listed*:yes_no ticker cite*"
        ),
        "REPORT CP-2 CP-2H CP-3 CP-6 CP-L10 FIT CP-8",
    ),
    TableSpec("snapshot.business_description", 1, "description* cite*", "REPORT CP-2 CP-DR CP-L10"),
    TableSpec(
        "cp1a.business_facts",
        3,
        "item* fact* risk_mechanism* credit_implication* evidence_quality*:evidence_quality cite*",
        "CP-2 CP-2A CP-DR CP-3 CP-L10",
    ),
    TableSpec(
        "cp1a.ownership_governance",
        1,
        "topic* fact* risk_direction*:risk_direction credit_implication* cite*",
        "CP-2 CP-4 CP-6 CP-L10",
    ),
    TableSpec(
        "cp1a.transactions_events",
        1,
        "event_date* event* status* credit_relevance* perimeter_change*:yes_no cite*",
        "CP-2 CP-2A CP-3C CP-4C CP-6 CP-8 CP-L10 CP-DR",
    ),
    TableSpec(
        "cp1a.ratings_register",
        0,
        "agency* scope* rating* outlook* rating_date* rationale cite*",
        "CP-2H CP-3 CP-2 REPORT",
    ),
]
INPUTS["CP-1A"] = Inputs(
    "CP-0", "CP-1", "issuer market", "issuer as_of_date objective morningstar_issuer_id"
)
