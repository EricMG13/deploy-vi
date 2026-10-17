---
module_id: "CP-2D"
module_name: "LiquidityCashFlowBridge"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2D-69dad545cdf3a943"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-11-CP-2D"
credit_os_invocation_sha256: "a47a1c7d7267ce820ede25b9525aadc65393c8b2c24517fd72cc47aee4b84cb9"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
  - module_id: "CP-2"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e949697dd98dc950367aedad3d0f31b38d29092a5cb491444c38876ed7a94ead"
confidence_score: 55
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - SOURCE_LIMITED_NOT_COMMITTEE_READY
  - NO_POST_Q2_2026_FINANCIALS
  - TWELVE_MONTH_CASH_FLOW_BRIDGE_INCOMPLETE
  - REVOLVER_FUNGIBILITY_AND_COVENANT_HEADROOM_UNRESOLVED
validation_warnings:
  - FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED
  - FORWARD_CASH_TAX_AND_WORKING_CAPITAL_ESTIMATES_NOT_PROVIDED
  - HOST_VALIDATION_PENDING
downstream_consumers: [CP-3, CP-3C, CP-6, CP-5, CP-5A]
---

## Audit Summary

Canonical handoff filename: `CZR_CP-2D_20261002.md`. Module status: **Ready with Limitations**; Liquidity Risk Level: **Insufficient Information**. The accepted CP-0, CP-1 and CP-2 handoffs match the issuer, reporting period and run, but retain restricted/source-limited status. The June 30, 2026 Form 10-Q provides cash, facility availability, cash flows, debt service estimates and remainder-of-2026 rent and capital expenditure estimates. It does not provide a complete forecast for the 12-month period through June 30, 2027, including H1 2027 cash uses, operating cash flow, cash taxes or working-capital needs. June 30 reported liquidity is therefore a starting snapshot, not proof of 12-month coverage. The source-supported six-month cash-flow period was cash-generative, so Months to Empty is not a meaningful exhaustion measure. Host validation follows this response; no host validation result is claimed.

## Analysis

### Liquidity view

At June 30, 2026, Caesars reported $965 million of cash and $2.928 billion of total cash and borrowing capacity; disclosed facility components imply approximately $1.963 billion of revolver availability after the listed letters-of-credit, reserve and regulatory deductions. [C1, C2, C3, C4, C5, C6, C7] Restricted cash of $96 million is excluded from accessible liquidity. [C8] The filings quantify only selected remainder-of-2026 uses: $425 million of debt service, $687 million of VICI/GLPI lease payments and $310–$390 million of estimated capital expenditures. [C10, C11, C12, C13] These figures do not establish full 12-month coverage because H1 2027 uses and forward operating cash, tax and working-capital estimates are not provided. H1 2026 cash flow was positive, a counterweight, but not a forward forecast. [C17, C19] Accordingly, ending liquidity and a decision-useful risk classification cannot be established; monitor cash, revolver availability and upcoming debt/rent requirements.

The summary below separates the reported opening position from the incomplete forward bridge; it is not a forecast of ending liquidity.

| Near-term liquidity item | Amount | Period / basis | Creditor interpretation |
|---|---:|---|---|
| Cash and cash equivalents | $965m | June 30, 2026 | Reported cash; excludes restricted cash. [C1, C8] |
| Beginning accessible liquidity | $2,928m | June 30, 2026; cash plus calculated available revolver | Issuer-reported aggregate; revolver access remains subject to facility terms. [C2] |
| Quantified debt service | $425m | Remainder of 2026 | Principal and interest estimate; H1 2027 amount not isolated. [C10, C11] |
| Lease payments | $687m | Remainder of 2026 | H1 2027 lease cash requirement not supplied. [C12] |
| Capital expenditures | $310–$390m | Remainder of 2026 estimate | Includes growth/renovation, digital and maintenance categories. [C13] |
| Months to Empty | Not Calculable | H1 2026 cash-generative period | No positive historical net cash burn to use as an exhaustion rate. [C19] |
| Ending accessible liquidity | [Insufficient Information] — full 12-month cash-flow bridge unavailable | Through June 30, 2027 | H1 2027 and forecast operating cash/cash uses are missing. |

#### Source gate and scope

CP-0 identifies the source set as limited and reports no post-Q2 2026 financial statements. CP-1 supplies the June-period financial data and defines balance-sheet carrying debt separately from face principal and financing obligations; CP-2 is a restricted same-run synthesis. Those upstream values are used only within their stated scope and are re-anchored below to the primary filings. The directly supplied filings support a partial liquidity analysis, not a complete 12-month forecast. [C1, C2]

The core entity is Caesars Entertainment, Inc. and its consolidated subsidiaries. The liquidity snapshot is as of June 30, 2026; cash-flow data cover the six months ended that date. The analysis horizon is July 1, 2026 through June 30, 2027. It does not blend the July 13, 2026 Alberta launch into Q2 results; that event is noted separately as subsequent to the balance-sheet date. [C31]

#### 12-month uses, pinch point and downside transmission

