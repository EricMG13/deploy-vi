---
module_id: "CP-1D"
module_name: "EarningsQuality"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1D-507255917b932a16"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-05-CP-1D"
credit_os_invocation_sha256: "b9d30b0f057de22b93df39974eb2299b47b2d98646ef2656d61af20ab76a7b4e"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
  - module_id: "CP-1B"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "339805d18ef63ec93786562d12f97a9813c148d2b8eadbc202bc3ffe209078a6"
confidence_score: 51
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, NO_POST_Q2_2026_FINANCIALS, QUALITY_ADJUSTED_EBITDA_UNRESOLVED, CURRENT_OPERATING_LEASE_LIABILITY_NOT_DISCLOSED]
validation_warnings: [TRANSACTION_COST_ADJUSTMENT_NOT_DISAGGREGATED, CP1_H1_TAX_BRIDGE_DASH_ZERO_CONFLICT, CP_MODEL_LESS_THAN_FOUR_COMPLETE_QUARTERS]
downstream_consumers: [CP-2, CP-2G, CP-4A]
---

## Audit Summary

**Canonical filename:** `CZR_CP-1D_20261002.md`. **Status:** Restricted; confidence 51/100, Low; committee status Requires More Work. The accepted CP-1 bridge is carried forward without re-extraction; CP-1B confirms most entries but flags the H1 tax bridge, where CP-1 stored zero and the filing displays a dash. [C6, C9] FY2025 impairments and transaction costs recur in prior periods, and stock compensation is present annually and in both 2026 periods; those exclusions are not accepted as clean one-offs. [C2, C3, C4, C7, C8] Transaction costs remain unresolved because the issuer reports a net, mixed category without a period-level component breakdown. Consequently, supported quality-adjusted EBITDA and its leverage ratio cannot be finalized. Operating cash flow converts only about 36% of LTM Adjusted EBITDA; recognized financing obligations materially increase debt-like claims. [C14, C15, C17]

## Analysis

### Earnings quality read-through

The reported Adjusted EBITDA bridge is issuer-defined, not a stand-alone proof that every excluded cost is non-recurring. [C5] The clearest recurring exclusions are stock-based compensation and impairment charges: the annual filing reports these in FY2023–FY2025, and current-period transaction-and-other costs also appear in both Q2 and H1 comparisons. [C2, C3, C4, C7, C8] The recurring nature of impairments and stock compensation makes their removal from earnings a material quality issue; the grouped transaction-cost amount remains unresolved because it includes different gains, losses and costs. The cash test is weak: FY2025 CFO was $1,302m against $3,624m Adjusted EBITDA; H1 2026 was $675m against $1,807m. [C1, C6, C14, C15] Recognized financing obligations also materially lift adjusted leverage. [C17]

#### Earnings quality summary

| Measure | FY2025 | LTM to June 30, 2026 | Creditor implication |
|---|---:|---:|---|
| Adjusted EBITDA conversion to CFO | 35.9% | 36.1% | Cash realization trails earnings; capex, interest and rent further reduce cash available. [C14, C15] |
| Recurring impairment and stock-compensation exclusions | $277m | — | Their recurrence challenges treating them as exceptional earnings exclusions. [C2, C3, C4] |
| Transaction-and-other adjustment | $72m | — | Recurs as a net category, but component split is not supplied; quality EBITDA remains unresolved. [C3, C7, C13] |
| Reported debt / issuer Adjusted EBITDA | — | 3.26x | CP-1 carrying debt divided by CP-1 LTM Adjusted EBITDA. [C16] |
| Adjusted debt / issuer Adjusted EBITDA | — | at least 6.92x | Adds disclosed financing obligations; excludes unquantified June operating-lease liability. [C16, C17] |

**Add-back achievability and recurrence.** No cost-out, synergy or run-rate savings add-back is identified in the inherited bridge. The issuer bridge instead removes standard tax, interest and depreciation items and separately excludes impairment, transaction/other costs and stock-based compensation. [C5] No action-based synergy realization is claimed or accepted. The explicit recurrence evidence supports rejecting impairment and stock compensation as non-recurring exclusions. Transaction-and-other costs recur, but the net line mixes unlike items and prior sale gains; absent a component bridge, its full current-period amount is unresolved rather than silently accepted or assigned an arbitrary haircut. [C2, C3, C4, C7, C8, C13]

**Cash conversion.** FY2025 CFO of $1,302m divided by Adjusted EBITDA of $3,624m is 35.9%; H1 2026 CFO of $675m divided by Adjusted EBITDA of $1,807m is 37.4%. The LTM calculation is $1,297m CFO divided by $3,592m Adjusted EBITDA, or 36.1%. [C1, C6, C14, C15] The $2,322m FY2025 and $1,132m H1 2026 differences between Adjusted EBITDA and CFO are not attributed to a single cause by the supplied filing. CFO reflects cash taxes, working-capital movements and other cash-flow adjustments; capex, cash interest, debt repayment and financing-lease rent are additional cash uses. The 10-K and 10-Q disclose debt and rent-related cash interest separately. [C14, C15, C16] This weak conversion reduces FCF durability and debt-service flexibility even before considering lease payments.

**Leverage sensitivity.** Using CP-1’s June 30 carrying debt of $11,699m and its LTM-to-June-2026 denominator, reported-debt leverage is 3.26x on issuer Adjusted EBITDA and 3.59x on CP-1 calculated GAAP EBITDA. [C16] The known adjusted-debt floor is $24,856m after adding $13,157m long-term financing obligations, producing at least 6.92x on issuer Adjusted EBITDA; the June 2026 operating-lease liability is not separately disclosed and is not replaced by the stale FY2025 figure. [C17] The principal leverage transmission is that lease/financing claims compete with debt service for cash, limiting refinancing and deleveraging capacity.

