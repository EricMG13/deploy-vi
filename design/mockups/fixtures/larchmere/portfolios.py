"""Larchmere portfolio: a synthetic CLO book (Fenwick Park CLO Ltd, fictional) holding 2.8% of NAV in the first-lien loan."""

from __future__ import annotations

from core import Ctx, plain

from . import facts as F


def synthetic_clo(ctx: Ctx) -> dict:
    """Prepared `rbot-portfolio/1`: 11.2m par of the term loan B on a 400m NAV against a 2.5% Hard single-issuer limit."""
    p = F.val("portfolio")
    src = "FENWICK_CLO_Indenture_Limits_2026-09-30.txt"

    def lim(
        limit_id: str,
        category: str,
        parameter: str,
        scope: str,
        scope_value,
        value,
        kind: str,
        current,
        section: str,
        unit: str = "pct_nav",
    ) -> dict:
        return {
            "limit_id": limit_id,
            "category": category,
            "parameter": parameter,
            "scope": scope,
            "scope_value": scope_value,
            "limit_value": plain(value),
            "unit": unit,
            "limit_kind": kind,
            "current_value": None if current is None else plain(current),
            "source": f"{src}, {section}",
        }

    limits = [
        lim(
            "L-01",
            "Concentration",
            "Max single issuer exposure",
            "issuer",
            None,
            p["single_issuer_limit"],
            "Hard",
            None,
            "section 7.1(a)",
        ),
        lim(
            "L-02",
            "Quality",
            "Max CCC and below",
            "rating_bucket",
            ["CCC"],
            p["ccc_limit"],
            "Hard",
            p["ccc_current"],
            "section 7.2",
        ),
        lim(
            "L-03",
            "Quality",
            "Max second lien and unsecured",
            "seniority",
            ["Second lien", "Unsecured"],
            p["second_lien_limit"],
            "Soft",
            p["second_lien_current"],
            "section 7.3",
        ),
        lim(
            "L-04",
            "Concentration",
            "Max single sector: Gaming, Lodging & Leisure",
            "sector",
            "Gaming, Lodging & Leisure",
            p["sector_limit"],
            "Hard",
            p["sector_current"],
            "section 7.4",
        ),
        {
            **lim(
                "L-05",
                "Portfolio test",
                "Maximum weighted average rating factor",
                "other",
                None,
                2800,
                "Hard",
                None,
                "section 8.1",
                "factor",
            ),
            "current_value": "2650",
            "headroom": "150",
        },
        {
            **lim(
                "L-06",
                "Portfolio test",
                "Minimum weighted average spread (%)",
                "other",
                None,
                3.6,
                "Soft",
                None,
                "section 8.2",
                "pct",
            ),
            "current_value": "3.85",
            "headroom": "0.25",
        },
    ]
    return {
        "schema": "rbot-portfolio/1",
        "portfolio_id": p["id"],
        "portfolio_name": p["name"],
        "strategy": "CLO",
        "as_of": "2026-09-30",
        "nav": plain(p["nav"]),
        "par": plain(p["par"]),
        "currency": "USD",
        "unit": "UNITS",
        "positions": [
            {"issuer_id": F.ISSUER_ID, "instrument": "llg_tlb", "par": plain(p["position_par"])},
            {
                "issuer_id": "OTHER-ISSUERS-AGGREGATE",
                "instrument": "all other positions",
                "par": plain(p["par"] - p["position_par"]),
            },
        ],
        "limits": limits,
        "unparsed": [],
        "notes": [
            "Synthetic test portfolio (fictional CLO). The only position in the issuer is 11.2m par of the first-lien term loan B, 2.8% of NAV. L-01 is tested on the issuer's own exposure."
        ],
    }
