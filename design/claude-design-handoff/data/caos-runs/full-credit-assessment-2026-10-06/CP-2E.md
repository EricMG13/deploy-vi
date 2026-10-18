---
module_id: "CP-2E"
module_name: "MacroFXHedgingSensitivity"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2E-6f7a0d50ae2f308c"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-09-CP-2E"
credit_os_invocation_sha256: "48263b6f2e3cfa4c561e2725f7b84ef732f1af35b60b466fb6bf08019e891cda"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
confidence_score: 59
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags: [SOURCE_LIMITED_NOT_COMMITTEE_READY, FX_CURRENCY_DETAIL_UNAVAILABLE, HEDGE_TERMS_LIMITED, COST_PASS_THROUGH_UNQUANTIFIED, ESG_DISCLOSURE_LIMITED]
validation_warnings: [FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED, NO_POST_Q2_2026_FINANCIALS]
downstream_consumers: [CP-6, CP-5, CP-5A]
---

## Audit Summary

Canonical handoff filename: `CZR_CP-2E_20261002.md`. Module status: **Ready with Limitations**; the accepted CP-0 source-readiness artifact matches issuer, period and run lineage. The Q2 2026 filing identifies approximately $6.0 billion of floating-rate borrowings and states that no cash-flow hedges or trading derivatives were held as of June 30, 2026. A mechanically derived +100 bps annualized cash-interest change is approximately $60 million, before any paydown, rate movement, facility margin step-down, or other offset. The annual report’s prior-period $61 million sensitivity is a useful reasonableness check, not a Q2 2026 input. FX currency matching and commodity-cost sensitivities are not calculable from the supplied data. CP-2, CP-1 and CP-1A analytical handoffs were not supplied; whole-credit integration is therefore limited. Self-check complete; host validation follows this response.

Confidence: E=90, C=80, S=0.70, P=0; formula gives 60.2 before the material-gap cap, so the reported score is capped at 59 (Low) under the Restricted status. The primary limitation is incomplete exposure/hedge/currency and input-cost detail, not absence of an identifiable rate exposure.

## Analysis

### Macro and hedging view

Caesars’ largest evidenced macro exposure is floating-rate debt: approximately $6.0 billion, or about 51% of long-term debt as reported, with no derivatives held at June 30, 2026. Applying the module’s +100 bps convention to that rounded exposure gives an approximately $60 million annualized increase in cash interest if the shock persists and the exposure is unchanged; the cash-flow consequence is lower FCF and less capacity for rent, debt service and investment. CPI-linked VICI rent and labor/tax pressure add unquantified cost sensitivity. Currency-specific revenue, cost, debt and cash data are absent, so FX mismatch cannot be rated from geography alone. The strongest counterpoint is that reported interest expense fell year over year, primarily with lower variable rates and reduced debt; sustained lower rates or further debt reduction would reduce the pressure, but do not remove the floating exposure. [C8, C9, C10, C14]

The compact table below distinguishes the quantified rate channel from directional or unquantifiable exposures; it does not assume unreported hedge coverage or pass-through.

| Driver | Evidence at Q2 2026 | Mitigation / limitation | Indicative credit channel | Monitoring trigger |
|---|---|---|---|---|
| Floating rates | ~$6.0bn floating borrowings; no derivatives held [C8, C9] | No disclosed hedge coverage; exposure is rounded | +100 bps ≈ $60m annualized interest; lower FCF [C8] | Variable debt, reference rates, cash interest and paydown |
| Lease inflation | CPI-based VICI escalations; ~$687m estimated VICI/GLPI rent for remainder of 2026 [C12, C13] | CPI escalator transfers inflation to rent; no rent hedge disclosed | Higher recurring cash rent can constrain liquidity and investment | November rent reset and actual lease payments |
| Labor / gaming taxes | Q2 report attributes flat Regional EBITDA margin partly to increased labor costs and gaming taxes [C19] | Cost efficiencies cited, but no quantified offset or pricing pass-through | Margin and FCF pressure | Wage settlements, tax-rate changes and segment margins |
| FX / energy / water | Aggregate FX/other OCI is disclosed; utility exposure is identified [C15, C26] | No currency-level exposure or cost base | Cannot size transaction FX or commodity sensitivity | Currency disclosures; utility expense and rates |

### Rate exposure and downside path

The debt table identifies five variable-rate facilities and fixed-coupon notes. The Q2 filing separately reports approximately $6.0 billion of variable-rate borrowings and says those borrowings are approximately 51% of consolidated long-term debt. The no-derivative disclosure supports treating the disclosed floating-rate base as unhedged for this snapshot; it does not establish protection after June 30 or exclude contractual changes in debt balances. [C1, C2, C3, C4, C5, C8, C9, C10]

**Downside sequence:** a sustained rise in Term SOFR/base rates first raises interest on the variable facilities; higher cash interest reduces operating cash available after rent and capital spending; weaker retained cash can increase revolver use and reduce debt-service flexibility, making refinancing more sensitive to market access. The estimated $60 million per +100 bps is annualized, not a forecast, and does not include rate path, debt amortization, covenant definitions or incremental borrowings. Monitor actual cash interest, variable balances, and the reported liquidity/covenant position. No covenant-headroom inference is made.

The contrary evidence is that Caesars reported a year-over-year decline in interest expense, primarily from reduced debt and lower variable-rate interest expense. This reduces near-term conviction that rates are currently worsening cash interest, but the conclusion would shift materially if lower rates persist alongside debt reduction; the source set does not provide a forward curve or a fully current debt schedule to quantify that case. [C14]

### FX, commodity and inflation read-through

The filing includes foreign-currency and other comprehensive-income movements, and Caesars has operations and leases in Canada. Neither item supplies currency-disaggregated revenues, costs, EBITDA, debt, cash, covenant denomination, transaction exposure, or repatriation restrictions. The translation line is not a substitute for those measures; therefore, natural hedge, mismatch and FX sensitivity remain unclassified rather than presumed immaterial. [C15, C27]

Rent inflation is the best evidenced non-rate macro channel: VICI lease escalations are linked to CPI, and the issuer estimated approximately $687 million of VICI/GLPI lease payments for the remainder of 2026. The CPI mechanism increases rent when the index escalates, with potential cash-flow lag or squeeze not quantified here. Labor costs and gaming taxes are also identified as affecting segment margins, while energy and water are described as significant operating inputs; no cost breakdown or supported pass-through formula is supplied. As a result, no numerical inflation, energy, wage, FX or FCF stress is presented beyond the rate calculation. [C12, C13, C19, C26]