**Strongest counterargument and trigger.** The issuer’s reconciliations transparently identify the bridge categories, impairment is non-cash, and the company reports FY2025 and interim cash generation. [C5, C14, C15] That evidence would strengthen the earnings view if detailed support showed transaction costs were genuinely non-recurring, impairments were not indicative of continuing property deterioration, and cash conversion improved after capex, interest and rent. Until then, monitoring should focus on recurring impairment/transaction charges, stock compensation, CFO-to-EBITDA conversion, revolver usage and updated financing obligations. Downside sequence: lower visitation or hold reduces operating contribution; lower EBITDA weakens CFO while rent, cash interest and capex remain; cash depletion then increases revolver reliance and refinancing pressure. The measurable trigger is repeated CFO conversion below the disclosed H1/FY level alongside rising debt or weaker segment EBITDA; the supplied pack does not support a numerical stress forecast.

### Adjusted debt read-through

The CP-1 canonical debt figure excludes the separately reported long-term financing-obligation line. At June 30, 2026, balance-sheet carrying debt is $11,699m and long-term financing obligations are $13,157m. [C17, C18, C19] For this analytical restatement, the financing-obligation line is debt-like and added once. The resulting $24,856m is a minimum adjusted-debt figure because a current June operating-lease liability is not separately disclosed. Under ASC 842, the FY2025 operating-lease liability was $742m; it is included only in the FY2025 bridge, not carried forward to June. [C20] The FY2025 VICI/GLPI financing obligation is already recorded in the financing-obligation line and is not added a second time. [C21]

Finance leases are separately disclosed at $147m liability at FY2025, but the supplied statements do not reconcile whether they are included in the balance-sheet financing-obligation total; therefore no incremental amount is added. [C22] No current agency treatment is supplied, so no divergence from rating-agency conventions is asserted. These are analytical, not reported or covenant debt figures.

### Analytical appendix — complete canonical registers

#### T1D.1 — Add-Back Register

| Add-Back ID | Description | Amount | Period | Category | Source / Locator | Management Rationale | Evidence ID |
|---|---|---:|---|---|---|---|---|
| FY25-NCI | Net income attributable to noncontrolling interests | 65 | FY2025 | Other | CP-1 bridge; 10-K p. 23 | Standard issuer reconciliation item; no separate one-off rationale stated. | [C1] |
| FY25-TAX | Benefit for income taxes | -11 | FY2025 | Other | CP-1 bridge; 10-K p. 23 | Standard issuer reconciliation item. | [C1] |
| FY25-OTHER | Other income | -2 | FY2025 | Other | CP-1 bridge; 10-K p. 23 | Standard issuer reconciliation item. | [C1] |
| FY25-EXT | Loss on extinguishment of debt | 4 | FY2025 | One-Off Cost | CP-1 bridge; 10-K p. 23 | Excluded in issuer EBITDA bridge; no claim that future debt costs cease. | [C1] |
| FY25-INT | Interest expense, net | 2,304 | FY2025 | Other | CP-1 bridge; 10-K p. 23 | Standard EBITDA reconciliation item. | [C1] |
| FY25-IMP | Impairment charges | 182 | FY2025 | One-Off Cost | CP-1 bridge; 10-K p. 23 | Excluded by issuer; no evidence that impairment risk has ended. | [C2] |
| FY25-DA | Depreciation and amortization | 1,417 | FY2025 | Accounting Normalization | CP-1 bridge; 10-K p. 23 | Standard EBITDA calculation item. | [C1] |
| FY25-TRANS | Transaction costs and other, net | 72 | FY2025 | One-Off Cost | CP-1 bridge; 10-K p. 23 | Issuer excludes a grouped category; components not separately quantified. | [C3, C13] |
| FY25-SBC | Stock-based compensation expense | 95 | FY2025 | Accounting Normalization | CP-1 bridge; 10-K p. 23 | Issuer excludes compensation expense; no evidence it has ceased. | [C4] |
| H1-26-NCI | Net income attributable to noncontrolling interests | 36 | H1 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard issuer reconciliation item. | [C9] |
| H1-26-TAX | Income-tax bridge item; CP-1 stores zero while source displays a dash | 0 in CP-1; source is dash | H1 2026 | Other | CP-1 bridge; 10-Q p. 16; CP-1B flags mismatch | Source value is unresolved; do not treat dash as numeric zero. | [C10] |
| H1-26-OTHER | Other income | -5 | H1 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard issuer reconciliation item. | [C11] |
| H1-26-INT | Interest expense, net | 1,142 | H1 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard EBITDA reconciliation item. | [C12] |
| H1-26-DA | Depreciation and amortization | 702 | H1 2026 | Accounting Normalization | CP-1 bridge; 10-Q p. 16 | Standard EBITDA calculation item. | [C13] |
| H1-26-TRANS | Transaction costs and other, net | 45 | H1 2026 | One-Off Cost | CP-1 bridge; 10-Q p. 16 | Grouped issuer exclusion; recurring category, components not split. | [C7, C13] |
| H1-26-SBC | Stock-based compensation expense | 47 | H1 2026 | Accounting Normalization | CP-1 bridge; 10-Q p. 16 | Recurring compensation exclusion. | [C8] |
| Q2-26-NCI | Net income attributable to noncontrolling interests | 21 | Q2 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard issuer reconciliation item. | [C9] |
| Q2-26-TAX | Benefit for income taxes | -12 | Q2 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard issuer reconciliation item. | [C10] |
| Q2-26-OTHER | Other income | -7 | Q2 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard issuer reconciliation item. | [C11] |
| Q2-26-INT | Interest expense, net | 573 | Q2 2026 | Other | CP-1 bridge; 10-Q p. 16 | Standard EBITDA reconciliation item. | [C12] |
| Q2-26-DA | Depreciation and amortization | 355 | Q2 2026 | Accounting Normalization | CP-1 bridge; 10-Q p. 16 | Standard EBITDA calculation item. | [C13] |
| Q2-26-TRANS | Transaction costs and other, net | 29 | Q2 2026 | One-Off Cost | CP-1 bridge; 10-Q p. 16 | Grouped issuer exclusion; components not split. | [C7, C13] |
| Q2-26-SBC | Stock-based compensation expense | 23 | Q2 2026 | Accounting Normalization | CP-1 bridge; 10-Q p. 16 | Recurring compensation exclusion. | [C8] |