The best-quantified near-term obligations are scheduled debt service and VICI/GLPI lease payments for the remainder of 2026, plus the issuer’s remaining-2026 capital expenditure estimate. Debt service for the remainder of 2026 is $425 million, comprising $55 million of scheduled principal maturities and $370 million of estimated interest in the debt-service schedule. [C10, C11] The company separately estimates $687 million of lease payments for the remainder of 2026 and $310–$390 million of capital expenditures from unrestricted cash. [C12, C13] These are not a complete 12-month cash-use total: they omit any H1 2027 allocation, forward working capital and cash tax needs, and any unquantified other cash uses.

The causal downside is that lower visitation, gaming hold or digital net win would reduce operating cash generation while debt service, lease payments and necessary maintenance continue. The first liquidity break would be weaker cash conversion or a working-capital outflow; the transmission is greater cash use and potentially increased revolver reliance, which would reduce flexibility if availability or covenant access then tightened. The observable triggers are falling cash, revolver draws or declining availability, deterioration in reported operating cash flow, and continued pressure on segment results. No stress amount is inferred from the materials.

#### Working capital and operating cash conversion

H1 2026 operating activities generated $675 million of cash, while PP&E purchases were $335 million; these reported figures do not isolate forward cash generation or a complete post-rent free-cash-flow amount. [C17, C18] The H1 cash-flow statement reports a $24 million receivables outflow, an $88 million outflow from prepaid expenses and other assets, an $11 million net income-tax receivable/payable outflow and a $52 million inflow from accounts payable, accrued expenses and other liabilities. Together these listed changes imply a calculated net working-capital-related cash outflow of $71 million for H1 2026. [C23, C24, C25, C26] This historical movement is not forecast for the next 12 months and is not added again to reported CFO in the bridge.

Customer deposits and other deferred revenue were $545 million at June 30, 2026, up from $492 million at year-end 2025. This is operating float associated with future customer gaming or service obligations, not ordinary payables or debt; if customer activity reverses or obligations are fulfilled, some cash may be absorbed. The filing does not disclose the immediately refundable portion or timing, so no liquidity credit is assigned to the balance. [C27]

#### Strongest counterargument and what would change the view

Management stated in the FY2025 filing that it expected then-current liquidity, committed-facility availability and operating cash flows to be sufficient for operations, capital requirements and debt service for the next twelve months and beyond. That characterization, together with June 30 reported liquidity, H1 positive operating cash flow and reported compliance with applicable financial covenants, is the strongest contrary evidence to a stressed-liquidity interpretation. [C2, C9, C17, C28] It would win greater weight if later filings showed continued cash generation after capex and rent, stable or rising accessible revolver capacity, current covenant headroom and a complete H1 2027 cash-use schedule. In their absence, it cannot resolve the bridge or establish 12-month coverage.

The company reported $6.0 billion of variable-rate borrowings at June 30, 2026. A rise in applicable rates would increase cash interest and reduce residual liquidity; the current debt-service estimate already uses forward interest-rate curves and may differ from actual payments. [C29, C11] The $10 million of merger-related transaction costs recorded in Q2 and H1 are historical and are not assumed to recur or to be zero in the future. [C30]

#### Liquidity risk assessment and monitoring

**Liquidity Risk Level: Insufficient Information.** Evidence supports a substantial reported starting liquidity position and positive H1 operating cash generation. The risk mechanic is that a dated cash/revolver snapshot and a cash-generative historical period do not show whether cash generation after debt service, rent, taxes, working capital and capital expenditure will sustain access through June 30, 2027. The creditor implication is an unquantified liquidity runway and refinancing buffer, not a conclusion that liquidity is inadequate. Access constraint: the issuer disclosed availability after specified deductions and reported covenant compliance, but current covenant headroom and future accessible capacity are not disclosed. Monitoring should focus on cash below a defined threshold, revolver draws or availability declines, working-capital outflows, cash-burn acceleration, capex inflexibility and maturity/refinancing developments.

### Analytical appendix — complete canonical registers

