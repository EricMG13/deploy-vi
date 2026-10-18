---
module_id: "CP-4"
module_name: "LegalCovenantInterpreter"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "COVENANT_REFINANCING"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-4-9883a02434934047"
credit_os_route_node_id: "RN-FULL_CREDIT_32-COVENANT_REFINANCING-03-CP-4"
credit_os_invocation_sha256: "b0597a6b191222f0c44c9d2b225bd1334aa1d2b815472830b4d135fb05494d40"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a4ee2ea26d222a51d5c167a5868ea43f9bba131c911042fc7dcb2840af340ca2"
  - module_id: "CP-1"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a412c541834dd7643188444e637ba16543096bf4686d71c334f32b4a53e19a67"
confidence_score: 58
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, EXECUTED_INTERCREDITOR_AGREEMENT_MISSING, GOVERNING_SCHEDULES_INCOMPLETE, CAPACITY_USAGE_AND_CERTIFICATE_MISSING, MERGER_FINANCING_DOCUMENTS_MISSING, MARKET_COMPARATOR_MISSING]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED, EXACT_CAPACITY_NOT_CALCULATED, ICA_DEPENDENT_FINDINGS_LIMITED]
downstream_consumers: [CP-4C, CP-4B, CP-4A, CP-6]
---

## Audit Summary

- **Run status:** Completed with Limitations; the delivered executed credit documents and Q2 filing support provision-level interpretation, but not exact capacity, current basket usage, or a complete intercreditor/recovery-control assessment.
- **Confidence:** 58/100 — Low. Calculation: evidence quality E=75, required-field coverage C=93, partial source gate S=0.7, no independently assessed QA penalty; clamp((0.6×75 + 0.4×93)×0.7)=58. Restricted status is consistent with material evidence gaps.
- **Committee status:** Requires More Work. No formal rating, legal advice, exact capacity calculation, or unsupported market-norm conclusion is made.
- **Canonical artifact:** `CZR_CP-4_20261002.md`.
- **Upstream re-anchor:** accepted CP-0 and CP-1 artifacts match issuer CZR, run COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 and Q2 2026. CP-1 reports canonical balance-sheet carrying debt of $11,699 million, but does not supply a governing covenant EBITDA bridge or current basket tracker. The source filing separately reports covenant compliance at June 30, 2026 [C14, C15].

## Analysis

### Creditor implication
The controlling package is the conformed July 2020 Credit Agreement, amended through the delivered February 2024 incremental agreement and separate Fourth and Fifth Amendments, together with the executed 2032 Notes Indenture and supplements. The strongest documented protection is a first-lien collateral and guarantee framework with financial tests for Covenant Facilities; the principal weakness is broad ratio, grower, reclassification and investment flexibility, combined with entity and asset exclusions [C1, C2, C3, C4, C7, C12, C13]. Q2 compliance is a point-in-time statement, not headroom. The covenant EBITDA definition permits broad pro forma and adjustment mechanics, while usage and covenant EBITDA are unavailable [C5, C15]. The executed intercreditor agreement and current schedules are absent, so standstill, enforcement control and complete collateral reach remain unresolved [C24, C25].

**Decision drivers.** The agreement permits pari passu incremental debt subject to tests, broad restricted-payment and investment routes, and unrestricted-subsidiary pathways; the actual remaining capacity is not calculable. A reported 6.50x maximum leverage test and 2.00x minimum coverage test apply to relevant Covenant Facilities, but only reported compliance—not measured cushion—is available. The strongest contrary evidence is the issuer’s compliance statement and continuing protections in the contractual tests and voting provisions; it would materially improve conviction if current certificates, EBITDA bridges, basket usage and the executed intercreditor package showed low usage and effective collateral/guarantee coverage [C1, C2, C11, C15, C26].

**Downside path and monitoring.** A renewed decline in Las Vegas visitation, table-game volume or hold would first reduce property EBITDA; lower earnings and cash conversion could then narrow the maintenance tests, increase reliance on incremental borrowing and heighten refinancing risk. Q2 Las Vegas Adjusted EBITDA was $410 million versus $469 million in Q2 2025, while the filing reports lower visitation and table-games performance [C27]. Track quarterly covenant certificates and test results, ratio and basket usage, new pari or non-guarantor debt, unrestricted-subsidiary designations, asset transfers, lien/guarantee releases, amendments and merger financing/closing developments. Do not blend the July 13 Alberta launch into Q2 results [C22].

**Market and transaction limitations.** No market-norm comparator or third-party covenant review was delivered; no relative market assessment is made. The merger is a Q2-period transaction, but the complete merger agreement schedules and commitment-letter terms are not included in the delivered evidence. Treat its financing as a separate transaction overlay, not as Q2 debt or covenant capacity [C21, C28].

### Analytical appendix — complete canonical registers

#### T4.2 — Controlling Document Register

| Authority Rank | Document | Document Type | Version / Date | Status | Governing Role | Credit Relevance | Evidence ID |
|---|---|---|---|---|---|---|---|
| 1 | Credit Agreement dated July 20, 2020, conformed through Incremental Assumption Agreement No. 3 | Executed credit agreement / conformed text | February 6, 2024 conformed version; referenced schedules not all delivered | Executed; schedule completeness limited | Primary source for loan covenants and definitions | Governs leverage tests, debt/lien capacity, investments, payments, collateral and releases [C3, C8] | [C3, C8] |
| 1 | Fourth Amendment to Credit Agreement | Executed amendment | May 9, 2024 | Executed; superseded on identified pricing terms by later delivered amendment | Amends Term B terms and lender replacement mechanics | Shows a non-pro-rata consent-allocation feature; not the latest delivered pricing text [C19] | [C19] |
| 1 | Fifth Amendment to Credit Agreement | Executed amendment | November 25, 2024 | Executed; latest delivered credit amendment | Amends Term B and B-1 pricing and replacement mechanics | Primary amendment source; no later amendment is in the delivered set [C20] | [C20] |
| 1 | 6.500% Senior Secured Notes due 2032 Indenture | Executed indenture | February 6, 2024 | Executed; separate supplements delivered | Controls 2032 Notes covenants, guarantees, collateral and remedies | Establishes noteholder protections, permitted leakage and pari first-lien status [C10, C12] | [C10, C12] |
| 1 | First Supplemental Indenture to 2032 Notes | Executed supplemental indenture | March 1, 2024 | Executed | Amends specified indenture provisions and adds guarantors | Relevant to guarantee perimeter and the defeasance/liens text [C11] | [C11] |
| 1 | Second Supplemental Indenture to 2032 Notes | Executed supplemental indenture | August 23, 2024 | Executed | Adds guarantors | Expands the documented note-guarantor roster; does not establish current asset values [C11] | [C11] |
| 3 | Q2 2026 Form 10-Q | Interim filing / financial and covenant-status source | Quarter ended June 30, 2026; filed July 28, 2026 | Filed; unaudited | Current financial inputs and issuer-reported compliance | Supplies carrying-value debt, current covenant-status statement and perimeter disclosures [C14, C15] | [C14, C15] |
| 1 / 2 gap | Executed intercreditor and security-document package | Intercreditor / collateral documents | Current versions not delivered | [Insufficient Information] — only agreement-form references are present | Would govern lien sharing, enforcement and turnover | No clause-level enforcement-control finding can be made [C25] | [C25] |

#### T4.3 — Covenant Feature Register

