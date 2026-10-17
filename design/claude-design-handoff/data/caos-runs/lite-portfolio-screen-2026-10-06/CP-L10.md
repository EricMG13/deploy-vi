---
module_id: "CP-L10"
module_name: "LiteFinancialChangeScreen"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T071305Z-0e81c3d0929f43aa97f1af13b46c9462"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T071305Z-0e81c3d0929f43aa97f1af13b46c9462"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_PORTFOLIO_DECISION"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-L10-7a2f81b655e45140"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_PORTFOLIO_DECISION-02-CP-L10"
credit_os_invocation_sha256: "f017255f58971038f9d9c2cec611312064b90b02a66aeb35c5de48dc3d037117"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T071305Z-0e81c3d0929f43aa97f1af13b46c9462"
    period: "Q2 2026"
    sha256: "40c0f10ee8fbb046b97c80be41a66105fc5f62608a5af877a86018929ea5fa81"
confidence_score: 59
confidence_band: Low
qa_status: Restricted
committee_status: Restricted
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED]
downstream_consumers: [CP-1C, CP-2H, CP-4C, CP-5, CP-5A]
---

## Audit Summary

**Screen status: COMPLETE_WITH_GAPS; source gate: PARTIAL; structured outcome: FULL_UPGRADE_REQUIRED.** The dated filings show modest revenue growth alongside lower consolidated Adjusted EBITDA and a slightly lower operating cash inflow; GAAP net loss also narrowed year over year. Cash, debt and facility disclosures provide context but do not establish a current liquidity bridge. [C1, C2, C3, C4, C6] A pending merger agreement, a June 30 fund position snapshot, and a last-trade-only market observation leave material decision questions open. [C8, C9, C10, C11, C12, C13] The combined screening posture is **MIXED**: operating and liquidity indicators do not move uniformly, and the available evidence is insufficient for a full credit or instrument decision. Complete the linked FULL_CREDIT_32 work only after user confirmation.

Confidence score: **59 / Low**. Basis: the preliminary evidence and coverage calculation is 65.8 with a partial source gate; the Restricted QA status caps the score at 59. `qa_status` is Restricted because current position, detailed forward liquidity, market comparables, and complete legal/security materials are not supplied. Committee status is Restricted; this screening run is not committee clearance.

## Analysis

### Financial change screen

**Screen conclusion.** Q2 revenue increased year over year, while Adjusted EBITDA declined; six-month operating cash flow was broadly flat, and reported debt was lower than the prior year-end comparison. [C1, C3, C4, C6, C7] These offsetting movements support a mixed screen rather than a single directional inference. The issuer also reports a pending merger agreement, but the supplied filing does not establish subsequent status or financing terms. [C8, C9]

**Primary support:** Q2 and six-month financial statements, debt and liquidity disclosures. **Primary risk:** high reported debt and material lease payments coexist with incomplete forward cash and transaction information. [C6, C7, C8] **Monitoring trigger:** changes in merger status or financing, liquidity/facility availability, and subsequent quarterly cash conversion. No post-June event is blended into Q2 figures.

### Credit screen

**Screen conclusion.** The operating record is mixed: overall Q2 Adjusted EBITDA declined, while Regional segment Adjusted EBITDA increased and Las Vegas and Caesars Digital declined. [C3] The company reported compliance with specified financial covenants at June 30, 2026, but that statement does not supply covenant headroom or a post-transaction view. [C19] Issuer-specific governance behavior and transition evidence are not established by the merger disclosure or the fund’s investment mandate; these remain targeted evidence gaps. [C9, C14]

**Monitoring trigger:** transaction terms, capital allocation following the pending merger, issuer-specific governance developments, and current transition/sustainability evidence.

### Liquidity and forward-risk screen

**Screen conclusion.** Disclosed cash and borrowing capacity, six-month operating cash inflow, capex and estimated remaining-2026 lease payments provide a directional liquidity picture, not a liquidity bridge. [C3, C4, C5, C6, C7, C8, C19] Management says it expects current liquidity, including committed-facility availability and operating cash flows, to be sufficient for the next twelve months and beyond; this is a forward-looking issuer statement, not a completed liquidity bridge. [C20] The reported facility capacity is not independently reconciled here to all availability conditions, uses, restricted cash or post-reporting changes. Interest-rate exposure is described for variable-rate borrowings, but a complete hedge inventory and downside sensitivity are not supplied. **Monitoring trigger:** facility availability, debt service, lease outflows, cash conversion and variable-rate funding costs.

