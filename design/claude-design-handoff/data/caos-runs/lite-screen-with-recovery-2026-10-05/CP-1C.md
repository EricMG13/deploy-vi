---
module_id: "CP-1C"
module_name: "PeerBenchmark"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_FULL_CREDIT_SCREEN"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1C-9286fbba6732a322"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_FULL_CREDIT_SCREEN-04-CP-1C"
credit_os_invocation_sha256: "2e9b3d99766caadb0a50191cf5ff549c5ef0c4c308cd5872fc97569f27f897d7"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "dcb45fd922bd40cf339a42308e91a3fac8f6e23b9f198f147d86c85f73a15eeb"
  - module_id: "CP-L10"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "1b3412810ea6d286e8dd1b78eaea47c62bfa80734d5ca52486c3d5933abc0d12"
confidence_score: 48
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "PEER_SET_SCREENING_ONLY", "NO_PUBLIC_WEB_DISCOVERY", "NO_TRADING_OR_TRANSACTION_MULTIPLES", "CP-1_CANONICAL_FINANCIALS_NOT_DELIVERED"]
validation_warnings: ["LITE_FULL_UPGRADE_REQUIRED", "PEER_STATISTICS_NOT_CALCULATED", "NO_TRADING_OR_TRANSACTION_COMPS", "HOST_VALIDATION_FOLLOWS"]
downstream_consumers: ["CP-2", "CP-3", "CP-5", "CP-5A"]
---

## Audit Summary

- **Canonical handoff:** `CZR_CP-1C_20261002.md`.
- **Run status:** Restricted; the LITE screening inputs support a bounded peer screen, not a completed FULL underwriting benchmark.
- **Identity and period:** Caesars Entertainment, Inc.; Q2 2026, quarter ended June 30, 2026. [C1]
- **Data gate:** Ready with limitations. The delivered set includes Caesars’ Q2 Form 10-Q and Q2 releases for PENN and MGM; peer data support directional operating comparisons but not a definition-aligned credit or valuation set. [C2, C5, C7]
- **Upstream boundary:** CP-0 is the accepted source-readiness anchor; CP-L10 is used only within its screening scope. No accepted CP-1 canonical-financial handoff was delivered, so no CP-1-owned normalization or leverage conclusion is asserted.
- **Confidence:** 48 — Low. Calibration: E=90, C=90, S=0.7, P=15; `(0.6 × 90 + 0.4 × 90) × 0.7 − 15 = 48`. The partial source gate, peer-definition gaps and unavailable valuation inputs constrain confidence.
- **Status implication:** Restricted under the LITE UPGRADE rule. A new, user-confirmed, linked `FULL_CREDIT_32` run is recommended to supply the FULL inputs; this run remains `LITE_CREDIT_22` and screening-only.

## Analysis

### Credit view

Caesars is directionally benchmarkable against PENN and MGM for Q2 operating context, but not for a conclusive credit ranking: only issuer results releases accompany the peer data, and the measures diverge in segment mix, geography, scale, lease treatment and Adjusted EBITDA definitions. Caesars reported revenue of $2,993m and Adjusted EBITDA of $920m; revenue grew 3.0% while EBITDA fell 3.7% year over year. [C2, C3, C4] PENN’s and MGM’s results provide breadth, not a reliable matched leverage, FCF or valuation comparison. [C5, C6, C7, C8, C9, C10] The immediate creditor signal is mixed earnings direction, with Las Vegas contraction partly offset by Regional growth; absent CP-1 canonical financials, fuller peer filings and dated market inputs prevent outlier, leverage and EV conclusions. [C13, C20] A further Las Vegas decline would reduce earnings available to service debt while leases, capex and debt service absorb cash; monitor segment EBITDA, cash generation and updated peer definitions. [C11, C12, C18, C21]

The snapshot compares reported Q2 values; it is descriptive, not a pooled peer statistic. Adjusted EBITDA definitions and scale differ materially, so the peer figures do not establish relative leverage or credit quality.

