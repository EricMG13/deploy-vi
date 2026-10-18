"""Larchmere CP-1: canonical data foundation. Every input is a synthetic fact (facts.py); everything derived is computed.

Mirrors czr/cp_1.py's register structure so ModelBuilder reads it unchanged. LTM columns are FY2025 + H1 2026 - H1 2025.
"""

from __future__ import annotations

from decimal import Decimal

from core import GAP, Ctx, D, FixtureError, Handoff, compute, plain
from helpers import join_marks

from . import derived as X
from . import facts as F
from .facts import syn

FLOWS = [  # metric, fact key, sign
    ("revenue", "revenue", 1),
    ("adjusted_ebitda", "adjusted_ebitda", 1),
    ("d_and_a", "d_and_a", 1),
    ("interest_expense", "interest_expense", 1),
    ("cash_interest_paid", "cash_interest", -1),
    ("lease_cash_paid", "lease_cash", -1),
    ("cash_taxes_paid", "cash_taxes", -1),
    ("cfo", "cfo", 1),
    ("capex", "capex", -1),
]
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
    ("FY2023_END", "2023", GAP, "PERIOD_END", "2023-12-31", "2023-12-31", "1", GAP),
    ("FY2024_END", "2024", GAP, "PERIOD_END", "2024-12-31", "2024-12-31", "1", GAP),
    ("FY2025_END", "2025", GAP, "PERIOD_END", "2025-12-31", "2025-12-31", "1", GAP),
    ("JUN30_2026", "2026", GAP, "PERIOD_END", "2026-06-30", "2026-06-30", "1", GAP),
]
ALL_FLOW = [*F.FLOW_PERIODS, "LTM_Q2_2026"]


class Accounts:
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


def _accounts(h: Handoff) -> Accounts:
    a = Accounts()
    for metric, key, sign in FLOWS:
        mk = syn(h, key)
        for p in F.FLOW_PERIODS:
            a.add(metric, p, X.flow(key, p) * sign, "Reported", mk, f"{key.replace('_', ' ')}, {p}")
        v, s = X.ltm(key, label=f"LTM {metric}")
        a.add(
            metric,
            "LTM_Q2_2026",
            v * sign,
            "Calculated",
            mk,
            s if sign == 1 else s + " (outflow negative)",
        )
    mk_ab = join_marks(
        *(syn(h, k) for _, _, _, k, _ in X.ADDBACKS), syn(h, "adjusted_ebitda"), syn(h, "d_and_a")
    )
    for p in ALL_FLOW:
        v, s = compute(
            "reported EBITDA",
            "adjusted - addbacks",
            0,
            "",
            adjusted=X.flow("adjusted_ebitda", p),
            addbacks=X.addback_total(p),
        )
        a.add("ebitda", p, v, "Calculated", mk_ab, s)
        e, s2 = compute("EBIT", "ebitda - da", 0, "", ebitda=v, da=X.flow("d_and_a", p))
        a.add("ebit", p, e, "Calculated", mk_ab, s2)
    for bp in F.BALANCE_PERIODS:
        a.add(
            "cash_and_equivalents",
            bp,
            X.cash(bp),
            "Reported",
            syn(h, "cash_balance"),
            f"cash and equivalents, {bp}",
        )
        tdv, tds = compute(
            "total face debt",
            "rcf + tlb + sl + notes",
            0,
            "",
            rcf=X.facility_balance("llg_rcf", bp),
            tlb=X.facility_balance("llg_tlb", bp),
            sl=X.facility_balance("llg_2l", bp),
            notes=X.facility_balance("llg_notes", bp),
        )
        a.add(
            "total_debt",
            bp,
            tdv,
            "Calculated",
            join_marks(syn(h, "rcf_drawn"), syn(h, "term_debt_face")),
            tds,
        )
        a.add(
            "financing_obligations",
            bp,
            D(F.val("financing_obligations")[bp]),
            "Reported",
            syn(h, "financing_obligations"),
            f"master-lease financing obligation, {bp}",
        )
        a.add(
            "undrawn_rcf",
            bp,
            D(F.val("undrawn_rcf")[bp]),
            "Reported",
            syn(h, "undrawn_rcf"),
            f"undrawn revolver availability, {bp}",
        )
        liq, ls = compute(
            "liquidity", "cash + undrawn", 0, "", cash=X.cash(bp), undrawn=F.val("undrawn_rcf")[bp]
        )
        a.add(
            "liquidity_total",
            bp,
            liq,
            "Calculated",
            join_marks(syn(h, "cash_balance"), syn(h, "undrawn_rcf")),
            ls,
        )
    dd, ds = compute(
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
        dd,
        "Calculated",
        a.marks[("total_debt", "JUN30_2026")],
        ds,
    )
    nc, ns = compute(
        "net change in cash",
        "cfo + capex + debt",
        0,
        "",
        cfo=a.values[("cfo", "H1_2026")],
        capex=a.values[("capex", "H1_2026")],
        debt=dd,
    )
    a.add(
        "net_cash_change",
        "H1_2026",
        nc,
        "Calculated",
        join_marks(
            a.marks[("cfo", "H1_2026")],
            a.marks[("capex", "H1_2026")],
            a.marks[("total_debt", "JUN30_2026")],
        ),
        ns,
    )
    if a.values[("net_cash_change", "H1_2026")] != X.cash("JUN30_2026") - X.cash("FY2025_END"):
        raise FixtureError("H1 2026 net change in cash does not tie to the cash balances")
    return a


