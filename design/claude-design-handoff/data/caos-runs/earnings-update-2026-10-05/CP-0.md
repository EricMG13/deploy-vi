---
module_id: "CP-0"
module_name: "SourceReadiness"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "EARNINGS_UPDATE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-0-f7e462bace2a2451"
credit_os_route_node_id: "RN-FULL_CREDIT_32-EARNINGS_UPDATE-01-CP-0"
credit_os_invocation_sha256: "37ef1f015c999fc80c686c4801271fdec16febf40ac0297a5eb80f830466fab1"
upstream_artifacts_used: []
confidence_score: 59
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY]
validation_warnings: [MATERIAL_SOURCE_GAPS_RECORDED, DEGRADED_VISUAL_CONTENT_NOT_REQUIRED_FOR_EARNINGS_UPDATE]
downstream_consumers: [CP-1, CP-1B, CP-2, CP-5]
---

## Audit Summary

- **Module / owned object:** CP-0 SourceReadiness / `source_readiness_register`.
- **Canonical filename:** `CZR_CP-0_20261002.md`.
- **Status:** Restricted; source evidence supports the selected earnings-update route, but current market evidence and complete executed financing documents are not included.
- **Confidence:** 59 / Low. The score is capped at 59 because material evidence limitations remain; QA status is Restricted.
- **Committee status:** Requires More Work. No credit conclusion, legal interpretation, or investment opinion is made.
- **Next action:** Run CP-1 first, then follow the T8 sequence; run CP-5 after the analytical outputs exist.

## Analysis

### Analytical read-through

Caesars’ Q2 2026 earnings update is supported by an issuer earnings release, a June 30 Form 10-Q and audited FY2025 Form 10-K; the filings anchor period figures and the release corroborates them. Reported consolidated Adjusted EBITDA was $920 million versus $955 million a year earlier [C1], with quarter/YTD statements, cash flows, segment data and debt disclosures available for downstream review [C5, C6]. Coverage supports CP-1, CP-1B and CP-2 with limitations: current market/ratings evidence and complete executed financing documents are not in the pack, and visual content is absent from two text extractions. The 10-Q separately identifies a July Alberta launch after quarter-end [C17]. This is a source-readiness assessment, not a credit conclusion. Run CP-1 first, then CP-1B and CP-2 in route order; CP-5 follows the analytical outputs.

**Preparation summary.** The host preparation record identifies three whole-source deliveries. P3 and P5 below cover each source once. The release extraction is complete; the 10-Q and 10-K extractions are usable with stated visual-content limitations. The available source text preserves the reported statements, operating and segment disclosures, debt and liquidity information, and transaction-related discussion needed to begin the selected earnings-update workflow. No source is represented as independently retrieved or externally verified in this run. The original remains the authority; each host extraction is the sole active content representation. No blocked parse or silent original fallback was identified.

**Source hierarchy and scope.** The 10-Q and audited annual filing are primary filings; the issuer earnings release is corroborative issuer material. The 10-Q covers the quarter ended June 30, 2026 [C2]; the annual filing covers FY2025 [C3] and reports audited financial statements [C4]. The quarterly report and release agree on reported consolidated Adjusted EBITDA for the quarter and six-month period [C1, C5]. The 10-Q carries the more complete statement, cash-flow, debt, covenant and segment disclosures, so the release should not replace it as the governing source for detailed financial work.

**Evidence coverage and limitations.** Revenue, segment performance, cash flow, debt, liquidity, contract liabilities and the proposed transaction are represented. The 10-Q describes a post-quarter Alberta launch, which must remain a flagged subsequent event rather than be blended into Q2 [C17]. The reported Q2 and YTD views must remain distinct. Comparability also requires attention: Caesars Windsor’s operations moved into Regional beginning March 3, 2026 [C20]. The release and 10-Q report Las Vegas weakness while Regional results strengthened; the Regional increase is attributed partly to the Caesars Windsor consolidation and event-related visitation [C10, C11]. This is a contrary operating signal to broad-based deterioration. It would be more persuasive as a durable offset if subsequent periods showed sustained performance on a comparable, same-perimeter basis; the current source set cannot establish that.