### Credit implication

**Highest-priority macro factor:** unhedged floating-rate exposure. Evidence: approximately $6.0 billion of floating-rate borrowings and no derivatives at June 30, 2026 [C8, C9]. Risk mechanic: higher reference rates raise cash interest on that debt; absent offsetting cash generation or deleveraging, FCF and liquidity after rent and capital spending decline. Credit implication: weaker debt-service capacity and reduced liquidity/refinancing flexibility under a sustained rate shock. The directional exposure is material; the $60 million per +100 bps estimate is a formula-based annualized illustration on a rounded balance, not company guidance. The cited prior-year $61 million sensitivity is consistent in scale but is dated to December 31, 2025. [C11]

**ESG / transition assessment:** Caesars reports Scope 1 and 2 reduction goals and a historical emissions reduction, while also identifying severe-weather and supply-chain impacts as potential operating risks. The goals do not establish a funded liability or quantified cost of transition. The company states that identified environmental investigation/remediation costs have not had and are not expected to have a material adverse financial effect, a meaningful counterweight to treating environmental matters as a current quantified credit detriment. Climate physical risk remains Watch because a property interruption, insurance gap or repair obligation could affect cash generation; the filing does not quantify site-level exposure. [C17, C18, C23]

Labor is the leading ESG/social operating watch: the filing identifies labor costs as one reason regional margins remained flat despite revenue growth, and its labor table lists an Atlantic City agreement with an expiration date of May 31, 2026. That date preceded this analysis date, but no post-expiration bargaining or labor-status evidence was supplied; do not infer renewal, strike or current contract status. A work stoppage or higher wage settlement could disrupt operations or increase costs, reducing FCF. [C19, C20]

**CP-6 debate handoff:** assess whether Q2 labor-cost/tax pressure and the unresolved post-May 2026 labor-contract status could impair regional margin and cash conversion; distinguish this operating channel from the independently quantified floating-rate exposure. Monitor disclosed labor outcomes and subsequent segment margins. The broader ESG-driven capital-access effect and any sustainability-linked pricing effect are not supported by the supplied sources.

### Analytical appendix — complete canonical registers

#### T2F.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars Entertainment, Inc. FY2025 Form 10-K | Primary-Verified; audited financial statements and issuer disclosures | FY ended Dec. 31, 2025 | Caesars Entertainment, Inc. and subsidiaries | Debt, rates, leases, CPI exposure, environmental/climate disclosures, labor and risk-factor context [C11, C13, C17, C18, C21, C23, C26] | Older than Q2 2026 for financial balances; no detailed FX or input-cost breakdown | Historical cross-check, lease/esg disclosures, CP-6 monitoring |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Entertainment, Inc. Q2 2026 Form 10-Q | Primary-Verified; unaudited interim filing | Quarter and six months ended June 30, 2026 | Caesars Entertainment, Inc. and consolidated subsidiaries | Debt schedule, variable-rate amount, derivative disclosure, interest expense, cash-flow, segment and lease context [C1-C10, C12, C14, C15, C19, C24, C25, C27] | No data after June 30, 2026; selected exposure inputs are rounded; no full currency or commodity cost schedule | Primary current-period rate and macro registers; CP-6 |
| c67320d0-3458-4ee9-bc3c-e1a8bc6f3c05 | MGM Resorts International Q2 2026 results release | Primary-Unverified for issuer-release metrics; separate peer issuer | Quarter and six months ended June 30, 2026 | MGM Resorts International | Peer operating, debt/lease and digital context | Not Caesars evidence; not used to estimate Caesars sensitivity | Context only; no direct input to issuer calculation |
| 156bf3bf-764e-4347-b2e7-bf6f34f22220 | PENN Entertainment Q2 2026 results release | Primary-Unverified for issuer-release metrics; separate peer issuer | Quarter and six months ended June 30, 2026 | PENN Entertainment, Inc. | Peer operating, debt/lease and digital context | Not Caesars evidence; not used to estimate Caesars sensitivity | Context only; no direct input to issuer calculation |

**Module Status:** Ready with Limitations. CP-0 accepted readiness is READY_WITH_LIMITATIONS for the matching run and reporting period. The missing CP-1/CP-1A/CP-2 handoffs limit integration, but do not replace or override the source-specific calculations below.

#### T2F.2 — Debt & Rate Exposure Register

