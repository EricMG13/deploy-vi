---
module_id: "CP-2"
module_name: "FundamentalCreditSynthesizer"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2-8a01c55a15aeedef"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-07-CP-2"
credit_os_invocation_sha256: "b32864611d2b673274509ea21e07b554211f2f5e6945b581d3b9cd4457ff96db"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
  - module_id: "CP-1A"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "6a269cb32ad5fd9b711677aaf183c2d1a6c81017a92b0233107694e1bc9dfca8"
  - module_id: "CP-1B"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "339805d18ef63ec93786562d12f97a9813c148d2b8eadbc202bc3ffe209078a6"
  - module_id: "CP-1D"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "14f82d3ec8922f3c8a7e25f5400cedd84f4d2af4e4cc9184c73b2a85b4392cf2"
  - module_id: "CP-1C"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "9d1b44137d4a4a3c4d7a7b2b4da416edc0fc65ec961a8c82289b3f8ec5e7fcf0"
confidence_score: 55
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - SOURCE_LIMITED_NOT_COMMITTEE_READY
  - NO_POST_Q2_2026_FINANCIALS
  - NO_COMPLETE_CURRENT_CREDIT_AGREEMENT_OR_SECURITY_PACKAGE
  - CP_MODEL_LESS_THAN_FOUR_COMPLETE_QUARTERS
validation_warnings:
  - FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED
  - CURRENT_COVENANT_HEADROOM_NOT_DISCLOSED
  - Q2_CASH_FLOW_NOT_REPORTED_DISCRETELY
  - QUALITY_ADJUSTED_EBITDA_UNRESOLVED
  - PEER_SET_LIMITED_AND_NOT_FULLY_ALIGNED
downstream_consumers: [CP-2A, CP-2B, CP-2C, CP-2D, CP-2E, CP-3, CP-5, CP-5A, CP-6, CP-MODEL]
---

## Audit Summary

**Canonical filename:** `CZR_CP-2_20261002.md`. CP-2 is **Ready with Limitations**; confidence is 55/100 (Low), QA status Restricted, and committee status Requires More Work. The accepted CP-0 and CP-1 artifacts match this run, issuer and reporting period; CP-1A, CP-1B, CP-1D and CP-1C are also accepted same-run inputs. Their restrictions remain in force: the latest financial statements end June 30, 2026, the full current credit agreement and security package are not retained, covenant headroom is not disclosed, and peer evidence is limited. This synthesis uses the June 30 statements as period-end evidence, not as October-current data. It does not infer covenant capacity, make a security recommendation, or assess legal capacity. Host validation follows this response; no host validation result is claimed.

## Analysis

### Credit view

Caesars has substantial operating scale across casino, hotel, food-and-beverage and digital wagering, but its cash generation remains exposed to discretionary demand, gaming hold and fixed debt and lease claims. H1 2026 revenue increased 2.8% year over year to $5.863 billion while Adjusted EBITDA declined 1.7% to $1.807 billion; Q2 revenue rose 3.0% while Adjusted EBITDA fell 3.7%. [C3, C4] The strongest support is broad property/channel reach and reported liquidity of $2.928 billion at June 30; the weakest material dimension is durable free cash flow after capex, cash interest and rent. [C2, C9, C10, C11, C12] The principal downside path is visitation or hold weakness reducing EBITDA and operating cash, while rent and debt service persist, leading to revolver reliance and greater refinancing sensitivity. Missing later-period accounts, covenant headroom and complete financing documents restrict conviction.

#### Decision drivers

- **Support:** 52 domestic properties across 18 states, with casino, hospitality and digital wagering operations, provide multiple sources of activity, though not immunity from common discretionary-demand or gaming-cycle risk. [C1, C2]
- **Constraint:** H1 and Q2 revenue growth did not translate into Adjusted EBITDA growth; Las Vegas weakened, and Q2 digital results faced lower sports hold and higher gaming tax rates. [C3, C4, C5, C8]
- **Liquidity / fixed claims:** June 30 liquidity is a reported snapshot, while FY2025 disclosures estimate $1.4 billion of VICI/GLPI rent for 2026; undrawn capacity is not cash flow or covenant headroom. [C9, C12]

### Company, ownership and operating model

