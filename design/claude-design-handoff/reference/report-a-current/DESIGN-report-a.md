---
name: RBOT Report
description: The State Street house Credit Snapshot as a numbered committee paper; an app shell of hash-routed views where every figure opens to its source.
colors:
  navy: "#000533"
  blue: "#0017E5"
  blue-deep: "#0012B8"
  ground: "#F0F2F5"
  sheet: "#FFFFFF"
  grey-100: "#E1E3E6"
  grey-200: "#C5C8CC"
  grey-400: "#8D939D"
  grey-600: "#55585E"
  soft-blue: "#CBE4FE"
  soft-blue-50: "#E7F5FF"
  mint: "#1EFF8F"
  mint-soft: "#A5FFD2"
  lemon: "#F7FF99"
  positive: "#0F8048"
  positive-text: "#0C6639"
  negative: "#D4625D"
  negative-text: "#A6100F"
  caution-text: "#7A4A00"
  caution-fill: "#FFF8D6"
  negative-on-navy: "#FFB4B0"
  chart-orange: "#C4410C"
  chart-mid-blue: "#2B8FD6"
  risk-high: "#F6D4D2"
typography:
  report-title:
    fontFamily: "Inter Tight, Inter, system-ui, sans-serif"
    fontSize: "1.814rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  view-title:
    fontFamily: "Inter Tight, Inter, system-ui, sans-serif"
    fontSize: "1.512rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  section-title:
    fontFamily: "Inter Tight, Inter, system-ui, sans-serif"
    fontSize: "1.26rem"
    fontWeight: 800
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  subhead:
    fontFamily: "Inter Tight, Inter, system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 700
    lineHeight: 1.2
  headline-finding:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 400
    lineHeight: 1.5
  bar:
    fontFamily: "Inter Tight, Inter, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "0.04em"
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  table:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.35
    fontFeature: "\"tnum\" 1, \"lnum\" 1"
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.35
rounded:
  chip: "2px"
spacing:
  s-1: "4px"
  s-2: "8px"
  s-3: "12px"
  s-4: "16px"
  s-5: "24px"
  s-6: "32px"
  s-7: "48px"
  s-8: "64px"
components:
  section-bar:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.sheet}"
    typography: "{typography.bar}"
    padding: "0.3rem 0.6rem"
    height: "2.25rem"
  paper-section-head:
    textColor: "{colors.navy}"
    typography: "{typography.section-title}"
    padding: "8px 0"
    height: "2.75rem"
  button:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.blue}"
    rounded: "{rounded.chip}"
    padding: "0.3rem 0.8rem"
    height: "2rem"
  button-hover:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.sheet}"
  button-quiet:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.navy}"
    rounded: "{rounded.chip}"
    padding: "0.15rem 0.6rem"
    height: "1.75rem"
  scale-badge:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.navy}"
    rounded: "{rounded.chip}"
    padding: "0.1rem 0.45rem 0.1rem 0.15rem"
  scale-badge-on-navy:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.chip}"
    padding: "0.2rem 0.6rem 0.2rem 0.2rem"
  status-pass:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.positive-text}"
    rounded: "{rounded.chip}"
    padding: "0.05rem 0.45rem 0.05rem 0.35rem"
  status-with-limitations:
    backgroundColor: "{colors.caution-fill}"
    textColor: "{colors.caution-text}"
    rounded: "{rounded.chip}"
    padding: "0.05rem 0.45rem 0.05rem 0.35rem"
  status-blocked:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.negative-text}"
    rounded: "{rounded.chip}"
    padding: "0.05rem 0.45rem 0.05rem 0.35rem"
  status-breach:
    backgroundColor: "{colors.negative-text}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.chip}"
    padding: "0.05rem 0.45rem 0.05rem 0.35rem"
  cite-chip:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.blue}"
    rounded: "{rounded.chip}"
    padding: "0 0.3rem"
  nav-link:
    textColor: "{colors.sheet}"
    typography: "{typography.table}"
    padding: "0.3rem 1rem"
    height: "2rem"
  nav-link-current:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.sheet}"
  headline-box:
    backgroundColor: "{colors.soft-blue-50}"
    textColor: "{colors.navy}"
    typography: "{typography.headline-finding}"
    padding: "12px 16px"
