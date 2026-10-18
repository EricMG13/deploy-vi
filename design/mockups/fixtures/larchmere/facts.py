"""Larchmere Leisure Group (fictional): the single source of every input value, each with a one-sentence rationale.

Everything here is invented for design; none of it is a fact about any real company. Content modules never type a
Larchmere input anywhere else: they read `val(key)` and cite the fact through `syn(handoff, key)`, which writes the
synthetic citation row (`fixtures/larchmere/facts.py#<key>`). Derived figures are computed in the modules (and in
`derived.py`) with the lib's Decimal helpers from these inputs. Money is USD millions unless a key says otherwise.
"""

from __future__ import annotations

import re
from typing import Any, NamedTuple

ISSUER = "Larchmere Leisure Group, Inc. (fictional)"
ISSUER_SHORT = "Larchmere Leisure Group (fictional)"
ISSUER_ID = "LLG-FICTIONAL"
SPONSOR = "Quillon Ridge Partners (fictional)"
LANDLORD = "Brightwater Gaming Properties Trust (fictional)"
OPCO = "Larchmere Operating Company, LLC (fictional)"
AS_OF = "2026-10-02"
REPORT_DATE = "2026-10-17"
ANALYST = "Credit Research (design fixture)"
OBJECTIVE = "Assess Larchmere's restructuring options, recoveries and the fulcrum security"

FLOW_PERIODS = ["FY2023", "FY2024", "FY2025", "H1_2025", "H1_2026"]
BALANCE_PERIODS = ["FY2023_END", "FY2024_END", "FY2025_END", "JUN30_2026"]
FACILITY_IDS = ["llg_rcf", "llg_tlb", "llg_2l", "llg_notes"]


class Fact(NamedTuple):
    value: Any
    why: str


FACTS: dict[str, Fact] = {}


def _f(key: str, value: Any, why: str) -> None:
    if "\n" in why or key in FACTS:
        raise ValueError(f"bad fact {key}")
    FACTS[key] = Fact(value, why)


def val(key: str) -> Any:
    return FACTS[key].value


def syn(h: Any, key: str) -> str:
    """Cite fact `key` in handoff `h` as a synthetic citation; returns the '[C<n>]' marker."""
    return h.cite_synthetic(key, FACTS[key].why, ISSUER_SHORT, file="larchmere/facts.py")


_NUM = re.compile(r"(?<![\d.,\w])(\d{4,})(\.\d+)?(?!\d)")


def prose(text: str) -> str:
    """Thousands separators for figures of four or more digits in prose (years and table cells are left alone)."""

    def sub(m: re.Match[str]) -> str:
        whole, frac = m.group(1), m.group(2) or ""
        if not frac and 1900 <= int(whole) <= 2100:
            return m.group(0)
        return f"{int(whole):,}{frac}"

    return _NUM.sub(sub, text)


def series(_unused: str, periods: list[str], values: list[Any]) -> dict[str, Any]:
    return dict(zip(periods, values, strict=True))


