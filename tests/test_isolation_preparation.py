from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pytest
from openpyxl import Workbook

from builders import make_pdf, prepared_pack
from rbotlib import dispatch, prepare, state
from rbotlib.inventory import RunError, kind_of
from rbotlib.isolation_capture import Capture
from rbotlib.isolation_preparation import observe


def _fixture(tmp_path: Path) -> tuple[Path, state.Record]:
    book = Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.title = "Visible"
    sheet.append(["Amount", "Formula", "Format"])
    sheet.append([1234567, "=A2*2", 200])
    sheet["A2"].number_format = "0.0,,"
    sheet["C2"].number_format = "[>100]0;[<=100]0"
    book.create_sheet("Hidden").sheet_state = "hidden"
    stream = io.BytesIO()
    book.save(stream)
    run = prepared_pack(
        tmp_path,
        {
            "a.txt": "FORD MOTOR COMPANY 2026-06-30\f<<< page 7 >>>\rline two",
            "empty.txt": "",
            "note.md": "# Note",
            "web.html": "<p>One</p>",
            "latin.txt": b"caf\xe9",
            "scan.pdf": make_pdf(["", ""]),
            "cover.pdf": make_pdf(["FORD MOTOR COMPANY 2026-06-30", "Second"]),
            "broken.pdf": b"%PDF bad",
            "image.png": b"an image",
            "other.bin": b"none",
            "table.csv": "name,value\nAlpha,20\n",
            "book.xlsx": stream.getvalue(),
        },
        managed=True,
    )
    return run, state.read(run)


def _metadata(run: Path, name: str = "prepared/index.json") -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / name).read_bytes())
    return data


def _write(run: Path, data: object, name: str = "prepared/index.json") -> None:
    (run / name).write_text(json.dumps(data), encoding="utf-8")


def _bytes(pack: Path) -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in pack.rglob("*") if path.is_file()}


def test_full_native_parity_and_preservation(tmp_path: Path) -> None:
    run, record = _fixture(tmp_path)
    before = _bytes(Path(record["pack_root"]))
    capture = Capture()
    capture.read(run / "run-state.json")
    result = observe(run, record, capture)
    assert result.entries == tuple(_metadata(run, "inventory.json")["files"])
    assert result.rows == tuple(_metadata(run)["files"])
    rows = {row["path"]: row for row in result.rows}
    assert rows["a.txt"]["pages"] == 2 and rows["a.txt"]["dates"] == ["2026-06-30"]
    assert rows["latin.txt"]["encoding"] == "cp1252"
    assert rows["scan.pdf"]["image_read"] and rows["image.png"]["image_read"]
    assert rows["broken.pdf"]["unreadable"] and rows["other.bin"]["prepared"] is None
    assert rows["book.xlsx"]["sheet_states"] == {"Visible": "visible", "Hidden": "hidden"}
    assert rows["book.xlsx"]["uncached_formulas"] == {"Visible": ["B2"]}
    assert rows["book.xlsx"]["display_scaled"] == {"Visible": ["A2"]}
    assert rows["book.xlsx"]["format_not_applied"] == {"Visible": ["C2"]}
    assert (run / "run-state.json") not in dict(result.files)
    assert result.files == tuple(sorted(result.files))
    assert dict(result.files) == {path: before[path] for path, _ in result.files}
    result.rows[0]["entities"].append("detached")
    result.entries[0]["path"] = "detached"
    capture.verify()
    assert _bytes(Path(record["pack_root"])) == before


@pytest.mark.parametrize(
    "pages", [[], ["\ud800FORD MOTOR COMPANY 2026-06-30\ud83d\ude00", "\udfff"]]
)
def test_exact_writer_oracle_surrogates_and_empty_pages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pages: list[str]
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "native"}, managed=True)
    entry = _metadata(run, "inventory.json")["files"][0]
    extracted = prepare.Prepared(pages, encoding="oracle")
    monkeypatch.setattr(prepare, "read", lambda *_: extracted)
    expected = prepare._ownedprepare_file(
        run, Path(state.read(run)["pack_root"]), entry, lambda: None
    )
    index = _metadata(run)
    index["files"] = [expected]
    _write(run, index)
    result = observe(run, state.read(run), Capture())
    assert result.rows == (expected,)
    assert expected["pages"] == len(pages)
    assert expected["dropped_surrogates"] == (2 if pages else 0)
    assert (
        dict(result.files)[run / expected["prepared"]] == (run / expected["prepared"]).read_bytes()
    )


