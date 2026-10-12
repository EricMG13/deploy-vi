---
module_id: CP-1
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0
---

## Analysis

Hand-written test fixture of a CP-1 Handoff for the synthetic Primary pack `czr-2026q2-primary`. Caesars Entertainment, Inc. reports consolidated US GAAP figures in USD millions; the registers carry FY2023 to FY2025 from the Form 10-K [C10], the six months to June 30 of 2025 and 2026 from the Form 10-Q [C1], and an LTM to June 30, 2026 that the Model derives. Adjusted EBITDA fell from 3,938 in FY2023 to 3,624 in FY2025 [C13] and from 1,839 to 1,807 in the first half [C4]; total debt at book was 11,705 at June 30, 2026 [C9]. Facility terms come from the debt note: the revolver's size and maturity [C35], the margins [C36], the term loans' floors, maturities and amortisation [C37] [C38] [C39] [C40] [C41] [C42] and the CVA term loan's size [C43]. Two definitions move leverage. Caesars' Adjusted EBITDA excludes the rent on the GLPI and VICI leases, which are accounted for as financing obligations [C44], while total debt excludes those obligations of 13,157 [C45]; the pair is consistent, but lease-adjusted leverage needs both. Debt is carried at book; the issuer's net debt of 10,842 is on face value [C46].

The new Senior Secured Term Loan B (`NEW-1`, 3,000) and the pro forma capitalisation come from SYNTHETIC test files [C47] [C48]: the PF register adds the tranche and repays the revolver (the Model carries both into total debt, so no separate total-debt row is written), adds 100 of cash and 213 of cash interest, and the bridge carries 150 of run-rate synergies as an unrealized add-back [C52]. Restricted: the PF figures are arranger estimates, FY2023 debt is not in the pack, and most instruments lack a call schedule.

## Tables

<!-- table: cp1.model_period_register -->
| period_id | fiscal_year | fiscal_quarter | period_type | start_date | end_date | day_count | currency | unit | component_period_ids |
|---|---|---|---|---|---|---|---|---|---|
| FY2023 | FY2023 | — | FY | 2023-01-01 | 2023-12-31 | 365 | USD | MILLIONS | — |
| FY2024 | FY2024 | — | FY | 2024-01-01 | 2024-12-31 | 366 | USD | MILLIONS | — |
| FY2025 | FY2025 | — | FY | 2025-01-01 | 2025-12-31 | 365 | USD | MILLIONS | — |
| H1_2025 | FY2025 | Q2 | YTD | 2025-01-01 | 2025-06-30 | 181 | USD | MILLIONS | — |
| H1_2026 | FY2026 | Q2 | YTD | 2026-01-01 | 2026-06-30 | 181 | USD | MILLIONS | — |
| LTM_Q2_2026 | FY2026 | Q2 | LTM | 2025-07-01 | 2026-06-30 | 365 | USD | MILLIONS | — |

