# Deploy VI Plan06 Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the v1 production controller and installed skill around approved Modules, with truthful state, continuation, proxy evidence and scorecards.

**Architecture:** One guarded state engine owns complete run records; dispatch/accept/host adapters add causally checked transitions without recreating approved financial logic. Approval retains its existing validation/rename behavior. Runtime and repository proxy call the same production controller; report fields remain unset until Plan07 provides rendering.

**Tech Stack:** Python >=3.11; standard library; pinned openpyxl==3.1.5 and pypdf==6.19.0; existing uv/Ruff/mypy/pytest/Hypothesis gates.

## Global Constraints
- Exact initial base: `7d5cfe196abe5a9bebc20438bd98492003a7cbe5` (approved combined02–05); preserve main WIP, sources, approved histories and frozen Report A.
- Binding interfaces `docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md` §§8–10/12–13 and host §§3/6–7; audited obligations in main `.superpowers/sdd/plan-06/requirements.md` remain binding.
- v1 order: `CP-0 → CP-1 → CP-1A → CP-1B → CP-1D → MODEL → CP-2 → CP-3 → FIT → CP-5 → CP-6`; only FULL_CREDIT_ASSESSMENT/full. Plans09–19 stay backlog.
- State schema `rbot-run-state/1`; pending/running/accepted/blocked/failed/skipped; QA Pass/Restricted/Blocked; validate0/1/2/3/4 taxonomy unchanged; Handoff cap98,304bytes.
- Source bytes unchanged; no invented figures/zero-for-gap/hidden fallback/weakened gates/new cap exemptions. Latest registered LTM CP1D judgment policy, both-direction overrides and conflicting-same-date refusal stay unchanged.
- Every independently reviewed implementation scope ≤800 changed lines including ordinary docs/tests and untracked deliverables. Only existing *.lock/reference/**/tests/golden/**/documents/**/tests/corpus/synthetic/** exclusions apply. This plan is a separate documentation scope; report lines count in06.1 evidence scope.
- Fresh explicit native GPT agents follow AGENTS/workflow ICM; root coordinates, implementers do not spawn. Each task needs causal red/green, affected gates, confidence review and nontrivial post-edit tournament; sensitive ordering/security/money gets independent adversarial review. No push/merge/publication assumed.
- Plan06 execution ends before07/08 planning. Actual worker-written A/B and local proxy evidence cannot establish installed Claude/GPT work-Copilot acceptance; capability probe is unmeasured, budget provisional51,200bytes.

## Status and file responsibilities
Only06.1–2 below are executed.06.1 initial and round1 adversarial refusals remain preserved history; both fresh final repaired-scope reviewers approved the final source tree, then root packaged its identical tree.06.2 independent reviews remain outstanding.06.3–16 remain an explicit draft task map, without code-bearing executable/replay instructions or verification claims. Write each next executable section against its actual reviewed predecessor; split before800 lines, preserve causal tests with each boundary.
`rbotlib/state.py` stores/checks records and public failure/skip edits; future `runs.py` creates/discovers; `dispatch.py` confines message inputs; `accept.py` records independent validation/history; `next.py` owns dependency selection; `host.py` integrates genuine host completion; `resume.py` revalidates; runtime SKILL/version/install files serve installed users; repository proxy and scorecard remain tools under scripts/.

### Task06.1: Checked state storage and public failure/skip command — executed
**Files:** Create `rbot/scripts/rbotlib/state.py`, `tests/test_state.py`, `tests/test_state_logging_authority.py`; modify `rbot/scripts/rbotlib/cli.py` registration and guarded logging lifecycle.
**Consumes:** `inventory.output_path(run: Path, relative: str)→Path`, `fsio.write_atomic(path: Path,text: str)→None`, approved Approval's `.approve.lock` exclusion, existing CLI log preflight plus explicit state `log_run_path` ownership guard (strict normalized run envelope plus checked state identity).
**Produces:** `Record=dict[str,Any]`; `read(run: Path)→Record`; `validate(record:Record,run:Path)→None`; `update(run:Path,change:Callable[[Record],None])→Record`; `set_status(run:Path,step:str,status:str,reason:str)→Record`; registered `state --run [--set STEP=STATUS --reason TEXT]`, exit0 JSON or named1.
**Boundary:** existing strictly resolved production `<pack>/rbot-runs/<run_id>` only; selected traversal and original final-logger spelling must map to it. Links entered or targeting inside the physical pack refuse; aliases above pack and ordinary existing child/.. spellings work; bootstrap fields honestly nullable and plan empty/CP-0-only. Public setters allow pending→failed/skipped and running→failed with reason. Trusted later owners add validated success, attempts/retries/history. An absent/corrupt/nonregular/mismatched state marker grants no log ownership and creates/appends no log. A valid checked run still logs failed commands as exit1. Current minimal legacy seeds are not promoted; Approval/proxy stay unchanged. Path guards measure static links and stage destination changes; hostile directory races, crash consistency and automatic stale-lock recovery are not promised.

- [x] **Step1: Write causal regression tests.** Exact retained final regression file is linked below; initial command command-missing assertions established red before implementation, and later confidence bugs each have measured red in the report.
Final exact retained causal tests bytes are in [core replay](2026-10-12-deploy-vi-06-state-replay.md) and [additional round2 ownership regressions](2026-10-12-deploy-vi-06-state-logging-replay.md). All are retained and exercised.

- [x] **Step2: Verify red.** `uv run pytest tests/test_state.py -k 'public_state or bad_schema or linked_destinations' --no-cov`: exit1,19 failed/1 deselected because CLI had no state command; later NaN/ancestor/prior-shape red cases are recorded in task report.
- [x] **Step3: Write the checked state engine.** Exact final implementation is linked below:
Final exact checked state engine bytes are in [2026-10-12-deploy-vi-06-state-replay.md](2026-10-12-deploy-vi-06-state-replay.md).

The final common CLI preserves approved callers and Approval rename while the state registration supplies its normalized envelope and checked-state ownership guard. Exact final CLI bytes:
```python
"""`rbot` command line. Each later command lives with its module (`add_command`).

A command given `--run <RUN>` appends one line to `<RUN>/log/rbot.log`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from rbotlib import approve, brief, calc, corpus, fit, grade, inventory, prepare, state
from rbotlib.catalog import check_tree
from rbotlib.contract import ContractError, load_contract
from rbotlib.model.run import add_command as add_model_command
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import check


def _fail(path: Path, exc: Exception) -> int:
    reason = exc.strerror if isinstance(exc, FileNotFoundError) and exc.strerror else exc
    print(f"error: {path}: {reason}", file=sys.stderr)
    return 1


def _validate(args: argparse.Namespace) -> int:
    rules = load_rules(args.root)
    path = args.root / "modules" / args.module / "contract.json"
    try:
        contract = load_contract(path, rules)
    except (FileNotFoundError, ContractError) as exc:
        return _fail(path, exc)
    try:
        text = Path(args.handoff).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        return _fail(Path(args.handoff), exc)
    run = Path(args.run_dir) if args.run_dir else None
    code, findings = check(text, contract, rules, run)
    for f in findings:
        if f.code == "run_error":
            print(f"error: {f.message}", file=sys.stderr)
            return code
        print(f"{f.code}: {f.message}")
    print(f"exit {code}")
    return code


def _render(args: argparse.Namespace) -> int:
    rules = load_rules(args.root)
    folder = args.root / "modules" / args.module
    try:
        text = render_module(load_contract(folder / "contract.json", rules), rules)
    except (FileNotFoundError, ContractError) as exc:
        return _fail(folder / "contract.json", exc)
    if args.write:
        (folder / "MODULE.md").write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def _check(args: argparse.Namespace) -> int:
    problems = check_tree(args.root, load_rules(args.root))
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


def _log_path(run: Path) -> Path:
    """Refuse pre-existing unsupported log kinds without opening or creating anything."""
    destination = inventory.output_path(run, "log/rbot.log")
    if destination.parent.exists() and not destination.parent.is_dir():
        raise inventory.RunError(f"{destination.parent}: log parent must be a directory")
    if destination.exists() and not destination.is_file():
        raise inventory.RunError(f"{destination}: log must be a regular file")
    return destination


def _log(run: Path, argv: list[str], code: int) -> None:
    """One line per command in <RUN>/log/rbot.log: time, command, exit (spec section 8.1)."""
    destination = _log_path(run)
    destination.parent.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    with destination.open("a", encoding="utf-8") as log:
        log.write(f"{stamp}\t{' '.join(argv)}\t{code}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rbot")
    parser.add_argument("--root", type=Path, default=RBOT_ROOT, help="the RBOT folder")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="check a Handoff against its module contract")
    v.add_argument("handoff")
    v.add_argument("--module", required=True)
    v.add_argument("--run", dest="run_dir", help="also check citations against this run folder")
    v.set_defaults(run=_validate)
    r = sub.add_parser("render-module", help="print or write a module's MODULE.md")
    r.add_argument("module")
    r.add_argument("--write", action="store_true")
    r.set_defaults(run=_render)
    c = sub.add_parser("check", help="contracts, generated modules, Pathways, Front Pages, budget")
    c.set_defaults(run=_check)
    corpus.add_command(sub)
    inventory.add_command(sub)
    prepare.add_command(sub)
    brief.add_command(sub)
    add_model_command(sub)
    grade.add_command(sub)
    approve.add_commands(sub)
    calc.add_command(sub)
    fit.add_command(sub)
    state.add_command(sub)
    args = parser.parse_args(argv)
    run_dir = getattr(args, "run_dir", None)
    log_run = None
    if run_dir:
        selected = Path(run_dir)
        try:
            guard = getattr(args, "log_run_guard", None)
            if guard is not None:
                selected = guard(selected)
            if selected.is_dir():
                _log_path(selected)
                log_run = selected
        except (OSError, ValueError, RecursionError) as exc:
            return _fail(selected, exc)
    result = 1  # what the log records when the command raises
    try:
        result = int(args.run(args))
    finally:
        if log_run is not None:
            log_run = Path(args.run_dir)
            try:
                _log(log_run, sys.argv[1:] if argv is None else argv, result)
            except (inventory.RunError, OSError) as exc:
                result = _fail(log_run, exc)
    return result
```
- [x] **Step4: Verify green and workflows.** Initial `uv run pytest tests/test_state.py --no-cov`:34 passed,exit0; fix-round `.venv/bin/pytest tests/test_state.py --no-cov`:45 passed,exit0. Required-root affected CLI corpus compatibility370 passed/0 skipped; final named affected suite101 passed/0 skipped. Inline CLI main/log-path tournament incumbent held, six candidates plus incumbent97 passed/2 corpus skipped each; five selected guard mutants killed with isolated passing baselines and byte restoration. `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv lock --check`, `uv run python rbot/scripts/rbot.py check`, suppression checker, scoped complexipy and Bandit all exit0. Report retains exact red/green, compatibility, mutation, confidence and full inline tournament evidence. Initial incumbent update won; fixed CLI main/log-path incumbents held; later unexercised behavior stays listed.
Executed proof: task commit 7ad14b2b0e51329d59e3e7866fbea02c1ab1e110; tree 2020f346df3c5330654abc647141fe44331a408b; uv.lock Git blob 35bf2e7e741576c67c5e2908add759111dd8fabf. Historical failed-scope proof retained. Historical round1 code proof (adversarially refused): repair commit `bb73187a7f0c335f41e1e9a3bdb086f245ce2eea`, tree `af83beb993f82ca91c629fb6b7c1b03202a5afb0`, unchanged uv.lock blob `35bf2e7e741576c67c5e2908add759111dd8fabf`; local artifact only, both repaired-task and whole-Plan06 approvals remain outstanding.
Round2 proof: final code/tests commit `692ca53eb547ad248068b4de04acb492cf5d4dd9`, tree `3bd20d789f686bc3bee6af3a06566cae14de7cf7`; unchanged uv.lock blob `35bf2e7e741576c67c5e2908add759111dd8fabf`, SHA256 `cea4c0f2021ff0048c47e643c828baee104062e64400fb314493ece76fe6cf30`. Final required-root affected414 passed/0 skipped/0 deselected; every complete tournament variant and incumbent145 passed/0 skipped plus full mypy178 files; six guard mutations killed after clean baselines/restoration. Final state/logging matrix44 passed; real200 type variants184 no-write refusals/16 legitimate shapes. Reported commands, confidence, narrow strict-resolution/loop handling and full inline tournament are in staging task-01-fix2-report.md and task-01-fix2-tournament.md. Core code+existing tests774, additional tests210, core replay and new regression replay are separate actual scopes; no exemption. Documentation commits/head/tree are recorded after commit in the report.
- [x] **Step5: Review and replay.** Original ordinary/adversarial source/log/FIFO refusals and round1 static parent-segment/ownership refusal remain above as historical evidence. Both fresh final reports (`main .superpowers/sdd/plan-06/task-01-final-review.md` and `task-01-final-adversarial-review.md`) APPROVE task06.1 at source `8652ce67678ec119ddd6b4101dbfa1227b2703fb`, tree `2b42ed0148703c3d0c8e84800363e4fa4f35fcc7`. Root preserved that source on `codex/06-state-source` and packaged `codex/06-v1` at `013a274d22f8e74f41a0f5351418109a0f237805` with the exact same complete tracked tree and uv.lock blob/SHA256. Main packaging report records the five actual 774/210/249/758/221-line immediate-parent scopes (all size gates exit0), unchanged exclusions and preserved main WIP. This closes06.1 task review/replay only; whole Plan06 is not approved.

### Task06.2: Run creation and unfinished discovery — executed
**Files:** Create `rbot/scripts/rbotlib/runs.py`, `tests/test_runs.py`; update CLI registration, checked post-creation logging and one-line escaped command text.
**Consumes:** `state.read(run:Path)→Record`, `state.validate(record:Record,run:Path)→None`, `state.log_run_path(run:Path)→Path`, `inventory.output_path(run:Path,relative:str)→Path`, `fsio.write_atomic(path:Path,text:str)→None`, authoritative `rbotlib.__version__`.
**Produces:** `create_run(pack:Path,issuer:str|None=None,objective:str|None=None)→Path`; `discover_unfinished(pack:Path,*,now:datetime|None=None)→Path|None`; registered `new-run --pack [--issuer] [--objective]`, exit0 printed canonical run path or cause-labelled1 (including actual resumable path on unfinished refusal).
**Boundary:** canonical selected pack; links at pack/output envelopes and destinations refuse; aliases above selected pack work. Folder-only `unknown` handles omitted/empty/non-sluggable hints; exact hint strings remain data and issuer_id remains null until CP-0. Initial checked state only plans CP-0, zero attempts, nullable analysis/approval/report fields. Markerless directories are reserved collisions, not checked runs. All present candidate markers are checked, including old/completed ones; malformed state/path refuses. Newest eligible unfinished record uses created_at then name as tie-break, includes exactly30days, refuses future creation timestamps and naive supplied clocks; failed/skipped statuses do not filter or change. Independent creation callers hold `.new-run.lock` across discovery and checked publication; bounded5-second wait diagnoses busy/stale locks without forced removal. Failure removes only the owned empty allocation, otherwise names the retained incomplete path. Static confinement does not promise hostile directory replacement or abrupt-crash consistency. Existing Approval args.run_dir rename remains the logger's effective path.

- [x] **Step1: Write causal tests.** Exact final retained tests are in [runs tests replay](2026-10-12-deploy-vi-06-runs-tests-replay.md). Initial22 missing-command/API regressions were written before production; newline-command logging and candidate-path diagnostics each gained a measured failing regression before repair.
- [x] **Step2: Verify red.** `uv run pytest tests/test_runs.py --no-cov`: exit1,22failed (no command/API). After registration, single-line hint logging:4failed/18passed; corrupt candidate path:2failed/2passed/30deselected. Full original stdout remains in main staging report's evidence paths.
- [x] **Step3: Implement checked creation/discovery/logging.** Exact executed final production bytes are in [runs code replay](2026-10-12-deploy-vi-06-runs-replay.md). No unexecuted implementation code is asserted.
- [x] **Step4: Historical producer verification before rejecting reviews.** Required-root affected suite447passed/0skipped/0deselected (includes source-hash-preserving new-run on primary/external verified copies). Global Ruff/format/mypy180files/uv lock/suppressions/complexipy/contracts/Bandit+floor all exit0. Confidence review verified all named doubts and fixed causal newline/path-label defects. Inline sequential no-argument tournament covered seven material functions across four capped passes; actual speed/memory/readability suites each177passed with declared roots, incumbent held. Four isolated ordering/security/age/log mutants killed, each with passing pre/post baseline. No dependencies/exemptions were added.
- [x] **Step5: Local scoped commit.** Actual code/tests commit `ea81e8dd6ee007d9368fa81dc021fae6fffaa36e`, tree `3346d8746096cdb9b9ee2c53d9768380536d99ec`, 655changed lines against its exact predecessor; unchanged lock proof matches06.1. Verified replay/canonical docs are separate ≤800-line scopes. No push/merge/publication. Independent ordinary and adversarial06.2 task approval remain outstanding; do not start06.3 before root accepts this task.


- [x] **Step6: Round1 causal cooperating Approval repair.** Both main task-02-review.md and task-02-adversarial-review.md rejected historical task head `e237107cf36b667f468f189386bab19b1eb6ba74`, tree `3075ddf27cf5ecac6d68bd608cf70f69c479fdc4`, for the same real pending→Pathway rename/discovery race. Preserve original reports/evidence; no03 continuation until fresh approvals. Four real public Approval subprocess barriers first failed on unchanged rejected production: iterator creation/consumption, postlisting directory, postdirectory marker and postread selected path. First three permitted a duplicate; the fourth named a vanished old path as resumable. Repair uses stat disappearance refusal, markerless-directory recheck and a second complete sorted real name enumeration; changed discovery names its cause and requests retry. Original markerless reservations/creator lock/Approval legacy callers remain; no new lock order, auto retry or forced unlock. Official Python3.11 iterator inclusion is unspecified; observed stale enumeration does not claim an actual omitted entry or filesystem-wide transaction/path lease.
- [x] **Step7: Repair verification/skills/local proof.** Runtime repair commit `ab064c4d790a7581d43ca0e7b2e8cb680b763033`, tree `9d1d8d7a045e1016d2968b8db1e4fcc848862b81`,127 immediate-parent lines; complete final runtime code/tests against013a274 count768. Required-root affected504passed/0skipped/0deselected (original affected set plus four new barriers and53 existing CP-0 review-repair tests),56.89s. All actual Ruff/format/mypy180/lock66/suppressions0/complexity15/contracts0/Bandit+floor gates exit0. Confidence review then two capped inline sequential passes retained incumbent; six actual candidates79passed each with exact restoration. Final name-check/unsafe-absence/checked-record/creator-lock mutants killed1/4/1/2, each baseline0→mutant1→restored0. Original witness mechanism copy: genuine Approval0/new-run1/one checked unfinished approved run/sourcehashes unchanged. Exact repaired production/test replay blocks below are executed bytes, with unchanged lock blob/SHA256. Main task-02-fix-report.md/tournament/mutations/drivers retain commands, raw paths and final docs identities/counts. Fresh independent ordinary/adversarial re-reviews remain pending; local commits do not imply approval, push, merge or publication.

## Draft remaining task map — acceptance constraints, no unexecuted code claimed
Each row supplies concrete files/contracts and public-caller proof for later just-in-time executable sections. Interfaces named as proposed are not available yet. No next task starts until root accepts06.2.

### 06.3 CP-0 bootstrap and Approval bridge (after06.2)
Files: `rbotlib/runs.py`, `rbotlib/approve.py`, `tests/test_bootstrap.py`; existing brief/grade remain authoritative. Consume genuine CP-0 validator/brief/grade and shared state lock; produce pre-Approval dispatch/accept readiness seam and renamed state handoff.
Only CP-0 may progress before two-turn Approval. Preserve accepted CP-0 hash/time/history and explicit pending identity lineage through approved rename; rebuild other analysis steps from actual current catalog. Tests drive new-run→inventory→prepare→real CP-0 acceptance→brief edits→grade→approve and log at returned renamed path. Re-Approval refuses. Bootstrap waiting is explicit, never analysis done/render.

### 06.4 Dispatch message confinement (after06.3)
Files: new `rbotlib/dispatch.py`, `tests/test_dispatch.py`; CLI. Produce `dispatch-message --run --module [--findings validate/ID.json]`; consume selected-root Contract.handoff_inputs, prepared index, accepted CP-0 classifications and state.
Persist/print exactly named canon/MODULE/run paths, declared source classes and concrete eligible prepared/image-original paths, required/optional Handoffs, Blocked/missing optional notes, allowed calc/output paths, selected-root validation command and DONE protocol. Resolve “never read another Handoff” as never read an undeclared one. Bootstrap CP-0 reads all prepared sources before classifications. Tests use malicious filenames/content, paths with spaces, explicit root and findings; undeclared/failed optional artifacts stay inaccessible.

### 06.5 Independent accept and retry history (after06.4)
Files: new `rbotlib/accept.py`, `tests/test_accept.py`; dispatch/state/CLI bounded extensions. Produce `accept --run --module` and trusted transition helpers; independently validate actual bytes, never DONE claims.
Latest `validate/ID.json` remains `{exit,findings:[{code,message}],sha256,at}`; immutable attributable attempt records retain actual model/time/exit/anchoring evidence.0 accepted,3 Blocked,2 one malformed retry then failed,4 identity failure immediate,1 named execution failure. Dispatch preparation and actual send must not double-count; resumed running keeps attempt/retry entitlement. Tests include duplicate accept, interrupted preparation/send, wrong run/issuer with CP-0 lineage exception, malformed/size/citation/identity and linked output histories; no unlimited retries.

### 06.6 Ordered dependency selection and next (after06.5)
Files: new `rbotlib/next.py`, `tests/test_next.py`, `tests/test_state_machine_transitions.py`; CLI. Produce `next --run` JSON `{step,kind,command,dispatch}`, carrying explicit --root through every generated command.
Consume actual ordered catalog/contracts and host readers. Select pending/running only; failed/skipped required input skips with named input; blocked required input still dispatches; missing/failed optional input limits without automatic skip. FIT requires CP-3 plus CP-1 and RUN_BRIEF. Fixed option skip strings remain exactly not approved/no prior case/CP-2G not run/no portfolio context where steps exist; absent backlog steps are not inserted. Corrupt state/root refuses. Test public JSON/root/order and exit-sequence properties; pre-Approval wait and terminal done are distinct.

### 06.7 Production MODEL completion (after06.6)
Files: new `rbotlib/host.py`, existing `rbotlib/model/run.py` bounded adapter, `tests/test_host_model.py`. Public model command returned by next must itself advance shared state after genuine success.
Qualify required CP-1/RUN_BRIEF and optional CP-1D from validated state, ignore failed leftover optional bytes with visible limitation, preserve approved Decimal/LTM policy. Track actual attempt/time/QA/hash/reason, require all model.json/model.xlsx/MODEL.md outputs and provenance, preserve actual partial-publication limitation. Tests run the generated command, prove next advances, missing required input cannot accept, failure has named reason, sources stay byte-identical; retain sensitive mutations/property gates.

### 06.8 FIT completion and precise host validation (after06.7)
Files: `rbotlib/host.py`, bounded `rbotlib/fit.py`, new `rbotlib/host_validate.py`, `tests/test_host_fit.py`, `tests/test_host_validate.py` split before800 lines.
FIT honors no-portfolio skip; qualify real CP-1/CP-3/RUN_BRIEF/optional CP-1A and prepared portfolios, not mere file existence. Record successful/failing public command once; Blocked CP-3 remains usable; failed CP-1A ignored honestly. Host Handoff readers validate MODEL/FIT/RUN_BRIEF shapes/identity and relevant model/workbook/fit consistency after edits, with no fake MODULE contracts. Partial output set/forged host Handoff cannot produce acceptance. Preserve money property/mutation coverage.

### 06.9 Resume integrity and interruption replay (after06.8)
Files: new `rbotlib/resume.py`, next/runs adapters, `tests/test_resume.py`, `tests/test_resume_from_each_step.py` in bounded scopes.
Before next, rehash accepted bytes; unchanged preserves history, changed valid gets current hash and note: edited, changed invalid/missing becomes failed with findings/downstream effects. Precise host revalidation handles non-MODULE Handoffs; retain bootstrap identity exception. Interruption at each public module/host/publication boundary matches uninterrupted ordering, pending/running only resumes, terminal failures never retry, approved renamed <=30day discovery never reapproves. Correct old §10.1 Finish cross-reference locally to the next/dispatch loop.

### 06.10 Installed skill and runtime metadata (after06.9)
Files: new `rbot/SKILL.md`, runtime version metadata and version command; `tests/test_runtime.py`. Consume actual production CLI; produce exact `rbot <version> <git sha>` without .git/pyproject/repository imports.
Skill shows classification/cited prefill/full installed menu, two Approval turns and blocked acknowledgement, explicit brief edits/renamed path, unattended next/dispatch/accept/host loop, truthful resume and Plan07 render seam. It never writes credit analysis/Handoffs in ordinary orchestrator mode. Document terminal/write/read/no-subagent fallbacks separately from unmeasured work capabilities; use actual platform Python command. Installed-tree smoke tests run outside source cwd and check provisional51,200byte budget; no runtime model hardcoding.

### 06.11 Runtime-only installers (after06.10)
Files: new `install.sh`, `install.ps1`, `tests/test_install.py`. Copy only runtime rbot/ to personal ~/.copilot/skills/rbot/; no repo/reference/tests/corpus/proxy/private sources.
Temp-directory tests cover spaces, repeat copy, complete skill/version files and outside-repo imports. Installer is skill-copy only, no speculative package/pip setup. PowerShell execution and work-policy Python/pip permission require actual host evidence in08; shell-text review cannot claim Windows execution.

### 06.12 Proxy start and genuine Approval (after06.9)
Files: bounded `scripts/proxy_run.py`, `tests/test_proxy_start.py`. Replace hand-seed/print-only --approve with production new-run/brief edits/grade/approve and returned renamed path.
Adopt nested production run layout under materialised pack, or independently review an explicit internal shared creation seam before preserving old sibling placement; never second state implementation or relocated analyst sources. Transparent simulated analyst edits meet real required fields and acknowledgements. Corpus copy/hash checks and malformed-input failures remain visible; actual production workflow drives proof, unchanged legacy interface tests updated only in this bounded integration.

### 06.13 Proxy continuation and isolated module mode (after06.12)
Files: proxy adapter/tests split as needed. Implement actual next/accept/module/host loop, --continue, --module ID, --model-label and optional --fetch semantics from §12.6.
Modules run from controller's exact persisted dispatch; newest same-pack qualified upstream or declared labelled fixture fallback supplies only declared inputs in isolated mode. No fabricated Handoffs/approval/financial outputs or manual shadow state updates. A requested backlog fetch names unavailable capability. Renderer invocation seam remains honest before07: report fields null, unavailable render named. Causal tests include retry, failed host, renamed discovery and selected model labels.

### 06.14 Measured step/attempt scorecard (after06.13)
Files: new `scripts/scorecard.py`, `tests/test_scorecard.py`; writes `docs/corpus-runs/<date>-<pack_id>-<pathway>-<depth>.md` only from real recorded run evidence.
Per step/attempt status/QA/validate exit, anchored÷total citations, gaps, bytes, times and actual model labels; Model limitations/reconciliation faults. Image-Read anchoring is not invented Yes. Missing timestamp/attempt/measurement is named unknown, never zero. Wrong citation changes measured ratio; forged terminal/file-existence artifact cannot count as accepted. Every report ends Not verified.

### 06.15 Front Page coverage and first real proxy record (after06.14)
Files: scorecard extension, `tests/test_front_page_scorecard.py`, actual primary-pack corpus-run record. Consume required row identities/expected counts and approved host tables; measure filled÷supportable critical cells.
Removing/duplicating Strategy/facility rows lowers/refuses coverage; gaps that sources cannot support remain explained, no fabricated denominator. Execute first genuine worker-written czr-2026q2-primary proxy run with model labels/source hashes and scorecard; fixture replay alone does not qualify Modules or installed Copilot. Native-r14/module A/B qualification still pending from05 stays visible and needs measured model-written evidence.

### 06.16 Integration closure (afterall reviewed06 tasks)
Files: actual integration report/evidence and bounded confirmed repairs. Run every actual CI/local gate including required external+synthetic corpus roots, collected/passed/skipped/deselected counts, source hashes, lock/tree replay, suppression/complexity/security/dependency/secrets/duplication/size and required changed-sensitive mutations.
Fresh independent whole-branch adversarial review uses actual final tree and authoritative requirements; production CLI/proxy must share one state engine. No ahead-of-time07/08 implementation. Retain report.md/html null until07; frozen Report A controls07, actual Claude and GPT installed work-Copilot acceptance and measured capabilities belong08. Run ponytail-review before any separately authorized merge.

Not verified:06.2 independent task approval,06.3–16 code, complete06 branch gates/corpus closure, model-written proxy/A-B qualification,07 rendering,08 installed Claude/GPT Copilot/PowerShell/pip/tool capabilities, measured prompt budget and fetch.06.1 exact committed evidence is in the staging task report.
