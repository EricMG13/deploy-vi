---
module_id: "CP-5"
module_name: "EvidenceTraceValidator"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "COVENANT_REFINANCING"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-5-5aaf807e6a88951f"
credit_os_route_node_id: "RN-FULL_CREDIT_32-COVENANT_REFINANCING-07-CP-5"
credit_os_invocation_sha256: "534098b33bc364766b686cefb3643af130107327be9e8745bd75ef1edda58210"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a4ee2ea26d222a51d5c167a5868ea43f9bba131c911042fc7dcb2840af340ca2"
  - module_id: "CP-1"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a412c541834dd7643188444e637ba16543096bf4686d71c334f32b4a53e19a67"
  - module_id: "CP-4"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "6c9650a7f874fc6e1a214611d44701f46dfc986371aeb7b103d5598570f9f0b7"
  - module_id: "CP-2"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "b5f995cd341cadb6d06fa727e089dcc5546204d11efb49cb6a0e23034aa9ab5c"
  - module_id: "CP-2D"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "2d6aff3999ac9671c2697cd209141108a993aae0d3f6b9434d3e017f0837d750"
  - module_id: "CP-3C"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "995716a2e75062eab9956be6ca569ff47fa57dc88aeee9468304e10369e23812"
confidence_score: 16
confidence_band: "Insufficient Information"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, CURRENT_REFINANCING_MARKET_DATA_MISSING, EXECUTED_INTERCREDITOR_AND_SCHEDULES_NOT_PROVIDED, DEBT_BASIS_RECONCILIATION_OPEN]
validation_warnings: [UPSTREAM_QA_STATUS_RESTRICTED, UPSTREAM_CITATION_SYNTAX_DEFECT, NULL_TO_ZERO_INTERFACE_DEFECT]
downstream_consumers: [CP-6, CP-6A]
---

## Audit Summary

- **Module status:** Ready with Limitations. The accepted substantive handoffs for CP-0, CP-1, CP-2, CP-2D, CP-3C and CP-4 match issuer CZR, run COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 and reporting period Q2 2026. Their QA statuses are Restricted; the full underwriting source set is not retained.
- **Traceability scope:** Top 5. The source gate is partial: the filings and selected executed financing documents support source-grounded review, while current market evidence, complete transaction financing terms, current legal schedules and an executed current intercreditor agreement are not in the evidence delivered.
- **Confidence:** 16/100 — Insufficient Information band. Inputs: E=60 (three directly sourced and two insufficient-information Top 5 claims), C=95, S=0.7 (partial source gate), P=36 (two MATERIAL and two MINOR CP-5A findings). Formula: clamp((0.6×60 + 0.4×95)×0.7 − 36, 0, 100)=16.
- **Clearance:** Restricted; no Critical issue was found. The source limitations are not repaired by this audit, and the original credit conclusions are not changed.
- **Canonical filename:** `CZR_CP-5_20261002.md`.

## Analysis

### Traceability conclusion
Overall, evidence traceability is Ready with Remediation. Of the Top 5 material credit drivers, 3 are directly sourced, 0 are calculated, 0 are assumption-based, 0 are analyst inferences, and 2 are weak-lineage, untraced, conflicting, or insufficient-information items. The most important provenance gap is current, instrument-specific refinancing-market evidence; full merger financing terms are also unavailable. Without these inputs, the 2028 maturity schedule cannot be translated into execution cost or reliable market access, restricting refinancing conviction and committee use. The Q2 filing directly reports $2,928 million of cash and borrowing capacity, $767 million of 2028 maturities, and lower Q2 Adjusted EBITDA margin year over year; none is a forward cash forecast. [C12, C13, C14] Two upstream trace defects require correction before downstream consumption; see T5.2–T5.3 and T5B.6.

**Evidence → risk mechanic → creditor implication.** Reported cash and capacity can buffer near-term requirements, but do not establish 12-month coverage or liquidity available to every borrower entity. Scheduled 2028 debt service makes refinancing execution important; current prices, lender terms and full transaction financing are absent, so execution cost and access remain unassessed. The issuer reports period-end covenant compliance, but neither this statement nor the executed covenant thresholds establish headroom without the test calculation and usage data. [C12, C13, C16, C17, C26, C27]

**Strongest contrary evidence.** Management expects existing liquidity, committed borrowing availability and operating cash flows to fund operations, capital requirements and debt service for twelve months and beyond; reported compliance and positive Regional Q2 Adjusted EBITDA are additional offsets. This challenge would gain weight if a reconciled monthly downside forecast and facility-access evidence demonstrated headroom through the 2028 refinancing window. It does not supply the missing market price, lender indication, covenant certificate or transaction financing terms. [C12, C16, C17]

**Downside and monitoring.** If lower Las Vegas visitation or hold persists, lower segment earnings are the first operational break; weaker cash conversion against scheduled debt service, lease payments and capex can increase revolver reliance and refinancing dependence. Monitor segment earnings and hold, cash and facility availability, covenant certificates, basket usage, executed transaction financing and any debt amendment or extension. Alberta’s July 13, 2026 launch is post-period and must not be blended into Q2 figures. [C13, C15, C30]