#### T1D.2 — Achievability Assessment

| Add-Back ID | Achievability Basis | Actions Taken To Date | Run-Rate Claimed | Realized To Date | Time To Realize | Evidence Quality | Countervailing Evidence | Assessment | Evidence ID |
|---|---|---|---|---|---|---|---|---|---|
| FY25-NCI | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Not a cash-cost elimination. | Supported | [C1, C5] |
| FY25-TAX | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Source-reported tax effect is negative. | Supported | [C1, C5] |
| FY25-OTHER | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Other income is not recurring operating savings. | Supported | [C1, C5] |
| FY25-EXT | Exclusion of debt extinguishment expense. | No future cost-out action evidenced. | None stated. | No savings realization disclosed. | Not applicable. | Directly reported; recurring historical pattern. | Loss-on-extinguishment is reported in 2023, 2024 and 2025. | Challenged | [C1] |
| FY25-INT | Standard EBITDA reconciliation item. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Cash debt and rent interest remain material cash claims. | Supported | [C1, C16] |
| FY25-IMP | Exclusion of impairment expense. | No evidence that affected assets or competitive conditions recovered. | None stated. | No cash savings realization disclosed. | Not applicable. | Directly reported; recurring in three annual periods. | Impairments were $182m, $302m and $95m in FY2025, FY2024 and FY2023. | Rejected | [C2] |
| FY25-DA | Standard EBITDA calculation item. | Not a management cost-out action. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Depreciation does not remove capital-maintenance needs. | Supported | [C1] |
| FY25-TRANS | Grouped transaction-and-other exclusion. | No component-level action schedule supplied. | None stated. | No separable realization disclosed. | Not calculable from supplied breakdown. | Directly reported total; component detail insufficient. | Category recurs and includes gains, losses, legal reserves, transaction, exit and pre-opening items. | Insufficient Information | [C3, C13] |
| FY25-SBC | Exclusion of compensation expense. | No evidence of eliminated compensation cost. | None stated. | No cost reduction evidenced. | Not applicable. | Directly reported; recurring annually. | SBC was $104m, $94m and $95m in FY2023–FY2025. | Rejected | [C4] |
| H1-26-NCI | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Not a cash-cost elimination. | Supported | [C9, C5] |
| H1-26-TAX | CP-1 source-to-bridge conflict. | No action established. | None stated. | Unresolved. | Not calculable. | CP-1B identifies source dash versus zero. | Source displays dash, not numeric zero. | Insufficient Information | [C10] |
| H1-26-OTHER | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Not an operating cost-out. | Supported | [C11, C5] |
| H1-26-INT | Standard EBITDA reconciliation item. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Debt and rent interest remain cash requirements. | Supported | [C12, C16] |
| H1-26-DA | Standard EBITDA calculation item. | Not a management cost-out action. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Does not evidence lower replacement or maintenance capex. | Supported | [C13] |
| H1-26-TRANS | Grouped transaction-and-other exclusion. | No component-level action schedule supplied. | None stated. | No separable realization disclosed. | Not calculable from supplied breakdown. | Directly reported total; component detail insufficient. | Q2 and H1 amounts recur in prior comparable periods. | Insufficient Information | [C7, C13] |
| H1-26-SBC | Exclusion of compensation expense. | No evidence of eliminated compensation cost. | None stated. | No cost reduction evidenced. | Not applicable. | Directly reported; appears in Q2 and H1 and annual periods. | Recurring compensation expense is not a demonstrated cost-out. | Rejected | [C4, C8] |
| Q2-26-NCI | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Not a cash-cost elimination. | Supported | [C9, C5] |
| Q2-26-TAX | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Signed tax adjustment is not a cost-out. | Supported | [C10, C5] |
| Q2-26-OTHER | Reconciliation item, not savings initiative. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Other income is not operating savings. | Supported | [C11, C5] |
| Q2-26-INT | Standard EBITDA reconciliation item. | No savings action claimed. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Debt and rent interest remain cash claims. | Supported | [C12, C16] |
| Q2-26-DA | Standard EBITDA calculation item. | Not a management cost-out action. | None stated. | Not applicable to savings. | Not applicable. | Directly reported. | Depreciation does not remove asset replacement needs. | Supported | [C13] |
| Q2-26-TRANS | Grouped transaction-and-other exclusion. | No component-level action schedule supplied. | None stated. | No separable realization disclosed. | Not calculable from supplied breakdown. | Directly reported total; component detail insufficient. | Same category occurs in FY2023–FY2025 and Q2/H1 comparisons. | Insufficient Information | [C3, C7, C13] |
| Q2-26-SBC | Exclusion of compensation expense. | No evidence of eliminated compensation cost. | None stated. | No cost reduction evidenced. | Not applicable. | Directly reported; recurring. | SBC is present in FY2023–FY2025 and Q2/H1 2026. | Rejected | [C4, C8] |

#### T1D.3 — Recurrence Test

