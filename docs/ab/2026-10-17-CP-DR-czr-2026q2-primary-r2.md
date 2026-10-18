# Module A/B: CP-DR on czr-2026q2-primary (Plan 10, round 2)
| Field | Value |
|---|---|
| Date (UTC) | 2026-10-17 |
| Pack / Pathway | czr-2026q2-primary / FULL_CREDIT_ASSESSMENT full; Deep Research approved Q1-Q5, fetch off (RBOT_FETCH unset; recorded approval.fetch off) |
| Run folder | (git-ignored) .wt/rc10f/corpus-runs/ab-r2-isolated/czr-2026q2-primary/isolated/CP-DR-1/... |
| Code | rbot tree 83261c3 (the RC of the final record run) |
| A | reference/deploy-v-r14/skills/cp-dr-deep-research + CANON_SHARED.md, supplied_only, non-interactive; mx-feature claude-sonnet-5-5; 2026-10-17T15:54:10Z to 2026-10-17T16:00:23Z; sha256 68c792fccf5044b0b29ec5ed8217c86cf16dfc8c9760fe2e85e6f678432d9c86 (unchanged from round 1: same upstream; A.md, A-evidence.json and measure-a.json reused) |
| B | isolated re-run at 83261c3 from the round-1 run's upstream (`proxy_run --module CP-DR --from-run <round-1 run>`); handoffs/CP-DR.md sha256 9b1ce4d0cd41ceaf18c915b896f3420a5a2c2518f007150f3bc8fc8a7b4f4a6f; model claude-sonnet-5-5; 2026-10-17T16:29:31.621934+00:00 to 2026-10-17T16:43:03.210881+00:00 |
| Order | X=B Y=A (sealed/CP-DR-r2/order.json) |
| Graders | two fresh mx-precise (agent effort: medium), rubric prompt verbatim |

## Measurements

measure-a.json:

```json
{"module": "CP-DR", "side": "A", "C": "23/27", "findings": ["citation_unanchored", "source_unknown"], "evidence_references": 27}
```

measure-b.json:

```json
{"module": "CP-DR", "validate_exit": 0, "findings": [], "C": "103/103", "gaps": 11, "bytes": 57877, "qa_status": "Restricted", "F": null}
```

C(A) = 23/27 = 0.852; C(B) = 103/103 = 1.00; F not applicable (CP-DR owns no Front Page table).

## Checked A map

A-evidence.json verbatim:

```json
{
 "source_registry": {
  "id": "id",
  "file": "file"
 },
 "evidence_trace": {
  "id": "id",
  "sources": "sources",
  "locator": "locator",
  "excerpt": "excerpt"
 },
 "source_fields": [],
 "citations": [
  {
   "evidence_id": "E1",
   "source_id": "S1",
   "locator": "Article I, definition of Requisite Gaming Approvals",
   "excerpt": "“Requisite Gaming Approvals” means the Gaming Approvals set forth on Section 1.1(b) of the Company Disclosure Schedule, as amended in accordance with the terms set forth thereon."
  },
  {
   "evidence_id": "E2",
   "source_id": "S1",
   "locator": "Section 7.1(c) Regulatory Approvals",
   "excerpt": "(ii) all Requisite Gaming Approvals shall have been duly obtained and shall be in full force and effect."
  },
  {
   "evidence_id": "E3",
   "source_id": "S2",
   "locator": "Item 1.01, Termination Fees; End Date",
   "excerpt": "The Merger Agreement contains customary termination rights, including the right of any party to terminate if the Effective Time has not occurred by May 27, 2027"
  },
  {
   "evidence_id": "E4",
   "source_id": "S2",
   "locator": "Item 1.01, Termination Fees; End Date",
   "excerpt": "provided that the Initial End Date will be automatically extended to August 27, 2027 (the “First Extended End Date”) and the First Extended End Date shall be automatically extended to November 27, 2027 if, as of the Initial End Date and First Extended End Date, as applicable, all conditions precedent, other than the expiration of the waiting period under the HSR Act and/or receipt of certain required gaming approvals, have been satisfied or are capable of being satisfied."
  },
  {
   "evidence_id": "E5",
   "source_id": "S1",
   "locator": "Section 6.6(e)",
   "excerpt": "prepare and submit to the Gaming Authorities as promptly as practicable, and in any event no later than (i) forty-five (45) days from the date of this Agreement with respect to the initial applications and supporting documents necessary to obtain the Requisite Gaming Approvals set forth on Section 1.1(b)(i) of the Company Disclosure Schedule and (ii) ninety (90) days from the date of this Agreement"
  },
  {
   "evidence_id": "E6",
   "source_id": "S2",
   "locator": "Exhibit index footnote to Exhibit 2.1",
   "excerpt": "Schedules have been omitted pursuant to Item 601(b)(2) of Regulation S-K."
  },
  {
   "evidence_id": "E7",
   "source_id": "S2",
   "locator": "Item 1.01, Termination Fees; End Date",
   "excerpt": "Parent will be required to pay the Company a reverse termination fee of $450,000,000 under certain circumstances"
  },
  {
   "evidence_id": "E8",
   "source_id": "S9",
   "locator": "Terms table, Maturity row",
   "excerpt": "2033-12-15 (seven years from expected closing)"
  },
  {
   "evidence_id": "E9",
   "source_id": "S6",
   "locator": "Observed FINRA record, rating lines",
   "excerpt": "Moody's last-rated date shown: 2026-09-28"
  },
  {
   "evidence_id": "E10",
   "source_id": "S6",
   "locator": "Observed FINRA record, rating lines",
   "excerpt": "Standard & Poor's last-rated date shown: 2024-02-02"
  },
  {
   "evidence_id": "E11",
   "source_id": "S7",
   "locator": "Observed FINRA record, rating lines",
   "excerpt": "Moody's last-rated date shown: 2026-09-28"
  },
  {
   "evidence_id": "E12",
   "source_id": "S8",
   "locator": "Data row for CZR TL B 2030",
   "excerpt": "CZR TL B 2030,BL3912045,,1L Term Loan,99.375,99.750,99.563,,252,Ba3,BB"
  },
  {
   "evidence_id": "E13",
   "source_id": "S9",
   "locator": "Closing paragraph after terms table",
   "excerpt": "An S&P downgrade of the existing first-lien to BB- is expected at closing."
  },
  {
   "evidence_id": "E14",
   "source_id": "S4",
   "locator": "Net Revenues, Three Months Ended June 30 table",
   "excerpt": "Las Vegas | $1,017 | $1,054 | (3.5)%"
  },
  {
   "evidence_id": "E15",
   "source_id": "S4",
   "locator": "Net Revenues, Three Months Ended June 30 table",
   "excerpt": "Regional | 1,570 | 1,435 | 9.4%"
  },
  {
   "evidence_id": "E16",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, net revenues discussion",
   "excerpt": "These increases were partially offset by declines in net revenues in our Las Vegas segment, attributable to lower table games volume and hold as well as lower city-wide leisure customer visitation."
  },
  {
   "evidence_id": "E17",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, Las Vegas segment table",
   "excerpt": "Hotel occupancy | 95.5% | 96.8% | (1.3) pts | 95.4% | 96.5% | (1.1) pts"
  },
  {
   "evidence_id": "E18",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, Las Vegas segment table",
   "excerpt": "Adjusted EBITDA margin | 40.3% | 44.5% | (4.2) pts | 41.4% | 43.9% | (2.5) pts"
  },
  {
   "evidence_id": "E19",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, Regional segment discussion",
   "excerpt": "increased visitation in northern Nevada due to a national tournament throughout the second quarter of 2026"
  },
  {
   "evidence_id": "E20",
   "source_id": "S5",
   "locator": "Item 7 MD&A, casino expenses",
   "excerpt": "Additionally, increased gaming tax rates on sports betting wagers and iGaming in certain states took effect on July 1, 2025."
  },
  {
   "evidence_id": "E21",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, casino expenses",
   "excerpt": "Gaming taxes increased due to higher casino revenues, as well as the impact of increased gaming tax rates on sports betting wagers and iGaming in certain states."
  },
  {
   "evidence_id": "E22",
   "source_id": "S5",
   "locator": "Item 1 Business, regulation discussion",
   "excerpt": "From time to time, federal, state, local and provincial legislators and officials have proposed changes in tax laws, or in the administration of such laws, affecting the gaming industry."
  },
  {
   "evidence_id": "E23",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, Debt and Master Lease Covenant Compliance",
   "excerpt": "The GLPI Leases require the Company to maintain a minimum adjusted revenue to rent ratio of 1.20:1, applicable to the operations of the underlying leased properties."
  },
  {
   "evidence_id": "E24",
   "source_id": "S3",
   "locator": "Part I Item 2 MD&A, Liquidity, VICI Leases",
   "excerpt": "In addition to the CPI escalator, our VICI Leases are also subject to a variable rent adjustment based on certain historical net revenues of our leased properties"
  },
  {
   "evidence_id": "G1",
   "source_id": "S10",
   "locator": "Analysis, Gaps & Conflicts, Missing governing documents",
   "excerpt": "Company Disclosure Schedule 1.1(b), the Requisite Gaming Approvals"
  },
  {
   "evidence_id": "G2",
   "source_id": "S10",
   "locator": "Analysis, Gaps & Conflicts, Missing governing documents",
   "excerpt": "Current agency rating reports (Moody's, S&P): the S&P last-rated dates of 2024-02-02"
  },
  {
   "evidence_id": "G5",
   "source_id": "S10",
   "locator": "Analysis, Gaps & Conflicts, Missing governing documents",
   "excerpt": "VICI Leases, GLPI Master Lease, Lumière lease, the OLG lease, and the document behind the other financing obligation."
  }
 ]
}
```