| Metric | Caesars | PENN | MGM | Credit reading |
|---|---:|---:|---:|---|
| Revenue, Q2 2026 (USD m) | 2,993 | 1,857.4 | 4,450.993 | Different scale; operating context only. [C2, C5, C7] |
| Adjusted EBITDA, Q2 2026 (USD m) | 920 | 312.6 | 610.387 | Definitions and lease treatment prevent direct ranking. [C3, C6, C8, C9, C10] |
| H1 2026 capital expenditure (USD m) | 335 | 192.0 | — | Partial cash-investment context; MGM value not delivered. [C12, C15] |

**Operating position and comparability.** Caesars’ consolidated revenue grew 3.0% year over year, but reported Q2 Adjusted EBITDA declined 3.7%. Within Caesars, Las Vegas Adjusted EBITDA margin fell to 40.3% from 44.5%, while Regional Adjusted EBITDA increased 11.2%. Those operating results transmit unevenly: Regional growth cushions the consolidated decline, but weaker Las Vegas visitation, hotel performance and table-game results reduce the earnings buffer available for debt service if they persist. [C4, C13, C20] The contrary evidence is meaningful: Regional growth is a current offset, and Caesars’ Q2 revenue increased; it would weigh more heavily if subsequent periods showed the Las Vegas decline stabilizing and Regional growth persisting without an equivalent decline elsewhere. [C2, C20]

PENN is a relevant operating-screen candidate because its supplied release describes a broad North American portfolio spanning casinos, racetracks and online gaming; MGM is a gaming and hospitality candidate with a global resort footprint. [C27, C16] Neither release provides a fully harmonized company-wide comparison with Caesars. Caesars expressly cautions that its Adjusted EBITDA may not be comparable to similarly titled industry measures; PENN’s Consolidated Adjusted EBITDA includes triple-net lease rent expense. That definition and lease-treatment divergence can distort margin, cash conversion and leverage comparisons, so no peer average or borrower rank is reported. [C9, C10]

**Cash flow, leverage and liquidity.** Caesars generated $675m of operating cash in H1 2026 versus $680m in H1 2025; property and equipment purchases were $335m versus $453m. These are reported cash-flow and investment figures, not a peer-aligned FCF measure. [C11, C12] The filing separately estimates $425m of debt service and $687m of VICI and GLPI lease payments for the remainder of 2026. If Las Vegas earnings weaken further before operating cash generation improves, the first transmission is less cash available after recurring investment and fixed cash uses, followed by tighter liquidity and refinancing flexibility. Monitor segment EBITDA, operating cash flow, capex, debt-service funding and lease payments; no unsupported downside amount is modeled. [C18, C21]

Reported liquidity components are not treated as interchangeable. Caesars reports cash and $1.9bn of available CEI revolver borrowing capacity; PENN reports $1.9bn total liquidity including $887.2m cash; MGM’s supplied balance sheet reports $2,547.4m cash but does not provide a matching total-liquidity measure in the delivered excerpt. Different disclosure scope prevents a like-for-like liquidity ranking. [C23, C24, C25]

**Valuation context and event boundary.** No dated market capitalization, public EV multiple or peer transaction multiple is available in the delivered evidence; implied EV is therefore not calculated. The Q2 filing reports shares outstanding, but no corresponding dated share price is supplied here. [C19] Separately, Caesars disclosed an Alberta mobile sports betting and iGaming launch on July 13, 2026. This post-period event is flagged as subsequent information and is not blended into Q2 results. [C17]

The strongest counterargument to a cautious relative-credit view is the combination of Caesars’ reported revenue growth and Regional EBITDA growth, alongside positive H1 operating cash flow. Those factors would gain weight if later comparable periods confirmed sustained improvement and documented debt-service capacity after leases and capital needs. They do not cure the present gaps in CP-1 canonical financials, comparable peer data, current market inputs or a forward cash-flow bridge; implementation should remain screening-only, with monitoring focused on segment performance, cash generation and data freshness.

### Analytical appendix — complete canonical registers

#### T4.1 — Peer Universe Register