#### T2E.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Entertainment, Inc. Form 10-Q | Primary-Verified | Quarter and six months ended June 30, 2026; balance sheet at June 30, 2026 | Caesars Entertainment, Inc. and consolidated subsidiaries | Cash and restricted cash, revolver capacity, debt service estimates, cash flows, capital expenditure estimates, lease payments, covenant compliance. [C1, C2, C8, C9, C10, C11, C12, C13, C17] | Unaudited interim report; no post-June financial statements; incomplete 12-month forecast and no discrete forward cash-tax or working-capital estimate. | Beginning liquidity, partial mandatory-use schedule, cash-flow analysis and monitoring. |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars Entertainment, Inc. Form 10-K | Primary-Verified | Fiscal year ended December 31, 2025 | Caesars Entertainment, Inc. and consolidated subsidiaries | Historical cash-flow and debt context; management liquidity characterization; lease and variable-rate risk context. [C28] | Historical year-end source; does not update June 2026 balances or supply H1 2027 forecasts. | Historical cross-check and counterargument, not a substitute for current liquidity data. |
| e24bf84e-82d3-4167-bd6f-f510b21fdd0e | Fourth Amendment to Credit Agreement | Primary-Verified | May 9, 2024 | Caesars borrower and lenders under CEI Credit Agreement | Prior credit-agreement amendment and pricing terms. | Does not provide the complete current credit agreement, current covenant calculation or current revolver access conditions. | Context only; no inference of current covenant capacity. |
| 41868018-6353-4359-b98f-d9d5d6d11715 | Fifth Amendment to Credit Agreement | Primary-Verified | November 25, 2024 | Caesars borrower and lenders under CEI Credit Agreement | Term B and Term B-1 margin reductions and consent/assignment mechanics. | Amendment only; not the complete current credit agreement or a current liquidity forecast. | Context only; no inference of covenant capacity or future funding. |
| CP-0 / e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9 | Accepted SourceReadiness handoff | Accepted upstream artifact; Restricted | Q2 2026; analysis date October 2, 2026 | CZR source pack | Source readiness, evidence limitations and subsequent-period coverage boundary. | Analytical handoff; it is not independent primary evidence. | Carry forward the source-limited status and period gap. |
| CP-1 / 2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc | Accepted CanonicalDataFoundation handoff | Accepted upstream artifact; Restricted | Q2 2026 | Caesars consolidated | Canonical financial data and debt-basis definitions. | Handoff remains restricted; no financial period after June 30, 2026. | Re-anchor reported financial measures and preserve carrying-value distinctions. |
| CP-2 / e949697dd98dc950367aedad3d0f31b38d29092a5cb491444c38876ed7a94ead | Accepted FundamentalCreditSynthesizer handoff | Accepted upstream artifact; Restricted | Q2 2026 | Caesars consolidated | Credit context and source-limited analytical conclusions. | Handoff is not a primary source and does not provide the missing 12-month cash forecast. | Context only; current module owns liquidity bridge and risk classification. |

#### T2E.2 — Beginning Liquidity Register

| Liquidity Component | Source-Supported Amount | Accessibility Status | Source Trace | Limitation / Restriction | Risk Mechanic | Credit Implication |
|---|---:|---|---|---|---|---|
| Cash | $965 million | Reported at June 30, 2026; counted in opening liquidity | Q2 2026 Form 10-Q, balance sheet, p. 2. [C1] | Dated snapshot; no subsequent cash balance supplied. | Cash absorbs cash-flow deficits and near-term obligations before incremental borrowing is required. | Supports the opening buffer but cannot establish October 2 or forward liquidity. |
| Restricted cash | $96 million | Excluded from accessible liquidity | Q2 2026 Form 10-Q, balance sheet, p. 2. [C8] | Restricted status is reported; source does not establish availability for debt service. | Excluding it avoids overstating funds available for general corporate uses. | Not counted in beginning accessible liquidity. |
| Revolver commitment | $2,275 million stated aggregate commitment: $2,250 million CEI RCF plus $25 million CVA RCF | Committed facilities; commitment is not itself undrawn availability | Q2 2026 Form 10-Q, debt and facility descriptions, p. 10. [C32, C33] | Facility commitments, drawings and usage restrictions differ; do not add full commitments to cash. | Only undrawn, disclosed available capacity can support the bridge. | Included only through the separately calculated availability line below. |
| Revolver drawn | $120 million CEI RCF; $0 million CVA RCF reported outstanding | Already drawn; not accessible liquidity | Q2 2026 Form 10-Q, debt table, p. 9. [C34] | No CVA RCF balance is reported; no inference about future borrowing beyond stated availability. | Drawn amounts are debt and reduce remaining facility capacity. | Excluded from accessible capacity; monitor any increase in drawings. |
| Accessible revolver availability | $1,963 million, calculated from $2,130 million CEI RCF capacity net of outstanding balance, plus $25 million CVA capacity, less $96 million letters of credit, $40 million reserves and $56 million regulatory commitments | Disclosed capacity components; available at reporting date subject to facility terms | Q2 2026 Form 10-Q, liquidity table, p. 22. [C3, C4, C5, C6, C7] | Arithmetic produces $1,963 million; company separately describes CEI available capacity as approximately $1.9 billion. Compliance is reported, but current covenant headroom and future access are not disclosed. [C9] | Deductions and any later covenant/access constraints can reduce drawable liquidity. | Counted at the disclosed June 30 level; not treated as unconditional or October-current availability. |
| Other committed liquidity | — | [Insufficient Information] — no additional committed accessible source identified in supplied materials | Q2 2026 Form 10-Q liquidity disclosures reviewed. [C2] | No separate additional source is quantified. | An unreported source cannot be relied upon to bridge a shortfall. | No amount added; follow up for any additional committed facilities or support. |
| Beginning accessible liquidity | $2,928 million | Calculated and matches the issuer’s reported aggregate cash-and-capacity total | $965 million cash plus $1,963 million calculated available revolver; Q2 liquidity table reports $2,928 million. [C1, C2, C3, C4, C5, C6, C7] | June 30, 2026 snapshot; excludes restricted cash and depends partly on revolver accessibility. | A larger opening buffer can absorb operating and working-capital volatility, but only while capacity remains accessible. | Starting point for the bridge; does not establish 12-month sufficiency. |

