---
module_id: "CP-0"
module_name: "SourceReadiness"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "COVENANT_REFINANCING"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-0-a3fd6b12c0cf1b46"
credit_os_route_node_id: "RN-FULL_CREDIT_32-COVENANT_REFINANCING-01-CP-0"
credit_os_invocation_sha256: "afe32f3c3bcd40e87f9785f20b9bf1f29f752f222c04514fd52f578ef1286366"
upstream_artifacts_used: []
confidence_score: 51
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED]
downstream_consumers: [CP-1, CP-2, CP-2D, CP-3C, CP-4, CP-5]
---

## Audit Summary

- **Run status:** Restricted; the available primary filings and executed financing documents support staged covenant-refinancing work, but transaction and market evidence gaps remain.
- **Confidence:** 51/100 — Low. The score is capped by material source limitations; it is not a credit rating or credit conclusion.
- **Canonical artifact:** `CZR_CP-0_20261002.md`.
- **Scope:** Source sufficiency and downstream readiness only. No credit conclusion, investment opinion, covenant-capacity calculation, or legal interpretation is made.
- **Recommended next action:** `Run CP-1`. T8 sequences the selected consumers and records their exact commands and attachments.

## Analysis

### Analytical read-through
The effective set is sufficient for staged Q2 2026 covenant-refinancing work, with material limitations. The Q2 filing provides interim financial statements, debt schedules, liquidity and covenant-status information; the FY2025 Form 10-K supplies audited annual comparatives and accounting context [C1, C2, C3, C4, C20, C21]. Credit-agreement materials include an executed February 2024 conformed agreement and separate Fourth and Fifth Amendments; the 2032 secured-note indenture and two supplemental indentures are also present [C6, C7, C8, C9, C10, C11, C22, C23]. Those sources support staged analysis, not a conclusion about capacity or legal effect. The proposed merger is a subsequent transaction and must remain distinct from Q2-period figures [C14]. The complete merger agreement and committed financing documents are not included in the admitted evidence, and current market quotations or lender indications are absent; these constrain transaction and refinancing work [C12, C13, C15]. The July 13 Alberta launch is also post-period [C19].

**Source hierarchy.** Controlling SEC filings and executed financing documents are the primary evidence. The issuer press release is supporting context only; it does not replace executed transaction documents. No dated loan-market or external pricing evidence is present in the admitted set. Readiness assessments are module-specific, not based on source count alone.

**Decision drivers.** Current-period financial and debt evidence is available; the legal-document chain is substantially represented but schedules and referenced transaction instruments are not fully evidenced; downstream analysis can proceed with limitations rather than wait for analytical predecessor handoffs. The command sheet below is the sole T8 table.

### Analytical appendix — complete canonical registers

#### P3 — Input Sources

