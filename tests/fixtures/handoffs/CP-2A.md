---
module_id: CP-2A
run_id: 20261011-czr-full-credit-assessment
issuer_id: CZR
analysis_date: 2026-10-02
qa_status: Restricted
inputs: CP-0, CP-1, CP-2, MODEL, CP-1A, CP-1B
---

## Analysis

Hand-written method fixture on the supplied synthetic Primary pack `czr-2026q2-primary`; conditional downside judgments are Analyst Inference, not source forecasts. Baseline is the CP-1/MODEL entity and periods unchanged. Search scope: issuer Q2 earnings release/10-Q, FY2025 10-K, merger release and supplied synthetic capitalisation; CP-2's fundamental chain supplies the monitoring context. CP-DR is unavailable and remains a limitation. The monitoring horizon is the 12 months from 2026-10-02, an analyst scope rather than an asserted event date.

Primary fragility: lower Las Vegas visitation transmits through fixed rent into weaker cash generation and refinancing flexibility [C1] [C2] [C3]. The first break is visitation, not an invented EBITDA shock. A second path is disruption during the proposed acquisition: integration benefits may not arrive while operational attention is diverted [C4]. The issuer identifies these risks; the cash-flow and creditor transmission is conditional inference. Probability and impact remain Unknown because no calibrated likelihood or severity is supplied. Neither chain establishes default, a recovery percentage, legal headroom or an exact liquidity exhaustion date.

Business model: revenue/volume and price/mix depend on discretionary casino/hospitality demand; cost flexibility is constrained by fixed lease charges [C2] [C3]. The supplied material does not calibrate contract retention, customer concentration, input pass-through, WC seasonality, maintenance capex or debt-service stress. Those missing dimensions limit the chain rather than supplying zero. Cash-flow conversion and leverage/liquidity/refinancing effects are qualitative; no CP-1 or MODEL number is recomputed. CP-3 receives conditional risk-premium implications; CP-6 receives the two triggers and the counter-case; CP-5 receives the missing timing/calibration and source-lineage limits. Later liquidity/legal consumers need sourced constraints before making capacity or recovery claims.

Calendar/event assessment: proposed acquisition, category corporate transaction, one identified material event; announcement is dated May 28, 2026 [C8], outside this forward horizon. Closing is subject to shareholder/regulatory conditions and has no supported date in this fixture [C5]; it is an undated-event gap, not a dated calendar entry. Path 002 retains that conditional timing. No timing/channel cluster or numeric event probability can be established. Monitoring priority is an analyst Medium judgment for both paths; review on subsequent issuer results or a disclosed transaction development, not an asserted issuer reporting schedule. Strongest counter-case: Regional and Digital growth offsets Las Vegas weakness [C6] [C7]. It wins if the earnings mix sustains cash generation and visitation stabilises, reducing escalation urgency; the required evidence is a subsequent issuer release. Overall, the fastest supported path is visitation weakness -> fixed-charge cash-flow pressure -> reduced deleveraging/refinancing flexibility; watch subsequent Las Vegas operating disclosure.

## Tables

<!-- table: cp2a.downside_paths -->
| path_id | driver | first_break | transmission | consequence | time_horizon | probability | impact | confidence | cite |
|---|---|---|---|---|---|---|---|---|---|
| CP-2A-DP-001 | Revenue: Las Vegas visitation | Lower visitation reduces non-gaming revenue | Analyst Inference: lower revenue with fixed rent reduces cash available after lease charges and debt service | Directional Only: less deleveraging and refinancing flexibility; no default/recovery estimate | Analyst monitoring scope: 12 months from 2026-10-02; onset/severity not dated | Unknown | Unknown | Low | [C1] [C2] [C3] |
| CP-2A-DP-002 | Governance: proposed acquisition integration | Disruption of operating plans or management attention | Analyst Inference: delayed benefits and integration demands could weaken cash generation | Directional Only: less financial flexibility during transaction execution; magnitude unknown | Conditional on transaction execution; closing timing unavailable within analyst 12-month scope | Unknown | Unknown | Low | [C4] [C5] |

<!-- table: cp2a.sensitivities -->
| sensitivity | input_basis | method | result | unit_label | interpretation | status | cite |
|---|---|---|---|---|---|---|---|

<!-- table: cp2a.triggers -->
| trigger_id | indicator | lead_lag | threshold | linked_path | consequence | cite |
|---|---|---|---|---|---|---|
| CP-2A-MON-001 | Las Vegas visitation disclosed in subsequent issuer results | Leading | Quantitative threshold not available in provided materials; further disclosed visitation weakness is a Directional Only escalation signal | CP-2A-DP-001 | Reassess fixed-charge cash conversion and refinancing flexibility | [C1] |
| CP-2A-MON-002 | Disclosed transaction disruption or delay to benefits | Lagging | Quantitative threshold not available in provided materials; an adverse transaction update is an Analyst Inference escalation signal | CP-2A-DP-002 | Reassess integration cash demands and confidence in deleveraging | [C4] |

## Gaps

- High: no source-calibrated shocks, elasticities, cash-flow component stress or break-even limits; sensitivities stay empty. Supply dated operating/price/volume and cash-flow sensitivities on CP-1/MODEL definitions, not invented zero or a numerical downside case.
- Medium: no calibrated likelihood/severity or closing date. Unknown axes and conditional horizon preserve the gap. A dated transaction update and current operating data would lift it; never turn a month/quarter into an exact day.
- Medium: retention/concentration, supplier/input pass-through, WC seasonality, capex split, usable revolver, legal covenant/structural constraints and refinance/recovery stress are uncalibrated here. CP-3/CP-6 must retain these limitations; obtain governing sources before capacity/default/recovery conclusions. Optional CP-DR missing; no fetch is authorized.

## Citations

<!-- table: citations -->
| id | source | locator | excerpt |
|---|---|---|---|
| C1 | CZR_Q2_2026_10Q.txt | MD&A, Las Vegas | lower city-wide leisure customer visitation resulting in decreased non-gaming revenues |
| C2 | CZR_FY2025_10K.txt | Risk factors, indebtedness | VICI and GLPI that require an annual rent payment of $1.4 billion in 2026 |
| C3 | CZR_FY2025_10K.txt | Supplemental disclosure of cash flow information | Cash interest paid for rent related to financing obligations \| 1,349 \| 1,324 \| 1,286 |
| C4 | CZR_2026_Merger_Press_Release.txt | Forward-looking statements | disruption of Caesars’ current plans and operations or diversion of management’s attention from ongoing business operations and opportunities |
| C5 | CZR_2026_Merger_Press_Release.txt | Transaction Details | satisfaction of customary closing conditions, including applicable regulatory approvals |
| C6 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Regional \| 923 \| 879 \| 5.0% |
| C7 | CZR_Q2_2026_Earnings_Release.txt | Adjusted EBITDA, six months ended June 30 | Caesars Digital \| 137 \| 123 \| 11.4% |
| C8 | CZR_2026_Merger_Press_Release.txt | p.1 | LAS VEGAS and RENO, Nev. (May 28, 2026) |
