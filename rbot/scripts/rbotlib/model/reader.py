"""Read a Handoff table's cells the way caos's host reads them.

The cell reading of caos `caos/methodology/model_inputs.py` and
`caos/methodology/tables.py` at `5c3cd52f`, over `rbotlib.handoff.Table`s,
refusing with `ModelInputError`, whose message names the table, the row
(1-based, as written) and the column.

A figure cell is read by `figure`, caos's `_exact` rules: citation markers
removed, `(x)` negative (a sign inside the parentheses is refused), a leading
or trailing currency symbol and one trailing `%` or `x` stripped, digit-group
spaces removed (an ordinary space only between groups of three digits, so
`1 2` and `2024 2025` are refused), the separator that comes last is the
decimal one, and `5,2` is refused rather than guessed. A cell holding
null text (`NULL_TEXT`, which includes the gap marker `—`) has no figure; any
other text that is not a figure is refused, never read as null. A figure that
is not finite, `MAX_FIGURE` or more in size, or written to more than
`MAX_DECIMALS` decimals is refused (never rounded); `-0` reads as `0`.

An enumerated column's text names a member of its vocabulary on case and
separators (`_`, `-` and whitespace alike) and reads as that member's
canonical spelling; text naming no member is refused, or read in upper case
where the column is open. A date is `YYYY-MM-DD` from 1900 to 2200.

Pure: no I/O.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TypeVar

from rbotlib.handoff import Table
from rbotlib.model.frame import SourceRef

NULL_TEXT = frozenset(
    {"", "null", "n/a", "not available", "not calculable", "-", "\N{EM DASH}", "\N{EN DASH}"}
)
MAX_FIGURE = Decimal(10) ** 18
MAX_DECIMALS = 10
FIGURE_CHARS = 64
FIRST_YEAR, LAST_YEAR = 1900, 2200
_SEPARATORS = re.compile(r"[\s_-]+")
_LIST_SEPARATOR = re.compile(r"[;,]")
_FOUR_DIGITS = re.compile(r"(?<!\d)\d{4}(?!\d)")
_TWO_YEARS = re.compile(r"(?<!\d)(\d{4})\s*[/-]\s*(\d{4}|\d{2})(?!\d)")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
# caos `citation_markers.unmarked`, for Plan 01's single `[C<n>]` markers.
_IN_CELL = re.compile(r"(?<! )(?: *\[C[0-9]+\])+")
_FIGURE_EDGE = frozenset("0123456789.,")
_SPACES = str.maketrans("", "", "\N{NO-BREAK SPACE}\N{THIN SPACE}\N{NARROW NO-BREAK SPACE}")
_GROUPED = re.compile(r"[-+]?\d{1,3}(?: \d{3})+(?:[.,]\d+)?")
CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")  # openpyxl's illegal characters
_SYMBOLS = "\N{EURO SIGN}$\N{POUND SIGN}\N{YEN SIGN}\N{INDIAN RUPEE SIGN}"
_CURRENCY = re.compile(f"^[{_SYMBOLS}]|[{_SYMBOLS}]$")
_UNIT_SUFFIX = re.compile(r"\s*[xX%]$")
_FIGURE = re.compile(r"[-+]?[0-9][0-9.,]*(?:[eE][-+]?[0-9]+)?")
_ANGLO_THOUSANDS = re.compile(r"^\d{1,3}(,\d{3})+(\.\d+)?$")
_CONTINENTAL = re.compile(r"^\d{1,3}(\.\d{3})+(,\d+)?$")
_AMBIGUOUS_COMMA = re.compile(r"^\d+,\d{1,2}$")

T = TypeVar("T")


class ModelInputError(ValueError):
    """A Model-input table is malformed; the message names table, row and column."""


@dataclass(frozen=True, slots=True)
class Row:
    """One table row keyed by column, with where it was written."""

    table_id: str
    number: int
    cells: Mapping[str, str]

    def refuse(self, column: str, why: str) -> ModelInputError:
        return ModelInputError(f"{self.table_id} row {self.number} column {column}: {why}")


def unmarked(cell: str) -> str:
    """`cell` without its `[C<n>]` markers (and the spaces before them); a
    marker splitting a figure (`4[C1]5`) becomes ` | `, so no figure reads."""

    def replaced(found: re.Match[str]) -> str:
        before = cell[found.start() - 1 : found.start()]
        after = cell[found.end() : found.end() + 1]
        split = before in _FIGURE_EDGE and after in _FIGURE_EDGE
        return " | " if split and not found.group().startswith(" ") else ""

    return _IN_CELL.sub(replaced, cell)


def _separated(core: str) -> str | None:
    body = core.lstrip("-+")
    if "," in core and "." in core:
        if core.rfind(",") > core.rfind("."):
            if not _CONTINENTAL.match(body):
                return None
            return core.replace(".", "").replace(",", ".")
        if not _ANGLO_THOUSANDS.fullmatch(body):
            return None
        return core.replace(",", "")
    if "," in core:
        if _AMBIGUOUS_COMMA.match(body) or not _ANGLO_THOUSANDS.match(body):
            return None
        return core.replace(",", "")
    return core


def figure(cell: str) -> Decimal | None:
    """The cell's exact figure (caos `_exact`), or None when it is not one."""
    text = unmarked(cell).strip()
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1].strip()
        if text[:1] in {"-", "+"}:
            return None
    core = _UNIT_SUFFIX.sub("", _CURRENCY.sub("", text).strip()).translate(_SPACES)
    if " " in core:
        if _GROUPED.fullmatch(core) is None:
            return None
        core = core.replace(" ", "")
    plain = _separated(core) if _FIGURE.fullmatch(core) and len(core) <= FIGURE_CHARS else None
    if plain is None:
        return None
    try:
        value = Decimal(plain)
    except InvalidOperation:
        return None
    return value.copy_negate() if negative else value


