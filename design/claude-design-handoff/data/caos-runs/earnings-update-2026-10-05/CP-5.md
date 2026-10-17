---
module_id: "CP-5"
module_name: "EvidenceTraceValidator"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "EARNINGS_UPDATE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-5-666bf5fb347c37cf"
credit_os_route_node_id: "RN-FULL_CREDIT_32-EARNINGS_UPDATE-05-CP-5"
credit_os_invocation_sha256: "d88b5e298b1dc31777c79cc0ffc128a38e4d1cdc7ee997d05a7755dfb4b68c86"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "391239d01ae8de0a192795066295a2f1d36f6c68d683de2a4deb87dac9933ddd"
  - module_id: "CP-1"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "ea255e9e1079d8ca891fe6bddc3797a6b2c6f7acb9652d0bbc4c1ad0af39baad"
  - module_id: "CP-1B"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "60266863190da1cb52552ec7b8761bd1f363d2273ef0abd1fe8f8adfc302c823"
  - module_id: "CP-2"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "a64d240737217941f035c225e08c4a21bbd3674bfb2970b3ed035b2e870680b1"
confidence_score: 46
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, MATERIAL_TRACEABILITY_REMEDIATION, CURRENT_MARKET_AND_EXECUTED_DOCUMENT_GAPS]
validation_warnings: [UPSTREAM_HANDOFFS_RESTRICTED, SOURCE_AND_CALCULATION_LIMITATIONS_RETAINED, HOST_VALIDATION_FOLLOWS]
downstream_consumers: [CP-6, CP-6A]
---

## Audit Summary

- **Canonical filename:** `CZR_CP-5_20261002.md`.
- **Module and entity:** CP-5 EvidenceTraceValidator; Caesars Entertainment, Inc. (CZR); Q2 2026.
- **Scope:** Top 5 material credit drivers, traced through the accepted CP-0, CP-1, CP-1B and CP-2 handoffs and the delivered filings and earnings release.
- **Module status:** Ready with Limitations. The material operating and liquidity claims in scope are substantially traceable, but upstream handoffs are Restricted and one source dash is rendered as zero in CP-1. Current market evidence and complete executed financing documents are not included.
- **Overall traceability:** Ready with Remediation. The null-to-zero treatment requires correction; covenant compliance is not covenant headroom, and no current relative-value conclusion is supported.
- **Confidence:** 46 / Low. Scoring inputs: E=88, C=95, S=0.7, P=18; `clamp((0.6 × 88 + 0.4 × 95) × 0.7 − 18, 0, 100) = 46` after integer rounding. One MATERIAL and one MINOR finding are reflected; the Restricted hard cap is satisfied.
- **Committee status:** Restricted. Preserve the limitations and remediate the source-dash conversion before downstream use.

## Analysis

### Traceability conclusion

Overall, evidence traceability is Ready with Remediation. Of the Top 5 material credit drivers, 4 are directly sourced, 0 are calculated, 0 are assumption-based, 1 is an analyst inference, and 0 are weak-lineage, untraced, conflicting, or insufficient-information items. The most important provenance defect is CP-1’s conversion of a source dash to zero in its H1 2026 tax add-back row; that breaks null fidelity and can distort the structured calculation record, although it does not alter the supported operating conclusion. The principal decision limitation remains missing executed financing documents and covenant calculations: reported compliance does not establish headroom. The strongest counterevidence is Regional growth and positive H1 operating cash flow; it would strengthen the earnings view if sustained on a comparable perimeter and after capex, rent and debt service.

**Decision drivers and trace.** The Q2 release reports revenue growth of 3.0% while Adjusted EBITDA declined 3.7%, and the 10-Q reports margin contraction [C1, C2, C3]. The filing attributes Las Vegas weakness to lower visitation, occupancy and room rates; Regional growth partly reflects the Windsor consolidation and event visitation [C4, C5]. That Regional result is the strongest supported counterargument to broad operating deterioration, but the changed segment perimeter and event contribution weaken its comparability. H1 CFO remained positive at $675 million [C6], while estimated remaining-2026 debt service and lease payments are separate substantial cash demands [C7, C8]. These figures support monitoring liquidity and cash conversion; they do not establish free cash flow or covenant cushion.