### Security opportunity screen

**Screen conclusion.** The market evidence is a dated last trade, not an executable quote or relative-value comparison. [C10, C11, C12] The indenture describes senior secured notes and first-priority lien sharing, but the underlying collateral/intercreditor package is not fully present in the delivered sources. [C15, C16] Posture: **INSUFFICIENT_INFORMATION** for a market/recovery opportunity screen; this is not a security recommendation. **Trigger:** current two-sided pricing and size, comparable spread basis, and the current security/collateral record.

### Creditor-document screen

**Screen conclusion.** The base indenture and two supplements establish a useful document starting point, and issuer disclosure describes a senior-secured guarantee/collateral package. [C15, C16, C17, C18] The full security documents, current collateral schedule and intercreditor agreement are absent; no capacity, compliance or recovery conclusion follows from this limited document set. Posture: **INSUFFICIENT_INFORMATION**. **Upgrade priority:** obtain and review the full operative document set, then test capacity and pressure points under the appropriate FULL owners.

### Analytical appendix — complete canonical registers

#### TL10.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; Q2 2026 issuer report | Form 10-Q [C1, C3, C4, C5, C6, C7, C8, C9, C18, C19, C20] | CP-1; CP-1B | Quarter and six months ended June 30, 2026 | PARTIAL | SOURCE_BASIS; EARNINGS_MARGIN_CHANGE; CASH_CONVERSION; LEVERAGE_COVERAGE; LIQUIDITY_MATURITIES; KPI_COMPARABILITY | Current post-quarter results and transaction financing are not supplied. |
| Caesars 6.500% Senior Secured Notes due 2032 | Indenture and supplements [C15, C16, C17, C18] | CP-1; CP-1B | February 6, 2024; March 1, 2024; August 23, 2024 | PARTIAL | SOURCE_BASIS; LEVERAGE_COVERAGE; LIQUIDITY_MATURITIES | Base indenture and supplements are supplied; full security/intercreditor source set is not. |

#### TL10.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| SOURCE_BASIS | Source and basis | CP-1; CP-1B | HIGH | PARTIAL | DEEPEN | 5 | Q2 issuer statements, note terms and a dated portfolio schedule are available; fund position is dated June 30 and the complete underwriting source set is absent. | 10-Q; indenture; fund schedule [C1, C6, C12, C13] | CP-1 |
| EARNINGS_MARGIN_CHANGE | Earnings and margin change | CP-1B | HIGH | SUFFICIENT | DEEPEN | 3 | Revenue increased year over year, but consolidated Adjusted EBITDA fell; segment movement is uneven. | 10-Q [C1, C3] | CP-1B |
| CASH_CONVERSION | Cash conversion | CP-1; CP-1B | HIGH | PARTIAL | DEEPEN | 4 | Six-month operating cash flow was slightly lower year over year; capex was also lower, and a normalized cash-conversion series is not established. | 10-Q [C4, C5] | CP-1B |
| LEVERAGE_COVERAGE | Leverage and coverage | CP-1; CP-1B | HIGH | PARTIAL | DEEPEN | 2 | The filing reports substantial debt and estimated debt-service requirements; available materials do not provide a complete leverage/coverage trend on consistent definitions. | 10-Q [C6, C7] | CP-1B |
| LIQUIDITY_MATURITIES | Liquidity and maturities | CP-1 | HIGH | PARTIAL | GAP_ONLY | 1 | [Insufficient Information] — a current, fully reconciled liquidity and maturity assessment is not available in the supplied materials. | 10-Q [C6, C7, C19, C20] | CP-1 |
| KPI_COMPARABILITY | KPI and comparability quality | CP-1B | MEDIUM | PARTIAL | SUMMARIZE | 6 | The filing identifies Adjusted EBITDA as a non-GAAP measure; its definition should not be assumed to match debt-agreement definitions. | 10-Q; issuer release [C3] | — |

#### TL10.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | MIXED | Revenue rose, Adjusted EBITDA fell, and six-month operating cash generation was slightly lower; debt remained substantial. [C1, C3, C4, C6] | Earnings resilience, leverage and policy changes can affect debt service and refinancing capacity. | Track cash conversion, debt service and transaction developments; complete FULL work before relying on a directional credit conclusion. | Medium | 10-Q [C1, C3, C4, C6, C7, C8, C9] |

