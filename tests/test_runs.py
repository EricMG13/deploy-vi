from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st
from test_state import STAMP, seeded

from conftest import HANG_TIMEOUT
from rbotlib import __version__
from rbotlib.cli import main
from rbotlib.state import read

NOW = datetime.fromisoformat(STAMP)
SCRIPT = Path(__file__).resolve().parents[1] / "rbot/scripts/rbot.py"


def start(pack: Path, *args: str) -> int:
    try:
        return main(["new-run", "--pack", str(pack), *args])
    except SystemExit as exc:
        assert isinstance(exc.code, int)
        return exc.code


@pytest.mark.parametrize("issuer", [None, "", "ACME / Holdings", "../../escape"])
def test_cli_creates_checked_bootstrap_and_logs_hints_as_data(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], issuer: str | None
) -> None:
    pack = tmp_path / "Source Pack"
    pack.mkdir()
    source = pack / "evidence.md"
    source.write_bytes(b"evidence must remain unchanged\n")
    extra = [] if issuer is None else ["--issuer", issuer]
    assert start(pack, *extra, "--objective", "quote $(false)\nreview") == 0
    run = Path(capsys.readouterr().out.strip())
    assert run.parent == pack / "rbot-runs"
    assert run.name.endswith("-pending")
    assert "/" not in run.name
    data = read(run)
    assert data["rbot_version"] == __version__
    assert data["pack_root"] == str(pack.resolve())
    assert data["hints"] == {"issuer": issuer, "objective": "quote $(false)\nreview"}
    assert data["plan"] == ["CP-0"]
    assert data["steps"] == {"CP-0": {"kind": "module", "status": "pending", "attempts": 0}}
    for field in ("issuer_id", "as_of_date", "approval", "pathway", "depth", "primary"):
        assert data[field] is None
    assert data["report"] == {"written_at": None, "html_sha256": None, "md_sha256": None}
    log = (run / "log/rbot.log").read_text()
    assert "new-run" in log
    assert len(log.splitlines()) == 1
    assert source.read_bytes() == b"evidence must remain unchanged\n"


def discover(pack: Path, now: datetime = NOW) -> Path | None:
    from rbotlib.runs import discover_unfinished

    return discover_unfinished(pack, now=now)


@pytest.mark.parametrize("status", ["pending", "running", "failed", "skipped"])
def test_discovery_uses_checked_state_after_rename_without_retry(
    tmp_path: Path, status: str
) -> None:
    run, data = seeded(tmp_path)
    renamed = run.with_name("20261012-acme-full-credit-assessment")
    run.rename(renamed)
    data["run_id"] = renamed.name
    data["steps"]["CP-0"] = {"kind": "module", "status": status, "reason": "terminal"}
    (renamed / "run-state.json").write_text(json.dumps(data))
    before = (renamed / "run-state.json").read_bytes()
    assert discover(renamed.parent.parent) == renamed
    assert (renamed / "run-state.json").read_bytes() == before


@pytest.mark.parametrize("age,expected", [(30, True), (30.000001, False), (0, True)])
def test_discovery_has_inclusive_30_day_boundary(
    tmp_path: Path, age: float, expected: bool
) -> None:
    run, data = seeded(tmp_path)
    data["created_at"] = (NOW - timedelta(days=age)).isoformat()
    (run / "run-state.json").write_text(json.dumps(data))
    assert (discover(run.parent.parent) == run) is expected


def test_future_and_malformed_candidates_refuse_by_cause(tmp_path: Path) -> None:
    from rbotlib.inventory import RunError

    run, data = seeded(tmp_path)
    data["created_at"] = (NOW + timedelta(microseconds=1)).isoformat()
    (run / "run-state.json").write_text(json.dumps(data))
    with pytest.raises(RunError, match="future"):
        discover(run.parent.parent)
    (run / "run-state.json").write_text('{"schema":')
    with pytest.raises(ValueError):
        discover(run.parent.parent)


