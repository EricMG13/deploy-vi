# Module record: CP-6 screening basis on czr-2026q2-lite-full-credit-screen (B only, Plan 09 R5)
| Field | Value |
|---|---|
| Date (UTC) | 2026-10-16 |
| Pack / Pathway | czr-2026q2-lite-full-credit-screen / FULL_CREDIT_ASSESSMENT quick |
| Run folder | (scratchpad) rc09b/corpus-runs/record-09-quick/czr-2026q2-lite-full-credit-screen/pack/rbot-runs/20261016-czr-full-credit-assessment (git-ignored; the 09.7 record run) |
| Code | rbot tree d7c0542 (build/09.7-quick-record) |
| A | none: r14 has no LITE CP-6 (reference/deploy-v-r14/skills/cp-6-ic-debate-challenge/SKILL.md, "LITE profile compatibility — CP-6": not executable in LITE_CREDIT_22, allowed_use FULL_ONLY, missing_input_behavior UPGRADE) |
| B | handoffs/CP-6.md sha256 382d3aa3495c576dc5e1bbf34ee62011015b8505772c2230381962fdb6de669d; model claude-sonnet-5-5; 2026-10-16T20:41:57.142754+00:00 to 2026-10-16T20:45:57.405567+00:00 |
| Graders | mx-precise ×2 (agent effort: medium), the rubric prompt adapted to one Handoff (X = B; steps-X = CP-6 MODULE.md; inputs = native upstream Handoffs and the Run Brief) |

Ruling R5 (owner-approved 2026-10-16): no A side exists, so this record is **B-only against the rubric** and is flagged **non-equivalent** to a §12.7 A/B: C, F and G are measured, and D is scored absolute without an A baseline. The §12.7 comparative bars ΣD(B) ≥ ΣD(A), no criterion B < A − 1 and G(B) ≥ G(A) cannot be evaluated.

## Measurements

measure-b.json:

```json
{"module": "CP-6", "validate_exit": 0, "findings": [], "C": "23/23", "gaps": 0, "bytes": 18579, "qa_status": "Restricted", "F": "32/34"}
```

C(B) = 23/23 = 1.00 (bar max(0.95, C(A)) with no C(A): 0.95). F(B) = 32/34 = 0.941 (bar 0.90).

## Grader sheets

Grader 1:

| criterion | X | reason |
|---|---|---|
| D1 | 2 | All eight steps appear in order: gate, neutral map with the central controversy, Bull/Bear with the zero-bound chain and its missing links, weighting with unsupported dimensions left unscored, the formula, an empty FIT table, the SGU and the memo. But the step-1 gate never registers CP-1A and CP-1B, which were available (front matter `inputs: CP-0, CP-3, CP-5, CP-L10`). The Bull defence is folded into each "resolution" rather than argued. |
| D2 | 2 | The step-5 sentence is chained: EBITDA and rent [C3][C4], then the mechanism, then PD/LGD. But the main driver, "rent is paid before bondholders", is the ranking that CP-5's open finding F-04 says no source supports, because the lease texts are absent. "Covenant coverage falls faster than revenue" has no citation and does not use CP-1B's covenant figures (FCCR 2.0x, 1,121 of EBITDA after rent). |
| D3 | 2 | It gives a concrete counter-case: the secured notes at 93.28 with a 101% put could be Overweight. It says what would make it win (proxy and commitment letters confirm the Change of Control triggers the put) and the move (to 2 - Modest OW). But one win condition, "financing is committed", is already met: X's own [C10] cites the fully executed commitment letters. |
| D4 | 2 | Starting point (93.28, 84.94, debt 11,699), first break at closing (2027-05-27 / 2027-08-27, [C6]), consequence (2028-01-31 refinancing) and triggers are present and dated. Transmission is left "unquantifiable". It drops the second automatic extension to 2027-11-27, which is in the 8-K and in CP-1A. |
| D5 | 2 | It reconciles three conflicts explicitly: calculator vs FINRA yield, Model 3,095 vs issuer 2,928 liquidity, and the Model vs CP-1 secured split. It does not reconcile CP-5 F-04 (it adopts the contested rent ranking), F-01 (maturity-wall basis) or F-02 (EBITDA basis 1,715 vs 1,807). It also ignores CP-1A/CP-1B evidence: covenants, the reverse fee, no financing condition, and the November extension. |
| D6 | 2 | Mostly lean. Neutral V3 is labelled as a placeholder and correctly does not drive a relative-value claim. But the four IC weighting scores (3/2/4/3) feed nothing in the decision, which is purely the 4+3=7 formula. The two bonds tie only because of that label, which X admits does not reflect their different risk. |
| G | 2 | Eight gaps, each with cause, effect and a lifting source, and no filler. Some lifting sources are vague ("The named Full modules", "A linked Full run"). The lease-text gap behind the rent-ranking claim is buried inside the recovery row, not tied to the conclusion it undermines. |

