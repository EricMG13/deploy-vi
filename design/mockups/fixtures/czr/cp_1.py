"""CZR CP-1: canonical data foundation, real data only (reference module for F2-F4).

Every figure comes from the corpus filings (10-K, 10-Q, earnings release, TRACE pages), the base data's
cited figures, or the real CAOS CP-1 output. Nothing here is invented. LTM columns are calculated with
`compute()` from cited inputs and asserted equal to the base data's K-figures.
"""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal

from core import GAP, Ctx, FixtureError, Handoff, compute, plain
from czr.cp_3 import FACTS, SOFR, cite_fact, is_primary
from helpers import cell_number, cite_row, join_marks

FOLDER = "full-credit-assessment-2026-10-06"
K10, Q10, REL = "CZR_FY2025_10K.txt", "CZR_Q2_2026_10Q.txt", "CZR_Q2_2026_Earnings_Release.txt"
TRACE = {
    "cei_secured_2032": "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt",
    "cei_unsecured_2032": "CZR_FINRA_TRACE_12769GAD2_2026-10-02.txt",
}
SUFFIX = {
    "FY2023": "fy2023",
    "FY2024": "fy2024",
    "FY2025": "fy2025",
    "H1_2025": "h1_2025",
    "H1_2026": "h1_2026",
    "Q2_2025": "q2_2025",
    "Q2_2026": "q2_2026",
}
ALL7 = list(SUFFIX)
FY3, H12 = ["FY2023", "FY2024", "FY2025"], ["H1_2025", "H1_2026"]

PERIODS = [  # id, fiscal_year, quarter, type, start, end, days, components
    ("FY2023", "2023", GAP, "FY", "2023-01-01", "2023-12-31", "365", GAP),
    ("FY2024", "2024", GAP, "FY", "2024-01-01", "2024-12-31", "366", GAP),
    ("FY2025", "2025", GAP, "FY", "2025-01-01", "2025-12-31", "365", GAP),
    ("H1_2025", "2025", GAP, "YTD", "2025-01-01", "2025-06-30", "181", GAP),
    ("H1_2026", "2026", GAP, "YTD", "2026-01-01", "2026-06-30", "181", GAP),
    (
        "LTM_Q2_2026",
        "2026",
        "2",
        "LTM",
        "2025-07-01",
        "2026-06-30",
        "365",
        "FY2025;H1_2026;H1_2025",
    ),
    ("Q2_2025", "2025", "2", "QUARTER", "2025-04-01", "2025-06-30", "91", GAP),
    ("Q2_2026", "2026", "2", "QUARTER", "2026-04-01", "2026-06-30", "91", GAP),
    ("FY2025_END", "2025", GAP, "PERIOD_END", "2025-12-31", "2025-12-31", "1", GAP),
    ("JUN30_2026", "2026", GAP, "PERIOD_END", "2026-06-30", "2026-06-30", "1", GAP),
]
FLOWS = [  # metric, base-figure prefix, sign, periods, base K figure for LTM
    ("revenue", "net_revenues", 1, ALL7, "ltm_net_revenues_q2_2026"),
    ("adjusted_ebitda", "adj_ebitda", 1, ALL7, "ltm_adj_ebitda_q2_2026"),
    ("d_and_a", "d_and_a", 1, ALL7, None),
    ("interest_expense", "interest_expense", 1, ALL7, "ltm_interest_expense_q2_2026"),
    ("cash_interest_paid", "cash_interest_debt", -1, FY3 + H12, "ltm_cash_interest_debt_q2_2026"),
    ("lease_cash_paid", "cash_interest_rent", -1, FY3 + H12, "ltm_cash_interest_rent_q2_2026"),
    ("cash_taxes_paid", "income_taxes_paid", -1, FY3 + H12, "ltm_income_taxes_paid_q2_2026"),
    ("cfo", "cfo", 1, FY3 + H12, "ltm_cfo_q2_2026"),
    ("capex", "capex", 1, FY3 + H12, "ltm_capex_q2_2026"),
]

