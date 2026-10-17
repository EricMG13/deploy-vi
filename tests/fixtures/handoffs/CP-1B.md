---
module_id: CP-1B
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-1, CP-1A
---

## Analysis

Hand-written test fixture of a CP-1B Handoff for the synthetic Primary pack `czr-2026q2-primary`. Revenue grew while earnings fell: first-half revenue rose 2.8% to 5,863 [C1] but Adjusted EBITDA fell 1.7% to 1,807 [C2], after a 3.1% fall in FY2025 to 3,624 [C3]. The growth is partly bought: Caesars Windsor is consolidated from March 3, 2026 [C4], so the first-half comparison has a perimeter change, and the like-for-like decline is larger than the reported one.

The driver is Las Vegas. Management attributes the segment's decline to lower city-wide leisure visitation, lower hotel occupancy and compressed rates [C5]; Regional and Caesars Digital offset part of it [C6] [C7]. The signal is a trend, not one period: FY2025 and the first half both show lower earnings on higher revenue. The strongest counter-reading is that Las Vegas is cyclical and regional growth is real; what would settle it is Las Vegas visitation and occupancy, which the pack does not report.

## Tables

<!-- table: snapshot.historical_performance -->
| text | cite |
|---|---|
| Revenue rose from 11,245 in FY2024 to 11,486 in FY2025 and from 5,701 to 5,863 in the first half of 2026, but Adjusted EBITDA fell from 3,739 to 3,624 and from 1,839 to 1,807. Las Vegas lost earnings on lower visitation and room rates while Regional (helped by consolidating Caesars Windsor) and Caesars Digital grew. Operating cash flow was flat at 675 in the first half against 680, so debt capacity has not grown with revenue. | [C1] [C2] [C3] [C8] [C4] [C5] [C9] |

<!-- table: cp1b.period_comparison -->
| metric_id | current_period_id | reference_period_id | comparison_basis | current_value | reference_value | abs_change | pct_change_pct | currency | unit | restatement | perimeter_change | cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | H1_2026 | H1_2025 | YoY | 5863 | 5701 | 162 | 2.8% | USD | MILLIONS | No | Yes | [C1] [C4] |
| adjusted_ebitda | H1_2026 | H1_2025 | YoY | 1807 | 1839 | -32 | -1.7% | USD | MILLIONS | No | Yes | [C2] [C4] |
| revenue | FY2025 | FY2024 | YoY | 11486 | 11245 | 241 | 2.1% | USD | MILLIONS | No | No | [C8] |
| adjusted_ebitda | FY2025 | FY2024 | YoY | 3624 | 3739 | -115 | -3.1% | USD | MILLIONS | No | No | [C3] |
| cfo_ncfo | H1_2026 | H1_2025 | YoY | 675 | 680 | -5 | -0.7% | USD | MILLIONS | No | Yes | [C9] |

<!-- table: cp1b.variance_drivers -->
| metric_id | management_driver | analyst_driver | credit_implication | cite |
|---|---|---|---|---|
| adjusted_ebitda | Las Vegas declined on lower city-wide leisure visitation, lower hotel occupancy and compressed hotel rates | the highest-margin segment is losing volume and price at once; regional growth partly comes from consolidating Caesars Windsor, not organic gains | earnings on the existing perimeter are falling while the buyout adds debt; pressure on leverage before synergies | [C5] [C4] |
| revenue | higher casino revenues, driven by iGaming handle and improved sports betting hold in Caesars Digital | digital growth is real but hold-dependent; hold improvements do not repeat reliably | revenue growth overstates the durable trend; treat digital hold as volatile | [C10] |

<!-- table: cp1b.kpi_changes -->
| kpi_id | current_value | reference_value | change | unit | trend | cite |
|---|---|---|---|---|---|---|

<!-- table: cp1b.guidance_vs_delivery -->
| metric_id | benchmark_source | benchmark_value | actual_value | variance | currency | unit | credit_implication | cite |
|---|---|---|---|---|---|---|---|---|

<!-- table: cp1b.signals -->
| signal | evidence | severity | credit_implication | cite |
|---|---|---|---|---|
| Core segment margin compression | Las Vegas Adjusted EBITDA down 12.6% in the second quarter | High | the segment that anchors asset value and rent cover is weakening | [C11] |
| Costs outgrowing revenue in Regional | Regional margin flat despite higher revenue, on labour costs and gaming taxes | Medium | growth does not convert into earnings, limiting deleveraging | [C12] |

## Gaps

- `cp1b.kpi_changes`: CP-1 registers no operating KPI; visitation, occupancy and RevPAR would lift it.
- `cp1b.guidance_vs_delivery`: Caesars gives no guidance in the pack and held no call for the second quarter.
- Like-for-like growth excluding Caesars Windsor: the pack does not split Windsor's contribution out.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_Q2_2026_10Q.txt | Statements of Operations | Net revenues \| 2,993 \| 2,907 \| 5,863 \| 5,701 |
| C2 | CZR_Q2_2026_Earnings_Release.txt | Reconciliation to Adjusted EBITDA | Adjusted EBITDA \| $920 \| $955 \| $1,807 \| $1,839 |
| C3 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Adjusted EBITDA \| 3,624 \| 3,739 \| 3,938 |
| C4 | CZR_Q2_2026_10Q.txt | MD&A, Regional | the consolidation of Caesars Windsor beginning March 3, 2026 |
| C5 | CZR_Q2_2026_10Q.txt | MD&A, Las Vegas | lower city-wide leisure customer visitation ... lower hotel occupancy and compressed hotel rates |
| C6 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Regional \| 923 \| 879 \| 5.0% |
| C7 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Caesars Digital \| 137 \| 123 \| 11.4% |
| C8 | CZR_FY2025_10K.txt | Consolidated Statements of Operations | Net revenues \| 11,486 \| 11,245 \| 11,528 |
| C9 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows | Net cash provided by operating activities \| 675 \| 680 |
| C10 | CZR_Q2_2026_10Q.txt | MD&A, consolidated | driven by significant growth in iGaming handle coupled with improved sports betting hold |
| C11 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, three months ended June 30 | Las Vegas \| $410 \| $469 \| (12.6)% |
| C12 | CZR_Q2_2026_10Q.txt | MD&A, Regional | primarily due to increased labor costs and gaming taxes |