### Analytical appendix — complete canonical registers

#### T5B.1 — Source Register

| Source Document ID | Source Document Name | Source Quality | Period | Entity Covered | Data Supplied | Limitation | Downstream Use |
|---|---|---|---|---|---|---|---|
| 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | Primary-Verified | Quarter and six months ended 2026-06-30 | Caesars Entertainment, Inc. and consolidated subsidiaries | Interim financials, debt, maturity schedule, liquidity, covenant statement and operating results. [C1, C12, C13, C15, C16] | Unaudited; period and perimeter changes affect comparability; does not provide a forward cash forecast. | Current financial and debt evidence for the five drivers. |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | Primary-Verified | Fiscal year ended 2025-12-31 | Caesars Entertainment, Inc. and consolidated subsidiaries | Audited annual financial statements, business context and segment results. [C2, C21, C29] | Historical comparator; not a substitute for Q2 2026 or current market evidence. | Source-quality and null-value cross-check; historical context. |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | Primary-Verified; executed document and conformed agreement | 2024-02-06 agreement; conformed agreement through Incremental Assumption Agreement No. 3 | CEI borrower and listed subsidiary loan parties | Credit definitions, covenant thresholds and permitted debt mechanisms. [C3, C22, C26, C27] | Referenced schedules are incomplete; current usage and a later fully conformed agreement are not established. | Legal definitions and capacity boundaries, not current remaining capacity. |
| 050d12fd-6a63-4d3a-8d28-263977d76585 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt | Primary-Verified; executed amendment | 2024-05-09 | Caesars Entertainment, Inc. and Term B lenders | Term B repricing and lender allocation provisions. [C4, C25] | Historical amendment; later pricing terms are in the Fifth Amendment. | Version history and amendment-mechanics trace. |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | CZR_2024_Credit_Agreement_Fifth_Amendment.txt | Primary-Verified; executed amendment | 2024-11-25 | Caesars Entertainment, Inc. and Term B / Term B-1 lenders | Later Term B and Term B-1 margin and amendment terms. [C5] | Does not establish whether later amendments exist. | Current delivered amendment sequence. |
| 13a99137-9563-4f67-9e21-c7e195278e82 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | Primary-Verified; executed indenture | 2024-02-06 | CEI and subsidiary guarantors | Notes covenant, collateral and guarantee provisions. [C6] | Does not establish current collateral perfection or an executed current intercreditor agreement. | Legal source for note terms; no recovery amount inferred. |
| fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | CZR_2024_650_Notes_First_Supplemental_Indenture.txt | Primary-Verified; executed supplement | 2024-03-01 | CEI and new note guarantors | Notes amendments and guarantor additions. [C7] | Does not establish the current guarantor roll-forward. | Supplement chronology. |
| 79bf3e7f-a2b9-4029-ac75-70816dc58005 | CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | Primary-Verified; executed supplement | 2024-08-23 | CEI and new note guarantors | Further note-guarantor additions. [C8] | Does not establish current entity values or collateral status. | Supplement chronology. |
| 6eb3eaa6-a948-486f-a6dd-0ecb3c140cbd | CZR_2026_Merger_Press_Release.txt | Primary-Verified issuer announcement; supporting-only transaction context | 2026-05-28 | Caesars and transaction parties | Proposed transaction announcement. [C9] | Not an executed financing instrument and does not replace the complete merger agreement. | Dated event context only. |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | CZR_2026_Merger_Agreement_8K.txt | Primary-Verified for filed narrative | Report date 2026-05-27; filed 2026-05-28 | CEI, Fertitta entities and transaction parties | Merger summary, commitment-letter existence and exhibit index. [C10, C23, C24] | Complete commitment-letter terms and merger schedules are absent from the delivered representation. | Separate transaction overlay; not Q2 debt or refinancing capacity. |

#### T5B.2 — Top 5 Material Credit Drivers