| Source ID | Issuer or entity | Document family and title | Reporting period or as-of date | Filing, signing or effective date | Version status and relationships | Identity evidence |
|---|---|---|---|---|---|---|
| 050d12fd-6a63-4d3a-8d28-263977d76585 | Caesars Entertainment, Inc., borrower | Executed Fourth Amendment to Credit Agreement | Credit Agreement terms; effective-date definition is May 9, 2024 | Dated May 9, 2024 | Fourth Amendment; modifies the July 20, 2020 Credit Agreement as previously modified, including Incremental Assumption Agreement No. 3 | [C7] |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | Caesars Entertainment, Inc., borrower; subsidiary loan parties | Incremental Assumption Agreement No. 3 with conformed Credit Agreement, Exhibit A | Incremental financing dated February 6, 2024 | Dated February 6, 2024 | Execution-version Incremental Assumption Agreement No. 3; Exhibit A identifies the conformed 2020 Credit Agreement through the listed prior amendments and incremental agreements | [C6, C24] |
| 13a99137-9563-4f67-9e21-c7e195278e82 | Caesars Entertainment, Inc., issuer; subsidiary guarantors | 6.500% Senior Secured Notes due 2032 Indenture | Notes issued February 6, 2024; $1.5 billion initial principal amount | Dated February 6, 2024 | Base indenture; amended by separately delivered supplemental indentures | [C9] |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | Caesars Entertainment, Inc., borrower | Executed Fifth Amendment to Credit Agreement | Credit Agreement terms; effective date defined as November 25, 2024 | Dated November 25, 2024 | Fifth Amendment; modifies the Credit Agreement after the Fourth Amendment; later than the other delivered credit amendments | [C8, C23] |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | Caesars Entertainment, Inc. and consolidated subsidiaries | FY2025 Form 10-K, audited annual report | Fiscal year ended December 31, 2025 | Signed February 17, 2026 | Filed annual report; contains audited financial statements and an exhibit index listing the Fourth and Fifth Amendments | [C5, C21, C22, C23] |
| 6eb3eaa6-a948-486f-a6dd-0ecb3c140cbd | Caesars Entertainment, Inc.; Fertitta Entertainment, Inc. | Issuer merger press release | Proposed transaction announced May 28, 2026 | May 28, 2026 | Issuer release describing the proposed transaction; separate from the Form 8-K and not a substitute for the merger agreement | [C12] |
| 743e5d19-d65d-4487-8114-c0614dfc076d | Caesars Entertainment, Inc. and consolidated subsidiaries | Q2 2026 Form 10-Q | Quarter ended June 30, 2026; six-month comparisons | Signed and filed July 28, 2026 | Current interim filing; reports the proposed merger and post-quarter Alberta launch separately from the period statements | [C1, C14, C19, C20] |
| 79bf3e7f-a2b9-4029-ac75-70816dc58005 | Caesars Entertainment, Inc.; subsidiary guarantors | Second Supplemental Indenture to 2032 Notes Indenture | 2032 Notes; August 23, 2024 | Dated August 23, 2024 | Second supplemental indenture; modifies the February 6, 2024 base indenture; distinct from the first supplement | [C11] |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | Caesars Entertainment, Inc.; Fertitta Gaming Holdco, LLC; merger subsidiary and related parties | Form 8-K, current report on merger agreement | Report date May 27, 2026 | Filed and signed May 28, 2026 | SEC current report; references Agreement and Plan of Merger as Exhibit 2.1 and a separate press release as Exhibit 99.1; full merger agreement text is not present in the delivered evidence | [C13, C15] |
| fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | Caesars Entertainment, Inc.; subsidiary guarantors | First Supplemental Indenture to 2032 Notes Indenture | 2032 Notes; March 1, 2024 | Dated March 1, 2024 | First supplemental indenture; modifies the base indenture and addresses new guarantors; distinct from the second supplement | [C10] |

#### P5 — Parse Jobs

| Source ID | Extractor | Delivery | Parse status | Extraction confidence | Pages covered in delivered representation | Fidelity limitations and downstream effect |
|---|---|---|---|---|---|---|
| 050d12fd-6a63-4d3a-8d28-263977d76585 | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; readable legal text and locators | Evidence pages 1–2 | Execution-version amendment text and signature material are represented. No separate underlying base agreement is implied by this extraction; use the linked conformed agreement and later amendment as separate sources. [C7] |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | caos.plain-text v4 | WHOLE | DEGRADED | Medium, qualitative; text and clause locators are readable | Evidence pages 1–34 | The conformed agreement identifies schedules and exhibits, but the delivered text does not provide all referenced schedule contents. CP-4 must record schedule-level limits and must not infer schedule values or substitute an unverified version. [C24] |
| 13a99137-9563-4f67-9e21-c7e195278e82 | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; readable text and clause/page locators | Evidence pages 1–66 | Indenture text and listed exhibits are represented in the delivered extraction. No separate current intercreditor agreement or collateral filing is established by this source. [C9] |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; readable amendment and execution text | Evidence pages 1–3 | Fifth Amendment text and consent form are represented. The amendment remains separate from, and linked to, the base agreement and prior amendments. [C8] |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; audited statements, tables and locators are legible | Evidence pages 1–57 | The annual report body and financial tables are represented. Exhibit-index references do not themselves provide the text of each separately filed exhibit. [C5, C21] |
| 6eb3eaa6-a948-486f-a6dd-0ecb3c140cbd | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; release text and page locators are legible | Evidence pages 1–2 | The press release is supporting-only transaction context; its forward-looking statements are not treated as executed financing terms. [C12] |
| 743e5d19-d65d-4487-8114-c0614dfc076d | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; statements, tables and locators are legible | Evidence pages 1–26 | Interim statements, notes and MD&A are represented. Q2 period facts remain separate from the reported merger and the July 13 post-period launch. [C1, C19] |
| 79bf3e7f-a2b9-4029-ac75-70816dc58005 | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; readable text and schedule locators | Evidence pages 1–6 | Supplemental indenture text and its schedule are represented; it does not provide the complete underlying security-document package. [C11] |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | caos.plain-text v4 | WHOLE | DEGRADED | Medium, qualitative; filed-report narrative is readable | Evidence pages 1–3 | The Form 8-K narrative identifies Exhibit 2.1 and committed financing letters, but their complete text is not present in the delivered representation. Do not treat the summary as a substitute for either instrument. [C13, C15] |
| fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | caos.plain-text v4 | WHOLE | COMPLETE | High, qualitative; readable text and execution material | Evidence pages 1–3 | First supplemental indenture text and signature material are represented; current collateral perfection is not established by this document alone. [C10] |