| Topic | Provision Summary | Source / Clause | Risk Mechanic | Credit Implication | Market Norm Assessment | Evidence ID |
|---|---|---|---|---|---|---|
| Maintenance covenant architecture | Total leverage maximum of 6.50x and fixed-charge coverage minimum of 2.00x for Covenant Facilities; following repayment of Term A, revolver tests depend on the stated Testing Condition. | Credit Agreement §6.11(a)–(b) | A tested breach may lead to Covenant Facility acceleration; cure rights can defer remedies but do not establish spare capacity. | Negative — Covenant Erosion if performance deteriorates; current headroom is Not Calculable. | No supported comparator. | [C1, C2, C15] |
| Incremental and ratio debt | Incremental Amount has a greater-of $2.6 billion or 1.00x EBITDA component, plus ratio-based and other components; pari collateral debt may use the 4.50x senior secured test. | Credit Agreement §§1.01, 2.21, 6.01(h), (r), (ee) | Grower and ratio routes can add pari debt and dilute existing first-lien recovery; usage and current covenant EBITDA are missing. | Negative — Leverage Increase; remaining capacity Not Calculable. | No supported comparator. | [C3, C4] |
| EBITDA and pro forma mechanics | Covenant EBITDA includes specified restructuring, transaction, non-cash and pro forma adjustments; some expected savings may be included subject to the definition’s conditions. | Credit Agreement §1.01, EBITDA and Pro Forma Basis | An expanded denominator can increase ratio-based debt and payment capacity even when cash generation does not rise proportionately. | Negative — Covenant Erosion; no quantitative inflation estimate. | No supported comparator. | [C5] |
| Restricted payments | Cumulative Credit supports specified payments; separate fixed/grower and ratio routes include a $300 million / 0.10x EBITDA basket and a 4.75x leverage test. | Credit Agreement §6.06(e), (h), (l) | Distributions can reduce cash available for debt service; the ratio route is conditional, while current use is unknown. | Negative — Liquidity Deterioration / Covenant Erosion. | No supported comparator. | [C7, C18] |
| Investments and unrestricted subsidiaries | Permitted investment routes include a $975 million / 0.425x EBITDA general basket and separate unrestricted-subsidiary investment capacity; certain designations require no default and pro forma compliance. | Credit Agreement §§1.01, 6.04(j), (s), (mm) | Investments/designations may transfer value beyond direct lender reach and may reclassify among eligible baskets. | Negative — Covenant Erosion; usage and entity value are unknown. | No supported comparator. | [C6, C8] |
| Collateral, guarantees and releases | The agreement identifies excluded property and subsidiaries and permits specified project-related collateral and guarantee releases; the indenture describes notes as pari passu with first-priority obligations. | Credit Agreement §§1.01, 5.11, 9.18; Indenture | Release or exclusion can reduce reachable assets; no current collateral schedule or executed ICA confirms full coverage or sharing. | Negative — Refinancing Risk / recovery dilution; no recovery valuation. | No supported comparator. | [C9, C10, C11, C12] |
| Amendments and lender control | Required-Lender consent governs ordinary amendments, subject to affected-lender and sacred-right provisions; the Fourth Amendment documents automatic replacement/assignment mechanics for non-consenting and reallocating lenders. | Credit Agreement §§2.19(c), 9.08; Fourth Amendment §§3–4 | Replacement mechanics can facilitate repricing or amendment despite holdouts; applicable thresholds and class effects remain document-specific. | Negative — Refinancing Risk, with countervailing sacred rights. | No supported comparator. | [C19, C26] |
| Events of Default and cure | Covenant failure may be an Event of Default for Covenant Facilities; equity cure may increase EBITDA for the test, subject to frequency and amount limits. | Credit Agreement §§7.01(d), 7.02 | Cure can delay acceleration after a deterioration trigger but may mask underlying deleveraging needs; current cure history is absent. | Neutral — Stable only while tests are met; current covenant status is issuer-reported. | No supported comparator. | [C15] |

#### T4.9 — PD versus LGD / Recovery Translation

| Legal Topic | Supported Fact | Risk Mechanic | PD Effect | LGD / Recovery Effect | Monitoring Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Maintenance tests | 6.50x maximum leverage and 2.00x minimum fixed-charge coverage apply to relevant Covenant Facilities; Q2 filing reports compliance. | Operating weakness can reduce covenant EBITDA or cash coverage; a breach can trigger acceleration subject to cure and facility-specific terms. | Potentially adverse on deterioration; present status reported compliant, headroom unknown. | Indirect: acceleration pressure may reduce restructuring time; no recovery amount inferred. | Review each certificate, tested ratios, revolver utilization, cure notices and testing-condition status. | [C1, C2, C15] |
| Pari debt and liens | Incremental and ratio debt routes permit specified additional secured debt, including pari debt subject to ratio tests. | New pari debt increases leverage and shares collateral value, potentially lowering existing lenders’ recovery per dollar. | Higher leverage can increase default/refinancing risk. | Direct dilution of first-lien collateral proceeds if incurred. | Track new facilities, debt notices, pro forma calculations and lien/intercreditor joinders. | [C3, C4] |
| EBITDA definition | The credit definition permits specified add-backs and pro forma adjustments, including expected savings under conditions. | A larger denominator increases ratio capacity without matching cash proceeds; subsequent operating shortfall can expose the gap. | May defer test pressure and increase leverage tolerance. | Indirect dilution if denominator supports additional secured debt. | Compare certificates with issuer Adjusted EBITDA and require covenant bridge/support. | [C5] |
| RP and investment leakage | Payment and investment baskets include fixed/grower and ratio pathways, with current usage unavailable. | Cash or assets may leave the restricted group before distress, reducing liquidity and assets available to creditors. | Potential increase if leakage weakens debt-service resources. | Potentially adverse if value moves outside collateral/guarantor reach. | Monitor distributions, investment trackers, designation notices and asset transfers. | [C6, C7, C8] |
| Guarantee and collateral perimeter | Material wholly owned domestic subsidiaries are generally described as guarantors; exclusions and automatic release provisions exist. | Coverage gaps or permitted releases can leave assets outside the relevant secured claim group. | Limited direct PD effect; possible reduction in support for refinancing. | Potentially adverse recovery access; cannot quantify without entity and collateral schedules. | Obtain current guarantor, collateral, perfection and release schedules. | [C9, C11, C13] |
| Covenant compliance statement | Issuer reports compliance as of June 30, 2026; this is not a calculation of cushion or unused capacity. | A point-in-time status can change after quarter-end; declining Las Vegas performance can reduce earnings before the next test. | Neutral at the reported date; future risk remains conditional. | No direct recovery conclusion. | Review next certificate and operating trend; separate subsequent events. | [C15, C27] |

#### T4.10 — Market Norm Comparison

| Topic | Issuer Provision | Market / Third-Party Reference | Relative Assessment | Agreement / Discrepancy | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Comparative covenant assessment | [Insufficient Information] — executed provisions are available, but no market dataset or third-party covenant-review report was delivered. | [Insufficient Information] — no comparative source in the delivered evidence. | Not assessed. | No relative-market conclusion is supportable. | Market-norm commentary omitted; provision-level risk analysis remains source-based. | G-08 |

#### T4.11 — Covenant Aggressiveness Score

| Area | Score 1–5 | Evidence | Risk Mechanic | Credit Implication | Confidence | Evidence ID |
|---|---:|---|---|---|---|---|
| Maintenance covenant architecture | 4 | Tests are limited to Covenant Facilities; reported 6.50x and 2.00x thresholds, with conditional revolver testing after Term A repayment. | Narrower tested perimeter and lack of supplied headroom/certificates reduce visibility into early intervention. | Negative — Covenant Erosion | Provisional | [C1, C2, C15] |
| Debt / lien incurrence capacity | 4 | Greater-of and ratio baskets permit incremental debt, including pari collateral debt. | Additional secured debt can increase leverage and dilute existing claims. | Negative — Leverage Increase | Provisional | [C3, C4] |
| RP / investment / leakage capacity | 4 | Distinct RP and investment baskets plus unrestricted-subsidiary routes are documented. | Value can be distributed, invested or transferred; usage is unknown. | Negative — Covenant Erosion | Provisional | [C6, C7, C8] |
| EBITDA definitions and add-back flexibility | 4 | Broad pro forma and adjustment language is present; expected savings can be included subject to conditions. | Denominator expansion can increase legal capacity beyond cash-supported debt-service capacity. | Negative — Leverage Increase | Provisional | [C5] |
| Collateral / guarantor protection | 4 | Broad domestic guarantor description is offset by exclusions, absent schedules and permitted releases. | Missing assets or released guarantors can reduce recovery access. | Negative — Refinancing Risk | Provisional | [C9, C11, C13] |
| Amendment / control mechanics | 3 | Required-Lender framework includes affected-lender/sacred-right protections; replacement mechanics are also documented. | Holdout replacement can facilitate selected amendments, while sacred rights constrain certain changes. | Negative — Refinancing Risk | Provisional | [C19, C26] |
| Overall | 4 | Composite judgment weighted toward documented debt, leakage and EBITDA flexibility; six areas are provisionally scorable. | Highest creditor-adverse areas dominate; incomplete schedules, certificates and ICA lower confidence. | Negative — Covenant Erosion | Provisional | [C3, C5, C7, C8, C11] |

