---
module_id: "CP-1B"
module_name: "EarningsDelta"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "EARNINGS_UPDATE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1B-71d30636ca958120"
credit_os_route_node_id: "RN-FULL_CREDIT_32-EARNINGS_UPDATE-03-CP-1B"
credit_os_invocation_sha256: "9ebf99c3a3539d784d426a2a4e304e5118f44a2a3309410c264a83c8827d3355"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "391239d01ae8de0a192795066295a2f1d36f6c68d683de2a4deb87dac9933ddd"
  - module_id: "CP-1"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "ea255e9e1079d8ca891fe6bddc3797a6b2c6f7acb9652d0bbc4c1ad0af39baad"
confidence_score: 56
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, SCRIPT_OWNED_CALCULATIONS_NOT_EXECUTED, DERIVED_KPI_GAPS, MODEL_INTERFACE_BLOCKED]
validation_warnings: [MATERIAL_DATA_GAPS_RECORDED, UPSTREAM_RESTRICTED, MODEL_READINESS_BLOCKED, HOST_VALIDATION_FOLLOWS]
downstream_consumers: [CP-2, CP-2A, CP-MODEL, CP-5, CP-5A]
---

## Audit Summary

- **Canonical filename:** `CZR_CP-1B_20261002.md`.
- **Entity and period:** Caesars Entertainment, Inc., consolidated; three and six months ended June 30, 2026, compared with the corresponding 2025 periods; USD millions; US GAAP. Interim statements are unaudited.
- **Status:** Restricted; the source set supports material operating and earnings comparisons, but canonical EBITDA leverage, FCF, several cash KPIs and model checks cannot be completed from the inherited handoff and available calculations.
- **Confidence:** 56 / Low. Material definition, calculation, perimeter and downstream model limitations remain.
- **Committee status:** Requires More Work. No instrument recommendation is made.
- **Source gate:** Primary interim and audited annual filings plus an issuer release are available; no approved base case or management guidance benchmark is provided. The CP-0 and CP-1 handoffs are both Restricted.
- **Next action:** Complete the governed CP-1 calculations and reconciliations, obtain the missing underwriting and benchmark inputs, then reassess CP-MODEL readiness.

## Analysis

### Credit view

Q2 revenue increased 3.0% year over year to $2,993 million, but issuer-reported Adjusted EBITDA fell to $920 million from $955 million and its margin contracted to 30.7% from 32.9% [C1, C2, C3]. The mixed growth/earnings result reduces the operating cushion available for debt service: Las Vegas weakness and lower Digital EBITDA outweighed Regional growth, which was partly related to the Caesars Windsor consolidation [C5, C6, C7]. The counterweight is $675 million of H1 operating cash flow and stronger Regional earnings; it would improve the credit read-through if sustained on a comparable perimeter and after capital spending, rent and debt service [C6, C9, C10, C18, C19]. Adjusted EBITDA is not cash flow. Because CP-1’s retained handoff does not provide a complete canonical EBITDA/FCF calculation set and script-owned comparisons were not executed here, leverage, FCF conversion and covenant headroom are not inferred.

**Key supported changes.** Revenue grew while Adjusted EBITDA declined; the margin signal is adverse. Segment comparisons show a Las Vegas contraction and a Regional increase with a stated perimeter/event contribution. These movements are evidence of differing property and channel trajectories, not a consolidated forecast.

**Earnings change summary**

| Measure | Q2 2025 | Q2 2026 | Reported change | Creditor read-through |
|---|---:|---:|---:|---|
| Revenue | $2,907m | $2,993m | +3.0% | Growth did not translate into Adjusted EBITDA growth [C8] |
| Adjusted EBITDA | $955m | $920m | (3.7)% | Smaller operating earnings cushion [C2] |
| Adjusted EBITDA margin | 32.9% | 30.7% | Lower | Margin compression weakens debt-service resilience [C3] |
| Operating cash flow, H1 | $680m | $675m | — | Slightly lower reported H1 cash generation; no Q2 CFO split [C9] |
| Cash and equivalents | $887m* | $965m* | — | Balance-sheet-date liquidity; restricted cash excluded [C13] |

*Balance-sheet comparison is June 30, 2026 versus December 31, 2025, not a same-quarter earnings comparison. Changes not printed by management are not hand-calculated here.

**Risk and monitoring view.** The initiating downside is weaker leisure visitation, hotel occupancy/rates, gaming volume or hold. The first operational break is lower property revenue or gaming win; higher labor, gaming taxes, marketing, maintenance and contractual rent constrain the offset. Continued EBITDA and cash conversion pressure would reduce liquidity and refinancing flexibility before a covenant breach can be assessed. Monitor Las Vegas visitation, occupancy and margin; Digital hold, promotions and EBITDA; Regional results on a Windsor-consistent basis; cash flow after capex and lease payments; and the filing of current covenant calculations. No stress number or covenant capacity is inferred.

**Contrary evidence and confidence.** Regional Adjusted EBITDA rose, while Las Vegas and Digital declined; the issuer attributes part of the Regional gain to Windsor, northern Nevada event visitation and recent investments [C6, C7]. The $675 million H1 CFO is another counterweight [C9]. That evidence would win if later reported periods demonstrate durable, comparable growth and cash generation after capex and rent. Until then, Windsor and event effects limit confidence in treating Regional growth as a recurring offset.

**Definition, normalization and comparability.** CP-1 remains numeric authority. Issuer-reported Adjusted EBITDA is presented separately from canonical EBITDA and any credit-agreement EBITDA; the issuer says its measure is not a liquidity measure and may differ from debt-agreement definitions. No analyst normalization is applied to CP-1 figures. Transaction costs and other adjustments remain in their reported source and reconciliation roles; the distinct Q2/H1 figures are preserved in the conflict register. Caesars Windsor moved into Regional reporting on March 3, 2026, so the affected segment comparison is not fully like-for-like [C22].

