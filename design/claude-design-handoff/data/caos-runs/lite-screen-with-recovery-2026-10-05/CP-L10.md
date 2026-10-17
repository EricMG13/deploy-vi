---
module_id: "CP-L10"
module_name: "LiteFinancialChangeScreen"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_FULL_CREDIT_SCREEN"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-L10-5e309f4e58c70937"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_FULL_CREDIT_SCREEN-02-CP-L10"
credit_os_invocation_sha256: "bc1f4e3d530d36332be06da615133c5d310336b9bbeb26aeb396729fb142b905"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "dcb45fd922bd40cf339a42308e91a3fac8f6e23b9f198f147d86c85f73a15eeb"
confidence_score: 55
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "MISSING_DATED_MARKET_DATA", "CURRENT_LEASE_AND_CREDIT_DOCUMENTS_NOT_SUPPLIED"]
validation_warnings: ["FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "SOURCE_LIMITED", "LITE_FULL_UPGRADE_REQUIRED"]
downstream_consumers: ["CP-1C", "CP-2H", "CP-4C", "CP-5", "CP-5A"]
---

## Audit Summary

- **Canonical handoff:** `CZR_CP-L10_20261002.md`.
- **Run status:** `COMPLETE_WITH_GAPS`; all five LITE screens are completed for their screening scope.
- **Structured outcome:** `FULL_UPGRADE_REQUIRED`. This is a screening outcome only and does not launch or mutate a FULL run.
- **Decision scope and execution basis:** `SCREENING_ONLY`; `MIXED` (direct source evidence plus accepted CP-0 lineage context). Only the delivered evidence is used for findings.
- **Confidence:** 55 — Low. Calibration: 30 material claims assessed as 15 Directly Sourced, 10 Analyst Inference and 5 Insufficient Information; E=63.3, C=100, S=0.7, giving 54.6 before integer rounding. The principal limitation is missing or incomplete evidence for annual context, current operative documents, forecast/downside, market data and comparability.
- **Screen postures:** Financial change — `MIXED`; credit — `MIXED`; liquidity and forward risk — `WATCH`; market and recovery — `INSUFFICIENT_INFORMATION`; legal structure and capacity — `INSUFFICIENT_INFORMATION`.
- **Primary monitoring trigger:** deterioration in Las Vegas and consolidated Adjusted EBITDA alongside cash uses, scheduled debt service, floating-rate exposure and lease payments; update the screen when current market, forecasts and operative documents are available.
- **Host validation:** host vendor validation and register completeness checks follow this answer. No host result or exit status is claimed.

## Analysis

### Financial change screen

Caesars’ Q2 2026 filing supports a mixed financial-change screen: consolidated revenue increased 3.0% year over year, while consolidated Adjusted EBITDA declined and the Las Vegas segment recorded a marked EBITDA decline; Regional growth partly offset that pressure. [C1, C3, C4, C5, C6, C7] Cash from operations was broadly stable against the prior-year half, but capital spending, lease payments and debt service remain substantial competing demands on cash. [C8, C9, C12, C13] Leverage and liquidity cannot be reduced to a single comparable ratio here: the filing presents several debt and liquidity bases, and $6.0 billion of long-term variable-rate borrowing is exposed to rate movements. [C10, C11, C14, C15] The screen is restricted by the absent referenced 2025 Form 10-K and incomplete current credit and lease documents. [C2, C30]

The principal support is revenue growth and Regional EBITDA growth; the primary risk is the Las Vegas earnings decline combined with material cash obligations. The monitoring trigger is a further decline in segment EBITDA or operating cash generation, especially alongside upcoming maturities or higher variable-rate costs. The evidence supports directional screening, not a canonical financial history, normalized financials, or a full coverage calculation.

### Credit screen

The creditor screen is mixed. The filing documents a diversified property and segment base, but consolidated results conceal different directions across Las Vegas, Regional and Caesars Digital. [C4, C5, C6] Six-month operating cash flow remains positive, although the measure does not include all capital expenditure, interest, debt repayment and lease cash demands. [C8, C9, C12, C13, C19] Debt service, refinancing context and the completed-versus-pending merger evidence warrant FULL work; the Q2 filing describes the merger as conditional, while no later transaction-status evidence is present in the delivered materials. [C22]

The strongest contrary evidence to a pressured view is Regional growth, positive six-month operating cash flow and management’s stated liquidity expectation. [C6, C8, C31] Those facts temper, but do not resolve, the weakness in Las Vegas and the lack of full historical, forward, governance and ESG evidence. Monitor segment contribution, cash conversion and any subsequent merger-status disclosure.

### Liquidity and forward-risk screen

The reported June 30, 2026 cash balance was $965 million and the filing reports $1.9 billion of available CEI revolving borrowing capacity after stated reserves and other commitments. [C10, C11] Management states that current liquidity and operating cash flows are expected to fund operations, capital needs and debt service for at least twelve months, but this screen does not independently test that assertion. [C31] Principal and interest debt service is estimated at $425 million for the remainder of 2026, and lease payments to VICI and GLPI are estimated at $687 million for that period. [C12, C13] Six billion dollars of variable-rate borrowings and the absence of cash-flow hedges make rate exposure a decision-relevant monitoring item. [C14, C15, C16]

The key breakpoint is the combination of cash generation, lease payments, debt maturities and refinancing availability; a source-grounded downside trajectory and sensitivity analysis are not available. Escalate to the relevant FULL liquidity, rates and forecast owners before treating the stated liquidity outlook as a completed bridge or downside assessment.

### Security opportunity screen

The defined documentary scope includes the 6.500% senior secured notes due 2032 and the 6.000% senior notes due 2032 listed in the Q2 debt note. [C20] The delivered evidence contains no dated quote, yield, spread, curve, comparable, trade-size or market-liquidity observations for either issue. Accordingly, the screen cannot establish compensation, technicals or a market-driven selection posture. The 2032 secured-note indenture describes security and guarantees, but the available document set does not establish current perfection, current collateral value, complete priority arrangements or downside recovery. [C26, C27]

The appropriate screening posture is `INSUFFICIENT_INFORMATION`, not a security recommendation. A dated, security-specific market snapshot and current structural/recovery analysis are required before FULL selection work can answer whether compensation warrants escalation, monitoring or deprioritisation.

### Creditor-document screen

The delivered documents include the 2032 secured-note indenture and two supplements, plus the February 2024 incremental assumption agreement with a conformed credit agreement. [C28, C29, C30] The 10-Q states that first-lien facilities and secured notes are guaranteed by material wholly owned domestic subsidiaries and secured by substantially all property and assets, subject to exceptions. [C26] The indenture also records collateral, guarantor and release mechanics, while its disclosed document perimeter is not a substitute for the full current operative credit and lease-document set. [C27]

The document/creditor-risk posture is `INSUFFICIENT_INFORMATION`: capacity, current entity coverage, baskets and leakage/priming implications require FULL legal and capacity work. The trigger is delivery and reconciliation of current controlling documents and the supporting calculations; no legal conclusion or capacity amount is made in this screen.

### Analytical appendix — complete canonical registers

#### TL10.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; consolidated issuer | Form 10-Q, source 1ae6b04b-413a-4f14-b5da-362701a558fb [C1] | CP-1; CP-1B | Q2 and six months ended June 30, 2026 | PARTIAL | SOURCE_BASIS; EARNINGS_MARGIN_CHANGE; CASH_CONVERSION; LEVERAGE_COVERAGE; LIQUIDITY_MATURITIES; KPI_COMPARABILITY | Interim unaudited information; filing refers readers to the 2025 Form 10-K, which is not in the delivered evidence. [C2] |
| Caesars Entertainment, Inc.; consolidated cash flows and debt | Form 10-Q, pages 4, 9–10, 22–23 [C8, C11, C20] | CP-1; CP-1B | Six months ended / June 30, 2026 | PARTIAL | CASH_CONVERSION; LEVERAGE_COVERAGE; LIQUIDITY_MATURITIES | No complete historical series, independent forecast or full current credit and lease-document set. |
| Caesars Entertainment, Inc.; business and segment basis | Form 10-Q, pages 18–21 [C4, C5, C6, C17] | CP-1; CP-1B | Q2 2026 versus Q2 2025 | PARTIAL | EARNINGS_MARGIN_CHANGE; KPI_COMPARABILITY | Caesars Windsor and other asset purchases affect comparison; filing expressly says post-purchase information is not fully comparable. [C17] |

#### TL10.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| SOURCE_BASIS | Source and basis | CP-1, CP-1B | HIGH | PARTIAL | GAP_ONLY | 5 | [Insufficient Information] — the referenced 2025 Form 10-K and complete current credit and lease documents are not included in the delivered evidence. | 1ae6b04b-413a-4f14-b5da-362701a558fb; b24b47d6-6bfd-4248-b660-e867409dd303 [C2, C30] | CP-1 |
| EARNINGS_MARGIN_CHANGE | Earnings and margin change | CP-1B | HIGH | SUFFICIENT | DEEPEN | 4 | Q2 revenue rose 3.0%, but consolidated Adjusted EBITDA fell year over year; Las Vegas Adjusted EBITDA declined while Regional Adjusted EBITDA rose. Lower Las Vegas earnings transmit through consolidated debt-service capacity, while Regional growth partly offsets the pressure; FULL work should establish persistent versus period-specific drivers. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C3, C4, C5, C6, C7] | CP-1B |
| CASH_CONVERSION | Cash conversion | CP-1, CP-1B | HIGH | PARTIAL | DEEPEN | 2 | Six-month operating cash flow was $675 million versus $680 million; property and equipment purchases were $335 million versus $453 million. Positive operating cash flow supports liquidity, while investment and lease/debt demands compete for cash; FULL work must reconcile recurring conversion and uses. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C8, C9, C12, C13, C19] | CP-1B |
| LEVERAGE_COVERAGE | Leverage and coverage | CP-1, CP-1B | HIGH | PARTIAL | DEEPEN | 3 | The filing presents debt maturities and $6.0 billion of long-term variable-rate borrowing; covenant compliance was reported at June 30, 2026. Rate increases or earnings weakness can pressure debt service and refinancing capacity; FULL work must establish canonical debt basis, coverage and current covenant headroom. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C14, C20, C21] | CP-1B |
| LIQUIDITY_MATURITIES | Liquidity and maturities | CP-1, CP-1B | HIGH | PARTIAL | DEEPEN | 1 | Reported cash was $965 million and available CEI revolver borrowing capacity was $1.9 billion after stated commitments and reserves; stated remainder-2026 debt service and VICI/GLPI lease payments are $425 million and $687 million, respectively. Liquidity resources mitigate near-term pressure, but debt and lease uses plus the lack of a full bridge require FULL testing. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C10, C11, C12, C13] | CP-1 |
| KPI_COMPARABILITY | KPI and comparability quality | CP-1, CP-1B | HIGH | CONFLICTED | GAP_ONLY | 6 | [Insufficient Information] — complete annual comparatives and a consistently adjusted segment/perimeter series are not included in the delivered evidence. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C2, C17, C18] | CP-1B |

