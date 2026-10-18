"""CZR CP-0: source readiness. The inventory is the real corpus (names, dates, sha256 from the files themselves);
the analysis is adapted from the real CAOS CP-0. Only the Run Brief tranche pre-fill (Primary) is synthetic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core import CORPUS_DIR, GAP, Ctx, Handoff, compute, fx
from czr.cp_3 import merger_debt_tail
from helpers import caos_text

FOLDER = "full-credit-assessment-2026-10-06"
FACTS = json.loads((Path(__file__).resolve().parent.parent / "synthetic-facts.json").read_text())[
    "czr"
]
FIX = "czr/cp_0.py"

TRACE_C = "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt"
CZR_NAME = "Caesars Entertainment, Inc."
FUND = "Federated Hermes Sustainable High Yield Bond Fund, Inc."

# file -> class, type, entity named, matches borrower, period, document date, pages (page-mapped only), note
INVENTORY: list[tuple[str, str, str, str, str, str, str, str, str]] = [
    (
        "CZR_FY2025_10K.txt",
        "issuer",
        "Annual report",
        CZR_NAME,
        "Yes",
        "FY2025",
        "2026-02-17",
        GAP,
        "Audited annual report; the historical baseline.",
    ),
    (
        "CZR_Q2_2026_10Q.txt",
        "issuer",
        "Quarterly report",
        CZR_NAME,
        "Yes",
        "Q2 2026",
        "2026-07-28",
        GAP,
        "Latest company financial period; unaudited; nothing after 30 June 2026.",
    ),
    (
        "CZR_Q2_2026_Earnings_Release.txt",
        "issuer",
        "Earnings release",
        CZR_NAME,
        "Yes",
        "Q2 2026",
        "2026-07-28",
        GAP,
        "Supplemental to the 10-Q; segment and Adjusted EBITDA reconciliation.",
    ),
    (
        "CZR_2026_Merger_Agreement.txt",
        "issuer",
        "Other",
        CZR_NAME,
        "Yes",
        "—",
        "2026-05-27",
        GAP,
        "Execution version of the Agreement and Plan of Merger; schedules absent.",
    ),
    (
        "CZR_2026_Merger_Agreement_8K.txt",
        "issuer",
        "Other",
        CZR_NAME,
        "Yes",
        "—",
        "2026-05-28",
        GAP,
        "Form 8-K summarising the merger; commitment letters not attached.",
    ),
    (
        "CZR_2026_Merger_Press_Release.txt",
        "issuer",
        "Other",
        CZR_NAME,
        "Yes",
        "—",
        "2026-05-28",
        GAP,
        "Announcement of the take-private; secondary to the agreement.",
    ),
    (
        "CZR_2024_650_Senior_Secured_Notes_2032_Indenture.txt",
        "issuer",
        "Indenture",
        CZR_NAME,
        "Yes",
        "—",
        "2024-02-06",
        "60",
        "Page map only (32 leading lines per page): degraded; attach by page range.",
    ),
    (
        "CZR_2024_650_Notes_First_Supplemental_Indenture.txt",
        "issuer",
        "Indenture",
        CZR_NAME,
        "Yes",
        "—",
        "2024-03-01",
        GAP,
        "Adds two guarantors; kept apart from the base indenture.",
    ),
    (
        "CZR_2024_650_Notes_Second_Supplemental_Indenture.txt",
        "issuer",
        "Indenture",
        CZR_NAME,
        "Yes",
        "—",
        "2024-08-23",
        GAP,
        "Guarantor joinders (Schedule A).",
    ),
    (
        "CZR_2024_Credit_Agreement_Incremental_Assumption_No3.txt",
        "issuer",
        "Credit agreement",
        CZR_NAME,
        "Yes",
        "—",
        "2024-02-06",
        "67",
        "Page map only (24 leading lines per page): degraded; carries the US$2.9bn Term B-1 and partial conformed text.",
    ),
    (
        "CZR_2024_Credit_Agreement_Fourth_Amendment.txt",
        "issuer",
        "Credit agreement",
        CZR_NAME,
        "Yes",
        "—",
        "2024-05-09",
        GAP,
        "Predecessor amendment; superseded in part by the fifth.",
    ),
    (
        "CZR_2024_Credit_Agreement_Fifth_Amendment.txt",
        "issuer",
        "Credit agreement",
        CZR_NAME,
        "Yes",
        "—",
        "2024-11-25",
        GAP,
        "Term B and B-1 repricing; not the full current credit agreement.",
    ),
    (
        TRACE_C,
        "market",
        "Bond report",
        CZR_NAME,
        "Yes",
        "—",
        "2026-10-02",
        GAP,
        "FINRA last trade of 1 October 2026 (6.50% secured 2032s); no bid, ask or size.",
    ),
    (
        "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt",
        "market",
        "Bond report",
        CZR_NAME,
        "Yes",
        "—",
        "2026-10-02",
        GAP,
        "FINRA last trade of 1 October 2026 (6.00% unsecured 2032s); no bid, ask or size.",
    ),
    (
        "MGM_FINRA_TRACE_552953CK5_2026-10-02.txt",
        "market",
        "Bond report",
        "MGM Resorts International",
        "No",
        "—",
        "2026-10-02",
        GAP,
        "Peer bond observation; not Caesars evidence.",
    ),
    (
        "PENN_FINRA_TRACE_707569AV1_2026-10-02.txt",
        "market",
        "Bond report",
        "PENN Entertainment, Inc.",
        "No",
        "—",
        "2026-10-02",
        GAP,
        "Peer bond observation; not Caesars evidence.",
    ),
    (
        "MGM_Q2_2026_Earnings_Release.txt",
        "issuer",
        "Earnings release",
        "MGM Resorts International",
        "No",
        "Q2 2026",
        "2026-07-29",
        GAP,
        "Peer release; Adjusted EBITDA definition differs from Caesars'.",
    ),
    (
        "PENN_Q2_2026_Earnings_Release.txt",
        "issuer",
        "Earnings release",
        "PENN Entertainment, Inc.",
        "No",
        "Q2 2026",
        "2026-08-06",
        GAP,
        "Peer release; reports triple-net lease expense separately.",
    ),
    (
        "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt",
        "portfolio",
        "Portfolio positions",
        FUND,
        "No",
        "—",
        "2026-06-30",
        GAP,
        "Real fund holdings at 30 June 2026 (includes four Caesars positions); basis of the Indexed HY test book.",
    ),
    (
        "FHSUHY_Prospectus_and_SAI_2026-05-26.txt",
        "portfolio",
        "Portfolio limits",
        FUND,
        "No",
        "—",
        "2026-05-26",
        "64",
        "Page map only (49 leading lines per page): degraded; investment policy context.",
    ),
    (
        "TEST_CLO_I_Mandate_and_Exposures_2026-10-02.txt",
        "portfolio",
        "Portfolio limits",
        "Test CLO I Ltd (synthetic)",
        "No",
        "—",
        "2026-10-02",
        GAP,
        "Synthetic test mandate with exposure report (positions and limits); no figure is a real holding.",
    ),
]


def _sha(file: str) -> str:
    return hashlib.sha256((CORPUS_DIR / file).read_bytes()).hexdigest()


def _prefill(ctx: Ctx, h: Handoff, rb: Handoff) -> list[dict]:
    q_trace = h.cite_doc_find(TRACE_C, "Observed at: 2026-10-02")
    m_q = h.cite_doc_find("CZR_Q2_2026_10Q.txt", "For the quarterly period ended June 30, 2026")
    ev = ctx.val("merger_transaction_value") * 1000
    mult, calc = compute(
        "merger EV over LTM Adjusted EBITDA",
        "ev / ebitda",
        4,
        "x",
        ev=ev,
        ebitda=ctx.val("ltm_adj_ebitda_q2_2026"),
    )
    ev_mark = h.cite_data("C212")
    primary = rb.rows("snapshot.run_header")[0]["primary"] == "Yes"
    rows = [
        {"field": "issuer", "value": CZR_NAME, "status": "Sourced", "cite": h.cite_data("C1")},
        {"field": "issuer_id", "value": "CZR", "status": "Sourced", "cite": h.cite_data("C2")},
        {"field": "as_of_date", "value": "2026-10-02", "status": "Sourced", "cite": q_trace},
        {"field": "reporting_period", "value": "Q2 2026", "status": "Sourced", "cite": m_q},
        {
            "field": "objective",
            "value": "Assess Caesars' credit profile ahead of the Fertitta take-private financing",
            "status": "Analyst-asserted",
        },
        {"field": "morningstar_issuer_id", "value": GAP, "status": "Gap"},
        {
            "field": "ssim_ev_multiple",
            "value": fx(mult, 4),
            "status": "Sourced",
            "cite": f"{ev_mark} {calc}",
        },
        {"field": "primary", "value": "Yes" if primary else "No", "status": "Analyst-asserted"},
    ]
    if primary:
        syn = h.cite_synthetic(
            "merger_tranches",
            "The merger's committed debt is unstated in the sources (G8), so the analyst supplies three plausible tranches priced near Caesars' own secured and unsecured levels.",
            "Caesars",
            file="synthetic-facts.json",
        )
        for t in FACTS["merger_tranches"]["tranches"]:
            rows.append(
                {
                    "field": "transaction_summary",
                    "tranche_id": t["tranche_id"],
                    "value": f"{t['instrument']}, US${int(t['size']):,}m, {t['price_talk']}, OID {t['oid']}, due {t['maturity_date']}",
                    "status": "Analyst-asserted",
                    "cite": syn,
                }
            )
    else:
        rows.append({"field": "transaction_summary", "value": GAP, "status": "Gap"})
    return rows


def _questions(h: Handoff, rb: Handoff) -> list[dict]:
    questions = rb.rows("brief.research_questions")
    if (
        not questions
    ):  # Quick depth: no approved questions, so no synthetic row is registered or cited
        return []
    syn = h.cite_synthetic(
        "deep_research",
        "No fetched sources exist in the pack, so three plausible approved questions illustrate Deep Research.",
        "Caesars",
        file="synthetic-facts.json",
    )
    why = {
        "RQ1": (
            "Visitation and room-rate trends test whether the Q2 Las Vegas decline is cyclical or structural.",
            "Strip RevPAR, visitation and table-games volume for 2026 against 2025, from public sources.",
        ),
        "RQ2": (
            "Approval states and timing set the merger end date and the cost of delay.",
            "Gaming regulators' approval lists and timetables for each state where Caesars is licensed.",
        ),
        "RQ3": (
            "Peers' online margins show whether Caesars Digital's Q2 margin fall is sector-wide.",
            "Peer online sports betting margins and state tax changes, 2025 to 2026.",
        ),
    }
    out = []
    for r in questions:
        w, e = why[r["question_id"]]
        out.append(
            {
                "question_id": r["question_id"],
                "question": r["question"],
                "why_it_matters": f"{w} {syn}",
                "consumer_module": r["consumer_module"],
                "evidence_needed": e,
            }
        )
    return out


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(ctx, "CP-0", "CZR", run_id, "2026-10-02", [], fixture_file=FIX)
    h.qa("Restricted")
    rb = ctx.get(run_id, "RUN_BRIEF")
    h.table(
        "cp0.source_inventory",
        [
            {
                "file": f,
                "class": cls,
                "document_type": dt,
                "entity_named": ent,
                "entity_match": match,
                "period_covered": period,
                "document_date": date,
                "readable": "Yes",
                "image_read": "No",
                "pages": pages,
                "sha256": _sha(f),
                "note": note,
            }
            for f, cls, dt, ent, match, period, date, pages, note in INVENTORY
        ],
    )
    h.table("cp0.run_brief_prefill", _prefill(ctx, h, rb))
    h.table("cp0.research_questions", _questions(h, rb))
    h.table(
        "cp0.prior_case",
        [
            {
                "file": r["file"],
                "report_date": r["report_date"],
                "run_id": r["run_id"],
                "pathway": FACTS["prior_case"]["pathway"],
                "depth": FACTS["prior_case"]["depth"],
                "offered": "Yes",
            }
            for r in rb.rows("brief.prior_case")
        ],
    )
    h.table(
        "cp0.portfolios",
        [
            {
                k: r[k]
                for k in (
                    "portfolio_id",
                    "portfolio_name",
                    "strategy",
                    "positions_file",
                    "limits_file",
                    "as_of_date",
                )
            }
            for r in rb.rows("brief.portfolios")
        ],
    )

    n_files = len(INVENTORY)
    n_map = sum(1 for r in INVENTORY if r[7] != GAP)
    text = (
        f"Yes, with limitations: the Source Pack supports a source-grounded review of Caesars' operating history, Q2 2026 results, reported debt and liquidity, selected note terms, the pending merger and a few public bond observations, but it is not a complete underwriting pack. "
        f"Of the {n_files} prepared files, {n_files - n_map} were delivered whole and {n_map} as page maps; none is Blocked. Readiness is Restricted. {{19, 9, 4}}\n\n"
        "The period boundary is the first limit. The FY2025 10-K and the 30 June 2026 10-Q give audited annual and unaudited interim figures; there is no Q3 filing or later operating update, so June figures must not be read as October figures. {19, 9, 4}\n\n"
        "The legal and debt limits come next. The base 2032 secured indenture, the Incremental Assumption Agreement No. 3 and the fund prospectus are page-mapped. The supplemental indentures and the fourth and fifth credit amendments are present, but the complete current CEI Credit Agreement and the collateral and intercreditor package are not, so covenant capacity and security cannot be established from this pack. The 10-K reports US$11.9bn of indebtedness and about US$1.4bn of 2026 VICI and GLPI rent; the 10-Q reports debt-table figures and long-term financing obligations. Face principal, carrying value and financing obligations are distinct bases. {21, 22, 23}\n\n"
        "Market evidence is thin. The four FINRA pages show 1 October last trades, not bids or evaluated prices, and the fund schedule values a Caesars secured-note position at 30 June. The merger agreement and 8-K give the US$31.00 cash price, but the debt commitment papers, schedules and the amount of new debt are not in the pack. {28, 29, 27, 10, 12}\n\n"
        "Source hierarchy: filed reports and executed legal documents control facts and terms; issuer releases supplement them; FINRA pages and the fund schedule are dated market context; nothing outside the pack is used. The portfolio files are a synthetic Test CLO I mandate and a real fund schedule used only to build a synthetic Indexed HY book."
    )
    h.analysis(caos_text(h, FOLDER, "CP-0", text))
    h.gaps(
        "- Complete current CEI Credit Agreement and collateral and intercreditor documents: not in the pack. Covenant capacity, security and recovery cannot be established. Source that would lift it: the conformed agreement and security documents.\n"
        "- Post-June 2026 company reporting: none delivered. Current liquidity, leverage and merger status are unverified. Source: the next 10-Q and a current debt and cash schedule.\n"
        "- Merger financing commitment papers and schedules: not in the pack (G8). The size and ranking of the new debt are unknown."
        + merger_debt_tail(ctx, run_id)
        + " Source: the debt commitment letters.\n"
        "- Market data: last trades only, no bid, ask, size or benchmark curve (G18, G19). Spreads and relative value are indicative. Source: dealer or evaluated prices and a Treasury curve.\n"
        "- Morningstar issuer id: not in the pack. The field stays blank in the Run Brief."
    )
    return h
