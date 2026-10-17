---
module_id: "CP-2G"
module_name: "ForwardCreditModel"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "RELATIVE_VALUE"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2G-51a44d9e9733643f"
credit_os_route_node_id: "RN-FULL_CREDIT_32-RELATIVE_VALUE-08-CP-2G"
credit_os_invocation_sha256: "02cb2c374e9c4f09d1b5ab05d5bcf1f8e3e83cb4b59b45ff74d4800eeb15ba5d"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "ae8d96880802acf87c821f7e39347793101215e1135a2589f2bf642c17fd9624"
  - module_id: "CP-1"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "feb32206df70f6261119dceb61308629455fa9537a6f5305a4d941c2fb2015a9"
  - module_id: "CP-2A"
    run_id: "COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6"
    period: "Q2 2026"
    sha256: "d1f94808cb6da2dbaa1fa9f9a9946cec503fcf4808c38199854f3e2ffaa0f2ad"
confidence_score: 42
confidence_band: Low
qa_status: Restricted
committee_status: Requires More Work
limitation_flags: [FORWARD_DRIVERS_UNAVAILABLE, BASE_AND_DOWNSIDE_NOT_NUMERICALLY_RECONCILABLE, CP_MODEL_PERIODS_UNAVAILABLE, COVENANT_HEADROOM_NOT_CALCULABLE, DEBTOR_CASH_ALLOCATION_MISSING, MERGER_FINANCING_MISSING]
validation_warnings: [DEBT_FACE_BOOK_CARRYING_BASES_DIFFER, REPORTED_CFO_ALREADY_AFTER_CASH_INTEREST, ACTIVE_DIVISION_SLOTS_NOT_READY, HOST_VALIDATION_PENDING]
downstream_consumers: [CP-2H, CP-4C, CP-MODEL]
---

## Audit Summary

**Canonical handoff:** `CZR_CP-2G_20261002.md`. Owned object: `forward_credit_model`; schema family: analytical canonical Markdown; runtime output: this handoff alone. CP-0, CP-1 and CP-2A match CZR, Q2 2026 and the selected run. Forecast scope is FY2026–FY2028, with June 2026 LTM as the operating base; FY2026 is partly actual. Currency and unit are consolidated USD millions, calendar fiscal years ending December 31. **Status: Complete with Gaps; 42/100, Low; Restricted; Requires More Work.** Historical and disclosed payment windows are auditable, but no sourced, complete base/upside/downside operating and financing drivers permit a reconciled numerical forward path. All three cases are therefore conditional pathways, **not forecasts with invented outputs**. CP-MODEL's required driver interface is present but its active-slot periods are unavailable. No host validation result is claimed.

## Analysis

### Forward credit view

At June 2026, constructed LTM revenue was $11,648 million and issuer Adjusted EBITDA $3,592 million; first-half operating cash flow of $675 million was nearly flat year over year, while lower capex protected after-capex cash. [C1, C2, C3, C4, C5, C6, C7, C8] The first prospective pressure point is the remainder-of-2026 payment window; the larger scheduled principal step arrives in 2028. [C15, C16, C17, C18] A persistent Las Vegas visitation and hold decline could first depress earnings, then cash conversion, then refinancing capacity. [C19, C46] Regional improvement is the strongest observed counterweight. [C20] Available reports do not establish future cash conversion, covenant headroom, debtor-accessible cash or transaction financing. Thus the base, upside and downside identify different drivers and monitoring triggers, but **none supports a closing leverage, liquidity-runway or refinancing-capacity number**. Reported compliance is not stress headroom. [C25, C27, C28]

### Decision drivers and conditional cases

1. **Observed cushion, not forecast deleveraging.** H1 CFO less property/equipment purchases was $340 million versus $227 million a year earlier; the $113 million improvement is largely a $118 million reduction in cash capex, not improved CFO. [C7, C8] That is contrary evidence to an immediate liquidity squeeze. It wins if future cash generation covers genuine maintenance and fixed payments without renewed borrowing; the historical maintenance split and future CFO are unavailable.
2. **Base:** carry forward the observed operating mix only as a monitoring reference, not a flat-growth assumption. **Upside:** sustained Regional gains and durable cash conversion offset Las Vegas weakness. **Downside:** persistent weaker visitation/hold and digital tax pressure reduce contribution before debt service, lease payments and capex necessarily reset. These are analyst-judgment causal cases, with no numerical shocks or probabilities. [C19, C20, C21, C46]
3. **First inflection:** remaining-2026 estimated debt service $425 million, VICI/GLPI payments $687 million and capex $310–390 million are separate future uses; adding them to already-after-interest CFO as though they were all incremental would double-count interest. FY2027 and FY2028 scheduled principal is $114 million and $767 million, respectively. [C15, C16, C17, C18, C29, C30] Without H2 CFO, working capital and other movements, the minimum-cash point is **Not Calculable from Provided Materials**.

