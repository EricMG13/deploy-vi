---
module_id: CP-3
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-1, MODEL, CP-1A, CP-1D, CP-2
---

## Analysis

Hand-written test fixture of a CP-3 Handoff for the synthetic Primary pack `czr-2026q2-primary`. The new Senior Secured Term Loan B is the best-compensated instrument: at SOFR + 300–325 with OID 99.0–99.5 it implies a 3-year DM of 316.67 to 358.33, 337.50 at the mid (calc: bond_analytics NEW-1) [C1] [C2], against 235.40 to 239.57 on Caesars' own term loans of the same rank (calc: bond_analytics CEI-TLB-1, CEI-TLB) [C3] [C4] and 248 on the BB loan index [C5]. The roughly 100 bps premium pays for more secured debt ahead of the buyout and lands between the BB index and the B sector average of 331 [C6], where its expected Ba3 / BB- ratings sit [C7].

The 6.50% secured notes due 2032 yield 8.071057% at 93.25 (calc: bond_analytics CEI-SSN-2032) [C8], about 160 bps more than the 2030 secured notes at 6.493579% [C9] for two more years and the same rank: attractive if the issuer refinances the earlier maturities. The unsecured notes are the weakest risk-reward: the 4.625% notes due 2029 yield 6.630562% (calc: bond_analytics CEI-SN-2029) [C10], no more than PENN's 2029 senior notes at 6.65 [C11] while 3,000 of new secured debt will rank ahead of them. The strongest case against preferring the new loan is that its final terms may tighten below the talk mid; at the low end it is still about 80 bps wide of the existing loans.

## Tables

<!-- table: snapshot.instrument_levels -->
| facility_id | instrument | level_basis | level_date | bid | ask | mid | spread_or_coupon | metric_basis | yield_or_dm | oid | valuation | rationale | cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CEI-TLB | CEI Term Loan B | Market | 2026-10-02 | 99.375 | 99.750 | 99.563 | Term SOFR + 2.25% | 3Y DM | 239.57 | — | V3 - Fair | about 9 bps inside the BB loan index (248) and 12 bps wide of the BB sector average (228); Bloomberg shows 252 on its own convention | [C3] [C5] [C12]; calc: bond_analytics CEI-TLB |
| CEI-TLB-1 | CEI Term Loan B-1 | Market | 2026-10-02 | 99.500 | 99.875 | 99.688 | Term SOFR + 2.25% | 3Y DM | 235.40 | — | V3 - Fair | in line with the BB index and sector average; Bloomberg shows 241 | [C4] [C5] [C12]; calc: bond_analytics CEI-TLB-1 |
| CEI-SSN-2030 | CEI Senior Secured Notes due 2030 | Market | 2026-10-02 | 101.250 | 101.750 | 101.500 | 7.00% | YTW | 6.493579 | — | V3 - Fair | no call schedule in the pack, so the YTW is the yield to maturity; Bloomberg's 6.41 YTW includes calls | [C9]; calc: bond_analytics CEI-SSN-2030 |
| CEI-SSN-2032 | CEI Senior Secured Notes due 2032 | Market | 2026-10-02 | 93.000 | 93.500 | 93.250 | 6.50% | YTW | 8.071057 | — | V2 - Attractive | about 160 bps over the 2030 secured notes for two more years at the same rank; a discount bond, so maturity is the worst date | [C8] [C13]; calc: bond_analytics CEI-SSN-2032 |
| CEI-SN-2029 | CEI Senior Notes due 2029 | Market | 2026-10-02 | 94.250 | 94.875 | 94.563 | 4.625% | YTW | 6.630562 | — | V4 - Unattractive | in line with PENN's B3 2029 notes at 6.65 while 3,000 of new secured debt ranks ahead; about 140 bps inside the secured 2032 notes | [C10] [C11]; calc: bond_analytics CEI-SN-2029 |
| CEI-SN-2032 | CEI Senior Notes due 2032 | Market | 2026-10-02 | 84.500 | 85.250 | 84.875 | 6.00% | YTW | 9.333010 | — | V3 - Fair | about 125 bps over the secured 2032 notes for the unsecured rank | [C14]; calc: bond_analytics CEI-SN-2032 |
| NEW-1 | New Senior Secured Term Loan B | Talk | 2026-09-29 | — | — | — | SOFR + 300–325 bps (initial talk) | 3Y DM | 337.50 | 99.25 | V2 - Attractive | talk mid about 100 bps wide of the issuer's own term loans and 90 bps wide of the BB loan index | [C1] [C2] [C5]; calc: bond_analytics NEW-1 |

