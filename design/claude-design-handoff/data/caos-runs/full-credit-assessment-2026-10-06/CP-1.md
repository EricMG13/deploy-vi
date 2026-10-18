---
module_id: "CP-1"
module_name: "CanonicalDataFoundation"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1-baaef2d9df7740bb"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-02-CP-1"
credit_os_invocation_sha256: "34d1503347c606e6b6b952ac49357afb9386c7a774594ab3aff5ff99a4b03704"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
confidence_score: 57
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - "SOURCE_LIMITED_NOT_COMMITTEE_READY"
  - "NO_POST_Q2_2026_FINANCIALS"
  - "CP_MODEL_LESS_THAN_FOUR_COMPLETE_QUARTERS"
  - "CASH_FLOW_COMPONENTS_NOT_REPORTED_DISCRETELY_FOR_Q2"
validation_warnings:
  - "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED"
  - "CP_MODEL_RECONCILIATION_AND_HISTORICAL_QUARTER_COVERAGE_INCOMPLETE"
downstream_consumers: [CP-1B, CP-1C, CP-2, CP-2A, CP-2D, CP-3, CP-3C, CP-4, CP-4A, CP-5, CP-5A, CP-MODEL]
---

## Audit Summary

**Canonical artifact:** `CZR_CP-1_20261002.md`. **Status:** Restricted; confidence 57/100, Low; committee status Requires More Work. The accepted CP-0 handoff is Restricted and flags a source-limited pack and no post-Q2 financial reporting. CP-1 uses the delivered FY2025 10-K, Q2 2026 10-Q and Q2 results release; no outside retrieval is available here. The audited annual and unaudited interim statements support a defined financial baseline, but not a current October balance sheet, four complete quarterly periods, or a complete covenant-capacity assessment. The CP-MODEL interface is supplied, but is blocked by the absence of four complete quarters of segment and debt schedules. Host validation follows this response; no host result is claimed.

## Analysis

### Analytical read-through

The canonical record shows FY2025 revenue of $11,486 million and Adjusted EBITDA of $3,624 million; H1 2026 revenue rose 2.8% year over year to $5,863 million while Adjusted EBITDA fell 1.7% to $1,807 million. Q2 revenue increased 3.0%, but Adjusted EBITDA declined 3.7% to $920 million. [C3, C4, C17, C18] At June 30, balance-sheet carrying debt was $11,699 million and cash was $965 million; the issuer’s debt table separately reports $11,807 million face principal. [C8, C9] The risk mechanic is that substantial interest and lease commitments absorb cash while operating performance varies by segment; this constrains cash available for debt reduction and refinancing flexibility. Filed cash flow and balance-sheet figures are usable, but cash-flow data are not discrete for Q2, so quarterly cash conversion is not established. [C5, C6, C10, C19]

The most decision-useful changes are summarized below. Values are source-reported unless expressly identified as calculated.

| Measure | FY2025 | H1 2026 | Change / comparison |
|---|---:|---:|---:|
| Net revenue, $m | 11,486 | 5,863 | H1 +2.8% YoY [C3, C18] |
| Adjusted EBITDA, $m | 3,624 | 1,807 | H1 -1.7% YoY [C4, C17] |
| Operating cash flow, $m | 1,302 | 675 | H1 2025 comparator 680 [C5, C6] |
| Balance-sheet carrying debt, $m | 11,784 | 11,699 | At FY2025 and June 30, 2026 [C7, C8] |

**Segment and earnings quality.** FY2025 Las Vegas revenue declined to $4,049 million while Regional revenue was $5,756 million and Digital revenue was $1,408 million; Digital Adjusted EBITDA improved from $117 million to $236 million, while Las Vegas Adjusted EBITDA declined from $1,907 million to $1,728 million. [C22, C4] In Q2 2026, Regional revenue increased to $1,570 million and Las Vegas revenue declined to $1,017 million; Las Vegas Adjusted EBITDA was $410 million versus $469 million in Q2 2025. [C23, C17] The mechanic is uneven demand and hold performance across markets and channels: Regional growth may offset, but does not remove, Las Vegas weakness or digital tax and hold volatility. For creditors this creates variability in the cash generation available for debt service; segment strength should not be treated as consolidated deleveraging without cash-flow confirmation.

**Debt, interest and lease burden.** The canonical debt measure is balance-sheet current debt plus long-term debt, net of financing costs: $11,784 million at December 31, 2025 and $11,699 million at June 30, 2026. [C7, C8] Face principal was $11,905 million and $11,807 million, respectively; the figures are not interchangeable. [C9] At year-end, the filing estimates $1.4 billion of 2026 VICI/GLPI rent, separate from balance-sheet debt. [C19, C26] Operating weakness or higher variable borrowing costs would therefore flow through interest and rent requirements before funds are available for discretionary investment or debt repayment, reducing debt-service and refinancing flexibility. The filings report covenant compliance at June 30, but the supplied statements do not provide a current covenant headroom calculation; no capacity is inferred.

**Cash flow and operating float.** Operating cash flow was $1,302 million in FY2025 and $675 million in H1 2026; property and equipment purchases were $805 million and $335 million. [C5, C6, C20, C21] The derived CFO less PP&E purchases is $497 million for FY2025 and $340 million for H1 2026; it is not issuer-reported FCF and excludes other investing items, financing, debt service and rent. Customer deposits and other deferred revenue were $492 million at FY2025 year-end and $545 million at June 30, 2026; this is a customer funding float accompanied by future gaming, wagering, lodging or service obligations, not debt or ordinary payables. [C13, C14] A demand shock or accelerated customer withdrawals/redemptions could turn that float into cash outflow, weakening liquidity. The supplied data do not identify the portion immediately refundable or the timing of fulfillment, so its liquidity value is qualified.

**Definitions, contrary evidence and monitoring.** The strongest counterweight is positive H1 revenue growth, H1 operating cash generation, and reported covenant compliance. [C6, C18] That evidence would materially strengthen the view if sustained in later quarters and accompanied by debt reduction and disclosed covenant headroom. It does not overcome lower H1 Adjusted EBITDA, high debt, large lease commitments, or the absence of post-June financial information. The primary monitoring triggers are subsequent reported cash/debt balances, sustained segment EBITDA, the maturity/refinancing profile, variable-rate expense and lease payments, customer-deposit movements, and any merger-related change. The Q2 filing reports an Alberta mobile launch on July 13, 2026; it is a subsequent event and is excluded from Q2 financial figures. [C15]

### FS Coverage

| Statement | Coverage in supplied sources | Key limitation |
|---|---|---|
| Income statement | Audited FY2023–FY2025; Q2 and H1 2025/2026 | Some canonical detail, including COGS and gross profit, is not separately reported. |
| Cash flow | FY2023–FY2025; H1 2025/2026 | No discrete Q2 cash-flow statement; Q2 cash flow is null, not zero. |
| Balance sheet | December 31, 2024/2025 and June 30, 2026 | Interim periods are unaudited; no post-June balance sheet. |
| Segment / KPI | Annual and interim segment revenue, EBITDA and selected operating KPIs | KPI definitions and source coverage vary by business and period. |

### Analytical appendix — complete canonical registers

#### T4.1 — Source Register

| Source File Name | Document Type | Period Coverage | Currency | Unit | Perimeter | Accounting Basis | Evidence Quality Tier | Analytical Use | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| CZR_FY2025_10K.txt | Form 10-K; audited financial statements | FY2023–FY2025; balance sheets at 2024/2025 | USD | millions | Caesars Entertainment, Inc. and consolidated subsidiaries | US GAAP; audited | Tier 1 — Audited FS | Annual statements, notes, segment results, debt, leases and risk context [C1, C3, C4, C5] | Historical year-end figures; no 2026 post-period update in this source. |
| CZR_Q2_2026_10Q.txt | Form 10-Q; unaudited interim statements | Three and six months ended June 30, 2025/2026; balance sheets at June 30, 2026 and December 31, 2025 | USD | millions | Caesars Entertainment, Inc. and consolidated subsidiaries | US GAAP; unaudited interim | Tier 2b — Primary, unaudited | Current interim financials, debt, liquidity, segments, merger and subsequent-event disclosures [C2, C8, C10, C15, C17, C18] | No Q2 cash-flow statement; no later financial period. |
| CZR_Q2_2026_Earnings_Release.txt | Earnings release | Three and six months ended June 30, 2025/2026 | USD | millions | Caesars Entertainment, Inc. consolidated | Supplemental non-GAAP and GAAP results | Tier 2 — Issuer release | Cross-check and supplemental Q2 segment / Adjusted EBITDA presentation [C16] | Release is not audited and adds no later reporting period. |