FACILITIES = [  # id, name, type, secured, seniority, debt_type, q-needle, k-needle, maturity source, extra
    dict(
        id="cei_rcf",
        name="CEI Revolving Credit Facility",
        ftype="Revolving credit",
        sec="SECURED",
        sen="Senior secured",
        dt="RCF",
        q="CEI Revolving Credit Facility | 2028 | variable | $120 |",
        k="CEI Revolving Credit Facility | 2028 | variable | $160 |",
        mat=("data", "cei_rcf_maturity"),
        commit="cei_rcf_commitment",
        ref="Term SOFR",
        spread=235,
        floor=0,
        margin="Adjusted Term SOFR (Term SOFR + 0.10%) + 2.25%",
        terms=(
            "Borrowings under the CEI Revolving Credit Facility and the CEI Term Loan A bear interest",
            "Such applicable margin is 2.25% per annum in the case of any Adjusted Term SOFR loan",
        ),
    ),
    dict(
        id="cei_term_a",
        name="CEI Term Loan A",
        ftype="Term loan",
        sec="SECURED",
        sen="Senior secured",
        dt="1L Term Loan",
        q="CEI Term Loan A | 2028 | variable | 619 |",
        k="CEI Term Loan A | 2028 | variable | 637 |",
        mat=("doc", "The CEI Term Loan A will mature on January 31, 2028."),
        ref="Term SOFR",
        spread=235,
        floor=0,
        margin="Adjusted Term SOFR (Term SOFR + 0.10%) + 2.25%",
        terms=(
            "Borrowings under the CEI Revolving Credit Facility and the CEI Term Loan A bear interest",
            "Such applicable margin is 2.25% per annum in the case of any Adjusted Term SOFR loan",
        ),
        amort=(
            "aggregate principal amount of $750 million",
            Decimal(750),
            "scheduled quarterly payments in amounts equal to 1.25%",
            Decimal("1.25"),
        ),
    ),
    dict(
        id="cva_rcf",
        name="CVA Revolving Credit Facility",
        ftype="Revolving credit",
        sec="SECURED",
        sen="Senior secured",
        dt="RCF",
        q="CVA Revolving Credit Facility | 2029 | variable | — |",
        k="CVA Revolving Credit Facility | 2029 | variable | — |",
        mat=("data", "cva_facilities_maturity"),
        commit="cva_rcf_commitment",
        ref="Term SOFR",
        spread=None,
        floor=None,
        margin="Term SOFR + margin (margin not stated in the sources)",
        terms=(
            "The CVA Revolving Credit Facility and the CVA Delayed Draw Term Loan are subject to a variable rate",
        ),
    ),
    dict(
        id="cva_term",
        name="CVA Delayed Draw Term Loan",
        ftype="Term loan",
        sec="SECURED",
        sen="Senior secured",
        dt="1L Term Loan",
        q="CVA Delayed Draw Term Loan | 2029 | variable | 376 |",
        k="CVA Delayed Draw Term Loan | 2029 | variable | 386 |",
        mat=("data", "cva_facilities_maturity"),
        commit="cva_ddtl_commitment",
        ref="Term SOFR",
        spread=None,
        floor=None,
        margin="Term SOFR + margin (margin not stated in the sources)",
        terms=(
            "The CVA Revolving Credit Facility and the CVA Delayed Draw Term Loan are subject to a variable rate",
        ),
    ),
    dict(
        id="cei_term_b",
        name="CEI Term Loan B",
        ftype="Term loan",
        sec="SECURED",
        sen="Senior secured",
        dt="1L Term Loan",
        q="CEI Term Loan B | 2030 | variable | 2,018 |",
        k="CEI Term Loan B | 2030 | variable | 2,031 |",
        mat=("doc", "The CEI Term Loan B will mature on February 6, 2030."),
        ref="Term SOFR",
        spread=225,
        floor=50,
        margin="Term SOFR (0.50% floor) + 2.25%",
        terms=(
            "Borrowings under the CEI Term Loan B, as amended, bear interest",
            "Such applicable margin is 2.25% per annum in the case of any Term SOFR loan",
        ),
        amort=(
            "aggregate principal amount of $2.5 billion",
            Decimal(2500),
            "scheduled quarterly principal payments in amounts equal to 0.25%",
            Decimal("0.25"),
        ),
    ),
    dict(
        id="cei_term_b1",
        name="CEI Term Loan B-1",
        ftype="Term loan",
        sec="SECURED",
        sen="Senior secured",
        dt="1L Term Loan",
        q="CEI Term Loan B-1 | 2031 | variable | 2,835 |",
        k="CEI Term Loan B-1 | 2031 | variable | 2,849 |",
        mat=("doc", "The CEI Term Loan B-1 will mature on February 6, 2031."),
        ref="Term SOFR",
        spread=225,
        floor=50,
        margin="Term SOFR (0.50% floor) + 2.25%",
        terms=(
            "Borrowings under the CEI Term Loan B-1, as amended, bear interest",
            "Such applicable margin is 2.25% per annum in the case of any Term SOFR loan",
        ),
        amort=(
            "aggregate principal amount of $2.9 billion",
            Decimal(2900),
            "requires quarterly principal payments in amounts equal to 0.25%",
            Decimal("0.25"),
        ),
    ),
    dict(
        id="cei_secured_2030",
        name="CEI Senior Secured Notes due 2030",
        ftype="Senior notes",
        sec="SECURED",
        sen="Senior secured",
        dt="SS Notes",
        q="CEI Senior Secured Notes due 2030 | 2030 | 7.00% | 2,000 |",
        k="CEI Senior Secured Notes due 2030 | 2030 | 7.00% | 2,000 |",
        mat=("doc", "The CEI Senior Secured Notes due 2030 will mature on February 15, 2030"),
        fixed="7.00",
        margin="7.00% fixed",
    ),
    dict(
        id="cei_secured_2032",
        name="CEI Senior Secured Notes due 2032",
        ftype="Senior notes",
        sec="SECURED",
        sen="Senior secured",
        dt="SS Notes",
        q="CEI Senior Secured Notes due 2032 | 2032 | 6.50% | 1,500 |",
        k="CEI Senior Secured Notes due 2032 | 2032 | 6.50% | 1,500 |",
        mat=("doc", "The CEI Senior Secured Notes due 2032 will mature on February 15, 2032"),
        fixed="6.50",
        margin="6.50% fixed",
    ),
    dict(
        id="cei_unsecured_2029",
        name="CEI Senior Notes due 2029",
        ftype="Senior notes",
        sec="UNSECURED",
        sen="Senior unsecured",
        dt="SU Notes",
        q="CEI Senior Notes due 2029 | 2029 | 4.625% | 1,200 |",
        k="CEI Senior Notes due 2029 | 2029 | 4.625% | 1,200 |",
        mat=("doc", "The CEI Senior Notes due 2029 will mature on October 15, 2029"),
        fixed="4.625",
        margin="4.625% fixed",
    ),
    dict(
        id="cei_unsecured_2032",
        name="CEI Senior Notes due 2032",
        ftype="Senior notes",
        sec="UNSECURED",
        sen="Senior unsecured",
        dt="SU Notes",
        q="CEI Senior Notes due 2032 | 2032 | 6.00% | 1,100 |",
        k="CEI Senior Notes due 2032 | 2032 | 6.00% | 1,100 |",
        mat=("doc", "The CEI Senior Notes due 2032 will mature on October 15, 2032"),
        fixed="6.00",
        margin="6.00% fixed",
    ),
    dict(
        id="sid_bonds",
        name="Special Improvement District Bonds",
        ftype="Improvement district bonds",
        sec="NOT_STATED",
        sen="Not stated",
        dt="Other",
        q="Special Improvement District Bonds | 2037 | 4.30% | 38 |",
        k="Special Improvement District Bonds | 2037 | 4.30% | 40 |",
        mat=None,
        fixed="4.30",
        margin="4.30% fixed",
    ),
    dict(
        id="other_debt",
        name="Long-term notes and other payables",
        ftype="Other debt",
        sec="NOT_STATED",
        sen="Not stated",
        dt="Other",
        q="Long-term notes and other payables | 1 | 1 | 2",
        k="Long-term notes and other payables | 2 | 2 | 2",
        mat=None,
        margin="Not stated",
    ),
]


class Accounts:
    """Rows of cp1.model_account_register."""

    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.values: dict[tuple[str, str], Decimal] = {}
        self.marks: dict[tuple[str, str], str] = {}

    def add(
        self, metric: str, period: str, value: Decimal, status: str, marks: str, locator: str
    ) -> None:
        self.rows.append(
            {
                "metric_id": metric,
                "period_id": period,
                "value": plain(value),
                "calculation_status": status,
                "source_id": marks,
                "source_locator": locator,
            }
        )
        self.values[(metric, period)] = value
        self.marks[(metric, period)] = marks


def _ltm(
    a: Accounts, metric: str, label: str, places: int = 0, check: Decimal | None = None
) -> None:
    fy, h1, p1 = (a.values[(metric, p)] for p in ("FY2025", "H1_2026", "H1_2025"))
    v, calc_s = compute(label, "fy + h1 - ph1", places, "", fy=fy, h1=h1, ph1=p1)
    if check is not None and v != check:
        raise FixtureError(f"LTM {metric}: {v} differs from the base data {check}")
    a.add(
        metric,
        "LTM_Q2_2026",
        v,
        "Calculated",
        join_marks(*(a.marks[(metric, p)] for p in ("FY2025", "H1_2026", "H1_2025"))),
        calc_s,
    )


