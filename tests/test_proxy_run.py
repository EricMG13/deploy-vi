from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import proxy_run
from conftest import CORPUS, corpus_gate
from rbotlib.corpus import resolve_roots, verify
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