| Rank | Credit Driver | Originating Module | Source-Supported Basis | Why Material | Committee Relevance | Source Trace | Limitation |
|---:|---|---|---|---|---|---|---|
| 1 | Reported cash and borrowing capacity | CP-2 / CP-2D | Cash was $965m; reported aggregate cash and borrowing capacity was $2,928m. [C11, C12] | Liquidity is the available buffer against operating and contractual uses. | Does not establish a forward runway or cross-entity availability. | CZR_Q2_2026_10Q.txt, pp. 2, 22. | Consolidated total; future uses and entity access are unconfirmed. |
| 2 | 2028 refinancing concentration | CP-3C | The Q2 schedule reports $767m of 2028 principal maturities; the 2028 total debt-service estimate is a different measure. [C13, C31] | A maturity requires repayment or replacement and can increase external funding dependence. | Current execution cost and takeout access are not established. | CZR_Q2_2026_10Q.txt, p. 9. | No current instrument-level quotes or lender indications. |
| 3 | Q2 earnings and margin pressure | CP-2 / CP-1 | Q2 revenue was $2,993m versus $2,907m; Q2 Adjusted EBITDA margin was 30.7% versus 32.9%; Las Vegas Adjusted EBITDA was $410m versus $469m. [C14, C15, C28] | Lower earnings with fixed obligations can weaken debt-service capacity and cash conversion. | Monitor like-for-like operating trends; Windsor consolidation affects comparability. | CZR_Q2_2026_10Q.txt, pp. 2, 18, 20. | Adjusted EBITDA is non-GAAP and is not a liquidity measure. |
| 4 | Covenant compliance is not measured headroom | CP-4 / CP-1 | The issuer reports compliance; the delivered credit agreement states 6.50x leverage and 2.00x fixed-charge coverage thresholds for relevant covenant tests. [C16, C26, C27] | A threshold and a point-in-time compliance statement do not give actual cushion or remaining basket usage. | Exact covenant capacity is not calculable from the supplied evidence. | CZR_Q2_2026_10Q.txt, p. 23; conformed Credit Agreement, p. 58. | Current certificate, covenant EBITDA bridge and usage tracker absent. |
| 5 | Refinancing execution and transaction financing uncertainty | CP-3C / CP-2 | Executed transaction debt commitment letters are reported as delivered, but complete terms are not in the delivered evidence; the Q2 filing identifies the proposed transaction and conditions. [C23, C24] | A funding delay or unavailable takeout could increase refinancing dependence. | Keep transaction financing separate from Q2 balances and the standalone refinancing assessment. | CZR_2026_Merger_Agreement_8K.txt, pp. 2–3. | No current market pricing, full financing terms or sponsor-support analysis. |

#### T5B.3 — Traceability Map

| Credit Driver / Conclusion | Originating Module | Source Evidence | Citation Present? | Source Quality | Classification | Claim Status | Confidence Level | Traceability Status |
|---|---|---|---|---|---|---|---|---|
| Q2 cash and reported aggregate borrowing capacity | CP-2 / CP-2D | Q2 cash and capacity tables. [C11, C12] | Partial | Primary-Verified | Directly Sourced | Supported | Medium | Committee-Ready |
| 2028 scheduled principal concentration | CP-3C | Q2 annual maturity schedule; CP-3C analysis contains unqualified citation ranges requiring correction. [C13] | Partial | Primary-Verified | Directly Sourced | Supported | Medium | Remediation Needed |
| Q2 EBITDA margin and Las Vegas EBITDA declined year over year | CP-2 / CP-1 | Q2 operating and segment tables. [C14, C15, C28] | Yes | Primary-Verified | Directly Sourced | Supported | High | Committee-Ready |
| Current covenant headroom is not established | CP-4 / CP-1 | Covenant compliance statement and executed test thresholds; no current test calculation in the accepted handoffs. [C16, C26, C27] | Partial | Primary-Verified | Insufficient Information | Insufficient Information | Low | Remediation Needed |
| Current market access and full merger financing terms | CP-3C / CP-2 | Commitment-letter existence is reported; full terms and instrument-specific current market evidence are not delivered. [C23, C24] | Partial | Primary-Verified for filed narrative | Insufficient Information | Insufficient Information | Low | Not Traceable — required inputs not supplied. |

#### T5B.4 — Source Lineage Register

| Statement | Source Path | Source File | Source Document ID | Page / Section | Module Section | Type | Source Quality | Notes |
|---|---|---|---|---|---|---|---|---|
| Reporting period is Q2 2026, quarter ended June 30. [C1] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 1 | CP-1 / CP-2 / CP-2D / CP-3C | Sourced | Primary-Verified | Reporting-date anchor. |
| June 30 cash and cash equivalents were $965m. [C11] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 2 | CP-2 / CP-2D | Sourced | Primary-Verified | Balance-sheet amount, not a forecast. |
| Reported cash and borrowing capacity totaled $2,928m. [C12] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 22 | CP-2 / CP-2D | Sourced | Primary-Verified | Issuer-reported aggregate; access perimeter remains qualified. |
| The Q2 debt schedule reports $767m of 2028 annual maturities. [C13] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 9 | CP-3C | Sourced | Primary-Verified | Do not substitute total debt service for principal. |
| Q2 Adjusted EBITDA margin was 30.7% versus 32.9%. [C14] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 18 | CP-1 / CP-2 | Sourced | Primary-Verified | Issuer non-GAAP margin. |
| Q2 Las Vegas Adjusted EBITDA was $410m versus $469m. [C15] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 20 | CP-2 / CP-4 / CP-3C | Sourced | Primary-Verified | Segment driver; not a forward estimate. |
| Q2 filing reports covenant compliance. [C16] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 23 | CP-1 / CP-2 / CP-4 | Sourced | Primary-Verified | Does not state headroom. |
| The credit agreement states the relevant 6.50x and 2.00x thresholds. [C26, C27] | Delivered evidence; filesystem path not supplied | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | 58 | CP-4 | Sourced | Primary-Verified | Thresholds do not establish current test ratios or capacity. |
| The debt note and balance sheet present different Q2 carrying totals. [C18, C19, C20] | Delivered evidence; filesystem path not supplied | CZR_Q2_2026_10Q.txt | 743e5d19-d65d-4487-8114-c0614dfc076d | 2, 9 | CP-1 / CP-2 / CP-2D / CP-3C | Conflicting | Primary-Verified | Preserve the $11,705m note book value and $11,699m balance-sheet sum; no reconciliation supplied. |
| The conformed credit agreement contents identify an intercreditor agreement as a form. [C22] | Delivered evidence; filesystem path not supplied | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | 8 | CP-4 / CP-3C | Sourced | Primary-Verified | Form reference does not establish an executed current agreement. |
| The Form 8-K reports executed merger financing commitment letters. [C23] | Delivered evidence; filesystem path not supplied | CZR_2026_Merger_Agreement_8K.txt | e909b0a2-f120-42de-8cf4-4f63b2acc275 | 2 | CP-0 / CP-2 / CP-3C | Sourced | Primary-Verified for filed narrative | Full terms are absent from the delivered evidence. |
| CP-1 model account translates a source dash into numeric zero for FY2023 Corporate and Other. [C21] | Accepted handoff; no filesystem path supplied | CZR_CP-1_20261002.md | a412c541834dd7643188444e637ba16543096bf4686d71c334f32b4a53e19a67 | T4.16, model segment schedule | CP-1 T4.16 | Weak Lineage | Primary-Verified source; defective handoff encoding | Source line displays a dash; zero is not supported. |

