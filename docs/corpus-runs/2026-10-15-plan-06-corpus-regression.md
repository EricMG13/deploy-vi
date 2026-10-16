# Plan 06 integration closure at RC3 — 2026-10-15

Task 06.16, plan and record only: no branch was created and nothing was pushed.

- Frozen tree: `build/v1-rc3` `2d190181a53943239fba61e95454e6ae2bbe1ff7`, tree `cff60799e9d0bca2f08f0cdf054dea69a0ef290f`. It is the v1 integration line and supersedes `build/06`.
- All gates ran on that tree (read-only worktree detached at `2d19018`) with the required roots `caos-qualification` (`/Users/ericguei/Documents/caos-databricks/qualification`) and `test-issuer-data` (`/Users/ericguei/Documents/TEST-Issuer Data`).
- Corpus verify also ran before the suite, at RC3 build: exit 0.

## Gates (every exit 0)

| Gate | Result |
|---|---|
| `uv sync --locked --all-groups`, `uv lock --check` | exit 0; 66 packages resolved, 64 checked |
| `ruff check .`, `ruff format --check .` | exit 0; 375 files formatted |
| `mypy` | exit 0; 279 source files |
| `uv run pytest` (full) | exit 0; 3871 collected, **3870 passed, 0 failed, 1 skipped, 0 deselected**; coverage **94.71%** (floor 80); 5460 s |
| `rbot.py check` | exit 0; 0 problems |
| `RBOT_REQUIRE_CORPUS=1 pytest -m corpus --no-cov` (roots set) | exit 0; **242 passed, 0 failed, 0 skipped**, 3629 deselected |
| same, roots unset, `RBOT_REQUIRE_CORPUS=synthetic` | exit 0; 242 passed, 3629 deselected |
| `corpus verify`, after the suite | exit 0; all 34 packs `ok`, source hashes unchanged |
| `check_suppressions.py` | exit 0; 0 suppressions, baseline 0 |
| `complexipy rbot/scripts scripts --max-complexity-allowed 15` | exit 0; all functions within the limit |
| bandit + `check_bandit_floor.py` | exit 0; 0 findings, 21,631 lines scanned |
| `pip-audit --strict` | exit 0; no known vulnerabilities |
| `jscpd@5.2.0 --threshold 3 --min-lines 10` | exit 0; 8 clones, 0.14% duplicated lines overall |
| `pre-commit run gitleaks --all-files` | Passed |
| `g2.log` (the §12.5 tests) | 53 tests, all passed; no summary line was captured |

Sources: the controller's `gates-summary.txt`, `gate-*.log`, `corpus-verify-after.log`, `g2.log` and `gitleaks.log`. Nothing was re-run for this record.

## Whole-branch size (expected failure)

`BASE_REF=origin/codex/stack-deploy-vi-05y bash scripts/check_pr_size.sh` exits 1: **70156 changed lines (limit 800)**. Under the stack's DROP set the figure is 38,398. The stack below is the remedy.

## Mutation on sensitive changed code

Prior reports name commits near these files, but I could not tie any of them to a file plus a commit `C` with an empty `git log C..2d19018 -- <file>`. So **no prior evidence was reused**. Every file below was mutated afresh in scratch worktrees (removed afterwards; the RC3 trees were never written).

- Method: scripted operator mutants, not mutmut. Four per file, spread across guard conditions (comparison flip, `not` removal, `and`/`or` swap). Judged by the test files that import the module, with `-x -m "not corpus"`. Survivors were re-run against every test file naming the module. A baseline passed first, so each kill is a real failure.
- Result: **136 mutants over 34 files; 121 killed, 15 survived.** Follow-up (06.16-mutants, tests only): 14 of the 15 survivors now killed by new tests, 1 proven equivalent, so 135 killed, 1 equivalent, 0 open.
- `install.sh` and `install.ps1` share one payload (the test asserts they are equal): 7 hand mutants applied to both, each killed by the guard's own test (linked ancestor, existing differs, late destination, entry hash, lock collision, overlap, oversized entry).

Files with 4 of 4 killed: origins, ownership, current, host_evidence, attempts, runlog, accept, resume, model/qualification, runs, fit_host, isolation_capture, isolation_manifest, isolation_code_roots, isolation_preparation, model/snapshot, model/house, model/run, host_preflight, report/assets, report/blocks, report/charts, validate. Also `install.sh`/`install.ps1` (7 of 7).