#### TL10.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| SOURCE_BASIS | Current position/source perimeter | Current position and full underwriting source set | Determines whether dated issuer and holding evidence remain applicable. | Current portfolio holdings and complete underwriting pack | CP-1 | canonical financial source basis | Yes |
| EARNINGS_MARGIN_CHANGE | Full earnings normalization | Consistent period history and debt-definition reconciliation | Could change the assessment of recurring earnings and margin trend. | Filed financial history and applicable debt definitions | CP-1B | canonical earnings and margin analysis | Yes |
| CASH_CONVERSION | Cash conversion | Matching-period normalized CFO, capex and cash uses | Affects FCF durability and debt-service capacity. | Filed cash-flow history and supporting schedules | CP-1B | canonical cash-conversion analysis | Yes |
| LEVERAGE_COVERAGE | Consistent leverage and coverage | Defined leverage/coverage inputs and full period history | Affects refinancing capacity and debt-service assessment. | Debt schedule, filed financials and governing definitions | CP-1B | canonical leverage and coverage analysis | Yes |
| LIQUIDITY_MATURITIES | Material liquidity gap | Current accessible liquidity, maturity schedule, commitments and uses | Required to assess near-term liquidity and refinancing pressure. | Current issuer liquidity/debt schedules and facility documents | CP-1 | canonical liquidity and maturity analysis | Yes |

#### TL20.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; operating, debt and transaction disclosures | Q2 Form 10-Q and issuer results release [C1, C3, C6, C8, C9, C18] | CP-2; CP-2C | Q2 and six months ended June 30, 2026 | PARTIAL | BUSINESS_DURABILITY; MARGIN_FCF_RESILIENCE; LEVERAGE_REFINANCING_CONTEXT; GOVERNANCE_SPONSOR_BEHAVIOR; FINANCIAL_POLICY_CAPITAL_ALLOCATION | No full historical credit package or current transaction financing is supplied. |
| Issuer sustainability/transition evidence | Fund prospectus describes the fund’s mandate, not issuer analysis [C14] | CP-2F | Prospectus dated May 31, 2026 | MISSING | ESG_TRANSITION | Fund criteria do not establish Caesars-specific ESG or transition performance. |

#### TL20.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| BUSINESS_DURABILITY | Business durability | CP-2 | MEDIUM | PARTIAL | SUMMARIZE | 5 | Reported Q2 revenue increased, but segment direction varied; a fuller durable-revenue and competitive-position review is not supplied. | 10-Q [C1] | — |
| MARGIN_FCF_RESILIENCE | Margin and FCF resilience | CP-2 | HIGH | PARTIAL | DEEPEN | 1 | Consolidated Adjusted EBITDA declined year over year while operating cash flow was slightly lower; the cash-flow record needs FULL analysis. | 10-Q [C3, C4] | CP-2 |
| LEVERAGE_REFINANCING_CONTEXT | Leverage and refinancing context | CP-2 | HIGH | PARTIAL | DEEPEN | 2 | Debt and scheduled service remain material; current ratings and complete refinancing/liquidity analysis are not present. | 10-Q [C6, C7] | CP-2 |
| GOVERNANCE_SPONSOR_BEHAVIOR | Governance and sponsor behavior | CP-2C | HIGH | MISSING | GAP_ONLY | 3 | [Insufficient Information] — issuer-specific governance conduct and sponsor behavior evidence is not included in the delivered set. | 10-Q merger disclosure [C8, C9] | CP-2C |
| FINANCIAL_POLICY_CAPITAL_ALLOCATION | Financial policy and capital allocation | CP-2; CP-2C | HIGH | PARTIAL | DEEPEN | 4 | A pending merger is disclosed, but the supplied filing does not establish later status, financing or pro forma capital allocation. | 10-Q [C8, C9] | CP-2C |
| ESG_TRANSITION | ESG and transition transmission | CP-2F | MEDIUM | MISSING | GAP_ONLY | 6 | [Insufficient Information] — issuer-specific ESG, transition-risk and related financial-transmission evidence is not included in the delivered set. | No issuer ESG source; fund mandate is not issuer evidence [C14] | CP-2F |

