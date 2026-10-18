---
module_id: "CP-2"
module_name: "FundamentalCreditSynthesizer"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "COVENANT_REFINANCING"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2-7dffa29515f89271"
credit_os_route_node_id: "RN-FULL_CREDIT_32-COVENANT_REFINANCING-04-CP-2"
credit_os_invocation_sha256: "b8f3b9098aa80ffe2157c3da3e64a905154c1e14140a36d11e8974cc7200108b"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a4ee2ea26d222a51d5c167a5868ea43f9bba131c911042fc7dcb2840af340ca2"
  - module_id: "CP-1"
    run_id: "COS-20261005T071138Z-264a667c228a4a3d98cd59223e790671"
    period: "Q2 2026"
    sha256: "a412c541834dd7643188444e637ba16543096bf4686d71c334f32b4a53e19a67"
confidence_score: 51
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, DEBT_BASIS_RECONCILIATION_OPEN, MERGER_FINANCING_TERMS_NOT_RETAINED, FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED, DEBT_BASIS_RECONCILIATION_OPEN, MERGER_FINANCING_TERMS_NOT_RETAINED, POST_PERIOD_EVENT_SEPARATION]
downstream_consumers: [CP-2A, CP-2B, CP-2C, CP-2D, CP-2E, CP-3, CP-6, CP-5, CP-5A, CP-MODEL]
---

## Audit Summary

- **Run status:** Ready with Limitations; the Q2 2026 filing, FY2025 audited filing and delivered executed credit-agreement documents support a complete, evidence-proportionate fundamental assessment, but not a fully underwritten or committee-ready conclusion.
- **Confidence:** 51/100 — Low. This is analytical confidence, not a rating. Estimate: E=94, C=93, source-gate multiplier S=0.70, and one material QA penalty P=15; (0.6×94 + 0.4×93)×0.70 − 15 = 50.54, reported as 51.
- **Committee status:** Requires More Work. Do not infer covenant capacity, a refinancing price, or transaction financing certainty.
- **Primary limitations:** Q2 balance-sheet carrying debt differs from the debt-note book value; free cash flow and leverage ratios are not calculated; complete merger financing terms and current market quotes are not in the evidence delivered here.
- **Canonical file name:** `CZR_CP-2_20261002.md`.
- **Recommended next action:** Run CP-2D, then CP-3C in route order, carrying the debt-basis, merger-financing and market-evidence gaps forward. CP-MODEL is always listed as a downstream consumer; this handoff supplies its interface tables, not a complete quarterly model pack.

## Analysis

### Credit view
Caesars has a large gaming and hospitality platform with land-based, hotel and digital revenue streams, but those streams remain exposed to discretionary demand, gaming outcomes, competition and regulation. In Q2 2026, revenue rose while Adjusted EBITDA and margin declined; Las Vegas weakness is the clearest operating pressure, while Regional growth partly reflects the March consolidation of Caesars Windsor. Current cash and disclosed revolver capacity provide a meaningful reported liquidity resource, but debt service, substantial lease payments and ongoing capital needs compete for that cash. The 2028–2030 debt schedule makes refinancing access material. The proposed merger is not a Q2 operating result or a completed financing: closing conditions and financing uncertainty remain. The strongest counterweight is reported liquidity and Regional/Digital support; sustained like-for-like earnings and cash conversion would improve that case. FCF, leverage and covenant headroom are not established here. [C5, C6, C7, C8, C9, C12, C13, C15, C16, C24, C25, C26]

**Overall conclusion:** The business profile is broad in footprint and offerings, but creditor resilience is constrained by weak recent margin direction, high fixed lease and debt commitments, and a refinancing need that cannot be assessed against current market quotations. Reported covenant compliance is positive evidence, not a measure of available headroom. [C17, C27]

### Company description and operating model
Caesars earns most revenue from casino gaming and supplements it with hotels, food and beverage, entertainment, racing, retail, management and branding, and digital sports betting and iGaming. At June 30, 2026 it reported 54 properties in 20 North American jurisdictions; its FY2025 filing described 52 properties in 18 states, so the two footprints are different as-of dates, not a same-period contradiction. Caesars Windsor moved from managed operations into the Regional segment on March 3, 2026, and Grand Bazaar was acquired in May; those events affect comparability. [C18, C19]