# ------------------------------------------------------------------ income and cash-flow series (USD m)
_f(
    "revenue",
    series("r", FLOW_PERIODS, [1684, 1601, 1492, 756, 676]),
    "A regional operator losing share to newer competitors would show revenue falling about 5-7% a year, with the first half of 2026 down 11% on 2025.",
)
_f(
    "adjusted_ebitda",
    series("a", FLOW_PERIODS, [298, 271, 241, 124, 93]),
    "Operating deleverage on falling revenue takes company-defined Adjusted EBITDA down 25% in the first half of 2026 and leaves about 210 for the LTM.",
)
_f(
    "d_and_a",
    series("d", FLOW_PERIODS, [108, 106, 104, 52, 53]),
    "A flat 11-property asset base depreciates at roughly 7% of revenue, close to 105 a year.",
)
_f(
    "addback_restructuring",
    series("b", FLOW_PERIODS, [6, 9, 14, 5, 13]),
    "Advisory and restructuring costs rise as the company prepares for a negotiation, and recur for a third year.",
)
_f(
    "addback_sponsor_fee",
    series("b", FLOW_PERIODS, [5, 5, 5, 3, 3]),
    "A sponsor monitoring fee of about 5 a year is typical of a 2022 sponsor buyout of this size.",
)
_f(
    "addback_run_rate_savings",
    series("b", FLOW_PERIODS, [0, 8, 12, 5, 9]),
    "Run-rate cost savings announced but not yet delivered are the usual unrealized add-back, growing as the business shrinks.",
)
_f(
    "interest_expense",
    series("i", FLOW_PERIODS, [196, 212, 221, 109, 118]),
    "Interest expense of about 230 LTM covers about 147 of cash interest on debt, 62 of lease financing interest and 21 of non-cash accretion and fee amortisation.",
)
_f(
    "cash_interest",
    series("c", FLOW_PERIODS, [121, 136, 141, 70, 76]),
    "Cash interest rises with the revolver draw and floating rates on 1,500 of floating-rate debt.",
)
_f(
    "lease_cash",
    series("l", FLOW_PERIODS, [58, 60, 61, 30, 31]),
    "Master-lease rent escalates about 1.5% a year from a base near 58.",
)
_f(
    "cash_taxes",
    series("t", FLOW_PERIODS, [9, 7, 4, 2, 1]),
    "Falling taxable income leaves only state and gaming taxes in cash taxes.",
)
_f(
    "cfo",
    series("o", FLOW_PERIODS, [98, 49, 14, 14, -21]),
    "Operating cash flow after interest, rent and working capital turns negative in the first half of 2026 as EBITDA falls below fixed charges.",
)
_f(
    "capex",
    series("x", FLOW_PERIODS, [66, 58, 49, 24, 21]),
    "Capital spending has been cut from 66 to about 46 LTM, close to maintenance level for eleven properties.",
)

# ------------------------------------------------------------------ balance sheet and liquidity (period-end)
_f(
    "cash_balance",
    series("c", BALANCE_PERIODS, [131, 96, 54, 62]),
    "Unrestricted cash falls from 131 to the mid-fifties and is topped up to 62 by the revolver draw in the first half of 2026.",
)
_f(
    "rcf_drawn",
    series("d", BALANCE_PERIODS, [60, 110, 150, 200]),
    "The revolver is drawn in steps to fund the cash burn and is fully drawn at 30 June 2026, which is what springs the leverage covenant.",
)
_f(
    "undrawn_rcf",
    series("u", BALANCE_PERIODS, [140, 90, 50, 0]),
    "Undrawn availability is the 200 commitment less the draws, so none is left at 30 June 2026.",
)
_f(
    "financing_obligations",
    series("f", BALANCE_PERIODS, [1164, 1158, 1152, 1149]),
    "The master-lease financing obligation is a capitalised rent stream of about 62 a year, accreting slowly at a rate near the implied lease rate.",
)
_f(
    "term_debt_face",
    {"llg_tlb": 1050, "llg_2l": 250, "llg_notes": 200},
    "The brief fixes the term loan B at 1,050, the second-lien term loan at 250 and the unsecured notes at 200, all unchanged since the 2022 buyout financing.",
)
_f(
    "rcf_commitment",
    200,
    "A 200 revolver is typical for a 210 EBITDA operator and is the 'fully drawn' figure the brief fixes.",
)
_f(
    "carrying_discount_pct",
    {"llg_rcf": 0, "llg_tlb": 1.3, "llg_2l": 1.6, "llg_notes": 1.5},
    "Unamortised issue discount and deferred fees leave carrying value 1.3% to 1.6% under face on the term debt.",
)
_f(
    "facility_terms",
    {
        "llg_rcf": dict(
            name="Revolving Credit Facility",
            ftype="Revolving credit",
            sec="SECURED",
            sen="Senior secured first lien",
            dt="RCF",
            spread=400,
            floor=75,
            maturity="2028-03-15",
            margin="Term SOFR (0.75% floor) + 4.00%",
        ),
        "llg_tlb": dict(
            name="First-Lien Term Loan B",
            ftype="Term loan",
            sec="SECURED",
            sen="Senior secured first lien",
            dt="1L Term Loan",
            spread=450,
            floor=75,
            maturity="2028-09-30",
            margin="Term SOFR (0.75% floor) + 4.50%",
            amort_pct=1,
            original=1050,
        ),
        "llg_2l": dict(
            name="Second-Lien Term Loan",
            ftype="Term loan",
            sec="SECURED",
            sen="Second lien secured",
            dt="2L Term Loan",
            spread=850,
            floor=100,
            maturity="2029-03-31",
            margin="Term SOFR (1.00% floor) + 8.50%",
        ),
        "llg_notes": dict(
            name="8.25% Senior Notes due 2029",
            ftype="Senior notes",
            sec="UNSECURED",
            sen="Senior unsecured",
            dt="SU Notes",
            fixed="8.25",
            maturity="2029-09-15",
            margin="8.25% fixed",
        ),
    },
    "Terms follow a 2022 sponsor buyout financing: a first-lien revolver and term loan B maturing in 2028, a second-lien term loan a half-year later and 2029 unsecured notes.",
)

