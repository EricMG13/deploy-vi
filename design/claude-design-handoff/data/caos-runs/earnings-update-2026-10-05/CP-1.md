---
module_id: "CP-1"
module_name: "CanonicalDataFoundation"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "EARNINGS_UPDATE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1-a431b9720d95afc6"
credit_os_route_node_id: "RN-FULL_CREDIT_32-EARNINGS_UPDATE-02-CP-1"
credit_os_invocation_sha256: "5978c55b9680fe4d298a27f1c9e65271609ad18b83c3203a68d44ba054a93c87"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "391239d01ae8de0a192795066295a2f1d36f6c68d683de2a4deb87dac9933ddd"
confidence_score: 59
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, MODEL_INTERFACE_PARTIAL, DERIVED_KPI_GAPS]
validation_warnings: [MATERIAL_SOURCE_GAPS_RECORDED, SCRIPT_OWNED_DERIVATIONS_NOT_EXECUTED, HOST_VALIDATION_FOLLOWS]
downstream_consumers: [CP-1B, CP-1C, CP-2, CP-2A, CP-2D, CP-3, CP-3C, CP-4, CP-4A, CP-6, CP-5, CP-5A, CP-MODEL]
---

## Audit Summary

- **Canonical filename:** `CZR_CP-1_20261002.md`.
- **Module / object:** CP-1 CanonicalDataFoundation / canonical financial data and KPIs.
- **Status:** Restricted; the filings provide substantial current financial evidence, but several derived metrics and model reconciliations remain unavailable in this run. Complete executed financing documents and current market or rating evidence were not delivered.
- **Confidence:** 59 / Low. The score is capped at 59 because material coverage and calculation limitations remain.
- **Committee status:** Requires More Work. This is a canonical data handoff, not an independent credit recommendation.
- **Basis:** Consolidated Caesars Entertainment, Inc.; USD millions; US GAAP. Q2 2026 and H1 2026 are unaudited; FY2025 is audited. Debt is normalized to balance-sheet carrying value, including current debt and long-term debt, net of disclosed financing costs.

## Analysis

### Analytical read-through

Caesars’ Q2 revenue rose to $2,993 million from $2,907 million, while issuer-reported Adjusted EBITDA fell to $920 million from $955 million and the reported margin declined to 30.7% from 32.9% [C1, C4, C13]. This weakens the earnings cushion available to service debt and substantial lease payments; Adjusted EBITDA is not a liquidity measure. The balance sheet reports $965 million of cash, but debt must be carried at the balance-sheet basis rather than the debt-note face-value total [C8, C9, C10]. The 10-Q balance sheet reports current and long-term debt separately [C22, C24]. Las Vegas deterioration is partly offset by Regional growth, although Caesars Windsor’s transfer into Regional makes the comparison less like-for-like [C15, C16, C27]. A $545 million customer-deposit/deferred-revenue balance is operating float, not ordinary payables [C12]. July’s Alberta launch is subsequent to Q2 and is excluded from period figures [C17].

**Largest supported changes and creditor transmission.** Revenue increased year over year while reported Adjusted EBITDA decreased; the margin contraction means the reported revenue growth did not translate into a larger operating earnings cushion. If leisure visitation or gaming hold weakens further, lower property contribution and fixed operating costs can pressure cash available for debt service and leases. The strongest counterpoint is positive Regional performance and reported H1 operating cash flow of $675 million; it would materially improve the durability case if sustained on a comparable perimeter and after recurring capital spending and lease cash requirements [C5, C15, C16].

**Perimeter and definition controls.** Regional growth is not wholly organic: Caesars Windsor operations are reported in Regional beginning March 3, 2026. Preserve issuer segment labels and do not treat the entire reported increase as same-property growth [C16, C27]. Adjusted EBITDA is an issuer-defined, unaudited performance measure and excludes cash uses including capex, interest, principal, and lease payments; it is not a substitute for cash flow [C4, C13, C23]. Debt-note face value, book value, deferred financing costs, and balance-sheet carrying value are distinct figures. The canonical debt metric below uses balance-sheet carrying values; both bases and their reconciliation gap are retained in T4.11 [C9, C10, C22, C24].

**Liquidity, float, and downside path.** The 10-Q reports $965 million cash and $2,130 million CEI revolver capacity net of outstanding balance, while estimated remaining-2026 debt service is approximately $425 million and lease payments to VICI and GLPI approximately $687 million. These are distinct obligations and the filing’s liquidity capacity is not a calculation of covenant headroom [C8, C11, C25, C28]. Customer deposits and other deferred revenue rose to $545 million from $492 million at year-end; these amounts represent gaming deposits and advance payments for goods and services. A demand shock, cancellations, or weaker customer activity could convert a funding source into delivery, redemption, or refund-related cash needs, reducing liquidity quality [C12]. The 10-Q reports covenant compliance at June 30, 2026, but full executed agreements and calculated headroom are not in the delivered source set [C26].

**Downside sequence and monitoring.** An initial fall in discretionary visitation, hotel occupancy, table volume, or gaming hold would first reduce property revenues and contribution; labor, rent, maintenance capex, and debt service would then limit the cash-flow offset. Persistent weakness could reduce liquidity and refinancing flexibility before any reported covenant breach. Monitor Las Vegas visitation/occupancy and margins, Regional performance on a comparable Windsor perimeter, Digital hold and promotional costs, operating cash flow after capex and leases, customer-deposit movements, and covenant calculations when the agreements are available [C15, C16]. No stress number is inferred.

**Subsequent event.** Caesars launched mobile sports betting and iGaming in Alberta on July 13, 2026. This is after the June 30 balance-sheet date and is not included in Q2 or H1 figures. Its earnings, cash-flow, and investment effects are not quantified in the delivered evidence [C17]. Separately, the 10-Q records that Caesars entered into a merger agreement on May 27, 2026 [C29]; no transaction effect is blended into period figures.

**Model and downstream readiness.** Source financial statements and segment schedules support downstream analysis with limitations. The derived-period and KPI scripts were not delivered in this interaction; script-owned LTM and derived KPI cells are therefore left unavailable rather than hand-derived. The CP-MODEL interface is populated with available reported periods and named facilities, but fewer than four discrete quarters and incomplete reconciliation checks prevent `ready` status. Obtain the complete underwriting source pack, current executed financing documents, and a complete quarterly history before model-dependent use.

### Analytical appendix — complete canonical registers

#### T4.1 — Source Register

| Source File Name | Document Type | Period Coverage | Currency | Unit | Perimeter | Accounting Basis | Evidence Quality Tier | Analytical Use | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| CZR_Q2_2026_10Q.txt | Form 10-Q; unaudited interim filing | Q2 and H1 ended 2026-06-30; comparative 2025 | USD | Millions | Caesars Entertainment, Inc. and consolidated subsidiaries | US GAAP interim | Tier 2b; primary filing, unaudited | Primary current-period statements, debt, liquidity, segments, operating data [C1, C4, C8] | Host-prepared text extraction; graphical map absent per accepted CP-0; complete executed financing documents not delivered |
| CZR_FY2025_10K.txt | Form 10-K; audited annual filing | FY2025, FY2024, FY2023 | USD | Millions | Caesars Entertainment, Inc. and consolidated subsidiaries | US GAAP | Tier 1; audited financial statements [C21] | Annual comparison, audited statements, debt, leases, cash flows [C18, C19, C20] | Host-prepared text extraction; stock-performance graph absent per accepted CP-0; annual data does not fill interim quarters |
| CZR_Q2_2026_Earnings_Release.txt | Issuer earnings release | Q2 and H1 ended 2026-06-30; comparative 2025 | USD | Millions | Consolidated issuer; segment summaries | Non-GAAP supplemental measures alongside reported GAAP highlights | Tier 2c; issuer release, unaudited | Corroborates reported Q2 Adjusted EBITDA and provides summary liquidity [C4] | Not controlling over 10-Q; Adjusted EBITDA is non-GAAP and issuer-defined |

