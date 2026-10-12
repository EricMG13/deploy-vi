---
module_id: CP-1D
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-1, CP-1A, CP-1B
---

## Analysis

Hand-written test fixture of a CP-1D Handoff for the synthetic Primary pack `czr-2026q2-primary`. The issuer's add-backs are realized costs and the evidence supports the LTM Adjusted EBITDA of 3,592 as a measure of the period, but not as a measure of what is left for creditors: it is before about 1.35 billion a year of rent on the GLPI and VICI leases [C1] [C2]. Impairment is non-cash and supported [C3]; transaction costs appear in every registered period [C4] [C5] and stock-based compensation is a recurring cost [C6] [C7], so both are challenged but kept as realized. The arranger's 150 of run-rate synergies is not achieved and is unrealized [C8].

Cash conversion is weak: operating cash flow was 37.4% of Adjusted EBITDA in the first half and 35.9% in FY2025 [C9] [C10], because rent and debt interest are paid out of operating cash. The financing obligations of 13,157 behave like debt [C11]: counted as debt they take adjusted debt to 27,742 on the PF-LTM. The strongest case for the issuer's figure is that rent is an operating cost of an asset-light operator; it fails because the rent is fixed, escalates and cannot be cut in a downturn.

## Tables

<!-- table: cp1d.addback_assessment -->
| addback_id | period_id | amount | currency | unit | category | house_realization_status | verdict | rationale | recurrence | cite |
|---|---|---|---|---|---|---|---|---|---|---|
| impairment | FY2025 | 182 | USD | MILLIONS | Impairment charges | REALIZED | Supported | non-cash write-down of Regional properties on lower projected cash flows | 3 of 3 fiscal years | [C3] |
| transaction_costs_other | FY2025 | 72 | USD | MILLIONS | Transaction costs | REALIZED | Challenged | write-downs, litigation reserves, integration and pre-opening costs recur every period | 5 of 5 periods | [C4] |
| transaction_costs_other | H1_2025 | 54 | USD | MILLIONS | Transaction costs | REALIZED | Challenged | recurs every period | 5 of 5 periods | [C5] |
| transaction_costs_other | H1_2026 | 45 | USD | MILLIONS | Transaction costs | REALIZED | Challenged | recurs every period | 5 of 5 periods | [C5] |
| stock_based_compensation | FY2025 | 95 | USD | MILLIONS | Stock-based compensation | REALIZED | Challenged | a recurring employee cost settled in shares | 5 of 5 periods | [C6] |
| stock_based_compensation | H1_2025 | 50 | USD | MILLIONS | Stock-based compensation | REALIZED | Challenged | a recurring employee cost settled in shares | 5 of 5 periods | [C7] |
| stock_based_compensation | H1_2026 | 47 | USD | MILLIONS | Stock-based compensation | REALIZED | Challenged | a recurring employee cost settled in shares | 5 of 5 periods | [C7] |
| run_rate_synergies | LTM_Q2_2026 | 150 | USD | MILLIONS | Synergies | UNREALIZED | Challenged | an arranger estimate of savings the buyer has identified but not achieved | 1 of 1 (LTM only) | [C8] |

<!-- table: cp1d.cash_conversion -->
| period_id | adjusted_ebitda | cfo | conversion_pct | currency | unit | explanation | credit_implication | cite |
|---|---|---|---|---|---|---|---|---|
| H1_2026 | 1807 | 675 | 37.4% | USD | MILLIONS | cash interest on debt of 368 and rent paid as interest of 686 sit between Adjusted EBITDA and operating cash flow | little cash is left for capex and debt reduction before the new term loan's interest | [C9] [C12] [C13] |
| FY2025 | 3624 | 1302 | 35.9% | USD | MILLIONS | cash interest on debt of 813 and rent paid as interest of 1,349 | the same structural gap in the full year | [C10] [C14] [C2] |

<!-- table: cp1d.debt_like_items -->
| item | amount | currency | unit | period_id | treatment | basis | cite |
|---|---|---|---|---|---|---|---|
| Long-term financing obligations (GLPI and VICI leases) | 13157 | USD | MILLIONS | LTM_Q2_2026 | Debt-like | sale-leaseback leases accounted for as financing obligations; fixed rent with CPI escalators | [C11] [C1] |
| Revolver letters of credit | 96 | USD | MILLIONS | LTM_Q2_2026 | Not debt-like | contingent; counted in available revolver capacity, not drawn | [C15] |

## Gaps

- Run-rate synergies: no evidence of the actions behind the arranger's 150; lifted by the lender presentation's synergy plan.
- Lease liabilities other than the GLPI and VICI financing obligations: not sized in the pack's extracts.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_FY2025_10K.txt | Risk factors, indebtedness | VICI and GLPI that require an annual rent payment of $1.4 billion in 2026 |
| C2 | CZR_FY2025_10K.txt | Supplemental disclosure of cash flow information | Cash interest paid for rent related to financing obligations \| 1,349 \| 1,324 \| 1,286 |
| C3 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Impairment charges (c) \| 182 \| 302 \| 95 |
| C4 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Transaction costs and other, net (d) \| 72 \| (285) \| 6 |
| C5 | CZR_Q2_2026_Earnings_Release.txt | Reconciliation to Adjusted EBITDA | Transaction costs and other, net (a) \| 29 \| 41 \| 45 \| 54 |
| C6 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Stock-based compensation expense \| 95 \| 94 \| 104 |
| C7 | CZR_Q2_2026_Earnings_Release.txt | Reconciliation to Adjusted EBITDA | Stock-based compensation expense \| 23 \| 24 \| 47 \| 50 |
| C8 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Earnings and interest | Run-rate cost synergies identified by Fertitta Entertainment, not yet realised \| 150 |
| C9 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows | Net cash provided by operating activities \| 675 \| 680 |
| C10 | CZR_FY2025_10K.txt | Consolidated Statements of Cash Flows | Net cash provided by operating activities \| 1,302 \| 1,075 \| 1,809 |
| C11 | CZR_Q2_2026_10Q.txt | Balance Sheets | Long-term financing obligations \| 13,157 \| 13,096 |
| C12 | CZR_Q2_2026_10Q.txt | Supplemental cash flow information | Cash interest paid for debt \| $368 \| $405 |
| C13 | CZR_Q2_2026_10Q.txt | Supplemental cash flow information | Cash interest paid for rent related to GLPI and VICI Leases \| 686 \| 672 |
| C14 | CZR_FY2025_10K.txt | Supplemental disclosure of cash flow information | Cash interest paid for debt \| $813 \| $1,052 \| $846 |
| C15 | CZR_Q2_2026_10Q.txt | Liquidity and Capital Resources | Revolver capacity committed to letters of credit \| (96) |
