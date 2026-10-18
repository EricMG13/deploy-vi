---
module_id: "CP-1"
module_name: "CanonicalDataFoundation"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1-f5866e9d304a4e59"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-02-CP-1"
credit_os_invocation_sha256: "b590d0964ed2a3ac2478fedef4785459adb0da554693bd935a3085889ee8dd25"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
confidence_score: 59
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [INTERIM_UNAUDITED, QUARTERLY_CASH_FLOW_NOT_REPORTED, COVENANT_EBITDA_NOT_DISCLOSED, FOUR_QUARTER_MODEL_HISTORY_MISSING, MERGER_FINANCING_NOT_PROVIDED]
validation_warnings: [DEBT_BASIS_CONFLICT, CASH_INTEREST_EXCLUDES_RENT_IF_UNQUALIFIED, RELEASE_NET_LOSS_LABEL_CONFLICT, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-1B, CP-1C, CP-2, CP-2A, CP-2D, CP-2G, CP-2H, CP-3, CP-3C, CP-4, CP-4A, CP-5, CP-5A, CP-MODEL]
---

## Audit Summary

**Canonical filename:** `CZR_CP-1_20261002.md`. Owned object: canonical financial data and KPIs. The accepted CP-0 handoff matches CZR, Q2 2026, run ID and the pinned hash. Financial-source gate passes: audited FY2025 filing, unaudited June 2026 filing and corroborating issuer release. [C1, C2] **Self-assessed confidence: 59/100, Low; Restricted; Requires More Work.** The material limitations are the lack of four discrete quarters for model export, unavailable contractual EBITDA/headroom and pending-merger financing. No host validation result is asserted.

## Analysis

### Analytical read-through

CZR's first-half 2026 revenue rose to $5,863 million from $5,701 million, but Adjusted EBITDA fell to $1,807 million from $1,839 million; operating cash flow was nearly unchanged at $675 million versus $680 million. [C3, C5, C15] Lower capex improved first-half after-capex cash generation, while substantial rent-related financing-obligation payments remain outside Adjusted EBITDA. [C6, C39] At June 30, balance-sheet debt carrying value was $11,699 million, not the $11,807 million face-value debt disclosed in the debt note. [C11, C12] [Analyst Judgement] This foundation permits definition-controlled liquidity and debt analysis, not a contractual leverage or security recommendation. The pending merger creates a financing question, not a June 30 pro forma adjustment; only its announcement, not closing, falls within Q2. [C18, C23]

### Largest changes and creditor transmission

The table compares sourced period values and explicitly calculated amounts from T4.8–T4.10; all amounts are USD millions unless labelled otherwise. The fall in earnings despite revenue growth matters because fixed financing and rent cash needs do not decline automatically. [C3, C15, C39]

| Key financial changes | Latest | Comparator | Change | Definition | Creditor consequence |
|---|---:|---:|---:|---|---|
| H1 revenue | 5,863 | 5,701 | +162 | Reported | Growth did not protect EBITDA |
| H1 Adjusted EBITDA | 1,807 | 1,839 | −32 | Issuer non-GAAP | Weaker fixed-charge cushion |
| H1 operating cash flow | 675 | 680 | −5 | Reported, after cash interest | Limited underlying cash growth |
| H1 capex cash outflow | 335 | 453 | −118 | Property/equipment purchases | Supports near-term cash retention |
| H1 FCF after capex | 340 | 227 | +113 | CFO less cash capex | Excludes acquisition and financing uses |
| June debt carrying value | 11,699 | 11,784 | −85 | Current plus long-term BS debt | Modest debt reduction |
| June unrestricted cash | 965 | 887 | +78 | Excludes restricted cash | Larger immediate buffer |
| LTM Adjusted EBITDA | 3,592 | FY2025: 3,624 | −32 | FY + H1 − prior H1 | Denominator weakened |

**Cash-flow quality and downside.** [Calculated] First-half FCF of $340 million reflects CFO $675 million less property/equipment purchases $335 million; FY2025 comparable FCF was $497 million and constructed LTM FCF $610 million. These exclude the separate $98 million first-half asset-acquisition cash outflow. [C5–C8] [Analyst Judgement] Lower capex is the strongest contrary evidence to an immediate cash squeeze; it would prevail if durable CFO and recurring maintenance needs remain covered without deferring necessary renovations. The downside sequence is softer Las Vegas leisure demand and hold, then EBITDA erosion, then reduced cash available after lease payments, then greater refinancing dependence. Las Vegas Q2 table-game hold fell to 16.6% from 21.1%; monitor subsequent hold, visitation, CFO and revolver drawings rather than extrapolate one quarter. [C30]

**Debt, rent and liquidity.** [Calculated] June carrying-value debt of $11,699 million less unrestricted cash $965 million gives net debt $10,734 million; dividing by constructed LTM Adjusted EBITDA of $3,592 million gives **3.00x on an explicitly non-contractual, issuer-Adjusted-EBITDA basis**. Cash interest paid on debt alone understates fixed cash costs: first-half debt interest was $368 million and GLPI/VICI rent-related interest $686 million. [C9, C39] [Analyst Judgement] Reported $2,928 million cash-plus-available-capacity is a liquidity resource, not excess cash: remaining-2026 estimated debt service $425 million, VICI/GLPI payments $687 million and capex $310–390 million compete for it. Revolver availability is conditional on governing terms. [C14, C21, C22, C41]

**Funding float and period control.** Customer deposits and other deferred revenue rose from $492 million at December 2025 to $545 million at June 2026. Together with chips and rewards, the three disclosed obligations rose from $620 million to $678 million. [C17, C36] [Analyst Judgement] Customer prepayments provide temporary non-debt funding but must support wagering settlements or future service; withdrawals or slower new deposits could turn apparent liquidity into a cash call. This is not trade-payables financing. Caesars Windsor moved from managed fees to consolidated Regional operations on March 3, complicating like-for-like growth; no unsourced pro forma adjustment is made. [C19]

**Definition and subsequent-event controls.** The release calls $62 million a GAAP net loss; the filing identifies $62 million as loss **attributable to Caesars**, versus consolidated net loss $41 million. The filing's labels control the respective metrics; both remain visible in CF-3. [C26, C27] June debt-note book debt is $11,705 million; current plus long-term balance-sheet debt is $11,699 million after the separately shown $6 million revolver-financing-charge difference. The $11,807 million figure is principal, not canonical debt. [C11–C13] Contractual leverage headroom is **Not Calculable from Provided Materials** because the covenant EBITDA/netting and required testing inputs are absent, even though compliance is reported. [C28, C42] The July 13 Alberta launch is a flagged **subsequent event** excluded from June financials. [C20]

### Analytical appendix — complete canonical registers

All financial amounts below use USD millions, consolidated US GAAP unless a row explicitly says percentage or count. FY2025 is audited; interim figures are unaudited. `S1` identifies the FY2025 10-K, `S2` the Q2 2026 10-Q, `S3` the issuer's Q2 release. A calculated row is not an issuer-reported cash-flow statement.

#### T4.1 — Source Register
| Source File Name | Document Type | Period Coverage | Currency | Unit | Perimeter | Accounting Basis | Evidence Quality Tier | Analytical Use | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| S1 · CZR_FY2025_10K.txt | SEC 10-K | FY2025; FY2024/2023 flow comparatives | USD | Millions | Caesars consolidated | US GAAP | Tier 1 audited | Annual base, balance sheet, debt, leases [C1, C4, C7, C8] | Extracted text; original layout not independently inspected |
| S2 · CZR_Q2_2026_10Q.txt | SEC 10-Q | Q2 and H1 2026/2025; June/December balances | USD | Millions | Caesars consolidated | US GAAP | Tier 2b unaudited | Primary current-period statements, debt and segments [C2, C3, C5, C11] | Q2 cash-flow statement not separately supplied; no completed merger financing |
| S3 · CZR_Q2_2026_Earnings_Release.txt | Issuer release | Q2 and H1 2026/2025 | USD | Millions | Caesars consolidated | GAAP and non-GAAP | Tier 2c issuer | Corroboration and release-label comparison [C26] | GAAP-net-loss headline is ambiguous against filing |

#### T4.2 — Entity Period Key
| Entity Name | Entity Role | Fiscal Year End | Reporting Currency | Reporting Unit | Consolidation Perimeter | Accounting Basis | Available Periods |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. and consolidated subsidiaries | SEC registrant and canonical issuer | December 31 | USD | Millions | Consolidated, including consolidated Caesars Virginia venture and, from March 3, Caesars Windsor | US GAAP | FY2025; Q2/H1 2026 and 2025; December 2025 and June 2026 BS [C1, C2, C19] |
| Caesars Virginia, LLC | Consolidated venture and separate facility borrower | December 31 | USD | Millions | Included in consolidated figures; 50% interest with noncontrolling partner | US GAAP | FY2025 and H1 2026, without standalone full statements [C11] |
| Caesars Windsor | Operationally consolidated from March 3, 2026 | December 31 | USD | Millions | Regional segment after acquisition of operations; previously Managed and Branded | US GAAP | Partial H1 2026 [C19] |

