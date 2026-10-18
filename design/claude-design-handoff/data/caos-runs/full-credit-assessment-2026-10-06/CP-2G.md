---
module_id: "CP-2G"
module_name: "ForwardCreditModel"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2G-739392094a3687bb"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-12-CP-2G"
credit_os_invocation_sha256: "99caf95a7facbe5e654357a2b66fda4f9fed838ac69eee8d3121f06766e341b2"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
  - module_id: "CP-1"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "2b6e7d314204037454a77127b5af58ed64b8eb4e0cc23081834e1de915c80dbc"
  - module_id: "CP-1D"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "14f82d3ec8922f3c8a7e25f5400cedd84f4d2af4e4cc9184c73b2a85b4392cf2"
  - module_id: "CP-2A"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "3bc62cc745eea3248e6a76af0f4c1a98c3c566c4d65ece793c77ed7f324ba689"
  - module_id: "CP-2D"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "01a3ee1272c2966c991c7a9c33b7b90debe3b32c302c08cd2a5bd669682a64b0"
confidence_score: 50
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - "SOURCE_LIMITED_NOT_COMMITTEE_READY"
  - "NO_POST_Q2_2026_FINANCIALS"
  - "NUMERIC_FORECAST_ASSUMPTIONS_NOT_SUPPORTED"
  - "CP_MODEL_ACTIVE_DRIVER_INPUTS_UNAVAILABLE"
validation_warnings:
  - "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED"
  - "CP1_HISTORICAL_QUARTER_COVERAGE_INCOMPLETE"
  - "TWELVE_MONTH_CASH_FLOW_AND_COVENANT_HEADROOM_UNRESOLVED"
downstream_consumers: [CP-2, CP-2B, CP-2D, CP-2E, CP-2H, CP-3, CP-3C, CP-3D, CP-4C, CP-MODEL, CP-5]
---

## Audit Summary

**Canonical filename:** `CZR_CP-2G_20261002.md`. **Status:** Complete with Gaps; confidence **50/100, Low**; QA **Restricted**; committee status **Requires More Work**. The accepted CP-0, CP-1, CP-1D, CP-2A and CP-2D artifacts match this issuer, run and Q2 2026 period, but retain material source limitations. The Q2 LTM base is calculable for selected historical measures. A numerical FY2026–FY2028 forecast is not supportable: forward operating, working-capital, tax and financing assumptions are absent, and CP-1 flags incomplete quarterly history. Unsupported forecast values remain null. The CP-MODEL interface is included but unavailable for consumption because active forecast drivers cannot be sourced. Host validation follows this response; no host result is claimed.

## Analysis

### Forward credit view

At June 30, 2026, LTM revenue was calculated at $11,648 million and issuer Adjusted EBITDA at $3,592 million; balance-sheet carrying debt was $11,699 million and cash was $965 million. [C1, C2, C3, C4, C7, C14, C15] These are historical anchors, not forecasts. Reported Las Vegas weakness and lower table-games hold support a qualitative downside pathway: weaker operating cash would meet debt service, rent and capex that do not necessarily adjust in step. [C9, C10, C11, C12, C21, C22] H1 revenue growth, positive operating cash flow and reported covenant compliance are the strongest contrary evidence. [C3, C5, C17] That counterevidence would gain weight if sustained alongside lower debt and disclosed headroom. Without post-June financials or forward cash-flow assumptions, projected leverage, liquidity and refinancing capacity remain unquantified.

The trajectory summary distinguishes the historical base from unsupported projections; dashes are unavailable values, not zeroes.

| Case | FY2026 | FY2027 | FY2028 | First material inflection | Creditor consequence |
|---|---|---|---|---|---|
| Base | H2 operating forecast — | Revenue, EBITDA and FCF — | Revenue, EBITDA and FCF — | Not measurable from supplied forecast inputs | No projected deleveraging claim is supportable. |
| Downside | Qualitative visitation/hold pressure; numeric shock — | Cash flow and leverage — | Refinancing capacity — | Cash conversion before fixed claims; timing unquantified | Monitor liquidity, revolver use, rent and debt service; no covenant breach inferred. |
| Upside | No numerical upside case supported | — | — | No sourced upside catalyst quantified | Not probability-weighted or included as a forecast. |

#### Historical-to-base bridge and definitions

The Q2 2026 LTM base is calculated as FY2025 plus H1 2026 less H1 2025. Revenue is $11,648 million; issuer Adjusted EBITDA $3,592 million; CFO $1,297 million; PP&E purchases $687 million; and CFO less PP&E purchases is a $610 million proxy. [C1, C2, C3, C4, C5, C6, C23, C26] The proxy is not issuer-reported FCF and excludes other investing activity, cash interest, taxes, rent, distributions and financing uses. Carrying debt is based on current debt plus long-term debt; financing obligations are shown separately. [C14, C15, C25] P&L interest and cash interest paid for rent are distinct measures. [C27, C28, C24]