#### T2E.3 — Mandatory Cash Uses Register

| Cash Use | Amount | Timing | Mandatory / Discretionary | Source Trace | Risk Mechanic | Credit Implication | Limitation |
|---|---:|---|---|---|---|---|---|
| Cash interest | $370 million estimated | Remainder of 2026; H1 2027 not separately supplied | Mandatory debt-service use | Q2 2026 debt-service schedule, p. 9. [C11] | Interest consumes liquidity before principal reduction or discretionary investment. | A material fixed cash claim; full 12-month amount is not calculable from the disclosed schedule. | 2027 figure is full-year, not H1-only; the 12-month period cannot be exactly totaled. |
| Debt amortization | $55 million scheduled principal maturities | Remainder of 2026; H1 2027 not separately isolated | Mandatory | Q2 2026 debt-service schedule, p. 9. [C10] | Principal repayment directly reduces cash or requires refinancing. | Known remainder-2026 amortization is modest relative to opening liquidity, but the full 12-month amount is not established. | 2027 schedule reports full-year maturities of $114 million, not a separate H1 amount. |
| Lease payment | $687 million estimated | Remainder of 2026; H1 2027 not supplied | Contractual / mandatory | Q2 2026 MD&A, p. 22. [C12] | Lease payments continue alongside debt service and reduce residual cash. | Major near-term fixed cash use; full 12-month rent coverage cannot be determined. | Estimate covers only the remainder of 2026. |
| Mandatory capex | $155–$185 million maintenance estimate | Remainder of 2026; H1 2027 not supplied | Management-guided; maintenance | Q2 2026 capex table, p. 22. [C16] | Deferring maintenance may preserve short-term cash but risks asset quality and operating performance. | Necessary maintenance competes with debt reduction for cash. | Company does not provide a 12-month mandatory maintenance forecast. |
| Growth capex | $155–$205 million calculated: $130–$170 million growth/renovation plus $25–$35 million Caesars Digital | Remainder of 2026; H1 2027 not supplied | Discretionary / execution-dependent | Q2 2026 capex table, p. 22. [C14, C15] | Deferral may preserve liquidity but could delay expected operating benefits. | Potential near-term flexibility exists, with a growth and competitiveness trade-off. | Estimates cover remaining 2026 only; no assumption of deferral is made. |
| Cash taxes | H1 2026 actual: $11 million; forward 12-month estimate: [Insufficient Information] — no estimate supplied | H1 actual; future timing unavailable | Mandatory when due | Q2 2026 cash-flow supplemental disclosure, p. 5. [C22] | Cash taxes reduce funds available for rent, interest and principal. | Forward tax use cannot be treated as zero; bridge remains incomplete. | Historical H1 amount is not a forecast. |
| Working-capital outflow | H1 2026 listed changes calculate to $(71) million net outflow; forward amount: [Insufficient Information] — no forecast supplied | H1 actual; future timing unavailable | Operating cash use; future amount not established | Q2 2026 cash-flow changes, p. 4. [C23, C24, C25, C26] | Receivables/prepayments and other working-capital movements can absorb cash before it is available for debt service. | Historical outflow is a monitoring signal, not a 12-month projection. | Do not add the historical movement again to operating cash flow; forward seasonal data absent. |
| Integration cost | $10 million transaction costs recorded for Q2 and H1 2026; future amount not supplied | Historical Q2/H1; future timing unknown | Transaction-related; future cash classification and amount not supplied | Q2 2026 Form 10-Q, p. 6. [C30] | Further transaction costs, if incurred, could add cash use while the merger is pending. | No future amount included; monitor transaction costs and payment timing. | Historical amount does not establish future spend or cash-paid amount. |
| Dividend / distribution | H1 2026 distributions to noncontrolling interest owners: $41 million; forward amount: [Insufficient Information] — no commitment forecast supplied | H1 actual; future timing unavailable | Historical distribution; future discretionary/contractual status not established | Q2 2026 cash-flow statement, p. 4. [C35] | Distributions reduce cash otherwise available to creditors. | Do not assume future distributions are zero or repeat the H1 amount. | Forward obligation and board policy under the pending merger are not quantified. |

#### T2E.4 — Working Capital & Capex Pressure