#### T1 — Input Gate

| Field | Finding | Status or evidence |
|---|---|---|
| Objective | Assess whether the admitted source set supports Q2 2026 covenant and refinancing work; identify material source gaps and route the selected consumers. | Selected pathway purpose: COVENANT_REFINANCING. |
| Issuer and entity | Caesars Entertainment, Inc.; borrower/issuer and consolidated subsidiaries as identified in each source. | Fit confirmed across current filing and financing documents. [C1, C5, C9] |
| Reporting period | Q2 2026; quarter ended June 30, 2026. FY2025 used as the audited comparator, not as a replacement for the current period. | PASS. [C1, C5] |
| Preparation record | HOST SOURCE PREPARATION metadata; one host extraction per listed source, delivered WHOLE. | Context only; hashes and package details are not restated. |
| Inventory and ordering | Ten admitted sources; P3 and P5 each contain one row per source before readiness mapping. | PASS, 10/10 P3 and 10/10 P5. |
| Identity, period and version map | Source identity comes from document content; credit agreement and note indenture amendments remain separately linked. | PASS with the P5 limitations recorded above. [C7, C8, C9, C10, C11, C22, C23] |
| Locator and representation use | Authority remains the original; the host extraction is the active content representation. Citations point to the delivered EVIDENCE pages. | PASS for cited evidence; two degraded extractions carry explicit restrictions. |
| Gaps and conflicts | Transaction documents, market evidence and some referenced schedules are not fully available; date and debt-basis distinctions are preserved. | PASS; see T5. [C3, C12, C13, C15, C24] |
| Downstream readiness | Each selected consumer can proceed with its own gaps recorded; no readiness verdict waits solely for a future analytical handoff. | READY_WITH_LIMITATIONS for all six selected consumers; see T4 and T8. |
| Source gate | Partial, reflecting material evidence limitations rather than a blocked parse of the financial filings. | PARTIAL. |

#### T2 — Source Register