@pytest.mark.parametrize(
    "field",
    [
        "pages",
        "excerpt",
        "entities",
        "dates",
        "sheets",
        "image_read",
        "unreadable",
        "encoding",
        "sheet_states",
        "uncached_formulas",
        "display_scaled",
        "format_not_applied",
        "dropped_surrogates",
        "extra",
        "numeric_type",
    ],
)
def test_complete_metadata_equality(tmp_path: Path, field: str) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "FORD MOTOR COMPANY 2026-06-30"}, managed=True)
    data = _metadata(run)
    row = data["files"][0]
    if field == "numeric_type":
        row["pages"] = float(row["pages"])
    elif field == "image_read":
        row[field] = True
    elif field == "unreadable":
        row[field] = "invented"
    else:
        row[field] = "corrupt"
    _write(run, data)
    with pytest.raises(RunError, match="metadata differs"):
        observe(run, state.read(run), Capture())


def _corrupt(inv: dict[str, Any], idx: dict[str, Any], change: str) -> None:
    last = idx["files"][-1]
    if change in ("inv_files", "idx_files"):
        (inv if change == "inv_files" else idx)["files"] = [False]
    elif change in ("inv_schema", "idx_schema", "pack"):
        (idx if change == "idx_schema" else inv)["pack_root" if change == "pack" else "schema"] = (
            "bad"
        )
    elif change.startswith("duplicate"):
        data = inv if change == "duplicate_inventory" else idx
        data["files"].append(data["files"][-1])
    elif change == "missing":
        idx["files"].pop()
    elif change == "extra":
        idx["files"].append({"path": "unknown.txt"})
    elif change == "nontext":
        last["path"] = []
    elif change in ("sha", "kind", "prepared"):
        last[{"sha": "sha256"}.get(change, change)] = "bad"
    elif change in ("registered_sha", "registered_kind"):
        key = "sha256" if change == "registered_sha" else "kind"
        last[key] = inv["files"][-1][key] = "bad"
    elif change == "readability":
        last["image_read"] = 0
    else:
        last["prepared"] = None


@pytest.mark.parametrize(
    "change",
    [
        "inv_object",
        "idx_object",
        "inv_files",
        "idx_files",
        "inv_schema",
        "idx_schema",
        "pack",
        "duplicate_inventory",
        "duplicate_index",
        "missing",
        "extra",
        "nontext",
        "sha",
        "kind",
        "registered_sha",
        "registered_kind",
        "readability",
        "prepared",
        "unreadable_default",
    ],
)
def test_all_registration_precedes_source_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "first", "z.txt": "second"}, managed=True)
    inv, idx = _metadata(run, "inventory.json"), _metadata(run)
    if change in ("inv_object", "idx_object"):
        _write(run, [], "inventory.json" if change == "inv_object" else "prepared/index.json")
    else:
        _corrupt(inv, idx, change)
    if change not in ("inv_object", "idx_object"):
        _write(run, inv, "inventory.json")
        _write(run, idx)
    reads: list[Path] = []
    native_read = prepare.read

    def watched(path: Path, kind: str) -> prepare.Prepared:
        reads.append(path)
        return native_read(path, kind)

    monkeypatch.setattr(prepare, "read", watched)
    with pytest.raises(RunError):
        observe(run, state.read(run), Capture())
    assert reads == []


@pytest.mark.parametrize(
    "path",
    ["/outside.txt", "../outside.txt", "a\n.txt", "a\\b.txt", "a:b.txt", "./a.txt", "a//b.txt", ""],
)
def test_forbidden_source_paths_before_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path: str
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    for name in ("inventory.json", "prepared/index.json"):
        data = _metadata(run, name)
        data["files"][0]["path"] = path
        data["files"][0]["kind"] = kind_of(Path(path))
        if name == "prepared/index.json":
            data["files"][0]["prepared"] = prepare.prepared_name(data["files"][0])
        _write(run, data, name)
    captured: list[Path] = []
    original = Capture.read

    def watched(self: Capture, target: Path) -> bytes:
        captured.append(target)
        return original(self, target)

    monkeypatch.setattr(Capture, "read", watched)
    with pytest.raises(RunError):
        observe(run, state.read(run), Capture())
    assert captured == [run / "inventory.json", run / "prepared/index.json"]


def test_directory_reference_refuses_before_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    for name in ("inventory.json", "prepared/index.json"):
        data = _metadata(run, name)
        row = data["files"][0]
        row.update(path=".", kind="other", prepared=None, unreadable="no reader")
        _write(run, data, name)
    original = Capture.read

    def watched(self: Capture, target: Path) -> bytes:
        assert target != run.parent.parent, "metadata-selected directory captured"
        return original(self, target)

    monkeypatch.setattr(Capture, "read", watched)
    with pytest.raises(RunError):
        observe(run, state.read(run), Capture())


@pytest.mark.parametrize("name", ["inventory.json", "prepared/index.json"])
def test_duplicate_json_keys(tmp_path: Path, name: str) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    target = run / name
    target.write_bytes(b'{"files":[],"files":[] }')
    with pytest.raises(RunError, match="duplicate key"):
        observe(run, state.read(run), Capture())


