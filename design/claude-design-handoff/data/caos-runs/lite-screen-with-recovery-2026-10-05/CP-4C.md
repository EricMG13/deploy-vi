---
module_id: "CP-4C"
module_name: "RestructuringScenario"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_FULL_CREDIT_SCREEN"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-4C-890a3dcec5d0ef7a"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_FULL_CREDIT_SCREEN-08-CP-4C"
credit_os_invocation_sha256: "f6945e05817bdd1844c1766652ac5cd73eec593f42caaf3c7c11848c82dc238a"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "dcb45fd922bd40cf339a42308e91a3fac8f6e23b9f198f147d86c85f73a15eeb"
  - module_id: "CP-L10"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "1b3412810ea6d286e8dd1b78eaea47c62bfa80734d5ca52486c3d5933abc0d12"
  - module_id: "CP-2A"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "beb161bbff621f35a8a07b16d0c96d46164a1a2dd72b4e9ba583ed0134f6bf54"
  - module_id: "CP-3C"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "f3dd0f99b859c58e4dff9c6a1642ccd989cb5ffaf5896a8dd9de7f41c8d7294b"
confidence_score: 49
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "LITE_FULL_UPGRADE_REQUIRED", "NO_DOCUMENTED_DISTRESS_GATE", "CURRENT_CLAIMS_AND_VALUE_NOT_RECONCILED"]
validation_warnings: ["NO_DISTRESS_GATE_DOCUMENTED", "LITE_FULL_UPGRADE_REQUIRED", "CURRENT_POST_Q2_TRANSACTION_STATUS_NOT_ESTABLISHED"]
downstream_consumers: ["CP-6", "CP-6E", "CP-5", "CP-5A"]
---

## Audit Summary

- **Canonical handoff:** `CZR_CP-4C_20261002.md`.
- **Run status:** Not Applicable — no documented distress gate is established by the evidence delivered for this run. No restructuring scenario is constructed.
- **Decision scope:** SCREENING_ONLY under `LITE_CREDIT_22`. Accepted upstream handoffs inform scope and limitations only; they are not treated as evidence or cited as such.
- **Confidence:** 49 — Low. Three material facts have direct documentary support and three material decision inputs remain insufficiently evidenced. Evidence quality E=50, required-field coverage C=100, source-gate multiplier S=0.7, QA penalty P=0; `(0.6 × 50 + 0.4 × 100) × 0.7 = 49`.
- **Disposition:** Restricted. The missing distress evidence, current claims and valuation inputs limit the conclusion; the LITE route also does not supply the full underwriting inputs this module requires.
- **Required next step:** Obtain current, source-supported evidence of a named distress trigger and a reconciled claims/value package. A new, user-confirmed, linked `FULL_CREDIT_32` run is required for full underwriting; this run remains LITE and screening-only.

## Analysis

### Restructuring view

Not Applicable: the delivered evidence does not document a qualifying distress trigger, so no restructuring path, valuation, waterfall, fulcrum or recovery is constructed. The May 27, 2026 Form 8-K records entry into a merger agreement and closing conditions; that transaction disclosure is not itself evidence of missed payment, failed refinancing, distressed exchange, covenant or enforcement escalation, adviser engagement or a filing. [C1, C2] The supplied 6.500% notes indenture documents a senior secured instrument and states New York governing law, but does not establish a current claims schedule, current collateral/perfection map or enterprise-value inputs. [C4, C5, C6] This source-bounded gate result is not a conclusion that distress cannot arise. Current payment/refinancing, covenant and restructuring-status evidence would be required before reassessment.

The strongest contrary consideration is that the transaction disclosure describes a conditional merger with dated end-date provisions, and the current post-Q2 transaction status is not established in the materials delivered here. [C2, C3] That uncertainty warrants monitoring, but does not meet the distress gate. If later evidence documents payment risk, a failed refinancing, an enforcement event or restructuring engagement, the gate and scenario work should be revisited. No assumption is made about transaction completion, issuer solvency, a court process or creditor treatment.

