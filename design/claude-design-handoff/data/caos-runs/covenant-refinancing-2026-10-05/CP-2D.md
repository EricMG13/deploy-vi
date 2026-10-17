---
module_id: "CP-2D"
module_name: "LiquidityCashFlowBridge"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "COVENANT_REFINANCING"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2D-152211d791d7d014"
credit_os_route_node_id: "RN-FULL_CREDIT_32-COVENANT_REFINANCING-05-CP-2D"
credit_os_invocation_sha256: "4d7a852c67dfe0db159dc3c17408f3584c9b77c4ed2bb9cd7634a5bc49f7ffe2"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a4ee2ea26d222a51d5c167a5868ea43f9bba131c911042fc7dcb2840af340ca2"
  - module_id: "CP-1"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a412c541834dd7643188444e637ba16543096bf4686d71c334f32b4a53e19a67"
  - module_id: "CP-2"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "b5f995cd341cadb6d06fa727e089dcc5546204d11efb49cb6a0e23034aa9ab5c"
confidence_score: 51
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, TWELVE_MONTH_CASH_FORECAST_NOT_PROVIDED, WORKING_CAPITAL_FORECAST_NOT_PROVIDED, REVOLVER_ENTITY_ACCESS_UNRESOLVED, DEBT_BASIS_RECONCILIATION_OPEN, MERGER_FINANCING_TERMS_NOT_IN_EVIDENCE, POST_PERIOD_EVENT_SEPARATION]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED, MONTHS_TO_EMPTY_NOT_CALCULABLE, TWELVE_MONTH_BRIDGE_INCOMPLETE, DEBT_BASIS_RECONCILIATION_OPEN]
downstream_consumers: [CP-3, CP-3C, CP-6, CP-5, CP-5A]
---

## Audit Summary

- **Module status:** Ready with Limitations. The Q2 2026 filing identifies period-end cash, revolver-capacity components, historical operating cash flow, scheduled debt service, lease payments and remaining-2026 capital expenditure estimates; it does not provide a complete forecast for the 12-month period ending June 30, 2027. [C1, C3, C8, C14, C17, C18]
- **Liquidity Risk Level:** Insufficient Information. The issuer reports $2,928 million of cash and borrowing capacity and management expects it to fund operations, capital requirements and debt service for the next twelve months and beyond. That characterization is counterevidence, not a substitute for a complete cash-flow bridge or confirmation of entity-level access. [C3, C4, C5, C6, C7, C21]
- **Confidence:** 51/100 — Low. Under the canon’s confidence formula, the partial source gate and material coverage gaps constrain confidence; the score is capped below 60 for Restricted status. This is not a rating or a credit conclusion.
- **Committee status:** Requires More Work. Maturity, interest, tax, working-capital, lease and capex forecasts and facility-level access are not all established for the full horizon.
- **Canonical file name:** `CZR_CP-2D_20261002.md`.
- **Next action:** Run CP-3C in route order; preserve the liquidity, debt-basis and merger-financing limitations. Obtain a monthly 12-month cash forecast and evidence of revolver availability at the relevant borrower and subsidiary perimeters.

## Analysis

### Liquidity view
Caesars reports $965 million of cash and a combined $2,928 million of cash and borrowing capacity at June 30, 2026; the disclosed facility components include letter-of-credit, specific-use and regulatory deductions. [C1, C3, C4, C5, C6, C7] The filing also reports $675 million of operating cash inflow for H1, but that historical flow is not a forecast and is not annualized here. [C8] For the remainder of 2026, estimated debt service is $425 million, VICI and GLPI lease payments are $687 million, and remaining capital expenditures are estimated at $310–390 million. [C16, C17, C18, C19, C20] These figures leave the 2027 portion of the July 2026–June 2027 horizon, cash taxes, forward working capital and other cash uses unresolved. Consequently, runway and months to empty are not calculable, and sufficiency cannot be independently established. Management’s stated sufficiency expectation is the strongest counterargument; it would carry more weight with a reconciled monthly forecast and confirmed access after all facility restrictions. [C21]

The concise summary below separates the reported opening resource from the partial, remaining-2026 cash-use estimates; the latter are not a complete 12-month forecast.

| Liquidity measure | Source-supported amount | Period / status | Creditor implication |
|---|---:|---|---|
| Cash and cash equivalents | $965m | June 30, 2026; Reported [C1] | Opening cash; restricted cash is excluded. [C2] |
| Reported cash and borrowing capacity | $2,928m | June 30, 2026; Reported [C3, C4, C5, C6, C7] | Issuer aggregate; entity-level fungibility remains unconfirmed. |
| Debt service | $425m | Remainder 2026; Provisional [C16] | Includes scheduled principal and estimated interest; not a full 12-month figure. |
| VICI and GLPI lease payments | $687m | Remainder 2026; Provisional [C17] | Contractual rent competes with other cash requirements. |
| Capital expenditures | $310–390m | Remainder 2026; Provisional [C18, C19, C20] | Includes maintenance, growth/renovation and digital investment. |
| Months to empty | Not calculable | Forward burn unsupported [C8] | No source-supported forward monthly cash-burn basis. |