**Covenant Aggressiveness Score:** 4/5 — Provisional. This is an evidence-based analytical score, not a legal conclusion or credit rating; it is not a simple average.

#### T4.12 — Red Flags and Monitoring Triggers

| Red Flag / Trigger | Provision or Signal | Why It Matters | PD / LGD / RV Impact | Monitoring Action | Evidence ID |
|---|---|---|---|---|---|
| New pari first-lien incremental debt | Credit Agreement §§2.21, 6.01 and incremental-amount definition | Can increase secured claims sharing collateral and add leverage; current utilization is unknown. | PD and LGD adverse if incurred; no capacity amount calculated. | Request incremental notices, usage schedule and pro forma test certificate. | [C3, C4] |
| Unrestricted-subsidiary designation or investment | Credit Agreement §§1.01, 6.04 | Can transfer value outside the restricted group subject to specified conditions. | Potential LGD/recovery leakage; potential PD effect through reduced liquidity. | Track designation, asset transfer and investment-certificate disclosures. | [C6, C8] |
| Covenant test deterioration or cure notice | Credit Agreement §§6.11, 7.01(d), 7.02 | Lower earnings/coverage can trigger a covenant Event of Default; cure can defer remedies. | PD/refinancing risk rises if deterioration persists or cure capacity is exhausted. | Obtain each certificate, test calculation and cure history. | [C1, C2, C15] |
| Collateral or guarantor release | Credit Agreement §§5.11, 9.18; Indenture §12.04 | Permitted releases can reduce collateral or guarantee support. | LGD/recovery access may weaken. | Monitor releases, dispositions, project notices and guarantee schedule changes. | [C10, C13] |
| Merger financing or closing changes | Q2 merger disclosure and Form 8-K financing-commitment statement | Financing terms and closing could alter debt, liquidity and refinancing requirements; complete commitments are absent. | Potential PD/refinancing risk; no pro forma conclusion. | Obtain executed commitment letters, amendments and definitive financing documents; track closing conditions. | [C21, C22, C28] |
| Intercreditor control and standstill | Executed ICA not delivered; only a form is identified in the credit-agreement contents. | Voting, enforcement standstill, turnover and release-control terms cannot be confirmed. | Recovery-control uncertainty; no recovery percentage assigned. | Obtain executed current ICA and all joinders/amendments. | [C25] |

#### T4.13 — Gaps Ledger

| Gap | Missing Document / Clause / Schedule | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Current controlling credit-agreement package | Complete post-Fifth Amendment conformed agreement, all later amendments, waivers, schedules and exhibits | The delivered conformed text predates the Fourth and Fifth Amendments; referenced schedules are not all represented. | T4.2–T4.8, covenant conclusions and T4C capacity formulas may omit operative changes or usage. [C20] | Obtain a current conformed executed agreement, all later amendments and the complete schedules. |
| Current tested ratios and covenant EBITDA | Compliance certificate, covenant EBITDA bridge and test calculations | Reported compliance does not establish headroom; issuer Adjusted EBITDA is not automatically covenant EBITDA. | T4.4–T4C.5; no exact headroom or ratio capacity. [C5, C15] | Obtain the latest certificate, calculation schedules, add-back support and governing EBITDA bridge. |
| Basket usage | Current debt, lien, RP, investment, builder/Cumulative Credit, reclassification and designation trackers | Legal basket formulas do not reveal utilization or remaining capacity. | T4C.5–T4C.9; remaining amounts Not Calculable. [C6, C7, C18] | Obtain current covenant usage certificates and transaction-level tracker, with shared-basket mapping. |
| Entity, collateral and guarantor perimeter | Current subsidiary, unrestricted-subsidiary, guarantor, collateral, excluded-asset and perfection schedules | Missing schedules prevent complete entity-by-entity reachable-value analysis and current guarantee/perfection confirmation. | T4D.2–T4D.5 and recovery-access assessment. [C9, C11, C13] | Obtain current organizational chart, schedules, security documents, perfection certificates and release history. |
| Executed intercreditor agreement | Current executed first-lien and any second-lien ICA, amendments and joinders | The conformed agreement references forms, not proof of an executed operative ICA; enforcement, standstill and turnover cannot be inferred. | T4F.1–T4F.5 and CP-3A/CP-4C recovery-control inputs. [C25] | Obtain executed current agreements and all authorized-representative joinders. |
| Merger financing and agreement schedules | Complete merger agreement and debt commitment letters, including schedules and any definitive financing documents | The Form 8-K states commitments were delivered but their full terms are not in the evidence; the exhibit index identifies the merger agreement and omitted schedules. | Transaction-specific debt, covenant and refinancing overlay incomplete. [C21, C28] | Obtain complete executed instruments and refresh the source set before transaction pro forma analysis. |
| Missing upstream context | CP-1A entity/transaction handoff and CP-3C refinancing/LME handoff are not accepted inputs in this route payload | These are declared CP-4 dependencies; their absence limits entity and refinancing/LME context but does not invalidate the available legal analysis. | Restricted-group cross-check and LME overlay remain incomplete. | Incorporate matching accepted handoffs on a linked rerun when available. |
| Market comparison | Third-party covenant review or relevant comparative legal source | No provision-level relative-market conclusion can be supported. | T4.10 skipped as a comparative assessment. | Provide a dated, comparable covenant-review source if market-relative analysis is required. |
| Non-debt operating float | Current covenant treatment and full liability roll-forward for deposits/deferred revenue | The credit definition excludes prepaid/deferred revenue; customer funds also carry performance or refund obligations. | Liquidity and debt-capacity interpretation must keep this float distinct from debt. [C16, C17] | Reconcile current balances and obligations to covenant debt definitions and liquidity reporting. |

#### T4C.2 — Controlling Capacity Source Map

| Authority Rank | Source | Source Type | Version / Date | Status | Controls Legal Formula / Financial Input / Usage | Credit Relevance | Evidence ID |
|---|---|---|---|---|---|---|---|
| 1 | Credit Agreement and delivered amendments | Executed legal documents | July 20, 2020 base; conformed through February 6, 2024; Fourth May 9, 2024; Fifth November 25, 2024 | Executed; schedules incomplete | Legal formula | Controls loan-facility covenant definitions, formulas, capacities and release mechanics. | [C3, C20] |
| 1 | 2032 Notes Indenture and supplements | Executed indenture package | February 6, March 1 and August 23, 2024 | Executed | Legal formula | Controls 2032 Notes restrictions, guarantees, collateral, amendments and remedies. | [C10, C11] |
| 3 | Q2 2026 Form 10-Q | Interim filing | June 30, 2026 | Filed; unaudited | Financial input and issuer-reported compliance | Current debt and reported covenant status; not covenant EBITDA or basket usage. | [C14, C15] |
| 3 | Current compliance certificates and basket trackers | Certificate / usage schedules | Not delivered | [Insufficient Information] — no current certificates or tracker in the delivered evidence | Tested ratios and usage unavailable | Prevents exact headroom and remaining-capacity calculations. | G-02, G-03 |
| 2 | Executed current intercreditor agreement | Intercreditor agreement | Not delivered; credit-agreement contents identify a form | [Insufficient Information] — no executed ICA provided | Intercreditor formula and enforcement usage unavailable | Prevents standstill, turnover and enforcement-control assessment. | [C25] |

#### T4C.3 — Covenant Definition and Ratio Mechanics Register

