---
module_id: "CP-3C"
module_name: "RefinancingLMERisk"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-3C-4cc0267c48aadc70"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-15-CP-3C"
credit_os_invocation_sha256: "234dae153cb05d2a8dac83f3f748e986ea00ff2cf03cd5a9b1cc909db2b07bba"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
  - module_id: "CP-1A"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "6a269cb32ad5fd9b711677aaf183c2d1a6c81017a92b0233107694e1bc9dfca8"
  - module_id: "CP-2A"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "3bc62cc745eea3248e6a76af0f4c1a98c3c566c4d65ece793c77ed7f324ba689"
  - module_id: "CP-4"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "a766da2b5399d0627ac2aeee835f1a4026aad4c21daa128e4f78e16949aaccba"
  - module_id: "CP-2D"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "01a3ee1272c2966c991c7a9c33b7b90debe3b32c302c08cd2a5bd669682a64b0"
  - module_id: "CP-3D"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "3b4e0bf5986fa15992ed14d27a7113ddce61ea99d27ed406d1eb2f8c86da516a"
confidence_score: 55
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags:
  - SOURCE_LIMITED_NOT_COMMITTEE_READY
  - NO_POST_Q2_2026_FINANCIALS
  - CURRENT_COVENANT_HEADROOM_NOT_DISCLOSED
  - FULL_CREDIT_AGREEMENT_AND_COLLATERAL_PACKAGE_NOT_AVAILABLE
  - CURRENT_MARKET_DATA_NOT_IN_DIRECT_EVIDENCE_SET
validation_warnings:
  - FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED
  - JUNE_30_2026_FINANCIAL_BASELINE
  - MARKET_ACCESS_NOT_ESTABLISHED_BY_LAST_TRADE_SUMMARIES
  - HOST_VALIDATION_PENDING
downstream_consumers: [CP-4, CP-6, CP-3A, CP-3B, CP-5, CP-5A]
---

## Audit Summary

**Canonical filename:** `CZR_CP-3C_20261002.md`. **Status:** Ready with Limitations; `qa_status: Restricted`; confidence **55/100, Low**; committee status **Requires More Work**. Debt and maturity data are available, so the module is not blocked. The June 30, 2026 debt table reports $11.699 billion of balance-sheet carrying debt, distinct from $11.807 billion face principal. [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11] The nearest final maturities are the CEI Term Loan A and revolving facility in January 2028; these are about 16 months after the balance-sheet date, while scheduled amortization and debt service occur earlier. [C1, C2, C12, C13, C22, C23] Reported cash and capacity provide a meaningful starting buffer, but no complete 12-month forecast, current legal-capacity calculation, sponsor-willingness evidence or direct market data is available. Accordingly, ordinary refinancing is the most credible path, while coercive LME vulnerability is assessed Low, not zero.

## Analysis

### Liquidity view

The June 30, 2026 carrying-value maturity wall is concentrated in 2028–2032, not within the next 12 months. The largest final-maturity clusters are $732 million in 2028, $1.565 billion in 2029, $3.980 billion in 2030, $2.808 billion in 2031 and $2.575 billion in 2032. [C1, C2, C3, C4, C5, C6, C7, C8, C9] Scheduled debt service includes principal and interest before final maturities; for the remainder of 2026, the issuer estimates $425 million of total debt service. [C12, C13] Cash plus reported borrowing capacity was $2.928 billion, and H1 operating cash flow was $675 million. [C14, C15, C16, C18] These facts support refinancing runway, but not a complete 12-month funding-gap result. The 2024 Term B/B-1 repricing shows prior amendment execution; it does not evidence present distressed-LME intent. [C29, C30, C31, C32]

| Decision driver | Current evidence | Risk mechanic | Creditor implication | Confidence |
|---|---|---|---|---|
| Maturity pressure | Jan. 2028 RCF/TLA; largest final wall is 2030–2032. [C1, C2, C4, C5, C6, C7, C9] | Time allows preparation, but 2028 refinancing must address both drawn debt and facility renewal. | Medium pressure over 12–18 months; no final maturity inside the next 12 months. | Medium |
| Liquidity / operating cash | June cash and capacity $2.928bn; H1 CFO $675m. [C14, C15, C16, C18] | Available capacity and positive cash generation cushion obligations, but figures are dated and the forward cash bridge is incomplete. | Near-term buffer is meaningful; full-horizon sufficiency not established. | Medium |
| Legal flexibility | Partial historical credit-agreement material and executed amendments; full current agreement, security package and ICA are absent. [C29, C30, C32, C37] | Current unused capacity and ability to execute priming or non-pro-rata transactions cannot be established. | Do not infer remaining basket capacity or a feasible priming transaction. | Low |
| Market access | No direct current market quote, spread, curve or primary refinancing terms are in the delivered evidence. | Refinancing cost and investor appetite cannot be measured from the available direct evidence. | Consensual refinancing is plausible but not market-verified. | Low |
| LME vulnerability | No supported evidence of sponsor willingness to coerce creditors; the 2024 amendments document a historical repricing process. [C29, C30, C31, C32] | No combined evidence of acute pressure, current coercive legal capacity and willingness. | Low LME vulnerability; monitor legal usage and transaction developments. | Low |

#### Maturity wall and refinancing pressure

T3D.2 uses carrying values, not face principal. The June 30 balance sheet reports current debt of $114 million and long-term debt of $11.585 billion, totaling $11.699 billion; the debt note separately reports total debt of $11.807 billion face and $11.705 billion book. [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11] Facility carrying values are allocated to the instrument rows, with the $6 million RCF deferred finance charge deducted so the schedule reconciles to balance-sheet carrying debt. Face-value and carrying-value differences are retained in CF-1; the refinancing need at maturity should be considered using principal due, not carrying value.

The annual schedule reports $805 million of principal maturities in 2028 and $864 million of total debt service in 2027. These are scheduled-payment figures, not a replacement for the instrument final-maturity wall; the schedule includes contractual maturities and scheduled repayments. [C12, C13] The CEI RCF and Term Loan A are stated to mature January 31, 2028. [C22, C23] The credit-agreement excerpt defines the revolving facility maturity as the earlier of January 31, 2028 or a date 91 days before specified debt maturities. The excerpt is partial and historical; current operation of any springing trigger must be confirmed against the full current agreement. [C37]

**Subsequent-event scan:** the Q2 filing identifies the Alberta digital launch on July 13, 2026, but no subsequent refinancing, debt exchange, amend-and-extend, debt buyback or LME transaction is identified in the delivered evidence. This is a source-bounded observation, not confirmation that no later event occurred. [C33] The 2024 Term B/B-1 repricing occurred before the June 30, 2026 balance-sheet date and is not a subsequent event to that balance sheet. [C29, C30]

