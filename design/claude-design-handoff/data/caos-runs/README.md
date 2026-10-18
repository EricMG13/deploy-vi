# Real analysis outputs: CAOS runs on Caesars (CZR, Q2 2026)

RBOT's methodology is ported from CAOS (caos-databricks), whose modules ran live on the same CZR Source Pack between 2 and 15 October 2026. These folders hold the **accepted module outputs** (canonical handoff Markdown, plus each one's citations as file line text) of the most complete run per Pathway, copied from `caos-databricks/.dev-data/qualification-blobs`. They are real model-written analysis: use them for findings, headlines, module views and judgement wording in place of illustrative placeholders wherever a run produced one.

| Folder | CAOS run | Modules | Feeds |
|---|---|---|---|
| `full-credit-assessment-2026-10-06/` | `COS-20261006T152956Z-6f30c70b…`, FULL_CREDIT_32 | 17: CP-0, 1, 1A, 1B, 1C, 1D, 2, 2A, 2D, 2E, 2G, 2H, 3, 3C, 3D, 4, 4C (stopped before CP-5 and CP-6) | Credit Snapshot; every module view; covenant, liquidity, ratings, market and recovery content for the other pages |
| `earnings-update-2026-10-05/` | `COS-20261005T055642Z-dff6ac04…` | CP-0, 1, 1B, 2, 5 | Earnings Update |
| `covenant-refinancing-2026-10-05/` | `COS-20261005T071138Z-264a667c…` | CP-0, 1, 2, 2D, 3C, 4, 5 | Covenant & Refinancing |
| `relative-value-2026-10-12/` | `COS-20261012T160551Z-a27732bd…` | CP-0, 1, 1C, 2, 2A, 2G, 3, 3D, 4 | Relative Value |
| `lite-screen-with-recovery-2026-10-05/` | `COS-20261005T115024Z-471a3043…`, LITE | CP-0, 1A, 1C, 2A, 2H, 3C, 4C, L10 | Distressed & Restructuring (CP-4C, CP-2H) |
| `lite-portfolio-screen-2026-10-06/` | `COS-20261006T071305Z-0e81c3d0…`, LITE | CP-0, L10 | Portfolio Decision (screen only) |

Each folder's `INDEX.md` lists every module's QA status, confidence and limitation flags.

## What the real runs concluded (read before mocking judgements)

- **Every module is "Restricted" (With limitations), confidence mostly 37–59 of 100 (the evidence check CP-5 as low as 16), committee status "Requires More Work".** None is committee-ready. This is the honest state of an analysis on a public-only Source Pack.
- **No Recommendation, Valuation or position size exists.** CP-6 (challenge and decision) never ran. The Relative Value run's CP-3 says **"Requires More Work" for both priced 2032 bonds; relative value "Unclear"; fundamental score "Not Scorable"** (no factor weights supplied). The Full Credit Assessment's CP-3 (confidence 44) marks no security Preferred.
- **Credit synthesis (CP-2):** "adequate but cyclical business profile … constrained by declining Adjusted EBITDA despite revenue growth", liquidity "Average" at US$2.928bn.
- **Covenants (CP-4):** overall protection score 4 (negative): debt and lien capacity, restricted payment and investment leakage, and no maintenance test on the notes are the most creditor-adverse areas.
- **Distress (CP-4C): "Not Applicable": no named distress trigger**; covenant compliance is reported at 30 June 2026. No paths, valuation, waterfall or fulcrum were produced.
- **Portfolio screen (CP-L10):** overall "MIXED", Full upgrade required.

## How this differs from the illustrative layer in the JSON

`front-pages-data.json` and `rbot-data-base.json` carry a complete, consistent set of **illustrative** judgements (e.g. CLO MW, Indexed HY Modest OW, Valuation V2, Credit Score 3 Fair, distress gate Unclear with an illustrative recovery waterfall) so that every block of every Front Page can be drawn. The real runs above are less complete and more cautious. Two choices for the mocks, for the owner to make:

1. **Real where it exists:** use the CAOS wording and statuses (Requires More Work, Unclear, Not Applicable), and show the blocks the real runs could not fill as their honest empty states. This is the truest picture of what RBOT will produce today.
2. **Illustrative to show the full page:** use the illustrative layer, labelled ILLUSTRATIVE, so every block has content.

The one direct conflict: the illustrative distress gate is **Unclear** (chosen on 17 October so the Distressed page could show its recovery waterfall), while the real CP-4C says **Not Applicable**. A real run would therefore show the Distressed page with its EV, recovery and fulcrum block replaced by the condition line "not shown: distress gate not met". Design both states.

## Caveats

- These runs used CAOS's methodology (r14), not RBOT's port; section names, register ids (T2.7 etc.) and citation markers ([C12]) follow CAOS conventions. Citation markers resolve through each `*.citations.json` (page and line text; `document_sha256` identifies the corpus file).
- These runs may predate the 6 October corpus change (D115) that replaced the synthetic Test CLO I with a real fund; figures from the CZR filings are unaffected.
- The Spirit Airlines distressed sets were never run; there is no real distressed issuer output.
