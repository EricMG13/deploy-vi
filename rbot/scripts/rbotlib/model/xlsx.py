"""`model.xlsx`: the Model as values for the analyst's own spreadsheet (§6.7).

Written with openpyxl (locked by Plan 02, decision record 0003): values only,
no formulas, no macros, no external links. Sheets, in order: `Columns`, one
per band (`01 …` to `12 …`), `House`, `Snapshot`, `Projection` (its header
only until the projection port), `Passport`. A band sheet has the column
labels in row 1, the line label in column A and its `line_id` in column B;
a figure is the Model's value with a number format by unit (money `#,##0.0`,
percentages `0.0%`, multiples `0.00"x"`, days `0.0`); the spreadsheet format
stores a number as an IEEE double, so a figure of more than 15 significant
digits is exact only in model.json. `House` and `Snapshot` hold the same
figures (from the tables' exact `Fig` values), not their display text. A
cell without a figure is blank; the `Passport` sheet gives every cell's
basis, reason and sources, one row per source (and, for a blank cell, its
reason). Every text cell is stored as a string, never as a formula, whatever
its first character.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.cell.cell import Cell as SheetCell
from openpyxl.worksheet.worksheet import Worksheet

from rbotlib.model.snapshot import Fig

CellValue = str | int | float | Decimal | None
SHEET_BANDS = (
    "01 Operating KPIs",
    "02 Revenue by business unit",
    "03 Gross profit",
    "04 Opex to EBITDA",
    "05 Adjusted EBITDA",
    "06 Adj. EBITDA to FCF",
    "07 Net cash flow and liquidity",
    "08 Debt stack by rank",
    "09 Debt roll-forward",
    "10 Interest calculation",
    "11 Working capital",
    "12 Credit metrics",
)
FORMATS = {
    "MONEY": "#,##0.0",
    "PERCENT": "0.0%",
    "RATE": "0.00%",
    "MULTIPLE": '0.00"x"',
    "DAYS": "0.0",
    "SHARE": '0.0"%"',  # a percentage already
}
PASSPORT = "sheet row column line_id column_id basis reason source locator excerpt".split()
COLUMN_KEYS = "column_id kind label period_id fiscal_year end_date days case".split()
SNAPSHOT_KEYS = "section line line_id unit_label fy_2 fy_1 fy pytd ytd ltm".split()
HOUSE_KEYS = "item value unit_label column_id formula components reason".split()


def _sheet(book: Workbook, title: str) -> Worksheet:
    sheet = book.create_sheet(title)
    if not isinstance(sheet, Worksheet):
        raise TypeError(f"openpyxl made {title!r} a {type(sheet).__name__}, not a worksheet")
    return sheet


def _put(sheet: Worksheet, row: int, column: int, value: CellValue) -> SheetCell:
    """The cell holding `value`; a string is stored as a string (openpyxl
    would store one starting with `=` as a formula)."""
    target = sheet.cell(row, column)
    if not isinstance(target, SheetCell):
        raise TypeError(f"{sheet.title} row {row} column {column} is a merged cell")
    target.value = value
    if isinstance(value, str):
        target.data_type = "s"
    return target


def _passport(passport: Worksheet, where: list[Any], cell: Mapping[str, Any]) -> None:
    """One `Passport` row per source of the cell; one row without a source when
    it has none."""
    why = [cell["column_id"], cell["basis"], cell["reason"]]
    for source in cell["sources"] or [None]:
        found = (None, None, None)
        if source is not None:
            found = (source["source"], source["locator"], source["excerpt"])
        _row(passport, [*where, *why, *found])


def _row(sheet: Worksheet, values: Sequence[CellValue]) -> None:
    """Append a row; every text cell is stored as a string."""
    cells: list[CellValue | SheetCell] = []
    for value in values:
        if isinstance(value, str):
            target = SheetCell(sheet, row=1, column=1, value=value)
            target.data_type = "s"
            cells.append(target)
        else:
            cells.append(value)
    sheet.append(cells)


def _band(sheet: Worksheet, model: Mapping[str, Any], band: int, passport: Worksheet) -> None:
    _row(sheet, ["Line", "line_id", *(c["label"] for c in model["columns"])])
    for line in (x for x in model["lines"] if x["band"] == band):
        row = sheet.max_row + 1
        _put(sheet, row, 1, line["label"])
        _put(sheet, row, 2, line["line_id"])
        for n, cell in enumerate(line["cells"], 3):
            if cell["value"] is not None:
                target = _put(sheet, row, n, Decimal(cell["value"]))
                target.number_format = FORMATS.get(line["unit"], "General")
            _passport(passport, [sheet.title, row, n, line["line_id"]], cell)


def _table(
    sheet: Worksheet,
    columns: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
    passport: Worksheet | None = None,
    label: str = "",
) -> None:
    """A table sheet: a figure (`Fig`) as its value with the unit's number
    format, a gap blank (its reason in `Passport`), any other cell as text."""
    _row(sheet, list(columns))
    for row in rows:
        at = sheet.max_row + 1
        for n, name in enumerate(columns, 1):
            value = row.get(name)
            if not isinstance(value, Fig):
                _put(sheet, at, n, value)
            elif value.value is not None:
                _put(sheet, at, n, value.value).number_format = FORMATS.get(value.unit, "General")
            elif passport is not None:
                where: list[CellValue] = [sheet.title, at, n, str(row.get(label, "")), name]
                _row(passport, [*where, None, value.reason, None, None, None])


def workbook(
    model: Mapping[str, Any],
    house: Sequence[Mapping[str, Any]],
    snapshot: Sequence[Mapping[str, Any]],
) -> bytes:
    """The workbook's bytes from `model.json`'s data and the `model.house` and
    `snapshot.financials` rows."""
    book = Workbook()
    book.remove(book.worksheets[0])
    columns = _sheet(book, "Columns")
    bands = [_sheet(book, name) for name in SHEET_BANDS]
    house_sheet = _sheet(book, "House")
    snapshot_sheet = _sheet(book, "Snapshot")
    projection = _sheet(book, "Projection")
    passport = _sheet(book, "Passport")
    _row(passport, PASSPORT)
    _table(columns, COLUMN_KEYS, model["columns"])
    for number, sheet in enumerate(bands, 1):
        _band(sheet, model, number, passport)
    _table(house_sheet, HOUSE_KEYS, house, passport, "item")
    _table(snapshot_sheet, SNAPSHOT_KEYS, snapshot, passport, "line_id")
    _row(projection, ["case", "fiscal_year", "column_id", "note"])
    _row(projection, [None, None, None, "no projection run"])
    buffer = BytesIO()
    book.save(buffer)
    return buffer.getvalue()
