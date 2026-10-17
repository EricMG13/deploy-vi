---
module_id: CP-L10
run_id: 20261011-czr-quick-credit-screen
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-1, CP-1A, MODEL, CP-1B
---

## Analysis

Hand-written test fixture of a CP-L10 Handoff for the synthetic Primary pack `czr-2026q2-primary`, screening only. Screen conclusion: Credit Score 4 - Weak, Credit Direction Deteriorating, Sector Outlook Neutral, screening posture Deteriorating. The buyout adds a 3,000 senior secured term loan to a PF-LTM that already carries 1.35 billion of fixed rent outside Adjusted EBITDA (calc: MODEL model.house Adjusted leverage) [C12] [C1]. Primary support: the largest US casino operator, with Regional and Digital growing [C4] [C11]. Primary risk: Las Vegas Adjusted EBITDA fell 12.6% in the second quarter while rent stays fixed [C10] [C2]. Monitoring trigger: a third quarterly decline in Las Vegas Adjusted EBITDA.

The source gate is PARTIAL: the pack holds no credit agreement or indenture, so the controlling-document, protection and capacity topics are Gap only, as are the owner's post-closing policy and any forecast. Six topics are Deepen; the rest are Summarize or Gap only, as the table shows. Sector Outlook rests on two comparable releases [C5] [C6], so its confidence is Medium and Deep Research is named as an upgrade. Portfolio fit is judged by FIT and CP-6, not here.

## Tables

<!-- table: snapshot.credit_view -->
| credit_score | credit_direction | sector_outlook | primary_support | primary_downside | confidence | basis | cite |
|---|---|---|---|---|---|---|---|
| 4 - Weak | Deteriorating | Neutral | the largest US casino operator with a regional and digital base that is still growing | Las Vegas earnings decline passing through fixed rent to thin free cash flow as acquisition debt is added | Medium | Screening | [C1] [C10] [C11]; calc: MODEL model.house Adjusted leverage |

<!-- table: snapshot.strengths_weaknesses -->
| kind | label | text | cite |
|---|---|---|---|
| Strength | Scale and diversification | the largest US casino-entertainment company, with one loyalty network across regional, Las Vegas and digital lines | [C4] |
| Strength | Growing regional and digital lines | Regional first-half Adjusted EBITDA rose 5.0% and Digital 11.4%, offsetting part of the Las Vegas decline | [C11] |
| Weakness | Fixed charges ahead of debt | 1.4 billion of rent in 2026 escalates with CPI and sits outside Adjusted EBITDA | [C1] |
| Weakness | Leverage after the buyout | a new 3,000 senior secured term loan is added to a PF-LTM already carrying 13,157 of financing obligations | [C12]; calc: MODEL model.house Adjusted leverage |