**Funding and definitions.** June balance-sheet carrying debt is $11,699 million: $114 million current plus $11,585 million long term. The debt note instead reports $11,807 million principal and $11,705 million book debt; its separate $6 million deferred-revolver-charge line explains the book-to-balance-sheet presentation difference, not a forecast cash movement. [C9, C10, C12, C13] June cash was $965 million; $2,928 million reported cash-plus-capacity includes conditional revolver access, not entirely free debtor cash. [C11, C14, C44, C45] The $13,157 million separately classified financing obligations remain outside canonical debt but their rent-related cash costs matter. [C35, C30] No captive finance-company perimeter is identified in the delivered issuer evidence; Caesars Virginia's separately financed operating venture nevertheless makes debtor-level access distinct from consolidated liquidity.

**Funding float and event boundary.** Customer deposits and other deferred revenue rose from $492 million at December 2025 to $545 million at June 2026. These prepayments represent future wagering or services, not ordinary trade payables or permanent free cash; withdrawals or fulfillment without replacement receipts could consume liquidity before scheduled debt principal changes. [C22, C23, C24] The May 2026 merger agreement predates June 30, but closing remains conditional, with an initial May 27, 2027 end date; no acquisition financing or completion is inserted into the model. [C25, C26, C47] **Subsequent event:** the July 13, 2026 Alberta launch postdates June 30 and supplies no June pro forma amount. [C37]

### Analytical appendix — complete canonical registers

`—` in these untagged registers means unavailable, never zero. Historical FCF = reported CFO minus cash purchases of property and equipment; CFO already incorporates operating cash interest and taxes. `EBITDA` below means issuer Adjusted EBITDA (ID E-ADJ), not covenant EBITDA (ID E-COV, unavailable). Debt ID D-BS is current plus long-term balance-sheet carrying debt, excluding separately classified financing obligations. Liquidity ID L-REP is the issuer's reported cash-plus-capacity; debtor-accessible liquidity ID L-ACC is unverified. [C7, C8, C9, C10, C14, C28, C35]

#### T2H.1 — Source and identity gate
| source_id | upstream module/run/period | status | locator | limitation |
|---|---|---|---|---|
| U0 · CP-0 | CP-0 / COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6 / Q2 2026 | Accepted; Restricted | CZR_CP-0_20261002.md, source readiness | Partial legal and forecast source set; lineage hash retained above |
| U1 · CP-1 | CP-1 / COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6 / Q2 2026 | Accepted; Restricted | CZR_CP-1_20261002.md, T4.8–T4.19 | Canonical history exists; quarterly CFO and covenant EBITDA missing |
| U2 · CP-2A | CP-2A / COS-20261012T160551Z-a27732bdb7f3447399dc538ced7614a6 / Q2 2026 | Accepted; Restricted | CZR_CP-2A_20261002.md, T2B.4–T2B.9 | Directional first break, not numeric stress |
| S1 · f991456d-d304-4d03-9648-bcdf899ce7a5 | Primary filing / CZR / FY2025 | Audited historical source | 10-K statements and MD&A, evidence pp.19, 30–32 [C1, C2, C3, C4] | Annual figures do not supply FY2026–FY2028 forecasts |
| S2 · 439e1450-b5ae-4830-b4c3-3719da918fe3 | Primary filing / CZR / Q2 2026 | Unaudited current source | 10-Q statements, notes and MD&A, evidence pp.2–5, 9, 20–22 [C5, C7, C9, C12, C15, C18] | H2 CFO and full multi-year driver set absent |
| S3 · 88bbc140-036a-46e0-8935-18a611301c95 | Issuer release / CZR / Q2 2026 | Corroborating only | Results summary, evidence p.1 [C5, C6] | Filing controls definitions; no independent forward forecast |

#### T2H.2 — Historical-to-base bridge
| metric | historical actual | LTM/base | adjustment | basis | evidence_id |
|---|---|---|---|---|---|
| Revenue, consolidated USDm | FY2025 11,486; H1 2026 5,863; H1 2025 5,701 | LTM June 2026 11,648 | +162 = 5,863 − 5,701 | calculated; FY + current H1 − prior H1; Windsor comparison changes | [C1, C5, C36] |
| Issuer Adjusted EBITDA, USDm | FY2025 3,624; H1 2026 1,807; H1 2025 1,839 | LTM June 2026 3,592 | −32 = 1,807 − 1,839 | calculated; E-ADJ, not E-COV | [C2, C6, C28] |
| Reported CFO, USDm | FY2025 1,302; H1 2026 675; H1 2025 680 | LTM June 2026 1,297 | −5 = 675 − 680 | calculated; after cash interest/taxes; cannot be relabelled pre-interest CFO | [C3, C7, C29] |
| Cash property/equipment capex, USDm | FY2025 805; H1 2026 335; H1 2025 453 | LTM June 2026 687 | −118 = 335 − 453 | calculated; positive spending magnitude | [C4, C8] |
| FCF after property/equipment capex, USDm | FY2025 497; H1 2026 340; H1 2025 227 | LTM June 2026 610 | +113 = 340 − 227 | calculated; CFO − cash capex; excludes separate acquisition uses | [C3, C4, C7, C8] |
| Debt carrying value, USDm | December 2025 11,784 | June 2026 11,699 | −85 balance-sheet change | calculated; D-BS; face and note-book alternatives in CF-1 | [C9, C10, C12, C13] |
| Unrestricted cash, USDm | December 2025 887 | June 2026 965 | +78 balance-sheet change | source_fact; debtor availability unverified | [C11] |
| Organic segment-growth normalization, USDm | Regional/Managed prior mix | — | — | analyst_judgment; no like-for-like Windsor bridge, so no numeric adjustment | [C36] |