Caesars earns gaming revenue from customer wagers and supplements it with hotels, food and beverage, entertainment, racing, retail and other services. Gaming win depends on volume and retained hold; hotel and non-gaming revenue is exposed to visitation, occupancy and spending. The company reports 52 domestic properties in 18 states and operates a digital business, but the evidence does not supply customer concentration, contract renewal or churn data. The operating model therefore offers breadth rather than contracted revenue visibility: lower discretionary demand or unfavorable hold can affect earnings before fixed debt and lease cash needs adjust. [C1, C2, C18]

Caesars was a public company at the latest delivered financial date. On May 27, 2026, it entered a merger agreement under which a Fertitta Gaming subsidiary would merge into Caesars, subject to stated conditions; the Q2 filing reports merger-related transaction costs and identifies the transaction as pending. No post-close capital structure, closing probability or funded sponsor support is assumed. Transaction uncertainty can affect management focus and future financing, but the terms do not change Q2 historical cash or debt figures. [C21, C22]

The company has a history of acquisitions and asset transactions. FY2025 repurchases were $229 million; there were no repurchases in H1 2026. This history supports monitoring of capital allocation and cash retention but is not, by itself, evidence of sponsor extraction or creditor-adverse behavior. Caesars’ $546 million 2025 note redemption was funded with revolver borrowings and proceeds related to the WSOP sale, demonstrating one debt-management transaction rather than a general assurance of future refinancing access. [C23]

### Revenue durability, margin resilience and cash conversion

Gaming remains the principal revenue source. Because casino revenue reflects net win, handle growth alone does not guarantee revenue growth: hold, customer mix, promotional activity and gaming-tax rates matter. H1 Regional and Digital EBITDA increased, but Las Vegas EBITDA fell; this dispersion cushions but does not remove consolidated volatility. [C6, C7, C5]

Costs include labor, gaming taxes, property operations, marketing, technology and capital maintenance. Gaming taxes and payroll can rise while demand weakens, creating operating deleverage; approximately 21,000 employees, or 42% of team members, were covered by collective bargaining agreements at FY2025. The filings identify higher taxes in certain states and lower Q2 sports hold as contributors to digital EBITDA pressure. [C8, C24]

H1 operating cash flow was $675 million, compared with $680 million in H1 2025; PP&E purchases were $335 million. The simple CFO-less-PP&E amount is $340 million, a calculation and not issuer-reported FCF. It excludes debt principal, cash interest, taxes, lease rent and other investing needs. Separately reported H1 cash interest paid for debt was $368 million and rent-related cash interest was $686 million. Thus EBITDA and the proxy are not equivalent to cash available for debt reduction. The causal credit concern is limited residual cash after necessary reinvestment and fixed claims, weakening deleveraging and refinancing flexibility if operating performance softens. [C10, C11]

Customer deposits and other deferred revenue reached $545 million at June 30, 2026. This is operating float associated with customer deposits, unpaid wagers and future goods or services—not debt or ordinary payables. A demand shock, customer withdrawal or service/redemption requirement could reverse some cash benefit. The provided breakdown does not establish the amount immediately refundable or its timing, so no liquidity credit is assigned to it beyond the observed balance. [C20]

### Market and macro frameworks

**Porter — credit-translated.** Competitive rivalry is material: Caesars describes intense competition across casino markets. Lower visitation, discounting or promotional reinvestment can reduce hold and margins, lowering cash available for rent and debt service. [C17] Substitutes include other entertainment, tribal gaming and online betting; substitution can divert visitation or require higher customer-acquisition spending. The company’s own digital operations may offset some channel migration, but digital earnings remain sensitive to hold and tax. [C1, C8] New entrants are constrained by gaming regulation and licensing, but new market openings and legalized online products can increase supply. Buyer power is diffuse across customers but discretionary: consumers can redirect leisure spending, limiting pricing power in downturns. [C18] Supplier power is most relevant through labor, utilities, technology and licensed gaming content; labor costs and collective bargaining can constrain short-term cost flexibility. [C24]

**PEST — material categories.** Economic conditions, inflation and travel costs affect discretionary casino and hospitality spending; lower visitation then pressures gaming, rooms and food-and-beverage cash flow. [C18] Regulatory and tax changes can raise gaming costs, and gaming licensing remains necessary to operate; higher gaming taxes already affected certain digital markets. [C8] Technology enables online betting and iGaming but adds competition, platform costs and hold volatility. The source evidence supports these channels, not a quantified forecast. Social and demographic factors are not independently assessed because the delivered material does not establish a material separate effect beyond discretionary customer behavior.

**Credit-translated SWOT.**

