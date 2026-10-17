---
module_id: "CP-0"
module_name: "SourceReadiness"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-0-47df199733558642"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-01-CP-0"
credit_os_invocation_sha256: "5ecad4be5819e78d475017da1387e4823a14b3e372ef7ffddd44c58c454f2cbe"
upstream_artifacts_used: []
confidence_score: 56
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags:
  - SOURCE_LIMITED_NOT_COMMITTEE_READY
  - PAGE_MAP_TARGETED_LEGAL_SOURCES
  - MARKET_DATA_LAST_TRADE_ONLY
  - NO_POST_Q2_2026_FINANCIALS
validation_warnings:
  - FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED
downstream_consumers: [CP-1, CP-1A, CP-1B, CP-1C, CP-1D, CP-2, CP-2A, CP-2D, CP-2E, CP-2G, CP-2H, CP-3, CP-3C, CP-3D, CP-4, CP-4C, CP-5, CP-6]
---

## Audit Summary

Canonical handoff filename: `CZR_CP-0_20261002.md`. Source-readiness status: `READY_WITH_LIMITATIONS`; committee status: **Requires More Work**. The host preparation record identifies 20 retained originals: 17 delivered WHOLE and three delivered as PAGE_MAP. P3 and P5 below inventory each source once. Authority is attributed to originals; extraction confidence and limitations are assessed separately. No source is classified BLOCKED. Material limitations include targeted excerpts of the 2032 notes indenture, the 2024 incremental credit agreement/conformed agreement and the fund prospectus/SAI; no complete current consolidated CEI Credit Agreement or collateral/intercreditor package; no post-Q2 financial reporting; and limited, dated last-trade market observations. Automated host validation follows this handoff.

## Analysis

### Analytical read-through

The delivered evidence supports a broad, source-grounded review of Caesars’ operating history, Q2 2026 results, reported debt and liquidity, selected note terms, the pending merger, and a small set of public bond observations. It does not constitute a complete underwriting pack: the current full credit agreement and security documents are absent, some legal and fund materials are page-mapped, and the latest company financial period is June 30, 2026. Consequently, covenant capacity, full collateral coverage, current leverage definitions, and post-Q2 changes cannot be established from this set alone. The most useful counterweight to these limitations is the combination of the 2025 Form 10-K, Q2 Form 10-Q, issuer results release and executed transaction documents. Modules can proceed with explicit source limitations; this gate makes no credit, legal or investment conclusion. [C21, C22, C26]

#### Readiness implications

- **Period coverage:** The FY2025 10-K and June 30, 2026 Form 10-Q provide audited annual and unaudited interim financial information. The Q2 release supplies supplemental segment and operating context. There is no Q3 2026 filing or later operating update in the delivered set. Downstream analysis must not treat June 30 figures as October 2 figures. [C19, C4, C9]
- **Debt and legal terms:** The debt stack, selected note indenture language, the first and second supplemental indentures, fourth and fifth credit amendments, and a targeted extract of Incremental Assumption Agreement No. 3 are present. The base 2032 notes indenture is also PAGE_MAP. A complete current CEI Credit Agreement, current executed security/collateral documents, and complete intercreditor documents are not present. The 10-K describes the revolving/term-loan financial covenants and reports compliance at year-end; the Q2 10-Q reports compliance at June 30, but neither supplies a current calculation of headroom. [C1, C2, C7, C8, C16, C20, C31]
- **Amounts and definitions:** The 10-K reports $11.9 billion of indebtedness at December 31, 2025 and $1.4 billion of 2026 VICI/GLPI rent; the 10-Q reports debt-table figures and long-term financing obligations at June 30, 2026. Debt carrying value, face principal, financing obligations and rent are distinct bases and should not be merged. The downstream financial module must reconcile them using source-defined scopes. [C21, C22, C23]
- **Market context:** FINRA observations are October 1 last trades, not current bids, evaluated prices or executable quotes; the extract provides no trade size, spread or benchmark curve. A June 30 fund schedule reports a position in the 6.50% secured 2032 notes, but that valuation is not contemporaneous with the October trades. These sources support limited market context, not a complete relative-value set. [C6, C18, C27, C28, C29]
- **Transaction and subsequent-event treatment:** The May 27, 2026 merger agreement remains identified as pending in the June 30 filing. The $31.00 per-share cash consideration and conditional ticking fee are transaction terms, not a completed transaction or a change to Q2 financial results. The 10-Q records $10 million of transaction costs for the quarter and six-month period. [C10, C12, C26, C32]

The downside evidence modules may identify reported exposures and scenario pathways, but this source gate cannot determine their likelihood or quantify their effect. The first limitation to resolve is the interval after June 30: absent subsequent company filings, later operations, cash movements, debt changes and any transaction developments cannot be verified. That missing interval limits testing of current liquidity, leverage, refinancing assumptions and the status of the transaction. Request subsequent-period company reporting and a current debt/cash schedule before relying on a current-period conclusion.

#### Source hierarchy

The operative hierarchy is: (1) filed company financial reports and executed/filed legal documents for facts and contract terms; (2) issuer earnings and transaction releases for reported context, checked against filings where available; (3) FINRA fixed-income observations and fund portfolio schedules for dated, limited market evidence; and (4) no unsupported external ratings, forecasts, lender materials or market data. A release does not replace an operative agreement, and a fund’s point-in-time holding value does not replace a current market quote. [C1, C4, C7, C9, C10, C17, C18, C19]

