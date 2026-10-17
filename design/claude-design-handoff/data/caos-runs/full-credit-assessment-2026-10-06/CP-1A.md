---
module_id: "CP-1A"
module_name: "BusinessTransactionFactPack"
issuer_id: "CZR"
issuer_name: "Caesars Entertainment, Inc."
run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
reporting_period: "Q2 2026"
analysis_date: "2026-10-02"
credit_os_run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
credit_os_profile_id: "FULL_CREDIT_32"
credit_os_selection_id: "FULL_CREDIT_ASSESSMENT"
credit_os_authority_bundle_sha256: "97106f1959788ff92db59c67f8619aa8b28f55050ac9defeef5b3766abb8a4a0"
credit_os_attempt_id: "ATT-CP-1A-2804564680220523"
credit_os_route_node_id: "RN-FULL_CREDIT_32-FULL_CREDIT_ASSESSMENT-03-CP-1A"
credit_os_invocation_sha256: "6487bce7a41778cd8ef2691fe0f6ee541e13233af3354ab14942d1615164e881"
upstream_artifacts_used:
  - module_id: "CP-0"
    run_id: "COS-20261006T152956Z-6f30c70b1e3a4d1ab488229837b87cc7"
    period: "Q2 2026"
    sha256: "e382167c9231e5002c2e545429ef1172d7697e3de7db3eb794331112e433d1f9"
confidence_score: 57
confidence_band: "Low"
qa_status: "Restricted"
committee_status: "Requires More Work"
limitation_flags:
  - SOURCE_LIMITED_NOT_COMMITTEE_READY
  - NO_POST_Q2_2026_FINANCIALS
  - NO_COMPLETE_CURRENT_CREDIT_AGREEMENT_OR_SECURITY_PACKAGE
validation_warnings:
  - FULL_UNDERWRITING_SOURCE_SET_NOT_RETAINED
downstream_consumers: [CP-2, CP-2C, CP-MODEL]
---

## Audit Summary

Canonical handoff filename: `CZR_CP-1A_20261002.md`. Status: **Completed with Limitations**; `qa_status: Restricted`; committee status: **Requires More Work**. The accepted CP-0 artifact for this issuer, run and period is present and has matching lineage; its source-readiness status is READY_WITH_LIMITATIONS, not a credit conclusion. [C6] This pack uses the supplied FY2025 10-K, Q2 2026 10-Q, merger agreement and 8-K. The Q2 filing is the latest financial report supplied and covers June 30, 2026, not the October 2 analysis date. [C6] The merger remained pending in the Q2 disclosure. [C27] Important gaps include the complete current credit agreement and security package, post-June financials, full merger financing materials, current ownership/control detail and lender reporting. Accordingly, the pack does not establish current covenant headroom, transaction closing probability, sponsor willingness or complete debt capacity.

## Analysis

### Analytical read-through

Caesars is a public gaming and hospitality company with material casino, hotel, food-and-beverage and digital wagering operations. It has signed a cash merger agreement with Fertitta Gaming Holdco, LLC: eligible common shares receive $31.00 per share, subject to a conditional ticking fee if closing has not occurred by June 26, 2027. [C1, C2] The deal is subject to stockholder and regulatory conditions and was still pending in the June 30 filing. [C25, C27] Operating performance is diversified by property and business line, but is exposed to gaming volumes and hold, discretionary travel, labor, taxes, regulation and substantial debt and lease commitments. H1 2026 revenue rose to $5.863 billion from $5.701 billion, while Adjusted EBITDA was $1.807 billion versus $1.839 billion. [C6, C16] The creditor consequence is that transaction timing and ongoing operating cash generation both matter; neither closing nor financing terms should be treated as certain or completed.

**Decision drivers.** (1) The signed transaction changes the ownership path but remains conditional; the agreement provides termination rights and fees, not a completed acquisition. (2) Q2 cash and debt measures are material, and debt face, debt book value and lease financing obligations must remain distinct. [C7, C9, C26] (3) Historical growth includes acquisitions and asset purchases, while the sources do not provide a complete acquisition funding or pro forma leverage history. [C17, C18, C19]

The strongest counterweight to transaction risk is the documented financing commitment and Parent Guarantor guarantee of Parent and Merger Sub obligations; however, the complete commitment materials are not included here, and funding is not a closing condition. [C28] That evidence would become more decision-useful with the executed commitment package, current financing status, current liquidity/debt schedule and later-period results. Until then, treat funding availability and completion as unverified conditions, not as an assumed source of repayment.

### Business and operating model

Caesars owns, leases, manages or brands domestic properties, operates digital wagering in multiple jurisdictions and generates revenue from gaming and non-gaming services. [C11] FY2025 net revenue was $11.486 billion; casino was $6.617 billion, food and beverage $1.714 billion, hotel $1.945 billion and other $1.210 billion. [C12, C13, C14, C15] These are reported revenue categories, not normalized recurring cash flow. Gaming revenue depends on customer volume and realized hold; non-gaming results depend on hotel occupancy, room rate and visitation. H1 2026 Adjusted EBITDA was $1.807 billion, compared with $1.839 billion in H1 2025. [C16] For creditors, these drivers make segment-level visitation, hold, labor and gaming taxes important early-warning indicators; results from one period should not be extrapolated without current data.

### Transaction and ownership view

The agreement provides for Empire Merger Sub to merge into Caesars, with Caesars surviving as a wholly owned subsidiary of Parent. Eligible shares receive cash consideration; designated rollover shares are treated separately. [C1, C2] Recreational Enterprises, Inc. was reported as owning approximately 5% of the outstanding common stock and agreed to roll a portion of its equity; the exact final rollover amount can be reduced under its rollover agreement. [C3] The public filings describe Parent as Fertitta Gaming Holdco, LLC and identify Landry’s Fertitta, LLC as guarantor for Section 9.14; Hospitality Headquarters, Inc. joins only for Section 9.14(j). [C1]

The agreement sets a $200 million Company Termination Fee generally, with specified $100 million cases, and a $450 million Reverse Termination Fee under specified regulatory/end-date circumstances. [C4, C5] Parent Guarantor guarantees Parent and Merger Sub obligations, but that guarantee is not evidence of an equity contribution or a separate sponsor commitment beyond its terms. [C28] The complete disclosure schedules, financing commitment and post-close capitalization are not supplied. Therefore, post-close ownership percentages beyond the stated wholly owned subsidiary structure, rollover economics, financing sources and pro forma leverage are not established.

### Financial and credit translation

At June 30, 2026, reported cash and cash equivalents were $965 million. [C7] The debt note reports total debt of $11.807 billion face value and $11.705 billion book value; the balance sheet separately reports current debt and long-term debt, and financing obligations include VICI/GLPI lease arrangements. [C9, C26] These presentations must not be silently combined: see conflict log CF-1. The 10-Q reports total cash/revolver capacity of $2.928 billion after stated commitments and reserves; this is a dated liquidity snapshot, not October availability. [C10] H1 operating cash flow was $675 million and cash capital expenditures were $335 million. [C8, C29] Debt service, lease payments and capital requirements absorb cash otherwise available for debt reduction or liquidity preservation; any deterioration in gaming performance or hold can therefore transmit to weaker FCF and refinancing capacity.

### Governance view

The available evidence supports a **Medium / incomplete-information governance and sponsor-risk view**, not a conclusion about sponsor reputation or willingness. The public issuer has documented financial reporting, annual audit and interim disclosure, while the transaction agreement provides a defined merger process and a Parent Guarantor guarantee. [C1, C23, C28] Countervailing facts include historical share repurchases, acquisition activity and a related-party land lease; the supplied evidence does not establish that these represent sponsor extraction or distressed creditor-adverse conduct. [C17, C20, C22] The evidence does not establish sponsor fund vintage, full current ownership, post-close equity contribution, lender reporting package, complete legal capacity or a full history of amendments/LME activity. Those gaps limit governance scoring and require monitoring, not an adverse assumption.

### Downside path and monitoring

