---
module_id: "CP-2"
module_name: "FundamentalCreditSynthesizer"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "EARNINGS_UPDATE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2-033795bc77858e70"
credit_os_route_node_id: "RN-FULL_CREDIT_32-EARNINGS_UPDATE-04-CP-2"
credit_os_invocation_sha256: "b545e7e62c38fc754f8bc9495521a8e36b1e012ded28fbaf90835f22b16a4a12"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "391239d01ae8de0a192795066295a2f1d36f6c68d683de2a4deb87dac9933ddd"
  - module_id: "CP-1"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "ea255e9e1079d8ca891fe6bddc3797a6b2c6f7acb9652d0bbc4c1ad0af39baad"
  - module_id: "CP-1B"
    run_id: "COS-20261005T055642Z-dff6ac042fa542b69b0b94f1c14a651b"
    period: "Q2 2026"
    sha256: "60266863190da1cb52552ec7b8761bd1f363d2273ef0abd1fe8f8adfc302c823"
confidence_score: 59
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, UPSTREAM_RESTRICTED, DERIVED_CASH_FLOW_AND_HEADROOM_GAPS]
validation_warnings: [MATERIAL_SOURCE_GAPS_RECORDED, NO_CURRENT_MARKET_OR_RATINGS_EVIDENCE, HOST_VALIDATION_FOLLOWS]
downstream_consumers: [CP-2A, CP-2B, CP-2C, CP-2D, CP-2E, CP-3, CP-6, CP-MODEL, CP-5, CP-5A]
---

## Audit Summary

- **Canonical filename:** `CZR_CP-2_20261002.md`.
- **Module status:** Ready with Limitations. The quarterly filing, audited annual filing and issuer release support a full qualitative credit synthesis, but the available evidence does not support a complete normalized FCF, leverage, covenant-headroom or current market assessment.
- **Confidence:** 59 / Low. Scoring inputs are E=82, C=88 and partial source-gate multiplier S=0.7; the formula gives 59.08 before display as an integer. The partial source gate and unresolved material limitations cap the handoff at Restricted.
- **Committee status:** Requires More Work. No formal rating, legal-capacity conclusion, security recommendation or portfolio sizing is made.
- **Reporting perimeter:** Caesars Entertainment, Inc. and consolidated subsidiaries. Q2/H1 2026 interim figures are unaudited; FY2025 audited annual information is context, not a substitute for missing interim cash-flow or quarterly history.
- **Debt basis:** Where debt is discussed as a canonical balance-sheet measure, use current debt plus long-term carrying value. The 10-Q separately presents debt-note face/book totals; preserve rather than conflate those bases [C44].
- **Next analytical need:** Complete the CP-1 derived cash-flow and reconciliation work, obtain current covenant calculations and a complete financing-document set, and update post-quarter event and market evidence before a definitive committee opinion.

## Analysis

### Credit view

Overall, Caesars’ fundamental credit profile is constrained by lower Q2 operating earnings against higher revenue, substantial debt and lease cash demands, and limited visibility into normalized free cash flow and covenant cushion. Consolidated Adjusted EBITDA fell to $920 million from $955 million while revenue rose to $2,993 million from $2,907 million; reported margin declined to 30.7% from 32.9% [C1, C2, C3]. Regional growth and $675 million of H1 operating cash flow provide counterevidence, but Windsor consolidation and event traffic affect comparability while Las Vegas and Digital earnings weakened [C4, C5, C6, C10]. Cash and reported revolver capacity support near-term liquidity, yet debt service, leases and continuing capital expenditure compete for cash [C11, C12, C13, C14, C15]. The primary downside is further discretionary visitation or hold pressure leading to margin and cash-conversion deterioration before refinancing; debt-service concentration rises in 2028–30, while runway and covenant headroom are not calculable from the supplied materials [C19, C22, C37].

**Three decision drivers.** Revenue increased year over year but Adjusted EBITDA and margin declined [C1, C2, C3]. Las Vegas weakness contrasts with Regional growth that partly reflects a changed perimeter and event-related activity [C4, C5]. Liquidity resources are meaningful as reported, but they are not equivalent to free cash after rent, debt service and capex [C11, C12, C13, C14, C15].

### Company description, ownership and group structure

Caesars operates a large North American gaming and hospitality platform: the 10-Q reports 54 owned, leased or managed properties across 20 jurisdictions, alongside casino, hotel, food and beverage, entertainment, racing and digital wagering activities [C7]. Gaming revenue depends on customer visitation, wagering volume and hold, while hotel and other amenities help attract visitors; these are discretionary activities rather than contracted recurring revenues [C8]. Caesars Rewards is a cross-property and digital loyalty mechanism that may support repeat engagement, but the source does not quantify retention, churn or pricing power [C31]. Accordingly, the footprint and brand platform support scale and customer reach, but do not insulate cash flow from visitation, competition or gaming outcomes.