@pytest.mark.parametrize("encoding", ["utf-16", "utf-8-sig"])
@pytest.mark.parametrize("name", ["inventory.json", "prepared/index.json"])
def test_native_metadata_encoding_refuses_before_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, encoding: str, name: str
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    target = run / name
    target.write_bytes(json.dumps(_metadata(run, name)).encode(encoding))
    captured: list[Path] = []
    original = Capture.read

    def watched(self: Capture, path: Path) -> bytes:
        captured.append(path)
        return original(self, path)

    monkeypatch.setattr(Capture, "read", watched)
    with pytest.raises(ValueError):
        observe(run, state.read(run), Capture())
    assert set(captured) <= {run / "inventory.json", run / "prepared/index.json"}


@pytest.mark.parametrize(
    "name",
    [
        "../secret.json",
        "prepared/portfolios/../../secret.json",
        "/secret.json",
        "prepared/portfolios/a\n.json",
        "prepared/wrong.json",
        "missing",
    ],
)
def test_portfolio_refusals_before_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    idx = _metadata(run)
    idx["portfolios"] = [{"json": name}]
    _write(run, idx)
    monkeypatch.setattr(prepare, "read", lambda *_: pytest.fail("source read before admission"))
    with pytest.raises((RunError, OSError)):
        observe(run, state.read(run), Capture())


def test_optional_portfolios_never_opened(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    optional = run / "prepared/portfolios/optional.json"
    optional.write_bytes(b"malformed optional content")
    idx = _metadata(run)
    idx["portfolios"] = [{"portfolio_id": "optional", "json": "prepared/portfolios/optional.json"}]
    _write(run, idx)
    native = Path.read_bytes

    def watched(path: Path) -> bytes:
        assert path != optional, "optional portfolio opened"
        return native(path)

    monkeypatch.setattr(Path, "read_bytes", watched)
    capture = Capture()
    result = observe(run, state.read(run), capture)
    assert optional not in dict(result.files) and optional not in dict(capture.inventory())


@pytest.mark.parametrize("name", ["raw", "text", "index", "inventory"])
def test_mid_observation_changes_refuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    record = state.read(run)
    row = _metadata(run)["files"][0]
    targets = {
        "raw": Path(record["pack_root"]) / "a.txt",
        "text": run / row["prepared"],
        "index": run / "prepared/index.json",
        "inventory": run / "inventory.json",
    }
    native = prepare.read

    def changed(path: Path, kind: str) -> prepare.Prepared:
        result = native(path, kind)
        target = targets[name]
        target.write_bytes(target.read_bytes() + b" ")
        return result

    monkeypatch.setattr(prepare, "read", changed)
    with pytest.raises(RunError, match="bytes changed"):
        observe(run, record, Capture())


@pytest.mark.parametrize("consumer", ["extract", "dispatch"])
def test_unexpected_native_errors_propagate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, consumer: str
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    before = _bytes(run.parent.parent)

    def failed(*args: object) -> None:
        raise OSError("native reader failure")

    monkeypatch.setattr(
        prepare if consumer == "extract" else dispatch,
        "read" if consumer == "extract" else "_prepared",
        failed,
    )
    with pytest.raises(OSError, match="native reader failure"):
        observe(run, state.read(run), Capture())
    assert _bytes(run.parent.parent) == before


def test_capture_precedes_native_consumers_and_final_verify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    record, capture = state.read(run), Capture()
    native_read, native_dispatch = prepare.read, dispatch._prepared

    def read(path: Path, kind: str) -> prepare.Prepared:
        assert path in dict(capture.inventory())
        assert (run / prepare.prepared_name(_metadata(run)["files"][0])) in dict(
            capture.inventory()
        )
        return native_read(path, kind)

    def dispatched(folder: Path, rec: state.Record) -> list[dict[str, Any]]:
        assert {run / "inventory.json", run / "prepared/index.json"} <= dict(
            capture.inventory()
        ).keys()
        record["pack_root"] = "caller mutation"
        rows = native_dispatch(folder, rec)
        (run / rows[0]["prepared"]).write_text("late change", encoding="utf-8")
        return rows

    monkeypatch.setattr(prepare, "read", read)
    monkeypatch.setattr(dispatch, "_prepared", dispatched)
    with pytest.raises(RunError, match="bytes changed"):
        observe(run, record, capture)


@pytest.mark.parametrize("name", ["raw", "text"])
def test_initial_changed_raw_and_text(tmp_path: Path, name: str) -> None:
    run = prepared_pack(tmp_path, {"a.txt": "source"}, managed=True)
    target = (
        run.parent.parent / "a.txt"
        if name == "raw"
        else run / _metadata(run)["files"][0]["prepared"]
    )
    target.write_bytes(b"edited")
    with pytest.raises(RunError, match="sha256 changed" if name == "raw" else "text differs"):
        observe(run, state.read(run), Capture())
