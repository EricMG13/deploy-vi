# RBOT Report mockups: shared foundation

Shared layer for the three Report mockups (A IC paper, B verdict rail, C period spine). Names, classes and APIs here are binding: use them and do not fork them. Open `gallery.html` to see each one drawn with real data.

| File | What it is |
|---|---|
| `tokens.css` | House tokens (CSS custom properties) and the component layer |
| `charts.js` | `RBOTCharts`, a vanilla SVG chart kit, and `RBOTUI`, which handles popovers, chips, scale badges, status chips, cells and tabs |
| `data.js` | `window.RBOT_DATA`, generated. Do not edit it by hand |
| `build-data.py` | Builds `data.js` from `czr.json` and the Test CLO I CSVs (standard library only): `python3 build-data.py [czr.json] [portfolio-dir]` |
| `gallery.html` | Every component and chart kind. `gallery.html#demo` opens two table twins and a citation popover |

## Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400..700;1,14..32,400..700&family=Inter+Tight:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="shared/tokens.css">
...
<script src="shared/data.js"></script>
<script src="shared/charts.js"></script>
<script> /* build the page */ RBOTUI.init(document); </script>
```

The mockups load Inter and Inter Tight from Google Fonts. **The Plan 07 renderer must embed both fonts** (base64 `@font-face` or files beside the Report): the Report needs no network when it is viewed (PRODUCT.md), and the mockup's `<link>` to Google Fonts would break that offline requirement if it were carried over. `charts.js` never writes `innerHTML`, so it works under a strict CSP.

**Logo paths.** Mockups in `design/mockups/` reference `../../brand/ssim-logo-horizontal-white.png` on navy or electric-blue grounds, and `../../brand/ssim-logo-stacked-black-trim.png` on white or `#F0F2F5`. From `shared/` the path is `../../../brand/`. Never recolour or redraw the logo. Classes: `.logo.logo--on-dark` (22px high) and `.logo.logo--on-light` (40px).

## Tokens (`tokens.css`)

**Colour.**
- Brand: `--navy #000533`, `--blue #0017E5` (`--blue-deep` for hover), `--ground #F0F2F5`, `--sheet #FFF`.
- Grey ramp: `--grey-100 #E1E3E6`, `--grey-200 #C5C8CC`, `--grey-400 #8D939D` (marks only, never text), `--grey-600 #55585E`.
- Blues and accents: `--soft-blue #CBE4FE`, `--soft-blue-50 #E7F5FF`, `--mint #1EFF8F` and `--mint-soft #A5FFD2` (state on navy only, used sparingly), `--lemon #F7FF99`.
- Signal: `--positive #0F8048`, `--positive-text #0C6639`, `--negative #D4625D` (marks), `--negative-text #A6100F`.
- Text: `--ink` (navy), `--ink-2` (grey-600). On navy use `--on-navy` and `--on-navy-2 #CBE4FE`.

**Chart palette.** Five hues, a neutral and a critical red, each at least 3:1 on white:

| Token | Hex | Use |
|---|---|---|
| `--chart-1` | `#0017E5` | Electric blue: the issuer and the primary series |
| `--chart-2` | `#C4410C` | Burnt orange |
| `--chart-3` | `#000533` | Navy: totals |
| `--chart-4` | `#55585E` | Slate |
| `--chart-5` | `#2B8FD6` | Mid blue |
| `--chart-neutral` | `#8D939D` | A sixth series, rules, peers. Hues are never recycled |
| `--chart-critical` | `#A6100F` | Unexplained residuals and breaches only |

Blue against orange is the pair that stays distinct under deutan, protan and tritan vision. Navy and slate differ by lightness. Lines also differ by point shape (circle, square, diamond, triangle, cross) and dash, so hue never carries meaning alone. Risk-zone fills are `--risk-low`, `--risk-med` and `--risk-high`.

**Type.** `--font-body` is Inter and `--font-head` is Inter Tight. `--nums` sets tabular, lining numerals, which apply to every table, `.num` element and chart label. The scale steps by 1.2 from a 14px body:

| Token | Size | Use |
|---|---|---|
| `--fs-xs` | 12px | Captions, chips, axis labels |
| `--fs-table` | 13px | Tables |
| `--fs-base` | 14px | Body |
| `--fs-md` | 16.8px | Sub-heads |
| `--fs-lg` | 20.2px | Section heads |
| `--fs-xl` | 24.2px | Page title |
| `--fs-2xl` | 29px | Report title |

