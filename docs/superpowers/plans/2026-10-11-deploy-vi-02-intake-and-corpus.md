# Deploy VI — Plan 02: Intake and corpus

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn an analyst's Source Pack into a hashed inventory, page-anchored text and portfolio JSON; check every Handoff citation against that text; build the Run Brief from the CP-0 Handoff; and register the local issuer corpus (34 packs, every file sha256-pinned) with deterministic corpus tests, the synthetic CZR Primary pack and the first step of the proxy run.

**Architecture:** Each new command lives in its own `rbotlib` module (`corpus`, `inventory`, `prepare`, `portfolio`, `brief`) and registers itself on the Plan 01 command line through `add_command(sub)`; a command given `--run <RUN>` writes only inside the run folder and logs one line to `<RUN>/log/rbot.log`. The prepared text (`<<< page N >>>` anchors) is the single thing citations are checked against: `rbot validate --run` refuses a citation whose source is not in the run or whose excerpt is not in that source's text. The corpus registry `tests/corpus/corpus.json` pins every corpus file by sha256; corpus tests materialise a pack into a temporary Source Pack and fail (never skip) under `RBOT_REQUIRE_CORPUS=1` when a file is missing or changed.

**Tech Stack:** Python ≥ 3.11 standard library plus `pypdf==6.19.0` and `openpyxl==3.1.5` at runtime (decision records 0002, 0003); `types-openpyxl` for mypy; the Plan 01 toolchain (uv, pytest + pytest-cov + hypothesis, mypy strict, ruff, complexipy, bandit, pip-audit, jscpd, gitleaks).

**Spec:** [`docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md`](../specs/2026-10-11-deploy-vi-interfaces.md) — §13 row **02** (scope, files, interfaces, PRs), §8.1 (run folder), §7 (portfolio JSON), §9 (`inventory`, `prepare`, `brief`, `validate --run`, `corpus`), §12 (corpus), §14.1 amendments A1, A3, A4, A5. Read with the design [`2026-10-11-deploy-vi-rbot-design.md`](../specs/2026-10-11-deploy-vi-rbot-design.md) (D6, D8, D14, D15, D28), the glossary [`CONTEXT.md`](../../../CONTEXT.md) and Plan 01 ([`2026-10-11-deploy-vi-01-foundation.md`](2026-10-11-deploy-vi-01-foundation.md)), whose executed tip (commit `813aa02`) this plan starts from.

**Rebase note (2026-10-11).** Base: Plan 01's executed tip, commit `813aa02` (116 tests), not Plan 01's plan text. Plan 01's review rounds changed the code this plan patches, so each task was replayed onto `813aa02`, every gate and the corpus gate re-run at each task boundary, and every code block, patch, base64 block, test count and PR size below regenerated from the replayed tree.

- Already in the base, built on here rather than added: public `rbotlib.handoff.cells` (was `_cells`; A8 makes it escaped-pipe aware); the validator's `duplicate_citation` and its exclusion of citation-table rows from marker counting, matched by parsed cells (Task 6 adds the test with `\|` in an excerpt); `_rules_block(rules, module_id)` with its new lines, the `## Conventions (not checked)` section and the `*` note; strict list and type checks in `contract.py`; `load_contracts` over module folders; the CLI's `error: <path>: <reason>` path (Task 7 keeps it); the gitleaks path allowlist, `bandit … || true` in CI and `.hypothesis/` ignored.
- Plan 01 final-review deferrals applied: **M4** the rules block says `inputs: <Handoff ids comma-separated, or none>` (Task 1, with A4); **M10** a non-string table `id` or `title`, or a non-list `document_types`, is a `ContractError`, never coerced with `str()` (Task 1); **M5** a table whose header or separator is indented four or more spaces is a code block, so its tag is reported as an orphan (Task 6, with A9).
- Moved for the 800-line cap: amendment A5 (PR-size exclusion of `tests/corpus/synthetic/**`, `corpus-runs/` ignored) from Task 1 to Task 8, where the first synthetic pack lands; nothing reads it earlier.

## Global Constraints

- Repo root: `/Users/ericguei/Documents/Deploy VI`. Analyst data never enters it; `rbot-runs/` and `corpus-runs/` are ignored. Source files are only read, never modified; `rbot` commands write only inside the run folder.
- Runtime dependencies: exactly `pypdf==6.19.0` and `openpyxl==3.1.5` (with its dependency `et-xmlfile`), recorded in `docs/decisions/0002-pypdf.md` and `docs/decisions/0003-openpyxl.md`; dev adds only `types-openpyxl==3.1.5.20260827`. No other new dependency. `pypdf` 6.19.0 is 25 days old on 2026-10-11: the newest release older than 30 days (6.18.1) fails `pip-audit --strict` (record 0002 explains); execute Task 3 on or after 2026-10-16 if the 30-day rule must hold on the day of install.
- Python floor `>=3.11` (ruff `py311`, mypy `3.11`) until the spike records the work machine's version.
- Every gate in `~/.claude/CLAUDE.md` section 3 exits 0 before a task is done; none is loosened; suppressions may only fall (baseline `0`). Coverage floor 80% (`--cov-fail-under=80`); complexity ≤ 15 (complexipy) and ≤ 10 (ruff mccabe); jscpd threshold 3.
- **The gate run** (named by every task): from the repo root, each must exit 0:

```bash
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python scripts/check_suppressions.py
uv run complexipy rbot/scripts scripts --max-complexity-allowed 15
uv run bandit -r rbot/scripts scripts -f json -o bandit.json
uv run python scripts/check_bandit_floor.py bandit.json
uv run pip-audit --strict
npx --yes jscpd@5.2.0 --threshold 3 --min-lines 10 rbot/scripts scripts tests
uv run python rbot/scripts/rbot.py check
```