def _accounts(ctx: Ctx, h: Handoff) -> Accounts:
    a = Accounts()
    for metric, prefix, sign, periods, ltm_key in FLOWS:
        for p in periods:
            key = f"{prefix}_{SUFFIX[p]}"
            mk = h.cite_fig(key)
            a.add(metric, p, ctx.val(key) * sign, "Verified", mk, h.citation(mk)["locator"])
        _ltm(
            a,
            metric,
            f"LTM {metric}",
            check=None
            if ltm_key is None
            else ctx.val(ltm_key) * (sign if metric not in ("capex",) else 1),
        )
    # operating income (EBIT) from the statements of operations; reported EBITDA = EBIT + D&A
    mk, nums = cite_row(h, ctx, K10, "Operating income | 1,858 | 2,304 | 2,472")
    for p, v in zip(("FY2025", "FY2024", "FY2023"), nums[:3], strict=True):
        a.add(
            "ebit", p, v, "Verified", mk, "operating income, consolidated statement of operations"
        )  # type: ignore[arg-type]
    mk, nums = cite_row(h, ctx, Q10, "Operating income | 513 | 526 | 1,013 | 1,014")
    for p, v in zip(("Q2_2026", "Q2_2025", "H1_2026", "H1_2025"), nums[:4], strict=True):
        a.add("ebit", p, v, "Verified", mk, "operating income, interim statement of operations")  # type: ignore[arg-type]
    _ltm(a, "ebit", "LTM ebit")
    for p in ALL7 + ["LTM_Q2_2026"]:
        v, calc_s = compute(
            "EBIT plus D&A",
            "ebit + da",
            0,
            "",
            ebit=a.values[("ebit", p)],
            da=a.values[("d_and_a", p)],
        )
        a.add(
            "ebitda",
            p,
            v,
            "Calculated",
            join_marks(a.marks[("ebit", p)], a.marks[("d_and_a", p)]),
            calc_s,
        )
    if a.values[("ebitda", "Q2_2026")] != ctx.val("reported_ebitda_q2_2026"):
        raise FixtureError("Q2 2026 Reported EBITDA differs from the base data")
    # period-end balances
    for p, key, fy_key in (
        ("FY2025_END", "cash_2025_12_31", "total_debt_face_2025_12_31"),
        ("JUN30_2026", "cash_2026_06_30", "total_debt_face_2026_06_30"),
    ):
        mk = h.cite_fig(key)
        a.add("cash_and_equivalents", p, ctx.val(key), "Verified", mk, h.citation(mk)["locator"])
        mk = h.cite_fig(fy_key)
        a.add("total_debt", p, ctx.val(fy_key), "Verified", mk, h.citation(mk)["locator"])
    for p, key in (
        ("FY2025_END", "lt_financing_obligations_2025_12_31"),
        ("JUN30_2026", "lt_financing_obligations_2026_06_30"),
    ):
        mk = h.cite_fig(key)
        a.add("financing_obligations", p, ctx.val(key), "Verified", mk, h.citation(mk)["locator"])
    parts = {
        k: ctx.val(k)
        for k in ("liq_cei_rcf_net", "liq_cva_rcf", "liq_lcs", "liq_reserves", "liq_regulatory")
    }
    v, calc_s = compute(
        "undrawn revolver availability",
        "cei + cva + lcs + reserves + regulatory",
        0,
        "",
        cei=parts["liq_cei_rcf_net"],
        cva=parts["liq_cva_rcf"],
        lcs=parts["liq_lcs"],
        reserves=parts["liq_reserves"],
        regulatory=parts["liq_regulatory"],
    )
    a.add(
        "undrawn_rcf",
        "JUN30_2026",
        v,
        "Calculated",
        join_marks(*(h.cite_fig(k) for k in parts)),
        calc_s,
    )
    mk = h.cite_fig("liq_total")
    a.add(
        "liquidity_total",
        "JUN30_2026",
        ctx.val("liq_total"),
        "Verified",
        mk,
        h.citation(mk)["locator"],
    )
    if a.values[("undrawn_rcf", "JUN30_2026")] + a.values[
        ("cash_and_equivalents", "JUN30_2026")
    ] != ctx.val("liq_total"):
        raise FixtureError("cash plus undrawn revolver differs from the cited liquidity total")
    # working-capital balances (10-Q balance sheet: 30 Jun 2026 | 31 Dec 2025)
    for metric, needle in (
        ("net_accounts_receivable", "Accounts receivable, net | 485 | 476"),
        ("inventory", "Inventories | 49 | 43"),
        ("accounts_payable", "Accounts payable | $290 | $297"),
    ):
        mk, nums = cite_row(h, ctx, Q10, needle)
        a.add(metric, "JUN30_2026", nums[0], "Verified", mk, "balance sheet, 30 June 2026")  # type: ignore[arg-type]
        a.add(metric, "FY2025_END", nums[1], "Verified", mk, "balance sheet, 31 December 2025")  # type: ignore[arg-type]
    # net change in cash = CFO + investing + financing
    k_cfo, k_inv, k_fin = (
        cite_row(h, ctx, K10, n)
        for n in (
            "Net cash provided by operating activities | 1,302",
            "Net cash used in investing activities | (571)",
            "Net cash used in financing activities | (763)",
        )
    )
    q_cfo, q_inv, q_fin = (
        cite_row(h, ctx, Q10, n)
        for n in (
            "Net cash provided by operating activities | 675 | 680",
            "Net cash used in investing activities | (411) | (434)",
            "Net cash used in financing activities | (171) | (176)",
        )
    )
    v, s = compute(
        "net change in cash",
        "cfo + investing + financing",
        0,
        "",
        cfo=k_cfo[1][0],
        investing=k_inv[1][0],
        financing=k_fin[1][0],
    )
    a.add("net_cash_change", "FY2025", v, "Calculated", join_marks(k_cfo[0], k_inv[0], k_fin[0]), s)
    for i, p in enumerate(("H1_2026", "H1_2025")):
        v, s = compute(
            "net change in cash",
            "cfo + investing + financing",
            0,
            "",
            cfo=q_cfo[1][i],
            investing=q_inv[1][i],
            financing=q_fin[1][i],
        )
        a.add("net_cash_change", p, v, "Calculated", join_marks(q_cfo[0], q_inv[0], q_fin[0]), s)
    d_debt, s = compute(
        "change in face debt",
        "end - start",
        0,
        "",
        end=a.values[("total_debt", "JUN30_2026")],
        start=a.values[("total_debt", "FY2025_END")],
    )
    a.add(
        "net_debt_issue_repay",
        "H1_2026",
        d_debt,
        "Calculated",
        join_marks(a.marks[("total_debt", "JUN30_2026")], a.marks[("total_debt", "FY2025_END")]),
        s + " (face principal, 31 Dec 2025 to 30 Jun 2026)",
    )
    return a


