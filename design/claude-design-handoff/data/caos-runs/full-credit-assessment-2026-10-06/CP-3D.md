---
module_id: "CP-3D"
module_name: "MarketImpliedRisk"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-3D-10944f89f91e09e9"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-14-CP-3D"
credit_os_invocation_sha256: "e8d8878d0ff0beddadd73dd1f77cec39dffb09f951b5d875c58e94794e52de13"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-2H"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "6606e14634c94ec2953d4856bc385eee95c999a001689dab9025b795c7129ea0"
confidence_score: 44
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - "SOURCE_LIMITED_NOT_COMMITTEE_READY"
  - "LAST_TRADE_ONLY_NO_EXECUTABLE_QUOTES"
  - "NO_BENCHMARK_CURVE_OR_BOND_ANALYTICS"
  - "NO_COMPLETE_FUNDAMENTAL_ALIGNMENT"
validation_warnings:
  - "FINRA_LAST_TRADE_NOT_EXECUTABLE"
  - "PEERS_NOT_DURATION_OR_SENIORITY_MATCHED"
  - "NO_POST_Q2_MARKET_FUNDAMENTAL_BRIDGE"
downstream_consumers: [CP-3, CP-3A, CP-3B, CP-6]
---

## Audit Summary

Canonical handoff filename: `CZR_CP-3D_20261002.md`. Market evidence is partial: four FINRA last-trade observations dated October 1, 2026, were observed October 2; none is a bid, ask, mid, or evaluated quote. The Caesars observations establish quoted prices and reported yields for two issues, but delivered evidence lacks benchmark curves, spreads, duration, trade size, intraday trade time and executable depth. A June 30 fund schedule provides a separate, non-contemporaneous secured-note holding valuation. Peer observations are not maturity- or structure-matched. No issuer curve, break-even default/loss estimate or numerical scenario repricing is supportable without locked conventions and assumptions. QA status is Restricted; confidence is 44/100, Low. The assessment makes no default-probability claim or trade recommendation. Host validation follows this response; no host result is claimed.

## Analysis

### Market-implied view

At the October 2, 2026 observation, the supplied Caesars securities have October 1 last-trade yields of 8.063520% for the 6.50% February 2032 issue and 9.318398% for the 6.00% October 2032 issue; recorded prices are $93.28 and $84.94, respectively. [C5, C6, C13, C14] These prints indicate demanding required returns, but do not isolate credit from rates, calls, security, liquidity or transaction effects: the extract reports no benchmark, spread, trade size, or executable bid/ask. [C35] The 6.00% issue’s seniority is not established in this evidence. The small MGM/PENN set is not maturity- or structure-matched; the June fund valuation is not contemporaneous. The accepted CP-2H case cannot be numerically aligned to these prints. The defensible conclusion is a high-yield market signal with low diagnostic precision—not an implied default probability. A current curve, execution-quality quotes and later-period issuer data are needed to test repricing and fundamental divergence.

The most direct issuer-level market comparison is between the two Caesars trades. Their reported yields differ by 125.4878 basis points (9.318398% less 8.063520%); this is an arithmetic difference between last-trade yields, not an option-adjusted or benchmark spread. The notes differ in coupon and maturity, and the 6.00% issue’s seniority is unverified here, so the gap cannot be read as a clean security premium. Existing fixed coupons do not reset because of a lower trading price; the creditor transmission is through the cost and availability of future issuance or refinancing, if Caesars needs to access those markets.

The strongest contrary interpretation is that the October 1 prints may overstate a durable financing signal: they are last trades, not executable quotes, and no trade size, bid/ask, benchmark or intraday time is supplied. That challenge would win if current two-sided quotes and repeat trades showed materially different levels or if benchmark and matched-security analysis explained the apparent yield gap. Conversely, sustained weak operating performance could reduce cash available for fixed claims and make future refinancing more difficult; the accepted CP-2H handoff describes operating downside qualitatively, but does not provide a market-aligned, numerical case. [CP-2H C16, CP-2H C17, CP-2H C21]

#### Market-signal summary

The table summarizes only the supplied market observations; it does not represent executable pricing or a matched relative-value conclusion.