| Driver | Evidence | Expected Cash Impact | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|---|
| H1 2026 working capital | Listed operating asset/liability movements calculate to a $71 million net cash outflow. | Actual H1 2026 outflow; forward amount not available. | Cash absorbed by receivables, prepayments and other items before it is available for debt service. | Adds uncertainty to cash conversion and shortens the buffer if repeated. | Q2 2026 cash-flow statement, p. 4. [C23, C24, C25, C26] | H1 actual is not a seasonal or forward forecast; no separate H1/Q3 seasonal pattern supplied. |
| Customer-deposit float | Customer deposits and other deferred revenue were $545 million at June 30, 2026 versus $492 million at December 31, 2025. | The increase is a source of operating float, but fulfillment, wagering or withdrawal may require future cash or services. | A liability tied to customer performance obligations can convert into cash use if customer activity reverses or obligations are fulfilled. | Do not count the liability balance as freely available liquidity; monitor changes and redemption/refund patterns. | Q2 2026 Form 10-Q, contract liabilities, p. 11. [C27] | No breakdown of immediately refundable balances or maturity/settlement timing. |
| Remaining-2026 maintenance capex | Maintenance estimate $155–$185 million. | Cash use from unrestricted cash during remaining 2026; H1 2027 not supplied. | Maintenance deferral can preserve short-term liquidity but risks property condition and operating quality. | Constrains discretionary deleveraging; a deferral is not assumed. | Q2 2026 capital expenditure estimate, p. 22. [C16] | Management estimate; no 12-month mandatory-versus-deferrable split. |
| Remaining-2026 growth and renovation capex | $130–$170 million estimated. | Cash use during remaining 2026; potential timing discretion not specified. | Deferral may preserve liquidity but delay expansion, renovation or planned returns. | A possible mitigant only if execution and project economics permit; not counted as a committed saving. | Q2 2026 capital expenditure estimate, p. 22. [C14] | No project-level deferral terms or H1 2027 estimate. |
| Remaining-2026 Caesars Digital capex | $25–$35 million estimated. | Cash use during remaining 2026; H1 2027 not supplied. | Reduced investment could preserve cash but impair digital-platform development or competitive position. | Limited potential liquidity lever, balanced against growth and operating requirements. | Q2 2026 capital expenditure estimate, p. 22. [C15] | No project-level schedule or deferral assessment. |
| Total remaining-2026 capex | $310–$390 million estimated from unrestricted cash. | Cash use during remaining 2026, before unprovided H1 2027 spend. | Total capex competes with debt service and rent; maintenance and growth portions have different deferral consequences. | A material partial-horizon use; not a complete 12-month capex figure. | Q2 2026 capital expenditure estimate, p. 22. [C13] | The filing does not give the full next-12-month amount or a mandatory/growth split for all projects. |

#### T2E.5 — 12-Month Liquidity Bridge

| Bridge Item | Amount | Source / Calculation | Status | Credit Comment | Source Trace |
|---|---:|---|---|---|---|
| Beginning cash | $965 million | Cash and cash equivalents at June 30, 2026; restricted cash excluded. | Reported | Dated opening cash balance, not October-current cash. | Q2 2026 Form 10-Q, balance sheet, p. 2. [C1, C8] |
| Accessible revolver availability | $1,963 million | $2,130m CEI capacity net of outstanding balance + $25m CVA capacity − $96m letters of credit − $40m specific reserves − $56m regulatory commitments. | Calculated | Issuer-reported components reconcile to reported total liquidity; access remains subject to facility terms and future conditions. | Q2 2026 liquidity table, p. 22; reported covenant compliance, p. 10. [C3, C4, C5, C6, C7, C9] |
| Beginning accessible liquidity | $2,928 million | $965m cash + $1,963m calculated accessible revolver; matches issuer’s reported total. | Calculated | Includes disclosed available borrowing capacity; excludes restricted cash. | Q2 2026 balance sheet and liquidity table, pp. 2, 22. [C1, C2, C3, C4, C5, C6, C7, C8] |
| Operating cash inflow/outflow | [Insufficient Information] — no forward 12-month operating-cash forecast supplied | H1 2026 operating cash flow was $675m, but is historical and includes working-capital movements. | Insufficient Information | Forecast cash generation is required before uses can be bridged to ending liquidity. | Q2 2026 cash-flow statement, p. 4. [C17] |
| Working-capital impact | [Insufficient Information] — no forward 12-month working-capital forecast supplied | H1 2026 listed changes calculate to a $(71)m outflow; not separately added to historical CFO. | Insufficient Information | Forecast working-capital absorption is unknown; avoid double counting historical changes in CFO. | Q2 2026 cash-flow statement, p. 4. [C23, C24, C25, C26] |
| Cash interest | [Insufficient Information] — remainder-2026 interest is $370m; H1 2027 amount is not separately provided | Debt-service schedule estimates $370m interest for remaining 2026 and $750m for FY2027. | Provisional | FY2027 amount is a full-year figure and cannot be allocated to the bridge horizon without unsupported assumptions. | Q2 2026 debt-service schedule, p. 9. [C11] |
| Cash taxes | [Insufficient Information] — no forward 12-month cash-tax estimate supplied | H1 2026 cash taxes paid were $11m; historical only. | Insufficient Information | Future cash taxes cannot be assumed zero or projected from the half-year actual. | Q2 2026 supplemental cash-flow disclosure, p. 5. [C22] |
| Mandatory capex | [Insufficient Information] — remaining-2026 maintenance estimate is $155–$185m; H1 2027 amount unavailable | Company estimates maintenance capex for remaining 2026; no complete 12-month schedule. | Management-guided | Maintenance spend competes with debt service; deferral may impair operations. | Q2 2026 capex estimate, p. 22. [C16] |
| Debt amortization/maturities | [Insufficient Information] — $55m scheduled for remaining 2026; H1 2027 amount not isolated | Debt schedule reports $55m remaining-2026 maturities and $114m for FY2027. | Provisional | Full-year 2027 principal cannot be assigned to the first six months of 2027 from this source. | Q2 2026 debt-service schedule, p. 9. [C10] |
| Other cash uses | [Insufficient Information] — remainder-2026 lease payments are $687m; H1 2027 and other future uses not supplied | VICI/GLPI lease-payment estimate for remaining 2026; future distributions and transaction cash costs are not forecast. | Provisional | Rent is a substantial separate claim; historical transaction costs/distributions are not assumed to repeat or to be zero. | Q2 2026 MD&A p. 22; cash-flow statement p. 4; merger cost disclosure p. 6. [C12, C30, C35] |
| Ending accessible liquidity | [Insufficient Information] — full 12-month operating cash, H1 2027 uses and accessible-facility forecast unavailable | Formula requires beginning accessible liquidity plus projected operating cash and WC, less interest, taxes, capex, debt service and other uses. | Insufficient Information | No point estimate or unsupported refinancing assumption is made. | Bridge inputs above; underlying incomplete forecast disclosures. [C1, C2, C10, C11, C12, C13, C17] |

