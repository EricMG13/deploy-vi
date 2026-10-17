"""CZR CP-DR: Deep Research (three approved questions, `czr.deep_research`).

Real: the Q2 10-Q's own explanation of the Las Vegas decline, the FY2025 hotel occupancy, the merger agreement's closing
conditions, the reverse termination fee and the Caesars Digital margin move. Synthetic and marked: the fetched public
sources (`fetched/<nn>-<host>.example.md (synthetic)`) and the figures they carry (Las Vegas visitation, Strip RevPAR,
the approval calendar and one trade-press quote); the fetch layer did not run, so no fetched file exists.

"""

from __future__ import annotations

from core import Ctx, Handoff
from czr.cp_3 import AS_OF, FACTS, num
from helpers import join_marks

FOLDER = "full-credit-assessment-2026-10-06"
K10, MERGER8K = "CZR_FY2025_10K.txt", "CZR_2026_Merger_Agreement_8K.txt"
SYNTHETIC = {
    "fetched_01": (
        "fetched/01-lvcva-visitor-stats.example.md (synthetic): Las Vegas visitor volume fell 4.1% in the first eight months of 2026 against the same period of 2025.",
        "2026-09-24",
    ),
    "fetched_02": (
        "fetched/02-strip-hotel-metrics.example.md (synthetic): Strip RevPAR fell 3.4% year to date as room rates eased 1.9% and occupancy slipped 1.4 points.",
        "2026-09-29",
    ),
    "fetched_03": (
        "fetched/03-gaming-regulator-calendar.example.md (synthetic): the merger needs approval from gaming regulators in 12 of Caesars' 18 states, and the Nevada hearing is calendared for 17 December 2026.",
        "2026-09-18",
    ),
    "fetched_04": (
        "fetched/04-trade-press-osb.example.md (synthetic): a trade-press article quotes one peer's finance chief saying online sports betting margin fell about 2 points after a state tax increase.",
        "2026-09-10",
    ),
}