| Entity Name | Peer Category Label | Source of Selection | Dimensions Assessed | Strengths | Limitations | Data Availability | Evidence Quality Tier | Usable For | Exclusion Reason |
|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Borrower/Issuer | Q2 2026 Form 10-Q; issuer profile [C1, C28] | Screened across 16 dimensions; 8 assessable from supplied filing and release: products, revenue model, end markets, geography, customer type, capital structure, public status and provenance | Direct Q2 operating, cash-flow and debt disclosures; segment detail | Unaudited interim period; purchases affect comparability; no accepted CP-1 canonical financials | Q2 2026 filing; official Q2 release; operating and cash-flow data available | Primary-Verified / Secondary-Reputable | Borrower anchor; reported operating trends and limited cash-flow context | Not excluded; CP-1 normalization, peer credit comparisons and valuation remain unavailable |
| PENN Entertainment, Inc. | Direct Operating Peer | Delivered PENN Q2 2026 results release; public-company candidate [C5, C27] | 6/16 screening dimensions: product/service, revenue model, end market, geography, public status and source provenance | Casino, racetrack and digital operations; Q2 and H1 reported revenue and Adjusted EBITDA; H1 capex | Issuer release only; adjusted metric and lease treatment differ; no matched full credit data | Q2/H1 release tables available; cash-flow and complete leverage inputs not delivered | Public Sources — official issuer release | Directional operating comparison; not a leverage or valuation comp | Not excluded from screening; excluded from statistics and direct EBITDA ranking for definition and coverage gaps |
| MGM Resorts International | Sector Peer | Delivered MGM Q2 2026 results release; public-company candidate [C7, C16] | 6/16 screening dimensions: product/service, revenue model, end market, geography, public status and source provenance | Q2 company-wide revenue and Adjusted EBITDA; segment and cash disclosures | Global and segment perimeter differs; peer release definitions and lease treatment are not harmonized; no matched full credit data | Q2 results and selected balance-sheet data available; peer cash flow/capex and comparable leverage are incomplete | Public Sources — official issuer release | Directional sector and operating context; not a direct credit or valuation comp | Not excluded from screening; excluded from statistics and direct EBITDA ranking for definition and coverage gaps |

#### T4.2 — Metric Alignment Register

