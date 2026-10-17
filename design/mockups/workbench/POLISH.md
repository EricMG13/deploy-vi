# RBOT Workbench: polish pass (W6)

Opus pass at xhigh effort, owner-requested, on the full mock at `6895c68`. Polish is refinement inside Direction C: no new components, no new data, every rule in WORKBENCH §7 kept. `git diff 6895c68 -- design/mockups/workbench` shows the changes.

Evidence (before): `shots/w6-before/` (first viewport of every run's Front Page, two module views per run, Model, Portfolio Fit, Evidence, Limitations, Design system at 1440×900 and 1280×800; full-canvas captures in `full/`; interaction states `state-*`; print `print-snapshot.pdf`), a text-contrast audit of every visible text node, a text lint for raw ids and fixture text, and a real keyboard Tab walk of the Credit Snapshot (Chrome DevTools Protocol, trusted key events).

## Findings, by severity

Severity: **P1** misleading state, broken or inaccessible path, rule breach; **P2** hierarchy, layout and chart finish; **P3** consistency and detail.

### P1

1. **The call misses the first viewport.** The verdict bar measures 260–410px at 1440×900 (Earnings Update about 400, Distressed about 400, Relative Value Blocked about 345) and 380–500px in the honest state. "Collapse all" wraps to its own row on every Front Page; Distressed and Covenant also wrap their byline. Earnings Update shows a "Recommendation: Not produced" tile its content doc does not have (the doc states the absence as a line), which pushes the tile row to two rows; the Distressed bar carries six call lines where its content doc names three. Earnings Update and Relative Value lose their first key panel's chart below the fold.
2. **Lender protection scores read as cited.** `cp4.protection_score.score` cells carry the cited mark and solid chart bars, but they are judgements (content doc 04: "illustrative five-point"); the verdict tile for the same score already says illustrative. The panel lacks its Illustrative tag.
3. **One limit, two states.** C-04 (7.36 against 7.5, headroom 0.14) reads "Within" in positive green in the Portfolio Fit view and "Tight" in caution on the Portfolio Decision Front Page.
4. **Covenant wording differs between chart and table:** the bullet says "Breach", the table and the house vocabulary say "Breached".
5. **The fulcrum class is drawn in caution amber;** the colour doc assigns the fulcrum class to negative.
6. **Amounts that look like years print ungrouped:** "2018" and "2000" in the Outstanding column beside "2,835" (Capital structure on Snapshot, Relative Value, Covenant).
7. **Print:** endnote markers sit on top of figures and chips (the 24px hit-area `::after` also positions the endnote text absolutely); "Full analysis" links print; the call-line disclosure (new) must print open.
8. **Contrast below AA:** navigator zero-count chips ("Pass 0", "Blocked 0") at 55% opacity, 2.3–2.7:1; the Design system's "No on-navy variant" label is navy on navy, 1:1. Every other text node on the eight Front Pages, Model, a module view and the Design system passes (9,500 nodes measured).
9. **Model grid cells lost their padding** (a selector-specificity slip: `.mg td { padding: 0 }` beats `.mg-c`), so figures touch the column rules; the grid's corner head is centred over a left-aligned label column.
10. **Design system tile specimen is broken:** the Credit Score tile is fed `scale: five` with "3 - Medium", which prints over the Valuation tile.
11. **Fixture summaries on screen** ("9 populated row(s) from model.metrics, …") under every chart title in module views, the Model and the Design system.
12. **Raw ids on screen:** chart source lines (`model.metrics, model.summary`), the inspector code line (`chart.factor_scores@cp4.protection_score` overflowing the inspector; `cp0.run_brief_prefill` above "Value"), Model limitation codes (`PROJECTION_OPENING_AT_LTM`, wrapping mid-token) and `Undated: sid_bonds, other_debt`, the `facility_id` column (`cei_rcf`, `llg_tlb`) in Capital structure by facility, claim-class ids in the Distressed fulcrum line (`C2-1L`, `C4-NOTES`), the `⟨date⟩` placeholder in "What changed since ⟨date⟩" (Covenant, Distressed, Portfolio panels and the outline), period ids (`Q2_2026`), case enums (`BASE`, `DOWNSIDE`), `snapshot.financials · ltm` under the what-changed dumbbells, "Metric ID" and "KPI ID" heads over humanised labels.
13. **Fixture text in the byline:** the Design system's Blocked specimen prints "Credit Research (design fixture)".
14. **Units:** "the 50 covenant floor" (US$50m); money in the Fit panels prints "US$ 400,000,000", "US$ m 491.6" and "883,300 US$" against the house style "US$5,000,000" and "US$491.6m".
15. **Stale interaction scenarios:** `check.py --interact` fails 3 of 80 (Fit now built; the fixture-text check matches the analyst string; the synthetic check picks a figure whose excerpt is a plain statement).

### P2

16. **Chart captions repeat the panel title** (Model chart strip, every module chart panel, debt stack under its own sub-heading).
17. **The Snapshot chart strip uses 70% of its panel** (an empty second grid column left from when the maturity wall sat beside it), so the three plots are cramped and the x labels run together ("FY23FY24FY25").
18. **Line charts:** end labels of Base and Downside collide ("12,482" over "10,955", "4,063" over a point), the "Projected" label sits on data labels, and a last-point label overprints the unit.
19. **Waterfall step labels stack and collide** where bands are narrow: the Covenant liquidity bridge (12 steps at half width), the Larchmere runway bridge and the Model's adjusted debt bridge.
20. **Spread curve:** the "bps" unit overprints the top tick; issuer points near the right edge lose their labels; names print in mono.
21. **Bullets at half width:** labels wrap to three or four lines in a 120px column and the track is about 150px; the unit group heading reads only "x".
22. **Value allocation:** four waterfalls stacked one per row (about 1,000px); allocation labels ungrouped ("1027" beside "1,067"); class ids on the axes.
23. **Recovery by class:** the recovery % appears on some bars and not others (a width test), although the legend promises it on every bar.
24. **Legends list series that are not drawn** ("Unexplained residual" with no residual, "Unrealized (removed)" with none unrealized).
25. **The reconciliation note uses a 3px coloured left border** (craft-floor refusal) and starts in lower case ("does not reconcile").
26. **Protection score axis runs 0–4** for a 1–5 scale.
27. **Tables clip in half-width and wide panels:** Earnings Update KPI changes and Early signals, the Fit view instrument table, Relative Value compensation and implied default. Every head is `nowrap`, so a column can never be narrower than its head.
28. **Panel heads drop "Full analysis" to a second row** whenever a note or tags are long (most collapsed panels, all half-width panels).
29. **Prose chips:** "( ⌀ G8)" leaves parentheses around a gap chip; runs of nine cite chips (C2 … C10) dominate key findings, red flags and the market table; inline `calc:` formulas render as mono boxes mid-sentence.
30. **Nested boxes:** restructuring-path cards and Fit limit lists draw a bordered box inside the panel (craft floor: nested cards).
31. **Breaches rows:** five rows in full negative fill on Larchmere's Fit panel read as a wall of colour.
32. **Fit limit rows overflow:** "(0.3) % NAV", "0.4118 % NAV", "2.7 notches" run into the next cell on the Distressed and Portfolio Front Pages.
33. **Blocked module view:** "Blocked Blocked: no market observation…"; every table repeats the module code and the Blocked state; all-n/a tables render as ten-row walls of n/a.
34. **Module view heads:** the table code repeats the module ("Fig. CP-4.4 CP-4"); chart panels carry "Model-authored" and "Host-computed", words outside the provenance vocabulary.
35. **Pinch point note** runs two sentences together ("falls out of liquidity The first date…").
36. **Names printed as codes:** `security_id` (bond names) and `kpi_id` (KPI labels) render in mono as ids.
37. **Keyboard:** the Credit Snapshot has 74 canvas tab stops: every cite chip and model mark in key findings, company, strengths and the call lines is its own stop (spec: one stop per block of figures, arrows within). Each chart's SVG root takes an extra stop before its marks.
38. **Relative Value Blocked call line** appends a meta sentence ("Its panels keep that reason…").

### P3

39. **House basis label:** the Model view says "House", the Front Page tables say "SSIM multiple" (data column). The content doc leaves the label to the owner.
40. **Fitch rating and outlook both n/a** print the same "G10 G11" chips twice.
41. **Honest tiles repeat a 3-line reason** three times (CLO, Indexed Loans, Indexed HY) and are not buttons, so the reason has no passport.

## Fixes

Each fix sits at the narrowest level that owns the cause (token, shared component, then page). Numbers refer to the findings above.

### Tokens and shared components (every view)

- **Verdict bar** (`render.js` `WB.verdictBar`, `WB.capCallLines`, `components.css`) [1, 13]: two head rows (title, question and tools; then Illustrative, analyst, date, honest notice), so tools never wrap to their own row. At most three call lines show, in each content doc's order (`WB.CALL_ORDER`; four on Covenant, whose call is four facts); the rest sit behind one disclosure that names them ("3 more: GATE · LIQUIDITY · MAIN RISK") and prints open. Bar height at 1440×900 is now 230–330px (was 260–410): every Front Page shows its call and the top of its first key panel; Earnings Update shows the headline table, Relative Value the levels table, Distressed the gate table.
- **Byline** (`WB.bylineNodes`, `WB.runMeta`) [13]: "Credit Research" with a quiet "Design fixture" tag, never the parenthetical; the Design system's Blocked specimen uses it too.
- **Honest tiles** (`WB.tile`) [41]: a short reason on the tile ("CP-6 did not run live"); the tile is a button whose passport holds the full reason and the producing module.
- **Provenance of judgements** (`WB.JUDGEMENT_NUMERIC`, `WB.cellOrigin`, `WB.tableTags`) [2]: the lender protection score reads illustrative in cells, chart bars (hatched) and panel tags.
- **One limit rule** (`WB.limitState`) [3]: Within with headroom under 10% of the limit is Tight in the Fit view and on the Front Pages (C-04 reads Tight in both).
- **Numbers** (`WB.fmtNum(s, {group})`, `renderCell`) [6]: amounts group (2,018); year-like values in id and date columns stay as years.
- **Words for ids** (`WB.columnKinds` `textual`/`periodIds`, `renderCell`, `WB.humanize`, `WB.rowLabel`, `WB.tableWhere`, `WB.claimName`, `WB.periodLabel`, `WB.enumWord`) [12, 36]: bond names and KPI labels read as text; `Q2_2026` reads "Q2 2026", `BASE` "Base"; `facility_id`/`portfolio_id` hide where the table names the facility or portfolio; single-word metric ids read as words ("Revenue", "Stock-based compensation"); claim classes read by name with the id small beside; source-id columns render `[C1]` as citation chips; "Metric ID" heads read "Metric"; "⟨date⟩" in block titles reads "the last Report" (or the Prior Case date).
- **Inline prose** (`WB.inline`, `WB.citeGroup`) [29]: a run of more than three citations is one chip ("C2–C10" or "9 sources") whose passport lists every source; "(G8)" renders as the chip alone; "(calc: …)" is a compact calculated chip with the formula in its passport (formulas with nested parentheses parse to their matching parenthesis).
- **Passports** (`WB.buildPassport`, `renderPassportEl`, `WB.renderPassport`) [12]: the head names the figure in words ("Restricted payments and leakage · Score"), the sub-line names the table and module ("Protection score by area chart, from Protection score · Covenants and legal (CP-4)"); short codes (C12, G8) stay in the head; raw table, Model-line and chart ids print small at the foot. Calculated inputs are labelled by column and value ("Current value · 2,993"). The Design system renders passports with the same function.
- **Charts** (`WB.chartSlot`, `charts.js`, `charts.css`) [11, 16–26]: no fixture summary anywhere; captions are for assistive technology where a panel or sub-heading names the chart; the source line names tables and modules in words ("Source: Covenant tests (Covenants and legal (CP-4)). Figures calculated by RBOT; select a mark for its passport.", raw ids as its tooltip); legends list only what is drawn; the fulcrum ring and word are negative; "Breached" everywhere; the reconciliation note is a wash with an icon, no coloured stripe, sentence case. Lines: end labels in a right gutter, de-collided; the last reported value sits above-left; "Projected" above the plot; "FY23 24 25" in tight bands; gap marks alternate height. Waterfalls with narrow bands turn on their side (step names as rows). Bullets in a narrow slot put the name above the track; groups read "Ratios (x)", "Amounts (US$ m)"; headroom reads "3.48x", "US$12m". Spread curve: unit above the axis, issuer labels flip left at the right edge, names in text. Value allocation: a 2×2 grid of horizontal waterfalls with class names. Recovery by class: the recovery % under every class. Protection score axis runs to 5. Dumbbell axes span the values. Category labels have a halo; rule labels do not print over bars.
- **Tables** (`components.css`) [27]: heads wrap, so a column is never wider than its widest value needs; row heads keep 120px.
- **Panel head** [28]: tools stay top-right; the title group wraps beside them.
- **Keyboard** (`WB.roving`, `WB.initRovingIn`, router) [37]: one tab stop per block of figures outside tables (tiles, call lines, key findings, lists, notes, prose); arrows, Home and End inside. Chart SVG roots leave the tab order. Credit Snapshot canvas tab stops: 74 to 39.
- **Print** (`shell.js`, `components.css`) [7]: endnote markers follow the figure in the flow ("[41–45]"), "Full analysis" links and disclosure toggles hide, disclosures print open.
- **Contrast** [8]: navigator zero-count chips use `--ink-3` (no signal colour on a zero); the Design system's "No on-navy variant" uses `--on-navy-2`. New token `--neg-wash` for Breaches rows and notes.

### Views and pages

- **Model** (`views.js`, `views.css`) [9, 12]: grid cell padding restored (selectors now beat `.mg td`); corner head left-aligned; limitations read by name ("Projection opens at LTM") with the code as a secondary chip; undated facilities by name; null counts in words.
- **Portfolio Fit view** [3, 14, 27]: Tight state; "2.5% NAV"; NAV and par "US$630,928,502"; size unit in the head ("Max size, US$"); rating bucket and limits touched under the instrument name, so Verdict, Uncapped, Cap and Final fit; a cap without a CP-6 row is a calculated figure with its rule as passport; limit rows are rows of the panel, not a box inside it.
- **Module view** (`pages.js`) [33, 34]: chart panels drop "Model-authored/Host-computed" and their duplicate caption; tables drop the repeated module code and Blocked state; an all-n/a table starts collapsed with "Every value is n/a: the module is Blocked"; "Blocked Blocked:" reads once.
- **Design system** [10, 8]: the Credit Score tile specimen uses its own scale; verdict-bar specimens are the Front Page's bar (title, standing, capped lines).
- **Credit Snapshot** [17]: the chart strip spans the panel. **Earnings Update** [1, 27]: no Recommendation tile (stated as a line, content doc 02); KPI changes table beside its dumbbell at full width; signals full width. **Relative Value** [1, 38]: talk rows behind a disclosure so the spread curve comes up the page; the Blocked line states the reason only; the implied-default table says a shared model and limitation once. **Covenant & Refinancing** [14, 35]: the springing note and pinch point read as sentences. **Distressed** [P1 brief items, 31, 30]: fulcrum line by class name ("First-lien claims, 82.2% recovery"); "the US$50m covenant floor"; Breaches rows washed; path cards and limit lists are rows, not nested boxes; limit values wrap as pairs. **Portfolio Decision** [14, 32]: tiles per Strategy on row one, per portfolio after the cap on row two ("Secured 2032s, Fits, no cap"); max size unit in the head.
- **Search**: chart twins and Design system specimens no longer appear as tables.

### Tests and tooling

- `tests/scenarios.js` [15]: the fixture-text check now looks for the parenthetical and raw table ids; the synthetic check reads the passport's kind, file and "TEST DATA rationale" heading; the Fit check uses a Pathway without Fit; 16 new checks cover the call cap and order, the byline, the first-viewport bar height, fulcrum names, the floor unit, the date placeholder, illustrative protection scores, grouped amounts, the key-findings tab stop, Model summaries and limitation names, the chart-mark passport, and the Tight limit in the Fit view. 96 checks.
- `check.py --shots [--tag]` covers every run's Front Page, two module views per run, Model, Fit, Evidence, Limitations and the Design system of two runs at both sizes, and writes a print PDF; a Chrome timeout is a logged retry, then a failing row, never a crash.
- `README.md` documents the additions.

## Confirming round (final build)

- `check.py --shots --tag w6-after`: 175 page loads pass (every run × view, ready, no errors); 112 screenshots; print PDF.
- `check.py --interact`: 96 checks, 0 failed, on two runs in a row. A third run had 2 failures in the anchor-scroll scenario (a fixed 200 ms wait); that scenario now waits for the scroll.
- Contrast: 0 text nodes below AA across the eight Front Pages, two Design systems, the Model, Portfolio Fit and two 1280 pages (about 17,900 nodes). Before: 2.3–2.7:1 zero-count chips on every page, and 1:1 for one Design system label.
- Verdict bar plus call lines at 1440×900, before → after (px): Snapshot 266 → 255, Quick 327 → 298, Earnings Update 398 → 301, Relative Value 280 → 268, Relative Value Blocked 345 → 297, Covenant 316 → 307, Distressed 399 → 301, Portfolio Decision 343 → 340. At 1280×800 Distressed 399 → 287.
- Keyboard (Credit Snapshot, trusted Tab presses): 74 → 39 canvas stops; order rail (11), navigator (39), canvas, inspector; every stop has a visible ring except chart marks, which show focus as a stroked hit area rather than an outline.

## Open

Ordered by severity. None blocks the gates. The brief's rule is to stop after the confirming round, so these are recorded, not fixed.

1. **First-viewport lines not fully met (P2).** The call and the first key panel fit on every Front Page at 1440×900. Some content docs ask for a second item in the first viewport, and it is still below the fold: Covenant (liquidity bridge; nine covenant tests make the first panel tall), Distressed (recovery chart, below the six-trigger gate table), Portfolio Decision (Fit bullets; two tile rows), Earnings Update (variance drivers). Meeting these needs a layout decision (side-by-side panels at 1440, or a shorter gate or covenant table on the Front Page). That is a composition change, not polish.
2. **Print (P2).** The Credit Snapshot prints on 12 A4 landscape pages: the page, then 237 endnotes. Content doc 00 §5 asks for the Front Page on one landscape page. This needs a print-specific composition (collapsed blocks stay collapsed, charts compact, endnotes on their own pages), and an owner decision on whether the endnotes count toward "one page".
3. **Module registers still show machine ids (P3).** CP-1 registers show `seg_las_vegas` beside "Las Vegas", `FY2025_END` / `JUN30_2026` period ids, `PERIOD_END`, `FY2025;H1_2026` and `synthetic-facts.json#…` locators. Claims and recoveries keep the class id (`C2-1L`) beside the class name. These are register tables whose ids are their content; hiding them is a judgement for the owner.
4. **Raw codes in data prose (P3).** CP-6 rationales mention `TEST_CLO_I` and `TEST_HY_I`. That is run text, so it is not rewritten.
5. **Gap ids on the Model strip (P3, carried from W2).** FY2023 and FY2024 leverage show "n/a" without their gap id, because `WB.cellGap` finds no matching item for the twin table.
6. **House basis label (owner).** The Model view says "House"; Front Page tables keep the data's "SSIM multiple" column. Content doc 07 leaves the label to the owner.
7. **Distressed honest state (owner, carried from W5).** The honest toggle states the real CAOS outcome for CZR over the fictional Larchmere fixture.
8. **Navigator tab stops (P3).** Each module row is its own tab stop: 21 on the full run, 39 navigator stops in all. A roving list would shorten the Tab path, but the navigator is links, so this is left as is.
9. **`tests/_w2gallery.html`** is W2's scratch gallery and is still in `tests/`. Delete it or keep it as a dev aid before commit (not this pass's file).
