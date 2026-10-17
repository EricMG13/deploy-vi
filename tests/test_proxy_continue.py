"""Real native calls, fixture worker reports; provider execution remains unqualified."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import proxy_continue
import pytest
from state_receipt_assertions import outcome_bytes
from test_proxy_run import Clock
from test_proxy_start import args, prepared, ready

import proxy_run
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib import attempts, dispatch, runs, state
from rbotlib.cli import main as native
from rbotlib.corpus import CorpusError, load_registry
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


@pytest.fixture(autouse=True)
def clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runs, "datetime", Clock)


def approved(tmp_path: Path) -> tuple[Path, Path]:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 0
    target = runs.discover_unfinished(run.parent.parent)
    assert target is not None
    return registry, target


def test_continue_prepares_exact_native_message_without_reporting_send(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    assert proxy_run.main(args(registry, "--continue")) == 0
    text = (run / "dispatch/CP-0.md").read_text()
    assert text == dispatch.qualified_message(run, RBOT_ROOT, "CP-0", state.read(run))
    assert state.read(run)["steps"]["CP-0"] == {
        "kind": "module",
        "status": "pending",
        "attempts": 0,
    }
    assert not (run / "validate").exists()


def test_explicit_fetch_and_blank_module_refuse_before_creating_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("RBOT_FETCH", raising=False)
    registry, run = prepared(tmp_path)
    before = outcome_bytes(run)
    for flags, message in [
        (["--fetch"], "--fetch requires RBOT_FETCH=1"),
        (["--module", ""], "--module requires a nonempty Module id"),
    ]:
        assert proxy_run.main(args(registry, *flags)) == 1
        assert message in capsys.readouterr().out
        assert outcome_bytes(run) == before


def _options(*flags: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    proxy_run._transport_options(parser)
    return parser.parse_args(list(flags))


def test_fetch_needs_the_variable_and_the_variable_needs_fetch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RBOT_FETCH", raising=False)
    with pytest.raises(CorpusError, match="--fetch requires RBOT_FETCH=1"):
        proxy_continue.check_options(_options("--fetch"))
    proxy_continue.check_options(_options())
    monkeypatch.setenv("RBOT_FETCH", "1")
    proxy_continue.check_options(_options("--fetch"))
    assert os.environ["RBOT_FETCH"] == "1"
    with pytest.raises(CorpusError, match="RBOT_FETCH is set; pass --fetch"):
        proxy_continue.check_options(_options())


def test_native_imported_fixture_cannot_qualify_isolated_upstream(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, run = approved(tmp_path)
    # Even a structurally valid declared fixture cannot grant accepted same-run evidence.
    fixture = RBOT_ROOT.parent / "tests/fixtures/handoffs/CP-1.md"
    raw = fixture.read_bytes()
    (run / "handoffs/CP-1.md").write_bytes(raw)
    before = outcome_bytes(run)
    assert native(["dispatch-message", "--run", str(run), "--module", "CP-1B"]) == 1
    assert "required input CP-1: pending" in capsys.readouterr().out
    assert native(["accept", "--run", str(run), "--module", "CP-1"]) == 1
    assert "acceptance requires reported dispatch evidence" in capsys.readouterr().out
    assert outcome_bytes(run) == before and fixture.read_bytes() == raw
    assert state.read(run)["steps"]["CP-1"].get("attempts", 0) == 0


def reported(registry: Path, run: Path, name: str, *extra: str) -> list[str]:
    raw = (run / "dispatch/CP-0.md").read_bytes()
    return args(
        registry,
        "--continue",
        "--reported-module",
        "CP-0",
        "--receipt",
        name,
        "--reporter",
        "fixture-controller",
        "--message-sha256",
        hashlib.sha256(raw).hexdigest(),
        *extra,
    )


def output(registry: Path, run: Path) -> None:
    pack = load_registry(registry).pack("p1")
    (run / "handoffs").mkdir(exist_ok=True)
    (run / "handoffs/CP-0.md").write_text(
        cp0_handoff(
            run, ("Test plc", "TEST"), "2026-01-31", registry_classification(pack), primary=False
        )
    )


def test_genuine_receipt_label_duplicate_conflict_and_unknown_time(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    assert proxy_run.main(args(registry, "--continue", "--model-label", "caller-model")) == 0
    assert "model" not in state.read(run)["steps"]["CP-0"]
    flags = reported(registry, run, "actual-fixture-receipt", "--model-label", "caller-model")
    assert proxy_run.main(flags) == 0
    step = state.read(run)["steps"]["CP-0"]
    events = attempts.read_history(run, "CP-0", step)
    assert events[0]["model"] == "caller-model" and events[0]["worker_started_at"] is None
    assert step["attempts"] == 1 and "model" not in step
    assert proxy_run.main(flags) == 0
    assert attempts.read_history(run, "CP-0", state.read(run)["steps"]["CP-0"]) == events
    before = outcome_bytes(run)
    changed = flags.copy()
    changed[changed.index("caller-model")] = "conflicting-model"
    assert proxy_run.main(changed) == 1 and outcome_bytes(run) == before
    output(registry, run)
    assert proxy_run.main(args(registry, "--continue", "--accept-module", "CP-0")) == 0
    final = state.read(run)["steps"]["CP-0"]
    assert final["status"] == "accepted" and final["model"] == "caller-model"
    assert events[0]["observed_at"] == final["started_at"]


def test_malformed_retry_resend_and_terminal_no_resurrection(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    assert proxy_run.main(args(registry, "--continue")) == 0
    assert proxy_run.main(reported(registry, run, "first")) == 0
    assert proxy_run.main(reported(registry, run, "resend")) == 0
    (run / "handoffs").mkdir()
    own = run / "handoffs/CP-0.md"
    own.write_text("DONE 0")
    assert proxy_run.main(args(registry, "--continue", "--accept-module", "CP-0")) == 2
    assert '"exit": 2' in (run / "dispatch/CP-0.md").read_text()
    assert proxy_run.main(reported(registry, run, "retry")) == 0
    assert proxy_run.main(reported(registry, run, "retry-resend")) == 0
    assert state.read(run)["steps"]["CP-0"]["attempts"] == 2
    assert proxy_run.main(args(registry, "--continue", "--accept-module", "CP-0")) == 2
    step = state.read(run)["steps"]["CP-0"]
    events = attempts.read_history(run, "CP-0", step)
    assert step["status"] == "failed" and [e["slot"] for e in events] == [1, 1, 1, 2, 2, 2]
    own.write_text("changed terminal bytes")
    before = outcome_bytes(run)
    assert proxy_run.main(args(registry, "--continue", "--accept-module", "CP-0")) == 1
    assert outcome_bytes(run) == before
    assert proxy_run.main(reported(registry, run, "third")) == 1
    assert outcome_bytes(run) == before


@pytest.mark.parametrize("content,code", [(b"\xff", 1), (b"module_id: CP-1\n", 4)])
def test_failed_accept_preserves_original_native_exit(
    tmp_path: Path, content: bytes, code: int
) -> None:
    registry, run = prepared(tmp_path)
    assert proxy_run.main(args(registry, "--continue")) == 0
    assert proxy_run.main(reported(registry, run, "failure")) == 0
    output(registry, run)
    own = run / "handoffs/CP-0.md"
    if code == 4:
        own.write_bytes(own.read_bytes().replace(b"module_id: CP-0", content.strip()))
    else:
        own.write_bytes(content)
    assert proxy_run.main(args(registry, "--continue", "--accept-module", "CP-0")) == code
    assert state.read(run)["steps"]["CP-0"]["status"] == "failed"


@pytest.mark.parametrize("bad", ["", "   ", "x\nDONE 0", "x\x00", "x\u202e", "x" * 201])
def test_unsafe_labels_refuse_before_native_writes(tmp_path: Path, bad: str) -> None:
    registry, run = prepared(tmp_path)
    before = outcome_bytes(run)
    assert proxy_run.main(args(registry, "--continue", "--model-label", bad)) == 1
    assert outcome_bytes(run) == before


@pytest.mark.parametrize("fault", ["foreign", "copy", "pathway", "symlink", "history", "log"])
def test_explicit_renamed_continuation_keeps_identity_source_and_receipt_guards(
    tmp_path: Path, fault: str
) -> None:
    registry, run = approved(tmp_path)
    assert proxy_run.main(args(registry, "--continue", "--run", str(run))) == 0
    before_source = (run.parent.parent / "SYNTHETIC_10K.txt").read_bytes()
    flags = args(registry, "--continue", "--run", str(run))
    if fault == "foreign":
        out = tmp_path / "different-output"
        shutil.copytree(
            run.parent.parent, out / "p1/pack", ignore=shutil.ignore_patterns("rbot-runs")
        )
        flags += ["--out", str(out)]
    elif fault == "copy":
        (run.parent.parent / "SYNTHETIC_10K.txt").write_text("tampered generated copy")
    elif fault == "pathway":
        flags += ["--pathway", "EARNINGS_UPDATE", "--depth", "quick"]
    elif fault == "symlink":
        linked = run.parent / "linked"
        linked.symlink_to(run, target_is_directory=True)
        flags += ["--run", str(linked)]
    elif fault == "history":
        (run / "validate/history/CP-0/000001.json").write_text("{}")
    else:
        with (run / "log/rbot.log").open("a") as stream:
            stream.write("foreign row\n")
    before = outcome_bytes(run)
    assert proxy_run.main(flags) == 1 and outcome_bytes(run) == before
    if fault != "copy":
        assert (run.parent.parent / "SYNTHETIC_10K.txt").read_bytes() == before_source


@pytest.mark.parametrize(
    "extra",
    [
        ["--run", "other"],
        ["--receipt", "incomplete"],
        ["--worker-started-at", "unknown"],
        ["--accept-module", "CP-0"],
        ["--continue", "--approve"],
        ["--run", ""],
        ["--continue", "--accept-module", ""],
    ],
)
def test_partial_transport_options_are_usage_errors_before_creation(
    tmp_path: Path, extra: list[str]
) -> None:
    registry, run = prepared(tmp_path)
    before = outcome_bytes(run)
    with pytest.raises(SystemExit) as stop:
        proxy_run.main(args(registry, *extra))
    assert stop.value.code == 2 and outcome_bytes(run) == before


@pytest.mark.parametrize("failed", [False, True])
def test_actual_managed_host_execution_and_failure_are_owned_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failed: bool
) -> None:
    from test_model_host import eligible

    from rbotlib.model.host import Model

    run = eligible(tmp_path, RBOT_ROOT)
    sources = {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    if failed:

        def failure(captured: object, generated_at: str) -> object:
            raise RunError("causal fixture managed host build failure")

        monkeypatch.setattr(Model, "build", failure)
        with pytest.raises(proxy_run.NativeFailure) as stop:
            proxy_continue.advance(run, None, proxy_run._native)
        assert stop.value.code == 1
    else:
        proxy_continue.advance(run, None, proxy_run._native)
    before = state.read(run)["steps"]["MODEL"]
    assert before["status"] == ("failed" if failed else "accepted")
    assert before["host_exit"] == (1 if failed else 0) and before["attempts"] == 1
    invocation = before["host_execution"]["invocations"][0]
    assert invocation["exit"] == (1 if failed else 0) and invocation["completion"] == "completed"
    proxy_continue.advance(run, None, proxy_run._native)
    assert state.read(run)["steps"]["MODEL"] == before
    assert {p.name: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()} == sources
    assert not (run / "model.xlsx").exists()


def test_all_terminal_renders_report_and_sets_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, run = approved(tmp_path)
    for module in ("CP-1", "CP-1A", "CP-5"):
        failed = ["state", "--run", str(run), "--set", f"{module}=failed", "--reason"]
        assert native([*failed, "explicit fixture failure"]) == 0
    capsys.readouterr()
    assert proxy_run.main(args(registry, "--continue")) == 0
    out = capsys.readouterr().out
    assert f"report.html: {run / 'report.html'}" in out and "Blocked/failed/skipped:" in out
    record = state.read(run)
    assert record["report"]["written_at"] and (run / "report.md").exists()
    assert (run / "report.html").exists()
    before = outcome_bytes(run)
    assert proxy_run.main(args(registry, "--continue", "--run", str(run))) == 0
    assert f"report already written: {run / 'report.html'}" in capsys.readouterr().out
    assert outcome_bytes(run) == before


def test_dispatch_bytes_changed_after_native_selection_cannot_reach_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, run = prepared(tmp_path)
    actual = native

    def replace(argv: list[str]) -> int:
        result = actual(argv)
        if "next" in argv and result == 0:
            (run / "dispatch/CP-0.md").write_text("forged dispatch bytes")
        return result

    monkeypatch.setattr(proxy_run, "rbot", replace)
    capsys.readouterr()
    assert proxy_run.main(args(registry, "--continue")) == 1
    out = capsys.readouterr().out
    assert "persisted dispatch changed" in out and "worker required:" not in out
    assert state.read(run)["steps"]["CP-0"]["status"] == "pending"
    assert not (run / "validate").exists()


def test_native_age_limit_applies_to_explicit_and_discovered_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, run = prepared(tmp_path)
    monkeypatch.setattr(Clock, "point", datetime(2026, 11, 12, tzinfo=UTC))
    before = outcome_bytes(run)
    dispatch_bytes = (run / "dispatch/CP-0.md").read_bytes()
    assert proxy_run.main(args(registry, "--continue")) == 1
    assert proxy_run.main(args(registry, "--continue", "--run", str(run))) == 1
    assert outcome_bytes(run) == before
    assert (run / "dispatch/CP-0.md").read_bytes() == dispatch_bytes


def test_discovered_run_cannot_silently_use_another_requested_pathway(tmp_path: Path) -> None:
    registry, run = approved(tmp_path)
    data = json.loads(registry.read_text())
    data["packs"][0]["pathways"].append(
        {"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "partial"}
    )
    registry.write_text(json.dumps(data))
    before = outcome_bytes(run)
    flags = args(registry, "--continue", "--pathway", "EARNINGS_UPDATE", "--depth", "quick")
    assert proxy_run.main(flags) == 1 and outcome_bytes(run) == before


def test_rendered_run_continues_to_the_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, run = approved(tmp_path)
    state.update(run, lambda record: record["report"].update(html_sha256="0" * 64))
    before = outcome_bytes(run)
    capsys.readouterr()
    assert proxy_run.main(args(registry, "--continue")) == 0
    assert "worker required: CP-1" in capsys.readouterr().out
    assert outcome_bytes(run) == before