**Subsequent event.** The 10-Q reports Alberta mobile sports betting and iGaming launched July 13, 2026, after the June 30 period end. It is flagged separately and excluded from Q2/H1 figures [C25]. The source set does not establish its financial contribution.

### Analytical appendix — complete canonical registers

#### T4.1 — Source Classification Register

| Source File Name | Document Type | Period Coverage | Evidence Quality Tier | Analytical Use | Limitations |
|---|---|---|---|---|---|
| CZR_Q2_2026_10Q.txt | Form 10-Q; unaudited interim filing | Q2 and H1 ended June 30, 2026; comparative 2025 | Primary-Unverified | Primary statements, segment operating data, cash flow, debt, liquidity, covenant and event disclosures | Host-prepared text representation; referenced map is not represented; full executed financing documents and amendments are not included in the delivered pack |
| CZR_FY2025_10K.txt | Form 10-K; audited annual filing | FY2025 and comparative annual periods | Primary-Unverified; audited financial statements | Annual baseline and issuer-specific Adjusted EBITDA add-back comparison | Annual periods do not supply missing discrete interim quarters; referenced stock-performance graph is not represented |
| CZR_Q2_2026_Earnings_Release.txt | Issuer earnings release | Q2 and H1 ended June 30, 2026; comparative 2025 | Secondary-Unverified; issuer release | Corroborates headline Q2 earnings and segment results | Supplemental and non-GAAP measures; 10-Q controls detailed financial analysis |

#### T4.2 — Definition Inheritance

| Metric Name | CP-1 Definition | CP-1 Formula | EBITDA Def in Use | Inheritance Status | Conflict Note |
|---|---|---|---|---|---|
| Revenue | CP-1 reported consolidated revenue | Inherited from CP-1; no transformation | Not applicable | Inherited | No period or currency conflict identified |
| EBITDA | CP-1 canonical EBITDA | No metric-level formula retained in the CP-1 handoff | Not confirmed | Partial; do not substitute Adjusted EBITDA | CP-1 distinguishes canonical EBITDA from issuer Adjusted EBITDA; canonical leverage is not calculated |
| Adjusted EBITDA | CP-1 issuer-reported Adjusted EBITDA kept distinct from canonical EBITDA | Source reconciliation to net loss; issuer-defined | Issuer-reported Adjusted EBITDA for performance comparisons only | Inherited with limitation | Not established as the debt-agreement definition or a liquidity measure |
| Adjusted EBITDA margin | Issuer-reported Adjusted EBITDA divided by revenue, as reported | Issuer-reported ratio; no recalculation | Issuer-reported Adjusted EBITDA | Inherited/source-reported | Do not present as cash margin or canonical EBITDA margin |
| Total debt | CP-1 carrying-value basis: current portion plus long-term debt carrying value | Current portion + long-term carrying value, net of disclosed financing costs | Not applicable | Inherited; CP-1 numeric authority retained | Debt-note face/book totals are distinct from carrying value; see CF-1 |
| Net debt and leverage | CP-1 canonical debt less cash and equivalents; leverage uses matched canonical EBITDA | CP-1 canonical formulas; matched EBITDA is not available here | Not confirmed | Partial | Do not substitute issuer Adjusted EBITDA or gross principal |
| CFO, FCF and FCF conversion | CP-1 cash-flow definitions and classifications | CP-1 normalized cash figures; FCF/KPI outputs not populated in the retained handoff | Not applicable | Partial | Q2 cash interest/taxes and quarterly CFO are not disclosed as discrete values in the delivered statements |
| Liquidity and coverage KPIs | CP-1 period, perimeter and denominator definitions | CP-1 formulas; no complete matched-period KPI set retained | Not confirmed | Partial | Cash, debt service and revolver capacity remain separate reported measures; no covenant headroom inferred |

#### T4.3 — Summary / Top-Sheet

| Row Label | Value / Observation |
|---|---|
| Issuer | Caesars Entertainment, Inc.; consolidated perimeter |
| Period(s) | Q2 and H1 2026 vs same 2025 periods; June 30, 2026 balance-sheet date |
| EBITDA Def | Issuer-reported Adjusted EBITDA for the earnings comparison; not confirmed as covenant EBITDA |
| Revenue | Q2 $2,993m vs $2,907m; reported growth 3.0% |
| EBITDA | Adjusted EBITDA $920m vs $955m; reported decline 3.7% |
| EBITDA Margin | Issuer-reported Adjusted EBITDA margin 30.7% vs 32.9% |
| FCF | No CP-1 canonical FCF value retained; not calculated in this run |
| Total / Net Leverage | Not calculated on the CP-1 canonical EBITDA basis |
| Cash Interest Coverage | Not calculated; Q2 cash interest and matched canonical EBITDA are not available as period inputs |
| Liquidity | June 30 cash and equivalents $965m; reported aggregate cash and borrowing-capacity summary $2,928m; not a headroom calculation |
| Key YoY Variance | Revenue up; Adjusted EBITDA and margin down. Las Vegas declined; Regional increased with a stated Windsor/event contribution |
| Key Credit Observation | Earnings cushion weakened despite revenue growth; treat Regional offset as less comparable and monitor cash generation after capex, rent and debt service |

#### T4.4 — Financial Performance Table

USD millions except margins. YoY change cells are `—` where a script-owned calculation was not executed or a source-provided comparison is not available; `—` is not zero.