**Risk transmission and monitoring.** A further decline in discretionary visitation, property occupancy or gaming hold would first pressure property revenue and contribution. If operating costs and lease obligations do not adjust at the same pace, lower earnings and cash conversion would compete with debt service, capex and customer-performance obligations, reducing liquidity and refinancing flexibility. The filing’s debt-service schedule shows higher annual obligations across 2028–30 [C9]. Monitor same-perimeter Regional results, Las Vegas operating measures, Digital hold and earnings, cash flow after capex and rent, customer-deposit balances, and current covenant calculations. No unsupported stress amount, refinancing outcome, recovery estimate or relative-value conclusion is introduced.

**Contrary evidence and what would make it win.** Regional revenue and Adjusted EBITDA increased, with management identifying Windsor, northern Nevada event visitation and investments as contributors [C5]. Positive H1 operating cash flow also provides a counterweight [C6]. This challenge would win if later periods showed sustained Regional improvement on a Windsor-consistent basis and cash generation after capex, rent and debt service. The evidence supplied here does not establish those conditions.

**Traceability limits.** CP-0, CP-1, CP-1B and CP-2 are accepted same-run handoffs with matching issuer, period and run identity; each reports Restricted status. Source citations in the handoffs were checked against the delivered evidence where cited below. CP-3 through CP-4A outputs are not included in this route’s accepted upstream set and are not inferred. No current market or ratings evidence, complete executed financing-document set, or later post-quarter update through the analysis date is delivered. CP-2 makes no current relative-value claim; the market-data absence is a limitation for any later market-dependent conclusion, not a basis for inventing one.

### Analytical appendix — complete canonical registers

#### T5B.1 — Source Register

| Source Document ID | Source Document Name | Source Quality | Period | Entity Covered | Data Supplied | Limitation | Downstream Use |
|---|---|---|---|---|---|---|---|
| 4700da60-4659-40e9-812a-9d9d3a2ef533 | CZR_Q2_2026_Earnings_Release.txt | Secondary-Unverified; issuer release | Q2 and H1 ended June 30, 2026 | Caesars Entertainment, Inc., consolidated and segments | Headline revenue and Adjusted EBITDA comparisons [C1, C2] | Issuer supplemental material; filing controls detailed financial analysis | Corroborates earnings-update claims |
| 8ed97f97-6f3e-411f-902d-955cf70fbb90 | CZR_Q2_2026_10Q.txt | Primary-Unverified; interim filing | Q2 and H1 ended June 30, 2026 | Caesars Entertainment, Inc. and consolidated subsidiaries | Margin, segments, cash flow, debt service, leases, maturities, contract liabilities and covenant status [C3-C15] | Unaudited interim filing; complete executed financing documents and covenant-headroom calculations are not provided | Principal current-period evidence |
| 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | CZR_FY2025_10K.txt | Primary-Unverified in this run; audited annual financial statements | FY2025 and comparative annual periods | Caesars Entertainment, Inc. and consolidated subsidiaries | Audited annual baseline and business-risk context | Prior-period data; does not supply current market evidence or missing Q2 calculations | Annual context only; no FY figure substituted for Q2/H1 |

**Module status:** Ready with Limitations. **Traceability scope:** Top 5. CP-0, CP-1, CP-1B and CP-2 are the accepted upstream artifacts used; each has matching CZR identity, Q2 2026 period and same-run ID. Their pre-audit QA status is Restricted. No external source use is represented. CP-5A is the absorbed phase of this CP-5 run; no separate QA artifact is required.

#### T5B.2 — Top 5 Material Credit Drivers

