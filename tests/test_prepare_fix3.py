"""02G round 3: corrupt package indices, exception boundary and conditional formats."""

import io
import zipfile
from pathlib import Path

import pytest
from test_prepare_fix1 import _book, _prep

from rbotlib import prepare


@pytest.mark.parametrize("damage", ["style", "shared"])
def test_corrupt_index_is_unreadable(tmp_path: Path, damage: str) -> None:
    raw = _book([["note", 1500]], {"B1": "0,"})
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as src, zipfile.ZipFile(out, "w") as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename.endswith("sheet1.xml"):
                if damage == "style":
                    data = data.replace(b's="1"', b's="999"')
                else:
                    data = data.replace(
                        b'<c r="A1" t="inlineStr"><is><t>note</t></is></c>',
                        b'<c r="A1" t="s"><v>99999</v></c>',
                    )
            dst.writestr(info, data)
    _, index, code = _prep(tmp_path, {"bad.xlsx": out.getvalue(), "ok.txt": b"fine"})
    assert code == 0 and index["ok.txt"]["prepared"]
    assert index["bad.xlsx"]["unreadable"] == (
        "openpyxl could not read the workbook: list index out of range"
    )


def test_rbot_value_error_propagates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "w.xlsx"
    path.write_bytes(_book([[1]], {}))

    def fail(*args: object) -> prepare.Prepared:
        raise ValueError("RBOT defect")

    monkeypatch.setattr(prepare, "_sheet_pages", fail)
    with pytest.raises(ValueError, match="RBOT defect"):
        prepare.read_xlsx(path)


@pytest.mark.parametrize("fmt", ["[>=1000]0,;0", "[<0]0%;0", "0;[Red][>100]0,"])
def test_conditional_sections_read_raw(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fmt: str
) -> None:
    run, index, code = _prep(tmp_path, {"w.xlsx": _book([["n", 1500]], {"B1": fmt})})
    assert code == 0 and prepare.cell_text(1500, fmt) == "1500"
    assert index["w.xlsx"]["format_not_applied"] == {"Sheet": ["B1"]}
    assert index["w.xlsx"]["display_scaled"] == {}
    assert "n,1500" in (run / index["w.xlsx"]["prepared"]).read_text()
    assert "conditional format not applied" in capsys.readouterr().out


def test_path_hash_is_sixteen_hex() -> None:
    name = prepare.prepared_name({"path": "x/a.txt", "sha256": "ab" * 32})
    assert len(name.split("-")[1]) == 16


def test_workbook_loader_keeps_read_only_mode(tmp_path: Path) -> None:
    path = tmp_path / "w.xlsx"
    path.write_bytes(_book([["n", 5]], {}))
    book = prepare._load_xlsx(path, True)
    try:
        assert book.read_only is True and book.data_only is True
    finally:
        book.close()