**Pinch point and downside transmission.** The known remaining-2026 debt service, rent and capex sum to $1,422–1,502 million, but this partial subtotal excludes unknown cash taxes, forward working-capital needs and operating cash flow and does not include the full 2027 portion of the 12-month horizon. [C16, C17, C18, C19, C20] H1 cash-flow details show accounts receivable and prepaid assets absorbing cash, partly offset by payables and accrued liabilities; the three disclosed items net to a $60 million historical outflow, not a forward assumption. [C9, C10, C11] Deposits and deferred revenue rose by $53 million in H1; these balances represent customer funds and advance payments associated with gaming play or future goods and services, so they are operating float with related performance obligations rather than unrestricted surplus liquidity. [C26, C27]

The causal downside path is a further weakening in Las Vegas visitation, hotel occupancy or table-game hold; the first break is lower segment earnings, while rent, labor, taxes and property needs continue. Q2 Las Vegas Adjusted EBITDA declined year over year, while Regional results increased but include the Windsor operating transition and do not remove the Las Vegas pressure. [C28, C29] Lower cash conversion or a working-capital outflow would then increase revolver reliance and reduce the buffer available for contractual rent, debt service and investment. A sustained decline alongside delayed or unavailable transaction financing would raise refinancing dependence; the observable triggers are falling cash or facility availability, accelerating cash burn, further working-capital absorption, missed forecast delivery, or a change in transaction financing or closing status. [C5, C9, C10, C11, C21, C32]

**Counterevidence and decision effect.** Management states that current liquidity, committed borrowing availability and operating cash flows should be sufficient for the next twelve months and beyond, and the issuer reports compliance with applicable financial covenants at June 30, 2026. [C21, C22] These points lower immediate concern but do not quantify covenant headroom or establish that every consolidated facility is available to the same debtor perimeter. The counterargument would prevail if monthly forecast cash flows, contractual uses and facility conditions demonstrate positive headroom through June 30, 2027 under a downside case; until then, conviction and downstream refinancing conclusions should remain limited. The proposed merger and its financing remain separate from period-end liquidity; financing risk is explicitly disclosed and must not be blended into reported Q2 balances. [C31, C32]

### Analytical appendix — complete canonical registers

#### T2E.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | Primary-Verified | Quarter and six months ended June 30, 2026 | Caesars Entertainment, Inc. and consolidated subsidiaries | Cash, restricted cash, debt and debt-service schedule, revolver-capacity components, H1 cash flows, historical working-capital movements, remaining-2026 lease and capex estimates, covenant status, contract liabilities and subsequent events. [C1, C2, C8, C9, C10, C11, C14, C16, C17, C18, C19, C20, C22, C26, C27, C31] | Interim results are not a forward cash forecast; estimates cover the remainder of 2026 rather than the full July 2026–June 2027 horizon. Revolver access across entity perimeters and complete transaction-financing terms are not established. | Beginning liquidity, cash-use register, partial bridge, event separation, monitoring and gaps. |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | Primary-Verified | Fiscal year ended December 31, 2025 | Caesars Entertainment, Inc. and consolidated subsidiaries | Audited annual financial statements, lease and debt context, annual cash flow, operating context and disclosed seasonality. [C36, C42] | Annual and year-end data are not substitutes for a current forward forecast; the reporting period precedes Q2 2026. | Historical context and evidence on seasonal variability; no annualized H1 burn used. |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | Primary-Verified | Executed February 6, 2024 agreement and delivered conformed Credit Agreement | Caesars Entertainment, Inc. borrower and listed subsidiary loan parties | Credit agreement framework and incremental Term B-1 documentation. [C33] | Referenced schedules are not all present in the delivered representation; not a forward cash forecast or a substitute for facility-level availability confirmation. | Financing-document context; no inferred covenant capacity or borrowing-base availability. |
| 050d12fd-6a63-4d3a-8d28-263977d76585 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt | Primary-Verified | Executed amendment dated May 9, 2024 | Caesars Entertainment, Inc., borrower | Amendment to the Credit Agreement. [C34] | No standalone liquidity forecast or current facility-access calculation. | Source chronology and document inventory. |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | CZR_2024_Credit_Agreement_Fifth_Amendment.txt | Primary-Verified | Executed amendment dated November 25, 2024 | Caesars Entertainment, Inc., borrower | Later delivered amendment to the Credit Agreement. [C35] | No standalone liquidity forecast; later executed amendment evidence is not included in this source set. | Source chronology and limitation on current terms. |

**Module Status:** Ready with Limitations. Current cash and cash-flow evidence is identifiable, so the module is not blocked; forward cash flow, working-capital forecasts, full-horizon uses and complete access constraints are partial or missing. Citation discipline: every material fact and calculation input is tied to a delivered evidence locator in the source-trace column or Evidence Trace section.

#### T2E.2 — Beginning Liquidity Register

