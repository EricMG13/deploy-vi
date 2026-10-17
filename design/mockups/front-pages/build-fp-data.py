#!/usr/bin/env python3
"""Build fp-data.js (window.RBOT_FP) for the Front Page mockups. Standard library only.

Inputs
  ../shared/data.js  the base data (window.RBOT_DATA), parsed as JSON
  fp-extract.json    39 supplementary citations: file, line, verbatim excerpt

What it does (SPEC.md section 3)
  * verifies every excerpt against its corpus line and stops, naming the key, on a mismatch;
  * continues the id sequences: citations C338+, synthetic S46+, calculations K110+, gaps G29+;
  * computes every calculation with Decimal (ROUND_HALF_UP) from the stored inputs;
  * builds the modules, block tables, chart specs, Portfolio Fit and Pathways, resolving every
    template token ({key|unit}, [key], [G8], [gap:name]) and stopping on an unknown key;
  * writes fp-data.js: window.RBOT_FP, then a merge into window.RBOT_DATA that throws on a clash.

Usage: python3 build-fp-data.py [data.js] [fp-extract.json]
       python3 build-fp-data.py --check [data.js] [fp-extract.json]   (self-test; writes nothing)
"""

from __future__ import annotations

import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / "shared" / "data.js"
DEFAULT_EXTRACT = HERE / "fp-extract.json"
OUT = HERE / "fp-data.js"

UNIT_DISPLAY = {
    "USD millions": "US$ m",
    "USD billions": "US$ bn",
    "USD": "US$",
    "x": "x",
    "%": "%",
    "pp": "pp",
    "% NAV": "% NAV",
    "months": "months",
}
SEGMENTS = [
    ("las_vegas", "Las Vegas"),
    ("regional", "Regional"),
    ("caesars_digital", "Caesars Digital"),
    ("managed_branded", "Managed and Branded"),
]
# Ordered words per scale (rules.json scales, interfaces spec 14.1). Position = index + 1 (meter fill);
# a word outside the list is an error.
SCALES = {
    "severity": ["Low", "Medium", "High"],
    "ordinal": ["Low", "Medium", "High"],
    "confidence": ["Low", "Medium", "High"],
    "gate_status": ["Not met", "Unclear", "Met"],
    "availability": ["Not available", "Unclear", "Available"],
    "alignment": ["Divergent", "Unclear", "Aligned"],
    "preference": ["Avoid", "Requires more work", "Neutral", "Preferred"],
    "compensation": ["Inadequate", "Unclear", "Adequate", "Attractive"],
    "calc_status": ["Not computable", "Directional", "Calculated"],
    "delta_direction": ["Down", "Flat", "Up"],
    "addback_verdict": ["Rejected", "Challenged", "Supported"],
    "debt_like_treatment": ["Not debt-like", "Unclear", "Debt-like"],
    "comparability": ["Weak", "Partial", "Close"],
    "trigger_status": ["Not computable", "Breached", "Tight", "Headroom"],
}
REC_WORDS = {1: "Strong OW", 2: "Modest OW", 3: "MW", 4: "Modest UW", 5: "Strong UW"}
VAL_WORDS = {
    1: "V1 Very attractive",
    2: "V2 Attractive",
    3: "V3 Fair",
    4: "V4 Unattractive",
    5: "V5 Very unattractive",
}
FINAL_ID = re.compile(r"^[CKGS]\d+$")
TOKEN = re.compile(r"\{([A-Za-z0-9_.]+)(?:\|([^}]*))?\}|\[(gap:[a-z0-9_]+|[A-Za-z0-9_.]+)\]")

# Reader questions, verbatim from docs/superpowers/specs/2026-10-11-deploy-vi-interfaces.md section 1.
QUESTIONS = {
    "CP-0": "Can this Source Pack support the requested work for this issuer, and what is missing?",
    "CP-1": "What are the issuer's canonical figures, definitions and instruments, period by period, with every figure cited?",
    "CP-1A": "Which business, ownership, transaction and operating facts matter most to the creditor?",
    "CP-1B": "How did earnings and KPIs change, what drove it, and how reliable is the signal?",
    "CP-1C": "Where does the borrower sit against comparable peers, and what is the credit implication?",
    "CP-1D": "How much of adjusted EBITDA is supported by evidence, and what is debt-like beyond reported debt?",
    "CP-2": "What is the fundamental credit profile, its strongest support and its primary downside?",
    "CP-2A": "What breaks first under stress, how does it transmit, and where does creditor risk become acute?",
    "CP-2D": "Is accessible liquidity sufficient for the next 12 months, and where is the pinch point?",
    "CP-2G": "How do base and downside cases change leverage, liquidity and refinancing capacity over time?",
    "CP-2H": "What rating pressure is evidenced, which trigger is nearest, and on what timing?",
    "CP-3": "Which instrument is best compensated for its risk, and at what level, including a new tranche at its talk?",
    "CP-3C": "Where is refinancing pressure concentrated, which path is most credible, and which creditor class is exposed?",
    "CP-3D": "What risk is the market pricing, what remains unpriced, and how fresh is the signal?",
    "CP-4": "Which provisions protect or weaken creditors, and through what PD/LGD mechanism?",
    "CP-4C": "If the distress gate is met, which path and fulcrum are most credible and what recoveries follow?",
    "CP-5": "Is the analysis traceable enough for the decision, and which provenance gap matters most?",
    "CP-6": "What Recommendation survives the strongest challenge, per Strategy and per instrument?",
}

# New gaps (SPEC 3.4), in order: G29 onward. The last one is added by this build (see GAP_NOT_SHOWN).
NEW_GAPS = [
    (
        "capex_2027",
        "Capital expenditure estimate for 2027",
        "not in the sources; the 10-Q estimates capital expenditure for the remainder of 2026 only",
    ),
    (
        "rate_deck",
        "Forward rate deck",
        "no forward SOFR curve or rate deck is in the Source Pack",
    ),
    (
        "agency_triggers",
        "Agency rating-trigger thresholds",
        "no rating-agency report is in the Source Pack, so downgrade and upgrade thresholds are not stated",
    ),
    (
        "rp_capacity",
        "Restricted payment and investment basket capacity",
        "the credit agreement and indenture baskets for restricted payments and investments were not extracted",
    ),
    (
        "incremental_usage",
        "Incremental amounts already used",
        "amounts used under the incremental free-and-clear clause since the Third Amendment are not stated in the sources",
    ),
    (
        "covenant_basis",
        "Agreement-basis covenant ratios",
        "the agreement's EBITDA, Total Net Debt and Cash Interest Expense are not reconciled to company figures; "
        "current ratios are on RBOT's basis (company Adjusted EBITDA, face debt)",
    ),
    (
        "issue_ratings_other",
        "Issue ratings for the term loans, the 2030 secured notes and the 2029 notes",
        "not in the sources; the TRACE pages rate the two 2032 notes only",
    ),
    (
        "structure_map",
        "Restricted, unrestricted and guarantor subsidiaries",
        "the entity and guarantor structure is not extracted; the supplemental indentures add guarantors "
        "without a full list in the extraction",
    ),
    (
        "implied_pd",
        "Market-implied default probability",
        "needs spreads or a risk-free curve (G19) and a recovery assumption; not computed",
    ),
    (
        "lease_claims",
        "Treatment of the GLPI and VICI master leases in a restructuring",
        "not modelled; lease claims are excluded from the waterfall and the leases are assumed to continue",
    ),
    (
        "cr_score",
        "CR Score for the merger's new tranches",
        "the new tranches are not stated in the sources (G8), so no CR Score can be read",
    ),
    (
        "bond_eligibility",
        "Whether a senior secured bond is an eligible Test CLO I asset",
        "the mandate excerpt does not say",
    ),
    # Added by this build, not by SPEC 3.4: a cell that is "n/a" because a measure has no meaning (not because
    # a source is missing) still needs a gap record for the cell's reason to open from.
    (
        "pct_not_shown",
        "Percentage change",
        "not shown: the line is itself a percentage or ratio, or its base is negative or changes sign, "
        "or the comparison does not call for it",
    ),
]
GAP_NOT_SHOWN = "pct_not_shown"

PATHWAY_DEFS = [
    (
        "EARNINGS_UPDATE",
        "Earnings Update",
        "Earnings update",
        "Earnings Update: Q2 2026",
        ["CP-0", "CP-1", "CP-1A", "CP-1B", "CP-1D", "CP-2"],
        False,
        ["CP-0", "CP-1", "CP-1A", "CP-DR", "CP-1B", "CP-1D", "MODEL", "CP-2", "CP-5", "CP-8"],
    ),
    (
        "RELATIVE_VALUE",
        "Relative Value",
        "Relative value",
        "Relative Value",
        [
            "CP-0",
            "CP-1",
            "CP-1A",
            "CP-1D",
            "CP-1C",
            "CP-2",
            "CP-2A",
            "CP-4",
            "CP-2G",
            "CP-3D",
            "CP-3",
        ],
        True,
        [
            "CP-0",
            "CP-1",
            "CP-1A",
            "CP-DR",
            "CP-1D",
            "MODEL",
            "CP-1C",
            "CP-2",
            "CP-2A",
            "CP-4",
            "CP-2G",
            "PROJECTION",
            "CP-3D",
            "CP-3",
            "FIT",
            "CP-5",
            "CP-6",
            "CP-8",
        ],
    ),
    (
        "COVENANT_REFINANCING",
        "Covenant & Refinancing",
        "Covenants & refinancing",
        "Covenant & Refinancing",
        ["CP-0", "CP-1", "CP-1A", "CP-1D", "CP-2", "CP-4", "CP-2D", "CP-3C"],
        False,
        [
            "CP-0",
            "CP-1",
            "CP-1A",
            "CP-DR",
            "CP-1D",
            "MODEL",
            "CP-2",
            "CP-4",
            "CP-2D",
            "CP-3C",
            "CP-5",
            "CP-8",
        ],
    ),
    (
        "DISTRESSED_RESTRUCTURING",
        "Distressed & Restructuring",
        "Distress & recovery",
        "Distressed & Restructuring",
        [
            "CP-0",
            "CP-1",
            "CP-1A",
            "CP-1D",
            "CP-2",
            "CP-2A",
            "CP-4",
            "CP-2D",
            "CP-2G",
            "CP-2H",
            "CP-3D",
            "CP-3C",
            "CP-4C",
            "CP-3",
        ],
        True,
        [
            "CP-0",
            "CP-1",
            "CP-1A",
            "CP-DR",
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
            "CP-5",
            "CP-6",
            "CP-8",
        ],
    ),
    (
        "PORTFOLIO_DECISION",
        "Portfolio Decision",
        "Portfolio decision",
        "Portfolio Decision",
        ["CP-0", "CP-1", "CP-1A", "CP-1D", "CP-2", "CP-2A", "CP-4", "CP-3D", "CP-3"],
        True,
        [
            "CP-0",
            "CP-1",
            "CP-1A",
            "CP-DR",
            "CP-1D",
            "MODEL",
            "CP-2",
            "CP-2A",
            "CP-4",
            "CP-3D",
            "CP-3",
            "FIT",
            "CP-5",
            "CP-6",
            "CP-8",
        ],
    ),
]
_BASE_TABLES = ["creditView", "transactionsEvents", "cashConversion", "debtLikeItems"]
_COV_TABLES = ["covenantTests", "redFlags", "capacity"]
# Block tables each Pathway draws (SPEC section 4 module sections), used to scope each Pathway's limitations.
PATHWAY_TABLES = {
    "EARNINGS_UPDATE": _BASE_TABLES
    + [
        "periodComparison",
        "segmentChanges",
        "varianceDrivers",
        "kpiChanges",
        "guidance",
        "signals",
        "addbackAssessment",
        "watchItems",
    ],
    "RELATIVE_VALUE": _BASE_TABLES
    + _COV_TABLES
    + [
        "peerSet",
        "downsidePaths",
        "marketVsFundamental",
        "instrumentLevels",
        "compensation",
        "securityPreference",
        "challenge",
    ],
    "COVENANT_REFINANCING": _BASE_TABLES
    + [
        "documentRegister",
        "covenantTests",
        "capacity",
        "structureMap",
        "redFlags",
        "ebitdaDefinition",
        "protectionScore",
        "liquiditySources",
        "cashUses",
        "runway",
        "maturityPressure",
        "lmeCapacity",
        "refinancingPaths",
        "creditorExposure",
    ],
    "DISTRESSED_RESTRUCTURING": _BASE_TABLES
    + _COV_TABLES
    + [
        "downsidePaths",
        "liquiditySources",
        "cashUses",
        "runway",
        "ratingTriggers",
        "migrationView",
        "marketVsFundamental",
        "maturityPressure",
        "lmeCapacity",
        "refinancingPaths",
        "creditorExposure",
        "distressGate",
        "claims",
        "evScenarios",
        "recoveries",
        "restructuringPaths",
        "instrumentLevels",
        "compensation",
        "securityPreference",
        "challenge",
    ],
    "PORTFOLIO_DECISION": _BASE_TABLES
    + _COV_TABLES
    + [
        "downsidePaths",
        "marketVsFundamental",
        "instrumentLevels",
        "compensation",
        "securityPreference",
        "challenge",
        "bindingLimitations",
    ],
}
# Gaps a Pathway's call band or Fit lines cite beyond its tables.
PATHWAY_EXTRA_GAPS = {
    "COVENANT_REFINANCING": ["cr_score"],
    "RELATIVE_VALUE": ["issue_ratings_other"],
    "DISTRESSED_RESTRUCTURING": ["issue_ratings_other"],
    "PORTFOLIO_DECISION": ["issue_ratings_other"],
}

# Expected displayed strings (SPEC 3.2); --check compares each with the built figure.
EXPECTED = {
    "eu_rev_chg_q2": "86",
    "eu_ebitda_chg_q2": "(35)",
    "eu_ebitda_pct_q2": "(3.7)",
    "eu_margin_q2_2025": "32.9",
    "eu_margin_chg_pp": "(2.1)",
    "eu_netloss_chg_q2": "20",
    "eu_int_chg_q2": "(6)",
    "eu_int_pct_q2": "(1.0)",
    "eu_da_chg_q2": "(9)",
    "eu_da_pct_q2": "(2.5)",
    "eu_capex_chg_q2": "(63)",
    "eu_capex_pct_q2": "(27.4)",
    "eu_cfo_chg_h1": "(5)",
    "eu_cfo_pct_h1": "(0.7)",
    "eu_netdebt_chg": "(176)",
    "eu_netlev_chg": "(0.02)",
    "eu_seg_rev_pct_las_vegas": "(3.5)",
    "eu_seg_rev_pct_regional": "9.4",
    "eu_seg_rev_pct_caesars_digital": "2.3",
    "eu_seg_rev_pct_managed_branded": "(23.0)",
    "eu_seg_ebitda_pct_las_vegas": "(12.6)",
    "eu_seg_ebitda_pct_regional": "11.2",
    "eu_seg_ebitda_pct_caesars_digital": "(15.0)",
    "eu_seg_ebitda_pct_managed_branded": "(5.9)",
    "eu_seg_margin_las_vegas_q2_2026": "40.3",
    "eu_seg_margin_las_vegas_q2_2025": "44.5",
    "eu_seg_margin_regional_q2_2026": "31.1",
    "eu_seg_margin_regional_q2_2025": "30.6",
    "eu_seg_margin_caesars_digital_q2_2026": "19.4",
    "eu_seg_margin_caesars_digital_q2_2025": "23.3",
    "eu_seg_margin_managed_branded_q2_2026": "28.1",
    "eu_seg_margin_managed_branded_q2_2025": "23.0",
    "eu_seg_margin_chg_las_vegas": "(4.2)",
    "eu_seg_margin_chg_regional": "0.5",
    "eu_seg_margin_chg_caesars_digital": "(4.0)",
    "eu_seg_margin_chg_managed_branded": "5.1",
    "rv_yield_pickup": "1.25",
    "dq_conv_fy2023": "45.9",
    "dq_conv_fy2024": "28.8",
    "dq_conv_fy2025": "35.9",
    "dq_conv_h1_2025": "37.0",
    "dq_conv_h1_2026": "37.4",
    "dq_conv_ltm": "36.1",
    "cr_mand_uses": "1,474",
    "cr_disc_uses": "205",
    "cr_closing": "1,249",
    "cr_headroom": "1,454",
    "cr_runway_months": "35.8",
    "cr_rcf_share": "72.7",
    "cr_liq_left_2026": "2,873",
    "cr_liq_left_2027": "2,759",
    "cr_liq_left_2028": "(138)",
    "cr_liq_left_2029": "(1,712)",
    "cr_liq_left_2030": "(5,674)",
    "cr_liq_left_after": "(11,009)",
    "cr_gap_2028": "138",
    "cr_gap_2029": "1,712",
    "cr_gap_2030": "5,674",
    "cr_gap_after": "11,009",
    "cr_rcf_util_pct": "5.3",
    "cov_tlr_headroom": "3.48",
    "cov_fccr_headroom": "2.63",
    "cov_sslr_headroom": "1.86",
    "ind_fccr_headroom": "2.63",
    "cap_pari_secured": "6,696",
    "cap_junior_secured": "7,594",
    "cap_free_clear_size": "3,592",
    "lme_sec_lme": "16,164",
    "lme_uns_base": "11,768",
    "lme_uns_lme": "18,464",
    "dr_ebitda_after_rent": "2,229",
    "dr_merger_multiple": "7.90",
    "dr_ev_downside": "11,145",
    "dr_ev_stress": "8,916",
    "dr_rec_merger_secured": "100.0",
    "dr_rec_merger_unsecured": "100.0",
    "dr_rec_merger_other": "100.0",
    "dr_residual_merger": "5,793",
    "dr_rec_downside_secured": "100.0",
    "dr_rec_downside_unsecured": "72.9",
    "dr_rec_downside_other": "0.0",
    "dr_residual_downside": "0",
    "dr_rec_stress_secured": "94.2",
    "dr_rec_stress_unsecured": "0.0",
    "dr_rec_stress_other": "0.0",
    "dr_residual_stress": "0",
    "fit_one_pct_nav": "6,309,285",
    "fit_c01_room": "15,773,213",
    "fit_c04_room": "883,300",
    "fit_c05_room": "8,012,792",
    "fit_sector_room": "34,259,418",
    "fit_c10_room": "59,244,186",
}
# Per-instrument Portfolio Fit expectations (SPEC 3.2): verdict, max size (displayed), final rec position.
EXPECTED_FIT = {
    "ssn_2032": ("Fits", "15,773,213", 2),
    "tlb": ("Watch", "883,300", 3),
    "tlb1": ("Watch", "883,300", 3),
    "ssn_2030": ("Watch", "883,300", 3),
    "sn_2029": ("Watch", None, 4),
    "sn_2032": ("Watch", "883,300", 4),
}


class BuildError(Exception):
    """A SPEC instruction could not be carried out as written."""


# ---------------------------------------------------------------- formatting
def dec(text: str) -> Decimal:
    t = str(text).strip().replace(",", "").replace("$", "")
    if t.startswith("(") and t.endswith(")"):
        t = "-" + t[1:-1]
    try:
        return Decimal(t)
    except InvalidOperation as exc:
        raise BuildError(f"not a number: {text!r}") from exc


def q(d: Decimal, places: int) -> Decimal:
    return d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def fmt(d: Decimal, places: int = 0) -> str:
    v = q(d, places)
    s = f"{abs(v):,.{places}f}"
    return f"({s})" if v < 0 else s


def disp_unit(unit: str | None) -> str | None:
    return UNIT_DISPLAY.get(unit or "")