**Source-level risk and downstream implication.** The 10-Q reports $965 million of cash and cash equivalents at June 30 [C7], while the debt schedule presents debt figures under face-value and book-value headings [C8, C9]. Downstream analysis should preserve those bases and use balance-sheet carrying values for canonical debt metrics; the source-level figures must not be silently conflated. The filing separately reports estimated remaining-2026 debt service and lease payments [C14, C15], and states covenant compliance as of June 30 [C16], but does not provide the full executed financing documents or calculated covenant headroom in this pack. Those gaps limit the legal-term and capacity evidence downstream can test. Adjusted EBITDA is expressly not a liquidity measure [C19]; cash flow and debt/lease requirements therefore remain separate evidence demands.

The 10-Q also reports an increase in customer deposits and other deferred revenue from January to June 2026 [C13]. This is a relevant non-debt funding liability and operating obligation for downstream review, not ordinary accounts payable. The filing explains the customer-related obligations and expected recognition; CP-0 makes no adjustment or liquidity calculation.

**Preparation and readiness determination.** T1 records the selected earnings-update objective and preparation checks. P3 and P5 each contain one row for every source named by the host preparation record. T2-T6 record authority, quality, content mapping, gaps and evidence trace; T7 records the run index. The next-module verdicts and exact commands appear once in T8 below. Missing current market/ratings evidence and complete executed financing documents are limitations, not grounds to block consumers that can proceed while recording gaps. No research question requiring CP-DR is identified in the delivered evidence.

### Analytical appendix — complete canonical registers

#### P3 — Input Sources

| Source ID | Logical source ID | Filename | Content-identified entity, title and family | Reporting period / as-of date | Filing, signing or effective date | Version status and relationships | Content locator / evidence |
|---|---|---|---|---|---|---|---|
| 4700da60-4659-40e9-812a-9d9d3a2ef533 | 4700da60-4659-40e9-812a-9d9d3a2ef533 | CZR_Q2_2026_Earnings_Release.txt | Caesars Entertainment, Inc.; Reports Second Quarter 2026 Results; issuer earnings release | Three and six months ended June 30, 2026 | July 28, 2026 | Issuer release; separate, contemporaneous source, not a duplicate of the 10-Q; corroborative to the filing | Release identifies the reported Q2 results and reporting date [C23] |
| 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | CZR_Q2_2026_10Q.txt | Caesars Entertainment, Inc.; Form 10-Q; quarterly filing | Quarterly period ended June 30, 2026; comparative quarter and six-month periods | Signed July 28, 2026 | Filed quarterly report; current-period primary filing; identifies FY2025 10-K as annual context and merger agreement as a separate referenced document | Registrant and period identified in filing [C2] |
| 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | CZR_FY2025_10K.txt | Caesars Entertainment, Inc.; Form 10-K; annual filing with audited financial statements | Fiscal year ended December 31, 2025, with comparative annual periods | Signed February 17, 2026 | Prior-period primary annual filing; not superseded for FY2025; provides the annual baseline and background referenced by the 10-Q | Reporting period [C3]; audited financial-statement opinion [C4] |

**P3 verification:** Inventory completeness PASS against the host preparation record; identity/period/version map PASS; duplicate and amendment handling PASS. No contained duplicate, amendment, waiver or supplement was identified among the three retained sources. The release and filings are separate evidence classes and remain separate sources.

#### P5 — Parse Jobs

| Source ID | Extractor / version | Delivery and mode | Parse status | Extraction confidence | Coverage | Fidelity limitations and downstream effect | Active representation |
|---|---|---|---|---|---|---|---|
| 4700da60-4659-40e9-812a-9d9d3a2ef533 | caos.plain-text v4 | WHOLE; HYBRID (layout text and tables) | COMPLETE | High | Evidence pages 1–4 | No specific loss or locator defect is evident in the delivered release text; reported results, tables, notes and narrative are represented. | Host extraction; original release remains authority |
| 8ed97f97-6f3e-411f-902d-955cf70fbb90 | caos.plain-text v4 | WHOLE; HYBRID (layout text and tables) | DEGRADED | High for retained text | Evidence pages 1–26 | The text refers to a Caesars Digital footprint map, but the map itself is not represented [C21]. No map-only data is treated as available. Financial statements, debt, cash flow, notes, segment tables and MD&A remain usable for the earnings-update route. | Host extraction; original filing remains authority |
| 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | caos.plain-text v4 | WHOLE; HYBRID (layout text and tables) | DEGRADED | High for retained text | Evidence pages 1–57 | The text refers to a stock-performance graph, but its graphical series are not represented [C22]. No performance-graph values are treated as available. Audited statements, notes, debt, lease and annual operating disclosures remain usable for the annual comparison. | Host extraction; original filing remains authority |