#### TL20.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | MIXED | Revenue rose, Adjusted EBITDA fell, and a merger agreement is reported without transaction financing in the supplied filing. [C1, C3, C8, C9] | Earnings resilience, leverage and policy changes can affect debt service and refinancing capacity. | Treat the issuer screen as mixed; prioritize full margin/FCF and transaction-policy work, without inferring governance behavior from the event alone. | Medium | 10-Q [C1, C3, C4, C6, C8, C9] |

#### TL20.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| MARGIN_FCF_RESILIENCE | EBITDA/cash-flow divergence | Normalized margin, FCF and cash-use history | Determines earnings resilience and cash available for creditors. | Filed financials and cash-flow support | CP-2 | fundamental credit analysis | Yes |
| LEVERAGE_REFINANCING_CONTEXT | Debt/refinancing pressure | Current rating updates, debt schedule, maturities and consistent ratios | Determines refinancing and debt-service vulnerability. | Current debt and ratings sources | CP-2 | leverage/refinancing assessment | Yes |
| GOVERNANCE_SPONSOR_BEHAVIOR | Issuer-specific conduct evidence absent | Governance history and transaction conduct evidence | Could alter creditor alignment and event-risk assessment. | Issuer filings and relevant governance/transaction records | CP-2C | governance and sponsor-behavior analysis | Yes |
| FINANCIAL_POLICY_CAPITAL_ALLOCATION | Merger terms not updated | Current transaction status, financing and pro forma policy | Could alter leverage, distributions and creditor risk. | Current merger filings and financing disclosures | CP-2C | capital-allocation and creditor-alignment analysis | Yes |
| ESG_TRANSITION | Issuer transition evidence absent | Issuer-specific environmental, social and transition data | Required to determine material ESG transmission to cash flow or risk. | Issuer sustainability/transition disclosures | CP-2F | ESG and transition analysis | Yes |

#### TL23.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; cash, debt service and capex disclosures | Q2 Form 10-Q [C3, C4, C5, C6, C7, C8, C19, C20] | CP-2D; CP-2E; CP-2G | June 30, 2026; remainder-2026 estimates as disclosed | PARTIAL | ACCESSIBLE_LIQUIDITY_USES; WORKING_CAPITAL_CAPEX_CASH_BURN; RATES_HEDGES; FX_COMMODITY_INFLATION; BASE_DOWNSIDE_TRAJECTORY; BREAKPOINTS_REFINANCING | No full liquidity bridge, hedge inventory, exposure sensitivity or downside forecast supplied. |

#### TL23.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| ACCESSIBLE_LIQUIDITY_USES | Accessible liquidity and uses | CP-2D | HIGH | PARTIAL | DEEPEN | 1 | Cash and borrowing capacity are disclosed alongside near-term debt and lease uses, but availability and uses are not reconciled into a full bridge. | 10-Q [C6, C7, C8, C19, C20] | CP-2D |
| WORKING_CAPITAL_CAPEX_CASH_BURN | Working capital, capex and cash burn | CP-2D | HIGH | PARTIAL | DEEPEN | 2 | Six-month operating cash flow and capex are reported; a consistent cash-burn and working-capital sensitivity is not supplied. | 10-Q [C4, C5] | CP-2D |
| RATES_HEDGES | Rates and hedges | CP-2E | HIGH | MISSING | GAP_ONLY | 3 | [Insufficient Information] — a complete current variable-rate exposure and hedge inventory is not included in the supplied materials. | No complete hedge schedule supplied | CP-2E |
| FX_COMMODITY_INFLATION | FX, commodity and inflation | CP-2E | MEDIUM | MISSING | GAP_ONLY | 4 | [Insufficient Information] — current issuer exposures, pass-through and sensitivities for FX, commodities and inflation are not supplied. | No exposure/sensitivity schedule supplied | CP-2E |
| BASE_DOWNSIDE_TRAJECTORY | Base and downside trajectory | CP-2G | HIGH | MISSING | GAP_ONLY | 5 | [Insufficient Information] — a source-grounded forward base/downside trajectory is not included in the delivered set. | No forecast or downside case supplied | CP-2G |
| BREAKPOINTS_REFINANCING | Breakpoints and refinancing | CP-2D; CP-2E; CP-2G | HIGH | PARTIAL | GAP_ONLY | 6 | [Insufficient Information] — quantified downside breakpoints and refinancing triggers are not established by the supplied period disclosures. | 10-Q debt/liquidity context [C6, C7, C19] | CP-2G |