## Grader sheets

Both sheets were transcribed from the agents' replies; byte equality with the replies is not machine-verified.

Grader 1:

| criterion | X | Y | reason |
|---|---|---|---|
| D1 | 3 | 1 | X: every step of its method is done and visible. It locks scope and states where CP-1 was used. It reads the pack first, notes that fetching was off, keeps a ledger with independence families, reconciles conflicts in one place, lists the terms it searched before writing "none found", gives one answer per question with a downside chain, fills the sector view and states the gaps with the status. Y: several steps are missing or broken. The frontmatter has no `approved_plan_hash` (step 3) and no `run_id`. The workstream plan has no evidence-needed, source-class or effort-cap columns. The synthesis uses figures that are not in its ledger, against "synthesize only from the ledger": 920/955, 68/80, 137/123, 14,687/3,592, "18 VICI and 6 GLPI properties" and "slot handle rose". The validator and confidence-script output is summarised, not kept verbatim. |
| D2 | 3 | 2 | X: each question runs from a cited source to a mechanism to a creditor effect. Examples: the outer End Date of 2027-11-27 is 65 days before the Term Loan A maturity of 2028-01-31 (619, [C94]/[C95], both verified); +2,880 of secured debt dilutes the first lien; financing obligations of 13,157 sit against debt of 11,807. Y: it labels each step (evidence, risk mechanic, creditor implication), but the implications are thin or unsupported. "Rent ranks ahead of debt service in practice" has no source, and the Q3 implication rests on 920/955, which has no evidence row. |
| D3 | 3 | 2 | X: each answer gives the strongest contrary case and what would make it win. Examples: Q1, Parent's 450 reverse fee, the divest/hold-separate undertaking and the arranger's implied December 2026 close; Q3, management's city-wide claim against MGM's ADR and RevPAR of -4%. Its Q4 counter is the weakest. Y: Q3 (slot handle +5.4%, 10-Q line 1156) and Q4 (Digital six-month Adjusted EBITDA 137 against 123) are good counters. But Y left the MGM and PENN releases out of the contrary search, and its Q5 counter rests on what Caesars does not list rather than on Merger Agreement Section 6.6(g). |
| D4 | 3 | 1 | X: each question has a dated chain: starting condition, first break, transmission, consequence and trigger, with arithmetic labelled where the pack allows it (59 x 4 = 236, which is 13.7% of Las Vegas 1,728; 1 point of Digital tax = 14.1, which is 6.0% of Digital Adjusted EBITDA). Y: there is one generic causal synthesis. Its transmission is not quantified ("the pack cannot test headroom"), the leverage uses synthetic 14,687/3,592 with no evidence row, and the scenarios are unweighted. |
| D5 | 3 | 2 | X: it reconciles the three acquirer entities, the arranger close date against the End Dates, ratings by instrument and date (FINRA against the synthetic export), MGM against Caesars on hold-definition and perimeter differences (Windsor; MGM same-store against reported) and the tax timing. It also rechecks the CP-1A and CP-0 figures (467 against 432, End Dates). Y: its conflicts section covers the entity, ratings by instrument, the Moody's date against the export, and the Windsor perimeter. It does not recheck CP-1A or CP-1 figures, never says how CP-1 was used, and avoids the peer disagreement by excluding MGM and PENN. |
| D6 | 3 | 1 | X: it adds no score or framework beyond the required sector outlook (Neutral), and that outlook is tied to cited drivers. Y: the confidence score of 42, the 0% coverage, the workstream matrix, the duplicated research-answer summary and the blanket UNRESOLVED/"consumer blocked" labels do not change any conclusion. The "UNRESOLVED" label also hides the partial findings Y itself sourced. |
| G | 3 | 2 | X: each gap names what is missing and why, what it limits downstream, and the source that would close it (proxy statement, gaming board dockets, agency reports, LVCVA and Nevada Gaming Control Board series, legislature trackers, VICI and GLPI filings). It adds the synthetic-source and subsequent-event limits and says fetching was off. Y: each gap row names where it searched, what would lift the gap and which consumer it blocks. The effect is stated only in a phrase ("Limits Q2 to dates"), and the peer-data gap for Q3 is self-inflicted. |

