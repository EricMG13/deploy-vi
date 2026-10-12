from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import make_pdf, make_run
from conftest import CORPUS
from rbotlib.cli import main
from rbotlib.prepare import dates, entities, load_index

SEC_COVER = (
    "Commission File No. 001-36629\nCAESARS ENTERTAINMENT, INC.\n"
    "(Exact name of registrant as specified in its charter)\nDelaware corporation\n"
    "For the quarterly period ended June 30, 2026"
)


def _prepared(tmp_path: Path, files: dict[str, bytes]) -> tuple[Path, dict[str, dict[str, Any]]]:
    pack = tmp_path / "pack"
    pack.mkdir()
    for name, data in files.items():
        (pack / name).write_bytes(data)
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    return run, {r["path"]: r for r in load_index(run)["files"]}


def _text(run: Path, record: dict[str, Any]) -> str:
    return (run / str(record["prepared"])).read_text(encoding="utf-8")


def test_text_markdown_and_html_become_page_anchored_text(tmp_path: Path) -> None:
    html = b"<html><style>p{}</style><p>Net revenue</p><table><tr><td>Q2</td><td>2,993</td></tr>"
    run, index = _prepared(
        tmp_path,
        {
            "CZR_10Q.txt": (SEC_COVER + "\fpage two text\n").encode(),
            "note.md": b"# Note\nOne page only.\n",
            "release.html": html + b"</table><script>alert(1)</script></html>",
        },
    )
    tenq = index["CZR_10Q.txt"]
    assert tenq["pages"] == 2 and tenq["kind"] == "txt"
    assert re.fullmatch(
        rf"prepared/{tenq['sha256'][:16]}-[0-9a-f]{{8}}-czr-10q-txt\.txt", tenq["prepared"]
    )
    assert _text(run, tenq).endswith("<<< page 2 >>>\npage two text\n")
    assert tenq["entities"] == ["CAESARS ENTERTAINMENT, INC."]
    assert tenq["dates"] == ["2026-06-30"]
    assert tenq["excerpt"].startswith("Commission File No. 001-36629 CAESARS ENTERTAINMENT, INC.")
    assert _text(run, index["note.md"]) == "<<< page 1 >>>\n# Note\nOne page only.\n"
    assert _text(run, index["release.html"]) == "<<< page 1 >>>\nNet revenue\n| Q2 | 2,993\n"


def test_pdf_pages_scans_and_unreadable_files(tmp_path: Path) -> None:
    run, index = _prepared(
        tmp_path,
        {
            "ford.pdf": make_pdf(["FORD MOTOR COMPANY, Dated as of July 28, 2025", "page two"]),
            "scan.pdf": make_pdf(["", ""]),
            "broken.pdf": b"%PDF-1.4 not really",
            "memo.docx": b"PK\x03\x04",
        },
    )
    ford = index["ford.pdf"]
    assert ford["pages"] == 2 and ford["entities"] == ["FORD MOTOR COMPANY"]
    assert ford["dates"] == ["2025-07-28"] and ford["image_read"] is False
    assert _text(run, ford) == (
        "<<< page 1 >>>\nFORD MOTOR COMPANY, Dated as of July 28, 2025\n<<< page 2 >>>\npage two\n"
    )
    assert index["scan.pdf"]["image_read"] is True and index["scan.pdf"]["pages"] == 2
    assert index["broken.pdf"]["unreadable"].startswith("pypdf could not read the PDF")
    assert index["broken.pdf"]["prepared"] is None
    assert index["memo.docx"]["unreadable"] == "no reader for .docx files"


def test_prepare_reports_unreadable_files_and_still_exits_0(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _prepared(tmp_path, {"a.txt": b"text\n", "memo.docx": b"PK"})
    out = capsys.readouterr().out
    assert "unreadable: memo.docx: no reader for .docx files\n" in out
    assert "prepared/index.json: 2 file(s), 1 unreadable\n" in out


def test_only_reprepares_one_file_and_keeps_the_rest(tmp_path: Path) -> None:
    run, index = _prepared(tmp_path, {"a.txt": b"first\n", "b.txt": b"second\n"})
    (tmp_path / "pack" / "b.txt").write_text("second, edited\n", encoding="utf-8")
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run), "--only", "b.txt"]) == 0
    again = {r["path"]: r for r in load_index(run)["files"]}
    assert again["a.txt"] == index["a.txt"]
    assert _text(run, again["b.txt"]) == "<<< page 1 >>>\nsecond, edited\n"
    assert main(["prepare", "--run", str(run), "--only", "nope.txt"]) == 1


def test_prepare_without_an_inventory_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = make_run(tmp_path / "pack")
    assert main(["prepare", "--run", str(run)]) == 1
    assert "run rbot inventory first" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("first_page", "expected"),
    [
        (SEC_COVER, ["CAESARS ENTERTAINMENT, INC."]),
        (
            "among\nFORD MOTOR COMPANY,\nand JPMORGAN CHASE BANK, N.A.",
            ["FORD MOTOR COMPANY", "JPMORGAN CHASE BANK, N.A."],
        ),
        ("as Parent SIX FLAGS OPERATIONS INC., as Holdings", ["SIX FLAGS OPERATIONS INC."]),
        ("a Delaware corporation and The Company", []),
        ("Overview. Ford Motor Company makes cars", ["Ford Motor Company"]),
    ],
)
def test_entity_names_on_the_first_page(first_page: str, expected: list[str]) -> None:
    assert entities(first_page) == expected


def test_dates_are_iso_in_order_without_repeats() -> None:
    text = "ended January 2, 2022; 31 March 2026; at 2026-10-02T09:31Z; again January 2, 2022"
    assert dates(text + "; February 30, 2020") == ["2022-01-02", "2026-03-31", "2026-10-02"]


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_prepare_pages_and_markers(pack_id: str, prepared_run: Callable[[str], Path]) -> None:
    run = prepared_run(pack_id)
    index = {r["path"]: r for r in load_index(run)["files"]}
    for f in CORPUS.pack(pack_id).files:
        record = index[f.path]
        assert record["unreadable"] is None, f.path
        if f.pages is not None:
            assert record["pages"] == f.pages, f.path
        text = _text(run, record)
        markers = [int(n) for n in re.findall(r"^<<< page (\d+) >>>$", text, re.M)]
        assert markers == list(range(1, record["pages"] + 1)), f.path
        if record["kind"] in ("csv", "xlsx"):
            assert not re.search(r"#N/A|#VALUE!|#DIV/0!|#NAME\?", text), f.path
        assert record["image_read"] is (record["kind"] == "image"), f.path


@pytest.mark.corpus
@pytest.mark.parametrize(
    ("pack_id", "misfiled", "named"),
    [
        (
            "tid-ford",
            "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf",
            "SIX FLAGS",
        ),
        ("tid-six-flags", "f-20251231.pdf", "Ford"),
    ],
)
def test_entity_trap_flagged(
    pack_id: str, misfiled: str, named: str, prepared_run: Callable[[str], Path]
) -> None:
    index = json.loads((prepared_run(pack_id) / "prepared" / "index.json").read_text())
    record = next(r for r in index["files"] if r["path"] == misfiled)
    assert any(named in name for name in record["entities"]), record["entities"]
    issuer = CORPUS.pack(pack_id).data["issuer"]["name"].split()[0].upper()
    assert not any(issuer in name.upper() for name in record["entities"])