#### TL10.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | MIXED | Revenue increased while consolidated and Las Vegas Adjusted EBITDA declined; Regional Adjusted EBITDA increased. Operating cash flow was positive, with material disclosed capital, debt-service and lease uses. [C4, C5, C6, C8, C9, C12, C13] | Segment divergence and cash demands affect FCF durability, debt service and refinancing capacity. | Monitor Las Vegas and consolidated EBITDA, cash conversion, maturity funding and lease outflows; complete CP-1/CP-1B work before relying on a canonical history or coverage conclusion. | Medium | 1ae6b04b-413a-4f14-b5da-362701a558fb [C4, C5, C6, C8, C9, C12, C13] |

#### TL10.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| SOURCE_BASIS | Referenced annual filing and current operative agreements are absent. | 2025 Form 10-K; complete current credit agreement and governing leases | Period, perimeter and definition basis may change historical leverage and cash-use interpretation. | Filed 2025 Form 10-K; executed current credit and lease documents | CP-1 | Canonical financial history and source-basis reconciliation | true |
| EARNINGS_MARGIN_CHANGE | Segment EBITDA directions diverge; annual and normalized history is absent. | Annual history, complete segment bridge and period-specific earnings detail | Determines persistence of earnings pressure and debt-service capacity. | Complete issuer filings, schedules and supporting earnings definitions | CP-1B | Period-specific earnings and margin analysis | false |
| CASH_CONVERSION | Interim cash flow and capex do not establish recurring conversion after all fixed cash uses. | Full cash-flow history, cash interest/rent detail and matched-period cash-use reconciliation | Affects FCF durability and liquidity available for debt service. | Complete issuer filings and cash-flow/debt/lease schedules | CP-1B | Cash-conversion and FCF transmission analysis | false |
| LEVERAGE_COVERAGE | Canonical debt basis, current agreement terms and covenant calculations are incomplete. | Carrying-value reconciliation, current definitions, EBITDA/interest basis and compliance calculations | Changes leverage, coverage and refinancing pressure assessment. | Complete current credit documents and filed financial statements | CP-1B | Leverage, coverage and debt-service analysis | true |
| LIQUIDITY_MATURITIES | No independently tested bridge reconciles resources, uses, leases and maturities. | Current accessible cash/facility detail, dated uses and maturity funding plan | Determines liquidity runway and near-term refinancing needs. | Complete current filings, facility and lease schedules | CP-1 | Liquidity and maturity analysis | true |
| KPI_COMPARABILITY | Asset-purchase effects and KPI definition comparability remain unresolved. | Consistent perimeter, segment and Adjusted EBITDA definitions across annual and interim periods | Could alter inferred earnings and margin direction. | 2025 Form 10-K and full issuer reconciliation schedules | CP-1B | KPI definitions and comparability analysis | true |