**Subsequent-events warning:** the Alberta mobile launch on July 13, 2026 postdates the June 30 balance sheet and has no sourced June pro forma financial amount. The May 27 merger agreement predates June 30, but completion remains conditional; hypothetical closing debt and cash are excluded. [C18, C20]

#### T4.3 — Normalization Register
| Description | Source | Type | Before | After | Rationale | Periods |
|---|---|---|---|---|---|---|
| Presentation basis | S1/S2 statements [C1, C2] | Unit/perimeter alignment | USD millions; consolidated | USD millions; consolidated | No FX conversion or entity substitution | All |
| Debt basis CF-1 | S2 BS and Note 6 [C11–C13] | Definition selection | June principal 11,807; note book 11,705 | BS current 114 + long-term 11,585 = 11,699 | Canonical net-carrying debt excludes separate 6 deferred revolver charges | June 2026 |
| Cash capex sign | S1/S2 cash flows [C6, C8] | Sign normalization | Purchases (805), (335), (453) | Outflows −805, −335, −453; positive magnitudes in FCF formulas | Preserve financing cash-flow convention | FY2025; H1 2026/2025 |
| Non-GAAP EBITDA retained separately | S1/S2 bridges [C15, C16, C23] | Definition separation | Issuer Adjusted EBITDA | Separate from calculated EBIT plus D&A | Does not imply covenant EBITDA | FY2025; Q2/H1 2026/2025 |

#### T4.4 — Normalized Income Statement
| Line Item | FY2025 | H1 2026 | H1 2025 | Q2 2026 | Q2 2025 |
|---|---:|---:|---:|---:|---:|
| Casino revenue | 6,617 | 3,425 | 3,262 | 1,759 | 1,668 |
| Food and beverage revenue | 1,714 | 850 | 863 | 426 | 428 |
| Hotel revenue | 1,945 | 982 | 991 | 495 | 509 |
| Other revenue | 1,210 | 606 | 585 | 313 | 302 |
| Total revenue | 11,486 | 5,863 | 5,701 | 2,993 | 2,907 |
| Casino expense | 3,602 | 1,857 | 1,748 | 955 | 887 |
| Food and beverage expense | 1,106 | 555 | 550 | 281 | 275 |
| Hotel expense | 615 | 319 | 306 | 163 | 155 |
| Other direct expense | 420 | 190 | 200 | 95 | 105 |
| General and administrative | 1,926 | 1,025 | 960 | 521 | 477 |
| Corporate expense | 322 | 182 | 166 | 94 | 84 |
| Impairment | 182 | — | — | — | — |
| Depreciation and amortization | 1,417 | 702 | 721 | 355 | 364 |
| Transaction and other costs, net | 38 | 20 | 36 | 16 | 34 |
| Total operating expenses | 9,628 | 4,850 | 4,687 | 2,480 | 2,381 |
| Operating income / EBIT | 1,858 | 1,013 | 1,014 | 513 | 526 |
| EBITDA, calculated EBIT + D&A | 3,275 | 1,715 | 1,735 | 868 | 890 |
| Adjusted EBITDA, issuer | 3,624 | 1,807 | 1,839 | 920 | 955 |
| Interest expense, net | 2,304 | 1,142 | 1,153 | 573 | 579 |
| Loss before income taxes | −448 | −124 | −139 | −53 | −52 |
| Income tax benefit / (expense) | 11 | 0 | −24 | 12 | −13 |
| Consolidated net income / (loss) | −437 | −124 | −163 | −41 | −65 |
| Net income / (loss) attributable to Caesars | −502 | −160 | −197 | −62 | −82 |
| Stock-based compensation | 95 | 47 | 50 | 23 | 24 |

Source: S1 statements pp.57–58 and EBITDA bridge pp.43–44; S2 statements pp.3–4 and bridge pp.27–28. [C3, C4, C15, C16, C27, C37] `—` means not separately presented, not zero; COGS/gross profit are not presented for the diversified consolidated business (G-1). Positive expenses above display statement magnitudes, except tax-benefit/(expense) and income lines.

#### T4.5 — Normalized Cash Flow Statement
| Line Item | FY2025 | H1 2026 | H1 2025 | LTM June 2026 |
|---|---:|---:|---:|---:|
| Net cash provided by operating activities / CFO | 1,302 | 675 | 680 | 1,297 |
| Depreciation and amortization cash-flow add-back | 1,417 | 702 | 721 | 1,398 |
| Stock-based compensation cash-flow add-back | 95 | 47 | 50 | 92 |
| Receivables movement | −53 | −24 | −37 | −40 |
| Prepaid and other asset movement | −49 | −88 | −47 | −90 |
| Income tax receivable/payable movement | −81 | −11 | −58 | −34 |
| Payables, accruals and other liabilities movement | −18 | 52 | 61 | −27 |
| Operating asset/liability movement, calculated | −201 | −71 | −81 | −191 |
| Property/equipment purchases / cash capex | −805 | −335 | −453 | −687 |
| Cash paid for asset acquisitions | — | −98 | — | — |
| Net investing cash flow | −571 | −411 | −434 | −548 |
| Debt and revolver proceeds | 1,580 | 885 | 590 | 1,875 |
| Debt and revolver repayments | −1,969 | −983 | −612 | −2,340 |
| Net debt issuance/(repayment), calculated | −389 | −98 | −22 | −465 |
| Common-stock repurchase | −229 | 0 | −100 | −129 |
| Noncontrolling-interest distributions | −102 | −41 | −30 | −113 |
| Net financing cash flow | −763 | −171 | −176 | −758 |
| Net change cash including restricted | −32 | 93 | 70 | −9 |
| Cash interest paid for debt | −813 | −368 | −405 | −776 |
| Cash interest paid on rent/GLPI-VICI financing obligations | −1,349 | −686 | −672 | −1,363 |
| Cash taxes paid, net | −81 | −11 | −58 | −34 |
| FCF, CFO less cash property/equipment capex [Calculated] | 497 | 340 | 227 | 610 |

Source: S1 cash flows pp.60–61 and S2 pp.7–8. [C5–C10, C32, C39, C40] LTM columns are constructed, not a filed statement. H1 2025 asset-acquisition cash was not separately stated; that absence does not establish zero. Maintenance/growth splits for historical cash capex are not supplied (G-2). Cash interest lines are cash outflows, not additional deductions from already-after-interest CFO.

#### T4.6 — Normalized Balance Sheet
| Line Item | June 2026 | December 2025 |
|---|---:|---:|
| Cash and cash equivalents | 965 | 887 |
| Restricted cash, current | 96 | 85 |
| Accounts receivable, net | 485 | 476 |
| Inventories | 49 | 43 |
| Prepayments and other current assets | 382 | 312 |
| Total current assets | 1,977 | 1,803 |
| Investments in unconsolidated affiliates | 124 | 133 |
| Property and equipment, net | 14,125 | 14,358 |
| Goodwill | 10,441 | 10,441 |
| Intangible assets other than goodwill | 3,959 | 3,985 |
| Deferred tax asset | 68 | 67 |
| Other long-term assets | 1,048 | 852 |
| Total assets | 31,742 | 31,639 |
| Accounts payable | 290 | 297 |
| Accrued interest | 222 | 224 |
| Accrued other liabilities | 1,696 | 1,618 |
| Current portion of long-term debt | 114 | 114 |
| Total current liabilities | 2,322 | 2,253 |
| Long-term financing obligations, separately classified | 13,157 | 13,096 |
| Long-term debt, net | 11,585 | 11,670 |
| Canonical total debt, current + long-term [Calculated] | 11,699 | 11,784 |
| Deferred tax liability | 57 | 58 |
| Other long-term liabilities | 1,069 | 876 |
| Total liabilities | 28,190 | 27,953 |
| Caesars stockholders' equity | 3,375 | 3,504 |
| Noncontrolling interests | 177 | 182 |
| Total equity | 3,552 | 3,686 |
| Customer deposits and other deferred revenue, note balance | 545 | 492 |
| Caesars Rewards obligation, note balance | 92 | 89 |
| Outstanding chips, note balance | 41 | 39 |

Source: S2 balance sheet p.2 and revenue Note 7 pp.19–20; S1 balance sheet p.56 and Note 10. [C11, C17, C35, C36] Note-level contract liabilities may include current and long-term amounts; the three note balances must **not** be added again to accrued liabilities. The separately presented financing obligations are not folded into canonical debt. [C24]