| Metric | Borrower Value | Borrower Period | Peer Entity | Peer Value | Peer Period | AP1-AP11 | Comparability Status | Limitation Notes |
|---|---:|---|---|---:|---|---|---|---|
| Revenue | $2,993m | Q2 2026, three months | PENN | $1,857.4m | Q2 2026, three months | AP1: reported net revenue; AP2: reported total revenue; AP3: same quarter end; AP4: USD; AP5: US GAAP; AP6: actual; AP7: reported; AP8: quarterly; AP9: official issuer release/filing; AP10: no normalization; AP11: limited by scale/perimeter | Comparable with Limitations | Values are reported, not normalized for scale or segment mix. Source values [C2, C5]. |
| Revenue | $2,993m | Q2 2026, three months | MGM | $4,450.993m | Q2 2026, three months | AP1: reported net revenue; AP2: reported consolidated revenue; AP3: same quarter end; AP4: USD; AP5: US GAAP; AP6: actual; AP7: reported; AP8: quarterly; AP9: official issuer release; AP10: no normalization; AP11: limited by geography/perimeter | Comparable with Limitations | MGM’s global operating footprint and different consolidation mix limit inference from the scale comparison. Source values [C2, C7, C16]. |
| Adjusted EBITDA | $920m | Q2 2026, three months | PENN | $312.6m | Q2 2026, three months | AP1: Caesars Adjusted EBITDA; AP2: PENN Consolidated Adjusted EBITDA; AP3: same quarter end; AP4: USD; AP5: US GAAP source with non-GAAP metric; AP6: actual; AP7: adjusted; AP8: quarterly; AP9: official issuer sources; AP10: definitions not reconciled; AP11: non-comparable | Not Comparable | Caesars warns similarly titled EBITDA may not be comparable; PENN’s measure includes triple-net lease rent expense. [C3, C6, C9, C10] |
| Adjusted EBITDA | $920m | Q2 2026, three months | MGM | $610.387m | Q2 2026, three months | AP1: Caesars Adjusted EBITDA; AP2: MGM Consolidated Adjusted EBITDA; AP3: same quarter end; AP4: USD; AP5: US GAAP source with non-GAAP metric; AP6: actual; AP7: adjusted; AP8: quarterly; AP9: official issuer sources; AP10: definitions/perimeter not reconciled; AP11: non-comparable | Not Comparable | MGM’s consolidated and segment perimeter and adjustment basis are not bridged to Caesars’ definition. [C3, C8, C9] |
| FCF / FCF conversion | Not Calculable from Provided Materials — no common peer FCF definition and peer operating cash-flow inputs are incomplete | H1 2026 | PENN | — | H1 2026 | AP1: not established; AP2: not established; AP3: H1 periods; AP4: USD; AP5: US GAAP source; AP6: actual; AP7: adjusted basis unresolved; AP8: six months; AP9: issuer releases; AP10: no matched CFO/FCF normalization; AP11: unavailable | Insufficient Information | PENN capex is available, but matched peer CFO and a common FCF definition are not. [C11, C12, C15] |
| FCF / FCF conversion | Not Calculable from Provided Materials — no common peer FCF definition and peer operating cash-flow inputs are incomplete | H1 2026 | MGM | — | H1 2026 | AP1: not established; AP2: not established; AP3: H1 periods; AP4: USD; AP5: US GAAP source; AP6: actual; AP7: adjusted basis unresolved; AP8: six months; AP9: issuer release; AP10: no matched CFO/FCF normalization; AP11: unavailable | Insufficient Information | Matched peer operating cash-flow and capex inputs are not supplied in the delivered excerpt. |
| Total/net/senior secured leverage | Not Calculable from Provided Materials — accepted CP-1 canonical financials and aligned definitions are not delivered | Q2 2026 | PENN | — | Q2 2026 | AP1: CP-1 definition unavailable; AP2: peer basis not matched; AP3: periods not fully aligned; AP4: USD; AP5: US GAAP source; AP6: actual; AP7: reported/adjusted basis unresolved; AP8: period basis unresolved; AP9: release-level evidence; AP10: no reconciliation; AP11: insufficient | Insufficient Information | No leverage comparison, ranking or covenant inference is made. |
| Total/net/senior secured leverage | Not Calculable from Provided Materials — accepted CP-1 canonical financials and aligned definitions are not delivered | Q2 2026 | MGM | — | Q2 2026 | AP1: CP-1 definition unavailable; AP2: peer basis not matched; AP3: periods not fully aligned; AP4: USD; AP5: US GAAP source; AP6: actual; AP7: reported/adjusted basis unresolved; AP8: period basis unresolved; AP9: release-level evidence; AP10: no reconciliation; AP11: insufficient | Insufficient Information | MGM debt and lease perimeter is not reconciled to a Caesars CP-1 basis. |

#### T4.3 — Operating Benchmark

| Entity | Revenue | Rev Growth | Gross Margin | EBITDA | EBITDA Margin | EBIT Margin | Period | Currency | Calc Status | Comp Status |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| Caesars Entertainment, Inc. | $2,993m | 3.0% reported | — | $920m Adjusted EBITDA | 30.7% reported | — | Q2 2026, three months | USD | Reported | Comparable with Limitations |
| PENN Entertainment, Inc. | $1,857.4m | — | — | $312.6m Consolidated Adjusted EBITDA | — | — | Q2 2026, three months | USD | Reported | Not Comparable for EBITDA; revenue Comparable with Limitations |
| MGM Resorts International | $4,450.993m | 1.0% reported | — | $610.387m Consolidated Adjusted EBITDA | — | — | Q2 2026, three months | USD | Reported | Not Comparable for EBITDA; revenue Comparable with Limitations |

#### T4.4 — Cash Flow & Cap Intensity

