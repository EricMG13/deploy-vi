---
module_id: "CP-1"
module_name: "CanonicalDataFoundation"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "COVENANT_REFINANCING"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1-27ee9985139850a3"
credit_os_route_node_id: "RN-FULL_CREDIT_32-COVENANT_REFINANCING-02-CP-1"
credit_os_invocation_sha256: "fc78fa4233ff38ac7d35a16ae1aa7e46406a9f08325c0faa6791a51118117577"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a4ee2ea26d222a51d5c167a5868ea43f9bba131c911042fc7dcb2840af340ca2"
confidence_score: 44
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED, DEBT_BASIS_RECONCILIATION_OPEN, SCRIPT_OWNED_KPI_AND_DERIVED_PERIOD_VALUES_NOT_POPULATED]
downstream_consumers: [CP-1B, CP-1C, CP-2, CP-2A, CP-2D, CP-3, CP-3C, CP-4, CP-4A, CP-5, CP-5A, CP-MODEL]
---

## Audit Summary

- **Run status:** Restricted. The delivered annual and interim filings support source-grounded financial extraction; important debt-basis, transaction-financing, and model-interface limitations remain.
- **Confidence:** 44/100 — Low. This is an evidence and coverage assessment, not a credit rating or covenant-capacity conclusion.
- **Committee status:** Requires More Work. No covenant capacity is inferred from reported compliance or from covenant thresholds.
- **Source gate:** Partial. Current unaudited Q2 2026 statements, audited FY2025 comparatives, and transaction filings are present [C1]. The filing reports executed merger financing commitments were delivered, but the complete commitment-letter terms are not in the delivered evidence [C18].
- **Canonical artifact:** `CZR_CP-1_20261002.md`.
- **Host validation:** Follows this response; no host validator or completeness-check result is asserted.

## Analysis

### Analytical read-through

The canonical record shows Q2 2026 revenue of $2,993 million, up from $2,907 million, while Adjusted EBITDA was $920 million versus $955 million; H1 revenue was $5,863 million and Adjusted EBITDA $1,807 million [C2, C4]. Thus, reported revenue growth did not translate into period-over-period Adjusted EBITDA growth. Consolidated balance-sheet cash was $965 million; the debt note reports $11,705 million book value while balance-sheet current and long-term debt sum to $11,699 million, an unresolved $6 million basis difference [C5, C6, C14, C15]. H1 operating cash flow was $675 million, but no derived FCF or leverage is presented because the deterministic KPI computation is unavailable in this run [C7]. The merger and Alberta launch are kept distinct from canonical Q2 financial-period measures [C10, C18].

Q2/H1 source changes below are issuer-reported; changes are not independent analyst calculations. The table highlights why downstream work should preserve both revenue and earnings measures rather than treating growth in the former as evidence of improved debt-service capacity.

| Financial change | Q2 2026 | Q2 2025 | H1 2026 | H1 2025 | Credit relevance |
|---|---:|---:|---:|---:|---|
| Net revenues ($m) | 2,993 | 2,907 | 5,863 | 5,701 | Higher reported revenue [C2] |
| Adjusted EBITDA ($m) | 920 | 955 | 1,807 | 1,839 | Lower reported earnings measure [C4] |
| Operating income ($m) | 513 | 526 | 1,013 | 1,014 | Near-flat H1; lower Q2 [C3] |
| Cash and equivalents ($m) | 965 at 30 Jun 2026 | 887 at 31 Dec 2025 | — | — | Period-end balance, not a cash-flow measure [C5] |
| Note total debt, book ($m) | 11,705 at 30 Jun 2026 | 11,792 at 31 Dec 2025 | — | — | Differs from balance-sheet carrying sum [C6] |

**Operating and cash-flow transmission.** Evidence: Q2 revenue grew while Adjusted EBITDA declined; the filing attributes the Las Vegas decline to lower leisure visitation, hotel occupancy/rates, table-game volume and hold, while Regional growth includes the consolidation of Caesars Windsor [C2, C4]. Risk mechanic: a mix of weaker Las Vegas performance and acquired/consolidated Regional contribution can obscure underlying organic earnings direction; lower hold and visitation can reduce operating cash generation, while labor and gaming taxes constrain conversion. Credit implication: debt-service and refinancing analysis should separate reported growth from recurring cash generation and compare like-for-like periods; the available evidence does not support an independent normalized EBITDA estimate.

**Liquidity and funding float.** Evidence: H1 CFO was $675 million versus $680 million in the prior-year H1, and cash interest paid for debt was $368 million versus $405 million [C7, C8]. Q2 liquidity disclosure reports $2,928 million of cash and borrowing capacity in aggregate [C17]. Customer deposits and other deferred revenue were $545 million at June 30, 2026, up $53 million from the beginning of the year; these customer funds relate to gaming play and advance payments for goods or services not yet delivered [C9]. Risk mechanic: the liability is operating float, not funded debt; a demand or redemption shock could turn advance receipts into future performance or cash obligations. Credit implication: assess available liquidity against contractual payments and the timing/fulfilment profile of deposits; do not add the float to debt or treat it as freely available without qualification.

**Debt, definition and covenant boundary.** Evidence: the Q2 debt note gives $11,807 million face value and $11,705 million book value; the Q2 balance sheet reports $114 million current debt and $11,585 million long-term debt [C6, C14, C15]. Risk mechanic: using face value, note book value or balance-sheet carrying amounts without aligning definitions changes leverage and refinancing denominators. Credit implication: the canonical CP-1 debt basis is balance-sheet carrying value, with the $6 million difference to the note book value retained as an unresolved conflict. The filing states covenant compliance at June 30, 2026 [C21], but the available inputs do not establish covenant EBITDA, testing mechanics, restricted-group perimeter, or capacity; covenant headroom is therefore **Not Calculable from Provided Materials**.

**Event separation and downside path.** The merger agreement was entered into on May 27, 2026, within the reporting quarter; the filed narrative says executed debt commitment letters were delivered, but their full terms are not present here [C18]. Do not merge transaction financing, assumed-debt estimates, or transaction costs into Q2 debt balances or recurring earnings. Separately, the Alberta mobile sports betting and iGaming launch occurred July 13, 2026, after the June 30 balance-sheet date, and is not included in Q2 figures [C10]. A downside path supported by the filings is weaker visitation/hold or increased competitive pressure, followed first by lower property earnings; lower cash conversion would then reduce internal funding available for debt service, rent and investment, increasing refinancing dependence. Observable monitoring triggers are subsequent reported visitation/hold, segment Adjusted EBITDA, CFO, cash, available revolver capacity, debt maturities, and changes to merger financing or closing status. No unsupported stress amount is assigned.

**Strongest counterevidence.** Regional and Digital results provide a partial offset to Las Vegas weakness; H1 revenue and CFO remain positive, and the issuer reports covenant compliance at the period end [C2, C4, C7, C21]. This would strengthen the view of near-term resilience if comparable-period operating improvements persisted, cash conversion improved, and debt definitions and financing terms were reconciled. It does not resolve the current definition gap or establish covenant capacity.

### Analytical appendix — complete canonical registers

#### T4.1 — Source Register