| File:line | Mutant | Result | Reading of the cause |
|---|---|---|---|
| command_receipts.py:33 | `or`→`and` pending-intent guard | KILLED by `test_resume_log.py::test_pending_intent_must_be_latest_even_with_pending_text` | only `test_resume_log.py` drives it; no test has a pending non-latest intent |
| command_receipts.py:168 | `<`→`>=` following-receipt bound | KILLED by `test_resume_log.py::test_each_following_receipt_is_bounded_by_the_next_prefix` | no test with more than one following receipt |
| state.py:234 | `or`→`and` approved-origin lineage guard | KILLED by `test_state.py::test_lineage_refuses_either_malformed_approved_origin_shape` | 53 test files; no partial-lineage case |
| next.py:165 | `and`→`or` host-vs-module selection | EQUIVALENT: `kind` is `host`/`module` (state validation) or `done` only when `module` is None, so `kind == "module"` and `module is not None` select the same branch for every record `state.read` accepts; the `host` case is taken by the preceding `if`. Mutant also survives `test_next.py` and `test_model_host.py` | no test gives `module=None` with a module kind |
| bootstrap.py:130 | `and`→`or` completion_origin capture | KILLED by `test_edit_origins.py::test_completion_origin_is_not_captured_over_registered_accept_history` | no test with an `accept_history` step and no origin |
| approve.py:441 | `or`→`and` Approval readback | KILLED by `test_approve.py::test_readback_refuses_when_only_one_published_file_differs` (brief and cp0) | partial divergence (brief or CP-0 hash alone) is untested |
| model/host.py:329 | `or`→`and` inputs-changed guard | KILLED by `test_model_host.py::test_either_input_or_context_change_during_execution_is_named` (inputs and context) | no test changes only the inputs or only the host context |
| dispatch.py:382 | `==`→`!=` CP-3 calculator paths | KILLED by `test_model_host.py::test_cp3_message_declares_the_calculator_and_its_write_paths` | no test asserts the calculator list in a message |
| fit.py:121 | `or`→`and` header/period guard | KILLED by `test_fit.py::test_run_context_needs_one_header_row_and_a_period` | half-bad inputs fail later by another route |
| fit.py:198 | `or`→`and` object-list guard | KILLED by `test_fit.py::test_prepared_positions_must_be_a_list_of_objects` | list of non-objects is untested |
| fit.py:390 | `is`→`is not` headroom note | KILLED by `test_fit.py::test_headroom_note_appears_only_when_some_limit_caps_no_size` | note text is not asserted |
| report/run_json.py:55 | `and`→`or` anchored finding | KILLED by `test_report_run_json.py::test_anchored_ignores_findings_naming_another_citation_and_source` | no finding naming another citation with a source set |
| report/run_json.py:158 | `is`→`is not` FIT step guard | KILLED by `test_report_run_json.py::test_fit_is_read_only_for_an_accepted_step` | no test with a missing FIT step |
| scripts/scorecard.py:399 | `or`→`and` expectations guard | KILLED by `test_scorecard.py::test_front_page_section_without_an_expectations_file_is_unknown` | `expectations` None vs not-a-file split is untested |
| scripts/proxy_isolated.py:260 | `or`→`and` native-next CP-0 guard | KILLED by `test_proxy_isolated.py::test_native_next_must_select_the_cp0_module_before_approval` | wrong kind with right step is untested |

One survivor (`next.py:165`) is equivalent; the other 14 were test gaps and are killed (see Result column; each mutant applied by hand, failed the new test, restored, test passed).

NOT COVERED: the PowerShell wrapper lines of `install.ps1` outside the shared payload (`pwsh` is not installed). `model/xlsx.py` and `model/statements.py` were outside the brief's list and not mutated.

## One state engine

```
git grep -nE "write_atomic|write_text|write_bytes|json\.dump|os\.replace|run-state" -- scripts/proxy_run.py scripts/proxy_continue.py scripts/scorecard.py
scripts/proxy_continue.py:93:  print("Requested caller model label (unqualified): " + json.dumps(label))   # stdout string
scripts/scorecard.py:9:       docstring naming run-state.json
scripts/scorecard.py:39:      from rbotlib.fsio import write_atomic
scripts/scorecard.py:584:     write_atomic(out / name, text)                                         # the scorecard record only
```

`proxy_run.py` has no match. The proxy reaches state only through `rbotlib.cli.main` (as `rbot`), `runs.create_run` (`proxy_run.py:189`) and read-only `state.read` (`proxy_run.py:124,155,301`; `proxy_continue.py:78,103,107`). It also calls `command_receipts.preflight`, `current.reconcile` and `bootstrap.phase` (`proxy_run.py:123,126,127`), which are native checks. `scorecard.py` writes only its own record. Tests that drive the native commands through the proxy: `tests/test_proxy_start.py` (for example `test_real_menu_blocked_refusal_then_simulated_approval_rename`, `test_busy_native_owner_prevents_simulated_brief_writes`, `test_original_primary_corpus_native_start_to_approval`) and `tests/test_proxy_continue.py` (`test_actual_managed_host_execution_and_failure_are_owned_once`, `test_failed_accept_preserves_original_native_exit`, `test_all_terminal_renders_report_and_sets_state`).

## 06.15 scorecard and report fields

- Scorecard: [2026-10-14-czr-2026q2-primary-full-credit-assessment-full.md](2026-10-14-czr-2026q2-primary-full-credit-assessment-full.md), 11/11 steps accepted (verified).
- That record says "Report: not rendered (report fields null)". It was written before Plan 07.
- "Report fields still null": **resolved by Plan 07**. `rbot render` (commit `6f38cb6`) now renders the report and the proxy sets state on all-terminal (`test_all_terminal_renders_report_and_sets_state`). The scorecard was not regenerated for this record.