---

# Design System: RBOT Report

<!-- Recorded from the shipped Report A mockup (design/mockups/report-a-ic-paper.html, report-a.css, report-a.js, shared/tokens.css, shared/charts.js) at c8e2742. Binding template brief for Plan 07, the Report renderer. Where shared/tokens.css and report-a.css disagree, report-a.css is what ships and is what this file records. -->

## Overview

**Creative North Star: "The Committee Paper"**

The Report is a State Street investment-committee paper rendered as an app shell. A navy navigation pane holds the Report's eleven destinations; the main column shows one view at a time. Page one is the Credit Snapshot, the house Excel template PMs already know: navy section bars with white bold capitals, dense bordered tables, the cool grey ground, the logo on navy. Every other view is a white paper sheet whose sections are ruled by a 3px navy line. View codes and figure numbers (S, CP-n, M, PF, E; Fig. CP-1.2) are the citable anchors, standing in for numbered sections.

Density is high and deliberate: 13px tables, 14px body, 12px small print, a 4px spacing rhythm, square corners. The interface is flat. The only colour that carries meaning is status (Pass, With limitations, Blocked) and Portfolio Fit (Watch, Breaches). Every house scale is neutral, so the word carries the call. Provenance is drawn into the figure itself: a corner mark on the value, a dotted rule on model-written blocks, a dashed outline on illustrative judgements, an n/a with its gap id where the sources are silent.

Confirmed rejections (owner rounds, 2026-10-11): the dashboard of cards and KPI tiles; tone-coloured scales; margin notes as the citation carrier; section numbering in place of view codes.

**Key Characteristics:**
- App shell: a 16.5rem navy pane, hash-routed views, one view visible.
- The Snapshot keeps the template's framed blocks under navy bars; the other views are white papers with navy-ruled sections.
- Neutral scales: the call band is white on navy, words carry meaning.
- Provenance by shape: triangle for cited, square for calculated, dashes for illustrative, dots for model.
- Every block collapses, says its state in words, and links one step to its owning module.
- Every chart has a table twin, an n/a frame when it cannot draw, and provenance in its marks.

## Colors

A two-colour house pair (deep navy and electric blue) on a cool grey ground, with a grey ramp for structure and status colours held back for status alone.

### Primary
- **House Navy** (navy): section bars, the pane, the title band, all headings and body ink (body text is navy, not black). Also the calculated-figure mark, table totals rules, the scale position box, and the 1px block frame.
- **Electric Blue** (blue): interaction only. Links, buttons, the focus ring on light grounds, the cited-figure corner mark, the source chip, and the issuer's series in charts (chart series 1). Hover and pressed states darken to **Pressed Blue** (blue-deep).

### Secondary
- **Soft Blue** (soft-blue): selection, secondary text on navy (as on-navy-2), nav hover tint at 12% and current tint at 18%.
- **Faint Blue** (soft-blue-50): table row hover, the headline-finding box, the Key findings "Main risk" line, the calculated chip fill.

### Tertiary (state on navy only)
- **Mint** (mint): the active state on navy. The current-view rule in the pane, the focus ring on navy, hover on navy links. Never on white.
- **Mint Soft** (mint-soft): Pass status on navy.
- **Lemon** (lemon): With limitations and Watch status on navy; search-hit highlight in the pane; the mockup banner.

### Status (the only meaningful colour)
- **Pass Green** (positive-text): Pass status text and icon on white. **Positive** (positive) is reserved for marks and fills.
- **Caution Brown on Cream** (caution-text on caution-fill): With limitations and Watch on white.
- **Critical Red** (negative-text): Blocked status text, the Breaches chip fill (white text), the chart residual and breach colour. **Negative** (negative) is for marks only, never text on white. **Negative on Navy** (negative-on-navy) is Blocked on navy.

