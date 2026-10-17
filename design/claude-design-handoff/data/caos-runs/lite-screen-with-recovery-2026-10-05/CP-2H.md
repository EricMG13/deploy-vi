---
module_id: "CP-2H"
module_name: "RatingTransitionCase"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_FULL_CREDIT_SCREEN"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2H-79dfc512ded59d0f"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_FULL_CREDIT_SCREEN-06-CP-2H"
credit_os_invocation_sha256: "6962ae939811b84cee6a15a965212c7b7bdac4c38f701fe69b84731756ae674f"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "dcb45fd922bd40cf339a42308e91a3fac8f6e23b9f198f147d86c85f73a15eeb"
  - module_id: "CP-L10"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "1b3412810ea6d286e8dd1b78eaea47c62bfa80734d5ca52486c3d5933abc0d12"
confidence_score: 55
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "LITE_FULL_UPGRADE_REQUIRED", "CURRENT_AGENCY_CRITERIA_AND_ACTIONS_NOT_SUPPLIED", "CP1_HISTORY_AND_CP2G_CASES_NOT_DELIVERED", "INSTRUMENT_RECOVERY_EVIDENCE_LIMITED"]
validation_warnings: ["SOURCE_LIMITED", "LITE_FULL_UPGRADE_REQUIRED", "AGENCY_RATING_OBSERVATIONS_ARE_SECONDARY_AND_DATE-DIVERGENT", "NO_AGENCY_SPECIFIC_TRIGGER_HEADROOM_CALCULABLE"]
downstream_consumers: ["CP-2B", "CP-3", "CP-3C", "CP-3D", "CP-6"]
---

## Audit Summary

- **Canonical handoff:** `CZR_CP-2H_20261002.md`.
- **Run status:** Complete with gaps; full analytical rating-migration assertions are restricted by the LITE screening boundary and absent agency criteria, issuer-specific triggers, CP-1 history, and CP-2G forecast cases.
- **Confidence:** 55 — Low. Screening evidence identifies issue-level rating displays and reported-period credit indicators, but does not establish current agency actions, agency metric definitions, or trigger headroom.
- **QA status:** Restricted. This is not a formal or shadow rating and does not predict an agency action.
- **Decision scope:** SCREENING_ONLY. Recommend a new, user-confirmed, linked FULL_CREDIT_32 run to supply the missing full-method inputs; this run remains LITE_CREDIT_22.

## Analysis

### Rating transition view

FINRA’s October 2, 2026 snapshots display issue-level ratings, not verified agency actions: for the 2032 secured notes, Moody’s is shown at B1 with a September 28, 2026 last-rated date and S&P at BB- last rated February 2, 2024; for the unsecured 2032 notes, the displays are Caa1 and B-, with S&P last rated October 2, 2024. [C1, C2, C3, C4, C5, C6, C7, C8] The non-synchronous observations show divergence but do not establish current agency disagreement. Q2 2026 indicators are mixed: consolidated and Las Vegas Adjusted EBITDA weakened, while Regional EBITDA increased; reported covenant compliance is supportive but is not agency headroom. [C9, C10, C11, C14] No applicable current agency criteria, issuer-specific rating trigger, CP-1 history, or CP-2G forecast case is delivered. Accordingly, migration class and timing remain insufficiently evidenced; the nearest monitor is subsequent agency action and the next reported operating update, not an inferred rating threshold.

The quantitative agency trigger nearest to breach cannot be identified or ranked from the delivered materials. The filing does disclose contractual CEI revolver/Term Loan A covenants of maximum net total leverage 6.50:1 and minimum fixed-charge coverage 2.0:1, and reports compliance at June 30, 2026; these are contractual tests, not agency rating triggers, and no tested ratio values are supplied. [C12, C13, C14] Consequently, covenant headroom is not calculated and must not be represented as rating headroom.

**Downside transmission and timing.** The reported Q2 Las Vegas weakness was associated with lower leisure visitation, non-gaming revenue, hotel occupancy and hotel rates. If those operating pressures persist, the first break would be weaker property earnings; lower issuer earnings would then reduce cash available against debt service, lease payments and capital needs, potentially increasing refinancing pressure. The delivered evidence has no forecast case or agency threshold with which to quantify that chain. Regional EBITDA growth, reported operating cash flow of $675 million for the first half, cash of $965 million, revolver availability of $1.9 billion, and reported covenant compliance are the strongest contrary evidence; those supports would outweigh the downside only if sustained operating cash generation and accessible liquidity continue to cover fixed cash demands while Las Vegas stabilizes. [C10, C11, C14, C17, C18, C19, C22]