| Definition / Ratio | Source / Clause | Formula / Definition Summary | Required Inputs | Capacity Effect | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|
| Credit Agreement EBITDA | Credit Agreement §1.01 | Consolidated net income plus defined tax, interest, D&A, restructuring, transaction and other adjustments; pro forma provisions may include expected savings subject to conditions. | Period statements, adjustment bridge, eligibility support and pro forma certificate. | Can increase ratio debt, RP and grower-basket capacity. | A non-cash or forward-looking add-back can expand denominator without contemporaneous cash generation. | Negative — Leverage Increase | [C5] |
| Total Leverage Ratio | Credit Agreement §§1.01, 6.11 | Total Net Debt / EBITDA, calculated on a pro forma basis under the governing definitions. | Covenant debt, permitted cash netting, covenant EBITDA and test period. | Determines maintenance compliance and ratio-based permissions. | Definition differences from reported debt/Adjusted EBITDA may change the tested ratio. | Insufficient Information — no current calculation. | [C1, C5, C14] |
| Senior Secured Leverage Ratio | Credit Agreement §1.01 | First-lien secured net debt / EBITDA, pro forma; specified excluded categories and cash netting apply. | First-lien debt, collateral classification, eligible cash, EBITDA and pro forma events. | Governs pari secured ratio debt and liens. | A permissive denominator and debt perimeter can support additional pari obligations. | Negative — Leverage Increase | [C4] |
| Fixed Charge Coverage Ratio | Credit Agreement §§1.01, 6.11 | EBITDA / defined cash interest expense, pro forma; specified debt and development exclusions apply. | Covenant EBITDA, cash interest, eligible exclusions and test period. | Affects maintenance testing and unsecured debt incurrence. | Lower coverage can constrain borrowing or create default risk; exclusions can alter the test. | Insufficient Information — no current calculation. | [C2, C5] |
| Indebtedness | Credit Agreement §1.01 | GAAP-linked definition with express exclusions, including prepaid or deferred revenue arising in ordinary course. | GAAP liabilities, specific contractual treatment and any bespoke ratio debt definition. | Excluded operating liabilities may remain outside debt baskets and tests. | Customer funding obligations may still transmit to liquidity despite exclusion from covenant debt. | Insufficient Information — current covenant bridge and float reconciliation missing. | [C16, C17] |
| Incremental Amount | Credit Agreement §1.01 and §2.21 | Greater of $2.6 billion and 1.00x pro forma EBITDA, plus additional ratio and specified repayment components; not summed across shared uses without support. | EBITDA, debt and commitment usage, repayment history, ratio compliance and reclassification. | Potential fixed/grower and ratio-based debt capacity. | Reclassification and shared debt routes can increase fungibility; remaining capacity is unknown. | Negative — Leverage Increase | [C3, C4] |

#### T4C.4 — Headroom Table

| Test | Test Type | Threshold | Current Basis | Formula | Headroom | Status | Limitation | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|---|---|---|
| Total Leverage Ratio — Covenant Facilities | Maximum ratio | 6.50x from December 31, 2024 | [Insufficient Information] — June 30 compliance is reported, but covenant ratio and bridge are not supplied | Threshold − current tested ratio | [Insufficient Information] — missing current tested ratio and covenant EBITDA | Insufficient Information | Q2 status does not give test value or distance to breach. | Earnings decline or debt increase could consume covenant cushion. | Insufficient Information | [C1, C15] |
| Fixed Charge Coverage Ratio — Covenant Facilities | Minimum ratio | 2.00x from December 31, 2024 | [Insufficient Information] — no current tested ratio or covenant EBITDA bridge | Current tested ratio − threshold | [Insufficient Information] — missing current tested ratio and numerator/denominator bridge | Insufficient Information | Exact interest, exclusions and current test calculation unavailable. | Lower EBITDA or increased cash interest could reduce coverage. | Insufficient Information | [C2, C15] |
| Pari secured incremental ratio test | Maximum ratio | 4.50x, or prior ratio in specified acquisition/investment cases | [Insufficient Information] — current senior secured ratio unavailable | Threshold − pro forma senior secured leverage | [Insufficient Information] — missing current ratio, EBITDA and current debt usage | Insufficient Information | No exact additional debt capacity calculated. | New pari debt may both raise leverage and dilute collateral. | Insufficient Information | [C4] |
| Unsecured incremental ratio test | Minimum ratio | 2.00x Fixed Charge Coverage Ratio | [Insufficient Information] — current test value unavailable | Current pro forma FCCR − threshold | [Insufficient Information] — missing current covenant calculation | Insufficient Information | No exact unsecured capacity calculated. | Lower coverage can close the unsecured borrowing route. | Insufficient Information | [C2] |

#### T4C.5 — Capacity Register

| Capacity Type | Basket / Test | Formula | Conditions | Current Input | Usage | Estimated Capacity | Remaining Capacity | Status | Severity | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Debt incurrence capacity | Incremental Amount / §2.21 | Greater of $2.6bn and 1.00x pro forma EBITDA, plus additional clauses in the definition | Ratio tests, eligible class, documentation and other stated conditions | [Insufficient Information] — covenant EBITDA and debt/commitment schedule absent | [Insufficient Information] — no tracker | Not Calculable from Provided Materials — no current inputs | [Insufficient Information] — missing usage and current inputs | Formula Extracted Only | High | Can support additional debt; pari secured debt can dilute first-lien claims. | Negative — Leverage Increase | [C3, C4] |
| Debt incurrence capacity | General basket / §6.01(k) | Greater of $750m and 0.325x pro forma EBITDA | Subject to agreement conditions and refinancing terms | [Insufficient Information] — current EBITDA unavailable | [Insufficient Information] — no tracker | Not Calculable from Provided Materials — grower input unavailable | [Insufficient Information] — missing usage | Formula Extracted Only | Moderate | Fixed/grower capacity may add debt; classification and reclassification affect other baskets. | Negative — Leverage Increase | [C3] |
| Investment capacity | General investment / §6.04(j) | Greater of $975m and 0.425x pro forma EBITDA, plus permitted returns and elected Cumulative Credit | Basket terms, cap, eligible investment and any applicable conditions | [Insufficient Information] — current EBITDA unavailable | [Insufficient Information] — no usage tracker | Not Calculable from Provided Materials — no current inputs | [Insufficient Information] — missing usage | Formula Extracted Only | High | Investments can move cash or assets to non-Loan Parties. | Negative — Covenant Erosion | [C6] |
| Unrestricted-subsidiary capacity | §6.04(s) and designation terms | Greater of $210m and 0.10x pro forma EBITDA, plus specified returns | No continuing or resulting Event of Default; designation and investment conditions apply | [Insufficient Information] — current EBITDA and entity schedule absent | [Insufficient Information] — no tracker | Not Calculable from Provided Materials — current EBITDA unavailable | [Insufficient Information] — missing usage | Formula Extracted Only | High | Funding/designation can place assets beyond the credit group. | Negative — Covenant Erosion | [C8] |
| Restricted payment capacity | Cumulative Credit / §6.06(e) | Greater of $240m and 0.105x pro forma EBITDA plus specified components, less usage | No Event of Default; pro forma compliance; election and notice; timing limits | [Insufficient Information] — cumulative components and EBITDA unavailable | [Insufficient Information] — no RP tracker | Not Calculable from Provided Materials — build-up inputs unavailable | [Insufficient Information] — missing usage | Formula Extracted Only | High | Distributions can reduce liquidity and secured-credit support. | Negative — Liquidity Deterioration | [C18] |
| Restricted payment capacity | General RP / §6.06(l) | Greater of $300m and 0.10x pro forma EBITDA, shared with specified junior-debt payments | No Event of Default; shared-cap terms apply | [Insufficient Information] — current EBITDA unavailable | [Insufficient Information] — no shared usage tracker | Not Calculable from Provided Materials — current inputs unavailable | [Insufficient Information] — missing usage | Formula Extracted Only | High | Shared capacity can be used for distributions or junior debt payments. | Negative — Covenant Erosion | [C7] |

#### T4C.6 — Debt, Lien, and Priming Capacity Analysis