#### TL20.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; consolidated issuer | Form 10-Q, source 1ae6b04b-413a-4f14-b5da-362701a558fb [C1, C4, C6] | CP-2; CP-2C; CP-2F | Q2 2026; June 30, 2026 | PARTIAL | BUSINESS_DURABILITY; MARGIN_FCF_RESILIENCE; LEVERAGE_REFINANCING_CONTEXT; GOVERNANCE_SPONSOR_BEHAVIOR; FINANCIAL_POLICY_CAPITAL_ALLOCATION; ESG_TRANSITION | Supports selected business and financial observations; does not supply full fundamental, governance or issuer-specific ESG evidence. |

#### TL20.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| BUSINESS_DURABILITY | Business durability | CP-2 | HIGH | PARTIAL | DEEPEN | 1 | Q2 revenue grew 3.0%; Regional EBITDA rose while Las Vegas EBITDA declined. Diversification cushions but does not eliminate segment-level earnings pressure; FULL work should test durability and concentration through a complete history. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C4, C5, C6] | CP-2 |
| MARGIN_FCF_RESILIENCE | Margin and FCF resilience | CP-2 | HIGH | PARTIAL | DEEPEN | 2 | Six-month operating cash flow was $675 million and capex was $335 million, while disclosed lease and debt-service needs remain material. Cash generation transmits to FCF durability only after recurring operating and financing uses are reconciled. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C8, C9, C12, C13, C19] | CP-2 |
| LEVERAGE_REFINANCING_CONTEXT | Leverage and refinancing context | CP-2 | HIGH | PARTIAL | DEEPEN | 3 | The filing reports a maturity schedule and substantial variable-rate borrowing, but does not provide the complete current-document and forecast set needed to assess leverage tolerance or market access. | 1ae6b04b-413a-4f14-b5da-362701a558fb; b24b47d6-6bfd-4248-b660-e867409dd303 [C14, C20, C30] | CP-2 |
| GOVERNANCE_SPONSOR_BEHAVIOR | Governance and sponsor behavior | CP-2C | MEDIUM | MISSING | GAP_ONLY | 4 | [Insufficient Information] — current issuer-specific evidence of governance conduct, sponsor behavior and creditor engagement is not included in the delivered materials. | No direct source delivered for the topic | CP-2C |
| FINANCIAL_POLICY_CAPITAL_ALLOCATION | Financial policy and capital allocation | CP-2, CP-2C | MEDIUM | PARTIAL | DEEPEN | 5 | No Q2 2026 share repurchases were reported; the filing also records a $100 million repurchase in Q2 2025. This limits evidence of current distributions but does not establish broader policy, transaction funding or creditor alignment. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C23, C24] | CP-2C |
| ESG_TRANSITION | ESG and transition transmission | CP-2F | MEDIUM | MISSING | GAP_ONLY | 6 | [Insufficient Information] — issuer-specific environmental, social, transition and sustainability-instrument evidence is not included in the delivered materials. | No direct source delivered for the topic | CP-2F |