#### T4.8 — Constructed Period Register
| Metric Name | Derived Period Type | Full-Year Component | Current Stub | Prior-Year Stub | Derived Value | Calculation Status | Source Files | Limitations |
|---|---|---:|---:|---:|---:|---|---|---|
| Revenue | LTM June 2026 | 11,486 | 5,863 | 5,701 | 11,648 | Calculated | S1 p.57; S2 p.3 [C3, C4] | Windsor creates perimeter/comparability change |
| Issuer Adjusted EBITDA | LTM June 2026 | 3,624 | 1,807 | 1,839 | 3,592 | Calculated | S1 p.44; S2 p.28 [C15, C16] | Not contractual EBITDA |
| EBIT | LTM June 2026 | 1,858 | 1,013 | 1,014 | 1,857 | Calculated | S1 p.57; S2 p.3 [C37, C38] | Operating-income basis |
| D&A | LTM June 2026 | 1,417 | 702 | 721 | 1,398 | Calculated | S1 p.57; S2 p.3 [C3] | Reported expense |
| EBITDA, EBIT + D&A | LTM June 2026 | 3,275 | 1,715 | 1,735 | 3,255 | Calculated | S1/S2 statements [C3, C37, C38] | Not issuer-adjusted |
| CFO | LTM June 2026 | 1,302 | 675 | 680 | 1,297 | Calculated | S1 p.60; S2 p.7 [C5, C7] | Already after operating cash interest |
| Cash capex magnitude | LTM June 2026 | 805 | 335 | 453 | 687 | Calculated | S1 p.60; S2 p.7 [C6, C8] | Does not include asset purchases |
| FCF | LTM June 2026 | 497 | 340 | 227 | 610 | Calculated | CFO/capex rows [C5–C8] | CFO minus cash property/equipment capex |
| Debt cash interest magnitude | LTM June 2026 | 813 | 368 | 405 | 776 | Calculated | S1 p.61; S2 p.8 [C9, C40] | Excludes rent-financing interest |
| Rent-financing cash interest magnitude | LTM June 2026 | 1,349 | 686 | 672 | 1,363 | Calculated | S1 p.61; S2 p.8 [C10, C39] | FY line covers financing obligations; H1 specifies GLPI/VICI |

#### T4.9 — Calculation Register
| Metric Name | Formula | Numerator Value | Numerator Source | Denominator Value | Denominator Source | Period | Currency | Unit | Calculated Value | Calculation Status | Evidence Quality Tier | Limitations |
|---|---|---:|---|---:|---|---|---|---|---:|---|---|---|
| Canonical total debt | Current + long-term | 114 | S2 BS p.2 [C11] | 11,585 | S2 BS p.2 [C11] | June 2026 | USD | Millions | 11,699 | Calculated | 2b | Excludes separately classified lease/financing obligations |
| Net debt | Debt − unrestricted cash | 11,699 | T4.6 [C11] | 965 | S2 BS p.2 [C14] | June 2026 | USD | Millions | 10,734 | Calculated | 2b | Restricted cash excluded |
| LTM debt/issuer Adjusted EBITDA | Debt ÷ LTM adjusted EBITDA | 11,699 | T4.6 [C11] | 3,592 | T4.8 [C15, C16] | LTM June 2026 | USD | x | 3.2570 | Calculated | Mixed 1/2b | Not covenant leverage; excludes financing obligations |
| LTM net debt/issuer Adjusted EBITDA | Net debt ÷ LTM adjusted EBITDA | 10,734 | T4.6/T4.9 [C11, C14] | 3,592 | T4.8 [C15, C16] | LTM June 2026 | USD | x | 2.9883 | Calculated | Mixed 1/2b | Not covenant leverage |
| FCF | CFO − capex magnitude | 675 | S2 cash flow [C5] | 335 | S2 cash flow [C6] | H1 2026 | USD | Millions | 340 | Calculated | 2b | CFO includes cash interest and taxes |
| LTM FCF conversion | FCF ÷ adjusted EBITDA | 610 | T4.8 [C5–C8] | 3,592 | T4.8 [C15, C16] | LTM June 2026 | USD | % | 16.98% | Calculated | Mixed 1/2b | Before acquisition cash and debt maturities |
| Liquidity | Cash + available revolvers | 965 | S2 liquidity [C14] | 1,963 | S2 liquidity p.39 [C14] | June 2026 | USD | Millions | 2,928 | Calculated | 2b | Revolver conditional; excludes restricted cash |
| Liquidity/debt | Liquidity ÷ BS debt | 2,928 | S2 liquidity [C14] | 11,699 | T4.6 [C11] | June 2026 | USD | % | 25.03% | Calculated | 2b | Liquidity not excess cash |
| LTM adjusted EBITDA / debt cash interest | Adjusted EBITDA ÷ cash interest | 3,592 | T4.8 [C15, C16] | 776 | T4.8 [C9, C40] | LTM June 2026 | USD | x | 4.629 | Calculated | Mixed 1/2b | Excludes rent interest; not fixed-charge coverage |
| LTM adjusted EBITDA / combined debt and rent-financing cash interest | Adjusted EBITDA ÷ (776 + 1,363) | 3,592 | T4.8 [C15, C16] | 2,139 | T4.8 [C9, C10, C39, C40] | LTM June 2026 | USD | x | 1.6793 | Calculated | Mixed 1/2b | Rent scope differs slightly across source labels; not covenant coverage |
| H1 adjusted EBITDA margin | Adjusted EBITDA ÷ revenue | 1,807 | S2 bridge [C15] | 5,863 | S2 IS [C3] | H1 2026 | USD | % | 30.82% | Calculated | 2b | Non-GAAP numerator |
| H1 revenue growth | Current ÷ prior − 1 | 5,863 | S2 IS [C3] | 5,701 | S2 IS [C3] | H1 2026 | USD | % | 2.84% | Calculated | 2b | Windsor perimeter change |
| H1 Adjusted EBITDA growth | Current ÷ prior − 1 | 1,807 | S2 bridge [C15] | 1,839 | S2 bridge [C15] | H1 2026 | USD | % | −1.74% | Calculated | 2b | Issuer-adjusted measure |
| Covenant headroom | Tested covenant numerator and denominator | — | Contract definition not supplied [C23, C42] | — | Contract testing inputs not supplied [C23, C42] | June 2026 | USD | x | — | Not Calculable | 2b | Reported compliance does not state numerical headroom |

#### T4.10 — KPI Dashboard
| KPI Category | Metric Name | FY2025 | H1 2026 | H1 2025 | Q2 2026 | Q2 2025 | Trend Direction | Analyst Note |
|---|---|---:|---:|---:|---:|---:|---|---|
| Earnings | Issuer Adjusted EBITDA, USD m | 3,624 | 1,807 | 1,839 | 920 | 955 | Down YoY | Excludes financing-obligation interest [C15, C16, C23] |
| Earnings | Issuer reported Adjusted EBITDA margin | 31.6% | 30.8% | 32.3% | 30.7% | 32.9% | Down YoY | Source-reported rounding [C15, C16] |
| Earnings | Calculated EBITDA, EBIT + D&A, USD m | 3,275 | 1,715 | 1,735 | 868 | 890 | Down YoY | Not the issuer's Adjusted EBITDA [C3, C37, C38] |
| Cash | CFO, USD m | 1,302 | 675 | 680 | — | — | Flat YoY | Separate Q2 cash-flow figures absent [C5, C7] |
| Cash | CFO less property/equipment capex, USD m | 497 | 340 | 227 | — | — | Up YoY | Capex reduction is principal driver [C5–C8] |
| Gaming | Las Vegas table-game hold | 19.9% | 17.5% | 20.1% | 16.6% | 21.1% | Down YoY | Hold variation contributes to EBITDA risk [C30] |
| Gaming | Caesars Digital iGaming handle, USD m | 19,025 | 10,205 | 9,193 | 4,831 | 4,705 | Up YoY | Does not itself represent revenue [C31] |
| Liquidity | Available cash plus revolver, USD m | — | 2,928 at June 30 | — | — | — | Snapshot | Conditional facility availability [C14] |