The operating model monetizes both patron visitation and gaming volume, but gaming revenue is the amount retained rather than total handle. A loyalty program links property and digital usage, supporting cross-market customer engagement, but the evidence does not establish contract-backed recurring revenue or customer retention rates. Competition for patrons and spend therefore remains material to cash-flow visibility. [C19, C20]

**Evidence → risk mechanic → creditor implication:** Q2 revenue rose 3.0% in the quarter and 2.8% in H1, but Adjusted EBITDA margin declined from 32.9% to 30.7% in Q2 and from 32.3% to 30.8% in H1. Revenue expansion therefore did not convert into higher consolidated Adjusted EBITDA; creditors should focus on earnings and cash conversion rather than revenue growth alone. [C6]

Las Vegas Q2 Adjusted EBITDA fell to $410 million from $469 million, and H1 fell to $836 million from $902 million. Management attributes the decline to lower city-wide leisure visitation, hotel occupancy and room rates, and lower table games volume and hold; slot handle partly offset it. Lower visitation and hold reduce property contribution while labor, gaming taxes, rent and maintenance needs persist, weakening debt-service cushion. [C7, C35]

Regional Adjusted EBITDA increased to $488 million from $439 million in Q2 and to $923 million from $879 million in H1. The Q2 filing attributes part of the quarter's increase to Windsor consolidation, northern Nevada visitation and recent property investments. This is meaningful support, but the acquired contribution and near-flat H1 margin mean the reported growth is not proof of broad-based organic improvement. [C8, C36]

Digital Q2 Adjusted EBITDA declined to $68 million from $80 million despite higher revenue; management identifies increased gaming tax rates and lower sports-betting hold. H1 Adjusted EBITDA improved to $137 million from $123 million. Digital can diversify physical-property revenue, but handle, hold, promotional spend, tax rates, technology and third-party services drive volatility; it is not a stable annuity on this evidence. [C9, C37]

### Ownership, group structure and financial policy
The issuer is a publicly traded Delaware corporation with common stock listed on Nasdaq. The FY2025 filing identifies Carano family origins and a related-party lease in which the Executive Chairman and siblings are beneficiaries of a trust. That evidence does not establish current voting control or the full beneficial-ownership picture. The ownership schedule and current post-merger capital structure are therefore gaps, not grounds to infer sponsor control or support. [C31, C32]

The May 27, 2026 merger agreement proposes that Caesars become a wholly owned subsidiary of Fertitta Gaming, subject to stockholder, antitrust and gaming approvals and other conditions. The transaction could alter ownership, leverage and creditor structure, but CP-2 does not determine legal effect or transaction capacity. The filing specifically identifies the risk that required financing may not be obtained on anticipated terms. [C23, C24, C25]

Financial policy is a monitoring risk: the FY2025 filing reports $229 million of 2025 share repurchases under a $500 million authorization, while the Q2 filing says no repurchases are expected at this time because of the proposed merger. The pause is a near-term counterweight, but the authorization and past use make capital allocation relevant to creditors. Governance and shareholder alignment cannot be fully assessed without current ownership data and the complete merger financing documents. [C29, C30]

### Revenue durability, cost structure and cash conversion
Revenue is diverse by product and geography, but the dominant gaming and hospitality activities remain discretionary and exposed to regional competition, travel, visitation and chance-based hold. Gaming taxes, labor and customer reinvestment costs can rise even when volume or mix is adverse. The 10-K identifies direct competition from nearby casinos and discretionary-spending sensitivity; the 10-Q shows current Las Vegas weakness and higher tax expense in digital and regional operations. This combination can compress contribution before fixed lease obligations adjust. [C20, C21, C35, C37]

A material fixed-cost and funding burden comes from the VICI and GLPI leases. FY2025 disclosure describes approximately $1.4 billion of 2026 annual lease payments with escalation; at Q2 the company estimated $687 million for the remainder of 2026. These are different as-of-date estimates and periods, so neither is substituted for the other. Rent, property maintenance and lease covenants reduce cash available for debt service, discretionary capex and deleveraging. [C15, C28]

H1 operating cash flow was $675 million versus $680 million; reported property and equipment purchases were $335 million versus $453 million. These inputs do not establish free cash flow: the supplied record does not provide an adopted FCF calculation, and this analysis does not manufacture one. Cash interest paid was $368 million in H1, before considering rent, taxes, debt principal, distributions and other uses. The credit implication is that FCF stability and deleveraging capacity remain unproven despite positive reported CFO. [C10, C11]