#### TL23.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | WATCH | The filing discloses cash/facility capacity, debt service and lease payments, but does not provide a complete forward bridge or sensitivity case. Management expects disclosed current liquidity to be sufficient for the next twelve months and beyond. [C6, C7, C8, C19, C20] | Liquidity is affected by accessible facilities, debt maturities, leases, capex and cash conversion. | Monitor facility access, cash uses and financing costs; obtain FULL liquidity and sensitivity work before judging downside resilience. | Medium | 10-Q [C4, C5, C6, C7, C8, C19, C20] |

#### TL23.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| ACCESSIBLE_LIQUIDITY_USES | Liquidity is not bridged | Restricted/unrestricted cash, conditions to facility availability, maturities and uses | Determines near-term ability to meet obligations. | Current liquidity schedules and facility documents | CP-2D | liquidity bridge | Yes |
| WORKING_CAPITAL_CAPEX_CASH_BURN | Cash conversion is not normalized | Working-capital movements, maintenance/growth capex and recurring cash needs | Determines FCF durability and cash available for debt service. | Filed cash-flow schedules and capex detail | CP-2D | cash-use analysis | Yes |
| RATES_HEDGES | Hedge/exposure inventory absent | Variable-rate debt balances, reset terms, swaps/caps and hedge maturities | Determines debt-service sensitivity to rates. | Current debt and hedge schedules | CP-2E | rates and hedge analysis | Yes |
| FX_COMMODITY_INFLATION | Exposure data absent | Currency/commodity exposure, cost pass-through and sensitivity | Determines margin and cash-flow vulnerability to cost shocks. | Issuer risk disclosures and sensitivity support | CP-2E | macro and exposure analysis | Yes |
| BASE_DOWNSIDE_TRAJECTORY | Forward case absent | Source-grounded operating and financial base/downside inputs | Determines likely liquidity and refinancing trajectory under stress. | Current forecast and operating assumptions | CP-2G | forward credit case | Yes |
| BREAKPOINTS_REFINANCING | Trigger levels absent | Maturity wall, facility conditions and downside refinancing needs | Determines when liquidity pressure could become acute. | Current debt documents, forecasts and liquidity schedule | CP-2G | breakpoint/refinancing analysis | Yes |

#### TL30.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars 6.500% Senior Secured Notes due 2032; CUSIP 12769GAC4 | FINRA observation [C10, C11, C12]; issuer indenture [C15] | CP-3D; CP-3A; CP-3 | Observed October 2, 2026; last trade October 1, 2026 | PARTIAL | DATED_MARKET_SNAPSHOT; CURVE_COMPARABLE_COMPENSATION; LIQUIDITY_TECHNICALS; STRUCTURAL_RECOVERY_PROTECTION; DOWNSIDE_LME_EXPOSURE; INTEGRATED_SCREENING_POSTURE | One last-trade observation; no two-sided quote, curve, size or complete collateral package. |
| Disclosed fund position | Fund portfolio schedule [C12, C13] | CP-3D; CP-3A; CP-3 | June 30, 2026 | PARTIAL | DATED_MARKET_SNAPSHOT; LIQUIDITY_TECHNICALS | Does not establish a current position as of analysis date. |

