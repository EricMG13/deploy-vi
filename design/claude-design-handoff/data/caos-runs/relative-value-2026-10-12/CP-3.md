---
module_id: "CP-3"
module_name: "RelativeValueSecuritySelection"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-3-7f6d1546a1fffc07"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-09-CP-3"
credit_os_invocation_sha256: "f4afdc8140054d7d87b17140fce635cfd57ddba077801598be0c73100083a1a8"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
  - module_id: "CP-1"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "feb32206df70f6261119dceb61308629455fa9537a6f5305a4d941c2fb2015a9"
  - module_id: "CP-1C"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "42230e82490f199a3a3c30c949a25432faf6c02f6113fbb878e0b50db5f1a42f"
  - module_id: "CP-2"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "cf766bfab5fb04e5d74ed27c529d923dbd0e60e7e3c34998f4cfdb20782d3d7a"
  - module_id: "CP-4"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "c2065f2772ed5d15894c37ebbc483f4d64bf3247b0f430f149163c1e52c470d0"
  - module_id: "CP-3D"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "84cc5fe2f9b0f2037db160b7d7feb101659850250cb0ffa41d1b591304cb4994"
  - module_id: "CP-2G"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "858a12c276a6a62ed2930d2fa32673309618f988394ca817c19975f9ad11ceb7"