Space follows a 4px rhythm, `--s-1` to `--s-8`. Shape is square: `--radius` is 2px and applies to chips only. `--frame` is the template's 1px navy block border, and `--hit` is the 24px minimum target.

Focus rings, text selection, scrollbars and link underline offset are all themed. There are no gradients and no shadows, except the popover's soft shadow.

## Components (classes)

| Class | What it is |
|---|---|
| `.bar` | The house section bar: navy band, white Inter Tight bold capitals. `.bar__meta` is a quiet right-hand note. `.bar--sub` is the template's grey sub-bar ("Strengths"). Use it on `h2` or `div` |
| `.block` + `.bar` + `.block__body` | A framed template block |
| `table.dt` | Dense bordered table. `.num` right-aligns and sets tabular figures. `thead th .unit` puts the unit under the head. Row classes: `tr.total`, `tr.sub` (italic % rows), `tr.indent`. Table variants: `.dt--framed`, `.dt--kv` (label/value). Wrap wide tables in `.table-scroll`. Negatives print in parentheses, as the filings do: data already holds `"(62)"` |
| `details.xp > summary` + `.xp__body` | Expandable section. The summary is a navy bar with a rotating chevron and the words "Show detail" or "Hide detail". `.xp--light` is for nesting. `.xp__lede` holds the always-visible line above the body |
| `[data-tabs] > .tabs__list > button.tabs__tab[aria-controls]` + `.tabs__panel` | Tabs. `RBOTUI.tabs()` (run by `init`) wires roles, arrow keys, Home and End |
| `.btn`, `.btn--quiet` | Buttons. `aria-pressed` and `aria-expanded` show as filled. Disabled buttons are dashed |
| `.status--pass/--restricted/--blocked/--watch/--breach/--na` | Status chips. Each carries an icon and a word. Portfolio Fit maps Fits to `pass`, Watch to `watch` and Breaches to `breach`. Use `RBOTUI.status(word)` |
| `.scale` | A house scale badge: position box, word and a five-step meter. Use `RBOTUI.scale(...)`. `.scale--lg` is the large size |
| `.dir--up/--flat/--down` | Credit Direction (Improving, Stable, Deteriorating) and Sector Outlook (Positive, Neutral, Negative). Each pairs an arrow with its word |
| `.on-navy` | Wrap chips, badges and `.illus` with this when they sit on a navy ground |
| `.chart-strip` | Three-column grid for the Model chart strip. It collapses to one column below 1100px |

## Provenance vocabulary

Cited, calculated and model-authored content never look alike, and each origin is marked by a shape or pattern as well as colour.

| Origin | Prose and chips | Dense table cell (`RBOTUI.cell`) | Chart mark |
|---|---|---|---|
| Cited `C<n>` | `button.cite[data-ref]`, shows `[C12]`, blue | Blue corner triangle; the figure is the button | Solid |
| Calculated `K<n>` | `button.calc[data-ref]`, shows `= K3`, navy | Navy corner square | Solid |
| Synthetic `S<n>` (Test CLO I) | `.synth` tag; `S` refs open as "Synthetic portfolio file" | Grey corner triangle | Solid |
| Model-authored | `.prov-model` (dotted underline) + `.tag-model` | Dotted underline | Hatched fill, hollow point, dashed line |
| Illustrative | `.illus` tag "ILLUSTRATIVE"; `.illus-band` above a block; `.is-illus` dashed outline | Dashed outline | Hatched, hollow or dashed, like model-authored |
| Gap `G<n>` | `.gap` shows "n/a" plus `.gap__reason`; `button.gapref` shows "n/a G8" | n/a; the reason opens in the popover | Labelled "n/a" mark with its reason; a line breaks there |
| Projected | — | — | Dashed line, with a "Projected" divider |

Clicking any `button[data-ref]`, or pressing Enter on a chart mark, opens one popover. For `C` it shows file, line locator and the verbatim excerpt. For `K` it shows the formula with clickable input chips. For `G` it shows the field and reason, and for `S` the synthetic file and row. Escape closes the popover and returns focus.

**ILLUSTRATIVE rule.** No RBOT run exists. Every score, recommendation, valuation, direction, outlook, sponsor view, thesis line, strength, weakness, catalyst and risk shows `.illus` (or sits under an `.illus-band`). Its wording uses only cited figures.

## RBOTUI (in `charts.js`)