#### Liquidity, FCF and market access

June 30 cash was $965 million, with $96 million of restricted cash excluded from accessible liquidity. [C16, C17] The issuer reported $2.928 billion total cash and borrowing capacity; its reported components yield approximately $1.963 billion of available revolver capacity after listed letters of credit, reserves and regulatory commitments. [C14] H1 2026 operating cash flow was $675 million; PP&E purchases were $335 million, so CFO less PP&E purchases is a $340 million historical proxy only. It is not issuer-reported FCF and excludes interest, rent, taxes, other investing, debt principal and working capital. [C15, C18]

The FY2025 filing reported $11.9 billion of indebtedness and estimated $1.4 billion of VICI/GLPI rent for 2026. [C26] At June 30, the issuer reported $6.0 billion of long-term variable-rate borrowings. [C27] The company reported covenant compliance at June 30, but no tested ratio or covenant headroom is provided. [C28, C35] The accepted CP-2D handoff also identifies the absence of a complete 12-month cash-flow bridge; that is retained as a limitation, not treated as evidence of current distress.

Direct current market evidence is not present in the permitted source set. The accepted CP-3D handoff is Restricted and describes last-trade-only data without executable quotes, benchmark curves or matched security analysis; it is contextual, not a replacement for direct market evidence. Thus refinancing market access, current price and spread are **Insufficient Information**.

#### Legal capacity for LME

The executed Fifth Amendment reduced Term B and Term B-1 margins and amended repricing/assignment mechanics. [C29, C30, C31, C32] The stated 1.00% premium applied to specified yield-reduction transactions within six months of the November 25, 2024 effective date; that window had expired by May 2025. [C30] These are historical contractual terms, not evidence that the same protection remained live in October 2026 or that Caesars intended a coercive transaction.

The partial incremental-agreement excerpt describes a yield-differential protection for certain qualifying Term B-1-related loans, but it is not a complete current conformed credit agreement. [C32] The FY2025 filing summarizes negative covenants over debt, investments, restricted payments, liens, asset sales and acquisitions; the Q2 filing reports June 30 compliance with applicable financial covenants but not basket usage or headroom. [C28, C35] Accordingly, exact capacity is Unclear for most LME indicators. No current basket availability, uptier route, drop-down capacity or intercreditor result is inferred.

#### Sponsor / governance willingness

CP-2C is not an accepted upstream artifact in this run. The delivered issuer filings describe the pending Fertitta transaction, but do not establish a willingness to support Caesars’ existing debt or to pursue an LME. The Parent Guarantor’s guarantee covers Parent and Merger Sub obligations under the merger agreement; it is not an equity injection or a guarantee of CEI debt. [C33, C34] The 2024 repricing is evidence of ordinary amendment execution, not distressed creditor coercion. [C29, C30, C31] Sponsor willingness is therefore **Insufficient Information**.

#### Refinancing path, creditor classes and trigger

The most credible path is consensual refinancing or replacement of the RCF and Term Loan A ahead of January 2028, supported by the reported June liquidity and positive H1 operating cash generation, subject to updated liquidity, covenant and market evidence. [C14, C15, C18, C22, C23] The most adverse creditor path is hypothetical priming or non-pro-rata exchange; its current legal feasibility cannot be established without the complete current agreement and intercreditor package. Senior unsecured creditors would be more exposed than first-lien creditors to a hypothetical collateral-priming event, but no specific transaction or recovery impairment is evidenced. [C34, C37] The top trigger is the next update to 2028 facility refinancing, availability and covenant compliance, alongside any new debt/lien, asset-transfer or amendment disclosure.

### Analytical appendix — complete canonical registers

#### T3D.1 — Source Register

| source_document_id | source_document_name | source_quality | period / date | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Entertainment, Inc. Q2 2026 Form 10-Q | Primary-Verified; filed, unaudited interim | June 30, 2026 | Caesars and consolidated subsidiaries | Facility face/book debt, maturities, cash, liquidity, debt service, covenant-compliance statement and merger status. [C1-C28, C33, C35] | No post-June financials; no full forecast or covenant headroom. | Debt schedule, liquidity and monitoring. |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars Entertainment, Inc. FY2025 Form 10-K | Primary-Verified; filed, audited statements | December 31, 2025 | Caesars and consolidated subsidiaries | Debt/lease burden, annual liquidity characterization and secured-guarantor summary. [C26, C34] | Historical; not a current cash/debt schedule. | Historical cross-check, debt structure and counterargument. |
| 41868018-6353-4359-b98f-d9d5d6d11715 | Fifth Amendment to Credit Agreement | Primary-Verified; executed amendment | November 25, 2024 | CEI borrower and Term B / Term B-1 lenders | Pricing, repricing premium, consent and replacement-lender mechanics. [C29-C31] | Amendment only; not the complete current credit agreement. | Historical refinancing behavior and limited legal mechanics. |
| e24bf84e-82d3-4167-bd6f-f510b21fdd0e | Fourth Amendment to Credit Agreement | Primary-Verified; executed amendment | May 9, 2024 | CEI borrower and Term B lenders | Prior Term B repricing and repricing premium provisions. | Predecessor amendment; no current capacity or market conclusion. | Historical refinancing context. |
| 51624212-915e-4c48-b500-9ecdd27a1efc | Incremental Assumption Agreement No. 3 and attached credit-agreement excerpt | Primary-Verified document excerpt; incomplete conformed material | February 6, 2024; excerpted credit-agreement terms | CEI and Term B-1 financing parties | Incremental debt, maturity and yield-protection mechanics in attached agreement text. [C32, C37] | Partial and not current full agreement; exact present capacity unknown. | Historical legal-capacity indicators only. |
| CP-0, CP-1, CP-1A, CP-2A, CP-2D, CP-3D accepted artifacts | Same-run accepted upstream context | Restricted upstream context | Q2 2026; analysis date October 2, 2026 | CZR | Period, definitions, liquidity limitations, operating downside, market limitations and source readiness. | Context only; not substituted for primary evidence. | Re-anchor and carry limitations. |

#### T3D.2 — Maturity Wall Register