| Entity | FCF | FCF Conversion | Capex/Rev | Capex/EBITDA | WC/Rev | Period | Currency | Calc Status | Comp Status |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| Caesars Entertainment, Inc. | —; no common FCF definition adopted | — | 5.7% | 18.5% | — | H1 2026 | USD | Derived — capex ratios use reported capex divided by reported revenue/Adjusted EBITDA; FCF not calculated | Comparable with Limitations |
| PENN Entertainment, Inc. | —; matched CFO not supplied | — | 5.3% | 33.2% | — | H1 2026 | USD | Derived — capex ratios use reported capex divided by reported revenue/Adjusted EBITDA; FCF not calculated | Comparable with Limitations for capex/revenue; Not Comparable for capex/EBITDA |
| MGM Resorts International | — | — | — | — | — | H1 2026 | USD | Insufficient Information | Insufficient Information |

#### T4.5 — Credit Metric Benchmark

| Entity | Total/Net/Sr Sec Leverage | Int Coverage | Adj Int Coverage | FFO/Debt | Liquidity | Period | Currency | Calc Status | Comp Status |
|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | — / — / — | — | — | — | Cash $965m; CEI revolver available capacity $1.9bn, separately reported | June 30, 2026 | USD | Insufficient Information | Insufficient Information |
| PENN Entertainment, Inc. | — / — / — | — | — | — | Total liquidity $1.9bn, including $887.2m cash | June 30, 2026 | USD | Insufficient Information | Insufficient Information |
| MGM Resorts International | — / — / — | — | — | — | Cash $2,547.4m only; total liquidity not established | June 30, 2026 | USD | Insufficient Information | Insufficient Information |

#### T4.6 — Summary Statistics

| Metric | Borrower Value | Peer Avg | Median | Min | Max | Q1 | Q3 | N | Borrower Position |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Q2 revenue (USD m) | $2,993 | — | — | — | — | — | — | 0 eligible for aggregate statistics; 2 candidates assessed | Not Ranked — candidate set and definitions are insufficient for a defensible peer statistic |
| Q2 Adjusted EBITDA (USD m) | $920 | — | — | — | — | — | — | 0 eligible comparable peers | Not Ranked — adjusted definitions are not reconciled |
| H1 capex / revenue | 5.7% | — | — | — | — | — | — | 0 eligible for aggregate statistics | Not Ranked — limited peer coverage and definition alignment |

#### T4.7 — Outlier Register

| Entity | Metric | Value | Peer Range (Min/Max/Med/Avg) | Deviation | Direction | Operating Impl | CF Impl | Lev/Liq Impl | Refi Impl | Valuation Impl | Downstream Handoff |
|---|---|---|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Q2 2026 Adjusted EBITDA year-over-year change | $920m; reported change (3.7)% | —; no eligible comparable range | Not calculable against aligned peer range; borrower declined year over year | Insufficient Information | Las Vegas margin and EBITDA declined; Regional EBITDA growth partly offsets. [C13, C20] | H1 CFO and capex are disclosed, but peer-aligned FCF is not established. [C11, C12] | No aligned leverage or coverage comparison | Fixed cash uses mean sustained earnings weakness could reduce flexibility; no refinancing conclusion is quantified. [C18, C21] | No dated public multiples; no valuation inference | CP-2: monitor operating/cash-flow durability; CP-3: no relative-value conclusion pending dated market and aligned credit data |

#### T4.8 — Public Trading Comps

| Entity | Mkt Cap | Mkt Cap Date | EV | EV/Rev | EV/EBITDA | Period Used | Metric Def | Comp Status | Source |
|---|---:|---|---:|---:|---:|---|---|---|---|
| Caesars Entertainment, Inc. | — | — | — | — | — | Q2 2026 reported financial period; no market date | Market capitalization and EV inputs not supplied | Insufficient Information | Q2 2026 Form 10-Q; shares outstanding reported, no matching dated share price [C19] |
| PENN Entertainment, Inc. | — | — | — | — | — | Q2 2026 reported financial period; no market date | Market capitalization and EV inputs not supplied | Insufficient Information | Q2 2026 results release; no dated market-price source delivered |
| MGM Resorts International | — | — | — | — | — | Q2 2026 reported financial period; no market date | Market capitalization and EV inputs not supplied | Insufficient Information | Q2 2026 results release; no dated market-price source delivered |