| Route | Supported Legal Capacity | Current Calculation Status | Priming / Dilution Mechanic | PD Effect | LGD / Recovery Effect | RV / Security Selection Effect | Evidence ID |
|---|---|---|---|---|---|---|---|
| Pari first-lien incremental debt | Ratio-based pari debt and incremental routes are provided, subject to the senior secured leverage test and documentation conditions. | Formula Extracted Only; usage and current ratio unavailable. | New pari debt shares first-priority collateral and increases debt burden; no evidence of a completed current-period draw from these clauses. | Potential increase in leverage and refinancing risk. | Potential dilution of existing first-lien recovery. | Distinguish first-lien instruments by collateral reach; no relative value conclusion without market evidence. | [C3, C4, C12] |
| Junior-lien and unsecured debt | The agreement permits specified junior-lien and unsecured debt subject to leverage/coverage tests, caps and intercreditor provisions. | Formula Extracted Only; current usage and executed intercreditor terms unavailable. | Additional claims may layer behind or alongside existing claims; priority depends on operative lien and ICA documents. | Potential increase in leverage/refinancing risk. | Potential collateral dilution or structural subordination. | Security selection requires current debt and executed ICA. | [C3, C4, C25] |
| Non-Loan-Party debt | The agreement includes capped non-Loan-Party debt routes and permits specified liens on non-Collateral assets. | Formula Extracted Only; entity-level debt and usage unavailable. | Debt at a non-guarantor may be serviced from subsidiary value before value reaches parent creditors. | Potentially adverse if operating entities incur material debt. | Potential structural priority; no current stranded value established. | Entity-level debt schedule required. | [C9] |
| Grower-basket and reclassification route | Defined debt baskets and classification/reclassification provisions can be used in combination, but the agreement prohibits counting the same item twice. | Not Calculable from Provided Materials. | Reclassification can preserve capacity under another permitted route; usage is not proven. | Potential increase if used to add debt under stress. | Potential dilution depends on lien and obligor. | Do not aggregate overlapping baskets. | [C3] |

#### T4C.7 — RP, Investment, Asset Transfer, and Leakage Analysis

| Leakage Route | Supported Fact | Formula / Basket | Usage / Remaining Capacity | Restricted-Group / Collateral Impact | Severity | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|
| Investment into unrestricted subsidiary | Investment route and designation mechanics are documented, subject to stated conditions. | §6.04(s), greater of $210m or 0.10x EBITDA plus returns; separate designation conditions. | [Insufficient Information] — usage, EBITDA and entity-value schedules absent. | Potentially moves cash/assets outside the credit group; actual transfers not demonstrated. | High | Negative — Covenant Erosion | [C6, C8] |
| RP / junior-debt payment | Separate RP and junior-debt payment routes are available under specified tests and shared caps. | §6.06(e), (h), (l); §6.09(b); formula-only. | [Insufficient Information] — current cumulative-credit and basket usage unavailable. | Cash may leave the obligor group and reduce liquidity available for creditors. | High | Negative — Liquidity Deterioration | [C7, C18] |
| Asset sale / transfer | Asset sale provisions permit specified dispositions, and permitted collateral dispositions may be released from liens. | §6.05; reinvestment, proceeds and fair-value conditions vary by route. | [Insufficient Information] — disposition tracker and proceeds application absent. | Collateral can leave the secured pool where an eligible disposition is permitted. | High | Negative — Refinancing Risk | [C13] |
| Interactive entertainment / convention center | Definitions identify specific unrestricted-subsidiary investment/designation pathways. | Credit Agreement §1.01 and applicable investment/disposition provisions. | [Insufficient Information] — no current designation, asset value or usage schedule. | Theoretical transfer route only; no current-period transfer established here. | High | Negative — Covenant Erosion | [C8] |
| Customer deposits and deferred revenue | Q2 filing reports customer deposits/deferred revenue of $545m at June 30; credit Indebtedness definition excludes ordinary-course prepaid/deferred revenue. | Excluded from defined Indebtedness; not an RP basket. | Not a basket usage figure; full covenant/liquidity reconciliation unavailable. | Operating float has customer performance/refund obligations and is not free cash or debt. | Moderate | Negative — Liquidity Deterioration | [C16, C17] |

#### T4C.8 — EBITDA Add-Back and Capacity Inflation Analysis

| Add-Back / Definition Feature | Source / Clause | Cap / Condition | Calculation Status | Capacity Inflation Mechanic | PD / LGD / RV Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Restructuring, optimization and cost savings | Credit Agreement §1.01, EBITDA | Expected to be achieved, completed or realized within 24 months, in Borrower good-faith determination; other definition conditions apply. | Formula Extracted Only; current covenant bridge unavailable. | Permitted adjustments may enlarge EBITDA and grower/ratio capacity without equal cash realization. | Potentially increases leverage tolerance and pari debt capacity; impact cannot be quantified. | [C5] |
| Pro forma transactions and savings | Credit Agreement §1.01, Pro Forma Basis | Responsible-officer good-faith determination and stated fact-supportability conditions; detailed supporting schedules absent. | Formula Extracted Only. | Acquisitions, dispositions, designations and operating changes may alter test-period EBITDA and debt calculations. | Potentially increases borrowing capacity; no current amount estimated. | [C5, C8] |
| Issuer Adjusted EBITDA versus covenant EBITDA | Q2 Form 10-Q, Adjusted EBITDA disclosure; Credit Agreement §1.01 | Issuer states its non-GAAP definition may differ from debt-agreement definitions. | Not Calculable from Provided Materials — no covenant bridge. | Substituting issuer Adjusted EBITDA could misstate covenant ratios and basket capacity. | No numerical conclusion; require reconciliation before capacity use. | [C5, C15] |

#### T4C.9 — Leakage and Basket Flags

| Flag | Supported Fact | Creditor Risk | Severity | Confidence | Downstream Module | Evidence ID |
|---|---|---|---|---|---|---|
| Grower and ratio capacity | Incremental debt and ratio routes use EBITDA and leverage tests. | Additional debt and first-lien dilution; current remaining capacity unavailable. | High | Formula Only | CP-4A, CP-3A, CP-6 | [C3, C4] |
| Basket fungibility / reclassification | Credit agreement permits classification and reclassification across qualifying debt, investment and payment categories, subject to non-duplication. | Actual capacity may be accessed through different routes; do not total baskets without proof of independent use. | High | Formula Only | CP-4A, CP-6 | [C3, C6, C7] |
| Unrestricted-subsidiary leakage | Investment and designation pathways exist, with conditions. | Potential assets outside direct lender reach; current use and value are unknown. | High | Provisional | CP-4B, CP-3A, CP-6 | [C6, C8] |
| Guarantor/collateral release | Contractual releases are available in specified circumstances. | Potential reduction in recovery access; current entity-level effect not known. | High | Provisional | CP-4B, CP-3A, CP-4C | [C9, C10, C13] |
| Amendment and replacement mechanics | Executed amendment shows non-consenting lender replacement and non-pro-rata allocation mechanics; agreement retains specified sacred rights. | Could facilitate repricing or amendment for affected loan classes, subject to required conditions and voting rules. | Moderate | Directly sourced | CP-6, CP-4C | [C19, C26] |

#### T4C.11 — Capacity Risk Prioritization Matrix

| Priority | Capacity Item | Severity | Confidence | Primary Risk Mechanic | PD Effect | LGD / Recovery Effect | Monitoring Action | Evidence ID |
|---|---|---|---|---|---|---|---|---|
| 1 | Pari secured incremental debt | High | Formula Only | Ratio and incremental pathways could add leverage while sharing first-priority collateral. | Adverse if used during earnings deterioration. | Potential direct dilution of first-lien recovery. | Obtain current incremental debt and lien usage; review certificates. | [C3, C4] |
| 2 | Unrestricted-subsidiary and investment route | High | Formula Only | Cash or assets may be invested or designated outside the credit group. | Possible increase if leakage reduces liquidity. | Potential loss of reachable value; current value unknown. | Track designations, transfers and usage. | [C6, C8] |
| 3 | EBITDA add-backs and pro forma adjustments | High | Formula Only | Denominator expansion can create additional ratio capacity without equivalent cash flow. | May defer test pressure and permit releveraging. | Indirect dilution if used to support secured debt. | Reconcile certificate adjustments to current source data. | [C5] |
| 4 | RP and junior-debt payments | High | Formula Only | Cash may leave the obligor group through permitted baskets. | Potentially adverse to liquidity and debt service. | Potential reduction in assets available for repayment. | Track RP/junior-debt notices and shared basket usage. | [C7, C18] |
| 5 | Guarantees, collateral exclusions and releases | High | Provisional | Excluded assets/entities and permitted releases can reduce creditor reach. | Limited direct PD effect; refinancing support may weaken. | Potential recovery-access impairment; no recovery amount assigned. | Obtain current entity and collateral schedule and release history. | [C9, C11, C13] |