| Instrument | Amount | Currency | Maturity Date | Years to Maturity | Seniority / Lien | Coupon / Margin | Fixed / Floating | Call Date | Refinancing Pressure | Credit Implication | Source Trace |
|---|---:|---|---|---:|---|---|---|---|---|---|---|
| CEI Revolving Credit Facility — drawn balance | $114m carrying value | USD | January 31, 2028, subject to possible springing maturity | 1.33 | Senior secured; first lien as described in issuer debt disclosures. [C34] | Variable; SOFR/base rate plus applicable margin, subject to leverage step-downs. [C36] | Floating | —; not stated in supplied debt table | Medium: renewal/refinancing of drawn balance and commitment is needed by stated maturity; springing trigger requires verification. | Main near-term facility event; current availability and conditions require the full agreement. | Q2 debt table; balance-sheet carrying-value reconciliation; historical agreement excerpt. [C1, C22, C36, C37] |
| CEI Term Loan A | $618m carrying value | USD | January 31, 2028 | 1.33 | Senior secured. [C34] | Variable; SOFR/base rate plus applicable margin, subject to leverage step-downs. [C36] | Floating | —; not stated in supplied debt table | Medium: nearest material term-loan maturity; scheduled amortization precedes maturity. | Refinancing runway exists, but a 2028 takeout or amendment must be arranged; no current headroom is known. | Q2 debt table and stated maturity. [C2, C23, C35, C36] |
| CVA Delayed Draw Term Loan | $372m carrying value | USD | April 26, 2029 | 2.56 | Senior secured first lien at Caesars Virginia obligor; CEI does not guarantee the facilities. | Variable; Term SOFR plus margin | Floating | —; not stated in supplied debt table | Low-to-Medium: later maturity, but interest and amortization remain cash claims. | Separate obligor/perimeter; do not attribute facility directly to CEI guarantor debt. | Q2 debt table and facility terms. [C3] |
| CEI Senior Notes due 2029 | $1,193m carrying value | USD | October 15, 2029 | 3.04 | Senior unsecured | 4.625% | Fixed | —; not stated in supplied debt table | Low near-term; unsecured maturity is beyond the 2028 facility wall. | Refinancing risk is longer-dated; unsecured recovery is structurally behind secured claims on collateral. | Q2 debt table. [C8] |
| CEI Term Loan B | $1,993m carrying value | USD | February 6, 2030 | 3.35 | Senior secured. [C34] | 2.25% Term Benchmark / 1.25% ABR margins under the 2024 amendment, plus relevant reference rate. [C29] | Floating | Historical six-month repricing protection expired; current call terms not stated. | Low near-term; floating interest and amortization persist before final maturity. | Cash interest remains rate-sensitive; maturity is not imminent. | Q2 debt table and Fifth Amendment. [C4, C29, C30] |
| CEI Senior Secured Notes due 2030 | $1,987m carrying value | USD | February 15, 2030 | 3.37 | Senior secured, first priority. [C34] | 7.00% | Fixed | —; not stated in supplied debt table | Low near-term; fixed coupon limits direct rate reset, but principal remains to refinance at maturity. | Secured class shares first-priority collateral subject to complete intercreditor terms. | Q2 debt table. [C6, C34] |
| CEI Term Loan B-1 | $2,808m carrying value | USD | February 6, 2031 | 4.35 | Senior secured. [C34] | 2.25% Term Benchmark / 1.25% ABR margins under the 2024 amendment, plus relevant reference rate. [C29] | Floating | Historical six-month repricing protection expired; current call terms not stated. | Low near-term; rate exposure persists before final maturity. | Large floating tranche increases interest-rate and eventual refinancing exposure. | Q2 debt table and Fifth Amendment. [C5, C29, C30] |
| CEI Senior Secured Notes due 2032 | $1,487m carrying value | USD | February 15, 2032 | 5.38 | Senior secured, first priority. [C34] | 6.50% | Fixed | —; not stated in supplied debt table | Low near-term; long-dated fixed coupon. | Recovery depends on collateral value, lien sharing and intercreditor provisions. | Q2 debt table and issuer guarantee summary. [C7, C34] |
| CEI Senior Notes due 2032 | $1,088m carrying value | USD | October 15, 2032 | 6.04 | Senior unsecured | 6.00% | Fixed | —; not stated in supplied debt table | Low near-term; long-dated unsecured maturity. | More exposed than first-lien creditors to hypothetical collateral priming; exact recovery not quantified. | Q2 debt table. [C9] |
| Special Improvement District Bonds | $38m carrying value | USD | 2037; exact date not stated | Approximately 10.25; year-only basis | Security/rank not stated in supplied evidence | 4.30% | Fixed | —; not stated | Low near-term; small balance and distant year-only maturity. | No material near-term wall contribution; security cannot be inferred. | Q2 debt table. [C10] |
| Long-term notes and other payables | $1m carrying value | USD | [Insufficient Information] — maturity not stated in supplied debt table | [Insufficient Information] — maturity unavailable | [Insufficient Information] — rank not stated | [Insufficient Information] — rate not stated | [Insufficient Information] — rate type not stated | [Insufficient Information] — call terms not stated | Unknown; balance is small but maturity cannot be mapped. | Retain in carrying-value debt total; do not assign a maturity year. | Q2 debt table. [C11] |

**Maturity concentrations:** carrying values total $732 million in 2028, $1.565 billion in 2029, $3.980 billion in 2030, $2.808 billion in 2031 and $2.575 billion in 2032. The 2037 bonds contribute $38 million; $1 million remains unmapped by maturity. The debt-service schedule reports $805 million of principal in 2028, a scheduled-payment measure that includes contractual maturities and scheduled repayments; it is not the instrument final-maturity wall. [C1-C13]

#### T3D.3 — Liquidity / Market Access Table