#### TL20.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | MIXED | Q2 revenue increased, but Las Vegas EBITDA declined; Regional EBITDA increased. Interim cash flow is positive, while the delivered evidence does not establish the full policy, governance or ESG picture. [C4, C5, C6, C8, C22] | Mixed operating performance affects FCF durability and debt-service capacity; missing policy and issuer-specific evidence limit creditor-alignment assessment. | Maintain a mixed screening posture; CP-2, CP-2C and CP-2F must resolve the identified evidence gaps for a complete fundamental view. | Low | 1ae6b04b-413a-4f14-b5da-362701a558fb [C4, C5, C6, C8, C22] |

#### TL20.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| BUSINESS_DURABILITY | Segment growth and decline require full-period testing. | Annual operating history, complete segment and market evidence | Determines durable revenue, margin and cash support. | Complete issuer filings and supporting segment schedules | CP-2 | Fundamental durability analysis | false |
| MARGIN_FCF_RESILIENCE | Interim conversion is not a full FCF resilience assessment. | Full cash-flow history, recurring cash costs and forward operating evidence | Determines FCF resilience available for creditors. | Complete issuer filings and cash-use schedules | CP-2 | Margin and FCF resilience analysis | true |
| LEVERAGE_REFINANCING_CONTEXT | Debt, maturity and rate evidence lacks complete current terms and forecast context. | Current debt documents, full debt-service projections and lender/market access evidence | Determines refinancing capacity and leverage tolerance. | Current executed financing documents and issuer forecast | CP-2 | Leverage and refinancing-context analysis | true |
| GOVERNANCE_SPONSOR_BEHAVIOR | No issuer-specific conduct evidence is supplied. | Governance records, transaction updates and creditor-facing conduct evidence | Determines whether policy or execution behavior changes creditor risk. | Current issuer and transaction disclosures | CP-2C | Governance and sponsor-behavior analysis | true |
| FINANCIAL_POLICY_CAPITAL_ALLOCATION | Current repurchase disclosure does not establish broader policy. | Full policy, debt-funded distributions, M&A and transaction-financing evidence | Determines creditor alignment and financial-policy risk. | Current issuer filings, financing documents and transaction updates | CP-2C | Financial-policy and capital-allocation analysis | true |
| ESG_TRANSITION | No issuer-specific transmission evidence is supplied. | Issuer-specific ESG, transition and sustainability-instrument disclosures | Determines any material operating, funding or liability transmission. | Issuer disclosures and applicable instrument terms | CP-2F | ESG and transition-transmission analysis | true |

#### TL23.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; consolidated liquidity and debt perimeter | Form 10-Q, source 1ae6b04b-413a-4f14-b5da-362701a558fb [C10, C11, C12, C13, C14, C15, C16, C20, C31] | CP-2D; CP-2E; CP-2G | June 30, 2026; stated remainder-2026 uses | PARTIAL | ACCESSIBLE_LIQUIDITY_USES; WORKING_CAPITAL_CAPEX_CASH_BURN; RATES_HEDGES; FX_COMMODITY_INFLATION; BASE_DOWNSIDE_TRAJECTORY; BREAKPOINTS_REFINANCING | Reported balances and uses support directional screening; no complete forward case, exposure sensitivities or independent liquidity bridge is supplied. |

#### TL23.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| ACCESSIBLE_LIQUIDITY_USES | Accessible liquidity and uses | CP-2D | HIGH | PARTIAL | DEEPEN | 1 | The filing reports $965 million cash and $1.9 billion CEI revolver availability after stated commitments and reserves; management expects liquidity to be sufficient for at least twelve months. Accessibility and all uses are not independently bridged here. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C10, C11, C31] | CP-2D |
| WORKING_CAPITAL_CAPEX_CASH_BURN | Working capital, capex and cash burn | CP-2D | HIGH | PARTIAL | DEEPEN | 2 | Six-month operating cash flow was $675 million and property/equipment purchases were $335 million; remainder-2026 capex, lease payments and debt service are additional disclosed cash demands. Their net path is not established by these figures alone. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C8, C9, C12, C13] | CP-2D |
| RATES_HEDGES | Rates and hedges | CP-2E | HIGH | PARTIAL | DEEPEN | 3 | Long-term variable-rate borrowings were $6.0 billion, approximately 51% of consolidated long-term debt; no cash-flow hedges were reported at June 30, 2026. Rate changes can affect debt service; documented hedge and sensitivity analysis remains for FULL work. | 1ae6b04b-413a-4f14-b5da-362701a558fb [C14, C15, C16] | CP-2E |
| FX_COMMODITY_INFLATION | FX, commodity and inflation | CP-2E | MEDIUM | MISSING | GAP_ONLY | 4 | [Insufficient Information] — quantified issuer-specific foreign-exchange, commodity and inflation mismatch or pass-through evidence is not included in the delivered materials. | No direct source delivered for the topic | CP-2E |
| BASE_DOWNSIDE_TRAJECTORY | Base and downside trajectory | CP-2G | HIGH | MISSING | GAP_ONLY | 5 | [Insufficient Information] — a source-grounded base case, downside case and forecast trajectory are not included in the delivered materials. | No direct forecast source delivered | CP-2G |
| BREAKPOINTS_REFINANCING | Breakpoints and refinancing | CP-2D, CP-2E, CP-2G | HIGH | PARTIAL | DEEPEN | 6 | The filing’s debt-service schedule shows large scheduled maturities, while the revolver matures in 2028 and floating-rate exposure is material. These are monitoring points, not a modeled breakpoint or refinancing forecast. | 1ae6b04b-413a-4f14-b5da-362701a558fb; b24b47d6-6bfd-4248-b660-e867409dd303 [C14, C20, C30] | CP-2G |

