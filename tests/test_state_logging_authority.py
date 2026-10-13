"""Real CLI regressions for selected-run logging ownership and normalized envelopes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_state import seeded


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        str(p.relative_to(root)): p.read_bytes() if p.is_file() else None for p in root.rglob("*")
    }


def call(selected: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path("rbot/scripts/rbot.py").resolve()), "state", "--run", selected],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )


@pytest.mark.parametrize("existing_log", [False, True])
@pytest.mark.parametrize(
    "spelling", ["parent", "relative parent", "repeated parent", "named parent"]
)
def test_unproved_source_selection_never_creates_or_changes_paths(
    tmp_path: Path, existing_log: bool, spelling: str
) -> None:
    source = tmp_path / ("rbot-runs/source-pack" if spelling == "named parent" else "source-pack")
    (source / "rbot-runs/nested").mkdir(parents=True)
    (source / "evidence.md").write_bytes(b"protected source evidence\n")
    if existing_log:
        (source / "log").mkdir()
        (source / "log/rbot.log").write_bytes(b"protected source log evidence\n")
    selected = str(source / "rbot-runs") + "/.."
    if spelling == "repeated parent":
        selected = str(source / "rbot-runs/nested") + "/../.."
    elif spelling == "relative parent":
        selected = "source-pack/rbot-runs/.."
    elif spelling == "named parent":
        selected = str(source)
    before = snapshot(tmp_path)
    result = call(selected, tmp_path if spelling == "relative parent" else None)
    assert result.returncode == 1 and "error:" in result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert snapshot(tmp_path) == before  # includes directories and newly created outside-run paths


@pytest.mark.parametrize(
    "kind",
    [
        "absent",
        "malformed",
        "array",
        "duplicate",
        "nonfinite",
        "deep",
        "run_id",
        "pack_root",
        "missing pack_root",
        "directory",
        "fifo",
    ],
)
@pytest.mark.parametrize("existing_log", [False, True])
def test_unproved_state_marker_never_acquires_logging_authority(
    tmp_path: Path, kind: str, existing_log: bool
) -> None:
    run, data = seeded(tmp_path)
    marker = run / "run-state.json"
    if kind in ("absent", "directory", "fifo"):
        marker.unlink()
        if kind == "directory":
            marker.mkdir()
        elif kind == "fifo":
            os.mkfifo(marker)
    elif kind in ("run_id", "pack_root", "missing pack_root"):
        field = "run_id" if kind == "run_id" else "pack_root"
        data[field] = "wrong-run" if field == "run_id" else str(tmp_path / "wrong-pack")
        if kind == "pack_root":
            (tmp_path / "wrong-pack").mkdir()
        marker.write_text(json.dumps(data), encoding="utf-8")
    else:
        raw = {
            "malformed": "{",
            "array": "[]",
            "duplicate": '{"schema": 1, "schema": 2}',
            "nonfinite": "NaN",
            "deep": "[" * 1200 + "0" + "]" * 1200,
        }[kind]
        marker.write_text(raw, encoding="utf-8")
    if existing_log:
        (run / "log").mkdir(exist_ok=True)
        (run / "log/rbot.log").write_bytes(b"protected existing log\n")
    before = snapshot(tmp_path)
    result = call(str(run))
    assert result.returncode == 1 and "error:" in result.stdout + result.stderr
    assert "run-state.json" in result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize(
    "spelling",
    [
        "dot",
        "parent",
        "repeated parent",
        "relative",
        "ancestor alias",
        "child",
        "alias child",
        "relative child",
    ],
)
def test_valid_run_normalized_spellings_preserve_state_and_log_once(
    tmp_path: Path, spelling: str
) -> None:
    run, _ = seeded(tmp_path / "real")
    (run / "child").mkdir()
    selected = str(run) + "/."
    if spelling == "parent":
        selected = str(run) + "/../" + run.name
    elif spelling == "repeated parent":
        selected = str(run) + "/../../rbot-runs/" + run.name
    elif spelling == "relative":
        selected = str(run.relative_to(tmp_path))
    elif spelling == "child":
        selected = str(run / "child") + "/.."
    elif spelling in ("ancestor alias", "alias child"):
        alias = tmp_path / "alias"
        alias.symlink_to(tmp_path / "real", target_is_directory=True)
        selected = str(alias / run.relative_to(tmp_path / "real"))
        if spelling == "alias child":
            selected += "/child/.."
    elif spelling == "relative child":
        selected = str(run.relative_to(tmp_path)) + "/child/.."
    before = (run / "run-state.json").read_bytes()
    result = call(selected, tmp_path if spelling in ("relative", "relative child") else None)
    assert result.returncode == 0
    assert (run / "run-state.json").read_bytes() == before
    assert (run.parent.parent / "source.md").read_bytes() == b"unaltered source evidence\n"
    lines = (run / "log/rbot.log").read_text().splitlines()
    assert len(lines) == 1 and lines[0].endswith("\t0")


@pytest.mark.parametrize("component", ["pack", "rbot-runs", "run"])
def test_parent_segments_cannot_hide_output_envelope_links(tmp_path: Path, component: str) -> None:
    run, _ = seeded(tmp_path)
    original = {"pack": run.parent.parent, "rbot-runs": run.parent, "run": run}[component]
    alias = original.parent / "alias"
    alias.symlink_to(original, target_is_directory=True)
    selected = str(alias / run.relative_to(original)) + "/../" + run.name
    before = snapshot(run.parent.parent)
    result = call(selected)
    assert result.returncode == 1 and "symlink" in result.stdout + result.stderr
    assert snapshot(run.parent.parent) == before


def test_missing_parent_segment_refuses_before_state_publication(tmp_path: Path) -> None:
    run, _ = seeded(tmp_path)
    before = snapshot(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "rbot/scripts/rbot.py",
            "state",
            "--run",
            str(run / "missing") + "/..",
            "--set",
            "MODEL=failed",
            "--reason",
            "host failed",
        ],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    assert result.returncode == 1 and "error:" in result.stdout + result.stderr
    assert snapshot(tmp_path) == before


def test_symlink_loop_refuses_without_traceback_or_creation(tmp_path: Path) -> None:
    link = tmp_path / "loop"
    link.symlink_to(link)
    result = call(str(link))
    assert result.returncode == 1 and "error:" in result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert list(tmp_path.iterdir()) == [link]


def test_existing_child_link_cannot_be_canceled_to_enable_logging(tmp_path: Path) -> None:
    run, _ = seeded(tmp_path)
    (run / "child").mkdir()
    (run / "alias").symlink_to(run / "child", target_is_directory=True)
    before = snapshot(run.parent.parent)
    result = call(str(run / "alias") + "/..")
    assert result.returncode == 1 and "symlink" in result.stdout + result.stderr
    assert snapshot(run.parent.parent) == before
