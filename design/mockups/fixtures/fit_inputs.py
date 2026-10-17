"""Instruments for Portfolio Fit, read from the built handoffs (CP-1 identity and facilities, CP-1A profile, Run Brief tranches)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from core import GAP, MCTX, Ctx, FixtureError, Handoff, q

LOAN_TYPES = ("RCF", "1L Term Loan", "2L Term Loan")


def _tenor(maturity: str, as_of: str) -> Decimal:
    if maturity == GAP:
        return Decimal(0)
    return q(
        MCTX.divide(
            Decimal((date.fromisoformat(maturity) - date.fromisoformat(as_of)).days),
            Decimal("365.25"),
        ),
        2,
    )


def _bucket(debt_type: str, secured: bool, seniority: str = "") -> str:
    if debt_type.startswith("2L") or "second lien" in seniority.lower():
        return "Second lien"
    return "First lien" if secured else "Unsecured"


def fit_instruments(
    ctx: Ctx,
    run_id: str,
    handoffs: dict[str, Handoff],
    run_brief: Handoff,
    exclude: tuple[str, ...] = (),
) -> list[dict]:
    cp1, cp1a = handoffs.get("CP-1"), handoffs.get("CP-1A")
    if cp1 is None or cp1a is None:
        raise FixtureError("Fit instruments need CP-1 and CP-1A")
    prof = cp1a.rows("snapshot.company_profile")[0]
    as_of = cp1.analysis_date
    facs = {r["facility_id"]: r for r in cp1.rows("cp1.debt_facility_register")}  # last period wins
    out: list[dict] = []
    for r in cp1.rows("cp1.instrument_identity"):
        fid = r["facility_id"]
        if fid in exclude or fid not in facs:
            continue
        f = facs[fid]
        rating = next(
            (r[k] for k in ("rating_moodys", "rating_sp", "rating_fitch") if r[k] != GAP), None
        )
        out.append(
            {
                "facility_id": fid,
                "instrument": r["instrument_name"],
                "rating": rating,
                "sector": prof["sector"],
                "country": prof["country"],
                "asset_type": "Loan" if r["debt_type"] in LOAN_TYPES else "Bond",
                "seniority": _bucket(
                    r["debt_type"], f["secured_status"] == "SECURED", f["seniority"]
                ),
                "currency": f["currency"],
                "maturity": str(_tenor(f.get("maturity_date", GAP), as_of)),
            }
        )
    if run_brief.rows("snapshot.run_header")[0]["primary"] == "Yes":
        for t in run_brief.rows("snapshot.transaction_summary"):
            tid = t["tranche_id"]
            if tid in exclude:
                continue
            out.append(
                {
                    "facility_id": tid,
                    "instrument": t["instrument"],
                    "rating": None,
                    "expected_rating": t.get("expected_ratings", GAP),
                    "sector": prof["sector"],
                    "country": prof["country"],
                    "asset_type": "Loan" if t["debt_type"] in LOAN_TYPES else "Bond",
                    "seniority": _bucket(
                        t["debt_type"], t["debt_type"] in ("1L Term Loan", "SS Notes", "RCF")
                    ),
                    "currency": t["currency"],
                    "maturity": str(_tenor(t["maturity_date"], as_of)),
                }
            )
    return out
