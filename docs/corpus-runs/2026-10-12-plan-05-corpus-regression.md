# Corpus regression — Plan 05 (core modules), 2026-10-12

Run during Plan 05's verification on the full corpus (`RBOT_CORPUS_ROOTS` set to caos-databricks `qualification/` and `TEST-Issuer Data`), `RBOT_REQUIRE_CORPUS=1`. Plan 05 adds eight modules (CP-1, CP-1A, CP-1B, CP-1D, CP-2, CP-3, CP-5, CP-6), the bond-analytics calculator, Portfolio Fit, the `FULL_CREDIT_ASSESSMENT` Pathway list and the A/B harness. The modules run from fixture Handoffs written by hand for `czr-2026q2-primary`; the proxy runs and A/B with model-written Handoffs are the controller's (Task 32 Steps 4–10) and are recorded in their own scorecards.

## Registry

- `rbot corpus verify`: 34 packs ok, `exit 0`. Amendment A12 adds the primary pack's two SYNTHETIC Test CLO I files to `czr-2026q2-portfolio` and `czr-2026q2-lite-portfolio` (same sha256).

## Deterministic corpus checks (209 passed, 0 failed, 0 skipped)

Plans 02–04's 151 checks pass unchanged. Plan 05 adds:

| Check | Cases | Result |
|---|---|---|
| `test_handoff_fixtures_validate[module]` | 9 | CP-0 and the eight core fixtures validate with `--run` against `czr-2026q2-primary` (exit 0, no finding); every citation names a pack file and its excerpt is in it |
| `test_cp1_figures_are_on_their_cited_lines` | 1 | all 73 CP-1 figures sit on the filing line they cite |
| `test_fit_arithmetic_test_clo_i` | 1 | `rbot fit` on the Test CLO I files and the CP-3 fixture: upper bound 15.7725 for rated non-CCC instruments, 0.88326 for unrated/CCC facilities, all 12 instruments `Watch`: unresolved sector exclusion C-17 and no matched issuer exposure are explicit conservative flags |
| `test_fit_runs_on_the_czr_portfolio_packs` | 2 | A12: both CZR portfolio packs prepare `TEST_CLO_I` and FIT runs (`CEI-TLB` Watch, `CEI-SN-2032` Watch); Plan 04's two pinned grades change to Available |
| `test_cp6_caps_are_fits` | 1 | CP-6's per-portfolio caps equal `rbot fit`'s on the same fixtures |
| `test_full_credit_assessment_grades_on_the_corpus[pack]` | 34 | `rbot grade` with the real contracts gives the hand-checked grade, blocking and limited modules on every registry pack |
| `test_measure_on_the_cp3_fixture` | 1 | `ab_grade measure` on the CP-3 fixture: C 25/25, F 129/129 from uniquely matched expected identities (11 supported loan peer/index rows; HY rows require spreads the source lacks, and the pack has no TRACE file), 6 gaps |

Full suite with the corpus required: 1388 passed, coverage 97.79%.

## Money code

- `rbot calc bond_analytics`: `mutmut` 3.7.0, all three bond test files: 1089 mutants, 1074 killed, 3 timed out (each makes the solver loop forever), 12 survivors, each rechecked against a concrete input in docs/calc/mutation.md.
- Portfolio Fit arithmetic: `mutmut` 3.7.0: 770 mutants, 768 killed, 2 equivalents (non-None dictionary default; unused rows argument), concrete inputs in docs/fit/mutation.md.

## The Model on the CP-1 fixtures

`rbot model` on the CP-0 and CP-1 fixtures (`tests/test_cp1.py`): PF-LTM to June 30, 2026 total debt 14,585 (11,705 + 3,000 of NEW-1 − 120 revolver repaid), SSIM EBITDA 3,592 (3,624 + 1,807 − 1,839), PF interest 989 and cover 3.63x, SSIM multiple 4.06x, no EV (no listed equity value), no reconciliation fault. With the CP-1D fixture adjusted debt adds the 13,157 of financing obligations: 27,742 and 7.72x. The arranger's 150 of run-rate synergies is registered on the LTM period and reaches the Model as that cell's `stated` figure only (the Model builds LTM from the FY and half-year rows): see the plan's Decision 8. This is the frozen pre-review Plan 03 base, not a new analytical policy: after the final Plan 03/04 rebase, accepted A14 changes Structuring EBITDA to 3,742 and its shared assertions/CP-5 finding/this record must change together; the approved latest-LTM realization policy is also an upstream rebase obligation.