Customer deposits and other deferred revenue increased by $53 million in H1 to $545 million. The filing describes these balances as gaming deposits or advance payments for goods and services not yet provided; they are operating funding float, not debt or unrestricted surplus cash. A downturn or elevated customer redemption/performance obligations can turn that float into future cash requirements. Track the balance and its obligation profile rather than adding it to funded debt. [C38, C39]

### Market frameworks translated to creditor consequences
**Porter — competitive rivalry:** High. The issuer reports direct competition from nearby casinos and aggressive reinvestment and marketing. Pressure on visitation, gaming hold and promotional spending can lower property margins and cash available for debt service. [C20, C35]

**Threat of new entrants:** Barriers are meaningful because gaming requires licenses and regulatory approvals, but those barriers do not prevent new casino supply or new online products. New supply and licensing-driven tax or compliance costs can dilute operating returns and raise capital needs. [C20, C24]

**Threat of substitutes:** Material. Other leisure activities, online offerings, tribal gaming and sports-event trading compete for customer spending. Substitution away from property visits can reduce hotel and gaming contribution before fixed obligations move. [C20, C21]

**Buyer power:** Material in the credit sense: the filing characterizes gaming and leisure as discretionary and describes competing offers and marketing. Customers can shift visitation or spend, and promotional responses may protect volume at the cost of margin. The evidence does not quantify customer concentration or switching rates. [C21, C37]

**Supplier power:** Relevant through labor, gaming taxes, utilities, technology and leased real estate. Union representation covers approximately 21,000 employees; Q2 expenses reflect wage and tax pressures, while lease costs are substantial and escalatory. These costs constrain downside flexibility and FCF. [C15, C22, C28]

**PEST:** Economic conditions affect discretionary travel and spending; interest rates affect floating-rate borrowings; gaming regulation and taxes can change operating costs and licensing; technology and third-party platform performance can interrupt digital access and revenue. Each channel can reduce margins or increase cash needs. No external macro forecast is available. [C21, C25, C34, C37]

**SWOT, credit translated:**
- **Strengths:** A large multi-property footprint; several revenue channels; Regional and H1 Digital Adjusted EBITDA growth; reported cash and borrowing capacity. These can absorb localized weakness if sustained. [C8, C9, C12, C18]
- **Weaknesses:** Q2 and H1 consolidated margin contraction; declining Las Vegas earnings; material debt and lease commitments; no calculated FCF or leverage in the delivered analytical record. These limit the demonstrated capacity to self-fund obligations. [C6, C7, C10, C15, C28]
- **Opportunities:** Further digital and jurisdictional expansion or operating improvements could support earnings if after-tax contribution exceeds promotional, technology and compliance costs. This is conditional, not an assumed forecast. [C19, C37]
- **Threats:** Weaker leisure demand, further competitive supply, lower hold, gaming-tax increases, labor pressure, refinancing-market closure or delayed merger financing could jointly reduce cash generation and increase refinancing dependence. [C20, C21, C25, C35, C37]

### Financial profile and outlook
The financial profile is mixed and qualitatively assessed. Scale and footprint support diversification, but gaming remains the principal revenue engine. FY2025 segment disclosure showed Las Vegas Adjusted EBITDA falling to $1,728 million from $1,907 million and Regional to $1,789 million from $1,810 million, while Digital increased to $236 million from $117 million. Q2 2026 confirms Las Vegas pressure and mixed Digital performance; Regional support includes a perimeter change. [C7, C8, C9]

For the next 12–24 months, the key credit question is whether Las Vegas visitation and hold stabilize while Windsor and Digital contributions offset wage, tax and lease costs. For the 3–5 year horizon, the question shifts to funding the 2028–2030 maturities and sustaining reinvestment without weakening liquidity. Management says current liquidity and operating cash flows should suffice for the next twelve months and beyond; that is the strongest issuer counterargument, but it is not supported here by a detailed forward monthly cash forecast or independent FCF calculation. It would gain weight with stable same-property earnings, continued CFO and documented transaction funding. [C13, C16, C17, C35]

The strongest counterevidence is the $2,928 million reported Q2 cash-and-borrowing-capacity total, reported covenant compliance, and improved Regional results. It reduces near-term distress concern but does not establish revolver availability after future uses, covenant headroom, or refinancing market access. Conviction should improve only if reported operating gains persist on a comparable basis and cash conversion and transaction funding become demonstrable. [C8, C12, C27]

