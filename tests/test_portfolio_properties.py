"""Property tests for the money parsing: units never mix, bare numbers are never guessed."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rbotlib.portfolio import Table, _limit_row, number, parse_limit
from rbotlib.prepare import cell_text, clean_cell

AMOUNTS = st.builds(lambda n, k: Decimal(n).scaleb(-k), st.integers(0, 10**14), st.integers(0, 12))
SUFFIXES = [("", ""), ("%", "%"), (" yrs", "years"), (" Years", "years"), (" bps", "bps")]
# limit text, parameter, unit of the limit, suffix a current value must carry
LIMITS = [
    ("≤ 2.5% NAV", "Max x", "pct_nav", "%"),
    ("≤ 15% par", "Max x", "pct_par", "%"),
    ("≤ 8 years", "Max x", "years", "years"),
    ("≤ $5,000,000", "Max x", "amount", ""),
    ("≤ 25", "Max number of issuers", "count", ""),
]


def plain(d: Decimal) -> str:
    return format(d, "f")


@given(d=AMOUNTS, suffix=st.sampled_from(SUFFIXES), dollar=st.sampled_from(["", "$"]))
def test_a_unit_round_trips_and_nothing_is_scaled(
    d: Decimal, suffix: tuple[str, str], dollar: str
) -> None:
    assert number(f"{dollar}{plain(d)}{suffix[0]}") == (plain(d), suffix[1])
    assert number(f"{d:,f}{suffix[0]}") == (plain(d), suffix[1])


@given(d=AMOUNTS, current=st.sampled_from(SUFFIXES), limit=st.sampled_from(LIMITS))
def test_percent_fraction_and_bps_are_never_mixed(
    d: Decimal, current: tuple[str, str], limit: tuple[str, str, str, str]
) -> None:
    text, parameter, kind, expected = limit
    item = {"breach type": "Hard", "limit": text, "parameter": parameter}
    item["current value"] = plain(d) + current[0]
    result = _limit_row(Table("t", [], 0, {}), 2, item, [])
    if current[1] == expected:
        assert isinstance(result, dict) and result["unit"] == kind
        assert result["current_value"] == plain(d)
    else:
        assert isinstance(result, str) and "not converted" in result


@given(d=AMOUNTS)
def test_a_bare_limit_number_is_never_guessed(d: Decimal) -> None:
    assert parse_limit(f"≤ {plain(d)}", "Max x") == f"limit '≤ {plain(d)}': unit not recognised"
    assert parse_limit(f"≤ {plain(d)}", "Max number of names") == (plain(d), "count")
    assert parse_limit(f"≤ ${plain(d)}", "Max x") == (plain(d), "amount")


@given(n=st.integers(-(10**9), 10**9), k=st.integers(0, 8))
def test_a_percent_cell_in_xlsx_and_the_csv_text_are_the_same(n: int, k: int) -> None:
    shown = plain((Decimal(n).scaleb(2 - k)).normalize()) + "%"
    assert cell_text(float(Decimal(n).scaleb(-k)), "0.00%") == clean_cell(shown) == shown
    assert number(shown) == (shown[:-1], "%")


@given(
    v=st.floats(allow_nan=False, allow_infinity=False), fmt=st.sampled_from(["General", "0.00%"])
)
def test_floats_are_never_written_in_scientific_notation(v: float, fmt: str) -> None:
    text = cell_text(v, fmt)
    assert "e" not in text.lower()
    assert Decimal(text.rstrip("%")) == (Decimal(repr(v)) * (100 if "%" in fmt else 1))


@pytest.mark.parametrize("text", ["0.0000001", "0.0000001%", "1000000000000"])
def test_number_text_is_never_scientific(text: str) -> None:
    parsed = number(text)
    assert parsed is not None and "e" not in parsed[0].lower()


def test_a_decimal_cell_is_never_scientific() -> None:
    assert clean_cell(Decimal("1E-7")) == "0.0000001"
    assert clean_cell(Decimal("1E+3")) == "1000"