# ------------------------------------------------------------------ segments and operating KPIs
_f(
    "segment_revenue",
    {
        "seg_gulf_coast": ("Gulf Coast", 1, [812, 781, 727, 369, 327]),
        "seg_mid_south": ("Mid-South", 2, [689, 640, 591, 301, 266]),
        "seg_online": ("Online", 3, [183, 180, 174, 86, 83]),
    },
    "Segment revenue is split 49% Gulf Coast, 39% Mid-South and 12% Online by LTM and sums exactly to each period's consolidated revenue.",
)
_f(
    "operating_kpis",
    {
        "gc_occupancy": ("Gulf Coast hotel occupancy", "%", "RATE", [87.4, 84.9, 81.2, 80.6, 76.8]),
        "ms_slot_win": (
            "Mid-South slot win per unit per day",
            "USD",
            "RATE",
            [188, 181, 172, 171, 163],
        ),
        "gc_slot_win": (
            "Gulf Coast slot win per unit per day",
            "USD",
            "RATE",
            [214, 205, 194, 193, 181],
        ),
        "online_actives": (
            "Online monthly active players",
            "thousand",
            "RATE",
            [212, 205, 197, 199, 192],
        ),
    },
    "Occupancy near 81%, slot win near 170-195 a day and about 200 thousand online players are ordinary for four-state regional operations and fall with revenue.",
)
_f(
    "operating_counts",
    {
        "properties": ("Properties", 11),
        "slots": ("Slot machines", 9420),
        "tables": ("Table games", 236),
        "rooms": ("Hotel rooms", 6310),
    },
    "Eleven properties with about 9,400 slots, 240 tables and 6,300 rooms give the scale of a regional operator with US$1.4bn of revenue.",
)

# ------------------------------------------------------------------ ratings, identity, profile
_f(
    "ratings",
    {
        "moodys": ("Caa2", "Negative", "2026-07-21", "Caa1"),
        "sp": ("CCC", "Negative", "2026-08-04", "CCC+"),
        "facility": {
            "llg_rcf": ("Caa1", "CCC+"),
            "llg_tlb": ("Caa1", "CCC+"),
            "llg_2l": ("Caa3", "CCC-"),
            "llg_notes": ("Ca", "CC"),
        },
    },
    "A 8x levered operator with a missed coupon would carry Caa2 / CCC corporate ratings on negative outlooks, with the junior tranches notched down.",
)
_f(
    "identifiers",
    {
        "llg_rcf": ("BBGLLG0001", "—"),
        "llg_tlb": ("BBGLLG0002", "—"),
        "llg_2l": ("BBGLLG0003", "—"),
        "llg_notes": ("BBGLLG0004", "LLG000AA1"),
    },
    "Invented identifiers in a clearly artificial range, so none resolves to a real instrument.",
)
_f(
    "profile",
    {
        "sector": "Gaming, Lodging & Leisure",
        "country": "United States",
        "shareholders": f"{SPONSOR} funds 88%; management 12%",
        "management": "Dana Whitcombe (CEO, fictional); Rafael Okonkwo (CFO, fictional)",
        "states": "Louisiana, Mississippi, Missouri, Indiana",
    },
    "A sponsor-held operator with eleven properties in four states is the profile the brief fixes; the officers are invented.",
)

