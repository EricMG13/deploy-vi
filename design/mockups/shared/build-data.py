#!/usr/bin/env python3
"""Build data.js (window.RBOT_DATA) for the RBOT Report mockups. Standard library only.

Inputs
  czr.json        real Caesars figures, each with file, line and excerpt (or a formula),
                  plus the gaps the extraction could not close.
  Test CLO I CSVs synthetic portfolio files (mandate, exposure report, constraints monitor).

Rules kept here
  * every reported figure becomes a citation C<n> with file, line and verbatim excerpt;
  * every calculated figure becomes K<n> with its formula and the ids of its inputs,
    computed exactly with Decimal (no float reaches a printed value);
  * every gap stays a gap G<n> with its reason (never 0);
  * negatives print in parentheses, as the filings print them;
  * judgement (scores, recommendations, thesis) sits in a separate `illustrative` block,
    each item flagged illustrative: true; no RBOT run exists;
  * the Test CLO I portfolio block is flagged synthetic: true.

Usage: python3 build-data.py [czr.json] [portfolio-dir]
"""

from __future__ import annotations

import re
import csv
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CZR = Path(
    "/private/tmp/claude-501/-Users-ericguei-Documents-Deploy-VI/"
    "bad82dc1-8ed2-470d-b186-e64741787ca5/scratchpad/mockup-data/czr.json"
)
DEFAULT_PORTFOLIO = Path("/Users/ericguei/Desktop/Portfolio Data ")  # trailing space is real
OUT = HERE / "data.js"

CITES: dict[str, dict] = {}
CALCS: dict[str, dict] = {}
GAPS: dict[str, dict] = {}
FIG: dict[str, dict] = {}  # key -> datum
KEY_REF: dict[str, str] = {}  # key -> C/K id
GAP_BY_KEY: dict[str, str] = {}


# ---------------------------------------------------------------- formatting
def dec(text: str) -> Decimal | None:
    t = str(text).strip().replace(",", "").replace("$", "")
    if t.startswith("(") and t.endswith(")"):
        t = "-" + t[1:-1]
    try:
        return Decimal(t)
    except Exception:  # noqa: BLE001 - non-numeric source values (dates, names, "—") are kept as text
        return None


def paren(text: str) -> str:
    """'-62' -> '(62)', as the filings print negatives."""
    t = str(text)
    return "(" + t[1:] + ")" if t.startswith("-") else t


def q(d: Decimal, places: int) -> Decimal:
    return d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def fmt(d: Decimal, places: int = 0) -> str:
    v = q(d, places)
    s = f"{abs(v):,.{places}f}"
    return f"({s})" if v < 0 else s


# ---------------------------------------------------------------- registries
def cite(key: str, rec: dict, label: str | None = None) -> str:
    cid = f"C{len(CITES) + 1}"
    CITES[cid] = {
        "id": cid,
        "key": key,
        "label": label or rec.get("label", key),
        "period": rec.get("period"),
        "value": rec["value"],
        "unit": rec.get("unit"),
        "file": rec["file"],
        "line": rec["line"],
        "locator": f"line {rec['line']}",
        "excerpt": rec["excerpt"],
    }
    KEY_REF[key] = cid
    return cid


def gap(field: str, reason: str, origin: str = "czr.json") -> str:
    gid = f"G{len(GAPS) + 1}"
    reason = re.sub(r"\s*\(recorded as [^)]*\)", "", reason)  # the extraction's own field names are not for the reader
    GAPS[gid] = {"id": gid, "field": field, "reason": reason, "origin": origin}
    GAP_BY_KEY[field] = gid
    return gid


def gap_datum(gid: str) -> dict:
    return {"v": None, "prov": "gap", "ref": gid, "reason": GAPS[gid]["reason"]}


def datum(key: str) -> dict:
    return dict(FIG[key])


def val(key: str) -> Decimal:
    d = dec(FIG[key]["raw"])
    if d is None:
        raise ValueError(f"{key} is not numeric: {FIG[key]['raw']!r}")
    return d


def calc(key: str, label: str, period: str, value: Decimal, places: int, unit: str,
         formula: str, inputs: list[str], note: str | None = None) -> dict:
    """Register a calculated figure. `formula` names inputs by key in {braces}."""
    kid = f"K{len(CALCS) + 1}"
    shown = formula
    for k in inputs:
        shown = shown.replace("{" + k + "}", f"{FIG[k]['label']} [{KEY_REF[k]}]")
    text = fmt(value, places)
    CALCS[kid] = {
        "id": kid, "key": key, "label": label, "period": period, "value": text, "unit": unit,
        "formula": shown, "formula_keys": formula.replace("{", "").replace("}", ""),
        "inputs": [KEY_REF[k] for k in inputs], "note": note,
    }
    KEY_REF[key] = kid
    FIG[key] = {"v": text, "raw": str(q(value, places)), "unit": unit, "label": label,
                "period": period, "prov": "calculated", "ref": kid}
    return FIG[key]


def strip(d: dict) -> dict:
    """Chart datum: only the fields the chart kit reads."""
    out = {k: d[k] for k in ("v", "prov", "ref", "reason", "projected") if k in d and d[k] is not None}
    if d.get("v") is None:
        out["v"] = None
    return out


# ---------------------------------------------------------------- load czr.json
def load_czr(path: Path) -> dict:
    src = json.loads(path.read_text())

    def walk(prefix: str, node: dict) -> None:
        for k, v in node.items():
            if isinstance(v, dict) and "value" in v and "file" in v:
                key = f"{prefix}.{k}"
                cid = cite(key, {**v, "label": k.replace("_", " "), "unit": "text"})
                FIG[key] = {"v": v["value"], "raw": v["value"], "unit": "text", "label": k.replace("_", " "),
                            "prov": "cited", "ref": cid}
            elif isinstance(v, dict):
                walk(f"{prefix}.{k}", v)

    walk("issuer", src["issuer"])
    pending_calcs = []
    for f in src["figures"]:
        if f.get("basis") == "calculated":
            pending_calcs.append(f)
            continue
        cid = cite(f["key"], f)
        raw = f["value"]
        d = {"v": paren(raw), "raw": raw, "unit": f["unit"], "label": f["label"], "period": f["period"],
             "prov": "cited", "ref": cid}
        if raw.strip() == "—":
            d["reason"] = "shown as — (nil) in the source"
        FIG[f["key"]] = d
    for f in pending_calcs:
        kid = f"K{len(CALCS) + 1}"
        keys = [t for t in f["formula"].replace("+", " ").replace("-", " ").split() if t in KEY_REF]
        shown = f["formula"]
        for k in sorted(keys, key=len, reverse=True):
            shown = shown.replace(k, f"{FIG[k]['label']} {FIG[k]['period']} [{KEY_REF[k]}]")
        CALCS[kid] = {"id": kid, "key": f["key"], "label": f["label"], "period": f["period"],
                      "value": paren(f["value"]), "unit": f["unit"], "formula": shown,
                      "formula_keys": f["formula"], "inputs": [KEY_REF[k] for k in keys], "note": None}
        KEY_REF[f["key"]] = kid
        FIG[f["key"]] = {"v": paren(f["value"]), "raw": f["value"], "unit": f["unit"], "label": f["label"],
                         "period": f["period"], "prov": "calculated", "ref": kid}
    for g in src["gaps"]:
        gap(g["key"], g["why"])
    return src