| Line Item | Q2 2026 | Q2 2025 | H1 2026 | H1 2025 | YoY Change (Abs) | YoY Change (%) | Analyst Note |
|---|---:|---:|---:|---:|---:|---:|---|
| Revenue | 2,993 | 2,907 | 5,863 | 5,701 | — | — | Management reports +3.0% Q2 and +2.8% H1; no change recalculated here |
| COGS | — | — | — | — | — | — | Not separately presented as a consolidated canonical line |
| Gross Profit | — | — | — | — | — | — | Not separately presented; no imputation |
| Gross Margin | — | — | — | — | — | — | Not calculable from a reported gross-profit basis |
| SG&A / General and administrative | 521 | 477 | 1,025 | 960 | — | — | Reported line; no script-owned change computed |
| EBITDA, canonical/reported | — | — | — | — | — | — | CP-1 does not retain a supported canonical EBITDA figure for this comparison |
| Adjusted EBITDA, issuer-reported | 920 | 955 | 1,807 | 1,839 | — | — | Kept distinct from canonical EBITDA; issuer-reported values |
| Adjusted EBITDA margin, issuer-reported | 30.7% | 32.9% | 30.8% | 32.3% | — | — | Source-reported ratios; not a cash margin |
| D&A | 355 | 364 | 702 | 721 | — | — | Reported GAAP income-statement line |
| EBIT / operating income | 513 | 526 | 1,013 | 1,014 | — | — | Reported operating income; not treated as EBITDA |
| Cash Interest Paid — debt | — | — | (368) | (405) | — | — | Cash-paid value reported for H1 only; no Q2 split |
| Cash Taxes Paid | — | — | (11) | (58) | — | — | Cash-paid value reported for H1 only; no Q2 split |
| Total Capex | (167) | (230) | (335) | (453) | — | — | Q2/H1 segment schedule; no quarterly maintenance/growth split |
| Maintenance Capex | — | — | (181) | — | — | — | H1 2026 source classification; prior-period split not provided here |
| Growth / renovation capex | — | — | (154) | — | — | — | H1 2026 CP-1 classification; source separates growth/renovation and Digital categories |
| Working Capital Change | — | — | — | — | — | — | CP-1 normalized aggregate not retained; not derived from individual cash-flow movements |
| OCF / CFO | — | — | 675 | 680 | — | — | Reported H1 CFO; Q2 is not separately reported |
| FCF | — | — | — | — | — | — | CP-1 canonical FCF not populated; no CFO-minus-capex calculation performed |
| DCF | — | — | — | — | — | — | No CP-1 value or definition retained for this period |
| Net Income (Loss) Attributable to Caesars | (62) | (82) | (160) | (197) | — | — | GAAP loss narrowed in Q2; no change recalculated here |

#### T4.5 — KPI Dashboard

| KPI Category | Metric Name | Q2 2026 | Q2 2025 | H1 2026 | H1 2025 | YoY Change | Trend Direction | Calculation Status | Analyst Note |
|---|---|---:|---:|---:|---:|---|---|---|---|
| Leverage | Total Debt / EBITDA | — | — | — | — | — | — | Not Calculable | Matching-period canonical EBITDA not retained |
| Leverage | Net Debt / EBITDA | — | — | — | — | — | — | Not Calculable | Matched canonical EBITDA and CP-1 ratio output not retained |
| Leverage | Senior Secured Leverage | — | — | — | — | — | — | Not Calculable | Supported carrying-value seniority ratio not available in the retained canonical KPI set |
| Coverage | EBITDA / Cash Interest | — | — | — | — | — | — | Not Calculable | Q2 cash interest is not separately disclosed; H1 numerator basis is not confirmed |
| Coverage | (EBITDA - Capex) / Cash Interest | — | — | — | — | — | — | Not Calculable | Matched canonical EBITDA and cash interest inputs absent |
| Leverage | FFO / Debt | — | — | — | — | — | — | Not Calculable | CP-1 FFO numerator and ratio not retained |
| Cash Flow | FCF / Debt | — | — | — | — | — | — | Not Calculable | CP-1 canonical FCF not populated |
| Cash Flow | FCF Conversion | — | — | — | — | — | — | Not Calculable | Canonical FCF and EBITDA denominator not populated |
| Margin | Gross Margin | — | — | — | — | — | — | Not Available | Gross profit is not separately presented on a consistent basis |
| Margin | Adjusted EBITDA Margin, issuer-reported | 30.7% | 32.9% | 30.8% | 32.3% | — | Lower | Supported | Source-reported measure; margin pressure weakens earnings cushion |
| Growth | Revenue Growth | 3.0% | — | 2.8% | — | Reported | Higher | Supported | Management-reported same-period revenue growth; no forecast beat/miss asserted |
| Liquidity | Reported cash and borrowing-capacity summary, $m | 2,928 | — | — | — | — | — | Supported | June 30, 2026 source summary, not a calculated covenant or unrestricted-liquidity headroom measure |

#### T4.6 — Variance Register