#### T5B.5 — Calculation and Assumption Register

| Item | Where Used | Source Inputs / Assumption | Formula or Logic | Status | Claim Status | Confidence Level | Credit Relevance | Source Trace |
|---|---|---|---|---|---|---|---|---|
| Q2 balance-sheet carrying debt | CP-1; downstream leverage inputs | Current debt $114m and long-term debt $11,585m. [C19, C20] | $114m + $11,585m = $11,699m. Note book value is $11,705m; $6m difference remains unresolved. [C18] | Calculated | Partially Supported | Medium | Leverage and refinancing | CZR_Q2_2026_10Q.txt, pp. 2, 9. |
| Q2 reported cash and borrowing capacity | CP-2D liquidity table | $965m cash, $2,130m CEI capacity, $25m CVA capacity and deductions of $96m, $40m and $56m. [C11, C12] | $965m + $2,130m + $25m − $96m − $40m − $56m = $2,928m; arithmetic agrees with issuer-reported total. Entity access is not established by the sum. | Calculated | Supported as issuer-reported aggregate; not proof of fungible access | Medium | Liquidity | CZR_Q2_2026_10Q.txt, pp. 2, 22. |
| Q2 FCF and leverage ratios | CP-1 / CP-2 / CP-2D | FCF formula, aligned period denominator and covenant EBITDA bridge are not supplied in the accepted handoffs. | Required numerator, denominator/period alignment and source-supported normalization are incomplete. | Not Calculable | Insufficient Information | Low | Liquidity, debt service and leverage | Q2 CFO and capex are reported separately; no supported FCF or leverage output is carried here. |
| Covenant headroom | CP-4 / CP-3C | Contractual thresholds and reported compliance are present; current certificate, covenant EBITDA calculation and basket use are absent. [C16, C26, C27] | Not Calculable from Provided Materials — current tested ratios and usage are missing. | Not Calculable | Insufficient Information | Low | Covenant capacity and refinancing | CZR_Q2_2026_10Q.txt, p. 23; conformed Credit Agreement, p. 58. |
| Consensual refinancing working path | CP-3C | Conditional working assumption; market prices, lender indications and complete financing terms are absent. [C13, C23, C24] | Scenario label only; no probability, execution price or market-access calculation is supported. | Assumption-Based | Partially Supported as a qualified working path | Low | Refinancing and monitoring | CZR_Q2_2026_10Q.txt, p. 9; CZR_2026_Merger_Agreement_8K.txt, pp. 2–3. |

#### T5B.6 — Missing Citation and Weak-Lineage Flags

| Severity | Conclusion | Issue | Classification | Why It Matters | Required Remediation | Affected Output / Export Record |
|---|---|---|---|---|---|---|
| Material | CP-1 T4.16 FY2023 Corporate and Other value | The source displays a dash, while the model account records numeric zero and labels it reported as dash. [C21] | Weak Lineage | Treating an unavailable value as zero breaks the evidence chain and can affect structured downstream comparisons. | Restore a null / dash value with the row retained; rerun affected interface validation. | CZR_CP-1_20261002.md, T4.16 and any dependent model export. |
| Material | CP-3C Analysis citation ranges | Bare or range-style references such as C2-C13 and C23-C29 do not individually resolve to qualified citation markers in the accepted citation register. The underlying maturity evidence is directly located. [C13] | Weak Lineage | A reader cannot reliably map each statement to its native source citation. | Replace the ranges with the exact qualified markers for each supported claim; retain the underlying source locators. | CZR_CP-3C_20261002.md, Analysis and Evidence Trace. |

#### T5B.7 — Auditability Assessment