| Debt Instrument | Amount | Fixed / Floating | Base Rate | Margin / Coupon | Currency | Maturity | Hedge Status | Source Trace | Credit Implication |
|---|---:|---|---|---|---|---|---|---|---|
| CEI Revolving Credit Facility | $120m book value, June 30, 2026 | Floating-rate debt | Adjusted Term SOFR or Base Rate | 2.25% Adjusted Term SOFR / 1.25% Base Rate, subject to disclosed step-downs | USD, reported in $ | Jan. 31, 2028 | No derivative hedge disclosed [C9] | Q2 2026 10-Q, debt table and terms, pp. 9–10 [C1] | Nearer maturity among the floating facilities; rate increases raise cash interest until repaid/refinanced. |
| CEI Term Loan A | $618m book value, June 30, 2026 | Floating-rate debt | Adjusted Term SOFR or Base Rate | 2.25% Adjusted Term SOFR / 1.25% Base Rate, subject to disclosed step-downs | USD, reported in $ | Jan. 31, 2028 | No derivative hedge disclosed [C9] | Q2 2026 10-Q, debt table and terms, pp. 9–10 [C2] | Floating cost and 2028 maturity add debt-service/refinancing sensitivity. |
| CVA Delayed Draw Term Loan | $372m book value, June 30, 2026 | Floating-rate debt | Term SOFR | Applicable margin not specified in supplied filing extract | USD, reported in $ | Apr. 26, 2029 | No derivative hedge disclosed [C9] | Q2 2026 10-Q, debt table and terms, pp. 9–10 [C3] | Adds variable-rate cost; facility is secured at Caesars Virginia and CEI is not guarantor, so do not treat it as interchangeable with parent obligations. |
| CEI Term Loan B | $1,993m book value, June 30, 2026 | Floating-rate debt | Term SOFR or Base Rate | 2.25% Term SOFR / 1.25% Base Rate | USD, reported in $ | Feb. 6, 2030 | No derivative hedge disclosed [C9] | Q2 2026 10-Q, debt table and terms, pp. 9–10 [C4] | Largest single listed floating facility; rates affect recurring cash interest. |
| CEI Term Loan B-1 | $2,808m book value, June 30, 2026 | Floating-rate debt | Term SOFR or Base Rate | 2.25% Term SOFR / 1.25% Base Rate | USD, reported in $ | Feb. 6, 2031 | No derivative hedge disclosed [C9] | Q2 2026 10-Q, debt table and terms, pp. 9–10 [C5] | Long-dated floating exposure preserves sensitivity beyond the nearer maturities. |
| CEI Senior Secured Notes due 2030 | $1,987m book value, June 30, 2026 | Fixed-rate debt | — | 7.00% coupon | USD, reported in $ | Feb. 15, 2030 | Fixed coupon; not a derivative hedge of floating facilities | Q2 2026 10-Q, debt table, p. 9 [C6] | Fixed coupon limits rate repricing on this instrument through maturity. |
| CEI Senior Secured Notes due 2032 | $1,487m book value, June 30, 2026 | Fixed-rate debt | — | 6.50% coupon | USD, reported in $ | Feb. 15, 2032 | Fixed coupon; not a derivative hedge of floating facilities | Q2 2026 10-Q, debt table, p. 9 | Fixed coupon limits rate repricing on this instrument through maturity. |
| CEI Senior Notes due 2029 | $1,193m book value, June 30, 2026 | Fixed-rate debt | — | 4.625% coupon | USD, reported in $ | Oct. 15, 2029 | Fixed coupon; not a derivative hedge of floating facilities | Q2 2026 10-Q, debt table, p. 9 [C7] | Fixed coupon; maturity/refinancing risk remains separate from rate sensitivity. |
| CEI Senior Notes due 2032 | $1,088m book value, June 30, 2026 | Fixed-rate debt | — | 6.00% coupon | USD, reported in $ | Oct. 15, 2032 | Fixed coupon; not a derivative hedge of floating facilities | Q2 2026 10-Q, debt table, p. 9 | Fixed coupon limits rate repricing on this instrument through maturity. |
| Special Improvement District Bonds | $38m book value, June 30, 2026 | Fixed-rate debt | — | 4.30% coupon | USD, reported in $ | 2037 | Fixed coupon; not a derivative hedge of floating facilities | Q2 2026 10-Q, debt table, p. 9 | Small fixed-coupon exposure; no variable-rate sensitivity implied. |
| Long-term notes and other payables | $1m book value, June 30, 2026 | Rate classification not disclosed | [Insufficient Information] — instrument-level base rate not supplied | [Insufficient Information] — coupon not supplied | USD, reported in $ | Not specified in supplied debt table | [Insufficient Information] — terms not supplied | Q2 2026 10-Q, debt table, p. 9 | Immaterial by disclosed balance but classification is not inferred. |
| Reported aggregate variable-rate borrowings | Approximately $6.0bn | Floating-rate debt | Term SOFR / facility base-rate options | Facility-specific; see rows above | USD, reported in $ | Various, 2028–2031 | No derivative instruments held at June 30, 2026 [C8, C9] | Q2 2026 10-Q, p. 23 | Principal driver of rate sensitivity; rounded issuer-reported amount is used in the sensitivity calculation. |

#### T2F.3 — Hedging Register

| Hedge Type | Notional | Instrument Covered | Rate / Strike | Maturity | Coverage Status | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| Interest-rate swap / cap / collar / other derivative | $0 held as of June 30, 2026, per issuer disclosure | No derivative-linked debt instrument disclosed | — | — | Insufficient Information for future periods; no derivatives held at the reporting date | Q2 2026 10-Q, Note 2, p. 7 [C9] | No instrument, notional schedule, strike, coverage period or hedge cliff terms; absence at June 30 does not establish later status. |
| Fixed-rate debt | See T2F.2 instrument rows; fixed debt balances are financing terms, not hedge notionals | Fixed-rate notes/bonds listed in T2F.2 | Fixed coupon by instrument | Through each stated maturity | Not an interest-rate derivative hedge; fixed coupon is effective only for the instrument’s own coupon exposure | Q2 2026 10-Q, debt table, p. 9 [C6, C7] | Do not count fixed-rate debt as offsetting the issuer’s floating-rate facilities. |
| FX / commodity / fuel / energy hedge | [Insufficient Information] — no such hedge terms identified in supplied sources | [Insufficient Information] — currency/commodity exposure linkage not disclosed | [Insufficient Information] — rates/strikes not disclosed | [Insufficient Information] — maturities not disclosed | Insufficient Information | Q2 2026 10-Q, Note 2, p. 7 [C9] | The no-derivatives disclosure concerns cash-flow hedges and derivatives held; no separate natural or contractual hedge coverage can be quantified. |

#### T2F.4 — Unhedged Floating-Rate Exposure

| Metric | Amount | Formula / Source | Status | Credit Implication | Source Trace |
|---|---:|---|---|---|---|
| Total debt, balance-sheet carrying-value basis | $11,699m | Current portion $114m + long-term debt $11,585m as shown on June 30, 2026 balance sheet | Calculated from reported balance-sheet amounts | Denominator for this analysis uses the defined balance-sheet carrying-value basis, not gross face principal. Debt-note conflict is preserved as CF-1. | Q2 2026 10-Q, consolidated condensed balance sheet, p. 2 [C24, C25] |
| Gross floating-rate debt | Approximately $6,000m | Issuer-reported aggregate long-term variable-rate borrowings; rounded | Reported | Gross exposure is sensitive to the underlying floating reference rates. | Q2 2026 10-Q, Item 3, p. 23 [C8] |
| Hedged floating-rate debt | $0m derivative-covered at the reporting date | No cash-flow hedges or trading derivatives held as of June 30, 2026; fixed-rate notes are not treated as hedges of floating facilities | Calculated from explicit no-derivatives disclosure; limited to the stated reporting date | No disclosed derivative protection offsets the identified variable-rate base. | Q2 2026 10-Q, Note 2, p. 7 [C9] |
| Unhedged floating-rate debt | Approximately $6,000m | Gross floating-rate debt minus derivative-covered floating-rate debt; $6,000m − $0m | Calculated; approximate because source exposure is rounded | A sustained rate rise increases cash interest and reduces FCF/liquidity before any offsetting deleveraging or cash generation. | Q2 2026 10-Q, pp. 7, 23 [C8, C9] |
| Unhedged debt percentage | Approximately 51.3% | $6,000m / $11,699m balance-sheet carrying debt | Calculated from rounded numerator and balance-sheet denominator | Roughly half of balance-sheet debt is exposed on this calculation; source separately reports approximately 51% of consolidated long-term debt. | Q2 2026 10-Q, pp. 2, 23 [C8, C24, C25] |