| Source ID | Effective source filename | Source class and authority | Period or date fit | Representation status | Readiness use and limitation | Evidence |
|---|---|---|---|---|---|---|
| 050d12fd-6a63-4d3a-8d28-263977d76585 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt | Executed financing amendment; primary legal source | Dated/effective May 9, 2024 | Active host extraction; COMPLETE | Relevant to credit-document chronology; analyze with the later Fifth Amendment and conformed agreement. [C7] | [C7] |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | Executed incremental financing agreement and conformed agreement; primary legal source | Dated February 6, 2024 | Active host extraction; DEGRADED | Provides the conformed agreement through the delivered text; referenced schedules are not all present. [C6, C24] | [C6, C24] |
| 13a99137-9563-4f67-9e21-c7e195278e82 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | Executed note indenture; primary legal source | Dated February 6, 2024 | Active host extraction; COMPLETE | Note terms and covenant source; do not infer collateral perfection or later amendments from the indenture alone. [C9] | [C9] |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | CZR_2024_Credit_Agreement_Fifth_Amendment.txt | Executed financing amendment; primary legal source | Dated/effective November 25, 2024 | Active host extraction; COMPLETE | Latest delivered credit-agreement amendment; later amendments, if any, are not included in the admitted set. [C8, C23] | [C8, C23] |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | SEC annual filing; primary financial and issuer source | FY ended December 31, 2025; filed February 2026 | Active host extraction; COMPLETE | Audited history, debt, liquidity, operations and risk disclosure; older than Q2 2026. [C5, C18, C21] | [C5, C18, C21] |
| 6eb3eaa6-a948-486f-a6dd-0ecb3c140cbd | CZR_2026_Merger_Press_Release.txt | Issuer announcement; secondary/supporting source | May 28, 2026 | Active host extraction; COMPLETE | Transaction context only; not the merger agreement or a financing commitment. [C12] | [C12] |
| 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | SEC quarterly filing; primary financial and issuer source | Quarter ended June 30, 2026; filed July 28, 2026 | Active host extraction; COMPLETE | Current interim statements, debt, liquidity, covenant and subsequent-event disclosures. [C1, C2, C3, C16, C20] | [C1, C2, C3, C16, C20] |
| 79bf3e7f-a2b9-4029-ac75-70816dc58005 | CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | Executed supplemental indenture; primary legal source | Dated August 23, 2024 | Active host extraction; COMPLETE | Part of the 2032 indenture lineage; current collateral status is not established. [C11] | [C11] |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | CZR_2026_Merger_Agreement_8K.txt | SEC current report; primary for its filed narrative | Report date May 27, 2026; signed/filing evidence dated May 28, 2026 | Active host extraction; DEGRADED | Filed summary identifies agreement and financing commitments; complete Exhibit 2.1 and commitment letters are absent from delivered text. [C13, C15] | [C13, C15] |
| fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | CZR_2024_650_Notes_First_Supplemental_Indenture.txt | Executed supplemental indenture; primary legal source | Dated March 1, 2024 | Active host extraction; COMPLETE | Part of the 2032 indenture lineage; analyze separately from the base and second supplemental indenture. [C10] | [C10] |

#### T3 — Source Hierarchy

| Tier | Source class and rule | Present in effective source set | Missing minimum or use limit | Evidence |
|---|---|---|---|---|
| 1 — controlling/primary | SEC filings and executed financing documents control source authority for filed financial facts and executed terms. Keep base documents and amendments linked, not merged. | Q2 2026 Form 10-Q, FY2025 Form 10-K, credit-agreement documents, 2032 Notes Indenture and two supplements. | Complete merger agreement, financing commitment letters and any post-November 2024 executed covenant amendments or relevant schedules are needed to close transaction-specific and current-term gaps. [C1, C5, C7, C8, C9, C10, C11, C22, C23] | [C1, C5, C7, C8, C9, C10, C11, C22, C23] |
| 2 — issuer/agency | Issuer releases and reports support context but do not replace executed primary instruments. | Merger press release and Form 8-K narrative. | Do not rely on summary language as the full merger agreement or financing terms. [C12, C13, C15] | [C12, C13, C15] |
| 3 — dated market/external | Current market prices, yields, trading levels and external financing evidence are required where a downstream workflow calls for them. | No dated market quote or lender pricing indication is included among admitted sources. | Obtain current, dated, instrument-specific market evidence for refinancing analysis; do not infer a price or spread. | [Insufficient Information] — no market quote or lender indication was located in the admitted source set. |
| 4 — user/unattributed context | Context may guide scope but cannot override primary sources. | No separate user summary or peer document is in the admitted evidence. | No user summary is needed to proceed; an absent peer, price or document remains a gap. | [Insufficient Information] — no such source is included in the effective-source inventory. |

#### T4 — Content-to-Module Map

