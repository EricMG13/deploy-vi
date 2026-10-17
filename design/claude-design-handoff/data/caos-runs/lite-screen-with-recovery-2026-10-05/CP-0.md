---
module_id: "CP-0"
module_name: "SourceReadiness"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_FULL_CREDIT_SCREEN"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-0-5caf73339d976728"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_FULL_CREDIT_SCREEN-01-CP-0"
credit_os_invocation_sha256: "afe410ed2f4c98776ab0dd8ab3149e4233037b91429fee71a05b9c9e1d369218"
upstream_artifacts_used: []
confidence_score: 55
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED"]
validation_warnings: ["FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "SOURCE_LIMITED"]
downstream_consumers: ["CP-1A", "CP-1C", "CP-2A", "CP-2H", "CP-3C", "CP-4C", "CP-5", "CP-L10"]
---

## Audit Summary

- **Canonical handoff:** `CZR_CP-0_20261002.md`.
- **Run status:** Restricted; source-readiness assessment completed with material source limitations.
- **Confidence:** 55 — Low. The broad primary-source coverage is offset by missing full-year, current legal-document, transaction-status and market-comparability evidence.
- **Preparation:** P3 and P5 contain one row for each of the 12 sources in the host preparation record. Ten extractions are recorded COMPLETE; the two FINRA representations are DEGRADED only for omitted chart points, while their displayed transaction fields remain usable. [C14]
- **Readiness:** Each of the eight route consumers is READY_WITH_LIMITATIONS. T8 sequences them; it does not assert that analytical predecessor handoffs already exist.
- **Scope:** This is a source-sufficiency handoff for SCREENING_ONLY. It makes no credit conclusion, legal interpretation or investment opinion.

## Analysis

### Analytical read-through

CP-0 finds the delivered source set usable for the selected LITE_FULL_CREDIT_SCREEN pathway, but not a complete underwriting record. The principal current-period anchor is Caesars’ Q2 2026 Form 10-Q, accompanied by issuer results and merger disclosures, the 2032 secured-note indenture and two supplements, a conformed credit agreement attached to the 2024 incremental agreement, two FINRA trade observations and two gaming peers’ Q2 releases. [C1, C6, C7, C8, C9, C10, C11, C12, C15, C16] These sources support bounded operating, debt, legal-document, issue-market and peer work. They do not supply the referenced 2025 Form 10-K, the full merger agreement and schedules, a post-2024 full credit-agreement update, complete master-lease documents or broad comparable-market observations. [C5, C18] Those omissions limit downstream coverage rather than automatically stopping consumers that can record gaps. The FINRA extracts also omit displayed chart points. [C14] T8 contains the eight route consumers and their source attachments.

The effective set includes a filed quarterly report, executed 2032 note documents and a conformed credit-agreement source; official company and peer results releases; merger disclosures; and two dated FINRA last-trade observations. The original-document authority and the fidelity of its active host extraction are recorded separately in T2 and P5. Source hierarchy is: **Tier 1** filed reports and executed financing documents; **Tier 2** issuer/agency releases and filed summaries; **Tier 3** dated market observations; **Tier 4** contextual or peer materials. Lower-tier material does not replace missing controlling documents. [C1, C6, C7, C8, C9, C10, C11, C12, C15, C16]

**Source coverage chain:** the Q2 filing and accompanying debt disclosures provide period-labelled financial, segment, debt and liquidity content; that content can support downstream screening, while the absent FY2025 report and full current lease/credit-document set constrain history, definitions and contractual coverage. The creditor-work implication for this gate is limited to readiness: downstream analysis must carry those gaps and must not present absent information as verified or complete. [C1, C5, C9, C10]

**Debt-basis trace:** the 10-Q debt note presents total debt and book-value columns, while its balance sheet separately shows current and long-term debt; the earnings release presents aggregate indebtedness and a non-GAAP net-debt measure. These are distinct displayed bases, not silently interchangeable inputs. Their coexistence requires the consuming analysis to preserve the stated definitions and investigate the basis before using a leverage figure. [C2, C3, C4]

**Market-data chain:** FINRA identifies the displayed prices as last trades, not bid, mid, ask or evaluated prices; the extracts omit chart points. A consumer using them as current market evidence must retain that basis and cannot infer a spread or a full price history from these records. [C11, C12, C14]

**Transaction-timing chain:** the Q2 filing describes merger conditions and separately identifies a July 13 post-period launch. Those dated events must remain separate from June 30 reporting-period figures. The delivered materials do not establish the merger’s status after the Q2 report; downstream work must not infer it from the older merger announcement or the later bond observations. [C17, C18]

The strongest contrary evidence to a restrictive readiness view is the unusually broad set of relevant filed and executed materials: the Q2 report, the 2032 indenture family, the conformed credit-agreement source and dated issue-level market observations provide usable inputs across several different evidence demands. [C1, C7, C8, C9, C10, C11, C12] That would support a less restricted gate if the full FY2025 filing, current operative credit and lease documents, complete merger materials and richer dated market data were supplied and reconciled. Until then, the omissions remain explicit limitations; no route consumer is blocked solely because its analytical predecessor has not yet run.

**Preparation summary:** The host preparation record is the preparation record; it holds the pinned originals, hashes, delivery decisions and active host extractions. P3 identifies and links the 12 logical sources; P5 records their WHOLE delivery, extraction status, page coverage and observed fidelity limits. Inventory and identity/version mapping pass; duplicate/amendment handling passes with the linked 2032 indenture family kept separate; locator coverage passes for the supplied evidence. Fidelity is restricted for the two FINRA charts only. The effective catalog uses one host extraction per source; no original fallback is used for a degraded field.

### Analytical appendix — complete canonical registers

#### P3 — Input Sources

| Source ID | Entity; document family and title | Period / as-of; filing, signing or effective date | Version status and relationships |
|---|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Caesars Entertainment, Inc.; SEC quarterly filing, Form 10-Q. [C1] | Quarter ended June 30, 2026; signed July 28, 2026. | Filed interim report; references the 2025 Form 10-K and merger agreement. Distinct from the Q2 earnings release. |
| 27f7042a-85aa-4a76-ac06-374bc7db0dbd | Caesars Entertainment, Inc.; FINRA fixed-income lookup, 6.500% senior secured notes due 2032, CUSIP 12769GAC4. [C11] | Observed October 2, 2026; last trade dated October 1, 2026. | Dated market observation for the 2032 secured-note issue; not an issuer filing or a quote-side market record. |
| 27f98f2d-64b4-4d3a-87f0-6946d3cb8c01 | Caesars Entertainment, Inc.; SEC Form 8-K, entry into material definitive merger agreement. [C6] | Report dated May 27, 2026; signed May 28, 2026. | Filed transaction summary. It references the merger agreement as Exhibit 2.1; the full agreement and schedules are not present in the delivered evidence. |
| 42064519-b433-435a-82c5-c1cabe537ac7 | Caesars Entertainment, Inc.; first supplemental indenture to the 6.500% senior secured notes due 2032 indenture. [C7] | Effective March 1, 2024. | Separate signed supplement to the February 6, 2024 base indenture; adds guarantors and amends specified provisions. Retained separately from the base and later supplement. |
| 463cb989-77ee-42f5-994d-606ea0f8b347 | PENN Entertainment, Inc.; Q2 2026 earnings release and supplemental results. [C15] | Quarter and six months ended June 30, 2026; release dated August 6, 2026. | Official peer issuer release; distinct issuer and evidence class from Caesars sources. |
| 4edecdd2-6ed8-429e-902c-eb92822cd767 | Caesars Entertainment, Inc.; Q2 2026 earnings release and financial schedules. [C4] | Quarter and six months ended June 30, 2026; release dated July 28, 2026. | Official issuer release for the same period as the 10-Q; supplemental, not a replacement for the filed report. |
| 6061f8bd-230a-4786-b679-b6acd966c841 | Caesars Entertainment, Inc.; second supplemental indenture to the 6.500% senior secured notes due 2032 indenture. [C8] | Effective August 23, 2024. | Separate signed supplement; recites the February 2024 indenture as supplemented by the March 2024 first supplement and adds guarantors. |
| 62196b68-88d8-4f6b-890a-402b6d44851b | Caesars Entertainment, Inc.; issuer merger announcement and transaction release. [C11] | Dated May 28, 2026. | Issuer release concerning the transaction also described in the Form 8-K and Q2 filing; supporting disclosure, not the operative agreement. |
| 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | Caesars Entertainment, Inc.; 6.500% senior secured notes due 2032 indenture, including exhibits and schedules. [C9] | Dated February 6, 2024. | Base executed indenture. The March and August 2024 supplements are separate linked sources and are not merged into this row. |
| b1d0e082-2cc6-4dc4-9544-5e758dd0e5e0 | MGM Resorts International; Q2 2026 results release and financial schedules. [C16] | Quarter and six months ended June 30, 2026; release dated July 29, 2026. | Official peer issuer release; distinct from Caesars materials. |
| b24b47d6-6bfd-4248-b660-e867409dd303 | Caesars Entertainment, Inc.; Incremental Assumption Agreement No. 3 and conformed July 20, 2020 credit agreement. [C10] | Agreement dated February 6, 2024; Term B-1 funding date February 6, 2024. | Executed incremental agreement with a conformed credit agreement incorporating listed prior amendments. No later full executed credit-agreement update is delivered. |
| b7df3500-3ccb-4b3a-8315-db4023c2a17f | Caesars Entertainment, Inc.; FINRA fixed-income lookup, 6.000% senior notes due 2032, CUSIP 12769GAD2. [C13] | Observed October 2, 2026; last trade dated October 1, 2026. | Dated market observation for the unsecured-note issue; distinct from the secured 2032 issue and not a quote-side market record. |

#### P5 — Parse Jobs

| Source ID | Extractor; delivery | Status; extraction confidence | Pages covered; fidelity limits shown by evidence |
|---|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–26. Locators and period labels are present; no lost table or chart is identified in the supplied representation. |
| 27f7042a-85aa-4a76-ac06-374bc7db0dbd | caos.plain-text v4; WHOLE | DEGRADED; Medium | Page 1. The displayed price/yield chart points are not transcribed; retain only displayed summary fields. [C14] |
| 27f98f2d-64b4-4d3a-87f0-6946d3cb8c01 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–3. The filed 8-K text is represented; the referenced full agreement and schedules are a source-coverage gap, not a parse fallback. [C6] |
| 42064519-b433-435a-82c5-c1cabe537ac7 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–3. Signature pages and operative amendment text are represented; no lost table or clause is identified. [C7] |
| 463cb989-77ee-42f5-994d-606ea0f8b347 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–5. Displayed tables and reconciliation notes are represented; the referenced presentation is not a supplied source. [C15] |
| 4edecdd2-6ed8-429e-902c-eb92822cd767 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–6. Displayed release schedules and reconciliation are represented; no extraction loss is identified. [C4] |
| 6061f8bd-230a-4786-b679-b6acd966c841 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–6. Main text, signatures and Schedule A are represented; no extraction loss is identified. [C8] |
| 62196b68-88d8-4f6b-890a-402b6d44851b | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–2. Release text is represented; it is issuer transaction communication, not the full merger agreement. [C11] |
| 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–60. Indenture, schedules and exhibits are represented; the second-lien intercreditor exhibit is a form, not evidence of an executed agreement. [C9] |
| b1d0e082-2cc6-4dc4-9544-5e758dd0e5e0 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–5. Displayed results, schedules and reconciliations are represented; no extraction loss is identified. [C16] |
| b24b47d6-6bfd-4248-b660-e867409dd303 | caos.plain-text v4; WHOLE | COMPLETE; High | Evidence pages 1–67. Incremental agreement and conformed credit-agreement text are represented; later full amendments are not in the delivered source set. [C10] |
| b7df3500-3ccb-4b3a-8315-db4023c2a17f | caos.plain-text v4; WHOLE | DEGRADED; Medium | Page 1. The displayed price/yield chart points are not transcribed; retain only displayed summary fields. |

#### T1 — Input Gate

| Field | CP-0 record | Validation |
|---|---|---|
| Objective | Assess whether the effective source set supports the selected LITE_FULL_CREDIT_SCREEN Q2 2026 credit-screening work, identify degraded or blocked evidence, and set downstream readiness. | PASS — objective is the selected pathway use case; no separate user objective was delivered. |
| Issuer / perimeter | Caesars Entertainment, Inc.; consolidated issuer and subsidiaries as identified in the filed 10-Q. | PASS — issuer identified from source content. [C1] |
| Reporting period / as-of | Q2 2026 ended June 30, 2026; market observations are dated October 1, 2026 and observed October 2, 2026. | PASS — periods and later observations are kept distinct. [C1, C11, C13] |
| Preparation record | HOST SOURCE PREPARATION record; host-pinned run source set, WHOLE delivery for all 12 sources. | PASS — context only; not cited as evidence. |
| Preparation identity and phase order | CP-0 owns the single preparation-then-readiness handoff; P3 and P5 precede readiness. | PASS — same run anchor; no separate CP-PARSE artifact. |
| Inventory / identity / version map | 12 unique source IDs; issuer, peer and market sources identified; supplements remain linked to their base indenture. | PASS — all host-listed sources represented once in P3 and P5. |
| Locator coverage / source quality separation | Source-content locators are present; original authority is recorded separately from extraction fidelity. | PASS, with FINRA chart limitation in P5. |
| Objective fit / conflicts / downstream readiness | Objective-specific gaps, one debt-basis conflict and eight module verdicts are recorded in T4, T5 and T8. | PASS WITH LIMITATIONS — no external retrieval or unprovided source is assumed. |
| Model-route boundary | CP-MODEL objective not selected; no model-route assertion made. | NA |
| Canonical Markdown | Filename, front matter, six headings, registers and citation markers checked in this draft. | PASS — host validator and completeness check follow this answer; their results are not claimed. |

#### T2 — Source Register

| Source ID | Original authority / source family | Quality label | Active representation and usability |
|---|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Filed Caesars Form 10-Q; primary interim financial filing. [C1] | Primary-Verified | Host extraction; COMPLETE. Primary period anchor for reported operating, balance-sheet, cash-flow, segment, debt and transaction disclosures. |
| 27f7042a-85aa-4a76-ac06-374bc7db0dbd | FINRA fixed-income lookup; secured 2032 issue. [C11] | Secondary-Reputable | Host extraction; DEGRADED for chart points only. Displayed trade and rating fields usable with last-trade caveat. |
| 27f98f2d-64b4-4d3a-87f0-6946d3cb8c01 | Filed Caesars Form 8-K; merger agreement summary. [C6] | Primary-Verified | Host extraction; COMPLETE for the filed report. The referenced agreement and schedules are not represented in its delivered text. |
| 42064519-b433-435a-82c5-c1cabe537ac7 | Signed first supplemental indenture. [C7] | Primary-Verified | Host extraction; COMPLETE. Separate source linked to the base 2032 indenture. |
| 463cb989-77ee-42f5-994d-606ea0f8b347 | Official PENN Q2 earnings release. [C15] | Secondary-Reputable | Host extraction; COMPLETE. Peer context only; does not substitute for a full peer filing or a verified comparable set. |
| 4edecdd2-6ed8-429e-902c-eb92822cd767 | Official Caesars Q2 earnings release. [C4] | Secondary-Reputable | Host extraction; COMPLETE. Supplemental to, not a substitute for, the filed 10-Q. |
| 6061f8bd-230a-4786-b679-b6acd966c841 | Signed second supplemental indenture. [C8] | Primary-Verified | Host extraction; COMPLETE. Separate linked supplement to the same base indenture and first supplement. |
| 62196b68-88d8-4f6b-890a-402b6d44851b | Official Caesars merger announcement. [C11] | Secondary-Reputable | Host extraction; COMPLETE. Transaction context only; not the controlling agreement. |
| 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | Executed 2032 senior secured notes indenture. [C9] | Primary-Verified | Host extraction; COMPLETE. Base legal document; supplements are separately active and linked. |
| b1d0e082-2cc6-4dc4-9544-5e758dd0e5e0 | Official MGM Q2 earnings release. [C16] | Secondary-Reputable | Host extraction; COMPLETE. Peer context only; does not substitute for a full peer filing or a verified comparable set. |
| b24b47d6-6bfd-4248-b660-e867409dd303 | Executed Incremental Assumption Agreement No. 3 and conformed credit agreement. [C10] | Primary-Verified | Host extraction; COMPLETE for delivered text. Current full post-2024 amendment history is not supplied. |
| b7df3500-3ccb-4b3a-8315-db4023c2a17f | FINRA fixed-income lookup; unsecured 2032 issue. [C13] | Secondary-Reputable | Host extraction; DEGRADED for chart points only. Displayed trade and rating fields usable with last-trade caveat. |

#### T3 — Source Hierarchy

| Source class | Authority rule | Present coverage | Missing minimum / limitation |
|---|---|---|---|
| Tier 1 — controlling filings and executed financing documents | Use filed reports and executed legal instruments as primary authority; keep each supplement separate. | Q2 Form 10-Q, 2032 indenture and supplements, and 2024 conformed credit-agreement source are present. [C1, C7, C8, C9, C10] | 2025 Form 10-K, full current post-2024 credit agreement, complete lease documents, and full executed merger agreement with schedules. The 10-Q itself refers readers to the 2025 Form 10-K. [C5] |
| Tier 2 — issuer / agency releases and reports | Use for supplemental reported results and dated management/transaction statements; do not override Tier 1. | Caesars and peer Q2 releases, Caesars 8-K merger summary and merger announcement are present. [C4, C6, C11, C15, C16] | Definitive merger proxy and current post-quarter transaction-status filing are not delivered. The transaction was subject to stated conditions. [C18] |
| Tier 3 — dated market / external evidence | Preserve publisher, issue, date, metric definition and observation basis. | Two FINRA last-trade observations for separate 2032 issues, dated October 1, 2026. [C11, C13] | No spread, benchmark curve, bid/mid/ask, dealer quote, trade size or transcribed chart points. [C14] |
| Tier 4 — peer or unattributed context | Context only; do not substitute for issuer-specific primary evidence. | Official PENN and MGM Q2 releases are available as isolated peer context. [C15, C16] | Full peer filings and a source-verified, definition-matched peer set are not included. |

#### T4 — Content-to-Module Map

| Module / capability | Active source content mapped | Evidence demand and readiness effect | Disposition |
|---|---|---|---|
| CP-1A | Caesars Q2 10-Q and earnings release; merger disclosures; credit agreement and indenture family. [C1, C4, C6, C9, C10] | Supports issuer-period filing and narrative work; FY2025 historical context and full current legal-document coverage remain gaps. | Recommended — READY_WITH_LIMITATIONS |
| CP-1C | Caesars, PENN and MGM Q2 releases; Caesars 10-Q. [C1, C15, C16] | Provides issuer and two peer release observations; no retrieved public-web peer filings or broad comparable set are available in this run. | Recommended — READY_WITH_LIMITATIONS |
| CP-2A | Caesars Q2 10-Q, segment schedules, debt/liquidity disclosures and issuer release. [C1, C4] | Supports screening from reported operating and financial data; annual history, current projections and fuller supporting documents are not supplied. | Recommended — READY_WITH_LIMITATIONS |
| CP-2H | Q2 filing, 2032 debt documents and two issue-level FINRA records. [C1, C9, C11, C13] | Provides issue-level ratings/trades and governing base indenture; chart points and full rating history or agency research are absent. | Recommended — READY_WITH_LIMITATIONS |
| CP-3C | Q2 filing and results release; credit agreement source; FINRA observations for two 2032 issues. [C1, C4, C10, C11, C13] | Supports a bounded refinancing-source review; no quote-side prices, spreads, benchmark curve or full current debt/lease documents. | Recommended — READY_WITH_LIMITATIONS |
| CP-4C | 2032 indenture and both supplements; credit agreement source; merger 8-K summary. [C6, C7, C8, C9, C10] | Provides a linked 2032 document family and credit-agreement text; full merger agreement, schedules and current full loan/lease document set remain absent. | Recommended — READY_WITH_LIMITATIONS |
| CP-L10 | 10-Q, credit agreement source, 2032 indenture and separate supplements. [C1, C7, C8, C9, C10] | The host-selected route includes this consumer; these materials are relevant document inputs, subject to the current-document and full-year limitations logged in T5. | Recommended — READY_WITH_LIMITATIONS |
| CP-5 | All 12 active host extractions; T1–T8, P3 and P5. [C1, C4, C6, C7, C8, C9, C10, C11, C12, C13, C15, C16] | Traceable source set and explicit fidelity/gap records support review; unresolved source gaps must remain visible in the receiving review. | Recommended — READY_WITH_LIMITATIONS |

#### T5 — Gaps and Conflicts

| ID | Type; severity | Source / evidence demand | Affected modules; readiness effect | Remediation; owner; status |
|---|---|---|---|---|
| G-1 | Missing source; MATERIAL | 2025 Form 10-K is referenced by the 10-Q but is not among delivered sources. [C5] | CP-1A, CP-2A, CP-2H, CP-3C, CP-L10; historical context and annual disclosure coverage limited. | Supply the filed 2025 Form 10-K and rerun CP-0; user/source owner; OPEN. |
| G-2 | Missing controlling legal documents; MATERIAL | Full executed merger agreement and schedules, definitive proxy, and post-Q2 transaction-status materials are not present in the delivered evidence. The 8-K is a summary source; stated closing conditions remain material evidence demands. [C6, C18] | CP-1A, CP-2A, CP-4C, CP-L10; transaction terms and subsequent status cannot be source-verified beyond the supplied disclosures. | Supply the full filed agreement/schedules and latest issuer transaction filing or definitive proxy; user/source owner; OPEN. |
| G-3 | Current-document coverage; MATERIAL | Full executed credit-agreement amendments after the February 2024 conformed source and the governing master-lease documents are not delivered. The 10-Q gives selected debt and lease disclosures, not the complete documents. [C9, C10] | CP-2H, CP-3C, CP-4C, CP-L10; current contractual and lease evidence is limited. | Supply the current executed credit-agreement package and controlling lease documents; user/source owner; OPEN. |
| G-4 | Market / peer coverage; MATERIAL | FINRA provides last-trade fields for two notes, not bid/mid/ask or spread data; chart points are not transcribed. Peer coverage consists of two issuer releases only. [C11, C13, C14, C15, C16] | CP-1C, CP-2H, CP-3C; broader comparable, spread and rating-history work is limited. | Supply dated quote-side/spread evidence and primary peer filings or other source-verified peer data; user/source owner; OPEN. |
| G-5 | Fidelity limitation; MINOR | FINRA extracts omit displayed chart points; all other supplied sources are recorded COMPLETE. [C14] | CP-2H, CP-3C; use only displayed FINRA summary fields and do not infer chart values. | Obtain a fidelity-checked chart representation if chart analysis is needed; source-preparation owner; OPEN. |
| CF-1 | Debt-basis conflict; MATERIAL | 10-Q debt note reports total debt and book-value columns; balance sheet reports current and long-term debt; issuer release reports aggregate indebtedness and its net-debt measure. [C2, C3, C4] | CP-1A, CP-2A, CP-2H, CP-3C, CP-L10; preserve gross/face, book and balance-sheet presentations distinctly until a downstream owner establishes the appropriate basis. | Reconcile to the defined downstream metric using the complete filing and its debt note; analytical consumer; OPEN. No CP-0 normalization or silent selection. |
| CF-2 | Period / subsequent-event boundary; MATERIAL | Q2 period ends June 30, 2026; the 10-Q separately identifies a July 13 post-period launch, while FINRA observations are dated October 1. [C1, C11, C13, C17] | All period-sensitive consumers; post-period facts and October market observations must remain dated and must not be blended into Q2 figures. | Keep period and event dates explicit; update only with a supplied subsequent filing; analytical consumer; OPEN. |

#### T6 — Evidence Trace

| Evidence ID | Claim / evidence basis | Original source | Active representation | Locator |
|---|---|---|---|---|
| E-01 | Q2 2026 filed reporting period. [C1] | Caesars Form 10-Q; source_id 1ae6b04b-413a-4f14-b5da-362701a558fb | CZR_Q2_2026_10Q.txt | p. 1 |
| E-02 | Balance-sheet current debt presentation. [C3] | Caesars Form 10-Q; source_id 1ae6b04b-413a-4f14-b5da-362701a558fb | CZR_Q2_2026_10Q.txt | p. 2 |
| E-03 | Debt-note total debt and book-value presentation. [C2] | Caesars Form 10-Q; source_id 1ae6b04b-413a-4f14-b5da-362701a558fb | CZR_Q2_2026_10Q.txt | p. 9 |
| E-04 | Issuer release net-debt presentation. [C4] | Caesars Q2 earnings release; source_id 4edecdd2-6ed8-429e-902c-eb92822cd767 | CZR_Q2_2026_Earnings_Release.txt | p. 2 |
| E-05 | Referenced 2025 annual report. [C5] | Caesars Form 10-Q; source_id 1ae6b04b-413a-4f14-b5da-362701a558fb | CZR_Q2_2026_10Q.txt | p. 5 |
| E-06 | Merger agreement entry disclosed in filed 8-K. [C6] | Caesars Form 8-K; source_id 27f98f2d-64b4-4d3a-87f0-6946d3cb8c01 | CZR_2026_Merger_Agreement_8K.txt | p. 1 |
| E-07 | First 2032 note supplemental indenture. [C7] | First Supplemental Indenture; source_id 42064519-b433-435a-82c5-c1cabe537ac7 | CZR_2024_650_Notes_First_Supplemental_Indenture.txt | p. 1 |
| E-08 | Second 2032 note supplemental indenture. [C8] | Second Supplemental Indenture; source_id 6061f8bd-230a-4786-b679-b6acd966c841 | CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | p. 1 |
| E-09 | Base 2032 notes indenture. [C9] | 6.500% Senior Secured Notes due 2032 Indenture; source_id 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | p. 1 |
| E-10 | Credit-agreement incremental and conformed document. [C10] | Incremental Assumption Agreement No. 3; source_id b24b47d6-6bfd-4248-b660-e867409dd303 | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | p. 1 |
| E-11 | Merger release consideration statement. [C11] | Caesars merger announcement; source_id 62196b68-88d8-4f6b-890a-402b6d44851b | CZR_2026_Merger_Press_Release.txt | p. 1 |
| E-12 | FINRA last-trade observation, secured issue. [C12] | FINRA lookup; source_id 27f7042a-85aa-4a76-ac06-374bc7db0dbd | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p. 1 |
| E-13 | FINRA last-trade observation, unsecured issue. [C13] | FINRA lookup; source_id b7df3500-3ccb-4b3a-8315-db4023c2a17f | CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | p. 1 |
| E-14 | FINRA chart transcription limitation. [C14] | FINRA lookup; source_id 27f7042a-85aa-4a76-ac06-374bc7db0dbd | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p. 1 |
| E-15 | PENN Q2 peer release. [C15] | PENN Q2 earnings release; source_id 463cb989-77ee-42f5-994d-606ea0f8b347 | PENN_Q2_2026_Earnings_Release.txt | p. 1 |
| E-16 | MGM Q2 peer release. [C16] | MGM Q2 earnings release; source_id b1d0e082-2cc6-4dc4-9544-5e758dd0e5e0 | MGM_Q2_2026_Earnings_Release.txt | p. 1 |
| E-17 | Identified post-period event. [C17] | Caesars Form 10-Q; source_id 1ae6b04b-413a-4f14-b5da-362701a558fb | CZR_Q2_2026_10Q.txt | p. 17 |
| E-18 | Merger conditions disclosure. [C18] | Caesars Form 10-Q; source_id 1ae6b04b-413a-4f14-b5da-362701a558fb | CZR_Q2_2026_10Q.txt | p. 5 |

#### T7 — Master Index State

| Field | State |
|---|---|
| Run / identity | COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; CZR; Caesars Entertainment, Inc.; Q2 2026; analysis date 2026-10-02. |
| Requested / resolved mode | LITE_CREDIT_22 / LITE_FULL_CREDIT_SCREEN; complete CP-0 preparation then readiness workflow. |
| Preparation record | HOST SOURCE PREPARATION is the preparation record; hashes, source pins and active host extractions remain host-owned. |
| Source inventory | 12 source records: 10 Caesars-related filing, legal, issuer-release or issue-market records and 2 peer issuer releases. No contained duplicate was identified; related reports and amendments remain separate sources. |
| Prepared representations | 12 active host extractions; 10 COMPLETE and 2 DEGRADED for omitted FINRA chart points. P3 and P5 cover the same 12 source IDs. |
| Canonical handoff | CZR_CP-0_20261002.md; sole analytical artifact for this CP-0 run. |
| Validation warnings / limitations | Missing full underwriting source set; missing 2025 Form 10-K; incomplete current legal-document and merger-status coverage; limited market and peer evidence; FINRA chart omission; debt-basis conflict. |
| Downstream consumers | CP-1A, CP-1C, CP-2A, CP-2H, CP-3C, CP-4C, CP-5, CP-L10. |
| Readiness state | READY_WITH_LIMITATIONS for each T8 row; source gaps remain open and follow the affected consumer. |

#### T8 — Recommended Run Command Sheet

| Sequence | Module | Candidate command | Exact command | Source files to attach | Upstream handoff | Readiness | Why now / blocker |
|---:|---|---|---|---|---|---|---|
| 1 | CP-1A | Run CP-1A | Run CP-1A | CZR_Q2_2026_10Q.txt; CZR_Q2_2026_Earnings_Release.txt; CZR_2026_Merger_Agreement_8K.txt; CZR_2026_Merger_Press_Release.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Current-period filings support screening; 2025 Form 10-K, full merger agreement and current complete legal-document set are absent. |
| 2 | CP-1C | Run CP-1C | Run CP-1C | CZR_Q2_2026_10Q.txt; CZR_Q2_2026_Earnings_Release.txt; PENN_Q2_2026_Earnings_Release.txt; MGM_Q2_2026_Earnings_Release.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Two peer releases are available; broad peer filings and a definition-matched comparable set are not supplied. |
| 3 | CP-2A | Run CP-2A | Run CP-2A | CZR_Q2_2026_10Q.txt; CZR_Q2_2026_Earnings_Release.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Q2 filing supports a bounded screen; FY2025 history, current forecasts and complete lease documents are absent. |
| 4 | CP-2H | Run CP-2H | Run CP-2H | CZR_Q2_2026_10Q.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Issue-level observations and debt documents are available; rating history and full market context are limited, and FINRA chart points are omitted. |
| 5 | CP-3C | Run CP-3C | Run CP-3C | CZR_Q2_2026_10Q.txt; CZR_Q2_2026_Earnings_Release.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Reported debt and two last-trade observations support bounded work; current full legal documents, lease documents and quote-side/spread data are absent. |
| 6 | CP-4C | Run CP-4C | Run CP-4C | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2026_Merger_Agreement_8K.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | The 2032 indenture family and conformed agreement are available; full merger agreement/schedules and current complete legal-document set are absent. |
| 7 | CP-L10 | Run CP-L10 | Run CP-L10 | CZR_Q2_2026_10Q.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Route-selected consumer has relevant filing and legal-document inputs; full current credit and lease documents remain a limitation. |
| 8 | CP-5 | Run CP-5 | Run CP-5 | CZR_Q2_2026_10Q.txt; CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_2026_Merger_Agreement_8K.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; PENN_Q2_2026_Earnings_Release.txt; CZR_Q2_2026_Earnings_Release.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2026_Merger_Press_Release.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; MGM_Q2_2026_Earnings_Release.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | This CP-0 handoff, run COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5; analytical predecessor is sequenced separately. | READY_WITH_LIMITATIONS | Source trace and preparation registers are present; downstream review must preserve the open gaps, fidelity limits and debt-basis conflict. |

The command sheet above appears once and is sourced only from the effective source set. No upstream analytical handoff is asserted to exist or treated as a source-readiness blocker.

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Q2 2026 reporting period | [C1] | Caesars Form 10-Q | 1 |
| Distinct balance-sheet and debt-note presentations | [C2, C3] | Caesars Form 10-Q | 2, 9 |
| Issuer release net-debt presentation | [C4] | Caesars Q2 earnings release | 2 |
| 2025 annual report is referenced | [C5] | Caesars Form 10-Q | 5 |
| Filed merger-agreement summary | [C6] | Caesars Form 8-K | 1 |
| 2032 indenture family supplements | [C7, C8, C9] | Indenture and supplemental indentures | 1 each |
| Conformed credit agreement source | [C10] | Incremental Assumption Agreement No. 3 | 1 |
| Merger announcement terms | [C11] | Caesars merger release | 1 |
| Secured and unsecured last-trade observations | [C12, C13] | FINRA fixed-income lookups | 1 each |
| FINRA chart fidelity limitation | [C14] | FINRA fixed-income lookup | 1 |
| Peer release coverage | [C15, C16] | PENN and MGM Q2 releases | 1 each |
| Post-period event and merger conditions | [C17, C18] | Caesars Form 10-Q | 17, 5 |

## Source Registry

The lossless input inventory and active-representation findings are recorded in P3, P5 and T2 under the analytical appendix. Each source has one row in P3 and one row in P5; hashes and extraction artifacts remain in the host preparation record. No P1, P2, P4, P6, P7 or P8 register is authored.

## Gaps & Conflicts

T5 records the open source gaps, downstream effects, remediation and one explicit debt-basis conflict. The material gaps do not prevent this source-readiness handoff or make any T8 consumer CONDITIONAL: each proposed consumer can proceed with the limitations recorded. The FINRA chart omission is a representation-fidelity limitation; no untranscribed points are supplied as evidence. Post-period events remain date-labelled and separate from Q2 figures.

## QA Validation

| Check | Result | Record |
|---|---|---|
| Preparation identity and internal phase order | PASS | CP-0 preparation registers precede readiness registers in this single artifact. |
| Inventory coverage | PASS | P3 and P5 each contain all 12 source IDs in the host preparation record exactly once. |
| Identity, period, version and amendment map | PASS | Issuer, peer and market identities are content-based; base indenture and supplements remain separate linked sources. |
| Locator and coverage integrity | PASS WITH LIMITATIONS | Evidence pages and locators are recorded; the two FINRA chart-point omissions are explicit in P5 and T5. |
| Authority / extraction-quality separation | PASS | Original-source authority is distinguished from active-extraction status and fidelity. |
| Entity, period and definition fit | PASS WITH LIMITATIONS | Q2 period and later observations remain separate; debt presentations are retained as a conflict rather than silently reconciled. |
| Gaps and conflicts | PASS WITH LIMITATIONS | T5 contains source gaps, effects, remediation, owner and status. |
| Downstream readiness | PASS WITH LIMITATIONS | All eight route consumers have objective-specific T4 and T8 rows. |
| Model-route assertion scope | NA | This is not a CP-MODEL objective; no model-readiness assertion is made. |
| Canonical Markdown draft | PASS — self-check | Required front matter, six H2 headings, P3/P5 and T1–T8 are present; confidence is 55 / Low and QA is Restricted. |
| Host validation | NOT RUN HERE | Host vendor validation and register-completeness checks follow this answer; no results or exit status are claimed. |
