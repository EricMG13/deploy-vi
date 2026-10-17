# Deploy VI

Leveraged-finance credit research run by RBOT inside a work coding assistant: an analyst supplies an issuer's documents plus market and portfolio context, and receives governed analysis and a published report.

## Language

### System

**RBOT**:
Research BOT: the single entry point an analyst invokes to run Deploy VI end to end.
_Avoid_: Orchestrator, CP-OS, CP-X, credit OS

**Module**:
One bounded analytical job inside RBOT (for example source readiness or relative value) that consumes and produces Handoffs.
_Avoid_: Agent, skill, CP (on its own)

**Handoff**:
The Markdown file a Module produces as its sole analytical output and that downstream Modules consume.
_Avoid_: Artifact, payload, output

**Pathway**:
A named, ordered set of Modules that answers one analytical question (for example Relative Value or Covenant & Refinancing), chosen by the analyst at the start of a run.
_Avoid_: Route, profile, selection

**cp-start**:
The pre-approval step of every run: classify the Source Pack, pre-fill the Run Brief, grade every Pathway as Available, With limitations or Blocked, and obtain Approval. It absorbs CP-0: its source-readiness Handoff is the one every later Module consumes. It performs no credit analysis.
_Avoid_: CP-0 (as entry), readiness check, intake

**Approval**:
The analyst's sign-off at the end of cp-start on the Run Brief (including whether the run is Primary), one Pathway, its Depth and every known limitation. After Approval the run completes without further questions; anything unforeseen is recorded in the Report.
_Avoid_: Gate, confirmation, sign-off (loosely)

**Depth**:
Whether a Pathway runs Full or as a Quick screen; Quick screen output is screening-only and can later be upgraded to Full.
_Avoid_: LITE, profile

**Deep Research**:
The Module that researches the issuer's market, competitors, regulation, sector, outlook and risks as context for the foundation and fundamental Modules; the only Module that may draw on public sources outside the Source Pack.
_Avoid_: CP-DR (in prose), web research

**Prior Case**:
An earlier RBOT Report on the same issuer, supplied in the Source Pack with its sources, against which a run reports what has changed.
_Avoid_: Previous memo, history, decision ledger

**Model**:
The issuer's historical and projected financials and credit metrics, computed deterministically from accepted Handoffs, where every figure traces to a citation or a stated calculation. It assists the analyst's own spreadsheet model; it does not replace it.
_Avoid_: CP-MODEL, workbook, spread

**PF-LTM**:
The Model column that adds the pro forma adjustments sourced in the pack (acquisitions, disposals, refinancings, new debt) to the LTM; PF interest, Structuring EBITDA and SSIM EBITDA are read from it.
_Avoid_: Pro forma (alone), PF column, run-rate

**Report**:
The single published output of a run: an interactive HTML document in the house design, saved alongside its Markdown source, opening on its Pathway's Front Page.
_Avoid_: Memo, deliverable, CP-MEMO, dashboard

**Front Page**:
The first page of a Report, designed for its Pathway's purpose; the Pathway's Modules are exactly those needed to fill it. Full Credit Assessment's Front Page, at either Depth, is the Credit Snapshot; specialised Pathways (for example Earnings Update) each have their own.
_Avoid_: Cover, summary, dashboard

### Credit Snapshot

**Credit Snapshot**:
The Front Page of Full Credit Assessment in the State Street Investment Management house format: company profile, recommendation, Transaction Summary (Primary only), capital structure, EBITDA adjustments, thesis, strengths and weaknesses, financials, credit metrics and loan and high-yield relative value, each field composed from Module outputs.
_Avoid_: Tear sheet, summary page, one-pager

**Credit Score**:
The fundamentals grade on a 1–5 scale: Strong, Good, Fair, Weak, Stressed.
_Avoid_: Credit rating, credit tier

**Valuation**:
The pricing grade on a 1–5 scale (V1–V5): Very attractive, Attractive, Fair, Unattractive, Very unattractive.
_Avoid_: RV label, value score

**Recommendation**:
The combined call from Credit Score and Valuation on a 1–5 scale (Strong OW, Modest OW, MW, Modest UW, Strong UW), or Avoid or N/A; given per Strategy and per instrument.
_Avoid_: Action bias, rating, final ranking