| Factor | Evidence | Current Level / Status | Direction | Risk Mechanic | Credit Implication | Confidence | Source Trace |
|---|---|---|---|---|---|---|---|
| Near-term maturity relative to liquidity | June 30 carrying debt $11.699bn; 2028 final maturities include $618m TLA and $114m RCF carrying value; cash and capacity $2.928bn. [C1, C2, C14, C16] | No final maturity inside the next 12 months from June 30; Jan. 2028 facilities are nearest wall. | Stable-to-Increasing as 2028 approaches | Refinancing need grows nearer while forward cash generation and facility access are not projected. | Medium forward refinancing pressure; no immediate maturity default risk evidenced. | Medium | [C1, C2, C14, C16, C22, C23] |
| Liquidity position | $965m cash; $2.928bn issuer-reported aggregate cash and borrowing capacity at June 30. [C14, C16] | Meaningful reported opening buffer; restricted cash excluded. [C17] | Insufficient Information | Cash is available immediately; revolver capacity remains subject to terms and later usage. | Supports near-term resilience, not a full 12-month sufficiency conclusion. | Medium | [C14, C16, C17] |
| Revolver draw status | CEI RCF face draw $120m; $2.25bn commitment; CVA RCF commitment $25m and no reported outstanding amount. [C1, C22] | CEI RCF partially drawn; no CVA RCF draw reported. | Stable | Draws reduce unused capacity; post-June draw status is unknown. | Monitor available capacity and draw trend. | Medium | [C1, C22] |
| FCF / operating cash | H1 CFO $675m and PP&E purchases $335m; CFO less PP&E is a $340m historical proxy only. [C15, C18] | Positive historical cash generation; no complete forecast. | Insufficient Information | Interest, rent, taxes, working capital and other investments reduce cash available for debt service. | Forward FCF and liquidity runway are not calculable. | Medium for historical figures; Low for forecast | [C15, C18, C21] |
| Cash-interest burden | $6.0bn variable-rate borrowings at June 30; estimated remainder-2026 interest $370m. [C13, C27] | Material floating-rate exposure; debt-service estimate is dated. | Increasing if rates rise | Higher reference rates increase interest and reduce deleveraging capacity. | Negative debt-service/refinancing sensitivity; current dollar stress not calculated. | Medium | [C13, C27] |
| Covenant headroom | June 30 compliance reported; CEI RCF/TLA include 6.50:1 maximum net-total-leverage and 2.0:1 minimum fixed-charge-coverage covenants. [C28, C35] | Compliance reported; cushion unknown. | Insufficient Information | Draws or lower EBITDA may reduce facility flexibility if testing conditions apply. | Do not infer unused capacity or distance to breach. | Low | [C28, C35] |
| Market access | No direct current market quote, spread, curve or primary refinancing terms are included in the delivered source set. | [Insufficient Information] — no executable market evidence. | Insufficient Information | Refinancing cost and investor appetite cannot be measured. | Consensual refinancing is plausible but not market-verified. | Insufficient Information | Source-scope limitation; direct market evidence not supplied. |
| Ratings / outlook | Current rating-agency report or outlook is not in the direct evidence set. | [Insufficient Information] — no current rating action. | Insufficient Information | Ratings could affect access and terms, but no direction is established. | Monitor notices; no downgrade assumption. | Insufficient Information | Source-scope limitation; direct rating evidence not supplied. |
| Asset sales / deleveraging | No post-June debt paydown or refinancing is identified in the direct evidence; 2025 redemption is historical. | Current proceeds/deleveraging not quantified. | Insufficient Information | Asset proceeds could reduce debt if realized and applied; no current event assumed. | No incremental liquidity or debt-reduction credit. | Low | Q2 debt schedule and FY2025 debt disclosure. [C11, C12, C26] |
| Improving EBITDA / deleveraging | H1 Adjusted EBITDA was $1.807bn versus $1.839bn in H1 2025. | No clear consolidated deleveraging trend established by EBITDA alone. | Stable-to-Insufficient Information | Improved operations could support cash generation, but H1 EBITDA declined despite revenue growth. | Counterargument to refinancing stress, not proof of future debt reduction. | Medium | Q2 2026 Form 10-Q; direct EBITDA figure not separately cited in this module’s direct evidence. |

#### T3D.4 — Legal Capacity Register

| Legal-Capacity Indicator | Available / Not Available / Unclear | Evidence | Risk Mechanic | LME Paths Enabled | Confidence | Source Trace |
|---|---|---|---|---|---|---|
| Incremental debt capacity | Unclear | Partial credit-agreement excerpt describes incremental facilities and yield mechanics; full current agreement and usage tracker absent. [C32, C33] | Contractual debt routes may exist, but current availability and conditions cannot be confirmed. | Consensual refinancing; Priming Debt only if current terms and tests permit. | Low | [C32, C33] |
| Lien capacity | Unclear | Issuer reports secured facilities and notes; full current lien baskets, security package and usage unavailable. [C34] | Additional permitted liens could dilute collateral, subject to current agreement and intercreditor terms. | Priming Debt; Uptier; not established. | Low | [C34] |
| Unrestricted subsidiary capacity | Unclear | Current designation covenant and usage tracker are not supplied. | A permitted designation could move value beyond direct guarantor/collateral reach. | Drop-Down / J.Crew-style transfer not established. | Insufficient Information | Current provision and usage not supplied. |
| Investment capacity | Unclear | Full current agreement and basket usage are absent. | Investments can transfer value or cash outside creditor reach. | Drop-Down / asset transfer, subject to current documents. | Low | Full current agreement not supplied. |
| RP / junior debt payment capacity | Unclear | FY2025 filing summarizes negative covenants, but detailed current baskets and usage are absent. | Restricted payments can reduce creditor-available liquidity. | No specific LME path established. | Low | Source-scope limitation; complete current covenant terms unavailable. |
| Collateral release | Unclear | Complete current security and release documents are not supplied. | Release can reduce recovery collateral if legally permitted and completed. | Drop-Down / asset sale; not established as current capacity. | Insufficient Information | Security package absent. |
| Guarantor release | Unclear | Annual filing describes material domestic subsidiary guarantees for secured debt; complete release terms and current schedules are absent. [C34] | Release could create structural subordination or reduce claim reach. | Drop-Down; not established. | Low | [C34] |
| Amendment thresholds | Available, limited to historical 2024 repricing transaction | Fifth Amendment describes lender consents and replacement of non-consenting lenders. [C30, C31] | Demonstrates a historical repricing process, not general current amendment rights. | Amend-and-Extend; consensual refinancing, subject to current terms. | Medium for historical transaction; low currently | [C30, C31] |
| Sacred rights | Unclear | Current credit-agreement sacred-right provisions are not supplied; historical amendment mechanics are transaction-specific. | Unverified rights could constrain changes to payment, lien or pro-rata treatment. | Uptier / Serta-style exchange not established. | Insufficient Information | Full current agreement and ICA absent. |
| Open-market purchase provisions | Unclear | No current governing provision or debt-purchase activity is supplied. | Repurchases could use liquidity or reduce debt below par; authority is unverified. | Open-market repurchase. | Insufficient Information | No direct provision or transaction evidence. |
| MFN protection | Available historically, not established as current | Partial 2024 agreement excerpt describes a conditional Term B-1 yield-differential protection. [C33] | Could limit pricing differential for qualifying debt; conditions are narrow and current applicability is not shown. | Consensual refinancing / incremental loan. | Low | [C33] |
| Intercreditor terms | Unclear | Complete intercreditor agreements are not supplied. | Standstill, control, turnover and lien-sharing terms determine practical priming/enforcement risk. | Uptier; Priming Debt; junior-lien financing. | Insufficient Information | No direct intercreditor text. |
| Class voting | Available, limited to historical amendment | Fifth Amendment documents consent and replacement mechanics for that repricing. [C30, C31] | Historical process does not establish current class-voting rules. | Amend-and-Extend; consensual refinancing. | Medium for historical transaction; low currently | [C30, C31] |
| Pro rata sharing provisions | Unclear; historical cashless allocation was not required to be pro rata | Fifth Amendment states cashless assignments need not be made by all lenders pro rata. [C32] | Transaction-specific allocation may differ among lenders but does not establish broad current non-pro-rata capacity. | Historical cashless consent/reallocation; Serta-style path not established. | Low | [C32] |