def _bridge(ctx: Ctx, h: Handoff, a: Accounts) -> list[dict]:
    rows: list[dict] = []
    k_imp = cite_row(h, ctx, K10, "Impairment charges (c) | 182 | 302 | 95")
    k_tx = cite_row(h, ctx, K10, "Transaction costs and other, net (d) | 72 | (285) | 6")
    k_sbc = cite_row(h, ctx, K10, "Stock-based compensation expense | 95 | 94 | 104")
    r_tx = cite_row(h, ctx, REL, "Transaction costs and other, net (a) | 29 | 41 | 45 | 54")
    r_sbc = cite_row(h, ctx, REL, "Stock-based compensation expense | 23 | 24 | 47 | 50")
    q_none = cite_row(h, ctx, Q10, "Total operating expenses | 2,480 | 2,381 | 4,850 | 4,687")
    vals: dict[tuple[str, str], tuple[Decimal, str, str]] = {}
    for p, v in zip(("FY2025", "FY2024", "FY2023"), k_imp[1][:3], strict=True):
        vals[("impairment", p)] = (
            v,
            k_imp[0],
            "impairment charges, adjusted EBITDA reconciliation",
        )  # type: ignore[assignment]
    for p, v in zip(("FY2025", "FY2024", "FY2023"), k_tx[1][:3], strict=True):
        vals[("transaction_costs", p)] = (
            v,
            k_tx[0],
            "transaction costs and other, net, reconciliation",
        )  # type: ignore[assignment]
    for p, v in zip(("FY2025", "FY2024", "FY2023"), k_sbc[1][:3], strict=True):
        vals[("sbc", p)] = (v, k_sbc[0], "stock-based compensation, reconciliation")  # type: ignore[assignment]
    for p, v in zip(("Q2_2026", "Q2_2025", "H1_2026", "H1_2025"), r_tx[1][:4], strict=True):
        vals[("transaction_costs", p)] = (
            v,
            r_tx[0],
            "transaction costs and other, net, reconciliation",
        )  # type: ignore[assignment]
    for p, v in zip(("Q2_2026", "Q2_2025", "H1_2026", "H1_2025"), r_sbc[1][:4], strict=True):
        vals[("sbc", p)] = (v, r_sbc[0], "stock-based compensation, reconciliation")  # type: ignore[assignment]
    for p in ("Q2_2026", "Q2_2025", "H1_2026", "H1_2025"):
        vals[("impairment", p)] = (
            Decimal(0),
            q_none[0],
            "no impairment line in the interim statement of operations; the reconciliation closes without one",
        )
    meta = {
        "impairment": ("Impairment charges", "OTHER_EXPLICIT", 1),
        "transaction_costs": ("Transaction costs and other, net", "TRANSACTION_COSTS", 2),
        "sbc": ("Stock-based compensation expense", "SBC", 3),
    }
    for aid in meta:
        for p in ("FY2023", "FY2024", "FY2025", "H1_2025", "H1_2026", "Q2_2025", "Q2_2026"):
            v, mk, loc = vals[(aid, p)]
            rows.append(
                {
                    "addback_id": aid,
                    "period_id": p,
                    "value": plain(v),
                    "source_id": mk,
                    "source_locator": loc,
                }
            )
        fy, h1, p1 = (vals[(aid, p)][0] for p in ("FY2025", "H1_2026", "H1_2025"))
        v, s = compute(f"LTM {aid}", "fy + h1 - ph1", 0, "", fy=fy, h1=h1, ph1=p1)
        rows.append(
            {
                "addback_id": aid,
                "period_id": "LTM_Q2_2026",
                "value": plain(v),
                "source_id": join_marks(
                    *(vals[(aid, p)][1] for p in ("FY2025", "H1_2026", "H1_2025"))
                ),
                "source_locator": s,
            }
        )
    for r in rows:
        label, cls, prio = meta[r["addback_id"]]
        r.update(
            {
                "addback_label": label,
                "addback_classification": cls,
                "realization_status": "REALIZED",
                "display_priority": str(prio),
            }
        )
    # every period reconciles: reported EBITDA + add-backs = stated Adjusted EBITDA
    for p in (
        "FY2023",
        "FY2024",
        "FY2025",
        "H1_2025",
        "H1_2026",
        "Q2_2025",
        "Q2_2026",
        "LTM_Q2_2026",
    ):
        tot = sum((Decimal(r["value"]) for r in rows if r["period_id"] == p), Decimal(0))
        if a.values[("ebitda", p)] + tot != a.values[("adjusted_ebitda", p)]:
            raise FixtureError(f"adjusted EBITDA bridge does not close for {p}")
    return rows


def _segments(ctx: Ctx, h: Handoff) -> list[dict]:
    rows: list[dict] = []
    segs = [
        (
            "seg_las_vegas",
            "Las Vegas",
            "OPERATING_SEGMENT",
            1,
            "Las Vegas | $4,049 | $4,274 | $4,470",
            "las_vegas",
        ),
        (
            "seg_regional",
            "Regional",
            "OPERATING_SEGMENT",
            2,
            "Regional | 5,756 | 5,539 | 5,778",
            "regional",
        ),
        (
            "seg_caesars_digital",
            "Caesars Digital",
            "OPERATING_SEGMENT",
            3,
            "Caesars Digital | 1,408 | 1,163 | 973",
            "caesars_digital",
        ),
        (
            "seg_managed_branded",
            "Managed and Branded",
            "OPERATING_SEGMENT",
            4,
            "Managed and Branded | 279 | 274 | 307",
            "managed_branded",
        ),
        (
            "seg_corporate_other",
            "Corporate and Other",
            "CORPORATE_ELIMINATION",
            5,
            "Corporate and Other (a) | (6) | (5) | —",
            "corporate_other",
        ),
    ]
    for sid, name, typ, prio, needle, key in segs:
        mk, nums = cite_row(h, ctx, K10, needle)
        for p, v in zip(("FY2025", "FY2024", "FY2023"), nums[:3], strict=True):
            loc = "segment net revenues, results of operations table" + (
                "; a dash in the 10-K is nil" if v is None else ""
            )
            rows.append(
                {
                    "segment_id": sid,
                    "segment_name": name,
                    "segment_type": typ,
                    "display_priority": str(prio),
                    "period_id": p,
                    "revenue": plain(v if v is not None else Decimal(0)),
                    "source_id": mk,
                    "source_locator": loc,
                }
            )
        for p in ("Q2_2025", "Q2_2026"):
            k = f"seg_rev_{key}_{SUFFIX[p]}"
            mk2 = h.cite_fig(k)
            rows.append(
                {
                    "segment_id": sid,
                    "segment_name": name,
                    "segment_type": typ,
                    "display_priority": str(prio),
                    "period_id": p,
                    "revenue": plain(ctx.val(k)),
                    "source_id": mk2,
                    "source_locator": h.citation(mk2)["locator"],
                }
            )
    return rows