| Source File Name | Document Type | Period Coverage | Currency | Unit | Perimeter | Accounting Basis | Evidence Quality Tier | Analytical Use | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| CZR_Q2_2026_10Q.txt | Form 10-Q, unaudited | Q2 and H1 ended 2026-06-30; comparative Q2/H1 2025 | USD | Millions unless stated | Caesars Entertainment, Inc. and consolidated subsidiaries | US GAAP interim | Tier 2b — unaudited without auditor review | Current IS, CFS, BS, debt, segment, liquidity and event inputs | Interim filing; financial results may not indicate full-year results; merger financing terms not fully included [C1, C18] |
| CZR_FY2025_10K.txt | Form 10-K, audited consolidated financial statements | FY2025, FY2024 BS comparatives; FY2025–FY2023 annual flows | USD | Millions unless stated | Caesars Entertainment, Inc. and consolidated subsidiaries | US GAAP | Tier 1 — audited FS | Audited annual comparator, debt, cash-flow and definition context | Older than Q2 2026; FY results are not a substitute for current-period results [C12, C13, C14, C15, C16] |
| CZR_2026_Merger_Agreement_8K.txt | Form 8-K, filed transaction narrative | Merger agreement dated 2026-05-27 | USD | As stated | Caesars and transaction parties | Documentary transaction disclosure | Tier 1 — SEC filing; excerpted transaction narrative | Event chronology and financing-commitment existence | Commitment letters’ complete terms are not present; agreement schedules omitted from the delivered filing representation [C18] |
| CZR_2026_Merger_Press_Release.txt | Issuer press release | Announcement dated 2026-05-28 | USD | Billions / per share as stated | Caesars and proposed transaction | Issuer announcement | Tier 2c — issuer supporting disclosure | Context only; not a substitute for the filed financial statements or financing documents | Transaction value and assumed debt are rounded announcement figures, not Q2 debt balances |

#### T4.2 — Entity Period Key

| Entity Name | Entity Role | Fiscal Year End | Reporting Currency | Reporting Unit | Consolidation Perimeter | Accounting Basis | Available Periods |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. and consolidated subsidiaries | Registrant / consolidated issuer; borrower and issuer identities are stated in the filings | December 31 | USD | Millions, except specified operating measures | Consolidated subsidiaries; includes consolidated Caesars Virginia; no finance-company perimeter disclosed in the delivered financial statements | US GAAP; FY2025 audited; Q2/H1 2026 unaudited interim | FY2025, FY2024 balance sheet, FY2023–FY2025 annual flows, Q2 and H1 2026, Q2 and H1 2025 |

#### T4.3 — Normalization Register

| Description | Source | Type | Before | After | Rationale | Periods |
|---|---|---|---|---|---|---|
| Establish common presentation basis | Q2 2026 Form 10-Q; FY2025 Form 10-K | Presentation normalization | USD millions as reported; consolidated CEI and subsidiaries; US GAAP | USD millions; consolidated CEI and subsidiaries; US GAAP | No currency or unit conversion performed. Period type, perimeter and audited/unaudited status remain identified; no undocumented adjustments made. | All reported periods |

#### T4.4 — Income Statement

| Line Item | FY2025 | FY2024 | FY2023 | Q2 2026 | Q2 2025 | H1 2026 | H1 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Net revenues | 11,486 | 11,245 | 11,528 | 2,993 | 2,907 | 5,863 | 5,701 |
| Casino revenue | 6,617 | 6,267 | 6,367 | 1,759 | 1,668 | 3,425 | 3,262 |
| Food and beverage revenue | 1,714 | 1,716 | 1,728 | 426 | 428 | 850 | 863 |
| Hotel revenue | 1,945 | 2,016 | 2,090 | 495 | 509 | 982 | 991 |
| Other revenue | 1,210 | 1,246 | 1,343 | 313 | 302 | 606 | 585 |
| COGS | — | — | — | — | — | — | — |
| Gross profit | — | — | — | — | — | — | — |
| Casino operating expense | 3,602 | 3,370 | 3,342 | 955 | 887 | 1,857 | 1,748 |
| Food and beverage operating expense | 1,106 | 1,073 | 1,049 | 281 | 275 | 555 | 550 |
| Hotel operating expense | 615 | 580 | 570 | 163 | 155 | 319 | 306 |
| Other operating expense | 420 | 396 | 434 | 95 | 105 | 190 | 200 |
| General and administrative | 1,926 | 1,920 | 2,012 | 521 | 477 | 1,025 | 960 |
| Corporate expense | 322 | 307 | 306 | 94 | 84 | 182 | 166 |
| Impairment charges | 182 | 302 | 95 | — | — | — | — |
| Depreciation and amortization | 1,417 | 1,324 | 1,261 | 355 | 364 | 702 | 721 |
| Transaction and other costs, net | 38 | (331) | (13) | 16 | 34 | 20 | 36 |
| Total operating expenses | 9,628 | 8,941 | 9,056 | 2,480 | 2,381 | 4,850 | 4,687 |
| Operating income (EBIT) | 1,858 | 2,304 | 2,472 | 513 | 526 | 1,013 | 1,014 |
| EBITDA (reported, GAAP) | — | — | — | — | — | — | — |
| Adjusted EBITDA (issuer non-GAAP) | 3,624 | 3,739 | 3,938 | 920 | 955 | 1,807 | 1,839 |
| Interest expense, net | (2,304) | (2,366) | (2,342) | (573) | (579) | (1,142) | (1,153) |
| Interest income, separately stated | — | — | — | — | — | — | — |
| Loss on extinguishment of debt | (4) | (89) | (200) | — | — | — | — |
| Other income | 2 | 27 | 10 | 7 | 1 | 5 | — |
| Loss before income taxes | (448) | (124) | (60) | (53) | (52) | (124) | (139) |
| Income tax benefit (provision) | 11 | (87) | 888 | 12 | (13) | — | (24) |
| Net income (loss) | (437) | (211) | 828 | (41) | (65) | (124) | (163) |
| Net income attributable to Caesars | (502) | (278) | 786 | (62) | (82) | (160) | (197) |
| Cash interest paid for debt | 813 | — | — | — | — | 368 | 405 |
| Cash taxes paid, net | 81 | — | — | — | — | 11 | 58 |
| Stock-based compensation expense | 95 | 94 | 104 | 23 | 24 | 47 | 50 |
| Exceptionals / separate one-off total | — | — | — | — | — | — | — |

#### T4.5 — Cash Flow Statement

| Line Item | FY2025 | FY2024 | FY2023 | H1 2026 | H1 2025 |
|---|---:|---:|---:|---:|---:|
| Net cash provided by operating activities | 1,302 | 1,075 | 1,809 | 675 | 680 |
| Working-capital change, aggregate | — | — | — | — | — |
| Purchase of property and equipment | (805) | (1,296) | (1,264) | (335) | (453) |
| Acquisition of intangible assets | (4) | (15) | (30) | — | — |
| Maintenance capex | — | — | — | — | — |
| Growth capex | — | — | — | — | — |
| FCF, issuer-reported | — | — | — | — | — |
| Dividends paid | — | — | — | — | — |
| Acquisitions / asset purchases | — | — | — | (98) | — |
| Proceeds from sale of property, equipment, trademark and businesses | 218 | 554 | 1 | 20 | 3 |
| Debt issuance proceeds | 1,580 | 7,525 | 5,460 | 885 | 590 |
| Debt repayments | (1,969) | (7,670) | (6,106) | (983) | (612) |
| Equity repurchases | (229) | (191) | — | — | (100) |
| Financing obligation payments | (26) | (8) | (8) | (19) | (8) |
| Net cash change, cash and restricted cash | (32) | (127) | (160) | 93 | 70 |
| Cash interest paid for debt | 813 | 1,052 | 846 | 368 | 405 |
| Cash interest paid for rent related to financing obligations / GLPI and VICI leases | 1,349 | 1,324 | 1,286 | 686 | 672 |
| Cash taxes paid, net | 81 | 48 | 26 | 11 | 58 |