#### T4.2 — Entity Period Key

| Entity Name | Entity Role | Fiscal Year End | Reporting Currency | Reporting Unit | Consolidation Perimeter | Accounting Basis | Available Periods |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. and consolidated subsidiaries | Registrant and consolidated reporting entity | December 31 | USD | Millions | Consolidated; includes controlled subsidiaries and consolidated VIEs; no separate finance-company perimeter identified in supplied statements [C23] | US GAAP; interim unaudited, FY2025 audited [C21] | Q2 2026, H1 2026, Q2 2025, H1 2025, FY2025, FY2024; balance-sheet dates June 30 2026, December 31 2025 and December 31 2024. **Subsequent Event:** Alberta mobile sports betting and iGaming launched July 13, 2026; excluded from reporting-period figures [C17]. |

#### T4.3 — Normalization Register

| Description | Source | Type | Before | After | Rationale | Periods |
|---|---|---|---|---|---|---|
| Reporting basis standardized to USD millions, consolidated issuer perimeter, US GAAP; no currency translation or perimeter adjustment applied. Debt normalized to current portion plus balance-sheet long-term carrying value; debt-note face/principal and book totals retained as separate definitions. | CZR_Q2_2026_10Q.txt pp. 2, 9; CZR_FY2025_10K.txt pp. 29, 40 [C9, C10, C22, C24] | Basis alignment; debt carrying-value normalization | Source statements and debt note show separate face, book, and balance-sheet lines | USD millions; consolidated; carrying-value debt basis | Avoids face-value substitution and silent reconciliation; see conflict CF-1 in T4.11 | Q2 2026; FY2025; FY2024 |

#### T4.4 — Income Statement

| Line Item | FY2025 | FY2024 | Q2 2026 | Q2 2025 | H1 2026 | H1 2025 |
|---|---:|---:|---:|---:|---:|---:|
| Revenue [C1, C18] | 11,486 | 11,245 | 2,993 | 2,907 | 5,863 | 5,701 |
| COGS [C1] | — | — | — | — | — | — |
| Gross Profit [C1] | — | — | — | — | — | — |
| SG&A / General and administrative [C2] | 1,926 | 1,920 | 521 | 477 | 1,025 | 960 |
| Other Operating Expenses, total operating expenses [C2] | 9,628 | 8,941 | 2,480 | 2,381 | 4,850 | 4,687 |
| EBITDA (Reported) [C2] | — | — | — | — | — | — |
| EBITDA (Adjusted), issuer-reported [C4] | 3,624 | 3,739 | 920 | 955 | 1,807 | 1,839 |
| Depreciation and amortization [C2] | 1,417 | 1,324 | 355 | 364 | 702 | 721 |
| EBIT / Operating income [C2] | 1,858 | 2,304 | 513 | 526 | 1,013 | 1,014 |
| Interest Expense, total, net [C3] | (2,304) | (2,366) | (573) | (579) | (1,142) | (1,153) |
| Interest Expense, cash paid for debt [C7] | (813) | (1,052) | — | — | (368) | (405) |
| Interest income [C3] | 20 | 11 | 3 | 7 | 5 | 13 |
| Other non-operating income [C3] | 2 | 27 | 7 | 1 | 5 | — |
| Pretax income (loss) [C2] | (448) | (124) | (53) | (52) | (124) | (139) |
| Tax, total benefit (provision) [C2] | 11 | (87) | 12 | (13) | — | (24) |
| Tax, cash paid [C7] | (81) | (48) | — | — | (11) | (58) |
| Net income (loss) attributable to Caesars [C2] | (502) | (278) | (62) | (82) | (160) | (197) |
| Exceptionals: transaction and other costs, net [C4] | 38 | (331) | 16 | 34 | 20 | 36 |
| Stock-based compensation expense [C4] | 95 | 94 | 23 | 24 | 47 | 50 |

#### T4.5 — Cash Flow Statement

| Line Item | FY2025 | FY2024 | H1 2026 | H1 2025 |
|---|---:|---:|---:|---:|
| OCF / CFO, reported [C19, C5] | 1,302 | 1,075 | 675 | 680 |
| OCF before working-capital change [C5] | — | — | — | — |
| Working-capital change, aggregate [C5] | — | — | — | — |
| Capex, maintenance [C6] | — | — | 181 | — |
| Capex, growth and renovation [C6] | — | — | 154 | — |
| Capex, total [C6] | (805) | (1,296) | (335) | (453) |
| FCF, levered [C5, C6] | — | — | — | — |
| FCF, unlevered [C5, C6] | — | — | — | — |
| Dividends paid [C5] | — | — | — | — |
| Acquisitions, net disclosed asset acquisitions [C5] | — | — | (98) | — |
| Disposals, proceeds from property and equipment [C5] | — | — | 20 | — |
| Debt issuance / repayment, net [C5] | (389) | (145) | (98) | (22) |
| Equity issuance / buyback [C5] | (229) | (191) | — | (100) |
| Net cash change, cash, cash equivalents and restricted cash [C5] | (32) | (127) | 93 | 70 |
| Cash taxes paid [C7] | (81) | (48) | (11) | (58) |
| Cash interest paid for debt [C7] | (813) | (1,052) | (368) | (405) |

#### T4.6 — Balance Sheet

| Line Item | June 30 2026 | December 31 2025 | December 31 2024 |
|---|---:|---:|---:|
| Cash and equivalents [C8] | 965 | 887 | 866 |
| Restricted cash [C24] | 96 | 85 | 95 |
| Short-term investments [C24] | 2 | 2 | 2 |
| Trade receivables, net [C24] | 485 | 476 | 470 |
| Inventories [C24] | 49 | 43 | 45 |
| Other current assets [C24] | 382 | 312 | 271 |
| Total current assets [C24] | 1,977 | 1,803 | 1,747 |
| PP&E, net [C24] | 14,125 | 14,358 | 14,812 |
| Goodwill [C24] | 10,441 | 10,441 | 10,601 |
| Other intangible assets [C24] | 3,959 | 3,985 | 4,133 |
| Other non-current assets [C24] | 1,240 | 919 | 1,297 |
| Total assets [C24] | 31,742 | 31,639 | 32,590 |
| Short-term debt [C24] | — | — | — |
| Current portion of long-term debt [C22] | 114 | 114 | 109 |
| Trade payables [C24] | 290 | 297 | 296 |
| Accrued interest [C24] | 222 | 224 | 242 |
| Other current liabilities [C24] | 1,696 | 1,618 | 1,625 |
| Total current liabilities [C24] | 2,322 | 2,253 | 2,272 |
| Long-term financing obligations [C24] | 13,157 | 13,096 | 12,899 |
| Long-term debt, carrying value [C10, C24] | 11,585 | 11,670 | 12,033 |
| Canonical total debt: current portion plus long-term carrying value [C10, C22, C24] | 11,699 | 11,784 | 12,142 |
| Senior secured debt [C10] | — | — | — |
| Senior unsecured debt [C10] | — | — | — |
| Subordinated debt [C10] | — | — | — |
| Deferred tax liability [C24] | 57 | 58 | 130 |
| Other non-current liabilities [C24] | 1,069 | 876 | 880 |
| Total liabilities [C24] | 28,190 | 27,953 | 28,214 |
| Total equity [C24] | 3,552 | 3,686 | 4,376 |
| Customer deposits and other deferred revenue, disclosed contract-liability component [C12] | 545 | 492 | 549 |