The issuer describes itself as a holding company dependent on subsidiary cash flows, cash on hand and its ability to raise capital [C35]. The filing documents a May 27, 2026 merger agreement under which the company would become a wholly owned subsidiary of Fertitta Gaming if the transaction closes; completion is conditional, and the current ownership outcome is not established by the delivered evidence [C20, C34]. This creates a financial-policy and execution uncertainty: transaction-related management distraction or delayed completion could complicate operating decisions and financing confidence, but no transaction outcome is assumed. The Caesars Virginia facilities are separately associated with Virginia operations, and the filing states CEI does not guarantee those facilities; CP-2 does not extend this fact into a legal-capacity or recovery conclusion [C36].

### Revenue drivers and pricing power

The principal revenue drivers are customer visitation, casino volume and hold, hotel occupancy/rates, and digital wagering. The filing says results are highly dependent on the volume and quality of customers using properties and applications; a reduction in discretionary visits can therefore reduce casino and non-gaming revenues together [C8, C22]. Hold is partly outside management control, and reported typical ranges include 7–11% for sports betting and 3–5% for iGaming; actual hold variation can produce earnings volatility even when handle is stable [C9, C41]. The Q2 evidence shows Las Vegas revenue and Adjusted EBITDA declining, while Regional performance improved on a partly non-comparable basis and Digital Q2 Adjusted EBITDA declined [C4, C5, C6]. Pricing power, customer concentration, renewal rates and customer-level retention are not quantified, so revenue visibility is assessed as moderate rather than durable or contracted.

### Cost structure, margin resilience and cash generation

Property operations carry labor, gaming-tax, marketing, utility, repair, maintenance and rent costs. The company reports ongoing efficiency efforts to manage labor and other costs, but provides no cost-flexibility measure demonstrating how quickly these expenses can fall with lower visitation [C39]. In Q2, increased gaming tax rates in some states and lower sports betting hold contributed to Digital earnings pressure; management also reports higher gaming taxes associated with revenues and jurisdictional tax-rate increases [C6, C40]. This creates operating leverage: if demand weakens, revenue can fall before labor, property upkeep and contractual occupancy costs adjust, compressing cash available for debt service.

Capital spending remains a material cash claim. H1 2026 cash capex was $335 million; management estimated $310–390 million of remaining-2026 expenditure from unrestricted cash, including maintenance, growth/renovation and digital investment [C15]. The Q2 capex schedule reports $167 million for Q2 2026 versus $230 million in Q2 2025 [C38]. H1 operating cash flow was $675 million versus $680 million, and working-capital changes contributed to the comparison [C10]. These figures are not a quarterly FCF calculation: the accepted CP-1 handoff leaves its script-owned FCF and derived KPIs unavailable, so CP-2 does not calculate FCF, conversion, leverage or interest coverage. The source explicitly cautions that Adjusted EBITDA excludes capex, interest, taxes, principal, distributions and lease cash payments; it is not a liquidity measure [C1, C10, C14, C15].

Customer deposits and other deferred revenue rose by $53 million from the start of 2026 to June 30 [C16]. These balances represent customer gaming deposits and advance payments for services not yet provided [C17]. **Evidence → Risk Mechanic → Credit Implication:** higher customer funding can temporarily support working capital, but it carries service, redemption or wager obligations; a demand disruption may weaken the quality of that float and create cash requirements rather than creditor-available surplus. The source does not establish the amount or timing of any resulting cash outflow, so no liquidity adjustment is calculated.

### Market frameworks translated to credit

**Porter’s Five Forces.**

- **Competitive rivalry:** The issuer describes the casino entertainment business as highly competitive [C21]. More rivalry can require reinvestment and marketing to defend visitation, reducing margin and FCF available for debt service.
- **Threat of new entrants:** Online betting expansion and new casino supply are identified as competitive pressures; regulated entry and licensing are material, but the evidence does not quantify entry barriers by market [C21, C43]. New entrants or market openings can increase customer-acquisition expense and weaken property-level contribution.
- **Threat of substitutes:** Caesars competes for discretionary spending with non-gaming resorts, other entertainment and other forms of gaming [C32]. Substitution can reduce visitation or gaming share, pressuring revenue and fixed-cost absorption.
- **Buyer power:** Individual customer concentration and contractual bargaining power are not disclosed. Customers can choose among gaming, lodging and entertainment alternatives; this constrains any conclusion that Caesars can pass through higher costs [C8, C21, C32].
- **Supplier power:** The source documents reliance on third-party technology and service providers for digital access, but does not provide supplier concentration, replacement costs or contract terms [C24]. An outage or a costly replacement could interrupt digital wagering and reduce digital cash earnings; overall supplier bargaining power remains not assessable.