#### TL23.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | WATCH | Reported cash and revolver capacity are material supports; debt service, rent, capex and variable-rate exposure are also material, and no sourced base/downside forecast is available. [C8, C9, C10, C11, C12, C13, C14, C15, C16, C20, C31] | Cash uses and rate sensitivity transmit through liquidity, debt service and refinancing capacity. | Watch cash conversion, availability and maturity funding; obtain CP-2D/2E/2G FULL work before relying on a forward liquidity conclusion. | Low | 1ae6b04b-413a-4f14-b5da-362701a558fb; b24b47d6-6bfd-4248-b660-e867409dd303 [C8, C9, C10, C11, C12, C13, C14, C15, C16, C20, C31] |

#### TL23.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| ACCESSIBLE_LIQUIDITY_USES | Reported capacity and management expectation have not been independently bridged. | Restricted/trapped cash, accessible facility terms, all dated uses and availability conditions | Determines usable liquidity and near-term payment capacity. | Current facility documents, issuer liquidity schedules and filings | CP-2D | Accessible-liquidity bridge | true |
| WORKING_CAPITAL_CAPEX_CASH_BURN | Cash flow and capex periods do not establish forward burn. | Working-capital components, committed capex, full lease and cash-use schedule | Determines cash absorption and liquidity flexibility. | Complete issuer cash-flow, capex and lease schedules | CP-2D | Working-capital, capex and cash-burn analysis | true |
| RATES_HEDGES | Floating-rate debt is material and no cash-flow hedge is reported. | Current borrowing terms, hedge contracts and documented sensitivity | Determines debt-service sensitivity to rate changes. | Current debt and hedge documents; issuer sensitivity disclosures | CP-2E | Rates and hedge exposure analysis | true |
| FX_COMMODITY_INFLATION | Issuer-specific exposure and pass-through data are absent. | Currency, commodity, inflation mismatch and pricing/pass-through evidence | Could affect operating cash flow and cost flexibility. | Issuer disclosures, contracts and operating exposure schedules | CP-2E | FX, commodity and inflation exposure analysis | true |
| BASE_DOWNSIDE_TRAJECTORY | No source-grounded forecast or downside trajectory is supplied. | Operating assumptions, dated forecast, downside case and cash-flow path | Determines forward liquidity and leverage breakpoint. | Issuer forecast and underlying source support | CP-2G | Base and downside trajectory | true |
| BREAKPOINTS_REFINANCING | Maturity schedule is disclosed but there is no integrated breakpoint analysis. | Current maturities, available funding, rate assumptions and downside trajectory | Determines refinancing timing and liquidity pressure point. | Current debt documents and CP-2D/2E/2G source-grounded inputs | CP-2G | Breakpoint and refinancing analysis | true |

#### TL30.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; 6.500% senior secured notes due 2032 and 6.000% senior notes due 2032 | Form 10-Q debt note, source 1ae6b04b-413a-4f14-b5da-362701a558fb [C20]; 2032 secured-note indenture, source 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 [C27] | CP-3D; CP-3A; CP-3 | Q2 2026 issuer debt disclosure; analysis date 2026-10-02 | PARTIAL | DATED_MARKET_SNAPSHOT; CURVE_COMPARABLE_COMPENSATION; LIQUIDITY_TECHNICALS; STRUCTURAL_RECOVERY_PROTECTION; DOWNSIDE_LME_EXPOSURE; INTEGRATED_SCREENING_POSTURE | Market quote, yield/spread, curve, comparable, trade-size and liquidity evidence is not present in the delivered evidence. |
| Dated market and comparable-source coverage | No direct dated quote or comparable source delivered | CP-3D; CP-3 | Required as of 2026-10-02 | MISSING | DATED_MARKET_SNAPSHOT; CURVE_COMPARABLE_COMPENSATION; LIQUIDITY_TECHNICALS | No market inference or security selection is supported without security-specific, dated observations. |

#### TL30.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| DATED_MARKET_SNAPSHOT | Dated market snapshot | CP-3D | HIGH | MISSING | GAP_ONLY | 1 | [Insufficient Information] — security-specific dated price, yield/spread, quote basis and freshness evidence is not included in the delivered materials. | No dated market source delivered | CP-3D |
| CURVE_COMPARABLE_COMPENSATION | Curve and comparable compensation | CP-3D, CP-3 | HIGH | MISSING | GAP_ONLY | 2 | [Insufficient Information] — dated curve, comparable compensation and definition-matched reference observations are not included in the delivered materials. | No dated market or comparable source delivered | CP-3D |
| LIQUIDITY_TECHNICALS | Liquidity and technicals | CP-3D | HIGH | MISSING | GAP_ONLY | 3 | [Insufficient Information] — current issue-level trade size, turnover, bid/ask and observable liquidity evidence is not included in the delivered materials. | No dated issue-level market source delivered | CP-3D |
| STRUCTURAL_RECOVERY_PROTECTION | Structural and recovery protection | CP-3A | HIGH | PARTIAL | DEEPEN | 4 | The 2032 secured-note indenture describes secured obligations and guarantees, but the delivered text does not establish current collateral perfection, value or recovery. These features can affect LGD; FULL work must reconcile current documents and collateral evidence. | 1ae6b04b-413a-4f14-b5da-362701a558fb; 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 [C26, C27] | CP-3A |
| DOWNSIDE_LME_EXPOSURE | Downside and LME exposure | CP-3A, CP-3 | HIGH | MISSING | GAP_ONLY | 5 | [Insufficient Information] — current debt-trading, restructuring, liability-management and downside-market evidence is not included in the delivered materials. | No current market or LME source delivered | CP-3A |
| INTEGRATED_SCREENING_POSTURE | Integrated screening posture | CP-3D, CP-3A, CP-3 | HIGH | MISSING | GAP_ONLY | 6 | [Insufficient Information] — an integrated dated market, compensation, technical and downside evidence set is not included in the delivered materials. | No integrated market evidence delivered | CP-3 |