| Liquidity Component | Source-Supported Amount | Accessibility Status | Source Trace | Limitation / Restriction | Risk Mechanic | Credit Implication |
|---|---:|---|---|---|---|---|
| Cash | $965m | Reported cash and cash equivalents; included in issuer liquidity. [C1] | Q2 2026 Form 10-Q, p. 2 [C1] | Consolidated balance; cash availability by debtor or jurisdiction is not itemized. | Cash is the immediate buffer for operating and contractual requirements. | Supports opening liquidity, but does not alone demonstrate 12-month coverage. |
| Restricted cash | $96m | Restricted; excluded from accessible liquidity. [C2] | Q2 2026 Form 10-Q, p. 2 [C2] | Restricted under operating agreements or for capital purposes; accessibility is not confirmed. | Including restricted cash would overstate usable liquidity. | Do not count as an accessible source. |
| Revolver commitment | $2,250m CEI commitment; $25m CVA commitment | Committed facilities; not equal to available cash. [C39, C41] | Q2 2026 Form 10-Q, pp. 10 [C39, C41] | CEI and Caesars Virginia have different borrower perimeters; do not presume unrestricted transferability. | Commitment supports liquidity only to the extent undrawn, available and accessible to the relevant entity. | Treat consolidated capacity as reported, with perimeter and covenant caveats. |
| Revolver drawn | $120m CEI revolver | Reported drawn amount. [C40] | Q2 2026 Form 10-Q, p. 9 [C40] | The CVA revolving balance is displayed as a dash; it is not converted to zero. | Draws reduce remaining facility capacity and may indicate cash pressure if they rise. | Monitor revolver draw and remaining availability. |
| Undrawn revolver | $2,130m CEI capacity net of outstanding balance; CVA capacity reported separately at $25m | Reported capacity before separately shown LC, specific-reserve and regulatory deductions. [C3, C4] | Q2 2026 Form 10-Q, p. 22 [C3, C4] | The disclosed amounts are not a guarantee of future availability; facility tests and entity-level access remain relevant. | Gross undrawn capacity can overstate usable liquidity if commitments are restricted or utilization increases. | Apply the separately disclosed deductions; do not equate commitment with unrestricted cash. |
| Accessible revolver availability | $1,963m calculated from $2,130m + $25m − $96m − $40m − $56m | Calculated from issuer-presented capacity and deductions; consolidated perimeter caveat remains. [C3, C4, C5, C6, C7] | Q2 2026 Form 10-Q, p. 22 [C3, C4, C5, C6, C7] | $40m specific reserves are not general-purpose liquidity; $56m is committed for regulatory requirements; CVA capacity may not be freely upstreamed. | Constraints reduce the amount available to meet general corporate cash uses. | Use $1,963m only as the displayed consolidated calculation, not as confirmed parent-only capacity. |
| Other committed liquidity | — | Not Available — no additional committed accessible source identified in the delivered evidence. | Q2 2026 liquidity disclosure, p. 22; absence of additional source in delivered evidence | No sponsor support, equity cure, or asset-sale proceeds are committed for the forecast horizon. | Treating uncommitted support or sales as available would overstate runway. | No additional liquidity is assumed. |
| Beginning accessible liquidity | $2,928m issuer-reported; equals $965m cash plus $1,963m calculated revolver availability | Reported aggregate cash and borrowing capacity, subject to perimeter caveat. [C1, C3, C4, C5, C6, C7] | Q2 2026 Form 10-Q, p. 22 [C1, C3, C4, C5, C6, C7] | Issuer aggregate does not prove each source is freely transferable or available after future conditions. | The usable opening buffer is the starting point for covering future cash needs. | Decision-useful opening figure, but insufficient by itself to establish 12-month sufficiency. |

#### T2E.3 — Mandatory Cash Uses Register