def is_null(cell: str) -> bool:
    return unmarked(cell).strip().casefold() in NULL_TEXT


def rows(tables: Mapping[str, Table], table_id: str, required: frozenset[str]) -> list[Row]:
    """The table's rows keyed by column; none for an absent table. Refused for
    a present table missing a `required` column or with a ragged row."""
    table = tables.get(table_id)
    if table is None:
        return []
    twice = sorted({c for c in table.columns if table.columns.count(c) > 1})
    if twice:
        raise ModelInputError(f"{table_id}: column {', '.join(twice)} appears twice")
    missing = sorted(required - set(table.columns))
    if missing:
        raise ModelInputError(f"{table_id}: missing column {', '.join(missing)}")
    found = []
    for number, cells in enumerate(table.rows, 1):
        if len(cells) != len(table.columns):
            width = f"{len(cells)} cells, header has {len(table.columns)}"
            raise ModelInputError(f"{table_id} row {number}: {width}")
        row = Row(table_id, number, dict(zip(table.columns, cells, strict=True)))
        for column, cell in row.cells.items():
            if CONTROL.search(cell):
                raise row.refuse(column, "control character")
        found.append(row)
    return found


def read(
    tables: Mapping[str, Table],
    table_id: str,
    required: frozenset[str],
    reader: Callable[[Row], T],
) -> tuple[T, ...]:
    return tuple(reader(row) for row in rows(tables, table_id, required))


def distinct(
    table_id: str, found: tuple[T, ...], key: Callable[[T], tuple[str, ...]]
) -> tuple[T, ...]:
    """`found`, refused when two rows share a key: one id in one period is one
    figure, never two for the Model to choose between."""
    seen: set[tuple[str, ...]] = set()
    for number, row in enumerate(found, 1):
        k = key(row)
        if k in seen:
            raise ModelInputError(f"{table_id} row {number}: {' / '.join(k)} written twice")
        seen.add(k)
    return found


def text(row: Row, column: str) -> str:
    return unmarked(row.cells[column]).strip()


def optional(row: Row, column: str) -> str | None:
    """The column's text, or None for null text or an absent column."""
    if column not in row.cells:
        return None
    value = text(row, column)
    return None if value.casefold() in NULL_TEXT else value


def required_text(row: Row, column: str) -> str:
    value = optional(row, column)
    if value is None:
        raise row.refuse(column, "required, found null")
    return value