### Neutral
- **Cool Grey Ground** (ground): the page ground behind sheets; the n/a chart frame fill; popover excerpt fill.
- **Sheet White** (sheet): paper sheets, tables, blocks, chips.
- **Rule Grey** (grey-100): table rules, table head fill, sub-bars ("Strengths", "Weaknesses"), chart gridlines.
- **Sheet Edge** (grey-200): paper-sheet border, quiet button border, view-code tag border.
- **Mark Grey** (grey-400): chart neutral series, stated totals, the n/a frame's dashed border. Never text (3.09:1 on white).
- **Slate** (grey-600): secondary text (ink-2), axis text, the Model tag, the Synthetic tag and synthetic corner mark, chart series 4.

### Chart palette
Series order: blue (1), **Burnt Orange** (chart-orange, 2), navy (3, totals), slate (4), **Mid Blue** (chart-mid-blue, 5), then grey-400 as the sixth series and peers. Critical red is for unexplained residuals and breaches only. Risk-matrix zones fill ground (low), soft-blue (medium) and **Risk Tint** (risk-high). Lines also differ by point shape and dash so no series rests on hue.

### Named Rules
**The Word Carries the Call Rule.** Every house scale (Recommendation, Valuation, Credit Score, Credit Direction, Sector Outlook) is white on navy or navy on white, in the call band, in tables and in the Key. Colour is used for status (Pass, With limitations, Blocked) and Portfolio Fit outcomes (Watch, Breaches) and nothing else. A green or red scale box tilts the call; it does not ship.

**The Blue Is a Verb Rule.** Electric blue marks what can be clicked or focused, plus the cited mark and the issuer series. Labels, numerals and figure numbers are navy or slate, never blue.

**The Mint Lives on Navy Rule.** Mint, mint-soft and lemon appear only on navy grounds. On white the same states use the status colours above.

## Typography

**Display Font:** Inter Tight (with Inter, system-ui)
**Body Font:** Inter (with system-ui)
**Label/Mono Font:** Inter for labels; ui-monospace (SF Mono, Menlo) only for formulas and file paths in the popover and Evidence table.

**Character:** A single grotesque family in two cuts: Inter Tight at 700–800 for the house bars and headings, Inter for reading and tables. The scale steps by 1.2 from a 14px body.

### Hierarchy
- **Report title** (800, 29px, 1.2, -0.02em): the H1 of a paper view (module, Model, Portfolio Fit, Evidence, Limitations). The Snapshot's H1 (the issuer) sits in the title band at 24.2px.
- **View title** (700, 24.2px, 1.2): the Snapshot H1 in the title band; folded-module titles inside Evidence and Portfolio Fit.
- **Section title** (800, 20.2px, 1.25, -0.01em, sentence case): the head of each collapsible paper section; also the issuer name in the pane.
- **Subhead** (700, 16.8px): sub-heads inside sections. The headline finding is set at the same 16.8px in Inter 400, line-height 1.5, capped at 62ch.
- **Bar** (700, 13px, 0.04em, uppercase): the navy section bars of the Snapshot blocks. Capitals belong to the bar, the house template's own device.
- **Body** (400, 14px, 1.5): prose, capped at 64ch (`--measure`).
- **Table** (400, 13px, 1.35, tabular lining numerals on number cells): every data table, nav links, chart labels.
- **Label** (600, 12px): captions, chips, axis labels, figure numbers, contents line, source lines, call-band keys.

### Named Rules
**The Numbers Align Rule.** Tabular lining numerals apply to numbers only (`.num` cells, chart text, chips, figure refs), never to running prose. Negatives print in parentheses as the filings do; colour is not the carrier.

**The Capitals Belong to the Bar Rule.** Uppercase is used where the house uses it: navy bars, the ILLUSTRATIVE and SYNTHETIC tags, the pane's ANALYSIS group heading. Headings inside papers are sentence case.

## Layout

**Shell.** A two-column grid: a 16.5rem sticky navy pane, full viewport height, scrolling on its own, and a fluid main column (`minmax(0, 1fr)`). The pane holds, top to bottom: the white horizontal SSIM logo (22px high), the issuer (20.2px, 800) and run line (12px, soft blue: pathway, period, analysis date), "Search the Report /" with its input, then the navigation. One view shows at a time; the rest are `hidden`.

