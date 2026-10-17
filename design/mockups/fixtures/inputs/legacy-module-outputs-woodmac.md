# Inventory: "Module Output" screenshots (Deploy V modules rendered in M365 Copilot)

Scope: 87 PNGs in `/Users/ericguei/Documents/Module Output/`, all dated 27 Aug 2026, 08:35:23 to 08:56:20, all viewed. Filenames are `Screenshot 2026-08-27 at 08.MM.SS.png`; below I give only `MM.SS`.
Rendering surface: light-theme Copilot markdown render (GitHub-like), H1/H2/H3 with rules under H1/H2, grey code chips, tables with horizontal rules only (no vertical borders, no zebra), thin vertical scrollbar at right edge. Screenshots are crops, not complete pages: most start or stop mid-section.

Two issuers appear:
- **Wood Mackenzie** (Planet Holdco 2 Ltd; borrower Planet US Buyer LLC; sponsor Veritas Capital via Planet TopCo LP; first-lien Term Loan B due 2031). 14 modules, run dates 2026-08-21 (CP-PARSE, CP-0), 2026-08-25 (CP-1 to CP-2H), 2026-08-26 (CP-3, CP-4).
- **Lambda, Inc. / Project Poutine** (GPV $917.2m senior secured term loan, Lambda Compute II LLC + Lambda Cloud Canada, Inc.; project-finance, DSCR/CFADS). 3 modules (CP-2F, CP-2H, CP-3), run date 2026-08-11. The brief's "issuer appears to be Wood Mackenzie" holds for most but not the last 14 shots.

Analyst field everywhere: `"Minsehimbe, Eric"`.

---
## 0. The two-part anatomy every module shares

### 0.1 Run header (a flat YAML-ish "envelope" that Copilot renders as ordinary text, NOT as a code block or table)
It is a single wrapped paragraph of `key: value` pairs (no line breaks between keys), with bullet lists breaking into the paragraph where a value is a list, framed by a horizontal rule above and below. The YAML tokens leak through literally: folded-scalar markers `>-` (e.g. `perimeter: >-`, `objective: >-`, `currency_basis: >-`, `predecessor_note: >-`, `instrument_scope: >-`), curly-brace pseudo-objects, square-bracket lists, and quoted strings. It is the least presentable element; a designer needs to parse it into a key/value panel.

Keys seen (order as rendered, Wood Mackenzie CP-1 / CP-2 family):
`module_id`, `module_name` (CamelCase, no spaces, e.g. `FundamentalCredit`, `DownsidePathway`, `MacroFXHedgingSensitivity`), `stage` (integer), `skill_dir` (kebab slug), `launch_companion` (e.g. `REF_CP-2A_STEPS.md`; from CP-2 onward), `deployment_scope: V`, `run_id` (`WoodMackenzie_CP-1_20260825`), `issuer_name`, `issuer_id` (`WoodMackenzie`), `identity_kind: ISSUER`, `borrower`, `holdings`, `sponsor`, `perimeter`, `transaction`, `reporting_period`, `scenario: Full Credit Assessment`, `run_profile: FULL_CREDIT_32`, `objective`, `analysis_date`, `analyst`, `owned_object` (snake_case, e.g. `fundamental_credit_synthesis`, `downside_pathway_stress_transmission`, `forward_credit_model`, `rating_transition_case`, `relative_value_security_selection`), `schema_family: Nested`, `output_class: CANONICAL_MARKDOWN` (CP-2F/2H/3 on), `route_authority: CP_DEPLOY_V_ROUTE_INDEX_v1`, `inventory_policy: LIVE_FULL_FOLDER_RESOLUTION`, `no_sha_policy: true`, `currency_basis`, `upstream_artifacts_used` (bullets, one `{module_id: ..., run_id: ..., verdict: ..., role: ...}` brace-object per upstream module), `predecessor_note`, `confidence_score`, `confidence_band`, `qa_status`, `committee_status`, `limitation_flags` (bulleted UPPER_SNAKE_CASE tokens, 5 to 8 per module), `validation_warnings` (same style, CP-0/CP-1/CP-1A/CP-1B/CP-1C/CP-2D), `downstream_consumers: [CP-2A, CP-2B, ...]`.
Module-specific extra keys: CP-0 `readiness_summary.finalized`, `capacity_outcome: SINGLE_WINDOW`, `pipeline.execution_state: FINALIZED`, and two sub-blocks introduced by odd H2-looking lines (markdown `---` text): "--- anchor values copied unchanged from the accepted CP-PARSE artifact ---" and "--- CP-0's own invocation echo fields ---" (keys `credit_os_run_id`, `credit_os_profile_id: POST_CP0_PROFILE_GATE_PENDING`, `credit_os_selection_id: PER_RUN`, `credit_os_authority_bundle_sha256: NOT_APPLIED_NO_SHA_POLICY`, `credit_os_attempt_id`, `credit_os_route_node_id: CP-0`, `credit_os_invocation_sha256`). CP-1A `absorbed_phase: CP-2C (GovernanceSponsorScore)`, `sponsor_governance_risk_level: Medium`. CP-1B `comparison`. CP-1C `peer_set_mode: auto_discover_and_verify (reputable_public_web)`. CP-2H `rating_issuance: PROHIBITED_NO_RATING_ISSUED`, and prose "INVESTOR-SIDE RATINGS ANALYSIS ONLY - does NOT issue, impersonate or predict a formal agency rating". CP-2F `esg_risk_level`, `operational_risk_level`. CP-3 `layer: L3`, `instrument_scope` (brace object with `leg`, `isin`/`figi`/`cusip` = `[Insufficient Information - license-restricted]`, `rate`, `call`, `seniority`, `PRIMARY_SUBJECT: true`), `market_basis`, `as_of`, `execution_mode: Single-Name RV (...)`, `module_status`, `evidence_class: full_run`, `frontmatter_limitation_flags` (renamed from `limitation_flags`).

### 0.2 Body (H1 then H2 sections)
- **H1**: `<MODULE-ID> — <Spaced Module Name> — <Issuer> (<perimeter>)`. Wood Mackenzie: `CP-2 — Fundamental Credit — Wood Mackenzie (Planet Holdco 2 Ltd / Planet US Buyer LLC first-lien TLB)`. Lambda: `CP-2F — ESG & Sustainability Credit Risk / Operational Materiality — Lambda / Project Poutine (GPV $917.2m Senior Secured Term Loan)`; Lambda CP-3 H1 adds `as of 2026-08-11`.
- **Canonical H2 sequence** (CP-1A/1B/2/2A/2D/2E/2G/2H/3 and Lambda): `Module Result` > `Analysis` > (`Analytical appendix ...` or `Evidence Trace` / registers) > `Downstream Handoffs & Recommended Next Command` > `QA & Governance` (or Lambda: `Credit Handoff & Monitoring` > `Conflicts, Limitations & QA Validation`). Lambda CP-2H's QA bullet says "six canonical H2 headings present".
- **Variants**: CP-0, CP-1, CP-1C, CP-4 use **`Audit Summary`** in place of `Module Result` (CP-1C and CP-4 headings seen as "Audit Summary" then "Analysis"). CP-PARSE uses H1 `CP-PARSE — DataPreparation — Module Result`. `Evidence Trace` is Title Case in CP-2G/CP-2H, sentence case ("Evidence trace") in CP-2D.
- **Result line** (first line under Module Result/Audit Summary, rendered as plain/bold run-in, not a badge): `Result: <STATUS> — <UPPER-CASE OUTCOME PHRASE> (<qualifier>).` Then a context paragraph, then 5 to 8 bullets with bold lead sentence + body + a trailing ref in square brackets, closing with a `Confidence N / 100 (Band).` bullet that lists deductions, then a bold-led closing verdict paragraph (`Macro verdict:`, `Downside verdict:`, `Liquidity verdict:`, `ESG/operational verdict:`, `Net:`).
- **Analysis**: starts with an H3 "(conclusion-first)" read, then key tables, then bullets in the pattern *Evidence -> Risk Mechanic -> Credit Implication* (the arrow glyph is literal; sometimes italic "Mechanic:"/"Implication:" run-ins, sometimes plain), then "Strongest contrary view (carried, unblended)" with "This wins if ... It loses if ... Monitoring triggers: (1)...(4)".
- **Evidence tags in square brackets** inline: `[CP-2G calc]`, `[CP-2D calc]`, `[CP-4 calc]`, `[CP-2F calc on CP-2A frozen inputs]` (rendered as grey code chip in most modules, plain brackets in CP-2G/CP-2H/CP-2F/CP-3), `[inferred - not separately disclosed]`, `[limitation: RCF_SPRINGING_COVENANT_TRIGGER_PENDING_CP4]`, `[external: ...]`, `[Insufficient Information]` (placeholder token, sometimes bold, also in table cells), `[Provisional — Equal-Weight]`, line-locators `[CP-2G L77/L79/L94/L102/L107]`, file names in brackets.
- **Citation style**: Copilot web-search markers appear only in CP-0 and CP-3 (Wood Mackenzie); see section 2.5.

---
## 1. Per-module inventory

### CP-PARSE — DataPreparation (shots 37.02, 37.19)
- Issuer Wood Mackenzie, run `WoodMackenzie_CP-PARSE_20260821`. Header block not captured.
- H1 `CP-PARSE — DataPreparation — Module Result`, then straight to `Result: PASS — READY_FOR_CP-0.` (the only module whose status is a machine token; code-style `READY_FOR_CP-0`).
- Bullets (bold lead-ins): `Entry gate satisfied.` `Live full-folder resolution.` `Representation-neutrality applied.` `Capacity plan: SINGLE_WINDOW.` `Coverage:` `Pack confidence: 92 / 100 (High), per canon clamp((0.6·E + 0.4·C)·S − P, 0, 100) with E=95, C=93, S=1.0, P=2.` `Blocking flags: none. Non-blocking flags: ...`
- Register: H2 `Triage Register`, line `table_id: cpparse.triage_register`. Note: "parse_need_score is a 0–100 selection signal (restructuring need), not a quality/confidence score. decision: PARSE = ...; PASS_THROUGH = ...".
  Columns: `# | Source (short) | Family | parse_need_score | Mode | Decision | Live-read evidence`. Example row: `1 | Credit Agreement (2024) [Exec] | LEGAL_AGREEMENT | 88 | LEGAL_CLAUSE | PARSE | 541pp, clean text; CUSIP 72706RAA4; BofA agent`. Families seen: LEGAL_AGREEMENT, LEGAL_AMENDMENT, COVENANT_REVIEW, ANNUAL_REPORT, QUARTERLY_REPORT, COMPLIANCE_CERTIFICATE, LENDER_PRESENTATION. 28 sources; grouped rows use ranges ("4–6", "7–13", "14–18", "19–22"). **WIDE: scrolls horizontally, last column cut off at the right edge** (37.19; scrollbar visible). Cut at bottom.
- Citations: `turn1search85`, `turn1search84`, `turn1search86`, `turn1search89` (37.02).