#### T4C.12 — Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Current covenant calculations | Tested leverage and coverage ratios, covenant EBITDA bridge and current certificate | Compliance alone does not give headroom or capacity. | T4C.3–T4C.5; no current headroom. [C1, C2, C15] | Obtain current compliance certificate and detailed calculation schedules. |
| Basket usage | Debt, lien, RP, investment, builder and designation tracker | Remaining capacity cannot be treated as unused. | T4C.5–T4C.9. [C6, C7, C18] | Obtain current usage, reclassification and shared-cap records. |
| Non-Loan-Party debt/value | Entity-level debt, EBITDA and assets | Necessary to assess structural debt and value movement. | T4C.6–T4C.7 and CP-3A recovery inputs. | Obtain current debt-by-entity and value schedule. |
| Covenant EBITDA definition bridge | Reconciliation of issuer measures to legal EBITDA | Reported Adjusted EBITDA is not automatically covenant EBITDA. | T4C.3, T4C.4 and T4C.8. [C5] | Obtain bridge, add-back support and pro forma certificates. |
| Executed intercreditor/perfection package | Executed ICA, current joinders, lien and guarantee schedules | Legal capacity does not establish control, perfected status or realized recovery. | T4D/T4F and CP-3A/CP-4C. [C25] | Obtain current executed documents and confirm filing/perfection status. |

#### T4D.1 — Structural Source Gate Register

| Source | Status | Authority Rank | Limitations | Module Status |
|---|---|---:|---|---|
| Credit Agreement, conformed text and Fourth/Fifth Amendments | Executed; primary legal source | 1 | Referenced schedules and a current post-amendment conformed version are not fully delivered. | Completed with Limitations [C19, C20] |
| 2032 Notes Indenture and first/second supplements | Executed; primary legal source | 1 | Indenture schedules do not supply current entity value, all collateral schedules or current perfection evidence. | Completed with Limitations [C10, C11] |
| Q2 2026 Form 10-Q | Filed; current issuer disclosure | 3 | Does not provide a complete entity-by-entity debt, collateral or guarantor schedule. | Completed with Limitations [C13, C14] |
| Current org chart, subsidiary schedule, collateral schedule and executed ICA | [Insufficient Information] — not delivered | — | Entity ownership, current designations, asset location, perfection and enforcement control cannot be fully mapped. | Completed with Limitations [C25] |

#### T4D.2 — Restricted / Unrestricted Entity Register

| Entity | Role | Jurisdiction | Parent | Designation | Material Value Held | Inside Credit Group? | Evidence ID |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Borrower and 2032 Notes issuer | Delaware | — | Restricted/issuer perimeter; not an unrestricted subsidiary | [Insufficient Information] — entity-specific assets not supplied | Yes, direct obligor | [C10, C14] |
| Named Subsidiary Loan Parties on delivered Credit Agreement execution pages | Subsidiary Loan Parties; credit agreement guarantor/security parties as specified by schedules and documents | Multiple; full current jurisdiction/ownership mapping unavailable | [Insufficient Information] — current parent schedule absent | Credit agreement perimeter; current designation by entity not fully established | [Insufficient Information] — no entity-level schedule | Yes, to the extent currently a Loan Party; exact roster and coverage by facility require schedules | [C11, C13] |
| 2032 Notes subsidiaries listed in the delivered supplemental indentures | Subsidiary guarantors / New Guarantors | Multiple U.S. jurisdictions; individual roster appears in schedules/signatures | [Insufficient Information] — current ownership chart absent | Notes-guarantor status supported for listed signatories; later changes unknown | [Insufficient Information] — no values by entity | Yes for the 2032 Notes, subject to documented exclusions/releases | [C11] |
| Caesars Virginia, LLC | Subsidiary / separate facility borrower | Virginia | Ownership chain not supplied | [Insufficient Information] — current restricted-group designation not established | Facility assets not quantified here | No CEI guarantee of CVA facilities reported | [C13] |
| CRC, CEOC and their respective subsidiaries | Subsidiary/legacy structural perimeter referenced in exclusions and legacy documents | [Insufficient Information] — current entity details not delivered | [Insufficient Information] — current parent schedule absent | Current designation and debt status not established by the delivered excerpt | [Insufficient Information] — current value/debt by entity unavailable | Credit Agreement excludes their assets unless elected otherwise; current reach must be confirmed | [C9] |
| Unrestricted Subsidiaries listed in the 2032 Notes schedule | Unrestricted subsidiaries as of the indenture issue-date schedule | Schedule lists multiple jurisdictions | Company | Issue-date designation; current status may have changed | [Insufficient Information] — current entity values absent | No for the Notes restricted group unless redesignated; current map unavailable | [C8, C23] |

#### T4D.3 — Guarantor Coverage Matrix

| Entity × Tranche | Guarantee Type | Direction | Release Trigger | Evidence ID |
|---|---|---|---|---|
| Caesars Entertainment, Inc. × CEI facilities and 2032 Notes | Direct borrower/issuer obligation; not a subsidiary guarantee | Direct | Payment, defeasance or other instrument-specific release | [C10, C13] |
| Material wholly owned domestic subsidiaries × CEI facilities / senior secured notes | Senior secured subsidiary guarantees, subject to documented exceptions | Subsidiary guarantees; individual direction/caps not established in delivered schedules | Permitted disposition, excluded-subsidiary status, project/other contractual release provisions | [C11, C13] |
| Subsidiary guarantors × 2032 Notes | Joint and several note guarantees; individual coverage follows executed indenture and supplements | Subsidiary guarantees | Permitted sale, unrestricted designation, release of qualifying debt guarantee, defeasance or other indenture conditions | [C11] |
| Caesars Virginia, LLC × CVA facilities | Borrower/obligor under its facilities; CEI does not guarantee them | Separate subsidiary borrower | Facility-specific terms not delivered | [C13] |

#### T4D.4 — Collateral-by-Entity Matrix

| Entity × Lien | Excluded Assets | Release Mechanic | Perfection Limit | Evidence ID |
|---|---|---|---|---|
| Borrower and Loan Parties × first-priority secured facilities / 2032 Notes | Excluded Property, regulatory/Gaming Law restrictions, specified CRC/CEOC assets and other contractual exclusions | Automatic or permitted releases on eligible dispositions, termination, excluded status or project financing under the operative documents | Current collateral schedules, perfection certificate and filing evidence absent; Gaming Authority approval may constrain enforcement | [C9, C10, C13] |
| Subsidiaries not shown to be Loan Parties × secured claims | No general collateral reach established; some permitted debt may be secured by non-Collateral assets | Not determined without entity schedules and executed security documents | Entity-level liens and perfection unavailable | [C3, C9] |
| Caesars Virginia, LLC × CVA facilities | Separate facility collateral perimeter; detailed asset schedule absent | Facility-specific | Q2 filing describes substantially all material CVA assets as secured; CEI does not guarantee CVA facilities | [C13] |
| Credit Agreement × second-lien or other junior lien tier | No current junior-lien grant or executed ICA established in delivered evidence | [Insufficient Information] — no executed junior-lien package | [Insufficient Information] — no junior lien schedule or executed ICA | [C25] |

#### T4D.5 — Structural Priority Table

| Claim/Tranche | Obligor Entity | Reachable Value | Structural-Priority Label | Stranded Value Named | Recovery-Access Implication | Confidence | Evidence ID |
|---|---|---|---|---|---|---|---|
| 2032 Senior Secured Notes | Caesars Entertainment, Inc. and the 2032 Notes guarantors | First-priority collateral to the extent included, perfected and not released; value by entity unavailable | Pari (same entity, same lien) with other stated first-priority obligations | [Insufficient Information] — no current value schedule for non-guarantors; no stranded amount established | Shared first-priority collateral position is documented, but actual lien sharing, value and recoveries require current security and ICA evidence. | Provisional | [C10, C12, C13] |
| CEI senior unsecured notes | Caesars Entertainment, Inc. and subsidiary guarantors as reported | Unsecured claims against obligors; no direct lien reach established by supplied source | Insufficient Information | [Insufficient Information] — non-guarantor assets/value not allocated | Payment rank is not a substitute for entity-level reach; no recovery ranking by value is supportable. | Insufficient Information | [C13] |
| Caesars Virginia facilities | Caesars Virginia, LLC and any facility-specific subsidiary obligors | Separate CVA collateral; value and overlap with CEI collateral unknown | Structurally Subordinated — Non-Guarantor Value, only to the extent value is outside CEI guarantees | Caesars Virginia facility assets, amount not disclosed | CEI creditors do not have a reported CEI guarantee of these facilities; entity-level asset and debt analysis is needed before ranking. | Provisional | [C13] |