#### T2H.3 — Assumption register
| assumption_id | driver | case | period | value/range | unit | class | source | rationale |
|---|---|---|---|---|---|---|---|---|
| A01 | H2 disclosed debt service, not a CFO deduction | base | FY2026 H2 | approximately 425 | USDm | source_fact | S2, MD&A p.22 [C15] | Includes principal and interest; informational funding window, not a forecast assumption about sources |
| A02 | H2 VICI/GLPI payments | base | FY2026 H2 | approximately 687 | USDm | source_fact | S2, MD&A p.22 [C16] | Fixed-cash-use monitor; do not deduct disclosed interest twice from CFO |
| A03 | H2 property/equipment capex | base | FY2026 H2 | 310–390 | USDm | management_guidance | S2, MD&A p.22 [C17] | Disclosed estimated range; neither endpoint is selected as a point forecast |
| A04 | Scheduled principal maturity | base | FY2027 | 114 | USDm | source_fact | S2, Note 6 p.9 [C18] | Contractual schedule, not proof of cash settlement without refinancing |
| A05 | Scheduled principal maturity | base | FY2028 | 767 | USDm | source_fact | S2, Note 6 p.9 [C18] | Refinancing exposure; no refinancing coupon or issuance assumed |
| A06 | Las Vegas visits, table hold and rooms | downside | FY2026 H2–FY2028 | unquantified — persistence and cash sensitivity not sourced | qualitative | analyst_judgment | S2, segment MD&A p.20 [C19, C46] | First operating break; not a numerical EBITDA haircut |
| A07 | Digital gaming tax/hold contribution | downside | FY2026 H2–FY2028 | unquantified — incremental forward tax/hold path absent | qualitative | analyst_judgment | S2, Digital MD&A p.21 [C21] | Margin transmission, not an invented percentage |
| A08 | Regional contribution and cash conversion | upside | FY2026 H2–FY2028 | unquantified — persistence and segment-to-CFO bridge absent | qualitative | analyst_judgment | S2, Regional MD&A p.20 [C20] | Disconfirming operating offset |
| A09 | Revenue, margin and working-capital continuation | base | FY2026 H2–FY2028 | unquantified — no complete projected drivers | qualitative | analyst_judgment | S2, statements and MD&A pp.3, 20–22 [C5, C19] | No flat historical run rate is assumed |
| A10 | Minimum cash, future interest/tax and borrower access | base | FY2026 H2–FY2028 | unquantified — required numerical inputs absent | qualitative | analyst_judgment | S2, liquidity/interest disclosures pp.5, 22 [C14, C29, C30] | Prevents fabricated cash and liquidity runway |
| A11 | Dividends, buybacks and transaction funding | downside | FY2026 H2–FY2028 | unquantified — merger outcome and future financing absent | qualitative | analyst_judgment | S2, Note 1 and repurchase disclosure pp.5, 13 [C25, C38] | No repayment, equity issuance or merger cash plug |
| A12 | Debt issuance, optional repayment and acquisitions/disposals | upside | FY2026 H2–FY2028 | unquantified — financing and transaction path absent | qualitative | analyst_judgment | S2, debt/merger disclosures pp.5, 9 [C18, C25] | Explicit missing movements, not assumed zeros |

A06–A12 describe case mechanics and gaps, not management forecasts, consensus or ready numeric drivers. Debt, rent and capex figures A01–A05 cannot establish opening-to-closing balances without their missing counterparts. Neither reported compliance nor the disclosed repurchase expectation is a forecast of future covenant headroom or a sourced zero in a model driver. [C27, C38]