**Single largest weakness:** the decision's main driver, "686 of rent ahead of debt / rent is paid before bondholders", is the ranking that CP-5 open finding F-04 says no source in the pack supports. The Handoff adopts it without reconciling it, and it never uses CP-1A/CP-1B, which were available and hold the covenant and merger-term evidence that could have replaced it.

Grader 2:

| criterion | X | reason |
|---|---|---|
| D1 | 2 | All eight steps are present and labelled. Step 1 lists the limitations correctly, step 4 leaves the unsupported dimensions unscored with no average, and step 6 has an empty cap table, correctly. Step 3 is compressed: there is no separate Bull Defense, and the Bear never states a fragility vector or what would prove it wrong. The challenge also never cites CP-L10's `OVERALL` row or its Deepen topics as its basis. |
| D2 | 2 | Most conclusions run evidence [C], then mechanism, then creditor effect. The Recommendation sentence follows the required formula. But the main driver, "rent is paid before bondholders and covenant coverage falls faster than revenue" [C3][C4], is a mechanism the sources do not show: no lease text and no covenant calculation exist. |
| D3 | 3 | The counter-case is strong and specific: the secured notes at 93.28 with a 101% put could be Overweight. It wins if the proxy and commitment letters confirm the put applies and the financing is committed, and the Handoff says the result would be 2 - Modest OW. It matches the strongest case in CP-3 and in step 7. |
| D4 | 2 | The downside has a start (93.28 and 84.94, debt 11,699), a first break (closing, dated by [C8][C26], plus the Credit Agreement default [C6]), transmission (put or priming, size marked as a gap), a consequence (the 2028-01-31 refinancing [C25]) and triggers. Weak points: the 8-K text also extends the end date again to November, which the Handoff leaves out. The consequence step names a date but has no financial mechanism. |
| D5 | 2 | Three conflicts are reconciled with a stated governing figure: the yields (calculator against FINRA), liquidity (3,095 against 2,928) and the secured/unsecured split (9,385/2,314 against 9,379/2,320). Missed: the third liquidity measure, 2,903 used by CP-1 and CP-L10 (CP-5 F-05). Also missed: CP-5 F-04 says no source supports rent ranking ahead of debt, yet the Handoff restates that ranking as fact. |
| D6 | 2 | The 1–5 weighting scores (3/2/4/3) do not feed the decision. The decision comes entirely from 4 + 3 = 7, and the 3 is a V3 the Handoff itself calls a scale-neutral placeholder. Both are method-mandated and openly qualified, but the weighting adds nothing to the conclusion. |
| G | 3 | There are eight gaps, each with a cause, what it limits and a named lifting source (Market Levels export, Sector RV Workbook, CP-4/CP-4C, indentures, lease texts, merger documents, portfolio files, a linked Full run). Each is specific to this pack, with no filler. |

Single largest weakness: the decision driver ("686 of rent ahead of debt ... rent is paid before bondholders and covenant coverage falls faster than revenue") states as fact a ranking and covenant mechanism that CP-5 F-04 flagged as unsupported, since the lease texts are absent and no covenant was computed. A smaller citation slip makes the same kind of error: the Handoff cites [C17] as "the issuer may redeem instead", but that indenture text (Section 4.08(f), line 1544) is the third-party-offer carve-out, not a redemption option.

## Resolution

| Criterion | G1 | G2 | Resolved (mean of two; no pair differs by more than 1) |
|---|---|---|---|
| D1 | 2 | 2 | 2 |
| D2 | 2 | 2 | 2 |
| D3 | 2 | 3 | 2.5 |
| D4 | 2 | 2 | 2 |
| D5 | 2 | 2 | 2 |
| D6 | 2 | 2 | 2 |
| ΣD | 12 | 13 | 12.5 / 18 |
| G | 2 | 3 | 2.5 |

| Bar | Result |
|---|---|
| citations C(B) ≥ 0.95 | PASS (1.00) |
| front_page F(B) ≥ 0.90 | PASS (0.941) |
| sum_depth, no_criterion_below_a_minus_1, gaps vs A | NOT MEASURED (no A side, R5) |

## Verdict

B-only record: C and F pass their absolute bars; D is adequate on every criterion (2 to 2.5), G 2.5. Screening behaviour per R4b holds: qa_status Restricted, basis Screening on all three Strategy rows, rationales open "Screening basis:", absent Full inputs named as limitations, a linked Full run named as the upgrade, no Committee Ready claim. Both graders name the same largest weakness: the decision driver adopts the rent-before-bondholders ranking that CP-5 open finding F-04 flags as unsupported (no lease texts in the pack), and the challenge does not use CP-1A/CP-1B covenant and merger-term evidence. Not equivalent to a §12.7 pass; the owner may waive or require an A (R5).

Not verified: any A-side comparison (none exists in r14); grader citation checks covered a sample of citations only (grader notes); live-model behaviour.