- X, largest weakness: on Q4 it argues the tax headwind fades but misses the strongest contrary fact in the pack. Caesars Digital six-month Adjusted EBITDA rose to 137 from 123 (Q2 release, line 62). It also states a "101% put on 1,500" in the Q1 consequence with no citation.
- Y, largest weakness: its downside is not causal or dated per question. It gives one generic synthesis built on figures outside its evidence ledger (the synthetic 14,687/3,592, 920/955 and 68/80), so no creditor transmission is quantified or tied to a dated trigger.

Spot-checks against the prepared pack: all of X's checked figures match the source text (Las Vegas, Regional and Digital segment lines, gaming taxes 99/80/166/367, FINRA ratings and dates, MGM Strip and Regional figures, PENN tax gross-up 185.5/137.9, financing obligations 13,157, rent 686, total debt 11,807, Term Loan A due 2028-01-31). Y's uncited figures do exist in the pack: the Q2 earnings release has 920/955, 68/80 and 137/123; the synthetic pro forma capitalisation has 14,687 and 3,592; the 10-Q has slot handle at 2,674 against 2,538 and the 18 VICI casinos. Y still never put them in its ledger.

Grader 2:

| criterion | X | Y | reason |
|---|---|---|---|
| D1 | 3 | 2 | X does every step of its 8-step method: scope lock, pack-first evidence, a fetch-off statement, a ledger with independence, upstream reconciliation, contrary evidence with named searches, a dated downside chain per question, sector view, and gaps/status (X.md:12-37, 113-130). Y has the six H2s, registers, gap rows and a workstream lane, but leaves out required parts of its own method: no `approved_plan_hash`, no `run_id` in the front matter (Y.md:1-18), no emitted validator findings in QA (only a paraphrase of the confidence script, Y.md:224), and the workstream table lacks the evidence-needed, source-class and effort-cap columns (Y.md:42). |
| D2 | 3 | 2 | X chains every question as evidence [Cn] → mechanism → creditor effect, and the figures I spot-checked match the pack (e.g. MGM Strip 2,170,045 vs 2,114,692; the 16-23% hold range; PF senior secured 12,348). Y's chains exist, but several load-bearing figures have no evidence row: consolidated Adjusted EBITDA 920 vs 955, Digital 68 vs 80 and 137 vs 123, Las Vegas slot handle up, 18 VICI casinos (Y.md:58-62). They are true in the pack but not anchored. Y's Q1 "creditor implication" just restates the End Dates. |
| D3 | 3 | 2 | X gives the strongest contrary case per question with what would make it win, and lists what was searched before writing "none found" (X.md:104-108, 35). Q3 uses MGM's falling ADR/RevPAR and management's city-wide view against X's own company-specific reading. Y gives a contrary case and win condition per row, but drops the MGM/PENN peer releases from Q3 (Y.md:36), and its Q1 and Q5 win conditions are near-tautological ("if the schedule showed none required"). |
| D4 | 3 | 1 | X writes a dated chain per question: starting figure, first break, transmission, consequence, trigger. The strongest is Q1: the 2027-11-27 outer End Date falls 65 days before the 2028-01-31 maturity of the 619 Term Loan A (X.md:16). Y has one aggregated causal paragraph whose transmission is unquantified ("erode Adjusted EBITDA") and which says the pack "cannot test" headroom (Y.md:66). Its scenarios are unweighted bullets. |
| D5 | 3 | 2 | X reconciles in one place: acquirer entity, closing date, ratings dates and levels by instrument, Las Vegas and Regional bases (hold definitions, Windsor, same-store), tax timing, and an upstream recompute against CP-0/CP-1A (X.md:26-33). It also uses the CP-1 perimeter (X.md:14). Y's conflicts list covers the acquirer entity, ratings by instrument, Windsor perimeter and subsequent events (Y.md:200-205). It has no upstream recompute, never uses CP-1's perimeter, and leaves out peer-vs-issuer disagreement by excluding the peer releases. |
| D6 | 3 | 2 | X adds no framework beyond the tables its contract requires; the sector outlook "Neutral" is tied to cited drivers. Y carries a confidence score of 42, coverage 0%, a workstream/hypothesis grid and a duplicate summary table (Y.md:6-17, 42-83). None of them changes a conclusion, and "UNRESOLVED ×5 / coverage 0" hides the partial answers Y actually found. |
| G | 3 | 2 | Each X gap names the missing item, its cause (omitted schedule, no landlord filing, fetching off), its effect on a named downstream use, and the source that would close it (X.md:120-128). The last two entries are notes rather than gaps. Each Y gap names its cause and the source that would lift it, but the only effect stated is "Blocks CP-x" (Y.md:192-196). |