**Definition conflict CF-1:** the balance sheet’s current portion plus long-term debt equals $11,699m, while the Q2 debt note reports total debt book value of $11,705m. The $6m difference is not reconciled in the supplied text. The prescribed balance-sheet basis is used for the total-debt percentage; the sensitivity numerator is the issuer’s rounded $6.0bn variable-rate amount. [C24, C25, C26]

#### T2F.5 — +100 bps Base-Rate Sensitivity

| Sensitivity | Formula | Source Inputs | Estimated Cash Impact | FCF / Liquidity Implication | Status | Source Trace |
|---|---|---|---:|---|---|---|
| +100 bps annualized increase on disclosed floating-rate debt | Unhedged floating-rate debt × 1.00% | Approximately $6,000m gross variable-rate borrowings; $0m derivative hedge at June 30, 2026 | Approximately $60m per year | If the increase is sustained and balances remain unchanged, cash interest rises and FCF falls by approximately the same amount before tax, working capital or management actions; liquidity available for lease payments, capital expenditure and debt repayment is reduced. | Calculated; approximate; not a forecast | Q2 2026 10-Q, pp. 7, 23 [C8, C9] |
| Historical cross-check, not a current-period input | Issuer’s disclosed +100 bps sensitivity | Approximately $61m annual interest-cost change based on gross amounts outstanding at Dec. 31, 2025 | Approximately $61m | Supports order-of-magnitude consistency only; do not blend with the June 2026 balance. | Reported, prior-period comparator | FY2025 10-K, Item 7A, p. 27 [C11] |

#### T2F.6 — FX Exposure & Mismatch Register

| Exposure Type | Revenue Currency / Region | Cost Currency / Region | Debt / EBITDA / Cash / Covenant Currency | Natural Hedge? | Evidence | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|---|---|
| Translation exposure | North American operations; Caesars Windsor is in Canada, but currency-disaggregated revenues are not supplied | Currency-specific costs not supplied | Financial statements and debt schedule are reported in dollars; exact non-U.S. denomination detail is not supplied | Insufficient Information | Aggregate “foreign currency and other” comprehensive-income line is $(3)m for six months ended June 30, 2026; the filing also identifies Caesars Windsor operations [C15, C27] | Translation effect cannot be isolated from “other,” nor matched against foreign-currency assets/liabilities | No support for a quantified EBITDA, cash or leverage effect; do not infer mismatch from geography | Q2 2026 10-Q, pp. 3, 17 | No currency-level revenue, cost, asset, debt or cash schedule. |
| Transaction exposure | [Insufficient Information] — currency of individual receipts and payments not disclosed | [Insufficient Information] — currency of individual costs not disclosed | Debt and statements predominantly presented in $; currency-level covenant and cash data not supplied | Insufficient Information | Aggregate foreign-currency/other OCI is not a transaction exposure schedule [C15] | A revenue-cost currency mismatch could alter margin and cash conversion, but direction and base are unknown | FX sensitivity and materiality are not calculable; no adverse or positive conclusion | Q2 2026 10-Q, p. 3 [C15] | No transactional FX schedule, sensitivity, repatriation or covenant-currency disclosure supplied. |
| Natural hedge / repatriation / covenant mismatch | [Insufficient Information] — geographic presence is not currency evidence | [Insufficient Information] — no matched operating-cost schedule | [Insufficient Information] — currency matching and trapped cash not disclosed | Insufficient Information | Canada operating context is disclosed, but not the currencies of revenue, costs, debt, EBITDA, cash or covenants [C27] | Unmatched exposures or restricted repatriation could affect available cash, but the required evidence is absent | No quantified credit implication; retain as a gap rather than infer exposure | Q2 2026 10-Q, p. 17 [C27] | Currency data and cash-repatriation restrictions not present. |

#### T2F.7 — Commodity & Inflation Sensitivity

| Input / Commodity / Inflation Driver | Cost Exposure | Pass-Through Mechanism | Evidence | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| Rent inflation | High recurring lease payment commitment; approximately $687m estimated VICI/GLPI payments for remainder of 2026 | CPI-linked escalation in VICI leases; explicit indexation, but no offset/hedge disclosed | CPI escalations apply annually; estimate for remaining 2026 rent [C12, C13] | Higher index readings raise contractual rent and reduce cash remaining for debt service and capex | Directional FCF/liquidity pressure; no CPI scenario quantified | Q2 2026 10-Q, p. 22; FY2025 10-K, p. 23 [C12, C13] | Exact future escalator amount and effect of CPI changes not supplied; variable rent adjustment terms not quantified here. |
| Labour / wage inflation | Material operating cost category; Q2 management cites increased labor costs | No contractual customer surcharge or demonstrated full pass-through disclosed | Q2 2026 Regional margin explanation cites labor costs and gaming taxes [C19] | If wage growth outpaces price/mix or productivity, property margins and cash conversion weaken | Directional margin/FCF pressure; no labor-cost sensitivity supplied | Q2 2026 10-Q, p. 20 [C19] | No wage cost base, labor escalation schedule or quantified efficiency offset. |
| Gaming tax changes | Casino and digital operations; Q2 expense increase linked to higher gaming taxes | Statutory/tax-rate pass-through to customers not disclosed | Filing reports increased gaming tax rates on sports betting wagers and iGaming in certain states and increased costs [C19] | Higher tax expense reduces gaming contribution margin on relevant revenue | Directional FCF pressure; no jurisdiction-level tax sensitivity supplied | Q2 2026 10-Q, p. 19 | No state-by-state exposure and no quantified tax effect. |
| Energy / water | Issuer identifies itself as a large electricity, water and utility consumer | [Insufficient Information] — no utility surcharge or cost pass-through evidence | FY2025 10-K states higher utility prices may adversely affect results [C26] | Higher input prices increase property expense; water stress may impair operations | Potential margin/FCF pressure, not quantified | FY2025 10-K, Item 1A, p. 11 [C26] | No utility spend, consumption sensitivity or procurement/hedge data. |
| Raw materials / freight / procurement | [Insufficient Information] — cost breakdown not supplied | [Insufficient Information] — pricing/surcharge evidence not supplied | No issuer-level exposure amount in supplied evidence | Input inflation without pass-through could compress margins; base and elasticity are unknown | Not calculable; do not infer a stress amount | No direct cost schedule identified in the Q2 10-Q or FY2025 10-K disclosures reviewed | Missing commodity, freight, procurement and pass-through data. |
| Physical climate / water stress | Casinos, hotels and related infrastructure; property-level exposure not quantified | No insurance or customer pass-through sufficient to quantify recovery | Company identifies extreme-weather damage and supply-chain disruption as potential operating impacts [C18] | A severe event may interrupt operations, reduce visitation and require repairs; lease repair obligations can leave cash rent due during restoration | Watch for property-level disruption, insurance gaps and cash-flow strain; no expected loss quantified | FY2025 10-K, pp. 5, 11 [C18, C23] | No site-level hazard, insurance adequacy by property, stress cost or water availability data. |