| Cash Use | Amount | Timing | Mandatory / Discretionary | Source Trace | Risk Mechanic | Credit Implication | Limitation |
|---|---:|---|---|---|---|---|---|
| Cash interest | $370m estimated | Remainder 2026 | Mandatory debt service | Q2 2026 Form 10-Q, p. 9 [C15] | Interest absorbs cash before discretionary investment or debt reduction. | Adds to near-term cash requirements. | Estimate based on forward-looking interest curves; 2027 portion of the 12-month horizon is not provided by quarter. |
| Debt amortization | $55m estimated | Remainder 2026 | Mandatory debt service | Q2 2026 Form 10-Q, p. 9 [C14] | Principal payments reduce liquidity unless refinanced or funded from operations. | Adds to cash needs; amount is not the full 12-month requirement. | Schedule states estimates based on contractual maturities and scheduled repayment dates; 2027 quarter allocation is unavailable. |
| Lease payment | $687m estimated | Remainder 2026 | Mandatory contractual operating use | Q2 2026 Form 10-Q, p. 22 [C17] | Rent competes directly with debt service, maintenance and other operating uses. | High fixed cash requirement reduces liquidity flexibility. | Issuer estimate for remaining 2026 only; no 12-month lease forecast supplied here. |
| Mandatory capex | $155–185m maintenance estimate | Remainder 2026 | Operationally necessary; not documented as a contract-level mandatory amount | Q2 2026 Form 10-Q, p. 22 [C20] | Deferral may preserve cash temporarily but can impair property upkeep and future cash generation. | Limits the scope for liquidity preservation without operating trade-offs. | Company estimate; “maintenance” is not further split into legally mandatory and deferrable components. |
| Growth capex | $130–170m growth and renovation estimate | Remainder 2026 | Discretionary / execution-dependent | Q2 2026 Form 10-Q, p. 22 [C18] | Deferral could preserve cash but delay projects and expected operating benefits. | Potential short-term mitigant, with possible future FCF trade-off. | Estimate only; no committed project-by-project schedule. |
| Growth capex | $25–35m Caesars Digital estimate | Remainder 2026 | Discretionary / strategic investment | Q2 2026 Form 10-Q, p. 22 [C19] | Lower investment could preserve cash but may constrain digital product and operating capacity. | Possible liquidity lever; not assumed to be deferrable without consequence. | Estimate only; no commitment schedule or cash phasing provided. |
| Working-capital outflow | H1 historical: $60m net outflow across three disclosed operating asset/liability lines | Six months ended June 30, 2026; not a forward estimate | Operating cash use; future level not calculable | Q2 2026 Form 10-Q, p. 4 [C9, C10, C11] | Receivables and prepaid assets absorbed more cash than the disclosed payables/accrual increase supplied. | Demonstrates working-capital cash absorption, not a forecast. | Excludes income taxes and is not annualized; future seasonality and cash timing are not supplied. |
| Cash taxes | [Insufficient Information] — no full-horizon cash-tax estimate provided; H1 cash taxes paid were $11m. | July 2026–June 2027 | Mandatory when due | Q2 2026 Form 10-Q, p. 5 [C37] | Taxes reduce cash available for other uses. | Full cash requirements are understated if omitted from a forecast. | H1 paid amount is historical and is not extrapolated. |
| Other mandatory cash use | [Insufficient Information] — full 12-month schedule for distributions, litigation, pension and other committed uses not provided. | July 2026–June 2027 | Not classifiable from the delivered evidence | Q2 2026 cash-flow statement, p. 4 [C38]; full-horizon schedule not provided | Unidentified commitments may consume the opening liquidity buffer. | No positive or adverse amount is assumed; bridge remains incomplete. | H1 noncontrolling-interest distributions were $41m but are not a full-horizon forecast. |

#### T2E.4 — Working Capital & Capex Pressure

| Driver | Evidence | Expected Cash Impact | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|---|
| Receivables and prepaid assets | H1 2026 cash-flow changes: receivables $(24)m; prepaid expenses and other assets $(88)m. [C9, C10] | Historical H1 cash absorption of $112m before offsets. | Cash is absorbed in operating assets before it can fund interest, rent or capex. | If repeated, absorption weakens debt-service capacity and runway. | Q2 2026 Form 10-Q, p. 4 [C9, C10] | Historical six-month movement only; no monthly forecast or seasonal bridge supplied. |
| Payables and accrued liabilities | H1 2026 change contributed $52m of operating cash. [C11] | Historical offset; the three identified lines net to $(60)m. [C9, C10, C11] | An offset may reverse if supplier balances unwind or accrued obligations are paid. | Do not assume repeat cash support from payable growth. | Q2 2026 Form 10-Q, p. 4 [C9, C10, C11] | Aggregate payables/accrual line is not a forecast; timing and composition are not detailed. |
| Seasonal working capital | Issuer states regional business is subject to seasonality tied to weather and visitor travel. [C42] | Direction and amount not calculable for July 2026–June 2027. | Seasonal receipts and payments can change the timing of liquidity needs. | A point-in-time balance cannot establish peak-period headroom. | FY2025 Form 10-K, p. 4 [C42] | No seasonal monthly working-capital history or forecast included in the evidence delivered. |
| Customer deposits and deferred revenue | Balance rose from $492m at January 1 to $545m at June 30, 2026, an increase of $53m. [C26] | Provided $53m of historical operating float; future cash impact unknown. | Deposits and advance receipts carry future performance or gaming obligations and are not unrestricted surplus cash. | A reversal or redemption/performance requirement could absorb liquidity. | Q2 2026 Form 10-Q, p. 11 [C26, C27] | No refund, redemption or performance schedule; do not classify as debt or freely available cash. |
| Maintenance capex | Company estimates $155–185m of remaining-2026 maintenance projects. [C20] | Estimated cash use in the remainder of 2026. | Sustained deferral may preserve cash temporarily but can weaken property condition and future cash generation. | Treat as a competing operational requirement, not assumed zero or freely deferrable. | Q2 2026 Form 10-Q, p. 22 [C20] | No maintenance-versus-essential split or full 12-month profile. |
| Growth, renovation and digital capex | Remaining-2026 estimates: $130–170m growth/renovation and $25–35m digital. [C18, C19] | Estimated cash use; timing after December 2026 is not provided. | Deferral may relieve near-term cash pressure but can delay project returns or weaken digital competitiveness. | Potential mitigant only if execution flexibility is evidenced; no such commitment is assumed. | Q2 2026 Form 10-Q, p. 22 [C18, C19] | Company estimates do not identify cancellable commitments or the full next-12-month schedule. |

#### T2E.5 — 12-Month Liquidity Bridge

