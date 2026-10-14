from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime, tzinfo
from pathlib import Path

import pytest

import proxy_run
from conftest import CORPUS, corpus_gate
from rbotlib import runs, state
from rbotlib.corpus import Pack, Registry, Roots, materialise, resolve_roots, verify
from rbotlib.inventory import RunError
from rbotlib.prepare import load_index


class Clock(datetime):
    point = datetime(2026, 10, 11, tzinfo=UTC)

    @classmethod
    def now(cls, tz: tzinfo | None = None) -> Clock:
        return cls.fromtimestamp(cls.point.timestamp(), tz=tz)


def test_proxy_never_adopts_existing_legacy_run(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry)) == 0
    run = _base(tmp_path) / "pack/rbot-runs/20261011-test-pending"
    record = state.read(run)
    record.pop("ownership")
    (run / state.STATE).write_text(json.dumps(record))
    from test_legacy_ownership import snapshot

    before = snapshot(run)
    assert proxy_run.main(_args(registry)) == 1
    assert proxy_run.main(_args(registry, "--approve")) == 1
    assert snapshot(run) == before


@pytest.fixture(autouse=True)
def native_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runs, "datetime", Clock)
    monkeypatch.setattr(Clock, "point", datetime(2026, 10, 11, tzinfo=UTC))


PACK = {
    "id": "p1",
    "root": "synthetic",
    "path": "p1",
    "issuer": {"id": "TEST", "name": "Test plc"},
    "period": "FY2025",
    "as_of": "2026-01-31",
    "primary": True,
    "portfolios": [],
    "prior_pack": None,
    "expectations": None,
    "pathways": [{"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "primary"}],
    "traps": [],
}


def _registry(tmp_path: Path) -> Path:
    """A repo at <tmp>/repo with one in-repo synthetic pack holding one file."""
    repo = tmp_path / "repo"
    pack = repo / "tests" / "corpus" / "synthetic" / "p1"
    pack.mkdir(parents=True)
    body = b"SYNTHETIC filing\nRevenue was 100.\n"
    (pack / "SYNTHETIC_10K.txt").write_bytes(body)
    (repo / "pyproject.toml").write_text('[project]\nversion = "0.1.0"\n', encoding="utf-8")
    entry: dict[str, object] = {"path": "SYNTHETIC_10K.txt"}
    entry["sha256"] = hashlib.sha256(body).hexdigest()
    entry |= {
        "class": "issuer",
        "document_type": "Annual report",
        "entity": "TEST",
        "synthetic": True,
    }
    roots = {"synthetic": "tests/corpus/synthetic"}
    data = {"schema": "rbot-corpus/1", "roots": roots, "packs": [PACK | {"files": [entry]}]}
    registry = repo / "tests" / "corpus" / "corpus.json"
    registry.write_text(json.dumps(data), encoding="utf-8")
    return registry


def _args(registry: Path, *extra: str) -> list[str]:
    base = ["--pack", "p1", "--pathway", "EARNINGS_UPDATE", "--depth", "quick"]
    return [*base, "--registry", str(registry), *extra]


def test_step_1_copies_the_pack_and_prepares_a_pending_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry)) == 0
    base = tmp_path / "repo" / "corpus-runs" / "p1"
    run = base / "pack/rbot-runs/20261011-test-pending"
    assert f"run folder: {run}\n" in capsys.readouterr().out
    assert (base / "pack" / "SYNTHETIC_10K.txt").is_file()
    state = json.loads((run / "run-state.json").read_text(encoding="utf-8"))
    assert (state["schema"], state["run_id"], state["pack_root"]) == (
        "rbot-run-state/1",
        "20261011-test-pending",
        str(base / "pack"),
    )
    assert (state["issuer_id"], state["as_of_date"], state["pathway"], state["plan"]) == (
        None,
        None,
        None,
        ["CP-0"],
    )
    assert state["hints"]["issuer"] == "TEST" and "ownership" in state
    assert [r["path"] for r in load_index(run)["files"]] == ["SYNTHETIC_10K.txt"]
    assert proxy_run.main(_args(registry)) == 1
    assert "unfinished run exists" in capsys.readouterr().out
    assert not (run.parent / "20261011-test-pending-2").exists()


def test_step_5_refuses_missing_readiness_instead_of_printing_approval(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry, "--approve")) == 1
    assert "no unfinished native proxy run; run step 1 first" in capsys.readouterr().out
    proxy_run.main(_args(registry))
    capsys.readouterr()
    assert proxy_run.main(_args(registry, "--approve")) == 1
    run = tmp_path / "repo/corpus-runs/p1/pack/rbot-runs/20261011-test-pending"
    assert f"{run}: native CP-0 readiness required" in capsys.readouterr().out
    assert proxy_run.main(_args(registry, "--approve", "--primary", "no")) == 1
    assert state.read(run)["approval"] is None


def test_a_pathway_the_pack_does_not_list_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    args = _args(registry)
    args[args.index("quick")] = "full"
    assert proxy_run.main(args) == 1
    assert "pack p1 lists [('EARNINGS_UPDATE', 'quick')]" in capsys.readouterr().out