**PEST factors.** Economic conditions matter because casino, hotel and leisure spending is sensitive to downturns, inflation and discretionary-income pressure; lower visits would transmit into property revenues and cash flow [C22]. Political/regulatory factors matter because gaming licenses are required and gaming taxes and fees may change; higher tax burdens or restrictions would reduce margins and refinancing capacity [C23, C43]. Technology is material because digital wagering relies on third-party infrastructure; service interruption or increased platform expense could impair revenue and customer access [C24]. Social factors are not separately assessed beyond customer demand and regulated responsible-gaming context because the delivered evidence does not quantify their incremental financial effect.

**SWOT translated to creditor implications.**

- **Strengths:** multi-property and multi-jurisdiction reach supports operating scale [C7]; Caesars Rewards is designed to link customers across properties and online services [C31]; reported cash and revolver availability provide a current liquidity counterweight [C11, C12].
- **Weaknesses:** Q2 Adjusted EBITDA and margin declined despite revenue growth [C1, C2, C3]; substantial scheduled debt service and lease payments compete with operating cash [C13, C14]; normalized FCF and covenant headroom are not established by the supplied analysis [C10, C15, C18].
- **Opportunities:** higher iGaming handle is a source-reported growth signal, though it does not establish improved earnings conversion [C33]; continued digital legalization and new launches could expand the addressable operating footprint if economics are positive [C28, C42]; sustained Regional performance on a comparable perimeter could offset some Las Vegas weakness [C5].
- **Threats:** discretionary-spending weakness can reduce visitation and non-gaming revenue [C22]; competition and substitutes may require ongoing promotional and capital expenditure [C21, C32]; tax increases or adverse hold variation can compress casino and Digital earnings [C9, C40, C42].

### Key strengths and weaknesses

1. **Liquidity resources:** reported cash and committed borrowing capacity support near-term flexibility; however, these must fund operations, capital requirements, debt service and rent, so they do not establish a long-term liquidity runway [C11, C12, C13, C14, C15].
2. **Multi-channel and geographic platform:** the property portfolio and digital operations provide multiple revenue channels; that breadth may absorb localized shocks, but the current quarter shows distinct regional and channel performance and no quantified customer-retention measure [C4, C5, C6, C7].
3. **Earnings and margin pressure:** Q2 Adjusted EBITDA fell to $920 million from $955 million and margin fell to 30.7% from 32.9%; weaker earnings reduce the operating cushion for fixed financial and lease claims [C1, C3].
4. **High fixed cash claims and refinancing exposure:** remaining-2026 debt service and lease payments are significant, with disclosed debt-service requirements increasing in 2028–30; weaker property contribution can therefore impair liquidity and refinance flexibility [C13, C14, C19].
5. **Financial-data and transaction uncertainty:** normalized FCF, covenant cushion and post-quarter transaction developments are not established in this source pack; creditors cannot confidently translate reported EBITDA into available cash or assess the final ownership and policy implications [C10, C18, C20, C34].

### Financial profile and credit quality

The profile is qualitative because a matched canonical EBITDA, normalized FCF, full covenant calculation and current market evidence are not available in the accepted handoffs. Reported cash and capacity are meaningful, but the company’s own cash-flow statement is H1 rather than a standalone Q2 cash-flow statement, and debt service, lease and capex claims remain material [C10, C11, C12, C13, C14, C15]. The company reported covenant compliance at June 30, 2026; compliance is not a calculation of headroom [C18]. Debt-note totals include face and book-value presentations distinct from balance-sheet carrying value [C44].

The strongest counterargument is that Regional Q2 revenue and Adjusted EBITDA increased, H1 operating cash flow remained positive, and management reported cash and revolving capacity sufficient for the next twelve months and beyond [C5, C10, C11, C12, C29]. It would win if subsequent reports showed continued Regional improvement on a Windsor-consistent basis, stable or recovering Las Vegas and Digital earnings, and cash generation after capex, rent and debt service, accompanied by verified covenant calculations. Until then, the perimeter change, event contribution and incomplete cash-conversion measures reduce conviction.

### Outlook, tailwinds and headwinds