| Rank | Credit Driver | Originating Module | Source-Supported Basis | Why Material | Committee Relevance | Source Trace | Limitation |
|---:|---|---|---|---|---|---|---|
| 1 | Q2 revenue increased while Adjusted EBITDA and margin declined | CP-1B / CP-2 | Reported revenue growth and Adjusted EBITDA decline [C1, C2]; issuer-reported margin comparison [C3] | Lower earnings conversion reduces the operating cushion against fixed cash claims | Monitor earnings and margin durability; no leverage ratio inferred | CZR_Q2_2026_Earnings_Release.txt p.1; CZR_Q2_2026_10Q.txt p.18 [C1-C3] | Adjusted EBITDA is issuer-defined and is not a liquidity measure |
| 2 | Las Vegas weakness contrasts with partly non-comparable Regional growth | CP-1B / CP-2 | Filing describes lower Las Vegas visitation, occupancy and rates and Regional growth including Windsor and event effects [C4, C5] | Different segment trajectories affect the durability of the offset to weakness | Require comparable-period evidence before treating Regional gains as recurring | CZR_Q2_2026_10Q.txt p.20 [C4, C5] | No same-perimeter recast is supplied |
| 3 | Liquidity must absorb debt service, rent and capital needs | CP-1 / CP-2 | H1 CFO and remaining-2026 debt-service and lease estimates are separately disclosed [C6-C8] | Cash generation must meet competing operating and contractual demands | Track cash conversion after capex, rent and debt service | CZR_Q2_2026_10Q.txt p.22 [C6-C8] | No normalized FCF or runway calculation is supported |
| 4 | Annual debt-service requirements rise across the disclosed 2028–30 period | CP-2 | Filing’s annual maturity schedule [C9] | Weaker earnings or delayed refinancing could increase reliance on liquidity and market access | Monitor maturities and refinancing progress without predicting access | CZR_Q2_2026_10Q.txt p.9 [C9] | Current prices, yields and ratings evidence are absent |
| 5 | Customer deposits and deferred revenue are operating float with customer obligations | CP-1 / CP-2 | Balance rose from 492 at year-end to 545 at June 30; filing describes gaming deposits and advance payments [C12] | A funding source also represents goods, services, wagers or other customer obligations | Monitor changes as a liquidity-quality indicator; do not treat as ordinary payables | CZR_Q2_2026_10Q.txt p.11 [C12] | No refund or cash-outflow stress amount is established |

#### T5B.3 — Traceability Map

| Credit Driver / Conclusion | Originating Module | Source Evidence | Citation Present? | Source Quality | Classification | Claim Status | Confidence Level | Traceability Status |
|---|---|---|---|---|---|---|---|---|
| Revenue grew while Q2 Adjusted EBITDA and margin declined | CP-1B / CP-2 | Release reports revenue and Adjusted EBITDA comparisons; 10-Q reports margin values [C1-C3] | Yes | Primary-Unverified filing; issuer release corroborative | Directly Sourced | Supported | High | Committee-Ready |
| Las Vegas weakness and Regional growth have different drivers and comparability | CP-1B / CP-2 | Filing attributes Las Vegas declines to lower visitation, occupancy and rates; Regional increases partly to Windsor and event visitation [C4, C5] | Yes | Primary-Unverified | Directly Sourced | Supported | High | Committee-Ready |
| H1 CFO and estimated remaining-2026 debt service and rent are distinct cash measures | CP-1 / CP-2 | CFO, debt-service and lease estimates are reported separately [C6-C8] | Yes | Primary-Unverified | Analyst Inference | Partially Supported | Medium | Remediation Needed — cash available after all demands is not calculated |
| Debt-service schedule creates a refinancing monitoring point in 2028–30 | CP-2 | Annual debt maturities and service schedule [C9] | Yes | Primary-Unverified | Directly Sourced | Supported | High | Committee-Ready |
| Customer deposits/deferred revenue are funding float with performance obligations | CP-1 / CP-2 | Balance trend and contractual recognition description in 10-Q [C12] | Yes | Primary-Unverified | Directly Sourced | Supported | Medium | Committee-Ready |

#### T5B.4 — Source Lineage Register

