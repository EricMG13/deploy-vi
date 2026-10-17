---
module_id: "CP-2A"
module_name: "DownsidePathway"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2A-c979c6d3c1355f73"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-07-CP-2A"
credit_os_invocation_sha256: "8029141c86d8be6bdee2e1ccbc8d6231527740ce8f3ce0a66696467191a1bdef"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
  - module_id: "CP-1"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "feb32206df70f6261119dceb61308629455fa9537a6f5305a4d941c2fb2015a9"
confidence_score: 49
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [CP_2_NOT_ON_DELIVERED_ROUTE, COVENANT_HEADROOM_NOT_CALCULABLE, MERGER_FINANCING_MISSING, DEBTOR_CASH_ALLOCATION_MISSING, SOURCE_GATE_PARTIAL]
validation_warnings: [DEBT_FACE_BOOK_CARRYING_BASES_DIFFER, EBITDA_NOT_CONTRACTUAL, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-2G, CP-2D, CP-2E, CP-3, CP-3A, CP-3B, CP-3C, CP-4A, CP-5, CP-5A, CP-6, CP-6A, CP-MODEL]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-2A_20261002.md`. Owned object: issuer downside pathway and absorbed dated catalyst register. **Module status: Ready with Limitations; 49/100, Low; Restricted; Requires More Work.** Accepted CP-0 and CP-1 match issuer, run and Q2 2026 period. The delivered route does not include CP-2: its absent separate business-risk handoff limits, but does not invalidate, the CP-1 and primary-filing-based pathways. The issuer reports June covenant compliance, not numerical headroom. [C18] Host validation and completeness checks follow this answer; no result from them is claimed.

## Analysis

### Downside view

The earliest observable operating weakness is Las Vegas leisure visitation, room pricing and table-game hold, not an assumed company-wide EBITDA shock: second-quarter hold fell to 16.6% from 21.1%, and Las Vegas Adjusted EBITDA fell to $410 million from $469 million. [C1, C2, C3] Continued weakness would reduce operating cash generation before necessarily reducing rent, debt service or essential capex, leaving less cash for refinancing; this is a directional risk, not a projected default. First-half operating cash flow remained $675 million and lower capex protected after-capex cash, while $2,928 million of reported cash and borrowing capacity provides a conditional buffer. [C7, C8, C44] Escalate on persistent visitation/hold weakness together with declining cash or rising revolver use. The failure point cannot be quantified without debtor-level cash, contractual covenant calculations and pending-merger financing.

**Transmission and contrary case.** First-half issuer Adjusted EBITDA declined to $1,807 million from $1,839 million despite operating cash flow of $675 million versus $680 million. [C6, C7] [Calculation] CFO less property/equipment purchases was $340 million in H1 2026 versus $227 million in H1 2025; CFO already includes operating cash interest, so do **not** deduct the separately disclosed $368 million debt interest and $686 million GLPI/VICI rent-related interest again. [C8, C9, C10] Stronger Regional Adjusted EBITDA ($488 million versus $439 million in Q2) and lower capex are the strongest observed offsets. [C4, C8] They would defeat the near-term liquidity-squeeze thesis if sustained cash generation covers actual maintenance, lease and debt needs without incremental borrowing; the present evidence does not establish that durability. Windsor's March 2026 move into Regional also limits organic interpretation. [C29]

**Buffer and escalation.** June cash was $965 million; reported aggregate cash plus borrowing capacity was $2,928 million, not an unrestricted cash balance. [C45, C44] Disclosed remaining-2026 debt service of approximately $425 million, VICI/GLPI lease payments of approximately $687 million and expected capex of $310–390 million compete for cash generation. These are different cash-flow classifications and periods, not a calculation of residual liquidity. [C13, C14, C15] The June debt schedule then has $767 million of 2028 principal maturities and $1,574 million in 2029; deteriorating cash conversion before those maturities would raise refinancing dependence. [C12] The reported 6.50:1 leverage and 2.0:1 fixed-charge covenant limits are not actual ratios or headroom. [C16, C17, C18]

**Balance-sheet and funding discipline.** [Calculation] Canonical balance-sheet debt is $11,699 million ($114 million current plus $11,585 million long-term), versus $11,807 million face debt and $11,705 million debt-note book value. The $108 million face-to-canonical difference and $6 million note-book-to-canonical difference remain explicit; the note separately presents deferred revolver charges of $(6) million. Failed-sale financing obligations of $13,157 million are separately classified rather than silently added to canonical debt, but their rent cash demands remain credit-relevant. [C31, C32, C33, C47, C30] Customer deposits and other deferred revenue rose from $492 million at year-start to $545 million in June: this is non-debt wagering/service float, not trade payables or free cash. Withdrawals or fulfillment without replacement receipts could consume liquidity. [C19, C20, C37]

**Transaction boundary.** The May 27 merger agreement was signed during Q2, but closing remains conditional on stockholder and regulatory approvals. Its $31.00 cash consideration and conditional ticking feature are transaction terms, not a June debt financing estimate. [C21, C22] The July 13 Alberta launch is a **subsequent event** to the June reporting date; no launch proceeds or costs are blended into June results. [C26] This analysis assigns no security preference, recovery percentage, refinancing coupon or predicted merger outcome.

### Catalyst view

The dated forward watch, measured from October 2, 2026 through October 2, 2027, contains **four calendar entries**: the disclosed remainder-of-2026 payment window and three conditional merger dates/windows. The net catalyst bias is **uncertain with material downside exposure**: an approved, financed closing could resolve uncertainty, whereas delay, failed financing or transaction costs could consume creditor capacity. The May 27, 2027 initial end date is the highest-priority dated decision point; August 27 is conditional, not a forecast close. [C22, C23, C40] The merger's possible $200 million company termination fee and $450 million reverse fee depend on contractual circumstances; neither is presumed cash available or payable. [C24, C25] The dated 2028 bank maturity and conditional November 2027 extension are catalogued outside this calendar horizon. [C42, C41] CP-MODEL receives four ranked, dated or disclosed-window rows below, not a forecast.

### Analytical appendix — complete canonical registers

#### T2B.1 — Source Register
| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| S1 | CZR Q2 2026 Form 10-Q | Primary-Verified | June 2026; filed July 28, 2026 | CZR consolidated | Operating KPIs, cash, debt, commitments and merger dates [C1, C7, C12, C23] | Unaudited interim; no post-close financing or debtor cash allocation | Downside, dated catalysts, liquidity handoff |
| S2 | CZR FY2025 Form 10-K | Primary-Verified | FY2025 | CZR consolidated | Audited comparative and impairment sensitivity [C36] | Historical, not a June covenant calculation | Historical fragility context |
| S3 | CZR Q2 2026 results release | Secondary-Reputable | Q2/H1 2026 | CZR consolidated | Corroborating operating results | Filing controls statement definitions | Cross-check |
| U0 | Accepted CP-0 SourceReadiness | Upstream artifact; Restricted | Q2 2026; same run | CZR | Source inventory and legal/market limitations | Not a substitute for missing operative documents | Source gate |
| U1 | Accepted CP-1 CanonicalDataFoundation | Upstream artifact; Restricted | Q2 2026; same run | CZR consolidated | Carrying-debt basis, FCF calculation and period bridge | Issuer Adjusted EBITDA is not contractual; quarter-level CFO absent | Financial baseline |

#### T2B.2 — Business Model Snapshot
| Dimension | Source-Supported Fact | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|
| Revenue model | Gaming, hotel, food and other reported revenue streams | Discretionary visits and wagering change cash receipts | Revenue decline can precede debt-service pressure | S1 statements [C3] | Segment cash contribution unavailable |
| Product/service criticality | Casino, lodging and online betting are offered | Discretionary demand can defer visits or wagers | Less reliable stressed cash flow | S1 MD&A [C3, C5] | Demand elasticity unmeasured |
| Customer/end-market exposure | Las Vegas leisure visitation softened | Weaker visits reduce room and gaming receipts | Margin and cash risk | S1 Las Vegas MD&A [C3] | No customer concentration schedule |
| Price/mix | Las Vegas room rates compressed | Lower yield weakens cash contribution | Reduced fixed-charge cushion | S1 Las Vegas MD&A [C3] | Room-rate sensitivity unavailable |
| Volume drivers | Q2 Las Vegas hold 16.6% versus 21.1%; occupancy 95.5% versus 96.8% | Hold and occupancy compound visit weakness | Less cash available after committed payments | S1 KPIs [C1, C43] | Hold is volatile, not a forecast |
| Contract duration/churn/retention | Customer deposits fund future wagering or service | Deposit unwind can reverse funding float | Liquidity monitoring needed | S1 revenue note [C37, C19] | Churn/retention not disclosed |
| Cost structure | Q2 issuer Adjusted EBITDA $920 million versus $955 million | Expenses and obligations do not automatically reset with hold | Fixed-charge cushion can narrow | S1 reconciliation [C6, C10] | Contractual EBITDA differs |
| Input-cost exposure | Digital gaming-tax increases pressured Q2 margin | More tax per gaming dollar lowers contribution | FCF durability weakens | S1 Digital MD&A [C5] | No jurisdictional stress bridge |
| Working-capital needs | Customer deposits/deferred revenue $545 million in June | Settlements and fulfillment require future cash/service | Float is conditional liquidity | S1 revenue note [C19, C37] | Deposit runoff timing absent |
| Capex intensity | H1 cash property purchases $335 million | Renovation or maintenance spend can persist under weaker earnings | FCF reduction | S1 cash flows [C8] | Historical maintenance split absent |
| Liquidity dependency | $2,928 million reported cash-plus-capacity | Borrowing draws replace operating cash if stress persists | Liquidity and covenant sensitivity | S1 liquidity [C44, C35] | Borrower-access conditions not modeled |
| Debt service/refinancing dependency | Remainder-2026 service $425 million; later maturities scheduled | Falling cash before maturities increases refinancing reliance | PD and market-access monitoring | S1 MD&A/note [C13, C12] | No projected closing debt |

#### T2B.3 — Fragility Map
| Fragility Driver | First Break Point | Evidence | Risk Mechanic | Credit Implication | Confidence | Source Trace |
|---|---|---|---|---|---|---|
| Revenue | Las Vegas leisure visits, hotel yield and table hold | Q2 hold and management explanation | Lower win/rooms → less cash contribution | Negative — Revenue Decline | High | S1 [C1, C3] |
| Margin | Digital gaming-tax and hold mix | Q2 digital earnings explanation | Tax cost and lower hold absorb revenue growth | Negative — Margin Compression | High | S1 [C5] |
| Cash-conversion | Maintenance/capital commitments during softer CFO | H1 CFO and purchases | Weaker CFO with continuing capex → lower FCF | Negative — Liquidity Deterioration | Medium | S1 [C7, C8, C15] |
| Liquidity | Cash decline or CEI revolver draw following negative cash conversion | Reported liquidity and CEI availability | Conditional borrowing capacity replaces cash | Negative — Liquidity Deterioration | Medium | S1 [C44, C35] |
| Capital-structure | Operating weakness before 2028–30 principal requirements | Maturity schedule | Lower FCF slows deleveraging before refinancing | Negative — Refinancing Risk | Medium | S1 [C12] |
| Legal/structural | Unverified actual covenant headroom and debtor cash | Compliance and stated tests | Reported compliance cannot establish stress capacity or recovery | Negative — Covenant Erosion, conditional | Low | S1 [C16, C17, C18, C34] |
| Governance/sponsor | Conditional acquisition closing and financing | Merger conditions, no repurchases currently expected | Transaction uncertainty can change debt needs and cash policy | Monitoring escalation, not assumed creditor loss | Medium | S1 [C22, C39] |
| Macro | Floating-rate debt cash burden | $6.0 billion variable-rate borrowings | Rate increase raises interest and reduces after-interest cash | Negative — Liquidity Deterioration, conditional | High | S1 [C27, C9] |

#### T2B.4 — Stress Transmission Table
| Operating Stress | Cash-Flow Impact | Leverage / Liquidity Result | Credit Consequence | Evidence Status | Source Trace |
|---|---|---|---|---|---|
| Persistently weak Las Vegas visits/hold → fewer gaming and room receipts | Lower contribution → reduced CFO; capex still requires cash | FCF buffer narrows → greater cash/revolver reliance → later refinancing exposure | PD/monitoring rises if weakness persists; no quantified default point | Directional Only | S1 [C1, C3, C7, C8, C12] |
| Digital tax increase plus adverse betting hold → margin compression | Lower segment cash contribution despite handle | Less cash for debt/rent and investments | Watch FCF, not handle alone | Directional Only | S1 [C5, C46, C10] |
| Customer deposit runoff → net funding float contracts | Settlement/fulfillment without replacement receipts → cash absorption | Available liquidity declines before debt principal changes | Liquidity/PD monitor; not incremental debt | Analyst Inference | S1 [C19, C20, C37] |
| Floating rates rise on variable-rate borrowings | Cash debt interest increases → CFO/FCF falls, all else equal | Cash buffer and potential refinancing capacity contract | Market-access and covenant monitoring | Directional Only | S1 [C27, C9, C16] |
| Merger delayed or terminated → transaction decisions and possible costs | Conditional financing/fees can alter cash needs | Post-close leverage and cash cannot be inferred from June balances | Event-driven PD/LGD/security review required | Directional Only | S1 [C22, C24, C25] |

#### T2B.5 — Downside Pathway Register
| Pathway Row ID | Pathway Category | Driver | Causal Vector | PD/LGD/RV/Monitoring Consequence | Source Trace | Confidence | Downstream Module |
|---|---|---|---|---|---|---|---|
| CP-2A-DP-001 | First Break Point | Revenue | Las Vegas visitation/hold weakens → room/gaming receipts fall | Leading PD monitor | S1 [C1, C3] | High | CP-2G, CP-6 |
| CP-2A-DP-002 | Transmission Accelerator | Margin | Weaker receipts plus tax/labour exposure → segment margin compresses | Lower earnings cushion; no spread estimate | S1 [C2, C5] | Medium | CP-2E, CP-3 |
| CP-2A-DP-003 | Cash-Flow Conversion Point | Capex and funding float | CFO slows while necessary capex and deposit settlements consume cash → FCF contracts | Monitor sustainable FCF | S1 [C7, C8, C19, C37] | Medium | CP-2D |
| CP-2A-DP-004 | Liquidity Pinch Point | Fixed cash uses | FCF shortfall → cash declines/revolver draws before debt and rent dates | Liquidity/PD escalation | S1 [C11, C13, C14, C15] | Medium | CP-2D, CP-3B |
| CP-2A-DP-005 | Covenant Inflection | Tested earnings | Cash/earnings weakness → potential test deterioration; numerical headroom unknown | Actual breach point Not Calculable from Provided Materials | S1 [C16, C17, C18, C28] | Low | CP-4A |
| CP-2A-DP-006 | Refinancing Inflection | Scheduled maturities | Less deleveraging → larger funding requirement against 2028–30 schedule | Refinancing PD monitor, no assumed failed issuance | S1 [C12] | Medium | CP-3C |
| CP-2A-DP-007 | PD Escalator | Merger uncertainty | Approval/financing delay → uncertain cash/debt structure and transaction expense | Reassess exposure on filed financing or termination | S1 [C22, C23, C24] | Medium | CP-3, CP-6 |
| CP-2A-DP-008 | LGD/Recovery Escalator | Claim and collateral perimeter | Potential new funding or covenant action → claim priority must be rechecked | Recovery direction unquantified; no security ranking | S1 guarantees [C34]; merger [C22] | Low | CP-3A, CP-4A |
| CP-2A-DP-009 | Monitoring Trigger | Operating/cash divergence | Persistent weak hold plus declining CFO or rising drawings → review liquidity and debt tests | Escalate review rather than assert a default threshold | S1 [C1, C7, C35] | Medium | CP-6, CP-5 |

#### T2B.6 — Downside Sensitivity Matrix
| Sensitivity | Input Basis | Formula / Method | Result | Credit Interpretation | Status | Source Trace |
|---|---|---|---|---|---|---|
| Observed H1 after-capex cash change | CFO 675/680; property purchases 335/453, 2026/2025 | CFO minus cash property purchases | $340m versus $227m; +$113m | Capex savings offset otherwise flat CFO; not a stress forecast | Calculated | S1 [C7, C8] |
| Observed Q2 Las Vegas hold change | 16.6% versus 21.1% | Source-reported percentage-point difference | −4.5 percentage points | Shows gaming volatility; cannot convert to cash without cost/tax response | Calculated | S1 [C1] |
| Static rate exposure | June variable-rate borrowings $6.0bn | All else equal, 1 percentage point × disclosed approximate principal | Approximately $60m annualized extra interest; illustrative, not forecast | Reduces cash generation if rates rise and principal stays constant | Calculated | S1 [C27] |
| Covenant headroom after EBITDA decline | Published 6.50:1 and 2.0:1 tests; no actual test values | Requires contractual earnings, net debt and test dates | Not Calculable from Provided Materials — actual covenant inputs absent | No breach threshold can be inferred from reported compliance | Not Calculable | S1 [C16, C17, C18, C28] |
| Merger refinancing or recovery | Cash consideration conditional on approvals | Requires financing commitments and operative priority terms | [Directional Only] — financing and closing outcome unknown | Reassess debt service and security claims when documents arrive | Directional Only | S1 [C21, C22, C34] |

#### T2B.7 — Monitoring Sensitivity Flags
| Trigger ID | Indicator | Leading / Lagging | Threshold or Qualitative Signal | Linked Pathway Row | Escalation Consequence | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| CP-2A-MON-001 | Las Vegas visits, hold and room yield | Leading | Continued weakness alongside lower occupancy; no invented cutoff | CP-2A-DP-001 | Review CFO assumptions | S1 [C1, C3, C43] | Quantitative threshold not available in provided materials. |
| CP-2A-MON-002 | CFO less property purchases | Lagging | Sustained deterioration from reported H1 conversion | CP-2A-DP-003 | Rebuild cash bridge | S1 [C7, C8] | H1 comparison is not guidance. |
| CP-2A-MON-003 | Cash and CEI revolver use | Leading | Cash declines while drawings rise | CP-2A-DP-004 | Check debtor liquidity and covenants | S1 [C45, C35] | Quantitative threshold not available in provided materials. |
| CP-2A-MON-004 | Actual compliance ratios/waiver | Lagging | Declining certified headroom or request for relief | CP-2A-DP-005 | Urgent covenant review | S1 [C16, C17, C18] | Test inputs not supplied. |
| CP-2A-MON-005 | Merger approval/financing and end-date status | Leading | Approval delay, new financing filing or termination | CP-2A-DP-007 | Refresh transaction-specific PD and claims | S1 [C22, C23, C24] | Closing date not forecast. |
| CP-2A-MON-006 | Deposit/deferred-revenue trend | Leading | Sustained runoff without offsetting cash generation | CP-2A-DP-003 | Assess wagering-settlement cash requirement | S1 [C19, C20, C37] | Quantitative threshold not available in provided materials. |

#### T2B.8 — Cross-Module Handoff Register
| Downstream Module | Handoff Item | Why It Matters | Required Consumer Action | Source / Pathway Link | Limitation |
|---|---|---|---|---|---|
| CP-2D | CFO, capex, deposit float, lease and debt cash uses | Defines first liquidity pinch | Bridge cash without double-deducting paid interest | DP-003/004 [C7, C8, C9, C10, C19] | Debtor cash/maintenance split missing |
| CP-2E | $6.0bn floating debt, gaming tax and leisure exposure | Changes cash interest and demand | Model sourced rate/operating drivers separately | DP-002/004 [C27, C5, C3] | No future rate path |
| CP-3 | Las Vegas first break and later refinancing exposure | RV downside requires security-aware pricing | Compare market evidence without a security recommendation from CP-2A | DP-001/006 [C1, C12] | No current trade evidence in this module |
| CP-3A | Guaranteed secured debt; uncertain transaction financing | Claim ranking changes recovery | Obtain operative legal documents and separate borrower claims | DP-008 [C34, C22] | No recovery valuation |
| CP-3B | Conditional liquidity and May 2027 catalyst | May constrain downside budget | Set sizing only after portfolio inputs | DP-004/007 [C44, C23] | No portfolio holdings supplied |
| CP-3C | 2028–30 maturity ramp and merger | Refinance gap can widen | Analyze refinancing and LME only with financing/legal evidence | DP-006/007 [C12, C22] | No refinancing terms or sponsor action assumed |
| CP-4A | Reported covenant limits but no actual test headroom | Compliance is not stress cushion | Obtain agreement definitions and certificates | DP-005 [C16, C17, C18] | No basket/leakage determination |
| CP-5A | Carrying/face debt conflict and illustrative sensitivities | Prevents false precision | Check arithmetic, source scope and status | DP-004/005 [C31, C32, C33, C47] | Host QA pending |
| CP-5 | First-break and cash-flow claim chain | Citation integrity | Verify direct versus inferred links | DP-001/003 [C1, C7, C8] | Deposit-runoff path inferred |
| CP-6/CP-6A | Fastest path, conditional buffer and key dates | Committee/watchlist synthesis | Preserve limitations, no security choice | DP-001/004/007 [C1, C44, C23] | Requires legal, cash and market follow-up |
| CP-2G | Operating first break and reported period baselines | Forward cases need actual drivers | Source explicit forecast inputs before numeric case | DP-001/003 [C1, C7] | No management downside forecast |
| CP-MODEL | Ranked dated catalyst projection | Enables consistent workbook monitoring | Consume tagged table; keep conditional dates conditional | T5.2 [C13, C23, C21, C40] | Projection is not a pro forma financing case |

#### T2B.9 — Gaps Ledger
| Gap ID | Missing Data | Why It Matters | Affected Pathway / Calculation / Trigger | Consequence for Confidence | Required Follow-Up Source |
|---|---|---|---|---|---|
| CP-2A-GAP-001 | Contractual covenant EBITDA, netting, certificates and actual headroom | Cannot locate breach point | DP-005; MON-004 | High | Current agreements and compliance certificates |
| CP-2A-GAP-002 | Full merger agreement and closing financing | Cannot price post-transaction debt or fee outcomes | DP-007/008; T5 events | High | Executed agreement, amendments and commitments |
| CP-2A-GAP-003 | Borrower-level unrestricted/restricted cash and accessible revolver | Consolidated buffer may not reach each obligor | DP-004 | High | Debtor liquidity and restriction schedule |
| CP-2A-GAP-004 | Maintenance versus discretionary cash capex and deposit runoff schedule | Durable FCF and float unwind unknown | DP-003; MON-002/006 | Medium | Project cash spend and customer-liability rollforward |
| CP-2A-GAP-005 | CP-2 business-risk handoff not included in this selected delivery | Independent business-risk cross-check unavailable | T2B.3; overall confidence | Medium | Route-selected CP-2 analysis, if subsequently supplied |
| CP-2A-GAP-006 | Trading, peer stress and operative collateral/basket details | Cannot infer RV, LME capacity or recovery | DP-006/008 | High | Dated market and signed legal source pack |
| CP-2A-GAP-007 | Forward cash forecast and room/hold cost sensitivity | No cash exhaustion time or operating threshold | DP-001/004; T2B.6 | High | Management forecast and property contribution bridge |

#### T5.1 — Event Source Register
| Event ID | Source Document | Event Description | Event Category | Date/Range | Evidence Quality | Source Reliability |
|---|---|---|---|---|---|---|
| EV-01 | S1 10-Q [C13, C14, C15] | Disclosed debt-service, lease and capex cash uses | Debt & Capital Structure | Remainder of 2026 | Filed estimate | Primary interim filing |
| EV-02 | S1 10-Q [C23] | Initial merger agreement end date; termination is conditional | Corporate | 2027-05-27 | Filed contract summary | Primary interim filing; full agreement absent |
| EV-03 | S1 10-Q [C21] | Conditional ticking-fee reference date if closing has not occurred | Corporate | 2027-06-26 | Filed contract summary | Primary interim filing; not a closing date |
| EV-04 | S1 10-Q [C40] | First extended end date, conditional on specified unfulfilled approvals | Corporate | 2027-08-27 | Filed contract summary | Primary interim filing; conditional |
| EV-05 | S1 10-Q [C41] | Further extended end date, conditional and beyond selected horizon | Corporate | 2027-11-27 | Filed contract summary | Primary interim filing; conditional |
| EV-06 | S1 10-Q [C12, C42] | CEI revolver/term-loan maturity; scheduled 2028 principal | Debt & Capital Structure | 2028-01-31 | Filed debt terms | Primary interim filing; outside horizon |

#### T5.2 — Catalyst Calendar
| Date/Window | Event Description | Event Category | Credit Relevance Summary | Source |
|---|---|---|---|---|
| Remainder of 2026 | Disclosed debt service, VICI/GLPI payments and capex | Debt & Capital Structure | Cash-generation coverage and use of reported capacity; not a residual-cash forecast | S1 [C13, C14, C15] |
| 2027-05-27 | Initial merger end date, with contractual extensions possible | Corporate | Failure or extension changes transaction and financing uncertainty | S1 [C23, C40] |
| 2027-06-26 | Conditional ticking-fee reference date | Corporate | If closing has not occurred, per-share consideration mechanism can change; no assumed cash debt | S1 [C21] |
| 2027-08-27 | Conditional first extended end date | Corporate | Monitor outstanding approvals and whether a further extension applies | S1 [C40, C41] |

#### T5.3 — Event Risk Register
| Event ID | Description | Probability | Credit Impact Channel(s) | Impact Severity | Affected Metrics | Risk Direction | Source |
|---|---|---|---|---|---|---|---|
| EV-01 | Scheduled/estimated cash uses in disclosed 2026 window | High | Liquidity, debt service, PD | High | CFO, cash, revolver | Negative | S1 [C13, C14, C15] |
| EV-02 | Initial merger end-date decision | Unknown | Liquidity, refinancing, PD, LGD | High | Financing, cash, debt perimeter | Uncertain | S1 [C22, C23, C24] |
| EV-03 | Conditional consideration ticking date | Unknown | Liquidity, refinancing | Medium | Consideration; funding requirement unknown | Uncertain | S1 [C21] |
| EV-04 | Conditional first extended end date | Unknown | Liquidity, refinancing, PD | High | Financing and timing | Uncertain | S1 [C40, C22] |
| EV-05 | Conditional later extended end date, beyond horizon | Unknown | Liquidity, refinancing | High | Transaction timing | Uncertain | S1 [C41] |
| EV-06 | 2028 bank maturity, beyond horizon | High | Refinancing, liquidity, PD | High | Debt principal and access | Negative | S1 [C42, C12] |

#### T5.4 — Probability/Impact Matrix
| Event ID | Description | Probability | Impact | P/I Classification |
|---|---|---|---|---|
| EV-01 | Remainder-2026 cash uses | High | High | Critical monitoring of coverage; not a default prediction |
| EV-02 | Initial merger end-date decision | Unknown | High | High uncertainty |
| EV-03 | Conditional ticking date | Unknown | Medium | Medium uncertainty |
| EV-04 | Conditional first extension | Unknown | High | High uncertainty |
| EV-05 | Further extension beyond horizon | Unknown | High | High uncertainty; outside horizon |
| EV-06 | 2028 bank maturity | High | High | Critical forward monitor; outside horizon |

#### T5.5 — Monitoring Priority Table
| Event ID | Description | Priority | Monitoring Frequency | Trigger Condition | Responsible Module |
|---|---|---|---|---|---|
| EV-01 | Remainder-2026 cash commitments | Critical | Quarterly | CFO weakens while cash/draws deteriorate | CP-2D |
| EV-02 | Initial merger end date | High | Event-driven | Approval status changes, extension or termination filing | CP-6 |
| EV-03 | Conditional ticking date | Medium | Event-driven | No closing by reference date and updated funding disclosed | CP-3C |
| EV-04 | Conditional first extended end date | High | Event-driven | Regulatory delay or further extension | CP-6 |
| EV-05 | Later extension outside horizon | Medium | Event-driven | Extension becomes effective | CP-6 |
| EV-06 | 2028 bank maturity outside horizon | Critical | Quarterly | Refinancing or amendment announced; weaker cash beforehand | CP-3C |

#### T5.6 — Watchlist Handoff Register
| Event ID | Description | Priority | Receiving Module | Handoff Content | Timing | Rationale |
|---|---|---|---|---|---|---|
| EV-01 | Cash-use window | Critical | CP-6, CP-5A | Coverage against cash generation; avoid double-counting interest [C9, C10, C13] | Remainder of 2026 | Liquidity transmission |
| EV-02 | Initial merger end date | High | CP-3, CP-6 | Approval, financing, extension or termination status [C22, C23] | 2027-05-27 | Post-deal debt/security uncertainty |
| EV-04 | Conditional extension | High | CP-5A, CP-6 | Verify condition before using extended date [C40] | 2027-08-27 | Avoid assumed closing |
| EV-06 | 2028 bank maturity | Critical | CP-3, CP-6 | Refinancing status and observed operating cash [C42, C7] | 2028-01-31; outside horizon | Material next refinancing monitor |

#### T5.7 — Gaps & Limitations Ledger
| Gap Description | Affected Section | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|
| Full merger/financing documents not delivered; approval and closing probabilities unquantified | EV-02–05 | Cannot forecast cash debt or fee payment | High | Obtain controlling filings and commitments |
| November 2027 conditional extension falls outside October 2, 2027 horizon | EV-05; calendar | Longer-dated event not silently discarded | Medium | Extend monitor when horizon rolls forward [C41] |
| January 2028 maturity falls outside selected horizon | EV-06; calendar | Refinancing still material to pathway | High | Carry forward into next dated calendar [C42] |
| No specified date for any refinancing announcement or covenant certificate | Calendar | Cannot calendar invented milestones | Medium | Monitor filed announcements and certificates |
| No numeric probability basis or actual covenant headroom | Matrix; priorities | Ordinal uncertainty and qualitative triggers only | High | Obtain covenant tests and financing evidence |

#### cp2b.cp_model_catalysts
<!-- table-id: cp2b.cp_model_catalysts -->
| rank | event_date_or_window | event | credit_relevance | status | source_id | source_locator | as_of |
|---:|---|---|---|---|---|---|---|
| 1 | Remainder of 2026 | Disclosed debt, lease and capex payment window | Test cash generation against commitments; not a forecast deficit | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | MD&A pp.39–40 [C13, C14, C15] | 2026-10-02 |
| 2 | 2027-05-27 | Initial conditional merger end date | Extension or termination can change refinancing and liquidity analysis | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | Note 1 p.10 [C23] | 2026-10-02 |
| 3 | 2027-06-26 | Conditional consideration ticking reference | Funding requirement may change if closing delayed; amount unknown | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | Note 1 p.9 [C21] | 2026-10-02 |
| 4 | 2027-08-27 | Conditional first extended merger end date | Approval status determines whether the further extension applies | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | Note 1 p.10 [C40, C41] | 2026-10-02 |

## Evidence Trace

| Claim | Marker | Document | Page / use |
|---|---|---|---|
| Las Vegas first break and Regional offset | [C1, C2, C3, C4, C43] | Q2 2026 10-Q | pp.20–21; observed operations |
| Cash generation, capex and fixed cash payments | [C7, C8, C9, C10, C13, C14, C15, C38] | Q2 2026 10-Q | pp.4–5, 22; different cash-flow roles, including asset acquisitions |
| Debt, liquidity and covenant bases | [C12, C16, C17, C18, C30, C31, C32, C33, C35, C44, C45, C47] | Q2 2026 10-Q | pp.2, 9–10, 22; carrying versus face |
| Float and changing operating perimeter | [C19, C20, C29, C37] | Q2 2026 10-Q | pp.6, 11; conditional funding |
| Merger dates, terms and conditionality | [C21, C22, C23, C24, C25, C40, C41] | Q2 2026 10-Q | pp.5–6; dated catalysts |
| Subsequent operating launch | [C26] | Q2 2026 10-Q | p.17; post-June event |
| Historical impairment sensitivity | [C36] | FY2025 10-K | p.26; historical disclosed sensitivity, not a June forecast |

## Source Registry

T2B.1 lists the three delivered primary/issuer documents and two accepted same-run handoffs. CP-0's broader inventory mentions legal and market sources not delivered as direct evidence to this module; no unsupported clause, trade or peer statistic is adopted. CP-1 supplies the accepted financial baseline, including the constructed H1 CFO-minus-capex comparison; this handoff independently cites the underlying filing. CP-2 is not in the host-owned upstream list. The Q2 filing reports both face and book debt presentations; neither replaces the separately identified balance-sheet carrying basis. [C31, C32, C33, C47]

## Gaps & Conflicts

T2B.9 and T5.7 are cumulative for their respective pathway and event purposes. **Definition conflict CF-1:** June principal debt $11,807 million (debt-note face), debt-note book $11,705 million, balance-sheet current plus long-term $11,699 million and separately displayed revolver deferred charges $(6) million. Roles explain the $108 million face-to-canonical and $6 million note-book-to-canonical deltas; no single number silently substitutes for another. [C31, C32, C33, C47] **CF-2:** issuer Adjusted EBITDA excludes items not necessarily excluded by financing agreements; neither reported compliance nor the issuer earnings measure proves actual covenant capacity. [C18, C28] **CF-3:** rent-related financing interest and debt interest are distinct cash disclosures; CFO must not be reduced by either a second time. [C7, C9, C10] No undisclosed merger closing or refinancing date is inserted into June results. The merger dates are conditional; Alberta's July 13 launch is flagged after the reporting date. [C22, C26]

## QA Validation

| Self-check | Result | Basis and disposition |
|---|---|---|
| Identity and lineage | PASS locally | Host-owned front matter unchanged; CP-0 and CP-1 accepted for the same issuer/run/period. |
| Workflow and register inventory | PASS locally | Ten downside steps, absorbed nine-step event phase, T2B.1–T2B.9, T5.1–T5.7 and ranked CP-MODEL projection represented. |
| Causal and date discipline | RESTRICTED | Every stress path identifies an operating first break and cash conversion; unknown headroom and conditional dates remain bounded. |
| Definitions and subsequent events | PASS locally | Face/book/carrying, financing-obligation interest and post-June Alberta launch separated. |
| Confidence self-scoring | RESTRICTED | Ten material claims classified: eight directly sourced, one calculated, one analyst inference, giving E=93; 18 of 20 assessed source/schema field groups covered, C=90; partial source gate S=0.7; one open material limitation P=15. Formula yields 49.26, rounded to 49/Low; Restricted. |
| Host validators | PENDING | Host validation and completeness checks follow the answer; no script output or exit status claimed. |

**Overall,** CZR's primary fragility is sustained Las Vegas demand/hold weakness against significant fixed cash uses. The fastest supported downside path is weaker visits/hold → reduced operating cash conversion → lower cash or greater revolver reliance → increased covenant/refinancing scrutiny. Monitor occupancy, hold, CFO and drawings together. The buffer is real but conditional; actual failure or breach points require debtor cash, contractual test values and merger financing. **CP-2A Completed with Limitations. Primary Fragility: Las Vegas visits/hold. Fastest Downside Path: operating cash weakness to liquidity and refinancing pressure, directional only. Monitoring Signal: persistent Las Vegas weakness alongside declining cash or rising drawings; quantitative escalation threshold not available.** Next analytical command: `Run CP-2G`, with the stated gaps preserved.