#### T4.8 — Constructed Period Register

| Metric Name | Derived Period Type | Full-Year Component | Current Stub | Prior-Year Stub | Derived Value | Calculation Status | Source Files | Limitations |
|---|---|---|---|---|---|---|---|---|
| Revenue | LTM through 2026-06-30 | FY2025: 11,486 | H1 2026: 5,863 | H1 2025: 5,701 | — | Not Available | CZR_FY2025_10K.txt p.19; CZR_Q2_2026_10Q.txt p.2 [C18, C1] | LTM construction is script-owned; script not delivered. Do not hand-derive. Gap G-1. |
| Adjusted EBITDA | LTM through 2026-06-30 | FY2025: 3,624 | H1 2026: 1,807 | H1 2025: 1,839 | — | Not Available | CZR_FY2025_10K.txt p.19; CZR_Q2_2026_10Q.txt p.16 [C4, C18] | Issuer definition; script-owned construction not executed. Gap G-1. |
| CFO | LTM through 2026-06-30 | FY2025: 1,302 | H1 2026: 675 | H1 2025: 680 | — | Not Available | CZR_FY2025_10K.txt p.31; CZR_Q2_2026_10Q.txt p.4 [C19, C5] | Script-owned construction not executed. Gap G-1. |
| Capital expenditures | LTM through 2026-06-30 | FY2025: 805 | H1 2026: 335 | H1 2025: 453 | — | Not Available | CZR_FY2025_10K.txt p.31; CZR_Q2_2026_10Q.txt p.4 [C6] | Script-owned construction not executed. Gap G-1. |

#### T4.9 — Calculation Register

| Metric Name | Formula | Numerator Value | Numerator Source | Denominator Value | Denominator Source | Period | Currency | Unit | Calculated Value | Calculation Status | Evidence Quality Tier | Limitations |
|---|---|---:|---|---:|---|---|---|---|---|---|---|---|
| Adjusted EBITDA margin, issuer-reported | Adjusted EBITDA / net revenue | 920 | 10-Q p.16 [C4] | 2,993 | 10-Q p.2 [C1] | Q2 2026 | USD | Percent | 30.7% | Verified; issuer-reported ratio [C13] | Primary-Unverified | Non-GAAP; source reports this margin; do not equate to cash margin. |
| Adjusted EBITDA margin, issuer-reported | Adjusted EBITDA / net revenue | 955 | 10-Q p.16 [C4] | 2,907 | 10-Q p.2 [C1] | Q2 2025 | USD | Percent | 32.9% | Verified; issuer-reported ratio [C13] | Primary-Unverified | Non-GAAP; source reports this margin. |
| Adjusted EBITDA margin, issuer-reported | Adjusted EBITDA / net revenue | 3,624 | 10-K p.19 [C18] | 11,486 | 10-K p.19 [C18] | FY2025 | USD | Percent | 31.6% | Verified; issuer-reported ratio | Primary-Unverified | Annual audited statements; Adjusted EBITDA is unaudited supplemental information. |
| Adjusted EBITDA margin, issuer-reported | Adjusted EBITDA / net revenue | 3,739 | 10-K p.19 [C18] | 11,245 | 10-K p.19 [C18] | FY2024 | USD | Percent | 33.3% | Verified; issuer-reported ratio | Primary-Unverified | Adjusted EBITDA is unaudited supplemental information. |
| Debt / EBITDA | Canonical carrying-value debt / matching-period canonical EBITDA | — | T4.6 [C10, C22, C24] | — | T4.4 | Q2 2026 and FY2025 | USD | x | — | Not Calculable | Primary-Unverified | No supported matching-period canonical EBITDA calculation in this handoff; issuer Adjusted EBITDA is not substituted. Gap G-2. |
| Net debt / EBITDA | (carrying-value debt − unrestricted cash) / matching-period canonical EBITDA | — | T4.6 [C8, C10, C22, C24] | — | T4.4 | Q2 2026 and FY2025 | USD | x | — | Not Calculable | Primary-Unverified | Matching-period canonical EBITDA not available; restricted cash excluded. Gap G-2. |
| Senior secured debt / EBITDA | Carrying-value senior secured debt / canonical EBITDA | — | T4.6 [C10] | — | T4.4 | Q2 2026 | USD | x | — | Not Calculable | Primary-Unverified | Balance-sheet debt is not classified by seniority in a single carrying-value total. Gap G-2. |
| Cash interest coverage | EBITDA / cash interest paid | — | T4.4 [C4] | — | T4.5 [C7] | Q2 2026 | USD | x | — | Not Calculable | Primary-Unverified | Cash interest paid is disclosed for H1, not Q2; no quarterly split. Gap G-3. |
| FCF and FCF conversion | CFO − total capex; FCF / EBITDA | — | T4.5 [C5] | — | T4.5 [C6] | FY2025; H1 2026 | USD | Millions / percent | — | Not Calculable | Primary-Unverified | Script-owned KPI not computed; lease cash uses are additional. Gap G-1. |
| Liquidity / debt | Cash plus committed undrawn facilities / canonical carrying debt | — | 10-Q p.22 [C8, C11] | — | T4.6 [C10, C22, C24] | June 30 2026 | USD | x | — | Not Calculable | Primary-Unverified | Revolver capacity has reservations and subsidiary-specific availability; no consolidated canonical KPI computed. Gap G-2. |

#### T4.10 — KPI Dashboard

| KPI Category | Metric Name | FY2025 | Q2 2026 | Q2 2025 | H1 2026 | H1 2025 | Trend Direction | Analyst Note |
|---|---|---:|---:|---:|---:|---:|---|---|
| Earnings | Net revenue [C1, C18] | 11,486 | 2,993 | 2,907 | 5,863 | 5,701 | Higher | Reported quarterly and H1 revenue increased year over year. |
| Earnings | Adjusted EBITDA, issuer-reported [C4, C18] | 3,624 | 920 | 955 | 1,807 | 1,839 | Lower | Q2 and H1 earnings declined despite revenue growth. |
| Margin | Adjusted EBITDA margin, issuer-reported [C13] | 31.6% | 30.7% | 32.9% | 30.8% | 32.3% | Lower | Issuer-reported margin contraction; non-GAAP performance measure. |
| Cash flow | CFO [C19, C5] | 1,302 | — | — | 675 | 680 | Slightly lower H1 | Q2 CFO not separately reported in supplied source; no quarterly inference. |
| Capital spending | Total capex [C6] | 805 | — | — | 335 | 453 | Lower H1 | Maintenance/growth split is only reported for H1 2026. |
| Liquidity | Cash and equivalents [C8] | — | 965 | — | — | — | — | Balance-sheet date measure; restricted cash excluded. |
| Debt | Carrying-value total debt [C10, C22, C24] | — | 11,699 | — | — | — | — | Current plus long-term carrying value; do not use gross principal as leverage denominator. |
| Operating float | Customer deposits and other deferred revenue [C12] | 492 | 545 | 586 | 545 | 586 | Higher since year-end; lower year over year | Funding float with customer performance/redemption obligations; not accounts payable. |

