# RBOT Workbench: the full interactive mock (Direction C)

Owner decision, 17 October 2026: Direction C, **Workbench**, is the chosen design (`design/claude-design-handoff/DECISION.md`). Build it here as **one** full interactive mock: a single self-contained HTML file that renders every test run, every view and every state, plus the design system. After it is complete, an Opus pass at xhigh effort polishes and refines it.

This mock is also the prototype of the Report renderer's front end: it renders the Report's own data (`rbot-run/1`) with vanilla JS, inline SVG charts and CSS tokens, exactly as the shipped Report must (no framework, no CDN library, no canvas, no images). Fonts load from Google Fonts in the mock; the shipped Report embeds them.

## 1. Inputs

| Input | Path | Use |
|---|---|---|
| The comp | `reference/direction-c-workbench.dc.html` (source), `reference/frames/direction-c-*.png` (rendered frames: 01 statement and Snapshot first viewport, 02–03 Snapshot full scroll, 03–04 Covenant & Refinancing, 05 module view, 06 Model, 07 navigation), `reference/vm.js`, `reference/charts.js` (its view-model and chart code, React-based: reference only, do not ship React) | The visual truth: layout, spacing, type, colour, components |
| Decision and refinements | `design/claude-design-handoff/DECISION.md` | Six refinements to apply (inputs labelled, quieter provenance in dense tables, no hue for module families, chart gaps on the axis, the honest state of the verdict bar, 1280×800/keyboard/print behaviour) |
| Content | `design/claude-design-handoff/content/00`–`07`, `colour-and-icons.md`, `provenance-and-states.md` | What each Front Page and view must say, the colour signals, icons, states |
| Data | `design/claude-design-handoff/data/test/*.run.json` (eight runs), `data/test/README.md`, `design/claude-design-handoff/data/front-pages-data.json` (`modules`: plain names and reader questions for all 18 modules) | The only data source. Never invent a figure |
| Chart semantics | `design/mockups/fixtures/inputs/interfaces-b4f39c3.md` §11.4 (chart map: what each `chart_id` draws from which columns) | Chart mapping |
| Chart reference code | `design/mockups/shared/charts.js` (RBOTCharts: accessible SVG marks, table twins, provenance in marks, n/a frames) | Port, restyle with the tokens |
| Brand | `brand/ssim-logo-horizontal-white.png` (on navy), `brand/README.md` | Rail mark; never redrawn or recoloured |

## 2. Output

```
design/mockups/workbench/
  WORKBENCH.md            this spec
  src/tokens.css          design tokens (CSS custom properties)
  src/base.css            reset, type, focus, selection, scrollbars, print base
  src/components.css      every component
  src/core.js             WB namespace: data access, citation and gap resolution, formatting, el() DOM helper, icon set
  src/shell.js            rail, run switcher, navigator, module switcher, router, inspector, search, keyboard, print
  src/render.js           generic renderers: panel, tables, marks, badges, verdict bar, condition line, markdown, module view
  src/charts.js           WB.chart(host, chartRecord): every chart kind from table-shaped data
  src/views.js            Model, Portfolio Fit, Evidence, Limitations, Design system
  src/frontpages.js       the six Front Page compositions
  build.py                inlines src/* + the eight runs + module metadata + the logo into one file
  dist/rbot-workbench.html
  shots/                  verification screenshots (git-ignored)
```

`python3 build.py` writes `dist/rbot-workbench.html` (one file, under 16 MB): `<style>` blocks for the CSS, `<script>` blocks for the JS, each run as `<script type="application/json" class="rbot-run" data-run="<file stem>">`, the module metadata as `<script type="application/json" id="rbot-modules">`, the logo as a base64 data URI. No external file except the Google Fonts stylesheet.

## 3. Visual system (from Direction C; tokens in `src/tokens.css`)