# ------------------------------------------------------------------ market (CP-3, CP-3D) and covenant (CP-4)
_f(
    "quotes",
    {"llg_tlb": 74, "llg_2l": 41, "llg_notes": 23},
    "Dealer quotes of 74, 41 and 23 are the levels the brief fixes for a 1L loan, 2L loan and unsecured notes of an operator with an unresolved liquidity gap.",
)
_f(
    "bid_ask_width",
    {"llg_tlb": 1, "llg_2l": 2, "llg_notes": 2},
    "A one- to two-point bid-ask spread is typical for distressed loans and bonds from a single dealer.",
)
_f(
    "sofr_spot",
    3.85,
    "A 3.85% Term SOFR is a plausible level for late 2026 and is the starting point of the rate deck.",
)
_f(
    "rate_deck",
    {"BASE": [3.85, 3.60, 3.50], "DOWNSIDE": [4.35, 4.10, 4.00]},
    "A gently falling base deck and a downside deck 50 basis points higher bracket the rate path.",
)
_f(
    "risk_free_3y",
    3.90,
    "A 3.90% three-year government yield is the reference for the spread-to-worst on the notes.",
)
_f(
    "covenants",
    {
        "test_date": "2026-06-30",
        "fl_threshold": 6.5,
        "min_liquidity": 50,
        "min_ebitda": 120,
        "rcf_use_trigger_pct": 35,
        "cert_delivered": "2026-09-21",
        "cure_deadline": "2026-10-19",
    },
    "A springing 6.50x first-lien net leverage test, a US$50m minimum liquidity floor and a US$120m minimum covenant EBITDA are standard for a sponsor revolver; the cure window runs 28 days from a late certificate.",
)
_f(
    "baskets",
    {
        "free_and_clear_floor": 110,
        "free_and_clear_pct": 80,
        "lien_floor": 80,
        "lien_pct": 55,
        "lien_used": 28,
        "unrestricted_investment_floor": 120,
        "unrestricted_investment_pct": 80,
        "unrestricted_investment_used": 0,
        "rp_floor": 60,
        "rp_pct": 40,
        "rp_used": 21,
    },
    "Greater-of baskets of a fixed amount and a percentage of Consolidated EBITDA are market for a 2022 sponsor deal, with modest past use of the lien and restricted-payment baskets.",
)
_f(
    "rent_in_covenant_ebitda",
    True,
    "Consolidated EBITDA is stated after cash rent under the master lease, which is how rent-burdened casino credits usually define covenant EBITDA.",
)
_f(
    "distress_events",
    {
        "coupon_due": "2026-09-15",
        "grace_end": "2026-10-15",
        "coupon_amount_note": "semi-annual interest on the 8.25% notes",
        "ae_proposal": "2026-09-22",
        "advisers_hired": "2026-08-18",
        "ratings_actions": "2026-07-21 and 2026-08-04",
    },
    "A 15 September coupon missed with a 30-day grace period ending 15 October is the event the brief fixes, with advisers hired in August and a sponsor proposal in late September.",
)