#### TL30.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| DATED_MARKET_SNAPSHOT | Dated market snapshot | CP-3D | HIGH | PARTIAL | DEEPEN | 1 | FINRA displays a last trade dated October 1, 2026; it is not a bid, mid, ask or evaluated price. | FINRA [C10, C11, C12] | CP-3D |
| CURVE_COMPARABLE_COMPENSATION | Curve and comparable compensation | CP-3D; CP-3 | HIGH | MISSING | GAP_ONLY | 2 | [Insufficient Information] — comparable spread, benchmark curve and matched-instrument data are not supplied. | FINRA observed fields [C12] | CP-3D |
| LIQUIDITY_TECHNICALS | Liquidity and technicals | CP-3D | HIGH | MISSING | GAP_ONLY | 3 | [Insufficient Information] — trade size, bid/ask, dealer quote and trading-depth evidence are not supplied. | FINRA observed fields [C12] | CP-3D |
| STRUCTURAL_RECOVERY_PROTECTION | Structural and recovery protection | CP-3A | HIGH | PARTIAL | DEEPEN | 4 | The indenture describes senior-secured notes and equal ranking with senior debt; underlying collateral and intercreditor materials are not supplied. | Indenture [C15] | CP-3A |
| DOWNSIDE_LME_EXPOSURE | Downside and LME exposure | CP-3A; CP-3 | HIGH | MISSING | GAP_ONLY | 5 | [Insufficient Information] — current liability-management, downside and recovery evidence is not included in the delivered set. | No current LME/recovery source supplied | CP-3A |
| INTEGRATED_SCREENING_POSTURE | Integrated screening posture | CP-3D; CP-3A; CP-3 | HIGH | PARTIAL | GAP_ONLY | 6 | [Insufficient Information] — the dated market, current holding and full protection evidence are not jointly established. | FINRA and fund schedule [C10, C11, C12, C13] | CP-3 |

#### TL30.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | INSUFFICIENT_INFORMATION | The observed price is a last trade and the summary omits spread, benchmark curve, dealer quote and trade size; the holding snapshot is June 30. [C10, C11, C12, C13] | Market compensation and liquidity cannot be assessed without a comparable quote; recovery depends on complete structural evidence. | Do not infer relative value or execution quality; obtain current quotes and full protection evidence in a linked FULL run. | Low | FINRA; fund schedule; indenture [C10, C11, C12, C13, C15] |

#### TL30.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| DATED_MARKET_SNAPSHOT | Single last trade | Current quote timestamp, bid/ask, side, size and instrument confirmation | Establishes current market compensation and freshness. | Dated dealer/market quote with trade or quote size | CP-3D | market snapshot | Yes |
| CURVE_COMPARABLE_COMPENSATION | No comparison basis | Benchmark curve, spread and matched comparable set | Determines compensation relative to duration and credit risk. | Dated market data and comparable instruments | CP-3D | curve/comparables | Yes |
| LIQUIDITY_TECHNICALS | Trading-depth fields absent | Bid/ask depth, trade sizes and liquidity observations | Determines execution and liquidity risk. | Dated transaction/quote and market technicals | CP-3D | liquidity technicals | Yes |
| STRUCTURAL_RECOVERY_PROTECTION | Security documents incomplete | Current collateral schedule, security documents and intercreditor terms | Determines lien scope and recovery sensitivity. | Executed security/intercreditor documents | CP-3A | recovery/protection analysis | Yes |
| DOWNSIDE_LME_EXPOSURE | Downside evidence absent | Current debt structure, liability-management activity and downside case | Determines potential impairment or restructuring exposure. | Current issuer debt and transaction documents | CP-3A | downside/LME analysis | Yes |
| INTEGRATED_SCREENING_POSTURE | Evidence not contemporaneous | Current holding, market snapshot and structural evidence | Determines whether market and recovery signals can be combined for selection. | Current holdings plus full market/legal source set | CP-3 | integrated selection screen | Yes |

#### TL40.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars 6.500% Senior Secured Notes due 2032 | Base indenture and supplements [C15, C16, C17, C18] | CP-4; CP-4B; CP-4A | February 6, 2024; March 1, 2024; August 23, 2024 | PARTIAL | CONTROLLING_DOCUMENT_AVAILABILITY; PROTECTION_WEAKNESS_FLAGS; ENTITY_GUARANTEE_COLLATERAL; LEAKAGE_PRIMING_FLAGS; CAPACITY_AVAILABILITY; PRESSURE_POINT_UPGRADE_PRIORITY | Security, intercreditor, current collateral and complete credit documents are not supplied. |
| Issuer debt/security summary | Q2 Form 10-Q [C6, C16, C18] | CP-4; CP-4B; CP-4A | June 30, 2026 | PARTIAL | ENTITY_GUARANTEE_COLLATERAL; CAPACITY_AVAILABILITY; PRESSURE_POINT_UPGRADE_PRIORITY | Summary disclosure does not replace operative security documents or capacity calculations. |