#### TL30.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | INSUFFICIENT_INFORMATION | The issuer filing identifies two 2032 debt issues; the available indenture documents describe some secured-note terms. No dated market observations or complete current recovery evidence are delivered. [C20, C26, C27] | Market compensation and structural protection jointly affect relative value, security selection and recovery; either evidence gap prevents an integrated screen. | Do not rank, value or recommend a security. Obtain dated issue-level market evidence and FULL structural/recovery work before selection. | Insufficient Information | 1ae6b04b-413a-4f14-b5da-362701a558fb; 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 [C20, C26, C27] |

#### TL30.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| DATED_MARKET_SNAPSHOT | No current dated quote for the identified issues is supplied. | Security identifier, timestamp, quote/last-trade basis, price, yield and source | Determines freshness and market compensation baseline. | Dated issue-level quote or trade source | CP-3D | Dated market snapshot | true |
| CURVE_COMPARABLE_COMPENSATION | No curve or definition-matched comparable evidence is supplied. | Benchmark curve, comparable instruments, basis and dates | Determines whether compensation is adequate relative to alternatives. | Dated curve and source-verified comparable evidence | CP-3D | Curve and comparable compensation analysis | true |
| LIQUIDITY_TECHNICALS | No issue-level liquidity observations are supplied. | Trade size, bid/ask, turnover and market depth | Determines execution and technical risk. | Dated issue-level trading/technical source | CP-3D | Security liquidity and technical analysis | true |
| STRUCTURAL_RECOVERY_PROTECTION | Existing indenture text is not a current collateral or recovery analysis. | Current collateral perimeter, perfection evidence, intercreditor documents and recovery inputs | Determines structural protection and LGD. | Current executed security package, collateral records and FULL recovery inputs | CP-3A | Structural protection and recovery analysis | true |
| DOWNSIDE_LME_EXPOSURE | Current market and liability-management evidence is absent. | Dated debt-market observations, transaction evidence and downside inputs | Determines exposure to market dislocation and liability-management actions. | Current market data and transaction evidence | CP-3A | Downside and LME exposure analysis | true |
| INTEGRATED_SCREENING_POSTURE | The market and structural evidence sets are incomplete. | Dated market, curve, technical, protection and downside findings | Prevents an integrated issuer/security screen. | Complete CP-3D, CP-3A and CP-3 source set | CP-3 | Integrated screening analysis | true |

#### TL40.1 — Source and Scope Gate

| subject_identity | source_ref | source_owner_module | as_of_or_period | scope_status | topics_supported | limitation |
|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc.; 6.500% senior secured notes due 2032 | Base indenture and two supplemental indentures [C27, C28, C29] | CP-4; CP-4B; CP-4A | Executed 2024 documents; Q2 2026 issuer context | PARTIAL | CONTROLLING_DOCUMENT_AVAILABILITY; PROTECTION_WEAKNESS_FLAGS; ENTITY_GUARANTEE_COLLATERAL; LEAKAGE_PRIMING_FLAGS; CAPACITY_AVAILABILITY; PRESSURE_POINT_UPGRADE_PRIORITY | These documents do not establish a complete current agreement, current perfection, current usage or calculated capacity. |
| Caesars Entertainment, Inc.; secured credit facilities | Incremental Assumption Agreement No. 3 and conformed credit agreement, source b24b47d6-6bfd-4248-b660-e867409dd303 [C30] | CP-4; CP-4B; CP-4A | February 6, 2024; conformed document through that date | PARTIAL | CONTROLLING_DOCUMENT_AVAILABILITY; PROTECTION_WEAKNESS_FLAGS; ENTITY_GUARANTEE_COLLATERAL; LEAKAGE_PRIMING_FLAGS; CAPACITY_AVAILABILITY; PRESSURE_POINT_UPGRADE_PRIORITY | Later executed amendments and current operative lease documents are not included in the delivered evidence. |
| Caesars Entertainment, Inc.; consolidated issuer and selected debt disclosures | Form 10-Q, source 1ae6b04b-413a-4f14-b5da-362701a558fb [C20, C26] | CP-4; CP-4B; CP-4A | Q2 2026 | PARTIAL | ENTITY_GUARANTEE_COLLATERAL; PRESSURE_POINT_UPGRADE_PRIORITY | Filed disclosures are not a substitute for current document-by-document perimeter and capacity work. |

#### TL40.2 — Topic Allocation Register

