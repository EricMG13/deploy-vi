# Front Pages: design and build spec

Status: **superseded 2026-10-17** — the owner moved the redesign of every Front Page (and Report A) to Claude Design; this spec's content model and `build-fp-data.py` feed `design/claude-design-handoff/`. Original status: design exploration, 2026-10-17. Five hi-fi mockups of the Front Pages that v1 does not ship: `earnings_update`, `relative_value`, `covenant_refinancing`, `distressed_restructuring`, `portfolio_decision` (interfaces spec `docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md` §4.2–§4.6, Pathways §5, charts §11.4, Portfolio Fit §7; read them from `main`, e.g. `git show main:docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md`). Plans 14–18 build these Pathways later; nothing here is build work.

Owner decisions for this exploration (2026-10-17): every page is Full depth with working module views; the Distressed gate is **Unclear** (ILLUSTRATIVE), so its EV, recovery and fulcrum block is drawn under the spec's own rule; covenant terms come from a small verified extraction of the corpus credit agreement and 2032 indenture (`fp-extract.json`).

## 0. Binding rules

1. **The world is frozen.** `../report-a.css`, `../report-a.js`, `../shared/*` and the repo-root `DESIGN.md` are Report A and are never edited. The pages link `../shared/tokens.css` and `../report-a.css`, then add their own CSS. Read `DESIGN.md` before any UI work: navy section bars, the neutral call band, the 2px radius, flat paper, 13/14px density, tabular numerals on numbers only.
2. **Provenance grammar, unchanged.** Cited = 6px electric-blue corner triangle; calculated = 5px navy corner square; synthetic = slate triangle; ILLUSTRATIVE = dashed tag and dashed outline; Model = dashed slate tag and dotted rule; n/a = italic slate "n/a" with its gap chip and reason. The figure itself is the button. On navy grounds the shapes stay and the colours change: cited triangle soft blue `#CBE4FE`, calculated square white.
3. **No invented figure.** Every number is a Datum from `RBOT_DATA` (`../shared/data.js`, built by `build-data.py` from the CZR corpus) or `RBOT_FP` (`fp-data.js`, built by `build-fp-data.py` from `data.js` plus `fp-extract.json`). A figure the sources cannot support is `{v: null, prov: "gap", ref: "G<n>"}` and renders as n/a with its reason, never 0. Arithmetic happens in Python with `Decimal`, never in the browser.
4. **Every judgement is ILLUSTRATIVE.** Scores, recommendations, valuations, directions, outlooks, gate statuses, severities, preferences, ordinal pressures, protection scores, paths, the multiples chosen for scenarios, and every analyst sentence carry the ILLUSTRATIVE tag (block tag or `.is-illus` outline). Model-written prose carries the Model tag once per block. The Test CLO I portfolio is SYNTHETIC.
5. **Colour carries status only.** Scales are neutral (white box on navy, navy box on white; the word carries the meaning). Colour is allowed for qa status (Pass, With limitations, Blocked), Portfolio Fit (Fits, Watch, Breaches) and, new here, covenant test status, which reuses the Fit chips: Headroom = Fits style, Tight = Watch style, Breached = Breaches style, Not computable = the n/a chip.
6. **Honest conditions.** A conditional block that is not shown is replaced by one condition line naming the condition (interfaces §11.2). "What changed since the last Report" is a condition line on every page: no Prior Case was accepted. Deep Research (CP-DR) and What changed (CP-8) are not run; each is one line under Limitations.
7. **Craft floor.** No KPI tiles, no cards of icon plus heading, no eyebrow labels, no gradients, no shadows except popovers, no coloured left borders above 1px, no emoji or Unicode glyph icons (draw SVG or reuse the house CSS masks), no `innerHTML` (build with `RBOTUI.el`). Every chart has a table twin, a summary, a source line and provenance in its marks. Every interactive target is at least 24px. Phone width is out of scope, as for Report A.
8. **No network beyond fonts.** Inter and Inter Tight from Google Fonts, as Report A does. No CDN, no library.

## 1. Files (all in `design/mockups/front-pages/`)

| File | Owner task | What |
|---|---|---|
| `SPEC.md` | controller | This document |
| `fp-extract.json` | controller | 40 supplementary citations: file, line, verbatim excerpt (33 corpus legal and MD&A items, 7 synthetic Test CLO I items); the synthetic FY2027 capex is registered from `fixtures/synthetic-facts.json` in code |
| `build-fp-data.py` | T1 data | Stdlib Python; reads `../shared/data.js` and `fp-extract.json`, verifies, computes, writes `fp-data.js`; `--check` runs its self-test |
| `fp-data.js` | T1 (generated) | `window.RBOT_FP`, then merges its citations, calcs, gaps and figures into `window.RBOT_DATA` |
| `fp-shell.js`, `fp.css` | T2 shell | The app shell generalised from `../report-a.js`: `window.FP` |
| `fp-blocks-a.js`, `fp-blocks-a.css` | T3a blocks | Earnings, credit view, company, instruments, relative value, Portfolio Fit and decision blocks |
| `fp-blocks-b.js`, `fp-blocks-b.css` | T3b blocks | Covenant, liquidity, refinancing, distress and recovery blocks |
| `earnings-update.html/.js`, `relative-value.html/.js`, `covenant-refinancing.html/.js`, `distressed-restructuring.html/.js`, `portfolio-decision.html/.js`, `index.html` | T4 pages | One page each: config, call band, Front Page layout; the index |

Page `<head>` and script order (paths relative to `front-pages/`):

```html
<link rel="stylesheet" href="../shared/tokens.css">
<link rel="stylesheet" href="../report-a.css">
<link rel="stylesheet" href="fp.css">
<link rel="stylesheet" href="fp-blocks-a.css">
<link rel="stylesheet" href="fp-blocks-b.css">
...
<script src="../shared/data.js"></script>
<script src="fp-data.js"></script>
<script src="../shared/charts.js"></script>
<script src="fp-shell.js"></script>
<script src="fp-blocks-a.js"></script>
<script src="fp-blocks-b.js"></script>
<script src="earnings-update.js"></script>   <!-- calls FP.boot(config) -->
```

The body markup copies `../report-a-ic-paper.html` (banner `hidden data-artifact-only`, skip link, pane with `<img class="brand-logo" data-brand src="../../../brand/ssim-logo-horizontal-white.png" alt="State Street Investment Management" width="176" height="22">`, search, `#nav`, `#main`, `#route-live`). The `<title>` is "⟨Front Page title⟩: Caesars Entertainment (CZR), RBOT Report".

## 2. Shell (`fp-shell.js`, `fp.css`)

Start from a copy of `../report-a.js`. Keep: display formatting, helpers, `rich`, `itemNodes`, notes, tables, figure numbering, `draw`, `naFigure`, `cb`, view tools, `newView`, `plainHead`, the module-view anatomy, the Model view, Evidence view, Limitations view, nav, contents line, spy, Key popover, search, routing, print, boot sequence. Remove: the Snapshot builder, `TOPICS`, `EXTRAS`, `QUESTIONS`, topic routing and everything that reads `D.modules`. The pathway object replaces them.

### 2.1 Boot

```js
FP.boot({
  pathway: "EARNINGS_UPDATE",            // key into RBOT_FP.pathways
  call: function (api) { return { title: "Credit view", illus: true, items: [/* {k, node} or {divider: true} */], lines: [{ k: "The quarter", nodes: [/* nodes */] }] }; },
  front: function (grid, api) { api.block(grid, "headlineResults", { cls: "span-7" }); /* ... */ api.condLine(grid, "What changed since the last Report", "…"); },
  sections: { "CP-1B": ["headlineResults", "varianceDrivers"] }   // optional overrides of FP.moduleSections
});
```

Boot order: Front Page view, each nav module view in plan order, Model, Portfolio Fit (only when `pathway.hasFit`), Evidence, Limitations, footer, contents lines, nav, search, `tidyDates`, `RBOTUI.init`, `RBOTUI.roving`, routing. Same as Report A.

### 2.2 Views and routes

- `#front-page` (default and fallback): figure prefix `FP` (Fig. FP.1, FP.2 …). It keeps the class `view--snapshot` so Report A's title band and grid styles apply.
- `#module-cp-1b` etc. for each module in `pathway.nav`; prefix = the module code (Fig. CP-1B.1).
- `#model` (M), `#portfolio-fit` (PF, only with FIT), `#evidence` (E), `#limitations`.
- Section anchors: `#<module-slug>-<block key>` (e.g. `#cp-1b-headline-results`) and `#<module-slug>-gaps`.
- Folding as Report A: CP-5 renders inside Evidence, CP-6 inside Portfolio Fit; `#module-cp-5` and `#module-cp-6` still resolve.

### 2.3 Title band (Front Page)

H1 = "Caesars Entertainment (CZR)". Meta line, middot-separated: ⟨pathway.frontTitle⟩ · ⟨pathway.label⟩, Full depth · Primary: 2026 Fertitta merger financing · Q2 2026 · No RBOT run exists; this is a design mockup. Then the contents line, then the call band from `config.call(api)`:

- `.call.on-navy` with `.call__label` (title, ILLUSTRATIVE tag when `illus`, "By Credit Research · 2 Oct 2026").
- `.call__cells` holds up to six items; `{divider: true}` separates groups (the next item gets `call__item--first`). Each item is `{k: "Credit Score", node: <badge>, sub?: [nodes]}`; `sub` is an optional 12px soft-blue line under the badge.
- `.call__lines`: up to three lines `{k, nodes}`; `k` is at most 14 characters so `.call__lk` stays on one line.

### 2.4 Pane

