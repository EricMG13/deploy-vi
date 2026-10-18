---
target: RBOT Workbench mock (polished build 536b715)
total_score: 27
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:/Users/ericguei/Documents/Deploy VI/.claude/worktrees/deploy-vi-plan-09-1992b3/design/mockups/workbench/dist/rbot-workbench.html"
target_fingerprint: "sha256:34bd54447385f094522def6a5e7aeb5a69db391eeb712eb4b8b0b6d7e23205ba"
target_path: /Users/ericguei/Documents/Deploy VI/.claude/worktrees/deploy-vi-plan-09-1992b3/design/mockups/workbench/dist/rbot-workbench.html
timestamp: 2026-10-17T19-32-39Z
slug: design-mockups-workbench-dist-rbot-workbench-html
---
Method: dual-agent (A: mx-precise, Opus 5.5 · B: mx-feature, Sonnet 5.5)

# Critique: RBOT Workbench, polished build (536b715)

Target design/mockups/workbench/dist/rbot-workbench.html. Mode: Operate.

## Design Health Score
| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Honest-state toggle shows only as one amber line; not in URL or run switcher |
| 2 | Match System / Real World | 2 | Machine strings: `Corp rating fitch`, `Origin data:C177`, `yield 8.06352%`, gap ids as values |
| 3 | User Control and Freedom | 3 | Esc and back work; inspector can't be closed or narrowed, even at 1280 |
| 4 | Consistency and Standards | 3 | All-n/a tables collapse in CP-3D, full grid in CP-2H; "Fitch" vs "Corp rating fitch" |
| 5 | Error Prevention | 3 | Illustrative/synthetic marks everywhere; main risk can fold behind "1 more" |
| 6 | Recognition Rather Than Recall | 2 | Icon-only rail; six glyphs to learn; CP codes and G-ids carry meaning wordlessly |
| 7 | Flexibility and Efficiency | 3 | / ? arrows Enter anchors; search skips Model lines; no next-module or run-switch keys |
| 8 | Aesthetic and Minimalist Design | 2 | ILLUSTRATIVE on nearly every panel head, glyph on every cell, fixture notes in call lines |
| 9 | Error Recovery | 3 | Blocked states say what lifts them; some gap passports fall back to a generic reason |
| 10 | Help and Documentation | 3 | `?` overlay concise and complete; inspector tab labels thin |
| **Total** | | **27/40** | **Acceptable** |

## Design Specificity Verdict
LLM: authored for this product inside a generic shell (rail, navigator, inspector). Per-Strategy house-scale tiles, six-shape provenance grammar, covenant bullets with Tight bands, distress-gate tables, Fit headroom bars, honest-state "Not produced" tiles are product-specific.
Detector: file + 7 rendered scans, all exit 2, 2,447 primary hits. undersized-ui-text 103–509/route (real: --fs-micro 10.5px, .tag 10px; missed by the review); tiny-text 20–85 (real, lower); low-contrast all on #7C839C (false positive for text: non-text provenance mark at 3.8:1); cramped-padding (real for .tag; FP for tab strips and system swatches); line-length (real for .v-line 150ch); text-occlusion 5 on RV-blocked (probable FP: collapsed talk disclosure; unconfirmed); skipped-heading 4 on system (real, low); design-system-font 3 (doc drift: root DESIGN.md describes Report A).
Overlays: none presented (no browser tool in the sub-agent).

## What's Working
1. Provenance is functional: each glyph opens a passport of its kind (cited with verbatim excerpt and uses; calculated with labelled inputs; synthetic with rationale).
2. States share one grammar across runs (Blocked lines, Not drawn frames, honest-state tiles; Larchmere explains Not met vs Met).
3. Charts are domain instruments (covenant bullets, Fit headroom with "From file", model strip with projected boundary and n/a on the axis).

## Priority Issues
- [P1] Gap passports leak machine labels and fall back to a catch-all reason (core.js:980-1012, shell.js:600-645). Fix: canvas label as title; chart marks from Model lines route to mcell passports; no-match says "Reason not recorded by the module", logs to __wbErrors, lists no gaps; de-dup; raw locators to foot. /impeccable clarify
- [P1] At 1280x800 no issuer name on screen; empty inspector takes 23% of width. Fix: issuer, ticker, Fictional tag in the verdict bar title row; collapse the empty inspector below 1360px or preload the main-risk passport. /impeccable adapt
- [P1] Quick Credit Snapshot folds MAIN RISK behind "1 more" (capCallLines, render.js:741-790); content doc 01 requires it. Other pages follow their content docs; owner call whether to guarantee it everywhere. Fix: uncappable main-risk slot; Screening/Blocked as byline tags. /impeccable layout
- [P2] Signal spent everywhere, labels too small: ILLUSTRATIVE per panel, glyph per cell, amber "With limitations" on 20/21 modules; tags 10–10.5px. Fix: state illustrative once in the bar, tag only differing panels; navigator icons only for rows off the norm; --fs-micro and .tag to 11px with vertical inset. /impeccable quieter, /impeccable typeset
- [P2] False precision in the call: "yield 8.06352% … 8.06%", "9.318398%", EV "1,406.5". Fix: format by unit; raw only under "Served as". /impeccable typeset

## Persona Red Flags
Alex: search misses Model lines (shell.js:376-405); no run-switch / rail / next-module shortcuts; honest state not in URL; empty inspector costs a click.
Sam: 10px uppercase tags; glyphs distinguished by shape at ~10px; inspector heading focus ring reads as an input; 11 icon-only rail buttons; crowded n/a axis labels; skipped headings on system.
Priya (CLO PM before committee): Fit line names no binding limit; fixture note in the main-risk sentence; Valuation on Blocked RV carries no dependency on CP-3D; no "Caesars" at 1280.

## Minor Observations
Rail logo cropped (brand: supplied variants only, components.css:12); views.js:912 silent catch; duplicate status chip in module view; CP-2H 32 n/a cells vs CP-3D collapse; honest FCA tiles orphan Direction on row two and Key findings still says ILLUSTRATIVE; Portfolio Decision final tile wraps; compact sticky bar clips the panel below; synthetic search hits indistinguishable; Evidence C7 "0 places"; Gaps tab lowercase starts; 92 em-dashes on system; DESIGN.md is Report A's; W6 open items stand (four first-viewport second items, 12-page print, machine ids in registers).

## Questions to Consider
- Should the navigator signal "touches the call" rather than module status?
- Should the inspector exist before it is asked for?
- Should Valuation carry a dependency mark when CP-3D is Blocked?
- Are CP codes reader or analyst vocabulary?
- What is the last thing a Front Page leaves the reader with?