- **Brand:** navy `#000533` (rail, verdict bar, ink; secondary on navy `#C7CBE0`), electric blue `#0017E5` (selection, links, cited glyph, focus; hover `#0012B8`).
- **Neutral:** ground `#EEF0F5`, panels `#FFFFFF`, rules `#DDE1EA`, secondary ink `#4A5068`, tertiary for marks only.
- **Signal (meaning for the creditor; never alone):** positive forest `#0E7A46` (fill `#DCF5E7`), caution amber `#8A5300` (fill `#FFF1C7`), negative brick `#B3261E` (fill `#FBE0DD`; white on brick allowed), neutral slate; on navy the pale tints `#7EE2A8`, `#FFD166`, `#FFB4B0`. Chart comparison `#C4410C`; issuer series electric blue.
- **Type:** Red Hat Display (titles 18/600, panel heads 13/600 caps with 0.04em tracking), Red Hat Text (body 13.5/400 on 1.5, labels 11.5/500), Red Hat Mono (every figure in a table, every code, formula and id; 12px in tables; tabular numerals). Prose figures stay in Red Hat Text with tabular numerals.
- **Shape and depth:** square-cornered panels with a 1px rule; 2–4px radius only on chips, tiles, inputs; no shadows except floating layers (module switcher, search, run switcher).
- **Layout:** rail 56px navy; navigator 240px; inspector 300px; canvas fluid between. At widths below 1360px the navigator starts closed (toggle in the rail); rail and the `/` module switcher stay, and the inspector is a 36px strip that opens as an overlay on the canvas (no reflow) when a figure is selected (C2).

## 4. Data contract (read-only; `rbot-run/1`)

- `run_brief.tables` (issuer, Pathway, Primary tranches, portfolios, research questions, Prior Case); `pathway`, `depth`, `primary`, `front_page`, `plan`, `steps` (status accepted, skipped with reason, blocked).
- `handoffs.<id>`: `qa_status`, `front_matter`, `analysis_md` (Markdown with `[Cn]` citation tokens and occasional `calc: …` text), `gaps_md`, `tables` (`{columns, rows}` of strings; a `cite` column holds `[Cn]` markers and/or `calc: <formula>`), `citations` (`id`, `source`, `locator`, `excerpt`, `anchored`, `synthetic`, `origin`). Citation ids are local to their handoff.
- `model` (rbot-model/1): `columns` (kind FY, QUARTER, PYTD, YTD, LTM, PF_LTM, PROJECTED; case BASE/DOWNSIDE), `lines` (band 1–12, kind, unit, terms, cells with `value` or `reason`, `basis`, `stated`, `note`, `sources`), `house`, `capital_structure`, `ebitda_adjustments`, `maturity_wall`, `rate_deck`, `forecast`, `limitations`.
- `fit[]`: portfolio inputs, per-instrument rows (verdict, max size, binding limit, cap, final), limit headroom.
- `charts[]`: `chart_id`, `where` (`front_page:<block>`, `analysis:CP-x`, `model_tab`, or `analysis`), `kind` (bar, bullet, columns, dumbbell, lineStrip, lines, rangeStrip, riskMatrix, scatter, stackedBar, stackedColumns, tornado, waterfall), `tables`, `data` (`{table_id: {columns, rows}}`), `summary`. Declared n/a charts are listed in `fixture.n_a_charts`.
- `front_page_blocks[]`: `id`, `title`, `shown`, `reason`, `line`, `tables`.
- `limitations` (approval, cp5, unforeseen), `prior_case`, `fixture` (notes).

Provenance of a figure: a cell in a row whose `cite` holds only `calc:` is **calculated**; a row citing `[Cn]` with `synthetic: true` is **synthetic**; `[Cn]` real is **cited**; an empty or `—` value is **n/a** with the reason from `gaps_md` or the table's note; text the module wrote (analysis, analyst columns) is **model-written**; judgements (scales, recommendations, verdict words) are **illustrative** (every test run is a design fixture). Model cells use their own `basis` and `sources`.

## 5. Behaviour