## Grades on the registry classification (`FULL_CREDIT_ASSESSMENT`, full)

CP-1 requires a readable Issuer Source and a financial statement (including offering memoranda and lender presentations); a Market Levels or equity export is optional. CP-1A ratings input specifically accepts Rating report and Market levels export files across issuer/market classes; CP-3 wants a Market Levels export or the Sector RV Workbook; FIT needs prepared positions and limits but owns only the conditional Portfolio Fit block, so a missing portfolio limits the grade rather than blocking it. The four packs with no usable financial statement (tid-ford, tid-six-flags and both save-2024 packs) are Blocked at CP-1 and MODEL.

| Pack | Grade | Blocking | Limited |
|---|---|---|---|
| czr-2026q2-primary | Available | — | — |
| czr-2026q2-full-credit-assessment | With limitations | — | FIT |
| czr-2026q2 | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| czr-2026q2-earnings-update | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| czr-2026q2-covenant-refinancing | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| czr-2026q2-lite-covenant-refinancing | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| czr-2026q2-liquidity | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| czr-2026q2-lite-full-credit-screen | With limitations | — | FIT |
| czr-2026q2-lite-portfolio | Available | — | — |
| czr-2026q2-lite-relative-value | With limitations | — | FIT |
| czr-2026q2-portfolio | Available | — | — |
| czr-2026q2-relative-value | With limitations | — | FIT |
| ccl-fy2025 | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| ccl-fy2025-covenant-refinancing | With limitations | — | FIT |
| ccl-fy2025-earnings-update | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| ccl-fy2025-full-relative-value | With limitations | — | FIT |
| ccl-fy2025-liquidity | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| ccl-fy2025-lite-covenant-refinancing | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| ccl-fy2025-lite-full-credit-screen | With limitations | — | CP-1, CP-3, FIT |
| ccl-fy2025-market-dislocation | With limitations | — | FIT |
| ccl-fy2025-portfolio | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| ccl-fy2025-relative-value | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| ba-fy2025 | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| f-fy2025 | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| save-2024-distressed-restructuring | Blocked | CP-1, CP-1B, MODEL, CP-2, CP-3, CP-6 | CP-1A, CP-1D, FIT |
| save-2024-lite-distressed-restructuring | Blocked | CP-1, CP-1B, MODEL, CP-2, CP-3, CP-6 | CP-1A, CP-1D, FIT |
| vmo2-fy2025 | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| vmo2-fy2025-deep-research | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| vmo2-fy2025-full-deep-research | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| vmo2-fy2025-portfolio | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| tid-ford | Blocked | CP-1, CP-1B, MODEL, CP-2, CP-3, CP-6 | CP-1A, CP-1D, FIT |
| tid-six-flags | Blocked | CP-1, CP-1B, MODEL, CP-2, CP-3, CP-6 | CP-1A, CP-1D, FIT |
| tid-vmo2-fy2025 | With limitations | — | CP-1, CP-1A, CP-3, FIT |
| tid-vmo2-2026q1 | With limitations | — | CP-1, CP-1A, CP-3, FIT |

## Independent review follow-up

All five Important findings are repaired: non-NR unreadable agency ratings remain conservative even with another readable rating; total par is required only for a touched pct_par limit and remains a gap otherwise; C(A) is measured through a checked map of actual frozen r14 Trace/Registry evidence, including every source on a multi-source record and any reference in headings; expected rows match unique identities with all three Strategies; carried null CP1D amounts remain null with explicit gaps and a noncritical amount contract. The validator also rejects duplicate real row keys while preserving honest Blocked placeholders.

