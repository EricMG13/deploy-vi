# Data for the mockups

All figures are real Caesars Entertainment (CZR) Q2 2026 data from public documents, each carrying its file, line and verbatim excerpt, or a deterministic calculation from them. No RBOT run has produced judgements on Caesars yet, so judgements are illustrative (labelled), and the Test CLO I portfolio is synthetic (labelled).

## Files

| File | What |
|---|---|
| `rbot-data-base.json` | The base set (built by `design/mockups/shared/build-data.py` from the CZR corpus). Keys: `meta`, `citations` (C1–C337, synthetic S1–S45), `calcs` (K1–K109), `gaps` (G1–G28), `figures` (every figure by name), `tables` (financials, balanceSheet, creditMetrics, capitalStructure, ebitdaAdjustments, liquidity, maturities, segments, trace, operatingModel), `charts` (ready chart specs), `modules`, `limitations`, `illustrative` (scores, recommendations, thesis, strengths, weaknesses, catalysts, key findings), `portfolio` (Test CLO I, synthetic), `counts` |
| `front-pages-data.json` | The Front Pages set (built by `design/mockups/front-pages/build-fp-data.py` from the base set plus `corpus-extract.json`): 34 more citations (C338–C371) from the credit agreement, 2032 indenture, 10-Q management discussion and the earnings release; 7 synthetic (S46–S52); 117 calculations (K110–K226); 13 gaps (G29–G41); `modules` (18 modules: plain name, reader question, status, reason, headline); `pathways` (navigation per Pathway); `blocks` (41 block tables); `charts` (12 chart specs); `fit` (Portfolio Fit per interfaces §7); `illustrative` (every judgement, flagged) |
| `corpus-extract.json` | The 39 supplementary citations with file, line and verbatim excerpt |

## Shapes

- **Datum**: `{ "v": "3.29", "prov": "cited" | "calculated" | "synthetic" | "illustrative" | "model" | "gap", "ref": "C12" | "K3" | "S4" | "G8", "reason"?: "…" }`. `v` is a string printed exactly as served (negatives in parentheses: `(35)`); `v: null` with `prov: "gap"` is an n/a with its reason.
- **Citation**: `{ id, key, label, period, value, unit, file, line, locator, excerpt }`. **Calculation**: `{ id, key, label, period, value, unit, formula, inputs: [ids], note }`. **Gap**: `{ id, field, reason }`.
- **Prose cell**: `{ "text": "… {K112|%} … [G8]", "refs": [...] }`: `{id|unit}` is a figure that should render as a clickable value; `[id]` is a chip.
- **Scale cell**: `{ "scale": "rec" | "val" | "score", "pos", "word" }` or `{ "scale": "word", "scaleName", "word", "steps", "pos", "illustrative" }`; **status cell**: `{ "status": "Headroom" }`.
- **Chart specs** follow the chart kit's shapes (`reference/report-a-current/runnable/shared/README.md`): `lineStrip`, `columns`, `waterfall`, `bullet`, `stackedColumns`, `rangeStrip`, `scatter`, `dumbbell`, `riskMatrix`.

## The figures that carry each story (quick reference)