def _bridge(h: Handoff, a: Accounts) -> list[dict]:
    rows = []
    for prio, (aid, label, cls, key, status) in enumerate(X.ADDBACKS, 1):
        mk = syn(h, key)
        for p in ALL_FLOW:
            if p == "LTM_Q2_2026":
                v, s = X.ltm(key, label=f"LTM {aid}")
                loc = s
            else:
                v, loc = X.flow(key, p), f"{label}, {p}"
            rows.append(
                {
                    "addback_id": aid,
                    "addback_label": label,
                    "addback_classification": cls,
                    "realization_status": status,
                    "display_priority": str(prio),
                    "period_id": p,
                    "value": plain(v),
                    "source_id": mk,
                    "source_locator": loc,
                }
            )
    for p in ALL_FLOW:
        tot = sum((Decimal(r["value"]) for r in rows if r["period_id"] == p), Decimal(0))
        if a.values[("ebitda", p)] + tot != a.values[("adjusted_ebitda", p)]:
            raise FixtureError(f"adjusted EBITDA bridge does not close for {p}")
    return rows


def _segments(h: Handoff) -> list[dict]:
    rows = []
    mk = syn(h, "segment_revenue")
    for sid, (name, prio, vals) in F.val("segment_revenue").items():
        for p, v in zip(F.FLOW_PERIODS, vals, strict=True):
            rows.append(_seg(sid, name, prio, p, Decimal(v), mk, "segment note"))
        s = compute(
            f"LTM {name} revenue", "fy + h1 - ph1", 0, "", fy=vals[2], h1=vals[4], ph1=vals[3]
        )
        rows.append(_seg(sid, name, prio, "LTM_Q2_2026", s[0], mk, s[1]))
    return rows


def _seg(sid: str, name: str, prio: int, p: str, v: Decimal, mk: str, loc: str) -> dict:
    return {
        "segment_id": sid,
        "segment_name": name,
        "segment_type": "OPERATING_SEGMENT",
        "display_priority": str(prio),
        "period_id": p,
        "revenue": plain(v),
        "source_id": mk,
        "source_locator": loc,
    }


