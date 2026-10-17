---
module_id: "CP-2A"
module_name: "DownsidePathway"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
credit_os_profile_id: "LITE_CREDIT_22"
credit_os_selection_id: "LITE_FULL_CREDIT_SCREEN"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-2A-12b1d1a01f5bce14"
credit_os_route_node_id: "RN-LITE_CREDIT_22-LITE_FULL_CREDIT_SCREEN-05-CP-2A"
credit_os_invocation_sha256: "22043175474a496de07d5cfd765b64a14d407524a3bd92f56a8ebf7fa880d9ae"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "dcb45fd922bd40cf339a42308e91a3fac8f6e23b9f198f147d86c85f73a15eeb"
  - module_id: "CP-L10"
    run_id: "COS-20261005T115024Z-471a30438a704fecbd6b1c218daa53f5"
    period: "Q2 2026"
    sha256: "1b3412810ea6d286e8dd1b78eaea47c62bfa80734d5ca52486c3d5933abc0d12"
confidence_score: 57
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Restricted"
limitation_flags: ["SOURCE_LIMITED_NOT_COMMITTEE_READY", "FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "LITE_FULL_UPGRADE_REQUIRED"]
validation_warnings: ["FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED", "SOURCE_LIMITED", "LITE_FULL_UPGRADE_REQUIRED"]
downstream_consumers: ["CP-2B", "CP-6", "CP-6A", "CP-5", "CP-5A", "CP-MODEL"]
---

## Audit Summary

- **Canonical handoff:** `CZR_CP-2A_20261002.md`.
- **Run status:** Completed with Limitations; screening scope only.
- **Confidence:** 57 — Low. Evidence quality is strongest for Q2 reported operating, cash-flow, debt, liquidity and transaction disclosures; coverage is restricted by missing annual history, issuer forecasts, current legal/lease documents, current transaction status and market evidence.
- **Scoring basis:** Own assessment: E=72, C=90, S=0.7; `(0.6 × 72 + 0.4 × 90) × 0.7 = 57.12`, rounded to 57. Restricted status follows the LITE upgrade requirement and material evidence gaps.
- **Upstream re-anchor:** Accepted CP-0 and CP-L10 handoffs match this issuer, Q2 2026 period and run. CP-0 is source-readiness context; CP-L10 is a screening-only artifact. Neither is treated as source evidence or used to replace the delivered filing evidence.
- **Module status:** Ready with Limitations. This FULL module remains on the `LITE_CREDIT_22` profile; missing FULL inputs are not inferred. A new, user-confirmed, linked `FULL_CREDIT_32` run is recommended to provide them.
- **Committee posture:** Restricted; this screening-only pathway does not provide committee clearance, a rating, security selection or a final relative-value conclusion.

## Analysis

### Downside view

Caesars’ clearest supported first break is weaker Las Vegas leisure visitation, with lower non-gaming revenue, hotel occupancy and rates, alongside lower table-games drop and hold. [C2, C3] That weakens segment EBITDA and margin; if it persists, cash available after operating needs, capex, debt service and rent contracts, pressuring liquidity and refinancing flexibility. The risk is elevated by substantial scheduled debt service, lease payments and variable-rate borrowing, but no sourced downside forecast or current liquidity bridge establishes a failure date or threshold. [C11, C12, C13, C14] Regional growth, reported cash and revolver capacity, and positive six-month operating cash flow are the strongest counterweights; they temper conviction but do not establish durable consolidated FCF or current forward headroom. [C4, C7, C9, C10] Monitor Las Vegas visitation, table-games activity, segment EBITDA, cash generation, accessible revolver capacity and dated merger disclosures.

**Stress-pathway summary:** The table identifies the supported initiating stress and the two principal financial accelerators; the full causal vectors and limitations remain in the appendix.

| Pathway | First observable break | Financial transmission | Creditor consequence | Evidence |
|---|---|---|---|---|
| Las Vegas demand | Lower city-wide leisure visitation; lower table-games drop and hold | Weaker hotel/non-gaming revenue and EBITDA; pressure on cash available after fixed cash uses | FCF durability and refinancing capacity weaken if persistent | [C2, C3] |
| Cash conversion | Operating cash flow must absorb capex, debt service and rent | Cash buffer may erode; revolver use could rise | Liquidity risk increases; no sourced trigger threshold | [C7, C8, C11, C12] |
| Floating rate | Higher rates on material unhedged variable-rate borrowings | Cash interest rises; FCF and debt-service capacity fall | Deleveraging and refinancing flexibility weaken | [C13, C25] |
| Transaction | Merger conditions or end-date slippage | Further transaction costs, disruption or delayed resolution are possible | Monitoring and liquidity attention increase; outcome remains uncertain | [C19, C20, C21] |

Regional EBITDA growth and the reported liquidity position are meaningful contrary evidence: if subsequent periods show sustained Las Vegas stabilization, resilient cash generation after all cash uses and maintained accessible facility capacity, the downside view would lose force. Until those observations and a current forecast are delivered, that counterargument reduces conviction but does not overturn the supported operating-risk pathway. [C4, C7, C9, C10]

### Catalyst view

The filing discloses two dated merger-related milestones within the 12-month monitoring window: the merger’s stated initial end date of May 27, 2027 and a ticking-fee date of June 26, 2027 if closing has not occurred. [C18, C19] The filing also describes shareholder, antitrust and gaming regulatory conditions; it does not establish current post-Q2 status or disclose dates for those approvals. [C20] These are not predictions of completion or failure. A delay or failure could bring transaction costs and operating disruption; a completed merger is not assumed to improve creditor outcomes. [C21]

Monitor subsequent filed transaction-status disclosures, regulatory and shareholder milestones when expressly dated, and any filing that changes the stated end dates or consideration. The dated event set is sparse; no undated event has been assigned a calendar date. Full event-source, risk, priority and handoff records appear below.

### Operating transmission and monitoring

The company reports a diversified gaming and hospitality operation, with casino gaming its primary revenue source and hotels, food, beverage, entertainment and digital offerings also supporting visitation and revenue. [C1, C6, C26] This breadth and Regional growth provide some offset, but do not remove the Las Vegas concentration of the fastest evidenced downside path. Digital results carry a different risk: hold variability and promotional/marketing expense can adversely affect segment results. [C4, C5]

Cash conversion, not EBITDA alone, is decisive. Six-month operating cash flow was $675 million versus $680 million in the prior-year period, while property and equipment purchases were $335 million versus $453 million. [C7, C8] Adjusted EBITDA is not a liquidity measure; the filing identifies capex, cash interest, debt principal, taxes, distributions and lease payments as cash uses not captured by it. [C16] Management’s Q2 disclosure estimated $425 million of debt service and $687 million of VICI/GLPI lease payments for the remainder of 2026; these are dated estimates, not an October 2 liquidity forecast. [C11, C12]

The June 30 filing reported $965 million of cash and $1.9 billion of CEI revolver borrowing capacity after stated reserves and commitments. [C9, C10] These resources and management’s stated liquidity expectation are contrary evidence, but a current accessible-liquidity bridge, subsequent cash position and forward uses are not supplied. No covenant headroom or liquidity runway is inferred. The filing reports covenant compliance at June 30, 2026; this is a dated fact, not a projection. [C15]

### Analytical appendix — complete canonical registers

#### T2B.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Caesars Entertainment, Inc. Form 10-Q, quarter ended June 30, 2026 | Primary-Verified | Q2 and six months ended 2026-06-30 | Caesars Entertainment, Inc. and consolidated subsidiaries | Segment operating data, financial statements, cash flows, debt, liquidity, leases, covenants and transaction disclosures. [C1, C2, C7, C9, C14, C15] | Interim unaudited filing; references the 2025 Form 10-K, which is not in the delivered evidence. [C17] Current forecasts and subsequent transaction status are not supplied. | Primary operating and financial baseline; bounded downside pathways; catalyst dates and monitoring. |
| 4edecdd2-6ed8-429e-902c-eb92822cd767 | Caesars Entertainment, Inc. Q2 2026 earnings release | Secondary-Reputable | Q2 2026 | Caesars Entertainment, Inc. | Supplemental reported results and issuer-defined debt/net-debt presentation. [C24] | Non-GAAP measures are issuer-defined; not interchangeable with carrying-value debt or cash-flow measures. [C16, C23, C24] | Cross-check reported direction and preserve differing debt definitions. |
| b24b47d6-6bfd-4248-b660-e867409dd303 | Incremental Assumption Agreement No. 3 and conformed credit agreement | Primary-Verified | Executed 2024 document; Q2 2026 context | Borrower and listed loan parties | Credit-agreement provisions and a conformed agreement through the February 2024 amendment. | No supplied evidence establishes whether later amendments exist; this document alone does not provide current covenant calculations or capacity. | Directional financing and covenant-document context; legal/capacity review remains for the relevant full modules. |
| CP-0 | Accepted CP-0 SourceReadiness handoff | User-Provided | Q2 2026 | Caesars Entertainment, Inc. source-readiness scope | Accepted source inventory, readiness and limitations. | Context, not evidence; restricted readiness. Not cited for analytical claims. | Re-anchor scope and carry source limitations. |
| CP-L10 | Accepted CP-L10 LiteFinancialChangeScreen handoff | User-Provided | Q2 2026 | Caesars Entertainment, Inc. screening scope | Accepted LITE screening scope, upgrade requirement and identified gaps. | Screening only; not a FULL baseline and not treated as source evidence. | Re-anchor LITE boundary; do not substitute its conclusions for delivered evidence. |

#### T2B.2 — Business Model Snapshot

| Dimension | Source-Supported Fact | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|
| Revenue model | Gaming is the primary revenue source; hospitality and digital gaming also contribute. [C1, C6] | Gaming volume and win/hold, visits, hotel activity and digital use feed revenue. | Demand or hold weakness may reduce revenue and operating cash generation. | 10-Q pp. 17–18. [C1, C6] | Full demand history and forward assumptions are not supplied. |
| Product/service criticality | The company operates gaming properties and digital wagering applications. [C1, C6] | Property visitation and platform activity support the reported revenue mix. | Operating disruption can affect revenue and FCF; no service interruption is asserted. | 10-Q pp. 17–18. [C1, C6] | No property-level downside contribution analysis is supplied. |
| Customer/end-market exposure | Results depend on customer volume and quality; Las Vegas leisure visitation declined. [C2, C6] | Lower discretionary visitation can reduce non-gaming revenue, occupancy and rates. | Revenue and EBITDA pressure may weaken debt-service capacity if sustained. | 10-Q pp. 18, 20. [C2, C6] | Customer concentration and quantified demand elasticity are not supplied. |
| Price/mix | Las Vegas hotel rates were lower; reported gaming measures include table-games hold and slot handle. [C2, C3] | Lower rates or adverse gaming outcomes can reduce revenue and margin even if some volumes hold. | FCF and refinancing flexibility may weaken; magnitude beyond reported periods is not calculated. | 10-Q p. 20. [C2, C3] | Property-level rate/mix bridge is not supplied. |
| Volume drivers | The filing identifies visitation, table-games drop, slot handle and digital handle as relevant measures. [C3, C6] | Reduced visits or wagering volume reaches casino and hotel revenue before cash-flow effects. | Leading monitoring should focus on visitation, drop/handle and occupancy. | 10-Q pp. 18, 20. [C3, C6] | No management downside thresholds are supplied. |
| Contract duration/churn/retention | Customer deposits and rewards liabilities relate to gaming, loyalty and advance payments; generally expected to be recognized within one year. [C17] | A demand shock could alter customer activity and timing of performance/refunds; cash consequences are not quantified. | Potential working-capital/liquidity sensitivity requires monitoring, not an assumed cash outflow. | 10-Q p. 11. [C17] | Churn, retention, redemption and refund behavior are not disclosed in the delivered evidence. |
| Cost structure | Casino expense includes salaries/wages, gaming taxes and marketing; G&A includes property costs and administration. | Weaker revenue with persistent costs can compress margins; reported labor and tax increases add pressure in some segments. | Lower EBITDA can reduce cash available for interest, debt service and rent. | 10-Q p. 19. [C2, C5] | Flexible versus fixed cost split is not supplied. |
| Input-cost exposure | Regional margin commentary attributes pressure partly to labor costs and gaming taxes; no complete cost sensitivity is delivered. | Costs rising faster than revenue would compress cash earnings. | FCF durability and debt-service capacity may weaken. | 10-Q p. 20. [C4] | No sourced wage, energy or tax stress assumptions. |
| Working-capital needs | Six-month operating cash flow was affected primarily by changes in working capital. [C7] | Working-capital absorption can reduce cash despite reported operating earnings. | Liquidity buffer may erode before a leverage or refinancing issue is observable. | 10-Q p. 22. [C7] | Seasonal detail and a current cash-flow bridge are not supplied. |
| Capex intensity | Six-month property/equipment purchases were reported; Q2 filing also gives a remaining-2026 estimate. [C8, C24] | Maintenance and growth spending compete with debt service and rent for cash; deferral flexibility is not established. | Lower discretionary cash can weaken FCF and liquidity. | 10-Q pp. 4, 22. [C8, C24] | Maintenance/growth flexibility beyond disclosed classifications is not established. |
| Liquidity dependency | The Q2 filing reports cash, CEI revolver capacity and substantial remaining-2026 debt service and lease estimates. [C9, C10, C11, C12] | Cash uses or reduced accessible capacity can turn earnings pressure into a liquidity pinch. | Liquidity deterioration is a higher-order creditor risk; current runway is not calculated. | 10-Q pp. 2, 10, 22. [C9, C10, C11, C12] | No October 2 cash bridge, restricted-cash availability analysis or current facility update. |
| Debt service/refinancing dependency | Debt maturities include larger scheduled amounts in 2030 and thereafter; variable-rate borrowing is material. [C13, C14] | Cash-interest increases or weak FCF can reduce repayment capacity and refinancing flexibility. | Refinancing risk rises if operating weakness coincides with maturities or restricted market access. | 10-Q pp. 9, 23. [C13, C14] | No current market pricing, forecast, covenant headroom or refinancing plan is supplied. |

#### T2B.3 — Fragility Map

| Fragility Driver | First Break Point | Evidence | Risk Mechanic | Credit Implication | Confidence | Source Trace |
|---|---|---|---|---|---|---|
| Revenue | Las Vegas leisure visitation and table-games activity weaken. | Lower city-wide leisure visitation, hotel occupancy/rates and table-games drop are disclosed. [C2, C3] | Lower visits/drop → lower hotel and gaming revenue → weaker segment EBITDA → less cash for fixed uses. | FCF durability, liquidity and refinancing capacity weaken if persistent. | High | 10-Q p. 20. [C2, C3] |
| Margin | Las Vegas Adjusted EBITDA margin declines with lower revenue; Regional commentary identifies higher labor costs and gaming taxes. | Las Vegas deterioration; Regional margin was affected by labor and gaming taxes. [C2, C4] | Revenue weakness or cost pressure → operating deleverage → EBITDA/FCF pressure. | Debt-service capacity and deleveraging weaken. | Medium | 10-Q pp. 20–21. [C2, C4] |
| Cash-conversion | Working-capital movements and capex compete with operating cash flow. | Six-month cash from operations and property/equipment purchases are disclosed. [C7, C8] | Cash absorption/capex → lower cash after debt service and rent → buffer erosion. | Liquidity pressure may precede a covenant or maturity event. | Medium | 10-Q pp. 4, 22. [C7, C8, C11, C12] |
| Liquidity | Current accessible liquidity cannot be tested against an updated forward cash bridge. | Q2 filing reports cash and revolver capacity, plus dated remaining-2026 uses. [C9, C10, C11, C12] | Deteriorating cash generation or capacity → reduced payment flexibility → greater revolver reliance. | Liquidity risk is material; no runway or failure date is calculated. | Medium | 10-Q pp. 2, 10, 22. [C9, C10, C11, C12] |
| Capital-structure | Variable-rate cash interest and scheduled maturities become harder to service if EBITDA/FCF declines. | $6.0 billion variable-rate borrowings; maturity schedule disclosed. [C13, C14] | Rates or operating pressure → higher debt-service burden/less deleveraging → refinancing flexibility narrows. | PD and refinancing risk could increase; no covenant headroom is inferred. | Medium | 10-Q pp. 9, 23. [C13, C14] |
| Legal/structural | Current collateral, guarantee and lease-document perimeter is not established by the delivered set. | Q2 filing describes guarantees/security subject to exceptions; delivered credit agreement is a 2024 conformed version. | Exclusions or changed documents could affect enforcement and recovery; actual change is not established. | LGD/recovery conclusion remains open; no security recommendation. | Not Assessable | 10-Q p. 11; 2024 agreement source. |
| Governance/sponsor | Current transaction status and any subsequent creditor-relevant capital-allocation action are not established. | Q2 merger disclosure is conditional; no current transaction update is included. [C19, C20] | A delayed/failed transaction could cause costs or disruption; no sponsor behavior is inferred. | Monitoring and refinancing uncertainty increase; direction of outcome remains uncertain. | Low | 10-Q pp. 5, 25. [C19, C20, C21] |
| Macro | Interest-rate sensitivity is source-supported; other issuer-specific macro mismatches are not. | Variable-rate borrowing is material and no cash-flow hedges were held at June 30. [C13, C25] | Higher reference rates → higher cash interest → lower FCF → weaker debt service. | FCF and refinancing flexibility are rate-sensitive; no numerical shock is assumed. | Medium | 10-Q pp. 7, 23. [C13, C25] |

#### T2B.4 — Stress Transmission Table

| Operating Stress | Cash-Flow Impact | Leverage / Liquidity Result | Credit Consequence | Evidence Status | Source Trace |
|---|---|---|---|---|---|
| Lower Las Vegas leisure visitation and table-games activity → lower non-gaming revenue, occupancy/rates and gaming revenue. [C2, C3] | Lower segment EBITDA reduces cash generation; the effect on FCF depends on working capital, capex, interest and rent. | Cash available after fixed uses falls; no leverage outcome is calculated. | FCF durability and refinancing capacity weaken if the operating stress persists. | Source Fact | 10-Q p. 20; cash conversion context p. 22. [C2, C3, C7, C11, C12] |
| Lower demand with labor/tax cost pressure. [C4] | Margin compression reduces cash available for debt service. | Slower deleveraging and reduced liquidity flexibility are directional, not quantified. | Higher refinancing/PD sensitivity if combined with maturity or rate pressure. | Analyst Inference | 10-Q pp. 20–21; Adjusted EBITDA limitations p. 16. [C4, C16] |
| Higher rates on variable-rate borrowing without cash-flow hedges. [C13, C25] | Cash interest rises; FCF after interest falls. | Less internal cash for scheduled principal, rent and capex; no interest shock quantified. | Debt-service and refinancing capacity weaken. | Directional Only | 10-Q pp. 7, 23. [C13, C25] |
| Working-capital absorption or capex maintained through weaker operations. [C7, C8] | More cash is tied up or spent while operating inflows are pressured. | Cash buffer could erode and revolver reliance could rise. | Liquidity deterioration; observable trigger is cash flow and accessible facility capacity. | Analyst Inference | 10-Q pp. 4, 22. [C7, C8, C9] |
| Merger delayed or not completed. [C19, C20] | Filing identifies possible transaction costs and business disruption; amount and timing are not forecast. | No liquidity or leverage outcome is calculated. | Monitoring and operating uncertainty rise; event direction remains uncertain. | Source Fact | 10-Q pp. 5, 25. [C19, C20, C21] |
| Current covenant headroom, current accessible liquidity and recovery under stress. | No sourced downside cash-flow bridge or current calculation is delivered. | No covenant capacity, liquidity runway or recovery estimate is produced. | Escalate for FULL inputs before committee or security conclusions. | Insufficient Information | Q2 covenant compliance is historical only; current calculations not supplied. [C15] |

#### T2B.5 — Downside Pathway Register

| Pathway Row ID | Pathway Category | Driver | Causal Vector | PD/LGD/RV/Monitoring Consequence | Source Trace | Confidence | Downstream Module |
|---|---|---|---|---|---|---|---|
| CP-2A-DP-001 | First Break Point | Las Vegas demand | Lower leisure visitation/table-games activity → weaker non-gaming and gaming revenue → lower Las Vegas EBITDA → less cash generation → reduced FCF and refinancing flexibility if persistent. [C2, C3] | Primary monitoring path; negative for FCF durability and potentially PD/refinancing capacity. | 10-Q p. 20. [C2, C3] | High | CP-2D; CP-3; CP-6/CP-6A |
| CP-2A-DP-002 | Transmission Accelerator | Margin/cost | Revenue pressure plus labor/tax expense → margin compression → lower operating cash generation → reduced cash available for debt service and rent. [C4] | Accelerates liquidity and refinancing pressure; monitor segment margins and cash conversion. | 10-Q pp. 20–21; cash-use disclosures pp. 16, 22. [C4, C16, C11, C12] | Medium | CP-2D; CP-3C; CP-4A |
| CP-2A-DP-003 | Cash-Flow Conversion Point | Cash conversion | Working-capital absorption or capex alongside weaker operating cash flow → lower post-capex cash → less capacity for debt service, rent and liquidity replenishment. [C7, C8, C11, C12] | FCF durability and liquidity worsen directionally; no amount or threshold is asserted. | 10-Q pp. 4, 22. [C7, C8, C11, C12] | Medium | CP-2D; CP-3B; CP-6/CP-6A |
| CP-2A-DP-004 | Liquidity Pinch Point | Liquidity | Cash-generation weakness plus scheduled debt service, rent and capex → cash/revolver resources decline → payment flexibility narrows. [C9, C10, C11, C12] | Liquidity and PD risk become acute only if accessible resources fail to meet uses; threshold is not established. | 10-Q pp. 2, 10, 22. [C9, C10, C11, C12, C24] | Medium | CP-2D; CP-3B; CP-3C |
| CP-2A-DP-005 | Refinancing Inflection | Capital structure | Lower EBITDA/FCF or higher variable-rate interest → weaker debt-service capacity → scheduled maturities harder to refinance or repay. [C13, C14, C25] | Refinancing risk increases; no funding failure, spread or refinancing date is predicted. | 10-Q pp. 9, 23. [C13, C14, C25] | Medium | CP-3C; CP-2H; CP-6/CP-6A |
| CP-2A-DP-006 | Covenant Inflection | Covenant | Operating weakness → potential reduction in covenant capacity; actual headroom and current definitions are not delivered. | Cannot infer breach or cushion; obtain current covenant calculation and controlling documents. | June 30, 2026 compliance was reported; that does not establish future headroom. [C15] | Low | CP-4A; CP-5A |
| CP-2A-DP-007 | LGD/Recovery Escalator | Legal/structural | Any future collateral/guarantee perimeter change or priming event could alter recovery; no such change is established by this evidence. | Recovery and security selection are not assessed; monitor current documents, guarantees, liens and collateral evidence. | Q2 filing describes secured guarantees subject to exceptions; full current package is not delivered. | Not Assessable | CP-3A; CP-4C |
| CP-2A-DP-008 | Monitoring Trigger | Transaction | Merger condition delay or failure → possible additional costs/disruption → potential operating cash-flow pressure; subsequent status is not established. [C19, C20] | Event-driven monitoring; no merger outcome or credit benefit assumed. | 10-Q pp. 5, 25. [C19, C20, C21] | Medium | CP-3C; CP-5; CP-6/CP-6A |
| CP-2A-DP-009 | Gap | Forecast and current liquidity | Missing current forecast and cash bridge prevents reliable quantification of operating stress → FCF → liquidity → refinancing consequences. | Restricted confidence; obtain current forecast, liquidity bridge and operative debt/lease documents. | Q2 disclosure is the latest delivered financial-period evidence; dated uses are not an October forecast. [C11, C12] | Not Assessable | CP-2D; CP-2G; CP-5A |

#### T2B.6 — Downside Sensitivity Matrix

| Sensitivity | Input Basis | Formula / Method | Result | Credit Interpretation | Status | Source Trace |
|---|---|---|---|---|---|---|
| Las Vegas revenue/volume weakening | Q2 filing identifies lower leisure visitation, table-games drop and hold. [C2, C3] | No sourced stress percentage or segment sensitivity; directional chain only. | Further demand/hold weakness would reduce segment cash earnings; amount not supported. | Lower FCF and refinancing flexibility if persistent. | Directional Only | 10-Q p. 20. [C2, C3] |
| Margin compression | Segment commentary identifies labor and gaming-tax pressure in Regional and weaker Las Vegas results. [C2, C4] | No issuer-specific incremental-cost pass-through or stress case supplied. | Directional reduction in cash earnings; magnitude not supported. | Less cash available for fixed cash uses. | Directional Only | 10-Q pp. 20–21. [C2, C4] |
| Working-capital absorption | Six-month CFO was $675 million versus $680 million; working capital contributed to the comparison. [C7] | No seasonal or component-level downside inputs supplied. | Cash-flow sensitivity cannot be sized from the delivered inputs. | May accelerate liquidity use. | Not Calculable | 10-Q p. 22. [C7] |
| Capex increase or deferral | Six-month purchases and remaining-2026 estimate disclosed. [C8, C24] | No stress assumption or maintenance-versus-discretionary cut case supplied. | Direction only: higher spend consumes cash; deferral flexibility is not established. | Competes with debt service and rent. | Directional Only | 10-Q pp. 4, 22. [C8, C24] |
| Cash-interest increase | $6.0 billion long-term variable-rate borrowing; no cash-flow hedges reported. [C13, C25] | No specified rate shock or complete loan-level exposure schedule supplied. | Interest sensitivity cannot be sized from the delivered inputs. | Higher cash interest would reduce FCF and debt-service capacity. | Not Calculable | 10-Q pp. 7, 23. [C13, C25] |
| Liquidity draw / covenant headroom | Cash, facility capacity and historical covenant compliance are disclosed for June 30, 2026. [C9, C10, C15] | No current facility availability bridge, current test calculation or stress EBITDA supplied. | No runway, draw threshold or headroom result is produced. | Do not infer covenant capacity or liquidity exhaustion. | Not Calculable | 10-Q pp. 2, 10, 23. [C9, C10, C15] |
| Refinancing spread/coupon | Maturity schedule disclosed; no current spread/coupon input in delivered evidence. [C14] | No dated spread, curve or refinancing assumption supplied. | No refinancing cost or coupon scenario is estimated. | Market access remains an unquantified sensitivity. | Not Calculable | 10-Q p. 9; no market input delivered. [C14] |

#### T2B.7 — Monitoring Sensitivity Flags

| Trigger ID | Indicator | Leading / Lagging | Threshold or Qualitative Signal | Linked Pathway Row | Escalation Consequence | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| CP-2A-MON-001 | Las Vegas leisure visitation, hotel occupancy/rates and table-games drop/hold | Leading | Qualitative: renewed deterioration from the reported Q2 pattern or failure to stabilize. Quantitative threshold not available in provided materials. | CP-2A-DP-001 | Refresh operating-to-EBITDA-to-cash pathway; elevate CP-2D and reviewer monitoring. | 10-Q p. 20. [C2, C3] | No management threshold or monthly property data supplied. |
| CP-2A-MON-002 | Las Vegas and consolidated Adjusted EBITDA/margins | Lagging | Qualitative: further decline or margin compression in subsequent reported periods. Quantitative threshold not available in provided materials. | CP-2A-DP-002 | Reassess FCF durability, cash uses and refinancing capacity. | 10-Q pp. 16, 20. [C2, C16] | Adjusted EBITDA is not liquidity; period comparability and add-backs require review. |
| CP-2A-MON-003 | Operating cash flow, working capital and property/equipment purchases | Lagging | Qualitative: weaker operating cash flow or cash investment needs that reduce cash after fixed uses. Quantitative threshold not available in provided materials. | CP-2A-DP-003 | Update cash-conversion and accessible-liquidity analysis. | 10-Q pp. 4, 22. [C7, C8] | No seasonal bridge or current forecast supplied. |
| CP-2A-MON-004 | Cash balance and CEI revolver availability | Lagging | Qualitative: decline in accessible resources or evidence of increased reliance on revolver capacity. Quantitative threshold not available in provided materials. | CP-2A-DP-004 | Escalate liquidity review and request updated facility/cash detail. | 10-Q pp. 2, 10. [C9, C10] | June 30, 2026 balances are historical, not current as of analysis date. |
| CP-2A-MON-005 | Variable-rate borrowing and cash interest | Leading | Qualitative: rising cash interest or changes in variable-rate borrowing/hedging. Quantitative threshold not available in provided materials. | CP-2A-DP-005 | Update debt-service and refinancing sensitivity. | 10-Q pp. 7, 23. [C13, C25] | No sourced rate-shock threshold or complete current debt schedule supplied. |
| CP-2A-MON-006 | Scheduled debt maturities and refinancing announcements | Leading | Qualitative: refinancing delay, maturity funding uncertainty or amended maturity schedule. Quantitative threshold not available in provided materials. | CP-2A-DP-005 | Escalate CP-3C; reassess market access and liquidity pathway. | 10-Q p. 9. [C14] | No current market pricing or refinancing plan supplied. |
| CP-2A-MON-007 | Financial covenant calculations and compliance | Lagging | Qualitative: any reported covenant headroom decline, waiver request or non-compliance. Quantitative threshold not available in provided materials. | CP-2A-DP-006 | Obtain current compliance certificate and escalate CP-4A. | 10-Q p. 23. [C15] | June 30 compliance does not establish current or stressed headroom. |
| CP-2A-MON-008 | Merger status, approvals, end-date or consideration amendments | Leading | Qualitative: filed delay, failed condition, amended end date or termination disclosure; monitor only when disclosed. | CP-2A-DP-008 | Event-driven review of costs, disruption, liquidity implications and refinancing assumptions. | 10-Q pp. 5, 25. [C19, C20, C21] | Current post-Q2 transaction status is not established by delivered evidence. |

#### T2B.8 — Cross-Module Handoff Register

| Downstream Module | Handoff Item | Why It Matters | Required Consumer Action | Source / Pathway Link | Limitation |
|---|---|---|---|---|---|
| CP-2D | Las Vegas demand-to-cash path; working-capital and capex pressure; debt service and lease uses; accessible liquidity. | These cash uses determine whether operating weakness becomes a liquidity pinch. | Build a current cash bridge; separate dated Q2 estimates from current facts; test working capital, capex, rent, interest and revolver access. | CP-2A-DP-001/003/004; [C7, C8, C9, C10, C11, C12] | No current October cash bridge or downside forecast. |
| CP-2E | $6.0 billion variable-rate borrowing and absence of cash-flow hedges. | Rate changes can transmit directly into cash interest and FCF. | Quantify with sourced current debt and rate inputs; include only evidenced FX/commodity/wage exposures. | CP-2A-DP-005; [C13, C25] | No specified rate stress, hedge schedule or quantified non-rate mismatch. |
| CP-3 | Primary fragility is Las Vegas demand; fastest path is visitation/table-games weakness to EBITDA and cash pressure; monitor liquidity and maturities. | Credit deterioration can affect relative value and market access before a breach. | Combine with dated market observations, spread/price evidence and a supported monitoring signal; do not infer a valuation label. | CP-2A-DP-001/005; [C2, C3, C14] | No current market prices, spreads or curve in the delivered evidence. |
| CP-3A | Security/recovery risk remains open; current collateral, guarantee, lien and priority perimeter is not verified. | Structural protection affects LGD and security selection. | Review current executed documents, collateral evidence and intercreditor position before recovery conclusions. | CP-2A-DP-007 | No current perfection, collateral value or recovery inputs. |
| CP-3B | Downside-budget caution: Las Vegas exposure, cash-use competition, maturity/rate sensitivity and sparse dated catalysts. | Position sizing and portfolio liquidity depend on downside severity and timing. | Treat as monitoring/sizing caution only; integrate portfolio-specific limits and current market liquidity. | CP-2A-DP-001/004/005; [C2, C11, C12, C13, C14] | Portfolio holdings, correlation and issue liquidity are not supplied. |
| CP-3C | Refinancing inflection: scheduled maturities, variable-rate burden, liquidity uses and conditional merger milestones. | Market access can deteriorate as FCF and debt-service capacity weaken. | Reconcile current debt and lease documents; assess refinancing options and LME vulnerability from supplied evidence. | CP-2A-DP-005/008; [C11, C12, C13, C14, C19] | No current funding plan, market data or complete operative documents. |
| CP-4A | Potential covenant transmission; reported June 30 compliance is not current headroom. | Covenant capacity depends on definitions, current usage and calculation inputs. | Obtain current agreement, compliance certificate, EBITDA definition and basket usage; calculate only from validated inputs. | CP-2A-DP-006; [C15] | Do not infer capacity or headroom from the reported compliance statement. |
| CP-5A | Material gaps, inference-heavy pathways, stale dated liquidity estimates and debt-basis distinctions. | QA review must preserve lineage and prevent unsupported calculations. | Audit claim lineage, source limitations, period alignment, definitions and missing inputs; retain Restricted posture. | T2B.1, T2B.6, T2B.9; [C11, C12, C16, C23, C24] | No host validator findings are claimed here. |
| CP-5 | Key claims: Las Vegas operating decline, Regional offset, cash-flow and liquidity facts, variable-rate exposure and merger dates. | Evidence traceability is necessary for downstream use and review. | Preserve source IDs, page locators, dated periods and fact/inference distinctions. | CP-2A-DP-001–009; [C2, C4, C7, C9, C13, C19] | Upstream citations are not used as evidence; source evidence is cited directly. |
| CP-6/CP-6A | Restricted downside view, contrary evidence, top triggers and explicit source gaps. | Reviewers need a bounded conclusion and clear escalation conditions. | Treat as screening-only; monitor specified signals and require a linked, user-confirmed FULL_CREDIT_32 run for underwriting decisions. | CP-2A-DP-001/004/005/008/009; [C2, C4, C9, C13, C19, C20] | Not committee-ready; no rating, security or position recommendation. |

#### T2B.9 — Gaps Ledger

| Gap ID | Missing Data | Why It Matters | Affected Pathway / Calculation / Trigger | Consequence for Confidence | Required Follow-Up Source |
|---|---|---|---|---|---|
| CP-2A-GAP-001 | 2025 Form 10-K and complete annual operating/cash-flow history. | The Q2 filing directs readers to the annual report; period history and normalization cannot be fully tested. [C17] | DP-001–003; MON-001–003; sensitivity analysis. | High | Filed 2025 Form 10-K and subsequent complete issuer filings. |
| CP-2A-GAP-002 | Current issuer forecast, downside case and integrated cash-flow/liquidity bridge. | Without sourced assumptions, FCF, runway, liquidity pinch and refinancing failure cannot be quantified. | DP-003–005; MON-003–006. | High | Current issuer forecast, operating assumptions and cash-use schedules. |
| CP-2A-GAP-003 | Current executed credit-agreement updates, full controlling lease documents, current covenant certificate and usage. | Contract terms, headroom, triggers, debt-service priority and lease constraints may affect creditor outcomes. | DP-004–007; MON-004/007; covenant and liquidity calculations. | High | Current executed credit and lease packages, compliance certificate and basket/usage schedules. |
| CP-2A-GAP-004 | Current debt-market observations, spreads, curve, trading liquidity and comparable evidence. | Refinancing capacity and relative value cannot be assessed from financial filings alone. | DP-005; MON-006; CP-3 handoff. | Medium | Dated issue-level market source and definition-matched comparables. |
| CP-2A-GAP-005 | Current merger status; dates for any shareholder or regulatory milestones not specified in delivered evidence. | Event probability and timing cannot be established from the Q2 filing. | DP-008; T5.2–T5.7; MON-008. | High | Subsequent issuer filing, definitive proxy and dated regulatory/transaction disclosures. |
| CP-2A-GAP-006 | Current collateral/perfection map, guarantee perimeter, intercreditor documents and recovery inputs. | LGD, structural subordination and security selection are not assessable. | DP-007 and CP-3A handoff. | High | Current executed security documents, entity chart, collateral records and recovery data. |
| CP-2A-GAP-007 | Property-level visitation, pricing, customer concentration, working-capital seasonality and maintenance-capex split. | The first break can be identified directionally, but operational resilience and quantified sensitivity remain uncertain. | DP-001–003; MON-001/003. | Medium | Property/segment operating data, customer metrics and capex/working-capital schedules. |

### Overall downside pathway view

Overall, the primary fragility for Caesars Entertainment, Inc. is Las Vegas revenue demand. The fastest transmission path is weaker city-wide leisure visitation and table-games activity → lower hotel/non-gaming and gaming revenue → lower segment EBITDA and cash generation → reduced FCF after working capital, capex, debt service and rent → weaker liquidity and refinancing flexibility if sustained. [C2, C3, C7, C8, C11, C12, C14] The main monitoring signal is subsequent Las Vegas visitation, table-games activity and segment EBITDA, accompanied by cash flow and accessible liquidity. Regional growth, reported June 30 cash/revolver capacity and positive operating cash flow are the strongest counterarguments; sustained stabilization and cash generation after all fixed uses would make them win. [C4, C7, C9, C10] Current forecast, covenant headroom, market access and recovery inputs remain gaps. No quantitative stress threshold or failure point is supported.

**Limited:** CP-2A Completed with Limitations. Primary Fragility: Las Vegas revenue demand. Fastest Downside Path: leisure visitation/table-games weakness → lower revenue and EBITDA → weaker cash generation after fixed uses → liquidity/refinancing pressure, directional only. Monitoring Signal: Las Vegas operating data and cash/liquidity updates; quantitative threshold not available in provided materials.

#### T5.1 — Event Source Register

| Event ID | Source Document | Event Description | Event Category | Date/Range | Evidence Quality | Source Reliability |
|---|---|---|---|---|---|---|
| CZR-EVT-001 | Caesars Q2 2026 Form 10-Q, Note 1, merger terms | Merger agreement states an initial end date of May 27, 2027, with conditional extensions. [C19] | Corporate | 2027-05-27; conditional extensions to 2027-08-27 and 2027-11-27 | Filed disclosure; date expressly stated | Primary issuer filing; source-supported, but current status not established. |
| CZR-EVT-002 | Caesars Q2 2026 Form 10-Q, Note 1, merger consideration | If closing has not occurred as of June 26, 2027, the agreement provides a per-day ticking-fee mechanism beginning after that date. [C18] | Corporate | 2027-06-26 and subsequent disclosed period | Filed disclosure; date and conditional term expressly stated | Primary issuer filing; current status not established. |

#### T5.2 — Catalyst Calendar

| Date/Window | Event Description | Event Category | Credit Relevance Summary | Source |
|---|---|---|---|---|
| 2027-05-27 | Initial merger end date; agreement provides conditional extensions if specified conditions remain outstanding. [C19] | Corporate | A delay or failure could prolong transaction uncertainty; filing identifies potential operating, cost and financial effects. | 10-Q, Note 1, p. 5. [C19, C20, C21] |
| 2027-06-26 | Ticking-fee date if merger closing has not occurred; fee mechanism then applies as described in the agreement. [C18] | Corporate | May change transaction cash economics and signals continuing completion delay; actual outcome and amount are not forecast. | 10-Q, Note 1, p. 5. [C18] |

#### T5.3 — Event Risk Register

| Event ID | Description | Probability | Credit Impact Channel(s) | Impact Severity | Affected Metrics | Risk Direction | Source |
|---|---|---|---|---|---|---|---|
| CZR-EVT-001 | Merger may remain incomplete at the initial end date; conditional extensions are disclosed. [C19, C20] | Unknown | PD; liquidity; refinancing; downgrade/monitoring | High | Transaction costs, operating cash flow, management attention, refinancing assumptions | Uncertain | 10-Q pp. 5, 25. [C19, C20, C21] |
| CZR-EVT-002 | Ticking-fee date applies conditionally if closing has not occurred. [C18] | Unknown | Liquidity; monitoring; transaction timing | Medium | Transaction consideration timing and cash implications | Uncertain | 10-Q p. 5. [C18] |

#### T5.4 — Probability / Impact Matrix

| Event ID | Description | Probability | Impact | P/I Classification |
|---|---|---|---|---|
| CZR-EVT-001 | Merger end date and conditional extensions | Unknown | High | Unknown / High — material conditional event; probability not established by delivered sources. |
| CZR-EVT-002 | Conditional ticking-fee date | Unknown | Medium | Unknown / Medium — depends on transaction status; no outcome probability assigned. |

#### T5.5 — Monitoring Priority Table

| Event ID | Description | Priority | Monitoring Frequency | Trigger Condition | Responsible Module |
|---|---|---|---|---|---|
| CZR-EVT-001 | Merger end date, extensions and completion conditions | High | Event-driven; review each subsequent filed transaction update | Filed evidence of delay, condition failure, end-date amendment or termination | CP-3C; CP-6/CP-6A |
| CZR-EVT-002 | Ticking-fee date and conditional consideration change | Medium | Event-driven; review transaction disclosures before and after stated date | Filed evidence that closing has not occurred by the stated date or that consideration terms change | CP-3C; CP-6/CP-6A |

#### T5.6 — Watchlist Handoff Register

| Event ID | Description | Priority | Receiving Module | Handoff Content | Timing | Rationale |
|---|---|---|---|---|---|---|
| CZR-EVT-001 | Merger end date and possible conditional extensions | High | CP-3C | Preserve stated dates, conditions and possible operating/cost consequences; do not infer completion or financing. [C19, C20, C21] | Event-driven and at each new filing | Transaction delay or failure could alter operating uncertainty and refinancing assumptions. |
| CZR-EVT-001 | Merger completion conditions and current-status gap | High | CP-5A | Verify that no conclusion treats Q2 status as current; retain missing-status limitation. [C20] | Before downstream clearance and on each update | Prevent stale event information from being represented as current. |
| CZR-EVT-002 | Conditional ticking-fee date | Medium | CP-6/CP-6A | Monitor only if subsequent evidence confirms the condition; assess cash implications from current documents. [C18] | At stated date or new transaction filing | The term is conditional; no amount or outcome is assumed. |

#### T5.7 — Gaps & Limitations Ledger

| Gap Description | Affected Section | Downstream Impact | Severity | Recommended Action |
|---|---|---|---|---|
| Current merger status after the Q2 filing is not established in the delivered evidence. [C20] | T5.1–T5.6; Analysis | Event probability, transaction timing and operating implications remain uncertain. | High | Obtain the latest filed transaction-status disclosure and update event classification. |
| Shareholder meeting and regulatory milestone dates are not stated in delivered evidence. [C20] | T5.2–T5.5 | No dated calendar entry can be assigned; probability and timing remain unknown. | Medium | Add only dates expressly stated in subsequent issuer or regulatory disclosures. |
| Conditional end-date extensions include a date beyond the 12-month horizon. [C19] | T5.2, T5.7 | November 2027 is outside the October 2, 2026–October 2, 2027 calendar horizon. | Low | Retain as a disclosed extension in the event source register and add to a later calendar if still material. |
| Q2 event disclosure does not provide a current cash or transaction-cost forecast. [C11, C12, C21] | Catalyst view; T5.3–T5.6 | Credit impact cannot be quantified or assigned a current liquidity consequence. | Medium | Obtain current forecast and transaction-cost disclosure before quantitative assessment. |

<!-- table-id: cp2b.cp_model_catalysts -->
| rank | event_date_or_window | event | credit_relevance | status | source_id | source_locator | as_of |
|---:|---|---|---|---|---|---|---|
| 1 | 2027-05-27; conditional extensions to 2027-08-27 and 2027-11-27 | Merger initial end date and conditional extensions | Delay or failure may prolong transaction uncertainty and potential operating/cost effects. [C19, C20, C21] | READY | 1ae6b04b-413a-4f14-b5da-362701a558fb | p. 5, Note 1, “Termination Fees; End Date” | 2026-10-02 |
| 2 | 2027-06-26 | Conditional ticking-fee date if closing has not occurred | May affect transaction cash economics; condition and current status require monitoring. [C18] | READY | 1ae6b04b-413a-4f14-b5da-362701a558fb | p. 5, Note 1, “Merger Consideration” | 2026-10-02 |

#### Overall Catalyst View

The defined catalyst horizon is 12 months from 2026-10-02 through 2027-10-02. Two source-supported future dated events are recorded: the initial merger end date and conditional ticking-fee date. Both have Unknown probability; the end-date event has High impact and the ticking-fee event Medium impact. The net catalyst bias is Uncertain because the transaction is conditional and no current post-Q2 status is supplied. Monitor subsequent filings and do not infer dates for undated approval or shareholder milestones. Based on available evidence, the following 2 events represent the most material forward-looking credit catalysts for Caesars Entertainment, Inc. within the 12-month monitoring period.

## Evidence Trace

| Claim | Citation | Document | Page |
|---|---|---|---:|
| Business model and diversified gaming/hospitality operations | [C1, C6, C26] | Caesars Entertainment, Inc. Form 10-Q | 17–18 |
| Las Vegas demand and EBITDA weakness | [C2, C3] | Caesars Entertainment, Inc. Form 10-Q | 20 |
| Regional offset | [C4] | Caesars Entertainment, Inc. Form 10-Q | 20 |
| Digital hold and promotional-cost sensitivity | [C5] | Caesars Entertainment, Inc. Form 10-Q | 21 |
| Operating cash flow and property/equipment purchases | [C7, C8] | Caesars Entertainment, Inc. Form 10-Q | 4, 22 |
| Cash and CEI revolver capacity | [C9, C10] | Caesars Entertainment, Inc. Form 10-Q | 2, 10 |
| Dated remaining-2026 debt-service and lease estimates | [C11, C12] | Caesars Entertainment, Inc. Form 10-Q | 22 |
| Variable-rate borrowings and no cash-flow hedges | [C13, C25] | Caesars Entertainment, Inc. Form 10-Q | 7, 23 |
| Debt maturity schedule and reported covenant compliance | [C14, C15] | Caesars Entertainment, Inc. Form 10-Q | 9, 23 |
| Adjusted EBITDA is not a liquidity measure | [C16] | Caesars Entertainment, Inc. Form 10-Q | 16 |
| Customer contract liability descriptions | [C17] | Caesars Entertainment, Inc. Form 10-Q | 11 |
| Merger end dates, ticking-fee condition and closing conditions | [C18, C19, C20] | Caesars Entertainment, Inc. Form 10-Q | 5 |
| Merger failure/disruption risk | [C21] | Caesars Entertainment, Inc. Form 10-Q | 25 |
| Annual filing reference, debt basis and capex estimate | [C17, C23, C24] | Caesars Entertainment, Inc. Form 10-Q | 5, 9, 22 |
| Issuer-defined net debt basis | [C24] | Caesars Q2 2026 earnings release | 2 |

## Source Registry

| Source ID | Source | Locator / use | Limitation |
|---|---|---|---|
| 1ae6b04b-413a-4f14-b5da-362701a558fb | Caesars Entertainment, Inc. Form 10-Q for quarter ended June 30, 2026 | Primary source for operating, cash-flow, debt, liquidity, lease, covenant and merger disclosures. Pages 2–25 used; claim locators in Evidence Trace. [C1, C2, C7, C9, C14, C19] | Interim-period evidence; referenced 2025 Form 10-K and current follow-up transaction/financial evidence not delivered. [C17] |
| 4edecdd2-6ed8-429e-902c-eb92822cd767 | Caesars Entertainment, Inc. Q2 2026 earnings release | Supplemental issuer result and net-debt presentation, p. 2. [C24] | Non-GAAP/issuer-defined presentation; not substituted for balance-sheet carrying-value debt. [C16, C23, C24] |
| b24b47d6-6bfd-4248-b660-e867409dd303 | Incremental Assumption Agreement No. 3 and conformed credit agreement | Executed 2024 financing document; contextual source for the dated agreement perimeter. | Not a current covenant calculation or evidence of amendments after the conformed date. |
| Accepted CP-0 handoff | Same-run CP-0 SourceReadiness artifact | Identity, source-readiness and limitation context only. | Not evidence and not cited. |
| Accepted CP-L10 handoff | Same-run CP-L10 LiteFinancialChangeScreen artifact | Screening-only scope and upgrade context. | Not a FULL baseline and not cited as source evidence. |

## Gaps & Conflicts

- **CP-2A-GAP-001 — Annual and comparable history:** the filing refers to the 2025 Form 10-K, which is absent from the delivered evidence. This limits trend and normalization work. [C17]
- **CP-2A-GAP-002 — Forecast and liquidity:** no current issuer forecast, sourced downside case or integrated cash bridge is delivered. Q2 estimates for the remainder of 2026 are dated and are not represented as current October estimates. [C11, C12]
- **CP-2A-GAP-003 — Debt definition/basis:** the 10-Q debt note presents face and book-value columns; the earnings release presents aggregate indebtedness and its issuer-defined net-debt measure. These are distinct presentations. Any future leverage analysis must use the prescribed balance-sheet carrying-value basis and retain the distinct source presentations rather than silently substituting them. [C23, C24]
- **CP-2A-GAP-004 — Current legal and lease documents:** the evidence includes a 2024 conformed credit-agreement source and Q2 lease disclosures, but does not establish a complete current operative agreement/lease package or current usage. Covenant capacity, leakage, collateral and recovery are not inferred.
- **CP-2A-GAP-005 — Market and peer evidence:** no dated price/spread/curve, current trading liquidity or definition-matched peer stress evidence is delivered. Relative value and market-access conclusions remain unassessed.
- **CP-2A-GAP-006 — Merger status:** the Q2 filing describes conditional terms and dates; current completion status is not established. [C19, C20]
- **Subsequent event:** the Q2 filing reports the Alberta mobile sports betting and iGaming launch on July 13, 2026, after the June 30 reporting date. It is a subsequent event, not a Q2-period result. No operating impact is quantified in this handoff.
- **Counterargument:** Regional growth, reported June 30 liquidity and positive six-month operating cash flow support resilience. Sustained Las Vegas stabilization and cash generation after capex, rent and debt service would make that evidence win; the current evidence does not provide the subsequent periods or forecast required to establish it. [C4, C7, C9, C10, C11, C12]

## QA Validation

| Check | Result | Record |
|---|---|---|
| Identity and filename | Self-check complete | Filename derived as `CZR_CP-2A_20261002.md`; issuer, module, run, period and analysis date match the host-owned front matter. |
| Required headings and front matter | Self-check complete | Six H2 headings appear once and in required order; only permitted model-authored front-matter fields were added. |
| Upstream re-anchor and LITE boundary | Restricted | Accepted same-run CP-0 and CP-L10 identity/period retained; upstream handoffs are context, not evidence. LITE screening does not satisfy this FULL method. |
| CP-2A registers | Self-check complete | T2B.1–T2B.9 present with required columns; pathway, monitoring and gap IDs follow required formats. |
| CP-2B registers | Self-check complete | T5.1–T5.7 present with required columns, event categories and ordinal probability/impact labels; calendar dates are explicitly disclosed dates only. |
| CP-MODEL interface | Self-check complete | `cp2b.cp_model_catalysts` emitted with two uniquely ranked READY rows, source IDs, locators and ISO as-of dates. |
| Causal chain and sensitivity discipline | Restricted | Supported operating-to-cash and creditor vectors are stated; unsupported stress magnitudes, headroom, runway and recovery are not inferred. |
| Citation discipline | Self-check complete | Citation excerpts are drawn from the delivered evidence; Markdown claims reference only citation markers. |
| Overall view and counterargument | Self-check complete | Synthesis adds no new data; strongest supported contrary evidence and conditions that would change conviction are stated. |
| Host validation and register completeness | Not run here | Host vendor validation and completeness checks follow this answer; no host findings or exit status are claimed. |