| Active content basis | Consumer | Specific evidence demand | Readiness effect | Limitation to carry forward | Evidence |
|---|---|---|---|---|---|
| Q2 2026 Form 10-Q; FY2025 Form 10-K; debt and segment disclosures | CP-1 | Current financial statements, historical comparators, debt carrying-value inputs, cash flow and definitions | READY_WITH_LIMITATIONS | Interim period only; preserve face/book-value distinctions and the pending merger as a separate event. [C1, C3, C4, C5, C25] | [C1, C3, C4, C5, C25] |
| Q2 2026 and FY2025 financial and operating disclosures; executed credit documents | CP-2 | Source-located operating, cash-flow, debt and covenant context | READY_WITH_LIMITATIONS | No CP-0 covenant-capacity calculation; full agreement schedules and merger financing evidence are not fully present. [C3, C7, C8, C20, C24] | [C3, C7, C8, C20, C24] |
| Q2 cash, revolver, debt service, operating cash flow and reported customer liabilities | CP-2D | Near-term liquidity inputs, contractual requirements and relevant timing | READY_WITH_LIMITATIONS | No detailed forward monthly cash forecast or complete merger funding terms. Customer deposits/deferred revenue are operating liabilities and should remain distinct from debt. [C2, C4, C16, C17, C27] | [C2, C4, C16, C17, C27] |
| Q2 and FY2025 debt schedule; Fourth and Fifth Amendments; 2032 Notes terms | CP-3C | Performing-issuer refinancing inputs, maturity and facility structure, covenant context and market evidence | READY_WITH_LIMITATIONS | Current loan/bond quotations, lender indications, and full merger financing commitments are absent; preserve the reported debt basis and transaction date. [C3, C7, C8, C12, C13, C17] | [C3, C7, C8, C12, C13, C17] |
| Conformed Credit Agreement, separately delivered amendments, 2032 Notes Indenture and supplements | CP-4 | Governing text, amendments, guarantees/security provisions, schedules and transaction agreements requested by the legal workflow | READY_WITH_LIMITATIONS | Some referenced schedules are not represented; complete merger agreement and executed commitment letters are not included. CP-0 makes no legal interpretation. [C7, C8, C9, C10, C11, C13, C15, C24] | [C7, C8, C9, C10, C11, C13, C15, C24] |
| This CP-0 handoff and its source-located registers | CP-5 | Reconcile source lineage, evidence, period, definitions, gaps and downstream analytical claims | READY_WITH_LIMITATIONS | The selected analytical handoffs are sequenced by T8; their not-yet-produced status is not a source-readiness blocker. Carry all T5 limitations into later QA. [C1, C3, C7, C8, C14, C20] | [C1, C3, C7, C8, C14, C20] |

#### T5 — Gaps and Conflicts

| ID | Type | Severity | Source or evidence demand | Affected modules | Readiness effect | Remediation, owner and status | Evidence |
|---|---|---|---|---|---|---|---|
| G-01 | Missing transaction source | MATERIAL | Complete merger agreement and executed debt commitment letters are referenced in the Form 8-K materials but their full terms are not in the delivered evidence. | CP-2D, CP-3C, CP-4, CP-5 | READY_WITH_LIMITATIONS; transaction terms are not a complete refinancing input. | Supply the complete Exhibit 2.1 and commitment letters or definitive financing documents; rerun CP-0 to refresh the source set. Owner: user/source provider. Status: open. [C13, C15] | [C13, C15] |
| G-02 | Missing market evidence | MATERIAL | Current instrument-level loan/bond quotations, yields, trading levels and lender indications are absent. | CP-3C; CP-2D where market access affects liquidity options | READY_WITH_LIMITATIONS; no market price or execution spread can be supported. | Attach dated market evidence for relevant instruments and financing terms; rerun CP-0. Owner: user/source provider. Status: open. | [Insufficient Information] — no dated market quote or lender indication is in the admitted source set. |
| G-03 | Schedule and representation coverage | MATERIAL | The conformed agreement references schedules, including Existing Indebtedness; delivered extracted text does not establish all schedule contents. | CP-2, CP-3C, CP-4 | READY_WITH_LIMITATIONS; no schedule-dependent conclusion should be inferred. | Provide the complete governing schedules and any relevant intercreditor/security documents if they are needed by the consumer. Owner: user/source provider. Status: open. [C24] | [C24] |
| CF-01 | Debt date/basis distinction | MATERIAL | The merger announcement states approximately $11.9 billion of debt assumed; the June 30, 2026 debt schedule reports $11,807 million face value and $11,705 million book value. These differ in date and stated basis; do not reconcile or silently select one. | CP-1, CP-2, CP-2D, CP-3C, CP-5 | READY_WITH_LIMITATIONS; retain each figure with its role and date. | Downstream users should use the governing metric definition and report both source values where relevant. Owner: receiving module. Status: open pending analytical reconciliation. [C3, C12] | [C3, C12] |
| CF-02 | Version sequence, not silently combined | MATERIAL | The Fourth Amendment states Term B margin terms different from those in the Fifth Amendment; the Fifth Amendment is dated later and the FY2025 exhibit index separately identifies both instruments. This is a version sequence to verify, not a CP-0 legal conclusion. | CP-2, CP-3C, CP-4, CP-5 | READY_WITH_LIMITATIONS; use each instrument as a separate active source and have CP-4 establish operative text. | Preserve the amendment chain and verify effective terms from the full agreement set. Owner: CP-4. Status: open for downstream review. [C7, C8, C22, C23] | [C7, C8, C22, C23] |
| G-04 | Subsequent event | MINOR | The Alberta mobile launch is dated July 13, 2026, after the June 30 reporting date; keep it outside period figures. | CP-1, CP-2, CP-2D, CP-3C, CP-5 | READY_WITH_LIMITATIONS; flag as post-period context only. | Carry the event date and do not blend it into Q2 results. Owner: receiving module. Status: recorded. [C1, C19] | [C1, C19] |