#### T4.6 — Balance Sheet

| Line Item | December 31, 2025 | December 31, 2024 | June 30, 2026 |
|---|---:|---:|---:|
| Cash and equivalents | 887 | 866 | 965 |
| Restricted cash | 85 | 95 | 96 |
| Short-term investments | 2 | 2 | 2 |
| Trade receivables, net | 476 | 470 | 485 |
| Inventories | 43 | 45 | 49 |
| Other current assets | 312 | 271 | 382 |
| Total current assets | 1,803 | 1,747 | 1,977 |
| PP&E, net | 14,358 | 14,812 | 14,125 |
| Goodwill | 10,441 | 10,601 | 10,441 |
| Intangible assets other than goodwill | 3,985 | 4,133 | 3,959 |
| Other non-current assets | 852 | 1,104 | 1,048 |
| Total assets | 31,639 | 32,590 | 31,742 |
| Current portion of long-term debt | 114 | 109 | 114 |
| Accounts payable | 297 | 296 | 290 |
| Accrued interest | 224 | 242 | 222 |
| Accrued other liabilities | 1,618 | 1,625 | 1,696 |
| Total current liabilities | 2,253 | 2,272 | 2,322 |
| Long-term financing obligations | 13,096 | 12,899 | 13,157 |
| Long-term debt | 11,670 | 12,033 | 11,585 |
| Total debt, balance-sheet carrying basis: current plus long-term debt | 11,784 | 12,142 | 11,699 |
| Senior secured debt, balance-sheet class total | — | — | — |
| Senior unsecured debt, balance-sheet class total | — | — | — |
| Subordinated debt | — | — | — |
| Other long-term liabilities | 876 | 880 | 1,069 |
| Total liabilities | 27,953 | 28,214 | 28,190 |
| Caesars stockholders' equity | 3,504 | 4,157 | 3,375 |
| Minority interests | 182 | 219 | 177 |
| Total stockholders' equity | 3,686 | 4,376 | 3,552 |
| Customer deposits and other deferred revenue, disclosed contract-liability balance | 549 at start of year; 492 at year-end | 693 at start of year; 549 at year-end | 545 |

#### T4.8 — Constructed Period Register

| Metric Name | Derived Period Type | Full-Year Component | Current Stub | Prior-Year Stub | Derived Value | Calculation Status | Source Files | Limitations |
|---|---|---:|---:|---:|---:|---|---|---|
| Net revenues, LTM to 2026-06-30 | LTM | 11,486 (FY2025) | 5,863 (H1 2026) | 5,701 (H1 2025) | null | Not Calculable | CZR_FY2025_10K.txt; CZR_Q2_2026_10Q.txt | Formula is FY + current YTD − prior YTD; the deterministic period-construction script was not delivered, so no hand-derived script-owned value is substituted. |
| Adjusted EBITDA, LTM to 2026-06-30 | LTM | 3,624 (FY2025) | 1,807 (H1 2026) | 1,839 (H1 2025) | null | Not Calculable | CZR_FY2025_10K.txt; CZR_Q2_2026_10Q.txt | Issuer non-GAAP definition; script-owned LTM value not computed in this run. |

#### T4.9 — Calculation Register

| Metric Name | Formula | Numerator Value | Numerator Source | Denominator Value | Denominator Source | Period | Currency | Unit | Calculated Value | Calculation Status | Evidence Quality Tier | Limitations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Debt / Adjusted EBITDA | Balance-sheet carrying debt / issuer Adjusted EBITDA; period and annualization must match | 11,699 | Q2 2026 Form 10-Q, BS p.2 | 1,807 | Q2 2026 Form 10-Q, H1 reconciliation p.16 | H1 2026; debt at 2026-06-30 | USD | Millions / ratio | null | Not Calculable | Tier 2b | No aligned annual or LTM EBITDA computation; deterministic KPI script not delivered; debt basis conflict CF-1 remains open. |
| Net Debt / Adjusted EBITDA | (balance-sheet carrying debt − cash and equivalents) / aligned Adjusted EBITDA | 10,734 | Q2 2026 Form 10-Q, BS p.2; canonical debt basis | 1,807 | Q2 2026 Form 10-Q, H1 reconciliation p.16 | H1 2026; debt and cash at 2026-06-30 | USD | Millions / ratio | null | Not Calculable | Tier 2b | No aligned annual or LTM EBITDA computation; restricted cash excluded from cash deduction; deterministic KPI script not delivered. |
| CFO | Reported net cash provided by operating activities | 675 | Q2 2026 Form 10-Q, CFS p.4 | 1 | Not applicable | H1 2026 | USD | Millions | 675 | Verified | Tier 2b | Reported cash-flow measure; not FCF. |
| Cash interest paid | Reported cash interest paid for debt | 368 | Q2 2026 Form 10-Q, supplemental cash-flow disclosure p.5 | 1 | Not applicable | H1 2026 | USD | Millions | 368 | Verified | Tier 2b | Cash paid, distinct from accrued interest expense. |
| Cash and committed borrowing capacity | Reported aggregate liquidity disclosure | 2,928 | Q2 2026 Form 10-Q, liquidity table p.22 | 1 | Not applicable | 2026-06-30 | USD | Millions | 2,928 | Verified | Tier 2b | Issuer-reported sum; does not establish availability after all future needs or covenant conditions. |

#### T4.10 — KPI Dashboard

| KPI Category | Metric Name | Period 1…N | Trend Direction | Analyst Note |
|---|---|---|---|---|
| Growth | Net revenues | FY2025 11,486; FY2024 11,245; FY2023 11,528; Q2 2026 2,993; Q2 2025 2,907; H1 2026 5,863; H1 2025 5,701 | Increased in Q2 and H1 year over year | Source-reported revenue; H1 2026 includes Caesars Windsor consolidation beginning March 3, 2026. Not a like-for-like growth calculation. [C2, C12] |
| Earnings | Adjusted EBITDA | FY2025 3,624; FY2024 3,739; FY2023 3,938; Q2 2026 920; Q2 2025 955; H1 2026 1,807; H1 2025 1,839 | Lower in Q2 and H1 year over year | Issuer non-GAAP metric; not a GAAP measure or liquidity measure. [C4, C13] |
| Margin | Adjusted EBITDA margin | Q2 2026 30.7%; Q2 2025 32.9%; H1 2026 30.8%; H1 2025 32.3%; FY2025 31.6%; FY2024 33.3%; FY2023 34.2% | Lower in Q2 and H1 year over year | Issuer-reported margin; margin change should be read with reported segment mix and perimeter changes. |
| Earnings | Operating income | FY2025 1,858; FY2024 2,304; FY2023 2,472; Q2 2026 513; Q2 2025 526; H1 2026 1,013; H1 2025 1,014 | Lower Q2; nearly unchanged H1 | Directly reported statement measure, USD millions. [C3] |
| Cash flow | CFO | FY2025 1,302; FY2024 1,075; FY2023 1,809; H1 2026 675; H1 2025 680 | Lower H1 year over year | CFO is not FCF; capex splits and script-produced FCF metrics are not populated. [C7, C16] |
| Liquidity | Cash and equivalents | 2026-06-30 965; 2025-12-31 887 | Increased between reported dates | Period-end balances; not directly comparable to a flow measure. [C5] |
| Leverage | Debt / EBITDA; Net Debt / EBITDA; Senior Secured Debt / EBITDA | Not Calculable for available periods | Not calculated | Required ratios are not hand-derived; carrying-value debt basis has an unresolved note-to-balance-sheet difference. [C6, C14, C15] |
| Liquidity | Customer deposits and other deferred revenue | 2026-06-30 545; 2026-01-01 492; 2025-06-30 586; 2025-01-01 549 | Increased by 53 in H1 2026; decreased by 37 in H1 2025 | Operating funding float with future performance/refund obligations; not debt. [C9] |