| Security | October 1 last trade | Reported yield | Next call | Signal caveat / source |
|---|---:|---:|---|---|
| Caesars 6.50% due 2032, CUSIP 12769GAC4 | $93.28 | 8.063520% | 2027-02-15 | Last trade only; [C1, C5, C6] |
| Caesars 6.00% due 2032, CUSIP 12769GAD2 | $84.94 | 9.318398% | 2027-10-15 | Seniority not established; [C9, C13, C14] |
| MGM 6.125% due 2029, CUSIP 552953CK5 | $98.42 | 6.722997% | 2026-10-11 | Different issuer and maturity; [C17, C21, C22] |
| PENN 4.125% due 2029, CUSIP 707569AV1 | $93.76 | 6.644415% | 2026-10-11 | Different issuer and maturity; [C25, C29, C30] |

### Analytical appendix — complete canonical registers

#### T3E.1 — Instrument and market source register

| security_id | issuer | currency | coupon | maturity/call | seniority | source | timestamp | quote_type | freshness |
|---|---|---|---|---|---|---|---|---|---|
| CUSIP 12769GAC4 | Caesars Entertainment, Inc. (FINRA display: CAESARS ENTMT INC NEW) | [Insufficient Information] — denomination not displayed | 6.500% | Maturity 2032-02-15; next call 2027-02-15 | Senior secured per fund schedule; CUSIP mapping aligned by issuer, coupon and maturity | FINRA Fixed Income Security Lookup; [C1, C2, C3, C4] | 2026-10-02 09:31:13Z; last trade 2026-10-01 | last_trade | Prior-day trade; not a current executable quote; intraday trade time absent |
| CUSIP 12769GAD2 | Caesars Entertainment, Inc. (FINRA display: CAESARS ENTMT INC NEW) | [Insufficient Information] — denomination not displayed | 6.000% | Maturity 2032-10-15; next call 2027-10-15 | [Insufficient Information] — seniority not established by delivered market extract | FINRA Fixed Income Security Lookup; [C9, C10, C11, C12] | 2026-10-02 09:31:27Z; last trade 2026-10-01 | last_trade | Prior-day trade; not a current executable quote; intraday trade time absent |
| CUSIP 552953CK5 | MGM Resorts International | [Insufficient Information] — denomination not displayed | 6.125% | Maturity 2029-09-15; next call 2026-10-11 | [Insufficient Information] — seniority not displayed in market extract | FINRA Fixed Income Security Lookup; [C17, C18, C19, C20] | 2026-10-02 09:32:08Z; last trade 2026-10-01 | last_trade | Prior-day trade; not a current executable quote; intraday trade time absent |
| CUSIP 707569AV1 | PENN Entertainment, Inc. | [Insufficient Information] — denomination not displayed | 4.125% | Maturity 2029-07-01; next call 2026-10-11 | [Insufficient Information] — seniority not displayed in market extract | FINRA Fixed Income Security Lookup; [C25, C26, C27, C28] | 2026-10-02 09:32:31Z; last trade 2026-10-01 | last_trade | Prior-day trade; not a current executable quote; intraday trade time absent |

#### T3E.2 — Market snapshot

| security_id | bid/mid/ask or evaluated price | yield | spread/OAS/DM | duration | benchmark | observation ID |
|---|---|---|---|---|---|---|
| CUSIP 12769GAC4 | $93.28 last trade; not bid/mid/ask/evaluated | 8.063520% FINRA last-trade yield; convention not stated | [Insufficient Information] — no spread/OAS/DM displayed | [Insufficient Information] — duration not displayed | [Insufficient Information] — benchmark not supplied | FINRA ERI5740550; October 1 trade; observed October 2 |
| CUSIP 12769GAD2 | $84.94 last trade; not bid/mid/ask/evaluated | 9.318398% FINRA last-trade yield; convention not stated | [Insufficient Information] — no spread/OAS/DM displayed | [Insufficient Information] — duration not displayed | [Insufficient Information] — benchmark not supplied | FINRA ERI5909471; October 1 trade; observed October 2 |
| CUSIP 552953CK5 | $98.42 last trade; not bid/mid/ask/evaluated | 6.722997% FINRA last-trade yield; convention not stated | [Insufficient Information] — no spread/OAS/DM displayed | [Insufficient Information] — duration not displayed | [Insufficient Information] — benchmark not supplied | FINRA MGM5885613; October 1 trade; observed October 2 |
| CUSIP 707569AV1 | $93.76 last trade; not bid/mid/ask/evaluated | 6.644415% FINRA last-trade yield; convention not stated | [Insufficient Information] — no spread/OAS/DM displayed | [Insufficient Information] — duration not displayed | [Insufficient Information] — benchmark not supplied | FINRA PENN5210723; October 1 trade; observed October 2 |

