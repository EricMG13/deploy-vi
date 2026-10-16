from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from builders import make_run
from rbotlib.cli import main
from rbotlib.prepare import clean_cell, load_index


def _run(pack: Path) -> tuple[Path, dict[str, dict[str, object]]]:
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run, {str(r["path"]): r for r in load_index(run)["files"]}


def test_spreadsheet_errors_and_blanks_are_empty_cells() -> None:
    for marker in ("#N/A", "#N/A N/A", "#N/A Field Not Applicable", "#VALUE!", "#DIV/0!"):
        assert clean_cell(marker) == ""
    for blank in ("#NAME?", "—", "  "):
        assert clean_cell(blank) == ""
    assert clean_cell(None) == ""
    assert clean_cell(99.5) == "99.5"
    assert clean_cell(True) == "TRUE"
    assert clean_cell(datetime(2026, 10, 2)) == "2026-10-02"
    assert clean_cell(datetime(2026, 10, 2, 9, 30)) == "2026-10-02T09:30:00"


def test_csv_becomes_one_sheet_page_with_markers_emptied(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    csv_text = "SYNTHETIC levels\nTicker,Bid,Ask\nCZR TLB,#N/A,99.75\nMGM 2032,#N/A N/A,\n\n"
    (pack / "levels.csv").write_text(csv_text, encoding="utf-8")
    run, index = _run(pack)
    record = index["levels.csv"]
    assert record["sheets"] == ["levels"] and record["pages"] == 1
    text = (run / str(record["prepared"])).read_text(encoding="utf-8")
    assert text == (
        "<<< page 1 >>>\n<<< sheet levels >>>\nSYNTHETIC levels\nTicker,Bid,Ask\n"
        "CZR TLB,,99.75\nMGM 2032\n"
    )


def test_each_workbook_sheet_is_a_page_of_stored_values(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    book = Workbook()
    rv = book.active
    assert rv is not None
    rv.title = "Gaming"
    rv.append(["SYNTHETIC Sector RV"])
    rv.append(["Company", "Margin", "Mid 3Y DM", "Maturity"])
    rv.append(["Caesars", 225, "#N/A N/A", datetime(2031, 2, 6)])
    book.create_sheet("Index Statistics").append(["Index", "3Y DM"])
    book.save(pack / "rv.xlsx")
    (pack / "broken.xlsx").write_bytes(b"PK not a workbook")
    run, index = _run(pack)
    record = index["rv.xlsx"]
    assert record["sheets"] == ["Gaming", "Index Statistics"] and record["pages"] == 2
    text = (run / str(record["prepared"])).read_text(encoding="utf-8")
    assert "<<< page 1 >>>\n<<< sheet Gaming >>>\nSYNTHETIC Sector RV\n" in text
    assert "Caesars,225,,2031-02-06\n" in text
    assert text.endswith("<<< page 2 >>>\n<<< sheet Index Statistics >>>\nIndex,3Y DM\n")
    assert str(index["broken.xlsx"]["unreadable"]).startswith("openpyxl could not read")


def test_an_image_is_an_image_read_stub(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "SYNTHETIC_Levels_Screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    run, index = _run(pack)
    record = index["SYNTHETIC_Levels_Screenshot.png"]
    assert record["image_read"] is True and record["pages"] == 1 and record["excerpt"] == ""
    assert (run / str(record["prepared"])).read_text(encoding="utf-8") == "<<< page 1 >>>\n"