If transaction approvals or stockholder approval are delayed or fail, the first observable break would be continued uncertainty and transaction execution costs; the issuer disclosed $10 million of merger-related costs for Q2 and H1 2026. [C27] Prolonged delay can keep management and resources focused on the deal, while market or operating deterioration could reduce cash generation. The next transmission is lower retained operating cash after debt service, lease payments and capital needs, increasing reliance on revolver liquidity or refinancing. The observable triggers are updated gaming/visitation/hold, operating cash flow, cash and revolver availability, debt and lease balances, transaction status, regulatory conditions and reported covenant compliance. A material counterargument is that Q2 covenant compliance was reported and the company reported a substantial liquidity pool at June 30; these historical snapshots would reduce near-term concern if confirmed in later-period reporting and accompanied by adequate operating performance. [C10, C24]

### Analytical appendix — complete canonical registers

#### source_classification

| Source ID | Source class | Quality | Use | Limitation |
|---|---|---|---|---|
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Filed interim financial report (Form 10-Q) | High — primary filing | Q2 2026 financials, debt, liquidity, transaction update and operating data [C6, C7, C8, C9, C10, C16, C27] | Unaudited; data through June 30, 2026 only; supplied text does not include subsequent-period financials. |
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Filed annual financial report (Form 10-K) | High — primary filing; audited statements | FY2025 business, revenue categories, historical acquisitions, debt/lease context, repurchases and related-party disclosure [C11, C12, C13, C14, C15, C17, C20, C22, C23, C26] | Historical baseline; no post-year-end current financial position beyond supplied Q2 report. |
| 80a091bf-ceb5-4bb8-9006-297fd19a762e | Executed Agreement and Plan of Merger | High — primary transaction document | Merger mechanics, consideration, termination fees, financing cooperation and guarantee terms [C1, C2, C4, C28] | Disclosure schedules and complete financing commitment materials are not included in the delivered source set. |
| 5e8a2604-12ea-471a-bbad-4e77b04c3186 | Filed Form 8-K and transaction description | High — filed primary summary | Transaction summary, rollover holder and reverse termination fee [C3, C5] | Summary is not a substitute for the full agreement; some schedules omitted. |

#### transaction_summary

| Transaction | Status | Credit relevance | Source |
|---|---|---|---|
| Merger of Empire Merger Sub into Caesars; Caesars survives as Parent’s wholly owned subsidiary | Signed May 27, 2026; pending as of June 30, 2026 | Changes prospective ownership, financing and capital structure; do not blend the proposed transaction into Q2 historical results. [C1, C27] | Agreement and 10-Q, pp. 5 and 6 [C1, C27] |
| Cash consideration | $31.00 per eligible share plus a conditional per-share ticking fee if closing has not occurred as of June 26, 2027 | Closing delay increases aggregate cash consideration after the defined date; actual amount depends on closing date. [C2] | Merger agreement, p. 9 [C2] |
| Rollover / support holder | Recreational Enterprises, Inc. reported to own approximately 5% and to roll a portion; Exhibit A lists 5,000,000 shares, subject to reduction under the Rollover Agreement | Rollover reduces cash consideration for designated shares but does not establish final ownership or final equity contribution. [C3] | 8-K, p. 1; agreement, Exhibit A [C3] |
| Conditions | Company stockholder approval, applicable HSR waiting period and required gaming approvals are among the conditions | Approval and regulatory timing are transaction dependencies; failure can delay or prevent closing. [C25] | 10-Q, p. 25 [C25] |
| End date | Initial date May 27, 2027; extensions to August 27 and November 27, 2027 in specified regulatory circumstances | Longer delay extends period of uncertainty and may affect liquidity, execution and transaction cost. | Agreement, §§8.1–8.3; 8-K, p. 2 [C4, C5] |
| Company Termination Fee | Generally $200 million; $100 million for specified go-shop/Excluded Party cases | Potential termination cash obligation is contingent on contract-defined events. [C4] | Agreement, p. 25 [C4] |
| Reverse Termination Fee | $450 million under specified antitrust/gaming regulatory or end-date circumstances, subject to agreement terms | Potential Parent payment is a contractual remedy, not current liquidity available to Caesars. [C5] | 8-K, p. 2 [C5] |
| Financing / guarantee | Parent delivered debt commitment letters; Parent Guarantor guarantees Parent and Merger Sub obligations; financing is not a closing condition | Commitment availability, funded amount and final capital structure are not verified from the full financing package. [C28] | 8-K, p. 2; agreement, §9.14 [C28] |

#### company_description

| Issuer | Business description | Country | Sector |
|---|---|---|---|
| Caesars Entertainment, Inc. | U.S. gaming and hospitality issuer operating casino properties, hotels, food and beverage, retail, entertainment and digital sports betting/iGaming; owns, leases, brands or manages 52 domestic properties as of FY2025. [C11] | United States; Delaware corporation. [C1] | Casinos, gaming, hospitality and digital wagering. [C11] |

#### revenue_business_mix

| Business line | Revenue mix | Period | Status | Limitation |
|---|---:|---|---|---|
| Casino | $6.617bn | FY2025 | Reported revenue; largest listed category. [C12] | Includes land-based and digital gaming reporting as presented; not a normalized cash-flow measure. |
| Food and beverage | $1.714bn | FY2025 | Reported revenue. [C13] | Revenue category; margin/cash conversion not provided in this row. |
| Hotel | $1.945bn | FY2025 | Reported revenue. [C14] | Sensitive to occupancy, room rate and visitation; no customer-level concentration data supplied. |
| Other | $1.210bn | FY2025 | Reported revenue. [C15] | Aggregated category includes multiple activities; composition limits precision. |
| Consolidated net revenue | $11.486bn | FY2025 | Reported total. [C12] | 2025 baseline; not a forecast. |
| Consolidated net revenue | $5.863bn vs. $5.701bn prior-year period | Six months ended June 30, 2026 vs. 2025 | Reported interim amount. [C6] | Interim and unaudited; no period after June 30 supplied. |

#### ownership_register

| Owner / class | Control | Economic interest | Credit relevance | Source |
|---|---|---|---|---|
| Public shareholders of Caesars | Caesars was a Nasdaq-listed Delaware corporation before the proposed merger; 203,720,372 shares outstanding as of July 23, 2026. | Public share ownership; complete beneficial-holder breakdown not supplied in these materials. | Public ownership changes to Parent control only if merger closes; do not assume close or infer unreported voting concentration. | Q2 10-Q cover, p. 1; merger agreement [C1] |
| Fertitta Gaming Holdco, LLC | Merger Parent; proposed direct owner of surviving Caesars subsidiary following closing. | Post-close ownership percentage at the ultimate Parent level and financing equity contribution not specified in supplied materials. | Parent ownership would shift control and capital structure; pro forma ownership and leverage need full financing documents. | Agreement preamble and §2.1 [C1] |
| Recreational Enterprises, Inc. | Stockholder; entered into support/rollover arrangements as described in the 8-K and agreement. | Approximately 5% of outstanding common stock reported; portion to roll; Exhibit A states 5,000,000 shares unless reduced. [C3] | Rollover preserves some continuing equity interest, but final share count and ownership depend on agreements. | 8-K, p. 1; agreement, Exhibit A [C3] |
| Landry’s Fertitta, LLC | Parent Guarantor solely for §9.14. | Ultimate economic interest and resources supporting the guarantee are not quantified in supplied sources. | Contractual guarantee is relevant to Parent obligations but does not evidence funded support or establish ability to pay. | Agreement, preamble and §9.14 [C28] |
| Hospitality Headquarters, Inc. | Party solely for §9.14(j). | Ownership and asset values are not fully provided in the main agreement text supplied. | Limited covenant role; do not treat as a general guarantor. | Agreement, preamble and §9.14(j) [C1] |

#### operating_model