def _kpis(ctx: Ctx, h: Handoff) -> list[dict]:
    rows: list[dict] = []
    spec = [
        (
            "lv_table_drop",
            "Las Vegas table games drop",
            "Table games drop (a) | $2,880 | $3,124 | $3,428",
            "USD millions",
            "PERIOD_FLOW",
        ),
        (
            "lv_table_hold",
            "Las Vegas table games hold",
            "Table games hold % | 19.9% | 21.3% | 22.2%",
            "%",
            "RATE",
        ),
        (
            "lv_slot_handle",
            "Las Vegas slot handle",
            "Slot handle (a) | $10,427 | $10,569 | $11,057",
            "USD millions",
            "PERIOD_FLOW",
        ),
        (
            "lv_occupancy",
            "Las Vegas hotel occupancy",
            "Hotel occupancy | 94.1% | 97.5% | 96.8%",
            "%",
            "RATE",
        ),
        (
            "reg_table_drop",
            "Regional table games drop",
            "Table games drop | $4,431 | $4,005 | $4,188",
            "USD millions",
            "PERIOD_FLOW",
        ),
        (
            "reg_table_hold",
            "Regional table games hold",
            "Table games hold % | 20.7% | 21.3% | 21.7%",
            "%",
            "RATE",
        ),
        (
            "reg_slot_handle",
            "Regional slot handle",
            "Slot handle | $43,203 | $40,850 | $43,211",
            "USD millions",
            "PERIOD_FLOW",
        ),
    ]
    for i, (kid, label, needle, unit, vt) in enumerate(spec, 1):
        mk, nums = cite_row(h, ctx, K10, needle)
        for p, v in zip(("FY2025", "FY2024", "FY2023"), nums[:3], strict=True):
            rows.append(
                {
                    "kpi_id": kid,
                    "kpi_label": label,
                    "display_priority": str(i),
                    "period_id": p,
                    "value": plain(v),
                    "unit": unit,
                    "value_type": vt,
                    "source_id": mk,
                    "source_locator": "results of operations, segment operating metrics",
                }
            )  # type: ignore[arg-type]
    base_kpis = [
        ("properties", "Properties", "opm_properties", "count", "PERIOD_END"),
        ("slots", "Slot machines", "opm_slots", "count", "PERIOD_END"),
        ("tables", "Table games", "opm_tables", "count", "PERIOD_END"),
        ("rooms", "Hotel rooms", "opm_rooms", "count", "PERIOD_END"),
    ]
    for j, (kid, label, key, unit, vt) in enumerate(base_kpis, len(spec) + 1):
        mk = h.cite_fig(key)
        rows.append(
            {
                "kpi_id": kid,
                "kpi_label": label,
                "display_priority": str(j),
                "period_id": "JUN30_2026",
                "value": plain(ctx.val(key)),
                "unit": unit,
                "value_type": vt,
                "source_id": mk,
                "source_locator": h.citation(mk)["locator"],
            }
        )
    mk = h.cite_fig("opm_casino_share_fy2025")
    rows.append(
        {
            "kpi_id": "casino_share",
            "kpi_label": "Casino share of net revenues",
            "display_priority": str(len(spec) + 5),
            "period_id": "FY2025",
            "value": plain(ctx.val("opm_casino_share_fy2025")),
            "unit": "%",
            "value_type": "RATE",
            "source_id": mk,
            "source_locator": h.citation(mk)["locator"],
        }
    )
    return rows


def _date(text: str) -> str:
    m = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", text)
    if not m:
        raise FixtureError(f"no date in {text!r}")
    return datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()


def _facilities(ctx: Ctx, h: Handoff) -> list[dict]:
    rows: list[dict] = []
    for f in FACILITIES:
        mat_iso, mat_mark = GAP, ""
        if f["mat"]:
            if f["mat"][0] == "data":
                mat_mark = h.cite_fig(f["mat"][1])
                mat_iso = _date(ctx.figure(f["mat"][1])["raw"])
            else:
                line = ctx.find_line(Q10, f["mat"][1])
                text = ctx.corpus_lines(Q10)[line - 1]
                mat_mark = h.cite_doc(Q10, line, f["mat"][1])
                mat_iso = _date(text)
        term_marks = ""
        if f.get("terms"):
            term_marks = join_marks(
                *(
                    h.cite_doc_find(
                        Q10,
                        n,
                        nth=(
                            1
                            if (
                                n.startswith(
                                    "Such applicable margin is 2.25% per annum in the case of any Term SOFR"
                                )
                                and f["id"] == "cei_term_b1"
                            )
                            else 0
                        ),
                    )
                    for n in f["terms"]
                )
            )
        amort, amort_marks = GAP, ""
        if f.get("amort"):
            o_needle, orig, p_needle, pct = f["amort"]
            v, _ = compute(
                "annual amortisation", "pct / 100 * original * 4", 1, "", pct=pct, original=orig
            )
            amort = plain(v)
            amort_marks = join_marks(h.cite_doc_find(Q10, o_needle), h.cite_doc_find(Q10, p_needle))
        commit_iso = GAP
        commit_mark = ""
        if f.get("commit"):
            raw = ctx.val(f["commit"])
            commit_iso = (
                plain(raw * 1000) if "billions" in ctx.figure(f["commit"])["unit"] else plain(raw)
            )
            commit_mark = h.cite_fig(f["commit"])
        for period, doc, needle in (
            ("FY2025_END", K10, f["k"]),
            ("JUN30_2026", Q10, f["q"]),
        ):
            line, text, _ = ctx.find_line(doc, needle), "", None
            text = ctx.corpus_lines(doc)[line - 1].rstrip()
            cells = [c.strip() for c in text.split(" | ")][1:]
            face_s, book_s = (cells[2], cells[3]) if len(cells) == 5 else (cells[0], cells[1])
            face = cell_number(face_s) or Decimal(0)
            book = cell_number(book_s) or Decimal(0)
            row_mark = h.cite_doc(doc, line, text)
            marks = join_marks(
                row_mark,
                mat_mark,
                term_marks,
                amort_marks,
                commit_mark if period == "JUN30_2026" else "",
            )
            fixed = f.get("fixed", GAP)
            rows.append(
                {
                    "facility_id": f["id"],
                    "facility_name": f["name"],
                    "period_id": period,
                    "facility_type": f["ftype"],
                    "currency": "USD",
                    "carrying_value": plain(book),
                    "drawn_amount": plain(face),
                    "commitment": commit_iso if period == "JUN30_2026" else GAP,
                    "secured_status": f["sec"],
                    "seniority": f["sen"],
                    "margin_or_coupon": f["margin"],
                    "maturity_date": mat_iso,
                    "lease_classification": "NOT_APPLICABLE",
                    "rate_type": "Fixed" if fixed != GAP else ("Floating" if f.get("ref") else GAP),
                    "reference_rate": f.get("ref", GAP),
                    "spread_bps": GAP if f.get("spread") is None else str(f["spread"]),
                    "floor_bps": GAP if f.get("floor") is None else str(f["floor"]),
                    "fixed_rate": fixed,
                    "annual_amortisation": amort,
                    "source_id": marks,
                    "source_locator": f"{doc}, debt note table row"
                    + (
                        "; maturity, margin and amortisation from the debt note text"
                        if period == "JUN30_2026"
                        else ""
                    ),
                }
            )
    return rows


