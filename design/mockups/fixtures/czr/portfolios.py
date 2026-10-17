"""The prepared Indexed HY portfolio for the Portfolio Decision run (`czr.portfolios:indexed_hy`).

Positions are real: the four Caesars bonds held by the Federated Hermes Sustainable High Yield Bond Fund at 30 June 2026
(N-PORT schedule in the pack, values in US$). NAV, par and the three limits are synthetic (`synthetic-facts.json ->
czr.indexed_hy_book`): the single-issuer limit leaves every Caesars instrument at most Watch, and the CCC bucket is
already over its Hard limit (12.1% against 12.0%), so a CCC-rated Caesars instrument Breaches and is capped at Avoid.
Test CLO I is the library's `test_clo_i`.

Exposure is the position's market value in US$ millions (the single-issuer limit is a percentage of NAV, and NAV is a
market value), so `par` on each position holds that market value.
"""

from __future__ import annotations

from core import Ctx, D, plain
from czr.cp_3 import FACTS

NPORT = "FHSUHY_NPORT_Schedule_of_Investments_2026-06-30.txt"
CZR_LINES = [  # (needle, name) of the four Caesars lines in the N-PORT schedule
    (
        "Caesars Entertainment, Inc., 144A, 6.000%, 10/15/2032 | ",
        "Caesars Entertainment, Inc. 6.000% 144A due 10/15/2032",
    ),
    (
        "Caesars Entertainment, Inc., Sr. Secd. Note, 144A, 6.500%, 2/15/2032 | ",
        "Caesars Entertainment, Inc. 6.500% Senior Secured Note due 2/15/2032",
    ),
    (
        "Caesars Entertainment, Inc., Sr. Secd. Note, 144A, 7.000%, 2/15/2030 | ",
        "Caesars Entertainment, Inc. 7.000% Senior Secured Note due 2/15/2030",
    ),
    (
        "Caesars Entertainment, Inc., Sr. Unsecd. Note, 144A, 4.625%, 10/15/2029 | ",
        "Caesars Entertainment, Inc. 4.625% Senior Unsecured Note due 10/15/2029",
    ),
]


def _read_positions(ctx: Ctx) -> list[dict]:
    out = []
    for needle, name in CZR_LINES:
        line = ctx.find_line(NPORT, needle)
        text = ctx.corpus_lines(NPORT)[line - 1]
        parts = [c.strip() for c in text.split(" | ")]
        face, value = (int(parts[i].replace("$", "").replace(",", "").strip()) for i in (0, -1))
        out.append(
            {
                "issuer_id": "CZR",
                "instrument": name,
                "face_usd": str(face),
                "market_value_usd": str(value),
                "par": plain(D(value) / D(1_000_000), 6),
                "source": f"{NPORT}, line {line}",
            }
        )
    return out


def indexed_hy(ctx: Ctx) -> dict:
    """Prepared `rbot-portfolio/1` for the Test Indexed HY I book."""
    book = FACTS["indexed_hy_book"]
    limits = []
    for lim in book["limits"]:
        row = {
            "limit_id": lim["limit_id"],
            "category": lim["category"],
            "parameter": lim["parameter"],
            "scope": lim["scope"],
            "scope_value": lim.get("scope_value"),
            "limit_value": lim["limit_value"],
            "unit": lim["unit"],
            "limit_kind": lim["limit_kind"],
            "current_value": lim.get("current_value"),
            "source": "synthetic-facts.json#czr.indexed_hy_book",
        }
        if lim["scope"] == "sector":
            row["scope_value"] = "Leisure Facilities & Services"
        limits.append(row)
    return {
        "schema": "rbot-portfolio/1",
        "portfolio_id": book["portfolio_id"],
        "portfolio_name": book["portfolio_name"],
        "strategy": book["strategy"],
        "as_of": "2026-06-30",
        "nav": book["nav"],
        "par": book["par"],
        "currency": book["currency"],
        "unit": book["unit"],
        "positions": _read_positions(ctx),
        "limits": limits,
        "unparsed": [],
        "notes": [
            "Synthetic limits on the real Caesars positions of the Federated Hermes Sustainable High Yield Bond Fund (N-PORT, 30 June 2026). "
            + book["note"]
        ],
    }