| Metric | Comparison Basis | Prior Value | Current Value | Abs Change | % Change | Mgmt Driver | Analyst Driver | Credit Implication |
|---|---|---:|---:|---:|---:|---|---|---|
| Consolidated revenue | YoY same quarter | 2,907 | 2,993 | 86 | 3.0% | Higher casino revenue; Digital handle/hold, Windsor consolidation, northern Nevada event visitation and investments contributed; Las Vegas declines partly offset | Growth is uneven by segment and includes a perimeter contribution | Revenue growth supports the top line, but does not establish improved debt-service capacity when Adjusted EBITDA falls |
| Consolidated Adjusted EBITDA | YoY same quarter | 955 | 920 | — | (3.7)% | Issuer-reported total; see segment drivers below | Earnings fell despite higher revenue, consistent with weaker conversion/mix | Negative for operating cushion and debt-service capacity; absolute change not independently calculated |
| Las Vegas revenue | YoY same quarter | 1,054 | 1,017 | (37) | (3.5)% | Lower city-wide leisure visitation; weaker hotel occupancy/rates and table games volume/hold | Las Vegas is a principal earnings engine; a further visitation decline can reduce property contribution while fixed costs remain | Negative for margin resilience and cash available for fixed obligations |
| Las Vegas Adjusted EBITDA | YoY same quarter | 469 | 410 | (59) | (12.6)% | Revenue and margin declines attributed principally to lower visitation, occupancy and room rates | EBITDA decline exceeded revenue decline, indicating adverse operating leverage in this segment | Negative for earnings cushion and debt-service resilience |
| Regional revenue | YoY same quarter | 1,435 | 1,570 | 135 | 9.4% | Windsor consolidation, event-driven northern Nevada visitation and recent investments | Reported growth is not fully comparable and may include non-repeat event contribution | Positive only if durable and comparable; otherwise it may not offset Las Vegas weakness |
| Regional Adjusted EBITDA | YoY same quarter | 439 | 488 | 49 | 11.2% | Same stated drivers; issuer reports increased labor costs and gaming taxes affecting margins | Strongest contrary evidence, but Windsor/perimeter and event effects qualify its durability | Could improve consolidated coverage if repeated on a comparable basis; monitor subsequent same-perimeter performance |
| Caesars Digital revenue | YoY same quarter | 343 | 351 | 8 | 2.3% | Higher sports betting/iGaming handle and higher iGaming hold | Revenue growth did not translate into EBITDA growth | Limited top-line support; hold, tax and promotion volatility may affect cash earnings |
| Caesars Digital Adjusted EBITDA | YoY same quarter | 80 | 68 | (12) | (15.0)% | Lower sports betting hold and higher gaming tax rates in some jurisdictions | Margin/earnings weakness despite increased revenue shows channel-level conversion risk | Negative for earnings diversity; monitor hold, taxes, promotions and EBITDA |
| CFO / OCF | YoY H1 | 680 | 675 | — | — | Company attributes change primarily to working-capital changes and operating results | H1 cash flow remains positive but is not quarterly FCF and does not include a matched debt-service analysis | Counterweight to earnings decline, but insufficient to establish cash available after capex and rent |
| GAAP net loss attributable to Caesars | YoY same quarter | (82) | (62) | — | — | Issuer reports a smaller net loss | Improvement in GAAP loss does not reverse lower Adjusted EBITDA; drivers differ | Limited counterevidence; EBITDA and cash obligations remain central to creditor capacity |

#### T4.7 — Corporate Actions & Comparability

| Event | Date | Description | Impact | Comparability Effect | Credit Implication | Source |
|---|---|---|---|---|---|---|
| Caesars Windsor operating and asset purchase | March 3, 2026 | Operations assumed under a 20-year operating agreement; the property is reported in Regional from this date | No discrete EBITDA effect isolated in the supplied comparison | Regional 2026 includes Windsor while prior-year Regional did not include its consolidated operations | Do not treat the whole reported Regional increase as same-perimeter recurring growth; affects earnings quality and confidence | 10-Q pp. 6, 17 [C22] |
| Grand Bazaar acquisition | May 1, 2026 | Remaining membership interest acquired; approximately $66m consideration, including $10m deferred consideration | Consideration disclosed; earnings contribution not isolated | Q2 includes the acquired asset after May 1 | Incremental investment and partial-period contribution complicate trend attribution; no earnings uplift assumed | 10-Q p. 18 [C23] |
| Proposed merger with Fertitta Gaming | May 27, 2026 | Merger agreement entered; filing reports merger-related transaction costs | Merger-specific costs reported as $10m for Q2 and H1; broader statement/reconciliation figures retained separately in CF-3 | In-period corporate transaction; no completion assumed | Costs and distraction may affect cash generation; monitor transaction progress and any change in operating flexibility | 10-Q pp. 5–6 [C24] |
| Subsequent Event — Alberta launch | July 13, 2026 | Mobile sports betting and iGaming launched in Alberta after June 30 | Financial effect not quantified | Outside Q2/H1 historical figures; not blended into reported results | Potential future operating contribution/cost is unmeasured; assess only when quantified | 10-Q p. 17 [C25] |
| Caesars Windsor segment reporting change | March 3, 2026 | Windsor operations transferred from Managed and Branded presentation into Regional | No comparable-period recast supplied in the delivered data | Creates segment classification and perimeter discontinuity | Track segment trends on a Windsor-consistent basis before relying on reported Regional growth | 10-Q pp. 6, 17 [C22] |
| Share repurchases | Q2 2025; none in Q2/H1 2026 | Filing reports $100m repurchase in Q2 2025 and no repurchases in the 2026 quarter or half-year | Historical financing cash use differs; not an operating earnings driver | Cash-flow financing comparison is affected | Do not read Q2 2026 operating cash change as directly comparable without recognizing the prior-period financing use | 10-Q p. 13; cash-flow statement p. 4 |

#### T4.8 — Comparative Evaluation

| Metric | Benchmark Source | Benchmark Type | Expected Value | Actual Value | Variance | Credit Implication |
|---|---|---|---:|---:|---|---|
| Revenue | 10-Q same-period 2025 actual | YoY actual; not forecast | 2,907 | 2,993 | Management reports +86m / +3.0% | Positive revenue growth, but not a beat against guidance or base case |
| Adjusted EBITDA | 10-Q same-period 2025 actual | YoY actual; issuer-reported measure | 955 | 920 | Management/release reports (3.7)% | Lower earnings cushion despite revenue growth |
| Adjusted EBITDA margin | 10-Q same-period 2025 actual | YoY actual; issuer-reported measure | 32.9% | 30.7% | Lower; no recalculated point change | Negative for margin resilience |
| H1 CFO | 10-Q H1 2025 actual | YoY actual | 680 | 675 | —; change not recalculated | Positive cash generation remains a counterweight, but does not establish FCF after capex/rent |
| Management guidance / approved base case | No such benchmark included in delivered source set | Not available for comparison | — | — | No beat/miss assessment made | Obtain a dated approved benchmark before making forecast variance claims |

