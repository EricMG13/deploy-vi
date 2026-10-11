# Deploy VI — RBOT design (grilled 2026-10-11)

Owner decisions from one grilling session. Vocabulary is in [`CONTEXT.md`](../../../CONTEXT.md); hard-to-reverse choices are ADRs [0001](../../adr/0001-vscode-copilot-personal-skill.md)–[0004](../../adr/0004-source-pack-only-except-deep-research.md). Status: **design, awaiting owner review** (revised 2026-10-11: Situation and New Issue Pricing removed; PF figures tied to the PF-LTM; per-Pathway Front Pages; methodology rewritten per increment). No build plan until approved.

**Framing.** RBOT turns an analyst's Source Pack into a governed credit view and a Credit Snapshot–led HTML Report inside GitHub Copilot. The pre-approval step exists so the analyst knows every limitation before the run starts; after Approval the run completes unattended.

## 1. Decisions

| # | Decision |
|---|---|
| D1 | **Host:** GitHub Copilot, VS Code Agent mode, installed as a personal skill at `~/.copilot/skills/rbot/` (ADR 0001). Analysts open the issuer folder as the workspace. |
| D2 | **Python with pip packages** runs in the VS Code terminal. Deterministic figures, document preparation and validation are script-owned. |
| D3 | **One discoverable skill.** Only `rbot/SKILL.md` is a skill; modules are internal files each run in its own subagent with only its module file and declared input Handoffs (ADR 0002). |
| D4 | **Methodology rewritten per increment** (ADR 0003). The caos-databricks Deploy V fork at r14 (`a14f9051`) is read-only reference, never shipped. Each module is rewritten in the increment that first needs it: a stage contract (Inputs / Process / Outputs) keeping Deploy V's analytical method; outputs only what a downstream module, the Model or a Front Page reads; house scales natively; prose and validator generated from one contract; a measured size budget. |
| D5 | **Primary is a flag, not a mode.** The analyst marks a run Primary at Approval (pre-ticked when the pack holds new-tranche terms). Its only effect is that the Credit Snapshot shows the Transaction Summary; every module runs the same either way. Secondary and other cases carry no system meaning. |
| D6 | **Source Pack in any layout.** cp-start classifies each file as Issuer Sources, Market Context or Portfolio Context and the analyst confirms. |
| D7 | **Run Brief:** always issuer/borrower entity, as-of date, objective and analyst. A Primary run adds the Transaction Summary per new tranche: borrower, Bloomberg ID, instrument, debt type, use of proceeds (LBO, Acquisition, Refinancing, A&E, Repricing, Other), size, Price Talk and its stage, OID, maturity, expected ratings, CR Score and commitment date. Optional from the Snapshot template: Morningstar Issuer ID and SSIM EV multiple (unlisted issuers). Every field is pre-filled from the pack with a citation; a blank field is an explicit gap. |
| D8 | **Source wins.** A dated source in the pack beats a conflicting Run Brief value, and the analyst's value is kept as context. A value with no source is used as analyst-asserted. To correct stale talk, add a dated note to the pack. |
| D9 | **cp-start takes two turns.** Turn 1 shows the file classification and pre-filled Run Brief; the analyst confirms or edits. Turn 2 shows the graded Pathway menu with limitations; the analyst picks Pathway and Depth and confirms the Primary flag (= **Approval**). cp-start absorbs CP-0; its source-readiness Handoff is the run's CP-0 Handoff. |
| D10 | **Menu:** every Pathway is graded Available / With limitations / Blocked (caos R2), and none are hidden. A Blocked Pathway can still start after an explicit acknowledgement naming the blocking modules. |
| D11 | **One Pathway per run.** A second question is a new run. |
| D12 | **Depth:** Full or Quick screen (CP-L10) where a LITE route exists. Quick output is screening-only. |
| D13 | **No checkpoints after Approval.** An unforeseen block or validator failure marks that module and its dependants in the Report; the run continues. |
| D14 | **Source Pack only**, except Deep Research, which may fetch public sources into the run folder with URL and retrieval date (ADR 0004). Model memory is never evidence. |
| D15 | **Market Context formats:** xlsx/csv (cached Bloomberg values read without a terminal; `#N/A` and similar markers are missing values) plus screenshots and PDFs. A figure read from an image is an Image-Read Value: labelled, and never used in a calculation. |
| D16 | **Assets:** leveraged loans and HY bonds. Loans price on margin, floor and OID to a 3-year DM; bonds on coupon and price to YTW/STW with the call schedule. |
| D17 | **Portfolio Context = positions + limits** per portfolio. Each portfolio belongs to one Strategy. |
| D18 | **Recommendations:** RBOT fills Credit Score, Valuation, Credit Direction, Sector Outlook and Recommendation per Strategy (CLO, Indexed Loans, Indexed HY; N/A where ineligible) and per instrument. Portfolio Fit can cap a Strategy's Recommendation for that portfolio. Analyst overrides happen outside RBOT. |
| D19 | **House EBITDAs and PF interest live on the PF-LTM.** Structuring EBITDA = PF-LTM Reported EBITDA + every issuer add-back (caos adjusted EBITDA); SSIM EBITDA = the same less Unrealized Add-backs (caos `exclude_unrealised`). PF interest is the PF-LTM cash interest. Structuring Multiple and SSIM Multiple are PF total debt over each. Without PF adjustments in the pack the PF-LTM equals the LTM. |
| D20 | **Model:** caos's host-computed design (pure Decimal, property-tested, every cell traceable), shown as an interactive Model tab plus a values-only `model.xlsx`. |
| D21 | **No Primary-specific module.** A new tranche is one more instrument: CP-3 values it against comparables and the issuer's own levels at its Price Talk and OID, labelled as talk, never as a market level. Pro forma figures come only from sources via CP-1's PF register. |
| D22 | **Deep Research (redesigned CP-DR)** complements the foundation and fundamental modules with a case-relevant deep dive into market, competitors, regulation, sector, outlook and risks. It runs in every Full Pathway, after CP-1A and before CP-2. cp-start lists its questions, and the analyst can untick it at Approval. It is skipped at Quick depth. |
| D23 | **Prior Case (redesigned CP-8)** is an add-on to any Pathway, offered only when the pack contains an earlier RBOT Report (including one in the folder's `rbot-runs/`). It runs last and adds "What changed since ⟨date⟩". |
| D24 | **Dropped:** CP-MEMO (replaced by the Report); the Decision Ledger, Market Dislocation and Near-Term Liquidity Pathways (CP-2D and CP-3D still run inside others); the M365 launchers and saved-memory prompts. |
| D25 | **Report:** opens on its Pathway's Front Page, with drill-down behind it. Full Credit Assessment's Front Page is the Credit Snapshot; each specialised Pathway gets its own. For the Credit Snapshot, three mockups are built once during the build and the owner picks one as the fixed template. Branding comes from SSIM's public site. Mockups are local files only, never published. |
| D26 | **Models:** prompts stay model-neutral; release needs passing runs on a Claude and a GPT model in Copilot. |
| D27 | **Full scope** (owner, 2026-10-11, replacing the earlier v1 thin slice): every Pathway at its Depths, every module, Deep Research, Prior Case, projections and every Front Page, built in the order of the roadmap; cross-plan names and schemas are fixed in the interfaces spec (`2026-10-11-deploy-vi-interfaces.md`). |
| D28 | **Test regularly on the local issuer corpus** (owner, 2026-10-11): `TEST-Issuer Data` PDFs and the caos qualification packs are registered with hashes in `tests/corpus/corpus.json`; every task that reads documents, computes, grades, validates or renders adds deterministic corpus tests (`pytest -m corpus`, failing, never skipping, when a required file is missing); every plan ends with a corpus regression, including proxy runs and module A/B where it changes modules or Pathways. |
| D29 | **Charts at parity with caos-databricks** (owner, 2026-10-11): the Report draws every figure caos draws (the Model chart strip of net leverage, interest coverage and liquidity across historical, Base and Downside; CP-1 earnings and balance lines and cash-flow bridge; CP-1D EBITDA quality bridge; CP-1C peer ranges; CP-2D liquidity bridge; CP-4 covenant headroom bullets; CP-4C recovery waterfall and value allocation; adjusted-debt bridge, implied EV ranges and maturity walls; CP-2G forecast and credit-path lines; CP-2E tornadoes; CP-2H rating-trigger bullets; scores; dumbbell; CP-3/CP-3D spread curve; probability and impact matrix; audit counts), each Front Page carrying the charts that serve its purpose. Inline SVG in the self-contained HTML; provenance in the mark (script-computed solid, model-authored hatched or dashed); a missing value is an n/a gap with its reason; title, summary and table twin per chart; keyboard-reachable marks. Tables carry one figure per cell with explicit units (fixing caos N192), and r14's calculators run as scripts so those marks are host-verified (fixing caos N193). Chart map in the interfaces spec §11. |

## 2. Analyst experience

1. Open the issuer folder in VS Code (or attach a folder in chat), switch Chat to Agent mode and run `/rbot`. The Source Pack root is the attached folder, otherwise the workspace root.
2. **cp-start, turn 1.** RBOT inventories and prepares every file and shows a classification table (file → Issuer Sources / Market Context / Portfolio Context, flagging unreadable files and Image-Read Values). It also shows the pre-filled Run Brief, with each value's citation or "gap". The analyst confirms or edits.
3. **cp-start, turn 2.** RBOT grades every Pathway on the confirmed brief and shows:
   - the graded menu and the Primary flag (pre-ticked when the pack holds new-tranche terms);
   - each Pathway's limitations and the sources that would lift them;
   - Deep Research questions (Full depth);
   - the Prior Case offer, when one is detected.

   The analyst picks Pathway and Depth and confirms the flag, which is the Approval.
4. The run executes unattended: modules run in dependency order, one subagent each, with Markdown Handoffs, script-owned Model, Portfolio Fit and validators.
5. RBOT writes `report.md` and `report.html` and returns their links, the Recommendation line and the limitation count.

## 3. Package layout

```text
~/.copilot/skills/rbot/
  SKILL.md                    # orchestrator only: cp-start, Approval, dispatch, render. Short.
  catalog.json                # modules, edges, Pathways, Snapshot field owners
  canon.md                    # rewritten shared rules: evidence, citations, gaps, depth, house scales
  modules/<id>/MODULE.md      # rewritten module prompt, generated from its contract (not named SKILL.md, so Copilot never discovers it)
  modules/<id>/contract.json  # inputs, outputs, tagged tables, Front Page fields owned; the validator reads this
  modules/<id>/scripts/       # module-owned deterministic calculations
  scripts/rbot.py             # CLI: inventory, prepare, brief, grade, plan, state, model, fit, render
  report/                     # chosen template, tokens, renderer assets (inline, no CDN)
```

`install.sh` / `install.ps1` copy `rbot/` from the Deploy VI repo into `~/.copilot/skills/`. The repo also holds tests, golden packs, the gates and `reference/deploy-v-r14/` (the fork, read-only, never installed). Analyst data never enters the repo.

**Run folder:** `<pack>/rbot-runs/<YYYYMMDD>-<issuer>-<pathway>/` contains `run-state.json`, `run-brief.md`, `prepared/` (page-anchored text), `fetched/` (Deep Research), `handoffs/<id>.md`, `model.json`, `model.xlsx`, `report.md` and `report.html`. Source files are never modified. Running `/rbot` again in a folder with an unfinished run resumes after the last accepted Handoff, with no re-approval.

## 4. Modules and Pathways

**Every Pathway has its own Front Page, and its modules are exactly those that fill it.** Full Credit Assessment (Full and Quick) opens on the Credit Snapshot (§5). Earnings Update and the other specialised Pathways each get a Front Page aligned with their purpose, designed in their own increment.

Each Pathway's ordered module list, per Depth, is fixed in the interfaces spec §5 and checked by `rbot check` (producers before consumers; every Front Page table owned exactly once).

Deterministic steps the orchestrator runs between modules:
- **Model** after CP-1D;
- **Portfolio Fit** arithmetic inside CP-3's portfolio phase;
- the **validators** after every module.

No Pathway depends on whether the run is Primary.

**A new tranche is one more instrument.** CP-3 gains one rule, keyed on data rather than on the flag: an instrument with Price Talk and no market level is valued at its talk (low, mid and high, with OID) against comparables and the issuer's own trading levels, and the level is labelled talk, never a market level. Without it CP-3's maintained protocol would grade such a tranche "Unclear".

## 5. Credit Snapshot field owners (Full Credit Assessment)

Each field has exactly one owner, written in a tagged `snapshot.*` table. The renderer composes and never analyses (caos D123).

| Snapshot block | Owner |
|---|---|
| Company profile: sector/country, shareholders, management, Corp ratings and outlook (M/S/F), Sponsor Quality, business description | CP-1A |
| Sector Outlook | as fixed in the interfaces spec §4 (Deep Research where it runs) |
| Credit Score, Credit Direction, strengths, weaknesses | CP-2 |
| Historical performance | CP-1B |
| EBITDA adjustments (Reported → add-backs → Structuring → − unrealized → SSIM, on the PF-LTM) | CP-1/CP-1D classify each add-back; Model computes |
| Transaction Summary (Primary flag only) | Run Brief, each field cited from the pack where it appears there |
| Capital structure (facility, ratings, spread/coupon, CCY, maturity, bid/ask, outstanding, multiples, % EV) and PF interest | CP-1 debt register + Market Levels via CP-3 + Model (PF-LTM) |
| Financials, balance sheet, credit metrics (FY-2…FY, PYTD, YTD, LTM or PF) | Model |
| Loan RV and HY RV (index statistics, comparables) | CP-3 |
| Valuation, existing and new instruments | CP-3 |
| Recommendation per Strategy and per instrument, investment thesis, catalysts | CP-6 |
| Portfolio Fit per portfolio | CP-3 portfolio phase (script-owned arithmetic) |

## 6. Model

- **Port** `caos/calculators/credit_model/` from caos branch `claude/book-model-redesign-7ce1fc` (`5c3cd52f`; the stacked PR series ends at `claude/book-model-13-statements`, `de49e035`): frame, history, debt, statements and projection. Its rules carry over: derived periods are host arithmetic, a missing component gives null with a typed reason that names itself on every figure built from it, a denominator ≤ 0 gives null, and no row repeats a figure.
- **PF-LTM is caos's `pro_forma_column`.** It is the LTM plus every row of CP-1's `cp1.pro_forma_adjustment_register` for that LTM (r14), each keeping CP-1's sign and adding to its own line: revenue, EBITDA and adjusted EBITDA, cash interest, cash, total debt and the facilities. It exists only when the register has rows for the LTM. Every PF figure therefore comes from a source in the pack, such as the lender presentation's pro forma capitalisation; RBOT never derives one from Price Talk.
- **House view on top of it** (D19):
  - Structuring EBITDA = PF-LTM adjusted EBITDA with every issuer add-back;
  - SSIM EBITDA = the same with `exclude_unrealised`;
  - PF interest = PF-LTM cash interest; PF interest cover = SSIM EBITDA over it;
  - Structuring Multiple and SSIM Multiple = PF total debt over each.
- **Snapshot columns:** FY-2…FY, PYTD, YTD and LTM, with PF-LTM in place of LTM when it exists.
- **EV:** listed equity from Market Context, else the SSIM EV multiple × SSIM EBITDA; % EV per facility.
- **Projections:** CP-2G drivers through a port of caos's CP-CF (`caos/calculators/cash_flow.py`), Base and Downside FY+1–3 (interfaces spec §6).
- **Output:** `model.json` (embedded in the Report) and `model.xlsx` (values only, one sheet per band) for the analyst's own model.

## 7. Evidence and quality

- **Method carried into the rewrite:** Deploy V's source hierarchy, gap and conflict rules, the six analytical-depth rules, and the evidence → risk mechanism → creditor implication chain. The fork's canon fixes (r1–r14) are the reference for what a checker can actually enforce.
- **Citations** follow caos D105–D107: a short excerpt plus file and page. A citation fault refuses the citation, never the answer.
- **Validators** are generated from each module's `contract.json` (successors of the fork's `validate_handoff.py`, `completeness_check.py` and `confidence_score.py`) and run on every Handoff, so prose and checker cannot contradict. On failure the module is marked Restricted or Blocked in the Report, its dependants run with that limitation or are skipped, and the run continues (D13).
- **Upstream Handoffs** passed to a module are capped (caos `MAX_UPSTREAM_HANDOFF_BYTES = 98_304`).