#### Preparation and coverage

All 20 sources in the host preparation record have P3 and P5 rows. Three PAGE_MAP sources remain DEGRADED, with only the supplied leading lines per page available; they may be attached only by relevant page ranges. Whole-source plain-text extractions are treated as COMPLETE for the delivered text, with no claim that visual layout or undisplayed content was independently rechecked. Relevant table content is generally represented as text, but downstream users must preserve printed units, periods and labels. There is no evidence that an unseen or truncated passage can be recovered from this handoff. [C1, C8, C11]

The strongest contrary evidence is the breadth and recency of the filed Q2 report, supplemented by the FY2025 audited report and transaction documents. That evidence would materially improve readiness if accompanied by a complete current credit agreement and collateral/intercreditor package, later-period financials, and current market observations with trade context. Until then, proceed with limitations rather than infer missing contract terms, capacity or market levels.

**Recommended Run Command Sheet:** The T8 table below is the only command sheet. It includes every module required by this run’s register; source readiness does not imply that any analytical predecessor has already run.

### Analytical appendix — complete canonical registers

#### P3 — Input Sources

| Source ID | Logical source / identity | Date, period and version relationship | Original authority and role | Evidence |
|---|---|---|---|---|
| 07da11e7-b44f-4a94-9c85-9c6430562d11 | Caesars Entertainment, Inc. 6.500% Senior Secured Notes due 2032 indenture; base indenture | Dated Feb. 6, 2024; base agreement, later supplemented separately | Executed/filed legal instrument; PAGE_MAP | [C1] |
| 094ea5dc-87e8-47db-a292-a36e926d252d | Caesars 6.500% notes second supplemental indenture | Aug. 23, 2024; supplements the Feb. 6, 2024 indenture and March 1, 2024 first supplement | Executed/filed legal instrument; new guarantors | [C2] |
| 156bf3bf-764e-4347-b2e7-bf6f34f22220 | PENN Entertainment Q2 2026 earnings release | Quarter and six months ended June 30, 2026; peer issuer release | Issuer-reported peer context; not Caesars evidence | [C3] |
| 19774e6f-0fd1-4810-bd5e-62e5a12aca63 | Caesars Q2 2026 results release | Quarter ended June 30, 2026; related to Caesars’ Q2 filing | Issuer results release and supplemental segment evidence | [C4] |
| 1a2fe5aa-adb4-43cb-b89d-da8ec867271a | Federated Hermes Sustainable High Yield Bond Fund portfolio of investments | As of June 30, 2026; portfolio schedule, not a Caesars filing | Third-party fund holdings and point-in-time valuation evidence | [C5] |
| 1c9a98d5-e5f9-4d40-8c31-0bae81db35d1 | FINRA TRACE lookup, Caesars 6.00% Senior Notes due 2032, CUSIP 12769GAD2 | Observation Oct. 2, 2026; last trade dated Oct. 1, 2026 | Regulatory trade-summary evidence; limited market fields | [C6] |
| 41868018-6353-4359-b98f-d9d5d6d11715 | Caesars CEI Credit Agreement fifth amendment | Nov. 25, 2024; amends the July 20, 2020 credit agreement and prior amendments | Executed/filed credit amendment | [C7] |
| 51624212-915e-4c48-b500-9ecdd27a1efc | Caesars Incremental Assumption Agreement No. 3 and attached credit-agreement material | Feb. 6, 2024; $2.9 billion Term B-1 transaction; PAGE_MAP | Executed/filed financing document and partial conformed credit-agreement content | [C8] |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Q2 2026 Form 10-Q | Quarter ended June 30, 2026; filed July 28, 2026; latest delivered company interim report | Primary filed interim report and financial statements | [C9] |
| 5e8a2604-12ea-471a-bbad-4e77b04c3186 | Caesars Form 8-K and attached Agreement and Plan of Merger | Merger agreement dated May 27, 2026; Form 8-K filed May 28, 2026 | Primary filing and executed transaction agreement | [C10] |
| 5f5cc816-e7db-441a-8d72-5e0394816d92 | Federated Hermes Sustainable High Yield Bond Fund prospectus and SAI | Filed May 26, 2026; PAGE_MAP; separate from June 30 holdings schedule | Third-party fund disclosure; contextual only | [C11] |
| 80a091bf-ceb5-4bb8-9006-297fd19a762e | Full Caesars Agreement and Plan of Merger | Execution version dated May 27, 2026; separate full agreement representation to the Form 8-K | Primary executed agreement; transaction and financing covenants | [C12] |
| 88e5b11d-20a4-45c0-b091-1f43b2ef3683 | FINRA TRACE lookup, PENN 4.125% notes due 2029, CUSIP 707569AV1 | Observation Oct. 2, 2026; last trade dated Oct. 1, 2026 | Regulatory trade-summary peer evidence; limited fields | [C13] |
| 8d0ab409-cb6c-4fb7-a903-bd471f0a4f3c | Caesars merger announcement press release | May 28, 2026; announcement and transaction summary | Issuer release; secondary to executed agreement and filing | [C14] |
| af7289ac-1c03-4ad3-82a7-da794dc6dc0d | FINRA TRACE lookup, MGM Resorts 6.125% notes due 2029, CUSIP 552953CK5 | Observation Oct. 2, 2026; last trade dated Oct. 1, 2026 | Regulatory trade-summary peer evidence; limited fields | [C15] |
| b22e7b80-965b-476a-abd7-7530b03bd0a7 | Caesars 6.500% notes first supplemental indenture | Mar. 1, 2024; amends Permitted Liens and defeasance text and adds CIENJ and Tropicana Atlantic City as guarantors | Executed/filed legal instrument; separate from base indenture and second supplement | [C16] |
| c67320d0-3458-4ee9-bc3c-e1a8bc6f3c05 | MGM Resorts Q2 2026 earnings release | Quarter ended June 30, 2026; issued July 29, 2026; peer issuer release | Issuer-reported peer operating and financial context | [C17] |
| cb0d6dd2-f997-4ab5-ab65-ca7059e97c5a | FINRA TRACE lookup, Caesars 6.500% Senior Secured Notes due 2032, CUSIP 12769GAC4 | Observation Oct. 2, 2026; last trade dated Oct. 1, 2026 | Regulatory trade-summary evidence; limited market fields | [C18] |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars FY2025 Form 10-K | Fiscal year ended Dec. 31, 2025; filed Feb. 17, 2026 | Primary audited annual report; historical baseline | [C19] |
| e24bf84e-82d3-4167-bd6f-f510b21fdd0e | Caesars CEI Credit Agreement fourth amendment | May 9, 2024; amends the July 20, 2020 credit agreement | Executed/filed credit amendment; precedes fifth amendment | [C20] |