#### T4.2 — Entity Period Key

| Entity Name | Entity Role | Fiscal Year End | Reporting Currency | Reporting Unit | Consolidation Perimeter | Accounting Basis | Available Periods |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Registrant / consolidated operating issuer; subsidiaries included in consolidated statements. Borrower and guarantor perimeter varies by debt instrument; no separate subsidiary perimeter modelled. | December 31 | USD | millions | Registrant and consolidated subsidiaries | US GAAP; FY audited, interim unaudited | FY2023–FY2025; Q2/H1 2025 and 2026; balance-sheet dates December 31, 2024/2025 and June 30, 2026 [C1, C2] |

**Subsequent Events — excluded from reporting-period values:** the Q2 filing states that mobile sports betting and iGaming launched in Alberta on July 13, 2026, after the June 30 balance-sheet date. No associated post-period financial value is included. [C15] The merger agreement was entered into May 27, 2026 and remained pending at the reporting date; it is not a completed transaction or a Q2 cash/debt adjustment. The filing reports $10 million transaction costs for Q2 and H1. [C21]

#### T4.3 — Normalization Register

| Description | Source | Type | Before | After | Rationale | Periods |
|---|---|---|---|---|---|---|
| Reporting basis | FY2025 10-K and Q2 2026 10-Q | Unit / perimeter alignment | Source tables in USD millions, consolidated US GAAP | USD millions; consolidated; US GAAP | No currency conversion or perimeter adjustment. Preserve audited FY and unaudited interim evidence tiers. | All reported periods |
| Adjusted EBITDA | FY2025 10-K, Q2 2026 10-Q and release | Definition retained; not normalized into GAAP earnings | Issuer non-GAAP Adjusted EBITDA | Retained as a separate issuer-defined performance measure; GAAP EBITDA shown as operating income plus D&A | Do not substitute non-GAAP EBITDA for GAAP earnings or cash flow. | FY2023–FY2025; Q2/H1 2025/2026 |
| Debt | FY2025 10-K and Q2 2026 10-Q | Canonical carrying-value basis | Face principal and debt-note book figures | Current portion plus balance-sheet long-term debt; financing obligations presented separately | Canonical debt is carrying value, not face value; financing obligations remain separately visible. | December 31, 2025; June 30, 2026 |

#### T4.4 — Income Statement

USD millions. Source-reported expenses are positive in expense rows; income, losses, benefits and calculated EBITDA use signed values as shown. Table-wide annual values are from the audited 10-K; Q2/H1 values are from the interim statements and segment/non-GAAP disclosures. [C3, C4, C16, C17, C18]

| Line Item | FY2025 | H1_2026 | Q2_2026 |
|---|---:|---:|---:|
| Net revenues | 11,486 | 5,863 | 2,993 |
| Casino revenue | 6,617 | 3,425 | 1,759 |
| Food and beverage revenue | 1,714 | 850 | 426 |
| Hotel revenue | 1,945 | 982 | 495 |
| Other revenue | 1,210 | 606 | 313 |
| Cost of goods sold | — | — | — |
| Gross profit | — | — | — |
| Casino operating expense | 3,602 | 1,857 | 955 |
| Food and beverage operating expense | 1,106 | 555 | 281 |
| Hotel operating expense | 615 | 319 | 163 |
| Other operating expense | 420 | 190 | 95 |
| General and administrative | 1,926 | 1,025 | 521 |
| Corporate expense | 322 | 182 | 94 |
| Impairment charges | 182 | — | — |
| Transaction and other costs, net | 38 | 20 | 16 |
| Total operating expenses | 9,628 | 4,850 | 2,480 |
| Operating income (EBIT) | 1,858 | 1,013 | 513 |
| Depreciation and amortization | 1,417 | 702 | 355 |
| EBITDA, calculated as EBIT plus D&A | 3,275 | 1,715 | 868 |
| Adjusted EBITDA, issuer-reported non-GAAP | 3,624 | 1,807 | 920 |
| Interest expense | 2,329 | 1,149 | 577 |
| Capitalized interest | (5) | (2) | (1) |
| Interest income | (20) | (5) | (3) |
| Interest expense, net | 2,304 | 1,142 | 573 |
| Loss on extinguishment of debt | 4 | — | — |
| Other income | 2 | 5 | 7 |
| Loss before income taxes | (448) | (124) | (53) |
| Income tax benefit / (provision), signed as statement result | 11 | 0 | 12 |
| Net income / (loss) | (437) | (124) | (41) |
| Net income attributable to noncontrolling interests | 65 | 36 | 21 |
| Net income / (loss) attributable to Caesars | (502) | (160) | (62) |
| Stock-based compensation expense | 95 | 47 | 23 |

#### T4.5 — Cash Flow Statement

USD millions. Cash-flow values are reported for FY or half-year unless otherwise stated. Q2 cash-flow values are not separately reported and remain null. CFO less PP&E purchases is a CP-1 calculation, not issuer-reported FCF. [C5, C6, C11, C12, C20, C21]

| Line Item | FY2025 | H1_2026 | Q2_2026 |
|---|---:|---:|---:|
| Net cash provided by operating activities (CFO/OCF) | 1,302 | 675 | — |
| Working-capital change, calculated from operating asset/liability changes | (201) | (71) | — |
| Operating cash flow before listed working-capital changes, calculated | 1,503 | 746 | — |
| Purchase of property and equipment | (805) | (335) | — |
| Acquisition of intangible assets | (4) | — | — |
| FCF proxy: CFO less PP&E purchases | 497 | 340 | — |
| Proceeds from sale of property/equipment/trademark/business | 218 | 20 | — |
| Cash paid for asset acquisitions | — | (98) | — |
| Net cash used in investing activities | (571) | (411) | — |
| Proceeds from long-term debt and revolving facilities | 1,580 | 885 | — |
| Repayments of long-term debt and revolving facilities | (1,969) | (983) | — |
| Net debt issuance / repayment | (389) | (98) | — |
| Financing obligation payments | (26) | (19) | — |
| Common stock repurchases | (229) | — | — |
| Distributions to noncontrolling interest owners | (102) | (41) | — |
| Net cash used in financing activities | (763) | (171) | — |
| Net increase / (decrease) in cash, cash equivalents and restricted cash | (32) | 93 | — |
| Cash taxes paid, net | (81) | (11) | — |
| Cash interest paid for debt | (813) | (368) | — |
| Cash interest paid for rent related to financing obligations | (1,349) | (686) | — |

#### T4.6 — Balance Sheet

USD millions. Canonical Total Debt is current portion plus long-term debt on the balance sheet. Lease financing obligations are a separate balance-sheet claim and are not silently included in Total Debt. [C7, C8, C9, C10]

| Line Item | FY2025_END | JUN30_2026 |
|---|---:|---:|
| Cash and cash equivalents | 887 | 965 |
| Restricted cash | 85 | 96 |
| Accounts receivable, net | 476 | 485 |
| Inventories | 43 | 49 |
| Prepayments and other current assets | 312 | 382 |
| Total current assets | 1,803 | 1,977 |
| Investments in unconsolidated affiliates | 133 | 124 |
| Property and equipment, net | 14,358 | 14,125 |
| Goodwill | 10,441 | 10,441 |
| Intangible assets other than goodwill | 3,985 | 3,959 |
| Deferred tax asset | 67 | 68 |
| Other long-term assets, net | 852 | 1,048 |
| Total assets | 31,639 | 31,742 |
| Accounts payable | 297 | 290 |
| Accrued interest | 224 | 222 |
| Accrued other liabilities | 1,618 | 1,696 |
| Current portion of long-term debt | 114 | 114 |
| Total current liabilities | 2,253 | 2,322 |
| Long-term financing obligations | 13,096 | 13,157 |
| Long-term debt | 11,670 | 11,585 |
| Total Debt, calculated as current plus long-term debt | 11,784 | 11,699 |
| Deferred tax liability | 58 | 57 |
| Other long-term liabilities | 876 | 1,069 |
| Total liabilities | 27,953 | 28,190 |
| Caesars stockholders’ equity | 3,504 | 3,375 |
| Noncontrolling interests | 182 | 177 |
| Total stockholders’ equity | 3,686 | 3,552 |
| Senior secured debt, instrument-level carrying values net of RCF deferred costs | 9,463 | 9,379 |
| Senior unsecured debt and other debt, calculated from debt note | 2,321 | 2,320 |
| Subordinated debt | — | — |