- **Strengths:** broad property and channel footprint; recognized brands and loyalty platform; digital and regional operations can offset localized weakness; reported cash/revolver liquidity at June 30. [C1, C2, C12]
- **Weaknesses:** Adjusted EBITDA declined despite revenue growth; high debt and lease obligations; variable-rate borrowing exposure; discretionary demand and hold volatility. [C3, C4, C9, C19]
- **Opportunities:** sustain Digital handle and Regional contributions; realize returns from recent property investments; lower interest cost if variable rates decline and operating cash is retained. These are conditional possibilities, not forecasts. [C6, C7, C19]
- **Threats:** prolonged Las Vegas visitation pressure; gaming-tax increases or unfavorable hold; wage and operating-cost inflation; regulatory delay or transaction uncertainty. [C5, C8, C18, C21]

### Financial profile assessment

The analysis is qualitative and uses the latest delivered financial information through June 30, 2026. Carrying debt, face principal, financing obligations and lease cash requirements are distinct measures. CP-1 calculates balance-sheet carrying debt of $11.699 billion as current debt plus long-term debt, while the debt note separately reports $11.807 billion of face principal and $11.705 billion of book debt. The differences are preserved rather than silently reconciled. [C13, C14, C15] Reported covenant compliance at June 30 is a positive fact, but no headroom is disclosed; covenant capacity is therefore Not Calculable from Provided Materials. [C16]

The strongest counterargument is the combination of revenue growth, Regional/Digital contribution, reported liquidity and reported covenant compliance. Those facts would strengthen the credit view if sustained in subsequent filings, supported by post-capex/post-rent cash generation and accompanied by lower carrying debt. The counterargument does not presently offset weaker consolidated EBITDA, substantial lease claims or the missing current covenant and operating information.

### Outlook and downside scenario

**Short term (12–24 months):** performance depends on Las Vegas visitation, Regional trends, Digital hold/tax and cost management. Continued revenue growth with falling EBITDA would signal deteriorating conversion; sustained cash generation and debt reduction would improve the outlook. The merger remains a separate event-risk variable and is not assumed to close. [C3, C4, C5, C8, C21]

**Medium term (3–5 years):** the principal credit questions are whether property investment supports durable cash generation, digital operations can earn through competitive tax and promotional pressures, and debt can be refinanced before maturities without sacrificing liquidity. The delivered evidence does not provide a forecast, current rating-agency case or complete financing plan, so medium-term outcomes remain conditional.

**Issuer-specific downside path:** A broad leisure slowdown or increased local competition first reduces customer visitation, hotel occupancy/rates and gaming volumes; unfavorable hold or higher tax and promotional costs can intensify the EBITDA decline. Labor and property costs, cash interest and VICI/GLPI rent do not fall in step. Operating cash then weakens while capex and customer-service obligations remain; liquidity is consumed, revolver reliance may rise, and debt refinancing becomes more market-window-sensitive. The observable sequence is sustained segment revenue/EBITDA deterioration, weaker operating cash relative to capex and fixed payments, and declining cash or revolver availability. No default probability or unsupported stress amount is assigned. [C5, C8, C9, C10, C11, C12]

### Overall credit view

Overall, Caesars presents an adequate but cyclical business profile supported by a large multi-property footprint, several revenue channels and reported liquidity, but credit quality is constrained by declining Adjusted EBITDA despite revenue growth, substantial debt and financing-lease claims, and discretionary demand and hold exposure. Cash-flow durability appears weak-to-adequate because operating cash flow is near flat year over year and the available CFO-less-capex proxy excludes significant interest, rent and principal payments. Refinancing capacity is likely to depend on sustained operating cash generation, market access, interest rates and transaction developments; covenant headroom and post-June conditions are not established. The primary downside path is lower visitation/hold reducing EBITDA and cash while fixed rent and debt service persist, increasing revolver use and refinancing risk. Further analysis requires post-Q2 financials, the complete current credit and security package, current covenant calculations and peer/market evidence. CP-2 Completed. Top Risk: sustained EBITDA and cash conversion pressure against substantial debt and lease obligations.

### Analytical appendix — complete canonical registers

