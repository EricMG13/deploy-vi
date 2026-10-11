from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from builders import make_pdf, make_run
from conftest import CORPUS
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