#### T4.9 — Conflict Log

| Conflict Description | Source(s) | Metric(s) | Period(s) | Materiality | Resolution Status | Downstream Impact |
|---|---|---|---|---|---|---|
| CF-1 — Face/book debt totals differ from balance-sheet carrying-value debt; Q2 debt note reports total debt of 11,807 face and 11,705 book, while the balance sheet reports current debt 114 and long-term debt 11,585. | 10-Q pp. 2, 9 [C13, C14, C15, C16] | Total debt; leverage denominator | June 30, 2026 | MATERIAL | Reconciled for CP-1 canonical debt use: 114 current plus 11,585 long-term carrying value; retain note totals as separate bases | Use carrying value only for canonical debt metrics; no gross-principal ratio substitution |
| CF-2 — Issuer Adjusted EBITDA is not the retained CP-1 canonical EBITDA or a confirmed credit-agreement definition. | 10-Q pp. 16, 21 [C2] | EBITDA; leverage; coverage; covenant metrics | Q2/H1 2026 and comparators | MATERIAL | Definition distinction retained; no alternative canonical value selected | Leverage, coverage and covenant headroom remain uncalculated |
| CF-3 — One transaction-related event carries several different reported amounts/roles: income-statement Transaction and other costs, net of 16 Q2 / 20 H1; issuer Adjusted EBITDA reconciliation add-back of 29 Q2 / 45 H1; and merger-specific costs of 10 for Q2 and H1. A cash-paid amount is not identified in the retained cash-flow detail. | 10-Q pp. 3, 6, 16 [C24, C36, C42] | Transaction costs; Adjusted EBITDA reconciliation; cash flow | Q2/H1 2026 | MATERIAL | Roles and periods preserved; not silently reconciled or treated as equivalent; no analyst normalization applied | Add-back quality and cash conversion require further review; do not equate the reconciliation add-back with cash paid or merger-only expense |
| CF-4 — Regional year-over-year comparison includes Caesars Windsor operations from March 3, 2026 and event-driven visitation; the prior-year perimeter differs. | 10-Q pp. 6, 20 [C6, C22, C29, C30] | Regional revenue; Adjusted EBITDA; margins | Q2/H1 2026 vs 2025 | MATERIAL | Reported figures retained; no same-perimeter recast supplied | Weakens confidence in Regional growth as a durable offset; affects downstream trend use |
| CF-5 — Q2 cash-flow measures cannot be matched to the income-statement quarter because the cash-flow statement and cash interest/tax disclosure are H1-only. | 10-Q pp. 4–5 [C9, C11, C12] | CFO, FCF, cash-interest coverage, cash taxes | Q2 2026 and Q2 2025 | MATERIAL | Preserved as a period-coverage gap; no quarterly split estimated | Q2 FCF and cash interest coverage remain uncalculated |

#### T4.10 — Monitoring Assessment

| Signal Type | Metric/Indicator | Evidence | Severity | Credit Implication | Recommended Action |
|---|---|---|---|---|---|
| Deterioration | Consolidated Adjusted EBITDA and margin | Q2 Adjusted EBITDA 920 vs 955; margin 30.7% vs 32.9% [C2, C3] | MATERIAL | Smaller operating cushion increases sensitivity to fixed debt and lease obligations | Track each reported quarter and reconcile EBITDA to CP-1 definitions |
| Deterioration | Las Vegas visitation, hotel and gaming trends | Lower city-wide leisure visitation, occupancy/rates and table-games volume/hold cited as drivers [C5] | MATERIAL | Weaker property contribution can reduce debt-service resilience while contractual costs persist | Monitor visitation, occupancy, table drop/hold and segment margin |
| Mixed / counter-signal | Regional growth and Windsor perimeter | Regional revenue and EBITDA rose; Windsor and event/investment drivers cited [C6, C22] | MATERIAL | Could offset Las Vegas weakness if repeated on a comparable basis; current comparison is not fully like-for-like | Require subsequent same-perimeter evidence before crediting durable offset |
| Deterioration | Caesars Digital EBITDA and hold/tax sensitivity | Q2 Adjusted EBITDA 68 vs 80; issuer attributes decline to lower sports hold and higher gaming taxes [C7, C32] | MATERIAL | Volatile hold and higher taxes can erode earnings despite handle/revenue growth | Monitor hold, promotions, tax rates and quarterly Adjusted EBITDA |
| Liquidity watch | Debt service, rent and cash conversion | Remaining-2026 estimated debt service about 425m and VICI/GLPI rent payments about 687m; H1 CFO 675m [C9, C18, C19] | MATERIAL | These obligations compete for operating cash; Adjusted EBITDA alone does not establish liquidity | Track CFO, capex, rent, debt service and unrestricted liquidity together |
| Definition / covenant watch | Covenant compliance vs headroom | Filing reports compliance as of June 30, 2026; no calculated headroom in the retained analysis [C26] | MATERIAL | Compliance is not evidence of cushion; deterioration could reduce financial flexibility | Obtain current agreement calculations and test inputs; do not infer headroom |
| Subsequent event | Alberta launch | Launch occurred July 13, after the reporting date [C25] | MINOR | Future earnings/cash effect cannot be included in historical Q2 or quantified here | Track separately when reported; never blend into Q2/H1 results |

#### T4.11 — Gaps & Limitations Ledger

