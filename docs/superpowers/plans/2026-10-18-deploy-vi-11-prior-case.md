# Prior Case — Plan11 Implementation Plan

**Goal:** Accept an earlier issuer Report, compute an exact host-owned comparison, run CP-8 last, and present the comparison, thesis review and Recommendation movements in HTML/Markdown.

**Architecture:** Parse the existing `rbot-run/1` payload without executing HTML. A pure comparison layer preserves source strings and row identities; a native command qualifies current inputs and publishes `prior/diff.json` and `prior/diff.md`. CP-8 interprets that comparison without changing the current Recommendation. Additive report helpers preserve the existing renderer API and module-pane architecture.

**Stack:** Existing Python >=3.11, stdlib HTML/JSON/Decimal, pytest/Hypothesis, the existing RBOTCharts dumbbell primitive. No dependency addition.

## Authority and execution base

- This is whole roadmap Plan11, interfaces §13 row11, §2.22 and §11.6, explicitly selected by the human for this objective. Plans12/13 follow tested predecessors; this document does not claim them implemented.
- Production traced at `1042761864c732a458670c177e607ab8fbed6a80`, tree `91ad66f2e009a3df11c49c8701a720b6ea6021ea`, lock Git blob `35bf2e7e741576c67c5e2908add759111dd8fabf`. Actual implementation checkout: `/Users/ericguei/.codex/worktrees/plans-11-13-dev/Deploy VI`, branch `codex/plans-11-13-dev`, base `bd717eb` from current `origin/main`. Root verified its production/model bytes equal1042761; recheck identities before dispatch and reuse baseline evidence only where unaffected.
- Current workflow and owner amendment govern: confidence review, causal failing tests, affected checks and retained branch/corpus/source/mutation gates remain. Independent code reviews and rewrite tournaments are retired. The human authorized Codex agents specifically for Plans11–13 after the native Sonnet CLI failed401; use fresh named `mx-feature` agents under that override, no implementer spawning. Root coordinates without production edits.
- Every coherent implementation PR including code/tests/docs/evidence remains <=800 ordinary changed lines, using only the actual existing exclusions at the implementation base. Budgets below include repair headroom; they are estimates, not waivers. Do not slice an oversized completed behavior to bypass the cap. Re-scope before editing if a complete behavior cannot fit.
- Preserve every `reference/**` byte, frozen Report A, source packs, approved histories and existing WIP; preserve XLSX input ingestion. No workbook report export, push, merge, publication or work-PC inspection. CP1D judgment rules and all money/source gates remain intact.
- Read the concise task brief plus the files named for that task; do not copy whole implementations into replay documentation. New public APIs/dependencies need their normal evidence/decision record.

## Actual seams and resolved choices

