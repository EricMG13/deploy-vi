"""CZR RUN_BRIEF (interfaces §3.1): run header, transaction summary, brief fields, portfolios, research questions, Prior Case, approval."""

from __future__ import annotations

import hashlib
import json

from core import GAP, Ctx, Handoff, compute, fx
from czr.cp_3 import FACTS, cite_fact, is_primary

# Hook: Primary runs (the run's flag, not its variant name) carry the synthetic merger tranches (`czr.merger_tranches`) in the transaction summary.
RESEARCH_QUESTIONS = [
    (q["question_id"], q["question"], q["consumer_module"])
    for q in FACTS["deep_research"]["questions"]
]
PRIOR = FACTS["prior_case"]
PRIOR_FILE = "../20260805-czr-earnings-update/report.html"
PORTFOLIO_ROWS = {
    "TEST_CLO_I": {
        "portfolio_id": "TEST_CLO_I",
        "portfolio_name": "Test CLO I Ltd",
        "strategy": "CLO",
        "positions_file": "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt",
        "limits_file": "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt",
        "as_of_date": "2026-05-29",
        "prepared_json": "prepared/portfolios/TEST_CLO_I.json",
    },
    "TEST_HY_I": {
        "portfolio_id": FACTS["indexed_hy_book"]["portfolio_id"],
        "portfolio_name": FACTS["indexed_hy_book"]["portfolio_name"],
        "strategy": FACTS["indexed_hy_book"]["strategy"],
        "positions_file": "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt",
        "limits_file": "TEST_HY_I_Limits_2026-06-30.csv (synthetic)",
        "as_of_date": "2026-06-30",
        "prepared_json": "prepared/portfolios/TEST_HY_I.json",
    },
}
# portfolios attached per pathway (build-fixtures.py RUNS): the Portfolio Decision run attaches both; the Covenant
# and Earnings Update plans have no Fit step and no portfolio
PORTFOLIOS = {
    "FULL_CREDIT_ASSESSMENT": ["TEST_CLO_I"],
    "RELATIVE_VALUE": ["TEST_CLO_I"],
    "PORTFOLIO_DECISION": ["TEST_CLO_I", "TEST_HY_I"],
}
PATHWAY_LABEL = {"FULL_CREDIT_ASSESSMENT": "Full Credit Assessment"}


def transaction_tranches(ctx: Ctx, h: Handoff, run_id: str) -> list[dict]:
    """Rows for `snapshot.transaction_summary`: the three synthetic merger tranches (Primary runs only)."""
    if not is_primary(ctx, run_id):
        return []
    debt_type = {
        "Term loan": "1L Term Loan",
        "Senior secured notes": "SS Notes",
        "Senior unsecured notes": "SU Notes",
    }
    block = FACTS["merger_tranches"]
    rows = []
    for t in block["tranches"]:
        syn = cite_fact(h, "merger_tranches", t["tranche_id"])
        rows.append(
            {
                "tranche_id": t["tranche_id"],
                "borrower": "Caesars Entertainment, Inc.",
                "instrument": t["instrument"],
                "debt_type": debt_type[t["debt_type"]],
                "use_of_proceeds": block["use_of_proceeds"],
                "size": t["size"],
                "currency": "USD",
                "unit": "MILLIONS",
                "price_talk": t["price_talk"],
                "talk_stage": t["talk_stage"],
                "oid": t["oid"],
                "maturity_date": t["maturity_date"],
                "expected_ratings": t["expected_ratings"],
                "cr_score": t["cr_score"],
                "commitment_date": block["commitment_date"],
                "status": "Analyst-asserted",
                "analyst_value": t["price_talk"],
                "cite": syn,
            }
        )
    return rows