def pro_forma_rows(ctx: Ctx, h: Handoff, run_id: str) -> list[dict]:
    """Primary variants: the merger financing as `facility:NEW-n` rows plus interest and cash rows (synthetic, from
    `synthetic-facts.json -> czr.merger_tranches`). Each tranche also gets an undrawn facility row at both balance-sheet
    periods so the Model has a line to add the pro forma amount to. Real runs return [] (the new debt is unstated, G8)."""
    if not is_primary(ctx, run_id):
        return []
    block = FACTS["merger_tranches"]
    syn_all = cite_fact(h, "merger_tranches")
    fac_rows = h.rows("cp1.debt_facility_register")
    pf: list[dict] = []
    total_interest = Decimal(0)
    for t in block["tranches"]:
        tid, size = t["tranche_id"], Decimal(t["size"])
        syn = cite_fact(h, "merger_tranches", tid)
        loan = t["debt_type"] == "Term loan"
        secured = "unsecured" not in t["debt_type"].lower()
        for period in ("FY2025_END", "JUN30_2026"):
            fac_rows.append(
                {
                    "facility_id": tid,
                    "facility_name": t["instrument"],
                    "period_id": period,
                    "facility_type": "Term loan" if loan else "Senior notes",
                    "currency": "USD",
                    "carrying_value": "0",
                    "drawn_amount": "0",
                    "commitment": plain(size) if period == "JUN30_2026" else GAP,
                    "secured_status": "SECURED" if secured else "UNSECURED",
                    "seniority": "Senior secured" if secured else "Senior unsecured",
                    "margin_or_coupon": t["price_talk"],
                    "maturity_date": t["maturity_date"],
                    "lease_classification": "NOT_APPLICABLE",
                    "rate_type": "Floating" if loan else "Fixed",
                    "reference_rate": FACTS["rate_deck"]["reference_rate"] if loan else GAP,
                    "spread_bps": t["talk_mid_bps"] if loan else GAP,
                    "floor_bps": GAP,
                    "fixed_rate": GAP if loan else t["talk_mid_pct"],
                    "annual_amortisation": GAP,
                    "source_id": syn,
                    "source_locator": "synthetic undrawn tranche: pro forma only, nothing is drawn at the balance-sheet date",
                }
            )
        pf.append(
            {
                "adjustment_id": f"PF-{tid}-DEBT",
                "label": f"{t['instrument']} issued at close (pro forma)",
                "period_id": "LTM_Q2_2026",
                "effective_date": "2026-06-30",
                "classification": "NEW_DEBT",
                "metric_id": f"facility:{tid}",
                "value": plain(size),
                "source_id": syn,
                "source_locator": f"synthetic-facts.json#czr.merger_tranches.{tid}; shown as if drawn at the LTM balance-sheet date",
            }
        )
        if loan:
            interest, calc_s = compute(
                f"{tid} annual cash interest at the talk mid",
                "-size * (sofr + margin / 100) / 100",
                1,
                size=size,
                sofr=SOFR,
                margin=Decimal(t["talk_mid_bps"]),
            )
        else:
            interest, calc_s = compute(
                f"{tid} annual cash interest at the talk mid",
                "-size * coupon / 100",
                1,
                size=size,
                coupon=Decimal(t["talk_mid_pct"]),
            )
        total_interest += interest
        pf.append(
            {
                "adjustment_id": f"PF-{tid}-INT",
                "label": f"Annual cash interest on {tid} at the talk mid (pro forma; SOFR from the synthetic deck)",
                "period_id": "LTM_Q2_2026",
                "effective_date": "2026-06-30",
                "classification": "INTEREST",
                "metric_id": "cash_interest_paid",
                "value": plain(interest, 1),
                "source_id": join_marks(syn, cite_fact(h, "rate_deck")) if loan else syn,
                "source_locator": calc_s,
            }
        )
    pf.append(
        {
            "adjustment_id": "PF-CASH",
            "label": "Cash to the balance sheet from the new debt (all proceeds fund the take-private)",
            "period_id": "LTM_Q2_2026",
            "effective_date": "2026-06-30",
            "classification": "CASH",
            "metric_id": "cash_and_equivalents",
            "value": block["cash_to_balance_sheet"],
            "source_id": syn_all,
            "source_locator": "synthetic-facts.json#czr.merger_tranches.cash_to_balance_sheet",
        }
    )
    h.table("cp1.debt_facility_register", fac_rows)
    return pf


def _identity(ctx: Ctx, h: Handoff, fac_rows: list[dict]) -> list[dict]:
    rows = []
    by_id = {r["facility_id"]: r for r in fac_rows if r["period_id"] == "JUN30_2026"}
    for f in FACILITIES:
        fr = by_id[f["id"]]
        cusip = call = GAP
        mo = sp = GAP
        marks = fr["source_id"].split("]")[0] + "]"
        if f["id"] in TRACE:
            tf = TRACE[f["id"]]
            cusip_line = ctx.find_line(tf, "CUSIP: ")
            ctext = ctx.corpus_lines(tf)[cusip_line - 1]
            cusip = ctext.split("CUSIP: ")[1].strip()
            m_cusip = h.cite_doc(tf, cusip_line, ctext.strip())
            m_mo = h.cite_doc_find(tf, "Moody's rating shown: ")
            m_sp = h.cite_doc_find(tf, "Standard & Poor's rating shown: ")
            mo = (
                ctx.corpus_lines(tf)[ctx.find_line(tf, "Moody's rating shown: ") - 1]
                .split(": ")[1]
                .strip()
            )
            sp = (
                ctx.corpus_lines(tf)[ctx.find_line(tf, "Standard & Poor's rating shown: ") - 1]
                .split(": ")[1]
                .strip()
            )
            m_call = h.cite_doc_find(tf, "Next call date: ")
            call = _iso_us(
                ctx.corpus_lines(tf)[ctx.find_line(tf, "Next call date: ") - 1]
                .split(": ")[1]
                .strip()
            )
            marks = join_marks(m_cusip, m_mo, m_sp, m_call)
        rows.append(
            {
                "facility_id": f["id"],
                "instrument_name": f["name"],
                "debt_type": f["dt"],
                "bloomberg_id": GAP,
                "isin": GAP,
                "cusip": cusip,
                "issuer_entity": "Caesars Virginia, LLC"
                if f["id"].startswith("cva_")
                else "Caesars Entertainment, Inc.",
                "rating_moodys": mo,
                "rating_sp": sp,
                "rating_fitch": GAP,
                "call_schedule": f"first call {call}" if call != GAP else GAP,
                "listed_market": "No",
                "cite": marks,
            }
        )
    return rows


