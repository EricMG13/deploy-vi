# RBOT Report: Claude Design hand-off pack

Private. For the owner's private Claude Design project only.

## Read in this order

1. `PROMPT.md`: the message to paste into Claude Design with this pack; `PROMPT-STEP2.md` and `DECISION.md` after the direction pick (Direction C, Workbench).
2. `BRIEF.md`: the design brief (product, readers, the ask, look and feel, brand, non-negotiables, data).
3. `content/`: what every surface must say.
   - `00-app-shell.md`: destinations, navigation per Pathway, module-view anatomy, global behaviour, platform constraints
   - `01-credit-snapshot.md` … `06-portfolio-decision.md`: the six Front Pages (purpose, the call, blocks with data paths and real values, first-viewport priority, states, module views)
   - `07-model.md`: the Model view (RBOT's own design brief)
   - `provenance-and-states.md`: provenance grammar, house scales, states every design must cover
   - `colour-and-icons.md`: colour as a signal, and where icons beat text
4. `data/`: the figures.
   - `README.md`: data guide, quick-reference figures, the real fund holdings
   - `rbot-data-base.json`, `front-pages-data.json`, `corpus-extract.json`: real Caesars Q2 2026 figures with file, line and excerpt; calculations; gaps; illustrative judgements (labelled)
   - `caos-runs/`: real module outputs from live CAOS runs on the same pack, with `README.md`
   - `test/`: eight complete test runs (`rbot-run/1`) populating every module, table and chart, with `README.md`
5. `reference/`
   - `report-a-current/`: the incumbent Credit Snapshot Report (screenshots at 1440 px, 2× density; `runnable/report-a-ic-paper.html` opens from disk; `DESIGN-report-a.md` is its design system)
   - `rejected-directions/`: alternatives B (verdict rail) and C (period spine), rejected on 11 October 2026
   - `PRODUCT.md`, `CONTEXT.md`: product truth and the glossary (owner instructions of 17 October override PRODUCT.md where they differ: no Excel template, modern application look, Report A in scope)
6. `brand/`: the State Street Investment Management logo files and their rules.

## Owner instructions captured here (17 October 2026)

- Clean, modern SaaS look in the company colours; colour as a signal; icons where they beat text; Report A is in scope for the redesign.
- No Excel requirement: the Credit Snapshot keeps its content, not the Excel template's form.
- The Report still carries a full financial model; design its view for this Report, do not copy caos-databricks's app.
- Three design directions first; the owner approves one before a full interactive mock is built.

## Not included, on purpose

- The owner's Sector RV workbook screenshots (`~/Desktop/Market Data/`): they carry Bloomberg identifiers and prices (licensed data). Add them only if your data policy allows.
- The old Excel Credit Snapshot template screenshots (the Excel requirement is retired).
- caos-databricks's model layout example (a different platform; see `content/07-model.md`).