**The 11 destinations.** Snapshot; an "Analysis" group heading with a tally line ("6 modules: 5 with limitations, 1 pass") over the six module views, each with its plain name, its RBOT code (CP-0, CP-1, CP-1B, CP-2, CP-3, CP-4) and a round status mark; then Model, Portfolio Fit, Evidence and Limitations. All 11 are visible without scrolling at 1280×800. CP-5 (Evidence checks) renders inside Evidence and CP-6 (Portfolio Fit summary) inside Portfolio Fit as folded sections; their own addresses still resolve. Nothing else sits in the pane: section lists, the Key and the view tools live in the view.

**Hash routes.** `#snapshot` (default and fallback), `#module-cp-0`, `#module-cp-1`, `#module-cp-1b`, `#module-cp-2`, `#module-cp-3`, `#module-cp-4`, `#model`, `#portfolio-fit`, `#evidence`, `#limitations`. Folded modules keep `#module-cp-5` and `#module-cp-6` as anchors inside their host view. Every section, figure and record has its own anchor (`#cp-1-capital-structure`, `#cp-1-gaps`, `#model-credit-metrics`, `#key-findings`, `#cite-C12`, `#calc-K3`, `#limit-G8`); any anchor routes to its owning view, opens every closed section around it, scrolls to it and moves focus to it. Back restores the prior scroll position. `#main` (the skip link) lands on the current view's H1.

**View header.** H1, then (on module views) the grey-bordered RBOT code tag, then right-aligned header tools: "How to read a figure" (opens the Key popover) and "Collapse all / Expand all" (state follows the open sections). Under the H1 sits the contents line: "On this page" in bold slate, then the view's sections as blue links separated by middots, 12px, wrapping. The section in view carries `aria-current="location"` (navy, bold, 2px underline). A view with fewer than two sections shows no contents line.

**Snapshot grid.** A navy title band, then a 12-column grid with an 8px gap: Key findings (5) beside Company and operating model (7); Model chart strip (12, four plots in a row); Capital structure (7) beside EBITDA adjustments (5); Financials and credit metrics (12, tables 7fr beside a chart 5fr); then Strengths and weaknesses, Relative value, Company profile, Transaction and Committee challenge. Acceptance: at 1440×900 all four strip plots sit in the first viewport.

**Paper views.** A white sheet with a 1px grey-200 border, 24px from the pane and edges, padded 24px top and 32px sides. Modules end in a previous/next pager above a 3px navy rule.

**Spacing.** 4px rhythm, `s-1` to `s-8`. Table cells pad 0.2rem by 0.5rem; block bodies 8px by 12px; paper sections are separated by 16px and a 3px navy rule.

**Breakpoints.** 1500px: sheet margins tighten to 16px. 1400px: call-band boxes step down to 14px words. 1150px: Snapshot 7/5 pairs stack; the chart strip goes 2×2; the call band goes to three columns. 1000px: the pane becomes a sticky top bar (logo, Menu button, current view name) with the navigation in a drop-down sheet; nav targets grow to 2.75rem; all two-column groups stack. 760px and 640px: further stacking. Phone width (390px) is out of scope (see Known limits).

**Print.** Landscape, 8mm margins. The Snapshot is re-flowed into its desktop grid and zoomed to fit one page (985×712 CSS px); every following view starts on a new page with every section open. The pane, tools, contents lines, pagers, popovers and block footers do not print. The one-page Snapshot drops Relative value, Company profile, Transaction, Committee challenge, chart twins, chart summaries and source notes.

### Known limits
- **Phone (390px) is out of scope.** The Financials tables overprint and call-band badges overlap at 390px. Desktop on wide monitors, laptop minimum, is the platform.
- **Fonts must be embedded by the renderer.** The mockup loads Inter and Inter Tight from Google Fonts; the Report opens from disk with no network, so Plan 07 embeds both (base64 `@font-face` or files beside the Report).
- **The Committee challenge is not printed in the one-page Snapshot print.** It prints in full with its module view (CP-2) on the later pages.

## Elevation & Depth

Flat. Depth comes from ground versus sheet (cool grey under white), the 1px navy block frame, and the navy bars and pane. Two floating layers carry a soft navy-tinted shadow because they sit over content: the source popover and the "How to read a figure" popover. Nothing else is lifted; no gradients anywhere, including charts.