<!-- table: cp1.model_account_register -->
| metric_id | period_id | value | calculation_status | source_id | source_locator |
|---|---|---|---|---|---|
| revenue | FY2023 | 11528 | VERIFIED | [C10] | Consolidated Statements of Operations |
| cogs | FY2023 | -5395 | CALCULATED | [C11] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | FY2023 | -3661 | CALCULATED | [C11] | total operating expenses less cogs |
| depreciation_amortization | FY2023 | -1261 | VERIFIED | [C12] | Consolidated Statements of Operations |
| adjusted_ebitda | FY2023 | 3938 | VERIFIED | [C13] | Adjusted EBITDA reconciliation |
| cash_interest_paid | FY2023 | -846 | VERIFIED | [C14] | Supplemental disclosure of cash flow information |
| capex_and_intangible_investment | FY2023 | -1264 | VERIFIED | [C15] | Consolidated Statements of Cash Flows |
| cfo_ncfo | FY2023 | 1809 | VERIFIED | [C16] | Consolidated Statements of Cash Flows |
| cash_and_equivalents | FY2023 | 1005 | VERIFIED | [C17] | Reconciliation of cash to the balance sheets |
| total_debt | FY2023 | — | NOT AVAILABLE | [C18] | Note 9. Long-Term Debt shows 2025 and 2024 only |
| revenue | FY2024 | 11245 | VERIFIED | [C10] | Consolidated Statements of Operations |
| cogs | FY2024 | -5419 | CALCULATED | [C11] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | FY2024 | -3522 | CALCULATED | [C11] | total operating expenses less cogs |
| depreciation_amortization | FY2024 | -1324 | VERIFIED | [C12] | Consolidated Statements of Operations |
| adjusted_ebitda | FY2024 | 3739 | VERIFIED | [C13] | Adjusted EBITDA reconciliation |
| cash_interest_paid | FY2024 | -1052 | VERIFIED | [C14] | Supplemental disclosure of cash flow information |
| capex_and_intangible_investment | FY2024 | -1296 | VERIFIED | [C15] | Consolidated Statements of Cash Flows |
| cfo_ncfo | FY2024 | 1075 | VERIFIED | [C16] | Consolidated Statements of Cash Flows |
| cash_and_equivalents | FY2024 | 866 | VERIFIED | [C17] | Reconciliation of cash to the balance sheets |
| total_debt | FY2024 | 12154 | VERIFIED | [C18] | Note 9. Long-Term Debt, book value |
| revenue | FY2025 | 11486 | VERIFIED | [C10] | Consolidated Statements of Operations |
| cogs | FY2025 | -5743 | CALCULATED | [C11] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | FY2025 | -3885 | CALCULATED | [C11] | total operating expenses less cogs |
| depreciation_amortization | FY2025 | -1417 | VERIFIED | [C12] | Consolidated Statements of Operations |
| adjusted_ebitda | FY2025 | 3624 | VERIFIED | [C13] | Adjusted EBITDA reconciliation |
| cash_interest_paid | FY2025 | -813 | VERIFIED | [C14] | Supplemental disclosure of cash flow information |
| capex_and_intangible_investment | FY2025 | -805 | VERIFIED | [C15] | Consolidated Statements of Cash Flows |
| cfo_ncfo | FY2025 | 1302 | VERIFIED | [C16] | Consolidated Statements of Cash Flows |
| cash_and_equivalents | FY2025 | 887 | VERIFIED | [C8] | Consolidated Condensed Balance Sheets |
| total_debt | FY2025 | 11792 | VERIFIED | [C9] | Note 6. Long-Term Debt, book value at December 31, 2025 |
| revenue | H1_2025 | 5701 | VERIFIED | [C1] | Statements of Operations, six months ended June 30 |
| cogs | H1_2025 | -2804 | CALCULATED | [C2] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | H1_2025 | -1883 | CALCULATED | [C2] | total operating expenses less cogs |
| depreciation_amortization | H1_2025 | -721 | VERIFIED | [C3] | Statements of Operations, six months ended June 30 |
| adjusted_ebitda | H1_2025 | 1839 | VERIFIED | [C4] | Adjusted EBITDA reconciliation, six months ended June 30 |
| cash_interest_paid | H1_2025 | -405 | VERIFIED | [C5] | Supplemental cash flow information, six months ended June 30 |
| capex_and_intangible_investment | H1_2025 | -453 | VERIFIED | [C6] | Statements of Cash Flows, six months ended June 30 |
| cfo_ncfo | H1_2025 | 680 | VERIFIED | [C7] | Statements of Cash Flows, six months ended June 30 |
| revenue | H1_2026 | 5863 | VERIFIED | [C1] | Statements of Operations, six months ended June 30 |
| cogs | H1_2026 | -2921 | CALCULATED | [C2] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | H1_2026 | -1929 | CALCULATED | [C2] | total operating expenses less cogs |
| depreciation_amortization | H1_2026 | -702 | VERIFIED | [C3] | Statements of Operations, six months ended June 30 |
| adjusted_ebitda | H1_2026 | 1807 | VERIFIED | [C4] | Adjusted EBITDA reconciliation, six months ended June 30 |
| cash_interest_paid | H1_2026 | -368 | VERIFIED | [C5] | Supplemental cash flow information, six months ended June 30 |
| capex_and_intangible_investment | H1_2026 | -335 | VERIFIED | [C6] | Statements of Cash Flows, six months ended June 30 |
| cfo_ncfo | H1_2026 | 675 | VERIFIED | [C7] | Statements of Cash Flows, six months ended June 30 |
| cash_and_equivalents | H1_2026 | 965 | VERIFIED | [C8] | Consolidated Condensed Balance Sheets |
| total_debt | H1_2026 | 11705 | VERIFIED | [C9] | Note 6. Long-Term Debt, book value at June 30, 2026 |