# ---------------------------------------------------------------- derived figures
def derive() -> None:
    # Gaps this build adds (the extraction carries no such figure).
    gap("total_debt_cash_fy2023_fy2024",
        "FY2023 and FY2024 year-end debt and cash were not extracted (the extraction carries balance-sheet "
        "figures at 2025-12-31 and 2026-06-30 only)", "build-data.py")
    gap("liquidity_fy2023_fy2025",
        "total liquidity is stated only at 2026-06-30 (Q2 2026 earnings release liquidity table)", "build-data.py")
    gap("covenant_levels",
        "no financial maintenance covenant level is cited in the extracted figures; the credit agreement "
        "and its amendments are not in the extraction", "build-data.py")
    gap("loan_margins_prices",
        "term loan margins, bids and asks are not in the sources (no loan pricing or LSTA marks); "
        "TRACE covers the two CZR notes only", "build-data.py")
    gap("spread_to_treasury",
        "spreads are not in the sources; FINRA TRACE pages give last price and yield only", "build-data.py")
    gap("reported_ebitda_ltm",
        "the FY2025 and H1 2025 reconciliation lines (taxes, other income, NCI) were not extracted, "
        "so LTM Reported EBITDA cannot be built", "build-data.py")
    gap("pf_ltm",
        "pro forma LTM needs the merger's new debt (amount, tranches, pricing), which the sources do not "
        "state", "build-data.py")
    gap("unrealized_addbacks",
        "no unrealized add-backs (run-rate synergies, cost saves) are marketed in the sources; a lender "
        "presentation is not in the Source Pack", "build-data.py")
    gap("gross_profit",
        "Caesars does not report gross profit; not in the sources", "build-data.py")
    gap("morningstar_issuer_id", "Morningstar Issuer ID is not in the sources", "build-data.py")
    gap("issuer_ratings",
        "no issuer or corporate family rating in the sources; only issue-level ratings on the FINRA TRACE "
        "pages (see the rating outlooks gap)", "build-data.py")
    gap("cash_flow_detail_h1_2026",
        "investing (other than capex) and financing cash flows for H1 2026 were not extracted", "build-data.py")
    gap("equity_market_value",
        "no listed equity value (Bloomberg) in the sources; EV is taken at the merger's stated transaction "
        "value instead", "build-data.py")
    gap("figi",
        "Bloomberg IDs (FIGI) are not in the sources; CUSIPs appear on the TRACE pages only", "build-data.py")

    # ---- LTM pieces
    calc("ltm_interest_expense_q2_2026", "LTM interest expense, net", "LTM Q2 2026",
         val("interest_expense_fy2025") + val("interest_expense_h1_2026") - val("interest_expense_h1_2025"), 0,
         "USD millions", "{interest_expense_fy2025} + {interest_expense_h1_2026} - {interest_expense_h1_2025}",
         ["interest_expense_fy2025", "interest_expense_h1_2026", "interest_expense_h1_2025"])
    calc("ltm_cash_interest_rent_q2_2026", "LTM cash interest paid for rent (GLPI and VICI leases)", "LTM Q2 2026",
         val("cash_interest_rent_fy2025") + val("cash_interest_rent_h1_2026") - val("cash_interest_rent_h1_2025"), 0,
         "USD millions", "{cash_interest_rent_fy2025} + {cash_interest_rent_h1_2026} - {cash_interest_rent_h1_2025}",
         ["cash_interest_rent_fy2025", "cash_interest_rent_h1_2026", "cash_interest_rent_h1_2025"])
    calc("ltm_income_taxes_paid_q2_2026", "LTM income taxes paid, net", "LTM Q2 2026",
         val("income_taxes_paid_fy2025") + val("income_taxes_paid_h1_2026") - val("income_taxes_paid_h1_2025"), 0,
         "USD millions", "{income_taxes_paid_fy2025} + {income_taxes_paid_h1_2026} - {income_taxes_paid_h1_2025}",
         ["income_taxes_paid_fy2025", "income_taxes_paid_h1_2026", "income_taxes_paid_h1_2025"])

    periods = {"FY2023": "fy2023", "FY2024": "fy2024", "FY2025": "fy2025", "H1 2025": "h1_2025",
               "H1 2026": "h1_2026", "LTM Q2 2026": "ltm"}

    def k(base: str, p: str) -> str:
        return f"ltm_{base}_q2_2026" if p == "ltm" else f"{base}_{p}"

    # ---- growth, margins, FFO, FCF per period
    prev = {"fy2024": "fy2023", "fy2025": "fy2024", "h1_2026": "h1_2025"}
    for name, p in periods.items():
        rev, ebitda = k("net_revenues", p), k("adj_ebitda", p)
        calc(f"ebitda_margin_{p}", "Adjusted EBITDA margin", name, val(ebitda) / val(rev) * 100, 1, "%",
             "{" + ebitda + "} / {" + rev + "} x 100", [ebitda, rev])
        if p in prev:
            for base, lab in (("net_revenues", "Net revenues growth"), ("adj_ebitda", "Adjusted EBITDA growth")):
                a, b = k(base, p), k(base, prev[p])
                calc(f"{base}_growth_{p}", lab, name, (val(a) / val(b) - 1) * 100, 1, "%",
                     "({" + a + "} / {" + b + "} - 1) x 100", [a, b])
        ci, cr, tx = k("cash_interest_debt", p), k("cash_interest_rent", p), k("income_taxes_paid", p)
        if p == "ltm":
            tx = "ltm_income_taxes_paid_q2_2026"
        ffo = val(ebitda) - val(ci) - val(cr) - val(tx)
        calc(f"ffo_{p}", "FFO (Adjusted EBITDA less cash interest, lease cash interest and cash tax)", name, ffo, 0,
             "USD millions", "{" + ebitda + "} - {" + ci + "} - {" + cr + "} - {" + tx + "}", [ebitda, ci, cr, tx],
             note="House template arithmetic; 'Other' is not extracted and taken as nil.")
        cfo, capex = k("cfo", p), k("capex", p)
        calc(f"wc_{p}", "Working capital and other (CFO less FFO, plug)", name, val(cfo) - ffo, 0, "USD millions",
             "{" + cfo + "} - {ffo_" + p + "}", [cfo, f"ffo_{p}"],
             note="A plug, not a reported working-capital figure.")
        calc(f"fcf_{p}", "FCF (CFO plus purchase of property and equipment)", name, val(cfo) + val(capex), 0,
             "USD millions", "{" + cfo + "} + {" + capex + "}", [cfo, capex])
        intx = k("interest_expense", p)
        calc(f"interest_cover_{p}", "Interest cover (Adjusted EBITDA / interest expense, net, incl. GLPI and VICI "
             "financing obligations)", name, val(ebitda) / val(intx), 2, "x",
             "{" + ebitda + "} / {" + intx + "}", [ebitda, intx])
        calc(f"cash_interest_cover_{p}", "Cash interest cover, debt only (Adjusted EBITDA / cash interest paid for "
             "debt)", name, val(ebitda) / val(ci), 2, "x", "{" + ebitda + "} / {" + ci + "}", [ebitda, ci])

    # ---- leverage at FY2025 (2025-12-31) and LTM Q2 2026 (2026-06-30)
    for p, bs, ebitda in (("fy2025", "2025_12_31", "adj_ebitda_fy2025"), ("ltm", "2026_06_30", "ltm_adj_ebitda_q2_2026")):
        pl = "FY2025" if p == "fy2025" else "LTM Q2 2026"
        calc(f"total_leverage_{p}", "Total leverage (total debt, face / Adjusted EBITDA)", pl, val(f"total_debt_face_{bs}")
             / val(ebitda), 2, "x", "{total_debt_face_" + bs + "} / {" + ebitda + "}", [f"total_debt_face_{bs}", ebitda])
        calc(f"net_leverage_{p}", "Net leverage (net debt / Adjusted EBITDA)", pl, val(f"net_debt_calc_{bs}") / val(ebitda),
             2, "x", "{net_debt_calc_" + bs + "} / {" + ebitda + "}", [f"net_debt_calc_{bs}", ebitda])

    secured = ["debt_cei_rcf_face_2026_06_30", "debt_cei_tla_face_2026_06_30", "debt_cva_ddtl_face_2026_06_30",
               "debt_cei_tlb_face_2026_06_30", "debt_cei_tlb1_face_2026_06_30", "debt_cei_ssn_2030_face_2026_06_30",
               "debt_cei_ssn_2032_face_2026_06_30"]
    unsecured = ["debt_cei_sn_2029_face_2026_06_30", "debt_cei_sn_2032_face_2026_06_30"]
    other = ["debt_sid_bonds_face_2026_06_30", "debt_lt_notes_other_face_2026_06_30"]
    calc("senior_secured_debt_2026_06_30", "Senior secured debt, face", "as of 2026-06-30",
         sum((val(x) for x in secured), Decimal(0)), 0, "USD millions", " + ".join("{" + x + "}" for x in secured), secured,
         note="CVA Delayed Draw Term Loan classed as secured by this build (model classification).")
    calc("unsecured_debt_2026_06_30", "Senior unsecured notes, face", "as of 2026-06-30",
         sum((val(x) for x in unsecured), Decimal(0)), 0, "USD millions", " + ".join("{" + x + "}" for x in unsecured), unsecured)
    calc("other_debt_2026_06_30", "Other debt (SID bonds, notes and other payables), face", "as of 2026-06-30",
         sum((val(x) for x in other), Decimal(0)), 0, "USD millions", " + ".join("{" + x + "}" for x in other), other)
    calc("total_debt_check_2026_06_30", "Total debt, face, sum of facilities", "as of 2026-06-30",
         val("senior_secured_debt_2026_06_30") + val("unsecured_debt_2026_06_30") + val("other_debt_2026_06_30"), 0,
         "USD millions", "{senior_secured_debt_2026_06_30} + {unsecured_debt_2026_06_30} + {other_debt_2026_06_30}",
         ["senior_secured_debt_2026_06_30", "unsecured_debt_2026_06_30", "other_debt_2026_06_30"],
         note="Equals the 10-Q's total debt, face value (C-ref in the capital structure table).")
    calc("senior_leverage_ltm", "Senior secured leverage (senior secured debt / LTM Adjusted EBITDA)", "LTM Q2 2026",
         val("senior_secured_debt_2026_06_30") / val("ltm_adj_ebitda_q2_2026"), 2, "x",
         "{senior_secured_debt_2026_06_30} / {ltm_adj_ebitda_q2_2026}", ["senior_secured_debt_2026_06_30", "ltm_adj_ebitda_q2_2026"])
    calc("ev_merger_usdm", "Enterprise value at the merger's stated transaction value", "2026-05-28",
         val("merger_transaction_value") * 1000, 0, "USD millions", "{merger_transaction_value} x 1,000",
         ["merger_transaction_value"], note="Approximate in the source ('approximately $17.6 billion').")
    calc("implied_equity_merger_usdm", "Implied equity value (transaction value less assumed debt)", "2026-05-28",
         (val("merger_transaction_value") - val("merger_assumed_debt")) * 1000, 0, "USD millions",
         "({merger_transaction_value} - {merger_assumed_debt}) x 1,000", ["merger_transaction_value", "merger_assumed_debt"])
    calc("ev_multiple_ltm", "EV / LTM Adjusted EBITDA at the merger value", "LTM Q2 2026",
         val("ev_merger_usdm") / val("ltm_adj_ebitda_q2_2026"), 2, "x", "{ev_merger_usdm} / {ltm_adj_ebitda_q2_2026}",
         ["ev_merger_usdm", "ltm_adj_ebitda_q2_2026"])

    # ---- Q2 2026 EBITDA build (Reported -> Structuring -> SSIM)
    rep = ["recon_net_loss_attrib_q2_2026", "recon_nci_q2_2026", "recon_income_taxes_q2_2026",
           "recon_other_income_q2_2026", "recon_interest_expense_q2_2026", "recon_d_and_a_q2_2026"]
    calc("reported_ebitda_q2_2026", "Reported EBITDA (before company add-backs)", "Q2 2026",
         sum((val(x) for x in rep), Decimal(0)), 0, "USD millions", " + ".join("{" + x + "}" for x in rep), rep)
    add = ["recon_transaction_costs_q2_2026", "recon_sbc_q2_2026"]
    calc("structuring_ebitda_q2_2026", "Structuring EBITDA (Reported plus issuer add-backs)", "Q2 2026",
         val("reported_ebitda_q2_2026") + sum((val(x) for x in add), Decimal(0)), 0, "USD millions",
         "{reported_ebitda_q2_2026} + " + " + ".join("{" + x + "}" for x in add), ["reported_ebitda_q2_2026"] + add,
         note="Equals company Adjusted EBITDA for Q2 2026.")

    # ---- capital-structure multiples (cumulative through each facility, on LTM Adjusted EBITDA)
    # ---- cash bridge H1 2026 with an unexplained residual
    calc("cash_bridge_residual_h1_2026", "Unexplained residual: cash bridge H1 2026", "H1 2026",
         val("cash_2026_06_30") - val("cash_2025_12_31") - val("cfo_h1_2026") - val("capex_h1_2026"), 0, "USD millions",
         "{cash_2026_06_30} - {cash_2025_12_31} - {cfo_h1_2026} - {capex_h1_2026}",
         ["cash_2026_06_30", "cash_2025_12_31", "cfo_h1_2026", "capex_h1_2026"],
         note="Financing, other investing and restricted-cash movements were not extracted; the residual names them.")
    # ---- interest outlook (projected)
    calc("cash_interest_fy2026e", "FY2026 interest: H1 2026 paid plus the 10-Q estimate for the remainder of 2026",
         "FY2026E", val("cash_interest_debt_h1_2026") + val("guide_remaining_2026_interest"), 0, "USD millions",
         "{cash_interest_debt_h1_2026} + {guide_remaining_2026_interest}",
         ["cash_interest_debt_h1_2026", "guide_remaining_2026_interest"],
         note="Mixes cash paid with the 10-Q's estimated interest payments; the bases are close but not identical.")
    # ---- peer metrics (Q2 2026)
    calc("mgm_ebitda_margin_q2_2026", "MGM Adjusted EBITDA margin", "Q2 2026",
         val("mgm_adj_ebitda_q2_2026") / val("mgm_revenues_q2_2026") * 100, 1, "%",
         "{mgm_adj_ebitda_q2_2026} / {mgm_revenues_q2_2026} x 100", ["mgm_adj_ebitda_q2_2026", "mgm_revenues_q2_2026"])
    calc("penn_ebitda_margin_q2_2026", "PENN Adjusted EBITDA margin", "Q2 2026",
         val("penn_adj_ebitda_q2_2026") / val("penn_revenues_q2_2026") * 100, 1, "%",
         "{penn_adj_ebitda_q2_2026} / {penn_revenues_q2_2026} x 100", ["penn_adj_ebitda_q2_2026", "penn_revenues_q2_2026"])
    calc("czr_ebitda_margin_q2_2026", "CZR Adjusted EBITDA margin", "Q2 2026",
         val("adj_ebitda_q2_2026") / val("net_revenues_q2_2026") * 100, 1, "%",
         "{adj_ebitda_q2_2026} / {net_revenues_q2_2026} x 100", ["adj_ebitda_q2_2026", "net_revenues_q2_2026"])
    for who, rv in (("mgm", "mgm_revenues"), ("penn", "penn_revenues"), ("czr", "net_revenues")):
        calc(f"{who}_rev_growth_q2_2026", f"{who.upper()} revenue growth, Q2 2026 on Q2 2025", "Q2 2026",
             (val(f"{rv}_q2_2026") / val(f"{rv}_q2_2025") - 1) * 100, 1, "%",
             "({" + rv + "_q2_2026} / {" + rv + "_q2_2025} - 1) x 100", [f"{rv}_q2_2026", f"{rv}_q2_2025"])
    ys = sorted(val(x) for x in ("trace_czr_12769gac4_last_yield", "trace_czr_12769gad2_last_yield",
                                 "trace_mgm_552953ck5_last_yield", "trace_penn_707569av1_last_yield"))
    calc("trace_yield_median", "Median TRACE last yield, four bonds", "2026-10-01", (ys[1] + ys[2]) / 2, 2, "%",
         "median({trace_czr_12769gac4_last_yield}, {trace_czr_12769gad2_last_yield}, {trace_mgm_552953ck5_last_yield}, "
         "{trace_penn_707569av1_last_yield})",
         ["trace_czr_12769gac4_last_yield", "trace_czr_12769gad2_last_yield", "trace_mgm_552953ck5_last_yield",
          "trace_penn_707569av1_last_yield"])
    # the other side of the H1 2026 cash bridge: closing cash built from the extracted lines (the residual is stated minus this)
    calc("cash_bridge_closing_from_lines_h1_2026", "Closing cash built from the extracted lines, H1 2026", "H1 2026",
         val("cash_2025_12_31") + val("cfo_h1_2026") + val("capex_h1_2026"), 0, "USD millions",
         "{cash_2025_12_31} + {cfo_h1_2026} + {capex_h1_2026}", ["cash_2025_12_31", "cfo_h1_2026", "capex_h1_2026"],
         note="Opening cash plus cash from operations less capex; financing and other investing flows were not extracted.")