**Agency divergence and instrument context.** FINRA’s displayed secured and unsecured ratings differ between agencies, and S&P’s displayed last-rated dates are materially older than Moody’s dates. This may reflect timing, differing methodologies or issue-specific assessment; the evidence cannot distinguish among them, so ratings are not averaged. The Q2 filing describes the 6.500% secured notes as ranking equally with first-priority lien obligations and the 6.000% unsecured notes as ranking equally with senior unsecured debt. That supports only a directional structural distinction; it does not establish agency notching, recovery ratings, collateral value or recovery. [C1, C2, C3, C4, C5, C6, C7, C8, C15, C16]

**Subsequent event:** the filing identifies an Alberta mobile sports betting and iGaming launch on July 13, 2026, after the June 30 reporting date. It is kept separate from Q2 figures and is not treated as a rating catalyst with a predicted agency response. [C23]

### Analytical appendix — complete canonical registers

#### T2R.1 — Rating evidence register

| agency | issuer/instrument | rating | outlook/watch | effective date | source | locator | status |
|---|---|---|---|---|---|---|---|
| Moody’s | Caesars Entertainment, Inc. — 6.500% senior secured notes due 2032 | B1 | No outlook/watch displayed in the delivered FINRA snapshot; no agency action supplied. | 2026-09-28, FINRA-displayed last-rated date | FINRA fixed-income lookup; CUSIP 12769GAC4 [C1, C3] | p. 1, rating and last-rated-date fields | Secondary issue-level observation; agency action and issuer-level rating not independently verified. |
| S&P | Caesars Entertainment, Inc. — 6.500% senior secured notes due 2032 | BB- | No outlook/watch displayed in the delivered FINRA snapshot; no agency action supplied. | 2024-02-02, FINRA-displayed last-rated date | FINRA fixed-income lookup; CUSIP 12769GAC4 [C2, C4] | p. 1, rating and last-rated-date fields | Secondary, stale issue-level observation; current agency action not verified. |
| Moody’s | Caesars Entertainment, Inc. — 6.000% senior notes due 2032 | Caa1 | No outlook/watch displayed in the delivered FINRA snapshot; no agency action supplied. | 2026-09-28, FINRA-displayed last-rated date | FINRA fixed-income lookup; CUSIP 12769GAD2 [C5, C7] | p. 1, rating and last-rated-date fields | Secondary issue-level observation; agency action and issuer-level rating not independently verified. |
| S&P | Caesars Entertainment, Inc. — 6.000% senior notes due 2032 | B- | No outlook/watch displayed in the delivered FINRA snapshot; no agency action supplied. | 2024-10-02, FINRA-displayed last-rated date | FINRA fixed-income lookup; CUSIP 12769GAD2 [C6, C8] | p. 1, rating and last-rated-date fields | Secondary, stale issue-level observation; current agency action not verified. |

#### T2R.2 — Applicable methodology map

| agency | criteria | publication/effective date | applicable entity/instrument | limitation |
|---|---|---|---|---|
| Moody’s | [Insufficient Information] — current corporate and gaming/hospitality criteria were not delivered; applicability and supersession cannot be checked. | [Insufficient Information] — no criteria publication or effective date is available in the delivered materials. | Caesars Entertainment, Inc. and the two 2032 debt issues; entity- and instrument-specific application is unverified. | No agency research or current criteria document; no methodology-based rating conclusion. |
| S&P | [Insufficient Information] — current corporate and gaming/hospitality criteria were not delivered; applicability and supersession cannot be checked. | [Insufficient Information] — no criteria publication or effective date is available in the delivered materials. | Caesars Entertainment, Inc. and the two 2032 debt issues; entity- and instrument-specific application is unverified. | No agency research or current criteria document; no methodology-based rating conclusion. |

#### T2R.3 — Agency metric bridge

