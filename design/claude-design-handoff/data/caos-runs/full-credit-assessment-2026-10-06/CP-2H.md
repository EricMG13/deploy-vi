---
module_id: "CP-2H"
module_name: "RatingTransitionCase"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2H-217e72deb7df90a6"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-13-CP-2H"
credit_os_invocation_sha256: "8f11628bb78ea3a2c411e7deacb0f8c4b96831745be9757a9a2a71c6640689fe"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
  - module_id: "CP-1D"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "14f82d3ec8922f3c8a7e25f5400cedd84f4d2af4e4cc9184c73b2a85b4392cf2"
  - module_id: "CP-2G"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "773d9eb85e48aa35b31b772d6960e68e70dbdfc2a7028d2afc08b410fb2cd5dc"
confidence_score: 53
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - "SOURCE_LIMITED_NOT_COMMITTEE_READY"
  - "CURRENT_AGENCY_CRITERIA_AND_ISSUER_LEVEL_RATINGS_NOT_SUPPLIED"
  - "NO_AGENCY_SPECIFIC_TRIGGERS_OR_NUMERIC_FORECAST_CASES"
  - "NO_POST_Q2_2026_FINANCIALS"
validation_warnings:
  - "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED"
  - "FINRA_RATINGS_ARE_ISSUE_LEVEL_AND_S_AND_P_OBSERVATIONS_ARE_STALE"
  - "AGENCY_METRIC_BRIDGE_AND_TRIGGER_HEADROOM_UNAVAILABLE"
downstream_consumers: [CP-2B, CP-3, CP-3C, CP-3D, CP-6]
---

## Audit Summary

**Canonical filename:** `CZR_CP-2H_20261002.md`. **Status:** Restricted; confidence **53/100, Low**; committee status **Requires More Work**. The accepted upstream handoffs match issuer, run and period, but are themselves source-limited. The supplied FINRA pages display ratings for two 144A bond issues, not a verified issuer-level rating action; no outlook/watch, agency report, applicable criteria or agency-specific upgrade/downgrade threshold is supplied. The October 2 observation records Moody’s rating dates of September 28, 2026, while the displayed S&P dates are from 2024. CP-2G supplies a historical LTM anchor, not numerical forecast cases. Thus, qualitative pressure can be mapped, but rating headroom, a formal transition forecast and instrument recovery notching cannot be established. Host validation follows this response; no host result is claimed.

## Analysis

### Rating transition view

At the observed date, FINRA displayed Moody’s B1 and S&P BB- for the 6.50% secured 2032 issue, and Moody’s Caa1 and S&P B- for the 6.00% unsecured 2032 issue. [C1, C2, C3, C4, C6, C7, C8, C9] These are issue-level observations, not issuer ratings or verified agency action notices; outlook/watch fields are absent. The nearest quantitative rating trigger is therefore **not identifiable**: no agency threshold or matching agency metric is in the delivered evidence. The 6.50:1 credit-facility covenant is contractual, not an agency rating trigger. [C25] CP-2G has a historical LTM base but no numeric forecast cases. Operating deterioration in Las Vegas supports a downside pressure pathway, but its agency timing and rating consequence remain uncertain. [C15, C16, C17]

The two agency displays show differing symbols for both issues. They are not averaged or translated into a notch comparison because the underlying agency reports, rating rationales and applicable methodologies are unavailable. S&P’s displayed last-rated dates are stale relative to the October 2026 FINRA observation. FINRA identifies these prices as last trades, not executable bid/ask observations; pricing is not used here as a rating trigger.

**Credit transmission and challenge.** Lower Las Vegas visitation and hold can reduce operating contribution; if that weakness persists while interest, rent and capex remain substantial, cash generation and refinancing flexibility could weaken. The Q2 filing reports H1 revenue growth and covenant compliance, which are meaningful contrary evidence. [C15, C16, C17, C19] That counterargument would gain weight if subsequent reporting showed sustained EBITDA and cash generation, lower debt, and updated agency outlooks or affirmed ratings. Conversely, further operating deterioration, weaker cash conversion, or an adverse agency action would increase concern. The evidence does not establish that any rating action is imminent.

**Metric and trigger boundary.** CP-2G’s Q2 2026 LTM carrying-debt / issuer Adjusted EBITDA measure is an analyst calculation using balance-sheet carrying debt and issuer-defined Adjusted EBITDA; it is not an agency-defined leverage ratio. [C18, C19, C20, C22, C23] Because agency adjustments for leases, debt perimeter, EBITDA normalization and testing period are unavailable, this ratio cannot provide agency headroom. CP-1D also leaves quality-adjusted EBITDA unresolved. No numeric headroom or probability is inferred.

