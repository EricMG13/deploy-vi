"""Prepared outputs and cleanup must stay inside the run folder."""

from pathlib import Path

import pytest
from test_prepare_fix1 import _prep

from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.portfolio import Portfolio, write_all
from rbotlib.rules import load_rules


@pytest.mark.parametrize(
    "target", ["prepared", "prepared/portfolios", "prepared/index.json", "text"]
)
def test_prepare_refuses_symlink_outputs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], target: str
) -> None:
    run, index, _ = _prep(tmp_path, {"a.txt": b"readable note"})
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "keep.txt"
    marker.write_text("unchanged")
    path = run / (index["a.txt"]["prepared"] if target == "text" else target)
    if path.is_dir():
        path.rename(run / "saved")
        path.symlink_to(outside, target_is_directory=True)
    else:
        path.unlink()
        path.symlink_to(marker)
    assert main(["prepare", "--run", str(run)]) == 1
    captured = capsys.readouterr()
    assert "symlink" in captured.out + captured.err
    assert marker.read_text() == "unchanged" and list(outside.iterdir()) == [marker]


def test_portfolio_writer_refuses_symlink_folder(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "old.json"
    marker.write_text("keep")
    (tmp_path / "prepared").mkdir()
    (tmp_path / "prepared/portfolios").symlink_to(outside, target_is_directory=True)
    with pytest.raises(RunError, match="symlink"):
        write_all(tmp_path, {"P1": Portfolio(meta={"portfolio_id": "P1"})}, load_rules())
    assert marker.read_text() == "keep" and list(outside.iterdir()) == [marker]


@pytest.mark.parametrize("target", ["inventory.json", "log", "log/rbot.log"])
def test_inventory_and_log_refuse_symlinks_before_command(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], target: str
) -> None:
    run, _, _ = _prep(tmp_path, {"a.txt": b"note"})
    before = (run / "inventory.json").read_bytes()
    (run.parent.parent / "a.txt").write_text("changed after inventory")
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "keep.txt"
    marker.write_text("keep")
    path = run / target
    if path.is_dir():
        path.rename(run / "saved-log")
        path.symlink_to(outside, target_is_directory=True)
    else:
        path.unlink()
        path.symlink_to(marker)
    assert main(["inventory", "--run", str(run)]) == 1
    captured = capsys.readouterr()
    assert "symlink" in captured.out + captured.err
    assert marker.read_text() == "keep" and list(outside.iterdir()) == [marker]
    if target != "inventory.json":
        assert captured.err.startswith(f"error: {run}: ")
        assert (run / "inventory.json").read_bytes() == before


def test_log_oserror_is_named_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from rbotlib import cli

    run, _, _ = _prep(tmp_path, {"a.txt": b"note"})

    def fail(*args: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("sys.argv", ["rbot", "inventory", "--run", str(run)])
    assert main() == 0
    assert "\tinventory --run " in (run / "log/rbot.log").read_text()
    monkeypatch.setattr(cli, "_log", fail)
    assert main(["inventory", "--run", str(run)]) == 1
    assert capsys.readouterr().err.startswith(f"error: {run}: disk full")


def test_resolved_run_symlink_is_supported(tmp_path: Path) -> None:
    run, _, _ = _prep(tmp_path, {"a.txt": b"note"})
    alias = tmp_path / "run-alias"
    alias.symlink_to(run, target_is_directory=True)
    assert main(["prepare", "--run", str(alias)]) == 0


@pytest.mark.parametrize("relative", ["../outside.txt", "/tmp/outside.txt"])
def test_output_path_refuses_non_run_paths(tmp_path: Path, relative: str) -> None:
    from rbotlib.inventory import output_path

    with pytest.raises(RunError, match="output path is outside the run folder"):
        output_path(tmp_path, relative)


def test_stale_portfolio_symlink_is_not_deleted(tmp_path: Path) -> None:
    folder = tmp_path / "prepared/portfolios"
    folder.mkdir(parents=True)
    marker = tmp_path / "keep.json"
    marker.write_text("keep")
    stale = folder / "old.json"
    stale.symlink_to(marker)
    with pytest.raises(RunError, match="symlink"):
        write_all(tmp_path, {"P1": Portfolio(meta={"portfolio_id": "P1"})}, load_rules())
    assert stale.is_symlink() and marker.read_text() == "keep"
    assert not (folder / "P1.json").exists()
