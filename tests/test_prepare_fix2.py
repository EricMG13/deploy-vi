"""02G fix round 2: bounded number formats, shared prepared names, surrogate pairs."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest
from test_prepare_fix1 import _book, _prep

from rbotlib.cli import main
from rbotlib.prepare import _drop_surrogates, cell_text, load_index, prepared_name, read_csv

MANY = "0." + "0" * 500 + ","  # a scaling format with 500 decimal places


def _with_big_integer(book: bytes, big: int) -> bytes:
    """The workbook with its 123456789 cell rewritten (openpyxl will not write such an int)."""
    src, out = zipfile.ZipFile(io.BytesIO(book)), io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.endswith("sheet1.xml"):
                data = data.replace(b"<v>123456789</v>", f"<v>{big}</v>".encode())
            z.writestr(info, data)
    return out.getvalue()


def test_n5_an_integer_cell_of_401_digits_is_read_whole(tmp_path: Path) -> None:
    big = 10**400
    run, index, code = _prep(
        tmp_path, {"w.xlsx": _with_big_integer(_book([["n", 123456789]], {}), big)}
    )
    assert code == 0 and index["w.xlsx"]["unreadable"] is None
    assert f"n,{big}\n" in (run / index["w.xlsx"]["prepared"]).read_text(encoding="utf-8")
    assert cell_text(big, "#,##0,,") == str(big // 10**6)
    assert cell_text(big, "0." + "0" * 20 + ",") == "1" + "0" * 397
    assert cell_text(1234567890123456789012345678500, "0,") == "1234567890123456789012345679"
    assert (
        cell_text(1234567890123456789012345678901234567, "0,")
        == "1234567890123456789012345678901235"
    )
    assert cell_text(1234567, '0"x",') == "1235"  # quoted text between the digit and the comma


def test_n5_a_format_with_500_decimal_places_is_not_applied_and_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run, index, code = _prep(tmp_path, {"w.xlsx": _book([["note", 1.5]], {"B1": MANY})})
    record = index["w.xlsx"]
    assert code == 0 and record["format_not_applied"] == {"Sheet": ["B1"]}
    assert record["display_scaled"] == {}
    assert "note,1.5\n" in (run / record["prepared"]).read_text(encoding="utf-8")
    assert "(read as stored): w.xlsx sheet Sheet: B1" in capsys.readouterr().out
    assert cell_text(1500, "0." + "0" * 20 + ",") == "1.5"


def test_n2_a_cell_whose_format_was_not_applied_makes_the_amount_unit_uncertain(
    tmp_path: Path,
) -> None:
    rows: list[list[Any]] = [["Portfolio ID", "P1"], ["Strategy", "CLO"], ["As of", "2026-05-29"]]
    rows += [["Unit", "USD"], ["Total NAV", 630900000], ["Total Par", 634000000], []]
    rows += [["Issuer ID", "Issuer", "Par", "% NAV"], ["CZR", "Caesars", 6000000, "0.95%"]]
    lim = "Portfolio ID,P1\n\nID,Constraint Category,Parameter,Limit,Breach Type,Current Value\n"
    lim += 'C-01,Single Name,Max x,"≤ $25,000,000",Hard,"$6,000,000"\n'
    files = {"a.xlsx": _book(rows, {"B5": MANY}), "b.csv": lim.encode()}  # scaled table first
    run, index, _ = _prep(tmp_path, files)
    assert index["a.xlsx"]["format_not_applied"] == {"Sheet": ["B5"]}
    data = json.loads((run / "prepared/portfolios/P1.json").read_text(encoding="utf-8"))
    assert data["limits"] == [] and data["nav"] == "630900000"
    assert [u["reason"] for u in data["unparsed"]] == [
        "values are display-scaled; the amount unit is not certain"
    ]


def test_m1_two_identical_files_at_different_paths_have_different_prepared_names(
    tmp_path: Path,
) -> None:
    files = {"a.txt": b"same body\n", "archive/a.txt": b"same body\n", "b.txt": b"bravo\n"}
    (tmp_path / "pack" / "archive").mkdir(parents=True)
    run, index, _ = _prep(tmp_path, files)
    assert index["a.txt"]["prepared"] != index["archive/a.txt"]["prepared"]
    (tmp_path / "pack" / "a.txt").write_bytes(b"a.txt edited, new content now\n")
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run), "--only", "a.txt"]) == 0
    again = {r["path"]: r for r in load_index(run)["files"]}
    assert (run / again["archive/a.txt"]["prepared"]).is_file()
    assert (run / again["a.txt"]["prepared"]).is_file()


def test_a_csv_page_is_written_with_plain_line_breaks(tmp_path: Path) -> None:
    (tmp_path / "s.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    assert read_csv(tmp_path / "s.csv").pages == ["<<< sheet s >>>\na,b\n1,2\n"]


def test_m1_the_name_is_content_path_hash_and_slug() -> None:
    entry = {"sha256": "ab" * 32, "path": "x/Q1 Report.txt"}
    name = prepared_name(entry)
    assert name.startswith("prepared/" + "ab" * 8 + "-") and name.endswith("-q1-report-txt.txt")
    assert len(name.split("-")[1]) == 8
    assert name != prepared_name(entry | {"path": "y/Q1 Report.txt"})
    assert prepared_name(entry | {"path": "\ud800.txt"})  # a lone surrogate in a path is hashed


def test_surrogate_pairs_are_joined_and_lone_ones_dropped() -> None:
    hi, lo, hi2, lo2 = chr(0xD835), chr(0xDC65), chr(0xD83D), chr(0xDE00)  # not literals: ruff
    pages = [f"x{hi}{lo}y", hi2 + lo2, f"a{hi2}{lo2}b{hi2}", f"{lo2}{hi2}{lo2}Z"]  # joins those
    texts, dropped = _drop_surrogates([*pages, f"p{lo}{hi}q", hi2 + hi2 + lo2])
    assert texts == [
        "x\U0001d465y",
        "\U0001f600",
        "a\U0001f600b",
        "\U0001f600Z",
        "pq",
        "\U0001f600",
    ]
    assert dropped == 0 + 0 + 1 + 1 + 2 + 1