#### T4.9 — Transaction Comps

| Txn Name | Date | Type | Buyer/Seller | TV | TV/Rev | TV/EBITDA | Period Used | Metric Def | Comp Status | Source |
|---|---|---|---|---:|---:|---:|---|---|---|---|
| No peer transaction comparable in delivered evidence | — | — | — | — | — | — | — | No transaction multiple or contemporaneous denominator supplied | Insufficient Information | No transaction-comparable source delivered; Caesars’ pending merger is not treated as a peer transaction multiple |

#### T4.10 — Implied EV

| Method | Multiple Source | Multiple Value | Borrower Metric | Period | Implied EV | Low | Median | High | Calc Status | Limitations |
|---|---|---:|---|---|---:|---:|---:|---:|---|---|
| EV/EBITDA | No qualified trading multiple supplied | — | $920m reported Adjusted EBITDA; Q2 denominator is not TTM | Q2 2026, three months | — | — | — | — | Insufficient Information | No dated public EV multiple and no aligned peer multiple; indicative context only, not recovery value |
| EV/Revenue | No qualified trading multiple supplied | — | $2,993m reported revenue; Q2 denominator is not TTM | Q2 2026, three months | — | — | — | — | Insufficient Information | No dated public EV multiple; indicative context only, not recovery value |
| Transaction EV/EBITDA | No transaction multiple supplied | — | $920m reported Adjusted EBITDA; Q2 denominator is not contemporaneous TTM | Q2 2026, three months | — | — | — | — | Insufficient Information | No peer transaction or contemporaneous transaction denominator supplied |
| Transaction EV/Revenue | No transaction multiple supplied | — | $2,993m reported revenue; Q2 denominator is not contemporaneous TTM | Q2 2026, three months | — | — | — | — | Insufficient Information | No peer transaction or contemporaneous transaction denominator supplied |

#### T4.11 — Gaps & Limitations

| Gap | Affected Metric/Section | Affected Peer(s) | Downstream Impact | Severity | Action |
|---|---|---|---|---|---|
| No accepted CP-1 canonical financial handoff in this route input set | Borrower definition inheritance; T4.2; T4.5; T4.6 | Caesars | No canonical CP-1 leverage, coverage or normalized financial comparison; no inference from memory or from screening summaries | High | In the linked FULL_CREDIT_32 run, obtain accepted CP-1 financials and rerun dependent comparisons |
| Peer input coverage is limited to supplied Q2 issuer releases | T4.1–T4.7 | PENN; MGM | Directional operating context only; cash flow, debt, coverage and full-period comparison remain incomplete | High | Supply primary peer filings and supporting schedules for matched periods and perimeters |
| Adjusted EBITDA definitions and lease treatment differ | T4.2–T4.7 | Caesars; PENN; MGM | EBITDA margin, FCF conversion and leverage ranking could be misleading; no aggregate statistics used | High | Reconcile each definition and lease basis before benchmarking; preserve remaining non-comparability |
| Asset purchases affect Caesars period comparability | T4.2–T4.4 | Caesars; all peers | Period comparisons may reflect perimeter changes as well as underlying performance | Material | Use full-period issuer disclosure and a consistent perimeter; the filing cautions periods after purchases are not fully comparable. [C26] |
| Peer cash-flow and capital-intensity data are incomplete | T4.4; T4.6 | MGM; PENN | No peer FCF, FCF conversion, working-capital or robust capex statistic | High | Obtain peer cash-flow statements and aligned capital expenditure definitions |
| Comparable leverage, interest coverage and FFO/debt inputs are absent or not aligned | T4.5; T4.6; T4.7 | PENN; MGM; Caesars | No borrower position, debt-service ranking or refinancing inference | High | Obtain CP-1 canonical borrower metrics and current peer debt/interest definitions |
| No dated market capitalization, EV multiples or transaction-comparable set is supplied | T4.8–T4.10 | Caesars; PENN; MGM | No public trading comparison, implied EV range or valuation-support conclusion | High | Supply dated market observations and qualified transaction evidence; align periods, currencies and definitions |
| Web discovery could not be performed from the delivered evidence | T4.D1; T4.1 | Additional candidate peers | Universe may omit more comparable operators; two supplied release candidates do not establish a complete peer set | Material | Perform reputable-source discovery and verify candidates and financials in the linked FULL run |
| Subsequent event must remain separate from Q2 values | Analysis; period alignment | Caesars | July 13, 2026 Alberta launch is not part of Q2 results | Minor | Retain the event date and update only from supplied subsequent reporting. [C17] |