#### TL40.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| CONTROLLING_DOCUMENT_AVAILABILITY | Controlling-document availability | CP-4 | HIGH | PARTIAL | DEEPEN | 1 | Base indenture and two supplements are available, but the complete operative credit, security and intercreditor source set is not. | Indenture/supplements [C15, C16, C17, C18] | CP-4 |
| PROTECTION_WEAKNESS_FLAGS | Protection and weakness flags | CP-4 | HIGH | PARTIAL | DEEPEN | 2 | The available indenture describes senior-secured ranking; provision-level protection assessment requires the complete operative documents. | Indenture [C15] | CP-4 |
| ENTITY_GUARANTEE_COLLATERAL | Entity, guarantee and collateral coverage | CP-4B | HIGH | PARTIAL | DEEPEN | 3 | Issuer disclosure describes guarantees by material wholly-owned domestic subsidiaries and a substantially-all-assets package subject to exceptions. | 10-Q [C16] | CP-4B |
| LEAKAGE_PRIMING_FLAGS | Leakage and priming flags | CP-4; CP-4B | HIGH | MISSING | GAP_ONLY | 4 | [Insufficient Information] — current collateral sharing, permitted lien activity and entity-level leakage evidence are not supplied. | Missing security/intercreditor documents | CP-4B |
| CAPACITY_AVAILABILITY | Capacity availability | CP-4A | HIGH | MISSING | GAP_ONLY | 5 | [Insufficient Information] — current covenant capacity and basket usage evidence are not supplied. | Complete current debt documents and compliance inputs | CP-4A |
| PRESSURE_POINT_UPGRADE_PRIORITY | Pressure point and upgrade priority | CP-4A | HIGH | PARTIAL | GAP_ONLY | 6 | [Insufficient Information] — operative capacity inputs and current pressure-point calculations are not included. | Indenture/issuer debt summary [C6, C15] | CP-4A |

#### TL40.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | INSUFFICIENT_INFORMATION | The indenture and supplements are supplied, and issuer disclosure summarizes a senior-secured guarantee/collateral package; underlying security/intercreditor documents are absent. [C15, C16, C17, C18] | Entity guarantees and collateral can affect structural support and recovery; lien sharing and capacity require operative terms. | Treat document coverage as partial; obtain the complete legal/security package before a creditor conclusion. | Medium | Indenture, supplements and 10-Q [C15, C16, C17, C18] |

#### TL40.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| CONTROLLING_DOCUMENT_AVAILABILITY | Operative source set incomplete | Current credit agreement, security documents, intercreditor agreements and schedules | Determines which terms govern the secured claim. | Complete executed and effective document set | CP-4 | controlling-document analysis | Yes |
| PROTECTION_WEAKNESS_FLAGS | Full terms not available | Complete provision-level protections and exceptions | Determines creditor protections and potential weaknesses. | Complete indenture/security/intercreditor set | CP-4 | provision-level protection screen | Yes |
| ENTITY_GUARANTEE_COLLATERAL | Entity/collateral perimeter not mapped | Current guarantor list, collateral schedule and excluded assets | Determines guarantee reach and collateral coverage. | Current entity chart and security schedules | CP-4B | entity/guarantee/collateral map | Yes |
| LEAKAGE_PRIMING_FLAGS | No current lien/leakage mapping | Permitted liens, subsidiary debt, lien sharing and leakage evidence | Determines priming or value leakage risk. | Current debt/security documents and subsidiary perimeter | CP-4B | leakage/priming map | Yes |
| CAPACITY_AVAILABILITY | Capacity inputs unavailable | Current debt, basket usage, ratios and transaction adjustments | Determines available debt/covenant capacity. | Current covenant calculations and source inputs | CP-4A | covenant capacity calculation | Yes |
| PRESSURE_POINT_UPGRADE_PRIORITY | No capacity/pressure calculation | Current compliance data, liquidity needs and relevant baskets | Determines which restriction or capacity test binds first. | Current compliance certificate, debt schedule and transaction data | CP-4A | capacity pressure-point analysis | Yes |

## Evidence Trace