The required downside chain cannot be completed without an evidenced initiating distress condition. No first operational break, resulting cash-flow transmission, liquidity consequence or restructuring trigger can be supported from the delivered evidence; assigning a date, threshold, enterprise value or recovery would be unsupported. The 2024 note documents are not a current, complete legal package, and the evidence does not include a current, reconciled balance sheet of claims, current forecast or operating valuation basis. These gaps are carried below rather than converted into zero values or a hypothetical case.

### Analytical appendix — complete canonical registers

#### T4E.1 — Distress and jurisdiction gate

| trigger | evidence/date | affected entity/instrument | jurisdiction | status | limitation |
|---|---|---|---|---|---|
| Missed or likely missed payment, failed refinancing, distressed exchange/LME escalation, covenant or enforcement event, adviser engagement, filing, creditor group formation, or equivalent named trigger | No qualifying trigger is documented in the delivered evidence. The May 27, 2026 filing documents merger-agreement entry and closing conditions, not a distress event. [C1, C2] | Caesars Entertainment, Inc.; no restructuring obligor or instrument scope established | The filing identifies Caesars Entertainment, Inc. as a Delaware corporation; the supplied 2032 notes indenture states New York governing law. Case venue, proceedings, obligors and cross-border recognition issues are not established. [C5] | Not Applicable — documented distress gate not met | [Insufficient Information] — current payment/default, refinancing, covenant/enforcement, adviser and post-Q2 event evidence is not included in the delivered source materials. This is not evidence that no trigger exists. |

#### T4E.2 — Claims register

| class/claim ID | obligor | principal/accrued/PIK | currency | security/guarantee | priority | disputed/contingent | evidence |
|---|---|---|---|---|---|---|---|
| 6.500% Senior Secured Notes due 2032 — documented issue; not a current allowed-claim balance | Caesars Entertainment, Inc.; subsidiary guarantors named in the indenture family | Initial issuance principal: $1,500 million. Current principal, accrued interest and PIK: [Insufficient Information] — no current claims balance is delivered; the original issuance amount is not treated as current outstanding principal. [C6] | USD | Indenture describes senior secured obligations and security interests, subject to the security documents and intercreditor terms; current collateral, guarantee reach and perfection are not established. [C4] | Documentary terms describe secured claims; current entity-level waterfall and relative priority are not locked. | [Insufficient Information] — current allowed, disputed or contingent claim amounts are not delivered. | Base indenture and supplemental-document family are delivered; no current claims reconciliation or current security/perfection evidence is provided. [C4, C8, C9] |
| All other debt, leases, accrued/administrative, employee, tax, intercompany, guarantee and contingent claims; plus any new-money/DIP claim | [Insufficient Information] — current obligor and entity-by-entity claims schedule not delivered | [Insufficient Information] — current principal, accrued interest, PIK and other claim amounts not delivered | [Insufficient Information] — current claim currencies not reconciled | [Insufficient Information] — current guarantees, collateral reach, lease and intercreditor documents not reconciled | [Insufficient Information] — current legal priority and entity waterfall not established | [Insufficient Information] — disputed and contingent amounts not inventoried | No current claims register, balance-sheet claims reconciliation or new-money proposal is included in delivered evidence. No claim is presumed zero. |

#### T4E.3 — Enterprise-value assumptions

| scenario | valuation date | metric/cash flow | multiple/discount | EV | source/judgment IDs | limitation |
|---|---|---|---|---|---|---|
| Not Applicable — low/base/high cases not constructed because the distress gate is not met | Not Applicable — no scenario valuation date established | Not Applicable — operating metric, cash flow and valuation perimeter not locked | Not Applicable — no multiple or discount-rate assumption made | — | No valuation source or judgment ID created | [Insufficient Information] — current operating forecast, reconciled claims, valuation perimeter and sourced low/base/high assumptions are absent; no numeric EV is inferred. |

#### T4E.4 — Restructuring path matrix