#### T2E.6 — Months to Empty

| Calculation | Result | Formula / Inputs | Cash-Burn Basis | Status | Source Trace |
|---|---|---|---|---|---|
| Months to Empty | Not Calculable — the latest six-month period was cash-generative rather than cash-burning, and its cash-flow perimeter is not a forward burn forecast. | Beginning accessible liquidity $2,928m / average monthly cash burn. H1 2026 total cash, cash equivalents and restricted cash increased by $93m; arithmetic average is a $15.5m monthly cash increase, not a positive burn. | Six months ended June 30, 2026; reported aggregate cash change includes operating, investing and financing activity and is not a normalized recurring runway basis. | Not Calculable | Beginning liquidity from Q2 2026 p. 22 [C2]; six-month cash change from Q2 2026 p. 4 [C19]. |

#### T2E.7 — Liquidity Mitigants & Constraints

| Mitigant / Constraint | Evidence | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|
| Mitigant — reported opening cash and facility liquidity | June 30 cash and cash equivalents of $965m; reported aggregate cash and capacity of $2.928bn. | Cash and disclosed available capacity can absorb operating volatility and scheduled uses. | Supports the opening buffer, but not a complete 12-month sufficiency conclusion. | Q2 2026 balance sheet and liquidity table, pp. 2, 22. [C1, C2] | Snapshot is dated; total depends on revolver access and excludes restricted cash. |
| Mitigant — disclosed available revolving capacity | Liquidity table components calculate to $1.963bn after specified deductions. | Available borrowing can bridge temporary cash timing deficits. | Provides a reported contingency source at June 30; monitor draws and availability decline. | Q2 2026 liquidity table, p. 22. [C3, C4, C5, C6, C7] | No current covenant headroom or post-June draw status; no unconditional access assumption. |
| Mitigant — reported covenant compliance | Company reported compliance with applicable financial covenants as of June 30, 2026. | Compliance supports the disclosed period’s continued facility operation. | Positive current-date evidence, but insufficient to infer cushion or future compliance. | Q2 2026 Form 10-Q, p. 10. [C9] | Complete current credit agreement and actual headroom calculations are absent. |
| Mitigant — positive H1 operating cash generation | H1 2026 CFO was $675m; total cash, cash equivalents and restricted cash rose by $93m. | Cash generation and cash balance growth provide evidence against immediate historical cash depletion. | Counters an assumption of current-period cash burn; does not prove forward coverage. | Q2 2026 cash-flow statement, p. 4. [C17, C19] | Historical six-month result includes working capital, investing and financing effects. |
| Constraint — restricted cash | $96m reported as restricted cash. | Funds not confirmed available for general use cannot support the cash bridge. | Excluded from accessible liquidity; reported total cash alone would overstate usable resources. | Q2 2026 balance sheet, p. 2. [C8] | Restriction-specific release conditions are not detailed here. |
| Constraint — sizable lease cash payments | $687m of VICI/GLPI payments estimated for the remainder of 2026. | Rent is a recurring cash claim alongside debt service and capex. | Limits residual cash for deleveraging and increases sensitivity to operating weakness. | Q2 2026 MD&A, p. 22. [C12] | H1 2027 lease-payment estimate is not supplied. |
| Constraint — variable-rate debt | $6.0bn long-term variable-rate borrowings at June 30, 2026. | Higher reference rates raise interest expense and reduce liquidity available for other uses. | Adds interest-rate sensitivity to debt service and cash-flow durability. | Q2 2026 market-risk disclosure, p. 23. [C29] | No forward rate scenario or hedging offset is used in this bridge. |
| Constraint — no forward cash-flow and use schedule | Operating cash, working capital, taxes and full H1 2027 uses are not forecast in delivered evidence. | Missing forecast inputs prevent a complete bridge and runway test. | Liquidity sufficiency and ending balance remain unclassified; monitor reporting gap. | Q2 2026 interim period and available remainder-2026 schedules. [C10, C11, C12, C13, C17, C22] | Requires subsequent reporting and forecast/debt-service support. |
| Constraint — management sufficiency statement is a characterization | FY2025 filing states management expected liquidity to fund needs for the next twelve months and beyond. | Management outlook is supportive, but it does not replace a current, quantified cash bridge. | Counterevidence reduces concern about immediate shortfall but does not resolve missing H1 2027 uses or headroom. | FY2025 Form 10-K, p. 24. [C28] | Forward statement was made before June 30, 2026; no post-Q2 confirmation supplied. |