def _syn(h: Handoff, key: str) -> str:
    return h.cite_synthetic(key, SYNTHETIC[key][0], "Caesars", file="czr/cp_dr.py")


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-DR", "CZR", run_id, AS_OF, ["CP-0", "CP-1A", "CP-1"], fixture_file="czr/cp_dr.py"
    )
    h.qa("Restricted")
    qs = FACTS["deep_research"]["questions"]
    h.table(
        "cpdr.questions",
        [
            {
                "question_id": q["question_id"],
                "question": q["question"],
                "consumer_module": q["consumer_module"],
                "status": q["status"],
            }
            for q in qs
        ],
    )
    cm = lambda n: h.cite_caos(FOLDER, "CP-3", n)  # noqa: E731
    lv_text = cm(8)  # the 10-Q's reason for the Las Vegas decline
    occ = h.cite_doc_find(K10, "Hotel occupancy | 94.1% | 97.5% | 96.8%")
    cond = h.cite_doc_find(
        MERGER8K, "the expiration or termination of any applicable waiting period under the HSR Act"
    )
    fee = h.cite_doc_find(
        MERGER8K,
        "Parent will be required to pay the Company a reverse termination fee of $450,000,000",
    )
    dig = join_marks(
        h.cite_fig("eu_seg_margin_chg_caesars_digital"),
        h.cite_fig("eu_seg_margin_caesars_digital_q2_2026"),
    )
    end_c, end2_c, end3_c = (
        join_marks(h.cite_fig(k))
        for k in (
            "merger_initial_end_date",
            "merger_first_extended_end_date",
            "merger_second_extended_end_date",
        )
    )
    s1, s2, s3, s4 = (_syn(h, f"fetched_0{i}") for i in range(1, 5))
    evidence = [
        (
            "E1",
            "RQ1",
            "Las Vegas net revenues, net income, Adjusted EBITDA and margin declined in Q2 and H1 on lower city-wide leisure visitation, hotel occupancy and room rates",
            "Issuer-reported fact",
            "Pack",
            "2026-06-30",
            "Issuer-reported; the Q2 10-Q",
            lv_text,
        ),
        (
            "E2",
            "RQ1",
            "Las Vegas hotel occupancy was 94.1% in FY2025 against 97.5% in FY2024",
            "Issuer-reported fact",
            "Pack",
            "2025-12-31",
            "Issuer-reported; the FY2025 10-K",
            occ,
        ),
        (
            "E3",
            "RQ1",
            "Las Vegas visitor volume fell 4.1% in the first eight months of 2026 against 2025 (fetched/01-lvcva-visitor-stats.example.md (synthetic))",
            "Market statistic (fetched)",
            "Fetched",
            SYNTHETIC["fetched_01"][1],
            "Independent third party (invented for design)",
            s1,
        ),
        (
            "E4",
            "RQ1",
            "Strip RevPAR fell 3.4% year to date (fetched/02-strip-hotel-metrics.example.md (synthetic))",
            "Market statistic (fetched)",
            "Fetched",
            SYNTHETIC["fetched_02"][1],
            "Independent third party (invented for design)",
            s2,
        ),
        (
            "E5",
            "RQ2",
            "Closing needs a majority shareholder vote, expiry of the HSR waiting period and certain gaming regulatory approvals",
            "Contractual condition",
            "Pack",
            "2026-05-28",
            "Issuer filing (the merger 8-K)",
            cond,
        ),
        (
            "E6",
            "RQ2",
            "A reverse termination fee of $450,000,000 is payable by Parent if a gaming or antitrust law blocks the merger or the End Date passes with only the regulatory conditions open",
            "Contractual condition",
            "Pack",
            "2026-05-28",
            "Issuer filing (the merger 8-K)",
            fee,
        ),
        (
            "E7",
            "RQ2",
            "Approval is needed from gaming regulators in 12 of Caesars' 18 states and the Nevada hearing is calendared for 17 December 2026 (fetched/03-gaming-regulator-calendar.example.md (synthetic))",
            "Regulatory calendar (fetched)",
            "Fetched",
            SYNTHETIC["fetched_03"][1],
            "Independent third party (invented for design)",
            s3,
        ),
        (
            "E8",
            "RQ3",
            f"Caesars Digital's Adjusted EBITDA margin fell {num(abs(ctx.val('eu_seg_margin_chg_caesars_digital')), 1)} pp year on year in Q2 2026 to {num(ctx.val('eu_seg_margin_caesars_digital_q2_2026'), 1)}%",
            "Issuer-reported fact",
            "Pack",
            "2026-06-30",
            "Issuer-reported; Caesars only, not a peer",
            dig,
        ),
        (
            "E9",
            "RQ3",
            "One peer's finance chief said online sports betting margin fell about 2 points after a state tax increase (fetched/04-trade-press-osb.example.md (synthetic))",
            "Company statement via trade press",
            "Fetched",
            SYNTHETIC["fetched_04"][1],
            "Not independent: a company statement relayed by the press",
            s4,
        ),
    ]
    h.table(
        "cpdr.evidence",
        [
            {
                "evidence_id": e,
                "question_id": q,
                "claim": c,
                "claim_type": ct,
                "source_type": st,
                "source_date": d,
                "independence": ind,
                "cite": ck,
            }
            for e, q, c, ct, st, d, ind, ck in evidence
        ],
    )
    answers = [
        {
            "question_id": "RQ1",
            "answer": "Las Vegas visitation and room economics are weaker in 2026 than in 2025: the 10-Q ties the segment's decline to lower visitation, occupancy and rates, and the fetched statistics show visitor volume down 4.1% and Strip RevPAR down 3.4% (synthetic).",
            "evidence_ids": "E1; E2; E3; E4",
            "contrary_evidence": f"Regional Adjusted EBITDA rose {num(ctx.val('eu_seg_ebitda_pct_regional'), 1)}% in Q2 and partly offsets the Las Vegas decline {join_marks(h.cite_fig('eu_seg_ebitda_pct_regional'))}",
            "uncertainty": "Medium: the fetched statistics are synthetic and one segment's visitation does not isolate hold or mix effects",
            "consequence_for": "CP-2 (Credit Direction), CP-2A (Las Vegas downturn path), CP-2G (Downside drivers)",
            "cite": join_marks(lv_text, occ, s1, s2, h.cite_fig("eu_seg_ebitda_pct_regional")),
        },
        {
            "question_id": "RQ2",
            "answer": "Closing needs a shareholder vote, the HSR waiting period to expire and gaming approvals; the synthetic regulator calendar puts approvals in 12 of 18 states with a Nevada hearing in December 2026, inside the merger's End Date of 27 May 2027.",
            "evidence_ids": "E5; E6; E7",
            "contrary_evidence": f"The End Date extends automatically to 27 August 2027 and 27 November 2027 if only regulatory conditions remain open {end2_c}{end3_c}",
            "uncertainty": "Medium: the regulator calendar is synthetic; the contractual conditions are real",
            "consequence_for": "CP-1A (transaction facts), CP-6 (catalysts)",
            "cite": join_marks(cond, fee, s3, end_c, end2_c, end3_c),
        },
        {
            "question_id": "RQ3",
            "answer": "Unresolved: the pack shows only Caesars' own Digital margin falling 4.0 pp, and the one fetched source about peers is a relayed company statement, so a peer margin trend under higher state taxes cannot be stated.",
            "evidence_ids": "E8; E9",
            "contrary_evidence": "None established; the single peer quote points the same way as Caesars' own result",
            "uncertainty": "High: no independent peer data, and the peers' digital results are partly equity-method",
            "consequence_for": "CP-1C (peer benchmark) would need peer digital margins; until then CP-2 treats Digital as a Caesars-only weakness",
            "cite": join_marks(dig, s4),
        },
    ]
    h.table("cpdr.answers", answers)
    h.table(
        "cpdr.sector_view",
        [
            {
                "sector": "Gaming and leisure (US casino operators)",
                "outlook": "Neutral",
                "drivers": "Las Vegas visitation and room rates, regional resilience, online gaming growth against higher state taxes",
                "competitors": "MGM Resorts and PENN Entertainment are the peers in the pack; both report different segment structures",
                "regulation": "State gaming approvals govern the merger and higher online gaming taxes press Digital margins",
                "risks": "Consumer slowdown, hold volatility, tax increases and the cost of financing the take-private",
                "cite": join_marks(lv_text, cond, dig, s3, s4),
            }
        ],
    )
    h.analysis(
        f"Two of the three approved questions are answered and one is unresolved. Las Vegas visitation and room economics are weaker in 2026, which the issuer's own 10-Q says drove the segment's decline {lv_text} and which fetched statistics confirm (visitor volume down 4.1%, Strip RevPAR down 3.4%) {s1}{s2}. Confidence: Medium, because the fetched figures are synthetic.\n\n"
        f"The merger needs a shareholder vote, expiry of the HSR waiting period and certain gaming regulatory approvals {cond}, with a $450,000,000 reverse termination fee if a gaming or antitrust law blocks it {fee}. The synthetic regulator calendar puts approvals in 12 of 18 states and the Nevada hearing in December 2026 {s3}, inside the End Date of 27 May 2027 {end_c}. Confidence: Medium.\n\n"
        f"The third question, how peers' online sports betting margins move under higher state taxes, is Unanswered. Caesars' own Digital margin fell {num(abs(ctx.val('eu_seg_margin_chg_caesars_digital')), 1)} pp in Q2 {dig}, and the only fetched peer source is a company statement relayed by the press {s4}, which is not independent. CP-1C would need peer digital margins before this can be answered.\n\n"
        "The sector view is Neutral: weaker Las Vegas demand and tax pressure on digital offset by regional resilience, and the creditor consequence runs through cash flow after fixed claims, not through a default signal. "
        "All fetched sources are synthetic and labelled (fetched/<nn>-<host>.example.md (synthetic)); no fetched file exists. Confidence in this module: Medium-Low."
    )
    h.gaps(
        "- Fetched sources: the four fetched pages are synthetic and no fetched file exists, so every fetched claim is a test value. Lifted by: running the fetch layer against the approved questions.\n"
        "- RQ3 is unresolved: no independent peer margin data. Effect: peer digital margins are not benchmarked. Lifted by: peer filings with segment margins, or a sector report.\n"
        "- The approval calendar (12 states, Nevada hearing date) is synthetic. Lifted by: the regulators' public agendas."
    )
    return h