1. `inventory._entry` currently recognizes only the literal HTML `id="rbot-run"` marker, including for Markdown files. Generated Markdown instead ends in ` ```json rbot-run `. `prepare.read_html` intentionally strips scripts. Therefore inventory must recognize both formats and diff/metadata qualification must read the original inventory-hashed pack Report, not prepared text. Marker detection is discovery, never proof of a valid report.
2. `cp0._inventory` currently checks only that a listed Prior Case is flagged in inventory. `brief.from_cp0` copies offered rows; `approve._confirm_rows` chooses the lexically greatest report date and silently takes the first tie. Keep newest-date selection but qualify its metadata and refuse conflicting newest candidates. HTML/Markdown copies with identical parsed payload and run identity are one candidate, preferring HTML deterministically. Do not silently pick one of two different payloads for the same run or two distinct newest runs on the same date.
3. Existing `snapshot.run_header.report_date` remains `—` (`brief._header_row`), and rendering does not fill it. Read a non-gap ISO report_date when present; otherwise use the embedded timezone-bearing `generated_at` calendar date and explicitly record that basis. Never substitute the analysis `as_of_date`, filesystem mtime or filename. Require header/front-matter run and issuer identities to agree. Reports can legitimately be generated after their analysis date; do not reject them on that basis. Refuse the current run as its own prior and a future generated timestamp.
4. `run_json.build` requires every step terminal, so it cannot build the current comparison while CP-8 is pending. The native diff input loader instead reuses current state/Approval/source/Handoff qualification, reads accepted or Blocked predecessors in plan order, and excludes CP-8. It must not relax the Report terminal gate. A Blocked predecessor supplies explicit gap cells, not an accepted financial fact.
5. Preserve the §11.6 required JSON keys: `prior:{run_id,report_date,pathway,depth}` and `changes:[{table,key,field,prior,current,kind,numeric}]`. `key` is a column/value object (empty for a single-row table); absent row/column values use JSON null, distinct from the source's `—`. Add a small `inputs` binding (prior source path/hash and current run/brief/predecessor digests), `limitations`, date basis and field unit/period context as additive metadata. They establish reproducibility, not authentication of the earlier analysis.
6. Compare exact source strings; numeric parsing only controls drawable data, never replaces the stored text or determines whether a text field changed. Use finite Decimal with plain `-?[0-9]+(\.[0-9]+)?` cell syntax; grouped numbers, exponents, percent suffixes and narrative remain text. No floats for comparison/arithmetic, rounding or broad stripping of units. A pair is numeric only when both cells parse with compatible currency/unit/period basis. Unknown/mismatched units and gaps remain in the text comparison with a reason; they are never plotted together or replaced by zero. Dates, ids and ranks are not monetary numeric chart fields.
7. Mechanical `kind` is `changed|added|removed|unchanged`. CP-8's `change`/`outcome` use the existing different `change_kind` scale: `Improved|Unchanged|Deteriorated|New|Removed`. Do not overwrite the scale or claim a numerical increase means Improved. `why` and `lesson` contain the creditor mechanism and uncertainty.
8. Compare the union of tables on the prior/current Front Page plus `model.house` and the three §11.6 watch/covenant/rating tables, when available. Exclude `cp8.*` from recursive comparison. Compare row adds/removes only where both sides expose an authoritative table. An absent table because an owner failed/skipped, a pathway does not run it, or an older payload omits it is a named comparability limitation, not proof that the debt or thesis disappeared. Empty accepted tables do establish row absence. Unknown comparison keys refuse with table id, never use positional joins or a catch-all first-column key.
9. Report date keys and latest-column choices below are implementation rulings filling underspecified §11.6 details. Record these concise rulings beside that section during implementation. Keep the three exact §2.22 tables; do not copy r14's T7.* schema, old invocation machinery or export requirements.
10. Plan07 R3 supersedes literal tab architecture: What changed is CP-8's module pane, titled What changed, with the host diff before its tables, linked from the Snapshot summary. Keep `#module-cp-8` and existing module navigation APIs. No duplicate CP-8 view. Absent/declined cases retain a precise limitation reason.

### Explicit comparison keys

| Tables | Identity |
| --- | --- |
| snapshot.run_header, snapshot.company_profile, snapshot.credit_view, snapshot.business_description, snapshot.historical_performance, snapshot.thesis | one row; refuse multiple rows |
| snapshot.recommendation | strategy |
| snapshot.instrument_recommendation, snapshot.instrument_levels, snapshot.capital_structure, cp3.talk_valuation | facility_id |
| snapshot.capital_structure_totals, snapshot.ebitda_adjustments | line |
| snapshot.financials, model.summary | line_id |
| snapshot.financial_columns | slot |
| snapshot.strengths_weaknesses | kind, label |
| snapshot.catalysts | event |
| snapshot.portfolio_fit | portfolio_id, facility_id |
| snapshot.transaction_summary | tranche_id |
| snapshot.relative_value | block, name |
| cp6.portfolio_recommendation | portfolio_id, strategy, instrument |
| model.house | item |
| model.metrics | metric_id |
| model.maturity_wall | fiscal_year, facility_id |
| model.projection_summary | case, fiscal_year |
| cp2.watch_items / cp4.covenant_tests / cp2h.rating_triggers | trigger / test / agency, metric |

Sort tables, encoded keys and fields deterministically; refuse duplicate/blank/gap key components rather than overwrite. For `snapshot.financials`, compare descriptive fields and one `latest` numeric field: choose each report's latest available `snapshot.financial_columns` row by end_date, preferring LTM on a date tie, then YTD, then FY; never choose an older column merely because that individual cell is missing. Record both selected column ids/periods and gap reasons. This supports rolling-period comparison while making differing periods visible. `model.summary`/metrics retain their named column fields and provenance; projected and historical fields are never silently joined. The unavailable PROJECTION host table in today's catalog is a visible limitation, not a new host qualification exemption.