#### T2H.4 — Forward operating model
| period | case | revenue | EBITDA | margin | CFO | capex | FCF | evidence/assumption IDs |
|---|---|---|---|---|---|---|---|---|
| LTM June 2026 actual-derived | historical reference | 11,648 | 3,592 | 30.84% | 1,297 | 687 | 610 | E-ADJ; FY2025 + H1 2026 − H1 2025; CFO − capex [C1, C2, C3, C4, C5, C6, C7, C8] |
| H1 2026 reported/derived | historical reference | 5,863 | 1,807 | 30.82% | 675 | 335 | 340 | E-ADJ; CFO − capex [C5, C6, C7, C8] |
| FY2026 | base | — | — | — | — | — | — | A01–A05, A09–A10; G-FWD: H2 drivers and operating cash absent [C15, C16, C17] |
| FY2027 | base | — | — | — | — | — | — | A04, A09–A10; G-FWD: principal schedule alone is insufficient [C18] |
| FY2028 | base | — | — | — | — | — | — | A05, A09–A10; G-FWD: no operating or refinancing forecast [C18] |
| FY2026 | upside | — | — | — | — | — | — | A08, A12; G-FWD: Regional offset unquantified [C20] |
| FY2027 | upside | — | — | — | — | — | — | A08, A12; G-FWD: future operating and financing drivers absent [C20] |
| FY2028 | upside | — | — | — | — | — | — | A08, A12; G-FWD: 2028 refinancing path absent [C18] |
| FY2026 | downside | — | — | — | — | — | — | A06–A07, A11; G-FWD: operating first break not a forecast number [C19, C21] |
| FY2027 | downside | — | — | — | — | — | — | A06–A07, A11; G-FWD: cash-conversion sensitivity absent [C19, C21] |
| FY2028 | downside | — | — | — | — | — | — | A05–A07, A11; G-FWD: no stressed refinance capacity [C18, C19] |

Historical margin is E-ADJ divided by reported/constructed revenue. No forecast FCF is computed by replacing missing CFO with reported after-interest history or assuming a capex-range midpoint. The forecast arithmetic is **unavailable**, rather than balanced by a silent residual.

#### T2H.5 — Debt and liquidity roll-forward
| period | case | opening debt/cash | issuance | repayment | interest | closing debt/cash | accessible liquidity |
|---|---|---|---|---|---|---|---|
| H1 2026 observed; D-BS USDm | historical reference | 11,784 / 887 | 885 proceeds | 983 repayments | debt cash interest 368, already in CFO | 11,699 / 965; principal-flow-only implied debt 11,686, carrying-value bridge residual +13; unrestricted-cash change +78 versus all-cash change +93 | L-REP 2,928 reported; L-ACC debtor-specific — [C9, C10, C11, C14, C29, C39, C40, C43] |
| FY2026 H2 | base | June 11,699 / 965 | — | scheduled remaining principal 55; cash settlement/financing unknown | included in 425 debt-service estimate; distinct cash-interest forecast — | — / —; roll-forward Not Calculable from Provided Materials — issuance, CFO and other cash movements missing | —; reported June L-REP is not a forecast [C11, C15, C18] |
| FY2027 | base | — / — | — | scheduled principal 114; refinancing treatment unknown | — | — / —; roll-forward Not Calculable from Provided Materials — opening and movements missing | — [C18] |
| FY2028 | base | — / — | — | scheduled principal 767; refinancing treatment unknown | — | — / —; roll-forward Not Calculable from Provided Materials — opening and movements missing | — [C18] |
| FY2026–FY2028 | upside | — / — | — | — | — | — / —; roll-forward Not Calculable from Provided Materials — named drivers lack amounts | — [C18, C20] |
| FY2026–FY2028 | downside | — / — | — | — | — | — / —; roll-forward Not Calculable from Provided Materials — stressed CFO and financing missing | — [C18, C19, C21] |

**Observed reconciliation control:** H1 financing reports $885 million debt proceeds and $983 million repayments, a $98 million net principal repayment; the carrying-value decrease is $85 million. Their $13 million difference is exposed, not attributed without an item-level carrying-value movement schedule. Reported CFO $675 million, investing $(411) million and financing $(171) million sum to $93 million growth in **cash including restricted amounts**; unrestricted balance-sheet cash increased $78 million, leaving a $15 million scope difference. Neither difference is a forward-model plug. [C7, C39, C40, C41, C42, C43, C11]

#### T2H.6 — Credit metrics
| period | case | gross/net leverage | coverage | FCF/debt | liquidity runway | definition IDs |
|---|---|---|---|---|---|---|
| June 2026 / LTM reference | historical | gross 3.26x = 11,699/3,592; consolidated unrestricted-cash proxy net 2.99x = (11,699−965)/3,592; debtor-accessible net — | P&L-interest basis 1.57x = 3,592/(2,304+1,142−1,153); alternative cash debt-interest 4.63x = 3,592/(813+368−405); alternative debt-plus-rent cash-interest 1.68x = 3,592/((813+368−405)+(1,349+686−672)) | 5.21% = 610/11,699 | Not Calculable from Provided Materials — no minimum cash or timed cash forecast | D-BS; E-ADJ; E-COV unavailable; L-ACC unverified; P&L interest and cash alternatives distinct [C2, C6, C9, C10, C11, C28, C29, C30, C31, C32, C33, C34] |
| FY2026 | base/upside/downside | — / — | — | — | Not Calculable from Provided Materials — missing H2 CFO and minimum cash | D-BS; E-ADJ; E-COV unavailable; G-FWD [C15, C16, C17] |
| FY2027 | base/upside/downside | — / — | — | — | Not Calculable from Provided Materials — missing cash, debt and refinancing movements | D-BS; E-ADJ; E-COV unavailable; G-FWD [C18, C26] |
| FY2028 | base/upside/downside | — / — | — | — | Not Calculable from Provided Materials — scheduled maturity does not establish funding | D-BS; E-ADJ; E-COV unavailable; G-FWD [C18] |

