"""Cell reading with caos's host rules; every refusal names where."""

from __future__ import annotations

import re
from contextlib import AbstractContextManager
from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rbotlib.handoff import Table
from rbotlib.model import registers
from rbotlib.model.frame import SourceRef
from rbotlib.model.reader import (
    ModelInputError,
    Row,
    cite,
    date_cell,
    decimal,
    distinct,
    enum,
    figure,
    fiscal_year_number,
    ids,
    integer,
    iso_date,
    optional,
    read,
    required_decimal,
    required_text,
    rows,
    source,
    unmarked,
)


def _row(**cells: str) -> Row:
    return Row("cp1.example", 3, cells)


def _refused(match: str) -> AbstractContextManager[pytest.ExceptionInfo[ModelInputError]]:
    return pytest.raises(ModelInputError, match=re.escape(match))


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("1,250.0", "1250.0"),
        ("(45) [C1]", "-45"),
        ("$1,234", "1234"),
        ("12.5%", "12.5"),
        ("4.2x", "4.2"),
        ("1.234,5", "1234.5"),
        ("-0.25", "-0.25"),
        ("1\N{NO-BREAK SPACE}234", "1234"),
        ("\N{EURO SIGN}12", "12"),
        ("1e3", "1000"),
    ],
)
def test_figure_reads_caos_exact_rules(text: str, value: str) -> None:
    assert figure(text) == Decimal(value)


@pytest.mark.parametrize("text", ["5,2", "abc", "4[C1]5", "1.2.3", "12,34.5", "1,2.345,6", ""])
def test_figure_refuses_what_it_will_not_guess(text: str) -> None:
    assert figure(text) is None


@given(st.decimals(min_value=Decimal("-1e15"), max_value=Decimal("1e15"), places=6))
def test_a_written_figure_reads_back_exactly(value: Decimal) -> None:
    assert figure(f"{value:,f}") == value
    if value:
        assert figure(f"({abs(value):,f})") == -abs(value)


def test_unmarked_keeps_a_split_figure_split() -> None:
    assert unmarked("(45) [C1]") == "(45)"
    assert unmarked("4[C1]5") == "4 | 5"
    assert unmarked("[C2] text") == " text"


def test_decimal_reads_null_as_none_and_refuses_the_rest_naming_where() -> None:
    assert decimal(_row(value="—"), "value") is None
    assert decimal(_row(), "value") is None
    zero = decimal(_row(value="(0)"), "value")
    assert zero is not None and zero == 0 and not zero.is_signed()
    with _refused("cp1.example row 3 column value: 'about 2bn' is not a figure"):
        decimal(_row(value="about 2bn"), "value")
    with _refused("cp1.example row 3 column value: figure out of range"):
        decimal(_row(value="1e18"), "value")
    with _refused("column value: figure out of range"):
        decimal(_row(value="1e999999x"), "value")
    with _refused("column value: more than 10 decimals"):
        decimal(_row(value="0.12345678901"), "value")
    with _refused("column value: required, found null"):
        required_decimal(_row(value="n/a"), "value")
    with _refused("column value: not a whole number"):
        integer(_row(value="1.5"), "value")
    assert integer(_row(value="2"), "value") == 2
    assert integer(_row(value="—"), "value") is None


def test_enum_reads_canonical_spellings_closed_or_open() -> None:
    vocabulary = frozenset({"SUPER_SENIOR", "SENIOR"})
    assert enum(_row(s="super senior"), "s", vocabulary) == "SUPER_SENIOR"
    assert enum(_row(s="Super-Senior"), "s", vocabulary) == "SUPER_SENIOR"
    with _refused("column s: 'Senior secured' is not one of ['SENIOR', 'SUPER_SENIOR']"):
        enum(_row(s="Senior secured"), "s", vocabulary)
    with _refused("column s: required, found null"):
        enum(_row(s="—"), "s", vocabulary)
    with _refused("column s: required, found null"):
        enum(_row(), "s", vocabulary)
    open_vocabulary = frozenset({"DEBT ADJUSTMENT"})
    assert enum(_row(t="debt_adjustment"), "t", open_vocabulary, closed=False) == "DEBT ADJUSTMENT"
    assert enum(_row(t="Term loan"), "t", open_vocabulary, closed=False) == "TERM LOAN"