#### T4.11 — Definition Conflict Register

| Metric Name | Canonical Definition | Issuer-Reported Definition | Source of Conflict | Periods Affected | Materiality | Downstream Modules Affected | Resolution / Recommendation |
|---|---|---|---|---|---|---|---|
| Debt / carrying value versus face value (CF-1) | Total Debt equals balance-sheet current plus long-term carrying value, net of financing costs; Net Debt subtracts cash and equivalents. | Debt note presents face value and book value totals, then current portion and deferred financing-cost adjustments; issuer earnings release describes aggregate principal amount. | 10-Q debt note and balance sheet; earnings release [C9, C10, C22, C24] | June 30 2026; FY2025; FY2024 | Material: figures differ by financing costs and current classification; incorrect denominator changes leverage. | CP-1B, CP-2, CP-3, CP-3C, CP-4, CP-4A, CP-MODEL | Use carrying-value total of 11,699 at June 30 2026 from current 114 plus long-term 11,585; retain face/book schedule separately. FY2025 carrying total 11,784. Instrument adjustment and complete reconciliation remain open. |
| EBITDA / Adjusted EBITDA (CF-2) | Canonical EBITDA is a consistently defined earnings measure; issuer Adjusted EBITDA remains separately labelled and is not presumed equivalent. | Issuer Adjusted EBITDA excludes specified interest, tax, D&A, stock compensation and other items; it is unaudited and may differ from debt-agreement definitions. | 10-Q non-GAAP definition and reconciliation [C4, C13] | Q2/H1 2026 and 2025; FY2025 and FY2024 | Material: leverage, coverage and covenant measures can change with addbacks and agreement-specific definitions. | CP-1B, CP-2, CP-4, CP-4A, CP-MODEL | Keep issuer-reported Adjusted EBITDA distinct. Do not calculate canonical leverage or covenant capacity from it absent an explicit matched definition. |
| Segment comparability / Caesars Windsor (CF-3) | Period comparisons require consistent reporting perimeter. | Operations moved from Managed and Branded to Regional beginning March 3, 2026. | 10-Q segment disclosure [C16, C27] | 2026 versus 2025 Q2/H1 | Material for Regional growth attribution. | CP-1B, CP-2, CP-MODEL | Retain source segment presentation; flag Windsor and avoid representing reported Regional growth as wholly comparable organic growth. |
| Interest expense versus cash interest and lease cash payments (CF-4) | Interest coverage denominator must state whether it is accrued P&L interest or cash interest paid; lease cash payments remain separate. | P&L net interest expense is reported separately from cash interest paid for debt and cash interest paid for rent/financing obligations. | 10-Q statements and supplemental cash-flow disclosure [C3, C7, C25] | Q2/H1 2026 and 2025 | Material for debt-service and cash-coverage analysis. | CP-2, CP-2A, CP-4, CP-4A | Do not substitute accrual expense for cash paid or combine lease payments silently. H1 cash paid is available; Q2 split is not. |

#### T4.12 — Gaps & Warnings

| Gap Description | Affected Line Item or Metric | Affected Period(s) | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|---|
| Deterministic period and KPI calculations were not executed; script was not delivered. | T4.8 LTM revenue, Adjusted EBITDA, CFO and capex; T4.9 calculated KPIs | LTM through 2026-06-30; FY2025; H1 2026 | Derived periods, leverage, coverage, FCF and liquidity ratios unavailable; prevents complete canonical KPI build. | MATERIAL (G-1) | Run the governed CP-1 calculation tools in the host environment and replace unavailable values with their output. |
| No supported matching-period canonical EBITDA and insufficient sourced carrying-value seniority subtotals. | T4.9 debt ratios, FFO/debt, coverage and liquidity ratios | Q2/H1 2026; annual comparison | Leverage, covenant-relevant ratios and debt service capacity cannot be calculated from this handoff without adopting issuer Adjusted EBITDA or an unsupported basis. | MATERIAL (G-2) | Obtain the supported canonical EBITDA bridge and classify instrument carrying amounts using the governing debt disclosures; retain issuer-adjusted measures separately. |
| Cash-flow statement is H1/FY, not discrete Q2; cash interest paid is also H1/FY only. | T4.5 CFO, FCF, cash interest, cash taxes | Q2 2026 and Q2 2025 | Quarterly FCF and cash interest coverage unavailable. | MATERIAL (G-3) | Do not derive quarterly flows by estimate; use direct quarterly disclosure if supplied. |
| Gross profit and COGS are not separately presented as such in the supplied statements. | T4.4 COGS, Gross Profit, gross margin | All shown periods | Gross-margin analysis not available on a consistent reported basis. | MINOR (G-4) | Leave null; seek a source-defined gross-profit presentation if required. |
| Reported EBITDA is not separately presented; Adjusted EBITDA is issuer-defined and separately disclosed. | T4.4 EBITDA (Reported), canonical EBITDA and related ratios | All shown periods | Do not silently relabel Adjusted EBITDA as canonical EBITDA. | MATERIAL (G-5) | Maintain separate definitions and obtain a reconciled, approved EBITDA basis before leverage work. |
| LTM cells in T4.8 are null because script-owned period construction was unavailable. | T4.8 all rows | LTM through 2026-06-30 | CP-MODEL and downstream trend metrics lack constructed LTM values. | MATERIAL (G-1) | Run the governed derived-period calculation. |
| Segment data includes five disclosed reporting lines; forecast allocation is a mapping, not a forecast. | T4.16 and allocation table | Q2/H1 2026 and 2025; FY2025 | Segment performance is reported, but Windsor comparability and fewer than four quarters limit model readiness. | MATERIAL (G-6) | Use the source perimeter and obtain four complete quarters for model readiness. |
| Complete executed debt and lease documents and computed covenant headroom are not delivered. | Covenant terms, debt/lease obligations, covenant capacity | June 30 2026 | Limits legal-term verification and covenant-capacity analysis; reported compliance is not headroom. | MATERIAL (G-7) | Obtain current executed agreements, amendments and covenant calculations. |
| July 13 2026 Alberta launch is post-quarter and its financial effect is not quantified. | Subsequent event | After June 30 2026 | Not included in Q2/H1 values; downstream forecast may need separate event treatment. | MINOR (G-8) | Keep excluded from historical periods; assess only when quantified evidence is provided. |
| T4.14 has no missing value-bearing cells; FY fiscal-quarter and direct-period component references are null by design. | T4.14 reference columns | All registered periods | No data gap; reference nulls are permitted. | MINOR | None. |
| T4.18 disclosed-facility rows lack instrument-level commitment for non-revolver debt; some maturity/rate data are not stated for the residual debt line. | T4.18 `commitment`, and residual-facility details | June 30 2026 | Debt schedule cannot satisfy complete per-facility data or CP-MODEL readiness. | MATERIAL (G-9) | Preserve nulls and obtain facility-level schedules and terms; do not infer commitments. |
| T4.19 reconciliation calculated values, differences and tolerances are unavailable because reconciliation calculations were not executed. | T4.19 named checks | Q2/H1 2026; FY2025 | Revenue, EBITDA bridge, CFO identity, debt, cash movement, and annual-to-quarter checks are WARN, not reconciled. | MATERIAL (G-10) | Run governed reconciliation; retain explicit WARN/BLOCK status until evidence closes checks. |