| Statement | Source Path | Source File | Source Document ID | Page / Section | Module Section | Type | Source Quality | Notes |
|---|---|---|---|---|---|---|---|---|
| Q2 revenue and Adjusted EBITDA moved in opposite directions year over year | Delivered evidence bundle | CZR_Q2_2026_Earnings_Release.txt | 4700da60-4659-40e9-812a-9d9d3a2ef533 | 1; second-quarter results summary | CP-1B / CP-2 Analysis | Sourced | Secondary-Unverified | Reported values and percentage changes [C1, C2] |
| Q2 and H1 issuer-reported Adjusted EBITDA margins declined year over year | Delivered evidence bundle | CZR_Q2_2026_10Q.txt | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 18; results of operations | CP-1B / CP-2 Analysis | Sourced | Primary-Unverified | Source-reported ratio [C3] |
| Las Vegas segment revenue, earnings and margin declined with lower visitation and hotel measures | Delivered evidence bundle | CZR_Q2_2026_10Q.txt | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 20; Las Vegas segment | CP-1B / CP-2 Analysis | Sourced | Primary-Unverified | Management attribution is presented as source attribution [C4] |
| Regional segment increased partly due to Windsor consolidation and event visitation | Delivered evidence bundle | CZR_Q2_2026_10Q.txt | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 20; Regional segment | CP-1B / CP-2 Analysis | Sourced | Primary-Unverified | Comparability limitation retained [C5] |
| H1 operating cash flow was 675; estimated remaining-2026 debt service 425 and lease payments 687 | Delivered evidence bundle | CZR_Q2_2026_10Q.txt | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 22; liquidity and capital resources | CP-1 / CP-2 Analysis | Sourced | Primary-Unverified | Distinct measures; not combined into an FCF figure [C6-C8] |
| Annual debt maturities are concentrated in the disclosed 2028–30 schedule | Delivered evidence bundle | CZR_Q2_2026_10Q.txt | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 9; annual estimated debt service | CP-2 Analysis | Sourced | Primary-Unverified | No market-access conclusion inferred [C9] |
| Customer deposits and deferred revenue increased to 545 by June 30 | Delivered evidence bundle | CZR_Q2_2026_10Q.txt | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 11; contract and contract-related liabilities | CP-1 / CP-2 Analysis | Sourced | Primary-Unverified | Customer obligations remain attached to the balance [C12] |

#### T5B.5 — Calculation and Assumption Register

| Item | Where Used | Source Inputs / Assumption | Formula or Logic | Status | Claim Status | Confidence Level | Credit Relevance | Source Trace |
|---|---|---|---|---|---|---|---|---|
| Q2 Adjusted EBITDA margin, issuer-reported | CP-1 T4.9; CP-1B Analysis | Q2 2026 Adjusted EBITDA 920 and revenue 2,993; Q2 2025 Adjusted EBITDA 955 and revenue 2,907 | Adjusted EBITDA / revenue; filing reports 30.7% and 32.9%; CP-5 does not independently recalculate | Calculated; source-reported ratio | Supported | High | Earnings cushion and monitoring | CZR_Q2_2026_Earnings_Release.txt p.1; CZR_Q2_2026_10Q.txt p.18 [C1-C3] |
| Total debt on balance-sheet carrying-value basis at June 30, 2026 | CP-1 T4.6; debt-basis review | Current debt 114; long-term debt 11,585 [C13, C14] | Current portion + long-term carrying value = 11,699; no face-value substitution | Calculated | Supported | High | Debt basis and leverage denominator | CZR_Q2_2026_10Q.txt p.2 [C13, C14] |
| H1 2026 tax adjustment displayed as dash in source but as zero in CP-1 T4.17 | CP-1 T4.17; CP-1B T4.14 | 10-Q reconciliation displays an em dash [C16]; CP-1 presents 0 while CP-1B retains null/WARN | No numeric zero is supported by the source dash; preserve null/dash and identify the gap | Not Calculable from Provided Materials — source does not report a numeric amount | Conflicting | Medium | Calculation trace and null integrity | CZR_Q2_2026_10Q.txt p.16 [C16]; CP-1 T4.17 and CP-1B T4.14 |
| Normalized FCF, covenant headroom and liquidity runway | CP-1 / CP-2 conclusions | Required calculation inputs or agreements are incomplete in accepted handoffs | Not Calculable from Provided Materials — matched formula, inputs and/or clause-level support are absent | Not Calculable | Insufficient Information | Low | Liquidity, debt service and covenant capacity | Accepted CP-1 and CP-2 handoffs; limitations retained in T5B.8 |

