from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

import proxy_run
from conftest import CORPUS, corpus_gate
from rbotlib.cli import main as rbot
from rbotlib.corpus import Pack, Registry, Roots, materialise, resolve_roots, verify
from rbotlib.prepare import load_index

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
    return [*base, "--registry", str(registry), "--date", "20261011", *extra]


def test_step_1_copies_the_pack_and_prepares_a_pending_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry)) == 0
    base = tmp_path / "repo" / "corpus-runs" / "p1"
    run = base / "20261011-test-pending"
    assert f"run folder: {run}\n" in capsys.readouterr().out
    assert (base / "pack" / "SYNTHETIC_10K.txt").is_file()
    state = json.loads((run / "run-state.json").read_text(encoding="utf-8"))
    assert (state["schema"], state["run_id"], state["pack_root"]) == (
        "rbot-run-state/1",
        "20261011-test-pending",
        str(base / "pack"),
    )
    assert (state["issuer_id"], state["pathway"], state["plan"]) == ("TEST", None, [])
    assert [r["path"] for r in load_index(run)["files"]] == ["SYNTHETIC_10K.txt"]
    assert proxy_run.main(_args(registry)) == 0
    assert (base / "20261011-test-pending-2" / "inventory.json").is_file()


def test_step_5_prints_the_simulated_approval(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    assert proxy_run.main(_args(registry, "--approve")) == 1
    assert "no pending proxy run; run step 1 first" in capsys.readouterr().out
    proxy_run.main(_args(registry))
    capsys.readouterr()
    assert proxy_run.main(_args(registry, "--approve")) == 0
    run = tmp_path / "repo" / "corpus-runs" / "p1" / "20261011-test-pending"
    assert capsys.readouterr().out == (
        f"python rbot/scripts/rbot.py approve --run {run} --pathway EARNINGS_UPDATE"
        " --depth quick --primary yes --analyst proxy-run --deep-research yes --prior-case no\n"
    )
    assert proxy_run.main(_args(registry, "--approve", "--primary", "no")) == 0
    assert "--primary no" in capsys.readouterr().out


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
    assert proxy_run.main([*args, "--out", str(tmp_path), "--date", "20261011"]) == 0
    run = tmp_path / pack.id / "20261011-czr-pending"
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
    assert proxy_run.main(_args(registry, "--date", "20261012")) == 1
    assert "SYNTHETIC_10K.txt" in capsys.readouterr().out
    assert not list(_base(tmp_path).glob("20261012*"))


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


@pytest.mark.parametrize("date", ["../x", "2026-10-11", "202610", "20261345", "x"])
def test_a_bad_date_is_a_usage_error_and_writes_nothing(tmp_path: Path, date: str) -> None:
    registry = _registry(tmp_path)
    args = _args(registry)
    args[args.index("20261011")] = date
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


def test_a_failed_step_is_recorded_and_the_run_is_not_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    monkeypatch.setattr("proxy_run.rbot", lambda argv: 1 if argv[0] == "prepare" else rbot(argv))
    assert proxy_run.main(_args(registry)) == 1
    run = _base(tmp_path) / "20261011-test-pending"
    steps = json.loads((run / "run-state.json").read_text(encoding="utf-8"))["steps"]
    assert steps["PREPARE"] == {
        "kind": "host",
        "status": "failed",
        "reason": "rbot prepare exited 1",
    }
    assert "INVENTORY" not in steps
    monkeypatch.setattr("proxy_run.rbot", rbot)
    capsys.readouterr()
    assert proxy_run.main(_args(registry, "--approve")) == 1
    assert "no pending proxy run" in capsys.readouterr().out


def test_the_newest_run_is_ordered_by_creation_time_not_mtime(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _registry(tmp_path)
    for date in ("20261011", "20261012"):
        assert proxy_run.main(_args(registry, "--date", date)) == 0
    base = _base(tmp_path)
    old, new = base / "20261011-test-pending", base / "20261012-test-pending"
    os.utime(new, (1, 1))  # the newer run looks the oldest by mtime
    os.utime(old, (2_000_000_000, 2_000_000_000))
    capsys.readouterr()
    assert proxy_run.main(_args(registry, "--approve")) == 0
    assert "20261012-test-pending" in capsys.readouterr().out


def test_two_starts_racing_for_one_name_take_the_next_suffix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = _registry(tmp_path)
    real = proxy_run.run_id
    calls: list[str] = []

    def racing(base: Path, issuer_id: str, day: str) -> str:
        name = real(base, issuer_id, day)
        if not calls:
            (base / name).mkdir(parents=True)  # another process claims it first
        calls.append(name)
        return name

    monkeypatch.setattr(proxy_run, "run_id", racing)
    assert proxy_run.main(_args(registry)) == 0
    assert calls == ["20261011-test-pending", "20261011-test-pending-2"]
    assert (_base(tmp_path) / "20261011-test-pending-2" / "inventory.json").is_file()
