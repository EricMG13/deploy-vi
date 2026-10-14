# Deploy VI — Plan 03: Model (history)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the caos credit model (historical columns, statements, debt stack, credit metrics, layout and assembly; projections excluded) into `rbotlib.model`, read it from CP-1's (and CP-1D's) Handoffs and the Run Brief, compute the house view on the PF-LTM (Structuring and SSIM EBITDA, PF interest and cover, the two Multiples, EV, adjusted debt and leverage), and write `model.json`, `model.xlsx` and `handoffs/MODEL.md` with `rbot model --run <RUN>`: the `MODEL` host step.

**Architecture:** `rbot/scripts/rbotlib/model/` is pure Decimal arithmetic with no I/O except `run.py`. Ported from caos `caos/calculators/credit_model/` at commit `5c3cd52f`: `frame`, `_cells`, `periods` + `history` (caos `history.py`, split in two), `debt`, `statements`, `metrics`, `layout`, `assemble` (without projections). New: `reader` (figure and cell rules, `ModelInputError`), `registers` (the typed CP-1 registers), `inputs` (CP-1 tables to registers), `house_inputs` (CP-1 identity and equity tables, CP-1D, the Run Brief), `house` (the house view), `citations`, `snapshot` (the §3.2 tables), `output` (`model.json`, MODEL.md), `xlsx` (`model.xlsx`) and `run` (`rbot model`). Every ported file is rebuilt from caos by a port kit (Task 1) that applies exact import rewrites and patches and checks each result against a sha256 manifest, so no ported line is retyped.

**Tech Stack:** Python ≥ 3.11 standard library (`decimal` at precision 38, `ROUND_HALF_EVEN`) plus `openpyxl==3.1.5` (Plan 02, decision record 0003) for `model.xlsx`; pytest + hypothesis (property tests on the money arithmetic); `mutmut==3.7.0` (pre-approved, no decision record) for the mutation gate; the Plan 01/02 toolchain.

**Spec:** [`docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md`](../specs/2026-10-11-deploy-vi-interfaces.md) — §13 row **03** (scope, files, PRs), §3.2 (the `MODEL` tables), §6 (Model: port, `model.json`, bands and lines, snapshot mapping, house view, exact inputs, `model.xlsx`, `rbot model`), §2.2 (CP-1 tables), §12.5 row 03. Read with the design [`2026-10-11-deploy-vi-rbot-design.md`](../specs/2026-10-11-deploy-vi-rbot-design.md) (D19), the glossary [`CONTEXT.md`](../../../CONTEXT.md), Plan 01 and Plan 02 ([`2026-10-11-deploy-vi-02-intake-and-corpus.md`](2026-10-11-deploy-vi-02-intake-and-corpus.md)), whose merged tree this plan starts from. Controller rulings that shape it (planning ledger, 2026-10-11): Plan 03 splits large ported files and caos test files by topic to meet the 800-line cap (this supersedes §6.1's file list and §13's PR grouping for Plan 03 only); projections and the CP-CF cash-flow port and goldens are Plan 13's; quality-adjusted EBITDA is not computed (a `Rejected` add-back counts as unrealized, so it would always equal SSIM EBITDA); MODEL.md shows multiples to 2 dp and percentages to 1 dp while `model.json` stays exact; mutmut is pinned to 3.7.0; amendment A10 renames Plan 02's CZR expectation ids to the Model's.

## Global Constraints

- Repo root: `/Users/ericguei/Documents/Deploy VI`. Analyst data never enters it; `rbot-runs/` and `corpus-runs/` are ignored. `rbot model` writes only inside the run folder.
- **Starts on Plan 02's merged tree.** Task 1 Step 1 checks it: `openpyxl==3.1.5` and `types-openpyxl==3.1.5.20260827` pinned, `docs/decisions/0003-openpyxl.md`, `rbotlib/corpus.py`, the `corpus` marker and `tests/corpus/expectations/czr-2026q2-primary.json` present. If any is missing, stop and report BLOCKED (Plan 02 not merged).
- Runtime dependencies: none new (openpyxl comes from Plan 02). Dev adds exactly `mutmut==3.7.0` (Task 25; pre-approved test tool, no decision record; 3.8.0 is 29 days old on 2026-10-11).
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

- **The corpus gate** (Tasks 24–26, and at any task boundary the owner asks for): the owner's corpus roots exported, then the command exits 0. A missing or changed corpus file fails; it never skips.

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov
```

- **Test counts** in each task are `uv run pytest` with `RBOT_CORPUS_ROOTS` unset, measured on Plan 02's final tree (221 passed, 110 skipped before Plan 03), so the corpus tests skip. A count that differs means the tree is not at the previous task's end state: stop and report BLOCKED.
- **The Model's rules.** Decimal only, at `rbotlib.model._cells.CONTEXT` (precision 38, `ROUND_HALF_EVEN`, traps on invalid operations, division by zero and overflow); no rounding anywhere except MODEL.md's display (multiples 2 dp, percentages and days 1 dp, half-even) and `model.xlsx` number formats; `model.json` holds every figure exact. A null is never zero: a cell has a figure or a reason (`NOT_SOURCED`, `COMPONENT_MISSING`, `ZERO_OR_NEGATIVE_DENOMINATOR`, `NOT_APPLICABLE`, `NOT_STATED`, `NOT_PROJECTED`). A malformed CP-1 or CP-1D table raises `ModelInputError` naming the table, row and column; `rbot model` then exits 1 and writes nothing. No projections: every Model notes `NO_PROJECTIONS` until Plan 13.
- **The port.** Ported files come only from the kit (`$KIT/out/`, Task 1) and are never edited by hand: each task copies them and the kit's manifest has already proved their bytes. If a later need changes a ported file, change the kit's patch and re-run Task 1, never the copy. `$KIT` is `.port-03/` at the repo root (`export KIT="$PWD/.port-03"`), git-ignored and never committed; it holds only the scripts, patches and lists of Task 1 and what they rebuild from caos with `git show`. If it is gone, re-run Task 1 Steps 3–4 before continuing.
- **How to apply this plan's code.** A label "`<path>`:" is followed by the file's complete content: write it byte for byte, ending with one newline. `$KIT/...` labels are kit files, written under `.port-03/` and never committed. Never retype a figure or a hash: the kit's manifest, the golden digests and the corpus tests compare them.
- **Money code.** The whole Model is money code: property tests (Hypothesis) ship with history, statements, the house view and the round trip; Task 25 adds the mutation gate (`scripts/mutate_model.sh`) and records its result in `docs/model/mutation.md`. Implementers: `mx-scaffold` for kit and transcription tasks, `mx-invariants` for the new money modules, `mx-precise` for output and command code; task reviewer `mx-precise`, plus `mx-adversary` on Tasks 3, 20, 21, 22 and 25 (money arithmetic and refusals). Escalate one rung only after a gate fails or the agent reports BLOCKED.
- PR ≤ 800 changed lines, excluding lock files, `reference/**`, `tests/golden/**/documents/**` and `tests/corpus/synthetic/**` (`scripts/check_pr_size.sh`). Plan 03 ships as **24 stacked PRs**, one per task from Task 2 to Task 25 (Task 1 builds the kit and commits nothing; Task 26 is the corpus regression record and joins PR 03F2's branch as its last commit — see Task 26): 03A1–03A3 cells, figures, registers and inputs; 03B1–03B6 history; 03C1–03C3 debt and statements; 03D1–03D6 metrics, layout and assembly; 03E1–03E4 house view and the `rbot model` outputs; 03F1–03F2 the corpus tests and the mutation gate. Each task states its measured size. §13 groups the same work as 03A–03F; measured, a ~15,000-line port does not fit six PRs under the cap, so each group became several (the controller's ruling). Every PR carries the tests of its own code: 03D3 tests `layout()` straight from the metric frame (before `assemble` exists) and 03E1 tests `citations`.
- `reference/deploy-v-r14/` is never edited and never installed (ADR 0003).
- No stub or fake value standing in for real behaviour; no catch-all that hides a failure. Every task report ends with a `Not verified:` line (each task says what to list).
- Glossary words exactly as in `CONTEXT.md` (Model, PF-LTM, Structuring EBITDA, SSIM EBITDA, Unrealized Add-back, Reported EBITDA, Run Brief, Handoff …); names, ids, columns, schemas and commands exactly as in the interfaces spec. Code identifiers such as the `adjusted_ebitda` line keep their caos names.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Amendment

| # | Change | Why | Task |
|---|---|---|---|
| A10 | `tests/corpus/expectations/czr-2026q2-primary.json` (Plan 02): metric `da` → `depreciation_amortization`; periods `YTD_Q2_2026` → `H1_2026`, `YTD_Q2_2025` → `H1_2025`, `Q2_2026_END` → `H1_2026` (the six months to June 30, whose end date carries the June 30 balances); the pro forma `cash_interest_paid` row `213` → `-213` (pro forma rows are not sign-normalised, so an outflow is negative); `carrying_value` and CP-1's `total_debt` are book values (the carrying amount as filed), so the four notes become 1,987 / 1,487 / 1,193 / 1,088 (face 2,000 / 1,500 / 1,200 / 1,100 dropped: the Model has no face line) and total debt 11,792 (FY2025) and 11,705 (H1 2026), each citing the filing's whole `Face | Book | Book` line; the note states both conventions. `tests/model/test_expectation_ids.py` proves every expectation lands on its Model line and fails if a face value sits under `carrying_value`. | The Model owns the ids (interfaces §6; controller ruling). | 24 |

## File map

| Path | Responsibility | Task |
|---|---|---|
| `rbot/scripts/rbotlib/model/__init__.py`, `frame.py` | the package; cells, columns and sources (ported) | 2 |
| `rbot/scripts/rbotlib/model/reader.py` | figure rules (caos `_exact`), cell readers, `ModelInputError` | 2 |
| `rbot/scripts/rbotlib/model/registers.py` | the typed CP-1 registers and their vocabularies | 2 |
| `rbot/scripts/rbotlib/model/inputs.py` | CP-1's Model-input tables into registers | 3 |
| `rbot/scripts/rbotlib/model/_cells.py` | cell arithmetic and notes (ported) | 4 |
| `rbot/scripts/rbotlib/model/periods.py`, `history.py` | historical columns; account frames and the LTM (ported, caos `history.py` split) | 5, 6 |
| `rbot/scripts/rbotlib/model/debt.py`, `statements.py` | the debt stack; statements and the PF-LTM (ported) | 11, 12 |
| `rbot/scripts/rbotlib/model/metrics.py`, `layout.py`, `assemble.py` | credit metrics; bands and lines; the assembled Model (ported; projection removed; `gross_profit_growth`, `secured_debt` added) | 14, 16, 17 |
| `rbot/scripts/rbotlib/model/house_inputs.py`, `citations.py` | CP-1 identity and equity, CP-1D, Run Brief fields; MODEL.md citations | 20 |
| `rbot/scripts/rbotlib/model/house.py` | the house view (D19, §6.5) | 21 |
| `rbot/scripts/rbotlib/model/snapshot.py` | the §3.2 tables | 22 |
| `rbot/scripts/rbotlib/model/output.py`, `xlsx.py`, `run.py`, `rbotlib/cli.py`, `rbotlib/__init__.py` | `model.json`, MODEL.md, `model.xlsx`, `rbot model`, `__version__` | 23 |
| `docs/model/enums.md` | the vocabularies `rbot model` accepts | 20 |
| `tests/model/*` | ported caos tests split by topic, new tests, fixtures | every task |
| `tests/corpus/expectations/czr-2026q2-primary.json` | A10 | 24 |
| `scripts/mutate_model.sh`, `docs/model/mutation.md`, `pyproject.toml`, `uv.lock` | the mutation gate | 25 |
| `docs/corpus-runs/2026-10-11-plan-03-corpus-regression.md` | the corpus regression record | 26 |

Not ported, by design: caos `projection.py`, `cash_flow.py`, their tests and the 79 cash-flow goldens (Plan 13, `rbot model --projection`); caos's `Refusal` and `BoundaryText` (replaced by `ModelInputError` and the reader's cell rules).


---

### Task 1: Port kit: every ported file rebuilt from caos and checked

**Files:**
- Create: `$KIT/stage.sh`, `$KIT/keep.txt`, `$KIT/split_tests.py`, `$KIT/MANIFEST.sha256`, `$KIT/patches/*.patch`, `$KIT/specs/*.json`
- Modify: `.gitignore (committed in Task 2)`

**Interfaces:**
- Consumes: caos-databricks at `/Users/ericguei/Documents/caos-databricks`, commit `5c3cd52f` (each file read with `git -C … show 5c3cd52f:<path>`, nothing written there); the repo's locked `ruff` (0.17.0) and `uv`.
- Produces: `$KIT/out/` holding the 36 ported files at their repo paths (9 Model modules, 27 test modules), each equal to `$KIT/MANIFEST.sha256`. Later tasks copy from it. What the kit does to caos, in order: (1) `git -C <caos> show 5c3cd52f:<path>` each of the eight credit-model modules and seven test modules, one command per file (in `stage.sh`); (2) rewrite imports `caos.calculators.credit_model` → `rbotlib.model` and `caos.methodology.model_inputs` → `rbotlib.model.registers`; (3) `ruff check --select I --fix` and `ruff format` with the repo's settings; (4) split caos `history.py` into `periods.py` and `history.py` by line ranges (`keep.txt`), moving code without changing it; (5) apply the patches (projection removed from `assemble.py`; `gross_profit_growth` and the `secured_debt` memo line; tests cut to the ported scope); (6) split the five large test modules by topic (`split_tests.py`, by the explicit test lists in `specs/`); (7) `ruff check --select F401,I --fix`, `ruff format`; (8) `shasum -c` the manifest.

**Agent:** `mx-scaffold` (transcription only).

- [ ] **Step 1: Check the preconditions (Plan 02 merged)**

```bash
grep -c '"openpyxl==3.1.5"\|"types-openpyxl==3.1.5.20260827"' pyproject.toml
test -f docs/decisions/0003-openpyxl.md && test -f rbot/scripts/rbotlib/corpus.py && test -f tests/corpus/expectations/czr-2026q2-primary.json && echo ok
grep -c 'corpus: reads the local issuer corpus' pyproject.toml
uv run ruff --version
git -C /Users/ericguei/Documents/caos-databricks cat-file -t 5c3cd52f
```

Expected: `2`, `ok`, `1`, `ruff 0.17.0`, `commit`. Anything else: stop, report BLOCKED.

- [ ] **Step 2: Ignore the kit folder**

Append these two lines to `.gitignore` (they are committed with PR 03A1, Task 2):

```text
# Plan 03 port kit, rebuilt from caos by Task 1 (never committed).
/.port-03/
```

- [ ] **Step 3: Write the kit**

Run `mkdir -p .port-03/patches .port-03/specs` and `export KIT="$PWD/.port-03"` (in every shell that runs a later task), then write each file below under it.

`$KIT/stage.sh`:

```bash
#!/usr/bin/env bash
# Plan 03 port kit: rebuild every ported Model file from caos 5c3cd52f into
# $KIT/out, then check each against MANIFEST.sha256. Writes nothing outside $KIT.
# Usage: bash stage.sh <Deploy VI repo> <caos-databricks repo>
set -euo pipefail
REPO="$1"
CAOS="$2"
KIT="$(cd "$(dirname "$0")" && pwd)"
OUT="$KIT/out"
MODEL="$OUT/rbot/scripts/rbotlib/model"
rm -rf "$OUT" "$KIT/whole"
mkdir -p "$MODEL" "$OUT/tests/model" "$KIT/whole"
# Each caos file at 5c3cd52f, with the two import rewrites (the package and the register types).
rewrite() {
  sed -e 's/caos\.calculators\.credit_model/rbotlib.model/g' \
      -e 's/caos\.methodology\.model_inputs/rbotlib.model.registers/g'
}
TESTS="$OUT/tests/model"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/_cells.py | rewrite > "$MODEL/_cells.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/frame.py | rewrite > "$MODEL/frame.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/debt.py | rewrite > "$MODEL/debt.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/statements.py | rewrite > "$MODEL/statements.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/metrics.py | rewrite > "$MODEL/metrics.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/layout.py | rewrite > "$MODEL/layout.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/assemble.py | rewrite > "$MODEL/assemble.py"
git -C "$CAOS" show 5c3cd52f:caos/calculators/credit_model/history.py | rewrite > "$MODEL/history.py"
git -C "$CAOS" show 5c3cd52f:tests/credit_model_fixture.py | rewrite > "$TESTS/credit_model_fixture.py"
git -C "$CAOS" show 5c3cd52f:tests/test_credit_model_cells.py | rewrite > "$TESTS/test_credit_model_cells.py"
git -C "$CAOS" show 5c3cd52f:tests/test_credit_model_debt.py | rewrite > "$TESTS/test_credit_model_debt.py"
git -C "$CAOS" show 5c3cd52f:tests/test_credit_model_statements.py | rewrite > "$TESTS/test_credit_model_statements.py"
git -C "$CAOS" show 5c3cd52f:tests/test_credit_model_metrics.py | rewrite > "$TESTS/test_credit_model_metrics.py"
git -C "$CAOS" show 5c3cd52f:tests/test_credit_model_assemble.py | rewrite > "$TESTS/test_credit_model_assemble.py"
git -C "$CAOS" show 5c3cd52f:tests/test_credit_model_history.py | rewrite > "$TESTS/test_credit_model_history.py"
# The repo's ruff and settings; the kit folder is git-ignored, so ruff is told not to skip it.
ruff() { uv run --project "$REPO" ruff "$@" --no-cache --no-respect-gitignore --config "$REPO/pyproject.toml"; }
(cd "$OUT" && ruff check --select I --fix -q . && ruff format -q .)
# history.py splits into periods.py (the columns) and history.py (the frames).
sed -n "$(sed -n 's/^periods //p' "$KIT/keep.txt")" "$MODEL/history.py" > "$MODEL/periods.py"
sed -n "$(sed -n 's/^history //p' "$KIT/keep.txt")" "$MODEL/history.py" > "$MODEL/history.new"
mv "$MODEL/history.new" "$MODEL/history.py"
for p in "$KIT"/patches/*.patch; do
  patch -s -p1 -d "$OUT" < "$p"
done
# The big caos test modules split by topic (PRs stay under 800 lines).
for spec in "$KIT"/specs/*.json; do
  name="$(basename "$spec" .json)"
  mv "$OUT/tests/model/$name.py" "$KIT/whole/$name.py"
  uv run --project "$REPO" python "$KIT/split_tests.py" \
    "$KIT/whole/$name.py" "$spec" "$OUT/tests/model"
done
(cd "$OUT" && ruff check --select F401,I --fix -q tests/model && ruff format -q tests/model)
if [ "${NO_CHECK:-0}" != "1" ]; then
  (cd "$OUT" && shasum -a 256 -c "$KIT/MANIFEST.sha256")
fi
```

`$KIT/keep.txt`:

```text
periods 2,23p;86,89p;93,93p;95,96p;176,179p;186,205p;228,671p
history 23,90p;92,109p;115,115p;116,176p;180,185p;206,227p;672,1057p
```

`$KIT/split_tests.py`:

```python
"""Split one pytest module into topic modules plus shared helper modules.

Usage: python split_tests.py SOURCE.py SPEC.json OUT_DIR

SPEC: {"support": [{"file": "x_cases.py", "doc": "...", "names": ["_a", ...]},
                   {"file": "x_more.py", "doc": "...", "names": "*"}],
       "chunks": [{"file": "test_a.py", "doc": "...", "tests": ["test_x", ...],
                   "header_sub": [["old", "new"], ...]}, ...]}

Every top-level test function goes to the chunk naming it. A helper (any
other top-level statement after the imports) goes to the one chunk whose
tests use it, directly or through other helpers; a helper two or more
chunks use is shared and goes to the first support module naming it, or to
the support module whose names are "*" (helpers a shared helper uses are
shared too). A helper no test uses stays with the next test after it. Each
output keeps the source's import block (with the chunk's `header_sub`
replacements) plus imports of the shared helpers it uses, and the source
order. The caller then runs `ruff check --select F401,I --fix` and
`ruff format` on the outputs.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


def _span(node: ast.stmt, lines: list[str]) -> tuple[int, int]:
    decorators = getattr(node, "decorator_list", [])
    start = min([node.lineno, *(d.lineno for d in decorators)])
    while start > 1 and lines[start - 2].startswith("#"):
        start -= 1
    end = node.end_lineno
    assert end is not None
    return start, end


def _defines(node: ast.stmt) -> set[str]:
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        return {node.name}
    targets: list[ast.expr] = []
    if isinstance(node, ast.Assign):
        targets = list(node.targets)
    elif isinstance(node, ast.AnnAssign | ast.AugAssign):
        targets = [node.target]
    return {n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name)}


def _uses(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _is_test(node: ast.stmt) -> bool:
    return isinstance(node, ast.FunctionDef) and node.name.startswith("test_")


def _closure(users: dict[str, set[int]], helpers: dict[str, ast.stmt]) -> None:
    """A helper's users include the users of every helper that uses it."""
    changed = True
    while changed:
        changed = False
        for name, node in helpers.items():
            for used in _uses(node) & users.keys():
                if not users[name] <= users[used]:
                    users[used] |= users[name]
                    changed = True


def _shared(users: dict[str, set[int]], helpers: dict[str, ast.stmt]) -> set[str]:
    shared = {name for name, found in users.items() if len(found) > 1}
    changed = True
    while changed:
        changed = False
        for name in list(shared):
            for used in _uses(helpers[name]) & users.keys():
                if used not in shared:
                    shared.add(used)
                    changed = True
    return shared


def _module(doc: str, header: str, imports: list[str], blocks: list[str]) -> str:
    extra = "".join(f"\n{line}" for line in imports)
    return f'"""{doc}"""\n\n{header}{extra}\n\n\n' + "\n\n\n".join(blocks) + "\n"


def main(source: Path, spec_path: Path, out: Path) -> None:
    text = source.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    body = list(tree.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    imports = [n for n in body if isinstance(n, ast.Import | ast.ImportFrom)]
    rest = [n for n in body if not isinstance(n, ast.Import | ast.ImportFrom)]
    header = "\n".join(lines[imports[0].lineno - 1 : imports[-1].end_lineno])
    chunks = spec["chunks"]
    supports = spec.get("support") or []
    owner = {name: index for index, chunk in enumerate(chunks) for name in chunk["tests"]}
    helpers = {name: node for node in rest if not _is_test(node) for name in _defines(node)}
    users: dict[str, set[int]] = {name: set() for name in helpers}
    for node in rest:
        if _is_test(node):
            assert isinstance(node, ast.FunctionDef)
            assert node.name in owner, f"no chunk for {node.name}"
            for name in _uses(node) & users.keys():
                users[name].add(owner[node.name])
    _closure(users, helpers)
    shared = _shared(users, helpers)
    home: dict[str, int] = {}
    for name in sorted(shared):
        named = [i for i, s in enumerate(supports) if name in s["names"]]
        star = [i for i, s in enumerate(supports) if s["names"] == "*"]
        assert named or star, f"no support module for shared helper {name}"
        home[name] = (named or star)[0]
    outputs: dict[str, list[str]] = {chunk["file"]: [] for chunk in chunks}
    support_blocks: list[list[str]] = [[] for _ in supports]
    pending: list[str] = []
    for node in rest:
        start, end = _span(node, lines)
        block = "\n".join(lines[start - 1 : end])
        if _is_test(node):
            assert isinstance(node, ast.FunctionDef)
            outputs[chunks[owner[node.name]]["file"]].extend([*pending, block])
            pending = []
            continue
        names = _defines(node)
        if names & shared:
            homes = {home[n] for n in names & shared}
            assert len(homes) == 1, f"{names} split across support modules"
            support_blocks[homes.pop()].append(block)
            continue
        found = set().union(*(users[n] for n in names)) if names else set()
        if len(found) == 1:
            outputs[chunks[found.pop()]["file"]].append(block)
        else:
            pending.append(block)
    assert not pending, "helpers after the last test"
    out.mkdir(parents=True, exist_ok=True)

    def imports_for(blocks: list[str], before: int) -> list[str]:
        used = set().union(*(_uses(ast.parse(b)) for b in blocks)) if blocks else set()
        found = []
        for index, support in enumerate(supports[:before]):
            names = sorted(n for n in shared if home[n] == index and n in used)
            if names:
                found.append(
                    f"from {support['file'].removesuffix('.py')} import {', '.join(names)}"
                )
        return found

    for index, support in enumerate(supports):
        blocks = support_blocks[index]
        body_text = _module(support["doc"], header, imports_for(blocks, index), blocks)
        (out / support["file"]).write_text(body_text, encoding="utf-8")
    for chunk in chunks:
        blocks = outputs[chunk["file"]]
        chunk_header = header
        for old, new in chunk.get("header_sub", []):
            assert old in chunk_header, f"{chunk['file']}: {old!r} not in the imports"
            chunk_header = chunk_header.replace(old, new)
        body_text = _module(chunk["doc"], chunk_header, imports_for(blocks, len(supports)), blocks)
        (out / chunk["file"]).write_text(body_text, encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
```

`$KIT/specs/test_credit_model_assemble.json`:

```json
{
 "support": [
  {
   "file": "assemble_cases.py",
   "doc": "The worked-example Model and cell edits shared by the Model tests (split from\ncaos `tests/test_credit_model_assemble.py`).",
   "names": "*"
  }
 ],
 "chunks": [
  {
   "file": "test_credit_model_assemble.py",
   "doc": "The assembled Model: columns, ranks, limitations and reconciliation faults.",
   "tests": [
    "test_the_worked_example_reconciles_with_no_faults",
    "test_columns_run_history_then_the_pf_ltm",
    "test_a_rank_with_one_facility_has_no_subtotal",
    "test_a_rank_subtotal_sums_its_facilities_on_every_column",
    "test_a_model_has_no_projection_columns_until_the_projection_port",
    "test_limitations_list_each_note_once",
    "test_exclude_unrealised_drops_unrealised_addbacks_from_adjusted_ebitda_everywhere",
    "test_each_bridge_reports_a_figure_that_breaks_it",
    "test_a_fault_names_only_the_bridges_the_figure_is_in",
    "test_a_bridge_with_a_line_without_a_figure_is_not_checked",
    "test_unallocated_movements_are_not_applicable_on_history",
    "test_pf_ltm_accounts_show_the_ltm_with_pf_rows_beneath",
    "test_business_units_that_do_not_sum_to_revenue_are_noted",
    "test_a_note_on_revenue_keeps_cp1s_own",
    "test_cells_a_column_has_not_say_why",
    "test_a_rank_subtotal_without_any_facility_at_a_date_says_why"
   ]
  },
  {
   "file": "test_credit_model_layout.py",
   "doc": "Every band and line of the Model in order, with kind, unit and rank.",
   "tests": [
    "test_band_and_line_order_matches_the_layout"
   ]
  },
  {
   "file": "test_credit_model_assemble_lines.py",
   "doc": "Model lines: terms, metrics, PF rows, growth and any consistent inputs.",
   "tests": [
    "test_less_cash_is_closing_cash_negated",
    "test_facility_terms_are_shown_as_stated_never_rounded",
    "test_every_metric_in_the_frame_has_one_line",
    "test_a_foreign_facility_is_a_memo_outside_its_rank_total",
    "test_pf_rows_sit_by_the_line_they_adjust_and_reconcile",
    "test_a_model_without_segments_notes_nothing_on_revenue",
    "test_any_consistent_inputs_reconcile",
    "test_growth_lines_read_their_growth",
    "test_an_add_back_with_another_realisation_status_shows_it",
    "test_registers_without_periods_give_a_model_without_columns",
    "test_debt_bridges_count_a_facility_absent_at_a_date_as_nothing",
    "test_the_roll_forward_adds_its_pf_rows",
    "test_a_period_without_revenue_notes_nothing"
   ]
  },
  {
   "file": "test_credit_model_assemble_cases.py",
   "doc": "Model edge cases: foreign facilities, PF registers, negative zeros and bridges.",
   "tests": [
    "test_a_foreign_facility_is_noted_on_debt_interest_and_their_metrics",
    "test_a_pf_register_with_ebitda_and_adjusted_ebitda_rows_is_a_limitation",
    "test_no_cell_is_a_negative_zero",
    "test_the_pf_ltm_debt_roll_forward_foots",
    "test_a_debt_adjustment_classified_as_an_operating_lease_is_in_the_stack",
    "test_the_unallocated_line_has_no_payment_rank",
    "test_an_add_back_label_shows_the_status_that_excludes_it",
    "test_a_pf_facility_issued_after_the_ltm_sums_in_its_rank",
    "test_business_unit_growth_reads_the_like_period",
    "test_an_acquisition_reconciles_through_the_net_cash_flow",
    "test_the_interest_bridge_allows_exactly_its_last_digits",
    "test_a_pf_register_of_only_ebitda_and_adjusted_ebitda_rows_is_noted",
    "test_a_pf_refinancing_that_cuts_interest_raises_pf_coverage",
    "test_a_parenthesised_zero_is_never_a_negative_zero"
   ]
  }
 ]
}
```

`$KIT/specs/test_credit_model_debt.json`:

```json
{
 "support": [
  {
   "file": "debt_cases.py",
   "doc": "Debt frames shared by the debt tests (split from caos\n`tests/test_credit_model_debt.py`).",
   "names": "*"
  }
 ],
 "chunks": [
  {
   "file": "test_credit_model_debt.py",
   "doc": "The debt stack by payment rank, its totals and roll-forward.",
   "tests": [
    "test_payment_rank_maps_seniority_and_security",
    "test_facility_keys_name_the_totals_a_row_enters",
    "test_debt_totals_need_every_carrying_value",
    "test_a_column_without_facility_rows_has_no_debt",
    "test_undrawn_rcf_needs_commitment_and_drawn",
    "test_a_column_reads_its_own_period_first_then_any_ending_that_day",
    "test_stack_cells_carry_sources_and_need_no_cp1_total",
    "test_a_foreign_facility_without_a_value_keeps_its_note",
    "test_debt_totals_are_exact_beyond_the_default_precision",
    "test_an_account_the_register_never_states_is_not_sourced",
    "test_a_facility_without_an_opening_row_leaves_no_opening_debt",
    "test_a_facility_repaid_or_outside_total_debt_leaves_the_opening_whole",
    "test_a_foreign_facility_is_noted_on_the_totals_it_leaves",
    "test_a_debt_adjustment_classified_as_an_operating_lease_is_debt",
    "test_notes_of_splits_a_compound_note_at_each_separator",
    "test_carried_names_only_what_a_figure_leaves_out_in_order",
    "test_left_out_names_the_totals_a_row_in_another_currency_would_enter",
    "test_a_facility_first_issued_inside_the_column_opens_at_nil",
    "test_a_facility_written_as_a_negative_zero_is_zero"
   ]
  },
  {
   "file": "test_credit_model_debt_flows.py",
   "doc": "Debt totals and roll-forward against the statement frame (needs\n`rbotlib.model.statements`).",
   "tests": [
    "test_total_debt_excludes_operating_leases_and_includes_finance_leases",
    "test_debt_roll_forward_closes_to_the_stack"
   ]
  }
 ]
}
```

`$KIT/specs/test_credit_model_history.json`:

```json
{
 "support": [
  {
   "file": "history_cases.py",
   "doc": "Registers built from period ids, shared by the history tests (split from caos\n`tests/test_credit_model_history.py`).",
   "names": [
    "_Figures",
    "_QUARTER",
    "_YTD",
    "_period",
    "_regs",
    "_relabelled",
    "_halves"
   ]
  },
  {
   "file": "history_frames.py",
   "doc": "History frames and register edits shared by the history tests (split from\ncaos `tests/test_credit_model_history.py`).",
   "names": "*"
  }
 ],
 "chunks": [
  {
   "file": "test_credit_model_periods.py",
   "doc": "The Model's columns: which periods become quarters, PYTD, YTD, FY and LTM\ncolumns, and their labels and days.",
   "tests": [
    "test_columns_are_ordered_quarters_pytd_ytd_fy_ltm",
    "test_a_ytd_ending_on_the_fy_end_is_left_out",
    "test_a_ytd_without_a_fiscal_quarter_is_labelled_by_its_id",
    "test_the_fixture_half_years_are_derived_periods",
    "test_an_anchor_quarter_without_a_fiscal_quarter_has_no_ytd",
    "test_a_label_takes_the_four_digit_year_however_the_text_ends",
    "test_a_derived_start_is_a_calendar_day_no_later_than_the_end"
   ],
   "header_sub": [
    [
     "    historical_columns,\n",
     ""
    ],
    [
     "from rbotlib.model.registers import",
     "from rbotlib.model.periods import historical_columns\nfrom rbotlib.model.registers import"
    ]
   ]
  },
  {
   "file": "test_credit_model_history.py",
   "doc": "Historical columns and derived periods: quarters, PYTD, YTD, FY and LTM.",
   "tests": [
    "test_flow_and_balance_metrics_are_cp1_controlled_ids",
    "test_ytd_and_pytd_are_omitted_when_the_latest_period_is_a_fy_end",
    "test_a_derived_ltm_without_a_register_row_is_named_by_its_ytd",
    "test_ltm_equals_fy_plus_ytd_minus_pytd_for_every_flow",
    "test_a_ytd_with_components_is_their_sum_and_keeps_cp1_stated",
    "test_a_reported_quarter_is_never_replaced_by_a_calculated_one"
   ]
  },
  {
   "file": "test_credit_model_history_flows.py",
   "doc": "Derived flows and balances: calculated quarters, missing components, KPIs\nand the rolling LTM frames.",
   "tests": [
    "test_q2_and_q3_are_calculated_from_the_ytd_periods",
    "test_q4_is_calculated_from_fy_minus_9m_only_without_a_reported_q4",
    "test_a_derived_column_with_a_missing_component_is_component_missing",
    "test_a_calculated_quarter_with_a_missing_component_is_component_missing",
    "test_a_stated_ltm_that_differs_beyond_rounding_is_noted",
    "test_balances_take_the_column_end_period",
    "test_a_balance_on_a_calculated_quarter_is_its_end_period",
    "test_a_rate_kpi_is_not_sourced_on_a_derived_column",
    "test_period_flow_kpis_segments_and_addbacks_follow_the_flow_rules",
    "test_an_account_outside_both_lists_is_shown_only_for_its_own_period",
    "test_ltm_frames_sum_the_four_quarters_ending_each_quarter",
    "test_ltm_frames_include_calculated_quarters_and_refuse_a_gap",
    "test_derived_flows_reconcile_for_any_quarter_values"
   ]
  },
  {
   "file": "test_credit_model_history_registers.py",
   "doc": "Period registers of every shape: irregular periods, fiscal labels and the\nregister's own LTM.",
   "tests": [
    "test_an_irregular_period_is_kept_without_a_guess",
    "test_fiscal_quarters_read_with_or_without_a_q",
    "test_a_fiscal_year_without_four_digits_is_labelled_by_its_last_two",
    "test_undated_periods_are_never_the_latest",
    "test_a_register_ltm_ending_elsewhere_is_not_the_columns",
    "test_the_register_ltm_supplies_its_days_and_its_own_rates",
    "test_derived_sums_are_exact_past_the_default_precision",
    "test_the_ltm_needs_the_fiscal_year_before_the_ytd",
    "test_a_q1_only_year_builds_its_ytd_and_pytd_from_quarters",
    "test_a_ytd_from_quarters_needs_every_quarter_to_date",
    "test_a_register_ltm_later_than_the_host_can_build_is_kept_unadopted",
    "test_a_stated_figure_in_hundreds_is_rounding_within_fifty",
    "test_a_register_with_only_an_ltm_row_keeps_it_unadopted",
    "test_quarters_to_date_make_the_ytd_and_pytd_without_ytd_rows",
    "test_an_undated_register_ltm_is_kept_unadopted",
    "test_a_fiscal_year_reads_as_its_four_digit_year_however_written"
   ]
  },
  {
   "file": "test_credit_model_history_sparse.py",
   "doc": "Sparse items: a figure resolved from the periods that tile it, bottom up.",
   "tests": [
    "test_an_absent_row_is_not_sourced_and_a_null_row_not_stated_or_missing",
    "test_an_addback_without_a_row_for_a_period_counts_zero_in_a_sum",
    "test_a_sparse_item_resolves_each_period_bottom_up",
    "test_a_sparse_item_with_a_null_row_it_uses_is_component_missing",
    "test_financing_lines_are_sparse",
    "test_a_sparse_period_resolves_only_through_dated_existing_parts",
    "test_a_flow_that_is_not_sparse_never_resolves_from_its_parts",
    "test_a_sparse_period_is_covered_greedily_by_its_longest_parts",
    "test_a_sparse_own_row_wins_and_is_noted_where_its_parts_differ",
    "test_a_sparse_own_row_over_a_gap_is_never_compared_with_a_partial_cover",
    "test_a_sparse_year_with_its_own_row_and_only_h1_below_keeps_its_row",
    "test_a_sparse_period_without_a_row_over_a_gap_is_component_missing",
    "test_a_complete_tiling_still_resolves_from_parts_and_notes_a_disagreement",
    "test_a_sparse_figure_from_parts_comes_only_from_parts_that_tile_it",
    "test_a_cover_reaches_the_last_day_of_the_period",
    "test_parts_with_the_same_dates_are_taken_in_register_order",
    "test_a_part_whose_components_do_not_span_it_leaves_its_days_unknown",
    "test_a_twin_without_a_row_is_never_nothing_over_the_period"
   ]
  },
  {
   "file": "test_credit_model_history_dates.py",
   "doc": "Signs, dates and day counts: outflows written positive, malformed dates and\ncomponents that do not span their period.",
   "tests": [
    "test_outflow_metrics_are_cp1s_sign_agnostic_outflows",
    "test_an_outflow_row_written_positive_is_negative_before_any_sum",
    "test_sixteen_nested_ltm_periods_resolve_a_sparse_item_in_under_a_second",
    "test_a_date_or_day_count_that_is_not_one_never_raises",
    "test_a_derived_period_whose_components_do_not_span_it_is_missing",
    "test_components_in_any_order_that_span_the_period_are_summed",
    "test_two_year_fiscal_spellings_read_as_the_end_year_throughout",
    "test_an_ltm_whose_fiscal_year_does_not_meet_its_ytd_is_missing",
    "test_a_sparse_period_takes_an_equal_twins_own_row_and_nothing_more",
    "test_every_register_row_keeps_its_source",
    "test_a_sparse_own_row_written_positive_keeps_its_note",
    "test_a_one_day_component_spans_its_day",
    "test_a_cover_part_resolves_through_its_components_but_a_twin_does_not",
    "test_an_unbuilt_ltm_keeps_cp1s_figure_as_stated",
    "test_quarters_to_date_meet_the_year_by_their_days_without_a_start",
    "test_a_period_without_a_start_date_starts_its_day_count_before_its_end",
    "test_a_ytd_built_from_quarters_with_a_gap_does_not_meet_the_year"
   ]
  },
  {
   "file": "test_credit_model_history_interims.py",
   "doc": "Prior-year YTDs found by dates, and LTMs never built from a one-sided interim.",
   "tests": [
    "test_an_unlabelled_ytd_finds_its_prior_year_ytd_by_its_dates",
    "test_a_labelled_register_still_finds_its_prior_year_ytd_by_label",
    "test_a_prior_year_ytd_the_dates_leave_ambiguous_is_no_pytd",
    "test_without_a_prior_year_ytd_the_ltm_is_missing_un_noted",
    "test_the_prior_year_ytd_by_dates_is_the_one_of_the_same_months",
    "test_a_labelled_ytd_falls_back_to_quarters_past_a_ytd_of_other_months",
    "test_whole_months_reads_a_span_from_a_first_day_to_a_last_day",
    "test_an_ltm_is_never_built_from_a_one_sided_interim",
    "test_a_sparse_ltm_needs_its_fy_when_an_interim_is_stated",
    "test_partly_stated_reads_the_three_terms_of_a_rolled_ltm"
   ]
  },
  {
   "file": "test_credit_model_history_model.py",
   "doc": "History read through the whole Model (needs `rbotlib.model.assemble`).",
   "tests": [
    "test_the_audits_h1_2026_written_positive_keeps_the_ltm_coverage",
    "test_a_one_sided_interim_leaves_the_ltm_cash_flow_missing"
   ]
  }
 ]
}
```

`$KIT/specs/test_credit_model_metrics.json`:

```json
{
 "support": [
  {
   "file": "metrics_cases.py",
   "doc": "Metric frames and expected ratios shared by the metric tests (split from caos\n`tests/test_credit_model_metrics.py`).",
   "names": "*"
  }
 ],
 "chunks": [
  {
   "file": "test_credit_model_metrics.py",
   "doc": "Credit metrics: leverage, coverage and ratios per column, with reasons.",
   "tests": [
    "test_quarter_leverage_uses_the_ltm_ending_that_quarter",
    "test_ytd_leverage_is_not_applicable",
    "test_each_metric_has_reported_and_adjusted_variants_where_named",
    "test_units_are_multiples_for_leverage_and_coverage",
    "test_every_column_carries_every_metric_and_keeps_its_cells",
    "test_a_non_positive_denominator_is_zero_or_negative",
    "test_a_missing_input_gives_its_reason_first_in_formula_order"
   ]
  },
  {
   "file": "test_credit_model_metrics_growth.py",
   "doc": "Credit metrics: growth, PF-LTM variants, leases and what a metric leaves out.",
   "tests": [
    "test_growth_compares_like_periods",
    "test_growth_takes_a_like_period_within_a_week_of_a_year_earlier",
    "test_projected_growth_needs_a_four_digit_year",
    "test_pf_leverage_uses_pf_debt_and_pf_ebitda",
    "test_pf_reported_ebitda_variants_are_not_applicable",
    "test_pf_margins_with_a_revenue_adjustment",
    "test_lease_adjusted_metrics_read_the_lease_balances",
    "test_corporate_names_only_segments",
    "test_ltm_growth_reads_the_ltm_ending_a_year_earlier",
    "test_a_metric_carries_what_its_debt_or_interest_leaves_out"
   ]
  }
 ]
}
```

`$KIT/specs/test_credit_model_statements.json`:

```json
{
 "support": [
  {
   "file": "statements_cases.py",
   "doc": "Statement frames shared by the statement tests (split from caos\n`tests/test_credit_model_statements.py`).",
   "names": "*"
  }
 ],
 "chunks": [
  {
   "file": "test_credit_model_statements.py",
   "doc": "Statements: income to adjusted EBITDA, the cash-flow waterfall and add-backs.",
   "tests": [
    "test_the_waterfall_reconciles_ffo_plus_wc_to_cfo_adjusted",
    "test_ebitda_stated_differs_note",
    "test_expense_metrics_written_positive_read_the_same",
    "test_cfo_adjusted_removes_lease_and_interest_classified_in_financing",
    "test_ncf_equals_reported_net_cash_change",
    "test_dio_and_dpo_are_null_when_cogs_is_not_negative",
    "test_exclude_unrealised_leaves_unrealised_and_not_stated_addbacks_out"
   ]
  },
  {
   "file": "test_credit_model_statements_pro_forma.py",
   "doc": "Statements: pro forma columns, any consistent accounts reconciling, sources and\nstated figures.",
   "tests": [
    "test_adjusted_ebitda_needs_every_addback",
    "test_a_missing_account_is_not_sourced_and_its_lines_component_missing",
    "test_pro_forma_adds_each_adjustment_once_and_blanks_the_waterfall",
    "test_pro_forma_revenue_and_total_debt_adjustments",
    "test_pro_forma_is_none_without_adjustments_for_the_ltm",
    "test_every_bridge_reconciles_for_any_consistent_accounts",
    "test_pro_forma_new_facility_unknown_metric_and_a_missing_line",
    "test_a_column_without_days_has_no_opening_balances_or_days_ratios",
    "test_lines_keep_their_sources_and_cp1_stated_figures",
    "test_adjusted_ebitda_differs_note_unless_unrealised_are_excluded",
    "test_days_ratios_divide_by_any_positive_flow_and_need_the_balance",
    "test_pro_forma_keeps_a_foreign_note_drops_a_differs_note_and_is_exact"
   ]
  },
  {
   "file": "test_credit_model_statements_cases.py",
   "doc": "Statements: absent rows, sparse items, foreign facilities and PF adjustments.",
   "tests": [
    "test_an_addback_without_a_row_contributes_zero_and_a_null_one_is_missing",
    "test_financing_lease_and_interest_without_rows_count_zero_in_cfo_adjusted",
    "test_a_pro_forma_ebitda_adjustment_adds_to_ebitda_and_adjusted_ebitda",
    "test_exclude_unrealised_compares_stated_where_nothing_was_excluded",
    "test_a_sparse_addback_and_financing_line_resolve_bottom_up",
    "test_an_all_absent_financing_line_with_a_stated_figure_counts_zero",
    "test_an_excluded_addback_absent_on_a_column_leaves_nothing_out",
    "test_a_foreign_facility_is_noted_on_every_debt_balance_it_leaves",
    "test_a_pf_adjustment_is_a_change_and_keeps_cp1s_sign",
    "test_a_pf_facility_with_no_ltm_row_starts_from_zero",
    "test_the_pf_debt_roll_forward_opens_at_the_ltm_and_closes_with_the_pf",
    "test_an_outflow_of_zero_is_no_negative_zero",
    "test_excluded_addbacks_are_those_with_any_row_unrealised_or_not_stated",
    "test_a_pf_adjustment_is_never_flipped_and_never_a_negative_zero"
   ]
  }
 ]
}
```

`$KIT/patches/assemble.patch`:

```diff
--- a/rbot/scripts/rbotlib/model/assemble.py
+++ b/rbot/scripts/rbotlib/model/assemble.py
@@ -3,9 +3,10 @@
 `credit_model` runs the calculator end to end: the historical columns and
 CP-1's figures over them, the statements (with "exclude unrealised" on every
 frame, the LTM ending each quarter included), the PF-LTM where the register
-has adjustments to the LTM, the projections where CP-CF ran, the credit
-metrics, then the layout. Columns run quarters, PYTD, YTD, FY, LTM, PF-LTM,
-then the Base years and the Downside years (spec M2).
+has adjustments to the LTM, the credit metrics, then the layout. Columns
+run quarters, PYTD, YTD, FY, LTM, then PF-LTM (spec M2). Deploy VI port: the
+projections (caos `projection.py`, CP-2G and CP-CF) arrive with Plan 13, so
+every model notes `NO_PROJECTIONS` and has no rate deck.
 
 `reconciliation_faults` checks these bridges on the assembled model, by line
 and column, on exact Decimal equality (the calculator never rounds):
@@ -56,11 +57,10 @@
 from collections.abc import Mapping
 from dataclasses import dataclass
 from decimal import Decimal, localcontext
-from typing import Any
 
 from rbotlib.model._cells import CONTEXT
 from rbotlib.model.debt import notes_of
-from rbotlib.model.frame import Cell, Column, Frame
+from rbotlib.model.frame import Cell, Column
 from rbotlib.model.history import (
     account_frame,
     historical_columns,
@@ -68,16 +68,7 @@
 )
 from rbotlib.model.layout import BANDS, UNALLOCATED, Line, layout
 from rbotlib.model.metrics import metric_frame
-from rbotlib.model.projection import (
-    ProjectionInputs,
-    RateDeck,
-    projection,
-)
-from rbotlib.model.registers import (
-    Cp1Registers,
-    DivisionGrowth,
-    SlotAllocation,
-)
+from rbotlib.model.registers import Cp1Registers
 from rbotlib.model.statements import (
     pro_forma_column,
     statement_frame,
@@ -111,30 +102,7 @@
 @dataclass(frozen=True, slots=True)
 class ModelInputs:
     registers: Cp1Registers
-    request: Mapping[str, Any] | None  # CP-CF's accepted request; None without
-    growth: tuple[DivisionGrowth, ...]
-    slots: tuple[SlotAllocation, ...]
-    deck: RateDeck | None
     exclude_unrealised: bool = False
-
-
-def _projected(inputs: ModelInputs, history: Frame) -> tuple[tuple[Column, ...], Frame]:
-    """The projected columns, Base years then Downside years, and their
-    frame; none without CP-CF's request."""
-    if inputs.request is None:
-        return (), {}
-    columns, frame = projection(
-        ProjectionInputs(
-            regs=inputs.registers,
-            request=inputs.request,
-            growth=inputs.growth,
-            slots=inputs.slots,
-            deck=inputs.deck,
-            history=history,
-        )
-    )
-    ordered = sorted(columns, key=lambda column: column.case == "DOWNSIDE")
-    return tuple(ordered), frame
 
 
 def _pro_forma_limitations(
@@ -157,23 +125,21 @@
     """The missing projections; the pro forma limitations; then each
     distinct cell note (each component of a compound one) with the columns
     it is on, in line order."""
-    model = [] if inputs.request is not None else [NO_PROJECTIONS]
     notes: dict[str, dict[str, None]] = {}
     for line in lines:
         for column, cell in zip(columns, line.cells, strict=True):
             for note in notes_of(cell.note):
                 notes.setdefault(note, {})[column.column_id] = None
     return (
-        *model,
+        NO_PROJECTIONS,
         *_pro_forma_limitations(inputs, columns, lines),
         *(f"{note}: {', '.join(on)}" for note, on in notes.items()),
     )
 
 
 def credit_model(inputs: ModelInputs) -> CreditModel:
-    """The credit model of CP-1's registers, with CP-2G and CP-CF's
-    projections where `request` is CP-CF's accepted request: every column,
-    every line and the limitations its cells note."""
+    """The credit model of CP-1's registers: every column, every line and
+    the limitations its cells note."""
     regs = inputs.registers
     exclude = inputs.exclude_unrealised
     historical = historical_columns(regs)
@@ -185,9 +151,6 @@
     if pro_forma is not None:
         columns.append(pro_forma[0])
         frame.update(pro_forma[1])
-    projected, projected_frame = _projected(inputs, history)
-    columns.extend(projected)
-    frame.update(projected_frame)
     quarters = tuple(column for column in historical if column.kind == "QUARTER")
     ltm_ending = statement_frame(ltm_frames(regs, historical), quarters, regs, exclude)
     corporate = frozenset(
@@ -195,14 +158,13 @@
     )
     every = tuple(columns)
     metrics = metric_frame(every, frame, ltm_ending, corporate=corporate)
-    deck = inputs.deck if inputs.request is not None else None
-    lines = layout(regs, every, metrics, exclude, deck.as_of if deck else None)
+    lines = layout(regs, every, metrics, exclude, None)
     return CreditModel(
         currency=regs.currency,
         unit=regs.unit,
         columns=every,
         lines=lines,
-        rate_deck_id=deck.deck_id if deck else None,
+        rate_deck_id=None,
         limitations=_limitations(inputs, every, lines),
     )
 
```

`$KIT/patches/credit_model_fixture.patch`:

```diff
--- a/tests/model/credit_model_fixture.py
+++ b/tests/model/credit_model_fixture.py
@@ -23,21 +23,17 @@
 
 from dataclasses import replace
 from decimal import Decimal
-from typing import Any
-
-from rbotlib.model.frame import Case, SourceRef
-from rbotlib.model.projection import RateDeck, RateDeckYear
+
+from rbotlib.model.frame import SourceRef
 from rbotlib.model.registers import (
     AccountRow,
     AddbackRow,
     Cp1Registers,
-    DivisionGrowth,
     FacilityRow,
     KpiRow,
     PeriodRow,
     PfAdjustmentRow,
     SegmentRow,
-    SlotAllocation,
 )
 
 _PERIODS = """
@@ -520,142 +516,3 @@
         currency="USD",
         unit="MILLIONS",
     )
-
-
-# The projections (CP-2G and CP-CF), the worked example's Base and Downside
-# cases. CP-2G binds three division slots; managed and other is in none, so
-# the host holds it flat. Each year's growth by slot:
-_GROWTH = """
-case     year DIVISION_1 DIVISION_2 DIVISION_3
-BASE     2026      0.025      0.010       0.10
-BASE     2027      0.030      0.015       0.08
-BASE     2028      0.030      0.015       0.06
-DOWNSIDE 2026      -0.06      -0.04       0.02
-DOWNSIDE 2027      -0.03      -0.02       0.03
-DOWNSIDE 2028       0.01       0.01       0.04
-"""
-_CASES: dict[str, Case] = {"BASE": "BASE", "DOWNSIDE": "DOWNSIDE"}
-_SLOTS = {"DIVISION_1": "las_vegas", "DIVISION_2": "regional", "DIVISION_3": "digital"}
-
-# CP-CF's drivers, unsigned: revenue is the slot growth on FY2025's business
-# units (rounded), EBITDA the example's margin on its revenue, `cfo` before
-# interest and taxes (EBITDA less lease cash 16, other 80 and the working
-# capital outflow), distributions the buybacks. Base sweeps cash to the term
-# loan. The stated closings follow CP-CF's own roll-forward from FY2025.
-_DRIVERS = """
-case     year revenue ebitda  cfo interest taxes capex distrib repaid  debt cash
-BASE     2026   11809   4136 4025      859   170  1700     400    822 13012 1030
-BASE     2027   12138   4290 4179      798   180  1650     400   1097 11891 1060
-BASE     2028   12451   4427 4316      728   190  1600     400    337 11530 2097
-DOWNSIDE 2026   11062   3319 3183      882   120  1500       0      0 13834 1637
-DOWNSIDE 2027   10872   3099 2983      894   100  1300       0      0 13810 2302
-DOWNSIDE 2028   11018   3196 3090      889   110  1200       0      0 13786 3169
-"""
-_FY2025_DEBT = {  # CP-CF's opening: CP-1's total debt, finance lease excluded
-    "rcf": "0",
-    "tlb": "2328",
-    "ssn29": "2000",
-    "ssn31": "1000",
-    "sun29": "3600",
-    "sun32": "3500",
-    "sub27": "1600",
-    "disc": "-170",
-}
-# The SOFR deck, as decimals: FY+1 is FY2026.
-_DECK = (
-    ("1", "0.0380", "0.0480"),
-    ("2", "0.0340", "0.0540"),
-    ("3", "0.0325", "0.0525"),
-)
-
-
-def example_growth() -> tuple[DivisionGrowth, ...]:
-    """CP-2G's division growth, a decimal fraction per case, year and slot."""
-    lines = _GROWTH.strip().splitlines()
-    slots = lines[0].split()[2:]
-    return tuple(
-        DivisionGrowth(_CASES[case], year, slot, Decimal(value))
-        for case, year, *values in (line.split() for line in lines[1:])
-        for slot, value in zip(slots, values, strict=True)
-    )
-
-
-def example_slots() -> tuple[SlotAllocation, ...]:
-    """CP-1's slot allocation: one segment per division slot."""
-    return tuple(SlotAllocation(slot, (segment,)) for slot, segment in _SLOTS.items())
-
-
-def example_deck() -> RateDeck:
-    """The pinned rate deck: SOFR for FY+1 to FY+3, Base and Downside."""
-    return RateDeck(
-        deck_id="deck-1",
-        as_of="2026-10-01",
-        years=tuple(
-            RateDeckYear("SOFR", int(offset), Decimal(base), Decimal(downside))
-            for offset, base, downside in _DECK
-        ),
-    )
-
-
-def example_request() -> dict[str, Any]:
-    """CP-CF's accepted request: FY2026-FY2028 for Base and Downside, from
-    FY2025's closing debt and cash, the term loan amortising 24 a year."""
-    rows = [line.split() for line in _DRIVERS.strip().splitlines()[1:]]
-    drivers = []
-    for case, year, revenue, ebitda, cfo, interest, taxes, capex, *rest in rows:
-        distributions, optional, debt, cash = rest
-        drivers.append(
-            {
-                "case": case,
-                "period_id": f"FY{year}",
-                "status": "READY",
-                "stated_closing_debt": debt,
-                "stated_closing_cash": cash,
-                "revenue": revenue,
-                "ebitda": ebitda,
-                "cfo": cfo,
-                "capex": capex,
-                "acquisitions_disposals": "0",
-                "cash_interest": interest,
-                "cash_taxes": taxes,
-                "distributions": distributions,
-                "issuance": "0",
-                "optional_repayment": optional,
-                "pik": "0",
-                "capitalised_interest": "0",
-                "fx_perimeter": "0",
-            }
-        )
-    return {
-        "opening": {
-            "cash": "980",
-            "as_of_period_id": "FY2025",
-            "debt_by_facility": [
-                {"facility_id": facility_id, "amount": amount}
-                for facility_id, amount in _FY2025_DEBT.items()
-            ],
-        },
-        "periods": [
-            {
-                "case": row[0],
-                "period_id": f"FY{row[1]}",
-                "fiscal_year": row[1],
-                "days": "365",
-            }
-            for row in rows
-        ],
-        "drivers": drivers,
-        "contractual": {
-            "amortisation": [
-                {
-                    "case": row[0],
-                    "period_id": f"FY{row[1]}",
-                    "facility_id": "tlb",
-                    "amount": "24",
-                }
-                for row in rows
-            ]
-        },
-        "units": {"currency": "USD", "scale": "millions"},
-        "perimeter": "Example Gaming Co. consolidated",
-    }
```

`$KIT/patches/history.patch`:

```diff
--- a/rbot/scripts/rbotlib/model/history.py
+++ b/rbot/scripts/rbotlib/model/history.py
@@ -1,3 +1,5 @@
+"""CP-1's figures over the historical columns (spec M2); the columns
+themselves are `periods`.
 
 The LTM's FY must end the day before its YTD starts, and its PYTD start
 with that FY; otherwise its flows are `COMPONENT_MISSING`, noted
@@ -66,6 +68,7 @@
 from __future__ import annotations
 
 import operator
+from collections.abc import Iterable, Iterator
 from dataclasses import dataclass, field, replace
 from datetime import date
 from decimal import Decimal, localcontext
@@ -84,7 +87,18 @@
     refs,
 )
 from rbotlib.model.frame import Cell, Column, Frame, SourceRef
+from rbotlib.model.periods import (
+    _ADDITIVE,
+    _dated,
+    _first_day,
+    _plan,
+    _quarter_index,
+    _Spec,
 )
+from rbotlib.model.periods import (
+    historical_columns as historical_columns,
+)
+from rbotlib.model.registers import Cp1Registers, PeriodRow
 
 FLOW_METRICS = frozenset(
     {
```

`$KIT/patches/layout.patch`:

```diff
--- a/rbot/scripts/rbotlib/model/layout.py
+++ b/rbot/scripts/rbotlib/model/layout.py
@@ -279,6 +279,13 @@
         _plain("cogs", "Cost of revenue"),
         _plain("gross_profit", "Gross profit", "SUBTOTAL"),
         _ratio("gross_margin", "Gross margin"),
+        _Spec(
+            "gross_profit_growth",
+            "gross_profit_growth",
+            "Gross profit growth YoY",
+            "GROWTH",
+            unit="PERCENT",
+        ),
     ]
     opex = [
         _plain("opex_ex_da", "Operating expenses excluding D&A"),
@@ -461,6 +468,7 @@
         unallocated,
         *pf.get("total_debt", []),
         _plain("total_debt", "Total debt", "SUBTOTAL"),
+        _plain("secured_debt", "Memo: senior secured debt", "MEMO"),
         replace(
             _plain("lease_liabilities", "Operating lease liabilities"),
             unadjusted=True,
```

`$KIT/patches/metrics.patch`:

```diff
--- a/rbot/scripts/rbotlib/model/metrics.py
+++ b/rbot/scripts/rbotlib/model/metrics.py
@@ -122,8 +122,9 @@
 # EBITDA margins: not applicable on the PF-LTM unless its revenue is adjusted
 # too (acquired EBITDA over unadjusted revenue is no margin).
 _PF_MARGINS = frozenset({"ebitda_margin", "adjusted_ebitda_margin"})
-_GROWTH = ("revenue", "adjusted_ebitda")
-_GROWTH_KEYS = frozenset({"revenue_growth", "adjusted_ebitda_growth"})
+# Deploy VI adds gross profit growth (spec §6.3) for the Credit Snapshot.
+_GROWTH = ("revenue", "gross_profit", "adjusted_ebitda")
+_GROWTH_KEYS = frozenset({"revenue_growth", "gross_profit_growth", "adjusted_ebitda_growth"})
 _LIKE = {"QUARTER": "QUARTER", "YTD": "PYTD", "FY": "FY", "LTM": "LTM"}
 _YEAR = 365
 _WEEK = 7  # a 52- or 53-week year ends within a week of the calendar year
```

`$KIT/patches/periods.patch`:

```diff
--- a/rbot/scripts/rbotlib/model/periods.py
+++ b/rbot/scripts/rbotlib/model/periods.py
@@ -1,3 +1,6 @@
+"""The historical columns (spec M2), split from caos `history.py`: which
+columns a register gives and how each is built from register periods;
+`history` reads CP-1's figures over them.
 
 Columns run quarters, PYTD, YTD, FY, then LTM. Every reported quarter is a
 column; where CP-1's period register has no quarter, one is calculated as
@@ -20,13 +23,19 @@
 its flows `COMPONENT_MISSING` with CP-1's figure as `stated` (spec M4: the
 host recomputes, it never adopts CP-1's arithmetic).
 
+Pure: no I/O.
 """
 
 from __future__ import annotations
 
+from collections.abc import Iterable, Mapping
+from dataclasses import dataclass, replace
 from datetime import date
 from typing import Literal
 
+from rbotlib.model._cells import UNSPANNED
+from rbotlib.model.frame import Column
+from rbotlib.model.registers import Cp1Registers, PeriodRow, fiscal_year_number, iso_date
 
 _YTD_LABELS = {1: "Q1", 2: "H1", 3: "9M", 4: "12M"}
 _QUARTERS = {f"{prefix}{n}": n for n in range(1, 5) for prefix in ("", "Q")}
```

`$KIT/patches/test_credit_model_assemble.patch`:

```diff
--- a/tests/model/test_credit_model_assemble.py
+++ b/tests/model/test_credit_model_assemble.py
@@ -5,17 +5,9 @@
 
 from dataclasses import replace
 from decimal import Decimal, localcontext
-from typing import Any
 
 import pytest
-from credit_model_fixture import (
-    example_deck,
-    example_growth,
-    example_registers,
-    example_request,
-    example_slots,
-    with_figures,
-)
+from credit_model_fixture import example_registers, with_figures
 from hypothesis import example, given, settings
 from hypothesis import strategies as st
 
@@ -45,36 +37,11 @@
 
 _PF = "PF:LTM_Q2_2026"
 _LTM = "LTM:LTM_Q2_2026"
-_BASE = "BASE:2026"
-
-
-def _inputs(
-    regs: Cp1Registers | None = None,
-    request: dict[str, Any] | None = None,
-    *,
-    projected: bool = True,
-    exclude_unrealised: bool = False,
-) -> ModelInputs:
-    return ModelInputs(
-        registers=regs or example_registers(),
-        request=(request or example_request()) if projected else None,
-        growth=example_growth(),
-        slots=example_slots(),
-        deck=example_deck(),
-        exclude_unrealised=exclude_unrealised,
-    )
-
-
-def _model(
-    regs: Cp1Registers | None = None,
-    request: dict[str, Any] | None = None,
-    *,
-    projected: bool = True,
-    exclude_unrealised: bool = False,
-) -> CreditModel:
-    return credit_model(
-        _inputs(regs, request, projected=projected, exclude_unrealised=exclude_unrealised)
-    )
+
+
+def _model(regs: Cp1Registers | None = None, *, exclude_unrealised: bool = False) -> CreditModel:
+    inputs = ModelInputs(regs or example_registers(), exclude_unrealised=exclude_unrealised)
+    return credit_model(inputs)
 
 
 def _line(model: CreditModel, line_id: str) -> Line:
@@ -120,7 +87,7 @@
     assert reconciliation_faults(model) == ()
     assert model.currency == "USD"
     assert model.unit == "MILLIONS"
-    assert model.rate_deck_id == "deck-1"
+    assert model.rate_deck_id is None
 
 
 # (band index, line_id, kind, unit, rank, label), the worked example's order.
@@ -166,6 +133,7 @@
     (2, "cogs", "ACCOUNT", "MONEY", None, "Cost of revenue"),
     (2, "gross_profit", "SUBTOTAL", "MONEY", None, "Gross profit"),
     (2, "metric:gross_margin", "RATIO", "PERCENT", None, "Gross margin"),
+    (2, "gross_profit_growth", "GROWTH", "PERCENT", None, "Gross profit growth YoY"),
     # Operating expenses to EBITDA
     (3, "opex_ex_da", "ACCOUNT", "MONEY", None, "Operating expenses excluding D&A"),
     (3, "da", "ACCOUNT", "MONEY", None, "Depreciation and amortisation"),
@@ -412,6 +380,7 @@
         "Unallocated movements (CP-CF)",
     ),
     (7, "total_debt", "SUBTOTAL", "MONEY", None, "Total debt"),
+    (7, "secured_debt", "MEMO", "MONEY", None, "Memo: senior secured debt"),
     (7, "lease_liabilities", "ACCOUNT", "MONEY", None, "Operating lease liabilities"),
     (7, "lease_adjusted_debt", "SUBTOTAL", "MONEY", None, "Lease-adjusted debt"),
     (7, "less_cash", "ACCOUNT", "MONEY", None, "Less: cash and equivalents"),
@@ -458,7 +427,7 @@
         "ACCOUNT",
         "RATE",
         None,
-        "Reference rate, rate deck 2026-10-01",
+        "Reference rate",
     ),
     (
         9,
@@ -639,10 +608,8 @@
     assert all(line.unit_label is None for line in model.lines if line.unit != "KPI")
 
 
-def test_columns_run_history_pf_then_base_years_then_downside_years() -> None:
-    request = example_request()
-    request["periods"] = sorted(request["periods"], key=lambda p: p["case"] == "BASE")
-    model = _model(request=request)
+def test_columns_run_history_then_the_pf_ltm() -> None:
+    model = _model()
     assert [c.column_id for c in model.columns] == [
         *(f"Q:Q{q}_{y}" for y in (2024, 2025) for q in (1, 2, 3, 4)),
         "Q:Q1_2026",
@@ -654,12 +621,6 @@
         "FY:FY2025",
         _LTM,
         _PF,
-        "BASE:2026",
-        "BASE:2027",
-        "BASE:2028",
-        "DOWNSIDE:2026",
-        "DOWNSIDE:2027",
-        "DOWNSIDE:2028",
     ]
 
 
@@ -685,12 +646,11 @@
         )
         assert _value(model, "rank:Senior secured", column.column_id) == secured
     assert _value(model, "rank:Senior secured", _PF) == 2316 + 2000 + 1600
-    assert _value(model, "rank:Senior secured", _BASE) == (2328 - 24) + 2000 + 1000
     assert _cell(model, "rank:Senior secured", _LTM).basis == "CALCULATED"
 
 
-def test_a_run_without_cp_cf_has_no_projection_columns() -> None:
-    model = _model(projected=False)
+def test_a_model_has_no_projection_columns_until_the_projection_port() -> None:
+    model = _model()
     assert all(column.kind != "PROJECTED" for column in model.columns)
     assert model.columns[-1].column_id == _PF
     assert model.limitations[0] == NO_PROJECTIONS
@@ -699,7 +659,6 @@
     for key in ("reference_rate", "interest_bearing_debt_opening", "wa_rate"):
         assert {cell.reason for cell in _line(model, key).cells} == {"NOT_APPLICABLE"}
     assert reconciliation_faults(model) == ()
-    assert NO_PROJECTIONS not in _model().limitations
 
 
 def test_limitations_list_each_note_once() -> None:
@@ -709,7 +668,6 @@
     for note in {cell.note for line in model.lines for cell in line.cells} - {None}:
         assert note in notes
     on = dict(text.split(": ", 1) for text in model.limitations)
-    assert on["assumed refinanced"] == "BASE:2027, DOWNSIDE:2027"
     assert on["residual"].split(", ")[0] == "Q:Q1_2024"
     # On the PF-LTM only the roll-forward's residual, the LTM's, is shown.
     assert _PF in on["residual"].split(", ")
@@ -731,11 +689,6 @@
     )
     dropped = 0
     for column in excluded.columns:
-        if column.kind == "PROJECTED":
-            assert _cell(excluded, "adjusted_ebitda", column.column_id) == _cell(
-                included, "adjusted_ebitda", column.column_id
-            )
-            continue
         savings = _value(included, addback, column.column_id)
         dropped += savings != 0
         assert _value(excluded, "adjusted_ebitda", column.column_id) == (
@@ -759,27 +712,18 @@
     ("ffo", "Q:Q3_2025", "ffo"),
     ("lease_cash_not_in_ebitda", "FY:FY2025", "ffo"),
     ("cfo_adjusted", "PYTD:H1_2025", "cfo"),
-    ("fcf", _BASE, "fcf"),
     ("capex", "Q:Q2_2024", "fcf"),
-    ("ncf", "DOWNSIDE:2027", "ncf"),
     ("other_investing_financing", "FY:FY2023", "ncf"),
-    ("cash_closing", "BASE:2028", "cash"),
     ("fx_and_other_cash", "Q:Q4_2025", "cash"),
     ("liquidity", _PF, "liquidity"),
-    ("undrawn_rcf", "DOWNSIDE:2026", "liquidity"),
     ("rank:Senior secured", "Q:Q1_2026", "rank:Senior secured"),
     ("fac:sun32", "Q:Q1_2026", "rank:Senior unsecured"),
     ("total_debt", _PF, "total_debt"),
-    ("total_debt", _BASE, "total_debt"),
-    ("debt:unallocated", "DOWNSIDE:2028", "total_debt"),
     ("pf:silverlake_notes", _PF, "rank:Senior secured"),
     ("pf:silverlake_cash", _PF, "liquidity"),
     ("fac:sub27", "FY:FY2025", "total_debt"),
-    ("debt_closing", "BASE:2027", "debt_rollforward"),
     ("debt_opening", "Q:Q2_2026", "debt_rollforward"),
     ("rollforward:debt_raised_net", "Q:Q2_2026", "debt_rollforward"),
-    ("cash_interest", "DOWNSIDE:2028", "interest"),
-    ("wa_rate", _BASE, "interest"),
 )
 
 
@@ -810,23 +754,9 @@
     assert reconciliation_faults(absent) == ("FY:FY2024:adjusted_ebitda",)
     total = _with_cell(model, "ebitda", "FY:FY2024", Cell(None, "NOT_STATED"))
     assert "FY:FY2024:ebitda" not in reconciliation_faults(total)
-    rate = _with_cell(
-        _nudged(_model(), "cash_interest", _BASE),
-        "wa_rate",
-        _BASE,
-        Cell(None, "COMPONENT_MISSING"),
-    )
-    assert f"{_BASE}:interest" not in reconciliation_faults(rate)
-    base = _with_cell(
-        _nudged(_model(), "cash_interest", _BASE),
-        "interest_bearing_debt_opening",
-        _BASE,
-        Cell(None, "COMPONENT_MISSING"),
-    )
-    assert f"{_BASE}:interest" not in reconciliation_faults(base)
-
-
-def test_projected_stack_foots_through_unallocated_movements() -> None:
+
+
+def test_unallocated_movements_are_not_applicable_on_history() -> None:
     model = _model()
     line = _line(model, "debt:unallocated")
     assert (line.label, line.kind, line.rank) == (
@@ -838,33 +768,8 @@
     assert ids.index("debt:unallocated") + 1 == ids.index("total_debt")
     for column in model.columns:
         cell = _cell(model, "debt:unallocated", column.column_id)
-        if column.kind != "PROJECTED":
-            assert cell.reason == "NOT_APPLICABLE"
-            continue
-        facilities = sum(
-            _value(model, line.line_id, column.column_id)
-            for line in model.lines
-            if line.line_id.startswith("fac:") and line.kind == "ACCOUNT"
-        )
-        with localcontext(CONTEXT):
-            unallocated = _value(model, "total_debt", column.column_id) - facilities
-        assert cell.value == unallocated
-        assert cell.basis == "CALCULATED"
-    # Base sweeps 822 of cash to optional repayment in FY2026.
-    assert _value(model, "debt:unallocated", _BASE) == -822
-    assert reconciliation_faults(model) == ()
-    regs = example_registers()
-    regs = replace(
-        regs,
-        facilities=tuple(
-            replace(f, carrying_value=None)
-            if f.facility_id == "sun29" and f.period_id in {"Q4_2025", "FY2025"}
-            else f
-            for f in regs.facilities
-        ),
-    )
-    missing = _model(regs=regs)
-    assert _cell(missing, "debt:unallocated", _BASE).reason == "COMPONENT_MISSING"
+        assert cell.reason == "NOT_APPLICABLE"
+    assert reconciliation_faults(model) == ()
 
 
 def test_pf_ltm_accounts_show_the_ltm_with_pf_rows_beneath() -> None:
@@ -936,12 +841,9 @@
 
 def test_cells_a_column_has_not_say_why() -> None:
     model = _model()
-    assert _cell(model, "kpi:lv_occupancy", _BASE).reason == "NOT_PROJECTED"
-    assert _cell(model, "cogs", _BASE).reason == "NOT_PROJECTED"
     assert _cell(model, "wa_rate", _LTM).reason == "NOT_APPLICABLE"
     assert _cell(model, "reference_rate", "Q:Q1_2024").reason == "NOT_APPLICABLE"
     assert _cell(model, "pf:silverlake_cash", _LTM).reason == "NOT_APPLICABLE"
-    assert _cell(model, "pf:silverlake_cash", _BASE).reason == "NOT_APPLICABLE"
     assert _value(model, "pf:silverlake_cash", _PF) == -50
     regs = example_registers()
     regs = replace(regs, kpis=tuple(k for k in regs.kpis if k.period_id != "FY2023"))
@@ -962,8 +864,9 @@
     model = _model(regs=regs)
     assert _cell(model, "rank:Senior unsecured", "FY:FY2023").reason == "NOT_SOURCED"
     assert _value(model, "rank:Senior unsecured", "FY:FY2024") == 7100
-    projected = Column(_BASE, "PROJECTED", "FY26E", "FY2026", "2026", None, 365, "BASE")
-    lines = layout(regs, (projected,), {_BASE: {}}, False, None)
+    base = "BASE:2026"
+    projected = Column(base, "PROJECTED", "FY26E", "FY2026", "2026", None, 365, "BASE")
+    lines = layout(regs, (projected,), {base: {}}, False, None)
     subtotal = next(line for line in lines if line.line_id == "rank:Senior unsecured")
     assert subtotal.cells == (Cell(None, "NOT_PROJECTED"),)
 
@@ -1151,7 +1054,7 @@
 
 def test_a_model_without_segments_notes_nothing_on_revenue() -> None:
     regs = replace(example_registers(), segments=())
-    model = _model(regs=regs, projected=False)
+    model = _model(regs=regs)
     assert not any(line.line_id.startswith("bu") for line in model.lines)
     assert all(cell.note is None for cell in _line(model, "revenue").cells)
     broken = _nudged(model, "revenue", "FY:FY2024")
@@ -1213,39 +1116,15 @@
     )
 
 
-@st.composite
-def _requests(draw: st.DrawFn) -> dict[str, Any]:
-    """CP-CF's example request with every driver redrawn."""
-    request = example_request()
-    flows = st.integers(min_value=0, max_value=9000).map(str)
-    debt = st.integers(min_value=0, max_value=900).map(str)
-    for driver in request["drivers"]:
-        for name in (
-            "revenue",
-            "ebitda",
-            "cfo",
-            "capex",
-            "cash_taxes",
-            "distributions",
-        ):
-            driver[name] = draw(flows)
-        driver["optional_repayment"] = draw(debt)
-        driver["issuance"] = draw(debt)
-    return request
-
-
 @settings(max_examples=40, deadline=None)
-@given(regs=_registers(), request=_requests(), exclude=st.booleans())
+@given(regs=_registers(), exclude=st.booleans())
 # Hypothesis's find: a year-end cash of "(0)" opened the next periods at -0.
 @example(
     regs=with_figures(example_registers(), "FY2023", {"cash_and_equivalents": Decimal("-0")}),
-    request=example_request(),
     exclude=False,
 )
-def test_any_consistent_inputs_reconcile(
-    regs: Cp1Registers, request: dict[str, Any], exclude: bool
-) -> None:
-    model = _model(regs=regs, request=request, exclude_unrealised=exclude)
+def test_any_consistent_inputs_reconcile(regs: Cp1Registers, exclude: bool) -> None:
+    model = _model(regs=regs, exclude_unrealised=exclude)
     assert reconciliation_faults(model) == ()
     assert _signed_zeros(model) == []
 
@@ -1272,15 +1151,9 @@
     assert (line.label, line.kind) == ("Add-back: Restructuring (PARTIAL)", "ACCOUNT")
 
 
-def test_projected_interest_reads_the_rate_deck() -> None:
-    model = _model()
-    assert _cell(model, "reference_rate", _BASE).value == Decimal("0.0380")
-    assert _cell(model, "reference_rate", "DOWNSIDE:2026").value == Decimal("0.0480")
-
-
 def test_registers_without_periods_give_a_model_without_columns() -> None:
     regs = replace(example_registers(), periods=())
-    model = _model(regs=regs, projected=False)
+    model = _model(regs=regs)
     assert model.columns == ()
     assert all(line.cells == () for line in model.lines)
     assert model.limitations == (NO_PROJECTIONS,)
@@ -1332,7 +1205,6 @@
 
 _BU_NOT_SUMMED = "business units do not sum to revenue"
 _EXCLUDES_FOREIGN = "excludes facility in another currency"
-_EXCLUDES_UNALLOCATED = "excludes unallocated CP-CF movements"
 _DOUBLE_COUNT = (
     "PF register states both ebitda and adjusted_ebitda adjustments; check for double counting"
 )
@@ -1341,28 +1213,6 @@
 def _on(model: CreditModel) -> dict[str, str]:
     """Each limitation's note and the columns it is on."""
     return dict(text.split(": ", 1) for text in model.limitations if ": " in text)
-
-
-def test_projected_metrics_read_cp_cf_revenue_not_a_partial_segment_sum() -> None:
-    regs = example_registers()
-    partial = replace(
-        regs,
-        segments=tuple(s for s in regs.segments if s.segment_id in {"las_vegas", "regional"}),
-    )
-    model = _model(regs=partial)
-
-    revenue = _cell(model, "revenue", _BASE)
-    assert (revenue.value, revenue.basis) == (Decimal(11809), "DRIVER")
-    assert revenue.note == _BU_NOT_SUMMED
-    with localcontext(CONTEXT):
-        assert _value(model, "metric:capex_to_revenue", _BASE) == Decimal(1700) / Decimal(11809)
-        assert _value(model, "metric:adjusted_ebitda_margin", _BASE) == Decimal(4136) / Decimal(
-            11809
-        )
-        assert _value(model, "revenue_growth", _BASE) == Decimal(11809) / Decimal(11519) - 1
-    assert _value(model, "bu:las_vegas", _BASE) == Decimal(4213) * Decimal("1.025")
-    assert _cell(_model(), "revenue", _BASE).note is None
-    assert reconciliation_faults(model) == ()
 
 
 def test_a_foreign_facility_is_noted_on_debt_interest_and_their_metrics() -> None:
@@ -1383,11 +1233,6 @@
         (_LTM, "metric:liquidity_to_debt"),
         (_PF, "total_debt"),
         (_PF, "metric:net_leverage_adjusted"),
-        (_BASE, "total_debt"),
-        (_BASE, "interest_bearing_debt_opening"),
-        (_BASE, "cash_interest"),
-        (_BASE, "metric:interest_coverage_adjusted"),
-        ("DOWNSIDE:2028", "metric:fcf_to_debt"),
     ):
         assert _EXCLUDES_FOREIGN in (_cell(model, line_id, column_id).note or ""), (
             column_id,
@@ -1398,19 +1243,6 @@
     on = _on(model)
     assert _LTM in on[_EXCLUDES_FOREIGN].split(", ")
     assert reconciliation_faults(model) == ()
-
-
-def test_projected_secured_metrics_note_unallocated_movements() -> None:
-    model = _model()
-
-    for line_id in (
-        "metric:senior_secured_leverage",
-        "metric:senior_secured_net_leverage",
-    ):
-        assert _cell(model, line_id, _BASE).note == _EXCLUDES_UNALLOCATED
-        assert _cell(model, line_id, "DOWNSIDE:2026").note is None
-        assert _cell(model, line_id, _LTM).note is None
-    assert _on(model)[_EXCLUDES_UNALLOCATED] == "BASE:2026, BASE:2027, BASE:2028"
 
 
 def test_a_pf_register_with_ebitda_and_adjusted_ebitda_rows_is_a_limitation() -> None:
@@ -1453,49 +1285,15 @@
 
 
 def test_no_cell_is_a_negative_zero() -> None:
-    request = example_request()
-    for driver in request["drivers"]:
-        driver.update({"capex": "0", "cash_taxes": "-0", "acquisitions_disposals": "0"})
     regs = with_figures(
         example_registers(),
         "FY2025",
         {"dividends_paid": Decimal(0), "capex_and_intangible_investment": Decimal(0)},
     )
-    model = _model(regs=regs, request=request)
+    model = _model(regs=regs)
 
     assert _signed_zeros(model) == []
-    assert _value(model, "dividends", "DOWNSIDE:2026") == 0
-
-
-def test_projected_interest_is_exact_and_its_bridge_still_bites() -> None:
-    model = _model()
-    assert _value(model, "cash_interest", _BASE) == Decimal("-858.984")
-    assert reconciliation_faults(model) == ()
-    cell = _cell(model, "cash_interest", _BASE)
-    off = replace(cell, value=Decimal("-858.984001"))
-    assert reconciliation_faults(_with_cell(model, "cash_interest", _BASE, off)) == (
-        f"{_BASE}:interest",
-    )
-
-
-def test_a_compound_note_is_listed_under_each_of_its_notes() -> None:
-    regs = example_registers()
-    regs = replace(
-        regs,
-        facilities=tuple(
-            replace(f, rate_type="NOT_STATED", annual_amortisation=None)
-            if f.facility_id == "tlb"
-            else f
-            for f in regs.facilities
-        ),
-    )
-    model = _model(regs=regs)
-    assert _cell(model, "fac:tlb", _BASE).note == "implied rate; amortisation not stated"
-
-    on = _on(model)
-    assert not any("; " in note for note in on)
-    assert _BASE in on["implied rate"].split(", ")
-    assert _BASE in on["amortisation not stated"].split(", ")
+    assert _value(model, "dividends", "FY:FY2025") == 0
 
 
 def test_the_pf_ltm_debt_roll_forward_foots() -> None:
@@ -1525,8 +1323,6 @@
 
     line = _line(model, "fac:disc")
     assert (line.kind, line.rank) == ("ACCOUNT", "Debt adjustments")
-    assert _value(model, "fac:disc", _BASE) == _value(model, "fac:disc", "FY:FY2025")
-    assert _value(model, "debt:unallocated", "DOWNSIDE:2026") == 0
     assert reconciliation_faults(model) == ()
 
 
@@ -1580,28 +1376,9 @@
             replace(notes, adjustment_id="ssn33_pf", metric_id="facility:ssn33"),
         ),
     )
-    model = _model(regs=regs, projected=False)
+    model = _model(regs=regs)
 
     assert _value(model, "rank:Senior secured", _PF) == 2316 + 2000 + 1000 + 600
-    assert reconciliation_faults(model) == ()
-
-
-def test_interest_at_an_implied_rate_reconciles_to_its_last_digits() -> None:
-    regs = example_registers()
-    regs = replace(
-        regs,
-        facilities=tuple(
-            replace(f, spread_bps=Decimal("2.25"))
-            if f.facility_id == "tlb"
-            else replace(f, fixed_rate=Decimal("0.065"))
-            if f.facility_id == "ssn29"
-            else f
-            for f in regs.facilities
-        ),
-    )
-    model = _model(regs=regs)
-
-    assert _cell(model, "fac:tlb", "BASE:2027").note == "term out of range"
     assert reconciliation_faults(model) == ()
 
 
@@ -1613,7 +1390,6 @@
             - 1
         )
     assert _value(model, "bu_growth:las_vegas", "FY:FY2025") == las_vegas
-    assert _value(model, "bu_growth:las_vegas", _BASE) == Decimal("0.025")
 
 
 def test_an_acquisition_reconciles_through_the_net_cash_flow() -> None:
@@ -1627,15 +1403,17 @@
     """The interest faults with a base of 1 at 5% and interest `gap` more
     negative than minus their product: the check allows a unit of the rate
     times the base (1E-39), the interest's rounding (about 5E-39) and a unit
-    of the interest (1E-39), about 7E-39."""
-    model = _model()
+    of the interest (1E-39), about 7E-39. Until the projection port, the
+    three cells are set by hand on a historical column."""
+    model = _model()
+    base = "FY:FY2025"
     for line_id, value in (
         ("interest_bearing_debt_opening", Decimal(1)),
         ("wa_rate", Decimal("0.05")),
         ("cash_interest", Decimal("-0.05") - gap),
     ):
-        cell = replace(_cell(model, line_id, _BASE), value=value)
-        model = _with_cell(model, line_id, _BASE, cell)
+        cell = replace(_cell(model, line_id, base), value=value)
+        model = _with_cell(model, line_id, base, cell)
     return tuple(f for f in reconciliation_faults(model) if f.endswith(":interest"))
 
 
@@ -1643,7 +1421,7 @@
     with localcontext(CONTEXT):
         assert _interest_at(Decimal(0)) == ()
         assert _interest_at(Decimal("6E-39")) == ()
-        assert _interest_at(Decimal("8E-39")) == (f"{_BASE}:interest",)
+        assert _interest_at(Decimal("8E-39")) == ("FY:FY2025:interest",)
 
 
 def test_a_pf_register_of_only_ebitda_and_adjusted_ebitda_rows_is_noted() -> None:
```

`$KIT/patches/test_credit_model_history.patch`:

```diff
--- a/tests/model/test_credit_model_history.py
+++ b/tests/model/test_credit_model_history.py
@@ -9,16 +9,11 @@
 from decimal import Decimal, localcontext
 
 import pytest
-from credit_model_fixture import (
-    example_deck,
-    example_growth,
-    example_registers,
-    example_slots,
-)
+from credit_model_fixture import example_registers
 from hypothesis import given, settings
 from hypothesis import strategies as st
 
-from rbotlib.model import history
+from rbotlib.model import history, periods
 from rbotlib.model._cells import (
     CONTEXT,
     SIGN_NORMALISED,
@@ -1601,14 +1596,7 @@
 
 
 def _model_inputs(regs: Cp1Registers) -> ModelInputs:
-    return ModelInputs(
-        registers=regs,
-        request=None,
-        growth=example_growth(),
-        slots=example_slots(),
-        deck=example_deck(),
-        exclude_unrealised=False,
-    )
+    return ModelInputs(registers=regs, exclude_unrealised=False)
 
 
 def _line_cell(model: CreditModel, line_id: str, column_id: str) -> Cell:
@@ -2067,7 +2055,7 @@
     undated = replace(q2, start_date=None)
 
     def first(days: int | None, end_date: str | None = "2026-06-30") -> date | None:
-        return history._first_day(replace(undated, day_count=days, end_date=end_date))
+        return periods._first_day(replace(undated, day_count=days, end_date=end_date))
 
     assert first(91) == date(2026, 4, 1)
     assert first(1) == end
@@ -2076,7 +2064,7 @@
     assert first(0) is None
     assert first(None) is None
     assert first(91, None) is None
-    assert history._first_day(q2) == date(2026, 4, 1)
+    assert periods._first_day(q2) == date(2026, 4, 1)
 
 
 def test_a_ytd_built_from_quarters_with_a_gap_does_not_meet_the_year() -> None:
@@ -2350,7 +2338,7 @@
 
 
 def test_whole_months_reads_a_span_from_a_first_day_to_a_last_day() -> None:
-    whole = history._whole_months
+    whole = periods._whole_months
     jan, feb = date(2024, 1, 1).toordinal(), date(2024, 2, 29).toordinal()
     assert whole((jan, feb)) == (2024 * 12 + 1, 2)
     assert whole((jan, date(2024, 12, 31).toordinal())) == (2024 * 12 + 1, 12)
@@ -2496,8 +2484,8 @@
     FY, YTD and PYTD: only all stated, or the FY beside two interims without
     a row, is summed; a part missing otherwise is left to the sum."""
     regs = _halves()
-    spec = next(s for s in history._plan(regs) if s.column.kind == "LTM")
-    year = next(s for s in history._plan(regs) if s.column.kind == "FY")
+    spec = next(s for s in periods._plan(regs) if s.column.kind == "LTM")
+    year = next(s for s in periods._plan(regs) if s.column.kind == "FY")
     cells = {
         "S": Cell(Decimal(1)),
         "A": Cell(None, "NOT_SOURCED"),
```

`$KIT/patches/test_credit_model_metrics.patch`:

```diff
--- a/tests/model/test_credit_model_metrics.py
+++ b/tests/model/test_credit_model_metrics.py
@@ -7,23 +7,16 @@
 from decimal import Decimal, localcontext
 
 import pytest
-from credit_model_fixture import (
-    example_deck,
-    example_growth,
-    example_registers,
-    example_request,
-    example_slots,
-)
+from credit_model_fixture import example_registers
 
 from rbotlib.model._cells import CONTEXT, refs
-from rbotlib.model.frame import Cell, Column, Frame, SourceRef
+from rbotlib.model.frame import Case, Cell, Column, Frame, SourceRef
 from rbotlib.model.history import (
     account_frame,
     historical_columns,
     ltm_frames,
 )
 from rbotlib.model.metrics import metric_frame, unit_of
-from rbotlib.model.projection import ProjectionInputs, projection
 from rbotlib.model.registers import Cp1Registers
 from rbotlib.model.statements import (
     pro_forma_column,
@@ -60,11 +53,43 @@
 )
 
 
+# Projected columns stand in for caos `projection` (Plan 13 ports it): each
+# carries only the keys a projection writes, from FY2025 with revenue,
+# adjusted EBITDA and the business units grown by its factor.
+_PROJECTED: tuple[tuple[Case, int, str], ...] = (
+    ("BASE", 2026, "1.02"),
+    ("BASE", 2027, "1.05"),
+    ("DOWNSIDE", 2026, "0.95"),
+    ("DOWNSIDE", 2027, "0.97"),
+)
+_PROJECTED_KEYS = ("total_debt", "secured_debt", "cash_closing", "capex", "cash_interest")
+_GROWN_KEYS = ("revenue", "adjusted_ebitda")
+
+
+def _projections(frame: Frame) -> tuple[tuple[Column, ...], Frame]:
+    fy = frame["FY:FY2025"]
+    columns: list[Column] = []
+    projected: Frame = {}
+    for case, year, factor in _PROJECTED:
+        column_id = f"{case}:{year}"
+        columns.append(
+            Column(column_id, "PROJECTED", f"FY{year % 100}E", None, str(year), None, 365, case)
+        )
+        cells = {key: fy[key] for key in _PROJECTED_KEYS}
+        for key in (*_GROWN_KEYS, *(k for k in fy if k.startswith("bu:"))):
+            value = fy[key].value
+            assert value is not None, key
+            cells[key] = Cell(value * Decimal(factor), basis="PROJECTED")
+        projected[column_id] = cells
+    return tuple(columns), projected
+
+
 def _model(
     regs: Cp1Registers | None = None,
 ) -> tuple[tuple[Column, ...], Frame, Frame]:
-    """Every column of the example: history, the PF-LTM and the projections;
-    their frame; and the statements of the LTM ending each quarter."""
+    """Every column of the example: history, the PF-LTM and stand-in
+    projections; their frame; and the statements of the LTM ending each
+    quarter."""
     regs = regs or example_registers()
     columns = historical_columns(regs)
     frame = statement_frame(account_frame(regs, columns), columns, regs)
@@ -74,16 +99,7 @@
     pro_forma = pro_forma_column(regs, ltm, frame)
     assert pro_forma is not None
     pf_column, pf_frame = pro_forma
-    projected, projected_frame = projection(
-        ProjectionInputs(
-            regs=regs,
-            request=example_request(),
-            growth=example_growth(),
-            slots=example_slots(),
-            deck=example_deck(),
-            history=frame,
-        )
-    )
+    projected, projected_frame = _projections(frame)
     every = (*columns, pf_column, *projected)
     return every, {**frame, **pf_frame, **projected_frame}, ltm_ending
 
@@ -358,10 +374,10 @@
         "FY:FY2025", "FY:FY2024", "bu:regional"
     )
     # A projection against the last FY, then its own case's prior year.
-    assert result["BASE:2026"]["bu_growth:las_vegas"].value == Decimal("0.025")
-    assert result["DOWNSIDE:2026"]["bu_growth:las_vegas"].value == Decimal("-0.06")
-    assert result["BASE:2027"]["bu_growth:regional"].value == Decimal("0.015")
-    assert result["BASE:2026"]["bu_growth:managed_other"].value == 0
+    assert result["BASE:2026"]["bu_growth:las_vegas"].value == Decimal("0.02")
+    assert result["DOWNSIDE:2026"]["bu_growth:las_vegas"].value == Decimal("-0.05")
+    regional = result["BASE:2027"]["bu_growth:regional"].value
+    assert regional == _rise(Decimal("1.05"), Decimal("1.02"))
     assert result["BASE:2027"]["revenue_growth"].value == growth(
         "BASE:2027", "BASE:2026", "revenue"
     )
```

`$KIT/MANIFEST.sha256`:

```text
21b430c69ba600a8b1a99c28cc27dbc0daf7026e5e6c09bd8d41ad9b63bf1a83  rbot/scripts/rbotlib/model/_cells.py
9090d766894033a4d65ac82fe7aaa23d28541a261d6088fa73e23b0597a419eb  rbot/scripts/rbotlib/model/assemble.py
97098e1bf35c17018af79cd26f5e2693b179627bea9216bbf51d98f38c6ab1f1  rbot/scripts/rbotlib/model/debt.py
964b5042068a16b3d47356a956523439657a31b93a3ccc684ea908531dce3f49  rbot/scripts/rbotlib/model/frame.py
ff6a5a5b0848bf2dbc682ecb741e9319b7220881604bc8f216886939d37b3033  rbot/scripts/rbotlib/model/history.py
66d356a74ab6a5525801c386f4b2e8b1eda2b447a004fb75cdde0143d8c69153  rbot/scripts/rbotlib/model/layout.py
c14504805cb28a7acdc32a04c6d40f9936312749e5f83031a55b532806baaeb5  rbot/scripts/rbotlib/model/metrics.py
eb01cc53ec993c40894467c2c32bc573a8da4cbae12abbf077385583d2fcad0a  rbot/scripts/rbotlib/model/periods.py
30b42ef334ac2987507a99bd1b0b2e0a91a3647038b733d079be8771a6f27d9e  rbot/scripts/rbotlib/model/statements.py
5f58183c82ea5a84a5a1327e80498f1279b0ce549fc42ad9acef19e4c606ed6f  tests/model/assemble_cases.py
c7a23701281e5d5e28b0d661f9ca1c0f3ac317784b7e519d563b8d8b9e94c640  tests/model/credit_model_fixture.py
6a354dc611d585d2f18988c26249d8c0651d6df0bc7a64517c2152d4c479f2b6  tests/model/debt_cases.py
a2466e7548ee50aaeab64da4f2b41a4f2a4562d085a359f03f7ea3c78073f588  tests/model/history_cases.py
600a30e1dd7aec313c87e8a1368195483df77430777f89cfaddcfe2c0ca38d4e  tests/model/history_frames.py
98a7c5df2ec32f727c6946de6c6d878a3c974269de945054c21a487f2c642b46  tests/model/metrics_cases.py
5e76f72a6a0b4530f7c757bdabc6d2358e9a9d02ef3b7e8327cecd56c6a2ccb5  tests/model/statements_cases.py
707df7af36a3e2190f65388d1bb8033a31c095dd19932c9bb43859f7f9e2d445  tests/model/test_credit_model_assemble.py
65627ab005c653bb2c2d60f5426e1754498fbdb8a12bd1097d6a82337a01004d  tests/model/test_credit_model_assemble_cases.py
d78fdb2a78ea493e43b80c87d45575c589dd5e541aa8b83bf37c0dc13bb63523  tests/model/test_credit_model_assemble_lines.py
3442ef35044a922874725394e5b7261a9b8419a0d7516222835d699bc6f2a85e  tests/model/test_credit_model_cells.py
442099e523f054a6d218457d5b138e15f8bc5c9d45a06f8e6a9baf712a02a77e  tests/model/test_credit_model_debt.py
577b10c9b3e255035ba622600124ff22f4588e6ef66e95601d4be9a8b5588d0a  tests/model/test_credit_model_debt_flows.py
db9064b5ce183772ba7707fe6a3c201d1ab7c2ce5a1afee46da442696a576d2c  tests/model/test_credit_model_history.py
8c208b928cdeee25a063ebc40a574f5a0021c5ed4b80cc4d76dccbc23e2226a4  tests/model/test_credit_model_history_dates.py
2cdbe08f7643aa31205291294051d4607b4ff7c67ff3598d685fceaf1dcd7a2f  tests/model/test_credit_model_history_flows.py
968a07f26824e2c10e7b69150aa0a6af9ee9873a33652d9cbb99fb4f4119b39a  tests/model/test_credit_model_history_interims.py
b51b7e6433d4c0f8060aa81f3338f48eb1d15923ea5b0954b5cfeb5d634f71e5  tests/model/test_credit_model_history_model.py
f4407989229647261ef9f82efce10f8b0e43aac7c397f73adeaacc8ae0ced3fa  tests/model/test_credit_model_history_registers.py
7a37f1b3f543fc93c319e506c4742d9df702d82d2673a4eb3ed66c62e3b9c799  tests/model/test_credit_model_history_sparse.py
b16f2b1833fde2dddcfed5726c260aab5a53a69181b6b1abb5ab50efe5480314  tests/model/test_credit_model_layout.py
7b71a456b061da809670ed143dafe58f747a08b8848c7b555aaa50026e0fc930  tests/model/test_credit_model_metrics.py
3a5137f08dbc63f99a63ede64b4c70b9999d01f9d1cb2614f44f1609a73b8e45  tests/model/test_credit_model_metrics_growth.py
bf65254b6d5745cb645b328a046e4fccbbb881942ac81294259eda4b263d7453  tests/model/test_credit_model_periods.py
f0376550f3f3790d7feb2b913a80ca9d408d6d357e087e626ab186aa1dd1da4b  tests/model/test_credit_model_statements.py
f9afd5c2fa163751bf5a997943b1e6bba4cd525d75393df839e8f0769d3f8414  tests/model/test_credit_model_statements_cases.py
9da776373d48d0299ede3280d70ad4de30e552c42f1523f83ffe4d0bcbedb0f7  tests/model/test_credit_model_statements_pro_forma.py
```

- [ ] **Step 4: Build and check the ported files**

```bash
export KIT="$PWD/.port-03"
bash "$KIT/stage.sh" "$PWD" /Users/ericguei/Documents/caos-databricks | tail -3
grep -c ': OK$' <(cd "$KIT/out" && shasum -a 256 -c "$KIT/MANIFEST.sha256")
```

Expected: the last three manifest lines end `: OK`; the count is `36`. A `FAILED` line means the kit or the toolchain differs from the verified one (most likely a `ruff` version other than 0.17.0): stop, report BLOCKED with the failing paths.

Report: `Not verified:` list nothing new; the kit is a build step (git-ignored, never committed), so its reproducibility rests on caos commit `5c3cd52f` staying reachable and on `ruff` 0.17.0 staying locked.


---

### Task 2: Cell types, the figure reader and the CP-1 register types (PR 03A1)

**Files:**
- Create: `rbot/scripts/rbotlib/model/__init__.py`, `rbot/scripts/rbotlib/model/frame.py`, `rbot/scripts/rbotlib/model/reader.py`, `rbot/scripts/rbotlib/model/registers.py`
- Modify: `.gitignore`
- Test: `tests/model/test_reader.py`

**Interfaces:**
- Consumes: Plan 01's `rbotlib.handoff.Table`.
- Produces: `rbotlib.model.frame` (ported): `SourceRef(source_id, source_locator, cell_text)`, `Cell(value, reason, basis, stated, sources, note)`, `Column(column_id, kind, label, period_id, fiscal_year, end_date, days, case)`, `Frame`. `rbotlib.model.reader`: `ModelInputError(ValueError)`; `Row(table_id, number, cells)` with `Row.refuse(column, why)`; `figure(cell) -> Decimal | None` (caos `_exact`: `(x)` negative, currency symbols, trailing `%`/`x` stripped, the last separator is the decimal one, `5,2` ambiguous → refused; null text → None; non-finite, ≥ 1e18 or > 10 decimals refused; markers `[C<n>]` stripped); `rows`, `read`, `distinct`, `text`, `optional`, `required_text`, `cite`, `enum(row, column, vocabulary, *, closed=True)`, `decimal`, `required_decimal`, `integer`, `ids`, `source`, `fiscal_year_number`, `iso_date`, `date_cell`. `rbotlib.model.registers`: `PeriodRow`, `AccountRow`, `AddbackRow`, `SegmentRow`, `KpiRow`, `FacilityRow`, `PfAdjustmentRow`, `Cp1Registers`, the closed vocabularies (`PERIOD_TYPES` … `REFERENCE_RATES`, `FACILITY_TYPES`), and `iso_date`, `fiscal_year_number` re-exported for the ported modules.

**Agent:** `mx-invariants` (figure parsing is money input).

- [ ] **Step 1: Write the failing test**

`tests/model/test_reader.py`:

```python
"""Cell reading with caos's host rules; every refusal names where."""

from __future__ import annotations

import re
from contextlib import AbstractContextManager
from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import (
    ModelInputError,
    Row,
    cite,
    date_cell,
    decimal,
    distinct,
    enum,
    figure,
    fiscal_year_number,
    ids,
    integer,
    iso_date,
    optional,
    read,
    required_decimal,
    required_text,
    rows,
    source,
    unmarked,
)


def _row(**cells: str) -> Row:
    return Row("cp1.example", 3, cells)


def _refused(match: str) -> AbstractContextManager[pytest.ExceptionInfo[ModelInputError]]:
    return pytest.raises(ModelInputError, match=re.escape(match))


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("1,250.0", "1250.0"),
        ("(45) [C1]", "-45"),
        ("$1,234", "1234"),
        ("12.5%", "12.5"),
        ("4.2x", "4.2"),
        ("1.234,5", "1234.5"),
        ("-0.25", "-0.25"),
        ("1\N{NO-BREAK SPACE}234", "1234"),
        ("\N{EURO SIGN}12", "12"),
        ("1e3", "1000"),
    ],
)
def test_figure_reads_caos_exact_rules(text: str, value: str) -> None:
    assert figure(text) == Decimal(value)


@pytest.mark.parametrize("text", ["5,2", "abc", "4[C1]5", "1.2.3", "12,34.5", "1,2.345,6", ""])
def test_figure_refuses_what_it_will_not_guess(text: str) -> None:
    assert figure(text) is None


@given(st.decimals(min_value=Decimal("-1e15"), max_value=Decimal("1e15"), places=6))
def test_a_written_figure_reads_back_exactly(value: Decimal) -> None:
    assert figure(f"{value:,f}") == value
    if value:
        assert figure(f"({abs(value):,f})") == -abs(value)


def test_unmarked_keeps_a_split_figure_split() -> None:
    assert unmarked("(45) [C1]") == "(45)"
    assert unmarked("4[C1]5") == "4 | 5"
    assert unmarked("[C2] text") == " text"


def test_decimal_reads_null_as_none_and_refuses_the_rest_naming_where() -> None:
    assert decimal(_row(value="—"), "value") is None
    assert decimal(_row(), "value") is None
    zero = decimal(_row(value="(0)"), "value")
    assert zero is not None and zero == 0 and not zero.is_signed()
    with _refused("cp1.example row 3 column value: 'about 2bn' is not a figure"):
        decimal(_row(value="about 2bn"), "value")
    with _refused("cp1.example row 3 column value: figure out of range"):
        decimal(_row(value="1e18"), "value")
    with _refused("column value: figure out of range"):
        decimal(_row(value="1e999999x"), "value")
    with _refused("column value: more than 10 decimals"):
        decimal(_row(value="0.12345678901"), "value")
    with _refused("column value: required, found null"):
        required_decimal(_row(value="n/a"), "value")
    with _refused("column value: not a whole number"):
        integer(_row(value="1.5"), "value")
    assert integer(_row(value="2"), "value") == 2
    assert integer(_row(value="—"), "value") is None


def test_enum_reads_canonical_spellings_closed_or_open() -> None:
    vocabulary = frozenset({"SUPER_SENIOR", "SENIOR"})
    assert enum(_row(s="super senior"), "s", vocabulary) == "SUPER_SENIOR"
    assert enum(_row(s="Super-Senior"), "s", vocabulary) == "SUPER_SENIOR"
    with _refused("column s: 'Senior secured' is not one of ['SENIOR', 'SUPER_SENIOR']"):
        enum(_row(s="Senior secured"), "s", vocabulary)
    with _refused("column s: required, found null"):
        enum(_row(s="—"), "s", vocabulary)
    with _refused("column s: required, found null"):
        enum(_row(), "s", vocabulary)
    open_vocabulary = frozenset({"DEBT ADJUSTMENT"})
    assert enum(_row(t="debt_adjustment"), "t", open_vocabulary, closed=False) == "DEBT ADJUSTMENT"
    assert enum(_row(t="Term loan"), "t", open_vocabulary, closed=False) == "TERM LOAN"


def test_text_columns() -> None:
    assert optional(_row(a="n/a"), "a") is None
    assert optional(_row(), "a") is None
    assert optional(_row(a=" x [C1]"), "a") == "x"
    with _refused("column a: required, found null"):
        required_text(_row(a="—"), "a")
    assert ids(_row(a="Q1; Q2,Q3"), "a") == ("Q1", "Q2", "Q3")
    assert ids(_row(a="—"), "a") == ()


def test_cite_keeps_markers_and_refuses_null() -> None:
    assert cite(_row(cite=" [C3] [C4] "), "cite") == "[C3] [C4]"
    assert cite(_row(cite="calc: a / b"), "cite") == "calc: a / b"
    with _refused("cp1.example row 3 column cite: required, found null"):
        cite(_row(cite="—"), "cite")
    with _refused("column cite: required, found null"):
        cite(_row(), "cite")


def test_source_keeps_markers_and_cell_text_verbatim() -> None:
    row = _row(source_id="[C12] [C13]", source_locator="p.61", value="1,234 [C12]")
    assert source(row, "value") == SourceRef("[C12] [C13]", "p.61", "1,234 [C12]")
    assert source(_row(source_id="—", value="1"), "value") is None
    assert source(_row(value="1"), "value") is None
    assert source(_row(source_id="[C1]", value="1"), "value") == SourceRef("[C1]", "", "1")


def test_dates() -> None:
    assert date_cell(_row(d="2025-12-31"), "d") == date(2025, 12, 31)
    assert date_cell(_row(d="—"), "d") is None
    for bad in ("2025-02-30", "31/12/2025", "1899-12-31"):
        with _refused(f"column d: {bad!r} is not a YYYY-MM-DD date in 1900-2200"):
            date_cell(_row(d=bad), "d")
    assert iso_date("2025-13-01") is None
    assert iso_date(None) is None


def test_fiscal_years() -> None:
    assert fiscal_year_number("FY2025/26") == 2026
    assert fiscal_year_number("2025-2026") == 2026
    assert fiscal_year_number("FY2025") == 2025
    assert fiscal_year_number("2025/27") == 2025
    assert fiscal_year_number("FY") is None


def test_rows_read_absent_tables_as_none_and_refuse_bad_shapes() -> None:
    tables = {"t": Table(["a", "b"], [["1", "2"]])}
    assert rows(tables, "absent", frozenset({"a"})) == []
    assert read(tables, "t", frozenset({"a"}), lambda r: r.cells["b"]) == ("2",)
    with _refused("t: missing column c"):
        rows(tables, "t", frozenset({"a", "c"}))
    with _refused("t row 1: 1 cells, header has 2"):
        rows({"t": Table(["a", "b"], [["1"]])}, "t", frozenset())


def test_distinct_refuses_a_key_written_twice() -> None:
    assert distinct("t", ("a", "b"), lambda x: (x,)) == ("a", "b")
    with _refused("t row 2: a / P written twice"):
        distinct("t", ("a", "a"), lambda x: (x, "P"))
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_reader.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/frame.py" rbot/scripts/rbotlib/model/frame.py
```

- [ ] **Step 4: Write the package**

`rbot/scripts/rbotlib/model/__init__.py`:

```python
"""The credit Model: pure Decimal arithmetic, no I/O, except `run`, which reads
the run folder and writes model.json, model.xlsx and handoffs/MODEL.md."""

from __future__ import annotations
```

`rbot/scripts/rbotlib/model/reader.py`:

```python
"""Read a Handoff table's cells the way caos's host reads them.

The cell reading of caos `caos/methodology/model_inputs.py` and
`caos/methodology/tables.py` at `5c3cd52f`, over `rbotlib.handoff.Table`s,
refusing with `ModelInputError`, whose message names the table, the row
(1-based, as written) and the column.

A figure cell is read by `figure`, caos's `_exact` rules: citation markers
removed, `(x)` negative, a leading or trailing currency symbol and a trailing
`%` or `x` stripped, digit-group spaces removed, the separator that comes last
is the decimal one, and `5,2` is refused rather than guessed. A cell holding
null text (`NULL_TEXT`, which includes the gap marker `—`) has no figure; any
other text that is not a figure is refused, never read as null. A figure that
is not finite, `MAX_FIGURE` or more in size, or written to more than
`MAX_DECIMALS` decimals is refused (never rounded); `-0` reads as `0`.

An enumerated column's text names a member of its vocabulary on case and
separators (`_`, `-` and whitespace alike) and reads as that member's
canonical spelling; text naming no member is refused, or read in upper case
where the column is open. A date is `YYYY-MM-DD` from 1900 to 2200.

Pure: no I/O.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TypeVar

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef

NULL_TEXT = frozenset(
    {"", "null", "n/a", "not available", "not calculable", "-", "\N{EM DASH}", "\N{EN DASH}"}
)
MAX_FIGURE = Decimal(10) ** 18
MAX_DECIMALS = 10
FIGURE_CHARS = 64
FIRST_YEAR, LAST_YEAR = 1900, 2200
_SEPARATORS = re.compile(r"[\s_-]+")
_LIST_SEPARATOR = re.compile(r"[;,]")
_FOUR_DIGITS = re.compile(r"(?<!\d)\d{4}(?!\d)")
_TWO_YEARS = re.compile(r"(?<!\d)(\d{4})\s*[/-]\s*(\d{4}|\d{2})(?!\d)")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
# caos `citation_markers.unmarked`, for Plan 01's single `[C<n>]` markers.
_IN_CELL = re.compile(r"(?<! )(?: *\[C[0-9]+\])+")
_FIGURE_EDGE = frozenset("0123456789.,")
_SPACES = str.maketrans("", "", "\N{NO-BREAK SPACE}\N{THIN SPACE}\N{NARROW NO-BREAK SPACE} ")
_SYMBOLS = "\N{EURO SIGN}$\N{POUND SIGN}\N{YEN SIGN}\N{INDIAN RUPEE SIGN}"
_CURRENCY = re.compile(f"^[{_SYMBOLS}]|[{_SYMBOLS}]$")
_MULTIPLE = re.compile(r"[xX]$")
_PERCENT = re.compile(r"%$")
_FIGURE = re.compile(r"[-+]?[0-9][0-9.,]*(?:[eE][-+]?[0-9]+)?")
_ANGLO_THOUSANDS = re.compile(r"^\d{1,3}(,\d{3})+(\.\d+)?$")
_CONTINENTAL = re.compile(r"^\d{1,3}(\.\d{3})+(,\d+)?$")
_AMBIGUOUS_COMMA = re.compile(r"^\d+,\d{1,2}$")

T = TypeVar("T")


class ModelInputError(ValueError):
    """A Model-input table is malformed; the message names table, row and column."""


@dataclass(frozen=True, slots=True)
class Row:
    """One table row keyed by column, with where it was written."""

    table_id: str
    number: int
    cells: Mapping[str, str]

    def refuse(self, column: str, why: str) -> ModelInputError:
        return ModelInputError(f"{self.table_id} row {self.number} column {column}: {why}")


def unmarked(cell: str) -> str:
    """`cell` without its `[C<n>]` markers (and the spaces before them); a
    marker splitting a figure (`4[C1]5`) becomes ` | `, so no figure reads."""

    def replaced(found: re.Match[str]) -> str:
        before = cell[found.start() - 1 : found.start()]
        after = cell[found.end() : found.end() + 1]
        split = before in _FIGURE_EDGE and after in _FIGURE_EDGE
        return " | " if split and not found.group().startswith(" ") else ""

    return _IN_CELL.sub(replaced, cell)


def _separated(core: str) -> str | None:
    body = core.lstrip("-+")
    if "," in core and "." in core:
        if core.rfind(",") > core.rfind("."):
            if not _CONTINENTAL.match(body):
                return None
            return core.replace(".", "").replace(",", ".")
        if not _ANGLO_THOUSANDS.fullmatch(body):
            return None
        return core.replace(",", "")
    if "," in core:
        if _AMBIGUOUS_COMMA.match(body) or not _ANGLO_THOUSANDS.match(body):
            return None
        return core.replace(",", "")
    return core


def figure(cell: str) -> Decimal | None:
    """The cell's exact figure (caos `_exact`), or None when it is not one."""
    text = unmarked(cell).strip()
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1].strip()
    core = _CURRENCY.sub("", text.translate(_SPACES))
    core = _PERCENT.sub("", _MULTIPLE.sub("", core))
    plain = _separated(core) if _FIGURE.fullmatch(core) and len(core) <= FIGURE_CHARS else None
    if plain is None:
        return None
    try:
        value = Decimal(plain)
    except InvalidOperation:
        return None
    return value.copy_negate() if negative else value


def is_null(cell: str) -> bool:
    return unmarked(cell).strip().casefold() in NULL_TEXT


def rows(tables: Mapping[str, Table], table_id: str, required: frozenset[str]) -> list[Row]:
    """The table's rows keyed by column; none for an absent table. Refused for
    a present table missing a `required` column or with a ragged row."""
    table = tables.get(table_id)
    if table is None:
        return []
    missing = sorted(required - set(table.columns))
    if missing:
        raise ModelInputError(f"{table_id}: missing column {', '.join(missing)}")
    found = []
    for number, cells in enumerate(table.rows, 1):
        if len(cells) != len(table.columns):
            width = f"{len(cells)} cells, header has {len(table.columns)}"
            raise ModelInputError(f"{table_id} row {number}: {width}")
        found.append(Row(table_id, number, dict(zip(table.columns, cells, strict=True))))
    return found


def read(
    tables: Mapping[str, Table],
    table_id: str,
    required: frozenset[str],
    reader: Callable[[Row], T],
) -> tuple[T, ...]:
    return tuple(reader(row) for row in rows(tables, table_id, required))


def distinct(
    table_id: str, found: tuple[T, ...], key: Callable[[T], tuple[str, ...]]
) -> tuple[T, ...]:
    """`found`, refused when two rows share a key: one id in one period is one
    figure, never two for the Model to choose between."""
    seen: set[tuple[str, ...]] = set()
    for number, row in enumerate(found, 1):
        k = key(row)
        if k in seen:
            raise ModelInputError(f"{table_id} row {number}: {' / '.join(k)} written twice")
        seen.add(k)
    return found


def text(row: Row, column: str) -> str:
    return unmarked(row.cells[column]).strip()


def optional(row: Row, column: str) -> str | None:
    """The column's text, or None for null text or an absent column."""
    if column not in row.cells:
        return None
    value = text(row, column)
    return None if value.casefold() in NULL_TEXT else value


def required_text(row: Row, column: str) -> str:
    value = optional(row, column)
    if value is None:
        raise row.refuse(column, "required, found null")
    return value


def cite(row: Row, column: str) -> str:
    """A required `cite` column as written, markers kept (`[C3] [C4]`, or
    `calc: <formula>`)."""
    value = row.cells.get(column, "").strip()
    if value.casefold() in NULL_TEXT:
        raise row.refuse(column, "required, found null")
    return value


def _key(value: str) -> str:
    return _SEPARATORS.sub(" ", value.casefold()).strip()


def enum(row: Row, column: str, vocabulary: frozenset[str], *, closed: bool = True) -> str:
    """A required enumerated column in its canonical spelling; text naming no
    member reads in upper case where the column is open (`closed=False`).
    Refused when null or, for a closed vocabulary, naming no member."""
    value = text(row, column) if column in row.cells else ""
    key = _key(value)
    member = next((m for m in vocabulary if _key(m) == key), None)
    if member is not None:
        return member
    if value.casefold() in NULL_TEXT:
        raise row.refuse(column, "required, found null")
    if closed:
        raise row.refuse(column, f"{value!r} is not one of {sorted(vocabulary)}")
    return value.upper()


def decimal(row: Row, column: str) -> Decimal | None:
    """The column's figure; None for null text or an absent column."""
    if column not in row.cells or is_null(row.cells[column]):
        return None
    value = figure(row.cells[column])
    if value is None:
        raise row.refuse(column, f"{row.cells[column]!r} is not a figure")
    if not value.is_finite() or abs(value) >= MAX_FIGURE:
        raise row.refuse(column, "figure out of range")
    if -int(value.as_tuple().exponent) > MAX_DECIMALS:
        raise row.refuse(column, f"more than {MAX_DECIMALS} decimals")
    return value.copy_abs() if value.is_zero() else value


def required_decimal(row: Row, column: str) -> Decimal:
    value = decimal(row, column)
    if value is None:
        raise row.refuse(column, "required, found null")
    return value


def integer(row: Row, column: str) -> int | None:
    value = decimal(row, column)
    if value is None:
        return None
    if value != value.to_integral_value():
        raise row.refuse(column, "not a whole number")
    return int(value)


def ids(row: Row, column: str) -> tuple[str, ...]:
    """A `;`- or `,`-separated list of ids; none for null text."""
    value = optional(row, column)
    if value is None:
        return ()
    return tuple(part.strip() for part in _LIST_SEPARATOR.split(value) if part.strip())


def source(row: Row, figure_column: str) -> SourceRef | None:
    """Where the row's figure came from, its cell text verbatim; None when the
    row names no source. `source_id` holds citation markers (`[C12]`), so it
    is read as written, never unmarked."""
    source_id = row.cells.get("source_id", "").strip()
    if source_id.casefold() in NULL_TEXT:
        return None
    return SourceRef(
        source_id=source_id,
        source_locator=optional(row, "source_locator") or "",
        cell_text=row.cells[figure_column],
    )


def _end_year(start: str, end: str) -> int | None:
    first = int(start)
    if len(end) == 4:
        return int(end) if int(end) == first + 1 else None
    return first + 1 if int(end) == (first + 1) % 100 else None


def fiscal_year_number(value: str) -> int | None:
    """A fiscal year's four-digit year: a two-year spelling's END year
    (`FY2025/26` is 2026), else the last run of exactly four digits."""
    for start, end in reversed(_TWO_YEARS.findall(value)):
        year = _end_year(start, end)
        if year is not None:
            return year
    runs = _FOUR_DIGITS.findall(value)
    return int(runs[-1]) if runs else None


def iso_date(value: str | None) -> date | None:
    """`value` as a calendar date where it is exactly `YYYY-MM-DD`; else None."""
    if value is None or _ISO_DATE.fullmatch(value) is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:  # `2025-02-30`: no such day
        return None


def date_cell(row: Row, column: str) -> date | None:
    """The column's date; None for null text; refused when it is not a
    `YYYY-MM-DD` calendar date from 1900 to 2200."""
    value = optional(row, column)
    if value is None:
        return None
    day = iso_date(value)
    if day is None or not FIRST_YEAR <= day.year <= LAST_YEAR:
        raise row.refuse(column, f"{value!r} is not a YYYY-MM-DD date in 1900-2200")
    return day
```

`rbot/scripts/rbotlib/model/registers.py`:

```python
"""CP-1's registers as the credit model reads them: typed rows and the
vocabularies of their enumerated columns.

Port of the row types of caos `caos/methodology/model_inputs.py` at
`5c3cd52f`; `rbotlib.model.inputs` reads CP-1's tables into them. The ported
Model imports every register type, `iso_date` and `fiscal_year_number` from
here. `docs/model/enums.md` lists the vocabularies; every one is closed
except `FACILITY_TYPES`, which names the one facility type the Model acts on.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import fiscal_year_number as fiscal_year_number
from rbotlib.model.reader import iso_date as iso_date

PERIOD_TYPES = frozenset({"QUARTER", "YTD", "FY", "LTM", "PERIOD_END"})
PERIOD_UNITS = frozenset({"UNITS", "THOUSANDS", "MILLIONS"})
CALCULATION_STATUSES = frozenset(
    {
        "VERIFIED",
        "CALCULATED",
        "ESTIMATED",
        "PROXY",
        "NOT CALCULABLE",
        "PARTIAL",
        "CONFLICTED",
        "NOT AVAILABLE",
    }
)
ADDBACK_CLASSIFICATIONS = frozenset(
    {
        "RESTRUCTURING",
        "SBC",
        "COST_SAVINGS",
        "RUN_RATE",
        "SYNERGY",
        "TRANSACTION_COSTS",
        "OTHER_EXPLICIT",
    }
)
REALIZATION_STATUSES = frozenset({"REALIZED", "UNREALIZED", "NOT_STATED"})
SEGMENT_TYPES = frozenset({"OPERATING_SEGMENT", "CORPORATE_ELIMINATION"})
KPI_VALUE_TYPES = frozenset({"PERIOD_END", "PERIOD_FLOW", "RATE"})
SECURED_STATUSES = frozenset({"SECURED", "UNSECURED", "NOT_STATED"})
SENIORITIES = frozenset(
    {"SUPER_SENIOR", "SENIOR", "SENIOR_SUBORDINATED", "SUBORDINATED", "JUNIOR", "NOT_STATED"}
)
LEASE_CLASSIFICATIONS = frozenset({"FINANCE_LEASE", "OPERATING_LEASE", "NOT_LEASE", "NOT_STATED"})
PF_CLASSIFICATIONS = frozenset(
    {
        "ACQUISITION",
        "DISPOSAL",
        "REFINANCING",
        "SUBSEQUENT_EVENT",
        "LENDER_UPDATE",
        "OTHER_EXPLICIT",
    }
)
RATE_TYPES = frozenset({"FIXED", "FLOATING", "NOT_STATED"})
REFERENCE_RATES = frozenset({"SOFR", "TERM_SOFR", "EURIBOR", "SONIA", "NONE", "NOT_STATED"})
FACILITY_TYPES = frozenset({"DEBT ADJUSTMENT"})  # open: other text reads in upper case


@dataclass(frozen=True, slots=True)
class PeriodRow:
    period_id: str
    fiscal_year: str
    fiscal_quarter: str | None
    period_type: str  # QUARTER|YTD|FY|LTM|PERIOD_END
    start_date: str | None
    end_date: str | None
    day_count: int | None
    currency: str
    unit: str
    component_period_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AccountRow:
    metric_id: str
    period_id: str
    value: Decimal | None
    calculation_status: str
    source: SourceRef | None


@dataclass(frozen=True, slots=True)
class AddbackRow:
    addback_id: str
    label: str
    classification: str
    realization_status: str
    display_priority: int
    period_id: str
    value: Decimal | None
    source: SourceRef | None


@dataclass(frozen=True, slots=True)
class SegmentRow:
    segment_id: str
    segment_name: str
    segment_type: str
    display_priority: int
    period_id: str
    revenue: Decimal | None
    source: SourceRef | None


@dataclass(frozen=True, slots=True)
class KpiRow:
    kpi_id: str
    kpi_label: str
    display_priority: int
    period_id: str
    value: Decimal | None
    unit: str
    value_type: str  # PERIOD_END|PERIOD_FLOW|RATE
    source: SourceRef | None


@dataclass(frozen=True, slots=True)
class FacilityRow:
    facility_id: str
    facility_name: str
    period_id: str
    facility_type: str
    currency: str
    carrying_value: Decimal | None
    commitment: Decimal | None
    drawn_amount: Decimal | None
    secured_status: str
    seniority: str
    lease_classification: str
    maturity_date: str | None
    margin_or_coupon: str
    rate_type: str
    reference_rate: str
    spread_bps: Decimal | None
    floor_bps: Decimal | None
    fixed_rate: Decimal | None
    annual_amortisation: Decimal | None
    source: SourceRef | None
    terms_out_of_range: bool = False


@dataclass(frozen=True, slots=True)
class PfAdjustmentRow:
    adjustment_id: str
    label: str
    period_id: str
    classification: str
    metric_id: str
    value: Decimal
    source: SourceRef | None


@dataclass(frozen=True, slots=True)
class Cp1Registers:
    periods: tuple[PeriodRow, ...]
    accounts: tuple[AccountRow, ...]
    addbacks: tuple[AddbackRow, ...]
    segments: tuple[SegmentRow, ...]
    kpis: tuple[KpiRow, ...]
    facilities: tuple[FacilityRow, ...]
    pro_forma: tuple[PfAdjustmentRow, ...]
    currency: str
    unit: str
```

- [ ] **Step 5: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `249 passed, 110 skipped` (28 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 93.22% (floor 80%); every gate exits 0.

- [ ] **Step 6: Commit and measure the PR**

```bash
git switch -c build/03a1-registers
git add .gitignore rbot/scripts/rbotlib/model/__init__.py rbot/scripts/rbotlib/model/frame.py rbot/scripts/rbotlib/model/reader.py rbot/scripts/rbotlib/model/registers.py tests/model/test_reader.py
git commit -m "model: cell types, figure reader and CP-1 register types

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=main bash scripts/check_pr_size.sh
```

Expected: `728 changed lines (limit 800)`.

Report: `Not verified:` how `figure` reads a cell no test names (the reader's rules are the caos `_exact` rules; a new spelling in a real CP-1 Handoff may still be refused).


---

### Task 3: CP-1's tables read into registers (PR 03A2)

**Files:**
- Create: `rbot/scripts/rbotlib/model/inputs.py`
- Test: `tests/model/inputs_cases.py`, `tests/model/test_inputs.py`

**Interfaces:**
- Consumes: Task 2's reader and registers; `rbotlib.handoff.Table`.
- Produces: `rbotlib.model.inputs.cp1_registers(tables: Mapping[str, Table]) -> Cp1Registers` reading `cp1.model_period_register` (required), `cp1.model_account_register`, `cp1.adjusted_ebitda_bridge`, `cp1.segment_revenue_schedule`, `cp1.operating_kpi_schedule`, `cp1.debt_facility_register`, `cp1.pro_forma_adjustment_register` with the caos columns (§2.2); table-id constants `PERIODS` … `PRO_FORMA`; `MAX_PERIODS = 200`, `MAX_NESTING = 4`. Refusals (each a `ModelInputError` naming table, row and column) as the module docstring lists; closed vocabularies are refused when unknown (stricter than caos, which upper-cased unknown text).

**Agent:** `mx-invariants`.

- [ ] **Step 1: Write the failing tests**

`tests/model/inputs_cases.py`:

```python
"""CP-1 tables built cell by cell, shared by the input tests."""

from __future__ import annotations

import re

import pytest

from rbotlib.handoff import Table
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.reader import ModelInputError

PERIOD_COLUMNS = [
    "period_id",
    "fiscal_year",
    "fiscal_quarter",
    "period_type",
    "start_date",
    "end_date",
    "day_count",
    "currency",
    "unit",
    "component_period_ids",
]


FY2025 = ["FY2025", "FY2025", "—", "FY", "2025-01-01", "2025-12-31", "365", "USD", "MILLIONS", "—"]


def _periods(*rows: list[str]) -> Table:
    return Table(PERIOD_COLUMNS, [list(r) for r in rows])


def _tables(**extra: Table) -> dict[str, Table]:
    tables = {"cp1.model_period_register": _periods(FY2025)}
    tables.update({f"cp1.{k}": v for k, v in extra.items()})
    return tables


def _refused(tables: dict[str, Table], match: str) -> None:
    with pytest.raises(ModelInputError, match=re.escape(match)):
        cp1_registers(tables)
```

`tests/model/test_inputs.py`:

```python
"""CP-1's tables read into registers, and what is refused."""

from __future__ import annotations

import re
from decimal import Decimal

import pytest
from inputs_cases import FY2025, PERIOD_COLUMNS, _periods, _refused, _tables

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.reader import ModelInputError

FACILITY_COLUMNS = [
    "facility_id",
    "facility_name",
    "period_id",
    "facility_type",
    "currency",
    "carrying_value",
    "drawn_amount",
    "commitment",
    "secured_status",
    "seniority",
    "margin_or_coupon",
    "maturity_date",
    "lease_classification",
    "source_id",
    "source_locator",
]


TLB = [
    "TLB",
    "Term Loan B",
    "FY2025",
    "Term loan",
    "USD",
    "2,018",
    "2,018",
    "—",
    "SECURED",
    "SENIOR",
    "SOFR + 225",
    "2030-02-06",
    "NOT_LEASE",
    "[C4]",
    "p.12",
]


def _facility(**cells: str) -> Table:
    row = dict(zip(FACILITY_COLUMNS, TLB, strict=True))
    row.update(cells)
    return Table(list(row), [list(row.values())])


def test_reads_every_register_with_sources_kept_verbatim() -> None:
    accounts = Table(
        ["metric_id", "period_id", "value", "calculation_status", "source_id", "source_locator"],
        [["revenue", "FY2025", "11,245.0 [C3]", "verified", "[C3]", "p.61"]],
    )
    addbacks = Table(
        [
            "addback_id",
            "addback_label",
            "addback_classification",
            "realization_status",
            "display_priority",
            "period_id",
            "value",
            "source_id",
            "source_locator",
        ],
        [["A1", "Synergies", "synergy", "unrealized", "1", "FY2025", "40", "[C5]", "p.3"]],
    )
    segments = Table(
        [
            "segment_id",
            "segment_name",
            "segment_type",
            "display_priority",
            "period_id",
            "revenue",
            "source_id",
            "source_locator",
        ],
        [["lv", "Las Vegas", "operating segment", "1", "FY2025", "4,213", "[C6]", "p.70"]],
    )
    kpis = Table(
        [
            "kpi_id",
            "kpi_label",
            "display_priority",
            "period_id",
            "value",
            "unit",
            "value_type",
            "source_id",
            "source_locator",
        ],
        [["occ", "Occupancy", "1", "FY2025", "96.1%", "percent", "RATE", "—", "—"]],
    )
    pro_forma = Table(
        [
            "adjustment_id",
            "label",
            "period_id",
            "effective_date",
            "classification",
            "metric_id",
            "value",
            "source_id",
            "source_locator",
        ],
        [
            [
                "PF1",
                "New TLB",
                "FY2025",
                "2026-01-01",
                "refinancing",
                "facility:NEW-1",
                "500",
                "[C7]",
                "p.2",
            ]
        ],
    )
    regs = cp1_registers(
        _tables(
            model_account_register=accounts,
            adjusted_ebitda_bridge=addbacks,
            segment_revenue_schedule=segments,
            operating_kpi_schedule=kpis,
            debt_facility_register=_facility(),
            pro_forma_adjustment_register=pro_forma,
        )
    )
    assert (regs.currency, regs.unit) == ("USD", "MILLIONS")
    assert regs.periods[0].day_count == 365
    assert regs.periods[0].fiscal_quarter is None
    account = regs.accounts[0]
    assert (account.value, account.calculation_status) == (Decimal("11245.0"), "VERIFIED")
    assert account.source == SourceRef("[C3]", "p.61", "11,245.0 [C3]")
    addback = regs.addbacks[0]
    assert (addback.classification, addback.realization_status) == ("SYNERGY", "UNREALIZED")
    assert regs.segments[0].segment_type == "OPERATING_SEGMENT"
    assert regs.segments[0].revenue == Decimal(4213)
    kpi = regs.kpis[0]
    assert (kpi.value, kpi.unit, kpi.source) == (Decimal("96.1"), "PERCENT", None)
    facility = regs.facilities[0]
    assert facility.facility_type == "TERM LOAN"
    assert (facility.carrying_value, facility.commitment) == (Decimal(2018), None)
    assert (facility.rate_type, facility.reference_rate) == ("NOT_STATED", "NOT_STATED")
    assert facility.terms_out_of_range is False
    assert regs.pro_forma[0].classification == "REFINANCING"
    assert regs.pro_forma[0].metric_id == "facility:NEW-1"


@pytest.mark.parametrize("null", ["—", "n/a", "null", "", "-"])
def test_null_text_is_no_figure(null: str) -> None:
    regs = cp1_registers(_tables(debt_facility_register=_facility(carrying_value=null)))
    assert regs.facilities[0].carrying_value is None


def test_text_that_is_not_a_figure_is_refused_naming_where() -> None:
    _refused(
        _tables(debt_facility_register=_facility(carrying_value="about 2bn")),
        "cp1.debt_facility_register row 1 column carrying_value: 'about 2bn' is not a figure",
    )


@pytest.mark.parametrize(
    ("cells", "match"),
    [
        ({"seniority": "Senior secured"}, "row 1 column seniority: 'Senior secured' is not one of"),
        ({"secured_status": "—"}, "row 1 column secured_status: required, found null"),
        ({"facility_id": "—"}, "row 1 column facility_id: required, found null"),
        ({"carrying_value": "-5"}, "column carrying_value: negative outside a DEBT ADJUSTMENT"),
        ({"commitment": "-1"}, "row 1 column commitment: cannot be negative"),
        ({"carrying_value": "1e18"}, "column carrying_value: figure out of range"),
        ({"carrying_value": "1e999999x"}, "column carrying_value: figure out of range"),
        ({"carrying_value": "0.12345678901"}, "column carrying_value: more than 10 decimals"),
    ],
)
def test_a_bad_facility_row_is_refused_naming_where(cells: dict[str, str], match: str) -> None:
    _refused(_tables(debt_facility_register=_facility(**cells)), match)


def test_enumerations_read_canonical_spellings_and_open_columns_upper_case() -> None:
    table = _facility(
        facility_type="debt-adjustment",
        carrying_value="(170)",
        currency="usd",
        seniority="super senior",
        lease_classification="finance lease",
    )
    row = cp1_registers(_tables(debt_facility_register=table)).facilities[0]
    assert row.facility_type == "DEBT ADJUSTMENT"
    assert row.carrying_value == Decimal(-170)
    assert (row.currency, row.seniority) == ("USD", "SUPER_SENIOR")
    assert row.lease_classification == "FINANCE_LEASE"


def test_rate_terms_read_not_stated_or_flag_a_wrong_unit() -> None:
    terms = {"rate_type": "floating", "reference_rate": "term sofr", "spread_bps": "225"}
    row = cp1_registers(_tables(debt_facility_register=_facility(**terms))).facilities[0]
    assert (row.rate_type, row.reference_rate) == ("FLOATING", "TERM_SOFR")
    assert (row.spread_bps, row.terms_out_of_range) == (Decimal(225), False)
    for wrong in ({"spread_bps": "2.25%"}, {"floor_bps": "0.5"}, {"fixed_rate": "0.065"}):
        row = cp1_registers(_tables(debt_facility_register=_facility(**wrong))).facilities[0]
        assert row.terms_out_of_range is True, wrong


def test_absent_tables_read_as_no_rows() -> None:
    regs = cp1_registers(_tables())
    for rows in (regs.accounts, regs.addbacks, regs.segments, regs.kpis):
        assert rows == ()
    assert (regs.facilities, regs.pro_forma) == ((), ())


def test_the_period_register_is_required() -> None:
    with pytest.raises(ModelInputError, match=re.escape("cp1.model_period_register: no rows")):
        cp1_registers({})
    _refused({"cp1.model_period_register": _periods()}, "no rows")


def test_a_missing_column_or_a_ragged_row_is_refused() -> None:
    table = Table(PERIOD_COLUMNS[:-1], [FY2025[:-1]])
    _refused({"cp1.model_period_register": table}, "missing column component_period_ids")
    ragged = Table(PERIOD_COLUMNS, [FY2025[:-1]])
    _refused({"cp1.model_period_register": ragged}, "row 1: 9 cells, header has 10")
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_inputs.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.inputs'`.

- [ ] **Step 3: Write the reader of CP-1's tables**

`rbot/scripts/rbotlib/model/inputs.py`:

```python
"""CP-1's Model-input tables read into the credit model's typed registers
(`rbotlib.model.registers`).

Port of caos `caos/methodology/model_inputs.py` at `5c3cd52f`, CP-1 part only
(CP-2G's drivers arrive with the projection port), reading
`rbotlib.handoff.Table`s keyed by table id through `rbotlib.model.reader`,
which refuses with `ModelInputError` naming table, row and column.

Every enumerated column is closed (`docs/model/enums.md`) except
`facility_type`, `currency` and a KPI's `unit`, which read in upper case
(`DEBT ADJUSTMENT` is the one facility type the Model acts on). A table the
Handoff does not carry reads as no rows, except the period register.
Refused, besides what `reader` refuses: a null in a required column; two
currencies or two units across the period register; one register id twice in
one period; two periods for one fiscal quarter, YTD or year; a fiscal year
without a four-digit year, outside 1900-2200 or more than a year from its end
date's year; more than `MAX_PERIODS` periods; a period naming a component
twice or nesting components past `MAX_NESTING` (or in a cycle); a start after
its end; a day count that is not end - start + 1 or not positive; a negative
facility carrying value other than a `DEBT ADJUSTMENT` row's; a negative
commitment, drawing, RCF commitment or RCF drawing; and a pro forma row
without a figure. A rate term written in the wrong unit (a spread or floor
with `%` or not whole basis points, a fixed coupon outside 0.5-30 percent) is
kept, the row flagged `terms_out_of_range`; the rate columns are absent from
an older register and read as `NOT_STATED`.

Pure: no I/O.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from decimal import Decimal

from rbotlib.handoff import Table
from rbotlib.model.reader import (
    FIRST_YEAR,
    LAST_YEAR,
    ModelInputError,
    Row,
    date_cell,
    decimal,
    distinct,
    enum,
    ids,
    integer,
    optional,
    read,
    required_decimal,
    required_text,
    source,
    text,
)
from rbotlib.model.registers import (
    ADDBACK_CLASSIFICATIONS,
    CALCULATION_STATUSES,
    FACILITY_TYPES,
    KPI_VALUE_TYPES,
    LEASE_CLASSIFICATIONS,
    PERIOD_TYPES,
    PERIOD_UNITS,
    PF_CLASSIFICATIONS,
    RATE_TYPES,
    REALIZATION_STATUSES,
    REFERENCE_RATES,
    SECURED_STATUSES,
    SEGMENT_TYPES,
    SENIORITIES,
    AccountRow,
    AddbackRow,
    Cp1Registers,
    FacilityRow,
    KpiRow,
    PeriodRow,
    PfAdjustmentRow,
    SegmentRow,
    fiscal_year_number,
)

PERIODS = "cp1.model_period_register"
ACCOUNTS = "cp1.model_account_register"
ADDBACKS = "cp1.adjusted_ebitda_bridge"
SEGMENTS = "cp1.segment_revenue_schedule"
KPIS = "cp1.operating_kpi_schedule"
FACILITIES = "cp1.debt_facility_register"
PRO_FORMA = "cp1.pro_forma_adjustment_register"

_OPEN: frozenset[str] = frozenset()
_MAX_DAYS = (date(LAST_YEAR, 12, 31) - date(FIRST_YEAR, 1, 1)).days + 1
MAX_PERIODS = 200
MAX_NESTING = 4
_COUPON_RANGE = (Decimal("0.5"), Decimal(30))
_BPS_TERMS = ("spread_bps", "floor_bps")
_DEBT_ADJUSTMENT = "DEBT ADJUSTMENT"
_RCF_BALANCES = frozenset({"rcf_drawn", "rcf_commitment"})


def _rate_term(row: Row, column: str, vocabulary: frozenset[str]) -> str:
    if optional(row, column) is None:
        return "NOT_STATED"
    return enum(row, column, vocabulary)


def _priority(row: Row) -> int:
    priority = integer(row, "display_priority")
    if priority is None:
        raise row.refuse("display_priority", "required, found null")
    return priority


def _span(row: Row) -> tuple[date | None, date | None, int | None]:
    start, end = date_cell(row, "start_date"), date_cell(row, "end_date")
    days = integer(row, "day_count")
    if start is not None and end is not None:
        if start > end:
            raise row.refuse("start_date", "after end_date")
        if days is not None and days != (end - start).days + 1:
            raise row.refuse("day_count", f"{days} is not end - start + 1")
    if days is not None and not 1 <= days <= _MAX_DAYS:
        raise row.refuse("day_count", f"{days} is out of range")
    return start, end, days


def _components(row: Row) -> tuple[str, ...]:
    found = ids(row, "component_period_ids")
    if len(set(found)) != len(found):
        raise row.refuse("component_period_ids", "names a component twice")
    return found


def _fiscal_year(row: Row, end: date | None) -> str:
    value = text(row, "fiscal_year")
    year = fiscal_year_number(value)
    if year is None or not FIRST_YEAR <= year <= LAST_YEAR:
        raise row.refuse("fiscal_year", f"{value!r} has no four-digit year in 1900-2200")
    if end is not None and abs(year - end.year) > 1:
        raise row.refuse("fiscal_year", f"{value!r} is more than a year from end_date")
    return value


_PERIOD_COLUMNS = frozenset(
    {
        "period_id",
        "fiscal_year",
        "fiscal_quarter",
        "period_type",
        "start_date",
        "end_date",
        "day_count",
        "currency",
        "unit",
        "component_period_ids",
    }
)


def _period(row: Row) -> PeriodRow:
    start, end, days = _span(row)
    return PeriodRow(
        period_id=required_text(row, "period_id"),
        fiscal_year=_fiscal_year(row, end),
        fiscal_quarter=optional(row, "fiscal_quarter"),
        period_type=enum(row, "period_type", PERIOD_TYPES),
        start_date=None if start is None else start.isoformat(),
        end_date=None if end is None else end.isoformat(),
        day_count=days,
        currency=enum(row, "currency", _OPEN, closed=False),
        unit=enum(row, "unit", PERIOD_UNITS),
        component_period_ids=_components(row),
    )


_ACCOUNT_COLUMNS = frozenset(
    {"metric_id", "period_id", "value", "calculation_status", "source_id", "source_locator"}
)


def _account(row: Row) -> AccountRow:
    metric_id = required_text(row, "metric_id")
    value = decimal(row, "value")
    if metric_id in _RCF_BALANCES and value is not None and value < 0:
        raise row.refuse("value", f"{metric_id} is a balance and cannot be negative")
    return AccountRow(
        metric_id=metric_id,
        period_id=required_text(row, "period_id"),
        value=value,
        calculation_status=enum(row, "calculation_status", CALCULATION_STATUSES),
        source=source(row, "value"),
    )


_ADDBACK_COLUMNS = frozenset(
    {
        "addback_id",
        "addback_label",
        "addback_classification",
        "realization_status",
        "display_priority",
        "period_id",
        "value",
        "source_id",
        "source_locator",
    }
)


def _addback(row: Row) -> AddbackRow:
    return AddbackRow(
        addback_id=required_text(row, "addback_id"),
        label=required_text(row, "addback_label"),
        classification=enum(row, "addback_classification", ADDBACK_CLASSIFICATIONS),
        realization_status=enum(row, "realization_status", REALIZATION_STATUSES),
        display_priority=_priority(row),
        period_id=required_text(row, "period_id"),
        value=decimal(row, "value"),
        source=source(row, "value"),
    )


_SEGMENT_COLUMNS = frozenset(
    {
        "segment_id",
        "segment_name",
        "segment_type",
        "display_priority",
        "period_id",
        "revenue",
        "source_id",
        "source_locator",
    }
)


def _segment(row: Row) -> SegmentRow:
    return SegmentRow(
        segment_id=required_text(row, "segment_id"),
        segment_name=required_text(row, "segment_name"),
        segment_type=enum(row, "segment_type", SEGMENT_TYPES),
        display_priority=_priority(row),
        period_id=required_text(row, "period_id"),
        revenue=decimal(row, "revenue"),
        source=source(row, "revenue"),
    )


_KPI_COLUMNS = frozenset(
    {
        "kpi_id",
        "kpi_label",
        "display_priority",
        "period_id",
        "value",
        "unit",
        "value_type",
        "source_id",
        "source_locator",
    }
)


def _kpi(row: Row) -> KpiRow:
    return KpiRow(
        kpi_id=required_text(row, "kpi_id"),
        kpi_label=required_text(row, "kpi_label"),
        display_priority=_priority(row),
        period_id=required_text(row, "period_id"),
        value=decimal(row, "value"),
        unit=enum(row, "unit", _OPEN, closed=False),
        value_type=enum(row, "value_type", KPI_VALUE_TYPES),
        source=source(row, "value"),
    )


# Not the rate and amortisation columns: an older register has none.
_FACILITY_COLUMNS = frozenset(
    {
        "facility_id",
        "facility_name",
        "period_id",
        "facility_type",
        "currency",
        "carrying_value",
        "drawn_amount",
        "commitment",
        "secured_status",
        "seniority",
        "margin_or_coupon",
        "maturity_date",
        "lease_classification",
        "source_id",
        "source_locator",
    }
)


def _non_negative(row: Row, column: str) -> Decimal | None:
    value = decimal(row, column)
    if value is not None and value < 0:
        raise row.refuse(column, "cannot be negative")
    return value


def _out_of_range(row: Row) -> bool:
    for column in _BPS_TERMS:
        value = decimal(row, column)
        if value is None:
            continue
        if "%" in text(row, column) or value != value.to_integral_value():
            return True
    coupon = decimal(row, "fixed_rate")
    low, high = _COUPON_RANGE
    return coupon is not None and not low <= coupon <= high


def _facility(row: Row) -> FacilityRow:
    facility_type = enum(row, "facility_type", FACILITY_TYPES, closed=False)
    carrying = decimal(row, "carrying_value")
    if carrying is not None and carrying < 0 and facility_type != _DEBT_ADJUSTMENT:
        raise row.refuse("carrying_value", "negative outside a DEBT ADJUSTMENT row")
    return FacilityRow(
        facility_id=required_text(row, "facility_id"),
        facility_name=required_text(row, "facility_name"),
        period_id=required_text(row, "period_id"),
        facility_type=facility_type,
        currency=enum(row, "currency", _OPEN, closed=False),
        carrying_value=carrying,
        commitment=_non_negative(row, "commitment"),
        drawn_amount=_non_negative(row, "drawn_amount"),
        secured_status=enum(row, "secured_status", SECURED_STATUSES),
        seniority=enum(row, "seniority", SENIORITIES),
        lease_classification=enum(row, "lease_classification", LEASE_CLASSIFICATIONS),
        maturity_date=optional(row, "maturity_date"),
        margin_or_coupon=text(row, "margin_or_coupon"),
        rate_type=_rate_term(row, "rate_type", RATE_TYPES),
        reference_rate=_rate_term(row, "reference_rate", REFERENCE_RATES),
        spread_bps=decimal(row, "spread_bps"),
        floor_bps=decimal(row, "floor_bps"),
        fixed_rate=decimal(row, "fixed_rate"),
        annual_amortisation=decimal(row, "annual_amortisation"),
        source=source(row, "carrying_value"),
        terms_out_of_range=_out_of_range(row),
    )


_PRO_FORMA_COLUMNS = frozenset(
    {
        "adjustment_id",
        "label",
        "period_id",
        "effective_date",
        "classification",
        "metric_id",
        "value",
        "source_id",
        "source_locator",
    }
)


def _pro_forma(row: Row) -> PfAdjustmentRow:
    return PfAdjustmentRow(
        adjustment_id=required_text(row, "adjustment_id"),
        label=required_text(row, "label"),
        period_id=required_text(row, "period_id"),
        classification=enum(row, "classification", PF_CLASSIFICATIONS),
        metric_id=required_text(row, "metric_id"),
        value=required_decimal(row, "value"),
        source=source(row, "value"),
    )


def _one(values: Sequence[str], column: str) -> str:
    found = sorted(set(values))
    if len(found) != 1:
        raise ModelInputError(f"{PERIODS} column {column}: states {', '.join(found)}; need one")
    return found[0]


def _fiscal_period(period: PeriodRow) -> tuple[str, int | None, str] | None:
    year = fiscal_year_number(period.fiscal_year)
    if period.period_type == "FY":
        return "FY", year, ""
    if period.period_type in {"QUARTER", "YTD"} and period.fiscal_quarter:
        return period.period_type, year, period.fiscal_quarter.upper().removeprefix("Q")
    return None


def _one_each(periods: tuple[PeriodRow, ...]) -> tuple[PeriodRow, ...]:
    seen: set[tuple[str, int | None, str]] = set()
    for number, period in enumerate(periods, 1):
        covered = _fiscal_period(period)
        if covered is None:
            continue
        if covered in seen:
            raise ModelInputError(f"{PERIODS} row {number}: a second period for {covered}")
        seen.add(covered)
    return periods


def _depth(
    period_id: str,
    components: Mapping[str, tuple[str, ...]],
    depths: dict[str, int],
    open_ids: frozenset[str],
) -> int:
    if period_id in depths:
        return depths[period_id]
    if period_id in open_ids:
        raise ModelInputError(f"{PERIODS} period {period_id}: components form a cycle")
    inner = open_ids | {period_id}
    parts = components.get(period_id, ())
    depth = max((_depth(p, components, depths, inner) + 1 for p in parts), default=0)
    if depth > MAX_NESTING:
        raise ModelInputError(f"{PERIODS} period {period_id}: nested past {MAX_NESTING}")
    depths[period_id] = depth
    return depth


def _bounded(periods: tuple[PeriodRow, ...]) -> tuple[PeriodRow, ...]:
    if len(periods) > MAX_PERIODS:
        raise ModelInputError(f"{PERIODS}: more than {MAX_PERIODS} periods")
    components = {p.period_id: p.component_period_ids for p in periods}
    depths: dict[str, int] = {}
    for period in periods:
        _depth(period.period_id, components, depths, frozenset())
    return periods


def cp1_registers(tables: Mapping[str, Table]) -> Cp1Registers:
    """CP-1's period, account, add-back, segment, KPI, debt and pro forma
    registers as typed rows, in the one currency and unit of the period
    register."""
    periods = _bounded(
        distinct(
            PERIODS,
            _one_each(read(tables, PERIODS, _PERIOD_COLUMNS, _period)),
            lambda p: (p.period_id,),
        )
    )
    if not periods:
        raise ModelInputError(f"{PERIODS}: no rows; the Model needs at least one period")
    return Cp1Registers(
        periods=periods,
        accounts=distinct(
            ACCOUNTS,
            read(tables, ACCOUNTS, _ACCOUNT_COLUMNS, _account),
            lambda a: (a.metric_id, a.period_id),
        ),
        addbacks=distinct(
            ADDBACKS,
            read(tables, ADDBACKS, _ADDBACK_COLUMNS, _addback),
            lambda b: (b.addback_id, b.period_id),
        ),
        segments=distinct(
            SEGMENTS,
            read(tables, SEGMENTS, _SEGMENT_COLUMNS, _segment),
            lambda g: (g.segment_id, g.period_id),
        ),
        kpis=distinct(
            KPIS, read(tables, KPIS, _KPI_COLUMNS, _kpi), lambda k: (k.kpi_id, k.period_id)
        ),
        facilities=distinct(
            FACILITIES,
            read(tables, FACILITIES, _FACILITY_COLUMNS, _facility),
            lambda f: (f.facility_id, f.period_id),
        ),
        pro_forma=distinct(
            PRO_FORMA,
            read(tables, PRO_FORMA, _PRO_FORMA_COLUMNS, _pro_forma),
            lambda a: (a.adjustment_id, a.period_id),
        ),
        currency=_one([p.currency for p in periods], "currency"),
        unit=_one([p.unit for p in periods], "unit"),
    )
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `269 passed, 110 skipped` (48 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 96.62% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03a2-inputs
git add rbot/scripts/rbotlib/model/inputs.py tests/model/inputs_cases.py tests/model/test_inputs.py
git commit -m "model: CP-1 tables read into registers

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03a1-registers bash scripts/check_pr_size.sh
```

Expected: `752 changed lines (limit 800)`.

Report: `Not verified:` a CP-1 Handoff written by a model (Plan 05): only hand-built tables are read here.


---

### Task 4: Cell arithmetic and the worked example (PR 03A3)

**Files:**
- Create: `rbot/scripts/rbotlib/model/_cells.py`, `tests/model/credit_model_fixture.py`
- Test: `tests/model/test_credit_model_cells.py`

**Interfaces:**
- Consumes: `frame`, `registers`.
- Produces (ported): `rbotlib.model._cells`: `CONTEXT`, `calc(parts, note=None)`, `refs`, `join_notes`, `flipped`, `beyond_rounding`, `no_negative_zero`, `opening_date`, `periods_at`, note constants (`DIFFERS`, `FOREIGN`, `RESIDUAL`, `SIGN_NORMALISED`, `UNSPANNED`), `ABSENT`. Test support `tests/model/credit_model_fixture.py`: `example_registers()` (caos Example Gaming Co., USD millions: FY2023–FY2025, Q1 2024–Q2 2026, H1 2025/H1 2026, LTM_Q2_2026, four PF rows) and `with_figures(regs, period_id, figures)`; the projection fixtures are cut.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests and the worked example from the kit**

```bash
cp "$KIT/out/tests/model/credit_model_fixture.py" tests/model/credit_model_fixture.py
cp "$KIT/out/tests/model/test_credit_model_cells.py" tests/model/test_credit_model_cells.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_cells.py --no-cov`
Expected: collection errors with `ImportError: cannot import name '_cells' from 'rbotlib.model'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/_cells.py" rbot/scripts/rbotlib/model/_cells.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `289 passed, 110 skipped` (68 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 96.69% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03a3-cells
git add rbot/scripts/rbotlib/model/_cells.py tests/model/test_credit_model_cells.py tests/model/credit_model_fixture.py
git commit -m "model: cell arithmetic and the worked example (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03a2-inputs bash scripts/check_pr_size.sh
```

Expected: `787 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the caos tests ported here.


---

### Task 5: Historical columns (PR 03B1)

**Files:**
- Create: `rbot/scripts/rbotlib/model/periods.py`, `tests/model/history_cases.py`
- Test: `tests/model/test_credit_model_periods.py`

**Interfaces:**
- Consumes: `_cells`, `frame`, `registers`.
- Produces (ported, the column half of caos `history.py`): `rbotlib.model.periods.historical_columns(regs) -> tuple[Column, ...]` (quarters, PYTD, YTD, FY, LTM; derived periods and labels such as `Q2 26`, `YTD H1 26`, `FY25`, `LTM Q2 26`). Test support `history_cases.py` (registers built from period ids).

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests from the kit**

```bash
cp "$KIT/out/tests/model/history_cases.py" tests/model/history_cases.py
cp "$KIT/out/tests/model/test_credit_model_periods.py" tests/model/test_credit_model_periods.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_periods.py --no-cov`
Expected: collection errors with `ImportError: cannot import name 'periods' from 'rbotlib.model'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/periods.py" rbot/scripts/rbotlib/model/periods.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `296 passed, 110 skipped` (75 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 95.29% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03b1-periods
git add rbot/scripts/rbotlib/model/periods.py tests/model/history_cases.py tests/model/test_credit_model_periods.py
git commit -m "model: historical columns (caos port, history split)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03a3-cells bash scripts/check_pr_size.sh
```

Expected: `749 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the caos tests ported here.


---

### Task 6: Historical frames (PR 03B2)

**Files:**
- Create: `rbot/scripts/rbotlib/model/history.py`, `tests/model/history_frames.py`
- Test: `tests/model/test_credit_model_history.py`

**Interfaces:**
- Consumes: `periods`, `_cells`.
- Produces (ported): `rbotlib.model.history`: `account_frame(regs, columns) -> Frame`, `ltm_frames(regs, columns)`, `FLOW_METRICS`, `BALANCE_METRICS`, `OUTFLOW_METRICS`, `PARTLY_STATED`, and `historical_columns` re-exported from `periods`. Test support `history_frames.py`.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests from the kit**

```bash
cp "$KIT/out/tests/model/history_frames.py" tests/model/history_frames.py
cp "$KIT/out/tests/model/test_credit_model_history.py" tests/model/test_credit_model_history.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_history.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.history'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/history.py" rbot/scripts/rbotlib/model/history.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `302 passed, 110 skipped` (81 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 93.67% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03b2-history
git add rbot/scripts/rbotlib/model/history.py tests/model/history_frames.py tests/model/test_credit_model_history.py
git commit -m "model: historical frames (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03b1-periods bash scripts/check_pr_size.sh
```

Expected: `799 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the caos tests ported here.


---

### Task 7: History tests: derived flows and register shapes (PR 03B3)

**Files:**
- Test: `tests/model/test_credit_model_history_flows.py`, `tests/model/test_credit_model_history_registers.py`

**Interfaces:**
- Consumes: `periods`, `history`.
- Produces: no code; caos history tests for derived flows, balances, KPIs, rolling LTMs and every period-register shape.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_history_flows.py" tests/model/test_credit_model_history_flows.py
cp "$KIT/out/tests/model/test_credit_model_history_registers.py" tests/model/test_credit_model_history_registers.py
```

- [ ] **Step 2:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 3: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `331 passed, 110 skipped` (110 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 96.09% (floor 80%); every gate exits 0.

- [ ] **Step 4: Commit and measure the PR**

```bash
git switch -c build/03b3-history-flows
git add tests/model/test_credit_model_history_flows.py tests/model/test_credit_model_history_registers.py
git commit -m "model: history tests for derived flows and registers (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03b2-history bash scripts/check_pr_size.sh
```

Expected: `749 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 8: History tests: sparse items; period-register refusals (PR 03B4)

**Files:**
- Test: `tests/model/test_credit_model_history_sparse.py`, `tests/model/test_inputs_periods.py`

**Interfaces:**
- Consumes: `history`, `inputs`.
- Produces: no code; caos tests of sparse items (a figure resolved from the periods that tile it) and the period-register refusals of `cp1_registers`.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the sparse-item tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_history_sparse.py" tests/model/test_credit_model_history_sparse.py
```

- [ ] **Step 2: Write the period-register refusal tests**

`tests/model/test_inputs_periods.py`:

```python
"""CP-1's period register and register-wide rules: what is refused."""

from __future__ import annotations

import pytest
from inputs_cases import FY2025, PERIOD_COLUMNS, _periods, _refused, _tables

from rbotlib.handoff import Table
from rbotlib.model.inputs import MAX_PERIODS, cp1_registers


def _period(**cells: str) -> list[str]:
    row = dict(zip(PERIOD_COLUMNS, FY2025, strict=True))
    row.update(cells)
    return list(row.values())


@pytest.mark.parametrize(
    ("cells", "match"),
    [
        ({"day_count": "364"}, "column day_count: 364 is not end - start"),
        ({"start_date": "2026-01-01"}, "column start_date: after end_date"),
        ({"end_date": "2025-02-30"}, "column end_date: '2025-02-30' is not a YYYY-MM-DD"),
        ({"fiscal_year": "FY"}, "column fiscal_year: 'FY' has no four-digit year"),
        ({"fiscal_year": "FY2030"}, "more than a year from end_date"),
        ({"period_type": "HALF"}, "column period_type: 'HALF' is not one of"),
        ({"unit": "billions"}, "column unit: 'billions' is not one of"),
        ({"day_count": "1.5"}, "column day_count: not a whole number"),
        ({"start_date": "—", "end_date": "—", "day_count": "0"}, "day_count: 0 is out of range"),
        ({"component_period_ids": "Q1;Q1"}, "names a component twice"),
    ],
)
def test_a_bad_period_is_refused_naming_where(cells: dict[str, str], match: str) -> None:
    _refused({"cp1.model_period_register": _periods(_period(**cells))}, match)


def test_period_register_wide_checks() -> None:
    eur = _period(period_id="FY2024", fiscal_year="FY2024", currency="EUR")
    eur = _period(
        period_id="FY2024",
        fiscal_year="FY2024",
        start_date="2024-01-01",
        end_date="2024-12-31",
        day_count="366",
        currency="EUR",
    )
    _refused({"cp1.model_period_register": _periods(FY2025, eur)}, "states EUR, USD; need one")
    twice = _period(period_id="FY2025b")
    _refused({"cp1.model_period_register": _periods(FY2025, twice)}, "a second period")
    same_id = _period(period_type="LTM")
    _refused({"cp1.model_period_register": _periods(FY2025, same_id)}, "FY2025 written twice")
    cycle = [
        _period(period_id="A", period_type="LTM", component_period_ids="B"),
        _period(period_id="B", period_type="LTM", component_period_ids="A"),
    ]
    _refused({"cp1.model_period_register": _periods(*cycle)}, "components form a cycle")
    chain = [
        _period(period_id=f"P{i}", period_type="LTM", component_period_ids=f"P{i + 1}")
        for i in range(6)
    ]
    _refused({"cp1.model_period_register": _periods(*chain)}, "nested past 4")
    quarter = {"period_type": "QUARTER", "fiscal_quarter": "Q2", "start_date": "2025-04-01"}
    quarter |= {"end_date": "2025-06-30", "day_count": "91"}
    quarters = [_period(period_id="Q2", **quarter), _period(period_id="Q2b", **quarter)]
    _refused({"cp1.model_period_register": _periods(*quarters)}, "a second period for")
    shared = [
        _period(period_id="A", period_type="LTM", component_period_ids="C"),
        _period(period_id="B", period_type="LTM", component_period_ids="C"),
        _period(period_id="C", period_type="LTM", start_date="—", end_date="—", day_count="—"),
    ]
    periods = cp1_registers({"cp1.model_period_register": _periods(*shared)}).periods
    assert [(p.period_id, p.start_date, p.day_count) for p in periods][2] == ("C", None, None)
    many = [_period(period_id=f"P{i}", period_type="LTM") for i in range(MAX_PERIODS + 1)]
    _refused({"cp1.model_period_register": _periods(*many)}, "more than 200 periods")


def test_account_and_pro_forma_rules() -> None:
    columns = [
        "metric_id",
        "period_id",
        "value",
        "calculation_status",
        "source_id",
        "source_locator",
    ]
    rcf = Table(columns, [["rcf_drawn", "FY2025", "-1", "VERIFIED", "—", "—"]])
    _refused(_tables(model_account_register=rcf), "rcf_drawn is a balance")
    twice = Table(columns, [["revenue", "FY2025", "1", "VERIFIED", "—", "—"]] * 2)
    _refused(_tables(model_account_register=twice), "row 2: revenue / FY2025 written twice")
    status = Table(columns, [["revenue", "FY2025", "1", "GUESSED", "—", "—"]])
    _refused(_tables(model_account_register=status), "calculation_status: 'GUESSED'")
    pf_columns = [
        "adjustment_id",
        "label",
        "period_id",
        "effective_date",
        "classification",
        "metric_id",
        "value",
        "source_id",
        "source_locator",
    ]
    empty = Table(
        pf_columns,
        [["PF1", "x", "FY2025", "2026-01-01", "ACQUISITION", "revenue", "—", "[C1]", "p.1"]],
    )
    _refused(_tables(pro_forma_adjustment_register=empty), "column value: required, found null")


def test_display_priority_is_a_required_whole_number() -> None:
    columns = [
        "segment_id",
        "segment_name",
        "segment_type",
        "display_priority",
        "period_id",
        "revenue",
        "source_id",
        "source_locator",
    ]
    for priority, match in (("—", "required, found null"), ("1.5", "not a whole number")):
        table = Table(
            columns, [["lv", "LV", "OPERATING_SEGMENT", priority, "FY2025", "1", "—", "—"]]
        )
        _refused(_tables(segment_revenue_schedule=table), f"display_priority: {match}")
```

- [ ] **Step 3:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `362 passed, 110 skipped` (141 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.23% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03b4-history-sparse
git add tests/model/test_credit_model_history_sparse.py tests/model/test_inputs_periods.py
git commit -m "model: sparse-item and period-register tests

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03b3-history-flows bash scripts/check_pr_size.sh
```

Expected: `594 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 9: History tests: signs, dates and day counts (PR 03B5)

**Files:**
- Test: `tests/model/test_credit_model_history_dates.py`

**Interfaces:**
- Consumes: `history`.
- Produces: no code; caos tests of outflows written positive, malformed dates and day counts, and components that do not span their period.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_history_dates.py" tests/model/test_credit_model_history_dates.py
```

- [ ] **Step 2:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 3: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `393 passed, 110 skipped` (172 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.29% (floor 80%); every gate exits 0.

- [ ] **Step 4: Commit and measure the PR**

```bash
git switch -c build/03b5-history-dates
git add tests/model/test_credit_model_history_dates.py
git commit -m "model: history tests for signs, dates and day counts (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03b4-history-sparse bash scripts/check_pr_size.sh
```

Expected: `503 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 10: History tests: interims; the CP-1 Handoff builder and the round trip (PR 03B6)

**Files:**
- Create: `tests/model/model_handoffs.py`
- Test: `tests/model/test_credit_model_history_interims.py`, `tests/model/test_round_trip.py`

**Interfaces:**
- Consumes: `history`, `inputs`, `registers`, Plan 02's Handoff parser (escaped pipes).
- Produces: test support `tests/model/model_handoffs.py`: `table(table_id, columns, rows)`, `handoff(module_id, tables, citations)`, `cp1_handoff(regs, extra=()) -> str` (every register written as CP-1's tables with `[C<n>]` citations), `run_brief(ssim_ev_multiple="8.5x", tranches=())`, `run_folder(root, cp1, brief, cp1d=None) -> Path`; the property test `test_round_trip` (`cp1_registers(parse(cp1_handoff(regs)).tables) == regs` for redrawn registers).

**Agent:** `mx-precise` (the builder writes Handoff text that later tasks read).

- [ ] **Step 1: Copy the interim tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_history_interims.py" tests/model/test_credit_model_history_interims.py
```

- [ ] **Step 2: Write the Handoff builder and the round trip**

`tests/model/model_handoffs.py`:

```python
"""Write CP-1, CP-1D and Run Brief Handoffs from typed rows, for the Model's tests.

`cp1_handoff` writes CP-1's Model-input tables (interfaces spec §2.2) from a
`Cp1Registers`; each `SourceRef` id `S<n>` becomes the marker `[C<n>]` with a
citations row. `run_folder` lays a run folder out as `rbot model` reads it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from pathlib import Path

from rbotlib.model.frame import SourceRef
from rbotlib.model.registers import Cp1Registers

GAP = "\N{EM DASH}"
_SOURCE = re.compile(r"^S(\d+)$")

PERIOD_COLUMNS = ["period_id", "fiscal_year", "fiscal_quarter", "period_type", "start_date"]
PERIOD_COLUMNS += ["end_date", "day_count", "currency", "unit", "component_period_ids"]
ACCOUNT_COLUMNS = ["metric_id", "period_id", "value", "calculation_status"]
ADDBACK_COLUMNS = ["addback_id", "addback_label", "addback_classification", "realization_status"]
ADDBACK_COLUMNS += ["display_priority", "period_id", "value"]
SEGMENT_COLUMNS = ["segment_id", "segment_name", "segment_type", "display_priority"]
SEGMENT_COLUMNS += ["period_id", "revenue"]
KPI_COLUMNS = ["kpi_id", "kpi_label", "display_priority", "period_id", "value", "unit"]
KPI_COLUMNS += ["value_type"]
FACILITY_COLUMNS = ["facility_id", "facility_name", "period_id", "facility_type", "currency"]
FACILITY_COLUMNS += ["carrying_value", "drawn_amount", "commitment", "secured_status"]
FACILITY_COLUMNS += ["seniority", "margin_or_coupon", "maturity_date", "lease_classification"]
FACILITY_COLUMNS += ["rate_type", "reference_rate", "spread_bps", "floor_bps", "fixed_rate"]
FACILITY_COLUMNS += ["annual_amortisation"]
PRO_FORMA_COLUMNS = ["adjustment_id", "label", "period_id", "effective_date", "classification"]
PRO_FORMA_COLUMNS += ["metric_id", "value"]
SOURCE_COLUMNS = ["source_id", "source_locator"]


def _text(value: object) -> str:
    if value is None:
        return GAP
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _marker(source: SourceRef | None, cited: dict[str, SourceRef]) -> list[str]:
    if source is None:
        return [GAP, GAP]
    found = _SOURCE.match(source.source_id)
    marker = f"[C{found.group(1)}]" if found else source.source_id
    cited.setdefault(marker, source)
    return [marker, source.source_locator or GAP]


def table(table_id: str, columns: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    lines = [f"<!-- table: {table_id} -->", "", "| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return [*lines, ""]


def handoff(
    module_id: str, tables: Sequence[list[str]], citations: Mapping[str, tuple[str, str, str]]
) -> str:
    """A Handoff: front matter, the four sections, the tables and citations
    (`[C<n>]` -> (source, locator, excerpt)), every citation cited in a cell."""
    lines = ["---", f"module_id: {module_id}", "run_id: 20261011-egc-full-credit-assessment"]
    lines += ["issuer_id: EGC", "analysis_date: 2026-10-02", "qa_status: Pass"]
    lines += ["inputs: CP-0", "---", "", "## Analysis", "", f"{module_id} fixture.", ""]
    lines += ["## Tables", ""]
    for block in tables:
        lines += block
    lines += ["## Gaps", "", "- None.", "", "## Citations", ""]
    rows = [[m.strip("[]"), *citations[m]] for m in citations]
    lines += table("citations", ["id", "source", "locator", "excerpt"], rows)
    return "\n".join(lines)


def cp1_handoff(regs: Cp1Registers, extra: Sequence[list[str]] = ()) -> str:
    cited: dict[str, SourceRef] = {}
    periods = [
        [
            p.period_id,
            p.fiscal_year,
            p.fiscal_quarter or GAP,
            p.period_type,
            _text(p.start_date),
            _text(p.end_date),
            _text(p.day_count),
            p.currency,
            p.unit,
            "; ".join(p.component_period_ids) or GAP,
        ]
        for p in regs.periods
    ]
    accounts = [
        [a.metric_id, a.period_id, _text(a.value), a.calculation_status, *_marker(a.source, cited)]
        for a in regs.accounts
    ]
    addbacks = [
        [
            b.addback_id,
            b.label,
            b.classification,
            b.realization_status,
            str(b.display_priority),
            b.period_id,
            _text(b.value),
            *_marker(b.source, cited),
        ]
        for b in regs.addbacks
    ]
    segments = [
        [
            s.segment_id,
            s.segment_name,
            s.segment_type,
            str(s.display_priority),
            s.period_id,
            _text(s.revenue),
            *_marker(s.source, cited),
        ]
        for s in regs.segments
    ]
    kpis = [
        [
            k.kpi_id,
            k.kpi_label,
            str(k.display_priority),
            k.period_id,
            _text(k.value),
            k.unit,
            k.value_type,
            *_marker(k.source, cited),
        ]
        for k in regs.kpis
    ]
    facilities = [
        [
            f.facility_id,
            f.facility_name,
            f.period_id,
            f.facility_type,
            f.currency,
            _text(f.carrying_value),
            _text(f.drawn_amount),
            _text(f.commitment),
            f.secured_status,
            f.seniority,
            f.margin_or_coupon or GAP,
            _text(f.maturity_date),
            f.lease_classification,
            f.rate_type,
            f.reference_rate,
            _text(f.spread_bps),
            _text(f.floor_bps),
            _text(f.fixed_rate),
            _text(f.annual_amortisation),
            *_marker(f.source, cited),
        ]
        for f in regs.facilities
    ]
    pro_forma = [
        [
            a.adjustment_id,
            a.label,
            a.period_id,
            "2026-07-01",
            a.classification,
            a.metric_id,
            _text(a.value),
            *_marker(a.source, cited),
        ]
        for a in regs.pro_forma
    ]
    blocks = [
        table("cp1.model_period_register", PERIOD_COLUMNS, periods),
        table("cp1.model_account_register", ACCOUNT_COLUMNS + SOURCE_COLUMNS, accounts),
        table("cp1.adjusted_ebitda_bridge", ADDBACK_COLUMNS + SOURCE_COLUMNS, addbacks),
        table("cp1.segment_revenue_schedule", SEGMENT_COLUMNS + SOURCE_COLUMNS, segments),
        table("cp1.operating_kpi_schedule", KPI_COLUMNS + SOURCE_COLUMNS, kpis),
        table("cp1.debt_facility_register", FACILITY_COLUMNS + SOURCE_COLUMNS, facilities),
        table("cp1.pro_forma_adjustment_register", PRO_FORMA_COLUMNS + SOURCE_COLUMNS, pro_forma),
        *extra,
    ]
    citations = {
        m: (f"fixture-{s.source_id}.txt", s.source_locator, s.cell_text) for m, s in cited.items()
    }
    return handoff("CP-1", blocks, citations)


def run_brief(ssim_ev_multiple: str = "8.5x", tranches: Sequence[str] = ()) -> str:
    header = ["run_id", "issuer", "issuer_id", "as_of_date", "objective", "analyst", "pathway"]
    header += ["depth", "primary", "currency", "unit", "morningstar_issuer_id"]
    header += ["ssim_ev_multiple_x", "report_date"]
    row = [
        "20261011-egc-full-credit-assessment",
        "Example Gaming Co.",
        "EGC",
        "2026-10-02",
        "Full credit assessment",
        "Analyst",
        "FULL_CREDIT_ASSESSMENT",
        "full",
        "Yes" if tranches else "No",
        "USD",
        "MILLIONS",
        GAP,
        ssim_ev_multiple,
        "2026-10-11",
    ]
    summary = [
        [
            t,
            "Example Gaming Co.",
            GAP,
            "Term loan",
            "1L Term Loan",
            "Acquisition",
            "600",
            "USD",
            "MILLIONS",
            "S+300-325",
            "Initial talk",
            "99.0",
            "2033-06-30",
            GAP,
            GAP,
            GAP,
            "Sourced",
            GAP,
            "[C1]",
        ]
        for t in tranches
    ]
    columns = ["tranche_id", "borrower", "bloomberg_id", "instrument", "debt_type"]
    columns += ["use_of_proceeds", "size", "currency", "unit", "price_talk", "talk_stage", "oid"]
    columns += ["maturity_date", "expected_ratings", "cr_score", "commitment_date", "status"]
    columns += ["analyst_value", "cite"]
    blocks = [
        table("snapshot.run_header", header, [row]),
        table("snapshot.transaction_summary", columns, summary),
    ]
    citations = {"[C1]": ("term-sheet.txt", "p.1", "S+300-325")} if tranches else {}
    return handoff("RUN_BRIEF", blocks, citations)


def run_folder(root: Path, cp1: str, brief: str, cp1d: str | None = None) -> Path:
    run = root / "rbot-runs" / "20261011-egc-full-credit-assessment"
    (run / "handoffs").mkdir(parents=True)
    (run / "handoffs" / "CP-1.md").write_text(cp1, encoding="utf-8")
    (run / "run-brief.md").write_text(brief, encoding="utf-8")
    if cp1d is not None:
        (run / "handoffs" / "CP-1D.md").write_text(cp1d, encoding="utf-8")
    return run
```

`tests/model/test_round_trip.py`:

```python
"""CP-1's registers written as a Handoff read back to the same figures."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers
from hypothesis import given, settings
from hypothesis import strategies as st
from model_handoffs import cp1_handoff

from rbotlib.handoff import parse
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.registers import Cp1Registers

_FIGURES = st.one_of(
    st.none(),
    st.decimals(min_value=Decimal("-1e12"), max_value=Decimal("1e12"), places=4),
)


@st.composite
def _registers(draw: st.DrawFn) -> Cp1Registers:
    regs = example_registers()
    accounts = tuple(replace(a, value=draw(_FIGURES)) for a in regs.accounts[:40])
    return replace(regs, accounts=accounts)


def _figures(regs: Cp1Registers) -> list[tuple[str, str, Decimal | None]]:
    return [(a.metric_id, a.period_id, a.value) for a in regs.accounts]


@settings(max_examples=25, deadline=None)
@given(regs=_registers())
def test_written_figures_read_back_exactly(regs: Cp1Registers) -> None:
    back = cp1_registers(parse(cp1_handoff(regs)).tables)
    assert _figures(back) == [
        (m, p, None if v is None else (v.copy_abs() if v.is_zero() else v))
        for m, p, v in _figures(regs)
    ]
    assert back.periods == regs.periods
    assert [f.carrying_value for f in back.facilities] == [
        f.carrying_value for f in regs.facilities
    ]
    assert [(a.metric_id, a.value) for a in back.pro_forma] == [
        (a.metric_id, a.value) for a in regs.pro_forma
    ]
    assert all(a.source is None or a.source.source_id.startswith("[C") for a in back.accounts)
```

- [ ] **Step 3:** Run `uv run pytest tests/model --no-cov`: the interim tests and the round trip pass (they exercise merged code; the round trip is a property test of `inputs` against the builder).

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `413 passed, 110 skipped` (192 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.41% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03b6-history-interims
git add tests/model/test_credit_model_history_interims.py tests/model/model_handoffs.py tests/model/test_round_trip.py
git commit -m "model: interim tests, CP-1 Handoff builder and round trip

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03b5-history-dates bash scripts/check_pr_size.sh
```

Expected: `691 changed lines (limit 800)`.

Report: `Not verified:` a CP-1 Handoff a model writes in Copilot (Plan 05); the builder writes the form Plan 02's parser reads.


---

### Task 11: Debt stack (PR 03C1)

**Files:**
- Create: `rbot/scripts/rbotlib/model/debt.py`, `tests/model/debt_cases.py`
- Test: `tests/model/test_credit_model_debt.py`

**Interfaces:**
- Consumes: `history`, `_cells`, `registers`.
- Produces (ported): `rbotlib.model.debt`: `debt_frame(regs, columns, accounts)`, `PAYMENT_RANKS` (Super senior … Debt adjustments), `SECURED_RANKS`, `payment_rank`, `facility_keys`, `is_operating_lease`, `left_out`, `carried`, `notes_of`. Test support `debt_cases.py`.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests from the kit**

```bash
cp "$KIT/out/tests/model/debt_cases.py" tests/model/debt_cases.py
cp "$KIT/out/tests/model/test_credit_model_debt.py" tests/model/test_credit_model_debt.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_debt.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.debt'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/debt.py" rbot/scripts/rbotlib/model/debt.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `433 passed, 110 skipped` (212 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.43% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03c1-debt
git add rbot/scripts/rbotlib/model/debt.py tests/model/debt_cases.py tests/model/test_credit_model_debt.py
git commit -m "model: debt stack (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03b6-history-interims bash scripts/check_pr_size.sh
```

Expected: `733 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the caos tests ported here.


---

### Task 12: Statements (PR 03C2)

**Files:**
- Create: `rbot/scripts/rbotlib/model/statements.py`, `tests/model/statements_cases.py`
- Test: `tests/model/test_credit_model_statements.py`

**Interfaces:**
- Consumes: `history`, `debt`, `_cells`.
- Produces (ported): `rbotlib.model.statements`: `statement_frame(accounts, columns, regs, exclude_unrealised=False)`, `pro_forma_column(regs, ltm, frame) -> tuple[Column, Frame] | None` (the PF-LTM), `excluded_addbacks`, `UNREALISED`. Test support `statements_cases.py`.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests from the kit**

```bash
cp "$KIT/out/tests/model/statements_cases.py" tests/model/statements_cases.py
cp "$KIT/out/tests/model/test_credit_model_statements.py" tests/model/test_credit_model_statements.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_statements.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.statements'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/statements.py" rbot/scripts/rbotlib/model/statements.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `440 passed, 110 skipped` (219 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 96.85% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03c2-statements
git add rbot/scripts/rbotlib/model/statements.py tests/model/statements_cases.py tests/model/test_credit_model_statements.py
git commit -m "model: statements and the PF-LTM (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03c1-debt bash scripts/check_pr_size.sh
```

Expected: `743 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the caos tests ported here.


---

### Task 13: Statement tests: pro forma; debt against the statements (PR 03C3)

**Files:**
- Test: `tests/model/test_credit_model_statements_pro_forma.py`, `tests/model/test_credit_model_debt_flows.py`

**Interfaces:**
- Consumes: `statements`, `debt`.
- Produces: no code; caos tests of the PF-LTM, any consistent accounts reconciling (property test), sources and stated figures, and debt totals and roll-forward against the statement frame.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_statements_pro_forma.py" tests/model/test_credit_model_statements_pro_forma.py
cp "$KIT/out/tests/model/test_credit_model_debt_flows.py" tests/model/test_credit_model_debt_flows.py
```

- [ ] **Step 2:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 3: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `454 passed, 110 skipped` (233 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.53% (floor 80%); every gate exits 0.

- [ ] **Step 4: Commit and measure the PR**

```bash
git switch -c build/03c3-statements-pf
git add tests/model/test_credit_model_statements_pro_forma.py tests/model/test_credit_model_debt_flows.py
git commit -m "model: pro forma and debt-flow tests (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03c2-statements bash scripts/check_pr_size.sh
```

Expected: `501 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 14: Credit metrics (PR 03D1)

**Files:**
- Create: `rbot/scripts/rbotlib/model/metrics.py`, `tests/model/metrics_cases.py`
- Test: `tests/model/test_credit_model_metrics.py`

**Interfaces:**
- Consumes: `statements`, `debt`, `_cells`.
- Produces (ported, plus the port addition `gross_profit_growth`): `rbotlib.model.metrics`: `metric_frame(columns, frame, ltm_ending, *, corporate=frozenset())` — the 21 `metric:*` keys of §6.3 and growth `revenue_growth`, `gross_profit_growth`, `adjusted_ebitda_growth`, `bu_growth:<seg>`; `unit_of(key)`. Test support `metrics_cases.py`.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests from the kit**

```bash
cp "$KIT/out/tests/model/metrics_cases.py" tests/model/metrics_cases.py
cp "$KIT/out/tests/model/test_credit_model_metrics.py" tests/model/test_credit_model_metrics.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_metrics.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.metrics'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/metrics.py" rbot/scripts/rbotlib/model/metrics.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `461 passed, 110 skipped` (240 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.47% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03d1-metrics
git add rbot/scripts/rbotlib/model/metrics.py tests/model/metrics_cases.py tests/model/test_credit_model_metrics.py
git commit -m "model: credit metrics (caos port, gross profit growth)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03c3-statements-pf bash scripts/check_pr_size.sh
```

Expected: `690 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the caos tests ported here.


---

### Task 15: Metric growth tests; statement edge cases (PR 03D2)

**Files:**
- Test: `tests/model/test_credit_model_metrics_growth.py`, `tests/model/test_credit_model_statements_cases.py`

**Interfaces:**
- Consumes: `metrics`, `statements`.
- Produces: no code; caos tests of growth on like periods, PF-LTM metric variants, leases and what a metric leaves out; statement edge cases (absent rows, sparse items, foreign facilities, PF signs).

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_metrics_growth.py" tests/model/test_credit_model_metrics_growth.py
cp "$KIT/out/tests/model/test_credit_model_statements_cases.py" tests/model/test_credit_model_statements_cases.py
```

- [ ] **Step 2:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 3: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `488 passed, 110 skipped` (267 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.57% (floor 80%); every gate exits 0.

- [ ] **Step 4: Commit and measure the PR**

```bash
git switch -c build/03d2-metrics-growth
git add tests/model/test_credit_model_metrics_growth.py tests/model/test_credit_model_statements_cases.py
git commit -m "model: growth and statement edge-case tests (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03d1-metrics bash scripts/check_pr_size.sh
```

Expected: `634 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 16: Layout (PR 03D3)

**Files:**
- Create: `rbot/scripts/rbotlib/model/layout.py`
- Test: `tests/model/test_layout.py`

**Interfaces:**
- Consumes: `metrics`, `statements`, `debt`, `history`.
- Produces (ported, plus the port additions: the `gross_profit_growth` line in band 3 and the `secured_debt` memo line after `total_debt` in band 8, which §6.4's "Senior debt" reads): `rbotlib.model.layout`: `layout(regs, columns, frame, exclude_unrealised, deck_as_of) -> tuple[Line, ...]`, `Line(line_id, band, label, kind, unit, unit_label, rank, terms, cells)`, `FacilityTerms`, `facility_terms`, `BANDS` (the twelve bands of §6.3), `UNALLOCATED`, `LineKind`, `Unit`. Its own tests (`test_layout.py`) call `layout()` on the metric frame the way `assemble` does: bands in order, one cell per column, the port additions, a rank subtotal exact past 28 digits, the unallocated line on history, terms and excluded add-backs as memos.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Write the failing tests**

`tests/model/test_layout.py`:

```python
"""The layout on the worked example, read straight from the metric frame (the
way `assemble` calls it): bands in order, one cell per column, rank
subtotals, the unallocated line, terms and the port additions."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

from credit_model_fixture import example_registers

from rbotlib.model._cells import CONTEXT
from rbotlib.model.frame import Column
from rbotlib.model.history import account_frame, historical_columns, ltm_frames
from rbotlib.model.layout import BANDS, UNALLOCATED, Line, facility_terms, layout
from rbotlib.model.metrics import metric_frame
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.statements import pro_forma_column, statement_frame

PF = "PF:LTM_Q2_2026"


def _lines(
    exclude: bool = False, regs: Cp1Registers | None = None
) -> tuple[tuple[Column, ...], dict[str, Line]]:
    regs = regs or example_registers()
    historical = historical_columns(regs)
    frame = dict(statement_frame(account_frame(regs, historical), historical, regs, exclude))
    ltm = next(c for c in historical if c.kind == "LTM")
    pf = pro_forma_column(regs, ltm, frame)
    assert pf is not None
    columns = (*historical, pf[0])
    frame.update(pf[1])
    quarters = tuple(c for c in historical if c.kind == "QUARTER")
    ltm_ending = statement_frame(ltm_frames(regs, historical), quarters, regs, exclude)
    lines = layout(regs, columns, metric_frame(columns, frame, ltm_ending), exclude, None)
    assert all(len(line.cells) == len(columns) for line in lines)
    runs = [b for n, b in enumerate(x.band for x in lines) if n == 0 or b != lines[n - 1].band]
    assert runs == list(BANDS)  # every band, each once, in the layout's order
    return columns, {line.line_id: line for line in lines}


def _on(columns: tuple[Column, ...], line: Line, column_id: str) -> Decimal | None:
    return line.cells[[c.column_id for c in columns].index(column_id)].value


def test_the_port_additions_sit_in_their_bands() -> None:
    columns, lines = _lines()
    ids = list(lines)
    assert lines["gross_profit_growth"].band == BANDS[2]
    assert ids.index("secured_debt") == ids.index("total_debt") + 1
    assert lines["secured_debt"].kind == "MEMO"
    assert _on(columns, lines["revenue"], "FY:FY2025") == 11519


def test_a_rank_subtotal_sums_its_facilities_and_unallocated_is_history_free() -> None:
    columns, lines = _lines()
    secured = [x for x in lines.values() if x.rank == "Senior secured" and x.kind == "ACCOUNT"]
    values = [_on(columns, x, "FY:FY2025") for x in secured]
    total = sum((v for v in values if v is not None), Decimal(0))
    assert _on(columns, lines["rank:Senior secured"], "FY:FY2025") == total
    assert {c.reason for c in lines[UNALLOCATED].cells} == {"NOT_APPLICABLE"}
    regs = example_registers()
    tlb = next(f for f in regs.facilities if f.facility_id == "tlb" and f.period_id == "Q2_2026")
    assert lines["fac:tlb"].terms == facility_terms(tlb)


def test_a_rank_subtotal_is_exact_past_28_digits() -> None:
    big = Decimal("512345678901234567.0123456789")  # the largest the reader takes
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=big) if f.facility_id in {"tlb", "ssn29"} else f
        for f in regs.facilities
    )
    columns, lines = _lines(regs=replace(regs, facilities=facilities))
    secured = [x for x in lines.values() if x.rank == "Senior secured" and x.kind == "ACCOUNT"]
    values = [_on(columns, x, "FY:FY2025") for x in secured]
    with localcontext(CONTEXT):
        total = sum((v for v in values if v is not None), Decimal(0))
    assert _on(columns, lines["rank:Senior secured"], "FY:FY2025") == total


def test_excluded_add_backs_are_memos() -> None:
    _, lines = _lines(exclude=True)
    assert lines["addback:run_rate_cost_savings"].kind == "MEMO"
    assert lines["addback:restructuring"].kind == "ACCOUNT"
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_layout.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.layout'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/layout.py" rbot/scripts/rbotlib/model/layout.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `492 passed, 110 skipped` (271 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.14% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03d3-layout
git add rbot/scripts/rbotlib/model/layout.py tests/model/test_layout.py
git commit -m "model: bands and lines (caos port, gross profit growth, secured debt memo)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03d2-metrics-growth bash scripts/check_pr_size.sh
```

Expected: `792 changed lines (limit 800)`.

Report: `Not verified:` nothing beyond the tests here; the caos layout tests run through `assemble` from Task 17 on.


---

### Task 17: The assembled Model (PR 03D4)

**Files:**
- Create: `rbot/scripts/rbotlib/model/assemble.py`, `tests/model/assemble_cases.py`
- Test: `tests/model/test_credit_model_assemble.py`

**Interfaces:**
- Consumes: every ported module.
- Produces (ported, projection removed): `rbotlib.model.assemble`: `ModelInputs(registers, exclude_unrealised=False)`, `credit_model(inputs) -> CreditModel(currency, unit, columns, lines, rate_deck_id, limitations)`, `reconciliation_faults(model) -> tuple[str, ...]` (`<column_id>:<bridge>`), `NO_PROJECTIONS`, `NOT_APPLIED`, `DOUBLE_COUNT`. Every Model notes `NO_PROJECTIONS` and has no rate deck. Test support `assemble_cases.py`.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the failing tests from the kit**

```bash
cp "$KIT/out/tests/model/assemble_cases.py" tests/model/assemble_cases.py
cp "$KIT/out/tests/model/test_credit_model_assemble.py" tests/model/test_credit_model_assemble.py
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_credit_model_assemble.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.assemble'`.

- [ ] **Step 3: Copy the ported files from the kit**

```bash
cp "$KIT/out/rbot/scripts/rbotlib/model/assemble.py" rbot/scripts/rbotlib/model/assemble.py
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `527 passed, 110 skipped` (306 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.33% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03d4-assemble
git add rbot/scripts/rbotlib/model/assemble.py tests/model/assemble_cases.py tests/model/test_credit_model_assemble.py
git commit -m "model: the assembled Model without projections (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03d3-layout bash scripts/check_pr_size.sh
```

Expected: `746 changed lines (limit 800)`.

Report: `Not verified:` projections (Plan 13).


---

### Task 18: Layout order, port additions and history through the Model (PR 03D5)

**Files:**
- Test: `tests/model/test_credit_model_layout.py`, `tests/model/test_credit_model_history_model.py`, `tests/model/test_port_additions.py`

**Interfaces:**
- Consumes: `assemble`, `layout`, `metrics`.
- Produces: no code; the caos golden of every band and line in order (`test_credit_model_layout.py`), the two history tests that need the whole Model, and `test_port_additions.py` (gross profit growth and the secured-debt memo line on the worked example).

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_layout.py" tests/model/test_credit_model_layout.py
cp "$KIT/out/tests/model/test_credit_model_history_model.py" tests/model/test_credit_model_history_model.py
```

- [ ] **Step 2: Write the port-addition tests**

`tests/model/test_port_additions.py`:

```python
"""Deploy VI's additions to the ported model: gross profit growth (spec §6.3)."""

from __future__ import annotations

from decimal import Decimal, localcontext

from credit_model_fixture import example_registers

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.frame import Cell
from rbotlib.model.layout import BANDS
from rbotlib.model.metrics import unit_of


def _model() -> CreditModel:
    return credit_model(ModelInputs(example_registers()))


def _cell(model: CreditModel, line_id: str, column_id: str) -> Cell:
    index = [c.column_id for c in model.columns].index(column_id)
    return next(line for line in model.lines if line.line_id == line_id).cells[index]


def _value(model: CreditModel, line_id: str, column_id: str) -> Decimal:
    value = _cell(model, line_id, column_id).value
    assert value is not None, (line_id, column_id)
    return value


def test_gross_profit_growth_is_a_growth_line_after_gross_margin() -> None:
    model = _model()
    ids = [line.line_id for line in model.lines]
    assert ids.index("gross_profit_growth") == ids.index("metric:gross_margin") + 1
    line = model.lines[ids.index("gross_profit_growth")]
    assert (line.band, line.kind, line.unit) == (BANDS[2], "GROWTH", "PERCENT")
    assert line.label == "Gross profit growth YoY"
    assert unit_of("gross_profit_growth") == "PERCENT"


def test_gross_profit_growth_compares_like_periods() -> None:
    model = _model()

    def growth(column_id: str, prior_id: str) -> Decimal:
        with localcontext(CONTEXT):
            current = _value(model, "gross_profit", column_id)
            return current / _value(model, "gross_profit", prior_id) - 1

    assert _value(model, "gross_profit_growth", "FY:FY2025") == growth("FY:FY2025", "FY:FY2024")
    ytd = growth("YTD:H1_2026", "PYTD:H1_2025")
    assert _value(model, "gross_profit_growth", "YTD:H1_2026") == ytd
    assert _cell(model, "gross_profit_growth", "FY:FY2023") == Cell(None, "NOT_APPLICABLE")
    assert _cell(model, "gross_profit_growth", "PF:LTM_Q2_2026").reason == "NOT_APPLICABLE"
```

- [ ] **Step 3:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `532 passed, 110 skipped` (311 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.35% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03d5-layout-tests
git add tests/model/test_credit_model_layout.py tests/model/test_port_additions.py tests/model/test_credit_model_history_model.py
git commit -m "model: layout order, port additions and history through the Model

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03d4-assemble bash scripts/check_pr_size.sh
```

Expected: `697 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 19: Model lines and edge cases (PR 03D6)

**Files:**
- Test: `tests/model/test_credit_model_assemble_lines.py`, `tests/model/test_credit_model_assemble_cases.py`, `tests/model/test_assemble_precision.py`

**Interfaces:**
- Consumes: `assemble`.
- Produces: no code; caos tests of facility terms, metric lines, PF rows, growth lines, any consistent inputs reconciling (property test), foreign facilities, PF-register limitations, negative zeros and the bridges.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Copy the tests from the kit**

```bash
cp "$KIT/out/tests/model/test_credit_model_assemble_lines.py" tests/model/test_credit_model_assemble_lines.py
cp "$KIT/out/tests/model/test_credit_model_assemble_cases.py" tests/model/test_credit_model_assemble_cases.py
```

- [ ] **Step 2: Write the precision test**

`tests/model/test_assemble_precision.py`:

```python
"""The assembled Model reconciles exactly past the 28 digits of Python's
default decimal context (its bridges are checked at `CONTEXT`'s 38)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers

from rbotlib.model.assemble import ModelInputs, credit_model, reconciliation_faults


def test_a_model_of_29_digit_debt_has_no_reconciliation_fault() -> None:
    big = Decimal("512345678901234567.0123456789")  # the largest the reader takes
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=big) if f.facility_id in {"tlb", "ssn29"} else f
        for f in regs.facilities
    )
    model = credit_model(ModelInputs(replace(regs, facilities=facilities)))
    assert reconciliation_faults(model) == ()
```

- [ ] **Step 3:** Run `uv run pytest tests/model --no-cov`. These tests exercise code already merged, so they pass on arrival; there is no failing step.

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `560 passed, 110 skipped` (339 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.73% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03d6-assemble-tests
git add tests/model/test_credit_model_assemble_lines.py tests/model/test_credit_model_assemble_cases.py tests/model/test_assemble_precision.py
git commit -m "model: Model line and edge-case tests (caos port)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03d5-layout-tests bash scripts/check_pr_size.sh
```

Expected: `679 changed lines (limit 800)`.

Report: `Not verified:` nothing.


---

### Task 20: House inputs, citations and the vocabulary page (PR 03E1)

**Files:**
- Create: `rbot/scripts/rbotlib/model/house_inputs.py`, `rbot/scripts/rbotlib/model/citations.py`, `docs/model/enums.md`
- Test: `tests/model/test_house_inputs.py`, `tests/model/test_enums_doc.py`, `tests/model/test_brief_interop.py`, `tests/model/test_citations.py`

**Interfaces:**
- Consumes: `reader`, `registers`, Plan 02's `rbot brief` (its `run-brief.md`).
- Produces: `rbotlib.model.house_inputs`: `Identity`, `EquityValue`, `AddbackAssessment`, `DebtLikeItem`, `BriefFields(run_id, ssim_ev_multiple, primary, tranche_ids)`, `HouseInputs(identities, equity, assessments, debt_like, brief)`; readers `identities` (`cp1.instrument_identity`), `equity_value` (`cp1.equity_value`), `check_entity_profile` (`cp1.entity_profile` currency and unit must match the period register), `assessments` (`cp1d.addback_assessment`), `debt_like_items` (`cp1d.debt_like_items`), `brief_fields` (`snapshot.run_header`, `snapshot.transaction_summary`); `effective_registers(regs, assessments)` (§6.5: CP-1D's `house_realization_status`, a `Rejected` verdict read as `UNREALIZED`); `VERDICTS`, `TREATMENTS`, `UNITS`. `rbotlib.model.citations`: `Citation`, `citation_rows(module, table)`, `Citations` (`resolve`, `cite` in MODEL.md's own `[C<n>]` numbering, `table()`). `docs/model/enums.md`: every vocabulary, checked against the code by `test_enums_doc.py`.

**Agent:** `mx-invariants`.

- [ ] **Step 1: Write the failing tests**

`tests/model/test_house_inputs.py`:

```python
"""What the house view reads besides CP-1's registers (spec §6.6)."""

from __future__ import annotations

import re
from contextlib import AbstractContextManager
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers

from rbotlib.handoff import Table
from rbotlib.model.house_inputs import (
    AddbackAssessment,
    assessments,
    brief_fields,
    check_entity_profile,
    debt_like_items,
    effective_registers,
    equity_value,
    identities,
)
from rbotlib.model.reader import ModelInputError

GAP = "—"


def _refused(match: str) -> AbstractContextManager[pytest.ExceptionInfo[ModelInputError]]:
    return pytest.raises(ModelInputError, match=re.escape(match))


def test_identities_read_ratings_as_one_text() -> None:
    columns = ["facility_id", "instrument_name", "bloomberg_id", "rating_moodys", "rating_sp"]
    columns += ["rating_fitch", "cite"]
    rows = [
        ["tlb", "Term Loan B", "BL1234567", "Ba3", "BB", GAP, "[C4]"],
        ["sun29", "4.625% notes", GAP, GAP, GAP, GAP, "[C5]"],
    ]
    found = identities({"cp1.instrument_identity": Table(columns, rows)})
    assert found["tlb"].ratings == "Ba3 / BB / —"
    assert found["tlb"].bloomberg_id == "BL1234567"
    assert (found["sun29"].ratings, found["sun29"].bloomberg_id) == (None, None)
    assert identities({}) == {}
    twice = Table(columns, [rows[0], rows[0]])
    with _refused("cp1.instrument_identity row 2: tlb written twice"):
        identities({"cp1.instrument_identity": twice})


EQUITY = ["market_cap", "share_price", "shares_outstanding", "value_date", "currency", "unit"]
EQUITY += ["cite"]


def test_equity_value_reads_one_row_at_most() -> None:
    row = ["6,316", "31.00", "203.7", "2026-10-02", "USD", "MILLIONS", "[C9]"]
    found = equity_value({"cp1.equity_value": Table(EQUITY, [row])})
    assert found is not None
    assert (found.market_cap, found.value_date, found.unit) == (
        Decimal(6316),
        "2026-10-02",
        "MILLIONS",
    )
    assert equity_value({}) is None
    with _refused("cp1.equity_value row 2: one listed equity value per run"):
        equity_value({"cp1.equity_value": Table(EQUITY, [row, row])})
    undated = [*row[:3], GAP, *row[4:]]
    with _refused("cp1.equity_value row 1 column value_date: required, found null"):
        equity_value({"cp1.equity_value": Table(EQUITY, [undated])})


def test_entity_profile_must_report_in_the_run_currency_and_unit() -> None:
    regs = example_registers()
    columns = ["entity", "role", "reporting_currency", "reporting_unit", "cite"]
    good = Table(columns, [["EGC", "Borrower", "usd", "millions", "[C1]"]])
    check_entity_profile({"cp1.entity_profile": good}, regs)
    eur = Table(columns, [["EGC", "Borrower", "EUR", "MILLIONS", "[C1]"]])
    with _refused("cp1.entity_profile row 1 column reporting_currency: EUR is not USD"):
        check_entity_profile({"cp1.entity_profile": eur}, regs)
    thousands = Table(columns, [["EGC", "Borrower", "USD", "THOUSANDS", "[C1]"]])
    with _refused("column reporting_unit: THOUSANDS is not MILLIONS"):
        check_entity_profile({"cp1.entity_profile": thousands}, regs)


ASSESSMENT = ["addback_id", "period_id", "amount", "currency", "unit", "category"]
ASSESSMENT += ["house_realization_status", "verdict", "rationale", "recurrence", "cite"]


def _assessment(addback_id: str, period_id: str, status: str, verdict: str) -> list[str]:
    return [addback_id, period_id, "1", "USD", "MILLIONS", "x", status, verdict, "r", "No", "[C2]"]


def test_effective_registers_take_cp1d_status_and_reject_as_unrealized() -> None:
    rows = [
        _assessment("restructuring", "LTM_Q2_2026", "REALIZED", "Rejected"),
        _assessment("run_rate_cost_savings", "LTM_Q2_2026", "REALIZED", "Supported"),
        _assessment("transaction_costs", "FY2025", "UNREALIZED", "Challenged"),
    ]
    found = assessments({"cp1d.addback_assessment": Table(ASSESSMENT, rows)})
    assert found[0] == AddbackAssessment(
        "restructuring", "LTM_Q2_2026", "REALIZED", "Rejected", "[C2]"
    )
    regs = effective_registers(example_registers(), found)
    status = {(b.addback_id, b.period_id): b.realization_status for b in regs.addbacks}
    assert status[("restructuring", "LTM_Q2_2026")] == "UNREALIZED"
    assert status[("run_rate_cost_savings", "LTM_Q2_2026")] == "REALIZED"
    assert status[("transaction_costs", "FY2025")] == "UNREALIZED"
    assert status[("restructuring", "FY2025")] == "REALIZED"  # not assessed: CP-1's
    bad = [_assessment("restructuring", "FY2025", "REALIZED", "Accepted")]
    with _refused("cp1d.addback_assessment row 1 column verdict: 'Accepted' is not one of"):
        assessments({"cp1d.addback_assessment": Table(ASSESSMENT, bad)})


DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]


def test_debt_like_items_must_be_in_the_run_currency_and_unit() -> None:
    regs = example_registers()
    row = [
        "Pension deficit",
        "120",
        "USD",
        "MILLIONS",
        "LTM_Q2_2026",
        "Debt-like",
        "unfunded",
        "[C3]",
    ]
    found = debt_like_items({"cp1d.debt_like_items": Table(DEBT_LIKE, [row])}, regs)
    assert (found[0].amount, found[0].treatment) == (Decimal(120), "Debt-like")
    eur = [*row[:2], "EUR", *row[3:]]
    with _refused("cp1d.debt_like_items row 1 column currency: EUR is not the run's USD"):
        debt_like_items({"cp1d.debt_like_items": Table(DEBT_LIKE, [eur])}, regs)
    units = [*row[:3], "UNITS", *row[4:]]
    with _refused("column unit: UNITS is not the run's MILLIONS"):
        debt_like_items({"cp1d.debt_like_items": Table(DEBT_LIKE, [units])}, regs)


HEADER = ["run_id", "primary", "ssim_ev_multiple_x"]


def test_brief_fields_read_the_multiple_primary_flag_and_tranches() -> None:
    tables = {
        "snapshot.run_header": Table(HEADER, [["R1", "Yes", "7.5x"]]),
        "snapshot.transaction_summary": Table(["tranche_id"], [["NEW-1"], ["NEW-2"]]),
    }
    found = brief_fields({"run_id": "R0"}, tables)
    assert (found.run_id, found.primary, found.ssim_ev_multiple) == ("R0", True, Decimal("7.5"))
    assert found.tranche_ids == frozenset({"NEW-1", "NEW-2"})
    plain = brief_fields({}, {"snapshot.run_header": Table(HEADER, [["R1", "No", GAP]])})
    assert (plain.run_id, plain.primary, plain.ssim_ev_multiple) == ("R1", False, None)
    with _refused("snapshot.run_header: needs exactly one row, found 0"):
        brief_fields({}, {})
    with _refused("snapshot.run_header row 1 column primary: 'Maybe' is not one of"):
        brief_fields({}, {"snapshot.run_header": Table(HEADER, [["R1", "Maybe", GAP]])})
```

`tests/model/test_enums_doc.py`:

```python
"""docs/model/enums.md lists exactly the vocabularies the Model reads with."""

from __future__ import annotations

import re
from pathlib import Path

from rbotlib.model import house_inputs, registers

DOC = Path(__file__).parents[2] / "docs" / "model" / "enums.md"
CLOSED = {
    "period_type": registers.PERIOD_TYPES,
    "unit": registers.PERIOD_UNITS,
    "calculation_status": registers.CALCULATION_STATUSES,
    "addback_classification": registers.ADDBACK_CLASSIFICATIONS,
    "realization_status": registers.REALIZATION_STATUSES,
    "segment_type": registers.SEGMENT_TYPES,
    "value_type": registers.KPI_VALUE_TYPES,
    "secured_status": registers.SECURED_STATUSES,
    "seniority": registers.SENIORITIES,
    "lease_classification": registers.LEASE_CLASSIFICATIONS,
    "rate_type": registers.RATE_TYPES,
    "reference_rate": registers.REFERENCE_RATES,
    "classification": registers.PF_CLASSIFICATIONS,
    "house_realization_status": registers.REALIZATION_STATUSES,
    "verdict": house_inputs.VERDICTS,
    "treatment": house_inputs.TREATMENTS,
}


def _rows() -> list[tuple[str, str, frozenset[str], str]]:
    rows = []
    for line in DOC.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0].startswith("`cp1"):
            values = frozenset(re.findall(r"`([^`]+)`", cells[2]))
            rows.append((cells[0].strip("`"), cells[1].strip("`"), values, cells[3]))
    return rows


def test_every_closed_vocabulary_is_documented_as_the_code_has_it() -> None:
    documented = {(column, values) for _, column, values, kind in _rows() if kind == "closed"}
    expected = {(column, frozenset(values)) for column, values in CLOSED.items()}
    assert expected <= documented
    assert {column for column, _ in documented} == set(CLOSED)


def test_the_open_columns_are_documented_as_open() -> None:
    open_columns = {(table, column) for table, column, _, kind in _rows() if kind == "open"}
    assert open_columns == {
        ("cp1.model_period_register", "currency"),
        ("cp1.operating_kpi_schedule", "unit"),
        ("cp1.debt_facility_register", "facility_type"),
        ("cp1.debt_facility_register", "currency"),
    }
```

`tests/model/test_brief_interop.py`:

```python
"""The run-brief.md `rbot brief` writes (Plan 02) reads into the Model's Run
Brief fields: the SSIM EV multiple, Primary and the new tranches."""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.model.house_inputs import BriefFields, brief_fields


def test_a_run_brief_from_rbot_brief_reads_into_brief_fields(tmp_path: Path) -> None:
    run = make_run(tmp_path / "pack", "20261011-czr-pending")
    (run / "handoffs").mkdir()
    shutil.copy(FIXTURES / "handoff_cp0_czr_primary.md", run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["brief", "--run", str(run), "--set", "ssim_ev_multiple=8.5"]) == 0
    brief = parse((run / "run-brief.md").read_text(encoding="utf-8"))
    fields = brief_fields(brief.front_matter, brief.tables)
    assert fields == BriefFields("20261011-czr-pending", Decimal("8.5"), True, frozenset({"NEW-1"}))
```

`tests/model/test_citations.py`:

```python
"""Module citations and MODEL.md's own numbering (`rbotlib.model.citations`)."""

from __future__ import annotations

import pytest

from rbotlib.handoff import Table
from rbotlib.model.citations import Citation, Citations, citation_rows
from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import ModelInputError

ROWS = [["C1", "10-K.txt", "p.4", "Revenue"], ["C2", "10-Q.txt", "p.9", "Total debt"]]
CITED = Table(["id", "source", "locator", "excerpt"], ROWS)


def test_markers_resolve_and_are_numbered_in_first_use_order() -> None:
    citations = Citations({"CP-1": citation_rows("CP-1", CITED)})
    second = SourceRef("[C2]", "p.9", "11,705")
    both = SourceRef("[C1] [C2]", "p.4", "x")
    assert citations.cite("CP-1", [second]) == "[C1]"
    assert citations.cite("CP-1", [both, second]) == "[C2] [C1]"
    assert citations.cite("CP-1", [SourceRef("S3", "", "1")]) == "\N{EM DASH}"
    assert citations.table().rows == [
        ["C1", "10-Q.txt", "p.9", "Total debt"],
        ["C2", "10-K.txt", "p.4", "Revenue"],
    ]
    assert citations.resolve("CP-1", both) == [
        Citation("CP-1", "C1", "10-K.txt", "p.4", "Revenue"),
        Citation("CP-1", "C2", "10-Q.txt", "p.9", "Total debt"),
    ]


def test_a_marker_without_its_citation_is_refused() -> None:
    citations = Citations({"CP-1": citation_rows("CP-1", CITED)})
    with pytest.raises(ModelInputError, match=r"CP-1 source_id \[C9\]: no citation C9"):
        citations.cite("CP-1", [SourceRef("[C9]", "", "1")])
    assert citation_rows("CP-1", None) == {}


def test_citation_rows_read_short_rows_and_absent_columns_as_empty() -> None:
    short = Table(["ID", "source", "locator"], [["C1", "10-K.txt"]])
    assert citation_rows("CP-1", short) == {"C1": Citation("CP-1", "C1", "10-K.txt", "", "")}
    unnamed = Table(["source"], [["10-K.txt"]])
    assert citation_rows("CP-1", unnamed) == {"": Citation("CP-1", "", "10-K.txt", "", "")}
    sourceless = Table(["id"], [["C2"]])
    assert citation_rows("CP-1", sourceless) == {"C2": Citation("CP-1", "C2", "", "", "")}
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_house_inputs.py --no-cov`
Expected: collection errors with `ImportError: cannot import name 'house_inputs' from 'rbotlib.model'`, `ModuleNotFoundError: No module named 'rbotlib.model.citations'`, `ModuleNotFoundError: No module named 'rbotlib.model.house_inputs'`.

- [ ] **Step 3: Write the readers, the citations and the vocabulary page**

`rbot/scripts/rbotlib/model/house_inputs.py`:

```python
"""What the house view reads besides CP-1's registers (spec §6.6).

From CP-1: `cp1.instrument_identity` (identifiers and ratings per facility),
`cp1.equity_value` (one listed equity value at most) and
`cp1.entity_profile` (its currency and unit must be the period register's).
From CP-1D, when its Handoff exists: `cp1d.addback_assessment` (the house
realization status and verdict per add-back and period) and
`cp1d.debt_like_items`. From the Run Brief: the SSIM EV multiple, the
Primary flag and the new tranches' ids. Every refusal is a
`ModelInputError` naming table, row and column.

`effective_registers` applies D19's house view to the add-backs: where CP-1D
assessed an add-back for a period, its `house_realization_status` replaces
CP-1's, and a `Rejected` verdict counts as `UNREALIZED` (spec §6.5).

Pure: no I/O.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from decimal import Decimal

from rbotlib.handoff import Table
from rbotlib.model.reader import (
    ModelInputError,
    Row,
    cite,
    date_cell,
    decimal,
    distinct,
    enum,
    optional,
    read,
    required_decimal,
    required_text,
    rows,
)
from rbotlib.model.registers import REALIZATION_STATUSES, Cp1Registers

IDENTITY = "cp1.instrument_identity"
EQUITY = "cp1.equity_value"
ENTITY = "cp1.entity_profile"
ASSESSMENT = "cp1d.addback_assessment"
DEBT_LIKE = "cp1d.debt_like_items"
RUN_HEADER = "snapshot.run_header"
TRANCHES = "snapshot.transaction_summary"
VERDICTS = frozenset({"Supported", "Challenged", "Rejected"})
TREATMENTS = frozenset({"Debt-like", "Not debt-like", "Unclear"})
UNITS = frozenset({"UNITS", "THOUSANDS", "MILLIONS"})
_YES_NO = frozenset({"Yes", "No"})


@dataclass(frozen=True, slots=True)
class Identity:
    facility_id: str
    instrument_name: str
    bloomberg_id: str | None
    ratings: str | None  # "Moody's / S&P / Fitch", a missing agency as —
    cite: str


@dataclass(frozen=True, slots=True)
class EquityValue:
    market_cap: Decimal
    value_date: str
    currency: str
    unit: str
    cite: str


@dataclass(frozen=True, slots=True)
class AddbackAssessment:
    addback_id: str
    period_id: str
    house_realization_status: str
    verdict: str
    cite: str


@dataclass(frozen=True, slots=True)
class DebtLikeItem:
    item: str
    amount: Decimal
    currency: str
    unit: str
    period_id: str
    treatment: str
    basis: str
    cite: str


@dataclass(frozen=True, slots=True)
class BriefFields:
    run_id: str
    ssim_ev_multiple: Decimal | None
    primary: bool
    tranche_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class HouseInputs:
    identities: Mapping[str, Identity]
    equity: EquityValue | None
    assessments: tuple[AddbackAssessment, ...]
    debt_like: tuple[DebtLikeItem, ...]
    brief: BriefFields


def _identity(row: Row) -> Identity:
    agencies = [optional(row, f"rating_{a}") for a in ("moodys", "sp", "fitch")]
    ratings = " / ".join(a or "\N{EM DASH}" for a in agencies) if any(agencies) else None
    return Identity(
        facility_id=required_text(row, "facility_id"),
        instrument_name=required_text(row, "instrument_name"),
        bloomberg_id=optional(row, "bloomberg_id"),
        ratings=ratings,
        cite=cite(row, "cite"),
    )


def identities(tables: Mapping[str, Table]) -> dict[str, Identity]:
    columns = frozenset({"facility_id", "instrument_name", "cite"})
    found = distinct(IDENTITY, read(tables, IDENTITY, columns, _identity), _facility_key)
    return {i.facility_id: i for i in found}


def _facility_key(identity: Identity) -> tuple[str, ...]:
    return (identity.facility_id,)


def _equity(row: Row) -> EquityValue:
    day = date_cell(row, "value_date")
    if day is None:
        raise row.refuse("value_date", "required, found null")
    return EquityValue(
        market_cap=required_decimal(row, "market_cap"),
        value_date=day.isoformat(),
        currency=enum(row, "currency", frozenset(), closed=False),
        unit=enum(row, "unit", UNITS),
        cite=cite(row, "cite"),
    )


def equity_value(tables: Mapping[str, Table]) -> EquityValue | None:
    columns = frozenset({"market_cap", "value_date", "currency", "unit", "cite"})
    found = read(tables, EQUITY, columns, _equity)
    if len(found) > 1:
        raise ModelInputError(f"{EQUITY} row 2: one listed equity value per run")
    return found[0] if found else None


def check_entity_profile(tables: Mapping[str, Table], regs: Cp1Registers) -> None:
    """Refused where an entity row reports in another currency or unit than
    the period register's."""
    columns = frozenset({"reporting_currency", "reporting_unit"})
    for row in rows(tables, ENTITY, columns):
        currency = enum(row, "reporting_currency", frozenset(), closed=False)
        if currency != regs.currency:
            raise row.refuse("reporting_currency", f"{currency} is not {regs.currency}")
        unit = enum(row, "reporting_unit", UNITS)
        if unit != regs.unit:
            raise row.refuse("reporting_unit", f"{unit} is not {regs.unit}")


def _assessment(row: Row) -> AddbackAssessment:
    return AddbackAssessment(
        addback_id=required_text(row, "addback_id"),
        period_id=required_text(row, "period_id"),
        house_realization_status=enum(row, "house_realization_status", REALIZATION_STATUSES),
        verdict=enum(row, "verdict", VERDICTS),
        cite=cite(row, "cite"),
    )


def assessments(tables: Mapping[str, Table]) -> tuple[AddbackAssessment, ...]:
    columns = frozenset({"addback_id", "period_id", "house_realization_status", "verdict", "cite"})
    found = read(tables, ASSESSMENT, columns, _assessment)
    return distinct(ASSESSMENT, found, lambda a: (a.addback_id, a.period_id))


def _debt_like(row: Row, regs: Cp1Registers) -> DebtLikeItem:
    currency = enum(row, "currency", frozenset(), closed=False)
    if currency != regs.currency:
        raise row.refuse("currency", f"{currency} is not the run's {regs.currency}")
    unit = enum(row, "unit", UNITS)
    if unit != regs.unit:
        raise row.refuse("unit", f"{unit} is not the run's {regs.unit}")
    return DebtLikeItem(
        item=required_text(row, "item"),
        amount=required_decimal(row, "amount"),
        currency=currency,
        unit=unit,
        period_id=required_text(row, "period_id"),
        treatment=enum(row, "treatment", TREATMENTS),
        basis=required_text(row, "basis"),
        cite=cite(row, "cite"),
    )


def debt_like_items(tables: Mapping[str, Table], regs: Cp1Registers) -> tuple[DebtLikeItem, ...]:
    columns = frozenset({"item", "amount", "currency", "unit", "period_id", "treatment", "cite"})
    columns |= {"basis"}
    found = read(tables, DEBT_LIKE, columns, lambda row: _debt_like(row, regs))
    return distinct(DEBT_LIKE, found, lambda d: (d.item, d.period_id))


def brief_fields(front_matter: Mapping[str, str], tables: Mapping[str, Table]) -> BriefFields:
    """The Run Brief fields the Model reads: `ssim_ev_multiple_x` and
    `primary` from `snapshot.run_header`, the tranche ids from
    `snapshot.transaction_summary`."""
    columns = frozenset({"run_id", "primary", "ssim_ev_multiple_x"})
    header = rows(tables, RUN_HEADER, columns)
    if len(header) != 1:
        raise ModelInputError(f"{RUN_HEADER}: needs exactly one row, found {len(header)}")
    row = header[0]
    tranches = rows(tables, TRANCHES, frozenset({"tranche_id"}))
    return BriefFields(
        run_id=front_matter.get("run_id") or required_text(row, "run_id"),
        ssim_ev_multiple=decimal(row, "ssim_ev_multiple_x"),
        primary=enum(row, "primary", _YES_NO) == "Yes",
        tranche_ids=frozenset(required_text(t, "tranche_id") for t in tranches),
    )


def effective_registers(regs: Cp1Registers, found: tuple[AddbackAssessment, ...]) -> Cp1Registers:
    """CP-1's add-backs with CP-1D's house realization status where CP-1D
    assessed that add-back for that period; `Rejected` counts as
    `UNREALIZED`."""
    status = {
        (a.addback_id, a.period_id): "UNREALIZED"
        if a.verdict == "Rejected"
        else a.house_realization_status
        for a in found
    }
    addbacks = tuple(
        replace(b, realization_status=status.get((b.addback_id, b.period_id), b.realization_status))
        for b in regs.addbacks
    )
    return replace(regs, addbacks=addbacks)
```

`rbot/scripts/rbotlib/model/citations.py`:

```python
"""Citations for the Model's outputs (spec §3, §6.2).

A Model cell's `SourceRef.source_id` holds the `[C<n>]` markers of the module
row it came from (CP-1's registers, CP-1D's debt-like items). `Citations`
resolves each marker through that module's `citations` table and gives
`MODEL.md` its own numbering: the first module citation used is `C1`, the
next `C2`, and so on, each row copying the module's source, locator and
excerpt. A marker the module's citations table does not have is refused:
the module's own validator refuses that Handoff, so the Model never shows a
figure whose source cannot be followed.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import ModelInputError

_MARKER = re.compile(r"\[(C\d+)\]")


@dataclass(frozen=True, slots=True)
class Citation:
    module: str
    citation_id: str
    source: str
    locator: str
    excerpt: str


def citation_rows(module: str, table: Table | None) -> dict[str, Citation]:
    """A module Handoff's citations by id; none when it has no table."""
    if table is None:
        return {}
    index = {name.casefold(): n for n, name in enumerate(table.columns)}
    found = {}
    for row in table.rows:
        cells = {name: row[n] if n < len(row) else "" for name, n in index.items()}
        found[cells.get("id", "")] = Citation(
            module,
            cells.get("id", ""),
            cells.get("source", ""),
            cells.get("locator", ""),
            cells.get("excerpt", ""),
        )
    return found


@dataclass
class Citations:
    """Module citations by module and id, and the local numbering in use."""

    modules: Mapping[str, Mapping[str, Citation]]
    used: dict[tuple[str, str], str] = field(default_factory=dict)

    def resolve(self, module: str, source: SourceRef) -> list[Citation]:
        """The module citations a source's markers name, in order."""
        found = []
        for marker in _MARKER.findall(source.source_id):
            citation = self.modules.get(module, {}).get(marker)
            if citation is None:
                raise ModelInputError(
                    f"{module} source_id {source.source_id}: no citation {marker}"
                )
            found.append(citation)
        return found

    def local(self, citation: Citation) -> str:
        key = (citation.module, citation.citation_id)
        if key not in self.used:
            self.used[key] = f"C{len(self.used) + 1}"
        return self.used[key]

    def cite(self, module: str, sources: Iterable[SourceRef]) -> str:
        """`[C<n>]` markers, in MODEL.md's numbering, for the sources; `—`
        when none names a citation."""
        ids = dict.fromkeys(
            self.local(c) for source in sources for c in self.resolve(module, source)
        )
        return " ".join(f"[{i}]" for i in ids) or "\N{EM DASH}"

    def table(self) -> Table:
        """MODEL.md's citations table, in local numbering order."""
        rows = []
        for (module, citation_id), local in self.used.items():
            c = self.modules[module][citation_id]
            rows.append([local, c.source, c.locator, c.excerpt])
        return Table(["id", "source", "locator", "excerpt"], rows)
```

`docs/model/enums.md`:

````markdown
# Model input enumerations

The values `rbot model` accepts in CP-1's and CP-1D's enumerated columns (interfaces spec §2.2), copied from caos `caos/methodology/model_inputs.py` at `5c3cd52f`. A cell names a value on case and separators (`_`, `-` and whitespace alike: `super senior` is `SUPER_SENIOR`) and reads as the spelling below. In a **closed** column any other text is refused, with the table, row and column named (`ModelInputError`, exit 1). An **open** column reads any other text in upper case. `tests/model/test_enums_doc.py` fails when this page and `rbotlib/model/registers.py` or `house_inputs.py` disagree.

| table | column | values | kind |
|---|---|---|---|
| `cp1.model_period_register` | `period_type` | `QUARTER`, `YTD`, `FY`, `LTM`, `PERIOD_END` | closed |
| `cp1.model_period_register` | `unit` | `UNITS`, `THOUSANDS`, `MILLIONS` | closed |
| `cp1.model_period_register` | `currency` | any ISO code | open |
| `cp1.model_account_register` | `calculation_status` | `VERIFIED`, `CALCULATED`, `ESTIMATED`, `PROXY`, `NOT CALCULABLE`, `PARTIAL`, `CONFLICTED`, `NOT AVAILABLE` | closed |
| `cp1.adjusted_ebitda_bridge` | `addback_classification` | `RESTRUCTURING`, `SBC`, `COST_SAVINGS`, `RUN_RATE`, `SYNERGY`, `TRANSACTION_COSTS`, `OTHER_EXPLICIT` | closed |
| `cp1.adjusted_ebitda_bridge` | `realization_status` | `REALIZED`, `UNREALIZED`, `NOT_STATED` | closed |
| `cp1.segment_revenue_schedule` | `segment_type` | `OPERATING_SEGMENT`, `CORPORATE_ELIMINATION` | closed |
| `cp1.operating_kpi_schedule` | `value_type` | `PERIOD_END`, `PERIOD_FLOW`, `RATE` | closed |
| `cp1.operating_kpi_schedule` | `unit` | any text | open |
| `cp1.debt_facility_register` | `facility_type` | `DEBT ADJUSTMENT` (the one the Model acts on) | open |
| `cp1.debt_facility_register` | `currency` | any ISO code | open |
| `cp1.debt_facility_register` | `secured_status` | `SECURED`, `UNSECURED`, `NOT_STATED` | closed |
| `cp1.debt_facility_register` | `seniority` | `SUPER_SENIOR`, `SENIOR`, `SENIOR_SUBORDINATED`, `SUBORDINATED`, `JUNIOR`, `NOT_STATED` | closed |
| `cp1.debt_facility_register` | `lease_classification` | `FINANCE_LEASE`, `OPERATING_LEASE`, `NOT_LEASE`, `NOT_STATED` | closed |
| `cp1.debt_facility_register` | `rate_type` | `FIXED`, `FLOATING`, `NOT_STATED` (null reads `NOT_STATED`) | closed |
| `cp1.debt_facility_register` | `reference_rate` | `SOFR`, `TERM_SOFR`, `EURIBOR`, `SONIA`, `NONE`, `NOT_STATED` (null reads `NOT_STATED`) | closed |
| `cp1.pro_forma_adjustment_register` | `classification` | `ACQUISITION`, `DISPOSAL`, `REFINANCING`, `SUBSEQUENT_EVENT`, `LENDER_UPDATE`, `OTHER_EXPLICIT` | closed |
| `cp1.equity_value` | `unit` | `UNITS`, `THOUSANDS`, `MILLIONS` | closed |
| `cp1d.addback_assessment` | `house_realization_status` | `REALIZED`, `UNREALIZED`, `NOT_STATED` | closed |
| `cp1d.addback_assessment` | `verdict` | `Supported`, `Challenged`, `Rejected` | closed |
| `cp1d.debt_like_items` | `treatment` | `Debt-like`, `Not debt-like`, `Unclear` | closed |

Null text in a figure or optional column is any of: an empty cell, `null`, `n/a`, `not available`, `not calculable`, `-`, `—`, `–` (case ignored).
````

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `572 passed, 110 skipped` (351 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.79% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03e1-house-inputs
git add rbot/scripts/rbotlib/model/house_inputs.py rbot/scripts/rbotlib/model/citations.py tests/model/test_house_inputs.py docs/model/enums.md tests/model/test_enums_doc.py tests/model/test_brief_interop.py tests/model/test_citations.py
git commit -m "model: CP-1D, Run Brief and citation readers; vocabulary page

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03d6-assemble-tests bash scripts/check_pr_size.sh
```

Expected: `641 changed lines (limit 800)`.

Report: `Not verified:` a CP-1D Handoff written by a model (Plan 05).


---

### Task 21: House view (PR 03E2)

**Files:**
- Create: `rbot/scripts/rbotlib/model/house.py`
- Test: `tests/model/test_house.py`

**Interfaces:**
- Consumes: `assemble`, `layout`, `debt`, `house_inputs`.
- Produces: `rbotlib.model.house`: `house_view(model, regs, inputs) -> HouseView(column, items, positions, equity, ev_basis, limitations)` on the snapshot column (PF-LTM, else the LTM): items, in order, Structuring EBITDA, SSIM EBITDA, PF interest, PF interest cover, Structuring Multiple, SSIM Multiple, EV, Adjusted debt, Adjusted leverage (`HouseItem(item, key, cell, unit, formula, components)`); positions per facility (LTM balance plus its PF rows); EV listed (`cp1.equity_value` converted to the run unit, + net debt) or SSIM multiple × SSIM EBITDA; limitations `PF_LTM_EQUALS_LTM`, `PF_INTEREST_NOT_SOURCED`, `EQUITY_CURRENCY_MISMATCH`, `EV_NOT_AVAILABLE`, `NO_LTM`. Helpers `snapshot_column`, `cell`, `ratio`, `with_pf`, `debt_like_key`, `with_debt_like_lines` (CP-1D `Debt-like` items as `debt_like:<item>` memo lines in band 8), `cumulative`, `secured`, `percent_of`. Quality-adjusted EBITDA is not computed (ruling). Property tests: Structuring − SSIM = the excluded add-backs; a Multiple × its EBITDA = total debt; adjusted debt = total debt + the debt-like items.

**Agent:** `mx-invariants` (D19 arithmetic).

- [ ] **Step 1: Write the failing tests**

`tests/model/test_house.py`:

```python
"""The house view on the PF-LTM (spec D19, §6.5), hand-checked on the caos
Example Gaming Co. registers and property-tested.

The example's PF-LTM (`PF:LTM_Q2_2026`): adjusted EBITDA with the run-rate
cost savings (40, unrealised) excluded is 4,049 + the Silverlake PF 45 =
4,094 (SSIM EBITDA); Structuring EBITDA adds the 40 back: 4,134. Total debt
is the LTM's 14,106 + the 600 add-on notes = 14,706; closing cash 1,000 - 50
= 950, so net debt is 13,756; cash interest -862 - 42 = -904, so PF interest
is 904.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

from credit_model_fixture import example_registers
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib.model._cells import CONTEXT
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.frame import Cell
from rbotlib.model.house import (
    HouseView,
    cell,
    cumulative,
    house_view,
    percent_of,
    ratio,
    secured,
    snapshot_column,
    with_debt_like_lines,
)
from rbotlib.model.house_inputs import (
    AddbackAssessment,
    BriefFields,
    DebtLikeItem,
    EquityValue,
    HouseInputs,
    effective_registers,
)
from rbotlib.model.registers import Cp1Registers

PF = "PF:LTM_Q2_2026"
LTM_PERIOD = "LTM_Q2_2026"


def _inputs(
    *,
    equity: EquityValue | None = None,
    assessed: tuple[AddbackAssessment, ...] = (),
    debt_like: tuple[DebtLikeItem, ...] = (),
    multiple: Decimal | None = Decimal("8.5"),
) -> HouseInputs:
    return HouseInputs(
        {}, equity, assessed, debt_like, BriefFields("R", multiple, False, frozenset())
    )


def _view(regs: Cp1Registers | None = None, inputs: HouseInputs | None = None) -> HouseView:
    inputs = inputs or _inputs()
    regs = effective_registers(regs or example_registers(), inputs.assessments)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    return house_view(with_debt_like_lines(model, inputs.debt_like), regs, inputs)


def _value(view: HouseView, key: str) -> Decimal:
    value = view.item(key).cell.value
    assert value is not None, key
    return value


def _div(a: Decimal, b: Decimal) -> Decimal:
    with localcontext(CONTEXT):
        return a / b


def test_the_house_items_on_the_pf_ltm() -> None:
    view = _view()
    assert view.column is not None and view.column.column_id == PF
    assert _value(view, "ssim_ebitda") == 4094
    assert _value(view, "structuring_ebitda") == 4134
    assert view.item("structuring_ebitda").components == (
        "adjusted_ebitda",
        "addback:run_rate_cost_savings",
    )
    assert _value(view, "pf_interest") == 904
    assert _value(view, "pf_interest_cover") == _div(Decimal(4094), Decimal(904))
    assert _value(view, "structuring_multiple") == _div(Decimal(14706), Decimal(4134))
    assert _value(view, "ssim_multiple") == _div(Decimal(14706), Decimal(4094))
    assert _value(view, "adjusted_debt") == 14706
    assert _value(view, "adjusted_leverage") == _div(Decimal(14706), Decimal(4094))
    assert [i.item for i in view.items] == [
        "Structuring EBITDA",
        "SSIM EBITDA",
        "PF interest",
        "PF interest cover",
        "Structuring Multiple",
        "SSIM Multiple",
        "EV",
        "Adjusted debt",
        "Adjusted leverage",
    ]


def test_ev_from_the_ssim_multiple_and_from_listed_equity() -> None:
    view = _view()
    assert view.ev_basis == "ssim_multiple"
    assert _value(view, "ev") == Decimal("8.5") * 4094
    assert view.equity.value == Decimal("8.5") * 4094 - 13756
    equity = EquityValue(Decimal(12_000_000), "2026-10-02", "USD", "THOUSANDS", "[C9]")
    listed = _view(inputs=_inputs(equity=equity))
    assert listed.ev_basis == "listed"
    assert listed.equity.value == 12000
    assert _value(listed, "ev") == 12000 + 13756
    euro = _view(inputs=_inputs(equity=replace(equity, currency="EUR")))
    assert euro.item("ev").cell.reason == "NOT_APPLICABLE"
    assert (
        "EQUITY_CURRENCY_MISMATCH",
        "equity value in EUR, the run is in USD",
    ) in euro.limitations
    none = _view(inputs=_inputs(multiple=None))
    assert none.item("ev").cell.reason == "NOT_SOURCED"
    assert none.ev_basis is None
    assert any(code == "EV_NOT_AVAILABLE" for code, _ in none.limitations)


def test_a_facility_on_the_pf_ltm_carries_its_pf_rows() -> None:
    view = _view()
    outstanding = {p.facility_id: p.outstanding.value for p in view.positions}
    assert outstanding["ssn31"] == 1000 + 600
    assert outstanding["tlb"] == 2316
    assert outstanding["disc"] == -170
    assert secured(view).value == 0 + 2316 + 2000 + 1600
    assert cumulative(view, "Senior unsecured").value == 5916 + 3600 + 3500
    share = percent_of(Cell(Decimal(1600)), view.item("ev").cell).value
    with localcontext(CONTEXT):
        assert share == Decimal(1600) / (Decimal("8.5") * 4094) * 100


def test_a_new_facility_with_only_pf_rows_starts_from_nothing() -> None:
    regs = example_registers()
    notes = next(a for a in regs.pro_forma if a.metric_id == "facility:ssn31")
    tlb = next(f for f in regs.facilities if f.facility_id == "tlb" and f.period_id == "Q2_2026")
    new = replace(tlb, facility_id="NEW-1", facility_name="New TLB", carrying_value=Decimal(0))
    regs = replace(
        regs,
        facilities=(*regs.facilities, new),
        pro_forma=(
            *regs.pro_forma,
            replace(notes, adjustment_id="new1", metric_id="facility:NEW-1"),
        ),
    )
    outstanding = {p.facility_id: p.outstanding.value for p in _view(regs).positions}
    assert outstanding["NEW-1"] == 600


def test_cp1d_statuses_move_add_backs_between_ssim_and_structuring() -> None:
    rejected = AddbackAssessment("restructuring", LTM_PERIOD, "REALIZED", "Rejected", "[C1]")
    view = _view(inputs=_inputs(assessed=(rejected,)))
    assert _value(view, "ssim_ebitda") == 4094 - 32
    assert _value(view, "structuring_ebitda") == 4134
    supported = AddbackAssessment(
        "run_rate_cost_savings", LTM_PERIOD, "REALIZED", "Supported", "[C1]"
    )
    view = _view(inputs=_inputs(assessed=(supported,)))
    # Realized in the LTM row only: earlier rows stay UNREALIZED, so the
    # add-back is still excluded on every column (caos: any row unrealised).
    assert _value(view, "ssim_ebitda") == 4094


def test_debt_like_items_add_to_adjusted_debt_and_show_as_memo_lines() -> None:
    pension = DebtLikeItem(
        "Pension deficit",
        Decimal(120),
        "USD",
        "MILLIONS",
        LTM_PERIOD,
        "Debt-like",
        "unfunded",
        "[C1]",
    )
    unclear = replace(pension, item="Guarantee", treatment="Unclear")
    inputs = _inputs(debt_like=(pension, unclear))
    view = _view(inputs=inputs)
    assert _value(view, "adjusted_debt") == 14706 + 120
    assert view.item("adjusted_debt").components == ("total_debt", "debt_like:pension_deficit")
    assert _value(view, "adjusted_leverage") == _div(Decimal(14826), Decimal(4094))
    regs = example_registers()
    model = with_debt_like_lines(
        credit_model(ModelInputs(regs, exclude_unrealised=True)), (pension, unclear)
    )
    ids = [line.line_id for line in model.lines]
    assert "debt_like:guarantee" not in ids
    line = model.lines[ids.index("debt_like:pension_deficit")]
    assert (line.kind, line.band, line.label) == (
        "MEMO",
        model.lines[ids.index("total_debt")].band,
        "Memo: debt-like, Pension deficit",
    )
    assert ids.index("debt_like:pension_deficit") > ids.index("lease_adjusted_net_debt")
    on = {c.column_id: x for c, x in zip(model.columns, line.cells, strict=True)}
    assert on[PF].value == 120 and on["LTM:LTM_Q2_2026"].value == 120
    assert on["FY:FY2025"].reason == "NOT_SOURCED"
    assert with_debt_like_lines(model, (unclear,)) is model


def test_without_pf_rows_the_snapshot_column_is_the_ltm() -> None:
    view = _view(replace(example_registers(), pro_forma=()))
    assert view.column is not None and view.column.column_id == "LTM:LTM_Q2_2026"
    assert _value(view, "pf_interest") == 862
    assert [code for code, _ in view.limitations] == ["PF_LTM_EQUALS_LTM"]
    regs = example_registers()
    no_interest = replace(
        regs, pro_forma=tuple(a for a in regs.pro_forma if a.metric_id != "cash_interest_paid")
    )
    view = _view(no_interest)
    assert _value(view, "pf_interest") == 862
    assert [code for code, _ in view.limitations] == ["PF_INTEREST_NOT_SOURCED"]


def test_no_ltm_means_no_house_view() -> None:
    regs = replace(example_registers(), periods=())
    view = _view(regs)
    assert view.column is None and view.items == () and view.positions == ()
    assert view.limitations == (("NO_LTM", "the Model has no LTM column, so no house view"),)


def test_a_denominator_at_or_below_zero_gives_no_figure() -> None:
    regs = example_registers()
    regs = replace(
        regs,
        pro_forma=tuple(
            replace(a, value=Decimal(904)) if a.metric_id == "cash_interest_paid" else a
            for a in regs.pro_forma
        ),
    )
    view = _view(regs)
    assert _value(view, "pf_interest") == -42
    assert view.item("pf_interest_cover").cell.reason == "ZERO_OR_NEGATIVE_DENOMINATOR"
    assert ratio(Cell(Decimal(1)), Cell(Decimal(0))).reason == "ZERO_OR_NEGATIVE_DENOMINATOR"
    missing = ratio(Cell(None, "NOT_STATED", note="a"), Cell(None, "NOT_SOURCED", note="b"))
    assert (missing.reason, missing.note) == ("COMPONENT_MISSING", "a; b")
    assert percent_of(Cell(Decimal(1)), Cell(None, "NOT_SOURCED")).reason == "COMPONENT_MISSING"


def test_snapshot_column_and_cell_lookups() -> None:
    model: CreditModel = credit_model(ModelInputs(example_registers(), exclude_unrealised=True))
    column = snapshot_column(model)
    assert column is not None and column.kind == "PF_LTM"
    assert cell(model, "no_such_line", column).reason == "NOT_SOURCED"


_FIGURES = st.integers(min_value=-500, max_value=500).map(Decimal)
_STATUS = st.sampled_from(("REALIZED", "UNREALIZED", "NOT_STATED"))


@st.composite
def _addbacks(draw: st.DrawFn) -> Cp1Registers:
    """The example with every add-back figure and status redrawn per add-back."""
    regs = example_registers()
    status = {b.addback_id: draw(_STATUS) for b in regs.addbacks}
    figure = {b.addback_id: draw(_FIGURES) for b in regs.addbacks}
    addbacks = tuple(
        replace(b, realization_status=status[b.addback_id], value=figure[b.addback_id])
        for b in regs.addbacks
    )
    return replace(regs, addbacks=addbacks)


@settings(max_examples=30, deadline=None)
@given(regs=_addbacks())
def test_structuring_less_ssim_is_the_excluded_add_backs(regs: Cp1Registers) -> None:
    view = _view(regs)
    column = view.column
    assert column is not None
    excluded = {b.addback_id for b in regs.addbacks if b.realization_status != "REALIZED"}
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    total = sum(
        (cell(model, f"addback:{a}", column).value or Decimal(0) for a in excluded), Decimal(0)
    )
    with localcontext(CONTEXT):
        assert _value(view, "structuring_ebitda") - _value(view, "ssim_ebitda") == total


@settings(max_examples=30, deadline=None)
@given(regs=_addbacks())
def test_a_multiple_times_its_ebitda_is_total_debt(regs: Cp1Registers) -> None:
    view = _view(regs)
    for key, ebitda in (
        ("ssim_multiple", "ssim_ebitda"),
        ("structuring_multiple", "structuring_ebitda"),
    ):
        multiple, earnings = view.item(key).cell, view.item(ebitda).cell
        if earnings.value is None or earnings.value <= 0:
            assert multiple.value is None
            continue
        assert multiple.value is not None
        with localcontext(CONTEXT):
            back = multiple.value * earnings.value
        assert abs(back - 14706) <= Decimal("1e-30")


@settings(max_examples=30, deadline=None)
@given(debt=st.lists(_FIGURES, max_size=4))
def test_adjusted_debt_is_total_debt_plus_the_debt_like_items(debt: list[Decimal]) -> None:
    items = tuple(
        DebtLikeItem(f"Item {n}", amount, "USD", "MILLIONS", LTM_PERIOD, "Debt-like", "b", "[C1]")
        for n, amount in enumerate(debt)
    )
    view = _view(inputs=_inputs(debt_like=items))
    assert _value(view, "adjusted_debt") == 14706 + sum(debt, Decimal(0))
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_house.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.house'`.

- [ ] **Step 3: Write the house view**

`rbot/scripts/rbotlib/model/house.py`:

```python
"""The house view on the PF-LTM (spec D19, §6.5): Structuring and SSIM EBITDA,
PF interest and its cover, the Structuring and SSIM Multiples, EV and each
facility's share of it, adjusted debt and adjusted leverage. Quality-adjusted
EBITDA is not computed: a `Rejected` add-back counts as unrealized (§6.5), so
it would always equal SSIM EBITDA (controller ruling, 2026-10-11).

Every figure is read on the snapshot column: the PF-LTM where the Model has
one, else the host's LTM (the first LTM column, the one the PF-LTM adds to).
The Model runs with `exclude_unrealised`, so its adjusted EBITDA is SSIM
EBITDA; Structuring EBITDA adds back every excluded add-back (an add-back
with no row for the period adds nothing). PF interest is the column's cash
interest as a positive amount. A denominator at or below zero gives no figure
(`ZERO_OR_NEGATIVE_DENOMINATOR`); a missing input gives `COMPONENT_MISSING`
noted with why each missing input is missing. EV is the listed equity value
(converted to the run's unit; another currency gives no EV) plus net debt,
else the Run Brief's SSIM EV multiple times SSIM EBITDA, else none.

A facility's outstanding on the PF-LTM is its LTM balance plus the PF rows
adjusting it; a facility with no balance at the date and no PF row is not in
the capital structure. CP-1D's debt-like items treated `Debt-like` become
`debt_like:<item>` memo lines in the debt band and add to adjusted debt.

Pure: Decimal only, no I/O; nothing is rounded.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from decimal import Decimal, localcontext
from typing import Literal

from rbotlib.model._cells import ABSENT, CONTEXT, calc, join_notes, refs
from rbotlib.model.assemble import CreditModel
from rbotlib.model.debt import PAYMENT_RANKS, SECURED_RANKS
from rbotlib.model.frame import Cell, Column, SourceRef
from rbotlib.model.house_inputs import DebtLikeItem, HouseInputs
from rbotlib.model.layout import BANDS, Line
from rbotlib.model.registers import Cp1Registers

Unit = Literal["MONEY", "MULTIPLE", "PERCENT"]
_SCALE = {"UNITS": Decimal(1), "THOUSANDS": Decimal(10) ** 3, "MILLIONS": Decimal(10) ** 6}
_FACILITY = "facility:"
_SLUG = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class HouseItem:
    item: str  # a `house_item` scale value
    key: str  # its model.json key
    cell: Cell
    unit: Unit
    formula: str
    components: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Position:
    """A facility in the capital structure on the snapshot column."""

    facility_id: str
    line: Line
    outstanding: Cell


@dataclass(frozen=True, slots=True)
class HouseView:
    column: Column | None
    items: tuple[HouseItem, ...]
    positions: tuple[Position, ...]
    equity: Cell
    ev_basis: Literal["listed", "ssim_multiple"] | None
    limitations: tuple[tuple[str, str], ...]

    def item(self, key: str) -> HouseItem:
        return next(i for i in self.items if i.key == key)


def snapshot_column(model: CreditModel) -> Column | None:
    """The PF-LTM where it exists, else the host's LTM, else none."""
    pf = next((c for c in model.columns if c.kind == "PF_LTM"), None)
    return pf or next((c for c in model.columns if c.kind == "LTM"), None)


def cell(model: CreditModel, line_id: str, column: Column) -> Cell:
    """The line's cell on the column; `NOT_SOURCED` for a line the Model has not."""
    index = model.columns.index(column)
    line = next((x for x in model.lines if x.line_id == line_id), None)
    return ABSENT if line is None else line.cells[index]


def ratio(numerator: Cell, denominator: Cell) -> Cell:
    """`numerator / denominator`, exact at the Model's precision."""
    if numerator.value is None or denominator.value is None:
        missing = (c.note for c in (numerator, denominator) if c.value is None)
        return Cell(None, "COMPONENT_MISSING", note=join_notes(*missing))
    if denominator.value <= 0:
        return Cell(None, "ZERO_OR_NEGATIVE_DENOMINATOR")
    with localcontext(CONTEXT):
        value = numerator.value / denominator.value
    sources = refs([*numerator.sources, *denominator.sources])
    return Cell(value, basis="CALCULATED", sources=sources)


def _sum(parts: Iterable[tuple[Cell, int]]) -> Cell:
    with localcontext(CONTEXT):
        return calc(parts)


def _pf_rows(model: CreditModel, regs: Cp1Registers, column: Column, metric_id: str) -> list[Cell]:
    if column.kind != "PF_LTM":
        return []
    ids = [
        a.adjustment_id
        for a in regs.pro_forma
        if a.period_id == column.period_id and a.metric_id == metric_id
    ]
    return [cell(model, f"pf:{i}", column) for i in ids]


def with_pf(
    model: CreditModel, regs: Cp1Registers, column: Column, line_id: str, metric_id: str
) -> Cell:
    """A line the PF-LTM shows unadjusted (its PF rows beneath: a facility,
    cash interest, closing cash) with those rows added; a line with no figure
    at the date (`NOT_SOURCED`) starts from zero when it has PF rows."""
    own = cell(model, line_id, column)
    rows = _pf_rows(model, regs, column, metric_id)
    if not rows:
        return own
    start = Cell(Decimal(0)) if own.reason == "NOT_SOURCED" else own
    return _sum([(start, 1), *((r, 1) for r in rows)])


def _positions(model: CreditModel, regs: Cp1Registers, column: Column) -> tuple[Position, ...]:
    found = []
    for line in model.lines:
        if not line.line_id.startswith("fac:") or line.kind != "ACCOUNT":
            continue
        facility_id = line.line_id.removeprefix("fac:")
        outstanding = with_pf(model, regs, column, line.line_id, f"{_FACILITY}{facility_id}")
        if outstanding.reason != "NOT_SOURCED":
            found.append(Position(facility_id, line, outstanding))
    return tuple(found)


def _slug(item: str) -> str:
    return _SLUG.sub("_", item.casefold()).strip("_")


def debt_like_key(item: DebtLikeItem) -> str:
    return f"debt_like:{_slug(item.item)}"


def with_debt_like_lines(model: CreditModel, items: tuple[DebtLikeItem, ...]) -> CreditModel:
    """The Model with a memo line per `Debt-like` item at the end of the debt
    band, its amount on the columns of its period."""
    counted = [i for i in items if i.treatment == "Debt-like"]
    if not counted:
        return model
    lines = list(model.lines)
    band = BANDS[7]
    at = max(n for n, line in enumerate(lines) if line.band == band) + 1
    new = []
    for item in counted:
        source = SourceRef(item.cite, "", f"{item.amount:f}")
        cells = tuple(
            Cell(item.amount, basis="REPORTED", sources=(source,))
            if c.period_id == item.period_id
            else Cell(None, "NOT_SOURCED")
            for c in model.columns
        )
        label = f"Memo: debt-like, {item.item}"
        new.append(Line(debt_like_key(item), band, label, "MEMO", "MONEY", None, None, None, cells))
    return replace(model, lines=(*lines[:at], *new, *lines[at:]))


def _structuring(model: CreditModel, column: Column, ssim: Cell) -> HouseItem:
    excluded = [x for x in model.lines if x.line_id.startswith("addback:") and x.kind == "MEMO"]
    cells = [(cell(model, x.line_id, column), x.line_id) for x in excluded]
    parts = [(c, 1) for c, _ in cells if c.reason != "NOT_SOURCED"]
    ids = tuple(i for c, i in cells if c.reason != "NOT_SOURCED")
    formula = "adjusted_ebitda + excluded (unrealized) add-backs"
    total = _sum([(ssim, 1), *parts])
    return HouseItem(
        "Structuring EBITDA",
        "structuring_ebitda",
        total,
        "MONEY",
        formula,
        ("adjusted_ebitda", *ids),
    )


def _adjusted_debt(column: Column, total_debt: Cell, inputs: HouseInputs) -> HouseItem:
    counted = [
        i
        for i in inputs.debt_like
        if i.treatment == "Debt-like" and i.period_id == column.period_id
    ]
    parts = [(Cell(i.amount, basis="REPORTED"), 1) for i in counted]
    value = _sum([(total_debt, 1), *parts])
    formula = "total_debt + CP-1D debt-like items"
    components = ("total_debt", *(debt_like_key(i) for i in counted))
    return HouseItem("Adjusted debt", "adjusted_debt", value, "MONEY", formula, components)


def _equity(
    regs: Cp1Registers, inputs: HouseInputs, net_debt: Cell, ssim: Cell
) -> tuple[Cell, Cell, Literal["listed", "ssim_multiple"] | None, list[tuple[str, str]]]:
    """EV, equity, EV basis and limitations."""
    equity = inputs.equity
    if equity is not None:
        if equity.currency != regs.currency:
            why = f"equity value in {equity.currency}, the run is in {regs.currency}"
            none = Cell(None, "NOT_APPLICABLE", note=why)
            return none, none, None, [("EQUITY_CURRENCY_MISMATCH", why)]
        with localcontext(CONTEXT):
            converted = equity.market_cap * _SCALE[equity.unit] / _SCALE[regs.unit]
        source = SourceRef(equity.cite, "", f"{equity.market_cap:f}")
        listed = Cell(converted, basis="REPORTED", sources=(source,))
        return _sum([(listed, 1), (net_debt, 1)]), listed, "listed", []
    multiple = inputs.brief.ssim_ev_multiple
    if multiple is not None and ssim.value is not None:
        with localcontext(CONTEXT):
            ev = Cell(multiple * ssim.value, basis="CALCULATED", sources=ssim.sources)
        return ev, _sum([(ev, 1), (net_debt, -1)]), "ssim_multiple", []
    why = "no listed equity value and no SSIM EV multiple (or no SSIM EBITDA)"
    none = Cell(None, "NOT_SOURCED", note=why)
    return none, none, None, [("EV_NOT_AVAILABLE", why)]


def _pf_limitations(
    model: CreditModel, regs: Cp1Registers, column: Column
) -> list[tuple[str, str]]:
    if column.kind != "PF_LTM":
        why = "no pro forma adjustments for the LTM: every PF figure is the LTM's"
        return [("PF_LTM_EQUALS_LTM", why)]
    if not _pf_rows(model, regs, column, "cash_interest_paid"):
        why = "no sourced PF cash interest: PF interest is the LTM's cash interest"
        return [("PF_INTEREST_NOT_SOURCED", why)]
    return []


def _negated(c: Cell) -> Cell:
    if c.value is None:
        return c
    return replace(c, value=c.value.copy_negate(), stated=None, note=None)


def house_view(model: CreditModel, regs: Cp1Registers, inputs: HouseInputs) -> HouseView:
    """The house items, the capital structure positions and the EV on the
    snapshot column; none of them without an LTM."""
    column = snapshot_column(model)
    if column is None:
        why = "the Model has no LTM column, so no house view"
        return HouseView(None, (), (), Cell(None, "NOT_APPLICABLE"), None, (("NO_LTM", why),))
    ssim = cell(model, "adjusted_ebitda", column)
    total_debt = cell(model, "total_debt", column)
    interest = _negated(with_pf(model, regs, column, "cash_interest", "cash_interest_paid"))
    structuring = _structuring(model, column, ssim)
    adjusted = _adjusted_debt(column, total_debt, inputs)
    ev, equity, basis, ev_limits = _equity(regs, inputs, cell(model, "net_debt", column), ssim)
    ev_formula = {
        "listed": "listed equity value + net_debt",
        "ssim_multiple": "SSIM EV multiple x SSIM EBITDA",
        None: "listed equity value + net_debt, else SSIM EV multiple x SSIM EBITDA",
    }[basis]
    items = (
        structuring,
        HouseItem(
            "SSIM EBITDA",
            "ssim_ebitda",
            ssim,
            "MONEY",
            "adjusted_ebitda, unrealized add-backs excluded",
            ("adjusted_ebitda",),
        ),
        HouseItem(
            "PF interest",
            "pf_interest",
            interest,
            "MONEY",
            "-(cash_interest + its PF rows)",
            ("cash_interest",),
        ),
        HouseItem(
            "PF interest cover",
            "pf_interest_cover",
            ratio(ssim, interest),
            "MULTIPLE",
            "SSIM EBITDA / PF interest",
            ("adjusted_ebitda", "cash_interest"),
        ),
        HouseItem(
            "Structuring Multiple",
            "structuring_multiple",
            ratio(total_debt, structuring.cell),
            "MULTIPLE",
            "total_debt / Structuring EBITDA",
            ("total_debt", *structuring.components),
        ),
        HouseItem(
            "SSIM Multiple",
            "ssim_multiple",
            ratio(total_debt, ssim),
            "MULTIPLE",
            "total_debt / SSIM EBITDA",
            ("total_debt", "adjusted_ebitda"),
        ),
        HouseItem("EV", "ev", ev, "MONEY", ev_formula, ("net_debt", "adjusted_ebitda")),
        adjusted,
        HouseItem(
            "Adjusted leverage",
            "adjusted_leverage",
            ratio(adjusted.cell, ssim),
            "MULTIPLE",
            "Adjusted debt / SSIM EBITDA",
            (*adjusted.components, "adjusted_ebitda"),
        ),
    )
    limits = (*_pf_limitations(model, regs, column), *ev_limits)
    return HouseView(column, items, _positions(model, regs, column), equity, basis, limits)


def cumulative(view: HouseView, rank: str) -> Cell:
    """The outstanding of every position ranked at or above `rank`."""
    through = PAYMENT_RANKS[: PAYMENT_RANKS.index(rank) + 1]
    return _sum((p.outstanding, 1) for p in view.positions if p.line.rank in through)


def secured(view: HouseView) -> Cell:
    return _sum((p.outstanding, 1) for p in view.positions if p.line.rank in SECURED_RANKS)


def percent_of(part: Cell, whole: Cell) -> Cell:
    """`part / whole x 100`."""
    share = ratio(part, whole)
    if share.value is None:
        return share
    with localcontext(CONTEXT):
        return replace(share, value=share.value * 100)
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `585 passed, 110 skipped` (364 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.78% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03e2-house
git add rbot/scripts/rbotlib/model/house.py tests/model/test_house.py
git commit -m "model: the house view on the PF-LTM (D19)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03e1-house-inputs bash scripts/check_pr_size.sh
```

Expected: `656 changed lines (limit 800)`.

Report: `Not verified:` PF interest from a real pro forma capitalisation (the synthetic Primary pack's PF rows reach the Model only through a CP-1 Handoff, Plan 05).


---

### Task 22: Snapshot and Model tables (PR 03E3)

**Files:**
- Create: `rbot/scripts/rbotlib/model/snapshot.py`
- Test: `tests/model/test_snapshot.py`

**Interfaces:**
- Consumes: `house`, `citations`, `layout`, `assemble`.
- Produces: `rbotlib.model.snapshot`: `Context(model, regs, view, inputs, citations)`; `build_tables(ctx) -> (tables, limitations)` giving every §3.2 table: `snapshot.capital_structure`, `snapshot.capital_structure_totals`, `snapshot.ebitda_adjustments` (Reported EBITDA, every add-back, Structuring EBITDA, each unrealized add-back negative, SSIM EBITDA), `snapshot.financial_columns` and `snapshot.financials` (§6.4 slots and mapping), `model.summary`, `model.metrics`, `model.house`, `model.maturity_wall`; `limitation_rows`; `display(value, unit)` (MODEL.md rounding: multiples 2 dp, percentages and days 1 dp, half-even); `slots`, `maturity_year` (a year-only maturity counts), `money_label`, `unit_label`, `shown_cell`, `line_of`; constants `GAP`, `SLOTS`, `FINANCIALS`.

**Agent:** `mx-invariants`.

- [ ] **Step 1: Write the failing tests**

`tests/model/test_snapshot.py`:

```python
"""The MODEL step's §3.2 tables from the Model and its house view."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff

from rbotlib.handoff import Table, parse
from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.citations import Citations, citation_rows
from rbotlib.model.house import house_view
from rbotlib.model.house_inputs import BriefFields, HouseInputs, Identity
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.snapshot import Context, build_tables, display, maturity_year, slots

GAP = "—"


@pytest.mark.parametrize(
    ("text", "year"),
    [("2028-01-26", 2028), ("2028", 2028), ("not stated", None), (None, None), ("28", None)],
)
def test_a_maturity_falls_in_its_date_or_stated_year(text: str | None, year: int | None) -> None:
    assert maturity_year(text) == year


def _context(regs: Cp1Registers | None = None, tranches: frozenset[str] = frozenset()) -> Context:
    """The registers (the example's by default) read back from a CP-1
    Handoff, so each source is a `[C<n>]` marker; their Model and house view.
    Registers without periods are used as they are (no Handoff holds them)."""
    regs = regs or example_registers()
    citations = Citations({})
    if regs.periods:
        written = parse(cp1_handoff(regs))
        regs = cp1_registers(written.tables)
        citations = Citations({"CP-1": citation_rows("CP-1", written.tables["citations"])})
    identity = Identity("tlb", "Term Loan B", "BL0001", "Ba3 / BB / —", "[C4]")
    brief = BriefFields("R", Decimal("8.5"), bool(tranches), tranches)
    inputs = HouseInputs({"tlb": identity}, None, (), (), brief)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    return Context(model, regs, house_view(model, regs, inputs), inputs, citations)


def test_the_unsecured_total_is_exact_past_28_digits() -> None:
    big = Decimal("512345678901234567.0123456789")  # the largest the reader takes
    regs = example_registers()
    facilities = tuple(
        replace(f, carrying_value=big) if f.facility_id in {"sun29", "sun32"} else f
        for f in regs.facilities
    )
    ctx = _context(replace(regs, facilities=facilities))
    totals = _by(build_tables(ctx)[0]["snapshot.capital_structure_totals"], "line")
    assert totals["Unsecured debt"]["amount"] == "1024691357802470734.0246913578"


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def _by(table: Table, key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in _rows(table)}


@pytest.mark.parametrize(
    ("value", "unit", "shown"),
    [
        (Decimal("1234.5"), "MONEY", "1234.5"),
        (Decimal("0.123456"), "PERCENT", "12.3"),
        (Decimal("0.12350"), "PERCENT", "12.4"),
        (Decimal("0.12250"), "PERCENT", "12.2"),
        (Decimal("3.5920859794"), "MULTIPLE", "3.59"),
        (Decimal("-0.001"), "MULTIPLE", "0.00"),
        (Decimal("41.25"), "SHARE", "41.2"),
        (Decimal("45.06"), "DAYS", "45.1"),
        (Decimal("0.0380"), "RATE", "3.80"),
        (None, "MONEY", GAP),
    ],
)
def test_display_rounds_ratios_half_even_and_never_amounts(
    value: Decimal | None, unit: str, shown: str
) -> None:
    assert display(value, unit) == shown


def test_snapshot_slots_and_the_no_ytd_fallback() -> None:
    ctx = _context()
    taken = {s: (c.column_id if c else None) for s, c in slots(ctx.model, ctx.view).items()}
    assert taken == {
        "FY-2": "FY:FY2023",
        "FY-1": "FY:FY2024",
        "FY": "FY:FY2025",
        "PYTD": "PYTD:H1_2025",
        "YTD": "YTD:H1_2026",
        "LTM": "PF:LTM_Q2_2026",
    }
    tables, _ = build_tables(ctx)
    rows = _by(tables["snapshot.financial_columns"], "slot")
    assert rows["LTM"] == {
        "slot": "LTM",
        "column_id": "PF:LTM_Q2_2026",
        "label": "PF-LTM",
        "period_id": "LTM_Q2_2026",
        "kind": "PF_LTM",
        "end_date": "2026-06-30",
    }
    regs = example_registers()
    years = replace(regs, periods=tuple(p for p in regs.periods if p.period_type == "FY"))
    fallback = _context(replace(years, pro_forma=()))
    rows = _by(build_tables(fallback)[0]["snapshot.financial_columns"], "slot")
    assert [rows[s]["column_id"] for s in ("FY-2", "FY-1", "FY", "PYTD", "YTD")] == [
        "FY:FY2023",
        "FY:FY2024",
        "FY:FY2025",
        GAP,
        GAP,
    ]
    assert rows["PYTD"]["label"] == "n/a"
    assert rows["LTM"]["column_id"] == "LTM:FY2025"


def test_financials_follow_the_template_mapping() -> None:
    tables, _ = build_tables(_context())
    financials = tables["snapshot.financials"]
    assert len(financials.rows) == 32
    rows = _by(financials, "line")
    assert rows["Revenue"]["line_id"] == "revenue"
    assert rows["Revenue"]["unit_label"] == "USD m"
    assert (rows["Revenue"]["fy"], rows["Revenue"]["ltm"]) == ("11519", "11654")
    assert rows["Revenue %Δ"]["fy"] == display(Decimal(11519) / Decimal(11165) - 1, "PERCENT")
    assert rows["EBITDA (SSIM basis)"]["ltm"] == "4094"
    assert rows["Cash"]["ltm"] == "950"
    assert rows["Cash Interest"]["ltm"] == "-904"
    assert rows["Senior debt"]["line_id"] == "secured_debt"
    assert rows["Total Leverage"]["unit_label"] == "x"
    assert rows["FFO"]["ltm"] == GAP  # NOT_APPLICABLE on the PF-LTM
    assert rows["FFO"]["cite"] == "calc: model.json line ffo"


def test_capital_structure_rows_join_identity_and_label_talk() -> None:
    ctx = _context(tranches=frozenset({"tlb"}))
    tables, _ = build_tables(ctx)
    rows = _by(tables["snapshot.capital_structure"], "facility_id")
    tlb = rows["tlb"]
    assert (tlb["bloomberg_id"], tlb["facility_ratings"]) == ("BL0001", "Ba3 / BB / —")
    assert tlb["spread_or_coupon"] == "+275 bp (talk)"
    assert (tlb["outstanding"], tlb["rank"], tlb["secured"]) == ("2316", "Senior secured", "Yes")
    assert tlb["structuring_multiple_x"] == display(Decimal(5916) / Decimal(4134), "MULTIPLE") + "x"
    assert rows["ssn31"]["outstanding"] == "1600"
    assert rows["sun29"]["secured"] == "No"
    assert (
        rows["sun29"]["ssim_multiple_x"]
        == display(Decimal(13016) / Decimal(4094), "MULTIPLE") + "x"
    )
    assert tlb["column_basis"] == "PF-LTM"
    assert tlb["cite"] == "[C1]"
    assert rows["ssn31"]["cite"] == "[C1] [C2]"


def test_capital_structure_totals() -> None:
    tables, _ = build_tables(_context())
    rows = _by(tables["snapshot.capital_structure_totals"], "line")
    assert list(rows) == [
        "Senior secured debt",
        "Unsecured debt",
        "Total debt",
        "Cash",
        "Equity",
        "EV",
        "PF interest",
        "PF interest cover",
    ]
    assert rows["Total debt"]["amount"] == "14706"
    assert rows["Unsecured debt"]["amount"] == str(3600 + 3500 + 1600)
    assert rows["Cash"]["structuring_multiple_x"] == GAP
    assert rows["EV"]["pct_ev_pct"] == "100.0%"
    assert rows["PF interest"]["amount"] == "904"
    cover = rows["PF interest cover"]
    assert cover["ssim_multiple_x"] == display(Decimal(4094) / Decimal(904), "MULTIPLE") + "x"
    assert (
        cover["structuring_multiple_x"] == display(Decimal(4134) / Decimal(904), "MULTIPLE") + "x"
    )


def test_ebitda_adjustments_bridge_reported_to_ssim() -> None:
    tables, _ = build_tables(_context())
    rows = _rows(tables["snapshot.ebitda_adjustments"])
    assert [(r["line"], r["kind"], r["amount"], r["realization_status"]) for r in rows] == [
        ("Reported EBITDA", "Total", "3904", GAP),
        ("Add-back: Restructuring (realised)", "Add-back", "32", "REALIZED"),
        ("Add-back: Stock-based compensation (realised)", "Add-back", "92", "REALIZED"),
        ("Add-back: Transaction costs (realised)", "Add-back", "21", "REALIZED"),
        ("Add-back: Run-rate cost savings (unrealised), excluded", "Add-back", "40", "UNREALIZED"),
        ("PF adjustment: Silverlake Resort LTM adjusted EBITDA", "Add-back", "45", GAP),
        ("Structuring EBITDA", "Total", "4134", GAP),
        (
            "Add-back: Run-rate cost savings (unrealised), excluded",
            "Unrealized add-back",
            "-40",
            "UNREALIZED",
        ),
        ("SSIM EBITDA", "Total", "4094", GAP),
    ]
    amounts = [Decimal(r["amount"]) for r in rows]
    assert sum(amounts[:6], Decimal(0)) == amounts[6]
    assert amounts[6] + amounts[7] == amounts[8]


def test_house_summary_metrics_and_maturity_wall() -> None:
    tables, limits = build_tables(_context())
    house = _by(tables["model.house"], "item")
    assert house["Structuring EBITDA"]["value"] == "4134"
    assert house["SSIM Multiple"]["unit_label"] == "x"
    assert house["EV"]["components"] == "net_debt; adjusted_ebitda"
    metrics = tables["model.metrics"]
    assert len(metrics.rows) == 19 and metrics.rows[-1][0] == "adjusted_ebitda_growth"
    summary = _by(tables["model.summary"], "line_id")
    assert {"fac:tlb", "rank:Senior secured", "addback:restructuring"} <= set(summary)
    assert (summary["cash_closing"]["ltm"], summary["cash_closing"]["pf_ltm"]) == ("1000", "950")
    wall = _rows(tables["model.maturity_wall"])
    assert [(r["fiscal_year"], r["facility_id"]) for r in wall][:3] == [
        ("2027", "sub27"),
        ("2029", "ssn29"),
        ("2029", "sun29"),
    ]
    assert "rcf" not in {r["facility_id"] for r in wall}  # nothing outstanding
    assert ("MATURITY_NOT_STATED", "finl: no maturity date") in limits


def test_no_ltm_leaves_the_house_tables_empty() -> None:
    tables, _ = build_tables(_context(replace(example_registers(), periods=())))
    for table_id in (
        "snapshot.capital_structure",
        "snapshot.capital_structure_totals",
        "snapshot.ebitda_adjustments",
        "model.house",
        "model.maturity_wall",
    ):
        assert tables[table_id].rows == [], table_id
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_snapshot.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.snapshot'`.

- [ ] **Step 3: Write the tables**

`rbot/scripts/rbotlib/model/snapshot.py`:

```python
"""The MODEL host step's tables (spec §3.2) from the Model and its house view.

Each table is an `rbotlib.handoff.Table` of display strings. A figure is shown
as served by the Model except where the Model's own figure is a ratio: a
multiple is shown to two decimals, a percentage (a fraction times 100) to one,
days to one, each rounded half-even here and only here; `model.json` keeps
every figure exact. A cell without a figure is `—`; its reason is in
`model.json`. Columns ending `_x` carry `x`, `_pct` carry `%`.

On the PF-LTM, cash interest, closing cash and a facility are shown with the
PF rows that adjust them (the Model's lines show the LTM's figure there, the
PF rows beneath).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, localcontext

from rbotlib.handoff import Table
from rbotlib.model._cells import CONTEXT, calc
from rbotlib.model.assemble import CreditModel
from rbotlib.model.citations import Citations
from rbotlib.model.debt import SECURED_RANKS
from rbotlib.model.frame import Cell, Column
from rbotlib.model.house import HouseView, cell, cumulative, percent_of, ratio, secured, with_pf
from rbotlib.model.house_inputs import HouseInputs
from rbotlib.model.layout import Line
from rbotlib.model.registers import Cp1Registers, iso_date

GAP = "\N{EM DASH}"
SLOTS = ("FY-2", "FY-1", "FY", "PYTD", "YTD", "LTM")
_SCALE_LABEL = {"UNITS": "", "THOUSANDS": " k", "MILLIONS": " m"}
_PLACES = {"PERCENT": Decimal("0.1"), "RATE": Decimal("0.01"), "MULTIPLE": Decimal("0.01")}
_PLACES |= {"DAYS": Decimal("0.1"), "SHARE": Decimal("0.1")}  # SHARE: a percentage already
_HUNDREDFOLD = frozenset({"PERCENT", "RATE"})
_UNSECURED_RANKS = ("Senior unsecured", "Subordinated", "Junior")
# The PF rows a line the PF-LTM shows unadjusted takes, by the metric they adjust.
_PF_METRIC = {"cash_interest": "cash_interest_paid", "cash_closing": "cash_and_equivalents"}
FINANCIALS = (
    ("Financials", "Revenue", "revenue"),
    ("Financials", "Revenue %Δ", "revenue_growth"),
    ("Financials", "Gross Profit", "gross_profit"),
    ("Financials", "Gross Profit %Δ", "gross_profit_growth"),
    ("Financials", "Gross Profit % margin", "metric:gross_margin"),
    ("Financials", "Reported EBITDA", "ebitda"),
    ("Financials", "EBITDA (SSIM basis)", "adjusted_ebitda"),
    ("Financials", "EBITDA (SSIM basis) %Δ", "adjusted_ebitda_growth"),
    ("Financials", "EBITDA (SSIM basis) % margin", "metric:adjusted_ebitda_margin"),
    ("Financials", "Cash Interest", "cash_interest"),
    ("Financials", "Leases", "lease_cash_not_in_ebitda"),
    ("Financials", "Cash tax", "cash_taxes"),
    ("Financials", "Other", "other_operating"),
    ("Financials", "FFO", "ffo"),
    ("Financials", "WC", "working_capital_change"),
    ("Financials", "CFO", "cfo_adjusted"),
    ("Financials", "Capex", "capex"),
    ("Financials", "FCF", "fcf"),
    ("Financials", "M&A", "acquisitions_net"),
    ("Financials", "Δ in debt", "debt_raised_net"),
    ("Financials", "Δ in equity", "equity_raised_net"),
    ("Financials", "Dividends", "dividends"),
    ("Financials", "Other investing and financing", "other_investing_financing"),
    ("Financials", "Net Δ in cash", "ncf"),
    ("Balance sheet", "Cash", "cash_closing"),
    ("Balance sheet", "Senior debt", "secured_debt"),
    ("Balance sheet", "Total debt", "total_debt"),
    ("Balance sheet", "Net debt", "net_debt"),
    ("Credit metrics", "Senior Leverage", "metric:senior_secured_leverage"),
    ("Credit metrics", "Total Leverage", "metric:total_leverage_adjusted"),
    ("Credit metrics", "Net Leverage", "metric:net_leverage_adjusted"),
    ("Credit metrics", "Interest Cover", "metric:interest_coverage_adjusted"),
)
_SUMMARY_FIXED = (
    "revenue",
    "revenue_growth",
    "gross_profit",
    "ebitda",
    "adjusted_ebitda",
    "cash_interest",
    "cash_taxes",
    "ffo",
    "cfo_adjusted",
    "capex",
    "fcf",
    "ncf",
    "cash_closing",
    "undrawn_rcf",
    "liquidity",
    "total_debt",
    "net_debt",
    "lease_adjusted_debt",
)


@dataclass(frozen=True, slots=True)
class Context:
    model: CreditModel
    regs: Cp1Registers
    view: HouseView
    inputs: HouseInputs
    citations: Citations


def display(value: Decimal | None, unit: str) -> str:
    """The figure as the tables show it (module docstring); `—` for none."""
    if value is None:
        return GAP
    with localcontext(CONTEXT):
        shown = value * 100 if unit in _HUNDREDFOLD else value
        if unit in _PLACES:
            shown = shown.quantize(_PLACES[unit], rounding=ROUND_HALF_EVEN)
    if shown.is_zero():
        shown = shown.copy_abs()
    return format(shown, "f")


def _suffixed(value: Decimal | None, unit: str, suffix: str) -> str:
    shown = display(value, unit)
    return shown if shown == GAP else f"{shown}{suffix}"


def money_label(regs: Cp1Registers) -> str:
    return f"{regs.currency}{_SCALE_LABEL.get(regs.unit, '')}"


def unit_label(line: Line, regs: Cp1Registers) -> str:
    labels = {"MONEY": money_label(regs), "PERCENT": "%", "RATE": "%", "MULTIPLE": "x"}
    labels |= {"DAYS": "days", "COUNT": "count", "KPI": line.unit_label or ""}
    return labels[line.unit]


def slots(model: CreditModel, view: HouseView) -> dict[str, Column | None]:
    """The Credit Snapshot's columns by slot (spec §6.4)."""
    fiscal = [c for c in model.columns if c.kind == "FY"]
    padded: list[Column | None] = [None, None, None, None, None, *fiscal]
    ytd = next((c for c in reversed(model.columns) if c.kind == "YTD"), None)
    pytd = next((c for c in model.columns if c.kind == "PYTD"), None)
    if ytd is None:
        pytd, ytd = padded[-5], padded[-4]
    return {
        "FY-2": padded[-3],
        "FY-1": padded[-2],
        "FY": padded[-1],
        "PYTD": pytd,
        "YTD": ytd,
        "LTM": view.column,
    }


def line_of(model: CreditModel, line_id: str) -> Line | None:
    return next((x for x in model.lines if x.line_id == line_id), None)


def shown_cell(ctx: Context, line_id: str, column: Column | None) -> Cell:
    """The line's cell on the column, PF rows added on the PF-LTM where the
    line shows the LTM's figure there."""
    if column is None:
        return Cell(None, "NOT_APPLICABLE")
    if line_id.startswith("fac:"):
        metric = f"facility:{line_id.removeprefix('fac:')}"
        return with_pf(ctx.model, ctx.regs, column, line_id, metric)
    if line_id in _PF_METRIC:
        return with_pf(ctx.model, ctx.regs, column, line_id, _PF_METRIC[line_id])
    return cell(ctx.model, line_id, column)


def financial_columns(ctx: Context) -> Table:
    rows = []
    for slot, column in slots(ctx.model, ctx.view).items():
        if column is None:
            rows.append([slot, GAP, "n/a", GAP, GAP, GAP])
            continue
        kind = "PF_LTM" if column.kind == "PF_LTM" else column.kind
        rows.append(
            [
                slot,
                column.column_id,
                column.label,
                column.period_id or GAP,
                kind,
                column.end_date or GAP,
            ]
        )
    return Table(["slot", "column_id", "label", "period_id", "kind", "end_date"], rows)


def _values(ctx: Context, line: Line, columns: Iterable[Column | None]) -> list[str]:
    return [display(shown_cell(ctx, line.line_id, c).value, line.unit) for c in columns]


def financials(ctx: Context) -> Table:
    columns = list(slots(ctx.model, ctx.view).values())
    rows = []
    for section, label, line_id in FINANCIALS:
        line = line_of(ctx.model, line_id)
        if line is None:
            rows.append(
                [section, label, line_id, GAP, *([GAP] * 6), f"calc: no Model line {line_id}"]
            )
            continue
        values = _values(ctx, line, columns)
        rows.append(
            [
                section,
                label,
                line_id,
                unit_label(line, ctx.regs),
                *values,
                f"calc: model.json line {line_id}",
            ]
        )
    names = ["section", "line", "line_id", "unit_label", "fy_2", "fy_1", "fy", "pytd", "ytd"]
    return Table([*names, "ltm", "cite"], rows)


def _host_ltm(model: CreditModel) -> Column | None:
    return next((c for c in model.columns if c.kind == "LTM"), None)


def _pf(model: CreditModel) -> Column | None:
    return next((c for c in model.columns if c.kind == "PF_LTM"), None)


def summary(ctx: Context) -> Table:
    taken = slots(ctx.model, ctx.view)
    columns = [*(taken[s] for s in SLOTS[:5]), _host_ltm(ctx.model), _pf(ctx.model)]
    wanted = [
        *_SUMMARY_FIXED[:5],
        *(x.line_id for x in ctx.model.lines if x.line_id.startswith("addback:")),
        *_SUMMARY_FIXED[5:15],
        *(x.line_id for x in ctx.model.lines if x.line_id.startswith(("rank:", "fac:"))),
        *_SUMMARY_FIXED[15:],
    ]
    rows = []
    for line_id in wanted:
        line = line_of(ctx.model, line_id)
        if line is None:
            continue
        rows.append(
            [
                line_id,
                line.label,
                line.band,
                unit_label(line, ctx.regs),
                *_values(ctx, line, columns),
            ]
        )
    names = ["line_id", "label", "band", "unit_label", "fy_2", "fy_1", "fy", "pytd", "ytd"]
    return Table([*names, "ltm", "pf_ltm"], rows)


def metrics(ctx: Context) -> Table:
    taken = slots(ctx.model, ctx.view)
    columns = [taken["FY-2"], taken["FY-1"], taken["FY"], _host_ltm(ctx.model), _pf(ctx.model)]
    rows = [
        [line.line_id, line.label, *_values(ctx, line, columns)]
        for line in ctx.model.lines
        if line.band == ctx.model.lines[-1].band
    ]
    return Table(["metric_id", "label", "fy_2", "fy_1", "fy", "ltm", "pf_ltm"], rows)


def _basis(ctx: Context) -> str:
    column = ctx.view.column
    return "PF-LTM" if column is not None and column.kind == "PF_LTM" else "LTM"


def _multiples(ctx: Context, amount: Cell) -> list[str]:
    structuring = ctx.view.item("structuring_ebitda").cell
    ssim = ctx.view.item("ssim_ebitda").cell
    return [
        _suffixed(ratio(amount, structuring).value, "MULTIPLE", "x"),
        _suffixed(ratio(amount, ssim).value, "MULTIPLE", "x"),
    ]


def _ev_share(ctx: Context, amount: Cell) -> str:
    return _suffixed(percent_of(amount, ctx.view.item("ev").cell).value, "SHARE", "%")


def capital_structure(ctx: Context) -> Table:
    rows = []
    talk = ctx.inputs.brief.tranche_ids
    for position in ctx.view.positions:
        line, identity = position.line, ctx.inputs.identities.get(position.facility_id)
        terms = line.terms
        spread = terms.spread_or_coupon if terms is not None else GAP
        if position.facility_id in talk:
            spread = f"{spread} (talk)"
        rank = line.rank or GAP
        through = cumulative(ctx.view, rank) if line.rank else Cell(None, "NOT_APPLICABLE")
        cite = ctx.citations.cite("CP-1", position.outstanding.sources)
        rows.append(
            [
                position.facility_id,
                line.label,
                (identity.bloomberg_id if identity else None) or GAP,
                (identity.ratings if identity else None) or GAP,
                spread,
                ctx.regs.currency,  # a facility in another currency is a memo line
                ctx.regs.unit,
                terms.maturity if terms is not None else GAP,
                display(position.outstanding.value, "MONEY"),
                rank,
                "Yes" if line.rank in SECURED_RANKS else "No",
                *_multiples(ctx, through),
                _ev_share(ctx, position.outstanding),
                _basis(ctx),
                cite,
            ]
        )
    columns = ["facility_id", "facility", "bloomberg_id", "facility_ratings", "spread_or_coupon"]
    columns += ["currency", "unit", "maturity_date", "outstanding", "rank", "secured"]
    columns += ["structuring_multiple_x", "ssim_multiple_x", "pct_ev_pct", "column_basis", "cite"]
    return Table(columns, rows)


def _total_row(ctx: Context, line: str, amount: Cell, basis: str, shown: str) -> list[str]:
    """A totals row; `shown` is `debt` (multiples of Structuring and SSIM
    EBITDA and the share of EV), `share` (the share of EV) or `amount`."""
    return [
        line,
        display(amount.value, "MONEY"),
        ctx.regs.currency,
        ctx.regs.unit,
        *(_multiples(ctx, amount) if shown == "debt" else [GAP, GAP]),
        _ev_share(ctx, amount) if shown in {"debt", "share"} else GAP,
        basis,
        f"calc: {basis}",
    ]


def _ranked(view: HouseView, ranks: Iterable[str]) -> Cell:
    wanted = set(ranks)
    parts = [(p.outstanding, 1) for p in view.positions if p.line.rank in wanted]
    with localcontext(CONTEXT):
        return calc(parts)


def capital_structure_totals(ctx: Context) -> Table:
    columns = ["line", "amount", "currency", "unit", "structuring_multiple_x", "ssim_multiple_x"]
    columns += ["pct_ev_pct", "basis", "cite"]
    view = ctx.view
    if view.column is None:
        return Table(columns, [])
    total = cell(ctx.model, "total_debt", view.column)
    cash = shown_cell(ctx, "cash_closing", view.column)
    interest = view.item("pf_interest").cell
    cover = [
        _suffixed(ratio(view.item(k).cell, interest).value, "MULTIPLE", "x")
        for k in ("structuring_ebitda", "ssim_ebitda")
    ]
    equity = {"listed": "listed equity value", "ssim_multiple": "EV - net_debt"}
    unsecured = _ranked(view, _UNSECURED_RANKS)
    equity_basis = equity.get(view.ev_basis or "", GAP)
    ev = view.item("ev")
    rows = [
        _total_row(ctx, "Senior secured debt", secured(view), "secured facilities", "debt"),
        _total_row(ctx, "Unsecured debt", unsecured, "unsecured facilities", "debt"),
        _total_row(ctx, "Total debt", total, "total_debt", "debt"),
        _total_row(ctx, "Cash", cash, "cash_closing with PF rows", "amount"),
        _total_row(ctx, "Equity", view.equity, equity_basis, "share"),
        _total_row(ctx, "EV", ev.cell, ev.formula, "debt"),
        _total_row(ctx, "PF interest", interest, "-(cash_interest + its PF rows)", "amount"),
        [
            "PF interest cover",
            GAP,
            ctx.regs.currency,
            ctx.regs.unit,
            *cover,
            GAP,
            "Structuring and SSIM EBITDA / PF interest",
            "calc: Structuring and SSIM EBITDA / PF interest",
        ],
    ]
    return Table(columns, rows)


def _adjustment_row(ctx: Context, label: str, kind: str, c: Cell, status: str) -> list[str]:
    cite = f"calc: {label}" if kind == "Total" else ctx.citations.cite("CP-1", c.sources)
    shown = c.value if kind != "Unrealized add-back" or c.value is None else -c.value
    unit = [ctx.regs.currency, ctx.regs.unit]
    return [label, kind, display(shown, "MONEY"), *unit, status, _basis(ctx), cite]


def ebitda_adjustments(ctx: Context) -> Table:
    """Reported EBITDA, every add-back (realized and not) and the PF rows to
    adjusted EBITDA, Structuring EBITDA, each unrealized add-back taken off
    again, SSIM EBITDA: a bridge that foots on the snapshot column (D19)."""
    column = ctx.view.column
    if column is None:
        return Table(_ADJUSTMENT_COLUMNS, [])
    band = _adjusted_band(ctx.model)
    shown = [
        (line, cell(ctx.model, line.line_id, column))
        for line in ctx.model.lines
        if line.band == band and (line.line_id.startswith("addback:") or line.kind == "PF")
    ]
    shown = [(line, c) for line, c in shown if c.reason != "NOT_SOURCED"]
    status = {"ACCOUNT": "REALIZED", "MEMO": "UNREALIZED", "PF": GAP}
    reported = cell(ctx.model, "ebitda", column)
    rows = [_adjustment_row(ctx, "Reported EBITDA", "Total", reported, GAP)]
    rows += [_adjustment_row(ctx, x.label, "Add-back", c, status[x.kind]) for x, c in shown]
    structuring = ctx.view.item("structuring_ebitda").cell
    rows.append(_adjustment_row(ctx, "Structuring EBITDA", "Total", structuring, GAP))
    rows += [
        _adjustment_row(ctx, x.label, "Unrealized add-back", c, "UNREALIZED")
        for x, c in shown
        if x.kind == "MEMO"
    ]
    ssim = ctx.view.item("ssim_ebitda").cell
    rows.append(_adjustment_row(ctx, "SSIM EBITDA", "Total", ssim, GAP))
    return Table(_ADJUSTMENT_COLUMNS, rows)


_ADJUSTMENT_COLUMNS = ["line", "kind", "amount", "currency", "unit", "realization_status"]
_ADJUSTMENT_COLUMNS += ["basis", "cite"]


def _adjusted_band(model: CreditModel) -> str:
    return next(x.band for x in model.lines if x.line_id == "adjusted_ebitda")


def house(ctx: Context) -> Table:
    column = ctx.view.column
    rows = []
    for item in ctx.view.items:
        label = money_label(ctx.regs) if item.unit == "MONEY" else "x"
        rows.append(
            [
                item.item,
                display(item.cell.value, item.unit),
                label,
                column.column_id if column else GAP,
                item.formula,
                "; ".join(item.components),
                item.cell.reason or GAP,
            ]
        )
    columns = ["item", "value", "unit_label", "column_id", "formula", "components", "reason"]
    return Table(columns, rows)


def maturity_year(text: str | None) -> int | None:
    """The calendar year a maturity falls in: a `YYYY-MM-DD` date's, or a
    year written alone (`2028`, as a debt note's final-maturity column
    gives it); None otherwise."""
    day = iso_date(text)
    if day is not None:
        return day.year
    if text is not None and len(text) == 4 and text.isdigit():
        return int(text)
    return None


def maturity_wall(ctx: Context) -> tuple[Table, list[tuple[str, str]]]:
    rows, limits = [], []
    for position in ctx.view.positions:
        terms = position.line.terms
        year = maturity_year(terms.maturity if terms is not None else None)
        if year is None:
            limits.append(("MATURITY_NOT_STATED", f"{position.facility_id}: no maturity date"))
            continue
        if position.outstanding.value in (None, Decimal(0)):
            continue
        rows.append(
            [
                str(year),
                position.facility_id,
                display(position.outstanding.value, "MONEY"),
                ctx.regs.currency,
                ctx.regs.unit,
                position.line.rank or GAP,
            ]
        )
    rows.sort(key=lambda r: (r[0], r[1]))
    columns = ["fiscal_year", "facility_id", "amount", "currency", "unit", "rank"]
    return Table(columns, rows), limits


def limitation_rows(limits: Iterable[tuple[str, str, str, str]]) -> Table:
    return Table(["code", "message", "line_id", "column_id"], [list(x) for x in limits])


def build_tables(ctx: Context) -> tuple[dict[str, Table], list[tuple[str, str]]]:
    """Every §3.2 table by id but `model.limitations`, and the limitations the
    tables found (a facility without a maturity date)."""
    wall, wall_limits = maturity_wall(ctx)
    tables = {
        "snapshot.capital_structure": capital_structure(ctx),
        "snapshot.capital_structure_totals": capital_structure_totals(ctx),
        "snapshot.ebitda_adjustments": ebitda_adjustments(ctx),
        "snapshot.financial_columns": financial_columns(ctx),
        "snapshot.financials": financials(ctx),
        "model.summary": summary(ctx),
        "model.metrics": metrics(ctx),
        "model.house": house(ctx),
        "model.maturity_wall": wall,
    }
    return tables, wall_limits
```

- [ ] **Step 4: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `608 passed, 110 skipped` (387 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.72% (floor 80%); every gate exits 0.

- [ ] **Step 5: Commit and measure the PR**

```bash
git switch -c build/03e3-snapshot
git add rbot/scripts/rbotlib/model/snapshot.py tests/model/test_snapshot.py
git commit -m "model: snapshot and Model tables (spec section 3.2)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03e2-house bash scripts/check_pr_size.sh
```

Expected: `745 changed lines (limit 800)`.

Report: `Not verified:` how the Report renders these tables (Plan 07).


---

### Task 23: `model.json`, `model.xlsx`, MODEL.md and `rbot model` (PR 03E4)

**Files:**
- Create: `rbot/scripts/rbotlib/model/output.py`, `rbot/scripts/rbotlib/model/xlsx.py`, `rbot/scripts/rbotlib/model/run.py`, `tests/model/run_cases.py`
- Modify: `rbot/scripts/rbotlib/cli.py`, `rbot/scripts/rbotlib/__init__.py`
- Test: `tests/model/test_run.py`

**Interfaces:**
- Consumes: everything above; Plan 02's `rbotlib.cli` (`add_command` convention, `--run` with `dest="run_dir"`, `<RUN>/log/rbot.log`) and its Handoff parser (escaped pipes).
- Produces: `rbot model --run <RUN>` (`rbotlib.model.run`: `run_model(run, generated_at) -> Written(qa_status, limitations)`, `run_command`, `add_command`, `read_handoff`): reads `handoffs/CP-1.md` (required), `handoffs/CP-1D.md` (optional), `run-brief.md` (required); writes `model.json` (`rbotlib.model.output.model_json`, schema `rbot-model/1`, §6.2), `model.xlsx` (`rbotlib.model.xlsx.workbook`: sheets `Columns`, the twelve band sheets, `House`, `Snapshot`, `Projection` (header and "no projection run" until Plan 13), `Passport`; values only) and `handoffs/MODEL.md` (`output.model_md`, a Handoff whose `citations` copy the module citations; a literal pipe written `\|`, amendment A8); exit 0 with the limitations printed, 1 naming the malformed input. `output`: `Limitation`, `Built`, `dumps`, `qa_status` (`Restricted` on reconciliation faults or cut sources), `sources_cut`, `SCHEMA`, `MAX_SOURCES = 8`, `MAX_COLUMNS = 64`, `MAX_LINES = 400`. `rbotlib.__version__ = "0.1.0"` (`model.json` `rbot_version`).

**Agent:** `mx-precise`.

- [ ] **Step 1: Write the failing tests**

`tests/model/run_cases.py`:

```python
"""Run folders and CP-1D Handoffs shared by the `rbot model` tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, handoff, run_brief, run_folder, table

from rbotlib.model.registers import Cp1Registers

CP1D_COLUMNS = ["addback_id", "period_id", "amount", "currency", "unit", "category"]
CP1D_COLUMNS += ["house_realization_status", "verdict", "rationale", "recurrence", "cite"]
DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]


def cp1d_handoff() -> str:
    """A CP-1D Handoff: restructuring Rejected, a 120 pension deficit Debt-like."""
    assessed = ["restructuring", "LTM_Q2_2026", "32", "USD", "MILLIONS", "Restructuring"]
    assessed += ["REALIZED", "Rejected", "recurring every year", "Yes", "[C1]"]
    pension = ["Pension deficit", "120", "USD", "MILLIONS", "LTM_Q2_2026", "Debt-like"]
    pension += ["unfunded obligation", "[C2]"]
    blocks = [
        table("cp1d.addback_assessment", CP1D_COLUMNS, [assessed]),
        table("cp1d.debt_like_items", DEBT_LIKE, [pension]),
    ]
    citations = {
        "[C1]": ("10-K.txt", "p.70", "restructuring charges recur"),
        "[C2]": ("10-K.txt", "p.95", "pension deficit of $120 million"),
    }
    return handoff("CP-1D", blocks, citations)


def _run(tmp_path: Path, regs: Cp1Registers | None = None, cp1d: str | None = None) -> Path:
    return run_folder(tmp_path, cp1_handoff(regs or example_registers()), run_brief(), cp1d)


def _model(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "model.json").read_text(encoding="utf-8"))
    return data
```

`tests/model/test_run.py`:

```python
"""`rbot model --run`: model.json and the exits (spec §6.2, §6.8)."""

from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, run_brief, run_folder
from run_cases import _model, _run

from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.model._cells import CONTEXT
from rbotlib.model.output import MAX_SOURCES


def test_rbot_model_writes_the_three_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    assert main(["model", "--run", str(run)]) == 0
    out = capsys.readouterr().out
    assert "qa_status Pass" in out and "CP1D_NOT_READ" in out
    data = _model(run)
    assert data["schema"] == "rbot-model/1"
    assert (data["currency"], data["unit"], data["exclude_unrealised"]) == ("USD", "MILLIONS", True)
    assert data["inputs"]["CP-1D"] is None and data["inputs"]["CP-2G"] is None
    assert len(data["inputs"]["CP-1"]) == 64
    assert data["snapshot_columns"]["LTM"] == "PF:LTM_Q2_2026"
    assert data["house"]["structuring_ebitda"]["value"] == "4134"
    assert data["house"]["ev"] == {
        "value": "34799.0",
        "basis": "ssim_multiple",
        "inputs": {"market_cap": None, "ssim_ev_multiple": "8.5"},
        "reason": None,
    }
    assert data["rate_deck"] is None and data["forecast"] is None
    assert data["reconciliation_faults"] == []
    assert (run / "model.xlsx").exists() and (run / "handoffs" / "MODEL.md").exists()


def test_model_json_cells_keep_figures_exact_and_name_their_sources(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["model", "--run", str(run)])
    data = _model(run)
    lines = {line["line_id"]: line for line in data["lines"]}
    revenue = {c["column_id"]: c for c in lines["revenue"]["cells"]}
    fy = revenue["FY:FY2025"]
    assert (fy["value"], fy["basis"], fy["reason"]) == ("11519", "REPORTED", None)
    assert fy["sources"] == [
        {
            "module": "CP-1",
            "citation_id": "C3",
            "source": "fixture-S3.txt",
            "locator": "10-K FY2025, Item 8 and quarterly data",
            "excerpt": "2873",  # the builder's C3 quotes the first S3 cell it wrote
        }
    ]
    assert lines["revenue"]["band"] == 2 and lines["revenue"]["unit_label"] == "USD m"
    margin = {c["column_id"]: c for c in lines["metric:gross_margin"]["cells"]}
    with localcontext(CONTEXT):
        assert Decimal(margin["FY:FY2025"]["value"]) == Decimal(6681) / Decimal(11519)
    growth = {c["column_id"]: c for c in lines["revenue_growth"]["cells"]}
    assert (growth["FY:FY2023"]["value"], growth["FY:FY2023"]["reason"]) == (None, "NOT_APPLICABLE")
    assert all(len(c["sources"]) <= MAX_SOURCES for x in data["lines"] for c in x["cells"])
    assert (
        "SOURCES_CUT: some cells name more than 8 sources; each shows its first 8"
        in data["limitations"]
    )
    tlb = lines["fac:tlb"]
    assert tlb["terms"]["spread_or_coupon"] == "+275 bp" and tlb["rank"] == "Senior secured"


def test_model_json_is_deterministic(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["model", "--run", str(run)])
    first = _model(run)
    main(["model", "--run", str(run)])
    second = _model(run)
    first.pop("generated_at"), second.pop("generated_at")
    assert first == second
    assert json.dumps(first, indent=1, ensure_ascii=False) == json.dumps(
        second, indent=1, ensure_ascii=False
    )


def test_a_malformed_input_exits_1_naming_where(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    regs = example_registers()
    text = cp1_handoff(regs).replace("| 11519 |", "| about 11.5bn |", 1)
    run = run_folder(tmp_path, text, run_brief())
    assert main(["model", "--run", str(run)]) == 1
    out = capsys.readouterr().out
    assert out.startswith("model: cp1.model_account_register row ")
    assert "column value: 'about 11.5bn' is not a figure" in out
    assert not (run / "model.json").exists()


def test_missing_or_unreadable_inputs_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    (run / "handoffs" / "CP-1.md").unlink()
    assert main(["model", "--run", str(run)]) == 1
    assert capsys.readouterr().out == "model: CP-1.md: missing; the Model needs it\n"
    (run / "handoffs" / "CP-1.md").write_text("no front matter", encoding="utf-8")
    assert main(["model", "--run", str(run)]) == 1
    assert "model: CP-1.md: missing front matter" in capsys.readouterr().out
    (run / "handoffs" / "CP-1.md").write_text(
        cp1_handoff(example_registers()).replace("[C3]", "[C99]"), encoding="utf-8"
    )
    assert main(["model", "--run", str(run)]) == 1
    assert "CP-1 source_id [C99]: no citation C99" in capsys.readouterr().out


def test_a_pipe_in_a_cited_excerpt_stays_escaped_in_model_md(tmp_path: Path) -> None:
    lines = cp1_handoff(example_registers()).splitlines()
    at = next(n for n, line in enumerate(lines) if line.startswith("| C3 |"))
    lines[at] = lines[at].removesuffix(" |") + r" \| 2,873 |"
    run = run_folder(tmp_path, "\n".join(lines), run_brief())
    assert main(["model", "--run", str(run)]) == 0
    text = (run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")
    assert r"| 2873 \| 2,873 |" in text
    excerpts = {row[1]: row[3] for row in parse(text).tables["citations"].rows}
    assert excerpts["fixture-S3.txt"] == "2873 | 2,873"
```

- [ ] **Step 2: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_run.py --no-cov`
Expected: collection errors with `ModuleNotFoundError: No module named 'rbotlib.model.output'`.

- [ ] **Step 3: Write the outputs and the command**

`rbot/scripts/rbotlib/model/output.py`:

```python
"""`model.json` (`rbot-model/1`, spec §6.2) and `handoffs/MODEL.md` (§3.2).

`model.json` keeps every figure exact (`format(value, "f")`, a null with its
reason, never zero) and each cell's sources resolved through the module's
citations (at most `MAX_SOURCES` per cell; a cell with more shows its first
`MAX_SOURCES` and the Model notes `SOURCES_CUT`). It is deterministic: the
same inputs give the same bytes except `generated_at`. `MODEL.md` is a
Handoff (front matter, the four H2 sections, the §3.2 tables, a citations
table in its own numbering) whose `qa_status` is `Restricted` when a bridge
does not close or there is no LTM, else `Pass`.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from rbotlib import __version__
from rbotlib.handoff import Table
from rbotlib.model.assemble import CreditModel
from rbotlib.model.citations import Citations
from rbotlib.model.frame import Cell, Column, SourceRef
from rbotlib.model.house import HouseView
from rbotlib.model.house_inputs import HouseInputs
from rbotlib.model.layout import BANDS, Line
from rbotlib.model.snapshot import GAP, slots

SCHEMA = "rbot-model/1"
MAX_SOURCES = 8
MAX_COLUMNS = 64
MAX_LINES = 400
RESTRICTING = frozenset({"RECONCILIATION_FAULT", "NO_LTM"})


@dataclass(frozen=True, slots=True)
class Limitation:
    code: str
    message: str
    line_id: str = GAP
    column_id: str = GAP


def _decimal(cell_value: object) -> str | None:
    return None if cell_value is None else format(cell_value, "f")


def _sources(
    module: str, sources: Sequence[SourceRef], citations: Citations
) -> list[dict[str, str | None]]:
    found: list[dict[str, str | None]] = []
    for source in sources:
        resolved = citations.resolve(module, source)
        if not resolved:
            found.append(
                {
                    "module": module,
                    "citation_id": None,
                    "source": source.source_id,
                    "locator": source.source_locator,
                    "excerpt": None,
                }
            )
        for c in resolved:
            found.append(
                {
                    "module": c.module,
                    "citation_id": c.citation_id,
                    "source": c.source,
                    "locator": c.locator,
                    "excerpt": c.excerpt,
                }
            )
    return found[:MAX_SOURCES]


def _module(line: Line) -> str:
    return "CP-1D" if line.line_id.startswith("debt_like:") else "CP-1"


def _cell(column: Column, cell: Cell, module: str, citations: Citations) -> dict[str, Any]:
    return {
        "column_id": column.column_id,
        "value": _decimal(cell.value),
        "reason": cell.reason,
        "basis": cell.basis,
        "stated": _decimal(cell.stated),
        "note": cell.note,
        "sources": _sources(module, cell.sources, citations),
    }


def _line(line: Line, model: CreditModel, unit_label: str, citations: Citations) -> dict[str, Any]:
    terms = line.terms
    return {
        "line_id": line.line_id,
        "band": BANDS.index(line.band) + 1,
        "label": line.label,
        "kind": line.kind,
        "unit": line.unit,
        "unit_label": unit_label,
        "rank": line.rank,
        "terms": None
        if terms is None
        else {
            "reference_rate": terms.reference_rate,
            "spread_or_coupon": terms.spread_or_coupon,
            "floor": terms.floor,
            "maturity": terms.maturity,
            "amortisation": terms.amortisation,
        },
        "cells": [
            _cell(column, cell, _module(line), citations)
            for column, cell in zip(model.columns, line.cells, strict=True)
        ],
    }


def sources_cut(model: CreditModel) -> list[Limitation]:
    cut = any(len(c.sources) > MAX_SOURCES for line in model.lines for c in line.cells)
    why = f"some cells name more than {MAX_SOURCES} sources; each shows its first {MAX_SOURCES}"
    return [Limitation("SOURCES_CUT", why)] if cut else []


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def _house(view: HouseView, inputs: HouseInputs, tables: Mapping[str, Table]) -> dict[str, Any]:
    column_id = view.column.column_id if view.column else None
    house: dict[str, Any] = {}
    for item in view.items:
        house[item.key] = {
            "column_id": column_id,
            "value": _decimal(item.cell.value),
            "formula": item.formula,
            "components": list(item.components),
            "reason": item.cell.reason,
        }
    ev = view.item("ev").cell if view.items else Cell(None, "NOT_APPLICABLE")
    multiple = inputs.brief.ssim_ev_multiple
    house["ev"] = {
        "value": _decimal(ev.value),
        "basis": view.ev_basis,
        "inputs": {
            "market_cap": _decimal(inputs.equity.market_cap) if inputs.equity else None,
            "ssim_ev_multiple": _decimal(multiple),
        },
        "reason": ev.reason,
    }
    house["pct_ev_by_facility"] = [
        {"facility_id": row["facility_id"], "pct": row["pct_ev_pct"].removesuffix("%")}
        for row in _rows(tables["snapshot.capital_structure"])
    ]
    return house


@dataclass(frozen=True, slots=True)
class Built:
    """Everything `model.json` is written from."""

    model: CreditModel
    view: HouseView
    inputs: HouseInputs
    tables: Mapping[str, Table]
    citations: Citations
    unit_labels: Mapping[str, str]
    shas: Mapping[str, str | None]
    limitations: tuple[Limitation, ...]
    faults: tuple[str, ...]


def model_json(built: Built, generated_at: str) -> dict[str, Any]:
    model, view, inputs, tables = built.model, built.view, built.inputs, built.tables
    citations, unit_labels = built.citations, built.unit_labels
    taken = slots(model, view)
    return {
        "schema": SCHEMA,
        "run_id": inputs.brief.run_id,
        "generated_at": generated_at,
        "rbot_version": __version__,
        "currency": model.currency,
        "unit": model.unit,
        "exclude_unrealised": True,
        "inputs": dict(built.shas),
        "columns": [
            {
                "column_id": c.column_id,
                "kind": c.kind,
                "label": c.label,
                "period_id": c.period_id,
                "fiscal_year": c.fiscal_year,
                "end_date": c.end_date,
                "days": c.days,
                "case": c.case,
            }
            for c in model.columns
        ],
        "snapshot_columns": {s: (c.column_id if c else None) for s, c in taken.items()},
        "lines": [_line(x, model, unit_labels[x.line_id], citations) for x in model.lines],
        "house": _house(view, inputs, tables),
        "capital_structure": {
            "column_id": view.column.column_id if view.column else None,
            "rows": _rows(tables["snapshot.capital_structure"]),
            "totals": _rows(tables["snapshot.capital_structure_totals"]),
        },
        "ebitda_adjustments": _rows(tables["snapshot.ebitda_adjustments"]),
        "maturity_wall": _rows(tables["model.maturity_wall"]),
        "rate_deck": None,
        "forecast": None,
        "limitations": [f"{x.code}: {x.message}" for x in built.limitations],
        "reconciliation_faults": list(built.faults),
    }


def dumps(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def _row(cells: Sequence[str]) -> str:
    """A table row; a literal pipe is written `\\|` (amendment A8)."""
    return "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"


def _markdown(table_id: str, table: Table) -> list[str]:
    for row in (table.columns, *table.rows):
        if any("\n" in cell for cell in row):
            raise ValueError(f"{table_id}: a cell holds a line break: {row}")
    lines = [f"<!-- table: {table_id} -->", "", _row(table.columns)]
    lines.append("|" + "|".join("---" for _ in table.columns) + "|")
    lines += [_row(row) for row in table.rows]
    return [*lines, ""]


def qa_status(limitations: Sequence[Limitation]) -> str:
    return "Restricted" if any(x.code in RESTRICTING for x in limitations) else "Pass"


def model_md(
    front_matter: Mapping[str, str],
    tables: Mapping[str, Table],
    citations: Citations,
    limitations: Sequence[Limitation],
    analysis: str,
) -> str:
    """MODEL.md: `front_matter` (every rules.json key but `qa_status`, which
    the limitations set), the analysis text, the tables, the limitations as
    gaps and the citations table."""
    lines = ["---", *(f"{k}: {v}" for k, v in front_matter.items())]
    lines += [f"qa_status: {qa_status(limitations)}", "---", "", "## Analysis", "", analysis, ""]
    lines += ["## Tables", ""]
    for table_id, table in tables.items():
        lines += _markdown(table_id, table)
    lines += ["## Gaps", ""]
    lines += [f"- {x.code}: {x.message}" for x in limitations] or ["- None."]
    lines += ["", "## Citations", ""]
    lines += _markdown("citations", citations.table())
    return "\n".join(lines)
```

`rbot/scripts/rbotlib/model/xlsx.py`:

```python
"""`model.xlsx`: the Model as values for the analyst's own spreadsheet (§6.7).

Written with openpyxl (locked by Plan 02, decision record 0003): values only,
no formulas, no macros, no external links. Sheets, in order: `Columns`, one
per band (`01 …` to `12 …`), `House`, `Snapshot`, `Projection` (its header
only until the projection port), `Passport`. A band sheet has the column
labels in row 1, the line label in column A and its `line_id` in column B;
a figure is the Model's exact Decimal with a number format by unit (money
`#,##0.0`, percentages `0.0%`, multiples `0.00"x"`, days `0.0`). A cell
without a figure is blank; the `Passport` sheet gives every cell's basis,
reason and sources, one row per source.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

SHEET_BANDS = (
    "01 Operating KPIs",
    "02 Revenue by business unit",
    "03 Gross profit",
    "04 Opex to EBITDA",
    "05 Adjusted EBITDA",
    "06 Adj. EBITDA to FCF",
    "07 Net cash flow and liquidity",
    "08 Debt stack by rank",
    "09 Debt roll-forward",
    "10 Interest calculation",
    "11 Working capital",
    "12 Credit metrics",
)
FORMATS = {
    "MONEY": "#,##0.0",
    "PERCENT": "0.0%",
    "RATE": "0.00%",
    "MULTIPLE": '0.00"x"',
    "DAYS": "0.0",
}
PASSPORT = "sheet cell line_id column_id basis reason source locator excerpt".split()
COLUMN_KEYS = "column_id kind label period_id fiscal_year end_date days case".split()
SNAPSHOT_KEYS = "section line line_id unit_label fy_2 fy_1 fy pytd ytd ltm".split()
HOUSE_KEYS = "item value unit_label column_id formula".split()


def _sheet(book: Workbook, title: str) -> Worksheet:
    sheet = book.create_sheet(title)
    if not isinstance(sheet, Worksheet):
        raise TypeError(f"openpyxl made {title!r} a {type(sheet).__name__}, not a worksheet")
    return sheet


def _passport(passport: Worksheet, where: list[Any], cell: Mapping[str, Any]) -> None:
    """One `Passport` row per source of the cell; one row without a source when
    it has none."""
    why = [cell["column_id"], cell["basis"], cell["reason"]]
    for source in cell["sources"] or [None]:
        found = (None, None, None)
        if source is not None:
            found = (source["source"], source["locator"], source["excerpt"])
        passport.append([*where, *why, *found])


def _band(sheet: Worksheet, model: Mapping[str, Any], band: int, passport: Worksheet) -> None:
    sheet.append(["Line", "line_id", *(c["label"] for c in model["columns"])])
    for line in (x for x in model["lines"] if x["band"] == band):
        row = sheet.max_row + 1
        sheet.cell(row, 1, line["label"])
        sheet.cell(row, 2, line["line_id"])
        for n, cell in enumerate(line["cells"], 3):
            if cell["value"] is not None:
                target = sheet.cell(row, n, Decimal(cell["value"]))
                target.number_format = FORMATS.get(line["unit"], "General")
            _passport(
                passport, [sheet.title, f"{get_column_letter(n)}{row}", line["line_id"]], cell
            )


def _table(sheet: Worksheet, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    sheet.append(list(columns))
    for row in rows:
        sheet.append([row.get(c) for c in columns])


def workbook(
    model: Mapping[str, Any],
    house: Sequence[Mapping[str, str]],
    snapshot: Sequence[Mapping[str, str]],
) -> bytes:
    """The workbook's bytes from `model.json`'s data and the `model.house` and
    `snapshot.financials` rows."""
    book = Workbook()
    book.remove(book.worksheets[0])
    columns = _sheet(book, "Columns")
    bands = [_sheet(book, name) for name in SHEET_BANDS]
    house_sheet = _sheet(book, "House")
    snapshot_sheet = _sheet(book, "Snapshot")
    projection = _sheet(book, "Projection")
    passport = _sheet(book, "Passport")
    _table(columns, COLUMN_KEYS, model["columns"])
    passport.append(PASSPORT)
    for number, sheet in enumerate(bands, 1):
        _band(sheet, model, number, passport)
    _table(house_sheet, HOUSE_KEYS, house)
    _table(snapshot_sheet, SNAPSHOT_KEYS, snapshot)
    projection.append(["case", "fiscal_year", "column_id", "note"])
    projection.append([None, None, None, "no projection run"])
    buffer = BytesIO()
    book.save(buffer)
    return buffer.getvalue()
```

`rbot/scripts/rbotlib/model/run.py`:

```python
"""`rbot model --run <RUN>`: the MODEL host step (spec §6.8).

Reads `handoffs/CP-1.md` (required), `handoffs/CP-1D.md` (optional) and
`run-brief.md` (required); writes `model.json`, `model.xlsx` and
`handoffs/MODEL.md`. This is the only I/O in `rbotlib.model`; every figure it
writes comes from the pure modules. A malformed input raises
`ModelInputError` naming the file, or the table, row and column, and then
nothing is written.
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from rbotlib.handoff import Handoff, HandoffError, Table, parse
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model, reconciliation_faults
from rbotlib.model.citations import Citations, citation_rows
from rbotlib.model.house import HouseView, house_view, with_debt_like_lines
from rbotlib.model.house_inputs import (
    HouseInputs,
    assessments,
    brief_fields,
    check_entity_profile,
    debt_like_items,
    effective_registers,
    equity_value,
    identities,
)
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.output import (
    MAX_COLUMNS,
    MAX_LINES,
    Built,
    Limitation,
    dumps,
    model_json,
    model_md,
    qa_status,
    sources_cut,
)
from rbotlib.model.reader import ModelInputError
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.snapshot import Context, build_tables, display, limitation_rows, unit_label
from rbotlib.model.xlsx import workbook


@dataclass(frozen=True, slots=True)
class Read:
    handoff: Handoff
    sha256: str


@dataclass(frozen=True, slots=True)
class Written:
    qa_status: str
    limitations: tuple[Limitation, ...]


def read_handoff(path: Path) -> Read:
    if not path.exists():
        raise ModelInputError(f"{path.name}: missing; the Model needs it")
    text = path.read_text(encoding="utf-8")
    try:
        handoff = parse(text)
    except HandoffError as exc:
        raise ModelInputError(f"{path.name}: {exc}") from exc
    return Read(handoff, hashlib.sha256(text.encode("utf-8")).hexdigest())


def _model_limitations(model: CreditModel) -> list[Limitation]:
    codes = (
        ("No projections", "NO_PROJECTIONS"),
        ("PF adjustment to a metric", "PF_NOT_APPLIED"),
        ("PF register states both", "PF_DOUBLE_COUNT"),
    )
    found = []
    for text in model.limitations:
        code = next((c for start, c in codes if text.startswith(start)), "CELL_NOTE")
        found.append(Limitation(code, text))
    for fault in reconciliation_faults(model):
        column_id, _, bridge = fault.rpartition(":")
        found.append(
            Limitation("RECONCILIATION_FAULT", f"{fault} does not close", bridge, column_id)
        )
    return found


def _analysis(view: HouseView) -> str:
    if view.column is None:
        return "Host-computed Model (`rbot model`): no LTM column, so no house view."
    ssim = display(view.item("ssim_ebitda").cell.value, "MONEY")
    structuring = display(view.item("structuring_ebitda").cell.value, "MONEY")
    multiple = display(view.item("ssim_multiple").cell.value, "MULTIPLE")
    return (
        "Host-computed Model (`rbot model`): every figure is arithmetic on CP-1's registers, "
        f"with CP-1D's house view where CP-1D ran. On the {view.column.label} column SSIM "
        f"EBITDA is {ssim}, Structuring EBITDA {structuring} and the SSIM Multiple {multiple}x. "
        "Each cell's passport is in model.json."
    )


def _inputs(
    cp1: Read, brief: Read, cp1d: Read | None
) -> tuple[HouseInputs, Cp1Registers, CreditModel]:
    """The house inputs, CP-1's registers with CP-1D's house statuses, and
    the Model run on them with `exclude_unrealised`."""
    regs = cp1_registers(cp1.handoff.tables)
    check_entity_profile(cp1.handoff.tables, regs)
    tables = cp1d.handoff.tables if cp1d else {}
    inputs = HouseInputs(
        identities(cp1.handoff.tables),
        equity_value(cp1.handoff.tables),
        assessments(tables),
        debt_like_items(tables, regs),
        brief_fields(brief.handoff.front_matter, brief.handoff.tables),
    )
    regs = effective_registers(regs, inputs.assessments)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    model = with_debt_like_lines(model, inputs.debt_like)
    if len(model.columns) > MAX_COLUMNS or len(model.lines) > MAX_LINES:
        raise ModelInputError(
            f"the Model has {len(model.columns)} columns and {len(model.lines)} lines; "
            f"model.json carries at most {MAX_COLUMNS} and {MAX_LINES}"
        )
    return inputs, regs, model


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def run_model(run: Path, generated_at: str) -> Written:
    """Build the Model for the run folder and write its three files."""
    cp1 = read_handoff(run / "handoffs" / "CP-1.md")
    brief = read_handoff(run / "run-brief.md")
    cp1d_path = run / "handoffs" / "CP-1D.md"
    cp1d = read_handoff(cp1d_path) if cp1d_path.exists() else None
    inputs, regs, model = _inputs(cp1, brief, cp1d)
    view = house_view(model, regs, inputs)
    modules = {"CP-1": citation_rows("CP-1", cp1.handoff.tables.get("citations"))}
    modules["CP-1D"] = citation_rows("CP-1D", cp1d.handoff.tables.get("citations")) if cp1d else {}
    citations = Citations(modules)
    tables, table_limits = build_tables(Context(model, regs, view, inputs, citations))
    limitations = [
        *_model_limitations(model),
        *(Limitation(code, why) for code, why in (*view.limitations, *table_limits)),
        *sources_cut(model),
    ]
    if cp1d is None:
        why = "no CP-1D Handoff: add-backs keep CP-1's realization status"
        limitations.append(Limitation("CP1D_NOT_READ", why))
    tables["model.limitations"] = limitation_rows(
        (x.code, x.message, x.line_id, x.column_id) for x in limitations
    )
    shas = {"CP-1": cp1.sha256, "CP-1D": cp1d.sha256 if cp1d else None}
    built = Built(
        model,
        view,
        inputs,
        tables,
        citations,
        unit_labels={line.line_id: unit_label(line, regs) for line in model.lines},
        shas={**shas, "CP-2G": None, "RUN_BRIEF": brief.sha256},
        limitations=tuple(limitations),
        faults=reconciliation_faults(model),
    )
    data = model_json(built, generated_at)
    front = {
        "module_id": "MODEL",
        "run_id": inputs.brief.run_id,
        "issuer_id": cp1.handoff.front_matter.get("issuer_id", "\N{EM DASH}"),
        "analysis_date": cp1.handoff.front_matter.get("analysis_date", "\N{EM DASH}"),
        "inputs": ", ".join(["CP-1", *(["CP-1D"] if cp1d else []), "RUN_BRIEF"]),
    }
    markdown = model_md(front, tables, citations, limitations, _analysis(view))
    workbook_bytes = workbook(
        data, _rows(tables["model.house"]), _rows(tables["snapshot.financials"])
    )
    (run / "model.json").write_text(dumps(data), encoding="utf-8")
    (run / "model.xlsx").write_bytes(workbook_bytes)
    (run / "handoffs" / "MODEL.md").write_text(markdown, encoding="utf-8")
    return Written(qa_status(limitations), tuple(limitations))


def run_command(args: argparse.Namespace) -> int:
    """`rbot model --run <RUN>`: 0 with the limitations printed, 1 naming the
    malformed input."""
    now = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        written = run_model(Path(args.run_dir), now)
    except ModelInputError as exc:
        print(f"model: {exc}")
        return 1
    print(f"model.json, model.xlsx and handoffs/MODEL.md written; qa_status {written.qa_status}")
    for limitation in written.limitations:
        print(f"{limitation.code}: {limitation.message}")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    m = sub.add_parser("model", help="build model.json, model.xlsx and MODEL.md for a run")
    m.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    m.set_defaults(run=run_command)
```

`rbot/scripts/rbotlib/__init__.py`:

```python
"""Deploy VI RBOT scripts: Handoff format, contracts, validator, generator, Model."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Register the command**

In `rbot/scripts/rbotlib/cli.py` (Plan 02's version), add before `from rbotlib.render import render_module`:

```python
from rbotlib.model.run import add_command as add_model_command
```

and after `    brief.add_command(sub)`:

```python
    add_model_command(sub)
```

- [ ] **Step 5: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `614 passed, 110 skipped` (393 Model tests passed on top of Plan 02's 221 passed, 110 skipped), coverage 98.56% (floor 80%); every gate exits 0. `uv run python rbot/scripts/rbot.py model --help` prints `--run RUN_DIR`.

- [ ] **Step 6: Commit and measure the PR**

```bash
git switch -c build/03e4-rbot-model
git add rbot/scripts/rbotlib/model/output.py rbot/scripts/rbotlib/model/xlsx.py rbot/scripts/rbotlib/model/run.py rbot/scripts/rbotlib/cli.py rbot/scripts/rbotlib/__init__.py tests/model/run_cases.py tests/model/test_run.py
git commit -m "model: model.json, model.xlsx, MODEL.md and rbot model

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03e3-snapshot bash scripts/check_pr_size.sh
```

Expected: `759 changed lines (limit 800)`.

Report: `Not verified:` opening `model.xlsx` in Excel on the work machine; `rbot model --projection` (Plan 13); `rbot accept` running the step (Plan 06).


---

### Task 24: Output tests, the corpus tests and amendment A10 (PR 03F1)

**Files:**
- Create: `tests/model/fixtures/cp1_czr_2026q2.md`, `tests/model/fixtures/run_brief_czr.md`
- Modify: `tests/corpus/expectations/czr-2026q2-primary.json`
- Test: `tests/model/test_run_outputs.py`, `tests/model/test_corpus_model.py`, `tests/model/test_expectation_ids.py`

**Interfaces:**
- Consumes: `rbot model`; Plan 02's `corpus_pack` fixture (`tests/conftest.py`) and registry; Plan 02's expectations file.
- Produces: `test_run_outputs.py` (MODEL.md as a Handoff whose citations resolve, a bridge fault restricting the Model, `model.xlsx` by band); the §12.5 row-03 corpus checks in `test_corpus_model.py` (`corpus` marker): `test_model_on_caos_fixture` (the ported Model on the caos worked example through `rbot model`), `test_cp1_czr_fixture_is_anchored_in_the_corpus` (every figure of the hand-written CZR CP-1 Handoff `fixtures/cp1_czr_2026q2.md` stands on the cited line of the hash-checked filing, pack `czr-2026q2-primary`), `test_model_from_cp1_handoff_fixture` (CZR LTM to 30 June 2026: revenue 11,648, EBITDA 3,255, SSIM = Structuring EBITDA 3,592, PF interest 776, cover 4.63x, SSIM Multiple 3.26x, EV 28,736.0 at 8.0x, senior secured 9,385, unsecured 2,319); amendment A10 and `test_expectation_ids.py`.

**Agent:** `mx-precise`.

- [ ] **Step 1: Write the output and corpus tests**

`tests/model/test_run_outputs.py`:

```python
"""`rbot model --run`: MODEL.md and model.xlsx (spec §3.2, §6.7)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from credit_model_fixture import example_registers
from openpyxl import load_workbook
from run_cases import _model, _run, cp1d_handoff

from rbotlib.cli import main
from rbotlib.handoff import markers, parse
from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.output import Limitation, qa_status
from rbotlib.model.run import _model_limitations
from rbotlib.model.xlsx import SHEET_BANDS
from rbotlib.rules import load_rules


def test_model_md_is_a_handoff_whose_citations_resolve(tmp_path: Path) -> None:
    run = _run(tmp_path, cp1d=cp1d_handoff())
    main(["model", "--run", str(run)])
    text = (run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")
    h = parse(text)
    rules = load_rules()
    assert set(rules.front_matter) <= set(h.front_matter)
    assert h.front_matter["module_id"] == "MODEL"
    assert h.front_matter["inputs"] == "CP-1, CP-1D, RUN_BRIEF"
    assert tuple(h.sections) == rules.sections
    assert h.duplicate_tags == [] and h.orphan_tags == []
    assert list(h.tables) == [
        "snapshot.capital_structure",
        "snapshot.capital_structure_totals",
        "snapshot.ebitda_adjustments",
        "snapshot.financial_columns",
        "snapshot.financials",
        "model.summary",
        "model.metrics",
        "model.house",
        "model.maturity_wall",
        "model.limitations",
        "citations",
    ]
    ids = {row[0] for row in h.tables["citations"].rows}
    assert markers(h.body) == ids
    assert ids == {f"C{n}" for n in range(1, len(ids) + 1)}
    house = {row[0]: row for row in h.tables["model.house"].rows}
    assert house["SSIM EBITDA"][1] == str(4094 - 32)  # CP-1D rejects restructuring
    assert house["Adjusted debt"][1] == str(14706 + 120)
    codes = [row[0] for row in h.tables["model.limitations"].rows]
    assert "CP1D_NOT_READ" not in codes and "NO_PROJECTIONS" in codes
    data = _model(run)
    lines = {line["line_id"]: line for line in data["lines"]}
    pension = {c["column_id"]: c for c in lines["debt_like:pension_deficit"]["cells"]}
    assert pension["PF:LTM_Q2_2026"]["sources"][0]["module"] == "CP-1D"
    assert pension["PF:LTM_Q2_2026"]["sources"][0]["excerpt"] == "pension deficit of $120 million"


def test_a_bridge_that_does_not_close_restricts_the_model() -> None:
    model = credit_model(ModelInputs(example_registers(), exclude_unrealised=True))
    index = [c.column_id for c in model.columns].index("FY:FY2024")
    lines = tuple(
        replace(
            x,
            cells=tuple(
                replace(c, value=Decimal(1)) if n == index else c for n, c in enumerate(x.cells)
            ),
        )
        if x.line_id == "ebit"
        else x
        for x in model.lines
    )
    found = _model_limitations(replace(model, lines=lines))
    fault = next(x for x in found if x.code == "RECONCILIATION_FAULT")
    assert fault == Limitation(
        "RECONCILIATION_FAULT", "FY:FY2024:ebitda does not close", "ebitda", "FY:FY2024"
    )
    assert qa_status(found) == "Restricted"
    assert qa_status([Limitation("NO_LTM", "x")]) == "Restricted"
    assert qa_status([Limitation("PF_LTM_EQUALS_LTM", "x")]) == "Pass"


def test_model_xlsx_holds_the_values_by_band(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["model", "--run", str(run)])
    book = load_workbook(BytesIO((run / "model.xlsx").read_bytes()))
    assert book.sheetnames == [
        "Columns",
        *SHEET_BANDS,
        "House",
        "Snapshot",
        "Projection",
        "Passport",
    ]
    revenue_band = book["02 Revenue by business unit"]
    header = [c.value for c in revenue_band[1]]
    assert header[:2] == ["Line", "line_id"] and "FY25" in header
    row = next(r for r in revenue_band.iter_rows(min_row=2) if r[1].value == "revenue")
    cell = row[header.index("FY25")]
    assert (cell.value, cell.number_format) == (11519, "#,##0.0")
    metrics = book["12 Credit metrics"]
    multiple = next(
        r for r in metrics.iter_rows(min_row=2) if r[1].value == "metric:total_leverage_adjusted"
    )
    assert multiple[header.index("FY25")].number_format == '0.00"x"'
    passport = book["Passport"]
    assert [c.value for c in passport[1]] == [
        "sheet",
        "cell",
        "line_id",
        "column_id",
        "basis",
        "reason",
        "source",
        "locator",
        "excerpt",
    ]
    assert passport.max_row > 100
    assert all(
        not isinstance(c.value, str) or not c.value.startswith("=")
        for r in revenue_band.iter_rows()
        for c in r
    )
```

`tests/model/fixtures/cp1_czr_2026q2.md`:

````markdown
---
module_id: CP-1
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Pass
inputs: CP-0
---

## Analysis

Hand-written CP-1 fixture for the Model's corpus test (Plan 03): Caesars Entertainment, Inc. FY2025, H1 2025 and H1 2026 from the 10-K, 10-Q and Q2 2026 earnings release of the caos-qualification pack `czr-2026q2-full-credit-assessment`. Direct operating costs (casino, food and beverage, hotel, other) are cogs; general and administrative, corporate, impairment, depreciation and amortization and transaction costs are opex_including_da. Cash interest is cash interest paid for debt (not the GLPI and VICI financing-obligation rent). No pro forma adjustments: the pack states none [C1].

## Tables

<!-- table: cp1.model_period_register -->

| period_id | fiscal_year | fiscal_quarter | period_type | start_date | end_date | day_count | currency | unit | component_period_ids |
|---|---|---|---|---|---|---|---|---|---|
| FY2025 | FY2025 | — | FY | 2025-01-01 | 2025-12-31 | 365 | USD | MILLIONS | — |
| H1_2025 | FY2025 | Q2 | YTD | 2025-01-01 | 2025-06-30 | 181 | USD | MILLIONS | — |
| H1_2026 | FY2026 | Q2 | YTD | 2026-01-01 | 2026-06-30 | 181 | USD | MILLIONS | — |
| LTM_Q2_2026 | FY2026 | Q2 | LTM | 2025-07-01 | 2026-06-30 | 365 | USD | MILLIONS | — |

<!-- table: cp1.model_account_register -->

| metric_id | period_id | value | calculation_status | source_id | source_locator |
|---|---|---|---|---|---|
| revenue | H1_2026 | 5863 | VERIFIED | [C1] | Statements of Operations, six months ended June 30 |
| cogs | H1_2026 | -2921 | CALCULATED | [C2] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | H1_2026 | -1929 | CALCULATED | [C2] | total operating expenses less cogs |
| depreciation_amortization | H1_2026 | -702 | VERIFIED | [C3] | Statements of Operations, six months ended June 30 |
| adjusted_ebitda | H1_2026 | 1807 | VERIFIED | [C4] | Adjusted EBITDA reconciliation, six months ended June 30 |
| cash_interest_paid | H1_2026 | -368 | VERIFIED | [C5] | Supplemental cash flow information, six months ended June 30 |
| capex_and_intangible_investment | H1_2026 | -335 | VERIFIED | [C6] | Statements of Cash Flows, six months ended June 30 |
| cfo_ncfo | H1_2026 | 675 | VERIFIED | [C7] | Statements of Cash Flows, six months ended June 30 |
| revenue | H1_2025 | 5701 | VERIFIED | [C1] | Statements of Operations, six months ended June 30 |
| cogs | H1_2025 | -2804 | CALCULATED | [C2] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | H1_2025 | -1883 | CALCULATED | [C2] | total operating expenses less cogs |
| depreciation_amortization | H1_2025 | -721 | VERIFIED | [C3] | Statements of Operations, six months ended June 30 |
| adjusted_ebitda | H1_2025 | 1839 | VERIFIED | [C4] | Adjusted EBITDA reconciliation, six months ended June 30 |
| cash_interest_paid | H1_2025 | -405 | VERIFIED | [C5] | Supplemental cash flow information, six months ended June 30 |
| capex_and_intangible_investment | H1_2025 | -453 | VERIFIED | [C6] | Statements of Cash Flows, six months ended June 30 |
| cfo_ncfo | H1_2025 | 680 | VERIFIED | [C7] | Statements of Cash Flows, six months ended June 30 |
| cash_and_equivalents | H1_2026 | 965 | VERIFIED | [C8] | Balance Sheets, June 30, 2026 and December 31, 2025 |
| total_debt | H1_2026 | 11705 | VERIFIED | [C9] | Note 6. Long-Term Debt, book value |
| revenue | FY2025 | 11486 | VERIFIED | [C10] | Consolidated Statements of Operations, 2025 |
| cogs | FY2025 | -5743 | CALCULATED | [C11] | casino, food and beverage, hotel and other operating expenses |
| opex_including_da | FY2025 | -3885 | CALCULATED | [C11] | total operating expenses less cogs |
| depreciation_amortization | FY2025 | -1417 | VERIFIED | [C12] | Consolidated Statements of Operations, 2025 |
| adjusted_ebitda | FY2025 | 3624 | VERIFIED | [C13] | Adjusted EBITDA reconciliation, 2025 |
| cash_interest_paid | FY2025 | -813 | VERIFIED | [C14] | Supplemental cash flow information, 2025 |
| capex_and_intangible_investment | FY2025 | -805 | VERIFIED | [C15] | Consolidated Statements of Cash Flows, 2025 |
| cfo_ncfo | FY2025 | 1302 | VERIFIED | [C16] | Consolidated Statements of Cash Flows, 2025 |
| cash_and_equivalents | FY2025 | 887 | VERIFIED | [C8] | Balance Sheets, June 30, 2026 and December 31, 2025 |
| total_debt | FY2025 | 11792 | VERIFIED | [C9] | Note 6. Long-Term Debt, book value |

<!-- table: cp1.adjusted_ebitda_bridge -->

| addback_id | addback_label | addback_classification | realization_status | display_priority | period_id | value | source_id | source_locator |
|---|---|---|---|---|---|---|---|---|
| impairment | Impairment charges | OTHER_EXPLICIT | REALIZED | 1 | FY2025 | 182 | [C21] | Adjusted EBITDA reconciliation, 2025 |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | FY2025 | 72 | [C18] | Adjusted EBITDA reconciliation, 2025 |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | H1_2025 | 54 | [C17] | Adjusted EBITDA reconciliation, six months ended June 30 |
| transaction_costs_other | Transaction costs and other, net | TRANSACTION_COSTS | REALIZED | 2 | H1_2026 | 45 | [C17] | Adjusted EBITDA reconciliation, six months ended June 30 |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | FY2025 | 95 | [C20] | Adjusted EBITDA reconciliation, 2025 |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | H1_2025 | 50 | [C19] | Adjusted EBITDA reconciliation, six months ended June 30 |
| stock_based_compensation | Stock-based compensation expense | SBC | REALIZED | 3 | H1_2026 | 47 | [C19] | Adjusted EBITDA reconciliation, six months ended June 30 |

<!-- table: cp1.debt_facility_register -->

| facility_id | facility_name | period_id | facility_type | currency | carrying_value | drawn_amount | commitment | secured_status | seniority | margin_or_coupon | maturity_date | lease_classification | rate_type | reference_rate | spread_bps | floor_bps | fixed_rate | annual_amortisation | source_id | source_locator |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cei_rcf | CEI Revolving Credit Facility | H1_2026 | Revolving credit facility | USD | 120 | 120 | — | SECURED | SENIOR | variable | 2028 | NOT_LEASE | FLOATING | — | — | — | — | — | [C22] | Note 6. Long-Term Debt, book value |
| cei_rcf | CEI Revolving Credit Facility | FY2025 | Revolving credit facility | USD | 160 | 160 | — | SECURED | SENIOR | variable | 2028 | NOT_LEASE | FLOATING | — | — | — | — | — | [C22] | Note 6. Long-Term Debt, book value |
| cei_tla | CEI Term Loan A | H1_2026 | Term loan | USD | 618 | — | — | SECURED | SENIOR | variable | 2028 | NOT_LEASE | FLOATING | — | — | — | — | — | [C23] | Note 6. Long-Term Debt, book value |
| cei_tla | CEI Term Loan A | FY2025 | Term loan | USD | 636 | — | — | SECURED | SENIOR | variable | 2028 | NOT_LEASE | FLOATING | — | — | — | — | — | [C23] | Note 6. Long-Term Debt, book value |
| cva_ddtl | CVA Delayed Draw Term Loan | H1_2026 | Term loan | USD | 372 | — | — | SECURED | SENIOR | variable | 2029 | NOT_LEASE | FLOATING | — | — | — | — | — | [C24] | Note 6. Long-Term Debt, book value |
| cva_ddtl | CVA Delayed Draw Term Loan | FY2025 | Term loan | USD | 381 | — | — | SECURED | SENIOR | variable | 2029 | NOT_LEASE | FLOATING | — | — | — | — | — | [C24] | Note 6. Long-Term Debt, book value |
| cei_tlb | CEI Term Loan B | H1_2026 | Term loan | USD | 1993 | — | — | SECURED | SENIOR | variable | 2030 | NOT_LEASE | FLOATING | — | — | — | — | — | [C25] | Note 6. Long-Term Debt, book value |
| cei_tlb | CEI Term Loan B | FY2025 | Term loan | USD | 2002 | — | — | SECURED | SENIOR | variable | 2030 | NOT_LEASE | FLOATING | — | — | — | — | — | [C25] | Note 6. Long-Term Debt, book value |
| cei_tlb1 | CEI Term Loan B-1 | H1_2026 | Term loan | USD | 2808 | — | — | SECURED | SENIOR | variable | 2031 | NOT_LEASE | FLOATING | — | — | — | — | — | [C26] | Note 6. Long-Term Debt, book value |
| cei_tlb1 | CEI Term Loan B-1 | FY2025 | Term loan | USD | 2820 | — | — | SECURED | SENIOR | variable | 2031 | NOT_LEASE | FLOATING | — | — | — | — | — | [C26] | Note 6. Long-Term Debt, book value |
| cei_ssn30 | CEI Senior Secured Notes due 2030 | H1_2026 | Notes | USD | 1987 | — | — | SECURED | SENIOR | 7.00% | 2030 | NOT_LEASE | FIXED | — | — | — | 7.00 | — | [C27] | Note 6. Long-Term Debt, book value |
| cei_ssn30 | CEI Senior Secured Notes due 2030 | FY2025 | Notes | USD | 1986 | — | — | SECURED | SENIOR | 7.00% | 2030 | NOT_LEASE | FIXED | — | — | — | 7.00 | — | [C27] | Note 6. Long-Term Debt, book value |
| cei_ssn32 | CEI Senior Secured Notes due 2032 | H1_2026 | Notes | USD | 1487 | — | — | SECURED | SENIOR | 6.50% | 2032 | NOT_LEASE | FIXED | — | — | — | 6.50 | — | [C28] | Note 6. Long-Term Debt, book value |
| cei_ssn32 | CEI Senior Secured Notes due 2032 | FY2025 | Notes | USD | 1486 | — | — | SECURED | SENIOR | 6.50% | 2032 | NOT_LEASE | FIXED | — | — | — | 6.50 | — | [C28] | Note 6. Long-Term Debt, book value |
| cei_sn29 | CEI Senior Notes due 2029 | H1_2026 | Notes | USD | 1193 | — | — | UNSECURED | SENIOR | 4.625% | 2029 | NOT_LEASE | FIXED | — | — | — | 4.625 | — | [C29] | Note 6. Long-Term Debt, book value |
| cei_sn29 | CEI Senior Notes due 2029 | FY2025 | Notes | USD | 1192 | — | — | UNSECURED | SENIOR | 4.625% | 2029 | NOT_LEASE | FIXED | — | — | — | 4.625 | — | [C29] | Note 6. Long-Term Debt, book value |
| cei_sn32 | CEI Senior Notes due 2032 | H1_2026 | Notes | USD | 1088 | — | — | UNSECURED | SENIOR | 6.00% | 2032 | NOT_LEASE | FIXED | — | — | — | 6.00 | — | [C30] | Note 6. Long-Term Debt, book value |
| cei_sn32 | CEI Senior Notes due 2032 | FY2025 | Notes | USD | 1087 | — | — | UNSECURED | SENIOR | 6.00% | 2032 | NOT_LEASE | FIXED | — | — | — | 6.00 | — | [C30] | Note 6. Long-Term Debt, book value |
| sid_bonds | Special Improvement District Bonds | H1_2026 | Bonds | USD | 38 | — | — | UNSECURED | SENIOR | 4.30% | 2037 | NOT_LEASE | FIXED | — | — | — | 4.30 | — | [C31] | Note 6. Long-Term Debt, book value |
| sid_bonds | Special Improvement District Bonds | FY2025 | Bonds | USD | 40 | — | — | UNSECURED | SENIOR | 4.30% | 2037 | NOT_LEASE | FIXED | — | — | — | 4.30 | — | [C31] | Note 6. Long-Term Debt, book value |
| other_payables | Long-term notes and other payables | H1_2026 | Other payables | USD | 1 | — | — | NOT_STATED | NOT_STATED | — | — | NOT_LEASE | NOT_STATED | — | — | — | — | — | [C32] | Note 6. Long-Term Debt, book value |
| other_payables | Long-term notes and other payables | FY2025 | Other payables | USD | 2 | — | — | NOT_STATED | NOT_STATED | — | — | NOT_LEASE | NOT_STATED | — | — | — | — | — | [C32] | Note 6. Long-Term Debt, book value |

<!-- table: cp1.entity_profile -->

| entity | role | fiscal_year_end | reporting_currency | reporting_unit | perimeter | accounting_basis | cite |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Borrower | 12-31 | USD | MILLIONS | Consolidated | US GAAP | [C33] |

## Gaps

- No pro forma adjustment register rows: the pack has no sourced pro forma figures.
- No listed equity value: no market data export in the pack.

## Citations

<!-- table: citations -->

| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_Q2_2026_10Q.txt | Statements of Operations, six months ended June 30 | Net revenues |
| C2 | CZR_Q2_2026_10Q.txt | Statements of Operations, six months ended June 30 | OPERATING EXPENSES: |
| C3 | CZR_Q2_2026_10Q.txt | Statements of Operations, six months ended June 30 | Depreciation and amortization |
| C4 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA reconciliation, six months ended June 30 | Adjusted EBITDA |
| C5 | CZR_Q2_2026_10Q.txt | Supplemental cash flow information, six months ended June 30 | Cash interest paid for debt |
| C6 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows, six months ended June 30 | Purchase of property and equipment |
| C7 | CZR_Q2_2026_10Q.txt | Statements of Cash Flows, six months ended June 30 | Net cash provided by operating activities |
| C8 | CZR_Q2_2026_10Q.txt | Balance Sheets, June 30, 2026 and December 31, 2025 | Cash and cash equivalents |
| C9 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | Total debt |
| C10 | CZR_FY2025_10K.txt | Consolidated Statements of Operations, 2025 | Net revenues |
| C11 | CZR_FY2025_10K.txt | Consolidated Statements of Operations, 2025 | OPERATING EXPENSES: |
| C12 | CZR_FY2025_10K.txt | Consolidated Statements of Operations, 2025 | Depreciation and amortization |
| C13 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation, 2025 | Adjusted EBITDA |
| C14 | CZR_FY2025_10K.txt | Supplemental cash flow information, 2025 | Cash interest paid for debt |
| C15 | CZR_FY2025_10K.txt | Consolidated Statements of Cash Flows, 2025 | Purchase of property and equipment |
| C16 | CZR_FY2025_10K.txt | Consolidated Statements of Cash Flows, 2025 | Net cash provided by operating activities |
| C17 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA reconciliation, six months ended June 30 | Transaction costs and other, net (a) |
| C18 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation, 2025 | Transaction costs and other, net (d) |
| C19 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA reconciliation, six months ended June 30 | Stock-based compensation expense |
| C20 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation, 2025 | Stock-based compensation expense |
| C21 | CZR_FY2025_10K.txt | Adjusted EBITDA reconciliation, 2025 | Impairment charges (c) |
| C22 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Revolving Credit Facility |
| C23 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Term Loan A |
| C24 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CVA Delayed Draw Term Loan |
| C25 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Term Loan B |
| C26 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Term Loan B-1 |
| C27 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Senior Secured Notes due 2030 |
| C28 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Senior Secured Notes due 2032 |
| C29 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Senior Notes due 2029 |
| C30 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | CEI Senior Notes due 2032 |
| C31 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | Special Improvement District Bonds |
| C32 | CZR_Q2_2026_10Q.txt | Note 6. Long-Term Debt, book value | Long-term notes and other payables |
| C33 | CZR_Q2_2026_10Q.txt | Balance Sheets, column headings | CONSOLIDATED CONDENSED BALANCE SHEETS |
````

`tests/model/fixtures/run_brief_czr.md`:

````markdown
---
module_id: RUN_BRIEF
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Pass
inputs: CP-0
---

## Analysis

Run Brief fixture for the Model's corpus test (Plan 03). The SSIM EV multiple is analyst-asserted.

## Tables

<!-- table: snapshot.run_header -->

| run_id | issuer | issuer_id | as_of_date | objective | analyst | pathway | depth | primary | currency | unit | morningstar_issuer_id | ssim_ev_multiple_x | report_date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20261011-czr-full-credit-assessment | Caesars Entertainment, Inc. | CZR | 2026-10-02 | Full credit assessment | Analyst | FULL_CREDIT_ASSESSMENT | full | No | USD | MILLIONS | — | 8.0x | 2026-10-11 |

<!-- table: snapshot.transaction_summary -->

| tranche_id | borrower | bloomberg_id | instrument | debt_type | use_of_proceeds | size | currency | unit | price_talk | talk_stage | oid | maturity_date | expected_ratings | cr_score | commitment_date | status | analyst_value | cite |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Gaps

- No Transaction Summary: not a Primary run.

## Citations

<!-- table: citations -->

| id | source | locator | excerpt |
|---|---|---|---|
````

`tests/model/test_corpus_model.py`:

```python
"""The Model on the local issuer corpus (interfaces spec §12.5, Plan 03).

`test_model_on_caos_fixture` runs the ported Model over the caos Example
Gaming Co. registers through `rbot model` and checks the house view the
caos figures give. `test_cp1_czr_fixture_is_anchored_in_the_corpus` checks
that every figure the hand-written CZR CP-1 Handoff reports is on the line
its citation names in the hash-checked corpus file (pack `czr-2026q2-primary`,
through the `corpus_pack` fixture, so RBOT_REQUIRE_CORPUS decides fail or
skip), and `test_model_from_cp1_handoff_fixture` runs `rbot model` on it.

CZR's LTM to 30 June 2026 is FY2025 + H1 2026 - H1 2025: revenue 11,486 +
5,863 - 5,701 = 11,648; EBITDA (operating income plus D&A) 3,275 + 1,715 -
1,735 = 3,255; add-backs impairment 182 (FY only), transaction costs 72 + 45
- 54 = 63 and stock-based compensation 95 + 47 - 50 = 92, so adjusted (SSIM,
all realized) EBITDA 3,592, as CZR states (3,624 + 1,807 - 1,839); cash
interest paid for debt 813 + 368 - 405 = 776; total debt 11,705 and cash 965
at 30 June 2026, net debt 10,740. No PF rows: the snapshot column is the LTM.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, run_brief, run_folder

from rbotlib.cli import main
from rbotlib.handoff import Table, parse
from rbotlib.model.snapshot import display

pytestmark = pytest.mark.corpus
FIXTURES = Path(__file__).parent / "fixtures"
CZR = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
CHECKED = {"VERIFIED"}
PACK = "czr-2026q2-primary"


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.columns, row, strict=True)) for row in table.rows]


def _shown(value: str) -> str:
    """A register figure as the filings print it: thousands separated, unsigned."""
    return f"{abs(Decimal(value)):,f}"


def _model(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "model.json").read_text(encoding="utf-8"))
    return data


def test_model_on_caos_fixture(tmp_path: Path) -> None:
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief())
    assert main(["model", "--run", str(run)]) == 0
    house = _model(run)["house"]
    assert {k: house[k]["value"] for k in ("structuring_ebitda", "ssim_ebitda", "pf_interest")} == {
        "structuring_ebitda": "4134",
        "ssim_ebitda": "4094",
        "pf_interest": "904",
    }
    assert _model(run)["reconciliation_faults"] == []


def test_cp1_czr_fixture_is_anchored_in_the_corpus(corpus_pack: Callable[[str], Path]) -> None:
    folder = corpus_pack(PACK)
    handoff = parse(CZR)
    citations = {row["id"]: row for row in _rows(handoff.tables["citations"])}
    texts = {
        c["source"]: (folder / c["source"]).read_text(encoding="utf-8") for c in citations.values()
    }
    for c in citations.values():
        assert c["excerpt"] in texts[c["source"]], c["id"]
    figures = [
        (r["source_id"], r["value"])
        for r in _rows(handoff.tables["cp1.model_account_register"])
        if r["calculation_status"] in CHECKED
    ]
    figures += [
        (r["source_id"], r["value"]) for r in _rows(handoff.tables["cp1.adjusted_ebitda_bridge"])
    ]
    figures += [
        (r["source_id"], r["carrying_value"])
        for r in _rows(handoff.tables["cp1.debt_facility_register"])
    ]
    assert len(figures) == 51
    for marker, value in figures:
        cited = citations[marker.strip("[]")]
        lines = texts[cited["source"]].splitlines()
        assert any(cited["excerpt"] in line and _shown(value) in line for line in lines), (
            marker,
            value,
        )


def test_model_from_cp1_handoff_fixture(tmp_path: Path, corpus_pack: Callable[[str], Path]) -> None:
    corpus_pack(PACK)  # the fixture's figures stand on the corpus
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, CZR, brief)
    assert main(["model", "--run", str(run)]) == 0
    data = _model(run)
    assert data["snapshot_columns"]["LTM"] == "LTM:LTM_Q2_2026"
    lines = {line["line_id"]: line for line in data["lines"]}
    ltm = {
        line_id: {c["column_id"]: c["value"] for c in lines[line_id]["cells"]} for line_id in lines
    }
    assert ltm["revenue"]["LTM:LTM_Q2_2026"] == "11648"
    assert ltm["ebitda"]["LTM:LTM_Q2_2026"] == "3255"
    assert ltm["adjusted_ebitda"]["LTM:LTM_Q2_2026"] == "3592"
    assert ltm["total_debt"]["LTM:LTM_Q2_2026"] == "11705"
    assert ltm["net_debt"]["LTM:LTM_Q2_2026"] == "10740"
    house = data["house"]
    assert house["ssim_ebitda"]["value"] == house["structuring_ebitda"]["value"] == "3592"
    assert house["pf_interest"]["value"] == "776"
    assert display(Decimal(house["pf_interest_cover"]["value"]), "MULTIPLE") == "4.63"
    assert display(Decimal(house["ssim_multiple"]["value"]), "MULTIPLE") == "3.26"
    assert house["ev"]["value"] == "28736.0" and house["ev"]["basis"] == "ssim_multiple"
    totals = {r["line"]: r for r in data["capital_structure"]["totals"]}
    assert totals["Senior secured debt"]["amount"] == "9385"
    assert totals["Unsecured debt"]["amount"] == "2319"
    assert totals["Equity"]["amount"] == "17996.0"
    wall = [(r["fiscal_year"], r["facility_id"], r["amount"]) for r in data["maturity_wall"]]
    assert wall[:2] == [("2028", "cei_rcf", "120"), ("2028", "cei_tla", "618")]
    assert wall[-1] == ("2037", "sid_bonds", "38")
    codes = {text.split(":")[0] for text in data["limitations"]}
    assert {"PF_LTM_EQUALS_LTM", "CP1D_NOT_READ", "NO_PROJECTIONS", "MATURITY_NOT_STATED"} <= codes
    assert data["reconciliation_faults"] == []
```

- [ ] **Step 2: Write the failing A10 test**

`tests/model/test_expectation_ids.py`:

```python
"""Plan 02's hand-checked CZR expectations use the Model's ids (amendment A10).

Every CP-1 account expectation is read into registers of its own and must
come out on the Model line its metric feeds, on the column of its period, as
the line's figure or as CP-1's stated figure the line is compared with. Pro
forma expectations name a metric the PF-LTM adjusts, and every facility
expectation sits on a period the account expectations also use.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.registers import AccountRow, Cp1Registers, PeriodRow

EXPECTATIONS = Path(__file__).parents[1] / "corpus/expectations/czr-2026q2-primary.json"
LINE_OF = {
    "revenue": "revenue",
    "depreciation_amortization": "da",
    "adjusted_ebitda": "adjusted_ebitda",
    "cash_interest_paid": "cash_interest",
    "cash_and_equivalents": "cash_closing",
    "total_debt": "total_debt",
}
PF_METRICS = {"revenue", "ebitda", "adjusted_ebitda", "cash_interest_paid"}
PF_METRICS |= {"cash_and_equivalents", "total_debt"}


def _values(table: str) -> list[dict[str, Any]]:
    data = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
    return [v for v in data["values"] if v["table"] == table]


def _period(period_id: str) -> PeriodRow:
    """`FY<yyyy>` is the calendar year; `H1_<yyyy>` its first six months."""
    if period_id.startswith("FY"):
        year, quarter, kind, end = period_id[2:], None, "FY", "12-31"
    else:
        head, _, year = period_id.partition("_")
        assert head == "H1", period_id
        quarter, kind, end = "Q2", "YTD", "06-30"
    start = f"{year}-01-01"
    return PeriodRow(period_id, f"FY{year}", quarter, kind, start, f"{year}-{end}", None, "USD",
                     "MILLIONS", ())  # fmt: skip


def test_every_account_expectation_lands_on_its_model_line() -> None:
    expected = _values("cp1.model_account_register")
    assert len(expected) == 12
    pids = sorted({v["where"]["period_id"] for v in expected})
    accounts = tuple(
        AccountRow(v["where"]["metric_id"], v["where"]["period_id"], Decimal(v["value"]),
                   "VERIFIED", None)
        for v in expected
    )  # fmt: skip
    regs = Cp1Registers(
        tuple(_period(p) for p in pids), accounts, (), (), (), (), (), "USD", "MILLIONS"
    )
    model = credit_model(ModelInputs(regs))
    lines = {line.line_id: line for line in model.lines}
    for v in expected:
        line = lines[LINE_OF[v["where"]["metric_id"]]]
        index = next(
            n
            for n, c in enumerate(model.columns)
            if c.period_id == v["where"]["period_id"] and c.kind in {"FY", "YTD", "PYTD"}
        )
        cell = line.cells[index]
        shown = {abs(x) for x in (cell.value, cell.stated) if x is not None}
        assert abs(Decimal(v["value"])) in shown, v


def test_pro_forma_and_facility_expectations_use_model_ids() -> None:
    for v in _values("cp1.pro_forma_adjustment_register"):
        metric = v["where"]["metric_id"]
        assert metric in PF_METRICS or metric.startswith("facility:"), v
    interest = next(
        v
        for v in _values("cp1.pro_forma_adjustment_register")
        if v["where"]["metric_id"] == "cash_interest_paid"
    )
    assert Decimal(interest["value"]) < 0
    periods = {v["where"]["period_id"] for v in _values("cp1.model_account_register")}
    facilities = _values("cp1.debt_facility_register")
    assert len(facilities) == 6
    assert {v["where"]["period_id"] for v in facilities} <= periods


def _figures(excerpt: str) -> list[Decimal]:
    return [Decimal(f.strip().strip("$").replace(",", "")) for f in excerpt.split("|")[-3:]]


def test_carrying_values_are_book_never_face() -> None:
    """The debt notes cite `Face Value | Book Value | Book Value (prior)`: a
    carrying value (and CP-1's total debt) is the book value, never the face."""
    carried = [v for v in _values("cp1.debt_facility_register") if v["column"] == "carrying_value"]
    carried += [
        v for v in _values("cp1.model_account_register") if v["where"]["metric_id"] == "total_debt"
    ]
    assert len(carried) == 6
    for v in carried:
        face, book, _ = _figures(v["excerpt"])
        assert Decimal(v["value"]) == book != face, v
```

- [ ] **Step 3: Run the new tests and see them fail**

Run: `uv run pytest tests/model/test_expectation_ids.py --no-cov`
Expected: 3 failed: `AssertionError: Q2_2026_END` (a period id the Model does not use), `assert Decimal('213') < 0`, and a face value under `carrying_value` (`2000` where the filing's book value is `1987`).

- [ ] **Step 4: Apply amendment A10**

Save this as `$KIT/a10.py` (the git-ignored kit folder) and run `uv run python "$KIT/a10.py" "$PWD"`; it prints `A10 applied` (every replacement is checked to occur exactly the stated number of times).

```python
"""Amendment A10: Plan 02's CZR expectations take the Model's ids and conventions."""

import json
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "tests/corpus/expectations/czr-2026q2-primary.json"
s = p.read_text(encoding="utf-8")
OLD_NOTE = (
    "Metric ids follow caos model_inputs (Plan 03 owns the exact list); period ids FY<yyyy>, "
    "YTD_Q2_<yyyy> (six months to June 30) and Q2_<yyyy>_END (balance at June 30)."
)
NEW_NOTE = (
    "Metric and period ids are the Model's (Plan 03, amendment A10): CP-1 metric ids as "
    "rbotlib.model reads them; period ids FY<yyyy> and H1_<yyyy> (six months to June 30; "
    "June 30 balances sit on H1_<yyyy>, the period ending that day). Sign convention: pro "
    "forma rows are not sign-normalised, so a cash outflow on a pro forma row is negative. "
    "carrying_value and total_debt are book values (the carrying amount as filed), never face."
)


def note_row(
    name: str, face: str, book: str, prior: str, maturity: str, rate: str
) -> tuple[str, str, int]:
    """A note's carrying value: book (the 10-Q's June 30 Book Value), with the whole line cited."""
    short = f'"value": "{face.replace(",", "")}", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "{name} | {maturity} | {rate} | {face}"'
    full = f'"value": "{book.replace(",", "")}", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt", "locator": "Note 6. Long-Term Debt", "excerpt": "{name} | {maturity} | {rate} | {face} | {book} | {prior}"'
    return short, full, 1


SUBS = [
    (OLD_NOTE, NEW_NOTE, 1),
    ('"metric_id": "da"', '"metric_id": "depreciation_amortization"', 1),
    ("YTD_Q2_2026", "H1_2026", 2),
    ("YTD_Q2_2025", "H1_2025", 1),
    ("Q2_2026_END", "H1_2026", 9),
    (
        '"value": "213", "tolerance": "0", "calc": "989 - 776"',
        '"value": "-213", "tolerance": "0", "calc": "-(989 - 776)"',
        1,
    ),
    # total debt is the book total (10-K and 10-Q Note: Face Value | Book Value | Book Value).
    (
        '"value": "11905", "tolerance": "0", "source": "CZR_FY2025_10K.txt"',
        '"value": "11792", "tolerance": "0", "source": "CZR_FY2025_10K.txt"',
        1,
    ),
    (
        '"value": "11807", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt"',
        '"value": "11705", "tolerance": "0", "source": "CZR_Q2_2026_10Q.txt"',
        1,
    ),
    note_row("CEI Senior Secured Notes due 2030", "2,000", "1,987", "1,986", "2030", "7.00%"),
    note_row("CEI Senior Secured Notes due 2032", "1,500", "1,487", "1,486", "2032", "6.50%"),
    note_row("CEI Senior Notes due 2029", "1,200", "1,193", "1,192", "2029", "4.625%"),
    note_row("CEI Senior Notes due 2032", "1,100", "1,088", "1,087", "2032", "6.00%"),
]
for old, new, count in SUBS:
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)
json.loads(s)
p.write_text(s, encoding="utf-8")
print("A10 applied")
```

- [ ] **Step 5: Run the corpus gate**

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov | tail -1
RBOT_CORPUS_ROOTS='{}' RBOT_REQUIRE_CORPUS=1 uv run pytest tests/model -m corpus --no-cov | tail -1
```

Expected: every corpus test passes (Plan 02's 110 plus this plan's 3: `113 passed`); with no roots the two CZR tests fail (not skip) naming the unresolved root: `2 failed, 1 passed`.

- [ ] **Step 6: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `621 passed, 112 skipped` (400 Model tests passed, 2 Model corpus tests skipped on top of Plan 02's 221 passed, 110 skipped), coverage 98.63% (floor 80%); every gate exits 0.

- [ ] **Step 7: Commit and measure the PR**

```bash
git switch -c build/03f1-corpus
git add tests/model/test_run_outputs.py tests/model/fixtures/cp1_czr_2026q2.md tests/model/fixtures/run_brief_czr.md tests/model/test_corpus_model.py tests/corpus/expectations/czr-2026q2-primary.json tests/model/test_expectation_ids.py
git commit -m "model: output and corpus tests; A10 aligns Plan 02's expectation ids

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03e4-rbot-model bash scripts/check_pr_size.sh
```

Expected: `578 changed lines (limit 800)`.

Report: `Not verified:` the CZR CP-1 fixture is hand-written; a CP-1 Handoff from a proxy run (Plan 05) may choose other facility ids (`facility:<id>` rows must name the register's ids). A10 sets book values (controller ruling).


---

### Task 25: Mutation gate (PR 03F2)

**Files:**
- Create: `scripts/mutate_model.sh`, `docs/model/mutation.md`
- Modify: `pyproject.toml`, `uv.lock`
- Test: `tests/model/test_house_detail.py`, `tests/model/test_golden_outputs.py`, `tests/model/test_reader_edges.py`, `tests/model/test_inputs_edges.py`, `tests/model/test_house_inputs_edges.py`, `tests/model/test_outputs_edges.py`

**Interfaces:**
- Consumes: the whole Model package and its tests.
- Produces: `scripts/mutate_model.sh` (mutmut 3.7.0 in a throwaway workspace: mutmut names a mutant by its file path, so the package is copied under `src/` exactly as the tests import it, `rbotlib.model.*`; nothing in the repo is written); the dev dependency `mutmut==3.7.0`; characterisation and edge tests that kill the survivors the gate found (`test_house_detail.py`; `test_golden_outputs.py`, the digests of `model.json`, MODEL.md and the `model.xlsx` values on two fixed inputs; `test_reader_edges.py`, `test_inputs_edges.py`, `test_house_inputs_edges.py`, `test_outputs_edges.py`); `docs/model/mutation.md`, the record of the run: 9424 mutants, 9243 killed, 3 timed out (killed), 178 survived, each survivor listed with why it is not killed (equivalent, projection-only until Plan 13, or a gap inherited unchanged from caos).

**Agent:** `mx-invariants`.

- [ ] **Step 1: Add mutmut**

Run `uv add --dev mutmut==3.7.0`. Expected: `pyproject.toml` gains `"mutmut==3.7.0",` in `[dependency-groups] dev` (sorted before `mypy`) and `uv.lock` changes; `uv lock --check` exits 0.

- [ ] **Step 2: Write the mutation gate**

`scripts/mutate_model.sh`:

```bash
#!/usr/bin/env bash
# Mutation gate for the Model (money code, interfaces spec section 6.1).
# mutmut 3 names a mutant by its file's path from the working directory, so
# it runs in a throwaway workspace where the package sits under src/ exactly
# as the tests import it (rbotlib.model.*). Nothing in the repo is written.
# Usage: bash scripts/mutate_model.sh [mutant glob ...], e.g. "rbotlib.model.house.*".
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)/model"
mkdir -p "$work/src" "$work/docs"
cp -R "$repo/rbot/scripts/rbotlib" "$work/src/rbotlib"
cp -R "$repo/tests" "$work/tests"
cp -R "$repo/docs/model" "$work/docs/model"
# rbotlib.rules.RBOT_ROOT is two folders above the package: the workspace.
cp "$repo/rbot/rules.json" "$repo/rbot/catalog.json" "$repo/rbot/canon.md" "$work/"
cat > "$work/pyproject.toml" <<'TOML'
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "tests"]
addopts = "-q --strict-markers -p no:cacheprovider"
markers = ["corpus: reads the local issuer corpus"]

[tool.mutmut]
source_paths = ["src"]
only_mutate = ["src/rbotlib/model/*.py"]
also_copy = ["docs", "rules.json", "catalog.json", "canon.md"]
pytest_add_cli_args_test_selection = ["tests/model"]
use_git_change_detection = false
TOML
cd "$work"
echo "mutation workspace: $work"
uv run --project "$repo" mutmut run "$@"
uv run --project "$repo" mutmut results
```

- [ ] **Step 3: Write the tests that kill the survivors**

They pin behaviour the Model already has, so they pass on arrival; the gate below is what proves they matter. `test_golden_outputs.py` pins digests: if one differs, the tree is not at Task 24's end state (stop, report BLOCKED); never regenerate a digest to make the test pass.

`tests/model/test_house_detail.py`:

```python
"""The house view in detail: what each item states, the cells' bases and
sources, the limitations' wording and exactness past 28 digits (the mutation
gate's findings on `rbotlib.model.house`)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from credit_model_fixture import example_registers

from rbotlib.model.assemble import ModelInputs, credit_model
from rbotlib.model.frame import Cell, SourceRef
from rbotlib.model.house import (
    HouseView,
    Position,
    cumulative,
    debt_like_key,
    house_view,
    ratio,
    with_debt_like_lines,
)
from rbotlib.model.house_inputs import BriefFields, DebtLikeItem, EquityValue, HouseInputs
from rbotlib.model.registers import Cp1Registers

PF = "PF:LTM_Q2_2026"
A, B = SourceRef("S1", "p.1", "1"), SourceRef("S2", "p.2", "2")


def _inputs(equity: EquityValue | None = None, multiple: str | None = None) -> HouseInputs:
    brief = BriefFields("R", None if multiple is None else Decimal(multiple), False, frozenset())
    return HouseInputs({}, equity, (), (), brief)


def _view(regs: Cp1Registers | None = None, inputs: HouseInputs | None = None) -> HouseView:
    regs = regs or example_registers()
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    return house_view(model, regs, inputs or _inputs())


def test_every_item_states_its_unit_formula_components_and_basis() -> None:
    view = _view()
    assert [(i.key, i.unit, i.formula, i.components, i.cell.basis) for i in view.items] == [
        ("structuring_ebitda", "MONEY", "adjusted_ebitda + excluded (unrealized) add-backs",
         ("adjusted_ebitda", "addback:run_rate_cost_savings"), "CALCULATED"),
        ("ssim_ebitda", "MONEY", "adjusted_ebitda, unrealized add-backs excluded",
         ("adjusted_ebitda",), "PRO_FORMA"),
        ("pf_interest", "MONEY", "-(cash_interest + its PF rows)", ("cash_interest",),
         "CALCULATED"),
        ("pf_interest_cover", "MULTIPLE", "SSIM EBITDA / PF interest",
         ("adjusted_ebitda", "cash_interest"), "CALCULATED"),
        ("structuring_multiple", "MULTIPLE", "total_debt / Structuring EBITDA",
         ("total_debt", "adjusted_ebitda", "addback:run_rate_cost_savings"), "CALCULATED"),
        ("ssim_multiple", "MULTIPLE", "total_debt / SSIM EBITDA",
         ("total_debt", "adjusted_ebitda"), "CALCULATED"),
        ("ev", "MONEY", "listed equity value + net_debt, else SSIM EV multiple x SSIM EBITDA",
         ("net_debt", "adjusted_ebitda"), None),
        ("adjusted_debt", "MONEY", "total_debt + CP-1D debt-like items", ("total_debt",),
         "CALCULATED"),
        ("adjusted_leverage", "MULTIPLE", "Adjusted debt / SSIM EBITDA",
         ("total_debt", "adjusted_ebitda"), "CALCULATED"),
    ]  # fmt: skip
    ev = view.item("ev").cell
    why = "no listed equity value and no SSIM EV multiple (or no SSIM EBITDA)"
    assert (ev.reason, ev.note, view.equity.note) == ("NOT_SOURCED", why, why)


def test_a_ratio_is_exact_calculated_and_keeps_both_sources() -> None:
    half = ratio(Cell(Decimal(1), sources=(A,)), Cell(Decimal("0.5"), sources=(B,)))
    assert (half.value, half.basis, half.sources) == (Decimal(2), "CALCULATED", (A, B))


def test_cumulative_debt_is_exact_past_28_digits() -> None:
    view = _view()
    line = next(p.line for p in view.positions if p.facility_id == "tlb")
    big = (Position("a", line, Cell(Decimal(10) ** 30)), Position("b", line, Cell(Decimal(1))))
    assert cumulative(replace(view, positions=big), "Senior secured").value == 10**30 + 1


def test_a_facility_with_no_balance_at_the_date_is_out_unless_pf_rows_add_it() -> None:
    regs = example_registers()
    tlb = next(f for f in regs.facilities if f.facility_id == "tlb" and f.period_id == "FY2024")
    notes = next(a for a in regs.pro_forma if a.metric_id == "facility:ssn31")
    regs = replace(
        regs,
        facilities=(
            *regs.facilities,
            replace(tlb, facility_id="old"),
            replace(tlb, facility_id="add"),
        ),
        pro_forma=(*regs.pro_forma, replace(notes, adjustment_id="a1", metric_id="facility:add")),
    )
    outstanding = {p.facility_id: p.outstanding.value for p in _view(regs).positions}
    assert "old" not in outstanding
    assert outstanding["add"] == 600


def test_an_excluded_add_back_without_a_row_on_the_column_is_no_component() -> None:
    regs = example_registers()
    old = next(b for b in regs.addbacks if b.addback_id == "run_rate_cost_savings")
    regs = replace(regs, addbacks=(*regs.addbacks, replace(old, addback_id="synergies")))
    structuring = _view(regs).item("structuring_ebitda")
    assert structuring.components == ("adjusted_ebitda", "addback:run_rate_cost_savings")
    assert structuring.cell.value == 4134


def test_pf_interest_drops_the_sign_note_of_the_interest_it_negates() -> None:
    regs = example_registers()
    positive = tuple(
        replace(a, value=abs(a.value)) if a.metric_id == "cash_interest_paid" and a.value else a
        for a in regs.accounts
    )
    view = _view(replace(regs, accounts=positive, pro_forma=()))
    interest = view.item("pf_interest").cell
    assert (interest.value, interest.note) == (Decimal(862), None)


def test_a_debt_like_line_follows_the_debt_band_with_its_cited_amount() -> None:
    item = DebtLikeItem(" Pension (deficit)! ", Decimal(120), "USD", "MILLIONS", "LTM_Q2_2026",
                        "Debt-like", "unfunded", "[C1]")  # fmt: skip
    assert debt_like_key(item) == "debt_like:pension_deficit"
    model = with_debt_like_lines(credit_model(ModelInputs(example_registers())), (item,))
    ids = [line.line_id for line in model.lines]
    at = ids.index("debt_like:pension_deficit")
    assert ids[at - 1] == "lease_adjusted_net_debt"
    assert model.lines[at + 1].band != model.lines[at].band
    on_pf = model.lines[at].cells[[c.column_id for c in model.columns].index(PF)]
    assert (on_pf.basis, on_pf.sources) == ("REPORTED", (SourceRef("[C1]", "", "120"),))


def test_listed_equity_is_reported_cited_and_exact() -> None:
    cap = Decimal("1234567890123456789012345.6789")
    listed = _view(inputs=_inputs(EquityValue(cap, "2026-10-02", "USD", "THOUSANDS", "[C9]")))
    assert listed.equity.value == Decimal("1234567890123456789012.3456789")
    assert listed.equity.basis == "REPORTED"
    assert listed.equity.sources == (SourceRef("[C9]", "", f"{cap:f}"),)
    assert listed.item("ev").formula == "listed equity value + net_debt"
    euro = _view(inputs=_inputs(EquityValue(cap, "2026-10-02", "EUR", "THOUSANDS", "[C9]")))
    assert euro.item("ev").cell.note == "equity value in EUR, the run is in USD"


def test_the_ssim_multiple_ev_is_calculated_from_ssim_ebitda_exactly() -> None:
    view = _view(inputs=_inputs(multiple="8.123456789012345678901234567"))
    ev, ssim = view.item("ev"), view.item("ssim_ebitda").cell
    assert ev.cell.value == Decimal("33257.432094216543209421654317298")
    assert (ev.cell.basis, ev.cell.sources) == ("CALCULATED", ssim.sources)
    assert ev.formula == "SSIM EV multiple x SSIM EBITDA"


def test_limitations_say_why_and_pf_interest_drops_the_stated_figure() -> None:
    regs = example_registers()
    plain = _view(replace(regs, pro_forma=()))
    assert plain.limitations[0] == (
        "PF_LTM_EQUALS_LTM",
        "no pro forma adjustments for the LTM: every PF figure is the LTM's",
    )
    interest = plain.item("pf_interest").cell
    assert (interest.value, interest.stated, interest.note) == (Decimal(862), None, None)
    rows = tuple(a for a in regs.pro_forma if a.metric_id != "cash_interest_paid")
    assert _view(replace(regs, pro_forma=rows)).limitations[0] == (
        "PF_INTEREST_NOT_SOURCED",
        "no sourced PF cash interest: PF interest is the LTM's cash interest",
    )
    assert _view(replace(regs, periods=())).equity.reason == "NOT_APPLICABLE"
```

`tests/model/test_golden_outputs.py`:

```python
"""`rbot model`'s three files on two fixed inputs, pinned by digest: the caos
example with a CP-1D Handoff, and the CZR CP-1 fixture (no CP-1D).

A characterisation gate (the mutation gate's findings on the output
modules): any change to a byte of model.json or MODEL.md, or to a value in
model.xlsx (or its number format), fails here. Regenerate a digest only for an intended change and
say in the commit which output changed and why; model.xlsx is compared by
its cell values because openpyxl stamps the file with the time it wrote it.
"""

from __future__ import annotations

import hashlib
import json
from io import BytesIO
from pathlib import Path

from credit_model_fixture import example_registers
from model_handoffs import cp1_handoff, run_brief, run_folder
from openpyxl import load_workbook
from run_cases import cp1d_handoff

from rbotlib.model.run import run_model

FIXTURES = Path(__file__).parent / "fixtures"
AT = "2026-10-11T00:00:00+00:00"


def _digests(run: Path) -> dict[str, str]:
    book = load_workbook(BytesIO((run / "model.xlsx").read_bytes()))
    cells = {
        s.title: [[f"{c.value}|{c.number_format}" for c in row] for row in s.iter_rows()]
        for s in book
    }
    texts = {
        "model.json": (run / "model.json").read_bytes(),
        "MODEL.md": (run / "handoffs" / "MODEL.md").read_bytes(),
        "model.xlsx": json.dumps(cells, sort_keys=True).encode("utf-8"),
    }
    return {name: hashlib.sha256(data).hexdigest() for name, data in texts.items()}


def test_the_example_outputs_are_unchanged(tmp_path: Path) -> None:
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief(), cp1d_handoff())
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "ac7c910c071ebde5969a068407a56e48f2f0e74d5de2bc0233ad5af0e372dbc6",
        "MODEL.md": "b1ed444e1a50b4a8d257a48e98ce0be2c2b3109683cf1c4d1e568ad1cd6044b2",
        "model.xlsx": "bb8c937cd4ebabf3001398f82474f2dae278b0337bfdef54481b5b9f2109d895",
    }


def test_the_czr_outputs_are_unchanged(tmp_path: Path) -> None:
    cp1 = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, cp1, brief)
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "3f65f04bd99ff0cde0261feb3015ac07be5be005e326fd9c670a82bf559b15af",
        "MODEL.md": "97302dbd031a439701038a1debcf27b7dd952c67241a273ce37e5fcd50eec386",
        "model.xlsx": "c43dbef947463086b1db9f67c62cc5e9fc5769d363d6d7fa4e35d080c5b28890",
    }
```

`tests/model/test_reader_edges.py`:

```python
"""The figure and cell rules at their edges (the mutation gate's findings on
`rbotlib.model.reader`)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from rbotlib.handoff import Table
from rbotlib.model.reader import ModelInputError, Row, date_cell, decimal, figure, rows


@pytest.mark.parametrize(
    ("cell", "value"),
    [
        ("4[C1]55", None),  # a marker inside a figure splits it, whatever follows
        ("4[C1]x", Decimal(4)),  # a marker before a non-figure character only drops
        ("4 [C1]5", Decimal(45)),  # a spaced marker is dropped with its space
        ("12,3456", None),  # a comma that is neither thousands nor ambiguous
        ("(12", None),  # one parenthesis is not a negative
        ("Infinity", None),
        ("1" * 64, Decimal("1" * 64)),  # 64 characters is the longest figure
        ("1" * 65, None),
    ],
)
def test_figure_edges(cell: str, value: Decimal | None) -> None:
    assert figure(cell) == value


def _row(**cells: str) -> Row:
    return Row("t", 1, cells)


def test_ten_decimals_and_the_date_bounds_are_accepted() -> None:
    assert decimal(_row(v="0.0000000001"), "v") == Decimal("0.0000000001")
    with pytest.raises(ModelInputError, match="more than 10 decimals"):
        decimal(_row(v="0.00000000001"), "v")
    assert str(date_cell(_row(d="1900-01-01"), "d")) == "1900-01-01"
    assert str(date_cell(_row(d="2200-12-31"), "d")) == "2200-12-31"
    with pytest.raises(ModelInputError, match="column d: '1899-12-31'"):
        date_cell(_row(d="1899-12-31"), "d")


def test_every_missing_column_is_named() -> None:
    with pytest.raises(ModelInputError, match=r"t: missing column a, b$"):
        rows({"t": Table(["c"], [])}, "t", frozenset({"a", "b", "c"}))
```

`tests/model/test_inputs_edges.py`:

```python
"""CP-1's tables at the edges of what `cp1_registers` accepts (the mutation
gate's findings on `rbotlib.model.inputs`)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers
from inputs_cases import FY2025, PERIOD_COLUMNS, _periods, _refused, _tables
from model_handoffs import cp1_handoff

from rbotlib.handoff import Table, parse
from rbotlib.model.inputs import MAX_PERIODS, cp1_registers
from rbotlib.model.registers import FacilityRow

FACILITY = {"facility_id": "TLB", "facility_name": "Term Loan B", "period_id": "FY2025"}
FACILITY |= {"facility_type": "Term loan", "currency": "USD", "carrying_value": "2,018"}
FACILITY |= {"drawn_amount": "2,018", "commitment": "—", "secured_status": "SECURED"}
FACILITY |= {"seniority": "SENIOR", "margin_or_coupon": "SOFR + 225", "maturity_date": "—"}
FACILITY |= {"lease_classification": "NOT_LEASE", "source_id": "—", "source_locator": "—"}


def _p(**cells: str) -> list[str]:
    row = dict(zip(PERIOD_COLUMNS, FY2025, strict=True))
    row.update(cells)
    return list(row.values())


def _facility(**cells: str) -> dict[str, Table]:
    row = FACILITY | cells
    return _tables(debt_facility_register=Table(list(row), [list(row.values())]))


def test_the_period_bounds_are_accepted() -> None:
    longest = (date(2200, 12, 31) - date(1900, 1, 1)).days + 1
    periods = [
        FY2025,
        _p(period_id="D", period_type="PERIOD_END", start_date="2025-12-31", day_count="1"),
        _p(period_id="O", period_type="LTM", end_date="—", day_count="—"),
        _p(period_id="FY1900", fiscal_year="FY1900", start_date="1900-01-01",
           end_date="1900-12-31", day_count="365"),
        _p(period_id="L", fiscal_year="FY2200", period_type="LTM", start_date="1900-01-01",
           end_date="2200-12-31", day_count=str(longest)),
        _p(period_id="FY2026", fiscal_year="FY2026"),  # a year from its end date's year
    ]  # fmt: skip
    found = cp1_registers({"cp1.model_period_register": _periods(*periods)}).periods
    assert [p.period_id for p in found] == ["FY2025", "D", "O", "FY1900", "L", "FY2026"]
    assert (found[1].day_count, found[2].end_date) == (1, None)


def test_a_refusal_names_its_column() -> None:
    far = _p(fiscal_year="FY2027")
    _refused({"cp1.model_period_register": _periods(far)},
             "column fiscal_year: 'FY2027' is more than a year from end_date")  # fmt: skip
    twice = _p(period_type="LTM", component_period_ids="A;A")
    _refused({"cp1.model_period_register": _periods(twice)},
             "column component_period_ids: names a component twice")  # fmt: skip
    columns = ["metric_id", "period_id", "value", "calculation_status", "source_id"]
    rcf = Table([*columns, "source_locator"], [["rcf_drawn", "FY2025", "-1", "VERIFIED", "—", "—"]])
    _refused(_tables(model_account_register=rcf), "row 1 column value: rcf_drawn is a balance")
    unit = _p(period_id="FY2024", fiscal_year="FY2024", start_date="2024-01-01",
              end_date="2024-12-31", day_count="366", unit="THOUSANDS")  # fmt: skip
    _refused({"cp1.model_period_register": _periods(FY2025, unit)},
             "cp1.model_period_register column unit: states MILLIONS, THOUSANDS")  # fmt: skip
    euro = _p(period_id="FY2024", fiscal_year="FY2024", start_date="2024-01-01",
              end_date="2024-12-31", day_count="366", currency="EUR")  # fmt: skip
    _refused({"cp1.model_period_register": _periods(FY2025, euro)},
             "cp1.model_period_register column currency: states EUR, USD")  # fmt: skip


def test_rate_terms_at_their_bounds_and_the_drawn_amount() -> None:
    def read(**cells: str) -> FacilityRow:
        return cp1_registers(_facility(**cells)).facilities[0]

    assert read(spread_bps="50%").terms_out_of_range is True
    low, high = read(fixed_rate="0.5"), read(fixed_rate="30")
    assert (low.terms_out_of_range, high.terms_out_of_range) == (False, False)
    tlb = cp1_registers(_facility()).facilities[0]
    assert (tlb.drawn_amount, tlb.margin_or_coupon) == (Decimal(2018), "SOFR + 225")
    _refused(_facility(drawn_amount="-1"), "row 1 column drawn_amount: cannot be negative")


@pytest.mark.parametrize(("kind", "first", "second"), [("YTD", "Q2", "2"), ("QUARTER", "q2", "Q2")])
def test_one_period_per_fiscal_quarter_however_the_quarter_is_written(
    kind: str, first: str, second: str
) -> None:
    ltm = _p(period_id="LTM", period_type="LTM", fiscal_quarter="Q2")
    a = _p(period_id="A", period_type=kind, fiscal_quarter=first)
    b = _p(period_id="B", period_type=kind, fiscal_quarter=second)
    _refused({"cp1.model_period_register": _periods(ltm, a, b)}, "row 3: a second period for")


def test_a_period_id_written_twice_is_refused_naming_the_period_register() -> None:
    twice = [_p(period_id="L", period_type="LTM"), _p(period_id="L", period_type="LTM")]
    _refused({"cp1.model_period_register": _periods(*twice)},
             "cp1.model_period_register row 2: L written twice")  # fmt: skip


def test_period_ends_may_share_a_quarter_and_nesting_four_deep_is_accepted() -> None:
    ends = [_p(period_id=f"E{i}", period_type="PERIOD_END", fiscal_quarter="Q4") for i in (1, 2)]
    chain = [
        _p(period_id=f"P{i}", period_type="LTM", component_period_ids=f"P{i + 1}" if i < 4 else "—")
        for i in range(5)
    ]
    periods = cp1_registers({"cp1.model_period_register": _periods(*ends, *chain)}).periods
    assert len(periods) == 7
    many = [_p(period_id=f"P{i}", period_type="LTM") for i in range(MAX_PERIODS)]
    assert len(cp1_registers({"cp1.model_period_register": _periods(*many)}).periods) == 200


@pytest.mark.parametrize(
    "table_id",
    [
        "cp1.model_period_register",
        "cp1.model_account_register",
        "cp1.adjusted_ebitda_bridge",
        "cp1.segment_revenue_schedule",
        "cp1.operating_kpi_schedule",
        "cp1.debt_facility_register",
        "cp1.pro_forma_adjustment_register",
    ],
)
def test_a_row_written_twice_is_refused_naming_its_table(table_id: str) -> None:
    tables = dict(parse(cp1_handoff(example_registers())).tables)
    table = tables[table_id]
    tables[table_id] = Table(table.columns, [*table.rows, table.rows[0]])
    _refused(tables, f"{table_id} row {len(table.rows) + 1}: ")
```

`tests/model/test_house_inputs_edges.py`:

```python
"""CP-1D, identity and equity rows read whole (the mutation gate's findings
on `rbotlib.model.house_inputs`)."""

from __future__ import annotations

import re
from decimal import Decimal

import pytest
from credit_model_fixture import example_registers

from rbotlib.handoff import Table
from rbotlib.model.house_inputs import (
    DebtLikeItem,
    EquityValue,
    Identity,
    assessments,
    debt_like_items,
    equity_value,
    identities,
)
from rbotlib.model.reader import ModelInputError

IDENTITY = ["facility_id", "instrument_name", "rating_moodys", "rating_sp", "rating_fitch", "cite"]
DEBT_LIKE = ["item", "amount", "currency", "unit", "period_id", "treatment", "basis", "cite"]
PENSION = ["Pension deficit", "120", "USD", "MILLIONS", "LTM_Q2_2026", "Debt-like", "unfunded"]
ASSESSED = ["addback_id", "period_id", "house_realization_status", "verdict", "cite"]


def test_identity_equity_and_debt_like_rows_are_read_whole() -> None:
    rows = [["tlb", "Term Loan B", "—", "—", "BB+", "[C4]"]]
    found = identities({"cp1.instrument_identity": Table(IDENTITY, rows)})
    assert found["tlb"] == Identity("tlb", "Term Loan B", None, "— / — / BB+", "[C4]")
    columns = ["market_cap", "value_date", "currency", "unit", "cite"]
    equity = Table(columns, [["6,316", "2026-10-02", "usd", "MILLIONS", "[C9]"]])
    assert equity_value({"cp1.equity_value": equity}) == EquityValue(
        Decimal(6316), "2026-10-02", "USD", "MILLIONS", "[C9]"
    )
    table = Table(DEBT_LIKE, [[*PENSION, "[C3]"]])
    pension = DebtLikeItem(
        "Pension deficit", Decimal(120), "USD", "MILLIONS", "LTM_Q2_2026", "Debt-like",
        "unfunded", "[C3]",
    )  # fmt: skip
    assert debt_like_items({"cp1d.debt_like_items": table}, example_registers()) == (pension,)


def test_a_debt_like_item_needs_its_basis_and_is_listed_once() -> None:
    regs = example_registers()
    no_basis = Table([*DEBT_LIKE[:6], "cite"], [[*PENSION[:6], "[C3]"]])
    with pytest.raises(
        ModelInputError, match=re.escape("cp1d.debt_like_items: missing column basis")
    ):
        debt_like_items({"cp1d.debt_like_items": no_basis}, regs)
    no_item = Table(DEBT_LIKE[1:], [[*PENSION[1:], "[C3]"]])
    with pytest.raises(ModelInputError, match=re.escape("missing column item")):
        debt_like_items({"cp1d.debt_like_items": no_item}, regs)
    twice = Table(DEBT_LIKE, [[*PENSION, "[C3]"]] * 2)
    match = "cp1d.debt_like_items row 2: Pension deficit / LTM_Q2_2026 written twice"
    with pytest.raises(ModelInputError, match=re.escape(match)):
        debt_like_items({"cp1d.debt_like_items": twice}, regs)
    rows = [["restructuring", "FY2025", "REALIZED", "Rejected", "[C1]"]] * 2
    match = "cp1d.addback_assessment row 2: restructuring / FY2025 written twice"
    with pytest.raises(ModelInputError, match=re.escape(match)):
        assessments({"cp1d.addback_assessment": Table(ASSESSED, rows)})
```

`tests/model/test_outputs_edges.py`:

```python
"""`rbot model` at its edges: limits, a Model without an LTM, listed equity,
uncited sources, foreign facilities and the limitation codes (the mutation
gate's findings on `run`, `output` and `snapshot`)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from credit_model_fixture import example_registers
from history_cases import _regs
from model_handoffs import cp1_handoff, run_brief, run_folder, table
from run_cases import _model

from rbotlib.cli import main
from rbotlib.handoff import Table, parse
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model
from rbotlib.model.frame import Cell, SourceRef
from rbotlib.model.output import sources_cut
from rbotlib.model.registers import Cp1Registers, KpiRow

EQUITY = ["market_cap", "value_date", "currency", "unit", "cite"]


def _run(
    tmp_path: Path, regs: Cp1Registers, cp1: str | None = None, multiple: str = "8.5x"
) -> Path:
    return run_folder(tmp_path, cp1 or cp1_handoff(regs), run_brief(multiple))


def _tables(run: Path) -> dict[str, Table]:
    return dict(parse((run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")).tables)


def _rows(found: Table) -> list[dict[str, str]]:
    return [dict(zip(found.columns, row, strict=True)) for row in found.rows]


def test_the_column_and_line_limits_are_inclusive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plain = [y for y in range(1901, 2100) if y % 4]  # 365-day years only (history_cases)
    years = _regs(fy={f"FY{y}": {"revenue": 1} for y in plain[:63]})
    assert len(credit_model(ModelInputs(years)).columns) == 64
    assert main(["model", "--run", str(_run(tmp_path / "a", years))]) == 0
    more = _regs(fy={f"FY{y}": {"revenue": 1} for y in plain[:64]})
    assert main(["model", "--run", str(_run(tmp_path / "b", more))]) == 1
    assert "the Model has 65 columns and" in capsys.readouterr().out
    regs = example_registers()
    kpis = tuple(
        KpiRow(f"k{n}", f"K {n}", 1, "FY2025", Decimal(1), "UNITS", "PERIOD_END", None)
        for n in range(290)
    )
    full = replace(regs, kpis=(*regs.kpis, *kpis))
    assert len(credit_model(ModelInputs(full)).lines) == 400
    assert main(["model", "--run", str(_run(tmp_path / "c", full))]) == 0
    over = replace(full, kpis=(*full.kpis, replace(kpis[0], kpi_id="k_over")))
    assert main(["model", "--run", str(_run(tmp_path / "d", over))]) == 1


def test_a_model_without_an_ltm_still_writes_every_file(tmp_path: Path) -> None:
    regs = example_registers()
    fy = next(p for p in regs.periods if p.period_id == "FY2025")
    undated = replace(fy, start_date=None, end_date=None, day_count=None)  # so no LTM column
    run = _run(tmp_path, replace(regs, periods=(undated,), pro_forma=()))
    assert main(["model", "--run", str(run)]) == 0
    data = _model(run)
    assert data["house"]["ev"]["reason"] == "NOT_APPLICABLE"
    assert data["generated_at"].endswith("+00:00")
    text = (run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")
    assert "\nHost-computed Model (`rbot model`): no LTM column, so no house view.\n" in text
    tables = _tables(run)
    assert tables["snapshot.capital_structure_totals"].columns[0] == "line"
    assert tables["snapshot.ebitda_adjustments"].columns[0] == "line"


def test_without_a_ytd_the_pytd_and_ytd_slots_show_older_years(tmp_path: Path) -> None:
    years = _regs(fy={f"FY{y}": {"revenue": 100 + y} for y in (2017, 2018, 2019, 2021, 2022)})
    run = _run(tmp_path, years)
    assert main(["model", "--run", str(run)]) == 0
    rows = _rows(_tables(run)["snapshot.financial_columns"])
    slots = {r["slot"]: r["column_id"] for r in rows}
    assert (slots["PYTD"], slots["YTD"], slots["FY"]) == ("FY:FY2017", "FY:FY2018", "FY:FY2022")


def test_an_add_back_with_no_row_on_the_column_is_not_in_the_adjustments(
    tmp_path: Path,
) -> None:
    regs = example_registers()
    old = next(b for b in regs.addbacks if b.addback_id == "run_rate_cost_savings")
    new = replace(old, addback_id="synergies", label="Synergies")  # a FY2023 row only
    run = _run(tmp_path, replace(regs, addbacks=(*regs.addbacks, new)))
    assert main(["model", "--run", str(run)]) == 0
    lines = [r["line"] for r in _rows(_tables(run)["snapshot.ebitda_adjustments"])]
    assert not any("Synergies" in x for x in lines)
    assert any("Run-rate cost savings" in x for x in lines)


def test_listed_equity_and_no_ev_basis_in_the_totals(tmp_path: Path) -> None:
    equity = table(
        "cp1.equity_value", EQUITY, [["12,000", "2026-10-02", "USD", "MILLIONS", "[C1]"]]
    )
    cp1 = cp1_handoff(example_registers(), [equity])
    run = _run(tmp_path / "a", example_registers(), cp1)
    assert main(["model", "--run", str(run)]) == 0
    assert _model(run)["house"]["ev"]["inputs"]["market_cap"] == "12000"
    totals = {r["line"]: r for r in _rows(_tables(run)["snapshot.capital_structure_totals"])}
    assert totals["Equity"]["basis"] == "listed equity value"
    bare = _run(tmp_path / "b", example_registers(), multiple="—")
    assert main(["model", "--run", str(bare)]) == 0
    totals = {r["line"]: r for r in _rows(_tables(bare)["snapshot.capital_structure_totals"])}
    assert totals["Equity"]["basis"] == "—"


def test_an_uncited_source_is_kept_as_written(tmp_path: Path) -> None:
    lines = cp1_handoff(example_registers()).splitlines()
    lines = [line.replace("| [C3] |", "| S3 |") for line in lines]
    run = _run(tmp_path, example_registers(), "\n".join(lines))
    assert main(["model", "--run", str(run)]) == 0
    revenue = next(x for x in _model(run)["lines"] if x["line_id"] == "revenue")
    fy = next(c for c in revenue["cells"] if c["column_id"] == "FY:FY2025")
    assert fy["sources"] == [
        {"module": "CP-1", "citation_id": None, "source": "S3",
         "locator": "10-K FY2025, Item 8 and quarterly data", "excerpt": None}
    ]  # fmt: skip


def test_missing_front_matter_shows_a_gap_and_the_run_is_required(tmp_path: Path) -> None:
    text = cp1_handoff(example_registers())
    text = text.replace("issuer_id: EGC\n", "").replace("analysis_date: 2026-10-02\n", "")
    run = _run(tmp_path, example_registers(), text)
    assert main(["model", "--run", str(run)]) == 0
    front = parse((run / "handoffs" / "MODEL.md").read_text(encoding="utf-8")).front_matter
    assert (front["issuer_id"], front["analysis_date"]) == ("—", "—")
    with pytest.raises(SystemExit):
        main(["model"])


def test_pf_limitations_carry_their_codes(tmp_path: Path) -> None:
    regs = example_registers()
    pf = regs.pro_forma[0]
    odd = replace(pf, adjustment_id="odd", metric_id="goodwill")
    both = replace(pf, adjustment_id="both", metric_id="ebitda")
    run = _run(tmp_path, replace(regs, pro_forma=(*regs.pro_forma, odd, both)))
    assert main(["model", "--run", str(run)]) == 0
    codes = {row["code"] for row in _rows(_tables(run)["model.limitations"])}
    assert {"PF_NOT_APPLIED", "PF_DOUBLE_COUNT"} <= codes


def test_the_maturity_wall_sorts_a_year_by_facility(tmp_path: Path) -> None:
    regs = example_registers()
    facilities = tuple(
        replace(f, maturity_date="2029-06-30") if f.facility_id == "tlb" else f
        for f in regs.facilities
    )
    run = _run(tmp_path, replace(regs, facilities=facilities))
    assert main(["model", "--run", str(run)]) == 0
    rows = _rows(_tables(run)["model.maturity_wall"])
    assert [r["facility_id"] for r in rows if r["fiscal_year"] == "2029"] == [
        "ssn29",
        "sun29",
        "tlb",
    ]


def test_sources_are_cut_only_past_eight() -> None:
    model = credit_model(ModelInputs(example_registers()))
    first = model.lines[0]

    def with_sources(count: int) -> CreditModel:
        sources = tuple(SourceRef(f"S{n}", "", "1") for n in range(count))
        line = replace(first, cells=(Cell(Decimal(1), sources=sources), *first.cells[1:]))
        return replace(model, lines=(line,))

    assert sources_cut(with_sources(8)) == []
    assert [x.code for x in sources_cut(with_sources(9))] == ["SOURCES_CUT"]
```

- [ ] **Step 4: Run the mutation gate**

Run: `bash scripts/mutate_model.sh > /tmp/mutation.txt 2>&1; grep -c ': survived$' /tmp/mutation.txt` (about 60 minutes on the 10-core verification machine under load; the first line is the workspace path).
Expected: `178`, and every survivor (`grep ': survived$' /tmp/mutation.txt`) is in the list of `docs/model/mutation.md` (next step). A survivor not in the list is a new test gap: kill it with a test, never by adding it to the list; a listed mutant the run kills is fine (drop it from the list).

- [ ] **Step 5: Write the mutation record**

`docs/model/mutation.md`:

````markdown
# Mutation record — the Model

`bash scripts/mutate_model.sh` (mutmut 3.7.0) on `rbotlib/model/`, 2026-10-11: 9424 mutants, 9243 killed, 3 timed out (killed), 178 survived. Every survivor is below, by why it is not killed; a survivor of a later run that is not listed is a test gap to kill, never an entry to add. Entries read `` `<module>.<function>` <mutant numbers> `` (mutmut's `rbotlib.model.<module>.x_<function>__mutmut_<n>`).

- **P** (19), reachable only with projected columns or a rate deck: the unallocated line's parts and total, the projected interest bridge, the deck date (Plan 13 brings back caos's projection tests, which reach them): `assemble._interest_closes` 10, 11, 19, 25; `layout._debt_specs` 13, 14, 15, 18, 27, 34, 35; `layout._specs` 70; `layout._unallocated` 2, 3, 10, 11, 14, 22; `layout.layout` 48.
- **E1** (4), dividing by a sign of +1 or -1 multiplies by it: `_cells.calc` 19; `assemble._sum` 8, 13; `metrics._total` 7.
- **E2** (15), `zip(..., strict=...)` over sequences the code already makes equal in length: `assemble._limitations` 4, 7, 8; `output._line` 46, 49, 50; `output._rows` 4, 7, 8; `reader.rows` 30, 33, 34; `run._rows` 4, 7, 8.
- **E3** (9), UTF-8 spelled `UTF-8`, or the platform default, which is UTF-8 on the work machine and macOS: `run.read_handoff` 4, 6, 17; `run.run_model` 202, 204, 210, 216, 218, 227.
- **E4** (7), `closed=None` is as falsy as `closed=False`: `house_inputs._debt_like` 5; `house_inputs._equity` 36; `house_inputs.check_entity_profile` 17; `inputs._facility` 5, 98; `inputs._kpi` 45; `inputs._period` 52.
- **E5** (5), `format(x, "F")` and `format(x, "f")` print a finite Decimal alike: `layout._decimal_text` 6; `output._decimal` 5, 7; `snapshot.display` 17, 19.
- **E6** (10), a path differing only in letter case: macOS file systems ignore case (a case-sensitive file system kills these through the same tests): `run.run_model` 6, 14, 19, 21, 22, 207, 214, 222, 224, 225.
- **E7** (9), argparse help text: `run.add_command` 3, 5, 8, 9, 10, 14, 18, 24, 25.
- **E9** (3), `\N{em dash}` and `\N{EM DASH}` name the same character: `house_inputs._identity` 17; `run.run_model` 155, 165.
- **E10** (18), `display` formats a money amount and an unknown unit alike (only multiples, percentages and days are rounded): `run._analysis` 7, 13, 14, 17, 23, 24; `snapshot._adjustment_row` 22, 25, 26; `snapshot._total_row` 2, 5, 6; `snapshot.capital_structure` 34, 37, 38; `snapshot.maturity_wall` 18, 21, 22.
- **E11** (1), the slug is case-folded first, so stripping `X` as well as `_` strips nothing more: `house._slug` 7.
- **E12** (4), `calc` takes no basis from its parts, so the parts' basis is never read: `house._adjusted_debt` 10, 12, 13, 14.
- **E13** (4), the mixed-separator branches refuse every figure on which `find` and `rfind` differ: `reader._separated` 4, 11, 13, 15.
- **E14** (1), both sides of the vocabulary match go through `_key`, so any separator spelling matches alike: `reader._key` 5.
- **E15** (4), a four-digit end year falls back to the last four-digit run, which is the same year: `reader._end_year` 4, 7, 8, 9.
- **E16** (3), the fiscal-period key is compared only with other keys from the same function: `inputs._fiscal_period` 6, 7, 8.
- **E17** (1), `ensure_ascii=None` is as falsy as `False`: `output.dumps` 4.
- **E18** (3), the display context: the default context also rounds half-even, and a display figure has far fewer than 28 digits: `snapshot.display` 2, 10, 12.
- **E19** (4), a cell for a missing column is shown as a gap whatever its reason: `snapshot.shown_cell` 2, 4, 5, 6.
- **E20** (2), a PF-LTM column's kind is `PF_LTM` either way: `snapshot.financial_columns` 15, 16.
- **E21** (1), the last two lines of the Model are both in band 12: `snapshot.metrics` 24.
- **E22** (7), the Equity basis label for a missing EV basis is the gap either way; `shown` other than `debt` or `share` prints no multiple, as `amount` does: `snapshot.capital_structure_totals` 91, 153, 165, 166, 200, 212, 213.
- **E23** (5), a payment rank is set on every facility line, so the no-rank cell is never built: `snapshot.capital_structure` 17, 18, 19, 20, 21.
- **E24** (1), maturity rows are unique by (year, facility), so sorting by the whole row orders them alike: `snapshot.maturity_wall` 24.
- **E25** (1), the notes map's values are never read, only its keys: `assemble._limitations` 10.
- **E26** (2), the debt band's first line is always a facility, a rank subtotal or the unallocated line, each of which sets `counted` before it is read (and `None` is as falsy as `False`): `assemble._summed` 2, 3.
- **E27** (3), the layout draws no growth line for a corporate or eliminations segment, so the metric frame's exclusion of their growth never reaches the Model: `assemble.credit_model` 63, 64, 75.
- **E28** (2), without an opening day there is no opening stack to check against; a facility with a row ending on the opening day is in the opening stack either way: `debt._issued_after` 4, 13.
- **E29** (5), the sparse cover's `tiled` flag is read only together with a figure for the parts, which these paths never have; past the last period start the cover ends either way; `""` is as falsy as `None`: `history._cover` 4, 21, 32; `history._parts` 6; `history._step` 25.
- **E30** (3), a subtotal reads its parts, never its key; every part of a rank subtotal is a facility key with the same missing reason; summing Decimals from an int 0 gives the same Decimal: `layout._rank_specs` 24; `layout._revenue_cell` 11; `layout._subtotal` 13.
- **E31** (1), a one-day span is never a whole month, so tightening the bounds check changes no result: `periods._whole_months` 7.
- **U** (21), unreachable defensive branch: the input that reaches it cannot occur (every Model notes `NO_PROJECTIONS`; every looked-up line exists; openpyxl always returns a worksheet; parsed cells hold no line break; units are a closed vocabulary): `output._markdown` 2, 4; `output.model_md` 34, 35, 36; `snapshot.financials` 14, 15, 16, 17; `snapshot.line_of` 3; `snapshot.money_label` 2, 4, 5; `snapshot.summary` 30; `snapshot.unit_label` 21, 22, 23, 24, 28; `xlsx._sheet` 4, 5.
````

- [ ] **Step 6: Run the tests and every gate**

Run: `uv run pytest` (with `RBOT_CORPUS_ROOTS` unset), then the gate commands of the Global Constraints.
Expected: `669 passed, 112 skipped` (448 Model tests passed, 2 Model corpus tests skipped on top of Plan 02's 221 passed, 110 skipped), coverage 98.80% (floor 80%); every gate exits 0.

- [ ] **Step 7: Commit and measure the PR**

```bash
git switch -c build/03f2-mutation
git add scripts/mutate_model.sh pyproject.toml uv.lock tests/model/test_house_detail.py tests/model/test_golden_outputs.py tests/model/test_reader_edges.py tests/model/test_inputs_edges.py tests/model/test_house_inputs_edges.py tests/model/test_outputs_edges.py docs/model/mutation.md
git commit -m "model: mutation gate, survivor-killing tests and the mutation record

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03f1-corpus bash scripts/check_pr_size.sh
```

Expected: `714 changed lines (limit 800)`.

Report: `Not verified:` the gate is not in CI (it takes most of an hour): run it before merging any change to `rbotlib/model/`. Survivors classed inherited are caos's own test gaps, reproduced, not fixed; those classed projection-only become reachable with Plan 13.


---

### Task 26: Corpus regression

**Files:**
- Create: `docs/corpus-runs/2026-10-11-plan-03-corpus-regression.md`

**Interfaces:**
- Consumes: everything above; the owner's corpus roots.
- Produces: the regression record Plan 03 closes with (interfaces spec §12.4 keeps records under `docs/corpus-runs/`). Plan 03 adds the `MODEL` host step, not a module or a Pathway, so there is no proxy-run scorecard and no A/B (§12.6–12.7); `rbot model` needs a CP-1 Handoff, which no proxy run writes before Plan 05. The record covers every deterministic corpus check. It is the last commit on PR 03F2's branch.

**Agent:** `mx-scaffold`.

- [ ] **Step 1: Re-run the whole corpus suite, required**

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
uv run python rbot/scripts/rbot.py corpus verify | tail -1
RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov | tail -1
RBOT_REQUIRE_CORPUS=1 uv run pytest | tail -2
```

Expected: `exit 0`; `113 passed, 668 deselected`; `781 passed` with coverage ≥ 80% (measured 98.80%).

- [ ] **Step 2: Write the regression record**

`docs/corpus-runs/2026-10-11-plan-03-corpus-regression.md`:

````markdown
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
| `test_model_from_cp1_handoff_fixture` | 1 | CZR LTM to 30 June 2026: revenue 11,648; Reported EBITDA 3,255; SSIM = Structuring EBITDA 3,592 (every add-back realized); PF interest 776; cover 4.63x; SSIM Multiple 3.26x; EV 28,736.0 at the Run Brief's 8.0x; senior secured debt 9,385, unsecured 2,319; maturity wall 2028 to 2037; no reconciliation fault; limitations `PF_LTM_EQUALS_LTM`, `CP1D_NOT_READ`, `NO_PROJECTIONS`, `MATURITY_NOT_STATED` |

With no corpus roots, the two CZR checks fail (not skip) naming the unresolved root. Full suite with the corpus required: 781 passed, coverage 98.8%.

## Rulings applied

- Amendment A10: Plan 02's CZR expectations take the Model's ids; `carrying_value` and CP-1's total debt are book values (the carrying amount as filed: CEI Senior Secured Notes due 2030 1,987, not the 2,000 face); pro forma rows are not sign-normalised (PF cash interest -213).
- Quality-adjusted EBITDA is not computed: under §6.5 a `Rejected` add-back counts as unrealized, so it would always equal SSIM EBITDA.

`Not verified:` a CP-1 Handoff written by a model (Plan 05) and `rbot model` on it inside a proxy run (Plan 06); Copilot behaviour and GPT models.
````

- [ ] **Step 3: Run the gates, commit on PR 03F2's branch and measure the PR**

Run the gate run. Then:

```bash
git add docs/corpus-runs/2026-10-11-plan-03-corpus-regression.md
git commit -m "corpus: Plan 03 regression record (deterministic Model checks)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
BASE_REF=build/03f1-corpus bash scripts/check_pr_size.sh
```

Expected: every gate exits 0; `739 changed lines (limit 800)` for PR 03F2 with this record.

Report: `Not verified:` a CP-1 Handoff written by a model and `rbot model` inside a proxy run (Plans 05–06); Copilot behaviour and GPT models.


---

## Self-review against the spec

| Requirement | Where |
|---|---|
| §13 row 03: port of `_cells`, `frame`, `history`, `statements`, `debt`, `metrics`, `layout`, `assemble` (projection excluded, Plan 13) | Tasks 1–19 |
| §6.1 `inputs.py` reading `rbotlib.handoff.Table`s with the caos `_exact` figure rules; `ModelInputError` naming table, row and column; Decimal precision 38 | Tasks 2–3 (`reader`, `registers`, `inputs`) |
| §6.2 `model.json` (`rbot-model/1`), every cell a figure or a reason, limits 64 columns / 400 lines / 8 sources | Task 23; limits tested in Task 25 |
| §6.3 bands, lines, metrics; port additions `gross_profit_growth`, `debt_like:<item>` (and `secured_debt`, which §6.4's Senior debt reads) | Tasks 14, 16, 18, 21 |
| §6.4 snapshot slots and the financials mapping | Task 22 |
| §6.5 house view and PF-LTM (quality-adjusted EBITDA dropped by ruling) | Task 21 |
| §6.6 exact inputs: CP-1 registers, `cp1.instrument_identity`, `cp1.equity_value`, `cp1.entity_profile`, CP-1D, Run Brief | Tasks 3, 20 |
| §6.7 `model.xlsx` (openpyxl, record 0003) | Task 23 |
| §6.8 `rbot model --run`: exit 0 with limitations, 1 naming the malformed input, idempotent `model.json` | Tasks 23–24 |
| §3.2 the `MODEL` tables | Tasks 22–24 |
| `docs/model/enums.md` | Task 20 |
| Money code: Hypothesis property tests; mutation gate with survivors killed or justified | Tasks 7, 8, 10, 13, 19, 21; Task 25 |
| §12.5 row 03: `test_model_on_caos_fixture`, `test_model_from_cp1_handoff_fixture` (with the corpus anchor check); the cash-flow goldens move to Plan 13 with `cash_flow.py` (ruling) | Task 24 |
| Amendment A10 (Plan 02 expectation ids) | Task 24 |
| Last task: corpus regression | Task 26 |


---

## Owner actions after Plan 03

- Review and merge PRs 03A1–03F2 in order (24 stacked PRs; each states its size).
- Keep caos commit `5c3cd52f` reachable: the port kit rebuilds from it.