CP-1D identifies recurring impairment and stock-compensation exclusions and leaves the transaction-and-other category unresolved. Quality-adjusted EBITDA is therefore not established and is not substituted for reported EBITDA. [C2, C4, C20] This limits confidence in treating Adjusted EBITDA as cash available for debt reduction.

#### Scenario logic and first inflection

The base case is the most evidence-supported historical anchor, not an assumed growth or margin trajectory. FY2026–FY2028 revenue, margin, CFO, capex, FCF, closing debt and cash remain unavailable because the sources supply no complete forecast. The downside case changes named drivers qualitatively—continued Las Vegas visitation or hold pressure and cost rigidity—without applying an invented percentage haircut. An upside case is shown directionally but not assigned values or probabilities.

The strongest counterargument is H1 revenue growth, positive H1 CFO, the reported June liquidity balance and covenant compliance. [C3, C5, C8, C17] It would win if subsequent periods showed sustained cash generation after capex and rent, stronger Las Vegas indicators, declining carrying debt and disclosed covenant headroom. The downside’s first observable trigger is further Las Vegas revenue or table-games hold deterioration. Lower contribution can reduce cash available after fixed claims, increase revolver reliance and weaken refinancing flexibility. [C11, C21, C22] Timing, numerical breakpoint and covenant consequences cannot be calculated from the supplied materials.

#### Liquidity, refinancing and contrary evidence

June 30 liquidity is a dated snapshot: reported total cash and capacity was $2,928 million. [C8] The company estimated $425 million of debt service, $687 million of VICI/GLPI lease payments and $310–$390 million of capital expenditures for the remainder of 2026. [C9, C10, C11, C12] These figures do not provide a full 12-month bridge through June 30, 2027; H1 2027 uses and forward CFO, working capital and cash taxes are missing. CP-2D likewise leaves ending liquidity and runway unquantified.

Management’s FY2025 statement that then-current liquidity was expected to cover operations, capital requirements and debt service for the next twelve months and beyond is supportive contrary evidence. [C19] It does not replace a current forecast or resolve the missing H1 2027 bridge. The observable monitoring triggers are cash decline, revolver draws or reduced availability, weaker CFO, lower segment results and updates to debt, lease or transaction status. No probability, rating, legal conclusion or security recommendation is made.

### Analytical appendix — complete canonical registers

#### T2H.1 — Source and identity gate

| source_id | upstream module/run/period | status | locator | limitation |
|---|---|---|---|---|
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | CP-1; COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7; Q2 2026 | Accepted; Restricted | Q2 2026 Form 10-Q, balance sheet, cash flow, debt, liquidity; pp. 2, 4, 9, 22 [C5, C7, C8, C14, C15] | Financial reporting ends June 30, 2026; no forward operating or complete 12-month cash-flow schedule. |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | CP-1; COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7; Q2 2026 | Accepted; Restricted | FY2025 Form 10-K, revenue, EBITDA and cash flow; pp. 19, 23, 31 [C1, C2, C23] | Historical annual information; not an October 2026 update. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | CP-1D; COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7; Q2 2026 | Accepted; Restricted | Q2 2026 Adjusted EBITDA reconciliation; p. 16 | Recurring add-backs and unresolved transaction-cost composition limit quality-adjusted earnings. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | CP-2A; COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7; Q2 2026 | Accepted; Restricted | Q2 Form 10-Q operating and transaction evidence; pp. 5, 15, 20 [C21, C22] | Supports qualitative downside drivers only, not numeric forecast assumptions. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | CP-2D; COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7; Q2 2026 | Accepted; Restricted | Q2 Form 10-Q liquidity, debt service and capex; pp. 9, 22 [C8, C9, C10, C11, C12] | Partial remainder-2026 uses only; full 12-month bridge unavailable. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Primary evidence; Q2 2026 Form 10-Q | Primary-Verified; unaudited interim | Cash, debt, flow and segment tables; pp. 2, 4, 9, 18-23 [C5, C7, C14, C15, C21, C22] | No post-June values inferred; restricted cash and financing obligations remain separately identified. |

#### T2H.2 — Historical-to-base bridge

