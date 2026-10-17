# Direction decision: C, Workbench (owner, 17 October 2026)

Claude Design project: "RBOT Report application design", file `Direction C - Workbench.dc.html`. Directions A (Rail and grid) and B (Reading page) were not chosen.

## Direction contract

- **THESIS.** An analyst's workbench: an icon rail for destinations, a navigator that lists and filters the modules, a dense panelled canvas under a navy verdict bar, and a persistent inspector where every figure's source lands. A figure's source is one click and zero popovers away. It refuses the long document where the source opens over the analysis.
- **OWN-WORLD.**
  - Colour: navy `#000533` rail and verdict bar; electric blue `#0017E5` for selection, links and the cited glyph; ground `#EEF0F5` with white panels.
  - Signal colours: positive forest `#0E7A46`, caution amber `#8A5300`, negative brick `#B3261E`; chart comparison `#C4410C`.
  - Type: Red Hat Display for titles and panel heads, Red Hat Text for body, Red Hat Mono for figures, codes and formulas (all OFL, embeddable).
  - Components: square-cornered panels with owner code and state word; 12px mono tables; CSS headroom bars and meters; SVG charts from the kit.
- **STORY.** A PM reads the verdict bar (the call per Strategy, Valuation, Credit Score, Direction, main risk, Fit, instrument) in the first viewport. An analyst clicks any figure and reads its passport, table twin and the page's gaps in the inspector without losing their place.
- **FIRST VIEWPORT (1440×900).**
  - Rail, 56px.
  - Navigator: modules with status and filters, then the page's sections.
  - Canvas: the navy verdict bar with the six position tiles and three call lines, then key findings beside company and operating model, then the four-chart strip.
  - Inspector: about 260px on the right.
  - At 1280×800 the navigator starts closed; the rail and the module switcher (`/`) stay, and the inspector is a 36px strip that opens as an overlay on the canvas (no reflow) when a figure is selected.
- **FORM.** Workbench; three Claude Design directions, the owner's pick. No impeccable concept seed was run: the directions were generated in Claude Design from this pack.
- **FINISH.** Unreviewed and undocumented is unfinished. This build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Refinements requested for Step 2

1. The inspector's formula "Inputs" must show each input's id and label, not bare glyphs.
2. Make provenance marks quieter by default in dense tables (a small muted mark), stronger on row hover or focus, and full in the inspector. Test both densities on the Capital structure and Model tables.
3. Navigator family markers must not use hue: use icons or a neutral tint, so colour stays a signal.
4. Chart gap labels sit on their axis position, not floating above the plot.
5. The honest state (the real run produced no Recommendation) is a designed state of the verdict bar, not a design tweak. Owner ruling (C2): a switch in the bar's header, state in the URL, every judgement tile honest, the fixture's own verdicts below the bar labelled and dimmed.
6. Specify 1280×800 behaviour, keyboard order across the rail, navigator, canvas and inspector, and print (the inspector does not print; passports print as endnotes).