Native reader ruling after executed11.1a: retained pending CP-0 identity is admissible only through same-issuer/date-pattern and three equal valid embedded hashes, with an explicit unavailable-full-lineage limitation. Citations are source-local, validated and preserved under each owner, outside the global analytical-table index. The native Model legitimately repeats an EBITDA bridge display label: reader preserves every row and names missing/blank/duplicate comparison identity; strict keyed_rows refuses ambiguous joins. No guessed keys, overwritten rows, positional joins or false added/removed claims.

## Bounded implementation tasks

### 11.1 — Pure prior-report reader and exact comparison (11A; <=700 lines)

**Write set:** new `rbot/scripts/rbotlib/prior_report.py`, `rbot/scripts/rbotlib/diff.py` (pure comparison portion), `tests/test_prior_report.py`, `tests/test_diff.py`; a concise §11.6 ruling note. No catalog, run-state, dispatch or Workbench writes.

**Contract:** `prior_report.parse_report(text: str, kind: str) -> dict[str, Any]` accepts HTML or Markdown; `diff.compare(prior: dict[str, Any], current: dict[str, Any], table_ids: Sequence[str]) -> dict[str, Any]` consumes detached run documents and returns the required diff plus limitations. Errors are `RunError` naming the source/table defect. Parser accepts exactly one correctly tagged payload, JSON object schema `rbot-run/1`, nonempty identity/pathway/depth, an ISO timestamp, valid table columns/row widths and string cells; reject duplicate JSON object keys and nonfinite numbers. Allow older additive payloads without `modules`/`fetched`; never execute scripts or follow links. Embedded table owners must be unique; don't select the first Handoff containing a table.

- [ ] Write failing tests using both existing `embed_json` and generated Markdown fence syntax. Round-trip escaped `</script>`, U+2028/U+2029, pipes/newlines and malicious HTML through a text-only parser. Refuse no payload, two payloads, truncated JSON, scalar schema, duplicate columns/JSON keys, bad row widths and conflicting embedded identity; preserve ambiguous row keys with named limitations and refuse them at strict comparison admission.
- [ ] Plant a one-digit debt change, numeric-to-gap, zero-to-nonzero, a newly added facility, a removed catalyst, a strategy movement, an unchanged field and a `model.house` change. Assert complete exact expected JSON; row reordering changes nothing. A different issuer refuses. Keep an older payload missing a table visible as a limitation.
- [ ] Test latest-period selection using a newer unavailable LTM cell, differing LTM periods, same-date FY/LTM tie and unknown units; no fallback to an older non-gap figure. Numeric tests include negative decimals, grouping only if explicitly supported, exponent policy, enormous finite values, NaN/Infinity, dates and embedded units. Require chart numeric eligibility only on governed metric fields.
- [ ] Implement the pure layer and property tests: identity comparison is all unchanged; row/column permutations preserve keyed results; applying add/remove reverses direction; original strings survive; Decimal precision is preserved. Run confidence-review on parser trust boundaries and every key map entry before recording passing focused tests.

**Checks:** `uv run pytest tests/test_prior_report.py tests/test_diff.py --no-cov`; lint/format/mypy on changed files. This is the first implementable task, independent of CP-8 and Workbench.

### 11.2 — Discover and qualify the offered report at CP-0/Approval (11A; <=650 lines)

**Depends:** tested11.1. **Write set:** `inventory.py`, `cp0.py`, `approve.py`, `rbot/modules/CP-0/contract.json` and generated `MODULE.md`; focused cases in `tests/test_inventory.py`, `tests/test_cp0_checks.py`, `tests/test_approve.py`, `tests/test_approval_inputs.py`. New shared small metadata helper belongs in `prior_report.py` if needed.