#### T4.13 — Downstream Readiness

| Downstream Module | Readiness Status | Gaps or Limitations | Recommended Actions |
|---|---|---|---|
| CP-1B | Ready with Limitations | Segment comparability; derived KPIs not computed. | Preserve Windsor perimeter transition; use reported source values. |
| CP-1C | Ready with Limitations | No peer/market evidence in this source pack. | Restrict conclusions to issuer financial data; acquire permitted benchmark evidence separately if required. |
| CP-2 | Ready with Limitations | No script-derived KPI/FCF build; executed agreements and covenant headroom absent. | Use carrying-value debt basis; obtain full agreements and complete cash-flow calculations. |
| CP-2A | Ready with Limitations | Cash flow and cash interest are H1/FY; no Q2 cash-flow statement. | Keep quarterly cash measures unavailable; distinguish leases and debt service. |
| CP-2D | Ready with Limitations | Earnings quality affected by Adjusted EBITDA definition and missing derived metrics. | Maintain GAAP results and addbacks separately; complete calculation audit trail. |
| CP-3 | Ready with Limitations | Debt carrying-value and security subtotals require reconciliation. | Use instrument disclosures and preserve unknown classifications. |
| CP-3C | Ready with Limitations | Facility schedule for June 2026 only; full debt-document pack absent. | Obtain complete facility schedule and executed documents. |
| CP-4 | Ready with Limitations | Adjusted EBITDA may differ from debt-agreement definitions. | Do not infer covenant capacity; retain definitions and gaps. |
| CP-4A | Not Ready | No calculated covenant headroom or complete executed documents. | Obtain agreements and the required covenant calculation inputs. |
| CP-6 | Ready with Limitations | Current market and ratings evidence not included; CP-1-derived KPIs incomplete. | Use only issuer-source facts and record source limitations. |
| CP-5 | Ready with Limitations | Receives a traceable source set but derived calculation checks are open. | Audit the completed analytical artifacts and source locators. |
| CP-5A | Ready with Limitations | Confidence and completeness audit must account for open material gaps. | Recompute score and validation against final accepted artifacts. |
| CP-MODEL | blocked | Fewer than four complete discrete quarters; T4.19 checks not calculated; debt-facility carrying-value schedule incomplete for historical quarters. | Obtain at least four quarterly periods, complete facility schedules and reconciliations; only then assess readiness. |

#### T4.14 — Model Period Register

<!-- table-id: cp1.model_period_register -->

| period_id | fiscal_year | fiscal_quarter | period_type | start_date | end_date | day_count | audit_status | currency | unit | accounting_basis | entity_perimeter | source_id | source_locator | component_period_ids |
|---|---:|---:|---|---|---|---:|---|---|---|---|---|---|---|---|
| FY2025 | 2025 | null | FY | 2025-01-01 | 2025-12-31 | 365 | AUDITED | USD | MILLIONS | US GAAP | Consolidated | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K pp. 29, 31, 40 [C18, C19, C20] | null |
| FY2024 | 2024 | null | FY | 2024-01-01 | 2024-12-31 | 366 | AUDITED | USD | MILLIONS | US GAAP | Consolidated | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K pp. 29, 31 [C18, C19] | null |
| Q2_2026 | 2026 | 2 | QUARTER | 2026-04-01 | 2026-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 2-3 [C1, C2] | null |
| Q2_2025 | 2025 | 2 | QUARTER | 2025-04-01 | 2025-06-30 | 91 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 2-3 [C1, C2] | null |
| H1_2026 | 2026 | null | YTD | 2026-01-01 | 2026-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 2-5 [C1, C5, C6] | null |
| H1_2025 | 2025 | null | YTD | 2025-01-01 | 2025-06-30 | 181 | UNAUDITED | USD | MILLIONS | US GAAP | Consolidated | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 2-5 [C1, C5, C6] | null |

#### T4.15 — Model Account Register

<!-- table-id: cp1.model_account_register -->

| metric_id | period_id | value | sign_convention | value_class | calculation_status | source_id | source_locator | conflict_refs | limitation_refs |
|---|---|---:|---|---|---|---|---|---|---|
| revenue | Q2_2026 | 2993 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C1] | null | G-6 |
| revenue | Q2_2025 | 2907 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C1] | null | null |
| revenue | H1_2026 | 5863 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C1] | null | G-6 |
| revenue | H1_2025 | 5701 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C1] | null | null |
| revenue | FY2025 | 11486 | INFLOW_POSITIVE | SOURCE | Verified | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] | null | null |
| revenue | FY2024 | 11245 | INFLOW_POSITIVE | SOURCE | Verified | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] | null | null |
| ebit | Q2_2026 | 513 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.3 [C2] | null | null |
| ebit | H1_2026 | 1013 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.3 [C2] | null | null |
| adjusted_ebitda | Q2_2026 | 920 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] | CF-2 | G-5 |
| adjusted_ebitda | H1_2026 | 1807 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] | CF-2 | G-5 |
| adjusted_ebitda | FY2025 | 3624 | INFLOW_POSITIVE | SOURCE | Verified | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] | CF-2 | G-5 |
| cash_interest_paid | H1_2026 | -368 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.5 [C7] | CF-4 | G-3 |
| cash_interest_paid | H1_2025 | -405 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.5 [C7] | CF-4 | G-3 |
| cash_taxes_paid | H1_2026 | -11 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.5 [C7] | null | G-3 |
| cash_taxes_paid | H1_2025 | -58 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.5 [C7] | null | G-3 |
| cfo_ncfo | H1_2026 | 675 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.4 [C5] | null | G-3 |
| cfo_ncfo | H1_2025 | 680 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.4 [C5] | null | G-3 |
| cfo_ncfo | FY2025 | 1302 | INFLOW_POSITIVE | SOURCE | Verified | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.31 [C19] | null | null |
| capex_and_intangible_investment | H1_2026 | -335 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.4 [C6] | null | G-3 |
| capex_and_intangible_investment | H1_2025 | -453 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.4 [C6] | null | G-3 |
| capex_and_intangible_investment | FY2025 | -805 | OUTFLOW_NEGATIVE | SOURCE | Verified | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.31 [C19] | null | null |
| net_debt_issue_repay | H1_2026 | -98 | OUTFLOW_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.4 [C5] | null | null |
| net_cash_change | H1_2026 | 93 | INFLOW_POSITIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.4 [C5] | null | null |
| cash_and_equivalents | Q2_2026 | 965 | POSITIVE_BALANCE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C8] | null | null |
| cash_and_equivalents | FY2025 | 887 | POSITIVE_BALANCE | SOURCE | Verified | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.29 [C18] | null | null |
| total_debt | Q2_2026 | 11699 | POSITIVE_BALANCE | NORMALIZED | Calculated from balance-sheet current plus long-term carrying value | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.2, 9 [C10, C22, C24] | CF-1 | G-2 |
| total_debt | FY2025 | 11784 | POSITIVE_BALANCE | NORMALIZED | Calculated from balance-sheet current plus long-term carrying value | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K pp.29, 40 [C20] | CF-1 | G-2 |
| net_accounts_receivable | Q2_2026 | 485 | POSITIVE_BALANCE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C24] | null | null |
| inventory | Q2_2026 | 49 | POSITIVE_BALANCE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C24] | null | null |
| accounts_payable | Q2_2026 | 290 | POSITIVE_BALANCE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.2 [C24] | null | null |
| pretax_income | Q2_2026 | -53 | NEGATIVE_FOR_LOSS | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.3 [C2] | null | null |
| income_tax_expense | Q2_2026 | -12 | EXPENSE_POSITIVE_BENEFIT_NEGATIVE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.3 [C2] | null | null |
| rcf_commitment | Q2_2026 | 2250 | POSITIVE_BALANCE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.10 [C11] | null | null |
| rcf_drawn | Q2_2026 | 120 | POSITIVE_BALANCE | SOURCE | Verified | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.9 [C9] | null | null |