#### T4.11 — Definition Conflict Register
| Metric Name | Canonical Definition | Issuer-Reported Definition | Source of Conflict | Periods Affected | Materiality | Downstream Modules Affected | Resolution / Recommendation |
|---|---|---|---|---|---|---|---|
| CF-1 debt carrying vs principal | BS current + long-term debt, net: June 11,699; December 11,784 | Debt note principal June 11,807 and December 11,905; debt-note book June 11,705 and December 11,792; deferred revolver charges −6/−8 outside note book | S2 BS p.2 and Note 6 p.16; S1 Note 9 [C11–C13, C33] | June 2026; December 2025 | June face exceeds canonical by 108; December by 121; June note book exceeds canonical by 6 | CP-2, CP-3, CP-3C, CP-MODEL | Use 11,699/11,784 for canonical debt; keep face, note book and financing-charge roles separate |
| CF-2 Adjusted EBITDA | Calculated EBIT + D&A separately from issuer adjustment | Issuer adds transaction/other, SBC, interest, tax, impairment and other bridge items; expressly disclaims alignment with debt/lease definitions | S1/S2 bridges [C15, C16, C23, C35] | FY2025; H1/Q2 2026/2025 | LTM issuer adjusted 3,592 versus calculated EBITDA 3,255: difference 337 | CP-2, CP-4, CP-4A | Label every adjusted-basis ratio non-contractual; obtain covenant definition and testing inputs |
| CF-3 consolidated vs attributable net loss | Distinguish consolidated loss from parent-attributable loss | Release headlines GAAP net loss 62 for Q2; filing consolidated loss 41, loss attributable to Caesars 62 | S3 p.1 vs S2 statement p.3 [C26, C27] | Q2 2026 and comparative | Q2 2026 difference 21, equal to noncontrolling income | CP-2, CP-2D, CP-1C | Retain both filing measures and qualify release headline |
| CF-4 interest and rent cash | Debt cash interest and lease-financing cash interest separately, with combined coverage labelled | H1 debt cash interest 368, GLPI/VICI rent interest 686; FY debt 813 and financing-obligation rent interest 1,349 | S2 cash supplemental p.8; S1 p.61 [C9, C10, C39, C40] | FY2025; H1 2026/2025; LTM | LTM debt-only 776 versus combined 2,139 | CP-2, CP-2A, CP-4 | Present both denominators, never treat Adjusted EBITDA as after rent |
| CF-5 segment perimeter | Preserve source segment and reporting dates | Windsor management fees formerly Managed and Branded, operations Regional from March 3 | S2 Note 1 [C19] | H1/Q2 2026 vs 2025 | No separately sourced pro forma EBITDA adjustment | CP-1C, CP-2G, CP-MODEL | Preserve reported comparison; seek like-for-like schedule before attributing all growth organically |

#### T4.12 — Gaps & Warnings
| Gap Description | Affected Line Item or Metric | Affected Period(s) | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|---|
| G-1 consolidated gross profit/COGS not stated as one GAAP total | T4.4 gross profit; gross-margin KPI | All | Gross margin not calculable | Minor | Retain source expense categories; do not aggregate an unsupported gross-profit definition |
| G-2 cash capex maintenance/growth split not disclosed historically | T4.5 cash capex components | FY2025, H1 | Sustainment FCF uncertain | Material | Obtain project-level cash capex split; estimates for remaining 2026 are not actuals |
| G-3 no discrete Q1, Q3, Q4 full selected history and no separate Q2 CFS | Model quarterly history and Q2 cash KPIs | 2025–26 | CP-MODEL blocked; Q2 FCF null | Material | Supply Q1/Q3/Q4 filings or valid components |
| G-4 contractual adjusted EBITDA, netting and actual covenant test values absent | Covenant headroom | June 2026 | CP-4A cannot calculate headroom | Material | Obtain applicable definitions and actual compliance certificates; do not infer from reported compliance |
| G-5 merger closing financing and full agreement unavailable in delivered financial source set | Post-closing debt, cash, maturity | After June 2026 | Merger scenario cannot be populated | Material | Supply executed agreement, financing commitments and amendments before pro forma work |
| G-6 restricted and trapped-cash distribution by debtor not given | Debtor-specific liquidity | June 2026 | Consolidated liquidity may overstate subsidiary-available liquidity | Material | Obtain entity cash allocation; exclude restricted cash from net debt |
| G-7 operating cash flow before both interest and tax not directly reported | Forecast-extension `cfo` | FY2025/H1 2026 | Forecast opening not ready; reported CFO cannot be relabelled | Material | Build and verify pre-interest, pre-tax CFO with cash classification and complete inputs |
| G-8 financing lease and operating lease June carrying detail not provided in current balance-sheet extract | Individual lease schedule | June 2026 | Contractual fixed-charge analysis limited | Minor | Obtain June lease note and distinguish failed-sale financing obligations |
| G-9 historical source comparability break from Windsor and pending merger | Organic growth/pro forma | H1 2026; after June | Forecast and peer comparison limited | Material | Obtain like-for-like history and disclosed transaction financing; do not invent adjustment |
| G-10 absence of a separately quantified subsequent-event financial adjustment | Alberta launch | July 13, 2026 | No June pro forma inclusion | Minor | Monitor later filings [C20] |

#### T4.13 — Downstream Readiness
| Downstream Module | Readiness Status | Gaps or Limitations | Recommended Actions |
|---|---|---|---|
| CP-1B | Ready with Limitations | Consolidated rather than full borrower-only detail | Carry perimeter flags |
| CP-1C | Ready with Limitations | Windsor break; peer evidence not in this CP-1 source set | Definition-controlled peer collection |
| CP-2 | Ready with Limitations | Rent/debt basis and capex split | Use CF-1/CF-4 and request capex detail |
| CP-2A | Ready with Limitations | No covenant EBITDA or merger financing | Stress causally without invented contractual headroom |
| CP-2D | Ready with Limitations | Working-capital float and acquisition cash must be differentiated | Preserve cash-flow classifications |
| CP-2G | Ready with Limitations | Historical split and pre-interest/pre-tax forecast CFO unavailable | Source forecasts and drivers; no unsupported JSON-pointer assignments |
| CP-2H | Ready with Limitations | No post-close capital structure | Conditional assessment only |
| CP-3 | Ready with Limitations | Market and security evidence requires separate owners | Retain carrying and principal alternatives |
| CP-3C | Ready with Limitations | Maturity data available; future merger financing absent | Use contractual schedule, isolate merger case |
| CP-4 | Ready with Limitations | Covenant text/version and merger agreement absent here | Obtain controlling instruments |
| CP-4A | Not Ready | Test EBITDA and covenant netting/headroom unavailable | Obtain compliance certificate and terms |
| CP-5 | Ready with Limitations | Explicit limitations and citations retained | Audit calculation lineage |
| CP-5A | Ready with Limitations | Host validation pending | Validate all numerical and machine-facing keys |
| CP-MODEL | blocked | Fewer than four complete discrete quarters; no complete selected-quarter facility schedule | Supply additional filings and rerun CP-1 |

#### T4.14 — Model Period Register

<!-- table-id: cp1.model_period_register -->

| period_id | fiscal_year | fiscal_quarter | period_type | start_date | end_date | day_count | audit_status | currency | unit | accounting_basis | entity_perimeter | source_id | source_locator | component_period_ids |
|---|---:|---:|---|---|---|---:|---|---|---|---|---|---|---|---|
| FY2025 | 2025 | null | FY | 2025-01-01 | 2025-12-31 | 365 | AUDITED | USD | MILLIONS | US GAAP | Consolidated | S1 | 10-K pp.56–61 [C1] | null |
| H1_2025 | 2025 | null | YTD | 2025-01-01 | 2025-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | S2 | 10-Q pp.3–8 [C3, C5] | null |
| Q2_2025 | 2025 | 2 | QUARTER | 2025-04-01 | 2025-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | S2 | 10-Q p.3 [C3] | null |
| H1_2026 | 2026 | null | YTD | 2026-01-01 | 2026-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | S2 | 10-Q pp.3–8 [C3, C5] | null |
| Q2_2026 | 2026 | 2 | QUARTER | 2026-04-01 | 2026-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | S2 | 10-Q p.3 [C3] | null |
| PE_2026_06 | 2026 | null | PERIOD_END | 2026-06-30 | 2026-06-30 | 1 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | S2 | 10-Q p.2 [C11] | null |
| PE_2025_12 | 2025 | null | PERIOD_END | 2025-12-31 | 2025-12-31 | 1 | AUDITED | USD | MILLIONS | US GAAP | Consolidated | S1 | 10-K p.56 [C1] | null |
| LTM_2026_06 | 2026 | null | LTM | 2025-07-01 | 2026-06-30 | 365 | CALCULATED | USD | MILLIONS | US GAAP | Consolidated | S1/S2 | 10-K pp.57–61; 10-Q pp.3–8 [C3–C8] | FY2025,H1_2026,H1_2025 |

#### T4.15 — Model Account Register

<!-- table-id: cp1.model_account_register -->