#### T2F.8 — Macro Sensitivity Summary

| Macro Driver | Evidence | Risk Mechanic | FCF / Liquidity Impact | Refinancing / RV Implication | Monitoring Trigger | Source Trace |
|---|---|---|---|---|---|---|
| Base rates / floating debt | ~$6.0bn variable-rate debt; no derivatives; calculated ~$60m annualized per +100 bps [C8, C9] | Reference-rate increases transmit to interest expense and cash interest | Lower FCF by an approximate $60m per +100 bps while exposure and rates persist | Less cash available for debt reduction and maturities; no market-spread inference made | Term SOFR/base rates, variable balances, cash interest and scheduled maturities | Q2 2026 10-Q, pp. 7, 23 [C8, C9] |
| Rent inflation | VICI CPI escalations; approximately $687m remaining-2026 rent estimate [C12, C13] | CPI resets increase contractual rent | Reduces post-rent liquidity and capacity for discretionary investment | Higher fixed cash burden may reduce refinancing flexibility | CPI and November lease reset; actual payments vs estimates | Q2 2026 10-Q p. 22; FY2025 10-K p. 23 [C12, C13] |
| Labor and gaming taxes | Q2 filing attributes margin pressure/flat margin partly to higher labor costs and taxes [C19] | Wage/tax increases reduce property-level contribution unless offset by productivity or pricing | Directional margin and FCF pressure | Lower cash generation could weaken refinancing flexibility; magnitude unavailable | Contract status, wage outcomes, state tax changes and segment margins | Q2 2026 10-Q, pp. 19–20 [C19] |
| FX mismatch | Foreign-currency/other OCI aggregate reported; no currency matching data [C15] | Unmatched receipts, costs or debt could create translation/transaction volatility | Not calculable | No supported currency-driven refinancing or RV conclusion | Currency-disaggregated revenue, costs, debt and cash disclosures | Q2 2026 10-Q, p. 3 [C15] |
| Energy / water / climate | Utility consumption and physical climate exposure disclosed, but no amounts [C18, C26] | Higher utility costs or severe weather can raise costs or interrupt operations | Directional risk; no stress figure supported | Potential cash-flow/recovery relevance if property damage or insurance shortfall occurs; not sized | Utility spending, water stress, weather events, insurance claims and restoration | FY2025 10-K, pp. 5, 11 [C18, C26] |
| Demand / pricing offset | Consolidated revenue increased in first-half 2026 mainly due to higher casino revenue [C28] | Stronger revenue may absorb some cost pressure, but revenue growth is not evidence of full pass-through | Counterweight to cost pressure, not a quantified offset to interest/rent | Supports monitoring rather than assuming margin deterioration; no forecast extrapolation | Segment revenue and EBITDA margin progression | Q2 2026 10-Q, p. 19 [C28] |

**Macro Risk Level: Moderate.** The principal exposure is identified and unhedged; a +100 bps sensitivity is calculable from the disclosed rounded variable-rate balance. Rent indexation and labor/tax costs add directional pressures, but the supplied documents do not establish FX mismatch or quantify commodity sensitivity. The classification is therefore not Low, while absent current curve, detailed costs and post-Q2 hedging data prevent a more complete stress conclusion.

#### T2F.9 — Gaps Ledger