| agency metric | CP metric | adjustments | period/perimeter | formula | evidence_id |
|---|---|---|---|---|---|
| [Insufficient Information] — agency leverage/coverage definitions are not supplied. | Issuer-reported Adjusted EBITDA: $1,807 million for six months ended June 30, 2026; this is not established as an agency numerator. | No agency adjustments can be reproduced; issuer states its Adjusted EBITDA is not necessarily comparable across companies and is not a liquidity measure. | Reported six-month period; consolidated Caesars; interim 2026 vs 2025. | No agency formula supplied; agency ratio and headroom not calculable from the evidence delivered. | E-01, Q2 Form 10-Q p. 16 [C9] |
| [Insufficient Information] — agency debt and cash definitions are not supplied. | Q2 filing debt-note carrying/book-value presentation; no agency-defined debt value selected. | The filing contains separate balance-sheet, debt-note, and agency-unavailable definitions; no reconciliation to an agency metric is established here. | June 30, 2026; issuer consolidated perimeter; no CP-1 history delivered. | No agency numerator/denominator or adjustments supplied; no ratio calculated. | E-02, Q2 Form 10-Q pp. 2, 9; annual report is referenced but absent [C20, C24] |

#### T2R.4 — Quantitative trigger matrix

| agency | rating type | trigger direction | metric | threshold | case/period value | headroom | status |
|---|---|---|---|---|---|---|---|
| Moody’s | Issue-level rating displayed for secured 2032 notes; current agency rating type/action unverified. | [Insufficient Information] — no issuer-specific upgrade or downgrade direction/trigger was delivered. | [Insufficient Information] — applicable agency metric not disclosed. | [Insufficient Information] — no agency threshold supplied; contractual covenant thresholds are not agency triggers. | reported Q2 2026; no CP-2G forecast case or agency-tested value delivered. | [Insufficient Information] — trigger threshold and agency-defined tested value are missing; no headroom asserted. | insufficient_information — no agency trigger test possible. |
| S&P | Issue-level rating displayed for secured 2032 notes; displayed last-rated date is 2024-02-02. | [Insufficient Information] — no current issuer-specific upgrade or downgrade direction/trigger was delivered. | [Insufficient Information] — applicable agency metric not disclosed. | [Insufficient Information] — no agency threshold supplied; contractual covenant thresholds are not agency triggers. | reported Q2 2026; no CP-2G forecast case or agency-tested value delivered. | [Insufficient Information] — trigger threshold and agency-defined tested value are missing; no headroom asserted. | insufficient_information — stale secondary observation; no agency trigger test possible. |
| Moody’s | Issue-level rating displayed for unsecured 2032 notes; current agency rating type/action unverified. | [Insufficient Information] — no issuer-specific upgrade or downgrade direction/trigger was delivered. | [Insufficient Information] — applicable agency metric not disclosed. | [Insufficient Information] — no agency threshold supplied; contractual covenant thresholds are not agency triggers. | reported Q2 2026; no CP-2G forecast case or agency-tested value delivered. | [Insufficient Information] — trigger threshold and agency-defined tested value are missing; no headroom asserted. | insufficient_information — no agency trigger test possible. |
| S&P | Issue-level rating displayed for unsecured 2032 notes; displayed last-rated date is 2024-10-02. | [Insufficient Information] — no current issuer-specific upgrade or downgrade direction/trigger was delivered. | [Insufficient Information] — applicable agency metric not disclosed. | [Insufficient Information] — no agency threshold supplied; contractual covenant thresholds are not agency triggers. | reported Q2 2026; no CP-2G forecast case or agency-tested value delivered. | [Insufficient Information] — trigger threshold and agency-defined tested value are missing; no headroom asserted. | insufficient_information — stale secondary observation; no agency trigger test possible. |

#### T2R.5 — Qualitative modifier matrix

| agency | factor | current evidence | supportive/neutral/negative/unknown | rationale | locator |
|---|---|---|---|---|---|
| Moody’s / S&P; screening assessment only | Earnings and business performance | Q2 consolidated Adjusted EBITDA was $920 million versus $955 million; Las Vegas was $410 million versus $469 million; Regional was $488 million versus $439 million. | negative | Las Vegas earnings pressure can reduce consolidated debt-service capacity if sustained; Regional growth partly offsets, but does not establish a full-period or forecast trend. | Q2 Form 10-Q pp. 15–16 [C9, C10, C11, C22] |
| Moody’s / S&P; screening assessment only | Liquidity and debt service | Cash was $965 million; reported CEI revolver borrowing capacity was $1.9 billion; first-half operating cash flow was $675 million. | supportive | Reported liquidity and cash generation support near-term payment capacity, but a full forward liquidity bridge and agency treatment are unavailable. | Q2 Form 10-Q pp. 4, 10, 22 [C17, C18, C19] |
| Moody’s / S&P; screening assessment only | Covenant compliance | Issuer reported compliance with applicable financial covenants as of June 30, 2026. | supportive | Compliance is evidence of reported contractual status at that date, not a disclosed covenant cushion or rating trigger headroom. | Q2 Form 10-Q p. 10 [C14] |
| Moody’s / S&P; screening assessment only | Merger execution and financial-policy uncertainty | Q2 filing describes merger closing conditions and possible non-completion. | unknown | A delay or non-completion could affect operations, costs and financing uncertainty, but current transaction status and agency treatment are not supplied. | Q2 Form 10-Q p. 25 [C21] |