#### T4.8 — Constructed Period Register

| Metric Name | Derived Period Type | Full-Year Component | Current Stub | Prior-Year Stub | Derived Value | Calculation Status | Source Files | Limitations |
|---|---|---:|---:|---:|---:|---|---|---|
| Net revenue | LTM to June 30, 2026 | 11,486 | 5,863 | 5,701 | 11,648 | Calculated | FY2025 10-K; Q2 2026 10-Q [C3, C18] | FY2025 + H1 2026 − H1 2025. |
| Adjusted EBITDA | LTM to June 30, 2026 | 3,624 | 1,807 | 1,839 | 3,592 | Calculated | FY2025 10-K; Q2 2026 10-Q [C4, C16] | Issuer non-GAAP definition retained. |
| EBITDA, EBIT plus D&A | LTM to June 30, 2026 | 3,275 | 1,715 | 1,735 | 3,255 | Calculated | FY2025 10-K; Q2 2026 10-Q [C3, C18] | H1 comparative EBITDA calculated from operating income plus D&A. |
| Operating cash flow | LTM to June 30, 2026 | 1,302 | 675 | 680 | 1,297 | Calculated | FY2025 10-K; Q2 2026 10-Q [C5, C6] | H1 period components are directly reported. |
| PP&E purchases | LTM to June 30, 2026 | 805 | 335 | 453 | 687 | Calculated | FY2025 10-K; Q2 2026 10-Q [C20, C21] | Presented as positive investment spend here; cash flow statement reports outflows. |
| FCF proxy: CFO less PP&E purchases | LTM to June 30, 2026 | 497 | 340 | 227 | 610 | Calculated | FY2025 10-K; Q2 2026 10-Q [C5, C6, C20, C21] | Excludes other investing, interest, taxes, debt service and lease payments. |
| Net income attributable to Caesars | LTM to June 30, 2026 | (502) | (160) | (197) | (465) | Calculated | FY2025 10-K; Q2 2026 10-Q | FY + current H1 − comparative H1. |

#### T4.9 — Calculation Register

| Metric Name | Formula | Numerator Value | Numerator Source | Denominator Value | Denominator Source | Period | Currency | Unit | Calculated Value | Calculation Status | Evidence Quality Tier | Limitations |
|---|---|---:|---|---:|---|---|---|---|---:|---|---|---|
| Adjusted EBITDA margin | Adjusted EBITDA / revenue | 3,624 | FY2025 issuer Adjusted EBITDA [C4] | 11,486 | FY2025 revenue [C3] | FY2025 | USD | % | 31.55% | Calculated | Tier 1 | Non-GAAP numerator. |
| Adjusted EBITDA margin | Adjusted EBITDA / revenue | 1,807 | H1 2026 [C16] | 5,863 | H1 2026 [C18] | H1 2026 | USD | % | 30.82% | Calculated | Tier 2b | Unaudited interim. |
| Adjusted EBITDA margin | Adjusted EBITDA / revenue | 920 | Q2 2026 [C16] | 2,993 | Q2 2026 [C18] | Q2 2026 | USD | % | 30.74% | Calculated | Tier 2b | Unaudited interim. |
| Revenue growth | Current period / prior comparable period − 1 | 5,863 | H1 2026 [C18] | 5,701 | H1 2025 [C18] | H1 YoY | USD | % | 2.84% | Calculated | Tier 2b | Periods comparable; asset purchases affect comparability. |
| Adjusted EBITDA growth | Current period / prior comparable period − 1 | 1,807 | H1 2026 [C16] | 1,839 | H1 2025 [C16] | H1 YoY | USD | % | (1.74)% | Calculated | Tier 2b | Issuer non-GAAP definition. |
| Debt / Adjusted EBITDA | Balance-sheet carrying debt / LTM Adjusted EBITDA | 11,699 | June 30, 2026 carrying debt [C8] | 3,592 | LTM calculation [C4, C16] | LTM to June 30, 2026 | USD | x | 3.26x | Calculated | Tier 2b | Excludes financing obligations; lease claims remain material. |
| Net debt / Adjusted EBITDA | Carrying debt less cash / LTM Adjusted EBITDA | 10,734 | 11,699 debt less 965 cash [C8, C10] | 3,592 | LTM calculation [C4, C16] | LTM to June 30, 2026 | USD | x | 2.99x | Calculated | Tier 2b | Restricted cash excluded from cash offset. |
| Senior secured debt / Adjusted EBITDA | Secured carrying debt / LTM Adjusted EBITDA | 9,379 | Instrument totals net RCF deferred costs | 3,592 | LTM calculation [C4, C16] | LTM to June 30, 2026 | USD | x | 2.61x | Calculated | Tier 2b | Instrument book values; debt allocation detail in T4.18. |
| Adjusted EBITDA / net interest expense | Adjusted EBITDA / interest expense, net | 3,624 | FY2025 [C4] | 2,304 | FY2025 [C3] | FY2025 | USD | x | 1.57x | Calculated | Tier 1 | P&L interest basis; not cash interest coverage. |
| Adjusted EBITDA / net interest expense | Adjusted EBITDA / interest expense, net | 1,807 | H1 2026 [C16] | 1,142 | H1 2026 [C17] | H1 2026 | USD | x | 1.58x | Calculated | Tier 2b | P&L interest basis. |
| Adjusted EBITDA / net interest expense | Adjusted EBITDA / interest expense, net | 920 | Q2 2026 [C16] | 573 | Q2 2026 [C17] | Q2 2026 | USD | x | 1.60x | Calculated | Tier 2b | P&L interest basis. |
| Adjusted EBITDA / cash debt interest paid | Adjusted EBITDA / cash interest paid for debt | 3,624 | FY2025 [C4] | 813 | FY2025 cash debt interest [C11] | FY2025 | USD | x | 4.46x | Calculated | Tier 1 | Excludes cash interest paid for rent. |
| Adjusted EBITDA / cash debt interest paid | Adjusted EBITDA / cash interest paid for debt | 1,807 | H1 2026 [C16] | 368 | H1 2026 cash debt interest [C12] | H1 2026 | USD | x | 4.91x | Calculated | Tier 2b | Half-year comparison; excludes rent interest. |
| FCF proxy | CFO less PP&E purchases | 1,302 | FY2025 CFO [C5] | 805 | FY2025 PP&E purchases [C20] | FY2025 | USD | millions | 497 | Calculated | Tier 1 | Not issuer-reported FCF. |
| FCF proxy | CFO less PP&E purchases | 675 | H1 2026 CFO [C6] | 335 | H1 2026 PP&E purchases [C21] | H1 2026 | USD | millions | 340 | Calculated | Tier 2b | Not issuer-reported FCF. |
| Liquidity / carrying debt | Cash plus undrawn facilities / carrying debt | 2,928 | June 30 cash plus net available capacity [C10] | 11,699 | June 30 balance-sheet carrying debt [C8] | June 30, 2026 | USD | % | 25.03% | Calculated | Tier 2b | Includes disclosed available facilities; not a covenant-capacity measure. |
| Gross margin | Gross profit / revenue | — | Gross profit not separately disclosed | 11,486 | FY2025 revenue [C3] | FY2025 | USD | % | — | Not Calculable | Tier 1 | COGS/gross profit not separately presented. |

#### T4.10 — KPI Dashboard