The four prices, yields and trade dates are reported last-trade fields, not calculated values. See Evidence Trace for source markers and observation locators. [C5, C6, C7, C13, C14, C15, C21, C22, C23, C29, C30, C31]

#### T3E.3 — Issuer curve

| security_id | maturity/call date | spread/yield | seniority | curve residual | explanation status |
|---|---|---|---|---|---|
| CUSIP 12769GAC4 | 2032-02-15 / next call 2027-02-15 | 8.063520% last-trade yield; spread unavailable | Senior secured per June fund schedule; mapping caveat in T3E.1 | [Insufficient Information] — no benchmark curve or matched issuer points | No issuer curve can be fitted from one secured Caesars point; call, liquidity and benchmark effects unresolved |
| CUSIP 12769GAD2 | 2032-10-15 / next call 2027-10-15 | 9.318398% last-trade yield; spread unavailable | [Insufficient Information] — seniority not established in delivered market extract | [Insufficient Information] — no benchmark curve or matched issuer points | Different coupon, maturity and unverified seniority prevent clean residual attribution |

#### T3E.4 — Peer/index context

| comparator | alignment basis | spread/yield/price | period | difference | comparability limitation |
|---|---|---|---|---|---|
| MGM Resorts 6.125% due 2029, CUSIP 552953CK5 | October 1 last-trade yield versus Caesars 6.50% due 2032 last-trade yield; arithmetic only | Yield 6.722997%; price $98.42 | Last trade 2026-10-01; observed 2026-10-02 | Caesars secured issue yield exceeds MGM by 134.0523 bp | Different issuer, maturity, coupon, call and unverified matched seniority; not a spread comparison |
| PENN 4.125% due 2029, CUSIP 707569AV1 | October 1 last-trade yield versus Caesars 6.50% due 2032 last-trade yield; arithmetic only | Yield 6.644415%; price $93.76 | Last trade 2026-10-01; observed 2026-10-02 | Caesars secured issue yield exceeds PENN by 141.9105 bp | Different issuer, maturity, coupon, call and unverified matched seniority; not a spread comparison |
| MGM Resorts 6.125% due 2029, CUSIP 552953CK5 | October 1 last-trade yield versus Caesars 6.00% due 2032 last-trade yield; arithmetic only | Yield 6.722997%; price $98.42 | Last trade 2026-10-01; observed 2026-10-02 | Caesars 6.00% issue yield exceeds MGM by 259.5401 bp | Different issuer, maturity, coupon, call and unverified Caesars seniority; not a spread comparison |
| PENN 4.125% due 2029, CUSIP 707569AV1 | October 1 last-trade yield versus Caesars 6.00% due 2032 last-trade yield; arithmetic only | Yield 6.644415%; price $93.76 | Last trade 2026-10-01; observed 2026-10-02 | Caesars 6.00% issue yield exceeds PENN by 267.3983 bp | Different issuer, maturity, coupon, call and unverified Caesars seniority; not a spread comparison |

Differences are calculations of reported yields: Caesars yield minus comparator yield, multiplied by 100 to express basis points. They are not matched-duration excess spreads. Source observations and terms are traced in Evidence Trace. [C3, C4, C6, C7, C19, C20, C21, C22, C23, C27, C28, C29, C30, C31]

#### T3E.5 — Implied risk calculations

| security_id | model | horizon | recovery | discount/benchmark | implied default/loss/break-even | formula ID | limitation |
|---|---|---|---|---|---|---|---|
| CUSIP 12769GAC4 | Not run — inputs not locked | [Insufficient Information] — no selected horizon | [Insufficient Information] — no recovery assumption | [Insufficient Information] — benchmark, yield convention, settlement, accrued interest and discounting not established | Not Calculable from Provided Materials — no break-even default/loss estimate supported | No formula applied; bond analytics inputs unavailable | Last-trade yield alone cannot identify default probability; call schedule and cash-flow conventions are not locked |
| CUSIP 12769GAD2 | Not run — inputs not locked | [Insufficient Information] — no selected horizon | [Insufficient Information] — no recovery assumption | [Insufficient Information] — benchmark, yield convention, settlement, accrued interest and discounting not established | Not Calculable from Provided Materials — no break-even default/loss estimate supported | No formula applied; bond analytics inputs unavailable | Seniority, call treatment and cash-flow conventions are unresolved; any output would be assumption-driven |

#### T3E.6 — Liquidity and technicals

