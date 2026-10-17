---
module_id: CP-6
run_id: 20261011-czr-quick-credit-screen
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-3, CP-5, CP-L10, FIT, CP-1A, CP-1B
---

## Analysis

Hand-written test fixture of a CP-6 Handoff at Quick depth for the synthetic Primary pack `czr-2026q2-primary`. Screening basis: recommendation 3 - MW for all three Strategies, through different instruments: the new Senior Secured Term Loan B for CLO and Indexed Loans, the 6.50% secured notes due 2032 for Indexed HY. With a Credit Score of 4 - Weak (calc: CP-L10 snapshot.credit_view), only an instrument that pays for the buyout's added secured debt earns a market weight: the new loan's talk mid of 337.50 bps (calc: CP-3 snapshot.instrument_levels NEW-1) [C1] is about 100 bps over the issuer's existing term loans, which stay at 4 - Modest UW.

The bear case came closest to changing the call: Las Vegas earnings are falling into fixed rent [C2] [C3], and the new debt adds 213 of cash interest [C4]. The Bear won on the existing debt and the Bull on the new loan. The bear case does not win there because the new loan ranks first, is priced for the added leverage and is sized within Test CLO I's issuer limit (calc: FIT snapshot.portfolio_fit NEW-1). The decision carries CP-5's limitations: no EV, Structuring EBITDA without the arranger's synergies, and DMs that exclude the floor benefit.

## Tables

<!-- table: snapshot.recommendation -->
| strategy | recommendation | basis | rationale | cite |
|---|---|---|---|---|
| CLO | 3 - MW | Screening | Screening basis: the new first-lien term loan at talk pays for the added secured debt; existing loans do not | calc: CP-6 snapshot.instrument_recommendation NEW-1 |
| Indexed Loans | 3 - MW | Screening | Screening basis: as CLO, the new term loan is the loan worth holding | calc: CP-6 snapshot.instrument_recommendation NEW-1 |
| Indexed HY | 3 - MW | Screening | Screening basis: the 6.50% secured notes due 2032 carry the widest secured yield; the unsecured notes are primed | calc: CP-6 snapshot.instrument_recommendation CEI-SSN-2032 |

<!-- table: snapshot.instrument_recommendation -->
| facility_id | instrument | recommendation | valuation | rationale | cite |
|---|---|---|---|---|---|
| NEW-1 | New Senior Secured Term Loan B | 3 - MW | V2 - Attractive | Credit Score 4 plus V2: priced for the buyout's leverage | [C1]; calc: CP-3 snapshot.instrument_levels NEW-1 |
| CEI-TLB | CEI Term Loan B | 4 - Modest UW | V3 - Fair | Credit Score 4 plus V3: fair spread on a weakening credit, diluted by the new loan | calc: CP-3 snapshot.instrument_levels CEI-TLB |
| CEI-TLB-1 | CEI Term Loan B-1 | 4 - Modest UW | V3 - Fair | as the Term Loan B | calc: CP-3 snapshot.instrument_levels CEI-TLB-1 |
| CEI-SSN-2030 | CEI Senior Secured Notes due 2030 | 4 - Modest UW | V3 - Fair | Credit Score 4 plus V3 | calc: CP-3 snapshot.instrument_levels CEI-SSN-2030 |
| CEI-SSN-2032 | CEI Senior Secured Notes due 2032 | 3 - MW | V2 - Attractive | Credit Score 4 plus V2: the widest secured yield at a discount price | calc: CP-3 snapshot.instrument_levels CEI-SSN-2032 |
| CEI-SN-2029 | CEI Senior Notes due 2029 | 4 - Modest UW | V4 - Unattractive | Credit Score 4 plus V4: primed by new secured debt without extra yield | calc: CP-3 snapshot.instrument_levels CEI-SN-2029 |
| CEI-SN-2032 | CEI Senior Notes due 2032 | 4 - Modest UW | V3 - Fair | Credit Score 4 plus V3 | calc: CP-3 snapshot.instrument_levels CEI-SN-2032 |

<!-- table: snapshot.thesis -->
| thesis | cite |
|---|---|
| Own the new first-lien term loan at its talk: about 100 bps over Caesars' existing loans pays for the buyout's added secured debt on a large, diversified but weakening casino base. Avoid the unsecured notes, which the new debt primes without extra yield. | [C1] [C5]; calc: CP-3 snapshot.instrument_levels NEW-1 |

