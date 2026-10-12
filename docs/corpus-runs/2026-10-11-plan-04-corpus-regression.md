# Corpus regression — Plan 04 (cp-start), 2026-10-12

Rerun by Codex after replaying the frozen Plan04 tasks onto final executed Plan02 `9e65cd94808373c92221a3cba7fa2401216474e5` on 2026-10-12, on the full corpus (`RBOT_CORPUS_ROOTS` set to caos-databricks `qualification/` and `TEST-Issuer Data`), `RBOT_REQUIRE_CORPUS=1`. Plan 04 adds the CP-0 module and the grading, Approval and plan commands; the shipped catalog lists no Pathway yet (the first, `FULL_CREDIT_ASSESSMENT.full`, lands with Plan 05), so grading is checked on the interfaces spec's six Pathways over stand-in contracts (`tests/spec_fixture.py`) and a CP-0 Handoff written from the registry's hand-checked classification (`tests/cp0_fixture.py`).

## Registry

- `rbot corpus verify`: 34 packs ok, `exit 0`.

## Deterministic corpus checks (148 passed, 0 failed, 0 skipped)

Final Plan02's 847 unique required-corpus cases comprise 737 default tests and 110 corpus cases. The 110 corpus checks pass unchanged; they are not added a second time to the full-suite total. Plan 04 adds:

| Check | Cases | Result |
|---|---|---|
| `test_the_fixture_validates_against_the_primary_pack` | 1 | the CP-0 fixture Handoff validates with `--run` (exit 0); its 30 inventory rows name every prepared file with the same sha256, pages and Image-Read flag |
| `test_the_fixture_is_true_to_the_primary_pack` | 1 | the CP-0 fixture Handoff draws no finding from the CP-0 checks against the real prepared run: the file list, sha256, pages, readable and Image-Read flags, and the one portfolio `TEST_CLO_I` agree with `inventory.json` and `prepared/index.json` |
| `test_tranche_edits_keep_the_brief_anchored_in_the_primary_pack` | 1 | after `--set-tranche` edits every Run Brief citation still anchors; source wins on `oid` |
| `test_grade_matches_expectations[pack]` | 34 | every registry `pathways[]` entry grades as its `fit` implies (interfaces spec section 12.5 row 04); every misfiled file is excluded; all 37 (pack, Pathway, depth) cases match exactly, grade, blocking modules and limited modules (`KNOWN` in `tests/test_grade.py`, the table below) |
| `test_approval_on_the_primary_pack` | 1 | grade then approve Full Credit Assessment, full, Primary: folder renamed `20261011-czr-full-credit-assessment`, CP-0 accepted, Deep Research and FIT pending, Prior Case skipped, the approved Run Brief's citations anchored |

Full suite with the corpus required: **998 passed, 0 skipped, coverage 98.02%**. Separate required-corpus gate: **148 passed, 850 deselected, 0 skipped**. Roots-unset synthetic gate: **850 passed, 148 skipped, coverage 97.85%**; skips are disclosed and never replace the required-root gate.

All unchanged project gates exited 0: lock check; frozen ruff/format/mypy/pytest; zero suppressions against baseline zero; complexipy 15 and McCabe 10; bandit plus scan floor; strict audit; jscpd threshold 3 (0.16% lines); `rbot check`; gitleaks; required corpus; registry verification. The detailed commands, outputs and exit statuses are in `p04-final-codex/final-verified-gates.log` and `.log.json` beside the continuation report.

Shared seams repaired by Codex preserve final02 duplicate/status/citation/control/finite-number validation, existing brief-state updates, unique-temp atomic writes and destination guards; CLI logging follows the final renamed run. CP-0 offered tranches still require a consistent Primary prefill, while analyst-created tranches await Approval. Fixture source hashes were calculated from the three synthetic files already changed by final02; no corpus, reference or global setting was modified.

## Grades on the registry classification

Stand-in sources: CP-1 needs a readable Issuer Source and wants financial statements, CP-4 the legal documents, CP-3 Market Levels (`tests/spec_fixture.py` `SOURCES`). The CZR portfolio packs hold the Test CLO I mandate as text only, which `rbot prepare` does not read into a portfolio, so FIT is limited there rather than blocked (a Portfolio Context file is present).