These are non-contractual historical ratios. The P&L interest denominator is net reported expense; the two cash-interest alternatives do not substitute for it. CFO already includes operating interest and taxes. Cash paid on financing obligations is separately relevant although the balance-sheet obligation is not added to D-BS. Contractual fixed-charge coverage, covenant EBITDA, permitted cash netting and headroom remain **Not Calculable from Provided Materials**. [C27, C28, C29, C30, C35]

#### T2H.7 — Scenario and breakpoint matrix
| driver shock | first break | period | liquidity/covenant/refinancing consequence | recovery action |
|---|---|---|---|---|
| Base: reported mix continues without an assumed growth rate | H2 cash generation must fund disclosed uses; quantitative minimum not located | FY2026 H2 | Liquidity path and covenant headroom Not Calculable from Provided Materials — CFO and contractual tests absent; monitor 2028 principal | Obtain quarterly CFO, project capex and debtor cash; update cash bridge [C15, C16, C17, C18] |
| Upside: Regional earnings and durable lower capex offset Las Vegas | Cash conversion holds rather than reported CFO weakening | FY2026 H2 onward, conditional | May reduce refinancing reliance; neither a cash balance nor leverage target follows without amounts | Verify like-for-like Windsor contribution and sustainable maintenance cash spending [C7, C8, C20, C36] |
| Downside: persistent Las Vegas visitation/hold weakness, with digital tax pressure | Gaming/hotel contribution falls before debt and rent requirements reset | FY2026 H2 earliest observable inflection; not a predicted occurrence | CFO/FCF could decline, leading to cash/revolver reliance; actual covenant breakpoint and FY2028 financing gap Not Calculable from Provided Materials | Review visitation, hold, room yield, CFO, cash and drawings together; request test certificate [C19, C21, C46, C15, C16, C18, C27] |
| Event overlay: proposed merger remains pending | Approval/financing or end-date status changes | FY2027; initial end date May 27 | Post-close funding, liquidity and claim effects cannot be quantified from June data | Obtain financing commitments and filed operative agreement; do not presume closing or a termination payment [C25, C26] |
| Float runoff: gaming deposits withdrawn or fulfilled without replacement | Customer-liability balance contracts | First observed future reporting period, date unknown | Cash can fall ahead of debt principal; not ordinary supplier payables | Monitor deposits and settlement cash with reported liquidity [C22, C23, C24] |

The downside is deliberately causal, not a numerical haircut: initiation in Las Vegas demand/hold → operating contribution → CFO and non-debt float → cash or revolver use → covenant/refinancing scrutiny. A certified test deterioration or persistent cash decline with rising drawings, not an invented ratio threshold, is the escalation signal.

#### T2H.8 — Deleveraging and monitoring handoff
| case | trajectory | target/date | dependency | trigger | downstream module |
|---|---|---|---|---|---|
| base | Historical carrying debt declined $85m through June; subsequent deleveraging not established | FY2026–FY2028: no supported leverage target | H2 CFO, debt movements, minimum cash and accessible revolver | Updated cash/debt schedule and 2028 refinancing plan | CP-2H, CP-4C [C9, C10, C18] |
| upside | Conditional faster cash-supported repayment; no numeric debt trajectory | FY2026 H2 onward, conditional | Sustained Regional contribution and maintenance-adjusted FCF | Repeated CFO after necessary capex covers fixed uses | CP-2H [C7, C8, C20] |
| downside | Conditional slower deleveraging or refinancing reliance | First operational test FY2026 H2; principal inflection FY2028 | Persistent weaker Vegas contribution, deposit cash needs, financing access | Weaker cash with rising revolver drawings or shrinking certified covenant cushion | CP-2H, CP-4C [C18, C19, C22, C27] |
| all cases | No consumable CP-MODEL numerical periods | FY2026–FY2028 | Active division growth and all four other flow drivers must be sourced and READY | Supply complete underwriting drivers; rerun CP-2G before workbook use | CP-MODEL [C5, C18] |

CP-2H may use these as **conditional monitoring pathways**, not projected rating-trigger headroom; CP-4C must obtain governing transaction and debt evidence before changing claim treatment. This module issues no rating, security preference, legal capacity determination or investment recommendation.