def cite(row: Row, column: str) -> str:
    """A required `cite` column as written, markers kept (`[C3] [C4]`, or
    `calc: <formula>`)."""
    value = row.cells.get(column, "").strip()
    if value.casefold() in NULL_TEXT:
        raise row.refuse(column, "required, found null")
    return value


def _key(value: str) -> str:
    return _SEPARATORS.sub(" ", value.casefold()).strip()


def enum(row: Row, column: str, vocabulary: frozenset[str], *, closed: bool = True) -> str:
    """A required enumerated column in its canonical spelling; text naming no
    member reads in upper case where the column is open (`closed=False`).
    Refused when null or, for a closed vocabulary, naming no member."""
    value = text(row, column) if column in row.cells else ""
    key = _key(value)
    member = next((m for m in vocabulary if _key(m) == key), None)
    if member is not None:
        return member
    if value.casefold() in NULL_TEXT:
        raise row.refuse(column, "required, found null")
    if closed:
        raise row.refuse(column, f"{value!r} is not one of {sorted(vocabulary)}")
    return value.upper()


def decimal(row: Row, column: str) -> Decimal | None:
    """The column's figure; None for null text or an absent column."""
    if column not in row.cells or is_null(row.cells[column]):
        return None
    value = figure(row.cells[column])
    if value is None:
        raise row.refuse(column, f"{row.cells[column]!r} is not a figure")
    if not value.is_finite() or abs(value) >= MAX_FIGURE:
        raise row.refuse(column, "figure out of range")
    if -int(value.as_tuple().exponent) > MAX_DECIMALS:
        raise row.refuse(column, f"more than {MAX_DECIMALS} decimals")
    return value.copy_abs() if value.is_zero() else value


def required_decimal(row: Row, column: str) -> Decimal:
    value = decimal(row, column)
    if value is None:
        raise row.refuse(column, "required, found null")
    return value


def integer(row: Row, column: str) -> int | None:
    value = decimal(row, column)
    if value is None:
        return None
    if value != value.to_integral_value():
        raise row.refuse(column, "not a whole number")
    return int(value)


def ids(row: Row, column: str) -> tuple[str, ...]:
    """A `;`- or `,`-separated list of ids; none for null text."""
    value = optional(row, column)
    if value is None:
        return ()
    return tuple(part.strip() for part in _LIST_SEPARATOR.split(value) if part.strip())


def source(row: Row, figure_column: str) -> SourceRef | None:
    """Where the row's figure came from, its cell text verbatim; None when the
    row names no source. `source_id` holds citation markers (`[C12]`), so it
    is read as written, never unmarked."""
    source_id = row.cells.get("source_id", "").strip()
    if source_id.casefold() in NULL_TEXT:
        return None
    return SourceRef(
        source_id=source_id,
        source_locator=optional(row, "source_locator") or "",
        cell_text=row.cells[figure_column],
    )


def _end_year(start: str, end: str) -> int | None:
    first = int(start)
    if len(end) == 4:
        return int(end) if int(end) == first + 1 else None
    return first + 1 if int(end) == (first + 1) % 100 else None


def fiscal_year_number(value: str) -> int | None:
    """A fiscal year's four-digit year: a two-year spelling's END year
    (`FY2025/26` is 2026), else the last run of exactly four digits."""
    for start, end in reversed(_TWO_YEARS.findall(value)):
        year = _end_year(start, end)
        if year is not None:
            return year
    runs = _FOUR_DIGITS.findall(value)
    return int(runs[-1]) if runs else None


def iso_date(value: str | None) -> date | None:
    """`value` as a calendar date where it is exactly `YYYY-MM-DD`; else None."""
    if value is None or _ISO_DATE.fullmatch(value) is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:  # `2025-02-30`: no such day
        return None


def date_cell(row: Row, column: str) -> date | None:
    """The column's date; None for null text; refused when it is not a
    `YYYY-MM-DD` calendar date from 1900 to 2200."""
    value = optional(row, column)
    if value is None:
        return None
    day = iso_date(value)
    if day is None or not FIRST_YEAR <= day.year <= LAST_YEAR:
        raise row.refuse(column, f"{value!r} is not a YYYY-MM-DD date in 1900-2200")
    return day
