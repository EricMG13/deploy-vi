# RBOT Workbench: foundation and API contract

The shell, the data layer and the generic renderers of the Direction C mock (spec: `WORKBENCH.md`). The agents that build the charts, Model, Portfolio Fit, Design system and the six Front Pages work on this API. It is a contract: change it only by adding to it.

```
python3 build.py                 # writes dist/rbot-workbench.html (one file, fails over 16 MB)
python3 check.py                 # every run x every registered view x every module: data-ready="1", data-errors="0"
python3 check.py --shots [--tag before]   # also 1440x900 and 1280x800 screenshots into shots/<tag>/: every run's Front Page,
                                          # two module views, Model, Fit, Evidence, Limitations, the Design system of two runs,
                                          # and a print PDF of the Credit Snapshot
python3 check.py --interact      # interaction scenarios (tests/scenarios.js) in headless Chrome
python3 check.py --shot '#/czr-full-credit-assessment/front' --size 1280x800 --name x \
                 --do 'click::.fig-cited||wait::200'      # one ad-hoc screenshot, with optional steps
```

`check.py` starts `python3 -m http.server 8765 --bind 127.0.0.1 --directory <repo root>` when nothing listens on 8765. Open the Report at `http://127.0.0.1:8765/design/mockups/workbench/dist/rbot-workbench.html`. `dist/` and `shots/` are git-ignored. `tests/` is test code and is not part of the build.

## Build order (fixed)

`build.py` inlines every `src/*.css` and `src/*.js`:

| | order |
|---|---|
| CSS | `tokens.css`, `base.css`, `components.css`, `charts.css`, `views.css`, `frontpages.css`, then any other `src/*.css` alphabetically |
| JS | `core.js`, `render.js`, `pages.js`, `charts.js`, `views.js`, `frontpages.js`, then any other `src/*.js` alphabetically, `shell.js` last |

`shell.js` starts the app (`WB.start()`) when the document is ready, so every view registered by an earlier file is known by then. `core.js` owns the registries (`WB.views`, `WB.frontPages`); a later file registering the same name wins, so `frontpages.js` replaces the generic Front Page and `views.js` adds `model`, `fit`, `system`.

Embedded data: each run as `<script type="application/json" class="rbot-run" data-run="<file stem>">`, the module names and reader questions as `#rbot-modules` (`{id, name, question}` from `front-pages-data.json` `modules`), the logo as the CSS variable `--logo-url`. Only the active run is parsed (`WB.loadRun`); the run switcher parses the others on demand.

## Rules for every file

- No `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, library, canvas or image. Build DOM with `WB.el` / `WB.svg` / `WB.icon`. `WB.el` throws on an `html` attribute.
- No stub or invented number. A value missing from the run is an n/a with its reason (`WB.gapChip`), never zero or blank.
- No catch-all that hides a failure: errors are recorded in `window.__wbErrors` and mirrored to `<html data-errors>`; a view that throws shows a visible error and rethrows.
- Colour is a signal (tokens `--pos`, `--cau`, `--neg`, `--neu`); provenance is shape (marks `WB.mark`). Never use a signal colour for provenance or a family hue in navigation.
- Panels square, 1px rule, no shadow except floating layers; 24px minimum target (compact controls get an invisible hit area).

## Router

`#/<run>/<view>[/<anchor>]`; `#/<run>/module/<id>[/<anchor>]`. Views: `front`, `module`, `model`, `fit`, `evidence`, `limitations`, `system`. Default `#/czr-full-credit-assessment/front`.