<!-- table: snapshot.catalysts -->
| date_or_window | event | direction | watch_trigger | cite |
|---|---|---|---|---|
| 2026-10-08 | Commitments due on the new Term Loan B | Flat | final margin and OID against the talk | [C6] |
| On closing (date not in the pack) | Fertitta Entertainment completes the acquisition; Caesars delists | Down | the closing capital structure and any change-of-control offer | [C7] |
| Next quarterly results (not dated in the pack) | Las Vegas segment results | Down | a third year-on-year decline in Las Vegas Adjusted EBITDA | [C2] |
| On closing | Agency rating actions on the secured and unsecured notes | Down | a downgrade from B1 / Caa1 | [C8] |

<!-- table: cp6.challenge -->
| claim | counter_evidence | resolution | what_would_change_view | cite |
|---|---|---|---|---|
| Bull: Regional and Digital growth and 2,928 of liquidity (calc: CP-L10 cpl10.screen_items Liquidity) hold the credit while the new loan prices about 100 bps over the existing loans | Las Vegas Adjusted EBITDA fell 12.6% in the second quarter against fixed rent (calc: CP-L10 cpl10.screen_items Las Vegas earnings) | Partially Mitigated: the screen supports a market weight through the new loan, not the existing debt; no Full analysis of cash flow or recovery exists at this depth | a Full run's cash-flow and liquidity analysis, or delivered growth that offsets Las Vegas | [C2] [C3] [C4] |
| Bear: falling Las Vegas earnings into fixed rent and 3,000 of new secured debt make the credit too levered to own (calc: CP-L10 cpl10.screen_items OVERALL) | the new loan ranks first and its talk is about 100 bps over the existing loans, which compensates for the added leverage (calc: CP-3 cp3.talk_valuation NEW-1) | Unresolved for the existing debt: the zero-bound path cannot be completed without CP-2 analysis and the controlling documents | final terms tighter than SOFR + 300 or a Full run that tests the downside | [C1] [C2] [C5] |

<!-- table: cp6.portfolio_recommendation -->
| portfolio_id | strategy | instrument | uncapped | cap | final | fit_verdict | reason |
|---|---|---|---|---|---|---|---|
| TEST_CLO_I | CLO | NEW-1 | 3 - MW | 3 - MW | 3 - MW | Watch | limit C-17 (excluded sectors) could not be computed: CZR's sector is not in the CLO's taxonomy; the cap equals the view |
| TEST_CLO_I | CLO | CEI-TLB | 4 - Modest UW | 3 - MW | 4 - Modest UW | Watch | limit C-17 could not be computed; the view is already below the cap |
| TEST_CLO_I | CLO | CEI-TLB-1 | 4 - Modest UW | 3 - MW | 4 - Modest UW | Watch | limit C-17 could not be computed; the view is already below the cap |

## Gaps

- Restricted: CP-2 and CP-1D are absent at Quick depth, so the Credit Score is CP-L10's screening view and the challenge has no causal downside model, add-back test or cash-flow analysis.
- No CP-2A, CP-4 or CP-3D at this depth: the challenge has no covenant reading or market-implied risk.
- Upgrade: a linked Full run (CP-2, CP-1D, CP-2D and CP-4) would lift the screening basis and allow a Full-basis recommendation.
- No EV: the decision cannot weigh the debt against enterprise value.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Price Talk \| SOFR + 300–325 bps (initial talk) |
| C2 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, three months ended June 30 | Las Vegas \| $410 \| $469 \| (12.6)% |
| C3 | CZR_FY2025_10K.txt | Risk factors, indebtedness | VICI and GLPI that require an annual rent payment of $1.4 billion in 2026 |
| C4 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Earnings and interest | Pro forma cash interest paid for debt, LTM \| 989 |
| C5 | CZR_Q2_2026_Earnings_Release.txt | About Caesars Entertainment, Inc. | the largest casino-entertainment company in the US |
| C6 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Commitment date \| 2026-10-08 |
| C7 | CZR_2026_Merger_Press_Release.txt | Transaction Details | shares of Caesars Entertainment common stock will no longer be listed on NASDAQ |
| C8 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | Moody's last-rated date shown: 2026-09-28 |