**Short term, 12–24 months:** source evidence supports a cautious, conditional view rather than a forecast. Las Vegas visitation, occupancy and gaming trends weakened in Q2; Regional results improved but included Windsor consolidation and event activity; Digital Adjusted EBITDA declined with lower sports hold and higher taxes [C4, C5, C6]. A stabilizing Las Vegas market and comparable Regional growth would support earnings, while lower discretionary demand, adverse hold, higher taxes or labor costs would reduce margin and liquidity [C22, C39, C40, C41]. Debt and lease payments plus remaining capital expenditure compete for available cash [C13, C14, C15].

**Medium term, 3–5 years:** no management forecast or independent sector benchmark is included. Potential digital expansion and higher iGaming handle are conditional growth supports, but competitive promotions, hold variability, tax changes and technology reliance could absorb incremental revenue [C24, C33, C42]. Debt-service requirements are concentrated in the disclosed 2028–30 schedule, making refinancing dependent on sustained earnings and cash generation, capital-market access and the resolution of the pending merger; no market price, yield or rating evidence is available to assess access [C19, C20].

**Subsequent event:** the 10-Q reports an Alberta mobile sports betting and iGaming launch on July 13, 2026, after the June 30 reporting date. Its financial effects are not quantified and are excluded from Q2 figures [C28]. The delivered evidence does not provide a later update through the analysis date; further post-quarter developments remain a gap.

### Qualitative downside scenario

A source-supported downside begins with weaker discretionary visitation, hotel demand or gaming volume/hold. The first operational break would be lower Las Vegas hotel and non-gaming contribution or lower casino win; Q2 already showed weaker Las Vegas revenue and earnings, while hold is inherently variable [C4, C8, C41, C45]. If lower revenue persists, labor, gaming taxes, maintenance and promotional spending may not decline in step, and property leases remain contractual cash claims [C14, C39, C40]. Lower operating cash conversion would then compete with debt service, lease payments and capital requirements, reducing cash and unused borrowing capacity. The resulting financing consequence would be greater dependence on refinancing as scheduled debt service rises in 2028–30 [C13, C14, C15, C19, C37].

Management could defer or reprioritize discretionary growth and renovation expenditure, but maintenance needs and lease-related obligations limit assumed flexibility; no amount of achievable savings is supplied. A stress outcome is not quantified and liquidity distress is not assumed. Monitor successive reported revenue and margin declines, reduced liquidity, and delayed refinancing. The scenario would be less concerning if Regional gains persisted on a comparable basis and operating cash flow covered capex, rent and debt service without drawing on liquidity; those conditions are not yet demonstrated [C5, C10, C15].

### Overall credit view

Overall, Caesars presents a **not fully assessable** business profile: multi-property scale, customer reach and reported liquidity support the credit, while Q2 margin deterioration, discretionary demand exposure, material debt and lease claims, and unverified cash conversion constrain it [C1, C3, C7, C11, C12, C13, C14]. Cash-flow durability is **not fully assessable** because H1 CFO is reported but matched normalized FCF, quarterly cash flow and covenant headroom are not established [C10, C15, C18]. Refinancing capacity is likely to depend on operating recovery, the availability of capital markets, liquidity preservation and performance against the disclosed maturity schedule; current market and ratings evidence is absent [C19, C29]. The primary downside path is weaker visitation or hold reducing property earnings and cash conversion while debt service, rent and capex remain due. Further analysis requires current financing agreements and covenant calculations, completed CP-1 derived measures, current market/rating evidence and post-quarter transaction updates.

CP-2 Completed. Top Risk: sustained visitation or hold weakness compresses earnings and liquidity ahead of concentrated 2028–30 debt-service requirements.

### Analytical appendix — complete canonical registers

#### T2.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 8ed97f97-6f3e-411f-902d-955cf70fbb90 | CZR_Q2_2026_10Q.txt — Form 10-Q | Primary-Unverified | Q2 and H1 ended June 30, 2026; comparative 2025 | Caesars Entertainment, Inc. and consolidated subsidiaries | Interim statements, segment results, cash, debt, liquidity, covenant status, leases, customer liabilities and subsequent event [C2, C10, C11, C18, C28] | Unaudited interim report; standalone Q2 cash flow and full normalized FCF are not provided in the accepted analytical handoff; full executed financing-document set and current covenant calculations are not included | Principal source for current-period CP-2 business, operating, liquidity and debt-service analysis |
| 99ca7fb0-35f0-4d58-ba54-dc8037e05dbf | CZR_FY2025_10K.txt — Form 10-K | Primary-Unverified | FY2025 and comparative annual periods | Caesars Entertainment, Inc. and consolidated subsidiaries | Audited annual financial statements, business description, competition, risk factors, annual cash flow, debt, lease and operating context [C21, C22, C30, C45] | Annual results do not replace missing Q2 cash-flow or current market data; source text includes a stock-performance graph not used as market evidence | Annual baseline and qualitative sector/business context |
| 4700da60-4659-40e9-812a-9d9d3a2ef533 | CZR_Q2_2026_Earnings_Release.txt — Q2 earnings release | Secondary-Unverified | Q2 and H1 ended June 30, 2026 | Caesars Entertainment, Inc.; consolidated and segment highlights | Headline earnings and segment summaries; cash and borrowing-capacity summary [C1, C11, C12] | Issuer release is corroborative; non-GAAP Adjusted EBITDA is not a liquidity measure and definitions may differ from debt agreements | Corroboration of current-period headline results; not controlling over the 10-Q |