def _kpis(h: Handoff) -> list[dict]:
    rows = []
    mk = syn(h, "operating_kpis")
    prio = 0
    for kid, (label, unit, vt, vals) in F.val("operating_kpis").items():
        prio += 1
        for p, v in zip(F.FLOW_PERIODS, vals, strict=True):
            rows.append(
                {
                    "kpi_id": kid,
                    "kpi_label": label,
                    "display_priority": str(prio),
                    "period_id": p,
                    "value": plain(v),
                    "unit": unit,
                    "value_type": vt,
                    "source_id": mk,
                    "source_locator": "operating statistics, annual and interim reports",
                }
            )
    mk2 = syn(h, "operating_counts")
    for kid, (label, v) in F.val("operating_counts").items():
        prio += 1
        rows.append(
            {
                "kpi_id": kid,
                "kpi_label": label,
                "display_priority": str(prio),
                "period_id": "JUN30_2026",
                "value": plain(v),
                "unit": "count",
                "value_type": "PERIOD_END",
                "source_id": mk2,
                "source_locator": "business overview, 30 June 2026",
            }
        )
    return rows


def _facilities(h: Handoff) -> list[dict]:
    rows = []
    terms_mark = syn(h, "facility_terms")
    carry = F.val("carrying_discount_pct")
    for fid in F.FACILITY_IDS:
        t = F.val("facility_terms")[fid]
        amort = GAP
        if t.get("amort_pct"):
            av, _ = compute(
                "annual amortisation",
                "pct / 100 * original",
                1,
                "",
                pct=t["amort_pct"],
                original=t["original"],
            )
            amort = plain(av)
        for bp in F.BALANCE_PERIODS:
            face = X.facility_balance(fid, bp)
            book, _ = compute(
                "carrying value", "face * (100 - disc) / 100", 1, "", face=face, disc=carry[fid]
            )
            fixed = t.get("fixed", GAP)
            bal_mark = syn(h, "rcf_drawn" if fid == "llg_rcf" else "term_debt_face")
            marks = join_marks(
                terms_mark,
                bal_mark,
                syn(h, "carrying_discount_pct"),
                syn(h, "rcf_commitment") if fid == "llg_rcf" else "",
            )
            rows.append(
                {
                    "facility_id": fid,
                    "facility_name": t["name"],
                    "period_id": bp,
                    "facility_type": t["ftype"],
                    "currency": "USD",
                    "carrying_value": plain(book),
                    "drawn_amount": plain(face),
                    "commitment": plain(F.val("rcf_commitment")) if fid == "llg_rcf" else GAP,
                    "secured_status": t["sec"],
                    "seniority": t["sen"],
                    "margin_or_coupon": t["margin"],
                    "maturity_date": t["maturity"],
                    "lease_classification": "NOT_APPLICABLE",
                    "rate_type": "Fixed" if fixed != GAP else "Floating",
                    "reference_rate": GAP if fixed != GAP else "Term SOFR",
                    "spread_bps": GAP if fixed != GAP else str(t["spread"]),
                    "floor_bps": GAP if fixed != GAP else str(t["floor"]),
                    "fixed_rate": fixed,
                    "annual_amortisation": amort,
                    "source_id": marks,
                    "source_locator": "debt note and credit agreement, facility terms and balances",
                }
            )
    return rows