#### T6 — Evidence Trace

| Evidence ID | Claim supported | Original source ID | Active representation | Locator | Evidence type | Citation |
|---|---|---|---|---|---|---|
| E-01 | Q2 2026 reporting period | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 1 | Filing identity | [C1] |
| E-02 | Q2 and FY2025 cash balance comparators | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 2 | Table value | [C2] |
| E-03 | Q2 debt face/book schedule values | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 9 | Table value | [C3] |
| E-04 | First-half operating cash flow | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 4 | Table value | [C4] |
| E-05 | FY2025 annual period | 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | p. 1 | Filing identity | [C5] |
| E-06 | Incremental Term B-1 commitment amount | 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | p. 4 | Schedule value | [C6] |
| E-07 | Fourth Amendment Term B margin wording | 050d12fd-6a63-4d3a-8d28-263977d76585 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt | p. 1 | Amendment text | [C7] |
| E-08 | Fifth Amendment Term B margin wording | 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | CZR_2024_Credit_Agreement_Fifth_Amendment.txt | p. 1 | Amendment text | [C8] |
| E-09 | 2032 senior secured note indenture identity | 13a99137-9563-4f67-9e21-c7e195278e82 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | p. 1 | Legal document identity | [C9] |
| E-10 | First supplemental indenture date | fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | CZR_2024_650_Notes_First_Supplemental_Indenture.txt | p. 1 | Legal document identity | [C10] |
| E-11 | Second supplemental indenture date | 79bf3e7f-a2b9-4029-ac75-70816dc58005 | CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | p. 1 | Legal document identity | [C11] |
| E-12 | Merger press-release stated transaction value and debt assumed | 6eb3eaa6-a948-486f-a6dd-0ecb3c140cbd | CZR_2026_Merger_Press_Release.txt | p. 1 | Issuer announcement | [C12] |
| E-13 | Form 8-K statement that financing commitment letters were delivered | e909b0a2-f120-42de-8cf4-4f63b2acc275 | CZR_2026_Merger_Agreement_8K.txt | p. 2 | Filed narrative | [C13] |
| E-14 | Merger agreement entry date | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 5 | Subsequent transaction disclosure | [C14] |
| E-15 | Form 8-K exhibit index identifies Agreement and Plan of Merger | e909b0a2-f120-42de-8cf4-4f63b2acc275 | CZR_2026_Merger_Agreement_8K.txt | p. 3 | Filing exhibit index | [C15] |
| E-16 | Q2 cash and borrowing-capacity summary | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 22 | Table value | [C16] |
| E-17 | Q2 annualized/remaining debt service schedule | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 9 | Table value | [C17] |
| E-18 | FY2026 expected VICI/GLPI lease payments | 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | p. 23 | Issuer disclosure | [C18] |
| E-19 | Post-period Alberta launch date | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 17 | Subsequent event | [C19] |
| E-20 | Q2 filing covenant-status statement | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 23 | Issuer disclosure | [C20] |
| E-21 | FY2025 audited financial-statement opinion | 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | p. 28 | Audit report | [C21] |
| E-22 | FY2025 exhibit index listing Fourth Amendment | 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | p. 56 | Filing exhibit index | [C22] |
| E-23 | FY2025 exhibit index listing Fifth Amendment | 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | p. 56 | Filing exhibit index | [C23] |
| E-24 | Conformed Credit Agreement schedule reference | 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | p. 8 | Table of contents | [C24] |
| E-25 | Q2 balance-sheet long-term debt amount | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 2 | Table value | [C25] |
| E-26 | FY2025 issuer-reported debt amount | 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | p. 13 | Issuer disclosure | [C26] |
| E-27 | Customer-deposit and deferred-revenue liability movement | 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | p. 11 | Table value | [C27] |