#### T3D.5 — Sponsor Willingness Table

| Factor | Evidence | Assessment | Risk Mechanic | Credit Implication | Source Trace |
|---|---|---|---|---|---|
| Historical refinancing/LME behavior | 2024 Term B/B-1 repricing reduced margins and included stated premium and replacement-lender mechanics. [C29, C30, C31] | Medium evidence of ordinary repricing execution; no evidence of distressed exchange or coercive LME. | Repricing shows amendment execution, not intent to subordinate nonparticipants or support debt with equity. | Supports ordinary refinancing execution history but not current LME intent. | [C29, C30, C31] |
| Current sponsor support signals | No direct sponsor support for CEI debt is established in direct source evidence. The merger guarantee is limited to Parent/Merger Sub obligations. [C34] | Insufficient Information | A transaction guarantee does not fund CEI debt or establish an equity cure. | No sponsor-support credit assumed. | [C34] |
| Sponsor economic incentive | Pending merger terms do not disclose a funded equity contribution or establish sponsor willingness to use balance-sheet support. | Insufficient Information | Ownership/transaction incentives may affect policy, but terms alone do not prove support or creditor-adverse intent. | No LME willingness inference from sponsor identity or deal terms. | Merger status appears in Q2 filing; no direct incentive conclusion drawn. |
| Governance structure | Q2 filing reports the merger is subject to stockholder and regulatory approvals and may not close on time or at all. | Medium transaction uncertainty; sponsor willingness remains insufficient. | Conditions and timing may constrain actions or divert attention; current post-Q2 status is unknown. | Monitor approvals and transaction status; no control or intent assumed. | Q2 2026 Form 10-Q, p. 5. |

#### T3D.6 — Refinancing Path Table

| Path Type | Feasibility | Likelihood Direction | Evidence Supporting | Evidence Against | Legal Capacity Required | Creditor Impact | Source Trace |
|---|---|---|---|---|---|---|---|
| Consensual refinancing | Medium | Medium | No final maturity falls within 12 months; reported $2.928bn liquidity and positive H1 CFO provide a buffer. [C14, C15, C18] | Market pricing/access, covenant headroom and post-June cash are unavailable. | Current debt, lien and covenant permissions; full agreement required. | Ordinarily preserves ranking if documentation does; could increase cost or leverage. | [C11, C14, C15, C18, C22, C23] |
| Amend-and-Extend | Medium | Low | 2024 amendments demonstrate prior consent-based repricing and replacement mechanics. [C29, C30, C31] | Current lender appetite and general amendment thresholds are not evidenced. | Current class voting, sacred rights and assignment provisions. | Can relieve maturity pressure but may add fees, pricing or covenant changes. | [C29, C30, C31] |
| Open-market repurchase | Low | Low | No current debt repurchase is reported in direct evidence. | No current market price, cash authorization or open-market provision supplied. | Issuer authority, payment capacity and applicable legal restrictions. | Could reduce debt below par but use liquidity; no action assumed. | No direct transaction evidence; source limitation. |
| Exchange offer | Medium | Low | Could be a route if refinancing conditions weaken; no current offer or full current capacity evidence. | No offer, term sheet or solicitation in supplied evidence. | Class voting, consent, registration and debt-incurrence provisions. | Could extend maturity but alter ranking, coupon or collateral for participants. | Current transaction evidence absent. |
| Distressed exchange | Low | Low | Maturity pressure increases as 2028 approaches. | No default, distressed offer, or demonstrated incentive; reported liquidity remains meaningful at June 30. [C14, C15] | Exchange authority, consent thresholds and default treatment. | Could impair nonparticipants; purely hypothetical. | [C14, C15, C28] |
| Uptier | Low | Low | Historical amendment shows replacement mechanics, but not a current uptier right. [C31] | Current credit agreement and ICA missing; no transaction or willingness evidence. | Sacred rights, majority thresholds, lien capacity and ICA terms. | Nonparticipants could be subordinated if legally executed; feasibility unestablished. | [C31, C32] |
| Drop-Down | Low | Low | Historical incremental agreement suggests debt/investment concepts, but current designation, collateral and baskets are not established. [C32] | No current asset transfer or complete legal package. | Unrestricted-subsidiary, investment, collateral-release and guarantee-release provisions. | Could reduce collateral/guarantor reach; no current path asserted. | [C32] |
| J.Crew-style transfer | Insufficient Information | Insufficient Information | No current transfer provision or asset-transfer transaction identified. | Full current agreement, collateral package and permitted investment capacity unavailable. | Specific transfer restrictions, IP/collateral terms and designation provisions. | Potential collateral leakage cannot be assessed. | Legal source gap. |
| Serta-style non-pro-rata exchange | Insufficient Information | Insufficient Information | Fifth Amendment documents a transaction-specific cashless allocation not required to be pro rata. [C32] | That mechanic is not evidence of a non-pro-rata exchange or current sacred-right waiver; no current ICA. | Current voting, sacred rights, pro-rata sharing and ICA terms. | Could subordinate holdouts if permitted; neither feasibility nor intent inferred. | [C32] |
| Priming debt | Low | Low | Historical partial agreement contains incremental debt/yield terms. [C32, C33] | Current debt/lien capacity, tests, headroom and market appetite unverified. | Debt/lien baskets, ratio tests, ICA and sacred rights. | Could prime or dilute existing secured recoveries if permitted; no capacity quantified. | [C32, C33] |
| Asset sale / partial paydown | Medium | Low | Company has reported historical asset dispositions, but no current debt-repayment proceeds are shown in direct evidence. | No current sale, proceeds allocation or mandatory paydown identified. | Asset-sale covenants, reinvestment rights and lien-release terms. | Could reduce debt if proceeds are applied; reinvestment may delay paydown. | Current transaction evidence absent. |
| Sponsor equity injection | Insufficient Information | Insufficient Information | Merger Parent Guarantor guarantee covers Parent/Merger Sub agreement obligations, not CEI debt. [C34] | No funded support commitment to CEI creditors evidenced. | Equity contribution documents and approvals. | Would improve liquidity if funded; no support assumed. | [C34] |