<!-- table: snapshot.relative_value -->
| block | name | bloomberg_id | ratings | size | currency | unit | margin_or_coupon | maturity_date | seniority | price | chg_1m | chg_ytd | yield_pct | spread_or_dm_bps | market_value | level_date | cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Loan index | Morningstar LSTA US Leveraged Loan Index | SPBDAL | — | — | USD | MILLIONS | — | — | — | 96.84 | 0.21 | 0.94 | 8.11 | 389 | 1452300 | 2026-10-02 | [C15] [C16] |
| Loan index | Morningstar LSTA US Leveraged Loan Index BB | SPBDLLBB | BB | — | USD | MILLIONS | — | — | — | 99.62 | 0.12 | 0.41 | 6.71 | 248 | 512000 | 2026-10-02 | [C5] [C16] |
| Loan index | Morningstar LSTA US Leveraged Loan Index B | SPBDLLB | B | — | USD | MILLIONS | — | — | — | 97.15 | 0.24 | 1.02 | 8.04 | 381 | 801500 | 2026-10-02 | [C17] [C16] |
| Loan index | Gaming sector average, BB | — | BB | 1878 | USD | MILLIONS | 219 | — | — | 99.905 | — | — | 6.44 | 228 | — | 2026-10-02 | [C12] [C16]; calc: (bid + ask) / 2 |
| Loan index | Gaming sector average, B | — | B | 1550 | USD | MILLIONS | 313 | — | — | 99.38 | — | — | 7.69 | 331 | — | 2026-10-02 | [C6] [C16]; calc: (bid + ask) / 2 |
| Loan comparable | Caesars Entertainment, Inc. Term Loan B | BL3912045 | Ba3/BB | 2018 | USD | MILLIONS | 225 | 2030-02-06 | 1st Lien | 99.5625 | 0.125 | -0.25 | 6.62 | 252 | — | 2026-10-02 | [C18] [C16]; calc: (bid + ask) / 2 |
| Loan comparable | Caesars Entertainment, Inc. Term Loan B-1 | BL4120876 | Ba3/BB | 2835 | USD | MILLIONS | 225 | 2031-02-06 | 1st Lien | 99.6875 | 0.125 | -0.125 | 6.55 | 241 | — | 2026-10-02 | [C19] [C16]; calc: (bid + ask) / 2 |
| Loan comparable | Station Casinos LLC Term Loan B | BL3550912 | Ba2/BB+ | 1500 | USD | MILLIONS | 200 | 2031-03-14 | 1st Lien | 100.125 | 0 | 0.125 | 6.21 | 202 | — | 2026-10-02 | [C20] [C16]; calc: (bid + ask) / 2 |
| Loan comparable | Light and Wonder International, Inc. Term Loan B | BL3640021 | Ba2/BB | 2200 | USD | MILLIONS | 225 | 2029-04-14 | 1st Lien | 100.25 | 0 | 0.25 | 6.38 | 218 | — | 2026-10-02 | [C21] [C16]; calc: (bid + ask) / 2 |
| Loan comparable | Golden Entertainment, Inc. Term Loan B | BL3729054 | B1/BB- | 400 | USD | MILLIONS | 275 | 2030-05-28 | 1st Lien | 99.25 | -0.25 | -0.5 | 7.36 | 296 | — | 2026-10-02 | [C22] [C16]; calc: (bid + ask) / 2 |
| Loan comparable | Fertitta Entertainment, LLC Term Loan B | BL3488123 | B2/B | 2700 | USD | MILLIONS | 350 | 2029-01-27 | 1st Lien | 99.5 | 0.25 | 0.125 | 8.02 | 366 | — | 2026-10-02 | [C23] [C16]; calc: (bid + ask) / 2 |

<!-- table: cp3.talk_valuation -->
| facility_id | talk_stage | talk_low | talk_mid | talk_high | oid | metric_basis | implied_low | implied_mid | implied_high | comparable_level | comparable_basis | verdict | cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NEW-1 | Initial talk | 300 | 312.5 | 325 | 99.25 | 3Y DM | 316.67 | 337.50 | 358.33 | 239.57 | Caesars Term Loan B, 3Y DM at the mid on 2026-10-02 | V2 - Attractive | [C1] [C2] [C3]; calc: bond_analytics NEW-1 |

<!-- table: cp3.compensation -->
| facility_id | structural_rank | recovery_sensitivity | compensation_vs_risk | comparables | cite |
|---|---|---|---|---|---|
| CEI-TLB | 1 (first-lien senior secured) | Medium | Adequate | BB loan index 248; gaming BB average 228 | [C5] [C12] |
| CEI-TLB-1 | 1 (first-lien senior secured) | Medium | Adequate | BB loan index 248; gaming BB average 228 | [C5] [C12] |
| CEI-SSN-2030 | 1 (first-lien senior secured notes) | Medium | Adequate | the issuer's 2032 secured notes | [C13] |
| CEI-SSN-2032 | 1 (first-lien senior secured notes) | Medium | Attractive | the issuer's 2030 secured notes | [C9] |
| CEI-SN-2029 | 2 (senior unsecured) | High | Inadequate | PENN 4.125% notes due 2029 at 6.65 | [C11] |
| CEI-SN-2032 | 2 (senior unsecured) | High | Adequate | the issuer's 2032 secured notes | [C13] |
| NEW-1 | 1 (first-lien senior secured, pari passu) | Medium | Attractive | the issuer's term loans; BB index; gaming B average 331 | [C3] [C5] [C6] [C24] |

