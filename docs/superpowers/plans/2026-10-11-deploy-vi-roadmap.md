# Deploy VI — build roadmap (full scope)

**Spec:** [`2026-10-11-deploy-vi-rbot-design.md`](../specs/2026-10-11-deploy-vi-rbot-design.md) · **Interfaces (binding cross-plan contract):** [`2026-10-11-deploy-vi-interfaces.md`](../specs/2026-10-11-deploy-vi-interfaces.md) · **Glossary:** [`CONTEXT.md`](../../../CONTEXT.md) · **ADRs:** [`docs/adr/`](../../adr/)

Full scope (spec D27): every Pathway at its Depths, every module, Deep Research, Prior Case, projections, every Front Page, and charts at parity with caos-databricks (D29). Tested regularly on the local issuer corpus (D28). The authoritative plan list, scopes, interfaces and PR groupings are in the interfaces spec §13; this page tracks them.

Plan just in time against the executed/tested predecessor. Fresh implementation uses a concise brief and real code/tests, without repeated full-code replay documentation. The 2026-10-13 owner amendment removes Excel report exports, independent review stages and rewrite tournaments; historical executed plans/evidence remain unchanged.

| Plan | Scope (interfaces §13) | Needs | Plan file | Status |
|---|---|---|---|---|
| 01 | Foundation: gates, Copilot spike, r14 reference, Handoff format, contracts, validator, generator, catalog, canon | — | [01 foundation](2026-10-11-deploy-vi-01-foundation.md) | merged to main (PRs #1–#4) |
| 02 | Intake and corpus: §14.1 amendments A1, A3–A5; corpus registry (34 packs) and `pytest -m corpus`; inventory, prepare, brief; synthetic CZR Primary pack; proxy-run skill | 01 | [02 intake and corpus](2026-10-11-deploy-vi-02-intake-and-corpus.md) | executed at `9e65cd9`; whole-branch and scoped review approved; 847 required-corpus tests and all gates pass; open stacked PRs #5–#24, CI green |
| 03 | Model (history): port of caos credit model `5c3cd52f`, PF-LTM, house view (Structuring/SSIM EBITDA, PF interest, multiples, EV), `model.json` (Excel export retired 2026-10-13) | 01 | [03 model](2026-10-11-deploy-vi-03-model.md) | final02 replay `0538271` approved; latest-LTM ruling implemented; 1,454 tests pass; executable plan reproduces all 561 files; open stacked PRs #25–#55, CI green |
| 04 | cp-start: CP-0 contract, grade / approve / plan, amendment A2, first FCA catalog entry | 02 | [04 cp-start](2026-10-11-deploy-vi-04-cp-start.md) | final02 replay `f4be647` approved; 11 task trees exact; 1,051 tests and all gates pass; review findings closed; open stacked PRs #56–#64, CI green |
| 05 | Core module rewrites (CP-1, CP-1A, CP-1B, CP-1D, CP-2, CP-3 + bond_analytics, FIT, CP-5, CP-6) with the A/B harness | 02, 03, 04 | — (plan file is uncommitted on main's working tree) | combined final-base `7d5cfe1` independently approved; 2,182 tests, all 16 gates and 49 exact task-tree/lock replays pass; live qualification pending; open stacked PRs #65–#89, CI green |
| 06 | Orchestrator: run state, dispatch, resume, `SKILL.md`, install, proxy run | 03, 04, 05 | [06 orchestrator](2026-10-12-deploy-vi-06-orchestrator.md) | executed; 06.15 first worker-written proxy run recorded; 06.16 integration in progress |
| 07 | Report: owner-picked mockup as template, chart engine, renderer, embedded run JSON, Credit Snapshot blocks | 06 | [07 report](2026-10-14-deploy-vi-07-report.md) | executed (07.1–07.8); template frozen (mockup A, DESIGN.md at design/report-a-refine b44aac0) |
| 08 | v1 acceptance on the corpus | 06, 07 | — | (A) complete; live pending |
| 09 | Quick depth (CP-L10, CP-6 screening) | 05, 07 | — | backlog (after v1) |
| 10 | Deep Research (CP-DR with fetch) | 06, 07 | — | backlog (after v1) |
| 11 | Prior Case (CP-8 diff, What changed tab) | 07 | — | backlog (after v1) |
| 12 | Full Credit Assessment remaining A (CP-1C, CP-2A, CP-2E, CP-4, CP-2D + calculators) | 05, 07 | — | backlog (after v1) |
| 13 | Full Credit Assessment remaining B and projections (projection + CP-CF ports, CP-2G, CP-2H, CP-3D, CP-3C, CP-4C) | 12 | — | backlog (after v1) |
| 14 | Earnings Update Pathway and Front Page | 09, 10, 11 | — | backlog (after v1) |
| 15 | Relative Value Pathway and Front Page | 12, 13, 14 | — | backlog (after v1) |
| 16 | Covenant & Refinancing Pathway and Front Page | 12, 13, 14 | — | backlog (after v1) |
| 17 | Distressed & Restructuring Pathway and Front Page | 13, 16 | — | backlog (after v1) |
| 18 | Portfolio Decision Pathway and Front Page | 12, 13, 14 | — | backlog (after v1) |
| 19 | Full-scope acceptance on Claude and GPT in work Copilot | 14–18 | — | backlog (after v1) |

**Scope decision (owner, 2026-10-11): v1 first.** The build targets v1 = Plans 01–08 (Full Credit Assessment end to end on the corpus, installed in work Copilot). Plans 09–19 stay on this roadmap as backlog and are not written until v1 is in use and the owner picks what comes next. Plans are written just in time: a plan is written after its predecessor is executed and tested, against actual code, so it needs no rebase. Plans 03 and 04 have been replayed onto approved Plan 02; Plan 05 has been replayed onto their approved combined base. Their local fixes and integration are reviewed, while live Copilot/model qualification remains pending. This narrows spec D27 (full scope) to v1 without removing it.

Build order: 02 → (03 ∥ 04) → 05 → 06 → 07 → 08 → (09 ∥ 10 ∥ 11) → 12 → 13 → 14 → (15 ∥ 16 ∥ 18) → 17 → 19.

**Execution model (global rules):** Sonnet implementation agents (`mx-scaffold`, `mx-feature`), with a task's third and later fixes on Fable (`mx-escalate`) (owner, 2026-10-14); confidence review and retained functional/calculation/source-integrity gates; no mandatory independent reviews or rewrite tournaments (owner, 2026-10-13). PRs ≤ 800 changed lines (lock files, `reference/**`, `tests/golden/**/documents/**` and `tests/corpus/synthetic/**` excluded). Every plan closes with a corpus regression and, where it changes modules or Pathways, proxy runs and module A/B (interfaces §12).