<!-- table: cpl10.screen_topics -->
| topic_id | family | topic | materiality | evidence_status | disposition | priority_rank | summary | upgrade_module | cite |
|---|---|---|---|---|---|---|---|---|---|
| SOURCE_BASIS | Financial change | Source, period and perimeter basis | Medium | Sufficient | Summarize | 13 | The 10-Q and the earnings release agree on the quarter, and CP-1 registers the PF-LTM perimeter. | CP-1 | [C3] [C10] |
| EARNINGS_MARGIN_CHANGE | Financial change | Earnings and margin direction | High | Sufficient | Deepen | 4 | Las Vegas Adjusted EBITDA fell 12.6% in the second quarter while Regional and Digital grew. | CP-1B | [C10] [C11] |
| CASH_CONVERSION | Financial change | Cash generation transmission | High | Partial | Deepen | 5 | Operating cash flow of 675 is flat on the prior period against lower Las Vegas earnings, and the 10-K and 10-Q give no full bridge. | CP-1D | [C3] [C2] |
| LEVERAGE_COVERAGE | Financial change | Leverage and coverage direction | High | Sufficient | Deepen | 1 | The 3,000 term loan lifts PF leverage, and lease financing obligations make adjusted leverage the binding measure. | CP-2 | [C12] [C2] |
| KPI_COMPARABILITY | Financial change | KPI reliability and comparability | Low | Partial | Summarize | 19 | Segment Adjusted EBITDA is reported on one basis in both quarters, with no definition conflict in the pack. | CP-1B | [C11] |
| BUSINESS_DURABILITY | Financial change | Business durability | Medium | Partial | Summarize | 14 | Scale and a growing regional and digital base support durability, while Las Vegas share is under pressure. | CP-2 | [C4] [C5] |
| MARGIN_FCF_RESILIENCE | Financial change | Margin and free cash flow resilience | High | Partial | Deepen | 3 | Rent paid as interest of 1,349 is fixed and escalating, so a fall in earnings passes straight to free cash flow. | CP-2 | [C2] [C1] |
| GOVERNANCE_SPONSOR_BEHAVIOR | Financial change | Governance and sponsor behavior | High | Missing | Gap only | 9 | The new owner's post-closing financial policy is not in the pack. | CP-2 |  |
| FINANCIAL_POLICY_CAPITAL_ALLOCATION | Financial change | Financial policy and capital allocation | Medium | Partial | Summarize | 15 | A debt-funded change of control sets the policy backdrop, and no post-closing distribution policy is stated. | CP-2 | [C9] |
| ESG_TRANSITION | Financial change | ESG and transition transmission | Low | Missing | Gap only | 24 | No issuer-specific environmental or social transmission evidence is in the pack. | CP-2 |  |
| LIQUIDITY_MATURITIES | Liquidity | Liquidity and maturities | High | Sufficient | Deepen | 2 | Cash and committed revolver capacity of 2,928 sit against the 2029 and 2030 maturities. | CP-2D | [C8] |
| ACCESSIBLE_LIQUIDITY_USES | Liquidity | Accessible liquidity and its uses | Medium | Partial | Summarize | 16 | Part of the revolver is committed as a regulatory requirement, which narrows accessible liquidity. | CP-2D | [C8] |
| WORKING_CAPITAL_CAPEX_CASH_BURN | Liquidity | Working capital, capex and cash burn | Medium | Missing | Gap only | 20 | No capex or working-capital schedule is in the pack. | CP-2D |  |
| RATES_HEDGES | Liquidity | Rates and hedges | Low | Missing | Gap only | 25 | No hedge terms are disclosed in the pack. | CP-2E |  |
| FX_COMMODITY_INFLATION | Liquidity | FX, commodity and inflation | Low | Missing | Gap only | 26 | No FX or commodity sensitivity is disclosed in the pack. | CP-2E |  |
| BASE_DOWNSIDE_TRAJECTORY | Liquidity | Base and downside trajectory | High | Missing | Gap only | 10 | No issuer forecast or post-closing plan is in the pack to build a trajectory. | CP-2G |  |
| BREAKPOINTS_REFINANCING | Covenant and refinancing | Breakpoints and refinancing | High | Partial | Deepen | 6 | Committed acquisition financing is arranged, but covenant levels and the refinancing terms of the 2029 and 2030 maturities are not in the pack. | CP-4 | [C7] [C12] |
| LEVERAGE_REFINANCING_CONTEXT | Covenant and refinancing | Leverage tolerance and refinancing access | Medium | Partial | Summarize | 17 | Ten banks committed the new financing, which supports access, against higher secured debt. | CP-2 | [C7] [C12] |
| CONTROLLING_DOCUMENT_AVAILABILITY | Covenant and refinancing | Controlling documents available | High | Missing | Gap only | 7 | No credit agreement or indenture is in the pack. | CP-4 |  |
| PROTECTION_WEAKNESS_FLAGS | Covenant and refinancing | Protection weakness flags | High | Missing | Gap only | 8 | Covenant protections cannot be read without the controlling documents. | CP-4 |  |
| ENTITY_GUARANTEE_COLLATERAL | Covenant and refinancing | Entity, guarantee and collateral map | Medium | Missing | Gap only | 21 | Guarantor and collateral perimeters are not in the pack. | CP-4 |  |
| LEAKAGE_PRIMING_FLAGS | Covenant and refinancing | Leakage and priming flags | Medium | Missing | Gap only | 22 | Basket capacity for leakage or priming is not in the pack. | CP-4 |  |
| CAPACITY_AVAILABILITY | Covenant and refinancing | Debt and restricted-payment capacity | Medium | Missing | Gap only | 23 | Debt and restricted-payment capacity cannot be read without the controlling documents. | CP-4 |  |
| PRESSURE_POINT_UPGRADE_PRIORITY | Covenant and refinancing | Pressure points for Full work | Medium | Partial | Summarize | 18 | Fixed rent and the new term loan are the pressure points to take to a Full covenant run. | CP-4 | [C1] [C12] |
| STRUCTURAL_RECOVERY_PROTECTION | Distress | Structural recovery protection | Medium | Missing | Gap only | 27 | No recovery-relevant collateral or structure evidence is in the pack. | CP-4C |  |
| DOWNSIDE_LME_EXPOSURE | Distress | Downside LME exposure | Medium | Missing | Gap only | 28 | No liability-management exposure can be read without the controlling documents. | CP-4C |  |
| DATED_MARKET_SNAPSHOT | Relative value | Dated market snapshot | Medium | Sufficient | Summarize | 11 | A TRACE print dated 2026-10-02 shows the secured notes' last Moody's rating date as 2026-09-28. | CP-3 | [C13] |
| CURVE_COMPARABLE_COMPENSATION | Relative value | Curve and comparable compensation | Medium | Missing | Gap only | 29 | No comparable curve or spread data is in the pack. | CP-3D |  |
| LIQUIDITY_TECHNICALS | Relative value | Liquidity and technicals | Low | Missing | Gap only | 30 | No bid-ask or trading-volume evidence is in the pack. | CP-3 |  |
| INTEGRATED_SCREENING_POSTURE | Relative value | Integrated screening posture | Medium | Partial | Summarize | 12 | The pack's dated price evidence supports a screening posture only, not a relative-value view. | CP-3 | [C13] |
| PORTFOLIO_CONTEXT | Portfolio | Portfolio context | Not assessable | Missing | Gap only | 31 | This screen reads no portfolio sources, so fit is judged by FIT and CP-6. | FIT |  |