# ------------------------------------------------------------------ forward view (CP-2D, CP-2G)
_f(
    "forward_12m",
    {
        "adjusted_ebitda": 168,
        "wc_change": -5,
        "cash_taxes": 2,
        "maintenance_capex": 40,
        "growth_capex": 12,
        "advisers": 12,
        "rent_escalator_pct": 1.5,
        "cage_cash": 41,
    },
    "A 168 forward EBITDA lies between the FY2026E and FY2027E base-case values that CP-2G projects; the other lines are the usual restructuring-year cash uses.",
)
_f(
    "segment_growth",
    {
        "BASE": {
            "seg_gulf_coast": [-6.0, -4.0, -2.0],
            "seg_mid_south": [-4.5, -3.5, -1.5],
            "seg_online": [-1.0, 0.0, 1.5],
        },
        "DOWNSIDE": {
            "seg_gulf_coast": [-10.0, -8.0, -5.0],
            "seg_mid_south": [-9.0, -7.0, -4.0],
            "seg_online": [-4.0, -3.0, -1.0],
        },
    },
    "Gulf Coast carries the most competitive supply, so it falls fastest in both cases; the downside deepens every segment's decline.",
)
_f(
    "projection_drivers",
    {
        "BASE": dict(
            margin=[13.0, 12.2, 12.0], capex_pct=[3.0, 3.0, 3.0], taxes=[2, 2, 2], wc=[-5, -4, -2]
        ),
        "DOWNSIDE": dict(
            margin=[11.5, 9.8, 9.0], capex_pct=[2.6, 2.4, 2.4], taxes=[1, 1, 1], wc=[-12, -8, -4]
        ),
    },
    "Margins fall about 70 basis points a year in the base case and by nearly twice that in the downside, with working capital turning against the company as suppliers tighten terms.",
)
_f(
    "projection_floor",
    {"min_cash": 50, "years": [2026, 2027, 2028], "tlb_amort": {2026: 5.25, 2027: 10.5, 2028: 0}},
    "Projections hold the US$50m liquidity floor, amortise the term loan B from September 2026 and leave the 2028 maturities unrefinanced.",
)