#### T4.11 — Definition Conflict Register

| Metric Name | Canonical Definition | Issuer-Reported Definition | Source of Conflict | Periods Affected | Materiality | Downstream Modules Affected | Resolution / Recommendation |
|---|---|---|---|---|---|---|---|
| Total debt: balance-sheet carrying value vs debt-note book value and face value | Current plus long-term balance-sheet carrying debt, net of issuance costs; gross principal is not the leverage denominator. | Q2 debt note: total debt face value 11,807 and book value 11,705. Q2 BS current portion 114 plus long-term debt 11,585 equals 11,699. FY2025 note book value 11,792 versus BS current 114 plus long-term 11,670 equals 11,784. | Q2 2026 Form 10-Q, debt note p.9 and BS p.2; FY2025 Form 10-K debt note and BS p.29 [C6, C14, C15] | Q2 2026 and FY2025 | $6m Q2 and $8m FY2025 difference between note book total and BS carrying sum; face value differs materially from carrying basis. | CP-1B, CP-2, CP-2A, CP-2D, CP-3, CP-3C, CP-4, CP-4A, CP-MODEL | Retain both source presentations. Use balance-sheet current plus long-term amounts for canonical CP-1 Total Debt; do not silently reconcile the note totals. Obtain source reconciliation before covenant or leverage use. |
| Adjusted EBITDA | Issuer Adjusted EBITDA is not a substitute for GAAP operating performance or cash liquidity; canonical reporting distinguishes issuer metric from GAAP EBITDA. | Issuer describes its non-GAAP Adjusted EBITDA and cautions that its definition may differ from debt/lease agreements and other companies. | Q2 2026 Form 10-Q, MD&A Adjusted EBITDA discussion p.21 [C11] | FY2023–FY2025, Q2/H1 2025–2026 | Material to leverage and covenant metrics; covenant EBITDA definition not supplied by these financial statements. | CP-2, CP-3C, CP-4, CP-4A, CP-MODEL | Retain issuer-reported Adjusted EBITDA separately; do not use as covenant EBITDA without governing-document definition and calculation. |
| Merger announcement debt amount vs reporting-date debt | Canonical debt is reporting-date balance-sheet carrying debt; transaction announcement amounts remain event-context figures with their stated date and basis. | Press release describes approximately $11.9bn debt assumed in the proposed transaction; Q2 debt note reports face 11,807 and book 11,705 at June 30, 2026. | Merger press release p.1; Q2 2026 Form 10-Q debt note p.9 [C6] | Merger announcement May 28, 2026 vs Q2 balance date June 30, 2026 | Different rounded amount, date and transaction role; not a period debt reconciliation. | CP-2, CP-2D, CP-3C, CP-4, CP-4A | Keep announcement and reporting-date values separate. Do not blend announced debt assumed into Q2 balance-sheet figures. |

#### T4.12 — Gaps & Warnings

| Gap Description | Affected Line Item or Metric | Affected Period(s) | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|---|
| Income statement does not disclose COGS, gross profit, separate interest income, GAAP EBITDA, or a total exceptionals line on the selected presentation basis. | T4.4: COGS, gross profit, EBITDA (reported), interest income, exceptionals | All listed periods | Gross margin and GAAP EBITDA calculations unavailable; CP-2 and CP-2D limitation. | MATERIAL | Obtain a source-supported mapping or leave metrics null; do not infer from aggregate expense categories. |
| Cash-flow working-capital aggregate, capex maintenance/growth split, issuer FCF and dividends paid are not separately available for all periods. | T4.5: working capital, capex split, FCF, dividends | FY2023–FY2025 and H1 2025–2026 | FCF durability and forecast inputs limited; CP-2/CP-2A limitation. | MATERIAL | Obtain detailed cash-flow/capex schedules; retain reported PP&E purchases separately. |
| BS seniority subtotals cannot be reconstructed as a source-reported balance-sheet total without instrument-level classification and carrying-value reconciliation. | T4.6: senior secured, unsecured and subordinated debt | FY2024–Q2 2026 | Capital structure and recovery analysis limited. | MATERIAL | Preserve facility-level classifications and unresolved total-debt difference; no inferred subtotal. |
| Note debt book totals differ from current plus long-term BS debt by $6m at Q2 2026 and $8m at FY2025; gross face values are a separate basis. | T4.6 total debt; T4.11 CF-1; T4.15 total_debt; T4.18 | Q2 2026; FY2025 | Leverage denominator, facility reconciliation and debt schedule outputs require review. | MATERIAL | Obtain issuer reconciliation; canonical basis remains current plus long-term BS carrying value. |
| Script-owned constructed LTM values are null; no script-generated period construction is available in this run. | T4.8: revenue and Adjusted EBITDA LTM | LTM to 2026-06-30 | Ratio and trend analysis using LTM is unavailable. | MATERIAL | Populate only from the deterministic period-construction process; do not hand-derive. |
| Script-owned KPI values are not populated; several required ratios cannot be presented as verified. | T4.9: leverage, coverage, FCF, liquidity/debt, margins and growth | FY2023–Q2 2026 | CP-2, CP-2A, CP-2D, CP-3C and covenant work require limitation. | MATERIAL | Run the governed calculation process when available; use Not Calculable pending that output. |
| Customer deposits/deferred revenue are material operating float and the interim filing records an increase. | Customer deposits and other deferred revenue | H1 2026 | Liquidity analysis must distinguish customer obligations from debt. | MATERIAL | Track balance, redemption/performance obligations and future movements; do not classify as debt. [C9] |
| Merger debt commitment letters are reported as delivered, but their complete terms are absent from delivered evidence. | Transaction financing and refinancing inputs | From 2026-05-27 onward | Transaction leverage and refinancing analysis remain incomplete. | MATERIAL | Obtain complete executed commitment letters and related definitive financing documents. [C18] |
| Alberta launch is subsequent to the June 30 balance-sheet date. | Subsequent event; operating results | 2026-07-13 | Do not blend into Q2 historical measures. | MINOR | Preserve event date; use only as post-period context. [C10] |
| CP-MODEL historical data do not meet the interface readiness standard of four complete discrete quarters and complete debt schedules. | T4.14–T4.19; CP-MODEL readiness | Q2 2026 and historical periods supplied | Workbook handoff is blocked; current interface contains annual, half-year and selected quarter inputs, not four discrete quarters. | MATERIAL | Provide four quarters of complete, source-located financial and facility data; resolve mandatory reconciliations. |
| Blank/dash values in T4.4–T4.6 are unavailable or not separately disclosed, not zero. | All rows with — in T4.4–T4.6 | As shown | Metrics depending on those line items remain unavailable. | MATERIAL | Retain null rendering; use gap entries above; do not infer or treat blanks as zero. |
| Value-bearing nulls in interface tables: T4.8 rows 1–2, Derived Value; T4.9 rows 1–2, Calculated Value; T4.17 H1 2026 income-tax adjustment; T4.18 CVA Revolving Credit Facility carrying_value/principal/drawn_amount; T4.19 FY-to-quarter reconciliation calculated_value/difference. | Specified tagged-table cells | LTM; H1 2026; Q2 2026; FY2025 | Missing values remain unavailable; related readiness/reconciliation limitation. | MATERIAL | Use null as shown and preserve each cell-level reason in this row; do not replace with zero. |