| Function | What it does |
|---|---|
| `RBOTUI.init(root)` | Wires the delegated popover and tabs. Call it once, after the DOM is built |
| `RBOTUI.value(datum, unit?, context?)` | Returns a fragment: the value plus its chip, or the n/a gap with its reason. Context `"prose"` or `"figure"` makes the figure itself the button, with a corner mark and no bracket chip |
| `RBOTUI.cell(td, datum, unit?, kind?)` | Fills a dense-table cell in the compact form (the figure is the button). `kind` hints the display format (`"rate"`, `"price"`) |
| `RBOTUI.setFormat(fn)` | Installs the display formatter `fn(datum, unit, context, kind)`, which returns the text to show or `null`. The popover still prints the string as served ("Served as"). Without a formatter, values print as served |
| `RBOTUI.roving(root)` | One tab stop per block of provenance buttons (a table, list or paragraph); arrow keys, Home and End move within it. Chart marks are one tab stop per chart |
| `RBOTUI.statusLabel(word)` | The reader-facing status word: `Restricted` reads "With limitations" (the data keeps `Restricted`); Pass and Blocked are unchanged |
| `RBOTUI.chip(ref)` | Returns a `cite`, `calc` or `gapref` button |
| `RBOTUI.scale({kind, pos, word?, label?, illustrative?, size?})` | Scale badge. `kind` is `"rec"` (1 Strong OW … 5 Strong UW, `pos: null` with `word: "Avoid"` or `"N/A"`), `"score"` (1 Strong, 2 Good, 3 Fair, 4 Weak, 5 Stressed) or `"val"` (V1 Very attractive … V5 Very unattractive). The position is printed and drawn, and the `aria-label` states the scale. Tone is a secondary cue only |
| `RBOTUI.status(word)` | Pass, Restricted, Blocked, Fits, Watch, Breaches or N/A |
| `RBOTUI.illus(text?)` | The ILLUSTRATIVE tag |
| `RBOTUI.open(ref, anchorEl)`, `RBOTUI.close()` | Open or close the popover |
| `RBOTUI.el(tag, attrs, kids)` | Small DOM helper (`text:` sets textContent) |

## RBOTCharts (in `charts.js`)

`RBOTCharts.<kind>(element, spec)` clears `element`, draws a `<figure class="chart">` and returns `{ element, redraw(), update(spec), destroy() }`. Charts redraw on resize and once fonts load.

**Datum.** `{ v: "3.29" | null, prov: "cited"|"calculated"|"model"|"illustrative"|"synthetic"|"gap", ref?: "C12"|"K3"|"G8"|"S4", reason?: string, projected?: true }`.
- `v` is printed exactly as given, as a string. Floats only place marks.
- `v: null`, or a non-numeric `v` with a `reason` such as the source's "—", is an n/a gap and is never drawn as 0.

**Common spec fields.**

| Field | Meaning |
|---|---|
| `title` | Chart title |
| `summary` | One plain sentence |
| `unit` | `"x"`, `"%"` or `"pp"` print attached; `"US$ m"` and `"% NAV"` print spaced |
| `source` | Caption line, printed after "Source:" |
| `number` | Optional, e.g. `"Figure 3"` |
| `headingLevel` | Heading level, 2–6; default 4 |
| `id` | Element id |
| `height` | Plot height in px |
| `ticks` | Approximate tick count |
| `categoryLabel` | First column of the table twin |

Every chart has:
- one value axis that holds zero (bridges and ranges float);
- no gradients, no shadows and square bar ends;
- each mark as a focusable `role="img"` element, at least 24px, whose `aria-label` names series, category, value, unit and provenance, with a tooltip on hover or focus;
- a legend, with provenance entries added automatically;
- a "Show table" toggle for the exact-values table twin.

| Kind | Spec fields beyond the common ones |
|---|---|
| `lineStrip` | `categories[]`, `series[{key, label, values[Datum], color?, shape?}]`, `labels: "last"\|"none"`. A projected datum dashes the segment into it and draws the "Projected" divider. A gap breaks the line and shows a labelled n/a |
| `columns` | `categories[]`, `series[]` as above (grouped bars), `labels: false` to hide value labels |
| `waterfall` | `steps[{label, short?, kind: "total"\|"delta"\|"residual", d: Datum}]`. A residual is drawn in `--chart-critical` and named "unexplained". `short` labels the axis; `label` names the mark and the twin row |
| `bullet` | `rows[{key, label, direction: "max"\|"min"\|null, threshold, current, headroom?}]`. The direction prints as ceiling or floor. Headroom is printed as served and never computed |
| `stackedColumns` | `categories[]`, `series[{label, color?, values[Datum\|null]}]`, `totals: false` to hide the exact decimal-sum labels |
| `rangeStrip` | `rows[{key, label, sub?, min?, q1?, median?, q3?, max?, marker?}]`, `markerLabel`. Any statistic left out is not drawn; a `null` statistic is a gap. The interquartile bar is drawn only when Q1 and Q3 are both present |
| `scatter` | `points[{key, label, short?, group, x: "YYYY-MM-DD", y: Datum}]`, `xLabel`, `yLabel`, `groupLabel`, `asOf`, `groupColors{group: 1..5}`, `curve?{group\|null, label, prov}`. The curve is a least-squares fit of y on ln(years from `asOf`). It only positions marks and never prints a value. Labels avoid collisions |
| `dumbbell` | `rows[{key, label, from, to, change?}]`, `fromLabel`, `toLabel`. From is a hollow neutral point; to is a filled blue point |
| `riskMatrix` | `events[{key, label, description, probability, impact, classification, prov, ref?}]`. The grid is High, Medium, Low (plus Unknown) by Low, Medium, High. Zones are named in labels and the twin |