| Operating driver | Measure | Period | Status | Credit relevance |
|---|---:|---|---|---|
| Portfolio footprint | 52 domestic properties in 18 states | Dec. 31, 2025 | Reported. [C11] | Multi-property operations diversify geography, while property-level competition and regulatory rules remain local. |
| Consolidated net revenue | $11.486bn; $5.863bn H1 2026 vs. $5.701bn H1 2025 | FY2025; H1 2026/2025 | Reported. [C6, C12] | Revenue growth supports scale but does not ensure margin or cash-flow growth. |
| Adjusted EBITDA | $1.807bn H1 2026 vs. $1.839bn H1 2025 | Six months ended June 30 | Reported non-GAAP measure. [C16] | Decline despite revenue growth indicates cost/segment mix pressure; definition differs from GAAP cash flow. |
| Operating cash flow | $675m vs. $680m | Six months ended June 30, 2026/2025 | Reported. [C8] | Cash generation is the primary near-term debt-service source; slight decline and working-capital movements merit monitoring. |
| Cash capital expenditures | $335m vs. $453m | Six months ended June 30, 2026/2025 | Reported. [C29] | Lower spend supports near-term cash retention, but maintenance and growth needs continue. |
| Cash / debt | Cash $965m; debt table book value $11.705bn and face value $11.807bn | June 30, 2026 | Reported on different bases. [C7, C9] | High absolute debt and financing obligations constrain flexibility; do not use gross face as canonical carrying debt without labeling. |
| Liquidity | Total reported cash and revolver capacity $2.928bn after identified commitments/reserves | June 30, 2026 | Reported snapshot. [C10] | Supports near-term liquidity but is not updated to analysis date; revolver access remains subject to terms and availability. |
| Gaming volume / hold | Slot handle, table-games drop and hold, sportsbook/iGaming handle and hold reported by segment | Q2/H1 2026 | Reported operating KPIs. [C16] | Lower volume or hold can reduce gaming revenue quickly; monitor alongside taxes, promotions and labor. |
| Labor / regulation | Gaming taxes increased in certain states; Caesars operates in regulated gaming jurisdictions | Q2/H1 2026 and FY2025 context | Reported. [C16] | Higher taxes and labor costs reduce EBITDA conversion; licenses and gaming approvals affect operating continuity. |
| Customer deposits / contract liabilities | Customer deposits and other deferred revenue $545m at June 30, 2026 vs. $492m at year-end | H1 2026 | Reported liability balance. | Provides operating cash float but represents deposits, wagers and future-service obligations; a demand/refund shock could reverse cash benefit. |

#### events_timeline

| Date / window | Event | Credit relevance | Status | Source |
|---|---|---|---|---|
| 1973 | Founding of Eldorado Hotel Casino in Reno | Origin of operating platform; historical context only. [C30] | Historical | FY2025 10-K, p. 2 [C30] |
| 2014–2021 | Acquisitions listed include MTR, Isle of Capri, Tropicana, Caesars Entertainment Corporation and William Hill | Demonstrates material acquisition-led growth history; transaction-level funding and pro forma leverage are not supplied here. [C17] | Historical | FY2025 10-K, p. 2 [C17] |
| 2025 | Repurchased 9.606m shares for aggregate $229m | Cash returned through repurchases; funding source and impact on covenant capacity not established here. [C20] | Historical | FY2025 10-K, p. 23 [C20] |
| Mar. 3, 2026 | Caesars began operating Caesars Windsor under a 20-year operating agreement and purchased specified net assets; entered a 20-year lease. | Adds regional revenue and operating commitments; purchase/lease funding and pro forma returns not fully detailed. [C18] | Completed | Q2 10-Q, p. 6 [C18] |
| May 1, 2026 | Acquired remaining Grand Bazaar membership interest for about $66m, including $10m deferred consideration; accounted for as asset purchase. | Uses capital and adds assets; funding and return data not supplied. [C19] | Completed | Q2 10-Q, p. 18 [C19] |
| May 27, 2026 | Merger agreement executed with Fertitta Gaming Holdco, LLC and Merger Sub. | Transaction, financing, regulatory and governance dependency. [C1] | Pending as of June 30, 2026 [C27] | 8-K and Q2 10-Q [C1, C27] |
| June 30, 2026 | Latest financial reporting date in supplied company data. | Financial figures are stale relative to analysis date; do not treat as October-current. [C6] | Period-end | Q2 10-Q, cover and statements [C6] |
| H1 2026 | No share repurchases in the six months ended June 30; company said no repurchases expected at that time due to proposed merger. [C21] | Supports near-term cash retention; subsequent behavior remains unknown. | Reported through June 30 | Q2 10-Q, p. 13 [C21] |
| May 27, 2027; extensions to Nov. 27, 2027 | Initial end date and potential regulatory extensions under merger agreement. | Longer delay preserves transaction uncertainty and may extend execution-cost period. [C25] | Contractual future dates | Q2 10-Q, p. 25 [C25] |
| July 1, 2027 onward, if applicable | Ticking fee accrues at $0.007150 per share per day for days specified in agreement if closing has not occurred by June 26, 2027. | Delayed closing increases consideration; actual total depends on closing date. [C2] | Conditional future term | Agreement, definition of Per Share Ticking Fee [C2] |

#### credit_translation

| Evidence | Risk mechanic | Credit implication | Confidence | Limitation |
|---|---|---|---|---|
| Pending cash merger with conditional approvals and ticking fee; deal remained pending at June 30. [C1, C2, C25, C27] | Approval delay extends uncertainty and may increase consideration and transaction costs; failed close may trigger contract-defined fees. | Monitoring of transaction status, liquidity and management focus is required; no closing probability or funding assurance inferred. | Medium | Complete financing commitment package and post-June status absent. |
| H1 revenue rose but Adjusted EBITDA and operating cash flow were lower year over year. [C6, C8, C16] | Revenue growth without equivalent EBITDA/cash conversion can weaken retained cash available after fixed obligations. | FCF durability and debt-service capacity depend on segment margins, gaming hold, costs and working capital. | Medium | Interim period, non-GAAP EBITDA and no full-year trend beyond FY2025. |
| June liquidity reported at $2.928bn; cash $965m; debt table book value $11.705bn. [C7, C9, C10] | Large debt and lease commitments absorb cash; liquidity is dated and may change. | Current refinancing and liquidity assessment requires an updated cash/debt/revolver schedule and full debt terms. | Medium | Not an October 2 balance; debt basis reconciliation remains open. |
| Multi-year acquisition history and two 2026 asset/property transactions; funding and pro forma metrics are incomplete. [C17, C18, C19] | Acquisitions can consume cash, add lease/debt obligations or create integration and execution risk. | Monitor returns, funding mix and incremental fixed obligations; do not infer acquisition-driven leverage without transaction data. | Medium | Purchase financing, incremental EBITDA and integration outcomes not supplied. |
| FY2025 audited reporting and Q2 filing report covenant compliance at respective dates. [C23, C24] | Audited annual/interim reporting improves visibility, but compliance snapshots do not quantify current headroom. | Supports monitoring quality; covenant capacity remains Not Calculable from Provided Materials without current agreement and certificate. | Medium | No lender compliance certificate or current covenant calculation supplied. |
| Historical share repurchases, with none in H1 2026, and a disclosed small related-party lease. [C20, C21, C22] | Repurchases can reduce cash retained; related-party payments can create leakage, though this lease is disclosed and modest relative to issuer scale. | No documented evidence here of a dividend recap, LME or sponsor extraction; continue monitoring cash distributions and related-party terms. | Medium | Full distribution history, related-party schedule and current legal capacity not supplied. |

#### gaps_ledger

| Gap | Affected analysis | Severity | Action | Status |
|---|---|---|---|---|
| Complete current CEI Credit Agreement, schedules, baskets and current compliance certificate | Debt capacity, covenant headroom, transaction financing and CP-2/CP-2C | Material | Obtain complete conformed agreement and current lender compliance package; do not infer capacity. | Open |
| Current collateral, guarantee and intercreditor package | Security priority, recovery, legal capacity and creditor treatment | Material | Obtain executed security/intercreditor documents and current guarantor/collateral schedules. | Open |
| Financial information after June 30, 2026 | Current liquidity, performance, debt and transaction status | Material | Obtain next company filing and current cash/debt/revolver schedule. | Open |
| Full merger financing commitment, fee letters and schedules | Financing availability, equity/debt sources and pro forma capitalization | Material | Obtain complete executed commitment materials and current funding-status evidence. | Open |
| Current ownership and ultimate Parent capitalization | Ownership percentages, control and post-close economic interests | Material | Obtain ownership chart, rollover agreements and final capitalization table. | Open |
| Acquisition funding and pro forma EBITDA for Windsor, Grand Bazaar and prior major acquisitions | Capital allocation, integration and leverage history | Material | Obtain transaction purchase agreements, funding sources, incremental EBITDA and integration tracking. | Open |
| Complete shareholder distribution, related-party fee and sponsor-support history | Governance and extraction/support assessment | Material | Obtain shareholder distribution schedule, related-party register, sponsor fee schedule and support history. | Open |
| Detailed customer and counterparty concentration | Revenue durability and downside sensitivity | Minor | Obtain management/customer concentration data if material to underwriting. | Open |
| Subsequent-events disclosure after June 30, 2026 | Period accuracy and current-condition assessment | Material | Obtain subsequent filings and issuer updates through analysis date. | Open |