**P5 verification:** Extraction fidelity and locator/coverage integrity PASS with the visual limitations above. Statuses describe the prepared representations, not original-source authority. The host preparation record holds hashes, paths, package and active-representation metadata; CP-0 records no independent result for those host-owned checks.

#### T1 — Input Gate

| Gate field | Finding | Result | Basis / limitation |
|---|---|---|---|
| Objective | Assess whether the effective source set supports FULL_CREDIT_32 EARNINGS_UPDATE work for the issuer-reported Q2 2026 results | PASS | With no separate user objective supplied, use the selected pathway’s earnings-update purpose. |
| Issuer and period | Caesars Entertainment, Inc. (CZR); Q2 2026 ended June 30, 2026 | PASS | Filing period confirmed in P3 [C2]. |
| Preparation record and order | Host preparation record is the preparation record; preparation performed before readiness | PASS | P3 and P5 each cover all three named sources. |
| Source identity and version | One release, one Q2 10-Q and one FY2025 10-K; each retained separately | PASS | No duplicate replacement or collapsed document family identified. |
| Locator and representation coverage | All three source rows have a corresponding P5 row; active content is the host extraction | PASS WITH LIMITATIONS | Visual map and stock-performance graph are not represented in two text extractions [C21, C22]. |
| Source sufficiency for selected route | Sufficient to begin CP-1, CP-1B and CP-2; CP-5 can follow route sequencing | READY_WITH_LIMITATIONS | Market/ratings evidence and complete executed financing documents are absent; downstream gaps are recorded in T5. |

#### T2 — Source Register

| Source ID | Original filename | Original-source authority / quality | Active-representation quality | Period and content usable | Readiness use and limitation |
|---|---|---|---|---|---|
| 4700da60-4659-40e9-812a-9d9d3a2ef533 | CZR_Q2_2026_Earnings_Release.txt | Issuer release; Secondary-Unverified; corroborative, not controlling over the filing | COMPLETE; high-confidence text and tables | Q2 and six months ended June 30, 2026; reported results, segment summary, liquidity summary and reconciliation [C1] | Usable for summary corroboration; detailed analysis should use the 10-Q. |
| 8ed97f97-6f3e-411f-902d-955cf70fbb90 | CZR_Q2_2026_10Q.txt | Quarterly filing; Primary-Unverified in this run; current-period filing authority | DEGRADED; retained financial and narrative text usable; map not represented [C21] | Q2/YTD 2026, comparative 2025, notes, MD&A, cash flow, debt, covenants and subsequent event | Principal current-period source; no external verification or full executed financing agreements supplied. |
| 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | CZR_FY2025_10K.txt | Annual filing with audited financial statements; Primary-Unverified in this run | DEGRADED; retained annual text usable; stock-performance graph not represented [C22] | FY2025 and comparative annual periods; audited statements, notes and annual MD&A [C4] | Annual comparison and background; prior-period source, not a substitute for Q2 data. |

#### T3 — Source Hierarchy