<!-- table: cp1.adjusted_ebitda_bridge -->
| addback_id | addback_label | addback_classification | realization_status | display_priority | period_id | value | source_id | source_locator |
|---|---|---|---|---|---|---|---|---|
| impairment | Impairment charges | OTHER_EXPLICIT | REALIZED | 1 | FY2023 | 95 | [C21] | Adjusted EBITDA reconciliation |
| impairment | Impairment charges | OTHER_EXPLICIT | REALIZED | 1 | FY2024 | 302 | [C21] | Adjusted EBITDA reconciliation |
| impairment | Impairment charges | OTHER_EXPLICIT | REALIZED | 1 | FY2025 | 182 | [C21] | Adjusted EBITDA reconciliation |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | FY2023 | 6 | [C22] | Adjusted EBITDA reconciliation |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | FY2024 | -285 | [C22] | Adjusted EBITDA reconciliation |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | FY2025 | 72 | [C22] | Adjusted EBITDA reconciliation |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | H1_2025 | 54 | [C19] | Adjusted EBITDA reconciliation, six months ended June 30 |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | H1_2026 | 45 | [C19] | Adjusted EBITDA reconciliation, six months ended June 30 |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | FY2023 | 104 | [C23] | Adjusted EBITDA reconciliation |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | FY2024 | 94 | [C23] | Adjusted EBITDA reconciliation |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | FY2025 | 95 | [C23] | Adjusted EBITDA reconciliation |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | H1_2025 | 50 | [C20] | Adjusted EBITDA reconciliation, six months ended June 30 |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | H1_2026 | 47 | [C20] | Adjusted EBITDA reconciliation, six months ended June 30 |
| run_rate_synergies | Run-rate cost synergies | SYNERGY | UNREALIZED | 4 | LTM_Q2_2026 | 150 | [C52] | Earnings and interest, last twelve months to June 30, 2026 |

<!-- table: cp1.segment_revenue_schedule -->
| segment_id | segment_name | segment_type | display_priority | period_id | revenue | source_id | source_locator |
|---|---|---|---|---|---|---|---|
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | FY2025 | 4049 | [C53] | Results of operations by segment |
| regional | Regional | OPERATING_SEGMENT | 2 | FY2025 | 5756 | [C54] | Results of operations by segment |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | FY2025 | 1408 | [C55] | Results of operations by segment |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | FY2025 | 279 | [C56] | Results of operations by segment |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2025 | -6 | [C57] | Results of operations by segment |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | H1_2025 | 2057 | [C58] | Net revenues, six months ended June 30 |
| regional | Regional | OPERATING_SEGMENT | 2 | H1_2025 | 2823 | [C59] | Net revenues, six months ended June 30 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2025 | 678 | [C60] | Net revenues, six months ended June 30 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2025 | 141 | [C61] | Net revenues, six months ended June 30 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2025 | 2 | [C62] | Net revenues, six months ended June 30 |
| las_vegas | Las Vegas | OPERATING_SEGMENT | 1 | H1_2026 | 2020 | [C58] | Net revenues, six months ended June 30 |
| regional | Regional | OPERATING_SEGMENT | 2 | H1_2026 | 3000 | [C59] | Net revenues, six months ended June 30 |
| caesars_digital | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2026 | 725 | [C60] | Net revenues, six months ended June 30 |
| managed_branded | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2026 | 123 | [C61] | Net revenues, six months ended June 30 |
| corporate_other | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2026 | -5 | [C62] | Net revenues, six months ended June 30 |

<!-- table: cp1.operating_kpi_schedule -->
| kpi_id | kpi_label | display_priority | period_id | value | unit | value_type | source_id | source_locator |
|---|---|---|---|---|---|---|---|---|