def _new_money_rows(h: Handoff, fac_rows: list[dict]) -> list[dict]:
    """NEW-1, the sponsor's priming loan, as undrawn facility rows (both balance dates, so the Model has a line to add to)
    and the pro forma adjustments: new debt, cash interest at the talk mid and cash to the balance sheet net of OID."""
    nm = F.val("new_money")
    tid, size, oid = nm["tranche_id"], D(nm["size"]), D(nm["oid"])
    m_new, m_sofr = syn(h, "new_money"), syn(h, "sofr_spot")
    for period in ("FY2025_END", "JUN30_2026"):
        fac_rows.append(
            {
                "facility_id": tid,
                "facility_name": nm["instrument"],
                "period_id": period,
                "facility_type": "Term loan",
                "currency": "USD",
                "carrying_value": "0",
                "drawn_amount": "0",
                "commitment": plain(size) if period == "JUN30_2026" else GAP,
                "secured_status": "SECURED",
                "seniority": "Super-priority senior secured",
                "margin_or_coupon": f"SOFR + {nm['spread_mid']} bps",
                "maturity_date": nm["maturity"],
                "lease_classification": "NOT_APPLICABLE",
                "rate_type": "Floating",
                "reference_rate": "Term SOFR",
                "spread_bps": str(nm["spread_mid"]),
                "floor_bps": GAP,
                "fixed_rate": GAP,
                "annual_amortisation": GAP,
                "source_id": m_new,
                "source_locator": "synthetic undrawn proposal: pro forma only, nothing is drawn at the balance-sheet date",
            }
        )
    interest, int_s = compute(
        f"{tid} annual cash interest at the talk mid",
        "-size * (sofr + margin / 100) / 100",
        1,
        "",
        size=size,
        sofr=D(F.val("sofr_spot")),
        margin=D(nm["spread_mid"]),
    )
    cash, cash_s = compute(
        f"{tid} cash proceeds net of OID", "size * oid / 100", 1, "", size=size, oid=oid
    )
    common = {
        "period_id": "LTM_Q2_2026",
        "effective_date": "2026-06-30",
    }
    return [
        {
            **common,
            "adjustment_id": f"PF-{tid}-DEBT",
            "label": f"{nm['instrument']} funded at close (pro forma)",
            "classification": "NEW_DEBT",
            "metric_id": f"facility:{tid}",
            "value": plain(size),
            "source_id": m_new,
            "source_locator": "fixtures/larchmere/facts.py#new_money; shown as if drawn at the LTM balance-sheet date",
        },
        {
            **common,
            "adjustment_id": f"PF-{tid}-INT",
            "label": f"Annual cash interest on {tid} at the talk mid (pro forma)",
            "classification": "INTEREST",
            "metric_id": "cash_interest_paid",
            "value": plain(interest, 1),
            "source_id": join_marks(m_new, m_sofr),
            "source_locator": int_s,
        },
        {
            **common,
            "adjustment_id": "PF-CASH",
            "label": "Cash to the balance sheet from the new money, net of OID",
            "classification": "CASH",
            "metric_id": "cash_and_equivalents",
            "value": plain(cash, 1),
            "source_id": m_new,
            "source_locator": cash_s,
        },
    ]


def _identity(h: Handoff) -> list[dict]:
    rows = []
    r = F.val("ratings")["facility"]
    ids = F.val("identifiers")
    m_rat, m_id = syn(h, "ratings"), syn(h, "identifiers")
    for fid in F.FACILITY_IDS:
        t = F.val("facility_terms")[fid]
        notes = fid == "llg_notes"
        rows.append(
            {
                "facility_id": fid,
                "instrument_name": t["name"],
                "debt_type": t["dt"],
                "bloomberg_id": ids[fid][0],
                "isin": GAP,
                "cusip": ids[fid][1],
                "issuer_entity": F.ISSUER if notes else F.OPCO,
                "rating_moodys": r[fid][0],
                "rating_sp": r[fid][1],
                "rating_fitch": GAP,
                "call_schedule": "callable at 102.063 from 2025-09-15 and at par from 2026-09-15"
                if notes
                else GAP,
                "listed_market": "No",
                "cite": join_marks(m_rat, m_id),
            }
        )
    return rows