| Bridge Item | Amount | Source / Calculation | Status | Credit Comment | Source Trace |
|---|---:|---|---|---|---|
| Beginning cash | $965m | Reported cash and cash equivalents at June 30, 2026. | Reported | Restricted cash of $96m is excluded. | Q2 2026 Form 10-Q, p. 2 [C1, C2] |
| Accessible revolver availability | $1,963m | $2,130m CEI capacity + $25m CVA capacity − $96m LCs − $40m specific reserves − $56m regulatory reserve. | Calculated | Issuer-disclosed components; subsidiary access and future facility conditions remain limitations. | Q2 2026 Form 10-Q, p. 22 [C3, C4, C5, C6, C7] |
| Beginning accessible liquidity | $2,928m | $965m cash + $1,963m calculated revolver availability; equals issuer-reported total. | Reported | Consolidated issuer measure, not confirmation that all amounts are freely accessible to the same debtor. | Q2 2026 Form 10-Q, p. 22 [C1, C3, C4, C5, C6, C7] |
| Operating cash inflow/outflow | [Insufficient Information] — no forecast for July 2026–June 2027. | H1 2026 CFO of $675m is historical and is not annualized. | Insufficient Information | Without a forecast, operations cannot be converted into a 12-month cash-flow input. | Q2 2026 Form 10-Q, p. 4 [C8] |
| Working-capital impact | [Insufficient Information] — forward impact not provided. | Three identified H1 changes net to $(60)m; historical only. | Insufficient Information | The historical cash absorption is not presumed to repeat or reverse. | Q2 2026 Form 10-Q, p. 4 [C9, C10, C11] |
| Cash interest | $370m estimated for remainder 2026 only. | Issuer debt-service schedule, based on forward interest curves. | Provisional | Does not cover the full next-12-month period. | Q2 2026 Form 10-Q, p. 9 [C15] |
| Cash taxes | [Insufficient Information] — no full-horizon estimate. | H1 2026 paid $11m; historical only. | Insufficient Information | No zero substitution or annualization. | Q2 2026 Form 10-Q, p. 5 [C37] |
| Mandatory capex | $155–185m maintenance estimate for remainder 2026. | Company estimate; no full-horizon split. | Provisional | Maintenance is an operating requirement; full timing and flexibility are not established. | Q2 2026 Form 10-Q, p. 22 [C20] |
| Debt amortization/maturities | $55m estimated for remainder 2026 only. | Issuer schedule of annual maturities. | Provisional | The 2027 portion of the 12-month period is not phased by quarter. | Q2 2026 Form 10-Q, p. 9 [C14] |
| Other cash uses | $155–205m estimated growth/renovation and digital capex for remainder 2026; other uses [Insufficient Information]. | Sum of $130–170m growth/renovation and $25–35m digital estimates; other uses are not supplied. | Provisional | Partial discretionary capex only; no 12-month total or committed-inflow schedule. | Q2 2026 Form 10-Q, p. 22 [C18, C19] |
| Ending accessible liquidity | [Insufficient Information] — full-horizon operating cash flow, working capital, taxes, 2027 cash uses, and other uses are missing. | Beginning accessible liquidity plus operating cash flow and committed inflows, less all cash uses; required forward inputs are incomplete. | Insufficient Information | No ending-liquidity estimate or unsupported zero substitution. | Q2 2026 Form 10-Q, pp. 4, 9, 22 [C8, C9, C10, C11, C14, C15, C17, C18, C19, C20, C37] |

The separately identified remaining-2026 subtotal for scheduled debt service ($425m), VICI/GLPI rent ($687m) and capex ($310–390m) is $1,422–1,502m. This is a partial remainder-of-year subtotal, not total 12-month cash uses; it excludes forecast operating cash flow, forward working capital, taxes and 2027 quarter phasing. [C16, C17, C18, C19, C20]

#### T2E.6 — Months to Empty

| Calculation | Result | Formula / Inputs | Cash-Burn Basis | Status | Source Trace |
|---|---|---|---|---|---|
| Months to Empty | [Insufficient Information] — average forward monthly cash burn and a supportable 12-month accessible-liquidity perimeter are not both available. | Beginning accessible liquidity / average monthly cash burn; opening issuer aggregate is $2,928m, but average monthly forward burn is not provided. | H1 2026 CFO was $675m for six months; it is historical and may reflect working-capital timing. Volatility, recurring profile and seasonality cannot be resolved from this period alone; no monthly average or annualization used. | Insufficient Information | Q2 2026 Form 10-Q, pp. 4, 22 [C8, C21] |

#### T2E.7 — Liquidity Mitigants & Constraints

