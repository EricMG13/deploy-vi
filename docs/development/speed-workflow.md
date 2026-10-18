# Development speed workflow

Apply [the canonical workflow](gpt-subagents.md) and [owner amendment](2026-10-13-scope-amendment.md). Root coordinates; fresh implementers do not spawn. Mandatory independent reviews and rewrite tournaments are retired. Preserve historical findings/evidence without regenerating their documents.

## Before implementation

Record the exact actual predecessor, protected inputs, read/write sets and deliverables in a concise [ICM brief](task-brief-template.md). Trace public callers, qualification guards, error/log paths and shared state before editing. Checks must cover valid and malformed/missing/conflicting input, guards before protected reads/mutations, ordering/interruption/concurrency where relevant, source preservation and honest gaps. Preserve latest registered LTM judgments, bidirectional overrides and conservative visible fallback.

Deliver one GitHub Copilot invocation and one issuer HTML/Markdown Report. Keep Excel input ingestion; remove Excel report exports. Do not write future dependent plans ahead of executed/tested predecessors.

## Verification and evidence

Code defects begin with a causal failing test. Run confidence-review after edits, investigating/refuting every doubt before patching confirmed causes. Run affected functional checks, sensitive changed-code mutations and deterministic-calculation properties. Rerun invalidated checks; unchanged matching evidence can be reused with an explicit rationale. All retained branch/corpus gates remain at integration; no independent approval stage or tournament is required.

Use one compact handoff linking actual command outputs/results. Keep real elapsed/count/exit information when captured; missing phases are unmeasured, not zero. Do not retrospectively reconstruct timings or add concurrent intervals into fake wall time. Completed old review/tournament/replay records remain historical. Fresh implementation does not need duplicated full-code executable replay documents; actual commits/diffs/tests are the working evidence. Mechanical replay of existing commits still checks exact tree/lock and stops mismatches/failed gates.

Budget code/tests/docs/evidence plus repair headroom within4,000 ordinary changed lines per coherent PR ([owner, 2026-10-18](2026-10-18-batch-size-amendment.md)). Only existing lock/reference/golden-document/synthetic-corpus/design exclusions (design: ADR 0006) apply. External/ignored evidence is disclosed and counted in its actual scope; retain whole oversize historical material unshipped, without slicing/exemptions. Keep unrelated main WIP out of the scope. New dependencies require a decision record.

`scripts/dev_evidence.py` may capture actual commands/identities/counts where installed; it is optional supporting machinery, not an approval source. Do not expand evidence work merely to replace retired review/tournament stages. Preserve sources, accurate errors and qualification limits.

## Dependencies

Once06.9 is tested complete, runtime metadata/install06.10→06.11 may run alongside proxy/scorecards06.12→06.13→06.14→06.15 with disjoint outputs/isolated tests. Check actual predecessor completion before each task, integrate retained gates at06.16, then execute07/08. The work desktop pause remains in force; local GitHub Copilot qualification is separate.

Not verified: task execution, gate results, live Copilot/A-B/fetch/platform qualification or speed merely from using this workflow.