### Qualitative downside scenario
Over the next 12–24 months, continued weakness in Las Vegas leisure visitation, hotel occupancy or table-game volume/hold is the initiating condition. The first operational break is lower property revenue and Adjusted EBITDA; labor, gaming taxes, minimum property upkeep and rent then limit cost relief. Lower operating cash flow, combined with capital expenditure, cash interest and contractual payments, would reduce liquidity and could increase revolver reliance. If the earnings weakness persists as the 2028 facility maturity approaches, refinancing becomes more dependent on external market access or transaction-related funding. Observable early signals are Las Vegas volume, hold, occupancy, segment EBITDA, consolidated CFO, cash and revolver availability. Cost efficiencies, marketing discipline and deferral of discretionary growth projects may help, but maintenance needs and rent constrain levers. Whether liquidity resilience is sufficient to avoid distress is not assessable without a forward cash forecast, covenant calculations and current financing evidence. [C7, C10, C11, C13, C15, C16, C25]

**Subsequent event:** Caesars launched mobile sports betting and iGaming in Alberta on July 13, 2026, after the June 30 reporting date. It is not included in Q2 period figures. [C26]

### Analytical appendix — complete canonical registers

#### T2.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 743e5d19-d65d-4487-8114-c0614dfc076d | CZR_Q2_2026_10Q.txt | Primary-Verified | Q2 and H1 2026; quarter ended 2026-06-30 | Caesars Entertainment, Inc. and consolidated subsidiaries | Interim statements, segment results, operating metrics, debt schedule, liquidity, covenant status, merger disclosure and subsequent-event disclosure. [C1, C5, C7, C12, C13, C27] | Unaudited interim period; Windsor and Grand Bazaar change comparability; no complete forward cash forecast or transaction financing terms. [C19, C24, C25] | Current business, earnings, liquidity, debt, downside, monitoring and downstream CP-2/CP-3/CP-6 analysis. |
| 698c9482-cc90-4172-88bb-4354b9b56f38 | CZR_FY2025_10K.txt | Primary-Verified | FY2025; audited annual comparatives | Caesars Entertainment, Inc. and consolidated subsidiaries | Audited history, business description, segment trends, competition, leases, debt, cash flows, capex, share repurchases and governance context. [C18, C20, C28, C29] | Annual figures are not substitutes for Q2 2026; some ownership information is incorporated by reference and not in the delivered evidence. | Business model, cycle and competition context; historical comparison and source-grounded risk assessment. |
| 0aa01e2a-5ebd-4019-90a6-02bf6fa94a3d | CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | Primary-Verified | Executed 2024 agreement; conformed Credit Agreement through February 6, 2024 | Caesars Entertainment, Inc. borrower and listed subsidiary loan parties | Incremental Term B-1 financing and conformed agreement definitions, maturity, financial covenants and loan-party structure. | Referenced schedules are not all present in the delivered representation; it is not a current full underwriting or market source. | Financing structure and interpretive boundary; no CP-2 legal-capacity or covenant-headroom conclusion. |
| 050d12fd-6a63-4d3a-8d28-263977d76585 | CZR_2024_Credit_Agreement_Fourth_Amendment.txt | Primary-Verified | Executed amendment dated May 9, 2024 | Caesars Entertainment, Inc., borrower | Term B margin reduction and amendment provisions. [C33] | Later Fifth Amendment must be read as a subsequent amendment; no standalone inference about current pricing from this earlier text. | Version chronology and financing-cost context. |
| 4577adf6-3d6a-4fa9-bab9-c517e95e6b88 | CZR_2024_Credit_Agreement_Fifth_Amendment.txt | Primary-Verified | Executed amendment dated November 25, 2024 | Caesars Entertainment, Inc., borrower; Term B and Term B-1 lenders | Later Term B and Term B-1 margin reductions and amendment sequence. [C34] | No later executed amendment is included in the CP-2 evidence delivered; no current loan-market quote supplied. | Cost context and source-version reconciliation, not legal advice or a pricing recommendation. |

**Module status:** Ready with Limitations. CP-0 and CP-1 accepted handoffs match the issuer, run and Q2 2026 period. CP-0 and CP-1 themselves carry restricted/source-limited status; their missing full underwriting and market inputs remain limitations, not grounds to fabricate values or to stop supported CP-2 work.