- [ ] A causal test first demonstrates that an actual generated Markdown Report is not flagged today. Detect HTML or tagged Markdown structurally, retain inventory hash, and keep malformed tagged candidates visible for CP-0 to explain rather than silently accept.
- [ ] CP-0 process: inspect every flagged candidate from its original pack path through the parser. Populate exact run/date/pathway/depth, classify `issuer` / `RBOT Report`; offered Yes only for matching issuer and usable report metadata. Parseable foreign candidates remain prior_case rows with No. An unparseable marker candidate remains explicitly described in source_inventory/Gaps and is omitted from prior_case, whose critical metadata columns cannot truthfully hold it. For HTML, visible text supplies normal citations; machine metadata qualification uses the original payload, never fabricated prepared-script text.
- [ ] Validate CP-0 Prior Case rows against original inventory-hashed report bytes: wrong date/run/pathway/depth/offered flag, omitted usable flagged candidate, unsupported file/path/link, current-run self-reference and edited source refuse with specific findings. An unparseable candidate cannot become an offered brief row. Qualify metadata at Approval too; a CP-0 claim alone never grants the report path.
- [ ] Selection retains one newest eligible candidate. Test older/newer in either table order, equivalent HTML/MD deduplication, conflicting same-run payloads, two newest distinct runs with the same date, no offer plus yes, and explicit decline. Refuse ambiguity before brief/state/folder publication; decline keeps CP-8 `skipped` / `no prior case`. Current source hash change refuses before content is used.
- [ ] Update existing approval fixture Reports (`tests/test_approve.py` currently uses `{}` payload) into valid minimal embedded reports; do not bypass new qualification to preserve fake fixture success. Keep all source/lock/ownership protections. Run confidence-review and affected tests.

**Checks:** `uv run pytest tests/test_inventory.py tests/test_cp0_checks.py tests/test_cp0.py tests/test_approve.py tests/test_approval_inputs.py tests/test_approval_authority.py --no-cov`; `uv run python rbot/scripts/rbot.py check`.

### 11.3 — Native diff publication and fresh CP-8 grants (11A; <=750 lines)

**Depends:** tested11.1/11.2. **Write set:** `diff.py` native command portion (split small `prior.py` qualification helper if needed), `cli.py`, `dispatch.py`, `resume.py`, `rbot/SKILL.md`, `scripts/proxy_continue.py`; new `tests/test_diff_cli.py`, `tests/test_prior_dispatch.py`; affected `tests/test_dispatch_boundaries.py`, `tests/test_proxy_continue.py`.

**Contract:** `diff.add_command(sub)` installs `diff --run RUN --prior report.html|report.md`. A shared read-only `qualified_prior(run, root, record)` returns the selected original report, current diff object and canonical Markdown after checking the entire input binding. This helper must be callable during dispatch's existing held lock without acquiring another one and without publication. Do not call `run_json.build` or `dispatch.qualified_message` recursively.

- [ ] Require native ownership, Approval with accepted prior, `--prior` matching the approved pack-relative path (or that exact absolute file), original inventory hash, guarded regular files and matching issuer. Reject absolute foreign paths, traversal, symlink/hardlink parents/files, absent/malformed payload and source changes before reading ungranted content or publishing output. `--prior` selects no new report and cannot override Approval.
- [ ] Qualify all terminal predecessors using existing dispatch/host seams; pending/running predecessors refuse, failed/skipped predecessors become named comparison limitations. Respect accepted-current edits/CP0 lineage, MODEL and FIT execution evidence. The diff helper must not invent a PROJECTION qualification path. Build current tables from qualified current Handoffs and Run Brief; exclude CP-8, even after it becomes terminal.
- [ ] Under the existing publication lock, preflight both output paths, write each atomically, recheck captured inputs before publishing, and use ordinary CLI receipt/log handling. Both outputs derive from the same object with no wall-clock fields; identical inputs produce identical bytes. Freshness excludes CP-8's own state/Handoff and volatile log/update counters, so accepting CP-8 does not invalidate its inputs. An interrupted pair is detected by comparing JSON and canonical Markdown on use; no half-pair is trusted. Preflight failures preserve previous outputs; a later write fault can leave a detectable incomplete pair and must exit1 naming the file. Do not claim rollback or two-file filesystem atomicity.
- [ ] CP-8 dispatch grants the qualified original prior Report and both diff files read-only, with their actual digests; still only its Handoff is writable and no fetching is granted. Require canonical diff equality at dispatch and accept re-qualification; edited JSON/Markdown, changed current Handoff, edited prior source, duplicate ownership or stale input binding must refuse before worker transport/acceptance. Extend `resume.fingerprint` to include CP-8's qualified prior artifacts, so interruption cannot substitute their bytes.
- [ ] Keep `next`'s existing semantics: it selects/prepares and never executes a host command. Before selecting CP-8, SKILL and proxy continuation explicitly run native diff once when CP-8 is the next outstanding step, using state.prior_case.report; then call next. Direct next/dispatch without a valid diff returns an actionable exact diff command. Do not add a fake host step, mutate plan order or auto-rewrite stale artifacts at accept. A retry reuses the same qualified diff or pauses if inputs changed.
- [ ] Test real native owned run through approval → predecessor completion → diff → next → receipt → CP-8 accept in a temporary CP-8 contract tree. Verify no writes for declined/no-prior, exact approved path, stale pair, busy ownership, failure between output writes, and substitution after dispatch before accept. Scope proxy tests to full-run continuation; isolated CP-8 imports must refuse explicitly until they carry an actual approved prior rather than borrowing an unrelated pack run.
- [ ] Confidence-review lock nesting, output ordering, all re-qualification callers, error receipts and restoration after injected faults.