#### P5 — Parse Jobs

| Source ID | Extractor / delivery | Pages covered in delivered representation | Parse status / confidence | Fidelity assessment and limitations |
|---|---|---|---|---|
| 07da11e7-b44f-4a94-9c85-9c6430562d11 | caos.plain-text v4 / PAGE_MAP | Pages 1–60; 32 leading lines per page; 1,915 of 3,567 lines shown | DEGRADED / Medium | Only page-leading text is active. Later text on each page and any omitted schedules or tables cannot be relied upon. Relevant excerpted provisions appear, but the full indenture is not available in the delivered representation. |
| 094ea5dc-87e8-47db-a292-a36e926d252d | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Text, parties, date, joinder provisions and Schedule A names are available. Visual formatting is not independently assessed. |
| 156bf3bf-764e-4347-b2e7-bf6f34f22220 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Earnings-release text and tables are available; peer issuer, not Caesars. |
| 19774e6f-0fd1-4810-bd5e-62e5a12aca63 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Release tables and supplemental reconciliation are represented; use with the filed 10-Q for controlling company-period figures. |
| 1a2fe5aa-adb4-43cb-b89d-da8ec867271a | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Portfolio schedule and identified holding values are represented. Valuation date is June 30, not an October executable quote. |
| 1c9a98d5-e5f9-4d40-8c31-0bae81db35d1 | caos.plain-text v4 / WHOLE | Whole delivered text; page shown in evidence | COMPLETE / High | Summary fields preserved. FINRA identifies a last trade, not bid, mid, ask or evaluated price; no trade size or spread in extract. |
| 41868018-6353-4359-b98f-d9d5d6d11715 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Amendment terms and consent mechanics represented. It is not the complete underlying credit agreement. |
| 51624212-915e-4c48-b500-9ecdd27a1efc | caos.plain-text v4 / PAGE_MAP | Pages 1–67; 24 leading lines per page; 1,605 of 3,981 lines shown | DEGRADED / Medium | Targeted page-leading text only. Full clause language, schedules and later text on pages are not assured; attached conformed credit-agreement material is partial. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Q2 statements, notes, MD&A, debt and merger disclosure represented. Interim report is unaudited and does not provide data after June 30, 2026. |
| 5e8a2604-12ea-471a-bbad-4e77b04c3186 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | 8-K summary and merger-agreement excerpt represented. Omitted schedules are not included in the evidence. |
| 5f5cc816-e7db-441a-8d72-5e0394816d92 | caos.plain-text v4 / PAGE_MAP | Pages 1–64; 49 leading lines per page; 3,133 of 3,827 lines shown | DEGRADED / Medium | Only page-leading text is active; later page text and visual chart detail may be missing. Use only identified portfolio-policy and risk disclosures. |
| 80a091bf-ceb5-4bb8-9006-297fd19a762e | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Full agreement text is represented, but schedules and disclosure schedules are not supplied with this source. |
| 88e5b11d-20a4-45c0-b091-1f43b2ef3683 | caos.plain-text v4 / WHOLE | Whole delivered text; page shown in evidence | COMPLETE / High | FINRA last-trade summary only; no bid/ask, spread, trade size or intraday timestamp. |
| 8d0ab409-cb6c-4fb7-a903-bd471f0a4f3c | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Issuer announcement and transaction summary represented; not a substitute for agreement or filing. |
| af7289ac-1c03-4ad3-82a7-da794dc6dc0d | caos.plain-text v4 / WHOLE | Whole delivered text; page shown in evidence | COMPLETE / High | FINRA last-trade summary only; comparator differs in issuer, maturity and credit structure. |
| b22e7b80-965b-476a-abd7-7530b03bd0a7 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Operative replacement language and signatures represented. Schedule of signatories is long; no visual verification asserted. |
| c67320d0-3458-4ee9-bc3c-e1a8bc6f3c05 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Peer release results and reconciliations represented; issuer-reported non-GAAP measures retain their stated definitions. |
| cb0d6dd2-f997-4ab5-ab65-ca7059e97c5a | caos.plain-text v4 / WHOLE | Whole delivered text; page shown in evidence | COMPLETE / High | FINRA last-trade summary only; no bid/ask, spread, trade size or intraday timestamp. |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Audited annual statements, notes, MD&A and debt disclosures represented. Period ends Dec. 31, 2025. |
| e24bf84e-82d3-4167-bd6f-f510b21fdd0e | caos.plain-text v4 / WHOLE | Whole delivered text; pages shown in evidence | COMPLETE / High | Amendment text and consent exhibit represented; it is a predecessor amendment, not a current full agreement. |