#### T2.7 — Financial Profile Scorecard

| Dimension | Assessment | Credit Rationale |
|---|---|---|
| Scale / market position | Average | 54 properties in 20 North American jurisdictions and multiple operating formats provide scale, but market share and comparative competitive position are not supplied. [C18] |
| Competitive advantage | Average | Caesars brands and Rewards connect property and digital offerings, but nearby casinos, online alternatives and promotional competition constrain pricing power. [C19, C20] |
| Business diversification | Average | Physical gaming, hospitality and digital operations diversify revenue sources; they remain exposed to related discretionary demand, regulation and gaming outcomes. [C18, C19, C21] |
| Cost and capex flexibility | Weak | Labor, gaming taxes, property upkeep, digital investment and lease payments compete with debt service; maintenance capex is not freely deferrable. [C11, C15, C16, C22, C28] |
| Margin stability | Weak | Consolidated margin declined year over year; Las Vegas earnings fell and Digital Q2 earnings declined amid hold and tax pressure. [C6, C7, C9, C37] |
| Free cash flow stability | Not Assessable | CFO and capex are disclosed, but FCF is not calculated in this handoff and lease, interest, tax and other cash uses are material. [C10, C11, C15, C28] |
| Ability to refinance / access capital markets | Weak | The Q2 maturity schedule includes material 2028–2030 payments; no current market quotations, lender indications or complete merger financing terms are available. [C13, C25] |
| Liquidity position | Average | Q2 reports $965 million cash and $2,928 million aggregate cash and borrowing capacity, but this is before a full forward cash-use and covenant-headroom assessment. [C2, C12, C14, C15, C16] |
| Financial policy and governance | Weak | FY2025 share repurchases were $229 million; Q2 indicates no repurchases are expected at this time because of the proposed merger. Ownership and transaction financing remain incomplete. [C23, C29, C30] |

**Synthesis:** The operating footprint and reported liquidity are supports, but recent margin weakness, lease and debt commitments, and refinancing requirements constrain the profile. The merger may change the outlook but is uncompleted and its full financing terms are not in the delivered evidence. No leverage, FCF or covenant headroom is inferred.

#### T2.10 — Materiality Filter

| Rank | Driver | Evidence | Risk Mechanic | Credit Implication | Direction | Confidence |
|---:|---|---|---|---|---|---|
| 1 | Reported liquidity resources | June 30 cash was $965 million and disclosed cash plus borrowing capacity was $2,928 million. [C2, C12] | Cash and facility access can fund near-term operations and contractual uses, subject to borrowing conditions and competing needs. | Positive — Liquidity Improvement | Positive | Medium |
| 2 | Diversified operating footprint and Q2 Regional support | Regional Adjusted EBITDA increased year over year, while the company reports a multi-jurisdictional property and digital footprint. [C8, C18] | Multiple markets and channels may offset localized weakness, although Windsor consolidation limits like-for-like interpretation. | Positive — Revenue Growth | Positive | Medium |
| 3 | Las Vegas deterioration and consolidated margin pressure | Q2 consolidated margin and Las Vegas Adjusted EBITDA declined year over year. [C6, C7, C35] | Lower visitation, hotel occupancy and table-game performance reduce earnings while rent, labor and debt service remain. | Negative — Margin Compression | Negative | High |
| 4 | Fixed lease and debt-service burden | Q2 estimates $687 million of remaining 2026 VICI/GLPI lease payments; FY2025 reports $1.4 billion for full-year 2026. [C15, C28] | Contractual rent and escalators reduce cash available for capex, debt service and deleveraging. | Negative — Liquidity Deterioration | Negative | High |
| 5 | Refinancing and merger-funding uncertainty | The schedule shows maturities in 2028–2030; the filing identifies risk that transaction financing may not be obtained on anticipated terms. [C13, C25] | Market access or transaction delay could increase refinancing dependence as maturities approach. | Negative — Refinancing Risk | Negative | High |

#### T2.11 — Issuer Matrix