def test_text_columns() -> None:
    assert optional(_row(a="n/a"), "a") is None
    assert optional(_row(), "a") is None
    assert optional(_row(a=" x [C1]"), "a") == "x"
    with _refused("column a: required, found null"):
        required_text(_row(a="—"), "a")
    assert ids(_row(a="Q1; Q2,Q3"), "a") == ("Q1", "Q2", "Q3")
    assert ids(_row(a="—"), "a") == ()


def test_cite_keeps_markers_and_refuses_null() -> None:
    assert cite(_row(cite=" [C3] [C4] "), "cite") == "[C3] [C4]"
    assert cite(_row(cite="calc: a / b"), "cite") == "calc: a / b"
    with _refused("cp1.example row 3 column cite: required, found null"):
        cite(_row(cite="—"), "cite")
    with _refused("column cite: required, found null"):
        cite(_row(), "cite")


def test_source_keeps_markers_and_cell_text_verbatim() -> None:
    row = _row(source_id="[C12] [C13]", source_locator="p.61", value="1,234 [C12]")
    assert source(row, "value") == SourceRef("[C12] [C13]", "p.61", "1,234 [C12]")
    assert source(_row(source_id="—", value="1"), "value") is None
    assert source(_row(value="1"), "value") is None
    assert source(_row(source_id="[C1]", value="1"), "value") == SourceRef("[C1]", "", "1")


def test_dates() -> None:
    assert date_cell(_row(d="2025-12-31"), "d") == date(2025, 12, 31)
    assert date_cell(_row(d="—"), "d") is None
    for bad in ("2025-02-30", "31/12/2025", "1899-12-31"):
        with _refused(f"column d: {bad!r} is not a YYYY-MM-DD date in 1900-2200"):
            date_cell(_row(d=bad), "d")
    assert iso_date("2025-13-01") is None
    assert iso_date(None) is None


def test_fiscal_years() -> None:
    assert fiscal_year_number("FY2025/26") == 2026
    assert fiscal_year_number("2025-2026") == 2026
    assert fiscal_year_number("FY2025") == 2025
    assert fiscal_year_number("2025/27") == 2025
    assert fiscal_year_number("FY") is None


def test_rows_read_absent_tables_as_none_and_refuse_bad_shapes() -> None:
    tables = {"t": Table(["a", "b"], [["1", "2"]])}
    assert rows(tables, "absent", frozenset({"a"})) == []
    assert read(tables, "t", frozenset({"a"}), lambda r: r.cells["b"]) == ("2",)
    with _refused("t: missing column c"):
        rows(tables, "t", frozenset({"a", "c"}))
    with _refused("t row 1: 1 cells, header has 2"):
        rows({"t": Table(["a", "b"], [["1"]])}, "t", frozenset())


def test_distinct_refuses_a_key_written_twice() -> None:
    assert distinct("t", ("a", "b"), lambda x: (x,)) == ("a", "b")
    with _refused("t row 2: a / P written twice"):
        distinct("t", ("a", "a"), lambda x: (x, "P"))


def test_registers_hold_the_closed_vocabularies_and_reexport_the_date_helpers() -> None:
    assert registers.iso_date is iso_date and registers.fiscal_year_number is fiscal_year_number
    for vocabulary in (
        registers.PERIOD_TYPES,
        registers.SENIORITIES,
        registers.REALIZATION_STATUSES,
    ):
        assert isinstance(vocabulary, frozenset) and vocabulary
    assert {"FY", "LTM"} <= registers.PERIOD_TYPES