| metric | historical actual | LTM/base | adjustment | basis | evidence_id |
|---|---:|---:|---|---|---|
| Revenue, USD millions | FY2025 11,486 | 11,648 | FY2025 + H1 2026 − H1 2025 | Calculated consolidated flow; no forecast adjustment. | [C1, C3] |
| Issuer Adjusted EBITDA, USD millions | FY2025 3,624 | 3,592 | FY2025 + H1 2026 − H1 2025 | Issuer-defined non-GAAP metric; not cash flow. | [C2, C4] |
| CFO, USD millions | FY2025 1,302 | 1,297 | FY2025 + H1 2026 − H1 2025 | Reported consolidated operating cash flow. | [C5, C23] |
| PP&E purchases, USD millions | FY2025 805 | 687 | FY2025 + H1 2026 − H1 2025; displayed as positive spend | Reported capital spending; excludes other investing items. | [C6, C26] |
| FCF proxy, USD millions | FY2025 497 | 610 | CFO less PP&E purchases | Analyst-defined proxy only; excludes other investing, interest, taxes, rent, distributions and financing. | [C5, C6, C23, C26] |
| Cash and equivalents, USD millions | FY2025 year-end 887 | 965 at June 30, 2026 | Period-end balance, not an LTM flow | Restricted cash excluded; June 30 snapshot. | [C7] |
| Carrying debt, USD millions | FY2025 year-end 11,784 | 11,699 at June 30, 2026 | Current portion plus balance-sheet long-term debt | Carrying-value basis; financing obligations are separate. | [C14, C15, C25] |
| Accessible liquidity, USD millions | FY2025 year-end 2,833 | 2,928 at June 30, 2026 | Dated cash plus disclosed capacity | Includes borrowing capacity; future access/headroom not established. | [C8] |
| Net P&L interest, USD millions | FY2025 2,304 | 2,293 | FY2025 + H1 2026 − H1 2025 | P&L basis; rent-related interest is separate. | [C27, C28] |
| Quality-adjusted EBITDA, USD millions | Not established | Not established | Transaction-and-other components unresolved; recurring impairment/SBC not treated as clean one-offs | No plug or arbitrary haircut. | [C2, C4, C20] |

#### T2H.3 — Assumption register

| assumption_id | driver | case | period | value/range | unit | class | source | rationale |
|---|---|---|---|---|---|---|---|---|
| A-BASE-ANCHOR | Revenue and earnings starting point | base | Q2 2026 LTM | Revenue 11,648; Adjusted EBITDA 3,592; historical, not forecast | USD millions | calculated | FY2025 and Q2 filings [C1, C2, C3, C4] | Common historical anchor; no forward growth rate disclosed. |
| A-BASE-OPERATING | Revenue, volume, price/mix and margin | base | FY2026-FY2028 | —; no sourced numerical forecast | USD millions / % | analyst_judgment | Q2 revenue and Adjusted EBITDA [C3, C4] | No numerical operating forecast is supplied; no flat-growth assumption is inserted. |
| A-BASE-WC | Working capital, deposits and cash taxes | base | FY2026-FY2028 | —; forward values unavailable | USD millions | source_fact | H1 cash flow and customer-liability disclosures [C5, C16] | Historical values are not annualized or substituted for future flows. |
| A-BASE-CAPEX | Capex and discretionary investment | base | FY2026 | Remaining-year total 310-390; later periods — | USD millions | management_guidance | Q2 capex estimate [C12] | Partial remainder-2026 estimate only; not extrapolated. |
| A-BASE-INTEREST | Interest and debt service | base | FY2026-FY2028 | Remainder-2026 estimates: principal 55, interest 370; FY2027 full-year 114/750; FY2028 767/680 | USD millions | source_fact | Q2 debt-service table [C9, C10] | FY2027 figures are full-year values; no H1 allocation or closing-debt roll-forward inferred. |
| A-BASE-LEASE | Lease payments | base | FY2026 | Remainder-year 687; FY2027-FY2028 — | USD millions | management_guidance | Q2 MD&A [C11] | No later-period estimate supplied. |
| A-BASE-LIQUIDITY | Opening cash and facility availability | base | FY2026 H2 opening | 2,928 at June 30, 2026 | USD millions | source_fact | Q2 liquidity table [C7, C8] | Dated opening snapshot only; not a forward closing-liquidity assumption. |
| A-DOWN-OPERATING | Visitation, gaming volume and hold | downside | FY2026-FY2028 | Qualitative downside; numeric shock — | qualitative | analyst_judgment | Las Vegas revenue and hold [C21, C22] | Observed weakness supports a named downside driver, but not a percentage haircut. |
| A-DOWN-COST | Labor, taxes and other costs | downside | FY2026-FY2028 | Qualitative cost rigidity; numeric shock — | qualitative | analyst_judgment | Filing describes higher gaming tax rates [C21] | Costs may not flex with receipts; amount and timing not supplied. |
| A-DOWN-CASH | Cash conversion and working capital | downside | FY2026-FY2028 | Directional pressure; numeric reduction — | qualitative | analyst_judgment | H1 CFO and cash-flow movements [C5] | Downside transmission is described without inventing a cash-flow amount. |
| A-DOWN-FINANCING | Issuance, repayment, refinancing and revolver access | downside | FY2026-FY2028 | —; no unsupported financing action assumed | USD millions | analyst_judgment | Carrying debt and reported liquidity [C7, C8, C14, C15] | Current debt, future draw access and transaction funding are not fully forecast. |
| A-UP-OPERATING | Improved operating performance | upside | FY2026-FY2028 | Directional only; numeric uplift — | qualitative | analyst_judgment | H1 revenue growth [C3] | Counterargument sensitivity only; not a sourced forecast or probability. |
| A-UP-CASH | Improved cash conversion and debt reduction | upside | FY2026-FY2028 | Directional only; numeric amount — | qualitative | analyst_judgment | H1 CFO and cash balance [C5, C7] | No debt-repayment target or cash-flow forecast supplied. |
| A-MIN-CASH | Minimum cash requirement | base | FY2026-FY2028 | —; not disclosed | USD millions | source_fact | Supplied sources reviewed; no issuer minimum-cash amount established. | No minimum-cash threshold is invented. |
| A-QUALITY | Quality-adjusted EBITDA | base | FY2026-FY2028 | —; unresolved | USD millions | source_fact | CP-1D bridge and recurring exclusions [C2, C4, C20] | Transaction-and-other components and the H1 tax dash/zero conflict prevent a quality-adjusted denominator. |