#### T1 — Input Gate

| Field | Value | Validation / evidence |
|---|---|---|
| Objective | FULL_CREDIT_ASSESSMENT source-readiness gate for Caesars Entertainment, Inc.; no narrower user task supplied | Selected pathway use case; source sufficiency only |
| Issuer and reporting perimeter | Caesars Entertainment, Inc. and consolidated subsidiaries; financing and note guarantors where the source defines them | Confirmed in filed report and legal documents [C9, C10] |
| Reporting period / as-of | Q2 2026; analysis date 2026-10-02 | Q2 report covers quarter ended June 30, 2026 [C9] |
| Preparation record | Host SOURCE PREPARATION record; pinned originals and extraction identities supplied by host | Record is host metadata, not citable evidence |
| Inventory completeness | PASS — 20 supplied sources represented once in P3 and P5 | All host-listed source IDs included |
| Version and amendment handling | PASS — base indenture, first and second supplements, and separate credit amendments retained as linked sources | Legal version family preserved [C1, C2, C7, C16, C20] |
| Preparation and locator status | PASS with limitation — whole sources plus three degraded page maps; no blocked source | See P5 and gap register |
| Readiness verdict | READY_WITH_LIMITATIONS | Modules may proceed with gaps explicitly carried |
| Prohibited conclusion boundary | No credit conclusion, legal interpretation or investment opinion | CP-0 source sufficiency only |

#### T2 — Source Register

| Source ID | Source / authority tier | Active representation | Relevant content | Readiness use and limitation |
|---|---|---|---|---|
| 07da11e7-b44f-4a94-9c85-9c6430562d11 | Base 2032 secured indenture / Tier 1 | Host PAGE_MAP | Definitions, selected covenants, note terms, liens and guarantee framework [C1] | Supports limited legal mapping; page-map constraint applies |
| 094ea5dc-87e8-47db-a292-a36e926d252d | Second supplemental indenture / Tier 1 | Host WHOLE | Aug. 2024 guarantor joinders [C2] | Supports guarantor-history review; does not supply collateral documents |
| 156bf3bf-764e-4347-b2e7-bf6f34f22220 | PENN Q2 release / Tier 2 peer | Host WHOLE | Peer operating and leverage context [C3] | Optional cross-check; not direct Caesars evidence |
| 19774e6f-0fd1-4810-bd5e-62e5a12aca63 | Caesars Q2 release / Tier 2 issuer | Host WHOLE | Q2 reported measures and segment context [C4] | Supplemental to 10-Q; issuer release |
| 1a2fe5aa-adb4-43cb-b89d-da8ec867271a | Fund portfolio schedule / Tier 3 | Host WHOLE | June 30 holdings, including Caesars debt [C5, C27] | Dated valuation only; not a current quote |
| 1c9a98d5-e5f9-4d40-8c31-0bae81db35d1 | FINRA Caesars unsecured bond / Tier 3 | Host WHOLE | Oct. 1 last trade and bond summary [C6, C29] | No bid/ask, size or spread |
| 41868018-6353-4359-b98f-d9d5d6d11715 | Fifth credit amendment / Tier 1 | Host WHOLE | Nov. 2024 Term B/B-1 repricing and assignment provisions [C7] | Amendment only; full current agreement absent |
| 51624212-915e-4c48-b500-9ecdd27a1efc | Incremental Agreement No. 3 / Tier 1 | Host PAGE_MAP | Term B-1 facility and partial conformed credit agreement [C8] | Detailed clauses may be absent from page-leading text |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Q2 Form 10-Q / Tier 1 | Host WHOLE | June 2026 financial statements, debt, liquidity, segment results and merger update [C9, C22, C23, C24] | Latest financial source supplied; unaudited; ends June 30 |
| 5e8a2604-12ea-471a-bbad-4e77b04c3186 | May 2026 Form 8-K / Tier 1 | Host WHOLE | Filed merger summary and excerpted agreement terms [C10, C32] | Omitted schedules not in evidence |
| 5f5cc816-e7db-441a-8d72-5e0394816d92 | Fund prospectus/SAI / Tier 3 | Host PAGE_MAP | Fund mandate, high-yield approach and risk descriptions [C11] | Not issuer credit evidence; page-map and chart limitations |
| 80a091bf-ceb5-4bb8-9006-297fd19a762e | Full merger agreement / Tier 1 | Host WHOLE | Merger mechanics, financing cooperation, restrictions and termination terms [C12] | Full agreement text; schedules absent |
| 88e5b11d-20a4-45c0-b091-1f43b2ef3683 | FINRA PENN bond / Tier 3 | Host WHOLE | Oct. 1 last trade [C13] | Peer comparison only; instrument terms not normalized |
| 8d0ab409-cb6c-4fb7-a903-bd471f0a4f3c | Caesars merger press release / Tier 2 issuer | Host WHOLE | Announced transaction and deal summary [C14] | Corroborative; agreement controls terms |
| af7289ac-1c03-4ad3-82a7-da794dc6dc0d | FINRA MGM bond / Tier 3 | Host WHOLE | Oct. 1 last trade [C15, C30] | Peer comparison only; different credit and structure |
| b22e7b80-965b-476a-abd7-7530b03bd0a7 | First supplemental indenture / Tier 1 | Host WHOLE | Mar. 2024 legal amendments and two new guarantors [C16] | Retained separately from base and second supplement |
| c67320d0-3458-4ee9-bc3c-e1a8bc6f3c05 | MGM Q2 release / Tier 2 peer | Host WHOLE | Peer operating measures [C17] | Not direct Caesars evidence |
| cb0d6dd2-f997-4ab5-ab65-ca7059e97c5a | FINRA Caesars secured bond / Tier 3 | Host WHOLE | Oct. 1 last trade and bond summary [C18, C28] | No bid/ask, size or spread |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | FY2025 Form 10-K / Tier 1 | Host WHOLE | Audited FY2025 financials, debt, leases, covenants and risks [C19, C21, C25, C31] | Historical baseline; not current-period data |
| e24bf84e-82d3-4167-bd6f-f510b21fdd0e | Fourth credit amendment / Tier 1 | Host WHOLE | May 2024 loan pricing and terms [C20] | Predecessor amendment; superseded in part by fifth amendment |