| metric_id | period_id | value | sign_convention | value_class | calculation_status | source_id | source_locator | conflict_refs | limitation_refs |
|---|---|---:|---|---|---|---|---|---|---|
| revenue | FY2025 | 11486 | INFLOW_POSITIVE | REPORTED | Verified | S1 | 10-K p.57 [C4] | null | null |
| revenue | H1_2025 | 5701 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | null |
| revenue | H1_2026 | 5863 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | G-9 |
| revenue | Q2_2025 | 2907 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | null |
| revenue | Q2_2026 | 2993 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | G-9 |
| revenue | LTM_2026_06 | 11648 | INFLOW_POSITIVE | CALCULATED | Calculated | S1/S2 | FY+H1−H1, T4.8 [C3, C4] | null | G-9 |
| opex_including_da | FY2025 | -9628 | OUTFLOW_NEGATIVE | REPORTED | Verified | S1 | 10-K p.57 [C4] | null | null |
| opex_including_da | H1_2026 | -4850 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | null |
| opex_including_da | H1_2025 | -4687 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | null |
| ebit | FY2025 | 1858 | INFLOW_POSITIVE | REPORTED | Verified | S1 | 10-K p.57 [C37] | null | null |
| ebit | H1_2025 | 1014 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C38] | null | null |
| ebit | H1_2026 | 1013 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C38] | null | null |
| ebit | Q2_2026 | 513 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C38] | null | null |
| ebit | Q2_2025 | 526 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C38] | null | null |
| depreciation_amortization | FY2025 | 1417 | EXPENSE_POSITIVE | REPORTED | Verified | S1 | 10-K p.57 [C4] | null | null |
| depreciation_amortization | H1_2026 | 702 | EXPENSE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | null |
| depreciation_amortization | H1_2025 | 721 | EXPENSE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C3] | null | null |
| ebitda | FY2025 | 3275 | INFLOW_POSITIVE | CALCULATED | Calculated | S1 | EBIT+D&A, T4.4 [C37] | CF-2 | null |
| ebitda | H1_2026 | 1715 | INFLOW_POSITIVE | CALCULATED | Calculated | S2 | EBIT+D&A, T4.4 [C38] | CF-2 | null |
| ebitda | H1_2025 | 1735 | INFLOW_POSITIVE | CALCULATED | Calculated | S2 | EBIT+D&A, T4.4 [C38] | CF-2 | null |
| adjusted_ebitda | FY2025 | 3624 | INFLOW_POSITIVE | REPORTED | Verified | S1 | 10-K p.44 [C16] | CF-2 | null |
| adjusted_ebitda | H1_2025 | 1839 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.28 [C15] | CF-2 | null |
| adjusted_ebitda | H1_2026 | 1807 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.28 [C15] | CF-2 | null |
| adjusted_ebitda | Q2_2025 | 955 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.28 [C15] | CF-2 | null |
| adjusted_ebitda | Q2_2026 | 920 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.28 [C15] | CF-2 | null |
| adjusted_ebitda | LTM_2026_06 | 3592 | INFLOW_POSITIVE | CALCULATED | Calculated | S1/S2 | FY+H1−H1, T4.8 [C15, C16] | CF-2 | G-9 |
| cfo_ncfo | FY2025 | 1302 | INFLOW_POSITIVE | REPORTED | Verified | S1 | 10-K p.60 [C7] | null | null |
| cfo_ncfo | H1_2025 | 680 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.7 [C5] | null | null |
| cfo_ncfo | H1_2026 | 675 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.7 [C5] | null | null |
| cfo_ncfo | LTM_2026_06 | 1297 | INFLOW_POSITIVE | CALCULATED | Calculated | S1/S2 | FY+H1−H1, T4.8 [C5, C7] | null | null |
| working_capital_change | H1_2026 | -71 | OUTFLOW_NEGATIVE | CALCULATED | Calculated | S2 | Sum operating asset/liability movements, 10-Q p.7 [C5] | null | null |
| capex_and_intangible_investment | FY2025 | -809 | OUTFLOW_NEGATIVE | CALCULATED | Calculated | S1 | Property 805 + intangible acquisition 4, 10-K p.60 [C8] | null | null |
| capex_and_intangible_investment | H1_2026 | -335 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | Property purchases, 10-Q p.7 [C6] | null | G-2 |
| capex_and_intangible_investment | H1_2025 | -453 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | Property purchases, 10-Q p.7 [C6] | null | G-2 |
| cash_interest_paid | FY2025 | -813 | OUTFLOW_NEGATIVE | REPORTED | Verified | S1 | 10-K p.61 [C40] | CF-4 | null |
| cash_interest_paid | H1_2025 | -405 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.8 [C9] | CF-4 | null |
| cash_interest_paid | H1_2026 | -368 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.8 [C9] | CF-4 | null |
| cash_lease_payments | FY2025 | -1349 | OUTFLOW_NEGATIVE | REPORTED | Verified | S1 | 10-K p.61 [C10] | CF-4 | null |
| cash_lease_payments | H1_2026 | -686 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.8 [C39] | CF-4 | null |
| cash_lease_payments | H1_2025 | -672 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.8 [C39] | CF-4 | null |
| cash_taxes_paid | FY2025 | -81 | OUTFLOW_NEGATIVE | REPORTED | Verified | S1 | 10-K p.61 [C10] | null | null |
| cash_taxes_paid | H1_2026 | -11 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.8 [C9] | null | null |
| cash_taxes_paid | H1_2025 | -58 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.8 [C9] | null | null |
| net_debt_issue_repay | H1_2026 | -98 | OUTFLOW_NEGATIVE | CALCULATED | Calculated | S2 | 885−983, 10-Q p.7 [C5] | null | null |
| net_equity_issue_repay | H1_2026 | 0 | INFLOW_POSITIVE | REPORTED | Verified | S2 | No repurchases, 10-Q p.7 [C5] | null | null |
| acquisitions_disposals | H1_2026 | -78 | OUTFLOW_NEGATIVE | CALCULATED | Calculated | S2 | Asset purchase −98 + property sale 20, 10-Q p.7 [C5] | null | G-9 |
| net_cash_change | H1_2026 | 93 | INFLOW_POSITIVE | REPORTED | Verified | S2 | 10-Q p.7 [C5] | null | null |
| net_cash_change | FY2025 | -32 | OUTFLOW_NEGATIVE | REPORTED | Verified | S1 | 10-K p.60 [C7] | null | null |
| cash_and_equivalents | PE_2026_06 | 965 | BALANCE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.2 [C14] | null | null |
| cash_and_equivalents | PE_2025_12 | 887 | BALANCE_POSITIVE | REPORTED | Verified | S1 | 10-K p.56 [C1] | null | null |
| rcf_commitment | PE_2026_06 | 2275 | BALANCE_POSITIVE | REPORTED | Verified | S2 | CEI 2250 + CVA 25, Note 6 pp.17–18 [C29] | null | null |
| rcf_drawn | PE_2026_06 | 120 | BALANCE_POSITIVE | REPORTED | Verified | S2 | Note 6 p.16 [C12] | null | null |
| total_debt | PE_2026_06 | 11699 | BALANCE_POSITIVE | CALCULATED | Calculated | S2 | BS current+long-term, p.2 [C11] | CF-1 | null |
| total_debt | PE_2025_12 | 11784 | BALANCE_POSITIVE | CALCULATED | Calculated | S1 | BS current+long-term, p.56 [C1, C33] | CF-1 | null |
| net_accounts_receivable | PE_2026_06 | 485 | BALANCE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.2 [C11] | null | null |
| inventory | PE_2026_06 | 49 | BALANCE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.2 [C11] | null | null |
| accounts_payable | PE_2026_06 | 290 | BALANCE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.2 [C11] | null | null |
| pretax_income | H1_2026 | -124 | LOSS_NEGATIVE | REPORTED | Verified | S2 | 10-Q p.3 [C27] | null | null |
| income_tax_expense | H1_2026 | 0 | EXPENSE_POSITIVE | REPORTED | Verified | S2 | 10-Q p.3 [C27] | null | null |
| effective_tax_rate | H1_2026 | 0 | RATE_PERCENT | REPORTED | Verified | S2 | Note 10 p.23 [C27] | null | null |
| interest_paid_in_financing | H1_2026 | 0 | OUTFLOW_NEGATIVE | REPORTED | Verified | S2 | US GAAP operating cash classification, 10-Q pp.7–8 [C5, C9] | null | null |

The model's `capex_and_intangible_investment` includes FY2025's separately reported $4 million intangible purchase; therefore its −809 differs intentionally from the property/equipment-only −805 used in T4.5 FCF. H1 intangible-acquisition cash is not separately stated; G-2 limits comparability. [C8]

#### T4.16 — Segment Revenue Schedule

<!-- table-id: cp1.segment_revenue_schedule -->