confidence_score: 53
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [LAST_TRADE_ONLY, NO_MATCHED_EXECUTABLE_COMPS, COLLATERAL_VALUE_AND_ICA_MISSING, NO_RECOVERY_CASES, NO_PORTFOLIO_CONSTRAINTS, NO_GOVERNING_SCORE_WEIGHTS, MERGER_FINANCING_MISSING]
validation_warnings: [DEBT_DEFINITION_CONFLICT_INHERITED, UNSECURED_INDENTURE_ABSENT, MARKET_COMPARABILITY_RESTRICTED, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-6, CP-6A, CP-5, CP-5A]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-3_20261002.md`. Owned object: security-level relative value, including absorbed instrument preference and generic portfolio fit. Execution mode: **Capital-Structure RV**. CP-0, CP-1, CP-2 and the selected optional handoffs match the pinned CZR/Q2 2026 run and hashes; CP-4 supplies a qualified legal overlay. CP-3 status: **Ready with Limitations**; CP-3A: **Ready with Limitations**; CP-3B: **Completed with Limitations**, generic mode. **Confidence: 53/100, Low; QA Restricted; committee Requires More Work.** Self-assessment uses ten material claims—seven directly sourced, one calculated, one inference, one information gap—giving E=83; 52/80 required source/schema demands covered gives C=65; partial source gate S=0.7 and P=0: `(0.6×83+0.4×65)×0.7=53.06`. No host validation or file-export result is claimed. No loan-market observation is delivered; the loan RV comparison remains a gap, not an assumed Sector RV quote.

## Analysis

### Recommendation

**Requires More Work** for both priced Caesars 2032 bonds; relative value is **Unclear**, not Cheap merely because one last-trade yield exceeds the other. FINRA's October 1 trades show the secured February 2032 bond at $93.28/8.063520% and unsecured October 2032 at $84.94/9.318398%; the different lien, maturity and call paths and missing executable quotes prevent an adequate-compensation finding. [C16, C17, C18, C19, C20, C21, C22, C23, C24, C29] The secured claim has a documented priority advantage, but collateral dilution and permitted releases prevent a recovery estimate. [C29, C41, C42] Lower Las Vegas earnings and fixed lease cash demands threaten refinancing flexibility; Regional earnings, reported liquidity and compliance counter an immediate-distress thesis. [C37, C38, C36, C46] Obtain matched prices, operative security documents, recovery inputs and transaction financing before selecting or sizing either instrument.

**Fundamental-to-market transmission.** First-half issuer Adjusted EBITDA was $1,807 million versus $1,839 million, despite $675 million of operating cash flow. CFO less $335 million of cash property/equipment purchases was $340 million; that is calculated after-capex cash, not recurring maintenance FCF. First-half debt cash interest of $368 million and GLPI/VICI rent-related cash interest of $686 million are separate disclosed costs already reflected through the cash-flow presentation; neither is deducted again from CFO. [C32, C33, C34, C35, C36] At June 30, cash plus reported available borrowing capacity was $2,928 million, while financing obligations were separately classified at $13,157 million. [C37, C52] Liquidity is a counterweight, not proof that cash is freely distributable to each obligor.

**Relative value and contrary case.** The unsecured-minus-secured displayed yield difference is **125.4878 basis points**, calculated solely from FINRA's reported yields. It is not a credit spread, matched-duration residual, yield-to-worst difference or executable switching return. MGM's 6.722997% and PENN's 6.644415% last-trade yields are contextual only: both sampled bonds mature in 2029, versus Caesars' two 2032 bonds; peer priority, cash-flow conventions and trade sizes are not established by the lookup summaries. [C18, C22, C25, C26, C27, C28] The strongest contrary argument is that collateral and guarantees make the secured issue preferable even without a spread model; it wins only if operative collateral schedules and a downside waterfall demonstrate meaningful protection after pari claims, and matched executable quotes show adequate compensation. Conversely, a larger unsecured yield is not sufficient without recovery and call-adjusted analysis.

**Downside and invalidation.** Repeated weak Las Vegas visitation or table hold would first lower gaming/hotel contribution; property and lease cash requirements would respond more slowly, compressing CFO and resources available for the 2028–30 principal schedule. Q2 Las Vegas Adjusted EBITDA was $410 million versus $469 million, while Regional rose to $488 million from $439 million; the offset could defeat the downside if it persists without acquisition-driven comparability distortion. [C38, C39, C40] Watch subsequent segment earnings, customer-deposit settlements, revolver use and documented refinancing. The May 2026 Fertitta agreement is **in-period but still conditional in the delivered filing**, not a completed post-quarter financing. Alberta's July 13 launch is a flagged subsequent operating event, not June revenue. [C44, C51]

### Instrument preference and portfolio decision

The CEI revolver, term loans and secured notes share a first-lien architecture as described in the filing; Caesars Virginia's locally secured facility has a different asset/guarantee perimeter. The 2032 unsecured note lacks a lien and therefore is more exposed to residual value after secured claims, but no recovery percentage is supported. [C29, C30, C31] CP-4 identifies theoretical pari-debt and release routes, not an executed uptier or proven unused basket; the delivered second-lien agreement is only a form. The March supplement changes the base indenture's defeasance text, and the August supplement adds guarantors; use the linked versions, not the original alone. [C41, C42, C43, C50] No instrument is designated Preferred or Secondary on compensation grounds. CP-3A Completed with Limitations. Preferred: none. Key Gaps: executable prices, collateral valuation, operative intercreditor documents and recovery cases.

Overall, **both Caesars 2032 bonds are Requires More Work for portfolio implementation**. Their dated last trades identify a research question, but no mandate, holdings, concentration limits, trade depth, exit route or loss budget is supplied. The binding implementation constraint is unknown mandate and portfolio capacity, compounded by unmeasured stressed liquidity; neither Core nor Starter sizing, a numeric size, or a scalable switch is supported. Monitor a fully specified two-sided market and any new first-lien issuance, guarantor release or merger-financing filing before reconsidering. CP-3B Completed with Limitations. Sizing Posture: Requires More Work. Missing Inputs: portfolio constraints, holdings, executable liquidity and loss budget.

Overall, Caesars' **fundamental score is Not Scorable** because no governing factor weights are supplied, despite observable earnings and fixed-charge risks. Relative value is **Unclear** because dated last trades are not comparable executable spreads and recovery cannot be quantified. The strongest upside to debt is durable Regional offset plus cash retention; the main downside is persistent Las Vegas weakness transmitted through lease cash needs to refinancing and potentially diluted collateral. Further analysis requires matched quotes, current governing documents, certified covenant inputs, collateral values and a portfolio mandate. CP-3 Completed with Limitations. Recommendation: Requires More Work. RV: Unclear. Key Gaps: comparable market values and recovery/implementation evidence.

### Analytical appendix — complete canonical registers

All June amounts below are USD millions and use **instrument book values** where an amount is assigned. Those instrument values sum to the debt-note book presentation, not automatically to canonical balance-sheet debt; the separately disclosed revolver finance-charge adjustment must be retained. `null` is a missing numerical input, never zero. Market prices and yields are FINRA last trades dated October 1, observed October 2; they are not bids, offers or evaluated marks. T3.3 factors are unweighted: no invented equal-weight composite. The recovery-waterfall calculation is withheld because asset values, priority-adjusted claims and enterprise-value cases are not delivered; no script result is asserted.

#### T3.1 — Source Register
| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 439e1450-b5ae-4830-b4c3-3719da918fe3 | CZR Form 10-Q | Primary-Unverified | June 2026 | CZR consolidated | Financials, debt stack, conditional merger [C6, C12, C32, C44] | Unaudited; entity cash and recovery values absent | Fundamental and instrument bases |
| f991456d-d304-4d03-9648-bcdf899ce7a5 | CZR FY2025 Form 10-K | Primary-Unverified | FY2025 | CZR | Annual EBITDA and later-amendment index [C45, C58] | Index is not operative amendment text | Period/version control |
| 8b807696-96c6-4d9b-9e4e-911e1fea35e5; 32dbac40-24c2-4e9a-9dfa-0bd4ad9cbe4e; 6a435737-2079-4a28-83cb-a9394c17059a | Executed 2032 secured-note legal family | Primary-Unverified | 2024 | CEI and joining guarantors | Note priority, calls, conditional releases and amended provisions [C29, C42, C43, C49, C50] | Collateral agreement and executed ICA absent | Structural assessment |
| 86dcb55f-6abe-4aab-8143-7e29addf278a; 3093e5d3-2687-41f0-b88a-2330b5077c7f | FINRA Caesars lookups | Secondary-Reputable | October 2026 observation | Two CZR notes | Last-trade price/yield [C16, C17, C18, C20, C21, C22] | No executable quote or spread [C24] | Bounded RV |
| 4b57b4a0-a633-4bf9-a890-34d48e34f3a7; 02ea2477-b79c-4618-80c2-3b4317e6bafa | FINRA MGM/PENN lookups | Secondary-Reputable | October 2026 observation | Contextual peers | Dated last-trade yields [C25, C26] | 2029 tenor and priority mismatch [C27, C28] | Context, not peer average |
| CP-0; CP-1; CP-1C; CP-2; CP-4; CP-3D; CP-2G | Accepted same-run handoffs | Secondary-Reputable | Q2 2026 | CZR | Definition, peer, legal, market and forward limitations | Handoff conclusions cannot replace original source or missing forecast | Re-anchored analytical context |

#### T3.3 — Issuer / Security Scorecard
| Category | Factor | Weight | Raw Score 1–5 | Weighted Score | Confidence | Evidence | Risk Mechanic | Credit Implication |
|---|---|---|---|---|---|---|---|---|
| F1 business | Las Vegas/Regional offset | Not provided — no governing weights | Not Assessable — offset durability and Windsor normalization unresolved | Not Scorable | Low | Vegas 410/469; Regional 488/439 [C38, C39] | Regional growth can offset a property downturn but may not persist | PD monitoring, not a precise grade |
| F2 cash | CFO and investment flexibility | Not provided — no governing weights | Not Assessable — maintenance split absent | Not Scorable | Low | H1 CFO 675/680, capex 335/453 [C33, C34] | Reduced investment improves cash after capex without proving sustainment | FCF durability uncertain |
| F3 financial | Fixed payments and refinancing | Not provided — no governing weights | Not Assessable — forward funding and covenant EBITDA absent | Not Scorable | Low | Cash interest categories and maturities [C35, C36, C40] | Fixed payments compete with reinvestment if EBITDA falls | Refinancing risk requires monitoring |
| F4 structural | Secured versus unsecured claim | Not provided — no governing weights | Not Assessable — value and current ICA absent | Not Scorable | Low | Secured architecture and release provision [C29, C42] | Priority can help secured recovery but releases/pari debt dilute access | LGD cannot be scored |

#### T3.4 — Override Log
| Override Type | Trigger Evidence | Score Cap / Penalty | Revised Composite Score | Explanation |
|---|---|---|---|---|
| No hard-risk override triggered | No weighted composite or sourced hard override threshold; reported compliance is not quantified headroom [C46] | None applied | Not Scorable | An override cannot repair absent weights or force a ranking. |

#### T3.5 — Relative Value Table
| Security | Market Level | Market Date | Source | Quote Quality | Comps | Seniority / Security | Compensation vs. Risk | RV Label |
|---|---|---|---|---|---|---|---|---|
| CZR 12769GAC4, 6.50% Feb 2032 | $93.28; 8.063520% vendor last-trade yield [C16, C17, C18] | Trade Oct 1; observed Oct 2 [C19] | FINRA | Last trade; no size, bid/ask or spread [C24] | Same issuer unsecured Oct 2032 differs in priority, tenor and call; MGM/PENN 2029 yields contextual only [C22, C25, C26, C27, C28] | USD notes; CEI first-priority secured, subject to exclusions [C29] | Recovery and matched executable spread absent | Unclear |
| CZR 12769GAD2, 6.00% Oct 2032 | $84.94; 9.318398% vendor last-trade yield [C20, C21, C22] | Trade Oct 1; observed Oct 2 [C23] | FINRA | Last trade; missing executable and benchmark fields [C24] | Same-issuer secured Feb 2032 not same collateral/call/maturity; peer 2029 bonds not like-for-like | USD reporting; bond denomination not independently verified; senior unsecured [C9] | Higher displayed yield cannot establish compensation after senior claims | Unclear |
| MGM/PENN 2029 context only | FINRA last-trade yields 6.722997% / 6.644415% [C25, C26] | Oct 1 trade observations | FINRA | Trade sizes, peer seniority and matched spreads absent | 2029 versus CZR 2032; currency/metric conventions not independently aligned [C27, C28] | Peer lien rank unverified | Excluded from matched peer statistic | Unclear |

#### T3.6 — Fundamental Value Matrix
| Security / Issuer | Fundamental View | Relative-Value View | Structural / Recovery View | Final Matrix Bucket | Rationale | Evidence ID |
|---|---|---|---|---|---|---|
| CZR secured 2032 | Unweighted; earnings pressured but liquidity reported | Unclear | First lien documented; value and dilution unquantified | Requires More Work | Fixed lease cash claims can reduce cushion; no executable compensation/recovery test [C32, C36, C37, C41] | F2, F3, F4 |
| CZR unsecured 2032 | Same issuer fundamental exposure | Unclear | Unsecured residual after secured claims; recovery unquantified | Requires More Work | Yield difference mixes priority, tenor and call; no supported loss-adjusted comparison [C18, C22, C29] | F1, F3, F4 |

#### T3.7 — Final Ranking
| Rank | Issuer | Security / Tranche | Composite Score /100 | Normalized /5.0 | Credit Tier | Fundamental View | Relative Value View | Final Recommendation | Strongest Attribute | Weakest Attribute | Key Credit Issue | Monitoring Trigger | Evidence ID | Countervailing Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Unranked | CZR | 12769GAC4 secured Feb 2032 | Not Scorable | Not Scorable | Not Scorable | Mixed, unweighted | Unclear | Requires More Work | Documented first-lien architecture [C29] | Collateral value and matched quote absent | Pari dilution ahead of maturity | New first-lien issue or release | F2, F3, F4 | Regional offset and liquidity [C37, C39] could support a stronger view if sustained and protection verified. |
| Unranked | CZR | 12769GAD2 unsecured Oct 2032 | Not Scorable | Not Scorable | Not Scorable | Same issuer exposure | Unclear | Requires More Work | Higher displayed last-trade yield [C22] | No secured collateral claim [C9, C29] | Residual recovery under debt load | Debt issuance or certified refinancing terms | F1, F3, F4 | Yield may compensate sufficiently if matched quotes and recovery cases demonstrate it; currently untested. |

#### T3.9 — Monitoring Triggers
| Trigger | Threshold / Signal | Why It Matters | Credit / RV Impact | Evidence ID |
|---|---|---|---|---|
| Las Vegas earnings | Further comparable-period deterioration from Q2 EBITDA 410; quantitative predictive threshold not supplied | Repeated weakness can consume fixed-charge cushion | Reassess both claims and refinancing | F1, F3 [C38] |
| Priority/perimeter | First-lien issuance, guarantor change or collateral release; quantitative threshold not available in provided materials | Additional equal-ranking claims or less collateral can raise LGD | Reassess secured preference | F4 [C41, C42, C43] |
| Price and transaction | Two contemporaneous executable quotes or filed merger financing | Allows matched compensation and revised debt stack | Recompute RV before selection | F3, F4 [C24, C44] |

#### T3.10 — Gaps Ledger
| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| G-RV | Executable two-sided prices, sizes, benchmark and aligned peer terms; enterprise Sector RV loan observations not delivered | No matched spread or loan DM | RV Unclear; no bond/loan switch | Obtain enterprise workbook access and instrument-level executable market data; do not use its placeholder |
| G-SCORE | Governing factor weights and complete factor evidence | No valid weighted composite | Both T3.7 score columns Not Scorable | Supply authorized scoring framework |
| G-LEGAL | Current bank amendments, executed ICA/collateral agreement, unsecured indenture and entity valuation | Reachable collateral and release mechanics unverified | Recovery and preference restricted [C45, C59] | Review operative signed documents and schedules |
| G-FUND | Covenant EBITDA/headroom, maintenance capex and merger funding | Cash and refinancing downside not quantified | No Preferred conclusion [C44, C46] | Obtain certificate, project spend and transaction financing |
| G-TECH | Trade depth, ownership and settlement detail | Last trade does not establish exit price | No executable switching or sizing [C24] | Obtain dealer colour and settlement terms |

#### T3B.1 — Source Register
| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 439e1450-b5ae-4830-b4c3-3719da918fe3 | CZR Form 10-Q | Primary-Unverified | June 2026 | CEI consolidated and described CVA borrower | Book debt, maturity and guarantee description [C6, C7, C30, C40] | No entity collateral value | Stack and structural overlay |
| 8b807696-96c6-4d9b-9e4e-911e1fea35e5; 32dbac40-24c2-4e9a-9dfa-0bd4ad9cbe4e; 6a435737-2079-4a28-83cb-a9394c17059a | Executed secured-note family | Primary-Unverified | 2024 | CEI and note guarantors | Priority, call and guarantor provisions [C29, C43, C49, C50] | Security/ICA text not delivered | Note protection |
| 86dcb55f-6abe-4aab-8143-7e29addf278a; 3093e5d3-2687-41f0-b88a-2330b5077c7f | FINRA bond observations | Secondary-Reputable | Oct 1 trades, Oct 2 observation | CEI 2032 notes | Prices/yields [C17, C18, C21, C22] | Last trade only [C24] | Compensation cross-check |
| CP-4 accepted handoff | LegalCovenantInterpreter | Secondary-Reputable | Q2 2026 route | CEI | Qualified provision-level overlay | Not executed ICA or asset appraisal | Legal-risk boundary |

No completed post-June capital-stack transaction is evidenced here. The July 13 Alberta launch is a subsequent **operating** event, not an issued debt instrument; it is excluded from the June stack. [C51]

#### T3B.2 — Capital Structure Dashboard
| Instrument | Type | Amount | Currency | Maturity | Seniority / Lien | Collateral | Guarantors | Coupon / Margin | Fixed / Floating | Source Trace |
|---|---|---|---|---|---|---|---|---|---|---|
| CEI revolver | Revolving credit facility | 120 book | USD reporting | Jan 2028 | CEI senior secured, first-lien group | CEI pledged assets subject to exclusions | CEI domestic guarantor group | SOFR-based margin | Floating | 10-Q Note 6 [C1, C30] |
| CEI Term A | First-lien term loan | 618 book | USD reporting | Jan 2028 | CEI first-lien group | Same qualified CEI collateral group | CEI domestic guarantor group | SOFR-based margin | Floating | 10-Q Note 6 [C2, C30] |
| CEI Term B | First-lien term loan | 1,993 book | USD reporting | Feb 2030 | CEI first-lien group | Same qualified CEI collateral group | CEI domestic guarantor group | SOFR plus stated margin in filing | Floating | 10-Q Note 6 [C3, C30] |
| CEI Term B-1 | First-lien term loan | 2,808 book | USD reporting | Feb 2031 | CEI first-lien group | Same qualified CEI collateral group | CEI domestic guarantor group | SOFR plus stated margin in filing | Floating | 10-Q Note 6 [C4, C30] |
| CEI secured 2030 | First-lien secured notes | 1,987 book | USD | Feb 2030 | Equal first-priority CEI liens | Qualified note collateral | Subsidiary note guarantors | 7.00% | Fixed | 10-Q Note 6 [C5, C30] |
| CEI secured 2032 | First-lien secured notes | 1,487 book | USD | Feb 2032 | Equal first-priority CEI liens | Qualified note collateral; exclusions/release routes | Signed subsidiary guarantors | 6.50% | Fixed | Note 6/indenture/supplement [C6, C29, C43] |
| CVA delayed draw | Non-guarantor/local debt | 372 book | USD reporting | Apr 2029 | Separate Caesars Virginia first lien | CVA material assets | No CEI guarantee of CVA facilities | Variable margin not supplied | Floating | 10-Q Notes 6/guarantees [C7, C31] |
| CEI unsecured 2029 | Senior unsecured notes | 1,193 book | USD reporting | Oct 2029 | CEI senior unsecured | No note lien stated | Filing-described unsecured subsidiary guarantees | 4.625% | Fixed | 10-Q Note 6 [C8] |
| CEI unsecured 2032 | Senior unsecured notes | 1,088 book | USD reporting | Oct 2032 | CEI senior unsecured | No note lien stated | Filing-described unsecured subsidiary guarantees; governing text absent | 6.00% | Fixed | 10-Q Note 6 [C9, C59] |
| Special Improvement District bonds | Non-guarantor/local debt, rank unverified | 38 book | USD reporting | 2037 | [Insufficient Information] — security/rank not specified in debt table | [Insufficient Information] — pledged assets not specified | [Insufficient Information] — obligor guarantees not specified | 4.30% | Fixed | 10-Q Note 6 [C10] |
| Other notes/payables | Non-guarantor/local debt, rank unverified | 1 book | USD reporting | [Insufficient Information] — final date not stated | [Insufficient Information] — rank not stated | [Insufficient Information] — collateral not stated | [Insufficient Information] — guarantees not stated | [Insufficient Information] — rate not stated | [Insufficient Information] — rate type not stated | 10-Q Note 6 [C11] |

The issuer's debt-note **secured** and **unsecured** subtotals are not separately printed in the delivered excerpt; avoid an invented subtotal. Note-book total is 11,705; balance-sheet canonical debt is 11,699 after the separate −6 deferred-finance-charge presentation. Neither includes the separately classified 13,157 financing obligations. [C12, C13, C14, C15, C52] CVA cannot be assumed pari on CEI collateral merely because its local facility is first lien. Ordering above is by claim group, with local and unverified claims explicitly outside a single CEI ordinal.

#### T3B.3 — Instrument Matrix
| Instrument | Price | Spread / Yield / DM | Market Date | Source | Quote Quality | Call Schedule | Covenant Package | Liquidity | Source Trace |
|---|---|---|---|---|---|---|---|---|---|
| CEI secured 2032 | $93.28 | FINRA yield 8.063520%; spread/DM missing | Oct 1 last trade | FINRA | Not executable | Feb 2027 onward per note; notice and conditional calls | Indenture incurrence, liens, sale and guarantee conditions | Exit depth not assessable | [C17, C18, C19, C24, C49] |
| CEI unsecured 2032 | $84.94 | FINRA yield 9.318398%; spread/DM missing | Oct 1 last trade | FINRA | Not executable | FINRA next call Oct 2027; full indenture absent | [Insufficient Information] — operative unsecured indenture not delivered | Exit depth not assessable | [C21, C22, C23, C57, C59] |
| Other CEI and CVA instruments | null — no delivered instrument quotes | [Insufficient Information] — no priced yield/DM | [Insufficient Information] — no quote date | 10-Q for terms only | No market observation | [Insufficient Information] — instrument-specific call/prepayment terms not all delivered | Filing describes facility and covenant families | Not assessable | [C1, C2, C3, C4, C5, C7, C8, C10, C11] |

#### T3B.4 — Structural Positioning Log
| Instrument | Structural Rank | Contractual Seniority | Lien Priority | Guarantee Coverage | Collateral Coverage | Structural Subordination | Priming Capacity | Key Risk Mechanic | Source Trace |
|---|---|---|---|---|---|---|---|---|---|
| CEI bank group and secured 2030/2032 notes | CEI first-lien pari group; enforcement allocation unverified | Senior | First priority subject to permitted liens | Material wholly owned domestic subsidiary architecture; complete entity/value schedule absent | Substantially all described assets, with exceptions; valuation missing | Partial exposure to non-guarantor value | Conditional pari issuance and other lien routes; unused capacity not calculated | Additional shared claims dilute collateral proceeds | [C29, C30, C41] |
| CVA delayed draw | Separate local first-lien claim; not a CEI pari rank | Senior at CVA | CVA asset first lien | No CEI guarantee of CVA facility | CVA material assets; value missing | Separate obligor perimeter | CVA-specific incremental capacity unverified | Local priority limits automatic CEI-note asset reach | [C7, C31] |
| CEI unsecured 2029/2032 | Behind secured claims as to CEI collateral | Senior unsecured | None stated | Filing-described subsidiary guarantee group; full 2032 indenture absent | No direct note lien | Exposure to debt at non-guarantors | Additional secured issuance can increase effective priority ahead | Unsecured residual value sensitivity | [C8, C9, C29, C30] |
| SID bonds and other payables | Unverified relative rank | Unverified | Unverified | Unverified | Unverified | Unverified | Unverified | Cannot place in a recovery waterfall | [C10, C11] |

#### T3B.5 — Legal / Covenant / LME Overlay
| Instrument | Legal / Structural Finding | Priming Risk | Leakage Risk | Weak Collateral | Covenant Weakness | LME Vulnerability | Exposed Creditor Class | Source (CP-4 / CP-4A / CP-3C) | Source Trace |
|---|---|---|---|---|---|---|---|---|---|
| CEI secured 2032 | Incurrence routes and automatic permitted releases coexist with holder protections | Pari dilution possible; priority priming not established | Qualifying disposition/designation can change direct reach | Value and perfection not verified | No measured unused baskets/headroom | No executed uptier established; transaction-specific risk unresolved | First-lien classes | Accepted CP-4; CP-3C not delivered | [C41, C42, C43] |
| CEI unsecured 2032 | Filing establishes unsecured rank; operative indenture absent | New liens may rank ahead in collateral | Restricted-group transfers could change residual value | No note collateral | Unsecured covenant text missing | No specific exchange or uptier established | Unsecured guarantor claims | Accepted CP-4 qualified overlay; CP-3C not delivered | [C9, C29, C59] |
| CVA facility | Distinct borrower and collateral | CEI pari-priming comparison inapplicable | Entity distributions not quantified | Local collateral value absent | CVA certificates not supplied | Not established | CVA lenders and indirect CEI equity claim | CP-4 entity finding | [C7, C31] |

#### T3B.6 — Recovery Sensitivity
| Instrument | Recovery Sensitivity | Evidence | Risk Mechanic | Credit Implication | Confidence | Source Trace |
|---|---|---|---|---|---|---|
| CEI secured 2032 | Insufficient Information | First-priority architecture and conditional releases [C29, C42] | Pari dilution and excluded assets can vary reachable value | Directionally ahead on pledged CEI collateral; numerical LGD withheld | Structural Only | [C29, C41, C42] |
| CEI unsecured 2032 | High sensitivity | Senior unsecured description versus CEI first-lien group [C9, C29] | Residual enterprise value must support claim after effective secured priority | Potentially greater LGD sensitivity; no recovery percentage | Low | [C9, C29, C52] |
| CVA and unpriced CEI layers | Insufficient Information | Local security and June amounts, without valuation [C1, C7, C31] | Distinct assets and unmeasured liens prevent joint EV allocation | No class recovery assignment | Structural Only | [C7, C31] |

#### T3B.7 — Compensation Cross-Check
| Instrument | Market Level | Market Date | Structural Rank | Recovery Sensitivity | Compensation Adequacy | Compensation vs. Risk | Source Trace |
|---|---|---|---|---|---|---|---|
| CEI secured 2032 | $93.28; 8.063520% vendor last trade | Oct 1 trade; Oct 2 observation | CEI first-lien | Insufficient Information | Unclear | No recovery cases or aligned executable comps | [C17, C18, C19, C24, C29] |
| CEI unsecured 2032 | $84.94; 9.318398% vendor last trade | Oct 1 trade; Oct 2 observation | CEI unsecured | High sensitivity | Unclear | Higher yield cannot establish adequate residual-risk payment | [C21, C22, C23, C24, C9] |
| Other instruments | [Insufficient Information] — no delivered price | [Insufficient Information] — no quote date | Mixed or unverified | Insufficient Information | Insufficient Information | Market compensation not assessed | [C1, C7, C10, C11] |

#### T3B.8 — Preference Decision Table
| Instrument | Preference | Structural Position | Recovery Sensitivity | Compensation Adequacy | Confidence | Key Reason | Monitoring Trigger | Source Trace |
|---|---|---|---|---|---|---|---|---|
| CEI secured 2032 | Requires More Work | First-lien architecture; actual asset reach unvalued | Insufficient Information | Unclear | Low | Priority advantage is not a proved loss-adjusted preference | Pari issue, release, matched quote | [C17, C18, C29, C41, C42] |
| CEI unsecured 2032 | Requires More Work | Unsecured residual claim | High sensitivity | Unclear | Low | Incremental yield not isolated from maturity/call and LGD | New secured debt and operative unsecured terms | [C9, C21, C22, C59] |
| Other CEI/CVA instruments | Requires More Work | First-lien, local or unverified | Insufficient Information | Insufficient Information | Structural Only | Unpriced or incomplete terms preclude a traded preference | Obtain quote and entity security schedule | [C1, C7, C10, C11] |

No within-tier traded ranking is forced. Structural priority favors the secured claim **only with respect to actual shared pledged assets**; it is not a statement that its observed yield adequately compensates the investor. A verified collateral waterfall and matched executable quote set could resolve the two Requires More Work outcomes.

#### T3B.10 — Monitoring Triggers
| Trigger | Instrument | Threshold / Signal | Why It Matters | Credit / Recovery Impact | Evidence ID |
|---|---|---|---|---|---|
| Pari issuance or collateral release | CEI secured 2032 | Any filed first-lien addition or release; quantitative threshold not available in provided materials | Can dilute or remove direct secured value | Reassess LGD and preference | F4 [C41, C42] |
| Residual-value dilution | CEI unsecured 2032 | New secured borrowing or material guarantor transfer | More prior-ranking claims can reduce unsecured recovery | Reassess compensation | F3, F4 [C9, C41] |
| Cash and maturities | Both 2032 bonds | Persistent EBITDA/CFO decline with delayed funding ahead of disclosed maturity wall | Weakens refinancing capacity | Escalate credit review | F1, F3 [C32, C33, C40] |

#### T3B.11 — Gaps Ledger
| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| B-G1 | Executed first-lien ICA, collateral agreement and asset/guarantor schedule | Legal rank alone does not measure realizable proceeds | Recovery waterfall withheld | Obtain executed instruments and entity valuations |
| B-G2 | Enterprise-value cases, priority-adjusted claims and valuation of leased versus owned assets | No supported fulcrum or recovery sensitivity amount | No recovery percentage or waterfall script output | Build sourced EV/collateral cases before running waterfall |
| B-G3 | Executable bond prices and 2032 unsecured indenture | Call-adjusted compensation and covenants incomplete | Both preferences Requires More Work [C24, C59] | Obtain matched quotes and signed unsecured terms |
| B-G4 | Current merger financing and certified ratios | Stack and capacity can change | No transaction-adjusted preference [C44, C46] | Review filed financing and compliance certificate |

#### T3C.1 — Portfolio Input Gate
| Input | Available / Missing | Source | Limitation | Portfolio Impact |
|---|---|---|---|---|
| Current-run CP-3 selection | Available with limitations | T3.7 and T3B.8; FINRA [C17, C21] | Both bonds Requires More Work | Generic fit only |
| Security identity and June debt stack | Available | 10-Q and FINRA [C6, C9, C16, C20] | June book amounts are not October holdings | Qualitative capital-layer exposure |
| Mandate, holdings, constraints and proposed size | Missing | No matching portfolio evidence delivered | No portfolio identity, as-of or limit | No mandate-specific fit or numeric size |
| Liquidity, downside budget and correlated exposures | Missing | FINRA summary lacks trade size [C24] | No exit-depth or position-loss input | Core and Starter not supported |

CP-3B output mode: **Generic Portfolio-Fit Logic**. No portfolio constraints workbook is delivered for this case; no sample limit is adopted.

#### T3C.2 — Portfolio Fit Register
| Name / Instrument | Fit Category | Evidence | Risk Mechanic | Why It Fits / Does Not Fit | Constraints / Notes | Source Trace |
|---|---|---|---|---|---|---|
| CZR secured 2032 | Not assessable | First-lien claim, last trade only [C17, C18, C29] | Priority may reduce LGD, but ill-defined exit and portfolio capacity prevent implementation | Watchlist / monitoring only, not an eligibility finding | Mandate and recovery cases missing | [C17, C24, C29] |
| CZR unsecured 2032 | Not assessable | Unsecured claim and last trade [C9, C21, C22] | Residual recovery and quote depth can dominate displayed yield | No supported RV-switch role | Mandate and loss budget missing | [C9, C22, C24] |

#### T3C.3 — Position Sizing Posture Table
| Name / Instrument | Sizing Posture | Evidence | Reason | Key Risk | Implementation Note | Confidence | Source Trace |
|---|---|---|---|---|---|---|---|
| CZR secured 2032 | Requires More Work | First-lien architecture; no executable quote [C29, C24] | No mandate capacity, exit route or quantified downside | Collateral dilution and stressed sale price | No order or numeric allocation proposed | Low | [C17, C24, C41] |
| CZR unsecured 2032 | Requires More Work | Unsecured claim; last trade [C9, C21] | No loss-budget or recovery-supported sizing | Residual LGD and maturity financing | No order or numeric allocation proposed | Low | [C9, C21, C40] |

#### T3C.4 — Risk Budget Flags
| Flag | Evidence | Risk Mechanic | Why It Matters | Caution Level | Portfolio Impact | Source Trace |
|---|---|---|---|---|---|---|
| First-lien supply/leakage | Conditional lien basket and release provisions [C41, C42] | More claims or less pledged value increase loss sensitivity | Secured label alone does not cap portfolio loss | High | Withhold executable allocation | [C41, C42] |
| Liquidity and issuer concentration | FINRA omits trade size and quotes [C24] | Sale price under stress may differ from last trade | No demonstrated exit or aggregate CZR exposure | Not Assessable | Withhold size pending portfolio and dealer evidence | [C24] |
| Refinancing/transaction | 2028–30 schedule; conditional merger [C40, C44] | New funding may change claims or cash needs | Portfolio maturity-factor correlation could rise | High | Monitor / Escalate before implementation | [C40, C44] |

#### T3C.5 — Concentration and Correlation Register
| Exposure Dimension | Current Exposure | Proposed / Pro Forma Exposure | Limit / Capacity | Evidence Status | Risk Mechanic | Portfolio Implication | Source Trace |
|---|---|---|---|---|---|---|---|
| Issuer/group | null | null | null | Not Provided — holdings/mandate absent | Both bonds share CZR operating risk | No issuer allocation | No portfolio source; issuer identity [C6, C9] |
| Sector/subsector | null | null | null | Not Provided — holdings/mandate absent | Gaming-cycle exposure can correlate | No sector-cap test | No portfolio source; operating exposure [C38] |
| Sponsor/ownership | null | null | null | Not Provided — portfolio absent | Proposed ownership change is conditional | No sponsor-cap test | [C44] |
| Rating bucket | null | null | null | Not Provided — mandate exposure absent | Agency grades may affect eligibility | No bucket-cap test | FINRA displays distinct Moody's grades [C55, C56] |
| Maturity year/wall | null | null | null | Not Provided — holdings absent | 2032 bonds coexist with nearer issuer maturities | No wall-concentration test | [C6, C9, C40] |
| Capital-structure layer | null | null | null | Not Provided — holdings absent | Secured/unsecured losses differ | No layer-cap test | [C9, C29] |
| Correlated holdings/common factor | null | null | null | Not Provided — holdings absent | Shared casino demand or real-estate lease exposure could correlate | No correlation allowance | [C36, C38] |

#### T3C.6 — Liquidity and Implementation Assessment
| Liquidity / Implementation Factor | Evidence | Risk Mechanic | Implementation Consequence | Constraint / Action | Source Trace |
|---|---|---|---|---|---|
| Trading depth/bid-ask | Last trade only; no size/dealer quote [C24] | A recorded print need not be a repeatable exit | Exit risk not assessable | Request timestamped two-sided depth | [C24] |
| Settlement/minimum denomination | Secured indenture describes $2,000 and $1,000 increments; no matched settlement information | Legal denomination does not establish accessible liquidity | Operational feasibility incomplete | Confirm custodial eligibility and settlement | Secured indenture p.19 [C29]; settlement gap |
| Stressed exit | No trade history or executable stress bid [C24] | Downdraft can widen liquidation cost | No forced-sale loss calculation | Require depth and mandate liquidity horizon | [C24] |
| Ability to add/trim | No current holdings or price-impact observations | Scaling may worsen execution | Neither action authorized | Revisit after holdings and dealer evidence | [C24] |

#### T3C.7 — Downside Budget and Recovery Sensitivity
| Downside Scenario / Driver | Input Basis | Formula / Method | Result / Directional View | Portfolio Loss / Risk-Budget Implication | Status | Source Trace |
|---|---|---|---|---|---|---|
| Price downside | FINRA last trades, no stress quote [C17, C21, C24] | Position size × price change; both inputs for an executable stress missing | Price shock Not Calculable from Provided Materials — no stress price | Portfolio loss Not Calculable from Provided Materials — size absent | Not Calculable | [C17, C21, C24] |
| Recovery/LGD | Secured priority versus unsecured residual [C9, C29] | Sourced EV less prior claims, allocated by operative security | Directional: unsecured more exposed to residual value | No quantified loss budget or fulcrum | Directional Only | [C9, C29, C41] |
| Refinancing wall | Filed 2028–30 maturities [C40] | Weaker earnings → cash demand → refinancing dependence | Directional downside, not a forecast default | Size/correlation unknown; avoid budget claim | Directional Only | [C38, C40] |
| Legal dilution/deal | Conditional lien/release routes and merger [C41, C42, C44] | Additional pari debt or asset movement changes reachable pool | Directional loss-severity risk | No transaction-adjusted portfolio loss | Directional Only | [C41, C42, C44] |

#### T3C.8 — Monitoring Triggers
| Trigger ID | Indicator | Leading / Lagging | Threshold or Qualitative Signal | Linked Risk Flag | Portfolio Action | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| CP-3B-MON-001 | New first-lien debt or collateral release | Leading | Any documented issue/release; quantitative threshold not available in provided materials | First-lien supply/leakage | Monitor / Escalate | [C41, C42] | Amount and basket use unverified |
| CP-3B-MON-002 | Vegas EBITDA, CFO and revolver access | Lagging | Repeated weakening versus filed periods with increased drawings; predictive cutoff not supplied | Refinancing/transaction | Monitor / Escalate | [C33, C38, C40] | No covenant headroom or forward cash bridge |
| CP-3B-MON-003 | Matched quotes and portfolio exposure | Leading | First executable two-sided prices plus current holdings/mandate | Liquidity and issuer concentration | Monitor / Escalate; reassess posture | [C24] | No trade depth or portfolio book delivered |

#### T3C.9 — Gaps Ledger
| Gap ID | Missing Data | Why It Matters | Affected Sizing / Risk Budget / Trigger | Consequence for Confidence | Required Follow-Up Source |
|---|---|---|---|---|---|
| CP-3B-GAP-001 | Portfolio identity, mandate eligibility, current and proposed positions | Cannot test concentration or compliance | T3C.2–T3C.5; all postures | High impact | Dated mandate and holdings report |
| CP-3B-GAP-002 | Executable market depth, settlement and stressed bids | Cannot assess exit or Starter feasibility | T3C.3, T3C.6–T3C.8 | High impact | Dealer/TRACE detail and operational confirmation |
| CP-3B-GAP-003 | EV cases, collateral and recovery waterfall | Cannot translate default to portfolio loss | T3C.7 loss budget | High impact | Entity valuation and signed security/ICA documents |
| CP-3B-GAP-004 | Current merger financing, legal basket usage and certified headroom | Forward claim dilution and access unresolved | Risk budget and event triggers | High impact | Filed financing and compliance certificate |

### Inherited definition and period conflicts

CP-1's accepted T4.11 **Definition Conflict Register** is inherited below without re-adjudicating its definitions. The direct source anchors for its debt, EBITDA, interest and Windsor distinctions are the June filing and annual report. [C12, C13, C14, C15, C32, C35, C36, C58]

#### T4.11 — Definition Conflict Register, inherited from CP-1
| Metric Name | Canonical Definition | Issuer-Reported Definition | Source of Conflict | Periods Affected | Materiality | Downstream Modules Affected | Resolution / Recommendation |
|---|---|---|---|---|---|---|---|
| CF-1 debt carrying vs principal | BS current + long-term debt, net: June 11,699; December 11,784 | Debt note principal June 11,807 and December 11,905; debt-note book June 11,705 and December 11,792; deferred revolver charges −6/−8 outside note book | S2 BS p.2 and Note 6 p.16; S1 Note 9 [CP-1 C11–C13, C33] | June 2026; December 2025 | June face exceeds canonical by 108; December by 121; June note book exceeds canonical by 6 | CP-2, CP-3, CP-3C, CP-MODEL | Use 11,699/11,784 for canonical debt; keep face, note book and financing-charge roles separate |
| CF-2 Adjusted EBITDA | Calculated EBIT + D&A separately from issuer adjustment | Issuer adds transaction/other, SBC, interest, tax, impairment and other bridge items; expressly disclaims alignment with debt/lease definitions | S1/S2 bridges [CP-1 C15, C16, C23, C35] | FY2025; H1/Q2 2026/2025 | LTM issuer adjusted 3,592 versus calculated EBITDA 3,255: difference 337 | CP-2, CP-4, CP-4A | Label every adjusted-basis ratio non-contractual; obtain covenant definition and testing inputs |
| CF-3 consolidated vs attributable net loss | Distinguish consolidated loss from parent-attributable loss | Release headlines GAAP net loss 62 for Q2; filing consolidated loss 41, loss attributable to Caesars 62 | S3 p.1 vs S2 statement p.3 [CP-1 C26, C27] | Q2 2026 and comparative | Q2 2026 difference 21, equal to noncontrolling income | CP-2, CP-2D, CP-1C | Retain both filing measures and qualify release headline |
| CF-4 interest and rent cash | Debt cash interest and lease-financing cash interest separately, with combined coverage labelled | H1 debt cash interest 368, GLPI/VICI rent interest 686; FY debt 813 and financing-obligation rent interest 1,349 | S2 cash supplemental p.8; S1 p.61 [CP-1 C9, C10, C39, C40] | FY2025; H1 2026/2025; LTM | LTM debt-only 776 versus combined 2,139 | CP-2, CP-2A, CP-4 | Present both denominators, never treat Adjusted EBITDA as after rent |
| CF-5 segment perimeter | Preserve source segment and reporting dates | Windsor management fees formerly Managed and Branded, operations Regional from March 3 | S2 Note 1 [CP-1 C19] | H1/Q2 2026 vs 2025 | No separately sourced pro forma EBITDA adjustment | CP-1C, CP-2G, CP-MODEL | Preserve reported comparison; seek like-for-like schedule before attributing all growth organically |

## Evidence Trace

| Claim | Marker | Document | Page / permitted use |
|---|---|---|---|
| June stack, carrying/face and separate financing presentation | [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C52] | CZR June 2026 10-Q | pp.2, 9; book values are not last-trade prices |
| Bond observation and limits | [C16, C17, C18, C19, C20, C21, C22, C23, C24] | FINRA Caesars lookups | p.1 each; last trade only |
| 2029 peer context | [C25, C26, C27, C28] | FINRA MGM/PENN lookups | p.1 each; tenor mismatched |
| Priority, guarantees, conditional liens/releases | [C29, C30, C31, C41, C42, C43, C49, C50] | Secured indenture/supplements; CZR 10-Q | Indenture pp.13, 34, 43; supplements p.1; filing p.11 |
| Cash, segment downside, float, merger and dates | [C32, C33, C34, C35, C36, C37, C38, C39, C40, C44, C46, C47, C48, C51, C53, C54] | CZR June 2026 10-Q | pp.4–5, 9–11, 16–17, 20, 22 |
| Missing legal versions and rating observations | [C45, C55, C56, C57, C59] | CZR FY2025 10-K; FINRA lookups | 10-K pp.55–56; FINRA p.1 |

## Source Registry

T3.1 and T3B.1 identify the active source family and its restricted uses. The filing supplies June debt amounts; October FINRA lookups supply only dated last trades. The secured base indenture must be read with both supplements. The FY2025 exhibit index identifies, but does not itself provide, later credit amendments and the unsecured 2032 indenture. [C45, C50, C59] MGM and PENN issuer releases provide contextual operating evidence but cannot repair differences in lease accounting or a missing matched bond quote. No enterprise Sector RV observation or current portfolio constraints is delivered to this run; neither sample reference is represented as live data.

## Gaps & Conflicts

T3.10, T3B.11 and T3C.9 are cumulative, phase-specific gap ledgers. CF-1 through CF-5 above remain the inherited CP-1 definition register. The issuer's reported compliance does not quantify covenant headroom; the last-trade cross-section does not supply bid/ask, size or benchmark; legal priority does not supply asset value. [C24, C41, C42, C46] These independent gaps jointly prevent an executable relative-value preference and portfolio size. The strongest contrary evidence—reported liquidity, Regional earnings and secured claim priority—raises the case for investigation, not the evidence quality of an untested recovery or price assumption. [C29, C37, C39]

**Event separation:** the proposed May 27 merger was signed before June 30 but remains conditional in the delivered filing; a hypothetical closing is not included in June debt. The July 13 Alberta launch is post-period and supplies no June cash or EBITDA. [C44, C51] No later capital-stack event is established by these materials. Missing current transaction status remains an explicit research question for a newly sourced run.

## QA Validation

| Self-check | Own result | Basis / disposition |
|---|---|---|
| Identity and lineage | Passed locally | Host-owned fields copied; matching accepted CP-0, CP-1, CP-1C, CP-2, CP-4, CP-3D and CP-2G hashes retained. |
| Workflow and appendix | Restricted | CP-3, CP-3A and CP-3B steps represented; every required T3/T3B/T3C register populated. Recovery waterfall not fabricated without inputs. |
| Figures, dates and definitions | Passed locally with limitations | Book/face/canonical debt distinguished; June financials separated from October trades and July operating event. |
| Score and recommendation | Restricted | Missing weights leave composite Not Scorable; no forced rank or Cheap/Preferred claim. |
| Market and portfolio gate | Restricted | Last trades and mismatched peers cannot establish executable RV; no mandate-specific size. |
| Confidence/status | Restricted | E=83, C=65, S=0.7, P=0 gives 53/Low; partial source gate maps to Restricted. |
| Host validation/completeness | Pending | Host checks follow this answer; no script output, exit status or saved-file confirmation is claimed. |

**Next analytical use:** CP-6 can debate the two bounded Requires More Work outcomes; CP-5/CP-5A should audit citation support and missing executable/recovery/portfolio inputs. Reassess CP-3 only after current signed legal documents, matched trade evidence and mandate constraints enter an accepted snapshot.