#### T2H.9 — Gaps and conflicts
| item | conflict/gap | affected case/period | model impact | required evidence |
|---|---|---|---|---|
| G-FWD | Complete division growth, margin, working capital, pre-interest/pre-tax CFO, future cash interest/taxes, minimum cash and financing flows not supplied | All cases FY2026–FY2028 | No balanced numeric forecast or CP-MODEL-ready case; reported CFO cannot populate pre-interest/pre-tax `cfo` | Dated operating forecast and full finance/cash-flow driver pack [C5, C7, C15, C17] |
| CF-1 | June debt note face $11,807m, note book $11,705m and D-BS $11,699m; separate deferred revolver charge $(6)m. Face-to-D-BS $108m; note-book-to-D-BS $6m | Historical opening; every forward case | Principal schedules cannot silently roll carrying debt; observed H1 principal-flow versus carrying movement leaves $13m bridge difference | Issuance-cost and other carrying-value roll-forward [C9, C10, C12, C13, C39, C40] |
| CF-2 | Reported issuer Adjusted EBITDA is not covenant EBITDA; financing obligations classified separately from debt but their interest consumes cash | All cases | No actual leverage/fixed-charge covenant headroom or refinancing-capacity test | Applicable covenant definitions, test certificates and entity-level fixed-charge inputs [C27, C28, C30, C35] |
| CF-3 | H1 unrestricted cash rises $78m; total cash including restricted rises $93m | Historical opening | $15m perimeter difference cannot become a cash forecast plug | Restricted/escrow and operational-cash movement by debtor [C11, C43] |
| G-PERIM | Windsor moves from managed fees to consolidated Regional operations March 3; CVA borrower has separate facilities | Base/upside/downside FY2026 onward | Historical segment growth and debtor liquidity not like-for-like | Property-level comparative and guarantor/borrower cash allocation [C36] |
| G-FLOAT | Customer deposits/deferred revenue increase $53m, but refund, settlement and replacement cadence absent | Base/downside FY2026 onward | Cannot use float as permanent cash or model runoff | Customer-liability cash and aging schedule [C22, C23, C24] |
| G-MERGER | Pending May merger has conditional approvals; financing and consummation cash not in delivered source set | Event overlay FY2027–FY2028 | No post-merger pro forma debt, cash, maturity or covenant path | Executed full transaction agreement, commitments and subsequent filings [C25, C26, C47] |
| G-ACCESS | Reported $2,928m combines cash and borrowing capacity; debtor-accessible unrestricted and operationally required cash unspecified | All cases | Net leverage proxy is not actual accessible-cash netting; no minimum runway | Borrower-level cash, restriction and availability schedule [C11, C14, C44, C45] |
| G-CAPEX | Disclosed H2 capex is a range, not project cash timing or historical maintenance requirement | All cases FY2026 onward | Cannot choose range midpoint or declare sustainable H1 FCF | Project-level maintenance/growth timetable and committed spend [C8, C17] |
| G-POST | July 13 Alberta launch follows June balance-sheet date; impact not quantified | FY2026 onward | No June pro forma adjustment or assumed forecast benefit | Subsequent period operating disclosure [C37] |