#### T4.D1 — Peer Discovery Source Register

| Candidate | Query / Source | URL or Source Locator | Retrieval Date | Dimensions Assessed | Promotion Decision | Evidence Tag | Limitation |
|---|---|---|---|---|---|---|---|
| PENN Entertainment, Inc. | Delivered Q2 2026 results release; gaming, hospitality and digital operating candidate [C27] | Source 463cb989-77ee-42f5-994d-606ea0f8b347, pp. 1–5 | No retrieval performed; source provided in run | At least 3 screening dimensions: product/service, revenue model, geography, public status, provenance; other dimensions not verified | Retained as a source-provided screening candidate; not promoted through web discovery | Official issuer release; not Web-Scraped | No peer list was supplied and public-web retrieval is unavailable here; release-level data do not establish full comparability |
| MGM Resorts International | Delivered Q2 2026 results release; gaming and hospitality operating candidate [C16] | Source b1d0e082-2cc6-4dc4-9544-5e758dd0e5e0, pp. 1–6 | No retrieval performed; source provided in run | At least 3 screening dimensions: product/service, revenue model, geography, public status, provenance; other dimensions not verified | Retained as a source-provided screening candidate; not promoted through web discovery | Official issuer release; not Web-Scraped | Global portfolio, segment mix and incomplete matched financial data limit comparison; no web discovery was performed |

## Evidence Trace

| Claim / register support | Citation | Document | Page |
|---|---|---|---:|
| Reporting period; borrower revenue and Adjusted EBITDA | [C1, C2, C3] | Caesars Form 10-Q | 1, 2, 16 |
| Caesars Q2 Adjusted EBITDA year-over-year change | [C4] | Caesars Q2 2026 results release | 1 |
| PENN Q2 revenue and Consolidated Adjusted EBITDA | [C5, C6] | PENN Q2 2026 results release | 2 |
| MGM Q2 revenue and Consolidated Adjusted EBITDA | [C7, C8] | MGM Q2 2026 results release | 3, 5 |
| Adjusted EBITDA definition caveat and PENN lease treatment | [C9, C10] | Caesars Form 10-Q; PENN Q2 2026 results release | 16; 4 |
| H1 operating cash flow and property/equipment purchases | [C11, C12] | Caesars Form 10-Q | 4 |
| PENN H1 capex; MGM/PENN business profiles | [C15, C16, C27] | PENN and MGM Q2 2026 results releases | 4–5; 3 |
| Caesars borrower profile; asset-purchase comparability | [C28, C26] | Caesars Form 10-Q | 17; 6 |
| Las Vegas margin contraction and Regional EBITDA growth | [C13, C20, C22] | Caesars Form 10-Q | 20; 20; 18 |
| Annual filing referenced by the Q2 report | [C14] | Caesars Form 10-Q | 5 |
| Subsequent Alberta launch; lease payments and debt service | [C17, C18, C21] | Caesars Form 10-Q | 17; 22; 9 |
| Liquidity components for Caesars, PENN and MGM | [C23, C24, C25] | MGM results release; PENN results release; Caesars Form 10-Q | 4; 1; 10 |
| Shares outstanding disclosed without a dated market price in the supplied evidence | [C19] | Caesars Form 10-Q | 1 |

## Source Registry

