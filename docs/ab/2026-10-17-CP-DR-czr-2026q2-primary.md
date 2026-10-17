# Module A/B: CP-DR on czr-2026q2-primary (Plan 10, round 1)
| Field | Value |
|---|---|
| Date (UTC) | 2026-10-17 |
| Pack / Pathway | czr-2026q2-primary / FULL_CREDIT_ASSESSMENT full; Deep Research approved Q1-Q5, fetch off (RBOT_FETCH unset; recorded approval.fetch off) |
| Run folder | (scratchpad) rc10/corpus-runs/record-10-full/czr-2026q2-primary/pack/rbot-runs/20261017-czr-full-credit-assessment (pre-RC run 1; git-ignored) |
| Code | rbot tree 991cbf8 (build/10.7-record before the 10.8a revision) |
| A | reference/deploy-v-r14/skills/cp-dr-deep-research + CANON_SHARED.md, supplied_only, non-interactive; mx-feature claude-sonnet-5-5; 2026-10-17T15:54:10Z to 2026-10-17T16:00:23Z; sha256 68c792fccf5044b0b29ec5ed8217c86cf16dfc8c9760fe2e85e6f678432d9c86 |
| B | handoffs/CP-DR.md sha256 5744f13c3970cf2513e80fee38c0d06ca648b9f5d02b108d6c6009d721efcd44; model claude-sonnet-5-5; 2026-10-17T15:24:07.817741+00:00 to 2026-10-17T15:34:06.224847+00:00 |
| Order | X=B Y=A |
| Graders | mx-precise ×2 (agent effort: medium), rubric prompt verbatim |

Side-A attempts (all kept in the sealed folder): A.r0 was refused by measure-a. Reason (A.r0-reason.txt, verbatim): A.r0 refused by measure-a (map worker): "ab_grade: Evidence Trace E10: an extra source reference is outside the configured source column" — the E10 excerpt quotes an upstream Handoff sentence ending in its citation marker "[C67]" (ab_evidence._extra_references treats any [..] outside the sources column as a reference); otherwise six sections and conforming tables. Ruling P12: one fresh side A with a no-bracket excerpt rule. Rulings P11 (format sentence given up front, Plan 09 P6/P6b precedent) and P12 (one retry with a no-bracket excerpt rule). Both can only raise C(A), and so B's citation bar.

## Measurements

measure-a.json:

```json
{"module": "CP-DR", "side": "A", "C": "23/27", "findings": ["citation_unanchored", "source_unknown"], "evidence_references": 27}
```

measure-b.json:

```json
{"module": "CP-DR", "validate_exit": 0, "findings": [], "C": "55/55", "gaps": 8, "bytes": 32666, "qa_status": "Restricted", "F": null}
```

