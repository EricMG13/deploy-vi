"""Larchmere CP-5: evidence trace. Statuses are read from the handoffs already built, so the table cannot drift from them."""

from __future__ import annotations

from core import Ctx, Handoff

from . import derived as X
from . import facts as F
from .facts import syn

ORDER = [
    "CP-0",
    "CP-1",
    "CP-1A",
    "CP-1D",
    "MODEL",
    "CP-2",
    "CP-2A",
    "CP-4",
    "CP-2D",
    "CP-2G",
    "PROJECTION",
    "CP-2H",
    "CP-3D",
    "CP-3C",
    "CP-4C",
    "CP-3",
    "FIT",
]
TRACE = {
    "CP-2H": "Partly traceable",
    "CP-3D": "Partly traceable",
    "CP-3C": "Partly traceable",
    "CP-4C": "Partly traceable",
    "CP-3": "Partly traceable",
}
NOTE = {
    "CP-2H": "Blocked: no rating-agency report admitted; the table rows carry no extracted value.",
    "CP-3D": "Single-dealer quotes, one file dated 1 October 2026.",
    "CP-3C": "Sources are the base-case projection; creditor-group evidence is absent.",
    "CP-4C": "Enterprise values rest on analyst multiples and the company's asset appraisal.",
    "CP-3": "Talk for the new-money loan is not a market level; peers are synthetic.",
    "CP-4": "Document summaries, not executed documents, for the master lease and intercreditor.",
    "CP-2G": "Drivers are the analyst's; management gave totals only.",
}
LIMITS = {
    "CP-0": (
        "No rating-agency report, valuation or lender-group term sheet in the pack.",
        "Ratings are unsourced beyond a market file; EV is analyst-set.",
        "Agency reports; an adviser's valuation.",
    ),
    "CP-1": (
        "Half-year cash flows only; no quarterly detail; no listed equity value.",
        "No quarterly cash conversion; EV uses a Run Brief multiple.",
        "Quarterly cash-flow statements.",
    ),
    "CP-1A": (
        "Management and competitor data absent.",
        "Governance and market-share views rest on the company's own statements.",
        "Proxy-style disclosure; gaming-board market reports.",
    ),
    "CP-1D": (
        "No detail behind the run-rate savings.",
        "The savings are rejected, so SSIM EBITDA is below the stated figure.",
        "The management savings plan.",
    ),
    "CP-2": (
        "One set of company documents and one dealer file.",
        "Credit score confidence is Medium.",
        "Independent sources.",
    ),
    "CP-2A": (
        "Flow-through of 45% is an analyst assumption; no hedge disclosure.",
        "Sensitivities bracket rather than replicate.",
        "Segment cost data; derivative note.",
    ),
    "CP-4": (
        "Master lease and intercreditor are read from summaries.",
        "Lease termination and standstill mechanics are uncertain.",
        "The executed documents.",
    ),
    "CP-2D": (
        "No management 13-week cash flow.",
        "The pinch month is an estimate.",
        "The 13-week cash flow.",
    ),
    "CP-2G": (
        "Management forecast totals only.",
        "Cases are analyst cases.",
        "The management model.",
    ),
    "CP-2H": (
        "Blocked: no rating-agency report admitted.",
        "No rating-trigger headroom or migration timing.",
        "A Moody's or S&P report.",
    ),
    "CP-3D": (
        "Single dealer; no second quote.",
        "Implied PD is indicative.",
        "A second dealer or trade prints.",
    ),
    "CP-3C": (
        "No creditor-group or cooperation-agreement evidence.",
        "Ability of excluded lenders to resist an uptier is unclear.",
        "Lender-group filings.",
    ),
    "CP-4C": (
        "Analyst multiples; master lease assumed; no independent valuation.",
        "Recoveries move one-for-one with EV.",
        "An adviser's valuation; the landlord's position.",
    ),
    "CP-3": (
        "Talk is not a market level; peers are synthetic.",
        "The new-money Valuation is conditional.",
        "Final terms; a vendor peer set.",
    ),
    "MODEL": (
        "Stated and SSIM EBITDA differ; no listed equity value.",
        "Leverage is shown on SSIM EBITDA beside the stated figure.",
        "A CP-1D ruling accepted by the analyst.",
    ),
    "PROJECTION": (
        "Projected years open from June 2026 balances; 2028 maturities assumed refinanced.",
        "The first-year gap is overstated against a half-year; negative cash is an unfunded gap.",
        "A quarterly model.",
    ),
}


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-5",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", *ORDER],
        fixture_file="larchmere/cp_5.py",
    )
    h.qa("Pass")
    m_rat = syn(h, "ratings")
    X.require(ctx, run_id, *ORDER)
    built = {s: ctx.get(run_id, s) for s in ORDER}
    h.table(
        "cp5.module_status",
        [
            {
                "module_id": s,
                "qa_status": b.qa_status,
                "traceability": TRACE.get(s, "Traceable"),
                "note": NOTE.get(s),
            }
            for s, b in built.items()
        ],
    )
    h.table(
        "cp5.findings",
        [
            {
                "finding_id": "F1",
                "severity": "High",
                "module_id": "CP-2H",
                "kind": "Lineage",
                "description": "No rating-agency report was admitted, so trigger thresholds cannot be traced.",
                "required_fix": "Admit a Moody's or S&P report.",
                "status": "Open",
            },
            {
                "finding_id": "F2",
                "severity": "Medium",
                "module_id": "CP-3D",
                "kind": "Market",
                "description": "All market levels come from one dealer file.",
                "required_fix": "Add a second dealer source or trade prints.",
                "status": "Open",
            },
            {
                "finding_id": "F3",
                "severity": "Medium",
                "module_id": "CP-4",
                "kind": "Consistency",
                "description": "Covenant EBITDA (stated Adjusted EBITDA less cash rent) differs from the Model's SSIM EBITDA.",
                "required_fix": "None: both definitions are labelled in CP-1 and CP-4.",
                "status": "Accepted",
            },
            {
                "finding_id": "F4",
                "severity": "Low",
                "module_id": "PROJECTION",
                "kind": "Calculation",
                "description": "FY2026E carries a full year of flows from June 2026 balances, which overstates the first-year gap.",
                "required_fix": "None for design; a live run would use a quarterly model.",
                "status": "Accepted",
            },
        ],
    )
    h.table(
        "cp5.limitations",
        [
            {
                "module_id": s,
                "limitation": lim,
                "effect_on_decision": eff,
                "source_that_would_lift": src,
            }
            for s, (lim, eff, src) in LIMITS.items()
        ],
    )
    n_restricted = sum(1 for b in built.values() if b.qa_status == "Restricted")
    h.analysis(
        f"The analysis is traceable enough for a screening-level stance and not for committing capital. {len(built)} upstream handoffs were checked: {len(built) - n_restricted - 1} Pass, {n_restricted} Restricted and 1 Blocked (CP-2H). "
        "In this design run every figure cites a labelled synthetic input; in a live run the same table would resolve to pack files. "
        f"The provenance gap that matters most is the missing rating-agency report: ratings are evidenced only by a market file {m_rat} and the trigger thresholds are untraceable.\n\n"
        "The second gap is valuation: every recovery moves one-for-one with an analyst multiple because no independent valuation was admitted, so the fulcrum conclusion is conditional. The third is market evidence from a single dealer.\n\n"
        "Four findings are recorded: two open (agency report, single dealer) and two accepted (the labelled covenant-EBITDA definition and the half-year overstatement in the first projected year). Confidence is Medium."
    )
    h.gaps(
        "- Rating-agency report: not admitted; CP-2H Blocked. Lifted by: a Moody's or S&P report.\n"
        "- Independent valuation: none. Lifted by: an adviser's report.\n"
        "- Second market source: none. Lifted by: a second dealer file."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
