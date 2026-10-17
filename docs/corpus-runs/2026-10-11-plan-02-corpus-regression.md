# Corpus regression — Plan 02 (intake and corpus)

Measured again on 2026-10-12 in the integrated `plan-02` worktree, repair diff based on `d153e37`. `RBOT_REQUIRE_CORPUS=1` and `RBOT_CORPUS_ROOTS` point to the owner's caos-databricks `qualification/` and `TEST-Issuer Data`. Results below come from this final repair tree, including the ordinary-copy control added during mutation review. Evidence: scratchpad `p02-repairs-codex/{gates.json,required-full.txt,required-corpus.txt,verify.txt,proxy.txt,corpus-observed.json}`. Plan 02 adds no module or Pathway; there is no proxy-run scorecard or A/B.

## Registry

- `rbot corpus verify`: 34 packs, each printed `ok`, then `exit 0`. 198 file entries over the 34 packs. Packs by root: `caos-qualification` 29, `test-issuer-data` 4, `synthetic` 1.

## Corpus tests: `pytest -m corpus`, 110 passed, 0 failed, 0 skipped

| Test function | Cases passed |
|---|---|
| `test_corpus_hashes_match` | 34 |
| `test_inventory_is_deterministic` | 34 |
| `test_prepare_pages_and_markers` | 34 |
| `test_entity_trap_flagged` | 2 |
| `test_citations_anchor_in_real_filings` | 1 |
| `test_primary_pack_traps` | 1 |
| `test_primary_pack_portfolio_json` | 1 |
| `test_expectations_anchor_in_their_sources` | 1 |
| `test_step_1_on_the_primary_pack` | 1 |
| `test_brief_citations_anchor_in_the_primary_pack` | 1 |

The existing expectation/citation tests remain included in the 110 passing corpus cases.

Full suite with the corpus required (`RBOT_REQUIRE_CORPUS=1 uv run pytest`): **847 passed**, zero skipped, total coverage **98.39%**. The ordinary local run passed **737**, skipped the 110 corpus cases and collected **847**. Integrated baseline `d153e37`: 781 collected, 671 passed + 110 skipped, 98.35%. The repair adds 66 cases; no original test case was removed.

Historical count correction: the earlier “617 passed” ledger claim was **617 collected: 507 passed + 110 skipped**. It was not 617 passes plus another 110 corpus skips. With `RBOT_REQUIRE_CORPUS=synthetic` and external roots unset, this registry skips all 110 corpus cases (its synthetic primary pack also contains registered external files); the command exits 0. The separately required owner-corpus run above exercised all 110.

## Observed on `czr-2026q2-primary`

- `TEST_CLO_I` portfolio JSON: strategy CLO, NAV 630.9, par 634.0, unit MILLIONS; 10 positions; 10 limits (`C-01`, `C-02`, `C-04`, `C-05`, `C-06`, `C-07`, `C-08`, `C-10`, `C-11`, `C-17`); 7 unparsed rows (lines 9, 15, 18, 19, 20, 21, 22); no portfolio notes.
- VMO2 bond report PDF: 47 pages, entities `['VMED O2 UK HOLDINGS LIMITED']`.

## Proxy run, steps 1 and 5 (Full Credit Assessment, full)

- Step 1: `inventory.json: 30 file(s), 0 skipped`; `prepared/index.json: 30 file(s), 0 unreadable`; `portfolios: TEST_CLO_I`. From the run folder: 30 inventory files, 0 skipped; 30 index files, 0 unreadable, 1 `image_read`, 76 pages; `log/rbot.log` has `inventory` and `prepare`, each exit 0.
- Step 5 prints: `python rbot/scripts/rbot.py approve --run <run> --pathway FULL_CREDIT_ASSESSMENT --depth full --primary yes --analyst proxy-run --deep-research yes --prior-case no`.

`Not verified:` dynamic hostile filesystem replacement after static preflight; remaining mutation diagnostic/old-contract coverage gaps (see scratchpad `p02-repairs-codex/mutation-report.md`); Copilot behaviour, GPT models and fetch (no module runs in Plan 02); proxy steps 2–4 and the scorecard (Plan 06); Image-Read of the screenshot by a model (Plan 05); what the entity-trap and citation tests assert beyond passing (this record shows their results, not their contents).