| security_id | bid-ask | trade frequency/volume | issue size | ownership/flow/supply evidence | direction | confidence |
|---|---|---|---|---|---|---|
| CUSIP 12769GAC4 | [Insufficient Information] — no bid/ask or quote depth reported | [Insufficient Information] — one last-trade date; frequency, volume and days without trades not reported | [Insufficient Information] — issue size not reported in supplied market summary | June 30 fund schedule reports 550,000 principal valued at $536,927; no aggregate ownership, flow or supply evidence [C33, C34] | Liquidity direction unresolved; one last trade does not establish depth | Low; dated observation with no executable-liquidity data |
| CUSIP 12769GAD2 | [Insufficient Information] — no bid/ask or quote depth reported | [Insufficient Information] — one last-trade date; frequency, volume and days without trades not reported | [Insufficient Information] — issue size not reported in supplied market summary | [Insufficient Information] — no dated ownership, flow, dealer or new-issue evidence supplied | Liquidity direction unresolved; price/yield alone do not measure liquidity | Low; one last-trade observation only |

#### T3E.7 — Fundamental-versus-market map

| market implication | CP-2/2H/2R evidence | aligned/divergent | possible basis | unresolved question |
|---|---|---|---|---|
| Caesars yields show a high required return, but do not isolate fundamental credit from rate, option or liquidity components | CP-2H is accepted and Restricted; its qualitative context is not an aligned market metric. CP-2 and CP-2R are not in the accepted upstream set. | not_comparable | Missing matched operating forecast, benchmark, duration and executable market evidence | How much of observed yield is attributable to credit, liquidity, call optionality or market rates? |
| October 1 last-trade yield gap between Caesars issues is 125.4878 bp | CP-2H qualitative context cannot determine the security-level premium; no accepted CP-2/2R evidence resolves structural or recovery differences | not_comparable | Coupon, maturity, call and unverified seniority differ; same-issuer curve has insufficient points | Is the gap persistent and attributable to credit/security rather than trade noise or instrument terms? |
| Caesars-to-MGM/PENN yield gaps are positive on the raw arithmetic comparison | No aligned CP-2/2H/2R peer credit or agency metric is available in the accepted context | not_comparable | Different issuers, maturities, coupons, calls and security terms; no benchmark normalization | Would matched-maturity, matched-seniority executable quotes materially narrow or widen the differences? |

#### T3E.8 — Scenario repricing

| scenario | driver | spread/yield/price assumption | calculated move | convexity/call limitation |
|---|---|---|---|---|
| Credit-widening stress | Hypothetical deterioration in issuer credit or refinancing access | [Insufficient Information] — no numerical widening or yield assumption supplied | Not Calculable from Provided Materials — duration, spread sensitivity and clean-price basis unavailable | Callable instruments; call path, yield convention and convexity not modelled |
| Benchmark-rate move | Hypothetical change in benchmark rates, held distinct from credit spread | [Insufficient Information] — no benchmark curve or rate shock supplied | Not Calculable from Provided Materials — duration and rate sensitivity unavailable | No locked benchmark or callable-bond analytics; no price move asserted |
| Liquidity dislocation | Hypothetical widening of executable bid/ask or evaluated-to-trade gap | [Insufficient Information] — no bid/ask, depth or dispersion assumption supplied | Not Calculable from Provided Materials — no executable starting price or liquidity shock | Last trades are not executable marks; call and price/yield convexity remain unmodelled |

#### T3E.9 — Monitoring and handoff

| observable | threshold | cadence/event | downstream module | evidence source |
|---|---|---|---|---|
| New Caesars bond trades and observed price/yield | No calibrated threshold; compare only after trade size, side and timestamp are available | Each new trade or refreshed market observation | CP-3; CP-6 | FINRA last-trade observations; [C5, C6, C7, C13, C14, C15] |
| Two-sided quote, depth and evaluated-versus-executable gap | Obtain contemporaneous bid/ask and depth; no numeric tolerance set | Before any market-relative conclusion or liquidity decision | CP-3B | Current dealer/evaluated data required; absent from supplied observations [C35] |
| Benchmark curve and matched issuer/peer yields | Build duration- and structure-matched comparisons; no numeric residual threshold set | On refreshed curve or new comparable issue | CP-3; CP-3A | Benchmark and matched-peer sources required; not displayed in FINRA extracts [C35] |
| Issuer operating and financing updates | Reconcile later-period data to market date before drawing a fundamental-market divergence | Next issuer filing, financing event or material operating update | CP-3; CP-6 | CP-2H accepted handoff is Restricted; post-Q2 financials not delivered |
| June fund holding versus current market evidence | Do not treat as a current quote; refresh same-date valuation and market price | At next portfolio schedule or matched market observation | CP-3B; CP-6 | Federated Hermes schedule is dated June 30, 2026; [C33, C34] |