- **Router:** `#/<run>/<view>[/<anchor>]`, views `front`, `module/<CP-x>`, `model`, `fit`, `evidence`, `limitations`, `system`. Default `#/czr-full-credit-assessment/front`. Back and forward work; every section, figure and citation has an anchor.
- **Run switcher:** the issuer block at the top of the navigator (or the rail) opens a list of the eight runs grouped by Pathway, each with its state tags (Primary, Prior Case, Blocked, Breaches, Fictional, Quick).
- **Rail:** icon-only with tooltips and accessible names: Front Page, Analysis, Model, Portfolio Fit (disabled with "Not in this Pathway" when the run has no FIT), Evidence, Limitations, Design system; bottom: search, "How to read a figure", print, navigator toggle.
- **Navigator:** issuer, Pathway, depth, Primary flag; modules in plan order with status icon (Pass, With limitations, Blocked, Not run), plain name and code; filter chips (All, With limitations, Pass, Blocked) with counts; "On this page" section list with scroll spy; no family hues (refinement 3).
- **Module switcher** (`/`): a search box over modules, figures and sources; Enter navigates.
- **Inspector:** tabs Source, Table, Gaps. Selecting any figure, chart mark or chip shows its passport: cited (source, locator, verbatim excerpt, "Used in n places"), calculated (formula with each input as a labelled chip that opens its own passport: refinement 1), synthetic (the TEST DATA rationale), gap (missing item, reason, effect), model-written, illustrative. Table tab: the focused chart's table twin. Gaps tab: every gap on the current page. Focus moves to the inspector heading; Escape returns focus to the figure.
- **Keyboard:** rail → navigator → canvas → inspector in tab order; one tab stop per table or chart, arrows inside; `/` opens the switcher; `?` opens "How to read a figure".
- **Print:** rail, navigator and inspector hidden; canvas full width; panels expanded; passports of the page's figures as numbered endnotes.
- **Honest state (refinement 5):** a verdict tile whose value the run did not produce reads "Not produced" with the reason and the module that would produce it; a switch in the verdict bar's header, "Real-run state" (state in the URL, `?state=real`; C2), replaces the illustrative verdicts with the real CAOS outcomes stated in `design/claude-design-handoff/data/caos-runs/README.md` (no Recommendation, Valuation not produced, relative value Unclear, distress gate Not met).

## 6. Views

- **Front Page** per `front_page`: a navy verdict bar (title, the page's question, Illustrative tag, analyst and date, position tiles, three call lines), then panels in the order and pairing of the content doc (`content/01`–`06`) and Direction C's frames. Use bespoke panel bodies for the key blocks (key findings, company and operating model, chart strip, capital structure with tabs, covenant tests, liquidity runway, recoveries, Fit) and the generic table panel elsewhere. A block with `shown: false` is a condition line.
- **Module view** (Direction C frame 05): title, code, status chip with reason; Question; headline (first paragraph of `analysis_md`) with a Model mark and Sources disclosure; panels for the module's charts (`where` = `analysis:CP-x` or `analysis` with this module's tables) and every table; Analysis text; Gaps and limitations; previous and next.
- **Model** (frame 06, content/07): summary first (house view ladder, multiples and EV, model limitations, the chart strip), then the twelve bands as a navigable grid: band list in the navigator, column groups (snapshot by default; quarters, YTD, PF-LTM, Base and Downside opt-in), sticky row labels and heads, every cell a figure with its basis and passport; null cells show their reason code compactly.
- **Portfolio Fit:** per portfolio: limits as CSS headroom bars, instruments with verdict, max size, binding limit, cap and final Recommendation; the proposed trade; portfolios not attached.
- **Evidence:** every citation in the run, filterable (real, synthetic, by source file, by module), each with excerpt and the places it is used.
- **Limitations:** approval, evidence-check and unforeseen limitations, plus the not-run steps.
- **Design system:** tokens (swatches with contrast values, type scale, spacing) and every component in every state, rendered live from the same code: verdict bar (illustrative, honest, Blocked), panel, dense table (1 and 20 rows, long text, n/a), kv table, period grid, each chart kind, status and scale marks, provenance marks (quiet and full), gap chip, icons, navigator rows, inspector passports, condition line, empty and not-run states.

## 7. Quality bar and gates

- Craft floor (`~/.claude/skills/impeccable/reference/craft-floor.md`): contrast AA, spacing rhythm, no eyebrow labels, no gradients, no glyph-emoji icons (one inline SVG icon set, 1.5px stroke, 16px), themed focus rings, selection, scrollbars, tabular numerals.
- No `innerHTML` with data (build DOM with `el()`); no console errors; no library.
- Every number on screen comes from a run file and opens a passport.
- Gates (headless Chrome against `dist/rbot-workbench.html` served from `http://127.0.0.1:8765/design/mockups/workbench/dist/rbot-workbench.html`): for every run × view (front, each module, model, fit where present, evidence, limitations, system), `document.documentElement.dataset.ready === "1"` and `window.__wbErrors` empty (the app records `error` and `unhandledrejection` events there and mirrors the count to `data-errors` on `<html>`); screenshots at 1440×900 and 1280×800 of every Front Page, one module view, Model, Fit and the design system, read and judged against the frames.