| Source ID | Source | Period / locator | Use and limitation |
|---|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Caesars Entertainment, Inc. Form 10-Q | Quarter ended June 30, 2026; pp. 1–26 | Primary interim source for reported borrower financials, segments, cash flow, debt and liquidity; unaudited and refers to the 2025 Form 10-K. [C1, C14] |
| 4edecdd2-6ed8-429e-902c-eb92822cd767 | Caesars Entertainment, Inc. Q2 2026 results release | Q2 2026; pp. 1–4 | Supplemental issuer-reported revenue, EBITDA change, debt and liquidity; non-GAAP definitions remain issuer-specific. [C4] |
| 463cb989-77ee-42f5-994d-606ea0f8b347 | PENN Entertainment, Inc. Q2 2026 results release | Three and six months ended June 30, 2026; pp. 1–5 | Peer revenue, Adjusted EBITDA and H1 capex; official issuer release, not a full matched peer underwriting set. [C5, C6, C15] |
| b1d0e082-2cc6-4dc4-9544-5e758dd0e5e0 | MGM Resorts International Q2 2026 results release and schedules | Quarter ended June 30, 2026; pp. 1–6 in delivered evidence | Peer revenue, Adjusted EBITDA and cash balance; global perimeter and incomplete cash-flow/capex evidence limit comparability. [C7, C8, C23] |

## Gaps & Conflicts

The benchmark is restricted by the absence of accepted CP-1 canonical financials, the limited release-level peer set, unbridged Adjusted EBITDA and lease definitions, incomplete peer cash-flow and debt metrics, and no dated trading or transaction multiples. The Q2 filing points readers to the 2025 Form 10-K, which is not included in the delivered evidence. [C14] No statistics were calculated from non-comparable or insufficiently covered observations, and no implied EV was presented.

The central analytical tension is that Caesars’ revenue increased and Regional EBITDA grew while Las Vegas EBITDA and margin weakened. These facts are not reconciled into a single peer rank: Regional growth is a genuine offset, but the periods and adjusted measures do not establish relative creditor strength. [C2, C13, C20]

Subsequent event: Caesars reported an Alberta mobile sports betting and iGaming launch on July 13, 2026, after the June 30 reporting date. It is date-labelled and excluded from Q2 figures. [C17]

No CP-DR research brief or research-adoption rows were delivered with this module; unresolved evidence questions are recorded in T4.11 and no research request is made. The recommended next step is a user-confirmed, linked `FULL_CREDIT_32` run with CP-1 canonical financials, current peer filings, matched credit/cash-flow definitions and dated valuation inputs.

## QA Validation

| Check | Result | Record |
|---|---|---|
| Identity, front matter and filename | Self-check complete | Host-owned identity and lineage copied as supplied; canonical filename is `CZR_CP-1C_20261002.md`. |
| Required headings and reading order | Self-check complete | Six H2 headings appear once and in required order; Analysis opens with `### Credit view` and a conclusion-first view before any table. |
| LITE scope and dependency boundary | Restricted | Screening inputs used without claiming CP-1 canonical metrics; absent FULL inputs are limitations, not inferred values or a stop. |
| Peer discovery and source provenance | Restricted | No web retrieval was available; T4.D1 records supplied candidates without labeling them Web-Scraped. |
| Required registers and columns | Self-check complete | T4.1–T4.11 and conditional T4.D1 are present with the required columns and at least one body row each. |
| Comparability and statistics | Restricted | Comparability is assigned before summaries; no peer aggregate or borrower rank is reported where the evidence is insufficient. |
| Outliers and valuation | Restricted | No outlier is asserted without an eligible peer range; public and transaction multiples and implied EV remain unavailable. |
| Confidence calibration | Self-check complete | E=90, C=90, S=0.7, P=15; score 48, band Low; Restricted is consistent with the source limitations and LITE UPGRADE requirement. |
| Citations and source trace | Self-check complete | Citation markers refer to the delivered evidence and are mapped in Evidence Trace; no upstream citation-register entries are cited as evidence. |
| Host validation and completeness check | Not run here | Host vendor validation and register-completeness checks follow this answer; no host result, exit status or finding is claimed. |