#### T2H.4 — Forward operating model

| period | case | revenue | EBITDA | margin | CFO | capex | FCF | evidence/assumption IDs |
|---|---|---:|---:|---:|---:|---:|---:|---|
| FY2026 | base | — | — | — | — | — | — | A-BASE-OPERATING; A-BASE-WC; A-BASE-CAPEX |
| FY2027 | base | — | — | — | — | — | — | A-BASE-OPERATING; A-BASE-WC; A-BASE-CAPEX |
| FY2028 | base | — | — | — | — | — | — | A-BASE-OPERATING; A-BASE-WC; A-BASE-CAPEX |
| FY2026 | upside | — | — | — | — | — | — | A-UP-OPERATING; A-UP-CASH |
| FY2027 | upside | — | — | — | — | — | — | A-UP-OPERATING; A-UP-CASH |
| FY2028 | upside | — | — | — | — | — | — | A-UP-OPERATING; A-UP-CASH |
| FY2026 | downside | — | — | — | — | — | — | A-DOWN-OPERATING; A-DOWN-COST; A-DOWN-CASH |
| FY2027 | downside | — | — | — | — | — | — | A-DOWN-OPERATING; A-DOWN-COST; A-DOWN-CASH |
| FY2028 | downside | — | — | — | — | — | — | A-DOWN-OPERATING; A-DOWN-COST; A-DOWN-CASH |

Formula lineage: future revenue, EBITDA and margin need forward volume/price/mix and cost assumptions not supplied. CFO, capex and FCF need forward working-capital, tax, interest and spending inputs. FCF is not calculated for forecast periods; null cells are not zero.

#### T2H.5 — Debt and liquidity roll-forward

| period | case | opening debt/cash | issuance | repayment | interest | closing debt/cash | accessible liquidity |
|---|---|---|---:|---:|---:|---|---|
| FY2026 | base | June 30 opening snapshot: carrying debt 11,699; cash 965 [C7, C14, C15, C25] | — | 55 remainder-year estimate [C9] | 370 remainder-year estimate [C10] | —; full-period cash/debt movements incomplete | 2,928 at June 30 opening; closing — [C8] |
| FY2027 | base | —; prior closing balance unavailable | — | 114 full-year schedule; H1 timing — [C9] | 750 full-year schedule; H1 timing — [C10] | — | — |
| FY2028 | base | — | — | 767 scheduled estimate [C9] | 680 scheduled estimate [C10] | — | — |
| FY2026 | upside | June 30 opening snapshot: carrying debt 11,699; cash 965 [C7, C14, C15, C25] | — | 55 remainder-year estimate [C9] | 370 remainder-year estimate [C10] | — | 2,928 at June 30 opening; closing — [C8] |
| FY2027 | upside | — | — | 114 full-year schedule; H1 timing — [C9] | 750 full-year schedule; H1 timing — [C10] | — | — |
| FY2028 | upside | — | — | 767 scheduled estimate [C9] | 680 scheduled estimate [C10] | — | — |
| FY2026 | downside | June 30 opening snapshot: carrying debt 11,699; cash 965 [C7, C14, C15, C25] | — | 55 remainder-year estimate [C9] | 370 remainder-year estimate [C10] | — | 2,928 at June 30 opening; closing — [C8] |
| FY2027 | downside | — | — | 114 full-year schedule; H1 timing — [C9] | 750 full-year schedule; H1 timing — [C10] | — | — |
| FY2028 | downside | — | — | 767 scheduled estimate [C9] | 680 scheduled estimate [C10] | — | — |