#### T5B.6 — Missing Citation and Weak-Lineage Flags

| Severity | Conclusion | Issue | Classification | Why It Matters | Required Remediation | Affected Output / Export Record |
|---|---|---|---|---|---|---|
| Material | CP-1 T4.17 H1 2026 tax adjustment | The source displays a dash, while CP-1 encodes zero; CP-1B preserves a null and records a WARN. A dash is not evidence of a numeric zero. | Conflicting | Converting null to zero breaks source fidelity and may affect downstream calculation or ingestion. | Replace the zero with the source dash/null, retain the row, and reconcile the CP-1 and CP-1B representations. | CP-1 T4.17; CP-1B T4.14; CP-5 issue CP5-001 |

#### T5B.7 — Auditability Assessment

| Auditability Dimension | Assessment | Evidence | Risk Mechanic | Credit Implication | Remediation Needed |
|---|---|---|---|---|---|
| Source coverage | Ready with Remediation | Three delivered source documents and four accepted same-run upstream handoffs are identified in T5B.1 and T5.1; current market and complete executed financing documents are absent. | Missing market or executed-document evidence limits market-dependent conclusions and clause-level covenant verification. | Earnings and operating claims remain traceable; committee use remains restricted for conclusions requiring those inputs. | Obtain current market/rating sources and executed financing documents only where the decision requires them. |
| Citation completeness | Ready with Remediation | Top five drivers have source locators and citations; CP-1’s source-dash/zero mismatch is recorded in T5B.6. | A transformed value can be mistaken for source fact if the null marker is lost. | Correct the affected structured record before downstream reliance. | Remediate CP5-001 and preserve dash/null consistently. |
| Calculation traceability | Ready with Remediation | Reported margin and carrying-value debt basis are traceable; CP-1’s dash-to-zero conversion is not supported. | Unsupported numeric conversion can contaminate a calculation input. | Leverage, FCF, runway and headroom remain uncalculated; no affected credit ratio is asserted. | Correct CP-1 and retain the source basis and formula for calculated measures. |
| Assumption transparency | Committee-Ready | Upstream handoffs distinguish reported measures, interpretations and unavailable calculations; Regional comparability is qualified [C5]. | Unlabelled assumptions could overstate the durability of earnings or liquidity. | Current synthesis is bounded; no forecast, stress value or headroom is inferred. | No additional action beyond preserving limitations. |
| Markdown/export artifact integrity | Ready with Remediation | Accepted handoff identities, required headings and register content are present in the delivered text; host validation is pending. | A handoff defect could impair downstream grounding even where claims are sourced. | Treat the artifact as pending host validation; do not claim validator output. | Host validation and register completeness checks follow this answer. |

#### T5B.8 — Gaps Ledger

| Gap ID | Gap | Missing Evidence / Citation | Why It Matters | Impact on Output | Consequence for Confidence | Required Follow-Up Source |
|---|---|---|---|---|---|---|
| CP-5-GAP-001 | Source dash rendered as zero in CP-1 T4.17 | Numeric amount is absent; source shows a dash [C16] | Null-to-zero conversion can distort an input and breaks traceability. | CP-1 T4.17 and CP-1B T4.14; downstream calculation records | High | Corrected CP-1 handoff preserving the source dash/null and corresponding CP-1B reconciliation |
| CP-5-GAP-002 | Covenant headroom and detailed legal terms are not calculated or independently verified | Complete executed financing documents, amendments, schedules and supporting covenant calculations are not in the delivered pack; filing reports compliance [C15] | Compliance does not measure cushion; missing definitions and inputs prevent headroom calculation. | CP-2 credit view and any covenant-capacity conclusion | High | Current executed agreements and amendments plus issuer covenant calculations and required financial inputs |
| CP-5-GAP-003 | Current market and ratings evidence is absent | Current security price/yield and current rating-agency evidence are not supplied | Market access and relative value cannot be assessed from issuer financial filings alone. | Any later market-dependent or relative-value conclusion | Medium | Dated, instrument-specific market evidence and current rating-agency material |
| CP-5-GAP-004 | Post-quarter status through the analysis date is not established by the delivered source set | Current issuer update or filing after the Q2 10-Q is not delivered | Later transaction or operating events could affect monitoring, but must not be blended into Q2. | Subsequent-event discussion and monitoring | Medium | Current issuer filing or update with event date and source locator |