**Checks:** `uv run pytest tests/test_diff_cli.py tests/test_prior_dispatch.py tests/test_dispatch.py tests/test_dispatch_boundaries.py tests/test_accept.py tests/test_accept_safety.py tests/test_proxy_continue.py tests/test_resume.py --no-cov`. If a named existing test file is absent at execution, locate its actual current counterpart and record the corrected command, never report an unrun command as passed.

### 11.4 — Report prior data and the two charts (11B; <=650 lines)

**Depends:** tested11.3. **Write set:** focused new `rbot/scripts/rbotlib/report/prior.py` (data helpers), `run_json.py`, new `report/prior_charts.py`, minimal `charts.py` registry imports; `tests/test_report_prior.py`, `tests/test_report_charts.py`, `tests/test_report_run_json.py`. Preserve current `build_all`, `render_html`, `render_markdown`, `Ctx` interfaces.

- [ ] `run_json.build` fills `prior_case.report/report_date/diff` only from the accepted qualified source/diff. Declined/absent stays null. Accepted prior with missing/stale pair refuses; failed/Blocked CP-8 preserves host comparison with its actual status/limitation, never the unconditional no-prior statement.
- [ ] Register `chart.what_changed` and `chart.expected_realised` using existing dumbbell entry/table-twin machinery. Host diff chart takes only compatible governed numeric changed pairs; do not plot ids, dates or scalar text. Partition panels by unit/basis rather than mix debt, bps and multiples on one axis. Keep exact displayed strings and escaped labels; float conversion only positions SVG marks.
- [ ] Expected/realised chart reads `cp8.thesis_review` and plots only pairs where both complete cells parse with matching units; narrative expectations remain in the full table with an undrawn reason. Origin is model for this chart and host for the script diff, with existing mark provenance/accessibility. No expected result is reconstructed from actual outcomes.
- [ ] Test negative/zero values, one-sided gaps, no numeric rows, mismatched currency/unit, very large precision, text expectations, malicious labels and distinct prior/current dates. Every drawn chart has a title/summary/table twin; absent charts give an honest reason. Embedded JSON contains precisely the drawn series and original full diff.
- [ ] Keep source/diff qualification errors visible as ReportError and prove old source/model/frozen asset tests remain unchanged. Confidence-review numerical parsing, unit partitions, origin markings and Report terminal gating.

**Checks:** `uv run pytest tests/test_report_prior.py tests/test_report_run_json.py tests/test_report_charts.py tests/test_report_assets.py --no-cov`.

### 11.5 — What changed pane and Snapshot summary (11B; <=650 lines)

**Depends:** tested11.4 and the Workbench integration checkpoint for shared callsites. **Write set:** `report/prior.py` presentation helper or focused `report/prior_views.py`, minimal `html_views.py`, `html.py`, `markdown.py`, `blocks.py`; `tests/test_report_prior.py`, `tests/test_report_blocks.py`, `tests/test_report_markdown.py`, `tests/test_report_html.py`, `tests/test_report_js.py`. Root coordinates shared callsites with the separate Workbench checkout before dispatch; do not overwrite Workbench changes or change renderer signatures.