## Stack proposal at RC3 (68 rows; proposal only)

Method: first-parent greedy walk from `origin/codex/stack-deploy-vi-05y` (`7d5cfe1`, present locally) to `2d19018`, with the brief's exclusions and DROP set. Five merges are over 800 on their own; each is linearised by packing its side-only commits (per-commit sums, which overestimate because later commits revise earlier files). Rows marked `~` must be re-measured after replay.

Rows 1-36 (end commit, lines): 1 efa28b2 774; 2 013a274 459; 3 7fd6091 796; 4 845c18a 735; 5 fe08de4 258; 6 66e8f00 719; 7 6fa314d 373; 8 fdf130e 689; 9 0a5b11b 797; 10 a9861c2 369; 11 1094a76 746; 12 a4d8c7c 369; 13 7bd3b14 697; 14 108dc40 497; 15 c876d17 447; 16 327c81e 752; 17 71aa8b7 152; 18 16617a0 739; 19 0140ea8 203; 20 eab1301 770; 21 fcf1ee9 744; 22 0dd53c9 244; 23 c1da340 651; 24 c276f95 781; 25 4599dbc 741; 26 8868063 452; 27 f8bc196 439; 28 ea766af 625; 29 6f5d6ed 664; 30 9a8d2c2 396; 31 8e14f82 742; 32 bce0fff 326; 33 3b1bb4b 768; 34 ae327cc 400; 35 d71e677 606; 36 5605edd 528. All are unchanged from the 3f526a0 measurement.

| # | commits | lines | theme |
|---|---|---|---|
| 37a-e | b46512f side, R3 order | ~588, 567, 791, 567, 717 | proxy Approval, continuation, runtime and SKILL, installed-source binding, installers (the merge is 2662) |
| 38 | b46512f..3f526a0 | 69 | roadmap, ADR, workflow docs |
| 39a-c | 928aaa8; a2f65b1; 9049354 | 718; 601; 318 | v1-finish: scorecard, isolated Module mode, validate preflight (merge is 1637) |
| 40 | 3774423..857c898 | 348 | scorecard gap fixes |
| 41a-j | 5221bf3,5d7a83c,d0671d; f22d4d2; 5bc350f,e5ff058,c8e2742; 1d9b09a,fd0d6ef; c839d2d; 77aeab1,7abfbcc; 701ced1,8091502; 0fbc03e; c58d42e; fdbb0a5 | ~761; 305; 675; 532; 602; 444; 795; 795; 590; 459 | v1-report Plan 07 (merge is 9789 with the design history) |
| 42-44 | c2488c1..9af9c91; ..851f3cf; ..8b4fc33 | 645; 581; 327 | report fixtures, report.js, win merge |
| 45a-e | f69e45a,b1d8061; 7133586,8e1e27a; e3215d3,652d807; ed82e0d; 167cf97 | ~559; 407; 733; 519; 344 | v1-xfer (merge is 1914) |
| 46 | 02da027..d0cf8cc | 476 | render on the done branch |
| 47a-b | 52a4ec0; fb060af | 756; 611 | codex-dev-status side (merge is 1367) |
| 48 | dc4d869..2d19018 | 215 | rc2 and rc3 merges |

Outside the stack (R4): the `006a8a2` design history, 6173 lines (`design/mockups/**`, `.impeccable/**`, `DESIGN.md`); its commits `9d49699` 3611, `bf527a1` 1000 and `b44aac0` 1033 each exceed 800. No exclusion may be added to `check_pr_size.sh`.

## Pending owner decisions (none taken here)

- **R1** omit the main-origin Plan 02-04 plan docs from replayed trees (already on main).
- **R2** omit the retired replay documents (`*-replay.md`, `task-07-implementation-code-*.md`).
- **R3** linearise `b46512f`: cherry-pick `61b572b`, `5233aff`, `c783ae5`, `40a1575`, `e481eb8`, `cbe0f18`, `a616d91`, `573f5bd`, `862a209` onto `5605edd'`; skip `5935e9e`, `45fa473`, `2b25edf`, `00cd4ea`; require the tree to equal `b46512f^{tree}` minus DROP.
- **R4** `006a8a2`: (a) land `design/report-a-refine` as its own design PRs with an owner exemption, or (b) split by file group within those commits.
- Same treatment for the four other over-limit merges above (side-commit linearisation).
- Whether to add tests for the 15 surviving mutants before any merge.

Not verified: that the stack rows replay cleanly and pass gates at each scope (rows 37a-e, 41, 45 and 47 are estimates until replayed); the 15 surviving mutants (open gaps, none proven equivalent); `install.ps1` wrapper behaviour (no `pwsh`); the exact reason for the 1 skipped test; that the 06.15 scorecard reflects rendering (not regenerated); ponytail-review; Copilot, GPT and installed behaviour (Plan 08); rendering quality (Plan 07).