| KPI Category | Metric Name | FY2025 | H1 2026 | Q2 2026 | Trend Direction | Analyst Note |
|---|---|---:|---:|---:|---|---|
| Scale | Net revenue, $m | 11,486 | 5,863 | 2,993 | H1 +2.8% YoY | Calculated growth against H1 2025. [C3, C18] |
| Earnings | Adjusted EBITDA, $m | 3,624 | 1,807 | 920 | H1 -1.7% YoY | Non-GAAP measure; definition retained in T4.11. [C4, C16] |
| Margin | Adjusted EBITDA margin | 31.55% | 30.82% | 30.74% | Lower | Calculated from issuer revenue and Adjusted EBITDA. [C3, C4, C16, C18] |
| Cash flow | Operating cash flow, $m | 1,302 | 675 | — | H1 slightly lower YoY | No discrete Q2 cash-flow statement. [C5, C6] |
| Cash flow | FCF proxy, $m | 497 | 340 | — | Not comparable as quarterly | CFO less PP&E purchases; not issuer FCF. [C5, C6, C20, C21] |
| Leverage | Carrying debt, $m | 11,784 | 11,699 | 11,699 | Lower at June 30 | Balance-sheet debt; excludes financing obligations. [C7, C8] |
| Leverage | LTM carrying debt / Adjusted EBITDA | — | 3.26x | 3.26x | Calculated | LTM denominator ends June 30, 2026. [C4, C8, C16] |
| Liquidity | Cash plus reported available capacity, $m | 2,833 | 2,928 | 2,928 | Higher at June 30 | Reported liquidity measure includes undrawn facility capacity. [C10] |
| Interest | Adjusted EBITDA / net interest expense | 1.57x | 1.58x | 1.60x | Slightly higher | P&L basis; cash-interest coverage is a different measure. [C3, C4, C16, C17] |
| Operating | Las Vegas hotel occupancy | 94.1% | — | — | FY YoY lower | H1 and Q2 not included in the annual-period KPI row. |
| Operating | Las Vegas table-games hold | 19.9% | 17.5% H1 | 16.6% | Lower | Hold variability affected Las Vegas results. |
| Operating | Caesars Digital iGaming handle, $m | 19,025 | 10,205 | 4,831 | H1 +11.0% YoY | Handle is volume, not revenue; hold affects retained win. |

#### T4.11 — Definition Conflict Register

| Metric Name | Canonical Definition | Issuer-Reported Definition | Source of Conflict | Periods Affected | Materiality | Downstream Modules Affected | Resolution / Recommendation |
|---|---|---|---|---|---|---|---|
| Total Debt / Net Debt | Total Debt is current plus long-term balance-sheet debt carrying value, net of issuance costs; Net Debt subtracts cash and equivalents, excluding restricted cash. | Debt tables also present face principal and book value; balance-sheet debt further reflects current portion and deferred facility finance costs. Long-term financing obligations are separately classified. At June 30, face principal is $11,807m versus carrying debt $11,699m; FY2025 face principal $11,905m versus carrying debt $11,784m. [C7, C8, C9] | FY2025 10-K and Q2 2026 10-Q balance sheet and debt note | FY2025; June 30, 2026 | Material: affects leverage and debt reconciliation. | CP-1B, CP-2, CP-2A, CP-2D, CP-3, CP-3C, CP-4, CP-MODEL | Use balance-sheet carrying value for canonical debt; show principal and financing obligations separately. Do not silently substitute face principal. |
| EBITDA / Adjusted EBITDA | GAAP EBITDA is operating income plus D&A; Adjusted EBITDA is a separately identified issuer non-GAAP measure. | Issuer Adjusted EBITDA adds specified interest, tax, noncontrolling interests, depreciation, stock compensation and other items; FY2025 reported Adjusted EBITDA is $3,624m versus calculated GAAP EBITDA of $3,275m. [C4] | FY2025 10-K and Q2 2026 10-Q non-GAAP reconciliation | FY2025; H1/Q2 2025/2026 | Material: $349m FY2025 gap between reported Adjusted EBITDA and calculated GAAP EBITDA. | CP-1B, CP-2, CP-2D, CP-3C, CP-4, CP-MODEL | Retain both measures and definitions. Use Adjusted EBITDA only when explicitly labelled; do not imply it is cash flow. |
| Interest coverage | P&L coverage uses Adjusted EBITDA / net P&L interest expense; cash basis is separately labelled as cash debt interest paid. | FY2025 net interest expense is $2,304m while cash interest paid for debt is $813m; an additional $1,349m cash interest payment relates to financing-obligation rent. H1 2026 corresponding cash interest values are $368m debt and $686m rent. [C11, C12] | Annual and interim statements of operations and cash-flow supplemental disclosures | FY2025; H1 2026 | Material: different denominators materially change apparent coverage. | CP-1B, CP-2, CP-2A, CP-2D, CP-4 | Keep the P&L ratio primary and label cash-debt-interest ratio as an alternative; rent interest is not omitted from the credit narrative. |
| FCF | No issuer-reported canonical FCF is established here. CP-1 proxy equals CFO less PP&E purchases only. | Issuer reports CFO and cash investment separately; Adjusted EBITDA explicitly excludes capital expenditure, interest, taxes, principal payments and lease payments. | FY2025 10-K and Q2 2026 10-Q | FY2025; H1 2026 | Material: proxy omits other investing and financing requirements. | CP-1B, CP-2, CP-2A, CP-2D, CP-MODEL | Use only the labelled FCF proxy; obtain detailed maintenance/growth capex and cash obligations before a full FCF build. |
| Multi-figure 2025 redemption of CEI Senior Notes due 2027 | Distinguish income-statement extinguishment expense, operating cash-flow non-cash add-back and financing cash repayment. | P&L loss on extinguishment $4m; operating cash-flow reconciliation add-back $4m; financing repayments include $546m principal redemption. These figures represent different statement roles for one debt event, not conflicting measures of the same amount. | FY2025 10-K income statement, cash-flow statement and Note 9 debt disclosure | FY2025 | Material to transaction/cash-flow interpretation; not a debt-balance discrepancy. | CP-1B, CP-2, CP-2A, CP-3C, CP-4 | Preserve all three roles; do not present one as the full event amount. |

#### T4.12 — Gaps & Warnings

| Gap Description | Affected Line Item or Metric | Affected Period(s) | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|---|
| No separate COGS or gross-profit disclosure | COGS, gross profit and gross margin | All | Gross-margin KPIs are not calculable from the provided filings. | MATERIAL | Do not infer; use disclosed operating expenses and segment EBITDA. |
| No discrete Q2 cash-flow statement | CFO, working capital, capex, FCF, cash interest and cash taxes | Q2 2026 | Quarterly cash conversion and cash-based coverage cannot be calculated. | MATERIAL | Obtain Q1 and Q2 cash-flow detail or later filing with comparable periods. |
| No Q1 2026/Q1 2025 financial statements in the delivered source set | Discrete-quarter history | 2025–2026 | Prevents four-quarter complete model schedule and complete quarterly comparison. | MATERIAL | Obtain the missing quarterly reports and build periods only from sourced values. |
| No maintenance/growth capex split | Capex by type | FY2025, H1/Q2 2026 | Maintenance FCF and growth investment cannot be separated. | MATERIAL | Keep total PP&E purchases only; request issuer capex classification. |
| Debt principal differs from carrying value | Debt, leverage and facility carrying amounts | FY2025 and June 30, 2026 | Alternative debt basis changes leverage and debt reconciliation. | MATERIAL | Apply T4.11 definition; use carrying values for canonical ratios. |
| Financing obligations and lease payments are substantial but separate from canonical debt | Lease financing obligations, rent and fixed-charge coverage | FY2025 and June 30, 2026 | Debt-only leverage understates fixed claims; total lease cash payments are not fully presented as one figure. | MATERIAL | Carry debt and lease obligations separately; obtain lease cash-flow schedule for fixed-charge analysis. |
| Customer deposits and deferred revenue form operational float | Contract liabilities / liquidity | FY2025 year-end and June 30, 2026 | Potential fulfillment or withdrawal converts float to cash use; refund timing and split by maturity are not fully quantified. | MATERIAL | Monitor balances and obtain detailed contract-liability/maturity data. |
| Covenant compliance is reported but current headroom is not provided | Leverage and fixed-charge covenant capacity | June 30, 2026 | No covenant capacity or distance-to-default calculation can be made. | MATERIAL | Obtain current covenant definitions, calculations and complete credit agreement. |
| No financial reporting after June 30, 2026 | Current liquidity, debt and performance | July 1–October 2, 2026 | Current-date conclusions cannot be verified; Alberta launch is operational only and excluded from Q2 values. | MATERIAL | Obtain subsequent filings and current debt/cash schedule. |
| Interest expense and cash interest paid differ in basis and scope | Interest coverage | FY2025 and H1 2026 | Cash debt coverage is not comparable to P&L-interest coverage; rent interest is separate. | MATERIAL | Retain the distinct measures and disclose denominator used. |
| Model quarter and segment coverage incomplete | CP-MODEL historical schedule | 2025–2026 | Four complete quarters and consistent segment/debt reconciliations are unavailable. | MATERIAL | Supply all missing quarterly filings before using historical schedule for forecasts. |
| T4.18 facility commitment is null for named facilities without a disclosed facility-specific commitment | T4.18 rows: CEI Term Loan A, Term Loan B, Term Loan B-1, senior notes, Special Improvement District Bonds and other debt; column `commitment` | FY2025_END and JUN30_2026 | Commitment schedule is incomplete at instrument level; null does not mean zero. | MATERIAL | Obtain the facility-level commitments or retain null and do not treat as zero. |
| T4.19 FY-to-quarter reconciliation has null reported value, calculated value, difference and tolerance because a complete FY2025 quarterly series is absent | T4.19 `reported_value`, `calculated_value`, `difference`, `tolerance` | FY2025 | Quarterly aggregation cannot be verified. | MATERIAL | Obtain all discrete FY2025 quarters before reconciliation. |

