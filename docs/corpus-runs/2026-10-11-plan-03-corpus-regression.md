# Corpus regression — Plan 03 (Model, history), 2026-10-11

Run during Plan 03's verification on the full corpus (`RBOT_CORPUS_ROOTS` set to caos-databricks `qualification/` and `TEST-Issuer Data`), `RBOT_REQUIRE_CORPUS=1`. Plan 03 adds the `MODEL` host step, not a module or a Pathway, so there is no proxy-run scorecard and no A/B; `rbot model` needs a CP-1 Handoff, which no proxy run writes before Plan 05. This record covers every deterministic corpus check.

## Registry

- `rbot corpus verify`: `exit 0` (Plan 02's 34 packs, unchanged by Plan 03).

## Deterministic corpus checks (113 passed, 0 failed, 0 skipped)

| Check | Cases | Result |
|---|---|---|
| Plan 02's checks (hashes, inventory, prepare, entity traps, citations, primary pack, expectations, proxy step 1, brief) | 110 | unchanged |
| `test_model_on_caos_fixture` | 1 | the ported Model on the caos worked example through `rbot model`: Structuring EBITDA 4,134, SSIM EBITDA 4,094, PF interest 904; no reconciliation fault |
| `test_cp1_czr_fixture_is_anchored_in_the_corpus` | 1 | every citation excerpt of the hand-written CZR CP-1 Handoff is in its filing (pack `czr-2026q2-primary`), and each of its 51 figures is on the cited line |
| `test_model_from_cp1_handoff_fixture` | 1 | CZR LTM to 30 June 2026: revenue 11,648; Reported EBITDA 3,255; SSIM = Structuring EBITDA 3,592 (every add-back realized); PF interest 776; cover 4.63x; SSIM Multiple 3.26x; EV 28,736.0 at the Run Brief's 8.0x; senior secured debt 9,385, unsecured 2,320; maturity wall 2028 to 2037; no reconciliation fault; limitations `PF_LTM_EQUALS_LTM`, `CP1D_NOT_READ`, `NO_PROJECTIONS`, `MATURITY_NOT_STATED` |

With no corpus roots, the two CZR checks fail (not skip) naming the unresolved root. Review-fix verification 2026-10-12 (Codex), on the original frozen Plan 02 review base: required corpus 113 passed, 820 deselected. Full required-corpus suite: 933 passed, coverage 98.85%. Static gates all exit 0. The exact roots-unset CI command with `RBOT_REQUIRE_CORPUS=synthetic` gives 1 passed / 112 skipped: this frozen base predates synthetic mode; meaningful synthetic-mode coverage requires the separate executed-Plan02 rebase. Required mode1 with missing roots gives 2 failed / 1 passed for the Model checks, as required.

## Rulings applied

- Amendment A10: Plan 02's CZR expectations take the Model's ids; `carrying_value` and CP-1's total debt are book values (the carrying amount as filed: CEI Senior Secured Notes due 2030 1,987, not the 2,000 face); pro forma rows are not sign-normalised (PF cash interest -213).
- Quality-adjusted EBITDA is not computed: under §6.5 a `Rejected` add-back counts as unrealized, so it would always equal SSIM EBITDA.

`Not verified:` a CP-1 Handoff written by a model (Plan 05) and `rbot model` on it inside a proxy run (Plan 06); Copilot behaviour and GPT models.

The owner ruling of 2026-10-12 applies CP-1D judgment for the newest dated registered LTM overall to each add-back throughout, both directions; absent that judgment, exact-period fallback remains with a visible mixed-status limitation. Current cover columns both use SSIM EBITDA / PF interest. Publication stages and fsyncs all outputs before per-file replacement; publication failure returns1 and may leave partial publication.

Final independent-review repairs (Codex, 2026-10-12): complete CP-1 period registry drives debt-like balance placement, including undisplayed PERIOD_END; known dates infer omitted day counts before FY/rolling annual guards; unrealized bridge sign changes use copy_negate at admitted29-digit derived precision. Six new CLI cases and strengthened existing guards cover the defects and paired controls.
