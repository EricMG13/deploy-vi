---
module_id: "CP-4"
module_name: "LegalCovenantInterpreter"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-4-b8c8c352a133e392"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-05-CP-4"
credit_os_invocation_sha256: "bb22e2642b7f99dd919c8d20ebeb9e29f5e81681dc7988a498fdbab5f5ce23d9"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
  - module_id: "CP-1"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "feb32206df70f6261119dceb61308629455fa9537a6f5305a4d941c2fb2015a9"
confidence_score: 52
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [POST_2024_CREDIT_AMENDMENTS_NOT_ATTACHED, EXECUTED_INTERCREDITOR_NOT_ATTACHED, COLLATERAL_AGREEMENT_NOT_ATTACHED, COVENANT_EBITDA_AND_USAGE_MISSING, ENTITY_LEVEL_VALUE_MISSING, MERGER_AGREEMENT_NOT_ATTACHED, UNSECURED_INDENTURE_NOT_ATTACHED]
validation_warnings: [LEGAL_VERSION_LIMIT, FORM_INTERCREDITOR_NOT_EXECUTED, COVENANT_HEADROOM_NOT_CALCULABLE, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-3, CP-3A, CP-3C, CP-4C, CP-6, CP-6A]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-4_20261002.md`; owned object: provision-level legal and covenant interpretation, including absorbed entity, intercreditor and capacity phases. Executed 2032 secured indenture and supplements clear the legal-document gate; the February 2024 bank incremental agreement supplies an executed amendment and then-conformed credit text. Later bank amendments are indexed but not supplied. The second-lien intercreditor text in the indenture is expressly a **form**, not evidence that such an agreement was executed. [C1, C2, C3, C4, C5, C32, C44, C45] Module status: **Completed with Limitations**. Self-assessed confidence **52/100, Low; Restricted**. Basis: estimated E=78, C=80, partial source gate S=0.7, one minor QA allowance P=3; `(0.6×78+0.4×80)×0.7−3≈52`. This is a self-check, not a host validator result. Legal thresholds below are documentary formulas, **not available headroom**. CP-0 and CP-1 match the pinned run, entity, period and hashes; CP-1's carrying-value debt and non-contractual adjusted EBITDA remain separate from legal test inputs. [C36, C37, C43]

## Analysis

### Creditor implication

The 2032 secured notes have a documented first-priority collateral and subsidiary-guarantee architecture, but pari first-lien issuance, investment and unrestricted-subsidiary routes can dilute creditor access before a payment default. The loan maintenance tests apply to Covenant Facilities, not automatically to Term B/B-1, while the notes rely principally on incurrence restrictions. [C6, C7, C8, C20, C21, C24] This weakens an inference that reported covenant compliance means substantial distance to distress. [C39] The most consequential relative-value question is how much collateral and cash flow would remain reachable after additional pari debt or a permitted transfer; an executed first-lien agreement, security schedules, basket utilization and actual covenant EBITDA are needed before quantifying it. The provided second-lien form cannot establish an operative 180-day junior standstill. [C32, C33]

### Provision-level read-through and creditor control

**Definitions and ratios.** Credit Agreement §6.11 sets a 6.50:1 maximum total leverage ratio and 2.00:1 minimum fixed-charge coverage ratio from December 31, 2024 for Covenant Facilities. An equity cure under §7.02 can increase test EBITDA for specified periods without improving historical operating cash generation. The non-covenant tranches do not automatically default solely from a financial-test breach; acceleration of Covenant Facilities is the transmission trigger. [C6, C7, C8, C9] Analyst interpretation: operating deterioration can reach covenant lenders first and impair refinancing access before it produces a direct Term B/B-1 covenant Event of Default. No tested ratios or covenant EBITDA bridge are supplied; reported Adjusted EBITDA is expressly potentially different. [C39, C43]

**Debt and liens.** The 2032 indenture permits Credit Agreement debt under §4.03(b)(i), while Permitted Liens clauses (6) and (25) establish separate ratio/fixed-or-grower routes. Credit Agreement §§2.21 and 6.01(r), together with §6.02(u), permit additional debt and corresponding lien capacity subject to their specified conditions. [C11, C13, C14, C20, C21, C53] Analyst interpretation: additional first-priority claims can share collateral proceeds and dilute recovery for an existing secured note even where there is no formal lien subordination. The Term B-1 incremental MFN applies only within the drafted size, timing, currency, lien and maturity conditions; do not project it as perpetual protection. [C12] No aggregate capacity is calculated: baskets overlap, some reclassify, and utilization is missing.

**Value transfer.** Credit Agreement §§6.04(j), 6.05(g), 6.06(h) and the indenture's restricted-payment and asset-sale provisions supply conditional investment, disposition and distribution routes. [C15, C16, C17, C22, C23] The indenture also defines an interactive-entertainment unrestricted-subsidiary investment route. [C54] A permitted designation or disposition can remove property from the secured group; recovery access then depends on remaining liens, guarantees and proceeds application rather than consolidated asset totals. This is **theoretical permission**, not proof that an IP drop-down, priming exchange or unrestricted designation occurred. No basket usage or asset-by-entity valuation supports a dollar leakage figure.

**Guarantees and releases.** Indenture §4.11 ties new domestic restricted guarantors to borrowing or guaranteeing the CEI Credit Agreement, subject to gaming approvals. The second supplemental indenture adds guarantors including Bally's Park Place LLC. The indenture permits specified automatic collateral and guarantee releases, while adversely changing a Significant Subsidiary guarantee outside express exceptions requires 66⅔% holder consent. [C4, C24, C29, C30, C31, C48, C57] The June filing describes CEI secured facilities as guaranteed by material wholly owned domestic subsidiaries but separately says CEI does not guarantee the Caesars Virginia facilities. [C40] Neither statement supplies entity-level asset values or proves that Caesars Virginia guarantees the CEI notes.

**Defaults and amendments.** Indenture §6.01(d) uses a $400 million cross-acceleration/payment threshold; §6.02 generally permits trustee or 30% of notes to accelerate after an applicable Event of Default, subject to its Bank Indebtedness delay. Majority consent generally amends the indenture, but affected-holder payment protections and supermajority release protections qualify that rule. [C26, C27, C28, C29] The bank agreement has affected-lender protections against specified economic changes and all-lender consent for releases of substantially all collateral or guarantors outside permitted release mechanics. [C18] Analyst interpretation: majority flexibility is not carte blanche to strip sacred rights; monitor any actual waiver or collateral-release certificate.

### Structural and intercreditor read-through

The signed indenture and guarantor accessions establish obligations at CEI and named joining subsidiaries, but the collateral agreement, complete current org chart and entity-level valuations are absent. Caesars Enterprise Services is listed as unrestricted as of the notes' issue date; that historic designation must not be projected unchanged to June 2026 without a current register. [C4, C47, C49] Caesars Virginia is a distinct borrower secured on its own material assets and not guaranteed by CEI; its assets therefore cannot be included automatically in the CEI noteholders' direct collateral recovery. [C40] This is structural separation, **not** contractual subordination of the CEI notes.

The indenture refers to a First Lien Intercreditor Agreement, but its executed text is not delivered here. Its Exhibit D is a bracketed **form** of a second-lien agreement: its 180-day standstill, turnover and par purchase provisions describe only what that form would do if operative. They are **not findings about an existing junior creditor**. [C32, C33, C34, C35] No issuer-specific standstill, release voting or first-lien enforcement waterfall is concluded from the form. CP-3A/CP-4C must obtain executed documents before quantifying recoveries.

### Covenant capacity and nearest pressure point

**Exactly supportable:** documentary thresholds include the bank 6.50:1 maximum and 2.00:1 minimum maintenance tests; the indenture permits a 4.75:1 consolidated-leverage RP route and its general-lien clause (25) is the greater of $750 million and 32.5% of applicable EBITDA. [C6, C7, C22, C53] These are limits or formula components, not unused balances. **Not calculable:** current tested ratios, incremental debt before breach, the grower amount and residual RP/investment/lien capacity; legal EBITDA, netting, existing basket use and current amendment texts are missing. The issuer reports compliance, but supplies no numerical cushion. [C39, C43, C44, C45]

**Single nearest pressure point — maintenance covenant headroom:** provision: Credit Agreement §6.11; evidence: the drafted tests and reported compliance. Risk mechanism: weaker earnings or higher debt may compress the Covenant Facility cushion; an uncured failure can lead to that facility's acceleration, and cross-creditor implications depend on other instruments' triggers. Creditor impact: higher near-term refinancing/default pressure, with secondary collateral competition if new secured funding is raised. Monitoring signal: next compliance certificate, tested leverage and fixed-charge ratio, cash utilization and any cure notice. Needed to tighten view: current signed amendments, covenant EBITDA and debt/netting bridge, tested ratios and certificate. [C6, C7, C8, C9, C39]

**Strongest contrary evidence:** the filing states June 2026 financial-covenant compliance, and cash stood at $965 million; these counter an assertion of an existing covenant breach. [C39, C51] They would support materially higher conviction if certified test values show durable cushion after contractual adjustments and if entity-level liquidity is available to the liable borrowers. Meanwhile a downside sequence remains conditional: declining visitation or gaming hold first reduces operating earnings; weaker EBITDA compresses ratio headroom; cure or financing may consume liquidity or add pari claims; refinancing or secured recoveries become more exposed. Observe tested ratios, operating trends, revolver use, new first-lien designations and security releases, not an invented stress date. The May 27 merger agreement precedes the June balance sheet, but closing and its financing remain conditional and are **not** incorporated as June debt or capacity. [C46]

### Analytical appendix — complete canonical registers

#### T4.2 — Controlling Document Register
| Authority Rank | Document | Document Type | Version / Date | Status | Governing Role | Credit Relevance | Evidence ID |
|---|---|---|---|---|---|---|---|
| 1 | CEI 6.500% secured notes indenture | Executed indenture | 2024-02-06 | Executed base, read with supplements | Secured-note covenants and remedies | Governs target note | [C1] |
| 1 | First supplemental indenture | Executed supplement | 2024-03-01 | Executed; replaces two clauses | Permitted Liens (44), §8.01(b), new guarantors | Later wording controls changed clauses | [C2, C3] |
| 1 | Second supplemental indenture | Executed supplement | 2024-08-23 | Executed accession | Adds scheduled guarantors | Expands signed guarantee list | [C4, C48] |
| 1 | Incremental Assumption Agreement No. 3 and then-conformed CEI credit text | Executed amendment / attached conformed text | 2024-02-06 | Executed amendment; bank text predates listed later amendments | Bank covenant formula and incremental mechanics, historical version | Current wording must be checked against later amendments | [C5, C44, C45] |
| 2 | First Lien Intercreditor Agreement | Referenced, not delivered | Referenced in indenture | Executed text absent | Would control first-lien enforcement | No operative waterfall conclusion | [C28] |
| 2, form only | Indenture Exhibit D second-lien form | Unexecuted exhibit form | 2024 indenture exhibit | Bracketed, not proof of execution | Illustrates potential junior mechanics only | Do not apply 180 days to existing creditors | [C32, C33] |
| Reporting source, not legal rank | June 2026 Form 10-Q | Filed issuer disclosure | 2026-06-30 | Unaudited current-period filing | Reported compliance and outstanding debt | Corroboration, not substitute for covenant certificate | [C36, C39] |

#### T4.3 — Covenant Feature Register
| Topic | Provision Summary | Source / Clause | Risk Mechanic | Credit Implication | Market Norm Assessment | Evidence ID |
|---|---|---|---|---|---|---|
| Maintenance | Max 6.50:1 and min 2.00:1 from Dec 2024 for Covenant Facilities | Credit Agreement §6.11(a),(b) | Ratios can trigger facility remedies as earnings weaken | Negative — Covenant Erosion | No comparative source | [C6, C7] |
| Non-covenant tranche | Financial-test breach alone does not trigger its default absent Covenant Facility acceleration | Credit Agreement §7.01(d) | Delayed cross-tranche trigger | Negative — Refinancing Risk | No comparative source | [C8] |
| EBITDA cure/add-backs | Cash equity cure and broad optimization adjustments subject to drafted restrictions | Credit Agreement §7.02; EBITDA definition | Test EBITDA can differ from cash earnings | Negative — Covenant Erosion | No comparative source | [C9, C10] |
| Incremental/MFN | Conditional incremental amount and conditional Term B-1 yield protection | Credit Agreement §2.21 | Additional debt may dilute liens; MFN limited in scope | Negative — Leverage Increase | No comparative source | [C11, C12] |
| Ratio debt and liens | Additional debt and corresponding lien routes subject to ratio and other conditions | Credit Agreement §§6.01(r), 6.02(u); indenture §4.03(b)(i) | Pari claims can share collateral | Negative — Leverage Increase | No comparative source | [C13, C14, C20] |
| Investments / RP | General investments and conditional ratio-based distributions | Credit Agreement §§6.04(j), 6.06(h); indenture §4.04(b)(xxi) | Cash or assets leave creditor group | Negative — Liquidity Deterioration | No comparative source | [C15, C16, C22] |
| Dispositions | Asset-sale permission and 18-month proceeds application | Credit Agreement §6.05(g); indenture §4.06(b) | Reinvestment delays debt reduction | Negative — Covenant Erosion | No comparative source | [C17, C23] |
| Guarantees | Domestic CEI borrower/guarantor accession; automatic release exceptions | Indenture §§4.11, 12.04, 13.02 | Subsidiary access can change without bondholder vote in permitted transactions | Negative — Covenant Erosion | No comparative source | [C24, C30, C31] |
| Defaults / amendments | Significant cross-acceleration and specified vote protections | Indenture §§6.01(d), 6.02, 9.02 | Enforcement only after drafted triggers; protected rights constrain amendments | Neutral — Stable | No comparative source | [C26, C27, C29] |

#### T4.9 — PD vs LGD / Recovery Translation
| Legal Topic | Supported Fact | Risk Mechanic | PD Effect | LGD / Recovery Effect | Monitoring Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Covenant test | Loan max leverage and minimum coverage apply to Covenant Facilities | Cash-flow deterioration compresses tested ratios | Potential earlier covenant pressure | No immediate lien change | Obtain tested ratios and cure notices | [C6, C7, C9] |
| Pari debt | Note and loan agreements permit conditional debt and liens | More equally ranked claims can fund operations but share security | Borrowing may defer distress while raising leverage | Potential pari collateral dilution | Monitor issuance and lien designation | [C13, C14, C20, C21] |
| Transfer / release | Conditional dispositions and automatic release provisions | Disposed assets may leave collateral pool | Sale may improve liquidity | Less direct collateral, subject to proceeds treatment | Track disposal and release certificates | [C17, C23, C30] |
| Caesars Virginia | Distinct asset-secured facility without CEI guarantee | Different obligor and collateral perimeter | Entity liquidity may not fund CEI claims | No automatic direct claim on its material assets | Monitor entity debt and upstream distributions | [C40] |
| Voting | Majority amendments coexist with affected-holder and supermajority exceptions | Negotiated changes may alter covenant protection | Waiver may defer default | Collateral-release protection limits specified votes | Read filed amendments and consent notices | [C18, C28, C29] |

#### T4.10 — Market Norm Comparison
| Topic | Issuer Provision | Market / Third-Party Reference | Relative Assessment | Agreement / Discrepancy | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Incremental yield | Conditional Term B-1 MFN in §2.21(b)(viii) | [Insufficient Information] — no comparable executed peer covenant or review supplied | Comparison deferred; no market-standard assertion | Issuer provision identified, comparative evidence absent | Insufficient Information | [C12] |

Market-norm and third-party covenant-review comparison is limited because no supported comparative source was provided.

#### T4.11 — Covenant Aggressiveness Score
| Area | Score 1–5 | Evidence | Risk Mechanic | Credit Implication | Confidence | Evidence ID |
|---|---|---|---|---|---|---|
| Maintenance covenant architecture | 4 | Tests cover Covenant Facilities; non-covenant loans have qualified default transmission | Uneven lender control | Negative — Covenant Erosion | Provisional | [C6, C7, C8] |
| Debt / lien incurrence capacity | 4 | Multiple first-lien and ratio routes | Additional claims can dilute pool | Negative — Leverage Increase | Provisional | [C13, C14, C20, C21] |
| RP / investment / leakage | 4 | Investment and RP routes plus transfer permissions | Potential movement of secured value | Negative — Liquidity Deterioration | Provisional | [C15, C16, C17, C22] |
| EBITDA definitions | 4 | Broad optimization and pro forma provisions | Denominator may exceed cash earnings | Negative — Covenant Erosion | Provisional | [C10, C43] |
| Collateral / guarantor protection | 3 | Accession and supermajority protection coexist with releases | Coverage is conditional on entity status | Neutral — Stable | Provisional | [C24, C29, C30] |
| Amendment / control | 3 | Majority general vote, protected individual rights and release thresholds | Majority cannot alone change protected payment rights | Neutral — Stable | Provisional | [C18, C28, C29] |
| Overall | 4 | Highest relevant routes: incurrence, transfer and conditional maintenance | Combined leverage/recovery exposure, not arithmetic mean | Negative — Leverage Increase | Provisional | [C6, C13, C17, C20] |

**Rubric assessment:** 4/5, **provisional**, based on provision-level breadth, not calculated unused capacity or a peer-market comparison. It is weighted toward incurrence and leakage; not a formal credit rating.

#### T4.12 — Red Flags and Monitoring Triggers
| Red Flag / Trigger | Provision or Signal | Why It Matters | PD / LGD / RV Impact | Monitoring Action | Evidence ID |
|---|---|---|---|---|---|
| Certified test approaches limit | Credit Agreement §6.11 | Potential Covenant Facility acceleration | PD and refinancing risk before all tranches default | Request quarterly certificate and cure disclosure | [C6, C7, C8] |
| New pari secured borrowing | §§2.21, 6.01(r), 6.02(u); note §4.03 | Shares secured collateral | LGD/RV dilution if capacity exercised | Track debt and first-lien joinders | [C11, C13, C14, C20] |
| Restricted-to-unrestricted transfer | Investment/designation provisions | Value can move away from guarantee perimeter if conditions satisfied | Possible higher LGD | Obtain designation notices and asset detail | [C15, C49, C54] |
| Automatic release | Indenture §12.04 and bank §9.18 | Release can follow qualifying transfer | Collateral coverage can shrink | Inspect officer certificates and security releases | [C19, C30] |
| Ratings-based covenant suspension | Indenture §4.14 | Enumerated note covenants may stop applying | Incurrence/leakage control reduced | Track two-agency ratings and reversion certificate | [C25] |
| Merger terms / funding change | May 27 pending agreement | Consent/refinancing consequences depend on operative texts | PD and instrument RV uncertainty | Obtain agreement and financing documents | [C46] |

#### T4.13 — Gaps Ledger
| Gap | Missing Document / Clause / Schedule | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| G1 current bank version | Executed May and November 2024 amendments, later changes | February conformed text may not be current [C44, C45] | T4C.4–T4C.5 and loan-control conclusions provisional | Supply amendments and current conformed agreement |
| G2 capacity inputs | Certified ratios, covenant EBITDA, netting and basket tracker | Reported compliance is not numerical headroom [C39, C43] | All remaining capacity and max debt unquantified | Obtain June certificate and basket use ledger |
| G3 first-lien enforcement | Executed First Lien Intercreditor Agreement and collateral agreement | Cannot verify first-lien control/proceeds | T4F first-lien class rows qualified | Supply executed ICA/security documents |
| G4 second lien actuality | Any executed junior ICA/joinders | Indenture contains only a form [C32] | T4F form terms not operative | Obtain executed instrument or confirm none exists |
| G5 group value | Org chart, current designations, entity debt/EBITDA and pledged-asset schedules | Claims cannot be ranked by reachable value | T4D.2–T4D.5 qualitative only | Supply current group and collateral schedules |
| G6 other securities / transaction | 6% unsecured 2032 indenture and full Fertitta merger agreement | Instrument comparison and change-of-control specifics unverified [C46] | RV and merger treatment incomplete | Supply both executed texts and financing commitments |
| G7 comparative standard | Covenant-review report or executed comparable peer documents | Market-relative statement unsourced | T4.10 limited | Provide definition-aligned comparative clauses |

#### T4D.1 — Structural Source Gate Register
| Source | Status | Authority Rank | Limitations | Module Status |
|---|---|---|---|---|
| Signed base and supplemental 2032 indentures | Executed; entity names and guarantee provisions present [C1, C4, C48] | 1 | No complete current ownership or value map | Completed with Limitations |
| February 2024 loan document | Executed historic bank amendment [C5] | 1 | Later amendments and pledged-asset exhibits absent | Completed with Limitations |
| June 2026 filed disclosure | Current reporting, not executed collateral instrument [C40] | Reporting corroboration | No debtor-level asset/debt distribution | Completed with Limitations |

#### T4D.2 — Restricted / Unrestricted Entity Register
| Entity | Role | Jurisdiction | Parent | Designation | Material Value Held | Inside Credit Group? | Evidence ID |
|---|---|---|---|---|---|---|---|
| Caesars Entertainment, Inc. | Issuer/borrower | Delaware | — | Issuer | Consolidated assets not entity assets; — | Yes, primary obligor | [C1, C5] |
| Caesars Interactive Entertainment New Jersey, LLC | March 2024 joining note guarantor | New Jersey | Caesars subsidiary; immediate parent — | Guarantor accession | — | Yes for 2032 notes | [C2] |
| Tropicana Atlantic City Corp. | March 2024 joining note guarantor | New Jersey | Caesars subsidiary; immediate parent — | Guarantor accession | — | Yes for 2032 notes | [C2] |
| Bally's Park Place LLC | August 2024 joining note guarantor | New Jersey | Immediate parent — | New guarantor | — | Yes for 2032 notes | [C4, C48] |
| Caesars Enterprise Services, LLC | Named initially unrestricted subsidiary | Delaware | Immediate parent — | Unrestricted on notes issue date; June status — | — | Not initially in restricted note group | [C47] |
| Caesars Virginia, LLC | Separate facility borrower | — | Group relation not fully mapped | CEI-guarantee status: no CEI guarantee of CVA facility | Material assets secure CVA; amount by entity — | Separate CVA collateral group; CEI-note reach unverified | [C40] |

`—` denotes entity-level data absent, not zero. The guarantee accessions identify additional entities beyond these representative rows; a complete current entity-by-entity value matrix requires the current subsidiary list and asset schedule.

#### T4D.3 — Guarantor Coverage Matrix
| Entity × Tranche | Guarantee Type | Direction | Release Trigger | Evidence ID |
|---|---|---|---|---|
| Caesars Entertainment, Inc. × 2032 secured notes | Primary issuer obligation, not subsidiary guarantee | Direct | Defeasance/discharge subject to indenture | [C1, C3] |
| Caesars Interactive Entertainment New Jersey, LLC × 2032 secured notes | Joint and several note guarantee | Subsidiary to issuer | Indenture §13.02(b) conditional releases | [C2, C31] |
| Tropicana Atlantic City Corp. × 2032 secured notes | Joint and several note guarantee | Subsidiary to issuer | Indenture §13.02(b) conditional releases | [C2, C31] |
| Bally's Park Place LLC × 2032 secured notes | Joined guarantee | Subsidiary to issuer | Indenture §13.02(b) conditional releases | [C4, C48, C31] |
| Caesars Enterprise Services, LLC × 2032 secured notes | No note guarantee established by initial unrestricted listing | — | Current designation to verify | [C47] |
| Caesars Virginia, LLC × CEI 2032 secured notes | [Insufficient Information] — current CEI-note guarantee status not established by CVA facility disclosure | — | Current guarantee schedule required | [C40] |
| Caesars Entertainment, Inc. × CVA loans | Filing expressly states no CEI guarantee | No upstream CEI guarantee | — | [C40] |

#### T4D.4 — Collateral-by-Entity Matrix
| Entity × Lien | Excluded Assets | Release Mechanic | Perfection Limit | Evidence ID |
|---|---|---|---|---|
| Caesars Entertainment, Inc. × CEI first lien | Indenture-defined excluded assets; asset amounts — | Indenture §12.04 | Actual pledge/perfection schedule absent | [C30] |
| Caesars Interactive Entertainment New Jersey, LLC × CEI first lien | Asset list — | §12.04 and guarantor release | Gaming approval/perfection to verify | [C24, C30] |
| Tropicana Atlantic City Corp. × CEI first lien | Asset list — | §12.04 and guarantor release | Gaming approval/perfection to verify | [C24, C30] |
| Bally's Park Place LLC × CEI first lien | Asset list — | §12.04 and guarantor release | Gaming approval/perfection to verify | [C4, C30, C48] |
| Caesars Enterprise Services, LLC × CEI first lien | Initial unrestricted status; value — | — | No direct pledge established | [C47] |
| Caesars Virginia, LLC × CVA first lien | Exact excluded assets — | CVA documents not delivered | Filed description only | [C40] |
| Caesars Virginia, LLC × CEI first lien | Exact status — | Current CEI collateral schedule missing | No CEI security interest established here | [C40] |
| Caesars Entertainment, Inc. × second lien | — | Actual junior agreement not supplied | Form is not a grant | [C32] |

#### T4D.5 — Structural Priority Table
| Claim/Tranche | Obligor Entity | Reachable Value | Structural-Priority Label | Stranded Value Named | Recovery-Access Implication | Confidence | Evidence ID |
|---|---|---|---|---|---|---|---|
| CEI 2032 secured notes | CEI and joined guarantors | Collateral subject to exclusions; entity value — | Pari | Caesars Virginia material assets under CVA security are not automatically CEI-note collateral | Direct secured claim is limited to actual pledged group assets | Low | [C1, C4, C40] |
| CVA loans | Caesars Virginia, LLC | Its material secured assets; valuation — | Structurally Senior | CEI-guarantor assets are not claimed as CVA security in filing | CVA lenders have a direct entity claim before an indirect CEI equity residual | Low | [C40] |
| CEI unsecured 2032 notes | CEI and filing-described guarantors | Unsecured claim; entity valuation — | Insufficient Information | Material non-guarantor value cannot be quantified | Specific unsecured-indenture package not attached | Low | [C40] |

#### T4D.6 — Drop-down / Transfer Capacity Register
| Route | Entity Path | Enabling Provision (CP-4 ref) | Value Exposed | Severity 1–5 | Recovery/Priority Implication | Demonstrated vs Theoretical | Evidence ID |
|---|---|---|---|---|---|---|---|
| Investment/designation | CEI restricted subsidiary → qualifying unrestricted subsidiary | CP-4 T4.3 investments; Credit Agreement §6.04(j) and note unrestricted-investment definition | — | 4 | Potentially shifts asset outside direct guarantee reach, subject to baskets | Theoretical permission; no transaction demonstrated | [C15, C49, C54] |
| Permitted asset transfer | CEI guarantor → third party | CP-4 T4.3 dispositions; Credit Agreement §6.05(g), note §12.04 | — | 4 | Released asset replaced by proceeds subject to applicable rules | Theoretical permission | [C17, C30] |
| Dividend / buyback | CEI restricted group → shareholders | CP-4 T4.3 RP; Credit Agreement §6.06(h), note §4.04(b)(xxi) | — | 3 | Reduces retained assets/cash if used | Theoretical route; no attributed capacity usage calculated | [C16, C22] |

#### T4D.7 — Priming-Exposure Findings
| Vulnerability | Enabling Provision (CP-4 ref) | Affected Creditor Class | Demonstrated vs Theoretical | Structural Implication | Confidence | Evidence ID |
|---|---|---|---|---|---|---|
| Additional pari claims, not contractual lien priming | CP-4 T4.3 debt/lien; loan §§6.01(r), 6.02(u) | Existing CEI secured creditors | Theoretical capacity; amount uncalculated | Equal-ranking claims can dilute shared collateral proceeds | Low | [C13, C14] |
| Potential unrestricted-group drop-down | CP-4 T4.3 investments and transfer provisions | CEI secured and unsecured creditors | Theoretical; no demonstrated trapdoor exchange | Future security selection requires actual asset and entity path | Low | [C15, C17, C49] |
| Non-pro-rata uptier transaction | [Insufficient Information] — current executed ICA, credit amendments and transaction documents absent | CEI classes | Not demonstrated | Cannot label an executed uptier permission | Insufficient | [C32, C44, C45] |

#### T4D.8 — Structural Gaps Ledger
| Gap | Missing Document/Schedule/Provision | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Entity ownership and designations | Current org chart and restricted/unrestricted list | Initial listing is not current perimeter [C47] | T4D.2, T4D.5 | Obtain dated subsidiary/designation schedule |
| Per-entity collateral | Executed collateral agreement and pledge schedules | Liens and excluded-value amounts cannot be verified | T4D.4–T4D.7, CP-3A | Obtain collateral schedules/perfection evidence |
| Entity financials | Subsidiary-level assets, cash flow and debt | Stranded value unquantifiable | T4D.5 and downstream recovery | Obtain entity-level accounts |
| Current loan version | Later executed amendments [C44, C45] | Transfer and release mechanics may have changed | T4D.6–T4D.7 | Supply signed texts |

#### T4F.1 — Intercreditor Controlling Documents
| Document | Parties | Date | Governing Law | Status | Source / Locator | Evidence ID |
|---|---|---|---|---|---|---|
| Indenture reference to First Lien Intercreditor Agreement | CEI, representative and agent as defined | Original first-lien agreement referenced; executed instrument absent | [Insufficient Information] — operative ICA text not supplied | Referenced only | Indenture Article XII and Exhibit A; operative document absent | [C1, C28] |
| Exhibit D second-lien agreement | Bracketed first- and second-lien agents, borrower | Blank | Draft form specifies New York | **Form only, unexecuted** | Base indenture Exhibit D, opening | [C32] |
| 2032 secured indenture | CEI, guarantors, trustee and collateral agent | 2024-02-06 | New York | Executed | Article XI and XII; governing note duties, not replacement for ICA | [C1] |

#### T4F.2 — Creditor Class Map
| Creditor Class | Rank | Security Interest | Enforcement Rights | Voting Weight | Evidence ID |
|---|---|---|---|---|---|
| CEI 2032 secured noteholders | First-priority lien subject to actual ICA and permitted liens | Security-documents collateral | Trustee/agent remedies under indenture; actual shared-lien control unresolved | 30% acceleration; majority general amendments; specified 66⅔% protections | [C27, C28, C29] |
| CEI credit lenders | Secured; actual intercreditor priority mechanics unresolved | CEI collateral package subject to exclusions | Administrative/collateral agent under bank documents; first-lien ICA absent | Required-lender and affected-lender distinctions | [C18] |
| Hypothetical second-priority creditors | No existing class established | Form describes junior Common Collateral | **Only if a second-lien agreement is executed** | [Insufficient Information] — executed junior class and voting provisions not supplied | [C32, C33] |

#### T4F.3 — Enforcement Control
| Provision | Standstill Period | Trigger | Who Controls Enforcement | Creditor Class Affected | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|
| Executed first-lien ICA | [Insufficient Information] — operative text absent | — | [Insufficient Information] — executed enforcement direction absent | CEI first-lien classes | Cannot determine which representative instructs collateral agent in shared enforcement | Recovery-control conclusion deferred | [C28] |
| Exhibit D form §3.1(a) | 180 days **in form only**; starts after junior default and written intent notice; exceptions/expiry depend on senior pursuit, insolvency and rescission | Form's second-priority default, due principal and written notice | Senior creditors until form's conditional expiry | Hypothetical second lien | Standstill can delay junior remedies if later adopted | No existing issuer junior standstill established | [C32, C33] |
| Indenture §6.02 | Bank-debt delay up to five Business Days after required notices, subject to earlier bank acceleration | Continuing qualifying note Event of Default | Trustee or holders of at least 30% declare note acceleration | Noteholders | Payment acceleration is distinct from collateral enforcement control | Monitor bank and trustee notices | [C27] |

#### T4F.4 — Turnover, Release and Purchase Options
| Provision | Turnover Obligation | Release Authority | Purchase Option | Conditions | Countervailing Evidence | Evidence ID |
|---|---|---|---|---|---|---|
| Exhibit D form §§4.2, 5.1, 5.8 | Form directs junior recoveries on Common Collateral to first-lien agent | Form links junior release to senior release | Form offers whole senior claim purchase at defined price | Operates only if completed/executed; no such execution established | Bracketed parties and blank date prevent current-class assertion | [C32, C34, C35] |
| Executed note indenture §§9.02, 12.04 | [Insufficient Information] — executed first-lien proceeds waterfall absent | Contractually specified automatic releases; 66⅔% for adverse Significant Subsidiary guarantee amendment outside exceptions | — | Permitted transaction or required votes | Affected-holder rights and release thresholds remain protections | [C29, C30, C57] |

#### T4F.5 — Recovery Control Assessment
| Creditor Class | Realised-Recovery Mechanic | Control Weakness | Severity | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|
| CEI secured notes | Shared collateral proceeds depend on executed security/ICA | First-lien control text absent | High | Pari issuance may dilute pro rata claim; enforcement direction unresolved | Qualitative recovery comparison only | [C20, C21, C28] |
| CEI bank lenders | Agent-directed remedies described in bank text | Later amendments and executed ICA absent | High | Assumed control hierarchy would overstate certainty | Obtain operative documents before class waterfall | [C18, C44, C45] |
| Potential junior creditors | Form would subordinate lien and delay remedies | No executed junior class evidenced | Insufficient Information | Form-only standstill/turnover cannot be applied | No recovery estimate or binding junior-control finding | [C32, C33, C34] |

#### T4F.6 — Intercreditor Gaps Ledger
| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| First-lien allocation | Signed First Lien Intercreditor Agreement and joinders | Controls class directions, releases and proceeds | T4F.2–T4F.5 first-lien precision | Obtain signed agreement and amendments |
| Junior agreement status | Executed second-lien ICA, if any | Form cannot bind creditors [C32] | 180-day and turnover rows illustrative only | Verify execution and classes |
| Security perfection | Collateral agreement and security schedules | Determines Common Collateral in practice | No issuer-specific recovery percentage | Obtain schedules for CP-3A/CP-4C |

#### T4C.2 — Controlling Capacity Source Map
| Authority Rank | Source | Source Type | Version / Date | Status | Controls Legal Formula / Financial Input / Usage | Credit Relevance | Evidence ID |
|---|---|---|---|---|---|---|---|
| 1 | Credit Agreement in incremental exhibit | Executed amendment; conformed credit text | 2024-02-06 | Later amendments absent | Historical formula only; no June usage | Test and basket mechanics subject to version verification | [C5, C44, C45] |
| 1 | Secured-note indenture plus two supplements | Executed documents | 2024-02-06 / 03-01 / 08-23 | Linked legal family | Note formula; no usage | March replacement controls amended definitions | [C1, C2, C3, C4] |
| Reporting | June 2026 10-Q | Filed interim report | 2026-06-30 | Unaudited | Reported debt and qualitative compliance; not basket use | Current reported inputs do not establish legal ratios | [C36, C39] |
| — | Compliance certificate and basket tracker | Absent | June 2026 | Missing | [Insufficient Information] — tested values and historical utilization not supplied | Prevents remaining-capacity computation | [C39] |

#### T4C.3 — Covenant Definition and Ratio Mechanics Register
| Definition / Ratio | Source / Clause | Formula / Definition Summary | Required Inputs | Capacity Effect | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|
| Total leverage maintenance | Bank §6.11(a), definitions of Total Net Debt/EBITDA | Contractual net debt ÷ covenant EBITDA; max 6.50:1 | Tested debt, permitted cash, EBITDA and amendments | Headroom undetermined | Reported cash and book debt are not certificate inputs | Negative — Covenant Erosion | [C6, C37] |
| Fixed charge coverage | Bank §6.11(b), Fixed Charge Coverage Ratio | Contract EBITDA ÷ defined fixed charges; min 2.00:1 | Covenant EBITDA, eligible charges, pro forma changes | Headroom undetermined | Lease/interest definitions differ from cash interest disclosure | Negative — Covenant Erosion | [C7, C43] |
| Grower and pari debt | Indenture §4.03(b)(i), Permitted Liens (6), (25); bank §§2.21, 6.01(r) | Fixed, grower and ratio alternatives | Contract EBITDA, net secured debt, usage | Largest numeric cap cannot be inferred from reported EBITDA | Pari claims dilute liens | Negative — Leverage Increase | [C11, C13, C20, C21, C53] |
| Contract liabilities outside ordinary debt ratio | Note Indebtedness definition; filed customer-contract note | Customer advance/service obligations are not automatically borrowed-money principal | $545m customer deposits; liability classification and contractual definition | Debt ratio may omit funding float; legal inclusion must be verified transaction by transaction | Refund or performance can demand liquidity despite ratio exclusion | Negative — Liquidity Deterioration | [C41, C42] |
| Unrestricted perimeter | Bank Unrestricted Subsidiary definition; note investment definition | Designation subject to legal conditions | Current designation, value, RP/investment usage | Potential transfer capacity unquantified | Assets can leave restricted-group reach | Negative — Covenant Erosion | [C49, C54] |

#### T4C.4 — Headroom Table
| Test | Test Type | Threshold | Current Basis | Formula | Headroom | Status | Limitation | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|---|---|---|
| Bank total leverage | Maximum ratio | 6.50:1 from Dec 2024 | Qualitative reported compliance, tested ratio undisclosed | 6.50 − actual tested leverage | [Insufficient Information] — missing certified June tested ratio and covenant debt/EBITDA bridge | Insufficient Information | Current later-amended terms also needed | Reduced EBITDA may compress cushion | Negative — Covenant Erosion | [C6, C38, C39, C44, C45] |
| Bank fixed-charge coverage | Minimum ratio | 2.00:1 from Dec 2024 | Qualitative reported compliance, tested coverage undisclosed | Actual tested coverage − 2.00 | [Insufficient Information] — missing certified coverage numerator and fixed-charge denominator | Insufficient Information | No compliant source bridge | Cash charges may outrun earnings | Negative — Covenant Erosion | [C7, C39] |
| Note ratio incurrence | Incurrence max ratio | Contract-specific first-lien threshold under Permitted Liens (6) | No pro forma secured test supplied | Applicable ceiling − pro forma legal leverage | [Insufficient Information] — missing tested debt, cash, covenant EBITDA and proposed transaction | Formula Extracted Only | Incurrence test is not a maintenance test | New pari issuance may dilute collateral | Negative — Leverage Increase | [C21] |

#### T4C.5 — Capacity Register
| Capacity Type | Basket / Test | Formula | Conditions | Current Input | Usage | Estimated Capacity | Remaining Capacity | Status | Severity | Risk Mechanic | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Debt incurrence capacity | Bank §6.01(r) | Pro forma applicable leverage or coverage alternative | No applicable Event of Default; debt terms and ratio requirements | Covenant EBITDA and debt absent | — | — | — | Formula Extracted Only | High | Additional borrowing raises leverage | Negative — Leverage Increase | [C13] |
| Incremental facility capacity | Bank §2.21 Incremental Amount | Greater of fixed amount / EBITDA-based component plus drafted ratio and replenishment components | Incremental agreement conditions and MFN scope | Reported EBITDA is non-contractual | — | — | — | Formula Extracted Only | High | Pari term debt may dilute security | Negative — Leverage Increase | [C11, C12, C43] |
| Lien capacity | Indenture Permitted Liens (25) | Greater of $750m and 32.5% of covenant EBITDA, less qualifying outstanding use | Permitted underlying obligation | Applicable EBITDA absent | — | — | — | Formula Extracted Only | High | Other secured claims erode collateral coverage | Negative — Leverage Increase | [C53] |
| Restricted payment capacity | Bank §6.06(h); note §4.04(b)(xxi) | Ratio-based distribution if contractual total leverage ≤4.75:1 under respective definitions | No Event of Default and pro forma test | Actual legal ratio absent | — | — | — | Formula Extracted Only | High | Cash leaves credit group | Negative — Liquidity Deterioration | [C16, C22] |
| Investment capacity | Bank §6.04(j) | Greater of $975m and 0.425× defined EBITDA plus elective cumulative-credit component | Classification and returns rules | Applicable EBITDA and builder amount absent | — | — | — | Formula Extracted Only | High | Potential non-guarantor transfers | Negative — Covenant Erosion | [C15] |
| Asset transfer capacity | Bank §6.05(g); note §4.06 | Fair value, cash consideration and proceeds application requirements | Transaction-specific thresholds and reinvestment conditions | No proposed asset/value | — | — | — | Formula Extracted Only | High | Release and reinvestment can change pool | Negative — Covenant Erosion | [C17, C23] |
| Guarantor / collateral release capacity | Note §§12.04, 13.02; bank §9.18 | Automatic on specified permitted events | Asset/entity facts and release conditions | Pledged schedule absent | — | — | — | Formula Extracted Only | High | Direct claim can disappear at sold entity | Negative — Covenant Erosion | [C19, C30, C31] |
| MFN protection | Bank §2.21(b)(viii) | Term B-1 repricing protection within qualifying incremental fact pattern | Size, time, maturity, security and pricing conditions | No proposed qualifying issuance | — | — | — | Formula Extracted Only | Moderate | Economic protection is conditional | Negative — Refinancing Risk | [C12] |

**No aggregation:** §2.21 and §6.01(r) may overlap, debt needs a permitted lien, and RP/investment routes may share builder components. No listed cap is assumed unused.

#### T4C.6 — Debt, Lien and Priming Capacity Analysis
| Route | Supported Legal Capacity | Current Calculation Status | Priming / Dilution Mechanic | PD Effect | LGD / Recovery Effect | RV / Security Selection Effect | Evidence ID |
|---|---|---|---|---|---|---|---|
| CEI pari first lien | Bank §§6.01(r), 6.02(u); note §4.03(b)(i), lien (6) | Formula only; later bank amendments unresolved | Additional same-rank claims share pledged assets; not proof of priming | Can fund refinancing while adding debt service | Potential equal-priority dilution | Require issue amount and ICA waterfall before preferring secured note | [C13, C14, C20, C21] |
| General secured obligation | Note Permitted Liens (25) | Fixed/grower formula only; usage absent | Additional lien claims against eligible assets | Incremental financing may defer cash stress | Recovery pool shared or otherwise encumbered depending on rank | Do not assume all $750m unused | [C53] |
| Incremental MFN | Bank §2.21(b)(viii) | Applicability to future deal unknown | Protects term-loan yield only in qualifying window | Less direct default effect | Not lien-ranking protection | Examine relative TLB-1 economics separately from note recovery | [C12] |

#### T4C.7 — RP, Investment, Asset Transfer and Leakage Analysis
| Leakage Route | Supported Fact | Formula / Basket | Usage / Remaining Capacity | Restricted-Group / Collateral Impact | Severity | Credit Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Shareholder distribution | Conditional ratio RP clauses | Legal 4.75:1 routes use distinct drafted definitions | [Insufficient Information] — utilization and certified legal ratio absent | Cash outside restricted group after payment | High | Negative — Liquidity Deterioration | [C16, C22] |
| Investment in other entity | General investment provision and unrestricted definition | Greater-of grower plus specified cumulative-credit election | [Insufficient Information] — EBITDA, builder and use absent | Possible migration beyond CEI-guarantor direct claim | High | Negative — Covenant Erosion | [C15, C49] |
| Asset sale and release | Conditional sales and note proceeds reinvestment | Transaction fair value/cash and 18-month application | [Insufficient Information] — asset-level sale and proceeds history absent | Eligible disposed collateral automatically released | High | Negative — Covenant Erosion | [C17, C23, C30] |

#### T4C.8 — EBITDA Add-Back and Capacity Inflation Analysis
| Add-Back / Definition Feature | Source / Clause | Cap / Condition | Calculation Status | Capacity Inflation Mechanic | PD / LGD / RV Implication | Evidence ID |
|---|---|---|---|---|---|---|
| Optimization / restructuring | Credit Agreement EBITDA definition | Identified categories expected within 24 months; qualifying amounts and documentation unprovided | Formula only | Higher covenant EBITDA reduces leverage and grows EBITDA-linked baskets | Can mask cash strain while permitting additional debt | [C10] |
| Pro forma ratios | Credit Agreement ratio and incremental provisions | Defined pro forma transaction conditions | Formula only | Acquisition/operating adjustments alter denominator | Secured dilution risk cannot be quantified from issuer Adjusted EBITDA | [C11, C13, C43] |
| Issuer Adjusted EBITDA mismatch | Q2 filing non-GAAP disclaimer | Not legal testing metric without reconciliation | Bridge absent | Reported non-GAAP EBITDA cannot substitute for contractual EBITDA | Uncertain covenant headroom and RV comparison | [C43] |

#### T4C.9 — Leakage and Basket Flags
| Flag | Supported Fact | Creditor Risk | Severity | Confidence | Downstream Module | Evidence ID |
|---|---|---|---|---|---|---|
| Shared / reclassified capacity | Multiple incremental, debt and lien routes | Double-counting would overstate new pari borrowing room | High | Formula Only | CP-3C, CP-6 | [C11, C13, C14] |
| Missing use | Formula does not prove unused basket | Cannot state remaining leakage | High | Formula Only | CP-3A, CP-6A | [C15, C53] |
| Releases | Specified automatic collateral/guarantor removal | Recovery reach may narrow after eligible transaction | High | Formula Only | CP-3A, CP-4C | [C19, C30, C31] |
| Funding float | Customer contract liabilities have settlement/service obligations | Operational withdrawal can draw cash without added contractual debt | Moderate | Moderate | CP-2, CP-6 | [C41, C42] |

#### T4C.11 — Capacity Risk Prioritization Matrix
| Priority | Capacity Item | Severity | Confidence | Primary Risk Mechanic | PD Effect | LGD / Recovery Effect | Monitoring Action | Evidence ID |
|---|---|---|---|---|---|---|---|---|
| 1 | Bank maintenance tests; headroom unknown | High | Formula Only | A deterioration may trigger Covenant Facility remedy | Earlier refinancing/default pressure | Indirect through acceleration | Obtain tested certificate and cure status | [C6, C7, C8, C39] |
| 2 | Additional pari secured debt | High | Formula Only | More first-lien claims on shared assets | Higher future debt service | Existing secured recovery diluted | Track first-lien issuance and joinders | [C13, C14, C20] |
| 3 | Investment plus automatic release | High | Formula Only | Qualifying transfer removes direct collateral reach | Liquidity may shrink | Stranded or substituted value | Track entity transfers and pledged-asset releases | [C15, C17, C30] |

#### T4C.12 — Capacity Gaps Ledger
| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Tested headroom | June maintenance compliance calculation and EBITDA bridge | No exact ratio distance [C39, C43] | T4C.4 and pressure-point magnitude | Request signed quarterly certificate |
| Basket use | Utilization/return history, restricted group asset transfers | Caps are not unused balances | T4C.5–T4C.7 and CP-6A | Obtain basket ledger |
| Later agreement version | Executed fourth/fifth bank amendments [C44, C45] | 2024 conformed mechanics potentially superseded | Current legal formula status provisional | Supply signed amendments |
| Contractual perimeter | Current org chart and security agreement | Non-guarantor asset reach unknown | CP-3A and CP-4C | Obtain schedules and executed ICA |

### Overall legal and capacity view

Overall, Caesars presents a **provisionally 4/5 creditor-adverse covenant architecture** on the supplied secured-note and historically conformed bank texts, rather than on verified current unused capacity. The chief protections are subsidiary accessions, specified supermajority/affected-holder rights and conditional loan maintenance tests. The main weaknesses are multiple conditional debt/lien routes, transfers with automatic security releases and a financial-test default that does not directly bind Non-Covenant Facilities. [C6, C8, C13, C17, C24, C29, C30] The primary PD route is maintenance deterioration followed by Covenant Facility acceleration and refinancing stress; the primary LGD route is additional equal-priority claims or eligible value transfer. The first-lien collateral-control and current bank-amendment gaps prevent a fully resolved secured-versus-unsecured selection. CP-4 Completed with Limitations. Covenant Aggressiveness: **4/5 provisional**. Key gaps: certified ratios, usage, executed ICA/security documents, current bank amendments.

Overall, Caesars has **limited covenant-capacity visibility**. The single nearest pressure point is the maintenance covenant because its trigger can arrive before a note payment default, but **exact headroom is not supported**. The largest stated general-lien and investment basket formulas are not additive or proven unused. Obtaining signed current agreements, legal EBITDA and a utilization certificate is the gating action before CP-3A/CP-4C recovery or CP-6A sizing. CP-4A Completed with Limitations. Key Gaps: current certified ratios, basket usage and current bank amendments.

**Structural handoff:** to CP-3A, only qualitative reachable-entity distinctions, not collateral valuation; to CP-6, challenge the conditional transfer/release route; to the capacity phase, do not net Caesars Virginia assets into CEI-note collateral or treat an issue-date unrestricted list as current. **Intercreditor handoff:** obtain the executed first-lien ICA; the 180-day junior provision remains a form-only scenario. [C32, C33, C40, C47]

## Evidence Trace

| Claim cluster | Citation marker | Document | Page / locator |
|---|---|---|---|
| Operative note base and supplements | [C1, C2, C3, C4] | 2032 indenture; first and second supplements | Base p.3; first p.1; second p.1 |
| Bank maintenance, cure and non-covenant effect | [C5, C6, C7, C8, C9] | Incremental No. 3 / conformed bank text | pp.1, 58–59; §§6.11, 7.01, 7.02 |
| EBITDA, debt and lien routes | [C10, C11, C12, C13, C14, C20, C21, C53] | Bank text; note indenture | Bank pp.16, 20, 43, 51, 53; notes pp.13–14, 22 |
| Leakage and releases | [C15, C16, C17, C19, C22, C23, C30, C31, C54] | Bank text; note indenture | Bank pp.54–56, 65; notes pp.10, 24–25, 34–35 |
| Defaults, voting and security safeguards | [C18, C24, C25, C26, C27, C28, C29, C57] | Bank text; note indenture | Bank p.63; notes pp.27–28, 32 |
| Form-only junior mechanics | [C32, C33, C34, C35] | Indenture Exhibit D | pp.49, 52–54 |
| Financial/current reporting and perimeter | [C36, C37, C38, C39, C40, C41, C42, C43, C51] | June 2026 10-Q | pp.2, 9–11, 21–22 |
| Version, entities and pending deal | [C44, C45, C46, C47, C48, C49] | 2025 10-K; June 10-Q; indenture; supplement; bank text | pp.56, 5, 60, 5, 18, 32 respectively |

## Source Registry

The source gate accepts executed indenture, two signed supplements and the February 2024 bank incremental document, but not the bracketed intercreditor form as an operative ICA. June 2026 disclosure is used for current reporting and qualitative compliance, not as proof of unused baskets. The 2025 filing identifies later credit amendments without delivering their text; this is a **version gap**, not authorization to infer their contents. [C1, C2, C3, C4, C5, C32, C39, C44, C45] March 2024 §8.01(b) replacement controls the base defeasance wording; defeasance still requires the applicable deposit and additional conditions, not simply borrower election. [C3, C52] The separately issued 6% unsecured 2032 indenture, full merger agreement, current certificates and original security/ICA instruments are not in the delivered pack. Source delivery of the long bank exhibit is a page map, so withheld lines cannot support a further current-term inference.

## Gaps & Conflicts

**CF-1 — debt measurement, not a reconciliation by assertion:** the June debt note reports $11,807 million face principal and $11,705 million note book value; the balance sheet reports $114 million current and $11,585 million long-term debt, or $11,699 million on the accepted CP-1 carrying-value basis. Face exceeds canonical by $108 million and note book exceeds it by $6 million; these have different accounting roles. Covenant debt is bespoke and cannot be assigned any of those values without the certified legal bridge. [C36, C37]

**CF-2 — EBITDA:** CP-1 carries issuer LTM Adjusted EBITDA $3,592 million, but the issuer warns that its definition can differ from debt agreements; covenant EBITDA cannot be inferred from that figure. [C43] **CF-3 — original versus supplement:** the March supplement replaces base §8.01(b), so the amended sequence is the working note provision, subject to original-document verification. [C3] **CF-4 — dated loan event:** the 2024 incremental commitment of $2.9 billion was an issuance commitment, whereas the June 2026 filing reports $2,835 million principal and $2,808 million book value for Term B-1; none is unused incremental capacity. [C5, C36] **Funding float:** June customer deposits and other deferred revenue were $545 million versus $492 million at the prior year-end; the promise to settle wagers or deliver future services can reverse cash funding even while that liability is not ordinary interest-bearing borrowed money. The indebtedness-definition treatment requires a current instrument and transaction-level check. [C41, C42]

**Open research questions, bounded:** actual tested ratios and add-back bridge; signed later credit amendments; complete group/security schedules; executed first-lien ICA and any junior ICA; the 6% unsecured note indenture; and merger financing/change-of-control documents. Without a delivered research brief or retrieval, these remain requests in T4.13, T4D.8, T4F.6 and T4C.12 rather than assumed facts. The May 2026 merger agreement is an in-quarter event; any closing after June 30 is not a June financial adjustment. [C44, C45, C46]

## QA Validation

| Self-check | Result | Basis / disposition |
|---|---|---|
| Identity and upstream | PASS locally | Pinned CP-0/CP-1 run, entity, period and hash retained without modifying host-owned fields. |
| Legal-source authority | RESTRICTED | Executed note family available; later bank amendments and operative ICAs absent; form distinguished from execution. |
| Numeric / null discipline | PASS locally | Documentary thresholds separated from uncalculated headroom; no missing usage treated as zero; finance obligations not inserted into contractual debt. |
| Structural / intercreditor distinction | RESTRICTED | Entity values and executed first-lien control unavailable; hypothetical 180-day form not asserted operative. |
| Required registers | PASS locally | T4.2, T4.3, T4.9–T4.13, T4D.1–T4D.8, T4F.1–T4F.6 and T4C.2–T4C.9/T4C.11–T4C.12 included. |
| Citation and status self-check | PASS locally | Claim-linked evidence markers and declared limitations; 52/Low, Restricted, Requires More Work. |
| Host validation | PENDING | Host completeness and handoff validation follow this answer; no script result or export confirmation claimed. |

**Next use:** CP-3 security-aware relative value only with the qualified legal perimeter; provide current signed amendments, compliance calculations and intercreditor/security documents before upgrading covenant headroom or recovery conclusions.