#### conflict_log

| Conflict | Sources | Materiality | Resolution | Downstream impact |
|---|---|---|---|---|
| Debt table distinguishes June 30 face value ($11.807bn) and book value ($11.705bn); balance sheet separately shows current portion ($114m) and long-term debt ($11.585bn), whose sum differs from the debt-note book value. | Q2 10-Q, pp. 2 and 9 [C7, C9] | Material | Preserve all figures and labels; do not silently reconcile the $6m difference. Use debt-note book value where explicitly described as book value and log the balance-sheet presentation difference for financial-module review. | Leverage and net-debt calculations must state selected carrying-value basis and treatment of deferred financing costs. |
| Q2 revenue rose year over year while Adjusted EBITDA and operating cash flow declined. | Q2 10-Q, pp. 2, 4 and 16 [C6, C8, C16] | Material | Not a source contradiction: metrics and periods are the same H1 comparison but measure different parts of the income/cash-flow chain. Preserve separately. | Credit analysis must not treat revenue growth as equivalent to EBITDA or cash-flow growth. |
| Proposed transaction consideration is described in the agreement and 8-K; the transaction remains pending in Q2 filing. | Merger agreement p. 9; Q2 10-Q p. 6 [C2, C27] | Material | No conflict: contractual terms are prospective; Q2 financials remain pre-close. | Do not pro forma the transaction into reported results or assume funding/closing. |
| FY2025 and Q2 debt disclosures include face, book, balance-sheet debt and lease financing obligations on different bases. | FY2025 10-K and Q2 10-Q [C9, C26] | Material | Preserve source-defined measures separately; no single total-obligations amount is substituted for debt. | Downstream leverage and debt-service analysis must state perimeter and debt definition. |

#### downstream_readiness

| Module | Status | Gap | Required action |
|---|---|---|---|
| CP-2 | READY_WITH_LIMITATIONS | Post-June results and current debt/covenant package absent. | Use H1 operating/financial evidence with dated caveats; obtain current figures and full agreement before current leverage or headroom conclusions. |
| CP-2C | READY_WITH_LIMITATIONS | Ownership, sponsor economics, complete distribution history and legal-capacity documents incomplete. | Separate observed issuer behavior from missing sponsor willingness/capacity; use governance gaps ledger. |
| CP-MODEL | READY_WITH_LIMITATIONS | Stable company and transaction facts available, but no October-current financial figures or final post-close capitalization. | Use only source-grounded snapshot rows below; retain source date and do not model transaction as completed. |

<!-- table-id: cp1a.cp_model_snapshot_fields -->
| field_id | value | status | source_id | source_locator | as_of |
|---|---|---|---|---|---|
| issuer_name | Caesars Entertainment, Inc. | READY | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Cover / issuer identity, p. 1 [C11] | 2026-10-02 |
| sector | Gaming, casino and hospitality; digital sports betting/iGaming | READY | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Business overview, p. 2 [C11] | 2026-10-02 |
| country | United States; Delaware corporation | READY | 5c51af90-71cc-4023-8aea-4523ce9f2428 | Merger disclosure identifies Delaware corporation, Note 1, p. 5 [C1] | 2026-10-02 |
| shareholders | Public company before closing; Recreational Enterprises reported approximately 5% and agreed to roll a portion; final rollover/post-close ownership not established | READY | 5e8a2604-12ea-471a-bbad-4e77b04c3186 | Merger description and rollover disclosure, p. 1 [C3] | 2026-10-02 |
| transaction_summary | Pending merger with Fertitta Gaming Holdco, LLC; $31.00 cash per eligible share plus conditional ticking fee | READY | 80a091bf-ceb5-4bb8-9006-297fd19a762e | Merger mechanics and consideration, §3.1(a), p. 25 [C2] | 2026-10-02 |
| business_description | Casino, hotel, food and beverage, entertainment and digital wagering operations; 52 domestic properties reported at FY2025 | READY | cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Business overview, p. 2 [C11] | 2026-10-02 |

#### T2D.1 — Source Register

| source_document_id | source_document_name | source_quality | period | entity_covered | data_supplied | limitation | downstream_use |
|---|---|---|---|---|---|---|---|
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars Entertainment, Inc. Form 10-K | High | FY ended Dec. 31, 2025 | Caesars and consolidated subsidiaries | Business, revenue categories, historical acquisitions, audited statements, debt/lease context, repurchases and related-party disclosure. [C11, C12, C13, C14, C15, C17, C20, C22, C23, C26] | Historical; no current post-Q2 data. | CP-2, CP-2C, CP-MODEL |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Entertainment, Inc. Form 10-Q | High | Q2 / six months ended June 30, 2026 | Caesars and consolidated subsidiaries | Interim results, debt, liquidity, acquisition events, merger status and operating segments. [C6, C7, C8, C9, C10, C16, C18, C19, C21, C24, C27] | Unaudited; June 30 period-end; no later-period figures. | CP-2, CP-2C, CP-MODEL |
| 80a091bf-ceb5-4bb8-9006-297fd19a762e | Agreement and Plan of Merger | High | Executed May 27, 2026 | Caesars, Fertitta Gaming, Merger Sub, Parent Guarantor and limited-purpose party | Transaction mechanics, consideration, termination fees, financing cooperation and guarantee. [C1, C2, C4, C28] | Financing commitment/schedules not fully supplied. | CP-2, CP-2C, CP-MODEL |
| 5e8a2604-12ea-471a-bbad-4e77b04c3186 | Caesars Form 8-K | High | Filed May 28, 2026 | Caesars and proposed merger parties | Transaction summary, rollover holder and reverse termination fee. [C3, C5] | Summary; agreement controls. | CP-2, CP-2C, CP-MODEL |

#### T2D.2 — Ownership & Control Register

| Item | Source-Supported Fact | Evidence Quality | Source Trace | Credit Mechanic | Credit Implication | Limitation |
|---|---|---|---|---|---|---|
| Current issuer ownership | Caesars was a listed public company; merger agreement proposes Parent ownership only upon closing. [C1] | High | 8-K p. 1; agreement §§2.1–2.3 [C1] | Transaction changes control and prospective capitalization; condition satisfaction is unconfirmed. | Do not treat Parent as current controlling shareholder before closing. | Current beneficial-owner breakdown not supplied. |
| Parent / acquirer | Fertitta Gaming Holdco, LLC is Parent and Merger Sub’s direct owner; Caesars would survive as wholly owned subsidiary. [C1] | High | Agreement preamble and §2.1 [C1] | Parent-level financing and capital structure may affect subsidiary creditors after close. | Require final structure and financing details for pro forma analysis. | Ultimate ownership, capital contributions and post-close structure beyond the stated subsidiary relationship not fully shown. |
| Rollover stockholder | Recreational Enterprises, Inc. was reported to own approximately 5% and to roll a portion; agreement Exhibit A lists 5,000,000 shares unless reduced. [C3] | High | 8-K p. 1; agreement Exhibit A [C3] | Rollover preserves some continuing equity interest, but final share count and ownership depend on agreements. | No precise post-close alignment conclusion. | Rollover and Parent Rollover Agreement terms not supplied. |
| Parent Guarantor | Landry’s Fertitta, LLC guarantees Parent and Merger Sub obligations under §9.14. [C28] | High | Agreement §9.14 [C28] | A guarantee creates a contractual payment/performance claim, subject to terms and guarantor capacity. | Relevant to transaction remedies; do not equate with funded equity support. | Guarantor financial statements and standalone capacity not provided. |
| Sponsor fund vintage / remaining life | No sponsor fund vintage or fund life disclosed in supplied materials. | Insufficient | Merger agreement and 10-Q review [C1] | Exit timing cannot be inferred from sponsor identity. | No exit-pressure conclusion. | Obtain sponsor vehicle/fund details if applicable. |
| Board, veto and control rights | Merger agreement provides a Parent board appointment right before closing after specified regulatory condition and notice. | High | Agreement §6.18, p. 94 | Pre-close board representation could affect governance during pendency, subject to conditions. | Monitor appointment and gaming approval; do not infer broader control rights. | Appointment status after June 30 not supplied. |
| Ownership percentages / equity contribution | Final Parent ownership percentages and committed equity contribution are not specified in the supplied materials. | Insufficient | Agreement and 8-K transaction descriptions [C1, C3] | Missing equity amount impairs pro forma leverage/funding assessment. | Requires full capitalization and financing schedule. | Commitment letters and rollover documents absent. |

