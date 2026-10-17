---
module_id: "CP-1C"
module_name: "PeerBenchmark"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1C-566ac1b49e930df5"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-06-CP-1C"
credit_os_invocation_sha256: "00b3b2c69bbb11338046c2437c145d58194a828c529211b5101b406342e4a5d4"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
confidence_score: 49
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "PEER_SET_LIMITED_TO_MGM_AND_PENN", "NO_PEER_MARKET_CAP_OR_EV_DATA", "NO_TRANSACTION_COMPS", "NO_POST_Q2_2026_FINANCIALS"]
validation_warnings: ["FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "PEER_DISCOVERY_LIMITED_TO_DELIVERED_SOURCES", "PEER_DEFINITIONS_AND_PERIODS_NOT_FULLY_ALIGNED"]
downstream_consumers: [CP-2, CP-3, CP-5, CP-5A]
---

## Audit Summary

CP-1C completed with limitations. The accepted CP-0 and CP-1 artifacts match the run, issuer and Q2 2026 period. The peer evidence delivered here supports a constrained operating comparison with MGM Resorts International and PENN Entertainment, Inc., plus dated bond-market context; it does not support a complete peer universe, current valuation multiples, or robust peer statistics. Peer results are Q2 2026, while the closest Caesars operating metrics are inherited from the accepted CP-1 handoff; both are issuer-reported, but Adjusted EBITDA definitions and business perimeters differ. Market observations are October 1 last trades, not executable quotes. Confidence is 49/100 (Low), QA is Restricted, and committee status is Requires More Work.

## Analysis

### Credit view

Caesars’ Q2 2026 operating position can be screened against MGM and PENN, but not ranked robustly: the delivered set contains only two gaming peers and their issuer-defined EBITDA measures are not fully aligned. CP-1 reports Caesars Q2 revenue of $2,993 million and Adjusted EBITDA of $920 million [CP-1 C16, C17]; peer Q2 revenue and Adjusted EBITDA were $4,451 million/$610 million for MGM [C1, C2] and $1,857 million/$313 million for PENN [C4, C5]. The resulting margin differences are directional, not a like-for-like profitability verdict. Last-trade yields also differ, but maturity, security and issuer risks prevent clean relative-value inference. Missing peer EVs and transaction data mean valuation support cannot be quantified; monitor comparable filings and current quotes before using this screen for credit sizing.

#### Borrower-versus-peer snapshot

The compact comparison below shows the reported Q2 scale and issuer-defined Adjusted EBITDA margin; definitions are not identical, so the margin contrast is a screening signal rather than a ranking.

| Entity | Q2 revenue (USD m) | Q2 Adjusted EBITDA (USD m) | EBITDA margin | Revenue growth | Credit reading |
|---|---:|---:|---:|---:|---|
| Caesars | 2,993 [CP-1 C17] | 920 [CP-1 C16] | 30.7% [CP-1 C16, C17] | 3.0% [CP-1 C17] | Higher reported margin; issuer definition and perimeter need alignment. |
| MGM | 4,451 [C1] | 610 [C2] | 13.7% [C1, C2] | 1.0% [C1] | Larger revenue base; EBITDA measure reflects MGM’s issuer methodology. |
| PENN | 1,857 [C4] | 313 [C5] | 16.8% [C4, C5] | 5.2% [C4] | Smaller revenue base; reported Adjusted EBITDA increased year over year. |

**Operating and cash-flow interpretation.** CP-1’s Q2 figures imply higher Caesars Adjusted EBITDA margin than either selected peer, but a favorable-looking margin is not itself evidence of superior debt-service capacity: Caesars’ issuer-specific adjustment basis must be reconciled before attributing the difference to operating efficiency. MGM reported Q2 operating income of $503.6 million [C3]; PENN reported capital expenditures of $97.5 million for Q2 [C6]. The supplied peer materials do not provide matched cash-flow, maintenance-capex or working-capital measures for all three issuers. Therefore comparative FCF durability and cash conversion remain unassessed; missing cash data could reverse any conclusion drawn from EBITDA margins alone.

**Leverage, liquidity and market context.** CP-1 reports Caesars LTM carrying debt/Adjusted EBITDA of 3.26x, net debt/Adjusted EBITDA of 2.99x, senior secured debt/Adjusted EBITDA of 2.61x, and reported liquidity of $2,928 million [CP-1 C8, C10 and CP-1 T4.9]. These are issuer calculations with a June 30, 2026 basis, not matched peer leverage ratios. PENN reports total liquidity of $1.9 billion at June 30, 2026 [C7]. MGM’s reported long-term debt and cash are visible in the delivered results, but comparable debt perimeters and undrawn liquidity are not established [C12, C13]. Do not infer relative leverage from those isolated balance-sheet amounts.

FINRA’s October 1 last-trade yields were 9.318398% for Caesars’ 6.00% notes due 2032 [C10], 8.063520% for Caesars’ 6.50% secured notes due 2032 [C11], 6.644415% for PENN’s 4.125% notes due 2029 [C8], and 6.722997% for MGM’s 6.125% notes due 2029 [C9]. These observations are not bids or spreads. Differences in maturity, rating, coupon and instrument structure—plus the absence of trade size and benchmark yields—mean they are market context only, not a matched credit spread comparison. The fund schedule separately lists a June 30 position in Caesars’ secured 6.50% notes at $536,927 [C14]; that dated holding valuation is not contemporaneous with the October last trades.

**Strongest contrary evidence and downside pathway.** The strongest positive counterargument is Caesars’ higher reported Q2 Adjusted EBITDA margin and a diversified selected peer backdrop. It would strengthen a relative operating view if a consistent EBITDA bridge, comparable cash conversion and subsequent-period results confirmed the margin advantage. It does not establish lower leverage or greater refinancing capacity. If gaming demand or hold weakens, the first break would be lower property revenue and EBITDA; weaker operating cash conversion would then reduce debt repayment capacity and liquidity headroom, increasing refinancing sensitivity. The supplied evidence cannot quantify that stress or current covenant capacity. Monitor later-period revenue and EBITDA, cash flow/capex, debt and liquidity, and current bid-side bond observations. No peer post-Q2 financial update is supplied; Q2 peer data are already several months old at the analysis date.

**Valuation context.** No market capitalization, complete enterprise value inputs, public trading multiples, or contemporaneous transaction multiples are supplied. The required EV formula is equity value plus total debt, minority interests and preferred equity, less cash and liquid short-term investments. Missing inputs prevent an EV calculation for the borrower and peers; implied EV is therefore not calculable. This is a valuation-context limitation, not evidence of zero enterprise value or a recovery estimate.

### Analytical appendix — complete canonical registers

#### T4.D1 — Peer Discovery Source Register

| Candidate | Query / Source | URL or Source Locator | Retrieval Date | Dimensions Assessed | Promotion Decision | Evidence Tag | Limitation |
|---|---|---|---|---|---|---|---|
| MGM Resorts International | Delivered Q2 2026 issuer results; gaming and resort operator | Q2 2026 results release, pp. 1, 3–5 [C1, C2, C3] | 2026-10-02 observation pack | Gaming services, revenue model, geography, public-company status, period, USD/US GAAP, operating data, source provenance; other dimensions incomplete | Retain as a limited sector operating peer; not an approved valuation comp | Document-Disclosed; public issuer report | No complete debt, cash-flow, market-cap or EV/multiple dataset; EBITDA measure requires reconciliation. |
| PENN Entertainment, Inc. | Delivered Q2 2026 issuer results; gaming, retail casino and interactive operator | Q2 2026 results release, pp. 1–4 [C4, C5, C6, C7] | 2026-10-02 observation pack | Gaming services, revenue model, North American geography, public-company status, period, USD/US GAAP, operating/capex data, source provenance; other dimensions incomplete | Retain as a limited sector operating peer; not an approved valuation comp | Document-Disclosed; public issuer report | No complete matched cash-flow or EV/multiple dataset; rent and EBITDA definitions differ. |
| Selected bond observations: MGM, PENN and Caesars | Delivered FINRA Fixed Income Security Lookup summaries | FINRA records, CUSIPs 552953CK5, 707569AV1, 12769GAD2 and 12769GAC4 [C8, C9, C10, C11] | Observed 2026-10-02; last trades dated 2026-10-01 | Issuer, coupon, maturity, callable status, ratings shown, last-trade price/yield and trade date | Use only for dated bond-market context; not a normalized peer set | FINRA public lookup; last-trade observation | No spread, benchmark curve, trade size, dealer quote or bid/ask; differing maturity and instrument terms. |

Auto-discovery was constrained to the supplied evidence pack; no web retrieval or external peer verification was available. These document-disclosed candidates are not represented as “Web-Scraped — Unverified” discoveries. The source limitation reduces universe breadth and does not satisfy a full 16-dimension peer search.

#### T4.1 — Peer Universe Register

| Entity Name | Peer Category Label | Source of Selection | Dimensions Assessed | Strengths | Limitations | Data Availability | Evidence Quality Tier | Usable For | Exclusion Reason |
|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Borrower/Issuer | CP-1 accepted canonical handoff; Caesars bond observations in delivered evidence [CP-1 C16, C17; C10, C11] | Public issuer; gaming and resort services; Q2 2026 period; USD; US GAAP; consolidated operating measures; dated bond terms; other dimensions as available | Borrower baseline includes Q2 operating measures, LTM debt ratios and reported liquidity in CP-1 | No later financials; distinct debt, lease and EBITDA definitions; current market quote unavailable | Q2/H1 2026 financials through CP-1; Oct. 1 bond last trades | Upstream financial handoff; FINRA primary public observation | Borrower anchor for directional operating and market context | — |
| MGM Resorts International | Sector Peer; Public Trading Comp | Delivered Q2 2026 issuer release and FINRA bond observation [C1, C2, C3, C9] | Gaming services; revenue model; public status; Q2 2026; USD; US GAAP; operating data; bond coupon/maturity/yield; other dimensions incomplete | Q2 revenue, issuer Adjusted EBITDA, operating income and selected balance-sheet data | Different operating and lease perimeter; insufficient comparable leverage, FCF, market cap and EV data | Q2 2026 release; Oct. 1, 2026 bond last trade | Document-Disclosed issuer results; FINRA last-trade observation | Directional operating comparison; dated bond context | Exclude from quantitative valuation statistics: no EV or market multiples. |
| PENN Entertainment, Inc. | Sector Peer; Public Trading Comp | Delivered Q2 2026 issuer release and FINRA bond observation [C4, C5, C6, C7, C8] | Gaming services; public status; Q2 2026; USD; US GAAP; operating and capex data; bond coupon/maturity/yield; other dimensions incomplete | Q2 revenue, issuer Adjusted EBITDA, capex and reported liquidity | Retail/interactive mix and rent treatment differ; no matched CFO, full debt metrics or valuation multiples | Q2 2026 release; Oct. 1, 2026 bond last trade | Document-Disclosed issuer results; FINRA last-trade observation | Directional operating/capex comparison; dated bond context | Exclude from quantitative valuation statistics: no EV or market multiples. |

#### T4.2 — Metric Alignment Register

| Metric | Borrower Value | Borrower Period | Peer Entity | Peer Value | Peer Period | AP1-AP11 | Comparability Status | Limitation Notes |
|---|---|---|---|---|---|---|---|---|
| Revenue | $2,993m [CP-1 C17] | Q2 2026 | MGM Resorts International | $4,451m [C1] | Q2 2026 | AP1 reported consolidated revenue; AP2 reported consolidated revenue; AP3 same quarter; AP4 USD; AP5 US GAAP; AP6 actual; AP7 reported; AP8 quarterly; AP9 CP-1 vs issuer release; AP10 unit conversion to USD m; AP11 limited definition/perimeter differences | Comparable with Limitations | Caesars is from CP-1 and MGM from issuer release; business mix and consolidation perimeter need review. |
| Revenue | $2,993m [CP-1 C17] | Q2 2026 | PENN Entertainment, Inc. | $1,857.4m [C4] | Q2 2026 | AP1 reported consolidated revenue; AP2 reported consolidated revenue; AP3 same quarter; AP4 USD; AP5 US GAAP; AP6 actual; AP7 reported; AP8 quarterly; AP9 CP-1 vs issuer release; AP10 unit conversion to USD m; AP11 limited definition/perimeter differences | Comparable with Limitations | PENN Interactive revenue includes stated tax gross-up; different retail/digital mix. |
| Adjusted EBITDA | $920m [CP-1 C16] | Q2 2026 | MGM Resorts International | $610.4m [C2] | Q2 2026 | AP1 Caesars issuer Adjusted EBITDA; AP2 MGM Consolidated Adjusted EBITDA; AP3 same quarter; AP4 USD; AP5 US GAAP reporting; AP6 actual; AP7 adjusted/non-GAAP; AP8 quarterly; AP9 mixed primary issuer sources; AP10 no bridge; AP11 definition mismatch | Comparable with Limitations | Different issuer adjustments and lease/rent treatment; no harmonized bridge. |
| Adjusted EBITDA | $920m [CP-1 C16] | Q2 2026 | PENN Entertainment, Inc. | $312.6m [C5] | Q2 2026 | AP1 Caesars issuer Adjusted EBITDA; AP2 PENN Consolidated Adjusted EBITDA; AP3 same quarter; AP4 USD; AP5 US GAAP reporting; AP6 actual; AP7 adjusted/non-GAAP; AP8 quarterly; AP9 mixed primary issuer sources; AP10 no bridge; AP11 definition mismatch | Comparable with Limitations | Different issuer adjustments; PENN separately reports triple-net lease expense. |
| Cash flow / FCF | Not established for Q2 in CP-1 | Q2 2026 | PENN Entertainment, Inc. | Capex $97.5m reported; CFO/FCF not supplied [C6] | Q2 2026 | AP1 CFO/FCF unavailable; AP2 capex reported only; AP3 same quarter; AP4 USD; AP5 US GAAP; AP6 actual; AP7 reported; AP8 quarterly; AP9 peer release; AP10 no CFO/FCF normalization; AP11 insufficient shared metric | Insufficient Information | Capex alone is not FCF; no common cash-flow numerator. |
| Leverage and liquidity | CP-1 LTM debt/Adjusted EBITDA 3.26x; net 2.99x; reported liquidity $2,928m [CP-1 C8, C10] | LTM/June 30, 2026 | PENN Entertainment, Inc. | Traditional net debt $1,927.5m; total liquidity $1.9bn, source-reported [C7] | June 30, 2026 | AP1 CP-1 carrying debt/issuer EBITDA; AP2 PENN traditional net debt and stated liquidity; AP3 same balance-sheet date but differing LTM conventions; AP4 USD; AP5 US GAAP issuer reporting; AP6 actual; AP7 issuer-defined; AP8 LTM/balance sheet; AP9 mixed sources; AP10 no denominator/perimeter reconciliation; AP11 not aligned for leverage | Comparable with Limitations | Do not infer a leverage ratio from source-reported PENN debt without aligned LTM EBITDA and definitions. |
| Bond last-trade yield | 9.318398% for Caesars 6.00% notes due 2032 [C10] | Last trade 2026-10-01 | PENN Entertainment, Inc. | 6.644415% for 4.125% notes due 2029 [C8] | Last trade 2026-10-01 | AP1 last-trade yield; AP2 last-trade yield; AP3 same trade date; AP4 USD; AP5 issuer/market instrument terms; AP6 actual trade summary; AP7 FINRA-reported; AP8 point-in-time; AP9 FINRA; AP10 none; AP11 instrument mismatch | Not Comparable | Different issuer, coupon, maturity and bond terms; no spread curve, trade size, bid/ask or quote basis. |

#### T4.3 — Operating Benchmark

| Entity | Revenue | Rev Growth | Gross Margin | EBITDA | EBITDA Margin | EBIT Margin | Period | Currency | Calc Status | Comp Status |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| Caesars Entertainment, Inc. | $2,993m [CP-1 C17] | 3.0% [CP-1 C17] | — | Adjusted EBITDA $920m [CP-1 C16] | 30.7% [CP-1 C16, C17] | 17.1% [CP-1 T4.4] | Q2 2026 | USD | Reported / Calculated | Comparable with Limitations |
| MGM Resorts International | $4,451m [C1] | 1.0% [C1] | — | Consolidated Adjusted EBITDA $610.4m [C2] | 13.7% [C1, C2] | 11.3% [C1, C3] | Q2 2026 | USD | Reported / Calculated | Comparable with Limitations |
| PENN Entertainment, Inc. | $1,857.4m [C4] | 5.2% [C4] | — | Consolidated Adjusted EBITDA $312.6m [C5] | 16.8% [C4, C5] | 7.1% [C4] | Q2 2026 | USD | Reported / Calculated | Comparable with Limitations |

Gross margin is not separately disclosed on a harmonized basis. Calculated margins use issuer-reported EBITDA and revenue; EBIT margin uses issuer-reported operating income where available. Caesars EBIT is carried from the accepted CP-1 handoff. EBITDA definitions and segment/perimeter differences remain unbridged; margins are descriptive and not a normalized ranking.

#### T4.4 — Cash Flow & Cap Intensity

| Entity | FCF | FCF Conversion | Capex/Rev | Capex/EBITDA | WC/Rev | Period | Currency | Calc Status | Comp Status |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| Caesars Entertainment, Inc. | FCF proxy $610m, CFO less PP&E purchases [CP-1 T4.8] | 17.0% | 5.9% | 19.1% | — | LTM to June 30, 2026 | USD | Calculated; proxy only | Comparable with Limitations |
| MGM Resorts International | — | — | — | — | — | Q2 2026 | USD | Insufficient Information | Insufficient Information |
| PENN Entertainment, Inc. | — | — | 5.2% | 31.2% | — | Q2 2026 | USD | Calculated | Comparable with Limitations |

Caesars proxy uses CFO less PP&E purchases and issuer Adjusted EBITDA as shown in CP-1; it is not issuer-reported FCF and is LTM, not Q2. PENN Q2 capex/revenue and capex/Adjusted EBITDA are calculated from $97.5m capex [C6], $1,857.4m revenue [C4] and $312.6m Adjusted EBITDA [C5]. No matched peer FCF, working-capital or maintenance/growth capex data are available; no statistics are calculated.

#### T4.5 — Credit Metric Benchmark

| Entity | Total/Net/Sr Sec Leverage | Int Coverage | Adj Int Coverage | FFO/Debt | Liquidity | Period | Currency | Calc Status | Comp Status |
|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | 3.26x / 2.99x / 2.61x [CP-1 T4.9] | 1.58x P&L basis, H1 [CP-1 T4.9] | — | — | $2,928m [CP-1 C10] | LTM to June 30, 2026; liquidity at June 30 | USD | Calculated from CP-1 definitions | Comparable with Limitations |
| MGM Resorts International | — / — / — | — | — | — | Cash $2,547.4m; undrawn facilities not established [C12] | June 30, 2026 | USD | Insufficient Information | Insufficient Information |
| PENN Entertainment, Inc. | — | — | — | — | $1.9bn reported total liquidity [C7] | June 30, 2026 | USD | Reported | Comparable with Limitations |

Peer leverage, coverage and FFO/debt remain uncalculated because matched debt perimeters, trailing EBITDA/FFO and cash-interest data are absent. The reported cash and liquidity observations above are not equivalent measures. MGM’s reported long-term debt, net, is $6,068.4m [C13], but the supplied excerpt does not establish an aligned total-debt and undrawn-liquidity basis.

#### T4.6 — Summary Statistics

| Metric | Borrower Value | Peer Avg | Median | Min | Max | Q1 | Q3 | N | Borrower Position |
|---|---|---|---|---|---|---|---|---:|---|
| Q2 Adjusted EBITDA margin | 30.7% [CP-1 C16, C17] | — | — | — | — | — | — | 0 qualifying | Not ranked; only two selected peers and issuer definitions/perimeters are not harmonized. |
| LTM FCF conversion | 17.0% proxy [CP-1 T4.8, T4.9] | — | — | — | — | — | — | 0 qualifying | Not ranked; no matching peer FCF data. |
| LTM debt/Adjusted EBITDA | 3.26x [CP-1 T4.9] | — | — | — | — | — | — | 0 qualifying | Not ranked; peer leverage bases and denominators are unavailable. |

No peer averages, medians or quartiles are reported: fewer than the required comparable observations exist. The two peers are descriptive comparison points only; no ranking or aggregate is justified.

#### T4.7 — Outlier Register

| Entity | Metric | Value | Peer Range (Min/Max/Med/Avg) | Deviation | Direction | Operating Impl | CF Impl | Lev/Liq Impl | Refi Impl | Valuation Impl | Downstream Handoff |
|---|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Q2 Adjusted EBITDA margin; outlier test | 30.7% [CP-1 C16, C17] | Not established; no qualifying comparable distribution | Not calculated; definitions differ and N is insufficient | Insufficient Information | Higher reported margin is a screening observation, not a confirmed operating outlier. | Peer cash conversion is unavailable; no inference about relative FCF. | Borrower leverage metrics exist in CP-1; peers cannot be normalized. | No matched peer leverage or refinancing comparison. | No sourced trading multiples or implied EV. | CP-2 and CP-3 may use only as a limited screening reference; CP-5/CP-5A should preserve these comparability limitations. |

#### T4.8 — Public Trading Comps

| Entity | Mkt Cap | Mkt Cap Date | EV | EV/Rev | EV/EBITDA | Period Used | Metric Def | Comp Status | Source |
|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | — | — | — | — | — | Q2 2026 financials; market inputs absent | EV requires equity value + total debt + minority interests + preferred equity − cash and liquid short-term investments | Insufficient Information | No market-cap or complete EV component evidence in delivered sources. |
| MGM Resorts International | — | — | — | — | — | Q2 2026 | Same EV formula; market inputs and consistent EBITDA denominator absent | Insufficient Information | Q2 release [C1, C2]; no market-cap or EV data supplied. |
| PENN Entertainment, Inc. | — | — | — | — | — | Q2 2026 | Same EV formula; market inputs and consistent EBITDA denominator absent | Insufficient Information | Q2 release [C4, C5]; no market-cap or EV data supplied. |

No market capitalization, complete EV inputs or sourced trading multiples were supplied. No multiple aggregation or implied valuation is supportable; last-trade bond data are not enterprise-value evidence.

#### T4.9 — Transaction Comps

| Txn Name | Date | Type | Buyer/Seller | TV | TV/Rev | TV/EBITDA | Period Used | Metric Def | Comp Status | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| No qualifying gaming transaction evidence supplied | — | — | — | — | — | — | — | Contemporaneous transaction value and financial denominator not provided | Insufficient Information | No transaction-comparable source in delivered evidence. |

#### T4.10 — Implied EV

| Method | Multiple Source | Multiple Value | Borrower Metric | Period | Implied EV | Low | Median | High | Calc Status | Limitations |
|---|---|---|---|---|---|---|---|---|---|---|
| EV/EBITDA | No qualifying public peer multiple | — | Caesars Adjusted EBITDA; CP-1 Q2 and LTM measures available | Q2/LTM 2026 | — | — | — | — | Insufficient Information | Peer multiples and aligned EBITDA definitions are absent. Context only; not recovery or debt coverage. |
| EV/Revenue | No qualifying public peer multiple | — | Caesars revenue; CP-1 Q2 and LTM measures available | Q2/LTM 2026 | — | — | — | — | Insufficient Information | Peer EVs/multiples and aligned period data are absent. Context only; not recovery or debt coverage. |
| Transaction EV/EBITDA | No qualifying transaction multiple | — | Caesars Adjusted EBITDA; CP-1 | Q2/LTM 2026 | — | — | — | — | Insufficient Information | Transaction value, transaction date and contemporaneous denominator are absent. |
| Transaction EV/Revenue | No qualifying transaction multiple | — | Caesars revenue; CP-1 | Q2/LTM 2026 | — | — | — | — | Insufficient Information | Transaction value, transaction date and contemporaneous denominator are absent. |

#### T4.11 — Gaps & Limitations

| Gap | Affected Metric/Section | Affected Peer(s) | Downstream Impact | Severity | Action |
|---|---|---|---|---|---|
| Peer evidence set is limited to MGM and PENN and no independent web discovery was possible in this run. | T4.D1, T4.1, T4.2, T4.6 | Caesars, MGM, PENN | A two-peer screen cannot establish a sector distribution or robust relative position. | MATERIAL | Obtain a broader independently verified gaming peer set with comparable filings and data. |
| EBITDA definitions, lease treatment and business perimeters differ. | T4.2, T4.3, T4.6, T4.7, T4.10 | Caesars, MGM, PENN | Apparent margin differences may reflect adjustments/perimeter rather than operating advantage; affects PD and debt-service comparison. | MATERIAL | Reconcile source definitions and rent treatment before any ranking or statistic. |
| Peer cash-flow and working-capital data are incomplete or unmatched. | T4.4, T4.6 | MGM, PENN | FCF durability, cash conversion and capex burden cannot be compared. | MATERIAL | Obtain matched cash-flow statements, capex detail and working-capital schedules. |
| Peer leverage and coverage cannot be aligned to Caesars’ CP-1 ratios. | T4.2, T4.5, T4.6 | MGM, PENN | No relative debt-service, leverage tolerance or refinancing conclusion is supported. | MATERIAL | Obtain peer debt schedules, LTM EBITDA/FFO and cash-interest definitions. |
| Market capitalization, complete EV components and trading multiples are not present. | T4.8, T4.10 | Caesars, MGM, PENN | No trading-comps valuation context or implied EV range can be produced. | MATERIAL | Obtain dated market-cap data and complete balance-sheet EV inputs with matched denominator periods. |
| No transaction-comparable values or contemporaneous financial denominators are supplied. | T4.9, T4.10 | Gaming transaction set | Transaction multiple context is unavailable. | MATERIAL | Obtain sourced transaction terms and financials contemporaneous with each deal. |
| FINRA observations are last trades, not quotes, and omit spread, benchmark, size and intraday time. | T4.D1, T4.2, T4.7 | Caesars, MGM, PENN bonds | Bond yield differences cannot isolate issuer credit or establish executable relative value. | MATERIAL | Obtain comparable bid/mid observations, trade sizes, benchmark yields and instrument terms. |
| Bond comparators differ in coupon, maturity, rating and potentially security/perimeter. | T4.2, T4.7 | Caesars, MGM, PENN bonds | Last-trade yields cannot be interpreted as normalized credit spreads. | MATERIAL | Compare matched maturity and seniority instruments with benchmark spreads and rating context. |
| Peer financials are Q2 2026; no later peer statements are supplied, while bond trades are dated October 1. | T4.2–T4.5, T4.8 | MGM, PENN | Financial comparisons may be stale relative to the analysis date; do not blend dates. | MATERIAL | Refresh peer financials when available and retain distinct financial and market dates. |
| CP-1 reports Caesars financials only through June 30, 2026; no later borrower financial data are supplied. | T4.2–T4.7, T4.10 | Caesars | Current borrower-versus-peer position and post-period changes cannot be verified. | MATERIAL | Obtain subsequent company reporting and a current debt/cash schedule before relying on current-condition conclusions. |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| MGM Q2 revenue | [C1] | MGM Resorts Q2 2026 earnings release | 3 |
| MGM Q2 Consolidated Adjusted EBITDA | [C2] | MGM Resorts Q2 2026 earnings release | 5 |
| MGM Q2 operating income | [C3] | MGM Resorts Q2 2026 earnings release | 4 |
| PENN Q2 revenue | [C4] | PENN Entertainment Q2 2026 earnings release | 3 |
| PENN Q2 Consolidated Adjusted EBITDA | [C5] | PENN Entertainment Q2 2026 earnings release | 2 |
| PENN capital expenditures | [C6] | PENN Entertainment Q2 2026 earnings release | 4 |
| PENN reported total liquidity and cash | [C7] | PENN Entertainment Q2 2026 earnings release | 1 |
| PENN bond last-trade yield | [C8] | FINRA lookup, CUSIP 707569AV1 | 1 |
| MGM bond last-trade yield | [C9] | FINRA lookup, CUSIP 552953CK5 | 1 |
| Caesars unsecured-note last-trade yield | [C10] | FINRA lookup, CUSIP 12769GAD2 | 1 |
| Caesars secured-note last-trade yield | [C11] | FINRA lookup, CUSIP 12769GAC4 | 1 |
| Fund-held Caesars secured-note position value at June 30 | [C14] | Federated Hermes Sustainable High Yield Bond Fund portfolio | 4 |
| Caesars operating and leverage baseline | [CP-1 C8, C10, C16, C17; CP-1 T4.4, T4.8, T4.9] | Accepted CP-1 canonical handoff; upstream citations and locators retained there | See upstream register |

## Source Registry

| Source | Period / observation | Provenance and use | Limitation |
|---|---|---|---|
| Accepted CP-0 and CP-1 handoffs | Q2 2026; analysis date 2026-10-02 | Matching issuer/run/period lineage; CP-1 supplies Caesars financial and leverage baseline | CP-0 and CP-1 are Restricted; CP-0 flags no post-Q2 financials and a source-limited pack. |
| MGM Resorts Q2 2026 earnings release | Quarter ended June 30, 2026 | Issuer-reported peer operating and financial data [C1, C2, C3] | Q2 issuer measures; no complete peer leverage, FCF or valuation dataset. |
| PENN Entertainment Q2 2026 earnings release | Quarter ended June 30, 2026 | Issuer-reported peer operating, capex and liquidity data [C4, C5, C6, C7] | Q2 issuer measures; no matched peer debt/FCF or valuation dataset. |
| FINRA fixed-income summaries | Observed 2026-10-02; last trades dated 2026-10-01 | Public regulatory last-trade summary for selected Caesars, MGM and PENN bonds [C8, C9, C10, C11] | Not bid, mid, ask or evaluated price; no spread, benchmark, trade size or intraday time. |
| Federated Hermes fund portfolio | June 30, 2026 | Third-party point-in-time holding and value for Caesars secured notes [C14] | Not a current quote and not directly comparable with October last trades. |

## Gaps & Conflicts

The source set supports a limited Q2 operating screen, not a fully normalized peer benchmark. The CP-1 Caesars values are accepted upstream financial measures; the MGM and PENN data are issuer-reported Q2 measures with distinct Adjusted EBITDA definitions and operating/lease perimeters. No reconciliation is available to resolve those differences, so margin comparisons remain directional and are not used for peer statistics. FINRA records last trades, not executable quotes; the October bond observations differ in maturity and instrument terms, while the fund’s Caesars position value is dated June 30. These are distinct measures and dates, not a price conflict. Material gaps and actions are itemized in T4.11; no implied EV or peer valuation range is calculated.

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity and upstream lineage | Self-checked | CP-0 and CP-1 accepted handoffs match issuer, run and Q2 2026 period; host-owned front matter retained. |
| Peer data gate | Complete with limitations | MGM and PENN have issuer-reported Q2 operating data; only dated bond summaries supplement them. |
| Peer universe and discovery | Restricted | Supplied-source discovery only; no external retrieval, broad verified universe or full 16-dimension assessment. |
| Metric alignment before statistics | Self-checked | AP1–AP11 recorded; definition and perimeter differences limit comparability. |
| Required registers | Self-checked | T4.1–T4.11 are present; conditional T4.D1 is included. |
| Peer statistics | Self-checked | No aggregate is presented where the comparable-data minimum is not met. |
| Outlier assessment | Self-checked | No supported outlier finding; the register preserves insufficient evidence rather than forcing a rank. |
| Valuation and transaction comps | Restricted | No sourced market caps, complete EVs, multiples or transaction values; implied EV remains null. |
| Confidence and QA | Restricted | Confidence 49/100, Low; E=72, C=68, S=0.70, P=0; score=(0.6×72+0.4×68)×0.70=49.28, rounded to 49. Material peer-data limitations cap QA at Restricted. |
| Host validation | Pending | Host validation follows this response; no host validation result is claimed. |