| Business Quality Factor | Assessment | Primary Downside Path | Credit Relevance |
|---|---|---|---|
| Revenue durability | Average | Discretionary leisure demand weakens, reducing visitation, hotel occupancy and gaming volume before fixed obligations adjust. [C21, C35] | Lower recurring property contribution reduces debt-service cushion; reported revenue growth alone is not a reliable proxy for cash generation. [C5, C6] |
| Margin resilience | Weak | Lower Las Vegas visitation or hold and higher taxes, wages or promotions compress Adjusted EBITDA. [C7, C35, C37] | Margin pressure transmits directly to lower debt-service capacity and refinancing flexibility. |
| FCF conversion | Not Assessable | CFO is absorbed by capex, interest, lease payments, taxes and other cash uses; a complete FCF figure is unavailable. [C10, C11, C15] | Deleveraging and liquidity runway cannot be established without an aligned FCF calculation and forward cash flow. |
| Liquidity buffer | Average | Operating weakness or transaction delays consume cash and available revolver capacity. [C12, C25] | Reported liquidity supports near-term resilience but does not prove future availability or covenant headroom. |
| Refinancing capacity | Weak | Failure to refinance the 2028–2030 maturities on acceptable terms increases repayment or liquidity pressure. [C13, C25] | No dated market evidence, lender indication or complete transaction financing terms supports an access conclusion. |
| Governance / financial policy | Weak | Capital allocation, ownership or transaction changes reduce resources available to creditors or delay funding certainty. [C23, C29, C30] | Monitor merger status, capital actions and source-supported creditor alignment; do not infer sponsor support. |

**Primary downside path:** Sustained Las Vegas visitation or gaming-hold weakness compresses earnings, reduces cash after leases and capex, and increases reliance on refinancing before the 2028–2030 maturities.

#### T2.12 — Monitoring Triggers

| Trigger | Threshold / Signal | Why It Matters | Credit Impact | Source / Limitation |
|---|---|---|---|---|
| Revenue decline | Quantitative threshold not available in provided materials; monitor reported revenue and Las Vegas visitation, table-game drop and hotel occupancy versus comparable periods. | Persistent weakness would show that diversified revenue is not offsetting pressure in the largest exposed market. | Lower revenue can reduce property contribution and debt-service capacity. | Q2 segment disclosures; comparable same-property series and company-specific tripwire are not provided. [C5, C35] |
| EBITDA margin pressure | Quantitative threshold not available in provided materials; monitor consolidated margin and Las Vegas/Regional/Digital Adjusted EBITDA and margin. | Margin shows whether revenue changes convert to operating earnings after taxes, labor and promotions. | Sustained compression weakens FCF durability and refinancing flexibility. | Q2 margin and segment reporting; issuer Adjusted EBITDA is non-GAAP and not cash flow. [C6, C7, C8, C9] |
| FCF deterioration | Quantitative threshold not available in provided materials; monitor CFO alongside capex, cash interest, lease payments and debt principal. | CFO alone omits important competing cash claims; no FCF measure is calculated here. | Deterioration would reduce liquidity and self-funded deleveraging. | Q2 CFO, capex, interest and lease disclosures; FCF not calculated. [C10, C11, C15] |
| Liquidity reduction | Monitor cash and disclosed revolver capacity against debt service, leases and capex; quantitative tripwire not available in provided materials. | Declining headroom would reduce ability to absorb volatility and fund maturities. | Lower liquidity increases refinancing and distress risk. | Q2 liquidity table and remaining-2026 cash uses; availability after all future needs is not established. [C12, C14, C15, C16] |
| Leverage increase | Quantitative threshold not available in provided materials; obtain aligned carrying-value debt and covenant EBITDA, then monitor reported debt and earnings trends. | Lower earnings or incremental borrowing can raise leverage; reported covenant compliance is not headroom. | Higher leverage can limit financing options and worsen refinancing risk. | Q2 debt schedule and covenant statement; leverage and headroom are not calculated. [C3, C27] |
| Refinancing delay | Signal: delay in refinancing, extension or replacement of facilities due in 2028–2030, or lack of committed transaction financing; quantitative threshold not available. | The maturity schedule places refinancing access on the critical path. | Delay can consume liquidity and increase execution risk. | Q2 maturity schedule; no current quotations, lender indications or complete financing terms. [C13, C25] |
| Sponsor/shareholder action | Signal: merger closing, delay, termination, change to committed financing or renewed capital distributions; quantitative threshold not available. | Ownership and transaction events can change debt, governance and available cash. | Could improve or weaken refinancing certainty and creditor alignment. | Q2 merger disclosure; full agreement and financing documents are not in the CP-2 evidence delivered. [C23, C24, C25, C30] |
| Sector deterioration | Signal: reported competitive supply, lower visitation, gaming-tax changes or sustained weakness in hold; quantitative threshold not available. | Demand, competition and taxes influence both property and digital margins. | Sector pressure can amplify operating leverage and liquidity stress. | FY2025 risk disclosure and Q2 operating discussion; no external sector forecast provided. [C20, C21, C35, C37] |