#### T4.13 — Downstream Readiness

| Downstream Module | Readiness Status | Gaps or Limitations | Recommended Actions |
|---|---|---|---|
| CP-1B | Ready with Limitations | Canonical statements available; KPI computation and debt-basis reconciliation remain open. | Carry source periods and limitations; avoid unsupported leverage conclusions. |
| CP-1C | Ready with Limitations | Financial history available, but incomplete current underwriting source set. | Use only delivered issuer sources and disclose gaps. |
| CP-2 | Ready with Limitations | FCF, LTM and some KPIs unavailable; customer funding float needs explicit treatment. | Use source-supported line items; obtain complete cash-flow/capex inputs. |
| CP-2A | Ready with Limitations | CFO and reported liquidity available; no calculated FCF or complete forecast. | Do not infer liquidity runway; request forward cash schedule if required. |
| CP-2D | Ready with Limitations | Earnings data available; issuer Adjusted EBITDA is not automatically covenant EBITDA. | Reconcile add-backs and periods before earnings-quality conclusions. |
| CP-3 | Ready with Limitations | Debt classification and balance-sheet/note basis difference require reconciliation. | Preserve carrying-value convention and facility-specific uncertainty. |
| CP-3C | Ready with Limitations | Debt maturity disclosures available; full transaction financing terms and market quotations not delivered. | Obtain commitment terms and current instrument-specific market evidence. |
| CP-4 | Ready with Limitations | Financial inputs available; CP-1 does not determine covenant EBITDA or legal capacity. | Use governing-document definitions and restrict conclusions to supported inputs. |
| CP-4A | Ready with Limitations | Covenant capacity cannot be calculated from this canonical dataset. | Obtain required covenant EBITDA, debt perimeter and testing data. |
| CP-5 | Ready with Limitations | Traceable source data with unresolved definition and source gaps. | Preserve citations, gaps and status. |
| CP-5A | Ready with Limitations | Structured financial inputs available, but material gaps and restricted QA status remain. | Audit source trace, conflict and completeness limitations. |
| CP-MODEL | Not Ready | Fewer than four discrete quarters; incomplete quarter facility history; unresolved debt reconciliation; selected null interface cells. | Obtain the complete quarterly source pack and resolve mandatory checks before workbook use. |

#### T4.14 — Model Period Register

<!-- table-id: cp1.model_period_register -->

| period_id | fiscal_year | fiscal_quarter | period_type | start_date | end_date | day_count | audit_status | currency | unit | accounting_basis | entity_perimeter | source_id | source_locator | component_period_ids |
|---|---:|---:|---|---|---|---:|---|---|---|---|---|---|---|---|
| FY2025 | 2025 | null | FY | 2025-01-01 | 2025-12-31 | 365 | AUDITED | USD | MILLIONS | US GAAP | CEI consolidated | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K pp.19, 29–32 | — |
| FY2024 | 2024 | null | FY | 2024-01-01 | 2024-12-31 | 366 | AUDITED | USD | MILLIONS | US GAAP | CEI consolidated | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K pp.29–32 | — |
| FY2023 | 2023 | null | FY | 2023-01-01 | 2023-12-31 | 365 | AUDITED | USD | MILLIONS | US GAAP | CEI consolidated | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K pp.29–32 | — |
| H1_2026 | 2026 | null | YTD | 2026-01-01 | 2026-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP interim | CEI consolidated | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.2–5 | — |
| Q2_2026 | 2026 | 2 | QUARTER | 2026-04-01 | 2026-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP interim | CEI consolidated | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.2–3 | — |
| H1_2025 | 2025 | null | YTD | 2025-01-01 | 2025-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP interim | CEI consolidated | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.2–5 | — |
| Q2_2025 | 2025 | 2 | QUARTER | 2025-04-01 | 2025-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP interim | CEI consolidated | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.2–3 | — |

#### T4.15 — Model Account Register

<!-- table-id: cp1.model_account_register -->