| Add-Back ID | Claimed Non-Recurring | Prior Occurrences (periods) | Recurrence Pattern | Verdict | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|
| FY25-NCI | No; standard bridge item. | FY2023–FY2024 and H1/Q2 2025–2026. | Repeated consolidation reconciliation. | Recurring | Recurring minority earnings are not exceptional savings. | Do not treat as a one-off benefit. | [C1, C9] |
| FY25-TAX | No; standard bridge item. | FY2023–FY2024 and H1/Q2 2025–2026. | Tax reconciliation repeats. | Recurring | Tax effects do not establish operating cost removal. | Retain only as EBITDA-definition reconciliation. | [C1, C10] |
| FY25-OTHER | No; standard bridge item. | FY2023–FY2024 and H1/Q2 2025–2026. | Other income/loss adjustment repeats. | Recurring | Recurring non-operating items can vary by period. | No exceptional earnings conclusion. | [C1, C11] |
| FY25-EXT | No specific one-off claim evidenced. | FY2023 $200m; FY2024 $89m; FY2025 $4m. | Debt extinguishment expense appears in three consecutive years. | Recurring | Repeated refinancing/repayment costs may recur as maturities are managed. | Do not assume future financing costs are eliminated. | [C1] |
| FY25-INT | No; standard EBITDA component. | FY2023–FY2025 and H1/Q2 2025–2026. | Ongoing debt-service cost. | Recurring | Cash interest remains a fixed claim. | EBITDA is not cash available for debt service. | [C1, C12, C16] |
| FY25-IMP | Issuer excludes as an adjustment; no cessation claim established. | FY2023 $95m; FY2024 $302m; FY2025 $182m. | Impairment recurs in three annual periods. | Recurring | Repeat impairments can signal continuing competition or asset deterioration. | Reject non-recurring treatment in quality view. | [C2] |
| FY25-DA | No; standard EBITDA component. | FY2023–FY2025 and H1/Q2 2025–2026. | Recurring depreciation/amortization. | Recurring | Excluding D&A can obscure asset replacement requirements. | Consider capex separately in cash analysis. | [C1, C13] |
| FY25-TRANS | No specific one-off claim evidenced for the whole category. | FY2023 $6m; FY2024 $(285)m net; FY2025 $72m. | Net transaction-and-other line appears each year with mixed signs. | Recurring | Aggregate net amounts mask recurring costs and gains. | Do not accept the full current adjustment without a component split. | [C3, C13] |
| FY25-SBC | No; recurring compensation item. | FY2023 $104m; FY2024 $94m; FY2025 $95m. | Annual recurrence. | Recurring | Excluding continuing compensation overstates durable earnings. | Reject as non-recurring exclusion. | [C4] |
| H1-26-NCI | No; standard bridge item. | FY2023–FY2025 and H1/Q2 2025–2026. | Repeats across periods. | Recurring | Not an exceptional cost-out. | No one-off normalization. | [C1, C9] |
| H1-26-TAX | Not determinable because source displays dash. | FY2025 and Q2 2026 differ; H1 source row is dash. | Source-to-bridge representation conflict. | Insufficient Information | Converting dash to zero could fabricate an adjustment. | Preserve unresolved value and do not use as a quality adjustment. | [C10] |
| H1-26-OTHER | No; standard bridge item. | FY2023–FY2025 and Q2/H1 2025–2026. | Repeats as other income/loss. | Recurring | Item is not a demonstrated cost-out. | Retain as definition bridge only. | [C1, C11] |
| H1-26-INT | No; standard EBITDA component. | FY2023–FY2025 and H1/Q2 2025–2026. | Ongoing interest cost. | Recurring | Interest consumes cash after EBITDA. | Monitor cash interest and debt balance. | [C1, C12] |
| H1-26-DA | No; standard EBITDA component. | FY2023–FY2025 and H1/Q2 2025–2026. | Recurring. | Recurring | Excluding D&A does not eliminate capital needs. | Assess cash conversion after capex. | [C1, C13] |
| H1-26-TRANS | No specific one-off claim evidenced for whole category. | H1 2025 $54m; H1 2026 $45m; FY2023–FY2025 also reported. | Comparable-period recurrence and annual recurrence. | Recurring | Recurring aggregate costs can be excluded repeatedly. | Challenge the adjustment; component split remains needed. | [C3, C7] |
| H1-26-SBC | No; recurring compensation item. | FY2023–FY2025; H1 2025 $50m and H1 2026 $47m. | Repeats annually and in comparable half-years. | Recurring | Ongoing compensation is part of economic cost base. | Reject non-recurring treatment. | [C4, C8] |
| Q2-26-NCI | No; standard bridge item. | FY2023–FY2025 and Q2/H1 2025–2026. | Repeats across periods. | Recurring | Not a one-off cost-out. | No one-off normalization. | [C1, C9] |
| Q2-26-TAX | No; standard bridge item. | FY2023–FY2025 and Q2/H1 2025–2026. | Tax bridge recurs. | Recurring | Tax adjustment is not evidence of operating savings. | Retain only as definition bridge. | [C1, C10] |
| Q2-26-OTHER | No; standard bridge item. | FY2023–FY2025 and Q2/H1 2025–2026. | Repeats as other income/loss. | Recurring | Variable non-operating items remain period dependent. | No exceptional earnings conclusion. | [C1, C11] |
| Q2-26-INT | No; standard EBITDA component. | FY2023–FY2025 and Q2/H1 2025–2026. | Ongoing interest cost. | Recurring | Cash interest persists after EBITDA. | No debt-service relief implied by add-back. | [C1, C12] |
| Q2-26-DA | No; standard EBITDA component. | FY2023–FY2025 and Q2/H1 2025–2026. | Recurring depreciation/amortization. | Recurring | Exclusion does not remove reinvestment needs. | Review capex and asset condition separately. | [C1, C13] |
| Q2-26-TRANS | No specific one-off claim evidenced for whole category. | Q2 2025 $41m; Q2 2026 $29m; FY2023–FY2025 also reported. | Comparable-quarter and annual recurrence. | Recurring | Recurring aggregate costs may persist. | Do not accept as fully non-recurring without detail. | [C3, C7] |
| Q2-26-SBC | No; recurring compensation item. | FY2023–FY2025; Q2 2025 $24m and Q2 2026 $23m. | Annual and comparable-quarter recurrence. | Recurring | Recurring compensation reduces economic earnings. | Reject non-recurring treatment. | [C4, C8] |

#### T1D.4 — Quality-Adjusted EBITDA Bridge