#### T3D.7 — Vulnerability Score Table

| Dimension | Score | Evidence | Risk Mechanic | Credit Implication | Source Trace |
|---|---|---|---|---|---|
| Refinancing pressure | Medium | Jan. 2028 RCF/TLA maturities; 2027 scheduled principal and interest are disclosed. [C1, C2, C12, C13, C22, C23] | Maturity wall is not inside the next 12 months, but preparation is needed and 2028 concentration is material. | Refinancing becomes more consequential over the next 12–18 months. | [C1, C2, C12, C13, C22, C23] |
| Legal capacity | Insufficient Information | Partial historical agreement excerpt and 2024 amendments; no full current agreement, ICA or basket tracker. [C29-C33, C37] | Current debt, lien and non-pro-rata capacity cannot be confirmed. | Do not infer present ability to prime, transfer collateral or change sacred rights. | [C29, C30, C31, C32, C33, C37] |
| Sponsor willingness | Insufficient Information | No accepted CP-2C evidence; no direct evidence of support for CEI debt or coercive LME intent. | Sponsor identity and merger terms do not prove willingness to support or subordinate creditors. | No support or LME intent assumed. | T3D.5; [C34] |
| Market access | Insufficient Information | No direct executable prices, spreads, curves or refinancing terms in direct evidence. | Cost and availability of a market takeout cannot be established. | Consensual refinancing is plausible but not market-verified. | T3D.1 source limitation. |
| Recovery impact | Insufficient Information | Full collateral, guarantor and intercreditor package unavailable. | Priming or releases could affect recovery, but asset value and priority are unquantified. | No recovery estimate or security preference. | [C34, C37] |
| **Overall Prime/LME Vulnerability** | **Low** | No source-supported combination of acute pressure, current coercive capacity and sponsor willingness; nearest material final-maturity wall is January 2028. [C1, C2, C14, C15, C18, C22, C23] | Liquidity and maturity runway reduce immediate pressure; legal capacity and willingness are not supported sufficiently for a High score. | Low LME vulnerability does not mean low refinancing risk; maintain elevated 2028 refinancing monitoring. | [C1, C2, C14, C15, C18, C22, C23, C29, C30, C31, C32] |

**Overall Evidence Confidence:** Low. Maturity facts are directly sourced; legal capacity, sponsor willingness, current market access and recovery evidence are incomplete.

#### T3D.8 — Creditor Class Exposure Table

| Creditor Class | Exposure: Base Case | Exposure: Stress Case | Exposure: LME Case | Recovery Implication | Priming / Subordination Risk | Source Trace |
|---|---|---|---|---|---|---|
| CEI Term Loan A and CEI RCF | 2028 maturity; carrying exposure $618m TLA and $114m drawn RCF. [C1, C2] | Lower cash conversion could increase refinancing reliance before January 2028. | Hypothetical new secured debt or non-pro-rata exchange could affect priority; current authority not established. | Senior secured guarantees are described, but full collateral waterfall and ICA are absent. [C34] | Medium relative exposure due to earliest maturity; actual priming capacity unknown. | [C1, C2, C22, C23, C34] |
| Term B / Term B-1 and 2030/2032 secured notes | First-priority secured claims are described; Term B/B-1 are floating-rate. [C4, C5, C6, C7, C29, C34] | Higher rates and weaker operating cash could slow deleveraging and increase future refinancing needs. [C27] | Hypothetical pari/priming debt or selective exchange could dilute or subordinate nonparticipants, subject to missing current terms. | Recovery depends on shared collateral, guarantees and intercreditor rights not fully supplied. | Medium; unsecured and nonparticipating claims could be more exposed, but no event or capacity is established. | [C4, C5, C6, C7, C27, C29, C34] |
| Senior unsecured notes due 2029/2032 | Long-dated fixed-coupon claims; carrying values $1.193bn and $1.088bn. [C8, C9] | Could face weaker recovery if secured claims grow or collateral is released. | Most exposed class to hypothetical collateral priming or leakage. | Structurally behind secured claims on collateral; no recovery value can be quantified. | Higher relative subordination risk in a hypothetical secured priming case; feasibility unknown. | [C8, C9, C34, C37] |
| CVA Delayed Draw Term Loan | Separate Caesars Virginia facility, carrying $372m and due 2029; CEI does not guarantee the facilities. [C3] | Facility-level cash flow and coverage stress are not separately modelled. | No evidence of CEI-level LME treatment or cross-collateral access. | Separate obligor security; do not combine recovery with CEI debt. | Unclear at wider group level; direct CEI guarantee is not stated in direct evidence. | [C3, C34] |

#### T3D.9 — Monitoring Triggers

| Trigger | Indicator | Threshold / Qualitative Signal | Leading / Lagging | Why It Matters | Linked Path(s) | Source Trace |
|---|---|---|---|---|---|---|
| 2028 facility refinancing | CEI RCF and Term Loan A refinancing, extension or replacement plan | Quantitative threshold not available in provided materials; monitor for filed financing, lender amendment or confirmed plan before January 31, 2028. | Leading | These are nearest material final maturities; delay can concentrate liquidity and execution risk. | Consensual refinancing; Amend-and-Extend | [C1, C2, C22, C23] |
| Cash and revolver availability | Cash balance, RCF drawings, letters of credit, reserves and regulatory commitments | Quantitative threshold not available in provided materials; material cash decline or falling available capacity. | Leading | Draws reduce fallback capacity and may indicate operating cash stress. | Consensual refinancing; Asset sale / partial paydown | [C14, C15, C16, C17] |
| Debt-service coverage of uses | Operating cash flow relative to interest, maturities, lease cash and capex | Quantitative threshold not available; sustained deterioration in reported CFO or cash flow after capex. | Lagging | Weaker cash conversion reduces internal funding for the 2028 wall. | Consensual refinancing; Amend-and-Extend | [C12, C13, C15, C18, C21] |
| Covenant compliance/headroom | Compliance certificates, test conditions and ratio calculations | Quantitative threshold not available; reported reduced headroom, waiver or breach. | Leading / lagging | Compliance alone does not show cushion; tighter tests may restrict access or transactions. | Consensual refinancing; Priming Debt; Uptier | [C28, C35] |
| New debt or liens | Filed debt issuance, lien grants, incremental facilities or debt classification | Quantitative threshold not available; any new secured borrowing or material lien disclosure. | Leading | Incremental debt could increase leverage or dilute collateral priority. | Priming Debt; Uptier; Consensual refinancing | [C32, C33, C34] |
| Asset transfers / subsidiary designations | Asset sale, unrestricted-subsidiary designation, collateral or guarantee release | Quantitative threshold not available; any reported transfer or release. | Leading | Could reduce creditor reach or change the collateral base. | Drop-Down; J.Crew-style transfer; Asset sale / partial paydown | Current legal documents are incomplete. |
| Merger status and funding | Regulatory/stockholder approvals, financing commitment status, termination or closing | Initial end date May 27, 2027 and ticking-fee date June 26, 2027; extensions are conditional. | Leading | Transaction outcomes may change capital structure, cash costs and operating flexibility. | Consensual refinancing; Sponsor equity injection | Q2 2026 Form 10-Q, p. 5. |
| Variable-rate debt cost | Term Loan and RCF rates, current debt balances and cash interest | Quantitative threshold not available in provided materials; monitor sustained increases in disclosed rates or cash interest. | Leading | Floating costs absorb cash and weaken refinancing flexibility. | Consensual refinancing; Amend-and-Extend | [C27, C29, C36] |