| metric_id | period_id | value | sign_convention | value_class | calculation_status | source_id | source_locator | conflict_refs | limitation_refs |
|---|---|---:|---|---|---|---|---|---|---|
| revenue | FY2025 | 11486 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 | null | null |
| revenue | FY2024 | 11245 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 | null | null |
| revenue | FY2023 | 11528 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 | null | null |
| revenue | H1_2026 | 5863 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| revenue | Q2_2026 | 2993 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| revenue | H1_2025 | 5701 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| revenue | Q2_2025 | 2907 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| ebit | FY2025 | 1858 | INCOME_POSITIVE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.30 | null | null |
| ebit | Q2_2026 | 513 | INCOME_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.3 | null | null |
| ebitda | FY2025 | null | INCOME_POSITIVE | NOT_AVAILABLE | Not Available | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.30; GAAP EBITDA not stated | null | GAP-IS-1 |
| adjusted_ebitda | FY2025 | 3624 | INCOME_POSITIVE | ISSUER_NON_GAAP | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K pp.19, 23 | null | LIM-EBITDA-1 |
| adjusted_ebitda | H1_2026 | 1807 | INCOME_POSITIVE | ISSUER_NON_GAAP | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.16 | null | LIM-EBITDA-1 |
| adjusted_ebitda | Q2_2026 | 920 | INCOME_POSITIVE | ISSUER_NON_GAAP | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.16 | null | LIM-EBITDA-1 |
| adjusted_ebitda | H1_2025 | 1839 | INCOME_POSITIVE | ISSUER_NON_GAAP | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.16 | null | LIM-EBITDA-1 |
| adjusted_ebitda | Q2_2025 | 955 | INCOME_POSITIVE | ISSUER_NON_GAAP | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.16 | null | LIM-EBITDA-1 |
| depreciation_amortization | FY2025 | 1417 | EXPENSE_POSITIVE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.30 | null | null |
| depreciation_amortization | H1_2026 | 702 | EXPENSE_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.3 | null | null |
| cash_interest_paid | FY2025 | 813 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_CASH_PAID | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.32; cash paid shown positive in source | null | null |
| cash_interest_paid | H1_2026 | 368 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_CASH_PAID | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.5; cash paid shown positive in source | null | null |
| cash_taxes_paid | FY2025 | 81 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_CASH_PAID | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.32 | null | null |
| cash_taxes_paid | H1_2026 | 11 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_CASH_PAID | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.5 | null | null |
| cfo_ncfo | FY2025 | 1302 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.31 | null | null |
| cfo_ncfo | H1_2026 | 675 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.4 | null | null |
| cfo_ncfo | H1_2025 | 680 | INFLOW_POSITIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.4 | null | null |
| capex_and_intangible_investment | FY2025 | -805 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_PP&E_ONLY | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.31; excludes separately reported intangible purchases | null | LIM-CAPEX-1 |
| capex_and_intangible_investment | H1_2026 | -335 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_PP&E_ONLY | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.4; excludes separately unreported intangible purchases | null | LIM-CAPEX-1 |
| capex_and_intangible_investment | H1_2025 | -453 | OUTFLOW_NEGATIVE | DIRECT_REPORTED_PP&E_ONLY | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.4 | null | LIM-CAPEX-1 |
| cash_and_equivalents | FY2025 | 887 | POSITIVE_BALANCE | DIRECT_REPORTED | Verified | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.29 | null | null |
| cash_and_equivalents | Q2_2026 | 965 | POSITIVE_BALANCE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| total_debt | FY2025 | 11784 | POSITIVE_BALANCE | CALCULATED_BS_CARRYING_SUM | Calculated | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.29; current 114 + long-term 11,670 | CF-1 | null |
| total_debt | Q2_2026 | 11699 | POSITIVE_BALANCE | CALCULATED_BS_CARRYING_SUM | Calculated | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2; current 114 + long-term 11,585 | CF-1 | null |
| rcf_commitment | Q2_2026 | 2250 | POSITIVE_COMMITMENT | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.10; CEI revolver aggregate commitment | null | null |
| rcf_drawn | Q2_2026 | 120 | POSITIVE_DRAWN_BALANCE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 | null | null |
| net_accounts_receivable | Q2_2026 | 485 | POSITIVE_BALANCE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| inventory | Q2_2026 | 49 | POSITIVE_BALANCE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| accounts_payable | Q2_2026 | 290 | POSITIVE_BALANCE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.2 | null | null |
| pretax_income | Q2_2026 | -53 | INCOME_POSITIVE_LOSS_NEGATIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.3 | null | null |
| income_tax_expense | Q2_2026 | -12 | EXPENSE_POSITIVE_BENEFIT_NEGATIVE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.3; reported benefit | null | null |
| effective_tax_rate | Q2_2026 | 22.6% | RATE | DIRECT_REPORTED | Verified | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.13 | null | null |

#### T4.16 — Segment Revenue Schedule

<!-- table-id: cp1.segment_revenue_schedule -->

| segment_id | segment_name | segment_type | display_priority | period_id | revenue | status | source_id | source_locator |
|---|---|---|---:|---|---:|---|---|---|
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | FY2025 | 4049 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| regional | Regional | OPERATING_SEGMENT | 2 | FY2025 | 5756 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | FY2025 | 1408 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | FY2025 | 279 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2025 | -6 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | FY2024 | 4274 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| regional | Regional | OPERATING_SEGMENT | 2 | FY2024 | 5539 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | FY2024 | 1163 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | FY2024 | 274 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2024 | -5 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | FY2023 | 4470 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| regional | Regional | OPERATING_SEGMENT | 2 | FY2023 | 5778 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | FY2023 | 973 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | FY2023 | 307 | REPORTED | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2023 | 0 | REPORTED_AS_DASH | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.19; source displays dash, value retained as reported zero only for reconciliation schedule |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2026 | 1017 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| regional | Regional | OPERATING_SEGMENT | 2 | Q2_2026 | 1570 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2026 | 351 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2026 | 57 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2026 | -2 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2025 | 1054 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| regional | Regional | OPERATING_SEGMENT | 2 | Q2_2025 | 1435 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2025 | 343 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2025 | 74 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2025 | 1 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | H1_2026 | 2020 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| regional | Regional | OPERATING_SEGMENT | 2 | H1_2026 | 3000 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2026 | 725 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2026 | 123 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2026 | -5 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | H1_2025 | 2057 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| regional | Regional | OPERATING_SEGMENT | 2 | H1_2025 | 2823 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2025 | 678 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2025 | 141 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2025 | 2 | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.11 |

<!-- table-id: cp1.cp_model_segment_allocation -->

| slot_id | slot_label | component_segment_ids |
|---|---|---|
| DIVISION_1 | Las Vegas and Regional | las_vegas, regional |
| DIVISION_2 | Digital and Managed and Branded | caesars_digital, managed_branded |
| DIVISION_3 | Corporate and Other | corporate_other |

<!-- table-id: cp1.operating_kpi_schedule -->

| kpi_id | kpi_label | business_unit | kpi_category | display_priority | period_id | value | unit | value_type | status | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|---|
| lv_table_games_drop | Table games drop | Las Vegas | Gaming volume | 1 | Q2_2026 | 706 | USD millions | PERIOD_FLOW | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| lv_table_games_hold | Table games hold | Las Vegas | Hold rate | 2 | Q2_2026 | 16.6% | Percent | RATE | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| lv_slot_handle | Slot handle | Las Vegas | Gaming volume | 3 | Q2_2026 | 2674 | USD millions | PERIOD_FLOW | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| lv_hotel_occupancy | Hotel occupancy | Las Vegas | Occupancy | 4 | Q2_2026 | 95.5% | Percent | RATE | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| regional_table_games_drop | Table games drop | Regional | Gaming volume | 1 | Q2_2026 | 1100 | USD millions | PERIOD_FLOW | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| regional_table_games_hold | Table games hold | Regional | Hold rate | 2 | Q2_2026 | 22.3% | Percent | RATE | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| regional_slot_handle | Slot handle | Regional | Gaming volume | 3 | Q2_2026 | 11644 | USD millions | PERIOD_FLOW | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| digital_sports_handle | Sports betting handle | Caesars Digital | Gaming volume | 1 | Q2_2026 | 2565 | USD millions | PERIOD_FLOW | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| digital_sports_hold | Sports betting hold | Caesars Digital | Hold rate | 2 | Q2_2026 | 8.4% | Percent | RATE | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| digital_igaming_handle | iGaming handle | Caesars Digital | Gaming volume | 3 | Q2_2026 | 4831 | USD millions | PERIOD_FLOW | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |
| digital_igaming_hold | iGaming hold | Caesars Digital | Hold rate | 4 | Q2_2026 | 3.9% | Percent | RATE | REPORTED | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.20 |

#### T4.17 — Adjusted EBITDA Bridge

<!-- table-id: cp1.adjusted_ebitda_bridge -->