| Step | Amount | Basis | Supported / Challenged / Rejected | Cumulative EBITDA | Evidence ID |
|---|---:|---|---|---:|---|
| FY2025 issuer-reported Adjusted EBITDA | 3,624 | CP-1 bridge, inherited without re-extraction | Supported as reported measure only | 3,624 | [C1] |
| FY2025 recurring impairment exclusion | (182) | Repeated annual charges; remove the issuer add-back from quality view | Rejected | 3,442 | [C2] |
| FY2025 recurring stock-compensation exclusion | (95) | Recurs annually; retain as ongoing economic cost | Rejected | 3,347 | [C4] |
| FY2025 transaction-and-other adjustment | — | $72m source amount remains unresolved; grouped net line contains unlike items | Insufficient Information | — | [C3, C13] |
| FY2025 quality-adjusted EBITDA | — | Final figure depends on unresolved transaction-and-other components | Insufficient Information | — | [C3, C13] |
| H1 2026 issuer-reported Adjusted EBITDA | 1,807 | CP-1 bridge, inherited without re-extraction | Supported as reported measure only | 1,807 | [C6] |
| H1 2026 recurring stock-compensation exclusion | (47) | Comparable-period and annual recurrence; retain as ongoing cost | Rejected | 1,760 | [C4, C8] |
| H1 2026 transaction-and-other adjustment | — | $45m source amount is recurring as a category but not component-disaggregated | Insufficient Information | — | [C7, C13] |
| H1 2026 source-dash tax bridge | — | CP-1 stores zero; source displays dash; unresolved representation | Insufficient Information | — | [C10] |
| H1 2026 quality-adjusted EBITDA | — | Final figure depends on unresolved transaction adjustment and bridge conflict | Insufficient Information | — | [C7, C10] |
| Q2 2026 issuer-reported Adjusted EBITDA | 920 | CP-1 bridge, inherited without re-extraction | Supported as reported measure only | 920 | [C6] |
| Q2 2026 recurring stock-compensation exclusion | (23) | Comparable-quarter and annual recurrence; retain as ongoing cost | Rejected | 897 | [C4, C8] |
| Q2 2026 transaction-and-other adjustment | — | $29m source amount recurs by category; composition not separated | Insufficient Information | — | [C7, C13] |
| Q2 2026 quality-adjusted EBITDA | — | Final figure depends on unresolved transaction adjustment | Insufficient Information | — | [C7, C13] |

#### T1D.5 — Cash Conversion Test

| Period | Adjusted EBITDA | CFO | Conversion % | Gap | Explanation | Risk Mechanic | Credit Implication | Evidence ID |
|---|---:|---:|---:|---:|---|---|---|---|
| FY2025 | 3,624 | 1,302 | 35.9% | 2,322 | CFO reconciles from net income through noncash, working-capital and other cash-flow items; filing does not attribute the full EBITDA/CFO gap to one cause. Capex, interest and rent are further cash uses. | Earnings do not convert fully to operating cash; subsequent investment and fixed claims further consume cash. | Lower FCF durability and less cash available for debt service/deleveraging. | [C1, C14, C16] |
| H1 2026 | 1,807 | 675 | 37.4% | 1,132 | Interim CFO includes working-capital and noncash movements; discrete Q2 CFO is not reported. H1 cash interest and capex are separate uses. | Cash generation is below Adjusted EBITDA before financing and lease requirements. | Constrains debt-service cushion; do not infer Q2 cash conversion. | [C6, C15, C16] |
| LTM to June 30, 2026 | 3,592 | 1,297 | 36.1% | 2,295 | Calculated from FY2025 plus H1 2026 less H1 2025; source does not provide an LTM cash-flow statement. | LTM conversion remains low relative to reported earnings, before capex, cash interest and rent. | Supports caution in treating issuer Adjusted EBITDA as durable debt-paydown capacity. | [C1, C6, C14, C15] |

#### T1D.6 — Leverage Sensitivity

| Metric | On Reported EBITDA | On Adjusted EBITDA | On Quality-Adjusted EBITDA | Delta (turns) | Credit Implication | Evidence ID |
|---|---:|---:|---:|---:|---|---|
| June 30 carrying debt / LTM earnings to June 30, 2026 | 3.59x | 3.26x | — | 0.34x reported-to-adjusted; quality delta not calculable | Issuer Adjusted EBITDA lowers apparent leverage relative to CP-1 calculated GAAP EBITDA. Quality-adjusted denominator remains unresolved because transaction-and-other costs are not disaggregated and the H1 bridge has a dash/zero conflict. | [C1, C6, C16] |
| June 30 adjusted-debt floor / LTM issuer Adjusted EBITDA | — | at least 6.92x | — | Adjusted debt adds 3.66x versus reported-debt basis | Adds disclosed long-term financing obligations to CP-1 carrying debt; current operating-lease liability is not separately disclosed, so this is a floor. | [C16, C17, C18, C19] |

#### T1D.7 — Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Transaction-and-other add-back | Component-level costs, gains, legal reserves, exit costs and transaction costs underlying the FY2025 $72m, H1 $45m and Q2 $29m net adjustments. | The category recurs, but its net aggregate combines unlike items; full acceptance or rejection would overstate what evidence supports. | Quality-adjusted EBITDA and quality-based leverage remain unresolved. | Obtain a period-by-period component bridge and evidence of settled/non-recurring items. |
| Impairment and SBC add-backs | Property-level impairment drivers and evidence of any eliminated compensation cost. | Both categories recur; impairment may reflect continuing asset/competition pressure and SBC remains recurring compensation. | Exclusions are rejected in the supported bridge; future impairment and ongoing compensation remain credit-relevant. | Monitor future impairments, competitive conditions and stock-compensation amounts. |
| H1 2026 tax bridge conflict | CP-1 numerical zero versus source dash. | A dash is not a sourced numeric zero and must not be normalized silently. | H1 quality bridge remains unresolved; CP-1B flags this issue. | CP-1 owner to correct/reconcile the bridge representation. |
| Current operating-lease liability | June 30, 2026 ASC 842 operating-lease liability and reconciliation to lease schedules. | FY2025 liability cannot be carried forward as a current-period value. | June adjusted debt is a minimum; current lease-adjusted leverage may be higher. | Obtain June 2026 lease note or liability schedule. |
| Agency convention | Current rating-agency adjusted-debt and earnings treatments. | Cannot claim agreement or divergence without agency evidence. | Convention comparison remains a gap, not an assumed standard. | Obtain current agency reports or documented adjustment schedules. |

