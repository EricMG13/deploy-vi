"""02G fix round 2: bounded number formats, shared prepared names, surrogate pairs."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest
from test_prepare_fix1 import _book, _damaged_xlsx, _prep

from rbotlib import prepare
from rbotlib.cli import main
from rbotlib.prepare import _drop_surrogates, cell_text, load_index, prepared_name


def _with_big_integer(book: bytes, big: int) -> bytes:
    """The workbook with its 123456789 cell rewritten (openpyxl will not write such an int)."""
    src = zipfile.ZipFile(io.BytesIO(book))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.endswith("sheet1.xml"):
                data = data.replace(b"<v>123456789</v>", f"<v>{big}</v>".encode())
            z.writestr(info, data)
    return out.getvalue()


def test_n5_an_integer_cell_of_401_digits_is_read_whole(tmp_path: Path) -> None:
    big = 10**400
    book = _with_big_integer(_book([["note", 123456789]], {}), big)
    run, index, code = _prep(tmp_path, {"w.xlsx": book})
    record = index["w.xlsx"]
    assert code == 0 and record["unreadable"] is None
    assert f"note,{big}\n" in (run / record["prepared"]).read_text(encoding="utf-8")
    assert cell_text(big, "General") == str(big)
    assert cell_text(big, "#,##0,,") == str(big // 10**6)


def test_n5_a_format_with_500_decimal_places_is_not_applied_and_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fmt = "0." + "0" * 500 + ","
    run, index, code = _prep(tmp_path, {"w.xlsx": _book([["note", 1.5]], {"B1": fmt})})
    record = index["w.xlsx"]
    assert code == 0 and record["format_not_applied"] == {
        "Sheet": ["B1 (more than 20 decimal places)"]
    }
    assert record["display_scaled"] == {}
    assert "note,1.5\n" in (run / record["prepared"]).read_text(encoding="utf-8")
    out = capsys.readouterr().out
    assert "number format not applied (read as stored): w.xlsx sheet Sheet: B1 (more" in out


def test_n5_twenty_decimal_places_are_still_applied() -> None:
    assert cell_text(1500, "0." + "0" * 20 + ",") == "1.5"


def test_c1_a_conditional_format_is_not_applied_and_is_listed(tmp_path: Path) -> None:
    fmt = "[<1]0.00%;0.0,,"
    book = _book([["a", 0.0095], ["b", 6000000]], {"B1": fmt, "B2": fmt})
    run, index, _ = _prep(tmp_path, {"w.xlsx": book})
    record = index["w.xlsx"]
    assert record["format_not_applied"] == {
        "Sheet": ["B1 (conditional format)", "B2 (conditional format)"]
    }
    assert "a,0.0095\nb,6000000\n" in (run / record["prepared"]).read_text(encoding="utf-8")
    assert record["display_scaled"] == {}


def test_c1_a_condition_inside_quotes_is_text_not_a_condition() -> None:
    assert cell_text(1234567, '#,##0.0,,"[<1]"') == "1.2"
    assert cell_text(0.5, "[Red]0%") == "50%"


def test_n2_a_cell_whose_format_was_not_applied_makes_the_amount_unit_uncertain(
    tmp_path: Path,
) -> None:
    rows: list[list[Any]] = [["Portfolio ID", "P1"], ["Strategy", "CLO"], ["As of", "2026-05-29"]]
    rows += [["Unit", "USD"], ["Total NAV", 630900000], ["Total Par", 634000000], []]
    rows += [["Issuer ID", "Issuer", "Par", "% NAV"], ["CZR", "Caesars", 6000000, "0.95%"]]
    lim = "Portfolio ID,P1\n\nID,Constraint Category,Parameter,Limit,Breach Type,Current Value\n"
    lim += 'C-01,Single Name,Max x,"≤ $25,000,000",Hard,"$6,000,000"\n'
    book = _book(rows, {"B5": "[>=1]0.0,,;0"})
    run, index, _ = _prep(tmp_path, {"w.xlsx": book, "l.csv": lim.encode()})
    assert index["w.xlsx"]["format_not_applied"] == {"Sheet": ["B5 (conditional format)"]}
    data = json.loads((run / "prepared/portfolios/P1.json").read_text(encoding="utf-8"))
    assert data["limits"] == [] and data["nav"] == "630900000"
    assert [u["reason"] for u in data["unparsed"]] == [
        "values are display-scaled; the amount unit is not certain"
    ]


def test_m1_two_identical_files_at_different_paths_have_different_prepared_names(
    tmp_path: Path,
) -> None:
    files = {"a.txt": b"same body\n", "archive/a.txt": b"same body\n", "b.txt": b"bravo\n"}
    pack = tmp_path / "pack"
    (pack / "archive").mkdir(parents=True)
    run, index, _ = _prep(tmp_path, files)
    assert index["a.txt"]["prepared"] != index["archive/a.txt"]["prepared"]
    (pack / "a.txt").write_bytes(b"a.txt edited, new content now\n")
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run), "--only", "a.txt"]) == 0
    again = {r["path"]: r for r in load_index(run)["files"]}
    assert (run / again["archive/a.txt"]["prepared"]).is_file()
    assert (run / again["a.txt"]["prepared"]).is_file()


def test_m1_the_name_is_content_path_hash_and_slug() -> None:
    entry = {"sha256": "ab" * 32, "path": "x/Q1 Report.txt"}
    name = prepared_name(entry)
    assert name.startswith("prepared/" + "ab" * 8 + "-") and name.endswith("-q1-report-txt.txt")
    assert len(name.split("-")[1]) == 8
    assert name != prepared_name(entry | {"path": "y/Q1 Report.txt"})
    assert name == prepared_name(dict(entry))


def test_surrogate_pairs_are_joined_and_lone_ones_dropped() -> None:
    pages = ["x\ud835\udc65y", "\ud83d\ude00", "a\ud83d\ude00b\ud83d", "\ude00\ud83d\ude00Z"]
    texts, dropped = _drop_surrogates([*pages, "p\udc65\ud835q", "\ud83d\ud83d\ude00"])
    assert texts == [
        "x\U0001d465y",
        "\U0001f600",
        "a\U0001f600b",
        "\U0001f600Z",
        "pq",
        "\U0001f600",
    ]
    assert dropped == 0 + 0 + 1 + 1 + 2 + 1


def test_an_error_of_rbots_own_is_not_swallowed_as_an_unreadable_workbook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(value: object, number_format: str | None) -> str:
        raise ValueError("a bug of ours")

    monkeypatch.setattr(prepare, "cell_text", boom)
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "w.xlsx").write_bytes(_book([["a", 1]], {}))
    with pytest.raises(ValueError, match="a bug of ours"):
        prepare.read_xlsx(pack / "w.xlsx")


def test_damaged_workbooks_are_still_listed_as_unreadable(tmp_path: Path) -> None:
    _, index, code = _prep(tmp_path, _damaged_xlsx())
    assert code == 0
    for name in ("malformed.xlsx", "deflate.xlsx"):
        assert index[name]["unreadable"].startswith("openpyxl could not read the workbook")