#### T3E.10 — Gaps and conflicts

| missing/stale/conflicting item | affected calculation/security | impact | required evidence |
|---|---|---|---|
| FINRA observations are last trades, not bid/mid/ask or evaluated marks; trade size and intraday time absent | All four securities; current price, liquidity and freshness assessment | Cannot establish executable level, depth, volume or intraday freshness; one-day date difference does not prove a current market | Timestamped two-sided quotes, trade size/volume, quote depth and evaluated-price methodology |
| Benchmark curves, spread/OAS/DM, duration and yield conventions absent | Caesars securities and all peer comparisons | Issuer curve residuals, spread decomposition and matched relative-value analysis unavailable | Same-time benchmark curve; aligned spread conventions; duration, settlement, accrued-interest and yield-to-call/worst analytics |
| Seniority for CUSIP 12769GAD2 and peer issues not established by delivered market extracts | T3E.1, T3E.3, T3E.4 and recovery-sensitive comparisons | Cannot attribute observed yield differences to structural subordination, lien priority or recovery | Current instrument terms, indenture/guarantee and collateral/intercreditor evidence matched to CUSIP |
| June 30 fund valuation and October 1 FINRA trade have different dates and valuation bases | CUSIP 12769GAC4; apparent price comparison and freshness | Date-basis difference, not a like-for-like price conflict; fund valuation is not an October executable quote | Same-date independently identified evaluated or executable price and transaction details |
| No recovery assumption, horizon, benchmark discounting or locked cash-flow conventions | T3E.5 for both Caesars issues | No break-even default, loss or implied-probability calculation can be responsibly produced | Explicit recovery/horizon assumptions and a supported analytics run using verified terms and conventions |
| No duration, convexity, rate shock or spread shock assumptions | T3E.8 for all issues | Scenario repricing and price sensitivity remain uncalculated | Verified duration/call analytics and explicit, labelled scenario assumptions |
| Fundamental inputs are not numerically matched to October trades; CP-2H is Restricted | T3E.7 and market/fundamental conclusion | Pricing cannot be reconciled to current leverage, liquidity or forecast headroom; risk may be priced or unpriced | Current issuer financials, debt/cash schedule and supported forward cases aligned to the market date |

## Evidence Trace

| claim | marker | document | page |
|---|---|---|---:|
| Caesars 6.50% 2032 security identifier, coupon, maturity, next call and October 1 last-trade price/yield/date; October 2 observation time | [C1, C2, C3, C4, C5, C6, C7, C8] | FINRA Fixed Income Security Lookup, CUSIP 12769GAC4 | 1 |
| Caesars 6.00% 2032 security identifier, coupon, maturity, next call and October 1 last-trade price/yield/date; October 2 observation time | [C9, C10, C11, C12, C13, C14, C15, C16] | FINRA Fixed Income Security Lookup, CUSIP 12769GAD2 | 1 |
| MGM 6.125% 2029 terms and October 1 last-trade price/yield/date; October 2 observation time | [C17, C18, C19, C20, C21, C22, C23, C24] | FINRA Fixed Income Security Lookup, CUSIP 552953CK5 | 1 |
| PENN 4.125% 2029 terms and October 1 last-trade price/yield/date; October 2 observation time | [C25, C26, C27, C28, C29, C30, C31, C32] | FINRA Fixed Income Security Lookup, CUSIP 707569AV1 | 1 |
| June 30 date for the fund schedule used as a non-contemporaneous holding comparison | [C33] | Federated Hermes Sustainable High Yield Bond Fund portfolio | 1 |
| June 30 principal and reported value of the Caesars 6.50% secured-note holding | [C34] | Federated Hermes Sustainable High Yield Bond Fund portfolio | 4 |
| Summary does not display spread, benchmark curve, seniority, dealer quote, trade size or intraday timestamp | [C35] | FINRA Fixed Income Security Lookup, CUSIP 12769GAC4 | 1 |

## Source Registry

