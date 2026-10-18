# Step 2 prompt for Claude Design (Direction C chosen)

Paste below the line into the same Claude Design project.

---

I choose **Direction C, Workbench**. Proceed to Step 2 as `PROMPT.md` sets out: first the design system, then the full interactive mock composed only from its components. Keep Direction C's world as you stated it: the icon rail, navigator, panelled canvas, navy verdict bar and persistent inspector; Red Hat Display, Text and Mono; navy and electric blue for brand and action; forest, amber and brick as signals.

## Refine these before building on them

1. **Inspector inputs.** In a calculated figure's passport, each formula input shows its citation id, label and value (e.g. "Liquidity table: total cash on hand and borrowing capacity, US$2,928m"), and clicking it opens that input's passport. Today they render as bare glyphs.
2. **Provenance density.** In dense tables (Capital structure, Financials, the Model grid) the per-figure provenance glyph is accurate but noisy. Default to a small muted mark, strengthened on row hover or focus, with the full mark and words in the inspector. Show the Capital structure table and a Model band both ways, and recommend one.
3. **Navigator families.** Don't separate module families by hue: nine family colours beside green, amber and red status marks dilute the signal. Use family icons or a neutral tint; keep colour for status alone.
4. **Chart gaps.** n/a marks sit at their own category on the axis with the gap id, not floating above the plot (see the leverage plot in the strip).
5. **The honest state** (a run that produced no Recommendation or Valuation, as the real CAOS runs did) is a designed state of the verdict bar: the tiles say "Not produced", with the reason and the module that would produce it, never blank. Design it as a component state, not a tweak.
6. **Behaviour to specify:** 1280×800 (the navigator starts closed; the rail, the `/` module switcher and the inspector stay); keyboard order across the rail, navigator, canvas and inspector, with focus landing in the inspector when a figure is chosen and Escape returning to the figure; print (the inspector does not print, and the passports of figures on the page print as numbered endnotes).

## Design system deliverables

- **Tokens** as CSS custom properties: brand, neutral ramp, signal (positive, caution, negative, neutral) with text, fill and on-navy variants and their contrast values, chart palette, type scale (Red Hat Display, Text, Mono), spacing, radii, borders, focus, motion (reduced-motion variant).
- **Components, each with every state and data variation** (1 and 20 rows; short and long text; present, absent, n/a, Blocked):
  - verdict bar and position tile;
  - panel;
  - dense table, key/value table and period grid;
  - chart frame and each chart kind used by the runs;
  - status, verdict and scale marks;
  - provenance marks;
  - gap chip;
  - icon set;
  - rail, navigator and module switcher;
  - inspector (source, formula, gap, synthetic, table twin, gaps on page);
  - condition line;
  - search;
  - empty and not-run states.
- For each component, show which `rbot-run/1` fields fill it, so the Python template can render it.

## Full mock

All six Front Pages, each from its `data/test/*.run.json`:
- Credit Snapshot (`czr-full-credit-assessment`);
- Earnings Update (`czr-earnings-update`, with the Prior Case);
- Relative Value (`czr-relative-value`, and the Blocked variant);
- Covenant & Refinancing;
- Distressed & Restructuring (`larchmere-distressed-restructuring`);
- Portfolio Decision (two portfolios, one Breaches).

Then every module view, Model (with PF-LTM and Base/Downside from the full Credit Assessment run), Portfolio Fit, Evidence, Limitations, search, "How to read a figure", and print.

Keep every rule in `PROMPT.md`, "Rules that must survive any direction" and "Data honesty".