| Auditability Dimension | Assessment | Evidence | Risk Mechanic | Credit Implication | Remediation Needed |
|---|---|---|---|---|---|
| Source coverage | Ready with Remediation | Primary Q2 and audited FY2025 filings and executed credit documents are represented; current market evidence and complete transaction financing terms are absent. [C1, C2, C23, C24, C29] | Missing financing and market inputs prevent validation of refinancing execution cost and access. | Refinancing conclusions remain conditional; committee use is restricted. | Obtain current instrument-level market evidence, complete executed financing documents and required current legal schedules. |
| Citation completeness | Ready with Remediation | Most material factual claims map to delivered filing lines; CP-3C contains unqualified citation ranges; CP-4 citation-register entries C4, C12, C21 and C24 and CP-3C C30 are host-listed as unverified. [C13, C15, C22] | Unverified or non-resolving markers weaken claim-to-source auditability. | Do not treat those markers as verified support; re-anchor affected claims to located source text. | Repair CP-3C citation syntax and recheck unverified source locators. |
| Calculation traceability | Ready with Remediation | Carrying debt sums to $11,699m from balance-sheet components; note book value is $11,705m. The dash-to-zero model encoding is identified. [C18, C19, C20, C21] | Conflicting debt bases and a false zero can distort ratios or structured inputs. | Leverage and covenant capacity remain unavailable; affected model data should not be consumed unchanged. | Reconcile the debt presentation; preserve the source dash as null and rerun the affected interface. |
| Assumption transparency | Committee-Ready | CP-3C labels consensual refinancing as a conditional working path and discloses missing market, forecast and sponsor inputs. [C13, C23, C24] | Explicit qualifications prevent the path assumption from being mistaken for a market-supported forecast. | Use only as a scenario label; no probability or price conclusion is cleared. | Maintain the qualification and update only when direct evidence is supplied. |
| Markdown/export artifact integrity | Ready with Remediation | The delivered upstream artifacts contain the canonical six H2 headings and matching issuer/module/date filenames; CP-1 null handling and CP-3C marker syntax still require correction. [C1, C11, C13, C21] | Downstream readers can ingest the handoffs, but defective values and citations weaken reliability. | Downstream use is restricted until identified corrections are made. | Correct the two material findings and rerun host validation after this response. |

#### T5B.8 — Gaps Ledger

| Gap ID | Gap | Missing Evidence / Citation | Why It Matters | Impact on Output | Consequence for Confidence | Required Follow-Up Source |
|---|---|---|---|---|---|---|
| CP-5-GAP-001 | Current refinancing-market evidence | Dated, instrument-specific price, yield, spread and lender indications are not in the admitted source set. | Without execution evidence, maturity pressure cannot be translated into takeout cost or reliable access. | Top 5 driver 2; T5.2/T5.5 market review; overall view. | High | Current lender/market source for CEI facilities and relevant notes; owner: source provider / CP-3C consumer. |
| CP-5-GAP-002 | Complete merger financing package | Form 8-K reports executed commitment letters, but the full commitment terms and merger schedules are not in the delivered representation. [C23, C24] | The transaction could alter funding requirements; commitment existence alone does not establish terms or standalone refinancing availability. | Top 5 driver 5; transaction overlay and refinancing conclusions. | High | Complete executed commitment letters, merger agreement schedules and definitive financing documents; owner: source provider / CP-3C. |
| CP-5-GAP-003 | Current covenant calculations and basket usage | Current compliance certificate, covenant EBITDA bridge, test ratios and debt / lien / RP / investment usage tracker are absent. [C16, C26, C27] | Reported compliance and contractual thresholds do not establish headroom or remaining capacity. | Top 5 driver 4; CP-4 capacity and CP-3C refinancing analysis. | High | Current compliance certificate, covenant calculation schedules and usage tracker; owner: source provider / CP-4. |
| CP-5-GAP-004 | Executed current intercreditor and complete legal schedules | The delivered credit agreement contents identify a form of intercreditor agreement; current executed ICA, joinders and relevant schedules are not supplied. [C22] | Enforcement control, turnover and current collateral-sharing terms cannot be established from a form reference. | CP-4 structural findings and any recovery-control conclusion. | High | Executed current intercreditor agreement, joinders, current collateral / guarantor schedules and all later credit amendments; owner: source provider / CP-4. |
| CP-5-GAP-005 | Debt-basis reconciliation | Q2 debt-note book value is $11,705m, while balance-sheet current plus long-term debt is $11,699m. [C18, C19, C20] | The difference affects comparability and would flow into any debt ratio; upstream modules appropriately do not silently reconcile it. | T5B.5; downstream leverage and model inputs. | Medium | Issuer debt reconciliation and current facility schedule; owner: issuer/source provider / CP-1. |
| CP-5-GAP-006 | Script-owned FCF, LTM and leverage outputs | Accepted CP-1 handoff records these values as null / not calculable; no computed outputs are present. | Cash conversion, leverage and runway cannot be reproduced from the handoffs as delivered. | CP-2, CP-2D and refinancing analysis. | High | Complete source inputs and governed calculation outputs with formula, period, units and source trace; owner: CP-1 / source provider. |
| CP-5-GAP-007 | Source-row null and citation syntax defects | CP-1 T4.16 records a source dash as zero; CP-3C uses unqualified citation ranges. [C13, C21] | These defects make one structured value false and leave some refinancing statements difficult to trace. | CP-1 structured interface and CP-3C Analysis / Evidence Trace. | Medium | Corrected CP-1 and CP-3C canonical handoffs with repaired null and marker lineage; owner: originating modules. |