#### T2.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars Entertainment, Inc. Form 10-K | Primary-Verified | FY ended Dec. 31, 2025 | Caesars and consolidated subsidiaries | Audited business, operating, debt, lease and financial information; independent auditor reports fairly presented statements. [C27] | Historical annual baseline; not current to analysis date. | Business risk, annual results, historical debt/lease burden. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Entertainment, Inc. Form 10-Q | Primary-Verified | Q2 and six months ended June 30, 2026 | Caesars and consolidated subsidiaries | Unaudited interim statements, segment performance, debt, liquidity, covenant statement and pending merger update. [C28, C16, C21] | No post-June reporting; no discrete Q2 cash-flow statement or current covenant headroom. | Current-period fundamentals, liquidity and monitoring. |
| e24bf84e-82d3-4167-bd6f-f510b21fdd0e | Fourth Amendment to Credit Agreement | Primary-Verified | May 9, 2024 | Caesars borrower and lenders under CEI Credit Agreement | Prior Term B applicable margins and repricing context. [C26] | Amendment is not the complete current credit agreement. | Historical financing and pricing context only. |
| 41868018-6353-4359-b98f-d9d5d6d11715 | Fifth Amendment to Credit Agreement | Primary-Verified | Nov. 25, 2024 | Caesars borrower and lenders under CEI Credit Agreement | Term B and Term B-1 margin reductions and consent/assignment mechanics. [C27] | Does not provide full current covenants, baskets, security or headroom. | Historical repricing evidence; no legal-capacity conclusion. |
| CP-0 / sha256 e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9 | Accepted SourceReadiness handoff | Upstream accepted; Restricted | Q2 2026; analysis date 2026-10-02 | Caesars source pack | Source coverage, period limitations and gaps. | Not primary issuer evidence; cited upstream markers are not used as this handoff’s citations. | Retain source-limited status and missing-current-data flags. |
| CP-1 / sha256 2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc | Accepted CanonicalDataFoundation handoff | Upstream accepted; Restricted | Q2 2026 | Caesars consolidated financial data | Canonical figures, debt basis, periods and calculations. | Incomplete quarter coverage; no post-Q2 financials; model readiness blocked. | Anchor calculations and preserve definitions. |
| CP-1A / sha256 6a269cb32ad5fd9b711677aaf183c2d1a6c81017a92b0233107694e1bc9dfca8 | Accepted BusinessTransactionFactPack handoff | Upstream accepted; Restricted | Q2 2026 | Caesars and proposed merger parties | Business, acquisition, transaction and ownership facts. | Current ownership, financing package and post-close capitalization incomplete. | Business/ownership context and event monitoring. |
| CP-1B / sha256 339805d18ef63ec93786562d12f97a9813c148d2b8eadbc202bc3ffe209078a6 | Accepted EarningsDelta handoff | Upstream accepted; Restricted | Q2 2026 | Caesars consolidated | Revenue/EBITDA/cash-flow comparisons, subsequent event and conflict register. | H1 tax-bridge dash/zero mismatch; model coverage incomplete. | Period comparisons and monitoring. |
| CP-1D / sha256 14f82d3ec8922f3c8a7e25f5400cedd84f4d2af4e4cc9184c73b2a85b4392cf2 | Accepted EarningsQuality handoff | Upstream accepted; Restricted | Q2 2026 | Caesars consolidated | Add-back recurrence, cash conversion and adjusted-debt assessment. | Quality-adjusted EBITDA unresolved; June operating-lease liability unavailable. | Qualify earnings quality and debt-like fixed claims. |
| CP-1C / sha256 9d1b44137d4a4a3c4d7a7b2b4da416edc0fc65ec961a8c82289b3f8ec5e7fcf0 | Accepted PeerBenchmark handoff | Upstream accepted; Restricted | Q2 2026; market observations Oct. 1, 2026 | Caesars, MGM and PENN | Limited peer operations and last-trade bond observations. | Two peers only; definitions and market data are not fully comparable. | Directional context only; no peer statistical ranking. |

#### T2.7 — Financial Profile Scorecard