#### T4.13 — Downstream Readiness

| Downstream Module | Readiness Status | Gaps or Limitations | Recommended Actions |
|---|---|---|---|
| CP-1B | Ready with Limitations | No post-June financials; GAAP/non-GAAP EBITDA and debt-basis distinctions remain. | Use T4 definitions and carry current-period gap. |
| CP-1C | Ready with Limitations | No peer filings or market evidence are included in this CP-1 evidence set. | Use its permitted evidence process; do not infer peer data here. |
| CP-2 | Ready with Limitations | Q2 discrete CFS and maintenance/growth capex absent; FCF is only a proxy. | Do not treat EBITDA or the proxy as free cash available for debt service. |
| CP-2A | Ready with Limitations | No discrete Q2 cash flow and no post-June cash position. | Use annual/H1 data and state timing limitations. |
| CP-2D | Ready with Limitations | Lease obligations and rent must be analysed separately from debt; no current covenant headroom. | Carry fixed-charge and covenant gaps explicitly. |
| CP-3 | Ready with Limitations | Instrument-level carrying values available, but complete current security package and market evidence are not part of CP-1 sources. | Preserve carrying/principal split and refer legal/market gaps to relevant sources. |
| CP-3C | Ready with Limitations | Debt-service estimates exist in filings, but no post-June update or complete covenant headroom. | Use dated schedule and request current financing information. |
| CP-4 | Ready with Limitations | EBITDA definition conflict and full current credit agreement not retained in this CP-1 source set. | Use reported definitions; do not infer covenant baskets or capacity. |
| CP-4A | Ready with Limitations | Current covenant calculation inputs and headroom are not supplied. | Mark capacity not calculable until complete definitions and calculations are available. |
| CP-5 | Ready with Limitations | Source pack is limited to three financial documents in this module’s evidence. | Preserve source locators and the upstream source-limited status. |
| CP-5A | Ready with Limitations | Later-period, complete legal and complete market evidence remain unavailable. | Audit the gaps and evidence lineage before downstream clearance. |
| CP-MODEL | blocked | Fewer than four complete discrete quarters; Q2 cash-flow metrics unavailable discretely; full segment/debt history not supplied. | Do not use for forecast workbook until full period and reconciliation requirements are satisfied. |

#### T4.14 — Model Period Register

<!-- table-id: cp1.model_period_register -->

| period_id | fiscal_year | fiscal_quarter | period_type | start_date | end_date | day_count | audit_status | currency | unit | accounting_basis | entity_perimeter | source_id | source_locator | component_period_ids |
|---|---:|---:|---|---|---|---:|---|---|---|---|---|---|---|---|
| FY2025 | 2025 | null | FY | 2025-01-01 | 2025-12-31 | 365 | AUDITED | USD | MILLIONS | US GAAP | Consolidated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 19, 23, 31 [C1, C3, C4, C5] | null |
| H1_2026 | 2026 | null | YTD | 2026-01-01 | 2026-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 2–5, 15–16 [C2, C6, C16, C18] | null |
| Q2_2026 | 2026 | 2 | QUARTER | 2026-04-01 | 2026-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 2–3, 15–16 [C2, C16, C18] | null |
| FY2025_END | 2025 | null | PERIOD_END | 2025-12-31 | 2025-12-31 | 1 | AUDITED | USD | MILLIONS | US GAAP | Consolidated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 29 [C7] | null |
| JUN30_2026 | 2026 | null | PERIOD_END | 2026-06-30 | 2026-06-30 | 1 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 2, 9 [C8, C9] | null |

#### T4.15 — Model Account Register

<!-- table-id: cp1.model_account_register -->