#### T2R.6 — Migration case matrix

| agency | case | transition class | earliest timing | catalyst | confidence | evidence/forecast IDs |
|---|---|---|---|---|---|---|
| Moody’s | reported Q2 2026; screening observation, not a forecast case | insufficient_information | Not assessable — agency review calendar and current rating action unavailable. | Subsequent Moody’s action or next reported operating update; no date or agency trigger supplied. | Low; secondary issue display and no CP-2G case. | E-01, E-03; no forecast ID [C1, C3, C9, C26] |
| S&P | reported Q2 2026; screening observation, not a forecast case | insufficient_information | Not assessable — displayed issue ratings are stale and agency review calendar unavailable. | A new, dated S&P action or next reported operating update; no date or agency trigger supplied. | Low; stale secondary issue display and no CP-2G case. | E-02, E-04; no forecast ID [C2, C4, C6, C8, C9, C26] |

#### T2R.7 — Agency divergence register

| issue | agency A/B positions | methodology/perimeter/timing explanation | unresolved conflict |
|---|---|---|---|
| 6.500% senior secured notes due 2032 | Moody’s B1, last-rated date displayed 2026-09-28; S&P BB-, last-rated date displayed 2024-02-02. | Different displayed rating levels and observation dates; current criteria, entity scope, adjustments and agency actions are unavailable, so timing or methodology cannot be isolated. | Divergence is visible in secondary snapshots; whether it persists on current, comparable agency assessments is unresolved. |
| 6.000% senior notes due 2032 | Moody’s Caa1, last-rated date displayed 2026-09-28; S&P B-, last-rated date displayed 2024-10-02. | S&P observation is older; criteria, entity scope, issue-specific rationale and any intervening agency action are unavailable. | Current agency positions and the reason for the difference cannot be verified; do not average or select a preferred rating. |

The displayed positions and dates in both divergence rows are FINRA observations, not direct agency reports. [C1, C2, C3, C4, C5, C6, C7, C8]

#### T2R.8 — Instrument and recovery-rating implications

| instrument | issuer rating link | notching/recovery evidence | possible direction | limitation |
|---|---|---|---|---|
| 6.500% senior secured notes due 2032 | No separately verified issuer rating or explicit issuer-to-instrument rating link delivered; FINRA shows an issue-level rating only. | Q2 filing says the notes rank equally with first-priority lien obligations. No agency recovery rating, current collateral value, perfection review or recovery analysis delivered. [C15] | Secured structure could directionally support recovery relative to unsecured debt, but no notching or recovery uplift is established. | Current collateral perimeter, lien perfection, intercreditor position and agency recovery analysis are unavailable. |
| 6.000% senior notes due 2032 | No separately verified issuer rating or explicit issuer-to-instrument rating link delivered; FINRA shows an issue-level rating only. | Q2 filing says the notes rank equally with senior unsecured indebtedness. No agency recovery rating or recovery analysis delivered. [C16] | Structurally unsecured position may be weaker than first-priority secured debt in recovery; magnitude and agency notching are unknown. | No recovery inputs, current structural analysis or direct agency rationale delivered. |

#### T2R.9 — Monitoring and handoff

| nearest trigger | buffer | leading indicator | review date/event | downstream module |
|---|---|---|---|---|
| No agency-specific quantitative trigger identified. Monitor sustained Las Vegas and consolidated earnings weakness and obtain current agency actions; contractual covenants are not rating triggers. | [Insufficient Information] — agency threshold, current tested ratio and forecast case are absent; no buffer can be measured. | Las Vegas and consolidated Adjusted EBITDA; Regional offset; reported covenant compliance; subsequent agency rating action. | Next quarterly filing or dated agency action, whichever is available first; exact review date not supplied. | CP-2B; CP-3; CP-3C; CP-3D; CP-6 |

