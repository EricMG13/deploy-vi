---
version: 1
slug: "design-mockups-report-a-ic-paper-html"
primary_target: "design/mockups/report-a-ic-paper.html"
related_targets: ["design/mockups/report-b-verdict-rail.html","design/mockups/report-c-period-spine.html"]
---

# Surface: RBOT Report (front page + drill-down)

Scope: the HTML Report RBOT renders per run; the mockups show Full Credit Assessment, whose Front Page is the Credit Snapshot. Mode: Read (the reader must understand the call and its basis; wayfinding and comprehension first). Platform: desktop browser on wide monitors, laptop minimum; print secondary.

Audience and job: PMs (decide own/size/avoid; want the call, the risk and the valuation in a minute) and the credit research team (check, challenge, trace any figure to its source in two clicks). Constraint: charts, analytics, visualisations and key findings visible immediately; every section expands for detail; provenance visible (cited / calculated / model-authored); missing values are n/a gaps with reasons.

World (settled, house): State Street Investment Management — deep navy #000533 section bars with white bold caps, dense bordered tables, cool grey ground #F0F2F5, electric blue #0017E5 for interaction, mint/soft-blue accents sparingly, Inter / Inter Tight; logo top-right (owner-supplied file). Data is real CZR Q2 2026 figures with citations; every judgement (scores, recommendation, thesis) labelled ILLUSTRATIVE.

Surface roll (impeccable concept-seed key 1943d727, mode read): ranked structures 1 template-faithful snapshot + tabs; 2 question-led bands; 3 verdict rail + scrolling analysis; 4 KPI-tile dashboard; 5 split snapshot ↔ evidence pane; 6 investment-committee paper; 7 period spine. Dealt: 6 (lead), 3, 7. All three are built as hi-fi mockups for the owner to choose one.

## Direction contracts

A — IC paper (THE ROLL)
THESIS: the Report as a numbered committee paper whose page one is the Credit Snapshot; refuses the dashboard-of-cards default.
OWN-WORLD: house navy bars as section rules, paper-white sheet on #F0F2F5, numbered sections, figures numbered and captioned, margin notes carry citations.
STORY: read page one, see the call and five charts; open any numbered section for the analysis.
FIRST VIEWPORT: title band with recommendation per Strategy; Credit Snapshot blocks in template order with the Model chart strip and capital-structure chart above the fold; sticky contents rail.
FORM: IC paper, rank 6, seed 1943d727.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

B — Verdict rail
THESIS: the call never leaves the screen; a sticky left rail holds recommendation, scores, PF metrics and top risks while the analysis scrolls; refuses the long scroll where the conclusion disappears.
OWN-WORLD: navy rail, white main column of chart-led cards with navy bar headings, evidence drawer from the right.
STORY: scan the rail, scroll chart-led Snapshot cards, expand any card in place, open evidence beside it.
FIRST VIEWPORT: rail (logo, issuer, Recommendation per Strategy, Credit Score, Valuation, PF leverage, top three risks, section index with status); main: key findings + Model chart strip + capital structure.
FORM: verdict rail, rank 3, seed 1943d727.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

C — Period spine
THESIS: credit is a story over time; a horizontal period spine (FY23 → LTM → PF-LTM → FY+1–3) organises the figures, charts and events; refuses static single-period tables.
OWN-WORLD: navy spine band with period stops, event pins (merger, maturities), charts aligned to the spine's columns, house tables beneath.
STORY: read the call, scrub the spine, watch metrics and blocks update to the chosen period, expand detail.
FIRST VIEWPORT: verdict band; the spine with the leverage / coverage / liquidity strip aligned to it; Snapshot blocks keyed to the selected period.
FORM: period spine, rank 7, seed 1943d727.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Owner decision (2026-10-11)

Chosen: **A — IC paper**, amended:
1. A persistent left navigation pane through which the reader reaches every part of the Report without scrolling the whole document: the Report becomes an app shell of views (hash-routed), not one long page.
2. The Credit Snapshot is a summary screen only; each module's output is its own view with its full analysis (reader question, headline, status and limitations, charts, detailed tables, findings with citations, gaps).
3. Sections are collapsible; the company description moves near the top of the Snapshot and gains the issuer's operating model (segments, revenue mix, property footprint, owned versus leased real estate, digital), every fact cited.
4. Clarity and polish: impeccable critique at max effort by one model (Fable), implementation by another (Opus).

Amended FIRST VIEWPORT (A): left pane (logo, issuer, run line, navigation: Snapshot, each module with status, Model, Portfolio Fit, Evidence, Limitations); main: title band with the call per Strategy and Valuation, key findings, company description with operating model, then the Model chart strip and capital structure; every block collapsible and linked to its module view.