| Dimension | Assessment | Credit Rationale |
|---|---|---|
| Scale / market position | Average | FY2025 footprint includes 52 domestic properties across 18 states and approximately 51,400 slots, 2,700 table games and 45,600 rooms; scale diversifies local exposures but does not prevent competitive or demand-driven earnings declines. [C2, C17] |
| Competitive advantage | Average | Brands, loyalty and digital channels complement casino operations, but evidence also identifies intense rivalry and consumer substitution; no quantitative market share, switching-cost or retention data are supplied. [C1, C17, C18] |
| Business diversification | Strong | Casino, hotel, food-and-beverage, regional, Las Vegas and digital channels give multiple operating sources; they remain correlated to leisure spending and gaming regulation, so diversification mitigates rather than removes cyclicality. [C1, C2, C6, C7] |
| Cost and capex flexibility | Weak | Labor, gaming taxes, property operations and ongoing capex constrain rapid cost reduction; H1 PP&E purchases were $335m and rent obligations are substantial. [C8, C11, C12, C24] |
| Margin stability | Weak | Q2 and H1 Adjusted EBITDA declined as revenue rose; Las Vegas weakness and Digital tax/hold pressure expose margins to visitation, gaming outcomes and regulation. [C3, C4, C5, C8] |
| Free cash flow stability | Weak | H1 CFO was $675m and PP&E purchases $335m; cash interest and rent add further cash uses, while issuer-reported FCF is not available in the supplied record. [C10, C11, C12] |
| Ability to refinance / access capital markets | Average | Debt transactions include the 2025 $546m note redemption funded partly through revolver borrowings and asset proceeds, and the 2024 Term B/B-1 repricing. These demonstrate past financing activity, not assured future market access; maturities and current terms require monitoring. [C23, C26, C27] |
| Liquidity position | Average | June 30 cash plus reported available capacity was $2.928bn, providing a buffer at that date; high debt and rent, absent post-June data and unavailable headroom limit the conclusion. [C12, C9, C16] |
| Financial policy and governance | Not Assessable | Public filings and a pending merger agreement provide some transparency, but post-close capitalization, current lender reporting, full legal documents and subsequent transaction status are unavailable; no sponsor support or legal capacity is inferred. [C21, C22, C28] |

#### T2.10 — Materiality Filter

| Rank | Driver | Evidence | Risk Mechanic | Credit Implication | Direction | Confidence |
|---:|---|---|---|---|---|---|
| 1 | Consolidated EBITDA contraction despite revenue growth | Q2 revenue rose to $2,993m while Adjusted EBITDA fell to $920m; H1 EBITDA fell to $1,807m. [C3, C4] | Lower earnings conversion reduces cash available after fixed debt and lease claims. | Negative — Margin Compression | Negative | High |
| 2 | Large financing and rent burden | FY2025 filing estimates 2026 VICI/GLPI rent of approximately $1.4bn, in addition to reported debt. [C9] | Fixed payments persist through operating weakness and limit discretionary cash. | Negative — Refinancing Risk | Negative | High |
| 3 | Discretionary demand, competition and hold volatility | Company discloses intense competition and sensitivity of leisure spending to downturns/inflation; Las Vegas visitation and Q2 Digital hold/tax pressures are reported. [C5, C8, C17, C18] | Lower visitation/hold can reduce revenue and EBITDA before costs and rent reset. | Negative — Revenue Decline | Negative | High |
| 4 | H1 revenue growth | H1 revenue increased to $5,863m from $5,701m. [C3] | Continued growth can support earnings and liquidity if retained as margin and cash. | Positive — Revenue Growth | Positive | High |
| 5 | Reported liquidity and covenant compliance at June 30 | Reported cash/revolver liquidity totaled $2.928bn; company reported covenant compliance at June 30. [C12, C16] | Available liquidity can absorb volatility, but is dated and does not establish covenant cushion. | Positive — Liquidity Improvement | Positive | Medium |
| 6 | Variable-rate debt exposure | FY2025 filing reports $6.1bn of variable-rate debt. [C19] | Higher benchmark rates increase cash interest and reduce residual cash. | Negative — Leverage Increase | Negative | High |
| 7 | Sequential reduction in carrying debt | Balance-sheet current portion and long-term debt imply $11.699bn at June 2026 versus $11.784bn at FY2025 year-end; financing obligations are separate. [C13, C14] | A modest carrying-debt decline supports deleveraging, but does not offset large fixed obligations. | Positive — Deleveraging | Positive | Medium |

#### T2.11 — Issuer Matrix