| Gap | Missing Data | Why It Matters | Impact on Output | Required Follow-Up | Downstream Module Affected |
|---|---|---|---|---|---|
| G-FX-1 | Revenue, costs, EBITDA, debt, cash and covenant data by currency; transaction/translation split; repatriation restrictions | Required to identify mismatch and calculate FX sensitivity without inferring from geography | FX risk remains Insufficient Information; no sensitivity in T2F.6/T2F.8 | Obtain currency-disaggregated filings or treasury exposure schedule | CP-6 |
| G-HEDGE-1 | Post-June 30, 2026 hedge position, if any; complete instrument/notional/rate/strike/maturity/coverage schedule | Determines whether current floating debt remains fully unhedged and whether a hedge cliff exists | Hedge status and sensitivity are a June 30 snapshot | Obtain current treasury hedge register and subsequent-events update | CP-6 |
| G-RATE-1 | Current facility-level balances, exact reference-rate mix, margin step-down status, base-rate split and current forward curve | Refines annualized sensitivity and expected cash interest | $60m estimate uses a rounded $6.0bn base and static +100 bps convention | Obtain current debt/interest schedule and rate assumptions | CP-6 |
| G-DEBT-1 | Reconciliation of balance-sheet debt carrying amount ($11,699m) to debt-note book value ($11,705m) | Affects total-debt denominator and related percentages | CF-1 retained; balance-sheet basis used for calculated percentage | Obtain source reconciliation or detailed debt issuance-cost allocation | CP-6 |
| G-COST-1 | Energy, water, freight, raw-material and procurement expense bases; cost sensitivities and hedge positions | Needed to quantify non-interest inflation/commodity impact | T2F.7 and T2F.8 remain directional or unquantifiable | Obtain utility/commodity spend and purchasing/hedge schedules | CP-6 |
| G-PASS-1 | Demonstrated customer price pass-through, surcharge or cost-recovery timing, and demand elasticity | Determines whether cost inflation is absorbed or recovered and with what lag | No margin or FCF pass-through estimate made | Obtain pricing, menu/room rate and contract pass-through evidence | CP-6 |
| G-LEASE-1 | Future CPI scenarios, lease-by-lease rent reset and complete variable-rent sensitivity | Quantifies rent inflation against significant lease payments | Rent risk remains directional | Obtain current VICI/GLPI rent schedule and sensitivity by CPI/lease component | CP-6 |
| G-LABOR-1 | Status of agreements expiring May 31 and June 30, 2026, negotiations, wage settlements and work-stoppage exposure | Expiration dates in FY2025 filing precede analysis date; no subsequent status supplied | Social/labor risk remains Watch/Directional; no strike or renewal inferred | Obtain post-expiration labor and collective-bargaining update | CP-6 |
| G-ESG-1 | Property-level climate hazard, insurance coverage/limits, adaptation capex and quantified transition costs | Needed to size physical/transition cash-flow, asset-value and recovery risk | Climate factor classified Watch, not quantified | Obtain site-level climate and insurance disclosures and transition capex | CP-6 |
| G-SLL-1 | Sustainability-linked instrument terms, KPI/SPT, test dates, ratchets and verification | Needed to assess spread ratchet and credit significance | No SLL ratchet conclusion supported | Review complete debt documentation and sustainability-linked terms, if any | CP-6 |
| G-CAPITAL-1 | ESG-specific investor-demand, market-access or funding-cost evidence | Needed to link ESG to refinancing access/cost of capital | T2G.6 remains Insufficient Information | Obtain issuer-specific financing or investor-demand evidence | CP-6 |
| G-UPSTREAM-1 | Matching CP-1, CP-1A and CP-2 analytical handoffs | Needed to integrate macro/ESG findings with established credit metrics and business/fundamental conclusions | Source facts are assessed directly; broader credit integration is limited | Attach accepted, matching-run upstream handoffs if available | CP-6 |

#### T2G.1 — ESG Disclosure Source Register

| Source | Reliability (audited/assured vs self-reported) | Greenwashing Flag | Module Status |
|---|---|---|---|
| Caesars FY2025 Form 10-K, environmental stewardship and CSR disclosure | Primary issuer filing; reported goals and emissions data are company-reported; no independent assurance identified in supplied text [C17, C18] | No specific greenwashing evidence identified; assurance and methodology detail are limited | Completed with Limitations |
| Caesars FY2025 Form 10-K, environmental matters and labor disclosures | Primary issuer filing; management disclosure, not independent assurance [C21, C23] | No specific greenwashing evidence identified | Completed with Limitations |
| Caesars Q2 2026 Form 10-Q, segment/labor cost and interim financial disclosure | Primary filed interim report; financial statements unaudited [C19] | Not an ESG claim source; no greenwashing conclusion | Completed with Limitations |

#### T2G.2 — Transition Risk Register

| Exposure | Source/Date | Transmission Mechanic | Affected Driver | Evidence ID |
|---|---|---|---|---|
| Physical climate risk to casino/hotel properties and supply chain | FY2025 Form 10-K, filed Feb. 17, 2026 | Extreme weather may damage or interrupt properties and supply; repair, insurance or reduced visitation could affect cash flow and asset value | FCF, operating continuity, asset value, recovery | [C18] |
| GHG transition goals and possible future regulation | FY2025 Form 10-K, filed Feb. 17, 2026 | Compliance or energy-transition investment could require capex or raise operating cost, but no issuer-specific cost or regulation is quantified | Capex, FCF, refinancing access | [C17, C18] |
| Environmental remediation and compliance | FY2025 Form 10-K, filed Feb. 17, 2026 | Remediation or compliance costs could consume cash; company states identified costs have not had and are not expected to have material adverse financial effect | FCF, liabilities, asset value | [C23] |

#### T2G.3 — Social Event-Risk Register

| Exposure | Source/Date | Transmission Mechanic | Event-Risk vs Ongoing | Evidence ID |
|---|---|---|---|---|
| Labor agreements with expiration dates before analysis date | FY2025 Form 10-K, active employee agreement table as of Dec. 31, 2025 | Higher wage settlements can increase operating expense; a work stoppage can reduce property operations and revenue. Current agreement status is not supplied. | Ongoing cost exposure; possible event risk | [C20] |
| Labor cost contribution to Q2 2026 Regional margin | Q2 2026 Form 10-Q, six months ended June 30, 2026 | Labor costs and gaming taxes contributed to relatively flat Regional margin despite higher revenue, limiting conversion of growth into EBITDA | Ongoing | [C19] |
| 2023 Data Incident litigation and regulatory inquiries | FY2025 Form 10-K, filed Feb. 17, 2026 | Legal, remediation, insurance and reputational consequences could consume cash or affect customer behavior; loss amount is not established here | Event-originated, continuing claims/inquiries | [C21] |

#### T2G.4 — Materiality Table

| Factor | Materiality Class | Transmission Basis | Catalyst (if Watch) | Evidence ID |
|---|---|---|---|---|
| Higher labor costs / contract settlements | Material — Directional | Q2 management attributes Regional margin outcome partly to increased labor costs; cost growth can reduce segment EBITDA/FCF; no amount or elasticity quantified | Not applicable | [C19] |
| Labor agreement status after May/June 2026 dates | Watch | A labor interruption or higher settlement could impair revenue or raise cost; the supplied year-end 2025 table does not establish current status | Confirm bargaining outcomes, renewals or work stoppages | [C20] |
| Physical climate and severe-weather property risk | Watch | Company identifies potential property damage and supply-chain effects, but no site-level probability, loss or insurance gap is quantified | Property-specific weather event, insurance renewal/claim or water-stress disruption | [C18] |
| GHG goals / transition investment | Watch | Goals are disclosed, but no binding issuer-specific carbon cost, required capex or quantified margin effect is provided | New applicable regulation or documented material transition capex | [C17, C18] |
| Environmental remediation matters disclosed | Immaterial to Credit on supplied evidence | Company states identified costs have not had and are not expected to have material adverse financial effect; future matters remain possible | Reclassify if new material remediation, penalty or liability is disclosed | [C23] |
| Data Incident litigation | Material — Directional | Continuing suits and regulatory inquiries may create legal, insurance and reputational cash costs; amount/range not estimable from supplied text | Material settlement, judgment, regulatory action or insurance shortfall | [C21] |

