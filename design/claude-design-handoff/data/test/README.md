# Test runs: every module, table and chart populated

Eight complete Report runs in the Report's own data shape, `rbot-run/1` (the JSON the renderer embeds in every Report; interfaces spec §11.3). Use them to render every view: each Pathway's Front Page, every module view, the Model, Portfolio Fit, Evidence and Limitations. Every chart in the chart map has data in at least one run.

Built by `design/mockups/fixtures/build-fixtures.py` (repo), which checks every run: every table and column, every citation, every derived figure recomputed, every chart drawable. All eight pass.

## The runs

| File | Pathway, depth | Issuer | Steps | Charts with data | Synthetic citations | States it shows |
|---|---|---|---|---|---|---|
| `czr-full-credit-assessment.run.json` | Full Credit Assessment, Full, Primary | Caesars | 23 run, What changed not run | 32 | 7% | Merger financing as three new tranches with price talk; PF-LTM; Base and Downside projections; Deep Research answered; Test CLO I Fit; real distress gate Not met |
| `czr-full-credit-assessment-quick.run.json` | Full Credit Assessment, Quick, Primary | Caesars | 10 | 12 | 8% | Quick-depth screen (CP-L10), decision at Screening basis |
| `czr-earnings-update.run.json` | Earnings Update, Full | Caesars | 10 | 10 | 2% | **Prior Case**: a prior Report of 5 Aug 2026, what changed, thesis review, recommendation change |
| `czr-relative-value.run.json` | Relative Value, Full, Primary | Caesars | 17 run, 1 not run | 21 | 8% | Loan marks, spread curve, talk valuation, peer ranges with three anonymised peers |
| `czr-relative-value-blocked.run.json` | Relative Value, Full, Primary | Caesars | 16 run, CP-3D **Blocked** | 21 | 8% | A Blocked module: tables kept, critical cells "—", two charts as deliberate n/a frames |
| `czr-covenant-refinancing.run.json` | Covenant & Refinancing, Full, Primary | Caesars | 11 run, 1 not run | 14 | 4% | Real covenant extraction plus basket usage; 13.5-month runway; funding gap |
| `czr-portfolio-decision.run.json` | Portfolio Decision, Full, Primary | Caesars | 14 run, 1 not run | 17 | 8% | Two portfolios: Test CLO I and Test Indexed HY I; one instrument **Breaches** |
| `larchmere-distressed-restructuring.run.json` | Distressed & Restructuring, Full, Primary | **Larchmere Leisure Group (fictional)** | 18 run, 2 not run, CP-2H **Blocked** | 27 | 100% | Distress gate **Met**; covenant **Breached** and minimum liquidity **Tight**; 6.5-month runway; rescue new-money tranche; EV scenarios, recovery waterfalls, fulcrum moving by scenario; every instrument **Breaches** its CLO limit |

## Reading a run

- `run_brief.tables`: the Run Brief (issuer, Pathway, Primary tranches, portfolios, research questions, Prior Case).
- `steps`: each plan step `accepted`, `skipped` (with its reason) or `blocked`.
- `handoffs.<module>`: `qa_status`, `front_matter`, `analysis_md` (cited prose), `tables` (every table the interfaces spec lists for the module, as columns and rows of strings), `gaps_md`, `citations` (`id`, `source`, `locator`, `excerpt`, `anchored`, `synthetic`).
- `model`: the full financial model (`rbot-model/1`): columns (history, PF-LTM, projected Base and Downside), twelve bands of lines, every cell with value or reason, basis and sources; house view; capital structure; maturity wall.
- `fit`: Portfolio Fit per portfolio, computed per interfaces §7.
- `charts`: every chart with `chart_id`, `where` (`front_page:<block>`, `analysis:CP-x` or `model_tab`), `kind` and the `data` to draw.
- `front_page_blocks`: each Front Page block, shown or replaced by its condition line.
- `limitations`, `prior_case`, and `fixture` (notes, chart ids with data, declared n/a charts).

## Real, synthetic, illustrative

- **Real**: every Caesars figure with a real citation (`synthetic: false`): filings, credit agreement, indenture, TRACE, peer releases, and real CAOS module findings where `analysis_md` cites them.
- **Synthetic**: values the sources cannot supply, each citing a row whose `source` reads "TEST DATA — invented for design, not a fact about …" with a one-sentence rationale. Render the synthetic mark wherever one appears. Examples: the merger tranches, loan marks, agency thresholds, the rate deck and projections, the anonymised peers, the prior Report, the second portfolio. Larchmere is entirely synthetic and fictional.
- **Illustrative**: every judgement (Recommendation, Valuation, Credit Score, gate statuses, severities, preferences) is the module's view in a design fixture, not a view on any issuer. The real CAOS runs (`../caos-runs/`) reached none of these decisions.

## Notes

- The Caesars liquidity runway is 13.5 months: 12 months from 30 June 2026, with lease payments counted as mandatory uses. The Front Pages data uses the same basis.
- Caesars' real distress gate is Not met, so the recovery and value-allocation charts are drawn in the Larchmere run.
- Expected ratings on new tranches count as Unrated in Portfolio Fit (interfaces §7), so the three Caesars tranches show Watch in Test CLO I.
- Only instruments with a level carry a per-instrument Recommendation; the revolver, Term Loan A and the unquoted notes have none, and CP-6's gaps say so.