- [ ] Add the `prior_case` condition to blocks and a precise false-condition reason. The comparison summary links to `#module-cp-8`, includes the qualified prior date and counts from the diff, and uses the CP-8 owner status when failed/skipped. Credit Snapshot block19 is a summary line/link only; no duplicate full diff/chart on the Front Page. Its catalog activation waits11.6.
- [ ] CP-8 module pane title is What changed. Place host diff Markdown content as safe generated tables/text, then both chart panels and all three CP-8 tables plus Analysis/Gaps/status. Never render arbitrary prior Markdown as trusted HTML or execute its script. The helper renders the canonical diff object equivalent to `prior/diff.md`; it must not omit added/removed rows.
- [ ] Markdown has the same host diff then CP-8 content and chart twins exactly once under What changed, not a second duplicate module section. Remove unconditional no-prior limitation only when the accepted prior comparison actually exists. Declined, no-offer, absent-from-old-plan, failed and Blocked cases display their actual reasons.
- [ ] Browser tests navigate `#module-cp-8` and the Snapshot summary link, check keyboard focus/current pane, offline resources, no console errors, escaped injection strings, print behavior and accessible chart names. Run both existing renderer and Workbench-facing tests after integration.
- [ ] Confidence-review nav/FOLDED ownership, duplicate chart numbering, anchors in Evidence, untrusted text and absent status. No CSS/design replacement is required by Plan11.

**Checks:** `uv run pytest tests/test_report_prior.py tests/test_report_blocks.py tests/test_report_html.py tests/test_report_markdown.py tests/test_report_js.py tests/test_report_quick.py --no-cov`.

### 11.6 — CP-8 method port, guarded table policy, catalog activation (11A/11B; <=780 lines)

**Depends:** tested11.3–11.5. **Write set:** new `rbot/modules/CP-8/{contract.json,MODULE.md}`, `tests/fixtures/handoffs/CP-8.md`, `tests/module_specs.py`, `tests/test_modules.py`, `tests/test_membership.py`, minimal `rbot/catalog.json`, `rbot/SKILL.md`; producer contract consumer lists/generated modules; new `rbot/scripts/rbotlib/prior_case_policy.py` with minimal `validate.py` callsite and `tests/test_prior_case_policy.py`. Count every generated MODULE.md and all consumer edits in the ordinary-line budget; reduce prompt redundancy, never analytical behavior. This scope activates the complete user path only after the earlier capabilities work.

**Exact tables, §2.22:**

| Table | Columns (* critical), minimum |
| --- | --- |
| cp8.what_changed | block*, field*, prior_value*, current_value*, change*:change_kind, why*, cite; 1 |
| cp8.thesis_review | prior_item*, expected*, realised*, outcome*:change_kind, lesson*, cite; 1 |
| cp8.recommendation_change | strategy*:strategy, prior*:recommendation, current*:recommendation, reason*; 0 |

**Inputs:** required CP-0; optional in §1 order, filtered to shipped predecessors: CP-1, CP-1A, CP-1B, CP-1D, CP-2, CP-3, CP-6, CP-L10, CP-DR, MODEL, FIT, CP-5. Sources issuer (the earlier Report), Run Brief prior_case. Add later Plan12/13 producers only when shipped. Every present §2 producer table listing CP-8 gains that consumer at the same activation checkpoint; use `module_specs.present_consumers` to enumerate, not an invented approximate list.