#### T3 — Source Hierarchy

| Tier | Source class and rule | Sources present | Minimum missing / readiness effect |
|---|---|---|---|
| 1 — Primary | Filed company reports and executed/filed legal documents control reported figures and operative terms | 10-K, 10-Q, indenture/supplements, credit amendments, merger agreement and 8-K [C1, C7, C9, C10, C12, C19] | Complete current credit agreement, current security/collateral and intercreditor documents, and omitted transaction schedules remain absent |
| 2 — Issuer | Releases supplement primary filings; use as company attribution, not as substitute for filed statements or contracts | Caesars, PENN and MGM earnings releases; Caesars merger release [C3, C4, C14, C17] | No lender presentation, management forecast pack or current financing presentation supplied |
| 3 — Dated market / external | FINRA last-trade summaries and fund portfolio schedule are limited dated observations; preserve date, instrument and measure | Three Caesars/PENN/MGM FINRA observations and June 30 fund schedule [C6, C13, C15, C18] | No complete quote history, bid/ask, size, spread, curve, broad peer set or current rating-agency report |
| 4 — Context only | Unattributed summaries or assumptions cannot override primary material | None used as an independent authority | No external research retrieved or assumed; no source outside the supplied pack used |

#### T4 — Content-to-Module Map

| Evidence set | Content carried | Applicable consumers | Readiness effect | Limitation |
|---|---|---|---|---|
| FY2025 10-K and Q2 10-Q | Audited annual statements, interim statements, cash flow, debt, liquidity, covenants, business narrative and segments [C9, C19, C21, C22, C24, C25] | CP-1, CP-1A, CP-1B, CP-1D, CP-2, CP-2A, CP-2D, CP-2E, CP-2G, CP-2H, CP-3, CP-3C, CP-4, CP-4C, CP-5, CP-6 | READY_WITH_LIMITATIONS | No reporting after June 30; current leverage/headroom and complete financing definitions are not calculated here |
| Caesars Q2 earnings release | Supplemental quarter and segment measures [C4] | CP-1, CP-1A, CP-1B, CP-2, CP-2A, CP-2G, CP-5, CP-6 | READY_WITH_LIMITATIONS | Cross-check against 10-Q; not a later period |
| 2032 secured indenture and supplements | Selected note and guarantor terms [C1, C2, C16] | CP-1D, CP-2D, CP-3, CP-3C, CP-3D, CP-4, CP-4C, CP-5, CP-6 | READY_WITH_LIMITATIONS | Base indenture is PAGE_MAP; complete collateral and intercreditor set absent |
| 2020 credit-agreement chain | Incremental agreement, fourth and fifth amendments [C7, C8, C20] | CP-1D, CP-2, CP-2D, CP-3C, CP-4, CP-4C, CP-5, CP-6 | READY_WITH_LIMITATIONS | No complete current conformed CEI Credit Agreement; one source is PAGE_MAP |
| Merger agreement, 8-K and release | Price, conditions, financing, covenants while pending, termination and timing [C10, C12, C14, C10] | CP-1A, CP-1D, CP-2, CP-2D, CP-2G, CP-2H, CP-3, CP-3C, CP-4, CP-4C, CP-5, CP-6 | READY_WITH_LIMITATIONS | Schedules and some financing commitment documents are absent; transaction remains pending in Q2 filing [C26] |
| FINRA and fund schedule | Selected bond trades and a June 30 bond holding [C6, C18, C27, C28] | CP-1C, CP-2H, CP-3, CP-3D, CP-5, CP-6 | READY_WITH_LIMITATIONS | Last trades and non-contemporaneous fund value do not establish executable relative value |
| Peer filings/releases | Selected PENN and MGM results and bond observations [C3, C13, C15, C17] | CP-1C, CP-2E, CP-3, CP-3D, CP-5, CP-6 | READY_WITH_LIMITATIONS | Small, non-normalized peer set; do not equate issuer, maturity or security risk |
| Fund prospectus/SAI | Investment mandate, high-yield and valuation/risk context [C11] | CP-1C, CP-3D, CP-5 | READY_WITH_LIMITATIONS | PAGE_MAP and third-party context; not a rating or Caesars credit assessment |
| Full debt and collateral details | Complete current covenants, definitions, baskets, security grants, intercreditor priority and current compliance calculation | CP-1D, CP-2D, CP-3C, CP-4, CP-4C, CP-5, CP-6 | READY_WITH_LIMITATIONS | Required evidence gap; downstream analyses must mark unavailable terms and capacity explicitly |
| Post-June operating and financing activity | Subsequent quarter statements, cash/debt movement, and transaction status after June 30 | CP-1, CP-1A, CP-1B, CP-2, CP-2A, CP-2D, CP-2G, CP-2H, CP-3, CP-3C, CP-3D, CP-5, CP-6 | READY_WITH_LIMITATIONS | Latest financial period is Q2 2026; do not extrapolate October current conditions |