#### T2G.5 — KPI / SPT / Ratchet Table

| Instrument | KPI | SPT + Test Date | Ratchet (direction, bps) | Symmetry | Credit-Meaningful? | Expected Spread Effect | Evidence ID |
|---|---|---|---|---|---|---|---|
| [Insufficient Information] — no sustainability-linked instrument terms identified in the supplied debt disclosures | [Insufficient Information] — KPI not supplied | [Insufficient Information] — target and test date not supplied | [Insufficient Information] — ratchet size/direction not supplied | [Insufficient Information] — no terms supplied | Cannot assess | Cannot assess; no SLL spread or covenant effect assumed | Q2 2026 Form 10-Q debt disclosures and FY2025 Form 10-K debt disclosure reviewed; detailed sustainability-linked terms not present in supplied evidence |

#### T2G.6 — Demand / Access Implications

| Effect | Direction | Quantified vs Directional | Linked Maturity / Funding Need | Evidence ID |
|---|---|---|---|---|
| ESG-specific investor demand, financing access or ESG funding premium | [Insufficient Information] — no issuer-specific financing or investor-demand evidence supplied | [Insufficient Information] — no spread, demand or financing comparison available | Not linked to a maturity from the supplied ESG evidence; debt maturities are described in filings but no ESG financing linkage is established | No direct evidence in supplied FY2025 10-K/Q2 2026 10-Q disclosures |
| Potential incremental climate compliance/transition capital | Directional, conditional | No cost quantified | Would affect cash needs only if applicable regulation or issuer plan creates material investment | [C17, C18] |

#### T2G.7 — ESG Credit Implication Table

| Material Factor | Risk Mechanic | Credit Implication | Confidence | Evidence ID |
|---|---|---|---|---|
| Labor cost / agreement status | Higher wages reduce property margin; unresolved agreement status could result in operating disruption, but no post-expiration labor update is supplied | Directional pressure on segment FCF and monitoring; do not infer a strike or contract outcome | Medium-low | [C19, C20] |
| Physical climate exposure | Severe weather can damage/interupt properties or supply; repair/insurance timing could reduce available cash, but site exposure and insurance adequacy are unquantified | Watch for operating continuity, liquidity and recovery; not a quantified expected loss | Low | [C18] |
| GHG transition goals | Potential future regulation or investment could raise capex/energy cost, but goals themselves do not establish a liability or cash cost | Watch; no present quantified PD, LGD or refinancing effect established | Low | [C17, C18] |
| Environmental remediation | Company says identified costs are not expected to have material adverse financial effect | Immaterial to Credit on current supplied evidence; monitor for new claims or material costs | Medium | [C23] |
| Data Incident litigation | Claims/inquiries could generate legal and remediation outflows; damages and insurance recovery are uncertain | Directional legal/liquidity risk, not quantified; monitor resolutions and insurance recovery | Low | [C21] |

#### T2G.8 — ESG Gaps Ledger

| Gap | Missing Item | Why It Matters | Impact on Output | Required Follow-Up |
|---|---|---|---|---|
| G-ESG-ASSURANCE | Assurance status and underlying methodology for emissions/CSR data | Affects reliability and comparability of disclosed goals and progress | Company-reported targets remain self-reported; no assurance conclusion | Obtain CSR report methodology, boundary and assurance statement |
| G-CLIMATE-SITE | Property-level hazard, adaptation, insurance and restoration cost information | Needed to assess operational interruption, liquidity and asset/recovery exposure | Climate exposure remains Watch, not quantified | Obtain site-level climate-risk and insurance analysis |
| G-TRANSITION-COST | Applicable issuer-specific regulation, carbon price, required capex and transition plan costs | Needed to quantify margin/capex and refinancing transmission | Transition exposure remains conditional Watch | Obtain regulatory applicability assessment and capital plan |
| G-LABOR-STATUS | Post-expiration status of agreements listed with May/June 2026 dates | Determines whether labor event risk is current or resolved and whether costs changed | Labor event risk remains Watch; no outcome inferred | Obtain current collective-bargaining and labor-status disclosure |
| G-SLL-TERMS | Complete SLL/SLB term inventory, KPI/SPT, ratchet, testing and verification terms | Needed to assess potential spread or covenant effect | T2G.5 cannot assess credit meaningfulness | Review full debt and financing-document inventory; provide any sustainability-linked terms |
| G-ESG-CAPITAL | Issuer-specific investor demand, financing access or cost-of-capital evidence | Needed to tie ESG claims to refinancing access or spread | T2G.6 remains Insufficient Information | Obtain financing-market evidence or issuer disclosure linking ESG factors to funding |
| G-SOCIAL-UPDATE | Updated Data Incident litigation/regulatory status and insurance recovery | Determines potential cash loss and whether stated risks have changed | Litigation implication remains directional | Obtain subsequent company/regulator disclosures and claim/insurance updates |
| G-UPSTREAM-CREDIT | CP-1, CP-1A and CP-2 handoffs | Required to integrate this factor review with current financial, business and fundamental-credit conclusions | CP-2F synthesis is evidence-specific and not a full credit conclusion | Supply matching accepted upstream handoffs if available |

## Evidence Trace

