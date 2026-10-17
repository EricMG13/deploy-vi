# Scorecard: FULL_CREDIT_ASSESSMENT quick on czr-2026q2-lite-full-credit-screen

- Run: 20261016-czr-full-credit-assessment; created 2026-10-16T19:34:10+00:00
- Steps accepted (verified): 9/10
- Report: written 2026-10-16T20:46:21+00:00; html f3ca49976aeca49ca98bd92ad807b2968061bbc946cbab6d88ebe2021523d5a7; md 59647e2c8c8b47d3ead4bd4e6a0d82cb069da04a999ed880bca0f79657ac9050
- Source: recorded run evidence only; nothing here was re-run or estimated.

## Steps

| Step | Kind | Status | Accepted (verified) | QA | Attempts | Validate exit per attempt | Citations anchored/total | Image-Read citations | Gaps | Bytes | Started | Finished | Duration | Model label | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CP-0 | module | accepted | yes | Pass | 1 | 1:0 | 30/30 | 0 | 0 | 23706 B | 2026-10-16T19:34:11.640602+00:00 | 2026-10-16T19:38:42.214464+00:00 | 270.574s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1 | module | accepted | yes | Restricted | 1 | 1:0 | 177/177 | 0 | 0 | 87434 B | 2026-10-16T19:38:55.231175+00:00 | 2026-10-16T19:55:34.991810+00:00 | 999.761s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1A | module | accepted | yes | Restricted | 1 | 1:0 | 66/66 | 0 | 10 | 34950 B | 2026-10-16T19:56:11.041886+00:00 | 2026-10-16T20:01:36.015605+00:00 | 324.974s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-1B | module | accepted | yes | Restricted | 1 | 1:0 | 61/61 | 0 | 0 | 29781 B | 2026-10-16T20:02:17.089167+00:00 | 2026-10-16T20:06:51.171729+00:00 | 274.083s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| MODEL | host | accepted | yes | Pass | 1 | unknown | 13/13 | 0 | unknown | 23035 B | 2026-10-16T20:07:13.592957+00:00 | 2026-10-16T20:07:28.333693+00:00 | 14.7407s | unknown | - |
| CP-L10 | module | accepted | yes | Restricted | 1 | 1:0 | 101/101 | 0 | 12 | 48364 B | 2026-10-16T20:09:10.392967+00:00 | 2026-10-16T20:19:10.977204+00:00 | 600.584s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-3 | module | accepted | yes | Restricted | 1 | 1:0 | 30/30 | 0 | 0 | 23967 B | 2026-10-16T20:20:47.362320+00:00 | 2026-10-16T20:27:20.688780+00:00 | 393.326s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| FIT | host | skipped | no | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | reason: no portfolio context |
| CP-5 | module | accepted | yes | Pass | 1 | 1:0 | 28/28 | 0 | 0 | 32453 B | 2026-10-16T20:29:09.555050+00:00 | 2026-10-16T20:40:42.408672+00:00 | 692.854s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |
| CP-6 | module | accepted | yes | Restricted | 1 | 1:0 | 23/23 | 0 | 0 | 18579 B | 2026-10-16T20:41:57.142754+00:00 | 2026-10-16T20:45:57.405567+00:00 | 240.263s | claude-sonnet-5-5 | worker start time unknown; re-validation exit 0 |

## Front Page completeness

| Owner | Critical cells filled/supportable | Note |
|---|---|---|
| CP-1A | 8/9 | - |
| CP-1B | 2/2 | - |
| CP-L10 | 16/16 | - |
| CP-3 | 18/18 | - |
| CP-6 | 32/34 | - |

Overall measured owners: 76/79.

Not measured (owned by a host step or no module in this plan, and the expectations give no expected_rows denominator; none is invented): snapshot.capital_structure (MODEL), snapshot.capital_structure_totals (MODEL), snapshot.ebitda_adjustments (MODEL), snapshot.financial_columns (MODEL), snapshot.financials (MODEL), snapshot.run_header (RUN_BRIEF).

## Model

- Limitations (8): NO_PROJECTIONS, CELL_NOTE, PF_LTM_EQUALS_LTM, EV_NOT_AVAILABLE, MATURITY_CALENDAR_YEAR, MATURITY_NOT_STATED, SOURCES_CUT, CP1D_NOT_READ
- Reconciliation faults (0): none

## Sources

| Path | sha256 | Now |
|---|---|---|
| CZR_2024_650_Notes_First_Supplemental_Indenture.txt | 0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219 | unchanged |
| CZR_2024_650_Notes_Second_Supplemental_Indenture.txt | 3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea | unchanged |
| CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt | 0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119 | unchanged |
| CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt | 25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c | unchanged |
| CZR_2026_Merger_Agreement_8K.txt | 6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169 | unchanged |
| CZR_2026_Merger_Press_Release.txt | 4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b | unchanged |
| CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | 4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51 | unchanged |
| CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt | 256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24 | unchanged |
| CZR_Q2_2026_10Q.txt | f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a | unchanged |
| CZR_Q2_2026_Earnings_Release.txt | b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8 | unchanged |
| MGM_Q2_2026_Earnings_Release.txt | 795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb | unchanged |
| PENN_Q2_2026_Earnings_Release.txt | 4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c | unchanged |

## Fit

- fit files: unknown (none in the run)

Not verified: Copilot behaviour (this is a proxy run, never a certification), GPT models, fetch (no network fetch is run or measured), the provider identity behind model labels (caller-reported), worker isolation beyond the dispatch message, module A/B qualification (pending from Plan 05), and report rendering unless the Report line says it was written.