### CP-0 — SourceReadiness (stage 2) (shots 35.23–36.31)
- Header (35.23): confidence_score 90, High; qa_status Passed; committee_status `SOURCE_READY — profile/use-case gate (POST_CP0_PROFILE_GATE) pending`; limitation_flags `[SOURCE_IDENTITY_CONNECTOR_NATIVE_NO_SHA, LICENSE_RESTRICTED_RATING_CELLS, PERIOD_OVERLAP_Q4-25_Q1-26_PRES_AND_CALL, NO_STANDALONE_Q4_QUARTERLY_EXPECTED]`; validation_warnings `[NOT_ALL_QUARTERS_HAVE_MATCHING_COMPLIANCE_CERT]`; downstream_consumers 15 modules (CP-1 ... CP-6).
- H1 `CP-0 — SourceReadiness — Wood Mackenzie (Planet Holdco 2 Ltd)`. H2 `Audit Summary`: "Readiness verdict: `READY` (with scoped limitations) — cleared to the profile/use-case gate and downstream analysis." (READY in code chip). Bullets: `Lineage accepted.` `Representation neutrality preserved.` `Coverage:` "Readiness distribution across 15 consumers: 12 READY, 3 READY_WITH_LIMITATIONS (...) No consumer is CONDITIONAL or BLOCKED." `Confidence: 90 / 100 (High) per canon clamp((0.6·E + 0.4·C)·S − P, 0, 100), E=94, C=92, S=1.0, P=3.`
- H2 `Analysis`; H3 is a full sentence: "Conclusion-first: the pack is analysis-ready for the full Wood Mackenzie covenant / refinancing + earnings + ratings workstream, with a single peripheral limitation (license-restricted rating cells) that does not gate any core module."
- H2 `Analytical appendix — canonical registers (T1–T8)` (note: CP-0's registers are T1–T8, not P1–P8):
  - **T1 — CP-PARSE handoff / lineage validation**: `Field | Value`. Ex: `Upstream module / run | CP-PARSE / WoodMackenzie_CP-PARSE_20260821`. Other fields: Preparation status `READY (pack confidence 92, High)`, Delivery mode, Inventory completeness, Representation uniqueness, Anchor copy, `Verdict | **ACCEPT**`.
  - **T2 — Frozen representation catalog (active representation per source)**: `# | Source (short) | Active representation | CP-PARSE mode | Limitation carried`. Ex: `1 | Credit Agreement (2024) [Exec] | PARSED_DERIVATIVE | LEGAL_CLAUSE | —`. 28 sources, ranges. Values: PARSED_DERIVATIVE, CONNECTOR_CONTENT (PASS_THROUGH); modes LEGAL_CLAUSE, LAYOUT_TEXT→LEGAL_CLAUSE, TABLE_FIRST, SLIDE_CHART, LAYOUT_TEXT, SHEET_RANGE; em dash for null.
  - **T3 — Source identity & stability**: `Identity class | Sources | Validation | State`. Ex: `CONNECTOR_NATIVE (SharePoint/OneDrive) | all 28 | Connector identity/version confirmed on live read; byte-SHA not applied (no-SHA policy) | NOT_VERIFIABLE-by-SHA → **limitation, not a block**`. Rows METADATA_ONLY / BYTE_NATIVE "none".
  - **T4 — Source usability (authority vs representation)**: `Dimension | Assignment` (Authority; Binary/content fidelity; Representation neutrality; Recorded deficiencies).
  - **T5 — Objective-agnostic authority hierarchy**: `Tier | Members` (Controlling primary; Issuer / agency; Dated external; User / unattributed context).
  - **T6 — Active content → module map (active representation IDs only)**: `Consumer | Primary active sources`. Ex: `CP-1 Canonical financials | 4–6, 7–13, 14–18`. 13 rows.
  - **T7 — Gaps & conflicts log (no silent reconciliation)**: `ID | Type | Detail | Disposition`. Ex: `G1 | Coverage/license | Moody's & S&P rating cells in primary-export.xlsx show export-license placeholders | Retained verbatim; CP-1C / CP-2H / CP-3 flagged READY_WITH_LIMITATIONS; agency PDFs (24–26) supply independent anchors`. IDs G1, C1 Version/period, C2 Time series, C3 Coverage, C4 Amount-basis, C5 Estimate vs actual.
  - **T8 — Downstream readiness verdict (minimum-missing-evidence per consumer)**: `Consumer | Verdict | Minimum missing evidence (if any)`. Ex: `CP-1C | READY_WITH_LIMITATIONS | Licensed Moody's/S&P export cells (use agency PDFs)`; most rows `READY | —`; `CP-5, CP-6 | READY | Gated on completion of upstream analytical modules`.
- Not seen: QA / Evidence Trace section of CP-0 (36.31 ends at T8's last row).
- Citations (35.37, 35.50): `turn1search85`, `turn1search89`, `turn1search29turn1search30turn1search31` (italic, run together, no spaces).

### CP-1 — FinancialDataFoundations (stage 3) (shots 37.33–38.39)
- Header: confidence 90 High; qa Passed; committee `Committee Ready`; limitation_flags `[PERIOD_BASIS_QTD_VS_YTD_MIX, EBITDA_MULTI_BASIS_REPORTED_ADJ_CONSOLIDATED, FX_CLASSIFICATION_PRESENTATION_DELTA, GOODWILL_AMORT_PCC_POLICY_BREAK_FY25, LICENSE_RESTRICTED_RATING_CELLS_NOT_USED]`.
- H2 `Audit Summary`. `Result: PASS — CANONICAL FINANCIAL BASE ESTABLISHED (COMMITTEE-GRADE).` Bullets `Lineage accepted.` `Entity perimeter frozen.` `Coverage.` "Four definitional conflicts logged (C4, C5, C6, C7) plus one policy-break normalization" `Confidence 90 / 100 (High) per canon clamp(...), E=94, C=95, S=1.0, P=3 (one MINOR: QTD/YTD basis mix ...)`.
- H2 `Analysis`; H3 `Financial base read-through`; numbered list 1.–3. ("Three quantified decision drivers": Amount-basis (C4); EBITDA multi-basis (C6); Goodwill-amortization policy break (FY2025)). Table `Key credit metrics — canonical base (latest + comparators)`: `Metric ($m unless noted) | FY2024 | FY2025 | LTM Mar-26 | Basis / note`. Ex: `Revenue (GAAP) | 594.0 | 623.0 | 630.0 | Reported; +def-rev adj → Adj. Rev 624 / 668 / 665`. Italic `Takeaway before detail:`.
- H2 `Analytical appendix — complete canonical registers` (A-series, all financial statements; negatives in parentheses `(31.2)`, null `—` never zero; italic `Notes:` under each):
  - **A1 — Canonical Income Statement — annual (Planet Holdco 2 Ltd consolidated, US$m)**: `Line | FY2023 (audited) | FY2024 (audited) | FY2025 (audited)`. Ex `Revenue (GAAP) | 520.8 | 594.0 | 623.0`.
  - **A2 — Canonical Income Statement — quarterly QTD (US$m; lender presentation p.14 ...)**: `Line | Dec-24 | Mar-25 | Jun-25 | Sep-25 | Dec-25 | Mar-26`. Ex `Revenue | 153.8 | 150.7 | 154.8 | 160.4 | 157.5 | 157.4`.
  - **A3 — §5.01 reported ...** (caption only visible, cut at bottom of 38.10; table not seen).
  - **A4 — Canonical Balance Sheet — quarterly (US$m; lender presentation p.15)**: same six period columns. Ex `Cash & cash equivalents | 120.1 | 123.8 | 114.0 | 136.8 | 138.6 | 161.9`.
  - **A5 — Canonical Cash Flow — quarterly QTD (US$m; lender presentation p.16)**: same columns. Ex `Net cash from operating activities | 16.3 | 25.5 | 18.1 | 47.6 | 16.4 | 43.0`. (A5 cut at bottom of 38.23.)
  - **A6 — Debt & tranche schedule (executed Credit Agreement 09-Feb-2024 + Amendment No.1 27-Nov-2024)**: `Tranche | Borrower | Amount | Key terms | CUSIP | Source`. Ex `First Lien Term Loan B | Planet US Buyer LLC | Gross principal **$1,292.0m** (Mar-26); carrying **$1,269.3m** | 1% p.a. amort (§2.09), ~$3.3m/qtr; maturity **2031**; repriced by Amendment No.1 (27-Nov-24) | 72706RAB2 | Exec CA; Amd.1; S&P`.
  - **A7 — Liquidity register (Mar-26)**: `Component | $m | Source`. Ex `Cash & cash equivalents | 161.9 | Q1'26 §5.01 report / lender deck`; `Total committed liquidity | **311.9** (deck: $312m) | Lender deck p.8`.
  - **A8 — EBITDA reconciliation register (QTD, US$m; lender presentation p.13)**: `Basis | Dec-24 ... Mar-26`; rows Reported EBITDA, Adjusted EBITDA (CA add-backs), Consolidated EBITDA (incl. def-rev). Italic footnote "FY2025 audited build (Q4-25 compliance certificate): ..." cut off at bottom of 38.39.
  - (A9, A10 referenced elsewhere, e.g. "CP-1 A10", not seen.)
- No citation markers seen.

### CP-1A — BusinessTransactionFactPack (stage 4; absorbs CP-2C GovernanceSponsorScore) (shots 38.54–41.20)
- Header: confidence 90 High; qa Passed; Committee Ready; `sponsor_governance_risk_level: Medium`.
- H1 `CP-1A — Business Transaction Fact Pack (incl. absorbed CP-2C) — Wood Mackenzie (Planet Holdco 2 Ltd / Planet US Buyer LLC)`. H2 `Module Result`: `Result: PASS — COMMITTEE-GRADE TRANSACTION / OWNERSHIP / CAPITALISATION FACT PACK ESTABLISHED.` Bullets `Dependency satisfied.` `Entity perimeter frozen.` `Transaction spine.` `Capitalisation (Mar-26, re-anchored from CP-1).` `Governance (absorbed CP-2C). Sponsor/Governance Risk Level = **Medium**` `Confidence 90 / 100 (High) per canon clamp(...) E=93, C=92, S=1.0, P=3.`
- H2 `Analysis`; H3 `Analytical read-through`; snapshot table (39.16): `Dimension | Source-supported fact | Status | Credit relevance | Source`. Ex `Business | Global energy/renewables/natural-resources data, analytics, research & consulting (Lens platform); HQ Edinburgh; ~2,200 staff | FY26 ongoing | Sticky subscription base; low asset intensity | Q1'26 §5.01; S&P Jan-26`. Dimensions: Business, Transaction, Refinancing, Ownership, Capital structure, Documentation, Ratings, Governance/sponsor.
- H2 `Analytical appendix — complete canonical registers` with R-series, **titles carry snake_case ids**:
  - **R1 — source_classification**: `Source ID | Source class | Quality | Use | Limitation`. Ex `1 — Credit Agreement 09-Feb-2024 [Exec] | Controlling primary (legal) | High | Tranche/agent/borrower identity | —`. Quality: High, Medium-High, Medium, Low.
  - **R2 — transaction_summary**: `Transaction | Status | Credit relevance | Source`. Ex `Veritas Capital acquisition of Wood Mackenzie (from Verisk) — closed 01-Feb-2023, $3.15bn ($2.15bn equity + $1.25bn debt) | Completed | Origin of goodwill/intangibles, TLB and equity cushion; Verisk TSA wound down by 31-Jul-2024 | CP-1 A10; Q2'24 §5.01; WoodMac workbook`. Status: Completed, Executed.
  - **R3 — company_description**: `Issuer | Business description | Country | Sector` (1 row).
  - **R4 — revenue_business_mix**: `Business line | Revenue mix | Period | Status | Limitation`. Ex `Subscription / research (recurring) | Majority of revenue; ACV $545m (+4% YoY) | Mar-26 (LTM) | Growing mid-single-digit | Segment $-split not printed in retained reps`.
  - **R5 — ownership_register**: `Owner / class | Control | Economic interest | Credit relevance | Source`. Ex `Veritas Capital (via Planet TopCo LP) | 100% sponsor control; PE board | Controlling common equity | Finite hold horizon; financial-policy setter; monitoring-fee recipient | CP-1 A10; WoodMac workbook; S&P`.
  - **R6 — operating_model**: `Operating driver | Measure | Period | Status | Credit relevance`. Ex `Annual Contract Value (ACV) | $545m (+4% YoY) | Mar-26 | Growing | Forward recurring-revenue visibility`.
  - **R7 — events_timeline**: `Date / window | Event | Credit relevance | Status | Source`. Ex `01-Feb-2023 | Veritas Capital buyout closes ($3.15bn) | LBO origin; goodwill/intangibles created | Historical | CP-1 A10`. Status: Historical, Executed, Flagged, Current.
  - **R8 — credit_translation**: `Evidence | Risk mechanic | Credit implication | Confidence | Limitation`. Ex `~68% equity-funded buyout ($2.15bn of $3.15bn) | Thick junior cushion absorbs first-loss ahead of TLB | Supportive of first-lien recovery; lowers LGD | High | Buyout equity quantum from workbook (context source), not audited`.
  - **R9 — gaps_ledger**: `Gap | Affected analysis | Severity | Action | Status`. Ex `Buyout sources & uses / exact equity cheque not in an audited source | Ownership economics; equity-at-risk sizing | Medium | Obtain 2023 S&U / SPA schedule | Open`. Severity Medium/Low; Status Open/Deferred/Substantially closed.
  - **R10 — conflict_log**: `Conflict | Sources | Materiality | Resolution | Downstream impact`. Ex `TLB gross principal vs carrying | Lender deck $1,292.0m vs BS $1,269.3m | Medium | Canonical = carrying $1,269.3m; gross labelled (inherited C4) | Leverage denominator basis (CP-2, CP-3)`. (40.41 cuts after first R10 row.)
  - H2-ish `Governance & Sponsor View (absorbed CP-2C — GovernanceSponsorScore)`; H3 `Governance view` ending "Sponsor / Governance Risk Level: Medium." Then T2D-series (named T2D.x here although the module is CP-1A):
    - **T2D.1 — Source classification (governance perimeter)**: **snake_case column headers** `source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use` (8 cols; WIDE, last column cut at right edge in 40.58). Ex `1 | Credit Agreement 09-Feb-2024 [Exec] | High | 2024 | Borrower/Guarantors | Guarantee/collateral, agent, control provisions | Full basket sizing not extracted in CP-1A | CP-4/CP-4A capacity`.
    - **T2D.2 — Ownership, sponsor & control register**: `Item | Source-Supported Fact | Evidence Quality | Source Trace | Credit Mechanic | Credit Implication | Limitation` (7 cols). Ex `Sponsor | Veritas Capital, 100% control via Planet TopCo LP | High | CP-1 A10; S&P; workbook | Control of financial policy/board | Finite-hold event risk (recap/sale/M&A) | Fund vintage not in pack`.
    - **T2D.3** (title cut off, governance/disclosure topics): `Governance Topic | Source-Supported Fact | Risk Direction | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace | Limitation` (8 cols). Ex `Reporting/disclosure | Quarterly §5.01 reports + compliance certs + lender calls/decks | Favourable | Enables covenant/leverage monitoring | Lower information-risk premium | High | §5.01 reports; certs | Private (no public filings)`. Risk Direction: Favourable, Neutral-favourable.
    - **T2D.4 — Sponsor / shareholder behaviour flags**: `Flag ID | Behavior Type | Documented Action | Behavior Category | Amount / Funding Source | Legal-Capacity Link | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace` (10 cols, widest table seen). Ex `B1 | Monitoring-fee extraction | Recurring management fee added back to EBITDA | Extraction (routine) | ~$13m/yr; operating cash | Permitted RP/fee basket (CP-4) | Cash leakage + EBITDA optics inflation | Modest FCF drag; leverage flattered | High | Lender deck p.13`. Behavior Category: Extraction (routine), Creditor-adverse (mild), Support, Creditor-adverse (capacity), Neutral. Flags B1–B5.
    - **T2D.5 — Capital-allocation risk table**: `Capital Allocation Item | Source-Supported Fact | Direction | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace | Limitation`. Ex `Debt reduction | Mandatory 1% p.a. amort (~$3.3m/qtr) only; no voluntary paydown observed | Neutral | Minimal deleveraging ex-EBITDA growth | Deleveraging relies on EBITDA, not cash sweep | High | CP-1 A5/A6 | Excess-cash-flow sweep not sized`. Direction: Neutral, Watch.
    - **T2D.6 — Acquisition appetite & integration**: `Acquisition / Period | Source-Supported Fact | Funding Mix | EBITDA / Pro Forma Basis | Integration Evidence | Leverage / Liquidity Effect | Risk Mechanic | Credit Implication | Source Trace | Limitation` (10 cols); a cell reads `[Insufficient Information] — no bolt-ons evidenced`.
    - **T2D.7 — Disclosure quality log**: `Disclosure Item | Available? | Source-Supported Detail | Credit Relevance | Severity | Source Trace | Required Follow-Up`. Ex `Quarterly financials | Yes | §5.01 reports Q1'24→Q1'26 (7) | High — leverage/liquidity monitoring | Low | §5.01 reports | Obtain any standalone Q4 (none exist)`. Available?: Yes/Partial. Cut at bottom of 41.20; horizontal scrollbar visible.
- Not seen: CP-1A Downstream Handoffs / QA & Governance.

### CP-1B — EarningsDelta (stage 5) (shots 41.32–42.33)
- Header: reporting_period `FY2024→FY2025 audited YoY; LTM Dec-25 → LTM Mar-26 sequential; QTD Q1'25 → Q1'26`; confidence 89 High; qa Passed; Committee Ready; limitation_flags 5 (EBITDA_MULTI_BASIS_..., PERIOD_BASIS_QTD_VS_YTD_MIX, GOODWILL_AMORT_PCC_POLICY_BREAK_FY25, NO_STANDALONE_Q4_QUARTERLY_REPORT, SEGMENT_LEVEL_ACV_SPLIT_NOT_DISCLOSED); upstream CP-0 `cp1b_readiness: READY`, `active_sources: "7–13, 4–6, 22, 23"`.
- H1 `CP-1B — EarningsDelta — Wood Mackenzie (Planet Holdco 2 Ltd / Planet US Buyer LLC)`; H2 `Module Result`; `Result: PASS — EARNINGS-DELTA VARIANCE BRIDGES ESTABLISHED (COMMITTEE-GRADE).` Bullets `Dependency satisfied (live).` ... `Confidence 89 / 100 (High) per canon clamp(...), E=93, C=92, S=1.0, P=4 (one MINOR: QTD/YTD basis mix; one MINOR: deferred-revenue adjustment volatility ...)`.
- H2 `Analysis`; H3 `Conclusion-first read-through`; "The contrary case, carried unblended:". H2 `Analytical appendix — variance bridges (B1–B8)` (H3 per bridge, each followed by italic note):
  - **B1 — Revenue delta (three lenses; GAAP vs Adjusted/billing basis)**: `Lens | Basis | From | To | Δ$ | Δ% | Driver`. Ex `FY24 → FY25 | GAAP | 594.0 | 623.0 | +29.0 | +4.9% | Organic ACV + consulting growth`.
  - **B2 — Consolidated EBITDA walk — LTM Dec-25 → LTM Mar-26 (the "new-results" delta)**: `Line ($m) | LTM Dec-25 | LTM Mar-26 | Δ | Read`. Ex `Reported EBITDA (P&L) | 190 | 189 | −1 | Underlying operating EBITDA flat`. Walk rows prefixed `+ ` and `= `; last row `= Consolidated EBITDA (CA-defined) | 296 | 281 | −15 (−5.1%) | Denominator fall — non-operating`.
  - **B3 — Reported (P&L) EBITDA build — cross-tie (LTM)**: `Component ($m) | LTM Dec-25 | LTM Mar-26 | Δ`. Ex `Net income (loss) | (238) | (272) | −34`.
  - **B4 — Cash conversion (LTM) — the divergence from accounting EBITDA**: `Metric ($m) | LTM Dec-25 | LTM Mar-26 | Δ`. Ex `Net cash from operating activities | 107.6 | 125.1 | +17.5`.
  - **B5 — Leverage progression (denominator-driven)**: `Basis | LTM Dec-25 | LTM Mar-26 | Δ | Note`. Ex `Net leverage — mgmt (gross principal / Consolidated EBITDA) | 3.9x | 4.0x | +0.1x | Company reports 4.02x at Mar-26`.
  - **B6 — Liquidity delta (Mar-26)**: `Component ($m) | Dec-25 | Mar-26 | Δ`.
  - **B7 — Operating / KPI delta**: `KPI | Prior | Latest | Δ | Credit read`. Ex `ACV | $522m (FY25 exit −5% YoY comp) | $545m (Mar-26) | +4% YoY | Forward recurring-revenue visibility intact`.
  - **B8 — Quarterly momentum (QTD, the leading indicator)**: `Metric | Q1'25 | Q1'26 | Δ | Driver (lender call)`. Ex `Revenue (GAAP, 3-mo) | 150.7 | 157.4 | +4.4% | ACV growth flow-through`.
- H2 `Conflicts & gaps register (no silent reconciliation)`: `ID | Type | Detail | Disposition`. Ex `D1 | EBITDA multi-basis | Reported $189m / Adjusted $246m / Consolidated $281m LTM Mar-26 | All three retained & labelled (inherited CP-1 C6); leverage denominators must state basis` (D1–D5).
- H2 `Downstream readiness`: `Module | Status | Handoff`. Ex `CP-2 (fundamental synthesis) | READY | Consume EBITDA-basis bridge + leverage denominator caveat`. 42.33 ends here; QA section not seen.

### CP-1C — PeerBenchmark (stage 4) (shots 42.52–43.13)
- Header (42.52): confidence **73 Medium**; qa_status `Passed with material limitations`; committee_status `USABLE_WITH_LIMITATIONS`; limitation_flags 7 (INTERNAL_PEER_EXPORT_LICENSE_RESTRICTED, PEER_FINANCIALS_WEB_SCRAPED_UNVERIFIED, LIVE_MARKET_EV_MULTIPLES_NOT_RETRIEVED, ...); validation_warnings 3 (PEER_N_5_THIN_FOR_AVERAGE_GATE, DNB_NOW_PRIVATE_NO_LIVE_TRADING_MULTIPLE, WOODMAC_MARGIN_BASIS_MUST_BE_STATED); upstream CP-0 `cp1c_readiness: READY_WITH_LIMITATIONS`. H1 not in crop.
- H2 `Audit Summary`: `Result: READY WITH MATERIAL LIMITATIONS — USABLE_WITH_LIMITATIONS.` Bullets `Dependency gate satisfied.` `Peer-First Gate.` (code chips `peer_set: auto_discover_and_verify`, `source_mode: reputable_public_web`; tag "Web-Scraped — Unverified") `Selected peers (N=5): ...` `Headline positioning.` `Confidence 73 / 100 (Medium): ...`.
- H2 `Analysis`; H3 `Credit view`; table `Borrower-versus-peer snapshot` (bold caption): `Metric (latest) | Wood Mackenzie | Peer median | Peer range (min–max) | Borrower position`. Ex `Revenue growth (organic/GAAP) | ~+4.9% | +3.7% | −4.0% to +6.6% | Upper-mid`. Position vocab: Upper-mid, Mid-pack, High end (leveraged cohort), Negative outlier, Low end. Then `Decision driver 1/2/3 — ...` with plain "Risk mechanic:" "Credit implication:" and `Strongest contrary view & what would make it win.` (43.05 has a strikethrough glitch from `~`).
- H2 `Analytical appendix — complete canonical registers`; italic Reading note ("workflow order ≠ reading order ... Web-Scraped — Unverified unless tagged Document-Disclosed ... Null ≠ zero"):
  - **T4.D1 — Web-Scrape Discovery Register (conditional; auto-discovery provenance)** (bold caption, not a heading): `Candidate | Discovery source (provenance) | Comparability dims met (of 16) | Promotion decision | Evidence tag`. Ex `Clarivate Plc (CLVT) | Company FY2025 release / SEC 8-K (24-Feb-2026) | ≥8 (subscription B2B intelligence; ~4x lev; PE heritage; margin band) | PROMOTED | Web-Scraped — Unverified`. Decisions: PROMOTED, PROMOTED (quality/valuation anchor), NOT PROMOTED; tag `Excluded (scale/quality mismatch)`. Literal `**former parent of WoodMac**` and `**energy-vertical**` asterisks visible in cells.
  - **T4.1 — Peer Universe Register**: `Entity Name | Peer Category Label | Source of Selection | Dimensions Assessed | Strengths | Limitations | Data Availability | Evidence Quality Tier | Usable For | Exclusion Reason` (10 cols; last col cut off at right). Ex `Clarivate (CLVT) | Public-Company / Close-Comparable | Web scrape (auto) | Model, subscription mix, leverage, margin, scale | Subscription-first intelligence; net lev ~4x ≈ WoodMac; PE heritage | Different verticals (IP/LS/academia); FY25 revenue declining on divestitures | High (public filings) | Public-Company — Web-Scraped Unverified | Operating, leverage, valuation | —`.
  - T4.2–T4.10 are referenced ("T4.5–T4.10") but not seen.

### CP-2 — FundamentalCredit (stage 6) (shots 43.28–46.01)
- Header (43.28): confidence **86 High**; qa_status long parenthetical `Passed (contract + identity fail-closed; CP-1 re-anchor validated; ...)`; Committee Ready; `frontmatter_limitation_flags` 8 bullets (LEVERAGE_DEFINITION_SPREAD_4p0x_MGMT_VS_7p3x_SANDP_ADJ, ...). upstream verdict strings now `PASS (Committee Ready, conf 90)` and CP-1C `USABLE_WITH_LIMITATIONS (conf 73)`. predecessor_note quotes the route rule: "CP-2 Needs CP-1, CP-1A, CP-1B, CP-1C ... Gate cleared — FULL RUN. Not fail-closed."
- H1 `CP-2 — Fundamental Credit — Wood Mackenzie (Planet Holdco 2 Ltd / Planet US Buyer LLC first-lien TLB)`; H2 `Module Result`; `Result: PASS — FUNDAMENTAL CREDIT VIEW ESTABLISHED (COMMITTEE-GRADE).` "The one-sentence credit view." 8 bullets (Fundamental anchor; The binding constraint; The most recent delta is definitional, not operational; The genuine early-warning signal is QTD margin; Cash conversion is the offset; Refinancing outlook; Governance — Medium (absorbed CP-2C); `Confidence 86 / 100 (High).` without a formula line).
- H2 `Analysis`; H3 `Fundamental credit view (conclusion-first)`; numbered 1–3; bold `Net:`. Tables (H2-sized captions): `Capital structure & leverage snapshot (inherited from CP-1 / CP-1A)`: `Item ($m unless noted) | Value (Mar-26 / LTM) | Basis / note` (ex `First-lien TLB — gross principal | 1,292.0 | Lender deck; alternative basis (C4)`); `Business & structural snapshot (inherited from CP-1A)`: `Dimension | Fact | Credit relevance`; `Deleveraging trajectory (conclusion-first)`: `Metric | LTM Dec-25 | LTM Mar-26 | Trend / read` (ex `Consolidated EBITDA ($m) | 296 | 281 | ▼ −$15m — 100% definitional (−9 def-rev adj, −5 PF savings; Reported flat)`; glyphs ▲ ▼).
- Then H2s: `Relative positioning (inherited from CP-1C)`; `Evidence → risk mechanic → credit implication`; `Strongest contrary view (carried, unblended)`; `Downstream Handoffs & Recommended Next Command` (bullets keyed `CP-2A (Downside Pathway):` `CP-2D (Liquidity & Cash-Flow Bridge):` `CP-2H (Ratings Migration):` `CP-3 / CP-3C (Relative Value / Refinancing):` `CP-4 / CP-4A / CP-4B (Covenant/Legal):` `CP-5 / CP-6 (QA / IC):`; "Recommended next command:" in a code chip `Run CP-2A [issuer: Wood Mackenzie; perimeter: Planet Holdco 2 Ltd]`); `QA & Governance` (46.01).
- **QA & Governance bullets (exact labels)**: `Identity / lineage:` `No-SHA policy:` `Fail-closed checks:` "Filename: WoodMackenzie_CP-2_20260825.md (issuer_id / module_id / analysis_date) — validated." "Confidence 86 / High; qa_status Passed; committee_status Committee Ready. Prohibited outputs (instrument ranking, recovery quantification, equity valuation, individual-person evaluation) not asserted." "Artifact: this Markdown is the sole canonical handoff (no DOCX/PDF/HTML/JSON/slide). Chat is non-canonical. Move export to the _RUNS folder."
- Boundary between 45.42 and 45.52 content assigned from reading order; the two screenshots are CP-2 body continuation (business snapshot, deleveraging table; then relative positioning, evidence bullets, contrary view).

### CP-2A — DownsidePathway (stage 7) (shots 46.47–47.46)
- Header: confidence 84 High; Committee Ready; limitation_flags 5 (SANDP_ADJ_EBITDA_DENOMINATOR_INFERRED_NOT_DISCLOSED, ...); `predecessor_note: >-` and `currency_basis: >-` literal markers.
- H2 `Module Result`: `Result: PASS — DOWNSIDE PATHWAYS ESTABLISHED (COMMITTEE-GRADE).` 7 bullets, `Confidence 84/100 (High).`, `Downside verdict:`.
- H2 `Analysis`; H3 `Downside view (conclusion-first)`, `First-break discipline (why margin, not demand, breaks first)`, `Stress transmission (directional vector logic)`. Strikethrough glitch from `~` on "(~$246m), lifting mgmt-basis leverage ~4.02x→~4.59x".
- Tables (T2A.x ids in H2/H3-sized captions):
  - **T2A.1 — Leverage breakpoint ladder (the binding axis)**: `EBITDA path (Δ vs frozen) | mgmt net leverage | S&P-adjusted leverage | Meaning`. Ex `Base (frozen) | 4.02x | 7.30x | Company reports 4.02x; S&P FY26e 7.3x / negative`. Rows −2.67%, −10%, −15% (S&P liquidity test), Def-rev add-back → 0, Flat EBITDA, FCF-only paydown.
  - **T2A.2 — Source register (inherited, frozen)**: `Source / module | Quality | Period | Data supplied | Downstream use`. Ex `WoodMackenzie_CP-1_20260825 | Accepted upstream (conf 90) | FY23–Q1'26 | Canonical debt/EBITDA multi-basis/liquidity/leverage | Quantitative anchors`; Quality values `Primary (agency)`, `Issuer call`.
  - **T2A.3 — Fragility map (first-break ranking)**: `Fragility driver | First break point | Evidence | Risk mechanic | Credit implication | Confidence`. Ex `Consulting margin / transformation opex | QTD Consolidated EBITDA −9.5% persists 2–3 quarters | CP-1B B8; lender call | Margin compression → agency leverage rises fastest | Primary rating-migration driver | High`. Confidence: High, Medium, `Medium (→CP-4)`.
  - **T2A.4 — Stress transmission table**: `Operating / definitional stress | EBITDA impact | Leverage / rating result | Credit consequence | Evidence status`. Ex `Consulting timing + transformation opex (QTD −9.5%) | Consolidated EBITDA compresses | −2.67% → 7.5x trigger; −10% → 8.1x | Downgrade risk; wider 2031 spread | Source fact (QTD) + [CP-2A calc]`. Evidence status: `Source fact (docs)`, `Directional`, `S&P + [CP-2A calc]`.
  - **T2A.5 — Downside pathway register**: `Row ID | Pathway category | Driver | Causal vector | Consequence | Confidence | Downstream`. Ex `CP-2A-DP-001 | First break point | Consulting margin / transformation opex | QTD −9.5% EBITDA persists → agency leverage → 7.5x trigger | Downgrade / refinancing-cost escalation | High | CP-2H, CP-2G, CP-3C`. Categories: First break point, Transmission accelerator, Structural constraint, Terminal consequence, Recovery (LGD) vector.
- H2 `Downstream Handoffs & Recommended Next Command` (code chip `Run CP-2G [issuer: ...; perimeter: ...]`); H2 `QA & Governance` (cut off mid-list at the bottom of 47.46).

### CP-2E — MacroFXHedgingSensitivity (stage 8) (shots 48.08–49.08)
- Header: confidence **76 Medium**; limitation_flags 7 (HEDGE_NOTIONAL_TENOR_STRIKE_NOT_DISCLOSED_IN_RETAINED_SOURCES, RATE_LADDER_RUN_ON_UNHEDGED_FLOATING_BOUND_CONSERVATIVE, ...); CP-2D noted absent (soft predecessor). qa_status/committee_status not visible in header crop but stated in QA & Governance.
- H2 `Module Result`: `Result: PASS (MEDIUM CONFIDENCE) — MACRO/RATE/FX SENSITIVITY ESTABLISHED; HEDGE LIMB SOURCE-GAPPED.` 7 bullets with refs like `[CP-2E calc; CP-2A T2A.1]`; `Confidence 76 / 100 (Medium).` with deductions (i)–(v); `Macro verdict:`.
- H2 `Analysis`; H3 `Macro view (conclusion-first)`;
  - **T2E.1 — Interest-rate sensitivity ladder (unhedged floating bound)**: `Rate shock (SOFR) | Cash interest ($m) | Reported-EBITDA coverage | Consol-EBITDA coverage | LTM FCF ($m) | FCF conversion | Read`. Ex `−100bps | 81.6 | 2.32x | 3.44x | 73.9 | 26.3% | Modest relief; deleveraging still slow`. Base row bold: `Base (frozen) | 94.5 | 2.00x | 2.97x | 61.0 | 21.9% | CP-2A anchor`.
  - **T2E.2 — FX sensitivity ladder (adverse = GBP strengthens vs USD)**: `FX move | USD cost Δ ($m) | Consol EBITDA ($m) | EBITDA Δ% | mgmt net leverage | S&P-adjusted leverage | Trigger?`. Ex `GBP +5% | +6.0 | 275.0 | −2.1% | 4.11x | 7.47x | Approaching 7.5x`; a bold row `THROUGH trigger`; italic `Threshold` row.
  - **T2E.3 — Combined macro tail (rate + FX simultaneous)**: `Scenario | Cash interest | Reported coverage | Consol EBITDA | mgmt leverage | S&P-adj leverage | LTM FCF / conv.`. Ex `Base (frozen) | $94.5m | 2.00x | $281m | 4.02x | 7.30x | $61.0m / 21.9%`.
  - **T2E.4 — Hedge-cliff analysis (source-gapped — flagged, not sized)**: `Element | What the retained sources show | What is NOT disclosed | Treatment`. Ex `Hedge existence | Lender-deck balance sheet carries a "Derivatives – Liability" line ($2.2 / 4.1 / 3.2 / 2.2 / 0.4m across quarters) | Instrument type (swap vs cap/collar) | Confirmed a rate hedge exists`.
- H2 `Evidence → risk mechanic → credit implication`; H2 `Downstream Handoffs & Recommended Next Command` ("Issuer follow-up (data request): ... would lift CP-2E from Medium to High confidence." Recommended next command here in plain text, not code chip); H2 `QA & Governance` (49.08, tight crop): same labels; "Confidence 76 / Medium; qa_status Passed; committee_status Committee Ready (with hedge-terms data caveat)."

### CP-2D — LiquidityCashFlowBridge (stage 9) (shots 49.19–50.00)
- Header: confidence 86 High; limitation_flags 6 (CASH_INTEREST_SPLIT_INFERRED_FROM_2p0x_COVERAGE_NOT_DISCLOSED, CASH_TAX_NOT_SEPARATELY_DISCLOSED_EMBEDDED_IN_OCF, ...); validation_warnings `LTM_CASH_FLOW_SUMMED_FROM_QTD_LENDER_DECK_NOT_STANDALONE_LTM_STATEMENT`.
- H2 `Module Result`: `Result: PASS — NEAR-TERM LIQUIDITY BRIDGE ESTABLISHED (COMMITTEE-GRADE). Liquidity Risk Level: STRONG.` Chips `[CP-2D calc on CP-1 A5]`; `Confidence 86 / 100 (High).`; `Liquidity verdict:`.
- H3 `Liquidity view (conclusion-first)`; table **EBITDA → cash bridge (LTM Mar-26, consolidated)**: `Bridge line | US$m | Basis / source`. A walk of 17 rows with italic `less` / `plus` prefixes and `= ` subtotal rows in bold, numbers right-aligned, negatives in parentheses, `n/a (embedded)`, chips `[CP-2D calc]` `[inferred – not separately disclosed]` `[limitation]`, a trailing `✓`. Ex `Consolidated EBITDA (CA-defined) | 281.0 | CP-1 A8 (LTM Mar-26); leverage denominator only`.
- **Sources & uses — forward 12 months (from Mar-26)**: `(blank) | US$m | Note` (first header cell empty); section-label rows `Sources (committed, standing)` and `Uses (mandatory, next 12m)`; ranges `~172–178`; `Maturities in window | 0.0 | RCF 2029 / TLB 2031 — no wall`.
- H3 `Revolver access & covenant posture` (chip `[limitation: RCF_SPRINGING_COVENANT_TRIGGER_PENDING_CP4]`).
- H3 `Cash runway & stress (why the runway is non-binding)`: `Scenario | Cash interest | FCF (post-capex) | Runway read` (ex `Base (LTM Mar-26) | 94.5 | +61.4 | Self-funding; $311.9m untouched`; text cells `float-dependent`, `compresses`).
- H2 `Evidence trace` (sentence case): `Claim / metric | Evidence (source, period) | Risk mechanic | Credit implication | Confidence`. Ex `OCF $125.1m; FCF $61.4m LTM | CP-1 A5 (Σ QTD Jun-25→Mar-26) | Self-funding cash engine | Liquidity non-binding | High`; Confidence `Medium [inferred]`.
- Not seen: Downstream Handoffs / QA & Governance for CP-2D (50.00 ends at a rule after Evidence trace).

### CP-2G — ForwardCreditModel (stage 10) (shots 50.15–50.51)
- Header: confidence 85 High; qa_status parenthetical; Committee Ready; limitation_flags 8 (NO_MANAGEMENT_MULTI_YEAR_FORECAST_PROVIDED, ..., 2031_TLB_WALL_BEYOND_3YR_EXPLICIT_HORIZON_GLIDE_ONLY). upstream roles marked `(advisory)`.
- H2 `Module Result`: `Result: PASS — FORWARD CREDIT MODEL ESTABLISHED (COMMITTEE-GRADE).` 8 bullets (the last `Confidence 85/100 (High).` citing limitation ids LG3, LG-SP, LG1, LG2). Assumption ids `A-CONS-B`, `A-REP-B`, `A-PAY-B/U`, `A-CONS-D/U`.
- H2 `Analysis`; H3 `Forward credit view (conclusion-first)`; table caption "Forward-credit trajectory (values from appendix registers T2H.4–T2H.6; US$m, FYE 31-Dec; all [CP-2G calc])": `Case / metric | LTM Mar-26 (A) | FY2026e | FY2027e | FY2028e`. Ex `Base — Mgmt net leverage | 4.02x | 3.74x | 3.36x | **2.98x**` — **literal `**` markdown asterisks show in cells** (bold failed inside table cells in 50.38). Rows: Base — S&P-adjusted leverage; Base — EBITDA/cash-int; `Upside — Mgmt net lev / S&P-adj` (cells like `4.02x / 7.30x`); Downside equivalents; `Downside — (EBITDA−capex)/int`; `Downside — Total liquidity ($m)`.
- H3s: `Base case — steady cash build, slow agency de-lever (conclusion-first)`, `Upside case — BB-optic migration (conclusion-first)`, `Downside case — a rating break, not a liquidity break (conclusion-first)`, `Refinancing breakpoints & minimum-liquidity (conclusion-first)`. H2 `Evidence Trace` with plain-text "Evidence: ... Mechanic: ... Implication: ..." bullets. Appendix registers `T2H.1–T2H.9` referenced, not seen. Cut at bottom of 50.51.

### CP-2H — RatingsMigrationTriggerHeadroom (stage 11), Wood Mackenzie (shots 51.05–51.55)
- Header: confidence **82 High**; qa_status long parenthetical; committee_status `Committee Ready (with limitations — inferred S&P-adjusted denominator; no Fitch coverage in pack; ...)`; limitation_flags 7; upstream CP-0 `cp2h_readiness: READY_WITH_LIMITATIONS`; `schema_family: Nested`, `output_class: CANONICAL_MARKDOWN`, `rating_issuance: PROHIBITED_NO_RATING_ISSUED`.
- H2 `Module Result`: `Result: PASS — RATING-TRANSITION CASE ESTABLISHED (COMMITTEE-GRADE, WITH LIMITATIONS). NO RATING ISSUED.` 8 bullets, last `Confidence 82/100 (High). ... Capped — not by analytical integrity — by the inferred S&P-adjusted EBITDA denominator (CP-2G LG-SP)` (cut at bottom of 51.18). Refs: line locators `[CP-2G L77/L79/L94/L102/L107]` and PDF filenames in plain brackets.
- Rating vocabulary: Moody's `B2 CFR / B2-PD / B2 senior secured, stable`; S&P `'B' issuer credit rating, Negative outlook (B/Negative/NR)`; `B2 ≡ B`; S&P anchor `'b'`, "Highly Leveraged / Vulnerable"; drift to `B-`; dates `29-Oct-2025`, `21-Jan-2026`.
- H2 `Analysis`; H3 `Rating transition view (conclusion-first)`; H3 `Rating-trigger summary` table, 8 columns, narrow wrapped cells, very tall rows (51.26): `Agency | Current verified posture | Date / source | Nearest published downgrade trigger | Nearest published upgrade/stabilise condition | CP-2G base/upside read | CP-2G downside read | Principal limitation`. Rows S&P, Moody's, Fitch (`No Fitch rating in the pack | — ...`). Bold lead-ins `Supportive —`, `Negative pressure —`. Italic note with bold `ANALYST-CONSTRUCTED` label (51.46).
- H3 `Methodology and metric bridge (conclusion-first)`; H3 `Trigger headroom and migration cases (conclusion-first)` (bold-led `S&P — the binding axis.` `Moody's — the counter-weight.` `Transition classes. Base = ... Upside = ... Downside = ...`); H3 `Agency divergence, notching & market-implied phase (absorbed CP-3D — source-limited)`.
- H2 `Evidence Trace` with intro "Evidence → Risk Mechanic → Credit Implication (each mapped to a creditor dimension; confidence and limitation stated):"; table `# | Claim / metric | Evidence (source, date, locator) | Risk mechanic | Credit implication (dimension) | Confidence | Limitation`. Ex `E1 | S&P 'B'/Negative; adj. leverage ~8x (2025e)→7.3x (2026e); downgrade if sustained >7.5x + low-single-digit FOCF/debt | S&P RatingsDirect, 21-Jan-2026 (RatingsDirect_PlanetHoldco2Ltd._3505877_Jan-21-2026.pdf) | Single first-lien, no junior cushion → ... | Negative outlook is the binding PD / rating-migration control; downside executes it (B-) | High | S&P-adjusted denominator inferred in CP-2G (LG-SP)`. E1–E4 seen (cut at E4).

### CP-3 — RelativeValueSecuritySelection (layer L3), Wood Mackenzie (shots 52.22–52.47)
- Header (52.22): confidence **57 Low**; qa_status `Passed — Ready with Limitations (RV Restricted; contract + identity validated fail-closed; ...)`; committee_status **`Requires More Work`**; module_status `Ready with Limitations`; `frontmatter_limitation_flags` 7 (RV_RESTRICTED_NO_DATED_MARKET_LEVEL_FOR_TLB, BENCHMARK_INDEX_SUPPLIED_WITHOUT_DATED_LEVEL, ...); evidence_class `full_run`. Placeholder tokens `[Insufficient Information — license-restricted]`, `[•]`.
- H2 `Module Result`: **`Result: READY WITH LIMITATIONS — SECURITY SELECTION WITHHELD PENDING DATED MARKET COMPENSATION (RV RESTRICTED).`** (no PASS word). 5 bullets; closing bullet "Composite fundamental/structural score: 3.05 / 5.0 → Credit Tier "Stretched" (composite 61/100) ... Confidence 57 / Low".
- H2 `Analysis`; H3 `Recommendation`: "Requires More Work (security selection withheld); RV = Unclear." H2-sized `Instrument & capital-structure snapshot (inherited from CP-1 / CP-1A / CP-2, not re-derived)`: `Item ($m unless noted) | Value (Mar-26 / LTM) | Basis / note`. H2-sized `Evidence → risk mechanic → credit implication (security-selection lens)`.
- H2 `Relative Value & Security Selection`: H3 `Relative-value determination (RV Restricted)` ("RV label = Unclear ... compensation-versus-risk is Not Assessable ... recommendation is capped at Requires More Work"); H3 `Security-selection conclusion (per-instrument)` ("Recommendation: Requires More Work; RV: Unclear; Fundamental/Structural Tier: Stretched (3.05/5.0)"). H2 `Downside, Recovery & Portfolio Implementation`: H3 `Recovery & structural position`, `Portfolio implementation (generic-fit only)`. H2 `Downstream Handoffs & Recommended Next Command` (bullets `CP-3B (Portfolio Fit / Position Sizing) — absorbed: registers authored below (T3C.*)`, `CP-4 / CP-4A / CP-4B (Covenant / Legal)`, `CP-6 (IC Debate)`, `CP-5 / CP-5A (Evidence & QA)`; code chip `Run CP-3 [issuer: Wood Mackenzie] [instrument: Planet US Buyer 1L TLB 2031] [as of: 2026-08-26]`). 52.47 cuts mid-sentence at bottom.
- Judgement scales: Recommendation words `Preferred` / `Neutral` / `Avoid` / `Requires More Work`; RV label `Unclear` (the other labels are not seen for WM); `Not Assessable`; tier `Stretched` with 0–5 score and composite /100; agency lens `Stretched`.
- Citations: Copilot markers appear here: `.turn1search105turn1search70` after refs such as `[CP-1 A4 / CP-1A / CP-2]`, `turn1search110turn1search121` mid-paragraph, `turn1search70` (shots 52.29, 52.37, 52.47). Italic, no spaces, glued to the preceding bracket or full stop.

### CP-4 — Legal Covenant Interpreter, Wood Mackenzie (shots 53.04–53.30)
- Screenshots start at the H1 (header block not captured; unknown). H1 `CP-4 — Legal Covenant Interpreter — Wood Mackenzie (Planet Holdco 2 Ltd / Planet US Buyer LLC first-lien TLB)`.
- H2 **`Audit Summary`**: `Result: PASS — COVENANT ARCHITECTURE CONSTRUED (COMMITTEE-GRADE).` 7 bullets (Documentation aggression is the headline; The one maintenance test is nearly inoperative; Day-one debt capacity is egregious and re-grows with EBITDA; Restricted-payment / leakage capacity is open right now; Repricing/refi friction has fallen away; Perimeter / recovery guardrails present but partial; `Confidence 84 / 100 (High).` with deductions (i)–(iii)). Chip `[CP-4 calc]`. Document scale: CovenantReview LFI11232 "Composite 5+ / Collateral Protection 5+ / Default Protection 5 / Repricing Optionality 3" (5+ = most aggressive band). Status token `Not Calculable`.
- H2 `Analysis`: H3 `Conclusion-first`; `Controlling-document construction hierarchy`; `The financial-covenant read (why lenders can't force the table)` table `Feature | Term (CA §6.08 / §8.03) | Current status | Creditor consequence` (ex `Test | Net First Lien Leverage ≤ 8.5x | ~4.0x actual → ~4.5 turns inside | Cosmetic; set ~1.75x above even the opening 4.87x`); `The debt-incurrence architecture (priming capacity)` table `Capacity route | Day-one (LFI11232, opening EBITDA $241m) | Current basis [CP-4 calc] (Consolidated EBITDA $281m) | Incurrence gate` (header cell contains a code chip; ex `Free-and-clear accordion (§2.20) | Gtr of $272m / 100% EBITDA | ~$281m | None (freebie)`; "Uncapped" repeated; bold total rows `$1,795.2m (6.6x)`); `The leakage architecture (restricted payments, investments, unrestricted subs)` table `Route | Term (CA §6.06 / §6.03) | Current availability | Creditor consequence` (ex `RP builder "Cumulative Amount" | Starter gtr $272m/100% EBITDA + 50% CNI/retained ECF + 50% deferred revenue (off-market) + equity + declined prepayments | Starter ~$281m [CP-4 calc]; builds over time | Dividend/investment leakage grows with retained earnings and def-rev`; status words `OPEN`); `Recovery guardrails — what the lender does have` (italic *does* inside the H3); `Strongest contrary view (and what would make it win)`.
- Not seen: CP-4 Evidence Trace, handoffs, QA; any CP-4 appendix registers.

### CP-2F — ESGAndSustainabilityCreditRisk, **Lambda** (shots 54.15–54.57)
- Header (54.15): run `Lambda_CP-2F_20260811`; confidence **80 High**; `esg_risk_level: Low-to-Moderate`, `operational_risk_level: Low-to-Moderate`; qa_status `Passed (...)`; committee_status `Committee Ready (with limitations — advisory reports draft; Tier III compliance not independently validated; OEM break/fix not contractually evidenced)`; limitation_flags 8 (ADVISORY_REPORTS_DRAFT_STATUS_TDD_AND_INSURANCE, TIER_III_COMPLIANCE_NOT_INDEPENDENTLY_VALIDATED_MMI, ...); downstream_consumers include CP-3A, CP-4B. Upstream CP-2A/2D/2E labelled `(SOFT support)`.
- H1 `CP-2F — ESG & Sustainability Credit Risk / Operational Materiality — Lambda / Project Poutine (GPV $917.2m Senior Secured Term Loan)`; H2 `Module Result`: `Result: PASS — ESG & OPERATIONAL MATERIALITY ESTABLISHED (COMMITTEE-GRADE, WITH LIMITATIONS). ESG Risk Level: LOW-TO-MODERATE. Operational Risk Level: LOW-TO-MODERATE.` (judgement scale: Low / Low-to-Moderate / Moderate ... in caps) Bullets plus `Confidence 80/100 (High).` (i)–(iv) and `ESG/operational verdict:`. Bold `[Insufficient Information]` inline. 54.22 has a black strip at the right edge (window edge).
- H2 `Analysis`: H3 `ESG & operational materiality view (conclusion-first)`; then:
  - **T2F.1 — ESG materiality matrix (transmission to CFADS / DSCR)**: `ESG pillar | Factor | Direction | In-pack evidence | Transmission to credit | Materiality`. Ex `E | Renewable hydro power (Hydro-Québec) | Positive | Lender Pres. / CP-1A | No carbon-transition opex pass-through; cost-stable power | Positive / Low risk`. Pillars E, S, G, Debt; Direction: Positive, Adverse, Neutral, Absent, —; Materiality: `Positive / Low risk`, `Low`, `Low-to-Moderate`, `Low-to-Moderate (gap)`, `[Insufficient Information]`, `Low (external)`, `See CP-2C`, `Not credit-material (today)`.
  - **T2F.2 — Operational DD register (Altman Solon TDD, draft)**: `Risk area | TDD finding | Mitigant | Residual gap | Credit read`. Ex `Cluster design | No material design gaps; NVIDIA 2-tier InfiniBand ref. architecture | Supermicro primary GB300 delivery partner | — | Low`. Credit read: Low, Low-to-Mod, `Low (above benchmark)`, `Low-to-Mod (uncontracted)`, `Low-to-Mod (gap)`.
  - **T2F.3 — Facility failure-scenario → SLA impact (TDD, inherited)**: `Event | Type | Likelihood | Post-protection impact | Mitigant`. Ex `Chiller-plant / CDU failure | Environmental | Low / Very Low | MRC impact ≤ ~-3% up to ~72h (−$850k/day gross) | 2N row-level cooling, isolation valves`. Likelihood: Low, Very Low, Low / Very Low. Followed by `Read-through:` with chip `[CP-2F calc on CP-2A frozen inputs]`.
  - **T2F.4 — Insurance adequacy read (MMI, draft)**: bullets, bold lead-ins `Programme scope (anticipated):` `Connectivity resilience:` `Binding caveat (material to reliance):` `Status caveat:` `Credit read:`.
  - **T2F.5 — Sustainability-linked / transition-debt assessment**: prose.
  - **T2F.6 — Gaps & conflicts ledger (no silent reconciliation)**: `ID | Type | Detail | Disposition`. Ex `G-2F.1 | Source status | Altman Solon TDD titled "Final Report (30-Apr-2026)" but carried draft per run scope; MMI draft (10-Aug-2026) | Both carried provisional; conflict logged, not reconciled`. The ID column wraps awkwardly ("G-" / "2F.1").
  - H3 `Cross-module handoffs` heading at the bottom (content not captured).
- Not seen: CP-2F QA section.

### CP-2H — Ratings Migration & Trigger Headroom, **Lambda** (shots 55.20–55.52)
- Header not captured (starts at H1). H1 `CP-2H — Ratings Migration & Trigger Headroom — Lambda / Project Poutine (GPV $917.2m Senior Secured Term Loan)`.
- H2 `Module Result`: `Result: PASS — RATING-TRANSITION CASE ESTABLISHED ON A METHODOLOGY-BRIDGE BASIS (COMMITTEE-GRADE, WITH LIMITATIONS). NO RATING ISSUED.` "Lambda / Project Poutine is private and unrated ... (code chip `READY_WITH_LIMITATIONS`)". 7 bullets; `Confidence 70/100 (Medium).`
- H2 `Analysis`; H3 `Rating transition view`; H3 `Rating-trigger summary` table (6 cols): `Agency lens (external / bridged) | Comparable anchor | Nearest trigger (direction) | Metric / threshold | CP-2G case value | Migration read`. Ex `Moody's — Generic PF / Digital-Infra (proposed) | CoreWeave DDTL 4.0 A3 | Downgrade: min DSCR | ~1.05x covenant | Downside FY27 1.048x | Negative pressure at covenant; base within range`. Italic footer "All entries are analyst-constructed bridges ... registers T2R.1–T2R.9; no rating is issued." Register ids here are **T2R.x** and **T3E.x** (CP-3D absorbed).
- H3s `Methodology & metric bridge (conclusion-first)` (a strikethrough glitch on "7.64% all-in ... ±50bps ≈ ∓1.8 DSCR-points" from `~`), `Trigger headroom (analyst-constructed; not agency-published)`, `Migration cases, notching & agency divergence` (state tokens in prose: `within_current_range`, `negative_pressure / trigger_breach`).
- H2 `Credit Handoff & Monitoring` (bullets `To CP-3 / CP-3A / CP-3C (...)`, `To CP-2B (catalyst register)`, `To CP-6 (IC debate)`, `Leading indicators (T2R.9 / T3E.9):`).
- H2 `Conflicts, Limitations & QA Validation` (55.52): "Conflicts / limitations carried (logged, not silently reconciled):" bullets (`NO ISSUER RATING (binding).` `Analyst-constructed triggers.` ... `CP-3D (market-implied) is source-limited (C-3D.1)`), then **`QA validation:`** bullets with bold labels `Route.` `Predecessors.` `Re-anchor integrity.` `Contract/identity.` ("YAML envelope complete; six canonical H2 headings present; filename `Lambda_CP-2H_20260811.md` matches issuer_id/module_id/analysis_date derivation. No DOCX/PDF/HTML/JSON analytical export.") and a last bullet "qa_status: Passed. committee_status: Committee Ready (with limitations). confidence: 70/100 (Medium) — capped by the absence of any actual rating anchor ..."; then "Recommended next commands: Run CP-3 (...) · Run CP-3A (...) · Run CP-4 / CP-4B (...) · Run CP-6 (...). Move this artifact into _RUNS before running the next module." (italic last sentence; commands in bold, separated by middle dots).
- Not seen: Lambda CP-2H Evidence Trace / appendix registers T2R.x.

### CP-3 — Relative Value & Security Selection, **Lambda** (shots 56.13, 56.20)
- H1 `CP-3 — Relative Value & Security Selection — Lambda / Project Poutine ($917.24m GPV Senior Secured Term Loan, as of 2026-08-11)`. Header not captured.
- H2 `Module Result`: **`Result: READY WITH LIMITATIONS — CROSS-ISSUER RELATIVE VALUE ESTABLISHED; RV DIRECTIONAL/PROVISIONAL PENDING EXECUTED MARGIN.`** Bullets (Headline RV conclusion; Where the credit becomes compensatory; Fundamental scorecard (equal-weight, provisional); Structural / recovery view; Single-instrument caveat (explicit); `Confidence 62/100 (Medium).`).
- Judgement words (verbatim): RV label `Fair-to-Rich (under-compensated)`, `Fair-to-Cheap`, `Unclear/Provisional (directional Rich at model)`; credit tier `"Acceptable"` from `Composite ≈ 2.94 / 5.0`; tag `[Provisional — Equal-Weight]`; `Benchmark UNLOCKED`; `NO MATCH`.
- H2 `Analysis`: **H3 headings are "Step N — ... (Tx.y)"**: `Step 1 — File Gate, Source Quality & Execution Mode (T3.1)` ("Module Status: READY WITH LIMITATIONS ... Execution Mode: Single-Name RV"); table `Source (ref) | Quality | As-of | Data supplied | Limitation | Downstream use` (ex `CP-1 / CP-1A (PASS) | High (frozen canonical) | FY26 + SPV model to FY30 | Sculpt, amortisation, instrument terms, call, hedge, collateral, step-in | Model-only SPV econ; indicative margin | Steps 2–3, 5`; last row `REF_CP-3_Sector_RV.xlsx | n/a | — | — | NO MATCH (private, no ISIN/FIGI) | Step 5 (no mark)`); then bullets `Market-data quality.` `Legal-data quality.` `Identity.`; `Step 2 — Fundamental Credit Summary (from CP-1/CP-2 family; summarised, not re-derived)` (56.20 cut mid-paragraph). Other register ids referenced: T3.3, T3.4, T3.7 ("ranking" table), T3.8 (security-selection conclusion), T3E.4. Eleven steps ("ran in full across all eleven steps").
- No Copilot citation markers seen in the Lambda shots.

---
## 2. Cross-module patterns

### 2.1 Status / result vocabularies (verbatim)
- Result line statuses: `PASS` (+ outcome in caps; qualifiers `(COMMITTEE-GRADE)`, `(COMMITTEE-GRADE, WITH LIMITATIONS)`, `(MEDIUM CONFIDENCE)`, `NO RATING ISSUED.`), `PASS — READY_FOR_CP-0.` (CP-PARSE), `READY WITH MATERIAL LIMITATIONS — USABLE_WITH_LIMITATIONS.` (CP-1C), `READY WITH LIMITATIONS — SECURITY SELECTION WITHHELD ...` and `READY WITH LIMITATIONS — CROSS-ISSUER RELATIVE VALUE ESTABLISHED; ...` (CP-3). CP-0 states `Readiness verdict: READY (with scoped limitations)`. No NOT_READY, Restricted-as-status, FAIL or BLOCKED seen as a final result; `BLOCKED`/`CONDITIONAL` appear only as unused readiness classes in CP-0 prose.
- `qa_status`: `Passed`; `Passed with material limitations` (CP-1C); `Passed — Ready with Limitations (RV Restricted; ...)` (CP-3); usually followed by a long parenthetical listing the checks.
- `committee_status`: `Committee Ready`; `Committee Ready (with limitations — ...)`; `USABLE_WITH_LIMITATIONS`; `Requires More Work` (CP-3 WM); `SOURCE_READY — profile/use-case gate (POST_CP0_PROFILE_GATE) pending` (CP-0). `module_status: Ready with Limitations` (CP-3).
- Upstream verdict strings: `READY`, `READY_WITH_LIMITATIONS`, `PASS`, `PASS (Committee Ready, conf 90)`, `USABLE_WITH_LIMITATIONS (conf 73)`, `PASS (with license-restricted rating-cell limitation)`; per-consumer readiness `cp1b_readiness: READY`, `cp1c_readiness: READY_WITH_LIMITATIONS`.
- Placeholder / null tokens: `—` (null), `n/a`, `[Insufficient Information]`, `[Insufficient Information — license-restricted]`, `[•]`, `Not Calculable`, `NO MATCH`, `[inferred]`, `Open / Deferred / Substantially closed` (gap status), `PROMOTED / NOT PROMOTED`, `Available? Yes / Partial`.
- Evidence-quality tags: `Web-Scraped — Unverified`, `Document-Disclosed`, `Public-Company — Web-Scraped Unverified`, `ANALYST-CONSTRUCTED`, `Source fact (docs)`, `Directional`.
- Module-specific judgement scales: Governance `Sponsor/Governance Risk Level: Medium` (CP-1A); `Liquidity Risk Level: STRONG` (CP-2D); `ESG Risk Level` / `Operational Risk Level: LOW-TO-MODERATE` (CP-2F); CP-3 `RV label = Unclear` / `Fair-to-Rich` / `Fair-to-Cheap`, `Credit Tier "Stretched"` / `"Acceptable"` with `/5.0` composite and `/100` composite, recommendation `Preferred / Avoid / Requires More Work / Neutral`; CP-1C position words (Upper-mid, Mid-pack, High end, Negative outlier, Low end); CP-2H ratings (B2, B, B-, outlooks, `trigger_breach`); CP-4 `CovenantReview 5+`; Confidence column `High / Medium / Low`; severity `High / Medium / Low`; Likelihood `Low / Very Low`.

### 2.2 Confidence
Always `Confidence N / 100 (Band)` (spacing varies: `90 / 100` vs `84/100`). Header carries `confidence_score` + `confidence_band`.
Formula quoted verbatim in CP-PARSE, CP-0, CP-1, CP-1A, CP-1B: `clamp((0.6·E + 0.4·C)·S − P, 0, 100)` ("per canon"), with named inputs E, C, S, P (e.g. `E=95, C=93, S=1.0, P=2`; CP-1 `E=94, C=95, S=1.0, P=3`; CP-1B `P=4`), P explained by "one MINOR: ...". Later modules (CP-2 on, Lambda) drop the formula and give deduction lists `(i)...(iv)` and "Capped — not by analytical integrity — by ...".
Values seen and bands: CP-PARSE 92 High; CP-0 90 High; CP-1 90 High; CP-1A 90 High; CP-1B 89 High; CP-1C 73 Medium; CP-2 86 High; CP-2A 84 High; CP-2E 76 Medium; CP-2D 86 High; CP-2G 85 High; CP-2H 82 High; CP-3 57 Low; CP-4 84 High; Lambda CP-2F 80 High; Lambda CP-2H 70 Medium; Lambda CP-3 62 Medium. Observed band thresholds are consistent with Low < ~60, Medium ~60–79, High >= 80 (inferred, no threshold table shown). Row-level confidence in tables uses `High / Medium / Low` words, sometimes with tags (`Medium [inferred]`, `Medium (→CP-4)`).

### 2.3 Registers and id schemes (headings carry the id; no consistent prefix)
CP-PARSE `Triage Register` (table_id `cpparse.triage_register`); CP-0 `T1–T8`; CP-1 `A1–A8` (+A9/A10 referenced); CP-1A `R1–R10` (snake_case ids in titles) and `T2D.1–T2D.7` (governance); CP-1B `B1–B8`, `D1–D5`; CP-1C `T4.D1`, `T4.1`…`T4.10`; CP-2 inherits (no new ids); CP-2A `T2A.1–T2A.5` (+ row ids `CP-2A-DP-001`); CP-2E `T2E.1–T2E.4`; CP-2D unnumbered tables; CP-2G `T2H.1–T2H.9` (note: "T2H" prefix inside CP-2G, same prefix as CP-2H's module) referenced; CP-2H (WM) `E1–E4` evidence rows; CP-3 `T3C.*`, `T3E.*` referenced; CP-3 Lambda `T3.1, T3.3, T3.4, T3.7, T3.8`; CP-2F `T2F.1–T2F.6` (gap ids `G-2F.1`); CP-2H Lambda `T2R.1–T2R.9`, `T3E.1–T3E.10`. No `P1–P8` register ids were seen anywhere. Gap/conflict ids: `G1`, `C1…C7`, `D1`, `G-2F.1`, and Lambda `G-1…G-6`, `C-2`, `C-3D.1`, `LG1–LG3`, `LG-SP`.

### 2.4 Standard recurring tables
- Gaps/conflicts: `ID | Type | Detail | Disposition` (CP-0 T7, CP-1B, CP-2F T2F.6).
- Evidence trace: `Claim / metric | Evidence (source, period) | Risk mechanic | Credit implication | Confidence` (CP-2D); with `#` and `Limitation` added in CP-2H.
- Downstream readiness: `Consumer | Verdict | Minimum missing evidence`, `Module | Status | Handoff`.
- Inherited snapshot: `Item ($m unless noted) | Value (Mar-26 / LTM) | Basis / note`.
- Period-matrix financial tables with 4–6 numeric columns (FY2023..FY2025, Dec-24..Mar-26, LTM Dec-25 / LTM Mar-26).

### 2.5 Citation style
- `turn1searchNN` markers: appear in WM CP-PARSE (`turn1search85`, `84`, `86`, `89`), CP-0 (`turn1search85`, `89`, `29`, `30`, `31`, `33`) and WM CP-3 (`turn1search105`, `70`, `110`, `121`). Rendered as **italic, un-spaced text** glued to the end of a sentence or bracket (`...[CP-1 A4 / CP-1A / CP-2].turn1search105turn1search70`); consecutive markers concatenate with no separator (`turn1search29turn1search30turn1search31`). Not hyperlinks.
- Other modules (CP-1 through CP-2H WM, CP-4, all Lambda) use only internal bracket refs (`[CP-1 A5; lender deck p.8]`, `[CP-2G L77/L79]`, `[both agency PDFs]`) and file names; none shows `turn1search`.

### 2.6 Things a report designer must accommodate
- **Run header panel**: ~25–35 keys, lists, brace-objects, folded scalars; long run-on strings (`qa_status` and `committee_status` parentheticals run 300+ chars). Needs key/value layout, chips for flags (`limitation_flags` UPPER_SNAKE tokens up to ~90 chars), and a lineage list (`upstream_artifacts_used`, `downstream_consumers`).
- **Result line** as a status banner with: status word set (PASS / READY WITH LIMITATIONS / READY WITH MATERIAL LIMITATIONS), outcome phrase, qualifier, optional judgement levels (Liquidity Risk Level, ESG Risk Level, ...), `NO RATING ISSUED` flag; plus confidence score/band and the formula inputs E, C, S, P.
- **Wide tables**: 7–10 columns (CP-1A T2D.2 7, T2D.3 8, T2D.4 10, T2D.6 10; CP-1C T4.1 10; CP-PARSE triage 7; CP-2H rating-trigger 8, Lambda 6; CP-2E ladders 7). In Copilot they overflow with a horizontal scrollbar; the rightmost column was cut off in 37.19, 40.58 and 43.13. Cells wrap to very tall rows with multi-sentence content.
- **Long tables**: 28-row source catalogs (CP-PARSE, CP-0 T2), 17-row EBITDA→cash walk, 13-row module map, 20+ rows in CP-1 statements.
- **Table cell formatting**: bold fragments (`**$1,292.0m**`), italics (`less`, `plus`), row-level bold for subtotals/base rows, right-aligned numerics with parentheses for negatives and `+`/`−` signs, `x` multiples (`4.02x`), `%`, em-dash nulls, `~` approximations, inline code chips inside cells and even in header cells, glyphs `→ ▲ ▼ ✓ ≈ ≥ ≤ Σ ± ∓ ≡`, the true minus sign `−`. Literal `**` leaking in cells (CP-2G trajectory, CP-1C T4.D1) shows the source markdown can contain bold-in-cell that must be parsed correctly.
- **Section-label rows inside tables** (Sources / Uses in CP-2D) and a table with an empty first header cell.
- **Nested/structured prose**: numbered lists 1.–3., inline `(i)(ii)(iii)` enumerations, bold lead-in bullets (the dominant pattern), "Evidence → Risk Mechanic → Credit Implication" triplets, "Mechanic:/Implication:" run-ins, "Read:", "Net:", "Takeaway before detail:" italic sentences, italic table notes ("Notes: Blank cells ... rendered '—' (null), never zero").
- **Code-styled identifiers**: run ids (`WoodMackenzie_CP-1_20260825`), filenames (`primary-export.xlsx`, `Lambda_CP-2H_20260811.md`), enum tokens (`READY`, `READY_WITH_LIMITATIONS`, `SINGLE_WINDOW`), calc tags `[CP-2D calc]`, commands `Run CP-2A [issuer: ...; perimeter: ...]`, `table_id: cpparse.triage_register`, snake_case register names (R1 `source_classification`) and snake_case column headers (T2D.1).
- **Formulas**: only the confidence formula `clamp((0.6·E + 0.4·C)·S − P, 0, 100)`; arithmetic inline (`$281.0m ÷ $48.2m`, `−2.65%`); leverage multiples and DSCR as `1.048x`.
- **Headings**: H3/H2 titles are long, include parentheticals and "(conclusion-first)" suffixes, ids (`T2A.1 — ...`), arrows, em dashes, `&`, and an italic word inside an H3 (CP-4 "what the lender *does* have"). Heading levels are inconsistent: table captions are sometimes H2-size (CP-2, CP-3, CP-2D), sometimes H3, sometimes a bold paragraph (CP-1C, CP-2G trajectory).
- **Markdown artefacts to avoid reproducing or to handle**: stray tildes causing strikethrough (CP-2A 47.14, CP-1C 43.05, Lambda CP-2H 55.40); `---` lines inside the header turning into H2 (CP-0); literal `>-` markers; run-together citations.
- Horizontal rules separate header from body and appear before `Analysis` and the closing sections.
- Currency/units: US$ millions 1 dp, `$1,292.0m`, `~$94.5m`, BPS (`+200bps`), turns `4.02x`, dates as `29-Oct-2025`, `FY2026e`, `LTM Mar-26`, `Q1'26`.

---
## 3. Screenshot map (filename time `08.MM.SS` -> module, section)

| Time | Module | Content |
|---|---|---|
| 35.23 | CP-0 | Run header (+ anchor / invocation-echo sub-blocks) |
| 35.37 | CP-0 | H1, Audit Summary, start of Analysis (turn1search markers) |
| 35.50 | CP-0 | Analysis continuation; Appendix heading; T1 |
| 36.00 | CP-0 | T2 representation catalog |
| 36.12 | CP-0 | T3, T4, T5 |
| 36.21 | CP-0 | T6 module map |
| 36.31 | CP-0 | T7 gaps log, T8 readiness verdicts (ends here) |
| 37.02 | CP-PARSE | Module Result (short wide crop) |
| 37.19 | CP-PARSE | Triage Register (last column cut off) |
| 37.33 | CP-1 | Run header, Audit Summary |
| 37.46 | CP-1 | Analysis, key metrics table |
| 37.58 | CP-1 | Appendix A1 |
| 38.10 | CP-1 | A2 (A3 caption at edge) |
| 38.23 | CP-1 | A4, A5 |
| 38.39 | CP-1 | A6, A7, A8 |
| 38.54 | CP-1A | Run header |
| 39.06 | CP-1A | H1, Module Result, start of Analysis |
| 39.16 | CP-1A | Business and transaction snapshot table |
| 39.36 | CP-1A | Appendix heading, R1, R2 |
| 39.47 | CP-1A | R3, R4, R5 |
| 39.58 | CP-1A | R6, R7 |
| 40.10 | CP-1A | R8, R9 |
| 40.41 | CP-1A | R9/R10 (overlaps 40.10; cut after first R10 row) |
| 40.58 | CP-1A | Governance & Sponsor View, T2D.1 (cut right), T2D.2 |
| 41.09 | CP-1A | T2D.3, T2D.4 |
| 41.20 | CP-1A | T2D.5, T2D.6, T2D.7 |
| 41.32 | CP-1B | Run header, H1, Module Result |
| 41.47 | CP-1B | Analysis, Appendix heading, B1 |
| 41.59 | CP-1B | B2, B3 |
| 42.11 | CP-1B | B4, B5, B6 |
| 42.20 | CP-1B | B7, B8 |
| 42.33 | CP-1B | Conflicts & gaps register, Downstream readiness |
| 42.52 | CP-1C | Run header, Audit Summary, Analysis start |
| 43.05 | CP-1C | Borrower-vs-peer snapshot, decision drivers |
| 43.13 | CP-1C | Appendix: reading note, T4.D1, T4.1 (last col cut) |
| 43.28 | CP-2 | Run header, H1, Module Result start |
| 43.42 | CP-2 | Module Result bullets |
| 43.57 | CP-2 | Analysis, capital-structure snapshot table |
| 45.42 | CP-2 | Business snapshot, Deleveraging trajectory table |
| 45.52 | CP-2 | Relative positioning, Evidence bullets, Strongest contrary view |
| 46.01 | CP-2 | Downstream Handoffs, QA & Governance |
| 46.47 | CP-2A | Run header, H1 |
| 47.05 | CP-2A | Module Result |
| 47.14 | CP-2A | Analysis (strikethrough glitch) |
| 47.25 | CP-2A | T2A.1, T2A.2 |
| 47.36 | CP-2A | T2A.3, T2A.4 |
| 47.46 | CP-2A | T2A.5, Handoffs, QA & Governance (cut) |
| 48.08 | CP-2E | Run header |
| 48.19 | CP-2E | H1, Module Result |
| 48.28 | CP-2E | Analysis, T2E.1 |
| 48.42 | CP-2E | T2E.2, T2E.3 |
| 48.55 | CP-2E | T2E.4, Evidence bullets, Handoffs |
| 49.08 | CP-2E | QA & Governance |
| 49.19 | CP-2D | Run header, H1 |
| 49.28 | CP-2D | Module Result (Liquidity Risk Level: STRONG) |
| 49.40 | CP-2D | Liquidity view, EBITDA → cash bridge |
| 49.49 | CP-2D | Sources & uses, Revolver access |
| 50.00 | CP-2D | Cash runway & stress, Evidence trace |
| 50.15 | CP-2G | Run header |
| 50.27 | CP-2G | H1, Module Result |
| 50.38 | CP-2G | Analysis, trajectory table (literal `**`) |
| 50.51 | CP-2G | Base/Upside/Downside/Refinancing H3s, Evidence Trace start (cut) |
| 51.05 | CP-2H (WM) | Run header |
| 51.18 | CP-2H (WM) | H1, Module Result |
| 51.26 | CP-2H (WM) | Analysis, Rating-trigger summary table |
| 51.46 | CP-2H (WM) | Methodology bridge, Trigger headroom |
| 51.55 | CP-2H (WM) | Agency divergence H3, Evidence Trace E1–E4 |
| 52.22 | CP-3 (WM) | Run header |
| 52.29 | CP-3 (WM) | Module Result, Analysis > Recommendation (turn1search markers) |
| 52.37 | CP-3 (WM) | Recommendation, snapshot table, evidence bullets |
| 52.47 | CP-3 (WM) | RV & Security Selection, Downside/Recovery, Handoffs (cut) |
| 53.04 | CP-4 | H1, Audit Summary |
| 53.14 | CP-4 | Analysis, financial-covenant read table |
| 53.22 | CP-4 | Debt-incurrence architecture table |
| 53.30 | CP-4 | Leakage architecture table, guardrails, contrary view |
| 54.15 | CP-2F (Lambda) | Run header |
| 54.22 | CP-2F (Lambda) | H1, Module Result |
| 54.30 | CP-2F (Lambda) | Module Result bullets, verdict |
| 54.41 | CP-2F (Lambda) | Analysis, T2F.1 |
| 54.49 | CP-2F (Lambda) | T2F.2, T2F.3 |
| 54.57 | CP-2F (Lambda) | T2F.4, T2F.5, T2F.6, Cross-module handoffs heading |
| 55.20 | CP-2H (Lambda) | H1, Module Result |
| 55.29 | CP-2H (Lambda) | Analysis, Rating-trigger summary |
| 55.40 | CP-2H (Lambda) | Methodology bridge, Trigger headroom, Migration cases |
| 55.52 | CP-2H (Lambda) | Credit Handoff & Monitoring; Conflicts, Limitations & QA Validation |
| 56.13 | CP-3 (Lambda) | H1, Module Result |
| 56.20 | CP-3 (Lambda) | Analysis, Step 1 table, Step 2 start (cut) |

Total: 87 screenshots (CP-0 7; CP-PARSE 2; CP-1 6; CP-1A 11; CP-1B 6; CP-1C 3; CP-2 6; CP-2A 6; CP-2E 6; CP-2D 5; CP-2G 4; CP-2H Wood Mackenzie 5; CP-3 Wood Mackenzie 4; CP-4 4; CP-2F Lambda 6; CP-2H Lambda 4; CP-3 Lambda 2).

## 4. Gaps and caveats
- Never captured: headers for CP-PARSE, CP-4, Lambda CP-2H and CP-3; CP-4's Evidence Trace/QA; CP-1A, CP-2D, CP-2G, CP-3 (both) QA & Governance; CP-0's QA/Evidence Trace; appendix registers for CP-2G (T2H.1–9), CP-3 (T3C.*, T3.2–T3.8 beyond Step 1), CP-2H Lambda (T2R.x), CP-1C T4.2–T4.10, CP-1 A3/A9/A10. No CP-1D, CP-2B, CP-2C (absorbed), CP-3A, CP-3C, CP-4A/4B, CP-5, CP-6 screenshots exist.
- Screenshot-to-section allocation follows reading order; the 45.42 vs 45.52 boundary within CP-2 is approximate.
- All cell values above are transcribed as legible at screenshot resolution; where cells were truncated by the viewport (right edge) I have said so.
- Tables are quoted with `|` separators by me; the originals have no vertical rules.