#### T5 — Gaps and Conflicts

| ID | Type / severity | Evidence and issue | Affected modules / readiness effect | Remediation / owner / status |
|---|---|---|---|---|
| GAP-1 | Missing primary legal source / MATERIAL | Complete CEI Credit Agreement as currently amended is not present; delivered material includes amendment documents and a partial PAGE_MAP of the 2024 agreement [C7, C8, C20]. | CP-1D, CP-2, CP-2D, CP-3C, CP-4, CP-4C, CP-5, CP-6; retain READY_WITH_LIMITATIONS and do not infer basket capacity. | Supply complete current executed/conformed agreement and operative schedules; user/source owner; open. |
| GAP-2 | Missing primary security documents / MATERIAL | Current collateral agreement, mortgages, complete first-lien intercreditor agreement and any relevant junior-lien arrangements are absent; notes evidence describes secured status but not the complete package [C1, C16, C19]. | CP-1D, CP-3, CP-3C, CP-4, CP-4C, CP-5, CP-6; recovery/security analysis limited. | Supply current security and intercreditor documents plus current guarantor/collateral schedules; user/source owner; open. |
| GAP-3 | Missing period / MATERIAL | Latest Caesars financial statements are for the quarter ended June 30, 2026; the merger was pending at that date [C9, C26]. | All current-condition consumers, especially CP-1, CP-2, CP-2D, CP-2G, CP-2H, CP-3C and CP-6. | Supply the next available quarterly/current report and a current debt/cash schedule; user/source owner; open. |
| GAP-4 | Market observation limitation / MATERIAL | FINRA summaries label price/yield as last trades dated Oct. 1 and show no bid/ask, size, spread or benchmark curve [C6, C13, C15, C18]. | CP-1C, CP-2H, CP-3, CP-3D and CP-6; market comparisons are indicative only. | Supply contemporaneous evaluated/bid/ask prices, trade sizes, benchmark yields/spreads and a broader comparable set; user/source owner; open. |
| CF-1 | Definition / measurement-basis conflict / MATERIAL | FY2025 filings present debt face and book figures, balance-sheet debt and financing obligations as distinct measures; Q2 2026 reports later values [C21, C22, C23]. No reconciliation is made here. | CP-1, CP-2, CP-2D, CP-3C, CP-4 and CP-5; current debt and leverage must use a stated source-defined basis. | Downstream owner reconcile carrying value, principal and financing obligations to the governing definition; open. |
| CF-2 | Date-basis difference / MINOR | The fund schedule values its 6.50% Caesars secured-note holding as of June 30; FINRA records an Oct. 1 last trade [C27, C28]. These are different dates and source valuation bases, not a like-for-like quote conflict. | CP-3 and CP-3D; retain both dates, do not average or silently select. | Obtain current comparable prices and valuation timestamps; open. |
| GAP-5 | Incomplete transaction evidence / MATERIAL | Full merger agreement is available, but disclosure schedules and complete debt-financing commitment materials are not included with the supplied filings [C10, C12]. | CP-2G, CP-3C, CP-4, CP-4C, CP-5 and CP-6; transaction funding and specific schedules cannot be fully verified. | Supply executed commitment letters, fee/financing documents and relevant schedules; user/source owner; open. |
| GAP-6 | Incomplete ratings evidence / MINOR | FINRA displays selected bond ratings and rating dates, but no current issuer-level rating-agency reports or outlook rationales are supplied [C6, C15, C18]. | CP-2H, CP-3, CP-5 and CP-6; ratings migration and agency rationale remain limited. | Supply current rating-agency reports/notices if available; user/source owner; open. |

#### T6 — Evidence Trace