<!-- table-id: cp2.cp_model_strengths_weaknesses -->

| direction | rank | label | mechanism | evidence_ids | status | source_id | source_locator | as_of |
|---|---:|---|---|---|---|---|---|---|
| STRENGTH | 1 | Reported liquidity resource | Cash and disclosed revolver capacity provide a buffer against near-term cash needs, subject to facility terms and future uses. | CP2-E01; [C2, C12] | READY | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp. 2, 22 | 2026-06-30 |
| STRENGTH | 2 | Multi-jurisdictional, multi-channel operations | Property, hospitality and digital channels may offset localized weakness; Windsor consolidation is a comparability limitation. | CP2-E02; [C8, C18, C19] | READY | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp. 6, 20 | 2026-06-30 |
| STRENGTH | 3 | Reported covenant compliance | Issuer-reported compliance indicates no disclosed period-end covenant breach, but does not quantify headroom. | CP2-E03; [C27] | READY | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q p. 23 | 2026-06-30 |
| WEAKNESS | 1 | Las Vegas earnings and margin decline | Lower visitation, hotel occupancy and table-game outcomes reduce cash contribution while fixed obligations persist. | CP2-E04; [C6, C7, C35] | READY | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp. 18, 20 | 2026-06-30 |
| WEAKNESS | 2 | Debt and lease obligations compete for cash | Material scheduled debt payments, lease payments and capex constrain liquidity available for refinancing and deleveraging. | CP2-E05; [C13, C15, C16, C28] | READY | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp. 9, 22; 10-K p. 13 | 2026-06-30 |
| WEAKNESS | 3 | Cash conversion and refinancing evidence incomplete | FCF, leverage, covenant headroom and current market access are not established in the delivered evidence. | CP2-E06; [C10, C11, C13, C25] | READY | 743e5d19-d65d-4487-8114-c0614dfc076d | 10-Q pp. 4, 9, 22, 24 | 2026-06-30 |

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Q2 reporting period and current filing identity | [C1] | Q2 2026 Form 10-Q | 1 |
| Current cash, liquidity and period cash flow | [C2, C10, C12] | Q2 2026 Form 10-Q | 2, 4, 22 |
| Reported debt note and balance-sheet debt inputs | [C3, C4, C5] | Q2 2026 Form 10-Q | 2, 9 |
| Revenue, margin and segment performance | [C5, C6, C7, C8, C9, C35, C36, C37] | Q2 2026 Form 10-Q | 18, 19, 20, 21 |
| Debt maturity schedule and remaining-2026 obligations | [C13, C14, C15, C16] | Q2 2026 Form 10-Q | 9, 22 |
| Business footprint, competition and economic sensitivity | [C18, C19, C20, C21] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 2, 3, 6 |
| Share repurchases, public listing and related-party context | [C29, C30, C31, C32] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 1, 23, 50 |
| Merger date, conditions and financing uncertainty | [C23, C24, C25] | Q2 2026 Form 10-Q | 5, 24 |
| Subsequent Alberta launch and covenant compliance | [C26, C27] | Q2 2026 Form 10-Q | 17, 23 |
| Credit-agreement margin chronology | [C33, C34] | Fourth Amendment; Fifth Amendment | 1, 1 |
| Contract-liability movement and nature | [C38, C39] | Q2 2026 Form 10-Q | 11, 11 |
| Cash capital expenditure and lease burden | [C11, C15, C16, C28] | Q2 2026 Form 10-Q; FY2025 Form 10-K | 4, 13, 22 |

## Source Registry

The complete CP-2 source register is T2.1 in the analytical appendix. The Q2 Form 10-Q is the primary current-period source; the FY2025 Form 10-K supplies audited historical and business context. The three executed credit-agreement documents are used for financing chronology only. Their presence does not establish current trading levels, refinancing terms, covenant headroom or transaction financing certainty. Citations above point to the delivered evidence pages.

## Gaps & Conflicts