| path | process/jurisdiction | consent/vote | new money | class treatment | milestones | blockers | probability class |
|---|---|---|---|---|---|---|---|
| Not Applicable — no restructuring route selected | Not Applicable — no case, proceeding or jurisdiction-specific process established | Not Applicable — no class voting or consent assumptions made | Not Applicable — no financing need or DIP/new-money proposal established | Not Applicable — claims are not locked and no treatment is modeled | No restructuring milestones established; see merger-status event in T4E.9, which is not a restructuring path. [C3] | No documented distress trigger; current claims, operative documents, consent evidence and liquidity/forecast inputs are missing | insufficient_information |

#### T4E.5 — Priority and waterfall

| scenario | entity | available value | priority claim | allocation | residual | legal evidence ID |
|---|---|---|---|---|---|---|
| Not Applicable — no waterfall constructed | Not Applicable — restructuring entity perimeter not established | — | — | Not Applicable — no claim ranking or allocation calculated | — | [Insufficient Information] — current entity/guarantee map, reconciled claims, valuation and controlling current priority/intercreditor evidence are not delivered. See G-3. |

#### T4E.6 — Fulcrum range

| scenario/EV range | last covered class | first impaired class | fulcrum class/range | uncertainty |
|---|---|---|---|---|
| Not Applicable — no low/base/high EV range | Not Applicable — no waterfall | Not Applicable — no waterfall | Not Applicable — no fulcrum determined | No documented distress gate, current claims reconciliation, supported enterprise value or current legal priority lock; any class-specific conclusion would be unsupported. |

#### T4E.7 — Recovery by class

| scenario | class/instrument | allowed claim | cash/debt/equity/warrant value | total recovery | timing | currency |
|---|---|---|---|---|---|---|
| Not Applicable — no recovery scenario | 6.500% Senior Secured Notes due 2032 and other potential classes not modeled | [Insufficient Information] — current allowed claim balance, accrued amounts and claim treatment not established | Not Applicable — no cash, reinstated debt, new debt, equity or warrant allocation calculated | Not Applicable — no recovery percentage or amount produced | Not Applicable — no process timetable established | USD is stated in the historic note documentation; class-by-class current claim currency and recovery basis are not reconciled. [C6] |

#### T4E.8 — Value-transfer and intercreditor risks

| mechanism | affected classes | required capacity/consent | evidence | possible outcome |
|---|---|---|---|---|
| No transaction-specific priming, asset transfer, exchange, release, or intercreditor action assessed; no distress path established | [Insufficient Information] — affected current classes and holder groups not mapped | [Insufficient Information] — current capacity, basket usage, intercreditor arrangements, class holdings and consent thresholds not established | The supplied indenture makes security subject to security-document and intercreditor terms; it does not establish a current restructuring transaction or current capacity. [C4] | Not Applicable — no value transfer or creditor outcome inferred. Current legal documents and transaction-specific facts are required before assessing possible outcomes. |

#### T4E.9 — Catalysts, timeline and handoff

| event/milestone | earliest/latest timing | evidence | consequence | downstream module |
|---|---|---|---|---|
| Merger initial end date and conditional extensions — transaction-status monitoring only, not a restructuring catalyst | Initial end date May 27, 2027; conditional extensions to August 27, 2027 and November 27, 2027, as stated in the filing. [C3] | Filed merger-agreement summary; current post-Q2 status is not established in the delivered evidence. [C2, C3] | A later status disclosure could change transaction and ownership context. It does not establish distress, a financing failure or a restructuring path. | CP-6; CP-6E — carry as a dated, conditional transaction-status item; do not treat it as a restructuring prediction. |
| Reassessment on receipt of a documented distress trigger and current claims/value package | Timing not available — no dated delivery or restructuring milestone established | No such source or dated milestone is included in the delivered evidence | Would permit the distress gate and, if passed, claims lock, path comparison, valuation, waterfall, fulcrum and recovery work; until then no scenario is produced. | CP-4C linked FULL_CREDIT_32 run, subject to new user confirmation; CP-5/CP-5A for subsequent review |

#### T4E.10 — Gaps and conflicts