### Analytical appendix — complete canonical registers

#### T2R.1 — Rating evidence register

| agency | issuer/instrument | rating | outlook/watch | effective date | source | locator | status |
|---|---|---|---|---|---|---|---|
| Moody’s | 6.50% senior secured notes due 2032; CUSIP 12769GAC4 | B1 | Not displayed | 2026-09-28, FINRA last-rated date shown | FINRA Fixed Income Security Lookup [C1, C2, C3] | Observed 2026-10-02; page 1 | Secondary rating observation; agency action/report not supplied. |
| S&P | 6.50% senior secured notes due 2032; CUSIP 12769GAC4 | BB- | Not displayed | 2024-02-02, FINRA last-rated date shown | FINRA Fixed Income Security Lookup [C1, C4, C5] | Observed 2026-10-02; page 1 | Displayed rating is stale relative to analysis date; current agency action not verified. |
| Moody’s | 6.00% senior notes due 2032; CUSIP 12769GAD2 | Caa1 | Not displayed | 2026-09-28, FINRA last-rated date shown | FINRA Fixed Income Security Lookup [C6, C7, C8] | Observed 2026-10-02; page 1 | Secondary rating observation; agency action/report not supplied. |
| S&P | 6.00% senior notes due 2032; CUSIP 12769GAD2 | B- | Not displayed | 2024-10-02, FINRA last-rated date shown | FINRA Fixed Income Security Lookup [C6, C9, C10] | Observed 2026-10-02; page 1 | Displayed rating is stale relative to analysis date; current agency action not verified. |
| Moody’s / S&P | Caesars Entertainment, Inc. issuer-level rating | Not established from supplied evidence | Not established | — | No issuer-level rating action or report supplied | No issuer-level locator in delivered material | Do not impute the observed bond ratings to the issuer. |

#### T2R.2 — Applicable methodology map

The delivered evidence contains no current Moody’s or S&P criteria publication, methodology excerpt or agency rating rationale applicable to Caesars or these instruments. The FINRA pages establish displayed bond-rating fields, not the criteria behind them. The issuer’s filed covenant disclosure is not a rating methodology. [C2, C4, C7, C9, C25]

| agency | criteria | publication/effective date | applicable entity/instrument | limitation |
|---|---|---|---|---|
| Moody’s | Applicable corporate, gaming/hospitality and issue-rating criteria not supplied | Not supplied | Caesars issuer and the two displayed 2032 bond issues | Cannot confirm criteria version, rating-factor weights, lease adjustments, liquidity treatment or recovery/notching framework. |
| S&P | Applicable corporate, gaming/hospitality and issue-rating criteria not supplied | Not supplied | Caesars issuer and the two displayed 2032 bond issues | Cannot confirm criteria version, rating-factor weights, lease adjustments, liquidity treatment or recovery/notching framework. |

#### T2R.3 — Agency metric bridge

| agency metric | CP metric | adjustments | period/perimeter | formula | evidence_id |
|---|---|---|---|---|---|
| Agency-adjusted leverage; definition unavailable | CP-2G historical carrying debt / issuer Adjusted EBITDA: 3.26x | CP-2G uses balance-sheet carrying debt; financing obligations are separate; agency lease, pension, restricted-cash and EBITDA adjustments are unknown. | Q2 2026 LTM ending June 30; consolidated issuer; not an October balance sheet | CP-2G calculation: $11,699m carrying debt / $3,592m LTM issuer Adjusted EBITDA. Not comparable to an undisclosed agency definition. | FY2025 and Q2 Adjusted EBITDA [C22, C23]; current debt and cash components [C18, C19, C20] |
| Agency-adjusted net leverage; definition unavailable | CP-2G historical net debt / issuer Adjusted EBITDA: 2.99x | Cash offset uses cash and equivalents; restricted cash excluded. Agency treatment and permitted offsets are unknown. | Q2 2026 LTM ending June 30; consolidated issuer; not an October balance sheet | ($11,699m carrying debt − $965m cash) / $3,592m LTM issuer Adjusted EBITDA. Not agency headroom. | Debt, cash and EBITDA components [C18, C19, C20, C22, C23] |
| Agency cash-flow or fixed-charge metric; definition unavailable | H1 2026 CFO $675m; CP-2G historical LTM Adjusted EBITDA $3,592m | No agency cash-flow metric or lease-adjusted coverage definition supplied; CFO is not a substitute for agency FFO or fixed-charge measures. | H1 2026 reported flow and Q2 2026 LTM historical denominator; consolidated | No agency formula can be reproduced from delivered materials. | H1 CFO [C21]; annual and interim Adjusted EBITDA [C22, C23] |