#### cp2g.cp_model_forecast_drivers
<!-- table-id: cp2g.cp_model_forecast_drivers -->
| driver_id | slot_id | case | period_id | fiscal_year | value | unit | assumption_id | status | source_id | source_locator | as_of |
|---|---|---|---|---:|---|---|---|---|---|---|---|
| division_growth | DIVISION_1 | BASE | FY2026 | 2026 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.20; forward rate absent [C19] | 2026-10-02 |
| division_growth | DIVISION_2 | BASE | FY2026 | 2026 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.20; forward rate absent [C20] | 2026-10-02 |
| division_growth | DIVISION_3 | BASE | FY2026 | 2026 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.21; grouped rate absent [C21] | 2026-10-02 |
| acquisitions_disposals |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q cash flow p.4; FY future total absent [C41] | 2026-10-02 |
| net_equity_issue_repay |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q repurchase note p.13; future amount absent [C38] | 2026-10-02 |
| dividends_paid |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q financing cash flow p.4; future amount absent [C42] | 2026-10-02 |
| other_investing_financing |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q cash flow p.4; future components absent [C41, C42] | 2026-10-02 |
| division_growth | DIVISION_1 | BASE | FY2027 | 2027 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.20; forward rate absent [C19] | 2026-10-02 |
| division_growth | DIVISION_2 | BASE | FY2027 | 2027 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.20; forward rate absent [C20] | 2026-10-02 |
| division_growth | DIVISION_3 | BASE | FY2027 | 2027 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.21; grouped rate absent [C21] | 2026-10-02 |
| acquisitions_disposals |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; future cash unknown [C25] | 2026-10-02 |
| net_equity_issue_repay |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; future equity unknown [C25] | 2026-10-02 |
| dividends_paid |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q liquidity MD&A p.22; amount absent [C14] | 2026-10-02 |
| other_investing_financing |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q debt schedule p.9 is not financing flow [C18] | 2026-10-02 |
| division_growth | DIVISION_1 | BASE | FY2028 | 2028 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.20; forward rate absent [C19] | 2026-10-02 |
| division_growth | DIVISION_2 | BASE | FY2028 | 2028 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.20; forward rate absent [C20] | 2026-10-02 |
| division_growth | DIVISION_3 | BASE | FY2028 | 2028 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q segment MD&A p.21; grouped rate absent [C21] | 2026-10-02 |
| acquisitions_disposals |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; future outcome unknown [C25] | 2026-10-02 |
| net_equity_issue_repay |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; future funding unknown [C25] | 2026-10-02 |
| dividends_paid |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q liquidity MD&A p.22; amount absent [C14] | 2026-10-02 |
| other_investing_financing |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q maturity note p.9; refinance flow unknown [C18] | 2026-10-02 |
| division_growth | DIVISION_1 | DOWNSIDE | FY2026 | 2026 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Las Vegas MD&A p.20; stress rate absent [C19] | 2026-10-02 |
| division_growth | DIVISION_2 | DOWNSIDE | FY2026 | 2026 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Regional MD&A p.20; stress rate absent [C20] | 2026-10-02 |
| division_growth | DIVISION_3 | DOWNSIDE | FY2026 | 2026 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Digital MD&A p.21; grouped stress rate absent [C21] | 2026-10-02 |
| acquisitions_disposals |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q cash flow p.4; future total absent [C41] | 2026-10-02 |
| net_equity_issue_repay |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q repurchase note p.13; future amount absent [C38] | 2026-10-02 |
| dividends_paid |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q financing cash flow p.4; future amount absent [C42] | 2026-10-02 |
| other_investing_financing |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q cash flow p.4; stressed future flows absent [C41, C42] | 2026-10-02 |
| division_growth | DIVISION_1 | DOWNSIDE | FY2027 | 2027 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Las Vegas MD&A p.20; stress rate absent [C19] | 2026-10-02 |
| division_growth | DIVISION_2 | DOWNSIDE | FY2027 | 2027 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Regional MD&A p.20; stress rate absent [C20] | 2026-10-02 |
| division_growth | DIVISION_3 | DOWNSIDE | FY2027 | 2027 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Digital MD&A p.21; grouped stress rate absent [C21] | 2026-10-02 |
| acquisitions_disposals |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; outcome unknown [C25, C26] | 2026-10-02 |
| net_equity_issue_repay |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; financing unknown [C25] | 2026-10-02 |
| dividends_paid |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q liquidity MD&A p.22; amount absent [C14] | 2026-10-02 |
| other_investing_financing |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q maturity note p.9; stressed financing absent [C18] | 2026-10-02 |
| division_growth | DIVISION_1 | DOWNSIDE | FY2028 | 2028 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Las Vegas MD&A p.20; stress rate absent [C19] | 2026-10-02 |
| division_growth | DIVISION_2 | DOWNSIDE | FY2028 | 2028 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Regional MD&A p.20; stress rate absent [C20] | 2026-10-02 |
| division_growth | DIVISION_3 | DOWNSIDE | FY2028 | 2028 | null | PERCENT_DECIMAL | G-FWD | NOT_APPLICABLE | S2 | 10-Q Digital MD&A p.21; grouped stress rate absent [C21] | 2026-10-02 |
| acquisitions_disposals |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; outcome unknown [C25] | 2026-10-02 |
| net_equity_issue_repay |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q merger disclosure p.5; funding unknown [C25] | 2026-10-02 |
| dividends_paid |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q liquidity MD&A p.22; amount absent [C14] | 2026-10-02 |
| other_investing_financing |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | G-FWD | NOT_APPLICABLE | S2 | 10-Q maturity note p.9; stressed refinance unknown [C18] | 2026-10-02 |

All three division slots are **active**, using CP-1's explicit allocation: DIVISION_1 = LAS_VEGAS; DIVISION_2 = REGIONAL; DIVISION_3 = DIGITAL, MANAGED and CORPORATE grouped. No slot was inferred from display order. The required `NOT_APPLICABLE` vocabulary here denotes a null, **not an inactive division, zero growth or usable period**. No BASE or DOWNSIDE FY2026–FY2028 period is CP-MODEL-consumable; missing early-period drivers also invalidate dependent later periods. No zero or future vendor-signed cash-flow assignment was fabricated.

## Evidence Trace

| Claim | Marker | Document | Page / use |
|---|---|---|---|
| FY2025 audited operating and cash anchors | [C1, C2, C3, C4] | CZR FY2025 Form 10-K | Evidence pp.19, 31; LTM FY component |
| H1 operating, CFO and capex anchors | [C5, C6, C7, C8] | CZR Q2 2026 Form 10-Q | Evidence pp.2, 4, 16; LTM stub and cash conversion |
| June carrying/face debt and cash | [C9, C10, C11, C12, C13] | CZR Q2 2026 Form 10-Q | Evidence pp.2, 9; CF-1 distinctions |
| Liquidity and disclosed future cash uses | [C14, C15, C16, C17, C18, C44, C45] | CZR Q2 2026 Form 10-Q | Evidence pp.9, 22; funding windows, not balances |
| Segment stress and contrary operating evidence | [C19, C20, C21, C46] | CZR Q2 2026 Form 10-Q | Evidence pp.20–21; scenario mechanics |
| Deposits, transaction and compliance | [C22, C23, C24, C25, C26, C27, C47] | CZR Q2 2026 Form 10-Q | Evidence pp.5, 10–11; conditionality and float |
| Interest and separately classified obligations | [C28, C29, C30, C31, C32, C33, C34, C35] | CZR Q2 2026 Form 10-Q; FY2025 Form 10-K | Evidence pp.2–5, 21, 30, 32; distinct coverage denominators |
| Entity change, post-period event, financing movements | [C36, C37, C38, C39, C40, C41, C42, C43] | CZR Q2 2026 Form 10-Q | Evidence pp.4, 6, 13, 17; perimeter and observed roll-forward |