Overall gap priority: CP-5-GAP-001 is the immediate provenance remediation; CP-5-GAP-002 is the most important substantive evidence gap for covenant capacity. Missing sources are not filled by inference.

#### T5.1 — Input Module Register

| Module | Handoff canonical `.md` / run_id | Scope | Source Quality | Envelope / Headings Status | QA Status | Notes |
|---|---|---|---|---|---|---|
| CP-0 | CZR_CP-0_20261002.md / COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b | Q2 2026 source readiness | Primary filings plus issuer release; visual extraction limitations disclosed | Envelope and six canonical H2 headings present in accepted handoff text; host validation not independently asserted | Restricted | Accepted CP-0 sha matches host lineage; market/rating and full executed financing documents absent |
| CP-1 | CZR_CP-1_20261002.md / COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b | Q2/H1 2026 financial foundation | Primary filings; derived calculations and reconciliations incomplete | Envelope and six canonical H2 headings present in accepted handoff text; host validation not independently asserted | Restricted | T4.17 converts a source dash to zero; derived KPI and reconciliation gaps disclosed |
| CP-1B | CZR_CP-1B_20261002.md / COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b | Q2/H1 2026 earnings delta | Primary filings and corroborative issuer release | Envelope and six canonical H2 headings present in accepted handoff text; host validation not independently asserted | Restricted | Preserves dash as null in its validation row and discloses calculation/perimeter limits |
| CP-2 | CZR_CP-2_20261002.md / COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b | Q2 2026 fundamental credit synthesis | Primary filings; qualitative synthesis with disclosed calculation and market-data gaps | Envelope and six canonical H2 headings present in accepted handoff text; host validation not independently asserted | Restricted | No FCF, covenant headroom, formal rating or relative-value conclusion is asserted |

**Module status:** Ready with Limitations. CP-5 evidence tracing and the absorbed research-integrity phase are completed in this single handoff. The source package is not sufficient to resolve every market, covenant or post-quarter question.

#### T5.2 — Citation and Evidence Support Audit

| Severity | Module | Claim / Section | Evidence Status | Issue | Required Fix | Clearance Impact |
|---|---|---|---|---|---|---|
| MATERIAL | CP-1 | T4.17 H1 2026 income-tax reconciliation row | Conflicting | `CZR_Q2_2026_10Q.txt` displays a dash, but CP-1 T4.17 records zero; CP-1B T4.14 preserves null. This is a source-to-handoff inconsistency and a null-integrity defect. [C16] | Preserve dash/null in CP-1 and reconcile the row with CP-1B; do not infer zero. | Requires Source Reconciliation |

#### T5.3 — Math / Logic / Definition Audit

| Severity | Module | Metric / Logic Issue | Formula / Definition Issue | Source Conflict | Required Fix | Clearance Impact |
|---|---|---|---|---|---|---|
| MATERIAL | CP-1 | H1 2026 tax adjustment source dash represented as numeric zero | No source amount is reported; zero is not a valid substitution for a null value. | `CZR_Q2_2026_10Q.txt` p.16 shows a dash; CP-1 T4.17 shows 0; CP-1B T4.14 retains null [C16] | Correct the value to dash/null, keep the row, and reconcile upstream records under CP5-001. | Requires Calculation Rebuild |

#### T5.4 — Legal / Structural Claim Audit

| Severity | Module | Legal / Structural Claim | Required Legal Source | Evidence Gap | Required Fix | Legal Review Dependency |
|---|---|---|---|---|---|---|
| MINOR | CP-2 | Reported covenant terms and compliance; no headroom or legal-capacity conclusion made | Current executed agreements, amendments and covenant calculations for any clause-level or headroom conclusion | The 10-Q reports compliance but the delivered pack lacks the complete executed financing-document set and calculated headroom [C15] | Retain the explicit limitation; do not infer capacity or creditor rights. | Legal review required only if a later output makes a clause-level or capacity claim |