| Hierarchy tier | Source class / presence | Authority rule | Minimum missing source or coverage | Readiness effect / evidence |
|---|---|---|---|---|
| 1 | Official quarterly and annual filings: 10-Q and 10-K present | Primary filing controls reported financial statements and period detail; preserve each period and filing separately | Full executed credit/lease instruments and any current amendments are not included in the supplied pack | Supports core financial and annual comparison work; limits covenant-term verification and detailed legal-term work [C2, C3, C4]. |
| 2 | Issuer earnings release present | Official issuer summary corroborates but does not override primary filing detail | No additional release required to begin the selected earnings-update route | Useful for reported Q2 highlights and reconciliation cross-check [C1]. |
| 3 | Dated market/external evidence not present | External evidence cannot be inferred or substituted | Current security prices/yields and current rating-agency research, if required by the receiving module | Market- and ratings-dependent analysis remains limited; not a block to the earnings analysis represented by these sources. |
| 4 | User/unattributed summaries not present | Context only; never silently overrides tiers 1–3 | None required for source readiness | No user summary was used as evidence. |

#### T4 — Content-to-Module Map

| Module / capability | Effective source content | Specific evidence demand supported | Readiness effect | Limitation / source basis |
|---|---|---|---|---|
| CP-1 | Q2 10-Q statements, notes, cash flows, debt and FY2025 audited comparison; release corroborates Q2 Adjusted EBITDA | Period-labelled financial statements, reported earnings, cash flow, debt and reconciliation | READY | Use filing as primary; preserve book/face-value basis and quarter/YTD distinction [C1, C5, C6, C8, C9]. |
| CP-1B | 10-Q MD&A and segment operating data; FY2025 10-K provides annual baseline | Current-period segment drivers and reported earnings developments | READY_WITH_LIMITATIONS | Las Vegas declines and Regional improvement are both represented; the Regional comparison includes Caesars Windsor consolidation and event visitation [C10, C11, C20]. No external peer set or market data is supplied. |
| CP-2 | 10-Q cash, debt, debt service, lease-payment, covenant, working-capital and contract-liability disclosures; 10-K annual debt/lease context | Capital structure, liquidity, cash flow and covenant disclosures for current earnings review | READY_WITH_LIMITATIONS | Filing reports covenant compliance but the source pack lacks complete executed documents and calculated headroom; retain those as gaps [C13, C14, C15, C16]. |
| CP-5 | All three sources and source locators in P3/P5/T6 | Traceability review of evidence and subsequent-module outputs | READY_WITH_LIMITATIONS | Run after sequenced analytical outputs are available. Missing current market/ratings evidence remains a limitation, not a readiness dependency. |

#### T5 — Gaps and Conflicts

| Gap / conflict ID | Type | Severity | Missing evidence or unresolved basis | Affected modules | Readiness effect | Remediation / owner / status |
|---|---|---|---|---|---|---|
| G-1 | Source gap | MATERIAL | Current market prices/yields and current rating-agency evidence are not in the delivered source set. | CP-1B, CP-2, CP-5 where their workflow requires market or ratings context | READY_WITH_LIMITATIONS; do not infer market evidence | Supply dated primary or reputable market/ratings sources if needed; receiving module owner; OPEN. |
| G-2 | Source gap | MATERIAL | Complete executed credit and lease agreements, including current amendments and schedules, are not in the delivered source set. The 10-Q summarizes terms and reports covenant compliance but does not provide the full agreements or computed headroom [C16]. | CP-2, CP-5 | READY_WITH_LIMITATIONS; detailed legal-term or headroom verification remains limited | Supply current executed agreements and amendments if detailed term/headroom analysis is required; source owner; OPEN. |
| G-3 | Representation limitation | MINOR | The 10-Q text refers to a footprint map and the 10-K text refers to a stock-performance graph, but those graphical contents are absent from the text representation [C21, C22]. | CP-1B, CP-5 only if those figures become material | No block to financial statement, segment-table or earnings update work | Obtain image/figure representation only if downstream work requires it; preparation owner; OPEN, non-blocking. |
| CF-1 | Basis / definition difference | MATERIAL | The debt note presents total debt and long-term debt across face-value and book-value columns [C8, C9]; the balance sheet separately presents carrying-value debt lines. These bases must not be conflated or silently selected. | CP-1, CP-2, CP-5 | READY_WITH_LIMITATIONS until the downstream calculation states its basis | Use balance-sheet carrying value for canonical debt metrics; retain gross/face-value disclosure as a separately labelled basis; analytical owners; OPEN. |
| CF-2 | Period comparability | MATERIAL | Caesars Windsor moved from Managed and Branded to Regional beginning March 3, 2026 [C20]; Q2 Regional growth therefore is not a pure like-for-like comparison. | CP-1B, CP-2, CP-5 | READY_WITH_LIMITATIONS; preserve reported perimeter and explain comparability | Carry the reported segment/perimeter change into analysis; analytical owners; OPEN. |