| Mitigant / Constraint | Evidence | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|
| Reported cash and borrowing capacity — mitigant, with access caveat | Issuer reports $2,928m aggregate cash and borrowing capacity, including stated deductions. [C1, C3, C4, C5, C6, C7] | Cash and available committed capacity can meet uses only to the extent each is accessible to the relevant entity and remains undrawn. | Supports the opening buffer, but not a conclusion of 12-month sufficiency. Monitoring trigger: Revolver availability decline. | Q2 2026 Form 10-Q, pp. 2, 22 [C1, C3, C4, C5, C6, C7] | Cross-entity access and future facility tests are not confirmed. |
| Management liquidity expectation — mitigant / counterargument | Management expects current liquidity, facility availability and cash flows to fund operations, capital needs and debt service for twelve months and beyond. [C21] | If realized, cash generation plus available borrowing would cover uses without emergency refinancing. | Strongest contrary evidence; it would prevail if supported by a forecast with adequate downside headroom. | Q2 2026 Form 10-Q, p. 22 [C21] | Forward monthly forecast and independent cash-use reconciliation are not provided. |
| Covenant compliance — mitigant | Issuer reports compliance with applicable financial covenants at June 30, 2026. [C22] | No disclosed period-end breach; covenant access could still depend on later tests and available headroom. | Reduces concern about a reported current breach but does not establish future revolver capacity. Monitoring trigger: Covenant access constraint. | Q2 2026 Form 10-Q, p. 23 [C22] | Covenant headroom and calculation inputs are not supplied here. |
| Restricted cash and facility deductions — constraint | Restricted cash is $96m; the liquidity table separately deducts $96m of LCs, $40m of specific reserves and $56m of regulatory requirements. [C2, C5, C6, C7] | Reported cash and gross commitment overstate the resources freely available for general uses if restrictions are ignored. | Exclude restricted cash and preserve the stated facility deductions. Monitoring trigger: Revolver availability decline. | Q2 2026 Form 10-Q, pp. 2, 22 [C2, C5, C6, C7] | Detailed reserve terms and future letters of credit are not forecast. |
| Customer deposits and deferred revenue — operating funding float / constraint | Balance increased to $545m from $492m during H1; disclosed as gaming deposits and advance payments for future services or goods. [C26, C27] | Customer funds support working capital but correspond to future performance, gaming or other obligations. | Not debt or freely available surplus cash; a change in customer behavior could create an operating cash use. Monitoring trigger: Working-capital outflow. | Q2 2026 Form 10-Q, p. 11 [C26, C27] | Redemption and fulfillment cash timing is unavailable. |
| Maintenance and discretionary capex — partial mitigant and constraint | Remaining-2026 estimates distinguish maintenance from growth/renovation and digital investment. [C18, C19, C20] | Deferring growth spend may preserve cash; deferring maintenance may weaken property condition and future FCF. | Monitor capex inflexibility; do not assume all forecast capex can be deferred. | Q2 2026 Form 10-Q, p. 22 [C18, C19, C20] | No project-level commitment, cancellation or full-year 2027 schedule. |
| Debt and lease service — constraint | Remainder-2026 estimated debt service is $425m and VICI/GLPI rent is $687m; calendar-2027 debt service is separately scheduled at $864m. [C16, C17] | Fixed debt and lease claims compete with operating cash needs and capital investment. | Sustained earnings or cash conversion weakness narrows liquidity; 2027 quarterly phasing is needed to assess the full horizon. | Q2 2026 Form 10-Q, pp. 9, 22 [C14, C15, C16, C17] | The annual 2027 schedule cannot be allocated to the 12-month horizon without a quarterly forecast. |
| Merger and financing uncertainty — constraint / contingent catalyst | Proposed transaction is subject to closing conditions; the filing identifies risk that financing may not be obtained on anticipated terms or at all. [C32] | Delay or failed financing could defer a transaction-related liquidity change and prolong standalone funding needs. | Do not assume merger funding or sponsor support; monitor refinancing failure and transaction milestones. | Q2 2026 Form 10-Q, pp. 5, 24 [C32] | Complete executed financing terms are not present in the delivered evidence. |
| Subsequent Alberta launch — post-period event | Mobile sports betting and iGaming launched in Alberta on July 13, 2026, after the June 30 reporting date. [C31] | Any contribution would arise after the reporting date and is not a period-end liquidity source. | Keep separate from Q2 cash flows; monitor subsequent reported performance. Monitoring trigger: Reporting gap. | Q2 2026 Form 10-Q, p. 17 [C31] | No post-launch operating or cash-flow data are supplied. |
| Refinancing window — monitoring constraint | CEI revolving facility matures January 31, 2028; Q2 maturity schedule includes principal payments thereafter. [C14, C39] | Persistent cash weakness or transaction delay could increase dependence on refinancing as maturities approach. | No immediate 12-month maturity wall is established by the cited schedule; initiate monitoring of execution well before 2028. Monitoring trigger: Maturity wall / Refinancing failure. | Q2 2026 Form 10-Q, pp. 9–10 [C14, C39] | Market quotations, lender indications and executed replacement financing are not provided. |