#### T5.5 — Relative Value / Market Claim Audit

| Severity | Module | Market / RV Claim | Missing Datapoint | Evidence Gap | Required Fix | Committee Impact |
|---|---|---|---|---|---|---|
| MINOR | CP-2 | No current relative-value, price, yield or spread conclusion identified | Current instrument-specific price/yield and comparable set are not provided | No market source is included; upstream handoffs explicitly limit market-dependent analysis | Do not add an RV label; obtain dated instrument-specific market evidence before making a current RV claim. | No current RV conclusion may be used; issuer-source credit trace remains usable with limitations |

#### T5.6 — Cross-Module Consistency and Version-Control Audit

| Severity | Affected Modules | Data / Claim Conflict | Version Issue | Required Fix | Downstream Impact |
|---|---|---|---|---|---|
| MINOR | CP-0, CP-1, CP-1B, CP-2 | Debt basis is explicitly distinguished: balance-sheet carrying value is used for canonical debt, while face/book debt-note figures are retained separately. No material contradiction was identified. | Same run and period; accepted artifact hashes match host lineage. | Preserve carrying-value basis and stated distinction; no silent reconciliation. | No additional downstream correction; CP-1 null-to-zero defect is tracked separately as CP5-001. |

#### T5.7 — Duplication / Materiality / Committee-Readiness Audit

| Severity | Module | Issue Type | Description | Required Fix | Committee Impact |
|---|---|---|---|---|---|
| MINOR | CP-2 | Duplicative / Immaterial Content | Liquidity demands, absent FCF/headroom and the limitation that Adjusted EBITDA is not cash flow recur in several analysis subsections. The repeated caveats do not change the conclusion but add avoidable reading burden. | Consolidate repeated caveats while retaining the key limitation and source trace once in the relevant analysis section. | Minor clarity improvement; no change to credit conclusion or current restricted use |

#### T5.8 — Handoff Envelope and Evidence Trace Audit

| Severity | Module | Handoff Component | Defect | Required Fix | Downstream Handoff Impact |
|---|---|---|---|---|---|
| MINOR | CP-0, CP-1, CP-1B, CP-2 | Envelope, headings and evidence trace | Accepted handoff text contains identity fields, the six canonical H2 headings and source/evidence sections; hashes, run and period align. This is a content self-review only, not a host validator result. | Preserve exact lineage and source locators; host validation follows this answer. | No additional defect identified; host validation remains pending |

#### T5.9 — Consolidated Issue Log

| Issue ID | Severity | Module | Issue Type | Description | Required Fix | Clearance Impact | Status |
|---|---|---|---|---|---|---|---|
| CP5-001 | MATERIAL | CP-1 | Evidence Trace Defect | CP-1 T4.17 renders the 10-Q source dash as zero while CP-1B retains null; this breaks null integrity and can distort downstream calculation inputs. [C16] | Replace zero with dash/null, retain the row and reconcile CP-1 and CP-1B representations. | Requires Source Reconciliation | Open |
| CP5-002 | MINOR | CP-2 | Duplicative / Immaterial Content | Repeated liquidity and calculation limitations add reading burden but do not change the credit conclusion. | Consolidate repeated caveats while preserving material limitations and source traces. | Formatting / Hygiene Only | Open |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| Q2 Adjusted EBITDA year-over-year comparison | [C1] | CZR_Q2_2026_Earnings_Release.txt | 1 |
| Q2 revenue year-over-year comparison | [C2] | CZR_Q2_2026_Earnings_Release.txt | 1 |
| Q2 and H1 Adjusted EBITDA margins | [C3] | CZR_Q2_2026_10Q.txt | 18 |
| Las Vegas operating decline and management attribution | [C4] | CZR_Q2_2026_10Q.txt | 20 |
| Regional growth drivers and comparability limitation | [C5] | CZR_Q2_2026_10Q.txt | 20 |
| H1 operating cash flow | [C6] | CZR_Q2_2026_10Q.txt | 22 |
| Estimated remaining-2026 debt service | [C7] | CZR_Q2_2026_10Q.txt | 22 |
| Estimated VICI and GLPI lease payments | [C8] | CZR_Q2_2026_10Q.txt | 22 |
| Annual debt maturities and service schedule | [C9] | CZR_Q2_2026_10Q.txt | 9 |
| Cash and cash equivalents | [C10] | CZR_Q2_2026_10Q.txt | 2 |
| CEI revolver capacity net of outstanding balance | [C11] | CZR_Q2_2026_10Q.txt | 22 |
| Customer deposits and other deferred revenue balances | [C12] | CZR_Q2_2026_10Q.txt | 11 |
| Current portion of long-term debt | [C13] | CZR_Q2_2026_10Q.txt | 2 |
| Long-term debt carrying value | [C14] | CZR_Q2_2026_10Q.txt | 2 |
| Reported covenant compliance, not headroom | [C15] | CZR_Q2_2026_10Q.txt | 10 |
| Source dash for H1 tax adjustment | [C16] | CZR_Q2_2026_10Q.txt | 16 |