#### T6 — Evidence Trace

| Evidence ID | Claim supported | Original source | Active representation | Locator | Citation marker |
|---|---|---|---|---|---|
| E-01 | Reported Q2 Adjusted EBITDA and comparison | CZR_Q2_2026_Earnings_Release.txt | Host extraction | Evidence page 1 | [C1] |
| E-02 | Q2 reporting period | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 1 | [C2] |
| E-03 | FY2025 annual period and audited-statement basis | CZR_FY2025_10K.txt | Host extraction | Evidence pages 1 and 28 | [C3, C4] |
| E-04 | Q2/YTD consolidated Adjusted EBITDA | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 16 | [C5] |
| E-05 | Six-month operating cash flow | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 4 | [C6] |
| E-06 | Cash and cash equivalents | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 2 | [C7] |
| E-07 | Debt presentation across total-debt and book-value lines | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 9 | [C8, C9] |
| E-08 | Las Vegas and Regional reported drivers | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 20 | [C10, C11] |
| E-09 | Caesars Digital quarterly driver | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 21 | [C12] |
| E-10 | Contract-liability balance at June 30 | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 11 | [C13] |
| E-11 | Estimated remaining-2026 debt service and lease payments | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 22 | [C14, C15] |
| E-12 | Reported covenant compliance as of June 30 | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 18 | [C16] |
| E-13 | Post-quarter Alberta launch, kept outside Q2 figures | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 17 | [C17] |
| E-14 | Merger agreement parties/date reference | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 5 | [C18] |
| E-15 | Adjusted EBITDA is not a liquidity measure | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 21 | [C19] |
| E-16 | Segment reporting transition for Caesars Windsor | CZR_Q2_2026_10Q.txt | Host extraction | Evidence page 17 | [C20] |
| E-17 | Referenced but unrepresented map and stock-performance graph | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | Host extractions | Evidence page 17 for each source | [C21, C22] |
| E-18 | Release operating-results date and quarter | CZR_Q2_2026_Earnings_Release.txt | Host extraction | Evidence page 1 | [C23] |

#### T7 — Master Index State

| Run ID | Issuer / objective / period | Preparation record | Source count and scope | Canonical handoff | Validation warnings | Downstream consumers |
|---|---|---|---|---|---|---|
| COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b | Caesars Entertainment, Inc.; EARNINGS_UPDATE; Q2 2026 | Host source preparation record; same-run P3/P5 | Three issuer sources: release, Q2 2026 10-Q, FY2025 10-K; issuer consolidated perimeter | CZR_CP-0_20261002.md | Current market/ratings and complete executed financing documents not supplied; two visual items not represented in text extractions | CP-1, CP-1B, CP-2, CP-5 |

#### T8 — Recommended Run Command Sheet

| Sequence | Module | Candidate command | Exact command | Source files to attach | Upstream handoff | Readiness | Why now / blocker |
|---:|---|---|---|---|---|---|---|
| 1 | CP-1 | Run CP-1 | Run CP-1 | CZR_Q2_2026_Earnings_Release.txt; CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | CP-0 handoff; route sequencing applies | READY | Current filing, release and audited annual comparison support earnings analysis. Preserve period and debt-basis distinctions. |
| 2 | CP-1B | Run CP-1B | Run CP-1B | CZR_Q2_2026_Earnings_Release.txt; CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | CP-0 handoff; CP-1 precedes where required by route | READY_WITH_LIMITATIONS | Segment drivers are present; account for Caesars Windsor perimeter change. No external peer or current market evidence is supplied. |
| 3 | CP-2 | Run CP-2 | Run CP-2 | CZR_Q2_2026_Earnings_Release.txt; CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | CP-0 handoff; route dependencies are sequenced separately | READY_WITH_LIMITATIONS | Liquidity, debt, cash flow and covenant disclosures are present. Full executed financing documents and calculated covenant headroom are absent; record the gap. |
| 4 | CP-5 | Run CP-5 | Run CP-5 | CZR_Q2_2026_Earnings_Release.txt; CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | CP-0 handoff; run after sequenced analytical outputs | READY_WITH_LIMITATIONS | Source trace is available now; perform downstream traceability review after the analytical artifacts exist. Market/ratings evidence remains absent if required by the review. |