#### T1E.1 — Obligation Inventory

| Item | Category | Reported Amount | Period | Source / Locator | Disclosure Quality | Evidence ID |
|---|---|---:|---|---|---|---|
| CEI carrying debt | Reported debt | 11,699 | June 30, 2026 | 10-Q balance sheet: current portion plus long-term debt, p. 2 | Primary filing; balance-sheet basis | [C18, C19] |
| Long-term financing obligations | Failed-sale-leaseback financing obligations; debt-like | 13,157 | June 30, 2026 | 10-Q balance sheet, p. 2 | Primary filing; aggregate line, no June lessor split in supplied material | [C17] |
| VICI financing obligation | Financing lease / failed sale-leaseback obligation | 11,705 | December 31, 2025 | 10-K Note 7, p. 38 | Primary audited filing; recognized balance-sheet obligation | [C21] |
| GLPI financing obligation | Financing lease / failed sale-leaseback obligation | 1,284 | December 31, 2025 | 10-K Note 7, p. 38 | Primary audited filing; recognized balance-sheet obligation | [C21] |
| Operating lease liability | Operating leases under ASC 842 | 742 | December 31, 2025 | 10-K Note 7, p. 37 | Primary audited filing; recognized lease liability | [C20] |
| Finance-lease liability | Finance leases | 147 | December 31, 2025 | 10-K Note 7, p. 37 | Primary audited filing; balance-sheet classification overlap with financing obligations not reconciled | [C22] |
| Sports sponsorship / partnership commitments | Contractual commitments; not automatically debt | 318 | December 31, 2025 | 10-K Note 8, p. 39 | Primary audited filing; future obligations through 2040 | [C23] |
| Customer deposits and deferred revenue | Operating float / performance obligation | 545 | June 30, 2026 | 10-Q Note 7, p. 11 | Primary interim filing; no debt classification | [C24] |
| Pension obligations | Pension / post-employment | Net deficit not shown; plan-level details disclosed | FY2025 | 10-K Note 13, p. 46 | Primary audited filing; multiemployer withdrawal liability not quantified in supplied extract | — |
| Factoring / reverse factoring | Supplier finance / receivables finance | — | FY2025 / Q2 2026 | Not separately identified in delivered financial disclosure; GAP-E1 | No quantified program terms in supplied pack | — |
| Securitisation / receivables sale funding | Receivables financing | — | FY2025 / Q2 2026 | Not separately identified in delivered financial disclosure; GAP-E1 | No quantified program terms in supplied pack | — |
| Hybrid / preferred securities | Hybrid capital | — | FY2025 / Q2 2026 | No issued preferred shares shown on FY2025 balance sheet; further hybrid terms not disclosed; GAP-E1 | No amount established | — |
| Earn-outs, put liabilities and deferred acquisition consideration | Contingent / acquisition obligations | — | FY2025 / Q2 2026 | No aggregate balance established in supplied statements; Grand Bazaar deferred consideration is $10m in 2026 acquisition disclosure | Individual later-period acquisition item, not a material-debt conclusion | — |

#### T1E.2 — Debt-Like Assessment

| Item | Debt-Like? | Basis for Treatment | Adjustment Amount | Convention Applied | Countervailing Evidence | Evidence ID |
|---|---|---|---:|---|---|---|
| CEI carrying debt | Yes; base | CP-1 canonical carrying value is balance-sheet current plus long-term debt. | 11,699 | GAAP carrying-value basis; already in reported debt, no incremental adjustment | Face principal is separately disclosed and should not replace carrying amount. | [C18, C19] |
| Long-term financing obligations, June 2026 | Yes | Separately recognized balance-sheet financing obligation; economically fixed claim alongside debt. | 13,157 | Add to reported debt once for analytical adjusted debt. | The 10-Q does not split the June total by VICI, GLPI and any other financing component; retain aggregate. | [C17] |
| VICI financing obligation, FY2025 | Yes | Recognized financing obligation from failed sale-leaseback; future contractual payments support debt-like treatment. | 11,705 | Included within FY2025 long-term financing-obligation balance; do not add again. | Amount is already recognized on balance sheet. | [C21] |
| GLPI financing obligation, FY2025 | Yes | Recognized financing obligation from failed sale-leaseback. | 1,284 | Included within FY2025 long-term financing-obligation balance; do not add again. | Amount is already recognized on balance sheet. | [C21] |
| Operating lease liability, FY2025 | Yes | ASC 842 lease liability is recognized but excluded from CP-1 debt. | 742 | Add for FY2025 analytical debt; do not carry stale amount to June 2026. | No June 2026 operating-lease liability is separately supplied. | [C20] |
| Finance lease liability | Yes in principle; incremental amount unresolved | Lease financing is a fixed claim, but supplied note does not reconcile it to balance-sheet financing obligations. | — | ASC 842 / balance-sheet recognition; no incremental add to avoid double count pending reconciliation. | Liability may already be included in financing obligations or other balance-sheet debt-like lines. | [C22, C17] |
| Sponsorship commitments | Not included in adjusted debt | Future contractual purchases/services are not shown as funded debt or a recognized financing liability. | — | Keep as contractual cash commitments, outside debt numerator. | Commitments total $318m at FY2025 and $309m at June 2026, extending through 2040. | [C23] |
| Customer deposits and deferred revenue | No; operating float, not debt | Funds received for gaming and future services create performance/refund obligations, not borrowing. | — | Track separately in liquidity / working capital; no debt adjustment. | Balance rose to $545m at June 2026. | [C24] |
| Pension / multiemployer exposure | Not quantified as debt-like adjustment | No disclosed net underfunded amount or withdrawal-liability figure established for consolidated company. | — | No amount added without a supported quantum. | Some disclosed plans are funded or overfunded; multiemployer withdrawal exposure is not quantified. | — |
| Factoring / reverse factoring | Insufficient Information — no program amount or terms supplied | Such funding may be debt-like if recourse or supplier-finance obligations exist, but no program is quantified here. | — | No default multiple or assumed adjustment. | Absence of a cited disclosure does not establish zero. | — |
| Securitisation / receivables financing | Insufficient Information — no program amount or terms supplied | Funding may be debt-like depending on recourse and transfer structure. | — | No adjustment without disclosed balance and terms. | No quantified program identified in supplied extracts. | — |
| Hybrid / preferred securities | No amount established | FY2025 balance sheet reports no preferred shares issued; no hybrid debt quantum is supplied. | — | No adjustment without a reported instrument. | This does not establish that no other contingent or off-balance obligation exists. | — |
| Earn-outs / put liabilities / acquisition obligations | Insufficient Information — aggregate balance not established | Deferred or contingent consideration can be debt-like when fixed or payable; supplied source gives only a discrete $10m deferred Grand Bazaar amount. | — | Do not aggregate or extrapolate the one acquisition disclosure. | Current aggregate liability and payment timing are not established. | — |