<!-- table: cpl10.screen_items -->
| item | assessment | evidence | transmission | implication | confidence | cite |
|---|---|---|---|---|---|---|
| Las Vegas earnings | Deteriorating | Las Vegas segment Adjusted EBITDA fell 12.6% in the second quarter, while Regional rose 5.0% | the highest-value assets lose earnings while rent is fixed | falling rent and interest cover | High | [C10] [C11] |
| Fixed rent and new debt | Deteriorating | rent paid as interest of 1,349 and 3,000 of new senior secured term loan | operating leverage to visitation plus more secured debt on an unchanged earnings base | lease-adjusted leverage is the binding measure and recovery for existing secured creditors falls | High | [C2] [C12] |
| Liquidity | Stable | cash and committed revolver capacity of 2,928 | near-term runway is covered, but part of the revolver is regulatory | no liquidity event is visible inside 12 months | Medium | [C8] |
| OVERALL | Deteriorating | Las Vegas earnings down against fixed rent, new acquisition debt, no controlling documents in the pack | earnings decline passes to cash flow, then to interest cover and refinancing of the 2029 and 2030 maturities | screening posture Deteriorating; a Full run is recommended for CP-2, CP-2D and CP-4 | Medium | [C10] [C12] [C8] |

<!-- table: cpl10.upgrade_triggers -->
| topic_id | trigger | decision_impact | required_source | target_full_module | blocking |
|---|---|---|---|---|---|
| LEVERAGE_COVERAGE | Final terms of the new 3,000 term loan | a larger size or wider margin lifts PF interest and secured leverage | the final financing terms and the closing capitalisation | CP-2 | No |
| LIQUIDITY_MATURITIES | A change in the revolver commitment or the 2029 and 2030 maturity plan | liquidity runway and refinancing confidence | the credit agreement and the post-closing liquidity schedule | CP-2D | No |
| MARGIN_FCF_RESILIENCE | A further quarterly fall in Las Vegas Adjusted EBITDA | rent and interest cover, free cash flow after rent | the lease agreements and segment cash-flow detail | CP-2 | No |
| EARNINGS_MARGIN_CHANGE | A third quarterly year-on-year fall in Las Vegas Adjusted EBITDA | confirms share loss rather than a soft quarter | the quarterly segment history | CP-1B | No |
| CASH_CONVERSION | Operating cash flow no longer covering rent and capex | free cash flow turns negative | the full cash-flow bridge and the add-back detail | CP-1D | No |
| BREAKPOINTS_REFINANCING | The 2029 and 2030 maturities approach without terms | refinancing risk and covenant headroom | the credit agreement, indentures and amendments | CP-4 | Yes |
| CONTROLLING_DOCUMENT_AVAILABILITY | Any covenant or basket judgement is needed | no protection can be assessed without the documents | the credit agreement and indentures | CP-4 | Yes |
| PROTECTION_WEAKNESS_FLAGS | A covenant-lite or loose-basket finding is needed | recovery and priming risk | the credit agreement and indentures | CP-4 | Yes |
| GOVERNANCE_SPONSOR_BEHAVIOR | The owner's post-closing financial policy is needed | distribution and leverage behaviour after the buyout | the owner's financing plan and a Deep Research answer | CP-2 | No |
| BASE_DOWNSIDE_TRAJECTORY | A liquidity or leverage trajectory is needed | downside path of cash, leverage and refinancing | an issuer forecast or a Model projection | CP-2G | No |
| SECTOR_OUTLOOK | The sector outlook needs more than two peer releases | Sector Outlook confidence is Low | researched sector evidence | CP-DR | No |

