# Scorecard: FULL_CREDIT_ASSESSMENT full on czr-2026q2-primary

- Run: 20261017-czr-full-credit-assessment; created 2026-10-17T16:45:28+00:00
- Steps accepted (verified): 12/12
- Report: written 2026-10-17T20:13:04+00:00; html b1d1e0cb207c868af57a688bb345d8093a90485e87c6c7906e874e46d0f8a80f; md eaeb6d0b61c5eab5106774bb602a7fb2471ca93f6034e616cdd5f47974db1907
- Fetch: off
- Source: recorded run evidence only; nothing here was re-run or estimated.

## Steps

| Step | Kind | Status | Accepted (verified) | QA | Attempts | Validate exit per attempt | Citations anchored/total | Image-Read citations | Gaps | Bytes | Started | Finished | Duration | Model label | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CP-0 | module | accepted | yes | Restricted | 1 | 1:0 | 75/75 | 0 | 15 | 45714 B | 2026-10-17T16:45:36.020824+00:00 | 2026-10-17T16:54:24.042979+00:00 | 528.022s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1 | module | accepted | yes | Restricted | 1 | 1:0 | 207/207 | 0 | 14 | 90171 B | 2026-10-17T16:55:10.934659+00:00 | 2026-10-17T17:23:40.325592+00:00 | 1709.39s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1A | module | accepted | yes | Restricted | 1 | 1:0 | 169/169 | 0 | 0 | 66960 B | 2026-10-17T17:25:53.805718+00:00 | 2026-10-17T17:39:08.924889+00:00 | 795.119s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-DR | module | accepted | yes | Restricted | 1 | 1:0 | 53/53 | 0 | 6 | 35022 B | 2026-10-17T17:40:30.388836+00:00 | 2026-10-17T17:53:18.438950+00:00 | 768.05s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1B | module | accepted | yes | Restricted | 1 | 1:0 | 156/156 | 0 | 0 | 78252 B | 2026-10-17T17:55:19.356146+00:00 | 2026-10-17T18:09:57.612135+00:00 | 878.256s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1D | module | accepted | yes | Restricted | 1 | 1:0 | 87/87 | 0 | 12 | 51173 B | 2026-10-17T18:13:12.271281+00:00 | 2026-10-17T18:30:00.828016+00:00 | 1008.56s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| MODEL | host | accepted | yes | Pass | 1 | unknown | 54/54 | 0 | unknown | 29106 B | 2026-10-17T18:30:58.051589+00:00 | 2026-10-17T18:31:30.828934+00:00 | 32.7773s | unknown | - |
| CP-2 | module | accepted | yes | Restricted | 1 | 1:0 | 119/119 | 0 | 0 | 63461 B | 2026-10-17T18:35:37.682988+00:00 | 2026-10-17T18:48:06.059100+00:00 | 748.376s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-3 | module | accepted | yes | Restricted | 1 | 1:0 | 123/123 | 0 | 0 | 76146 B | 2026-10-17T18:51:56.853217+00:00 | 2026-10-17T19:18:17.141777+00:00 | 1580.29s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| FIT | host | accepted | yes | Restricted | 1 | unknown | unknown (no citation rows) | 0 | unknown | 29950 B | 2026-10-17T19:20:08.168489+00:00 | 2026-10-17T19:20:51.861997+00:00 | 43.6935s | unknown | - |
| CP-5 | module | accepted | yes | Restricted | 1 | 1:0 | 42/42 | 0 | 0 | 44253 B | 2026-10-17T19:29:07.471568+00:00 | 2026-10-17T19:47:21.554254+00:00 | 1094.08s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-6 | module | accepted | yes | Restricted | 1 | 1:0 | 47/47 | 0 | 0 | 43073 B | 2026-10-17T19:52:47.375947+00:00 | 2026-10-17T20:08:07.063010+00:00 | 919.687s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |

## Front Page completeness

| Owner | Critical cells filled/supportable | Note |
|---|---|---|
| CP-1A | 9/9 | - |
| CP-1B | 2/2 | - |
| CP-2 | 24/24 | - |
| CP-3 | 129/129 | - |
| CP-6 | 15/15 | - |
| FIT | 156/156 | - |

Overall measured owners: 335/335.

Not measured (owned by a host step or no module in this plan, and the expectations give no expected_rows denominator; none is invented): snapshot.capital_structure (MODEL), snapshot.capital_structure_totals (MODEL), snapshot.ebitda_adjustments (MODEL), snapshot.financial_columns (MODEL), snapshot.financials (MODEL), snapshot.run_header (RUN_BRIEF), snapshot.transaction_summary (RUN_BRIEF).