#### T3D.10 — Scenario Map

| Scenario | Key Assumptions | Refinancing Path | Timeline | Creditor Impact | Recovery Implication | Probability Direction | Confidence | Source Trace |
|---|---|---|---|---|---|---|---|---|
| Base Case | Operations and cash generation remain sufficient to support debt service; June 30 reported cash/capacity is not materially impaired; no coercive transaction is assumed. [C14, C15, C18, C28] | Consensual refinancing or replacement/extension of 2028 facilities | Before January 31, 2028; no exact financing date assumed. [C22, C23] | Existing creditors retain contractual ranking, subject to final documentation, fees and market access. | No change inferred; recovery remains dependent on collateral and guarantees. | Medium | Medium | [C1, C2, C14, C15, C18, C22, C23] |
| Stress Case | Las Vegas operating weakness persists, cash conversion declines, rates remain burdensome, and market access is less favorable; no numerical shock assumed. | Amend-and-Extend or consensual refinancing; asset sale/partial paydown only if evidenced and permitted. | Before 2028 maturity; earlier negotiation may be needed if liquidity/covenant indicators weaken. | Higher pricing, fees or tighter terms could reduce residual cash; no default or distressed exchange is assumed. | Lower cash generation may pressure recovery, but no asset valuation or waterfall is available. | Increasing if triggers worsen; otherwise Insufficient Information | Low | [C11, C12, C18, C27, C28] |
| LME Case | Severe operating/market stress plus a legally available non-pro-rata or priming path and issuer/sponsor incentive are assumed only as a hypothetical adverse case; none is established as actual intent. | Hypothetical uptier, priming debt or selective exchange; current legal feasibility is unverified. | Could arise before or around a refinancing need only if terms, consent rights and incentives support it; no timing prediction. | Participating creditors could receive priority or improved economics; holdouts could be subordinated. | Unsecured claims and nonparticipants could face impaired recovery if collateral is primed or transferred; magnitude cannot be quantified. | Low | Low | Current agreement, sacred rights, intercreditor terms and sponsor willingness are insufficiently evidenced. [C29, C30, C31, C32, C34, C37] |

#### T3D.11 — Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| Complete current CEI Credit Agreement | Full conformed agreement, schedules, current definitions, amendments and basket usage | Needed to determine current debt/lien capacity, voting, sacred rights and covenant access. | T3D.4, T3D.6 and LME feasibility remain limited; no exact capacity. | Obtain complete executed agreement and latest basket/compliance tracker; coordinate with CP-4/CP-4A. |
| Security and intercreditor package | Current collateral agreements, guarantor/collateral schedules, First Lien ICA and any Junior ICA | Needed to evaluate lien priority, enforcement control, turnover, releases and recovery. | T3D.4, T3D.8 and LME recovery effects remain qualitative. | Obtain executed current documents and release/perfection history; coordinate with CP-4A. |
| Covenant EBITDA, headroom and current compliance certificate | Tested ratios, covenant definitions, permitted adjustments and test conditions | Reported compliance is not headroom; affects refinancing and debt-incurrence capacity. | No numerical headroom or capacity conclusion. | Obtain current calculations and source-defined EBITDA bridge. |
| Current sponsor/governance evidence | Matching-run CP-2C handoff, ownership/capitalization, support history and sponsor economics | Sponsor identity or merger terms alone cannot establish willingness or incentive. | Sponsor-willingness score and High-LME test remain Insufficient Information. | Obtain matching-run CP-2C and current ownership/financing disclosures; do not infer meanwhile. |
| Direct, current market evidence | Executable prices, spreads/yields, benchmark curves, trade size/depth and refinancing terms | Market access and price of refinancing are central to path feasibility. | T3D.3 market assessment remains Insufficient Information; no market-based stress. | Obtain current instrument-specific two-sided quotes and benchmarked loan/bond evidence. |
| Post-June 2026 financials and debt schedule | Subsequent cash, debt draws/repayments, operating results and merger status | Analysis date is October 2, but latest financial statements end June 30. | Current liquidity, maturity status and transaction effects cannot be verified. | Obtain subsequent filings and current treasury debt/cash schedule. |
| Cash-flow forecast and full 12-month liquidity bridge | H1 2027 CFO, working capital, cash taxes, lease, debt service and capex | Determines whether current liquidity can support the 2028 refinancing runway. | No quantified funding gap or ending liquidity forecast. | Obtain a dated forecast through June 30, 2027 and reconcile to facility availability; coordinate with CP-2D. |
| LME and amendment history | Full amendments, waivers, exchanges, open-market purchases and class voting history | Needed to evaluate creditor treatment, historical willingness and transaction precedent. | No supported conclusion on coercive behavior. | Obtain complete transaction/legal history and current lender communications if permitted. |
| Recovery and entity value | Asset values, debt by entity, guarantees, collateral coverage and structural claims | Needed to quantify LGD and class exposure. | Recovery effects remain directional only. | Obtain current entity-level financials, collateral valuation and intercreditor waterfall. |
| Subsequent debt-event scan | Later refinancing, extension, buyback, exchange or LME activity after June 30 | Absence from the supplied Q2 filing does not prove no later event through October 2. | As-of-balance-sheet structure cannot be confirmed current. | Review subsequent filings and issuer notices; log events separately from June 30 figures. |

### Overall refinancing / LME view