| Story | Figures |
|---|---|
| Leverage and coverage | Total leverage 3.29x, net leverage 3.02x, senior secured leverage 2.64x (LTM Adjusted EBITDA US$3,592m, total debt US$11,807m); interest cover 1.57x including the GLPI/VICI lease obligations (US$13,157m, shown apart from debt), 4.63x on debt cash interest |
| The quarter | Q2 2026 net revenues US$2,993m (+3.0%), Adjusted EBITDA US$920m ((3.7)%), margin 30.7% ((2.1)pp); Las Vegas Adjusted EBITDA 410 vs 469, Regional 488 vs 439 with Caesars Windsor consolidated from 3 March 2026 |
| Liquidity | US$2,928m (cash 965, revolver net capacity 2,130); mandatory uses US$2,601m; 13.5 months of runway before operating cash flow (12 months from 30 June 2026, lease payments included); the CEI revolver matures 31 January 2028 |
| Maturities | 2026 rest 55; 2027 114; 2028 767; 2029 1,574; 2030 3,962; thereafter 5,335 (US$m); liquidity left before refinancing turns negative in 2028 (138) once the revolver lapses |
| Covenants | Total Leverage Ratio max 6.50x (headroom 3.48x on RBOT's basis); FCCR min 2.00x (headroom 2.63x); tested for the revolver and Term A only; Term B-1 is a Non-Covenant Facility; pari secured capacity to 4.50x ≈ US$6,696m; change of control put at 101% on the 2032 secured notes |
| Market | 6.50% secured 2032s at 93.28, 8.06% yield (B1/BB-); 6.00% unsecured 2032s at 84.94, 9.32% (Caa1/B-); 1.25pp pick-up; spreads n/a (G19); loan prices n/a (G18) |
| Merger | Fertitta take-private at about US$17.6bn including assumed debt of about US$11.9bn; new committed debt from ten banks of unstated size (G8); End Date 27 May 2027, extendable to 27 Nov 2027 |
| Distress (illustrative) | Gate Unclear; recovery at the merger value 100% for every class; at an illustrative 5.0x downside the unsecured notes recover 72.9% (fulcrum); at 4.0x stress the secured recover 94.2% |
| Portfolio Fit (synthetic) | Test CLO I, NAV US$630.9m, no existing Caesars exposure; proposed US$5.0m of the secured 2032s (0.7925% of NAV) Fits, max US$15.8m under C-01; loans and unrated notes Watch, max US$0.9m under the CCC bucket C-04 because no issue rating is in the sources |

## Real portfolio data (alternative to the synthetic Test CLO I)

On 6 October 2026 (D115) the CZR corpus admitted a real fund's public filings in place of the synthetic Test CLO I: the Federated Hermes Sustainable High Yield Bond Fund's N-PORT schedule of investments at 30 June 2026 and its prospectus. They are in `caos-databricks/qualification/czr-2026q2-full-credit-assessment/documents/`. The fund holds four Caesars positions (`FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt`, under "Gaming—2.6%", line 183):

| Line | Position | Principal (US$) | Value (US$) |
|---|---|---|---|
| 185 | 6.000% 10/15/2032 | 1,650,000 | 1,496,434 |
| 186 | 6.500% 2/15/2032 Sr. Secd. | 550,000 | 536,927 |
| 187 | 7.000% 2/15/2030 Sr. Secd. | 375,000 | 377,380 |
| 188 | 4.625% 10/15/2029 Sr. Unsecd. | 500,000 | 480,852 |

Net assets US$491,554,960 (line 527); the fund's 80% policy is in `FHSUHY_Prospectus_and_SAI_2026-05-26.txt` line 2624. The real documents carry no single-name limit, compliance monitor or proposed position, so Portfolio Fit arithmetic in this pack still uses Test CLO I (synthetic). A Portfolio Decision mock can show this fund as a real existing holder (an Indexed HY-style book) alongside it; no Fit figures for it are computed here.

## Real analysis outputs

`caos-runs/` holds the accepted module outputs of live CAOS runs on the same CZR Source Pack (2–15 October 2026). Read `caos-runs/README.md`: they are real but cautious (no Recommendation, distress gate Not Applicable), and they differ from the illustrative layer above.

## Known issues with this data

- The Front Pages set's Portfolio Fit (`front-pages-data.json → fit`) supersedes the base set's illustrative `portfolio.fit`, which misread the C-01 headroom as Caesars' own (it belongs to the largest existing issuer, Asurion).
- Recommendation, Valuation, Credit Score, Direction, Outlook and every analyst sentence are illustrative placeholders for design, not a view on Caesars.