## Source Registry

The complete source-document inventory and its limitations are in T5B.1. The accepted same-run upstream handoffs are listed in T5.1; the four artifact hashes match the host-owned upstream lineage. CP-0, CP-1, CP-1B and CP-2 each report Restricted QA status. Evidence in this handoff is cited directly to the delivered source material; upstream citation-register text is not itself treated as source evidence. No web, connector or external retrieval was used.

## Gaps & Conflicts

- **CP5-001 / CP-5-GAP-001:** CP-1 converts a source dash into zero in T4.17; CP-1B preserves null. The source dash is directly visible in `CZR_Q2_2026_10Q.txt` [C16]. Correct and reconcile before downstream use.
- **Debt and covenant:** The filing reports covenant compliance [C15], but no calculated covenant headroom is supported by the delivered materials. Detailed clause-level conclusions require current executed documents and calculation inputs.
- **Liquidity and refinancing:** Cash, debt service, lease payments and debt maturities are separately reported [C6-C11]. They do not supply a normalized FCF, runway, current market-access or refinancing-capacity calculation.
- **Post-quarter evidence:** The accepted analytical handoffs identify a later Alberta launch but do not establish developments through the analysis date. Keep subsequent events separate from Q2 and obtain a current issuer update where required.
- **Route scope:** CP-3 through CP-4A artifacts are not part of the accepted upstream set for this run; no conclusions from those modules are inferred.

No source conflict is silently reconciled. The strongest supported contrary evidence to the earnings concern remains Regional growth and positive H1 operating cash flow [C5, C6]; its durability is unresolved without comparable subsequent results and cash conversion after fixed claims.

## QA Validation

| Check | Result | Notes |
|---|---|---|
| Identity, issuer, period and upstream lineage | Self-review complete | CZR, CP-5, Q2 2026 and run identity match the host-owned front matter; CP-0, CP-1, CP-1B and CP-2 hashes are copied exactly. |
| Required headings and order | Self-review complete | The six required H2 headings appear once and in the required order. |
| Required registers and columns | Self-review complete | T5B.1-T5B.8 and T5.1-T5.9 are present with declared columns and at least one body row each. |
| Citation and locator discipline | Self-review complete | Every citation marker maps to one citation entry; matched text is drawn from the delivered evidence and locators are in the appendix/Evidence Trace. |
| Calculation and definition review | Restricted | Carrying-value debt basis is retained. CP-1’s dash-to-zero defect is recorded as CP5-001; FCF, runway and covenant headroom remain unavailable. |
| QA findings and clearance | Restricted | One MATERIAL and one MINOR open issue; no CRITICAL issue identified. Committee use is Restricted pending disclosed remediation. |
| Confidence score | Self-assessed | 46 / Low; E=88, C=95, S=0.7 and P=18; one MATERIAL and one MINOR unique finding. |
| Host validation | Pending | Host validation and completeness checks follow this answer. No host validator output, exit status or finding is asserted. |

**Run status:** Ready with Limitations. **Confidence:** 46 / Low. **QA status:** Restricted. **Host validation:** follows this answer.