#### T2R.4 — Quantitative trigger matrix

The only located leverage threshold is a credit-agreement covenant. It is not treated as an agency rating trigger, and its calculation definitions and current headroom are not established by this rating evidence. [C25] No agency-specific trigger line was supplied.

| agency | rating type | trigger direction | metric | threshold | case/period value | headroom | status |
|---|---|---|---|---|---|---|---|
| Moody’s | Issue rating; agency trigger not provided | Not available | Agency-defined leverage, coverage or cash-flow metric | No issuer-specific agency threshold in delivered evidence | CP-2G Q2 2026 LTM carrying-debt / issuer Adjusted EBITDA 3.26x; not an agency-defined value | Cannot quantify without agency threshold, formula and testing period | Not assessable from supplied agency evidence. |
| S&P | Issue rating; agency trigger not provided | Not available | Agency-defined leverage, coverage or cash-flow metric | No issuer-specific agency threshold in delivered evidence | CP-2G Q2 2026 LTM carrying-debt / issuer Adjusted EBITDA 3.26x; not an agency-defined value | Cannot quantify without agency threshold, formula and testing period | Not assessable from supplied agency evidence. |

#### T2R.5 — Qualitative modifier matrix

| agency | factor | current evidence | supportive/neutral/negative/unknown | rationale | locator |
|---|---|---|---|---|---|
| Moody’s / S&P | Las Vegas operating performance | Q2 filing attributes declines to lower city-wide leisure visitation, lower hotel occupancy and compressed room rates. | negative | Persistent weakness could reduce operating cash available for interest, rent and investment; no agency factor weights are known. | Q2 2026 Form 10-Q, p. 20 [C16] |
| Moody’s / S&P | Las Vegas gaming hold | Table-games hold was 16.6% in Q2 2026 and 17.5% H1 2026, down year over year. | negative | Lower hold can weaken casino revenue and EBITDA; hold volatility means a single period is not proof of a sustained trend. | Q2 2026 Form 10-Q, p. 20 [C17] |
| Moody’s / S&P | Consolidated revenue trend | H1 2026 revenue increased 2.8% year over year. | supportive | Growth is a counterweight, but does not by itself establish stronger cash conversion or lower debt. | Q2 2026 Form 10-Q, p. 19 [C15] |
| Moody’s / S&P | Liquidity and covenant condition | The company reported compliance with applicable financial covenants as of June 30, 2026; reported liquidity is dated to that period. | supportive | Supports near-term resilience at the reported date; covenant headroom and post-June availability remain unknown. | Q2 2026 Form 10-Q, pp. 10, 22 [C19] |
| Moody’s / S&P | Debt and fixed claims | FY2025 disclosure reported $11.9bn indebtedness and approximately $1.4bn of 2026 VICI/GLPI rent. | negative | Fixed debt service and rent absorb cash that could otherwise fund debt reduction or refinancing needs. | FY2025 Form 10-K, p. 13 [C24] |
| Moody’s / S&P | Rating action, outlook and criteria | FINRA displays issue ratings but no outlook/watch; no agency reports or rationale supplied. | unknown | Cannot identify agency view of drivers, tolerance, upgrade path or downgrade conditions. | FINRA observations, p. 1 [C2, C4, C7, C9] |

#### T2R.6 — Migration case matrix

Transition classes below are investor-side assessments, not agency actions or notch predictions. CP-2G supplies no numerical forecast case; the reported LTM base is historical. The downside classification reflects evidenced operating pressure only, with low confidence and no agency trigger linkage. [C15, C16, C17, C21, C22, C23]