| claim/legal/value/process gap | affected scenario/class | impact | required evidence |
|---|---|---|---|
| No documented distress trigger in delivered materials; current event coverage is incomplete and no current post-Q2 restructuring-status evidence is supplied. | All restructuring scenarios and classes | Gate remains Not Applicable on the delivered evidence; no restructuring case, path, fulcrum or recovery can be responsibly stated. | Current issuer or creditor evidence of payment/default risk, failed refinancing, distressed exchange/LME escalation, covenant/enforcement event, adviser engagement, creditor group formation, filing or equivalent trigger; dated and tied to affected obligor/instrument. |
| Current claims, cash, liquidity, forecasts, leases, administrative claims, accrued/PIK amounts and new-money needs are not reconciled. | All claims, EV cases, waterfall and class recoveries | Prevents claims lock, net-debt/priority deductions, low/base/high enterprise valuation and recovery calculation; missing amounts remain unknown, not zero. | Current filed financial statements and debt/lease schedules, claim and obligor detail, accrued/PIK and contingent claim data, forecast cases and any administrative/new-money estimates with source locators. |
| Current operative credit, lease, entity/guarantee, collateral and intercreditor package is incomplete; delivered credit agreement is a conformed 2024 version and the 2032 indenture family does not establish current perfection or current usage. [C7, C8, C9] | Path capacity, consent/vote, priority, priming/leakage and recovery by class | No current legal capacity, restructuring process right, collateral value, guarantee reach or legal priority conclusion can be made. | Current executed financing, lease, guarantee, security and intercreditor documents; current entity/obligor map; collateral/perfection records; usage/compliance certificates; and transaction-specific consent and holder evidence. |
| Valuation and process inputs needed by the FULL method are not provided by this LITE screening route. | All low/base/high valuations, paths, fulcrum and recoveries | LITE screening does not complete the FULL underwriting method; unsupported forecasts, legal conclusions and valuations are not constructed. | User-confirmed linked `FULL_CREDIT_32` run with required FULL underwriting sources and validated predecessor work. |
| Material evidence questions remain unresolved and no CP-DR research brief is delivered with this module. | Distress gate, current claims, current documents and transaction status | No research request is made; unresolved questions remain limitations and confidence is reduced. | Supply the missing factual evidence. If a research brief is later provided, follow its bounded request and adoption controls; do not create a self-dependency. |

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Merger agreement entry described in the filed summary | [C1] | Caesars Entertainment, Inc. Form 8-K | 1 |
| Merger closing conditions are stated in the filed summary | [C2] | Caesars Entertainment, Inc. Form 8-K | 2 |
| Merger end date and conditional extensions | [C3] | Caesars Entertainment, Inc. Form 8-K | 2 |
| 2032 notes are described as senior secured obligations | [C4] | 6.500% Senior Secured Notes due 2032 Indenture | 43 |
| Indenture security interests are subject to security documents and intercreditor terms | [C5] | 6.500% Senior Secured Notes due 2032 Indenture | 33 |
| Indenture governing-law statement | [C6] | 6.500% Senior Secured Notes due 2032 Indenture | 36 |
| Historic initial principal amount of 2032 secured notes; not current outstanding principal | [C7] | 6.500% Senior Secured Notes due 2032 Indenture | 3 |
| Supplied credit-agreement conformed version and amendments identified on its cover | [C8] | Incremental Assumption Agreement No. 3 and conformed credit agreement | 4 |
| First 2032 notes supplemental indenture is dated March 1, 2024 | [C9] | First Supplemental Indenture | 1 |
| Second 2032 notes supplemental indenture is dated August 23, 2024 | [C10] | Second Supplemental Indenture | 1 |

## Source Registry