| Claim / evidence point | Citation marker | Original document | Locator |
|---|---|---|---|
| Base 6.50% secured notes indenture dated Feb. 6, 2024 | [C1] | Caesars 6.500% Senior Secured Notes due 2032 indenture | p. 1 |
| 2024 second supplemental indenture and guarantor joinder | [C2] | Second Supplemental Indenture | p. 1 |
| FY2025 reported debt and rent context | [C21] | Caesars FY2025 Form 10-K | p. 13 |
| Q2 debt table | [C22] | Caesars Q2 2026 Form 10-Q | p. 9 |
| Q2 financing obligations | [C23] | Caesars Q2 2026 Form 10-Q | p. 2 |
| Q2 liquidity capacity | [C24] | Caesars Q2 2026 Form 10-Q | p. 22 |
| FY2025 Adjusted EBITDA presentation | [C25] | Caesars FY2025 Form 10-K | p. 23 |
| Merger remained pending and transaction costs were recorded | [C26] | Caesars Q2 2026 Form 10-Q | p. 6 |
| June 30 value of a fund-held 6.50% Caesars secured-note position | [C27] | Federated Hermes portfolio of investments | p. 4 |
| October 1 Caesars secured-note last trade | [C28] | FINRA TRACE lookup, CUSIP 12769GAC4 | p. 1 |
| October 1 Caesars unsecured-note last-trade yield | [C29] | FINRA TRACE lookup, CUSIP 12769GAD2 | p. 1 |
| October 1 MGM peer bond last-trade yield | [C30] | FINRA TRACE lookup, CUSIP 552953CK5 | p. 1 |
| Financial covenant summary disclosed by Caesars | [C31] | Caesars FY2025 Form 10-K | p. 24 |
| Merger cash consideration and conditional ticking fee | [C32] | Caesars Form 8-K merger description | p. 1 |

#### T7 — Master Index State

| Field | State |
|---|---|
| Module / run / issuer | CP-0 SourceReadiness / COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 / CZR — Caesars Entertainment, Inc. |
| Objective / period | FULL_CREDIT_ASSESSMENT source sufficiency / Q2 2026; analysis date 2026-10-02 |
| Preparation record | Host SOURCE PREPARATION record; one active host extraction per retained original; no upstream artifact |
| Inventory / preparation | 20 source IDs; P3 = 20 rows; P5 = 20 rows; 17 WHOLE and 3 PAGE_MAP; no duplicate or amendment collapsed |
| Effective evidence families | Filed annual/interim reports; indenture and credit-document family; merger documents; issuer and peer releases; dated FINRA and fund holdings |
| QA and warnings | Source-limited; three targeted PAGE_MAP sources; full current credit agreement and security package, subsequent-period company reporting and richer market data absent |
| Handoff | CZR_CP-0_20261002.md; canonical Markdown only |
| Downstream consumers | CP-1, CP-1A, CP-1B, CP-1C, CP-1D, CP-2, CP-2A, CP-2D, CP-2E, CP-2G, CP-2H, CP-3, CP-3C, CP-3D, CP-4, CP-4C, CP-5, CP-6 |

#### T8 — Recommended Run Command Sheet