| Business Quality Factor | Assessment | Primary Downside Path | Credit Relevance |
|---|---|---|---|
| Revenue durability | Average | Leisure downturn or local competition lowers visits, gaming volume, hotel activity and non-gaming spend; weaker retained win reduces revenue. | Revenue growth in H1 is supportive, but revenue is discretionary and affected by hold and customer behavior. [C3, C17, C18] |
| Margin resilience | Weak | Lower visitation/hold plus gaming-tax, labor and marketing pressure causes EBITDA to fall faster than revenue. | Q2 and H1 EBITDA declines despite revenue growth reduce debt-service cushion. [C4, C5, C8] |
| FCF conversion | Weak | Lower EBITDA and continuing capex, cash interest and rent reduce cash available for debt repayment. | The H1 CFO-less-capex proxy is not free cash after fixed claims; conversion requires monitoring. [C10, C11, C12] |
| Liquidity buffer | Average | Operating weakness or customer-fund outflow consumes cash and revolver availability. | Reported June liquidity offers a buffer, but is dated and does not establish covenant headroom. [C12, C16, C20] |
| Refinancing capacity | Average | Weaker EBITDA, higher variable rates or delayed transaction developments reduce financing flexibility. | Past redemption/repricing shows prior financing activity; future access is not assured. [C19, C23, C26, C27] |
| Governance / financial policy | Not Assessable | Merger delay or changed control could affect capital allocation, financing and creditor alignment; complete post-close terms are absent. | Monitor transaction status; do not infer sponsor willingness, legal capacity or pro forma support. [C21, C22] |

Primary downside path: a demand or hold shock reduces segment EBITDA and operating cash while rent, debt service and necessary capex persist, increasing liquidity use and refinancing sensitivity.

#### T2.12 — Monitoring Triggers

| Trigger | Threshold / Signal | Why It Matters | Credit Impact | Source / Limitation |
|---|---|---|---|---|
| Revenue decline | Quantitative threshold not available in provided materials; monitor reported YoY revenue and gaming/visitation trends for consecutive deterioration. | Lower visitation and hold reduce casino and hotel contribution. | Sustained decline pressures EBITDA and cash available for debt service. [C3, C5, C18] | Q2 2026 is latest financial period; no post-June results supplied. |
| EBITDA margin pressure | Quantitative threshold not available in provided materials; monitor Adjusted EBITDA falling while revenue is stable/growing, and segment margin changes. | Signals adverse mix, costs, taxes or hold before liquidity necessarily falls. | Persistent compression weakens fixed-charge coverage and refinancing flexibility. [C3, C4, C5, C8] | Issuer Adjusted EBITDA is non-GAAP; no covenant EBITDA bridge in this evidence set. |
| FCF deterioration | Quantitative threshold not available in provided materials; monitor CFO relative to capex, cash debt interest, rent interest, taxes and debt principal. | CFO-less-capex is not FCF and does not capture rent or debt service. | Lower post-fixed-claim cash increases reliance on liquidity and refinancing. [C10, C11, C12] | No discrete Q2 cash flow or issuer-reported FCF supplied. |
| Liquidity reduction | Quantitative threshold not available in provided materials; monitor cash, revolver availability, draws, restricted cash and customer-deposit movements. | A shrinking buffer reduces ability to absorb operating volatility and transaction delays. | Increased revolver use can increase leverage and reduce refinancing options. [C12, C20, C21] | $2.928bn is a June 30 snapshot, not October-current availability. |
| Leverage increase | Quantitative threshold not available in provided materials; monitor carrying debt, financing obligations, lease claims and LTM EBITDA on consistent bases. | Debt/lease claims can rise while EBITDA falls. | Higher fixed claims constrain debt service and refinancing. [C13, C14, C15] | Face, book, carrying debt and financing obligations are distinct measures. |
| Refinancing delay | Quantitative threshold not available in provided materials; monitor progress on refinancing, maturities, revolver reliance and updated debt-service schedules. | Delay can expose the issuer to tighter markets and higher cost. | Refinancing risk rises if cash generation or liquidity weakens before maturities. [C23, C27] | Complete current credit agreement and future financing plans are not supplied. |
| Sponsor/shareholder action | Quantitative threshold not available in provided materials; monitor merger approvals/status, financing commitments, distributions, repurchases and material asset transactions. | Ownership change or cash distributions can alter liquidity and creditor alignment. | Adverse changes may divert cash or change capital structure; do not infer support. [C21, C22, C23] | Merger remained pending in Q2; no final post-close capitalization. |
| Sector deterioration | Quantitative threshold not available in provided materials; monitor gaming-tax changes, local openings, leisure spending, hold and competitive promotional intensity. | Competition and tax/hold pressure can affect several segments concurrently. | Sector deterioration can weaken EBITDA, cash flow and refinancing capacity. [C8, C17, C18] | No external forward market or sector forecast supplied. |

#### cp2.cp_model_strengths_weaknesses — CP-MODEL Strengths and Weaknesses

<!-- table-id: cp2.cp_model_strengths_weaknesses -->