| segment_id | segment_name | segment_type | display_priority | period_id | revenue | status | source_id | source_locator |
|---|---|---|---:|---|---:|---|---|---|
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | FY2025 | 4049 | REPORTED | S1 | 10-K p.37 [C16] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | FY2025 | 5756 | REPORTED | S1 | 10-K p.37 [C16] |
| DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | FY2025 | 1408 | REPORTED | S1 | 10-K p.37 [C16] |
| MANAGED | Managed and Branded | OPERATING_SEGMENT | 4 | FY2025 | 279 | REPORTED | S1 | 10-K p.37 [C16] |
| CORPORATE | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2025 | -6 | REPORTED | S1 | 10-K p.37 [C16] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | H1_2026 | 2020 | REPORTED | S2 | 10-Q p.26 [C25] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | H1_2026 | 3000 | REPORTED | S2 | 10-Q p.26 [C25] |
| DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2026 | 725 | REPORTED | S2 | 10-Q p.26 [C25] |
| MANAGED | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2026 | 123 | REPORTED | S2 | 10-Q p.26 [C25] |
| CORPORATE | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2026 | -5 | REPORTED | S2 | 10-Q p.26 [C25] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | H1_2025 | 2057 | REPORTED | S2 | 10-Q p.26 [C25] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | H1_2025 | 2823 | REPORTED | S2 | 10-Q p.26 [C25] |
| DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2025 | 678 | REPORTED | S2 | 10-Q p.26 [C25] |
| MANAGED | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2025 | 141 | REPORTED | S2 | 10-Q p.26 [C25] |
| CORPORATE | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2025 | 2 | REPORTED | S2 | 10-Q p.26 [C25] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2026 | 1017 | REPORTED | S2 | 10-Q p.26 [C25] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | Q2_2026 | 1570 | REPORTED | S2 | 10-Q p.26 [C25] |
| DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2026 | 351 | REPORTED | S2 | 10-Q p.26 [C25] |
| MANAGED | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2026 | 57 | REPORTED | S2 | 10-Q p.26 [C25] |
| CORPORATE | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2026 | -2 | REPORTED | S2 | 10-Q p.26 [C25] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2025 | 1054 | REPORTED | S2 | 10-Q p.26 [C25] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | Q2_2025 | 1435 | REPORTED | S2 | 10-Q p.26 [C25] |
| DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2025 | 343 | REPORTED | S2 | 10-Q p.26 [C25] |
| MANAGED | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2025 | 74 | REPORTED | S2 | 10-Q p.26 [C25] |
| CORPORATE | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2025 | 1 | REPORTED | S2 | 10-Q p.26 [C25] |

**Forecast driver allocation only, not segment aggregation:** Corporate/elimination is retained as its own source row. Any division forecast must explicitly preserve its negative revenue rather than applying an operating-growth driver to it.

<!-- table-id: cp1.cp_model_segment_allocation -->

| slot_id | slot_label | component_segment_ids |
|---|---|---|
| DIVISION_1 | Las Vegas | LAS_VEGAS |
| DIVISION_2 | Regional | REGIONAL |
| DIVISION_3 | Digital, Managed and Corporate driver group | DIGITAL,MANAGED,CORPORATE |

<!-- table-id: cp1.operating_kpi_schedule -->

| kpi_id | kpi_label | business_unit | kpi_category | display_priority | period_id | value | unit | value_type | status | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|---|
| VEGAS_TABLE_HOLD | Table games hold | Las Vegas | Gaming hold | 1 | Q2_2026 | 16.6 | PERCENT | RATE | REPORTED | S2 | 10-Q p.35 [C30] |
| VEGAS_TABLE_HOLD | Table games hold | Las Vegas | Gaming hold | 1 | Q2_2025 | 21.1 | PERCENT | RATE | REPORTED | S2 | 10-Q p.35 [C30] |
| VEGAS_TABLE_HOLD | Table games hold | Las Vegas | Gaming hold | 1 | H1_2026 | 17.5 | PERCENT | RATE | REPORTED | S2 | 10-Q p.35 [C30] |
| DIGITAL_IG_HANDLE | iGaming handle | Caesars Digital | Wagering volume | 2 | Q2_2026 | 4831 | USD_MILLIONS | PERIOD_FLOW | REPORTED | S2 | 10-Q p.37 [C31] |
| DIGITAL_IG_HANDLE | iGaming handle | Caesars Digital | Wagering volume | 2 | Q2_2025 | 4705 | USD_MILLIONS | PERIOD_FLOW | REPORTED | S2 | 10-Q p.37 [C31] |
| DIGITAL_IG_HANDLE | iGaming handle | Caesars Digital | Wagering volume | 2 | H1_2026 | 10205 | USD_MILLIONS | PERIOD_FLOW | REPORTED | S2 | 10-Q p.37 [C31] |
| DIGITAL_IG_HANDLE | iGaming handle | Caesars Digital | Wagering volume | 2 | H1_2025 | 9193 | USD_MILLIONS | PERIOD_FLOW | REPORTED | S2 | 10-Q p.37 [C31] |

#### T4.17 — Adjusted EBITDA Bridge

<!-- table-id: cp1.adjusted_ebitda_bridge -->

| addback_id | addback_label | addback_classification | realization_status | display_priority | period_id | value | status | source_definition | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|
| NCI | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | REALIZED | 1 | FY2025 | 65 | REPORTED | Bridge from parent-attributable loss | S1 | 10-K p.44 [C16] |
| TAX | (Benefit) provision for income taxes | OTHER_EXPLICIT | REALIZED | 2 | FY2025 | -11 | REPORTED | Tax bridge | S1 | 10-K p.44 [C16] |
| OTHER | Other income | OTHER_EXPLICIT | REALIZED | 3 | FY2025 | -2 | REPORTED | Other-income exclusion | S1 | 10-K p.44 [C16] |
| EXTING | Loss on extinguishment of debt | OTHER_EXPLICIT | REALIZED | 4 | FY2025 | 4 | REPORTED | Debt extinguishment loss | S1 | 10-K p.44 [C16] |
| INTEREST | Interest expense, net | OTHER_EXPLICIT | REALIZED | 5 | FY2025 | 2304 | REPORTED | Interest add-back | S1 | 10-K p.44 [C16] |
| IMPAIR | Impairment charges | OTHER_EXPLICIT | REALIZED | 6 | FY2025 | 182 | REPORTED | Noncash impairments | S1 | 10-K p.44 [C16] |
| DA | Depreciation and amortization | OTHER_EXPLICIT | REALIZED | 7 | FY2025 | 1417 | REPORTED | D&A exclusion | S1 | 10-K p.44 [C16] |
| TRANSACTION | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | FY2025 | 72 | REPORTED | Issuer bridge includes multiple transaction/other components | S1 | 10-K p.44 [C16] |
| SBC | Stock-based compensation expense | SBC | REALIZED | 9 | FY2025 | 95 | REPORTED | Stock-compensation exclusion | S1 | 10-K p.44 [C16] |
| NCI | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | REALIZED | 1 | H1_2026 | 36 | REPORTED | Parent-to-consolidated bridge | S2 | 10-Q p.27 [C15] |
| TAX | (Benefit) provision for income taxes | OTHER_EXPLICIT | REALIZED | 2 | H1_2026 | 0 | REPORTED | Reported dash, provision/benefit nil | S2 | 10-Q p.27 [C15] |
| OTHER | Other income | OTHER_EXPLICIT | REALIZED | 3 | H1_2026 | -5 | REPORTED | Other-income exclusion | S2 | 10-Q p.27 [C15] |
| INTEREST | Interest expense, net | OTHER_EXPLICIT | REALIZED | 5 | H1_2026 | 1142 | REPORTED | Interest add-back | S2 | 10-Q p.27 [C15] |
| DA | Depreciation and amortization | OTHER_EXPLICIT | REALIZED | 7 | H1_2026 | 702 | REPORTED | D&A exclusion | S2 | 10-Q p.27 [C15] |
| TRANSACTION | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | H1_2026 | 45 | REPORTED | Includes other non-recurring items | S2 | 10-Q p.27 [C35] |
| SBC | Stock-based compensation expense | SBC | REALIZED | 9 | H1_2026 | 47 | REPORTED | Stock-compensation exclusion | S2 | 10-Q p.27 [C15] |
| NCI | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | REALIZED | 1 | Q2_2026 | 21 | REPORTED | Parent-to-consolidated bridge | S2 | 10-Q p.27 [C15] |
| TAX | (Benefit) provision for income taxes | OTHER_EXPLICIT | REALIZED | 2 | Q2_2026 | -12 | REPORTED | Tax-benefit bridge | S2 | 10-Q p.27 [C15] |
| OTHER | Other income | OTHER_EXPLICIT | REALIZED | 3 | Q2_2026 | -7 | REPORTED | Other-income exclusion | S2 | 10-Q p.27 [C15] |
| INTEREST | Interest expense, net | OTHER_EXPLICIT | REALIZED | 5 | Q2_2026 | 573 | REPORTED | Interest add-back | S2 | 10-Q p.27 [C15] |
| DA | Depreciation and amortization | OTHER_EXPLICIT | REALIZED | 7 | Q2_2026 | 355 | REPORTED | D&A exclusion | S2 | 10-Q p.27 [C15] |
| TRANSACTION | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | Q2_2026 | 29 | REPORTED | Issuer's adjusted bridge amount, not P&L 16 | S2 | 10-Q p.27 [C35] |
| SBC | Stock-based compensation expense | SBC | REALIZED | 9 | Q2_2026 | 23 | REPORTED | Stock-compensation exclusion | S2 | 10-Q p.27 [C15] |