| Gap Description | Affected Metric/Section | Affected Period(s) | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|---|
| CP-1 retained handoff does not contain a complete metric-level canonical EBITDA definition/formula and matching canonical EBITDA history for this comparison. | T4.2, T4.3, T4.5, T4.12–T4.15 | Q2/H1 2026 and comparators | Leverage, coverage and covenant measures cannot use issuer Adjusted EBITDA as a substitute | MATERIAL | Complete CP-1 definition and calculation registers; keep issuer Adjusted EBITDA separately labelled |
| Script-owned period changes and KPI calculations were not executed in this interaction. | T4.4, T4.5, T4.6, T4.12 | Q2/H1 2026 and comparators | Numeric change cells and dependent ratios remain null or `—`; no hand-derived substitutes | MATERIAL | Run governed host calculations and reconcile their output to CP-1 before downstream model use |
| Cash-flow and cash-paid interest/tax disclosure is H1/FY, not a discrete Q2 cash-flow statement. | T4.4–T4.6, T4.12–T4.13 | Q2 2026 and Q2 2025 | Quarterly CFO, FCF and cash interest coverage cannot be calculated | MATERIAL | Obtain direct quarter-level source data if available; otherwise retain as null |
| CP-1 canonical FCF, FFO and several operating cash-flow KPIs are not populated in its retained handoff. | T4.3–T4.5, T4.12–T4.13 | H1 2026, H1 2025 and other periods | Cash conversion and debt-service capacity remain unassessed on a canonical basis | MATERIAL | Complete CP-1 normalized cash-flow calculations and preserve its capex/WC conventions |
| No dated approved base case, management guidance or rating-agency benchmark is in the delivered evidence. | T4.8; comparative assessment | Q2/H1 2026 | No forecast beat/miss or rating-agency variance can be asserted | MATERIAL | Supply the benchmark and its period/definition before comparison |
| Windsor consolidation and event visitation affect Regional comparability; no same-perimeter recast is supplied. | T4.6–T4.10; segment trend | Q2/H1 2026 vs 2025 | Reduces confidence that Regional growth is repeatable or fully offsets Las Vegas decline | MATERIAL | Obtain comparable-period segment data or monitor later reported periods on a consistent perimeter |
| Full executed financing documents and current covenant calculations are not included in the delivered source set. | Covenant headroom; T4.10; downstream model | June 30, 2026 | Compliance statement cannot be converted into covenant capacity or headroom | MATERIAL | Obtain current executed documents, amendments and covenant calculation inputs |
| Subsequent-event review is bounded by the delivered 10-Q and release; Alberta is identified, but the supplied pack does not establish later event effects through the analysis date. | T4.7; subsequent events | After June 30, 2026 | No subsequent event is blended into period results; later financial effects remain open | MINOR | Review a current issuer filing/update when supplied and retain each event date |
| The 10-Q map and 10-K stock-performance graphic are not represented in the delivered text extractions. | Source coverage; segment/map and market-context work | Current and annual source periods | No map-only or performance-graph values are used; no effect on reported statement figures | MINOR | Obtain graphical representation only if required for a downstream question |
| No consumer, peer or market source is included beyond issuer filings and release. | Comparative evaluation | Q2 2026 | External peer/market performance is not assessed | MINOR | Keep conclusions issuer-specific unless permitted comparative evidence is supplied |

#### T4.12 — Model Comparator Register

<!-- table-id: cp1b.model_comparator_register -->

| metric_id | current_period_id | reference_period_id | comparison_basis | current_value | reference_value | absolute_change | percentage_change | calculation_status | restatement_flag | basis_change_flag | perimeter_change_flag | definition_change_flag | values | changes |
|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|
| revenue | Q2_2026 | Q2_2025 | YOY_SAME_QUARTER | 2993 | 2907 | null | null | Not Available | false | false | true | false | 2993/2907 | null |
| adjusted_ebitda | Q2_2026 | Q2_2025 | YOY_SAME_QUARTER | 920 | 955 | null | null | Not Available | false | false | true | false | 920/955 | null |
| cfo_ncfo | H1_2026 | H1_2025 | YTD_PRIOR | 675 | 680 | null | null | Not Available | false | false | true | false | 675/680 | null |
| capex_and_intangible_investment | H1_2026 | H1_2025 | YTD_PRIOR | -335 | -453 | null | null | Not Available | false | false | true | false | -335/-453 | null |
| total_debt | Q2_2026 | FY2025 | SEQUENTIAL | 11699 | 11784 | null | null | Not Available | false | false | false | false | 11699/11784 | null |
| cash_and_equivalents | Q2_2026 | FY2025 | SEQUENTIAL | 965 | 887 | null | null | Not Available | false | false | false | false | 965/887 | null |

#### T4.13 — Model Validation Register

<!-- table-id: cp1b.model_validation_register -->

| metric_id | period_id | cp1_value | cp1b_comparison_value | difference | tolerance | status | explanation | source_or_conflict_ref |
|---|---|---:|---:|---:|---:|---|---|---|
| revenue | Q2_2026 | 2993 | 2993 | 0 | 0 | PASS | Same source-reported period value; CP-1 remains authoritative | 10-Q p. 2 [C1] |
| revenue | Q2_2025 | 2907 | 2907 | 0 | 0 | PASS | Same source-reported period value; CP-1 remains authoritative | 10-Q p. 2 [C1] |
| adjusted_ebitda | Q2_2026 | 920 | 920 | 0 | 0 | PASS | Issuer-reported value matches the source; definition remains distinct from canonical EBITDA | 10-Q p. 16 [C2] |
| adjusted_ebitda | Q2_2025 | 955 | 955 | 0 | 0 | PASS | Issuer-reported value matches the source; definition remains distinct from canonical EBITDA | 10-Q p. 16 [C2] |
| adjusted_ebitda | H1_2026 | 1807 | 1807 | 0 | 0 | PASS | Issuer-reported value matches the source | 10-Q p. 16 [C2] |
| adjusted_ebitda | H1_2025 | 1839 | 1839 | 0 | 0 | PASS | Issuer-reported value matches the source | 10-Q p. 16 [C2] |
| ebitda | Q2_2026 | null | null | null | null | WARN | CP-1 retained value is null; no substitute selected | CF-2 |
| cfo_ncfo | H1_2026 | 675 | 675 | 0 | 0 | PASS | Direct H1 cash-flow value matches the source | 10-Q p. 4 [C9] |
| cfo_ncfo | H1_2025 | 680 | 680 | 0 | 0 | PASS | Direct H1 cash-flow value matches the source | 10-Q p. 4 [C9] |
| fcf | H1_2026 | null | null | null | null | WARN | CP-1 canonical FCF is null; not inferred from CFO and capex | G-3 |
| total_debt | Q2_2026 | 11699 | 11699 | 0 | 0 | PASS | CP-1 carrying-value debt retained; face/book figures remain separate | 10-Q pp. 2, 9 [C13, C14, C15, C16]; CF-1 |
| cash_and_equivalents | Q2_2026 | 965 | 965 | 0 | 0 | PASS | Balance-sheet cash and equivalents match the source; restricted cash excluded | 10-Q p. 2 [C13] |