def load_data_js(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.index("{")
    end = text.rindex("}")
    return json.loads(text[start : end + 1])


class Ctx:
    """The registries and helpers one build uses."""

    def __init__(self, base: dict, extract: dict) -> None:
        self.base = base
        self.extract = extract
        self.cit: dict[str, dict] = {}
        self.calcs: dict[str, dict] = {}
        self.gaps: dict[str, dict] = {}
        self.fig: dict[str, dict] = {}
        self.local: dict[str, dict] = {}  # inputs read from synthetic rows; not emitted as figures
        self.gap_by_name: dict[str, str] = {}
        self.verified = 0
        self._next = {
            "C": 1 + max(int(k[1:]) for k in base["citations"] if k.startswith("C")),
            "S": 1 + max(int(k[1:]) for k in base["citations"] if k.startswith("S")),
            "K": 1 + max(int(k[1:]) for k in base["calcs"]),
            "G": 1 + max(int(k[1:]) for k in base["gaps"]),
        }

    # -- ids
    def new_id(self, prefix: str) -> str:
        n = self._next[prefix]
        self._next[prefix] = n + 1
        return f"{prefix}{n}"

    def known_ref(self, ref: str) -> bool:
        b = self.base
        return any(
            ref in d
            for d in (b["citations"], b["calcs"], b["gaps"], self.cit, self.calcs, self.gaps)
        )

    def record(self, ref: str) -> dict:
        for d in (
            self.base["citations"],
            self.base["calcs"],
            self.base["gaps"],
            self.cit,
            self.calcs,
            self.gaps,
        ):
            if ref in d:
                return d[ref]
        raise BuildError(f"unknown reference {ref}")

    # -- figures
    def figure(self, key: str) -> dict:
        if key in self.fig:
            return self.fig[key]
        if key in self.local:
            return self.local[key]
        if key in self.base["figures"]:
            return self.base["figures"][key]
        raise BuildError(f"unknown figure key: {key}")

    def ref(self, key: str) -> str:
        return self.figure(key)["ref"]

    def val(self, key: str) -> Decimal:
        return dec(self.figure(key)["raw"])

    def dv(self, key: str) -> dict:
        """A table-cell Datum for a figure key."""
        f = self.figure(key)
        out = {"v": f["v"], "prov": f["prov"], "ref": f["ref"]}
        u = disp_unit(f.get("unit"))
        if u:
            out["unit"] = u
        if f.get("reason"):
            out["reason"] = f["reason"]
        return out

    def cd(self, key: str) -> dict:
        """A chart Datum (only the fields the chart kit reads)."""
        d = self.dv(key)
        d.pop("unit", None)
        return d

    def gap_id(self, name: str) -> str:
        if FINAL_ID.match(name):
            return name
        if name not in self.gap_by_name:
            raise BuildError(f"unknown gap: {name}")
        return self.gap_by_name[name]

    def gd(self, name: str, reason: str | None = None) -> dict:
        gid = self.gap_id(name)
        return {
            "v": None,
            "prov": "gap",
            "ref": gid,
            "reason": reason or self.record(gid)["reason"],
        }

    def sref(self, key: str) -> str:
        return self.ref(key)

    # -- prose
    def res(self, text: str) -> tuple[str, list[str]]:
        refs: list[str] = []

        def one(m: re.Match) -> str:
            if m.group(1):
                key, unit = m.group(1), m.group(2)
                ref = key if FINAL_ID.match(key) else self.ref(key)
                out = "{" + ref + (("|" + unit) if unit else "") + "}"
            else:
                key = m.group(3)
                if key.startswith("gap:"):
                    ref = self.gap_id(key[4:])
                elif FINAL_ID.match(key):
                    ref = key
                else:
                    ref = self.ref(key)
                out = "[" + ref + "]"
            if not self.known_ref(ref):
                raise BuildError(f"token {m.group(0)!r} resolves to unknown reference {ref}")
            if ref not in refs:
                refs.append(ref)
            return out

        return TOKEN.sub(one, text), refs

    def T(self, text: str, **flags) -> dict:
        t, refs = self.res(text)
        return {"text": t, "refs": refs, **flags}

    # -- registration
    def verify_and_register(self, corpus: Path) -> None:
        for it in self.extract["items"]:
            key = it["key"]
            path = corpus / it["file"]
            if not path.is_file():
                raise BuildError(f"{key}: corpus file not found: {path}")
            lines = path.read_text(encoding="utf-8").split("\n")
            n = it["line"]
            if n < 1 or n > len(lines) or it["excerpt"] not in lines[n - 1]:
                raise BuildError(f"{key}: excerpt not found on {it['file']} line {n}")
            self.verified += 1
            syn = bool(it.get("synthetic"))
            cid = self.new_id("S" if syn else "C")
            rec = {
                "id": cid,
                "key": key,
                "label": it["label"],
                "period": it["period"],
                "value": it["value"],
                "unit": it["unit"],
                "file": it["file"],
                "line": n,
                "locator": it["locator"],
                "excerpt": it["excerpt"],
            }
            if syn:
                rec["synthetic"] = True
            self.cit[cid] = rec
            if key in self.base["figures"] or key in self.fig:
                raise BuildError(f"{key}: figure key already exists")
            self.fig[key] = {
                "v": it["value"],
                "prov": "synthetic" if syn else "cited",
                "ref": cid,
                "label": it["label"],
                "period": it["period"],
                "unit": it["unit"],
                "raw": it["value"],
            }

    def register_gaps(self) -> None:
        for name, field, reason in NEW_GAPS:
            gid = self.new_id("G")
            self.gaps[gid] = {
                "id": gid,
                "field": field,
                "reason": reason,
                "origin": "build-fp-data.py",
            }
            self.gap_by_name[name] = gid
            if name in self.base["figures"] or name in self.fig:
                raise BuildError(f"{name}: figure key already exists")
            self.fig[name] = {
                "v": None,
                "prov": "gap",
                "ref": gid,
                "reason": reason,
                "label": field,
                "period": None,
                "unit": None,
                "raw": None,
            }

    def calc(
        self,
        key: str,
        label: str,
        period: str,
        value: Decimal,
        places: int,
        unit: str,
        formula: str,
        inputs: list[str],
        note: str | None = None,
        illustrative: bool = False,
        synthetic: bool = False,
    ) -> None:
        """Register a calculated figure. `formula` names inputs by key in {braces}."""
        if key in self.fig or key in self.base["figures"]:
            raise BuildError(f"{key}: figure key already exists")
        kid = self.new_id("K")
        shown = formula
        for k in sorted(inputs, key=len, reverse=True):
            f = self.figure(k)
            shown = shown.replace("{" + k + "}", f"{f['label']} [{f['ref']}]")
        text = fmt(value, places)
        rec = {
            "id": kid,
            "key": key,
            "label": label,
            "period": period,
            "value": text,
            "unit": unit,
            "formula": shown,
            "formula_keys": formula.replace("{", "").replace("}", ""),
            "inputs": list(dict.fromkeys(self.figure(k)["ref"] for k in inputs)),
            "note": note,
        }
        if illustrative:
            rec["illustrative"] = True
        if synthetic:
            rec["synthetic"] = True
        self.calcs[kid] = rec
        self.fig[key] = {
            "v": text,
            "raw": str(q(value, places)),
            "unit": unit,
            "label": label,
            "period": period,
            "prov": "illustrative" if illustrative else "calculated",
            "ref": kid,
        }


# ---------------------------------------------------------------- calculations (SPEC 3.2)
def calcs_earnings(c: Ctx) -> None:
    v = c.val
    P = "Q2 2026"

    def chg(key, label, a, b, period=P, places=0):
        c.calc(
            key,
            label,
            period,
            v(a) - v(b),
            places,
            "USD millions",
            f"{{{a}}} - {{{b}}}",
            [a, b],
        )

    def pct(key, label, a, b, period=P):
        c.calc(
            key,
            label,
            period,
            (v(a) - v(b)) / v(b) * 100,
            1,
            "%",
            f"({{{a}}} - {{{b}}}) / {{{b}}} x 100",
            [a, b],
        )

    chg(
        "eu_rev_chg_q2",
        "Change in net revenues, Q2 2026 on Q2 2025",
        "net_revenues_q2_2026",
        "net_revenues_q2_2025",
    )
    chg(
        "eu_ebitda_chg_q2",
        "Change in Adjusted EBITDA, Q2 2026 on Q2 2025",
        "adj_ebitda_q2_2026",
        "adj_ebitda_q2_2025",
    )
    pct(
        "eu_ebitda_pct_q2",
        "Change in Adjusted EBITDA, Q2 2026 on Q2 2025, %",
        "adj_ebitda_q2_2026",
        "adj_ebitda_q2_2025",
    )
    c.calc(
        "eu_margin_q2_2025",
        "Adjusted EBITDA margin, Q2 2025",
        "Q2 2025",
        v("adj_ebitda_q2_2025") / v("net_revenues_q2_2025") * 100,
        1,
        "%",
        "{adj_ebitda_q2_2025} / {net_revenues_q2_2025} x 100",
        ["adj_ebitda_q2_2025", "net_revenues_q2_2025"],
    )
    c.calc(
        "eu_margin_chg_pp",
        "Change in Adjusted EBITDA margin, Q2 2026 on Q2 2025",
        P,
        v("adj_ebitda_q2_2026") / v("net_revenues_q2_2026") * 100
        - v("adj_ebitda_q2_2025") / v("net_revenues_q2_2025") * 100,
        1,
        "pp",
        "{adj_ebitda_q2_2026} / {net_revenues_q2_2026} x 100 - {adj_ebitda_q2_2025} / {net_revenues_q2_2025} x 100",
        [
            "adj_ebitda_q2_2026",
            "net_revenues_q2_2026",
            "adj_ebitda_q2_2025",
            "net_revenues_q2_2025",
        ],
        note="Difference of the unrounded margins.",
    )
    chg(
        "eu_netloss_chg_q2",
        "Change in net loss attributable to Caesars, Q2 2026 on Q2 2025",
        "net_income_attrib_q2_2026",
        "net_income_attrib_q2_2025",
    )
    chg(
        "eu_int_chg_q2",
        "Change in interest expense, net, Q2 2026 on Q2 2025",
        "interest_expense_q2_2026",
        "interest_expense_q2_2025",
    )
    pct(
        "eu_int_pct_q2",
        "Change in interest expense, net, Q2 2026 on Q2 2025, %",
        "interest_expense_q2_2026",
        "interest_expense_q2_2025",
    )
    chg(
        "eu_da_chg_q2",
        "Change in depreciation and amortization, Q2 2026 on Q2 2025",
        "d_and_a_q2_2026",
        "d_and_a_q2_2025",
    )
    pct(
        "eu_da_pct_q2",
        "Change in depreciation and amortization, Q2 2026 on Q2 2025, %",
        "d_and_a_q2_2026",
        "d_and_a_q2_2025",
    )
    chg(
        "eu_capex_chg_q2",
        "Change in capital expenditures, net by segment, Q2 2026 on Q2 2025",
        "capex_net_segment_q2_2026",
        "capex_net_segment_q2_2025",
    )
    pct(
        "eu_capex_pct_q2",
        "Change in capital expenditures, net by segment, Q2 2026 on Q2 2025, %",
        "capex_net_segment_q2_2026",
        "capex_net_segment_q2_2025",
    )
    chg(
        "eu_cfo_chg_h1",
        "Change in cash from operations, H1 2026 on H1 2025",
        "cfo_h1_2026",
        "cfo_h1_2025",
        period="H1 2026",
    )
    pct(
        "eu_cfo_pct_h1",
        "Change in cash from operations, H1 2026 on H1 2025, %",
        "cfo_h1_2026",
        "cfo_h1_2025",
        period="H1 2026",
    )
    chg(
        "eu_netdebt_chg",
        "Change in net debt, 30 June 2026 on 31 December 2025",
        "net_debt_calc_2026_06_30",
        "net_debt_calc_2025_12_31",
        period="as of 2026-06-30",
    )
    c.calc(
        "eu_netlev_chg",
        "Change in net leverage, LTM Q2 2026 on FY2025",
        "LTM Q2 2026",
        v("net_leverage_ltm") - v("net_leverage_fy2025"),
        2,
        "x",
        "{net_leverage_ltm} - {net_leverage_fy2025}",
        ["net_leverage_ltm", "net_leverage_fy2025"],
        note="Difference of the two published two-decimal ratios.",
    )
    for s, name in SEGMENTS:
        pct(
            f"eu_seg_rev_pct_{s}",
            f"{name} net revenues, change Q2 2026 on Q2 2025, %",
            f"seg_rev_{s}_q2_2026",
            f"seg_rev_{s}_q2_2025",
        )
    for s, name in SEGMENTS:
        pct(
            f"eu_seg_ebitda_pct_{s}",
            f"{name} Adjusted EBITDA, change Q2 2026 on Q2 2025, %",
            f"seg_adj_ebitda_{s}_q2_2026",
            f"seg_adj_ebitda_{s}_q2_2025",
        )
    for s, name in SEGMENTS:
        for yr in ("2026", "2025"):
            e, r = f"seg_adj_ebitda_{s}_q2_{yr}", f"seg_rev_{s}_q2_{yr}"
            c.calc(
                f"eu_seg_margin_{s}_q2_{yr}",
                f"{name} Adjusted EBITDA margin, Q2 {yr}",
                f"Q2 {yr}",
                v(e) / v(r) * 100,
                1,
                "%",
                f"{{{e}}} / {{{r}}} x 100",
                [e, r],
            )
        e6, r6, e5, r5 = (
            f"seg_adj_ebitda_{s}_q2_2026",
            f"seg_rev_{s}_q2_2026",
            f"seg_adj_ebitda_{s}_q2_2025",
            f"seg_rev_{s}_q2_2025",
        )
        c.calc(
            f"eu_seg_margin_chg_{s}",
            f"{name} Adjusted EBITDA margin, change Q2 2026 on Q2 2025",
            P,
            v(e6) / v(r6) * 100 - v(e5) / v(r5) * 100,
            1,
            "pp",
            f"{{{e6}}} / {{{r6}}} x 100 - {{{e5}}} / {{{r5}}} x 100",
            [e6, r6, e5, r5],
            note="Difference of the unrounded margins.",
        )


def calcs_rv_dq(c: Ctx) -> None:
    v = c.val
    c.calc(
        "rv_yield_pickup",
        "Yield pickup, 6.00% unsecured 2032s over 6.50% secured 2032s",
        "2026-10-01",
        v("trace_czr_12769gad2_last_yield") - v("trace_czr_12769gac4_last_yield"),
        2,
        "pp",
        "{trace_czr_12769gad2_last_yield} - {trace_czr_12769gac4_last_yield}",
        ["trace_czr_12769gad2_last_yield", "trace_czr_12769gac4_last_yield"],
    )
    for p, name, cfo, eb in (
        ("fy2023", "FY2023", "cfo_fy2023", "adj_ebitda_fy2023"),
        ("fy2024", "FY2024", "cfo_fy2024", "adj_ebitda_fy2024"),
        ("fy2025", "FY2025", "cfo_fy2025", "adj_ebitda_fy2025"),
        ("h1_2025", "H1 2025", "cfo_h1_2025", "adj_ebitda_h1_2025"),
        ("h1_2026", "H1 2026", "cfo_h1_2026", "adj_ebitda_h1_2026"),
        ("ltm", "LTM Q2 2026", "ltm_cfo_q2_2026", "ltm_adj_ebitda_q2_2026"),
    ):
        c.calc(
            f"dq_conv_{p}",
            "Cash conversion (cash from operations / Adjusted EBITDA)",
            name,
            v(cfo) / v(eb) * 100,
            1,
            "%",
            f"{{{cfo}}} / {{{eb}}} x 100",
            [cfo, eb],
        )


def calcs_liquidity(c: Ctx) -> None:
    v = c.val
    mand = [
        "guide_remaining_2026_debt_service",
        "guide_2027_interest",
        "debt_maturity_2027",
        "guide_capex_remaining_2026_maintenance_high",
    ]
    c.calc(
        "cr_mand_uses",
        "Mandatory uses of cash, July 2026 to December 2027",
        "to 2027-12-31",
        sum((v(k) for k in mand), Decimal(0)),
        0,
        "USD millions",
        " + ".join(f"{{{k}}}" for k in mand),
        mand,
        note="Debt service for the rest of 2026, 2027 interest, 2027 maturities and the high end of the maintenance capex estimate.",
    )
    disc = ["guide_capex_remaining_2026_growth_high", "guide_capex_remaining_2026_digital_high"]
    c.calc(
        "cr_disc_uses",
        "Discretionary uses of cash, rest of 2026 (growth and digital capex, high end)",
        "H2 2026",
        sum((v(k) for k in disc), Decimal(0)),
        0,
        "USD millions",
        " + ".join(f"{{{k}}}" for k in disc),
        disc,
    )
    c.calc(
        "cr_closing",
        "Accessible liquidity at 31 December 2027 before operating cash flow",
        "to 2027-12-31",
        v("liq_total") - v("cr_mand_uses") - v("cr_disc_uses"),
        0,
        "USD millions",
        "{liq_total} - {cr_mand_uses} - {cr_disc_uses}",
        ["liq_total", "cr_mand_uses", "cr_disc_uses"],
    )
    c.calc(
        "cr_headroom",
        "Liquidity headroom over mandatory uses to 31 December 2027",
        "to 2027-12-31",
        v("liq_total") - v("cr_mand_uses"),
        0,
        "USD millions",
        "{liq_total} - {cr_mand_uses}",
        ["liq_total", "cr_mand_uses"],
    )
    c.calc(
        "cr_runway_months",
        "Months of runway on mandatory uses",
        "to 2027-12-31",
        v("liq_total") / (v("cr_mand_uses") / 18),
        1,
        "months",
        "{liq_total} / ({cr_mand_uses} / 18)",
        ["liq_total", "cr_mand_uses"],
        note="18 months: July 2026 to December 2027. Before any operating cash flow.",
    )
    c.calc(
        "cr_rcf_share",
        "CEI revolver capacity as a share of accessible liquidity",
        "as of 2026-06-30",
        v("liq_cei_rcf_net") / v("liq_total") * 100,
        1,
        "%",
        "{liq_cei_rcf_net} / {liq_total} x 100",
        ["liq_cei_rcf_net", "liq_total"],
    )
    mats = [
        ("2026", "debt_maturity_remaining_2026"),
        ("2027", "debt_maturity_2027"),
        ("2028", "debt_maturity_2028"),
        ("2029", "debt_maturity_2029"),
        ("2030", "debt_maturity_2030"),
        ("after", "debt_maturity_thereafter"),
    ]
    left: dict[str, Decimal] = {}
    for i, (tag, _) in enumerate(mats):
        used = [k for _, k in mats[: i + 1]]
        value = v("liq_total") - sum((v(k) for k in used), Decimal(0))
        ins = ["liq_total"] + used
        formula = "{liq_total} - " + " - ".join(f"{{{k}}}" for k in used)
        if tag in ("2028", "2029", "2030", "after"):
            value -= v("liq_cei_rcf_net")
            ins.append("liq_cei_rcf_net")
            formula += " - {liq_cei_rcf_net}"
        left[tag] = value
        label = "Liquidity left before refinancing, " + (
            "after 2030" if tag == "after" else f"end of {tag}"
        )
        c.calc(
            f"cr_liq_left_{tag}",
            label,
            f"to {tag}",
            value,
            0,
            "USD millions",
            formula,
            ins,
            note="Accessible liquidity less cumulative scheduled maturities, and less the CEI revolver's net capacity from "
            "2028, when it matures (31 January 2028). No operating cash flow, no refinancing.",
        )
    for tag in ("2028", "2029", "2030", "after"):
        c.calc(
            f"cr_gap_{tag}",
            "Funding gap, " + ("after 2030" if tag == "after" else f"by end of {tag}"),
            f"to {tag}",
            -left[tag],
            0,
            "USD millions",
            f"-{{cr_liq_left_{tag}}}",
            [f"cr_liq_left_{tag}"],
            note="The shortfall where liquidity left before refinancing is negative.",
        )
    c.calc(
        "cr_rcf_util_pct",
        "CEI revolver drawn as a share of commitments",
        "as of 2026-06-30",
        v("debt_cei_rcf_face_2026_06_30") / (v("cei_rcf_commitment") * 1000) * 100,
        1,
        "%",
        "{debt_cei_rcf_face_2026_06_30} / ({cei_rcf_commitment} x 1,000) x 100",
        ["debt_cei_rcf_face_2026_06_30", "cei_rcf_commitment"],
    )


def calcs_covenants(c: Ctx) -> None:
    v = c.val

    def head(key, label, a, b, unit="x", places=2, period="LTM Q2 2026"):
        c.calc(key, label, period, v(a) - v(b), places, unit, f"{{{a}}} - {{{b}}}", [a, b])

    head(
        "cov_tlr_headroom",
        "Total Leverage Ratio headroom (RBOT basis)",
        "cov_max_total_leverage",
        "net_leverage_ltm",
    )
    head(
        "cov_fccr_headroom",
        "Fixed Charge Coverage Ratio headroom (RBOT basis)",
        "cash_interest_cover_ltm",
        "cov_min_fccr",
    )
    head(
        "cov_sslr_headroom",
        "Pari secured incremental test headroom (RBOT basis, gross secured debt)",
        "cov_incr_pari_sslr",
        "senior_leverage_ltm",
    )
    head(
        "ind_fccr_headroom",
        "Indenture ratio-debt test headroom (RBOT basis)",
        "cash_interest_cover_ltm",
        "ind_ratio_debt_fccr",
    )
    e, sd = "ltm_adj_ebitda_q2_2026", "senior_secured_debt_2026_06_30"
    c.calc(
        "cap_pari_secured",
        "Indicative pari secured incremental capacity to 4.50x",
        "as of 2026-06-30",
        v("cov_incr_pari_sslr") * v(e) - v(sd),
        0,
        "USD millions",
        f"{{cov_incr_pari_sslr}} x {{{e}}} - {{{sd}}}",
        ["cov_incr_pari_sslr", e, sd],
        note="RBOT basis: company LTM Adjusted EBITDA and face senior secured debt; the agreement's EBITDA definition is not reconciled.",
    )
    c.calc(
        "cap_junior_secured",
        "Indicative junior secured incremental capacity to 4.75x",
        "as of 2026-06-30",
        v("cov_incr_junior_tslr") * v(e) - v(sd),
        0,
        "USD millions",
        f"{{cov_incr_junior_tslr}} x {{{e}}} - {{{sd}}}",
        ["cov_incr_junior_tslr", e, sd],
        note="An alternative to the pari amount, not additive. RBOT basis.",
    )
    c.calc(
        "cap_free_clear_size",
        "Free-and-clear incremental amount: the greater of US$2,600m and 1.00x EBITDA",
        "as of 2026-06-30",
        max(v("cov_incr_free_clear_floor"), Decimal("1.00") * v(e)),
        0,
        "USD millions",
        f"max({{cov_incr_free_clear_floor}}, 1.00 x {{{e}}})",
        ["cov_incr_free_clear_floor", e],
        note="Before amounts already used, which are not stated.",
    )
    c.calc(
        "lme_sec_lme",
        "Senior secured claims after drawing the pari secured capacity",
        "as of 2026-06-30",
        v(sd) + v("cap_pari_secured"),
        0,
        "USD millions",
        f"{{{sd}}} + {{cap_pari_secured}}",
        [sd, "cap_pari_secured"],
    )
    c.calc(
        "lme_uns_base",
        "Claims at or ahead of the senior unsecured notes, base",
        "as of 2026-06-30",
        v(sd) + v("unsecured_debt_2026_06_30"),
        0,
        "USD millions",
        f"{{{sd}}} + {{unsecured_debt_2026_06_30}}",
        [sd, "unsecured_debt_2026_06_30"],
    )
    c.calc(
        "lme_uns_lme",
        "Claims at or ahead of the senior unsecured notes after the pari secured capacity is drawn",
        "as of 2026-06-30",
        v("lme_uns_base") + v("cap_pari_secured"),
        0,
        "USD millions",
        "{lme_uns_base} + {cap_pari_secured}",
        ["lme_uns_base", "cap_pari_secured"],
    )


SCENARIOS = [
    ("merger", "Merger value", None),
    ("downside", "Downside", Decimal("5.0")),
    ("stress", "Stress", Decimal("4.0")),
]
CLASSES = [
    ("secured", "Senior secured", "senior_secured_debt_2026_06_30"),
    ("unsecured", "Senior unsecured", "unsecured_debt_2026_06_30"),
    ("other", "Other debt", "other_debt_2026_06_30"),
]


def calcs_distress(c: Ctx) -> None:
    v = c.val
    c.calc(
        "dr_ebitda_after_rent",
        "LTM Adjusted EBITDA after cash interest paid for rent (GLPI and VICI leases)",
        "LTM Q2 2026",
        v("ltm_adj_ebitda_q2_2026") - v("ltm_cash_interest_rent_q2_2026"),
        0,
        "USD millions",
        "{ltm_adj_ebitda_q2_2026} - {ltm_cash_interest_rent_q2_2026}",
        ["ltm_adj_ebitda_q2_2026", "ltm_cash_interest_rent_q2_2026"],
        note="Rent is treated as a claim ahead of debt, so value is measured after it.",
    )
    c.calc(
        "dr_merger_multiple",
        "Merger transaction value over LTM Adjusted EBITDA after rent",
        "LTM Q2 2026",
        v("ev_merger_usdm") / v("dr_ebitda_after_rent"),
        2,
        "x",
        "{ev_merger_usdm} / {dr_ebitda_after_rent}",
        ["ev_merger_usdm", "dr_ebitda_after_rent"],
    )
    for tag, name, mult in SCENARIOS[1:]:
        c.calc(
            f"dr_ev_{tag}",
            f"Enterprise value, {name.lower()} scenario at an illustrative {mult}x",
            "LTM Q2 2026",
            mult * v("dr_ebitda_after_rent"),
            0,
            "USD millions",
            f"{mult} (illustrative multiple) x " + "{dr_ebitda_after_rent}",
            ["dr_ebitda_after_rent"],
            note=f"The {mult}x multiple is an illustrative analyst input, not a sourced figure.",
            illustrative=True,
        )
    for tag, name, mult in SCENARIOS:
        ill = mult is not None
        ev = "ev_merger_usdm" if tag == "merger" else f"dr_ev_{tag}"
        avail = ev
        for cls, cname, claim in CLASSES:
            if cls != "secured":
                prev = CLASSES[[x[0] for x in CLASSES].index(cls) - 1][0]
                avail_key = f"dr_avail_{tag}_{cls}"
                c.calc(
                    avail_key,
                    f"Value left for {cname.lower()} after the class ahead, {name.lower()} scenario",
                    "LTM Q2 2026",
                    v(avail) - v(f"dr_alloc_{tag}_{prev}"),
                    0,
                    "USD millions",
                    f"{{{avail}}} - {{dr_alloc_{tag}_{prev}}}",
                    [avail, f"dr_alloc_{tag}_{prev}"],
                    illustrative=ill,
                )
                avail = avail_key
            c.calc(
                f"dr_alloc_{tag}_{cls}",
                f"Allocation to {cname.lower()}, {name.lower()} scenario (absolute priority)",
                "LTM Q2 2026",
                min(v(claim), v(avail)),
                0,
                "USD millions",
                f"min({{{claim}}}, {{{avail}}})",
                [claim, avail],
                illustrative=ill,
            )
            c.calc(
                f"dr_rec_{tag}_{cls}",
                f"Recovery of {cname.lower()}, {name.lower()} scenario",
                "LTM Q2 2026",
                v(f"dr_alloc_{tag}_{cls}") / v(claim) * 100,
                1,
                "%",
                f"{{dr_alloc_{tag}_{cls}}} / {{{claim}}} x 100",
                [f"dr_alloc_{tag}_{cls}", claim],
                illustrative=ill,
            )
        c.calc(
            f"dr_residual_{tag}",
            f"Residual value to equity, {name.lower()} scenario",
            "LTM Q2 2026",
            v(ev) - sum((v(f"dr_alloc_{tag}_{cls}") for cls, _, _ in CLASSES), Decimal(0)),
            0,
            "USD millions",
            f"{{{ev}}} - " + " - ".join(f"{{dr_alloc_{tag}_{cls}}}" for cls, _, _ in CLASSES),
            [ev] + [f"dr_alloc_{tag}_{cls}" for cls, _, _ in CLASSES],
            illustrative=ill,
        )


def parse_pct(excerpt: str, label: str, key: str) -> Decimal:
    m = re.search(label + r"\s*([0-9.]+)%", excerpt)
    if not m:
        raise BuildError(f"{key}: cannot read '{label}' from the synthetic row")
    return Decimal(m.group(1))


LOCAL_KEY = {
    "c01": "clo_c01_limit_pct",
    "c04": "clo_c04_headroom_pct",
    "c05": "clo_c05_headroom_pct",
    "c10": "clo_c10_headroom_pct",
    "c06": "clo_c06_limit_pct",
    "sector": "clo_leisure_weight_pct",
}


def calcs_fit(c: Ctx) -> None:
    """Portfolio Fit arithmetic (interfaces spec 7). Inputs are synthetic rows; results are calculated figures
    flagged synthetic in the calculation record, as K107 to K109 are."""
    base = c.base["citations"]
    nav_m = re.search(r"\$([0-9,]+)", base["S18"]["excerpt"])
    if not nav_m:
        raise BuildError("S18: NAV not readable")
    c.local["clo_nav"] = {
        "v": nav_m.group(1),
        "raw": nav_m.group(1).replace(",", ""),
        "unit": "USD",
        "label": "Test CLO I total NAV",
        "period": "29-May-2026",
        "prov": "synthetic",
        "ref": "S18",
    }
    rows = {
        "c01": ("S1", "C-01 single-issuer limit"),
        "c04": ("S4", "C-04 CCC bucket headroom"),
        "c05": ("S5", "C-05 unrated headroom"),
        "c10": ("S10", "C-10 second lien and unsecured headroom"),
        "c06": ("S6", "C-06 single-sector limit"),
        "sector": ("S32", "Leisure Facilities & Services sector weight"),
    }
    for tag, (sid, label) in rows.items():
        c.local[LOCAL_KEY[tag]] = {
            "v": None,
            "raw": None,
            "unit": "% NAV",
            "label": label,
            "period": "29-May-2026",
            "prov": "synthetic",
            "ref": sid,
        }
    nav = c.val("clo_nav")

    def exc(sid: str) -> str:
        return base[sid]["excerpt"]

    existing = c.figure("clo_czr_existing")
    if "none" not in existing["raw"]:
        raise BuildError("clo_czr_existing: expected 'none'")
    for tag, expect in (
        ("c01", "Hard"),
        ("c04", "Hard"),
        ("c05", "Soft"),
        ("c10", "Soft"),
        ("c06", "Soft"),
    ):
        m = re.search(r"Breach Type: (Hard|Soft)", exc(rows[tag][0]))
        if not m or m.group(1) != expect:
            raise BuildError(f"{rows[tag][0]}: expected breach type {expect}")
    c01_limit = parse_pct(exc("S1"), r"Limit: ≤", "S1")
    c.calc(
        "fit_one_pct_nav",
        "1% of Test CLO I NAV",
        "29-May-2026",
        nav / 100,
        0,
        "USD",
        "1% x {clo_nav}",
        ["clo_nav"],
        note="Synthetic portfolio data. The Watch threshold for a maximum size (interfaces spec 7, rule 4).",
        synthetic=True,
    )
    c.local["clo_c01_limit_pct"].update({"v": str(c01_limit), "raw": str(c01_limit)})
    c.calc(
        "fit_c01_headroom_pct",
        "Single-issuer headroom for Caesars: C-01 limit less existing Caesars exposure (none)",
        "29-May-2026",
        c01_limit - 0,
        2,
        "% NAV",
        "{clo_c01_limit_pct} - 0 (existing Caesars exposure: none; see {clo_czr_existing})",
        ["clo_c01_limit_pct", "clo_czr_existing"],
        note="Synthetic portfolio data. Uses Caesars' own exposure (none), not the largest name's (Asurion).",
        synthetic=True,
    )
    c.calc(
        "fit_c01_room",
        "Room under C-01 (Hard): (2.5 - 0)% x NAV",
        "29-May-2026",
        c.val("fit_c01_headroom_pct") / 100 * nav,
        0,
        "USD",
        "{fit_c01_headroom_pct}% x {clo_nav}",
        ["fit_c01_headroom_pct", "clo_nav"],
        synthetic=True,
    )
    for tag, kind, label in (("c04", "Hard", "C-04 CCC bucket"), ("c05", "Soft", "C-05 unrated")):
        hp = parse_pct(exc(rows[tag][0]), "Headroom:", rows[tag][0])
        c.local[LOCAL_KEY[tag]].update({"v": str(hp), "raw": str(hp)})
        c.calc(
            f"fit_{tag}_room",
            f"Room under {label} ({kind}): headroom x NAV",
            "29-May-2026",
            hp / 100 * nav,
            0,
            "USD",
            f"{{{LOCAL_KEY[tag]}}}% x {{clo_nav}}",
            [LOCAL_KEY[tag], "clo_nav"],
            synthetic=True,
        )
    leis = parse_pct(exc("S32"), r"Leisure Facilities & Services", "S32")
    c06_limit = parse_pct(exc("S6"), r"Limit: ≤", "S6")
    c.local["clo_leisure_weight_pct"].update({"v": str(leis), "raw": str(leis)})
    c.local["clo_c06_limit_pct"].update({"v": str(c06_limit), "raw": str(c06_limit)})
    c.calc(
        "fit_sector_headroom_pct",
        "Leisure Facilities & Services sector headroom: single-sector limit less current weight",
        "29-May-2026",
        c06_limit - leis,
        2,
        "% NAV",
        "{clo_c06_limit_pct} - {clo_leisure_weight_pct}",
        ["clo_c06_limit_pct", "clo_leisure_weight_pct"],
        note="Synthetic portfolio data.",
        synthetic=True,
    )
    c.calc(
        "fit_sector_room",
        "Room under the Leisure Facilities & Services sector limit (Soft): headroom x NAV",
        "29-May-2026",
        c.val("fit_sector_headroom_pct") / 100 * nav,
        0,
        "USD",
        "{fit_sector_headroom_pct}% x {clo_nav}",
        ["fit_sector_headroom_pct", "clo_nav"],
        synthetic=True,
    )
    hp10 = parse_pct(exc("S10"), "Headroom:", "S10")
    c.local["clo_c10_headroom_pct"].update({"v": str(hp10), "raw": str(hp10)})
    c.calc(
        "fit_c10_room",
        "Room under C-10 second lien and unsecured (Soft): headroom x NAV",
        "29-May-2026",
        hp10 / 100 * nav,
        0,
        "USD",
        "{clo_c10_headroom_pct}% x {clo_nav}",
        ["clo_c10_headroom_pct", "clo_nav"],
        synthetic=True,
    )


# ---------------------------------------------------------------- cell helpers
def scale_word(name: str, word: str, illustrative: bool = True) -> dict:
    order = SCALES[name]
    if word == "Unknown" and name == "ordinal":
        pos = 0
    elif word in order:
        pos = order.index(word) + 1
    else:
        raise BuildError(f"{word!r} is not a word of scale {name}")
    return {
        "scale": "word",
        "scaleName": name,
        "word": word,
        "steps": len(order),
        "pos": pos,
        "illustrative": illustrative,
    }


def five_point(n: int) -> dict:
    return {
        "scale": "word",
        "scaleName": "five_point",
        "word": f"{n} of 5",
        "steps": 5,
        "pos": n,
        "illustrative": True,
    }


def rec_cell(pos: int | None, word: str) -> dict:
    return {"scale": "rec", "pos": pos, "word": word, "illustrative": True}


def status_cell(word: str, illustrative: bool = False) -> dict:
    return {"status": word, "illustrative": illustrative} if illustrative else {"status": word}


def neg(d: dict) -> dict:
    """The same Datum shown as a use of cash or a deduction: the value in parentheses."""
    out = dict(d)
    s = str(d["v"])
    if d.get("v") is not None and not s.startswith("("):
        out["v"] = f"({s})"
    return out


def col(key, label, unit=None, num=False, summary=None):
    out = {"key": key, "label": label}
    if unit:
        out["unit"] = unit
    if num:
        out["num"] = True
    if summary is not None:
        out["summary"] = summary
    return out


def table(
    owner,
    title,
    columns,
    rows,
    unit=None,
    note=None,
    illustrative=False,
    model=False,
    synthetic=False,
):
    t = {"title": title, "owner": owner, "columns": columns, "rows": rows}
    if unit:
        t["unit"] = unit
    if note:
        t["note"] = note
    if illustrative:
        t["illustrative"] = True
    if model:
        t["model"] = True
    if synthetic:
        t["synthetic"] = True
    return t


# ---------------------------------------------------------------- Portfolio Fit
INSTRUMENTS = [
    # key, short name, facility name in D.illustrative.byInstrument, issue-rating prefix, secured
    ("tlb", "Term Loan B", "CEI Term Loan B", None, True),
    ("tlb1", "Term Loan B-1", "CEI Term Loan B-1", None, True),
    ("ssn_2030", "7.00% SSN 2030", "CEI 7.00% Senior Secured Notes 2030", None, True),
    (
        "ssn_2032",
        "6.50% SSN 2032",
        "CEI 6.50% Senior Secured Notes 2032",
        "trace_czr_12769gac4",
        True,
    ),
    ("sn_2029", "4.625% SN 2029", "CEI 4.625% Senior Notes 2029", None, False),
    ("sn_2032", "6.00% SN 2032", "CEI 6.00% Senior Notes 2032", "trace_czr_12769gad2", False),
]
NOT_EVALUATED = [
    "CEI Revolving Credit Facility",
    "CEI Term Loan A",
    "CVA Delayed Draw Term Loan",
    "Special Improvement District Bonds 4.30%",
    "Long-term notes and other payables",
]


def build_fit(c: Ctx) -> dict:
    d = c.base
    one_pct = c.val("fit_one_pct_nav")
    byi = {x["facility"]: x for x in d["illustrative"]["byInstrument"]}
    limits = {
        "C-01": {
            "id": "C-01",
            "label": "Single issuer (Caesars' own exposure)",
            "kind": "Hard",
            "scope": "issuer",
            "limit": {"v": "2.5", "prov": "synthetic", "ref": "S1", "unit": "% NAV"},
            "current": {
                "v": "0",
                "prov": "synthetic",
                "ref": c.ref("clo_czr_existing"),
                "unit": "% NAV",
            },
            "headroomPct": c.dv("fit_c01_headroom_pct"),
            "room": c.dv("fit_c01_room"),
        },
        "C-04": {
            "id": "C-04",
            "label": "CCC bucket (CCC+ and below, incl. unrated and other)",
            "kind": "Hard",
            "scope": "rating_bucket",
            "limit": {"v": "7.5", "prov": "synthetic", "ref": "S4", "unit": "% NAV"},
            "current": {"v": "7.36", "prov": "synthetic", "ref": "S4", "unit": "% NAV"},
            "headroomPct": {"v": "0.14", "prov": "synthetic", "ref": "S4", "unit": "% NAV"},
            "room": c.dv("fit_c04_room"),
        },
        "C-05": {
            "id": "C-05",
            "label": "Unrated exposure",
            "kind": "Soft",
            "scope": "rating_bucket",
            "limit": {"v": "5.0", "prov": "synthetic", "ref": "S5", "unit": "% NAV"},
            "current": {"v": "3.73", "prov": "synthetic", "ref": "S5", "unit": "% NAV"},
            "headroomPct": {"v": "1.27", "prov": "synthetic", "ref": "S5", "unit": "% NAV"},
            "room": c.dv("fit_c05_room"),
        },
        "C-10": {
            "id": "C-10",
            "label": "Second lien and unsecured",
            "kind": "Soft",
            "scope": "seniority",
            "limit": {"v": "10.0", "prov": "synthetic", "ref": "S10", "unit": "% NAV"},
            "current": {"v": "0.61", "prov": "synthetic", "ref": "S10", "unit": "% NAV"},
            "headroomPct": {"v": "9.39", "prov": "synthetic", "ref": "S10", "unit": "% NAV"},
            "room": c.dv("fit_c10_room"),
        },
        "SECTOR": {
            "id": "SECTOR",
            "label": "Leisure Facilities & Services sector (single-sector limit)",
            "kind": "Soft",
            "scope": "sector",
            "limit": {"v": "10.0", "prov": "synthetic", "ref": "S6", "unit": "% NAV"},
            "current": {"v": "4.57", "prov": "synthetic", "ref": "S32", "unit": "% NAV"},
            "headroomPct": c.dv("fit_sector_headroom_pct"),
            "room": c.dv("fit_sector_room"),
        },
    }
    # the limit/current/headroom strings in `limits` come from the synthetic rows; check them
    for lid, tag in (
        ("C-04", LOCAL_KEY["c04"]),
        ("C-05", LOCAL_KEY["c05"]),
        ("C-10", LOCAL_KEY["c10"]),
    ):
        if limits[lid]["headroomPct"]["v"] != c.figure(tag)["v"]:
            raise BuildError(f"{lid}: headroom string differs from the synthetic row")
    if limits["C-01"]["limit"]["v"] != c.figure(LOCAL_KEY["c01"])["v"]:
        raise BuildError("C-01: limit string differs from the synthetic row")
    if limits["SECTOR"]["current"]["v"] != c.figure(LOCAL_KEY["sector"])["v"]:
        raise BuildError("sector: current weight differs from the synthetic row")
    insts = []
    for key, short, facility, trace, secured in INSTRUMENTS:
        if trace:
            moodys, sp = c.figure(f"{trace}_moodys")["raw"], c.figure(f"{trace}_sp")["raw"]
            rating = {
                "rated": True,
                "moodys": c.dv(f"{trace}_moodys"),
                "sp": c.dv(f"{trace}_sp"),
            }
            ccc = moodys.startswith("Caa") or sp.startswith("CCC")
        else:
            rating = {
                "rated": False,
                "moodys": c.gd("issue_ratings_other"),
                "sp": c.gd("issue_ratings_other"),
            }
            ccc = True  # Unrated: counts in the CCC bucket (C-04) and the unrated limit (C-05)
        touched = ["C-01"]
        if ccc:
            touched += ["C-04", "C-05"]
        if not secured:
            touched.append("C-10")
        touched.append("SECTOR")
        hard = [t for t in touched if limits[t]["kind"] == "Hard"]
        rooms = {t: dec(limits[t]["room"]["v"]) for t in touched}
        binding = min(hard, key=lambda t: rooms[t])
        max_size = max(rooms[binding], Decimal(0))
        soft_breach = any(
            dec(limits[t]["headroomPct"]["v"]) < 0 for t in touched if limits[t]["kind"] == "Soft"
        )
        hard_breach = any(dec(limits[t]["headroomPct"]["v"]) < 0 for t in hard) or max_size == 0
        if hard_breach:
            verdict, cap = "Breaches", "Avoid"
        elif soft_breach or max_size < one_pct:
            verdict, cap = "Watch", "3 - MW"
        else:
            verdict, cap = "Fits", None
        unc = byi[facility]
        if unc["pos"] is None:
            raise BuildError(f"{facility}: no uncapped Recommendation")
        if cap == "Avoid":
            final = {"pos": None, "word": "Avoid"}
        elif cap == "3 - MW":
            fp = max(unc["pos"], 3)
            final = {"pos": fp, "word": REC_WORDS[fp]}
        else:
            final = {"pos": unc["pos"], "word": unc["word"]}
        insts.append(
            {
                "key": key,
                "instrument": short,
                "facility": facility,
                "secured": secured,
                "issueRating": rating,
                "touches": touched,
                "maxSize": limits[binding]["room"],
                "bindingLimit": binding,
                "verdict": verdict,
                "cap": cap,
                "uncapped": {"pos": unc["pos"], "word": unc["word"], "illustrative": True},
                "final": {**final, "illustrative": True},
                "note": None
                if trace
                else c.T(
                    "No issue rating is in the sources, so it counts as Unrated [gap:issue_ratings_other]."
                ),
            }
        )
    proposed = next(i for i in insts if i["key"] == "ssn_2032")
    par = c.dv("clo_proposed_par")
    fits = dec(par["v"]) <= dec(proposed["maxSize"]["v"])
    return {
        "synthetic": True,
        "illustrative": True,
        "portfolio": {
            "name": "Test CLO I Ltd",
            "asOf": "29-May-2026",
            "nav": {
                "v": c.figure("clo_nav")["v"],
                "prov": "synthetic",
                "ref": "S18",
                "unit": "US$",
            },
            "onePctNav": c.dv("fit_one_pct_nav"),
            "existingCaesarsExposure": c.dv("clo_czr_existing"),
            "asOfMismatch": c.dv("clo_asof_mismatch"),
            "indentureNote": c.dv("clo_indenture_note"),
        },
        "limits": [limits[k] for k in ("C-01", "C-04", "C-05", "C-10", "SECTOR")],
        "instruments": insts,
        "notEvaluated": [
            {"facility": f, "text": "Not evaluated: bank or other facility"} for f in NOT_EVALUATED
        ],
        "proposed": {
            "instrument": "6.50% SSN 2032",
            "par": par,
            "weightOnPar": c.dv("clo_proposed_weight_par"),
            "marketValue": c.dv("clo_proposed_mv"),
            "price": c.dv("trace_czr_12769gac4_last_price"),
            "maxSize": proposed["maxSize"],
            "bindingLimit": proposed["bindingLimit"],
            "verdict": proposed["verdict"],
            "withinMaxSize": fits,
            "note": c.T(
                "The workbook NAV and compliance check are dated 29 May 2026; the price is dated 1 October 2026 "
                "[clo_asof_mismatch]. The CLO's Indenture 7.11 is its own indenture, not the Caesars notes "
                "indenture [clo_indenture_note]."
            ),
        },
        "rule": "Interfaces spec 7: max_size is the smallest Hard room; Watch when max_size is under 1% of NAV or a "
        "Soft limit is breached; Watch caps the Recommendation at 3 - MW, Breaches at Avoid; final is the weaker of "
        "the illustrative uncapped Recommendation and the cap.",
    }


# ---------------------------------------------------------------- modules (SPEC 3.3)
MODULE_DEFS = [
    (
        "CP-0",
        "Source readiness",
        "Restricted",
        "Ratings outlooks, Fitch, issue ratings beyond the two 2032 notes and the merger's debt terms are missing from the Source Pack.",
        ["G10", "G11", "gap:issue_ratings_other", "G8"],
        "The Source Pack answers every Pathway's question except one input that moves them all: the merger's new debt [G8].",
    ),
    (
        "CP-1",
        "Financials and debt",
        "Pass",
        "Historical financials, the debt table and liquidity reconcile to the filings.",
        [],
        "Total debt {total_debt_check_2026_06_30|US$ m} against LTM Adjusted EBITDA {ltm_adj_ebitda_q2_2026|US$ m}: "
        "total leverage {total_leverage_ltm|x}, before any merger debt.",
    ),
    (
        "CP-1A",
        "Business and events",
        "Restricted",
        "No issuer or corporate family rating and no outlooks; merger debt terms unstated.",
        ["G25", "G11", "G8"],
        "Fertitta's take-private at about US$17.6bn [merger_transaction_value] assumes Caesars' debt and adds new "
        "committed debt of unstated size [G8].",
    ),
    (
        "CP-1B",
        "Earnings delta",
        "Restricted",
        "Quarterly cash flows, cash interest and cash taxes are disclosed for six months only.",
        ["G3", "G1", "G2"],
        "Q2 2026 net revenues rose {czr_rev_growth_q2_2026|%} but Adjusted EBITDA fell {eu_ebitda_pct_q2|%}: Regional "
        "grew with Caesars Windsor consolidated, while Las Vegas and Digital margins fell.",
    ),
    (
        "CP-1C",
        "Peer benchmark",
        "Restricted",
        "Two peers only (MGM, PENN); their EBITDAR definitions differ.",
        ["G14"],
        "Caesars' Q2 margin {czr_ebitda_margin_q2_2026|%} sits above MGM's {K69|%} and PENN's {K70|%}, on company "
        "definitions that differ [G14].",
    ),
    (
        "CP-1D",
        "Earnings quality",
        "Restricted",
        "No unrealized add-backs are marketed; cash conversion is six-monthly only.",
        ["G22", "G3"],
        "Q2 add-backs take Reported EBITDA {reported_ebitda_q2_2026|US$ m} to {structuring_ebitda_q2_2026|US$ m}; the "
        "GLPI and VICI leases of {lt_financing_obligations_2026_06_30|US$ m} are the debt-like item that matters.",
    ),
    (
        "CP-2",
        "Credit synthesis",
        "Restricted",
        "The merger's new debt is unstated, so the post-close credit profile is open.",
        ["G8"],
        "Fair today at {net_leverage_ltm|x} net leverage and {interest_cover_ltm|x} lease-inclusive cover; the "
        "direction turns on debt not yet disclosed [G8].",
    ),
    (
        "CP-2A",
        "Downside paths",
        "Restricted",
        "Downside paths cannot size the merger's new debt.",
        ["G8"],
        "The first break is a layered take-private: pari secured capacity of {cap_pari_secured|US$ m} under the 4.50x "
        "test would rank ahead of the unsecured notes.",
    ),
    (
        "CP-2D",
        "Liquidity bridge",
        "Restricted",
        "No operating cash flow forecast (no guidance) and no 2027 capex estimate.",
        ["G13", "gap:capex_2027"],
        "Liquidity of {liq_total|US$ m} covers mandatory uses to December 2027 of {cr_mand_uses|US$ m}: "
        "{cr_runway_months} months of runway before any operating cash flow.",
    ),
    (
        "CP-2G",
        "Forecast cases",
        "Restricted",
        "No company guidance and no forward rate deck in the pack.",
        ["G13", "gap:rate_deck"],
        None,
    ),
    (
        "CP-2H",
        "Rating triggers",
        "Restricted",
        "Agency reports and their trigger thresholds are not in the pack.",
        ["gap:agency_triggers", "G11"],
        "The unsecured 2032s are rated {trace_czr_12769gad2_moodys} by Moody's (rated 28 September 2026); no agency "
        "threshold is in the sources [gap:agency_triggers].",
    ),
    (
        "CP-3",
        "Relative value",
        "Restricted",
        "TRACE gives yields, not spreads; no loan prices.",
        ["G19", "G18"],
        "The secured 2032s at {trace_czr_12769gac4_last_price} yield {trace_czr_12769gac4_last_yield|%}; the unsecured "
        "2032s at {trace_czr_12769gad2_last_price} yield {trace_czr_12769gad2_last_yield|%}, {rv_yield_pickup|pp} more "
        "for a junior claim.",
    ),
    (
        "CP-3C",
        "Refinancing and LME",
        "Restricted",
        "Restricted payment and investment baskets were not extracted; merger tranches unstated.",
        ["gap:rp_capacity", "G8"],
        "The pinch point is 31 January 2028, when the CEI revolver and its {liq_cei_rcf_net|US$ m} of capacity mature; "
        "liquidity left before refinancing turns negative that year.",
    ),
    (
        "CP-3D",
        "Market-implied risk",
        "Restricted",
        "No spreads or risk-free curve, so implied default is not computable.",
        ["G19", "gap:implied_pd"],
        "The market prices the unsecured 2032s {rv_yield_pickup|pp} over the secured 2032s; implied default is not "
        "computable [gap:implied_pd].",
    ),
    (
        "CP-4",
        "Covenants and legal",
        "Restricted",
        "Agreement definitions are not reconciled to company figures; RP and investment baskets not extracted.",
        ["gap:covenant_basis", "gap:rp_capacity"],
        "Maintenance tests protect only the revolver and Term A: total leverage {net_leverage_ltm|x} against "
        "{cov_max_total_leverage|x}, and Term B-1 is a Non-Covenant Facility.",
    ),
    (
        "CP-4C",
        "Recovery and fulcrum",
        "Restricted",
        "Scenario multiples are illustrative; lease claims are not modelled.",
        ["gap:lease_claims"],
        "At the illustrative 5.0x downside the unsecured notes are the fulcrum, recovering "
        "{dr_rec_downside_unsecured|%}; at the merger value every class recovers in full.",
    ),
    (
        "CP-5",
        "Evidence checks",
        "Pass",
        "Every cited figure resolves to a file, line and excerpt.",
        [],
        None,
    ),
    (
        "CP-6",
        "Challenge and decision",
        "Restricted",
        "Recommendations rest on illustrative judgement; the merger's debt is unstated.",
        ["G8"],
        None,
    ),
]


def build_modules(c: Ctx, nav_ids: set[str]) -> dict:
    out = {}
    for mid, name, status, reason, refs, headline in MODULE_DEFS:
        if mid in nav_ids and len(name) > 20:
            raise BuildError(f"{mid}: name {name!r} is longer than 20 characters")
        rr = [c.gap_id(r[4:] if r.startswith("gap:") else r) for r in refs]
        rec = {
            "id": mid,
            "name": name,
            "status": status,
            "reason": reason,
            "refs": rr,
            "question": QUESTIONS[mid],
            "headline": None,
        }
        if headline:
            h = c.T(headline, model=True)
            rec["headline"] = h
        out[mid] = rec
    out["CP-2G"]["headlineNote"] = (
        "No headline: the module view says Base and Downside need assumptions the pack cannot cite."
    )
    return out


# ---------------------------------------------------------------- block tables (SPEC 3.5)
def build_blocks(c: Ctx, fit: dict) -> dict:
    B: dict[str, dict] = {}
    T = c.T
    dv = c.dv
    gd = c.gd
    D = c.base
    ill = D["illustrative"]
    NS = GAP_NOT_SHOWN

    def quote(key: str) -> dict:
        ex = next(i["excerpt"] for i in c.extract["items"] if i["key"] == key)
        return T("“" + ex + "” [" + key + "]")

    # --- CP-1B ---------------------------------------------------------------
    def pc(
        metric,
        ref,
        cur,
        chg,
        pctk,
        basis,
        perim="Not stated",
        summary=True,
        note=None,
        pct_reason=None,
    ):
        row = {
            "metric": metric,
            "reference": dv(ref),
            "current": dv(cur),
            "change": dv(chg),
            "changePct": dv(pctk) if pctk else gd(NS, pct_reason),
            "basis": basis,
            "restatement": "Not stated",
            "perimeter": T(perim) if "[" in perim or "{" in perim else perim,
        }
        if not summary:
            row["summary"] = False
        if note:
            row["note"] = T(note)
        return row

    windsor = "Yes: Caesars Windsor consolidated from 3 March 2026 [mgmt_driver_regional]"
    rows = [
        pc(
            "Net revenues, Q2",
            "net_revenues_q2_2025",
            "net_revenues_q2_2026",
            "eu_rev_chg_q2",
            "czr_rev_growth_q2_2026",
            "YoY",
            windsor,
        ),
        pc(
            "Adjusted EBITDA, Q2",
            "adj_ebitda_q2_2025",
            "adj_ebitda_q2_2026",
            "eu_ebitda_chg_q2",
            "eu_ebitda_pct_q2",
            "YoY",
            "Yes",
        ),
        pc(
            "Adjusted EBITDA margin, Q2 (%)",
            "eu_margin_q2_2025",
            "czr_ebitda_margin_q2_2026",
            "eu_margin_chg_pp",
            None,
            "YoY",
            pct_reason="not meaningful: the line is itself a percentage; its change is shown in percentage points",
        ),
        pc(
            "Net loss attributable to Caesars, Q2",
            "net_income_attrib_q2_2025",
            "net_income_attrib_q2_2026",
            "eu_netloss_chg_q2",
            None,
            "YoY",
            summary=False,
            pct_reason="not meaningful: the base is negative",
        ),
        pc(
            "Interest expense, net, Q2",
            "interest_expense_q2_2025",
            "interest_expense_q2_2026",
            "eu_int_chg_q2",
            "eu_int_pct_q2",
            "YoY",
        ),
        pc(
            "Depreciation and amortization, Q2",
            "d_and_a_q2_2025",
            "d_and_a_q2_2026",
            "eu_da_chg_q2",
            "eu_da_pct_q2",
            "YoY",
            summary=False,
        ),
        pc(
            "Capital expenditures, net by segment, Q2",
            "capex_net_segment_q2_2025",
            "capex_net_segment_q2_2026",
            "eu_capex_chg_q2",
            "eu_capex_pct_q2",
            "YoY",
            summary=False,
        ),
        pc(
            "Cash from operations, six months (H1)",
            "cfo_h1_2025",
            "cfo_h1_2026",
            "eu_cfo_chg_h1",
            "eu_cfo_pct_h1",
            "YoY",
            summary=False,
            note="Six months: quarterly cash flows are not disclosed [G3].",
        ),
        pc(
            "Net debt (31 Dec 2025 to 30 Jun 2026)",
            "net_debt_calc_2025_12_31",
            "net_debt_calc_2026_06_30",
            "eu_netdebt_chg",
            None,
            "LTM vs FY",
            pct_reason="not shown: the comparison is of the level and its change in US$ m",
        ),
        pc(
            "Net leverage (FY2025 to LTM Q2 2026) (x)",
            "net_leverage_fy2025",
            "net_leverage_ltm",
            "eu_netlev_chg",
            None,
            "LTM vs FY",
            pct_reason="not meaningful: the line is itself a ratio; its change is shown in turns",
        ),
    ]
    B["periodComparison"] = table(
        "CP-1B",
        "Period comparison",
        [
            col("metric", "Metric", summary=True),
            col("reference", "Reference", num=True, summary=True),
            col("current", "Current", num=True, summary=True),
            col("change", "Change", num=True, summary=True),
            col("changePct", "Change", unit="%", num=True, summary=True),
            col("basis", "Basis", summary=False),
            col("restatement", "Restatement", summary=False),
            col("perimeter", "Perimeter change", summary=False),
        ],
        rows,
        unit="US$ m unless stated",
        note="Q2 2026 against Q2 2025, except where the metric names another period. Change in percentage points for margins and turns for ratios.",
    )

    segrows = []
    for s, name in SEGMENTS:
        segrows.append(
            {
                "segment": name,
                "rev25": dv(f"seg_rev_{s}_q2_2025"),
                "rev26": dv(f"seg_rev_{s}_q2_2026"),
                "revPct": dv(f"eu_seg_rev_pct_{s}"),
                "ebitda25": dv(f"seg_adj_ebitda_{s}_q2_2025"),
                "ebitda26": dv(f"seg_adj_ebitda_{s}_q2_2026"),
                "ebitdaPct": dv(f"eu_seg_ebitda_pct_{s}"),
                "margin26": dv(f"eu_seg_margin_{s}_q2_2026"),
                "marginChg": dv(f"eu_seg_margin_chg_{s}"),
            }
        )
    sign = "not meaningful: the sign changes"
    segrows.append(
        {
            "segment": "Corporate and Other",
            "rev25": dv("seg_rev_corporate_other_q2_2025"),
            "rev26": dv("seg_rev_corporate_other_q2_2026"),
            "revPct": gd(NS, sign),
            "ebitda25": dv("seg_adj_ebitda_corporate_other_q2_2025"),
            "ebitda26": dv("seg_adj_ebitda_corporate_other_q2_2026"),
            "ebitdaPct": gd(NS, sign),
            "margin26": gd(NS, "not meaningful: Corporate and Other has no operating margin"),
            "marginChg": gd(NS, "not meaningful: Corporate and Other has no operating margin"),
            "kind": "sub",
        }
    )
    B["segmentChanges"] = table(
        "CP-1B",
        "Segment changes",
        [
            col("segment", "Segment"),
            col("rev25", "Net revenues Q2 2025", num=True),
            col("rev26", "Net revenues Q2 2026", num=True),
            col("revPct", "Change", unit="%", num=True),
            col("ebitda25", "Adj. EBITDA Q2 2025", num=True),
            col("ebitda26", "Adj. EBITDA Q2 2026", num=True),
            col("ebitdaPct", "Change", unit="%", num=True),
            col("margin26", "Margin Q2 2026", unit="%", num=True),
            col("marginChg", "Margin change", unit="pp", num=True),
        ],
        segrows,
        unit="US$ m",
    )

    vd = [
        (
            "Las Vegas",
            "mgmt_driver_las_vegas",
            "Margin {eu_seg_margin_chg_las_vegas|pp} to {eu_seg_margin_las_vegas_q2_2026|%}: hold and volume, not price, so partly reversible.",
            "Las Vegas is the higher-margin segment, so its decline costs more EBITDA than Regional adds.",
        ),
        (
            "Regional",
            "mgmt_driver_regional",
            "Revenue up {eu_seg_rev_pct_regional|%} with Windsor consolidated from 3 March: not like-for-like.",
            "Organic growth is lower than reported.",
        ),
        (
            "Caesars Digital",
            "mgmt_driver_digital",
            "Revenue up {eu_seg_rev_pct_caesars_digital|%}, Adjusted EBITDA {eu_seg_ebitda_pct_caesars_digital|%}.",
            "Growth is being bought with promotion or hold.",
        ),
        (
            "Interest expense",
            "mgmt_driver_interest",
            "{eu_int_pct_q2|%} on lower debt and floating rates.",
            "Merger debt will reverse this [G8].",
        ),
    ]
    B["varianceDrivers"] = table(
        "CP-1B",
        "Variance drivers",
        [
            col("metric", "Metric", summary=True),
            col("mgmt", "Management says", summary=True),
            col("analyst", "Analyst view", summary=True),
            col("implication", "Credit implication", summary=False),
        ],
        [
            {
                "metric": m,
                "mgmt": quote(k),
                "analyst": T(a, illustrative=True, model=True),
                "implication": T(i, illustrative=True, model=True),
                "illustrative": True,
            }
            for m, k, a, i in vd
        ],
        illustrative=True,
        model=True,
    )

    kp = []
    for s, name in SEGMENTS:
        change = c.val(f"eu_seg_margin_chg_{s}")
        word = "Up" if change > 0 else ("Down" if change < 0 else "Flat")
        kp.append(
            {
                "kpi": f"{name} Adjusted EBITDA margin",
                "reference": dv(f"eu_seg_margin_{s}_q2_2025"),
                "current": dv(f"eu_seg_margin_{s}_q2_2026"),
                "change": dv(f"eu_seg_margin_chg_{s}"),
                "unit": "% (change in pp)",
                "trend": scale_word("delta_direction", word, illustrative=False),
            }
        )
    B["kpiChanges"] = table(
        "CP-1B",
        "KPI changes",
        [
            col("kpi", "KPI"),
            col("reference", "Q2 2025", unit="%", num=True),
            col("current", "Q2 2026", unit="%", num=True),
            col("change", "Change", unit="pp", num=True),
            col("unit", "Unit"),
            col("trend", "Trend"),
        ],
        kp,
    )

    B["guidance"] = table(
        "CP-1B",
        "Guidance against delivery",
        [
            col("metric", "Metric"),
            col("benchmark", "Guidance", num=True),
            col("actual", "Actual", num=True),
            col("variance", "Variance", num=True),
            col("note", "Note"),
        ],
        [
            {
                "metric": "Revenue and Adjusted EBITDA guidance",
                "benchmark": gd("G13"),
                "actual": dv("adj_ebitda_q2_2026"),
                "variance": gd("G13"),
                "note": T(
                    "No guidance, and no conference call because of the pending merger [release_no_call]."
                ),
            }
        ],
        unit="US$ m",
    )

    sig = [
        (
            "Las Vegas margin compression",
            "Adjusted EBITDA margin {eu_seg_margin_las_vegas_q2_2026|%}, down {eu_seg_margin_chg_las_vegas|pp} on Q2 2025.",
            "High",
            "The higher-margin segment is losing earnings faster than Regional adds them.",
        ),
        (
            "Regional growth flattered by the Windsor consolidation",
            "Revenue up {eu_seg_rev_pct_regional|%} with Caesars Windsor consolidated from 3 March 2026 [mgmt_driver_regional].",
            "Medium",
            "Reported growth overstates the organic trend.",
        ),
        (
            "Digital revenue up, Adjusted EBITDA down",
            "Revenue {eu_seg_rev_pct_caesars_digital|%}, Adjusted EBITDA {eu_seg_ebitda_pct_caesars_digital|%}; margin down {eu_seg_margin_chg_caesars_digital|pp}.",
            "Medium",
            "Growth costs more than it earns this quarter.",
        ),
        (
            "Unsecured 2032s priced for distress",
            "Last price {trace_czr_12769gad2_last_price}, rated {trace_czr_12769gad2_moodys} by Moody's.",
            "High",
            "The market is pricing unstated merger debt behind the secured notes [G8].",
        ),
    ]
    B["signals"] = table(
        "CP-1B",
        "Early-warning signals",
        [
            col("signal", "Signal"),
            col("evidence", "Evidence"),
            col("severity", "Severity"),
            col("implication", "Credit implication"),
        ],
        [
            {
                "signal": s,
                "evidence": T(e),
                "severity": scale_word("severity", sv),
                "implication": T(i, illustrative=True),
                "illustrative": True,
            }
            for s, e, sv, i in sig
        ],
        illustrative=True,
    )

    B["watchItems"] = table(
        "CP-2",
        "Watch items",
        [
            col("trigger", "Trigger"),
            col("signal", "Threshold or signal"),
            col("why", "Why it matters"),
        ],
        [
            {
                "trigger": "Merger debt terms",
                "signal": T(
                    "Amount and ranking of the committed financing [G8].", illustrative=True
                ),
                "why": T(
                    "Sets post-close leverage and where the unsecured notes rank.",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "trigger": "Las Vegas margin",
                "signal": T(
                    "Below {eu_seg_margin_las_vegas_q2_2026|%} for a second quarter.",
                    illustrative=True,
                ),
                "why": T(
                    "It would confirm that the Q2 decline is not one quarter's hold.",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "trigger": "CEI revolver maturity",
                "signal": T(
                    "Maturity on [cei_rcf_maturity] with no extension announced.", illustrative=True
                ),
                "why": T(
                    "The revolver is {cr_rcf_share|%} of accessible liquidity.", illustrative=True
                ),
                "illustrative": True,
            },
            {
                "trigger": "Merger timetable",
                "signal": T(
                    "End Date {merger_initial_end_date} and ticking fee from {merger_ticking_fee_date}.",
                    illustrative=True,
                ),
                "why": T(
                    "Delay raises the cost of the deal and the time the new debt stays undisclosed.",
                    illustrative=True,
                ),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    cs = ill["creditScore"]
    B["creditView"] = table(
        "CP-2",
        "Credit view",
        [col("item", "Item"), col("value", "View")],
        [
            {
                "item": "Credit Score",
                "value": {
                    "scale": "score",
                    "pos": cs["pos"],
                    "word": cs["word"],
                    "illustrative": True,
                },
            },
            {
                "item": "Credit Direction",
                "value": {
                    "scale": "dir",
                    "word": ill["creditDirection"]["word"],
                    "illustrative": True,
                },
            },
            {
                "item": "Sector Outlook",
                "value": {
                    "scale": "dir",
                    "word": ill["sectorOutlook"]["word"],
                    "illustrative": True,
                },
            },
            {
                "item": "Primary support",
                "value": T(
                    "Secured leverage {senior_leverage_ltm|x} and liquidity {liq_total|US$ m}.",
                    illustrative=True,
                ),
            },
            {
                "item": "Primary downside",
                "value": T("Unstated merger debt [G8].", illustrative=True),
            },
            {"item": "Confidence", "value": scale_word("confidence", "Medium")},
            {"item": "Basis", "value": "Full"},
        ],
        illustrative=True,
    )

    B["transactionsEvents"] = table(
        "CP-1A",
        "Transactions and events",
        [col("event", "Event"), col("date", "Date"), col("detail", "Detail")],
        [
            {
                "event": "Merger agreement signed",
                "date": dv("issuer.merger.agreement_date"),
                "detail": T("With {issuer.merger.parent} and {issuer.merger.merger_sub}."),
            },
            {
                "event": "Go-shop ended",
                "date": dv("merger_go_shop_end"),
                "detail": "Window for competing proposals closed.",
            },
            {
                "event": "Merger End Date",
                "date": dv("merger_initial_end_date"),
                "detail": T(
                    "Extendable to {merger_first_extended_end_date} and {merger_second_extended_end_date}."
                ),
            },
            {
                "event": "Ticking fee starts",
                "date": dv("merger_ticking_fee_date"),
                "detail": T("Per-day fee of {merger_ticking_fee_per_day|US$ m}."),
            },
            {
                "event": "Caesars Windsor consolidated",
                "date": T("3 March 2026 [mgmt_driver_regional]"),
                "detail": "Adds to Regional revenue from March.",
            },
        ],
        note="All dates are as stated in the merger documents and the Q2 2026 10-Q.",
    )

    # --- CP-4 ----------------------------------------------------------------
    B["documentRegister"] = table(
        "CP-4",
        "Document register",
        [
            col("document", "Document"),
            col("type", "Type"),
            col("date", "Date"),
            col("parties", "Parties"),
            col("status", "Status"),
        ],
        [
            {
                "document": "Credit Agreement",
                "type": "Credit agreement",
                "date": dv("doc_credit_agreement_date"),
                "parties": gd("structure_map"),
                "status": "In force",
            },
            {
                "document": "Incremental Assumption Agreement No. 3",
                "type": "Amendment",
                "date": dv("doc_incr3_date"),
                "parties": gd("structure_map"),
                "status": "In force",
            },
            {
                "document": "Fourth Amendment to Credit Agreement",
                "type": "Amendment",
                "date": dv("doc_amend4_date"),
                "parties": gd("structure_map"),
                "status": "In force",
            },
            {
                "document": "Fifth Amendment to Credit Agreement",
                "type": "Amendment",
                "date": dv("doc_amend5_date"),
                "parties": gd("structure_map"),
                "status": "In force",
            },
            {
                "document": "6.500% Senior Secured Notes due 2032 Indenture",
                "type": "Indenture",
                "date": dv("doc_indenture_2032_date"),
                "parties": T("Trustee: [doc_indenture_2032_trustee]"),
                "status": "In force",
            },
            {
                "document": "First Supplemental Indenture (2032 notes)",
                "type": "Supplemental indenture",
                "date": dv("doc_suppl1_date"),
                "parties": gd("structure_map"),
                "status": "In force",
            },
            {
                "document": "Second Supplemental Indenture (2032 notes)",
                "type": "Supplemental indenture",
                "date": dv("doc_suppl2_date"),
                "parties": gd("structure_map"),
                "status": "In force",
            },
            {
                "document": "Merger Agreement",
                "type": "Merger agreement",
                "date": dv("issuer.merger.agreement_date"),
                "parties": T("{issuer.merger.parent}; {issuer.merger.merger_sub}"),
                "status": "Signed, pending close",
            },
        ],
    )

    def status_for(headroom: Decimal, threshold: Decimal) -> str:
        if headroom < 0:
            return "Breached"
        if headroom < threshold / 10:
            return "Tight"
        return "Headroom"

    cov = [
        (
            "Total Leverage Ratio",
            "Maintenance",
            "Ceiling",
            "cov_max_total_leverage",
            "net_leverage_ltm",
            "cov_tlr_headroom",
        ),
        (
            "Fixed Charge Coverage Ratio",
            "Maintenance",
            "Floor",
            "cov_min_fccr",
            "cash_interest_cover_ltm",
            "cov_fccr_headroom",
        ),
        (
            "Pari secured incremental",
            "Incurrence",
            "Ceiling",
            "cov_incr_pari_sslr",
            "senior_leverage_ltm",
            "cov_sslr_headroom",
        ),
        (
            "Ratio debt (2032 indenture)",
            "Incurrence",
            "Floor",
            "ind_ratio_debt_fccr",
            "cash_interest_cover_ltm",
            "ind_fccr_headroom",
        ),
    ]
    B["covenantTests"] = table(
        "CP-4",
        "Covenant tests",
        [
            col("test", "Test"),
            col("type", "Type"),
            col("direction", "Direction"),
            col("threshold", "Threshold", unit="x", num=True),
            col("current", "Current", unit="x", num=True),
            col("basis", "Basis"),
            col("headroom", "Headroom", unit="x", num=True),
            col("status", "Status"),
        ],
        [
            {
                "test": t,
                "type": ty,
                "direction": d,
                "threshold": dv(th),
                "current": dv(cu),
                "basis": T("RBOT basis [gap:covenant_basis]"),
                "headroom": dv(hr),
                "status": status_cell(status_for(c.val(hr), c.val(th))),
            }
            for t, ty, d, th, cu, hr in cov
        ],
        note=T(
            "Maintenance tests apply to the Covenant Facilities only [cov_covenant_facilities]; after Term A is repaid they "
            "spring only when revolver use exceeds {cov_testing_condition_pct|%} of commitments [cov_springing_after_tla]; "
            "use today is {cr_rcf_util_pct|%}."
        ),
    )
    B["covenantTests"]["statusRule"] = (
        "Breached when headroom is below zero; Tight when it is under 10% of the threshold; otherwise Headroom."
    )

    cap_rows = [
        (
            "Debt",
            "Pari secured to 4.50x",
            "Ratio test: pro forma Senior Secured Leverage Ratio up to {cov_incr_pari_sslr|x} [cov_incr_pari_sslr]",
            dv("senior_secured_debt_2026_06_30"),
            dv("cap_pari_secured"),
            "Calculated",
            "High",
            "Secured debt ahead of the unsecured notes could grow by this much without lender consent.",
        ),
        (
            "Debt",
            "Junior secured to 4.75x",
            "Ratio test: pro forma Total Secured Leverage Ratio up to {cov_incr_junior_tslr|x} [cov_incr_junior_tslr]",
            dv("senior_secured_debt_2026_06_30"),
            dv("cap_junior_secured"),
            "Calculated",
            "Medium",
            "An alternative to the pari amount, not additive.",
        ),
        (
            "Debt",
            "Free-and-clear",
            "The greater of US$2,600m and 1.00x EBITDA, size {cap_free_clear_size|US$ m} [cov_incr_free_clear]",
            gd("incremental_usage"),
            gd("incremental_usage"),
            "Not computable",
            "Medium",
            "Size known; amount already used is not.",
        ),
        (
            "Debt",
            "Unsecured ratio debt at FCCR 2.00x",
            "Ratio test: pro forma Fixed Charge Coverage Ratio at least {cov_incr_unsecured_fccr|x} [cov_incr_unsecured_fccr]",
            gd("G21"),
            gd("G21"),
            "Not computable",
            None,
            "Needs pro forma interest on the new debt, which is unknown.",
        ),
        (
            "Restricted payments",
            "Restricted payments and investments",
            "Not extracted [gap:rp_capacity]",
            gd("rp_capacity"),
            gd("rp_capacity"),
            "Not computable",
            None,
            "Leakage capacity is unknown.",
        ),
    ]
    cap_out = []
    for ct, basket, formula, used, rem, st, sev, imp in cap_rows:
        cap_out.append(
            {
                "type": ct,
                "basket": basket,
                "formula": T(formula),
                "used": used,
                "remaining": rem,
                "status": scale_word("calc_status", st, illustrative=False),
                "severity": scale_word("severity", sev)
                if sev
                else gd(NS, "not rated: capacity cannot be computed"),
                "implication": T(imp, illustrative=True),
                "illustrative": True,
            }
        )
    B["capacity"] = table(
        "CP-4",
        "Debt and restricted-payment capacity",
        [
            col("type", "Capacity type"),
            col("basket", "Basket"),
            col("formula", "Formula"),
            col("used", "Used", num=True),
            col("remaining", "Remaining", num=True),
            col("status", "Status"),
            col("severity", "Severity"),
            col("implication", "Credit implication"),
        ],
        cap_out,
        unit="US$ m",
        note=T(
            "Indicative, on RBOT's basis [gap:covenant_basis]. The pari and junior amounts are alternatives."
        ),
    )

    flags = [
        ("Term B-1 is a Non-Covenant Facility", "[cov_tlb1_non_covenant]", "High", False),
        (
            "Maintenance tests spring after Term A is repaid",
            "[cov_springing_after_tla]",
            "Medium",
            False,
        ),
        (
            "Asset-sale sweep falls away at 3.00x or below",
            "[cov_asset_sale_stepdown_300]; Caesars is at {senior_leverage_ltm|x}",
            "High",
            False,
        ),
        ("Equity cure right for the maintenance tests", "[cov_equity_cure]", "Medium", False),
        (
            "Pro forma synergies count in indenture EBITDA",
            "[ind_pro_forma_synergies]",
            "Medium",
            False,
        ),
        (
            "Pari secured capacity could rank ahead of the unsecured notes",
            "{cap_pari_secured|US$ m} of capacity under the 4.50x test [cov_incr_pari_sslr]",
            "High",
            False,
        ),
        (
            "Change of control put (protective)",
            "Put at {ind_change_of_control|%} on the 2032 secured notes [ind_change_of_control]",
            "Low",
            True,
        ),
    ]
    B["redFlags"] = table(
        "CP-4",
        "Red flags",
        [col("flag", "Provision"), col("provision", "Evidence"), col("severity", "Severity")],
        [
            {
                "flag": f,
                "provision": T(p),
                "severity": scale_word("severity", sv),
                "illustrative": True,
                **({"kind": "protective", "tag": "Protective"} if prot else {}),
            }
            for f, p, sv, prot in flags
        ],
        illustrative=True,
    )

    B["ebitdaDefinition"] = table(
        "CP-4",
        "EBITDA definition",
        [
            col("feature", "Feature"),
            col("clause", "Clause"),
            col("cap", "Cap or condition"),
            col("effect", "Capacity effect"),
        ],
        [
            {
                "feature": "Pro forma cost savings and synergies",
                "clause": T("[ind_pro_forma_synergies]"),
                "cap": "“Reasonably expected”; no numeric cap in the excerpt.",
                "effect": T("Raises EBITDA, so raises capacity.", illustrative=True),
            },
            {
                "feature": "Testing Condition carve-out",
                "clause": T("[cov_testing_condition_pct]"),
                "cap": T(
                    "Revolver use above {cov_testing_condition_pct|%} of commitments, after US$170m of undrawn letters of credit."
                ),
                "effect": T(
                    "Lets the revolver be drawn to the carve-out without testing.",
                    illustrative=True,
                ),
            },
            {
                "feature": "Asset-sale step-downs",
                "clause": T("[cov_asset_sale_stepdown_350]; [cov_asset_sale_stepdown_300]"),
                "cap": T(
                    "50% of proceeds need not prepay at {cov_asset_sale_stepdown_350|x}; none at {cov_asset_sale_stepdown_300|x}."
                ),
                "effect": T("Less cash is swept to lenders as leverage falls.", illustrative=True),
            },
        ],
    )

    prot = [
        (
            "Maintenance covenants",
            2,
            "Tests protect the revolver and Term A only [cov_covenant_facilities]; Term B-1 has none [cov_tlb1_non_covenant].",
        ),
        (
            "Debt and lien capacity",
            2,
            "Pari capacity of {cap_pari_secured|US$ m} and a free-and-clear amount of {cap_free_clear_size|US$ m} [cov_incr_free_clear].",
        ),
        (
            "Change of control",
            4,
            "Put at {ind_change_of_control|%} on the 2032 secured notes [ind_change_of_control].",
        ),
        (
            "Asset-sale protection",
            2,
            "Sweep steps down at {cov_asset_sale_stepdown_350|x} and ends at {cov_asset_sale_stepdown_300|x} [cov_asset_sale_stepdown_300].",
        ),
        (
            "Disclosure",
            3,
            "Agreement and indenture terms extracted; restricted payment and investment baskets were not [gap:rp_capacity].",
        ),
    ]
    B["protectionScore"] = table(
        "CP-4",
        "Lender protection score",
        [col("area", "Area"), col("score", "Score"), col("evidence", "Evidence")],
        [
            {"area": a, "score": five_point(s), "evidence": T(e), "illustrative": True}
            for a, s, e in prot
        ],
        illustrative=True,
    )

    def na() -> dict:
        return gd("structure_map")

    B["structureMap"] = table(
        "CP-4",
        "Structure map",
        [
            col("entity", "Entity"),
            col("role", "Role"),
            col("restricted", "Restricted"),
            col("guarantor", "Guarantor"),
            col("source", "Source"),
        ],
        [
            {
                "entity": "Caesars Entertainment, Inc.",
                "role": T("Borrower and notes issuer [issuer.name] [trace_czr_12769gac4_issuer]"),
                "restricted": na(),
                "guarantor": na(),
                "source": "10-Q and TRACE",
            },
            {
                "entity": "Subsidiary Guarantors",
                "role": T(
                    "Added by the supplemental indentures of {doc_suppl1_date} and {doc_suppl2_date}"
                ),
                "restricted": na(),
                "guarantor": na(),
                "source": "Supplemental indentures",
            },
            {
                "entity": "CVA",
                "role": T(
                    "Separate borrower of the delayed draw term loan and revolver [debt_cva_ddtl_face_2026_06_30] [cva_rcf_commitment]"
                ),
                "restricted": na(),
                "guarantor": na(),
                "source": "10-Q debt table",
            },
            {
                "entity": "GLPI and VICI",
                "role": T(
                    "Landlords; financing obligations of {lt_financing_obligations_2026_06_30|US$ m}"
                ),
                "restricted": na(),
                "guarantor": na(),
                "source": "10-Q",
            },
        ],
    )

    # --- CP-2D ---------------------------------------------------------------
    liq = D["tables"]["liquidity"]["rows"]
    liq_meta = [
        ("Yes", "None stated"),
        ("Yes", "Net of the outstanding balance"),
        ("Yes", "CVA is a separate borrower"),
        ("Yes", "Committed to letters of credit"),
        ("No", "Committed to specific reserves"),
        ("No", "Committed as a regulatory requirement"),
        ("Yes", "Total of the lines above"),
    ]
    ls_rows = []
    for r, (acc, restr) in zip(liq, liq_meta, strict=True):
        ls_rows.append(
            {
                "component": r["label"],
                "amount": {**r["cell"], "unit": "US$ m"},
                "accessible": acc,
                "restriction": restr,
                **({"kind": "total"} if r["label"].startswith("Total") else {}),
            }
        )
    B["liquiditySources"] = table(
        "CP-2D",
        "Liquidity sources",
        [
            col("component", "Component"),
            col("amount", "Amount", num=True),
            col("accessible", "Accessible"),
            col("restriction", "Restriction"),
        ],
        ls_rows,
        unit="US$ m",
        note="Liquidity at 30 June 2026 as the Q2 2026 release states it.",
    )

    B["cashUses"] = table(
        "CP-2D",
        "Cash uses",
        [
            col("use", "Use"),
            col("amount", "Amount", num=True),
            col("timing", "Timing"),
            col("mandatory", "Mandatory"),
        ],
        [
            {
                "use": "Debt service, rest of 2026",
                "amount": dv("guide_remaining_2026_debt_service"),
                "timing": "H2 2026",
                "mandatory": "Yes",
            },
            {
                "use": "Interest, 2027",
                "amount": dv("guide_2027_interest"),
                "timing": "FY2027",
                "mandatory": "Yes",
            },
            {
                "use": "Maturities, 2027",
                "amount": dv("debt_maturity_2027"),
                "timing": "FY2027",
                "mandatory": "Yes",
            },
            {
                "use": "Maintenance capex, rest of 2026 (high end)",
                "amount": dv("guide_capex_remaining_2026_maintenance_high"),
                "timing": "H2 2026",
                "mandatory": "Yes",
            },
            {
                "use": "Growth and digital capex, rest of 2026 (high end)",
                "amount": dv("cr_disc_uses"),
                "timing": "H2 2026",
                "mandatory": "No",
            },
            {
                "use": "Capex, 2027",
                "amount": gd("capex_2027"),
                "timing": "FY2027",
                "mandatory": "Not known",
            },
            {
                "use": "Operating cash inflow",
                "amount": gd("G13"),
                "timing": "To December 2027",
                "mandatory": "Not applicable",
            },
        ],
        unit="US$ m",
    )

    B["runway"] = table(
        "CP-2D",
        "Runway",
        [col("item", "Item"), col("value", "Value", num=True)],
        [
            {"item": "Accessible liquidity", "value": dv("liq_total")},
            {"item": "Mandatory uses to 31 Dec 2027", "value": dv("cr_mand_uses")},
            {"item": "Headroom", "value": dv("cr_headroom")},
            {"item": "Months of runway", "value": dv("cr_runway_months")},
            {
                "item": "Pinch point",
                "value": T(
                    "31 January 2028: the CEI revolver matures [cei_rcf_maturity]; its net capacity {liq_cei_rcf_net|US$ m} is {cr_rcf_share|%} of liquidity."
                ),
            },
        ],
        unit="US$ m unless stated",
    )

    # --- CP-3C ---------------------------------------------------------------
    mp = []
    for tag, label, mat, press in (
        ("2026", "2026 (rest)", "debt_maturity_remaining_2026", "Low"),
        ("2027", "2027", "debt_maturity_2027", "Low"),
        ("2028", "2028", "debt_maturity_2028", "High"),
        ("2029", "2029", "debt_maturity_2029", "High"),
        ("2030", "2030", "debt_maturity_2030", "High"),
        ("after", "Thereafter", "debt_maturity_thereafter", "Medium"),
    ):
        mp.append(
            {
                "year": label,
                "maturing": dv(mat),
                "liquidityLeft": dv(f"cr_liq_left_{tag}"),
                "gap": dv(f"cr_gap_{tag}") if f"cr_gap_{tag}" in c.fig else "None",
                "pressure": scale_word("ordinal", press),
            }
        )
    B["maturityPressure"] = table(
        "CP-3C",
        "Maturity pressure",
        [
            col("year", "Fiscal year"),
            col("maturing", "Maturing", num=True),
            col("liquidityLeft", "Liquidity left before refinancing", num=True),
            col("gap", "Funding gap", num=True),
            col("pressure", "Pressure"),
        ],
        mp,
        unit="US$ m",
        note=T(
            "Liquidity left is accessible liquidity less cumulative scheduled maturities, and less the CEI revolver's capacity from 2028; before operating cash flow and any refinancing."
        ),
    )

    B["lmeCapacity"] = table(
        "CP-3C",
        "LME capacity",
        [
            col("indicator", "Indicator"),
            col("available", "Available"),
            col("evidence", "Evidence"),
            col("paths", "Paths enabled"),
        ],
        [
            {
                "indicator": "Pari secured incremental",
                "available": scale_word("availability", "Available"),
                "evidence": T(
                    "{cap_pari_secured|US$ m} indicative under the 4.50x test [cov_incr_pari_sslr]"
                ),
                "paths": "Priming by dilution",
                "illustrative": True,
            },
            {
                "indicator": "Junior secured incremental",
                "available": scale_word("availability", "Available"),
                "evidence": T(
                    "{cap_junior_secured|US$ m} indicative under the 4.75x test [cov_incr_junior_tslr]"
                ),
                "paths": "Secured debt behind the first lien",
                "illustrative": True,
            },
            {
                "indicator": "Non-covenant Term B-1",
                "available": scale_word("availability", "Available"),
                "evidence": T("[cov_tlb1_non_covenant]"),
                "paths": "Amend-and-extend without a maintenance test",
                "illustrative": True,
            },
            {
                "indicator": "Unrestricted subsidiary and drop-down capacity",
                "available": scale_word("availability", "Unclear"),
                "evidence": T("Baskets not extracted [gap:rp_capacity]"),
                "paths": "Asset transfers outside the credit group",
                "illustrative": True,
            },
            {
                "indicator": "Equity cure",
                "available": scale_word("availability", "Available"),
                "evidence": T("[cov_equity_cure]"),
                "paths": "Cures a maintenance breach with cash",
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    B["refinancingPaths"] = table(
        "CP-3C",
        "Refinancing paths",
        [
            col("path", "Path"),
            col("feasibility", "Feasibility"),
            col("direction", "Likelihood direction"),
            col("evidenceFor", "Evidence for"),
            col("evidenceAgainst", "Evidence against"),
            col("impact", "Creditor impact"),
        ],
        [
            {
                "path": "Merger closes with committed financing",
                "feasibility": scale_word("ordinal", "High"),
                "direction": scale_word("delta_direction", "Up"),
                "evidenceFor": T(
                    "Committed financing from ten banks [issuer.merger.financing]; not subject to a financing condition [issuer.merger.financing_condition].",
                    illustrative=True,
                ),
                "evidenceAgainst": T("Size of the new debt is unstated [G8].", illustrative=True),
                "impact": T(
                    "Existing secured and unsecured creditors may rank behind new debt or be diluted.",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "path": "Revolver and Term A extended before 2028",
                "feasibility": scale_word("ordinal", "Medium"),
                "direction": scale_word("delta_direction", "Flat"),
                "evidenceFor": T(
                    "Revolver {cr_rcf_util_pct|%} drawn and total liquidity of {liq_total|US$ m}.",
                    illustrative=True,
                ),
                "evidenceAgainst": T(
                    "Maturity on [cei_rcf_maturity] falls while the merger financing is unsettled.",
                    illustrative=True,
                ),
                "impact": T(
                    "Neutral to secured lenders if terms are unchanged.", illustrative=True
                ),
                "illustrative": True,
            },
            {
                "path": "Amend-and-extend of Term Loan B 2030",
                "feasibility": scale_word("ordinal", "Medium"),
                "direction": scale_word("delta_direction", "Flat"),
                "evidenceFor": T(
                    "Senior secured leverage of {senior_leverage_ltm|x}, inside the {cov_incr_pari_sslr|x} test.",
                    illustrative=True,
                ),
                "evidenceAgainst": T(
                    "2030 is the heaviest maturity year at {debt_maturity_2030|US$ m}.",
                    illustrative=True,
                ),
                "impact": T(
                    "Longer tenor for lenders, usually at a higher margin.", illustrative=True
                ),
                "illustrative": True,
            },
            {
                "path": "Exchange of the unsecured notes into secured debt",
                "feasibility": scale_word("ordinal", "Low"),
                "direction": scale_word("delta_direction", "Down"),
                "evidenceFor": T(
                    "Pari capacity of {cap_pari_secured|US$ m} could take part of the exchange.",
                    illustrative=True,
                ),
                "evidenceAgainst": T(
                    "Unsecured 2032s at {trace_czr_12769gad2_last_price} give holders little reason to exchange down in claim.",
                    illustrative=True,
                ),
                "impact": T(
                    "Unsecured holders move up in rank; existing secured creditors are diluted.",
                    illustrative=True,
                ),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    ce_rows = []
    for cls, base_k, lme_k, base_p, lme_p in (
        ("Senior secured", "senior_secured_debt_2026_06_30", "lme_sec_lme", "Low", "Medium"),
        ("Senior unsecured", "lme_uns_base", "lme_uns_lme", "Medium", "High"),
    ):
        ce_rows.append(
            {
                "class": cls,
                "case": "Base",
                "claims": dv(base_k),
                "priming": scale_word("ordinal", base_p),
                "illustrative": True,
            }
        )
        ce_rows.append(
            {
                "class": cls,
                "case": "LME",
                "claims": dv(lme_k),
                "priming": scale_word("ordinal", lme_p),
                "illustrative": True,
            }
        )
    for cls in ("Senior secured", "Senior unsecured"):
        ce_rows.append(
            {
                "class": cls,
                "case": "Stress",
                "claims": gd(
                    "G8", "the stress case needs the merger's debt, which the sources do not state"
                ),
                "priming": scale_word("ordinal", "Unknown"),
                "illustrative": True,
            }
        )
    B["creditorExposure"] = table(
        "CP-3C",
        "Creditor exposure",
        [
            col("class", "Creditor class"),
            col("case", "Case"),
            col("claims", "Claims at or ahead", num=True),
            col("priming", "Priming risk"),
        ],
        ce_rows,
        unit="US$ m",
        illustrative=True,
    )

    # --- CP-4C ---------------------------------------------------------------
    gates = [
        (
            "Market prices debt at distressed levels",
            "Unsecured 2032s at {trace_czr_12769gad2_last_price}, yield {trace_czr_12769gad2_last_yield|%}.",
            "Not met",
        ),
        (
            "Rating in Caa or below",
            "Unsecured 2032s rated {trace_czr_12769gad2_moodys} by Moody's, rated 28 Sep 2026.",
            "Met",
        ),
        (
            "Liquidity runway under 12 months",
            "{cr_runway_months} months of runway on mandatory uses.",
            "Not met",
        ),
        (
            "Maturity within 24 months without a path",
            "Next large maturity 2028, {debt_maturity_2028|US$ m}.",
            "Not met",
        ),
        ("Leverage after the merger debt", "Unstated [G8].", "Unclear"),
        ("Missed payment, covenant breach or LME announced", "None in the sources.", "Not met"),
    ]
    B["distressGate"] = table(
        "CP-4C",
        "Distress gate",
        [col("trigger", "Trigger"), col("evidence", "Evidence"), col("status", "Status")],
        [
            {
                "trigger": t,
                "evidence": T(e),
                "status": scale_word("gate_status", s),
                "illustrative": True,
            }
            for t, e, s in gates
        ]
        + [
            {
                "trigger": "Overall",
                "evidence": "Gate status for the Pathway",
                "status": scale_word("gate_status", "Unclear"),
                "kind": "total",
                "illustrative": True,
            }
        ],
        illustrative=True,
    )
    B["distressGate"]["overall"] = scale_word("gate_status", "Unclear")

    B["claims"] = table(
        "CP-4C",
        "Claims",
        [
            col("class", "Class"),
            col("claim", "Claim"),
            col("obligor", "Obligor"),
            col("amount", "Amount", num=True),
            col("security", "Security"),
            col("rank", "Priority rank"),
        ],
        [
            {
                "class": "Senior secured",
                "claim": "Revolvers, Term A, Term B, Term B-1, CVA delayed draw term loan, 7.00% and 6.50% secured notes",
                "obligor": "CEI and CVA",
                "amount": dv("senior_secured_debt_2026_06_30"),
                "security": "Secured",
                "rank": "1",
                "note": T("CVA is a separate borrower, treated pari passu here."),
            },
            {
                "class": "Senior unsecured",
                "claim": "4.625% notes 2029 and 6.00% notes 2032",
                "obligor": "CEI",
                "amount": dv("unsecured_debt_2026_06_30"),
                "security": "Unsecured",
                "rank": "2",
            },
            {
                "class": "Other debt",
                "claim": "SID bonds and other payables",
                "obligor": "Not stated",
                "amount": dv("other_debt_2026_06_30"),
                "security": "Not stated",
                "rank": "3",
                "note": T("Priority not stated, ranked last."),
            },
            {
                "class": "Lease financing obligations",
                "claim": "GLPI and VICI master leases",
                "obligor": "Not stated",
                "amount": dv("lt_financing_obligations_2026_06_30"),
                "security": "Not stated",
                "rank": T("Excluded [gap:lease_claims]"),
                "kind": "sub",
            },
        ],
        unit="US$ m",
    )

    def mult_cell(tag: str, mult) -> dict:
        if tag == "merger":
            return dv("dr_merger_multiple")
        return {"v": str(mult), "prov": "illustrative", "unit": "x"}

    B["evScenarios"] = table(
        "CP-4C",
        "Enterprise value scenarios",
        [
            col("scenario", "Scenario"),
            col("basis", "Valuation basis"),
            col("metric", "EBITDA after rent", num=True),
            col("multiple", "Multiple", unit="x", num=True),
            col("ev", "Enterprise value", num=True),
        ],
        [
            {
                "scenario": "Merger value",
                "basis": "Merger transaction value (cited)",
                "metric": dv("dr_ebitda_after_rent"),
                "multiple": mult_cell("merger", None),
                "ev": dv("ev_merger_usdm"),
            },
            {
                "scenario": "Downside",
                "basis": "Illustrative multiple",
                "metric": dv("dr_ebitda_after_rent"),
                "multiple": mult_cell("downside", SCENARIOS[1][2]),
                "ev": dv("dr_ev_downside"),
                "illustrative": True,
            },
            {
                "scenario": "Stress",
                "basis": "Illustrative multiple",
                "metric": dv("dr_ebitda_after_rent"),
                "multiple": mult_cell("stress", SCENARIOS[2][2]),
                "ev": dv("dr_ev_stress"),
                "illustrative": True,
            },
        ],
        unit="US$ m",
        note="EBITDA after rent is LTM Adjusted EBITDA less cash interest paid for the GLPI and VICI leases.",
    )

    rec_rows = []
    for tag, sname, mult in SCENARIOS:
        ill_s = mult is not None
        fulcrum_done = False
        for cls, cname, claim in CLASSES:
            r = c.val(f"dr_rec_{tag}_{cls}")
            is_fulcrum = (not fulcrum_done) and r < 100
            fulcrum_done = fulcrum_done or is_fulcrum
            avail = (
                dv("ev_merger_usdm" if tag == "merger" else f"dr_ev_{tag}")
                if cls == "secured"
                else dv(f"dr_avail_{tag}_{cls}")
            )
            rec_rows.append(
                {
                    "scenario": sname,
                    "class": cname,
                    "claim": dv(claim),
                    "available": avail,
                    "allocation": dv(f"dr_alloc_{tag}_{cls}"),
                    "residual": dv(f"dr_residual_{tag}") if cls == "other" else "",
                    "recovery": dv(f"dr_rec_{tag}_{cls}"),
                    "fulcrum": {
                        "text": "Yes" if is_fulcrum else "No",
                        "refs": [],
                        **({"illustrative": True} if ill_s else {}),
                    },
                    **({"illustrative": True} if ill_s else {}),
                }
            )
    for r in rec_rows:
        if r["residual"] == "":
            r["residual"] = {
                "text": "Not applicable: shown on the last class of the scenario",
                "refs": [],
            }
    B["recoveries"] = table(
        "CP-4C",
        "Recoveries",
        [
            col("scenario", "Scenario"),
            col("class", "Class"),
            col("claim", "Allowed claim", num=True),
            col("available", "Available value", num=True),
            col("allocation", "Allocation", num=True),
            col("residual", "Residual to equity", num=True),
            col("recovery", "Recovery", unit="%", num=True),
            col("fulcrum", "Fulcrum"),
        ],
        rec_rows,
        unit="US$ m",
        note="Absolute priority: senior secured, then senior unsecured, then other debt; lease claims excluded [gap:lease_claims]. The downside and stress rows rest on illustrative multiples.",
    )
    B["recoveries"]["note"] = c.T(B["recoveries"]["note"])

    B["restructuringPaths"] = table(
        "CP-4C",
        "Restructuring paths",
        [
            col("path", "Path"),
            col("process", "Process"),
            col("consent", "Consent"),
            col("newMoney", "New money"),
            col("treatment", "Class treatment"),
            col("milestones", "Milestones"),
            col("blockers", "Blockers"),
            col("likelihood", "Likelihood"),
        ],
        [
            {
                "path": "Merger closes and new debt is layered pari",
                "process": "Out of court",
                "consent": T(
                    "None needed within incremental capacity [cap_pari_secured]", illustrative=True
                ),
                "newMoney": T("Committed financing, amount unstated [G8]", illustrative=True),
                "treatment": T(
                    "Unsecured notes diluted behind new secured debt", illustrative=True
                ),
                "milestones": T("Merger End Date {merger_initial_end_date}", illustrative=True),
                "blockers": T(
                    "Size and ranking of the new debt are unknown [G8]", illustrative=True
                ),
                "likelihood": scale_word("ordinal", "High"),
                "illustrative": True,
            },
            {
                "path": "Amend-and-extend with secured lenders",
                "process": "Out of court",
                "consent": T("Secured lender consent", illustrative=True),
                "newMoney": T("None assumed", illustrative=True),
                "treatment": T("Secured lenders extend; unsecured unchanged", illustrative=True),
                "milestones": T(
                    "Before the revolver matures on [cei_rcf_maturity]", illustrative=True
                ),
                "blockers": T("Merger timetable and financing", illustrative=True),
                "likelihood": scale_word("ordinal", "Medium"),
                "illustrative": True,
            },
            {
                "path": "Distressed exchange of the unsecured notes",
                "process": "Out of court exchange offer",
                "consent": T("Holder participation", illustrative=True),
                "newMoney": T("None assumed", illustrative=True),
                "treatment": T(
                    "Unsecured holders take lower claim or higher rank", illustrative=True
                ),
                "milestones": T("After a downgrade or missed milestone", illustrative=True),
                "blockers": T(
                    "Unsecured 2032s at {trace_czr_12769gad2_last_price}; holders resist",
                    illustrative=True,
                ),
                "likelihood": scale_word("ordinal", "Low"),
                "illustrative": True,
            },
            {
                "path": "Chapter 11 with the master leases assumed",
                "process": "In court",
                "consent": T("Class votes", illustrative=True),
                "newMoney": T("Debtor-in-possession financing, not sized", illustrative=True),
                "treatment": T(
                    "Leases continue; lease claims excluded [gap:lease_claims]", illustrative=True
                ),
                "milestones": T("Filing and plan confirmation", illustrative=True),
                "blockers": T("Gaming licences and the lease structure", illustrative=True),
                "likelihood": scale_word("ordinal", "Low"),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    # --- CP-2H ---------------------------------------------------------------
    rt = []
    for agency, rk, _sk, label in (
        ("Moody's", "trace_czr_12769gad2_moodys", None, "6.00% unsecured 2032s"),
        ("S&P", "trace_czr_12769gad2_sp", None, "6.00% unsecured 2032s"),
        ("Moody's", "trace_czr_12769gac4_moodys", None, "6.50% secured 2032s"),
        ("S&P", "trace_czr_12769gac4_sp", None, "6.50% secured 2032s"),
    ):
        rt.append(
            {
                "agency": agency,
                "type": f"Issue rating, {label}",
                "metric": "Not stated",
                "threshold": gd("agency_triggers"),
                "current": dv(rk),
                "status": status_cell("Not computable"),
            }
        )
    B["ratingTriggers"] = table(
        "CP-2H",
        "Rating triggers",
        [
            col("agency", "Agency"),
            col("type", "Rating type"),
            col("metric", "Metric"),
            col("threshold", "Threshold", num=True),
            col("current", "Current rating"),
            col("status", "Status"),
        ],
        rt,
    )
    mig = []
    for agency, view in (
        (
            "Moody's",
            {
                "Base": "Unchanged until the new debt terms are known",
                "Downside": "Downgrade if the new debt ranks ahead of the unsecured notes",
            },
        ),
        (
            "S&P",
            {
                "Base": "Unchanged until the new debt terms are known",
                "Downside": "Downgrade if leverage rises materially at close",
            },
        ),
    ):
        for case, text in view.items():
            mig.append(
                {
                    "agency": agency,
                    "case": case,
                    "transition": T(text, illustrative=True),
                    "timing": "At merger close",
                    "catalyst": T("The new debt terms [G8]", illustrative=True),
                    "confidence": scale_word("confidence", "Low"),
                    "illustrative": True,
                }
            )
    B["migrationView"] = table(
        "CP-2H",
        "Migration view",
        [
            col("agency", "Agency"),
            col("case", "Case"),
            col("transition", "Likely transition"),
            col("timing", "Earliest timing"),
            col("catalyst", "Catalyst"),
            col("confidence", "Confidence"),
        ],
        mig,
        illustrative=True,
    )

    # --- CP-3 ----------------------------------------------------------------
    trace_of = {
        "CEI 6.50% Senior Secured Notes 2032": "trace_czr_12769gac4",
        "CEI 6.00% Senior Notes 2032": "trace_czr_12769gad2",
    }
    valuation = {"CEI 6.50% Senior Secured Notes 2032": 2, "CEI 6.00% Senior Notes 2032": 4}
    il = []
    for item in ill["byInstrument"]:
        f = item["facility"]
        tr = trace_of.get(f)
        row = {
            "instrument": f,
            "basis": "Market" if tr else "None",
            "date": dv(f"{tr}_last_date") if tr else gd("G18"),
            "price": dv(f"{tr}_last_price") if tr else gd("G18"),
            "yield": dv(f"{tr}_last_yield") if tr else gd("G18"),
            "spread": gd("G19"),
            "valuation": {
                "scale": "val",
                "pos": valuation[f],
                "word": VAL_WORDS[valuation[f]],
                "illustrative": True,
            }
            if f in valuation
            else gd("G18", "no level: no price or yield is in the sources"),
            "recommendation": rec_cell(item["pos"], item["word"]),
            "illustrative": True,
        }
        il.append(row)
    B["instrumentLevels"] = table(
        "CP-3",
        "Instrument levels",
        [
            col("instrument", "Instrument"),
            col("basis", "Level basis"),
            col("date", "Level date"),
            col("price", "Price", num=True),
            col("yield", "Yield (YTM)", unit="%", num=True),
            col("spread", "Spread", num=True),
            col("valuation", "Valuation"),
            col("recommendation", "Recommendation"),
        ],
        il,
        illustrative=True,
        note=T(
            "Last trade from FINRA TRACE, not a bid or evaluated price. Spreads need a benchmark curve [G19]; loan prices are not in the sources [G18]."
        ),
    )

    B["compensation"] = table(
        "CP-3",
        "Compensation against risk",
        [
            col("instrument", "Instrument"),
            col("rank", "Structural rank"),
            col("sensitivity", "Recovery sensitivity"),
            col("compensation", "Compensation against risk"),
            col("comparables", "Comparables"),
        ],
        [
            {
                "instrument": "6.50% SSN 2032",
                "rank": "1",
                "sensitivity": scale_word("ordinal", "Low"),
                "compensation": scale_word("compensation", "Attractive"),
                "comparables": T(
                    "MGM 6.125% 2029 at {trace_mgm_552953ck5_last_yield|%}", illustrative=True
                ),
                "illustrative": True,
            },
            {
                "instrument": "6.00% SN 2032",
                "rank": "2",
                "sensitivity": scale_word("ordinal", "High"),
                "compensation": scale_word("compensation", "Inadequate"),
                "comparables": T(
                    "{rv_yield_pickup|pp} over the secured for a fulcrum-risk claim",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "instrument": "Term Loan B",
                "rank": "1",
                "sensitivity": scale_word("ordinal", "Low"),
                "compensation": scale_word("compensation", "Unclear"),
                "comparables": T("No loan price or margin in the sources [G18]", illustrative=True),
                "illustrative": True,
            },
            {
                "instrument": "Term Loan B-1",
                "rank": "1",
                "sensitivity": scale_word("ordinal", "Low"),
                "compensation": scale_word("compensation", "Unclear"),
                "comparables": T("No loan price or margin in the sources [G18]", illustrative=True),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    pref = [
        (
            "6.50% SSN 2032",
            "Preferred",
            "Secured, priced below par with a first-lien claim.",
            "Merger debt that ranks pari [G8].",
        ),
        (
            "7.00% SSN 2030",
            "Neutral",
            "Secured, but no market level in the sources [G18].",
            "A price or level becoming available.",
        ),
        (
            "Term Loan B",
            "Requires more work",
            "No loan price or margin in the sources [G18].",
            "A loan level or LSTA mark.",
        ),
        (
            "Term Loan B-1",
            "Requires more work",
            "No loan price or margin in the sources [G18]; a Non-Covenant Facility.",
            "A loan level or LSTA mark.",
        ),
        (
            "6.00% SN 2032",
            "Avoid",
            "Unsecured and the likely fulcrum in the downside.",
            "Disclosure of the merger debt [G8].",
        ),
        (
            "4.625% SN 2029",
            "Avoid",
            "Unsecured, behind the secured debt and its pari capacity.",
            "Disclosure of the merger debt [G8].",
        ),
    ]
    B["securityPreference"] = table(
        "CP-3",
        "Security preference",
        [
            col("instrument", "Instrument"),
            col("preference", "Preference"),
            col("reason", "Key reason"),
            col("trigger", "Monitoring trigger"),
        ],
        [
            {
                "instrument": i,
                "preference": scale_word("preference", p),
                "reason": T(r, illustrative=True),
                "trigger": T(t, illustrative=True),
                "illustrative": True,
            }
            for i, p, r, t in pref
        ],
        illustrative=True,
    )

    B["marketVsFundamental"] = table(
        "CP-3D",
        "Market against fundamentals",
        [
            col("implication", "Market implication"),
            col("fundamental", "Fundamental evidence"),
            col("alignment", "Alignment"),
            col("basis", "Basis"),
            col("open", "Open question"),
        ],
        [
            {
                "implication": T(
                    "Unsecured priced for distress at {trace_czr_12769gad2_last_price}",
                    illustrative=True,
                ),
                "fundamental": T("Net leverage {net_leverage_ltm|x} before merger debt"),
                "alignment": scale_word("alignment", "Divergent"),
                "basis": T("The market prices the unstated merger debt [G8].", illustrative=True),
                "open": T("What will the new debt be? [G8]", illustrative=True),
                "illustrative": True,
            },
            {
                "implication": T(
                    "Secured below par at {trace_czr_12769gac4_last_price}", illustrative=True
                ),
                "fundamental": T("Secured leverage {senior_leverage_ltm|x}"),
                "alignment": scale_word("alignment", "Aligned"),
                "basis": T(
                    "Yield of {trace_czr_12769gac4_last_yield|%} for a secured claim covered at this leverage.",
                    illustrative=True,
                ),
                "open": T(
                    "Does pari capacity dilute the secured claim? [cap_pari_secured]",
                    illustrative=True,
                ),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    # --- CP-1C / CP-1D / CP-2A / CP-6 / CP-5 ----------------------------------
    B["peerSet"] = table(
        "CP-1C",
        "Peer set",
        [
            col("peer", "Peer"),
            col("basis", "Selection basis"),
            col("comparability", "Comparability"),
            col("data", "Data availability"),
        ],
        [
            {
                "peer": "MGM Resorts",
                "basis": T(
                    "Large US casino operator with Las Vegas and regional assets", illustrative=True
                ),
                "comparability": scale_word("comparability", "Partial"),
                "data": T(
                    "Revenue {mgm_revenues_q2_2026|US$ m}, Adjusted EBITDA {mgm_adj_ebitda_q2_2026|US$ m}; EBITDAR differs [G14]"
                ),
                "illustrative": True,
            },
            {
                "peer": "PENN Entertainment",
                "basis": T("US regional casino and online operator", illustrative=True),
                "comparability": scale_word("comparability", "Partial"),
                "data": T(
                    "Revenue {penn_revenues_q2_2026|US$ m}, Adjusted EBITDA {penn_adj_ebitda_q2_2026|US$ m}; EBITDAR differs [G14]"
                ),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    cc = []
    for p, name, eb in (
        ("fy2023", "FY2023", "adj_ebitda_fy2023"),
        ("fy2024", "FY2024", "adj_ebitda_fy2024"),
        ("fy2025", "FY2025", "adj_ebitda_fy2025"),
        ("h1_2025", "H1 2025", "adj_ebitda_h1_2025"),
        ("h1_2026", "H1 2026", "adj_ebitda_h1_2026"),
        ("ltm", "LTM Q2 2026", "ltm_adj_ebitda_q2_2026"),
    ):
        cfo = {"ltm": "ltm_cfo_q2_2026"}.get(p, f"cfo_{p}")
        cc.append(
            {"period": name, "ebitda": dv(eb), "cfo": dv(cfo), "conversion": dv(f"dq_conv_{p}")}
        )
    B["cashConversion"] = table(
        "CP-1D",
        "Cash conversion",
        [
            col("period", "Period"),
            col("ebitda", "Adjusted EBITDA", unit="US$ m", num=True),
            col("cfo", "Cash from operations", unit="US$ m", num=True),
            col("conversion", "Conversion", unit="%", num=True),
        ],
        cc,
    )

    B["addbackAssessment"] = table(
        "CP-1D",
        "Add-back assessment",
        [
            col("addback", "Add-back"),
            col("period", "Period"),
            col("amount", "Amount", unit="US$ m", num=True),
            col("status", "Realization"),
            col("verdict", "Verdict"),
            col("rationale", "Rationale"),
        ],
        [
            {
                "addback": "Transaction costs and other, net",
                "period": "Q2 2026",
                "amount": dv("recon_transaction_costs_q2_2026"),
                "status": "REALIZED",
                "verdict": scale_word("addback_verdict", "Supported"),
                "rationale": T(
                    "Issuer-stated; includes merger costs [merger_transaction_costs_2026].",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "addback": "Stock-based compensation expense",
                "period": "Q2 2026",
                "amount": dv("recon_sbc_q2_2026"),
                "status": "REALIZED",
                "verdict": scale_word("addback_verdict", "Supported"),
                "rationale": T("Issuer-stated non-cash charge.", illustrative=True),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    B["debtLikeItems"] = table(
        "CP-1D",
        "Debt-like items",
        [
            col("item", "Item"),
            col("amount", "Amount", unit="US$ m", num=True),
            col("period", "Period"),
            col("treatment", "Treatment"),
            col("basis", "Basis"),
        ],
        [
            {
                "item": "GLPI and VICI financing obligations",
                "amount": dv("lt_financing_obligations_2026_06_30"),
                "period": "30 Jun 2026",
                "treatment": scale_word("debt_like_treatment", "Debt-like"),
                "basis": T(
                    "Shown apart from reported debt; the leases carry cash rent [ltm_cash_interest_rent_q2_2026].",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "item": "Operating lease liability",
                "amount": dv("operating_lease_liability_2025_12_31"),
                "period": "31 Dec 2025",
                "treatment": scale_word("debt_like_treatment", "Debt-like"),
                "basis": T("Latest stated balance.", illustrative=True),
                "illustrative": True,
            },
            {
                "item": "Operating lease liability",
                "amount": gd("G5"),
                "period": "30 Jun 2026",
                "treatment": scale_word("debt_like_treatment", "Unclear"),
                "basis": T("Not stated at 30 June 2026 [G5].", illustrative=True),
                "illustrative": True,
            },
            {
                "item": "Finance lease liability",
                "amount": dv("finance_lease_liability_2025_12_31"),
                "period": "31 Dec 2025",
                "treatment": scale_word("debt_like_treatment", "Debt-like"),
                "basis": T("Latest stated balance.", illustrative=True),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    B["downsidePaths"] = table(
        "CP-2A",
        "Downside paths",
        [
            col("path", "Path"),
            col("firstBreak", "First break"),
            col("timing", "Timing"),
            col("probability", "Probability"),
            col("impact", "Impact"),
        ],
        [
            {
                "path": "Layered take-private",
                "firstBreak": T(
                    "Unsecured recovery: {dr_rec_downside_unsecured|%} in the illustrative downside",
                    illustrative=True,
                ),
                "timing": "At close",
                "probability": scale_word("ordinal", "Medium"),
                "impact": scale_word("ordinal", "High"),
                "illustrative": True,
            },
            {
                "path": "Las Vegas downturn",
                "firstBreak": T(
                    "Lease-inclusive interest cover of {interest_cover_ltm|x}", illustrative=True
                ),
                "timing": "Next four quarters",
                "probability": scale_word("ordinal", "Medium"),
                "impact": scale_word("ordinal", "Medium"),
                "illustrative": True,
            },
            {
                "path": "2028-2030 refinancing wall without the revolver",
                "firstBreak": T(
                    "Liquidity left turns negative in 2028 ({cr_liq_left_2028|US$ m})",
                    illustrative=True,
                ),
                "timing": "2028 to 2030",
                "probability": scale_word("ordinal", "Low"),
                "impact": scale_word("ordinal", "High"),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    B["challenge"] = table(
        "CP-6",
        "Challenge",
        [
            col("claim", "Claim"),
            col("counter", "Counter-evidence"),
            col("resolution", "Resolution"),
            col("change", "What would change the view"),
        ],
        [
            {
                "claim": T("Secured 2032s are money-good after the merger", illustrative=True),
                "counter": T("Pari capacity of {cap_pari_secured|US$ m} dilutes them"),
                "resolution": T(
                    "Held, with the unstated merger debt as the open risk [G8].", illustrative=True
                ),
                "change": T("New secured debt larger than the pari capacity.", illustrative=True),
                "illustrative": True,
            },
            {
                "claim": T("The unsecured notes are the fulcrum", illustrative=True),
                "counter": T(
                    "At the merger value every class recovers in full ({dr_rec_merger_unsecured|%})"
                ),
                "resolution": T(
                    "Held only below the merger value, at the illustrative 5.0x downside.",
                    illustrative=True,
                ),
                "change": T(
                    "A disclosed capital structure that changes the value waterfall.",
                    illustrative=True,
                ),
                "illustrative": True,
            },
            {
                "claim": T("Las Vegas weakness is cyclical", illustrative=True),
                "counter": T(
                    "Two segments lost margin in the same quarter [eu_seg_margin_chg_las_vegas] [eu_seg_margin_chg_caesars_digital]"
                ),
                "resolution": T("Not resolved; one quarter is not a trend.", illustrative=True),
                "change": T("A second quarter of lower Las Vegas margin.", illustrative=True),
                "illustrative": True,
            },
        ],
        illustrative=True,
    )

    B["bindingLimitations"] = table(
        "CP-5",
        "Binding limitations",
        [
            col("module", "Module"),
            col("limitation", "Limitation"),
            col("effect", "Effect on the decision"),
            col("lift", "Source that would lift it"),
        ],
        [
            {
                "module": "CP-2",
                "limitation": T("Merger debt amount and ranking [G8]"),
                "effect": "Post-close leverage and the rank of existing creditors cannot be sized.",
                "lift": "The merger financing commitment papers or a lender presentation.",
            },
            {
                "module": "CP-3",
                "limitation": T("Loan prices and margins [G18]"),
                "effect": "The term loans cannot be valued against the notes.",
                "lift": "Loan marks or a dealer run.",
            },
            {
                "module": "FIT",
                "limitation": T(
                    "Issue ratings for the loans and other notes [gap:issue_ratings_other]"
                ),
                "effect": "The loans count as Unrated in Test CLO I's CCC bucket, which sets the 0.14% headroom.",
                "lift": "Issue ratings for the loans and the 2029 and 2030 notes.",
            },
            {
                "module": "CP-3",
                "limitation": T("Spreads [G19]"),
                "effect": "Compensation is judged on yield, not spread.",
                "lift": "A benchmark curve and spread data.",
            },
            {
                "module": "FIT",
                "limitation": T("Eligibility of a senior secured bond [gap:bond_eligibility]"),
                "effect": "Whether the proposed notes can be bought at all is unconfirmed.",
                "lift": "The CLO indenture eligibility criteria.",
            },
        ],
    )
    return B


# ---------------------------------------------------------------- charts (SPEC 3.6)
def build_charts(c: Ctx, fit: dict) -> dict:
    CH: dict[str, dict] = {}
    cd = c.cd

    def fv(k: str) -> str:
        return c.figure(k)["v"]

    def chart(cid, kind, title, summary, source, unit, **rest):
        CH[cid] = {
            "id": cid,
            "kind": kind,
            "title": title,
            "unit": unit,
            "summary": summary,
            "source": source,
            **rest,
        }

    chart(
        "fig-headline-results",
        "columns",
        "Q2 2026 against Q2 2025: Adjusted EBITDA, interest, D&A and capex",
        f"Adjusted EBITDA was {fv('adj_ebitda_q2_2026')} in Q2 2026 against {fv('adj_ebitda_q2_2025')} in Q2 2025; "
        f"interest expense, net was {fv('interest_expense_q2_2026')} against {fv('interest_expense_q2_2025')}, "
        f"depreciation and amortization {fv('d_and_a_q2_2026')} against {fv('d_and_a_q2_2025')} and net capital "
        f"expenditures {fv('capex_net_segment_q2_2026')} against {fv('capex_net_segment_q2_2025')}.",
        "Caesars Q2 2026 earnings release, income statement, EBITDA reconciliation and capital expenditures by segment",
        "US$ m",
        categoryLabel="Metric",
        categories=["Adjusted EBITDA", "Interest expense, net", "D&A", "Capex, net"],
        series=[
            {
                "key": "q2_2025",
                "label": "Q2 2025",
                "color": "neutral",
                "values": [
                    cd("adj_ebitda_q2_2025"),
                    cd("interest_expense_q2_2025"),
                    cd("d_and_a_q2_2025"),
                    cd("capex_net_segment_q2_2025"),
                ],
            },
            {
                "key": "q2_2026",
                "label": "Q2 2026",
                "color": 1,
                "values": [
                    cd("adj_ebitda_q2_2026"),
                    cd("interest_expense_q2_2026"),
                    cd("d_and_a_q2_2026"),
                    cd("capex_net_segment_q2_2026"),
                ],
            },
        ],
    )

    rows = []
    for s, name in SEGMENTS:
        rows.append(
            {
                "key": s,
                "label": name,
                "from": cd(f"eu_seg_margin_{s}_q2_2025"),
                "to": cd(f"eu_seg_margin_{s}_q2_2026"),
                "change": cd(f"eu_seg_margin_chg_{s}"),
            }
        )
    chart(
        "fig-kpi-margins",
        "dumbbell",
        "Segment Adjusted EBITDA margin, Q2 2025 to Q2 2026",
        f"Las Vegas margin moved {fv('eu_seg_margin_chg_las_vegas')} pp to {fv('eu_seg_margin_las_vegas_q2_2026')}% and "
        f"Caesars Digital {fv('eu_seg_margin_chg_caesars_digital')} pp; Regional moved {fv('eu_seg_margin_chg_regional')} pp "
        f"and Managed and Branded {fv('eu_seg_margin_chg_managed_branded')} pp.",
        "Caesars Q2 2026 earnings release, segment table (margins calculated)",
        "%",
        categoryLabel="Segment",
        fromLabel="Q2 2025",
        toLabel="Q2 2026",
        rows=rows,
    )

    chart(
        "fig-liquidity-bridge",
        "waterfall",
        "Accessible liquidity to December 2027 before operating cash flow",
        f"Accessible liquidity of {fv('liq_total')} falls to {fv('cr_closing')} by December 2027 after mandatory uses of "
        f"{fv('cr_mand_uses')} and discretionary capex of {fv('cr_disc_uses')}; operating cash flow is not forecast.",
        "Caesars Q2 2026 10-Q and earnings release (liquidity, debt maturities, interest and capital expenditure estimates)",
        "US$ m",
        categoryLabel="Step",
        steps=[
            {
                "label": "Accessible liquidity, 30 Jun 2026",
                "short": "Opening liquidity",
                "kind": "total",
                "d": cd("liq_total"),
            },
            {
                "label": "Debt service, rest of 2026",
                "short": "Debt service",
                "kind": "delta",
                "d": neg(cd("guide_remaining_2026_debt_service")),
            },
            {
                "label": "Interest, 2027",
                "short": "Interest 2027",
                "kind": "delta",
                "d": neg(cd("guide_2027_interest")),
            },
            {
                "label": "Maturities, 2027",
                "short": "Maturities 2027",
                "kind": "delta",
                "d": neg(cd("debt_maturity_2027")),
            },
            {
                "label": "Maintenance capex, rest of 2026",
                "short": "Maintenance capex",
                "kind": "delta",
                "d": neg(cd("guide_capex_remaining_2026_maintenance_high")),
            },
            {
                "label": "Growth and digital capex, rest of 2026",
                "short": "Growth capex",
                "kind": "delta",
                "d": neg(cd("cr_disc_uses")),
            },
            {
                "label": "Operating cash inflow",
                "short": "Operating cash",
                "kind": "delta",
                "d": c.gd("G13"),
            },
            {
                "label": "Closing liquidity before operating cash flow",
                "short": "Closing",
                "kind": "total",
                "d": cd("cr_closing"),
            },
        ],
    )

    cats = ["2026 (rest)", "2027", "2028", "2029", "2030", "Thereafter"]
    tags = ["2026", "2027", "2028", "2029", "2030", "after"]
    mats = [
        "debt_maturity_remaining_2026",
        "debt_maturity_2027",
        "debt_maturity_2028",
        "debt_maturity_2029",
        "debt_maturity_2030",
        "debt_maturity_thereafter",
    ]
    chart(
        "fig-funding-gap",
        "columns",
        "Maturities and liquidity left before refinancing",
        f"Liquidity left before refinancing turns negative in 2028, at {fv('cr_liq_left_2028')}, when the CEI revolver "
        f"matures, and reaches {fv('cr_liq_left_after')} after 2030.",
        "Caesars Q2 2026 10-Q debt maturities and liquidity (liquidity left calculated)",
        "US$ m",
        categoryLabel="Fiscal year",
        categories=cats,
        series=[
            {"key": "maturing", "label": "Maturing", "color": 4, "values": [cd(m) for m in mats]},
            {
                "key": "left",
                "label": "Liquidity left before refinancing",
                "color": 1,
                "values": [cd(f"cr_liq_left_{t}") for t in tags],
            },
        ],
    )

    cov_rows = [
        (
            "tlr",
            "Total Leverage Ratio (maintenance)",
            "max",
            "cov_max_total_leverage",
            "net_leverage_ltm",
            "cov_tlr_headroom",
        ),
        (
            "fccr",
            "Fixed Charge Coverage Ratio (maintenance)",
            "min",
            "cov_min_fccr",
            "cash_interest_cover_ltm",
            "cov_fccr_headroom",
        ),
        (
            "pari",
            "Pari secured incremental (incurrence)",
            "max",
            "cov_incr_pari_sslr",
            "senior_leverage_ltm",
            "cov_sslr_headroom",
        ),
        (
            "ratio",
            "Ratio debt, 2032 indenture (incurrence)",
            "min",
            "ind_ratio_debt_fccr",
            "cash_interest_cover_ltm",
            "ind_fccr_headroom",
        ),
    ]
    chart(
        "fig-covenant-headroom",
        "bullet",
        "Covenant and incurrence tests against their thresholds",
        f"Total leverage of {fv('net_leverage_ltm')}x sits {fv('cov_tlr_headroom')}x inside its {fv('cov_max_total_leverage')}x "
        f"ceiling and fixed charge cover of {fv('cash_interest_cover_ltm')}x sits {fv('cov_fccr_headroom')}x above its "
        f"{fv('cov_min_fccr')}x floor, on RBOT's basis.",
        "Credit Agreement Incremental Assumption No. 3 and 2032 secured notes indenture; ratios on RBOT's basis (company Adjusted EBITDA, face debt)",
        "x",
        categoryLabel="Test",
        rows=[
            {
                "key": k,
                "label": lab,
                "direction": d,
                "threshold": cd(th),
                "current": cd(cu),
                "headroom": cd(hr),
            }
            for k, lab, d, th, cu, hr in cov_rows
        ],
    )

    chart(
        "fig-basket-capacity",
        "stackedColumns",
        "Incremental debt capacity: used and remaining",
        f"Under the 4.50x test senior secured debt of {fv('senior_secured_debt_2026_06_30')} leaves {fv('cap_pari_secured')} "
        f"of indicative pari capacity; the 4.75x junior amount of {fv('cap_junior_secured')} is an alternative, not additive; "
        f"the free-and-clear amount used is not stated.",
        "Credit Agreement Incremental Assumption No. 3, Section 2.21; amounts on RBOT's basis",
        "US$ m",
        categoryLabel="Basket",
        categories=["Pari secured 4.50x", "Junior secured 4.75x", "Free-and-clear"],
        series=[
            {
                "label": "Used",
                "color": 4,
                "values": [
                    cd("senior_secured_debt_2026_06_30"),
                    cd("senior_secured_debt_2026_06_30"),
                    c.gd("incremental_usage"),
                ],
            },
            {
                "label": "Remaining",
                "color": 1,
                "values": [
                    cd("cap_pari_secured"),
                    cd("cap_junior_secured"),
                    c.gd("incremental_usage"),
                ],
            },
        ],
    )

    chart(
        "fig-lme-exposure",
        "columns",
        "Claims at or ahead of each class: base and LME case",
        f"Drawing the pari secured capacity lifts claims at or ahead of the unsecured notes from {fv('lme_uns_base')} to "
        f"{fv('lme_uns_lme')} and senior secured claims from {fv('senior_secured_debt_2026_06_30')} to {fv('lme_sec_lme')}.",
        "Caesars Q2 2026 10-Q debt table; capacity from the Credit Agreement Section 2.21 (indicative)",
        "US$ m",
        categoryLabel="Creditor class",
        categories=["Senior secured", "Senior unsecured"],
        series=[
            {
                "key": "base",
                "label": "Base",
                "color": 4,
                "values": [cd("senior_secured_debt_2026_06_30"), cd("lme_uns_base")],
            },
            {
                "key": "lme",
                "label": "LME",
                "color": 1,
                "values": [cd("lme_sec_lme"), cd("lme_uns_lme")],
            },
        ],
    )

    chart(
        "fig-recovery-by-class",
        "columns",
        "Recovery by class and scenario",
        f"At the merger value every class recovers in full; at an illustrative 5.0x the senior unsecured notes recover "
        f"{fv('dr_rec_downside_unsecured')}%, and at 4.0x the senior secured debt recovers {fv('dr_rec_stress_secured')}%.",
        "Calculated from the Caesars Q2 2026 10-Q debt table and the merger's stated transaction value; downside and stress multiples are illustrative",
        "%",
        categoryLabel="Class",
        categories=["Senior secured", "Senior unsecured", "Other debt"],
        series=[
            {
                "key": tag,
                "label": label,
                "color": col_,
                "values": [cd(f"dr_rec_{tag}_{cls}") for cls, _, _ in CLASSES],
            }
            for tag, label, col_ in (
                ("merger", "Merger value", 1),
                ("downside", "Downside 5.0x", 2),
                ("stress", "Stress 4.0x", 4),
            )
        ],
    )

    for tag, name, mult in SCENARIOS:
        ev = "ev_merger_usdm" if tag == "merger" else f"dr_ev_{tag}"
        steps = [
            {
                "label": f"Enterprise value, {name.lower()}",
                "short": "Enterprise value",
                "kind": "total",
                "d": cd(ev),
            }
        ]
        for cls, cname, _ in CLASSES:
            steps.append(
                {
                    "label": f"{cname}",
                    "short": cname.replace("Senior ", ""),
                    "kind": "delta",
                    "d": neg(cd(f"dr_alloc_{tag}_{cls}")),
                }
            )
        steps.append(
            {
                "label": "Residual to equity",
                "short": "Residual",
                "kind": "total",
                "d": cd(f"dr_residual_{tag}"),
            }
        )
        chart(
            f"fig-value-allocation-{tag}",
            "waterfall",
            f"Value allocation, {name.lower()} scenario",
            f"Enterprise value of {fv(ev)} is allocated by absolute priority; {fv('dr_residual_' + tag)} is left for equity.",
            "Calculated from the Caesars Q2 2026 10-Q debt table"
            + ("" if mult is None else "; the scenario multiple is illustrative"),
            "US$ m",
            categoryLabel="Step",
            steps=steps,
        )

    lim = {x["id"]: x for x in fit["limits"]}

    def bare(d: dict) -> dict:
        return {k: v for k, v in d.items() if k != "unit"}

    def brow(key, label, lid, current=None):
        x = lim[lid]
        return {
            "key": key,
            "label": label,
            "direction": "max",
            "threshold": bare(x["limit"]),
            "current": bare(current or x["current"]),
            "headroom": bare(x["headroomPct"]),
        }

    chart(
        "fig-fit-limits",
        "bullet",
        "Test CLO I limits a Caesars position touches",
        f"Caesars has no existing exposure (C-01 headroom {lim['C-01']['headroomPct']['v']}% of NAV) and the Leisure "
        f"Facilities & Services sector has {lim['SECTOR']['headroomPct']['v']}%; the CCC bucket (C-04) has only "
        f"{lim['C-04']['headroomPct']['v']}%, which binds the unrated instruments. Synthetic portfolio.",
        "Test CLO I constraints compliance monitor and exposure report, 29 May 2026 (synthetic)",
        "% NAV",
        categoryLabel="Limit",
        rows=[
            brow("c01", "C-01 Single issuer (Caesars, existing exposure none)", "C-01"),
            brow("sector", "Leisure Facilities & Services sector", "SECTOR"),
            brow("c04", "C-04 CCC bucket (binds unrated instruments)", "C-04"),
            brow("c05", "C-05 Unrated", "C-05"),
        ],
    )
    return CH


# ---------------------------------------------------------------- pathways (SPEC 3.8)
GAP_REF = re.compile(r"(?<![A-Za-z0-9])G(\d+)(?![0-9])")


def gap_refs(obj, first_new: int) -> set[str]:
    return {
        f"G{n}"
        for n in map(int, GAP_REF.findall(json.dumps(obj, ensure_ascii=False)))
        if n >= first_new
    }


def build_pathways(c: Ctx, modules: dict, blocks: dict, first_new_gap: int) -> dict:
    not_run = [
        "Deep Research (CP-DR): not run. No research questions were approved at Approval and the Source Pack has no fetched sources.",
        "What changed (CP-8): not run. No earlier RBOT Report on Caesars was offered as a Prior Case.",
    ]
    skip = c.gap_id(GAP_NOT_SHOWN)
    out = {}
    for key, label, nav_label, front_title, nav, has_fit, plan in PATHWAY_DEFS:
        folded = {"CP-5": "evidence"}
        if "CP-6" in plan:
            folded["CP-6"] = "portfolio-fit"
        cited: set[str] = set()
        for m in plan:
            if m in modules:
                cited |= {r for r in modules[m]["refs"] if int(r[1:]) >= first_new_gap}
                cited |= gap_refs(modules[m]["headline"], first_new_gap)
        for t in PATHWAY_TABLES[key]:
            if t not in blocks:
                raise BuildError(f"{key}: unknown block table {t}")
            cited |= gap_refs(blocks[t], first_new_gap)
        cited |= {c.gap_id(n) for n in PATHWAY_EXTRA_GAPS.get(key, [])}
        cited.discard(skip)
        lims = [
            {
                "ref": r,
                "field": c.gaps[r]["field"],
                "text": c.gaps[r]["reason"],
                "scope": "Source Pack gap",
            }
            for r in sorted(cited, key=lambda x: int(x[1:]))
        ]
        out[key] = {
            "key": key,
            "label": label,
            "navLabel": nav_label,
            "frontTitle": front_title,
            "nav": nav,
            "hasFit": has_fit,
            "plan": plan,
            "folded": folded,
            "notRun": not_run,
            "limitations": lims,
        }
    return out


# ---------------------------------------------------------------- illustrative registry
def text_of(cell) -> str:
    if isinstance(cell, dict):
        return str(
            cell.get("text") or cell.get("word") or cell.get("status") or cell.get("v") or ""
        )
    return str(cell)


def build_illustrative(c: Ctx, blocks: dict, fit: dict) -> dict:
    judgements: dict[str, list] = {}
    for bkey, tb in blocks.items():
        first = tb["columns"][0]["key"]
        recs = []
        for row in tb["rows"]:
            for k, cell in row.items():
                if isinstance(cell, dict) and cell.get("illustrative") is True:
                    rec = {"row": text_of(row.get(first)), "field": k, "illustrative": True}
                    if "word" in cell:
                        rec["word"] = cell["word"]
                        if cell.get("pos") is not None:
                            rec["pos"] = cell["pos"]
                    if "text" in cell:
                        rec["text"] = cell["text"]
                        rec["refs"] = cell.get("refs", [])
                    if "status" in cell:
                        rec["word"] = cell["status"]
                    recs.append(rec)
        if recs:
            judgements[bkey] = recs
    mult_refs = [c.ref("dr_merger_multiple"), c.ref("ev_multiple_ltm")]
    maint = [r for r in blocks["covenantTests"]["rows"] if r["type"] == "Maintenance"]
    prot = min(r["score"]["pos"] for r in blocks["protectionScore"]["rows"])
    press = max(blocks["maturityPressure"]["rows"], key=lambda r: r["pressure"]["pos"])["pressure"][
        "word"
    ]
    return {
        "_notice": "ILLUSTRATIVE. No RBOT run exists. These are analyst views written for the mockups, grounded in the cited figures.",
        "scenarioMultiples": {
            "downside": {
                "v": "5.0",
                "unit": "x",
                "prov": "illustrative",
                "illustrative": True,
                "refs": mult_refs,
                "label": "Downside EV multiple of EBITDA after rent",
            },
            "stress": {
                "v": "4.0",
                "unit": "x",
                "prov": "illustrative",
                "illustrative": True,
                "refs": mult_refs,
                "label": "Stress EV multiple of EBITDA after rent",
            },
        },
        "callBand": {
            "covenantTests": {
                "status": "Headroom",
                "sub": f"Maintenance, {len(maint)} tests",
                "illustrative": False,
                "refs": [c.ref("cov_tlr_headroom"), c.ref("cov_fccr_headroom")],
            },
            "lenderProtection": {
                **five_point(prot),
                "basis": "Weakest area of the protection score",
                "refs": [],
            },
            "refinancingPressure": {
                **scale_word("ordinal", press),
                "basis": "Highest year of the maturity pressure table",
                "refs": [c.ref("cr_liq_left_2028")],
            },
            "distressGate": {
                **blocks["distressGate"]["overall"],
                "refs": [c.ref("cr_runway_months")],
            },
            "priorCase": {
                "word": "No Prior Case",
                "na": True,
                "text": "No Prior Case was accepted at Approval; this is the first RBOT Report on Caesars.",
            },
            "fitSummary": {
                "text": "Proposed US$5.0m of the 6.50% secured 2032s Fits; loans and unrated notes Watch.",
                "synthetic": True,
            },
        },
        "judgements": judgements,
    }


# ---------------------------------------------------------------- assembly
def build(data_path: Path, extract_path: Path) -> tuple[Ctx, dict, dict]:
    base = load_data_js(data_path)
    extract = json.loads(extract_path.read_text(encoding="utf-8"))
    c = Ctx(base, extract)
    c.verify_and_register(Path(extract["corpus"]))
    first_new_gap = c._next["G"]
    c.register_gaps()
    calcs_earnings(c)
    calcs_rv_dq(c)
    calcs_liquidity(c)
    calcs_covenants(c)
    calcs_distress(c)
    calcs_fit(c)
    fit = build_fit(c)
    nav_ids = {m for p in PATHWAY_DEFS for m in p[4]}
    modules = build_modules(c, nav_ids)
    blocks = build_blocks(c, fit)
    charts = build_charts(c, fit)
    pathways = build_pathways(c, modules, blocks, first_new_gap)
    illustrative = build_illustrative(c, blocks, fit)
    x = {
        "meta": {
            "builtBy": "build-fp-data.py",
            "pathwayKeys": [p[0] for p in PATHWAY_DEFS],
            "counts": {
                "citations": sum(1 for k in c.cit if k.startswith("C")),
                "synthetic": sum(1 for k in c.cit if k.startswith("S")),
                "calcs": len(c.calcs),
                "gaps": len(c.gaps),
                "blocks": len(blocks),
                "charts": len(charts),
                "pathways": len(pathways),
            },
        },
        "citations": c.cit,
        "calcs": c.calcs,
        "gaps": c.gaps,
        "figures": c.fig,
        "modules": modules,
        "blocks": blocks,
        "charts": charts,
        "fit": fit,
        "illustrative": illustrative,
        "pathways": pathways,
    }
    return c, x, base


MERGE_JS = """(function () {
  var D = window.RBOT_DATA, X = window.RBOT_FP;
  if (!D) throw new Error("fp-data.js: load ../shared/data.js first");
  var kinds = ["citations", "calcs", "gaps", "figures"];
  kinds.forEach(function (k) {
    Object.keys(X[k]).forEach(function (id) {
      if (Object.prototype.hasOwnProperty.call(D[k], id)) throw new Error("fp-data.js: RBOT_DATA." + k + "." + id + " already exists");
    });
  });
  kinds.forEach(function (k) {
    Object.keys(X[k]).forEach(function (id) { D[k][id] = X[k][id]; });
  });
})();
"""


def render(x: dict) -> str:
    head = "/* Generated by build-fp-data.py from ../shared/data.js and fp-extract.json. Do not edit by hand. */\n"
    return (
        head + "window.RBOT_FP = " + json.dumps(x, ensure_ascii=False, indent=1) + ";\n" + MERGE_JS
    )


# ---------------------------------------------------------------- self-check (SPEC 3.7)
def walk(obj, path=""):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")


def numeric_looking(v) -> bool:
    if not isinstance(v, str):
        return isinstance(v, int | float)
    try:
        dec(v)
    except BuildError:
        return False
    return True


def run_checks(c: Ctx, x: dict, base: dict) -> list[str]:
    bad: list[str] = []
    for key, exp in EXPECTED.items():
        f = c.fig.get(key)
        if f is None:
            bad.append(f"{key}: not built")
        elif f["v"] != exp:
            bad.append(f"{key}: expected {exp}, got {f['v']}")
    insts = {i["key"]: i for i in x["fit"]["instruments"]}
    for key, (verdict, size, pos) in EXPECTED_FIT.items():
        i = insts.get(key)
        if i is None:
            bad.append(f"fit {key}: missing")
            continue
        if i["verdict"] != verdict:
            bad.append(f"fit {key}: verdict {i['verdict']}, expected {verdict}")
        if size and i["maxSize"]["v"] != size:
            bad.append(f"fit {key}: max size {i['maxSize']['v']}, expected {size}")
        if i["final"]["pos"] != pos:
            bad.append(f"fit {key}: final position {i['final']['pos']}, expected {pos}")
    if insts["sn_2029"]["maxSize"]["v"] != "883,300" or insts["sn_2029"]["bindingLimit"] != "C-04":
        bad.append("fit sn_2029: expected max 883,300 under C-04")
    if insts["ssn_2032"]["bindingLimit"] != "C-01":
        bad.append("fit ssn_2032: expected C-01 binding")
    if not x["fit"]["proposed"]["withinMaxSize"]:
        bad.append("fit: the proposed US$5,000,000 exceeds the 6.50% SSN 2032 max size")
    if c.verified != len(c.extract["items"]):
        bad.append("fewer excerpts verified than items")
    first = {"C": min((k for k in c.cit if k.startswith("C")), key=lambda k: int(k[1:])), "S": None}
    if first["C"] != "C338":
        bad.append(f"first new citation is {first['C']}, expected C338")
    if "S46" not in c.cit:
        bad.append("S46 missing")
    if "K110" not in c.calcs or c.calcs["K110"]["key"] != "eu_rev_chg_q2":
        bad.append("K110 is not eu_rev_chg_q2")
    if "G29" not in c.gaps or c.gaps["G29"]["field"] != NEW_GAPS[0][1]:
        bad.append("G29 is not the first new gap")
    for kind in ("citations", "calcs", "gaps", "figures"):
        for k in x[kind]:
            if k in base[kind]:
                bad.append(f"{kind}.{k} overwrites RBOT_DATA")
    shown = {k: v for k, v in x.items() if k not in ("citations", "calcs", "gaps", "figures")}
    for path, o in walk(shown):
        if isinstance(o, dict) and o.get("prov") == "gap" and numeric_looking(o.get("v")):
            bad.append(f"{path}: a gap Datum carries a numeric value {o['v']!r}")
        if isinstance(o, dict) and isinstance(o.get("ref"), str) and FINAL_ID.match(o["ref"]):
            if not c.known_ref(o["ref"]):
                bad.append(f"{path}: unknown ref {o['ref']}")
        if isinstance(o, str):
            for m in TOKEN.finditer(o):
                tok = m.group(1) or m.group(3)
                if not FINAL_ID.match(tok):
                    bad.append(f"{path}: unresolved token {m.group(0)!r}")
                elif not c.known_ref(tok):
                    bad.append(f"{path}: token {m.group(0)!r} names an unknown reference")
    for key, p in x["pathways"].items():
        for m in p["nav"]:
            if m not in x["modules"]:
                bad.append(f"{key}: nav module {m} is not defined")
            elif len(x["modules"][m]["name"]) > 20:
                bad.append(f"{m}: name longer than 20 characters")
    for tb_key, tb in x["blocks"].items():
        keys = {col_["key"] for col_ in tb["columns"]}
        for i, row in enumerate(tb["rows"]):
            for k in row:
                if k not in keys and k not in ("summary", "kind", "illustrative", "note", "tag"):
                    bad.append(f"blocks.{tb_key}.rows[{i}]: key {k} is not a column")
    return bad


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    check = "--check" in argv
    data = Path(args[0]) if args else DEFAULT_DATA
    extract = Path(args[1]) if len(args) > 1 else DEFAULT_EXTRACT
    try:
        c, x, base = build(data, extract)
    except BuildError as exc:
        print(f"build-fp-data: {exc}", file=sys.stderr)
        return 1
    if check:
        bad = run_checks(c, x, base)
        if bad:
            print(f"build-fp-data --check: {len(bad)} failure(s)", file=sys.stderr)
            for b in bad:
                print(f"  - {b}", file=sys.stderr)
            return 1
        m = x["meta"]["counts"]
        print(
            f"build-fp-data --check OK: {c.verified} excerpts verified, {m['citations']} citations, {m['synthetic']} synthetic, "
            f"{m['calcs']} calcs, {m['gaps']} gaps, {m['blocks']} blocks, {m['charts']} charts, {m['pathways']} pathways; "
            f"{len(EXPECTED)} expected values and {len(EXPECTED_FIT)} Fit rows match"
        )
        return 0
    OUT.write_text(render(x), encoding="utf-8")
    print(f"wrote {OUT.name}: {len(c.cit)} citations, {len(c.calcs)} calcs, {len(c.gaps)} gaps")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