| source | use | observation/period | limitation |
|---|---|---|---|
| FINRA Fixed Income Security Lookup, CUSIP 12769GAC4 | Caesars 6.50% issue identity and last-trade fields [C1, C2, C3, C4, C5, C6, C7, C8] | Observed October 2, 2026; last trade October 1, 2026 | Summary identifies last trade, not bid, mid, ask or evaluated price; no spread, benchmark curve, trade size or intraday timestamp [C35]. |
| FINRA Fixed Income Security Lookup, CUSIP 12769GAD2 | Caesars 6.00% issue identity and last-trade fields [C9, C10, C11, C12, C13, C14, C15, C16] | Observed October 2, 2026; last trade October 1, 2026 | Last-trade observation only; seniority and yield convention are not established in the delivered summary. |
| FINRA Fixed Income Security Lookup, CUSIP 552953CK5 | MGM comparator terms and last-trade fields [C17, C18, C19, C20, C21, C22, C23, C24] | Observed October 2, 2026; last trade October 1, 2026 | One peer issue; not a maturity-, seniority- or structure-matched benchmark. |
| FINRA Fixed Income Security Lookup, CUSIP 707569AV1 | PENN comparator terms and last-trade fields [C25, C26, C27, C28, C29, C30, C31, C32] | Observed October 2, 2026; last trade October 1, 2026 | One peer issue; not a maturity-, seniority- or structure-matched benchmark. |
| Federated Hermes Sustainable High Yield Bond Fund portfolio of investments | June 30 schedule identifies a Caesars 6.50% senior secured note holding and value [C33, C34] | June 30, 2026 | Fund valuation is a separate date and source basis; not contemporaneous or executable October market evidence. |
| Caesars 6.50% notes indenture excerpt | Selected collateral, defeasance, amendments and guarantee provisions | 2024 indenture excerpt; delivered pages 31–35 | Targeted excerpt only; not used to infer a complete current collateral or intercreditor package. |

## Gaps & Conflicts

The primary limitation is quote quality: the observed FINRA fields are last trades rather than executable bids or offers, and no trade size, spread, benchmark, duration or intraday trade time is provided. Thus, “fresh” means only that the summary was observed on October 2 and identifies an October 1 trade; it does not establish a currently executable level. [C7, C8, C15, C16, C35]

The Caesars June fund schedule and October FINRA observation are not conflicting prices on a like-for-like basis: dates and valuation bases differ. The schedule lists 550,000 principal of a 6.50% senior secured note at $536,927 on June 30; it cannot be treated as a current October quote. [C33, C34]

Issuer-curve and peer residuals remain unresolved because no matched benchmark curve, spread convention, duration, or complete security seniority data is supplied. The arithmetic yield gaps in T3E.4 should not be interpreted as credit spreads. Fundamental reconciliation is also limited: the accepted CP-2H handoff is Restricted, and no aligned numeric current-case bridge can be established from the delivered market evidence. No source supports a factual default probability, and no unsupported market level or scenario move is inferred.

## QA Validation

| check | result | note |
|---|---|---|
| Instrument identifiers and available coupon, maturity and call terms | PASS WITH LIMITATIONS | FINRA CUSIPs and displayed terms captured; denomination and some seniority details are not established. |
| Timestamp, source and quote type | PASS WITH LIMITATIONS | Each FINRA observation carries its observed timestamp and last-trade date; no intraday transaction timestamp is displayed. |
| Price, yield, spread, benchmark and duration conventions | RESTRICTED | Prices/yields are last-trade fields; spread, benchmark, duration, settlement and yield convention are not locked. |
| Vendor values separated from calculations | PASS | Reported yields and prices remain identified as last trades; yield differences are labelled arithmetic calculations. |
| Implied risk and recovery assumptions | RESTRICTED | No default/loss estimate is stated because horizon, recovery, discounting and cash-flow conventions are unavailable. |
| Liquidity, ownership, flow and supply claims | RESTRICTED | Only a dated fund holding is available; no bid/ask, volume, depth, ownership aggregate, flow or supply evidence. |
| Fundamental-versus-market disagreement | RESTRICTED | CP-2H context is not quantitatively aligned with October trades; missing comparison remains explicit. |
| Unsupported market values, probabilities or recommendations | PASS | No fabricated quote, factual default probability, trade recommendation, ranking or sizing conclusion. |
| Required canonical registers and columns | SELF-CHECKED | T3E.1–T3E.10 included, each with required columns and at least one body row. |
| Confidence calculation | RESTRICTED | E=75, C=45, S=0.70, P=0; (0.6×75 + 0.4×45)×0.70 = 44.1, rounded to 44; band Low. Coverage is partial because core curve, convention and liquidity fields are missing. |
| Final status | RESTRICTED | Committee status Requires More Work; no committee-ready relative-value or implied-risk conclusion. |
| Host automated validation | PENDING | Host validation follows this response; no host script result or finding is claimed. |