# ---------------------------------------------------------------- tables and charts
def D(key: str) -> dict:
    return strip(FIG[key])


REV_KEYS = ("net_revenues_fy2023", "net_revenues_fy2024", "net_revenues_fy2025", "ltm_net_revenues_q2_2026")


def rev_extremes() -> tuple[str, str, str, str]:
    """(low, high, low key, high key) over every net-revenue bar the Report draws, so the prose matches the chart."""
    vals = {k: float(FIG[k]["v"].replace(",", "")) for k in REV_KEYS}
    lo, hi = min(vals, key=vals.get), max(vals, key=vals.get)
    return FIG[lo]["v"], FIG[hi]["v"], lo, hi


def rate(text: str) -> str:
    """A yield or coupon for prose: 3 decimals at most, trailing zeros trimmed to two (display only)."""
    out = f"{float(text):.3f}"
    return out[:-1] if out.endswith("0") else out


def G(field: str) -> dict:
    return gap_datum(GAP_BY_KEY[field])


def tables() -> dict:
    cols = ["FY2023", "FY2024", "FY2025", "H1 2025", "H1 2026", "LTM Q2 2026"]
    ps = ["fy2023", "fy2024", "fy2025", "h1_2025", "h1_2026", "ltm"]

    def k(base: str, p: str) -> str:
        return f"ltm_{base}_q2_2026" if p == "ltm" else f"{base}_{p}"

    def row(label: str, fn, kind: str | None = None) -> dict:
        return {"label": label, "kind": kind, "cells": [fn(p) for p in ps]}

    def maybe(key: str) -> dict:
        return D(key) if key in FIG else {"v": None, "prov": "gap", "reason": "not applicable for this period (n.a.)"}

    def interest(p):  # noqa: ANN001
        return D(k("cash_interest_debt", p))

    def taxes(p):  # noqa: ANN001
        return D("ltm_income_taxes_paid_q2_2026" if p == "ltm" else f"income_taxes_paid_{p}")

    financials = {
        "title": "Financials", "unit": "US$ m", "columns": cols,
        "rows": [
            row("Revenue", lambda p: D(k("net_revenues", p)), "head"),
            row("% Δ", lambda p: maybe(f"net_revenues_growth_{p}"), "sub"),
            row("Gross Profit", lambda p: G("gross_profit"), "head"),
            row("EBITDA (Adjusted, company-defined)", lambda p: D(k("adj_ebitda", p)), "head"),
            row("% Δ", lambda p: maybe(f"adj_ebitda_growth_{p}"), "sub"),
            row("% margin", lambda p: D(f"ebitda_margin_{p}"), "sub"),
            row("Cash Interest (debt)", interest),
            row("Leases (cash interest for GLPI and VICI rent)", lambda p: D(k("cash_interest_rent", p))),
            row("Cash tax", taxes),
            row("FFO", lambda p: D(f"ffo_{p}"), "total"),
            row("WC and other (plug)", lambda p: D(f"wc_{p}")),
            row("CFO", lambda p: D(k("cfo", p)), "total"),
            row("Capex", lambda p: D(k("capex", p))),
            row("FCF", lambda p: D(f"fcf_{p}"), "total"),
        ],
        "note": "Columns follow the house template (FY-2, FY-1, FY, PYTD, YTD, LTM). Negatives in parentheses.",
    }
    bs_cols = ["FY2023", "FY2024", "FY2025", "Q2 2026"]
    nf = G("total_debt_cash_fy2023_fy2024")
    balance = {
        "title": "Balance sheet", "unit": "US$ m", "columns": bs_cols,
        "rows": [
            {"label": "Cash", "cells": [nf, nf, D("cash_2025_12_31"), D("cash_2026_06_30")]},
            {"label": "Senior debt (secured)", "cells": [nf, nf, {"v": None, "prov": "gap", "ref": GAP_BY_KEY["total_debt_cash_fy2023_fy2024"],
                                                         "reason": "facility split at 2025-12-31 not extracted"}, D("senior_secured_debt_2026_06_30")]},
            {"label": "Total debt (face)", "cells": [nf, nf, D("total_debt_face_2025_12_31"), D("total_debt_face_2026_06_30")], "kind": "total"},
            {"label": "Net debt", "cells": [nf, nf, D("net_debt_calc_2025_12_31"), D("net_debt_calc_2026_06_30")]},
            {"label": "Financing obligations (GLPI and VICI leases)", "cells": [nf, nf, D("lt_financing_obligations_2025_12_31"),
                                                                              D("lt_financing_obligations_2026_06_30")]},
        ],
    }
    lev_cols = ["FY2023", "FY2024", "FY2025", "LTM Q2 2026"]
    metrics = {
        "title": "Credit metrics", "unit": "x", "columns": lev_cols,
        "rows": [
            {"label": "Senior Leverage", "cells": [nf, nf, {"v": None, "prov": "gap", "ref": GAP_BY_KEY["total_debt_cash_fy2023_fy2024"],
                                                       "reason": "facility split at 2025-12-31 not extracted"}, D("senior_leverage_ltm")]},
            {"label": "Total Leverage", "cells": [nf, nf, D("total_leverage_fy2025"), D("total_leverage_ltm")]},
            {"label": "Net Leverage", "cells": [nf, nf, D("net_leverage_fy2025"), D("net_leverage_ltm")], "kind": "total"},
            {"label": "Interest Cover", "cells": [D("interest_cover_fy2023"), D("interest_cover_fy2024"), D("interest_cover_fy2025"),
                                                  D("interest_cover_ltm")]},
            {"label": "Cash interest cover, debt only", "cells": [D("cash_interest_cover_fy2023"), D("cash_interest_cover_fy2024"),
                                                                  D("cash_interest_cover_fy2025"), D("cash_interest_cover_ltm")]},
        ],
        "note": "Leverage on company Adjusted EBITDA; GLPI and VICI financing obligations are not in debt.",
    }

    # capital structure, per facility, cumulative multiples on LTM Adjusted EBITDA, % of EV at the merger value
    fac = [
        ("CEI Revolving Credit Facility", "RCF", "debt_cei_rcf_face_2026_06_30", "variable", "Jan 31, 2028", "cei_rcf_maturity", "secured"),
        ("CEI Term Loan A", "1L Term Loan", "debt_cei_tla_face_2026_06_30", "variable", "2028", None, "secured"),
        ("CVA Delayed Draw Term Loan", "1L Term Loan", "debt_cva_ddtl_face_2026_06_30", "variable", "Apr 26, 2029", "cva_facilities_maturity", "secured"),
        ("CEI Term Loan B", "1L Term Loan", "debt_cei_tlb_face_2026_06_30", "variable", "2030", None, "secured"),
        ("CEI Term Loan B-1", "1L Term Loan", "debt_cei_tlb1_face_2026_06_30", "variable", "2031", None, "secured"),
        ("CEI 7.00% Senior Secured Notes 2030", "SS Notes", "debt_cei_ssn_2030_face_2026_06_30", "debt_cei_ssn_2030_coupon", "2030", None, "secured"),
        ("CEI 6.50% Senior Secured Notes 2032", "SS Notes", "debt_cei_ssn_2032_face_2026_06_30", "debt_cei_ssn_2032_coupon", "Feb 15, 2032", "trace_czr_12769gac4_maturity", "secured"),
        ("CEI 4.625% Senior Notes 2029", "SU Notes", "debt_cei_sn_2029_face_2026_06_30", "debt_cei_sn_2029_coupon", "2029", None, "unsecured"),
        ("CEI 6.00% Senior Notes 2032", "SU Notes", "debt_cei_sn_2032_face_2026_06_30", "debt_cei_sn_2032_coupon", "Oct 15, 2032", "trace_czr_12769gad2_maturity", "unsecured"),
        ("Special Improvement District Bonds 4.30%", "Other", "debt_sid_bonds_face_2026_06_30", "debt_sid_bonds_coupon", "2037", None, "other"),
        ("Long-term notes and other payables", "Other", "debt_lt_notes_other_face_2026_06_30", None, "not stated", None, "other"),
    ]
    prices = {"debt_cei_ssn_2032_face_2026_06_30": ("trace_czr_12769gac4_last_price", "trace_czr_12769gac4_last_yield",
                                                    "trace_czr_12769gac4_moodys", "trace_czr_12769gac4_sp"),
              "debt_cei_sn_2032_face_2026_06_30": ("trace_czr_12769gad2_last_price", "trace_czr_12769gad2_last_yield",
                                                   "trace_czr_12769gad2_moodys", "trace_czr_12769gad2_sp")}
    ltm = val("ltm_adj_ebitda_q2_2026")
    ev = val("ev_merger_usdm")
    cum = Decimal(0)
    cum_keys: list[str] = []
    rows = []
    for i, (name, dtype, key, cpn, mat, matkey, rank) in enumerate(fac):
        cum += val(key)
        cum_keys.append(key)
        mult = calc(f"cum_multiple_{i}", f"Cumulative multiple through {name}", "LTM Q2 2026", cum / ltm, 2, "x",
                    "(" + " + ".join("{" + x + "}" for x in cum_keys) + ") / {ltm_adj_ebitda_q2_2026}",
                    cum_keys + ["ltm_adj_ebitda_q2_2026"])
        pev = calc(f"pct_ev_{i}", f"Cumulative debt through {name} as % of EV", "2026-06-30", cum / ev * 100, 1, "%",
                   "(" + " + ".join("{" + x + "}" for x in cum_keys) + ") / {ev_merger_usdm} x 100",
                   cum_keys + ["ev_merger_usdm"])
        px = prices.get(key)
        coupon = D(cpn) if cpn and cpn in FIG else (G("loan_margins_prices") if cpn == "variable" else
                                                    {"v": None, "prov": "gap", "reason": "rate not stated"})
        rows.append({
            "facility": name, "debtType": dtype, "rank": rank,
            "figi": G("figi"),
            "ratings": ({"v": FIG[px[2]]["v"] + " / " + FIG[px[3]]["v"], "prov": "cited", "ref": KEY_REF[px[2]],
                         "refs": [KEY_REF[px[2]], KEY_REF[px[3]]]} if px else G("issuer_ratings")),
            "coupon": coupon, "coupon_kind": "variable (margin not in sources)" if cpn == "variable" else "fixed",
            "ccy": "USD",
            "maturity": D(matkey) if matkey else {"v": mat, "prov": "cited", "ref": KEY_REF[key]},
            "bid": D(px[0]) if px else G("loan_margins_prices"),
            "ask": D(px[0]) if px else G("loan_margins_prices"),
            "price_note": "TRACE last trade price (no bid/ask in sources)" if px else None,
            "yield": D(px[1]) if px else G("loan_margins_prices"),
            "outstanding": D(key), "book": D(key.replace("_face_", "_book_")),
            "structuring_multiple": strip(mult), "ssim_multiple": strip(mult), "pct_ev": strip(pev),
        })
    cap = {
        "title": "Capital structure", "unit": "US$ m", "asOf": "2026-06-30",
        "ebitda_basis": "LTM Q2 2026 Adjusted EBITDA " + FIG["ltm_adj_ebitda_q2_2026"]["v"] + " [" + KEY_REF["ltm_adj_ebitda_q2_2026"] + "]; "
                        "SSIM multiple equals Structuring multiple because no unrealized add-backs are marketed (see "
                        + GAP_BY_KEY["unrealized_addbacks"] + ")",
        "rows": rows,
        "subtotals": {
            "senior_secured": D("senior_secured_debt_2026_06_30"),
            "unsecured": D("unsecured_debt_2026_06_30"),
            "other": D("other_debt_2026_06_30"),
            "total_debt": D("total_debt_face_2026_06_30"),
            "total_debt_check": D("total_debt_check_2026_06_30"),
            "cash": D("cash_2026_06_30"),
            "net_debt": D("net_debt_calc_2026_06_30"),
            "implied_equity": D("implied_equity_merger_usdm"),
            "ev": D("ev_merger_usdm"),
            "ev_multiple": D("ev_multiple_ltm"),
            "pf_interest": G("pf_ltm"),
            "equity_market_value": G("equity_market_value"),
        },
    }
    ebitda_adj = {
        "title": "EBITDA adjustments", "unit": "US$ m", "columns": ["Q2 2026", "LTM Q2 2026", "PF-LTM"],
        "rows": [
            {"label": "Reported EBITDA", "kind": "total", "cells": [D("reported_ebitda_q2_2026"), G("reported_ebitda_ltm"), G("pf_ltm")]},
            {"label": "Transaction costs and other, net", "kind": "indent", "cells": [D("recon_transaction_costs_q2_2026"), G("reported_ebitda_ltm"), G("pf_ltm")]},
            {"label": "Stock-based compensation", "kind": "indent", "cells": [D("recon_sbc_q2_2026"), G("reported_ebitda_ltm"), G("pf_ltm")]},
            {"label": "Structuring EBITDA", "kind": "total", "cells": [D("structuring_ebitda_q2_2026"), D("ltm_adj_ebitda_q2_2026"), G("pf_ltm")]},
            {"label": "unrealized add-backs", "kind": "sub", "cells": [G("unrealized_addbacks"), G("unrealized_addbacks"), G("pf_ltm")]},
            {"label": "SSIM EBITDA", "kind": "total", "cells": [D("structuring_ebitda_q2_2026"), D("ltm_adj_ebitda_q2_2026"), G("pf_ltm")]},
        ],
        "note": "Owner's definitions: Reported = before any adjustments; Structuring = Reported + every issuer add-back; "
                "SSIM = Structuring - unrealized add-backs. With none marketed, SSIM equals Structuring.",
    }
    liquidity = {
        "title": "Liquidity at 2026-06-30", "unit": "US$ m",
        "rows": [{"label": FIG[x]["label"].replace("Liquidity table: ", ""), "cell": D(x)} for x in
                 ("liq_cash", "liq_cei_rcf_net", "liq_cva_rcf", "liq_lcs", "liq_reserves", "liq_regulatory", "liq_total")],
    }
    maturities = {
        "title": "Annual maturities of long-term debt (10-Q)", "unit": "US$ m",
        "rows": [{"label": lab, "cell": D(x)} for lab, x in (("Remaining 2026", "debt_maturity_remaining_2026"), ("2027", "debt_maturity_2027"),
                                                             ("2028", "debt_maturity_2028"), ("2029", "debt_maturity_2029"),
                                                             ("2030", "debt_maturity_2030"), ("Thereafter", "debt_maturity_thereafter"))],
    }
    segs = [("Las Vegas", "las_vegas"), ("Regional", "regional"), ("Caesars Digital", "caesars_digital"),
            ("Managed and Branded", "managed_branded"), ("Corporate and Other", "corporate_other")]
    segments = {
        "title": "Segments, Q2 2026 against Q2 2025", "unit": "US$ m",
        "columns": ["Net revenues Q2 2025", "Net revenues Q2 2026", "Adj. EBITDA Q2 2025", "Adj. EBITDA Q2 2026"],
        "rows": [{"label": lab, "cells": [D(f"seg_rev_{s}_q2_2025"), D(f"seg_rev_{s}_q2_2026"),
                                          D(f"seg_adj_ebitda_{s}_q2_2025"), D(f"seg_adj_ebitda_{s}_q2_2026")]} for lab, s in segs],
    }
    trace = {
        "title": "TRACE observations, 2026-10-02", "unit": "%",
        "rows": [{"issuer": who, "cusip": cus.upper(), "coupon": D(f"trace_{t}_coupon"), "maturity": D(f"trace_{t}_maturity"),
                  "next_call": D(f"trace_{t}_next_call"), "price": D(f"trace_{t}_last_price"), "yield": D(f"trace_{t}_last_yield"),
                  "trade_date": D(f"trace_{t}_last_date"), "moodys": D(f"trace_{t}_moodys"), "sp": D(f"trace_{t}_sp"),
                  "seniority": sen}
                 for who, cus, t, sen in (("CZR", "12769gac4", "czr_12769gac4", "Senior secured"),
                                          ("CZR", "12769gad2", "czr_12769gad2", "Senior unsecured"),
                                          ("MGM", "552953ck5", "mgm_552953ck5", "Senior unsecured"),
                                          ("PENN", "707569av1", "penn_707569av1", "Senior unsecured"))],
        "note": "Coupons print as TRACE serves them (to 19 decimal places). Seniority of the MGM and PENN notes is not in "
                "the sources (model classification).",
    }
    return {"financials": financials, "balanceSheet": balance, "creditMetrics": metrics, "capitalStructure": cap,
            "ebitdaAdjustments": ebitda_adj, "liquidity": liquidity, "maturities": maturities, "segments": segments,
            "trace": trace}