@pytest.mark.corpus
def test_step_1_on_the_primary_pack(tmp_path: Path) -> None:
    pack = CORPUS.pack("czr-2026q2-primary")
    corpus_gate(verify(CORPUS, pack, resolve_roots(CORPUS)))
    args = ["--pack", pack.id, "--pathway", "FULL_CREDIT_ASSESSMENT", "--depth", "full"]
    assert proxy_run.main([*args, "--out", str(tmp_path)]) == 0
    run = tmp_path / pack.id / "pack/rbot-runs/20261011-czr-pending"
    index = load_index(run)
    assert len(index["files"]) == len(pack.files)
    assert [r["path"] for r in index["files"] if r["unreadable"]] == []
    assert [p["portfolio_id"] for p in index["portfolios"]] == ["TEST_CLO_I"]


def _base(tmp_path: Path) -> Path:
    return tmp_path / "repo" / "corpus-runs" / "p1"


def test_a_tampered_copy_of_the_pack_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry)) == 0
    (_base(tmp_path) / "pack" / "SYNTHETIC_10K.txt").write_text("tampered", encoding="utf-8")
    capsys.readouterr()
    assert proxy_run.main(_args(registry)) == 1
    assert "SYNTHETIC_10K.txt" in capsys.readouterr().out
    assert not (_base(tmp_path) / "pack/rbot-runs/20261011-test-pending-2").exists()


def test_a_first_copy_that_does_not_match_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def corrupting(registry: Registry, pack: Pack, roots: Roots, dest: Path) -> Path:
        made = materialise(registry, pack, roots, dest)
        (made / "SYNTHETIC_10K.txt").write_text("torn", encoding="utf-8")
        return made

    monkeypatch.setattr("proxy_run.materialise", corrupting)
    assert proxy_run.main(_args(_registry(tmp_path))) == 1
    assert "SYNTHETIC_10K.txt" in capsys.readouterr().out


@pytest.mark.parametrize("date", ["20261011", "../x", "2026-10-11", "202610", "20261345", "x"])
def test_retired_date_override_is_a_usage_error_and_writes_nothing(
    tmp_path: Path, date: str
) -> None:
    registry = _registry(tmp_path)
    args = _args(registry, "--date", date)
    with pytest.raises(SystemExit) as stop:
        proxy_run.main(args)
    assert stop.value.code == 2
    assert not (tmp_path / "repo" / "corpus-runs").exists()


def test_unreadable_registry_or_version_files_are_messages_not_tracebacks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    (tmp_path / "repo" / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    assert proxy_run.main(_args(registry)) == 1
    assert "pyproject.toml" in capsys.readouterr().out
    (tmp_path / "repo" / "pyproject.toml").unlink()
    assert proxy_run.main(_args(registry)) == 1
    assert "pyproject.toml" in capsys.readouterr().out
    registry.write_text("{not json", encoding="utf-8")
    assert proxy_run.main(_args(registry)) == 1
    assert str(registry) in capsys.readouterr().out
    assert proxy_run.main(_args(tmp_path / "missing.json")) == 1
    assert "missing.json" in capsys.readouterr().out


def test_native_prepare_failure_is_logged_without_a_fabricated_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)

    def failed(*args: object, **kwargs: object) -> None:
        raise RunError("causal preparation I/O failure")

    monkeypatch.setattr("rbotlib.prepare.write", failed)
    assert proxy_run.main(_args(registry)) == 1
    run = _base(tmp_path) / "pack/rbot-runs/20261011-test-pending"
    steps = json.loads((run / "run-state.json").read_text(encoding="utf-8"))["steps"]
    assert steps == {"CP-0": {"kind": "module", "status": "pending", "attempts": 0}}
    assert "prepare --run" in (run / "log/rbot.log").read_text()
    assert (run / "log/rbot.log").read_text().endswith("\t1\n")
    assert not (run / "prepared").exists()
    capsys.readouterr()
    assert proxy_run.main(_args(registry)) == 1
    assert "unfinished run exists" in capsys.readouterr().out
    assert state.read(run)["steps"] == steps


def test_the_newest_run_is_ordered_by_creation_time_not_mtime(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry)) == 0
    base = _base(tmp_path) / "pack/rbot-runs"
    old, new = base / "20261011-test-pending", base / "20261012-test-pending"
    state.update(old, lambda record: record["report"].update(written_at=Clock.now(UTC).isoformat()))
    monkeypatch.setattr(Clock, "point", datetime(2026, 10, 12, tzinfo=UTC))
    assert proxy_run.main(_args(registry)) == 0
    state.update(old, lambda record: record["report"].update(written_at=None))
    os.utime(new, (1, 1))  # the newer run looks the oldest by mtime
    os.utime(old, (2_000_000_000, 2_000_000_000))
    capsys.readouterr()
    assert proxy_run.main(_args(registry, "--approve")) == 1
    assert "20261012-test-pending" in capsys.readouterr().out


def test_native_collision_preserves_unknown_reservation_and_takes_next_suffix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = _registry(tmp_path)
    real = runs._allocate
    calls: list[str] = []

    def racing(base: Path, name: str) -> Path:
        if not calls:
            (base / name).mkdir(parents=True)  # another process claims it first
        calls.append(name)
        return real(base, name)

    monkeypatch.setattr(runs, "_allocate", racing)
    assert proxy_run.main(_args(registry)) == 0
    assert calls == ["20261011-test-pending"]
    base = _base(tmp_path) / "pack/rbot-runs"
    assert list((base / "20261011-test-pending").iterdir()) == []
    assert (base / "20261011-test-pending-2/inventory.json").is_file()