### Shadow Vocabulary
- **Popover** (`box-shadow: 0 6px 18px rgba(0, 5, 51, 0.16)`): the source passport.
- **Key popover** (`box-shadow: 0 6px 18px rgba(0, 5, 51, 0.18)`): "How to read a figure".

### Named Rules
**The Flat Paper Rule.** Blocks, sheets, cards and charts are flat at rest and on hover. Only a popover that floats over the paper casts a shadow.

## Shapes

Square house. The one radius is 2px, on chips, tags, buttons, the search input, kbd keys and the chart tooltip. Blocks, sheets, tables, bars, the headline box and charts have square corners; bar ends in charts are square. Two shapes are round by meaning: the pane's status mark (a 1.15rem circle around the status icon) and the dashed circle inside the ILLUSTRATIVE tag.

Lines do the structural work: 1px navy frame for Snapshot blocks; 3px navy top rule for paper sections, view-head facts and the pager; 1px grey-100 rules between rows and cells; 1px navy rules above and below table totals; a dotted slate rule at the top of a model-written block body; dashed borders for illustrative, gaps and the n/a chart frame.

## Components

### Collapsible block bars
The one disclosure affordance. A `details` whose summary is the bar: a border-drawn chevron (rotates 160ms, `cubic-bezier(0.16, 1, 0.3, 1)`, off under reduced motion), the title, a quiet meta note, tags (ILLUSTRATIVE, SYNTHETIC, Model), and the state in words at the right ("Collapse" / "Expand", underlined, 12px).
- **Snapshot block:** navy bar (2.25rem min height), uppercase 13px Inter Tight 700, meta in soft blue; 1px navy frame. Hover turns the state word mint; focus is a mint ring inset 4px.
- **Paper section:** no fill; a 3px navy top rule; sentence-case 20.2px 800 navy title; 2.75rem min height; state word in blue.
- **Footer line:** under a Snapshot block, a 12px slate source line on the left and a blue "Full analysis" link (24px target) on the right that goes to the owning module section. The link never sits inside the toggle.
- Key findings carries `data-keep` and is never collapsed by "Collapse all".

### Call band (Snapshot title band)
Navy band, full main-column width. Row 1: the issuer H1 and the header tools. Row 2: run meta, middot-separated, 12px soft blue. Then the contents line. Then the call: "Analyst recommendation" with its ILLUSTRATIVE tag and "By Credit Research · date".
- **Six items** in one row (`repeat(6, max-content)`, spaced between): Recommendation for CLO, Indexed Loans and Indexed HY; a soft-blue divider; Valuation, Credit Score and Credit Direction. Each is a 12px soft-blue key over a large scale badge: a white box holding the navy position (2.1rem, 24.2px numeral, or an arrow for Credit Direction), the word in white at 16.8px bold, and a five-step rising meter.
- **Neutral:** every position box is white on navy whatever the value. No tone colour appears in the band.
- **Portfolio Fit line:** key "Portfolio Fit", then the portfolio name in bold, its overall status chip, each Breaches chip with the instrument and limit, the Watch headroom in words, a "Details in Portfolio Fit" link and a SYNTHETIC tag.
- **Instrument line:** key "Instrument", then the Strategy in bold, the preferred-instrument sentence with ILLUSTRATIVE, and, where Fit flags that instrument, its status chip and reason with a "see Portfolio Fit" link and SYNTHETIC.

