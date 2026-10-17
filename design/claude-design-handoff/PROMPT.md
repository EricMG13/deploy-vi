# Paste this into Claude Design (with the whole pack attached)

I'm designing the Report application for RBOT, a credit-research tool used by leveraged-finance portfolio managers and credit analysts. The attached pack has everything: start with `README.md`, then `BRIEF.md`.

**What I need first: three design directions** for a modern, clean, application-like Report. They should differ in layout model and navigation, not just colour and type. Each direction should show, at 1440×900 with the real Caesars data in `data/`:

1. the Credit Snapshot Front Page (first viewport, then the full scroll);
2. one denser Front Page: Covenant & Refinancing or Distressed & Restructuring;
3. one module view (Earnings delta CP-1B or Covenants and legal CP-4) with the source popover open on a cited figure;
4. the Model view's first viewport;
5. navigation holding 14 to 17 modules.

For each direction, give me its thesis in one sentence, its type and colour system, its component language (tables, charts, the call, status, provenance marks) and its honest risk. I'll pick one; then we build the full interactive mock of all six Front Pages, the shell, module views, Model, Portfolio Fit, Evidence and Limitations.

**Hold these product rules** (`content/provenance-and-states.md`):
- the call first;
- every figure opens to its source;
- cited, calculated, model-written, illustrative and synthetic content never look alike, and not by colour alone;
- a missing value is shown as n/a with its reason, never zero;
- scales are words, not tone colours; colour is for status;
- every chart has a table twin;
- WCAG 2.2 AA;
- one offline HTML file rendered from data.

**Data:**
- Use only the figures in `data/`.
- Label every judgement Illustrative and the Test CLO I portfolio Synthetic.
- Where the real CAOS outputs in `data/caos-runs/` give a judgement, prefer their wording. Design both states where they conflict: distress gate Not Applicable versus the illustrative Unclear.

**Brand:**
- State Street Investment Management logos in `brand/`: use as supplied, never redrawn or recoloured.
- The house pair is navy #000533 and electric blue #0017E5.
- Everything else is open, including a full redesign of the current Report A (`reference/report-a-current/`).
- No Excel template requirement.