<!-- table: cp3.security_preference -->
| facility_id | preference | key_reason | monitoring_trigger | cite |
|---|---|---|---|---|
| NEW-1 | Preferred | first-lien rank at about 100 bps over the issuer's own loans | final margin set below SOFR + 300 or the OID above 99.5 | [C1] [C2] |
| CEI-TLB | Neutral | fair for its rank; diluted by the new secured debt | the new loan's final terms | [C3] |
| CEI-TLB-1 | Neutral | fair for its rank; diluted by the new secured debt | the new loan's final terms | [C4] |
| CEI-SSN-2030 | Neutral | fair carry; near-dated against the 2030 term loan maturity | the call schedule from the 2030 indenture | [C9] |
| CEI-SSN-2032 | Preferred | secured rank at a discount price and the widest secured yield | a downgrade from B1 on closing | [C8] [C25] |
| CEI-SN-2029 | Avoid | priced like a B3 peer while new secured debt primes it | a tender or change-of-control offer on closing | [C10] [C11] |
| CEI-SN-2032 | Requires more work | wide yield but most exposed to the added secured debt | the 2032 senior notes indenture's change-of-control terms | [C14] |

## Gaps

- `SYNTHETIC_Levels_Screenshot.png`: its levels are Image-Read Values and are not used.
- No `snapshot.instrument_levels` row for the CEI revolver, Term Loan A, the CVA Delayed Draw Term Loan, the Special Improvement District Bonds and the other payables: no Market level in the pack.
- No reference rate or forward curve: the term loans' 0.50% floor benefit is not computed (the DMs exclude it).
- Call schedules are in the pack for the 2032 secured notes only; the other bonds' YTW is their yield to maturity.
- No benchmark Treasury yield: no spread to worst; the HY block of `snapshot.relative_value` is empty because no bond in the pack has a stated spread.
- PENN's term loan in the Sector RV Workbook has `#N/A` levels and is left out.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Price Talk \| SOFR + 300–325 bps (initial talk) |
| C2 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | OID \| 99.0–99.5 |
| C3 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 4 | CZR TL B 2030 BL3912045  1L Term Loan 99.375 99.750 99.563  252 Ba3 BB |
| C4 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 5 | CZR TL B-1 2031 BL4120876  1L Term Loan 99.500 99.875 99.688  241 Ba3 BB |
| C5 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, Index Statistics | Morningstar LSTA US Leveraged Loan Index BB SPBDLLBB 512000 99.62 0.12 0.41 6.71 248 |
| C6 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, Sector Ratings Average | B 2 1550 313 99.13 99.63 7.69 331 |
| C7 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Expected facility ratings \| Ba3 (Moody's) / BB- (S&P) |
| C8 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 7 | CZR 6.50 02/15/32 BO2201453 US12769GAC44 Senior Secured Notes 93.000 93.500 93.250 8.07 |
| C9 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 6 | CZR 7.00 02/15/30 BO1185520 US12769GAA87 Senior Secured Notes 101.250 101.750 101.500 6.41 |
| C10 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 8 | CZR 4.625 10/15/29 BO1203310 US12769GAB60 Senior Notes 94.250 94.875 94.563 6.52 |
| C11 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 11 | PENN 4.125 07/01/29 BO1164521 US707569AV19 Senior Notes 93.500 94.000 93.750 6.65 |
| C12 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, Sector Ratings Average | BB 4 1878 219 99.75 100.06 6.44 228 |
| C13 | CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | Paragraph 5, optional redemption | 2029 and thereafter \| 100.000% |
| C14 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 9 | CZR 6.00 10/15/32 BO2219978 US12769GAD27 Senior Notes 84.500 85.250 84.875 9.33 |
| C15 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, Index Statistics | Morningstar LSTA US Leveraged Loan Index SPBDAL 1452300 96.84 0.21 0.94 8.11 389 |
| C16 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, title | Gaming: loan relative value as of 2026-10-02 |
| C17 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, Index Statistics | Morningstar LSTA US Leveraged Loan Index B SPBDLLB 801500 97.15 0.24 1.02 8.04 381 |
| C18 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, issuers | BL3912045 B 1st Lien Ba3/BB 2018 225 2030-02-06 99.375 99.75 0.125 -0.25 6.62 252 |
| C19 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, issuers | BL4120876 B-1 1st Lien Ba3/BB 2835 225 2031-02-06 99.5 99.875 0.125 -0.125 6.55 241 |
| C20 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, issuers | BL3550912 B 1st Lien Ba2/BB+ 1500 200 2031-03-14 100 100.25 0 0.125 6.21 202 |
| C21 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, issuers | BL3640021 B 1st Lien Ba2/BB 2200 225 2029-04-14 100.125 100.375 0 0.25 6.38 218 |
| C22 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, issuers | BL3729054 B 1st Lien B1/BB- 400 275 2030-05-28 99 99.5 -0.25 -0.5 7.36 296 |
| C23 | SYNTHETIC_Sector_RV_Gaming.xlsx | sheet Gaming, issuers | BL3488123 B 1st Lien B2/B 2700 350 2029-01-27 99.25 99.75 0.25 0.125 8.02 366 |
| C24 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | Summary of terms | Pari passu with the existing CEI senior secured credit facilities and senior secured notes |
| C25 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | Moody's rating shown: B1 |