The sourced principal and interest rows are schedule estimates, not complete closing-balance roll-forwards. A roll-forward needs operating cash, capex, taxes, rent, other investing/financing movements and actual payment timing; those residuals are left unresolved, not plugged.

#### T2H.6 — Credit metrics

| period | case | gross/net leverage | coverage | FCF/debt | liquidity runway | definition IDs |
|---|---|---|---|---|---|---|
| Q2 2026 LTM base | base | Gross 3.26x; net 2.99x | Adjusted EBITDA / LTM net P&L interest 1.57x | 5.2% CFO-less-PP&E proxy / carrying debt | —; no supported forward runway | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2026 | base | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2027 | base | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2028 | base | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2026 | upside | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2027 | upside | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2028 | upside | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2026 | downside | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2027 | downside | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |
| FY2028 | downside | — | — | — | — | D-DEBT; D-NET; D-INT-P&L; D-FCF-PROXY |

Historical base formulas: carrying debt $11,699m / LTM Adjusted EBITDA $3,592m = 3.26x; net debt ($11,699m − $965m cash) / $3,592m = 2.99x; $3,592m / LTM net P&L interest $2,293m = 1.57x; LTM proxy FCF $610m / carrying debt $11,699m = 5.2%. [C2, C4, C7, C14, C15, C25, C27, C28] The FCF/debt measure uses a limited proxy, not issuer-reported FCF. Restricted cash is excluded from net debt. No forecast-period ratios are calculated without forecast inputs.

#### T2H.7 — Scenario and breakpoint matrix

| driver shock | first break | period | liquidity/covenant/refinancing consequence | recovery action |
|---|---|---|---|---|
| Base: no numerical operating change assumed; retain actual LTM as anchor | Not measurable from supplied forward assumptions | FY2026-FY2028; exact timing unavailable | Ending liquidity, leverage, coverage and headroom cannot be reconciled; scheduled debt service and rent remain material uses. | Obtain complete forecast, cash/debt schedule and covenant calculations; do not treat missing data as stability. |
| Downside: continued Las Vegas visitation/table-games hold pressure plus cost rigidity; qualitative only | Lower property contribution and cash conversion before fixed interest, rent and capex | Potentially FY2026; precise first period unavailable | Could increase revolver reliance, slow deleveraging and reduce refinancing flexibility; no breach or draw amount inferred. | Monitor segment revenue/hold, CFO, cash, revolver usage and fixed uses; refresh when reporting arrives. |
| Upside: operating and cash-conversion improvement; qualitative only | No quantified upside breakpoint | FY2026-FY2028; not dated | Improved cash generation could support debt reduction and refinancing flexibility, but scale cannot be measured. | Require sustained post-capex/rent cash generation, lower debt and disclosed headroom before crediting upside. |

#### T2H.8 — Deleveraging and monitoring handoff

| case | trajectory | target/date | dependency | trigger | downstream module |
|---|---|---|---|---|---|
| Base | Historical LTM anchor only; forward debt direction unquantified. | No supported target/date. | Full operating, cash, debt and lease forecasts. | Subsequent filings show cash generation after capex/rent and lower carrying debt. | CP-2H |
| Downside | Directional risk of slower deleveraging or releveraging if operating cash weakens while fixed claims persist. | No supported target/date. | Las Vegas results, cash conversion and actual revolver accessibility. | Cash decline, rising revolver draws, weaker segment results or reduced availability. | CP-3C |
| Upside | Directional possibility of improved deleveraging if operating performance and cash conversion strengthen. | No supported target/date. | Later results, capex execution and debt schedule. | Repeated positive post-capex cash generation, lower debt and disclosed covenant headroom. | CP-3 |
| All cases | Forecast driver interface is not consumable on delivered data. | FY2026-FY2028 interface periods. | Active division and flow-driver assumptions with traceable numerical values. | New accepted source pack supplies complete periods and supported assumptions. | CP-MODEL |

#### T2H.9 — Gaps and conflicts