| direction | rank | label | mechanism | evidence_ids | status | source_id | source_locator | as_of |
|---|---:|---|---|---|---|---|---|---|
| STRENGTH | 1 | Broad property and channel footprint | Multiple property, hospitality and digital activities diversify local revenue sources, though shared leisure exposure remains. | C1; C2 | READY | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K pp. 2, 18 | 2025-12-31 |
| STRENGTH | 2 | Reported liquidity and covenant compliance | June cash/revolver capacity and reported compliance provide a dated liquidity/compliance buffer; neither establishes headroom. | C12; C16 | READY | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 22–23 | 2026-06-30 |
| STRENGTH | 3 | Regional and H1 Digital contribution | Segment EBITDA gains can offset some Las Vegas weakness and support consolidated earnings. | C6; C7 | READY | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 20–21 | 2026-06-30 |
| WEAKNESS | 1 | Adjusted EBITDA contracted despite revenue growth | Lower earnings conversion leaves less cash for debt service, capex and rent. | C3; C4 | READY | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 2, 16 | 2026-06-30 |
| WEAKNESS | 2 | Substantial debt and lease cash claims | High carrying debt plus significant lease/rent obligations consume cash and constrain deleveraging. | C9; C13; C14; C15 | READY | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | 10-K p. 23; 10-Q pp. 2, 9 | 2026-06-30 |
| WEAKNESS | 3 | Cash conversion is not established after all fixed claims | H1 CFO less PP&E purchases is only a proxy; interest and rent remain additional outflows. | C10; C11; C12 | READY | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 4–5; 10-K p. 23 | 2026-06-30 |
| WEAKNESS | 4 | Consumer, competition and hold sensitivity | Demand weakness or unfavorable hold/tax reduces EBITDA while many costs and lease obligations remain. | C5; C8; C17; C18 | READY | 5c51af90-71cc-4023-8aea-4523ce9f2428 | 10-Q pp. 20–21; 10-K pp. 8–9 | 2026-06-30 |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| Gaming as primary revenue source and business channels | [C1] | Caesars FY2025 Form 10-K | 2 |
| Property footprint and scale | [C2] | Caesars FY2025 Form 10-K | 18 |
| Q2/H1 consolidated revenue | [C3] | Caesars Q2 2026 Form 10-Q | 2 |
| Q2/H1 Adjusted EBITDA | [C4] | Caesars Q2 2026 Form 10-Q | 16 |
| Las Vegas performance deterioration | [C5] | Caesars Q2 2026 Form 10-Q | 20 |
| Regional Adjusted EBITDA comparison | [C6] | Caesars Q2 2026 Form 10-Q | 20 |
| Digital H1 trend | [C7] | Caesars Q2 2026 Form 10-Q | 21 |
| Digital tax and hold pressures | [C8] | Caesars Q2 2026 Form 10-Q | 21 |
| FY2026 VICI/GLPI lease-payment estimate | [C9] | Caesars FY2025 Form 10-K | 23 |
| H1 operating cash flow | [C10] | Caesars Q2 2026 Form 10-Q | 4 |
| H1 PP&E purchases | [C11] | Caesars Q2 2026 Form 10-Q | 4 |
| June reported cash and available borrowing capacity | [C12] | Caesars Q2 2026 Form 10-Q | 22 |
| Current portion of debt | [C13] | Caesars Q2 2026 Form 10-Q | 2 |
| Long-term debt carrying value | [C14] | Caesars Q2 2026 Form 10-Q | 2 |
| Face-value debt-note total | [C15] | Caesars Q2 2026 Form 10-Q | 9 |
| Covenant compliance statement | [C16] | Caesars Q2 2026 Form 10-Q | 23 |
| Competitive intensity | [C17] | Caesars FY2025 Form 10-K | 8 |
| Discretionary-spending sensitivity | [C18] | Caesars FY2025 Form 10-K | 9 |
| Variable-rate debt exposure | [C19] | Caesars FY2025 Form 10-K | 27 |
| Customer-deposit/deferred-revenue balance | [C20] | Caesars Q2 2026 Form 10-Q | 11 |
| Merger-related costs in Q2/H1 | [C21] | Caesars Q2 2026 Form 10-Q | 6 |
| Merger agreement execution and parties | [C22] | Caesars Q2 2026 Form 10-Q | 5 |
| 2025 note redemption funding | [C23] | Caesars FY2025 Form 10-K | 23 |
| Collective bargaining coverage | [C24] | Caesars FY2025 Form 10-K | 6 |
| Prior covenant leverage threshold, not current headroom | [C25] | Caesars FY2025 Form 10-K | 24 |
| Prior Term B margin before the 2024 fifth amendment | [C26] | Fourth Amendment to Credit Agreement | 1 |
| Term B / B-1 margin after fifth amendment | [C27] | Fifth Amendment to Credit Agreement | 1 |
| Interim reporting period identity | [C28] | Caesars Q2 2026 Form 10-Q | 1 |
| Audited annual financial statement opinion | [C29] | Caesars FY2025 Form 10-K | 28 |