Reported figures and the contractual-versus-agency distinction supporting this monitoring entry are cited in Evidence Trace. [C9, C10, C11, C12, C13, C14, C22]

#### T2R.10 — Gaps and conflicts

| missing/stale item | affected agency/trigger | impact | required follow-up |
|---|---|---|---|
| Direct, current Moody’s and S&P issuer/instrument actions, outlooks and watch status | Both agencies; all rating posture and migration assessments | FINRA observations are issue-level secondary displays; S&P last-rated dates are older, and no direct agency action or outlook/watch evidence is available. | Obtain dated agency reports/actions for the issuer and each instrument; verify rating type, effective date, outlook/watch and recovery rating. |
| Applicable current Moody’s and S&P corporate and gaming/hospitality criteria | Both agencies; qualitative modifiers, metric definitions and instrument notching | Applicability, methodology version, definitions and any superseding criteria cannot be established. | Obtain current published criteria and agency-specific rationale applicable to Caesars and each instrument. |
| Agency-defined issuer-specific triggers and tested values | Both agencies; quantitative trigger matrix | No threshold, duration test, numerator, denominator or tested agency value; headroom and nearest trigger are not calculable. | Obtain agency report lines stating complete triggers and definitions, plus corresponding tested data and required observation periods. |
| CP-1 history and CP-2G forecast cases | Both agencies; bridge and migration cases | LITE route supplies only reported-period screening inputs; no forecast case or full historical metric bridge may be constructed. | Recommend a new, user-confirmed, linked FULL_CREDIT_32 run with CP-1 history and CP-2G cases; retain this run as LITE. |
| Full 2025 annual report and current complete financing/lease documents | Both agencies; financial definitions, leverage and liquidity context | The Q2 filing references the 2025 Annual Report; missing history and current documents limit definition reconciliation and creditor analysis. | Supply the referenced 2025 Form 10-K and current executed credit/lease-document package, then reconcile agency and issuer definitions. |
| Current instrument recovery evidence and agency recovery ratings | Both agencies; secured/unsecured notching and LGD implications | Documented ranking alone does not establish current collateral coverage, recovery prospects or agency notching. | Obtain current security, collateral, intercreditor and agency recovery evidence; assess each instrument separately. |

### Downstream handoff

CP-2B should receive the dated observed rating displays and the next-action monitoring signal; CP-3/CP-3D should receive the issue-level rating and notching limitations; CP-3C should receive the unresolved transition/refinancing uncertainty; CP-6 should retain the agency divergence and the counterargument from Regional growth, cash generation, available revolver capacity and reported covenant compliance. None of these observations constitutes a security recommendation or formal agency conclusion.

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| FINRA-displayed secured-note ratings and last-rated dates | [C1, C2, C3, C4] | FINRA fixed-income lookup, CUSIP 12769GAC4 | 1 |
| FINRA-displayed unsecured-note ratings and last-rated dates | [C5, C6, C7, C8] | FINRA fixed-income lookup, CUSIP 12769GAD2 | 1 |
| Consolidated, Las Vegas and Regional Adjusted EBITDA comparisons | [C9, C10, C11, C22] | Caesars Form 10-Q | 15–16, 20 |
| Contractual leverage and fixed-charge covenant thresholds | [C12, C13] | Caesars Form 10-Q | 10 |
| Reported covenant compliance | [C14] | Caesars Form 10-Q | 10 |
| Secured and unsecured 2032 note ranking disclosures | [C15, C16] | Caesars Form 10-Q | 10 |
| Cash, revolver capacity and operating cash flow | [C17, C18, C19] | Caesars Form 10-Q | 4, 10, 22 |
| Referenced 2025 Annual Report | [C20] | Caesars Form 10-Q | 5 |
| Merger conditions | [C21] | Caesars Form 10-Q | 25 |
| Subsequent Alberta launch, after the Q2 reporting date | [C23] | Caesars Form 10-Q | 17 |
| Reported Q2 2026 period | [C26] | Caesars Form 10-Q | 1 |
| Debt-note carrying/book-value presentation | [C24] | Caesars Form 10-Q | 9 |
| Supplied executed secured-note indenture identity | [C25] | 6.500% Senior Secured Notes due 2032 indenture | 1 |

## Source Registry

