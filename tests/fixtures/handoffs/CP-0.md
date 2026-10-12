---
module_id: CP-0
run_id: 20261011-czr-pending
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Pass
inputs: none
---

## Analysis

Hand-written test fixture of a CP-0 Handoff for the synthetic Primary pack `czr-2026q2-primary`. The pack supports Full Credit Assessment work on Caesars: the FY2025 annual report, the Q2 2026 quarterly report and earnings release, the credit agreement amendments and the 2032 notes indentures, Market Levels, the Sector RV Workbook, a term sheet for a new senior secured term loan [C3] and the Test CLO I positions [C16] and limits [C17]. Two files cannot be used as issuer evidence: a Virgin Media O2 bond report is misfiled, and the levels screenshot holds Image-Read Values only.

## Tables

<!-- table: cp0.source_inventory -->
| file | class | document_type | entity_named | entity_match | period_covered | document_date | readable | image_read | pages | sha256 | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CZR_2024_650_Notes_First_Supplemental_Indenture.txt | issuer | Indenture | Caesars Entertainment, Inc. | Yes | — | 2024-03-01 | Yes | No | 1 | 0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219 | supplements the 2032 notes indenture |
| CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | issuer | Indenture | Caesars Entertainment, Inc. | Yes | — | 2024-08-23 | Yes | No | 1 | 3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea | supplements the 2032 notes indenture |
| CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | issuer | Indenture | Caesars Entertainment, Inc. | Yes | — | 2024-02-06 | Yes | No | 1 | 0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119 | base indenture of the 6.50% senior secured notes due 2032 |
| CZR_2024_Credit_Agreement_Fifth_Amendment.txt | issuer | Credit agreement | Caesars Entertainment, Inc. | Yes | — | 2024-11-25 | Yes | No | 1 | 7f2b5c777dc3347938a007eaea63a623b299a1188dbcfbe8980d389a0bcfc5b3 | amends the 2020 credit agreement (base not in the pack) |
| CZR_2024_Credit_Agreement_Fourth_Amendment.txt | issuer | Credit agreement | Caesars Entertainment, Inc. | Yes | — | 2024-05-09 | Yes | No | 1 | 32f91de6ef3ff93d9924eb8d4e3dc4734d28b68ed1da0f816a085ffdcb085c95 | amends the 2020 credit agreement (base not in the pack) |
| CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | issuer | Credit agreement | Caesars Entertainment, Inc. | Yes | — | 2024-02-06 | Yes | No | 1 | 25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c | incremental assumption agreement under the 2020 credit agreement |
| CZR_2026_Merger_Agreement.txt | issuer | Other | Caesars Entertainment, Inc. | Yes | — | 2026-05-27 | Yes | No | 1 | e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c | merger agreement with Fertitta Gaming Holdco, LLC |
| CZR_2026_Merger_Agreement_8K.txt | issuer | Other | Caesars Entertainment, Inc. | Yes | — | 2026-05-27 | Yes | No | 1 | 6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169 | current report on the merger agreement |
| CZR_2026_Merger_Press_Release.txt | issuer | Other | Caesars Entertainment, Inc. | Yes | — | 2026-05-28 | Yes | No | 1 | 4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b | press release on the merger |
| CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | market | Market levels export | CAESARS ENTMT INC | Yes | — | 2026-10-02 | Yes | No | 1 | 4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51 | TRACE trades in CUSIP 12769GAC4 |
| CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | market | Market levels export | CAESARS ENTMT INC | Yes | — | 2026-10-02 | Yes | No | 1 | 256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24 | TRACE trades in CUSIP 12769GAD2 |
| CZR_FY2025_10K.txt | issuer | Annual report | Caesars Entertainment, Inc. | Yes | FY2025 | 2026-02-12 | Yes | No | 1 | 172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512 | — |
| CZR_Q2_2026_10Q.txt | issuer | Quarterly report | Caesars Entertainment, Inc. | Yes | six months to 2026-06-30 | 2026-07-23 | Yes | No | 1 | f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a | — |
| CZR_Q2_2026_Earnings_Release.txt | issuer | Earnings release | Caesars Entertainment, Inc. | Yes | Q2 2026 | 2026-07-28 | Yes | No | 1 | b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8 | — |
| FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt | portfolio | Portfolio positions | Federated Hermes Sustainable High Yield Bond Fund, Inc. | No | — | 2026-06-30 | Yes | No | 1 | e2490912d9cc688135e15732e0fcf4aafd715e91e4d580edd577483535507bab | a public fund's schedule of investments, not one of the analyst's portfolios |
| FHSUHY_Prospectus_and_SAI_2026-05-26.txt | portfolio | Portfolio limits | Federated Hermes Sustainable High Yield Bond Fund, Inc. | No | — | 2026-05-26 | Yes | No | 1 | 10455d54958421c56b4902f2fa41bfc08873bb9d16ee9fb22ab31ded215846ea | a public fund's prospectus, not one of the analyst's portfolios |
| MGM_FINRA_TRACE_552953CK5_2026-10-02.txt | market | Market levels export | MGM Resorts International | Yes | — | 2026-10-02 | Yes | No | 1 | e17cea1bb90debdeb8c1fea9c352132b57ae9b27ee0d3225fb67c6466d7d0e4a | comparable issuer's TRACE trades |
| MGM_Q2_2026_Earnings_Release.txt | market | Earnings release | MGM Resorts International | Yes | Q2 2026 | 2026-07-29 | Yes | No | 1 | 795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb | comparable issuer |
| PENN_FINRA_TRACE_707569AV1_2026-10-02.txt | market | Market levels export | PENN ENTMT INC | Yes | — | 2026-10-02 | Yes | No | 1 | 666c0f36ace32336dffbcff324eaec5b4657edade407bb0b8a0e8d8fb405de6d | comparable issuer's TRACE trades |
| PENN_Q2_2026_Earnings_Release.txt | market | Earnings release | PENN Entertainment, Inc. | Yes | Q2 2026 | 2026-08-06 | Yes | No | 1 | 4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c | comparable issuer |
| SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | market | Market levels export | Caesars Entertainment, Inc. | Yes | — | 2026-10-02 | Yes | No | 1 | 85b00e2decdff09c8258daabaab56cba5d35c4846153d55523435abffff0a2fa | SYNTHETIC test file; #N/A cells are missing values |
| SYNTHETIC_CZR_2026_PF_Capitalisation.md | issuer | Lender presentation | Caesars Entertainment, Inc. | Yes | 2026-06-30 pro forma | — | Yes | No | 1 | 23ae4d3c2cc09604884c95ae06ab6a0a20c4cd367a413f41e12fb8027157bd49 | SYNTHETIC test file: pro forma capitalisation |
| SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | issuer | Term sheet | Caesars Entertainment, Inc. | Yes | — | 2026-09-29 | Yes | No | 1 | 5caa5d1d322ca5e2778f14970b4ba41c4c04d507d59844c1b9f4c10834e0517d | SYNTHETIC test file: new Term Loan B terms and Price Talk |
| SYNTHETIC_Levels_Screenshot.png | market | Market levels export | Not identified | Yes | — | — | No | Yes | 1 | de535203f4a7476b8ca8d27749e5408818898fea07711795ee849c3c47d44e3d | screenshot: its levels are Image-Read Values |
| SYNTHETIC_Sector_RV_Gaming.xlsx | market | Sector RV Workbook | Caesars Entertainment, Inc. | Yes | — | 2026-10-02 | Yes | No | 1 | c25d7d1893f172c81536a0baafe837acdde4db2dffa9766a7a5141cd8d958ef1 | SYNTHETIC test file: gaming loan relative value |
| SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | portfolio | Portfolio limits | Test CLO I Ltd | Yes | — | 2026-05-29 | Yes | No | 1 | 039e5b7e03677062a8ac6f081587f9c771b4c32af3b3c9fe7dd8573776e9b021 | SYNTHETIC test file |
| SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | portfolio | Portfolio positions | Test CLO I Ltd | Yes | — | 2026-05-29 | Yes | No | 1 | 35c5d82b5128b53ca2a32ab3f9f51e8552c197c9b8e522b6e0d3e735921d8a0d | SYNTHETIC test file |
| TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt | portfolio | Portfolio limits | Test CLO I Ltd | Yes | — | 2026-10-02 | Yes | No | 1 | 864ee90ab21372bcf89c8b27e02cd5d691d9095a64d507c7f656d5963cfe3207 | mandate text behind the limits file |
| TRACE_12769GAC4_last_trade.txt | market | Market levels export | CAESARS ENTMT INC | Yes | — | 2026-10-02 | Yes | No | 1 | 4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51 | duplicate of CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt |
| VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf | issuer | Bond report | VMED O2 UK HOLDINGS LIMITED | No | Q1 2026 | 2026-03-31 | Yes | No | 47 | 4ec0fed1044430a13a2e38e24c822847149571002651e897f3f076abc61c79be | misfiled: a Virgin Media O2 bond report, not about Caesars |

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

- `VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf`: a Virgin Media O2 bond report in a Caesars pack; excluded as issuer evidence.
- `SYNTHETIC_Levels_Screenshot.png`: levels readable only as Image-Read Values; the Bloomberg export and TRACE files carry the same securities.
- `TRACE_12769GAC4_last_trade.txt`: duplicate of `CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt`.
- The 2020 credit agreement the amendments modify is not in the pack.
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
| C10 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | OID 99.0–99.5 |
| C11 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Maturity 2033-12-15 |
| C12 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Expected facility ratings Ba3 (Moody's) / BB- (S&P) |
| C13 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Commitment date 2026-10-08 |
| C14 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Bloomberg ID and CUSIP are not yet assigned |
| C15 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | No Covenant Review score has been published |
| C16 | SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | p.1 | Portfolio ID TEST_CLO_I |
| C17 | SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | p.1 | Portfolio ID TEST_CLO_I |