#### T4.16 — Segment Revenue Schedule

<!-- table-id: cp1.segment_revenue_schedule -->

| segment_id | segment_name | segment_type | display_priority | period_id | revenue | status | source_id | source_locator |
|---|---|---|---:|---|---:|---|---|---|
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2026 | 1017 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | Q2_2026 | 1570 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CAESARS_DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2026 | 351 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| MANAGED_BRANDED | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2026 | 57 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CORPORATE_OTHER | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2026 | -2 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | Q2_2025 | 1054 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | Q2_2025 | 1435 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CAESARS_DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | Q2_2025 | 343 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| MANAGED_BRANDED | Managed and Branded | OPERATING_SEGMENT | 4 | Q2_2025 | 74 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CORPORATE_OTHER | Corporate and Other | CORPORATE_ELIMINATION | 5 | Q2_2025 | 1 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | H1_2026 | 2020 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | H1_2026 | 3000 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CAESARS_DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2026 | 725 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| MANAGED_BRANDED | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2026 | 123 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CORPORATE_OTHER | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2026 | -5 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | H1_2025 | 2057 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | H1_2025 | 2823 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CAESARS_DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | H1_2025 | 678 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| MANAGED_BRANDED | Managed and Branded | OPERATING_SEGMENT | 4 | H1_2025 | 141 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| CORPORATE_OTHER | Corporate and Other | CORPORATE_ELIMINATION | 5 | H1_2025 | 2 | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.15 [C14] |
| LAS_VEGAS | Las Vegas | OPERATING_SEGMENT | 1 | FY2025 | 4049 | REPORTED | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] |
| REGIONAL | Regional | OPERATING_SEGMENT | 2 | FY2025 | 5756 | REPORTED | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] |
| CAESARS_DIGITAL | Caesars Digital | OPERATING_SEGMENT | 3 | FY2025 | 1408 | REPORTED | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] |
| MANAGED_BRANDED | Managed and Branded | OPERATING_SEGMENT | 4 | FY2025 | 279 | REPORTED | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] |
| CORPORATE_OTHER | Corporate and Other | CORPORATE_ELIMINATION | 5 | FY2025 | -6 | REPORTED | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.19 [C18] |

#### CP-MODEL Segment Allocation

<!-- table-id: cp1.cp_model_segment_allocation -->

| slot_id | slot_label | component_segment_ids |
|---|---|---|
| DIVISION_1 | Las Vegas | LAS_VEGAS |
| DIVISION_2 | Regional | REGIONAL |
| DIVISION_3 | Other reported businesses and eliminations | CAESARS_DIGITAL, MANAGED_BRANDED, CORPORATE_OTHER |

#### CP-MODEL Operating KPI Schedule

<!-- table-id: cp1.operating_kpi_schedule -->

| kpi_id | kpi_label | business_unit | kpi_category | display_priority | period_id | value | unit | value_type | status | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|---|
| LV_TABLE_GAMES_DROP | Table games drop | Las Vegas | GAMING_VOLUME | 1 | Q2_2026 | 706 | USD millions | PERIOD_FLOW | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| LV_TABLE_GAMES_HOLD | Table games hold | Las Vegas | GAMING_HOLD | 2 | Q2_2026 | 16.6 | Percent | RATE | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| LV_HOTEL_OCCUPANCY | Hotel occupancy | Las Vegas | HOTEL | 3 | Q2_2026 | 95.5 | Percent | RATE | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| REGIONAL_TABLE_GAMES_DROP | Table games drop | Regional | GAMING_VOLUME | 1 | Q2_2026 | 1100 | USD millions | PERIOD_FLOW | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| REGIONAL_TABLE_GAMES_HOLD | Table games hold | Regional | GAMING_HOLD | 2 | Q2_2026 | 22.3 | Percent | RATE | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| DIGITAL_SPORTS_HANDLE | Sports betting handle | Caesars Digital | DIGITAL_VOLUME | 1 | Q2_2026 | 2565 | USD millions | PERIOD_FLOW | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| DIGITAL_SPORTS_HOLD | Sports betting hold | Caesars Digital | DIGITAL_HOLD | 2 | Q2_2026 | 8.4 | Percent | RATE | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |
| DIGITAL_IGAMING_HANDLE | iGaming handle | Caesars Digital | DIGITAL_VOLUME | 3 | Q2_2026 | 4831 | USD millions | PERIOD_FLOW | REPORTED | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.20 |

#### T4.17 — Adjusted EBITDA Bridge

<!-- table-id: cp1.adjusted_ebitda_bridge -->