- [ ] Port the complete applicable analytical method from frozen `reference/deploy-v-r14/skills/cp-8-decision-ledger-post-mortem/SKILL.md` and `references/REF_CP-8_STEPS.md`: original decision/thesis/uncertainty and catalysts captured as recorded; dated realised outcomes and observation window; descriptive expected/realised variance; attribution separating process from outcome (Thesis Confirmed, Flagged Risk Materialized, Unflagged Risk Materialized, Right for Wrong Reason, Premature/Mistimed, Insufficient Information); strongest contrary evidence and what would make it win; timing/sizing/exit discipline only where recorded; evidence-grounded lesson and consolidated Gaps. Pattern calibration requires >=3 comparable decisions and remains advisory; a single Prior Case supports an observation, never a new prior or invented hit-rate population. Put method details in Analysis under named headings because the three new canonical tables do not carry every r14 register field. The current Recommendation is read-only, not a new CP-8 decision.
- [ ] Host-generated diff supplies exact prior/current values. CP-8 maps rows to human-readable block/field names with stable key context, explains Improved/Deteriorated from creditor consequences, preserves gap explanations in critical display values and Gaps. No changes: write a truthful Unchanged row from an actually compared field; no comparable field/thesis: Blocked with gap cells and explanation. Missing one expectation or an open observation window: Restricted with a precise limitation, never reconstructed expectations. Recommendation rows cover strategies present with valid recommendations on both sides; newly introduced/absent strategy is described in what_changed/Gaps, not a fake enum value.
- [ ] Add focused validation for CP-8 against qualified diff and prior evidence: no altered mechanical prior/current values, no conflicting duplicate block/field, no invented strategy Recommendation moves, no unsupported Pass when its documented gating evidence is missing. Use stable shared comparison-label projection so the validator and prompt agree. `calc: rbot diff <table> <key> <field>` identifies script values; prior/current factual citations still use inventory/prepared source evidence. Do not make arbitrary `prior/` files a new trusted citation class.
- [ ] Fixture is explicitly test-only and pack-anchored, not a claimed real prior issuer decision. Keep pure shape validation and use a dedicated temporary prior-report run for CP-8 run-aware validation. Existing `test_handoff_fixtures_validate` must select that genuine prepared fixture context for CP-8, rather than silently omit source checks or invent prior evidence in the canonical synthetic pack.
- [ ] Append CP-8 last to both existing FCA depth lists. Add `cp8.what_changed` to Credit Snapshot tables and final `what_changed` block with condition prior_case and summary-only rendering. Keep absent other Pathways absent. Remove tests asserting CP-8 is unbuilt; assert last position, optional dependency order and both accepted/declined transitions. Amend SKILL Approval offer and `--prior-case yes|no` once the behavior is active.
- [ ] Tests: exact schema/inputs/generated budget; valid/Restricted/Blocked Handoff; mismatch of each mechanical field; unsupported Recommendation, new strategy, zero/no-change run; Full and Quick actual native completion with yes, explicit no, no candidate, stale source and tied candidates. A prior report cannot alter current CP-6/FIT outputs. Preserve normal fail/skip status propagation.
- [ ] If consumer+prompt+tests cannot fit780 lines, report actual measured delta before dispatching a revised coherent scope; no new exclusion. Confidence-review analytical method coverage, status policy, copied source provenance and activation ordering.

**Checks:** `uv run pytest tests/test_modules.py tests/test_membership.py tests/test_prior_case_policy.py tests/test_prior_dispatch.py tests/test_approve.py --no-cov`; `uv run python rbot/scripts/rbot.py check`; required-root CP-8 corpus validation.

### 11.7 — Functional corpus closure and separate analytical acceptance (<=700 lines per record scope)

**Depends:** all implementation tasks tested. **Write set:** affected expectations, one concise actual implementation handoff, CP-8 A/B record, genuine proxy scorecard(s), roadmap row11/release note. Separate coherent records if necessary; no repeated reviewer packets. Do not modify source packs/reference fixtures to make an analytical result pass.

- [ ] Add `test_diff_on_two_fixture_reports` (§12.5 Plan11) using actual rendered HTML/Markdown payloads with planted changes, exact numeric/source assertions and different-issuer refusal. Extend `tests/report_run.py` through an explicit opt-in Prior Case shape without changing ordinary no-prior defaults; run both depths through real native transitions and rendering. No hand-edited terminal states may stand in for this functional proof.
- [ ] The §12 primary `tid-vmo2-2026q1` is currently registered for EARNINGS_UPDATE, which is not installed until Plan14. Do not add a stand-in production Pathway. Qualify its files under today's actual FCA full route with the actual `tid-vmo2-fy2025` earlier Report, and record this explicit route distinction; preserve the planned Earnings Update scorecard for Plan14. `prior_pack` metadata currently does not materialize a prior report. Copy only a real completed prior Report into the mutable proxy pack before inventory, record its originating run/hash, and regenerate inventory/prepare/CP-0 natively. Add a small guarded proxy import helper and tests if repeatable native staging cannot be expressed by the existing tool; bound it as its own <=600-line coherent behavior rather than an implicit manual substitution.
- [ ] Run controller proxy with native receipts/acceptance, CP-8 accepted and diff generated; `scripts/acceptance.py check --run RUN` and `scripts/scorecard.py --run RUN --out DIR` record real outcomes and limitations. Earlier report source gaps do not become zero. A synthetic two-report fixture proves mechanics; it does not qualify the real decision method.
- [ ] Separate CP-8 A/B per §12.7 and `docs/ab/rubric.md`: r14 original + canon vs new exact dispatch, identical qualified original/current inputs and source pack, Markdown only. Blind analytical scoring uses the existing harness; this is analytical acceptance, not a retired code-review approval stage. Record actual scores/evidence or say unmeasured; do not synthesize them. Pass bar: sum D(B)>=sum D(A), no D(B)<D(A)-1, C(B)>=max(.95,C(A)), G(B)>=G(A), F(B)>=.90 when expected Front Page cells apply. Put the new CP-8 Front Page expectation in the actual experimental expectation file, including stable row identities; `--f-b` cannot be faked or omitted. A measured failure becomes a bounded causal fix task.
- [ ] Until that real proxy/A-B work is performed, distinguish implemented local mechanics from unqualified analytical/runtime behavior. A/B agent scoring is not evidence of live Copilot, provider identity, fetch or Windows qualification. No work-desktop inspection resumes.

