# 0003 — openpyxl for workbook values

**Need:** `rbot prepare` turns every sheet of an `.xlsx` Source Pack file (the Sector RV Workbook, Bloomberg exports, portfolio files) into CSV rows of stored values, so modules cite cells and `#N/A`-style markers become empty cells (interfaces spec section 8.1, design D15). The owner retired Model workbook exports on 2026-10-13; openpyxl remains required for supplied source inputs.

**Order of preference (global rule):** CSV files use the standard library `csv` module. The standard library can unzip an `.xlsx` (`zipfile` + `xml.etree`), but resolving shared strings, inline strings, styles-dependent dates, cached formula results and sheet relationships correctly is a parser of its own, more code than this plan's whole intake. No locked dependency reads workbooks. So a new runtime dependency.

**Choice:** `openpyxl` — pure Python, MIT, the reference reader for `.xlsx`, one dependency (`et-xmlfile`, pure Python, MIT), and the library the Copilot spike installs (`pip install --user pypdf openpyxl`, Plan 01 Task 2). Read with `load_workbook(path, read_only=True, data_only=True)`: stored values only, formulas never recalculated (a Bloomberg `BDP` cell keeps its cached result), no macros, no external links. Old binary `.xls` stays unsupported and is listed as unreadable.

**Versions:** `openpyxl==3.1.5` (released 2024-06-28; no known advisory); it pulls `et-xmlfile==2.0.0` (2024-10-25). Dev only: `types-openpyxl==3.1.5.20260827` (released 2026-08-27, typeshed stubs) so `mypy --strict` checks the calls instead of a suppression. All three are older than 30 days on 2026-10-11 and pass `pip-audit --strict`.

**Failure handling:** a workbook openpyxl cannot open (`InvalidFileException`, `BadZipFile`, `KeyError`, `ValueError`, `OSError`) is listed as unreadable with the error text; the rest of the pack is still prepared.