**Formula lineage:** LTM flow = FY2025 + H1 2026 − H1 2025. FCF = reported CFO − positive cash property/equipment spending; cash interest/taxes are not subtracted again. Historical gross leverage = D-BS/E-ADJ. The 2.99x net figure deducts consolidated cash only as a labelled proxy; actual debtor-accessible netting is unknown. Coverage always states whether its denominator is P&L net interest, cash debt interest or cash debt-plus-rent interest. Forward debt = opening carrying debt + supported issuance/PIK − supported repayments ± supported carrying/perimeter movements; forward cash requires CFO, investing and financing movements on a matching unrestricted-cash perimeter. None is solved by an unsourced plug.

## Source Registry

T2H.1 identifies all current direct sources and the three accepted same-run handoffs. CP-1 supplies the canonical financial definition and explicit segment-slot mapping; CP-2A supplies the causal first-break pathway, not stress quantities. The SEC 10-Q controls current reported amounts; the audited 10-K supplies FY2025 components; the release corroborates results only. There is no externally supplied consensus, management multi-year forecast, user-approved numerical assumption or borrower-specific cash allocation in this delivered set. No external retrieval or research brief is provided.

## Gaps & Conflicts

T2H.9 is the controlling issue register. The most important conflict is not a competing forward projection: **there is no supported quantitative forward operating and financing projection**. The issuer's remaining-year capex range and contractual principal schedule are partial inputs, not permission to invent revenue, EBITDA, CFO, dividends or refinancing. An H1 reported CFO amount is after cash interest and taxes; it cannot populate a forecast `cfo` slot defined before those payments. The debt-face/book/carrying alternatives and the $13 million observed principal-flow-versus-carrying bridge difference remain visible. The current cash-plus-capacity number must not be equated with cash available to every borrower. [C7, C9, C10, C12, C13, C14, C29, C39, C40, C44, C45]

**Research questions for a later sourced run:** What are management's or an explicitly authorized analyst's FY2026 H2–FY2028 segment, margin and working-capital drivers? What are actual debt-document covenant EBITDA, test headroom and debtor-available cash? What financing accompanies a consummated merger? Those questions are unresolved here, not assigned to a nonexistent research process. The first new certified cash/covenant statement or transaction-financing filing should trigger recalculation rather than a silent edit to these cases. [C25, C27, C28]

## QA Validation

| Self-check | Result | Basis and disposition |
|---|---|---|
| Issuer, period and accepted lineage | PASS locally | Three accepted matching upstream hashes retained exactly; FY2025 audited plus Q2 2026 unaudited anchored. |
| Forecast scope and case isolation | RESTRICTED | FY2026–FY2028 base/upside/downside named; only historical amounts and partial future windows quantified. No numerical case is represented as balanced. |
| Assumption class, units and source | PASS locally | T2H.3 separates facts, disclosed estimate and analyst-judgment mechanisms; unquantified values remain explicit. |
| Debt/cash identity and residual visibility | RESTRICTED | Observed $13m debt-basis and $15m cash-perimeter differences exposed; prospective checks cannot run and are not reported as passed. |
| FCF, interest, lease and perimeter consistency | PASS locally with limitation | Reported CFO is after cash interest; alternative coverage denominators distinguished; debtor cash and E-COV unavailable. |
| Downside first break and contrary challenge | PASS locally | Las Vegas operating deterioration precedes cash pressure; Regional earnings and reduced capex could defeat the squeeze thesis if durable. |
| CP-MODEL interface completeness and consumption | RESTRICTED | Forty-two required BASE/DOWNSIDE rows present; all active division and flow values null; every dependent forecast period unavailable. |
| Confidence self-assessment | RESTRICTED | Ten material claims: seven directly sourced, two calculated, one insufficient (E=88); 70% assessed source/schema coverage (C=70); partial source gate S=0.7; one material analytical limitation P=15. Formula rounds to 42/Low; Restricted. |
| Canonical structure and host checks | PASS locally; HOST PENDING | Exact filename and six ordered H2 headings specified; T2H.1–T2H.9 and tagged stable table present. Host validation and completeness checks follow this answer; no exit status or exported-file confirmation is asserted. |

**Downstream restriction:** CP-2H and CP-4C receive historical metrics, dated refinancing exposure and monitoring triggers, not modelled covenant or recovery outcomes. CP-MODEL receives a structurally complete but entirely unconsumable forward-driver table. Obtain the named assumptions and controlling transaction/covenant evidence, then rerun CP-2G before using forecast leverage, minimum liquidity or refinancing capacity in a decision.