#### T2D.3 — Governance Register

| Governance Topic | Source-Supported Fact | Risk Direction | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| Board and transaction governance | Caesars Board approved the merger agreement and recommended stockholder adoption; agreement includes a Parent nominee appointment process subject to regulatory approval. | Mixed | Board recommendation supports an orderly process, while Parent nominee rights alter oversight during a pending deal. | Monitor appointment, regulatory approval and any later recommendation changes. | High | 8-K p. 1; agreement §6.18 [C1] | No post-June appointment status. |
| Reporting and audit | FY2025 financial statements received an unqualified audit opinion; Q2 filing supplies interim statements. | Supportive | Audited annual reporting and filed interim results improve creditor visibility. | Supports monitoring, but does not replace lender certificates or later current reporting. | High | 10-K p. 28; Q2 10-Q [C23] | Q2 is unaudited and no post-June filing supplied. |
| Covenant reporting | Q2 filing reports compliance with applicable financial covenants at June 30. | Supportive | Reported compliance lowers evidence of an existing breach at that date; absent headroom prevents measurement of cushion. | Obtain covenant calculations and current compliance certificates. | High | Q2 10-Q p. 23 [C24] | No certificate or headroom calculation. |
| Related-party transactions | 10-K discloses CSY lease; a trust associated with the Executive Chairman’s family receives approximately 27% of rent. | Mixed | Related-party rent is a potential leakage/conflict channel; amount disclosed is $0.6m annual rent. | Monitor amendments, renewals and full related-party schedule; no material credit effect concluded from this fact alone. | High | 10-K p. 50 [C22] | Full current related-party register not supplied. |
| Transaction governance / financing | Parent Guarantor guarantees Parent and Merger Sub obligations; financing is not a closing condition. | Mixed | Guarantee provides contractual recourse, but funding can remain a Parent obligation independent of financing success. | Financing and guarantee capacity require separate verification; do not treat commitment as funded cash. | High | Agreement §§5.9, 6.16, 9.14 [C28] | Complete financing documents and guarantor financials absent. |
| Disclosure completeness | Public financial statements and deal terms are available, but schedules, financing commitment documents and current lender reporting are absent. | Insufficient Information | Missing details reduce visibility into pro forma capitalization, covenant capacity and sponsor economics. | Governance confidence restricted pending complete source package. | High for supplied documents; gap based on delivered source scope | Agreement and 10-Q [C1, C27] | Absence in the delivered set does not prove absence in issuer files. |

#### T2D.4 — Behavior Flag Register

| Flag ID | Behavior Type | Documented Action | Behavior Category | Amount / Funding Source | Legal-Capacity Link | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|---|---|---|
| CP-2C-FLAG-001 | Acquisition | Caesars reports a multi-year acquisition history and completed Windsor and Grand Bazaar transactions in 2026. [C17, C18, C19] | B — Neutral / Mixed | Grand Bazaar consideration approx. $66m, including $10m deferred; Windsor purchased net assets, funding source not specified. | Transaction agreements and financing terms not fully supplied. | Acquisitions can consume liquidity, introduce lease obligations and create integration risk. | Monitor funding, contribution and returns; no leverage increase inferred without financing data. | High | FY2025 10-K p. 2; Q2 10-Q pp. 6, 18 [C17, C18, C19] | No acquired EBITDA, pro forma leverage or integration data. |
| CP-2C-FLAG-002 | Share repurchase | Repurchased shares for $229m during FY2025; no repurchases in H1 2026 and company stated no further repurchases expected at that time due to proposed merger. [C20, C21] | B — Neutral / Mixed | $229m in FY2025; source of funds not separately identified. | Debt-document restrictions/baskets are not fully available; do not infer capacity. | Repurchases reduce retained cash, but cessation during pending transaction preserves cash relative to continued buyback. | Monitor cash retention and distributions; no distressed extraction or sponsor motive concluded. | High | FY2025 10-K p. 23; Q2 10-Q p. 13 [C20, C21] | No complete full-period distribution or funding-source history. |
| CP-2C-FLAG-003 | Support / guarantee | Parent Guarantor signed an unconditional guarantee of specified Parent and Merger Sub obligations. [C28] | A — Supportive / Creditor-Aligned, limited to contractual transaction obligations | Amount not separately stated; covers defined agreement obligations. | Guarantee language in agreement §9.14. | Adds a contractual obligor for Parent/Merger Sub obligations but does not fund the operating company. | Supports transaction counterparty recourse subject to guarantee terms and guarantor capacity. | High | Agreement §9.14 [C28] | Not an operating-company equity injection or evidence of sponsor support for existing debt. |
| CP-2C-FLAG-004 | Related-party transaction | Disclosed lease of approximately 30,000 sq. ft. from CSY; annual rent $0.6m, with a trust tied to the Executive Chairman’s family receiving approximately 27%. [C22] | B — Neutral / Mixed | $0.6m annual rent; no financing source. | Lease disclosed in 10-K; full current contract not reviewed here. | Related-party rent may create leakage/conflict, but amount is disclosed and not shown to be material to consolidated cash flow. | Monitor terms and other related-party payments; no extraction conclusion from this lease alone. | High | FY2025 10-K p. 50 [C22] | No complete related-party schedule or current lease amendment history. |

#### T2D.5 — Capital Allocation Risk Table

| Capital Allocation Item | Source-Supported Fact | Direction | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|
| Acquisitions / property purchases | Acquisition history includes several material acquisitions; 2026 Windsor and Grand Bazaar transactions completed. [C17, C18, C19] | Mixed | Cash use, new lease/fixed costs and integration may absorb liquidity; acquired earnings can offset only if demonstrated. | Require funding mix, acquired EBITDA and return evidence before pro forma credit benefit. | High | FY2025 10-K p. 2; Q2 10-Q pp. 6, 18 [C17, C18, C19] | Transaction-specific funding and pro forma leverage absent. |
| Share repurchases | FY2025 repurchases totaled $229m; no H1 2026 repurchases. [C20, C21] | Mixed | Repurchases lower retained cash; cessation limits additional current-period cash outflow. | Monitor future buybacks against leverage and liquidity. | High | FY2025 10-K p. 23; Q2 10-Q p. 13 [C20, C21] | Funding source and complete buyback authorization usage not fully reconciled here. |
| Organic capex | H1 2026 cash capex was $335m versus $453m in H1 2025. [C29] | Supportive near-term / mixed over cycle | Lower spend preserves cash in period; underinvestment could impair property competitiveness if sustained. | Evaluate maintenance versus growth split and required lease/gaming capital commitments. | High | Q2 10-Q p. 4 [C29] | No multi-year maintenance adequacy analysis. |
| Debt service / deleveraging | Q2 debt table shows $11.705bn book debt; operating cash flow H1 was $675m. [C8, C9] | Mixed | Debt service competes with capex, lease payments and liquidity needs. | Debt reduction and refinancing remain central credit sensitivities. | High | Q2 10-Q pp. 4, 9 [C8, C9] | No current net leverage or refinancing forecast calculated. |
| Dividends / distributions | No evidence of a Caesars common dividend in supplied sources; H1 2026 noncontrolling-interest distributions were $41m in cash-flow statement. | Mixed | Distributions to minority owners reduce consolidated cash available, while common dividends are not established. | Track subsidiary-level distributions and applicable debt restrictions. | High | Q2 10-Q p. 4 [C8] | No detailed recipient/source schedule or current basket tracker. |
| Liquidity preservation | No share repurchases during H1 2026; company said no repurchases expected at that time due to merger. [C21] | Supportive | Suspended buybacks retain cash versus continuing repurchases during pending transaction. | Positive for near-term cash retention, subject to subsequent behavior. | High | Q2 10-Q p. 13 [C21] | Statement is as of Q2 filing, not a later-period commitment. |
| Related-party payments | CSY lease annual rent $0.6m, with disclosed family trust interest. [C22] | Mixed | Related-party cash payment can be a leakage channel but disclosed rent is modest on its face. | Monitor full related-party arrangements; no broader leakage conclusion. | High | FY2025 10-K p. 50 [C22] | Full schedule absent. |