| addback_id | addback_label | addback_classification | realization_status | display_priority | period_id | value | status | source_definition | source_id | source_locator |
|---|---|---|---|---:|---|---:|---|---|---|---|
| NCI_2026Q2 | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | Q2_2026 | 21 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| TAX_2026Q2 | Benefit for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | Q2_2026 | -12 | REPORTED | Same issuer reconciliation; benefit shown as negative adjustment | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| OTHER_INCOME_2026Q2 | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | Q2_2026 | -7 | REPORTED | Same issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| INTEREST_2026Q2 | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 4 | Q2_2026 | 573 | REPORTED | Same issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| DA_2026Q2 | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 5 | Q2_2026 | 355 | REPORTED | Same issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| TRANSACTION_2026Q2 | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 6 | Q2_2026 | 29 | REPORTED | Issuer-described transaction costs and other items; retain exact label | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| SBC_2026Q2 | Stock-based compensation expense | SBC | NOT_STATED | 7 | Q2_2026 | 23 | REPORTED | Issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| NCI_2026H1 | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | H1_2026 | 36 | REPORTED | Issuer reconciliation from net loss attributable to Caesars to Adjusted EBITDA | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| TAX_2026H1 | Benefit for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | H1_2026 | 0 | REPORTED | Issuer reconciliation; displayed dash treated as zero only where the source reports no amount in this reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| OTHER_INCOME_2026H1 | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | H1_2026 | -5 | REPORTED | Same issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| INTEREST_2026H1 | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 4 | H1_2026 | 1142 | REPORTED | Same issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| DA_2026H1 | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 5 | H1_2026 | 702 | REPORTED | Same issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| TRANSACTION_2026H1 | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 6 | H1_2026 | 45 | REPORTED | Issuer-described transaction costs and other items; retain exact label | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| SBC_2026H1 | Stock-based compensation expense | SBC | NOT_STATED | 7 | H1_2026 | 47 | REPORTED | Issuer reconciliation | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.16 [C4] |
| NCI_FY2025 | Net income attributable to noncontrolling interests | OTHER_EXPLICIT | NOT_STATED | 1 | FY2025 | 65 | REPORTED | Issuer reconciliation to Adjusted EBITDA | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| TAX_FY2025 | Benefit for income taxes | OTHER_EXPLICIT | NOT_STATED | 2 | FY2025 | -11 | REPORTED | Issuer reconciliation; tax benefit adjustment | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| OTHER_INCOME_FY2025 | Other income | OTHER_EXPLICIT | NOT_STATED | 3 | FY2025 | -2 | REPORTED | Issuer reconciliation | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| DEBT_EXT_FY2025 | Loss on extinguishment of debt | OTHER_EXPLICIT | NOT_STATED | 4 | FY2025 | 4 | REPORTED | Issuer reconciliation | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| INTEREST_FY2025 | Interest expense, net | OTHER_EXPLICIT | NOT_STATED | 5 | FY2025 | 2304 | REPORTED | Issuer reconciliation | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| IMPAIRMENT_FY2025 | Impairment charges | OTHER_EXPLICIT | NOT_STATED | 6 | FY2025 | 182 | REPORTED | Issuer reconciliation | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| DA_FY2025 | Depreciation and amortization | OTHER_EXPLICIT | NOT_STATED | 7 | FY2025 | 1417 | REPORTED | Issuer reconciliation | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| TRANSACTION_FY2025 | Transaction costs and other, net | TRANSACTION_COSTS | NOT_STATED | 8 | FY2025 | 72 | REPORTED | Issuer-described transaction costs and other items; retain exact label | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |
| SBC_FY2025 | Stock-based compensation expense | SBC | NOT_STATED | 9 | FY2025 | 95 | REPORTED | Issuer reconciliation | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 10-K p.52 [C18] |

#### T4.18 — Debt Facility Register

<!-- table-id: cp1.debt_facility_register -->

| facility_id | facility_name | period_id | facility_type | carrying_value | principal | drawn_amount | commitment | secured_status | seniority | currency | margin_or_coupon | maturity_date | lease_classification | source_id | source_locator |
|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|
| CEI_RCF | CEI Revolving Credit Facility | Q2_2026 | REVOLVER | 120 | 120 | 120 | 2250 | SECURED | SENIOR_SECURED | USD | Variable; SOFR/base plus margin | 2028-01-31 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9, C11] |
| CEI_TLA | CEI Term Loan A | Q2_2026 | TERM_LOAN | 618 | 619 | 619 | null | SECURED | SENIOR_SECURED | USD | Variable; SOFR/base plus margin | 2028-01-31 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CVA_RCF | CVA Revolving Credit Facility | Q2_2026 | REVOLVER | 0 | 0 | 0 | 25 | SECURED | SENIOR_SECURED | USD | Variable; Term SOFR plus margin | 2029-04-26 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CVA_DDTL | CVA Delayed Draw Term Loan | Q2_2026 | TERM_LOAN | 372 | 376 | 376 | 400 | SECURED | SENIOR_SECURED | USD | Variable; Term SOFR plus margin | 2029-04-26 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CEI_TLB | CEI Term Loan B | Q2_2026 | TERM_LOAN | 1993 | 2018 | 2018 | null | SECURED | SENIOR_SECURED | USD | Variable; Term SOFR/base plus margin | 2030-02-06 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CEI_TLB1 | CEI Term Loan B-1 | Q2_2026 | TERM_LOAN | 2808 | 2835 | 2835 | null | SECURED | SENIOR_SECURED | USD | Variable; Term SOFR/base plus margin | 2031-02-06 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CEI_SEC2030 | CEI Senior Secured Notes due 2030 | Q2_2026 | NOTES | 1987 | 2000 | null | null | SECURED | SENIOR_SECURED | USD | 7.00% | 2030-02-15 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CEI_SEC2032 | CEI Senior Secured Notes due 2032 | Q2_2026 | NOTES | 1487 | 1500 | null | null | SECURED | SENIOR_SECURED | USD | 6.50% | 2032-02-15 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp.9-10 [C9] |
| CEI_UNSEC2029 | CEI Senior Notes due 2029 | Q2_2026 | NOTES | 1193 | 1200 | null | null | UNSECURED | SENIOR_UNSECURED | USD | 4.625% | 2029-10-15 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.9 [C9] |
| CEI_UNSEC2032 | CEI Senior Notes due 2032 | Q2_2026 | NOTES | 1088 | 1100 | null | null | UNSECURED | SENIOR_UNSECURED | USD | 6.00% | 2032-10-15 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.9 [C9] |
| SID_BONDS | Special Improvement District Bonds | Q2_2026 | BONDS | 38 | 38 | null | null | NOT_STATED | NOT_STATED | USD | 4.30% | 2037-12-31 | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.9 [C9] |
| OTHER_DEBT | Long-term notes and other payables | Q2_2026 | OTHER | 1 | 1 | null | null | NOT_STATED | NOT_STATED | USD | Not stated | Not stated | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.9 [C9] |
| RCF_COST_ADJ | DEBT ADJUSTMENT — CEI revolver deferred finance charges | Q2_2026 | DEBT_ADJUSTMENT | -6 | null | null | null | NOT_STATED | NOT_STATED | USD | Not applicable | Not applicable | NOT_APPLICABLE | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p.9 [C10] |

#### T4.19 — Model Reconciliation Register

<!-- table-id: cp1.model_reconciliation_register -->

| check_id | period_id | check_type | reported_value | calculated_value | difference | tolerance | status | explanation | source_refs |
|---|---|---|---:|---:|---:|---|---|---|---|
| SEGMENT_REVENUE | Q2_2026 | SEGMENT_REVENUE_TO_REPORTED_REVENUE | 2993 | null | null | null | WARN | Source segment values are present; governed reconciliation was not executed. | 10-Q pp.2, 15 [C1, C14] |
| EBITDA_BRIDGE | Q2_2026 | EBITDA_BRIDGE | 920 | null | null | null | WARN | Issuer-reported endpoint retained; no script reconciliation output. | 10-Q p.16 [C4] |
| ADJUSTED_EBITDA_BRIDGE | Q2_2026 | ADJUSTED_EBITDA_BRIDGE | 920 | null | null | null | WARN | Addbacks retained at source granularity; bridge arithmetic not validated. | 10-Q p.16 [C4] |
| CFO_IDENTITY | H1_2026 | CFO_IDENTITY | 675 | null | null | null | WARN | Direct CFO retained; statement identity not calculated. | 10-Q p.4 [C5] |
| DEBT_TOTAL | Q2_2026 | DEBT_TOTAL | 11699 | null | null | null | WARN | Carrying-value balance-sheet total retained; facility aggregation and adjustment not reconciled. | 10-Q pp.2, 9 [C9, C10, C22, C24] |
| NET_CASH_CHANGE | H1_2026 | NET_CASH_TO_CASH_MOVEMENT | 93 | null | null | null | WARN | Reported change in cash, cash equivalents and restricted cash retained; reconciliation not calculated. | 10-Q p.4 [C5] |
| FY_QUARTER_SUM | FY2025 | REPORTED_FY_TO_QUARTERLY_SUM | 11486 | null | null | null | WARN | Four-quarter source set not delivered; no forced reconciliation. | 10-K p.19 [C18] |