## Evidence Trace

| Claim | Marker | Document | Evidence page |
|---|---|---|---:|
| Q2 Adjusted EBITDA reported below prior year | [C1] | Q2 2026 earnings release | 1 |
| Quarterly and annual filing scope | [C2, C3] | Q2 2026 Form 10-Q; FY2025 Form 10-K | 1 |
| Audited annual financial statements | [C4] | FY2025 Form 10-K | 28 |
| Q2/YTD earnings and operating cash flow | [C5, C6] | Q2 2026 Form 10-Q | 16; 4 |
| Cash and debt bases | [C7, C8, C9] | Q2 2026 Form 10-Q | 2; 9 |
| Segment trends and perimeter change | [C10, C11, C12, C20] | Q2 2026 Form 10-Q | 20; 21; 17 |
| Contract liabilities; debt service and lease obligations | [C13, C14, C15] | Q2 2026 Form 10-Q | 11; 22 |
| Covenant status and subsequent event | [C16, C17] | Q2 2026 Form 10-Q | 18; 17 |
| Merger disclosure; non-GAAP liquidity limitation | [C18, C19] | Q2 2026 Form 10-Q | 5; 21 |
| Unrepresented graphical items; issuer release date | [C21, C22, C23] | Q2 2026 Form 10-Q; FY2025 Form 10-K; Q2 release | 17; 17; 1 |

## Source Registry

The effective-source register is T2; the source hierarchy is T3. P3 identifies the three original sources and their relationships; P5 records each host extraction, delivery, status, coverage and fidelity limitation. The host preparation record remains the record for hashes, pinned originals, extraction identity and the single active representation per source. No additional source package or duplicate representation is introduced.

## Gaps & Conflicts

T5 records two material source gaps, the non-blocking visual-representation limitations, the debt-basis issue and the reported segment-perimeter change. These are carried into the affected consumer rows in T4 and T8. The reported source figures are preserved without normalization or silent reconciliation. The post-quarter Alberta launch is flagged separately in T6 and is not included in Q2-period figures. Current market/ratings evidence and complete executed financing documents are the minimum additional source categories for the identified limitations; no broader source request is made.

## QA Validation

| Check | Result | Notes |
|---|---|---|
| Preparation identity and internal phase ordering | PASS | CP-0 identity is consistent with the host-owned front matter; preparation precedes readiness. |
| Inventory coverage | PASS | P3 and P5 each cover all three sources named by the host preparation record. |
| P3 identity, period, version and duplicate handling | PASS | Filing periods and source relationships are recorded; no duplicate or amendment collapse identified. |
| P5 locator coverage and fidelity | PASS WITH LIMITATIONS | Whole-source deliveries and evidence-page coverage are recorded; referenced map and graph are disclosed as absent from text representations. |
| Quality / authority separation | PASS | Original-source authority is separated from active-representation status and fidelity. |
| Entity, period and definition fit | PASS WITH LIMITATIONS | Consolidated issuer scope and period bases are recorded; debt-basis and segment comparability issues remain explicit. |
| Gaps and conflicts | PASS | Missing sources and unresolved basis/comparability items are recorded in T5 with effect and remediation. |
| Downstream readiness and command safety | PASS | T8 contains only the four host-designated modules; non-blocking limitations are carried into the relevant rows. |
| Model-route assertion scope | NA | This is an EARNINGS_UPDATE route, not a CP-MODEL objective. |
| Canonical Markdown self-review | PASS | Required front matter, exact derived filename, six H2 headings in order, appendix heading and required registers are present in this draft. Host validation follows this answer. |

**Run status:** Restricted. **Confidence:** 59 / Low. **Host validation:** follows this answer; no host validator output or result is asserted here.