#### T4.18 — Debt Facility Register

<!-- table-id: cp1.debt_facility_register -->

| facility_id | facility_name | period_id | facility_type | carrying_value | principal | drawn_amount | commitment | secured_status | seniority | currency | margin_or_coupon | maturity_date | lease_classification | rate_type | reference_rate | spread_bps | floor_bps | fixed_rate | annual_amortisation | source_id | source_locator |
|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---|---|
| RCF | CEI Revolving Credit Facility | PE_2026_06 | REVOLVER | 120 | 120 | 120 | 2250 | SECURED | SENIOR | USD | Term SOFR plus variable margin | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | null | 0 | S2 | Note 6 pp.16–17 [C12] |
| TLA | CEI Term Loan A | PE_2026_06 | TERM_LOAN | 618 | 619 | 619 | 750 | SECURED | SENIOR | USD | Term SOFR plus variable margin | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | null | 37.5 | S2 | Note 6 pp.16–17 [C12] |
| CVA | CVA Delayed Draw Term Loan | PE_2026_06 | TERM_LOAN | 372 | 376 | 376 | 400 | SECURED | SENIOR | USD | Term SOFR plus applicable margin not stated | 2029-04-26 | NOT_LEASE | FLOATING | TERM_SOFR | null | null | null | null | S2 | Note 6 pp.16–18 [C12] |
| TLB | CEI Term Loan B | PE_2026_06 | TERM_LOAN | 1993 | 2018 | 2018 | 2500 | SECURED | SENIOR | USD | Term SOFR + 225 bps | 2030-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | null | 25 | S2 | Note 6 pp.16–17 [C12] |
| TLB1 | CEI Term Loan B-1 | PE_2026_06 | TERM_LOAN | 2808 | 2835 | 2835 | 2900 | SECURED | SENIOR | USD | Term SOFR + 225 bps | 2031-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | null | 29 | S2 | Note 6 pp.16–17 [C29] |
| SS2030 | CEI Senior Secured Notes due 2030 | PE_2026_06 | NOTES | 1987 | 2000 | 2000 | 2000 | SECURED | SENIOR | USD | 7.00% | 2030-02-15 | NOT_LEASE | FIXED | NONE | null | null | 7.000 | 0 | S2 | Note 6 pp.16–18 [C12] |
| SS2032 | CEI Senior Secured Notes due 2032 | PE_2026_06 | NOTES | 1487 | 1500 | 1500 | 1500 | SECURED | SENIOR | USD | 6.50% | 2032-02-15 | NOT_LEASE | FIXED | NONE | null | null | 6.500 | 0 | S2 | Note 6 pp.16–18 [C39] |
| U2029 | CEI Senior Notes due 2029 | PE_2026_06 | NOTES | 1193 | 1200 | 1200 | 1200 | UNSECURED | SENIOR | USD | 4.625% | 2029-10-15 | NOT_LEASE | FIXED | NONE | null | null | 4.625 | 0 | S2 | Note 6 pp.16–18 [C12] |
| U2032 | CEI Senior Notes due 2032 | PE_2026_06 | NOTES | 1088 | 1100 | 1100 | 1100 | UNSECURED | SENIOR | USD | 6.00% | 2032-10-15 | NOT_LEASE | FIXED | NONE | null | null | 6.000 | 0 | S2 | Note 6 pp.16–18 [C12] |
| SID | Special Improvement District Bonds | PE_2026_06 | OTHER_DEBT | 38 | 38 | 38 | 38 | NOT_STATED | NOT_STATED | USD | 4.30% | 2037; exact date not stated | NOT_LEASE | FIXED | NONE | null | null | 4.300 | null | S2 | Note 6 p.16 [C12] |
| OTHER_DEBT | Long-term notes and other payables | PE_2026_06 | OTHER_DEBT | 1 | 1 | 1 | null | NOT_STATED | NOT_STATED | USD | Not stated | Not stated | NOT_LEASE | NOT_STATED | NOT_STATED | null | null | null | null | S2 | Note 6 p.16 [C12] |
| DEBT_ADJ | Revolver deferred finance charges | PE_2026_06 | DEBT_ADJUSTMENT | -6 | null | null | null | NOT_STATED | NOT_STATED | USD | Not applicable | Not applicable | NOT_LEASE | NOT_STATED | NONE | null | null | null | 0 | S2 | Note 6 p.16 [C13] |
| RCF | CEI Revolving Credit Facility | PE_2025_12 | REVOLVER | 160 | 160 | 160 | 2250 | SECURED | SENIOR | USD | Term SOFR plus variable margin | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | null | 0 | S1 | Note 9 p.74 [C33] |
| TLA | CEI Term Loan A | PE_2025_12 | TERM_LOAN | 636 | 637 | 637 | 750 | SECURED | SENIOR | USD | Term SOFR plus variable margin | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | null | 37.5 | S1 | Note 9 pp.74–76 [C33] |
| CVA | CVA Delayed Draw Term Loan | PE_2025_12 | TERM_LOAN | 381 | 386 | 386 | 400 | SECURED | SENIOR | USD | Term SOFR plus applicable margin not stated | 2029-04-26 | NOT_LEASE | FLOATING | TERM_SOFR | null | null | null | null | S1 | Note 9 pp.74–76 [C33] |
| TLB | CEI Term Loan B | PE_2025_12 | TERM_LOAN | 2002 | 2031 | 2031 | 2500 | SECURED | SENIOR | USD | Term SOFR + 225 bps | 2030-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | null | 25 | S1 | Note 9 pp.74–76 [C33] |
| TLB1 | CEI Term Loan B-1 | PE_2025_12 | TERM_LOAN | 2820 | 2849 | 2849 | 2900 | SECURED | SENIOR | USD | Term SOFR + 225 bps | 2031-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | null | 29 | S1 | Note 9 pp.74–76 [C33] |
| SS2030 | CEI Senior Secured Notes due 2030 | PE_2025_12 | NOTES | 1986 | 2000 | 2000 | 2000 | SECURED | SENIOR | USD | 7.00% | 2030-02-15 | NOT_LEASE | FIXED | NONE | null | null | 7.000 | 0 | S1 | Note 9 p.74 [C33] |
| SS2032 | CEI Senior Secured Notes due 2032 | PE_2025_12 | NOTES | 1486 | 1500 | 1500 | 1500 | SECURED | SENIOR | USD | 6.50% | 2032-02-15 | NOT_LEASE | FIXED | NONE | null | null | 6.500 | 0 | S1 | Note 9 p.74 [C33] |
| U2029 | CEI Senior Notes due 2029 | PE_2025_12 | NOTES | 1192 | 1200 | 1200 | 1200 | UNSECURED | SENIOR | USD | 4.625% | 2029-10-15 | NOT_LEASE | FIXED | NONE | null | null | 4.625 | 0 | S1 | Note 9 p.74 [C33] |
| U2032 | CEI Senior Notes due 2032 | PE_2025_12 | NOTES | 1087 | 1100 | 1100 | 1100 | UNSECURED | SENIOR | USD | 6.00% | 2032-10-15 | NOT_LEASE | FIXED | NONE | null | null | 6.000 | 0 | S1 | Note 9 p.74 [C33] |
| SID | Special Improvement District Bonds | PE_2025_12 | OTHER_DEBT | 40 | 40 | 40 | 40 | NOT_STATED | NOT_STATED | USD | 4.30% | 2037; exact date not stated | NOT_LEASE | FIXED | NONE | null | null | 4.300 | null | S1 | Note 9 p.74 [C33] |
| OTHER_DEBT | Long-term notes and other payables | PE_2025_12 | OTHER_DEBT | 2 | 2 | 2 | null | NOT_STATED | NOT_STATED | USD | Not stated | Not stated | NOT_LEASE | NOT_STATED | NOT_STATED | null | null | null | null | S1 | Note 9 p.74 [C33] |
| DEBT_ADJ | Revolver deferred finance charges | PE_2025_12 | DEBT_ADJUSTMENT | -8 | null | null | null | NOT_STATED | NOT_STATED | USD | Not applicable | Not applicable | NOT_LEASE | NOT_STATED | NONE | null | null | null | 0 | S1 | Note 9 p.74 [C33] |

