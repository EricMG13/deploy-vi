# Model input enumerations

The values `rbot model` accepts in CP-1's and CP-1D's enumerated columns (interfaces spec §2.2), copied from caos `caos/methodology/model_inputs.py` at `5c3cd52f`. A cell names a value on case and separators (`_`, `-` and whitespace alike: `super senior` is `SUPER_SENIOR`) and reads as the spelling below. In a **closed** column any other text is refused, with the table, row and column named (`ModelInputError`, exit 1). An **open** column reads any other text in upper case. `tests/model/test_enums_doc.py` fails when this page and `rbotlib/model/registers.py` or `house_inputs.py` disagree.

| table | column | values | kind |
|---|---|---|---|
| `cp1.model_period_register` | `period_type` | `QUARTER`, `YTD`, `FY`, `LTM`, `PERIOD_END` | closed |
| `cp1.model_period_register` | `unit` | `UNITS`, `THOUSANDS`, `MILLIONS` | closed |
| `cp1.model_period_register` | `currency` | any ISO code | open |
| `cp1.model_account_register` | `calculation_status` | `VERIFIED`, `CALCULATED`, `ESTIMATED`, `PROXY`, `NOT CALCULABLE`, `PARTIAL`, `CONFLICTED`, `NOT AVAILABLE` | closed |
| `cp1.adjusted_ebitda_bridge` | `addback_classification` | `RESTRUCTURING`, `SBC`, `COST_SAVINGS`, `RUN_RATE`, `SYNERGY`, `TRANSACTION_COSTS`, `OTHER_EXPLICIT` | closed |
| `cp1.adjusted_ebitda_bridge` | `realization_status` | `REALIZED`, `UNREALIZED`, `NOT_STATED` | closed |
| `cp1.segment_revenue_schedule` | `segment_type` | `OPERATING_SEGMENT`, `CORPORATE_ELIMINATION` | closed |
| `cp1.operating_kpi_schedule` | `value_type` | `PERIOD_END`, `PERIOD_FLOW`, `RATE` | closed |
| `cp1.operating_kpi_schedule` | `unit` | any text | open |
| `cp1.debt_facility_register` | `facility_type` | `DEBT ADJUSTMENT` (the one the Model acts on) | open |
| `cp1.debt_facility_register` | `currency` | any ISO code | open |
| `cp1.debt_facility_register` | `secured_status` | `SECURED`, `UNSECURED`, `NOT_STATED` | closed |
| `cp1.debt_facility_register` | `seniority` | `SUPER_SENIOR`, `SENIOR`, `SENIOR_SUBORDINATED`, `SUBORDINATED`, `JUNIOR`, `NOT_STATED` | closed |
| `cp1.debt_facility_register` | `lease_classification` | `FINANCE_LEASE`, `OPERATING_LEASE`, `NOT_LEASE`, `NOT_STATED` | closed |
| `cp1.debt_facility_register` | `rate_type` | `FIXED`, `FLOATING`, `NOT_STATED` (null reads `NOT_STATED`) | closed |
| `cp1.debt_facility_register` | `reference_rate` | `SOFR`, `TERM_SOFR`, `EURIBOR`, `SONIA`, `NONE`, `NOT_STATED` (null reads `NOT_STATED`) | closed |
| `cp1.pro_forma_adjustment_register` | `classification` | `ACQUISITION`, `DISPOSAL`, `REFINANCING`, `SUBSEQUENT_EVENT`, `LENDER_UPDATE`, `OTHER_EXPLICIT` | closed |
| `cp1.pro_forma_adjustment_register` | `metric_id` | `revenue`, `ebitda`, `adjusted_ebitda`, `cash_interest_paid`, `cash_and_equivalents`, `total_debt`, `facility:<id>` (a facility of the register) | closed |
| `cp1.equity_value` | `unit` | `UNITS`, `THOUSANDS`, `MILLIONS` | closed |
| `cp1d.addback_assessment` | `house_realization_status` | `REALIZED`, `UNREALIZED`, `NOT_STATED` | closed |
| `cp1d.addback_assessment` | `verdict` | `Supported`, `Challenged`, `Rejected` | closed |
| `cp1d.debt_like_items` | `treatment` | `Debt-like`, `Not debt-like`, `Unclear` | closed |

Null text in a figure or optional column is any of: an empty cell, `null`, `n/a`, `not available`, `not calculable`, `-`, `—`, `–` (case ignored).