| topic_id | topic_label | source_owner_modules | materiality | evidence_status | disposition | priority_rank | summary | source_refs | upgrade_module_ids |
|---|---|---|---|---|---|---:|---|---|---|
| CONTROLLING_DOCUMENT_AVAILABILITY | Controlling-document availability | CP-4 | HIGH | PARTIAL | GAP_ONLY | 1 | [Insufficient Information] — the complete current operative credit-agreement amendment package and controlling lease documents are not included in the delivered evidence. | 1ae6b04b-413a-4f14-b5da-362701a558fb; b24b47d6-6bfd-4248-b660-e867409dd303 [C2, C30] | CP-4 |
| PROTECTION_WEAKNESS_FLAGS | Protection and weakness flags | CP-4 | HIGH | PARTIAL | DEEPEN | 2 | The indenture contains affirmative security, guarantee and covenant provisions, but also exceptions and document-specific release mechanics. Their current operation and practical effect require provision-level FULL review. | 1ae6b04b-413a-4f14-b5da-362701a558fb; 42064519-b433-435a-82c5-c1cabe537ac7; 6061f8bd-230a-4786-b679-b6acd966c841; 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 [C26, C27, C28, C29] | CP-4 |
| ENTITY_GUARANTEE_COLLATERAL | Entity, guarantee and collateral coverage | CP-4B | HIGH | PARTIAL | DEEPEN | 3 | The 10-Q describes guarantees by material wholly owned domestic subsidiaries and security over substantially all assets, subject to exceptions; the supplements add guarantors to the 2032 notes. This transmits through entity coverage and potential recovery, but does not establish current completeness or perfection. | 1ae6b04b-413a-4f14-b5da-362701a558fb; 42064519-b433-435a-82c5-c1cabe537ac7; 6061f8bd-230a-4786-b679-b6acd966c841 [C26, C28, C29] | CP-4B |
| LEAKAGE_PRIMING_FLAGS | Leakage and priming flags | CP-4, CP-4B | HIGH | PARTIAL | GAP_ONLY | 4 | [Insufficient Information] — current basket usage, debt and lien incurrence, lease and intercreditor status are not established by the delivered document set. | 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4; b24b47d6-6bfd-4248-b660-e867409dd303 [C27, C30] | CP-4B |
| CAPACITY_AVAILABILITY | Capacity availability | CP-4A | HIGH | MISSING | GAP_ONLY | 5 | [Insufficient Information] — current covenant capacity, basket usage and headroom calculations are not included in the delivered evidence. | No current capacity calculation delivered | CP-4A |
| PRESSURE_POINT_UPGRADE_PRIORITY | Pressure point and upgrade priority | CP-4A | HIGH | PARTIAL | GAP_ONLY | 6 | [Insufficient Information] — current capacity calculations and a complete current legal-document package are not included in the delivered evidence. | b24b47d6-6bfd-4248-b660-e867409dd303 [C30] | CP-4A |

#### TL40.3 — Decision Screen

| screen_item | assessment | evidence | credit_transmission | screening_implication | confidence | source_refs |
|---|---|---|---|---|---|---|
| OVERALL | INSUFFICIENT_INFORMATION | The delivered source set includes the 2032 indenture family and a 2024 conformed credit-agreement source; current operative documents, actual capacity calculations and full current entity evidence are incomplete. [C26, C27, C28, C29, C30] | Document and capacity uncertainty affects covenant protection, leakage/priming exposure and potential recovery. | Do not infer capacity or a legal conclusion. Escalate to CP-4, CP-4B and CP-4A before a creditor-document conclusion. | Insufficient Information | 1ae6b04b-413a-4f14-b5da-362701a558fb; 42064519-b433-435a-82c5-c1cabe537ac7; 6061f8bd-230a-4786-b679-b6acd966c841; 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4; b24b47d6-6bfd-4248-b660-e867409dd303 [C26, C27, C28, C29, C30] |

#### TL40.4 — Gaps and Upgrade Register

| topic_id | trigger | missing_inputs | decision_impact | required_source | target_full_module_id | expected_owned_object | blocking_for_full_decision |
|---|---|---|---|---|---|---|---|
| CONTROLLING_DOCUMENT_AVAILABILITY | Current operative documents are incomplete. | Current executed credit amendments, current leases, amendments, schedules and transaction-status documents | Terms and perimeter may alter protection and creditor rights. | Complete current executed financing and lease documents | CP-4 | Controlling-document review | true |
| PROTECTION_WEAKNESS_FLAGS | 2032 note provisions require current provision-level review. | Current indenture family, relevant provisions, releases, amendments and operative documents | Affects covenant protection and creditor options. | Complete executed current note and credit documents | CP-4 | Provision-level protection analysis | true |
| ENTITY_GUARANTEE_COLLATERAL | Disclosed guarantee scope is not a current verified entity/collateral map. | Current subsidiary perimeter, guarantee status, collateral schedules, exclusions and perfection evidence | Affects structural coverage and potential LGD. | Current entity chart, executed guarantees, collateral records and schedules | CP-4B | Entity, guarantee and collateral mapping | true |
| LEAKAGE_PRIMING_FLAGS | Current usage and intercreditor position are not established. | Actual basket usage, new liens/debt, current intercreditor agreements and lease-document routes | Affects leakage, priming and relative creditor position. | Current executed agreements, compliance certificates and usage schedules | CP-4B | Leakage and priming analysis | true |
| CAPACITY_AVAILABILITY | No current capacity calculation is supplied. | Current definitions, inputs, usage and applicable calculation dates | Determines whether capacity can be calculated and creditor protection assessed. | Current documents, financial inputs and complete basket-usage records | CP-4A | Covenant capacity and headroom calculation | true |
| PRESSURE_POINT_UPGRADE_PRIORITY | Current documents and calculations do not establish the controlling pressure point. | Capacity results, current covenant terms, usage and issuer transactions | Determines which FULL capacity calculation should be completed first. | Current operative documents and CP-4A calculation inputs | CP-4A | Capacity pressure-point prioritization | true |

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Reporting period and interim filing identity | [C1] | Caesars Form 10-Q | 1 |
| Referenced annual filing and historical-basis limitation | [C2] | Caesars Form 10-Q | 5 |
| Consolidated Adjusted EBITDA comparison | [C3] | Caesars Form 10-Q | 16 |
| Consolidated revenue direction | [C4] | Caesars Form 10-Q | 19 |
| Segment divergence | [C5, C6] | Caesars Form 10-Q | 20 |
| Table-games hold comparison | [C7] | Caesars Form 10-Q | 20 |
| Operating cash flow and capex | [C8, C9] | Caesars Form 10-Q | 4 |
| Cash, revolver capacity, debt service and lease uses | [C10, C11, C12, C13] | Caesars Form 10-Q | 10, 22 |
| Variable-rate exposure and absence of cash-flow hedges | [C14, C15, C16] | Caesars Form 10-Q | 7, 23 |
| Comparability limitations | [C17, C18, C19] | Caesars Form 10-Q | 16, 18, 21 |
| Debt maturities and reported covenant compliance | [C20, C21] | Caesars Form 10-Q | 9, 23 |
| Merger condition and capital-allocation context | [C22, C23, C24] | Caesars Form 10-Q | 5, 13, 25 |
| Subsequent event kept separate from Q2 results | [C25] | Caesars Form 10-Q | 17 |
| Guarantee and security disclosure | [C26, C27] | Caesars Form 10-Q; 2032 secured-note indenture | 11; 33 |
| 2032 secured-note guarantor additions | [C28, C29] | First and Second Supplemental Indentures | 1; 1 |
| Credit agreement version/date | [C30] | Incremental Assumption Agreement No. 3 and conformed credit agreement | 1 |
| Issuer liquidity expectation | [C31] | Caesars Form 10-Q | 22 |