## 8. Report

- **One self-contained HTML file:** inline CSS, JS and SVG, no network, so it opens offline from disk. Alongside it, `report.md` carries the same content.
- **Tabs:**
  1. Front Page (the Credit Snapshot for Full Credit Assessment)
  2. Analysis by module
  3. Model (collapsible bands, column toggles, a click-through passport per cell)
  4. Portfolio Fit
  5. Deep Research
  6. What changed (Prior Case)
  7. Evidence (every citation with its excerpt)
  8. Limitations: those known at Approval, then anything unforeseen
- **Embedded data:** `<script type="application/json" id="rbot-run">` holds the Run Brief, Handoff digests and bodies, and `model.json`, so a later Prior Case diff is exact.
- **Design process:** build three mockups of the Snapshot plus one drill-down tab from the CZR golden run, using the `impeccable` skill, with tokens sampled from State Street Investment Management's public site and the template's own conventions (navy section bars, logo top-right, dense tables). The owner picks one. The others are deleted.

## 9. Build order

1. **Spike on the work machine** (owner-run, recorded; Plan 01 Task 2). Confirm personal skills load from `~/.copilot/skills/`; `/rbot` invocation; subagents (`runSubagent`) can read and write files and run the terminal; Python and pip; fetch availability (for Deep Research); the Claude and GPT models offered. Any "no" changes the design before the plans that depend on it.
2. **Plans in roadmap order** (`docs/superpowers/plans/2026-10-11-deploy-vi-roadmap.md`, plan list in the interfaces spec §13): foundation; corpus and intake; Model; cp-start; module rewrites by layer, each with an A/B against its r14 original on corpus packs (ship only with no loss on the depth rubric); orchestrator; Report and every Front Page (three Credit Snapshot mockups, owner pick); install and live acceptance on Claude and GPT in VS Code.
3. **Corpus regression closes every plan** (D28).

## 10. Not verified

- Quick-depth Credit Snapshot: the fork bars CP-6 (and CP-3B) from LITE input, so at Quick depth nothing owns Recommendation, thesis or catalysts yet. The rewrite can lift that bar; decide in the Quick increment (e.g. a rewritten CP-6 accepts screening input and labels its output screening-only).
- VS Code subagent tool access, personal-skill loading and fetch on the work build (step 1 exists for this).
- That the rewrite preserves analytical quality: the A/B grading rubric and its pass bar are set in step 3, not yet defined.
- That the r14 branch's CP-1 amendment is final: it was unmerged when chosen; later caos fixes are reference input only.
- SSIM brand tokens: sampled from public pages, not an internal brand guide.
- HY comparables: no HY Sector RV workbook was seen, so HY RV relies on whatever Bloomberg exports the analyst attaches.
- Talk valuation conventions in CP-3 (3Y DM horizon with OID, call-adjusted bond yields) need owner review against desk practice.
- The template's own PF interest formula ("adjust if EURIBOR or SONIA") suggests the desk sometimes computes PF interest from base rate + margin; Deploy VI reads it from sourced PF adjustments only, per the owner's 2026-10-11 decision.