#### T7 — Master Index State

| Run ID | Issuer and objective | Preparation record | Source counts and scope | Validation warnings and limitation state | Canonical handoff | Downstream consumers |
|---|---|---|---|---|---|---|
| COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | CZR; Q2 2026 COVENANT_REFINANCING | HOST SOURCE PREPARATION metadata | 10 originals; 10 P3 rows; 10 P5 rows; zero upstream artifacts; 8 COMPLETE and 2 DEGRADED parses | SOURCE_LIMITED_NOT_COMMITTEE_READY; FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED; transaction instruments and market evidence remain gaps | CZR_CP-0_20261002.md | CP-1, CP-2, CP-2D, CP-3C, CP-4, CP-5 [C1, C5, C13, C20] |

#### T8 — Recommended Run Command Sheet

| Sequence | Module | Candidate command | Exact command | Source files to attach | Upstream handoff | Readiness | Why now / blocker |
|---:|---|---|---|---|---|---|---|
| 1 | CP-1 | Run CP-1 | Run CP-1 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2026_Merger_Press_Release.txt; CZR_2026_Merger_Agreement_8K.txt | CZR_CP-0_20261002.md; run COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | READY_WITH_LIMITATIONS | Current interim and audited annual financial sources are present; preserve date, debt-basis and pending-transaction limitations. [C1, C3, C5, C14] |
| 2 | CP-2 | Run CP-2 | Run CP-2 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt | CZR_CP-0_CP-1 handoff in route order; retain this CP-0 run ID | READY_WITH_LIMITATIONS | Proceed on available current financial and financing disclosures; schedule and transaction-document gaps remain. [C3, C7, C8, C24] |
| 3 | CP-2D | Run CP-2D | Run CP-2D | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt | CZR_CP-0_CP-1 and CP-2 handoffs in route order; retain this CP-0 run ID | READY_WITH_LIMITATIONS | Current cash, revolver capacity, cash flow, debt-service and lease information is available; no detailed forward cash forecast or merger financing documents are supplied. [C2, C4, C16, C17, C18] |
| 4 | CP-3C | Run CP-3C | Run CP-3C | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2026_Merger_Agreement_8K.txt | CZR_CP-0_CP-1, CP-2 and CP-2D handoffs in route order; retain this CP-0 run ID | READY_WITH_LIMITATIONS | Performing-issuer refinancing work can proceed, but current market quotes, lender indications and full merger financing terms are missing; exact remediation is G-01 and G-02. [C3, C12, C13, C17] |
| 5 | CP-4 | Run CP-4 | Run CP-4 | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2026_Merger_Agreement_8K.txt; CZR_Q2_2026_10Q.txt | CZR_CP-0 and earlier selected route handoffs; retain this CP-0 run ID | READY_WITH_LIMITATIONS | The amendment and indenture sources are separately available; the full merger agreement, commitment letters and referenced schedules remain unresolved source gaps. [C7, C8, C9, C10, C11, C13, C15, C24] |
| 6 | CP-5 | Run CP-5 | Run CP-5 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt; CZR_FY2025_10K.txt; CZR_2026_Merger_Press_Release.txt; CZR_Q2_2026_10Q.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2026_Merger_Agreement_8K.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt | CZR_CP-0 and selected analytical handoffs in route order; retain this CP-0 run ID | READY_WITH_LIMITATIONS | Run after the selected analytical outputs are available for validation; the not-yet-produced handoffs are a sequencing matter, not a source-readiness blocker. Preserve G-01 through G-04 and CF-01 through CF-02. [C1, C3, C7, C8, C14, C20] |

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Q2 reporting period and current statements | [C1] | Q2 2026 Form 10-Q | 1 |
| Current cash and debt schedule | [C2, C3] | Q2 2026 Form 10-Q | 2, 9 |
| First-half operating cash flow | [C4] | Q2 2026 Form 10-Q | 4 |
| Audited FY2025 comparator | [C5, C21] | FY2025 Form 10-K | 1, 28 |
| Credit amendment sequence | [C7, C8, C22, C23] | Fourth Amendment; Fifth Amendment; FY2025 Form 10-K exhibit index | 1; 1; 56 |
| 2032 Notes indenture and supplements | [C9, C10, C11] | Base indenture; first and second supplemental indentures | 1; 1; 1 |
| Merger value, filing and financing references | [C12, C13, C14, C15] | Press release; Form 8-K; Q2 Form 10-Q | 1; 2–3; 5 |
| Q2 liquidity, debt service and covenant status | [C16, C17, C20, C25] | Q2 2026 Form 10-Q | 2, 9, 23, 2 |
| Lease obligation scale and FY2026 payments | [C18] | FY2025 Form 10-K | 23 |
| Post-quarter event and operating-liability movement | [C19, C27] | Q2 2026 Form 10-Q | 17, 11 |
| Referenced agreement schedule | [C24] | Conformed Credit Agreement table of contents | 8 |
| FY2025 reported debt context | [C26] | FY2025 Form 10-K | 13 |

