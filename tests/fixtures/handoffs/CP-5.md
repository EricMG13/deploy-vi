---
module_id: CP-5
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Pass
inputs: CP-0, CP-1, CP-1A, CP-1B, CP-1D, CP-2, CP-3, MODEL, FIT
---

## Analysis

Hand-written test fixture of a CP-5 Handoff for the synthetic Primary pack `czr-2026q2-primary`. Overall, evidence traceability is Ready with Remediation. Of the Top 5 material credit drivers (Las Vegas earnings, the acquisition debt, the lease fixed charges, the new loan's talk valuation, the Portfolio Fit caps), 3 are directly sourced, 2 are calculated, 0 are assumption-based, 0 are analyst inferences, and 0 are weak-lineage, untraced or conflicting items. The upstream Handoffs agree on the debt stack, the ratings and the house EBITDA, and no High finding is open.

The provenance gap that matters most is the Structuring EBITDA. CP-1 registers the arranger's 150 of run-rate synergies on the LTM period [C1], but the Model builds the LTM from the fiscal year and the half-years, so its Structuring EBITDA (3,592) leaves the synergies out and equals SSIM EBITDA; the marketed figure would be 3,742. The decision rests on SSIM EBITDA, so the gap changes a Front Page line, not the call. Second, CP-3's discount margins are the house convention and sit 12 to 6 bps below the Bloomberg export's own figures [C2]; CP-3 states both.

## Tables

<!-- table: cp5.findings -->
| finding_id | severity | module_id | kind | description | required_fix | status |
|---|---|---|---|---|---|---|
| F-1 | Medium | MODEL | Calculation | Structuring EBITDA on the PF-LTM is 3,592: the 150 of run-rate synergies CP-1 registers on LTM_Q2_2026 is not in it (the Model reads an add-back on the LTM from its parts) | carry an add-back stated only for the LTM into the PF-LTM's Structuring EBITDA | Open |
| F-2 | Low | CP-3 | Market | the house 3Y DM of the CEI Term Loan B (239.57) differs from the Bloomberg export's 252, and of the B-1 (235.40) from 241 | none: CP-3 shows both; the floor benefit is excluded for want of a reference rate | Accepted |
| F-3 | Low | CP-1 | Lineage | the new term loan's terms, the pro forma capitalisation and the synergies come from SYNTHETIC test files | none in a test run; a live run needs the lender presentation | Accepted |

<!-- table: cp5.limitations -->
| module_id | limitation | effect_on_decision | source_that_would_lift |
|---|---|---|---|
| MODEL | no EV: no listed equity value and no SSIM EV multiple | no % of EV per facility on the capital structure | an equity value export, or the SSIM EV multiple in the Run Brief |
| MODEL | Structuring EBITDA leaves out the 150 of LTM synergies | the marketed multiple is overstated against the arranger's figure | a Model that carries LTM-only add-backs |
| CP-3 | no reference rate: the 0.50% floors' benefit is not computed | DMs are a floor-free lower bound | a SOFR forward curve in Market Context |
| CP-1A | no corporate family or issuer ratings in the pack | the ratings block shows instrument ratings only | an agency report |
| FIT | minimum limits (rating floor, first-lien share, obligor count) are not sized against | the Portfolio Fit verdict covers maximum limits only | none: RBOT sizes against maximum limits by design |

<!-- table: cp5.module_status -->
| module_id | qa_status | traceability | note |
|---|---|---|---|
| CP-0 | Pass | Traceable | — |
| CP-1 | Restricted | Traceable | FY2023 debt and most call schedules are not in the pack |
| CP-1A | Restricted | Traceable | no corporate ratings |
| CP-1B | Restricted | Traceable | no KPIs and no guidance in the pack |
| CP-1D | Restricted | Traceable | synergy actions not evidenced |
| MODEL | Pass | Partly traceable | Structuring EBITDA misses the LTM synergies (F-1) |
| CP-2 | Restricted | Traceable | — |
| CP-3 | Restricted | Traceable | floor benefit and STW not computed |
| FIT | Restricted | Traceable | minimum limits not sized |

## Gaps

- No CP-1C, CP-2A, CP-4 or other full-depth modules in this run's Pathway list yet: their checks are absent.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | SYNTHETIC_CZR_2026_PF_Capitalisation.md | Earnings and interest | Run-rate cost synergies identified by Fertitta Entertainment, not yet realised \| 150 |
| C2 | SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | sheet SYNTHETIC_Bloomberg_Levels_2026-10-02, row 4 | CZR TL B 2030,BL3912045,,1L Term Loan,99.375,99.750,99.563,,252,Ba3,BB |
