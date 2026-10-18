"""Larchmere CP-0: source classification and readiness for the Distressed & Restructuring run (all files fictional)."""

from __future__ import annotations

import hashlib

from core import GAP, Ctx, Handoff

from . import facts as F
from .facts import syn

# file, class, document type, period, date, pages, readable, image_read, note
FILES = [
    (
        "LLG_FY2025_Annual_Report.txt",
        "issuer",
        "Annual report",
        "FY2025",
        "2026-03-12",
        "148",
        "Yes",
        "No",
        "Audited statements; segment note; debt note; master lease note.",
    ),
    (
        "LLG_Q2_2026_Quarterly_Report.txt",
        "issuer",
        "Quarterly report",
        "H1 2026",
        "2026-08-14",
        "71",
        "Yes",
        "No",
        "Unaudited interim; liquidity section; going-concern language added.",
    ),
    (
        "LLG_Q2_2026_Lender_Presentation.txt",
        "issuer",
        "Lender presentation",
        "LTM Q2 2026",
        "2026-08-20",
        "34",
        "Yes",
        "No",
        "Management forecast to 2028 and the sponsor's covenant EBITDA bridge.",
    ),
    (
        "LLG_First_Lien_Credit_Agreement_2025_Amendment.txt",
        "issuer",
        "Credit agreement",
        GAP,
        "2025-06-30",
        "212",
        "Yes",
        "No",
        "Revolver, term loan B and second-lien terms as amended; covenant and basket definitions.",
    ),
    (
        "LLG_2029_Notes_Indenture.txt",
        "issuer",
        "Indenture",
        GAP,
        "2022-09-15",
        "168",
        "Yes",
        "No",
        "8.25% Senior Notes due 2029; events of default and grace periods.",
    ),
    (
        "LLG_Master_Lease_Summary.txt",
        "issuer",
        "Other",
        GAP,
        "2022-09-01",
        "19",
        "Yes",
        "No",
        "Summary of the master lease with the landlord: rent, escalator, cross-default.",
    ),
    (
        "LLG_Q2_2026_Compliance_Certificate.txt",
        "issuer",
        "Other",
        "Q2 2026",
        "2026-09-21",
        "6",
        "Yes",
        "No",
        "Delivered late under an Agent extension; shows the first-lien net leverage test at 30 June 2026.",
    ),
    (
        "LLG_Notice_of_Non_Payment_2026-09-16.txt",
        "issuer",
        "Other",
        GAP,
        "2026-09-16",
        "2",
        "Yes",
        "No",
        "Notice that the 15 September 2026 coupon on the notes was not paid; the 30-day grace period runs to 15 October.",
    ),
    (
        "LLG_Market_Levels_2026-10-01.csv",
        "market",
        "Market levels export",
        GAP,
        "2026-10-01",
        GAP,
        "Yes",
        "No",
        "Single-dealer quotes for the term loan B, second-lien term loan and notes; agency ratings.",
    ),
    (
        "FENWICK_CLO_Positions_2026-09-30.csv",
        "portfolio",
        "Portfolio positions",
        GAP,
        "2026-09-30",
        GAP,
        "Yes",
        "No",
        "One position in the issuer: 11.2m par of the term loan B.",
    ),
    (
        "FENWICK_CLO_Indenture_Limits_2026-09-30.txt",
        "portfolio",
        "Portfolio limits",
        GAP,
        "2026-09-30",
        "9",
        "Yes",
        "No",
        "Single-issuer, CCC, second-lien and sector limits.",
    ),
]