def test_latest_eligible_unfinished_ignores_completed_and_issuer_hints(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run, data = seeded(tmp_path)
    newer = run.with_name("newer-completed")
    newer.mkdir()
    finished = data | {"run_id": newer.name, "created_at": NOW.isoformat()}
    finished["report"] = data["report"] | {"written_at": NOW.isoformat()}
    (newer / "run-state.json").write_text(json.dumps(finished))
    assert discover(run.parent.parent) == run
    assert start(run.parent.parent, "--issuer", "OTHER") == 1
    assert str(run) in capsys.readouterr().out
    assert not (run / "log/rbot.log").exists()


def test_completed_and_empty_name_collision_allow_new_allocation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    today = datetime.now(UTC).strftime("%Y%m%d")
    collision = pack / "rbot-runs" / f"{today}-unknown-pending"
    collision.mkdir(parents=True)
    assert start(pack) == 0
    run = Path(capsys.readouterr().out.strip())
    assert run.name == collision.name + "-2"
    data = read(run)
    data["report"]["written_at"] = data["created_at"]
    (run / "run-state.json").write_text(json.dumps(data))
    assert start(pack) == 0
    assert Path(capsys.readouterr().out.strip()).name == collision.name + "-3"
    assert list(collision.iterdir()) == []


@pytest.mark.parametrize("target", ["rbot-runs", "run", "state"])
def test_linked_generated_outputs_never_touch_source(
    tmp_path: Path, target: str, capsys: pytest.CaptureFixture[str]
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    source = pack / "evidence.md"
    source.write_bytes(b"preserve me")
    envelope = pack / "rbot-runs"
    if target == "rbot-runs":
        envelope.symlink_to(pack, target_is_directory=True)
    else:
        envelope.mkdir()
        run = envelope / f"{datetime.now(UTC):%Y%m%d}-unknown-pending"
        if target == "run":
            run.symlink_to(pack, target_is_directory=True)
        else:
            run.mkdir()
            (run / "run-state.json").symlink_to(source)
    assert start(pack) == 1
    assert "symlink" in capsys.readouterr().out
    assert source.read_bytes() == b"preserve me"
    assert not (pack / "log").exists()


def test_pack_alias_above_selected_pack_remains_usable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    physical = tmp_path / "physical"
    pack = physical / "pack"
    pack.mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to(physical, target_is_directory=True)
    assert start(alias / "pack") == 0
    run = Path(capsys.readouterr().out.strip())
    assert read(run)["pack_root"] == str(pack)


@pytest.mark.parametrize("kind", ["missing", "file"])
def test_invalid_pack_is_named_without_creating_outputs(
    tmp_path: Path, kind: str, capsys: pytest.CaptureFixture[str]
) -> None:
    pack = tmp_path / kind
    if kind == "file":
        pack.write_bytes(b"source")
    assert start(pack) == 1
    assert str(pack) in capsys.readouterr().out
    assert not (tmp_path / "rbot-runs").exists()


@given(age=st.integers(min_value=0, max_value=100))
def test_age_policy_property(age: int) -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as temporary:
        run, data = seeded(Path(temporary))
        data["created_at"] = (NOW - timedelta(days=age)).isoformat()
        (run / "run-state.json").write_text(json.dumps(data))
        assert (discover(run.parent.parent) is not None) == (age <= 30)


def test_independent_cli_processes_refuse_duplicate_unfinished_run(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    command = [sys.executable, str(SCRIPT), "new-run", "--pack", str(pack)]
    first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    results = [(process, process.communicate(timeout=HANG_TIMEOUT)) for process in (first, second)]
    assert sorted(process.returncode for process, _ in results) == [0, 1]
    runs = [path for path in (pack / "rbot-runs").iterdir() if path.is_dir()]
    assert len(runs) == 1
    loser = next(output for process, (output, _) in results if process.returncode == 1)
    assert str(runs[0]) in loser


@pytest.mark.parametrize("boundary", ["selection", "publication"])
def test_cli_process_ownership_covers_empty_snapshot_and_partial_publication(
    tmp_path: Path, boundary: str
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    wrapper = """
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from rbotlib import runs
from rbotlib.cli import main
pack, signal, release = map(Path, sys.argv[2:5])
original = runs.discover_unfinished if sys.argv[5] == "selection" else runs.write_atomic
def barrier(*args, **kwargs):
    result = original(*args, **kwargs) if sys.argv[5] == "selection" else None
    signal.touch()
    deadline = time.monotonic() + 8
    while not release.exists():
        if time.monotonic() >= deadline:
            raise RuntimeError("test barrier timed out")
        time.sleep(0.01)
    return result if sys.argv[5] == "selection" else original(*args, **kwargs)
if sys.argv[5] == "selection":
    runs.discover_unfinished = barrier
else:
    runs.write_atomic = barrier
sys.exit(main(["new-run", "--pack", str(pack)]))
"""
    signal, release = tmp_path / "entered", tmp_path / "release"
    first = subprocess.Popen(
        [
            sys.executable,
            "-c",
            wrapper,
            str(SCRIPT.parent),
            str(pack),
            str(signal),
            str(release),
            boundary,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    import time

    deadline = time.monotonic() + HANG_TIMEOUT
    while not signal.exists():
        assert first.poll() is None
        assert time.monotonic() < deadline
        time.sleep(0.01)
    second = subprocess.Popen(
        [sys.executable, str(SCRIPT), "new-run", "--pack", str(pack)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        # The owner is suspended after discovery or before publishing checked state.
        # A second public CLI must not finish while that ownership is outstanding.
        with pytest.raises(subprocess.TimeoutExpired):
            second.communicate(timeout=0.3)
        release.touch()
        out, err = first.communicate(timeout=HANG_TIMEOUT)
        assert first.returncode == 0, err
        loser, err = second.communicate(timeout=HANG_TIMEOUT)
        assert second.returncode == 1, err
        run = Path(out.strip())
        assert str(run) in loser
        assert len([p for p in run.parent.iterdir() if p.is_dir()]) == 1
    finally:
        release.touch()
        for process in (first, second):
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=HANG_TIMEOUT)


@pytest.mark.parametrize("content", [False, True])
def test_failed_publication_removes_only_owned_empty_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    content: bool,
) -> None:
    from rbotlib import runs

    pack = tmp_path / "pack"
    pack.mkdir()

    def fail(path: Path, text: str) -> None:
        if content:
            (path.parent / "user-file").write_bytes(b"keep")
        raise OSError("publication failure")

    monkeypatch.setattr(runs, "write_atomic", fail)
    assert start(pack) == 1
    out = capsys.readouterr().out
    assert "publication failure" in out
    envelope = pack / "rbot-runs"
    if content:
        run = next(envelope.iterdir())
        assert str(run) in out and "incomplete run retained" in out
        assert (run / "user-file").read_bytes() == b"keep"
    else:
        retained = list(envelope.iterdir())
        assert len(retained) == 1 and "incomplete run retained" in out
        assert not (retained[0] / "run-state.json").exists()
    assert not (envelope / runs.LOCK).exists()


def test_stale_creation_lock_refuses_without_forced_unlock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from rbotlib import runs

    envelope = tmp_path / "pack/rbot-runs"
    envelope.mkdir(parents=True)
    lock = envelope / runs.LOCK
    lock.write_bytes(b"do not force unlock")
    monkeypatch.setattr(runs, "LOCK_WAIT", 0)
    assert start(envelope.parent) == 1
    assert str(lock) in capsys.readouterr().out
    assert lock.read_bytes() == b"do not force unlock"
    assert list(envelope.iterdir()) == [lock]


def test_created_run_logging_rechecks_checked_identity_and_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from rbotlib import runs

    pack = tmp_path / "pack"
    pack.mkdir()
    source = pack / "source.md"
    source.write_bytes(b"original")
    original = runs.create_run

    def tamper(pack: Path, issuer: str | None, objective: str | None) -> Path:
        run = original(pack, issuer, objective)
        (run / "log").mkdir(exist_ok=True)
        (run / "log/rbot.log").symlink_to(source)
        return run

    monkeypatch.setattr(runs, "create_run", tamper)
    assert start(pack) == 1
    assert "symlink" in capsys.readouterr().err
    assert source.read_bytes() == b"original"


@pytest.mark.parametrize("defect", ["json", "schema", "directory", "hardlink"])
def test_corrupt_discovery_candidate_is_named_and_not_silently_ignored(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], defect: str
) -> None:
    import os

    run, data = seeded(tmp_path)
    marker = run / "run-state.json"
    if defect == "json":
        marker.write_text('{"schema":')
    elif defect == "schema":
        marker.write_text(json.dumps(data | {"pack_root": "/outside"}))
    else:
        marker.unlink()
        if defect == "directory":
            marker.mkdir()
        else:
            source = run.parent.parent / "source.md"
            os.link(source, marker)
    before = list(run.parent.iterdir())
    assert start(run.parent.parent) == 1
    out = capsys.readouterr().out
    assert str(marker) in out
    assert list(run.parent.iterdir()) == before
    assert not (run / "log/rbot.log").exists()


def test_newest_creation_time_and_tie_break_are_deterministic(tmp_path: Path) -> None:
    run, data = seeded(tmp_path)
    another = run.with_name("a-later")
    another.mkdir()
    changed = data | {
        "run_id": another.name,
        "created_at": (NOW - timedelta(seconds=1)).isoformat(),
    }
    (another / "run-state.json").write_text(json.dumps(changed))
    assert discover(run.parent.parent) == run
    changed["created_at"] = NOW.isoformat()
    (another / "run-state.json").write_text(json.dumps(changed))
    assert discover(run.parent.parent) == another


def test_discovery_rejects_naive_clock(tmp_path: Path) -> None:
    from rbotlib.inventory import RunError

    pack = tmp_path / "pack"
    pack.mkdir()
    with pytest.raises(RunError, match="timezone-aware"):
        discover(pack, now=NOW.replace(tzinfo=None))


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", ["czr-2026q2-primary", "czr-2026q2-full-credit-assessment"])
def test_new_run_preserves_hashes_of_verified_real_corpus_copies(
    corpus_pack: Callable[[str], Path],
    pack_id: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    import shutil

    from conftest import CORPUS
    from rbotlib.corpus import sha256_file

    pack = shutil.copytree(corpus_pack(pack_id), tmp_path / "working pack")
    registered = CORPUS.pack(pack_id)
    before = {entry.path: sha256_file(pack / entry.path) for entry in registered.files}
    assert before == {entry.path: entry.sha256 for entry in registered.files}
    assert start(pack, "--issuer", "hint-only") == 0
    run = Path(capsys.readouterr().out.strip())
    assert read(run)["issuer_id"] is None
    assert start(pack) == 1
    assert str(run) in capsys.readouterr().out
    assert {path: sha256_file(pack / path) for path in before} == before


def _public_approve(run: Path) -> None:
    child = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "approve",
            "--run",
            str(run),
            "--pathway",
            "FULL_CREDIT_ASSESSMENT",
            "--depth",
            "full",
            "--primary",
            "no",
            "--analyst",
            "B. Approver",
        ],
        capture_output=True,
        text=True,
        timeout=HANG_TIMEOUT,
    )
    assert child.returncode == 0, child.stdout + child.stderr


@pytest.mark.parametrize("boundary", ["enumeration", "directory", "marker", "selection"])
def test_public_approval_rename_during_discovery_refuses_duplicate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    boundary: str,
) -> None:
    import hashlib

    from test_approve import _ready

    from rbotlib import runs, state

    run = _ready(SCRIPT.parent.parent, tmp_path)
    pack = run.parent.parent
    (run / state.STATE).write_text(
        json.dumps(
            runs._bootstrap(run, pack, None, None) | {"ownership": state.read(run)["ownership"]}
        )
    )
    state.read(run)
    before = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.iterdir() if p.is_file()
    }
    assert start(pack) == 1
    assert str(run) in capsys.readouterr().out
    original_listing, original_exists, original_read = Path.iterdir, Path.exists, state.read
    triggered = False

    def approve() -> None:
        nonlocal triggered
        triggered = True
        _public_approve(run)

    def listing(path: Path) -> Iterator[Path]:
        iterator = original_listing(path)
        if boundary == "enumeration" and path == run.parent and not triggered:
            approve()  # rename after iterator creation, before real enumeration
        snapshot = list(iterator)
        if boundary == "directory" and path == run.parent and not triggered:
            approve()  # real snapshot captured before the independent public rename
        return iter(snapshot)

    def exists(path: Path) -> bool:
        if boundary == "marker" and path == run / state.STATE and not triggered:
            approve()  # directory check succeeded; marker check now sees the vanished path
        return original_exists(path)

    def reading(path: Path) -> state.Record:
        record = original_read(path)
        if boundary == "selection" and path == run and not triggered:
            approve()  # checked selection becomes a vanished old path before return
        return record

    monkeypatch.setattr(Path, "iterdir", listing)
    monkeypatch.setattr(Path, "exists", exists)
    monkeypatch.setattr(state, "read", reading)
    assert start(pack) == 1
    output = capsys.readouterr().out
    assert triggered
    if boundary != "enumeration":
        assert "discovery changed" in output and str(run.parent) in output
        assert (
            "unfinished run exists" not in output
        )  # vanished old path is not a resume instruction
    folders = [p for p in original_listing(run.parent) if p.is_dir()]
    assert len(folders) == 1
    renamed = folders[0]
    record = state.read(renamed)
    assert renamed != run and record["approval"] is not None
    assert record["report"]["written_at"] is None
    assert "approve" in (renamed / "log/rbot.log").read_text()
    assert not (run.parent / runs.LOCK).exists()
    assert before == {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in pack.iterdir() if p.is_file()
    }
    assert start(pack) == 1
    assert str(renamed) in capsys.readouterr().out