## Model

- Limitations (5): NO_PROJECTIONS, CELL_NOTE, EV_NOT_AVAILABLE, MATURITY_NOT_STATED, SOURCES_CUT
- Reconciliation faults (0): none

## Sources

| Path | sha256 | Now |
|---|---|---|
| CZR_2024_650_Notes_First_Supplemental_Indenture.txt | 0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219 | unchanged |
| CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | 3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea | unchanged |
| CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | 0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119 | unchanged |
| CZR_2024_Credit_Agreement_Fifth_Amendment.txt | 7f2b5c777dc3347938a007eaea63a623b299a1188dbcfbe8980d389a0bcfc5b3 | unchanged |
| CZR_2024_Credit_Agreement_Fourth_Amendment.txt | 32f91de6ef3ff93d9924eb8d4e3dc4734d28b68ed1da0f816a085ffdcb085c95 | unchanged |
| CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | 25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c | unchanged |
| CZR_2026_Merger_Agreement.txt | e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c | unchanged |
| CZR_2026_Merger_Agreement_8K.txt | 6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169 | unchanged |
| CZR_2026_Merger_Press_Release.txt | 4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b | unchanged |
| CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | 4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51 | unchanged |
| CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | 256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24 | unchanged |
| CZR_FY2025_10K.txt | 172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512 | unchanged |
| CZR_Q2_2026_10Q.txt | f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a | unchanged |
| CZR_Q2_2026_Earnings_Release.txt | b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8 | unchanged |
| FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt | e2490912d9cc688135e15732e0fcf4aafd715e91e4d580edd577483535507bab | unchanged |
| FHSUHY_Prospectus_and_SAI_2026-05-26.txt | 10455d54958421c56b4902f2fa41bfc08873bb9d16ee9fb22ab31ded215846ea | unchanged |
| MGM_FINRA_TRACE_552953CK5_2026-10-02.txt | e17cea1bb90debdeb8c1fea9c352132b57ae9b27ee0d3225fb67c6466d7d0e4a | unchanged |
| MGM_Q2_2026_Earnings_Release.txt | 795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb | unchanged |
| PENN_FINRA_TRACE_707569AV1_2026-10-02.txt | 666c0f36ace32336dffbcff324eaec5b4657edade407bb0b8a0e8d8fb405de6d | unchanged |
| PENN_Q2_2026_Earnings_Release.txt | 4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c | unchanged |
| SYNTHETIC_Bloomberg_Levels_2026-10-02.csv | 85b00e2decdff09c8258daabaab56cba5d35c4846153d55523435abffff0a2fa | unchanged |
| SYNTHETIC_CZR_2026_PF_Capitalisation.md | 23ae4d3c2cc09604884c95ae06ab6a0a20c4cd367a413f41e12fb8027157bd49 | unchanged |
| SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | 5caa5d1d322ca5e2778f14970b4ba41c4c04d507d59844c1b9f4c10834e0517d | unchanged |
| SYNTHETIC_Levels_Screenshot.png | de535203f4a7476b8ca8d27749e5408818898fea07711795ee849c3c47d44e3d | unchanged |
| SYNTHETIC_Sector_RV_Gaming.xlsx | c25d7d1893f172c81536a0baafe837acdde4db2dffa9766a7a5141cd8d958ef1 | unchanged |
| SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | 039e5b7e03677062a8ac6f081587f9c771b4c32af3b3c9fe7dd8573776e9b021 | unchanged |
| SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | 35c5d82b5128b53ca2a32ab3f9f51e8552c197c9b8e522b6e0d3e735921d8a0d | unchanged |
| TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt | 864ee90ab21372bcf89c8b27e02cd5d691d9095a64d507c7f656d5963cfe3207 | unchanged |
| TRACE_12769GAC4_last_trade.txt | 4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51 | unchanged |
| VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf | 4ec0fed1044430a13a2e38e24c822847149571002651e897f3f076abc61c79be | unchanged |

## Fit

- fit files: TEST_CLO_I.json (75189 B)

Not verified: Copilot behaviour (this is a proxy run, never a certification), GPT models, fetch (fetch was off, so no network fetch was run or measured), the provider identity behind model labels (caller-reported), worker isolation beyond the dispatch message, module A/B qualification (pending from Plan 05), and report rendering unless the Report line says it was written.
