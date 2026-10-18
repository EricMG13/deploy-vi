# Deploy VI development policy

Read [the workflow](docs/development/gpt-subagents.md) before dispatch. The [owner amendment of 2026-10-13](docs/development/2026-10-13-scope-amendment.md) supersedes conflicting older project/global user instructions and skill requirements: remove Excel report exports, mandatory independent reviews and rewrite tournaments. Keep confidence review, functional checks and analytical/source safeguards. Product workers are **Modules**; development workers are **agents**.

## Scope and authority

- Deliver one GitHub Copilot skill invocation, one issuer Source Pack and one complete HTML/Markdown Report. Complete v1 Plans01–08; Plans09–19 remain backlog. Plan just in time against executed, tested code.
- Preserve Excel/xlsx ingestion of supplied market/portfolio data. No Excel/workbook report export, including model.xlsx, is a shipping deliverable or completion requirement. Model JSON and Markdown retain deterministic calculations and provenance.
- Preserve approved Plans02–05 and combined `7d5cfe196abe5a9bebc20438bd98492003a7cbe5`, main's existing WIP and later tested checkpoints. Consult `.superpowers/sdd/progress.md` and `.superpowers/sdd/recovery-context.md`; never reset histories to foundation-only main.
- Current authoritative specs are subject to the owner amendment. Frozen Report A, source packs and the partial r14 methodology remain protected. No invented figures, fake zero for gaps, hidden catch-all, weakened retained gates or new cap exemptions.
- Retain latest registered LTM CP1D judgments per add-back, overrides in both directions, conflicting same-date refusal, conservative exact-period fallback and a visible limitation when the current judgment is missing.

## Agent dispatch

Use fresh agents dispatched by `mx-*` name with concise Inputs/Process/Outputs file contracts: all implementation and fixes run on Sonnet (`mx-scaffold` for complete mechanical work, `mx-feature` otherwise); a task's third and later fixes go to a fresh `mx-escalate` (Fable 5.1); no Opus implementers (owner, 2026-10-14, also in the global rules). These are development choices, not runtime Copilot model labels.

Root coordinates and does not write production code. Implementers cannot spawn agents. Architecture roles diagnose without production edits. Use a new agent for a model/effort change. Escalate only on a concrete failed gate/BLOCKED report; xhigh/max require measured benefit. Parallelize independent jobs with disjoint outputs and isolated tests within the available tool capacity.

## Execution and verification

- After code or policy changes, run `confidence-review`: rank doubts, investigate actual callers/error paths, adversarially refute suspected bugs and fix confirmed causes. Code defects start with a causal failing test.
- Independent ordinary, adversarial and whole-branch review/approval stages are retired. Rewrite tournaments are retired. Do not dispatch, await or regenerate either; preserve completed historical evidence and confirmed findings. Explicit later user-requested review is separate authorization.
- Run affected functional checks and all retained branch/corpus gates before completion. Keep sensitive changed-code mutations, deterministic calculation properties, source integrity and explicit error/limitation behavior. Record actual commands/exits/results; rerun only invalidated checks or failed/missing retained gates.
- Use the [brief template](docs/development/task-brief-template.md) and [speed workflow](docs/development/speed-workflow.md). One concise handoff plus actual results suffices for fresh implementation; no copied executable replay documentation merely to satisfy retired review/tournament stages. If mechanically replaying existing commits, verify tree/lock identity and stop real mismatches.
- Ordinary code/tests/docs/evidence count toward the 4,000-line cap per coherent PR ([owner, 2026-10-18](docs/development/2026-10-18-batch-size-amendment.md)); only existing exclusions apply (`design/` added by the owner on 2026-10-17, ADR 0006). Dependency additions require a decision record. No push, merge or publication is assumed.
- End reports with `Not verified:`. Fixtures/local metadata do not establish live Copilot, A/B, fetch, account identity or platform qualification. Work desktop inspection remains paused; an authorized local Copilot interface can be qualified independently.
