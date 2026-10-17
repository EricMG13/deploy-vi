# Design fixtures: complete test runs for every Pathway

Status: 2026-10-17. Owner decision: populate **every** module for the Claude Design hand-off. Caesars (CZR) stays real-first: every real figure, citation and real CAOS finding is kept, and only what the sources or runs cannot supply is filled with **synthetic test values**. The Distressed & Restructuring page uses a **fully fictional distressed issuer**, because no real distressed issuer was ever run. Variants exercise every state a design must handle. The merger financing is pending, so every CZR run whose plan has CP-3 is Primary (the Earnings Update is not).

These are design fixtures. They are never a source for a credit decision, never a fact about Caesars, and every synthetic value says so in its own citation.

## 1. Output contract

One JSON file per Report run, shaped as the Report's embedded data `rbot-run/1` (interfaces spec §11.3; read it from `git show b4f39c3:docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md`), plus a top-level `fixture` block:

```json
{
  "schema": "rbot-run/1", "fixture": {"kind": "design", "real_first": true, "issuer_fictional": false, "notes": ["..."]},
  "rbot_version": "design-fixture", "run_id": "FIX-CZR-FCA-001", "generated_at": "2026-10-17T00:00:00Z",
  "run_brief": {"front_matter": {...}, "tables": {"snapshot.run_header": {"columns": [...], "rows": [[...]]}, "snapshot.transaction_summary": {...}, "brief.approval": {...}, ...}},
  "pathway": "FULL_CREDIT_ASSESSMENT", "depth": "full", "primary": true, "front_page": "credit_snapshot",
  "plan": ["CP-0", "CP-1", ...], "steps": {"CP-0": {"status": "accepted", "qa_status": "Restricted"}, "CP-DR": {"status": "skipped", "reason": "..."}},
  "handoffs": {"CP-1": {"qa_status": "Pass", "front_matter": {...}, "analysis_md": "...", "gaps_md": "...", "tables": {"cp1.debt_facility_register": {"columns": [...], "rows": [[...]]}}, "citations": [{"id": "C1", "source": "...", "locator": "...", "excerpt": "...", "anchored": true, "synthetic": false}]}},
  "model": {...rbot-model/1, interfaces §6.2...}, "fit": [{...}],
  "charts": [{"chart_id": "chart.model_strip", "where": "front_page:15", "kind": "lineStrip", "origin": "host", "tables": [...], "data": {...}}],
  "front_page_blocks": [{"id": "...", "title": "...", "shown": true, "reason": null, "tables": [...]}],
  "limitations": {"approval": [...], "cp5": [...], "unforeseen": [...]},
  "prior_case": null
}
```