<!-- table: cp1.debt_facility_register -->
| facility_id | facility_name | period_id | facility_type | currency | carrying_value | drawn_amount | commitment | secured_status | seniority | margin_or_coupon | maturity_date | lease_classification | rate_type | reference_rate | spread_bps | floor_bps | fixed_rate | annual_amortisation | source_id | source_locator |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CEI-RCF | CEI Revolving Credit Facility | H1_2026 | Revolving credit facility | USD | 120 | 120 | 2250 | SECURED | SENIOR | Adjusted Term SOFR + 2.25% | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | — | 0 | [C24] | Note 6. Long-Term Debt |
| CEI-RCF | CEI Revolving Credit Facility | FY2025 | Revolving credit facility | USD | 160 | 160 | 2250 | SECURED | SENIOR | Adjusted Term SOFR + 2.25% | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | — | 0 | [C24] | Note 6. Long-Term Debt |
| CEI-TLA | CEI Term Loan A | H1_2026 | Term loan | USD | 618 | 619 | — | SECURED | SENIOR | Adjusted Term SOFR + 2.25% | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | — | 37.5 | [C25] | Note 6. Long-Term Debt |
| CEI-TLA | CEI Term Loan A | FY2025 | Term loan | USD | 636 | — | — | SECURED | SENIOR | Adjusted Term SOFR + 2.25% | 2028-01-31 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 0 | — | 37.5 | [C25] | Note 6. Long-Term Debt |
| CVA-DDTL | CVA Delayed Draw Term Loan | H1_2026 | Term loan | USD | 372 | 376 | 400 | SECURED | SENIOR | Term SOFR plus an applicable margin | 2029-04-26 | NOT_LEASE | FLOATING | TERM_SOFR | — | — | — | — | [C26] | Note 6. Long-Term Debt |
| CVA-DDTL | CVA Delayed Draw Term Loan | FY2025 | Term loan | USD | 381 | — | 400 | SECURED | SENIOR | Term SOFR plus an applicable margin | 2029-04-26 | NOT_LEASE | FLOATING | TERM_SOFR | — | — | — | — | [C26] | Note 6. Long-Term Debt |
| CEI-TLB | CEI Term Loan B | H1_2026 | Term loan | USD | 1993 | 2018 | — | SECURED | SENIOR | Term SOFR + 2.25% | 2030-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | — | 25 | [C27] | Note 6. Long-Term Debt |
| CEI-TLB | CEI Term Loan B | FY2025 | Term loan | USD | 2002 | — | — | SECURED | SENIOR | Term SOFR + 2.25% | 2030-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | — | 25 | [C27] | Note 6. Long-Term Debt |
| CEI-TLB-1 | CEI Term Loan B-1 | H1_2026 | Term loan | USD | 2808 | 2835 | — | SECURED | SENIOR | Term SOFR + 2.25% | 2031-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | — | 29 | [C28] | Note 6. Long-Term Debt |
| CEI-TLB-1 | CEI Term Loan B-1 | FY2025 | Term loan | USD | 2820 | — | — | SECURED | SENIOR | Term SOFR + 2.25% | 2031-02-06 | NOT_LEASE | FLOATING | TERM_SOFR | 225 | 50 | — | 29 | [C28] | Note 6. Long-Term Debt |
| CEI-SSN-2030 | CEI Senior Secured Notes due 2030 | H1_2026 | Notes | USD | 1987 | — | — | SECURED | SENIOR | 7.00% | 2030-02-15 | NOT_LEASE | FIXED | NONE | — | — | 7.00 | 0 | [C29] | Note 6. Long-Term Debt |
| CEI-SSN-2030 | CEI Senior Secured Notes due 2030 | FY2025 | Notes | USD | 1986 | — | — | SECURED | SENIOR | 7.00% | 2030-02-15 | NOT_LEASE | FIXED | NONE | — | — | 7.00 | 0 | [C29] | Note 6. Long-Term Debt |
| CEI-SSN-2032 | CEI Senior Secured Notes due 2032 | H1_2026 | Notes | USD | 1487 | — | — | SECURED | SENIOR | 6.50% | 2032-02-15 | NOT_LEASE | FIXED | NONE | — | — | 6.50 | 0 | [C30] | Note 6. Long-Term Debt |
| CEI-SSN-2032 | CEI Senior Secured Notes due 2032 | FY2025 | Notes | USD | 1486 | — | — | SECURED | SENIOR | 6.50% | 2032-02-15 | NOT_LEASE | FIXED | NONE | — | — | 6.50 | 0 | [C30] | Note 6. Long-Term Debt |
| CEI-SN-2029 | CEI Senior Notes due 2029 | H1_2026 | Notes | USD | 1193 | — | — | UNSECURED | SENIOR | 4.625% | 2029-10-15 | NOT_LEASE | FIXED | NONE | — | — | 4.625 | 0 | [C31] | Note 6. Long-Term Debt |
| CEI-SN-2029 | CEI Senior Notes due 2029 | FY2025 | Notes | USD | 1192 | — | — | UNSECURED | SENIOR | 4.625% | 2029-10-15 | NOT_LEASE | FIXED | NONE | — | — | 4.625 | 0 | [C31] | Note 6. Long-Term Debt |
| CEI-SN-2032 | CEI Senior Notes due 2032 | H1_2026 | Notes | USD | 1088 | — | — | UNSECURED | SENIOR | 6.00% | 2032-10-15 | NOT_LEASE | FIXED | NONE | — | — | 6.00 | 0 | [C32] | Note 6. Long-Term Debt |
| CEI-SN-2032 | CEI Senior Notes due 2032 | FY2025 | Notes | USD | 1087 | — | — | UNSECURED | SENIOR | 6.00% | 2032-10-15 | NOT_LEASE | FIXED | NONE | — | — | 6.00 | 0 | [C32] | Note 6. Long-Term Debt |
| SID-BONDS | Special Improvement District Bonds | H1_2026 | Bonds | USD | 38 | — | — | UNSECURED | NOT_STATED | 4.30% | 2037 | NOT_LEASE | FIXED | NONE | — | — | 4.30 | — | [C33] | Note 6. Long-Term Debt |
| SID-BONDS | Special Improvement District Bonds | FY2025 | Bonds | USD | 40 | — | — | UNSECURED | NOT_STATED | 4.30% | 2037 | NOT_LEASE | FIXED | NONE | — | — | 4.30 | — | [C33] | Note 6. Long-Term Debt |
| OTHER-PAYABLES | Long-term notes and other payables | H1_2026 | Other payables | USD | 1 | — | — | UNSECURED | NOT_STATED | Not stated | — | NOT_LEASE | NOT_STATED | NOT_STATED | — | — | — | — | [C34] | Note 6. Long-Term Debt |
| OTHER-PAYABLES | Long-term notes and other payables | FY2025 | Other payables | USD | 2 | — | — | UNSECURED | NOT_STATED | Not stated | — | NOT_LEASE | NOT_STATED | NOT_STATED | — | — | — | — | [C34] | Note 6. Long-Term Debt |
| NEW-1 | New Senior Secured Term Loan B | LTM_Q2_2026 | Term loan | USD | 0 | — | — | SECURED | SENIOR | SOFR + 300–325 bps (initial talk) | 2033-12-15 | NOT_LEASE | FLOATING | SOFR | — | 50 | — | 30 | [C47] | Summary of terms |