#### T1E.3 — Adjusted Debt Bridge

| Step | Amount | Basis | Cumulative Adjusted Debt | Evidence ID |
|---|---:|---|---:|---|
| FY2025 reported carrying debt | 11,784 | CP-1 canonical basis: current portion plus long-term debt. | 11,784 | [C18, C19] |
| Add FY2025 long-term financing obligations | 13,096 | Balance-sheet financing-obligation line; debt-like and outside CP-1 debt. | 24,880 | [C17] |
| Add FY2025 operating lease liability | 742 | ASC 842 liability at year-end; separate from CP-1 debt. | 25,622 | [C20] |
| FY2025 incremental finance-lease liability | — | Not added; overlap with financing-obligation line is unreconciled. | 25,622 | [C22] |
| June 30, 2026 reported carrying debt | 11,699 | CP-1 canonical basis. | 11,699 | [C18, C19] |
| Add June 2026 long-term financing obligations | 13,157 | Reported aggregate balance-sheet obligation. | 24,856 | [C17] |
| Add June 2026 operating lease liability | — | June liability not separately supplied; no stale FY2025 amount carried forward. | 24,856 minimum known adjusted debt | [C20] |
| June 2026 incremental finance-lease liability | — | No increment pending reconciliation to reported financing obligations. | 24,856 minimum known adjusted debt | [C22, C17] |

#### T1E.4 — Leverage Restatement

| Metric | On Reported Debt | On Adjusted Debt | Delta (turns) | Risk Mechanic | Credit Implication | Evidence ID |
|---|---:|---:|---:|---|---|---|
| FY2025 debt / FY2025 issuer Adjusted EBITDA | 3.25x | 7.07x | +3.82x | Adds recognized financing obligations and FY2025 operating-lease liability to CP-1 carrying debt. | Fixed lease/financing claims materially increase leverage relative to debt-only presentation. | [C1, C17, C18, C19, C20] |
| June 30, 2026 debt / LTM issuer Adjusted EBITDA | 3.26x | At least 6.92x | At least +3.66x | Adds June financing obligations; June operating-lease liability is not separately disclosed. | Adjusted-debt floor is materially higher; current lease liability could increase it. | [C6, C17, C18, C19] |

#### T1E.5 — Convention Reconciliation

| Item | Agency / Convention | Their Treatment | This Analysis | Divergence Rationale | Evidence ID |
|---|---|---|---|---|---|
| Financing obligations | No current rating-agency adjustment schedule supplied. | Not established from provided evidence. | Add recognized financing-obligation balance to CP-1 carrying debt once. | This analysis treats the separately presented balance-sheet obligation as debt-like; no agency divergence is asserted. | [C17, C21] |
| Operating leases | ASC 842 financial statements supplied; no current agency lease adjustment supplied. | Agency treatment not established. | Add FY2025 recognized operating-lease liability; June amount remains unquantified. | Prevents treating recognized operating-lease liabilities as absent while avoiding stale-period carry-forward. | [C20] |
| Finance leases | ASC 842 note reports a finance-lease liability; no agency treatment supplied. | Agency treatment not established. | No incremental addition until balance-sheet overlap is reconciled. | Avoids possible double counting against financing obligations. | [C22, C17] |

#### T1E.6 — Adjusted-Debt Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Current operating-lease liability | June 30, 2026 operating-lease liability detail. | The FY2025 $742m liability is not a valid June 2026 substitute. | June adjusted debt and leverage are stated as a minimum known floor. | Obtain the June 2026 lease note / updated ASC 842 liability schedule. |
| Finance-lease overlap | Reconciliation of the $147m FY2025 finance-lease liability to long-term financing obligations and other liabilities. | Separate addition could double count an amount already included in financing obligations. | No incremental finance-lease amount added. | Obtain debt/lease classification reconciliation. |
| Rating-agency convention | Current agency debt, lease and pension adjustment schedules. | Cannot claim agency alignment or divergence without the applicable convention evidence. | T1E.5 records no agency treatment as established. | Obtain current rating-agency reports or adjustment schedules. |
| Factoring, reverse factoring and securitisation | Program balances, recourse, transferred receivables and supplier-finance terms. | Such arrangements could create debt-like obligations or operational funding dependence. | No amount assumed; debt build excludes unquantified programs. | Obtain current financing and supplier-finance disclosures. |
| Pensions and contingent obligations | Consolidated unfunded pension, multiemployer withdrawal liability, earn-out and put-liability balances. | Potential cash claims cannot be quantified from supplied excerpts. | No unsupported amount or leverage adjustment applied. | Obtain benefit-plan and contingent-obligation schedules. |
| Post-June information | Updated debt, cash, lease and transaction position after June 30, 2026. | Analysis date is October 2, while latest financial period is June 30. | Current adjusted leverage is not established. | Obtain subsequent financial reporting and current debt/cash schedules. |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| FY2025 Adjusted EBITDA and history | [C1] | Caesars FY2025 Form 10-K | 23 |
| Impairment recurrence FY2023–FY2025 | [C2] | Caesars FY2025 Form 10-K | 23 |
| Transaction-and-other amounts FY2023–FY2025 | [C3] | Caesars FY2025 Form 10-K | 23 |
| Stock compensation FY2023–FY2025 | [C4] | Caesars FY2025 Form 10-K | 23 |
| Issuer definition of Adjusted EBITDA | [C5] | Caesars FY2025 Form 10-K | 22 |
| Q2/H1 issuer Adjusted EBITDA | [C6] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 transaction-and-other bridge amounts | [C7] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 stock-based compensation | [C8] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 noncontrolling-interest bridge | [C9] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 income-tax bridge | [C10] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 other-income bridge | [C11] | Caesars Q2 2026 Form 10-Q | 16 |
| Q2/H1 interest and D&A bridge | [C12, C13] | Caesars Q2 2026 Form 10-Q | 16 |
| FY2025 and H1 2026 CFO | [C14, C15] | Caesars FY2025 Form 10-K; Q2 2026 Form 10-Q | 31; 4 |
| June 2026 carrying debt and financing obligations | [C17, C18, C19] | Caesars Q2 2026 Form 10-Q | 2 |
| FY2025 operating-lease liability | [C20] | Caesars FY2025 Form 10-K | 37 |
| FY2025 VICI and GLPI financing obligations | [C21] | Caesars FY2025 Form 10-K | 38 |
| Finance-lease liability | [C22] | Caesars FY2025 Form 10-K | 37 |
| Sponsorship obligations | [C23] | Caesars FY2025 Form 10-K | 39; Q2 2026 Form 10-Q p. 8 |
| Customer deposits and deferred revenue | [C24] | Caesars Q2 2026 Form 10-Q | 11 |