The debt schedule excludes VICI/GLPI failed-sale financing obligations of $13,157 million in June and $13,096 million in December; these require separate fixed-charge analysis, not inclusion in the balance-sheet current-plus-long-term debt account. [C11, C24]

#### T4.19 — Model Reconciliation Register

<!-- table-id: cp1.model_reconciliation_register -->

| check_id | period_id | check_type | reported_value | calculated_value | difference | tolerance | status | explanation | source_refs |
|---|---|---|---:|---:|---:|---:|---|---|---|
| SEG_FY25 | FY2025 | SEGMENT_REVENUE | 11486 | 11486 | 0 | 0 | PASS | Sum five issuer segment rows | S1 p.37 [C16] |
| SEG_H126 | H1_2026 | SEGMENT_REVENUE | 5863 | 5863 | 0 | 0 | PASS | Sum all five segment rows | S2 p.26 [C25] |
| SEG_Q226 | Q2_2026 | SEGMENT_REVENUE | 2993 | 2993 | 0 | 0 | PASS | Sum all five segment rows | S2 p.26 [C25] |
| ADJ_FY25 | FY2025 | ADJUSTED_EBITDA_BRIDGE | 3624 | 3624 | 0 | 0 | PASS | Parent loss −502 plus all nine explicit bridge rows | S1 p.44 [C16] |
| ADJ_H126 | H1_2026 | ADJUSTED_EBITDA_BRIDGE | 1807 | 1807 | 0 | 0 | PASS | Parent loss −160 plus explicit disclosed bridge rows | S2 p.27 [C15] |
| ADJ_Q226 | Q2_2026 | ADJUSTED_EBITDA_BRIDGE | 920 | 920 | 0 | 0 | PASS | Parent loss −62 plus explicit disclosed bridge rows | S2 p.27 [C15] |
| CFO_H126 | H1_2026 | CFO_IDENTITY | 675 | 675 | 0 | 0 | PASS | Statement cash-flow subtotal retained | S2 p.7 [C5] |
| CASH_H126 | H1_2026 | NCF_TO_CASH_MOVEMENT | 93 | 675−411−171=93 | 0 | 0 | PASS | Cash includes restricted balances | S2 pp.7–8 [C5, C32] |
| DEBT_JUN | PE_2026_06 | DEBT_TOTAL_EX_LEASES | 11699 | 11705−6=11699 | 0 | 0 | PASS | Facility book values plus disclosed deferred-charge adjustment | S2 BS/Note 6 [C11–C13] |
| DEBT_DEC | PE_2025_12 | DEBT_TOTAL_EX_LEASES | 11784 | 11792−8=11784 | 0 | 0 | PASS | Facility book values plus disclosed deferred-charge adjustment | S1 BS/Note 9 [C33] |
| FY_QUARTERS | FY2025 | REPORTED_FY_TO_QUARTERLY_SUM | 11486 | null | null | 0 | WARN | Four discrete 2025 quarters are not supplied in this evidence set | S1 p.57; S2 p.3 [C3, C4] |

<!-- table-id: cp1.downstream_readiness -->

| downstream_module | status | missing_metric_ids | conflict_refs | explanation |
|---|---|---|---|---|
| CP-MODEL | blocked | Q1_2025,Q3_2025,Q4_2025,Q1_2026; discrete-quarter cash flows | CF-1,CF-2 | Four complete discrete quarters and matching debt schedules absent; exporter must not treat H1 or LTM as quarters |

## Evidence Trace

| Claim | Marker | Document | Page / use |
|---|---|---|---|
| Annual audited and interim unaudited bases | [C1, C2] | S1 10-K; S2 10-Q | 10-K p.54; 10-Q p.11 |
| Income, operating income and attribution | [C3, C4, C27, C37, C38] | S1; S2 | Statements pp.3, 57–58 |
| CFO, capex, cash and debt/rent interest | [C5–C10, C32, C39, C40] | S1; S2 | Cash flows and supplemental disclosures pp.7–8, 60–61 |
| Debt and liquidity bases | [C11–C14, C24, C33] | S1; S2 | Balance sheets, debt/lease notes and liquidity tables |
| Adjusted EBITDA and definition limitation | [C15, C16, C23, C35] | S1; S2 | Reconciliations pp.27–28, 43–44 |
| Deposits and segment/perimeter changes | [C17, C19, C25, C36] | S2 | Notes 1, 7 and 12 |
| Pending transaction and post-period launch | [C18, C20] | S2 | Note 1; MD&A |
| Remaining-year obligations and covenants | [C21, C22, C28, C41, C42] | S2 | Debt table and MD&A |
| Release-label discrepancy | [C26, C27] | S3; S2 | Release p.1; filed statement p.3 |
| Operating KPI trend | [C30, C31] | S2 | Segment MD&A pp.35–37 |

## Source Registry

T4.1 is the controlling three-source financial register. The broader accepted CP-0 inventory also lists legal documents, market observations and peer releases, but their contents were not delivered as CP-1 evidence here; none is silently used to populate issuer figures, covenant mechanics or pricing. S3 only corroborates the reporting and supplies the explicitly flagged release-label difference. The current filing controls current-period financial labels; FY2025's audited statements control annual history. [C1–C4, C26, C27]

## Gaps & Conflicts

T4.11 preserves five definition/perimeter issues and T4.12 records evidence gaps. **Machine-table null inventory:** T4.14's FY/YTD/LTM/PERIOD_END `fiscal_quarter` and all directly reported `component_period_ids`, T4.15's `conflict_refs`/`limitation_refs`, and inapplicable fixed/floating rate fields in T4.18 are reference or inapplicable nulls, not missing observations. T4.18 `CVA` at both dates has `spread_bps`, `floor_bps`, `fixed_rate` (inapplicable), and `annual_amortisation` absent because the CVA spread/floor/payment amount is not specified; `OTHER_DEBT` has `commitment`, `spread_bps`, `floor_bps`, `fixed_rate`, and `annual_amortisation` absent because terms are not stated; `SID` has `annual_amortisation` absent because its scheduled payments are not given; `DEBT_ADJ` has `principal`, `drawn_amount`, `commitment`, `spread_bps`, `floor_bps` and `fixed_rate` inapplicable to a financing-cost contra-row. T4.19 `FY_QUARTERS`, `calculated_value` and `difference`: null because four 2025 discrete quarters are absent. These absent values block a complete machine-ready quarterly history; no missing amount is assumed zero.

**Open material research questions:** What are actual June covenant EBITDA and netting figures, what current signed documents govern the pending merger and bank debt, and what unrestricted cash is available to each borrower? The delivered source set does not resolve these; no research brief or retrieval is available. G-4 through G-6 retain them as gaps. The strongest counterargument to the restricted rating is reported covenant compliance and the larger cash balance; it would improve conviction only with the actual compliance calculation and debtor-level available cash. [C14, C28]

## QA Validation

| Self-check | Result | Basis and disposition |
|---|---|---|
| Identity and source gate | PASS | Accepted CP-0 identity/hash preserved; issuer 10-K and 10-Q supplied. |
| Financial statement and period separation | RESTRICTED | FY, H1, Q2 and period-end rows differentiated; four-quarter history absent. |
| Debt, EBITDA and release reconciliation | PASS with flagged conflicts | CF-1–CF-5 and T4.19 preserve alternatives; no silent principal-to-carrying substitution. |
| Missing-value discipline | RESTRICTED | G-1–G-10 and machine-table null inventory; no missing quarter inferred. |
| Confidence self-scoring | RESTRICTED | Thirteen material claims: eight directly sourced, three calculated, one analyst inference, one insufficient: E≈85; 85 of 100 assessed coverage fields present: C=85; source gate S=1; one open material limitation P=15. Uncapped ≈70, material cap 59; Low/Restricted. |
| Canonical structure self-check | PASS locally | Host-owned YAML retained; six ordered H2 sections and required register headings/tags authored; exact filename specified. |
| Host validation and completeness scripts | PENDING | Host performs checks after this answer; no exit status or finding claimed. |

**Next analytical use:** pass the definition-controlled facts to CP-2, CP-2A and CP-4; obtain covenant inputs, additional quarters and transaction financing before upgrading contractual headroom, CP-MODEL export or a relative-value conclusion.