<!-- table: cp1.pro_forma_adjustment_register -->
| adjustment_id | label | period_id | effective_date | classification | metric_id | value | source_id | source_locator |
|---|---|---|---|---|---|---|---|---|
| PF-1 | New Senior Secured Term Loan B | LTM_Q2_2026 | 2026-06-30 | ACQUISITION | facility:NEW-1 | 3000 | [C48] | Capitalisation |
| PF-2 | Repay CEI Revolving Credit Facility | LTM_Q2_2026 | 2026-06-30 | REFINANCING | facility:CEI-RCF | -120 | [C49] | Capitalisation |
| PF-3 | Cash to balance sheet | LTM_Q2_2026 | 2026-06-30 | ACQUISITION | cash_and_equivalents | 100 | [C51] | Capitalisation |
| PF-4 | Pro forma cash interest paid for debt | LTM_Q2_2026 | 2026-06-30 | ACQUISITION | cash_interest_paid | -213 | [C63] | Earnings and interest; calc: -(989 - 776) |

<!-- table: cp1.cp_model_segment_allocation -->
| slot_id | component_segment_ids |
|---|---|
| DIVISION_1 | las_vegas |
| DIVISION_2 | regional |
| DIVISION_3 | caesars_digital; managed_branded |

<!-- table: cp1.equity_value -->
| market_cap | share_price | shares_outstanding | value_date | currency | unit | cite |
|---|---|---|---|---|---|---|

<!-- table: cp1.instrument_identity -->
| facility_id | instrument_name | debt_type | bloomberg_id | isin | cusip | issuer_entity | rating_moodys | rating_sp | rating_fitch | call_schedule | listed_market | cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CEI-RCF | CEI Revolving Credit Facility | RCF | — | — | — | Caesars Entertainment, Inc. | — | — | — | — | No | [C24] |
| CEI-TLA | CEI Term Loan A | 1L Term Loan | — | — | — | Caesars Entertainment, Inc. | — | — | — | — | No | [C25] |
| CVA-DDTL | CVA Delayed Draw Term Loan | 1L Term Loan | — | — | — | Caesars Virginia, LLC | — | — | — | — | No | [C26] |
| CEI-TLB | CEI Term Loan B | 1L Term Loan | BL3912045 | — | — | Caesars Entertainment, Inc. | Ba3 | BB | — | — | Yes | [C64] |
| CEI-TLB-1 | CEI Term Loan B-1 | 1L Term Loan | BL4120876 | — | — | Caesars Entertainment, Inc. | Ba3 | BB | — | — | Yes | [C65] |
| CEI-SSN-2030 | CEI Senior Secured Notes due 2030 | SS Notes | BO1185520 | US12769GAA87 | — | Caesars Entertainment, Inc. | B1 | BB- | — | — | Yes | [C66] |
| CEI-SSN-2032 | CEI Senior Secured Notes due 2032 | SS Notes | BO2201453 | US12769GAC44 | 12769GAC4 | Caesars Entertainment, Inc. | B1 | BB- | — | 103.250 from 2027-02-15; 101.625 from 2028-02-15; 100.000 from 2029-02-15 | Yes | [C67] [C68] [C69] |
| CEI-SN-2029 | CEI Senior Notes due 2029 | SU Notes | BO1203310 | US12769GAB60 | — | Caesars Entertainment, Inc. | Caa1 | B- | — | — | Yes | [C70] |
| CEI-SN-2032 | CEI Senior Notes due 2032 | SU Notes | BO2219978 | US12769GAD27 | 12769GAD2 | Caesars Entertainment, Inc. | Caa1 | B- | — | — | Yes | [C71] [C72] |
| SID-BONDS | Special Improvement District Bonds | Other | — | — | — | Caesars Entertainment, Inc. | — | — | — | — | No | [C33] |
| OTHER-PAYABLES | Long-term notes and other payables | Other | — | — | — | Caesars Entertainment, Inc. | — | — | — | — | No | [C34] |
| NEW-1 | New Senior Secured Term Loan B | 1L Term Loan | — | — | — | Caesars Entertainment, Inc. | Ba3 | BB- | — | — | No | [C73] |

