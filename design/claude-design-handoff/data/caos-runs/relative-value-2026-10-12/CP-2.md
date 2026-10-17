---
module_id: "CP-2"
module_name: "FundamentalCreditSynthesizer"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2-a879da1642c8c0f6"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-04-CP-2"
credit_os_invocation_sha256: "7c947c292a0df56ec37f19f394de023dd2c93729ab2301f2842bd4dd514cc599"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
  - module_id: "CP-1"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "feb32206df70f6261119dceb61308629455fa9537a6f5305a4d941c2fb2015a9"
  - module_id: "CP-1C"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "42230e82490f199a3a3c30c949a25432faf6c02f6113fbb878e0b50db5f1a42f"
confidence_score: 58
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [INTERIM_UNAUDITED, POST_2024_CREDIT_AMENDMENTS_NOT_ATTACHED, COVENANT_HEADROOM_NOT_CALCULABLE, MERGER_FINANCING_NOT_PROVIDED, ENTITY_CASH_ALLOCATION_MISSING, PEER_PRIMARY_SOURCES_NOT_DELIVERED_TO_CP2]
validation_warnings: [DEBT_BASIS_DIFFERENCES_PRESERVED, LEASE_INTEREST_SEPARATED, WINDSOR_COMPARABILITY_BREAK, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-2A, CP-2B, CP-2C, CP-2D, CP-2E, CP-3, CP-6, CP-5, CP-5A, CP-MODEL]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-2_20261002.md`. Owned object: issuer-level fundamental credit synthesis; schema family: Nested; runtime output: this Markdown handoff. **Module status: Ready with Limitations. Confidence: 58/100, Low; QA: Restricted; committee status: Requires More Work.** The accepted CP-0, CP-1 and CP-1C artifacts match issuer, Q2 2026, run and pinned lineage. CP-1 re-anchors first-half revenue of $5,863 million, issuer Adjusted EBITDA of $1,807 million, operating cash flow of $675 million, and balance-sheet debt of $11,699 million to the supplied filing. [C2, C3, C4, C9, C10] CP-1C provides a definition-limited peer challenge, not verified peer-source evidence in this invocation. The current filing and audited FY2025 filing support a complete but bounded synthesis; missing current credit amendments, covenant inputs and merger financing prevent committee clearance. [C37, C39, C40]

**Own confidence calculation:** Among twelve material assessment claims, eight are directly sourced, two calculated, one an analyst inference and one an unresolved information question: E=85. Forty of fifty assessed source/schema demands are covered: C=80. Partial source gate S=0.7; no additional self-QA penalty P=0. Formula `(0.6×85 + 0.4×80)×0.7 = 58.1`, reported as **58**. Restricted status follows the partial gate; this is not a host-validator result.

## Analysis

### Credit view

Caesars has meaningful operating scale and a reported $2,928 million cash-plus-available-revolver resource, but its first-half 2026 Adjusted EBITDA fell despite revenue growth. [C43, C14, C2, C3] The binding fundamental constraint is cash needed for debt and property leases: first-half cash interest paid for debt was $368 million and rent-related financing-obligation interest was another $686 million. [C6, C7] Lower cash capex supported cash after capex, countering an immediate liquidity-stress thesis, but does not establish durable maintenance flexibility. [C4, C5] A repeat of weak Las Vegas demand and table hold would first pressure property earnings, then the cash cushion available for renovation and refinancing. [C19, C20] The pending Fertitta merger adds a conditional financing question, not a completed change to June debt. [C28, C29] Monitor Las Vegas earnings, operating cash flow, customer-deposit float and documented refinancing progress; contractual headroom remains unquantified.

### Business, structure and operating transmission

**Source Fact → Risk Mechanic → Credit Implication.** At June 30 Caesars operated or managed 54 properties in 20 North American jurisdictions, alongside digital gaming and wagering. [C43] Multiple properties and channels reduce dependence on one location, supporting revenue breadth and debt-service continuity. Gaming remains discretionary: the FY2025 filing identifies new prediction-market competition, while the current filing shows higher digital gaming taxes. [C46, C24] Neither customer concentration nor durable pricing power is quantified in the delivered sources; wagering handle is activity, not revenue. Caesars Digital's first-half iGaming handle rose to $10,205 million from $9,193 million, but Q2 Digital Adjusted EBITDA fell to $68 million from $80 million as increased taxes and lower sports hold affected results. [C22, C23, C24] Digital volume therefore cannot be extrapolated into proportional creditor cash flow.

The parent is publicly traded in the reported period, with a May 27 agreement under which Caesars would become a subsidiary of Fertitta Gaming **if** required approvals and other conditions are met. [C28, C29] This is a possible financial-policy and refinancing discontinuity, not evidence that a take-private has closed. Caesars Virginia is a consolidated 50% venture; its facilities have their own asset support and CEI does not guarantee them. [C43, C42] The filing describes senior-secured guarantees for the main CEI facilities, but collateral value and distribution constraints cannot be converted into a recovery estimate here. [C41] FY2025 disclosed no cash common-stock dividends, and no repurchases occurred in first-half 2026; the unused repurchase authorization and possible merger nevertheless warrant monitoring rather than an assumption of permanent creditor-friendly policy. [C48, C49, C54]

Revenue and margin evidence cut both ways. Q2 Las Vegas Adjusted EBITDA fell $59 million year on year to $410 million, with table-game hold falling to 16.6% from 21.1%; Regional EBITDA rose $49 million to $488 million. [C19, C20, C21] **Analyst Judgement:** geographic offset mitigates a single-market shock but does not fully protect consolidated earnings when Las Vegas weakens. Windsor entered Regional operating results on March 3, so reported Regional improvement is not wholly organic. [C30] The FY2025 workforce included about 21,000 union-covered employees; together with property operating costs, gaming taxes and lease commitments, that limits how quickly cash costs can follow lower visitation. [C45, C24, C16] Digital reliance on outside technology and verification providers adds service-disruption exposure that can interrupt wagering and damage cash generation. [C51]

### Cash conversion, liquidity and refinancing

**Calculation; USD millions, consolidated, June 30 unless stated.** Current balance-sheet debt $114 plus long-term debt $11,585 equals canonical carrying debt **$11,699**. Less $965 cash and equivalents, excluding restricted cash, gives **$10,734 net debt**. [C9, C10, C8] The note separately presents $11,807 face debt and $11,705 book debt; the face-to-canonical difference is $108, and separately displayed revolver charges account for the $6 book-to-balance-sheet difference. Neither face amount nor $13,157 of separately classified long-term financing obligations is silently added to canonical debt. [C11, C12, C13] Those financing obligations remain highly material to fixed cash charges.

First-half CFO of $675 less $335 cash property/equipment purchases gives **$340 million after-capex cash**, versus $227 million from $680 less $453 a year earlier. [C4, C5] CFO declined $5 million while capex fell $118 million: lower investment, rather than stronger CFO, drove the $113 million improvement. This is **not** a normalized recurring FCF forecast; the filing also reports asset-purchase cash outlays and does not provide a historical maintenance/growth cash-capex split. First-half debt cash interest of $368 million and GLPI/VICI rent-related cash interest of $686 million are separately disclosed cash-cost categories, not deductions to take again from already-reported CFO. [C6, C7] The issuer itself warns its Adjusted EBITDA may differ from debt- or lease-agreement definitions. [C35]

Reported liquidity of $2,928 million is supportive, but conditional facility capacity is not interchangeable with unrestricted parent cash. [C14] For the remainder of 2026, management estimates $425 million debt service, $687 million VICI/GLPI lease payments and $310–390 million capex; these are separately disclosed future requirements, **not** an additive forecast cash deficit. [C15, C16, C17] The disclosed principal schedule rises from $767 million in 2028 to $1,574 million in 2029 and $3,962 million in 2030. [C18] A sustained earnings setback preceding that wall would reduce internal repayment capacity and make market access more important. Rough issuer-adjusted LTM EBITDA, constructed from FY2025 $3,624 million plus first-half 2026 $1,807 million less first-half 2025 $1,839 million, is **$3,592 million**; carrying debt divided by that denominator is approximately **3.26x**, before separately classified financing obligations. [C36, C3, C9, C10] This is expressly **non-contractual**. Reported compliance with 6.50:1 maximum net leverage and 2.0:1 minimum fixed-charge covenants is positive evidence, but actual covenant headroom is **Not Calculable from Provided Materials** without the tested numerator, permitted netting and compliance calculation. [C32, C33, C34, C35]

**Non-debt funding float:** Customer deposits and other deferred revenue increased from $492 million at January 1 to $545 million at June 30; outstanding chips rose from $39 million to $41 million, and Caesars Rewards obligations from $89 million to $92 million. Together the disclosed balances moved from $620 million to $678 million. [C25, C26] These are customer wagering-settlement or future-service obligations, not trade payables or free cash. [C27] Deposit runoff or redemption during a gaming slowdown could consume cash at the same time property earnings weaken; monitor the obligation and its settlement behavior separately from debt leverage.

### Frameworks, outlook and contrary case

**Competitive forces, translated to credit:** rivalry and substitutes matter where online operators and prediction-market products divert discretionary gaming spending; weaker visitation or promotional intensity lowers property contribution before fixed rent adjusts. [C46, C16] Regulated licensing can constrain entrants but also raises compliance costs and requires approvals for a transaction. [C29] Customer choice limits demonstrated pricing power; union labor and essential digital vendors constrain rapid cost substitution. [C45, C51] These mechanisms support closer monitoring of property margin and service continuity, not an unsupported market-share claim.

**PEST credit transmission:** political/regulatory approvals condition the merger and higher digital gaming taxes can absorb wagering growth; economic leisure demand affects Las Vegas hold and occupancy; technological dependence on third-party platforms creates potential operational interruption. [C29, C24, C19, C51] Social or country-wide effects beyond these sourced mechanisms are not independently quantified. **Credit-translated SWOT:** strengths—property breadth, Regional earnings offset, liquidity and positive CFO; weaknesses—fixed lease cash demands, Las Vegas volatility and uncertain maintenance FCF; opportunities—continued iGaming activity and refinancing ahead of 2028–30 maturities, if converted into cash and documented financing; threats—gaming-tax or competitive pressure and transaction delay. [C43, C21, C14, C4, C7, C19, C22, C18, C24, C29] Each opportunity is conditional, not forecast earnings.

**12–24 months:** liquidity and lower first-half capex provide a near-term counterweight, while $425 million remaining-2026 debt service and $687 million projected lease payments make operating-cash durability decisive. [C14, C4, C5, C15, C16] **Three to five years:** the 2028–30 maturity sequence and any still-pending merger financing determine refinancing confidence; no unprovided deal debt is modeled. [C18, C28, C29] The strongest challenge to the negative fixed-charge thesis is management's stated belief that current liquidity and operations can fund needs beyond twelve months, alongside reported covenant compliance and improved after-capex cash. [C53, C34, C4, C5] It would prevail if later CFO remains durable **while** necessary refurbishment is funded and the maturity wall is refinanced on documented terms. If improvement depends on postponing maintenance or drawing the revolver amid weaker EBITDA, conviction in that challenge falls.

### Time-aware downside and overall assessment

A source-grounded downside begins with recurring weaker Las Vegas leisure visitation and table hold, possibly alongside higher digital tax or marketing costs. [C19, C20, C24] First, casino revenue and property contribution soften; next, wage, operating and property-lease cash commitments respond slowly, compressing consolidated EBITDA. Cash after maintenance and customer settlements then narrows; use of the revolver or reduced cash diminishes the cushion ahead of 2028–30 maturities. [C45, C16, C25, C26, C18] Management could reduce discretionary growth capex and pursue refinancing, but the maintenance minimum, debtor-level cash availability and actual covenant cushion are not established here. The observable sequence is repeated Las Vegas hold weakness → declining segment EBITDA and CFO → deposit runoff or facility drawings → delayed refinancing. This does **not** establish impending default.

Overall, Caesars presents an **adequate but financially constrained** business profile supported by operating breadth, Regional offset and reported liquidity, while fixed lease costs and volatility in Las Vegas constrain cash-flow durability. Refinancing capacity depends on sustained after-capex cash generation, transaction outcome and access before the 2028–30 maturities. Peer handoff observations are definition-limited and their underlying peer releases were not delivered to CP-2; no issuer-versus-peer financial ranking or security recommendation follows. Obtain current credit amendments, compliance calculations, debtor-level cash, maintenance capex and transaction financing before upgrading the view. [C39, C40, C18, C35, C29]

**Subsequent event:** Alberta mobile wagering and iGaming launched July 13, 2026, after the June 30 balance sheet; no June revenue, cash or debt adjustment is attributed to it. The May 27 merger agreement was signed **within** Q2, but closing remains conditional after June. [C31, C28, C29]

CP-2 Completed. Top Risk: persistent Las Vegas earnings pressure interacting with fixed lease cash costs before the maturity wall.

### Analytical appendix — complete canonical registers

#### T2.1 — Source Register
| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 439e1450-b5ae-4830-b4c3-3719da918fe3 | Caesars Form 10-Q [C1] | Primary-Unverified | Q2/H1 2026 and 2025; June/December balances | Caesars consolidated | Income, cash flows, debt, liquidity, segments, merger and July event [C2, C4, C11, C28, C31] | Unaudited; supplied text rather than independent original-layout review | Operating, liquidity, maturity and event anchor |
| f991456d-d304-4d03-9648-bcdf899ce7a5 | Caesars FY2025 Form 10-K [C37] | Primary-Unverified | FY2025 with historical comparisons | Caesars consolidated | Audited history, labor and listed credit amendments [C36, C45, C39, C40] | Exhibit index does not supply later amendment text | Annual/LTM base and legal-version gap |
| 1b81ec57-5e7f-4eb7-81bf-b1fbc9d4b2b2 | Incremental Assumption Agreement No. 3 [C38] | Primary-Unverified | February 2024 | CEI borrower and loan parties | Historical incremental-facility and then-conformed agreement | Predates later indexed amendments [C39, C40]; not sole authority for current terms | Version context; CP-4 legal handoff |
| CP-0 accepted handoff | SourceReadiness; matching pinned run | Secondary-Reputable | Q2 2026 | CZR source scope | Source gate, delivery and missing-document inventory | Context, not underlying legal or financial proof | Source and limitation re-anchor |
| CP-1 accepted handoff | CanonicalDataFoundation; matching pinned run | Secondary-Reputable | Q2 2026 | Caesars consolidated | Canonical debt, period construction and definition flags, rechecked against filing [C9, C10, C11, C12] | No contractual EBITDA or debtor-level cash | Financial lineage and downstream model context |
| CP-1C accepted handoff | PeerBenchmark; matching pinned run | Secondary-Reputable | Q2 2026 | CZR and contextual peers | Definition-comparability warning | Underlying MGM/PENN releases not in this CP-2 evidence delivery; no independent peer figures used | Boundary on peer inference; CP-3 handoff |

#### T2.7 — Financial Profile Scorecard
| Dimension | Assessment | Credit Rationale |
|---|---|---|
| Scale / market position | Strong | 54 operated, leased or managed North American properties support geographic breadth; market share is not established. [C43] |
| Competitive advantage | Average | Brand and property channels support repeat engagement, but digital substitution and promotional competition weaken demonstrated pricing power. [C43, C46] |
| Business diversification | Average | Regional EBITDA rose while Las Vegas fell; Windsor's consolidation impairs organic comparison, and consolidated cash still depends on gaming. [C20, C21, C30] |
| Cost and capex flexibility | Weak | Lower capex improved after-capex cash, but property leases and a union-covered workforce constrain rapid reductions; maintenance split is missing. [C5, C16, C45] |
| Margin stability | Weak | Las Vegas Q2 hold and EBITDA deteriorated; gaming tax growth can absorb Digital volume gains. [C19, C20, C23, C24] |
| Free cash flow stability | Average | H1 CFO less property/equipment capex was $340 million versus $227 million, primarily on reduced capex, not stronger CFO. [C4, C5] |
| Ability to refinance / access capital markets | Not Assessable | Scheduled 2028–30 maturities are known, but future financing terms and merger-closing capital structure are absent. [C18, C28, C29] |
| Liquidity position | Average | $2,928 million reported cash plus available capacity counters near-term demands; debtor allocation and actual covenant cushion are unknown. [C14, C15, C16, C34] |
| Financial policy and governance | Average | No first-half repurchases and proposed suspension support near-term cash retention; merger outcome and unused repurchase authorization leave future policy uncertain. [C49, C50, C54] |

#### T2.10 — Materiality Filter
| Rank | Driver | Evidence | Risk Mechanic | Credit Implication | Direction | Confidence |
|---:|---|---|---|---|---|---|
| 1 | Fixed lease and debt cash commitments | H1 cash-interest categories and remaining-year estimates [C6, C7, C15, C16] | Contractual payments persist when gaming earnings decline | Negative — Liquidity Deterioration | Negative | High |
| 2 | Reported liquidity resource | June reported cash-plus-available capacity [C14] | Buffer permits timing flexibility against cash demands, subject to draw conditions | Positive — Liquidity Improvement | Positive | High |
| 3 | Las Vegas earnings exposure | Q2 table hold and segment EBITDA fell [C19, C20] | Gaming-volume and hold shocks flow into EBITDA before fixed rent resets | Negative — Margin Compression | Negative | High |
| 4 | Regional offset | Q2 Regional EBITDA increased [C21, C30] | Additional segment earnings partly absorb Las Vegas weakness, with Windsor comparison qualification | Positive — Revenue Growth | Positive | Medium |
| 5 | Maturity concentration and pending merger | Principal schedule and conditional merger [C18, C28, C29] | Weaker internal cash ahead of larger maturities increases refinancing dependence; deal financing unknown | Negative — Refinancing Risk | Negative | Medium |
| 6 | Reduced first-half cash capex | CFO and property/equipment purchases [C4, C5] | Preserves cash after capex without proving sustainable maintenance spending | Positive — Liquidity Improvement | Positive | Medium |

#### T2.11 — Issuer Matrix
| Business Quality Factor | Assessment | Primary Downside Path | Credit Relevance |
|---|---|---|---|
| Revenue durability | Average | Repeated Las Vegas visitation and hold weakness | Regional offset helps but discretionary gaming revenue can weaken debt-service cash. [C19, C20, C21] |
| Margin resilience | Weak | Gaming taxes and slow-to-adjust property costs | EBITDA falls faster than fixed lease demands under a demand shock. [C24, C16, C20] |
| FCF conversion | Average | Capex reverts while CFO stalls | H1 cash improvement was capex-driven; sustainable creditor cash is unproven. [C4, C5] |
| Liquidity buffer | Average | Deposit runoff and revolver drawings | Reported capacity provides time, but wagering obligations can become cash uses. [C14, C25, C26, C27] |
| Refinancing capacity | Not Assessable | Earnings weakness precedes 2028–30 principal maturities | Transaction financing and post-close debt perimeter remain unresolved. [C18, C28, C29] |
| Governance / financial policy | Average | Change in control alters funding priorities | Current repurchase pause is supportive; future ownership and financing policy are conditional. [C49, C50, C28] |

Primary downside path: persistent Las Vegas earnings pressure reduces after-capex cash and liquidity ahead of larger debt maturities while merger financing remains unresolved.

#### T2.12 — Monitoring Triggers
| Trigger | Threshold / Signal | Why It Matters | Credit Impact | Source / Limitation |
|---|---|---|---|---|
| Revenue decline | Repeated Las Vegas revenue decline against comparable reported quarters | Distinguishes ongoing demand weakness from one-quarter hold variance | Negative — Revenue Decline | Q2 segment comparison [C20]; no independently sourced predictive cutoff |
| EBITDA margin pressure | Repeated fall in consolidated Adjusted EBITDA while revenue grows | Costs and hold can erode debt-service earnings despite volume | Negative — Margin Compression | H1/Q2 earnings comparison [C2, C3, C19] |
| FCF deterioration | CFO less property/equipment purchases no longer sustains the H1 $340 million outcome | Tests whether capex reduction or operating cash actually funds obligations | Negative — Liquidity Deterioration | Calculated H1 baseline [C4, C5]; no maintenance-only threshold |
| Liquidity reduction | Falling cash or available facility capacity versus June reported $2,928 million | Shrinks timing cushion against debt, lease and settlement demands | Negative — Liquidity Deterioration | Reported resource [C14]; borrower allocation absent |
| Leverage increase | Rising carrying debt or falling issuer-adjusted LTM EBITDA relative to June bases | Erodes non-contractual debt-service flexibility | Negative — Leverage Increase | Balance-sheet debt and earnings [C9, C10, C3, C36]; covenant threshold not inferred |
| Refinancing delay | No documented funding plan as 2028–30 maturities approach | Greater dependence on a narrower market window | Negative — Refinancing Risk | Filed schedule [C18]; no assumed refinancing date |
| Sponsor/shareholder action | Merger closes, terminates or supplies new financing; repurchases resume | Could change debtor perimeter, leverage and cash-retention policy | Negative — Leverage Increase | Conditional agreement and pause [C28, C29, C49, C50] |
| Sector deterioration | Further digital gaming-tax increases or substitution alongside weak property visitation | Raises acquisition costs or reduces revenue while fixed cash charges persist | Negative — Margin Compression | Filing and annual risk disclosure [C24, C46]; no invented sector threshold |

#### cp2.cp_model_strengths_weaknesses — CP-MODEL projection
<!-- table-id: cp2.cp_model_strengths_weaknesses -->
| direction | rank | label | mechanism | evidence_ids | status | source_id | source_locator | as_of |
|---|---:|---|---|---|---|---|---|---|
| STRENGTH | 1 | Reported liquidity | Cash and available borrowing capacity defer immediate funding pressure, conditional on access | [C14] | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | p.22, Liquidity and Capital Resources | 2026-06-30 |
| STRENGTH | 2 | Regional earnings offset | Regional EBITDA improvement partly offsets weaker Las Vegas contribution | [C20, C21, C30] | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | p.20, segment comparisons; p.6, Windsor | 2026-06-30 |
| STRENGTH | 3 | Positive after-capex cash | CFO less cash property/equipment purchases remains positive, though capex timing matters | [C4, C5] | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | p.4, cash-flow statement | 2026-06-30 |
| WEAKNESS | 1 | Lease cash burden | Large rent-related cash interest persists through a gaming earnings decline | [C7, C16] | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | p.5, cash interest; p.22, lease estimate | 2026-06-30 |
| WEAKNESS | 2 | Las Vegas volatility | Lower hold and segment EBITDA narrow fixed-charge cushion | [C19, C20] | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | p.20, Las Vegas comparison | 2026-06-30 |
| WEAKNESS | 3 | Refinancing and transaction uncertainty | Maturity schedule meets conditional merger without supplied closing financing | [C18, C28, C29] | READY | 439e1450-b5ae-4830-b4c3-3719da918fe3 | p.9, maturities; p.5, merger conditions | 2026-06-30 |

#### Definition, perimeter and event controls
| Control | Distinct source presentations or period | Treatment and creditor implication | Evidence |
|---|---|---|---|
| CF-1 — debt definitions | June face $11,807m; note book $11,705m; balance-sheet current $114m plus long-term $11,585m = $11,699m; face-to-canonical delta $108m; note-book delta $6m | Use balance-sheet carrying debt for issuer leverage; note separately displays revolver finance charges. Financing obligations $13,157m are separately classified but relevant to fixed payments. | [C11, C12, C9, C10, C13] |
| CF-2 — earnings definition | FY2025 issuer Adjusted EBITDA $3,624m; H1 2026 $1,807m; H1 2025 $1,839m | Constructed LTM $3,592m is not covenant EBITDA; numerical headroom cannot be inferred from reported compliance. | [C36, C3, C35, C34] |
| CF-3 — cash-interest bases | H1 2026 debt cash interest $368m; GLPI/VICI rent-related cash interest $686m | Keep distinct, rather than present debt-only interest as total cash fixed cost or deduct either again from CFO. | [C6, C7, C4] |
| P-1 — entity perimeter | Consolidated CZR includes the 50% Caesars Virginia venture; CEI does not guarantee its facilities | CVA borrower cash and debt-service capacity cannot be separately calculated from consolidated cash; do not treat separate facility obligations as parent-guaranteed. | [C43, C42] |
| E-1 — agreement and subsequent event | Merger signed May 27 during Q2, still conditional; Alberta launch July 13 after quarter-end | No assumed June closing financing or Alberta earnings; subsequent launch is flagged separately. | [C28, C29, C31] |

## Evidence Trace

| Claim group | Citation marker | Document | Page and role |
|---|---|---|---|
| Income, segment earnings and gaming activity | [C2, C3, C19, C20, C21, C22, C23] | Q2 2026 Form 10-Q | pp.2, 18, 20; reported period and segment comparisons |
| Cash generation, cash interest and funding float | [C4, C5, C6, C7, C25, C26, C27] | Q2 2026 Form 10-Q | pp.4–5, 11; CFO, capex, separately labelled obligations |
| Debt definitions, liquidity and maturities | [C8, C9, C10, C11, C12, C13, C14, C18] | Q2 2026 Form 10-Q | pp.2, 9, 22; balance-sheet and note roles retained |
| Future demands and covenant limits | [C15, C16, C17, C32, C33, C34, C35] | Q2 2026 Form 10-Q | pp.10, 21–22; estimates and compliance, not headroom |
| Ownership, operating perimeter and event dates | [C28, C29, C30, C31, C41, C42, C43, C49, C50] | Q2 2026 Form 10-Q | pp.5–6, 11, 13–14, 17; no hypothetical closing balance |
| Annual and historical version anchor | [C36, C37, C38, C39, C40, C45, C46, C48] | FY2025 Form 10-K; 2024 incremental agreement | 10-K pp.6, 8, 17, 23, 28, 56; agreement p.20 |

## Source Registry

T2.1 is the complete source register for this handoff. The three directly delivered sources are the Q2 2026 filing, FY2025 filing and historical incremental agreement. The CP-0, CP-1 and CP-1C handoffs are accepted same-run context, re-anchored where used to those directly delivered issuer sources. No MGM/PENN primary release, market quote, executed May 2026 merger agreement or post-February-2024 bank amendment text is supplied to this module; their absence limits independent peer, valuation and current-document conclusions. The annual filing's exhibit-index references establish document existence, not operative amendment language. [C39, C40]

## Gaps & Conflicts

- **Current legal versions:** [Insufficient Information] — the May and November 2024 credit amendments are indexed but their texts are absent. The February 2024 conformed agreement cannot establish every June 2026 operative term. Refer document interpretation to CP-4. [C38, C39, C40]
- **Covenant capacity:** Numerical headroom is **Not Calculable from Provided Materials**: the filed covenant limits and reported compliance do not supply the tested covenant EBITDA, debt netting or compliance certificate. Do not substitute issuer Adjusted EBITDA. [C32, C33, C34, C35]
- **Cash and FCF perimeter:** [Insufficient Information] — debtor-level unrestricted cash, CVA standalone cash flow and historical maintenance-versus-growth cash capex are not supplied. Consolidated liquidity may not equal resources available to each debtor. [C14, C42, C43, C4, C5]
- **Merger and refinancing:** [Insufficient Information] — full operative merger and financing documents are not delivered. The filed agreement description confirms conditional approvals but cannot specify post-close debt service. [C28, C29]
- **Peer challenge:** CP-1C finds accounting and segment-perimeter differences, but underlying peer releases are not evidence in this invocation. No sourced, aligned peer EBITDA, debt or FCF ranking is asserted here.
- **Definitions:** CF-1 through CF-3 preserve debt, interest and lease distinctions. The positive after-capex cash calculation neither normalizes cash capex nor includes a prospective merger adjustment. [C4, C5, C11, C12, C13]
- **Event scan:** The May 27 agreement is an in-period agreement with an unresolved future closing; the July 13 Alberta launch is subsequent to June 30 and is excluded from quarter-end figures. No other post-June event is established by the delivered sources. [C28, C29, C31]

## QA Validation

| Self-check | Result | Basis and disposition |
|---|---|---|
| Identity and upstream acceptance | PASS locally | Host-owned envelope retained; accepted CP-0, CP-1 and CP-1C run, issuer, period and hashes match. |
| Full method and register coverage | PASS locally | Business model, structure, revenue, costs, FCF, Porter, PEST, SWOT, outlook, contrary case and downside represented; T2.1/T2.7/T2.10/T2.11/T2.12 and stable CP-MODEL table present. |
| Source and calculation discipline | RESTRICTED | Source-bound calculations labelled; debt definitions, lease cash and merger timing separated; covenant headroom and peer ranking withheld. |
| Confidence and status | RESTRICTED | Own E=85, C=80, S=0.7, P=0 assessment gives 58/Low; partial source gate requires Restricted and Requires More Work. |
| Filename and handoff self-check | PASS locally | Exact intended filename `CZR_CP-2_20261002.md`; six ordered H2 headings and seven model-authored YAML fields checked in this draft. |
| Host validation | PENDING | Host validation and completeness checks follow this answer; no script execution, exit code or host finding is claimed. |

**Downstream use:** CP-MODEL may consume the cited ranked strengths/weaknesses, not treat them as a forecast. CP-2A can develop the causal downside; CP-4 should resolve current legal versions before CP-3 security selection; CP-3 needs its own dated market and definition-aligned evidence. No legal-capacity, recovery-waterfall, relative-value or position-sizing conclusion is made here.