## Gaps

- Source gate PARTIAL: no credit agreement, indenture or amendment is in the pack, so covenant, protection, guarantee and capacity topics are Gap only.
- No issuer forecast or post-closing financial policy: the trajectory and governance topics are Gap only.
- No Deep Research: the Sector Outlook rests on two comparable releases, so its confidence is Medium; Deep Research (CP-DR) would add researched sector evidence.
- No CP-1D in this depth: cash conversion carries CP-1's realization statuses only.
- No portfolio context: the Portfolio topic is Not assessable.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_FY2025_10K.txt | Risk factors, indebtedness | VICI and GLPI that require an annual rent payment of $1.4 billion in 2026 |
| C2 | CZR_FY2025_10K.txt | Supplemental disclosure of cash flow information | Cash interest paid for rent related to financing obligations \| 1,349 \| 1,324 \| 1,286 |
| C3 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows | Net cash provided by operating activities \| 675 \| 680 |
| C4 | CZR_Q2_2026_Earnings_Release.txt | About Caesars Entertainment, Inc. | the largest casino-entertainment company in the US |
| C5 | MGM_Q2_2026_Earnings_Release.txt | p.1 | Second consecutive quarter of Las Vegas Strip Resorts year-over-year revenue growth |
| C6 | MGM_Q2_2026_Earnings_Release.txt | Las Vegas Strip Resorts | Segment Adjusted EBITDAR of $735 million in the current quarter compared to $710 million |
| C7 | CZR_2026_Merger_Press_Release.txt | Transaction Details | new committed debt financing arranged by a group consisting of 10 banks |
| C8 | CZR_Q2_2026_10Q.txt | Liquidity and Capital Resources | Revolver capacity committed as regulatory requirement \| (56) ... Total \| $2,928 |
| C9 | CZR_2026_Merger_Press_Release.txt | p.1 | Caesars Entertainment shareholders to receive $31.00 per share in cash |
| C10 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, three months ended June 30 | Las Vegas \| $410 \| $469 \| (12.6)% |
| C11 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Regional \| 923 \| 879 \| 5.0% |
| C12 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Capitalisation | New Senior Secured Term Loan B \| 0 \| 3,000 \| 3,000 |
| C13 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | Moody's last-rated date shown: 2026-09-28 |