#### T5.1 — Input Module Register

| Module | Handoff canonical `.md` / run_id | Scope | Source Quality | Envelope / Headings Status | QA Status | Notes |
|---|---|---|---|---|---|---|
| CP-0 | CZR_CP-0_20261002.md / COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | Q2 2026 readiness | Primary filings and executed documents; source-limited | Envelope and six canonical H2 headings present | Restricted | Full underwriting set, market and transaction evidence gaps disclosed. |
| CP-1 | CZR_CP-1_20261002.md / COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | Q2 2026 data foundation | Primary-Verified filings; source-limited | Envelope and six canonical H2 headings present | Restricted | Debt basis conflict and script-owned nulls disclosed; one dash is rendered as zero in T4.16. [C18, C19, C20, C21] |
| CP-4 | CZR_CP-4_20261002.md / COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | Q2 2026 legal/covenant interpretation | Executed agreement and indenture; incomplete schedules | Envelope and six canonical H2 headings present | Restricted | Capacity, usage and executed intercreditor gaps are explicitly stated. [C22, C26, C27] |
| CP-2 | CZR_CP-2_20261002.md / COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | Q2 2026 fundamental analysis | Primary filings; incomplete transaction/market pack | Envelope and six canonical H2 headings present | Restricted | FCF, leverage and current market access are not claimed as calculated. |
| CP-2D | CZR_CP-2D_20261002.md / COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | Q2 2026 liquidity bridge | Primary interim filing; partial forward inputs | Envelope and six canonical H2 headings present | Restricted | Twelve-month forecast and entity-level access are expressly limited. [C11, C12, C17] |
| CP-3C | CZR_CP-3C_20261002.md / COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671 | Q2 2026 refinancing/LME risk | Primary debt/legal sources; no current market package | Envelope and six canonical H2 headings present | Restricted | Maturity data present; some Analysis references are unqualified ranges. [C13, C23, C24] |
| CP-5A | [Insufficient Information] — no separate prior CP-5A artifact delivered | Absorbed QA phase in this CP-5 run | Not Available — no separate artifact | Not applicable to this consolidated artifact | Not available as an upstream artifact | CP-5A severity audit is completed within this single handoff; no separate prior output is asserted. |

**Module Status:** Ready with Limitations. At least one substantive module handoff is available and the accepted substantive outputs match CZR, the selected run and Q2 2026. **Traceability Scope:** Top 5. The limitation is source completeness and restricted upstream status, not an identity mismatch. No external research or retrieval was used.

#### T5.2 — Citation and Evidence Support Audit

| Severity | Module | Claim / Section | Evidence Status | Issue | Required Fix | Clearance Impact |
|---|---|---|---|---|---|---|
| MATERIAL | CP-3C | Analysis / citations to maturity and refinancing pathways | Partially Supported | The underlying 2028 schedule is located, but unqualified ranges such as C2-C13 and C23-C29 do not individually resolve to the qualified citation markers in the accepted register. [C13] | Replace each range with the exact module-qualified marker(s) for the supported claim and preserve the native source locator. | Restricts Committee Use |

#### T5.3 — Math / Logic / Definition Audit

| Severity | Module | Metric / Logic Issue | Formula / Definition Issue | Source Conflict | Required Fix | Clearance Impact |
|---|---|---|---|---|---|---|
| MATERIAL | CP-1 | FY2023 Corporate and Other in T4.16 | A displayed source dash is encoded as numeric zero in the model account; the source does not report zero. [C21] | 10-K segment row displays a dash. | Render the value as null / dash, retain the row and rerun affected interface checks. | Requires Calculation Rebuild |
| MINOR | CP-2D | T2E.2 accessible revolver availability | Arithmetic for the reported aggregate is shown, but the label “accessible” is broader than the evidence because CEI and CVA facility access is not established as fungible. [C11, C12] | Source reports a consolidated total; facility perimeter caveat remains. | Label as issuer-reported aggregate after listed deductions and retain the entity-access qualification. | Formatting / Hygiene Only |

#### T5.4 — Legal / Structural Claim Audit

| Severity | Module | Legal / Structural Claim | Required Legal Source | Evidence Gap | Required Fix | Legal Review Dependency |
|---|---|---|---|---|---|---|
| MINOR | CP-4 | No clause-level overreach identified in sampled covenant and lien claims; the handoff does not infer current capacity or intercreditor control. | Executed current credit agreement, amendments, indenture and executed ICA. [C22, C26, C27] | The available credit-agreement contents identify a form of intercreditor agreement; CP-4 explicitly leaves current enforcement terms and usage unresolved. | Preserve the stated limitation; obtain the executed current ICA and usage schedules before making an enforcement or capacity conclusion. | Required for any subsequent clause-level enforcement-control conclusion; no legal conclusion is added here. |

