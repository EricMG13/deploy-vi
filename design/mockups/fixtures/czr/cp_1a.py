"""CZR CP-1A: business and transaction fact pack. Real profile, ownership, management, merger events and operating
facts (base data C1-C18, C210-C227, C284-C310, the operating-model figures); issue ratings from TRACE; the
corporate family rating and outlooks are synthetic (no agency report in the pack, G11) and marked."""

from __future__ import annotations

import json
from pathlib import Path

from core import GAP, Ctx, Handoff
from czr.cp_3 import is_primary, merger_debt_tail, post_close_leverage
from helpers import caos_text, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]
Q10, K10 = "CZR_Q2_2026_10Q.txt", "CZR_FY2025_10K.txt"
TRACE = {
    "secured": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt",
    "unsecured": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt",
}


def _ratings(ctx: Ctx, h: Handoff) -> tuple[list[dict], dict]:
    ag = FACTS["agency"]
    syn = h.cite_synthetic(
        "agency",
        "No agency report is in the pack (G11), so the corporate family rating and outlooks are plausible for a B1 gaming credit under a pending take-private.",
        "Caesars",
        file="synthetic-facts.json",
    )
    syn_dates = h.cite_synthetic(
        "agency_dates",
        "The rating dates of the synthetic corporate ratings are invented to follow the Moody's last-rated date on the notes and the merger announcement.",
        "Caesars",
    )
    rows: list[dict] = []
    info = {}
    for key, label in (
        ("secured", "6.50% senior secured notes due 2032"),
        ("unsecured", "6.00% senior notes due 2032"),
    ):
        f = TRACE[key]
        for agency, rl, dl in (
            ("Moody's", "Moody's rating shown: ", "Moody's last-rated date shown: "),
            (
                "S&P",
                "Standard & Poor's rating shown: ",
                "Standard & Poor's last-rated date shown: ",
            ),
        ):
            m_r = h.cite_doc_find(f, rl)
            m_d = h.cite_doc_find(f, dl)
            rating = ctx.corpus_lines(f)[ctx.find_line(f, rl) - 1].split(": ")[1].strip()
            date = ctx.corpus_lines(f)[ctx.find_line(f, dl) - 1].split(": ")[1].strip()
            rows.append(
                {
                    "agency": agency,
                    "scope": f"Issue rating, {label}",
                    "rating": rating,
                    "outlook": "Not displayed",
                    "rating_date": date,
                    "rationale": "FINRA displays the rating and its last-rated date; no outlook, report or rationale is shown."
                    + (
                        " The S&P date is stale against the October observation."
                        if agency == "S&P"
                        else ""
                    ),
                    "cite": join_marks(m_r, m_d),
                }
            )
            info[(key, agency)] = rating
    rows.append(
        {
            "agency": "Moody's",
            "scope": "Corporate family rating",
            "rating": ag["moodys"]["cfr"],
            "outlook": ag["moodys"]["outlook"],
            "rating_date": "2026-09-28",
            "rationale": "Synthetic: leverage near 5.6x on Moody's adjusted basis and unstated merger debt; dated with the notes' last-rated date.",
            "cite": join_marks(syn, syn_dates),
        }
    )
    rows.append(
        {
            "agency": "S&P",
            "scope": "Issuer credit rating",
            "rating": ag["sp"]["issuer_rating"],
            "outlook": ag["sp"]["outlook"],
            "rating_date": "2026-05-28",
            "rationale": "Synthetic: placed on CreditWatch the day after the merger announcement while the new debt is unstated.",
            "cite": join_marks(syn, syn_dates),
        }
    )
    return rows, {"syn": syn}


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-1A", "CZR", run_id, "2026-10-02", ["CP-0", "CP-1"], fixture_file="czr/cp_1a.py"
    )
    h.qa("Restricted")
    ratings, rinfo = _ratings(ctx, h)
    syn = rinfo["syn"]
    c = h.cite_data
    m_sh = h.cite_doc_find(Q10, "203,720,372")
    mgmt = join_marks(c("C3"), c("C4"), c("C5"))

    syn_sponsor = h.cite_synthetic(
        "sponsor_quality",
        "Fertitta Entertainment is an owner-operator rather than a financial sponsor, so Medium reflects an untested leverage appetite.",
        "Caesars",
    )
    h.table(
        "snapshot.company_profile",
        [
            {
                "morningstar_issuer_id": GAP,
                "sector": "Leisure Facilities & Services",
                "country": "United States",
                "shareholders": f"Public holders of 203,720,372 shares outstanding at 23 July 2026; the Carano family owns about {ctx.val('merger_carano_stake'):.0f}% {c('C217')}",
                "management": "Thomas R. Reeg (Chief Executive Officer), Bret Yunker (Chief Financial Officer), Anthony Carano (President and Chief Operating Officer)",
                "corp_rating_moodys": FACTS["agency"]["moodys"]["cfr"],
                "corp_rating_sp": FACTS["agency"]["sp"]["issuer_rating"],
                "corp_rating_fitch": GAP,
                "outlook_moodys": FACTS["agency"]["moodys"]["outlook"],
                "outlook_sp": FACTS["agency"]["sp"]["outlook"],
                "outlook_fitch": GAP,
                "sponsor_quality": "Medium",
                "listed": "Yes",
                "ticker": "CZR",
                "cite": join_marks(m_sh, c("C217"), c("C2"), mgmt, syn, syn_sponsor),
            }
        ],
    )

    desc_marks = join_marks(
        c("C284"), c("C285"), c("C292"), c("C294"), c("C295"), c("C296"), c("C287")
    )
    h.table(
        "snapshot.business_description",
        [
            {
                "description": (
                    "Caesars is a geographically diversified gaming and hospitality company founded in 1973 by the Carano family. "
                    "At 30 June 2026 it owned, leased, managed or branded 54 properties in 20 jurisdictions in North America, with about 53,800 slot machines, 2,800 table games and 46,300 hotel rooms. "
                    "It reports four segments: Las Vegas, Regional, Caesars Digital, and Managed and Branded. "
                    "Its pending acquisition by Fertitta Entertainment would take it private at about US$17.6bn including assumed debt."
                ),
                "cite": join_marks(desc_marks, c("C212")),
            }
        ],
    )

    share_lv = h.cite_fig("opm_seg_share_las_vegas_fy2025")
    marg_lv = h.cite_fig("opm_seg_margin_las_vegas_fy2025")
    share_rg = h.cite_fig("opm_seg_share_regional_fy2025")
    marg_rg = h.cite_fig("opm_seg_margin_regional_fy2025")
    share_dg = h.cite_fig("opm_seg_share_caesars_digital_fy2025")
    marg_dg = h.cite_fig("opm_seg_margin_caesars_digital_fy2025")
    facts = [
        {
            "item": "Revenue mix",
            "fact": "FY2025 net revenues of US$11,486m: casino 58%, hotel 17% and food and beverage 15% of the total, the rest other.",
            "risk_mechanism": "Casino revenue is net win, so hold and volume move it faster than costs adjust.",
            "credit_implication": "Gaming-led, discretionary revenue makes EBITDA and cash conversion cyclical.",
            "evidence_quality": "Audited",
            "cite": join_marks(c("C51"), c("C289"), c("C290"), c("C291")),
        },
        {
            "item": "Segments, FY2025",
            "fact": "Las Vegas earns 42.7% margin on 35.3% of revenue, Regional 31.1% on 50.1%, Caesars Digital 16.8% on 12.3%, Managed and Branded 24.0% on 2.4%.",
            "risk_mechanism": "The highest-margin segment is also the one now losing margin, so mix shifts EBITDA down faster than revenue.",
            "credit_implication": "Las Vegas weakness costs more EBITDA than Regional growth adds.",
            "evidence_quality": "Audited",
            "cite": f"{share_lv} {marg_lv} {share_rg} {marg_rg} {share_dg} {marg_dg}",
        },
        {
            "item": "Footprint and real estate",
            "fact": "The company owned 22 and leased 25 of its casinos at 30 June 2026; 18 are leased from VICI and six from GLPI, and Caesars Windsor is leased from the Ontario Lottery and Gaming Corporation.",
            "risk_mechanism": "Master-lease rent is fixed and escalates, and does not fall when trading weakens.",
            "credit_implication": "Rent ranks as a fixed claim ahead of debt service in effect, so EBITDA after rent is the thinner cushion.",
            "evidence_quality": "Issuer-stated",
            "cite": join_marks(c("C297"), c("C298"), c("C299"), c("C300"), c("C301")),
        },
        {
            "item": "Lease financing obligations",
            "fact": "The VICI leases carry a 15-year initial term and about US$11.7bn of financing obligation; the GLPI leases run 20 years with about US$1.3bn. The balance sheet shows US$13,157m of long-term financing obligations at 30 June 2026.",
            "risk_mechanism": "Failed sale-leaseback accounting keeps the obligations outside reported debt although the cash rent is contractual.",
            "credit_implication": "Debt-only leverage understates fixed claims; CP-1D restates it with the obligations added.",
            "evidence_quality": "Audited",
            "cite": join_marks(c("C302"), c("C304"), c("C305"), c("C306"), c("C184")),
        },
        {
            "item": "Digital reach",
            "fact": "Online sports betting is offered in 27 of 34 jurisdictions with sports betting, iGaming in five, and the Racebook app in 23 states.",
            "risk_mechanism": "Digital earnings depend on hold and on state tax rates, both outside management's control.",
            "credit_implication": "Digital growth has not yet converted into EBITDA growth (Q2 Digital Adjusted EBITDA fell).",
            "evidence_quality": "Issuer-stated",
            "cite": join_marks(c("C307"), c("C308"), c("C309"), c("C310")),
        },
        {
            "item": "Perimeter change",
            "fact": "Caesars Windsor was consolidated from 3 March 2026 and the remaining Grand Bazaar interest bought on 1 May 2026 for about US$66m.",
            "risk_mechanism": "Acquired revenue flatters reported growth and adds lease and capital commitments.",
            "credit_implication": "Reported Regional growth overstates the organic trend.",
            "evidence_quality": "Issuer-stated",
            "cite": join_marks(c("C365"), h.cite_caos(FOLDER, "CP-1A", 19)),
        },
    ]
    h.table("cp1a.business_facts", facts)

    h.table(
        "cp1a.ownership_governance",
        [
            {
                "topic": "Control today",
                "fact": "Public company listed on Nasdaq with 203,720,372 shares outstanding; the Carano family holds about 5% through Recreational Enterprises, Inc.",
                "risk_direction": "Neutral",
                "credit_implication": "No controlling holder; control passes to Fertitta Gaming Holdco only if the merger closes.",
                "cite": join_marks(m_sh, c("C217"), h.cite_caos(FOLDER, "CP-1A", 3)),
            },
            {
                "topic": "Acquirer",
                "fact": "Fertitta Gaming Holdco, LLC (Parent) with Empire Merger Sub, Inc.; Landry's Fertitta, LLC is Parent Guarantor and Hospitality Headquarters, Inc. is party only for Section 9.14(j).",
                "risk_direction": "Neutral",
                "credit_implication": "An owner-operator, not a financial sponsor; its leverage appetite is untested in the sources.",
                "cite": join_marks(c("C7"), c("C8"), c("C9"), c("C10"), c("C6")),
            },
            {
                "topic": "Financing of the deal",
                "fact": "Equity from Fertitta Entertainment, assumed Caesars debt and new committed debt arranged by 10 banks; the deal is not subject to a financing condition.",
                "risk_direction": "Negative",
                "credit_implication": "New debt of unstated size (G8) may rank ahead of or alongside existing creditors."
                + merger_debt_tail(ctx, run_id),
                "cite": join_marks(c("C12"), c("C13"), c("C216")),
            },
            {
                "topic": "Break fees",
                "fact": "Company termination fee of US$200m (US$100m in specified go-shop cases) and a reverse termination fee of US$450m payable by Parent.",
                "risk_direction": "Neutral",
                "credit_implication": "A reverse fee is a remedy for Caesars, not liquidity available to creditors.",
                "cite": join_marks(c("C224"), c("C225"), c("C226")),
            },
            {
                "topic": "Capital allocation",
                "fact": "Caesars bought back 9,606,145 shares for US$229m in 2025 and made none in the first half of 2026.",
                "risk_direction": "Neutral",
                "credit_implication": "History of buybacks is monitored, but the sources show no sponsor extraction or distressed distributions.",
                "cite": join_marks(
                    h.cite_caos(FOLDER, "CP-1A", 20), h.cite_caos(FOLDER, "CP-1A", 21)
                ),
            },
            {
                "topic": "Advisers",
                "fact": "PJT Partners, Latham & Watkins and Skadden advise Caesars; Morgan Stanley, Goldman Sachs and White & Case advise Fertitta.",
                "risk_direction": "Neutral",
                "credit_implication": "No credit effect; recorded so the transaction record is complete.",
                "cite": join_marks(c("C14"), c("C15")),
            },
        ],
    )

    ev = [
        (
            "2026-03-03",
            "Caesars Windsor consolidated under a 20-year operating agreement",
            "Completed",
            "Adds Regional revenue and a 20-year property lease; growth is not like-for-like.",
            "Yes",
            join_marks(c("C365"), h.cite_caos(FOLDER, "CP-1A", 18)),
        ),
        (
            "2026-05-01",
            "Remaining Grand Bazaar membership interest acquired for about US$66m",
            "Completed",
            "Uses cash and adds assets; accounted for as an asset purchase.",
            "Yes",
            h.cite_caos(FOLDER, "CP-1A", 19),
        ),
        (
            "2026-05-27",
            "Merger agreement signed with Fertitta Gaming Holdco at US$31.00 a share, about US$17.6bn including assumed debt",
            "Pending",
            "Changes ownership and the capital structure; new debt of unstated size."
            + merger_debt_tail(ctx, run_id),
            "No",
            join_marks(c("C11"), c("C210"), c("C212"), c("C213")),
        ),
        (
            "2026-07-11",
            "Go-shop period ended",
            "Completed",
            "The window for competing proposals has closed.",
            "No",
            c("C223"),
        ),
        (
            "2026-07-13",
            "Mobile sports betting and iGaming launched in Alberta, Canada",
            "Completed",
            "A subsequent event after the balance-sheet date; no earnings effect is quantified.",
            "No",
            h.cite_doc_find(Q10, "launched mobile sports betting and iGaming in Alberta"),
        ),
        (
            "2027-05-27",
            "Initial merger End Date",
            "Contractual",
            "Failure to close by this date allows termination and prolongs uncertainty.",
            "No",
            c("C220"),
        ),
        (
            "2027-06-26",
            "Ticking fee starts at US$0.00715 per share per day",
            "Contractual",
            "Delay raises the price paid and the cost of the deal.",
            "No",
            join_marks(c("C219"), c("C218")),
        ),
        (
            "2027-08-27",
            "First extended End Date, in specified regulatory cases",
            "Contractual",
            "Extends the period of uncertainty.",
            "No",
            c("C221"),
        ),
        (
            "2027-11-27",
            "Second extended End Date",
            "Contractual",
            "Latest date before termination rights arise.",
            "No",
            c("C222"),
        ),
    ]
    h.table(
        "cp1a.transactions_events",
        [
            {
                "event_date": d,
                "event": e,
                "status": s,
                "credit_relevance": r,
                "perimeter_change": p,
                "cite": ck,
            }
            for d, e, s, r, p, ck in ev
        ],
    )
    h.table("cp1a.ratings_register", ratings)

    text = (
        "Four facts matter most to a creditor. Caesars is a large, lease-heavy and gaming-led operator whose Las Vegas segment is weakening while Regional grows partly through the Windsor consolidation; "
        "it has agreed to a US$31.00 cash take-private by Fertitta Gaming Holdco that is conditional and still pending, and the size of the new debt is not stated in the sources. {1, 2, 3, 18, 27}\n\n"
        "Operating model. FY2025 net revenue was US$11.486bn, led by casino at US$6.617bn, with hotel US$1.945bn, food and beverage US$1.714bn and other US$1.210bn. H1 2026 revenue rose to US$5.863bn from US$5.701bn while Adjusted EBITDA fell to US$1.807bn from US$1.839bn. "
        "For creditors, hold, visitation, labour, taxes and rent decide how much revenue reaches cash. {12, 13, 14, 15, 6, 16}\n\n"
        "Transaction and ownership. The signed agreement keeps Caesars as a wholly owned subsidiary of Parent after the merger. The Carano family, with about 5%, rolls part of its stake. A US$200m company termination fee and a US$450m reverse fee apply in defined cases, and Parent's financing is not a closing condition. "
        "Funding terms, schedules and post-close capitalisation are not in the pack, so no closing probability is inferred"
        + (
            " and pro forma leverage rests on the three synthetic tranches of this test run"
            if is_primary(ctx, run_id)
            else " and no pro forma leverage is inferred"
        )
        + ". {3, 5, 28}\n\n"
        "Governance view: Medium and incomplete. Reporting is audited and regular, and no repurchases were made in H1 2026, but acquisitions, a US$229m 2025 buyback and a small related-party lease are monitored items. {20, 21, 22, 23}\n\n"
        "Ratings: the pack shows issue ratings only, from FINRA (Moody's B1 and S&P BB- on the secured 2032s, Caa1 and B- on the unsecured 2032s). The corporate family rating B1 negative and S&P BB- on CreditWatch negative in the register are synthetic test values, marked as such, because no agency report was supplied. "
        "The downside path is a merger delay or weaker Las Vegas trading consuming cash while debt service and rent persist; the disclosed US$10m of merger costs is the first visible cost. {27, 24}"
    )
    h.analysis(caos_text(h, FOLDER, "CP-1A", text))
    h.gaps(
        "- Corporate family rating, outlooks and Fitch: no agency report in the pack (G10, G11). The register rows for the corporate family rating and outlooks are synthetic test values. Source: current agency reports.\n"
        "- Merger debt: amount, ranking and banks not stated (G8, G9); the sources say only 10 banks."
        + merger_debt_tail(ctx, run_id)
        + f" Effect: {post_close_leverage(ctx, run_id)}. Source: the debt commitment letters.\n"
        "- Post-close ownership, rollover final share count and sponsor equity: not in the sources. Effect: sponsor quality is a Medium, incomplete view. Source: the agreement schedules and financing papers.\n"
        "- Morningstar issuer id: not in the pack."
    )
    return h