<!-- table-id: cp1.downstream_readiness -->

| downstream_module | status | missing_metric_ids | conflict_refs | explanation |
|---|---|---|---|---|
| CP-MODEL | blocked | total_debt, adjusted_ebitda, cfo_ncfo, capex_and_intangible_investment | CF-1, CF-2, CF-3 | Fewer than four discrete quarters, mandatory reconciliation checks are WARN, and historical facility carrying-value schedules are not complete. G-1, G-2, G-6, G-9, G-10 remain open. |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| Q2 and H1 reported consolidated revenue | [C1] | CZR_Q2_2026_10Q.txt | 2 |
| Operating income and pretax income | [C2] | CZR_Q2_2026_10Q.txt | 3 |
| Net interest expense | [C3] | CZR_Q2_2026_10Q.txt | 3 |
| Adjusted EBITDA and issuer reconciliation | [C4] | CZR_Q2_2026_10Q.txt | 16 |
| H1 CFO and reported cash movement | [C5] | CZR_Q2_2026_10Q.txt | 4 |
| Capital expenditures | [C6] | CZR_Q2_2026_10Q.txt | 4 |
| Cash interest and cash taxes | [C7] | CZR_Q2_2026_10Q.txt | 5 |
| Cash and equivalents | [C8] | CZR_Q2_2026_10Q.txt | 2 |
| Debt-note facility values and aggregate basis | [C9] | CZR_Q2_2026_10Q.txt | 9 |
| Long-term debt carrying value and financing-cost treatment | [C10, C24] | CZR_Q2_2026_10Q.txt | 2, 9 |
| CEI revolver commitment capacity | [C11] | CZR_Q2_2026_10Q.txt | 22 |
| Customer contract liabilities | [C12] | CZR_Q2_2026_10Q.txt | 11 |
| Issuer-reported Adjusted EBITDA margins | [C13] | CZR_Q2_2026_10Q.txt | 18 |
| Segment revenue reporting | [C14] | CZR_Q2_2026_10Q.txt | 15 |
| Las Vegas operating weakness | [C15] | CZR_Q2_2026_10Q.txt | 20 |
| Regional growth and stated drivers | [C16] | CZR_Q2_2026_10Q.txt | 20 |
| Subsequent Alberta launch | [C17] | CZR_Q2_2026_10Q.txt | 17 |
| FY2025/FY2024 results and EBITDA | [C18] | CZR_FY2025_10K.txt | 19 |
| FY cash-flow baseline | [C19] | CZR_FY2025_10K.txt | 31 |
| FY debt-note comparison | [C20] | CZR_FY2025_10K.txt | 40 |
| FY audited basis | [C21] | CZR_FY2025_10K.txt | 28 |
| Balance-sheet current portion of debt | [C22] | CZR_Q2_2026_10Q.txt | 2 |
| Consolidated entity perimeter | [C23] | CZR_Q2_2026_10Q.txt | 5 |
| Balance-sheet long-term debt | [C24] | CZR_Q2_2026_10Q.txt | 2 |
| VICI and GLPI lease payments | [C25] | CZR_Q2_2026_10Q.txt | 22 |
| Reported covenant compliance | [C26] | CZR_Q2_2026_10Q.txt | 23 |
| Caesars Windsor segment transfer | [C27] | CZR_Q2_2026_10Q.txt | 17 |
| Remaining-2026 debt service | [C28] | CZR_Q2_2026_10Q.txt | 22 |
| May 27, 2026 merger agreement reference | [C29] | CZR_Q2_2026_10Q.txt | 5 |

## Source Registry

T4.1 is the complete source register for this CP-1 run. The accepted CP-0 handoff identifies the 10-Q and 10-K text extractions as usable with visual-content limitations and identifies the release as corroborative. CP-1 uses only the three evidence source IDs listed in T4.1; no external retrieval or independent verification is asserted. Source locators and evidence quality are retained in T4.1 and the register citations.

## Gaps & Conflicts

T4.11 preserves the debt-basis, Adjusted EBITDA-definition, segment-perimeter, and interest-versus-cash-payment distinctions. T4.12 records the material evidence and computation gaps and their downstream impact. T4.14–T4.19 contain null value-bearing cells as specified below; reference nulls in `component_period_ids`, `conflict_refs`, and `limitation_refs` indicate no applicable reference and are not gaps.

- T4.8 rows 1–4, `Derived Value`: null — script-owned LTM construction was not executed; see G-1.
- T4.9 rows Debt / EBITDA, Net debt / EBITDA, Senior secured debt / EBITDA, Cash interest coverage, FCF and FCF conversion, and Liquidity / debt: unavailable numerical fields — see G-1, G-2 and G-3; ratios are not inferred.
- T4.14: no value-bearing nulls. `fiscal_quarter` for FY/YTD and direct-period `component_period_ids` are reference nulls.
- T4.15: no value-bearing nulls. Reference nulls in conflict and limitation fields mean none applies.
- T4.16: no null values. Revenue schedule includes all reported operating segments and Corporate and Other for each emitted period.
- T4.17: no null values. Source-displayed dash in the H1 2026 tax reconciliation is represented as zero only for that explicit source row.
- T4.18 `CEI_TLA`, `CEI_TLB`, `CEI_TLB1`: `commitment` null — no separate commitment value for these term loans in the supplied schedule; see G-9.
- T4.18 `CEI_SEC2030`, `CEI_SEC2032`, `CEI_UNSEC2029`, `CEI_UNSEC2032`, `SID_BONDS`, `OTHER_DEBT`: `drawn_amount` and `commitment` null — source provides face and book values, not those separate facility fields; see G-9.
- T4.18 `RCF_COST_ADJ`: `principal`, `drawn_amount`, and `commitment` null — adjustment row is a carrying-value financing-cost adjustment, not a funded facility; see G-9.
- T4.19 all seven rows: `calculated_value`, `difference`, and `tolerance` null — governed reconciliations were not executed; see G-10. Status remains WARN, not PASS.

## QA Validation

| Severity | Check | Status | Finding / resolution |
|---|---|---|---|
| MATERIAL | Period and KPI construction | Open | Script-owned derived periods and KPI calculations were not executed; affected cells are null and recorded in G-1 through G-3. |
| MATERIAL | Model reconciliation and debt schedule | Open | T4.19 checks are WARN with null calculated values; historical quarterly facility schedule is incomplete. CP-MODEL readiness is blocked. |
| MINOR | Source and perimeter traceability | Reviewed | Source IDs, period coverage, carrying-value basis, segment transition, customer float, and subsequent event are recorded with evidence locators. |
| MINOR | Register structure and null handling | Reviewed | Required T4.1–T4.6 and T4.8–T4.19 registers are present; T4.7 is retired; tagged stable tables appear once. Value-bearing nulls are listed above. |
| MINOR | Self-review and host validation | Self-review complete; host validation pending | Identity, copied front matter, filename derivation, six H2 headings/order, required register columns, markers, and interface-table placement were reviewed in this draft. No vendor validator, confidence script, calculation script, or host completeness output is claimed. Host validation follows this answer. |

**Run status:** Restricted. **Confidence:** 59 / Low. **Host validation:** follows this answer; no host validator result is asserted.