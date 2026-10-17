# Initialisation prompt for Claude Design

Attach the whole pack, then paste everything below the line.

---

You're designing the Report application for **RBOT**, a credit-research tool for leveraged-finance portfolio managers and credit analysts at State Street Investment Management. Each RBOT run turns one issuer's documents into a governed credit analysis and produces one Report: a self-contained HTML application, opened from disk.

The attached pack holds everything you need. Read it before designing, in this order:
1. `README.md`
2. `BRIEF.md`
3. everything in `content/`
4. `data/README.md`
5. `data/test/README.md`

Ask me only what the pack can't answer.

## Look and feel

- **Clean, modern SaaS, in the company colours.**
  - Deep navy `#000533` and electric blue `#0017E5` carry the brand, the frame and every action.
  - A calm neutral surface carries the content.
  - It should feel like a best-in-class analytics product, not a printed paper or a spreadsheet.
- **Colour is a signal.**
  - Use positive, caution, negative and neutral, applied by what a value means for the creditor (leverage up is bad; headroom is good). That covers statuses, verdicts, directions, severities and scale positions.
  - Colour is never the only carrier: always pair it with a word, an icon or a position marker.
  - Keep most of the surface neutral, so the signals stand out.
  - Provenance is not a signal colour; it keeps its own marks. See `content/colour-and-icons.md`.
- **Icons where they beat text.** `content/colour-and-icons.md` lists my candidates: statuses, verdicts, directions, severities, provenance marks in dense tables, actions, navigation families, document types.
  - Confirm, cut or add to that list.
  - Use one consistent icon set, drawn as inline SVG (the Report is offline).
  - Give every icon an accessible name and a tooltip.
  - Keep words where an icon would be ambiguous: scale values, numbers, gap reasons, headings.
- **Density for experts.** PMs read on wide monitors and want the call, the main risk and the valuation within a minute. Analysts want every figure one click from its source.

## Step 1: three design directions

Give me three directions that differ in layout model and navigation, not only in palette. For each direction, render with the real data at 1440×900:
1. the **Credit Snapshot** Front Page: first viewport, then the full scroll (`content/01`);
2. one dense Front Page: **Covenant & Refinancing** (`content/04`) or **Distressed & Restructuring** (`content/05`, using the fictional distressed issuer in `data/test/`);
3. one **module view** (Earnings delta CP-1B or Covenants and legal CP-4), with the source popover open on a cited figure;
4. the **Model view**'s first viewport (`content/07`);
5. **navigation** holding 14 to 17 modules, plus its collapsed form.

For each direction, state:
- its thesis in one sentence;
- its colour system: the signal palette with contrast values;
- its type system;
- its component language: the call, tables, charts, status and verdict marks, provenance marks, icons;
- its honest risk.

I'll pick one direction.

## Step 2, after I pick: the design system, then the full interactive mock

First deliver a **design system**, because the Report is rendered by a template from variable data:
- **Tokens** (brand and signal colours with contrast values, type scale, spacing, radii, chart palette, motion) as CSS custom properties.
- **Every component with its states**: call band, block, tables, chart frame and each chart kind, status and verdict marks, scale badges, provenance marks, icons, navigation, popover, condition line, search, empty and n/a states. Show each at 1 and 20 rows, with short and long text, present and absent.

Then compose the mock **only from those components**. Build all six Front Pages from `data/test/*.run.json`, so every block and chart is populated, and then:
- the application shell;
- every module view's anatomy;
- Model, Portfolio Fit, Evidence and Limitations;
- the source popover;
- search and "How to read a figure";
- collapsed and expanded states;
- the n/a, not-run, absent, Blocked, Breaches, Tight, Prior Case ("What changed") and Primary new-issue states;
- print.

## Rules that must survive any direction

These are in `content/provenance-and-states.md` and `BRIEF.md` §6.
- The call first: each Front Page's verdict and key charts are visible without scrolling.
- Every figure opens to its source (file, locator, excerpt) or its formula.
- Cited, calculated, model-written, illustrative and synthetic content never look alike, and not by colour alone.
- A missing value shows as n/a with its reason, never zero.
- Every chart has a table twin, a summary and a source line, with provenance in its marks.
- WCAG 2.2 AA throughout; keyboard-reachable charts; 24px minimum targets.
- Buildable: one offline HTML file, rendered by a Python template from the run JSON. Design components that take variable rows, lengths and presence, not one-off pages.
- Charts are SVG components drawn in the browser by a small vanilla JS kit, so every mark stays focusable and source-linked. Draw small in-cell visuals (headroom bars, meters, severity bars) in CSS. No canvas, no images, no charting library.
- Desktop: 1280×800 minimum, 1440×900 typical; phone out of scope.

## Data honesty

- **Caesars (CZR) Q2 2026 figures are real.** Each carries its file, line and verbatim excerpt.
- **Real CAOS analysis** (`data/caos-runs/`) is cautious: no recommendation, relative value "Unclear", distress gate "Not Applicable". Design that honest state alongside the populated one.
- **The test runs fill what the sources lack** with values marked **synthetic**, each citing its own "TEST DATA" record. Render the synthetic mark wherever such a value appears.
- **Larchmere Leisure Group is fictional.**
- **Every judgement is illustrative** and must say so.
- **Never invent a number** beyond the data in the pack.

## Brand

- Use the State Street Investment Management logo files in `brand/` only as supplied: never redrawn or recoloured.
- The current Report A (`reference/report-a-current/`) is the incumbent to improve on, not a constraint.
- The Excel template is no longer a requirement.
- caos-databricks's app is a different platform; don't copy its model screen.