def charts(portfolio: dict) -> dict:
    nf = G("total_debt_cash_fy2023_fy2024")
    lq = G("liquidity_fy2023_fy2025")
    cats = ["FY2023", "FY2024", "FY2025", "LTM Q2 2026"]
    src_fin = "Caesars FY2025 10-K, Q2 2026 10-Q and earnings release; calculations from the cited figures"
    leverage = {
        "id": "fig-leverage", "title": "Leverage", "unit": "x", "categories": cats, "categoryLabel": "Period",
        "summary": "Total leverage " + FIG["total_leverage_ltm"]["v"] + "x at LTM Q2 2026 against "
                   + FIG["total_leverage_fy2025"]["v"] + "x at FY2025; FY2023 and FY2024 not extracted.",
        "series": [
            {"key": "total", "label": "Total leverage", "values": [nf, nf, D("total_leverage_fy2025"), D("total_leverage_ltm")]},
            {"key": "net", "label": "Net leverage", "values": [nf, nf, D("net_leverage_fy2025"), D("net_leverage_ltm")]},
        ], "source": src_fin,
    }
    coverage = {
        "id": "fig-coverage", "title": "Interest cover", "unit": "x", "categories": cats, "categoryLabel": "Period",
        "summary": "Adjusted EBITDA covers interest expense, including the GLPI and VICI financing obligations, "
                   + FIG["interest_cover_ltm"]["v"] + "x at LTM; debt-only cash interest " + FIG["cash_interest_cover_ltm"]["v"] + "x.",
        "series": [
            {"key": "all", "label": "EBITDA / interest expense, net", "values": [D(f"interest_cover_{p}") for p in ("fy2023", "fy2024", "fy2025", "ltm")]},
            {"key": "cash", "label": "EBITDA / cash interest, debt only", "values": [D(f"cash_interest_cover_{p}") for p in ("fy2023", "fy2024", "fy2025", "ltm")]},
        ], "source": src_fin,
    }
    liquidity = {
        "id": "fig-liquidity", "title": "Liquidity", "unit": "US$ m", "categories": cats, "categoryLabel": "Period end",
        "summary": "Cash and revolver capacity of " + FIG["liq_total"]["v"] + " at 30 June 2026; total liquidity is stated for that date only.",
        "series": [
            {"key": "total", "label": "Total liquidity", "values": [lq, lq, lq, D("liq_total")]},
            {"key": "cash", "label": "Cash and equivalents", "values": [nf, nf, D("cash_2025_12_31"), D("cash_2026_06_30")]},
        ], "source": "Caesars Q2 2026 earnings release liquidity table; Q2 2026 10-Q balance sheet",
    }
    interest_path = {
        "id": "fig-interest-path", "title": "Cash interest on debt, paid and estimated", "unit": "US$ m",
        "categories": ["FY2023", "FY2024", "FY2025", "FY2026E", "FY2027E"], "categoryLabel": "Year",
        "summary": "Cash interest on debt fell to " + FIG["cash_interest_debt_fy2025"]["v"] + " in FY2025; the 10-Q estimates "
                   + FIG["guide_2027_interest"]["v"] + " of interest payments for 2027 (projected, dashed).",
        "series": [{"key": "int", "label": "Cash interest, debt", "values": [
            D("cash_interest_debt_fy2023"), D("cash_interest_debt_fy2024"), D("cash_interest_debt_fy2025"),
            {**D("cash_interest_fy2026e"), "projected": True}, {**D("guide_2027_interest"), "projected": True}]}],
        "source": "Caesars FY2025 10-K; Q2 2026 10-Q contractual obligations (estimated interest payments)",
    }
    rev_ebitda = {
        "id": "fig-rev-ebitda", "title": "Net revenues and Adjusted EBITDA", "unit": "US$ m", "categories": cats,
        "categoryLabel": "Period",
        "summary": "Net revenues ranged from " + rev_extremes()[0] + " to " + rev_extremes()[1] + " across the four periods; Adjusted EBITDA eased from " + FIG["adj_ebitda_fy2023"]["v"] + " in FY2023 to "
                   + FIG["ltm_adj_ebitda_q2_2026"]["v"] + " at LTM Q2 2026.",
        "series": [
            {"key": "rev", "label": "Net revenues", "values": [D("net_revenues_fy2023"), D("net_revenues_fy2024"), D("net_revenues_fy2025"), D("ltm_net_revenues_q2_2026")]},
            {"key": "ebitda", "label": "Adjusted EBITDA", "values": [D("adj_ebitda_fy2023"), D("adj_ebitda_fy2024"), D("adj_ebitda_fy2025"), D("ltm_adj_ebitda_q2_2026")]},
        ], "source": src_fin,
    }
    segs = [("Las Vegas", "las_vegas"), ("Regional", "regional"), ("Caesars Digital", "caesars_digital"),
            ("Managed and Branded", "managed_branded"), ("Corporate and Other", "corporate_other")]
    seg_db = {
        "id": "fig-segments", "title": "Segment Adjusted EBITDA, Q2 2025 to Q2 2026", "unit": "US$ m",
        "fromLabel": "Q2 2025", "toLabel": "Q2 2026", "categoryLabel": "Segment",
        "summary": "Las Vegas fell from " + FIG["seg_adj_ebitda_las_vegas_q2_2025"]["v"] + " to " + FIG["seg_adj_ebitda_las_vegas_q2_2026"]["v"]
                   + " while Regional rose from " + FIG["seg_adj_ebitda_regional_q2_2025"]["v"] + " to " + FIG["seg_adj_ebitda_regional_q2_2026"]["v"] + ".",
        "rows": [{"key": s, "label": lab, "from": D(f"seg_adj_ebitda_{s}_q2_2025"), "to": D(f"seg_adj_ebitda_{s}_q2_2026")} for lab, s in segs],
        "source": "Caesars Q2 2026 earnings release, segment table",
    }
    # maturity wall: face value by final maturity year and instrument type
    wall = [("2028", {"RCF": "debt_cei_rcf_face_2026_06_30", "Term loans": "debt_cei_tla_face_2026_06_30"}),
            ("2029", {"Term loans": "debt_cva_ddtl_face_2026_06_30", "Senior unsecured notes": "debt_cei_sn_2029_face_2026_06_30"}),
            ("2030", {"Term loans": "debt_cei_tlb_face_2026_06_30", "Senior secured notes": "debt_cei_ssn_2030_face_2026_06_30"}),
            ("2031", {"Term loans": "debt_cei_tlb1_face_2026_06_30"}),
            ("2032", {"Senior secured notes": "debt_cei_ssn_2032_face_2026_06_30", "Senior unsecured notes": "debt_cei_sn_2032_face_2026_06_30"}),
            ("2037", {"Other": "debt_sid_bonds_face_2026_06_30"})]
    series = ["RCF", "Term loans", "Senior secured notes", "Senior unsecured notes", "Other"]
    colours = {"RCF": 4, "Term loans": 1, "Senior secured notes": 3, "Senior unsecured notes": 2, "Other": "neutral"}
    mwall = {
        "id": "fig-maturity-wall", "title": "Debt maturity wall at 30 June 2026", "unit": "US$ m", "categoryLabel": "Final maturity",
        "categories": [y for y, _ in wall],
        "summary": "2030 is the heaviest year (Term Loan B and the 7.00% secured notes); nothing matures before the RCF in January 2028.",
        "series": [{"key": s, "label": s, "color": colours[s], "values": [D(m[s]) if s in m else None for _, m in wall]} for s in series],
        "note": "Face value at final maturity, by instrument; amortisation sits in the 10-Q's annual maturities table. "
                "Long-term notes and other payables (" + FIG["debt_lt_notes_other_face_2026_06_30"]["v"] + ") carry no stated maturity.",
        "source": "Caesars Q2 2026 10-Q debt table",
    }
    bridge_keys = [("Net loss attributable to Caesars", "Net loss", "recon_net_loss_attrib_q2_2026"),
                   ("Net income attributable to noncontrolling interests", "NCI", "recon_nci_q2_2026"),
                   ("(Benefit) provision for income taxes", "Taxes", "recon_income_taxes_q2_2026"),
                   ("Other income", "Other income", "recon_other_income_q2_2026"),
                   ("Interest expense, net", "Interest", "recon_interest_expense_q2_2026"),
                   ("Depreciation and amortization", "D&A", "recon_d_and_a_q2_2026"),
                   ("Transaction costs and other, net", "Transaction costs", "recon_transaction_costs_q2_2026"),
                   ("Stock-based compensation expense", "SBC", "recon_sbc_q2_2026")]
    ebitda_bridge = {
        "id": "fig-ebitda-bridge", "title": "From net loss to Adjusted EBITDA, Q2 2026", "unit": "US$ m", "categoryLabel": "Step",
        "summary": "A net loss of " + FIG["recon_net_loss_attrib_q2_2026"]["v"] + " becomes Adjusted EBITDA of " + FIG["recon_adj_ebitda_q2_2026"]["v"]
                   + " once interest and D&A are added back; the bridge reconciles.",
        "steps": [{"label": lab, "short": sh, "kind": "total" if i == 0 else "delta", "d": D(k)} for i, (lab, sh, k) in enumerate(bridge_keys)]
                 + [{"label": "Adjusted EBITDA", "short": "Adj. EBITDA", "kind": "total", "d": D("recon_adj_ebitda_q2_2026")}],
        "source": "Caesars Q2 2026 earnings release, Adjusted EBITDA reconciliation",
    }
    cash_bridge = {
        "id": "fig-cash-bridge", "title": "Cash bridge, H1 2026", "unit": "US$ m", "categoryLabel": "Step",
        "summary": "Cash rose from " + FIG["cash_2025_12_31"]["v"] + " to " + FIG["cash_2026_06_30"]["v"] + "; "
                   + FIG["cash_bridge_residual_h1_2026"]["v"] + " is unexplained by the extracted lines (financing and other investing).",
        "steps": [{"label": "Cash, 31 Dec 2025", "kind": "total", "d": D("cash_2025_12_31")},
                  {"label": "Cash from operations", "kind": "delta", "d": D("cfo_h1_2026")},
                  {"label": "Purchase of property and equipment", "kind": "delta", "d": D("capex_h1_2026")},
                  {"label": "Financing and other", "kind": "residual", "d": D("cash_bridge_residual_h1_2026")},
                  {"label": "Cash, 30 Jun 2026", "kind": "total", "d": D("cash_2026_06_30")}],
        "source": "Caesars Q2 2026 10-Q cash flow statement and balance sheet; residual calculated from the cited lines",
    }
    pts = []
    for lab, short, t, grp in (("CZR 6.50% senior secured 2032", "CZR 6.50% SS 2032", "czr_12769gac4", "CZR"),
                               ("CZR 6.00% senior notes 2032", "CZR 6.00% SU 2032", "czr_12769gad2", "CZR"),
                               ("MGM 6.125% notes 2029", "MGM 6.125% 2029", "mgm_552953ck5", "MGM"),
                               ("PENN 4.125% notes 2029", "PENN 4.125% 2029", "penn_707569av1", "PENN")):
        m, dd, yy = FIG[f"trace_{t}_maturity"]["v"].split("/")
        pts.append({"key": t, "label": lab, "short": short, "group": grp, "x": f"{yy}-{int(m):02d}-{int(dd):02d}",
                    "y": D(f"trace_{t}_last_yield")})
    scatter = {
        "id": "fig-yield-curve", "title": "Yield against maturity, CZR and peers", "unit": "%", "yLabel": "Last trade yield",
        "xLabel": "Maturity", "groupLabel": "Issuer", "asOf": "2026-10-02",
        "summary": "CZR's unsecured 2032s yield " + rate(FIG["trace_czr_12769gad2_last_yield"]["v"]) + "%, above its secured 2032s at "
                   + rate(FIG["trace_czr_12769gac4_last_yield"]["v"]) + "%; the MGM and PENN 2029s yield " + rate(FIG["trace_mgm_552953ck5_last_yield"]["v"]) + "% and " + rate(FIG["trace_penn_707569av1_last_yield"]["v"]) + "%.",
        "points": pts, "groupColors": {"CZR": 1, "MGM": 2, "PENN": 4},
        "curve": {"group": None, "label": "Fitted curve, all four bonds (calculated; positions only)", "prov": "calculated"},
        "gap": G("spread_to_treasury"),
        "source": "FINRA TRACE pages observed 2026-10-02 (last trades 2026-10-01)",
    }
    rng = {
        "id": "fig-peer-range", "title": "CZR against MGM and PENN, Q2 2026", "unit": "%", "markerLabel": "CZR",
        "categoryLabel": "Metric",
        "summary": "CZR's Adjusted EBITDA margin of " + FIG["czr_ebitda_margin_q2_2026"]["v"] + "% is the highest of the three; its "
                   "unsecured notes yield the most.",
        "rows": [
            {"key": "margin", "label": "Adjusted EBITDA margin", "min": D("mgm_ebitda_margin_q2_2026"),
             "median": D("penn_ebitda_margin_q2_2026"), "max": D("czr_ebitda_margin_q2_2026"), "marker": D("czr_ebitda_margin_q2_2026")},
            {"key": "growth", "label": "Revenue growth on Q2 2025", "min": D("mgm_rev_growth_q2_2026"),
             "median": D("czr_rev_growth_q2_2026"), "max": D("penn_rev_growth_q2_2026"), "marker": D("czr_rev_growth_q2_2026")},
            {"key": "yield", "label": "TRACE last yield, four bonds", "min": D("trace_penn_707569av1_last_yield"),
             "median": D("trace_yield_median"), "max": D("trace_czr_12769gad2_last_yield"), "marker": D("trace_czr_12769gac4_last_yield"),
             "sub": "marker: CZR secured 2032"},
        ],
        "note": "Three issuers: no quartiles are drawn. Adjusted EBITDA is company-defined and not adjusted for comparability.",
        "source": "CZR, MGM and PENN Q2 2026 earnings releases; FINRA TRACE",
    }
    covenant = {
        "id": "fig-covenant", "title": "Covenant headroom", "unit": "x", "categoryLabel": "Test",
        "summary": "No covenant level is cited in the sources, so headroom is not drawn.",
        "rows": [{"key": "lev", "label": "Maximum net leverage (CEI credit agreement)", "direction": "max",
                  "threshold": G("covenant_levels"), "current": D("net_leverage_ltm"), "headroom": G("covenant_levels")}],
        "source": "Caesars Q2 2026 10-Q; credit agreement not extracted",
    }
    risk = {
        "id": "fig-risk", "title": "Probability and impact", "summary": "Two events sit in the high zone: merger financing and the Las Vegas trend. Illustrative: no RBOT run exists.",
        "events": [
            {"key": "R1", "label": "Merger debt", "description": "New committed debt for the Fertitta merger has no stated amount; leverage after closing is unknown.",
             "probability": "High", "impact": "High", "classification": "High", "prov": "illustrative", "ref": GAP_BY_KEY["merger_committed_debt_financing_amount"]},
            {"key": "R2", "label": "Las Vegas trend", "description": "Las Vegas Adjusted EBITDA fell year on year in Q2 2026.",
             "probability": "Medium", "impact": "High", "classification": "High", "prov": "illustrative", "ref": KEY_REF["seg_adj_ebitda_las_vegas_q2_2026"]},
            {"key": "R3", "label": "Lease burden", "description": "GLPI and VICI financing obligations sit outside debt but absorb cash as rent.",
             "probability": "Low", "impact": "High", "classification": "Medium", "prov": "illustrative", "ref": KEY_REF["lt_financing_obligations_2026_06_30"]},
            {"key": "R4", "label": "Digital margin", "description": "Caesars Digital Adjusted EBITDA fell year on year in Q2 2026.",
             "probability": "Medium", "impact": "Low", "classification": "Low", "prov": "illustrative", "ref": KEY_REF["seg_adj_ebitda_caesars_digital_q2_2026"]},
            {"key": "R5", "label": "RCF maturity", "description": "The CEI revolver matures on January 31, 2028, two months after the merger's latest End Date of November 27, 2027.",
             "probability": "Low", "impact": "Medium", "classification": "Low", "prov": "illustrative", "ref": KEY_REF["cei_rcf_maturity"]},
        ],
        "source": "Illustrative event register; descriptions cite the figures they rest on",
    }
    # synthetic: Test CLO I constraint bullets and sector range
    c = {r["id"]: r for r in portfolio["constraints"]}

    def pc(cid: str, field: str) -> dict:
        r = c[cid]
        return {"v": r[field].replace("%", "").replace("≤", "").replace("≥", "").replace("NAV", "").strip(),
                "prov": "synthetic", "ref": r["ref"]}

    clo_bullet = {
        "id": "fig-clo-limits", "title": "Test CLO I limits nearest their thresholds", "unit": "% NAV", "categoryLabel": "Constraint",
        "summary": "Single-name (C-01) and CCC bucket (C-04) sit within 0.14% of their ceilings; synthetic portfolio.",
        "rows": [
            {"key": "C-01", "label": "C-01 Single issuer", "direction": "max", "threshold": pc("C-01", "limit"), "current": pc("C-01", "current"), "headroom": pc("C-01", "headroom")},
            {"key": "C-04", "label": "C-04 CCC bucket", "direction": "max", "threshold": pc("C-04", "limit"), "current": pc("C-04", "current"), "headroom": pc("C-04", "headroom")},
            {"key": "C-05", "label": "C-05 Unrated", "direction": "max", "threshold": pc("C-05", "limit"), "current": pc("C-05", "current"), "headroom": pc("C-05", "headroom")},
            {"key": "C-06", "label": "C-06 Largest sector", "direction": "max", "threshold": pc("C-06", "limit"), "current": pc("C-06", "current"), "headroom": pc("C-06", "headroom")},
        ],
        "source": "Test CLO I constraints compliance monitor, 29 May 2026 (synthetic)",
    }
    sw = portfolio["sectors"]
    vals = sorted(Decimal(s["pct"].rstrip("%")) for s in sw)

    def quart(p: Decimal) -> Decimal:  # inclusive linear interpolation, exact in Decimal
        pos = (len(vals) - 1) * p
        lo = int(pos)
        frac = pos - lo
        return vals[lo] + (vals[min(lo + 1, len(vals) - 1)] - vals[lo]) * frac

    leis = next(s for s in sw if s["sector"] == "Leisure Facilities & Services")
    sect_ref = portfolio["sources"]["sectors"]
    qn = {"v": None}
    for name, p in (("q1", Decimal("0.25")), ("median", Decimal("0.5")), ("q3", Decimal("0.75"))):
        kid = f"K{len(CALCS) + 1}"
        CALCS[kid] = {"id": kid, "key": f"clo_sector_{name}", "label": f"Test CLO I top-20 sector weight, {name}",
                      "period": "29-May-2026", "value": fmt(quart(p), 2), "unit": "% NAV",
                      "formula": f"{name} of the 20 sector weights in the exposure report section C (inclusive linear interpolation)",
                      "formula_keys": "", "inputs": [sect_ref], "note": "Synthetic portfolio data.", "synthetic": True}
        qn[name] = {"v": fmt(quart(p), 2), "prov": "calculated", "ref": kid}
    sector_range = {
        "id": "fig-clo-sectors", "title": "Test CLO I sector weights, top 20", "unit": "% NAV", "markerLabel": "Leisure Facilities",
        "categoryLabel": "Distribution",
        "summary": "Leisure Facilities & Services, the sector a Caesars loan would join, holds " + leis["pct"] + " of NAV, above the median sector; synthetic portfolio.",
        "rows": [{"key": "sectors", "label": "Sector weight", "sub": "20 sectors",
                  "min": {"v": vals[0].to_eng_string(), "prov": "synthetic", "ref": sect_ref},
                  "q1": qn["q1"], "median": qn["median"], "q3": qn["q3"],
                  "max": {"v": vals[-1].to_eng_string(), "prov": "synthetic", "ref": sect_ref},
                  "marker": {"v": leis["pct"].rstrip("%"), "prov": "synthetic", "ref": sect_ref}}],
        "source": "Test CLO I exposure report, 29 May 2026, section C (synthetic)",
    }
    return {"leverage": leverage, "coverage": coverage, "liquidity": liquidity, "interestPath": interest_path,
            "revenueEbitda": rev_ebitda, "segments": seg_db, "maturityWall": mwall, "ebitdaBridge": ebitda_bridge,
            "cashBridge": cash_bridge, "yieldCurve": scatter, "peerRange": rng, "covenant": covenant, "risk": risk,
            "cloLimits": clo_bullet, "cloSectors": sector_range}