def _iso_us(s: str) -> str:
    return datetime.strptime(s, "%m/%d/%Y").date().isoformat()


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(ctx, "CP-1", "CZR", run_id, "2026-10-02", ["CP-0"])
    h.qa("Restricted")
    a = _accounts(ctx, h)
    fac = _facilities(ctx, h)
    bridge = _bridge(ctx, h, a)
    # tables ---------------------------------------------------------------------------------
    h.table(
        "cp1.model_period_register",
        [
            {
                "period_id": p,
                "fiscal_year": fy,
                "fiscal_quarter": fq,
                "period_type": pt,
                "start_date": s,
                "end_date": e,
                "day_count": d,
                "currency": "USD",
                "unit": "MILLIONS",
                "component_period_ids": comp,
            }
            for p, fy, fq, pt, s, e, d, comp in PERIODS
        ],
    )
    h.table("cp1.model_account_register", a.rows)
    h.table("cp1.adjusted_ebitda_bridge", bridge)
    h.table("cp1.segment_revenue_schedule", _segments(ctx, h))
    h.table("cp1.operating_kpi_schedule", _kpis(ctx, h))
    h.table("cp1.debt_facility_register", fac)
    h.table("cp1.pro_forma_adjustment_register", pro_forma_rows(ctx, h, run_id))
    caos_alloc = ctx.caos_table(FOLDER, "CP-1", "cp1.cp_model_segment_allocation")
    h.table(
        "cp1.cp_model_segment_allocation",
        [
            {
                "slot_id": r["slot_id"],
                "component_segment_ids": r["component_segment_ids"].replace(", ", ";"),
            }
            for r in caos_alloc
        ],
    )
    h.table("cp1.equity_value", [])  # no listed equity value in the sources (G27)
    h.table("cp1.instrument_identity", _identity(ctx, h, fac))
    h.table("cp1.reconciliation_checks", _reconciliation(ctx, h, a, bridge, fac))
    h.table("cp1.definition_conflicts", _conflicts(ctx, h))
    ent_mark = join_marks(h.cite_caos(FOLDER, "CP-1", 1), h.cite_caos(FOLDER, "CP-1", 2))
    h.table(
        "cp1.entity_profile",
        [
            {
                "entity": "Caesars Entertainment, Inc.",
                "role": "Registrant and consolidated operating issuer; borrower and guarantor perimeter varies by debt instrument",
                "fiscal_year_end": "December 31",
                "reporting_currency": "USD",
                "reporting_unit": "MILLIONS",
                "perimeter": "Registrant and consolidated subsidiaries",
                "accounting_basis": "US GAAP; FY audited, interim unaudited",
                "cite": ent_mark,
            }
        ],
    )
    # analysis -------------------------------------------------------------------------------
    ltm_e, ltm_d = (
        a.values[("adjusted_ebitda", "LTM_Q2_2026")],
        a.values[("total_debt", "JUN30_2026")],
    )
    lev, lev_s = compute(
        "total leverage on face debt", "debt / ebitda", 2, "x", debt=ltm_d, ebitda=ltm_e
    )
    from helpers import caos_text

    ct = lambda s: caos_text(h, FOLDER, "CP-1", s)  # noqa: E731
    h.analysis(
        f"The canonical record answers the reader question with audited annual and unaudited interim figures: FY2025 net revenues were 11,486 and Adjusted EBITDA 3,624, "
        f"H1 2026 revenue rose 2.8% to 5,863 while Adjusted EBITDA fell 1.7% to 1,807, and in Q2 revenue grew 3.0% while Adjusted EBITDA fell 3.7% to 920 {ct('{3,4,16,17}')}. "
        f"LTM Adjusted EBITDA to 30 June 2026 is {plain(ltm_e)} and face debt {plain(ltm_d)}, so total leverage is {lev}x ({lev_s}) {ct('{9}')}. USD millions throughout; confidence is Restricted.\n\n"
        f"RBOT counts debt at face principal because the facility register is built from the debt note: 11,905 at 31 December 2025 and 11,807 at 30 June 2026. Balance-sheet carrying debt is lower, at 11,699 on the same date after discounts and deferred finance charges, so the two measures are not interchangeable {ct('{7,8,9}')}. "
        f"The GLPI and VICI financing obligations of 13,157 sit outside debt, and the filing estimates about 1.4 billion of 2026 lease payments to them, so debt-only leverage understates fixed claims {ct('{18}')}.\n\n"
        f"Reported EBITDA is operating income plus D&A, and Adjusted EBITDA adds back impairment, transaction costs and stock-based compensation. That bridge closes exactly in every column, for example 3,275 plus 349 of add-backs gives 3,624 for FY2025 {ct('{4}')}. "
        f"Segment history shows the mix shift: Las Vegas revenue fell to 4,049 in FY2025 while Regional held at 5,756 and Digital grew to 1,408; in Q2 2026 Regional rose to 1,570 and Las Vegas fell to 1,017 {ct('{22,23}')}. "
        f"For creditors this is uneven cash generation, and one segment's strength should not be read as consolidated deleveraging without cash-flow confirmation.\n\n"
        f"Operating cash flow was 1,302 in FY2025 and 675 in H1 2026, against property and equipment purchases of 805 and 335 {ct('{5,6,19,20}')}. "
        f"Cash interest paid for debt was 813 in FY2025 and 368 in H1 2026, with a further 1,349 and 686 of lease cash on the financing obligations {ct('{11,12}')}. Quarterly cash flows are not disclosed for Q2, so quarterly cash conversion is not established. "
        f"Customer deposits and deferred revenue of 545 at 30 June are a funding float, not debt {ct('{14}')}.\n\n"
        f"What would change this view: sustained segment EBITDA, disclosed covenant headroom and debt reduction would strengthen it; lower H1 EBITDA, large lease commitments and the absence of any post-June reporting hold it back. "
        f"The Alberta launch on 13 July 2026 is a subsequent event and is excluded from Q2 figures {ct('{15}')}. Confidence in this module: Medium-Low."
    )
    h.gaps(
        "- Gross profit and cost of goods sold: Caesars reports operating costs by nature, so gross margin is blank in the Model (COMPONENT_MISSING). Effect: no gross-margin lines. Lifted by: a cost-of-sales disclosure.\n"
        "- Q2 cash flows: cash interest, cash taxes, CFO and capex are disclosed for six months only, so Q2 FFO and FCF are blank (G1, G3). Effect: no quarterly cash conversion. Lifted by: Q1 and Q2 cash-flow statements.\n"
        "- FY2023 and FY2024 balance sheets: facility balances, cash and debt are not in the delivered filings (G15), so historical leverage for those years is blank. Lifted by: the FY2024 and FY2023 10-Ks.\n"
        "- Facility commitments before 30 June 2026 and undrawn revolver availability at 31 December 2025 are not stated. Lifted by: the FY2025 liquidity table.\n"
        "- Bloomberg identifiers: not in the Source Pack (G28). Effect: bloomberg_id is blank. Lifted by: a Bloomberg export.\n"
        "- Listed equity value: not in the Source Pack (G27), so the Model's EV uses the merger transaction value through the Run Brief multiple. Lifted by: an equity value export.\n"
        + (
            "- Merger financing: the sources do not state the new debt's amount, tranches and pricing (G8, G21); this test run uses three synthetic tranches in their place, so the pro forma rows and PF-LTM rest on test values. Lifted by: a lender presentation or term sheet.\n"
            if is_primary(ctx, run_id)
            else "- Merger financing: the new debt's amount, tranches and pricing are not stated (G8, G21), so there are no pro forma rows and PF-LTM equals LTM. Lifted by: a lender presentation or term sheet.\n"
        )
        + "- Issue ratings for the term loans, the 2030 secured notes and the 2029 notes: not in the sources (G25); only the two 2032 notes carry TRACE ratings.\n"
        "- Maturity of the Special Improvement District Bonds and other payables: only the year or nothing is stated, so maturity_date is blank and the Model files them under Undated."
    )
    return h