| metric_id | period_id | value | sign_convention | value_class | calculation_status | source_id | source_locator | conflict_refs | limitation_refs |
|---|---|---:|---|---|---|---|---|---|---|
| revenue | FY2025 | 11486 | Positive | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 19 [C3] | null | null |
| revenue | H1_2026 | 5863 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 [C18] | null | null |
| revenue | Q2_2026 | 2993 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 [C18] | null | null |
| ebit | FY2025 | 1858 | Positive | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 19–20 | null | null |
| ebit | H1_2026 | 1013 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 3 | null | null |
| ebit | Q2_2026 | 513 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 3 | null | null |
| depreciation_amortization | FY2025 | 1417 | Positive | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 20 | null | null |
| depreciation_amortization | H1_2026 | 702 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 3 | null | null |
| depreciation_amortization | Q2_2026 | 355 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 3 | null | null |
| ebitda | FY2025 | 3275 | Positive | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | EBIT + D&A; 10-K pp. 19–20 | null | null |
| ebitda | H1_2026 | 1715 | Positive | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | EBIT + D&A; 10-Q pp. 3, 8 | null | null |
| ebitda | Q2_2026 | 868 | Positive | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | EBIT + D&A; 10-Q pp. 3, 8 | null | null |
| adjusted_ebitda | FY2025 | 3624 | Positive | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 23 [C4] | CF-2 | null |
| adjusted_ebitda | H1_2026 | 1807 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 [C16] | CF-2 | null |
| adjusted_ebitda | Q2_2026 | 920 | Positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 [C16] | CF-2 | null |
| cash_interest_paid | FY2025 | -813 | Outflow negative | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 32 [C11] | CF-3 | null |
| cash_interest_paid | H1_2026 | -368 | Outflow negative | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 5 [C12] | CF-3 | null |
| cash_taxes_paid | FY2025 | -81 | Outflow negative | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 32 | null | null |
| cash_taxes_paid | H1_2026 | -11 | Outflow negative | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 5 | null | null |
| cfo_ncfo | FY2025 | 1302 | Inflow positive | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 31 [C5] | null | null |
| cfo_ncfo | H1_2026 | 675 | Inflow positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 4 [C6] | null | null |
| working_capital_change | FY2025 | -201 | Outflow negative | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Sum of reported operating asset/liability changes, 10-K p. 31 | null | null |
| working_capital_change | H1_2026 | -71 | Outflow negative | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Sum of reported operating asset/liability changes, 10-Q p. 4 | null | null |
| capex_and_intangible_investment | FY2025 | -809 | Outflow negative | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | PP&E purchases plus intangible acquisition, 10-K p. 31 [C20] | CF-4 | null |
| capex_and_intangible_investment | H1_2026 | -335 | Outflow negative | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | PP&E purchases; 10-Q p. 4 [C21] | CF-4 | null |
| acquisitions_disposals | H1_2026 | -78 | Net outflow negative | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Asset acquisition less sale proceeds; 10-Q p. 4 | null | null |
| net_debt_issue_repay | FY2025 | -389 | Net outflow negative | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Proceeds less repayments; 10-K p. 31 | null | null |
| net_debt_issue_repay | H1_2026 | -98 | Net outflow negative | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Proceeds less repayments; 10-Q p. 4 | null | null |
| net_equity_issue_repay | FY2025 | -229 | Outflow negative | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Share repurchase cash flow, 10-K p. 31 | null | null |
| net_cash_change | FY2025 | -32 | Outflow negative | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 31 | null | null |
| net_cash_change | H1_2026 | 93 | Inflow positive | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 4 | null | null |
| cash_and_equivalents | FY2025_END | 887 | Positive balance | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 29 | null | null |
| cash_and_equivalents | JUN30_2026 | 965 | Positive balance | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 2 | null | null |
| rcf_commitment | FY2025_END | 2250 | Positive commitment | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 24 | null | null |
| rcf_commitment | JUN30_2026 | 2250 | Positive commitment | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 10 | null | null |
| rcf_drawn | FY2025_END | 160 | Positive drawn | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 | null | null |
| rcf_drawn | JUN30_2026 | 120 | Positive drawn | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 [C24] | null | null |
| senior_secured_debt | FY2025_END | 9463 | Positive balance | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Secured instrument book values less RCF deferred costs, 10-K p. 40 | CF-1 | null |
| senior_secured_debt | JUN30_2026 | 9379 | Positive balance | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Secured instrument book values less RCF deferred costs, 10-Q p. 9 | CF-1 | null |
| unsecured_debt | FY2025_END | 2321 | Positive balance | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Unsecured notes, bonds and other debt, 10-K p. 40 | CF-1 | null |
| unsecured_debt | JUN30_2026 | 2320 | Positive balance | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Unsecured notes, bonds and other debt, 10-Q p. 9 | CF-1 | null |
| total_debt | FY2025_END | 11784 | Positive carrying value | CALCULATED | Calculated | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Current portion plus long-term debt, 10-K p. 29 [C7] | CF-1 | null |
| total_debt | JUN30_2026 | 11699 | Positive carrying value | CALCULATED | Calculated | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Current portion plus long-term debt, 10-Q p. 2 [C8] | CF-1 | null |
| net_accounts_receivable | FY2025_END | 476 | Positive balance | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 29 | null | null |
| net_accounts_receivable | JUN30_2026 | 485 | Positive balance | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 2 | null | null |
| inventory | FY2025_END | 43 | Positive balance | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 29 | null | null |
| inventory | JUN30_2026 | 49 | Positive balance | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 2 | null | null |
| accounts_payable | FY2025_END | 297 | Positive balance | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 29 | null | null |
| accounts_payable | JUN30_2026 | 290 | Positive balance | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 2 | null | null |
| pretax_income | FY2025 | -448 | Negative loss | SOURCE | Verified | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 30 | null | null |
| pretax_income | H1_2026 | -124 | Negative loss | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 3 | null | null |
| pretax_income | Q2_2026 | -53 | Negative loss | SOURCE | Verified | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 3 | null | null |

#### T4.16 — Segment Revenue Schedule

<!-- table-id: cp1.segment_revenue_schedule -->

| segment_id | segment_name | segment_type | display_priority | period_id | revenue | status | source_id | source_locator |
|---|---|---|---:|---|---:|---|---|---|
| seg_las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | FY2025 | 4049 | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 19 [C22] |
| seg_regional | Regional | OPERATING_SEGMENT | 2 | FY2025 | 5756 | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 19 [C22] |
| seg_caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | FY2025 | 1408 | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 19 |
| seg_managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | FY2025 | 279 | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 19 |
| seg_corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2025 | -6 | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 19 |
| seg_las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | H1_2026 | 2020 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_regional | Regional | OPERATING_SEGMENT | 2 | H1_2026 | 3000 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2026 | 725 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2026 | 123 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2026 | -5 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2026 | 1017 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 [C23] |
| seg_regional | Regional | OPERATING_SEGMENT | 2 | Q2_2026 | 1570 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2026 | 351 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 [C27] |
| seg_managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2026 | 57 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |
| seg_corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2026 | -2 | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 18 |

#### cp1.cp_model_segment_allocation — CP-MODEL Segment Allocation

<!-- table-id: cp1.cp_model_segment_allocation -->

| slot_id | slot_label | component_segment_ids |
|---|---|---|
| DIVISION_1 | Las Vegas driver | seg_las_vegas |
| DIVISION_2 | Regional and managed/branded driver | seg_regional, seg_managed_branded |
| DIVISION_3 | Digital driver | seg_caesars_digital |

Allocation is a provisional forecast-slot mapping, not an issuer segment reclassification. Corporate and Other is an elimination/corporate row and is not assigned a division-growth driver. CP-MODEL remains blocked by insufficient quarter coverage.

#### cp1.operating_kpi_schedule — Operating KPI Schedule

<!-- table-id: cp1.operating_kpi_schedule -->

| kpi_id | kpi_label | business_unit | kpi_category | display_priority | period_id | value | unit | value_type | status | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|---|
| lv_table_drop | Table games drop | Las Vegas | Gaming volume | 1 | FY2025 | 2880 | USD millions | PERIOD_FLOW | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| lv_table_drop | Table games drop | Las Vegas | Gaming volume | 1 | H1_2026 | 1425 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_table_drop | Table games drop | Las Vegas | Gaming volume | 1 | Q2_2026 | 706 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_table_hold | Table games hold | Las Vegas | Hold rate | 2 | FY2025 | 19.9 | % | RATE | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| lv_table_hold | Table games hold | Las Vegas | Hold rate | 2 | H1_2026 | 17.5 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_table_hold | Table games hold | Las Vegas | Hold rate | 2 | Q2_2026 | 16.6 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_slot_handle | Slot handle | Las Vegas | Gaming volume | 3 | FY2025 | 10427 | USD millions | PERIOD_FLOW | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| lv_slot_handle | Slot handle | Las Vegas | Gaming volume | 3 | H1_2026 | 5275 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_slot_handle | Slot handle | Las Vegas | Gaming volume | 3 | Q2_2026 | 2674 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_occupancy | Hotel occupancy | Las Vegas | Hotel operating rate | 4 | FY2025 | 94.1 | % | RATE | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| lv_occupancy | Hotel occupancy | Las Vegas | Hotel operating rate | 4 | H1_2026 | 95.4 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| lv_occupancy | Hotel occupancy | Las Vegas | Hotel operating rate | 4 | Q2_2026 | 95.5 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| regional_table_hold | Table games hold | Regional | Hold rate | 5 | FY2025 | 20.7 | % | RATE | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| regional_table_hold | Table games hold | Regional | Hold rate | 5 | H1_2026 | 21.7 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| regional_table_hold | Table games hold | Regional | Hold rate | 5 | Q2_2026 | 22.3 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| digital_sports_handle | Sports betting handle | Caesars Digital | Digital gaming volume | 6 | FY2025 | 11496 | USD millions | PERIOD_FLOW | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| digital_sports_handle | Sports betting handle | Caesars Digital | Digital gaming volume | 6 | H1_2026 | 5598 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| digital_sports_handle | Sports betting handle | Caesars Digital | Digital gaming volume | 6 | Q2_2026 | 2565 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| digital_sports_hold | Sports betting hold | Caesars Digital | Hold rate | 7 | FY2025 | 8.1 | % | RATE | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| digital_sports_hold | Sports betting hold | Caesars Digital | Hold rate | 7 | H1_2026 | 8.4 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| digital_sports_hold | Sports betting hold | Caesars Digital | Hold rate | 7 | Q2_2026 | 8.4 | % | RATE | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| digital_igaming_handle | iGaming handle | Caesars Digital | Digital gaming volume | 8 | FY2025 | 19025 | USD millions | PERIOD_FLOW | Reported | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 21 |
| digital_igaming_handle | iGaming handle | Caesars Digital | Digital gaming volume | 8 | H1_2026 | 10205 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |
| digital_igaming_handle | iGaming handle | Caesars Digital | Digital gaming volume | 8 | Q2_2026 | 4831 | USD millions | PERIOD_FLOW | Reported | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 20 |