| Source ID | Document | Use | Limitation |
|---|---|---|---|
| 27f98f2d-64b4-4d3a-87f0-6946d3cb8c01 | Caesars Entertainment, Inc. Form 8-K, merger-agreement summary | Confirms merger-agreement entry, stated closing conditions and dated end-date terms. [C1, C2, C3] | Summary is not evidence of current post-Q2 transaction status or a distress trigger. |
| 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | 6.500% Senior Secured Notes due 2032 Indenture | Documents the 2032 secured-note instrument, historic initial issuance amount, security-document relationship and governing-law text. [C4, C5, C6, C7] | Historic issue terms do not establish current outstanding claims, current perfection, complete current entity/guarantee coverage or a current restructuring waterfall. |
| 42064519-b433-435a-82c5-c1cabe537ac7 | First Supplemental Indenture to 2032 secured-note indenture | Identifies a dated supplement in the delivered 2032 notes document family. [C9] | Does not establish current claims balances, current collateral perfection or a complete current operative legal package. |
| 6061f8bd-230a-4786-b679-b6acd966c841 | Second Supplemental Indenture to 2032 secured-note indenture | Identifies a dated supplement and schedule of new guarantors in the delivered 2032 notes document family. [C10] | Does not establish current guarantee reach or a complete current entity/perfection map. |
| b24b47d6-6bfd-4248-b660-e867409dd303 | Incremental Assumption Agreement No. 3 and conformed credit agreement | Identifies the conformed credit-agreement version and amendment history supplied. [C8] | Conformed source is dated 2024; current operative amendments, current capacity usage and current calculations are not established. |

## Gaps & Conflicts

The run is Not Applicable because no documented distress gate is established by the evidence delivered here; this finding is limited to the delivered source set, not a claim that no distress exists. The 8-K documents a conditional transaction, but the evidence does not establish current transaction status after the filing date. [C2, C3] The historic $1,500 million note issuance is not substituted for current outstanding principal. [C7] No current claims reconciliation, operating forecast, EV basis, priority waterfall or class recovery is available, so no numeric scenario is produced. The supplied LITE route cannot supply the FULL inputs needed to infer these items. A current source pack, documented distress trigger and user-confirmed linked FULL_CREDIT_32 run are required to reconsider the question.

## QA Validation

| Check | Status | Record |
|---|---|---|
| Distress gate and issuer identity | Restricted | Issuer identity is matched to the delivered issuer filing. No qualifying distress trigger is documented in the delivered evidence; the gate is recorded Not Applicable, not assumed passed. |
| Jurisdiction and controlling-document scope | Restricted | Delaware incorporation and New York governing-law text are recorded only as document facts. No case-specific venue, process, cross-border recognition or legal conclusion is made. |
| Claims identity and reconciliation | Restricted | Historic note issuance is distinguished from current outstanding claims. Current claims, accruals, PIK, guarantees, leases and contingent claims are not reconciled. |
| Double counting, intercompany and guarantee treatment | Restricted | No waterfall or recovery calculation is performed; no guarantee or claim is counted at multiple entities. Current entity and guarantee evidence is required. |
| Valuation basis and scenario independence | Restricted | No low/base/high operating metric, multiple, discount rate, EV or scenario is constructed because the gate and valuation inputs are missing. |
| Priority, allocation and waterfall | Restricted | No priority waterfall is run. The supplied indenture describes documentary security terms subject to other documents, but current priority and collateral status are not locked. |
| Path, consent and new-money assumptions | Restricted | No restructuring path, consent threshold application, new-money/DIP amount, probability or process outcome is inferred. |
| Currency and recovery presentation | Restricted | No recovery amounts or percentages are reported; no unsupported numeric value or zero is substituted for missing data. |
| Source locators and citations | Self-check complete | Citation excerpts are from the delivered evidence and each marker is listed in the Evidence Trace. Raw locators remain in appendix/register material. |
| LITE boundary and upgrade requirement | Restricted | Screening-only scope is preserved. Missing FULL inputs are limitations, not inferred; a new, user-confirmed linked FULL_CREDIT_32 run is recommended. |
| Confidence and QA status | Restricted | Confidence 49 / Low; qa_status Restricted reflects missing gate evidence and LITE/source limitations. Committee status remains Restricted under SCREENING_ONLY scope. |
| Host validation and completeness check | Pending host processing | Host vendor validation and completeness checks follow this answer. No host output, result, exit status or findings are claimed. |