def _reconciliation(h: Handoff, a: Accounts, bridge: list[dict]) -> list[dict]:
    rows = []
    for p in ALL_FLOW:
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
                "explanation": "Reported EBITDA (EBIT plus D&A) plus the three add-backs against stated Adjusted EBITDA.",
                "cite": join_marks(a.marks[("adjusted_ebitda", p)], a.marks[("ebitda", p)])
                + " "
                + s,
            }
        )
    seg = h.rows("cp1.segment_revenue_schedule")
    for p in ALL_FLOW:
        tot = sum((Decimal(r["revenue"]) for r in seg if r["period_id"] == p), Decimal(0))
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
                "explanation": "The three operating segments against consolidated net revenues.",
                "cite": a.marks[("revenue", p)],
            }
        )
    cash_change = X.cash("JUN30_2026") - X.cash("FY2025_END")
    calc_v = a.values[("net_cash_change", "H1_2026")]
    rows.append(
        {
            "check_id": "cash_change_h1_2026",
            "period_id": "H1_2026",
            "check_type": "Cash flow to change in cash",
            "reported_value": plain(cash_change),
            "calculated_value": plain(calc_v),
            "difference": plain(cash_change - calc_v),
            "status": "PASS" if cash_change == calc_v else "FAIL",
            "explanation": "CFO plus capital spending plus net debt drawn against the movement in unrestricted cash.",
            "cite": a.marks[("net_cash_change", "H1_2026")],
        }
    )
    return rows


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx, "CP-1", F.ISSUER_ID, run_id, F.AS_OF, ["CP-0"], fixture_file="larchmere/cp_1.py"
    )
    h.qa("Restricted")
    a = _accounts(h)
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
    bridge = _bridge(h, a)
    h.table("cp1.adjusted_ebitda_bridge", bridge)
    h.table("cp1.segment_revenue_schedule", _segments(h))
    h.table("cp1.operating_kpi_schedule", _kpis(h))
    fac_rows = _facilities(h)
    pf_rows = _new_money_rows(h, fac_rows)
    h.table("cp1.debt_facility_register", fac_rows)
    h.table("cp1.pro_forma_adjustment_register", pf_rows)
    h.table(
        "cp1.cp_model_segment_allocation",
        [
            {"slot_id": "DIVISION_1", "component_segment_ids": "seg_gulf_coast"},
            {"slot_id": "DIVISION_2", "component_segment_ids": "seg_mid_south"},
            {"slot_id": "DIVISION_3", "component_segment_ids": "seg_online"},
        ],
    )
    h.table("cp1.equity_value", [])
    h.table("cp1.instrument_identity", _identity(h))
    h.table("cp1.reconciliation_checks", _reconciliation(h, a, bridge))
    m_adj = syn(h, "adjusted_ebitda")
    m_sav = syn(h, "addback_run_rate_savings")
    m_rent = syn(h, "rent_in_covenant_ebitda")
    h.table(
        "cp1.definition_conflicts",
        [
            {
                "metric_id": "adjusted_ebitda",
                "issuer_definition": "Company-defined Adjusted EBITDA adds back run-rate cost savings of 16 LTM that are announced but not delivered.",
                "canonical_definition": "RBOT counts only realized add-backs; unrealized run-rate savings are left out of SSIM EBITDA.",
                "periods_affected": "FY2024, FY2025, H1 2025, H1 2026, LTM",
                "materiality": "High",
                "resolution": "CP-1D rules on each add-back; the Model uses SSIM EBITDA and shows the stated figure beside it.",
                "cite": join_marks(m_adj, m_sav),
            },
            {
                "metric_id": "covenant_ebitda",
                "issuer_definition": "Consolidated EBITDA for the springing test is stated after cash rent under the master lease.",
                "canonical_definition": "Adjusted EBITDA in the Model is before master-lease rent, because the lease is a financing obligation.",
                "periods_affected": "LTM Q2 2026",
                "materiality": "High",
                "resolution": "CP-4 tests the covenant on covenant EBITDA (stated Adjusted EBITDA less cash rent) and the Model leverage on SSIM EBITDA before rent.",
                "cite": m_rent,
            },
            {
                "metric_id": "total_debt",
                "issuer_definition": "Reported debt is carrying value net of unamortised discount and fees.",
                "canonical_definition": "RBOT counts face principal of every facility; carrying value is kept beside it.",
                "periods_affected": "All balance dates",
                "materiality": "Low",
                "resolution": "Leverage uses face debt; the master-lease obligation stays outside debt and enters the lease-adjusted lines.",
                "cite": syn(h, "carrying_discount_pct"),
            },
        ],
    )
    h.table(
        "cp1.entity_profile",
        [
            {
                "entity": F.ISSUER,
                "role": "Registrant and parent guarantor; the operating company is the borrower of the revolver and term loans",
                "fiscal_year_end": "December 31",
                "reporting_currency": "USD",
                "reporting_unit": "MILLIONS",
                "perimeter": "Parent and consolidated restricted subsidiaries; master-lease landlord excluded",
                "accounting_basis": "US GAAP; FY audited, interim unaudited",
                "cite": syn(h, "profile"),
            }
        ],
    )
    ltm_rev, _ = X.ltm("revenue")
    ltm_e, _ = X.ltm("adjusted_ebitda")
    ltm_td = a.values[("total_debt", "JUN30_2026")]
    lev, lev_s = compute(
        "total leverage on face debt", "debt / ebitda", 2, "x", debt=ltm_td, ebitda=ltm_e
    )
    ltm_cfo = a.values[("cfo", "LTM_Q2_2026")]
    ltm_capex = a.values[("capex", "LTM_Q2_2026")]
    fcf, fcf_s = compute("LTM free cash flow", "cfo + capex", 0, "", cfo=ltm_cfo, capex=ltm_capex)
    seg = F.val("segment_revenue")
    drop = {
        k: compute(f"{k} H1 change", "(h1 - ph1) / ph1 * 100", 1, "", h1=v[2][4], ph1=v[2][3])[0]
        for k, v in seg.items()
    }
    gc_s, ms_s, on_s = (
        plain(abs(drop[k]), 1) for k in ("seg_gulf_coast", "seg_mid_south", "seg_online")
    )
    m = {
        k: syn(h, k)
        for k in (
            "revenue",
            "adjusted_ebitda",
            "rcf_drawn",
            "cash_balance",
            "cash_interest",
            "lease_cash",
            "cfo",
            "capex",
            "segment_revenue",
            "financing_obligations",
            "term_debt_face",
            "addback_run_rate_savings",
        )
    }
    h.analysis(
        f"The canonical record shows a company whose cash earnings no longer cover its fixed charges. LTM net revenues to 30 June 2026 are {plain(ltm_rev)} against {plain(X.flow('revenue', 'FY2025'))} in FY2025 {m['revenue']}, "
        f"and company-defined Adjusted EBITDA is {plain(ltm_e)} against 241 in FY2025; first-half Adjusted EBITDA fell 25.0% to 93 {m['adjusted_ebitda']}. "
        f"Face debt at 30 June 2026 is {plain(ltm_td)}, so total leverage on the company's EBITDA is {lev}x ({lev_s}); the revolver is fully drawn at 200 {m['rcf_drawn']}. USD millions throughout; confidence is Restricted.\n\n"
        f"Cash flow is the sharper signal. Operating cash flow was 14 in FY2025 and -21 in H1 2026, and capital spending was 21 in the half {m['cfo']}{m['capex']}, so LTM free cash flow is {plain(fcf)} ({fcf_s}). "
        f"Cash interest of 147 LTM and master-lease cash rent of 62 {m['cash_interest']}{m['lease_cash']} absorb all of the company's 210 of Adjusted EBITDA. Unrestricted cash is 62 {m['cash_balance']}.\n\n"
        f"Reported EBITDA is Adjusted EBITDA less three add-backs; the bridge closes in every period. Run-rate cost savings of 16 LTM are announced but not delivered and are carried as NOT_STATED for CP-1D to rule on {m['addback_run_rate_savings']}. "
        f"Segment revenue shows the mix: Gulf Coast fell {gc_s}% and Mid-South {ms_s}% in H1 2026 on H1 2025, and Online {on_s}% {m['segment_revenue']}. "
        f"The master-lease financing obligation of 1,149 stays outside debt {m['financing_obligations']}. Facility terms and balances are in the debt register {m['term_debt_face']}."
    )
    h.gaps(
        "- Quarterly cash flows: only half-year figures are reported, so Q2 FFO and FCF are blank. Effect: no quarterly cash conversion. Lifted by: quarterly cash-flow statements.\n"
        "- Gross profit and cost of goods sold: costs are reported by nature, so gross margin is blank in the Model. Lifted by: a cost-of-sales disclosure.\n"
        "- Bloomberg identifiers and ISINs for the loans: not in the pack; identifiers shown are the market file's internal codes.\n"
        "- Listed equity value: none, because the sponsor owns the company; the Model's EV uses the Run Brief multiple.\n"
        "- Issue ratings for the revolver: shown at the term loan level from the market file; no agency report is in the pack."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