<!-- table: cp1.reconciliation_checks -->
| check_id | period_id | check_type | reported_value | calculated_value | difference | status | explanation | cite |
|---|---|---|---|---|---|---|---|---|
| R-1 | H1_2026 | DEBT_TOTAL | 11705 | 11705 | 0 | PASS | facility book values sum to total debt | [C9] |
| R-2 | FY2025 | DEBT_TOTAL | 11792 | 11792 | 0 | PASS | facility book values sum to total debt | [C9] |
| R-3 | FY2025 | ADJUSTED_EBITDA_BRIDGE | 3624 | 3624 | 0 | PASS | operating income 1,858 plus D&A 1,417 plus impairment, transaction costs and stock-based compensation | [C13] |
| R-4 | FY2024 | ADJUSTED_EBITDA_BRIDGE | 3739 | 3739 | 0 | PASS | operating income 2,304 plus D&A 1,324 plus the three add-backs | [C13] |
| R-5 | FY2023 | ADJUSTED_EBITDA_BRIDGE | 3938 | 3938 | 0 | PASS | operating income 2,472 plus D&A 1,261 plus the three add-backs | [C13] |
| R-6 | H1_2026 | ADJUSTED_EBITDA_BRIDGE | 1807 | 1807 | 0 | PASS | operating income 1,013 plus D&A 702 plus transaction costs and stock-based compensation | [C4] |
| R-7 | H1_2025 | ADJUSTED_EBITDA_BRIDGE | 1839 | 1839 | 0 | PASS | operating income 1,014 plus D&A 721 plus transaction costs and stock-based compensation | [C4] |
| R-8 | FY2025 | SEGMENT_REVENUE | 11486 | 11486 | 0 | PASS | four segments plus Corporate and Other | [C10] |
| R-9 | H1_2026 | SEGMENT_REVENUE | 5863 | 5863 | 0 | PASS | four segments plus Corporate and Other | [C1] |
| R-10 | H1_2025 | SEGMENT_REVENUE | 5701 | 5701 | 0 | PASS | four segments plus Corporate and Other | [C1] |
| R-11 | H1_2026 | NET_DEBT_ISSUER | 10842 | 10740 | 102 | WARN | the issuer's net debt is on face value (11,807); the registers carry book (11,705) | [C46] |
| R-12 | LTM_Q2_2026 | PF_TOTAL_DEBT | 14687 | 14585 | 102 | WARN | the pro forma capitalisation is on face value; book total debt plus the new tranche less the repaid revolver is 14,585 | [C50] |

<!-- table: cp1.definition_conflicts -->
| metric_id | issuer_definition | canonical_definition | periods_affected | materiality | resolution | cite |
|---|---|---|---|---|---|---|
| adjusted_ebitda | excludes the rent on leases accounted for as financing obligations (charged to interest expense) | EBITDA after every operating cost, before the house add-back review | FY2023 to H1 2026 | High | registers carry the issuer figure; it pairs with total debt that excludes the 13,157 financing obligations, so lease-adjusted leverage needs both (CP-1D) | [C44] [C45] |
| cash_interest_paid | cash interest paid for debt shown apart from cash interest paid for rent on the GLPI and VICI leases (686 in H1 2026) | cash interest paid on debt | FY2023 to H1 2026 | High | registers carry interest on debt only; the rent is lease cash for CP-1D | [C74] |
| total_debt | total outstanding indebtedness at face value (11,807) | carrying value of debt at book | H1 2026, FY2025 | Low | registers carry book (11,705); face is in the debt note and the pro forma capitalisation | [C46] |

<!-- table: cp1.entity_profile -->
| entity | role | fiscal_year_end | reporting_currency | reporting_unit | perimeter | accounting_basis | cite |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Borrower | 12-31 | USD | MILLIONS | Consolidated | US GAAP | [C75] |

## Gaps