| addback_id | addback_label | addback_classification | realization_status | display_priority | period_id | value | status | source_definition | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|
| noncontrolling_income | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | FY2025 | 65 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| tax_adjustment | (Benefit) provision for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | FY2025 | -11 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| other_income_adjustment | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | FY2025 | -2 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| debt_extinguishment | Loss on extinguishment of debt | OTHER_EXPLICIT | NOT_STATED | 4 | FY2025 | 4 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| interest_expense | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 5 | FY2025 | 2304 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| impairment | Impairment charges | OTHER_EXPLICIT | NOT_STATED | 6 | FY2025 | 182 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| depreciation_amortization | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 7 | FY2025 | 1417 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| transaction_costs | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | FY2025 | 72 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| stock_based_compensation | Stock-based compensation expense | SBC | NOT_STATED | 9 | FY2025 | 95 | REPORTED | Issuer reconciliation from net income attributable to Caesars to Adjusted EBITDA | 698c9482-cc90-4172-88bb-4354b9b56f38 | 10-K p.23 |
| noncontrolling_income | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | Q2_2026 | 21 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| tax_adjustment | (Benefit) provision for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | Q2_2026 | -12 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| other_income_adjustment | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | Q2_2026 | -7 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| interest_expense | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 4 | Q2_2026 | 573 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| depreciation_amortization | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 5 | Q2_2026 | 355 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| transaction_costs | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 6 | Q2_2026 | 29 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| stock_based_compensation | Stock-based compensation expense | SBC | NOT_STATED | 7 | Q2_2026 | 23 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| noncontrolling_income | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | H1_2026 | 36 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| tax_adjustment | (Benefit) provision for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | H1_2026 | null | NOT_REPORTED_AS_NUMERIC | Issuer reconciliation displays a dash; it is retained as null, not zero | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| other_income_adjustment | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | H1_2026 | -5 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| interest_expense | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 4 | H1_2026 | 1142 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| depreciation_amortization | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 5 | H1_2026 | 702 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| transaction_costs | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 6 | H1_2026 | 45 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |
| stock_based_compensation | Stock-based compensation expense | SBC | NOT_STATED | 7 | H1_2026 | 47 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.22 |

#### T4.18 — Debt Facility Register

<!-- table-id: cp1.debt_facility_register -->

| facility_id | facility_name | period_id | facility_type | carrying_value | principal | drawn_amount | commitment | secured_status | seniority | currency | margin_or_coupon | maturity_date | lease_classification | source_id | source_locator |
|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|
| cei_rcf | CEI Revolving Credit Facility | Q2_2026 | Revolving credit facility | 120 | 120 | 120 | 2250 | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | Variable; Term SOFR + 2.25% or Base Rate + 1.25%, subject to terms | 2028-01-31 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.9–10 |
| cei_term_a | CEI Term Loan A | Q2_2026 | Term loan | 618 | 619 | 619 | NOT_APPLICABLE | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | Variable; Term SOFR + 2.25% or Base Rate + 1.25%, subject to terms | 2028-01-31 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.9–10 |
| cva_rcf | CVA Revolving Credit Facility | Q2_2026 | Revolving credit facility | null | null | null | 25 | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | Variable; Term SOFR plus applicable margin | 2029-04-26 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.9–10; no outstanding amount printed as a dash |
| cva_delayed_draw | CVA Delayed Draw Term Loan | Q2_2026 | Delayed draw term loan | 372 | 376 | 376 | 400 | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | Variable; Term SOFR plus applicable margin | 2029-04-26 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp.9–10 |
| cei_term_b | CEI Term Loan B | Q2_2026 | Term loan | 1993 | 2018 | 2018 | NOT_APPLICABLE | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | Variable; Term SOFR + 2.25% or Base Rate + 1.25% | 2030-02-06 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| cei_term_b1 | CEI Term Loan B-1 | Q2_2026 | Term loan | 2808 | 2835 | 2835 | NOT_APPLICABLE | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | Variable; Term SOFR + 2.25% or Base Rate + 1.25% | 2031-02-06 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| cei_ssn_2030 | CEI Senior Secured Notes due 2030 | Q2_2026 | Senior secured notes | 1987 | 2000 | 2000 | NOT_APPLICABLE | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | 7.00% | 2030-02-15 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| cei_ssn_2032 | CEI Senior Secured Notes due 2032 | Q2_2026 | Senior secured notes | 1487 | 1500 | 1500 | NOT_APPLICABLE | SECURED | SENIOR_SECURED_FIRST_LIEN | USD | 6.50% | 2032-02-15 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| cei_sn_2029 | CEI Senior Notes due 2029 | Q2_2026 | Senior unsecured notes | 1193 | 1200 | 1200 | NOT_APPLICABLE | UNSECURED | SENIOR_UNSECURED | USD | 4.625% | 2029-10-15 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| cei_sn_2032 | CEI Senior Notes due 2032 | Q2_2026 | Senior unsecured notes | 1088 | 1100 | 1100 | NOT_APPLICABLE | UNSECURED | SENIOR_UNSECURED | USD | 6.00% | 2032-10-15 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| sid_bonds | Special Improvement District Bonds | Q2_2026 | Bonds | 38 | 38 | 38 | NOT_APPLICABLE | NOT_STATED | NOT_STATED | USD | 4.30% | 2037 | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |
| other_notes_payables | Long-term notes and other payables | Q2_2026 | Other debt / payables | 1 | 1 | 1 | NOT_APPLICABLE | NOT_STATED | NOT_STATED | USD | Not stated | Not stated | NOT_APPLICABLE | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p.9 |

#### T4.19 — Model Reconciliation Register

<!-- table-id: cp1.model_reconciliation_register -->

| check_id | period_id | check_type | reported_value | calculated_value | difference | tolerance | status | explanation | source_refs |
|---|---|---|---:|---:|---:|---:|---|---|---|
| rev_q2_2026 | Q2_2026 | Segment revenue to reported revenue | 2993 | 2993 | 0 | 0 | PASS | 1,017 + 1,570 + 351 + 57 − 2 equals reported consolidated revenue. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q pp.2,11 |
| rev_h1_2026 | H1_2026 | Segment revenue to reported revenue | 5863 | 5863 | 0 | 0 | PASS | 2,020 + 3,000 + 725 + 123 − 5 equals reported consolidated revenue. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q pp.2,11 |
| rev_fy2025 | FY2025 | Segment revenue to reported revenue | 11486 | 11486 | 0 | 0 | PASS | 4,049 + 5,756 + 1,408 + 279 − 6 equals reported consolidated revenue. | 698c9482-cc90-4172-88bb-4354b9b56f38 10-K p.19 |
| ebitda_q2_2026 | Q2_2026 | Adjusted EBITDA bridge | 920 | 920 | 0 | 0 | PASS | Issuer reconciliation; its displayed components sum to issuer-reported Adjusted EBITDA. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q p.22 |
| ebitda_h1_2026 | H1_2026 | Adjusted EBITDA bridge | 1807 | 1807 | 0 | 0 | WARN | Issuer reports the bridge and total; tax adjustment is displayed as a dash and retained null rather than presumed zero. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q p.22 |
| ebitda_fy2025 | FY2025 | Adjusted EBITDA bridge | 3624 | 3624 | 0 | 0 | PASS | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA. | 698c9482-cc90-4172-88bb-4354b9b56f38 10-K p.23 |
| debt_q2_2026 | Q2_2026 | Debt total / balance-sheet carrying value | 11705 | 11699 | 6 | 0 | WARN | Note book total differs from current plus long-term balance-sheet debt; conflict CF-1 remains open. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q pp.2,9 |
| debt_fy2025 | FY2025 | Debt total / balance-sheet carrying value | 11792 | 11784 | 8 | 0 | WARN | Note book total differs from current plus long-term balance-sheet debt; conflict CF-1 remains open. | 698c9482-cc90-4172-88bb-4354b9b56f38 10-K pp.29,40 |
| cfo_identity_h1_2026 | H1_2026 | CFO identity | 675 | 675 | 0 | 0 | PASS | Directly reported CFO; not a derived FCF measure. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q p.4 |
| ncf_h1_2026 | H1_2026 | Net cash change identity | 93 | 93 | 0 | 0 | PASS | CFO 675 plus investing cash flow (411) plus financing cash flow (171) equals reported increase 93. | 743e5d19-d65d-4487-8114-c0614dfc076d 10-Q p.4 |
| fy2025_quarter_sum | FY2025 | Reported FY to quarterly sum | 3624 | null | null | 0 | WARN | Complete four discrete quarterly Adjusted EBITDA values are not available in the delivered evidence. | 698c9482-cc90-4172-88bb-4354b9b56f38 10-K p.23 |