#### T2E.9 — Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up | Downstream Module Affected |
|---|---|---|---|---|---|
| Full 12-month cash forecast | Monthly operating cash flow and a forecast through June 30, 2027. | Cash generation is needed to test whether liquidity covers all cash uses and to calculate runway. | T2E.5 ending liquidity and T2E.6 months to empty are not calculable; risk level remains Insufficient Information. | Provide a monthly cash forecast with assumptions, seasonality, recurring items and one-offs. | CP-3, CP-3C, CP-6 |
| Revolver accessibility by entity | Facility-level availability, borrower perimeter, conditions to draw, and availability for transfer between CEI and CVA. | Consolidated disclosed capacity may not be available to the same debtor or for all uses. | Beginning accessible liquidity is an issuer aggregate with an access limitation. | Supply facility certificates, borrowing conditions and entity-level cash/access map. | CP-3C, CP-6 |
| Restricted and reserved cash classification | Detailed restriction, purpose and release timing for restricted cash and facility reserves. | Restricted or purpose-limited amounts cannot be treated as general liquidity. | Accessibility and liquidity downside buffer remain qualified. | Supply cash-account restrictions, reserve terms and release conditions. | CP-3C, CP-6 |
| Revolver borrowing-base and covenant access | Current borrowing-base support and facility-specific draw conditions or headroom. | A committed facility is not necessarily accessible if contractual or other draw conditions limit it. | Future accessible revolver availability cannot be confirmed. | Supply current compliance certificate and facility availability documentation. | CP-3C, CP-4A, CP-6 |
| 2027 debt service and cash interest phasing | Quarterly schedule for July 2026–June 2027, including the 2027 portion and cash-interest assumptions. | The annual 2027 schedule does not identify the portion falling within this bridge horizon. | Mandatory cash uses and ending liquidity cannot be calculated for the full 12 months. | Provide a dated monthly or quarterly debt and cash-interest schedule. | CP-3C, CP-6 |
| Cash taxes | Forward cash-tax estimate and payment timing. | Taxes compete with debt service, rent, working capital and capex. | Cash-use register and bridge are incomplete; no zero is assumed. | Provide tax-payment forecast by quarter and jurisdiction. | CP-3, CP-3C, CP-6 |
| Working-capital and seasonal forecast | Monthly receivables, prepaid assets, payables/accruals and customer deposit/deferred-revenue expectations. | H1 movements show material cash timing but cannot be projected from the delivered evidence. | Forward WC impact and months to empty are unsupported. | Provide monthly working-capital forecast, prior-year seasonal pattern and deposit/performance timing. | CP-3, CP-3C, CP-6 |
| Capex commitments and flexibility | Full 12-month project schedule, mandatory-versus-deferrable designation and cancellation commitments. | Maintenance and growth spend have different liquidity and FCF consequences. | Only remainder-2026 company estimates are included; full-period uses remain incomplete. | Provide project-level cash timing and committed, maintenance, growth and digital splits. | CP-3, CP-3C, CP-6 |
| Lease and other contractual cash uses | Full 12-month lease, sponsorship, litigation, pension, distribution and other committed-use schedule. | Rent and other recurring or contingent uses can consume liquidity independent of debt service. | Complete mandatory-use coverage cannot be established. | Provide contractual payment calendar and material contingent cash-use estimates. | CP-3C, CP-6 |
| Debt-basis reconciliation CF-1 | Reconciliation between Q2 debt-note book value and current plus long-term balance-sheet carrying debt. | Carrying debt is a key denominator and facility-level liquidity analysis must preserve source definitions. | Note total is $11,705m versus $11,699m from $114m current plus $11,585m long-term balance-sheet debt; $6m difference remains unresolved. [C23, C24, C25] | Obtain issuer reconciliation; retain both presentations until resolved. | CP-1, CP-2, CP-3C, CP-4A, CP-5A |
| Merger financing and transaction cash flows | Complete executed financing commitments, fees, funding conditions and a transaction-related liquidity schedule. | The merger could alter liquidity and debt, but financing is not certain on the disclosed evidence. | No merger proceeds, transaction debt or support is included in the Q2-period bridge. [C32] | Provide complete financing commitments and a cash-flow schedule, with event dates kept separate from Q2 actuals. | CP-3C, CP-4, CP-6 |
| Subsequent-event scan after June 30 | Later-period primary disclosure through the analysis date. | Later financing, operating or transaction developments may change access and cash needs. | Only the July 13 Alberta launch is evidenced here; no later event is inferred. [C31] | Provide the latest primary filing or other admitted subsequent-event source. | CP-3C, CP-5A |
| Sponsor support and asset-sale proceeds | Executed, committed support or transaction-specific proceeds and timing. | Uncommitted sponsor support and unexecuted asset sales cannot support runway. | No such source is added to beginning liquidity or bridge. | Provide signed commitments or executed sale documents and expected receipt dates. | CP-3C, CP-6 |

## Evidence Trace

