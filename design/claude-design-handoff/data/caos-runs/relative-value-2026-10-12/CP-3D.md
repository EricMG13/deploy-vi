---
module_id: "CP-3D"
module_name: "MarketImpliedRisk"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-3D-af753ed1e611fec2"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-06-CP-3D"
credit_os_invocation_sha256: "35d1d447fbbe744d467edccee8ba5499adc6990df981f957b9dfa0075f956419"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
confidence_score: 37
confidence_band: Insufficient Information
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [LAST_TRADE_ONLY, NO_EXECUTABLE_QUOTES, NO_BENCHMARK_OR_SPREAD, NO_DURATION_OR_SETTLEMENT_CONVENTION, NO_TRADE_SIZE_OR_HISTORY, PEER_TENOR_AND_SENIORITY_MISMATCH, NO_IMPLIED_DEFAULT_CALCULATION, MERGER_STATUS_UNVERIFIED_AFTER_FILING, FUNDAMENTAL_PREDECESSORS_NOT_DELIVERED]
validation_warnings: [SOURCE_GATE_PARTIAL, MARKET_CALCULATIONS_RESTRICTED, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-3]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-3D_20261002.md`. Owned object: `market_implied_risk_map`; schema family: analytical canonical Markdown; runtime output: this handoff. **Run status: Complete with Gaps.** The accepted, matching CP-0 handoff supplies source-readiness context, not an executable price or a fundamental conclusion. Only CP-0 is in the delivered upstream lineage; CP-2, CP-2H and CP-2R findings are not delivered. Their absence limits comparison rather than becoming an invented disagreement.

**Confidence: 37/100, Insufficient Information band; QA Restricted; committee Requires More Work.** Self-assessment: ten material claims comprise seven directly sourced, one calculated, one analyst inference and one unsupported calculation need, giving E=83. Source-gate and required-field coverage is assessed at 45/75=60%; partial source gate S=0.7; one material calculation-coverage penalty P=15. Rounded score = (0.6×83 + 0.4×60)×0.7 − 15 = 37. This score concerns completeness of market-implied analysis, not whether the four displayed last trades exist. Host validation and completeness checks follow this answer; no result from either is claimed.

## Analysis

### Market-implied view

FINRA shows October 1 last trades, observed October 2: Caesars’ secured 6.50% February 2032 note at $93.28 and 8.063520% yield, and its unsecured 6.00% October 2032 note at $84.94 and 9.318398%. [C1, C5, C6, C7, C8, C12, C13, C14, C15, C16] The unsecured yield is 125.4878 basis points higher, but maturity, coupon and call dates differ; this is a cross-sectional observation, not a credit-spread or recovery residual. [C3, C4, C10, C11] FINRA supplies neither executable quotes nor benchmark spreads, trade sizes or chart history. [C19, C20, C21, C54] Caesars’ weaker first-half adjusted EBITDA and conditional merger provide plausible credit-risk channels, not proof that a particular event is priced. [C40, C44, C45] Executable liquidity, comparable curves and current transaction evidence must precede a stronger conclusion.

**Three decision drivers.** First, the observed issuer yield gap is +125.4878 bp, calculated as (9.318398% − 8.063520%)×100; the displayed price gap is −$8.34 in FINRA’s price units. Neither difference isolates seniority because maturities, coupons and call dates differ. [C3, C4, C5, C6, C10, C11, C12, C13] Second, MGM and PENN last-trade yields of 6.722997% and 6.644415% are dated the same day, but their 2029 maturities and near-term displayed call dates defeat a matched 2032 comparison. [C25, C26, C28, C29, C33, C34, C36, C37] Third, Q2 filing context is mixed: six-month adjusted EBITDA fell $32 million year over year to $1,807 million, while six-month operating cash inflow was $675 million and property/equipment purchases were $335 million. The cash figures are period flows, not an October refinancing forecast. [C40, C41, C42]

**Pricing interpretation and strongest challenge.** The issuer’s unsecured note trades at a lower displayed price and higher displayed yield than its first-priority secured note. The filing establishes those different claim positions; weaker residual recovery prospects could transmit stress into unsecured refinancing capacity. This is an **analyst interpretation**, not a decomposed or executable spread finding. [C5, C6, C12, C13, C17, C18] The strongest contrary case is that different coupons, maturity dates, call paths or unobserved trade-size and liquidity effects explain much or all of the gap. It wins if contemporaneous executable, convention-aligned prices and cash-flow analysis eliminate the residual. Until then CP-3 should treat the gap as a question for investigation, not an instrument preference. [C3, C4, C10, C11, C19, C20]

**Downside and time.** If weaker Las Vegas earnings persist or merger financing and approval conditions change, the first break could be reduced operating cash generation or changed transaction funding needs; debt service and lease commitments would then compete with investment, increasing refinancing sensitivity ahead of the disclosed 2028–2030 maturity concentrations. The observable triggers are subsequent operating releases, filed transaction/financing terms and new executable prices—not a fabricated default probability. The filing reports lower Las Vegas quarterly adjusted EBITDA, $686 million of first-half cash interest related to GLPI/VICI leases, and scheduled principal maturities of $767 million in 2028, $1,574 million in 2029 and $3,962 million in 2030. It also reported $1.9 billion of available CEI revolver capacity at June 30, a meaningful contrary liquidity buffer whose availability in a later stress has not been retested here. [C43, C44, C49, C50, C51, C52, C53] These figures have different cash-flow and balance-sheet roles; lease cash interest must not simply be subtracted again from reported operating cash flow.

**Period and definition guardrails.** The May 27 merger agreement was signed within Q2, not after it; completion remained conditional in the supplied filing, whose status is not verified through October 2. The July 13 Alberta launch is a flagged subsequent operating event relative to June 30, not Q2 revenue. [C44, C45, C50] For any fundamental comparison, June balance-sheet debt carrying value is $11,699 million ($114 million current plus $11,585 million long-term), versus debt-note face value $11,807 million: a $108 million gross-minus-carrying difference matching the note’s reported unamortized discounts and deferred finance charges. These are not interchangeable market-value inputs. [C43, C46, C47, C48]

**Calculation lock and handoff.** All four FINRA prices and yields remain vendor-reported last-trade fields. No settlement date, clean-versus-dirty basis, accrued interest, yield-to-maturity/worst convention, benchmark curve, duration, recovery assumption or FX denomination verification is delivered. The displayed dollar sign indicates price notation but does not independently certify bond currency or price per $100 face. Callable notes cannot be treated as bullets: Caesars’ displayed next calls are in 2027; both peers show October 11, 2026. No yield, OAS, hazard rate, price shock, curve history, credit/liquidity/optionality decomposition or executable relative-value measure is calculated. [C4, C11, C19, C20, C21, C26, C34] Obtain matched executable quotes, trade sizes, security cash flows, settlement/accrual conventions, a benchmark and a dated merger update. CP-3 owns any eventual security selection; this handoff supplies no recommendation, rank or size.

### Analytical appendix — complete canonical registers

#### T3E.1 — Instrument and market source register
| security_id | issuer | currency | coupon | maturity/call | seniority | source | timestamp | quote_type | freshness |
|---|---|---|---|---|---|---|---|---|---|
| 12769GAC4 | Caesars Entertainment, Inc. | [Insufficient Information] — dollar price shown, note denomination not stated | 6.50% | 2032-02-15 / next call 2027-02-15 | First-priority senior secured | FINRA lookup; 10-Q debt note [C2, C3, C4, C15, C17] | Last trade 2026-10-01; page observed 2026-10-02 09:31:13Z [C1, C7] | last_trade | Prior-calendar-day trade; intraday trade time and intervening activity unknown |
| 12769GAD2 | Caesars Entertainment, Inc. | [Insufficient Information] — dollar price shown, note denomination not stated | 6.00% | 2032-10-15 / next call 2027-10-15 | Senior unsecured | FINRA lookup; 10-Q debt note [C9, C10, C11, C16, C18] | Last trade 2026-10-01; page observed 2026-10-02 09:31:27Z [C8, C14] | last_trade | Prior-calendar-day trade; intraday trade time and intervening activity unknown |
| 552953CK5 | MGM Resorts International | [Insufficient Information] — dollar price shown, note denomination not stated | 6.125% | 2029-09-15 / next call 2026-10-11 | [Insufficient Information] — FINRA summary does not display seniority | FINRA lookup [C23, C24, C25, C26, C38] | Last trade 2026-10-01; page observed 2026-10-02 09:32:08Z [C22, C29] | last_trade | Prior-calendar-day trade; intraday trade time and intervening activity unknown |
| 707569AV1 | PENN Entertainment, Inc. | [Insufficient Information] — dollar price shown, note denomination not stated | 4.125% | 2029-07-01 / next call 2026-10-11 | [Insufficient Information] — FINRA summary does not display seniority | FINRA lookup [C31, C32, C33, C34, C39] | Last trade 2026-10-01; page observed 2026-10-02 09:32:31Z [C30, C37] | last_trade | Prior-calendar-day trade; intraday trade time and intervening activity unknown |

CUSIPs are FINRA identifiers. The association of the two Caesars CUSIPs with secured/unsecured filing line items uses issuer, coupon and maturity matching; the filing excerpt does not itself print those CUSIPs. FINRA public-page access is subject to its Fixed Income Data User Agreement; no redistribution or executable-quote entitlement is established by this handoff.

#### T3E.2 — Market snapshot
| security_id | bid/mid/ask or evaluated price | yield | spread/OAS/DM | duration | benchmark | observation ID |
|---|---|---|---|---|---|---|
| 12769GAC4 | FINRA last_trade $93.28; not bid/mid/ask or evaluated | FINRA last_trade 8.063520% | [Insufficient Information] — no spread displayed | [Insufficient Information] — no duration or cash-flow calculation inputs | [Insufficient Information] — no curve displayed | FINRA 2026-10-02 09:31:13Z, trade dated 2026-10-01 [C1, C5, C6, C7, C19, C54] |
| 12769GAD2 | FINRA last_trade $84.94; not bid/mid/ask or evaluated | FINRA last_trade 9.318398% | [Insufficient Information] — no spread displayed | [Insufficient Information] — no duration or cash-flow calculation inputs | [Insufficient Information] — no curve displayed | FINRA 2026-10-02 09:31:27Z, trade dated 2026-10-01 [C8, C12, C13, C14, C20] |
| 552953CK5 | FINRA last_trade $98.42; not bid/mid/ask or evaluated | FINRA last_trade 6.722997% | [Insufficient Information] — no spread displayed | [Insufficient Information] — no duration or cash-flow calculation inputs | [Insufficient Information] — no curve displayed | FINRA 2026-10-02 09:32:08Z, trade dated 2026-10-01 [C22, C27, C28, C29, C38] |
| 707569AV1 | FINRA last_trade $93.76; not bid/mid/ask or evaluated | FINRA last_trade 6.644415% | [Insufficient Information] — no spread displayed | [Insufficient Information] — no duration or cash-flow calculation inputs | [Insufficient Information] — no curve displayed | FINRA 2026-10-02 09:32:31Z, trade dated 2026-10-01 [C30, C35, C36, C37, C39] |

#### T3E.3 — Issuer curve
| security_id | maturity/call date | spread/yield | seniority | curve residual | explanation status |
|---|---|---|---|---|---|
| 12769GAC4 | 2032-02-15 / 2027-02-15 | FINRA last-trade yield 8.063520% | First-priority senior secured | [Insufficient Information] — one secured point, no matched secured curve or benchmark | No residual estimated; call, tenor and liquidity unresolved [C3, C4, C6, C17, C19] |
| 12769GAD2 | 2032-10-15 / 2027-10-15 | FINRA last-trade yield 9.318398% | Senior unsecured | [Insufficient Information] — one unsecured point, no matched unsecured curve or benchmark | Observed +125.4878 bp versus secured is not a curve residual [C10, C11, C13, C18, C20] |

#### T3E.4 — Peer/index context
| comparator | alignment basis | spread/yield/price | period | difference | comparability limitation |
|---|---|---|---|---|---|
| Caesars unsecured versus Caesars secured | Same issuer and last-trade date; different priority, coupon, maturity and call | 9.318398% / $84.94 versus 8.063520% / $93.28 | Trades dated 2026-10-01 | Unsecured minus secured: +125.4878 bp displayed yield; −$8.34 displayed price | No matched spread, cash-flow or executable-quote comparison [C3, C4, C5, C6, C10, C11, C12, C13, C19, C20] |
| MGM 552953CK5 versus Caesars secured | Same last-trade date; 2029 versus 2032 maturity | 6.722997% / $98.42 versus 8.063520% / $93.28 | Trades dated 2026-10-01 | Caesars minus MGM displayed yield: +134.0523 bp | Peer seniority unverified; imminent MGM call, tenor and pricing conventions unmatched [C6, C25, C26, C27, C28, C38] |
| PENN 707569AV1 versus Caesars secured | Same last-trade date; 2029 versus 2032 maturity | 6.644415% / $93.76 versus 8.063520% / $93.28 | Trades dated 2026-10-01 | Caesars minus PENN displayed yield: +141.9105 bp | Peer seniority unverified; imminent PENN call, tenor and pricing conventions unmatched [C6, C33, C34, C35, C36, C39] |

No index observation or valid same-seniority, duration-aligned peer residual was delivered. Differences are arithmetic on reported yields, not relative-value conclusions.

#### T3E.5 — Implied risk calculations
| security_id | model | horizon | recovery | discount/benchmark | implied default/loss/break-even | formula ID | limitation |
|---|---|---|---|---|---|---|---|
| 12769GAC4 | Unrun illustrative flat-hazard approximation | Analysis date to 2032-02-15 maturity; settlement and call exercise unverified | [Insufficient Information] — no sourced or authorised recovery assumption | [Insufficient Information] — no comparable benchmark spread or discount curve | Not Calculable from Provided Materials — spread, recovery and call-adjusted cash flows missing | F1: annual approximation h≈s/(1−R); cumulative over T years 1−(1−h)^T | Formula is not an estimated default probability; no numerical sensitivity can be computed without s [C3, C4, C19] |
| 12769GAD2 | Unrun illustrative flat-hazard approximation | Analysis date to 2032-10-15 maturity; settlement and call exercise unverified | [Insufficient Information] — no sourced or authorised recovery assumption | [Insufficient Information] — no comparable benchmark spread or discount curve | Not Calculable from Provided Materials — spread, recovery and call-adjusted cash flows missing | F1: annual approximation h≈s/(1−R); cumulative over T years 1−(1−h)^T | Formula is not an estimated default probability; no numerical sensitivity can be computed without s [C10, C11, C20] |

In F1, s would be an aligned annual credit spread, R an explicitly assumed recovery fraction, h a one-period break-even hazard approximation and T a convention-locked horizon. Discounting, default timing and callable-bond option effects remain unspecified; F1 was **not run**. No yield difference is substituted for s. Accordingly no factual probability, break-even loss or recovery ranking is stated.

#### T3E.6 — Liquidity and technicals
| security_id | bid-ask | trade frequency/volume | issue size | ownership/flow/supply evidence | direction | confidence |
|---|---|---|---|---|---|---|
| 12769GAC4 | [Insufficient Information] — no bid or ask | [Insufficient Information] — last-trade date only; no count or size | $1,500m face at 2026-06-30; not an October liquidity measure | [Insufficient Information] — no dated ownership, flows or new supply | Unresolved; cannot label liquid or dislocated | Low [C7, C15, C19] |
| 12769GAD2 | [Insufficient Information] — no bid or ask | [Insufficient Information] — last-trade date only; no count or size | $1,100m face at 2026-06-30; not an October liquidity measure | [Insufficient Information] — no dated ownership, flows or new supply | Unresolved; cannot label liquid or dislocated | Low [C14, C16, C20] |
| 552953CK5 | [Insufficient Information] — no bid or ask | [Insufficient Information] — last-trade date only; no count or size | [Insufficient Information] — peer issue size not delivered | [Insufficient Information] — no dated ownership, flows or new supply | Unresolved | Low [C29, C38] |
| 707569AV1 | [Insufficient Information] — no bid or ask | [Insufficient Information] — last-trade date only; no count or size | [Insufficient Information] — peer issue size not delivered | [Insufficient Information] — no dated ownership, flows or new supply | Unresolved | Low [C37, C39] |

A June face amount is not evidence of quote depth. No dealer positioning, fund/ETF/CLO flows, days without trades, evaluated-versus-executable gap or event-positioning direction is asserted.

#### T3E.7 — Fundamental-versus-market map
| market implication | CP-2/2H/2R evidence | aligned/divergent | possible basis | unresolved question |
|---|---|---|---|---|
| Unsecured last-trade yield exceeds secured by 125.4878 bp | Those module handoffs are not delivered; filing identifies senior unsecured versus first-priority secured claims [C6, C13, C17, C18] | not_comparable | Priority could affect recovery, but tenor, option and liquidity effects are unseparated | Does a matched, executable spread gap survive convention alignment? |
| Both Caesars 2032 prices displayed below $100; this does not itself quantify expected loss | No CP-2/2H/2R handoffs; filing reports first-half adjusted EBITDA $1,807m versus $1,839m [C5, C12, C40] | not_comparable | Operating pressure could affect debt service, but last trades do not establish a model-implied default rate | How do independently reviewed cash forecasts and covenant triggers compare with dated spreads? |
| Merger uncertainty may affect pricing | No delivered module transaction case; filing describes conditional completion [C44, C45] | not_comparable | Financing, approvals and timing could change refinancing needs; no October deal status established | What is the current filed transaction and financing position? |
| Fundamental liquidity counters an unqualified stress reading | No CP-2 liquidity conclusion; filing reported $1.9bn June CEI revolver availability [C51] | not_comparable | A disclosed liquidity buffer may defer a funding break, subject to later availability and cash needs | Has availability or access changed since June? |

#### T3E.8 — Scenario repricing
| scenario | driver | spread/yield/price assumption | calculated move | convexity/call limitation |
|---|---|---|---|---|
| Illustrative secured yield rise | Hypothetical +100 bp change from the reported last-trade yield; not a forecast | 9.063520% illustrative yield, versus observed 8.063520% [C6] | Not Calculable from Provided Materials — duration, settlement, accrued interest and cash-flow/call schedule unavailable | Price convexity and 2027 call exercise could materially alter any linear estimate [C4] |
| Illustrative unsecured yield rise | Hypothetical +100 bp change from the reported last-trade yield; not a forecast | 10.318398% illustrative yield, versus observed 9.318398% [C13] | Not Calculable from Provided Materials — duration, settlement, accrued interest and cash-flow/call schedule unavailable | Price convexity and 2027 call exercise could materially alter any linear estimate [C11] |
| Transaction delay or changed financing | Conditional merger approval and financing exposure | [Insufficient Information] — no sourced October spread, yield or price shock | Not Calculable from Provided Materials — no quantified financing terms or market sensitivity | Both call treatment and refinancing path could change; no closing assumed [C44, C45] |

The two +100 bp inputs are expressly hypothetical analyst assumptions, not observed spreads. Adding 1.000000 percentage point to a reported yield does not calculate a bond-price move.

#### T3E.9 — Monitoring and handoff
| observable | threshold | cadence/event | downstream module | evidence source |
|---|---|---|---|---|
| Matched Caesars executable secured/unsecured quotes, settlement and trade sizes | First contemporaneous bid and ask for both; recompute rather than extrapolate the +125.4878 bp last-trade gap | On new quote or trading event; record exact timestamps | CP-3 | FINRA last-trade baseline and missing quote fields [C5, C6, C12, C13, C19, C20] |
| Comparable benchmark curve, cash flows and call treatment | First fully specified spread and duration for each instrument | On data delivery or a call-date change | CP-3 | Displayed calls; benchmark absent [C4, C11, C19, C20] |
| Merger approval, completion, termination or financing filing | Any material filed change from conditional transaction description | On filing or announced event, with event date | CP-3 | Q2 merger conditions and completion risk [C44, C45] |
| Operating cash, adjusted EBITDA, available revolver and maturity plan | New reported period or change from June baseline; assess like-for-like definitions | Each issuer filing or financing event | CP-3 | First-half and June baselines [C40, C41, C43, C51] |

#### T3E.10 — Gaps and conflicts
| missing/stale/conflicting item | affected calculation/security | impact | required evidence |
|---|---|---|---|
| G01 — last trades, no bid/ask, intraday trade time or size | All four securities | No executable level, dispersion or liquidity inference | Timestamped executable bid/ask and TRACE trade detail [C19, C20, C38, C39, C54] |
| G02 — no benchmark, spread, duration, settlement, accrued interest or price basis | Curve, default model and repricing | Spread/OAS, residual, yield-to-worst and price shocks uncomputed | Dated benchmark; full cash flows, calls, price convention and settlement [C4, C11, C19, C20] |
| G03 — FINRA chart points untranscribed | All proposed price/yield history | No trend, frequency or dislocation history | Licensed timestamped historical trade/quote series [C21] |
| G04 — peer tenor/call mismatch; peer seniority unverified | MGM/PENN comparisons | Yield differences are descriptive, not matched residuals | Peer indenture terms and matched-duration, same-seniority quotes [C25, C26, C33, C34, C38, C39] |
| G05 — no recovery, default timing or discount assumption | Both Caesars implied-risk rows | No factual or modelled default/loss result | Explicit recovery scenarios, benchmark and convention-locked model [C19, C20] |
| G06 — June issuer fundamentals versus October trades; no CP-2/2H/2R handoffs | Fundamental-versus-market diagnosis | Alignment and trigger headroom unverified | Current, validated analytical predecessors and issuer updates [C40, C41, C51] |
| G07 — merger outcome and financing not established as of analysis date | Event pricing and downside | No completed-transaction or pro forma funding conclusion | Dated transaction-status filing and financing documents [C44, C45] |
| CF-1 — debt-note face versus balance-sheet carrying basis | Fundamental leverage cross-check | $11,807m face versus $11,699m carrying; $108m difference, not a market-price change | Preserve June note and balance-sheet labels in any later leverage analysis [C43, C46, C47, C48] |
| G08 — July operating launch is post-period | Q2 fundamental comparison | Cannot be blended into six-month results | Subsequent-period results before quantifying contribution [C50] |

## Evidence Trace

The table identifies source excerpts through this answer’s citation markers; arithmetic rows are labelled calculations rather than source-reported spreads.

| Claim or calculation | Marker | Document | Locator and role |
|---|---|---|---|
| Caesars identifiers, maturities, calls and last trades | [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14] | FINRA Caesars security lookups | Each p.1; vendor observations; 125.4878 bp and −$8.34 are arithmetic on them |
| Claim priority and June issue faces | [C15, C16, C17, C18] | Caesars Q2 2026 Form 10-Q | pp.9–10; filing descriptions, not FINRA seniority fields |
| Missing spreads, market detail and chart points | [C19, C20, C21, C54] | FINRA Caesars security lookups | Each p.1; observed-summary limitations |
| MGM identifiers, terms and last trade | [C22, C23, C24, C25, C26, C27, C28, C29, C38] | FINRA MGM security lookup | p.1; peer observation and limits |
| PENN identifiers, terms and last trade | [C30, C31, C32, C33, C34, C35, C36, C37, C39] | FINRA PENN security lookup | p.1; peer observation and limits |
| Earnings, cash flow, maturities and lease payment | [C40, C41, C42, C43, C49, C52, C53] | Caesars Q2 2026 Form 10-Q | pp.4–5, 9, 16, 20; period-specific fundamentals |
| Merger conditions and post-period launch | [C44, C45, C50] | Caesars Q2 2026 Form 10-Q | pp.5, 17, 25; conditional event and dated subsequent operation |
| Debt definition and available facility | [C46, C47, C48, C51] | Caesars Q2 2026 Form 10-Q | pp.2, 9–10; June carrying basis, adjustments and liquidity |

## Source Registry

| Source ID | Document and publisher | Observed or reporting basis | Permitted use and constraint |
|---|---|---|---|
| 86dcb55f-6abe-4aab-8143-7e29addf278a | FINRA fixed-income lookup, CUSIP 12769GAC4 | Page observed 2026-10-02 09:31:13Z; last trade 2026-10-01 [C1, C7] | Displayed last-trade fields only; no executable quote, benchmark or transcribed chart [C19, C21, C54] |
| 3093e5d3-2687-41f0-b88a-2330b5077c7f | FINRA fixed-income lookup, CUSIP 12769GAD2 | Page observed 2026-10-02 09:31:27Z; last trade 2026-10-01 [C8, C14] | Displayed last-trade fields only; missing spread and trade detail [C20] |
| 4b57b4a0-a633-4bf9-a890-34d48e34f3a7 | FINRA fixed-income lookup, CUSIP 552953CK5 | Page observed 2026-10-02 09:32:08Z; last trade 2026-10-01 [C22, C29] | Peer last trade; seniority, benchmark and trade detail absent [C38] |
| 02ea2477-b79c-4618-80c2-3b4317e6bafa | FINRA fixed-income lookup, CUSIP 707569AV1 | Page observed 2026-10-02 09:32:31Z; last trade 2026-10-01 [C30, C37] | Peer last trade; seniority, benchmark and trade detail absent [C39] |
| 439e1450-b5ae-4830-b4c3-3719da918fe3 | Caesars Entertainment, Inc., Q2 2026 Form 10-Q | June 30 reporting date; subsequent events separately flagged [C44, C50] | Filing controls issuer descriptions and reported fundamentals, not October bond quotes |

The source set is the delivered evidence only. CP-0 is a matching accepted upstream readiness handoff, not an additional market-data vendor. No external retrieval, chart reconstruction or unsupplied peer document was used.

## Gaps & Conflicts

T3E.10 is the complete issue register. Priority is matched executable prices and terms, followed by a benchmark and recovery assumptions; until obtained, the model-dependent default and scenario-price cells remain uncomputed. The comparison crosses issuer claim priority and maturity as well as reporting dates. The June-versus-October period distinction and debt face-versus-carrying distinction must survive downstream reuse. A new quote, transaction filing or fundamental handoff changes the input snapshot and calls for a fresh comparison, not retrospective insertion into this one. [C3, C10, C17, C18, C19, C20, C43, C44, C46, C47]

## QA Validation

| Self-check | Result | Basis and disposition |
|---|---|---|
| Identity and lineage | Restricted | Host-owned fields and CP-0 hash retained; no other predecessor delivered or inferred. |
| Security identity and seniority | Restricted | Four FINRA CUSIPs retained; Caesars claim priority cross-checked to the filing by coupon/maturity, not by a filing CUSIP; peer seniority unresolved. |
| Timestamp, quote and freshness | Restricted | All four page observation times and October 1 trade dates recorded; trade time, execution context and bid/ask missing. |
| Convention and vendor/calculation separation | Restricted | Vendor yields stay vendor yields; no unsourced settlement, spread, duration, YTW or price conversion. Arithmetic yield gaps identified separately. |
| Implied risk and repricing | Restricted | F1 disclosed but unrun; neither model probability nor bond-price shock fabricated. Material missing-input penalty included in confidence score. |
| Liquidity and technicals | Restricted | June issue faces are not presented as October liquidity; no ownership or flow direction asserted. |
| Fundamental conflict and subsequent events | Restricted | Conditional merger, post-June Alberta launch, reporting-period cash measures and debt-definition difference kept separate. |
| Recommendation boundary | Passed self-check | No buy/sell/hold, rich/cheap terminal finding, rank or position size; CP-3 retains selection ownership. |
| Canonical handoff self-check | Passed self-check | Exact derived filename stated; seven permitted model-authored YAML fields, six ordered H2 headings and T3E.1–T3E.10 present. Host validation follows this answer and is not claimed. |

**Downstream action:** CP-3 may consume the dated observation and explicit gaps, but must not turn this cross-section into executable relative value or an implied default estimate without the named additional evidence.