### Module view anatomy
In order: H1 with RBOT code tag and header tools; the contents line; two facts side by side under 3px navy rules: **Question:** (bold run-in, then the reader question in italic slate) and **Status** (bold key with the status chip, then the reason with gap chips that link to this view's gaps); the **headline finding** in a faint-blue box with a dotted slate border, 16.8px, figures as buttons, one Model tag; **Sources (n)**, a blue disclosure listing the headline's citations; the paper sections (figures, detailed tables, module extras); **Gaps and limitations**, always the last section, the one place each gap is stated, as a table; then the pager. A module with no headline says so in a slate note.

### Navigation pane
- **Links:** 13px white on navy, 2rem min height, 3px transparent left rule; top-level destinations in Inter Tight 700 at 14px. Hover tints soft blue at 12%. Current: `aria-current="page"`, soft blue at 18%, mint left rule, bold.
- **Module rows:** plain name, then the RBOT code in 12px soft blue, then the round status mark. The status word appears in a white tag on hover and focus and is always read aloud.
- **Group:** "ANALYSIS" in 12px Inter Tight uppercase, 0.08em tracking, soft blue, with the module tally beneath.

### Provenance grammar
The figure itself is the button. Its origin is a mark, never colour alone:
- **Cited:** a 6px electric-blue corner triangle (top right of the cell, or after the figure in prose).
- **Calculated:** a 5px navy corner square.
- **Synthetic:** a slate corner triangle; blocks carry a SYNTHETIC tag (slate border, uppercase 12px).
- **ILLUSTRATIVE:** an uppercase 12px tag with a 1px dashed navy border and a dashed circle; judgement values carry a dashed outline.
- **Model:** a "Model" tag with a 1px dashed slate border; a model-written block body has a dotted slate top rule; model-authored phrases a dotted underline.
- **n/a:** italic slate "n/a" with a dashed grey underline in cells; the gap chip reads "n/a G8" with a dashed slate border. Inside a module view the gap chip is a link to that view's Gaps and limitations.
- **Source chip** ([C12], blue bordered) and **calculation chip** (= K3, navy bordered on faint blue) are used in source notes and the Key, not in running figures.
- **Popover passport:** a 28rem white panel, 1px navy border and a 4px navy top edge, with the soft shadow. The head shows the id in Inter Tight bold and the kind in 12px uppercase slate. A definition list follows. Cited: Served as, File, Locator, then the verbatim excerpt in a ground-filled quote with a navy left rule (scrolls past 12rem). Calculated: Served as, Formula (monospace), and its input chips, which open in turn. Gap: Missing item (plain words), Reason. Synthetic: the synthetic file and row. A Close button (24px minimum). Escape closes and returns focus.
- **Key:** "How to read a figure" lists every mark above, the house scale example with "The word carries the meaning; colour does not", the three pane status marks, and the keys (/, arrows, Esc).

### Figures and charts
- **Numbering:** "Fig. " plus the pane label of the view that draws it first, then a running number: Fig. S.n (Snapshot), Fig. CP-n.n (a module, e.g. CP-1.1, CP-1B.2), Fig. M.n (Model), Fig. PF.n (Portfolio Fit), Fig. E.n (Evidence). A figure redrawn in another view keeps its first number. The number is 12px Inter Tight bold slate, before a 14px navy title.
- **Head:** number, title, one-sentence summary (13px slate; screen-reader-only in the strip). **Foot:** legend (provenance entries added automatically), a "Show table" toggle, and "Source:" in 12px slate.
- **Kinds:** line strip, grouped columns, waterfall (bridge), bullet, stacked columns (maturity wall), range strip, scatter with fitted curve, dumbbell, risk matrix.
- **Provenance in the marks:** cited, calculated and synthetic marks are solid; model-authored and illustrative are hatched, hollow or dashed; projected values dash the segment with a "Projected" divider; a gap breaks the line and shows a labelled n/a; a residual is critical red and named "unexplained". One value axis holds zero; bridges and ranges float.
- **n/a frame:** a chart the data cannot draw keeps its number, title and source; the plot becomes a 9rem dashed grey-400 frame on ground with a white note: "n/a: not drawn", the missing input, and its gap chips.
- **Table twin:** every chart has one, opened by "Show table", printing exact values and gap reasons.

### Buttons
- **Shape:** 2px corners, 1px border, 2rem min height (1.75rem in view headers), 13px 600.
- **Primary:** white with blue text and border; hover and pressed fill blue with white text.
- **Quiet:** grey-200 border, navy text; hover blue border on faint blue. On the navy title band: transparent, soft-blue border, white text; hover white fill with navy text.
- **Disabled:** dashed grey-400 border on ground.

### Status chips
12px bold word with a 0.7rem icon (tick, half-filled circle, slashed circle, warning triangle, cross, dash), 1px border in the text colour, 2px corners. Pass, With limitations (the reader word for the data's Restricted), Blocked; Fits, Watch, Breaches for Portfolio Fit (Breaches is filled critical red). On navy the chip goes transparent with mint-soft, lemon or pale red.

### Data tables
13px, collapsed borders, 1px grey-100 row rules, a grey-100 head with a grey-400 bottom rule, units on a second line under the head, numbers right-aligned in tabular figures, totals bold between navy rules, italic slate sub-rows, faint-blue row hover. Wide tables scroll inside their block; long ones scroll with a sticky head.

## Accessibility baselines

Measured, with the pass that measured them:
- **Contrast (computed from tokens, this pass):** navy on white 19.64:1; blue on white 9.32:1; slate on white 7.13:1, on ground 6.36:1, on grey-100 5.55:1; soft blue on navy 15.02:1; mint on navy 14.73:1; lemon on navy 18.44:1; positive-text 7.06:1; negative-text 7.77:1; caution-text on caution-fill 7.0:1. grey-400 on white is 3.09:1, so it is marks only. Blue on navy is 2.11:1, so focus on navy is mint.
- **Rendered contrast (critique 2, 2026-10-11T17:45Z, before the last two fix passes):** 0 failures in 2,660 text nodes; 0 heading skips, duplicate ids or tap-target failures.
- **Tab stops:** one per block of provenance buttons (roving focus in each table, list or paragraph; arrows, Home and End move within) and one per chart (arrows move between marks), plus each chart's "Show table". The Snapshot main column measured 45 tab stops at critique 2 (down from about 219 before roving focus).
- **Hit area:** 24px minimum. Inline chips and figure buttons carry an absolutely positioned 24px `.hit`; chart marks carry a 24px hit rect; the popover Close button, "Full analysis" links and Sources disclosures are 24px tall. Below 1000px nav links and the Menu button are 2.75rem.
- **Focus:** 2px blue ring, 2px offset, on light grounds; 2px mint ring on navy (3px on the skip link).
- **Motion:** only the chevron rotates; `prefers-reduced-motion` removes all transitions.
- **Not re-measured this pass:** rendered contrast, tab-stop counts and target sizes after commits e5ff058 and c8e2742.

## Do's and Don'ts

### Do:
- **Do** keep every house scale neutral: navy position box on white, white box on navy, the word in bold beside it, the five-step meter after it.
- **Do** keep the pane to the Report's 11 destinations, all visible at 1280×800; put each view's sections in its "On this page" contents line under the H1.
- **Do** build every block as one collapsible bar that names its state in words ("Collapse" / "Expand") and links its owning module from the footer line, never from inside the toggle.
- **Do** make the figure itself the button, marked by origin: blue corner triangle for cited, navy corner square for calculated, slate triangle for synthetic.
- **Do** tag every judgement ILLUSTRATIVE and every model-written block Model, once per block.
- **Do** show a missing value as n/a with its gap id and reason, in cells, prose and charts; state each gap once, under the module's Gaps and limitations.
- **Do** number figures by the pane label of the view that first draws them (Fig. S.1, CP-1.2, M.1, PF.1, E.1) and keep that number wherever the figure is redrawn.
- **Do** give every chart a table twin, provenance in its marks, and an n/a frame when it cannot draw.
- **Do** give every interactive target a 24px minimum hit area, and use mint for focus on navy.

### Don't:
- **Don't** colour a scale. Green, grey or red position boxes for Recommendation, Valuation, Credit Score, Credit Direction or Sector Outlook do not ship, in the band, in tables or in the Key.
- **Don't** use colour for anything except status (Pass, With limitations, Blocked) and Portfolio Fit outcomes (Watch, Breaches), and always pair it with an icon and a word.
- **Don't** put electric blue on labels, numerals or figure numbers; blue means clickable.
- **Don't** put mint, mint-soft or lemon on white; they are states on navy only.
- **Don't** use grey-400 for text; it is a mark colour (3.09:1).
- **Don't** set a small uppercase kicker label above a heading; uppercase belongs to the navy bars, the ILLUSTRATIVE and SYNTHETIC tags and the pane group heading.
- **Don't** add shadows, gradients or rounded cards; only floating popovers cast a shadow, and the radius is 2px on chips and buttons.
- **Don't** repeat a gap, a headline or a figure within a module view; each thing is said once.
- **Don't** load fonts from the network in a shipped Report; embed Inter and Inter Tight.