| agency | case | transition class | earliest timing | catalyst | confidence | evidence/forecast IDs |
|---|---|---|---|---|---|---|
| Moody’s | Base; historical Q2 2026 LTM anchor only | insufficient_information | At a future agency review; date not disclosed | No numerical CP-2G forecast, agency outlook or rating rationale available. | Low | FINRA issue observation; CP-2G historical bridge [C2, C7, C22, C23] |
| S&P | Base; historical Q2 2026 LTM anchor only | insufficient_information | At a future agency review; date not disclosed | Displayed S&P rating dates are from 2024; no later action or criteria supplied. | Low | FINRA issue observation; CP-2G historical bridge [C4, C9, C22, C23] |
| Moody’s | Downside; qualitative only | negative_pressure | Could be considered at a future review after subsequent operating reporting; no date supportable | Further Las Vegas revenue/hold deterioration and weaker cash generation while fixed claims persist. | Low | CP-2G downside limitations; Q2 operating evidence [C16, C17, C21] |
| S&P | Downside; qualitative only | negative_pressure | Could be considered at a future review after subsequent operating reporting; no date supportable | Further Las Vegas revenue/hold deterioration and weaker cash generation while fixed claims persist. | Low | CP-2G downside limitations; displayed rating date is stale [C9, C16, C17, C21] |
| Moody’s | Upside; no numeric assumptions supplied | insufficient_information | No timing established | Sustained post-capex cash generation and debt reduction would be supportive, but no forward case is supplied. | Low | CP-2G does not provide a numeric upside forecast; H1 revenue growth is counterevidence [C15] |
| S&P | Upside; no numeric assumptions supplied | insufficient_information | No timing established | Sustained post-capex cash generation and debt reduction would be supportive, but no forward case is supplied. | Low | CP-2G does not provide a numeric upside forecast; H1 revenue growth is counterevidence [C15] |

#### T2R.7 — Agency divergence register

| issue | agency A/B positions | methodology/perimeter/timing explanation | unresolved conflict |
|---|---|---|---|
| 6.50% secured notes due 2032 | Moody’s displays B1; S&P displays BB-. | FINRA shows a Moody’s last-rated date in September 2026 and an S&P last-rated date in February 2024. No agency rationale, criteria, rating action notice or adjustment bridge is delivered. [C2, C3, C4, C5] | The reason for the symbol difference and whether the displayed S&P rating remains current cannot be resolved. Do not average or translate symbols into notches. |
| 6.00% unsecured notes due 2032 | Moody’s displays Caa1; S&P displays B-. | FINRA shows a Moody’s last-rated date in September 2026 and an S&P last-rated date in October 2024. No agency rationale, criteria or adjustment bridge is delivered. [C7, C8, C9, C10] | The reason for the symbol difference and whether the displayed S&P rating remains current cannot be resolved. Do not average or translate symbols into notches. |
| Issuer rating versus bond ratings | No issuer-level rating evidence supplied; FINRA observations are for two individual instruments. | Rated entity, security terms and recovery assumptions may differ; applicable agency methodology is unavailable. | No issuer-level rating or outlook can be inferred from the bond observations. |

#### T2R.8 — Instrument and recovery-rating implications

| instrument | issuer rating link | notching/recovery evidence | possible direction | limitation |
|---|---|---|---|---|
| 6.50% senior secured notes due February 15, 2032; CUSIP 12769GAC4 | FINRA displays issue ratings; issuer-level rating link not established. | FY2025 filing says the notes rank equally with first-priority lien obligations; no recovery rating, collateral valuation, priority waterfall or agency notching rationale supplied. [C11, C12] | Security could support relative recovery versus unsecured claims, but no direction or number of notches is established. | Full collateral/intercreditor package and agency recovery analysis absent; FINRA classification alone does not establish recovery. |
| 6.00% senior notes due October 15, 2032; CUSIP 12769GAD2 | FINRA displays issue ratings; issuer-level rating link not established. | FY2025 filing says the notes rank equally with senior unsecured indebtedness; no recovery rating or agency notching rationale supplied. [C13, C14] | Unsecured ranking could imply different recovery exposure from the secured issue; no recovery estimate or notch is established. | Asset coverage, structural priority and agency recovery assumptions unavailable. |

#### T2R.9 — Monitoring and handoff

No numerical agency trigger or buffer is identified in the supplied evidence. The next review event is therefore an agency action or new company reporting, not a calendar forecast. Q2 operating conditions and the dated debt/liquidity disclosures support monitoring the following items. [C16, C17, C19, C20, C22, C23]