# ---------------------------------------------------------------- synthetic portfolio (Test CLO I)
PII_FIELDS = {"Checked By", "Portfolio Manager(s)"}


def load_portfolio(folder: Path) -> dict:
    sources: dict[str, dict] = {}

    def src(file: str, line: int, excerpt: str, label: str) -> str:
        sid = f"S{len(sources) + 1}"
        sources[sid] = {"id": sid, "file": file, "line": line, "locator": f"line {line}", "excerpt": excerpt,
                        "label": label, "synthetic": True}
        return sid

    mon = "CP-6A_-_Portfolio_Constraints_Compliance_Monitor_-_Test_CLO_I_Ltd.csv"
    constraints = []
    with open(folder / mon, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        for i, r in enumerate(rd, start=2):
            excerpt = ", ".join(f"{k}: {v}" for k, v in r.items() if k not in PII_FIELDS)
            constraints.append({"id": r["ID"], "category": r["Constraint Category"], "parameter": r["Parameter"],
                                "limit": r["Limit"], "breachType": r["Breach Type"], "sourceDocument": r["Source Document"],
                                "current": r["Current Value"], "headroom": r["Headroom"], "status": r["Status"],
                                "lastChecked": r["Last Checked"],
                                "ref": src(mon, i, excerpt, f"{r['ID']} {r['Parameter']}")})
    exp = "CP-6A___Exposure_Report__Test_CLO_I_Ltd__29-May-2026_.csv"
    summary, sectors, section = {}, [], ""
    with open(folder / exp, newline="", encoding="utf-8-sig") as fh:
        lines = list(csv.reader(fh))
    sec_line = 0
    for i, row in enumerate(lines, start=1):
        cells = [c for c in row if c != ""]
        if not cells:
            continue
        if cells[0].startswith("SECTION"):
            section = cells[0]
            sec_line = i
            continue
        if section.startswith("SECTION A") and len(cells) == 2 and cells[0] != "Metric":
            summary[cells[0]] = {"v": cells[1], "prov": "synthetic", "ref": src(exp, i, f"{cells[0]}: {cells[1]}", cells[0])}
        if section.startswith("SECTION C") and len(cells) >= 6 and cells[0] not in ("Sector",):
            sectors.append({"sector": cells[0], "pct": cells[1], "issuers": cells[2], "limit": cells[3],
                            "headroom": cells[4], "status": cells[5]})
    c_first = next(i for i, r in enumerate(lines, start=1) if r and r[0].startswith("SECTION C"))
    sect = src(exp, c_first, "SECTION C - Sector Exposure (Top 20 Sectors): " +
               "; ".join(f"{s['sector']} {s['pct']}" for s in sectors), "Sector exposure, top 20")
    mandate = "CP-6A_-_Mandate_File_-_Test_CLO_I_Ltd.csv"
    mand = {}
    with open(folder / mandate, newline="", encoding="utf-8-sig") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            if r["Field"] in PII_FIELDS:
                continue
            if r["Section"] in ("Strategy", "Capital Structure", "Mandate Constraints"):
                mand[r["Field"]] = {"v": r["Value"], "prov": "synthetic",
                                    "ref": src(mandate, i, f"{r['Section']}, {r['Field']}: {r['Value']}", r["Field"])}
    del sec_line
    return {"synthetic": True, "name": "Test CLO I Ltd", "asOf": "29-May-2026", "summary": summary, "sectors": sectors,
            "constraints": constraints, "mandate": mand, "sources": {"sectors": sect, **sources}}


def portfolio_fit(p: dict) -> dict:
    c = {r["id"]: r for r in p["constraints"]}
    leis = next(s for s in p["sectors"] if s["sector"] == "Leisure Facilities & Services")

    def ref(cid: str) -> str:
        return c[cid]["ref"]

    return {
        "synthetic": True, "illustrative": True, "portfolio": "Test CLO I Ltd",
        "overall": {"v": "Watch", "prov": "illustrative"},
        "summary": "A first-lien Caesars term loan fits the sector and lien limits; the CCC bucket (C-04) and single-name "
                   "limit (C-01) are near their ceilings, and the loans' own ratings are not in the sources.",
        "checks": [
            {"constraint": "C-06 Sector (Leisure Facilities & Services)", "limit": c["C-06"]["limit"], "current": leis["pct"],
             "headroom": leis["headroom"], "result": "Fits", "ref": p["sources"]["sectors"]},
            {"constraint": "C-09 Min 1st Lien / Senior Secured", "limit": c["C-09"]["limit"], "current": c["C-09"]["current"],
             "headroom": c["C-09"]["headroom"], "result": "Fits", "ref": ref("C-09")},
            {"constraint": "C-01 Max single issuer", "limit": c["C-01"]["limit"], "current": c["C-01"]["current"],
             "headroom": c["C-01"]["headroom"], "result": "Watch", "ref": ref("C-01"),
             "note": "Caps any Caesars position at the single-issuer limit."},
            {"constraint": "C-04 CCC bucket", "limit": c["C-04"]["limit"], "current": c["C-04"]["current"],
             "headroom": c["C-04"]["headroom"], "result": "Watch", "ref": ref("C-04"),
             "note": "Loan ratings are not in the sources; the CZR unsecured 2032s show Caa1 on TRACE."},
        ],
        "byInstrument": [
            {"instrument": "CEI Term Loan B", "fit": "Fits"}, {"instrument": "CEI Term Loan B-1", "fit": "Fits"},
            {"instrument": "CEI 6.50% Senior Secured Notes 2032", "fit": "Watch",
             "note": "No admitted document says whether a senior secured bond is an eligible CLO asset."},
            {"instrument": "CEI 6.00% Senior Notes 2032", "fit": "Breaches",
             "note": "Caa1 (Moody's, TRACE) would sit in the CCC bucket, already 0.14% from its ceiling."},
        ],
    }


# ---------------------------------------------------------------- illustrative judgement
def illustrative() -> dict:
    def r(text: str, refs: list[str]) -> dict:
        return {"text": text, "refs": refs, "illustrative": True}

    C = KEY_REF

    def F(key: str) -> str:
        return FIG[key]["v"]

    return {
        "_notice": "ILLUSTRATIVE. No RBOT run exists. Scores, recommendations, valuations and thesis lines are plausible "
                   "analyst views written for the mockups, grounded in the cited figures; they are not a view on Caesars.",
        "creditScore": {"pos": 3, "word": "Fair", "illustrative": True},
        "valuation": {"pos": 2, "word": "V2 Attractive", "illustrative": True},
        "creditDirection": {"word": "Deteriorating", "illustrative": True},
        "sectorOutlook": {"word": "Neutral", "illustrative": True},
        "sponsorQuality": {"word": "Medium", "illustrative": True,
                           "basis": "Fertitta Entertainment is an owner-operator, not a financial sponsor; its leverage appetite is untested in the sources."},
        "recommendation": {
            "CLO": {"pos": 3, "word": "MW", "illustrative": True},
            "Indexed Loans": {"pos": 3, "word": "MW", "illustrative": True},
            "Indexed HY": {"pos": 2, "word": "Modest OW", "illustrative": True},
        },
        "byInstrument": [
            {"facility": "CEI Revolving Credit Facility", "pos": None, "word": "N/A", "illustrative": True},
            {"facility": "CEI Term Loan A", "pos": None, "word": "N/A", "illustrative": True},
            {"facility": "CVA Delayed Draw Term Loan", "pos": None, "word": "N/A", "illustrative": True},
            {"facility": "CEI Term Loan B", "pos": 3, "word": "MW", "illustrative": True},
            {"facility": "CEI Term Loan B-1", "pos": 3, "word": "MW", "illustrative": True},
            {"facility": "CEI 7.00% Senior Secured Notes 2030", "pos": 3, "word": "MW", "illustrative": True},
            {"facility": "CEI 6.50% Senior Secured Notes 2032", "pos": 2, "word": "Modest OW", "illustrative": True},
            {"facility": "CEI 4.625% Senior Notes 2029", "pos": 4, "word": "Modest UW", "illustrative": True},
            {"facility": "CEI 6.00% Senior Notes 2032", "pos": 4, "word": "Modest UW", "illustrative": True},
            {"facility": "Special Improvement District Bonds 4.30%", "pos": None, "word": "N/A", "illustrative": True},
            {"facility": "Long-term notes and other payables", "pos": None, "word": "N/A", "illustrative": True},
        ],
        "thesis": r("Caesars is a large, cash-generative operator whose secured debt is well covered today, but a pending "
                    "take-private by Fertitta adds new debt of unstated size on top of a lease-heavy structure. Prefer the "
                    "secured 2032 notes, which trade below par, over the unsecured notes until the merger financing is known.",
                    [C["ltm_adj_ebitda_q2_2026"], C["trace_czr_12769gac4_last_price"], GAP_BY_KEY["merger_committed_debt_financing_amount"]]),
        "catalysts": [
            r("Go-shop period ended July 11, 2026.", [C["merger_go_shop_end"]]),
            r("Merger End Date May 27, 2027, extendable to August 27, 2027 and November 27, 2027.",
              [C["merger_initial_end_date"], C["merger_first_extended_end_date"], C["merger_second_extended_end_date"]]),
            r("Ticking fee accrues from June 26, 2027.", [C["merger_ticking_fee_date"]]),
            r("Disclosure of the committed debt financing (amount and tranches) for the merger.", [GAP_BY_KEY["merger_committed_debt_financing_amount"]]),
        ],
        "strengths": [
            {"label": "Scale and cash generation", **r(f"LTM Adjusted EBITDA of {F('ltm_adj_ebitda_q2_2026')} on net revenues of {F('ltm_net_revenues_q2_2026')}.", [C["ltm_adj_ebitda_q2_2026"], C["ltm_net_revenues_q2_2026"]])},
            {"label": "Liquidity", **r(f"Cash and revolver capacity of {F('liq_total')} at 30 June 2026 against {F('debt_maturity_remaining_2026')} of debt due in the rest of 2026.", [C["liq_total"], C["debt_maturity_remaining_2026"]])},
            {"label": "Regional growth", **r(f"Regional Adjusted EBITDA rose to {F('seg_adj_ebitda_regional_q2_2026')} from {F('seg_adj_ebitda_regional_q2_2025')} in Q2 2026.", [C["seg_adj_ebitda_regional_q2_2026"], C["seg_adj_ebitda_regional_q2_2025"]])},
            {"label": "Committed bid", **r(f"An all-cash offer at {F('merger_price_per_share_pr')}, not subject to a financing condition.", [C["merger_price_per_share_pr"], C["issuer.merger.financing_condition"]])},
        ],
        "weaknesses": [
            {"label": "Merger debt unknown", **r("The committed debt financing has no stated amount; leverage after closing cannot be computed.", [GAP_BY_KEY["merger_committed_debt_financing_amount"]])},
            {"label": "Lease burden", **r(f"Financing obligations to GLPI and VICI of {F('lt_financing_obligations_2026_06_30')} sit outside reported debt.", [C["lt_financing_obligations_2026_06_30"]])},
            {"label": "Las Vegas softness", **r(f"Las Vegas Adjusted EBITDA fell to {F('seg_adj_ebitda_las_vegas_q2_2026')} from {F('seg_adj_ebitda_las_vegas_q2_2025')} in Q2 2026.", [C["seg_adj_ebitda_las_vegas_q2_2026"], C["seg_adj_ebitda_las_vegas_q2_2025"]])},
            {"label": "Thin GAAP earnings", **r(f"Net loss attributable to Caesars of {F('net_income_attrib_q2_2026')} in Q2 2026 and {F('net_income_attrib_fy2025')} in FY2025.", [C["net_income_attrib_q2_2026"], C["net_income_attrib_fy2025"]])},
        ],
        "historicalPerformance": r(f"Net revenues have ranged from {rev_extremes()[0]} to {rev_extremes()[1]} between FY2023 and LTM Q2 2026 while Adjusted EBITDA has eased each year, from {FIG['adj_ebitda_fy2023']['v']} to {FIG['adj_ebitda_fy2025']['v']} in FY2025.",
                                   [C[rev_extremes()[2]], C[rev_extremes()[3]], C["adj_ebitda_fy2023"], C["adj_ebitda_fy2025"]]),
        "businessDescription": r("Caesars Entertainment reports four operating segments: Las Vegas, Regional, Caesars Digital, and Managed and Branded. "
                                 "It agreed on May 27, 2026 to be acquired by Fertitta Entertainment in an all-cash transaction valued at approximately $17.6 billion including assumed debt.",
                                 [C["seg_rev_las_vegas_q2_2026"], C["issuer.merger.agreement_date"], C["merger_transaction_value"]]),
        "transactionSummary": r("Fertitta Entertainment will acquire Caesars for 31.00 in cash, funded by Fertitta equity, assumed Caesars debt "
                                "and new committed debt financing from a group of 10 banks. The amount, tranches and pricing of the new debt are not in the sources.",
                                [C["merger_price_per_share_pr"], C["issuer.merger.financing"], GAP_BY_KEY["merger_committed_debt_financing_amount"]]),
        "keyFindings": [
            r(f"Total leverage {F('total_leverage_ltm')}x on LTM Adjusted EBITDA, before any merger debt.", [C["total_leverage_ltm"]]),
            r(f"Interest cover {F('interest_cover_ltm')}x including lease financing obligations; {F('cash_interest_cover_ltm')}x on debt cash interest alone.",
              [C["interest_cover_ltm"], C["cash_interest_cover_ltm"]]),
            r(f"No final maturity before {F('cei_rcf_maturity')}; {F('debt_maturity_2030')} is scheduled for 2030 in the 10-Q table, amortisation included.", [C["cei_rcf_maturity"], C["debt_maturity_2030"]]),
            r(f"Unsecured 2032s at {F('trace_czr_12769gad2_last_price')} ({F('trace_czr_12769gad2_moodys')}) against secured 2032s at {F('trace_czr_12769gac4_last_price')} ({F('trace_czr_12769gac4_moodys')}).",
              [C["trace_czr_12769gad2_last_price"], C["trace_czr_12769gac4_last_price"]]),
        ],
    }



# ---------------------------------------------------------------- operating model (cited from the filings)
DOCS_DIR = Path("/Users/ericguei/Documents/caos-databricks/qualification/czr-2026q2-full-credit-assessment/documents")
K10 = "CZR_FY2025_10K.txt"
Q10 = "CZR_Q2_2026_10Q.txt"
# (key, label, period, value, unit, file, line, verbatim excerpt of at most 15 words)
OPM_FACTS: list[tuple[str, str, str, str, str, str, int, str]] = [
    ("opm_founded", "Founded", "—", "1973", "year", K10, 90, "founded in 1973 by the Carano family"),
    ("opm_description", "Business description", "—", "geographically diversified gaming and hospitality company", "text", K10, 90,
     "geographically diversified gaming and hospitality company"),
    ("opm_revenue_source", "Primary source of revenue", "FY2025", "gaming operations", "text", K10, 93,
     "Our primary source of revenue is generated by our gaming operations"),
    ("opm_segments_count", "Reportable segments", "FY2025", "four reportable segments", "text", K10, 1071,
     "four reportable segments: (1) Las Vegas, (2) Regional, (3) Caesars Digital"),
    ("opm_mb_fees", "Managed and Branded earns", "FY2025", "fees", "text", K10, 130,
     "We earn revenue from fees paid for the management of other hotels and casinos"),
    ("opm_casino_share_fy2025", "Casino share of net revenues", "FY2025", "58", "%", K10, 105,
     "approximately 58% of our total net revenues in 2025"),
    ("opm_fb_share_fy2025", "Food and beverage share of net revenues", "FY2025", "15", "%", K10, 124,
     "represented approximately 15% of our total net revenues in 2025"),
    ("opm_hotel_share_fy2025", "Hotel share of net revenues", "FY2025", "17", "%", K10, 127,
     "represented approximately 17% of our total net revenues in 2025"),
    ("opm_properties", "Properties owned, leased or managed", "30 Jun 2026", "54", "count", Q10, 983,
     "aggregate of 54 properties in 20 jurisdictions in North America"),
    ("opm_jurisdictions", "Jurisdictions with properties", "30 Jun 2026", "20", "count", Q10, 983,
     "54 properties in 20 jurisdictions in North America"),
    ("opm_slots", "Slot machines, VLTs and e-tables", "30 Jun 2026", "53,800", "count", Q10, 983,
     "approximately 53,800 slot machines, video lottery terminals and e-tables"),
    ("opm_tables", "Table games", "30 Jun 2026", "2,800", "count", Q10, 983, "approximately 2,800 table games"),
    ("opm_rooms", "Hotel rooms", "30 Jun 2026", "46,300", "count", Q10, 983,
     "approximately 46,300 hotel rooms as of June 30, 2026"),
    ("opm_owned_casinos", "Casinos owned", "30 Jun 2026", "22", "count", Q10, 986, "we owned 22 of our casinos"),
    ("opm_leased_casinos", "Casinos leased", "30 Jun 2026", "25", "count", Q10, 986,
     "leased 25 casinos in North America"),
    ("opm_vici_casinos", "Casinos leased from VICI", "30 Jun 2026", "18", "count", Q10, 987,
     "We lease 18 casinos from VICI Properties L.P."),
    ("opm_glpi_casinos", "Casinos leased from GLPI", "30 Jun 2026", "six", "count", Q10, 988,
     "We also lease six casinos from GLP Capital, L.P."),
    ("opm_windsor", "Caesars Windsor lessor", "30 Jun 2026", "Ontario Lottery and Gaming Corporation", "text", Q10, 989,
     "we lease Caesars Windsor from the Ontario Lottery and Gaming Corporation"),
    ("opm_vici_term", "VICI lease initial term", "31 Dec 2025", "15-year", "text", K10, 1474,
     "a 15-year initial term with four five-year renewal options"),
    ("opm_vici_rent", "VICI initial annual fixed rent", "31 Dec 2025", "$1.1 billion", "text", K10, 1474,
     "initial annual fixed rent payments of $1.1 billion"),
    ("opm_vici_obligation", "VICI financing obligation", "31 Dec 2025", "$11.7 billion", "text", K10, 1480,
     "Our VICI Leases are accounted for as a financing obligation and totaled $11.7 billion"),
    ("opm_glpi_term", "GLPI Master Lease initial term", "31 Dec 2025", "20 years", "text", K10, 1485,
     "an initial term of 20 years (through September 2038)"),
    ("opm_glpi_obligation", "GLPI financing obligation", "31 Dec 2025", "$1.3 billion", "text", K10, 1488,
     "The GLPI Leases are accounted for as financing obligations and totaled $1.3 billion"),
    ("opm_sports_jurisdictions", "Sports wagering jurisdictions", "30 Jun 2026", "34", "count", Q10, 992,
     "across 34 jurisdictions in North America, 27 of which offer online sports betting"),
    ("opm_online_sports_jurisdictions", "Online sports betting jurisdictions", "30 Jun 2026", "27", "count", Q10, 992,
     "27 of which offer online sports betting"),
    ("opm_igaming_jurisdictions", "iGaming jurisdictions", "30 Jun 2026", "five", "count", Q10, 993,
     "we operate iGaming in five jurisdictions in North America"),
    ("opm_racebook_states", "Caesars Racebook states", "30 Jun 2026", "23", "count", Q10, 995,
     "operate the Caesars Racebook app in 23 states as of June 30, 2026"),
]
OPM_SEGS = [("Las Vegas", "las_vegas"), ("Regional", "regional"), ("Caesars Digital", "caesars_digital"),
            ("Managed and Branded", "managed_branded")]
OPM_TYPES = [("Casino", "casino"), ("Food and beverage", "fb"), ("Hotel", "hotel"), ("Other", "other")]
# segment net revenues and Adjusted EBITDA, FY2025: the 10-K MD&A results table (first value is 2025)
_SEG_REV = [("4,049", "Las Vegas | $4,049 | $4,274 | $4,470"), ("5,756", "Regional | 5,756 | 5,539 | 5,778"),
            ("1,408", "Caesars Digital | 1,408 | 1,163 | 973"), ("279", "Managed and Branded | 279 | 274 | 307")]
_SEG_EBITDA = [("1,728", "Las Vegas | $1,728 | $1,907 | $2,016"), ("1,789", "Regional | 1,789 | 1,810 | 1,962"),
               ("236", "Caesars Digital | 236 | 117 | 38"), ("67", "Managed and Branded | 67 | 71 | 76")]
for _i, (_lab, _s) in enumerate(OPM_SEGS):
    OPM_FACTS.append((f"opm_seg_rev_{_s}_fy2025", f"{_lab} net revenues", "FY2025", _SEG_REV[_i][0], "USD millions", K10, 1098 + _i, _SEG_REV[_i][1]))
    OPM_FACTS.append((f"opm_seg_ebitda_{_s}_fy2025", f"{_lab} Adjusted EBITDA", "FY2025", _SEG_EBITDA[_i][0], "USD millions", K10, 1106 + _i, _SEG_EBITDA[_i][1]))
# net revenues by type: FY2025 (10-K) and H1 2026 (10-Q consolidated table, third value)
_TYPE_FY = [("6,617", "Casino | $6,617 | $6,267 | $6,367"), ("1,714", "Food and beverage | 1,714 | 1,716 | 1,728"),
            ("1,945", "Hotel | 1,945 | 2,016 | 2,090"), ("1,210", "Other | 1,210 | 1,246 | 1,343")]
_TYPE_H1 = [("3,425", "Casino | $1,759 | $1,668 | $3,425 | $3,262"), ("850", "Food and beverage | 426 | 428 | 850 | 863"),
            ("982", "Hotel | 495 | 509 | 982 | 991"), ("606", "Other | 313 | 302 | 606 | 585")]
for _i, (_lab, _t) in enumerate(OPM_TYPES):
    OPM_FACTS.append((f"opm_type_{_t}_fy2025", f"{_lab} net revenues", "FY2025", _TYPE_FY[_i][0], "USD millions", K10, 1128 + _i, _TYPE_FY[_i][1]))
    OPM_FACTS.append((f"opm_type_{_t}_h1_2026", f"{_lab} net revenues", "H1 2026", _TYPE_H1[_i][0], "USD millions", Q10, 109 + _i, _TYPE_H1[_i][1]))
# net revenues by segment and type, Q2 2026 (10-Q Note 7); Corporate and Other eliminations are not drawn
_Q2_MATRIX = {  # type -> (line, [Las Vegas, Regional, Caesars Digital, Managed and Branded], row excerpt)
    "casino": (612, ["277", "1,144", "340", "—"], "Casino | $277 | $1,144 | $340 | $— | $(2) | $1,759"),
    "fb": (613, ["267", "160", "—", "—"], "Food and beverage | 267 | 160 | — | — | (1) | 426"),
    "hotel": (614, ["315", "180", "—", "—"], "Hotel | 315 | 180 | — | — | — | 495"),
    "other": (615, ["158", "86", "11", "57"], "Other | 158 | 86 | 11 | 57 | 1 | 313"),
}
for _lab, _t in OPM_TYPES:
    _ln, _vals, _ex = _Q2_MATRIX[_t]
    for _j, (_sl, _s) in enumerate(OPM_SEGS):
        if _vals[_j] != "—":
            OPM_FACTS.append((f"opm_mix_{_s}_{_t}_q2_2026", f"{_sl}: {_lab.lower()} net revenues", "Q2 2026", _vals[_j],
                              "USD millions", Q10, _ln, _ex))


def _norm(text: str) -> str:
    return " ".join(text.split())


def register_operating_model() -> None:
    """Cite every operating-model fact. Each is checked against the filing: the line must contain the
    verbatim excerpt (at most 15 words) and the value must appear in that excerpt."""
    source: dict[str, list[str]] = {}
    for key, label, period, value, unit, file, line, excerpt in OPM_FACTS:
        lines = source.setdefault(file, (DOCS_DIR / file).read_text(encoding="utf-8").split("\n"))
        if not 1 <= line <= len(lines) or _norm(excerpt) not in _norm(lines[line - 1]):
            raise ValueError(f"{key}: excerpt not found at {file} line {line}: {excerpt!r}")
        if len(excerpt.split()) > 15:
            raise ValueError(f"{key}: excerpt longer than 15 words")
        if value.lower() not in excerpt.lower():
            raise ValueError(f"{key}: value {value!r} not in excerpt {excerpt!r}")
        cid = cite(key, {"label": label, "period": period, "value": value, "unit": unit, "file": file, "line": line, "excerpt": excerpt})
        FIG[key] = {"v": paren(value), "raw": value, "unit": unit, "label": label, "period": period, "prov": "cited", "ref": cid}


def operating_model() -> tuple[dict, dict]:
    """Calculated shares and margins, the operating-model tables and the segment-mix chart."""
    tot = "net_revenues_fy2025"
    for lab, s in OPM_SEGS:
        calc(f"opm_seg_share_{s}_fy2025", f"{lab} share of net revenues", "FY2025", val(f"opm_seg_rev_{s}_fy2025") / val(tot) * 100, 1, "%",
             "{opm_seg_rev_%s_fy2025} / {%s} x 100" % (s, tot), [f"opm_seg_rev_{s}_fy2025", tot])
        calc(f"opm_seg_margin_{s}_fy2025", f"{lab} Adjusted EBITDA margin", "FY2025",
             val(f"opm_seg_ebitda_{s}_fy2025") / val(f"opm_seg_rev_{s}_fy2025") * 100, 1, "%",
             "{opm_seg_ebitda_%s_fy2025} / {opm_seg_rev_%s_fy2025} x 100" % (s, s), [f"opm_seg_ebitda_{s}_fy2025", f"opm_seg_rev_{s}_fy2025"])
    stated = {"casino": "opm_casino_share_fy2025", "fb": "opm_fb_share_fy2025", "hotel": "opm_hotel_share_fy2025"}
    other_share = {"v": None, "prov": "gap", "reason": "the 10-K states shares for casino, food and beverage and hotel only"}
    t = {
        "segments": {
            "title": "Segments, FY2025", "unit": "US$ m",
            "columns": ["Net revenues FY2025", "Share of net revenues, %", "Adj. EBITDA FY2025", "Adj. EBITDA margin, %"],
            "rows": [{"label": lab, "cells": [D(f"opm_seg_rev_{s}_fy2025"), D(f"opm_seg_share_{s}_fy2025"),
                                              D(f"opm_seg_ebitda_{s}_fy2025"), D(f"opm_seg_margin_{s}_fy2025")]} for lab, s in OPM_SEGS],
            "note": "Corporate and Other (net revenues (6), Adjusted EBITDA (196)) is not shown; shares are of consolidated net revenues of "
                    + FIG[tot]["v"] + ".",
        },
        "revenueType": {
            "title": "Net revenues by type", "unit": "US$ m", "columns": ["FY2025", "H1 2026", "Share of FY2025, % as stated"],
            "rows": [{"label": lab, "cells": [D(f"opm_type_{x}_fy2025"), D(f"opm_type_{x}_h1_2026"),
                                              D(stated[x]) if x in stated else other_share]} for lab, x in OPM_TYPES],
        },
    }
    mix_series = []
    for lab, x in OPM_TYPES:
        vals = []
        for _sl, s in OPM_SEGS:
            k = f"opm_mix_{s}_{x}_q2_2026"
            vals.append(D(k) if k in FIG else None)
        mix_series.append({"label": lab, "color": {"casino": 1, "fb": 2, "hotel": 5, "other": 4}[x], "values": vals})
    c = {
        "segmentMix": {
            "id": "fig-segment-mix", "title": "Net revenues by segment and type, Q2 2026", "unit": "US$ m", "categoryLabel": "Segment",
            "categories": [lab for lab, _ in OPM_SEGS],
            "summary": "Regional is the largest segment and casino the largest revenue type; Managed and Branded earns fees recorded in Other.",
            "series": mix_series,
            "note": "A cell the 10-Q prints as — (nil) is not drawn. Corporate and Other eliminations of (2) casino and (1) food and beverage are not shown.",
            "source": "Caesars Q2 2026 10-Q, Note 7 Revenue Recognition",
        },
    }
    return t, c

# ---------------------------------------------------------------- run metadata, modules, limitations
def meta_block() -> dict:
    return {
        "issuer": "Caesars Entertainment, Inc.", "ticker": "CZR", "issuerRef": KEY_REF["issuer.name"],
        "pathway": "Full Credit Assessment", "depth": "Full", "primary": True,
        "primaryLabel": "Primary: 2026 Fertitta merger financing",
        "analysisDate": "2026-10-02", "reportingPeriod": "Q2 2026",
        "analyst": {"v": "Credit Research (illustrative)", "prov": "illustrative"},
        "runId": None, "runNote": "No RBOT run exists; this is a design mockup.",
        "strategies": ["CLO", "Indexed Loans", "Indexed HY"],
    }


def modules() -> list[dict]:
    g = GAP_BY_KEY
    mods = [
        {"id": "CP-0", "name": "Source readiness", "status": "Restricted",
         "reason": "Ratings outlooks, Fitch and the merger's debt commitment terms are missing from the Source Pack.",
         "refs": [g["rating_fitch"], g["rating_outlooks_moodys_sp"], g["merger_committed_debt_financing_amount"]]},
        {"id": "CP-1", "name": "Financial analysis and capital structure", "status": "Pass", "reason": "Historical financials, debt table and liquidity reconcile to the filings.", "refs": []},
        {"id": "CP-1B", "name": "Earnings delta", "status": "Restricted",
         "reason": "Q2 2026 against Q2 2025 revenue, Adjusted EBITDA, segments and the EBITDA reconciliation are cited; "
                   "quarterly cash flows, cash interest and cash taxes are disclosed for six months only, so the cash side of the delta is H1.",
         "refs": [g["cfo_q2_2026 / q2_2025"], g["cash_interest_paid_q2_2026 / q2_2025"], g["income_taxes_paid_q2_2026 / q2_2025"]]},
        {"id": "CP-2", "name": "Forecast, liquidity and cash flow", "status": "Restricted",
         "reason": "No company revenue or EBITDA guidance; quarterly cash flows are not disclosed.",
         "refs": [g["czr_financial_guidance_revenue_ebitda"], g["cfo_q2_2026 / q2_2025"]]},
        {"id": "CP-3", "name": "Credit score and relative value", "status": "Restricted",
         "reason": "TRACE gives yields, not spreads; no loan prices; peer EBITDAR definitions differ.",
         "refs": [g["spread_to_treasury"], g["loan_margins_prices"], g["mgm_consolidated_adj_ebitdar / penn_consolidated_adj_ebitdar"]]},
        {"id": "CP-4", "name": "Documentation and covenants", "status": "Restricted",
         "reason": "No covenant level is cited; covenant headroom is not computed.", "refs": [g["covenant_levels"]]},
        {"id": "CP-5", "name": "Issue log and review", "status": "Pass", "reason": "Every figure carries a citation or a formula; gaps are logged.", "refs": []},
        {"id": "CP-6", "name": "Portfolio fit (Test CLO I)", "status": "Restricted",
         "reason": "Synthetic mandate; the eligibility of senior secured bonds is not stated and loan ratings are missing.",
         "refs": [g["issuer_ratings"]]},
    ]
    questions = {  # the reader question each module answers (module role, not a finding)
        "CP-0": "Is the Source Pack complete enough to analyse this issuer, and what is missing?",
        "CP-1": "What are the issuer's earnings base, capital structure and leverage today?",
        "CP-1B": "What changed between Q2 2025 and Q2 2026, and where did it come from?",
        "CP-2": "Can the issuer meet its obligations over the next twelve months, and what breaks first in a downside?",
        "CP-3": "How do the issuer's bonds and loans price against peers, and what score and valuation follow?",
        "CP-4": "What do the documents allow the issuer to do, and how much covenant headroom is there?",
        "CP-5": "Does every figure trace to a source, and do the reconciliations close?",
        "CP-6": "Does the issuer fit the portfolio's mandate and constraints?",
    }
    for m in mods:
        m["question"] = questions[m["id"]]
    return mods


def limitations() -> list[dict]:
    out = []
    scopes = {"pf_ltm": "Model limitation: PF-LTM column",
              "merger_committed_debt_financing_amount": "Model limitation: PF-LTM column"}
    for gid, g in GAPS.items():
        out.append({"ref": gid, "field": g["field"], "text": g["reason"], "origin": g["origin"],
                    "scope": scopes.get(g["field"], "Source Pack gap")})
    return out


# ---------------------------------------------------------------- main
def main() -> None:
    czr_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CZR
    port_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORTFOLIO
    load_czr(czr_path)
    register_operating_model()
    derive()
    om_tables, om_charts = operating_model()
    portfolio = load_portfolio(port_path)
    for sid, s in portfolio["sources"].items():
        if isinstance(s, dict):
            CITES[sid] = s
    data = {
        "meta": meta_block(),
        "citations": CITES,
        "calcs": CALCS,
        "gaps": GAPS,
        "figures": FIG,
        "tables": {**tables(), "operatingModel": om_tables},
        "charts": {**charts(portfolio), **om_charts},
        "modules": modules(),
        "limitations": limitations(),
        "illustrative": illustrative(),
        "portfolio": {**portfolio, "fit": portfolio_fit(portfolio)},
        "counts": {
            "cited": sum(1 for c in CITES.values() if c["id"].startswith("C")),
            "calculated": len(CALCS), "gaps": len(GAPS),
            "synthetic_sources": sum(1 for c in CITES.values() if c["id"].startswith("S")),
        },
    }
    # the sector source id is referenced by a key, keep it resolvable
    data["portfolio"]["sources"] = {k: v for k, v in portfolio["sources"].items()}
    body = json.dumps(data, ensure_ascii=False, indent=1)
    OUT.write_text("/* Generated by build-data.py from czr.json and the Test CLO I CSVs. Do not edit by hand. */\n"
                   "window.RBOT_DATA = " + body + ";\n", encoding="utf-8")
    print(f"wrote {OUT} : {data['counts']}")


if __name__ == "__main__":
    main()