#### T2D.6 — Acquisition Appetite Table

| Acquisition / Period | Source-Supported Fact | Funding Mix | EBITDA / Pro Forma Basis | Integration Evidence | Leverage / Liquidity Effect | Risk Mechanic | Credit Implication | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|---|---|
| Historical acquisitions, 2014–2021 | Issuer identifies MTR, Isle of Capri, Tropicana, Caesars Entertainment Corporation and William Hill acquisitions. [C17] | Not disclosed in supplied excerpt | Not disclosed | Not disclosed in supplied excerpt | Not calculable from these materials | Serial acquisitions expand scale and may create integration and financing demands. | Treat acquisition history as evidence of growth via M&A, not evidence of current appetite or realized synergies. | FY2025 10-K p. 2 [C17] | Purchase prices, funding, acquired EBITDA and leverage unavailable here. |
| Caesars Windsor, March 2026 | Assumed operations under 20-year operating agreement; purchased net assets and entered 20-year lease. [C18] | Funding mix not specified | No acquired/pro forma EBITDA supplied | Operations transferred to Regional segment from March 3, 2026. | New asset purchase and lease obligations; amount of net leverage effect not established. | Long-term operating/lease commitments raise fixed-cost exposure; operating contribution may offset if sustained. | Assess with current Windsor contribution, rent and capital needs. | Q2 10-Q p. 6 [C18] | Purchase assets and lease terms are partially described; no full transaction agreement or pro forma return. |
| Grand Bazaar, May 2026 | Acquired remaining membership interest for approx. $66m, including $10m deferred consideration; accounted for as asset purchase. [C19] | Funding source not disclosed | Not disclosed | No post-acquisition contribution data. | Cash/deferred obligation; net liquidity impact not calculated. | Acquisition consumes capital and may add operating exposure. | Monitor settlement, asset performance and financing source. | Q2 10-Q p. 18 [C19] | No EBITDA, valuation or funding detail. |

#### T2D.7 — Disclosure Quality Log

| Disclosure Item | Available? | Source-Supported Detail | Credit Relevance | Severity | Source Trace | Required Follow-Up |
|---|---|---|---|---|---|---|
| Audited annual financial statements | Yes | FY2025 10-K includes audited statements and unqualified opinion. [C23] | Supports historical financial monitoring and baseline. | Minor | 10-K p. 28 [C23] | Obtain future filings when available. |
| Interim financial statements | Yes | Q2 2026 10-Q provides June 30 statements and H1 cash flow. [C6–C10] | Core current-period performance/liquidity, but not October-current. | Material | Q2 10-Q pp. 1–4, 9, 22 | Obtain subsequent filing and current cash/debt schedule. |
| Debt and maturity schedule | Partial | Debt table provides face/book values and contractual debt service. [C9] | Relevant to refinancing and debt service. | Material | Q2 10-Q p. 9 [C9] | Obtain complete current agreement, maturity schedule and reconciled carrying values. |
| Liquidity / revolver availability | Partial | June 30 total liquidity reported at $2.928bn. [C10] | Near-term liquidity; dated availability may change. | Material | Q2 10-Q p. 22 [C10] | Obtain current revolver certificate, borrowing base/availability and restrictions. |
| Covenant certificate / headroom | Partial | Filed report states covenant compliance at June 30 but does not provide full headroom calculations. [C24] | Monitoring and default risk. | Material | Q2 10-Q p. 23 [C24] | Obtain compliance certificate and covenant calculations. |
| EBITDA bridge / add-backs | Partial | Adjusted EBITDA is reconciled in public reporting; issuer defines non-GAAP measure. [C16] | Important for debt-service and covenant normalization. | Material | Q2 10-Q pp. 15–16 [C16] | Reconcile to debt-document EBITDA definitions. |
| Sponsor economics / fees | No | No sponsor fund economics, management fees or complete post-close ownership schedule established in supplied files. | Alignment, leakage and pro forma capital. | Material | Merger agreement and 8-K review [C1, C3] | Obtain financing, ownership, fee and rollover documents. |
| Dividend / distribution detail | Partial | Cash-flow statement reports noncontrolling distributions; no complete distribution history is supplied. | Cash leakage and subsidiary liquidity. | Material | Q2 10-Q p. 4 [C8] | Obtain entity-level distribution and restricted-payment history. |
| Acquisition funding details | Partial | Windsor and Grand Bazaar events described, but funding and acquired EBITDA not supplied. [C18, C19] | Leverage and return analysis. | Material | Q2 10-Q pp. 6, 18 [C18, C19] | Obtain transaction funding and pro forma contribution. |
| Board / control rights | Partial | Merger agreement has Parent nominee appointment process; current post-June status unavailable. | Governance and transaction control. | Material | Agreement §6.18, p. 94 | Obtain current board/appointment and gaming approval status. |
| Basket usage tracker | No | No current basket usage tracker or full credit agreement supplied. | Cannot determine permitted capacity. | Material | Q2 10-Q debt disclosure [C9] | Obtain current covenant/basket tracker and legal documents. |

#### T2D.8 — Creditor Alignment & Financial Policy Table

| Dimension | Assessment | Evidence | Risk Mechanic | Credit Implication | Score | Evidence Quality | Source Trace | Limitation |
|---|---|---|---|---|---|---|---|---|
| Leverage tolerance | Not Scorable | High debt and lease obligations are reported, but no sponsor policy or full pro forma leverage is supplied. [C9, C26] | Balance-sheet burden is observable; risk appetite cannot be attributed to current or future owners. | Do not infer sponsor leverage tolerance; obtain pro forma capitalization and full current debt definitions. | Not Scorable | High | Q2 10-Q p. 9; FY2025 10-K p. 13 [C9, C26] | Debt and lease measures have differing bases; ownership transition pending. |
| Shareholder extraction risk | Mixed | FY2025 repurchases were $229m; no repurchases in H1 2026, with no further repurchases expected at that time due to merger. [C20, C21] | Past repurchases reduced retained cash, while H1 cessation supports cash retention. | Monitor distributions and buybacks relative to leverage and liquidity. | 3 | High | FY2025 10-K p. 23; Q2 10-Q p. 13 [C20, C21] | No evidence here of debt-funded recap or stressed repurchase. |
| Acquisition appetite | Mixed | Multiple historical acquisitions and two 2026 asset/property transactions; funding and returns incomplete. [C17, C18, C19] | M&A may consume cash or add obligations; benefits cannot be credited without demonstrated EBITDA. | Monitor funding, integration and returns; no pro forma leverage inferred. | 3 | High | FY2025 10-K p. 2; Q2 10-Q pp. 6, 18 [C17, C18, C19] | No complete acquisition-level financing/EBITDA history. |
| Support behavior | Not Scorable | Parent Guarantor guarantees defined Parent/Merger Sub obligations under merger agreement. [C28] | Contractual transaction guarantee is not evidence of operating-company support or equity cure. | Do not assume sponsor willingness to support existing creditors. | Not Scorable | High | Agreement §9.14 [C28] | Guarantee capacity and any support for Caesars debt not established. |
| Disclosure transparency | Mixed | Public 10-K/10-Q and merger documents disclose key facts, but current agreement, schedules, financing package and lender reporting are absent. | Missing detail limits verification of current covenant capacity, ownership and funding. | Restricted confidence; request missing materials. | 3 | High for supplied sources | 10-K, 10-Q, agreement and 8-K [C1, C27] | Delivered source set is incomplete; absence here is not proof issuer has not disclosed elsewhere. |
| Creditor treatment / amendment behavior | Not Scorable | Several credit amendments are named in filings, but full current agreement and complete amendment/LME history are not included in evidence. | Cannot determine lender treatment, covenant weakening or priming behavior from incomplete legal set. | Obtain full amendment history and current documents before creditor-treatment conclusion. | Not Scorable | High for filed statements | FY2025 10-K debt disclosures; Q2 10-Q [C9] | No complete legal package or LME history. |
| Legal-capacity linkage | Not Scorable | Deal covenants and selected debt provisions do not establish complete current RP, investment, debt, lien or transfer capacity. | Legal capacity cannot be determined from partial instruments. | Do not infer permitted distributions, debt or asset transfers. | Not Scorable | High | Agreement; Q2 10-Q [C2, C9] | Complete current credit agreement and security documents absent. |
| Reporting quality | Creditor-favorable | FY2025 audited financial statements received an unqualified opinion; interim filing provides detailed statements and debt data. [C23] | Regular filed reporting improves historical monitoring and reduces information uncertainty. | Supports ongoing monitoring, with current-period and lender-reporting caveats. | 1 | High | FY2025 10-K p. 28; Q2 10-Q [C23] | No lender certificates, later quarter or complete covenant package. |
| Related-party leakage risk | Mixed | Disclosed CSY lease and related family trust interest; annual rent $0.6m. [C22] | Related-party payment can create leakage, though disclosed amount alone is not evidence of material extraction. | Monitor complete related-party schedule and changes to terms. | 3 | High | FY2025 10-K p. 50 [C22] | Other fees/payments and full agreement not supplied. |

