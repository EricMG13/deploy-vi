from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pypdf import PdfWriter

from builders import make_pdf, make_run
from conftest import CORPUS
from rbotlib import inventory as inventory_module
from rbotlib.cli import main
from rbotlib.inventory import RunError, pack_root


def _pack(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    (pack / "sub").mkdir(parents=True)
    (pack / "CZR_10Q.txt").write_text("CAESARS ENTERTAINMENT, INC.\n", encoding="utf-8")
    (pack / "sub" / "levels.csv").write_text("id,price\nA,99.5\n", encoding="utf-8")
    (pack / "report.pdf").write_bytes(make_pdf(["page one", "page two"]))
    (pack / "broken.pdf").write_bytes(b"%PDF-1.4 not really")
    (pack / ".DS_Store").write_bytes(b"\x00")
    (pack / "~$model.xlsx").write_bytes(b"lock")
    (pack / ".git").mkdir()
    (pack / "link.txt").symlink_to(pack / "CZR_10Q.txt")
    earlier = pack / "rbot-runs" / "20260715-czr-earnings-update"
    earlier.mkdir(parents=True)
    (earlier / "report.html").write_text('<script id="rbot-run">{}</script>', encoding="utf-8")
    (earlier / "model.json").write_text("{}", encoding="utf-8")
    return pack


def _inventory(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    return data


def test_inventory_lists_files_and_skips_with_reasons(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pack = _pack(tmp_path)
    run = make_run(pack)
    (run / "inventory.json").write_text("{}", encoding="utf-8")
    assert main(["inventory", "--run", str(run)]) == 0
    assert capsys.readouterr().out == "inventory.json: 5 file(s), 4 skipped\n"
    data = _inventory(run)
    assert data["schema"] == "rbot-inventory/1" and data["pack_root"] == str(pack)
    by_path = {f["path"]: f for f in data["files"]}
    assert list(by_path) == [
        "CZR_10Q.txt",
        "broken.pdf",
        "rbot-runs/20260715-czr-earnings-update/report.html",
        "report.pdf",
        "sub/levels.csv",
    ]
    assert by_path["report.pdf"]["pages"] == 2 and by_path["report.pdf"]["kind"] == "pdf"
    assert by_path["broken.pdf"]["pages"] is None
    assert by_path["sub/levels.csv"]["kind"] == "csv" and by_path["sub/levels.csv"]["size"] == 16
    assert by_path["rbot-runs/20260715-czr-earnings-update/report.html"]["rbot_report"] is True
    assert by_path["CZR_10Q.txt"]["rbot_report"] is False
    assert len(by_path["CZR_10Q.txt"]["sha256"]) == 64
    assert data["skipped"] == [
        {"path": ".DS_Store", "reason": "hidden"},
        {"path": ".git", "reason": "hidden"},
        {"path": "link.txt", "reason": "symbolic link"},
        {"path": "~$model.xlsx", "reason": "office lock file"},
    ]


def test_inventory_is_deterministic_apart_from_its_time(tmp_path: Path) -> None:
    run = make_run(_pack(tmp_path))
    main(["inventory", "--run", str(run)])
    first = _inventory(run)
    main(["inventory", "--run", str(run)])
    second = _inventory(run)
    first.pop("generated_at")
    second.pop("generated_at")
    assert first == second


def test_each_run_command_is_logged(tmp_path: Path) -> None:
    run = make_run(_pack(tmp_path))
    main(["inventory", "--run", str(run)])
    time, command, code = (run / "log" / "rbot.log").read_text(encoding="utf-8").split("\t")
    assert time.endswith("+00:00")
    assert (command, code) == (f"inventory --run {run}", "0\n")


def test_the_pack_root_comes_from_run_state_or_the_folder(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    assert pack_root(make_run(pack)) == pack
    elsewhere = tmp_path / "proxy" / "run"
    elsewhere.mkdir(parents=True)
    with pytest.raises(RunError, match="not inside a rbot-runs/ folder"):
        pack_root(elsewhere)
    state = {"schema": "rbot-run-state/1", "pack_root": str(pack)}
    (elsewhere / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    assert pack_root(elsewhere) == pack
    (elsewhere / "run-state.json").write_text("{", encoding="utf-8")
    with pytest.raises(RunError, match="no readable pack_root"):
        pack_root(elsewhere)


def test_an_empty_pack_or_a_stray_folder_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = make_run(tmp_path / "empty")
    assert main(["inventory", "--run", str(run)]) == 1
    assert "the Source Pack has no files" in capsys.readouterr().out
    assert main(["inventory", "--run", str(tmp_path / "nowhere")]) == 1
    assert "no such run folder" in capsys.readouterr().out
    (tmp_path / "stray").mkdir()
    assert main(["inventory", "--run", str(tmp_path / "stray")]) == 1
    assert "not inside a rbot-runs/ folder" in capsys.readouterr().out


def test_a_symlinked_run_folder_or_runs_folder_is_skipped(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    outside = tmp_path / "outside" / "20260101-evil"
    outside.mkdir(parents=True)
    (outside / "report.html").write_text('<script id="rbot-run">{}</script>', encoding="utf-8")
    (pack / "rbot-runs" / "20260101-evil").symlink_to(outside, target_is_directory=True)
    run = make_run(pack)
    main(["inventory", "--run", str(run)])
    data = _inventory(run)
    assert not [f for f in data["files"] if "evil" in f["path"]]
    assert {"path": "rbot-runs/20260101-evil", "reason": "symbolic link"} in data["skipped"]
    moved = tmp_path / "moved-runs"
    (pack / "rbot-runs").rename(moved)
    (pack / "rbot-runs").symlink_to(moved, target_is_directory=True)
    state = {"schema": "rbot-run-state/1", "pack_root": str(pack)}
    (moved / run.name / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    main(["inventory", "--run", str(pack / "rbot-runs" / run.name)])
    data = _inventory(run)
    assert not [f for f in data["files"] if f["path"].startswith("rbot-runs/")]
    assert {"path": "rbot-runs", "reason": "symbolic link"} in data["skipped"]


def test_a_run_inside_the_pack_never_lists_its_own_outputs(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    run = pack / "analysis" / "run1"
    run.mkdir(parents=True)
    state = {"schema": "rbot-run-state/1", "pack_root": str(pack)}
    (run / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    main(["inventory", "--run", str(run)])
    first = _inventory(run)
    main(["inventory", "--run", str(run)])
    second = _inventory(run)
    assert not [f for f in first["files"] if f["path"].startswith("analysis/run1")]
    assert [f["path"] for f in first["files"]] == [f["path"] for f in second["files"]]


def test_run_dot_inside_the_run_folder_works(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = _pack(tmp_path)
    run = make_run(pack)
    (run / "report.html").write_text('<script id="rbot-run">{}</script>', encoding="utf-8")
    monkeypatch.chdir(run)
    assert main(["inventory", "--run", "."]) == 0
    paths = [f["path"] for f in _inventory(run)["files"]]
    assert not [p for p in paths if p.endswith(run.name + "/report.html")]


def test_a_relative_pack_root_in_run_state_is_refused(tmp_path: Path) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "run-state.json").write_text(json.dumps({"pack_root": "pack"}), encoding="utf-8")
    with pytest.raises(RunError, match="pack_root must be an absolute path"):
        pack_root(run)


def test_an_unreadable_file_is_skipped_with_its_reason(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    locked = pack / "locked.txt"
    locked.write_text("secret", encoding="utf-8")
    locked.chmod(0)
    try:
        run = make_run(pack)
        assert main(["inventory", "--run", str(run)]) == 0
    finally:
        locked.chmod(0o600)
    data = _inventory(run)
    assert "locked.txt" not in [f["path"] for f in data["files"]]
    (entry,) = [s for s in data["skipped"] if s["path"] == "locked.txt"]
    assert entry["reason"].startswith("unreadable: ") and "ermission" in entry["reason"]


def test_an_unreadable_pdf_says_why(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.encrypt("pw", algorithm="RC4-128")
    with (pack / "locked.pdf").open("wb") as handle:
        writer.write(handle)
    run = make_run(pack)
    main(["inventory", "--run", str(run)])
    by_path = {f["path"]: f for f in _inventory(run)["files"]}
    assert by_path["locked.pdf"]["pages"] is None
    assert by_path["locked.pdf"]["problem"].startswith("encrypted PDF")
    assert by_path["broken.pdf"]["pages"] is None
    assert re.match(r"\w+: .+", by_path["broken.pdf"]["problem"])
    assert "problem" not in by_path["report.pdf"]


def test_pypdf_warnings_are_captured_not_logged(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, capfd: pytest.CaptureFixture[str]
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    damaged = make_pdf(["hello world"]).replace(b"startxref\n", b"startxref\n9")
    (pack / "damaged.pdf").write_bytes(damaged)
    run = make_run(pack)
    with caplog.at_level(logging.WARNING):
        main(["inventory", "--run", str(run)])
    assert not [r for r in caplog.records if r.name.startswith("pypdf")]
    assert capfd.readouterr().err == ""
    (entry,) = _inventory(run)["files"]
    assert entry["pages"] == 1 and "startxref" in entry["problem"]


def test_a_missing_pack_is_named(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run = tmp_path / "run"
    run.mkdir()
    state = {"pack_root": str(tmp_path / "gone")}
    (run / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    assert main(["inventory", "--run", str(run)]) == 1
    assert f"{tmp_path / 'gone'}: no such Source Pack" in capsys.readouterr().out


def test_a_raising_command_is_still_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = make_run(_pack(tmp_path))

    def boom(_run: Path) -> None:
        raise OSError("disk gone")

    monkeypatch.setattr(inventory_module, "write", boom)
    with pytest.raises(OSError, match="disk gone"):
        main(["inventory", "--run", str(run)])
    assert (run / "log" / "rbot.log").read_text(encoding="utf-8").endswith("\t1\n")


def test_other_runs_are_listed_safely(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    linked = pack / "rbot-runs" / "20260801-linked"
    linked.mkdir()
    (linked / "report.html").symlink_to(pack / "CZR_10Q.txt")
    locked = pack / "rbot-runs" / "20260802-locked"
    locked.mkdir()
    locked.chmod(0)
    try:
        run = make_run(pack)
        assert main(["inventory", "--run", str(run)]) == 0
    finally:
        locked.chmod(0o700)
    skipped = {s["path"]: s["reason"] for s in _inventory(run)["skipped"]}
    assert skipped["rbot-runs/20260801-linked/report.html"] == "symbolic link"
    assert skipped["rbot-runs/20260802-locked"].startswith("unreadable: ")


def test_a_pack_root_that_is_the_run_or_a_bad_run_state_is_named(tmp_path: Path) -> None:
    run = tmp_path / "run"
    run.mkdir()
    state = run / "run-state.json"
    state.write_text(json.dumps({"pack_root": str(run)}), encoding="utf-8")
    with pytest.raises(RunError, match="pack_root is the run folder"):
        pack_root(run)
    state.write_bytes(b"\xff\xfe{}")
    with pytest.raises(RunError, match=r"no readable pack_root"):
        pack_root(run)


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_inventory_is_deterministic(pack_id: str, corpus_pack: Callable[[str], Path]) -> None:
    run = make_run(corpus_pack(pack_id), f"20261011-{pack_id}-inventory")
    runs = []
    for _ in range(2):
        assert main(["inventory", "--run", str(run)]) == 0
        data = _inventory(run)
        data.pop("generated_at")
        runs.append(data)
    assert runs[0] == runs[1]
    registered = {f.path: f for f in CORPUS.pack(pack_id).files}
    listed = {f["path"]: f for f in runs[0]["files"]}
    assert sorted(listed) == sorted(registered)
    for path, f in registered.items():
        assert listed[path]["sha256"] == f.sha256
        assert listed[path]["pages"] == f.pages


def test_loose_files_in_rbot_runs_are_ignored_not_unreadable(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    (pack / "rbot-runs" / ".DS_Store").write_bytes(b"x")
    (pack / "rbot-runs" / "notes.txt").write_text("hi", encoding="utf-8")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    skipped = [s["path"] for s in _inventory(run)["skipped"]]
    assert not [p for p in skipped if p.startswith("rbot-runs/")]


def test_an_unreadable_earlier_run_gives_the_real_error_text(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    locked = pack / "rbot-runs" / "20260101-locked"
    locked.mkdir()
    run = make_run(pack)
    locked.chmod(0)
    try:
        assert main(["inventory", "--run", str(run)]) == 0
    finally:
        locked.chmod(0o700)
    reasons = {s["path"]: s["reason"] for s in _inventory(run)["skipped"]}
    assert reasons["rbot-runs/20260101-locked"] == "unreadable: Permission denied"