## Source Registry

The evidence base consists of the FY2025 Form 10-K, the Q2 2026 Form 10-Q, the fourth and fifth amendments to the CEI Credit Agreement, and accepted same-run CP-0, CP-1, CP-1A, CP-1B, CP-1D and CP-1C artifacts. The primary filings establish reported results and period-end balances; CP-1 supplies the governed carrying-debt and calculation basis; CP-1B supplies validated comparisons but flags the source-dash/CP-1-zero tax-bridge mismatch; CP-1D leaves quality-adjusted EBITDA unresolved; CP-1C supplies a limited, unaligned peer screen. All upstream lineage is retained in front matter and T2.1. The evidence does not include financial statements after June 30, 2026, a complete current credit/security package, current covenant calculations, or a complete peer/market dataset. [C3, C4, C15, C16, C28, C29]

## Gaps & Conflicts

- **Period gap:** June 30, 2026 is the latest financial reporting date in the delivered set; no post-Q2 financial update is provided. [C28]
- **Debt basis:** Balance-sheet carrying debt and debt-note face/book figures differ. Current debt is carried using CP-1’s defined balance-sheet basis; face principal and financing obligations remain separate. [C13, C14, C15]
- **Cash conversion:** No discrete Q2 cash-flow statement or issuer-reported canonical FCF is available. The $340 million H1 CFO-less-PP&E amount is a proxy only; rent, interest, taxes and principal remain separate cash claims. [C10, C11, C12]
- **Covenants:** Compliance is reported at June 30, but headroom is not. A covenant threshold described in the FY2025 report is not a substitute for a current calculation. [C16, C25]
- **Earnings quality:** CP-1D rejects recurring impairment and stock-compensation exclusions as non-recurring, but cannot finalize quality-adjusted EBITDA because the transaction-and-other bucket is not disaggregated; CP-1B also flags an H1 dash/zero bridge mismatch. These remain unresolved upstream limitations.
- **Peer comparison:** MGM and PENN are a two-issuer screen with differing EBITDA, lease and perimeter definitions; last trades are not executable or maturity-matched quotes. No peer averages, EV multiples or ranking are calculated.
- **Transaction:** Merger costs are reported and the agreement was entered into May 27, 2026, but the filing’s Q2 period remains pre-close. Transaction funding and post-close capitalization are not assumed. [C21, C22]

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity and selected-run lineage | Self-checked | Host-owned issuer, period, run, profile and upstream hashes retained. |
| Source gate | Restricted | Primary annual and interim reports plus credit amendments are available; complete current legal, later-period and market materials are not. |
| Workflow coverage | Self-checked | Business, ownership, revenue, costs, FCF, Porter, PEST, SWOT, financial profile, outlook, downside, materiality, issuer matrix and monitoring are represented. |
| Required registers | Self-checked | T2.1, T2.7, T2.10, T2.11, T2.12 and tagged CP-MODEL projection are present with required columns and row counts. |
| Period and definition controls | Self-checked with limitations | Annual, H1, Q2 and period-end values remain distinct; debt carrying value, principal, financing obligations, EBITDA and cash-flow proxy are separately labelled. |
| Citation trace | Self-checked | Each citation marker references an excerpt from the supplied EVIDENCE section; no upstream marker is used as this handoff’s source citation. |
| Null and gap treatment | Self-checked | Unreported Q2 cash flow, current covenant headroom, quality-adjusted EBITDA and peer valuation remain unavailable rather than zero. |
| Confidence score | 55/100 — Low | Evidence is materially sourced, but coverage is partial and current/legal/covenant and quality-adjustment gaps limit confidence; source-gate multiplier and Restricted cap applied. |
| QA and committee status | Restricted / Requires More Work | Not a rating, security recommendation, legal-capacity opinion or position-sizing conclusion. |
| Host validation | Pending | Host validation follows this response; no script output or host finding is claimed. |