C(A) = 23/27 = 0.852; C(B) = 55/55 = 1.00; F not applicable (CP-DR owns no Front Page table).

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
| D1 | 2 | 2 | X: completed all 8 steps (scope lock, pack first, fetch marked off, ledger, contrary evidence, answers, sector view, gaps). But its step-5 search for contrary evidence missed the pack's Q4 counter-evidence: the 10-Q (lines 1202-1211) and the Q2 release (line 62) show Digital H1 Adjusted EBITDA up 137 vs 123 while Q2 fell on the tax rates. It also left CP-1 unused. Y: did the brief/ledger, workstreams, gap rows, synthesis, scenarios and QA. But it has no `approved_plan_hash` (a required YAML field and pipeline step 3), no validator output kept verbatim, and its workstream rows lack the evidence-needed, source-class and effort-cap columns. |
| D2 | 2 | 2 | X: every question is chained evidence [Cn] → mechanism → creditor effect, all cited, but Q2 and Q4 mechanisms are generic. Y: chains are more issuer-specific (LV margin 40.3% vs 44.5%; the pari passu TLB putting the expected BB- downgrade on all first-lien debt). But key links rest on figures with no evidence row or locator: consolidated EBITDA 920/955, Digital 68/80, 18 VICI/6 GLPI casinos. All are true in the pack. |
| D3 | 2 | 3 | X: a counter-argument with a win condition for Q1, Q2, Q3 and Q5. Q3 is strong and checks out (MGM Strip table win 29.6% vs 22.9%), but Q4 says "No contrary evidence found" when the pack holds some, and Q5 rests on a financing-cooperation clause (6.16). Y: every question has a counter-argument and win condition. Q3 slot handle +5.4% and the 16.6% vs 21.1% hold swing, and Q4 Digital H1 EBITDA +11.4%, are both verified; Q5 is weak (argument from absence). |
| D4 | 2 | 3 | X: one Q3 chain (LV EBITDA 410 vs 469 → visitation/rate break → USD 1.4bn fixed rent → 2.0:1 FCCR, which checks out in the 10-K/10-Q). It names no timing, and hold % is a weak trigger. Y: a time-dated chain from approval delay or landlord consent, through operating drift during pendency, to synthetic PF leverage of 14,687/3,592 (labelled synthetic), with dated triggers (Moody's post-09-28, 2027-08-27 extension, LV margin <40.3%, 2027 tax enactments) and scenarios. |
| D5 | 2 | 3 | X: one explicit reconciliation block (Fertitta Entertainment vs Gaming Holdco; FINRA vs Bloomberg ratings; Caesars Regional vs MGM reported/same-store). Upstream Handoffs are not cross-checked. Y: a conflicts list covering entity, instrument-level ratings (correctly records S&P B- on the 6.00% notes), the meaning of the Moody's date vs the Bloomberg export, the Windsor perimeter (Not Calculable), the subsequent-event date (TLB 2026-10-08) and announcement 05-28 vs signing 05-27. Each is kept open with lower confidence, and CP-0 gaps are cited. |
| D6 | 3 | 1 | X: no framework beyond the required sector outlook; statuses (Partly answered vs Unanswered) carry meaning. Y: confidence score 42, coverage 0%, a workstream table, a Research-answer summary repeating TDR.3, and a self-certified QA "Pass" table change no conclusion. The blanket UNRESOLVED/"blocks consumer" labels hide that Q1 timing is in fact answered. |
| G | 3 | 2 | X: each gap gives what is missing, its cause (not in pack; fetching off), its effect on the named consumer ("limits CP-2 to contractual dates"), the source that closes it, and the terms searched; no filler. Y: gap rows give cause, search path and the source that would close them. The effect is mostly a blanket "Blocks CP-2/CP-3/CP-6" rather than what it changes, and the QA/Audit sections add filler. |

X's largest weakness: on Q4 (CP-6's tax downside) it reports "No contrary evidence found" and leaves the mechanism generic. It never uses the 10-Q's direct attribution of the Q2 Digital EBITDA decline to the tax rates, or the offsetting H1 +11.4%, both in the pack.

Y's largest weakness: material figures in its chains and counter-arguments have no evidence row or locator (920/955, Digital 68/80 and 137/123, slot handle, VICI/GLPI casino counts), which breaks its own evidence rule. On top of that, labels flatten partly answered questions to 0% / UNRESOLVED.

Not verified: I spot-checked the figures and claims named above against the prepared pack files. I did not check every citation locator or excerpt in either Handoff line by line, or every CP-0/CP-1/CP-1A statement.

Grader 2:

| criterion | X | Y | reason |
|---|---|---|---|
| D1 | 3 | 2 | X completes all 8 steps of its method: scope lock, Pack-first evidence, the fetch-off case named under Gaps, a ledger with independence, contrary evidence per question, answers, the sector view, and Gaps and status. It also names CP-1 as unused. Y's front matter has no required `approved_plan_hash` field. Its workstream rows leave out evidence needed, source classes and effort cap. Its QA table has no plan-hash continuity, freshness or validator output. |
| D2 | 2 | 2 | X gives each question an evidence, mechanism, creditor chain, but the Q2 and Q4 mechanisms are thin ("higher tax rates cut digital margin"). Y's chains go deeper (for example, the closing downgrade lands on the pari passu new TLB and the existing first lien together), but several links are outside its TDR.2 ledger: consolidated Adj. EBITDA 920 v 955, Digital 68 v 80, 18 VICI casinos, the cross-default risk factor. The figures check out against the pack but have no evidence id. "Rent ranks ahead of debt service in practice" has no citation. |
| D3 | 2 | 3 | X's Q4 says "no contrary evidence found", yet the Q2 release shows Digital H1 Adj. EBITDA up, 137 v 123. Its Q2 counter leans on the synthetic Bloomberg export. Y's counters are grounded in the pack and each says what would make it win: the Las Vegas table hold of 16.6% v 21.1% with slot handle up 5.4% (10-Q lines 1155-1164), and Digital H1 EBITDA up for Q4. Y's Q5 counter is weak, but it is stated. |
| D4 | 2 | 3 | X has one downside chain, for Q3: starting EBITDA 410 v 469, then rent of USD 1.4bn, the 2.0:1 FCCR, and occupancy and hold triggers. It is not dated and is not quantified. Y's causal synthesis runs from approval delay to longer pendency to EBITDA erosion to leverage (synthetic 14,687 / 3,592). Its triggers are dated (Moody's after 2026-09-28, the 2027-08-27 extension, LV margin below 40.3%), and it adds three scenarios. |
| D5 | 2 | 3 | X has one reconciliation paragraph: the buyer entity, FINRA v Bloomberg, and Caesars Regional v MGM same-store. It does not address the 05-27 signing date against the 05-28 announcement date. Y keeps each conflict open with its effect: the acquirer entity (from CP-0), ratings by instrument (it correctly shows S&P B- on the 6.00% notes), the meaning of Moody's 2026-09-28 date, the Windsor perimeter left Not Calculable, the TLB commitment date as a subsequent event, and the synthetic sources. |
| D6 | 3 | 1 | X adds nothing that does not feed an answer or a consequence. Y carries Confidence 42, coverage 0%, a Research-answer summary that repeats TDR.3, a workstream hypothesis grid and a 13-row QA table, and none of them changes the conclusion. Its blanket UNRESOLVED/0% also flattens findings that are partly answered, such as the Q1 timing. |
| G | 3 | 2 | Each X gap gives what is missing, the cause (not in the pack; fetching off), the effect on the consumer ("limits CP-2's timing view to contractual dates"), the source that would close it, and what was searched. Y's gap rows have the cause, the searched files and the lifting source, but give the effect only as "Blocks CP-x". The Audit Summary, Executive answer and QA table repeat the same gaps. |

X's largest weakness is that it leaves evidence in the pack unused for its counter-arguments and downside. It records no Q4 contrary even though Digital H1 EBITDA rose, it does not use the Las Vegas slot-handle and hold split, and its only downside chain is the undated Q3 one.

Y's largest weakness is that material figures in its Analysis sit outside its own TDR.2 ledger with no evidence id: consolidated and Digital Adj. EBITDA, slot handle, the VICI property count, the lease cross-default and the pro forma leverage. It also excluded the MGM and PENN peer releases, which leaves the regional-casino half of Q3 unexamined.

## Resolution and pass bar

score.json (exit 1):

```json
{
  "pass": false,
  "lines": {
    "sum_depth": false,
    "no_criterion_below_a_minus_1": true,
    "citations": true,
    "gaps": true,
    "front_page": true
  },
  "scores": {
    "A": {
      "D1": "2",
      "D2": "2",
      "D3": "3",
      "D4": "3",
      "D5": "3",
      "D6": "1",
      "G": "2"
    },
    "B": {
      "D1": "5/2",
      "D2": "2",
      "D3": "2",
      "D4": "2",
      "D5": "2",
      "D6": "3",
      "G": "3"
    }
  }
}
```

| Line | Result |
|---|---|
| sum_depth ΣD(B) ≥ ΣD(A) | FAIL (13.5 < 14) |
| no_criterion_below_a_minus_1 | PASS |
| citations C(B) ≥ max(0.95, C(A)) | PASS (1.00 ≥ 0.95) |
| gaps G(B) ≥ G(A) | PASS (3 ≥ 2) |
| front_page | PASS (not applicable; CP-DR owns no Front Page table) |

## Verdict

FAIL on sum_depth only (ΣD(B) 13.5 < ΣD(A) 14). This became Task 10.8a (CP-DR process revision, 83261c3), then round 2.

Not verified: Copilot behaviour; fetch quality (fetch off); blinding beyond instructions; A/B on one pack only.