## Source Registry

| Source ID | Source | Use and limitation |
|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Caesars Entertainment, Inc. Form 10-Q for the quarter ended June 30, 2026 | Primary interim financial, operating, debt, liquidity and transaction disclosure. Cited in the appendix and Evidence Trace. [C1, C4, C8, C20] |
| 42064519-b433-435a-82c5-c1cabe537ac7 | First Supplemental Indenture for the 6.500% senior secured notes due 2032 | Dated 2024 note-document evidence; does not by itself establish the current full document set. [C28] |
| 6061f8bd-230a-4786-b679-b6acd966c841 | Second Supplemental Indenture for the 6.500% senior secured notes due 2032 | Dated 2024 note-document evidence; does not by itself establish current entity coverage. [C29] |
| 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | 6.500% Senior Secured Notes due 2032 Indenture | Executed base indenture and its exhibits; a form exhibit is not evidence of an executed intercreditor agreement. [C27] |
| b24b47d6-6bfd-4248-b660-e867409dd303 | Incremental Assumption Agreement No. 3 and conformed July 20, 2020 credit agreement | Executed 2024 amendment/conformed version; does not supply subsequent full amendments or complete current lease documents. [C30] |

## Gaps & Conflicts

- **G-1 — Annual and basis coverage:** the Q2 filing refers readers to the 2025 Form 10-K, which is not among the delivered evidence. The financial-change and fundamental screens therefore remain source-limited. [C2]
- **CF-1 — Debt and coverage basis:** the available filing contains debt carrying/book-value, maturity and interest information, but no FULL reconciliation to a current canonical leverage/coverage basis. Do not substitute face, carrying, covenant or issuer-defined figures for one another; CP-1/CP-1B own that reconciliation. [C14, C20]
- **G-2 — Current operative documents:** the credit agreement source is dated February 2024; complete current credit amendments and controlling lease documents are not delivered. This restricts contractual, capacity, guarantee and leakage work. [C30]
- **G-3 — Market and comparable evidence:** no dated issue-level quote, curve, comparable or trading-technical source is included in the evidence delivered here. The market/recovery screen therefore cannot establish compensation or selection posture.
- **G-4 — Forecast and sensitivity:** no source-grounded base/downside trajectory, forecast, rate sensitivity or integrated liquidity breakpoint is available in the delivered evidence.
- **G-5 — Governance and ESG:** issuer-specific governance/sponsor conduct and ESG/transition-transmission evidence are not included; neither is inferred from sector or transaction identity.
- **G-6 — Legal/capacity:** the 2032 indenture family and 2024 credit-agreement source do not establish current basket usage, capacity, current collateral perfection or a complete current entity map. CP-4, CP-4B and CP-4A must resolve these areas.
- **Subsequent event:** the filing identifies a July 13, 2026 Alberta mobile sports betting and iGaming launch after the June 30 reporting date. It is retained as a dated event and is not blended into Q2 results. No later transaction-status source is included. [C22, C25]

## QA Validation

| Check | Result | Record |
|---|---|---|
| Identity and canonical filename | Self-check complete | Issuer, module, run, period and analysis date match host-owned front matter; filename stated as `CZR_CP-L10_20261002.md`. |
| Canonical structure | Self-check complete | Six required H2 sections appear once and in required order; Analysis opens with `### Financial change screen`. |
| LITE boundary and outcome | Restricted | Screening-only posture maintained; no canonical financial history, normalized financials, FULL conclusion, investment recommendation, legal opinion or capacity calculation asserted. Structured outcome is FULL_UPGRADE_REQUIRED. |
| Register inventory and columns | Self-check complete | TL10.1–TL10.4, TL20.1–TL20.4, TL23.1–TL23.4, TL30.1–TL30.4 and TL40.1–TL40.4 are present with required columns and topic rows. |
| Topic identity and posture semantics | Self-check complete | Each screen includes its six required topic IDs once and an OVERALL decision-screen row whose assessment matches the stated posture. |
| Evidence trace and citation markers | Self-check complete | Material sourced findings and figures have citation markers; citations refer only to delivered evidence and are listed in the response citation array. |
| Gaps and FULL upgrades | Restricted | Material gaps and DEEPEN topics have targeted FULL owner, expected object, required source, decision impact and blocking status in the corresponding gaps register. |
| Confidence and QA status | Restricted | Confidence 55 / Low; QA Restricted due source limitations and required linked FULL upgrades. Committee status remains Restricted because this is SCREENING_ONLY. |
| Host validation and completeness check | Not run here | Host vendor validation and register-completeness checks follow this answer; no output, finding or exit status is claimed. |