#### T2.7 — Financial Profile Scorecard

| Dimension | Assessment | Credit Rationale |
|---|---|---|
| Scale / market position | Average | 54 properties in 20 North American jurisdictions provide meaningful scale and shock absorption, but scale does not remove sensitivity to visitation and gaming volume [C7, C8]. |
| Competitive advantage | Average | Caesars Rewards links property and online customers and may support repeat engagement; intense competition and unquantified retention prevent a stronger conclusion [C21, C31]. |
| Business diversification | Average | Casino, hotel, food and beverage, entertainment and digital operations broaden revenue sources, but the reported Las Vegas, Regional and Digital results moved in different directions and remain exposed to leisure demand [C4, C5, C6, C7]. |
| Cost and capex flexibility | Weak | Management reports efficiency efforts, but maintenance and growth capex, labor and tax costs, and substantial lease payments constrain the ability to preserve cash in a downturn [C14, C15, C39, C40]. |
| Margin stability | Weak | Q2 consolidated Adjusted EBITDA and margin declined; Las Vegas and Digital weakened, and gaming hold and tax rates can vary [C3, C4, C6, C40, C41]. |
| Free cash flow stability | Not Assessable | H1 CFO is reported, but the accepted handoff does not establish matched normalized FCF or conversion after capex, rent, debt service and other cash uses; no FCF is inferred [C10, C14, C15]. |
| Ability to refinance / access capital markets | Weak | Disclosed debt-service requirements rise across 2028–30, including a larger 2030 requirement; current yields, ratings and market access evidence are absent, preventing a stronger assessment [C19, C37]. |
| Liquidity position | Average | June 30 cash and reported revolver capacity are meaningful, but availability must support operations, debt service, leases and capex; no cash runway or covenant cushion is calculated [C11, C12, C13, C14, C15, C18]. |
| Financial policy and governance | Not Assessable | FY2025 repurchases and the absence of Q2/H1 2026 repurchases are observable, while the pending merger creates a conditional ownership change; a current post-quarter policy outcome is not established [C20, C26, C27, C34]. |

#### T2.10 — Materiality Filter

| Rank | Driver | Evidence | Risk Mechanic | Credit Implication | Direction | Confidence |
|---:|---|---|---|---|---|---|
| 1 | Regional operating support | Q2 Regional revenue and Adjusted EBITDA increased, partly due to Windsor consolidation and event visitation [C5]. | Sustained comparable regional contribution could offset pressure elsewhere and support cash available for fixed claims. | Positive — Revenue Growth | Positive | Medium |
| 2 | Reported liquidity resources | June 30 cash was $965 million and CEI revolving facility capacity net of outstanding balance was $2,130 million [C11, C12]. | Cash and borrowing availability can bridge operating volatility, but remain subject to debt, rent and capex demands. | Positive — Liquidity Improvement | Positive | Medium |
| 3 | Q2 earnings and margin deterioration | Adjusted EBITDA was $920 million versus $955 million; reported margin was 30.7% versus 32.9% [C1, C3]. | Lower earnings reduce the cushion for operating costs, debt service and rent. | Negative — Margin Compression | Negative | High |
| 4 | Fixed debt-service and lease claims | Estimated remaining-2026 debt service was $425 million and VICI/GLPI lease payments were estimated at $687 million [C13, C14]. | Contractual cash demands can absorb liquidity before discretionary investment or deleveraging. | Negative — Liquidity Deterioration | Negative | High |
| 5 | Refinancing concentration and incomplete capacity evidence | The debt-service schedule shows higher requirements in 2028–30; current market and rating evidence are absent [C19, C37]. | Weaker earnings or delayed refinancing could increase reliance on liquidity and market access as maturities approach. | Negative — Refinancing Risk | Negative | Medium |

#### T2.11 — Issuer Matrix