**Strategy**:
One of the investment strategies a Recommendation is stated for: CLO, Indexed Loans or Indexed HY. Every run states all three (N/A where the issuer has no eligible instrument); each portfolio in the Portfolio Context belongs to one Strategy, and its Portfolio Fit can cap that Strategy's Recommendation for that portfolio.
_Avoid_: Mandate, fund, book

**Credit Direction**:
The fundamental trend: Improving, Stable or Deteriorating.
_Avoid_: Outlook (reserved for agencies and sector)

**Sector Outlook**:
The sector's direction: Positive, Neutral or Negative.
_Avoid_: Industry view

**Reported EBITDA**:
EBITDA as the issuer reports it, before any add-backs.
_Avoid_: Adjusted EBITDA, company EBITDA

**Structuring EBITDA**:
Reported EBITDA plus every add-back the issuer claims, on the PF-LTM; the marketed figure a deal is structured on.
_Avoid_: Marketed EBITDA, PF adjusted EBITDA, covenant EBITDA

**SSIM EBITDA**:
Structuring EBITDA less Unrealized Add-backs, on the PF-LTM: the house view of earnings that leverage is judged on.
_Avoid_: Adjusted EBITDA, house EBITDA

**Unrealized Add-back**:
An add-back for a benefit not yet achieved in the period, such as run-rate synergies or planned cost savings.
_Avoid_: Pro forma adjustment (that is a perimeter change), one-off

**CR Score**:
The Covenant Review composite covenant-protection score for an instrument, 1 (strongest lender protection) to 5 (weakest); an external input, not computed by RBOT.
_Avoid_: Covenant score, covenant quality

### Inputs

**Source Pack**:
Everything the analyst attaches for one run, in any folder layout; RBOT classifies each file into Issuer Sources, Market Context or Portfolio Context.
_Avoid_: Upload, data room, folder

**Issuer Sources**:
Documents by or about the issuer: filings, financial statements, credit agreements, indentures, offering memoranda, lender presentations, rating reports.
_Avoid_: Source documents (as the whole pack)

**Market Context**:
Dated market files not authored by the issuer, such as the Sector RV sheet and Bloomberg pricing exports.
_Avoid_: Market data (as a vague catch-all)

**Portfolio Context**:
Current positions and constraints for one or more portfolios the analysis may be sized against.
_Avoid_: Book, holdings

**Portfolio Fit**:
For one portfolio in the Portfolio Context: current exposure, headroom against each mandate limit, the largest size that keeps every hard limit, and a verdict of Fits, Watch or Breaches.
_Avoid_: Sizing (alone), mandate check

**Run Brief**:
The analyst-confirmed facts that frame a run and that sources cannot settle on their own: issuer, as-of date, objective, analyst, whether the run is Primary, and the Transaction Summary when it is. Pre-filled from the Source Pack with citations, then confirmed or edited by the analyst; an unknown field is an explicit gap. Where a dated source in the pack states a different value, the source governs and the analyst's value is kept only as context; a value with no source behind it is used as analyst-asserted.
_Avoid_: Issuer context, user context, qualifiers

### Primary transactions

**Primary**:
A run on a primary market transaction (a new issue, including LBO, acquisition, refinancing, amend-and-extend or repricing debt), marked by the analyst at Approval. Its only effect is that the Credit Snapshot shows the Transaction Summary; every Module runs the same way either way.
_Avoid_: Situation, Secondary, Event, deal type

**Transaction Summary**:
The Credit Snapshot block for a Primary run: per new tranche, borrower, Bloomberg ID, instrument, debt type, use of proceeds, size, Price Talk, OID, maturity, expected ratings, CR Score and commitment date.
_Avoid_: New-issue terms, deal terms, term sheet

**Price Talk**:
The arranger's indicated pricing for a new tranche at a stated point in marketing (initial talk, revised guidance or final).
_Avoid_: IPT (as the only stage), guidance

**Market Levels**:
Observed, dated prices, spreads or yields for securities that already trade.
_Avoid_: Marks, quotes

**Sector RV Workbook**:
The maintained per-sector loan relative-value workbook (Bloomberg-backed peer rows, index statistics and sector rating averages) supplied as Market Context.
_Avoid_: RV sheet, RV table, comps sheet

**Image-Read Value**:
A figure transcribed from a screenshot or scanned page rather than read from a data file; always shown with that label and never used in a calculation.
_Avoid_: OCR value, estimate