<!-- table-id: cp1.downstream_readiness -->

| downstream_module | status | missing_metric_ids | conflict_refs | explanation |
|---|---|---|---|---|
| CP-MODEL | blocked | complete_four_quarters; quarterly_facility_carrying_values; reconciled_total_debt | CF-1 | Interface tables are emitted, but fewer than four discrete quarters are available and debt reconciliation remains WARN; workbook readiness criteria are not met. |

## Evidence Trace

| Claim or register coverage | Citation | Document | Page |
|---|---|---|---:|
| Reporting period and current filing identity | [C1] | Q2 2026 Form 10-Q | 1 |
| T4.4 reported revenue and comparative periods | [C2] | Q2 2026 Form 10-Q | 2 |
| T4.4 operating income | [C3] | Q2 2026 Form 10-Q | 3 |
| T4.4 and T4.10 Adjusted EBITDA | [C4] | Q2 2026 Form 10-Q | 16 |
| T4.6 cash and equivalents | [C5] | Q2 2026 Form 10-Q | 2 |
| Debt-note book and face values; T4.11 CF-1 | [C6] | Q2 2026 Form 10-Q | 9 |
| H1 cash flow and T4.5 CFO | [C7] | Q2 2026 Form 10-Q | 4 |
| H1 cash interest paid | [C8] | Q2 2026 Form 10-Q | 5 |
| Customer deposit/deferred revenue movement | [C9] | Q2 2026 Form 10-Q | 11 |
| Subsequent Alberta event | [C10] | Q2 2026 Form 10-Q | 17 |
| Issuer Adjusted EBITDA definition limitation | [C11] | Q2 2026 Form 10-Q | 21 |
| T4.4/T4.10 FY2023–FY2025 segment revenue | [C12] | FY2025 Form 10-K | 19 |
| T4.10 annual Adjusted EBITDA | [C13] | FY2025 Form 10-K | 19 |
| T4.6 FY2025/FY2024 current debt | [C14] | FY2025 Form 10-K | 29 |
| T4.6 FY2025/FY2024 long-term debt | [C15] | FY2025 Form 10-K | 29 |
| T4.5 annual CFO | [C16] | FY2025 Form 10-K | 31 |
| Q2 aggregate liquidity | [C17] | Q2 2026 Form 10-Q | 22 |
| Merger commitment-letter existence; terms limitation | [C18] | Merger Agreement Form 8-K | 2 |
| Debt facility schedule and CEI Term Loan A terms | [C19] | Q2 2026 Form 10-Q | 9–10 |
| Contract-liability period-end balances | [C20] | Q2 2026 Form 10-Q | 11 |
| Q2 covenant-compliance statement | [C21] | Q2 2026 Form 10-Q | 23 |
| Annual PP&E purchases | [C22] | FY2025 Form 10-K | 31 |
| H1 PP&E purchases | [C23] | Q2 2026 Form 10-Q | 4 |
| Quarterly segment detail and revenue reconciliation | [C24] | Q2 2026 Form 10-Q | 11 |
| Cash balance and total-liquidity presentation | [C5, C17] | Q2 2026 Form 10-Q | 2, 22 |

## Source Registry

| Source ID | Source file | Use in this handoff | Evidence locator basis |
|---|---|---|---|
| 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | Current interim statements, debt, liquidity, segments, operating KPIs and subsequent event | Delivered evidence pages 1–26 |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | Audited annual financial statements, debt, cash flows, segments and definitions | Delivered evidence pages 19–57 |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | CZR_2026_Merger_Agreement_8K.txt | Merger chronology and filed financing-commitment narrative | Delivered evidence pages 1–3 |
| 6eb3eaa6-a948-486f-a6dd-4354b9b56f38 | CZR_2026_Merger_Press_Release.txt | Context for announced proposed transaction; not blended into period data | Delivered evidence pages 1–2 |

## Gaps & Conflicts

The principal canonical-definition issue is the debt basis: balance-sheet current plus long-term debt does not equal the debt-note book-value total in either Q2 2026 or FY2025. CP-1 retains each value, uses the balance-sheet carrying sum for canonical Total Debt and carries the discrepancy as CF-1; it is not silently reconciled [C6, C14, C15]. Issuer Adjusted EBITDA remains distinct from GAAP EBITDA and covenant EBITDA [C11].

H1 CFO, cash interest, cash taxes and capex inputs are directly reported, but FCF, LTM and leverage/coverage calculations are not populated because their deterministic computation was unavailable. Nulls in the tagged registers are itemized in T4.12; untagged dashes in T4.4–T4.6 are unavailable, not zero. Customer deposits and deferred revenue are operating float and must remain separate from debt [C9].

The proposed merger is a Q2-period transaction; the 8-K records that financing commitments were delivered but does not provide their full terms in the evidence delivered here [C18]. The Alberta launch is post-period and is excluded from Q2 results [C10]. CP-MODEL is not ready because the delivered historical set does not provide four complete discrete quarters and a reconciled facility history.

## QA Validation

- **Identity and lineage:** PASS — CP-1, CZR, Q2 2026, analysis date and accepted CP-0 lineage match the supplied invocation context.
- **Source gate and evidence trace:** PASS WITH LIMITATIONS — primary audited annual and unaudited interim financial sources are present; transaction financing terms remain incomplete.
- **Register inventory:** PASS — required registers T4.1–T4.6 and T4.8–T4.19 are present; retired T4.7 is omitted; stable CP-MODEL interface tables are tagged once.
- **Null discipline:** PASS WITH LIMITATIONS — tagged value-bearing nulls are recorded in T4.12; unavailable untagged financial values are rendered as dashes and described in the gap ledger.
- **Debt and definition conflicts:** RESTRICTED — CF-1 is preserved; no silent reconciliation or covenant-capacity inference is made.
- **Analytical separation:** PASS WITH LIMITATIONS — source data, issuer non-GAAP measures, calculations, and analyst judgement are distinguished; subsequent Alberta event is not blended into Q2.
- **Confidence and QA status:** RESTRICTED — confidence score 44, Low band; material coverage and definition limitations cap status at Restricted.
- **Downstream readiness:** RESTRICTED — analytical consumers may proceed with stated limitations; CP-MODEL is blocked pending four-quarter history and reconciliation inputs.
- **Host validation:** Pending after this response. No host validator or completeness-check result is asserted.