#### T2D.9 — Sponsor Risk Assessment Table

| Risk-Level Driver | Evidence | Risk Mechanic | Credit Implication | Evidence Quality | Source Trace | Countervailing Evidence | Limitation |
|---|---|---|---|---|---|---|---|
| Transaction and ownership transition | Signed merger agreement; Parent Guarantor guarantees defined obligations. [C1, C28] | New ownership and financing may change leverage and creditor risk; completion remains conditional. | Monitor approvals, funding and final capitalization before using pro forma conclusions. | High | Agreement §§2.1, 9.14; Q2 10-Q [C1, C27, C28] | Contractual guarantee and defined end-date/regulatory fee structure. | No full commitment package, current status or final ownership table. |
| Shareholder financial policy | $229m FY2025 repurchases; none in H1 2026. [C20, C21] | Buybacks reduce retained cash; H1 pause preserves cash relative to continued repurchases. | Mixed behavior; no evidence of stressed extraction or recap in supplied materials. | High | FY2025 10-K p. 23; Q2 10-Q p. 13 [C20, C21] | No buybacks during reported H1 2026. | Full distribution/funding history absent. |
| Acquisition and fixed-cost exposure | Historical acquisitions; Windsor lease/asset purchase and Grand Bazaar acquisition. [C17, C18, C19] | Capital use, integration, rent and operating commitments may reduce liquidity if cash flows underperform. | Require returns and funding information; monitor fixed costs. | High | FY2025 10-K p. 2; Q2 10-Q pp. 6, 18 [C17, C18, C19] | Transactions are disclosed; no evidence of failure or distress in supplied sources. | Funding, pro forma EBITDA and integration outcome not reported. |
| Reporting and monitoring | Audited FY2025 statements, Q2 filing, and Q2 covenant-compliance statement. [C23, C24] | Strong public reporting helps monitor, but absence of lender certificate/headroom restricts early-warning assessment. | Public disclosure is a positive counterweight; current covenant cushion remains unknown. | High | FY2025 10-K p. 28; Q2 10-Q p. 23 [C23, C24] | Issuer reports compliance as of June 30. | No later covenant data or full credit agreement. |
| Overall level | Mixed evidence and material ownership/legal-capacity gaps; no documented dividend recap, LME, priming or equity cure in supplied source set. | Incomplete behavior evidence prevents a confident directional sponsor assessment; documented repurchases/acquisitions warrant monitoring but do not establish extraction. | **Medium / incomplete-information governance risk** for monitoring purposes; not a sponsor-reputation conclusion. | High for cited facts; incomplete for behavior history | T2D.2–T2D.8 [C17, C18, C19, C20, C21, C22, C23, C24, C28] | Audited reporting, reported covenant compliance, cessation of H1 buybacks and contractual guarantee. | Obtain full ownership, fee, distribution, lender-treatment and legal-capacity records. |

#### T2D.10 — Cross-Module Handoff Register

| Downstream Module | Handoff Tag | Handoff Item | Why It Matters | Required Consumer Action | Source / Flag Link | Limitation |
|---|---|---|---|---|---|---|
| CP-2 | CP-2C-HANDOFF-CP-2 | Pending transaction; H1 revenue/EBITDA/cash-flow trends; buybacks and acquisition history | Governance and capital allocation affect retained FCF and pro forma leverage. | Keep pre-close and pro forma cases separate; request current results and full debt schedule. | T2D.4–T2D.9; [C6, C8, C16, C17, C18, C19, C20, C21] | Current post-June figures unavailable. |
| CP-2A | CP-2C-HANDOFF-CP-2A | Transaction delay, gaming volatility, costs and liquidity transmission | Behavioral and transaction pathways can intensify downside timing. | Use only supported triggers; do not assign unsupported scenario probabilities. | Analysis downside path; [C25, C27, C28] | No forecast or stress-case inputs supplied. |
| CP-2D | CP-2C-HANDOFF-CP-2D | Dated cash/revolver pool, debt and lease burden, no H1 buybacks | Cash retention and fixed charges affect liquidity runway. | Reconfirm cash and revolver availability and distributions after June 30. | T2D.5, T2D.8; [C7, C9, C10, C21, C26] | No October liquidity schedule. |
| CP-3 | CP-2C-HANDOFF-CP-3 | Public ownership transition, historical buybacks/acquisitions and reporting | Governance can affect relative-value confidence and monitoring. | Treat transaction as pending and do not infer sponsor behavior from identity. | T2D.2–T2D.9 [C1, C17, C18, C19, C20, C21, C22, C23, C24] | No full current market or sponsor data in this module. |
| CP-3C | CP-2C-HANDOFF-CP-3C | No proven sponsor support for existing debt; transaction guarantee is limited to specified obligations | Distinguishes contractual transaction guarantee from willingness to support operating debt. | Do not treat guarantee as funded support; verify commitment and guarantor capacity. | T2D.4, T2D.8–T2D.9 [C28] | Guarantor financial capacity not supplied. |
| CP-4A | CP-2C-HANDOFF-CP-4A | Legal capacity remains unresolved without full current credit/security package | Permitted payments, debt, liens and transfers affect leakage and recovery. | Obtain and analyze complete operative documents; no capacity inference from partial sources. | T2D.7–T2D.8; conflict CF-1 [C9] | Current complete agreement and security package absent. |
| CP-5 | CP-2C-HANDOFF-CP-5 | Cited records support identified facts; source limitations and conflicts preserved | Supports traceability and validation of downstream claims. | Recheck all cited facts against primary sources and maintain period/basis labels. | Evidence Trace and Source Registry [C1–C30] | No host validation result claimed. |
| CP-5A | CP-2C-HANDOFF-CP-5A | Restricted confidence reflects source/period gaps, not a source-supported adverse behavior finding | Confidence must reflect missing current and legal evidence. | Test completeness and verify debt-basis reconciliation and source locators. | QA Validation; CF-1; gaps ledger | Automated host validation follows this response. |
| CP-6 | CP-2C-HANDOFF-CP-6 | Medium / incomplete-information governance view; key triggers are transaction status, funding, liquidity and distributions | Committee decision requires transaction and governance uncertainty to remain explicit. | Debate both conditional deal support and unresolved capitalization/behavior evidence. | T2D.9 [C1, C2, C10, C27, C28] | No decision or investment recommendation is made here. |
| CP-6A | CP-2C-HANDOFF-CP-6A | Public shareholders, rollover participant and prospective Parent ownership | Ownership concentration and transaction exposure may affect portfolio event risk. | Use only verified ownership facts and flag final post-close control as unknown. | T2D.2; [C1, C3] | Final rollover and capitalization unavailable. |

#### T2D.11 — Gaps Ledger