| ID | Type | Finding | Credit effect | Remediation |
|---|---|---|---|---|
| CF-1 | Definition / debt basis | The Q2 debt note reports book debt of $11,705 million and face value of $11,807 million; balance-sheet current debt of $114 million plus long-term debt of $11,585 million gives a carrying-value sum of $11,699 million. The $6 million book-value difference remains unresolved. [C3, C4, C5] | Preserve the balance-sheet carrying basis for canonical debt, show the note totals separately, and do not silently reconcile. Leverage and covenant ratios remain uncalculated. | Obtain issuer reconciliation and aligned current debt schedules. |
| G-1 | Missing metric / cash-flow detail | CFO and capex are reported, but FCF, aligned LTM leverage and covenant EBITDA are not calculated in this handoff. Adjusted EBITDA is issuer-defined and is not a liquidity measure. [C10, C11] | FCF conversion, leverage tolerance and debt-service cushion cannot be determined from these inputs alone. | Obtain complete cash-flow and capex detail plus governed calculations and debt-agreement definitions. |
| G-2 | Missing transaction evidence | The merger is proposed and subject to closing conditions; the filing identifies risk that financing may not be obtained on anticipated terms. Complete financing terms are not in the evidence delivered to CP-2. [C23, C24, C25] | Do not blend transaction financing into Q2 balances or assume transaction support, incremental debt or refinancing execution. | Obtain complete executed financing commitments and definitive transaction documents. |
| G-3 | Missing market evidence | No dated loan or bond quotations, lender pricing indications or current market access evidence are present in the delivered source set. | Refinancing cost, execution probability and instrument-level market access are not assessable. | Obtain dated, instrument-specific market evidence; CP-2 makes no price or spread estimate. |
| G-4 | Subsequent event | Alberta launch on July 13, 2026 occurred after the June 30 reporting date and is not blended into Q2 figures. [C26] | Potential future contribution is not quantified and does not improve historical Q2 results. | Assess in later-period reporting when results are available. |
| G-5 | Subsequent-event coverage | The delivered filing identifies the Alberta launch; the CP-2 evidence set contains no later subsequent-event disclosure through the analysis date. | Later transaction, funding or operating developments cannot be assumed absent. | Update from a later primary filing or supplied source before a definitive refinancing opinion. |
| G-6 | Ownership and group structure | Public listing and a related-party lease are documented, but the delivered materials do not establish current beneficial ownership or a complete post-merger group structure. [C31, C32] | Sponsor behavior, control and creditor alignment are not inferred. | Obtain current ownership and transaction structure records. |
| CF-2 | Amendment sequence | The Fourth Amendment states a higher Term B margin; the later Fifth Amendment restates the Term B margin at a lower level. This is a dated amendment sequence, not a silent source conflict. [C33, C34] | Use the later disclosed amendment for historical pricing chronology; verify any later operative terms before a refinancing calculation. | Confirm the complete current amendment chain through CP-4 and current financing documents. |

## QA Validation

- **Identity and lineage:** PASS — CP-2, CZR, Q2 2026, analysis date, run ID and accepted CP-0/CP-1 lineage match the supplied invocation.
- **Source gate:** RESTRICTED — current and audited primary filings plus executed financing documents are present; market and full transaction-financing evidence remain absent.
- **Workflow coverage:** PASS WITH LIMITATIONS — company description, ownership, revenue, cost and capex, Porter, PEST, SWOT, strengths and weaknesses, financial profile, outlook, downside scenario, materiality, issuer matrix, monitoring and overall view are represented.
- **Register completeness:** PASS — T2.1, T2.7, T2.10, T2.11 and T2.12 are present with required columns and minimum rows; CP-MODEL interface table is tagged and includes ranked strength and weakness rows.
- **Evidence and locator discipline:** PASS WITH LIMITATIONS — material sourced claims carry citation markers; the debt-basis difference, absent refinancing evidence and source limitations remain explicit.
- **Metric and null discipline:** PASS WITH LIMITATIONS — no FCF, leverage ratio, covenant headroom, refinancing price or missing numeric value is fabricated; the balance-sheet debt basis is distinguished from debt-note figures.
- **Subsequent events:** PASS — Alberta launch is dated and excluded from Q2 figures; later events not represented in the delivered filing remain a named gap.
- **Confidence and status:** PASS — score 51, Low band and Restricted QA status reflect partial source coverage and material unresolved limitations.
- **Host validation:** Pending after this response. No host validator or completeness-check result is asserted.
