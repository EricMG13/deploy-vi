---
module_id: "CP-0"
module_name: "SourceReadiness"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-0-22baad3673eca22f"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-01-CP-0"
credit_os_invocation_sha256: "353d443e421cd92dc1d97a3c9410bd4ea0fd5f880dfb4c87aa6ec5d6b58b7470"
upstream_artifacts_used: []
confidence_score: 46
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [MERGER_AGREEMENT_NOT_ATTACHED, POST_2024_CREDIT_AMENDMENTS_NOT_ATTACHED, UNSECURED_2032_INDENTURE_NOT_ATTACHED, FINRA_LAST_TRADE_ONLY, FINRA_CHART_POINTS_NOT_TRANSCRIBED, PEER_METRIC_DEFINITIONS_DIFFER, NO_CURRENT_DEAL_FINANCING, POST_PERIOD_MERGER]
validation_warnings: [SOURCE_GATE_PARTIAL, LEGAL_VERSION_GAPS, MARKET_OBSERVATION_LIMITS, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-1, CP-1C, CP-2, CP-2A, CP-2G, CP-3, CP-3D, CP-4]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-0_20261002.md`. Owned object: `source_readiness_register`; internal preparation object: `document_parse_manifest`. Schema family: analytical canonical Markdown. Runtime output: this single Markdown handoff. Source gate: **READY_WITH_LIMITATIONS** for the selected relative-value pathway; this is not committee clearance or a finding that any subsequent analytical handoff has passed. The host preparation record identifies 13 pinned sources and one host extraction per source. P3 and P5 cover all 13 before T1–T8 assess readiness. The host's record, rather than another CP-0 artifact, retains original hashes and extraction lineage.

**Own confidence assessment:** nine of ten material readiness claims have direct source support, so E=90; 41 of 50 checked source-demand fields are present, so C=82; the source gate is partial, S=0.7; one material unresolved coverage finding gives P=15. The formula yields 45.76, reported as **46 / Low**; `qa_status: Restricted`. These counts assess this source gate, not downstream calculations. Host validation and completeness checks follow this answer; neither result is claimed here.

## Analysis

### Analytical read-through

The effective pack supports a bounded start to the CZR relative-value route: it contains Q2 2026 reporting, FY2025 comparatives, the executed 2032 secured-note indenture and two supplements, dated bond observations, and MGM/PENN comparison releases. [C1, C12, C15, C16, C18, C21, C22, C23, C24, C27, C28] The limiting issue is not source count. The announced Fertitta transaction follows the reporting date, while its full merger agreement, later credit-agreement amendments and the unsecured 2032 indenture are not attached. [C2, C31, C32, C33, C36] FINRA provides last trades rather than executable or spread observations, and chart points are omitted. [C25, C26] Those gaps constrain legal and price-comparison work but do not prevent the selected modules from producing expressly limited analyses. Start with **Run CP-1**; obtain the named documents before treating transaction-specific conclusions as resolved.

### Preparation summary

All 13 host-listed logical sources have separate P3 identity/version rows and P5 extraction rows. The supplied evidence is page-anchored text from `caos.plain-text` v4 and the host labels every delivery `WHOLE`; therefore none is a page-mapped attachment. `WHOLE` describes delivery, not proof that every original figure, chart or legal layout has been visually checked here. The legal base and its supplements remain separate. Financial tables retain period labels and many row values; complex layout cannot be independently checked against the inaccessible originals. The FINRA observations explicitly omit chart points, so those representations are usable for their displayed summaries, not historical chart analysis. [C15, C16, C18, C25, C26]

### Source authority, scope and contrary evidence

The Q2 filing and FY2025 filing are the primary reporting anchors; the Q2 release is corroborating issuer material. [C1, C12, C14] The secured indenture, March correction and August guarantor supplement are a linked legal family, not three substitutes for one another. [C15, C16, C17, C18] The February 2024 incremental agreement includes a then-conformed credit agreement; the later amendments listed in the 2025 filing are not supplied, so it cannot by itself establish every currently operative credit-agreement term. [C19, C20, C31, C32] The strongest contrary argument to a limited start is that the reported transaction and current debt disclosures already give substantial context, and four same-day FINRA last trades allow a dated comparison. [C2, C4, C21, C22, C23, C24] That argument would support greater conviction only after the missing controlling documents and comparable quote or trade-detail evidence settle the transaction treatment and pricing bases. Until then, route modules must retain these as gaps rather than infer terms or spreads.

The evidence-to-readiness chain is specific: merger consideration and approvals are described in the Q2 filing, but closing is conditional [C2, C3, C11]; an uncompleted transaction can change instrument treatment or refinancing needs; CP-4 and CP-3 must flag the missing agreement and avoid an assumed closing outcome. The secured bond's FINRA summary lacks a benchmark and trade size [C21, C25]; that prevents a supported executable spread comparison, so CP-3D and CP-3 can use only explicitly labelled last-trade observations. No investment preference or legal-effect conclusion is made here.

### Definition, period and market controls

At June 30, the debt note displays face-value total debt of $11,807 million and book-value total debt of $11,705 million, while the balance sheet separately displays $114 million current and $11,585 million long-term debt; the note separately shows deferred revolver finance charges. These are different labelled presentations, not interchangeable leverage inputs. No leverage or reconciliation is computed at this gate. [C4, C5, C6, C7] The Q2 filing itself warns that its Adjusted EBITDA definition may differ from debt or lease agreements. [C8] FY2025 cash interest and first-half 2026 cash interest are different periods and must remain separate. [C38, C39] The May 2026 merger announcement is a **subsequent event relative to June 30 only in its ongoing closing assessment, not in its announcement date**: its May agreement was signed inside Q2, while any completion after June 30 remains pending; do not blend hypothetical closing financing into June balances. [C2, C11]

MGM's digital measure excludes its BetMGM North America venture, whereas PENN's interactive revenue includes a tax gross-up. Their releases are suitable for peer discovery and definition-controlled comparison, not an unadjusted peer multiple. [C27, C28, C29, C30] FINRA's displayed prices are last trades; the source does not provide bid, ask, size, spread or an intraday timestamp. [C21, C22, C23, C24, C25]

### Downstream readiness and next command

The eight selected consumers and their exact safe commands appear **once**, in T8. CP-1 is the first executable row. CP-4 precedes dependent security selection, and the dated market-dislocation assessment precedes CP-3. Readiness assesses source availability, not whether analytical predecessors have already been produced; navigation must sequence and verify those handoffs. CP-2D's liquidity capability and CP-3C's refinancing capability are acknowledged in T4 but cannot be added to this host-pinned eight-row T8; their source demands are carried into CP-2 and CP-4 respectively. No retrieval capability exists in this run, so CP-DR is not asserted executable.

**Time-aware limitation trigger:** if regulatory approval, financing terms or merger timing changes before closing, the first break is to the current transaction assumptions; the transmission is to cash needs, debt treatment and comparable security pricing; the observable remedy is a new filed agreement, amendment or dated market observation. The next command remains `Run CP-1`, followed by source refresh and a new CP-0 assessment when those materials are delivered. [C3, C10, C11, C25]

### Analytical appendix — complete canonical registers

#### P3 — Input Sources
| Logical source | Host filename | Entity; family and content identity | Period or as-of; document date | Version and relationship | Source evidence |
|---|---|---|---|---|---|
| S01 · 02ea2477-b79c-4618-80c2-3b4317e6bafa | PENN_FINRA_TRACE_707569AV1_2026-10-02.txt | PENN; FINRA fixed-income observation, CUSIP 707569AV1 | Observed Oct 2, 2026; last trade Oct 1, 2026 | Separate peer security; not an issuer filing | [C24] |
| S02 · 1b81ec57-5e7f-4eb7-81bf-b1fbc9d4b2b2 | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | CZR; incremental assumption No. 3 and conformed CEI credit agreement | Effective Feb 6, 2024 | Amends 2020 credit agreement; conformed version precedes later listed amendments | [C19, C20, C31, C32] |
| S03 · 3093e5d3-2687-41f0-b88a-2330b5077c7f | CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | CZR; FINRA observation, 6.00% 2032, CUSIP 12769GAD2 | Observed Oct 2, 2026; last trade Oct 1, 2026 | Distinct from secured 6.50% 2032 observation | [C22, C33] |
| S04 · 32dbac40-24c2-4e9a-9dfa-0bd4ad9cbe4e | CZR_2024_650_Notes_First_Supplemental_Indenture.txt | CZR; first supplemental indenture | Dated Mar 1, 2024 | Changes base secured-note indenture and adds guarantors; retain separately | [C16, C17] |
| S05 · 439e1450-b5ae-4830-b4c3-3719da918fe3 | CZR_Q2_2026_10Q.txt | CZR; quarterly filing | Quarter and six months ended Jun 30, 2026; signed Jul 28, 2026 | Current-period primary report; includes proposed merger disclosure | [C1, C2] |
| S06 · 4b57b4a0-a633-4bf9-a890-34d48e34f3a7 | MGM_FINRA_TRACE_552953CK5_2026-10-02.txt | MGM; FINRA fixed-income observation, CUSIP 552953CK5 | Observed Oct 2, 2026; last trade Oct 1, 2026 | Separate peer security | [C23] |
| S07 · 6a435737-2079-4a28-83cb-a9394c17059a | CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | CZR; second supplemental indenture | Dated Aug 23, 2024 | Adds guarantors to Feb 2024 base as previously supplemented; retain separately | [C18] |
| S08 · 86dcb55f-6abe-4aab-8143-7e29addf278a | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | CZR; FINRA observation, 6.50% secured 2032, CUSIP 12769GAC4 | Observed Oct 2, 2026; last trade Oct 1, 2026 | Target bond observation; separate from legal terms | [C21, C25] |
| S09 · 88bbc140-036a-46e0-8935-18a611301c95 | CZR_Q2_2026_Earnings_Release.txt | CZR; Q2 results release and non-GAAP reconciliation | Quarter ended Jun 30, 2026; released Jul 28, 2026 | Issuer corroboration, not replacement for 10-Q | [C14] |
| S10 · 8b807696-96c6-4d9b-9e4e-911e1fea35e5 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | CZR; executed 6.50% secured 2032 indenture and exhibits | Dated Feb 6, 2024 | Base document linked to S04 and S07; embedded intercreditor Exhibit D is a form | [C15, C16, C18] |
| S11 · bc3f76d7-9b8a-4d78-97b4-199dbebb1ba3 | PENN_Q2_2026_Earnings_Release.txt | PENN; Q2 results release | Quarter ended Jun 30, 2026; released Aug 6, 2026 | Peer disclosure; metric-definition differences retained | [C28, C29] |
| S12 · dccb51cb-32e5-4249-833a-03c3f8809eca | MGM_Q2_2026_Earnings_Release.txt | MGM; Q2 results release | Quarter ended Jun 30, 2026; released Jul 29, 2026 | Peer disclosure; venture/perimeter distinction retained | [C27, C30] |
| S13 · f991456d-d304-4d03-9648-bcdf899ce7a5 | CZR_FY2025_10K.txt | CZR; audited annual filing and exhibit index | FY ended Dec 31, 2025; signed Feb 17, 2026 | Historical comparative and index to legal documents not attached | [C12, C31, C32, C33] |

No contained duplicate is established from the supplied content. S04 and S07 are supplements, not duplicates of S10; S09 corroborates but does not replace S05. The host preparation record holds immutable source hashes; none is recalculated here.

#### P5 — Parse Jobs
| Source | Extractor; delivery and mode | Pages covered in delivered evidence | Status; extraction confidence | Active content and fidelity limitation | Source evidence |
|---|---|---|---|---|---|
| S01 | caos.plain-text v4; WHOLE; LAYOUT_TEXT | 1 | DEGRADED; high for summary | Host extraction active; chart points absent; snapshot only | [C24, C26] |
| S02 | caos.plain-text v4; WHOLE; HYBRID/LEGAL_CLAUSE | 1–67 | DEGRADED; medium | Host extraction active; long clauses and conformed tables flattened; later amendments absent as sources | [C19, C20, C31, C32] |
| S03 | caos.plain-text v4; WHOLE; LAYOUT_TEXT | 1 | DEGRADED; high for summary | Host extraction active; displayed chart points absent and no executable quote | [C22, C25, C26] |
| S04 | caos.plain-text v4; WHOLE; LEGAL_CLAUSE | 1–3 | DEGRADED; medium-high | Host extraction active; wording/page anchors usable; original legal layout not independently compared | [C16, C17] |
| S05 | caos.plain-text v4; WHOLE; HYBRID/TABLE_FIRST | 1–26 | DEGRADED; medium-high | Host extraction active; tables text-rendered; digital presence map not transcribed as plotted geography | [C1, C4, C9] |
| S06 | caos.plain-text v4; WHOLE; LAYOUT_TEXT | 1 | DEGRADED; high for summary | Host extraction active; chart points absent and no bid/ask evidence | [C23, C25, C26] |
| S07 | caos.plain-text v4; WHOLE; LEGAL_CLAUSE | 1–6 | DEGRADED; medium-high | Host extraction active; guarantor schedule text available; layout/line-wrap review reserved | [C18] |
| S08 | caos.plain-text v4; WHOLE; LAYOUT_TEXT | 1 | DEGRADED; high for summary | Host extraction active; chart expressly untranscribed; no spread, size or intraday time | [C21, C25, C26] |
| S09 | caos.plain-text v4; WHOLE; TABLE_FIRST | 1–4 | DEGRADED; medium-high | Host extraction active; tabular text and release reconciliation usable, no original-layout inspection | [C14] |
| S10 | caos.plain-text v4; WHOLE; HYBRID/LEGAL_CLAUSE | 1–60 | DEGRADED; medium | Host extraction active; extensive legal tables/exhibits flattened; base defeasance text visibly differs from S04; form is not executed agreement | [C15, C17, C34, C35] |
| S11 | caos.plain-text v4; WHOLE; TABLE_FIRST | 1–5 | DEGRADED; medium-high | Host extraction active; peer tables usable with tax-gross-up definition warning | [C28, C29] |
| S12 | caos.plain-text v4; WHOLE; TABLE_FIRST | 1–6 | DEGRADED; medium-high | Host extraction active; peer tables usable with BetMGM perimeter distinction | [C27, C30] |
| S13 | caos.plain-text v4; WHOLE; HYBRID/TABLE_FIRST | 1–57 | DEGRADED; medium-high | Host extraction active; statements/notes/exhibit index text usable; figures and original table layout not independently checked | [C12, C13, C31, C32] |

`DEGRADED` here means scoped text remains usable with the stated limitation; it does not mean a missing entire source. No P5 row is BLOCKED, and no original is silently substituted for its host extraction. Fidelity findings concern delivered representation only; the host record, not this handoff, owns hash and original-blob verification.

#### T1 — Input Gate
| Gate | Resolved value | Evidence or preparation basis | Assessment |
|---|---|---|---|
| Objective | Source sufficiency for FULL_CREDIT_32 / RELATIVE_VALUE: CZR 6.50% secured 2032 against issuer and gaming peers | Target and comparison observations [C21, C22, C23, C24] | Defined; no investment conclusion |
| Identity and period | CZR; Q2 2026 at Jun 30; analysis as of Oct 2, 2026 | Quarterly filing [C1]; dated market observation [C21] | PASS |
| Preparation record | Host source-preparation block; 13 originals, 13 host extractions, WHOLE deliveries | Host metadata, not source-content evidence | P3/P5 completed first; hashes remain host-owned |
| Authority and version | Filing, legal family, issuer releases and market observations kept separate | [C12, C15, C16, C18, C25] | PASS with legal-version gaps |
| Source gate | READY_WITH_LIMITATIONS; no source-count proxy to committee readiness | Gaps G01–G07 below | Restricted; named remediation |
| Canonical handoff | CZR_CP-0_20261002.md; zero upstream artifacts | Host-owned run envelope | Own structure checked; host validation pending |

#### T2 — Source Register
| Source | Original authority; quality label | Active representation and usability | Relevant objective coverage | Limitation / evidence |
|---|---|---|---|---|
| S01 | External regulated-market page; Secondary-Reputable | Host extraction; summary usable | PENN dated bond observation | Last trade and chart omission [C24, C26] |
| S02 | Executed financing filing; Primary-Unverified | Host extraction; clauses usable with version check | Historical CEI bank facility and mechanics | Subsequent amendments not attached [C19, C31, C32] |
| S03 | External regulated-market page; Secondary-Reputable | Host extraction; summary usable | CZR unsecured bond market observation | No executable spread [C22, C25] |
| S04 | Executed supplement; Primary-Unverified | Host extraction; operative text usable | Secured indenture correction/guarantors | Read with S10 [C16, C17] |
| S05 | Issuer SEC filing; Primary-Verified as filed source | Host extraction; statements and narrative usable | Current quarter, liquidity, debt, merger | Text-rendered tables and missing agreement [C1, C2, C36] |
| S06 | External regulated-market page; Secondary-Reputable | Host extraction; summary usable | MGM bond observation | Last trade only [C23, C25] |
| S07 | Executed supplement; Primary-Unverified | Host extraction; schedule and text usable | Additional secured-note guarantors | Read with S10/S04 [C18] |
| S08 | External regulated-market page; Secondary-Reputable | Host extraction; summary usable | Target secured bond market snapshot | Chart and quote detail absent [C21, C25, C26] |
| S09 | Issuer release; Secondary-Reputable | Host extraction; corroborating only | Q2 results and adjusted reconciliation | Filing remains primary [C14, C1] |
| S10 | Executed base indenture; Primary-Unverified | Host extraction; base clauses usable | Secured-note terms and protections | S04 corrects text; layout flattened [C15, C17, C34, C35] |
| S11 | Peer issuer release; Secondary-Reputable | Host extraction; definition-controlled use | PENN operations and comparator | Interactive tax gross-up [C28, C29] |
| S12 | Peer issuer release; Secondary-Reputable | Host extraction; definition-controlled use | MGM operations and comparator | BetMGM excluded from MGM Digital [C27, C30] |
| S13 | Audited issuer SEC filing; Primary-Verified as filed source | Host extraction; comparative use | FY2025, debt/leases/exhibit history | Indexed legal amendments are not their texts [C12, C13, C31, C32] |

Authority labels refer to originals; fidelity and extraction confidence are in P5. `Primary-Unverified` on the legal text means CP-0 has not compared every clause against its retained original, not that the host failed to pin that original.

#### T3 — Source Hierarchy
| Tier | Rule | Present source set | Missing minimum or constraint | Evidence |
|---|---|---|---|---|
| 1 | Filed statements and executed operative documents control their own scope | S02, S04, S05, S07, S10, S13 | Full merger agreement, later credit amendments, unsecured-note indenture | [C1, C15, C16, C18, C31, C32, C33, C36] |
| 2 | Issuer/peer releases corroborate and explain, not replace controlling filings | S09, S11, S12 | Peer metric-definition alignment remains required | [C14, C27, C28, C29, C30] |
| 3 | Dated external market pages support only fields displayed | S01, S03, S06, S08 | No executable quote, spread, trade size or chart history | [C21, C22, C23, C24, C25, C26] |
| 4 | Unattributed context cannot control a finding | No such source identified | Not a replacement for tiers 1–3 | Preparation inventory; no source-content claim |

#### T4 — Content-to-Module Map
| Capability / module | Active source basis | Specific evidence demand and status | Disposition; readiness effect | Evidence |
|---|---|---|---|---|
| CP-1 issuer analysis | S05, S09, S13 | Current/prior periods, operating drivers, statements and segments present | Recommended; READY | [C1, C12, C14] |
| CP-1C peer comparison | S11, S12, S01, S06 | Peer results and dated observations present; definitions unequal; peer filings absent | Recommended; READY_WITH_LIMITATIONS | [C23, C24, C27, C28, C29, C30] |
| CP-2 debt/cash-flow | S05, S13, S02 | Debt, liquidity, cash interest and leases present; current bank-document version incomplete | Recommended; READY_WITH_LIMITATIONS | [C4, C9, C10, C31, C32, C38, C39] |
| CP-2A downside | S05, S13, S09 | Issuer drivers and maturity schedule present; independent scenario assumptions absent | Recommended; READY_WITH_LIMITATIONS; no invented stress | [C10, C11, C14] |
| CP-2G forward view | S05, S13 | Near-term estimates and maturity information present; no full multi-year management forecast supplied | Recommended; READY_WITH_LIMITATIONS; gap-led forward work | [C9, C10] |
| CP-4 legal/covenant | S10, S04, S07, S02, S05 | Secured terms present; merger agreement, later bank amendments and unsecured indenture missing | Recommended; READY_WITH_LIMITATIONS; no unresolved term asserted | [C15, C16, C18, C31, C32, C33, C36] |
| CP-3D market dislocation | S08, S03, S06, S01 | Dated prices/yields present, not spread or series | Recommended; READY_WITH_LIMITATIONS | [C21, C22, C23, C24, C25, C26] |
| CP-3 relative value | S05, S08, S03, S06, S01, S10, S04, S07, S11, S12 | Target/security and comparison evidence present; no executable bid or fully equivalent peer | Recommended after legal/market steps; READY_WITH_LIMITATIONS | [C15, C16, C18, C21, C22, C23, C24, C25, C29, C30] |
| CP-2D near-term liquidity | S05, S13 | Liquidity disclosures available, but module not among host-pinned T8 IDs | Explicitly out of this selected command sheet; demand carried into CP-2 | [C9, C10, C13] |
| CP-3C refinancing | S05, S10, S02 | Maturity/transaction facts available; module not among host-pinned T8 IDs | Explicitly out of this selected command sheet; demand carried into CP-4 and CP-3 | [C2, C10, C15, C19] |
| CP-DR research | No retrieval tool or research brief delivered | Named missing-document questions exist, but no executable research capability in this invocation | Inapplicable as a T8 recommendation here; request files and re-run CP-0 | [C31, C32, C36] |

#### T5 — Gaps/Conflicts
| ID; kind | Severity | Source/evidence demand and competing presentations | Affected modules and readiness effect | Exact remediation; owner / state | Evidence |
|---|---|---|---|---|---|
| G01 · source gap | MATERIAL | Signed May 2026 merger agreement is cited but not delivered | CP-4, CP-3, CP-2A; limited transaction treatment | Supply full agreement and material amendments; issuer/user; open | [C2, C3, C11, C36] |
| G02 · version gap | MATERIAL | May and November 2024 credit amendments listed, but S02's conformed agreement predates them | CP-4, CP-2; current covenant/collateral wording limited | Supply both executed amendments and later changes, if any; issuer/user; open | [C19, C20, C31, C32] |
| G03 · instrument gap | MATERIAL | Unsecured 6.00% 2032 issue identified; its operative indenture not delivered | CP-4, CP-3; unsecured covenant comparison limited | Supply executed 2032 unsecured indenture and supplements; issuer/user; open | [C22, C33] |
| G04 · market gap | MATERIAL | FINRA last trades have no spread, benchmark, size, bid/ask or intraday stamp | CP-3D, CP-3; executable value and spread attribution unavailable | Obtain dated comparable quotes/trade detail and benchmark, or retain last-trade-only bounds; market-source owner; open | [C21, C22, C23, C24, C25] |
| G05 · parse limitation | MINOR | FINRA page charts displayed but chart points untranscribed | CP-3D, CP-3; no chart trend | Supply source-exported points if trend required; source owner; open | [C26] |
| G06 · definition conflict | MATERIAL | June debt note face $11,807m/book $11,705m; balance-sheet current $114m/long-term $11,585m; revolver deferred charges separately $(6)m. Labels and perimeters differ; no silent single basis | CP-2, CP-3; basis must be named before calculations | Reconcile under each module's debt definition using note and balance-sheet labels; analytical owner; open | [C4, C5, C6, C7] |
| G07 · peer-definition conflict | MATERIAL | PENN interactive tax gross-up; MGM Digital excludes its North America venture | CP-1C, CP-3; raw margins not directly comparable | Obtain aligned definitions or show separate perimeters; peer-analysis owner; open | [C29, C30] |
| CF-1 · base/supplement difference | MATERIAL | S10's defeasance section contains a malformed cross-reference; S04 expressly replaces §8.01(b) and gives a different sequence | CP-4, CP-3; use linked versions and verify exact operative text, without legal interpretation here | Inspect original clauses alongside the executed supplement; legal-analysis owner; open | [C17, C34, C35] |
| G08 · forward gap | MINOR | No complete forward operating forecast or financing for a consummated merger in this pack | CP-2G, CP-2A; scenario outputs bounded | Request dated forecasts/financing terms if quantified case is required; issuer/user; open | [C3, C10, C11] |

The missing exhibits are source gaps, not failed host parsing. None becomes an assumed zero or an unstated completed transaction. The later FY2025 index identifies documents; an index entry does not supply the documents' clauses. [C31, C32, C33]

#### T6 — Evidence Trace
| Evidence ID / claim | Marker | Original document; active content | Locator and allowed use |
|---|---|---|---|
| ET01 · current reporting anchor | [C1] | S05; host extraction | p.1; quarter identity |
| ET02 · transaction announced and conditional | [C2, C3, C11] | S05; host extraction | pp.5, 25; pending transaction, not completed financing |
| ET03 · separate debt labels | [C4, C5, C6, C7] | S05; host extraction | pp.2, 9; preserve displayed roles |
| ET04 · maturity schedule | [C10] | S05; host extraction | p.9; scheduled debt figures, not a scenario |
| ET05 · annual comparative | [C12, C13, C38] | S13; host extraction | pp.1, 23, 31; FY basis |
| ET06 · legal document family | [C15, C16, C17, C18] | S10/S04/S07; separate host extractions | base p.3; supplements p.1; linked, not merged |
| ET07 · credit version | [C19, C20, C31, C32] | S02/S13; separate host extractions | S02 pp.1, 4; S13 p.56; later texts missing |
| ET08 · four last-trade prices | [C21, C22, C23, C24] | S08/S03/S06/S01; separate host extractions | each p.1; last trade only |
| ET09 · market extraction limits | [C25, C26] | S08; host extraction | p.1; missing market fields/chart points |
| ET10 · peer definitions | [C29, C30] | S11/S12; separate host extractions | S11 p.2; S12 p.1; not directly interchangeable |
| ET11 · missing operative documents identified | [C31, C32, C33, C36] | S13/S05; separate host extractions | S13 pp.55–56; S05 p.6; references, not their text |
| ET12 · base-versus-supplement text | [C34, C35] | S10/S04; separate host extractions | S10 p.31; S04 p.1; verification flag |
| ET13 · first-half cash interest | [C39] | S05; host extraction | p.5; six-month basis distinct from FY |

#### T7 — Master Index State
| Field | State | Evidence / limitation |
|---|---|---|
| Run and owner | COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6; CZR CP-0 SourceReadiness | Host-owned front matter |
| Requested / resolved mode | FULL_CREDIT_32 / RELATIVE_VALUE; source sufficiency only | Host-owned selection; T1 objective |
| Preparation record | Host source-preparation block; 13 pinned sources, 13 WHOLE host extractions | Metadata; P3/P5 retain CP-0 findings, not hashes |
| Entity and period | CZR Q2 2026; FY2025 comparative; MGM/PENN Q2 2026; Oct 2026 market snapshots | [C1, C12, C21, C23, C24, C27, C28] |
| Version families | Secured 2032 base plus first and second supplements; Feb 2024 bank incremental/conformed agreement; later amendments indexed only | [C15, C16, C18, C19, C20, C31, C32] |
| Canonical output | CZR_CP-0_20261002.md; P3/P5 and T1–T8 in one handoff | Own draft; host validation follows |
| Warnings and consumers | Restricted source gate; eight selected consumers listed in T8; G01–G08 and CF-1 remain visible | T5 and T8; no downstream pass asserted |

#### T8 — Recommended Run Command Sheet
| Sequence | Module | Candidate command | Exact command | Source files to attach | Upstream handoff | Readiness | Why now / blocker |
|---:|---|---|---|---|---|---|---|
| 1 | CP-1 | Run CP-1 | Run CP-1 | CZR_Q2_2026_10Q.txt; CZR_Q2_2026_Earnings_Release.txt; CZR_FY2025_10K.txt | This CP-0 handoff | READY | Establish issuer/period operating base; separately flag pending merger [C1, C2, C12, C14]. |
| 2 | CP-1C | Run CP-1C | Run CP-1C | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; MGM_Q2_2026_Earnings_Release.txt; PENN_Q2_2026_Earnings_Release.txt | This CP-0; CP-1 when produced | READY_WITH_LIMITATIONS | Compare peer definitions explicitly; peer 10-Ks absent and PENN/MGM perimeters differ [C27, C28, C29, C30]. |
| 3 | CP-2 | Run CP-2 | Run CP-2 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | This CP-0; CP-1 when produced | READY_WITH_LIMITATIONS | Reconcile carrying/face/current debt and cash periods; later bank amendments missing [C4, C5, C6, C7, C31, C32, C38, C39]. |
| 4 | CP-2A | Run CP-2A | Run CP-2A | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_Earnings_Release.txt | This CP-0; CP-1 and CP-2 when produced | READY_WITH_LIMITATIONS | Downside can document causal triggers, but no invented forecast or merger-closing case [C3, C10, C11]. |
| 5 | CP-2G | Run CP-2G | Run CP-2G | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_Q2_2026_Earnings_Release.txt | This CP-0; preceding analysis as navigation requires | READY_WITH_LIMITATIONS | Forward work may use disclosed dates/estimates; complete forecast and deal financing absent [C9, C10, C11]. |
| 6 | CP-4 | Run CP-4 | Run CP-4 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt; CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt; CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt | This CP-0; CP-2 when produced | READY_WITH_LIMITATIONS | Analyze supplied secured terms before security selection; do not infer missing merger, later bank or unsecured-note clauses [C15, C16, C18, C31, C32, C33, C36]. |
| 7 | CP-3D | Run CP-3D | Run CP-3D | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt; MGM_FINRA_TRACE_552953CK5_2026-10-02.txt; PENN_FINRA_TRACE_707569AV1_2026-10-02.txt; CZR_Q2_2026_10Q.txt | This CP-0; preceding analysis as navigation requires | READY_WITH_LIMITATIONS | Dated last trades support bounded market observations, not executable spreads or chart history [C21, C22, C23, C24, C25, C26]. |
| 8 | CP-3 | Run CP-3 | Run CP-3 | CZR_Q2_2026_10Q.txt; CZR_FY2025_10K.txt; CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt; CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt; MGM_FINRA_TRACE_552953CK5_2026-10-02.txt; PENN_FINRA_TRACE_707569AV1_2026-10-02.txt; MGM_Q2_2026_Earnings_Release.txt; PENN_Q2_2026_Earnings_Release.txt; CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt; CZR_2024_650_Notes_First_Supplemental_Indenture.txt; CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | This CP-0; CP-1C, CP-2, CP-4 and CP-3D when produced | READY_WITH_LIMITATIONS | Perform security-aware, definition-controlled RV only; quote detail and missing operative documents remain gaps [C15, C16, C18, C21, C22, C23, C24, C25, C29, C30]. |

## Evidence Trace

T6 is the complete source-locator trace for the material readiness claims. Markers refer to this answer's citation list; source IDs and host filenames are paired in P3. Prepared text is the content vehicle, while the original source remains the cited authority. The host preparation metadata is used for delivery and extraction identity only and is not cited as source-content evidence.

## Source Registry

P3 records all 13 input identities and version links; P5 records all 13 host extraction jobs; T2 separates original authority from prepared-content usability; T3 states the controlling hierarchy. No retired P1, P2, P4, P6, P7 or P8 register is authored. The source set does not include an executable market quote, the full merger agreement, the two listed later bank amendments, or the unsecured 2032 indenture, notwithstanding references to those documents in filed material. [C25, C31, C32, C33, C36]

## Gaps & Conflicts

T5 is the lossless issue register. Priority remediation is the full merger agreement, executed post-February-2024 credit amendments, and unsecured-note indenture; then comparable dated market quote/trade detail if an executable pricing or spread claim is needed. [C25, C31, C32, C33, C36] Treat the base/supplement defeasance difference as a version-verification question for CP-4, not a CP-0 legal ruling. [C17, C34, C35] Source-refresh trigger: any newly supplied operative document, updated bond observation, merger closing/termination, or change in filing period requires preparation and readiness to be rebuilt before dependent claims are upgraded. [C11, C25]

## QA Validation

| Self-check | Result | Basis and disposition |
|---|---|---|
| Preparation identity and ordering | PASS | P3/P5 cover the 13 host-listed sources before T1–T8; host-owned envelope unchanged. |
| Inventory, entity, period and versions | PASS | Thirteen separate rows each in P3/P5; supplements linked rather than collapsed. |
| Duplicate and amendment handling | PASS | No contained duplicate asserted; base and both supplements retained. |
| Locator and coverage integrity | PASS | Delivered pages stated per P5; no claim of original visual verification; chart omission and layout limitations disclosed. |
| Fidelity and authority separation | PASS | P5 labels prepared extraction; T2 labels original authority; scoped DEGRADED findings carried forward. |
| Definition and subsequent-event discipline | PASS | Debt presentations remain separate; merger closing remains pending, with no pro forma blend. |
| Gaps/conflicts and per-consumer readiness | PASS | T5 issues carried into T4/T8; absent analytical predecessors are sequencing, not source blockers. |
| Route and model-boundary discipline | PASS | T8 lists precisely the eight pinned live modules once; no CP-MODEL readiness assertion. |
| Confidence and status self-check | PASS | E=90, C=82, S=0.7, P=15; 46/Low, Restricted, Requires More Work. |
| Canonical Markdown self-check | PASS | Exact derived filename specified, seven allowed authored YAML fields, six ordered H2 headings, P3/P5/T1–T8 present; host validation follows and is not claimed. |

**Next safe action:** `Run CP-1`. This is a source-readiness handoff, not a credit conclusion, legal opinion, investment recommendation, or assertion that the host's subsequent validators have passed.