| Sequence | Module | Candidate command | Exact command | Source files to attach | Upstream handoff | Readiness | Why now / blocker |
|---:|---|---|---|---|---|---|---|
| 1 | CP-1 | Run CP-1 | Run CP-1 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_Earnings_Release.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Primary annual/interim reporting is available; Q2 is latest and not October-current. |
| 2 | CP-1A | Run CP-1A | Run CP-1A | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2026_Merger_Agreement.txt; CZR_2026_Merger_Agreement_8K.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Business, transaction and annual/interim evidence available; later-period performance and schedules absent. |
| 3 | CP-1B | Run CP-1B | Run CP-1B | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_Earnings_Release.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Historical and Q2 operating evidence available; no Q3 data. |
| 4 | CP-1C | Run CP-1C | Run CP-1C | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt; MGM_FINRA_TRACE_552953CK5_2026-10-02.txt; PENN_FINRA_TRACE_707569AV1_2026-10-02.txt; MGM_Q2_2026_Earnings_Release.txt; PENN_Q2_2026_Earnings_Release.txt; FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Limited peer evidence is present; market observations are last trades and require comparability controls. |
| 5 | CP-1D | Run CP-1D | Run CP-1D | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt page 13-14; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 22-27; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 1-2; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 9-10; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 17-24; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt page 31; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 43-53; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Legal/financing evidence is meaningful but incomplete; page-map limits and missing current security documents apply. |
| 6 | CP-2 | Run CP-2 | Run CP-2 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Filed liquidity, debt and operating history support analysis; complete current covenant calculations are absent. |
| 7 | CP-2A | Run CP-2A | Run CP-2A | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_Earnings_Release.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Historical evidence supports a bounded downside review; stress assumptions and current-period data are not supplied. |
| 8 | CP-2D | Run CP-2D | Run CP-2D | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Cash, revolver, debt service and lease disclosures are present; no current full credit agreement or post-June data. |
| 9 | CP-2E | Run CP-2E | Run CP-2E | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; MGM_Q2_2026_Earnings_Release.txt; PENN_Q2_2026_Earnings_Release.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Issuer interest-rate exposures and peer context are available; independent current macro/curve research is not supplied. |
| 10 | CP-2G | Run CP-2G | Run CP-2G | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2026_Merger_Agreement.txt; CZR_2026_Merger_Agreement_8K.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Filed outlook context and transaction terms are available; detailed company forecasts and financing commitments are absent. |
| 11 | CP-2H | Run CP-2H | Run CP-2H | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_10Q.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Some bond ratings and company evidence are available; current agency rationale and issuer-level reports are not. |
| 12 | CP-4 | Run CP-4 | Run CP-4 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt page 13-14; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 22-27; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 1-2; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 17-24; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 43-53; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_10Q.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Operative provisions are partially represented; complete current credit, collateral and intercreditor texts are missing. |
| 13 | CP-4C | Run CP-4C | Run CP-4C | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Security and guarantor evidence supports bounded review; full collateral, perfection, priority and intercreditor materials are absent. |
| 14 | CP-3 | Run CP-3 | Run CP-3 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt; MGM_FINRA_TRACE_552953CK5_2026-10-02.txt; PENN_FINRA_TRACE_707569AV1_2026-10-02.txt; CZR_Q2_2026_10Q.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35 | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Selected market and issuer facts support review; no loan-market workbook, executable quotes or full comparable set is provided. |
| 15 | CP-3C | Run CP-3C | Run CP-3C | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 17-24; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt pages 43-53; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Debt maturities, cash, revolver and amendments are available; full current legal terms and later-period data are absent. |
| 16 | CP-3D | Run CP-3D | Run CP-3D | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt; MGM_FINRA_TRACE_552953CK5_2026-10-02.txt; PENN_FINRA_TRACE_707569AV1_2026-10-02.txt; FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35 | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Dated observations support a bounded market view; valuation and trading fields are incomplete and dates differ. |
| 17 | CP-5 | Run CP-5 | Run CP-5 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2026_Merger_Agreement.txt; CZR_2026_Merger_Agreement_8K.txt; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 13-14; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35 | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Source diligence can proceed; complete agreements, schedules and subsequent-period reporting remain requested evidence. |
| 18 | CP-6 | Run CP-6 | Run CP-6 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_Earnings_Release.txt; CZR_2026_Merger_Agreement.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt page 13-14; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 22-27; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt pages 31-35; CZR_2024_Credit_Agreement_Fourth_Amendment.txt; CZR_2024_Credit_Agreement_Fifth_Amendment.txt; CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | CP-0 run COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7 | READY_WITH_LIMITATIONS | Decision workflow can record the evidence gaps; no recommendation or investment conclusion is made by CP-0. |

## Evidence Trace

The citation markers refer to exact source text in the supplied evidence and its page header. The complete short-form evidence trace is register T6 in the appendix. Source identity and period are separately recorded in P3; extraction delivery and fidelity are recorded in P5. The host preparation record, not an evidence citation, is the authority for pinned-source and extraction metadata.

## Source Registry

The complete effective-source register is T2 in the analytical appendix, with its original identity and authority cross-referenced to P3 and its one active host extraction and fidelity status cross-referenced to P5. Originals remain the authority. Whole-source host extractions are the active representations for 17 sources; the three identified PAGE_MAP extractions remain targeted and degraded. No alternative file, external source, prior handoff or unverified attachment has been substituted.

## Gaps & Conflicts

T5 records the source gaps and the one date-basis difference. The key unresolved sources are the complete current credit agreement, complete current collateral and intercreditor documents, omitted merger schedules and financing commitment materials, the next company reporting period, and a richer current market data set. The FY2025 and Q2 debt presentations include measures on different bases; downstream work must retain the face, carrying-value and financing-obligation distinctions and identify its chosen definition. June fund valuation and October last trade are not comparable observations. No conflict has been silently reconciled. [C21, C22, C23, C27, C28]

## QA Validation

| Check | Result | Note |
|---|---|---|
| Preparation identity and phase order | PASS | CP-0 preparation registers precede source-readiness registers in this single handoff. |
| Inventory coverage | PASS | Each of the 20 host-listed source IDs appears once in P3 and once in P5. |
| Version and amendment handling | PASS | Base indenture, supplements and separate credit amendments are retained and linked. |
| Locator and coverage integrity | PASS WITH LIMITATIONS | Whole-source rows preserve delivered text; three PAGE_MAP limitations are explicit and page-scoped in T8. |
| Authority and representation quality | PASS | Original authority is distinguished from extraction confidence. |
| Period, entity and definition fit | PASS WITH LIMITATIONS | Q2 2026 is the latest company financial period; debt-basis and dated market differences are logged. |
| Gaps and conflict disclosure | PASS | T5 records material gaps, severity, affected modules and remediation. |
| Downstream readiness | PASS WITH LIMITATIONS | Every required T8 module is listed once and is source-ready with limitations; no readiness is based on a missing predecessor handoff. |
| Canonical structure and register completeness | PASS — self-check | Required six H2 headings and P3, P5, T1–T8 are present; T8 is not duplicated in the Analysis narrative. |
| Host automated validation | PENDING | Host validation follows this response; no script result is claimed. |

Confidence calculation: E=87, C=68, S=0.70, P=0; rounded score = 56, Low. Source coverage is partial because material operative documents, later-period reporting and complete market evidence are not in the supplied set. QA is Restricted and committee status is Requires More Work. [C1, C8, C9, C18, C19]