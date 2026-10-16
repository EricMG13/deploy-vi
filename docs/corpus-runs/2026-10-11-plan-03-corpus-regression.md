# Corpus regression — Plan03 Model on final executed Plan02, 2026-10-12

Codex mechanically integrated the independently approved Model package at source commit `6b6f02b3f81a275973ca041cec2b21602c4c4dad` onto final Plan02 `9e65cd9`. Every Model production file remains byte-identical to the approved package. The shared CLI preserves final Plan02's named validation errors and safe log preflight/append behavior, and adds Model command registration. The unchanged caos port retains its original source attribution. Synthetic replay identity `r <r@x>` was a scratch artifact; integration commits are authored by Codex and carry the verified source SHA and inherited Claude/caos provenance.

The final required-root suite passes **1454 tests**, coverage **99.06%** (floor80%). Required corpus: **116 passed,1338 deselected**,0 failed/0 skipped. `rbot corpus verify` exits0 for the34 registered packs. All static/security gates exit0: lock, frozen ruff/format/mypy, suppressions0, complexipy15/McCabe10, bandit and scan floor, strict pip-audit, jscpd3%, rbot check and gitleaks. Native evidence is in `scratchpad/p03-final-codex/`; this record is a deterministic Model check, with no proxy scorecard or A/B.

## Outputs exercised

| Check | Cases | Result |
|---|---|---|
| Final Plan02 corpus checks |110| Hashes, inventory, prepare, entity traps, citations, primary pack, expectations, proxy step1 and brief; all retained |
| Model on caos example |1| Structuring EBITDA4134, SSIM EBITDA4094, PF interest904; no reconciliation fault |
| Filing-only CZR fixture anchor and Model |2| All51 figures anchor to hash-checked filing lines. Revenue11648; Reported EBITDA3255; Structuring=SSIM3592; interest776; cover4.63x; SSIM multiple3.26x; EV28736 at8x; debt11705 and net debt10740. This input has no synergy row, so3592 remains correct |
| A14/current registered-LTM controls |3| Add150 from the existing registered `SYNTHETIC_CZR_2026_PF_Capitalisation.md` to the separate LTM-only input. Structuring is3742 in every case. UNREALIZED/Challenged and REALIZED/Rejected keep SSIM3592; current registered-LTM REALIZED/Supported gives SSIM3742 |

Two additional output digest goldens pin Model JSON, MODEL.md and workbook cell values/formats for the latter UNREALIZED and supported-REALIZED controls. Existing filing-only goldens remain valid. The supported-REALIZED case is a hypothetical positive control for the approved judgment rule, not a claim that this synthetic source evidences realized savings. No source file, hash, registry or filing-only fixture was changed.

Latest dated registered-LTM judgment applies throughout an add-back in both directions; absent that judgment, exact-period fallback remains with visible mixed-status limitations. Existing stale/older/contradictory judgment guards pass. Current cover columns both use SSIM EBITDA/PF interest. The full CP1 date map includes undisplayed PERIOD_END debt-like balance rows; known dates infer omitted day counts; sign-only bridge flips retain exact Decimal precision.

## History, gates and limits

All30 mechanically replayed PR scopes pass lock, frozen ruff/format/mypy/complexipy and the complete roots-unset suite on their actual exported trees; max797 changed lines. Final02 baseline is737 passed/110 skipped; original03F2 end state1337 passed/112 skipped. The test/documentation follow-up03G1 preserves all production arithmetic and packages the5 new controls plus this current record under the800-line cap.

Exact roots-unset CI command `RBOT_REQUIRE_CORPUS=synthetic uv run --frozen pytest -m corpus --no-cov`: **1 passed,115 skipped,1338 deselected**, exit0. Full primary-pack materialization still depends on unresolved external filings, so this command does not prove meaningful synthetic Model execution. Required mode1 refuses absent roots by name rather than skipping; required real roots exercise all116 corpus cases.

A10 expectation ids/book-value/sign conventions remain unchanged. A14 adds an LTM-only150 to Structuring when that row exists; it does not invent one in the filing-only input. Later Plan05's actual CP1 fixture includes that row, so its rebase must coordinate Model expectations and CP5 findings.

No production repair was needed. Confidence review is recorded; no material production symbol qualifies for a post-edit rewrite tournament because this was mechanical replay plus test-only/docs changes. The approved101-mutant four-function selection (100 killed,1 sentinel survivor independently paired) remains applicable to byte-identical source. No new whole-package mutation claim or sweep is made.

Publication stages/fsyncs all three outputs before replacing each file; a publication failure returns1 and may leave a partially published set. No rollback/crash/concurrent-attacker guarantee is claimed.

`Not verified:` analyst work-machine Excel/runtime; model-written CP1/CP1D inside the later Plan05/06 proxy/A-B; meaningful roots-unset synthetic Model coverage; simultaneous multi-file visibility, rollback/abrupt-crash consistency or concurrent attacker directory swaps; broad mutation coverage of the unchanged current package.