| Pack | Pathway, depth (fit) | Grade | Blocking | Limited |
|---|---|---|---|---|
| czr-2026q2-primary | FULL_CREDIT_ASSESSMENT full (primary) | Available | — | — |
| czr-2026q2-primary | PORTFOLIO_DECISION full (exercises) | Available | — | — |
| czr-2026q2-primary | RELATIVE_VALUE full (exercises) | Available | — | — |
| czr-2026q2-full-credit-assessment | FULL_CREDIT_ASSESSMENT full (exercises) | With limitations | — | FIT |
| czr-2026q2 | EARNINGS_UPDATE quick (exercises) | Available | — | — |
| czr-2026q2-earnings-update | EARNINGS_UPDATE full (primary) | Available | — | — |
| czr-2026q2-covenant-refinancing | COVENANT_REFINANCING full (primary) | Available | — | — |
| czr-2026q2-lite-covenant-refinancing | COVENANT_REFINANCING quick (primary) | Available | — | — |
| czr-2026q2-liquidity | COVENANT_REFINANCING quick (partial) | Available | — | — |
| czr-2026q2-lite-full-credit-screen | FULL_CREDIT_ASSESSMENT quick (primary) | With limitations | — | FIT |
| czr-2026q2-lite-portfolio | PORTFOLIO_DECISION quick (primary) | With limitations | — | FIT |
| czr-2026q2-lite-relative-value | RELATIVE_VALUE quick (primary) | With limitations | — | FIT |
| czr-2026q2-portfolio | PORTFOLIO_DECISION full (primary) | With limitations | — | FIT |
| czr-2026q2-relative-value | RELATIVE_VALUE full (primary) | With limitations | — | FIT |
| ccl-fy2025 | EARNINGS_UPDATE quick (exercises) | Available | — | — |
| ccl-fy2025-covenant-refinancing | COVENANT_REFINANCING full (exercises) | Available | — | — |
| ccl-fy2025-earnings-update | EARNINGS_UPDATE full (exercises) | Available | — | — |
| ccl-fy2025-full-relative-value | RELATIVE_VALUE full (exercises) | With limitations | — | FIT |
| ccl-fy2025-liquidity | COVENANT_REFINANCING quick (partial) | With limitations | — | CP-4 |
| ccl-fy2025-lite-covenant-refinancing | COVENANT_REFINANCING quick (exercises) | Available | — | — |
| ccl-fy2025-lite-full-credit-screen | FULL_CREDIT_ASSESSMENT quick (exercises) | With limitations | — | CP-3, FIT |
| ccl-fy2025-market-dislocation | RELATIVE_VALUE quick (partial) | With limitations | — | FIT |
| ccl-fy2025-portfolio | PORTFOLIO_DECISION quick (partial) | Blocked | FIT | CP-3 |
| ccl-fy2025-relative-value | RELATIVE_VALUE quick (exercises) | With limitations | — | CP-3, FIT |
| ba-fy2025 | EARNINGS_UPDATE quick (exercises) | Available | — | — |
| f-fy2025 | EARNINGS_UPDATE quick (exercises) | Available | — | — |
| save-2024-distressed-restructuring | DISTRESSED_RESTRUCTURING full (primary) | With limitations | — | CP-1, CP-4, CP-3, FIT |
| save-2024-lite-distressed-restructuring | DISTRESSED_RESTRUCTURING quick (primary) | With limitations | — | CP-1, CP-4, CP-3, FIT |
| vmo2-fy2025 | EARNINGS_UPDATE quick (exercises) | Available | — | — |
| vmo2-fy2025-deep-research | EARNINGS_UPDATE quick (partial) | Available | — | — |
| vmo2-fy2025-full-deep-research | EARNINGS_UPDATE full (exercises) | Available | — | — |
| vmo2-fy2025-portfolio | PORTFOLIO_DECISION quick (partial) | Blocked | FIT | CP-3 |
| tid-ford | COVENANT_REFINANCING full (partial) | With limitations | — | CP-1 |
| tid-six-flags | COVENANT_REFINANCING full (partial) | With limitations | — | CP-1 |
| tid-vmo2-fy2025 | FULL_CREDIT_ASSESSMENT full (exercises) | With limitations | — | CP-4, CP-3, FIT |
| tid-vmo2-fy2025 | EARNINGS_UPDATE full (exercises) | Available | — | — |
| tid-vmo2-2026q1 | EARNINGS_UPDATE full (primary) | Available | — | — |

## CP-0 measures on the fixture Handoff (calibration for the proxy scorecard)

The Task 9 scoring command on `czr-2026q2-primary` with `tests/fixtures/handoffs/CP-0.md` as the Handoff: `{"validate_exit": 0, "findings": [], "C": "17/17", "files": "30/30", "class": "30/30", "document_type": "30/30", "entity_match": "30/30", "traps_caught": "2/2", "F": "14/14", "V": "11/11", "gaps": 6, "bytes": 12654, "qa_status": "Pass"}`.

`Not verified:` qualified live-model CP-0 Handoffs, proxy runs and A/B; full live qualification remains open. Fixture calibration is deterministic evidence only. A CP-0 Handoff written by a model (the proxy runs and the A/B of Task 9 Steps 3–7 are the controller's; their scorecards are separate files); Copilot behaviour, GPT models and fetch; grading with the real module contracts (Plans 05–13 replace the stand-ins).