#### T4.17 — Adjusted EBITDA Bridge

<!-- table-id: cp1.adjusted_ebitda_bridge -->

| addback_id | addback_label | addback_classification | realization_status | display_priority | period_id | value | status | source_definition | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|
| bridge_nci | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | FY2025 | 65 | Reported bridge item | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 [C4] |
| bridge_tax | Benefit / provision for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | FY2025 | -11 | Reported bridge item | Signed as issuer reconciliation adjustment | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_other_income | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | FY2025 | -2 | Reported bridge item | Issuer reconciliation | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_debt_extinguishment | Loss on extinguishment of debt | OTHER_EXPLICIT | NOT_STATED | 4 | FY2025 | 4 | Reported bridge item | Issuer reconciliation; $4m P&L amount, not principal repaid | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_interest | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 5 | FY2025 | 2304 | Reported bridge item | Issuer reconciliation | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_impairment | Impairment charges | OTHER_EXPLICIT | NOT_STATED | 6 | FY2025 | 182 | Reported bridge item | Issuer reconciliation | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_da | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 7 | FY2025 | 1417 | Reported bridge item | Issuer reconciliation | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_transaction | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | FY2025 | 72 | Reported bridge item | Issuer non-GAAP reconciliation definition | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_sbc | Stock-based compensation expense | SBC | NOT_STATED | 9 | FY2025 | 95 | Reported bridge item | Issuer reconciliation | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 22–23 |
| bridge_nci | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | H1_2026 | 36 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 [C16] |
| bridge_tax | Benefit / provision for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | H1_2026 | 0 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_other_income | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | H1_2026 | -5 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_interest | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 5 | H1_2026 | 1142 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_da | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 7 | H1_2026 | 702 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_transaction | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | H1_2026 | 45 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_sbc | Stock-based compensation expense | SBC | NOT_STATED | 9 | H1_2026 | 47 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_nci | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | Q2_2026 | 21 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 [C16] |
| bridge_tax | Benefit / provision for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | Q2_2026 | -12 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_other_income | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | Q2_2026 | -7 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_interest | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 5 | Q2_2026 | 573 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_da | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 7 | Q2_2026 | 355 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_transaction | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | Q2_2026 | 29 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |
| bridge_sbc | Stock-based compensation expense | SBC | NOT_STATED | 9 | Q2_2026 | 23 | Reported bridge item | Issuer reconciliation | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 16 |

#### T4.18 — Debt Facility Register

<!-- table-id: cp1.debt_facility_register -->

| facility_id | facility_name | period_id | facility_type | carrying_value | principal | drawn_amount | commitment | secured_status | seniority | currency | margin_or_coupon | maturity_date | lease_classification | source_id | source_locator |
|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|
| cei_rcf | CEI Revolving Credit Facility | FY2025_END | Revolving credit | 152 | 160 | 160 | 2250 | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2028-01-31 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 24, 40; carrying value net of $8m deferred facility costs [C7] |
| cei_term_a | CEI Term Loan A | FY2025_END | Term loan | 636 | 637 | 637 | null | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2028-01-31 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| cva_term | CVA Delayed Draw Term Loan | FY2025_END | Term loan | 381 | 386 | 386 | 400 | SECURED | Senior secured | USD | Variable; SOFR plus margin | 2029-04-26 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 25, 40 |
| cva_rcf | CVA Revolving Credit Facility | FY2025_END | Revolving credit | 0 | 0 | 0 | 25 | SECURED | Senior secured | USD | Variable; SOFR plus margin | 2029-04-26 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 25, 40; no outstanding amount reported |
| cei_term_b | CEI Term Loan B | FY2025_END | Term loan | 2002 | 2031 | 2031 | null | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2030-02-06 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| cei_term_b1 | CEI Term Loan B-1 | FY2025_END | Term loan | 2820 | 2849 | 2849 | null | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2031-02-06 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 24–25, 40 |
| cei_secured_2030 | CEI Senior Secured Notes due 2030 | FY2025_END | Senior notes | 1986 | 2000 | 2000 | null | SECURED | Senior secured | USD | 7.00% | 2030-02-15 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| cei_secured_2032 | CEI Senior Secured Notes due 2032 | FY2025_END | Senior notes | 1486 | 1500 | 1500 | null | SECURED | Senior secured | USD | 6.50% | 2032-02-15 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| cei_unsecured_2029 | CEI Senior Notes due 2029 | FY2025_END | Senior notes | 1192 | 1200 | 1200 | null | UNSECURED | Senior unsecured | USD | 4.625% | 2029-10-15 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| cei_unsecured_2032 | CEI Senior Notes due 2032 | FY2025_END | Senior notes | 1087 | 1100 | 1100 | null | UNSECURED | Senior unsecured | USD | 6.00% | 2032-10-15 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| sid_bonds | Special Improvement District Bonds | FY2025_END | Improvement district bonds | 40 | 40 | 40 | null | NOT_STATED | Not stated | USD | 4.30% | 2037 | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| other_debt | Long-term notes and other payables | FY2025_END | Other debt | 2 | 2 | 2 | null | NOT_STATED | Not stated | USD | Not stated | Not stated | NOT_APPLICABLE | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 40 |
| cei_rcf | CEI Revolving Credit Facility | JUN30_2026 | Revolving credit | 114 | 120 | 120 | 2250 | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2028-01-31 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 9–10; carrying value net of $6m deferred facility costs [C24] |
| cei_term_a | CEI Term Loan A | JUN30_2026 | Term loan | 618 | 619 | 619 | null | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2028-01-31 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| cva_term | CVA Delayed Draw Term Loan | JUN30_2026 | Term loan | 372 | 376 | 376 | 400 | SECURED | Senior secured | USD | Variable; SOFR plus margin | 2029-04-26 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 9–10 [C25] |
| cva_rcf | CVA Revolving Credit Facility | JUN30_2026 | Revolving credit | 0 | 0 | 0 | 25 | SECURED | Senior secured | USD | Variable; SOFR plus margin | 2029-04-26 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 9–10; no amount outstanding |
| cei_term_b | CEI Term Loan B | JUN30_2026 | Term loan | 1993 | 2018 | 2018 | null | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2030-02-06 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| cei_term_b1 | CEI Term Loan B-1 | JUN30_2026 | Term loan | 2808 | 2835 | 2835 | null | SECURED | Senior secured | USD | Variable; SOFR/base rate plus margin | 2031-02-06 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| cei_secured_2030 | CEI Senior Secured Notes due 2030 | JUN30_2026 | Senior notes | 1987 | 2000 | 2000 | null | SECURED | Senior secured | USD | 7.00% | 2030-02-15 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| cei_secured_2032 | CEI Senior Secured Notes due 2032 | JUN30_2026 | Senior notes | 1487 | 1500 | 1500 | null | SECURED | Senior secured | USD | 6.50% | 2032-02-15 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| cei_unsecured_2029 | CEI Senior Notes due 2029 | JUN30_2026 | Senior notes | 1193 | 1200 | 1200 | null | UNSECURED | Senior unsecured | USD | 4.625% | 2029-10-15 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| cei_unsecured_2032 | CEI Senior Notes due 2032 | JUN30_2026 | Senior notes | 1088 | 1100 | 1100 | null | UNSECURED | Senior unsecured | USD | 6.00% | 2032-10-15 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| sid_bonds | Special Improvement District Bonds | JUN30_2026 | Improvement district bonds | 38 | 38 | 38 | null | NOT_STATED | Not stated | USD | 4.30% | 2037 | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |
| other_debt | Long-term notes and other payables | JUN30_2026 | Other debt | 1 | 1 | 1 | null | NOT_STATED | Not stated | USD | Not stated | Not stated | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q p. 9 |

Debt-register carrying amounts net the separately disclosed deferred financing costs associated with the RCF from that facility; other facility balances use the debt table book values. The aggregate reconciles to balance-sheet current plus long-term debt. Facility commitment fields are null where no commitment amount is disclosed for that named facility; these are not zero commitments.

#### T4.19 — Model Reconciliation Register

<!-- table-id: cp1.model_reconciliation_register -->