| item | conflict/gap | affected case/period | model impact | required evidence |
|---|---|---|---|---|
| Forward operating forecast | No sourced FY2026-FY2028 revenue, volume, price/mix or margin assumptions. | Base/upside/downside; FY2026-FY2028 | Operating forecasts remain null; no silent flat-growth assumption. | Period-specific forecast or explicitly approved assumptions with source and rationale. |
| Cash flow and working capital | No forward CFO, working-capital or cash-tax schedule. | All cases; FY2026-FY2028 | FCF and ending cash cannot be calculated. | Detailed forecast and working-capital/tax schedule. |
| Capex horizon | Remaining-2026 estimate is available; later periods and complete maintenance/growth flexibility are not. | All cases; FY2026-FY2028 | No full-period capex or FCF forecast. | Dated capex schedule by project, maintenance need and deferrability. |
| Debt/cash roll-forward | Future issuance, optional repayment, other financing flows and full cash movements are not established. | All cases; FY2026-FY2028 | Closing debt, cash and leverage cannot be reconciled. | Current debt-by-tranche, cash schedule and full financing/investing forecast. |
| Debt service and rent | FY2027 debt-service figures are annual; H1 timing and H1 2027 lease payments are unavailable. | 12 months to June 30, 2027 | Full-horizon fixed cash uses cannot be totaled. | Dated debt-service and lease schedules through June 30, 2027. |
| Revolver and covenant access | Covenant compliance reported, but current headroom and full current credit agreement are not supplied. | All cases; current and forecast | Accessible liquidity cannot be treated as unconditional; covenant breakpoints unavailable. | Current agreement, compliance certificate and borrowing conditions. |
| Earnings quality | CP-1D identifies recurring impairment/SBC and unresolved transaction-and-other costs; H1 tax bridge has source dash/zero conflict. | LTM denominator and all forecast cases | Quality-adjusted EBITDA and related leverage are not established. | Transaction-cost component bridge and reconciliation of the H1 tax display. |
| Post-June actuals | No financial report after June 30, 2026; Alberta launch is a subsequent event. | FY2026 H2 and analysis date | Current operating and debt/cash position cannot be verified. | Subsequent filings and current operating/treasury update. |
| CP-MODEL active drivers | CP-1 allocation identifies active divisions; delivered sources contain no supported forward numerical growth inputs or complete driver assumptions. | BASE/DOWNSIDE; FY2026-FY2028 | Required interface rows are present but unavailable; no case period is consumable. | Complete accepted period history and sourced or expressly approved driver inputs. |

#### cp2g.cp_model_forecast_drivers — CP-MODEL interface

<!-- table-id: cp2g.cp_model_forecast_drivers -->