| Business Quality Factor | Assessment | Primary Downside Path | Credit Relevance |
|---|---|---|---|
| Revenue durability | Average | Discretionary demand or property visitation weakens, reducing gaming and hotel revenues. | Volume and customer quality directly affect results; contractual revenue visibility and retention metrics are not supplied [C8, C22]. |
| Margin resilience | Weak | Lower visitation or hold combines with labor, gaming taxes and promotional costs that do not adjust at the same pace. | Q2 EBITDA and margin declined, and Digital earnings were pressured by hold and taxes [C3, C6, C39, C40]. |
| FCF conversion | Not Assessable | Operating cash flow falls short of capex, rent, debt service and other cash claims. | H1 CFO is available, but normalized FCF and conversion are not established; no cash-conversion ratio is inferred [C10, C14, C15]. |
| Liquidity buffer | Average | Operating cash use and scheduled claims reduce cash and usable borrowing capacity. | Cash and revolver capacity support near-term flexibility, but do not demonstrate covenant headroom or runway [C11, C12, C13, C18]. |
| Refinancing capacity | Weak | Delayed or more costly refinancing coincides with scheduled debt-service requirements rising in 2028–30. | Capital-market access, current yield and rating evidence are missing; a definitive refinance conclusion is not possible [C19, C37]. |
| Governance / financial policy | Not Assessable | Merger delay, termination or completion changes ownership context and may distract management or affect operating flexibility. | The merger is conditional; no post-quarter status or resulting financial policy is established [C20, C34]. |

**Primary downside path:** sustained lower visitation or adverse hold weakens property earnings and cash conversion while debt service, rent and maintenance needs continue, reducing liquidity and refinancing flexibility.

#### T2.12 — Monitoring Triggers

| Trigger | Threshold / Signal | Why It Matters | Credit Impact | Source / Limitation |
|---|---|---|---|---|
| Revenue decline | Compare each reported quarter with the same prior-year period; Q2 revenue was $2,993 million versus $2,907 million, but Las Vegas revenue declined. No additional quantitative threshold is available. | Further visitation or gaming-volume deterioration reduces operating contribution and fixed-cost absorption. | Negative — Revenue Decline | 10-Q, pp. 2 and 20; no forecast benchmark supplied [C2, C4]. |
| EBITDA margin pressure | Track issuer-reported margin against Q2 2026 30.7% and Q2 2025 32.9%; no covenant or rating threshold is inferred. | Lower margin reduces the earnings cushion for rent and debt service. | Negative — Margin Compression | 10-Q, p. 18; issuer-reported non-GAAP measure [C3]. |
| FCF deterioration | Monitor reported CFO, capex, cash interest, rent and debt service together; quantitative FCF threshold is not available in the provided materials. | EBITDA alone omits material cash claims and cannot establish debt-service capacity. | Negative — Liquidity Deterioration | H1 CFO and capex are reported, but matched normalized FCF is not established [C10, C14, C15]. |
| Liquidity reduction | Track cash and usable revolver capacity against June 30, 2026 reported levels of $965 million and $2,130 million; no minimum liquidity trigger is provided. | Depletion reduces the buffer for operating volatility, obligations and refinancing execution. | Negative — Liquidity Deterioration | 10-Q, pp. 2 and 22; capacity is not covenant headroom [C11, C12, C18]. |
| Leverage increase | Monitor balance-sheet carrying-value debt and any future matched EBITDA disclosure; no leverage threshold is inferred because canonical leverage is not calculated here. | Rising carrying debt or declining earnings can reduce refinancing flexibility and increase debt-service pressure. | Negative — Leverage Increase | 10-Q debt note and balance sheet; face, book and carrying-value presentations differ [C44]. |
| Refinancing delay | Monitor progress toward the CEI Revolving Credit Facility and Term Loan A January 31, 2028 maturity and the disclosed annual debt-service schedule. | A delay can concentrate refinancing risk and increase dependence on liquidity or market access. | Negative — Refinancing Risk | 10-Q, pp. 9–10; current market evidence is absent [C19, C37]. |
| Sponsor/shareholder action | Track merger approval, regulatory conditions, closing, termination or other material shareholder action; do not assume a completion date. | Ownership change or delay may affect operating flexibility, management attention and financing confidence. | Negative — Refinancing Risk | Merger agreement disclosed in the 10-Q and pending-transaction statement in the release; no later status is supplied [C20, C34]. |
| Sector deterioration | Monitor reported visitation, hold, gaming-tax changes, competitive openings and promotional intensity; quantitative sector threshold is not available in the provided materials. | Sector pressure can reduce revenue, margins and the cash available to service fixed obligations. | Negative — Revenue Decline | Issuer identifies competition, discretionary sensitivity, tax and hold exposure [C9, C21, C22, C40, C42]. |

#### CP-MODEL interface — strengths and weaknesses

<!-- table-id: cp2.cp_model_strengths_weaknesses -->