#### T4D.6 — Drop-down / Transfer Capacity Register

| Route | Entity Path | Enabling Provision (CP-4 ref) | Value Exposed | Severity 1–5 | Recovery/Priority Implication | Demonstrated vs Theoretical | Evidence ID |
|---|---|---|---|---:|---|---|---|
| Investment into / designation of unrestricted subsidiary | Borrower or restricted subsidiary → qualifying investment/designation → unrestricted subsidiary | CP-4 T4.3/T4C.7; Credit Agreement §§1.01, 6.04(s), (mm) | [Insufficient Information] — no current entity value or utilization schedule | 4 | Potentially moves assets beyond direct guarantor/collateral reach; no completed transfer demonstrated. | Theoretical capacity; current usage not established | [C6, C8] |
| Project financing and collateral release | Mortgaged property → project/qualified non-recourse subsidiary → project financing | CP-4 T4.3/T4C.6; Credit Agreement §§5.11, 9.18 | [Insufficient Information] — no current property-level schedule or project notice | 4 | Specified project conditions can release a mortgage and, in the stated case, related guarantee; actual use unknown. | Theoretical capacity; use not established | [C10] |
| Asset disposition to a non-Loan Party | Loan Party → permitted disposition → third party or non-Loan Party | CP-4 T4.3/T4C.7; Credit Agreement §§6.05, 9.18 | [Insufficient Information] — current asset disposition and proceeds records absent | 3 | Collateral may be released on a permitted disposition; proceeds treatment depends on the governing provision and exceptions. | Theoretical capacity; use not established | [C13] |

#### T4D.7 — Priming-Exposure Findings

| Vulnerability | Enabling Provision (CP-4 ref) | Affected Creditor Class | Demonstrated vs Theoretical | Structural Implication | Confidence | Evidence ID |
|---|---|---|---|---|---|---|
| Pari first-lien incremental dilution; not a demonstrated non-pro-rata uptier | CP-4 T4.3/T4C.6; Credit Agreement §§2.21, 6.01 | Existing CEI first-priority secured lenders and 2032 Notes | Theoretical capacity; no current incurrence or uptier established | Additional pari claims could share first-priority collateral; no evidence here establishes a non-pro-rata subordination of existing claims. | Provisional | [C3, C4, C12] |
| Non-pro-rata lender amendment/reallocation | CP-4 T4.3; Fourth Amendment §§3–4 and Credit Agreement §2.19(c) | Term B and Term B-1 lenders | Demonstrated amendment mechanics; not evidence of collateral priming | Non-consenting and allocated loans may be replaced/reallocated under the documented amendment mechanics; apply only to the affected loan classes. | Directly sourced | [C19, C20] |
| Trapdoor/drop-down priming | No current executed non-pro-rata transfer/uptier provision established | Existing first-lien and note creditors | [Insufficient Information] — executed ICA and current collateral/entity schedules absent | Do not infer a trapdoor or priming route beyond the separately described theoretical investment and pari-debt capacities. | Insufficient Information | [C25] |

#### T4D.8 — Structural Gaps Ledger

| Gap | Missing Document/Schedule/Provision | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Current entity perimeter | Current org chart, subsidiary schedule, designation notices and CP-1A entity facts | The provided schedules are incomplete or issue-date specific and do not establish present ownership/designation. | T4D.2 and all entity-level conclusions. | Obtain the current organizational chart, full subsidiary schedules and designation history. |
| Entity-level value and debt | Debt, assets and EBITDA by legal entity, including CVA and non-guarantors | Structural subordination requires the entity gap and value stranded at that entity. | T4D.5; no value-based rank or recovery access conclusion. | Obtain debt-by-entity and asset/EBITDA schedules. |
| Current collateral/perfection | Executed security documents, current collateral schedule and perfection certificates | The credit agreement definitions do not prove present attachment, perfection or value. | T4D.4–T4D.5. | Obtain executed security documents and current filing/perfection evidence. |
| Current ICA and joinders | Executed first-lien and any junior-lien ICA, amendments and representative joinders | Enforcement, turnover and intercreditor voting cannot be established from a form exhibit. | T4D.6–T4D.7 and T4F.1–T4F.5. [C25] | Obtain the executed, current agreement package. |
| Release and transfer usage | Project notices, collateral/guarantee releases, unrestricted subsidiary transfers and basket usage | Theoretical permissions do not demonstrate a completed transaction or remaining capacity. | Leakage severity, demonstrated/theoretical separation and recovery access. | Obtain post-period transaction and release logs and current basket tracker. |
| Subsequent perimeter events | Current-period and post-period guarantee/security release and designation records | No complete event schedule is supplied to establish changes after the source-document dates. | Period-end map and subsequent-event assessment. | Confirm all events through the analysis date; report each separately from Q2 balances. |

#### T4F.1 — Intercreditor Controlling Documents

| Document | Parties | Date | Governing Law | Status | Source / Locator | Evidence ID |
|---|---|---|---|---|---|---|
| First- and second-lien intercreditor agreement forms referenced in the Credit Agreement | Form references identify agents/representatives, but no current executed agreement is supplied | [Insufficient Information] — execution date unavailable | [Insufficient Information] — operative ICA not delivered | [Insufficient Information] — form/template reference only, not evidence of an executed current ICA | Credit Agreement contents list exhibits N and O as forms; no executed ICA document in delivered evidence | [C25] |

#### T4F.2 — Creditor Class Map

| Creditor Class | Rank | Security Interest | Enforcement Rights | Voting Weight | Evidence ID |
|---|---|---|---|---|---|
| CEI revolving, Term A, Term B, Term B-1 and secured notes | Stated first-priority secured obligations; exact sharing priority subject to executed intercreditor terms | First-priority liens on specified Collateral, subject to exclusions and perfection limits | [Insufficient Information] — executed ICA and current enforcement package absent | [Insufficient Information] — current lender register and class holdings absent | [C10, C12, C13, C25] |
| CEI senior unsecured notes | Senior unsecured claims at Company and reported guarantors | No secured interest established by supplied filing | Contractual unsecured remedies; exact intercreditor effect not applicable to collateral control | [Insufficient Information] — indenture voting is class-specific; current holdings not provided | [C13] |
| Caesars Virginia facility lenders | Secured claims against Caesars Virginia borrower/collateral perimeter | Q2 filing describes substantially all material CVA assets as collateral | Facility-specific remedies not delivered | [Insufficient Information] — lender holdings and facility agreement absent | [C13] |

#### T4F.3 — Enforcement Control and Standstill

| Provision | Standstill Period | Trigger | Who Controls Enforcement | Creditor Class Affected | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|
| Executed intercreditor standstill and enforcement-control provisions | [Insufficient Information] — executed ICA not provided; cannot state a drafted period or expiry mechanics | [Insufficient Information] — operative trigger unavailable | [Insufficient Information] — no executed ICA | First-lien and any junior-lien classes | Standstill, control and expiry terms cannot be inferred from an exhibit form. | Recovery-control analysis remains restricted; no recovery percentage asserted. | [C25] |

#### T4F.4 — Turnover and Release

| Provision | Turnover Obligation | Release Authority | Purchase Option | Conditions | Countervailing Evidence | Evidence ID |
|---|---|---|---|---|---|---|
| Executed intercreditor turnover/release/purchase-option provisions | [Insufficient Information] — executed ICA absent | [Insufficient Information] — ICA release authority not established; credit agreement contains separate permitted collateral releases | [Insufficient Information] — ICA purchase option not established | [Insufficient Information] — no executed clause available | Credit Agreement permits certain collateral releases, but does not establish the absent ICA’s turnover or purchase-option terms. | [C10, C25] |

#### T4F.5 — Recovery Control Assessment