| driver_id | slot_id | case | period_id | fiscal_year | value | unit | assumption_id | status | source_id | source_locator | as_of |
|---|---|---|---|---:|---:|---|---|---|---|---|---|
| division_growth | DIVISION_1 | BASE | FY2026 | 2026 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Las Vegas slot; no forward numerical growth input supplied; historical segment evidence only [C21] | 2026-10-02 |
| division_growth | DIVISION_2 | BASE | FY2026 | 2026 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Regional/Managed slot; no forward numerical growth input supplied. | 2026-10-02 |
| division_growth | DIVISION_3 | BASE | FY2026 | 2026 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Digital slot; no forward numerical growth input supplied. | 2026-10-02 |
| acquisitions_disposals |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2026 forward transaction cash-flow input supplied; null is not zero. | 2026-10-02 |
| net_equity_issue_repay |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No forward equity issue/repurchase amount supplied. | 2026-10-02 |
| dividends_paid |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No forecast dividend amount supplied. | 2026-10-02 |
| other_investing_financing |  | BASE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No forward other investing/financing amount supplied. | 2026-10-02 |
| division_growth | DIVISION_1 | BASE | FY2027 | 2027 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Las Vegas slot; no FY2027 numerical growth input supplied. | 2026-10-02 |
| division_growth | DIVISION_2 | BASE | FY2027 | 2027 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Regional/Managed slot; no FY2027 numerical growth input supplied. | 2026-10-02 |
| division_growth | DIVISION_3 | BASE | FY2027 | 2027 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Digital slot; no FY2027 numerical growth input supplied. | 2026-10-02 |
| acquisitions_disposals |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 transaction cash-flow input supplied. | 2026-10-02 |
| net_equity_issue_repay |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 equity issue/repurchase amount supplied. | 2026-10-02 |
| dividends_paid |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 dividend amount supplied. | 2026-10-02 |
| other_investing_financing |  | BASE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 other investing/financing amount supplied. | 2026-10-02 |
| division_growth | DIVISION_1 | BASE | FY2028 | 2028 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Las Vegas slot; no FY2028 numerical growth input supplied. | 2026-10-02 |
| division_growth | DIVISION_2 | BASE | FY2028 | 2028 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Regional/Managed slot; no FY2028 numerical growth input supplied. | 2026-10-02 |
| division_growth | DIVISION_3 | BASE | FY2028 | 2028 | null | PERCENT_DECIMAL | A-BASE-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Digital slot; no FY2028 numerical growth input supplied. | 2026-10-02 |
| acquisitions_disposals |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 transaction cash-flow input supplied. | 2026-10-02 |
| net_equity_issue_repay |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 equity issue/repurchase amount supplied. | 2026-10-02 |
| dividends_paid |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 dividend amount supplied. | 2026-10-02 |
| other_investing_financing |  | BASE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 other investing/financing amount supplied. | 2026-10-02 |
| division_growth | DIVISION_1 | DOWNSIDE | FY2026 | 2026 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Las Vegas slot; downside is qualitative; no numeric growth shock supported [C21, C22] | 2026-10-02 |
| division_growth | DIVISION_2 | DOWNSIDE | FY2026 | 2026 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Regional/Managed slot; no numerical downside input supplied. | 2026-10-02 |
| division_growth | DIVISION_3 | DOWNSIDE | FY2026 | 2026 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Digital slot; no numerical downside input supplied. | 2026-10-02 |
| acquisitions_disposals |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No downside transaction cash-flow value supplied. | 2026-10-02 |
| net_equity_issue_repay |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No downside equity financing value supplied. | 2026-10-02 |
| dividends_paid |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No downside dividend value supplied; not treated as zero. | 2026-10-02 |
| other_investing_financing |  | DOWNSIDE | FY2026 | 2026 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No downside other investing/financing value supplied. | 2026-10-02 |
| division_growth | DIVISION_1 | DOWNSIDE | FY2027 | 2027 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Las Vegas slot; no FY2027 numerical downside input supplied. | 2026-10-02 |
| division_growth | DIVISION_2 | DOWNSIDE | FY2027 | 2027 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Regional/Managed slot; no FY2027 numerical downside input supplied. | 2026-10-02 |
| division_growth | DIVISION_3 | DOWNSIDE | FY2027 | 2027 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Digital slot; no FY2027 numerical downside input supplied. | 2026-10-02 |
| acquisitions_disposals |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 downside transaction value supplied. | 2026-10-02 |
| net_equity_issue_repay |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 downside equity financing value supplied. | 2026-10-02 |
| dividends_paid |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 downside dividend value supplied. | 2026-10-02 |
| other_investing_financing |  | DOWNSIDE | FY2027 | 2027 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2027 downside other investing/financing value supplied. | 2026-10-02 |
| division_growth | DIVISION_1 | DOWNSIDE | FY2028 | 2028 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Las Vegas slot; no FY2028 numerical downside input supplied. | 2026-10-02 |
| division_growth | DIVISION_2 | DOWNSIDE | FY2028 | 2028 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Regional/Managed slot; no FY2028 numerical downside input supplied. | 2026-10-02 |
| division_growth | DIVISION_3 | DOWNSIDE | FY2028 | 2028 | null | PERCENT_DECIMAL | A-DOWN-OPERATING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Active Digital slot; no FY2028 numerical downside input supplied. | 2026-10-02 |
| acquisitions_disposals |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 downside transaction value supplied. | 2026-10-02 |
| net_equity_issue_repay |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 downside equity financing value supplied. | 2026-10-02 |
| dividends_paid |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 downside dividend value supplied. | 2026-10-02 |
| other_investing_financing |  | DOWNSIDE | FY2028 | 2028 | null | CURRENCY_MM | A-FINANCING | NOT_APPLICABLE | 5c51af90-71cc-4023-8aea-4523ce9f2428 | No FY2028 downside other investing/financing value supplied. | 2026-10-02 |

## Evidence Trace

| Claim | Marker | Document | Page |
|---|---|---|---:|
| FY2025 revenue | [C1] | Caesars FY2025 Form 10-K | 19 |
| FY2025 issuer Adjusted EBITDA | [C2] | Caesars FY2025 Form 10-K | 23 |
| H1 revenue growth | [C3] | Caesars Q2 2026 Form 10-Q | 19 |
| Q2/H1 Adjusted EBITDA | [C4] | Caesars Q2 2026 Form 10-Q | 16 |
| H1 operating cash flow and PP&E spending | [C5, C6] | Caesars Q2 2026 Form 10-Q | 4 |
| Cash, current debt and long-term debt | [C7, C14, C15, C25] | Caesars Q2 2026 Form 10-Q | 2 |
| Total cash and borrowing capacity | [C8] | Caesars Q2 2026 Form 10-Q | 22 |
| Scheduled maturities and interest estimates | [C9, C10] | Caesars Q2 2026 Form 10-Q | 9 |
| Lease payment and capex estimates | [C11, C12] | Caesars Q2 2026 Form 10-Q | 22 |
| Variable-rate borrowing exposure | [C13] | Caesars Q2 2026 Form 10-Q | 23 |
| Customer deposits and deferred revenue | [C16] | Caesars Q2 2026 Form 10-Q | 11 |
| Covenant compliance | [C17] | Caesars Q2 2026 Form 10-Q | 10 |
| Subsequent Alberta launch | [C18] | Caesars Q2 2026 Form 10-Q | 17 |
| Management liquidity sufficiency statement | [C19] | Caesars FY2025 Form 10-K | 24 |
| Pending-merger transaction costs | [C20] | Caesars Q2 2026 Form 10-Q | 6 |
| Las Vegas revenue and table-games hold | [C21, C22] | Caesars Q2 2026 Form 10-Q | 18, 20 |
| FY2025 CFO and capex; net interest | [C23, C26, C27] | Caesars FY2025 Form 10-K | 20, 31 |
| Interim net interest and rent-related cash interest | [C28, C24] | Caesars Q2 2026 Form 10-Q | 3, 5 |
| H1 change in cash | [C29] | Caesars Q2 2026 Form 10-Q | 4 |