#### T5.5 — Relative Value / Market Claim Audit

| Severity | Module | Market / RV Claim | Missing Datapoint | Evidence Gap | Required Fix | Committee Impact |
|---|---|---|---|---|---|---|
| MINOR | CP-3C | No current relative-value or trading-level conclusion is made; the refinancing path is explicitly conditional. | Dated instrument price, yield, spread and lender indications. | No such market observation is in the delivered source package; the dated maturity schedule remains supported. [C13] | Keep current market access unassessed until an instrument-specific source is supplied. | No RV label is cleared; the qualified refinancing discussion may be used with limitations. |

#### T5.6 — Cross-Module Consistency and Version-Control Audit

| Severity | Affected Modules | Data / Claim Conflict | Version Issue | Required Fix | Downstream Impact |
|---|---|---|---|---|---|
| MINOR | CP-1 / CP-2 / CP-2D / CP-3C | Q2 debt-note book value of $11,705m differs from the $11,699m sum of balance-sheet current and long-term debt; each handoff preserves the difference rather than selecting silently. [C18, C19, C20] | Same Q2 filing; not a run or period mismatch. | Retain CF-1 and obtain an issuer reconciliation before any leverage calculation. | No leverage conclusion is supplied; downstream users must preserve both bases until resolved. |

#### T5.7 — Duplication / Materiality / Committee-Readiness Audit

| Severity | Module | Issue Type | Description | Required Fix | Committee Impact |
|---|---|---|---|---|---|
| MINOR | CP-2 | Duplicative / Immaterial Content | The same earnings, liquidity and downside themes recur across the operating narrative, scorecard and framework sections. The underlying cited facts are supported, but repetition adds committee-reading noise. [C14, C15, C17] | Consolidate repeated narrative while retaining the causal chain, contrary evidence and limitations. | Presentation hygiene only; no change to the credit conclusion. |

#### T5.8 — Handoff Envelope and Evidence Trace Audit

| Severity | Module | Handoff Component | Defect | Required Fix | Downstream Handoff Impact |
|---|---|---|---|---|---|
| MINOR | CP-1 / CP-2 / CP-2D / CP-3C / CP-4 | Envelope and canonical H2 headings | Accepted handoffs show the expected envelope, issuer/module/date naming and six canonical H2 headings. The identified CP-1 null value and CP-3C citation ranges are tracked in T5.3 and T5.2 respectively; no separate filename or heading defect is identified. | Correct the two material trace/data findings before relying on affected fields; preserve the existing qualified gaps. | Restricted until source-trace and null-handling corrections are made; no validator result is asserted. |

#### T5.9 — Issue Log

| Issue ID | Severity | Module | Issue Type | Description | Required Fix | Clearance Impact | Status |
|---|---|---|---|---|---|---|---|
| CP5-001 | MATERIAL | CP-1 | Evidence Trace Defect | T4.16 records zero where the FY2023 source displays a dash, creating an unsupported numeric value in a structured interface. [C21] | Restore null / dash and rerun affected interface checks. | Requires Calculation Rebuild | Open |
| CP5-002 | MATERIAL | CP-3C | Citation Gap | Unqualified citation ranges in the Analysis do not resolve claim-by-claim to qualified native citation markers, although the underlying 2028 schedule is located. [C13] | Replace ranges with exact qualified citations and recheck each claim’s locator. | Restricts Committee Use | Open |
| CP5-003 | MINOR | CP-2 | Duplicative / Immaterial Content | Operating and downside themes are repeated across the analytical narrative and framework sections. [C14, C15, C17] | Consolidate repeated passages without changing analytical conclusions. | Formatting / Hygiene Only | Open |
| CP5-004 | MINOR | CP-2D | Formula / Definition Drift | The $1,963m calculated facility subtotal is labeled accessible despite a disclosed limitation on CEI/CVA entity access; the $2,928m aggregate arithmetic itself reconciles. [C11, C12] | Use an issuer-aggregate label and retain the entity-access caveat. | Formatting / Hygiene Only | Open |

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Q2 2026 reporting period and filing identity | [C1] | Q2 2026 Form 10-Q | 1 |
| Q2 cash and reported liquidity total | [C11, C12] | Q2 2026 Form 10-Q | 2, 22 |
| 2028 annual maturity amount and total debt service distinction | [C13, C31] | Q2 2026 Form 10-Q | 9 |
| Q2 earnings margin and Las Vegas segment trend | [C14, C15, C27] | Q2 2026 Form 10-Q | 2, 18, 20 |
| Q2 covenant status and contractual threshold context | [C16, C26, C27] | Q2 2026 Form 10-Q; conformed Credit Agreement | 23; 58 |
| Q2 debt-note versus balance-sheet carrying inputs | [C18, C19, C20] | Q2 2026 Form 10-Q | 2, 9 |
| FY2023 source dash in Corporate and Other row | [C21] | FY2025 Form 10-K | 19 |
| Merger commitment-letter existence; complete text gap | [C23, C24] | Merger Form 8-K | 2–3 |
| Credit agreement identifies an intercreditor form | [C22] | Conformed Credit Agreement | 8 |
| Historical non-pro-rata amendment allocation wording | [C25] | Fourth Amendment to Credit Agreement | 1 |

