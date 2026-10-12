"""Portfolio Fit arithmetic (interfaces spec section 7): hand cases and properties (money code).

The portfolio below is Test CLO I's shape (NAV 630.9, par 634.0, USD millions) with a 6.0 par
position in the run's issuer, so its exposure is 6.0 / 630.9 x 100 = 0.951022...% of NAV.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rbotlib import fit_arithmetic as fa
from rbotlib.fit_arithmetic import Instrument, Portfolio, Run

RUN = Run("CZR", date(2026, 10, 2), "USD", "MILLIONS", ("Caesars Entertainment, Inc.",))
NAV = Decimal("630.9")
TAXONOMY = {"sector": frozenset({"casinos", "insurance"}), "country": frozenset({"us", "gb"})}


def limit(
    limit_id: str, scope: str, value: str, unit: str, kind: str, **extra: object
) -> dict[str, Any]:
    """A limit as `rbot prepare` writes it; a bucket limit is a "largest bucket" one by default."""
    row: dict[str, Any] = {"limit_id": limit_id, "category": scope, "scope": scope}
    row["parameter"] = f"max {scope}"
    row |= {"scope_value": None, "limit_value": value, "unit": unit, "limit_kind": kind}
    row["largest"] = scope != "issuer"
    return row | {"current_value": "0", "source": f"limits.csv row {limit_id}"} | extra


def portfolio(
    *limits: dict[str, Any],
    positions: list[dict[str, Any]] | None = None,
    unparsed: tuple[dict[str, str], ...] = (),
    nav: Decimal | None = NAV,
    par: Decimal | None = Decimal("634.0"),
    unit: str = "MILLIONS",
) -> Portfolio:
    held = [{"issuer_id": "CZR", "par": "6.0"}, {"issuer_id": "ASURION", "par": "15.0"}]
    return Portfolio(
        "P",
        "Test",
        "CLO",
        nav,
        par,
        "USD",
        unit,
        tuple(held if positions is None else positions),
        tuple(limits),
        unparsed,
    )


LOAN = Instrument(
    "TLB",
    "Term Loan B",
    "1L Term Loan",
    True,
    "USD",
    date(2031, 2, 6),
    ("Ba3", "BB"),
    "Casinos",
    "US",
)
EXPOSURE = fa.CONTEXT.divide(Decimal("600.0"), NAV)  # 6.0 x 100 / 630.9


def loan(**extra: object) -> Instrument:
    fields = asdict(LOAN)
    fields.update(extra)
    return Instrument(**fields)


def test_the_issuer_limit_uses_the_run_issuers_own_exposure() -> None:
    f = fa.fit(
        portfolio(limit("C-01", "issuer", "2.5", "pct_nav", "Hard", current_value="2.37")),
        loan(),
        RUN,
    )
    assert f.current_exposure == Decimal("6.0")
    assert f.current_exposure_pct_nav == EXPOSURE
    row = f.rows[0]
    assert row.current_value == EXPOSURE  # not the file's 2.37 (Asurion)
    assert row.headroom == fa.CONTEXT.subtract(Decimal("2.5"), EXPOSURE)
    # (2.5 - 0.951022...) x 630.9 / 100 = 15.7725 - 6.0 = 9.7725
    assert row.headroom_amount == Decimal("9.7725")
    assert (f.max_size, f.binding_limit, f.verdict, f.recommendation_cap) == (
        Decimal("9.7725"),
        "C-01",
        "Fits",
        "1 - Strong OW",
    )


@pytest.mark.parametrize(
    ("unit", "current", "amount"),
    [
        (
            "pct_par",
            fa.CONTEXT.divide(Decimal(600), Decimal(634)),
            Decimal("9.85"),
        ),  # 2.5 x 6.34 - 6
        ("amount", Decimal("6.0"), Decimal("-3.5")),
        ("count", Decimal(1), None),
    ],
)
def test_issuer_limits_in_other_units(unit: str, current: Decimal, amount: Decimal | None) -> None:
    f = fa.fit(portfolio(limit("C-01", "issuer", "2.5", unit, "Soft")), loan(), RUN)
    assert f.rows[0].current_value == current
    assert f.rows[0].headroom_amount == amount


@pytest.mark.parametrize(
    ("ratings", "bucket"),
    [
        (("Ba3", "BB"), "BB"),
        (("B1", "BB-"), "B"),
        (("Caa1", "B-"), "CCC"),
        (("Baa3",), "IG"),
        (("BBB-",), "IG"),
        (("B+",), "B"),
        (("CCC+",), "CCC"),
        (("A1", "D"), "CCC"),
        (("NR",), "Unrated"),
        ((), "Unrated"),
        (("B3*",), "B"),
    ],
)
def test_rating_buckets_take_the_lowest_agency(ratings: tuple[str, ...], bucket: str) -> None:
    assert fa.rating_bucket(ratings) == bucket


@pytest.mark.parametrize(
    ("scope", "value", "instrument", "touched"),
    [
        ("sector", "Tobacco, Casinos", loan(), True),
        ("sector", "Insurance", loan(), False),
        ("sector", None, loan(), True),  # the largest sector bounds every sector
        ("sector", "Casinos", loan(sector=None), None),
        ("rating_bucket", "CCC", loan(ratings=("Caa1",)), True),
        ("rating_bucket", "CCC", loan(), False),
        ("rating_bucket", "Unrated", loan(ratings=()), True),
        ("rating_bucket", "CCC", loan(ratings=()), True),  # unrated counts toward the CCC bucket
        ("seniority", "2nd Lien / Unsecured", loan(debt_type="SU Notes", secured=False), True),
        ("seniority", "2nd Lien / Unsecured", loan(), False),
        ("seniority", "1st Lien / Senior Secured", loan(), True),
        ("seniority", "2nd Lien", loan(debt_type="Other", secured=None), None),
        ("seniority", "Mezzanine", loan(), False),
        ("asset_type", "Loan", loan(), True),
        ("asset_type", "Bond", loan(debt_type="SS Notes"), True),
        ("asset_type", "Loan", loan(debt_type="Other"), None),
        ("country", "US", loan(), True),
        ("currency", "EUR", loan(), False),
        ("maturity", "any", loan(), True),
        ("maturity", "any", loan(maturity=None), None),
        ("other", None, loan(), False),
        ("unknown", "x", loan(), False),
    ],
)
def test_which_limits_touch_an_instrument(
    scope: str, value: str | None, instrument: Instrument, touched: bool | None
) -> None:
    row = {"scope": scope, "scope_value": value, "largest": value is None}
    assert fa.touches(row, instrument, TAXONOMY) is touched


def test_a_maturity_limit_uses_the_tenor_and_caps_no_size() -> None:
    f = fa.fit(
        portfolio(limit("M", "maturity", "8", "years", "Hard", scope_value="max")), loan(), RUN
    )
    # 2026-10-02 to 2031-02-06 is 1588 days: 8 - 1588 / 365
    assert f.rows[0].headroom == fa.CONTEXT.subtract(
        Decimal(8), fa.CONTEXT.divide(Decimal(1588), Decimal(365))
    )
    assert (f.rows[0].headroom_amount, f.max_size, f.binding_limit) == (None, None, None)
    late = fa.fit(
        portfolio(limit("M", "maturity", "3", "years", "Hard", scope_value="max")), loan(), RUN
    )
    assert (late.rows[0].status, late.verdict) == ("Breached", "Breaches")


def test_a_book_statistic_is_from_file_and_never_binds() -> None:
    f = fa.fit(
        portfolio(limit("C-11", "other", "8.0", "years", "Soft", current_value="4.82")), loan(), RUN
    )
    assert (f.rows[0].status, f.rows[0].headroom, f.max_size) == (
        "From file",
        Decimal("3.18"),
        None,
    )


@pytest.mark.parametrize(
    ("limits", "verdict", "reason"),
    [
        (
            [limit("H", "sector", "5", "pct_nav", "Hard", current_value="6")],
            "Breaches",
            "hard limit H has negative headroom",
        ),
        (
            [limit("H", "sector", "5", "pct_nav", "Hard", current_value="5")],
            "Breaches",
            "no size fits the hard limits",
        ),
        (
            [limit("S", "sector", "5", "pct_nav", "Soft", current_value="6")],
            "Watch",
            "soft limit S has negative headroom",
        ),
        (
            [limit("H", "sector", "5", "pct_nav", "Hard", current_value="4.5")],
            "Watch",
            "the largest size that fits is under 1% of NAV",
        ),
        (
            [limit("H", "sector", "5", "pct_nav", "Hard", current_value="3.99")],
            "Fits",
            "every touched limit has headroom",
        ),
        (
            [limit("N", "sector", "5", "pct_nav", "Soft", scope_value="Casinos")],
            "Fits",
            "every touched limit has headroom",
        ),
    ],
)
def test_verdicts(limits: list[dict[str, Any]], verdict: str, reason: str) -> None:
    f = fa.fit(portfolio(*limits), loan(), RUN)
    assert (f.verdict, f.reason) == (verdict, reason)


def test_a_limit_that_cannot_be_computed_is_a_watch() -> None:
    f = fa.fit(
        portfolio(limit("N", "sector", "5", "pct_nav", "Soft", scope_value="Casinos")),
        loan(sector=None),
        RUN,
    )
    assert (f.rows[0].status, f.verdict, f.reason) == (
        "Not computed",
        "Watch",
        "limit N could not be computed",
    )
    assert f.recommendation_cap == "3 - MW"


def test_units_convert_and_a_foreign_currency_is_not_computed() -> None:
    thousands = Portfolio(
        "P",
        "T",
        "CLO",
        Decimal(630900),
        Decimal(634000),
        "USD",
        "THOUSANDS",
        (),
        (limit("C", "issuer", "2.5", "pct_nav", "Hard"),),
    )
    f = fa.fit(thousands, loan(), RUN)
    assert (f.max_size, f.currency, f.unit) == (Decimal("15.7725"), "USD", "MILLIONS")
    euros = Portfolio(
        "P",
        "T",
        "CLO",
        NAV,
        Decimal(634),
        "EUR",
        "MILLIONS",
        (),
        (limit("C", "issuer", "2.5", "pct_nav", "Hard"),),
    )
    f = fa.fit(euros, loan(), RUN)
    assert (f.rows[0].status, f.verdict, f.currency) == ("Not computed", "Watch", "EUR")


def test_the_smallest_hard_headroom_binds() -> None:
    f = fa.fit(
        portfolio(
            limit("A", "sector", "10", "pct_nav", "Hard", current_value="5"),
            limit("B", "issuer", "2.5", "pct_nav", "Hard"),
            limit("C", "sector", "1", "pct_nav", "Soft", current_value="0"),
        ),
        loan(),
        RUN,
    )
    assert (f.max_size, f.binding_limit) == (Decimal("9.7725"), "B")


# --- properties ------------------------------------------------------------------------------

LIMIT_VALUES = st.decimals(min_value=Decimal(0), max_value=Decimal(20), places=2)
CURRENT = st.decimals(min_value=Decimal(0), max_value=Decimal(20), places=2)


@settings(deadline=None)
@given(LIMIT_VALUES, LIMIT_VALUES, CURRENT)
def test_headroom_rises_with_the_limit(a: Decimal, b: Decimal, current: Decimal) -> None:
    low, high = sorted((a, b))
    rows = [
        fa.fit(
            portfolio(limit("L", "sector", str(v), "pct_nav", "Hard", current_value=str(current))),
            loan(),
            RUN,
        ).rows[0]
        for v in (low, high)
    ]
    assert rows[0].headroom is not None and rows[1].headroom is not None
    assert rows[0].headroom <= rows[1].headroom


@settings(deadline=None)
@given(
    st.lists(
        st.tuples(LIMIT_VALUES, CURRENT, st.sampled_from(["Hard", "Soft"])), min_size=1, max_size=6
    )
)
def test_max_size_never_exceeds_a_hard_headroom(limits: list[tuple[Decimal, Decimal, str]]) -> None:
    rows = [
        limit(f"L{n}", "sector", str(v), "pct_nav", k, current_value=str(c))
        for n, (v, c, k) in enumerate(limits)
    ]
    f = fa.fit(portfolio(*rows), loan(), RUN)
    hard = [
        r.headroom_amount
        for r in f.rows
        if r.limit["limit_kind"] == "Hard" and r.headroom_amount is not None
    ]
    if hard:
        assert f.max_size is not None and f.max_size <= max(Decimal(0), min(hard))
    else:
        assert f.max_size is None


ORDER = {"Fits": 0, "Watch": 1, "Breaches": 2}


@settings(deadline=None)
@given(
    st.lists(st.tuples(LIMIT_VALUES, CURRENT, st.sampled_from(["Hard", "Soft"])), max_size=5),
    st.tuples(LIMIT_VALUES, CURRENT, st.sampled_from(["Hard", "Soft"])),
)
def test_adding_a_limit_never_improves_the_verdict(
    limits: list[tuple[Decimal, Decimal, str]], extra: tuple[Decimal, Decimal, str]
) -> None:
    rows = [
        limit(f"L{n}", "sector", str(v), "pct_nav", k, current_value=str(c))
        for n, (v, c, k) in enumerate(limits)
    ]
    before = fa.fit(portfolio(*rows), loan(), RUN).verdict
    added = limit("X", "sector", str(extra[0]), "pct_nav", extra[2], current_value=str(extra[1]))
    after = fa.fit(portfolio(*rows, added), loan(), RUN).verdict
    assert ORDER[after] >= ORDER[before]


def test_attributes_and_senior_rank() -> None:
    assert [fa.asset_type(t) for t in ("1L Term Loan", "SU Notes", "Other", None)] == [
        "Loan",
        "Bond",
        None,
        None,
    ]
    assert fa.is_senior_secured(loan(debt_type="2L Term Loan", secured=True)) is False
    assert fa.is_senior_secured(loan(debt_type="Other", secured=True)) is True
    two_words = {"scope": "sector", "scope_value": "Health Care, Insurance"}
    assert fa.touches(two_words, loan(sector="Health Care"), TAXONOMY) is True


def test_units_other_than_millions_scale_every_amount() -> None:
    held = (
        {"issuer_id": "CZR", "par": "6000"},
        {"issuer_id": "A", "par": "1"},
        {"issuer_id": "B", "par": "1"},
    )
    limits = (
        limit("P", "issuer", "2.5", "pct_par", "Hard"),
        limit("A", "issuer", "20000", "amount", "Hard"),
        limit("N", "issuer", "3", "count", "Soft"),
    )
    thousands = Portfolio(
        "P", "T", "CLO", Decimal(630900), Decimal(634000), "USD", "THOUSANDS", held, limits
    )
    f = fa.fit(thousands, loan(), RUN)
    assert [r.headroom_amount for r in f.rows] == [Decimal("9.85"), Decimal(14), None]
    assert f.rows[2].current_value == Decimal(1)  # one Caesars position, not the others
    assert (f.current_exposure, f.max_size, f.binding_limit) == (Decimal(6), Decimal("9.85"), "P")


def test_an_unknown_unit_or_currency_is_not_computed_and_keeps_the_figures() -> None:
    billions = Portfolio(
        "P",
        "T",
        "CLO",
        NAV,
        Decimal(634),
        "USD",
        "BILLIONS",
        (),
        (limit("C", "issuer", "2.5", "pct_nav", "Hard"),),
    )
    f = fa.fit(billions, loan(), RUN)
    assert (f.rows[0].status, f.rows[0].current_value) == ("Not computed", Decimal(0))
    stats = fa.fit(
        portfolio(limit("W", "other", "8.0", "years", "Soft", current_value="4.82")), loan(), RUN
    )
    assert stats.rows[0].current_value == Decimal("4.82")
    euros = Portfolio(
        "P",
        "T",
        "CLO",
        NAV,
        Decimal(634),
        "EUR",
        "MILLIONS",
        (),
        (limit("C", "issuer", "2.5", "pct_nav", "Hard"),),
    )
    f = fa.fit(euros, loan(), RUN)
    assert type(f.current_exposure) is Decimal and f.current_exposure == 0
    assert (f.portfolio, f.instrument, f.current_exposure_pct_nav) == (euros, loan(), Decimal(0))
    assert (f.max_size, f.binding_limit, f.reason) == (None, None, "limit C could not be computed")


def test_the_first_of_two_equal_hard_limits_binds() -> None:
    f = fa.fit(
        portfolio(
            limit("Z", "sector", "5", "pct_nav", "Hard", current_value="2"),
            limit("A", "sector", "5", "pct_nav", "Hard", current_value="2"),
        ),
        loan(),
        RUN,
    )
    assert f.binding_limit == "Z"


def test_a_size_of_exactly_one_percent_of_nav_fits() -> None:
    f = fa.fit(
        portfolio(limit("H", "sector", "5", "pct_nav", "Hard", current_value="4")), loan(), RUN
    )
    assert (f.max_size, f.verdict) == (Decimal("6.309"), "Fits")


# --- the up-front review of Plan 05 (money): every case below failed before its fix -----------


def test_an_unreadable_limit_or_position_row_lowers_the_verdict() -> None:
    """C1: spec section 7.4, a row in `unparsed` makes the fit a Watch."""
    issuer = limit("C-01", "issuer", "2.5", "pct_nav", "Hard")
    for kind in ("limit", "position"):
        row = {"row": "limits.csv row 23", "reason": "amount limit under Unit 'millions'"}
        f = fa.fit(portfolio(issuer, unparsed=({**row, "kind": kind},)), loan(), RUN)
        assert (f.verdict, f.recommendation_cap) == ("Watch", "3 - MW")
        assert f.reason == (
            "limits.csv row 23 could not be read (amount limit under Unit 'millions')"
        )
    unkinded = fa.fit(portfolio(issuer, unparsed=(row,)), loan(), RUN)
    assert unkinded.verdict == "Watch"  # a row of unknown kind is not assumed harmless


@pytest.mark.parametrize("kind", ["info", "minimum", "meta"])
def test_an_info_minimum_or_meta_row_only_goes_to_the_gaps(kind: str) -> None:
    row = {"row": "limits.csv row 14", "reason": "minimum limit", "kind": kind}
    f = fa.fit(
        portfolio(limit("C-01", "issuer", "2.5", "pct_nav", "Hard"), unparsed=(row,)), loan(), RUN
    )
    assert (f.verdict, f.reason) == ("Fits", "every touched limit has headroom")


def test_a_sector_name_that_holds_a_comma_is_touched() -> None:
    """C2: `Hotel, Gaming & Leisure` is one name, not two."""
    name = "Hotel, Gaming & Leisure"
    hard = limit("S-1", "sector", "8", "pct_nav", "Hard", scope_value=name, largest=False)
    hard["current_value"] = "7.9"
    f = fa.fit(portfolio(hard), loan(sector=name), RUN)
    assert [r.limit["limit_id"] for r in f.rows] == ["S-1"]
    listed = limit(
        "S-2", "sector", "8", "pct_nav", "Hard", scope_values=["Hotel, Gaming & Leisure", "Tobacco"]
    )
    assert fa.touches(listed | {"largest": False}, loan(sector=name)) is True


def test_an_exclusion_list_cannot_clear_a_sector_outside_the_portfolios_taxonomy() -> None:
    """C2: CP-1A's free text is not in the exclusion list's words, so the answer is unknown."""
    gambling = limit(
        "C-17", "sector", "0", "pct_nav", "Hard", scope_value="Tobacco, Gambling, Thermal Coal"
    )
    gambling["largest"] = False
    casino = loan(sector="Casino-entertainment and online gaming")
    f = fa.fit(portfolio(gambling), casino, RUN)
    assert [(r.limit["limit_id"], r.status) for r in f.rows] == [("C-17", "Not computed")]
    assert (f.verdict, f.recommendation_cap) == ("Watch", "3 - MW")
    assert f.uncomputed_hard == ("C-17",)  # max_size ignores it


def test_the_portfolios_own_sector_for_the_run_issuer_is_used_when_it_holds_the_issuer() -> None:
    gambling = limit("C-17", "sector", "0", "pct_nav", "Hard", scope_value="Tobacco, Gambling")
    gambling["largest"] = False
    held = [{"issuer_id": "CZR", "par": "6.0", "sector": "Gambling", "country": "US"}]
    f = fa.fit(portfolio(gambling, positions=held), loan(sector="Casino-entertainment"), RUN)
    assert (f.rows[0].status, f.verdict) == ("Within", "Breaches")  # a 0% limit leaves no size


def test_a_sector_in_the_portfolios_taxonomy_but_not_listed_is_not_touched() -> None:
    tobacco = limit("T", "sector", "0", "pct_nav", "Hard", scope_value="Tobacco")
    tobacco["largest"] = False
    held = [{"issuer_id": "ASURION", "par": "15.0", "sector": "Casinos"}]
    assert fa.fit(portfolio(tobacco, positions=held), loan(sector="Casinos"), RUN).rows == ()


@pytest.mark.parametrize("ratings", [("(P)Caa1",), ("Caa1 *-",), ("Caa1u",), ("CCC+ (sf)",)])
def test_provisional_watch_and_structured_ratings_are_read(ratings: tuple[str, ...]) -> None:
    assert fa.rating_bucket(ratings) == "CCC"


@pytest.mark.parametrize(
    ("ratings", "bucket"),
    [
        (("NR",), "Unrated"),
        (("WR", ""), "Unrated"),
        (("Zz9",), "Unreadable"),
        (("Zz9", "BB"), "Unreadable"),
    ],
)
def test_no_rating_is_unrated_and_an_unreadable_one_is_unreadable(
    ratings: tuple[str, ...], bucket: str
) -> None:
    assert fa.rating_bucket(ratings) == bucket


@pytest.mark.parametrize("ratings", [(), ("Zz9",)])
def test_an_unrated_or_unreadable_instrument_counts_toward_the_ccc_bucket(
    ratings: tuple[str, ...],
) -> None:
    """I1: C-04 sits at 7.36% of 7.5% (Hard), so such an instrument is a Watch."""
    ccc = limit(
        "C-04", "rating_bucket", "7.5", "pct_nav", "Hard", scope_value="CCC", current_value="7.36"
    )
    ccc["largest"] = False
    f = fa.fit(portfolio(ccc), loan(ratings=ratings), RUN)
    assert (f.max_size, f.verdict) == (Decimal("0.88326"), "Watch")
    assert f.notes == ("TLB: missing or unreadable rating, counted toward C-04",)
    assert fa.fit(portfolio(ccc), loan(ratings=("B2",)), RUN).rows == ()  # a rated B is not in it


def test_a_limit_without_a_scope_value_that_is_not_a_largest_bucket_limit_is_not_computed() -> None:
    """I2: `Asset Type, Max bonds` must not bind a loan, nor `Non-USD` make a USD loan Avoid."""
    bonds = limit("C-20", "asset_type", "5", "pct_nav", "Hard", current_value="5", largest=False)
    non_usd = limit("C-22", "currency", "0", "pct_nav", "Hard", current_value="0", largest=False)
    f = fa.fit(portfolio(bonds, non_usd), loan(), RUN)
    assert [r.status for r in f.rows] == ["Not computed", "Not computed"]
    assert (f.verdict, f.max_size) == ("Watch", None)


def test_a_count_limit_with_no_room_left_gives_no_size() -> None:
    """I5: spec 7.2, count headroom under 1 gives an amount of 0, so Breaches."""
    two = limit("C-26", "issuer", "2", "count", "Hard")
    held = [{"issuer_id": "CZR", "par": "1"}, {"issuer_id": "CZR", "par": "2"}]
    f = fa.fit(portfolio(two, positions=held), loan(), RUN)
    assert (f.rows[0].headroom_amount, f.verdict, f.reason) == (
        Decimal(0),
        "Breaches",
        "no size fits the hard limits",
    )
    three = fa.fit(portfolio(two | {"limit_value": "3"}, positions=held), loan(), RUN)
    assert (three.rows[0].headroom_amount, three.verdict) == (None, "Fits")


def test_a_maturity_limit_equal_to_the_tenor_caps_the_size_at_zero() -> None:
    tenor = fa.tenor_years(loan(), RUN.as_of)
    assert tenor is not None
    row = limit("M", "maturity", str(tenor), "years", "Hard")
    f = fa.fit(portfolio(row), loan(), RUN)
    assert (f.rows[0].headroom_amount, f.verdict) == (Decimal(0), "Breaches")


@pytest.mark.parametrize("issuer_id", ["czr", " CZR "])
def test_the_issuer_id_is_matched_without_case_or_spaces(issuer_id: str) -> None:
    """I6: `czr` is the run issuer, so its 14.0 par counts (2.5% limit, 2.22% held)."""
    held = [{"issuer_id": issuer_id, "par": "14.0"}]
    f = fa.fit(
        portfolio(limit("C-01", "issuer", "2.5", "pct_nav", "Hard"), positions=held), loan(), RUN
    )
    assert f.current_exposure == Decimal("14.0")
    assert f.max_size == Decimal("1.7725")


def test_a_position_matched_by_issuer_name_alone_is_counted_and_a_watch() -> None:
    held = [{"issuer_id": "CAESARS", "issuer_name": "CAESARS ENTERTAINMENT INC", "par": "14.0"}]
    f = fa.fit(
        portfolio(limit("C-01", "issuer", "5", "pct_nav", "Hard"), positions=held), loan(), RUN
    )
    assert f.current_exposure == Decimal("14.0")
    assert (f.verdict, f.reason) == (
        "Watch",
        "positions CAESARS matched the issuer by name only; the ids disagree",
    )


def test_a_breached_hard_book_statistic_avoids() -> None:
    """I7: a Hard limit shown From file that is already negative still counts."""
    book = limit("C-30", "other", "12.0", "pct_nav", "Hard", current_value="12.5")
    f = fa.fit(portfolio(book), loan(), RUN)
    assert f.rows[0].status == "From file"
    assert (f.verdict, f.max_size, f.recommendation_cap) == ("Breaches", None, "Avoid")
    assert f.reason == "hard limit C-30 has negative headroom"


@pytest.mark.parametrize("nav", [Decimal(0), Decimal("-630.9"), None])
def test_a_zero_negative_or_missing_nav_is_a_watch_not_a_crash(nav: Decimal | None) -> None:
    """I8."""
    rows = (
        limit("C-01", "issuer", "2.5", "pct_nav", "Hard"),
        limit("C-09", "issuer", "9", "amount", "Soft"),
    )
    f = fa.fit(portfolio(*rows, nav=nav), loan(), RUN)
    assert [r.status for r in f.rows] == ["Not computed", "Within"]
    assert (f.verdict, f.max_size, f.current_exposure_pct_nav) == ("Watch", None, None)


def test_par_matters_only_to_a_limit_in_percent_of_par() -> None:
    nav_limit = limit("C-01", "issuer", "2.5", "pct_nav", "Hard")
    par_limit = limit("C-02", "issuer", "2.5", "pct_par", "Hard")
    assert fa.fit(portfolio(nav_limit, par=None), loan(), RUN).rows[0].status == "Within"
    assert fa.fit(portfolio(par_limit, par=None), loan(), RUN).rows[0].status == "Not computed"


@pytest.mark.parametrize(
    ("scope_value", "instrument", "touched"),
    [
        ("Senior secured bonds", loan(), False),
        ("Senior secured bonds", loan(debt_type="SS Notes"), True),
        ("Second lien loans", loan(debt_type="SU Notes", secured=False), False),
        ("Second lien loans", loan(debt_type="2L Term Loan"), True),
    ],
)
def test_seniority_words_also_name_the_asset_type(
    scope_value: str, instrument: Instrument, touched: bool
) -> None:
    assert fa.touches({"scope": "seniority", "scope_value": scope_value}, instrument) is touched


@pytest.mark.parametrize("unit", ["Millions", "MILLIONS", "millions"])
def test_the_unit_is_matched_without_case(unit: str) -> None:
    f = fa.fit(portfolio(limit("C", "issuer", "2.5", "pct_nav", "Hard"), unit=unit), loan(), RUN)
    assert f.max_size == Decimal("9.7725")


@pytest.mark.parametrize("unit", ["units", "USD"])
def test_an_unscaled_unit_converts_to_the_run_unit(unit: str) -> None:
    f = fa.fit(
        portfolio(limit("C", "issuer", "20000000", "amount", "Hard"), unit=unit), loan(), RUN
    )
    assert f.rows[0].headroom_amount == Decimal("19.999994")  # 20,000,000 less 6, in millions


def test_a_blank_unit_is_not_guessed() -> None:
    f = fa.fit(portfolio(limit("C", "issuer", "2.5", "pct_nav", "Hard"), unit=""), loan(), RUN)
    assert f.rows[0].status == "Not computed"


# --- mutation review: cases that pin the arithmetic's small decisions ----------------------------


def test_fold_and_name_are_what_the_matching_relies_on() -> None:
    assert fa._fold("  Hotel,  Gaming &\tLeisure ") == "hotel, gaming & leisure"
    assert fa._name("Caesars Entertainment, Inc.") == "caesars entertainment"
    assert fa._name("THE Acme Holdings Co Ltd") == "acme holdings"


def test_scope_values_lists_the_whole_name_then_its_comma_parts() -> None:
    assert fa.scope_values({"scope_value": "Hotel, Gaming & Leisure"}) == [
        "hotel, gaming & leisure",
        "hotel",
        "gaming & leisure",
    ]
    assert fa.scope_values({"scope_value": "Tobacco"}) == ["tobacco"]
    assert fa.scope_values({"scope_value": "A, , B"}) == ["a, , b", "a", "b"]
    assert fa.scope_values({"scope_values": ["X, Y", "Z"], "scope_value": "ignored"}) == [
        "x, y",
        "z",
    ]
    assert fa.scope_values({"scope_value": None}) == []


def test_a_sector_name_with_a_comma_is_a_within_row_with_its_headroom() -> None:
    name = "Hotel, Gaming & Leisure"
    hard = limit("S-1", "sector", "8", "pct_nav", "Hard", scope_value=name, largest=False)
    hard["current_value"] = "7.9"
    row = fa.fit(portfolio(hard), loan(sector=name), RUN).rows[0]
    assert (row.status, row.headroom, row.headroom_amount) == (
        "Within",
        Decimal("0.1"),
        Decimal("0.6309"),
    )


@pytest.mark.parametrize(
    ("scope", "value", "instrument", "touched"),
    [
        ("rating_bucket", "B", loan(ratings=()), False),  # unrated counts toward CCC only
        ("rating_bucket", "B", loan(ratings=("Zz9",)), False),
        ("rating_bucket", "Unrated", loan(ratings=("Zz9",)), True),
        ("sector", "Tobacco", loan(sector="Casinos"), False),
    ],
)
def test_unrated_instruments_touch_only_the_ccc_and_unrated_limits(
    scope: str, value: str, instrument: Instrument, touched: bool
) -> None:
    row = {"scope": scope, "scope_value": value}
    assert (
        fa.touches(row, instrument, TAXONOMY | {"sector": frozenset({"casinos", "tobacco"})})
        is touched
    )


@pytest.mark.parametrize(
    ("scope", "value", "ratings", "counted"),
    [
        ("rating_bucket", "CCC", (), True),
        ("rating_bucket", "CCC", ("Zz9",), True),
        ("rating_bucket", "CCC", ("B2",), False),  # rated: counted for what it is
        ("rating_bucket", "Unrated", (), False),  # a direct hit, not a stretch to CCC
        ("sector", "CCC", (), False),  # not a rating limit
        ("rating_bucket", "B", (), False),
    ],
)
def test_the_unrated_are_flagged_only_when_stretched_to_the_ccc_bucket(
    scope: str, value: str, ratings: tuple[str, ...], counted: bool
) -> None:
    assert (
        fa.counted_as_ccc({"scope": scope, "scope_value": value}, loan(ratings=ratings)) is counted
    )


def test_a_taxonomy_without_the_scope_means_unknown() -> None:
    row = {"scope": "sector", "scope_value": "Tobacco", "largest": False}
    assert fa.touches(row, loan(sector="Casinos")) is None
    assert fa.touches(row, loan(sector="Casinos"), {"country": frozenset({"us"})}) is None
    assert fa.touches(row, loan(sector="Casinos"), {"sector": frozenset({"casinos"})}) is False


def test_the_attributes_of_a_position_without_an_id_or_a_name() -> None:
    """Defaults: a position with neither key is nobody's, whatever the run's id or name is."""
    nameless = [{"par": "5.0"}]
    for who in (
        Run("None", RUN.as_of, "USD", "MILLIONS", ("None",)),
        Run("XXXX", RUN.as_of, "USD", "MILLIONS", ("XXXX",)),
    ):
        held = fa.exposure(portfolio(positions=nameless), who)
        assert held.par == 0 and held.count == 0 and not held.by_name_only
    by_name = [{"issuer_name": "Caesars Entertainment Inc", "par": "5.0"}]
    held = fa.exposure(portfolio(positions=by_name), RUN)
    assert held.by_name_only == ("",) and held.count == 1  # a position with no id: the empty id


def test_the_issuer_the_portfolio_holds_gives_its_own_sector_and_country() -> None:
    positions = [
        {"issuer_id": "CZR", "par": "6.0", "sector": "Casinos", "country": "US"},
        {"issuer_id": "CZR", "par": "1.0", "sector": "Casinos", "country": "US"},
    ]
    held = fa.exposure(portfolio(positions=positions), RUN)
    assert held.par == 7 and held.sector == "Casinos" and held.country == "US"
    split = [{**positions[0], "country": "GB"}, positions[1]]
    held = fa.exposure(portfolio(positions=split), RUN)
    assert held.sector == "Casinos" and held.country is None  # the positions disagree
    country = limit("K", "country", "5", "pct_nav", "Soft", scope_value="US", largest=False)
    f = fa.fit(portfolio(country, positions=positions), loan(country="United States"), RUN)
    assert f.rows[0].status == "Within"  # the portfolio's "US", not CP-1A's "United States"


def test_a_maturity_with_room_under_a_year_is_not_a_cap() -> None:
    tenor = fa.tenor_years(loan(), RUN.as_of)
    assert tenor is not None
    row = limit("M", "maturity", str(tenor + Decimal("0.5")), "years", "Hard")
    f = fa.fit(portfolio(row), loan(), RUN)
    assert (f.rows[0].headroom_amount, f.verdict) == (None, "Fits")


def test_a_pct_nav_limit_that_is_not_the_issuers_needs_the_nav_too() -> None:
    sector = limit("S", "sector", "10", "pct_nav", "Soft", current_value="5")
    par = limit("P", "sector", "10", "pct_par", "Soft", current_value="5")
    assert fa.fit(portfolio(sector, nav=None), loan(), RUN).rows[0].status == "Not computed"
    assert fa.fit(portfolio(par, par=None), loan(), RUN).rows[0].status == "Not computed"
    assert fa.fit(portfolio(par, nav=None), loan(), RUN).rows[0].status == "Within"
    assert fa.fit(portfolio(sector, par=None), loan(), RUN).rows[0].status == "Within"


def test_a_small_positive_nav_or_par_is_a_figure() -> None:
    issuer = limit("C", "issuer", "2.5", "pct_nav", "Hard")
    f = fa.fit(portfolio(issuer, nav=Decimal("0.5"), par=Decimal("0.5")), loan(), RUN)
    assert f.rows[0].status != "Not computed" and f.current_exposure_pct_nav is not None
    zero_par = limit("P", "issuer", "2.5", "pct_par", "Hard")
    assert fa.fit(portfolio(zero_par, par=Decimal(0)), loan(), RUN).rows[0].status == "Not computed"


def test_the_portfolio_with_nothing_to_compute_is_still_a_watch_for_a_missing_nav() -> None:
    reason = "the portfolio's NAV is not a positive figure"
    for nav, par in ((None, Decimal(634)), (None, None)):
        f = fa.fit(portfolio(nav=nav, par=par), loan(), RUN)
        assert (f.verdict, f.reason) == ("Watch", reason)
    assert fa.fit(portfolio(), loan(), RUN).verdict == "Fits"


def test_the_one_percent_test_uses_the_nav_in_the_run_unit() -> None:
    thousands = portfolio(
        limit("C", "issuer", "2.5", "pct_nav", "Hard"),
        positions=[{"issuer_id": "CZR", "par": "0"}],
        nav=Decimal(630900),
        par=Decimal(634000),
        unit="THOUSANDS",
    )
    f = fa.fit(thousands, loan(), RUN)
    assert (f.max_size, f.verdict, f.positions_held) == (Decimal("15.7725"), "Fits", 1)
    held = fa.fit(portfolio(limit("C", "issuer", "5", "pct_nav", "Hard")), loan(), RUN)
    assert held.positions_held == 1


@pytest.mark.parametrize(
    ("current", "verdict"),
    [("12.5", "Breaches"), ("12.0", "Fits"), ("11.5", "Fits"), ("11.99", "Fits")],
)
def test_only_a_negative_hard_book_statistic_is_a_concern(current: str, verdict: str) -> None:
    book = limit("C-30", "other", "12.0", "pct_nav", "Hard", current_value=current)
    assert fa.fit(portfolio(book), loan(), RUN).verdict == verdict
    soft = limit("C-31", "other", "12.0", "pct_nav", "Soft", current_value="12.5")
    assert fa.fit(portfolio(soft), loan(), RUN).verdict == "Watch"  # never binds size


def test_a_non_book_row_is_not_a_book_concern() -> None:
    breached = limit("S", "sector", "5", "pct_nav", "Soft", current_value="6")
    f = fa.fit(portfolio(breached), loan(), RUN)
    assert fa.concerns(f.portfolio, fa.exposure(f.portfolio, RUN), f.rows) == []


def test_two_name_only_matches_are_listed_together() -> None:
    held = [
        {"issuer_id": "A", "issuer_name": "Caesars Entertainment", "par": "1"},
        {"issuer_id": "B", "issuer_name": "CAESARS ENTERTAINMENT, INC.", "par": "1"},
    ]
    f = fa.fit(portfolio(positions=held), loan(), RUN)
    assert f.reason == "positions A, B matched the issuer by name only; the ids disagree"


@pytest.mark.parametrize(
    ("ratings", "bucket"),
    [
        (("Ba2u",), "BB"),  # Moody's unsolicited mark is dropped, not the rating's last letter
        (("(P)Baa2",), "IG"),
        (("B1 *+",), "B"),
        (("BB (sf)",), "BB"),
        (("Caa1",), "CCC"),
    ],
)
def test_marks_are_dropped_from_a_rating_and_the_rating_is_kept(
    ratings: tuple[str, ...], bucket: str
) -> None:
    assert fa.rating_bucket(ratings) == bucket


@settings(deadline=None)
@given(
    st.lists(st.tuples(LIMIT_VALUES, CURRENT, st.sampled_from(["Hard", "Soft"])), max_size=4),
    st.sampled_from(["limit", "position"]),
)
def test_an_unreadable_row_never_improves_the_verdict_and_is_never_a_fit(
    limits: list[tuple[Decimal, Decimal, str]], kind: str
) -> None:
    rows = [
        limit(f"L{n}", "sector", str(v), "pct_nav", k, current_value=str(c))
        for n, (v, c, k) in enumerate(limits)
    ]
    lost = ({"row": "limits.csv row 9", "reason": "unreadable", "kind": kind},)
    before = fa.fit(portfolio(*rows), loan(), RUN).verdict
    after = fa.fit(portfolio(*rows, unparsed=lost), loan(), RUN).verdict
    assert ORDER[after] >= ORDER[before] and after != "Fits"


def test_unmatched_issuer_exposure_is_not_presented_as_a_fit() -> None:
    f = fa.fit(
        portfolio(
            limit("C", "issuer", "2.5", "pct_nav", "Hard"),
            positions=[{"issuer_id": "OTHER", "par": "2.0"}],
        ),
        loan(),
        RUN,
    )
    assert f.current_exposure == 0
    assert f.verdict == "Watch"
    assert f.recommendation_cap == "3 - MW"
    assert f.reason == "exposure not determined: no position matches the issuer id or name"
