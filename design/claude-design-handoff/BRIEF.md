# Design brief: the RBOT Report application

Owner: Eric Guei, leveraged-finance credit research. Date: 17 October 2026. Private: this pack and its outputs stay in the owner's private Claude Design project.

## 1. What you are designing

RBOT (Research BOT) is a GitHub Copilot skill. An analyst gives it a Source Pack for one issuer: filings and legal documents, market levels, and optionally portfolio positions and limits. RBOT runs a governed chain of analysis modules and produces **one Report per run**: a self-contained HTML application, opened from disk and shared inside the team.

Every run follows one of six **Pathways**, and each Pathway opens on its own **Front Page**, a summary screen built for that Pathway's question:

| Front Page | The reader's question | Content doc |
|---|---|---|
| Credit Snapshot (Full Credit Assessment) | Should we own this issuer, in which instrument, and why? | `content/01-credit-snapshot.md` |
| Earnings Update | What did the period change, and does the credit view move? | `content/02-earnings-update.md` |
| Relative Value | Which instrument is best compensated for its risk, and at what level? | `content/03-relative-value.md` |
| Covenant & Refinancing | Which provisions protect creditors, and can the issuer refinance? | `content/04-covenant-refinancing.md` |
| Distressed & Restructuring | Is the distress gate met; which path and fulcrum; what recoveries? | `content/05-distressed-restructuring.md` |
| Portfolio Decision | Should each portfolio own it, how much, and which instrument? | `content/06-portfolio-decision.md` |

Behind every Front Page sits the same application shell: navigation to each analysis module's view, the Model, Portfolio Fit, Evidence and Limitations (`content/00-app-shell.md`). The **Model** is a full financial model (RBOT computes it with a port of caos-databricks's credit-model maths), read in its own view and designed for this offline Report, not copied from caos's web workbench (`content/07-model.md`).

## 2. Who reads it, and where

- **Portfolio managers** (CLO, Indexed Loans, Indexed HY strategies) decide whether and how much to own. Success: within a minute they can state the recommendation, the main risk and the valuation view.
- **Credit research analysts** check, challenge and extend the analysis. Success: any figure traced to its source excerpt in two clicks.
- Desktop browsers on wide work monitors; laptops (1280×800) are the minimum. Office lighting, long reading sessions, many Reports open side by side. Print/PDF is secondary. Phone is out of scope.

## 3. The ask

**Phase 1: three design directions.** Three genuinely different directions for a **modern, clean application**. They should differ in layout model and navigation, not only in colour and type. Each direction shows, at 1440×900 with real data:
1. the Credit Snapshot Front Page (first viewport, then the full scroll);
2. one denser Front Page: Covenant & Refinancing (covenant bullets, liquidity bridge, funding gap, red flags) or Distressed & Restructuring (gate, recovery waterfall, fulcrum);
3. one module view (Earnings delta CP-1B or Covenants and legal CP-4), with the source popover open on a cited figure;
4. the Model view's first viewport: the period grid, band navigation and the chart strip (`content/07-model.md`);
5. how navigation holds 14 to 17 modules (the Distressed and full-scope Full Credit Assessment lists).

For each direction state its thesis in a sentence, its type and colour system, its component language (tables, charts, call, status, provenance marks) and its honest risk.

**Phase 2, after the owner picks one:** a full interactive mock of all six Front Pages, the shell, every module view's anatomy, Model, Portfolio Fit, Evidence, Limitations, popovers, search, collapsed and expanded states, and the n/a, not-run and absent states.

## 4. Look and feel (owner, 17 October 2026)

- **Modern, clean, application-like.** It should feel like a well-made analytics product, not a printed committee paper or a spreadsheet.
- **No Excel requirement any more.** The Credit Snapshot no longer has to resemble the house Excel template; keep its content (`content/01`), not its form. RBOT still produces a full financial **model** (no Excel file): its home is the Model view, designed for RBOT's readers and platform rather than copied from caos-databricks's app.
- **Report A is in scope for the redesign.** The current mockup (`reference/report-a-current/`) and its design system (`DESIGN-report-a.md`) are the incumbent to improve on, not a constraint. What worked there: the call first, density that respects expert readers, provenance in the figure, every block linking to its module, honest gaps.
- Earlier owner rejections (2026-10-11), kept as context; the owner may relax them in this round: a dashboard of KPI tiles and cards; tone-coloured scales; citations as margin notes; numbered sections in place of view codes. The rejected alternatives B (verdict rail) and C (period spine) are in `reference/rejected-directions/`.

## 5. Brand

State Street Investment Management. Logo files in `brand/` (horizontal white, stacked black, horizontal blue-on-black, white-on-blue tile; see `brand/README.md`): use only these, never redrawn or recoloured. The house pair is deep navy `#000533` and electric blue `#0017E5` (the logo field `#001AFF`). Everything else (palette roles, type, density, motion) is open. Fonts must be embeddable in an offline file (licence permitting).

## 6. Non-negotiables (product truth)

Read `content/provenance-and-states.md` in full. In short:
1. **The call first**: each Front Page's verdict, key findings and charts visible without scrolling or clicking.
2. **Depth on demand**: every section expands; every figure opens to its source.
3. **Provenance visible**: cited, calculated, model-written, illustrative and synthetic content never look alike, and never by colour alone.
4. **Honest gaps**: a missing value shows as missing with its reason, never as zero or a guess.
5. **Scales are words**: the fixed house vocabularies, not tone-coloured; colour is for status (module status, Portfolio Fit, covenant tests).
6. **Every chart** has a table twin, a summary, a source line and provenance in its marks; a chart the data cannot draw shows an n/a frame.
7. **Accessible**: WCAG 2.2 AA, keyboard reachable charts and figures, 24px targets.
8. **Buildable**: one offline HTML file rendered by a Python template from data; components must take variable rows, lengths and presence.

## 7. Data you must use

Real Caesars Entertainment (CZR) Q2 2026 figures from its public filings, FINRA TRACE pages, the credit agreement, the 2032 notes indenture, the merger documents and two peers' releases (MGM, PENN). Every figure carries its file, line and verbatim excerpt (`data/`). No RBOT run has produced judgements on Caesars yet, so every score, recommendation, valuation, thesis, gate status and severity is **illustrative** and must be labelled so; the Test CLO I portfolio is **synthetic** and labelled so. Never invent a figure: use the data, or show n/a with its reason. Read `data/README.md` first.

Real analysis text also exists: live CAOS runs (RBOT's methodology source) on the same Caesars pack produced accepted module outputs, in `data/caos-runs/`. They are cautious: every module With limitations, confidence about 40–60 of 100, no Recommendation or Valuation, relative value "Unclear", distress gate "Not Applicable". Read `data/caos-runs/README.md`: it says where they conflict with the illustrative layer and asks for both states to be designed.

## 8. What is in this pack

See `README.md`.