| nearest trigger | buffer | leading indicator | review date/event | downstream module |
|---|---|---|---|---|
| No agency-specific quantitative trigger supplied | Not measurable; agency threshold and definition absent | Moody’s/S&P rating action, outlook/watch and published rationale | Next agency publication; date not disclosed | CP-2B; CP-6 |
| Qualitative downside: further Las Vegas operating deterioration | No agency tolerance or numerical breakpoint supplied | Las Vegas revenue, table-games hold, EBITDA and company cash generation | Next quarterly filing and any agency review | CP-3C; CP-6 |
| Debt-service and liquidity capacity | Agency headroom unavailable; June covenant compliance is not headroom | Cash, revolver draws/availability, carrying debt, debt service, lease payments and updated covenant reporting | Next financial filing or financing event | CP-3C; CP-3D |
| Secured/unsecured issue differentiation | Recovery and rating notches unavailable | Updated collateral, guarantees, intercreditor terms and issue-specific agency ratings | New agency recovery/issue report or debt-document change | CP-3; CP-3D |

#### T2R.10 — Gaps and conflicts

| missing/stale item | affected agency/trigger | impact | required follow-up |
|---|---|---|---|
| Current issuer-level ratings, outlooks/watch and agency rationale | Moody’s and S&P; overall rating posture | Bond observations cannot establish issuer rating, rating trend or agency rationale. | Obtain current agency rating actions/reports for Caesars and the two issues, including outlook/watch and publication dates. |
| Current S&P rating actions | S&P; both 2032 issues | FINRA displays last-rated dates in 2024; current status cannot be verified. | Confirm subsequent S&P actions and current issue/issuer ratings. |
| Applicable agency criteria | Moody’s and S&P; all triggers and notching | Criteria version, definitions, adjustments and rating tolerances are unknown. | Obtain current corporate, gaming/hospitality and issue-rating criteria and apply the exact versions. |
| Issuer-specific quantitative upgrade/downgrade triggers | Moody’s and S&P; leverage, coverage, cash flow and liquidity | No threshold, formula, duration test or headroom can be calculated. | Obtain explicit issuer-specific trigger language and the agency-defined metric bridge. |
| Agency treatment of lease financing obligations and EBITDA adjustments | Moody’s and S&P; leverage and fixed-charge triggers | CP-2G historical leverage is not comparable to an undisclosed agency calculation. | Obtain agency adjustment schedules; reconcile leases, debt, cash, pension and non-recurring items. |
| CP-2G numerical forecast cases | Moody’s and S&P; base/upside/downside migration timing | Only historical LTM measures and qualitative cases are available; transition timing is unquantified. | Update CP-2G with supported forward cases after forecast inputs and post-June financials are supplied. |
| Recovery ratings and full collateral/intercreditor package | Both bond issues; instrument notching | Relative recovery direction cannot be quantified from first-lien/senior-unsecured labels alone. | Obtain current collateral, guarantor, intercreditor and agency recovery evidence. |
| Post-June financial reporting | Both agencies; current liquidity and operating triggers | October 2 current conditions are not verified by financial data ending June 30, 2026. | Obtain the next filing and current cash/debt/covenant schedule. |

## Evidence Trace

| claim | marker | document | page |
|---|---|---|---:|
| Secured-note CUSIP and Moody’s/S&P issue ratings and displayed dates | [C1, C2, C3, C4, C5] | FINRA Fixed Income Security Lookup, CUSIP 12769GAC4 | 1 |
| Unsecured-note CUSIP and Moody’s/S&P issue ratings and displayed dates | [C6, C7, C8, C9, C10] | FINRA Fixed Income Security Lookup, CUSIP 12769GAD2 | 1 |
| Secured 6.50% notes due 2032 issuance and first-priority ranking | [C11, C12] | Caesars FY2025 Form 10-K | 25 |
| Unsecured 6.00% notes due 2032 issuance and senior-unsecured ranking | [C13, C14] | Caesars FY2025 Form 10-K | 25 |
| H1 2026 revenue growth | [C15] | Caesars Q2 2026 Form 10-Q | 19 |
| Las Vegas performance and visitation pressure | [C16] | Caesars Q2 2026 Form 10-Q | 20 |
| Las Vegas table-games hold | [C17] | Caesars Q2 2026 Form 10-Q | 20 |
| Carrying debt, cash and Adjusted EBITDA inputs used in historical bridge | [C18, C19, C20, C22, C23] | Caesars Q2 2026 Form 10-Q; FY2025 Form 10-K | 2, 16, 23 |
| H1 operating cash flow | [C21] | Caesars Q2 2026 Form 10-Q | 4 |
| Covenant compliance reported at June 30, 2026 | [C19] | Caesars Q2 2026 Form 10-Q | 10 |
| Contractual 6.50:1 leverage covenant, not an agency rating trigger | [C25] | Caesars FY2025 Form 10-K | 24 |
| FY2025 indebtedness and VICI/GLPI rent context | [C24] | Caesars FY2025 Form 10-K | 13 |