## Source Registry

| Source | Use | Period | Limitation |
|---|---|---|---|
| Caesars FY2025 Form 10-K | Annual EBITDA bridge, recurrence history, annual cash conversion, debt and lease disclosures. | FY2023–FY2025 | Audited but historical; operating-lease liability is year-end 2025 only. |
| Caesars Q2 2026 Form 10-Q | Interim bridge, Q2/H1 cash conversion, current balance-sheet debt and financing obligations. | Q2/H1 2026 and comparative periods | Unaudited; no discrete Q2 cash-flow statement and no post-June financial update. |
| Accepted CP-0 handoff | Source readiness, source limits and run identity. | Q2 2026 | Restricted; does not replace primary source evidence. |
| Accepted CP-1 handoff | Required inherited Adjusted EBITDA bridge and carrying-debt/earnings calculations. | Q2 2026 | Used as upstream data, not cited as source evidence; CP-1B flags the H1 tax dash/zero issue. |
| Accepted CP-1B handoff | Bridge transcription validation and identified source conflict. | Q2 2026 | Used as upstream validation context, not as primary evidence. |

## Gaps & Conflicts

The $72m FY2025, $45m H1 2026 and $29m Q2 2026 transaction-and-other adjustments are recurring as a reported category, but source detail does not isolate which costs are truly non-recurring or offset by gains. They remain unresolved rather than accepted, rejected wholesale or haircutted. [C3, C7, C13] The H1 tax bridge is another unresolved point: CP-1 records zero while the Q2 filing prints a dash. [C10] Both limitations prevent a final quality-adjusted EBITDA figure and quality-adjusted earnings leverage. Impairment and stock compensation are rejected as non-recurring exclusions because the annual and interim evidence shows recurrence. [C2, C4, C8]

For adjusted debt, June 2026 financing obligations are disclosed as an aggregate, and June operating-lease and finance-lease reconciliation detail is not supplied. The adjusted-debt leverage is therefore a minimum known amount, not a complete lease-inclusive figure. [C17, C20, C21, C22] No agency-adjustment package is present, so agency divergence remains a gap. Factoring, securitisation, pensions and contingent obligations are not quantified in the supplied excerpts; no default assumptions or amounts are applied.

## QA Validation

| Check | Result | Note |
|---|---|---|
| CP-1 bridge inherited without restatement | PASS | Each listed FY2025, H1 2026 and Q2 2026 CP-1 bridge item is carried in T1D.1. |
| Every CP-1 bridge add-back present in T1D.1 | PASS | All 23 inherited period-specific rows are present; no `NONE` row is applicable because the bridge is populated. |
| Achievability assessed on action evidence | PASS WITH LIMITATIONS | No synergy/run-rate action is accepted; standard reconcilers are separated from claimed cost-outs; unresolved transaction bucket is not silently accepted. |
| Recurrence tested against named prior periods | PASS | T1D.3 names FY2023–FY2025 and comparable H1/Q2 periods where available. |
| T1D.4 cumulative arithmetic reconciles | PASS WITH LIMITATIONS | Supported subtotals reconcile; final quality-adjusted EBITDA remains null because transaction costs and H1 bridge conflict are unresolved. |
| Leverage restated on reported, adjusted and quality-adjusted bases | PASS WITH LIMITATIONS | Reported and issuer-Adjusted EBITDA leverage calculated; quality-adjusted leverage remains null, with explicit gap. |
| Unresolved add-backs carried as gaps | PASS | Transaction and H1 tax conflict are recorded in T1D.7 and T1E.6; not treated as zero or accepted. |
| CP-1E obligation classes inventoried and treatment assessed | PASS WITH LIMITATIONS | Recognized financing obligations and lease liabilities quantified where sourced; unquantified classes remain explicit gaps. |
| Operating lease accounting and double-count control | PASS | ASC 842 identified; FY2025 operating lease added once, stale liability not carried into June, financing leases not double counted. |
| Adjusted debt bridge arithmetic | PASS | FY2025 adjusted debt totals $25,622m; June known adjusted debt floor totals $24,856m. |
| Agency-convention reconciliation | RESTRICTED | No current agency treatment supplied; divergence is not asserted. |
| Confidence score and band | RESTRICTED | 51/100, Low; material unresolved add-back, current lease and source-coverage gaps cap confidence. |
| Host automated validation | PENDING | Host validation follows this response; no script result or host finding is claimed. |