#### T2E.9 — Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up | Downstream Module Affected |
|---|---|---|---|---|---|
| Complete next-12-month operating cash forecast | Forecast CFO or operating cash flow from July 1, 2026 through June 30, 2027, with assumptions and period detail | Operating cash is the principal source for debt service, rent and capital needs. | T2E.5 ending accessible liquidity and T2E.6 runway cannot be calculated. | Obtain subsequent-period company forecast or cash-flow guidance with assumptions; reconcile to reported results. | CP-3, CP-3C, CP-6 |
| H1 2027 debt-service allocation | Separately timed principal and interest due January–June 2027 | The debt schedule supplies full-year 2027 values, not the portion inside the 12-month horizon. | Exact 12-month mandatory debt service remains unavailable. | Obtain current debt amortization and interest schedule by payment date. | CP-3C, CP-6 |
| H1 2027 lease cash payments | Lease-payment estimate for January–June 2027, including material financing-lease cash requirements | Remaining-2026 rent is disclosed, but the 12-month horizon extends into 2027. | Lease cash-use total and ending liquidity remain incomplete. | Obtain current VICI/GLPI lease cash schedule and any other material lease obligations for the horizon. | CP-3C, CP-6 |
| Forward cash taxes | Cash-tax estimate through June 30, 2027 | Taxes reduce cash available after operations; historical H1 taxes are not a forecast. | Mandatory-use total and bridge remain incomplete. | Obtain tax cash forecast and timing, including known federal/state payments. | CP-3, CP-6 |
| Forward working capital and seasonality | Quarterly forecast or historical seasonal working-capital movements after June 2026 | Working-capital absorption can occur before cash is available for creditors. | No forecast WC adjustment; Months to Empty cannot use a normalized burn basis. | Obtain quarterly receivables, prepayments, accrued liabilities, deposits and seasonality detail. | CP-3, CP-6 |
| Complete 12-month capex classification | H1 2027 capex estimate and maintenance-versus-growth/deferrable split | Maintenance and growth capex have different liquidity and operating consequences. | Remaining-2026 estimate does not provide total next-12-month capex. | Obtain current capex schedule by project, payment date, maintenance need and deferral flexibility. | CP-3, CP-3C, CP-6 |
| Revolver accessibility and covenant headroom | Complete current credit agreement, current calculations, conditions to draw, and post-June utilization | Reported capacity is not guaranteed future availability; financial covenant access may depend on testing conditions. | Opening availability is a June 30 calculation; future accessible liquidity and covenant-constrained capacity are not calculable. | Obtain complete current CEI Credit Agreement and current lender/covenant certificates and borrowing-base or other access data. | CP-3C, CP-4A, CP-6 |
| Post-June financial and transaction update | Later cash/debt balances, actual operating cash, financing changes and merger status after June 30 | Analysis date is October 2, 2026; interim filing ends June 30. | Current liquidity may differ from reported opening snapshot; no changes may be inferred. | Obtain subsequent SEC filings and material current reports; separately flag events after period end. | CP-3, CP-3C, CP-6 |
| Future distributions and transaction-related cash costs | Forecast or commitments for noncontrolling-interest distributions, merger costs and other transaction uses | Historical outflows do not establish future commitments or zero future cash use. | Other-cash-use line remains incomplete. | Obtain current transaction budget, cash-paid status and distribution commitments. | CP-3, CP-6 |
| Liquidity risk level and Months to Empty | Normalized recurring cash-burn basis and full 12-month cash bridge | Opening liquidity and a cash-generative half-year do not supply a positive burn rate or future net cash use. | Liquidity Risk Level remains Insufficient Information; Months to Empty is Not Calculable. | Recalculate after current forward cash flows, all uses and accessible capacity are documented. | CP-3, CP-3C, CP-6 |
| Subsequent-event coverage after June 30 | Subsequent events beyond the July 13 Alberta launch disclosed in the Q2 filing | A later refinancing, draw, acquisition, distribution or commitment could change liquidity materially. | Subsequent-period liquidity changes cannot be ruled in or out. | Review subsequent company filings through the analysis date; preserve each event separately from Q2 values. | CP-3, CP-3C, CP-6 |

## Evidence Trace