| Claim / register evidence | Citation | Document | Page |
|---|---|---|---:|
| Variable facility balances and terms | [C1] | Caesars Q2 2026 Form 10-Q | 9 |
| Term Loan A balance and floating classification | [C2] | Caesars Q2 2026 Form 10-Q | 9 |
| Caesars Virginia term loan balance and floating classification | [C3] | Caesars Q2 2026 Form 10-Q | 9 |
| Term Loan B balance and floating classification | [C4] | Caesars Q2 2026 Form 10-Q | 9 |
| Term Loan B-1 balance and floating classification | [C5] | Caesars Q2 2026 Form 10-Q | 9 |
| Fixed-rate secured note coupon | [C6] | Caesars Q2 2026 Form 10-Q | 9 |
| Fixed-rate unsecured note coupon | [C7] | Caesars Q2 2026 Form 10-Q | 9 |
| Aggregate June 2026 variable-rate borrowings | [C8] | Caesars Q2 2026 Form 10-Q | 23 |
| Derivative / hedge holdings at reporting date | [C9] | Caesars Q2 2026 Form 10-Q | 7 |
| Reported floating share and weighted-average debt rates | [C10] | Caesars Q2 2026 Form 10-Q | 23 |
| Prior-period +100 bps interest sensitivity | [C11] | Caesars FY2025 Form 10-K | 27 |
| Remaining-2026 VICI/GLPI lease estimate | [C12] | Caesars Q2 2026 Form 10-Q | 22 |
| CPI escalation mechanism | [C13] | Caesars FY2025 Form 10-K | 23 |
| Lower year-over-year variable-rate interest expense counterpoint | [C14] | Caesars Q2 2026 Form 10-Q | 19 |
| Foreign-currency and other comprehensive-income line | [C15] | Caesars Q2 2026 Form 10-Q | 3 |
| Emissions reduction target and long-term goal | [C17] | Caesars FY2025 Form 10-K | 7 |
| Historical Scope 1 and 2 emissions reduction | [C18] | Caesars FY2025 Form 10-K | 7 |
| Physical climate risk to facilities and supply chain | [C19] | Caesars FY2025 Form 10-K | 11 |
| Q2 labor cost and gaming-tax margin attribution | [C20] | Caesars Q2 2026 Form 10-Q | 20 |
| FY2025 labor agreement expiration-date example | [C21] | Caesars FY2025 Form 10-K | 6 |
| Environmental cost counterweight | [C23] | Caesars FY2025 Form 10-K | 5 |
| Balance-sheet current debt | [C24] | Caesars Q2 2026 Form 10-Q | 2 |
| Balance-sheet long-term debt | [C25] | Caesars Q2 2026 Form 10-Q | 2 |
| Energy and water cost exposure | [C26] | Caesars FY2025 Form 10-K | 11 |
| Caesars Windsor / Canada operating context | [C27] | Caesars Q2 2026 Form 10-Q | 17 |
| Revenue-growth counterweight | [C28] | Caesars Q2 2026 Form 10-Q | 19 |
| Debt-note book-value comparator for CF-1 | [C26] | Caesars Q2 2026 Form 10-Q | 9 |

## Source Registry

| Source ID | Source | Period / quality | Evidence use | Limitation |
|---|---|---|---|---|
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars Entertainment, Inc. Form 10-K | FY2025; filed annual report, audited financial statements | Historical rate sensitivity, CPI rent, environmental/climate, emissions, labor and risk disclosures | Period ends Dec. 31, 2025; not a current post-Q2 schedule |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Entertainment, Inc. Form 10-Q | Q2 2026; unaudited interim statements; filed July 28, 2026 | Debt balances, floating exposure, derivatives, Q2 interest, rent, FX line and segment/labor context | Ends June 30, 2026; currency and commodity detail unavailable |
| c67320d0-3458-4ee9-bc3c-e1a8bc6f3c05 | MGM Resorts Q2 2026 results release | Q2 2026; issuer-reported peer | Catalogued peer context only | No Caesars exposure or calculation input used |
| 156bf3bf-764e-4347-b2e7-bf6f34f22220 | PENN Entertainment Q2 2026 results release | Q2 2026; issuer-reported peer | Catalogued peer context only | No Caesars exposure or calculation input used |

The accepted CP-0 handoff is an upstream artifact, not a primary source citation. Its source-readiness verdict is READY_WITH_LIMITATIONS for the matching issuer/run/period; the exact inherited lineage appears in front matter. No CP-1, CP-1A or CP-2 analytical artifact was delivered. No external research or market data was used.

## Gaps & Conflicts

- **CF-1 — debt carrying-value basis:** Q2 balance-sheet current debt of $114m plus long-term debt of $11,585m yields $11,699m; the debt note separately reports total debt book value of $11,705m. The $6m difference is unresolved in the delivered extract. T2F.4 uses the balance-sheet basis as required and does not silently reconcile the note figure. [C24, C25, C26]
- **Period gap:** the $6.0bn floating-rate exposure and no-derivatives disclosure are as of June 30, 2026; current balances and hedges after that date are unavailable. The FY2025 $61m sensitivity is retained only as a dated cross-check, not blended with Q2. [C8, C9, C11]
- **Currency gap:** foreign-currency and other OCI is an aggregate figure, not a currency exposure schedule. Currency mismatch, natural hedges, cash repatriation and covenant mismatch remain unassessed. [C15]
- **Pass-through and input-cost gap:** CPI-linked rent is documented, but energy, water, freight, procurement and wage cost bases and effective pass-through are not quantified. [C12, C13, C19, C26]
- **ESG disclosure gap:** emissions goals and physical-risk statements are company disclosures, with no assurance information identified in the supplied text; property-level climate costs, SLL terms, financing-demand effects and updated labor agreement status are absent. [C17, C18, C20, C21]
- **Integration gap:** accepted CP-1, CP-1A and CP-2 outputs were not supplied. This limits full credit synthesis but does not invalidate the source-supported exposure inventory and calculations in this handoff.

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity and lineage | PASS — self-check | CZR, CP-2E, Q2 2026 and accepted matching CP-0 lineage retained. |
| Required analytical registers | PASS — self-check | T2F.1–T2F.9 and T2G.1–T2G.8 included with required columns and populated rows. |
| Rate classification | PASS — self-check | Disclosed floating and fixed instruments are separated; $6.0bn issuer-reported aggregate is not silently reconstructed from rounded components. |
| Hedge discipline | PASS — self-check | No derivative hedge is assumed; date limitation and non-derivative fixed coupon distinction are stated. |
| Rate sensitivity | PASS — self-check | Approximate $60m equals rounded $6.0bn × 1.00%; prior-period $61m is separately labeled and not blended. |
| FX / commodity calculation controls | PASS — limitation applied | No sensitivity fabricated where currency/cost bases or driver amounts are not supplied. |
| ESG materiality and SLL | PASS — limitation applied | Factors are classified before implications; no SLL, assurance or capital-access effect is invented. |
| Source trace and conflicts | PASS — self-check | Material claims carry evidence markers; debt basis conflict CF-1 is explicit. |
| Committee status | Requires More Work | Limited current exposure detail and missing upstream analytical handoffs preclude committee-ready integration. |
| Host validation | PENDING | Host validation follows this response; no script output or host-validation result is claimed. |

Confidence calculation is described in Audit Summary. QA status is Restricted because material exposure and integration gaps remain; the confidence score is capped at 59. Recommended downstream consumer: CP-6, with CP-5 and CP-5A QA review.