- **Every module in the Pathway's Full plan** (interfaces §5) has a handoff with front matter (`module_id, run_id, issuer_id, analysis_date, qa_status, inputs`), `analysis_md`, every table its §2 catalogue lists with every column (critical columns never blank; a missing non-critical value is `—` explained in `gaps_md`), `gaps_md` and `citations`. Host steps (`RUN_BRIEF`, `MODEL`, `PROJECTION`, `FIT`) produce their §3 tables.
- **Cell values are strings** as the handoffs serve them (`"3.29x"` columns ending `_x`, `"12.5%"` for `_pct`, integers for `_bps`, ISO dates for `_date`, plain decimals otherwise, `—` for a gap). A `cite` column holds `[C<n>]` markers or `calc: <formula>`.
- **Synthetic values** carry a citation row with `"synthetic": true`, `source` `"TEST DATA — invented for design, not a fact about <issuer>"`, `locator` `"fixtures/<file>#<key>"` and `excerpt` = one sentence of rationale (why this value is plausible). Their figures cite only that row. A table row mixing real and synthetic figures cites both.
- **Real values** keep their real citations: the CZR base data (`design/mockups/shared/data.js`), the Front Pages data (`design/mockups/front-pages/fp-data.js`) and the real CAOS module outputs (`design/claude-design-handoff/data/caos-runs/`). Prefer real CAOS wording for `analysis_md` where a real module exists (keep its meaning; rewrite only to RBOT's four-section form; carry its citations).
- **Arithmetic** (sums, ratios, multiples, headroom, recoveries, projections, Fit) is computed in the generator with `Decimal` and `ROUND_HALF_UP` from the stated inputs, never typed. A synthetic input is typed; everything derived from it is calculated.

## 2. The runs

| File | Pathway, depth | Issuer | Notes |
|---|---|---|---|
| `czr-full-credit-assessment.run.json` | FULL_CREDIT_ASSESSMENT, full, Primary | CZR | All 24 plan steps; Primary: the merger financing as three synthetic new tranches with Price Talk, OID, expected ratings and CR Score; PF-LTM populated from them (synthetic); PROJECTION with Base and Downside (synthetic drivers); CP-DR run with three approved questions (synthetic answers from synthetic fetched sources, labelled); CP-6 decision; FIT on Test CLO I (synthetic) |
| `czr-full-credit-assessment-quick.run.json` | FULL_CREDIT_ASSESSMENT, quick, Primary | CZR | CP-L10 screen (real CAOS LITE output where it exists); CP-6 basis Screening |
| `czr-earnings-update.run.json` | EARNINGS_UPDATE, full, **with Prior Case** | CZR | A synthetic prior Report dated 2026-08-05 (Q1 2026 update) and CP-8: what changed, thesis review, recommendation change |
| `czr-relative-value.run.json` | RELATIVE_VALUE, full, Primary | CZR | Synthetic loan marks for TLB and TLB-1 (bid/ask, 3Y DM) and a synthetic spread curve so every RV block fills |
| `czr-relative-value-blocked.run.json` | RELATIVE_VALUE, full, Primary | CZR | State variant: CP-3D **Blocked** (no market observations admitted) so its tables keep critical cells `—` |
| `czr-covenant-refinancing.run.json` | COVENANT_REFINANCING, full, Primary | CZR | Real covenant extraction plus synthetic RP and investment basket usage, so capacity is fully computable |
| `czr-portfolio-decision.run.json` | PORTFOLIO_DECISION, full, Primary | CZR | Two portfolios: Test CLO I (synthetic) and a synthetic Indexed HY book modelled on a real fund's four Caesars positions; one instrument **Breaches** |
| `larchmere-distressed-restructuring.run.json` | DISTRESSED_RESTRUCTURING, full, Primary | **Larchmere Leisure Group (fictional)** | Primary: the sponsor's 150 super-priority priming loan is tranche `NEW-1` (transaction summary, CP-1 pro forma rows, Model PF-LTM, CP-3 talk row, Fit); CP-DR and CP-8 skipped; Gate **Met**; every module synthetic; a covenant **Breached** and one **Tight**; fulcrum migrates by scenario |

## 3. The fictional distressed issuer

**Larchmere Leisure Group, Inc. (fictional)**, issuer id `LLG-FICTIONAL`, no ticker. A regional casino-resort operator, eleven properties in four US states, bought in a 2022 sponsor LBO (sponsor: "Quillon Ridge Partners (fictional)"). The name, sponsor, figures and documents are invented; it must not resemble any real company and no real company's facts may be used.

The story the numbers must tell (calculate every derived figure):
- LTM revenue about US$1.4bn, falling; Adjusted EBITDA about US$210m (down about 25% year on year); EBITDA after master-lease rent thin.
- Debt about US$1.7bn: RCF US$200m fully drawn (springing first-lien net leverage covenant 6.50x, tested because use exceeds 35%), first-lien term loan B US$1.05bn (SOFR + 450, matures 2028), second-lien term loan US$250m, senior unsecured notes US$200m (8.25%, 2029). Net leverage about 8x.
- Liquidity runway under 12 months; the RCF matures within 18 months; an interest payment grace period is running on the unsecured notes.
- Covenant: first-lien net leverage **Breached** at the last test date, with an equity cure available once; minimum liquidity covenant **Tight**.
- Ratings Caa2 / CCC (synthetic); first-lien loan quoted at 74, second lien at 41, notes at 23 (synthetic quotes, freshness Current).
- EV scenarios: going concern at three multiples of LTM Adjusted EBITDA and a liquidation case; recovery waterfall by class; fulcrum = second lien in the base case, first lien in the stress case.
- Paths: amend-and-extend with an uptier (non-pro-rata, open-market purchase language present), a pre-packaged Chapter 11, an out-of-court exchange of the notes; LME capacity: unrestricted-subsidiary drop-down Available, sacred-rights protection Weak.
- One module **Blocked**: CP-2H (no rating-agency report admitted), its tables kept with critical cells `—`. (CP-1C is not in this Pathway's plan.)
- Portfolio Fit: a synthetic CLO book holding 2.8% of NAV of the first-lien loan against a 2.5% single-issuer Hard limit: **Breaches**, capped at Avoid.

## 4. Module outputs: anatomy and voice

- `analysis_md`: three to six short paragraphs in the house voice (plain, cited, every figure with its marker; judgements stated as the module's view with confidence). Start with the module's answer to its reader question (interfaces §1).
- Real CAOS outputs (`data/caos-runs/`) show the depth expected per module. The legacy Deploy V outputs (M365 Copilot screenshots, catalogued in `inputs/legacy-module-outputs-vmo2.md` and `inputs/legacy-module-outputs-woodmac.md`) are **content inspiration only**: realistic values, wording and density for populating modules. **RBOT's methodology supersedes them** (owner, 17 Oct 2026): the module set, reader questions and §2 tables of the interfaces spec, and the four-section handoff (Analysis, Tables, Gaps, Citations). Never reproduce Deploy V's T-/P-registers, QA Validation lists, front-matter blocks or status strings.
- `gaps_md`: one bullet per gap: what is missing, why, effect, source that would lift it.

## 5. Every chart must be viewable

The purpose of these fixtures is that every design and every chart can be seen populated. For each run, every chart in interfaces §11.4 whose source tables belong to the run's modules or host steps must receive non-empty data: model strip with Base and Downside, maturity wall, capital structure, EBITDA bridge, adjusted-debt bridge, headline results, KPI changes, peer ranges (add up to three anonymised synthetic peers, labelled "Peer C (synthetic)" etc., so quartiles are meaningful), implied EV, liquidity sources, cash uses, liquidity bridge, rate/FX tornado, downside tornado, risk matrix, forecast lines, credit path, rating triggers, RV loan and HY, talk range, factor scores, spread curve, implied PD, LME exposure, funding gap, covenant headroom, basket capacity, value allocation, recovery by class, issue counts, topic counts, expected against realised, what changed, and Fit bullets. The only charts allowed to draw as n/a frames are those a deliberate state variant blanks (the Blocked CP-3D run; Larchmere's Blocked CP-2H, whose rating-triggers chart is n/a; CZR's CP-4C, whose real gate is Not met, so its value allocation and recovery charts appear in the Larchmere run instead).

## 6. Checks the generator runs (`--check`)

- Every plan step has a handoff or a step status with a reason; every §2 table of every handoff exists with every column; critical cells non-blank except in Blocked handoffs.
- Every `[C<n>]` resolves to a citation of that handoff; every synthetic figure resolves to a synthetic citation; no real citation is marked synthetic.
- Every derived figure recomputes from its inputs (sums, multiples, headroom, recoveries, Fit verdicts and caps per §7, projection identities).
- No real CZR figure differs from the base or Front Pages data.
- Every chart required by §5 has non-empty data in each run (list the chart ids per run in the run's `fixture.notes`).
- Larchmere contains no real company name (a deny-list check against the CZR corpus issuer names and the peers MGM and PENN) and no figure copied from CZR.
