# Plan 10 corpus regression — 2026-10-17

Task 10.8, records and closeout. Nothing was pushed.

## Branch stack

- Base `b47c47d` = Plan 09 tip `cd795ed` + plan docs.
- build/10.1a-fetch-policy `b6f381d`
- build/10.1b-fetch-network `2ccf4fe`
- build/10.1c-fetch-save `d094398`
- build/10.3-cp-dr-module `1776002` (parallel with 10.1; merged `6bbe8ee`)
- build/10.2-fetch-command `b6bff24`
- build/10.4-fetched-downstream `32dea51`
- build/10.5-cp-start-catalog `c30e6d3` (merge `c45ac28`)
- build/10.6-report-view `b42ffae` (merge `991cbf8`)
- build/10.7-record `83261c3` (10.7a integration seams `81eee2f`, 10.8a CP-DR revision `83261c3` = RC rbot tree)
- build/10.8-records `fbd8f03` (A/B records `1a01e4a`, 10.7b identity aliases `fbd8f03`)
- build/10.8b-closeout (10.7c CP-5 fixture `4e90b55`, 10.7d test isolation `db2d91b`, this commit)

origin/main moved to `b4f39c3` (Plan 09 PRs #91–#99 merged) during execution. It differs from `cd795ed` only in install.sh, install.ps1 and tests/test_install.py, which Plan 10 does not touch (`git merge-tree` clean). Rebasing onto main is a pre-PR step for the owner.

## Gates

| Gate | Result |
|---|---|
| `ruff check .`, `ruff format --check .`, `mypy`, `rbot.py check`, `complexipy` (15), `check_suppressions.py` | exit 0 on every task branch (controller re-runs) |
| gitleaks | pass |
| mutation gate on `rbotlib/fetch.py` and `rbotlib/fetched.py` | 10.1: 672 mutants, 33 survivors, all equivalent or justified, none in check_address, check_url, the byte cap, the redirect counter or the hash check. 10.2: no survivor in execute/run_command/add_command, 1 equivalent in _refuse_unless_authorized |
| full suite at db2d91b, chunked runner (owner decision 2026-10-17) | every chunk exit 0; 4198 passed, 1 skipped, 0 failed; coverage 95% (floor 80); slowest chunk (report tests with headless Chrome) 1 h 27 m |
| single-process `RBOT_REQUIRE_CORPUS=1 pytest tests -m corpus` at db2d91b | exit 0; 255 passed (34 m 42 s) |
| `rbot.py check` at db2d91b | exit 0 |
| PR size per branch | 10.1a 599, 10.1b 766, 10.1c 299, 10.3 516, 10.2 390, 10.4 607, 10.5 249, 10.6 199, 10.7-record 152, 10.8-records 694, 10.8b-closeout 157 (all ≤ 800) |

## Record run

Pre-RC run 1 at rbot tree `991cbf8` found: integration seams (10.7a); CP-DR A/B round 1 FAIL (10.8a); R5 FAIL on CP-3 facility-id spellings 81/129 (owner decision "Fix matching" → 10.7b). Verification also found the stale CP-5 fixture (10.7c; full suite at 81eee2f: 4191 passed, 1 failed) and a test-order defect (10.7d: tests/test_brief.py wrote run-brief.md into the session-shared prepared run, failing test_modules[CP-DR] in single-process `-m corpus`; chunked runs hid it).

Final run at RC rbot tree `83261c3` (run 20261017-czr-full-credit-assessment; 12/12 steps accepted and verified; CP-DR accepted, Restricted, 53/53 citations anchored, pack-only; Fetch: off), scored with the closeout tooling (rbot/ byte-identical 83261c3..4e90b55): R1 12/12 terminal, R2 PASS, R3 0 failed/skipped/blocked, R4 10 measured 0 failing, R5 335/335 (287/335 FAIL under the pre-alias matching: the CP-3 rows named the instruments CEI-SSN30 etc.), R6 30 unchanged, R7 11 limitations, R8 PASS. Scorecard: docs/corpus-runs/2026-10-17-czr-2026q2-primary-full-credit-assessment-full-rc6.md.

## A/B

CP-DR, spec §12.7 bar. Round 1 FAIL: ΣD(B) 13.5 < ΣD(A) 14; other checks held. Round 2 (B = isolated CP-DR re-run at 83261c3 from the pre-RC upstream, the upstream side A read) PASS: ΣD(B) 18 ≥ ΣD(A) 12, no criterion below A−1, C(B) 103/103 ≥ max(0.95, C(A) 23/27), G 3 ≥ 2, F n/a. Records: docs/ab/2026-10-17-CP-DR-czr-2026q2-primary.md, docs/ab/2026-10-17-CP-DR-czr-2026q2-primary-r2.md.

## Known flakes

- hypothesis DeadlineExceeded in tests/model/test_credit_model_statements_nature.py at load ~200 (seen at b6bff24; passed at 81eee2f and db2d91b). None recurred in the final suite.
- Headless Chrome teardown retry (Plan 09).

## Owner decisions 2026-10-17

- "Allow chunked runner": full suites run in 10-file chunks with coverage appended because external SIGTERMs killed single-process runs.
- "Fix matching": R5 alias matching, bar unchanged at 0.90.

Not verified: live Copilot runs; fetch on (no network fetch was run or measured; fetch code is covered by local-server tests and mutation only); GPT models; a run of the `quick` depth after Plan 10 (unchanged list, covered by tests only).