def build(
    ctx: Ctx,
    run_id: str,
    variant: str,
    pathway: str = "FULL_CREDIT_ASSESSMENT",
    depth: str = "full",
) -> Handoff:
    primary = is_primary(ctx, run_id)
    deep = depth == "full"
    prior = pathway == "EARNINGS_UPDATE"
    pf_ids = PORTFOLIOS.get(pathway, [])
    h = Handoff(
        ctx, "RUN_BRIEF", "CZR", run_id, "2026-10-02", ["CP-0"], fixture_file="czr/run_brief.py"
    )
    h.qa("Restricted")
    m_name, m_tick = h.cite_data("C1"), h.cite_data("C2")
    ev = ctx.val("merger_transaction_value") * 1000
    ev_mark = h.cite_data("C212")
    ltm = ctx.val("ltm_adj_ebitda_q2_2026")
    mult, mult_s = compute(
        "merger EV over LTM Adjusted EBITDA", "ev / ebitda", 4, "x", ev=ev, ebitda=ltm
    )
    h.table(
        "snapshot.run_header",
        [
            {
                "run_id": run_id,
                "issuer": ctx.figure("issuer.name")["raw"],
                "issuer_id": "CZR",
                "as_of_date": "2026-10-02",
                "objective": "Assess Caesars' credit profile ahead of the Fertitta take-private financing",
                "analyst": "Credit Research (design fixture)",
                "pathway": pathway,
                "depth": depth,
                "primary": "Yes" if primary else "No",
                "currency": "USD",
                "unit": "MILLIONS",
                "morningstar_issuer_id": GAP,
                "ssim_ev_multiple_x": fx(mult, 4),
                "report_date": "2026-10-17",
            }
        ],
    )
    h.table("snapshot.transaction_summary", transaction_tranches(ctx, h, run_id) if primary else [])
    fields = [
        ("issuer", ctx.figure("issuer.name")["raw"], "Sourced", GAP, m_name),
        ("issuer_id", "CZR", "Sourced", GAP, m_tick),
        ("as_of_date", "2026-10-02", "Analyst-asserted", "2026-10-02", GAP),
        (
            "objective",
            "Assess Caesars' credit profile ahead of the Fertitta take-private financing",
            "Analyst-asserted",
            "Assess Caesars' credit profile ahead of the Fertitta take-private financing",
            GAP,
        ),
        (
            "analyst",
            "Credit Research (design fixture)",
            "Analyst-asserted",
            "Credit Research (design fixture)",
            GAP,
        ),
        (
            "primary",
            "Yes" if primary else "No",
            "Analyst-asserted",
            "Yes" if primary else "No",
            GAP,
        ),
        ("pathway", pathway, "Analyst-asserted", pathway, GAP),
        ("depth", depth, "Analyst-asserted", depth, GAP),
        ("morningstar_issuer_id", GAP, "Gap", GAP, GAP),
        ("ssim_ev_multiple", fx(mult, 4), "Analyst-asserted", fx(mult, 4), f"{ev_mark} {mult_s}"),
        (
            "transaction_summary",
            "see snapshot.transaction_summary" if primary else GAP,
            "Analyst-asserted" if primary else "Gap",
            GAP,
            GAP,
        ),
        (
            "portfolios",
            "; ".join(pf_ids) if pf_ids else GAP,
            "Sourced" if pf_ids else "Gap",
            GAP,
            GAP,
        ),
        (
            "research_questions",
            "; ".join(q_[0] for q_ in RESEARCH_QUESTIONS) if deep else GAP,
            "Analyst-asserted" if deep else "Gap",
            GAP,
            GAP,
        ),
        (
            "prior_case",
            PRIOR_FILE if prior else GAP,
            "Sourced" if prior else "Gap",
            GAP,
            GAP,
        ),
    ]
    h.table(
        "brief.run_brief_fields",
        [
            {"field": f, "value": v, "status": s, "analyst_value": av, "cite": c}
            for f, v, s, av, c in fields
        ],
    )
    h.table("brief.portfolios", [PORTFOLIO_ROWS[i] for i in pf_ids])
    h.table(
        "brief.research_questions",
        [
            {"question_id": i, "question": t, "consumer_module": m, "approved": "Yes"}
            for i, t, m in RESEARCH_QUESTIONS
        ]
        if deep
        else [],
    )
    h.table(
        "brief.prior_case",
        [
            {
                "file": PRIOR_FILE,
                "report_date": PRIOR["report_date"],
                "run_id": PRIOR["prior_run_id"],
                "accepted": "Yes",
            }
        ]
        if prior
        else [],
    )
    sha = hashlib.sha256(
        json.dumps(h.tables["brief.run_brief_fields"], sort_keys=True).encode()
    ).hexdigest()
    h.table(
        "brief.approval",
        [
            {
                "approved_at": "2026-10-02T09:30:00Z",
                "analyst": "Credit Research (design fixture)",
                "pathway": pathway,
                "depth": depth,
                "primary": "Yes" if primary else "No",
                "deep_research": "Yes" if deep else "No",
                "prior_case": "Yes" if prior else "No",
                "pathway_grade": "With limitations",
                "acknowledged_blocked_modules": GAP,
                "brief_sha256": sha,
            }
        ],
    )
    h.analysis(
        f"The Run Brief fixes the scope: issuer {ctx.figure('issuer.name')['raw']} {m_name}, listed as {ctx.figure('issuer.ticker')['raw']} {m_tick}, as of 2 October 2026, USD millions. "
        f"The SSIM EV multiple of {fx(mult, 4)} is the merger transaction value of about US$17.6bn {ev_mark} over LTM Adjusted EBITDA; it is the Model's only EV input because no listed equity value is in the sources ({mult_s})."
    )
    if primary:
        syn_note = cite_fact(h, "merger_tranches")
        h.gaps(
            "- Morningstar issuer id: not in the Source Pack.\n"
            f"- Merger tranches: the new debt's terms are not stated in the sources (G8), so the three tranches in the transaction summary are synthetic test values {syn_note}. Lifted by: a term sheet or the commitment papers."
        )
    else:
        h.gaps(
            "- Morningstar issuer id: not in the Source Pack.\n- Merger tranches: the new debt's terms are not stated in the sources, so the transaction summary is empty until a term sheet is supplied."
        )
    return h