#### T4.14 — Add-Back Validation Register

<!-- table-id: cp1b.addback_validation_register -->

| addback_id | period_id | cp1_value | cp1b_comparison_value | difference | tolerance | status | label_match | definition_change_flag | explanation | source_or_conflict_ref |
|---|---|---:|---:|---:|---:|---|---|---|---|---|
| NCI_2026Q2 | Q2_2026 | 21 | 21 | 0 | 0 | PASS | true | false | Exact CP-1 issuer label and Q2 value match | 10-Q p. 16 [C37] |
| TAX_2026Q2 | Q2_2026 | -12 | -12 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C38] |
| OTHER_INCOME_2026Q2 | Q2_2026 | -7 | -7 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C39] |
| INTEREST_2026Q2 | Q2_2026 | 573 | 573 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C40] |
| DA_2026Q2 | Q2_2026 | 355 | 355 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C41] |
| TRANSACTION_2026Q2 | Q2_2026 | 29 | 29 | 0 | 0 | PASS | true | false | Exact issuer label and reconciliation value match; this is not the P&L charge or merger-only cost | 10-Q p. 16 [C42]; CF-3 |
| SBC_2026Q2 | Q2_2026 | 23 | 23 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C43] |
| NCI_2026H1 | H1_2026 | 36 | 36 | 0 | 0 | PASS | true | false | Exact CP-1 issuer label and H1 value match | 10-Q p. 16 [C37] |
| TAX_2026H1 | H1_2026 | 0 | null | null | 0 | WARN | true | false | Source displays a dash; comparison remains null rather than silently converting the dash to zero | 10-Q p. 16 [C38] |
| OTHER_INCOME_2026H1 | H1_2026 | -5 | -5 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C39] |
| INTEREST_2026H1 | H1_2026 | 1142 | 1142 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C40] |
| DA_2026H1 | H1_2026 | 702 | 702 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C41] |
| TRANSACTION_2026H1 | H1_2026 | 45 | 45 | 0 | 0 | PASS | true | false | Exact issuer label and reconciliation value match; distinct from P&L and merger-only amounts | 10-Q p. 16 [C42]; CF-3 |
| SBC_2026H1 | H1_2026 | 47 | 47 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-Q p. 16 [C43] |
| NCI_FY2025 | FY2025 | 65 | 65 | 0 | 0 | PASS | true | false | Exact CP-1 issuer label and value match | 10-K p. 52 [C44] |
| TAX_FY2025 | FY2025 | -11 | -11 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C45] |
| OTHER_INCOME_FY2025 | FY2025 | -2 | -2 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C46] |
| DEBT_EXT_FY2025 | FY2025 | 4 | 4 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C47] |
| INTEREST_FY2025 | FY2025 | 2304 | 2304 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C48] |
| IMPAIRMENT_FY2025 | FY2025 | 182 | 182 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C49] |
| DA_FY2025 | FY2025 | 1417 | 1417 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C50] |
| TRANSACTION_FY2025 | FY2025 | 72 | 72 | 0 | 0 | PASS | true | false | Exact issuer label and source value match | 10-K p. 52 [C51] |
| SBC_FY2025 | FY2025 | 95 | 95 | 0 | 0 | PASS | true | false | Exact label and source value match | 10-K p. 52 [C52] |

#### T4.15 — Model Readiness

<!-- table-id: cp1b.model_readiness -->

| downstream_module | status | blocking_metric_ids | blocking_period_ids | conflict_refs | explanation |
|---|---|---|---|---|---|
| CP-MODEL | BLOCKED | adjusted_ebitda; cfo_ncfo; capex_and_intangible_investment; total_debt | Q2_2026; Q2_2025; H1_2026; H1_2025; FY2025 | CF-1; CF-2; CF-3; CF-4; G-1; G-2; G-3; G-4 | CP-MODEL is listed as the downstream consumer on every run. Readiness is blocked because the retained upstream contains fewer than four complete discrete quarters, script-owned calculations/reconciliations remain open, and the H1 tax add-back source dash is not a supported numeric comparison. CP-1 remains authoritative; no alternative canonical value is emitted. |

<!-- table-id: cp1b.cp_model_snapshot_fields -->

| field_id | value | status | source_id | source_locator | as_of |
|---|---|---|---|---|---|
| historical_performance | Q2 revenue increased 3.0% while issuer-reported Adjusted EBITDA and margin declined; Las Vegas weakness and lower Digital EBITDA were partly offset by Regional growth, whose comparability is affected by Windsor consolidation and event visitation. H1 CFO remained positive at $675m. Cash conversion and canonical leverage are not concluded from these trends. | READY | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 4, 18–21 [C2, C3, C5, C6, C7, C8, C9, C22] | 2026-06-30 |

## Evidence Trace

