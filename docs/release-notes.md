# Release notes

## Unreleased (Plan 10: Deep Research)

- CP-DR (Deep Research) joins the `full` list of Full Credit Assessment right after CP-1A; `quick` is unchanged.
- `rbot fetch` is new: off by default, enabled by `RBOT_FETCH=1`, with the mode recorded at Approval (`approval.fetch`). `grade` states which note applies before Approval.
- Downstream readers (CP-2, CP-3, CP-5, CP-6) may cite qualified `fetched/` pages, each with its URL and retrieval date.
- Validator: new finding `research_policy` for CP-DR answers, evidence and approved question ids.
- cp-start: CP-0 offers up to five research questions `Q1`..`Q5` (consumers CP-2, CP-3, CP-6); the analyst keeps or drops them with `approve --deep-research yes|no --untick <id>…`. CP-2 cites `cpdr.sector_view.outlook` when CP-DR is accepted.
- Proxy: `proxy_run --fetch` requires `RBOT_FETCH=1` in the environment and never sets it; a run without `--fetch` refuses while the variable is set. The scorecard prints the recorded `Fetch: on|off`.

## Unreleased (Plan 09: Quick depth)

- FCA offers `quick`: CP-0, CP-1, CP-1A, CP-1B, MODEL, CP-L10, CP-3, FIT, CP-5, CP-6 (CP-8 joins in Plan 11). Deep Research and the Full-only modules (CP-2, CP-1D, CP-2A, CP-2E, CP-2G, PROJECTION) do not run at quick.
- CP-L10 (Quick-depth screen) is new: one topics table by family (financial change, liquidity, covenant and refinancing, distress, relative value, portfolio), screen items, upgrade triggers; it owns the credit view and strengths/weaknesses at quick.
- CP-6 writes `basis` Screening at quick: Restricted, never Committee Ready, a linked Full run named as the upgrade.
- Validator: new findings `screen_policy` (LITE rules on cpl10.screen_topics), `basis_depth` (basis must match the run depth) and `blocked_gate` (CP-3 may be Blocked only with no market level and no talk).
- Report: "Screening only" in the Credit Snapshot title band at quick; new Analysis chart `chart.topic_counts` (topics by materiality and disposition, one per family).
- Module and depth gates read the installed catalog (module ids from rbot/modules/*/contract.json).
- Record run on czr-2026q2-lite-full-credit-screen (quick): R1–R8 PASS. FIT was switched off by approval (no portfolio context), which R3 counts as satisfied (owner, 2026-10-16). Scorecard: docs/corpus-runs/2026-10-16-czr-2026q2-lite-full-credit-screen-full-credit-assessment-quick.md.
- A/B: CP-L10 PASS (docs/ab/2026-10-16-CP-L10-czr-2026q2-lite-full-credit-screen.md); CP-6 screening B-only, non-equivalent (docs/ab/2026-10-16-CP-6-czr-2026q2-lite-full-credit-screen-screening.md).

## v1 (draft)

RC: build/v1-rc5 `9f049c8` (supersedes RC4 `daa45c3` and RC3 `2d19018`). Live status: **deferred** (owner, 2026-10-15: the work PC is available only once the first functional version is complete; see [acceptance/v1.md](acceptance/v1.md)).

### What v1 does

Full Credit Assessment at `full` depth, run unattended as sub-agents in Copilot: CP-0, CP-1, CP-1A, CP-1B, CP-1D, MODEL, CP-2, CP-3, FIT, CP-5, CP-6, then a rendered report (`report.html`, `report.md`) with citations and a Limitations tab. Excel input ingestion is supported; Excel report export is not part of v1. Quick, CP-DR, CP-8, PROJECTION and the other Pathways are backlog.

### What changed in Plan 08

- Model fix (F3): the pro forma undrawn revolver now reflects facility-stack movements on the revolver (spec §6.5).
- Model fix: an income statement with no cost of revenue (nature-of-expense) now computes EBITDA and EBIT instead of blanking them; gross profit is left blank with a note.
- Report fix (R7): Restricted steps that no CP-5 row names appear as unforeseen limitations.
- A validator finding for unresolved `[[...]]` placeholders.
- Module revisions after the model-written A/B: canon rules (counter-argument, conflict register, time-ordered downside), and process changes in CP-0, CP-1, CP-1D and CP-3.
- Windows run lock (`msvcrt.locking`) for the work PC.
- Owner decisions of 2026-10-15: F8 (an expected rating is Unrated for FIT bucket limits), F11 (excluded add-backs keep negative amounts; FY2024 Adjusted EBITDA 3,723 = issuer), F10 (the Credit Snapshot prints at full scale across pages), F12 (deep links show only the target view). F4 kept as specified.
- Print fixes (owner, 2026-10-15, "fix all three print issues"; RC5): page 1 of the printed Snapshot holds the title band, call band and the full-width thesis; wide Snapshot tables print as compact whole-word label/value records; print shows the per-block "Source:" lines, chart summaries and chart sources, and the relative-value and transaction-summary blocks (chart data tables stay hidden). Every Snapshot block prints full width. Print rules live in report.js; report.css is unchanged. Snapshot print is 25 pages Letter landscape.
- Transfer package, extracted-install smoke and acceptance check scripts.

### Known limitations

- F10 residual: some printed Snapshot pages end with blank space where a block is kept whole. Not verified: physical printer output, A4 paper, Firefox/Safari, the interactive print dialog.
- F5, F6: FIT Evidence Trace is empty; C-17 is not computed when the sector is only in CP-1A prose.
- F7: CP-3 comparables may mix secured and unsecured seniority without disclosure; indenture Schedule II is not examined.
- F9: CP-6 recovery stress may rank sale-leaseback obligations ahead of secured lenders.
- R5 measurement is keyed on worker-chosen facility ids.
- Windows behaviour (run lock, installers, `os.replace` with open handles) is unverified.

### Live acceptance

Deferred by the owner (2026-10-15): the work PC is available only once the first functional version is complete, so live acceptance has not been run and nothing is waived. Still to run: L1-L11 and R1-R8 on one Claude and one GPT model on the work PC. The package (rbot-v1-9f049c845305.zip, 2,422,231 bytes, sha256 `f2596542784c5c41ca2b2663d5d8d1bbcb6e97bcd68b1541a2e3cbc26bfe38c4`) was handed over to the owner in-session on 2026-10-15.
