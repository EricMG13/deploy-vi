# Deploy VI — build roadmap (full scope)

**Spec:** [`2026-10-11-deploy-vi-rbot-design.md`](../specs/2026-10-11-deploy-vi-rbot-design.md) · **Interfaces (binding cross-plan contract):** [`2026-10-11-deploy-vi-interfaces.md`](../specs/2026-10-11-deploy-vi-interfaces.md) · **Glossary:** [`CONTEXT.md`](../../../CONTEXT.md) · **ADRs:** [`docs/adr/`](../../adr/)

Full scope (spec D27): every Pathway at its Depths, every module, Deep Research, Prior Case, projections, every Front Page, and charts at parity with caos-databricks (D29). Tested regularly on the local issuer corpus (D28). The authoritative plan list, scopes, interfaces and PR groupings are in the interfaces spec §13; this page tracks them.

Plan just in time against the executed/tested predecessor. Fresh implementation uses a concise brief and real code/tests, without repeated full-code replay documentation. The 2026-10-13 owner amendment removes Excel report exports, independent review stages and rewrite tournaments; historical executed plans/evidence remain unchanged.

| Plan | Scope (interfaces §13) | Needs | Plan file | Status |
|---|---|---|---|---|
| 01 | Foundation: gates, Copilot spike, r14 reference, Handoff format, contracts, validator, generator, catalog, canon | — | [01 foundation](2026-10-11-deploy-vi-01-foundation.md) | written, verified |
| 02 | Intake and corpus: §14.1 amendments A1, A3–A5; corpus registry (34 packs) and `pytest -m corpus`; inventory, prepare, brief; synthetic CZR Primary pack; proxy-run skill | 01 | — | being written |
| 03 | Model (history): port of caos credit model `5c3cd52f`, PF-LTM, house view (Structuring/SSIM EBITDA, PF interest, multiples, EV), `model.json` (Excel export retired 2026-10-13) | 01 | — | being written |
| 04 | cp-start: CP-0 contract, grade / approve / plan, amendment A2, first FCA catalog entry | 02 | — | queued |
| 05 | Core module rewrites (CP-1, CP-1A, CP-1B, CP-1D, CP-2, CP-3 + bond_analytics, FIT, CP-5, CP-6) with the A/B harness | 02, 03, 04 | — | queued |
| 06 | Orchestrator: run state, dispatch, resume, `SKILL.md`, install, proxy run | 03, 04, 05 | — | queued |
| 07 | Report: owner-picked mockup as template, chart engine, renderer, embedded run JSON, Credit Snapshot blocks | 06 | — | queued (waits on the mockup pick) |
| 08 | v1 acceptance on the corpus | 06, 07 | — | queued |
| 09 | Quick depth (CP-L10, CP-6 screening) | 05, 07 | — | queued |
| 10 | Deep Research (CP-DR with fetch) | 06, 07 | — | queued |
| 11 | Prior Case (CP-8 diff, What changed tab) | 07 | — | queued |
| 12 | Full Credit Assessment remaining A (CP-1C, CP-2A, CP-2E, CP-4, CP-2D + calculators) | 05, 07 | — | queued |
| 13 | Full Credit Assessment remaining B and projections (projection + CP-CF ports, CP-2G, CP-2H, CP-3D, CP-3C, CP-4C) | 12 | — | queued |
| 14 | Earnings Update Pathway and Front Page | 09, 10, 11 | — | queued |
| 15 | Relative Value Pathway and Front Page | 12, 13, 14 | — | queued |
| 16 | Covenant & Refinancing Pathway and Front Page | 12, 13, 14 | — | queued |
| 17 | Distressed & Restructuring Pathway and Front Page | 13, 16 | — | queued |
| 18 | Portfolio Decision Pathway and Front Page | 12, 13, 14 | — | queued |
| 19 | Full-scope acceptance on Claude and GPT in work Copilot | 14–18 | — | queued |

Build order: 02 → (03 ∥ 04) → 05 → 06 → 07 → 08 → (09 ∥ 10 ∥ 11) → 12 → 13 → 14 → (15 ∥ 16 ∥ 18) → 17 → 19.

**Execution model (global rules):** fresh native GPT implementation agents, confidence review and retained functional/calculation/source-integrity gates; no mandatory independent reviews or rewrite tournaments (owner, 2026-10-13). PRs ≤ 800 changed lines (lock files, `reference/**`, `tests/golden/**/documents/**` and `tests/corpus/synthetic/**` excluded). Every plan closes with a corpus regression and, where it changes modules or Pathways, proxy runs and module A/B (interfaces §12).