## Source Registry

| source | use | period | limitation |
|---|---|---|---|
| Caesars FY2025 Form 10-K | Audited annual revenue, Adjusted EBITDA, CFO, capex, debt and management liquidity statement | FY2025 | Historical; not an October 2026 update. |
| Caesars Q2 2026 Form 10-Q | Unaudited H1/Q2 statements, June balance sheet, debt service, liquidity, capex, customer liabilities and covenant compliance | Through June 30, 2026 | No post-June financials or complete next-12-month forecast. |
| Accepted CP-0 handoff | Source-readiness and period-coverage limits | Q2 2026 | Restricted upstream context; not primary financial evidence. |
| Accepted CP-1 handoff | Canonical history and carrying-debt definitions | Q2 2026 | Restricted; incomplete quarter coverage and no forward schedule. |
| Accepted CP-1D handoff | Earnings-quality and debt-like obligation limitations | Q2 2026 | Restricted; quality-adjusted EBITDA unresolved. |
| Accepted CP-2A handoff | Qualitative downside pathways and triggers | Q2 2026 | Restricted; no quantitative forecast. |
| Accepted CP-2D handoff | Partial liquidity bridge and use schedule | Q2 2026 | Restricted; ending 12-month liquidity unavailable. |

## Gaps & Conflicts

The main gap is the forward horizon: sources provide a June 30 liquidity snapshot and selected remainder-2026 cash-use estimates, but not forward operating cash, cash taxes, working capital, H1 2027 rent/capex/debt service or current covenant headroom. Therefore no exact 12-month cash-use total, ending accessible liquidity or positive cash-burn rate can be supported. The $610 million LTM CFO-less-PP&E calculation is a historical proxy only. [C5, C6, C9, C10, C11, C12]

The positive counterevidence—H1 revenue growth, positive CFO, June liquidity and reported covenant compliance—does not resolve the missing period after June or establish future revolver access. [C3, C5, C8, C17] Carrying debt and financing obligations are separate reported lines and are not silently combined in the canonical debt figure. [C14, C15] Alberta’s July 13 launch is a subsequent event, not part of Q2 results. [C18] CP-1D’s recurring adjustments and unresolved transaction-cost composition prevent a quality-adjusted denominator. [C2, C4, C20]

## QA Validation

| check | result | note |
|---|---|---|
| Identity, lineage and forecast scope | Self-checked | Host-owned identity and hashes retained; FY2026-FY2028 horizon and Q2 2026 LTM base applied. |
| Historical-to-base calculations | Self-checked | LTM flow values use FY2025 + H1 2026 − H1 2025; balance-sheet values remain June 30 snapshots. |
| Assumption labels and continuity | Restricted | Sources, calculations and analyst judgments are distinguished; no forward numerical assumptions are invented. |
| Forecast engine and debt/cash roll-forward | Restricted | Dated scheduled debt service is shown; closing values and residuals remain unavailable rather than plugged. |
| Scenario isolation and downside | Self-checked with limitations | Base, upside and downside are separated; downside changes named drivers qualitatively and has no probability weight. |
| FCF, leverage and coverage definitions | Self-checked | Carrying debt, financing obligations, P&L interest, rent interest and FCF proxy remain distinct. |
| CP-MODEL interface | Restricted; not consumable | Stable table has 42 BASE/DOWNSIDE rows for FY2026-FY2028. Active division slots have no sourced numeric inputs; rows are not evidence of inactive divisions, and no case period is consumable. |
| Null handling | Self-checked | Unsupported values remain null in the tagged table and dashes in untagged registers; no missing value is converted to zero. |
| Downside breakpoint and triggers | Restricted | Causal operating-to-cash-to-refinancing pathway and observable monitoring triggers are stated; numerical breakpoint and runway are unavailable. |
| Subsequent-event handling | Self-checked | July 13 Alberta launch is flagged separately and not blended into Q2 actuals. |
| Confidence and status | Restricted | Confidence 50/100, Low; QA Restricted; committee status Requires More Work. |
| Host automated validation | Pending | Host validation follows this response; no script output, exit status or host finding is claimed. |