- First entry: the Front Page with `pathway.navLabel` and the code tag `FP` (`nav__code`).
- "Analysis" group heading and tally ("11 modules: 10 with limitations, 1 pass"), then one row per `pathway.nav` module: plain name, code, round status mark (Report A's row). When the group has more than eight modules add `nav--compact` to its list: rows 1.75rem min height, the name on one line (names are at most 20 characters, §3.3).
- Then Model, Portfolio Fit, Evidence, Limitations. When `!pathway.hasFit`, Portfolio Fit is a non-link `span.nav__a.nav__a--absent` (`aria-disabled="true"`, soft-blue text at reduced emphasis) reading "Portfolio Fit" with a 12px second line "Not in this Pathway".
- Pane meta: "⟨pathway.label⟩ · Q2 2026 · Analysis 2 Oct 2026".
- Acceptance: the whole pane fits without scrolling at 1440×900 on every page; at 1280×800 it fits for Earnings Update, Covenant & Refinancing and Portfolio Decision, and scrolls inside the pane (never the page) for Relative Value and Distressed, with the current row scrolled into view.

### 2.5 Block contract (shared by T3a, T3b and T4)

```js
FP.defineBlock("headlineResults", {
  title: "Headline results",           // sentence case; the bar shows it in capitals
  short: "Results",                    // contents-line label (optional)
  key: "headline-results",             // section id suffix in the owner's view
  owner: "CP-1B",                      // module id, or "MODEL" | "FIT" | "CP-6" | "CP-5"
  illus: false, model: false, synth: false,
  meta: function (api) { return ["Q2 2026 against Q2 2025, US$ m"]; },   // bar meta nodes
  foot: function (api) { return [api.txt("Source: …")]; },               // Front Page footer source line
  condition: function (api) { return null; },  // or a string: the block is replaced by a condition line
  body: function (body, api, mode) { /* mode "summary" on the Front Page, "full" in a module view */ }
});
```

- `api.block(grid, name, {cls, open, keep})` draws a Front Page block: `cb()` with the definition's title, meta and tags, the grid span `cls`, the footer source line and a "Full analysis" link to the owner's section (`#cp-1b-headline-results`; MODEL → `#model`, FIT and CP-6 → `#portfolio-fit`, CP-5 → `#evidence`; no link when the owner module is not in this pathway). When `condition(api)` returns text, it draws `api.condLine(grid, title, text)` instead.
- Module views: a module's sections are `config.sections[id] || FP.moduleSections[id] || []`, drawn in order with Report A's paper `add()` and `body(..., "full")`; a section id is `<module-slug>-<key>`. Then "Gaps and limitations" (the module's `refs` gaps plus gaps cited in its headline), then the pager. A module with an empty list shows its anatomy, headline, Sources and gaps only.
- `FP.moduleSections` is filled by the blocks files (`FP.moduleSections["CP-4"] = ["covenantTests", "capacity", "redFlags"]`); pages override per pathway with `config.sections`.

### 2.6 `api` (passed to every builder)

Data: `D` (RBOT_DATA), `X` (RBOT_FP), `PW` (the pathway), `F` (`D.figures`), `T` (`D.tables`), `K` (`D.charts`), `XK` (`X.charts`), `I` (`D.illustrative`), `XI` (`X.illustrative`), `XB` (`X.blocks`), `FIT` (`X.fit`), `M` (`D.meta`).

Helpers kept from Report A with the same behaviour: `el`, `txt`, `rich`, `itemNodes`, `tk`, `ck`, `fd`, `refDatum`, `gapD`, `th`, `tdD`, `tdN`, `rowTh`, `table`, `periodTable`, `pick`, `kvTable`, `srcNote`, `subh`, `draw`, `naFigure`, `figHost`, `cb`, `sourceNote`, `sourcesDisclosure`, `swRows`, `scaleRec`, `dirBadge`, `dirChip`, `modelTag`, `nw`, `glue`, `capSummary`, `capitalTable`, `debtStack`, `loanRv`, `hyRv`, `profileTable`, `opmSentence`, `opmFacts`, `gapTable`, `displayFormat`.

New: `block`, `condLine`, `wordBadge`, `statusChip` (`RBOTUI.status` plus rule 5's covenant mapping), `illusTag`, `synthTag`, `fullLink(owner, key)`, `hasModule(id)`, `xtable(spec, mode)`.

- `xtable(spec, mode)` renders an `X.blocks.*` table spec (§3.5) with Report A's table classes: one `th` per column (unit on the second line), Datum cells through `RBOTUI.cell` (numbers right-aligned, tabular), plain strings as text, `{text, refs}` cells through `itemNodes` (figures become buttons), `{scale: "rec"|"val"|"score", pos, word}` and `{scale: "word", word, steps, pos}` cells through the badges, `{status}` cells through `statusChip`. Rows with `illustrative: true` get the dashed outline on their judgement cells. In `summary` mode only columns with `summary: true` (all columns when none is marked) and rows with `summary !== false` show.
- `wordBadge({label, word, steps, pos, illustrative, size})`: the neutral scale for word scales (gate status, ordinal, five-point, severity): bordered box, the word in bold, a meter of `steps` cells with the first `pos` filled; no position box. `aria-label` states label, word and "illustrative" when it is. On navy it follows `.on-navy .scale`. `size: "lg"` matches the call-band badges.
- `condLine(parent, title, text)`: a full-width `p.cond` (grid span 12): 1px grey-200 border on white, 0.4rem 0.75rem padding, 13px; the title in bold navy, then the text in slate; a leading 0.8rem dashed slate circle drawn in CSS. `id` = slug of the title, so it appears in the contents line.
- Figure numbering: `draw()` keeps a spec id's first number, so a chart drawn on the Front Page and again in its owner's view keeps `Fig. FP.n`.

### 2.7 Model, Portfolio Fit, Evidence, Limitations

- Model: Report A's `buildModel` unchanged.
- Portfolio Fit (only with FIT): H1 "Portfolio Fit"; sections `["portfolioFit", "fitLimits", "portfolioRecommendation"]` from the blocks, then the CP-6 fold with `FP.moduleSections["CP-6"]`. It reads `X.fit` (computed per §7), not Report A's `D.portfolio.fit`.
- Evidence: Report A's `buildEvidence` (the merged citations include `fp-extract.json`'s) and the CP-5 fold with a module-status table for this pathway's modules plus `FP.moduleSections["CP-5"]`.
- Limitations: Report A's view fed by `D.limitations` filtered to the gaps this pathway's modules and blocks cite, plus `PW.limitations`, plus `PW.notRun` lines: "Deep Research (CP-DR): not run. No research questions were approved at Approval and the Source Pack has no fetched sources." and "What changed (CP-8): not run. No earlier RBOT Report on Caesars was offered as a Prior Case."

### 2.8 `fp.css`

Only what Report A lacks: `.nav--compact`, `.nav__a--absent`, `.cond`, `.scale--word`, the on-navy corner-mark colours for `.figref` and `.cellref` inside `.call`, the call item `sub` line. Read `../report-a.css` first and reuse its classes; never restyle a Report A class globally.

## 3. Data (`build-fp-data.py` → `fp-data.js`)

Standard library only (`json`, `re`, `decimal`, `pathlib`, `sys`). `python3 build-fp-data.py [data.js] [fp-extract.json]` writes `fp-data.js`; `--check` asserts §3.7 and exits non-zero on any mismatch.

### 3.1 Inputs, ids, tokens

- Parse `../shared/data.js` as JSON (strip the leading comment line and `window.RBOT_DATA = `, and the trailing `;`).
- `fp-extract.json`: for each item open `corpus + file`, take line `line` (1-based, split on `\n`) and stop with the key named unless `excerpt` is a substring of that line. New ids continue the existing sequences in list order: citations `C338` onward (items without `synthetic`), synthetic items `S46` onward (`synthetic: true`, `prov: "synthetic"`), calculations `K110` onward, gaps `G29` onward. A rebuild gives the same ids.
- Every new citation, calculation and gap also gets a `figures[key]` Datum `{v, prov, ref, label, period, unit, raw}` as `build-data.py` writes them: negatives in parentheses (`(35)`), money with thousands separators, multiples and percentages to the stated places, `pp` values with their sign as a parenthesised negative.
- Templates in this spec: `{key}` or `{key|unit}` is a figure (resolved to `{C19|US$ m}`), `[key]` is a chip, `[G8]` an existing gap, `[gap:name]` a new gap (§3.4). Keys are `D.figures` keys, `fp-extract.json` keys or §3.2 keys; existing ids (`{K69|%}`) pass through. The script resolves every token and stops on an unknown key. A prose cell becomes `{text, refs}`.

### 3.2 Calculations

`Decimal`, `ROUND_HALF_UP`, computed from unrounded inputs; formula strings and `inputs` (the C/K/S ids used) as `build-data.py` writes them.

Earnings delta (period Q2 2026, inputs cited):

| key | formula | places, unit | expected |
|---|---|---|---|
| `eu_rev_chg_q2` | net_revenues_q2_2026 − net_revenues_q2_2025 | 0, USD millions | 86 |
| `eu_ebitda_chg_q2` | adj_ebitda_q2_2026 − adj_ebitda_q2_2025 | 0, USD millions | (35) |
| `eu_ebitda_pct_q2` | change / adj_ebitda_q2_2025 × 100 | 1, % | (3.7) |
| `eu_margin_q2_2025` | adj_ebitda_q2_2025 / net_revenues_q2_2025 × 100 | 1, % | 32.9 |
| `eu_margin_chg_pp` | Q2 2026 margin − Q2 2025 margin, unrounded | 1, pp | (2.1) |
| `eu_netloss_chg_q2` | net_income_attrib_q2_2026 − net_income_attrib_q2_2025 | 0 | 20 |
| `eu_int_chg_q2`, `eu_int_pct_q2` | interest_expense_q2_2026 against q2_2025 | 0; 1, % | (6); (1.0) |
| `eu_da_chg_q2`, `eu_da_pct_q2` | d_and_a_q2_2026 against q2_2025 | 0; 1, % | (9); (2.5) |
| `eu_capex_chg_q2`, `eu_capex_pct_q2` | capex_net_segment_q2_2026 against q2_2025 | 0; 1, % | (63); (27.4) |
| `eu_cfo_chg_h1`, `eu_cfo_pct_h1` | cfo_h1_2026 against cfo_h1_2025 | 0; 1, % | (5); (0.7) |
| `eu_netdebt_chg` | net_debt_calc_2026_06_30 − K7 | 0 | (176) |
| `eu_netlev_chg` | net_leverage_ltm − K54 | 2, x | (0.02) |
| `eu_seg_rev_pct_<s>` for s in las_vegas, regional, caesars_digital, managed_branded | seg_rev_<s>_q2_2026 against q2_2025 | 1, % | (3.5), 9.4, 2.3, (23.0) |
| `eu_seg_ebitda_pct_<s>` | seg_adj_ebitda_<s>_q2_2026 against q2_2025 | 1, % | (12.6), 11.2, (15.0), (5.9) |
| `eu_seg_margin_<s>_q2_2026`, `eu_seg_margin_<s>_q2_2025` | segment Adjusted EBITDA / segment net revenues × 100 | 1, % | 40.3 / 44.5; 31.1 / 30.6; 19.4 / 23.3; 28.1 / 23.0 |
| `eu_seg_margin_chg_<s>` | unrounded difference | 1, pp | (4.2), 0.5, (4.0), 5.1 |
| `rv_yield_pickup` | trace_czr_12769gad2_last_yield − trace_czr_12769gac4_last_yield | 2, pp | 1.25 |
| `dq_conv_<p>` for FY2023, FY2024, FY2025, H1 2025, H1 2026, LTM | CFO / Adjusted EBITDA × 100 (the period's cited or calculated figures) | 1, % | 45.9, 28.8, 35.9, 37.0, 37.4, 36.1 |

Liquidity, refinancing and covenants:

| key | formula | places, unit | expected |
|---|---|---|---|
| `cr_int_h1_2027` | guide_2027_interest / 2 | 0 | 375 |
| `cr_mat_h1_2027` | debt_maturity_2027 / 2 | 0 | 57 |
| `cr_rent_h1_2027` | ltm_cash_interest_rent_q2_2026 / 2 (round half up) | 0 | 682 |
| `cr_capex_h1_2027` | synthetic_capex_fy2027 / 2 (the synthetic Base FY2027 capex of 800, S citation from `fixtures/synthetic-facts.json`) | 0 | 400 |
| `cr_maint_h1_2027` | cr_capex_h1_2027 × guide_capex_remaining_2026_maintenance_high / guide_capex_remaining_2026_total_high | 0 | 190 |
| `cr_growth_h2_2026` | guide_capex_remaining_2026_growth_high + guide_capex_remaining_2026_digital_high | 0 | 205 |
| `cr_growth_h1_2027` | cr_capex_h1_2027 − cr_maint_h1_2027 | 0 | 210 |
| `cr_mand_uses` | guide_remaining_2026_debt_service + cr_int_h1_2027 + cr_mat_h1_2027 + guide_remaining_2026_lease_payments (C371, US$687m) + cr_rent_h1_2027 + guide_capex_remaining_2026_maintenance_high + cr_maint_h1_2027 | 0 | 2,601 |
| `cr_disc_uses` | cr_growth_h2_2026 + cr_growth_h1_2027 | 0 | 415 |
| `cr_op_inflow` | ltm_cfo_q2_2026 + ltm_cash_interest_debt_q2_2026 + ltm_cash_interest_rent_q2_2026 (the LTM level held flat; an assumption) | 0 | 3,436 |
| `cr_closing` | liq_total + cr_op_inflow − cr_mand_uses − cr_disc_uses (30 June 2027) | 0 | 3,348 |
| `cr_headroom` | liq_total − cr_mand_uses | 0 | 327 |
| `cr_runway_months` | liq_total / (cr_mand_uses / 12): 12 months from 30 June 2026, lease payments included | 1, months | 13.5 |
| `cr_rcf_share` | liq_cei_rcf_net / liq_total × 100 | 1, % | 72.7 |
| `cr_liq_left_2026`, `_2027`, `_2028`, `_2029`, `_2030`, `_after` | liq_total less cumulative annual maturities (debt_maturity_remaining_2026 … debt_maturity_thereafter), less liq_cei_rcf_net from 2028 (the CEI RCF matures 31 Jan 2028) | 0 | 2,873; 2,759; (138); (1,712); (5,674); (11,009) |
| `cr_gap_2028`, `_2029`, `_2030`, `_after` | the shortfall (−liq_left) where liq_left < 0 | 0 | 138; 1,712; 5,674; 11,009 |
| `cr_rcf_util_pct` | debt_cei_rcf_face_2026_06_30 / (cei_rcf_commitment × 1,000) × 100 | 1, % | 5.3 |
| `cov_tlr_headroom` | cov_max_total_leverage − net_leverage_ltm | 2, x | 3.48 |
| `cov_fccr_headroom` | cash_interest_cover_ltm − cov_min_fccr | 2, x | 2.63 |
| `cov_sslr_headroom` | cov_incr_pari_sslr − senior_leverage_ltm | 2, x | 1.86 |
| `ind_fccr_headroom` | cash_interest_cover_ltm − ind_ratio_debt_fccr | 2, x | 2.63 |
| `cap_pari_secured` | cov_incr_pari_sslr × ltm_adj_ebitda_q2_2026 − senior_secured_debt_2026_06_30 | 0 | 6,696 |
| `cap_junior_secured` | cov_incr_junior_tslr × ltm_adj_ebitda_q2_2026 − senior_secured_debt_2026_06_30 | 0 | 7,594 |
| `cap_free_clear_size` | max(cov_incr_free_clear_floor, 1.00 × ltm_adj_ebitda_q2_2026) | 0 | 3,592 |
| `lme_sec_lme` | senior_secured_debt_2026_06_30 + cap_pari_secured | 0 | 16,164 |
| `lme_uns_base` | senior_secured_debt_2026_06_30 + unsecured_debt_2026_06_30 | 0 | 11,768 |
| `lme_uns_lme` | lme_uns_base + cap_pari_secured | 0 | 18,464 |

Distress and recovery (CP-4C). The scenario multiples are ILLUSTRATIVE inputs (`X.illustrative.scenarioMultiples`: Downside 5.0x, Stress 4.0x). Every Datum derived from them carries `prov: "illustrative"` and `ref` = its K id, so the passport shows the formula and the cell shows the dashed outline.

| key | formula | places, unit | expected |
|---|---|---|---|
| `dr_ebitda_after_rent` | ltm_adj_ebitda_q2_2026 − ltm_cash_interest_rent_q2_2026 | 0 | 2,229 |
| `dr_merger_multiple` | ev_merger_usdm / dr_ebitda_after_rent | 2, x | 7.90 |
| `dr_ev_downside`, `dr_ev_stress` | multiple × dr_ebitda_after_rent | 0 | 11,145; 8,916 |
| `dr_alloc_<scenario>_<class>`, `dr_rec_<scenario>_<class>`, `dr_residual_<scenario>` for scenario in merger, downside, stress and class in secured, unsecured, other | absolute priority: senior secured (K57), then senior unsecured (K58), then other debt (K59); recovery = allocation / claim × 100; the merger scenario's available value is ev_merger_usdm | 0; 1, % | merger 100.0 / 100.0 / 100.0, residual 5,793; downside 100.0 / 72.9 / 0.0, residual 0; stress 94.2 / 0.0 / 0.0, residual 0 |

Fulcrum = the first class whose recovery is below 100%: merger none (equity takes the residual), downside senior unsecured, stress senior secured.

Portfolio Fit (§7, Test CLO I; synthetic inputs):

| key | formula | expected |
|---|---|---|
| `fit_one_pct_nav` | 1% × NAV (S18) | 6,309,285 USD |
| `fit_c01_room` | (2.5 − 0)% × NAV: C-01 limit (S1); Caesars exposure none (`clo_czr_existing`) | 15,773,213 |
| `fit_c04_room` | C-04 headroom 0.14% (S4) × NAV | 883,300 |
| `fit_c05_room` | C-05 headroom 1.27% (S5) × NAV, Soft | 8,012,792 |
| `fit_sector_room` | Leisure Facilities & Services headroom 5.43% (S32) × NAV, Soft | 34,259,418 |
| `fit_c10_room` | C-10 headroom 9.39% (S10) × NAV, Soft | 59,244,186 |

Amounts round to whole dollars. Per instrument (Term Loan B, Term Loan B-1, 7.00% SSN 2030, 6.50% SSN 2032, 4.625% SN 2029, 6.00% SN 2032) the touched limits are: C-01 always; C-04 (Hard) and C-05 (Soft) when the instrument has no issue rating in the sources (Unrated) or is rated Caa or CCC; C-10 (Soft) when unsecured; the Leisure sector limit (Soft). Only the two 2032 notes have issue ratings (C235/C236 B1/BB-; C244/C245 Caa1/B-); the others are Unrated ([gap:issue_ratings_other]). `max_size` = the minimum Hard `room`; binding = that limit; verdict per §7 rule 4 (Watch when `max_size` < `fit_one_pct_nav`); cap per rule 5; final = the weaker of the illustrative uncapped Recommendation (`D.illustrative.byInstrument`) and the cap. Expected: 6.50% SSN 2032 Fits, max 15,773,213 (C-01), final 2 Modest OW; Term Loan B, Term Loan B-1 and 7.00% SSN 2030 Watch, max 883,300 (C-04), final 3 MW; 4.625% SN 2029 Watch, final 4 Modest UW; 6.00% SN 2032 Watch, max 883,300 (C-04), final 4 Modest UW. The revolver, Term Loan A, CVA DDTL, SID bonds and other payables are "Not evaluated: bank or other facility". The proposed trade (US$5,000,000 par of the 6.50% SSN 2032, `clo_proposed_par`, 0.7925% of NAV, US$4,664,000 at 93.28) fits within its max size. Note on Report A: its illustrative fit reads C-01's 0.13% headroom, which is Asurion's; this computation uses Caesars' own exposure (none).

### 3.3 Modules (`X.modules`, keyed by id)

Plain names (at most 20 characters), §1 reader questions verbatim from the interfaces spec, statuses (`Pass` or `Restricted`, shown as "With limitations"), reasons and refs. Headlines are Model-written, one sentence, figures as tokens.

| id | name | status | reason (refs) | headline |
|---|---|---|---|---|
| CP-0 | Source readiness | Restricted | Ratings outlooks, Fitch, issue ratings beyond the two 2032 notes and the merger's debt terms are missing from the Source Pack. ([G10], [G11], [gap:issue_ratings_other], [G8]) | The Source Pack answers every Pathway's question except one input that moves them all: the merger's new debt [G8]. |
| CP-1 | Financials and debt | Pass | Historical financials, the debt table and liquidity reconcile to the filings. | Total debt {total_debt_check_2026_06_30\|US$ m} against LTM Adjusted EBITDA {ltm_adj_ebitda_q2_2026\|US$ m}: total leverage {total_leverage_ltm\|x}, before any merger debt. |
| CP-1A | Business and events | Restricted | No issuer or corporate family rating and no outlooks; merger debt terms unstated. ([G25], [G11], [G8]) | Fertitta's take-private at about US$17.6bn [merger_transaction_value] assumes Caesars' debt and adds new committed debt of unstated size [G8]. |
| CP-1B | Earnings delta | Restricted | Quarterly cash flows, cash interest and cash taxes are disclosed for six months only. ([G3], [G1], [G2]) | Q2 2026 net revenues rose {czr_rev_growth_q2_2026\|%} but Adjusted EBITDA fell {eu_ebitda_pct_q2\|%}: Regional grew with Caesars Windsor consolidated, while Las Vegas and Digital margins fell. |
| CP-1C | Peer benchmark | Restricted | Two peers only (MGM, PENN); their EBITDAR definitions differ. ([G14]) | Caesars' Q2 margin {czr_ebitda_margin_q2_2026\|%} sits above MGM's {K69\|%} and PENN's {K70\|%}, on company definitions that differ [G14]. |
| CP-1D | Earnings quality | Restricted | No unrealized add-backs are marketed; cash conversion is six-monthly only. ([G22], [G3]) | Q2 add-backs take Reported EBITDA {reported_ebitda_q2_2026\|US$ m} to {structuring_ebitda_q2_2026\|US$ m}; the GLPI and VICI leases of {lt_financing_obligations_2026_06_30\|US$ m} are the debt-like item that matters. |
| CP-2 | Credit synthesis | Restricted | The merger's new debt is unstated, so the post-close credit profile is open. ([G8]) | Fair today at {net_leverage_ltm\|x} net leverage and {interest_cover_ltm\|x} lease-inclusive cover; the direction turns on debt not yet disclosed [G8]. |
| CP-2A | Downside paths | Restricted | Downside paths cannot size the merger's new debt. ([G8]) | The first break is a layered take-private: pari secured capacity of {cap_pari_secured\|US$ m} under the 4.50x test would rank ahead of the unsecured notes. |
| CP-2D | Liquidity bridge | Restricted | No operating cash flow forecast (no guidance; the bridge holds the LTM level) and no 2027 capex estimate (a synthetic test value is used). ([G13], [gap:capex_2027]) | Liquidity of {liq_total\|US$ m} covers mandatory uses of {cr_mand_uses\|US$ m} over the 12 months from 30 June 2026, lease payments included: {cr_runway_months} months of runway before any operating cash flow. |
| CP-2G | Forecast cases | Restricted | No company guidance and no forward rate deck in the pack. ([G13], [gap:rate_deck]) | none (the module view says Base and Downside need assumptions the pack cannot cite) |
| CP-2H | Rating triggers | Restricted | Agency reports and their trigger thresholds are not in the pack. ([gap:agency_triggers], [G11]) | The unsecured 2032s are rated {trace_czr_12769gad2_moodys} by Moody's (rated 28 September 2026); no agency threshold is in the sources [gap:agency_triggers]. |
| CP-3 | Relative value | Restricted | TRACE gives yields, not spreads; no loan prices. ([G19], [G18]) | The secured 2032s at {trace_czr_12769gac4_last_price} yield {trace_czr_12769gac4_last_yield\|%}; the unsecured 2032s at {trace_czr_12769gad2_last_price} yield {trace_czr_12769gad2_last_yield\|%}, {rv_yield_pickup\|pp} more for a junior claim. |
| CP-3C | Refinancing and LME | Restricted | Restricted payment and investment baskets were not extracted; merger tranches unstated. ([gap:rp_capacity], [G8]) | The pinch point is 31 January 2028, when the CEI revolver and its {liq_cei_rcf_net\|US$ m} of capacity mature; liquidity left before refinancing turns negative that year. |
| CP-3D | Market-implied risk | Restricted | No spreads or risk-free curve, so implied default is not computable. ([G19], [gap:implied_pd]) | The market prices the unsecured 2032s {rv_yield_pickup\|pp} over the secured 2032s; implied default is not computable [gap:implied_pd]. |
| CP-4 | Covenants and legal | Restricted | Agreement definitions are not reconciled to company figures; RP and investment baskets not extracted. ([gap:covenant_basis], [gap:rp_capacity]) | Maintenance tests protect only the revolver and Term A: total leverage {net_leverage_ltm\|x} against {cov_max_total_leverage\|x}, and Term B-1 is a Non-Covenant Facility. |
| CP-4C | Recovery and fulcrum | Restricted | Scenario multiples are illustrative; lease claims are not modelled. ([gap:lease_claims]) | At the illustrative 5.0x downside the unsecured notes are the fulcrum, recovering {dr_rec_downside_unsecured\|%}; at the merger value every class recovers in full. |
| CP-5 | Evidence checks | Pass | Every cited figure resolves to a file, line and excerpt. | none |
| CP-6 | Challenge and decision | Restricted | Recommendations rest on illustrative judgement; the merger's debt is unstated. ([G8]) | none |

### 3.4 New gaps (`[gap:name]` → G29 onward, in this order)

| name | field | reason |
|---|---|---|
| capex_2027 | Capital expenditure estimate for 2027 | not in the sources; the 10-Q estimates capital expenditure for the remainder of 2026 only |
| rate_deck | Forward rate deck | no forward SOFR curve or rate deck is in the Source Pack |
| agency_triggers | Agency rating-trigger thresholds | no rating-agency report is in the Source Pack, so downgrade and upgrade thresholds are not stated |
| rp_capacity | Restricted payment and investment basket capacity | the credit agreement and indenture baskets for restricted payments and investments were not extracted |
| incremental_usage | Incremental amounts already used | amounts used under the incremental free-and-clear clause since the Third Amendment are not stated in the sources |
| covenant_basis | Agreement-basis covenant ratios | the agreement's EBITDA, Total Net Debt and Cash Interest Expense are not reconciled to company figures; current ratios are on RBOT's basis (company Adjusted EBITDA, face debt) |
| issue_ratings_other | Issue ratings for the term loans, the 2030 secured notes and the 2029 notes | not in the sources; the TRACE pages rate the two 2032 notes only |
| structure_map | Restricted, unrestricted and guarantor subsidiaries | the entity and guarantor structure is not extracted; the supplemental indentures add guarantors without a full list in the extraction |
| implied_pd | Market-implied default probability | needs spreads or a risk-free curve (G19) and a recovery assumption; not computed |
| lease_claims | Treatment of the GLPI and VICI master leases in a restructuring | not modelled; lease claims are excluded from the waterfall and the leases are assumed to continue |
| cr_score | CR Score for the merger's new tranches | the new tranches are not stated in the sources (G8), so no CR Score can be read |
| bond_eligibility | Whether a senior secured bond is an eligible Test CLO I asset | the mandate excerpt does not say |

### 3.5 Block tables (`X.blocks`)

Each is `{title, unit?, columns: [{key, label, unit?, num?, summary?}], rows: [{<column key>: cell, summary?, kind?, illustrative?}], note?}`. Cells are Datums, plain strings, `{text, refs}` (prose with tokens resolved), `{scale, pos, word, steps?}` or `{status}`.

- `periodComparison` (CP-1B): metric, reference, current, change, change %, basis (comparison_basis), restatement, perimeter change. Rows: Net revenues (Q2 2025, Q2 2026; perimeter change Yes: Caesars Windsor consolidated from 3 March 2026 [mgmt_driver_regional]); Adjusted EBITDA (Yes); Adjusted EBITDA margin (`eu_margin_q2_2025` against `czr_ebitda_margin_q2_2026`, change in pp, change % blank); Net loss attributable to Caesars; Interest expense, net; Depreciation and amortization; Capital expenditures, net by segment; Cash from operations (H1 2025 against H1 2026, note "six months: quarterly cash flows not disclosed [G3]"); Net debt (31 Dec 2025 against 30 Jun 2026, basis "LTM vs FY"); Net leverage (FY2025 against LTM). Summary rows: net revenues, Adjusted EBITDA, margin, interest expense, net debt, net leverage.
- `segmentChanges` (CP-1B): segment, net revenues Q2 2025, Q2 2026, change %, Adjusted EBITDA Q2 2025, Q2 2026, change %, margin Q2 2026, margin change. The four segments plus Corporate and Other (figures cited; change % n/a with reason "not meaningful: the sign changes").
- `varianceDrivers` (CP-1B): metric; management says (cited `{text, refs}` from `mgmt_driver_*`); analyst view (ILLUSTRATIVE, Model); credit implication (ILLUSTRATIVE; full mode only). Rows: Las Vegas (mgmt_driver_las_vegas; analyst: "Margin {eu_seg_margin_chg_las_vegas|pp} to {eu_seg_margin_las_vegas_q2_2026|%}: hold and volume, not price, so partly reversible"; implication: "Las Vegas is the higher-margin segment, so its decline costs more EBITDA than Regional adds"); Regional (mgmt_driver_regional; analyst: "Revenue up {eu_seg_rev_pct_regional|%} with Windsor consolidated from 3 March: not like-for-like"; implication: "Organic growth is lower than reported"); Caesars Digital (mgmt_driver_digital; analyst: "Revenue up {eu_seg_rev_pct_caesars_digital|%}, Adjusted EBITDA {eu_seg_ebitda_pct_caesars_digital|%}"; implication: "Growth is being bought with promotion or hold"); Interest expense (mgmt_driver_interest; analyst: "{eu_int_pct_q2|%} on lower debt and floating rates"; implication: "Merger debt will reverse this [G8]").
- `kpiChanges` (CP-1B): KPI, reference, current, change, unit, trend (delta_direction). Rows: segment Adjusted EBITDA margin for the four segments (calculated).
- `guidance` (CP-1B): one row: metric "Revenue and Adjusted EBITDA guidance", benchmark n/a [G13], actual {adj_ebitda_q2_2026|US$ m}, variance n/a, note: "No guidance, and no conference call because of the pending merger [release_no_call]".
- `signals` (CP-1B; severity ILLUSTRATIVE): Las Vegas margin compression (High); Regional growth flattered by the Windsor consolidation (Medium); Digital revenue up, Adjusted EBITDA down (Medium); unsecured 2032s at {trace_czr_12769gad2_last_price} and rated {trace_czr_12769gad2_moodys} (High). Each with evidence tokens and a credit implication.
- `watchItems` (CP-2, ILLUSTRATIVE): trigger, threshold or signal, why it matters. Merger debt terms (amount and ranking of the committed financing [G8]); Las Vegas margin (below {eu_seg_margin_las_vegas_q2_2026|%} for a second quarter); CEI revolver maturity [cei_rcf_maturity]; merger End Date {merger_initial_end_date} and ticking fee from {merger_ticking_fee_date}.
- `creditView` (CP-2, ILLUSTRATIVE): Credit Score, Credit Direction, Sector Outlook (from `D.illustrative`), primary support "Secured leverage {senior_leverage_ltm|x} and liquidity {liq_total|US$ m}", primary downside "Unstated merger debt [G8]", confidence Medium, basis Full.
- `transactionsEvents` (CP-1A, cited): merger agreement signed {issuer.merger.agreement_date}; go-shop ended {merger_go_shop_end}; End Date {merger_initial_end_date}, extendable to {merger_first_extended_end_date} and {merger_second_extended_end_date}; ticking fee from {merger_ticking_fee_date}; Caesars Windsor consolidated from 3 March 2026 [mgmt_driver_regional].
- `documentRegister` (CP-4, cited): Credit Agreement (20 Jul 2020) and Incremental Assumption Agreement No. 3 (6 Feb 2024), Fourth Amendment (9 May 2024), Fifth Amendment (25 Nov 2024), 6.500% Senior Secured Notes due 2032 Indenture (6 Feb 2024; trustee U.S. Bank Trust Company), First and Second Supplemental Indentures (1 Mar 2024, 23 Aug 2024), Merger Agreement (27 May 2026, C11). Columns: document, type, date, parties, status ("In force"; the Merger Agreement "Signed, pending close").
- `covenantTests` (CP-4): test, type (test_type), direction, threshold (cited), current (calculated, RBOT basis), basis, headroom (calculated), status (trigger_status). Rows: Total Leverage Ratio | Maintenance | Ceiling | `cov_max_total_leverage` | `net_leverage_ltm` | "RBOT basis [gap:covenant_basis]" | `cov_tlr_headroom` | Headroom; Fixed Charge Coverage Ratio | Maintenance | Floor | `cov_min_fccr` | `cash_interest_cover_ltm` | same basis | `cov_fccr_headroom` | Headroom; Pari secured incremental | Incurrence | Ceiling | `cov_incr_pari_sslr` | `senior_leverage_ltm` (gross) | same basis | `cov_sslr_headroom` | Headroom; Ratio debt (2032 indenture) | Incurrence | Floor | `ind_ratio_debt_fccr` | `cash_interest_cover_ltm` | same basis | `ind_fccr_headroom` | Headroom. `note`: "Maintenance tests apply to the Covenant Facilities only [cov_covenant_facilities]; after Term A is repaid they spring only when revolver use exceeds {cov_testing_condition_pct|%} of commitments [cov_springing_after_tla]; use today is {cr_rcf_util_pct|%}."
- `capacity` (CP-4): capacity type, basket, formula (cited text), used, remaining, status (calc_status), severity (ILLUSTRATIVE), credit implication (ILLUSTRATIVE). Rows: Debt, Pari secured to 4.50x (used `senior_secured_debt_2026_06_30`, remaining `cap_pari_secured`, Calculated, High); Debt, Junior secured to 4.75x (used the same, remaining `cap_junior_secured`, Calculated, Medium; "an alternative to the pari amount, not additive"); Debt, Free-and-clear (size `cap_free_clear_size`, used n/a [gap:incremental_usage], remaining n/a, Not computable, Medium); Debt, Unsecured ratio debt at FCCR 2.00x (n/a: pro forma interest on new debt unknown, Not computable); Restricted payments (n/a [gap:rp_capacity], Not computable).
- `redFlags` (CP-4; provision cited; severity ILLUSTRATIVE): Term B-1 is a Non-Covenant Facility [cov_tlb1_non_covenant] (High); maintenance tests spring after Term A [cov_springing_after_tla] (Medium); the asset-sale sweep falls away at senior secured leverage of 3.00x or below [cov_asset_sale_stepdown_300], and Caesars is at {senior_leverage_ltm|x} (High); equity cure right [cov_equity_cure] (Medium); pro forma synergies in indenture EBITDA [ind_pro_forma_synergies] (Medium); pari secured capacity of {cap_pari_secured|US$ m} could rank ahead of the unsecured notes (High). One protective row, marked "Protective": change of control put at {ind_change_of_control|%} on the 2032 secured notes (Low).
- `ebitdaDefinition` (CP-4): feature, clause, cap or condition, capacity effect. Rows: pro forma cost savings and synergies ([ind_pro_forma_synergies]; "reasonably expected", no numeric cap in the excerpt; raises capacity); Testing Condition carve-out of US$170m of undrawn letters of credit ([cov_testing_condition_pct]); asset-sale step-downs at {cov_asset_sale_stepdown_350|x} and {cov_asset_sale_stepdown_300|x}.
- `protectionScore` (CP-4, ILLUSTRATIVE five_point): Maintenance covenants 2; Debt and lien capacity 2; Change of control 4; Asset-sale protection 2; Disclosure 3. Evidence tokens per row.
- `structureMap` (CP-4): entities from the sources only: Caesars Entertainment, Inc. (borrower and notes issuer; C1, C228); Subsidiary Guarantors (added by the supplemental indentures; doc_suppl1_date, doc_suppl2_date); CVA (separate borrower of the DDTL and revolver; C138, C168); GLPI and VICI (landlords; financing obligations C184). Every other column n/a [gap:structure_map].
- `liquiditySources` (CP-2D): from `D.tables.liquidity`: component, amount, accessible (yes_no: Yes except the reserves and regulatory commitments), restriction.
- `cashUses` (CP-2D): use, amount, timing, mandatory; the 12 months from 30 June 2026. Debt service, second half of 2026 (C273, Yes); Interest, first half of 2027 (`cr_int_h1_2027`, Yes); Debt maturities, first half of 2027 (`cr_mat_h1_2027`, Yes); VICI and GLPI lease payments, second half of 2026 (C371, Yes); lease payments, first half of 2027 (`cr_rent_h1_2027`, Yes); Maintenance capex, second half of 2026 (C283, Yes); Maintenance capex, first half of 2027 (`cr_maint_h1_2027`, Yes); Growth and digital capex, second half of 2026 (`cr_growth_h2_2026`, No); Growth and digital capex, first half of 2027 (`cr_growth_h1_2027`, No). Operating cash inflow is in the bridge, not this table.
- `runway` (CP-2D): Accessible liquidity `liq_total`; Mandatory uses, 12 months to 30 Jun 2027 `cr_mand_uses`; Headroom `cr_headroom`; Months of runway `cr_runway_months`; Pinch point: "31 January 2028: the CEI revolver matures [cei_rcf_maturity]; its net capacity {liq_cei_rcf_net|US$ m} is {cr_rcf_share|%} of liquidity."
- `maturityPressure` (CP-3C): fiscal year, maturing (C178–C183), liquidity left before refinancing (`cr_liq_left_*`), funding gap (n/a "no gap" where liquidity left ≥ 0, else `cr_gap_*`), pressure (ordinal, ILLUSTRATIVE: 2026 Low, 2027 Low, 2028 High, 2029 High, 2030 High, thereafter Medium).
- `lmeCapacity` (CP-3C): indicator, available (availability), evidence, paths enabled. Pari secured incremental (Available; {cap_pari_secured|US$ m} indicative; priming by dilution); Junior secured incremental (Available; {cap_junior_secured|US$ m}); Non-covenant Term B-1 (Available; [cov_tlb1_non_covenant]); Unrestricted subsidiary and drop-down capacity (Unclear; [gap:rp_capacity]); Equity cure (Available; [cov_equity_cure]).
- `refinancingPaths` (CP-3C, ILLUSTRATIVE): path, feasibility (ordinal), likelihood direction, evidence for, evidence against, creditor impact. Merger closes with committed financing (High; for: committed financing from ten banks [issuer.merger.financing], not subject to a financing condition [issuer.merger.financing_condition]; against: size unstated [G8]); Revolver and Term A extended before 2028 (Medium); Amend-and-extend of Term Loan B 2030 (Medium); Exchange of the unsecured notes into secured debt (Low).
- `creditorExposure` (CP-3C): class, case (exposure_case), claims at or ahead (calculated), priming risk (ordinal, ILLUSTRATIVE). Senior secured Base `senior_secured_debt_2026_06_30`, LME `lme_sec_lme`; Senior unsecured Base `lme_uns_base`, LME `lme_uns_lme`; Stress rows n/a [G8] ("the stress case needs the merger's debt").
- `distressGate` (CP-4C; status ILLUSTRATIVE, evidence cited): trigger, evidence, status (gate_status). Market prices debt at distressed levels: unsecured 2032s at {trace_czr_12769gad2_last_price}, yield {trace_czr_12769gad2_last_yield|%} (Not met); Rating in Caa or below: unsecured {trace_czr_12769gad2_moodys}, rated 28 Sep 2026 (Met); Liquidity runway under 12 months: {cr_runway_months} months on the 12-month, lease-inclusive basis (Not met); Maturity within 24 months without a path: next large maturity 2028, {debt_maturity_2028|US$ m} (Not met); Leverage after the merger debt: unstated [G8] (Unclear); Missed payment, covenant breach or LME announced: none in the sources (Not met). Overall: Unclear.
- `claims` (CP-4C): class, claim, obligor, amount, security, priority rank. Senior secured (K57; CEI and CVA; rank 1; note: CVA is a separate borrower, treated pari here); Senior unsecured (K58; CEI; rank 2); Other debt (K59; rank 3, "priority not stated, ranked last"); Lease financing obligations (C184; excluded [gap:lease_claims]).
- `evScenarios` (CP-4C): scenario, valuation basis, metric, multiple, EV. Merger value (transaction value, cited `ev_merger_usdm`; metric `dr_ebitda_after_rent`; multiple `dr_merger_multiple`, calculated); Downside (ILLUSTRATIVE 5.0x; `dr_ev_downside`); Stress (ILLUSTRATIVE 4.0x; `dr_ev_stress`).
- `recoveries` (CP-4C): scenario, class, allowed claim, available value, allocation, residual, recovery %, fulcrum (yes_no).
- `restructuringPaths` (CP-4C, ILLUSTRATIVE): path, process, consent, new money, class treatment, milestones, blockers, likelihood (ordinal). Merger closes and new debt is layered pari (out of court; no consent needed within capacity; unsecured diluted; High); Amend-and-extend with secured lenders (Medium); Distressed exchange of the unsecured notes (Low); Chapter 11 with the master leases assumed (Low; [gap:lease_claims]).
- `ratingTriggers` (CP-2H): agency, rating type, metric, threshold n/a [gap:agency_triggers], current (issue ratings cited), status Not computable. `migrationView` (ILLUSTRATIVE): Moody's and S&P; Base and Downside; likely transition; earliest timing "at merger close"; catalyst "the new debt terms [G8]"; confidence Low.
- `instrumentLevels` (CP-3): per capital-structure facility: instrument, level basis (Market for the two TRACE notes, None otherwise), level date, price, yield (YTM), spread n/a [G19], valuation (ILLUSTRATIVE V-scale: 6.50% SSN 2032 V2, 6.00% SN 2032 V4, others n/a "no level"), Recommendation (`D.illustrative.byInstrument`). Loans: price n/a [G18].
- `compensation` (CP-3, ILLUSTRATIVE): instrument, structural rank, recovery sensitivity (ordinal), compensation against risk (compensation), comparables. 6.50% SSN 2032: rank 1, Low, Attractive, "MGM 6.125% 2029 at {trace_mgm_552953ck5_last_yield|%}"; 6.00% SN 2032: rank 2, High, Inadequate, "{rv_yield_pickup|pp} over the secured for a fulcrum-risk claim"; term loans: Unclear [G18].
- `securityPreference` (CP-3, ILLUSTRATIVE): 6.50% SSN 2032 Preferred; 7.00% SSN 2030 Neutral; Term Loan B and B-1 Requires more work [G18]; 6.00% SN 2032 Avoid; 4.625% SN 2029 Avoid. Key reason and monitoring trigger per row.
- `marketVsFundamental` (CP-3D, ILLUSTRATIVE alignment): "Unsecured priced for distress" against "net leverage {net_leverage_ltm|x} before merger debt": Divergent, basis "the market prices the unstated merger debt [G8]"; "Secured below par at {trace_czr_12769gac4_last_price}" against "secured leverage {senior_leverage_ltm|x}": Aligned.
- `peerSet` (CP-1C): MGM and PENN with selection basis and comparability (ILLUSTRATIVE) and data availability (cited revenue and Adjusted EBITDA; [G14]).
- `cashConversion` (CP-1D): FY2023, FY2024, FY2025, H1 2025, H1 2026, LTM: Adjusted EBITDA, CFO, conversion (`dq_conv_*`).
- `addbackAssessment` (CP-1D, ILLUSTRATIVE verdicts): Transaction costs and other, Q2 2026 (C204, REALIZED, Supported, "issuer-stated; includes merger costs [merger_transaction_costs_2026]"); Stock-based compensation (C206, REALIZED, Supported).
- `debtLikeItems` (CP-1D, ILLUSTRATIVE treatment): GLPI and VICI financing obligations (C184, Debt-like); operating lease liability (C188 at 31 Dec 2025, Debt-like; 30 Jun 2026 n/a [G5]); finance leases (C191, Debt-like).
- `downsidePaths` (CP-2A, ILLUSTRATIVE): Layered take-private (first break: unsecured recovery; at close; probability Medium; impact High); Las Vegas downturn (first break: lease-inclusive cover {interest_cover_ltm|x}; Medium; Medium); 2028–2030 refinancing wall without the revolver (Low; High).
- `challenge` (CP-6, ILLUSTRATIVE): claim, counter-evidence, resolution, what would change the view. "Secured 2032s are money-good after the merger" against "pari capacity {cap_pari_secured|US$ m} dilutes them"; "The unsecured notes are the fulcrum" against "at the merger value every class recovers in full"; "Las Vegas weakness is cyclical" against "two segments lost margin in the same quarter".
- `bindingLimitations` (CP-5): module, limitation, effect on the decision, source that would lift it. Merger debt (G8); loan prices (G18); issue ratings ([gap:issue_ratings_other]: the loans count as Unrated in Test CLO I's CCC bucket); spreads (G19); bond eligibility ([gap:bond_eligibility]).

### 3.6 Chart specs (`X.charts`; RBOTCharts kinds, Datums; each with `id`, `title`, `summary`, `source`, `unit`)

| id | kind | content |
|---|---|---|
| `fig-headline-results` | columns | categories Adjusted EBITDA, Interest expense net, D&A, Capex net (segment table); series Q2 2025 (`color` 6, neutral) and Q2 2026 (chart-1); US$ m |
| `fig-kpi-margins` | dumbbell | segment Adjusted EBITDA margin, Q2 2025 → Q2 2026, % |
| `fig-liquidity-bridge` | waterfall | Opening accessible liquidity (total, 30 Jun 2026) → operating cash flow before cash interest and rent at the LTM level (delta `cr_op_inflow`, positive) → the nine 12-month uses (negative deltas: debt service, interest, maturities, lease payments, maintenance capex, growth and digital capex, each H2 2026 and H1 2027 where applicable) → closing before refinancing (total `cr_closing`, 30 Jun 2027) |
| `fig-funding-gap` | columns | categories 2026 (rest), 2027, 2028, 2029, 2030, Thereafter; series Maturing (cited) and Liquidity left before refinancing (calculated; negative values below zero) |
| `fig-covenant-headroom` | bullet | the four `covenantTests` rows; direction max for Ceiling, min for Floor |
| `fig-basket-capacity` | stackedColumns | categories Pari secured 4.50x, Junior secured 4.75x, Free-and-clear; series Used and Remaining (free-and-clear both n/a) |
| `fig-lme-exposure` | columns | categories Senior secured, Senior unsecured; series Base, LME (claims at or ahead) |
| `fig-recovery-by-class` | columns | categories Senior secured, Senior unsecured, Other debt; series Merger value, Downside 5.0x, Stress 4.0x; recovery %; illustrative Datums (hatched) |
| `fig-value-allocation-merger`, `-downside`, `-stress` | waterfall | EV (total) → allocation per class (negative deltas) → residual (total) |
| `fig-fit-limits` | bullet | the limits the proposed instrument touches: C-01, Leisure sector; and for comparison the CCC bucket C-04 and Unrated C-05 that bind the unrated instruments; current % NAV, threshold, headroom; synthetic Datums |

Reuse from `D.charts` without copying: `leverage`, `coverage`, `liquidity` (historical strip), `maturityWall`, `ebitdaBridge`, `yieldCurve`, `peerRange`, `segments`, `risk`, `revenueEbitda`.

### 3.7 Self-check (`--check`)

Assert every "expected" value in §3.2, every excerpt verified, no Datum with a numeric-looking `v` carries `prov: "gap"`, every `{key}` token resolved, and no `RBOT_DATA` id overwritten.

### 3.8 `X.pathways`

| key | label | navLabel | frontTitle | nav (plan order) | hasFit |
|---|---|---|---|---|---|
| EARNINGS_UPDATE | Earnings Update | Earnings update | Earnings Update: Q2 2026 | CP-0, CP-1, CP-1A, CP-1B, CP-1D, CP-2 | no |
| RELATIVE_VALUE | Relative Value | Relative value | Relative Value | CP-0, CP-1, CP-1A, CP-1D, CP-1C, CP-2, CP-2A, CP-4, CP-2G, CP-3D, CP-3 | yes |
| COVENANT_REFINANCING | Covenant & Refinancing | Covenants & refinancing | Covenant & Refinancing | CP-0, CP-1, CP-1A, CP-1D, CP-2, CP-4, CP-2D, CP-3C | no |
| DISTRESSED_RESTRUCTURING | Distressed & Restructuring | Distress & recovery | Distressed & Restructuring | CP-0, CP-1, CP-1A, CP-1D, CP-2, CP-2A, CP-4, CP-2D, CP-2G, CP-2H, CP-3D, CP-3C, CP-4C, CP-3 | yes |
| PORTFOLIO_DECISION | Portfolio Decision | Portfolio decision | Portfolio Decision | CP-0, CP-1, CP-1A, CP-1D, CP-2, CP-2A, CP-4, CP-3D, CP-3 | yes |

Each pathway also carries `plan` (the §5 Full list verbatim), `folded` (`{"CP-5": "evidence"}`, plus `"CP-6": "portfolio-fit"` when CP-6 is in the plan), `notRun` (CP-DR and CP-8 lines, §2.7) and `limitations` (the new gaps its modules cite, each `{ref, field, text, scope: "Source Pack gap"}`).

## 4. Pages

Grid: Report A's `.fp` 12-column grid with its `span-*` classes. First-viewport acceptance is at 1440×900; every page also gets a 1280×800 screenshot with no horizontal scroll. Blocks are open unless marked collapsed.

### 4.1 Earnings Update (`earnings-update.html`)

Purpose (§4.2): what the period changed, and whether the credit view moves. No Recommendation, Valuation or Portfolio Fit: the Pathway runs no CP-3, CP-6 or FIT.

Call band: title "Credit view", ILLUSTRATIVE. Items: Credit Score (3 Fair), Credit Direction (Deteriorating), Sector Outlook (Neutral; an arrow badge like Credit Direction), divider, "Since last Report": a word badge "No Prior Case" drawn with the n/a styling (dashed box), Sponsor quality (Medium, word badge). Lines: "The quarter": "Net revenues {net_revenues_q2_2026|US$ m}, up {czr_rev_growth_q2_2026|%}; Adjusted EBITDA {adj_ebitda_q2_2026|US$ m}, {eu_ebitda_pct_q2|%}; margin {czr_ebitda_margin_q2_2026|%}, {eu_margin_chg_pp|pp}. Regional includes Caesars Windsor from 3 March." "Watch": "Merger debt terms [G8]; Las Vegas margin {eu_seg_margin_las_vegas_q2_2026|%}, down {eu_seg_margin_chg_las_vegas|pp}." "Recommendation": "Not produced by an Earnings Update (no CP-6); this page answers whether the credit view moves."

Layout, in order:
1. `headlineResults` span-7 (summary rows of `periodComparison` beside `fig-headline-results` at ≥ 1400px, stacked below) | `varianceDrivers` span-5 (metric, management says, analyst view; credit implication in full mode only).
2. `kpiChanges` span-7 (`fig-kpi-margins` + compact table) | `guidanceSignals` span-5 (the guidance row as one n/a sentence with its reason, then the signals with severity word badges).
3. `ebitdaAdjustments` span-5 (`D.charts.ebitdaBridge` + the Reported → Structuring → SSIM table) | `metricStrip` span-7 (historical strip: leverage, coverage, liquidity from `D.charts`, three plots in a row; meta "Historical only").
4. `financials` span-12 (Report A's financials and credit metrics tables).
5. `watchItems` span-6 | `historicalPerformance` span-6 (Model prose `D.illustrative.historicalPerformance` + `D.charts.revenueEbitda`).
6. `companyProfile` span-12, collapsed (compact: sector, country, ratings, outlooks, Sponsor Quality).
7. Condition line "What changed since the last Report": "Not shown: no Prior Case was accepted at Approval; this is the first RBOT Report on Caesars."

Acceptance: at 1440×900 the call band, the headline results table and chart, and the variance drivers are fully visible.

Module sections: CP-0 `sourceInventory`, `companyProfile`; CP-1 `financials`, `capitalStructure`; CP-1A `companyProfile`, `operatingModel`, `transactionsEvents`; CP-1B `headlineResults`, `segmentChanges`, `varianceDrivers`, `kpiChanges`, `guidanceSignals`, `historicalPerformance`; CP-1D `ebitdaAdjustments`, `addbackAssessment`, `cashConversion`, `debtLikeItems`; CP-2 `creditView`, `strengthsWeaknesses`, `watchItems`.

### 4.2 Relative Value (`relative-value.html`)

Purpose (§4.3): which instrument is best compensated for its risk, and at what level.

Call band: title "Analyst recommendation", ILLUSTRATIVE. Items as Report A: CLO, Indexed Loans, Indexed HY, divider, Valuation, Credit Score, Credit Direction. Lines: "Preferred": "6.50% secured 2032s at {trace_czr_12769gac4_last_price}, {trace_czr_12769gac4_last_yield|%}: Preferred. 6.00% unsecured 2032s at {trace_czr_12769gad2_last_price}: Avoid, {rv_yield_pickup|pp} more for a claim behind {senior_secured_debt_2026_06_30|US$ m} of secured debt." with the ILLUSTRATIVE tag after the judgement words. "Portfolio Fit": the Test CLO I line from `X.fit` (proposed US$5.0m of the secured 2032s Fits; loans and unrated notes Watch, max {fit_c04_room|US$} under C-04) + "Details in Portfolio Fit" + SYNTHETIC.

Layout:
1. `instrumentLevels` span-7 | `spreadCurve` span-5 (`D.charts.yieldCurve`; meta "Yield to maturity; spreads n/a G19").
2. `compensation` span-7 (with the preference column joined) | `marketVsFundamental` span-5.
3. `peerPositioning` span-6 (`D.charts.peerRange`) | `capitalStructure` span-6 (Report A's capital structure summary with multiples and % EV, and its debt stack).
4. `rvBlocks` span-12 (Report A's loan and HY relative value tables), collapsed.
5. `instrumentRecommendation` span-12 (per instrument: Recommendation, Valuation, rationale).
6. `portfolioFit` span-12 (per instrument verdict, max size, binding limit).
7. `creditViewLine` span-12, collapsed (Credit Score, Direction, Sector Outlook, Sponsor quality, sector, country, issue ratings).
8. Condition line "What changed since the last Report".

Acceptance: the band, the instrument table and the yield chart visible at 1440×900.

Module sections: CP-0, CP-1, CP-1A as 4.1; CP-1D as 4.1 without `addbackAssessment`; CP-1C `peerSet`, `peerPositioning`; CP-2 `creditView`, `strengthsWeaknesses`; CP-2A `downsidePaths`, `riskMatrix`; CP-4 `covenantTests`, `redFlags`, `capacity`; CP-2G `forecastCases` (n/a frame with its reasons); CP-3D `observations`, `spreadCurve`, `impliedRisk` (n/a frame), `marketVsFundamental`; CP-3 `instrumentLevels`, `compensation`, `securityPreference`, `rvBlocks`, `instrumentRecommendation`. CP-6 fold: `portfolioRecommendation`, `thesisChallenge`.

### 4.3 Covenant & Refinancing (`covenant-refinancing.html`)

Purpose (§4.4): which provisions protect creditors, and whether the issuer can refinance. No Recommendation or Fit (no CP-3, CP-6, FIT). Primary run: CR Score per new tranche shows as n/a.

Call band: title "Covenant and refinancing view", ILLUSTRATIVE. Items: Credit Score; "Covenant tests": the covenant status chip "Headroom" (calculated, not illustrative) with `sub` "Maintenance, 2 tests"; "Lender protection": word badge five-point (pos 2, word "2 of 5", illustrative); "Refinancing pressure": word badge ordinal (High, 3 steps, illustrative); divider; Credit Direction. Lines: "Covenants": "Total Leverage {net_leverage_ltm|x} against {cov_max_total_leverage|x}; FCCR {cash_interest_cover_ltm|x} against {cov_min_fccr|x}; tested for the revolver and Term A only, and Term B-1 has no maintenance test." "Liquidity": "{liq_total|US$ m} against mandatory uses of {cr_mand_uses|US$ m} over 12 months from 30 June 2026, lease payments included: {cr_runway_months} months; the revolver matures 31 January 2028." "New tranches": "Merger debt unstated; CR Score n/a [gap:cr_score]."

Layout:
1. `covenantTests` span-7 (`fig-covenant-headroom` + the table; the springing note under it) | `liquidityRunway` span-5 (`fig-liquidity-bridge` + the runway rows).
2. `maturityWall` span-7 (`D.charts.maturityWall` + the capital structure summary) | `fundingGap` span-5 (`fig-funding-gap` + the pressure table).
3. `capacity` span-6 (`fig-basket-capacity` + table) | `redFlags` span-6 (flags with severity word badges; the protective change-of-control row last).
4. `ebitdaDefinition` span-6 | `protectionScore` span-6.
5. `refinancingPaths` span-12 (paths, then the LME capacity table and `fig-lme-exposure` side by side).
6. `documentRegister` span-12, collapsed. `structureMap` span-12, collapsed.
7. Condition line "What changed since the last Report".

Acceptance: the band, the covenant bullets and the liquidity bridge visible at 1440×900.

Module sections: CP-0, CP-1, CP-1A, CP-1D as 4.1; CP-2 `creditView`, `strengthsWeaknesses`; CP-4 `documentRegister`, `covenantTests`, `capacity`, `structureMap`, `redFlags`, `ebitdaDefinition`, `protectionScore`; CP-2D `liquiditySources`, `cashUses`, `liquidityRunway`; CP-3C `fundingGap`, `lmeCapacity`, `refinancingPaths`, `creditorExposure`.

### 4.4 Distressed & Restructuring (`distressed-restructuring.html`)

Purpose (§4.5): is the distress gate met; which path and fulcrum are most credible; what recoveries follow.

Call band: title "Distress view and recommendation", ILLUSTRATIVE. Items: "Distress gate": word badge "Unclear" (3 steps: Not met, Unclear, Met; pos 2); divider; CLO, Indexed Loans, Indexed HY; divider; Credit Score. Lines: "Fulcrum": "Senior unsecured in the 5.0x downside ({dr_rec_downside_unsecured|%} recovery); senior secured in the 4.0x stress ({dr_rec_stress_secured|%}); none at the merger value." "Instrument": "Prefer the 6.50% secured 2032s; avoid the unsecured notes." "Portfolio Fit": as 4.2.

Layout:
1. `distressGate` span-5 | `recoveries` span-7 (a three-row scenario strip, Merger value / Downside / Stress with EV and multiple, then `fig-recovery-by-class`, the fulcrum named per scenario; bar meta "Gate Unclear: shown, as the rule requires for Met or Unclear").
2. `claims` span-7 | `liquidityRunway` span-5.
3. `fundingGap` span-6 (with the LME capacity table) | `covenantLevers` span-6 (`fig-covenant-headroom` + a compact red flags list).
4. `ratingTriggers` span-5 (n/a frame + migration view) | `restructuringPaths` span-7.
5. `instrumentDecision` span-12 (levels, preference and Recommendation per instrument).
6. `portfolioFit` span-12.
7. Condition line "What changed since the last Report".

Acceptance: the band, the gate table and the recovery chart visible at 1440×900.

Module sections: CP-0, CP-1, CP-1A, CP-1D, CP-2 as 4.3; CP-2A `downsidePaths`, `riskMatrix`; CP-4 `covenantTests`, `redFlags`, `capacity`; CP-2D `liquiditySources`, `cashUses`, `liquidityRunway`; CP-2G `forecastCases`; CP-2H `ratingTriggers`, `migrationView`; CP-3D `observations`, `spreadCurve`, `impliedRisk`, `marketVsFundamental`; CP-3C `fundingGap`, `lmeCapacity`, `refinancingPaths`, `creditorExposure`; CP-4C `distressGate`, `claims`, `evScenarios`, `recoveries`, `valueAllocation` (three waterfalls), `restructuringPaths`; CP-3 `instrumentLevels`, `compensation`, `securityPreference`, `instrumentRecommendation`. CP-6 fold: `portfolioRecommendation`, `thesisChallenge`.

### 4.5 Portfolio Decision (`portfolio-decision.html`)

Purpose (§4.6): should each portfolio own it, how much, and which instrument.

Call band: title "Portfolio decision", ILLUSTRATIVE. Items: CLO, Indexed Loans, Indexed HY (Strategy recommendations); divider; "Test CLO I": the final Recommendation badge for the proposed instrument (2 Modest OW) with `sub` "Secured 2032s · Fits, no cap"; Valuation; Credit Score. Lines: "Test CLO I": "Proposed US$5.0m par of the 6.50% secured 2032s ({clo_proposed_weight_par|%} of NAV): Fits, max {fit_c01_room|US$} under C-01. Loans and unrated notes: Watch, max {fit_c04_room|US$} under C-04, because no issue rating is in the sources." + SYNTHETIC. "Other books": "Indexed Loans and Indexed HY: no portfolio attached; Fit not run."

Layout:
1. `portfolioRecommendation` span-5 (portfolio, strategy, instrument, uncapped, cap, final, verdict; uncapped and final as rec badges) | `portfolioFit` span-7 (`fig-fit-limits` + per instrument verdict, max size, binding limit).
2. `instrumentDecision` span-7 | `capitalStructure` span-5.
3. `strengthsWeaknesses` span-12 (credit view line + Report A's strengths and weaknesses grid).
4. `thesisChallenge` span-12 (thesis, catalysts, challenge).
5. `bindingLimitations` span-12.
6. Condition line "What changed since the last Report".

Acceptance: the band, the per-portfolio table and the Fit bullets visible at 1440×900.

Module sections: CP-0, CP-1, CP-1A, CP-1D, CP-2 as 4.3; CP-2A `downsidePaths`, `riskMatrix`; CP-4 `covenantTests`, `redFlags`, `capacity`; CP-3D `observations`, `spreadCurve`, `marketVsFundamental`; CP-3 `instrumentLevels`, `compensation`, `securityPreference`, `instrumentRecommendation`. CP-6 fold: `portfolioRecommendation`, `thesisChallenge`. CP-5 fold: `bindingLimitations`.

## 5. Block inventory and owners

| Block | File | Owner | Draws |
|---|---|---|---|
| headlineResults, segmentChanges, varianceDrivers, kpiChanges, guidanceSignals, historicalPerformance | a | CP-1B | `periodComparison`, `segmentChanges`, `varianceDrivers`, `kpiChanges`, `guidance` + `signals`; `fig-headline-results`, `fig-kpi-margins`, `D.charts.revenueEbitda` |
| ebitdaAdjustments, addbackAssessment, cashConversion, debtLikeItems | a | MODEL (ebitdaAdjustments), CP-1D | `D.tables.ebitdaAdjustments`, `D.charts.ebitdaBridge`; `X.blocks` tables |
| metricStrip, financials, capitalStructure | a | MODEL; CP-1 for capitalStructure in module views | `D.charts.leverage/coverage/liquidity`; Report A tables; `capSummary`, `debtStack` |
| sourceInventory, companyProfile, operatingModel, transactionsEvents | a | CP-0, CP-1A | citations grouped by file (count per file, document type from the file name); `profileTable`, `opmFacts`; `transactionsEvents` |
| creditView, creditViewLine, strengthsWeaknesses, watchItems, downsidePaths, riskMatrix, forecastCases | a | CP-2, CP-2A, CP-2G | `creditView`; Report A strengths and weaknesses; `watchItems`; `downsidePaths`; `D.charts.risk`; n/a frame |
| peerSet, peerPositioning | a | CP-1C | `peerSet`; `D.charts.peerRange` |
| instrumentLevels, spreadCurve, observations, impliedRisk, marketVsFundamental, compensation, securityPreference, rvBlocks, instrumentRecommendation, instrumentDecision | a | CP-3, CP-3D | `X.blocks`; `D.charts.yieldCurve`; `D.tables.trace`; `loanRv`, `hyRv` |
| portfolioFit, fitLimits, portfolioRecommendation, thesisChallenge, bindingLimitations | a | FIT, CP-6, CP-5 | `X.fit`, `fig-fit-limits`, `D.illustrative.thesis/catalysts`, `challenge`, `bindingLimitations` |
| documentRegister, covenantTests, covenantLevers, capacity, structureMap, redFlags, ebitdaDefinition, protectionScore | b | CP-4 | `X.blocks`; `fig-covenant-headroom`, `fig-basket-capacity` |
| liquiditySources, cashUses, liquidityRunway | b | CP-2D | `X.blocks`; `fig-liquidity-bridge` |
| maturityWall, fundingGap, lmeCapacity, refinancingPaths, creditorExposure | b | MODEL (maturityWall), CP-3C | `D.charts.maturityWall`; `fig-funding-gap`, `fig-lme-exposure` |
| distressGate, claims, evScenarios, recoveries, valueAllocation, restructuringPaths, ratingTriggers, migrationView | b | CP-4C, CP-2H | `X.blocks`; `fig-recovery-by-class`, `fig-value-allocation-*`, `fig-rating-triggers` (n/a frame) |

## 6. Index (`index.html`)

A single white paper sheet in the house world, no pane: H1 "RBOT Front Pages", a one-sentence lede (design exploration; Caesars Q2 2026 figures from public filings; every judgement illustrative), then a dense bordered table with six rows (the five pages and Report A's Credit Snapshot at `../report-a-ic-paper.html`): page name as a link, its Pathway, the reader question it answers (§4 purpose), modules in its pane, and what leads its first viewport. Footer: the mockup disclaimer. No cards, no thumbnails.

## 7. Done means

- Every page loads with no console error, routes every pane destination, and every Front Page block's "Full analysis" link lands on its section.
- `python3 build-fp-data.py --check` exits 0.
- Screenshots at 1440×900 and 1280×800 for each page, checked by eye against §4's acceptance lines.
- `impeccable detect` over the changed files; findings fixed or justified.
- The brand-stripped artifact gallery (no State Street name, no logo, no `SSIM` in visible text) is published from copies; the repo files keep the logo.