| Claim or calculation | Citation | Document | Page |
|---|---|---|---:|
| Period-end cash and restricted cash | [C1, C2] | Q2 2026 Form 10-Q | 2 |
| Revolver capacity components and reported total | [C3, C4, C5, C6, C7] | Q2 2026 Form 10-Q | 22 |
| CEI and CVA revolver commitment terms; CEI revolver balance | [C39, C40, C41] | Q2 2026 Form 10-Q | 9–10 |
| H1 operating cash flow and operating asset/liability changes | [C8, C9, C10, C11] | Q2 2026 Form 10-Q | 4 |
| H1 cash interest, taxes and capex | [C12, C13, C37] | Q2 2026 Form 10-Q | 4–5 |
| Debt maturities and estimated interest/debt service | [C14, C15, C16] | Q2 2026 Form 10-Q | 9 |
| Remaining-2026 lease and capex estimates | [C17, C18, C19, C20] | Q2 2026 Form 10-Q | 22 |
| Management sufficiency characterization and covenant status | [C21, C22] | Q2 2026 Form 10-Q | 22–23 |
| Debt-basis conflict CF-1 | [C23, C24, C25] | Q2 2026 Form 10-Q | 2, 9 |
| Customer deposits, deferred revenue and obligation character | [C26, C27] | Q2 2026 Form 10-Q | 11 |
| Las Vegas, Regional and Digital earnings evidence | [C28, C29, C30] | Q2 2026 Form 10-Q | 20–21 |
| Alberta subsequent event | [C31] | Q2 2026 Form 10-Q | 17 |
| Merger financing risk | [C32] | Q2 2026 Form 10-Q | 24 |
| Agreement source identity | [C33, C34, C35] | Incremental Assumption Agreement No. 3; Fourth Amendment; Fifth Amendment | 1; 1; 1 |
| FY2025 audited financial-statement quality | [C36] | FY2025 Form 10-K | 28 |
| Regional seasonality disclosure | [C42] | FY2025 Form 10-K | 4 |

## Source Registry

The Q2 2026 Form 10-Q is the principal current source for cash, facility capacity, H1 cash flows, debt service, remaining-2026 lease and capex estimates, covenant status and the dated subsequent event. [C1, C3, C8, C14, C16, C17, C18, C19, C20, C22, C31] The FY2025 Form 10-K supplies audited historical context and seasonal-risk disclosure, not a replacement for a forward cash forecast. [C36, C42] The delivered executed credit-agreement materials are retained as financing-document sources; their existence does not establish current borrowing-base availability, future cash generation or a refinancing outcome. [C33, C34, C35]

## Gaps & Conflicts

**CF-1 — debt-basis conflict.** At June 30, 2026, the debt note reports $11,807 million face value and $11,705 million book value; balance-sheet current and long-term debt are $114 million and $11,585 million, respectively, summing to $11,699 million. The $6 million book-value difference is not reconciled here. This does not change the reported cash figure but limits debt-service and leverage reconciliation; retain both presentations and do not silently select the debt-note total. [C23, C24, C25]

**Bridge coverage gap.** The source-supported beginning liquidity is an issuer-reported aggregate, but accessibility across consolidated entities is not confirmed. The remaining-2026 debt service, lease and capex figures do not cover the full July 2026–June 2027 period, and there is no complete forward operating cash flow, cash-tax or working-capital schedule. Consequently, ending liquidity, full-horizon cash uses and months to empty are not calculable from the provided materials. [C3, C4, C8, C14, C15, C16, C17, C18, C19, C20, C37]

**Subsequent events.** The mobile sports betting and iGaming launch in Alberta occurred July 13, 2026, after the June 30 reporting date; it is not blended into Q2 figures or treated as a cash inflow. The evidence delivered does not establish later-period results. [C31]

**Transaction uncertainty.** The proposed merger is distinct from Q2-period cash and debt. The filing identifies a risk that transaction financing may not be obtained on anticipated terms or at all; no transaction financing proceeds or sponsor support are assumed. [C32]

## QA Validation

- **Identity and upstream re-anchor:** PASS WITH LIMITATIONS — CZR, CP-2D, Q2 2026, run and analysis date match the supplied host-owned identity; accepted CP-0, CP-1 and CP-2 lineage is preserved exactly in front matter.
- **Source gate and evidence trace:** RESTRICTED — current primary interim evidence and audited annual context are available. Material forward cash-flow, access-perimeter and transaction-financing gaps remain explicit.
- **Register inventory and columns:** PASS — T2E.1, T2E.2, T2E.3, T2E.4, T2E.5, T2E.6, T2E.7 and T2E.9 are present with the required columns and at least one body row each.
- **Liquidity classification and null discipline:** PASS WITH LIMITATIONS — reported cash is distinguished from restricted cash and borrowing capacity; unavailable amounts are shown as `[Insufficient Information]` or `—`, never substituted with zero.
- **Bridge and months-to-empty calculation:** RESTRICTED — known remaining-2026 amounts are kept separate from the incomplete 12-month horizon. Months to empty is withheld because average forward cash burn is unsupported. No host-script output is claimed.
- **Conflicts and events:** PASS WITH LIMITATIONS — CF-1 is preserved without silent reconciliation; the July 13 Alberta launch is dated and kept outside Q2 figures; merger financing is not assumed.
- **Risk assessment and counterevidence:** PASS WITH LIMITATIONS — Liquidity Risk Level is Insufficient Information; management’s sufficiency statement and reported covenant compliance are presented as counterevidence, not as independently established headroom.
- **Confidence and status:** PASS — confidence score 51, Low band, qa_status Restricted and committee_status Requires More Work reflect the partial source gate and material coverage limitations.
- **Arithmetic check:** Formula inputs and displayed deductions are stated transparently. The reported liquidity components reconcile to the $2,928m issuer total; no external script result is asserted.
- **Host validation:** Pending after this response. No host validator or completeness-check result is asserted.