## Source Registry

The effective source catalog consists of the ten filenames listed in the host’s source-preparation record and reproduced in T2. Each retained source has one active host extraction; original-source authority is distinct from extraction fidelity. P3 records source identity, period, version and relationships; P5 records delivery, status, coverage and limitations. The host-preparation record remains the source of hashes and managed artifacts and is not restated here.

## Gaps & Conflicts

The source set is useful but not complete for transaction-specific refinancing or full covenant work. T5 retains the open document and market gaps, preserves the debt amount/date/basis difference without reconciliation, distinguishes the amendment version sequence from an unresolved source conflict, and flags the July post-period event separately. These gaps do not prevent the selected consumers from proceeding with limitations. No legal effect, covenant capacity or refinancing price is determined in CP-0.

## QA Validation

- **Preparation identity and phase ordering:** PASS — the CP-0 run anchor is preserved; P3 and P5 are listed before readiness registers.
- **Inventory and source coverage:** PASS — ten listed sources each have one P3 row and one P5 row; active representation is identified by the host’s preparation record.
- **Locator and citation coverage:** PASS — citations use delivered EVIDENCE source IDs and page coordinates; citation markers in the body map to the citations list.
- **Authority/fidelity separation:** PASS WITH LIMITATIONS — primary authority is assigned to original filings and executed instruments; two degraded representations and their effects are disclosed.
- **Entity, period, version, gaps and conflicts:** PASS WITH LIMITATIONS — Q2, FY2025, amendment chronology, debt bases and the merger event are kept distinct.
- **Downstream readiness and route:** PASS WITH LIMITATIONS — T8 contains exactly CP-1, CP-2, CP-2D, CP-3C, CP-4 and CP-5 once each, in sequence; no upstream handoff absence is treated as a source blocker.
- **Confidence and QA status:** PASS — score 51, band Low and qa_status Restricted are consistent with material limitations and the score cap.
- **Canonical Markdown identity and structure:** PASS — filename, issuer, module, run anchor, front matter and six required H2 headings are consistent in this draft; required registers P3, P5 and T1–T8 are present, and T8 appears once.
- **Host validation:** Pending after this response. No host validator or completeness-check result is asserted.