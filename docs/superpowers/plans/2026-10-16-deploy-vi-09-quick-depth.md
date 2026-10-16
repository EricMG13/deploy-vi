# Deploy VI Plan 09 — Quick depth (CP-L10, CP-6 screening)

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development`. One fresh implementer per task, and the controller re-runs the gates. Do not copy code-replay blocks; the owner amendment of 2026-10-13 removed them. Task briefs name the files, the tests to write first, and the exact values. The implementer writes the code.

**Goal:** Full Credit Assessment runs at Quick depth end to end. The steps are `rbot approve --depth quick`, then the module steps, then the Credit Snapshot. The new `CP-L10` screen owns the credit view, and `CP-6` writes screening-only recommendations. The work is proven on the `czr-2026q2-lite-full-credit-screen` corpus pack.

**Architecture:** `CP-L10` is a new contract-driven module, like every other module: `contract.json`, plus a generated `MODULE.md`, plus a fixture Handoff. It ports the r14 LITE screen (`cp-l10-financial-change-screen`), with the four absorbed screens (L20, L23, L30, L40) folded into one topics table keyed by `family`. Quick depth is a second catalog list for the same Pathway and Front Page. The runtime gates that hard-code module ids or the `full` depth become catalog-driven. The renderer gains one chart, `chart.topic_counts`, and a visible "Screening only" label.

**Tech:** Python ≥ 3.11, stdlib only. No new dependency. The frozen report assets (`report.css`, `tokens.css`, `charts.js`) do not change.

**Spec:** `docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md` (binding). The relevant sections are:
- §0.1 membership rule; §1 rows `CP-L10` and `CP-6`; §1.1 absorbed r14 phases;
- §2.7 and §2.19 (the CP-2 and CP-6 tables); §2.20 (the CP-L10 tables and the LITE rules);
- §5, FCA quick list, line ~522; §11.4 `chart.topic_counts`;
- §12.5 row 09; §12.7 A/B; §13 row 09; scales at lines 1210–1214.

Also read:
- design `docs/superpowers/specs/2026-10-11-deploy-vi-rbot-design.md`: D12, D22, and "Not verified" at line 151;
- `docs/adr/0003-base-on-caos-fork-r14.md` and its 2026-10-11 amendment (port r14 method text, with only minimal structural edits);
- r14 source: `reference/deploy-v-r14/skills/cp-l10-financial-change-screen/`. That is `SKILL.md` plus `references/CP-L10_CP_LITE_ANALYSIS_POLICY_v1.md` and `references/REF_CP-L10_ADAPTIVE_METHOD.md`, and the `REF_CP-L20/L23/L30/L40_*` files.

## Global Constraints

- **Base.** Base is `main` after PR #90 merges. Until then use `build/v1` at `d1774df` (v1 at RC5 `9f049c8`, plus records). Pre-flight before Task 09.1: re-check every `file:line` named below against the base tip, because line numbers drift.
- **Scope.** Only `FULL_CREDIT_ASSESSMENT` at `quick`. Other Pathways stay out of scope; they arrive in Plans 14–18.
- **Quick list.** The committed quick list is the §5 list without `CP-8`. §5 says "a list is only committed once every module in it exists", and CP-8 arrives in Plan 11. The committed list is: `["CP-0","CP-1","CP-1A","CP-1B","MODEL","CP-L10","CP-3","FIT","CP-5","CP-6"]`.
- **Invariants:**
  - no invented figure, and no zero or placeholder for a gap;
  - a critical cell is never empty;
  - source text never goes into logs;
  - every table has at least one consumer;
  - one owner per Front Page table **per depth list**.
- **Size budget.** `MODULE.md` + `rbot/canon.md` ≤ 51,200 bytes for every module (`catalog.json` `size_budget_bytes`). r14 `SKILL.md` is about 54 KB, so the port drops the M365 machinery: the Output profile completeness config, payload schemas, invocation and digest fields, and CP-DR adoption. That is the minimal-edit rule of ADR 0003.
- **Frozen assets.** `report.css`, `tokens.css` and `charts.js` are pinned by `tests/test_report_assets.py`. New charts reuse existing RBOTCharts kinds (`stackedColumns`), and any print-time CSS goes through `report.js`.
- **Gates per task, all exit 0.** Run the full suite once per branch, not per task:
  - `uv run ruff check .` · `uv run ruff format --check .` · `uv run mypy` · `uv run python rbot/scripts/rbot.py check`
  - `uv run complexipy rbot/scripts scripts --max-complexity-allowed 15` · `uv run python scripts/check_suppressions.py` (stays 0)
  - `uv run python -m pytest <affected test files> --no-cov` · `RBOT_REQUIRE_CORPUS=1 uv run python -m pytest tests -m corpus --no-cov` when corpus-touching
  - `gitleaks` via pre-commit on the range.
  - Export `RBOT_CORPUS_ROOTS` first: `{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}`.
- **PR size.** Each task is one PR scope of ≤ 800 changed lines including tests (CI `scripts/check_pr_size.sh`).
- **Agents.** All implementation and fixes run on Sonnet (`mx-feature`; `mx-scaffold` for docs and config with a complete spec). A task's third and later fixes go to a fresh `mx-escalate` (Fable). No Opus implementer.
- **Reviews.** Owner amendment 2026-10-13: no mandatory independent reviews and no tournaments. The controller re-runs the gates and does an inline confidence review. Module A/B grading stays (ADR 0003: "The A/B on the golden pack still gates each ported module").
- **Every brief says:**
  - no stub or fake value standing in for real behaviour;
  - no catch-all that hides a failure unless the fail-open is documented and logged;
  - every report ends with a `Not verified:` line;
  - a defect fix starts with a failing test for the reported cause.

## Rulings (defaults; owner may override — cost if wrong in the last column)

| # | Gap or conflict in the spec | Ruling | If wrong |
|---|---|---|---|
| R1 | §2.20 requires "one row per family", but the r14 L10–L40 screens and the six `screen_family` values do not map 1:1, and there is no r14 Portfolio screen | Map the r14 topics to families. **Financial change** takes L10 SOURCE_BASIS, EARNINGS_MARGIN_CHANGE, CASH_CONVERSION, LEVERAGE_COVERAGE and KPI_COMPARABILITY, plus L20 BUSINESS_DURABILITY, MARGIN_FCF_RESILIENCE, GOVERNANCE_SPONSOR_BEHAVIOR, FINANCIAL_POLICY_CAPITAL_ALLOCATION and ESG_TRANSITION. **Liquidity** takes L10 LIQUIDITY_MATURITIES and L23 ACCESSIBLE_LIQUIDITY_USES, WORKING_CAPITAL_CAPEX_CASH_BURN, RATES_HEDGES, FX_COMMODITY_INFLATION and BASE_DOWNSIDE_TRAJECTORY. **Covenant and refinancing** takes L23 BREAKPOINTS_REFINANCING, L20 LEVERAGE_REFINANCING_CONTEXT and all six L40 topics. **Distress** takes L30 STRUCTURAL_RECOVERY_PROTECTION and DOWNSIDE_LME_EXPOSURE. **Relative value** takes L30 DATED_MARKET_SNAPSHOT, CURVE_COMPARABLE_COMPENSATION, LIQUIDITY_TECHNICALS and INTEGRATED_SCREENING_POSTURE. **Portfolio** takes a new topic, PORTFOLIO_CONTEXT, written as `Not assessable`, `Missing`, `Gap only`, because FIT and CP-6 judge fit at this depth and CP-L10 reads no portfolio sources. | One contract edit: re-family some topic ids |
| R2 | The spec gives no allocation algorithm in §2.20 | Port the r14 8-step adaptive method verbatim in intent: gate, classify, rank, assign depth, develop the screen, preserve boundaries, upgrade, status. `priority_rank` is a deterministic order: urgency, then downside, then evidence confidence, then canonical topic order. Each topic's `summary` is one sentence for `Gap only`. | Method wording only |
| R3 | Sector Outlook is critical and its scale (`Positive`/`Neutral`/`Negative`) has no "not assessable" value. Q3 names `cpdr.sector_view` as evidence, but CP-DR is absent at Quick. | CP-L10 judges `sector_outlook` from the pack's issuer and market sources (peer releases, sector RV sheet), with `confidence` reflecting the evidence. With no sector evidence, it writes the outlook the issuer and peer evidence supports, sets confidence `Low`, and records the gap in Gaps and as an upgrade trigger to `CP-DR`. | Owner may prefer Blocked; one process-step edit |
| R4 | The spec does not say how a screening-only output is labelled, and only `snapshot.credit_view` and `snapshot.recommendation` carry `basis` | (a) The validator enforces `basis` against the run's depth: `Full` at full and `Screening` at quick, for every table with a `basis` column (new finding code `basis_depth`). (b) At quick, CP-6 sets `qa_status` Restricted, lists every Full input it lacks (CP-2, CP-1D) as a limitation, and recommends a linked Full run. This is r14 CANON SEC5 + D2: "SCREENING_ONLY never permits Committee Ready". (c) The report title band shows "Screening only" when the run depth is quick. | Label wording; one validator rule |
| R5 | CP-6 has no r14 LITE variant (r14 bars CP-6 from LITE input), so §12.7 has no A side for screening | Port nothing new from r14 for CP-6. Add the Screening method to the existing CP-6 contract (R4b, plus how `cp6.challenge` is built from CP-L10 `screen_items` and CP-3 when CP-2 is absent). The CP-6 A/B at quick is recorded as **B-only against the rubric** (C, G and F measured; D scored without an A baseline) and flagged non-equivalent for the owner. | Owner may waive or require an A |
| R6 | CP-1 tables do not list CP-L10 as a consumer, but CP-L10 requires CP-1 | Follow the spec as written: CP-L10 reads the CP-1 Handoff as a required input. Only the CP-1A and CP-1B tables add CP-L10, because the spec lists it there. | Contract consumer lists only |
| R7 | `cpl10.screen_topics.upgrade_module` and `cpl10.upgrade_triggers.target_full_module` have no scale | Keep them free text in v1. The process text says to use §1 module ids (for example CP-2, CP-1D, CP-2D, CP-4). No validator rule. | Add a module-id check later |
| R8 | Fixtures are keyed by module id only, but CP-3, CP-5 and CP-6 read different inputs at quick | Add `tests/fixtures/handoffs/quick/<ID>.md` for every module whose Handoff differs at quick (at least CP-3, CP-5, CP-6). The fixture loader prefers `quick/<ID>.md` when the run depth is quick and falls back to `<ID>.md`. | Test-harness only |
| R9 | CP-1D is absent at quick | No change. `model/qualification._optional` already records "CP-1D: missing; excluded; CP-1 realization statuses retained". Add a test that pins it. | None |

## Review Focus (the inputs most likely to bite; each line's test is in its owning task)

1. **A quick run on a pack with no portfolio** (FIT skipped, "no portfolio context"). Expected: the Portfolio topic is `Not assessable` and `Gap only`, CP-6 recommends without FIT caps and is Restricted (not failed), and the Snapshot renders. Tests in 09.4 and 09.6.
2. **The lite pack has no 10-K** (`czr-2026q2-lite-full-credit-screen` trap `missing_document_type`). Expected: grading stays `L`. CP-L10's issuer-source input must not require a document type, or the pack goes Blocked. MODEL builds without CP-1D, and the Financial change topics read `Partial`. Tests in 09.2 and 09.5.
3. **A Full-depth Handoff reused in a quick run, or the reverse.** Expected: the validator rejects `basis` Full at quick and `basis` Screening at full (`basis_depth`). Test in 09.3.
4. **A topic that breaks the LITE policy.** Expected: a High topic with Missing or Conflicted evidence marked anything but `Gap only` fails validation, `Immaterial` without `Sufficient` evidence fails, and a family with no row fails. Test in 09.3.
5. **Resuming or accepting a CP-L10 step** after a closed chat, on the r14-style id `CP-L10` that the old `CP-[0-9]+` patterns rejected. Expected: `dispatch-message`, `accept`, `resume` and `proxy_run --module CP-L10` all work. Test in 09.1.

## Shared interfaces (names later tasks rely on)

- **Module id pattern.** A module id is `CP-` + optional letter + digits + optional letter. Regex: `CP-[A-Z]?[0-9]+[A-Z]?` (matches `CP-1A`, `CP-L10`). Better still, derive allow-lists from `rbot/modules/*/contract.json`. Task 09.1 picks one, and every gate uses the same helper: `rbotlib.catalog.module_ids(root) -> frozenset[str]` (new), or a shared regex constant.
- **Catalog.** `Pathway.depths["quick"]` is the list above. `next._plan` resolves `pathway.depths[record["depth"]]` for any Pathway and depth.
- **Validator finding codes:** `basis_depth` (R4a) and `screen_policy` (LITE rules). Both are malformed (exit 2), like the other table findings.
- **Fixture lookup.** `fixture_path(module_id, depth) -> Path`, which prefers `tests/fixtures/handoffs/quick/<ID>.md` at quick. It is used by `proxy_isolated` (`--fixtures`), `tests/report_run.py` and `test_pathway_fixtures.py`.
- **Chart.** `chart.topic_counts` is registered in `CHART_IDS` and `REGISTRY`. Source table `cpl10.screen_topics`; categories `materiality` (scale order); series `disposition` (scale order); one chart per `family` present; counts are integers (0 is a real count, not a gap); origin `host (counts)`; placement Analysis › CP-L10.

---

### Task 09.1 — Module-id and depth gates become catalog-driven (`mx-feature`, ~200 lines)

**Files:**
- Modify: `rbot/scripts/rbotlib/dispatch.py` (~474 `prepare_message`, "undeclared module target"), `rbot/scripts/rbotlib/attempts.py` (~333 `target` allow-list of the nine v1 modules), `rbot/scripts/rbotlib/isolation_code_roots.py` (~106–107), `rbot/scripts/rbotlib/next.py` (~33–41 `_plan`, the FCA/full-only gate), plus the new shared helper (in `catalog.py` or a small module).
- Test: the existing test files for those modules (`tests/test_dispatch*.py`, `tests/test_attempts*.py` or `test_accept*.py`/`test_resume*.py`, `tests/test_isolation_code_roots.py`, `tests/test_next*.py`).

**Tests first.** These must fail before the change:
1. On a stand-in tree (`tests/spec_fixture.py` already models CP-L10 and quick lists), `prepare_message` for target `CP-L10` produces a message.
2. `accept` and `resume` accept a `CP-L10` step.
3. `proxy_run`'s isolation check accepts `--module CP-L10`.
4. `next` on an approved FCA **quick** run returns the first step of the quick list instead of "unsupported or corrupt approved plan".
5. Negative tests: an id that is not a module (`CP-99`, `CP-L`) is still refused, and `next` on a depth missing from the catalog is still refused.

**Done when:** the four gates use one helper, the old hard-coded nine-module list is gone, the negative cases still refuse, and the gates pass. No catalog change yet: the real tree still has only `full`, so test against the stand-in tree.

### Task 09.2 — CP-L10 module (09A) (`mx-feature`, ~700 lines; split into 09.2a contract + MODULE.md and 09.2b fixture + specs if it exceeds 800)

**Files:**
- Create: `rbot/modules/CP-L10/contract.json` and `rbot/modules/CP-L10/MODULE.md` (generated by `uv run python rbot/scripts/rbot.py render-module CP-L10 --write`).
- Create: `tests/fixtures/handoffs/CP-L10.md`.
- Modify: `tests/module_specs.py` (`TABLES["CP-L10"]`, `INPUTS["CP-L10"]`); the `rbot/modules/CP-1A/contract.json` and `rbot/modules/CP-1B/contract.json` consumer lists (add `CP-L10` where the spec lists it, in spec order) and their regenerated `MODULE.md`; `tests/test_membership.py` (`_owners` must build owners **per depth list**, not from all contracts, because CP-2 and CP-L10 both declare `snapshot.credit_view` and `snapshot.strengths_weaknesses`).

**Contract content (exact values; copy CP-2's credit-view columns byte for byte from `rbot/modules/CP-2/contract.json`):**
- `module_id` `CP-L10`; title "Quick-depth screen".
- `reader_question`: "Which financial, liquidity, covenant, distress and value changes are decision-relevant, and where is Full work required?"
- Inputs:
  - handoff `CP-0` required, `CP-1` required, `CP-1A` required, `MODEL` required, `CP-1B` optional;
  - sources `issuer` and `market` with **no** `document_types` (Review Focus 2);
  - run_brief `objective`, `as_of_date`.
- Tables (spec §2.20):
  - `snapshot.credit_view`: min 1; CP-2's columns; `basis` scale `depth_basis`.
  - `snapshot.strengths_weaknesses`: min 2; CP-2's columns.
  - `cpl10.screen_topics`: min 6; columns `topic_id*`, `family*:screen_family`, `topic*`, `materiality*:materiality`, `evidence_status*:evidence_status`, `disposition*:disposition`, `priority_rank*`, `summary*`, `upgrade_module`, `cite`.
  - `cpl10.screen_items`: min 3; columns `item*`, `assessment*`, `evidence*`, `transmission*`, `implication*`, `confidence*:confidence`, `cite*`.
  - `cpl10.upgrade_triggers`: min 0; columns `topic_id*`, `trigger*`, `decision_impact*`, `required_source*`, `target_full_module*`, `blocking*:yes_no`.
  - Consumers are the spec's lists filtered to shipped modules plus REPORT. That is `REPORT`, `CP-3`, `CP-5`, `CP-6` where the spec names them; `check_tree._consumers` rejects unshipped consumers.
- Process: port r14. Steps:
  1. Source gate (identity; COMPLETE or PARTIAL).
  2. Classify every canonical topic per R1.
  3. Rank (R2).
  4. Assign disposition, with the LITE rules quoted verbatim from `CP-L10_CP_LITE_ANALYSIS_POLICY_v1.md`.
  5. `screen_items` as an Evidence → transmission → implication chain, with an `OVERALL` item carrying the screening posture.
  6. Credit view and strengths/weaknesses at `basis` Screening, with Sector Outlook per R3. The Credit Score method follows CP-2's "Overall Credit View" step wording, because r14 has no Credit Score at LITE. Mark this in the step.
  7. `upgrade_triggers`: every Deepen topic and every decision-material Gap-only topic.
  8. Gaps.
- Prohibited, ported from the r14 prohibitions: no canonical numeric history, no normalized financials, no restating CP-1 definitions or MODEL fields, no null-to-zero.
- `MODULE.md` + canon must stay ≤ 51,200 bytes. Record the byte count in the report.

**Tests first:**
- `test_tables_are_those_of_the_interfaces_spec[CP-L10]`, `test_inputs…[CP-L10]`, `test_module_md_is_generated_and_within_budget[CP-L10]` and `test_handoff_fixtures_validate[CP-L10]` (the corpus marker, against the synthetic `czr-2026q2-primary` pack). The fixture cites only that pack's files; the Blocked variant exits 3. These fail until the files exist.
- The existing `[CP-1A]` and `[CP-1B]` spec tests fail as soon as the CP-L10 folder exists (`module_specs.present_consumers`). That is the signal to add the consumer entries.
- `test_membership` owners-per-depth: a full list owning `snapshot.credit_view` resolves to CP-2, and a quick list resolves to CP-L10.

**Done when:** `rbot check` is green with the CP-L10 folder present and still no `quick` catalog entry, and the gates pass.

### Task 09.3 — Validator: LITE policy and basis-vs-depth (`mx-feature`, ~250 lines)

**Files:** `rbot/scripts/rbotlib/validate.py` (next to `ROW_KEYS`, ~33–39), `tests/test_validate*.py` (or the module test file that owns validator findings), `docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md` (add the two finding codes to the validator findings list; docs-only edit).

**Tests first, each failing before the change:**
1. `cpl10.screen_topics` row with `High` + `Missing` + `Summarize` gives `screen_policy`. The same with `Conflicted` gives `screen_policy`.
2. `Immaterial` with `evidence_status` other than `Sufficient` gives `screen_policy`.
3. Table missing any `screen_family` value gives `screen_policy`, naming the missing family.
4. With `--run` at depth `quick`: `snapshot.credit_view.basis` = `Full` gives `basis_depth`. At depth `full`, `basis` = `Screening` gives `basis_depth`. The same applies to `snapshot.recommendation.basis`.
5. Without `--run` (no run context), `basis_depth` is not evaluated, and the report says so in its `Not verified` line.
6. Regression: every existing fixture (`tests/fixtures/handoffs/*.md`) still validates. The RC5 record run's handoffs pass at `full`; check them with `rbot validate` on a copy, and record the check in the report.

**Done when:** both codes exit 2 like the other malformed findings, the existing fixtures and corpus tests are green, and the gates pass.

### Task 09.4 — CP-6 screening method (09B part 1) (`mx-feature`, ~350 lines)

**Files:** `rbot/modules/CP-6/contract.json` (process and prohibited text only; the tables are unchanged) and the regenerated `MODULE.md`; create `tests/fixtures/handoffs/quick/CP-6.md`, `tests/fixtures/handoffs/quick/CP-5.md` and `tests/fixtures/handoffs/quick/CP-3.md` (Handoffs as written at quick, with `inputs` naming CP-L10 instead of CP-2 and CP-1D); `tests/test_modules.py` (gate-text assertions near line 122).

**Contract changes (R4b, R5):**
- Step 1 (source gate): at quick, the gate is "Screening Run when CP-L10 and CP-3 are available". Every absent Full input (CP-2, CP-1D) is listed as a limitation, and `qa_status` is Restricted.
- Step 5: `snapshot.recommendation.basis` is `Screening` on every row at quick. The rationale opens with "Screening basis:".
- `cp6.challenge` at quick is built from CP-L10 `screen_items` (the `OVERALL` posture and the Deepen topics) and CP-3. Nothing is invented for absent CP-2 analysis.
- Gaps: name the linked Full run as the upgrade.
- Prohibited: add "claim committee-ready or Full-basis conviction at Quick depth" (r14 D2).
- `MODULE.md` stays within budget.

**Tests first:**
- `test_modules`: the CP-6 contract text contains the quick gate sentence and the prohibited line.
- Validate the quick fixtures at depth quick: they pass with `basis_depth` active (needs 09.3).
- A no-portfolio quick fixture variant: FIT is skipped, and CP-6 is Restricted with no FIT caps (Review Focus 1).

**Done when:** the full-depth CP-6 fixture and corpus checks are unchanged and green, the quick fixtures validate at quick, and the gates pass.

### Task 09.5 — FCA quick catalog entry, menu and grading (09B part 2) (`mx-feature`, ~300 lines)

**Files:**
- Modify: `rbot/catalog.json` (add the `quick` list from Global Constraints); `rbot/SKILL.md` (~37–43: the menu now offers Full Credit Assessment at full **and** quick; at quick, Deep Research and the Full-only modules do not run, and output is screening-only); `docs/release-notes.md` (the unreleased section).
- Tests: `tests/test_membership.py` (line ~84 asserts `"quick" not in pathway.depths`; flip it to "the committed quick list equals the derived list filtered to built steps"); `tests/test_runtime.py` (~332, installed depths become `full` and `quick`); new `test_quick_lists_exclude_full_only_modules`, spec §12.5 row 09 (no quick list contains CP-2, CP-DR, CP-1D, CP-2A, CP-2E, CP-2G or PROJECTION); new real-tree quick grading test next to `tests/test_grade_fca.py` (`czr-2026q2-lite-full-credit-screen` and `ccl-fy2025-lite-full-credit-screen` grade at quick per the KNOWN values in `tests/test_grade.py:275,286`, `L`/[]/["FIT"] and `L`/[]/["CP-3","FIT"]; adjust only if the real CP-L10 inputs justify it, and record why); `test_pathway_membership_matches_front_pages` covers quick.

**Tests first:** the four tests above fail on the current catalog.

**Done when:**
- `rbot check` is green: `_order` puts CP-L10 before CP-3, CP-5 and CP-6; `_owners` gives one owner per depth.
- `rbot approve --depth quick` works on a fixture run.
- `proxy_run --pack czr-2026q2-lite-full-credit-screen --pathway FULL_CREDIT_ASSESSMENT --depth quick` gets past approval to CP-0 (record the exit).
- The gates pass.

### Task 09.6 — `chart.topic_counts`, the Screening label, and a quick render (09B part 3) (`mx-feature`, ~450 lines)

**Files:**
- `rbot/scripts/rbotlib/report/charts.py`: the builder, `CHART_IDS` and `REGISTRY` (~28–39, 551–562), reusing `stackedColumns` and the `issue_counts` pattern (~531).
- `rbot/scripts/rbotlib/report/html.py`: the title band. When `run.depth == "quick"`, show "Screening only" next to "{pathway}, {depth} depth" (~237), using existing classes only.
- The fixture lookup helper (Shared interfaces). Wire it into `scripts/proxy_isolated.py`, `tests/report_run.py` (~32–34; parametrize depth) and `tests/test_pathway_fixtures.py` (~96–100).
- Tests: `tests/test_report_charts.py` (the set check ~100–113 grows to 11); `tests/test_report_assets.py:85` (exactly 10 charts becomes 11; the frozen blobs are unchanged); new quick render test.

**Tests first:**
1. `chart.topic_counts` on the CP-L10 fixture gives one spec per family present. Its categories are in materiality scale order and its series in disposition scale order, and the counts equal a direct count of the fixture rows. The table twin and an accessible name per mark exist (§11.4 rules).
2. A complete fixture run at quick (the R8 fixtures) renders `report.html`:
   - the Credit Snapshot shows the CP-L10 credit view, and the title band reads "Screening only";
   - the Analysis tab has a CP-L10 view with the chart;
   - the deep link `#module-cp-l10` shows only that view (F12 behaviour);
   - there are no console errors (headless Chrome, as `tests/test_report_js.py` does).
3. A no-portfolio variant renders (Review Focus 1).

**Done when:** the full-depth render tests are unchanged, the quick render passes, and the gates pass.

### Task 09.7 — Corpus closure: expectations and the quick record run (`mx-feature` for the expectations; the controller runs the record run with the proxy transport)

**Files:** create `tests/corpus/expectations/czr-2026q2-lite-full-credit-screen.json` (the `front_pages.credit_snapshot.supportable` cells this pack supports at quick, written from the pack's files the same way `czr-2026q2-primary.json` was; no projection, no CP-1D items); `tests/corpus/corpus.json` (the `expectations` pointer for that pack); `docs/corpus-runs/<date>-czr-2026q2-lite-full-credit-screen-full-credit-assessment-quick.md` (scorecard committed from the run).

**Record run (controller).**
- Run `scripts/proxy_run.py --pack czr-2026q2-lite-full-credit-screen --pathway FULL_CREDIT_ASSESSMENT --depth quick` with the proxy transport used for the Plan 08 runs: receipt, then an `mx-feature` worker with the exact dispatch bytes, then `--accept-module`.
- MODEL and FIT run inline.
- Then `scripts/acceptance.py check --run RUN`: R1–R8 must pass.
- Then `scripts/scorecard.py --run RUN --out DIR`.

**Done when:** R1–R8 pass on the quick run, the scorecard is committed, and the corpus gates are green.

### Task 09.8 — A/B records and plan closure (controller + `mx-scaffold` for docs)

- **CP-L10 A/B** on `czr-2026q2-lite-full-credit-screen`. A is `reference/deploy-v-r14/skills/cp-l10-financial-change-screen/SKILL.md` + `CANON_SHARED.md`; B is the CP-L10 Handoff from the 09.7 run. Use `scripts/ab_grade.py` (`order`, `steps`, `to-r14`, `measure`, `score`) and `docs/ab/rubric.md`. The pass bar is §12.7: ΣD(B) ≥ ΣD(A), no criterion B < A − 1, C(B) ≥ max(0.95, C(A)), G(B) ≥ G(A), F(B) ≥ 0.90. Commit `docs/ab/<date>-CP-L10-czr-2026q2-lite-full-credit-screen.md`.
- **CP-6 screening record** per R5. B is graded against the rubric with C, G and F, and D is scored absolute. The record says plainly that r14 has no LITE CP-6 (r14 `cp-6-ic-debate-challenge/SKILL.md` "LITE profile compatibility"), so there is no A side.
- **Docs.** Roadmap row 09 → executed (with commit ids); `docs/release-notes.md`; a Plan 09 corpus regression note in `docs/corpus-runs/`.

**Done when:** the CP-L10 A/B passes the bar, or it fails and the failure becomes a module fix task (a test first, then a re-run of 09.7 and the A/B per runbook §5.6). The records are committed and the full suite is green once on the branch.

## Execution order and parallelism

`09.1 → 09.2 → 09.3 → 09.4 → 09.5 → 09.6 → 09.7 → 09.8`. Each task builds on the previous one's interfaces, so there is no parallel implementation. While 09.6 runs, the controller may draft the 09.7 expectations file. Spec §13 PR mapping: 09A = 09.1–09.3, and 09B = 09.4–09.6. 09.7 and 09.8 are records.

## Open points (owner)

- R1 family mapping, R3 Sector Outlook fallback, and R5 the B-only CP-6 record. Each default is above.
- A Quick→Full upgrade command, which "can later be upgraded to Full" (CONTEXT.md), is **not** in Plan 09. No plan owns it yet.
- `ccl-fy2025-lite-full-credit-screen` (`exercises`) is graded in 09.5 but gets no record run in Plan 09. Plan 19 scores every Pathway × depth.

## Not verified (at planning time)

- Line numbers come from read-only exploration of `build/v1` `d1774df`. Nothing was executed while planning.
- Whether the real CP-L10 contract fits the 51,200-byte budget after the port.
- Whether the lite pack's actual files support every R1 family at better than `Not assessable`.
- How long the quick record run takes: about 10 module dispatches, with the Plan 08 runs at roughly 3 h for 11 steps.