| direction | rank | label | mechanism | evidence_ids | status | source_id | source_locator | as_of |
|---|---:|---|---|---|---|---|---|---|
| STRENGTH | 1 | Regional earnings counterweight | Reported Regional growth may offset weaker Las Vegas contribution if sustained on a comparable basis; Windsor and event effects temper durability. | E05 | READY | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p. 20 [C5] | 2026-06-30 |
| STRENGTH | 2 | Reported cash and revolver capacity | Cash and borrowing availability can support near-term liquidity, but remain subject to debt service, rent and capex demands. | E11; E12 | READY | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 2, 22 [C11, C12] | 2026-06-30 |
| WEAKNESS | 1 | Q2 earnings and margin contraction | Lower Adjusted EBITDA and margin reduce cash-flow cushion against fixed obligations. | E01; E03 | READY | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 16, 18 [C1, C3] | 2026-06-30 |
| WEAKNESS | 2 | Debt service and lease burden | Debt service, lease payments and capex compete for liquidity and limit downside cash flexibility. | E13; E14; E15 | READY | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q p. 22 [C13, C14, C15] | 2026-06-30 |
| WEAKNESS | 3 | Refinancing and cash-conversion uncertainty | Higher scheduled debt service in 2028–30 coincides with unavailable normalized FCF and current market evidence. | E19; E37 | READY | 8ed97f97-6f3e-411f-902d-955cf70fbb90 | 10-Q pp. 9–10 [C19, C37] | 2026-06-30 |

#### CP-MODEL downstream readiness

<!-- table-id: cp2.downstream_readiness -->

| downstream_module | readiness | basis | limitation | recommended_action |
|---|---|---|---|---|
| CP-MODEL | BLOCKED | The accepted CP-1 and CP-1B handoffs state that required model-period history, calculations and reconciliations remain incomplete. | No substituted leverage, FCF, or missing-quarter value is inferred in CP-2. | Complete the governed upstream calculations, reconciliations and required quarterly history before model use. |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| Reported Q2 Adjusted EBITDA comparison | [C1] | CZR_Q2_2026_Earnings_Release.txt | 1 |
| Revenue and margin comparisons | [C2, C3] | CZR_Q2_2026_10Q.txt | 2, 18 |
| Las Vegas decline and Regional counterevidence | [C4, C5] | CZR_Q2_2026_10Q.txt | 20 |
| Caesars Digital Q2 earnings pressure | [C6] | CZR_Q2_2026_10Q.txt | 21 |
| Property footprint and demand drivers | [C7, C8] | CZR_Q2_2026_10Q.txt | 6, 18 |
| Gaming hold variability | [C9, C41] | CZR_Q2_2026_10Q.txt | 18 |
| H1 operating cash flow | [C10] | CZR_Q2_2026_10Q.txt | 22 |
| Cash, revolver capacity and management liquidity statement | [C11, C12, C29] | CZR_Q2_2026_10Q.txt | 2, 22 |
| Remaining-2026 debt service, leases and capex | [C13, C14, C15] | CZR_Q2_2026_10Q.txt | 22 |
| Customer-deposit trend and obligation | [C16, C17] | CZR_Q2_2026_10Q.txt | 11 |
| Reported covenant compliance | [C18] | CZR_Q2_2026_10Q.txt | 10 |
| Annual debt-service maturities and facility maturity | [C19, C37] | CZR_Q2_2026_10Q.txt | 9–10 |
| Proposed merger and conditional ownership context | [C20, C34] | CZR_Q2_2026_10Q.txt; CZR_Q2_2026_Earnings_Release.txt | 5; 2 |
| Competition and substitutes | [C21, C32] | CZR_FY2025_10K.txt | 3 |
| Discretionary spending sensitivity | [C22] | CZR_FY2025_10K.txt | 9 |
| Gaming tax exposure and licensing | [C23, C43] | CZR_FY2025_10K.txt | 4 |
| Digital third-party infrastructure dependence | [C24] | CZR_FY2025_10K.txt | 12 |
| Variable-rate borrowing exposure | [C25] | CZR_Q2_2026_10Q.txt | 23 |
| FY2025 repurchase and 2026 no-repurchase disclosures | [C26, C27] | CZR_FY2025_10K.txt; CZR_Q2_2026_10Q.txt | 23; 23 |
| Alberta subsequent event | [C28] | CZR_Q2_2026_10Q.txt | 17 |
| FY2025 audited financial statements | [C30] | CZR_FY2025_10K.txt | 28 |
| Caesars Rewards and customer cross-property linkage | [C31] | CZR_FY2025_10K.txt | 4 |
| iGaming handle comparison | [C33] | CZR_Q2_2026_10Q.txt | 20 |
| Holding-company structure and Virginia facility perimeter | [C35, C36] | CZR_Q2_2026_10Q.txt | 11, 22 |
| Q2 capex and labor efficiency evidence | [C38, C39] | CZR_Q2_2026_10Q.txt | 16, 19 |
| Gaming tax-rate pressure | [C40] | CZR_Q2_2026_10Q.txt | 19 |
| Digital hold and promotion risk | [C42] | CZR_Q2_2026_10Q.txt | 21 |
| Debt face/book total basis distinction | [C44] | CZR_Q2_2026_10Q.txt | 9 |
| FY2025 Las Vegas trend | [C45] | CZR_FY2025_10K.txt | 21 |