- **The corpus gate** (from Task 2 on, at every task boundary): the owner's corpus roots exported, then both commands exit 0. A missing or changed corpus file fails; it never skips.

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov
uv run python rbot/scripts/rbot.py corpus verify
```

- PR ≤ 800 changed lines, excluding lock files, `reference/**`, `tests/golden/**/documents/**` and `tests/corpus/synthetic/**` (amendment A5 adds the last). Plan 02 ships as **five** stacked PRs, measured with `scripts/check_pr_size.sh`: **02A** = Tasks 1–2 (784 lines), **02B** = Tasks 3–4 (785), **02C** = Tasks 5–6 (799), **02D** = Tasks 7–9 (744), **02E** = Tasks 10–11 (612). The interfaces spec §13 groups the same work as three PRs; measured, it does not fit three PRs under the 800-line cap, so: §13's 02A stays 02A, except that `validate --run` (which needs prepared text) moves after `prepare` into 02D; §13's 02B (inventory + prepare) becomes 02B + 02C, and 02C also carries the controller's amendments A8 and A9 with deferral M5 (02A has no room under the cap; 02C is one line under it, so transcribe exactly); §13's 02C (brief + synthetic pack + proxy skeleton) becomes 02D + 02E. Order and scope are unchanged.
- `reference/deploy-v-r14/` is never edited and never installed (ADR 0003).
- No stub or fake value standing in for real behaviour; no catch-all that hides a failure. Every task report ends with a `Not verified:` line (each task says what to list).
- Glossary words exactly as in `CONTEXT.md` (Source Pack, Handoff, Run Brief, Primary, Price Talk, Image-Read Value, Portfolio Context …); names, ids, columns, schemas and commands exactly as in the interfaces spec.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **How to apply this plan's code.** A line "`<path>` — create:" is followed by the file's complete content: write it byte for byte, ending with one newline. A line "`<path>` — patch:" is followed by a unified diff against the previous task's end state: save the block to a file and run `git apply <file>` from the repo root (if `git apply` refuses, the tree is not at the previous task's end state: stop and report BLOCKED). A line "`<path>` — binary, base64:" is followed by base64: save the block to a file and run `base64 -d -i <file> -o <path>` (macOS) or `base64 -d <file> > <path>` (Linux). Never retype a figure, a hash or a SYNTHETIC document: the corpus tests compare sha256.
- **Agents.** Every task here is complete, verified code to transcribe and verify: implementer `mx-scaffold`; task reviewer `mx-precise`; no task touches money, ordering or security code, so no `mx-adversary` or mutation step. Escalate one rung (`mx-feature`, then `mx-precise`) only after a gate fails or the agent reports BLOCKED.

## File map

| Path | Responsibility | Task |
|---|---|---|
| `rbot/rules.json` | A1: host producers and the 70 new scales | 1 |
| `rbot/scripts/rbotlib/contract.py`, `rbot/scripts/rbotlib/render.py` | A4: `document_types` on a sources input, printed in MODULE.md; M4: the `inputs` line; M10: string-only table id and title; A8: the escaped-pipe rule in MODULE.md | 1, 6 |
| `rbot/scripts/rbotlib/handoff.py` | A8 escaped pipes in `cells`; A9 short separators, invalid tags, fenced blocks, front-matter keys; M5 indented tables are code | 6 |
| `rbot/scripts/rbotlib/validate.py` | A3 `too_large`; A9 `invalid_tag`; `--run`: `source_unknown`, `citation_unanchored` | 1, 6, 7 |
| `scripts/check_pr_size.sh`, `.gitignore`, `docs/decisions/0001-toolchain.md` | A5: synthetic packs outside the PR count; `corpus-runs/` ignored | 8 |
| `rbot/scripts/rbotlib/corpus.py`, `tests/corpus/corpus.json`, `tests/corpus/README.md`, `Makefile` | the corpus registry, `rbot corpus verify/list`, `make corpus` | 2, 8 |
| `rbot/scripts/rbotlib/inventory.py` | `rbot inventory`, `inventory.json`, the run's pack root | 3 |
| `rbot/scripts/rbotlib/prepare.py` | `rbot prepare`: page-anchored text, first-page entities and dates, `prepared/index.json` | 4, 5 |
| `rbot/scripts/rbotlib/portfolio.py` | Portfolio Context sheets to `prepared/portfolios/<id>.json` | 5 |
| `rbot/scripts/rbotlib/brief.py` | `rbot brief --from/--set/--show`, `run-brief.md` | 10 |
| `rbot/scripts/rbotlib/cli.py` | registers each command; `<RUN>/log/rbot.log` | 2, 3, 4, 7, 10 |
| `docs/decisions/0002-pypdf.md`, `docs/decisions/0003-openpyxl.md` | dependency records | 3, 5 |
| `tests/corpus/synthetic/czr-2026q2-primary/**`, `tests/corpus/expectations/czr-2026q2-primary.json` | the synthetic Primary pack and its hand-checked values | 8 |
| `scripts/proxy_run.py` | proxy run steps 1 and 5 | 9 |
| `docs/corpus-runs/2026-10-11-plan-02-corpus-regression.md` | the corpus regression record | 11 |
| `tests/builders.py`, `tests/conftest.py`, `tests/fixtures/handoff_cp0_czr_primary.md`, `tests/test_*.py` | tests | every task |

`rbot/scripts/rbotlib/portfolio.py` is an extra file beside §13's `prepare.py`: portfolio parsing is its own responsibility and Plan 05's `rbot fit` reads its output.

---

### Task 1: Plan 01 amendments A1, A3, A4 and review deferrals M4, M10

**Files:**
- Modify: `rbot/rules.json` (replace with the full version below), `rbot/scripts/rbotlib/contract.py`, `rbot/scripts/rbotlib/render.py`, `rbot/scripts/rbotlib/validate.py`
- Test: `tests/test_rules.py`, `tests/test_contract.py`, `tests/test_render.py`, `tests/test_validate.py`

**Interfaces:**
- Consumes: Plan 01's `Rules`, `contract_from_dict` (with its `_str_list` helper), `render_module` and `_rules_block(rules, module_id)`, `validate.check` (all as at commit `813aa02`).
- Produces:
  - `rbot/rules.json`: `host_producers` = `["MODEL", "RUN_BRIEF", "PROJECTION", "FIT"]`; 76 scales (Plan 01's six plus the 70 of interfaces spec §14.1, values exactly as there, in that order).
  - `rbotlib.contract.Input.document_types: tuple[str, ...]` (default `()`); a `sources` input may carry `"document_types": [...]`, a list of `document_type` scale values; `ContractError` names `unknown document type '<x>'`, `only a sources input takes document_types` or `input sources document_types must be a list of non-empty strings`. Plan 04's `rbot grade` reads them.
  - **M10:** a table's `id` and `title` must be strings; anything else is a `ContractError` (`table id 7 must be a string`, `table title ['Facts'] must be a string`), never coerced with `str()`.
  - `rbotlib.render`: the Inputs row prints `Sources: issuer (Credit agreement, Indenture)`; **M4:** the rules block gains the line `` - `inputs: <Handoff ids comma-separated, or none>`. `` under the front-matter line.
  - `rbotlib.validate.MAX_HANDOFF_BYTES = 98_304`; a larger Handoff gets finding `too_large` (exit 2).
  - Amendment A5 (the PR-size exclusion for `tests/corpus/synthetic/**` and `corpus-runs/` ignored) lands in Task 8, with the first synthetic pack: here it would push PR 02A over the 800-line cap.

- [ ] **Step 1: Branch from the Plan 01 end state**

```bash
cd "/Users/ericguei/Documents/Deploy VI"
git switch -c build/02a-registry 813aa02   # Plan 01's executed tip (or main, once it is merged there)
uv sync
uv run pytest
```

Expected: `116 passed` (Plan 01's suite at `813aa02`).

- [ ] **Step 2: Write the failing tests**

`tests/test_rules.py` — patch:

```diff
--- a/tests/test_rules.py
+++ b/tests/test_rules.py
@@ -12,6 +12,17 @@ def test_rules_load_the_handoff_shape_and_house_scales(rules: Rules) -> None:
     assert "MODEL" in rules.host_producers
 
 
+def test_amendment_a1_adds_host_producers_and_scales(rules: Rules) -> None:
+    assert rules.host_producers == ("MODEL", "RUN_BRIEF", "PROJECTION", "FIT")
+    assert len(rules.scales) == 76
+    assert rules.scales["yes_no"] == ("Yes", "No")
+    assert rules.scales["document_type"][:2] == ("Annual report", "Quarterly report")
+    assert rules.scales["document_type"][-2:] == ("RBOT Report", "Other")
+    assert rules.scales["level_basis"] == ("Market", "Talk", "Image-Read", "None")
+    assert rules.scales["unit"] == ("UNITS", "THOUSANDS", "MILLIONS")
+    assert rules.scales["rate_basis"] == ("Fixed", "Deck plus spread", "Implied")
+
+
 @pytest.mark.parametrize(
     ("cell", "expected"),
     [
```

`tests/test_contract.py` — patch:

```diff
--- a/tests/test_contract.py
+++ b/tests/test_contract.py
@@ -41,6 +41,11 @@ _BREAKS: dict[str, Callable[[dict[str, Any]], None]] = {
     "no_why": lambda d: d["inputs"][0].pop("why"),
     "negative_rows": lambda d: d["tables"][0].update(min_rows=-1),
     "no_process": lambda d: d.update(process=[]),
+    "bad_document_type": lambda d: d["inputs"][0].update(document_types=["Napkin"]),
+    "document_types_off_sources": lambda d: d["inputs"][1].update(document_types=["Other"]),
+    "document_types_string": lambda d: d["inputs"][0].update(document_types="Indenture"),
+    "table_id_int": lambda d: d["tables"][0].update(id=7),
+    "table_title_list": lambda d: d["tables"][0].update(title=["Facts"]),
 }
 
 
@@ -64,6 +69,11 @@ def _broken(change: str) -> dict[str, Any]:
         ("no_why", "has no 'why'"),
         ("negative_rows", "negative min_rows"),
         ("no_process", "process has no steps"),
+        ("bad_document_type", "unknown document type 'Napkin'"),
+        ("document_types_off_sources", "only a sources input takes document_types"),
+        ("document_types_string", "document_types must be a list of non-empty strings"),
+        ("table_id_int", "table id 7 must be a string"),
+        ("table_title_list", r"table title \['Facts'\] must be a string"),
     ],
 )
 def test_broken_contracts_name_the_problem(rules: Rules, change: str, message: str) -> None:
@@ -115,3 +125,11 @@ def test_load_contract_names_the_path_on_invalid_json(tmp_path: Path, rules: Rul
     path.write_text("{not json", encoding="utf-8")
     with pytest.raises(ContractError, match=r"contract\.json"):
         load_contract(path, rules)
+
+
+def test_a_sources_input_may_name_document_types(rules: Rules) -> None:
+    data = fixture_json("contract_cp_x.json")
+    data["inputs"][0]["document_types"] = ["Credit agreement", "Indenture"]
+    c = contract_from_dict(data, rules)
+    assert c.inputs[0].document_types == ("Credit agreement", "Indenture")
+    assert c.inputs[1].document_types == ()
```

`tests/test_render.py` — patch:

```diff
--- a/tests/test_render.py
+++ b/tests/test_render.py
@@ -82,6 +82,10 @@ def test_front_matter_rule_names_non_empty_values_and_the_module_id(rules: Rules
     assert "`module_id` is `CP-X`" in text
 
 
+def test_the_inputs_key_lists_handoff_ids_or_none(rules: Rules) -> None:
+    assert "- `inputs: <Handoff ids comma-separated, or none>`." in _cp_x_text(rules)
+
+
 def test_tags_are_one_per_table_directly_above_it(rules: Rules) -> None:
     assert (
         "Tag each table exactly once, with its `<!-- table: <id> -->` line "
@@ -121,3 +125,10 @@ def test_the_printed_headers_pass_the_checker_once_the_asterisk_is_stripped(
         text = text[: old.start()] + block + text[old.end() :]
     _, findings = check(text, contract, rules)
     assert [f for f in findings if f.code == "column_missing"] == []
+
+
+def test_document_types_print_beside_their_source_class(rules: Rules) -> None:
+    data = fixture_json("contract_cp_x.json")
+    data["inputs"][0]["document_types"] = ["Credit agreement", "Indenture"]
+    text = render_module(contract_from_dict(data, rules), rules)
+    assert "| Sources: issuer (Credit agreement, Indenture) | the filings |" in text
```

`tests/test_validate.py` — patch:

```diff
--- a/tests/test_validate.py
+++ b/tests/test_validate.py
@@ -5,6 +5,7 @@ from hypothesis import given
 from hypothesis import strategies as st
 
 from conftest import FIXTURES, fixture_json
+from rbotlib import validate
 from rbotlib.contract import Contract, contract_from_dict
 from rbotlib.rules import Rules, load_rules
 from rbotlib.validate import EXIT_BLOCKED, EXIT_IDENTITY, EXIT_MALFORMED, EXIT_VALID, check
@@ -103,6 +104,16 @@ def test_a_scale_value_that_reads_like_a_placeholder_is_valid(
     assert check(text, contract, rules) == (EXIT_VALID, [])
 
 
+def test_a_handoff_over_the_upstream_cap_is_too_large(
+    handoff_text: str, contract: Contract, rules: Rules
+) -> None:
+    padding = "x" * (validate.MAX_HANDOFF_BYTES - len(handoff_text.encode("utf-8")) + 1)
+    text = handoff_text.replace("None.", "None. " + padding)
+    assert codes(text, contract, rules) == (EXIT_MALFORMED, {"too_large"})
+    at_cap = handoff_text.replace("None.", "None." + padding[:-2])
+    assert check(at_cap, contract, rules) == (EXIT_VALID, [])
+
+
 def test_text_without_front_matter_is_malformed(contract: Contract, rules: Rules) -> None:
     assert codes("# just prose", contract, rules) == (EXIT_MALFORMED, {"not_a_handoff"})
 
```

- [ ] **Step 3: Run them to see them fail**

Run: `uv run pytest --no-cov`
Expected: FAIL — `10 failed, 116 passed`: the A1 scales and host producers (`assert ('MODEL', 'RUN_BRIEF') == ('MODEL', 'RU...CTION', 'FIT')`), `document_types` in the contract and in MODULE.md, the M10 non-string table id and title, the M4 `inputs` line, and `too_large` (`AttributeError: module 'rbotlib.validate' has no attribute 'MAX_HANDOFF_BYTES'`).

- [ ] **Step 4: Write the amendments**

`rbot/rules.json` — create:

```json
{
  "handoff": {
    "front_matter": ["module_id", "run_id", "issuer_id", "analysis_date", "qa_status", "inputs"],
    "sections": ["Analysis", "Tables", "Gaps", "Citations"],
    "qa_status": ["Pass", "Restricted", "Blocked"]
  },
  "gap_marker": "—",
  "placeholders": [
    "tbd",
    "n/a",
    "na",
    "unknown",
    "insufficient information",
    "[insufficient information]",
    "not assessable",
    "unavailable",
    "not calculable from provided materials"
  ],
  "citation_columns": ["id", "source", "locator", "excerpt"],
  "source_classes": ["issuer", "market", "portfolio"],
  "host_producers": ["MODEL", "RUN_BRIEF", "PROJECTION", "FIT"],
  "scales": {
    "credit_score": ["1 - Strong", "2 - Good", "3 - Fair", "4 - Weak", "5 - Stressed"],
    "valuation": ["V1 - Very attractive", "V2 - Attractive", "V3 - Fair", "V4 - Unattractive", "V5 - Very unattractive"],
    "recommendation": ["1 - Strong OW", "2 - Modest OW", "3 - MW", "4 - Modest UW", "5 - Strong UW", "Avoid", "N/A"],
    "credit_direction": ["Improving", "Stable", "Deteriorating"],
    "sector_outlook": ["Positive", "Neutral", "Negative"],
    "portfolio_fit": ["Fits", "Watch", "Breaches"],
    "yes_no": ["Yes", "No"],
    "source_class": ["issuer", "market", "portfolio"],
    "document_type": ["Annual report", "Quarterly report", "Earnings release", "Bond report", "Credit agreement", "Indenture", "Offering memorandum", "Lender presentation", "Term sheet", "Rating report", "Investor presentation", "Market levels export", "Sector RV Workbook", "Forward curve", "Equity value export", "Portfolio positions", "Portfolio limits", "RBOT Report", "Other"],
    "readiness": ["Available", "With limitations", "Blocked"],
    "brief_status": ["Sourced", "Analyst-asserted", "Gap"],
    "strategy": ["CLO", "Indexed Loans", "Indexed HY"],
    "sponsor_quality": ["High", "Medium", "Low", "N/A"],
    "debt_type": ["RCF", "1L Term Loan", "2L Term Loan", "SS Notes", "SU Notes", "Sub Debt", "PIK", "Hybrid", "DIP Financing", "Other"],
    "use_of_proceeds": ["LBO", "Acquisition", "Refinancing", "A&E", "Repricing", "Other"],
    "price_talk_stage": ["Initial talk", "Revised guidance", "Final"],
    "period_type": ["QUARTER", "YTD", "FY", "LTM", "PERIOD_END"],
    "unit": ["UNITS", "THOUSANDS", "MILLIONS"],
    "realization_status": ["REALIZED", "UNREALIZED", "NOT_STATED"],
    "segment_type": ["OPERATING_SEGMENT", "CORPORATE_ELIMINATION"],
    "value_type": ["PERIOD_END", "PERIOD_FLOW", "RATE"],
    "case": ["BASE", "DOWNSIDE"],
    "level_basis": ["Market", "Talk", "Image-Read", "None"],
    "metric_basis": ["3Y DM", "YTW", "YTM", "STW", "OAS", "Price"],
    "rv_block": ["Loan index", "Loan comparable", "HY index", "HY comparable"],
    "preference": ["Preferred", "Neutral", "Avoid", "Requires more work"],
    "compensation": ["Adequate", "Inadequate", "Rich", "Unclear"],
    "addback_verdict": ["Supported", "Challenged", "Rejected"],
    "debt_like_treatment": ["Debt-like", "Not debt-like", "Unclear"],
    "sw_kind": ["Strength", "Weakness"],
    "delta_direction": ["Up", "Flat", "Down"],
    "risk_direction": ["Positive", "Neutral", "Negative"],
    "change_kind": ["Improved", "Unchanged", "Deteriorated", "New", "Removed"],
    "availability": ["Available", "Not available", "Unclear"],
    "alignment": ["Aligned", "Divergent", "Unclear"],
    "gate_status": ["Met", "Not met", "Unclear"],
    "severity": ["High", "Medium", "Low"],
    "ordinal": ["High", "Medium", "Low", "Unknown"],
    "confidence": ["High", "Medium", "Low"],
    "evidence_quality": ["Audited", "Issuer-stated", "Third-party", "Analyst"],
    "comparability": ["Close", "Partial", "Weak"],
    "position": ["Above", "In line", "Below"],
    "multiple_basis": ["Trading", "Transaction", "Analyst"],
    "comparison_basis": ["YoY", "QoQ", "LTM vs FY", "vs guidance"],
    "finding_kind": ["Citation", "Consistency", "Calculation", "Legal", "Market", "Lineage"],
    "finding_status": ["Open", "Fixed", "Accepted"],
    "qa_status": ["Pass", "Restricted", "Blocked"],
    "traceability": ["Traceable", "Partly traceable", "Untraceable"],
    "depth_basis": ["Full", "Screening"],
    "screen_family": ["Financial change", "Liquidity", "Covenant and refinancing", "Distress", "Relative value", "Portfolio"],
    "materiality": ["High", "Medium", "Low", "Not assessable"],
    "evidence_status": ["Sufficient", "Partial", "Missing", "Conflicted"],
    "disposition": ["Deepen", "Summarize", "Gap only", "Immaterial"],
    "research_status": ["Answered", "Partly answered", "Unanswered"],
    "source_type": ["Pack", "Fetched"],
    "exposure_kind": ["Rates", "FX", "Commodity", "Inflation", "Sustainability"],
    "test_type": ["Maintenance", "Incurrence", "Springing"],
    "trigger_direction": ["Ceiling", "Floor"],
    "trigger_status": ["Headroom", "Tight", "Breached", "Not computable"],
    "calc_status": ["Calculated", "Directional", "Not computable"],
    "lead_lag": ["Leading", "Lagging"],
    "basis_class": ["Sourced", "Derived", "Analyst assumption"],
    "bridge_kind": ["Opening total", "Delta", "Use", "Closing total"],
    "exposure_case": ["Base", "Stress", "LME"],
    "quote_type": ["Trade", "Dealer quote", "Evaluated", "Image-Read"],
    "freshness": ["Current", "Stale", "Unknown date"],
    "five_point": ["1", "2", "3", "4", "5"],
    "limit_kind": ["Hard", "Soft"],
    "limit_status": ["Within", "Breached", "Not computed", "From file"],
    "column_basis": ["LTM", "PF-LTM"],
    "capstruct_line": ["Senior secured debt", "Unsecured debt", "Total debt", "Cash", "Equity", "EV", "PF interest", "PF interest cover"],
    "ebitda_line_kind": ["Total", "Add-back", "Unrealized add-back"],
    "snapshot_slot": ["FY-2", "FY-1", "FY", "PYTD", "YTD", "LTM"],
    "financial_section": ["Financials", "Balance sheet", "Credit metrics"],
    "house_item": ["Structuring EBITDA", "SSIM EBITDA", "Quality-adjusted EBITDA", "PF interest", "PF interest cover", "Structuring Multiple", "SSIM Multiple", "EV", "Adjusted debt", "Adjusted leverage"],
    "rate_basis": ["Fixed", "Deck plus spread", "Implied"]
  }
}
```

`rbot/scripts/rbotlib/contract.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/contract.py
+++ b/rbot/scripts/rbotlib/contract.py
@@ -42,6 +42,7 @@ class Input:
     values: tuple[str, ...]
     required: bool
     why: str
+    document_types: tuple[str, ...] = ()
 
 
 @dataclass(frozen=True)
@@ -94,6 +95,20 @@ def _input_values(kind: str, raw: dict[str, Any], problems: list[str]) -> tuple[
     return (value,)
 
 
+def _document_types(
+    raw: dict[str, Any], kind: str, rules: Rules, problems: list[str]
+) -> tuple[str, ...]:
+    """The document types a sources input names (amendment A4); `rbot grade` reads them."""
+    if "document_types" not in raw:
+        return ()
+    if kind != "sources":
+        problems.append(f"only a sources input takes document_types: {raw}")
+    found = _str_list(raw["document_types"], f"input {kind} document_types", problems)
+    scale = rules.scales["document_type"]
+    problems += [f"unknown document type {d!r}" for d in found if d not in scale]
+    return found
+
+
 def _input(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Input:
     kinds = [k for k in _INPUT_KINDS if k in raw]
     if len(kinds) != 1:
@@ -112,7 +127,8 @@ def _input(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Input:
     if not isinstance(required, bool):
         problems.append(f"input {kind}={list(values)} 'required' must be true or false")
         required = False
-    return Input(kind, values, required, why if isinstance(why, str) else "")
+    document_types = _document_types(raw, kind, rules, problems)
+    return Input(kind, values, required, why if isinstance(why, str) else "", document_types)
 
 
 def _column(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Column:
@@ -140,8 +156,17 @@ def _min_rows(raw: dict[str, Any], table_id: str, problems: list[str]) -> int:
     return value
 
 
+def _text(raw: dict[str, Any], key: str, default: str, problems: list[str]) -> str:
+    """A string field; any other type is a problem, never coerced with str()."""
+    value = raw.get(key, default)
+    if not isinstance(value, str):
+        problems.append(f"table {key} {value!r} must be a string")
+        return ""
+    return value
+
+
 def _table(raw: dict[str, Any], rules: Rules, problems: list[str]) -> TableSpec:
-    table_id = str(raw.get("id", ""))
+    table_id = _text(raw, "id", "", problems)
     if not table_id or table_id in RESERVED_TABLES:
         problems.append(f"table id {table_id!r} is empty or reserved")
     columns = tuple(
@@ -155,7 +180,8 @@ def _table(raw: dict[str, Any], rules: Rules, problems: list[str]) -> TableSpec:
     if not consumers:
         problems.append(f"table {table_id!r} has no consumers; nothing reads it")
     min_rows = _min_rows(raw, table_id, problems)
-    return TableSpec(table_id, str(raw.get("title", table_id)), min_rows, columns, consumers)
+    title = _text(raw, "title", table_id, problems)
+    return TableSpec(table_id, title, min_rows, columns, consumers)
 
 
 def contract_from_dict(data: dict[str, Any], rules: Rules) -> Contract:
```

`rbot/scripts/rbotlib/render.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/render.py
+++ b/rbot/scripts/rbotlib/render.py
@@ -17,6 +17,8 @@ def _input_row(i: Input) -> str:
         label = f"Handoff `{i.values[0]}` ({'required' if i.required else 'optional'})"
     elif i.kind == "sources":
         label = "Sources: " + ", ".join(i.values)
+        if i.document_types:
+            label += " (" + ", ".join(i.document_types) + ")"
     else:
         label = "Run Brief: " + ", ".join(i.values)
     return f"| {label} | {i.why} |"
@@ -46,6 +48,7 @@ def _rules_block(rules: Rules, module_id: str) -> list[str]:
         "",
         "- Front matter keys, one non-empty `key: value` per line: "
         f"{', '.join(rules.front_matter)}; `module_id` is `{module_id}`.",
+        "- `inputs: <Handoff ids comma-separated, or none>`.",
         f"- `qa_status` is one of: {', '.join(rules.qa_status)}.",
         f"- H2 sections, exactly and in order: {', '.join(rules.sections)}.",
         "- Tag each table exactly once, with its `<!-- table: <id> -->` line "
```

`rbot/scripts/rbotlib/validate.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/validate.py
+++ b/rbot/scripts/rbotlib/validate.py
@@ -1,7 +1,8 @@
 """Check a Handoff against its module's contract and the shared rules.
 
 Exit codes follow Deploy V: 0 valid, 2 malformed, 3 blocked (valid but
-qa_status Blocked), 4 identity mismatch.
+qa_status Blocked), 4 identity mismatch. A Handoff over the upstream cap
+(spec section 7, caos MAX_UPSTREAM_HANDOFF_BYTES) is malformed: `too_large`.
 """
 
 from __future__ import annotations
@@ -14,6 +15,7 @@ from rbotlib.handoff import Handoff, HandoffError, Table, cells, markers, parse
 from rbotlib.rules import Rules
 
 EXIT_VALID, EXIT_MALFORMED, EXIT_BLOCKED, EXIT_IDENTITY = 0, 2, 3, 4
+MAX_HANDOFF_BYTES = 98_304
 
 
 @dataclass(frozen=True)
@@ -141,6 +143,9 @@ def check(text: str, contract: Contract, rules: Rules) -> tuple[int, list[Findin
     except HandoffError as exc:
         return EXIT_MALFORMED, [Finding("not_a_handoff", str(exc))]
     findings = _front_matter(h, contract, rules) + _sections(h, rules) + _tags(h, contract)
+    size = len(text.encode("utf-8"))
+    if size > MAX_HANDOFF_BYTES:
+        findings.append(Finding("too_large", f"{size} bytes; the cap is {MAX_HANDOFF_BYTES}"))
     for spec in contract.tables:
         findings += _table(spec, h, rules)
     findings += _citations(h, rules)
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest`
Expected: `126 passed`, coverage ≥ 80%.

- [ ] **Step 6: Run the gate run** (Global Constraints). Expected: every command exits 0; `rbot check` prints `0 problem(s)`.

- [ ] **Step 7: Commit**

```bash
git add rbot tests
git commit -m "rbot: Plan 01 amendments A1, A3, A4 and deferrals M4, M10 (scales, too_large, document_types, inputs line, string-only table ids)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report: the test count and every gate's exit code. `Not verified:` that no Plan 01 contract already used a value the new scales reject (Plan 01 ships no module contract; Plan 04 writes the first).

---

### Task 2: Corpus registry, `rbot corpus` and the corpus marker

**Files:**
- Create: `rbot/scripts/rbotlib/corpus.py`, `tests/corpus/corpus.json`, `tests/corpus/README.md`, `Makefile`
- Modify: `rbot/scripts/rbotlib/cli.py`, `tests/conftest.py`, `pyproject.toml` (the `corpus` marker), `.github/workflows/ci.yml`
- Test: `tests/test_corpus.py`

**Interfaces:**
- Consumes: `rbotlib.rules.RBOT_ROOT`; `rbotlib.cli.main`.
- Produces:
  - `rbotlib.corpus`: `REGISTRY: Path` (`<repo>/tests/corpus/corpus.json`); `ROOTS_ENV = "RBOT_CORPUS_ROOTS"`; `EXTERNAL = "external"`; `MISSING, UNRESOLVED = 1, 2`; `CorpusError(ValueError)`; `CorpusFile(path, sha256, cls, document_type, entity, external: str | None, pages: int | None)`; `Pack(id, root, path, files: tuple[CorpusFile, ...], data: dict[str, Any])` where `data` is the registry entry as written (`issuer`, `period`, `as_of`, `primary`, `portfolios`, `prior_pack`, `expectations`, `pathways`, `traps`); `Registry(location, roots, packs)` with `.pack(id) -> Pack`; `Problem(code, in_repo, message)`; `load_registry(path=REGISTRY) -> Registry`; `repo_root(registry) -> Path`; `resolve_roots(registry, env=os.environ) -> dict[str, Path]`; `locate(pack, f, roots) -> Path | None`; `sha256_file(path) -> str`; `verify(registry, pack, roots) -> list[Problem]`; `materialise(registry, pack, roots, dest) -> Path`; `add_command(sub)`.
  - `rbot corpus list` and `rbot corpus verify [--pack <id>] [--registry <corpus.json>]`: exit 0 ok, 1 a file missing or its sha256 differs, 2 a root unresolved (interfaces spec §9).
  - `tests/conftest.py`: `CORPUS` (the loaded registry), `REQUIRE_ENV = "RBOT_REQUIRE_CORPUS"`, `corpus_gate(problems)` — the §12.3 require rule: `RBOT_REQUIRE_CORPUS=1` fails on any problem, `=synthetic` fails on in-repo files only (CI), otherwise the test skips with the same message.
  - The `corpus` pytest marker (`--strict-markers` is already on); `make corpus`; a CI step running the corpus tests with `RBOT_REQUIRE_CORPUS=synthetic`.
  - `tests/corpus/corpus.json` (`"schema": "rbot-corpus/1"`): the 33 external packs of §12.2 with every file's sha256, class, document type, entity and PDF page count; Task 8 adds the synthetic Primary pack (34).

Registry decisions to keep: a caos pack's `path` is `<id>/documents`, so the pack is exactly the documents an analyst would attach, and every file in that folder is listed (several caos folders now hold more files than `corpus-inventory.md` counted; the registry follows the folder). The hashes are from caos-databricks `5ca9118e` (its `qualification/` last changed in `8fd9652b`) and `TEST-Issuer Data` on 2026-10-11. `tid-vmo2-fy2025` and `tid-vmo2-2026q1` list subsets of the `virgin` folder; a pack is always exactly its listed files, because tests copy the listed files into a temporary Source Pack. The CCL Fitch rating PDF has text on every page, so `ccl-fy2025-lite-full-credit-screen` carries no `image_read_only` trap. The `tid-vmo2-2026q1` Prior Case Report is produced by a proxy run in Plan 11; until then the pack names `prior_pack` only.

- [ ] **Step 1: Write the failing tests**

`tests/test_corpus.py` — create:

```python
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

from conftest import CORPUS, REQUIRE_ENV, corpus_gate
from rbotlib.cli import main
from rbotlib.corpus import (
    MISSING,
    ROOTS_ENV,
    UNRESOLVED,
    CorpusError,
    Problem,
    load_registry,
    materialise,
    resolve_roots,
    verify,
)
from rbotlib.rules import Rules

PATHWAYS = set(
    "FULL_CREDIT_ASSESSMENT RELATIVE_VALUE COVENANT_REFINANCING DISTRESSED_RESTRUCTURING"
    " EARNINGS_UPDATE PORTFOLIO_DECISION".split()
)
TRAPS = set(
    "entity_mismatch period_mismatch price_talk_not_market_level image_read_only"
    " missing_document_type prior_case_present duplicate_source".split()
)


def _registry(tmp_path: Path, files: dict[str, bytes], listed: dict[str, str]) -> Path:
    """A one-pack registry at <tmp>/repo/tests/corpus/corpus.json over <tmp>/ext/pack/."""
    folder = tmp_path / "ext" / "pack"
    folder.mkdir(parents=True)
    for name, data in files.items():
        (folder / name).write_bytes(data)
    entry = {"class": "issuer", "document_type": "Other", "entity": "TEST"}
    pack: dict[str, Any] = {"id": "p1", "root": "ext", "path": "pack", "period": "FY2025"}
    pack |= {"issuer": {"id": "TEST", "name": "Test plc"}, "pathways": []}
    pack["files"] = [{"path": n, "sha256": d, **entry} for n, d in listed.items()]
    registry = tmp_path / "repo" / "tests" / "corpus" / "corpus.json"
    registry.parent.mkdir(parents=True)
    roots = {"ext": "external", "synthetic": "tests/corpus/synthetic"}
    body = {"schema": "rbot-corpus/1", "roots": roots, "packs": [pack]}
    registry.write_text(json.dumps(body), encoding="utf-8")
    return registry


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_the_registry_is_well_formed(rules: Rules) -> None:
    ids = [p.id for p in CORPUS.packs]
    assert len(ids) == len(set(ids)) == 33
    for pack in CORPUS.packs:
        assert pack.root in CORPUS.roots
        assert {w["id"] for w in pack.data["pathways"]} <= PATHWAYS
        assert {w["fit"] for w in pack.data["pathways"]} <= {"primary", "exercises", "partial"}
        assert {t["kind"] for t in pack.data["traps"]} <= TRAPS
        assert pack.data["prior_pack"] is None or pack.data["prior_pack"] in ids
        names = [f.path for f in pack.files]
        assert len(names) == len(set(names)), pack.id
        for f in pack.files:
            assert re.fullmatch(r"[0-9a-f]{64}", f.sha256), f.path
            assert f.cls in rules.source_classes, f.path
            assert f.document_type in rules.scales["document_type"], f.path
            assert (f.pages is not None) == f.path.lower().endswith(".pdf"), f.path


def test_unresolved_external_roots_are_named(tmp_path: Path) -> None:
    data = b"filing text\n"
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    roots = resolve_roots(registry, {})
    assert "ext" not in roots
    problems = verify(registry, registry.pack("p1"), roots)
    assert [(p.code, p.in_repo) for p in problems] == [(UNRESOLVED, False)]
    assert "root 'ext' is unresolved; set RBOT_CORPUS_ROOTS" in problems[0].message


def test_missing_and_changed_files_are_named(tmp_path: Path) -> None:
    data = b"filing text\n"
    listed = {"a.txt": _sha(b"other bytes"), "b.txt": _sha(data)}
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, listed))
    roots = resolve_roots(registry, {ROOTS_ENV: json.dumps({"ext": str(tmp_path / "ext")})})
    messages = [(p.code, p.message) for p in verify(registry, registry.pack("p1"), roots)]
    assert messages[0] == (MISSING, "p1: a.txt: sha256 differs")
    assert messages[1][0] == MISSING and messages[1][1].startswith("p1: b.txt: missing at ")


def test_materialise_copies_verified_files_only(tmp_path: Path) -> None:
    data = b"filing text\n"
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    roots = resolve_roots(registry, {ROOTS_ENV: json.dumps({"ext": str(tmp_path / "ext")})})
    pack = materialise(registry, registry.pack("p1"), roots, tmp_path / "copy")
    assert (pack / "a.txt").read_bytes() == data
    with pytest.raises(CorpusError, match="root 'ext' is unresolved"):
        materialise(registry, registry.pack("p1"), {}, tmp_path / "copy2")


def test_bad_registries_and_environments_are_refused(tmp_path: Path) -> None:
    path = _registry(tmp_path, {}, {})
    with pytest.raises(CorpusError, match="not a JSON object"):
        resolve_roots(load_registry(path), {ROOTS_ENV: "[1, 2]"})
    with pytest.raises(CorpusError, match="not a JSON object"):
        resolve_roots(load_registry(path), {ROOTS_ENV: "{nope"})
    with pytest.raises(CorpusError, match="no pack 'p9'"):
        load_registry(path).pack("p9")
    path.write_text(json.dumps({"schema": "other/1"}), encoding="utf-8")
    with pytest.raises(CorpusError, match="expected 'rbot-corpus/1'"):
        load_registry(path)


def test_corpus_command_lists_and_verifies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    data = b"filing text\n"
    registry = str(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    assert main(["corpus", "list", "--registry", registry]) == 0
    assert capsys.readouterr().out.startswith("p1  ext:pack  TEST FY2025  1 file(s)")
    monkeypatch.delenv(ROOTS_ENV, raising=False)
    assert main(["corpus", "verify", "--registry", registry]) == UNRESOLVED
    assert capsys.readouterr().out.endswith("exit 2\n")
    monkeypatch.setenv(ROOTS_ENV, json.dumps({"ext": str(tmp_path / "ext")}))
    assert main(["corpus", "verify", "--pack", "p1", "--registry", registry]) == 0
    assert capsys.readouterr().out == "ok p1 (1 files)\nexit 0\n"
    (tmp_path / "ext" / "pack" / "a.txt").write_bytes(b"edited\n")
    assert main(["corpus", "verify", "--registry", registry]) == MISSING


@pytest.mark.parametrize(
    ("level", "in_repo", "outcome"),
    [
        ("1", False, "fail"),
        ("synthetic", True, "fail"),
        ("synthetic", False, "skip"),
        ("", True, "skip"),
    ],
)
def test_the_require_rule(
    monkeypatch: pytest.MonkeyPatch, level: str, in_repo: bool, outcome: str
) -> None:
    monkeypatch.setenv(REQUIRE_ENV, level)
    problems = [Problem(MISSING, in_repo, "p1: a.txt: sha256 differs")]
    expected = pytest.fail.Exception if outcome == "fail" else pytest.skip.Exception
    with pytest.raises(expected, match=re.escape("p1: a.txt: sha256 differs")):
        corpus_gate(problems)
    corpus_gate([])


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_corpus_hashes_match(pack_id: str) -> None:
    pack = CORPUS.pack(pack_id)
    corpus_gate(verify(CORPUS, pack, resolve_roots(CORPUS)))
```

`tests/conftest.py` — patch:

```diff
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -1,8 +1,9 @@
-"""Shared fixtures: the real rules, the example contracts and a throwaway RBOT tree."""
+"""Shared fixtures: the real rules, the example contracts, a throwaway RBOT tree and the corpus."""
 
 from __future__ import annotations
 
 import json
+import os
 import shutil
 from pathlib import Path
 from typing import Any
@@ -10,6 +11,7 @@ from typing import Any
 import pytest
 
 from rbotlib.contract import contract_from_dict
+from rbotlib.corpus import Problem, load_registry
 from rbotlib.render import render_module
 from rbotlib.rules import RBOT_ROOT, Rules, load_rules
 
@@ -66,3 +68,23 @@ def tree(tmp_path: Path, rules: Rules) -> Path:
     write_module(tmp_path, fixture_json("contract_cp_x.json"), rules)
     write_module(tmp_path, fixture_json("contract_cp_y.json"), rules)
     return tmp_path
+
+
+CORPUS = load_registry()
+REQUIRE_ENV = "RBOT_REQUIRE_CORPUS"
+
+
+def corpus_gate(problems: list[Problem]) -> None:
+    """Fail or skip a corpus test whose files are not usable (interfaces spec section 12.3).
+
+    RBOT_REQUIRE_CORPUS=1 fails on any problem (the owner's machine); =synthetic fails
+    only on in-repo files and skips the external ones (CI); otherwise the test skips.
+    The message names the unresolved root or the mismatched file either way.
+    """
+    if not problems:
+        return
+    message = "; ".join(p.message for p in problems)
+    level = os.environ.get(REQUIRE_ENV, "")
+    if level == "1" or (level == "synthetic" and any(p.in_repo for p in problems)):
+        pytest.fail(message)
+    pytest.skip(message)
```

`pyproject.toml` — patch:

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -38,6 +38,9 @@ exclude = ["^reference/"]
 testpaths = ["tests"]
 pythonpath = ["rbot/scripts", "scripts", "tests"]
 addopts = "-q --strict-markers --cov --cov-branch --cov-report=term-missing:skip-covered --cov-fail-under=80"
+markers = [
+    "corpus: reads the local issuer corpus (tests/corpus/corpus.json, interfaces spec section 12.3)",
+]
 
 [tool.coverage.run]
 branch = true
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest --no-cov`
Expected: FAIL — `ImportError while loading conftest`: `ModuleNotFoundError: No module named 'rbotlib.corpus'`.

- [ ] **Step 3: Write the registry**

`tests/corpus/corpus.json` — create:

```json
{
  "schema": "rbot-corpus/1",
  "roots": {"caos-qualification": "external", "test-issuer-data": "external", "synthetic": "tests/corpus/synthetic"},
  "packs": [
    {"id": "czr-2026q2-full-credit-assessment", "root": "caos-qualification", "path": "czr-2026q2-full-credit-assessment/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": ["TEST_CLO_I"], "prior_pack": null, "expectations": null, "pathways": [{"id": "FULL_CREDIT_ASSESSMENT", "depth": "full", "fit": "exercises"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no Sector RV Workbook: CP-3 loan RV limited"}], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Fifth_Amendment.txt", "sha256": "7f2b5c777dc3347938a007eaea63a623b299a1188dbcfbe8980d389a0bcfc5b3", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Fourth_Amendment.txt", "sha256": "32f91de6ef3ff93d9924eb8d4e3dc4734d28b68ed1da0f816a085ffdcb085c95", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement.txt", "sha256": "e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement_8K.txt", "sha256": "6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Press_Release.txt", "sha256": "4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt", "sha256": "256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"},
      {"path": "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt", "sha256": "e2490912d9cc688135e15732e0fcf4aafd715e91e4d580edd577483535507bab", "class": "portfolio", "document_type": "Portfolio positions", "entity": "FHSUHY"},
      {"path": "FHSUHY_Prospectus_and_SAI_2026-05-26.txt", "sha256": "10455d54958421c56b4902f2fa41bfc08873bb9d16ee9fb22ab31ded215846ea", "class": "portfolio", "document_type": "Portfolio limits", "entity": "FHSUHY"},
      {"path": "MGM_FINRA_TRACE_552953CK5_2026-10-02.txt", "sha256": "e17cea1bb90debdeb8c1fea9c352132b57ae9b27ee0d3225fb67c6466d7d0e4a", "class": "market", "document_type": "Market levels export", "entity": "MGM"},
      {"path": "MGM_Q2_2026_Earnings_Release.txt", "sha256": "795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb", "class": "market", "document_type": "Earnings release", "entity": "MGM"},
      {"path": "PENN_FINRA_TRACE_707569AV1_2026-10-02.txt", "sha256": "666c0f36ace32336dffbcff324eaec5b4657edade407bb0b8a0e8d8fb405de6d", "class": "market", "document_type": "Market levels export", "entity": "PENN"},
      {"path": "PENN_Q2_2026_Earnings_Release.txt", "sha256": "4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c", "class": "market", "document_type": "Earnings release", "entity": "PENN"},
      {"path": "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt", "sha256": "864ee90ab21372bcf89c8b27e02cd5d691d9095a64d507c7f656d5963cfe3207", "class": "portfolio", "document_type": "Portfolio limits", "entity": "TEST_CLO_I"}]},
    {"id": "czr-2026q2", "root": "caos-qualification", "path": "czr-2026q2/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CZR_2026_Merger_Agreement.txt", "sha256": "e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"}]},
    {"id": "czr-2026q2-earnings-update", "root": "caos-qualification", "path": "czr-2026q2-earnings-update/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "full", "fit": "primary"}], "traps": [], "files": [
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"}]},
    {"id": "czr-2026q2-covenant-refinancing", "root": "caos-qualification", "path": "czr-2026q2-covenant-refinancing/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "full", "fit": "primary"}], "traps": [], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Fifth_Amendment.txt", "sha256": "7f2b5c777dc3347938a007eaea63a623b299a1188dbcfbe8980d389a0bcfc5b3", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Fourth_Amendment.txt", "sha256": "32f91de6ef3ff93d9924eb8d4e3dc4734d28b68ed1da0f816a085ffdcb085c95", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement.txt", "sha256": "e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement_8K.txt", "sha256": "6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Press_Release.txt", "sha256": "4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"}]},
    {"id": "czr-2026q2-lite-covenant-refinancing", "root": "caos-qualification", "path": "czr-2026q2-lite-covenant-refinancing/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "quick", "fit": "primary"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no 10-K (Annual report)"}], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Fifth_Amendment.txt", "sha256": "7f2b5c777dc3347938a007eaea63a623b299a1188dbcfbe8980d389a0bcfc5b3", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Fourth_Amendment.txt", "sha256": "32f91de6ef3ff93d9924eb8d4e3dc4734d28b68ed1da0f816a085ffdcb085c95", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement.txt", "sha256": "e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement_8K.txt", "sha256": "6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"}]},
    {"id": "czr-2026q2-liquidity", "root": "caos-qualification", "path": "czr-2026q2-liquidity/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "quick", "fit": "partial", "note": "block 8 (liquidity)"}], "traps": [], "files": [
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement.txt", "sha256": "e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"}]},
    {"id": "czr-2026q2-lite-full-credit-screen", "root": "caos-qualification", "path": "czr-2026q2-lite-full-credit-screen/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "FULL_CREDIT_ASSESSMENT", "depth": "quick", "fit": "primary"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no 10-K (Annual report)"}], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Agreement_8K.txt", "sha256": "6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_2026_Merger_Press_Release.txt", "sha256": "4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b", "class": "issuer", "document_type": "Other", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt", "sha256": "256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"},
      {"path": "MGM_Q2_2026_Earnings_Release.txt", "sha256": "795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb", "class": "market", "document_type": "Earnings release", "entity": "MGM"},
      {"path": "PENN_Q2_2026_Earnings_Release.txt", "sha256": "4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c", "class": "market", "document_type": "Earnings release", "entity": "PENN"}]},
    {"id": "czr-2026q2-lite-portfolio", "root": "caos-qualification", "path": "czr-2026q2-lite-portfolio/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": ["TEST_CLO_I"], "prior_pack": null, "expectations": null, "pathways": [{"id": "PORTFOLIO_DECISION", "depth": "quick", "fit": "primary"}], "traps": [], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"},
      {"path": "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt", "sha256": "e2490912d9cc688135e15732e0fcf4aafd715e91e4d580edd577483535507bab", "class": "portfolio", "document_type": "Portfolio positions", "entity": "FHSUHY"},
      {"path": "FHSUHY_Prospectus_and_SAI_2026-05-26.txt", "sha256": "10455d54958421c56b4902f2fa41bfc08873bb9d16ee9fb22ab31ded215846ea", "class": "portfolio", "document_type": "Portfolio limits", "entity": "FHSUHY"},
      {"path": "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt", "sha256": "864ee90ab21372bcf89c8b27e02cd5d691d9095a64d507c7f656d5963cfe3207", "class": "portfolio", "document_type": "Portfolio limits", "entity": "TEST_CLO_I"}]},
    {"id": "czr-2026q2-lite-relative-value", "root": "caos-qualification", "path": "czr-2026q2-lite-relative-value/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "RELATIVE_VALUE", "depth": "quick", "fit": "primary"}], "traps": [], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt", "sha256": "256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"},
      {"path": "MGM_FINRA_TRACE_552953CK5_2026-10-02.txt", "sha256": "e17cea1bb90debdeb8c1fea9c352132b57ae9b27ee0d3225fb67c6466d7d0e4a", "class": "market", "document_type": "Market levels export", "entity": "MGM"},
      {"path": "MGM_Q2_2026_Earnings_Release.txt", "sha256": "795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb", "class": "market", "document_type": "Earnings release", "entity": "MGM"},
      {"path": "PENN_FINRA_TRACE_707569AV1_2026-10-02.txt", "sha256": "666c0f36ace32336dffbcff324eaec5b4657edade407bb0b8a0e8d8fb405de6d", "class": "market", "document_type": "Market levels export", "entity": "PENN"},
      {"path": "PENN_Q2_2026_Earnings_Release.txt", "sha256": "4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c", "class": "market", "document_type": "Earnings release", "entity": "PENN"}]},
    {"id": "czr-2026q2-portfolio", "root": "caos-qualification", "path": "czr-2026q2-portfolio/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": ["TEST_CLO_I"], "prior_pack": null, "expectations": null, "pathways": [{"id": "PORTFOLIO_DECISION", "depth": "full", "fit": "primary"}], "traps": [], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt", "sha256": "256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt", "sha256": "e2490912d9cc688135e15732e0fcf4aafd715e91e4d580edd577483535507bab", "class": "portfolio", "document_type": "Portfolio positions", "entity": "FHSUHY"},
      {"path": "FHSUHY_Prospectus_and_SAI_2026-05-26.txt", "sha256": "10455d54958421c56b4902f2fa41bfc08873bb9d16ee9fb22ab31ded215846ea", "class": "portfolio", "document_type": "Portfolio limits", "entity": "FHSUHY"},
      {"path": "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt", "sha256": "864ee90ab21372bcf89c8b27e02cd5d691d9095a64d507c7f656d5963cfe3207", "class": "portfolio", "document_type": "Portfolio limits", "entity": "TEST_CLO_I"}]},
    {"id": "czr-2026q2-relative-value", "root": "caos-qualification", "path": "czr-2026q2-relative-value/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "RELATIVE_VALUE", "depth": "full", "fit": "primary"}], "traps": [], "files": [
      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt", "sha256": "256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24", "class": "market", "document_type": "Market levels export", "entity": "CZR"},
      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR"},
      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR"},
      {"path": "MGM_FINRA_TRACE_552953CK5_2026-10-02.txt", "sha256": "e17cea1bb90debdeb8c1fea9c352132b57ae9b27ee0d3225fb67c6466d7d0e4a", "class": "market", "document_type": "Market levels export", "entity": "MGM"},
      {"path": "MGM_Q2_2026_Earnings_Release.txt", "sha256": "795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb", "class": "market", "document_type": "Earnings release", "entity": "MGM"},
      {"path": "PENN_FINRA_TRACE_707569AV1_2026-10-02.txt", "sha256": "666c0f36ace32336dffbcff324eaec5b4657edade407bb0b8a0e8d8fb405de6d", "class": "market", "document_type": "Market levels export", "entity": "PENN"},
      {"path": "PENN_Q2_2026_Earnings_Release.txt", "sha256": "4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c", "class": "market", "document_type": "Earnings release", "entity": "PENN"}]},
    {"id": "ccl-fy2025", "root": "caos-qualification", "path": "ccl-fy2025/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-07-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-covenant-refinancing", "root": "caos-qualification", "path": "ccl-fy2025-covenant-refinancing/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "full", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_2025_575_Notes_2030_Indenture.txt", "sha256": "2340549fd4f215dfeadada890658195a30456d68031f73387dc9c98b6ba498d1", "class": "issuer", "document_type": "Indenture", "entity": "CCL"},
      {"path": "CCL_2025_Fitch_Rating_Action.pdf", "sha256": "33863f60a0f6c94529538b535076e0d287f24183746dbd202b2b86c434d879ae", "class": "issuer", "document_type": "Rating report", "entity": "CCL", "pages": 19},
      {"path": "CCL_2025_Revolving_Credit_Agreement.txt", "sha256": "0f5a7510e20cbf7182108e4a48ea1c8e7e85800d06205518f79ec049da169c49", "class": "issuer", "document_type": "Credit agreement", "entity": "CCL"},
      {"path": "CCL_FINRA_TRACE_143658BY7_2026-09-19.txt", "sha256": "28f9289818978608ad48ed744f0483c8d3385d84cd7980402b5366545e00ae36", "class": "market", "document_type": "Market levels export", "entity": "CCL"},
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-earnings-update", "root": "caos-qualification", "path": "ccl-fy2025-earnings-update/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "full", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-full-relative-value", "root": "caos-qualification", "path": "ccl-fy2025-full-relative-value/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "RELATIVE_VALUE", "depth": "full", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_2025_575_Notes_2030_Indenture.txt", "sha256": "2340549fd4f215dfeadada890658195a30456d68031f73387dc9c98b6ba498d1", "class": "issuer", "document_type": "Indenture", "entity": "CCL"},
      {"path": "CCL_2025_Revolving_Credit_Agreement.txt", "sha256": "0f5a7510e20cbf7182108e4a48ea1c8e7e85800d06205518f79ec049da169c49", "class": "issuer", "document_type": "Credit agreement", "entity": "CCL"},
      {"path": "CCL_FINRA_TRACE_143658BY7_2026-09-19.txt", "sha256": "28f9289818978608ad48ed744f0483c8d3385d84cd7980402b5366545e00ae36", "class": "market", "document_type": "Market levels export", "entity": "CCL"},
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"},
      {"path": "NCLH_Q4_2025_Earnings_Release.txt", "sha256": "dd9a0eb7211c111b8180ea10f95416066c3e714a7390e0424799b6f522981b88", "class": "market", "document_type": "Earnings release", "entity": "NCLH"},
      {"path": "RCL_Q4_2025_Earnings_Release.txt", "sha256": "43005bdbd3a05fd62ef4107dd7dd4e97977c135d1f5902b68d45996cb6e2c592", "class": "market", "document_type": "Earnings release", "entity": "RCL"}]},
    {"id": "ccl-fy2025-liquidity", "root": "caos-qualification", "path": "ccl-fy2025-liquidity/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "quick", "fit": "partial", "note": "block 8 (liquidity)"}], "traps": [], "files": [
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-lite-covenant-refinancing", "root": "caos-qualification", "path": "ccl-fy2025-lite-covenant-refinancing/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_2025_575_Notes_2030_Indenture.txt", "sha256": "2340549fd4f215dfeadada890658195a30456d68031f73387dc9c98b6ba498d1", "class": "issuer", "document_type": "Indenture", "entity": "CCL"},
      {"path": "CCL_2025_Revolving_Credit_Agreement.txt", "sha256": "0f5a7510e20cbf7182108e4a48ea1c8e7e85800d06205518f79ec049da169c49", "class": "issuer", "document_type": "Credit agreement", "entity": "CCL"},
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-lite-full-credit-screen", "root": "caos-qualification", "path": "ccl-fy2025-lite-full-credit-screen/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "FULL_CREDIT_ASSESSMENT", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_2025_575_Notes_2030_Indenture.txt", "sha256": "2340549fd4f215dfeadada890658195a30456d68031f73387dc9c98b6ba498d1", "class": "issuer", "document_type": "Indenture", "entity": "CCL"},
      {"path": "CCL_2025_Fitch_Rating_Action.pdf", "sha256": "33863f60a0f6c94529538b535076e0d287f24183746dbd202b2b86c434d879ae", "class": "issuer", "document_type": "Rating report", "entity": "CCL", "pages": 19},
      {"path": "CCL_2025_Revolving_Credit_Agreement.txt", "sha256": "0f5a7510e20cbf7182108e4a48ea1c8e7e85800d06205518f79ec049da169c49", "class": "issuer", "document_type": "Credit agreement", "entity": "CCL"},
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"},
      {"path": "NCLH_Q4_2025_Earnings_Release.txt", "sha256": "dd9a0eb7211c111b8180ea10f95416066c3e714a7390e0424799b6f522981b88", "class": "market", "document_type": "Earnings release", "entity": "NCLH"},
      {"path": "RCL_Q4_2025_Earnings_Release.txt", "sha256": "43005bdbd3a05fd62ef4107dd7dd4e97977c135d1f5902b68d45996cb6e2c592", "class": "market", "document_type": "Earnings release", "entity": "RCL"}]},
    {"id": "ccl-fy2025-market-dislocation", "root": "caos-qualification", "path": "ccl-fy2025-market-dislocation/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "RELATIVE_VALUE", "depth": "quick", "fit": "partial", "note": "blocks 6-7"}], "traps": [], "files": [
      {"path": "CCL_FINRA_TRACE_143658BY7_2026-09-19.txt", "sha256": "28f9289818978608ad48ed744f0483c8d3385d84cd7980402b5366545e00ae36", "class": "market", "document_type": "Market levels export", "entity": "CCL"},
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-portfolio", "root": "caos-qualification", "path": "ccl-fy2025-portfolio/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-17", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "PORTFOLIO_DECISION", "depth": "quick", "fit": "partial", "note": "graded Blocked: no Portfolio Context"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no Portfolio positions file"}], "files": [
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"}]},
    {"id": "ccl-fy2025-relative-value", "root": "caos-qualification", "path": "ccl-fy2025-relative-value/documents", "issuer": {"id": "CCL", "name": "Carnival Corporation & plc"}, "period": "FY2025", "as_of": "2026-09-18", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "RELATIVE_VALUE", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "CCL_FY2025_10K.txt", "sha256": "8fa7fceda34be50b3b9b5406e0c9269b5269870d1cd8c2bdafb682755a1c88e6", "class": "issuer", "document_type": "Annual report", "entity": "CCL"},
      {"path": "NCLH_Q4_2025_Earnings_Release.txt", "sha256": "dd9a0eb7211c111b8180ea10f95416066c3e714a7390e0424799b6f522981b88", "class": "market", "document_type": "Earnings release", "entity": "NCLH"},
      {"path": "RCL_Q4_2025_Earnings_Release.txt", "sha256": "43005bdbd3a05fd62ef4107dd7dd4e97977c135d1f5902b68d45996cb6e2c592", "class": "market", "document_type": "Earnings release", "entity": "RCL"}]},
    {"id": "ba-fy2025", "root": "caos-qualification", "path": "ba-fy2025/documents", "issuer": {"id": "BA", "name": "The Boeing Company"}, "period": "FY2025", "as_of": "2026-07-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "BA_FY2025_10K.txt", "sha256": "0446b367110afddcc0d66bc531d70324091b5bd1a96be56b7494ccdb7472f719", "class": "issuer", "document_type": "Annual report", "entity": "BA"}]},
    {"id": "f-fy2025", "root": "caos-qualification", "path": "f-fy2025/documents", "issuer": {"id": "F", "name": "Ford Motor Company"}, "period": "FY2025", "as_of": "2026-07-19", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "F_FY2025_10K.txt", "sha256": "97a38bc17e505cd1c000aa833d55e4dcfdbaedc5a75ce03a39474b9467fe4b43", "class": "issuer", "document_type": "Annual report", "entity": "F"}]},
    {"id": "save-2024-distressed-restructuring", "root": "caos-qualification", "path": "save-2024-distressed-restructuring/documents", "issuer": {"id": "SAVE", "name": "Spirit Airlines, Inc."}, "period": "FY2024", "as_of": "2024-11-18", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "DISTRESSED_RESTRUCTURING", "depth": "full", "fit": "primary"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no financial statements: CP-1 Restricted"}], "files": [
      {"path": "SAVE_2024_Chapter_11_8K.txt", "sha256": "9d3c7ba8d1632130c4cca089cf495a15bbfb54699fb7bc657d3fbf53c8af6a5d", "class": "issuer", "document_type": "Other", "entity": "SAVE"},
      {"path": "SAVE_2024_RSA_with_Chapter_11_Plan.txt", "sha256": "6b40ff57e904068b28ede10e9b9300fe545feaa0382107ca9303b408cddfb8b5", "class": "issuer", "document_type": "Other", "entity": "SAVE"}]},
    {"id": "save-2024-lite-distressed-restructuring", "root": "caos-qualification", "path": "save-2024-lite-distressed-restructuring/documents", "issuer": {"id": "SAVE", "name": "Spirit Airlines, Inc."}, "period": "FY2024", "as_of": "2024-11-18", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "DISTRESSED_RESTRUCTURING", "depth": "quick", "fit": "primary"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no financial statements: CP-1 Restricted"}], "files": [
      {"path": "SAVE_2024_Chapter_11_8K.txt", "sha256": "9d3c7ba8d1632130c4cca089cf495a15bbfb54699fb7bc657d3fbf53c8af6a5d", "class": "issuer", "document_type": "Other", "entity": "SAVE"},
      {"path": "SAVE_2024_RSA_with_Chapter_11_Plan.txt", "sha256": "6b40ff57e904068b28ede10e9b9300fe545feaa0382107ca9303b408cddfb8b5", "class": "issuer", "document_type": "Other", "entity": "SAVE"}]},
    {"id": "vmo2-fy2025", "root": "caos-qualification", "path": "vmo2-fy2025/documents", "issuer": {"id": "VMO2", "name": "Virgin Media O2"}, "period": "FY2025", "as_of": "2026-09-15", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "exercises"}], "traps": [], "files": [
      {"path": "Virgin-Media-O2-Q3-2025-Earnings-Release.pdf", "sha256": "505bf1a0f4181c9cdffeeac7e6af3253d1883788e9cd1a81e65952e008aa17a1", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 13},
      {"path": "Virgin-Media-O2-Q4-2025-Earnings-Release.pdf", "sha256": "66055bbb8d27721d07a5e8cb834c9b96a256ada45a0812ea4fb2e7202ee4f64d", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 18}]},
    {"id": "vmo2-fy2025-deep-research", "root": "caos-qualification", "path": "vmo2-fy2025-deep-research/documents", "issuer": {"id": "VMO2", "name": "Virgin Media O2"}, "period": "FY2025", "as_of": "2026-09-18", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "partial", "note": "Deep Research questions listed, skipped at Quick"}], "traps": [], "files": [
      {"path": "Virgin-Media-O2-Q3-2025-Earnings-Release.pdf", "sha256": "505bf1a0f4181c9cdffeeac7e6af3253d1883788e9cd1a81e65952e008aa17a1", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 13},
      {"path": "Virgin-Media-O2-Q4-2025-Earnings-Release.pdf", "sha256": "66055bbb8d27721d07a5e8cb834c9b96a256ada45a0812ea4fb2e7202ee4f64d", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 18}]},
    {"id": "vmo2-fy2025-full-deep-research", "root": "caos-qualification", "path": "vmo2-fy2025-full-deep-research/documents", "issuer": {"id": "VMO2", "name": "Virgin Media O2"}, "period": "FY2025", "as_of": "2026-09-18", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "full", "fit": "exercises", "note": "Deep Research primary"}], "traps": [], "files": [
      {"path": "Virgin-Media-O2-Q3-2025-Earnings-Release.pdf", "sha256": "505bf1a0f4181c9cdffeeac7e6af3253d1883788e9cd1a81e65952e008aa17a1", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 13},
      {"path": "Virgin-Media-O2-Q4-2025-Earnings-Release.pdf", "sha256": "66055bbb8d27721d07a5e8cb834c9b96a256ada45a0812ea4fb2e7202ee4f64d", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 18}]},
    {"id": "vmo2-fy2025-portfolio", "root": "caos-qualification", "path": "vmo2-fy2025-portfolio/documents", "issuer": {"id": "VMO2", "name": "Virgin Media O2"}, "period": "FY2025", "as_of": "2026-09-17", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "PORTFOLIO_DECISION", "depth": "quick", "fit": "partial", "note": "graded Blocked: no Portfolio Context"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no Portfolio positions file"}], "files": [
      {"path": "Virgin-Media-O2-Q3-2025-Earnings-Release.pdf", "sha256": "505bf1a0f4181c9cdffeeac7e6af3253d1883788e9cd1a81e65952e008aa17a1", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 13},
      {"path": "Virgin-Media-O2-Q4-2025-Earnings-Release.pdf", "sha256": "66055bbb8d27721d07a5e8cb834c9b96a256ada45a0812ea4fb2e7202ee4f64d", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 18}]},
    {"id": "tid-ford", "root": "test-issuer-data", "path": "ford", "issuer": {"id": "F", "name": "Ford Motor Company"}, "period": "FY2025", "as_of": "2025-07-28", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "full", "fit": "partial", "note": "blocks 3, 5-7; CP-1 Restricted"}], "traps": [{"kind": "entity_mismatch", "file": "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf", "expect": "prepared/index.json entities name SIX FLAGS for this file"}, {"kind": "period_mismatch", "file": "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf", "expect": "fiscal year ended 2022-01-02, years before the Ford credit agreement"}], "files": [
      {"path": "ford ca.pdf", "sha256": "a30ef8d72493877ce246085f132882dd7b5c6c932ee13a304ae8e4aaebd20e9d", "class": "issuer", "document_type": "Credit agreement", "entity": "F", "pages": 63},
      {"path": "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf", "sha256": "cde003b14559c27e82b30349a127817f9015f8f829f817b7040fdcf68eccda36", "class": "issuer", "document_type": "Annual report", "entity": "SIX", "pages": 170}]},
    {"id": "tid-six-flags", "root": "test-issuer-data", "path": "six flags", "issuer": {"id": "SIX", "name": "Six Flags Entertainment Corporation"}, "period": "FY2025", "as_of": "2025-12-31", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "COVENANT_REFINANCING", "depth": "full", "fit": "partial", "note": "CP-1 Restricted"}], "traps": [{"kind": "entity_mismatch", "file": "f-20251231.pdf", "expect": "prepared/index.json entities name Ford for this file"}], "files": [
      {"path": "Exhibit 10-Credit Agreement.pdf", "sha256": "1ee3928871199803c53286605e09f299dfc96f0373ff0c40b4b340c6d70e7287", "class": "issuer", "document_type": "Credit agreement", "entity": "SIX", "pages": 119},
      {"path": "f-20251231.pdf", "sha256": "e2868ea611b297c26f5a27f92a1a0c2d0c12fcffbd4e0a3d5c3e3f66031f66e1", "class": "issuer", "document_type": "Annual report", "entity": "F", "pages": 181}]},
    {"id": "tid-vmo2-fy2025", "root": "test-issuer-data", "path": "virgin", "issuer": {"id": "VMO2", "name": "Virgin Media O2"}, "period": "FY2025", "as_of": "2026-03-01", "primary": false, "portfolios": [], "prior_pack": null, "expectations": null, "pathways": [{"id": "FULL_CREDIT_ASSESSMENT", "depth": "full", "fit": "exercises"}, {"id": "EARNINGS_UPDATE", "depth": "full", "fit": "exercises"}], "traps": [{"kind": "duplicate_source", "file": "VMO2-IFRS-Quarterly-Bond-Report-Q3-2025.pdf", "expect": "the Q3 2025 bond report and Q3 2025 earnings release report the same quarter"}], "files": [
      {"path": "VMED-O2-UK-Limited-2025-Annual-Report-and-Consolidated-Financial-Statements.pdf", "sha256": "9a01f61f83e8c0c1aac943fb08df8fbb6b94d5415521818acc78dd59872b2b47", "class": "issuer", "document_type": "Annual report", "entity": "VMO2", "pages": 179},
      {"path": "VMO2-IFRS-Quarterly-Bond-Report-Q1-2025.pdf", "sha256": "6ab6655e85b1e29aeefb6183b00927a93086f7d8463bb94a28252140cdac9787", "class": "issuer", "document_type": "Bond report", "entity": "VMO2", "pages": 46},
      {"path": "VMO2-IFRS-Quarterly-Bond-Report-Q2-2025.pdf", "sha256": "5a2498ab849a78233810a6ac183db5f914a5183b2b86d1dde2a58d8809b34dd4", "class": "issuer", "document_type": "Bond report", "entity": "VMO2", "pages": 48},
      {"path": "VMO2-IFRS-Quarterly-Bond-Report-Q3-2025.pdf", "sha256": "dc1d977f3f6b98e84a93af0c6f6b3bccb32b9a9e2e178b37846871e4b06ac9e9", "class": "issuer", "document_type": "Bond report", "entity": "VMO2", "pages": 52},
      {"path": "Virgin-Media-O2-Q1-2025-Earnings-Release.pdf", "sha256": "9bf6e0922433ec6231f5212b028616acd1537785bfd17f6d622e835f76e98d86", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 12},
      {"path": "Virgin-Media-O2-Q2-2025-Earnings-Release.pdf", "sha256": "ef918e8c90a3400dd596da29bbf0da8fec6f6bfa1dd2cbe66192943e087a9f4d", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 12},
      {"path": "Virgin-Media-O2-Q3-2025-Earnings-Release.pdf", "sha256": "505bf1a0f4181c9cdffeeac7e6af3253d1883788e9cd1a81e65952e008aa17a1", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 13},
      {"path": "Virgin-Media-O2-Q4-2025-Earnings-Release.pdf", "sha256": "66055bbb8d27721d07a5e8cb834c9b96a256ada45a0812ea4fb2e7202ee4f64d", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 18}]},
    {"id": "tid-vmo2-2026q1", "root": "test-issuer-data", "path": "virgin", "issuer": {"id": "VMO2", "name": "Virgin Media O2"}, "period": "2026Q1", "as_of": "2026-05-15", "primary": false, "portfolios": [], "prior_pack": "tid-vmo2-fy2025", "expectations": null, "pathways": [{"id": "EARNINGS_UPDATE", "depth": "full", "fit": "primary", "note": "Prior Case"}], "traps": [{"kind": "prior_case_present", "file": null, "expect": "the tid-vmo2-fy2025 proxy-run Report (added by Plan 11) is offered as the Prior Case"}], "files": [
      {"path": "VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf", "sha256": "4ec0fed1044430a13a2e38e24c822847149571002651e897f3f076abc61c79be", "class": "issuer", "document_type": "Bond report", "entity": "VMO2", "pages": 47},
      {"path": "VMED-O2-UK-Limited-2025-Annual-Report-and-Consolidated-Financial-Statements.pdf", "sha256": "9a01f61f83e8c0c1aac943fb08df8fbb6b94d5415521818acc78dd59872b2b47", "class": "issuer", "document_type": "Annual report", "entity": "VMO2", "pages": 179},
      {"path": "Virgin-Media-O2-Q1-2026-Earnings-Release.pdf", "sha256": "4ae93a7a25f84b818379405c6adbd20e94d54b6ee115e49ac9788db80f3a3791", "class": "issuer", "document_type": "Earnings release", "entity": "VMO2", "pages": 15}]}
  ]
}
```

`tests/corpus/README.md` — create:

````markdown
# Corpus

`corpus.json` registers every corpus pack with each file's sha256 (interfaces spec section 12). External files never enter the repo; `RBOT_CORPUS_ROOTS` says where they are:

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
uv run python rbot/scripts/rbot.py corpus verify   # 0 ok, 1 missing or changed file, 2 unresolved root
make corpus                                        # RBOT_REQUIRE_CORPUS=1: a missing file fails, never skips
```

Hashes were taken on 2026-10-11 from caos-databricks `5ca9118e` (`qualification/` last changed in `8fd9652b`) and `TEST-Issuer Data` as found that day. A differing hash means the source changed: re-check the pack and update its entry with the tests it affects. `synthetic/` holds packs authored for RBOT: every authored file is labelled SYNTHETIC in its name and first line, and files borrowed from an external root are listed with `external` and copied in at test time.
````

- [ ] **Step 4: Write the corpus module and register the command**

`rbot/scripts/rbotlib/corpus.py` — create:

```python
"""The local issuer corpus: `tests/corpus/corpus.json` (interfaces spec section 12).

Each pack lists its files with sha256 under a root. `external` roots resolve through
RBOT_CORPUS_ROOTS (JSON: root name to absolute path); in-repo roots against the repo.
A file naming `external` (`<root>/<path>`) is copied into the pack when materialised.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rbotlib.rules import RBOT_ROOT

REGISTRY = RBOT_ROOT.parent / "tests" / "corpus" / "corpus.json"
ROOTS_ENV = "RBOT_CORPUS_ROOTS"
EXTERNAL = "external"
MISSING, UNRESOLVED = 1, 2


class CorpusError(ValueError):
    """A pack cannot be materialised; the message names every problem."""


@dataclass(frozen=True)
class CorpusFile:
    path: str
    sha256: str
    cls: str
    document_type: str
    entity: str
    external: str | None
    pages: int | None


@dataclass(frozen=True)
class Pack:
    id: str
    root: str
    path: str
    files: tuple[CorpusFile, ...]
    data: dict[str, Any]  # every registry field as written: issuer, as_of, pathways, traps, ...


@dataclass(frozen=True)
class Registry:
    location: Path
    roots: dict[str, str]
    packs: tuple[Pack, ...]

    def pack(self, pack_id: str) -> Pack:
        for p in self.packs:
            if p.id == pack_id:
                return p
        raise CorpusError(f"no pack {pack_id!r} in {self.location}")


@dataclass(frozen=True)
class Problem:
    code: int  # MISSING (file absent or hash differs) or UNRESOLVED (root unknown)
    in_repo: bool
    message: str


def _file(raw: dict[str, Any]) -> CorpusFile:
    keys = ("path", "sha256", "class", "document_type", "entity")
    path, sha, cls, kind, entity = (raw[k] for k in keys)
    return CorpusFile(path, sha, cls, kind, entity, raw.get("external"), raw.get("pages"))


def _pack(raw: dict[str, Any]) -> Pack:
    return Pack(raw["id"], raw["root"], raw["path"], tuple(_file(f) for f in raw["files"]), raw)


def load_registry(path: Path = REGISTRY) -> Registry:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "rbot-corpus/1":
        raise CorpusError(f"{path}: schema is {data.get('schema')!r}, expected 'rbot-corpus/1'")
    return Registry(path, dict(data["roots"]), tuple(_pack(p) for p in data["packs"]))


def repo_root(registry: Registry) -> Path:
    """The repo holding the registry (`<repo>/tests/corpus/corpus.json`)."""
    return registry.location.parents[2]


def resolve_roots(registry: Registry, env: Mapping[str, str] = os.environ) -> dict[str, Path]:
    """Every root that resolves to a folder; an unresolved root is simply absent."""
    raw = env.get(ROOTS_ENV, "")
    try:
        external = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        raise CorpusError(f"{ROOTS_ENV} is not a JSON object: {exc}") from exc
    if not isinstance(external, dict):
        raise CorpusError(f"{ROOTS_ENV} is not a JSON object")
    roots: dict[str, Path] = {}
    for name, value in registry.roots.items():
        if value != EXTERNAL:
            folder = repo_root(registry) / value
        elif name in external:
            folder = Path(external[name])
        else:
            continue
        if folder.is_dir():
            roots[name] = folder
    return roots


def locate(pack: Pack, f: CorpusFile, roots: Mapping[str, Path]) -> Path | None:
    """Where the file lives now, or None when its root is unresolved."""
    root, _, rest = (f.external or "").partition("/")
    if f.external:
        return roots[root] / rest if root in roots else None
    return roots[pack.root] / pack.path / f.path if pack.root in roots else None


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _check(
    registry: Registry, pack: Pack, roots: Mapping[str, Path]
) -> tuple[list[Problem], dict[str, Path]]:
    problems, found = [], {}
    for f in pack.files:
        local = f.external is None and registry.roots.get(pack.root) != EXTERNAL
        where = locate(pack, f, roots)
        if where is None:
            root = (f.external or "").partition("/")[0] or pack.root
            message = f"{pack.id}: {f.path}: root {root!r} is unresolved; set {ROOTS_ENV}"
            problems.append(Problem(UNRESOLVED, local, message))
        elif not where.is_file():
            problems.append(Problem(MISSING, local, f"{pack.id}: {f.path}: missing at {where}"))
        elif sha256_file(where) != f.sha256:
            problems.append(Problem(MISSING, local, f"{pack.id}: {f.path}: sha256 differs"))
        else:
            found[f.path] = where
    return problems, found


def verify(registry: Registry, pack: Pack, roots: Mapping[str, Path]) -> list[Problem]:
    """Every file of the pack that is unresolved, missing or not the registered bytes."""
    return _check(registry, pack, roots)[0]


def materialise(registry: Registry, pack: Pack, roots: Mapping[str, Path], dest: Path) -> Path:
    """Copy the pack's verified files into `dest` (the Source Pack a test runs on)."""
    problems, found = _check(registry, pack, roots)
    if problems:
        raise CorpusError("; ".join(p.message for p in problems))
    for name, source in found.items():
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return dest


def _list(registry: Registry) -> int:
    for p in registry.packs:
        pathways = "; ".join(f"{w['id']} {w['depth']} {w['fit']}" for w in p.data["pathways"])
        issuer = f"{p.data['issuer']['id']} {p.data['period']}"
        print(f"{p.id}  {p.root}:{p.path}  {issuer}  {len(p.files)} file(s)  {pathways}")
    return 0


def _verify(registry: Registry, pack_id: str | None) -> int:
    roots = resolve_roots(registry)
    packs = [registry.pack(pack_id)] if pack_id else list(registry.packs)
    worst = 0
    for p in packs:
        problems = verify(registry, p, roots)
        for problem in problems:
            print(problem.message)
            worst = max(worst, problem.code)
        if not problems:
            print(f"ok {p.id} ({len(p.files)} files)")
    print(f"exit {worst}")
    return worst


def run_command(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    if args.action == "list":
        return _list(registry)
    return _verify(registry, args.pack)


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("corpus", help="list the corpus packs or verify their files' sha256")
    c.add_argument("action", choices=["verify", "list"])
    c.add_argument("--pack", help="verify one pack only")
    c.add_argument("--registry", default=str(REGISTRY), help="the corpus.json to read")
    c.set_defaults(run=run_command)
```

`rbot/scripts/rbotlib/cli.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/cli.py
+++ b/rbot/scripts/rbotlib/cli.py
@@ -6,6 +6,7 @@ import argparse
 import sys
 from pathlib import Path
 
+from rbotlib import corpus
 from rbotlib.catalog import check_tree
 from rbotlib.contract import ContractError, load_contract
 from rbotlib.render import render_module
@@ -73,6 +74,7 @@ def main(argv: list[str] | None = None) -> int:
     r.set_defaults(run=_render)
     c = sub.add_parser("check", help="contracts, generated modules, Pathways, Front Pages, budget")
     c.set_defaults(run=_check)
+    corpus.add_command(sub)
     args = parser.parse_args(argv)
     result: int = args.run(args)
     return result
```

- [ ] **Step 5: Wire `make corpus` and CI**

`Makefile` — create:

```make
# Corpus regression on the owner's machine (interfaces spec section 12.3).
# Needs RBOT_CORPUS_ROOTS (tests/corpus/README.md); a missing corpus file fails, never skips.
.PHONY: corpus
corpus:
	RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov
	uv run python rbot/scripts/rbot.py corpus verify
```

`.github/workflows/ci.yml` — patch:

```diff
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -32,6 +32,9 @@ jobs:
       - run: uv run mypy
       - run: uv run pytest
       - run: uv run python rbot/scripts/rbot.py check
+      # Corpus tests (interfaces spec section 12.3): in-repo synthetic files must be
+      # present; external packs live only on the owner's machine (make corpus).
+      - run: RBOT_REQUIRE_CORPUS=synthetic uv run pytest -m corpus --no-cov
       - run: uv run python scripts/check_suppressions.py
       - run: uv run complexipy rbot/scripts scripts --max-complexity-allowed 15
       - run: uv run bandit -r rbot/scripts scripts -f json -o bandit.json || true
```

- [ ] **Step 6: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without `RBOT_CORPUS_ROOTS`: `136 passed, 33 skipped` (the 33 `test_corpus_hashes_match` cases skip, naming the unresolved root).

Run the gate run, then the corpus gate (Global Constraints).
Expected: every command exits 0; `RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov` reports `33 passed, 136 deselected`; `rbot corpus verify` prints `ok <pack> (<n> files)` for all 33 packs and `exit 0`.

- [ ] **Step 7: Prove the require rule fails rather than skips**

```bash
RBOT_CORPUS_ROOTS='{}' RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov; echo "exit $?"
```

Expected: `33 failed`, each naming `root 'caos-qualification' is unresolved; set RBOT_CORPUS_ROOTS` (or `test-issuer-data`), and `exit 1`.

- [ ] **Step 8: Commit, then open PR 02A (Tasks 1–2)**

```bash
git add rbot tests Makefile pyproject.toml .github/workflows/ci.yml
git commit -m "corpus: registry of 33 packs with sha256, rbot corpus, corpus marker and require rule

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=813aa02 bash scripts/check_pr_size.sh
```

Expected: `784 changed lines (limit 800)`.

Report: test counts with and without the corpus roots, the gate and corpus-gate exit codes, the PR size. `Not verified:` CI on GitHub (no remote yet); that the caos checkout stays at `5ca9118e` (a moved checkout fails `rbot corpus verify` loudly, by design).

---

### Task 3: `rbot inventory`, the run's pack root and pypdf

**Files:**
- Create: `rbot/scripts/rbotlib/inventory.py`, `docs/decisions/0002-pypdf.md`, `tests/builders.py`
- Modify: `rbot/scripts/rbotlib/cli.py`, `tests/conftest.py`, `pyproject.toml` (the `pypdf` dependency; `builders` as first-party), `uv.lock` (regenerated)
- Test: `tests/test_inventory.py`

**Interfaces:**
- Consumes: `rbotlib.corpus.sha256_file`, `CORPUS`, `corpus_gate`, `materialise`.
- Produces:
  - `rbotlib.inventory`: `SCHEMA = "rbot-inventory/1"`; `RUNS = "rbot-runs"`; `RunError(ValueError)`; `pack_root(run) -> Path` (`pack_root` from `<RUN>/run-state.json` when that file exists — Plan 06's `new-run` writes it, Task 9's proxy run writes a pre-Approval seed — else the folder above `rbot-runs/`); `kind_of(path) -> str` (`pdf`, `xlsx`, `csv`, `txt`, `md`, `html`, `image`, `other`); `pdf_pages(path) -> int | None`; `build(pack, run_name) -> dict`; `write(run) -> dict`; `load(run) -> dict`; `add_command(sub)`.
  - `<RUN>/inventory.json`: `{"schema", "pack_root", "generated_at", "files": [{"path", "size", "sha256", "extension", "kind", "pages", "rbot_report"}], "skipped": [{"path", "reason"}]}`, files sorted by path; `pages` is the PDF page count (else null); `rbot_report` is true for an html/md file holding `id="rbot-run"`. Hidden files and folders, Office lock files (`~$…`) and symbolic links are skipped with their reason; `rbot-runs/` is not walked, except another run's `report.html`/`report.md` (a Prior Case candidate, design D23).
  - `rbot inventory --run <RUN>`: exit 0; 1 when the pack is empty or the run folder is unusable (§9).
  - `rbotlib.cli`: every command given `--run` appends `<ISO time>\t<command line>\t<exit>` to `<RUN>/log/rbot.log` (§8.1).
  - `tests/builders.py`: `make_pdf(pages: list[str]) -> bytes` (a minimal valid PDF, one Helvetica line per page, `''` = a page without text); `make_run(pack, name="20261011-test-pending") -> Path`.
  - `tests/conftest.py`: session fixture `corpus_pack(pack_id) -> Path` (a materialised throwaway Source Pack per corpus pack).

- [ ] **Step 1: Branch for PR 02B and add the PDF dependency (decision record first)**

```bash
git switch -c build/02b-intake
```

`docs/decisions/0002-pypdf.md` — create:

```markdown
# 0002 — pypdf for PDF text and page counts

**Need:** `rbot inventory` counts PDF pages and `rbot prepare` turns each PDF page into page-anchored text (interfaces spec section 8.1). Filings, rating reports and bond reports arrive as PDFs (TEST-Issuer Data, the VMO2 packs).

**Order of preference (global rule):** the standard library has no PDF parser; no locked dependency reads PDFs; writing a PDF text extractor (fonts, encodings, compressed streams, cross-reference repair) is far beyond this plan. So a new runtime dependency.

**Choice:** `pypdf` — pure Python, no compiled code and no required dependencies on Python 3.11+, BSD-3-Clause, actively maintained, and the library the Copilot spike installs (`pip install --user pypdf openpyxl`, Plan 01 Task 2). Alternatives rejected: `pdfminer.six` (pulls in `cryptography` and `charset-normalizer`), `pypdfium2` and `PyMuPDF` (compiled binaries; PyMuPDF is AGPL).

**Version:** pinned `pypdf==6.19.0` (released 2026-09-16). The newest release older than 30 days on 2026-10-11 is 6.18.1 (2026-09-11), but it carries three advisories fixed in 6.19.0 (GHSA-w23x-9jrw-r45c page-label memory use, GHSA-php9-fj8v-98fj form flattening runtime, GHSA-v247-6f48-mgcj embedded-file runtime), so `pip-audit --strict` refuses it. 6.19.0 has no known advisory and passes 30 days on 2026-10-16. 6.20.0 (2026-10-09) is too new. Upgrade only to a release at least 30 days old that `pip-audit --strict` accepts.

**Use:** only `PdfReader(path)`, `is_encrypted`, `decrypt("")`, `len(reader.pages)` and `page.extract_text()`. A file pypdf cannot open (`PyPdfError`, `ValueError`, `KeyError`, `OSError`) is listed as unreadable with the error text, never skipped silently. PDFs are untrusted input: no page labels, form flattening or embedded files are read, which keeps RBOT off the code paths of the advisories above.

**Analyst machines:** the Copilot host installs it with `python -m pip install --user pypdf==6.19.0` (the install step arrives with Plan 06).
```

`pyproject.toml` — patch:

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -3,7 +3,9 @@ name = "deploy-vi"
 version = "0.1.0"
 description = "RBOT: leveraged-finance credit research as a GitHub Copilot skill"
 requires-python = ">=3.11"
-dependencies = []
+dependencies = [
+    "pypdf==6.19.0",
+]
 
 [tool.uv]
 package = false
@@ -25,7 +27,9 @@ ignore = ["TRY003"]
 max-complexity = 10
 
 [tool.ruff.lint.isort]
-known-first-party = ["rbotlib", "conftest", "check_suppressions", "check_bandit_floor"]
+known-first-party = [
+  "rbotlib", "conftest", "builders", "check_suppressions", "check_bandit_floor",
+]
 
 [tool.mypy]
 python_version = "3.11"
```

```bash
uv lock && uv sync
uv run python -c "import pypdf; print(pypdf.__version__)"
uv run pip-audit --strict
```

Expected: `6.19.0`; `No known vulnerabilities found`.

- [ ] **Step 2: Write the failing tests**

`tests/builders.py` — create:

```python
"""Builders for test inputs: tiny real PDFs and run folders inside a Source Pack."""

from __future__ import annotations

from pathlib import Path

FONT = "<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>"


def make_pdf(pages: list[str]) -> bytes:
    """A minimal valid PDF with one Helvetica text line per page ('' = a page without text)."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", ""]
    kids = []
    for text in pages:
        content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET" if text else ""
        objects.append(f"<< /Length {len(content)} >>\nstream\n{content}\nendstream")
        objects.append(
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
            f" /Contents {len(objects)} 0 R /Resources {FONT} >>"
        )
        kids.append(f"{len(objects)} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    out, offsets = b"%PDF-1.4\n", []
    for n, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out + trailer.encode()


def make_run(pack: Path, name: str = "20261011-test-pending") -> Path:
    """An empty run folder at <pack>/rbot-runs/<name>/ (spec section 8.1)."""
    run = pack / "rbot-runs" / name
    run.mkdir(parents=True)
    return run
```

`tests/conftest.py` — patch:

```diff
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -5,13 +5,14 @@ from __future__ import annotations
 import json
 import os
 import shutil
+from collections.abc import Callable
 from pathlib import Path
 from typing import Any
 
 import pytest
 
 from rbotlib.contract import contract_from_dict
-from rbotlib.corpus import Problem, load_registry
+from rbotlib.corpus import Problem, load_registry, materialise, resolve_roots, verify
 from rbotlib.render import render_module
 from rbotlib.rules import RBOT_ROOT, Rules, load_rules
 
@@ -88,3 +89,19 @@ def corpus_gate(problems: list[Problem]) -> None:
     if level == "1" or (level == "synthetic" and any(p.in_repo for p in problems)):
         pytest.fail(message)
     pytest.skip(message)
+
+
+@pytest.fixture(scope="session")
+def corpus_pack(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
+    """Materialise a corpus pack once per session as a throwaway Source Pack."""
+    made: dict[str, Path] = {}
+
+    def get(pack_id: str) -> Path:
+        if pack_id not in made:
+            pack = CORPUS.pack(pack_id)
+            roots = resolve_roots(CORPUS)
+            corpus_gate(verify(CORPUS, pack, roots))
+            made[pack_id] = materialise(CORPUS, pack, roots, tmp_path_factory.mktemp(pack_id))
+        return made[pack_id]
+
+    return get
```

`tests/test_inventory.py` — create:

```python
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import make_pdf, make_run
from conftest import CORPUS
from rbotlib.cli import main
from rbotlib.inventory import RunError, pack_root


def _pack(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    (pack / "sub").mkdir(parents=True)
    (pack / "CZR_10Q.txt").write_text("CAESARS ENTERTAINMENT, INC.\n", encoding="utf-8")
    (pack / "sub" / "levels.csv").write_text("id,price\nA,99.5\n", encoding="utf-8")
    (pack / "report.pdf").write_bytes(make_pdf(["page one", "page two"]))
    (pack / "broken.pdf").write_bytes(b"%PDF-1.4 not really")
    (pack / ".DS_Store").write_bytes(b"\x00")
    (pack / "~$model.xlsx").write_bytes(b"lock")
    (pack / ".git").mkdir()
    (pack / "link.txt").symlink_to(pack / "CZR_10Q.txt")
    earlier = pack / "rbot-runs" / "20260715-czr-earnings-update"
    earlier.mkdir(parents=True)
    (earlier / "report.html").write_text('<script id="rbot-run">{}</script>', encoding="utf-8")
    (earlier / "model.json").write_text("{}", encoding="utf-8")
    return pack


def _inventory(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    return data


def test_inventory_lists_files_and_skips_with_reasons(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pack = _pack(tmp_path)
    run = make_run(pack)
    (run / "inventory.json").write_text("{}", encoding="utf-8")
    assert main(["inventory", "--run", str(run)]) == 0
    assert capsys.readouterr().out == "inventory.json: 5 file(s), 4 skipped\n"
    data = _inventory(run)
    assert data["schema"] == "rbot-inventory/1" and data["pack_root"] == str(pack)
    by_path = {f["path"]: f for f in data["files"]}
    assert list(by_path) == [
        "CZR_10Q.txt",
        "broken.pdf",
        "rbot-runs/20260715-czr-earnings-update/report.html",
        "report.pdf",
        "sub/levels.csv",
    ]
    assert by_path["report.pdf"]["pages"] == 2 and by_path["report.pdf"]["kind"] == "pdf"
    assert by_path["broken.pdf"]["pages"] is None
    assert by_path["sub/levels.csv"]["kind"] == "csv" and by_path["sub/levels.csv"]["size"] == 16
    assert by_path["rbot-runs/20260715-czr-earnings-update/report.html"]["rbot_report"] is True
    assert by_path["CZR_10Q.txt"]["rbot_report"] is False
    assert len(by_path["CZR_10Q.txt"]["sha256"]) == 64
    assert data["skipped"] == [
        {"path": ".DS_Store", "reason": "hidden"},
        {"path": ".git", "reason": "hidden"},
        {"path": "link.txt", "reason": "symbolic link"},
        {"path": "~$model.xlsx", "reason": "office lock file"},
    ]


def test_inventory_is_deterministic_apart_from_its_time(tmp_path: Path) -> None:
    run = make_run(_pack(tmp_path))
    main(["inventory", "--run", str(run)])
    first = _inventory(run)
    main(["inventory", "--run", str(run)])
    second = _inventory(run)
    first.pop("generated_at")
    second.pop("generated_at")
    assert first == second


def test_each_run_command_is_logged(tmp_path: Path) -> None:
    run = make_run(_pack(tmp_path))
    main(["inventory", "--run", str(run)])
    time, command, code = (run / "log" / "rbot.log").read_text(encoding="utf-8").split("\t")
    assert time.endswith("+00:00")
    assert (command, code) == (f"inventory --run {run}", "0\n")


def test_the_pack_root_comes_from_run_state_or_the_folder(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    assert pack_root(make_run(pack)) == pack
    elsewhere = tmp_path / "proxy" / "run"
    elsewhere.mkdir(parents=True)
    with pytest.raises(RunError, match="not inside a rbot-runs/ folder"):
        pack_root(elsewhere)
    state = {"schema": "rbot-run-state/1", "pack_root": str(pack)}
    (elsewhere / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    assert pack_root(elsewhere) == pack
    (elsewhere / "run-state.json").write_text("{", encoding="utf-8")
    with pytest.raises(RunError, match="no readable pack_root"):
        pack_root(elsewhere)


def test_an_empty_pack_or_a_stray_folder_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = make_run(tmp_path / "empty")
    assert main(["inventory", "--run", str(run)]) == 1
    assert "the Source Pack has no files" in capsys.readouterr().out
    assert main(["inventory", "--run", str(tmp_path / "nowhere")]) == 1
    assert "no such run folder" in capsys.readouterr().out
    (tmp_path / "stray").mkdir()
    assert main(["inventory", "--run", str(tmp_path / "stray")]) == 1
    assert "not inside a rbot-runs/ folder" in capsys.readouterr().out


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_inventory_is_deterministic(pack_id: str, corpus_pack: Callable[[str], Path]) -> None:
    run = make_run(corpus_pack(pack_id), f"20261011-{pack_id}-inventory")
    runs = []
    for _ in range(2):
        assert main(["inventory", "--run", str(run)]) == 0
        data = _inventory(run)
        data.pop("generated_at")
        runs.append(data)
    assert runs[0] == runs[1]
    registered = {f.path: f for f in CORPUS.pack(pack_id).files}
    listed = {f["path"]: f for f in runs[0]["files"]}
    assert sorted(listed) == sorted(registered)
    for path, f in registered.items():
        assert listed[path]["sha256"] == f.sha256
        assert listed[path]["pages"] == f.pages
```

- [ ] **Step 3: Run them to see them fail**

Run: `uv run pytest tests/test_inventory.py --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'rbotlib.inventory'` while collecting `tests/test_inventory.py`.

- [ ] **Step 4: Write the inventory and register the command**

`rbot/scripts/rbotlib/inventory.py` — create:

```python
"""`rbot inventory`: list every file of the Source Pack (interfaces spec section 8.1).

Writes `<RUN>/inventory.json`: per file its path relative to the pack, size, sha256,
extension, detected kind, PDF page count and whether it is an earlier RBOT Report.
Hidden files and folders, Office lock files and symbolic links are skipped and listed
with the reason. `rbot-runs/` is not walked: only another run's `report.html` or
`report.md` is listed, because an earlier Report is a Prior Case candidate. Source
files are only read, never modified.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from rbotlib.corpus import sha256_file

SCHEMA = "rbot-inventory/1"
RUNS = "rbot-runs"
REPORT_MARKER = 'id="rbot-run"'
REPORT_NAMES = ("report.html", "report.md")
KINDS = {
    "pdf": "pdf",
    "xlsx": "xlsx",
    "xlsm": "xlsx",
    "csv": "csv",
    "txt": "txt",
    "md": "md",
    "markdown": "md",
    "html": "html",
    "htm": "html",
    **dict.fromkeys(("png", "jpg", "jpeg", "gif", "bmp", "tif", "tiff", "webp"), "image"),
}


class RunError(ValueError):
    """The run folder cannot be used; the message names why."""


def pack_root(run: Path) -> Path:
    """The Source Pack of a run: `pack_root` in run-state.json, else the folder above rbot-runs/."""
    state = run / "run-state.json"
    if state.is_file():
        try:
            return Path(json.loads(state.read_text(encoding="utf-8"))["pack_root"])
        except (json.JSONDecodeError, KeyError) as exc:
            raise RunError(f"{state}: no readable pack_root ({exc})") from exc
    if run.parent.name == RUNS:
        return run.parent.parent
    raise RunError(f"{run}: no run-state.json and not inside a {RUNS}/ folder")


def kind_of(path: Path) -> str:
    return KINDS.get(path.suffix.lower().lstrip("."), "other")


def pdf_pages(path: Path) -> int | None:
    """Page count, or None when pypdf cannot open the file (prepare records why)."""
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:
            reader.decrypt("")
        return len(reader.pages)
    except (PyPdfError, ValueError, KeyError, OSError):
        return None


def _skip_reason(path: Path) -> str | None:
    if path.is_symlink():
        return "symbolic link"
    if path.name.startswith("."):
        return "hidden"
    if path.name.startswith("~$"):
        return "office lock file"
    return None


def _earlier_reports(runs: Path, run_name: str) -> list[Path]:
    """Report files of other runs in the pack's rbot-runs/ folder."""
    if not runs.is_dir():
        return []
    found = [
        runs / d / name for d in sorted(os.listdir(runs)) if d != run_name for name in REPORT_NAMES
    ]
    return [p for p in found if p.is_file() and not p.is_symlink()]


def _walk(pack: Path, run_name: str) -> tuple[list[Path], list[dict[str, str]]]:
    keep: list[Path] = []
    skipped: list[dict[str, str]] = []

    def usable(path: Path) -> bool:
        reason = _skip_reason(path)
        if reason:
            skipped.append({"path": path.relative_to(pack).as_posix(), "reason": reason})
        return reason is None

    for folder, dirs, names in os.walk(pack):
        here = Path(folder)
        dirs[:] = [d for d in sorted(dirs) if usable(here / d) and not (here == pack and d == RUNS)]
        keep += [here / n for n in sorted(names) if usable(here / n)]
    return keep + _earlier_reports(pack / RUNS, run_name), skipped


def _entry(path: Path, rel: str) -> dict[str, Any]:
    kind = kind_of(path)
    report = False
    if kind in ("html", "md"):
        report = REPORT_MARKER in path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": rel,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "extension": path.suffix.lower().lstrip("."),
        "kind": kind,
        "pages": pdf_pages(path) if kind == "pdf" else None,
        "rbot_report": report,
    }


def build(pack: Path, run_name: str) -> dict[str, Any]:
    keep, skipped = _walk(pack, run_name)
    files = [_entry(path, path.relative_to(pack).as_posix()) for path in keep]
    return {
        "schema": SCHEMA,
        "pack_root": str(pack),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "files": sorted(files, key=lambda f: f["path"]),
        "skipped": sorted(skipped, key=lambda f: f["path"]),
    }


def write(run: Path) -> dict[str, Any]:
    if not run.is_dir():
        raise RunError(f"{run}: no such run folder")
    pack = pack_root(run)
    inventory = build(pack, run.name)
    if not inventory["files"]:
        raise RunError(f"{pack}: the Source Pack has no files")
    text = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    (run / "inventory.json").write_text(text, encoding="utf-8")
    return inventory


def load(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    return data


def run_command(args: argparse.Namespace) -> int:
    try:
        inventory = write(Path(args.run_dir))
    except RunError as exc:
        print(exc)
        return 1
    n, s = len(inventory["files"]), len(inventory["skipped"])
    print(f"inventory.json: {n} file(s), {s} skipped")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("inventory", help="list every Source Pack file with its sha256 and kind")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    c.set_defaults(run=run_command)
```

`rbot/scripts/rbotlib/cli.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/cli.py
+++ b/rbot/scripts/rbotlib/cli.py
@@ -1,12 +1,16 @@
-"""`rbot` command line: validate a Handoff, render a MODULE.md, check the tree."""
+"""`rbot` command line. Each later command lives with its module (`add_command`).
+
+A command given `--run <RUN>` appends one line to `<RUN>/log/rbot.log`.
+"""
 
 from __future__ import annotations
 
 import argparse
 import sys
+from datetime import UTC, datetime
 from pathlib import Path
 
-from rbotlib import corpus
+from rbotlib import corpus, inventory
 from rbotlib.catalog import check_tree
 from rbotlib.contract import ContractError, load_contract
 from rbotlib.render import render_module
@@ -60,6 +64,14 @@ def _check(args: argparse.Namespace) -> int:
     return 1 if problems else 0
 
 
+def _log(run: Path, argv: list[str], code: int) -> None:
+    """One line per command in <RUN>/log/rbot.log: time, command, exit (spec section 8.1)."""
+    (run / "log").mkdir(exist_ok=True)
+    stamp = datetime.now(UTC).isoformat(timespec="seconds")
+    with (run / "log" / "rbot.log").open("a", encoding="utf-8") as log:
+        log.write(f"{stamp}\t{' '.join(argv)}\t{code}\n")
+
+
 def main(argv: list[str] | None = None) -> int:
     parser = argparse.ArgumentParser(prog="rbot")
     parser.add_argument("--root", type=Path, default=RBOT_ROOT, help="the RBOT folder")
@@ -75,6 +87,10 @@ def main(argv: list[str] | None = None) -> int:
     c = sub.add_parser("check", help="contracts, generated modules, Pathways, Front Pages, budget")
     c.set_defaults(run=_check)
     corpus.add_command(sub)
+    inventory.add_command(sub)
     args = parser.parse_args(argv)
     result: int = args.run(args)
+    run_dir = getattr(args, "run_dir", None)
+    if run_dir and Path(run_dir).is_dir():
+        _log(Path(run_dir), sys.argv[1:] if argv is None else argv, result)
     return result
```

- [ ] **Step 5: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `141 passed, 66 skipped`. With the corpus gate: `66 passed, 141 deselected` — `test_inventory_is_deterministic[<pack>]` runs `rbot inventory` twice on every pack and finds identical files, sha256 and PDF page counts equal to the registry.

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 6: Commit**

```bash
git add rbot tests pyproject.toml uv.lock docs/decisions/0002-pypdf.md
git commit -m "intake: rbot inventory with sha256, kinds and PDF page counts; pypdf (decision 0002)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report: test counts, gate and corpus-gate exit codes. `Not verified:` installing `pypdf` on the work machine (`pip install --user`, Plan 01's spike); behaviour on a Windows path with a non-ASCII file name (no corpus file has one).

---

### Task 4: `rbot prepare` for text and PDF, with first-page entities and dates

**Files:**
- Create: `rbot/scripts/rbotlib/prepare.py`
- Modify: `rbot/scripts/rbotlib/cli.py`, `tests/conftest.py`
- Test: `tests/test_prepare.py`

**Interfaces:**
- Consumes: `inventory.json` and `rbotlib.inventory.RunError` (Task 3); `pypdf.PdfReader`.
- Produces:
  - `rbotlib.prepare`: `SCHEMA = "rbot-prepared/1"`; `UnreadableError(Exception)`; `Prepared(pages: list[str], sheets, image_read: bool)`; `page_marker(n) -> str` (`<<< page N >>>`); `read_text`, `read_pdf` (a PDF with under 20 extractable characters in total is a scan: `image_read` true); `READERS: dict[str, Callable[[Path], Prepared]]`; `read(path, kind) -> Prepared` (raises `UnreadableError("no reader for .<ext> files")`); `entities(first_page) -> list[str]` (the SEC registrant line, then capitalised corporate names, at most 8 — hints for CP-0, not a classification); `dates(first_page) -> list[str]` (ISO dates written as `Month D, YYYY`, `D Month YYYY` or ISO, in order, no repeats); `slug(name)`; `prepared_name(entry) -> "prepared/<sha16>-<slug>.txt"`; `anchored_text(pages) -> str`; `prepare_file(run, pack, entry) -> dict`; `write(run) -> dict`; `load_index(run) -> dict`; `add_command(sub)`.
  - `<RUN>/prepared/<sha16>-<slug>.txt`: each page as `<<< page N >>>` then its text; a text or Markdown file is one page unless it holds form feeds (SEC text filings carry no page breaks, so their citations use section locators).
  - `<RUN>/prepared/index.json`: `{"schema", "generated_at", "files": [{"path", "sha256", "kind", "prepared", "pages", "excerpt", "entities", "dates", "sheets", "image_read", "unreadable"}]}`; `excerpt` = the first 400 characters of page 1 with whitespace collapsed; an unreadable file keeps `prepared` null and `unreadable` = the reason.
  - `rbot prepare --run <RUN>`: exit 0 with unreadable files listed; 1 only when the run has no readable `inventory.json` or the run folder cannot be written (§9).
  - `tests/conftest.py`: session fixture `prepared_run(pack_id) -> Path` (inventory and prepare done once per corpus pack).

- [ ] **Step 1: Write the failing tests**

`tests/conftest.py` — patch:

```diff
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -11,6 +11,7 @@ from typing import Any
 
 import pytest
 
+from rbotlib.cli import main
 from rbotlib.contract import contract_from_dict
 from rbotlib.corpus import Problem, load_registry, materialise, resolve_roots, verify
 from rbotlib.render import render_module
@@ -105,3 +106,20 @@ def corpus_pack(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Pat
         return made[pack_id]
 
     return get
+
+
+@pytest.fixture(scope="session")
+def prepared_run(corpus_pack: Callable[[str], Path]) -> Callable[[str], Path]:
+    """A run folder per corpus pack with `rbot inventory` and `rbot prepare` done, once."""
+    made: dict[str, Path] = {}
+
+    def get(pack_id: str) -> Path:
+        if pack_id not in made:
+            run = corpus_pack(pack_id) / "rbot-runs" / f"20261011-{pack_id}-prepared"
+            run.mkdir(parents=True)
+            assert main(["inventory", "--run", str(run)]) == 0
+            assert main(["prepare", "--run", str(run)]) == 0
+            made[pack_id] = run
+        return made[pack_id]
+
+    return get
```

`tests/test_prepare.py` — create:

```python
from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import make_pdf, make_run
from conftest import CORPUS
from rbotlib.cli import main
from rbotlib.prepare import dates, entities, load_index

SEC_COVER = (
    "Commission File No. 001-36629\nCAESARS ENTERTAINMENT, INC.\n"
    "(Exact name of registrant as specified in its charter)\nDelaware corporation\n"
    "For the quarterly period ended June 30, 2026"
)


def _prepared(tmp_path: Path, files: dict[str, bytes]) -> tuple[Path, dict[str, dict[str, Any]]]:
    pack = tmp_path / "pack"
    pack.mkdir()
    for name, data in files.items():
        (pack / name).write_bytes(data)
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run, {r["path"]: r for r in load_index(run)["files"]}


def _text(run: Path, record: dict[str, Any]) -> str:
    return (run / str(record["prepared"])).read_text(encoding="utf-8")


def test_text_and_markdown_become_page_anchored_text(tmp_path: Path) -> None:
    run, index = _prepared(
        tmp_path,
        {
            "CZR_10Q.txt": (SEC_COVER + "\fpage two text\n").encode(),
            "note.md": b"# Note\nOne page.\n",
        },
    )
    tenq = index["CZR_10Q.txt"]
    assert tenq["pages"] == 2 and tenq["kind"] == "txt"
    assert tenq["prepared"] == f"prepared/{tenq['sha256'][:16]}-czr-10q-txt.txt"
    assert _text(run, tenq).endswith("<<< page 2 >>>\npage two text\n")
    assert tenq["entities"] == ["CAESARS ENTERTAINMENT, INC."]
    assert tenq["dates"] == ["2026-06-30"]
    assert tenq["excerpt"].startswith("Commission File No. 001-36629 CAESARS ENTERTAINMENT, INC.")
    assert _text(run, index["note.md"]) == "<<< page 1 >>>\n# Note\nOne page.\n"


def test_pdf_pages_scans_and_unreadable_files(tmp_path: Path) -> None:
    run, index = _prepared(
        tmp_path,
        {
            "ford.pdf": make_pdf(["FORD MOTOR COMPANY, Dated as of July 28, 2025", "page two"]),
            "scan.pdf": make_pdf(["", ""]),
            "broken.pdf": b"%PDF-1.4 not really",
            "memo.docx": b"PK\x03\x04",
        },
    )
    ford = index["ford.pdf"]
    assert ford["pages"] == 2 and ford["entities"] == ["FORD MOTOR COMPANY"]
    assert ford["dates"] == ["2025-07-28"] and ford["image_read"] is False
    assert _text(run, ford) == (
        "<<< page 1 >>>\nFORD MOTOR COMPANY, Dated as of July 28, 2025\n<<< page 2 >>>\npage two\n"
    )
    assert index["scan.pdf"]["image_read"] is True and index["scan.pdf"]["pages"] == 2
    assert index["broken.pdf"]["unreadable"].startswith("pypdf could not read the PDF")
    assert index["broken.pdf"]["prepared"] is None
    assert index["memo.docx"]["unreadable"] == "no reader for .docx files"


def test_prepare_reports_unreadable_files_and_still_exits_0(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _prepared(tmp_path, {"a.txt": b"text\n", "memo.docx": b"PK"})
    out = capsys.readouterr().out
    assert "unreadable: memo.docx: no reader for .docx files\n" in out
    assert out.endswith("prepared/index.json: 2 file(s), 1 unreadable\n")


def test_prepare_without_an_inventory_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = make_run(tmp_path / "pack")
    assert main(["prepare", "--run", str(run)]) == 1
    assert "run rbot inventory first" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("first_page", "expected"),
    [
        (SEC_COVER, ["CAESARS ENTERTAINMENT, INC."]),
        (
            "among\nFORD MOTOR COMPANY,\nand JPMORGAN CHASE BANK, N.A.",
            ["FORD MOTOR COMPANY", "JPMORGAN CHASE BANK, N.A."],
        ),
        ("as Parent SIX FLAGS OPERATIONS INC., as Holdings", ["SIX FLAGS OPERATIONS INC."]),
        ("a Delaware corporation and The Company", []),
        ("Overview. Ford Motor Company makes cars", ["Ford Motor Company"]),
    ],
)
def test_entity_names_on_the_first_page(first_page: str, expected: list[str]) -> None:
    assert entities(first_page) == expected


def test_dates_are_iso_in_order_without_repeats() -> None:
    text = "ended January 2, 2022; 31 March 2026; at 2026-10-02T09:31Z; again January 2, 2022"
    assert dates(text + "; February 30, 2020") == ["2022-01-02", "2026-03-31", "2026-10-02"]


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_prepare_pages_and_markers(pack_id: str, prepared_run: Callable[[str], Path]) -> None:
    run = prepared_run(pack_id)
    index = {r["path"]: r for r in load_index(run)["files"]}
    for f in CORPUS.pack(pack_id).files:
        record = index[f.path]
        assert record["unreadable"] is None, f.path
        if f.pages is not None:
            assert record["pages"] == f.pages, f.path
        text = _text(run, record)
        markers = [int(n) for n in re.findall(r"^<<< page (\d+) >>>$", text, re.M)]
        assert markers == list(range(1, record["pages"] + 1)), f.path


@pytest.mark.corpus
@pytest.mark.parametrize(
    ("pack_id", "misfiled", "named"),
    [
        (
            "tid-ford",
            "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf",
            "SIX FLAGS",
        ),
        ("tid-six-flags", "f-20251231.pdf", "Ford"),
    ],
)
def test_entity_trap_flagged(
    pack_id: str, misfiled: str, named: str, prepared_run: Callable[[str], Path]
) -> None:
    index = json.loads((prepared_run(pack_id) / "prepared" / "index.json").read_text())
    record = next(r for r in index["files"] if r["path"] == misfiled)
    assert any(named in name for name in record["entities"]), record["entities"]
    issuer = CORPUS.pack(pack_id).data["issuer"]["name"].split()[0].upper()
    assert not any(issuer in name.upper() for name in record["entities"])
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'rbotlib.prepare'` while collecting `tests/test_prepare.py`.

- [ ] **Step 3: Write the preparer and register the command**

`rbot/scripts/rbotlib/prepare.py` — create:

```python
"""`rbot prepare`: page-anchored text for every inventoried file (interfaces spec section 8.1).

Each readable file becomes `prepared/<sha16>-<slug>.txt`, its pages opened by
`<<< page N >>>` lines, so a citation's page locator and excerpt can be checked.
`prepared/index.json` records per file the prepared path, page count, a 400-character
first-page excerpt, the entity names and dates found on the first page, sheet names
and the `image_read` flag. A file that cannot be read is listed with `unreadable`
and the reason; the others are still prepared (exit 0).
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from rbotlib.inventory import RunError

SCHEMA = "rbot-prepared/1"
EXCERPT_CHARS = 400
MAX_ENTITIES = 8
MIN_PDF_TEXT = 20  # fewer extracted characters in the whole PDF: a scan, read as an image


class UnreadableError(Exception):
    """This file cannot be prepared; the message is recorded as `unreadable`."""


@dataclass
class Prepared:
    pages: list[str]
    sheets: list[str] = field(default_factory=list)
    image_read: bool = False


def page_marker(n: int) -> str:
    return f"<<< page {n} >>>"


# --- readers -----------------------------------------------------------------


def read_text(path: Path) -> Prepared:
    """Plain text and Markdown: form feeds separate pages; without them, one page."""
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    return Prepared(text.split("\f"))


def read_pdf(path: Path) -> Prepared:
    """PDF pages through pypdf; a PDF with (almost) no extractable text is a scan."""
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and not reader.decrypt(""):
            raise UnreadableError("encrypted PDF: a password is needed")
        pages = [(page.extract_text() or "").replace("\r\n", "\n") for page in reader.pages]
    except (PyPdfError, ValueError, KeyError, OSError) as exc:
        raise UnreadableError(f"pypdf could not read the PDF: {type(exc).__name__}: {exc}") from exc
    if sum(len(p.strip()) for p in pages) < MIN_PDF_TEXT:
        return Prepared(["" for _ in pages], image_read=True)
    return Prepared(pages)


READERS: dict[str, Callable[[Path], Prepared]] = {
    "txt": read_text,
    "md": read_text,
    "pdf": read_pdf,
}


def read(path: Path, kind: str) -> Prepared:
    reader = READERS.get(kind)
    if reader is None:
        raise UnreadableError(f"no reader for .{path.suffix.lower().lstrip('.')} files")
    return reader(path)


# --- first-page detection ------------------------------------------------------

_REGISTRANT = re.compile(r"^\s*(.+?)\s*\n\s*\(exact name of registrant", re.I | re.M)
_SUFFIX = (
    r"(?:Inc\.?|INC\.?|Corporation|CORPORATION|Corp\.|CORP\.|Company|COMPANY|plc|PLC"
    r"|Limited|LIMITED|Ltd\.?|LTD\.?|LLC|L\.P\.|N\.A\.)"
)
_NAME = re.compile(r"\b((?:[A-Z][\w&'\u2019.-]*,?\s+){1,6}" + _SUFFIX + r")(?![\w])")
_GENERIC = frozenset({"the", "this", "our", "such", "each", "any"})
_MONTHS = "january february march april may june july august september october november december"
_MONTH = {m: n for n, m in enumerate(_MONTHS.split(), 1)}
_MDY = re.compile(r"\b(" + "|".join(_MONTH) + r")\s+(\d{1,2}),\s*(\d{4})\b", re.I)
_DMY = re.compile(r"\b(\d{1,2})\s+(" + "|".join(_MONTH) + r")\s+(\d{4})\b", re.I)
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?!\d)")


def _clean(raw: str) -> str | None:
    """Trim a candidate name to the company: drop a preceding sentence and lower-case lead-ins."""
    words = raw.replace("|", " ").split()
    breaks = [i for i, w in enumerate(words[:-1]) if w.endswith(".") and len(w) > 4]
    words = words[breaks[-1] + 1 :] if breaks else words
    if any(w.isupper() and len(w) > 1 for w in words[:-1]):
        while words and not words[0].isupper():
            words.pop(0)
    if len(words) < 2 or {w.casefold() for w in words[:-1]} <= _GENERIC:
        return None
    return " ".join(words).strip(" ,")


def entities(first_page: str) -> list[str]:
    """Entity names on the first page: the SEC registrant line first, then corporate names."""
    found = [m.group(1) for m in _REGISTRANT.finditer(first_page)]
    found += [m.group(1) for m in _NAME.finditer(first_page)]
    names: list[str] = []
    for raw in found:
        name = _clean(raw)
        if name and name.casefold() not in {n.casefold() for n in names}:
            names.append(name)
    return names[:MAX_ENTITIES]


def _iso(y: str, m: int, d: str) -> str | None:
    try:
        return date(int(y), m, int(d)).isoformat()
    except ValueError:
        return None


def dates(first_page: str) -> list[str]:
    """ISO dates written on the first page, in the order they appear, without repeats."""
    hits = [(m.start(), _iso(m[3], _MONTH[m[1].lower()], m[2])) for m in _MDY.finditer(first_page)]
    hits += [(m.start(), _iso(m[3], _MONTH[m[2].lower()], m[1])) for m in _DMY.finditer(first_page)]
    hits += [(m.start(), _iso(m[1], int(m[2]), m[3])) for m in _ISO.finditer(first_page)]
    ordered = [d for _, d in sorted(hits) if d]
    return list(dict.fromkeys(ordered))


# --- the command ---------------------------------------------------------------


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]


def prepared_name(entry: dict[str, Any]) -> str:
    return f"prepared/{entry['sha256'][:16]}-{slug(Path(entry['path']).name)}.txt"


def anchored_text(pages: list[str]) -> str:
    return "".join(f"{page_marker(n)}\n{text.rstrip()}\n" for n, text in enumerate(pages, 1))


def prepare_file(run: Path, pack: Path, entry: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"path": entry["path"], "sha256": entry["sha256"]}
    record |= {"kind": entry["kind"], "prepared": None, "pages": 0, "excerpt": ""}
    record |= {"entities": [], "dates": [], "sheets": [], "image_read": False, "unreadable": None}
    try:
        result = read(pack / entry["path"], entry["kind"])
    except UnreadableError as exc:
        record["unreadable"] = str(exc)
        return record
    name = prepared_name(entry)
    (run / name).write_text(anchored_text(result.pages), encoding="utf-8")
    first = result.pages[0] if result.pages else ""
    record |= {"prepared": name, "pages": len(result.pages), "sheets": result.sheets}
    record |= {"excerpt": " ".join(first.split())[:EXCERPT_CHARS], "image_read": result.image_read}
    record |= {"entities": entities(first), "dates": dates(first)}
    return record


def write(run: Path) -> dict[str, Any]:
    try:
        inventory = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunError(f"{run}: no readable inventory.json; run rbot inventory first") from exc
    (run / "prepared").mkdir(exist_ok=True)
    index_path = run / "prepared" / "index.json"
    pack = Path(inventory["pack_root"])
    kept = {entry["path"]: prepare_file(run, pack, entry) for entry in inventory["files"]}
    index: dict[str, Any] = {"schema": SCHEMA}
    index["generated_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    index["files"] = [kept[p] for p in sorted(kept)]
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index


def load_index(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
    return data


def run_command(args: argparse.Namespace) -> int:
    try:
        index = write(Path(args.run_dir))
    except (RunError, OSError) as exc:
        print(exc)
        return 1
    unreadable = [r for r in index["files"] if r["unreadable"]]
    for r in unreadable:
        print(f"unreadable: {r['path']}: {r['unreadable']}")
    print(f"prepared/index.json: {len(index['files'])} file(s), {len(unreadable)} unreadable")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("prepare", help="write page-anchored text for every inventoried file")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    c.set_defaults(run=run_command)
```

`rbot/scripts/rbotlib/cli.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/cli.py
+++ b/rbot/scripts/rbotlib/cli.py
@@ -10,7 +10,7 @@ import sys
 from datetime import UTC, datetime
 from pathlib import Path
 
-from rbotlib import corpus, inventory
+from rbotlib import corpus, inventory, prepare
 from rbotlib.catalog import check_tree
 from rbotlib.contract import ContractError, load_contract
 from rbotlib.render import render_module
@@ -88,6 +88,7 @@ def main(argv: list[str] | None = None) -> int:
     c.set_defaults(run=_check)
     corpus.add_command(sub)
     inventory.add_command(sub)
+    prepare.add_command(sub)
     args = parser.parse_args(argv)
     result: int = args.run(args)
     run_dir = getattr(args, "run_dir", None)
```

- [ ] **Step 4: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `151 passed, 101 skipped`. With the corpus gate: `101 passed, 151 deselected`, about 80 seconds (the three 170–181-page TEST-Issuer Data PDFs dominate). `test_prepare_pages_and_markers[<pack>]` finds every corpus file readable, every PDF's page count equal to the registry and page markers `1..N`; `test_entity_trap_flagged` finds `SIX FLAGS` named on the mis-filed 10-K in `tid-ford` and `Ford` on the mis-filed 10-K in `tid-six-flags`, and the pack's own issuer named on neither.

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 5: Commit, then open PR 02B (Tasks 3–4)**

```bash
git add rbot tests
git commit -m "intake: rbot prepare for text and PDF with page anchors, entities and dates

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/02a-registry bash scripts/check_pr_size.sh
```

Expected: `785 changed lines (limit 800)`.

Report: test counts, gate and corpus-gate exit codes, PR size. `Not verified:` a scanned PDF from a real pack (none in the corpus; the scan rule is tested on a built PDF without text); an encrypted PDF that needs a password (tested only through pypdf's error path); page anchors for SEC text filings, which have no page breaks.

---

### Task 5: `rbot prepare` for HTML, sheets and images, `--only`, and portfolio JSON

**Files:**
- Create: `rbot/scripts/rbotlib/portfolio.py`, `docs/decisions/0003-openpyxl.md`
- Modify: `rbot/scripts/rbotlib/prepare.py`, `pyproject.toml` (`openpyxl`, `types-openpyxl`), `uv.lock` (regenerated)
- Test: `tests/test_sheets.py`, `tests/test_portfolio.py`, `tests/test_prepare.py`

**Interfaces:**
- Consumes: Task 4's `prepare` module; `rbotlib.rules.load_rules` (the `strategy` scale).
- Produces:
  - `rbotlib.prepare`: `Sheet = tuple[str, list[list[str]]]`; `Prepared.sheets: list[Sheet]`; `clean_cell(value) -> str` (`None`, blanks, `—`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#REF!`, `#NUM!`, `#NULL!` and anything starting `#N/A` become an empty cell, never zero; a midnight `datetime` becomes an ISO date); `read_csv`, `read_xlsx` (stored values only: `load_workbook(path, read_only=True, data_only=True)`), `read_image` (one empty page, `image_read` true), `read_html`; each sheet is one page: `<<< page N >>>`, `<<< sheet NAME >>>`, then its rows as CSV with trailing empty cells and rows trimmed; a page without text is its marker line alone; `write(run, rules, only=None)`; `--only <file>` re-prepares one inventoried file and keeps every other index entry.
  - `prepared/index.json` gains `"portfolios": [{"portfolio_id", "json"}]` and `"portfolio_notes": [str]`; the command prints `portfolio: <note>` per note and `portfolios: <ids or none>`.
  - `rbotlib.portfolio`: `SCHEMA = "rbot-portfolio/1"`; `Portfolio` (meta, positions, limits, unparsed, files); `number(text) -> str | None` (`$630,928,502` → `630928502`, `2.37%` → `2.37`, `4.82 yrs` → `4.82`, `313 bps` → `313`); `parse_limit(text) -> tuple[str, str] | str` (`≤ 2.5% NAV` → `("2.5", "pct_nav")`; units `pct_nav`, `pct_par`, `years`, `amount`, `count`; a minimum limit or wordy limit returns the reason); `read_sheet(source, rows, found) -> str | None`; `to_json(p, rules) -> dict`; `write_all(run, found, rules) -> list[dict]`.
  - `prepared/portfolios/<portfolio_id>.json` exactly as interfaces spec §7 (`portfolio_id`, `portfolio_name`, `strategy`, `as_of`, `nav`, `par`, `currency`, `unit`, `positions[]`, `limits[]` with `scope` ∈ issuer, sector, rating_bucket, country, asset_type, seniority, maturity, currency, other, `unparsed[]`) plus `positions_file` and `limits_file` (the `cp0.portfolios` columns). Recognised layouts: a positions table whose header names `Issuer ID`, `Issuer`, `Par`, `% NAV`; a limits table with the compliance-monitor header `ID`, `Constraint Category`, `Parameter`, `Limit`, `Breach Type`, `Current Value` (the desk's CP-6A layout); key–value rows above either header give `Portfolio ID` (links the two), `Portfolio`, `Strategy`, `As of`, `Currency`, `Unit`, `Total NAV`, `Total Par`. A minimum limit (`≥`), an info-only row or a non-numeric value goes to `unparsed` with its reason: Portfolio Fit (Plan 05) sizes against maximum limits only. A generic limit's `current_value` is the file's (for "largest" limits, the largest issuer's or sector's), so its headroom is a lower bound for any other issuer or sector.

- [ ] **Step 1: Branch for PR 02C and add the workbook dependency (decision record first)**

```bash
git switch -c build/02c-sheets
```

`docs/decisions/0003-openpyxl.md` — create:

```markdown
# 0003 — openpyxl for workbook values

**Need:** `rbot prepare` turns every sheet of an `.xlsx` Source Pack file (the Sector RV Workbook, Bloomberg exports, portfolio files) into CSV rows of stored values, so modules cite cells and `#N/A`-style markers become empty cells (interfaces spec section 8.1, design D15). Plan 03 writes `model.xlsx` with the same library.

**Order of preference (global rule):** CSV files use the standard library `csv` module. The standard library can unzip an `.xlsx` (`zipfile` + `xml.etree`), but resolving shared strings, inline strings, styles-dependent dates, cached formula results and sheet relationships correctly is a parser of its own, more code than this plan's whole intake. No locked dependency reads workbooks. So a new runtime dependency.

**Choice:** `openpyxl` — pure Python, MIT, the reference reader for `.xlsx`, one dependency (`et-xmlfile`, pure Python, MIT), and the library the Copilot spike installs (`pip install --user pypdf openpyxl`, Plan 01 Task 2). Read with `load_workbook(path, read_only=True, data_only=True)`: stored values only, formulas never recalculated (a Bloomberg `BDP` cell keeps its cached result), no macros, no external links. Old binary `.xls` stays unsupported and is listed as unreadable.

**Versions:** `openpyxl==3.1.5` (released 2024-06-28; no known advisory); it pulls `et-xmlfile==2.0.0` (2024-10-25). Dev only: `types-openpyxl==3.1.5.20260827` (released 2026-08-27, typeshed stubs) so `mypy --strict` checks the calls instead of a suppression. All three are older than 30 days on 2026-10-11 and pass `pip-audit --strict`.

**Failure handling:** a workbook openpyxl cannot open (`InvalidFileException`, `BadZipFile`, `KeyError`, `ValueError`, `OSError`) is listed as unreadable with the error text; the rest of the pack is still prepared.
```

`pyproject.toml` — patch:

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,6 +4,7 @@ version = "0.1.0"
 description = "RBOT: leveraged-finance credit research as a GitHub Copilot skill"
 requires-python = ">=3.11"
 dependencies = [
+    "openpyxl==3.1.5",
     "pypdf==6.19.0",
 ]
 
@@ -61,4 +62,5 @@ dev = [
     "pytest>=9.1.1",
     "pytest-cov>=7.1.0",
     "ruff>=0.17.0",
+    "types-openpyxl==3.1.5.20260827",
 ]
```

```bash
uv lock && uv sync
uv run python -c "import openpyxl; print(openpyxl.__version__)"
uv run pip-audit --strict
```

Expected: `3.1.5`; `No known vulnerabilities found`.

- [ ] **Step 2: Write the failing tests**

`tests/test_sheets.py` — create:

```python
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from builders import make_run
from rbotlib.cli import main
from rbotlib.prepare import clean_cell, load_index


def _run(pack: Path) -> tuple[Path, dict[str, dict[str, object]]]:
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run, {str(r["path"]): r for r in load_index(run)["files"]}


def test_spreadsheet_errors_and_blanks_are_empty_cells() -> None:
    for marker in ("#N/A", "#N/A N/A", "#N/A Field Not Applicable", "#VALUE!", "#DIV/0!"):
        assert clean_cell(marker) == ""
    for blank in ("#NAME?", "—", "  "):
        assert clean_cell(blank) == ""
    assert clean_cell(None) == ""
    assert clean_cell(99.5) == "99.5"
    assert clean_cell(True) == "TRUE"
    assert clean_cell(datetime(2026, 10, 2)) == "2026-10-02"
    assert clean_cell(datetime(2026, 10, 2, 9, 30)) == "2026-10-02T09:30:00"


def test_csv_becomes_one_sheet_page_with_markers_emptied(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    csv_text = "SYNTHETIC levels\nTicker,Bid,Ask\nCZR TLB,#N/A,99.75\nMGM 2032,#N/A N/A,\n\n"
    (pack / "levels.csv").write_text(csv_text, encoding="utf-8")
    run, index = _run(pack)
    record = index["levels.csv"]
    assert record["sheets"] == ["levels"] and record["pages"] == 1
    text = (run / str(record["prepared"])).read_text(encoding="utf-8")
    assert text == (
        "<<< page 1 >>>\n<<< sheet levels >>>\nSYNTHETIC levels\nTicker,Bid,Ask\n"
        "CZR TLB,,99.75\nMGM 2032\n"
    )


def test_each_workbook_sheet_is_a_page_of_stored_values(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    book = Workbook()
    rv = book.active
    assert rv is not None
    rv.title = "Gaming"
    rv.append(["SYNTHETIC Sector RV"])
    rv.append(["Company", "Margin", "Mid 3Y DM", "Maturity"])
    rv.append(["Caesars", 225, "#N/A N/A", datetime(2031, 2, 6)])
    book.create_sheet("Index Statistics").append(["Index", "3Y DM"])
    book.save(pack / "rv.xlsx")
    (pack / "broken.xlsx").write_bytes(b"PK not a workbook")
    run, index = _run(pack)
    record = index["rv.xlsx"]
    assert record["sheets"] == ["Gaming", "Index Statistics"] and record["pages"] == 2
    text = (run / str(record["prepared"])).read_text(encoding="utf-8")
    assert "<<< page 1 >>>\n<<< sheet Gaming >>>\nSYNTHETIC Sector RV\n" in text
    assert "Caesars,225,,2031-02-06\n" in text
    assert text.endswith("<<< page 2 >>>\n<<< sheet Index Statistics >>>\nIndex,3Y DM\n")
    assert str(index["broken.xlsx"]["unreadable"]).startswith("openpyxl could not read")


def test_an_image_is_an_image_read_stub(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "SYNTHETIC_Levels_Screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    run, index = _run(pack)
    record = index["SYNTHETIC_Levels_Screenshot.png"]
    assert record["image_read"] is True and record["pages"] == 1 and record["excerpt"] == ""
    assert (run / str(record["prepared"])).read_text(encoding="utf-8") == "<<< page 1 >>>\n"
```

`tests/test_portfolio.py` — create:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest

from builders import make_run
from rbotlib.cli import main
from rbotlib.portfolio import number, parse_limit
from rbotlib.prepare import load_index

POSITIONS = """SYNTHETIC test positions
Portfolio ID,TEST_CLO_I
Portfolio,Test CLO I Ltd
Strategy,CLO
As of,2026-05-29
Currency,USD
Unit,MILLIONS
Total NAV,630.9
Total Par,634.0

Issuer ID,Issuer,Instrument ID,Par,% NAV,Sector,Rating,Country,Currency,Seniority,Asset Type
CZR,Caesars Entertainment,CZR TLB-B1,6.0,0.95%,Gaming,B1,US,USD,Senior secured,Loan
ASU,Asurion,ASU TL,"14.95",2.37%,Insurance,B3,US,USD,Senior secured,Loan
BAD,Broken row,X,n/a,1%,Software,B2,US,USD,Senior secured,Loan
"""
LIMITS = """SYNTHETIC test limits
Portfolio ID,TEST_CLO_I

ID,Constraint Category,Parameter,Limit,Breach Type,Source Document,Current Value
C-01,Single Name,Max single issuer exposure (largest: Asurion),≤ 2.5% NAV,Hard,Indenture,2.37%
C-04,Rating — CCC Bucket,Max CCC+ and below,≤ 7.5% NAV,Hard,Indenture,7.36%
C-07,Sector,2nd largest sector: Commercial Support Services,≤ 10.0% NAV,Soft,Indenture,6.74%
C-09,Instrument,Min 1st Lien / Senior Secured,≥ 90.0% NAV,Hard,Indenture,99.39%
C-10,Instrument,Max 2nd Lien / Unsecured,≤ 10.0% NAV,Soft,Indenture,0.61%
C-11,Duration / Maturity,Max WAL (weighted avg life),≤ 8.0 years,Soft,Indenture,4.82 yrs
C-15,Pricing,WA Mid Price,Info only,—,—,99.578
C-17,ESG / Exclusion,"Excluded sectors (Tobacco, Thermal Coal)",0% NAV,Hard,Indenture,0%
"""


MINIMUM = "minimum limit: Portfolio Fit sizes against maximum limits only"


def _prepare(tmp_path: Path, files: dict[str, str]) -> tuple[Path, list[str]]:
    pack = tmp_path / "pack"
    pack.mkdir()
    for name, text in files.items():
        (pack / name).write_text(text, encoding="utf-8")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run, load_index(run)["portfolio_notes"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("$630,928,502", "630928502"), ("2.37%", "2.37"), ("4.82 yrs", "4.82"), ("313 bps", "313")],
)
def test_numbers_lose_their_symbols_but_keep_their_digits(text: str, expected: str) -> None:
    assert number(text) == expected


def test_words_are_not_numbers() -> None:
    assert number("B1 (14.3)") is None
    assert number("n/a") is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("≤ 2.5% NAV", ("2.5", "pct_nav")),
        ("<= 15.0% par", ("15.0", "pct_par")),
        ("≤ 8.0 years", ("8.0", "years")),
        ("≤ $25,000,000", ("25000000", "amount")),
        ("≤ 25", ("25", "count")),
        ("0% NAV", ("0", "pct_nav")),
    ],
)
def test_maximum_limits_parse_to_value_and_unit(text: str, expected: tuple[str, str]) -> None:
    assert parse_limit(text) == expected


def test_minimum_and_wordy_limits_give_a_reason() -> None:
    assert (
        parse_limit("≥ 90.0% NAV")
        == "minimum limit: Portfolio Fit sizes against maximum limits only"
    )
    assert (
        parse_limit("≥ Caa1 (numeric ≤ 17)")
        == "limit '≥ Caa1 (numeric ≤ 17)' is not a number with a unit"
    )


def test_positions_and_limits_become_one_portfolio_json(tmp_path: Path) -> None:
    run, notes = _prepare(tmp_path, {"positions.csv": POSITIONS, "limits.csv": LIMITS})
    assert notes == []
    data = json.loads((run / "prepared" / "portfolios" / "TEST_CLO_I.json").read_text())
    assert data["schema"] == "rbot-portfolio/1"
    assert (data["portfolio_name"], data["strategy"], data["as_of"]) == (
        "Test CLO I Ltd",
        "CLO",
        "2026-05-29",
    )
    assert (data["nav"], data["par"], data["currency"], data["unit"]) == (
        "630.9",
        "634.0",
        "USD",
        "MILLIONS",
    )
    assert (data["positions_file"], data["limits_file"]) == ("positions.csv", "limits.csv")
    assert data["positions"][0] == {
        "issuer_id": "CZR",
        "issuer_name": "Caesars Entertainment",
        "instrument_id": "CZR TLB-B1",
        "par": "6.0",
        "pct_nav": "0.95",
        "sector": "Gaming",
        "rating": "B1",
        "country": "US",
        "currency": "USD",
        "seniority": "Senior secured",
        "asset_type": "Loan",
    }
    scopes = {lim["limit_id"]: (lim["scope"], lim["scope_value"]) for lim in data["limits"]}
    assert scopes == {
        "C-01": ("issuer", None),
        "C-04": ("rating_bucket", "CCC"),
        "C-07": ("sector", "Commercial Support Services"),
        "C-10": ("seniority", "2nd Lien / Unsecured"),
        "C-11": ("other", None),
        "C-17": ("sector", "Tobacco, Thermal Coal"),
    }
    first = data["limits"][0]
    assert (first["limit_value"], first["unit"], first["limit_kind"]) == ("2.5", "pct_nav", "Hard")
    assert (first["current_value"], first["source"]) == ("2.37", "limits.csv row 5")
    assert data["unparsed"] == [
        {"row": "limits.csv row 8", "reason": MINIMUM},
        {
            "row": "limits.csv row 11",
            "reason": "no Hard or Soft breach type (info only)",
        },
        {"row": "positions.csv row 14", "reason": "par or % NAV is not a number"},
    ]
    index = load_index(run)
    assert index["portfolios"] == [
        {"portfolio_id": "TEST_CLO_I", "json": "prepared/portfolios/TEST_CLO_I.json"}
    ]


def test_an_unlinked_table_is_a_note_and_bad_totals_are_unparsed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    orphan = LIMITS.replace("Portfolio ID,TEST_CLO_I\n", "")
    bad = POSITIONS.replace("Total NAV,630.9", "Total NAV,lots").replace(
        "Strategy,CLO", "Strategy,Hedge"
    )
    run, notes = _prepare(tmp_path, {"limits.csv": orphan, "positions.csv": bad})
    assert notes == ["limits.csv: limits table without a Portfolio ID row; not linked"]
    assert (
        "portfolio: limits.csv: limits table without a Portfolio ID row" in capsys.readouterr().out
    )
    data = json.loads((run / "prepared" / "portfolios" / "TEST_CLO_I.json").read_text())
    assert data["nav"] == "" and data["limits"] == []
    assert {"row": "Total NAV", "reason": "missing or not a number"} in data["unparsed"]
    assert {"row": "Strategy", "reason": "'Hedge' is not a Strategy"} in data["unparsed"]
```

`tests/test_prepare.py` — patch:

```diff
--- a/tests/test_prepare.py
+++ b/tests/test_prepare.py
@@ -35,12 +35,14 @@ def _text(run: Path, record: dict[str, Any]) -> str:
     return (run / str(record["prepared"])).read_text(encoding="utf-8")
 
 
-def test_text_and_markdown_become_page_anchored_text(tmp_path: Path) -> None:
+def test_text_markdown_and_html_become_page_anchored_text(tmp_path: Path) -> None:
+    html = b"<html><style>p{}</style><p>Net revenue</p><table><tr><td>Q2</td><td>2,993</td></tr>"
     run, index = _prepared(
         tmp_path,
         {
             "CZR_10Q.txt": (SEC_COVER + "\fpage two text\n").encode(),
-            "note.md": b"# Note\nOne page.\n",
+            "note.md": b"# Note\nOne page only.\n",
+            "release.html": html + b"</table><script>alert(1)</script></html>",
         },
     )
     tenq = index["CZR_10Q.txt"]
@@ -50,7 +52,8 @@ def test_text_and_markdown_become_page_anchored_text(tmp_path: Path) -> None:
     assert tenq["entities"] == ["CAESARS ENTERTAINMENT, INC."]
     assert tenq["dates"] == ["2026-06-30"]
     assert tenq["excerpt"].startswith("Commission File No. 001-36629 CAESARS ENTERTAINMENT, INC.")
-    assert _text(run, index["note.md"]) == "<<< page 1 >>>\n# Note\nOne page.\n"
+    assert _text(run, index["note.md"]) == "<<< page 1 >>>\n# Note\nOne page only.\n"
+    assert _text(run, index["release.html"]) == "<<< page 1 >>>\nNet revenue\n| Q2 | 2,993\n"
 
 
 def test_pdf_pages_scans_and_unreadable_files(tmp_path: Path) -> None:
@@ -81,7 +84,18 @@ def test_prepare_reports_unreadable_files_and_still_exits_0(
     _prepared(tmp_path, {"a.txt": b"text\n", "memo.docx": b"PK"})
     out = capsys.readouterr().out
     assert "unreadable: memo.docx: no reader for .docx files\n" in out
-    assert out.endswith("prepared/index.json: 2 file(s), 1 unreadable\n")
+    assert "prepared/index.json: 2 file(s), 1 unreadable\n" in out
+
+
+def test_only_reprepares_one_file_and_keeps_the_rest(tmp_path: Path) -> None:
+    run, index = _prepared(tmp_path, {"a.txt": b"first\n", "b.txt": b"second\n"})
+    (tmp_path / "pack" / "b.txt").write_text("second, edited\n", encoding="utf-8")
+    assert main(["inventory", "--run", str(run)]) == 0
+    assert main(["prepare", "--run", str(run), "--only", "b.txt"]) == 0
+    again = {r["path"]: r for r in load_index(run)["files"]}
+    assert again["a.txt"] == index["a.txt"]
+    assert _text(run, again["b.txt"]) == "<<< page 1 >>>\nsecond, edited\n"
+    assert main(["prepare", "--run", str(run), "--only", "nope.txt"]) == 1
 
 
 def test_prepare_without_an_inventory_exits_1(
@@ -127,6 +141,9 @@ def test_prepare_pages_and_markers(pack_id: str, prepared_run: Callable[[str], P
         text = _text(run, record)
         markers = [int(n) for n in re.findall(r"^<<< page (\d+) >>>$", text, re.M)]
         assert markers == list(range(1, record["pages"] + 1)), f.path
+        if record["kind"] in ("csv", "xlsx"):
+            assert not re.search(r"#N/A|#VALUE!|#DIV/0!|#NAME\?", text), f.path
+        assert record["image_read"] is (record["kind"] == "image"), f.path
 
 
 @pytest.mark.corpus
```

- [ ] **Step 3: Run them to see them fail**

Run: `uv run pytest --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'rbotlib.portfolio'` (`tests/test_portfolio.py`) and `ImportError: cannot import name 'clean_cell' from 'rbotlib.prepare'` (`tests/test_sheets.py`).

- [ ] **Step 4: Write the portfolio reader and extend the preparer**

`rbot/scripts/rbotlib/portfolio.py` — create:

```python
"""Portfolio Context to `prepared/portfolios/<portfolio_id>.json` (interfaces spec section 7).

A sheet (CSV or workbook tab) is a positions table when its header row names Issuer ID,
Issuer, Par and % NAV, and a limits table when it names the compliance-monitor columns
ID, Constraint Category, Parameter, Limit, Breach Type and Current Value. Key-value
rows above the header give the portfolio: Portfolio ID (required to link the two),
Portfolio, Strategy, As of, Currency, Unit, Total NAV and Total Par. Amounts keep the
file's unit. Rows RBOT cannot use are kept under `unparsed` with the reason, never dropped.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from rbotlib.rules import Rules

SCHEMA = "rbot-portfolio/1"
POSITIONS = ("issuer id", "issuer", "par", "% nav")
LIMITS = ("id", "constraint category", "parameter", "limit", "breach type", "current value")
META = {
    "portfolio id": "portfolio_id",
    "portfolio": "portfolio_name",
    "strategy": "strategy",
    "as of": "as_of",
    "currency": "currency",
    "unit": "unit",
    "total nav": "nav",
    "total par": "par",
}
POSITION_COLUMNS = {
    "issuer id": "issuer_id",
    "issuer": "issuer_name",
    "instrument id": "instrument_id",
    "par": "par",
    "% nav": "pct_nav",
    "sector": "sector",
    "rating": "rating",
    "country": "country",
    "currency": "currency",
    "seniority": "seniority",
    "asset type": "asset_type",
}
_LIMIT = re.compile(
    r"^(?P<op>≤|<=|<|≥|>=|>)?\s*(?P<cur>\$)?(?P<num>\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>%\s*nav|%\s*par|years?|yrs?)?$",
    re.I,
)


@dataclass
class Portfolio:
    meta: dict[str, str] = field(default_factory=dict)
    positions: list[dict[str, str]] = field(default_factory=list)
    limits: list[dict[str, Any]] = field(default_factory=list)
    unparsed: list[dict[str, str]] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)


def _norm(cell: str) -> str:
    return " ".join(cell.casefold().split())


def number(text: str) -> str | None:
    """A plain decimal from `$630,928,502`, `2.37%`, `4.82 yrs` or `313 bps`; else None."""
    match = re.match(r"^\$?(-?\d[\d,]*(?:\.\d+)?)\s*(%|yrs?|years?|bps)?$", text.strip(), re.I)
    if not match:
        return None
    try:
        return str(Decimal(match.group(1).replace(",", "")))
    except InvalidOperation:
        return None


def parse_limit(text: str) -> tuple[str, str] | str:
    """(`limit_value`, `unit`) for a maximum limit, or the reason it cannot be sized against."""
    match = _LIMIT.match(text.strip())
    if not match:
        return f"limit {text!r} is not a number with a unit"
    if match["op"] in ("≥", ">=", ">"):
        return "minimum limit: Portfolio Fit sizes against maximum limits only"
    unit = _norm(match["unit"] or "").replace(" ", "")
    units = {"%nav": "pct_nav", "%par": "pct_par", "year": "years", "years": "years"}
    kind = units.get(unit) or ("years" if unit.startswith("yr") else None)
    kind = kind or ("amount" if match["cur"] else "count")
    return str(Decimal(match["num"].replace(",", ""))), kind


def _scope(category: str, parameter: str) -> tuple[str, str | None]:
    c = _norm(category)
    named = re.search(r"(?:\(largest:[^)]*\)|sector:\s*(?P<s>.+)|\((?P<x>[^)]*)\))", parameter)
    if c in ("single name", "issuer"):
        return "issuer", None
    if c.startswith("rating"):
        bucket = category.split("—")[-1].strip()
        return "rating_bucket", "CCC" if "ccc" in bucket.casefold() else bucket
    if c.startswith("sector") or "exclusion" in c:
        value = named and (named["s"] or named["x"])
        return "sector", value.strip() if value else None
    if c.startswith("instrument"):
        return "seniority", re.sub(r"^(max|min)\s+", "", parameter, flags=re.I).strip()
    for scope in ("country", "currency", "asset_type", "seniority"):
        if c == scope.replace("_", " "):
            return scope, None
    return "other", None


def _header(rows: list[list[str]], required: tuple[str, ...]) -> int | None:
    for i, row in enumerate(rows):
        if set(required) <= {_norm(c) for c in row}:
            return i
    return None


def _meta(rows: list[list[str]]) -> dict[str, str]:
    found = {}
    for row in rows:
        cells = [c for c in row if c]
        if len(cells) == 2 and _norm(cells[0]) in META:
            found[META[_norm(cells[0])]] = cells[1]
    return found


def _positions(source: str, rows: list[list[str]], start: int, p: Portfolio) -> None:
    columns = [POSITION_COLUMNS.get(_norm(c)) for c in rows[start]]
    for n, row in enumerate(rows[start + 1 :], start + 2):
        if not any(row):
            continue
        item = {key: cell for key, cell in zip(columns, row, strict=False) if key}
        par, pct = number(item.get("par", "")), number(item.get("pct_nav", ""))
        if par is None or pct is None:
            p.unparsed.append(
                {"row": f"{source} row {n}", "reason": "par or % NAV is not a number"}
            )
            continue
        p.positions.append(item | {"par": par, "pct_nav": pct})


def _limit_row(source: str, n: int, item: dict[str, str]) -> dict[str, Any] | str:
    kind = item.get("breach type", "")
    if kind not in ("Hard", "Soft"):
        return "no Hard or Soft breach type (info only)"
    parsed = parse_limit(item.get("limit", ""))
    if isinstance(parsed, str):
        return parsed
    current = number(item.get("current value", ""))
    if current is None:
        return f"current value {item.get('current value', '')!r} is not a number"
    scope, scope_value = _scope(item.get("constraint category", ""), item.get("parameter", ""))
    return {
        "limit_id": item.get("id", ""),
        "category": item.get("constraint category", ""),
        "parameter": item.get("parameter", ""),
        "scope": scope,
        "scope_value": scope_value,
        "limit_value": parsed[0],
        "unit": parsed[1],
        "limit_kind": kind,
        "current_value": current,
        "source": f"{source} row {n}",
    }


def _limits(source: str, rows: list[list[str]], start: int, p: Portfolio) -> None:
    header = [_norm(c) for c in rows[start]]
    for n, row in enumerate(rows[start + 1 :], start + 2):
        if not any(row):
            continue
        result = _limit_row(source, n, dict(zip(header, row, strict=False)))
        if isinstance(result, str):
            p.unparsed.append({"row": f"{source} row {n}", "reason": result})
        else:
            p.limits.append(result)


def read_sheet(source: str, rows: list[list[str]], found: dict[str, Portfolio]) -> str | None:
    """Add a positions or limits sheet to its portfolio; a note when it cannot be linked."""
    for kind, required in (("positions", POSITIONS), ("limits", LIMITS)):
        start = _header(rows, required)
        if start is None:
            continue
        meta = _meta(rows[:start])
        portfolio_id = meta.get("portfolio_id")
        if not portfolio_id:
            return f"{source}: {kind} table without a Portfolio ID row; not linked"
        p = found.setdefault(portfolio_id, Portfolio())
        p.meta.update(meta)
        p.files[kind] = source
        (_positions if kind == "positions" else _limits)(source, rows, start, p)
    return None


def to_json(p: Portfolio, rules: Rules) -> dict[str, Any]:
    meta, unparsed = dict(p.meta), list(p.unparsed)
    for key in ("nav", "par"):
        value = number(meta.get(key, ""))
        if value is None:
            unparsed.append({"row": f"Total {key.upper()}", "reason": "missing or not a number"})
        meta[key] = value or ""
    if meta.get("strategy") not in rules.scales["strategy"]:
        unparsed.append(
            {"row": "Strategy", "reason": f"{meta.get('strategy')!r} is not a Strategy"}
        )
    data: dict[str, Any] = {"schema": SCHEMA}
    for key in ("portfolio_id", "portfolio_name", "strategy", "as_of", "nav", "par"):
        data[key] = meta.get(key, "")
    data |= {"currency": meta.get("currency", ""), "unit": meta.get("unit", "")}
    data["positions_file"] = p.files.get("positions", "")
    data["limits_file"] = p.files.get("limits", "")
    return data | {"positions": p.positions, "limits": p.limits, "unparsed": unparsed}


def write_all(run: Path, found: dict[str, Portfolio], rules: Rules) -> list[dict[str, str]]:
    folder = run / "prepared" / "portfolios"
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for portfolio_id in sorted(found):
        data = to_json(found[portfolio_id], rules)
        name = f"prepared/portfolios/{portfolio_id}.json"
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        (run / name).write_text(text, encoding="utf-8")
        written.append({"portfolio_id": portfolio_id, "json": name})
    return written
```

`rbot/scripts/rbotlib/prepare.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/prepare.py
+++ b/rbot/scripts/rbotlib/prepare.py
@@ -11,18 +11,26 @@ and the reason; the others are still prepared (exit 0).
 from __future__ import annotations
 
 import argparse
+import csv
+import io
 import json
 import re
 from collections.abc import Callable
 from dataclasses import dataclass, field
 from datetime import UTC, date, datetime
+from html.parser import HTMLParser
 from pathlib import Path
 from typing import Any
+from zipfile import BadZipFile
 
+from openpyxl import load_workbook
+from openpyxl.utils.exceptions import InvalidFileException
 from pypdf import PdfReader
 from pypdf.errors import PyPdfError
 
+from rbotlib import portfolio
 from rbotlib.inventory import RunError
+from rbotlib.rules import Rules, load_rules
 
 SCHEMA = "rbot-prepared/1"
 EXCERPT_CHARS = 400
@@ -34,10 +42,13 @@ class UnreadableError(Exception):
     """This file cannot be prepared; the message is recorded as `unreadable`."""
 
 
+Sheet = tuple[str, list[list[str]]]  # sheet name, rows of cleaned cells
+
+
 @dataclass
 class Prepared:
     pages: list[str]
-    sheets: list[str] = field(default_factory=list)
+    sheets: list[Sheet] = field(default_factory=list)
     image_read: bool = False
 
 
@@ -54,6 +65,38 @@ def read_text(path: Path) -> Prepared:
     return Prepared(text.split("\f"))
 
 
+class _HTMLText(HTMLParser):
+    BLOCKS = frozenset({"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table", "section"})
+
+    def __init__(self) -> None:
+        super().__init__(convert_charrefs=True)
+        self.parts: list[str] = []
+        self.hidden = 0
+
+    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
+        if tag in ("script", "style"):
+            self.hidden += 1
+        elif tag in self.BLOCKS:
+            self.parts.append("\n")
+        elif tag in ("td", "th"):
+            self.parts.append(" | ")
+
+    def handle_endtag(self, tag: str) -> None:
+        if tag in ("script", "style"):
+            self.hidden -= 1
+
+    def handle_data(self, data: str) -> None:
+        if not self.hidden:
+            self.parts.append(data)
+
+
+def read_html(path: Path) -> Prepared:
+    parser = _HTMLText()
+    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
+    lines = (" ".join(line.split()) for line in "".join(parser.parts).splitlines())
+    return Prepared(["\n".join(line for line in lines if line)])
+
+
 def read_pdf(path: Path) -> Prepared:
     """PDF pages through pypdf; a PDF with (almost) no extractable text is a scan."""
     try:
@@ -68,10 +111,81 @@ def read_pdf(path: Path) -> Prepared:
     return Prepared(pages)
 
 
+_ERRORS = frozenset({"#VALUE!", "#DIV/0!", "#NAME?", "#REF!", "#NUM!", "#NULL!", "—"})
+
+
+def clean_cell(value: object) -> str:
+    """One cell as text: spreadsheet errors, `#N/A…`, `—` and blanks are an empty cell."""
+    if value is None:
+        return ""
+    if isinstance(value, bool):
+        return "TRUE" if value else "FALSE"
+    if isinstance(value, datetime):
+        return (
+            value.date().isoformat() if value.time() == datetime.min.time() else value.isoformat()
+        )
+    text = str(value).strip()
+    return "" if text in _ERRORS or text.startswith("#N/A") else text
+
+
+def _trimmed(rows: list[list[str]]) -> list[list[str]]:
+    out = []
+    for row in rows:
+        while row and not row[-1]:
+            row = row[:-1]
+        out.append(row)
+    while out and not out[-1]:
+        out.pop()
+    return out
+
+
+def _sheet_pages(sheets: list[Sheet]) -> Prepared:
+    pages = []
+    for name, rows in sheets:
+        buffer = io.StringIO()
+        csv.writer(buffer, lineterminator="\n").writerows(rows)
+        pages.append(f"<<< sheet {name} >>>\n{buffer.getvalue()}")
+    return Prepared(pages, sheets)
+
+
+def read_csv(path: Path) -> Prepared:
+    text = path.read_text(encoding="utf-8-sig", errors="replace")
+    rows = [[clean_cell(c) for c in row] for row in csv.reader(io.StringIO(text))]
+    return _sheet_pages([(path.stem, _trimmed(rows))])
+
+
+def read_xlsx(path: Path) -> Prepared:
+    """Every sheet's stored values (formula results as cached, never recalculated)."""
+    try:
+        book = load_workbook(path, read_only=True, data_only=True)
+    except (InvalidFileException, BadZipFile, KeyError, ValueError, OSError) as exc:
+        raise UnreadableError(f"openpyxl could not read the workbook: {exc}") from exc
+    try:
+        sheets = [
+            (
+                ws.title,
+                _trimmed([[clean_cell(c) for c in row] for row in ws.iter_rows(values_only=True)]),
+            )
+            for ws in book.worksheets
+        ]
+    finally:
+        book.close()
+    return _sheet_pages(sheets)
+
+
+def read_image(path: Path) -> Prepared:
+    """An image has no text: one empty page, flagged so its figures are Image-Read Values."""
+    return Prepared([""], image_read=True)
+
+
 READERS: dict[str, Callable[[Path], Prepared]] = {
     "txt": read_text,
     "md": read_text,
+    "html": read_html,
     "pdf": read_pdf,
+    "csv": read_csv,
+    "xlsx": read_xlsx,
+    "image": read_image,
 }
 
 
@@ -151,7 +265,9 @@ def prepared_name(entry: dict[str, Any]) -> str:
 
 
 def anchored_text(pages: list[str]) -> str:
-    return "".join(f"{page_marker(n)}\n{text.rstrip()}\n" for n, text in enumerate(pages, 1))
+    """Each page under its `<<< page N >>>` line; a page without text is the line alone."""
+    bodies = (text.rstrip() for text in pages)
+    return "".join(f"{page_marker(n)}\n" + (f"{b}\n" if b else "") for n, b in enumerate(bodies, 1))
 
 
 def prepare_file(run: Path, pack: Path, entry: dict[str, Any]) -> dict[str, Any]:
@@ -166,24 +282,49 @@ def prepare_file(run: Path, pack: Path, entry: dict[str, Any]) -> dict[str, Any]
     name = prepared_name(entry)
     (run / name).write_text(anchored_text(result.pages), encoding="utf-8")
     first = result.pages[0] if result.pages else ""
-    record |= {"prepared": name, "pages": len(result.pages), "sheets": result.sheets}
+    sheets = [n for n, _ in result.sheets]
+    record |= {"prepared": name, "pages": len(result.pages), "sheets": sheets}
     record |= {"excerpt": " ".join(first.split())[:EXCERPT_CHARS], "image_read": result.image_read}
     record |= {"entities": entities(first), "dates": dates(first)}
     return record
 
 
-def write(run: Path) -> dict[str, Any]:
+def _portfolios(run: Path, pack: Path, files: list[dict[str, Any]], rules: Rules) -> dict[str, Any]:
+    """Every portfolio found in the pack's sheets, written to prepared/portfolios/."""
+    found: dict[str, portfolio.Portfolio] = {}
+    notes = []
+    for entry in (e for e in files if e["kind"] in ("csv", "xlsx")):
+        try:
+            sheets = read(pack / entry["path"], entry["kind"]).sheets
+        except UnreadableError:
+            continue  # already listed as unreadable in index.json
+        for name, rows in sheets:
+            label = entry["path"] if entry["kind"] == "csv" else f"{entry['path']} sheet {name}"
+            note = portfolio.read_sheet(label, rows, found)
+            notes += [note] if note else []
+    return {"portfolios": portfolio.write_all(run, found, rules), "portfolio_notes": notes}
+
+
+def write(run: Path, rules: Rules, only: str | None = None) -> dict[str, Any]:
     try:
         inventory = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
     except (OSError, json.JSONDecodeError) as exc:
         raise RunError(f"{run}: no readable inventory.json; run rbot inventory first") from exc
+    entries = [e for e in inventory["files"] if only is None or e["path"] == only]
+    if only is not None and not entries:
+        raise RunError(f"{only}: not in inventory.json")
     (run / "prepared").mkdir(exist_ok=True)
     index_path = run / "prepared" / "index.json"
+    kept = {}
+    if only is not None and index_path.is_file():
+        kept = {r["path"]: r for r in json.loads(index_path.read_text(encoding="utf-8"))["files"]}
     pack = Path(inventory["pack_root"])
-    kept = {entry["path"]: prepare_file(run, pack, entry) for entry in inventory["files"]}
+    for entry in entries:
+        kept[entry["path"]] = prepare_file(run, pack, entry)
     index: dict[str, Any] = {"schema": SCHEMA}
     index["generated_at"] = datetime.now(UTC).isoformat(timespec="seconds")
     index["files"] = [kept[p] for p in sorted(kept)]
+    index |= _portfolios(run, pack, inventory["files"], rules)
     index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
     return index
 
@@ -195,18 +336,23 @@ def load_index(run: Path) -> dict[str, Any]:
 
 def run_command(args: argparse.Namespace) -> int:
     try:
-        index = write(Path(args.run_dir))
+        index = write(Path(args.run_dir), load_rules(args.root), args.only)
     except (RunError, OSError) as exc:
         print(exc)
         return 1
     unreadable = [r for r in index["files"] if r["unreadable"]]
     for r in unreadable:
         print(f"unreadable: {r['path']}: {r['unreadable']}")
+    for note in index["portfolio_notes"]:
+        print(f"portfolio: {note}")
+    found = ", ".join(p["portfolio_id"] for p in index["portfolios"]) or "none"
     print(f"prepared/index.json: {len(index['files'])} file(s), {len(unreadable)} unreadable")
+    print(f"portfolios: {found}")
     return 0
 
 
 def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
     c = sub.add_parser("prepare", help="write page-anchored text for every inventoried file")
     c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
+    c.add_argument("--only", help="prepare one file (its path as in inventory.json)")
     c.set_defaults(run=run_command)
```

- [ ] **Step 5: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `170 passed, 101 skipped`. With the corpus gate: `101 passed, 170 deselected`; `test_prepare_pages_and_markers` now also asserts that no prepared sheet holds a spreadsheet error marker and that only images are `image_read` (the corpus gains sheets and an image in Task 8).

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 6: Commit**

```bash
git add rbot tests pyproject.toml uv.lock docs/decisions/0003-openpyxl.md
git commit -m "intake: prepare HTML, sheets and images; --only; portfolio JSON; openpyxl (decision 0003)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report: test counts, gate and corpus-gate exit codes. `Not verified:` a real analyst positions export (no real layout was available; the parser reads the layout the synthetic pack defines); `.xls` binary workbooks (listed unreadable by design); workbooks whose cached formula values are missing (they read as empty cells).

---

### Task 6: Plan 01 amendments A8 and A9 and review deferral M5: the Handoff parser

The controller added these to Plan 02 (planning ledger, 2026-10-11): citation excerpts quoted from the caos `.txt` filings are pipe-delimited tables, and the parser must not lose a table or a key a model writes slightly differently.

**Files:**
- Modify: `rbot/scripts/rbotlib/handoff.py`, `rbot/scripts/rbotlib/validate.py`, `rbot/scripts/rbotlib/render.py`
- Test: `tests/test_handoff.py`, `tests/test_validate.py`, `tests/test_render.py`

**Interfaces:**
- Consumes: Plan 01's `rbotlib.handoff.parse` and public `cells(line)`, `validate.check` (its `_outside_citation_rows` matches citation rows by `cells`), `render_module`.
- Produces:
  - **A8:** a table cell may hold a literal pipe written `\|`; `cells` (and so `parse`) splits rows only on unescaped pipes and returns the cell with `|` (a backslash not before a pipe stays as written). The validator's exclusion of citation-table rows from marker counting compares lines as `cells`, so a citation row whose excerpt holds `\|` still cannot cite itself (ledger note for A8; a test proves it). Every generated MODULE.md tells modules: "Write a literal pipe inside any cell, excerpts included, as `\|`." Task 10's Run Brief writes cells the same way.
  - **A9:** the separator row accepts GitHub's short cells (`|-|`, `| :- | -: |`); a `<!-- table: … -->` tag whose id is not `[A-Za-z0-9_.-]+` is kept in `Handoff.invalid_tags: list[str]` (new field, default empty) and the validator reports it as `invalid_tag` (exit 2), never drops it; lines inside fenced code blocks (``` or ~~~) are neither H2 sections nor tags; a duplicate or empty front-matter key raises `HandoffError` naming it.
  - **M5:** a table whose header or separator line is indented four or more spaces (a tab counts as four) is an indented code block, not a table: its tag is reported as `orphan_tag`.

- [ ] **Step 1: Write the failing tests**

`tests/test_handoff.py` — patch:

`````diff
--- a/tests/test_handoff.py
+++ b/tests/test_handoff.py
@@ -48,3 +48,64 @@ def test_a_header_without_separator_is_not_a_table() -> None:
 
 def test_markers_finds_every_citation_id() -> None:
     assert markers("a [C1] b [C12] c [C1] [X3]") == {"C1", "C12"}
+
+
+def _one_table(row: str, separator: str = "|---|---|") -> list[list[str]]:
+    text = f"---\nk: v\n---\n<!-- table: t -->\n| a | b |\n{separator}\n{row}\n"
+    return parse(text).tables["t"].rows
+
+
+@pytest.mark.parametrize(
+    ("row", "cells"),
+    [
+        (r"| Net revenues \| 11,486 | p.1 |", ["Net revenues | 11,486", "p.1"]),
+        (r"| a\|b\|c | d |", ["a|b|c", "d"]),
+        ("| C:\\ | d |", ["C:\\", "d"]),
+        ("| x | ends with \\|", ["x", "ends with |"]),
+    ],
+)
+def test_an_escaped_pipe_stays_inside_its_cell(row: str, cells: list[str]) -> None:
+    assert _one_table(row) == [cells]
+
+
+@pytest.mark.parametrize("separator", ["|-|-|", "| :- | -: |", "|---|:---:|", "-|-"])
+def test_short_github_separators_are_accepted(separator: str) -> None:
+    assert _one_table("| 1 | 2 |", separator) == [["1", "2"]]
+
+
+@pytest.mark.parametrize("tag", ["cp1 model", "cp1/model", ""])
+def test_a_tag_with_an_invalid_id_is_reported(tag: str) -> None:
+    h = parse(f"---\nk: v\n---\n<!-- table: {tag} -->\n| x |\n|---|\n| 1 |\n")
+    assert h.invalid_tags == [tag]
+    assert h.tables == {}
+
+
+@pytest.mark.parametrize("fence", ["```", "````markdown", "~~~"])
+def test_fenced_blocks_hold_no_sections_or_tags(fence: str) -> None:
+    close = fence.rstrip("markdown")
+    text = (
+        "---\nk: v\n---\n## Analysis\n"
+        f"{fence}\n## Not a section\n<!-- table: hidden -->\n| x |\n|---|\n| 1 |\n{close}\n"
+        "## Tables\n"
+    )
+    h = parse(text)
+    assert h.sections == ["Analysis", "Tables"]
+    assert h.tables == {} and h.orphan_tags == [] and h.invalid_tags == []
+
+
+@pytest.mark.parametrize(
+    ("front", "message"),
+    [
+        ("module_id: CP-X\nmodule_id: CP-Y", "front matter key 'module_id' appears twice"),
+        (": no key", "front matter line is not key: value"),
+    ],
+)
+def test_duplicate_or_empty_front_matter_keys_are_refused(front: str, message: str) -> None:
+    with pytest.raises(HandoffError, match=message):
+        parse(f"---\n{front}\n---\nbody\n")
+
+
+@pytest.mark.parametrize(("indent", "orphans"), [("   ", []), ("    ", ["t"]), ("  \t", ["t"])])
+def test_a_table_indented_four_spaces_is_a_code_block(indent: str, orphans: list[str]) -> None:
+    h = parse(f"---\nk: v\n---\n<!-- table: t -->\n{indent}| x |\n{indent}|---|\n| 1 |\n")
+    assert (h.orphan_tags, set(h.tables)) == (orphans, set() if orphans else {"t"})
`````

`tests/test_validate.py` — patch:

```diff
--- a/tests/test_validate.py
+++ b/tests/test_validate.py
@@ -66,6 +66,7 @@ def test_another_modules_handoff_exits_4(
         ),
         ("<!-- table: citations -->", "<!-- table: cites -->", "table_missing"),
         ("## Gaps", "<!-- table: nothing -->\n\n## Gaps", "orphan_tag"),
+        ("## Gaps", "<!-- table: bad id -->\n\n## Gaps", "invalid_tag"),
     ],
 )
 def test_each_defect_is_named(
@@ -159,6 +160,15 @@ def test_a_citation_that_cites_itself_is_unused(
     assert "unused_citation" in found
 
 
+def test_a_citation_row_with_an_escaped_pipe_still_cannot_cite_itself(
+    handoff_text: str, contract: Contract, rules: Rules
+) -> None:
+    piped = handoff_text.replace("revenue was 100 |", r"Net revenues \| 100 |")
+    assert check(piped, contract, rules) == (EXIT_VALID, [])
+    text = piped.replace("period [C1].", "period.").replace(r"\| 100 |", r"\| 100 [C1] |")
+    assert codes(text, contract, rules) == (EXIT_MALFORMED, {"unused_citation"})
+
+
 def test_a_marker_inside_another_table_still_counts(
     handoff_text: str, contract: Contract, rules: Rules
 ) -> None:
```

`tests/test_render.py` — patch:

```diff
--- a/tests/test_render.py
+++ b/tests/test_render.py
@@ -23,6 +23,7 @@ def test_module_md_carries_the_contract_and_the_checked_rules(rules: Rules) -> N
     assert "<!-- table: citations -->\n| id | source | locator | excerpt |" in text
     assert "Each citation id appears on exactly one row." in text
     assert "- No investment opinion." in text
+    assert "- Write a literal pipe inside any cell, excerpts included, as `\\|`." in text
     assert "rbot.py validate handoffs/CP-X.md --module CP-X" in text
     for placeholder in rules.placeholders:
         assert placeholder in text
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_handoff.py tests/test_validate.py tests/test_render.py --no-cov`
Expected: FAIL — `19 failed, 55 passed`: the escaped-pipe, short-separator, invalid-tag, fenced-block, front-matter and indented-table (M5) cases, the `invalid_tag` finding, the escaped-pipe citation row that cites itself, and the MODULE.md pipe rule.

- [ ] **Step 3: Amend the parser, the validator and the generator**

`rbot/scripts/rbotlib/handoff.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/handoff.py
+++ b/rbot/scripts/rbotlib/handoff.py
@@ -2,18 +2,24 @@
 
 A Handoff is Markdown: flat `key: value` front matter between `---` lines,
 H2 sections, tagged tables (`<!-- table: <id> -->` then a GitHub table, blank
-lines allowed between) and citation markers `[C<n>]`.
+lines allowed between) and citation markers `[C<n>]`. A literal pipe inside
+a cell is written as a backslash and a pipe (amendment A8). Fenced code blocks
+hold no sections or tags (A9); a table indented 4+ spaces is code, not a table.
 """
 
 from __future__ import annotations
 
 import re
-from dataclasses import dataclass
+from dataclasses import dataclass, field
 
-_TABLE_TAG = re.compile(r"^<!--\s*table:\s*([A-Za-z0-9_.\-]+)\s*-->$")
+_TABLE_TAG = re.compile(r"^<!--\s*table:\s*(.*?)\s*-->$")
+_TABLE_ID = re.compile(r"[A-Za-z0-9_.\-]+")
+_FENCE = re.compile(r"^(`{3,}|~{3,})")
 _H2 = re.compile(r"^##\s+(.+?)\s*$")
 _MARKER = re.compile(r"\[C(\d+)\]")
-_SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")
+_SEPARATOR = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$")
+_PIPE = re.compile(r"(?<!\\)\|")
+_CODE_INDENT = re.compile(r"^(?: {4}| {0,3}\t)")  # an indented code line, never a table (M5)
 
 
 class HandoffError(ValueError):
@@ -34,6 +40,7 @@ class Handoff:
     duplicate_tags: list[str]
     orphan_tags: list[str]
     body: str
+    invalid_tags: list[str] = field(default_factory=list)
 
 
 def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
@@ -48,15 +55,36 @@ def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
         if not line.strip():
             continue
         key, sep, value = line.partition(":")
-        if not sep:
+        if not sep or not key.strip():
             raise HandoffError(f"front matter line is not key: value: {line!r}")
+        if key.strip() in front_matter:
+            raise HandoffError(f"front matter key {key.strip()!r} appears twice")
         front_matter[key.strip()] = value.strip()
     return front_matter, "\n".join(lines[end + 1 :])
 
 
 def cells(line: str) -> list[str]:
-    # ponytail: an escaped pipe (\|) inside a cell splits it; no module needs one.
-    return [cell.strip() for cell in line.strip().strip("|").split("|")]
+    """The cells of a table row; `\\|` is a literal pipe inside a cell (A8)."""
+    text = line.strip()
+    text = text[1:] if text.startswith("|") else text
+    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
+    return [cell.strip().replace("\\|", "|") for cell in _PIPE.split(text)]
+
+
+def _unfenced(lines: list[str]) -> list[str]:
+    """The lines with every fenced code block blanked, so it holds no section or tag."""
+    out, fence = [], ""
+    for line in lines:
+        opener = _FENCE.match(line.strip())
+        if fence:
+            fence = "" if opener and opener.group(1).startswith(fence) else fence
+            out.append("")
+        elif opener:
+            fence = opener.group(1)
+            out.append("")
+        else:
+            out.append(line)
+    return out
 
 
 def _read_table(lines: list[str], start: int) -> Table | None:
@@ -66,6 +94,8 @@ def _read_table(lines: list[str], start: int) -> Table | None:
         i += 1
     if i + 1 >= len(lines) or not lines[i].lstrip().startswith("|"):
         return None
+    if any(_CODE_INDENT.match(line) for line in lines[i : i + 2]):
+        return None
     if not _SEPARATOR.match(lines[i + 1].strip()):
         return None
     rows = []
@@ -78,24 +108,27 @@ def _read_table(lines: list[str], start: int) -> Table | None:
 
 def parse(text: str) -> Handoff:
     front_matter, body = _split_front_matter(text)
-    lines = body.splitlines()
+    lines = _unfenced(body.splitlines())
     sections = [m.group(1) for line in lines if (m := _H2.match(line))]
     tables: dict[str, Table] = {}
     duplicates: list[str] = []
     orphans: list[str] = []
+    invalid: list[str] = []
     for i, line in enumerate(lines):
         tag = _TABLE_TAG.match(line.strip())
         if not tag:
             continue
         table_id = tag.group(1)
         table = _read_table(lines, i + 1)
-        if table is None:
+        if not _TABLE_ID.fullmatch(table_id):
+            invalid.append(table_id)
+        elif table is None:
             orphans.append(table_id)
         elif table_id in tables:
             duplicates.append(table_id)
         else:
             tables[table_id] = table
-    return Handoff(front_matter, sections, tables, duplicates, orphans, body)
+    return Handoff(front_matter, sections, tables, duplicates, orphans, body, invalid)
 
 
 def markers(text: str) -> set[str]:
```

`rbot/scripts/rbotlib/validate.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/validate.py
+++ b/rbot/scripts/rbotlib/validate.py
@@ -94,6 +94,7 @@ def _tags(h: Handoff, contract: Contract) -> list[Finding]:
     declared = {t.id for t in contract.tables} | {"citations"}
     found = [Finding("duplicate_table", f"table {t} is tagged twice") for t in h.duplicate_tags]
     found += [Finding("orphan_tag", f"tag {t} has no table under it") for t in h.orphan_tags]
+    found += [Finding("invalid_tag", f"tag {t!r} is not a table id") for t in h.invalid_tags]
     found += [
         Finding("undeclared_table", f"table {t} is not in the contract")
         for t in h.tables
@@ -103,7 +104,10 @@ def _tags(h: Handoff, contract: Contract) -> list[Finding]:
 
 
 def _outside_citation_rows(body: str, table: Table) -> str:
-    """The body without the citations table's own rows, so a row cannot cite itself."""
+    """The body without the citations table's own rows, so a row cannot cite itself.
+
+    Lines are compared as parsed cells, so an excerpt with an escaped pipe (A8) still matches.
+    """
     rows = {tuple(row) for row in table.rows}
     kept = [line for line in body.splitlines() if tuple(cells(line)) not in rows]
     return "\n".join(kept)
```

`rbot/scripts/rbotlib/render.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/render.py
+++ b/rbot/scripts/rbotlib/render.py
@@ -53,6 +53,7 @@ def _rules_block(rules: Rules, module_id: str) -> list[str]:
         f"- H2 sections, exactly and in order: {', '.join(rules.sections)}.",
         "- Tag each table exactly once, with its `<!-- table: <id> -->` line "
         "directly above the table.",
+        "- Write a literal pipe inside any cell, excerpts included, as `\\|`.",
         "- Emit no table the contract does not list.",
         "- Column names exactly as printed, without the `*` that marks a critical column.",
         f"- A critical cell (column marked *) is never empty or `{rules.gap_marker}`,",
```

- [ ] **Step 4: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `191 passed, 101 skipped`. With the corpus gate: `101 passed, 191 deselected` (unchanged from Task 5; the parser change is covered by the unit tests and, from Task 7 on, by a corpus citation whose excerpt keeps the 10-K's pipes).

Run the gate run and the corpus gate. Expected: every command exits 0; `rbot check` still `0 problem(s)` (the shipped tree has no MODULE.md yet to regenerate).

- [ ] **Step 5: Commit, then open PR 02C (Tasks 5–6)**

```bash
git add rbot tests
git commit -m "handoff: amendments A8 (escaped pipes) and A9 (short separators, invalid tags, fenced blocks, front-matter keys), deferral M5 (indented tables are code)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/02b-intake bash scripts/check_pr_size.sh
```

Expected: `799 changed lines (limit 800)`.

Report: test counts, gate and corpus-gate exit codes, PR size. `Not verified:` that GPT and Claude models escape pipes as MODULE.md asks (Plan 05's proxy runs and A/B measure it; an unescaped pipe shows as `row_shape` or `citation_incomplete`); a table nested inside a list item (M5 counts indent from the line start, not from the list marker as GitHub does).

---

### Task 7: `rbot validate --run`: every citation names a run source and anchors in it

**Files:**
- Modify: `rbot/scripts/rbotlib/validate.py`, `rbot/scripts/rbotlib/cli.py`
- Test: `tests/test_validate_run.py`

**Interfaces:**
- Consumes: `prepared/index.json` and the prepared texts (Tasks 4–5); `<RUN>/fetched/` (written by `rbot fetch`, Plan 10).
- Produces:
  - `rbotlib.validate.check(text, contract, rules, run: Path | None = None) -> tuple[int, list[Finding]]`; with `run`, each `citations` row is checked: a `source` that is neither an inventoried path nor an existing `fetched/<file>` gives `source_unknown`; an unreadable source, or an excerpt not found in the source's prepared text (only on the cited pages when the locator holds `p.<n>` or `pp.<a>-<b>`), gives `citation_unanchored`; both exit 2. A source flagged `image_read` (a screenshot or scan) has no text and is not anchored; its figures are Image-Read Values by canon rule 7.
  - `rbotlib.validate.normalise(text) -> str` (NFKC, case-folded, curly quotes and en/em dashes made plain, `|` table separators dropped, whitespace collapsed); `excerpt_found(text, excerpt) -> bool` (an excerpt split at `...` or `…` matches in order); `pages(prepared_text) -> dict[int, str]`; `run_findings(h, run) -> list[Finding]`. Plan 06's scorecard counts citation validity with `run_findings`; Task 8's expectations test reuses `excerpt_found`.
  - `rbot validate <handoff> --module <ID> --run <RUN>` (interfaces spec §9); Plan 01's `error: <path>: <reason>` exit 1 for a missing contract or Handoff file is kept unchanged.

- [ ] **Step 1: Branch for PR 02D and write the failing tests**

```bash
git switch -c build/02d-anchors
```

`tests/test_validate_run.py` — create:

```python
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from builders import make_run
from conftest import FIXTURES, fixture_json
from rbotlib.cli import main
from rbotlib.contract import Contract, contract_from_dict
from rbotlib.handoff import parse
from rbotlib.rules import Rules
from rbotlib.validate import EXIT_MALFORMED, check, excerpt_found, normalise, pages, run_findings

CITATION = "| C1 | TEST_10Q.txt | p.3 | revenue was 100 |"


@pytest.fixture
def contract(rules: Rules) -> Contract:
    return contract_from_dict(fixture_json("contract_cp_x.json"), rules)


@pytest.fixture
def run(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    pack.mkdir()
    text = "Cover page\fNotes\fIn the quarter, Revenue  was 100 (“reported”).\n"
    (pack / "TEST_10Q.txt").write_text(text, encoding="utf-8")
    (pack / "levels.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (pack / "broken.pdf").write_bytes(b"%PDF-1.4 not really")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    (run / "fetched").mkdir()
    (run / "fetched" / "01-example.com.md").write_text(
        "Gaming revenue grew 4%.\n", encoding="utf-8"
    )
    return run


def _codes(text: str, contract: Contract, rules: Rules, run: Path) -> tuple[int, list[str]]:
    code, findings = check(text, contract, rules, run)
    return code, [f"{f.code}: {f.message}" for f in findings]


def test_a_cited_excerpt_on_its_page_is_anchored(
    handoff_text: str, contract: Contract, rules: Rules, run: Path
) -> None:
    assert check(handoff_text, contract, rules, run) == (0, [])


@pytest.mark.parametrize(
    "case",
    [
        (
            "| C1 | TEST_10Q.txt | p.2 | revenue was 100 |",
            "citation_unanchored: C1: excerpt not found in TEST_10Q.txt p.2: 'revenue was 100'",
        ),
        (
            "| C1 | TEST_10Q.txt | Note 4 | revenue was 200 |",
            "citation_unanchored: C1: excerpt not found in TEST_10Q.txt: 'revenue was 200'",
        ),
        (
            "| C1 | OTHER.txt | p.1 | revenue |",
            "source_unknown: 'OTHER.txt' is not in inventory.json or fetched/",
        ),
        (
            "| C1 | broken.pdf | p.1 | revenue |",
            "citation_unanchored: 'broken.pdf' is unreadable: pypdf could not read the PDF",
        ),
    ],
)
def test_unknown_sources_and_unanchored_excerpts_are_malformed(
    handoff_text: str, contract: Contract, rules: Rules, run: Path, case: tuple[str, str]
) -> None:
    row, finding = case
    code, findings = _codes(handoff_text.replace(CITATION, row), contract, rules, run)
    assert code == EXIT_MALFORMED
    assert len(findings) == 1 and findings[0].startswith(finding)


@pytest.mark.parametrize(
    "row",
    [
        '| C1 | TEST_10Q.txt | pp.2-3 | In the quarter ... was 100 ("reported") |',
        "| C1 | fetched/01-example.com.md | section 1 | gaming revenue grew 4% |",
        "| C1 | levels.png | top left | Image-Read: CZR TLB 99.5 |",
    ],
)
def test_ranges_ellipses_fetched_pages_and_image_sources(
    handoff_text: str, contract: Contract, rules: Rules, run: Path, row: str
) -> None:
    assert check(handoff_text.replace(CITATION, row), contract, rules, run) == (0, [])


def test_without_a_citations_table_there_is_nothing_to_anchor(handoff_text: str, run: Path) -> None:
    assert run_findings(parse(handoff_text.split("## Citations")[0]), run) == []


def test_validate_takes_a_run_folder(
    tree: Path, run: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.md"
    text = (FIXTURES / "handoff_cp_x.md").read_text(encoding="utf-8")
    bad.write_text(text.replace("p.3", "p.1"), encoding="utf-8")
    args = ["--root", str(tree), "validate", str(bad), "--module", "CP-X", "--run", str(run)]
    assert main(args) == EXIT_MALFORMED
    assert (
        "citation_unanchored: C1: excerpt not found in TEST_10Q.txt p.1" in capsys.readouterr().out
    )


def test_normalise_and_pages() -> None:
    assert normalise("  “Net”  revenues | 2,993 — Q2 ") == '"net" revenues 2,993 - q2'
    assert excerpt_found("alpha beta gamma delta", "alpha … gamma")
    assert not excerpt_found("alpha beta gamma delta", "gamma ... alpha")
    assert pages("<<< page 1 >>>\none\n<<< page 2 >>>\ntwo\n") == {1: "\none\n", 2: "\ntwo\n"}


@pytest.mark.corpus
def test_citations_anchor_in_real_filings(
    prepared_run: Callable[[str], Path], handoff_text: str, contract: Contract, rules: Rules
) -> None:
    tenk = r"| C1 | CZR_FY2025_10K.txt | p.1 | Net revenues \| 11,486 \| 11,245 \| 11,528 |"
    wrong = tenk.replace("11,528", "11,529")
    run = prepared_run("czr-2026q2")
    assert check(handoff_text.replace(CITATION, tenk), contract, rules, run) == (0, [])
    assert check(handoff_text.replace(CITATION, wrong), contract, rules, run)[0] == EXIT_MALFORMED
    six = "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf"
    cover = f"| C1 | {six} | p.1 | SIX FLAGS ENTERTAINMENT CORPORATION |"
    ford = prepared_run("tid-ford")
    assert check(handoff_text.replace(CITATION, cover), contract, rules, ford) == (0, [])
    moved = handoff_text.replace(CITATION, cover.replace("p.1", "p.2"))
    assert check(moved, contract, rules, ford)[0] == EXIT_MALFORMED
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_validate_run.py --no-cov`
Expected: FAIL — `ImportError: cannot import name 'excerpt_found' from 'rbotlib.validate'` while collecting `tests/test_validate_run.py`.

- [ ] **Step 3: Write the run checks**

`rbot/scripts/rbotlib/validate.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/validate.py
+++ b/rbot/scripts/rbotlib/validate.py
@@ -3,12 +3,21 @@
 Exit codes follow Deploy V: 0 valid, 2 malformed, 3 blocked (valid but
 qa_status Blocked), 4 identity mismatch. A Handoff over the upstream cap
 (spec section 7, caos MAX_UPSTREAM_HANDOFF_BYTES) is malformed: `too_large`.
+With a run folder, a citation whose source is not in the run (`source_unknown`) or
+whose excerpt is not in that source's prepared text, on the cited page when the
+locator names one (`citation_unanchored`), is malformed too. A citation of an
+Image-Read source (a screenshot or scan) has no text to anchor and is not checked.
 """
 
 from __future__ import annotations
 
+import json
+import re
+import unicodedata
 from collections import Counter
 from dataclasses import dataclass
+from pathlib import Path
+from typing import Any
 
 from rbotlib.contract import Column, Contract, TableSpec
 from rbotlib.handoff import Handoff, HandoffError, Table, cells, markers, parse
@@ -141,12 +150,113 @@ def _citations(h: Handoff, rules: Rules) -> list[Finding]:
     return found
 
 
-def check(text: str, contract: Contract, rules: Rules) -> tuple[int, list[Finding]]:
+# --- `--run`: every citation names a pack file and its excerpt is in that file ---------
+
+_PAGE_LOCATOR = re.compile(r"\bpp?\.\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?", re.I)
+_PAGE_LINE = re.compile(r"^<<< page (\d+) >>>$", re.M)
+_QUOTES = str.maketrans(
+    {
+        "\u2018": "'",
+        "\u2019": "'",
+        "\u201c": '"',
+        "\u201d": '"',
+        "\u2013": "-",
+        "\u2014": "-",
+        "|": " ",
+    }
+)
+
+
+def normalise(text: str) -> str:
+    """Compare text as a reader would: NFKC, case-folded, plain quotes and dashes, one space."""
+    return " ".join(unicodedata.normalize("NFKC", text).translate(_QUOTES).casefold().split())
+
+
+def excerpt_found(text: str, excerpt: str) -> bool:
+    """Every part of the excerpt (split at an ellipsis) appears in the text, in order."""
+    haystack, at = normalise(text), 0
+    for part in re.split(r"\.\.\.|\u2026", excerpt):
+        needle = normalise(part)
+        if not needle:
+            continue
+        at = haystack.find(needle, at)
+        if at < 0:
+            return False
+        at += len(needle)
+    return True
+
+
+def pages(prepared_text: str) -> dict[int, str]:
+    """The text of each `<<< page N >>>` section of a prepared file."""
+    marks = list(_PAGE_LINE.finditer(prepared_text))
+    ends = [m.start() for m in marks[1:]] + [len(prepared_text)]
+    return {
+        int(m.group(1)): prepared_text[m.end() : end] for m, end in zip(marks, ends, strict=True)
+    }
+
+
+def _source_text(
+    run: Path, source: str, records: dict[str, dict[str, Any]]
+) -> str | Finding | None:
+    """The text a citation must anchor in; None for an Image-Read source (nothing to anchor)."""
+    if source.startswith("fetched/") and (run / source).is_file():
+        return "<<< page 1 >>>\n" + (run / source).read_text(encoding="utf-8")
+    record = records.get(source)
+    if record is None:
+        return Finding("source_unknown", f"{source!r} is not in inventory.json or fetched/")
+    if record["unreadable"]:
+        return Finding("citation_unanchored", f"{source!r} is unreadable: {record['unreadable']}")
+    if record["image_read"]:
+        return None
+    return (run / str(record["prepared"])).read_text(encoding="utf-8")
+
+
+def _anchor(row: list[str], text: str) -> Finding | None:
+    cid, source, locator, excerpt = row[:4]
+    by_page = pages(text)
+    wanted = _PAGE_LOCATOR.search(locator)
+    if wanted:
+        first = int(wanted.group(1))
+        last = int(wanted.group(2) or first)
+        scope = "\n".join(by_page.get(n, "") for n in range(first, last + 1))
+        where = f"{source} {locator}"
+    else:
+        scope, where = "\n".join(by_page.values()), source
+    if excerpt_found(scope, excerpt):
+        return None
+    return Finding("citation_unanchored", f"{cid}: excerpt not found in {where}: {excerpt!r}")
+
+
+def run_findings(h: Handoff, run: Path) -> list[Finding]:
+    """source_unknown and citation_unanchored for each citation row, against the run folder."""
+    table = h.tables.get("citations")
+    if table is None:
+        return []
+    index = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
+    records = {r["path"]: r for r in index["files"]}
+    found: list[Finding] = []
+    for row in table.rows:
+        if len(row) < 4:
+            continue
+        text = _source_text(run, row[1], records)
+        if isinstance(text, Finding):
+            found.append(text)
+        elif text is not None:
+            found += [f for f in [_anchor(row, text)] if f]
+    return found
+
+
+def check(
+    text: str, contract: Contract, rules: Rules, run: Path | None = None
+) -> tuple[int, list[Finding]]:
+    """Validate a Handoff; with `run`, also check each citation against the run's sources."""
     try:
         h = parse(text)
     except HandoffError as exc:
         return EXIT_MALFORMED, [Finding("not_a_handoff", str(exc))]
     findings = _front_matter(h, contract, rules) + _sections(h, rules) + _tags(h, contract)
+    if run is not None:
+        findings += run_findings(h, run)
     size = len(text.encode("utf-8"))
     if size > MAX_HANDOFF_BYTES:
         findings.append(Finding("too_large", f"{size} bytes; the cap is {MAX_HANDOFF_BYTES}"))
```

`rbot/scripts/rbotlib/cli.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/cli.py
+++ b/rbot/scripts/rbotlib/cli.py
@@ -35,7 +35,8 @@ def _validate(args: argparse.Namespace) -> int:
         text = Path(args.handoff).read_text(encoding="utf-8")
     except FileNotFoundError as exc:
         return _fail(Path(args.handoff), exc)
-    code, findings = check(text, contract, rules)
+    run = Path(args.run_dir) if args.run_dir else None
+    code, findings = check(text, contract, rules, run)
     for f in findings:
         print(f"{f.code}: {f.message}")
     print(f"exit {code}")
@@ -79,6 +80,7 @@ def main(argv: list[str] | None = None) -> int:
     v = sub.add_parser("validate", help="check a Handoff against its module contract")
     v.add_argument("handoff")
     v.add_argument("--module", required=True)
+    v.add_argument("--run", dest="run_dir", help="also check citations against this run folder")
     v.set_defaults(run=_validate)
     r = sub.add_parser("render-module", help="print or write a module's MODULE.md")
     r.add_argument("module")
```

- [ ] **Step 4: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `202 passed, 102 skipped`. With the corpus gate: `102 passed, 202 deselected`; `test_citations_anchor_in_real_filings` anchors a CZR 10-K income-statement line quoted with its pipes escaped (A8), refuses the same line with one digit changed, anchors the Six Flags registrant on page 1 of the mis-filed PDF and refuses it on page 2.

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 5: Commit**

```bash
git add rbot tests
git commit -m "validate: --run checks every citation's source and anchors its excerpt (source_unknown, citation_unanchored)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report: test counts, gate and corpus-gate exit codes. `Not verified:` excerpts a model paraphrases rather than quotes (refused, by design; Plan 06's proxy runs measure how often); citations of `fetched/` pages (no `rbot fetch` until Plan 10; tested with a hand-written file).

---

### Task 8: The synthetic CZR Primary pack, its expectations and amendment A5

**Files:**
- Create: `tests/corpus/synthetic/czr-2026q2-primary/` (seven SYNTHETIC files below), `tests/corpus/expectations/czr-2026q2-primary.json`
- Modify: `tests/corpus/corpus.json` (adds the pack, 34 in all), `scripts/check_pr_size.sh`, `.gitignore`, `docs/decisions/0001-toolchain.md`
- Test: `tests/test_synthetic_pack.py`, `tests/test_corpus.py`, `tests/test_gate_scripts.py`

**Interfaces:**
- Consumes: the registry format (Task 2), `prepared_run` (Task 4), the sheet and portfolio readers (Task 5), `excerpt_found` (Task 7), Plan 01's `scripts/check_pr_size.sh`.
- Produces:
  - Amendment A5: `scripts/check_pr_size.sh` also excludes `tests/corpus/synthetic/**` (the authored pack below is data, like `tests/golden/**/documents/**`), recorded in `docs/decisions/0001-toolchain.md`; `.gitignore` ignores `/corpus-runs/` (Task 9's proxy runs write there).
  - Pack `czr-2026q2-primary` (root `synthetic`, `primary: true`, portfolios `TEST_CLO_I`): the 21 files of caos `czr-2026q2-full-credit-assessment` by `external` reference; the same FINRA TRACE observation a second time as `TRACE_12769GAC4_last_trade.txt` (trap `duplicate_source`); the VMO2 Q1 2026 bond report PDF from TEST-Issuer Data as the pack's real PDF (no CZR rating PDF is public in the corpus; it is a PDF-path exercise, trap `entity_mismatch`); and seven authored files, each labelled SYNTHETIC in its name and first line: the new Term Loan B term sheet (Price Talk SOFR + 300–325, OID 99.0–99.5, USD 3,000 million, maturity 2033-12-15, use of proceeds Acquisition, commitment date 2026-10-08; trap `price_talk_not_market_level`), the pro forma capitalisation with sourced PF interest (989) and one unrealized add-back (run-rate cost synergies, 150), the Sector RV Workbook (`Gaming` sheet: loan rows, Index Statistics, Sector Ratings Average, `#N/A N/A` cells), a Bloomberg levels export with `#N/A` cells, a levels screenshot (trap `image_read_only`) and the Test CLO I positions and compliance-monitor CSVs. Pathways: Full Credit Assessment full `primary`; Portfolio Decision full and Relative Value full `exercises`.
  - The scenario is the real one in the caos documents — Fertitta Entertainment's agreed acquisition of Caesars Entertainment, Inc. (merger agreement of May 27, 2026) — financed by a synthetic new Term Loan B. Actual figures in the authored files are copied from the Form 10-K and 10-Q (each sum checked); pro forma figures are labelled arranger estimates. The positions file holds no Caesars exposure, consistent with the caos Test CLO I adaptation in the same pack.
  - `tests/corpus/expectations/czr-2026q2-primary.json` (`"schema": "rbot-expectations/1"`): 38 hand-checked values in the §12.1 shape (`module`, `table`, `where`, `value`, `tolerance`) plus `source`, `locator` and a verbatim `excerpt` that a test anchors in the prepared text (or a `rule` where the value follows from a spec rule, such as `level_basis` Talk for NEW-1); figures are plain decimals in USD millions (the §0 column convention); and, for `credit_snapshot`, the tables whose critical cells the pack supports (the completeness denominator of §12.6). Plan 03's `test_model_from_cp1_handoff_fixture` takes its CZR figures from here.

- [ ] **Step 1: Branch state and the failing tests**

(Still on `build/02d-anchors`.)

`tests/test_synthetic_pack.py` — create:

```python
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from openpyxl import load_workbook

from conftest import CORPUS
from rbotlib.corpus import repo_root
from rbotlib.prepare import load_index
from rbotlib.validate import excerpt_found

SYNTHETIC = repo_root(CORPUS) / "tests" / "corpus" / "synthetic"
PRIMARY = "czr-2026q2-primary"


def _first_line(path: Path) -> str:
    if path.suffix == ".xlsx":
        book = load_workbook(path, read_only=True)
        first = next(book.worksheets[0].iter_rows(max_row=1, values_only=True))
        book.close()
        return str(first[0])
    return path.read_text(encoding="utf-8").splitlines()[0]


def test_every_authored_file_is_labelled_and_registered() -> None:
    committed = sorted(p for p in SYNTHETIC.rglob("*") if p.is_file())
    registered = {
        f"{pack.path}/{f['path']}"
        for pack in CORPUS.packs
        for f in pack.data["files"]
        if f.get("synthetic")
    }
    assert {p.relative_to(SYNTHETIC).as_posix() for p in committed} == registered
    for path in committed:
        assert "SYNTHETIC" in path.name
        if path.suffix != ".png":  # the screenshot carries its label in the picture
            assert _first_line(path).startswith("SYNTHETIC"), path.name


def _records(run: Path) -> dict[str, dict[str, Any]]:
    return {r["path"]: r for r in load_index(run)["files"]}


@pytest.mark.corpus
def test_primary_pack_traps(prepared_run: Callable[[str], Path]) -> None:
    run = prepared_run(PRIMARY)
    inventory = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    digests = {f["path"]: f["sha256"] for f in inventory["files"]}
    assert (
        digests["TRACE_12769GAC4_last_trade.txt"]
        == digests["CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt"]
    )
    records = _records(run)
    assert records["SYNTHETIC_Levels_Screenshot.png"]["image_read"] is True
    vmo2 = records["VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf"]
    assert vmo2["pages"] == 47 and vmo2["entities"] == ["VMED O2 UK HOLDINGS LIMITED"]
    assert records["SYNTHETIC_Sector_RV_Gaming.xlsx"]["sheets"] == ["Gaming"]
    levels = (run / records["SYNTHETIC_Bloomberg_Levels_2026-10-02.csv"]["prepared"]).read_text()
    assert "CZR TL B 2030,BL3912045,,1L Term Loan,99.375,99.750,99.563,,252,Ba3,BB\n" in levels


@pytest.mark.corpus
def test_primary_pack_portfolio_json(prepared_run: Callable[[str], Path]) -> None:
    run = prepared_run(PRIMARY)
    assert load_index(run)["portfolios"] == [
        {"portfolio_id": "TEST_CLO_I", "json": "prepared/portfolios/TEST_CLO_I.json"}
    ]
    data = json.loads((run / "prepared" / "portfolios" / "TEST_CLO_I.json").read_text())
    assert (data["strategy"], data["nav"], data["par"], data["unit"]) == (
        "CLO",
        "630.9",
        "634.0",
        "MILLIONS",
    )
    assert len(data["positions"]) == 10
    assert not [p for p in data["positions"] if p["issuer_id"] == "CZR"]
    assert [lim["limit_id"] for lim in data["limits"]] == [
        "C-01", "C-02", "C-04", "C-05", "C-06", "C-07", "C-08", "C-10", "C-11", "C-17",
    ]  # fmt: skip
    unparsed = [u["row"].rsplit(" ", 1)[-1] for u in data["unparsed"]]
    assert unparsed == ["8", "14", "17", "18", "19", "20", "21"]  # C-03, C-09, C-12 to C-16


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs if p.data["expectations"]])
def test_expectations_anchor_in_their_sources(
    pack_id: str, prepared_run: Callable[[str], Path]
) -> None:
    expected = json.loads(
        (CORPUS.location.parent / CORPUS.pack(pack_id).data["expectations"]).read_text()
    )
    assert expected["pack"] == pack_id
    records = _records(prepared_run(pack_id))
    run = prepared_run(pack_id)
    for item in expected["values"]:
        assert {"module", "table", "where", "value"} <= set(item), item
        if "source" in item:
            text = (run / records[item["source"]]["prepared"]).read_text(encoding="utf-8")
            assert excerpt_found(text, item["excerpt"]), item
        else:
            assert "rule" in item, item
```

`tests/test_corpus.py` — patch:

```diff
--- a/tests/test_corpus.py
+++ b/tests/test_corpus.py
@@ -57,7 +57,7 @@ def _sha(data: bytes) -> str:
 
 def test_the_registry_is_well_formed(rules: Rules) -> None:
     ids = [p.id for p in CORPUS.packs]
-    assert len(ids) == len(set(ids)) == 33
+    assert len(ids) == len(set(ids)) == 34
     for pack in CORPUS.packs:
         assert pack.root in CORPUS.roots
         assert {w["id"] for w in pack.data["pathways"]} <= PATHWAYS
```

`tests/test_gate_scripts.py` — patch:

```diff
--- a/tests/test_gate_scripts.py
+++ b/tests/test_gate_scripts.py
@@ -1,5 +1,7 @@
 from __future__ import annotations
 
+import os
+import subprocess
 from pathlib import Path
 
 import check_bandit_floor
@@ -54,3 +56,23 @@ def test_bandit_main_reads_a_report(tmp_path: Path) -> None:
     report = tmp_path / "bandit.json"
     report.write_text('{"errors": [], "results": [], "metrics": {"_totals": {"loc": 400}}}')
     assert check_bandit_floor.main([str(report)]) == 0
+
+
+def _git(repo: Path, *args: str) -> None:
+    ident = ["-c", "user.name=t", "-c", "user.email=t@t"]
+    subprocess.run(["git", "-C", str(repo), *ident, *args], check=True, capture_output=True)
+
+
+def test_pr_size_ignores_the_corpus_synthetic_packs(tmp_path: Path) -> None:
+    _git(tmp_path, "init", "-q", "-b", "main")
+    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "base")
+    pack = tmp_path / "tests" / "corpus" / "synthetic" / "pack"
+    pack.mkdir(parents=True)
+    (pack / "big.md").write_text("line\n" * 900, encoding="utf-8")
+    (tmp_path / "small.py").write_text("x = 1\n" * 10, encoding="utf-8")
+    _git(tmp_path, "add", "-A")
+    _git(tmp_path, "commit", "-q", "-m", "work")
+    script = Path(__file__).parents[1] / "scripts" / "check_pr_size.sh"
+    env = {**os.environ, "BASE_REF": "HEAD~1"}
+    result = subprocess.run(["bash", str(script)], cwd=tmp_path, env=env, capture_output=True)
+    assert (result.returncode, result.stdout) == (0, b"10 changed lines (limit 800)\n")
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_synthetic_pack.py tests/test_corpus.py tests/test_gate_scripts.py --no-cov`
Expected: FAIL — `4 failed`: `test_the_registry_is_well_formed` (`assert 33 == 34`), `test_primary_pack_traps` and `test_primary_pack_portfolio_json` (`CorpusError: no pack 'czr-2026q2-primary'`), and `test_pr_size_ignores_the_corpus_synthetic_packs` (`910 changed lines (limit 800)`, exit 1).

- [ ] **Step 3: Amendment A5: keep the synthetic packs out of the PR count**

`scripts/check_pr_size.sh` — patch:

```diff
--- a/scripts/check_pr_size.sh
+++ b/scripts/check_pr_size.sh
@@ -1,8 +1,10 @@
 #!/usr/bin/env bash
 # PR size gate (global rule): at most 800 changed lines against the base.
-# Lock files, the read-only reference copy and the public golden-pack
-# documents are data, not authored code (docs/decisions/0001-toolchain.md).
+# Lock files, the read-only reference copy, the public golden-pack documents
+# and the corpus's synthetic packs are data, not authored code
+# (docs/decisions/0001-toolchain.md).
 set -euo pipefail
 base="${BASE_REF:-origin/main}"
-n=$(git diff --numstat "$base...HEAD" -- . ':!*.lock' ':!reference/**' ':!tests/golden/**/documents/**')
+n=$(git diff --numstat "$base...HEAD" -- . ':!*.lock' ':!reference/**' ':!tests/golden/**/documents/**' \
+  ':!tests/corpus/synthetic/**')
 echo "$n" | awk '{s+=$1+$2} END{print s+0 " changed lines (limit 800)"; exit s>800}'
```

`.gitignore` — patch:

```diff
--- a/.gitignore
+++ b/.gitignore
@@ -13,3 +13,5 @@ node_modules/
 .DS_Store
 # Analyst runs never enter the repo.
 rbot-runs/
+# Proxy runs on the corpus (interfaces spec section 12.4); scorecards go to docs/corpus-runs/.
+/corpus-runs/
```

`docs/decisions/0001-toolchain.md` — patch:

```diff
--- a/docs/decisions/0001-toolchain.md
+++ b/docs/decisions/0001-toolchain.md
@@ -8,7 +8,7 @@
 
 **Exclusions, all data rather than authored code:**
 - `reference/deploy-v-r14/` (read-only Deploy V fork, ADR 0003) is outside ruff, mypy, coverage, bandit, jscpd, the suppression count and the PR-size count; gitleaks scans it in full (it reports no leaks at r14).
-- `tests/golden/**/documents/**` (public filings and labelled synthetic test documents, Plan 02) is outside the PR-size count.
+- `tests/golden/**/documents/**` and `tests/corpus/synthetic/**` (public filings and labelled synthetic test documents, Plan 02) are outside the PR-size count.
 - Lock files are outside the PR-size count (the global rule's own exclusion).
 - `design/` (design prototypes: report mockups and the script that builds their sample data) is outside ruff, mypy, coverage, bandit, jscpd and the suppression count; the shipping renderer lives under `rbot/` (Plan 07) and is gated. gitleaks scans it in full.
 
```

Run: `uv run pytest tests/test_gate_scripts.py --no-cov`
Expected: PASS.

- [ ] **Step 4: Write the authored text files**

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_CZR_2026_TLB_Term_Sheet.md` — create:

```markdown
SYNTHETIC: authored for Deploy VI tests. Not a real term sheet; every term below is illustrative.

# Caesars Entertainment, Inc.: Senior Secured Term Loan B, summary of terms

Dated 2026-09-29. Marketing stage: initial talk.

| Term | Detail |
|---|---|
| Borrower | Caesars Entertainment, Inc. (the surviving corporation of the merger with Empire Merger Sub, Inc.) |
| Facility | New Senior Secured Term Loan B |
| Debt type | First lien term loan |
| Size | USD 3,000 million |
| Use of proceeds | Acquisition: to finance part of the cash consideration for Fertitta Entertainment's acquisition of Caesars Entertainment, Inc. under the merger agreement dated May 27, 2026 |
| Price Talk | SOFR + 300–325 bps (initial talk) |
| SOFR floor | 0.50% |
| OID | 99.0–99.5 |
| Maturity | 2033-12-15 (seven years from expected closing) |
| Amortisation | 1.00% per annum, payable quarterly |
| Call protection | 101 soft call for six months |
| Expected facility ratings | Ba3 (Moody's) / BB- (S&P) |
| Commitment date | 2026-10-08 |
| Ranking | Pari passu with the existing CEI senior secured credit facilities and senior secured notes |

Bloomberg ID and CUSIP are not yet assigned. No Covenant Review score has been published for this facility.
```

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_CZR_2026_PF_Capitalisation.md` — create:

```markdown
SYNTHETIC: authored for Deploy VI tests. Pro forma figures are illustrative arranger estimates, not issuer disclosures.

# Caesars Entertainment, Inc.: pro forma capitalisation at June 30, 2026

Pro forma for Fertitta Entertainment's acquisition of Caesars Entertainment, Inc. and the new Senior Secured Term Loan B. USD millions. Actual figures are the face values in Note 6 of the Form 10-Q for the quarter ended June 30, 2026.

## Sources and uses

| Sources | Amount | Uses | Amount |
|---|---|---|---|
| New Senior Secured Term Loan B | 3,000 | Purchase of Caesars common equity | 6,324 |
| Fertitta Entertainment equity contribution | 3,524 | Repay CEI Revolving Credit Facility | 120 |
| Rollover equity | 300 | Fees, expenses and OID | 280 |
| | | Cash to balance sheet | 100 |
| Total sources | 6,824 | Total uses | 6,824 |

## Capitalisation

| Facility | Actual June 30, 2026 | Adjustment | Pro forma |
|---|---|---|---|
| CEI Revolving Credit Facility | 120 | (120) | 0 |
| CEI Term Loan A | 619 | 0 | 619 |
| CVA Delayed Draw Term Loan | 376 | 0 | 376 |
| CEI Term Loan B | 2,018 | 0 | 2,018 |
| CEI Term Loan B-1 | 2,835 | 0 | 2,835 |
| New Senior Secured Term Loan B | 0 | 3,000 | 3,000 |
| CEI Senior Secured Notes due 2030 | 2,000 | 0 | 2,000 |
| CEI Senior Secured Notes due 2032 | 1,500 | 0 | 1,500 |
| Total senior secured debt | 9,468 | 2,880 | 12,348 |
| CEI Senior Notes due 2029 | 1,200 | 0 | 1,200 |
| CEI Senior Notes due 2032 | 1,100 | 0 | 1,100 |
| Special Improvement District Bonds | 38 | 0 | 38 |
| Long-term notes and other payables | 1 | 0 | 1 |
| Total debt | 11,807 | 2,880 | 14,687 |
| Cash and cash equivalents | 965 | 100 | 1,065 |
| Net debt | 10,842 | 2,780 | 13,622 |

## Earnings and interest (last twelve months to June 30, 2026)

| Item | Amount | Basis |
|---|---|---|
| Adjusted EBITDA (issuer definition) | 3,592 | FY2025 3,624 plus H1 2026 1,807 less H1 2025 1,839, from the Form 10-K and Form 10-Q |
| Run-rate cost synergies identified by Fertitta Entertainment, not yet realised | 150 | Arranger estimate |
| Marketed Adjusted EBITDA | 3,742 | Adjusted EBITDA plus run-rate cost synergies |
| Cash interest paid for debt, LTM | 776 | FY2025 813 plus H1 2026 368 less H1 2025 405 |
| Pro forma cash interest paid for debt, LTM | 989 | Arranger estimate: LTM cash interest, plus the new Term Loan B at an assumed all-in rate of 7.325%, less interest on the repaid revolver |
```

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_Bloomberg_Levels_2026-10-02.csv` — create:

```text
SYNTHETIC: Bloomberg levels export authored for Deploy VI tests; not market observations
As of,2026-10-02
Security,Bloomberg ID,ISIN,Ranking,Bid Price,Ask Price,Mid Price,Mid YTW,Mid 3Y DM (bp),Moody's,S&P,Fitch
CZR TL B 2030,BL3912045,#N/A N/A,1L Term Loan,99.375,99.750,99.563,#N/A N/A,252,Ba3,BB,#N/A
CZR TL B-1 2031,BL4120876,#N/A N/A,1L Term Loan,99.500,99.875,99.688,#N/A N/A,241,Ba3,BB,#N/A
CZR 7.00 02/15/30,BO1185520,US12769GAA87,Senior Secured Notes,101.250,101.750,101.500,6.41,#N/A Field Not Applicable,B1,BB-,#N/A
CZR 6.50 02/15/32,BO2201453,US12769GAC44,Senior Secured Notes,93.000,93.500,93.250,8.07,#N/A Field Not Applicable,B1,BB-,#N/A
CZR 4.625 10/15/29,BO1203310,US12769GAB60,Senior Notes,94.250,94.875,94.563,6.52,#N/A Field Not Applicable,Caa1,B-,#N/A
CZR 6.00 10/15/32,BO2219978,US12769GAD27,Senior Notes,84.500,85.250,84.875,9.33,#N/A Field Not Applicable,Caa1,B-,#N/A
MGM 6.125 09/15/29,BO1199087,US552953CK52,Senior Notes,98.125,98.750,98.438,6.72,#N/A Field Not Applicable,B1,BB-,#N/A
PENN 4.125 07/01/29,BO1164521,US707569AV19,Senior Notes,93.500,94.000,93.750,6.65,#N/A Field Not Applicable,B3,B,#N/A
PENN TL B 2029,BL3301276,#N/A N/A,1L Term Loan,#N/A,#N/A,#N/A,#N/A N/A,#N/A,Ba3,BB-,#N/A
```

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv` — create:

```text
SYNTHETIC: Test CLO I Ltd positions extract authored for Deploy VI tests; no figure is a real holding
Portfolio ID,TEST_CLO_I
Portfolio,Test CLO I Ltd
Strategy,CLO
As of,2026-05-29
Currency,USD
Unit,MILLIONS
Total NAV,630.9
Total Par,634.0
Note,Extract of the ten largest issuers; the book holds 383 positions in 350 obligors. No Caesars Entertainment exposure.

Issuer ID,Issuer,Instrument ID,Par,% NAV,Sector,Rating,Country,Currency,Seniority,Asset Type
ASURION,Asurion,ASURION TL B,15.0,2.37%,Insurance,B3,US,USD,Senior secured,Loan
TDG,TransDigm,TDG TL,12.1,1.91%,Aerospace & Defense,Ba3,US,USD,Senior secured,Loan
TELEVISA,TelevisaUnivision,TELEVISA TL,9.0,1.42%,Entertainment Content,B2,US,USD,Senior secured,Loan
DIRECTV,Directv,DIRECTV TL,6.1,0.96%,Cable & Satellite,B1,US,USD,Senior secured,Loan
SIGNATURE,Signature Aviation,SIGNATURE TL,6.0,0.96%,Transportation & Logistics,B2,US,USD,Senior secured,Loan
NOVOLEX,Novolex,NOVOLEX TL,5.8,0.91%,Containers & Packaging Manufacturing,B2,US,USD,Senior secured,Loan
QUIKRETE,Quikrete,QUIKRETE TL,4.0,0.64%,Construction Materials Manufacturing,Ba3,US,USD,Senior secured,Loan
FRONERI,Froneri,FRONERI TL,4.0,0.63%,Food Production,B1,GB,USD,Senior secured,Loan
WHITECAP,White Cap Supply Holdings,WHITECAP TL,4.0,0.63%,Retail - Consumer Discretionary,B3,US,USD,Senior secured,Loan
ZELIS,Zelis,ZELIS TL,4.0,0.63%,Software,B2,US,USD,Senior secured,Loan
```

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv` — create:

```text
SYNTHETIC: Test CLO I Ltd compliance monitor authored for Deploy VI tests from the packaged sample constraints
Portfolio ID,TEST_CLO_I
As of,2026-05-29

ID,Constraint Category,Parameter,Limit,Breach Type,Source Document,Current Value,Headroom,Status
C-01,Single Name,Max single issuer exposure (largest: Asurion),≤ 2.5% NAV,Hard,Indenture §7.11,2.37%,0.13%,Watch
C-02,Top 10 Concentration,Aggregate top 10 issuers,≤ 15.0% NAV,Soft,Indenture §7.11,11.05%,3.95%,Pass
C-03,Rating — Floor,Min portfolio WAR,≥ Caa1 (numeric ≤ 17),Hard,Indenture §7.11,B1 (14.3),2.7 notches,Pass
C-04,Rating — CCC Bucket,Max CCC+ and below (incl. Unrated & Other),≤ 7.5% NAV,Hard,Indenture §7.11,7.36%,0.14%,Watch
C-05,Rating — Unrated,Max unrated exposure,≤ 5.0% NAV,Soft,Indenture §7.11,3.73%,1.27%,Pass
C-06,Sector,Max single sector (largest: Health Care Facilities & Services),≤ 10.0% NAV,Soft,Indenture §7.11,7.16%,2.84%,Pass
C-07,Sector,2nd largest sector: Commercial Support Services,≤ 10.0% NAV,Soft,Indenture §7.11,6.74%,3.26%,Pass
C-08,Sector,3rd largest sector: Insurance,≤ 10.0% NAV,Soft,Indenture §7.11,5.63%,4.37%,Pass
C-09,Instrument,Min 1st Lien / Senior Secured,≥ 90.0% NAV,Hard,Indenture §7.11,99.39%,9.39%,Pass
C-10,Instrument,Max 2nd Lien / Unsecured,≤ 10.0% NAV,Soft,Indenture §7.11,0.61%,9.39%,Pass
C-11,Duration / Maturity,Max WAL (weighted avg life),≤ 8.0 years,Soft,Indenture §7.11,4.82 yrs,3.18 yrs,Pass
C-12,Diversification,Min number of obligors,≥ 100,Hard,Indenture §7.11,350,250,Pass
C-13,Diversification,Smallest position (% NAV),Info only,—,—,0.0654%,—,Pass
C-14,Yield / Spread,WA Margin (bps over SOFR),Info only,—,—,313 bps,—,Pass
C-15,Pricing,WA Mid Price,Info only,—,—,99.578,—,Pass
C-16,Covenant,Covenant-Lite % (est.),Info only,—,—,~100%,—,Pass
C-17,ESG / Exclusion,"Excluded sectors (Tobacco, Contr. Weapons, Thermal Coal)",0% NAV,Hard,Indenture §7.11,0%,0%,Pass
```

- [ ] **Step 5: Write the two binary files from base64**

Save each block below to a file, then decode it to its path from the repo root (the decoder is the standard library, so it behaves the same on macOS and Linux):

```bash
uv run python -c "import base64, pathlib, sys; pathlib.Path(sys.argv[2]).write_bytes(base64.decodebytes(pathlib.Path(sys.argv[1]).read_bytes()))" <saved block> <path>
```

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_Sector_RV_Gaming.xlsx` — binary, base64:

```text
UEsDBBQAAAAIADd7S11Gx01IlQAAAM0AAAAQAAAAZG9jUHJvcHMvYXBwLnhtbE3PTQvCMAwG4L9S
dreZih6kDkQ9ip68zy51hbYpbYT67+0EP255ecgboi6JIia2mEXxLuRtMzLHDUDWI/o+y8qhiqHk
e64x3YGMsRoPpB8eA8OibdeAhTEMOMzit7Dp1C5GZ3XPlkJ3sjpRJsPiWDQ6sScfq9wcChDneiU+
ixNLOZcrBf+LU8sVU57mym/8ZAW/B7oXUEsDBBQAAAAIADd7S12Oydzp6gAAAMsBAAARAAAAZG9j
UHJvcHMvY29yZS54bWylkcFOwzAMhl9l6r11040eoiwXECeQkJgE4hY53lbRtFFi1O7tScvWgeDG
Mf4/f7YVhV5iH+gp9J4CNxRXo2u7KNFvsyOzlwARj+RMLBLRpXDfB2c4PcMBvMF3cyCoyrIGR2ys
YQOTMPeLMTsrLS5K/xHaWWARqCVHHUcQhYAryxRc/LNhThZyjM1CDcNQDOuZSxsJeH18eJ6Xz5su
sumQMq0sSgxkuA96usifxlbBt6I6z/4qkF2lCZJPnrbZJXlZ397t7jNdlVWdizIXYic2srqRm/pt
cv3ovwpdb5t98w/jRaAV/Po3/QlQSwMEFAAAAAgAN3tLXZlcnCMQBgAAnCcAABMAAAB4bC90aGVt
ZS90aGVtZTEueG1s7Vpbc9o4FH7vr9B4Z/ZtC8Y2gba0E3Npdtu0mYTtTh+FEViNbHlkkYR/v0c2
EMuWDe2STbqbPAQs6fvORUfn6Dh58+4uYuiGiJTyeGDZL9vWu7cv3uBXMiQRQTAZp6/wwAqlTF61
WmkAwzh9yRMSw9yCiwhLeBTL1lzgWxovI9bqtNvdVoRpbKEYR2RgfV4saEDQVFFab18gtOUfM/gV
y1SNZaMBE1dBJrmItPL5bMX82t4+Zc/pOh0ygW4wG1ggf85vp+ROWojhVMLEwGpnP1Zrx9HSSICC
yX2UBbpJ9qPTFQgyDTs6nVjOdnz2xO2fjMradDRtGuDj8Xg4tsvSi3AcBOBRu57CnfRsv6RBCbSj
adBk2PbarpGmqo1TT9P3fd/rm2icCo1bT9Nrd93TjonGrdB4Db7xT4fDronGq9B062kmJ/2ua6Tp
FmhCRuPrehIVteVA0yAAWHB21szSA5ZeKfp1lBrZHbvdQVzwWO45iRH+xsUE1mnSGZY0RnKdkAUO
ADfE0UxQfK9BtorgwpLSXJDWzym1UBoImsiB9UeCIcXcr/31l7vJpDN6nX06zmuUf2mrAaftu5vP
k/xz6OSfp5PXTULOcLwsCfH7I1thhyduOxNyOhxnQnzP9vaRpSUyz+/5CutOPGcfVpawXc/P5J6M
ciO73fZYffZPR24j16nAsyLXlEYkRZ/ILbrkETi1SQ0yEz8InYaYalAcAqQJMZahhvi0xqwR4BN9
t74IyN+NiPerb5o9V6FYSdqE+BBGGuKcc+Zz0Wz7B6VG0fZVvNyjl1gVAZcY3zSqNSzF1niVwPGt
nDwdExLNlAsGQYaXJCYSqTl+TUgT/iul2v6c00DwlC8k+kqRj2mzI6d0Js3oMxrBRq8bdYdo0jx6
/gX5nDUKHJEbHQJnG7NGIYRpu/AerySOmq3CEStCPmIZNhpytRaBtnGphGBaEsbReE7StBH8Waw1
kz5gyOzNkXXO1pEOEZJeN0I+Ys6LkBG/HoY4SprtonFYBP2eXsNJweiCy2b9uH6G1TNsLI73R9QX
SuQPJqc/6TI0B6OaWQm9hFZqn6qHND6oHjIKBfG5Hj7lengKN5bGvFCugnsB/9HaN8Kr+ILAOX8u
fc+l77n0PaHStzcjfWfB04tb3kZuW8T7rjHa1zQuKGNXcs3Ix1SvkynYOZ/A7P1oPp7x7frZJISv
mlktIxaQS4GzQSS4/IvK8CrECehkWyUJy1TTZTeKEp5CG27pU/VKldflr7kouDxb5OmvoXQ+LM/5
PF/ntM0LM0O3ckvqtpS+tSY4SvSxzHBOHssMO2c8kh22d6AdNfv2XXbkI6UwU5dDuBpCvgNtup3c
OjiemJG5CtNSkG/D+enFeBriOdkEuX2YV23n2NHR++fBUbCj7zyWHceI8qIh7qGGmM/DQ4d5e1+Y
Z5XGUDQUbWysJCxGt2C41/EsFOBkYC2gB4OvUQLyUlVgMVvGAyuQonxMjEXocOeXXF/j0ZLj26Zl
tW6vKXcZbSJSOcJpmBNnq8reZbHBVR3PVVvysL5qPbQVTs/+Wa3InwwRThYLEkhjlBemSqLzGVO+
5ytJxFU4v0UzthKXGLzj5sdxTlO4Ena2DwIyubs5qXplMWem8t8tDAksW4hZEuJNXe3V55ucrnoi
dvqXd8Fg8v1wyUcP5TvnX/RdQ65+9t3j+m6TO0hMnHnFEQF0RQIjlRwGFhcy5FDukpAGEwHNlMlE
8AKCZKYcgJj6C73yDLkpFc6tPjl/RSyDhk5e0iUSFIqwDAUhF3Lj7++TaneM1/osgW2EVDJk1RfK
Q4nBPTNyQ9hUJfOu2iYLhdviVM27Gr4mYEvDem6dLSf/217UPbQXPUbzo5ngHrOHc5t6uMJFrP9Y
1h75Mt85cNs63gNe5hMsQ6R+wX2KioARq2K+uq9P+SWcO7R78YEgm/zW26T23eAMfNSrWqVkKxE/
Swd8H5IGY4xb9DRfjxRiraaxrcbaMQx5gFjzDKFmON+HRZoaM9WLrDmNCm9B1UDlP9vUDWj2DTQc
kQVeMZm2NqPkTgo83P7vDbDCxI7h7Yu/AVBLAwQUAAAACAA3e0tdh1/dSXMIAAAdKgAAGAAAAHhs
L3dvcmtzaGVldHMvc2hlZXQxLnhtbJ2a7XLiuBKGb0XFnjq1W5uAZYMxs0mq+IYdIASSbM1PAQq4
YmzGEslmf+1F7HXtRZwrObLJgCV3Ox+pykyg+23Jsh631PLFcxQ/ig3nkvy5DUJxWdpIuftSqYjl
hm+ZKEc7HirLQxRvmVQf43VF7GLOVqloG1Rsy3IrW+aHpauL9LtpfHUR7WXgh3waE7Hfbln80uJB
9HxZoqUfX8z89UamX1SuLnZszedc3u2UQH2sHOOs/C0PhR+FJOYPl6Um/TKznVSSutz7/Flk/ibJ
1Syi6DH5MFxdlqykUzzgS5nEYOq/J97mQZCEUl35/hq1dGo1UWb//hG+lw6A6t+CCd6Ogj/8ldxc
lrwSWfEHtg/kLHoe8NeLqp262GGSXV3E0TOJk6u9ulgmfyRNKkc/TEZpLmP1va9aklfzb5PbQfd2
2P5C5qrXUUxm96TPtn64Pl4cYXu5iWK+IuqukA7fBdELuR8SyYUUv5EwIg/+eh9z4gvCiBrsR3V3
o4Xg8RNLxuGiItUVJu1VlupX9e3YQfvYQRvp4KEvX0gQseSmBCwZUvLEgj0nTJDogdiW7Z5T69yy
yc93884ZEf5fXBA/JP8Zh2dJf9Z+mH5e7H4p6Itz7IuD9GU4n991Z3M9RirpYZLRdXNCOs3bZkHD
1WPDVSRKO9ruWPgCNNzCJK0oVuF5TCZsywFhG29L3cnWXqivhVB3Wyxjf5e/jWmQDhZkvl+cH+YT
oOpiqul+EfjLyjT21cSBOt1DrzaIou2Cx2sy7AC6PqYbJbPq9mUHNTbARDMWPqo5CUiGuEQqhQAk
v6NDqGYx+VlN4V8A1VdMNU5nO6AY4Qq5j30JTa4xOtz+CnCfYO5N8Qi4X2Pu//5D6BgQTAsE326h
+36DXrS/UhKokVmRxPlGOuMCkmtHkmsYXYwLFkMTofWGhHRDyWOpEp9KUfKMDMNlGeIaC3M3J0um
qI7UU1REsVTP6nBFotSPrNOnLEQ43qskFnQhXUxywBvCGlO0Rk6D2la1BjGNiiCWMWcqJBn5HCJm
iDbAnEoLauX3gyJZmTxd2Rb1LipPWWg1s13TrSNlFekC5ehTrddsS/caZ2M0GmWnboSZGA6m/Tpr
t8rU7MY0az+3yqb9Jmt3y66tm2faNdZOVo0T98iJ+3FO3pC8lxMszCc5wXuFcoJJcE4wRWtUVZh4
dRfiBBWdU4gUzL2IFLQJlBQ3O008x5hkX91CUlyAFM8zvMauDoLJiWH2cqC4b4Di6qDkHG5cjZSa
YZ5p11ilMCn1Iyl1bJ0g00U2wSda651SMhq1IVIw+Uitv+/5Wv0bREsWiFduoC50sBgFeGASHA9M
odJIrWapTALhgYogODDnIjjQBpit4PgVoqOemRq0Zhk54GvWbJvWUR2go2FTgw6tCTPGxLDmssB1
1sEQT+vF4NzUNS7Mns30q0MyiHfkwsOmSXcygWAo8n9v7sBizPha8cSCHyRkU4fYpclkwaVEUggW
tYAR9GJQRjCFYsSxqA2nEFQEMYI5FzGCNpAmkHOIEU+foiYjWbNtPttHHsBI9hl8YATr1U+TSpOo
X2gP9AnN9Sc0009obj6hmX1MozHaODLawDJIUr8i/2Xb3W/kjyhccahc0CpWJ4gdtApXRW+Y5jQW
4PRi8V7LXlu23CTFjzSyeBGSb8GU9kaY7ve9v0seIxC3mBbnFlMobt2qZdnQWq6PiiBuMecibtEG
0twGYdvQVnY5bHWziW0DwtY2tiDjhv5kyGegiemR20VdZz3M/KbZ8hukrNktO8YmcKZdYWaLqKFD
rVPl1sLmWRSseKinLAifDwXAqUHDTPgTWzEt5Un2pEAEqUHDFGQ5VIPjgkoUL3W7YdWqEC+4CgIG
9S4iBm+CYpnuVfI64XPIaOZ8qkvMOWhcx8x1WpRGwwDGsJqbqWvNDlQNpqaDCY1mr5cd16BGv8iG
i2CTOfDATjx6arL7UrJ3gPOxEGfY/gmNM+NCsn3MQinOyCYSO1+ywJcvKUMFmyk04OAUA+QI0xVU
3FGNAqnqedR2QJBQFQgS5l0IEtqESj0gRlTjJM9R1u7UzG1VYs5xRKtm1UGLokjJ5R7TIZd6NAcI
Jd2e319pDl7ZMkt0+oW6GEun8zCKHoipZdefJC0jCOkvRcFikJ5OuShWYk/DgSQWKuAznzYqGh9O
KO+TM0QQL/Qc42lNFCpLSNVFVdhxRq9IAZ9n9FEJfJgxQP3fOsmgp6MMitXBx1EcJqdaksVkNL9t
krs5GXGV+dmar0h6tIbfUSzofNrqNEfg/cyWlhV4tmMi3NFcGm7Zq+oOXapXv83aQ8+wN5yG9qN7
9zVvr0ytAueB5ux4DYS6U2mcYlXV9447AVfgLTRuMvSjEShq02y1skbt3Ia7Q42Cqnky0KVmQdUc
e91u7sb7VK+n1qk5wHpBFVtZnyqqFKvMvX+AwfFFy62H8QWHN1v08qx8za+jeTTq5cTl+EPNodZL
cHbVHGqtvpfLEH29O2XLKZzYdW1iI4VseqoGUGzX+OMNlMNhOWkeRrzo9ZHTNsnG1tWHaNCNQiU/
kaEQew4eP7VRVeGBfQeVoSf2XVQCH7/3UH/4/L2Pdwk9HR8Uat5KKvZpeW6jqzeQKVtbdukTsK0Z
qVc3dtwdzW5TY/527TcWZD09vmWVLWN30tc83HLV6OFA74GNPJrszNtQ2OtQ8OjY2fDm6GSNtGau
azua3aGOOTq2PjqmQ890cB1zcLIO9bJrPj/0DjjI88M+LUdtbDnabkP7r9arP1jMaaPB/vf3PyDH
H/PvftC/90H//gf9B+/3Pwx/JfNWYfLa5Pj1dbqAP6gwlqKlROLDa4iHDzLapbukRSRltE3/3HC2
4nHioOwPUSSPH5LXII9vhF79H1BLAwQUAAAACAA3e0tdCYb2BnwCAADpCgAADQAAAHhsL3N0eWxl
cy54bWzdVkuPmzAQ/iuI+5YktCisIIciRarUVivtHnp1YhMs+UGNWSX99fVgL4HdDKtWPRUUeWY+
f/PyWKTo7EWwx4YxG52lUF0ZN9a290nSHRsmSfdBt0w5pNZGEutUc0q61jBCOyBJkWxWqyyRhKt4
V6he7qXtoqPulS3j9WiK/PKFOmP2MY68u0pTVsYX99xJeUdp1NxLed91cZTsiiQ42xW1VnOfYHCe
iWTRMxFlXBHBD4YPtJpILi7evhksRy20iawrhwEdTN0vv2EdVKg1+JJcaeMT8GGGBbLgQoxZbGJv
2BUtsZYZtXeKJw3Wt1iQny6ty+JkyGW9+RRPGMPiwhy0oczMyvWmXSFYbYFh+KkZBKtbWA7aWi1B
opyctCI+kxdaEJzvIxPiEQ78Rz0LcK4n57OC01Gj6LIKoncTFAgwdeedT/xu/s5vy5+1/dy7gtSg
/+y1ZQ+G1fw86Of6msDMfRirfxogCTVNOjfr22iNYBbL+DtMtZj4OPRcWK6C1nBKmXrbPuffkoO7
hrMAbhdlNemFfRrBMr7K3xjlvczHXQ9QWNh1lb/CrKyz60Vwwbii7MxoFVRzOgxi5AQXNjwD4zW0
Hx4EQlkeRCAA0VhoGijL89BY/2NdW7wuD6IZbm9DW5y1xVmedxOqhheNhbBy9yAl53maZhna3qq6
nUaF9jDL4Ic4RDMEDhoLov1p5xcGYGFs3pkN9JQXxwYteWFE0ZIXOg8Q0kPg5DkyAGgs4KCHgk4U
JIHEglFDWGkK54xmiF7zBSjPUQiGFJneLMMalcGLnBd6idI0zxEIQCSNNEUhuLALEJoGJIJCaeo/
pK++Z8nLdy65/rnd/QZQSwMEFAAAAAgAN3tLXbdH64rAAAAAFgIAAAsAAABfcmVscy8ucmVsc52S
S24CMQxArxJlX0ypxAIxrNiwQ4gLuInno5nEkWPE9PaN2MAgaBFL/56eLa8PNKB2HHPbpWzGMMRc
2VY1rQCyaylgnnGiWCo1S0AtoTSQ0PXYECzm8yXILcNu1rdMc/xJ9AqR67pztGV3ChT1Afiuw5oj
SkNa2XGAM0v/zdzPCtSana+s7PynNfCmzPP1IJCiR0VwLPSRpEyLdpSvPp7dvqTzpWNitHjf6P/z
0KgUPfm/nTClidLXRQkmb7D5BVBLAwQUAAAACAA3e0tdV5WFIDMBAAApAgAADwAAAHhsL3dvcmti
b29rLnhtbI2Q0U7DMAxFf6XKB9BugklM616YGJMQIIb2nrbuai2JK8fdYF9P0lKYxMueHF9bJ/d6
cSI+FESH5NMa5+ecq0aknaepLxuw2t9QCy7MamKrJbS8T6musYQVlZ0FJ+k0y2Ypg9GC5HyDrVcD
7RqWbxl05RsAsWZAWY1OLRejszdO0suOBMr4U1SjskM4+b+F2CZH9FigQfnKVf82oBKLDi2eocpV
phLf0OmJGM/kRJttyWRMribDYAcsWP6Tt9Hmhy58r4gu3mPmXM2yAKyRvfQbPV8Hk0cIy0PXCT2i
EeCVFlgzdS26fY8JMdKLHP0pxpo4bSFXax2876OHoG2qwY8E0EU6nmMY8Kb6QY6cCmp0UL0EkI+D
kKoMJ42lJ01v7yb3wX1nzEPQXt0z6erX2HjV5TdQSwMEFAAAAAgAN3tLXTPr47qtAAAA+wEAABoA
AAB4bC9fcmVscy93b3JrYm9vay54bWwucmVsc7WRPQ6DMAyFrxLlABio1KECpi6sFReIgvkRgUSx
q8LtG8EASB26MFnPlr/3ZGcvNIp7O1HXOxLzaCbKZcfsHgCkOxwVRdbhFCaN9aPiIH0LTulBtQhp
HN/BHxmyyI5MUS0O/yHapuk1Pq1+jzjxDzB8rB+oQ2QpKuVb5FzCbPY2wVqSKJClKOtc+rJOpIDL
EhEvBmmPs+mTf3qlP4dd3O1XuTXPR7itIeD06+ILUEsDBBQAAAAIADd7S12bhkKEGwEAANcDAAAT
AAAAW0NvbnRlbnRfVHlwZXNdLnhtbK2Tz07DMAzGX6XqdWozOHBA6y6MK+zAC4TEXaPmn2JvdG+P
27JKoLENlUujxvb3c/wlq7djBMw6Zz1WeUMUH4VA1YCTWIYIniN1SE4S/6adiFK1cgfifrl8ECp4
Ak8F9Rr5erWBWu4tZc8db6MJvsoTWMyzpzGxZ1W5jNEaJYnj4uD1D0rxRSi5csjBxkRccEKeibOI
IfQr4VT4eoCUjIZsKxO9SMdporMC6WgBy8saZ7oMdW0U6KD2jktKjAmkxgaAnC1H0cUVNPGQYfze
zW5gkLlI5NRtChHZtQR/551s6auLyEKQyFw55IRk7dknhN5xDfpWOE/4I6R28ATFsMwf83efJ/1b
GnkPof3ve9avpZPGTw2I4T2vPwFQSwECFAMUAAAACAA3e0tdRsdNSJUAAADNAAAAEAAAAAAAAAAA
AAAAgAEAAAAAZG9jUHJvcHMvYXBwLnhtbFBLAQIUAxQAAAAIADd7S12Oydzp6gAAAMsBAAARAAAA
AAAAAAAAAACAAcMAAABkb2NQcm9wcy9jb3JlLnhtbFBLAQIUAxQAAAAIADd7S12ZXJwjEAYAAJwn
AAATAAAAAAAAAAAAAACAAdwBAAB4bC90aGVtZS90aGVtZTEueG1sUEsBAhQDFAAAAAgAN3tLXYdf
3UlzCAAAHSoAABgAAAAAAAAAAAAAAICBHQgAAHhsL3dvcmtzaGVldHMvc2hlZXQxLnhtbFBLAQIU
AxQAAAAIADd7S10JhvYGfAIAAOkKAAANAAAAAAAAAAAAAACAAcYQAAB4bC9zdHlsZXMueG1sUEsB
AhQDFAAAAAgAN3tLXbdH64rAAAAAFgIAAAsAAAAAAAAAAAAAAIABbRMAAF9yZWxzLy5yZWxzUEsB
AhQDFAAAAAgAN3tLXVeVhSAzAQAAKQIAAA8AAAAAAAAAAAAAAIABVhQAAHhsL3dvcmtib29rLnht
bFBLAQIUAxQAAAAIADd7S10z6+O6rQAAAPsBAAAaAAAAAAAAAAAAAACAAbYVAAB4bC9fcmVscy93
b3JrYm9vay54bWwucmVsc1BLAQIUAxQAAAAIADd7S12bhkKEGwEAANcDAAATAAAAAAAAAAAAAACA
AZsWAABbQ29udGVudF9UeXBlc10ueG1sUEsFBgAAAAAJAAkAPgIAAOcXAAAAAA==
```

`tests/corpus/synthetic/czr-2026q2-primary/SYNTHETIC_Levels_Screenshot.png` — binary, base64:

```text
iVBORw0KGgoAAAANSUhEUgAAAa4AAABAAQAAAABqt65xAAAEKUlEQVR42u2WXWwUVRiGnzM7tAVb
uxBMttrSQYz2ym5vtCXZdtAL0CjipSY1i2CCCRcFjS4JtKdFof7ReocJ2ir+3pgmmCBQ7EAD7YXG
1UTSBLDDj7QxQKfLWma3M3O82EC2souEmGgi381MzskzZ773vN/5jlDcRvgatxX/LnaLqWp+YvX2
q/OjBgAOQ/gmLu6AREIABDgK4FQ+pivzxEZmHHF9RPQD+o0LzB2azf5weSa4NLWkoae68cy5yEjN
5cbX7zv0dcPxZaoyMn228di3I7uqE2fG3tlVq66Fp2mUAYSf+XwiuffN7GfpuNrbkuRI7J4neegX
7672yNCXkz+1vBusmVyTl5t4HMIGJI3epUE3gDLRjpJKZ5Mm5ZSoLaCaxAWQ+ZgEx8bpJeHMkwDC
Bqh8YFEULjIjdkpCK+XMXCU9dEDQb7uOn5PTBiXVZBooQwdJIOVcRTRhAWGiH8eroj4ldrla23q4
oYvhyW8Q9WmyrEhE6js7DzqRPEwU2F9PV+K2rPy3XhH/o8LJC+dmmDJxc8pJAlT2fJ8Z61jugedc
Ix37xnJQ8ZyXr2l0Idl3cnurlzNFmPxH/mpBbN2jtcb5kRqZGjR6j3cv7hBa5yqqUqNfjS66tKqm
yd/kWTdgofbw0EuhD/zf9CdOPNiVyax3Sp9vFgsrnAPLlv9euqJ688OfNO+5v+6vdtBYBhKiHWaq
2piMKqa7SSoy5Tk3WBl0zSqg5CEABkJmJc6qgQA7QjSgdGPus1apLKikdhQAI5AKJ2l4Fy2CjkHo
zs1LCmPqMAhzR1K1DVfVJ5MvV70fDz32li5eLaMcWNHZaWXaCphdKeWPK6XGVV7MXn8ZUiqYM5U7
ggBEHDAKnm7CAmXcKZxbwFRTQyZ61vdTvabnOj0tNZvBSY2eqzBHE+Hladcsgn2xc4dVEahXJiRl
TPSd3gf46dlxK80GslOyMBZgAbq+oBM/YYD2NlUB4GA26oSni+VWK3Pn4hihFhtM1HA7lCh5Eapv
IklGcqVfyTqAhS39iO+2amXZcXNxFAK7GDZeIrk7rnJOnxoGdeyNwKUEC/CeKoJpgQAIco3I/TV4
jW0oj0HAc910sQ1oNZm+wh/vRfCPGEu3rHuamKZXlgirnN3Gz3d6wH8Uy2xaveeoDCdrUjj2UNP0
i6NgjRofNrHkdGyyJ1YEC62UPMKGifptYKi+nuB74Eryx4MdSdHPxEc3/0nzU0idlihZ5693Qc4T
wg7TpRfFysLgAlQoKWQatcAFJRlAtI3Fi11DDwDsdlUXIFo6soSyznxjyuRZC+r6i+W2E6DNUQGg
LKLMLgpftS/kGnN78Q3QywD7BQVgB/aYlsZzBmcLN+3rt1fnuX1XSytLw5vUmVPNjSfPjbhr94/c
W55QtVtj+3c1q0Lh3Smcfwr7E1KhEmtfzaQdAAAAAElFTkSuQmCC
```

The screenshot is a 430 × 64 one-bit PNG reading, line by line: "SYNTHETIC screenshot for Deploy VI tests - not a market observation", "Gaming loans, levels at 2026-10-02 (read from image only)", "CZR TL B-1 2031 bid 99.500 ask 99.875 3Y DM 241", "PENN TL B 2029 bid 98.750 ask 99.250 3Y DM 331". Open it to confirm.

- [ ] **Step 6: Register the pack and write its expectations**

`tests/corpus/corpus.json` — patch:

```diff
--- a/tests/corpus/corpus.json
+++ b/tests/corpus/corpus.json
@@ -2,6 +2,37 @@
   "schema": "rbot-corpus/1",
   "roots": {"caos-qualification": "external", "test-issuer-data": "external", "synthetic": "tests/corpus/synthetic"},
   "packs": [
+    {"id": "czr-2026q2-primary", "root": "synthetic", "path": "czr-2026q2-primary", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": true, "portfolios": ["TEST_CLO_I"], "prior_pack": null, "expectations": "expectations/czr-2026q2-primary.json", "pathways": [{"id": "FULL_CREDIT_ASSESSMENT", "depth": "full", "fit": "primary"}, {"id": "PORTFOLIO_DECISION", "depth": "full", "fit": "exercises"}, {"id": "RELATIVE_VALUE", "depth": "full", "fit": "exercises"}], "traps": [{"kind": "price_talk_not_market_level", "file": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "expect": "snapshot.instrument_levels.level_basis == Talk for NEW-1"}, {"kind": "image_read_only", "file": "SYNTHETIC_Levels_Screenshot.png", "expect": "prepared/index.json image_read true; its levels are Image-Read Values, never used in yield_or_dm"}, {"kind": "duplicate_source", "file": "TRACE_12769GAC4_last_trade.txt", "expect": "inventory.json: same sha256 as CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt"}, {"kind": "entity_mismatch", "file": "VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf", "expect": "PDF-path exercise: a VMO2 bond report in a CZR pack; CP-0 classifies it as not the issuer's"}], "files": [
+      {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2024_650_Notes_First_Supplemental_Indenture.txt"},
+      {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2024_650_Notes_Second_Supplemental_Indenture.txt"},
+      {"path": "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt", "sha256": "0809ab3981090bd2c23950da9530adb10e96882ddfa7db4404635e014d4c1119", "class": "issuer", "document_type": "Indenture", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt"},
+      {"path": "CZR_2024_Credit_Agreement_Fifth_Amendment.txt", "sha256": "7f2b5c777dc3347938a007eaea63a623b299a1188dbcfbe8980d389a0bcfc5b3", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2024_Credit_Agreement_Fifth_Amendment.txt"},
+      {"path": "CZR_2024_Credit_Agreement_Fourth_Amendment.txt", "sha256": "32f91de6ef3ff93d9924eb8d4e3dc4734d28b68ed1da0f816a085ffdcb085c95", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2024_Credit_Agreement_Fourth_Amendment.txt"},
+      {"path": "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt", "sha256": "25bea1d14fd9bb22838775f6fe056cd00741dc3d50eb1b79cc53498db502941c", "class": "issuer", "document_type": "Credit agreement", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt"},
+      {"path": "CZR_2026_Merger_Agreement.txt", "sha256": "e01077c1ed37c5b08c4d2dbfc15da19b78d50b4b38a42e3da22c3cf0e4c3038c", "class": "issuer", "document_type": "Other", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2026_Merger_Agreement.txt"},
+      {"path": "CZR_2026_Merger_Agreement_8K.txt", "sha256": "6808734cfbb19b56c5624e5a69e7209ccaad8a5039de94ad64563efdedf93169", "class": "issuer", "document_type": "Other", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2026_Merger_Agreement_8K.txt"},
+      {"path": "CZR_2026_Merger_Press_Release.txt", "sha256": "4fbecbd5f5a10b15911b5749daee41b3e40090e43ed54bf33aee07a21877e68b", "class": "issuer", "document_type": "Other", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_2026_Merger_Press_Release.txt"},
+      {"path": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt"},
+      {"path": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt", "sha256": "256c646128b7b670ebeb2e795aaced255373b488261b7f5c9111f933e2226b24", "class": "market", "document_type": "Market levels export", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt"},
+      {"path": "CZR_FY2025_10K.txt", "sha256": "172309048af2a6a2dab515d765f00a7c89bf8c874c6104a5e3a052b66cad4512", "class": "issuer", "document_type": "Annual report", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_FY2025_10K.txt"},
+      {"path": "CZR_Q2_2026_10Q.txt", "sha256": "f369ce5f1ebeddd9a0d4ce02ce3958112267d8701d1a348dfd6dc82d2034793a", "class": "issuer", "document_type": "Quarterly report", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_Q2_2026_10Q.txt"},
+      {"path": "CZR_Q2_2026_Earnings_Release.txt", "sha256": "b385f76ff631243d1053fa8073ebde4f8886b4a50c9ce34ce3498d6b2ac3e9f8", "class": "issuer", "document_type": "Earnings release", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_Q2_2026_Earnings_Release.txt"},
+      {"path": "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt", "sha256": "e2490912d9cc688135e15732e0fcf4aafd715e91e4d580edd577483535507bab", "class": "portfolio", "document_type": "Portfolio positions", "entity": "FHSUHY", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt"},
+      {"path": "FHSUHY_Prospectus_and_SAI_2026-05-26.txt", "sha256": "10455d54958421c56b4902f2fa41bfc08873bb9d16ee9fb22ab31ded215846ea", "class": "portfolio", "document_type": "Portfolio limits", "entity": "FHSUHY", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/FHSUHY_Prospectus_and_SAI_2026-05-26.txt"},
+      {"path": "MGM_FINRA_TRACE_552953CK5_2026-10-02.txt", "sha256": "e17cea1bb90debdeb8c1fea9c352132b57ae9b27ee0d3225fb67c6466d7d0e4a", "class": "market", "document_type": "Market levels export", "entity": "MGM", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/MGM_FINRA_TRACE_552953CK5_2026-10-02.txt"},
+      {"path": "MGM_Q2_2026_Earnings_Release.txt", "sha256": "795ac68aa1c51a7e0a6799a6e1ca053ee597dc9a1a9a6550a2438280a6e76cdb", "class": "market", "document_type": "Earnings release", "entity": "MGM", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/MGM_Q2_2026_Earnings_Release.txt"},
+      {"path": "PENN_FINRA_TRACE_707569AV1_2026-10-02.txt", "sha256": "666c0f36ace32336dffbcff324eaec5b4657edade407bb0b8a0e8d8fb405de6d", "class": "market", "document_type": "Market levels export", "entity": "PENN", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/PENN_FINRA_TRACE_707569AV1_2026-10-02.txt"},
+      {"path": "PENN_Q2_2026_Earnings_Release.txt", "sha256": "4d12fff94b066f73e6eccce84eec937e8fd4fdc38d6061704db66a40511a210c", "class": "market", "document_type": "Earnings release", "entity": "PENN", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/PENN_Q2_2026_Earnings_Release.txt"},
+      {"path": "SYNTHETIC_Bloomberg_Levels_2026-10-02.csv", "sha256": "85b00e2decdff09c8258daabaab56cba5d35c4846153d55523435abffff0a2fa", "class": "market", "document_type": "Market levels export", "entity": "CZR", "synthetic": true},
+      {"path": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "sha256": "23ae4d3c2cc09604884c95ae06ab6a0a20c4cd367a413f41e12fb8027157bd49", "class": "issuer", "document_type": "Lender presentation", "entity": "CZR", "synthetic": true},
+      {"path": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "sha256": "100351f6bb8035b2149a88d005b9d37a8d3ae9968b1625c92591ab15ab1a1749", "class": "issuer", "document_type": "Term sheet", "entity": "CZR", "synthetic": true},
+      {"path": "SYNTHETIC_Levels_Screenshot.png", "sha256": "de535203f4a7476b8ca8d27749e5408818898fea07711795ee849c3c47d44e3d", "class": "market", "document_type": "Market levels export", "entity": "CZR", "synthetic": true},
+      {"path": "SYNTHETIC_Sector_RV_Gaming.xlsx", "sha256": "c25d7d1893f172c81536a0baafe837acdde4db2dffa9766a7a5141cd8d958ef1", "class": "market", "document_type": "Sector RV Workbook", "entity": "GAMING", "synthetic": true},
+      {"path": "SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv", "sha256": "0d6a3b8f9016275654f16ec5ed10b7893beadf3cdd327b489c52f0529550f2ec", "class": "portfolio", "document_type": "Portfolio limits", "entity": "TEST_CLO_I", "synthetic": true},
+      {"path": "SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv", "sha256": "6763cbcc4263b7d972a8af47d36dcfa358c35ded0a6df937d0d14f839c7d3f18", "class": "portfolio", "document_type": "Portfolio positions", "entity": "TEST_CLO_I", "synthetic": true},
+      {"path": "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt", "sha256": "864ee90ab21372bcf89c8b27e02cd5d691d9095a64d507c7f656d5963cfe3207", "class": "portfolio", "document_type": "Portfolio limits", "entity": "TEST_CLO_I", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt"},
+      {"path": "TRACE_12769GAC4_last_trade.txt", "sha256": "4018aaa62309df6cd66a9b5fc766c4a9429e886e649023de2bad8673baf8aa51", "class": "market", "document_type": "Market levels export", "entity": "CZR", "external": "caos-qualification/czr-2026q2-full-credit-assessment/documents/CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt"},
+      {"path": "VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf", "sha256": "4ec0fed1044430a13a2e38e24c822847149571002651e897f3f076abc61c79be", "class": "issuer", "document_type": "Bond report", "entity": "VMO2", "pages": 47, "external": "test-issuer-data/virgin/VMED-O2-Quarterly-Bond-Report-Q1-2026.pdf"}]},
     {"id": "czr-2026q2-full-credit-assessment", "root": "caos-qualification", "path": "czr-2026q2-full-credit-assessment/documents", "issuer": {"id": "CZR", "name": "Caesars Entertainment, Inc."}, "period": "2026Q2", "as_of": "2026-10-02", "primary": false, "portfolios": ["TEST_CLO_I"], "prior_pack": null, "expectations": null, "pathways": [{"id": "FULL_CREDIT_ASSESSMENT", "depth": "full", "fit": "exercises"}], "traps": [{"kind": "missing_document_type", "file": null, "expect": "no Sector RV Workbook: CP-3 loan RV limited"}], "files": [
       {"path": "CZR_2024_650_Notes_First_Supplemental_Indenture.txt", "sha256": "0af4615b9a52e91e2675adacbbc90ecc7b21a61dc8205b4b2459cf4b9db0a219", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
       {"path": "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt", "sha256": "3621f08611f4c6a6faed734993a3f2d9c97041693053ffa97624cbe5b7299aea", "class": "issuer", "document_type": "Indenture", "entity": "CZR"},
```

`tests/corpus/expectations/czr-2026q2-primary.json` — create:

```json
{
  "schema": "rbot-expectations/1",
  "pack": "czr-2026q2-primary",
  "note": "Hand-checked on 2026-10-11 against the cited files. Figures are plain decimals in USD millions. Metric ids follow caos model_inputs (Plan 03 owns the exact list); period ids FY<yyyy>, YTD_Q2_<yyyy> (six months to June 30) and Q2_<yyyy>_END (balance at June 30).",
  "values": [
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "revenue", "period_id": "FY2025"}, "value": "11486", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Consolidated Statements of Operations", "excerpt": "Net revenues | 11,486 | 11,245 | 11,528"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "revenue", "period_id": "FY2024"}, "value": "11245", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Consolidated Statements of Operations", "excerpt": "Net revenues | 11,486 | 11,245 | 11,528"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "revenue", "period_id": "FY2023"}, "value": "11528", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Consolidated Statements of Operations", "excerpt": "Net revenues | 11,486 | 11,245 | 11,528"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "da", "period_id": "FY2025"}, "value": "1417", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Consolidated Statements of Operations", "excerpt": "Depreciation and amortization | 1,417 | 1,324 | 1,261"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "adjusted_ebitda", "period_id": "FY2025"}, "value": "3624", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Segment reconciliation to Adjusted EBITDA", "excerpt": "Adjusted EBITDA | $3,624 | $3,739 | $3,938"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "cash_interest_paid", "period_id": "FY2025"}, "value": "813", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Supplemental disclosure of cash flow information", "excerpt": "Cash interest paid for debt | $813 | $1,052 | $846"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "total_debt", "period_id": "FY2025"}, "value": "11905", "tolerance": "0", "source": "CZR_FY2025_10K.txt", "locator": "Note: Long-Term Debt", "excerpt": "Total debt | 11,905 | 11,792 | 12,154"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "revenue", "period_id": "YTD_Q2_2026"}, "value": "5863", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Consolidated Condensed Statements of Operations", "excerpt": "Net revenues | 2,993 | 2,907 | 5,863 | 5,701"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "revenue", "period_id": "YTD_Q2_2025"}, "value": "5701", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Consolidated Condensed Statements of Operations", "excerpt": "Net revenues | 2,993 | 2,907 | 5,863 | 5,701"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "cash_interest_paid", "period_id": "YTD_Q2_2026"}, "value": "368", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Supplemental disclosure of cash flow information", "excerpt": "Cash interest paid for debt | $368 | $405"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "cash_and_equivalents", "period_id": "Q2_2026_END"}, "value": "965", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Consolidated Condensed Balance Sheets", "excerpt": "Cash and cash equivalents | $965 | $887"},
    {"module": "CP-1", "table": "cp1.model_account_register", "where": {"metric_id": "total_debt", "period_id": "Q2_2026_END"}, "value": "11807", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "Total debt | 11,807 | 11,705 | 11,792"},
    {"module": "CP-1", "table": "cp1.debt_facility_register", "where": {"facility_name": "CEI Term Loan B", "period_id": "Q2_2026_END"}, "column": "drawn_amount", "value": "2018", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "CEI Term Loan B | 2030 | variable | 2,018"},
    {"module": "CP-1", "table": "cp1.debt_facility_register", "where": {"facility_name": "CEI Term Loan B-1", "period_id": "Q2_2026_END"}, "column": "drawn_amount", "value": "2835", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "CEI Term Loan B-1 | 2031 | variable | 2,835"},
    {"module": "CP-1", "table": "cp1.debt_facility_register", "where": {"facility_name": "CEI Senior Secured Notes due 2030", "period_id": "Q2_2026_END"}, "column": "carrying_value", "value": "2000", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "CEI Senior Secured Notes due 2030 | 2030 | 7.00% | 2,000"},
    {"module": "CP-1", "table": "cp1.debt_facility_register", "where": {"facility_name": "CEI Senior Secured Notes due 2032", "period_id": "Q2_2026_END"}, "column": "carrying_value", "value": "1500", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "CEI Senior Secured Notes due 2032 | 2032 | 6.50% | 1,500"},
    {"module": "CP-1", "table": "cp1.debt_facility_register", "where": {"facility_name": "CEI Senior Notes due 2029", "period_id": "Q2_2026_END"}, "column": "carrying_value", "value": "1200", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "CEI Senior Notes due 2029 | 2029 | 4.625% | 1,200"},
    {"module": "CP-1", "table": "cp1.debt_facility_register", "where": {"facility_name": "CEI Senior Notes due 2032", "period_id": "Q2_2026_END"}, "column": "carrying_value", "value": "1100", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "CEI Senior Notes due 2032 | 2032 | 6.00% | 1,100"},
    {"module": "CP-1", "table": "cp1.pro_forma_adjustment_register", "where": {"metric_id": "facility:NEW-1"}, "value": "3000", "tolerance": "0", "source": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "locator": "Capitalisation", "excerpt": "New Senior Secured Term Loan B | 0 | 3,000 | 3,000"},
    {"module": "CP-1", "table": "cp1.pro_forma_adjustment_register", "where": {"metric_id": "facility:CEI-RCF"}, "value": "-120", "tolerance": "0", "source": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "locator": "Capitalisation", "excerpt": "CEI Revolving Credit Facility | 120 | (120) | 0"},
    {"module": "CP-1", "table": "cp1.pro_forma_adjustment_register", "where": {"metric_id": "total_debt"}, "value": "2880", "tolerance": "0", "source": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "locator": "Capitalisation", "excerpt": "Total debt | 11,807 | 2,880 | 14,687"},
    {"module": "CP-1", "table": "cp1.pro_forma_adjustment_register", "where": {"metric_id": "cash_and_equivalents"}, "value": "100", "tolerance": "0", "source": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "locator": "Capitalisation", "excerpt": "Cash and cash equivalents | 965 | 100 | 1,065"},
    {"module": "CP-1", "table": "cp1.pro_forma_adjustment_register", "where": {"metric_id": "cash_interest_paid"}, "value": "213", "tolerance": "0", "calc": "989 - 776", "source": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "locator": "Earnings and interest", "excerpt": "Pro forma cash interest paid for debt, LTM | 989"},
    {"module": "CP-1", "table": "cp1.adjusted_ebitda_bridge", "where": {"addback_label": "Run-rate cost synergies"}, "column": "value", "value": "150", "tolerance": "0", "realization_status": "UNREALIZED", "source": "SYNTHETIC_CZR_2026_PF_Capitalisation.md", "locator": "Earnings and interest", "excerpt": "Run-rate cost synergies identified by Fertitta Entertainment, not yet realised | 150"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "size", "value": "3000", "tolerance": "0", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Size | USD 3,000 million"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "price_talk", "value": "SOFR + 300–325 bps", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Price Talk | SOFR + 300–325 bps (initial talk)"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "talk_stage", "value": "Initial talk", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Marketing stage: initial talk"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "oid", "value": "99.0–99.5", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "OID | 99.0–99.5"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "maturity_date", "value": "2033-12-15", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Maturity | 2033-12-15"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "use_of_proceeds", "value": "Acquisition", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Use of proceeds | Acquisition"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "debt_type", "value": "1L Term Loan", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Debt type | First lien term loan"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "expected_ratings", "value": "Ba3 / BB-", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Expected facility ratings | Ba3 (Moody's) / BB- (S&P)"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "commitment_date", "value": "2026-10-08", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Commitment date | 2026-10-08"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "bloomberg_id", "value": "—", "status": "Gap", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "Bloomberg ID and CUSIP are not yet assigned"},
    {"module": "RUN_BRIEF", "table": "snapshot.transaction_summary", "where": {"tranche_id": "NEW-1"}, "column": "cr_score", "value": "—", "status": "Gap", "source": "SYNTHETIC_CZR_2026_TLB_Term_Sheet.md", "locator": "Summary of terms", "excerpt": "No Covenant Review score has been published"},
    {"module": "CP-3", "table": "snapshot.instrument_levels", "where": {"facility_id": "NEW-1"}, "column": "level_basis", "value": "Talk", "rule": "talk rule, interfaces spec section 2.13: Price Talk and no market level"},
    {"module": "CP-3", "table": "snapshot.instrument_levels", "where": {"facility_id": "CEI-TLB-1"}, "column": "level_basis", "value": "Market", "source": "SYNTHETIC_Bloomberg_Levels_2026-10-02.csv", "locator": "row 5", "excerpt": "CZR TL B-1 2031,BL4120876,,1L Term Loan,99.500,99.875,99.688,,241"},
    {"module": "FIT", "table": "snapshot.portfolio_fit", "where": {"portfolio_id": "TEST_CLO_I"}, "column": "current_exposure", "value": "0", "tolerance": "0", "source": "SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv", "locator": "row 10", "excerpt": "No Caesars Entertainment exposure"}
  ],
  "front_pages": {
    "credit_snapshot": {
      "supportable": [
        {"table": "snapshot.run_header", "critical": "all"},
        {"table": "snapshot.company_profile", "critical": "all"},
        {"table": "snapshot.business_description", "critical": "all"},
        {"table": "snapshot.transaction_summary", "critical": "all", "rows": ["NEW-1"], "note": "bloomberg_id and cr_score are explicit gaps (not critical)"},
        {"table": "snapshot.capital_structure", "critical": "all", "rows": ["one per facility at Q2_2026_END plus NEW-1"]},
        {"table": "snapshot.capital_structure_totals", "critical": "all", "note": "PF interest rows from the PF capitalisation"},
        {"table": "snapshot.ebitda_adjustments", "critical": "all", "note": "one unrealized add-back: run-rate cost synergies"},
        {"table": "snapshot.instrument_levels", "critical": "all", "note": "NEW-1 at talk; screenshot levels are Image-Read and never used in yield_or_dm"},
        {"table": "snapshot.relative_value", "critical": "all", "note": "Loan RV from the Sector RV Workbook; HY rows from the Bloomberg levels export and TRACE"},
        {"table": "snapshot.credit_view", "critical": "all"},
        {"table": "snapshot.strengths_weaknesses", "critical": "all"},
        {"table": "snapshot.historical_performance", "critical": "all"},
        {"table": "snapshot.financial_columns", "critical": "all"},
        {"table": "snapshot.financials", "critical": "all"},
        {"table": "snapshot.recommendation", "critical": "all"},
        {"table": "snapshot.portfolio_fit", "critical": "all", "rows": ["TEST_CLO_I"]}
      ]
    }
  }
}
```

Check the authored files against the registry before running anything else:

```bash
uv run python rbot/scripts/rbot.py corpus verify --pack czr-2026q2-primary
```

Expected (corpus roots exported): `ok czr-2026q2-primary (30 files)` and `exit 0`. A `sha256 differs` line names an authored file that was not written byte for byte.

- [ ] **Step 7: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `204 passed, 108 skipped`. With the corpus gate: `108 passed, 204 deselected`. The primary pack now runs through every corpus check: inventory determinism (30 files), prepare markers (the workbook, both CSVs and the screenshot included: no `#N/A` survives, only the image is `image_read`), the traps, the Test CLO I portfolio JSON (NAV 630.9, ten positions, ten maximum limits, seven rows unparsed with reasons) and all 38 expectations anchored in their sources.

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 8: Commit**

```bash
git add tests scripts/check_pr_size.sh .gitignore docs/decisions/0001-toolchain.md
git commit -m "corpus: synthetic CZR Primary pack (term sheet, PF capitalisation, Sector RV, levels, screenshot, Test CLO I), expectations and amendment A5

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report: test counts, gate and corpus-gate exit codes. `Not verified:` that the synthetic terms resemble desk practice for an LBO-style Term Loan B (owner review); the expectation `where` keys (metric and period ids) against Plan 03's final CP-1 vocabulary; Image-Read of the screenshot by a model (Plan 05's CP-3).

---

### Task 9: `scripts/proxy_run.py`, steps 1 and 5

**Files:**
- Create: `scripts/proxy_run.py`
- Modify: `pyproject.toml` (`proxy_run` as first-party for the import sorter)
- Test: `tests/test_proxy_run.py`

**Interfaces:**
- Consumes: `rbotlib.corpus` (`load_registry`, `materialise`, `resolve_roots`, `repo_root`), `rbotlib.cli.main` (`inventory`, `prepare`), `rbotlib.prepare.load_index`.
- Produces (interfaces spec §12.6, steps 1 and 5 only):
  - `uv run python scripts/proxy_run.py --pack <id> --pathway <ID> --depth full|quick [--primary yes|no] [--registry <corpus.json>] [--out <corpus-runs>] [--date YYYYMMDD]` — step 1: copies the pack into `corpus-runs/<pack_id>/pack/` (external files resolved and hash-checked; skipped when already there), creates `corpus-runs/<pack_id>/<YYYYMMDD>-<issuer>-pending[-n]/` (§8.1 naming before Approval) with a pre-Approval `run-state.json` (`"schema": "rbot-run-state/1"`, `pack_root`, `run_id`, `issuer_id`, `as_of_date`, `plan: []`, `steps: {}`, `report.written_at: null`, every Approval field null, plus `proxy: {pack, pathway, depth}`), then runs `rbot inventory` and `rbot prepare`. Exit 1 when the pack does not list that Pathway and depth.
  - `--approve` — step 5: prints the `rbot approve` command line for the newest pending run of the pack: `--pathway`, `--depth`, `--primary` (the pack's flag unless overridden), `--analyst proxy-run`, `--deep-research yes`, `--prior-case yes|no` (from `prior_pack`). `rbot approve` itself arrives with Plan 04, `new-run`/`next` and steps 2–4 (dispatch, accept, scorecard) with Plan 06, which replaces the run-state seed with `rbot new-run`.
  - `proxy_run.run_id(base, issuer_id, day) -> str`; `seed_state(run, pack, entry, args, version)`; `approve_command(run, entry, args) -> list[str]`; `start(registry, entry, args, out) -> Path`; `main(argv=None) -> int`.

- [ ] **Step 1: Write the failing tests**

`tests/test_proxy_run.py` — create:

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import proxy_run
from conftest import CORPUS, corpus_gate
from rbotlib.corpus import resolve_roots, verify
from rbotlib.prepare import load_index

PACK = {
    "id": "p1",
    "root": "synthetic",
    "path": "p1",
    "issuer": {"id": "TEST", "name": "Test plc"},
    "period": "FY2025",
    "as_of": "2026-01-31",
    "primary": True,
    "portfolios": [],
    "prior_pack": None,
    "expectations": None,
    "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "primary"}],
    "traps": [],
}


def _registry(tmp_path: Path) -> Path:
    """A repo at <tmp>/repo with one in-repo synthetic pack holding one file."""
    repo = tmp_path / "repo"
    pack = repo / "tests" / "corpus" / "synthetic" / "p1"
    pack.mkdir(parents=True)
    body = b"SYNTHETIC filing\nRevenue was 100.\n"
    (pack / "SYNTHETIC_10K.txt").write_bytes(body)
    (repo / "pyproject.toml").write_text('[project]\nversion = "0.1.0"\n', encoding="utf-8")
    entry: dict[str, object] = {"path": "SYNTHETIC_10K.txt"}
    entry["sha256"] = hashlib.sha256(body).hexdigest()
    entry |= {
        "class": "issuer",
        "document_type": "Annual report",
        "entity": "TEST",
        "synthetic": True,
    }
    roots = {"synthetic": "tests/corpus/synthetic"}
    data = {"schema": "rbot-corpus/1", "roots": roots, "packs": [PACK | {"files": [entry]}]}
    registry = repo / "tests" / "corpus" / "corpus.json"
    registry.write_text(json.dumps(data), encoding="utf-8")
    return registry


def _args(registry: Path, *extra: str) -> list[str]:
    base = ["--pack", "p1", "--pathway", "EARNINGS_UPDATE", "--depth", "quick"]
    return [*base, "--registry", str(registry), "--date", "20261011", *extra]


def test_step_1_copies_the_pack_and_prepares_a_pending_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry)) == 0
    base = tmp_path / "repo" / "corpus-runs" / "p1"
    run = base / "20261011-test-pending"
    assert f"run folder: {run}\n" in capsys.readouterr().out
    assert (base / "pack" / "SYNTHETIC_10K.txt").is_file()
    state = json.loads((run / "run-state.json").read_text(encoding="utf-8"))
    assert (state["schema"], state["run_id"], state["pack_root"]) == (
        "rbot-run-state/1",
        "20261011-test-pending",
        str(base / "pack"),
    )
    assert (state["issuer_id"], state["pathway"], state["plan"]) == ("TEST", None, [])
    assert [r["path"] for r in load_index(run)["files"]] == ["SYNTHETIC_10K.txt"]
    assert proxy_run.main(_args(registry)) == 0
    assert (base / "20261011-test-pending-2" / "inventory.json").is_file()


def test_step_5_prints_the_simulated_approval(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry, "--approve")) == 1
    assert "no pending proxy run; run step 1 first" in capsys.readouterr().out
    proxy_run.main(_args(registry))
    capsys.readouterr()
    assert proxy_run.main(_args(registry, "--approve")) == 0
    run = tmp_path / "repo" / "corpus-runs" / "p1" / "20261011-test-pending"
    assert capsys.readouterr().out == (
        f"python rbot/scripts/rbot.py approve --run {run} --pathway EARNINGS_UPDATE"
        " --depth quick --primary yes --analyst proxy-run --deep-research yes --prior-case no\n"
    )
    assert proxy_run.main(_args(registry, "--approve", "--primary", "no")) == 0
    assert "--primary no" in capsys.readouterr().out


def test_a_pathway_the_pack_does_not_list_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    args = _args(registry)
    args[args.index("quick")] = "full"
    assert proxy_run.main(args) == 1
    assert "pack p1 lists [('EARNINGS_UPDATE', 'quick')]" in capsys.readouterr().out


@pytest.mark.corpus
def test_step_1_on_the_primary_pack(tmp_path: Path) -> None:
    pack = CORPUS.pack("czr-2026q2-primary")
    corpus_gate(verify(CORPUS, pack, resolve_roots(CORPUS)))
    args = ["--pack", pack.id, "--pathway", "FULL_CREDIT_ASSESSMENT", "--depth", "full"]
    assert proxy_run.main([*args, "--out", str(tmp_path), "--date", "20261011"]) == 0
    run = tmp_path / pack.id / "20261011-czr-pending"
    index = load_index(run)
    assert len(index["files"]) == len(pack.files)
    assert [r["path"] for r in index["files"] if r["unreadable"]] == []
    assert [p["portfolio_id"] for p in index["portfolios"]] == ["TEST_CLO_I"]
```

`pyproject.toml` — patch:

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -29,7 +29,7 @@ max-complexity = 10
 
 [tool.ruff.lint.isort]
 known-first-party = [
-  "rbotlib", "conftest", "builders", "check_suppressions", "check_bandit_floor",
+  "rbotlib", "conftest", "builders", "check_suppressions", "check_bandit_floor", "proxy_run",
 ]
 
 [tool.mypy]
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_proxy_run.py --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'proxy_run'` while collecting `tests/test_proxy_run.py`.

- [ ] **Step 3: Write the proxy-run skeleton**

`scripts/proxy_run.py` — create:

```python
"""Proxy run on a corpus pack (interfaces spec section 12.6): steps 1 and 5 only.

Step 1 (default): copy the pack into `corpus-runs/<pack_id>/pack/` (external files
resolved), create the run folder `corpus-runs/<pack_id>/<YYYYMMDD>-<issuer>-pending/`
with a pre-Approval `run-state.json`, then run `rbot inventory` and `rbot prepare`.
Step 5 (`--approve`): print the `rbot approve` command the simulated Approval runs,
from the pack's registry fields. Dispatch, accept and the scorecard (steps 2 to 4) and
`rbot new-run`, `rbot next` and `rbot approve` themselves arrive with Plans 04 and 06;
until then step 1 writes the run-state seed itself and step 5 prints the command only.
Repo tooling: never installed with the skill.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

from rbotlib.cli import main as rbot
from rbotlib.corpus import (
    REGISTRY,
    CorpusError,
    Pack,
    Registry,
    load_registry,
    materialise,
    repo_root,
    resolve_roots,
)


def run_id(base: Path, issuer_id: str, day: str) -> str:
    """`<YYYYMMDD>-<issuer>-pending`, with -2, -3, ... when that folder exists (spec 8.1)."""
    stem = f"{day}-{issuer_id.lower()}-pending"
    n, candidate = 1, stem
    while (base / candidate).exists():
        n += 1
        candidate = f"{stem}-{n}"
    return candidate


def _version(repo: Path) -> str:
    data = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def seed_state(run: Path, pack: Path, entry: Pack, args: argparse.Namespace, version: str) -> None:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    state: dict[str, Any] = {"schema": "rbot-run-state/1", "rbot_version": version}
    state |= {"run_id": run.name, "pack_root": str(pack), "created_at": now, "updated_at": now}
    state |= {"run_brief": "run-brief.md", "run_brief_sha256": None}
    state |= {"issuer_id": entry.data["issuer"]["id"], "as_of_date": entry.data["as_of"]}
    state |= dict.fromkeys(
        ("pathway", "depth", "primary", "deep_research", "prior_case", "approval")
    )
    state |= {"plan": [], "steps": {}}
    state["report"] = {"written_at": None, "html_sha256": None, "md_sha256": None}
    state["proxy"] = {"pack": entry.id, "pathway": args.pathway, "depth": args.depth}
    (run / "run-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def approve_command(run: Path, entry: Pack, args: argparse.Namespace) -> list[str]:
    """Step 5: the Approval a proxy run simulates (every Deep Research question approved)."""
    primary = args.primary or ("yes" if entry.data["primary"] else "no")
    prior = "yes" if entry.data["prior_pack"] else "no"
    command = ["python", "rbot/scripts/rbot.py", "approve", "--run", str(run)]
    command += ["--pathway", args.pathway, "--depth", args.depth, "--primary", primary]
    return [*command, "--analyst", "proxy-run", "--deep-research", "yes", "--prior-case", prior]


def _check_pathway(entry: Pack, pathway: str, depth: str) -> None:
    listed = [(w["id"], w["depth"]) for w in entry.data["pathways"]]
    if (pathway, depth) not in listed:
        raise CorpusError(f"pack {entry.id} lists {listed}, not ({pathway!r}, {depth!r})")


def _latest_run(base: Path) -> Path:
    runs = sorted(p for p in base.glob("*-pending*") if (p / "run-state.json").is_file())
    if not runs:
        raise CorpusError(f"{base}: no pending proxy run; run step 1 first")
    return max(runs, key=lambda p: p.stat().st_mtime)


def start(registry: Registry, entry: Pack, args: argparse.Namespace, out: Path) -> Path:
    """Step 1: materialise the pack, create the run folder, inventory and prepare."""
    base = out / entry.id
    pack = base / "pack"
    if not pack.is_dir():
        materialise(registry, entry, resolve_roots(registry), pack)
    run = base / run_id(base, entry.data["issuer"]["id"], args.date)
    run.mkdir(parents=True)
    seed_state(run, pack, entry, args, _version(repo_root(registry)))
    for command in ("inventory", "prepare"):
        if rbot([command, "--run", str(run)]) != 0:
            raise CorpusError(f"rbot {command} failed for {run}")
    return run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="proxy_run", description=__doc__.splitlines()[0])
    parser.add_argument("--pack", required=True)
    parser.add_argument("--pathway", required=True)
    parser.add_argument("--depth", required=True, choices=["full", "quick"])
    parser.add_argument("--primary", choices=["yes", "no"], help="override the pack's flag")
    parser.add_argument("--approve", action="store_true", help="step 5: print the approval")
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--out", help="the corpus-runs folder (default: <repo>/corpus-runs)")
    parser.add_argument("--date", default=datetime.now(UTC).strftime("%Y%m%d"))
    args = parser.parse_args(argv)
    try:
        registry = load_registry(Path(args.registry))
        entry = registry.pack(args.pack)
        _check_pathway(entry, args.pathway, args.depth)
        out = Path(args.out) if args.out else repo_root(registry) / "corpus-runs"
        if args.approve:
            print(shlex.join(approve_command(_latest_run(out / entry.id), entry, args)))
            return 0
        run = start(registry, entry, args, out)
    except CorpusError as exc:
        print(exc)
        return 1
    print(f"run folder: {run}")
    print("next: CP-0 (dispatch arrives with Plan 06: rbot next)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `207 passed, 109 skipped`. With the corpus gate: `109 passed, 207 deselected`; `test_step_1_on_the_primary_pack` prepares all 30 files of `czr-2026q2-primary` with none unreadable and finds the `TEST_CLO_I` portfolio.

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 5: Commit, then open PR 02D (Tasks 7–9)**

```bash
git add scripts/proxy_run.py tests pyproject.toml
git commit -m "corpus: proxy_run.py steps 1 and 5 (pack copy, pending run, inventory, prepare; simulated approval)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/02c-sheets bash scripts/check_pr_size.sh
```

Expected: `744 changed lines (limit 800)` (the pack's own files are outside the count, amendment A5).

Report: test counts, gate and corpus-gate exit codes, PR size. `Not verified:` steps 2–4 of §12.6 (Plan 06); that Plan 06's `rbot new-run` accepts the seed's fields unchanged (it should write the same §8.2 keys).

---

### Task 10: `rbot brief --from / --set / --show` and the Run Brief

**Files:**
- Create: `rbot/scripts/rbotlib/brief.py`, `tests/fixtures/handoff_cp0_czr_primary.md`
- Modify: `rbot/scripts/rbotlib/cli.py`
- Test: `tests/test_brief.py`

**Interfaces:**
- Consumes: `rbotlib.handoff.parse`, `markers`; the `brief_status` and `yes_no` scales (Task 1); a CP-0 Handoff carrying `cp0.run_brief_prefill` (`field`, `tranche_id`, `value`, `status`, `cite`), `cp0.portfolios`, `cp0.research_questions` and `cp0.prior_case` with the columns of interfaces spec §2.1 (Plan 04 writes CP-0's contract; this task's fixture is hand-written).
- Produces:
  - `<RUN>/run-brief.md`, Handoff-format, `module_id: RUN_BRIEF`, `inputs: CP-0`, `qa_status` Restricted while `issuer`, `issuer_id`, `as_of_date`, `objective` or `analyst` is a gap, else Pass; tables of §3.1 minus `brief.approval`: `snapshot.run_header`, `snapshot.transaction_summary` (one row per `tranche_id`; row `status` Gap when a critical cell is missing, Analyst-asserted when any field is, else Sourced; `cite` = the fields' markers), `brief.run_brief_fields` (every Run Brief field with `value`, `status`, `analyst_value`, `cite`), `brief.portfolios` (with `prepared_json` = `prepared/portfolios/<id>.json`), `brief.research_questions` (`approved` Yes until `rbot approve --untick`), `brief.prior_case` (`accepted` No until `rbot approve --prior-case`); `citations` = the CP-0 rows the brief cites, same ids. Every cell is written with `\|` for a literal pipe (A8), so a value or excerpt holding a pipe round-trips. `pathway`, `depth`, `currency`, `unit` and `report_date` stay `—` until Approval, CP-1 and render fill them.
  - `rbotlib.brief`: `BRIEF = "run-brief.md"`; `CP0 = "handoffs/CP-0.md"`; `EDITABLE` (issuer, issuer_id, as_of_date, objective, analyst, primary, morningstar_issuer_id, ssim_ev_multiple); `FIELDS` (`EDITABLE` plus pathway and depth); `TRANCHE` (the 15 tranche fields); `BriefError(ValueError)`; `Entry(value, status, analyst_value, cite)`; `Brief`; `normalise_value(name, value, rules) -> str`; `apply_edit(entry, value)` (source wins, design D8); `from_cp0(run, cp0_text, rules) -> Brief`; `previous(run) -> dict[str, Entry]`; `carry(old, new)`; `render(brief) -> str`; `build(run, source, edits, rules) -> Brief`; `add_command(sub)`.
  - `rbot brief --run <RUN> --from handoffs/CP-0.md` / `--set <field>=<value>` (repeatable; rebuilds from `handoffs/CP-0.md` and every earlier edit) / `--show`: exit 0; 1 for an unknown field, a field Approval sets, an invalid value (`primary` not Yes/No, `as_of_date` not ISO, `ssim_ev_multiple` not a number), a prefill field that is not a Run Brief or tranche field, or a missing CP-0 Handoff (§9). `--set-tranche` arrives with Plan 04.

- [ ] **Step 1: Branch for PR 02E and write the failing tests**

```bash
git switch -c build/02e-brief
```

`tests/fixtures/handoff_cp0_czr_primary.md` — create:

```markdown
---
module_id: CP-0
run_id: 20261011-czr-pending
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Pass
inputs: none
---

## Analysis

Hand-written test fixture: the CP-0 tables `rbot brief` reads, for the synthetic Primary pack `czr-2026q2-primary`. The pack holds a term sheet for a new senior secured term loan [C3] and the Test CLO I positions [C16] and limits [C17].

## Tables

<!-- table: cp0.run_brief_prefill -->
| field | tranche_id | value | status | cite |
|---|---|---|---|---|
| issuer | | Caesars Entertainment, Inc. | Sourced | [C1] |
| issuer_id | | CZR | Sourced | [C1] |
| as_of_date | | 2026-10-02 | Sourced | [C2] |
| objective | | — | Gap | |
| analyst | | — | Gap | |
| primary | | Yes | Sourced | [C3] |
| morningstar_issuer_id | | — | Gap | |
| ssim_ev_multiple | | — | Gap | |
| borrower | NEW-1 | Caesars Entertainment, Inc. | Sourced | [C4] |
| instrument | NEW-1 | New Senior Secured Term Loan B | Sourced | [C3] |
| debt_type | NEW-1 | 1L Term Loan | Sourced | [C5] |
| use_of_proceeds | NEW-1 | Acquisition | Sourced | [C6] |
| size | NEW-1 | 3000 | Sourced | [C7] |
| currency | NEW-1 | USD | Sourced | [C7] |
| unit | NEW-1 | MILLIONS | Sourced | [C7] |
| price_talk | NEW-1 | SOFR + 300–325 bps | Sourced | [C8] |
| talk_stage | NEW-1 | Initial talk | Sourced | [C9] |
| oid | NEW-1 | 99.0–99.5 | Sourced | [C10] |
| maturity_date | NEW-1 | 2033-12-15 | Sourced | [C11] |
| expected_ratings | NEW-1 | Ba3 / BB- | Sourced | [C12] |
| commitment_date | NEW-1 | 2026-10-08 | Sourced | [C13] |
| bloomberg_id | NEW-1 | — | Gap | [C14] |
| cr_score | NEW-1 | — | Gap | [C15] |

<!-- table: cp0.research_questions -->
| question_id | question | why_it_matters | consumer_module | evidence_needed |
|---|---|---|---|---|
| RQ-1 | How is Las Vegas Strip visitation trending into 2027? | Las Vegas drives the largest segment's Adjusted EBITDA | CP-2 | Visitation and convention statistics |

<!-- table: cp0.prior_case -->
| file | report_date | run_id | pathway | depth | offered |
|---|---|---|---|---|---|

<!-- table: cp0.portfolios -->
| portfolio_id | portfolio_name | strategy | positions_file | limits_file | as_of_date |
|---|---|---|---|---|---|
| TEST_CLO_I | Test CLO I Ltd | CLO | SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | 2026-05-29 |

## Gaps

- `objective`, `analyst`: the analyst gives them at turn 1.
- `morningstar_issuer_id`, `ssim_ev_multiple`: not in the pack; the issuer is listed, so EV uses its equity value.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_Q2_2026_10Q.txt | p.1 | CAESARS ENTERTAINMENT, INC. (Exact name of registrant as specified in its charter) |
| C2 | CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt | p.1 | Observed at: 2026-10-02T09:31:13Z |
| C3 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Facility New Senior Secured Term Loan B |
| C4 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Borrower Caesars Entertainment, Inc. |
| C5 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Debt type First lien term loan |
| C6 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Use of proceeds Acquisition |
| C7 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Size USD 3,000 million |
| C8 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Price Talk SOFR + 300–325 bps (initial talk) |
| C9 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Marketing stage: initial talk |
| C10 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | OID 99.0–99.5 |
| C11 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Maturity 2033-12-15 |
| C12 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Expected facility ratings Ba3 (Moody's) / BB- (S&P) |
| C13 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Commitment date 2026-10-08 |
| C14 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | Bloomberg ID and CUSIP are not yet assigned |
| C15 | SYNTHETIC_CZR_2026_TLB_Term_Sheet.md | p.1 | No Covenant Review score has been published |
| C16 | SYNTHETIC_TEST_CLO_I_Positions_2026-10-02.csv | p.1 | Portfolio ID,TEST_CLO_I |
| C17 | SYNTHETIC_TEST_CLO_I_Limits_2026-10-02.csv | p.1 | Portfolio ID,TEST_CLO_I |
```

`tests/test_brief.py` — create:

```python
from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.handoff import Handoff, markers, parse
from rbotlib.validate import run_findings

CP0 = FIXTURES / "handoff_cp0_czr_primary.md"


def _run(tmp_path: Path) -> Path:
    run = make_run(tmp_path / "pack", "20261011-czr-pending")
    (run / "handoffs").mkdir()
    shutil.copy(CP0, run / "handoffs" / "CP-0.md")
    return run


def _brief(run: Path) -> Handoff:
    return parse((run / "run-brief.md").read_text(encoding="utf-8"))


def _fields(h: Handoff) -> dict[str, list[str]]:
    return {row[0]: row[1:] for row in h.tables["brief.run_brief_fields"].rows}


def test_from_cp0_prefills_every_table(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run = _run(tmp_path)
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert capsys.readouterr().out == "run-brief.md: written\n"
    h = _brief(run)
    assert (
        h.front_matter["module_id"] == "RUN_BRIEF" and h.front_matter["qa_status"] == "Restricted"
    )
    assert h.sections == ["Analysis", "Tables", "Gaps", "Citations"]
    header = dict(
        zip(
            h.tables["snapshot.run_header"].columns,
            h.tables["snapshot.run_header"].rows[0],
            strict=True,
        )
    )
    assert (header["run_id"], header["issuer_id"], header["primary"]) == (
        "20261011-czr-pending",
        "CZR",
        "Yes",
    )
    assert (header["pathway"], header["report_date"]) == ("—", "—")
    tranche = dict(
        zip(
            h.tables["snapshot.transaction_summary"].columns,
            h.tables["snapshot.transaction_summary"].rows[0],
            strict=True,
        )
    )
    assert (tranche["tranche_id"], tranche["size"], tranche["status"]) == (
        "NEW-1",
        "3000",
        "Sourced",
    )
    assert (tranche["bloomberg_id"], tranche["cr_score"]) == ("—", "—")
    assert tranche["cite"].split()[:3] == ["[C4]", "[C3]", "[C5]"]
    fields = _fields(h)
    assert fields["issuer"] == ["Caesars Entertainment, Inc.", "Sourced", "—", "[C1]"]
    assert fields["analyst"] == ["—", "Gap", "—", "—"]
    assert h.tables["brief.portfolios"].rows[0][-1] == "prepared/portfolios/TEST_CLO_I.json"
    assert h.tables["brief.research_questions"].rows == [
        ["RQ-1", "How is Las Vegas Strip visitation trending into 2027?", "CP-2", "Yes"]
    ]
    assert h.tables["brief.prior_case"].rows == []
    assert "- `objective`: not found in the Source Pack" in h.body


def test_citations_are_the_cited_cp0_rows_only(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    h = _brief(run)
    ids = [row[0] for row in h.tables["citations"].rows]
    assert ids == [f"C{n}" for n in range(1, 16)]
    assert markers(h.body) == set(ids)


def test_source_wins_and_edits_survive_a_rebuild(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    edits = [
        "issuer=Caesars",
        "analyst=A. Analyst",
        "objective=New issue review",
        "ssim_ev_multiple=8.5x",
    ]
    assert main(["brief", "--run", str(run), *[a for e in edits for a in ("--set", e)]]) == 0
    fields = _fields(_brief(run))
    assert fields["issuer"] == ["Caesars Entertainment, Inc.", "Sourced", "Caesars", "[C1]"]
    assert fields["analyst"] == ["A. Analyst", "Analyst-asserted", "A. Analyst", "—"]
    assert fields["ssim_ev_multiple"][0] == "8.5"
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    h = _brief(run)
    assert _fields(h)["analyst"][0] == "A. Analyst" and h.front_matter["qa_status"] == "Pass"
    assert h.tables["snapshot.run_header"].rows[0][12] == "8.5x"


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        ("pathway=RELATIVE_VALUE", "pathway is set by rbot approve"),
        ("sector=Gaming", "unknown field 'sector'"),
        ("primary=maybe", "primary must be one of ('Yes', 'No')"),
        ("as_of_date=02/10/2026", "as_of_date must be YYYY-MM-DD"),
        ("ssim_ev_multiple=high", "ssim_ev_multiple must be a number"),
        ("analyst", "unknown field 'analyst'"),
    ],
)
def test_refused_edits_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit: str, message: str
) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--set", edit]) == 1
    assert message in capsys.readouterr().out


def test_show_prints_the_brief_and_needs_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    assert main(["brief", "--run", str(run), "--show"]) == 1
    assert (
        "no run-brief.md; run rbot brief --from handoffs/CP-0.md first" in capsys.readouterr().out
    )
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--show"]) == 0
    assert capsys.readouterr().out == (run / "run-brief.md").read_text(encoding="utf-8")


def test_a_bad_prefill_or_missing_cp0_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(CP0.read_text(encoding="utf-8").replace("| oid | NEW-1", "| margin | NEW-1"))
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 1
    assert "'margin' is not a tranche field" in capsys.readouterr().out
    cp0.write_text(CP0.read_text(encoding="utf-8").replace("| issuer_id | |", "| ticker | |"))
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 1
    assert "unknown field 'ticker'" in capsys.readouterr().out
    cp0.unlink()
    assert main(["brief", "--run", str(run), "--set", "analyst=A"]) == 1


@pytest.mark.corpus
def test_brief_citations_anchor_in_the_primary_pack(prepared_run: Callable[[str], Path]) -> None:
    run = prepared_run("czr-2026q2-primary")
    (run / "handoffs").mkdir(exist_ok=True)
    shutil.copy(CP0, run / "handoffs" / "CP-0.md")
    assert run_findings(parse(CP0.read_text(encoding="utf-8")), run) == []
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert run_findings(_brief(run), run) == []


def test_a_pipe_in_a_value_round_trips_escaped(tmp_path: Path) -> None:
    run = _run(tmp_path)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(CP0.read_text(encoding="utf-8").replace("Ba3 / BB-", r"Ba3 \| BB-"))
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert r"| Ba3 \| BB- |" in (run / "run-brief.md").read_text(encoding="utf-8")
    table = _brief(run).tables["snapshot.transaction_summary"]
    assert table.rows[0][table.columns.index("expected_ratings")] == "Ba3 | BB-"
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_brief.py --no-cov`
Expected: FAIL — `12 failed`: every `main(["brief", ...])` stops in argparse with `invalid choice: 'brief'` (`SystemExit: 2`); the corpus case skips without roots.

- [ ] **Step 3: Write the Run Brief and register the command**

`rbot/scripts/rbotlib/brief.py` — create:

```python
"""`rbot brief`: the Run Brief, `<RUN>/run-brief.md` (interfaces spec section 3.1).

`--from handoffs/CP-0.md` builds it from CP-0's `cp0.run_brief_prefill`, `cp0.portfolios`,
`cp0.research_questions` and `cp0.prior_case`, keeping the analyst's earlier edits.
`--set <field>=<value>` records an analyst edit and rebuilds from `handoffs/CP-0.md`, so
the brief always reflects the CP-0 Handoff plus every edit. Source wins (design D8): a
Sourced value stays and the edit is kept as `analyst_value`; a gap or an earlier assertion
takes the edit as Analyst-asserted. Pathway, depth and Primary are confirmed by
`rbot approve` (Plan 04), which also writes the approval table. The file is
Handoff-format with module id RUN_BRIEF.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from rbotlib.handoff import Handoff, HandoffError, Table, markers, parse
from rbotlib.rules import Rules, load_rules

BRIEF = "run-brief.md"
CP0 = "handoffs/CP-0.md"
MISSING = "—"
GAP, SOURCED, ASSERTED = "Gap", "Sourced", "Analyst-asserted"
EDITABLE = (
    "issuer",
    "issuer_id",
    "as_of_date",
    "objective",
    "analyst",
    "primary",
    "morningstar_issuer_id",
    "ssim_ev_multiple",
)
FIELDS = (*EDITABLE, "pathway", "depth")
REQUIRED = ("issuer", "issuer_id", "as_of_date", "objective", "analyst")
TRANCHE = (
    "borrower",
    "bloomberg_id",
    "instrument",
    "debt_type",
    "use_of_proceeds",
    "size",
    "currency",
    "unit",
    "price_talk",
    "talk_stage",
    "oid",
    "maturity_date",
    "expected_ratings",
    "cr_score",
    "commitment_date",
)
TRANCHE_OPTIONAL = frozenset(
    {"bloomberg_id", "oid", "expected_ratings", "cr_score", "commitment_date"}
)
COLUMNS = {
    "snapshot.run_header": (
        "run_id",
        "issuer",
        "issuer_id",
        "as_of_date",
        "objective",
        "analyst",
        "pathway",
        "depth",
        "primary",
        "currency",
        "unit",
        "morningstar_issuer_id",
        "ssim_ev_multiple_x",
        "report_date",
    ),
    "snapshot.transaction_summary": ("tranche_id", *TRANCHE, "status", "analyst_value", "cite"),
    "brief.run_brief_fields": ("field", "value", "status", "analyst_value", "cite"),
    "brief.portfolios": (
        "portfolio_id",
        "portfolio_name",
        "strategy",
        "positions_file",
        "limits_file",
        "as_of_date",
        "prepared_json",
    ),
    "brief.research_questions": ("question_id", "question", "consumer_module", "approved"),
    "brief.prior_case": ("file", "report_date", "run_id", "accepted"),
}


class BriefError(ValueError):
    """An edit or input the Run Brief refuses; the message names it."""


@dataclass
class Entry:
    value: str = MISSING
    status: str = GAP
    analyst_value: str = ""
    cite: str = ""


@dataclass
class Brief:
    run_id: str
    fields: dict[str, Entry] = field(default_factory=lambda: {f: Entry() for f in FIELDS})
    tranches: dict[str, dict[str, Entry]] = field(default_factory=dict)
    portfolios: list[list[str]] = field(default_factory=list)
    questions: list[list[str]] = field(default_factory=list)
    prior: list[list[str]] = field(default_factory=list)
    citations: list[list[str]] = field(default_factory=list)


def _rows(table: Table | None, columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Each row as a dict of the named columns; a cell holding only the gap marker is empty."""
    if table is None:
        return []
    index = {c.casefold(): i for i, c in enumerate(table.columns)}
    rows = []
    for row in table.rows:
        cells = {c: row[index[c]] if index.get(c, len(row)) < len(row) else "" for c in columns}
        rows.append({c: "" if v == MISSING else v for c, v in cells.items()})
    return rows


def normalise_value(name: str, value: str, rules: Rules) -> str:
    """The edit as stored, or BriefError naming why it is refused."""
    value = value.strip()
    if name == "primary":
        match = [v for v in rules.scales["yes_no"] if v.casefold() == value.casefold()]
        if not match:
            raise BriefError(f"primary must be one of {rules.scales['yes_no']}, not {value!r}")
        return match[0]
    try:
        if name == "as_of_date":
            return date.fromisoformat(value).isoformat()
        if name == "ssim_ev_multiple":
            return str(Decimal(value.removesuffix("x")))
    except (ValueError, InvalidOperation) as exc:
        kind = "YYYY-MM-DD" if name == "as_of_date" else "a number"
        raise BriefError(f"{name} must be {kind}, not {value!r}") from exc
    return value


def apply_edit(entry: Entry, value: str) -> None:
    """Source wins: a Sourced value stays; otherwise the edit becomes Analyst-asserted."""
    entry.analyst_value = value
    if entry.status != SOURCED:
        entry.value, entry.status = value, ASSERTED


def _prefill(h: Handoff, brief: Brief, rules: Rules) -> None:
    columns = ("field", "tranche_id", "value", "status", "cite")
    for row in _rows(h.tables.get("cp0.run_brief_prefill"), columns):
        status = row["status"] if row["status"] in rules.scales["brief_status"] else GAP
        entry = Entry(row["value"] or MISSING, status, "", row["cite"])
        if row["tranche_id"] and row["field"] in TRANCHE:
            brief.tranches.setdefault(row["tranche_id"], {})[row["field"]] = entry
        elif row["tranche_id"]:
            raise BriefError(f"cp0.run_brief_prefill: {row['field']!r} is not a tranche field")
        elif row["field"] in FIELDS:
            brief.fields[row["field"]] = entry
        else:
            raise BriefError(f"cp0.run_brief_prefill: unknown field {row['field']!r}")


def from_cp0(run: Path, cp0_text: str, rules: Rules) -> Brief:
    h = parse(cp0_text)
    brief = Brief(run.name)
    _prefill(h, brief, rules)
    portfolio = COLUMNS["brief.portfolios"][:-1]
    for p in _rows(h.tables.get("cp0.portfolios"), portfolio):
        brief.portfolios.append([*p.values(), f"prepared/portfolios/{p['portfolio_id']}.json"])
    questions = COLUMNS["brief.research_questions"][:-1]
    brief.questions = [
        [*q.values(), "Yes"] for q in _rows(h.tables.get("cp0.research_questions"), questions)
    ]
    prior = COLUMNS["brief.prior_case"][:-1]
    brief.prior = [[*p.values(), "No"] for p in _rows(h.tables.get("cp0.prior_case"), prior)]
    brief.citations = h.tables["citations"].rows if "citations" in h.tables else []
    return brief


def previous(run: Path) -> dict[str, Entry]:
    """The fields of the Run Brief as last written (empty when there is none yet)."""
    if not (run / BRIEF).is_file():
        return {}
    h = parse((run / BRIEF).read_text(encoding="utf-8"))
    rows = _rows(h.tables.get("brief.run_brief_fields"), COLUMNS["brief.run_brief_fields"])
    return {
        r["field"]: Entry(r["value"] or MISSING, r["status"], r["analyst_value"], r["cite"])
        for r in rows
    }


def carry(old: dict[str, Entry], new: Brief) -> None:
    """Re-apply the analyst's earlier edits, and Approval's fields, to a fresh pre-fill."""
    for name, entry in old.items():
        if name in EDITABLE and entry.analyst_value:
            apply_edit(new.fields[name], entry.analyst_value)
        elif name in FIELDS and name not in EDITABLE and entry.status != GAP:
            new.fields[name] = entry


def _table(table_id: str, rows: list[list[str]]) -> list[str]:
    columns = COLUMNS.get(table_id, ("id", "source", "locator", "excerpt"))
    lines = [f"<!-- table: {table_id} -->", "| " + " | ".join(columns) + " |"]
    lines.append("|" + "---|" * len(columns))
    cells = [[(cell or MISSING).replace("|", "\\|") for cell in row] for row in rows]
    lines += ["| " + " | ".join(row) + " |" for row in cells]
    return [*lines, ""]


def _tranche_row(tranche_id: str, entries: dict[str, Entry]) -> list[str]:
    values = [entries.get(f, Entry()).value for f in TRANCHE]
    critical = [entries.get(f, Entry()) for f in TRANCHE if f not in TRANCHE_OPTIONAL]
    status = SOURCED
    if any(e.status == GAP or e.value == MISSING for e in critical):
        status = GAP
    elif any(e.status == ASSERTED for e in entries.values()):
        status = ASSERTED
    edits = "; ".join(f"{f}={e.analyst_value}" for f, e in entries.items() if e.analyst_value)
    cites = " ".join(dict.fromkeys(m for e in entries.values() for m in e.cite.split()))
    return [tranche_id, *values, status, edits, cites]


def _header_row(brief: Brief) -> list[str]:
    f = {name: entry.value for name, entry in brief.fields.items()}
    multiple = f["ssim_ev_multiple"]
    head = [brief.run_id, *(f[n] for n in ("issuer", "issuer_id", "as_of_date", "objective"))]
    head += [f[n] for n in ("analyst", "pathway", "depth", "primary")]
    tail = [f["morningstar_issuer_id"], f"{multiple}x" if multiple != MISSING else MISSING]
    return [*head, MISSING, MISSING, *tail, MISSING]  # currency, unit (CP-1); report_date


def _analysis(brief: Brief) -> str:
    sourced = sum(e.status == SOURCED for e in brief.fields.values())
    asserted = sum(e.status == ASSERTED for e in brief.fields.values())
    return (
        f"Run Brief pre-filled from the CP-0 Handoff: {sourced} field(s) sourced, {asserted}"
        f" analyst-asserted; {len(brief.tranches)} new tranche(s), {len(brief.portfolios)}"
        f" portfolio(s), {len(brief.questions)} research question(s), {len(brief.prior)}"
        " earlier Report(s). Pathway, depth and Primary are confirmed at Approval"
        " (`rbot approve`)."
    )


def render(brief: Brief) -> str:
    gaps = [n for n in REQUIRED if brief.fields[n].status == GAP]
    field_rows = [[n, e.value, e.status, e.analyst_value, e.cite] for n, e in brief.fields.items()]
    tranche_rows = [_tranche_row(t, e) for t, e in sorted(brief.tranches.items())]
    used = markers(" ".join(cell for row in field_rows + tranche_rows for cell in row))
    front = ["---", "module_id: RUN_BRIEF", f"run_id: {brief.run_id}"]
    front += [f"issuer_id: {brief.fields['issuer_id'].value}"]
    front += [f"analysis_date: {brief.fields['as_of_date'].value}"]
    front += [f"qa_status: {'Restricted' if gaps else 'Pass'}", "inputs: CP-0", "---", ""]
    hint = "not found in the Source Pack; set it with `rbot brief --set {0}=<value>`."
    gap_lines = [f"- `{n}`: " + hint.format(n) for n in gaps] or ["None."]
    return "\n".join(
        [
            *front,
            *("## Analysis", "", _analysis(brief), "", "## Tables", ""),
            *_table("snapshot.run_header", [_header_row(brief)]),
            *_table("snapshot.transaction_summary", tranche_rows),
            *_table("brief.run_brief_fields", field_rows),
            *_table("brief.portfolios", brief.portfolios),
            *_table("brief.research_questions", brief.questions),
            *_table("brief.prior_case", brief.prior),
            *("## Gaps", "", *gap_lines, "", "## Citations", ""),
            *_table("citations", [r for r in brief.citations if r and r[0] in used]),
        ]
    )


def build(run: Path, source: Path, edits: list[str], rules: Rules) -> Brief:
    """Pre-fill from the CP-0 Handoff, carry earlier edits, then apply `edits` in order."""
    brief = from_cp0(run, source.read_text(encoding="utf-8"), rules)
    carry(previous(run), brief)
    for assignment in edits:
        name, sep, value = assignment.partition("=")
        if not sep or name not in FIELDS:
            raise BriefError(f"unknown field {name!r}; fields are {', '.join(EDITABLE)}")
        if name not in EDITABLE:
            raise BriefError(f"{name} is set by rbot approve")
        apply_edit(brief.fields[name], normalise_value(name, value, rules))
    return brief


def run_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    if args.show:
        if not (run / BRIEF).is_file():
            print(f"{run}: no {BRIEF}; run rbot brief --from {CP0} first")
            return 1
        print((run / BRIEF).read_text(encoding="utf-8"), end="")
        return 0
    source = Path(args.source or CP0)
    source = source if source.is_absolute() else run / source
    try:
        brief = build(run, source, args.set or [], load_rules(args.root))
    except (BriefError, HandoffError, OSError) as exc:
        print(exc)
        return 1
    (run / BRIEF).write_text(render(brief), encoding="utf-8")
    print(f"{BRIEF}: written")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("brief", help="build, edit or show the Run Brief")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    mode = c.add_mutually_exclusive_group(required=True)
    mode.add_argument("--from", dest="source", help="the CP-0 Handoff, relative to the run")
    mode.add_argument("--set", action="append", help="an analyst edit <field>=<value>")
    mode.add_argument("--show", action="store_true", help="print run-brief.md")
    c.set_defaults(run=run_command)
```

`rbot/scripts/rbotlib/cli.py` — patch:

```diff
--- a/rbot/scripts/rbotlib/cli.py
+++ b/rbot/scripts/rbotlib/cli.py
@@ -10,7 +10,7 @@ import sys
 from datetime import UTC, datetime
 from pathlib import Path
 
-from rbotlib import corpus, inventory, prepare
+from rbotlib import brief, corpus, inventory, prepare
 from rbotlib.catalog import check_tree
 from rbotlib.contract import ContractError, load_contract
 from rbotlib.render import render_module
@@ -91,6 +91,7 @@ def main(argv: list[str] | None = None) -> int:
     corpus.add_command(sub)
     inventory.add_command(sub)
     prepare.add_command(sub)
+    brief.add_command(sub)
     args = parser.parse_args(argv)
     result: int = args.run(args)
     run_dir = getattr(args, "run_dir", None)
```

- [ ] **Step 4: Run the tests, the gate run and the corpus gate**

Run: `uv run pytest`
Expected without corpus roots: `219 passed, 110 skipped`. With the corpus gate: `110 passed, 219 deselected`; `test_brief_citations_anchor_in_the_primary_pack` finds every citation of the CP-0 fixture and of the written Run Brief anchored in the primary pack's prepared text (`run_findings` empty).

Run the gate run and the corpus gate. Expected: every command exits 0.

- [ ] **Step 5: Commit**

```bash
git add rbot tests
git commit -m "brief: rbot brief --from/--set/--show writes the Run Brief from CP-0, source wins

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report: test counts, gate and corpus-gate exit codes. `Not verified:` a CP-0 Handoff written by a model (Plan 04's contract and proxy run); tranche edits (`--set-tranche`, Plan 04); the `snapshot.run_header` `currency`/`unit` fill after CP-1 (Plan 05).

---

### Task 11: Corpus regression

**Files:**
- Create: `docs/corpus-runs/2026-10-11-plan-02-corpus-regression.md`

**Interfaces:**
- Consumes: everything above; the owner's corpus roots.
- Produces: the regression record Plan 02 closes with (design D28; interfaces spec §12.4 keeps records under `docs/corpus-runs/`). Plan 02 adds no module and no Pathway, so it has no proxy-run scorecard and no A/B (§12.6–12.7 start with Plans 04–06); the record covers every deterministic corpus check and step 1 of the proxy run on the Primary pack.

- [ ] **Step 1: Re-run the whole corpus suite, required**

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
uv run python rbot/scripts/rbot.py corpus verify | tail -1
RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov | tail -1
RBOT_REQUIRE_CORPUS=1 uv run pytest | tail -2
```

Expected: `exit 0` (34 packs ok); `110 passed, 219 deselected`; `329 passed` with coverage ≥ 80%.

- [ ] **Step 2: Run proxy step 1 and step 5 on the Primary pack**

```bash
uv run python scripts/proxy_run.py --pack czr-2026q2-primary --pathway FULL_CREDIT_ASSESSMENT --depth full
uv run python scripts/proxy_run.py --pack czr-2026q2-primary --pathway FULL_CREDIT_ASSESSMENT --depth full --approve
run=$(ls -td corpus-runs/czr-2026q2-primary/*-pending* | head -1)
uv run python -c "
import json, sys
index = json.load(open(sys.argv[1] + '/prepared/index.json'))
files = index['files']
print(len(files), 'files;', sum(1 for f in files if f['unreadable']), 'unreadable;',
      sum(1 for f in files if f['image_read']), 'image_read;', sum(f['pages'] for f in files), 'pages;',
      [p['portfolio_id'] for p in index['portfolios']], index['portfolio_notes'])
" "$run"
```

Expected: the run folder path, `next: CP-0 (dispatch arrives with Plan 06: rbot next)`; the approval command ending `--primary yes --analyst proxy-run --deep-research yes --prior-case no`; then ``30 files; 0 unreadable; 1 image_read; 76 pages; ['TEST_CLO_I'] []``.

- [ ] **Step 3: Write the regression record**

`docs/corpus-runs/2026-10-11-plan-02-corpus-regression.md` — create:

```markdown
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
```

Every figure in it was measured when this plan was verified. If a re-run in Steps 1–2 gives a different count, stop and report BLOCKED with both values: the code or the corpus differs from the verified state. If every count matches, append one line to the file: `Re-run <YYYY-MM-DD>: identical results.`

- [ ] **Step 4: Run the gate run and the corpus gate one last time, commit, then open PR 02E (Tasks 10–11)**

```bash
git add docs/corpus-runs
git commit -m "corpus: Plan 02 regression record (34 packs, deterministic checks, proxy step 1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/02d-anchors bash scripts/check_pr_size.sh
```

Expected: every gate exits 0; `612 changed lines (limit 800)`.

Report: the record's figures and every exit code. `Not verified:` Copilot behaviour, GPT models and fetch (no module runs in Plan 02); the proxy steps 2–4 (Plan 06).

---

## Self-review against the spec

| Requirement (interfaces spec) | Where |
|---|---|
| §14.1 A1 scales and host producers; A3 `too_large`; A4 `document_types` | Task 1 |
| §14.1 A5 PR-size exclusion and `corpus-runs/` | Task 8 |
| Controller amendments A8 (escaped pipes in cells) and A9 (short separators, invalid tags reported, fenced blocks skipped, duplicate or empty front-matter keys refused) | Task 6 |
| Plan 01 final-review deferrals M4 (`inputs` line in the rules block) and M10 (string-only table id and title) | Task 1 |
| Deferral M5 (an indented table is a code block); A8 note (citation-row exclusion by parsed cells, tested with `\|` in an excerpt) | Task 6 |
| §12.1 `corpus.json`, `RBOT_CORPUS_ROOTS`, external and synthetic roots; §12.2 every pack (34) | Tasks 2, 8 |
| §12.3 `corpus` marker, require rule, `make corpus`, CI with in-repo packs required; `rbot corpus verify/list` (§9) | Task 2 |
| §12.5 row 02: `test_corpus_hashes_match`, `test_inventory_is_deterministic[pack]`, `test_prepare_pages_and_markers[pack]`, `test_entity_trap_flagged` | Tasks 2, 3, 4, 5 |
| §8.1 `inventory.json`, `prepared/index.json`, `prepared/<sha16>-<slug>.txt`, `prepared/portfolios/<id>.json`, `log/rbot.log`; §9 `inventory`, `prepare [--only]` | Tasks 3, 4, 5 |
| §7 prepared portfolio JSON (`rbot-portfolio/1`) | Task 5 |
| §9 `validate --run` (`source_unknown`, `citation_unanchored`) | Task 7 |
| §12.2 synthetic Primary pack, §12.1 expectations | Task 8 |
| §12.6 `proxy_run.py` steps 1 and 5 | Task 9 |
| §3.1 `run-brief.md` minus approval; §9 `brief --from/--set/--show` | Task 10 |
| Decision records 0002 (`pypdf`), 0003 (`openpyxl`) | Tasks 3, 5 |
| Last task: corpus regression | Task 11 |
