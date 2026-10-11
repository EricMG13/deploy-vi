---
module_id: CP-0
run_id: 20261011-czr-pending
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Pass
inputs: none
---

## Analysis

Hand-written test fixture: the CP-0 tables `rbot brief` reads, for the synthetic Primary pack `czr-2026q2-primary`. The pack holds a term sheet for a new senior secured term loan [C3] and the Test CLO I positions [C16] and limits [C17].

## Tables

<!-- table: cp0.run_brief_prefill -->
| field | tranche_id | value | status | cite |
|---|---|---|---|---|
| issuer | | Caesars Entertainment, Inc. | Sourced | [C1] |
| issuer_id | | CZR | Sourced | [C1] |
| as_of_date | | 2026-10-02 | Sourced | [C2] |
| objective | | — | Gap | |
| analyst | | — | Gap | |
| primary | | Yes | Sourced | [C3] |
| morningstar_issuer_id | | — | Gap | |
| ssim_ev_multiple | | — | Gap | |
| borrower | NEW-1 | Caesars Entertainment, Inc. | Sourced | [C4] |
| instrument | NEW-1 | New Senior Secured Term Loan B | Sourced | [C3] |
| debt_type | NEW-1 | 1L Term Loan | Sourced | [C5] |
| use_of_proceeds | NEW-1 | Acquisition | Sourced | [C6] |
| size | NEW-1 | 3000 | Sourced | [C7] |
| currency | NEW-1 | USD | Sourced | [C7] |
| unit | NEW-1 | MILLIONS | Sourced | [C7] |
| price_talk | NEW-1 | SOFR + 300–325 bps | Sourced | [C8] |
| talk_stage | NEW-1 | Initial talk | Sourced | [C9] |
| oid | NEW-1 | 99.0–99.5 | Sourced | [C10] |
| maturity_date | NEW-1 | 2033-12-15 | Sourced | [C11] |
| expected_ratings | NEW-1 | Ba3 / BB- | Sourced | [C12] |
| commitment_date | NEW-1 | 2026-10-08 | Sourced | [C13] |
| bloomberg_id | NEW-1 | — | Gap | [C14] |
| cr_score | NEW-1 | — | Gap | [C15] |

<!-- table: cp0.research_questions -->
| question_id | question | why_it_matters | consumer_module | evidence_needed |
|---|---|---|---|---|
| RQ-1 | How is Las Vegas Strip visitation trending into 2027? | Las Vegas drives the largest segment's Adjusted EBITDA | CP-2 | Visitation and convention statistics |

<!-- table: cp0.prior_case -->
| file | report_date | run_id | pathway | depth | offered |
|---|---|---|---|---|---|

<!-- table: cp0.portfolios -->
| portfolio_id | portfolio_name | strategy | positions_file | limits_file | as_of_date |
|---|---|---|---|---|---|
| TEST_CLO_I | Test CLO I Ltd | CLO | SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | 2026-05-29 |

## Gaps

- `objective`, `analyst`: the analyst gives them at turn 1.
- `morningstar_issuer_id`, `ssim_ev_multiple`: not in the pack; the issuer is listed, so EV uses its equity value.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_Q2_2026_10Q.txt | p.1 | CAESARS ENTERTAINMENT, INC. (Exact name of registrant as specified in its charter) |
| C2 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | Observed at: 2026-10-02T09:31:13Z |
| C3 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Facility New Senior Secured Term Loan B |
| C4 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Borrower Caesars Entertainment, Inc. |
| C5 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Debt type First lien term loan |
| C6 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Use of proceeds Acquisition |
| C7 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Size USD 3,000 million |
| C8 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Price Talk SOFR + 300–325 bps (initial talk) |
| C9 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Marketing stage: initial talk |
| C10 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | OID 99.0–99.5 Maturity 2033-12-15 |
| C11 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Maturity 2033-12-15 (seven years from expected closing) |
| C12 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Expected facility ratings Ba3 (Moody's) / BB- (S&P) |
| C13 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Commitment date 2026-10-08 |
| C14 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Bloomberg ID and CUSIP are not yet assigned |
| C15 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | No Covenant Review score has been published |
| C16 | SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | p.1 | Portfolio ID TEST_CLO_I Portfolio Test CLO I Ltd |
| C17 | SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | p.1 | Portfolio ID TEST_CLO_I As of 2026-05-29 |