| Claim / calculation | Citation marker | Source document | Page |
|---|---|---|---:|
| June 30 cash and restricted cash | [C1], [C8] | Caesars Q2 2026 Form 10-Q | 2 |
| Reported aggregate cash and borrowing-capacity total | [C2] | Caesars Q2 2026 Form 10-Q | 22 |
| Revolver components and calculated available capacity | [C3]–[C7] | Caesars Q2 2026 Form 10-Q | 22 |
| Facility covenant compliance | [C9] | Caesars Q2 2026 Form 10-Q | 10 |
| Remaining-2026 principal and estimated interest | [C10], [C11] | Caesars Q2 2026 Form 10-Q | 9 |
| Remainder-2026 lease payments and capital expenditure estimates | [C12]–[C16] | Caesars Q2 2026 Form 10-Q | 22 |
| H1 operating cash, capex and total cash movement | [C17]–[C19] | Caesars Q2 2026 Form 10-Q | 4 |
| H1 cash interest and taxes | [C20]–[C22] | Caesars Q2 2026 Form 10-Q | 5 |
| H1 working-capital items and contract liabilities | [C23]–[C27] | Caesars Q2 2026 Form 10-Q | 4, 11 |
| Management liquidity outlook; variable-rate debt | [C28], [C29] | Caesars FY2025 Form 10-K; Caesars Q2 2026 Form 10-Q | 24; 23 |
| Merger-related costs and post-period Alberta launch | [C30], [C31] | Caesars Q2 2026 Form 10-Q | 6; 17 |
| Revolver commitment and drawn balance | [C32]–[C34] | Caesars Q2 2026 Form 10-Q | 10; 9 |
| Historical distribution to noncontrolling owners | [C35] | Caesars Q2 2026 Form 10-Q | 4 |

## Source Registry

Primary sources are the Q2 2026 Form 10-Q and FY2025 Form 10-K; the fourth and fifth credit amendments provide limited financing context and do not replace the full current credit agreement. The Q2 Form 10-Q is the controlling source for the June 30 liquidity snapshot, interim cash flow, debt-service schedule, remainder-2026 lease payments, capex estimates and covenant-compliance statement. All calculations are labelled, restricted cash is excluded, and the $1.963 billion available-revolver calculation is reconciled to the issuer’s reported $2.928 billion aggregate liquidity. Accepted CP-0, CP-1 and CP-2 artifacts are retained as restricted upstream context, not substituted for primary evidence. [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C17]

## Gaps & Conflicts

The key unresolved issue is the incomplete horizon: reported remainder-2026 estimates do not provide January–June 2027 debt service, rent, capex, taxes, working capital or operating cash. Therefore no exact 12-month cash-use total, ending accessible liquidity or positive cash-burn rate can be supported. The disclosed revolver table yields $1.963 billion after listed deductions, while the narrative describes CEI available capacity as approximately $1.9 billion; the table also includes $25 million of CVA RCF capacity. These are consistent in scale and scope after rounding, but the calculated amount remains a June 30 snapshot and not a guarantee of future access. [C2, C3, C4, C5, C6, C7]

Restricted cash is excluded. The H1 working-capital calculation uses the reported operating-asset/liability movements and is historical; it is not added again to CFO in the bridge. The H1 net increase in total cash is cash-generative but includes investing and financing activity and is not a normalized forward burn measure. [C8, C17, C19, C23, C24, C25, C26] The management sufficiency statement is a counterargument, not a quantified current forecast. [C28] CP-0’s source-limited status and lack of post-Q2 financial reporting remain unresolved; the Alberta launch after June 30 is kept separate from Q2 financial results. [C31]

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity, filename and host-owned front matter | Self-checked | Filename is derived as `CZR_CP-2D_20261002.md`; host-owned front matter is retained exactly and closed with a YAML boundary. |
| Upstream re-anchor | Restricted | CP-0, CP-1 and CP-2 are accepted same-run artifacts with matching issuer, period and run; all retain restricted status. |
| Source gate and module status | Ready with Limitations | Cash, revolver, debt service, leases, capex and interim cash flow are identifiable; material 12-month forecast inputs are missing. |
| Beginning liquidity | Self-checked | Cash is distinguished from restricted cash; accessible revolver is calculated from disclosed components and reconciles to reported aggregate liquidity. |
| Cash-use coverage | Restricted | Known uses are limited to remainder-2026 and H1 actuals; no category is assumed zero and H1 2027 estimates are missing. |
| Bridge calculation | Restricted | Opening liquidity is supported; ending 12-month liquidity is not calculated because operating cash and several cash-use inputs are unavailable. |
| Months to Empty | Not Calculable | H1 2026 cash and restricted cash increased by $93 million; that period is not a positive cash-burn basis and is not a normalized forecast. |
| Risk assessment | Insufficient Information | Source evidence supports an opening buffer and countervailing cash-generative history, but not a decision-useful full-horizon coverage conclusion. |
| Required canonical registers | Self-checked | T2E.1, T2E.2, T2E.3, T2E.4, T2E.5, T2E.6, T2E.7 and T2E.9 are present with all required columns and populated rows. |
| Citation and locator review | Self-checked | Citation excerpts are tied to supplied evidence pages; each citation marker is used in the Markdown body. |
| Confidence | 55/100 — Low | Conservative score reflects primary-source support for the opening snapshot but partial source coverage and missing full-horizon inputs; Restricted status caps the score at 59. |
| QA / committee status | Restricted / Requires More Work | Host validation follows this response; no host script result or finding is claimed. |