| Creditor Class | Realised-Recovery Mechanic | Control Weakness | Severity | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|
| First-priority secured creditors | Stated first-priority liens and equal-rank secured obligations; actual intercreditor proceeds waterfall not delivered | [Insufficient Information] — executed ICA and current collateral package absent | Insufficient Information | Enforcement, turnover and proceeds control cannot be confirmed from the available form reference. | Do not estimate recovery; pass control mechanics to CP-3A/CP-4C when executed documents are available. | [C12, C25] |
| Unsecured creditors | Claims against Company and guarantors; no collateral recovery basis established here | Entity-level assets and structural ranking unavailable | Insufficient Information | Value at non-guarantors or structurally senior entities could affect recoveries, but current values are unknown. | Qualitative ranking remains incomplete. | [C13] |

#### T4F.6 — Intercreditor Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Executed ICA absent | Current executed first-lien and any junior-lien intercreditor agreement, amendments and joinders | A form is not an executed clause; standstill, enforcement, turnover and voting cannot be established. | T4F.1–T4F.5 are limited; no class-level recovery-control finding. [C25] | Provide the executed current ICA package and all amendments/joinders. |
| Creditor positions and voting | Current lender register, facility/class holdings and noteholder voting data | Voting weight and control may depend on holdings, class and applicable thresholds. | T4F.2–T4F.5. | Obtain current agent register and applicable class-level voting data. |
| Collateral value/perfection | Current collateral schedules, perfection certificates and valuation inputs | A lien description does not establish perfected reachable value or proceeds. | Qualitative recovery access only; downstream recovery modules need source material. | Obtain current security and perfection schedules; no recovery percentage is assigned here. |

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Covenant test thresholds and structure | [C1, C2] | Conformed Credit Agreement | 58 |
| Incremental debt and pari secured ratio mechanics | [C3, C4] | Conformed Credit Agreement | 19 |
| EBITDA adjustment and pro forma provisions | [C5] | Conformed Credit Agreement | 16 |
| Investment and unrestricted-subsidiary capacity | [C6, C8] | Conformed Credit Agreement | 54; 32 |
| Restricted payment and Cumulative Credit mechanics | [C7, C18] | Conformed Credit Agreement | 56; 14 |
| Collateral exclusions and project releases | [C9, C10] | Conformed Credit Agreement | 17; 50 |
| Notes ranking and guarantee framework | [C10, C11, C12, C13] | 2032 Notes Indenture; Q2 Form 10-Q | 10; 27; 10; 11 |
| Q2 debt basis and covenant status | [C14, C15] | Q2 2026 Form 10-Q | 9; 10 |
| Customer funding float and covenant debt exclusion | [C16, C17] | Conformed Credit Agreement; Q2 Form 10-Q | 20; 11 |
| Amendment/reallocation mechanics and later pricing terms | [C19, C20, C26] | Fourth/Fifth Amendments; Credit Agreement | 1; 1; 63 |
| Merger financing and transaction status | [C21, C22, C28] | Merger Form 8-K; Q2 Form 10-Q | 2; 5; 3 |
| Subsequent Alberta launch | [C23] | Q2 2026 Form 10-Q | 17 |
| Intercreditor evidence limitation | [C25] | Conformed Credit Agreement contents | 8 |
| Las Vegas downside operating trigger | [C27] | Q2 2026 Form 10-Q | 20 |

## Source Registry

| Source ID | Document | Authority / Type | Version / Status | Use and limitation |
|---|---|---|---|---|
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | Incremental Assumption Agreement No. 3 with conformed Credit Agreement | Rank 1; executed legal document | February 6, 2024 conformed version; referenced schedules incomplete | Governing legal formulas and capacity provisions; later delivered amendments are analyzed separately. |
| 050d12fd-6a63-4d3a-8d28-263977d76585 | Fourth Amendment to Credit Agreement | Rank 1; executed amendment | May 9, 2024 | Amendment and lender-reallocation mechanics; affected terms later amended by Fifth Amendment. |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | Fifth Amendment to Credit Agreement | Rank 1; executed amendment | November 25, 2024 | Latest delivered Term B/B-1 margin and consent/replacement terms; later changes are not established. |
| 13a99137-9563-4f67-9e21-c7e195278e82 | 2032 Senior Secured Notes Indenture | Rank 1; executed indenture | February 6, 2024 | Note covenant, guarantee, collateral, remedies and amendment provisions; supplements must be read with it. |
| fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | First Supplemental Indenture | Rank 1; executed supplement | March 1, 2024 | Adds guarantors and amends specified indenture text. |
| 79bf3e7f-a2b9-4029-ac75-70816dc58005 | Second Supplemental Indenture | Rank 1; executed supplement | August 23, 2024 | Adds guarantors; does not establish current asset values or all later changes. |
| 743e5d19-d65d-4487-8114-c0614dfc076d | Q2 2026 Form 10-Q | Rank 3 financial/covenant-status source | Quarter ended June 30, 2026; filed July 28, 2026 | Current debt, issuer-reported covenant compliance, guarantee description and subsequent-event disclosure. |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | Merger Agreement Form 8-K | SEC-filed transaction report | May 27, 2026 report; signed/filing material dated May 28, 2026 | Summary and financing-commitment statement; complete agreement schedules and commitment terms are not delivered. |

## Gaps & Conflicts

The latest delivered credit amendment is the Fifth Amendment dated November 25, 2024, which changes the Term B and Term B-1 margins; the Fourth Amendment’s earlier pricing text is not treated as operative where superseded by the later delivered amendment [C19, C20]. The conformed agreement does not establish that no later amendments exist. Its referenced First Lien and Second Lien Intercreditor Agreement exhibits are forms; no executed current ICA was delivered [C25]. Consequently, CP-4D rows dependent on executed ICA terms remain [Insufficient Information], and no standstill length, turnover obligation, release authority, purchase option or recovery percentage is inferred.

The Q2 filing reports total debt of $11,705 million book value and $11,807 million face value; CP-1 separately identifies $11,699 million as current plus long-term balance-sheet carrying debt. These are distinct bases and are not silently reconciled; canonical CP-1 carrying debt is not substituted for legal covenant debt without the governing test calculation [C14]. The issuer reports covenant compliance at June 30, 2026, but current headroom remains Not Calculable without covenant EBITDA, test details and the certificate [C15].

The legal documents contain significant basket, reclassification, pro forma and release flexibility, but present utilization and entity-level values are not supplied. No total debt, lien, RP or leakage capacity is calculated or summed. Customer deposits/deferred revenue remain operating float, not covenant Indebtedness under the cited exclusion; their liquidity implications require current-period analysis [C16, C17]. The proposed merger and its financing remain separate from Q2-period debt figures; full financing documents are a gap [C21, C22, C28].

## QA Validation

- **Identity and lineage:** PASS — issuer, module, run, reporting period, analysis date and accepted CP-0/CP-1 lineage match the supplied invocation.
- **Source gate:** PASS WITH LIMITATIONS — executed Credit Agreement and Notes Indenture are present; schedules, current certificates, executed ICA and later amendments are not fully established.
- **Workflow coverage:** PASS WITH LIMITATIONS — legal source authority, covenant features, definitions, debt capacity, leakage, collateral/guarantees, defaults/remedies, PD/LGD translation, comparison limitation, scoring, monitoring, gaps, restricted-group mapping, capacity registers and intercreditor registers are represented.
- **Register completeness:** PASS — all required CP-4, CP-4A, CP-4B and CP-4D register IDs and their declared columns are present with at least one body row each.
- **Citation and locator discipline:** PASS — citation excerpts are taken from delivered evidence lines and cited by marker; source locators are recorded in Evidence Trace and source registers. No upstream citation-register marker is used as an evidence citation.
- **Null and capacity discipline:** PASS WITH LIMITATIONS — unavailable values are identified with specific gaps; no unknown usage is treated as zero and no exact capacity or recovery amount is inferred.
- **Conflicts, periods and subsequent events:** PASS WITH LIMITATIONS — face/book/carrying debt bases and the Fourth/Fifth Amendment sequence are retained as distinct; the July 13 Alberta event is not blended into Q2 figures.
- **Confidence and status:** PASS — score 58, Low band, qa_status Restricted and committee_status Requires More Work reflect the partial source gate and unresolved material inputs.
- **Host validation:** Pending after this response. No host validator, completeness-check result, or exit status is asserted.