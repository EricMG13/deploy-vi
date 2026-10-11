# Corpus regression — Plan 02 (intake and corpus), 2026-10-11

Run during Plan 02's verification on the full corpus (`RBOT_CORPUS_ROOTS` set to caos-databricks `qualification/` at `5ca9118e` and `TEST-Issuer Data`), `RBOT_REQUIRE_CORPUS=1`. Plan 02 adds no module and no Pathway, so there is no proxy-run scorecard and no A/B; this record covers every deterministic corpus check and proxy step 1.

## Registry

- `rbot corpus verify`: 34 packs ok (33 external, 1 synthetic), 198 file entries, `exit 0`.

## Deterministic corpus checks (110 passed, 0 failed, 0 skipped)

| Check | Cases | Result |
|---|---|---|
| `test_corpus_hashes_match[pack]` | 34 | every file's sha256 matches |
| `test_inventory_is_deterministic[pack]` | 34 | two `rbot inventory` runs identical apart from time; files, sha256 and PDF page counts equal the registry |
| `test_prepare_pages_and_markers[pack]` | 34 | no file unreadable; PDF pages equal the registry; page markers `1..N`; no spreadsheet error marker survives; only images are `image_read` |
| `test_entity_trap_flagged` | 2 | `tid-ford`: the mis-filed 10-K names `SIX FLAGS ENTERTAINMENT CORPORATION`; `tid-six-flags`: the mis-filed 10-K names `Ford Motor Company`; neither names its pack's issuer |
| `test_citations_anchor_in_real_filings` | 1 | a CZR 10-K line with escaped pipes anchors, a one-digit change does not; the Six Flags registrant anchors on p.1, not p.2 |
| `test_primary_pack_traps` | 1 | duplicate TRACE file (same sha256), screenshot `image_read`, VMO2 PDF 47 pages naming `VMED O2 UK HOLDINGS LIMITED`, Sector RV `Gaming` sheet, Bloomberg `#N/A` cells empty |
| `test_primary_pack_portfolio_json` | 1 | `TEST_CLO_I`: Strategy CLO, NAV 630.9, par 634.0, MILLIONS, 10 positions, no Caesars exposure, 10 maximum limits, 7 rows unparsed with reasons |
| `test_expectations_anchor_in_their_sources[czr-2026q2-primary]` | 1 | all 38 expectations anchored in their sources or backed by a spec rule |
| `test_step_1_on_the_primary_pack` | 1 | proxy step 1 prepares all 30 files, none unreadable, portfolio `TEST_CLO_I` |
| `test_brief_citations_anchor_in_the_primary_pack` | 1 | every citation of the CP-0 fixture and of the written Run Brief anchored |

Full suite with the corpus required: 329 passed, coverage 97.4%.

## Proxy run, steps 1 and 5, on `czr-2026q2-primary` (Full Credit Assessment, full)

- Step 1: `inventory.json: 30 file(s), 0 skipped`; `prepared/index.json: 30 file(s), 0 unreadable`; `portfolios: TEST_CLO_I`.
- Prepared: 30 files; 0 unreadable; 1 image_read; 76 pages; portfolio notes: none.
- Step 5 prints: `python rbot/scripts/rbot.py approve --run <run> --pathway FULL_CREDIT_ASSESSMENT --depth full --primary yes --analyst proxy-run --deep-research yes --prior-case no`.

`Not verified:` Copilot behaviour, GPT models and fetch (no module runs in Plan 02); proxy steps 2–4 and the scorecard (Plan 06); Image-Read of the screenshot by a model (Plan 05).

Re-run 2026-10-11: identical results.
