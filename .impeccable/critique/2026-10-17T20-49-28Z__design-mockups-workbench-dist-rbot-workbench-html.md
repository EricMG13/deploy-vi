---
target: RBOT Workbench mock (after C1 fixes, 2154cce)
total_score: 27
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:/Users/ericguei/Documents/Deploy VI/.claude/worktrees/deploy-vi-plan-09-1992b3/design/mockups/workbench/dist/rbot-workbench.html"
target_fingerprint: "sha256:a402c4427e1c604251b59b51c878efc1b9d6242218140823e582e68dd1701765"
target_path: /Users/ericguei/Documents/Deploy VI/.claude/worktrees/deploy-vi-plan-09-1992b3/design/mockups/workbench/dist/rbot-workbench.html
timestamp: 2026-10-17T20-49-28Z
slug: design-mockups-workbench-dist-rbot-workbench-html
---
Method: dual-agent (A: mx-precise, Opus 5.5 · B: mx-feature, Sonnet 5.5)

# Critique 2: RBOT Workbench after C1 fixes (2154cce)

## Design Health Score
| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | No visible selection ring on navy; honest state one amber line |
| 2 | Match System / Real World | 3 | TEST_CLO_I in CP-6 prose; enum chips in Model limitations; chart.model_strip@model.metrics Table-tab head |
| 3 | User Control and Freedom | 3 | Honest toggle global, silent, only in run switcher |
| 4 | Consistency and Standards | 2 | Text values unmarked vs numbers marked; RV "Avoid" vs "4 - Modest UW"; dashed outline overloaded; prev/next walks unlisted host steps |
| 5 | Error Prevention | 2 | Larchmere CLO 3 MW with Breaches folded; honest state leaves Direction |
| 6 | Recognition Rather Than Recall | 3 | Real-run toggle undiscoverable |
| 7 | Flexibility and Efficiency | 3 | No rail/prev-next shortcuts; one passport at a time |
| 8 | Aesthetic and Minimalist Design | 2 | Call lines studded with glyphs and codes; Covenant shows eight tests twice |
| 9 | Error Recovery | 3 | Blocked page exemplary; uncited EV/Equity unmarked |
| 10 | Help and Documentation | 3 | No on-page explanation of Not produced, Binds an instrument, dashed tiles |
| **Total** | | **27/40** | **Acceptable** |
C1's five issues verified fixed (169/169 checks); unanchored reviewer found a deeper layer. Two P1/P2s stem from C1 trade-offs.

## Design Specificity Verdict
Authored for this product; identity in the navy verdict bar, which is the weakest-executed surface.
Detector: primary hits 2,447 -> 915; undersized-ui-text 103–509/route -> 0–1; file scan no primary findings. tiny-text 421 (deliberate 11–11.5px); low-contrast 380 (FP, non-text #7C839C mark); line-length 39 (real minor); cramped-padding 42 (mostly FP; verdict-lines needs look); text-occlusion 16 on blocked RV (not a chart twin: render.js:651-655 renders notice only; probable collapsed talk rows under next panel; unverified); skipped-heading 4, repeated-container-text 2 (real minor).
Overlays: none presented.

## What's Working
1. Passport model (cited, calculated with inputs, gap never zero, illustrative; Back/Esc).
2. Honest gaps and Blocked states as designed states.
3. Disciplined token system; signal colour always paired with word or icon; one tab stop per table.

## Priority Issues
- [P1] Most severe Fit signal folded or misattributed: Larchmere Breaches behind "4 more" (C1 Distressed 2-line cap); PD "1 Breaches" wraps under the wrong portfolio. Fix: negative-tone lines never fold; per-portfolio unbreakable segment; cap shown on the Strategy tile. /impeccable clarify
- [P1] Provenance hole: text columns resolve to plain (core.js:960) so synthetic Moody's/S&P ratings, coupons, SOFR spreads are unmarked; uncited EV/Equity unmarked. Fix: resolve text through WB.rowInfo; visible no-source mark and passport. /impeccable harden
- [P1] Honest state partial: Credit Direction (pages.js:99) and EU Direction/Outlook/Since-last tiles not mapped; Larchmere bar Not met vs panel Met; ILLUSTRATIVE tag stays. Fix: map every judgement tile; dim illustrative panel verdicts; REAL-RUN STATE tag; toggle in bar header. /impeccable clarify
- [P2] Call lines read as annotated source text; fixture caveat in main-risk slot. Fix: bold lead, sentence, one "Sources n" affordance; caveat to byline; ~80ch. /impeccable distill
- [P2] 1280 inspector strip reflows the canvas on first click (C1 brief; departs from DECISION.md). Fix: fixed 260px or overlay; thin chart-strip axis. /impeccable adapt

## Persona Red Flags
Alex: no rail/prev-next shortcuts; one passport at a time; Evidence places capped at 3.
Sam: citation buttons mid-sentence in call prose; gap chip named only "Not available"; ratings not focusable; 51 tab stops before canvas (skip link exists).
Priya: Larchmere CLO 3 MW with Breaches hidden; RV Avoid vs Modest UW; two red tiles for one fact on EU; Strategy vs instrument finals unexplained on PD; Blocked RV Valuation unqualified.

## Minor Observations
Panel heads 11px vs WORKBENCH 13/600; C12 excerpt cut without ellipsis; Lender protection uses min area not Overall; "Headroom" repeated x8; EU chart mixes US$5.9bn and (62) on one axis; "Primary" on 7/8 run rows; wide twins truncate in Table tab; Model limitation chips lead with enum codes; Rating triggers title duplicated; 1,075 unresolved n/a cells are fixture gaps.

## Questions to Consider
- Why does the bar try to be a passport? One "Trace this call" action?
- Should Breaches ever sit next to an unqualified Strategy tile?
- Should the real-run state be the default?
- Plan order or question-based navigation?
