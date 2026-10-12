# A/B rubric for module rewrites

Interfaces spec section 12.7. A rewritten module ships only when its B side does not lose to the r14 original (A) on the analytical-depth rules of `rbot/canon.md` (ADR 0003). The controller runs both sides and the graders as Claude Code subagents; `scripts/ab_grade.py` does the mechanical parts. Graders never see which side is the rewrite.

## Sides

- **A**, the r14 original: a fresh subagent receives `reference/deploy-v-r14/skills/<m>/SKILL.md` (and the references it names), `reference/deploy-v-r14/CANON_SHARED.md`, the run's prepared sources and the same upstream Handoffs, and the Run Brief, converted with `uv run python scripts/ab_grade.py to-r14 --in <Handoff> --out <A-inputs>/<ID>.md` (the Run Brief as `<A-inputs>/run-brief.md`: B reads it for the Transaction Summary, the tranche ids, Primary, the portfolios and the analyst, so A must too), with the instruction to ignore the invocation, file name, integrity and export machinery and to write Markdown only.
- **Known difference between the sides.** The conversion maps known registers to the names and headings in the frozen r14 SKILL/schema references (including CP-1's Model Period/Account/Debt registers, CP-1B's Model Comparator, CP-3's RV Table and Preference Decision Table). It preserves every source row and column. A Deploy VI-only host table has no r14 counterpart and retains its explicit id; graders are given both methods and the same complete upstream data, and the controller records any resulting schema difference. X and Y blinding hides the file names only: A writes r14's six sections and B Deploy VI's four, so a grader can often tell the sides apart.
- **B**, the rewrite: the module's dispatch message (interfaces spec section 10.5), unchanged.

## Criteria (each 0 to 3: 0 absent, 1 weak, 2 adequate, 3 strong)

| Criterion | What earns a 3 |
|---|---|
| D1 | Every step of the module's method is visibly done, not only its tables filled. |
| D2 | Every material conclusion is a chain: evidence and its citation, the risk mechanism, the creditor implication. |
| D3 | The strongest supported counter-argument is stated with what would make it win. |
| D4 | Downside is causal and time-aware: starting condition, first break, financial transmission, consequence, trigger. |
| D5 | Disagreements across sources, periods, definitions and upstream Handoffs are reconciled explicitly, or kept as gaps. |
| D6 | No framework, score or label that does not change the conclusion. |
| G | Each gap names the missing data, its cause, its effect on the output and the source that would lift it; no filler. |

Script-measured on B (`ab_grade.py measure`): **C** = anchored citations ÷ citations (`rbot validate --run`), and **F** = filled critical cells ÷ the critical cells the pack's `expectations` say the Front Page tables the module owns should hold (`expected_rows` rows of every critical column; a row the module did not write counts as unfilled; no F for a module that owns no Front Page table). A writes no Deploy VI citations table, so C(A) is not measured and the citation bar is C(B) ≥ 0.95. C is the validator's own anchoring, so it can fail only for a Handoff the validator already refuses (B must exit 0 or 3 under `--run` before it is scored); the owner may drop the line. `score` requires `--f-b` for a module that owns Front Page tables.

## Grader prompt

Each grader is a fresh subagent (`mx-precise`, effort high) given exactly this text, with `<AB>` the A/B folder and `<RUN>` the run folder:

```text
You grade two Handoffs written by two versions of the same credit-research module for the same Source Pack. Read <AB>/X.md and <AB>/Y.md, the method each was given in <AB>/steps-X.md and <AB>/steps-Y.md (D1 asks whether every step of that method was done), and check their claims against <RUN>/prepared/*.txt and the upstream Handoffs in <AB>/inputs/. Do not read any other file.

Score each Handoff 0-3 on each criterion (0 absent, 1 weak, 2 adequate, 3 strong):
D1 every step of the module's method completed, not only its tables filled.
D2 every material conclusion chained: evidence and citation, then the risk mechanism, then what it means for creditors.
D3 the strongest supported counter-argument stated, with what would make it win.
D4 downside causal and time-aware: starting condition, first break, financial transmission, consequence, trigger.
D5 disagreements across sources, periods, definitions and upstream Handoffs reconciled explicitly, or kept as gaps.
D6 no framework, score or label that does not change the conclusion.
G each gap named with its cause, its effect and the source that would lift it; no filler.

Reply with one Markdown table, columns: criterion | X | Y | reason (one line per score), with rows D1, D2, D3, D4, D5, D6, G in that order; then one line per Handoff naming its single largest weakness.
```

## Resolution and pass bar

`uv run python scripts/ab_grade.py steps --module <ID> --folder <r14 skill folder> --order <AB>/order.json --out <AB>` writes `steps-X.md` and `steps-Y.md` before grading, and `uv run python scripts/ab_grade.py score --order <AB>/order.json --sheets <AB>/grader-1.md <AB>/grader-2.md --module <ID> --expectations <pack expectations> --c-b <C(B)> [--f-b <F(B)>]` maps X and Y back to A and B. Two graders that differ by more than one point on any criterion need a third (exit 3; the same prompt, a fresh subagent), and the median of three decides; otherwise the mean of two.

B passes when every line holds: ΣD(B) ≥ ΣD(A); no criterion with D(B) < D(A) − 1; C(B) ≥ max(0.95, C(A)); G(B) ≥ G(A); F(B) ≥ 0.90 where F applies (exit 0; 1 when a line fails).

## Record

`docs/ab/<YYYY-MM-DD>-<ID>-<pack>.md`: the pack, the run folder, both sides' model labels and wall times, the order drawn, every grader sheet verbatim, the resolved scores, C(B) and F(B), each pass-bar line and the verdict. A module that fails is revised (its contract's `process`), re-rendered and re-run; every round's record is kept.