**X's largest weakness:** several downside chains are conditional on facts the pack does not hold (the Q5 landlord-consent break, the direction of the Q2 Moody's event), so the quantified transmission stops at "cannot be computed". The Q3 annualised 236 loss is illustrative arithmetic rather than evidence.

**Y's largest weakness:** it leaves the MGM/PENN peer primary filings out of scope (Y.md:36). That leaves Q3 without the market-comparison evidence the pack holds, and leaves Y's Q3 contrary view and reconciliation without that evidence. Y also states unanchored figures (920/955, 68/80, 137/123) in its analysis.

## Resolution and pass bar

score.json (exit 0):

```json
{
  "pass": true,
  "lines": {
    "sum_depth": true,
    "no_criterion_below_a_minus_1": true,
    "citations": true,
    "gaps": true,
    "front_page": true
  },
  "scores": {
    "A": {
      "D1": "3/2",
      "D2": "2",
      "D3": "2",
      "D4": "1",
      "D5": "2",
      "D6": "3/2",
      "G": "2"
    },
    "B": {
      "D1": "3",
      "D2": "3",
      "D3": "3",
      "D4": "3",
      "D5": "3",
      "D6": "3",
      "G": "3"
    }
  }
}
```

| Line | Result |
|---|---|
| sum_depth ΣD(B) ≥ ΣD(A) | PASS (18 ≥ 10) |
| no_criterion_below_a_minus_1 | PASS |
| citations C(B) ≥ max(0.95, C(A)) | PASS (1.00 ≥ 0.95) |
| gaps G(B) ≥ G(A) | PASS (3 ≥ 2) |
| front_page | PASS (not applicable; CP-DR owns no Front Page table) |

## Verdict

PASS; all five pass-bar lines true. Known differences: r14's six sections against Deploy VI's four; A ran no rbot calculator; the A/B does not exercise fetch (both sides pack-only).

Not verified: Copilot behaviour; fetch quality (fetch off); blinding beyond instructions; A/B on one pack only; B is an isolated re-run (ruling-10 style), not the final record run's own CP-DR.
