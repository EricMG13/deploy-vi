"""Larchmere RUN_BRIEF (interfaces §3.1): run header, transaction summary (the sponsor's NEW-1 priming loan, so the run is
Primary), brief fields, portfolio, approval. No research question is approved and
no Prior Case exists, so CP-DR and CP-8 are skipped; the approval acknowledges the Blocked CP-2H."""

from __future__ import annotations

import hashlib
import json

from core import GAP, Ctx, D, Handoff, fx, plain

from . import facts as F
from .facts import syn

EV_MULTIPLE = "7.25"


def build(
    ctx: Ctx,
    run_id: str,
    variant: str,
    pathway: str = "DISTRESSED_RESTRUCTURING",
    depth: str = "full",
) -> Handoff:
    h = Handoff(
        ctx,
        "RUN_BRIEF",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0"],
        fixture_file="larchmere/run_brief.py",
    )
    h.qa("Restricted")
    m_prof = syn(h, "profile")
    m_mult = syn(h, "ev_multiples")
    mult = D(F.val("ev_multiples")["base"])
    assert fx(mult) == EV_MULTIPLE + "x"
    h.table(
        "snapshot.run_header",
        [
            {
                "run_id": run_id,
                "issuer": F.ISSUER,
                "issuer_id": F.ISSUER_ID,
                "as_of_date": F.AS_OF,
                "objective": F.OBJECTIVE,
                "analyst": F.ANALYST,
                "pathway": pathway,
                "depth": depth,
                "primary": "Yes",
                "currency": "USD",
                "unit": "MILLIONS",
                "morningstar_issuer_id": GAP,
                "ssim_ev_multiple_x": fx(mult),
                "report_date": F.REPORT_DATE,
            }
        ],
    )
    nm = F.val("new_money")
    m_new = syn(h, "new_money")
    h.table(
        "snapshot.transaction_summary",
        [
            {
                "tranche_id": nm["tranche_id"],
                "borrower": F.ISSUER,
                "instrument": nm["instrument"],
                "debt_type": "1L Term Loan",
                "use_of_proceeds": "Other",
                "size": plain(nm["size"]),
                "currency": "USD",
                "unit": "MILLIONS",
                "price_talk": f"SOFR + {nm['spread_low']}-{nm['spread_high']} bps",
                "talk_stage": "Initial talk",
                "oid": plain(D(nm["oid"]), 2),
                "maturity_date": nm["maturity"],
                "expected_ratings": nm["expected_ratings"],
                "commitment_date": GAP,
                "status": "Analyst-asserted",
                "analyst_value": f"SOFR + {nm['spread_mid']} bps",
                "cite": m_new,
            }
        ],
    )
    p = F.val("portfolio")
    fields = [
        ("issuer", F.ISSUER, "Sourced", GAP, m_prof),
        ("issuer_id", F.ISSUER_ID, "Sourced", GAP, m_prof),
        ("as_of_date", F.AS_OF, "Analyst-asserted", F.AS_OF, GAP),
        ("objective", F.OBJECTIVE, "Analyst-asserted", F.OBJECTIVE, GAP),
        ("analyst", F.ANALYST, "Analyst-asserted", F.ANALYST, GAP),
        ("primary", "Yes", "Analyst-asserted", "Yes", GAP),
        ("pathway", pathway, "Analyst-asserted", pathway, GAP),
        ("depth", depth, "Analyst-asserted", depth, GAP),
        ("morningstar_issuer_id", GAP, "Gap", GAP, GAP),
        ("ssim_ev_multiple", fx(mult), "Analyst-asserted", fx(mult), m_mult),
        ("transaction_summary", "see snapshot.transaction_summary", "Analyst-asserted", GAP, GAP),
        ("portfolios", p["id"], "Sourced", GAP, GAP),
        ("research_questions", GAP, "Gap", GAP, GAP),
        ("prior_case", GAP, "Gap", GAP, GAP),
    ]
    h.table(
        "brief.run_brief_fields",
        [
            {"field": f, "value": v, "status": s, "analyst_value": av, "cite": c}
            for f, v, s, av, c in fields
        ],
    )
    h.table(
        "brief.portfolios",
        [
            {
                "portfolio_id": p["id"],
                "portfolio_name": p["name"],
                "strategy": "CLO",
                "positions_file": "FENWICK_CLO_Positions_2026-09-30.csv",
                "limits_file": "FENWICK_CLO_Indenture_Limits_2026-09-30.txt",
                "as_of_date": "2026-09-30",
                "prepared_json": "prepared/portfolios/FENWICK_CLO.json",
            }
        ],
    )
    h.table("brief.research_questions", [])
    h.table("brief.prior_case", [])
    sha = hashlib.sha256(
        json.dumps(h.tables["brief.run_brief_fields"], sort_keys=True).encode()
    ).hexdigest()
    h.table(
        "brief.approval",
        [
            {
                "approved_at": "2026-10-02T09:30:00Z",
                "analyst": F.ANALYST,
                "pathway": pathway,
                "depth": depth,
                "primary": "Yes",
                "deep_research": "No",
                "prior_case": "No",
                "pathway_grade": "With limitations",
                "acknowledged_blocked_modules": "CP-2H",
                "brief_sha256": sha,
            }
        ],
    )
    h.analysis(
        f"The Run Brief fixes the scope: issuer {F.ISSUER} {m_prof}, as of 2 October 2026, USD millions, Distressed & Restructuring at full depth. "
        f"The SSIM EV multiple of {fx(mult)} is the analyst's base going-concern multiple of LTM Adjusted EBITDA {m_mult}; no listed equity value exists because the sponsor owns the company. "
        f"The run is Primary because the sponsor's {plain(nm['size'])} super-priority priming loan (NEW-1) is the pending transaction {m_new}. "
        "No Deep Research question was approved and no earlier Report exists, so CP-DR and CP-8 do not run; the analyst acknowledged that CP-2H is Blocked."
    )
    h.gaps(
        "- Morningstar issuer id: not in the Source Pack.\n"
        "- Transaction summary: NEW-1, the sponsor's super-priority rescue loan, is a proposal at initial talk, not a committed tranche; its size, spread, OID and expected rating are synthetic and there is no commitment date.\n"
        "- Research questions and Prior Case: none approved or found."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