The June 30, 2026 carrying-value maturity wall is concentrated in 2028–2032, with the first final maturities at the CEI RCF and Term Loan A in January 2028. [C1, C2, C4, C5, C6, C7, C9, C22, C23] The 2028 annual principal schedule is $805 million, a scheduled-payment measure rather than the final-maturity sum. [C12] Reported cash and borrowing capacity, positive H1 operating cash flow and management’s FY2025 liquidity outlook are the strongest counterarguments to immediate funding stress. [C14, C15, C18, C28] That counterargument would become stronger if subsequent filings showed durable cash generation, stable availability and debt reduction; missing post-June reporting leaves that test open.

Consensual refinancing or an amend-and-extend is the most credible path on the evidence available, but no financing plan is confirmed and market access is unverified. The executed 2024 repricing shows prior amendment execution, but the repricing protection was time-limited and does not demonstrate distressed-LME intent. [C29, C30, C31, C32] Current legal capacity, sponsor willingness, intercreditor terms and recovery values are insufficiently evidenced. Unsecured noteholders would be more exposed than first-lien creditors to a hypothetical collateral-priming or leakage event, but no such transaction is evidenced and feasibility is not established. [C34, C37] The top trigger is a current plan for the January 2028 RCF/TLA maturities, together with updated cash, availability and covenant certificates. **CP-3C Completed with Limitations. Prime/LME Vulnerability: Low. Most Likely Path: Consensual refinancing.**

## Evidence Trace

| Claim | Citation marker | Document | Page |
|---|---|---|---:|
| Q2 facility face/book values and carrying debt reconciliation inputs | [C1-C11] | Caesars Q2 2026 Form 10-Q | 9 |
| Scheduled principal maturities and total debt-service estimates | [C12, C13] | Caesars Q2 2026 Form 10-Q | 9 |
| June 30 liquidity and revolver components | [C14-C17] | Caesars Q2 2026 Form 10-Q | 2, 22 |
| H1 operating cash and capex estimate | [C15, C18, C20] | Caesars Q2 2026 Form 10-Q | 4, 22 |
| Cash increase and remainder-2026 lease payment estimate | [C19, C21] | Caesars Q2 2026 Form 10-Q | 4, 22 |
| Revolver and TLA maturity dates | [C22, C23] | Caesars Q2 2026 Form 10-Q | 10 |
| Term B and B-1 maturity dates | [C24, C25] | Caesars Q2 2026 Form 10-Q | 10 |
| FY2025 debt and rent context | [C26] | Caesars FY2025 Form 10-K | 13 |
| Variable-rate borrowing exposure and covenant compliance | [C27, C28] | Caesars Q2 2026 Form 10-Q | 23 |
| 2024 Term B/B-1 repricing margins and premium | [C29, C30] | Fifth Amendment to Credit Agreement | 1 |
| Non-consenting and cashless consent mechanics | [C31, C32] | Fifth Amendment to Credit Agreement | 1 |
| B-1 yield protection conditions | [C33] | Incremental Assumption Agreement No. 3 excerpt | 43 |
| Secured subsidiary guarantees; facility covenant ratio | [C34, C35] | FY2025 Form 10-K; Q2 2026 Form 10-Q | 42; 23 |
| RCF/TLA margin and leverage step-downs | [C36] | Caesars Q2 2026 Form 10-Q | 10 |
| RCF springing maturity definition in partial agreement excerpt | [C37] | Incremental Assumption Agreement No. 3 / credit agreement excerpt | 20 |

## Source Registry

Primary maturity and liquidity evidence is the June 30, 2026 Form 10-Q; the FY2025 Form 10-K supplies historical debt, lease and guarantee context. Executed fourth and fifth credit amendments and the partial Incremental Assumption Agreement No. 3 provide only their stated historical terms; none substitutes for a complete current conformed credit agreement, security package or intercreditor agreement. Accepted CP-0, CP-1, CP-1A, CP-2A, CP-4, CP-2D and CP-3D artifacts match the stated run and period, but their restricted status and scope are retained. CP-2C is not an accepted input. T3D.2 uses balance-sheet carrying value; face principal and debt-service schedule measures remain separately identified. [C1, C2, C11, C12, C26, C29, C30, C32, C34]

## Gaps & Conflicts

The Q2 debt note reports $11.807 billion face value and $11.705 billion book value; the balance sheet reports $114 million current debt and $11.585 billion long-term debt, totaling $11.699 billion. The $6 million difference between debt-note book value and balance-sheet carrying debt corresponds to RCF deferred finance charges; the $108 million face-to-balance-sheet carrying difference is retained, not silently reconciled. The annual schedule reports $805 million of 2028 principal maturities, a scheduled-payment measure that includes contractual maturities and scheduled repayments; the carrying-value sum of the two instruments with 2028 final maturities is $732 million. Both measures are shown by role. [C1, C2, C12]

Other material gaps are current covenant headroom, basket usage, the full credit agreement, collateral/intercreditor terms, sponsor willingness, direct market evidence, recovery values and financial/transaction updates after June 30. Consequently no funding gap, market-access conclusion, precise LME capacity or recovery estimate is calculated. The Q2 filing identifies the July 13 Alberta launch after the balance-sheet date; it is not blended into June 30 financial figures. No later refinancing or LME event is identified in the delivered evidence, which does not establish that none occurred through October 2. [C33]

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity, lineage and filename | Self-checked | Host-owned front matter retained; derived filename is `CZR_CP-3C_20261002.md`. |
| Maturity/debt source gate | Passed with limitations | Q2 debt table and annual debt-service schedule are available; module is not blocked. |
| Debt basis and conflict handling | Self-checked | T3D.2 uses carrying value; face principal and annual schedule figures remain separately labelled in CF-1. |
| Subsequent-event scan | Self-checked | July 13 Alberta launch recorded separately; no later refinancing/LME event identified in delivered evidence, with source-coverage limitation retained. |
| Liquidity and market access | Restricted | June liquidity is reported, but no complete 12-month forecast or direct current market evidence is available. |
| Legal capacity and sponsor willingness | Restricted | Historical amendments are distinguished from current legal capacity; CP-2C and current complete documents are absent. |
| Required registers | Self-checked | T3D.1 through T3D.11 are present with required columns and populated rows. |
| Scenarios and probability labels | Self-checked | Base, stress and hypothetical LME cases use directional labels; no numerical probabilities or unsupported intent inferred. |
| Confidence | 55/100 — Low | Restricted evidence and material legal, market, sponsor and period gaps cap the score below 60. |
| QA / committee status | Restricted / Requires More Work | Material legal, market, sponsor and post-period gaps remain. |
| Host automated validation | Pending | Host validation follows this response; no script result or host finding is claimed. |