| claim | marker | document | page |
|---|---|---|---:|
| Q2 revenue, operating cash and capital spending comparisons | [C1, C4, C5] | Caesars Entertainment, Inc. Form 10-Q | 2; 4 |
| GAAP net loss comparison and consolidated Adjusted EBITDA comparison | [C2, C3] | Caesars Entertainment, Inc. Form 10-Q | 3; 16 |
| Debt principal and liquidity context | [C6, C7] | Caesars Entertainment, Inc. Form 10-Q | 22; 9 |
| Estimated remaining-2026 lease payments | [C8] | Caesars Entertainment, Inc. Form 10-Q | 22 |
| Pending merger disclosure | [C9] | Caesars Entertainment, Inc. Form 10-Q | 5 |
| Last-trade observation, date and its limitations | [C10, C11, C12] | FINRA Fixed Income Security Lookup observation | 1 |
| Disclosed fund note position and as-of date | [C13] | Fund Portfolio of Investments | 4; 1 |
| Fund lower-rated investment mandate | [C14] | Fund Prospectus and SAI | 3 |
| Note ranking, guarantee and collateral summary | [C15, C16] | Indenture; Form 10-Q | 43; 11 |
| First supplemental indenture provision replacement | [C17] | First Supplemental Indenture | 1 |
| Second supplemental indenture date | [C18] | Second Supplemental Indenture | 1 |
| Financial-covenant compliance statement | [C19] | Caesars Entertainment, Inc. Form 10-Q | 10 |
| Issuer liquidity sufficiency expectation | [C20] | Caesars Entertainment, Inc. Form 10-Q | 22 |

## Source Registry

- **Issuer primary financial source:** Caesars Entertainment, Inc. Form 10-Q for the quarter ended June 30, 2026; used for operating results, cash flow, debt, liquidity, covenants and the disclosed merger agreement. [C1, C2, C3, C4, C5, C6, C7, C8, C9, C19, C20]
- **Issuer contractual sources:** February 6, 2024 indenture and March 1 and August 23, 2024 supplements; useful for stated note and guarantee context, but not a complete security/intercreditor package. [C15, C16, C17, C18]
- **Issuer corroboration:** Q2 2026 results release; secondary corroboration of reported issuer results. [C3]
- **Market observation:** FINRA public fixed-income summary observed October 2, 2026, reporting an October 1 last trade; summary lacks a two-sided quote and several market-comparison fields. [C10, C11, C12]
- **Fund sources:** June 30, 2026 portfolio schedule and May 31, 2026 prospectus/SAI; the schedule evidences a period-end disclosed holding, not current ownership. [C13, C14]

## Gaps & Conflicts

1. **Current position:** the fund schedule is dated June 30, 2026; it does not establish ownership or size on October 2. [C13]
2. **Market basis:** the FINRA record is a last trade, not an executable bid/ask or matched spread comparison; absent fields are recorded in the CP-L30 gaps register. [C10, C11, C12]
3. **Merger:** the Q2 filing reports a May 27 agreement; later status, transaction financing and pro forma leverage are not in the delivered materials. [C9]
4. **Cash-flow comparability:** reported six-month operating cash flow and capex are available, but the delivered evidence is not a normalized FCF series or forward bridge. [C4, C5]
5. **Legal/security scope:** base indenture and two supplements are not the full security, intercreditor, collateral-schedule and current capacity package. [C15, C16, C17, C18]
6. **Rating dates:** FINRA displays agency ratings with differing last-rated dates; this is a coverage limitation, not a like-for-like rating conflict. No current same-date multi-agency set is established in the supplied market summary. [C12]

## QA Validation

- Identity and period: **PASS** — issuer, Q2 2026 reporting period, analysis date and CP-0 lineage match the supplied run context.
- Scope gate: **PARTIAL** — issuer, fund, indenture and dated market evidence are available; current holdings, complete market comparables, transaction financing, current collateral documents and full forward sensitivities are not.
- Register coverage: **PASS** — TL10.1–TL10.4, TL20.1–TL20.4, TL23.1–TL23.4, TL30.1–TL30.4 and TL40.1–TL40.4 are present; all five topic registers contain six canonical topics and each decision screen contains OVERALL.
- Ownership and limits: **PASS** — this is SCREENING_ONLY; no canonical financial history, normalized financials, full forecast, legal opinion, exact capacity, recovery value or investment recommendation is emitted.
- Source/citation discipline: **PASS** — direct evidence is cited by marker; citations quote only supplied evidence. Analytical conclusions are separated from disclosed figures and source limitations.
- Confidence and QA state: **Restricted** — 59 / Low; restricted by the partial source gate and missing decision-material inputs.
- Canonical filename: **CZR_CP-L10_20261002.md**.
- Host validation follows this response; no host validator execution or result is claimed.