| Claim / register coverage | Marker | Document | Page |
|---|---|---|---:|
| Q2/H1 consolidated revenue values | [C1] | CZR_Q2_2026_10Q.txt | 2 |
| Adjusted EBITDA Q2/H1 values | [C2] | CZR_Q2_2026_10Q.txt | 16 |
| Adjusted EBITDA margins | [C3] | CZR_Q2_2026_10Q.txt | 18 |
| GAAP Q2 net-loss comparison | [C4] | CZR_Q2_2026_Earnings_Release.txt | 1 |
| Las Vegas driver narrative | [C5] | CZR_Q2_2026_10Q.txt | 20 |
| Regional drivers and counter-signal | [C6] | CZR_Q2_2026_10Q.txt | 20 |
| Digital earnings driver | [C7] | CZR_Q2_2026_10Q.txt | 21 |
| Reported revenue changes | [C8] | CZR_Q2_2026_10Q.txt | 19 |
| H1 CFO comparison | [C9] | CZR_Q2_2026_10Q.txt | 4 |
| Q2/H1 capex | [C10] | CZR_Q2_2026_10Q.txt | 16 |
| H1 cash interest and taxes | [C11, C12] | CZR_Q2_2026_10Q.txt | 5 |
| Cash, carrying debt lines and debt-note total | [C13, C14, C15, C16] | CZR_Q2_2026_10Q.txt | 2, 9 |
| Reported liquidity capacity, debt service and lease payments | [C17, C18, C19] | CZR_Q2_2026_10Q.txt | 22 |
| Customer-liability obligation and balance | [C20, C21] | CZR_Q2_2026_10Q.txt | 11 |
| Windsor perimeter, Grand Bazaar acquisition and merger costs | [C22, C23, C24] | CZR_Q2_2026_10Q.txt | 6, 18 |
| Post-period Alberta launch and covenant compliance | [C25, C26] | CZR_Q2_2026_10Q.txt | 17, 18 |
| Las Vegas revenue and Adjusted EBITDA changes | [C27, C28] | CZR_Q2_2026_10Q.txt | 20 |
| Regional revenue and Adjusted EBITDA changes | [C29, C30] | CZR_Q2_2026_10Q.txt | 20 |
| Digital revenue and Adjusted EBITDA changes | [C31, C32] | CZR_Q2_2026_10Q.txt | 20 |
| G&A, operating income and attributable net loss | [C33, C34, C35] | CZR_Q2_2026_10Q.txt | 3 |
| P&L transaction-cost role | [C36] | CZR_Q2_2026_10Q.txt | 3 |
| Q2/H1 adjusted EBITDA add-back validation rows, in CP-1 issuer-label order | [C37, C38, C39, C40, C41, C42, C43] | CZR_Q2_2026_10Q.txt | 16 |
| FY2025 issuer-specific add-back validation rows, in CP-1 issuer-label order | [C44, C45, C46, C47, C48, C49, C50, C51, C52] | CZR_FY2025_10K.txt | 52 |
| CP-MODEL historical snapshot and limitation context | [C1, C2, C3, C5, C6, C7, C8, C9, C22] | CZR_Q2_2026_10Q.txt | 2, 4, 16, 18–21 |

## Source Registry

T4.1 classifies the three delivered sources and their periods, quality and uses. The Q2 Form 10-Q is the controlling current-period financial source; the audited FY2025 Form 10-K supplies annual context; the earnings release corroborates headline results. No external source, peer, current market observation, rating-agency benchmark or approved forecast is included. The accepted CP-0 handoff identifies text-representation limitations for the filing visuals; no visual-only value is used. CP-1’s accepted handoff supplies the canonical numeric reference for this module, with its Restricted status and calculation limitations preserved.

## Gaps & Conflicts

CF-1 through CF-5 preserve debt-basis, EBITDA-definition, transaction-cost-role, segment-perimeter and period-alignment issues. G-1 through G-4 record unavailable calculation lineage, missing Q2 cash-flow data, absent benchmarks and missing executed financing/covenant inputs. The earnings signal is therefore bounded: revenue growth is directly reported, but earnings declined and cash conversion/leverage cannot be established on a complete canonical basis. The strongest contrary evidence is Regional growth and positive H1 CFO; it would materially improve conviction only if sustained on a comparable perimeter after capex, lease payments and debt service. The Alberta launch is subsequent to quarter-end and excluded from reported-period figures.

## QA Validation

| Check | Result | Notes |
|---|---|---|
| Identity, filename and host-owned front matter | Self-review complete | Identity matches CZR / CP-1B / 2026-10-02; filename derives as `CZR_CP-1B_20261002.md`; host-owned lines are retained unchanged. |
| Canonical structure | Self-review complete | Six required H2 headings appear once and in order; conclusion-first opening precedes any table; appendix is present. |
| Required analytical registers | Self-review complete | T4.1–T4.15 are present with declared columns; all required minimum row counts are met; CP-MODEL interface tables are emitted and tagged. |
| Null, definition and period discipline | Restricted | Nulls remain null in tagged tables and `—` in ordinary registers; Q2/H1/FY periods and subsequent event remain separate; no gross-debt or Adjusted EBITDA substitution is used for canonical leverage. |
| Keyed CP-1 validation and add-backs | Restricted | Reported matching values are checked without overriding CP-1. All retained issuer-specific add-back IDs are listed once; the H1 tax dash remains a WARN rather than being converted into a comparison value. |
| Confidence and run status | Restricted | Confidence score 56 / Low; material evidence and calculation gaps cap QA at Restricted. Committee status is Requires More Work. |
| Host validation | Pending | Host validation and completeness checks follow this answer. No vendor-validator result, script output or host finding is asserted. |

**Run status:** Restricted. **Confidence:** 56 / Low. **Host validation:** follows this answer.