| Gap ID | Missing Data | Why It Matters | Affected Section / Flag / Export Record | Consequence for Confidence | Required Follow-Up Source |
|---|---|---|---|---|---|
| CP-2C-GAP-001 | Final ownership chart, ultimate Parent owners and post-close capitalization | Ownership and control determine governance, leverage allocation and creditor recourse. | Ownership register; T2D.2; T2D.9; CP-MODEL snapshot | High impact | Current ownership chart, merger closing capitalization and equity contribution schedule. |
| CP-2C-GAP-002 | Sponsor vehicle/fund vintage and remaining life, if applicable | Cannot assess time horizon or exit pressure without disclosed fund facts. | T2D.2; T2D.8 | Medium impact | Sponsor/Parent ownership and fund disclosure documents. |
| CP-2C-GAP-003 | Final rollover amount and rollover agreement terms | Affects cash consideration, ownership and alignment. | Transaction summary; T2D.2; T2D.10 | High impact | Executed Rollover Agreement and Parent Rollover Agreements. |
| CP-2C-GAP-004 | Complete financing commitments, sources/uses and equity funding | Needed to assess transaction funding, pro forma debt and potential sponsor support. | Transaction summary; T2D.3, T2D.4, T2D.6, T2D.7 | High impact | Executed debt/equity commitment letters, fee letters and final sources-and-uses statement. |
| CP-2C-GAP-005 | Complete distribution, buyback and sponsor-fee history with funding sources | Needed to distinguish ordinary capital allocation from extraction and test cash leakage. | Behavior flags; T2D.4–T2D.8 | High impact | Company cash-flow schedules, related-party disclosures and lender distribution records. |
| CP-2C-GAP-006 | Complete current credit agreement, amendments, compliance certificates and basket tracker | Needed to assess legal capacity, lender control and creditor treatment. | T2D.3, T2D.4, T2D.7, T2D.8 | High impact | Current conformed credit agreement, schedules, certificates and amendment history. |
| CP-2C-GAP-007 | Current collateral, guarantee and intercreditor documentation | Needed for lien priority, recovery access and asset-transfer/priming capacity. | T2D.3, T2D.7, T2D.8, T2D.10 | High impact | Executed security agreements, intercreditor agreements, mortgages and guarantee/collateral schedules. |
| CP-2C-GAP-008 | Post-June 30, 2026 reporting and transaction status | Current financial policy, liquidity, behavior and closing status may have changed. | All governance and financial-policy assessments | High impact | Subsequent 10-Q/8-K filings and current management/lender reporting. |
| CP-2C-GAP-009 | Acquisition funding, acquired EBITDA and integration results for recent transactions | Prevents assessment of returns, leverage effect and acquisition discipline. | T2D.4–T2D.6 | Medium impact | Purchase agreements, funding documents and post-close operating/EBITDA schedules. |
| CP-2C-GAP-010 | Full related-party transaction and payment schedule | A single disclosed lease does not establish total leakage or conflict exposure. | T2D.3–T2D.5, T2D.8 | Medium impact | Current related-party register, contracts and payments. |
| CP-2C-GAP-011 | LME, amendment, waiver, exchange and restructuring history | Required to assess creditor treatment and prior willingness evidence. | T2D.4, T2D.7–T2D.9 | High impact | Complete lender amendment, waiver, exchange and restructuring history. |
| CP-2C-GAP-012 | Parent Guarantor financial capacity | Contractual guarantee does not itself establish ability to perform. | T2D.3, T2D.4, T2D.9 | Medium impact | Guarantor financial statements, structure chart and guarantee support analysis. |

## Evidence Trace

| Claim | Citation marker | Document and page |
|---|---|---|
| Proposed merger parties and structure | [C1] | Q2 10-Q, p. 5 |
| $31.00 consideration and conditional ticking fee | [C2] | Merger agreement, p. 9 |
| Rollover holder and approximate ownership | [C3] | 8-K, p. 1 |
| Company termination fee | [C4] | Merger agreement, p. 25 |
| Reverse termination fee | [C5] | 8-K, p. 2 |
| H1 revenue and comparison | [C6] | Q2 10-Q, p. 2 |
| Cash balance | [C7] | Q2 10-Q, p. 2 |
| H1 operating cash flow | [C8] | Q2 10-Q, p. 4 |
| Debt face and book value | [C9] | Q2 10-Q, p. 9 |
| Reported cash and revolver capacity | [C10] | Q2 10-Q, p. 22 |
| FY2025 portfolio size | [C11] | FY2025 10-K, p. 2 |
| FY2025 casino revenue | [C12] | FY2025 10-K, p. 19 |
| FY2025 food and beverage revenue | [C13] | FY2025 10-K, p. 19 |
| FY2025 hotel revenue | [C14] | FY2025 10-K, p. 19 |
| FY2025 other revenue | [C15] | FY2025 10-K, p. 19 |
| H1 consolidated Adjusted EBITDA | [C16] | Q2 10-Q, p. 16 |
| Historical acquisition sequence | [C17] | FY2025 10-K, p. 2 |
| Caesars Windsor transaction | [C18] | Q2 10-Q, p. 6 |
| Grand Bazaar acquisition | [C19] | Q2 10-Q, p. 18 |
| FY2025 share repurchases | [C20] | FY2025 10-K, p. 23 |
| H1 2026 share-repurchase disclosure | [C21] | Q2 10-Q, p. 13 |
| CSY related-party lease | [C22] | FY2025 10-K, p. 50 |
| Annual audit opinion | [C23] | FY2025 10-K, p. 28 |
| Reported covenant compliance | [C24] | Q2 10-Q, p. 23 |
| Merger conditions and timing risk | [C25] | Q2 10-Q, p. 25 |
| FY2025 debt and lease context | [C26] | FY2025 10-K, p. 13 |
| Merger costs and pending status | [C27] | Q2 10-Q, p. 6 |
| Parent Guarantor guarantee | [C28] | Merger agreement, §9.14, p. 27 |
| H1 cash capital expenditures | [C29] | Q2 10-Q, p. 4 |
| Company founding | [C30] | FY2025 10-K, p. 2 |

## Source Registry

| Source ID | Document | Type / quality | Period and use | Limitation |
|---|---|---|---|---|
| cfe73d91-1930-4827-88ff-f1cbfb3b9f18 | Caesars FY2025 Form 10-K | Primary filed annual report; audited financial statements | FY ended Dec. 31, 2025; business, revenue mix, acquisition history, debt/lease, governance and related-party facts. [C11, C12, C13, C14, C15, C17, C20, C22, C23, C26, C30] | Historical baseline only. |
| 5c51af90-71cc-4023-8aea-4523ce9f2428 | Caesars Q2 2026 Form 10-Q | Primary filed interim report; unaudited statements | Quarter and six months ended June 30, 2026; performance, liquidity, debt, acquisitions, transaction status and covenant statement. [C6, C7, C8, C9, C10, C16, C18, C19, C21, C24, C25, C27, C29] | No post-June data. |
| 80a091bf-ceb5-4bb8-9006-297fd19a762e | Agreement and Plan of Merger | Executed primary transaction agreement | May 27, 2026; merger mechanics, consideration, termination, financing and guarantee. [C1, C2, C4, C28] | Schedules and complete financing package absent. |
| 5e8a2604-12ea-471a-bbad-4e77b04c3186 | Form 8-K transaction disclosure | Primary SEC filing | May 28, 2026; summary of transaction, rollover and reverse termination provisions. [C3, C5] | Summary is qualified by full agreement. |

## Gaps & Conflicts

The material open items are complete current debt and security documents, post-June financial results, current ownership/capitalization, detailed acquisition funding, sponsor economics and the complete distribution/LME history. These gaps limit current leverage, legal capacity, recovery, governance scoring and transaction funding assessment. See the detailed gaps register and source conflict log above. The debt table contains multiple disclosed bases: Q2 face value $11.807bn, book value $11.705bn, and balance-sheet current plus long-term debt of $11.699bn. Preserve all three and obtain an accounting/debt schedule reconciliation; do not silently select or combine them. [C7, C9]

## QA Validation

| Check | Result | Note |
|---|---|---|
| Identity and lineage | PASS | CP-1A, CZR, Q2 2026, analysis date and CP-0 lineage match the host-provided run fields. |
| Evidence scope | PASS WITH LIMITATIONS | Used only the four delivered evidence source IDs; no external research or unprovided source asserted. |
| Citation trace | SELF-CHECKED | Each material claim is cited to an evidence marker; host citation location verification is not claimed. |
| Register completeness | SELF-CHECKED | CP-1A core registers, T2D.1–T2D.11 and the tagged six-row CP-MODEL snapshot are present. |
| Nulls, periods and conflicts | PASS WITH LIMITATIONS | No unreported metric is converted to zero; Q2, FY2025, debt bases and transaction status remain separately labeled. |
| Governance discipline | PASS WITH LIMITATIONS | No sponsor reputation or willingness inferred from identity; guarantee distinguished from funded support; gaps retained. |
| Confidence | 57 / 100 — Low | Source gate is partial and material current/legal inputs are absent; score is capped consistently with Restricted status. |
| QA / committee status | Restricted / Requires More Work | Source-limited handoff; not a completed credit recommendation. |
| Host validation | PENDING | Host validation follows this response; no script result or file attachment result is claimed. |