The actual Model integration keeps addback:impairment FY:FY2023 null with NOT_STATED after the CP1 and CP1D carried amount is —. No fake zero is supplied in the Handoff. The frozen upstream A14/latest-LTM methodology and final Plan02 sign/currency anchoring repair still require the final base rebase. A global run_error from the final Plan02 validator is refused by name for both A and B; it cannot become one bad citation in a 20-reference ratio. Individual unanchored quotations remain measured with findings. No frozen validator edit is made. Main interfaces already synchronize the null amount, CP5 prepared-source access, Blocked critical/min_rows allowance and catalog host ownership.

Required confidence-review and inline capped rewrite-tournament completed before the local review commits. Plan05 publication records the separate deterministic block replay against the unchanged frozen m0 tree.

## The A/B harness on stand-in Handoffs

The dry run of Task 32 Step 2 (fixtures as side B, their `to-r14` conversion as side A, the stand-in grader sheets): no model runs, so it proves the commands and the pass-bar arithmetic, not the modules. Both C(A) and C(B) are actual prepared-source measurements; all eight stand-in comparative bars pass. A valid mapped bad citation lowers C(A) with findings, while missing/duplicate/malformed/unverifiable maps fail qualification by name rather than receiving a fabricated ratio.

```text
model exit 0
fit exit 0
X=A Y=B
{"module": "CP-1", "validate_exit": 0, "findings": [], "C": "76/76", "gaps": 6, "bytes": 34873, "qa_status": "Restricted", "F": null}
{"module": "CP-1", "side": "A", "C": "76/76", "findings": [], "evidence_references": 76}
CP-1 score exit 0
X=A Y=B
{"module": "CP-1A", "validate_exit": 0, "findings": [], "C": "27/27", "gaps": 4, "bytes": 10384, "qa_status": "Restricted", "F": "9/9"}
{"module": "CP-1A", "side": "A", "C": "27/27", "findings": [], "evidence_references": 27}
CP-1A score exit 0
X=A Y=B
{"module": "CP-1B", "validate_exit": 0, "findings": [], "C": "12/12", "gaps": 3, "bytes": 6051, "qa_status": "Restricted", "F": "2/2"}
{"module": "CP-1B", "side": "A", "C": "12/12", "findings": [], "evidence_references": 12}
CP-1B score exit 0
X=A Y=B
{"module": "CP-1D", "validate_exit": 0, "findings": [], "C": "15/15", "gaps": 2, "bytes": 6471, "qa_status": "Restricted", "F": null}
{"module": "CP-1D", "side": "A", "C": "15/15", "findings": [], "evidence_references": 15}
CP-1D score exit 0
X=A Y=B
{"module": "CP-2", "validate_exit": 0, "findings": [], "C": "16/16", "gaps": 3, "bytes": 8230, "qa_status": "Restricted", "F": "24/24"}
{"module": "CP-2", "side": "A", "C": "16/16", "findings": [], "evidence_references": 16}
CP-2 score exit 0
X=A Y=B
{"module": "CP-3", "validate_exit": 0, "findings": [], "C": "25/25", "gaps": 6, "bytes": 13651, "qa_status": "Restricted", "F": "129/129"}
{"module": "CP-3", "side": "A", "C": "25/25", "findings": [], "evidence_references": 25}
CP-3 score exit 0
X=A Y=B
{"module": "CP-5", "validate_exit": 0, "findings": [], "C": "2/2", "gaps": 1, "bytes": 4457, "qa_status": "Pass", "F": null}
{"module": "CP-5", "side": "A", "C": "2/2", "findings": [], "evidence_references": 2}
CP-5 score exit 0
X=A Y=B
{"module": "CP-6", "validate_exit": 0, "findings": [], "C": "10/10", "gaps": 2, "bytes": 7628, "qa_status": "Restricted", "F": "15/15"}
{"module": "CP-6", "side": "A", "C": "10/10", "findings": [], "evidence_references": 10}
CP-6 score exit 0
CP-3 score without --f-b exit 2
V 27/27 missed 0
```

Not verified: the modules written by a model, their A/B against r14, Copilot behaviour, GPT models and fetch (Task 32 Steps 4–10).