| check_id | period_id | check_type | reported_value | calculated_value | difference | tolerance | status | explanation | source_refs |
|---|---|---|---:|---:|---:|---:|---|---|---|
| revenue_segments_fy25 | FY2025 | Segment revenue to consolidated revenue | 11486 | 11486 | 0 | 0 | PASS | Segment revenue including Corporate and Other elimination sums to consolidated net revenue. | 10-K p. 19 [C3, C22] |
| revenue_segments_h1 | H1_2026 | Segment revenue to consolidated revenue | 5863 | 5863 | 0 | 0 | PASS | Segment revenue including Corporate and Other elimination sums to consolidated net revenue. | 10-Q pp. 15, 18 [C18, C23] |
| revenue_segments_q2 | Q2_2026 | Segment revenue to consolidated revenue | 2993 | 2993 | 0 | 0 | PASS | Segment revenue including Corporate and Other elimination sums to consolidated net revenue. | 10-Q pp. 15, 18 [C18, C23] |
| adj_ebitda_segments_fy25 | FY2025 | Segment Adjusted EBITDA to consolidated | 3624 | 3624 | 0 | 0 | PASS | Segment values reconcile to issuer total. | 10-K pp. 19, 23 [C4] |
| adj_ebitda_segments_q2 | Q2_2026 | Segment Adjusted EBITDA to consolidated | 920 | 920 | 0 | 0 | PASS | Segment values reconcile to issuer total. | 10-Q pp. 15–16 [C16] |
| adj_ebitda_bridge_fy25 | FY2025 | Adjusted EBITDA bridge | 3624 | 3624 | 0 | 0 | PASS | Net income attributable to Caesars plus disclosed reconciliation items. | 10-K pp. 22–23 [C4] |
| adj_ebitda_bridge_h1 | H1_2026 | Adjusted EBITDA bridge | 1807 | 1807 | 0 | 0 | PASS | Reconciliation uses displayed H1 items. | 10-Q p. 16 [C16] |
| adj_ebitda_bridge_q2 | Q2_2026 | Adjusted EBITDA bridge | 920 | 920 | 0 | 0 | PASS | Reconciliation uses displayed Q2 items. | 10-Q p. 16 [C16] |
| cfo_identity_fy25 | FY2025 | CFO plus investing plus financing to net cash change | -32 | -32 | 0 | 0 | PASS | 1302 − 571 − 763 = -32. | 10-K p. 31 [C5] |
| cfo_identity_h1 | H1_2026 | CFO plus investing plus financing to net cash change | 93 | 93 | 0 | 0 | PASS | 675 − 411 − 171 = 93. | 10-Q p. 4 [C6] |
| debt_balance_fy25 | FY2025_END | Balance-sheet carrying debt | 11784 | 11784 | 0 | 0 | PASS | Current portion 114 plus long-term debt 11670. | 10-K p. 29 [C7] |
| debt_balance_jun26 | JUN30_2026 | Balance-sheet carrying debt | 11699 | 11699 | 0 | 0 | PASS | Current portion 114 plus long-term debt 11585. | 10-Q p. 2 [C8] |
| debt_note_to_bs_fy25 | FY2025_END | Debt-note carrying schedule to balance sheet | 11784 | 11784 | 0 | 0 | PASS | Debt-note book total 11792 less $8m deferred RCF finance costs. | 10-K p. 40 |
| debt_note_to_bs_jun26 | JUN30_2026 | Debt-note carrying schedule to balance sheet | 11699 | 11699 | 0 | 0 | PASS | Debt-note book total 11705 less $6m deferred RCF finance costs. | 10-Q p. 9 [C9] |
| reported_fy_quarter_sum | FY2025 | FY to quarterly sum | null | null | null | null | WARN | A complete FY2025 discrete quarterly series is not present in the delivered evidence; no forced reconciliation. | 10-K and Q2 10-Q; Q1 detail not supplied |

#### cp1.downstream_readiness — CP-MODEL Readiness

<!-- table-id: cp1.downstream_readiness -->

| downstream_module | status | missing_metric_ids | conflict_refs | explanation |
|---|---|---|---|---|
| CP-MODEL | blocked | discrete_quarters; quarterly_cash_flow; four_quarter_segment_schedule; four_quarter_debt_schedule | CF-1; CF-2; CF-3; CF-4 | Fewer than four complete discrete quarters are available; Q2 cash flow is not reported discretely, so the required quarter and reconciliation gates are not satisfied. |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| FY2025 net revenue | [C3] | Caesars FY2025 Form 10-K | 29 |
| FY2025 issuer Adjusted EBITDA | [C4] | Caesars FY2025 Form 10-K | 23 |
| FY2025 and H1 2026 operating cash flow | [C5, C6] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 31; 4 |
| Balance-sheet debt at FY2025 and June 30, 2026 | [C7, C8] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 29; 2 |
| Face principal and debt-note book values | [C9] | Caesars Q2 2026 Form 10-Q | 9 |
| Q2 liquidity and facility capacity | [C10] | Caesars Q2 2026 Form 10-Q | 22 |
| FY/H1 cash debt interest paid | [C11, C12] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 32; 5 |
| Contract liabilities and customer deposit/deferred revenue balances | [C13, C14] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 43; 11 |
| Post-period Alberta launch | [C15] | Caesars Q2 2026 Form 10-Q | 17 |
| Adjusted EBITDA by Q2 and H1 period | [C16] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 revenue and segment revenue | [C18, C23, C27] | Caesars Q2 2026 Form 10-Q | 18; 15; 21 |
| 2026 VICI/GLPI rent estimate | [C19] | Caesars FY2025 Form 10-K | 23 |
| PP&E purchases | [C20, C21] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 31; 4 |
| FY2025 Las Vegas segment revenue | [C22] | Caesars FY2025 Form 10-K | 19 |
| Q2 debt-facility carrying and principal information | [C24, C25] | Caesars Q2 2026 Form 10-Q | 9 |

## Source Registry

The effective financial sources are the three items in T4.1. The 10-K is the audited source for FY2025; the 10-Q is the unaudited primary source for Q2/H1 2026 and the June 30 balance sheet; the earnings release is supplemental. All figures are USD millions unless a ratio, rate or operating KPI explicitly states another unit. Source-limited upstream status is retained; no market, legal-document, peer or post-Q2 source is treated as present in this CP-1 evidence set. [C1, C2, C16, C18]

## Gaps & Conflicts

The complete cumulative gap register is T4.12. Definitions requiring explicit downstream treatment are T4.11: carrying debt versus principal and financing obligations; GAAP EBITDA versus issuer Adjusted EBITDA; P&L interest versus cash debt interest and rent interest; and the distinct P&L, operating cash-flow and financing cash-flow figures for the 2025 note redemption. No figures are silently substituted or reconciled. CP-MODEL is blocked because the delivered reporting does not contain four complete discrete quarters with the required segment, cash-flow and debt schedules. The accepted CP-0 artifact also identifies the pack as source-limited and reports no post-Q2 financial reporting; this CP-1 handoff does not upgrade those limitations.

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity and host front matter | Self-checked | Host-owned lines retained; model-authored fields limited to those required. |
| Source gate | Passed with limitations | Audited FY2025 and unaudited Q2 2026 financial statements are available; source set is limited. |
| Period and entity scope | Passed with limitations | Consolidated issuer periods distinguished from period-end balances; subsequent Alberta launch excluded from Q2. |
| Normalization | Passed | USD millions and consolidated US GAAP retained; non-GAAP EBITDA, face principal and financing obligations remain separately labelled. |
| Statement coverage | Passed with gaps | FY and interim income, cash-flow and balance-sheet statements represented; absent Q2 cash flows and gross-profit detail logged. |
| Reconciliation | Passed with limitation | Available revenue, EBITDA and cash identities tie; FY-to-quarter sum cannot be tested from supplied periods. |
| Required registers | Self-checked | T4.1–T4.6, T4.8–T4.19 and conditional CP-MODEL interface tables are present. |
| Confidence | Restricted | Score 57, Low; partial source gate and material coverage gaps cap the score below 60. |
| Host automated validation | Pending | Host validation follows this response; no script output or host finding is claimed. |