# ------------------------------------------------------------------ restructuring (CP-4C, CP-3C)
_f(
    "claims_other",
    {"admin": 40, "trade": 62},
    "Administrative and priority claims of 40 and trade and other unsecured claims of 62 are ordinary for a business with US$1.4bn of revenue.",
)
_f(
    "ev_multiples",
    {"low": 5.5, "base": 7.25, "high": 8.5},
    "Going-concern multiples of 5.5x, 7.25x and 8.5x of LTM EBITDA bracket regional gaming transactions with part of the real estate owned.",
)
_f(
    "liquidation",
    {"asset_value": 1180, "haircut_pct": 40},
    "Appraised property, equipment and licences of 1,180 less a 40% forced-sale discount give the liquidation floor.",
)
_f(
    "ev_probabilities",
    {"low": 30, "base": 50, "high": 10, "liquidation": 10},
    "A 50% weight on the base case and 30% on the stress case reflects an analyst view that negotiation outcomes cluster around the mid-case.",
)
_f(
    "new_money",
    {
        "size": 150,
        "spread_low": 950,
        "spread_mid": 1000,
        "spread_high": 1050,
        "oid": 96,
        "maturity": "2030-09-30",
        "talk_date": "2026-09-30",
        "tranche_id": "NEW-1",
        "instrument": "Super-Priority Priming Term Loan (sponsor new money)",
        "expected_ratings": "B3 / B-",
    },
    "A 150 super-priority first-out term loan from the sponsor at SOFR + 950 to 1,050 with a 96 OID and a B3 / B- expected rating is what a sponsor-proposed priming rescue of this size would carry.",
)
_f(
    "recoveries_market",
    {"llg_tlb": 65, "llg_2l": 25, "llg_notes": 10},
    "Market-implied recovery assumptions of 65%, 25% and 10% by class are conventional for first lien, second lien and unsecured debt in a distressed casino credit.",
)
_f(
    "peers",
    {
        "loan_index": dict(
            block="Loan index",
            name="CCC loan index (synthetic)",
            ratings="CCC",
            price=72.5,
            spread=1305,
            chg_1m=-2.5,
            chg_ytd=-14.0,
            coupon="—",
            maturity="—",
        ),
        "loan_peer_c": dict(
            block="Loan comparable",
            name="Peer C (synthetic) Term Loan B",
            ratings="Caa1 / CCC+",
            price=78.5,
            spread=1085,
            chg_1m=-1.5,
            chg_ytd=-9.0,
            coupon="S+425",
            maturity="2028-12-31",
        ),
        "loan_peer_d": dict(
            block="Loan comparable",
            name="Peer D (synthetic) Term Loan B",
            ratings="Caa2 / CCC",
            price=69.0,
            spread=1490,
            chg_1m=-4.0,
            chg_ytd=-18.0,
            coupon="S+475",
            maturity="2029-06-30",
        ),
        "hy_index": dict(
            block="HY index",
            name="CCC high-yield index (synthetic)",
            ratings="CCC",
            price=64.0,
            spread=2240,
            chg_1m=-3.0,
            chg_ytd=-12.5,
            coupon="—",
            maturity="—",
        ),
        "hy_peer_e": dict(
            block="HY comparable",
            name="Peer E (synthetic) 9.0% Senior Notes 2028",
            ratings="Caa2 / CCC",
            price=52.0,
            spread=3010,
            chg_1m=-6.0,
            chg_ytd=-27.0,
            coupon="9.00%",
            maturity="2028-11-15",
        ),
        "hy_peer_f": dict(
            block="HY comparable",
            name="Peer F (synthetic) 7.5% Senior Notes 2029",
            ratings="Caa3 / CCC-",
            price=37.0,
            spread=4120,
            chg_1m=-8.5,
            chg_ytd=-35.0,
            coupon="7.50%",
            maturity="2029-04-30",
        ),
    },
    "Anonymised synthetic peers with distressed levels bracket the Larchmere loans and notes so the relative-value charts have comparables.",
)
_f(
    "quote_history",
    {
        "llg_tlb": dict(one_month=79, ytd_open=91),
        "llg_2l": dict(one_month=49, ytd_open=78),
        "llg_notes": dict(one_month=31, ytd_open=66),
    },
    "Prices a month ago and at the start of the year fall steeply, as a missed coupon and a covenant breach would produce.",
)
_f(
    "portfolio",
    {
        "id": "FENWICK_CLO",
        "name": "Fenwick Park CLO Ltd (fictional)",
        "nav": 400000000,
        "par": 396000000,
        "position_par": 11200000,
        "single_issuer_limit": 2.5,
        "ccc_limit": 7.5,
        "ccc_current": 6.1,
        "second_lien_limit": 10.0,
        "second_lien_current": 7.2,
        "sector_limit": 8.0,
        "sector_current": 5.4,
    },
    "A 400m CLO holding 11.2m par of the first-lien loan (2.8% of NAV) against a 2.5% Hard single-issuer limit is the Fit breach the brief fixes.",
)