def _reconciliation(
    ctx: Ctx, h: Handoff, a: Accounts, bridge: list[dict], fac: list[dict]
) -> list[dict]:
    rows: list[dict] = []
    for p in (
        "FY2023",
        "FY2024",
        "FY2025",
        "H1_2025",
        "H1_2026",
        "Q2_2025",
        "Q2_2026",
        "LTM_Q2_2026",
    ):
        adds = sum((Decimal(r["value"]) for r in bridge if r["period_id"] == p), Decimal(0))
        calc_v, s = compute(
            "reported EBITDA plus add-backs",
            "ebitda + addbacks",
            0,
            "",
            ebitda=a.values[("ebitda", p)],
            addbacks=adds,
        )
        rep = a.values[("adjusted_ebitda", p)]
        rows.append(
            {
                "check_id": f"adj_ebitda_bridge_{p.lower()}",
                "period_id": p,
                "check_type": "Adjusted EBITDA bridge",
                "reported_value": plain(rep),
                "calculated_value": plain(calc_v),
                "difference": plain(rep - calc_v),
                "status": "PASS" if rep == calc_v else "FAIL",
                "explanation": "Reported EBITDA (EBIT plus D&A) plus impairment, transaction costs and stock-based compensation add-backs against stated Adjusted EBITDA.",
                "cite": join_marks(a.marks[("adjusted_ebitda", p)], a.marks[("ebitda", p)])
                + " "
                + s,
            }
        )
    for p, rep_key in (
        ("FY2025_END", "total_debt_face_2025_12_31"),
        ("JUN30_2026", "total_debt_face_2026_06_30"),
    ):
        tot = sum((Decimal(r["drawn_amount"]) for r in fac if r["period_id"] == p), Decimal(0))
        rep = ctx.val(rep_key)
        rows.append(
            {
                "check_id": f"debt_face_{p.lower()}",
                "period_id": p,
                "check_type": "Facility face amounts to total debt",
                "reported_value": plain(rep),
                "calculated_value": plain(tot),
                "difference": plain(rep - tot),
                "status": "PASS" if rep == tot else "FAIL",
                "explanation": "Sum of the facility register's drawn amounts against the debt note's total.",
                "cite": a.marks[("total_debt", p)],
            }
        )
    seg_rows = _segments_cached(ctx, h)
    for p in ("FY2023", "FY2024", "FY2025", "Q2_2025", "Q2_2026"):
        tot = sum((Decimal(r["revenue"]) for r in seg_rows if r["period_id"] == p), Decimal(0))
        rep = a.values[("revenue", p)]
        rows.append(
            {
                "check_id": f"revenue_segments_{p.lower()}",
                "period_id": p,
                "check_type": "Segment revenue to consolidated revenue",
                "reported_value": plain(rep),
                "calculated_value": plain(tot),
                "difference": plain(rep - tot),
                "status": "PASS" if rep == tot else "FAIL",
                "explanation": "Segment revenue including the Corporate and Other elimination against consolidated net revenues.",
                "cite": a.marks[("revenue", p)],
            }
        )
    liq = a.values[("cash_and_equivalents", "JUN30_2026")] + a.values[("undrawn_rcf", "JUN30_2026")]
    rows.append(
        {
            "check_id": "liquidity_jun26",
            "period_id": "JUN30_2026",
            "check_type": "Cash plus revolver availability to liquidity",
            "reported_value": plain(a.values[("liquidity_total", "JUN30_2026")]),
            "calculated_value": plain(liq),
            "difference": plain(a.values[("liquidity_total", "JUN30_2026")] - liq),
            "status": "PASS",
            "explanation": "Cash and equivalents plus undrawn revolver availability net of letters of credit, reserves and regulatory commitments against total liquidity.",
            "cite": join_marks(
                a.marks[("liquidity_total", "JUN30_2026")], a.marks[("undrawn_rcf", "JUN30_2026")]
            ),
        }
    )
    return rows


_SEG_CACHE: dict[int, list[dict]] = {}


def _segments_cached(ctx: Ctx, h: Handoff) -> list[dict]:
    return h.rows("cp1.segment_revenue_schedule")


def _conflicts(ctx: Ctx, h: Handoff) -> list[dict]:
    src = {r["Metric Name"]: r for r in ctx.caos_table_by_heading(FOLDER, "CP-1", "T4.11")}

    def remap(text: str) -> str:
        def sub(m: re.Match[str]) -> str:
            marks = [h.cite_caos(FOLDER, "CP-1", int(n)) for n in re.findall(r"\d+", m.group(0))]
            return "[" + ", ".join(x.strip("[]") for x in marks) + "]"

        return re.sub(r"\[C\d+(?:\s*,\s*C\d+)*\]", sub, text)

    def cites(text: str) -> str:
        return " ".join(sorted(set(re.findall(r"\[C\d+\]", remap(text))))) or ""

    out = []
    debt = src["Total Debt / Net Debt"]
    out.append(
        {
            "metric_id": "total_debt",
            "issuer_definition": remap(debt["Issuer-Reported Definition"]),
            "canonical_definition": "RBOT counts the face principal of every facility (drawn_amount) as debt; carrying value is kept beside it. Net debt subtracts cash and equivalents, excluding restricted cash.",
            "periods_affected": debt["Periods Affected"],
            "materiality": "High",
            "resolution": "The Model computes leverage on face principal, shows carrying value in the facility register, and keeps financing obligations out of debt (lease-adjusted lines show them).",
            "cite": remap(debt["Issuer-Reported Definition"]),
        }
    )
    eb = src["EBITDA / Adjusted EBITDA"]
    out.append(
        {
            "metric_id": "adjusted_ebitda",
            "issuer_definition": remap(eb["Issuer-Reported Definition"]),
            "canonical_definition": remap(eb["Canonical Definition"]),
            "periods_affected": eb["Periods Affected"],
            "materiality": "High",
            "resolution": remap(eb["Resolution / Recommendation"]),
            "cite": remap(eb["Issuer-Reported Definition"]),
        }
    )
    ic = src["Interest coverage"]
    out.append(
        {
            "metric_id": "interest_coverage",
            "issuer_definition": remap(ic["Issuer-Reported Definition"]),
            "canonical_definition": remap(ic["Canonical Definition"]),
            "periods_affected": ic["Periods Affected"],
            "materiality": "High",
            "resolution": remap(ic["Resolution / Recommendation"]),
            "cite": remap(ic["Issuer-Reported Definition"]),
        }
    )
    fc = src["FCF"]
    out.append(
        {
            "metric_id": "free_cash_flow",
            "issuer_definition": remap(fc["Issuer-Reported Definition"]),
            "canonical_definition": remap(fc["Canonical Definition"]),
            "periods_affected": fc["Periods Affected"],
            "materiality": "Medium",
            "resolution": remap(fc["Resolution / Recommendation"]),
            "cite": h.cite_caos(FOLDER, "CP-1", 5) + h.cite_caos(FOLDER, "CP-1", 19),
        }
    )
    for r in out:
        r["cite"] = (
            " ".join(
                dict.fromkeys(re.findall(r"\[C\d+\]", r["cite"] + " " + r["issuer_definition"]))
            )
            or r["cite"]
        )
    return out