## Source Registry

The complete source register is T2.1 in the analytical appendix. The Q2 Form 10-Q is the principal current-period source; the audited FY2025 Form 10-K supplies annual and business-risk context; the Q2 earnings release corroborates reported highlights. The 10-Q and 10-K text extractions have stated visual-content limitations in the accepted CP-0 handoff; no map or stock-performance-graph values are used. CP-1 and CP-1B are accepted same-run upstream handoffs with Restricted status; their stated limitations on normalized FCF, derived KPIs, covenant calculations and model readiness are retained rather than replaced with estimates.

## Gaps & Conflicts

| Gap / conflict | Finding and effect |
|---|---|
| Debt definition and perimeter | The 10-Q debt note reports total debt on face and book bases, while the balance sheet separately reports current and long-term debt. These are not interchangeable. The debt metric used by CP-2 follows current plus long-term balance-sheet carrying value; no gross-principal leverage ratio is used [C18, C44]. |
| Adjusted EBITDA versus cash flow | Adjusted EBITDA is issuer-defined and does not include all cash claims. H1 CFO is available, but quarterly CFO, normalized FCF and cash conversion after leases and debt service are not established; these ratios remain Not Calculable from Provided Materials [C10, C13, C14, C15]. |
| Covenant compliance versus capacity | The filing reports covenant compliance at June 30, 2026, but the delivered evidence does not provide a calculated headroom measure. Compliance is not treated as evidence of cushion [C18]. |
| Segment comparability | Regional growth includes Caesars Windsor beginning March 3, 2026, plus event-related visitation and investment effects; a same-perimeter recast is not supplied [C5]. |
| Current market, ratings and financing documents | No current price/yield, ratings-agency evidence or complete executed financing-document set is included in the delivered source pack. Market access, covenant headroom and detailed legal-term conclusions are therefore limited. |
| Subsequent events | The July 13, 2026 Alberta launch is separately flagged and excluded from Q2 figures. No later update through the analysis date is supplied; current merger and other post-quarter status remains unverified [C20, C28, C34]. |
| Digital supplier exposure | Third-party technology dependence is disclosed, but supplier concentration, replacement terms and outage exposure by provider are not quantified [C24]. |
| Ownership and policy | The merger agreement is conditional and no closing, termination or resulting financial-policy outcome is established by the delivered evidence [C20, C34]. |

Unresolved material evidence questions are retained as gaps; no CP-DR research brief was delivered with this module, so no research request is made. These limitations reduce confidence and support Restricted status.

## QA Validation

- **Identity and lineage self-review:** CP-2, CZR, Q2 2026 and analysis date match the host-owned front matter. Same-run CP-0, CP-1 and CP-1B lineage is preserved exactly.
- **Canonical structure self-review:** Filename derives as `CZR_CP-2_20261002.md`; the six required H2 headings appear once and in order. Analysis opens with `### Credit view` and a conclusion-first view before any table.
- **Workflow coverage self-review:** Company and ownership, revenue, costs, capital intensity/FCF, Porter, PEST, SWOT, strengths/weaknesses, financial profile, outlook, downside, materiality, issuer matrix, triggers and overall view are represented.
- **Register self-review:** T2.1, T2.7, T2.10, T2.11 and T2.12 are present with declared columns and required minimum rows. The CP-MODEL strengths/weaknesses projection is tagged and includes at least one independently ranked strength and weakness; the downstream readiness row names CP-MODEL.
- **Evidence and null discipline:** Material sourced claims include evidence markers with locators. No unsupported numeric stress case, leverage ratio, FCF, covenant headroom, market price, rating or merger outcome is inferred. Source gaps and the debt-basis distinction remain explicit.
- **Confidence and status:** 59 / Low; qa_status Restricted; committee_status Requires More Work. Restrictions reflect material evidence and calculation limitations.
- **Host validation:** Host validation and completeness checks follow this answer. No host validator, confidence script, or completeness-check output is asserted.