| Source ID | Source | Use and limitation |
|---|---|---|
| 27f7042a-85aa-4a76-ac06-374bc7db0dbd | FINRA fixed-income lookup, 6.500% senior secured notes due 2032, CUSIP 12769GAC4 | Timestamped October 2, 2026 observation; ratings are displayed as issue-level data and are not direct agency reports. Price/yield are last-trade fields; no quote-side or spread evidence is used. [C1, C2, C3, C4] |
| b7df3500-3ccb-4b3a-8315-db4023c2a17f | FINRA fixed-income lookup, 6.000% senior notes due 2032, CUSIP 12769GAD2 | Timestamped October 2, 2026 observation; ratings are displayed as issue-level data and are not direct agency reports. Price/yield are last-trade fields; no quote-side or spread evidence is used. [C5, C6, C7, C8] |
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Caesars Entertainment, Inc. Form 10-Q for quarter ended June 30, 2026 | Filed interim operating, debt, liquidity, covenant, transaction and instrument disclosures; not a rating-agency report. [C9, C12, C14, C15, C16, C17, C18, C19, C20, C21, C23, C24, C26] |
| 9e7b8728-8ea5-4cd9-b90b-9e0b1311bdc4 | 6.500% Senior Secured Notes due 2032 indenture, dated February 6, 2024 | Executed base indenture; does not establish current collateral perfection, recovery value or a current agency rating. Its definitions are not treated as agency definitions. [C25] |

## Gaps & Conflicts

- **Current ratings and outlooks:** direct dated agency actions, issuer-level ratings, outlooks/watch and recovery ratings were not delivered. FINRA’s secondary displays are retained as observations only; the S&P observations are older than Moody’s on both issues. [C1, C2, C3, C4, C5, C6, C7, C8]
- **Methodology and triggers:** no current applicable agency criteria, issuer-specific rating trigger text, trigger duration requirement or agency-tested ratio is available. No agency trigger headroom or formal transition conclusion is made.
- **LITE route limitations:** CP-1 history and CP-2G forecast cases are not delivered. CP-2H maps only reported Q2 2026 screening information and does not construct forecast cases or assert a full rating migration. [C26]
- **Metric bridge:** reported issuer Adjusted EBITDA and contractual covenant tests cannot be assumed to equal agency metrics. The contractual thresholds are not substituted for rating triggers; tested values and headroom are unavailable. [C9, C12, C13, C14]
- **Agency divergence:** displayed ratings differ and are not synchronized. Missing criteria and rationale prevent attribution to methodology, perimeter or timing; ratings are not averaged.
- **Debt and legal context:** the filing references the 2025 Annual Report, and current complete credit/lease documents are absent; these limit historical and contractual reconciliation. [C20, C24]
- **Subsequent event:** July 13, 2026 Alberta launch is post-period and remains separate from Q2 reported figures. [C23]

## QA Validation

| Check | Result | Record |
|---|---|---|
| Issuer and instrument ratings separated | PASS WITH LIMITATIONS | Ratings are recorded as instrument-level FINRA displays; no issuer rating is inferred. |
| Agency attribution, dates and locators | PASS WITH LIMITATIONS | Agency labels and FINRA-displayed last-rated dates are retained with secondary-source status; direct agency actions remain unavailable. |
| Criteria applicability and recency | RESTRICTED | Current agency criteria and agency reports were not delivered; no applicability or supersession assertion is made. |
| Metric bridge and adjustments | RESTRICTED | Issuer-reported metrics are not equated with agency metrics; no unsupported adjustment or ratio is calculated. |
| Trigger direction, period and sustainability | PASS WITH LIMITATIONS | No agency trigger is invented; latest reported period is identified and no forecast case or sustained-breach claim is constructed. |
| Transition classes and formal actions | PASS WITH LIMITATIONS | Insufficient-information classes are screening analyses, not agency actions, notches or predictions. |
| Agency divergence | PASS WITH LIMITATIONS | Agency differences and observation-date mismatch remain visible and are not averaged. |
| Fabrication and quotation control | PASS | No agency trigger, probability, rating action, recovery estimate or unsupported quotation is invented. |
| Subsequent-event boundary | PASS | July 13, 2026 event is explicitly date-labelled and not blended into Q2 figures. |
| Required registers and columns | SELF-CHECK COMPLETE | T2R.1–T2R.10 are present with the declared columns and at least one body row each. |
| Confidence and QA status | RESTRICTED | Confidence score 55 / Low; QA Restricted for source and LITE-route limitations. |
| Host validation | NOT RUN HERE | Host vendor validation and register-completeness checks follow this answer; no host result or exit status is claimed. |