## Verification and retained gates

Every task: capture actual base/tree/lock, red test then passing command/exit/count, confidence-review doubts and findings; run affected tests once after final edits. Full integration uses the actual `.github/workflows/ci.yml`, `gitleaks.yml`, `Makefile`, `pyproject.toml`, corpus README and installed tools, not a remembered legacy checklist:

```sh
uv sync --locked --all-groups
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python rbot/scripts/rbot.py check
RBOT_REQUIRE_CORPUS=synthetic uv run pytest -m corpus --no-cov
make corpus
uv run python scripts/check_suppressions.py
uv run complexipy rbot/scripts scripts --max-complexity-allowed 15
uv run bandit -r rbot/scripts scripts -f json -o /tmp/plan11-bandit.json
uv run python scripts/check_bandit_floor.py /tmp/plan11-bandit.json
uv run pip-audit --strict
npx --yes jscpd@5.2.0 --threshold 3 --min-lines 10 rbot/scripts scripts tests
bash scripts/check_pr_size.sh
```

Bandit findings are evaluated through the existing floor, preserving its actual exit and report, rather than treating its nonzero scan exit as a passed clean scan. Run pinned gitleaks per its workflow on the actual branch range; report unavailable tooling honestly. Set real `RBOT_CORPUS_ROOTS` before `make corpus`, resolving/hash-verifying both external roots; roots-unset or synthetic-only results never close that gate. Use exact final commands from the base's size script (bd717eb has existing differences from1042761); count new/untracked/evidence files too. Compare protected-byte hashes to root's baseline manifest before claiming source integrity.

Sensitive changed-code mutants must challenge: issuer equality; approved prior path/hash; newest tie refusal; duplicate-key refusal; subtraction/order reversal; missing-to-zero; current/old period selection; malformed/stale diff acceptance; skipped-owner disappearance; diff source changes between dispatch and accept; and host/model origin. Run them in a throwaway workspace following `scripts/mutation_workspace.py` / `scripts/mutate_fetch.sh`; the former does not copy launcher `rbot.py`, so copy it explicitly if selected tests import CLI. Record actual killed/surviving mutants and refute each survivor. Retain Hypothesis exact-decimal/key/order properties. Reuse unaffected Plan10 money/model/source evidence only when root verifies matching production/dependencies/assumptions; no invented new qualification claim.

## Dependencies and remaining uncertainty

Order: `11.1 -> 11.2 -> 11.3 -> 11.4 -> 11.5 -> 11.6 -> 11.7`. Chart and view work can split only after their interfaces are tested; catalog activation comes last. Root provides fresh concise file contracts and actual predecessor evidence. Shared Workbench callsites wait its tested checkpoint, while11.1–11.3 progress independently.

- Local report dates are now resolvable from generated_at; selecting between genuinely different newest same-date reports remains a visible refusal because the CLI has no analyst-selection flag. An explicit future selector would be a separate authorized interface change.
- The exact live VMO2 proxy source sufficiency and size are unknown before execution. `tid-vmo2-fy2025` and Q1 source packs may give Restricted/Blocked source outcomes; record them. Do not invent committee decisions, expected returns, outcomes or attribution to obtain Pass.
- Plan14's EARNINGS_UPDATE primary route cannot close in Plan11. The actual FCA-route experiment closes Plan11 mechanics/method only; state this distinction in its record.
- Real diff/parser/Module size and mutation performance are measured during implementation. These budgets are not measured results. No newly invented catch-all, suppression, cap exclusion or missing-data exemption is authorized.

Not verified: Plan11 production implementation, functional or mutation results, full required-root corpus closure, real proxy/A-B analytical acceptance, live Copilot/account/provider/fetch/platform behavior, Windows work PC or publication. Planning only.