## Source Registry

| source | use | period / observation | limitation |
|---|---|---|---|
| FINRA Fixed Income Security Lookup, CUSIP 12769GAC4 | Displayed ratings and instrument identifiers for the 6.50% 144A secured 2032 issue. [C1, C2, C3, C4, C5] | Observed 2026-10-02; last trade 2026-10-01 | FINRA is the rating observation source here, not the agency action report; outlook/watch, rationale and rating methodology absent. |
| FINRA Fixed Income Security Lookup, CUSIP 12769GAD2 | Displayed ratings and instrument identifiers for the 6.00% 144A unsecured 2032 issue. [C6, C7, C8, C9, C10] | Observed 2026-10-02; last trade 2026-10-01 | No agency report or outlook/watch; S&P displayed rating date is 2024-10-02. |
| Caesars FY2025 Form 10-K | Instrument terms, secured/unsecured ranking, financial and contractual context. [C11, C12, C13, C14, C24, C25] | FY ended 2025-12-31; filed 2026-02-17 | Historical financial period; does not contain current agency methodology or an agency-specific trigger. |
| Caesars Q2 2026 Form 10-Q | H1 operating trends, current balance-sheet inputs and covenant compliance. [C15, C16, C17, C18, C19, C20, C21, C23] | Quarter ended 2026-06-30; filed 2026-07-28 | Unaudited; no later financial period or current agency report supplied. |
| Accepted CP-1 and CP-2G handoffs | Historical definitions, LTM bridge and absence of numerical forecast cases. | Q2 2026 | Restricted upstream artifacts; used within their stated scope, with primary-source components cited above. |

## Gaps & Conflicts

The principal conflict is the difference between displayed Moody’s and S&P symbols for each issue, combined with materially different displayed rating dates. Without agency action notices and criteria, the cause cannot be assigned to methodology, rating timing, issuer/instrument perimeter or recovery assumptions. No symbol equivalence or preferred agency is selected. [C2, C3, C4, C5, C7, C8, C9, C10]

The available FINRA ratings are for named bond issues, not a verified issuer-level rating; outlook/watch and recovery ratings are not displayed. The S&P dates are stale relative to the analysis date. The applicable agency criteria, current agency trigger language and rating-adjusted financial calculations are missing. CP-2G offers no numeric forward base/upside/downside cases, so migration timing remains bounded to future reporting or agency review. Q2 operating weakness is a qualitative downside input, counterbalanced by H1 revenue growth and reported covenant compliance; neither establishes a likely rating action. [C15, C16, C17, C19]

## QA Validation

| check | result | note |
|---|---|---|
| Issuer and instrument ratings distinguished | PASS | FINRA observations are labelled issue-level; no issuer rating is imputed. |
| Rating attribution, dates and outlook/watch | RESTRICTED | Displayed ratings and dates are captured; agency reports and outlook/watch are absent, and S&P dates are stale. |
| Criteria applicability | RESTRICTED | Current agency criteria and rating rationales are not in the delivered evidence. |
| Metric bridge | RESTRICTED | CP-2G historical metric is shown with formula and perimeter; agency adjustments and definitions are unavailable. |
| Trigger direction, period and sustainability | RESTRICTED | No agency-specific trigger or sustained-period language is supplied; covenant threshold is not misclassified as an agency trigger. |
| Migration classes and forecasts | RESTRICTED | Classes are investor-side only; no unsupported numeric forecast, probability or agency action is asserted. |
| Agency disagreement | PASS WITH LIMITATIONS | Raw issue-rating displays and differing dates are preserved; no averaging or unsupported notch equivalence. |
| Instrument notching and recovery | RESTRICTED | First-priority secured and senior-unsecured terms are distinguished; recovery rating and full collateral analysis are absent. |
| Required registers and columns | SELF-CHECKED | T2R.1–T2R.10 are present with required columns and at least one row each. |
| Confidence calculation | RESTRICTED | E=75, C=75, S=0.70, P=0; score = (0.6×75 + 0.4×75)×0.70 = 52.5, rounded to 53; Low. Material source gaps require Restricted status. |
| Final status | RESTRICTED | QA status Restricted; committee status Requires More Work. |
| Host automated validation | PENDING | Host validation follows this response; no script result, exit status or host finding is claimed. |