- Anchors resolve to `document.getElementById(anchor)`, then `p-<anchor>`, `t-<anchor>`, `c-<anchor>`. Panels are `id="p-<anchor>"` (`WB.panel({anchor})`), tables `id="t-<cssId(table_id)>"`, chart slots `id="c-<cssId(chart_id)>"`, evidence rows `id="ev-<module>-<Cn>"`. `WB.cssId` replaces anything outside `A-Za-z0-9_-` with `-`.
- Same run, view and module with a new anchor scrolls without re-rendering. Back and Forward work.
- Unknown run, unknown view, unknown module, a module that is not in the run's plan, a not-run step, an unbuilt view and an unavailable view each render a state page, not an error. `data-ready="1"` is set after every route, including those.
- `WB.href(view, anchor, runId)` builds a hash (`view` may be `module/CP-1B`); `WB.navigate(hash)`; `WB.rerender()` re-renders the current route; `WB.setHonest(on)` switches the real-run state (updates `?state=real` in the URL, re-renders, returns focus to the bar's switch); `WB.readStateFromUrl()` reads it at boot; `WB.parseHash`.

## View registry

```js
WB.registerView('model', {
  title: 'Model',
  icon: 'model',                       // any name in WB.iconNames
  available(run) { return true; },     // true, or a string reason shown in the rail tooltip and the state page ("Not in this Pathway")
  render(canvas, run, params) { /* params = { id, anchor }; append to canvas */ },
});
WB.registerFrontPage('credit_snapshot', (canvas, run, params) => { /* bespoke Front Page */ });
```

Inside `render`:

- `WB.setOutline([{ id: '<dom id>', label, na }])` fills "On this page" (scroll spy follows it; `na` marks a condition line).
- `WB.page.gapModules = ['CP-1B', ...]` feeds the inspector Gaps tab (module ids, `WB.citeModule`-resolved).
- `WB.setNavExtra(node)` puts a node under the module list (the Model's band list).
- `WB.run` is the current run; `WB.state.honest` is the real-run state (`?state=real`; set it with `WB.setHonest`, the switch is in the verdict bar).
- The rail destinations are fixed (Front Page, Analysis, Model, Portfolio Fit, Evidence, Limitations, Design system). An item is disabled with a tooltip until its view is registered; `fit` should return a reason string when `run.fit` is empty.
- Views registered here: `front` (generic, replaced by `registerFrontPage`), `module` (`module/<id>`, also the not-run state), `evidence`, `limitations`.

## Data helpers (`core.js`)

| helper | returns |
|---|---|
| `WB.run`, `WB.runIds`, `WB.loadRun(id)`, `WB.runMeta(run)` | current run; stems; parsed run with indexes; `{issuer, issuerId, asOf, analyst, pathway, depth, primary, frontPage, frontPageName, tags[]}` |
| `WB.handoff(id)`, `WB.step(id)` | `run.handoffs[id]`, `run.steps[id]` |
| `WB.table(tableId)` | `{id, owner, columns, rows}` across handoffs, then `run_brief.tables` (owner `RUN_BRIEF`); `null` if absent. Chart twin tables are registered here as `<chart_id>@<table_id>` |
| `WB.citeModule(owner)` | the module whose citations a table's `[Cn]` resolve against (`RUN_BRIEF` resolves to its first input, CP-0) |
| `WB.citation(moduleId, 'C12')` | `{module, id, source, locator, excerpt, anchored, synthetic, origin}` or `null` |
| `WB.citationUses(moduleId, id)` | places: analysis paragraphs, table rows, Model cells |
| `WB.parseCite(raw)` | `{cites: ['C1', ...], calc: 'formula' \| null, note, raw}`; handles `[C1][C2]`, `[C1] [C2]`, `[C1, C2]`, `calc: ...`, prose with tokens, `—` |
| `WB.rowInfo(table, r)` | `{cites, calc, note, module, citations[], synthetic, allSynthetic}` or `null` when the table has no `cite` column |
| `WB.columnKinds(table)` | per column `{name, label, kind: hidden/scale/id/numeric/prose/text, modelWritten, index}` |
| `WB.cellOrigin(table, r, c)` | `{kind: cited/calculated/synthetic/model/illustrative/gap/none/plain, info?, model?}` (rules below) |
| `WB.gapItems(moduleId)`, `WB.gapsByIds(['G8'])`, `WB.cellGap(table, r, c)` | parsed `gaps_md` items `{module, ids, missing, text}` (an identical gap stated twice is listed once); `{item, moduleItems, module, model}` for an n/a cell: `item` is the matching gap, `model` names the Model cell (`{lineId, columnId}`) when the cell is a Model cell with a reason code (the Model strip tables and the Snapshot financials resolve to it, `WB.modelCellFor`); a cell neither explains is counted in `window.__wbUnresolvedGaps` (one entry per cell) and `<html data-unresolved>`, and its passport reads "Reason not recorded by the module" with no gaps listed. `check.py` prints the count per page and does not fail on it (documented fail-open: a fixture-data issue) |
| `WB.fmtByUnit(table, r, c)` | a numeric cell by unit: yields (and percents served with decimals) and prices to 2 dp, US$m amounts as whole millions with grouping; `null` for anything else (then `WB.fmtNum`). Used by tables, call lines and chart labels; the passport keeps the served value, grouped, under "Served as" (`WB.groupServed`) |
| `WB.modelLine(id)`, `WB.modelCell(lineId, columnId)`, `WB.modelCellFor(table, r, c)` | Model line, cell, and the Model cell behind a `snapshot.financials` figure |
| `WB.moduleName(id)`, `WB.moduleQuestion(id)`, `WB.stepStatus(id)`, `WB.stepReason(id)` | plain name and question (from `#rbot-modules`, fallbacks for CP-DR, CP-8, CP-L10, CP-2E, MODEL, PROJECTION, FIT); `pass`/`limitations`/`blocked`/`notrun`; the reason (CP-5 limitation, step reason, first gap) |
| `WB.chartTitle(chart_id)`, `WB.chartsForBlock(n)`, `WB.chartsForModule(id)` | chart title; charts of Front Page block `n`; charts of a module (`analysis:CP-x`, or `analysis` whose first owned table belongs to it) |
| `WB.colLabel(name)`, `WB.fmtNum(s)`, `WB.unitLabel(cur, unit)`, `WB.tableUnit(table)`, `WB.fmtDate(iso)` | sentence-case label with acronyms (`ebitda` becomes EBITDA); grouped thousands and negatives in parentheses (`-3.7%` shows `(3.7)%`; the passport keeps "Served as"); `USD`+`MILLIONS` becomes `US$ m` |
| `WB.signal(value, col)` | `{tone: pos/cau/neg/neu, icon, word, pos?, label?, scalePos?, ordinal?}` for scale values (house scales, High/Medium/Low per column direction, status words) |
| `WB.el(tag, attrs, children)`, `WB.svg`, `WB.frag`, `WB.text`, `WB.qs`, `WB.qsa`, `WB.cssId` | DOM helpers |
| `WB.icon(name, {size, stroke, label, cls})`, `WB.iconNames` | one set: 16px, 1.5px stroke, inline SVG, `aria-hidden` unless `label` |
| `WB.mark(kind, {size})` | 10px provenance glyph: `cited` (document), `calculated` (filled square with equals), `synthetic` (flask), `model` (pen), `gap` (empty set), `illustrative` (dashed square) |
| `WB.recordError(kind, err, where)` | appends to `__wbErrors`, updates `data-errors` |

## Provenance per cell (`WB.cellOrigin`)

A figure has one origin, drawn by shape. Rules, in order (`kind` of the column from `WB.columnKinds`):

1. `—`, empty, `n/a` in a non-scale column: **gap** (`WB.gapChip`, matched to a `gaps_md` item by words in the row and column label; if none matches, the passport lists the module's gaps and says so).
2. Scale/status column (`WB.SCALE_COLS`, and at least half the values are known scale words): **calculated** when a rule produces it (Fit verdicts and caps, covenant status, QA status) and in host tables (MODEL, PROJECTION, FIT); otherwise **illustrative**. `cr_score` is illustrative.
3. Id, hidden (`cite`, uniform `currency`/`unit`): no mark. A date-named id column (`level_date`) and **text** take the row's origin (C2): a row that cites a source gives a short text value that source's mark and passport (cited, or synthetic when a cited source is); plain when the row cites nothing, and always plain for the table's row-label column (the first visible non-`_id` column of a multi-row table) and for `unit_label`/`unit`/`currency`. An agency rating or outlook column (`rating`, `ratings`, `outlook` in its name) with no cited source is **none** ("no source stated"). `renderCell` draws such a value as a `.fig.fig-txt` button; text that holds its own chips stays text.
3b. **none** (a numeric figure whose row names no source, or a rating with none) has its own mark: a ring holding a question mark (`WB.mark('none')`), and a passport that says "No source stated by the module" and the row it sits in (`WB.rowContextText`).
4. Prose or text column whose name reads as the model's own words (`analyst_*`, `rationale`, `implication`, `thesis`, `reason`, `primary_downside`, `text`, ...): **model-written**. Other prose takes the row origin.
5. Numeric cell: a `snapshot.financials` figure takes its Model cell's basis (REPORTED cited, otherwise calculated); a row whose `cite` holds only `calc:` is **calculated**; a row with `[Cn]` and `calc:` marks a number that is an operand of the formula as **cited** and every other number as **calculated**; a derived column of a host table (multiples, percentages, headroom) is **calculated**; a row citing a synthetic citation is **synthetic**; `[Cn]` real is **cited**; a table with no `cite` column owned by MODEL, PROJECTION or FIT is **calculated** (host); any other is a register row with no source stated.

The passport for a calculated figure lists each input as a labelled chip (sibling cells found in the formula, plus the cited sources), each opening its own passport (refinement 1).

## Components (`render.js`)

- `WB.panel({title, code, fig, tags:[{kind,label}], state:{word,tone,icon}, note, link:{href,label}, tools:[node], anchor, body, collapsed, pinned, collapsible, className})` returns `section.panel` with `_setOpen(bool)`. `WB.collapseAll(root, open)`, `WB.collapseTool(() => root)`.
- `WB.renderTable(table, {maxRows=40, hide:[], anchor, caption})` dense table, one tab stop with arrow keys (`WB.initGrid`); `WB.renderKV(table)` one-row table as key/value; `WB.tablePanel(tableId|table, opts)`; `WB.tableTags(table)`; `WB.tableTitle(id)`; `WB.renderCell(table, r, c)` returns `{node, cls}`.
- `WB.fig(desc, content, {kind, cls, rg, label, noMark})` a figure button bound to a passport descriptor; `WB.gapChip(ids, {label, reason, items, desc})` (its accessible name always carries a reason: the module's gap text, else "Reason not recorded by the module"); `WB.citeChip(module, id)`; `WB.inline(text, module)` turns `[Cn]`, `G8`, `**bold**`, `` `code` ``, `(calc: ...)` into marks and chips; `WB.md(text, {module})` markdown to a fragment (paragraphs, lists, headings, tables); `WB.paragraphs(text)`.
- `WB.badge(value, col)`, `WB.statusChip(status)`, `WB.tag(kind, label)`, `WB.signalBars(level)`, `WB.meter(pos, total)`, `WB.conditionLine(text, {module})`.
- `WB.tile(t)` and `WB.verdictBar(cfg)`. A tile is `{label, key, scale: rec|val|score|dir|outlook|gate|cov|press|five|plain, value, ref, illustrative, sub, word}`; a tile with `value: null` renders the honest **Not produced** state: a button whose passport holds the full `reason`, a `short` reason on the tile and the `producer` module as a link. `{rowBreak: true}` in `tiles` starts a new tile row. A tile may carry `cap: {tone, icon, value, aria, desc}` (C2): a "Capped by Fit" badge button on the tile (pages.js `fitCap`, counted from `cp6.portfolio_recommendation`). `cfg = {title, question, illustrative, bylineNodes | byline, tiles, lines:[{label, tone, children}], honest, tools, maxLines = 3, order: [labels]}`; the head is two rows (title and question; then Illustrative, analyst, date, honest notice, tools); the title row opens with the issuer (`WB.issuerNode`: name, ticker, the Fictional tag), at every width; `notices: [{word, tone, icon, code, desc}]` are tags in the byline row (`WB.noticeTag`: the word, its icon and the module code; the passport holds the full sentence): a Blocked module, a Quick run's Screening basis, what a Covenant Pathway does not run. They are not call lines. The call lines scroll away while the head and tiles stay pinned. At most `maxLines` lines show, in `order` (the content doc's order, `WB.CALL_ORDER[front_page]`, `WB.CALL_MAX`); the rest sit behind one `details.v-more` that names them. The main risk has a reserved slot (`WB.CALL_RESERVED`) and so does every **negative** line (its `.v-ll` has `tone-neg`: Breaches, Breached, a gate Met, a runway short of its uses): they never fold, the cap yields and the bar grows (C2). `cfg.meta` (instead of `bylineNodes`) builds the byline inside the bar, so the sentences about the test run that lines hand over (`line.caveats`, from `WB.splitFixtureCaveats(text)`) reach the Design-fixture tag's passport (`WB.fixtureTag(caveats)`, a button). The head's tag is ILLUSTRATIVE, or REAL-RUN STATE when `cfg.honest` is set, with the real-run switch beside it (`WB.stateSwitch`, `aria-pressed`; `cfg.stateSwitch: false` omits it for a specimen). **Lines read as a call** (`WB.flattenCallLine`, run by `capCallLines` on every line once): the line's chips, figures and `calc:` marks leave the prose, and the line becomes label, a bold lead (`strong.v-lead`: to the first comma not inside a number, semicolon or colon, else the first sentence; `line.leadTo` is a regex source for another split; a line that already holds a `.v-lead` keeps it), the rest, and one `button.v-src` ("Sources n · k gaps", aria-label "Sources, n") whose passport lists every citation and gap of the line as chips (`passport.gapChips`), each opening its own passport. The Fit line is `span.v-fit` segments (one per portfolio, `white-space: nowrap`). Call-line prose is capped at 80ch. A page that adds or removes lines after the bar is built calls `WB.capCallLines(linesEl)` again (idempotent). `WB.bylineNodes(meta, lead, caveats)` builds the byline: analyst (`meta.analystName`), a quiet "Design fixture" tag when `meta.designFixture`, the date. `WB.callConfig(run)` derives tiles and lines for each Pathway from the run's tables (and the honest state from `WB.state.honest`); `WB.callBar(run, tools)` returns the finished bar for a Front Page to put at the top. Replace or extend `WB.callConfig` output rather than copying it.
- `WB.genericFrontPage(canvas, run)` every `front_page_blocks` entry as a panel (half width for small tables, full width otherwise) or a condition line when `shown: false`.
- `WB.moduleView(canvas, run, id)` the module view.
- Charts: `WB.chartSlot(chart, {caption, summary})` returns `figure.chart-slot#c-<id>` with caption and a `.cs-host`; `caption: false` keeps the caption for assistive technology only (the panel or a sub-heading names the chart); `summary` is a one-sentence data summary written by the page, and the fixture's own summary is never shown. If `WB.chart` is a function it is called as `WB.chart(host, chartRecord, opts)`; until then the slot shows the table twin. Declared n/a charts (`chart.data = {unavailable: 'reason'}`, `WB.chartUnavailable(chart)`) render the n/a frame and never call `WB.chart`. `WB.chartTwinTables(chart)` returns the twin tables (ids `<chart_id>@<table_id>`, each row carrying its `cite`), so a mark's passport is `{t: 'cell', table: twin.id, r, c}`.

## Passports and the inspector (`shell.js`)

Every figure carries `data-ref`, a key into `WB.ref(desc)`. Clicking, or Enter or Space on a non-native control, opens `WB.inspect(WB.getRef(key), el)`. Descriptors (`WB.buildPassport` resolves them lazily):

| `t` | fields | passport |
|---|---|---|
| `cell` | `table, r, c` | by `WB.cellOrigin`: cited (file, locator, verbatim excerpt, Used in n places), calculated (formula, labelled input chips), synthetic (TEST DATA rationale), gap (missing item, reason), model-written, illustrative |
| `row` | `table, r` | the row's cites and formula |
| `cite` | `module, id` | the citation |
| `mcell` | `lineId, columnId` | Model cell: value or reason code, basis, sources (use for every Model grid cell) |
| `gap` | `ids` or `items` | gap items |
| `chart` | `chartId` | chart summary and origin; the Table tab shows its twins |
| `note` | `kind, code, title, sub, fields:[[label, value, mono]], note, excerpt, cites, table` | free-form passport |

`WB.inspect(desc, originEl, {tab: 'source'|'table'|'gaps', noFocus})`. A `cell` descriptor may carry `label`, the name the page shows the figure under (`WB.labelCell(node, 'Fitch')`): the passport is titled with it, never with a column id; a "—" row label is dropped. The foot prints the raw id in whole tokens (`.pp-tok`, wrapping only at their own separators); a cited passport names its origin in words (`WB.originInWords`) and puts the raw locator in the foot. Focus moves to the passport heading; Escape returns it to the figure (below 1360px it also closes the inspector back to its strip); the figure shows `.is-selected`. A chip opened inside the inspector pushes a Back stack. Tab order is rail, navigator, canvas, inspector. Chart marks: give each mark `data-ref`, `tabindex`, `role="button"` (or use `<button>`/`<a>`), and an accessible name; arrows between marks are the chart's own handler.

## Honest state (refinement 5)

`WB.state.honest` is switched in the verdict bar's header (`.v-state`, beside the tag) and lives in the URL (`?state=real`: it survives a reload and can be shared; `WB.setHonest`). It replaces every judgement tile the real run did not produce with **Not produced** plus reason and module: Recommendation, Valuation, Credit Score, Credit Direction, Sector Outlook, Since last Report (the reason is the run's own gap text, `gapHonest` in `pages.js`; fixed copy only when the run carries none), and any tile still flagged illustrative (a judgement no RBOT run has produced yet). The distress gate reads Not met and a "Relative value: Unclear" call line is added, per `caos-runs/README.md`. The bar's tag reads REAL-RUN STATE. Below the bar (`WB.markFixtureView`, called by the router for a Front Page) a panel that holds `.fig-illustrative` figures gets `.is-fixture` and a "Fixture's own view" tag, and its illustrative verdict words lose their signal colour (`components.css`). Any view reading illustrative verdicts should call `WB.callConfig` or test `WB.state.honest`.

## Additions in the polish pass (W6)

| helper | does |
|---|---|
| `WB.fmtNum(s, {group: true})` | groups a four-digit amount (2,018) that would otherwise read as a year; `renderCell` passes it for numeric columns |
| `WB.limitState(status, limit, current)` | one rule for a portfolio limit in every view: Breached as served; Within with headroom under 10% of the limit is Tight |
| `WB.claimName(classId)` | a claim class in words from `cp4c.claims_register` (C2-1L reads "First-lien claims") |
| `WB.rowLabel(table, r)`, `WB.tableWhere(table)` | a row and a table in words for passports ("Protection score by area chart, from Protection score · Covenants and legal (CP-4)") |
| `WB.citeGroup(module, ids)` | a run of more than three citations as one chip ("C2–C10" or "9 sources") whose passport lists each source; `WB.inline` uses it, renders `(G8)` as the chip alone and `(calc: …)` as a compact calculated chip |
| `WB.roving(box)`, `WB.initRovingIn(root)`, `WB.ROVING_BLOCKS` | one tab stop per block of figures outside tables (tiles, call lines, key findings, lists, prose with chips); arrows, Home and End inside; the router applies it after every render |
| `WB.renderPassport(p)` | the inspector's passport renderer, static (the Design system uses it). A passport has `code` (a short code heads it: C12, G8) and `id` (a raw table, Model line or chart id, printed small at its foot) |
| `WB.tablePanel(t, {code: null, state: false, note})` | hides the owner code and the Blocked state (a module view does not repeat its own), overrides the head note |
| `WB.JUDGEMENT_NUMERIC` | numeric columns that hold a judgement (the lender protection score): `WB.cellOrigin` reads them as illustrative |
| `WB.periodLabel(v)`, `WB.enumWord(v)` | `Q2_2026` reads "Q2 2026"; `BASE` reads "Base" |

Id columns whose values are names (bond names, KPI labels) render as text (`columnKinds` marks them `textual`); `facility_id` and `portfolio_id` are not shown where the table also names the facility or portfolio (the passport keeps the id); dense-table heads wrap so no column is wider than its widest value needs.

## Keyboard, 1280x800 and print (refinement 6)

- Below 1360px the navigator starts closed (rail toggle opens it) and the inspector's grid column is always a 36px strip (`.insp-open`, a labelled button; `#app[data-insp]`). Selecting a figure opens the pane (`.insp-pane`) as an **overlay** on the canvas (`position: fixed`, `--shadow-float`, a close control) without changing the `#app` grid or any canvas layout (C2). It sits on the right edge; when the selected figure would be under it, `placeInspector` docks it on the canvas's left edge (`#app[data-insp-side="left"]`, `--insp-left`), so the figure stays visible and nothing scrolls. Escape or the close button returns to the strip and focus to the figure. From 1360px the pane is the docked 300px column. At 1280 the canvas stays 1188px with the strip or the overlay.
- The issuer (name, ticker, Fictional tag) is on screen at every width: in the verdict bar's title row on Front Pages, in the canvas header of every other view.
- The navigator shows a module's status icon only where it departs from the run's most common status; the status word stays in each row's accessible name and tooltip. Illustrative is stated once on a Front Page (the verdict bar): its panels drop the Illustrative tag and keep Synthetic and Model-written. Type floor: 11px (`--fs-micro`, `.tag`).
- The rail shows the wave icon only, cropped at build time (`build.py` `logo_icon`, stdlib) from the supplied horizontal logo.
- `/` opens the switcher (modules, figures, sources, citation excerpts; Enter navigates), `?` opens "How to read a figure", Escape closes a layer or returns focus to the figure.
- Tab order: rail, navigator, canvas, inspector. In the canvas one tab stop per table, chart (its marks, never the SVG root) and block of figures (`WB.roving`); arrows move inside.
- Print (`beforeprint` / `afterprint`, `WB.beforePrint()` and `WB.afterPrint()`): rail, navigator, inspector, "Full analysis" links hidden; panels, tables and disclosures (extra call lines, Sources) expanded; every figure that has a source gets numbered endnotes (`[n]`, `[n–m]` for a run) after it in the flow; the passports print as the endnote list. Front Page and modules start new pages.

## Tests

`tests/harness.html` + `tests/scenarios.js` (run by `check.py --interact`) drive the built file in a same-origin iframe: passports of each origin, focus return, router edge cases, roving grid, search, help, the real-run switch (in the bar, `?state=real`), navigator filters, 1280 and 1440 layout and the overlay inspector, call lines (leads, Sources passports, breaches never folded, Fit segments, tile caps), text provenance, scroll spy, print endnotes. `open(hash, size, search)` takes a query string (`'?state=real'`). Add scenarios there for new views.