## Data (`window.RBOT_DATA`)

| Key | Contents |
|---|---|
| `meta` | Issuer Caesars Entertainment, Inc. (CZR); Pathway Full Credit Assessment; Depth Full; `primary: true` (2026 Fertitta merger financing); analysis date 2026-10-02; reporting period Q2 2026; strategies |
| `citations` | `C1…C283`: `{id, key, label, period, value, unit, file, line, locator, excerpt}`. `S1…` are the synthetic Test CLO I rows, flagged `synthetic: true` (no reviewer names are kept) |
| `calcs` | `K1…K100`: `{id, key, label, period, value, unit, formula, formula_keys, inputs[C/K ids], note}` |
| `gaps` | `G1…G28`: `{id, field, reason, origin}`. G1–G14 come from `czr.json`; the rest are added by `build-data.py` for figures the extraction does not carry |
| `figures` | Every figure by `czr.json` key (plus `issuer.*`). Each is a Datum with `label`, `period`, `unit` and `raw` (the source string) |
| `tables` | `financials` (FY2023, FY2024, FY2025, H1 2025, H1 2026, LTM), `balanceSheet`, `creditMetrics`, `capitalStructure` (rows per facility with cumulative Structuring and SSIM multiples, % of EV, subtotals), `ebitdaAdjustments` (Reported to Structuring to SSIM), `liquidity`, `maturities`, `segments`, `trace`. Rows hold Datums |
| `charts` | Ready specs: `leverage`, `coverage`, `liquidity` (the strip), `interestPath`, `revenueEbitda`, `segments`, `maturityWall`, `ebitdaBridge`, `cashBridge`, `yieldCurve`, `peerRange`, `covenant`, `cloLimits`, `cloSectors`, `risk` |
| `modules` | CP-0, CP-1, CP-1B (Earnings Delta), CP-2 … CP-6, each `{id, name, status, reason, refs}`. Statuses are Pass or Restricted; none is Blocked, because every module can answer its reader question from the CZR pack. The Primary flag only shows the Transaction Summary block |
| `limitations` | Every gap, as it is stated at Approval, each `{ref, field, text, origin, scope}`. `scope` is "Model limitation: PF-LTM column" for the unstated merger debt (no pro forma LTM) and "Source Pack gap" for the rest |
| `illustrative` | Credit Score, Valuation, Recommendation per Strategy and per instrument, credit direction, sector outlook, sponsor quality, thesis, catalysts, strengths, weaknesses, historical performance, business description, transaction summary and key findings. Every item is flagged `illustrative: true` and carries the refs its wording rests on |
| `portfolio` | Test CLO I, flagged `synthetic: true`: `summary`, `sectors`, `constraints`, `mandate`, `sources` and `fit` (Portfolio Fit: overall, checks and per instrument) |
| `counts` | Number of cited, calculated, gap and synthetic records |

**Conventions.**
- Money is in US$ m unless the unit says otherwise.
- Multiples are given to 2 dp, and percentages to 1 dp as computed.
- Display follows the unit (Mockup A's formatter): yields and coupons 2 to 3 dp with zeros trimmed (`8.064`, `6.50`, `4.125`); prices 2 dp; multiples 2 dp with `x`; percentages as computed; money as `US$11,486m` or `US$17.6bn`. Dates read `15 Feb 2032` in tables and `30 June 2026` in prose.
- The data and the passport keep the string exactly as served (e.g. `8.063520`, shown as "Served as").
- Leverage uses company Adjusted EBITDA and total debt at face value. The GLPI and VICI financing obligations (13,157) are shown separately, not added to debt.
- EV is the merger's stated transaction value of approximately $17.6 billion, because no listed equity value is in the sources.
