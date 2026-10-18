"""Isolated Module mode: genuine native runs, bytes imported only through native commands."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import proxy_isolated
import pytest
from state_receipt_assertions import outcome_bytes
from test_proxy_continue import approved
from test_proxy_run import Clock
from test_proxy_start import args
from test_resume_from_each_step import handoff

import proxy_run
from rbotlib import attempts, cli, dispatch, runs, state
from rbotlib import next as selection
from rbotlib.rules import RBOT_ROOT

REAL_FIXTURES = Path(__file__).parent / "fixtures/handoffs"


@pytest.fixture(autouse=True)
def clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runs, "datetime", Clock)


def _own(run: Path, module: str) -> None:
    """The generated Blocked Handoff of test_resume_from_each_step, for this test pack."""
    handoff(run, module)
    path = run / f"handoffs/{module}.md"
    text = path.read_text()
    text = text.replace("issuer_id: ACME", "issuer_id: TEST").replace("2026-10-02", "2026-01-31")
    text = text.replace("acme_10k.txt", "SYNTHETIC_10K.txt").replace(
        "Acme Holdings, Inc.", "Test plc"
    )
    path.write_text(text)


def _report(run: Path, module: str, model: str | None) -> None:
    text = dispatch.prepare_message(run, RBOT_ROOT, module, None)
    flags = [
        "dispatch-receipt", "--run", str(run), "--module", module, "--receipt", f"src-{module}",
        "--reporter", "source-controller", "--message-sha256",
        hashlib.sha256(text.encode()).hexdigest(),
    ]  # fmt: skip
    assert cli.main(flags + (["--model", model] if model else [])) == 0


def source_run(tmp_path: Path, upto: str | None = None) -> tuple[Path, Path]:
    """A genuinely approved proxy run whose Modules are accepted natively with labelled models."""
    registry, run = approved(tmp_path)
    while True:
        selected = selection.select(run, RBOT_ROOT)
        if selected["kind"] == "done" or selected["step"] == upto:
            return registry, run
        module = selected["step"]
        if selected["kind"] == "host":
            assert cli.main([module.lower(), "--run", str(run)]) in (0, 3)
            continue
        _own(run, module)
        _report(run, module, f"label-{module}")
        assert cli.main(["accept", "--run", str(run), "--module", module]) in (0, 3)


def iso_run(out: Path) -> Path:
    found = [p for p in (out / "p1/isolated").glob("*/p1/pack/rbot-runs/*") if p.is_dir()]
    assert len(found) == 1
    return found[0]


def record_path(run: Path) -> Path:
    return run.parents[3] / f"{run.name}.json"


def run_flag(registry: Path, *extra: str) -> list[str]:
    return args(registry, "--acknowledge-blocked", *extra)


def events(run: Path, module: str) -> list[dict[str, object]]:
    return attempts.read_history(run, module, state.read(run)["steps"][module])


def test_imports_from_prior_run_then_stops_at_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, source = source_run(tmp_path)
    before = outcome_bytes(source)
    capsys.readouterr()
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B")) == 0
    text = capsys.readouterr().out
    run = iso_run(tmp_path / "repo/corpus-runs")
    assert "worker required: CP-1B" in text and str(run / "dispatch/CP-1B.md") in text
    record = state.read(run)
    for module in ("CP-0", "CP-1", "CP-1A"):
        step = record["steps"][module]
        assert step["status"] in ("accepted", "blocked")
        own = (run / f"handoffs/{module}.md").read_bytes()
        original = (source / f"handoffs/{module}.md").read_bytes()
        assert own.replace(run.name.encode(), source.name.encode()) == original
        assert step["sha256"] == hashlib.sha256(own).hexdigest()
        report = events(run, module)[0]
        assert report["receipt"] == f"isolated-import:{source.name}:{module}"
        assert f"sha256 {hashlib.sha256(original).hexdigest()}" in str(report["reporter"])
        assert str(source / f"handoffs/{module}.md") in str(report["reporter"])
        assert report["model"] == (None if module == "CP-0" else f"label-{module}")
    assert next(m for m, s in record["steps"].items() if s["status"] == "pending") == "CP-1B"
    assert record["steps"]["CP-1B"].get("attempts", 0) == 0
    assert not (run / "dispatch/CP-1D.md").exists()
    saved = json.loads(record_path(run).read_text())
    assert saved["module"] == "CP-1B" and saved["source"] == str(source)
    assert set(saved["imported"]) == {"CP-0", "CP-1", "CP-1A"}
    assert outcome_bytes(source) == before


def test_host_step_runs_natively_between_imports(tmp_path: Path) -> None:
    registry, source = source_run(tmp_path)
    assert proxy_run.main(run_flag(registry, "--module", "CP-2")) == 0
    run = iso_run(tmp_path / "repo/corpus-runs")
    steps = state.read(run)["steps"]
    assert steps["MODEL"]["status"] == state.read(source)["steps"]["MODEL"]["status"]
    assert "MODEL" not in json.loads(record_path(run).read_text())["imported"]
    assert steps["CP-1D"]["status"] in ("accepted", "blocked")
    assert steps["CP-2"]["status"] == "pending" and (run / "dispatch/CP-2.md").is_file()


def test_fixture_mode_labels_fixture_and_ignores_runs(tmp_path: Path) -> None:
    registry, source = source_run(tmp_path)
    fixtures = tmp_path / "repo/tests/fixtures/handoffs"
    fixtures.mkdir(parents=True)
    for module in ("CP-0", "CP-1", "CP-1A"):
        (fixtures / f"{module}.md").write_bytes((source / f"handoffs/{module}.md").read_bytes())
    shutil.copy(REAL_FIXTURES / "CP-DR.md", fixtures)  # the source run switched Deep Research off
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B", "--fixtures")) == 0
    run = iso_run(tmp_path / "repo/corpus-runs")
    for module in ("CP-1", "CP-1A"):
        report = events(run, module)[0]
        assert report["receipt"] == f"isolated-import:fixtures:{module}"
        assert report["model"] == "fixture"
    saved = json.loads(record_path(run).read_text())
    assert saved["source"] == "fixtures"


def test_no_qualifying_source_names_modules_and_never_falls_back(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, source = source_run(tmp_path, upto="CP-1A")  # CP-1A still pending upstream
    fixtures = tmp_path / "repo/tests/fixtures/handoffs"
    fixtures.mkdir(parents=True)
    (fixtures / "CP-1.md").write_text("fixture present but not requested")
    before = outcome_bytes(source)
    capsys.readouterr()
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B")) == 1
    out = capsys.readouterr().out
    assert "no qualifying source run" in out and "CP-1A" in out and "nothing was substituted" in out
    assert not (tmp_path / "repo/corpus-runs/p1/isolated").exists()
    assert outcome_bytes(source) == before
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B", "--fixtures")) == 1
    assert "no fixture Handoff for: CP-0, CP-1A" in capsys.readouterr().out
    assert not (tmp_path / "repo/corpus-runs/p1/isolated").exists()


def test_source_handoff_edited_after_acceptance_is_not_used(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, source = source_run(tmp_path)
    path = source / "handoffs/CP-1.md"
    path.write_text(path.read_text() + "\nedited after acceptance\n")
    capsys.readouterr()
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B")) == 1
    out = capsys.readouterr().out
    assert f"{source.name}: CP-1" in out and "nothing was substituted" in out
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B", "--from-run", str(source))) == 1
    assert not (tmp_path / "repo/corpus-runs/p1/isolated").exists()


def test_accept_refusal_stops_with_native_exit_and_keeps_bytes(tmp_path: Path) -> None:
    registry, source = source_run(tmp_path)
    fixtures = tmp_path / "repo/tests/fixtures/handoffs"
    fixtures.mkdir(parents=True)
    for module in ("CP-0", "CP-1", "CP-1A"):
        raw = (source / f"handoffs/{module}.md").read_bytes()
        if module == "CP-1":
            raw = raw.replace(b"module_id: CP-1", b"module_id: CP-1Z")
        (fixtures / f"{module}.md").write_bytes(raw)
    shutil.copy(REAL_FIXTURES / "CP-DR.md", fixtures)
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B", "--fixtures")) == 4
    run = iso_run(tmp_path / "repo/corpus-runs")
    step = state.read(run)["steps"]["CP-1"]
    assert step["status"] == "failed"
    assert state.read(run)["steps"]["CP-1A"]["status"] == "pending"
    assert not (run / "dispatch/CP-1A.md").exists()
    assert b"module_id: CP-1Z" in (run / "handoffs/CP-1.md").read_bytes()


def test_continue_accepts_target_then_stops(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, _ = source_run(tmp_path)
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B")) == 0
    run = iso_run(tmp_path / "repo/corpus-runs")
    _own(run, "CP-1B")
    _report(run, "CP-1B", "label-CP-1B")
    capsys.readouterr()
    flags = args(registry, "--continue", "--run", str(run), "--accept-module", "CP-1B")
    assert proxy_run.main(flags) in (0, 3)
    assert "stopped after CP-1B" in capsys.readouterr().out
    steps = state.read(run)["steps"]
    assert steps["CP-1B"]["status"] in ("accepted", "blocked")
    assert steps["CP-1D"]["status"] == "pending" and not (run / "dispatch/CP-1D.md").exists()
    assert proxy_run.main(args(registry, "--continue", "--run", str(run))) == 0
    assert not (run / "dispatch/CP-1D.md").exists()


@pytest.mark.parametrize("flags", [["--approve"], ["--continue"]])
def test_module_with_approve_or_continue_is_a_usage_error(tmp_path: Path, flags: list[str]) -> None:
    registry, _ = source_run(tmp_path, upto="CP-1")
    with pytest.raises(SystemExit) as stop:
        proxy_run.main(run_flag(registry, "--module", "CP-1B", *flags))
    assert stop.value.code == 2


@pytest.mark.parametrize("module", ["CP-0", "MODEL", "CP-9", ""])
def test_target_must_be_an_upstream_dependent_module(tmp_path: Path, module: str) -> None:
    registry, _ = source_run(tmp_path, upto="CP-1")
    assert proxy_run.main(run_flag(registry, "--module", module)) == 1
    assert not (tmp_path / "repo/corpus-runs/p1/isolated").exists()


def test_only_the_front_matter_run_id_line_is_rewritten() -> None:
    raw = b"---\r\nmodule_id: CP-1\r\nrun_id: old\r\nissuer_id: X\r\n---\r\nrun_id: old\r\n"
    out = proxy_isolated.rewrite_run_id(raw, "new")
    assert out == raw.replace(b"run_id: old", b"run_id: new", 1)
    assert proxy_isolated.rewrite_run_id(b"no front matter run_id: old", "new") == (
        b"no front matter run_id: old"
    )


@pytest.mark.parametrize("wrong", [{"kind": "host"}, {"step": "CP-1"}])
def test_native_next_must_select_the_cp0_module_before_approval(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    wrong: dict[str, str],
) -> None:
    registry, _ = source_run(tmp_path)
    real = proxy_run._native
    seen: list[str] = []

    def native(run: Path, command: str, extra: list[str] | None = None) -> str:
        text = real(run, command, extra)
        if command == "next" and not seen:
            seen.append(text)
            return json.dumps(json.loads(text) | wrong)
        return text

    monkeypatch.setattr(proxy_run, "_native", native)
    capsys.readouterr()
    assert proxy_run.main(run_flag(registry, "--module", "CP-1B")) == 1
    assert seen
    assert "native next did not select CP-0 before Approval" in capsys.readouterr().out


def test_source_run_with_deep_research_switched_off_qualifies(tmp_path: Path) -> None:
    _, run = source_run(tmp_path)
    steps = state.read(run)["steps"]
    assert steps["CP-DR"]["status"] == "skipped"
    source, missing = proxy_isolated._unqualified(run, ["CP-0", "CP-DR"])
    assert source is not None and missing == []


def test_source_run_with_an_unexplained_skip_does_not_qualify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, run = source_run(tmp_path)
    record = state.read(run)
    record["steps"]["CP-DR"]["reason"] = "required input CP-3: failed"
    monkeypatch.setattr(state, "read", lambda _: record)
    source, missing = proxy_isolated._unqualified(run, ["CP-DR"])
    assert source is None and missing == ["CP-DR"]