## Source Registry

| Source ID | Source file | Use in this handoff | Evidence locator basis |
|---|---|---|---|
| 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | Current financial statements, debt, liquidity, maturity, covenant, operating and transaction evidence. [C1, C11–C20, C27, C28, C30, C31] | Delivered evidence pages 1–26; source-register detail in T5B.1 and T5B.4. |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | Audited annual comparator, source-quality anchor and null-value cross-check. [C2, C21, C29] | Delivered evidence pages 1–57. |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | Executed incremental agreement and conformed credit-agreement provisions. [C3, C22, C26, C27] | Delivered evidence pages 1–67; referenced schedules and a current executed intercreditor agreement are not established. |
| 050d12fd-6a63-4d3a-8d28-263977d76585 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt | Historical executed repricing and assignment mechanics. [C4, C25] | Delivered evidence pages 1–2. |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | CZR_2024_Credit_Agreement_Fifth_Amendment.txt | Later delivered Term B / Term B-1 amendment. [C5] | Delivered evidence pages 1–3. |
| 13a99137-9563-4f67-9e21-c7e195278e82 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | Executed note indenture and clause-level source. [C6] | Delivered evidence pages 1–67; it does not itself establish the executed current ICA. |
| fdbba2a4-6e56-4f73-92c8-ff8614a9f462 | CZR_2024_650_Notes_First_Supplemental_Indenture.txt | Executed first supplement and guarantor additions. [C7] | Delivered evidence pages 1–3. |
| 79bf3e7f-a2b9-4029-ac75-70816dc58005 | CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | Executed second supplement and guarantor additions. [C8] | Delivered evidence pages 1–6. |
| 6eb3eaa6-a948-486f-a6dd-0ecb3c140cbd | CZR_2026_Merger_Press_Release.txt | Issuer announcement, supporting-only transaction context. [C9] | Delivered evidence pages 1–2; not a substitute for executed financing documents. |
| e909b0a2-f120-42de-8cf4-4f63b2acc275 | CZR_2026_Merger_Agreement_8K.txt | Filed transaction narrative and commitment-letter existence. [C10, C23, C24] | Delivered evidence pages 1–3; complete commitment terms and merger schedules are absent. |

## Gaps & Conflicts

- **CF-1 — debt basis.** The Q2 note reports $11,705m book value; balance-sheet current and long-term debt sum to $11,699m. The $6m difference remains unresolved, is preserved across the accepted handoffs and is not silently reconciled. No affected leverage ratio is cleared. [C18, C19, C20]
- **Financing and market evidence.** Executed buyer debt commitment letters are reported, but the complete terms and merger schedules are not in the delivered representation. Current, instrument-specific market quotes and lender indications are not in the admitted package. Refinancing cost, execution probability and market access remain unassessed. [C13, C23, C24]
- **Legal capacity and collateral control.** The Q2 filing reports covenant compliance, and the delivered agreement states test thresholds; current certificates, basket usage and an executed current intercreditor agreement are missing. Exact capacity, enforcement control and recovery are not inferred. [C16, C22, C26, C27]
- **Model and calculation coverage.** FCF, LTM and leverage measures recorded as unavailable in CP-1 remain unavailable here. The CP-1 dash-to-zero and CP-3C citation syntax defects are open issues, not grounds to invent or repair upstream source facts. [C13, C21]
- **Subsequent event.** The Alberta launch on July 13, 2026 is after the June 30 reporting date and is excluded from Q2 figures. [C30]

## QA Validation

- **Identity and lineage:** PASS — accepted upstream handoffs match CZR, the run ID and Q2 2026; the exact upstream SHA-256 values are retained in front matter.
- **Source gate:** READY WITH LIMITATIONS — multiple substantive module handoffs and delivered source evidence are available; market, transaction, covenant-usage and current intercreditor gaps remain.
- **Register coverage:** PASS — T5B.1–T5B.8 and T5.1–T5.9 are present with their declared columns and at least one body row each.
- **Trace and calculation audit:** RESTRICTED — CP-1 T4.16 renders a source dash as zero; CP-3C uses unresolved citation ranges. Both are open MATERIAL findings. The debt-basis difference is retained rather than reconciled.
- **Legal and market discipline:** PASS WITH LIMITATIONS — no exact legal capacity, recovery amount, current relative value or market access conclusion is asserted from missing inputs; source gaps are stated.
- **Null and period discipline:** PASS WITH LIMITATIONS — the CP-1 null-to-zero defect is flagged for correction; the post-period Alberta launch is not blended into Q2 values.
- **Confidence and status:** PASS — score 16, band Insufficient Information, qa_status Restricted and committee_status Restricted follow the stated partial source gate and issue count.
- **Filename and heading self-check:** PASS — canonical filename is `CZR_CP-5_20261002.md`; the six required H2 headings appear once and in order; Analysis begins with the required H3 and a conclusion-first view before any table.
- **Host validation:** Pending after this response. Host validation and register completeness checks follow this answer; no result, exit status or finding from those checks is asserted.