# ------------------------------------------------------------------ business, ownership and event narrative (CP-1A)
_f(
    "business_overview",
    {
        "description": (
            "Larchmere operates eleven casino resorts in Louisiana, Mississippi, Missouri and Indiana plus an online sports-betting and iGaming business, "
            "serving mainly drive-in regional customers. Gaming is the large majority of revenue; hotel, food and entertainment are supporting lines. "
            "Seven of the eleven properties are leased from one landlord under a single master lease; four are owned."
        ),
        "gaming_share_pct": 71,
        "leased_properties": 7,
        "owned_properties": 4,
        "loyalty_share_pct": 58,
    },
    "A regional operator with seven master-leased and four owned properties and a small online arm is the structure the brief's rent-burdened story needs.",
)
_f(
    "ownership_terms",
    {
        "sponsor_stake_pct": 88,
        "board": "seven directors, four appointed by the sponsor",
        "equity_cure_committed": False,
        "lease_cross_default": "an event of default under the funded debt that is not cured within 30 days is an event of default under the master lease",
        "lessor_consent": "the landlord must consent to a change of control and to any assignment of the lease in a restructuring",
    },
    "A sponsor holding 88%, no committed support and a lessor with consent rights are the governance facts that decide who can fund and who can block a rescue.",
)
_f(
    "event_history",
    [
        (
            "2022-09-01",
            "Sponsor buyout closes; master lease with the landlord executed for seven properties",
            "Completed",
            "Sets the debt stack and the rent burden",
            "No",
        ),
        (
            "2025-06-30",
            "First-lien credit agreement amended: term loan B amortisation holiday and covenant reset",
            "Completed",
            "Gives the covenant package and the amortisation start date",
            "No",
        ),
        (
            "2026-07-21",
            "Moody's downgrades the corporate family rating to Caa2 from Caa1, outlook negative",
            "Completed",
            "Confirms distressed ratings and a high default risk",
            "No",
        ),
        (
            "2026-08-04",
            "S&P lowers the issuer credit rating to CCC from CCC+, outlook negative",
            "Completed",
            "Second agency confirms distress",
            "No",
        ),
        (
            "2026-08-18",
            "Company retains restructuring advisers and a financial adviser",
            "Completed",
            "Signals preparation for a negotiated deal",
            "No",
        ),
        (
            "2026-09-15",
            "Semi-annual coupon on the 8.25% notes due 2029 not paid; 30-day grace period begins",
            "Open",
            "Starts the clock to an event of default and cross-default",
            "No",
        ),
        (
            "2026-09-21",
            "Q2 compliance certificate delivered 30 days late: first-lien net leverage above the 6.50x springing test",
            "Open",
            "Breach with an equity cure window to 19 October",
            "No",
        ),
        (
            "2026-09-22",
            "Sponsor proposes an amend-and-extend with 150 of new-money priming debt",
            "Proposed",
            "Sets up the uptier path and the creditor conflict",
            "No",
        ),
    ],
    "A dated sequence from the 2022 buyout to a missed coupon and a sponsor rescue proposal is the typical run-up to a negotiated restructuring.",
)

# ------------------------------------------------------------------ earnings-quality items (CP-1D)
_f(
    "debt_like_inputs",
    {"earn_out": 22, "pension_withdrawal": 14, "customer_deposits": 19, "coupon_pct": 8.25},
    "A deferred earn-out of 22, a multi-employer pension withdrawal liability of 14 and customer deposits of 19 are ordinary off-balance or non-debt claims for a regional casino operator.",
)

# ------------------------------------------------------------------ sensitivities (CP-2A)
_f(
    "sensitivity_inputs",
    {
        "flow_through_pct": 45,
        "revenue_shock_pct": 5,
        "ebitda_shock_pct": 10,
        "sofr_shock_bps": 100,
        "rent_shock_pp": 1,
        "capex_cut_pct": 25,
    },
    "A 45% revenue-to-EBITDA flow-through is typical for casinos with high fixed costs, and 5%, 10%, 100 bps, 1 pp and 25% are standard shock sizes.",
)

# ------------------------------------------------------------------ legal provisions (CP-4)
_f(
    "legal_provisions",
    {
        "required_lenders_pct": 50.1,
        "savings_cap_pct": 20,
        "savings_months": 18,
        "cure_frequency": "once over the life of the revolver, and not used to date",
        "open_market": "the Borrower and its affiliates may purchase term loans in open-market purchases or Dutch auctions that need not be offered to all lenders",
        "sacred": "payment priority and lien priority can be changed with Required Lender consent; only the amount, rate and maturity of an individual lender's loan need that lender's consent",
        "designation": "a restricted subsidiary can be designated unrestricted if the investment fits the unrestricted-subsidiary basket, with no leverage test",
        "agent": "Marlow Fenwick Bank (fictional)",
        "law": "New York",
    },
    "Required-lender amendment of priority, open-market purchases and an unrestricted-subsidiary basket without a leverage test are the typical 2022 sponsor-deal terms that enable uptier and drop-down transactions.",
)