def _sha(name: str) -> str:
    return hashlib.sha256(("larchmere-fixture/" + name).encode()).hexdigest()


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(ctx, "CP-0", F.ISSUER_ID, run_id, F.AS_OF, [], fixture_file="larchmere/cp_0.py")
    h.qa("Restricted")
    m_prof, m_mkt = syn(h, "profile"), syn(h, "quotes")
    m_port = syn(h, "portfolio")
    h.table(
        "cp0.source_inventory",
        [
            {
                "file": f,
                "class": c,
                "document_type": dt,
                "entity_named": "Fenwick Park CLO Ltd (fictional)"
                if c == "portfolio"
                else F.ISSUER,
                "entity_match": "Yes",
                "period_covered": per,
                "document_date": d,
                "readable": rd,
                "image_read": ir,
                "pages": pg,
                "sha256": _sha(f),
                "note": note,
            }
            for f, c, dt, per, d, pg, rd, ir, note in FILES
        ],
    )
    prefill = [
        ("issuer", GAP, F.ISSUER, "Sourced", m_prof),
        ("issuer_id", GAP, F.ISSUER_ID, "Sourced", m_prof),
        ("as_of_date", GAP, F.AS_OF, "Analyst-asserted", GAP),
        ("objective", GAP, F.OBJECTIVE, "Analyst-asserted", GAP),
        ("morningstar_issuer_id", GAP, GAP, "Gap", GAP),
        ("portfolios", GAP, F.val("portfolio")["id"], "Sourced", m_port),
        ("market_levels_date", GAP, "2026-10-01", "Sourced", m_mkt),
        ("rating_agency_report", GAP, GAP, "Gap", GAP),
    ]
    h.table(
        "cp0.run_brief_prefill",
        [
            {"field": f, "tranche_id": t, "value": v, "status": s, "cite": c}
            for f, t, v, s, c in prefill
        ],
    )
    h.table(
        "cp0.research_questions",
        [
            {
                "question_id": "Q1",
                "question": "How have regional casino operators in comparable distress resolved master-lease burdens, and what did lessors concede?",
                "why_it_matters": "The 62 of rent ranks ahead of every funded creditor in practice, so what the lessor concedes sets the size of the debt problem.",
                "consumer_module": "CP-4C",
                "evidence_needed": "Fetched public precedents and lessor commentary.",
            },
            {
                "question_id": "Q2",
                "question": "What is the licensing and regulatory path for a Chapter 11 filing by a four-state gaming licensee?",
                "why_it_matters": "Gaming regulators can delay or condition a filing and any change of control, which bounds the timeline of the prepack.",
                "consumer_module": "CP-3C",
                "evidence_needed": "State gaming-control board rules and recent approvals.",
            },
        ],
    )
    h.table("cp0.prior_case", [])
    p = F.val("portfolio")
    h.table(
        "cp0.portfolios",
        [
            {
                "portfolio_id": p["id"],
                "portfolio_name": p["name"],
                "strategy": "CLO",
                "positions_file": "FENWICK_CLO_Positions_2026-09-30.csv",
                "limits_file": "FENWICK_CLO_Indenture_Limits_2026-09-30.txt",
                "as_of_date": "2026-09-30",
            }
        ],
    )
    h.analysis(
        f"The Source Pack supports the Distressed & Restructuring work for {F.ISSUER} with limitations: 8 issuer files, one market file and two portfolio files were classified, all readable and all naming the right entity {m_prof}. "
        f"The pack holds the credit agreement as amended, the notes indenture, the master-lease summary, the late compliance certificate and the non-payment notice, which are the documents a restructuring read needs. "
        f"Market evidence is a single dealer file dated 1 October 2026 {m_mkt}.\n\n"
        "The pack has no rating-agency report: ratings come from the market file only, so the rating-trigger module cannot establish agency thresholds and is expected to be Blocked. "
        f"The Source Pack also lacks an independent valuation and any lender-group intercreditor term sheet, so enterprise values rest on analyst multiples. "
        f"One portfolio was found, {p['name']}, holding a single position in the first-lien loan {m_port}. "
        "Two Deep Research questions were offered and not approved; no earlier Report was found."
    )
    h.gaps(
        "- Rating-agency report: none in the pack, so agency trigger thresholds are unknown; CP-2H is expected to be Blocked. Effect: no rating-trigger headroom. Lifted by: a Moody's or S&P rating report.\n"
        "- Independent valuation or lender-group term sheet: none provided. Effect: enterprise values use analyst multiples. Lifted by: an adviser's valuation.\n"
        "- Morningstar issuer id: not in the pack."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