- `cp1.model_account_register`, total_debt / FY2023, `value`: the Form 10-K's debt note shows December 31, 2025 and 2024 only.
- `cp1.operating_kpi_schedule`: the pack reports no operating KPI (visits, occupancy) for any period.
- `cp1.equity_value`: no listed market capitalisation in the Market Context; the merger values Caesars at about 17.6 billion including debt [C76], which is not a listed equity value.
- `cp1.debt_facility_register`: the CVA Delayed Draw Term Loan's margin, floor and amortisation amount are not stated; the Special Improvement District Bonds' amortisation is not stated.
- `cp1.instrument_identity`: call schedules are in the pack for the 2032 senior secured notes only; no Fitch rating and no corporate rating is in the pack.
- `NEW-1`: Price Talk is not final, so `spread_bps` is a gap; the pro forma figures are SYNTHETIC arranger estimates.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_Q2_2026_10Q.txt | Statements of Operations | Net revenues \| 2,993 \| 2,907 \| 5,863 \| 5,701 |
| C2 | CZR_Q2_2026_10Q.txt | Statements of Operations | Total operating expenses \| 2,480 \| 2,381 \| 4,850 \| 4,687 |
| C3 | CZR_Q2_2026_10Q.txt | Statements of Operations | Depreciation and amortization \| 355 \| 364 \| 702 \| 721 |
| C4 | CZR_Q2_2026_Earnings_Release.txt | Reconciliation to Adjusted EBITDA | Adjusted EBITDA \| $920 \| $955 \| $1,807 \| $1,839 |
| C5 | CZR_Q2_2026_10Q.txt | Supplemental cash flow information | Cash interest paid for debt \| $368 \| $405 |
| C6 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows | Purchase of property and equipment \| (335) \| (453) |
| C7 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows | Net cash provided by operating activities \| 675 \| 680 |
| C8 | CZR_Q2_2026_10Q.txt | Balance Sheets | Cash and cash equivalents \| $965 \| $887 |
| C9 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | Total debt \| 11,807 \| 11,705 \| 11,792 |
| C10 | CZR_FY2025_10K.txt | Consolidated Statements of Operations | Net revenues \| 11,486 \| 11,245 \| 11,528 |
| C11 | CZR_FY2025_10K.txt | Consolidated Statements of Operations | Total operating expenses \| 9,628 \| 8,941 \| 9,056 |
| C12 | CZR_FY2025_10K.txt | Consolidated Statements of Operations | Depreciation and amortization \| 1,417 \| 1,324 \| 1,261 |
| C13 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Adjusted EBITDA \| 3,624 \| 3,739 \| 3,938 |
| C14 | CZR_FY2025_10K.txt | Supplemental disclosure of cash flow information | Cash interest paid for debt \| $813 \| $1,052 \| $846 |
| C15 | CZR_FY2025_10K.txt | Consolidated Statements of Cash Flows | Purchase of property and equipment \| (805) \| (1,296) \| (1,264) |
| C16 | CZR_FY2025_10K.txt | Consolidated Statements of Cash Flows | Net cash provided by operating activities \| 1,302 \| 1,075 \| 1,809 |
| C17 | CZR_FY2025_10K.txt | Reconciliation of cash to the balance sheets | Cash and cash equivalents \| $887 \| $866 \| $1,005 |
| C18 | CZR_FY2025_10K.txt | Note 9. Long-Term Debt | Total debt \| 11,905 \| 11,792 \| 12,154 |
| C19 | CZR_Q2_2026_Earnings_Release.txt | Reconciliation to Adjusted EBITDA | Transaction costs and other, net (a) \| 29 \| 41 \| 45 \| 54 |
| C20 | CZR_Q2_2026_Earnings_Release.txt | Reconciliation to Adjusted EBITDA | Stock-based compensation expense \| 23 \| 24 \| 47 \| 50 |
| C21 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Impairment charges (c) \| 182 \| 302 \| 95 |
| C22 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Transaction costs and other, net (d) \| 72 \| (285) \| 6 |
| C23 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation | Stock-based compensation expense \| 95 \| 94 \| 104 |
| C24 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Revolving Credit Facility \| 2028 \| variable \| $120 \| $120 \| $160 |
| C25 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Term Loan A \| 2028 \| variable \| 619 \| 618 \| 636 |
| C26 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CVA Delayed Draw Term Loan \| 2029 \| variable \| 376 \| 372 \| 381 |
| C27 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Term Loan B \| 2030 \| variable \| 2,018 \| 1,993 \| 2,002 |
| C28 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Term Loan B-1 \| 2031 \| variable \| 2,835 \| 2,808 \| 2,820 |
| C29 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Senior Secured Notes due 2030 \| 2030 \| 7.00% \| 2,000 \| 1,987 \| 1,986 |
| C30 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Senior Secured Notes due 2032 \| 2032 \| 6.50% \| 1,500 \| 1,487 \| 1,486 |
| C31 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Senior Notes due 2029 \| 2029 \| 4.625% \| 1,200 \| 1,193 \| 1,192 |
| C32 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | CEI Senior Notes due 2032 \| 2032 \| 6.00% \| 1,100 \| 1,088 \| 1,087 |
| C33 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | Special Improvement District Bonds \| 2037 \| 4.30% \| 38 \| 38 \| 40 |
| C34 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt | Long-term notes and other payables \| 1 \| 1 \| 2 |
| C35 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | aggregate principal amount of $2.25 billion ... will mature on January 31, 2028 |
| C36 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | applicable margin is 2.25% per annum in the case of any Adjusted Term SOFR loan |
| C37 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | 1.25% of the original aggregate principal amount of the CEI Term Loan A |
| C38 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | CEI Term Loan B, as amended, bear interest ... subject to a floor of 0.50% |
| C39 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | The CEI Term Loan B will mature on February 6, 2030. |
| C40 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | The CEI Term Loan B-1 will mature on February 6, 2031. |
| C41 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | 0.25% of the original aggregate principal amount of the CEI Term Loan B, |
| C42 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | 0.25% of the original aggregate principal amount of the CEI Term Loan B-1, |
| C43 | CZR_Q2_2026_10Q.txt | Terms of Outstanding Debt | up to an aggregate principal amount of $400 million (the “CVA Delayed Draw Term Loan”) |
| C44 | CZR_Q2_2026_Earnings_Release.txt | Non-GAAP Measures | leases ... accounted for as financing obligations and the associated expense is included in interest |
| C45 | CZR_Q2_2026_10Q.txt | Balance Sheets | Long-term financing obligations \| 13,157 \| 13,096 |
| C46 | CZR_Q2_2026_Earnings_Release.txt | Balance Sheet and Liquidity | Net debt (a) \| $10,842 \| $11,018 |
| C47 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Maturity \| 2033-12-15 (seven years from expected closing) |
| C48 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Capitalisation | New Senior Secured Term Loan B \| 0 \| 3,000 \| 3,000 |
| C49 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Capitalisation | CEI Revolving Credit Facility \| 120 \| (120) \| 0 |
| C50 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Capitalisation | Total debt \| 11,807 \| 2,880 \| 14,687 |
| C51 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Capitalisation | Cash and cash equivalents \| 965 \| 100 \| 1,065 |
| C52 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Earnings and interest | Run-rate cost synergies identified by Fertitta Entertainment, not yet realised \| 150 |
| C53 | CZR_FY2025_10K.txt | Results of operations by segment | Las Vegas \| $4,049 \| $4,274 \| $4,470 |
| C54 | CZR_FY2025_10K.txt | Results of operations by segment | Regional \| 5,756 \| 5,539 \| 5,778 |
| C55 | CZR_FY2025_10K.txt | Results of operations by segment | Caesars Digital \| 1,408 \| 1,163 \| 973 |
| C56 | CZR_FY2025_10K.txt | Results of operations by segment | Managed and Branded \| 279 \| 274 \| 307 |
| C57 | CZR_FY2025_10K.txt | Results of operations by segment | Corporate and Other (a) \| (6) \| (5) \| — |
| C58 | CZR_Q2_2026_Earnings_Release.txt | Net Revenues, six months ended June 30 | Las Vegas \| $2,020 \| $2,057 \| (1.8)% |
| C59 | CZR_Q2_2026_Earnings_Release.txt | Net Revenues, six months ended June 30 | Regional \| 3,000 \| 2,823 \| 6.3% |
| C60 | CZR_Q2_2026_Earnings_Release.txt | Net Revenues, six months ended June 30 | Caesars Digital \| 725 \| 678 \| 6.9% |
| C61 | CZR_Q2_2026_Earnings_Release.txt | Net Revenues, six months ended June 30 | Managed and Branded \| 123 \| 141 \| (12.8)% |
| C62 | CZR_Q2_2026_Earnings_Release.txt | Net Revenues, six months ended June 30 | Corporate and Other \| (5) \| 2 \| * |
| C63 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Earnings and interest | Pro forma cash interest paid for debt, LTM \| 989 |
| C64 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 4 | CZR TL B 2030,BL3912045,,1L Term Loan,99.375,99.750,99.563,,252,Ba3,BB |
| C65 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 5 | CZR TL B-1 2031,BL4120876,,1L Term Loan,99.500,99.875,99.688,,241,Ba3,BB |
| C66 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 6 | CZR 7.00 02/15/30,BO1185520,US12769GAA87,Senior Secured Notes |
| C67 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 7 | CZR 6.50 02/15/32,BO2201453,US12769GAC44,Senior Secured Notes |
| C68 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | CUSIP: 12769GAC4 |
| C69 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | Paragraph 5, optional redemption | 2027 \| 103.250% |
| C70 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 8 | CZR 4.625 10/15/29,BO1203310,US12769GAB60,Senior Notes |
| C71 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 9 | CZR 6.00 10/15/32,BO2219978,US12769GAD27,Senior Notes |
| C72 | CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | p.1 | CUSIP: 12769GAD2 |
| C73 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Expected facility ratings \| Ba3 (Moody's) / BB- (S&P) |
| C74 | CZR_Q2_2026_10Q.txt | Supplemental cash flow information | Cash interest paid for rent related to GLPI and VICI Leases \| 686 \| 672 |
| C75 | CZR_Q2_2026_10Q.txt | Balance Sheets | CONSOLIDATED CONDENSED BALANCE SHEETS |
| C76 | CZR_2026_Merger_Press_Release.txt | p.1 | all-cash transaction valued at approximately $17.6 billion |
