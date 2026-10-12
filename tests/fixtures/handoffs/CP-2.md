---
module_id: CP-2
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-1, CP-1A, MODEL, CP-1B, CP-1D
---

## Analysis

Hand-written test fixture of a CP-2 Handoff for the synthetic Primary pack `czr-2026q2-primary`. Credit Score 4 - Weak, Credit Direction Deteriorating, Sector Outlook Neutral. On the house view the buyout leaves total debt at 4.06x SSIM EBITDA of 3,592 on the PF-LTM (calc: MODEL model.house SSIM Multiple), but the earnings figure is before about 1.35 billion of rent [C1] [C2]: counting the 13,157 of financing obligations as debt, adjusted leverage is 7.72x (calc: MODEL model.house Adjusted leverage) and operating cash flow converts only 37.4% of Adjusted EBITDA [C3].

Profile, nine dimensions: scale and market position Strong (largest US casino operator, four segments [C4]); competitive advantage Average (Caesars Rewards network, but Las Vegas losing share while MGM's Strip resorts grew 3% [C5] [C6]); diversification Average; cost and capex flexibility Weak (fixed rent with CPI escalators); margin stability Average; free cash flow stability Weak; access to capital Average (committed acquisition financing [C7]); liquidity Average (2,928 of cash and revolver capacity [C8]); financial policy and governance Weak (a debt-funded change of control to a private owner [C9]).

Primary downside path: Las Vegas visitation keeps falling (the first break, already visible in a 12.6% second-quarter EBITDA decline [C10]); with rent fixed and escalating, the decline passes straight to cash flow; interest on 3,000 of new term loan takes PF cash interest to 989 (calc: MODEL model.house PF interest), so free cash flow after rent and capex turns thin and deleveraging stalls before the 2029 and 2030 maturities. The trigger to watch is Las Vegas segment Adjusted EBITDA. The strongest counter-argument is that Regional and Digital growth offset Las Vegas and that the new owner integrates Golden Nugget with synergies; it wins if Las Vegas stabilises and the 150 of synergies is delivered, which no source yet evidences [C11]. Overall, Caesars presents a strong business profile supported by scale and a growing regional and digital base, but credit quality is constrained by fixed rent ahead of debt and the buyout's added leverage. The primary downside path is a Las Vegas earnings decline passing through fixed rent to thin free cash flow.

## Tables

<!-- table: snapshot.credit_view -->
| credit_score | credit_direction | sector_outlook | primary_support | primary_downside | confidence | basis | cite |
|---|---|---|---|---|---|---|---|
| 4 - Weak | Deteriorating | Neutral | the largest US casino operator with a regional and digital base that is still growing | Las Vegas earnings decline passing through fixed rent to thin free cash flow as acquisition debt is added | Medium | Full | [C1] [C10] [C12]; calc: MODEL model.house Adjusted leverage |

<!-- table: snapshot.strengths_weaknesses -->
| kind | label | text | cite |
|---|---|---|---|
| Strength | Scale and diversification | the largest US casino-entertainment company, with Regional, Las Vegas, Digital and Managed segments and one loyalty network | [C4] |
| Strength | Growing regional and digital lines | Regional first-half Adjusted EBITDA rose to 923 and Digital to 137, offsetting part of the Las Vegas decline | [C12] [C13] |
| Weakness | Fixed charges ahead of debt | 1.4 billion of rent in 2026 under the VICI and GLPI leases, escalating with CPI, sits outside Adjusted EBITDA | [C1] |
| Weakness | Leverage after the buyout | adjusted leverage of 7.72x on the PF-LTM once financing obligations count as debt; a new 3,000 term loan is added | [C14]; calc: MODEL model.house Adjusted leverage |

<!-- table: cp2.drivers -->
| rank | driver | evidence | risk_mechanism | credit_implication | direction | confidence | cite |
|---|---|---|---|---|---|---|---|
| 1 | Las Vegas earnings | segment Adjusted EBITDA down 12.6% in the second quarter on lower visitation, occupancy and rates | the highest-value assets lose earnings while rent is fixed | falling rent and interest cover; higher PD if the decline persists | Negative | High | [C10] [C15] |
| 2 | Acquisition debt | a 3,000 senior secured term loan funds part of Fertitta Entertainment's purchase | more senior secured debt on an unchanged earnings base | higher leverage and lower recovery for existing secured creditors | Negative | High | [C14] [C9] |
| 3 | Lease fixed charges | rent paid as interest of 1,349 in FY2025, excluded from Adjusted EBITDA | operating leverage to visitation; rent cannot be cut in a downturn | lease-adjusted leverage is the binding measure | Negative | High | [C2] |
| 4 | Regional and digital growth | Regional first-half Adjusted EBITDA up 5.0%; Digital up 11.4% | diversification away from Las Vegas | partial offset to the Las Vegas decline | Positive | Medium | [C12] [C13] |

<!-- table: cp2.watch_items -->
| trigger | threshold_or_signal | why_it_matters | credit_impact | cite |
|---|---|---|---|---|
| Las Vegas segment Adjusted EBITDA | a third quarterly year-on-year decline | confirms share loss rather than a soft quarter | Credit Score moves toward 5 - Stressed on rent cover | [C10] |
| Final terms of the new Term Loan B | margin above the 325 bps top of talk or a larger size | higher PF interest or more secured debt | PF interest cover falls below the 3.63x of the PF-LTM | [C14]; calc: MODEL model.house PF interest cover |
| Agency actions on closing | a downgrade of the secured notes from B1 | Moody's reviewed both notes on 2026-09-28 | wider spreads and tighter CLO eligibility | [C16] |

## Gaps

- No CP-1C peer benchmark in this Pathway's current list: peer positioning rests on the MGM and PENN releases alone.
- No Deep Research: the Sector Outlook rests on two comparable releases in the pack.
- Las Vegas visitation, occupancy and the owner's post-closing financial policy are not in the pack.

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
| C11 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Earnings and interest | Run-rate cost synergies identified by Fertitta Entertainment, not yet realised \| 150 |
| C12 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Regional \| 923 \| 879 \| 5.0% |
| C13 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Caesars Digital \| 137 \| 123 \| 11.4% |
| C14 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Capitalisation | New Senior Secured Term Loan B \| 0 \| 3,000 \| 3,000 |
| C15 | CZR_Q2_2026_10Q.txt | MD&A, Las Vegas | lower city-wide leisure customer visitation resulting in decreased non-gaming revenues |
| C16 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | Moody's last-rated date shown: 2026-09-28 |
