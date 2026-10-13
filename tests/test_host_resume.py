"""Future host entitlement is exercised through public processes and real sources."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from host_process import command, finish, start
from test_host_fit import fit_run
from test_model_host import eligible

from rbotlib import cli, host_evidence, state
from rbotlib import next as next_step
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("kind", ["model", "fit"])
def test_active_owner_and_killed_registration(tmp_path: Path, kind: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    process = start(run, kind, "build")
    try:
        original = state.read(run)["steps"][kind.upper()]
        with pytest.raises(ValueError, match="holds"):
            next_step.select(run, RBOT_ROOT)
        contender = command(run, kind)
        assert contender.returncode == 1 and "holds" in contender.stderr
        assert state.read(run)["steps"][kind.upper()] == original
        process.kill()
        assert process.wait(timeout=10) == -9
        selected = next_step.select(run, RBOT_ROOT)
        assert selected["step"] == kind.upper()
        resumed = command(run, kind)
        assert resumed.returncode == 0, resumed.stderr
        current = state.read(run)["steps"][kind.upper()]
        assert current["status"] == "accepted" and current["attempts"] == 1
        evidence = current["host_execution"]
        assert evidence["token"] == original["host_execution"]["token"]
        assert evidence["generated_at"] == original["host_execution"]["generated_at"]
        assert len(evidence["invocations"]) == 2
        assert evidence["invocations"][0]["completion"] == "interrupted; exit unknown"
        assert evidence["invocations"][1]["exit"] == 0
    finally:
        finish(process)


@pytest.mark.parametrize("phase", ["output", "intent", "log", "commit"])
def test_publication_interruption_is_truthfully_reconciled(tmp_path: Path, phase: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    process = start(run, "model", phase)
    try:
        original = state.read(run)["steps"]["MODEL"]
        prefix = (run / "log/rbot.log").read_bytes()
        process.kill()
        assert process.wait(timeout=10) == -9
        resumed = command(run, "model")
        current = state.read(run)["steps"]["MODEL"]
        if phase == "commit":
            assert resumed.returncode == 1 and current == original
        else:
            assert resumed.returncode == 0, resumed.stderr
            assert current["status"] == "accepted" and current["attempts"] == 1
            assert len(current["host_execution"]["invocations"]) == 2
            assert (run / "log/rbot.log").read_bytes().startswith(prefix)
    finally:
        finish(process)


def test_public_next_after_receipt_interruption_can_continue(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    process = start(run, "model", "log")
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        assert cli.main(["next", "--run", str(run)]) == 0
        resumed = command(run, "model")
        assert resumed.returncode == 0, resumed.stderr
    finally:
        finish(process)


@pytest.mark.parametrize("kind", ["model", "fit"])
@pytest.mark.parametrize("phase", ["built", "output-json", "output", "intent", "log", "commit"])
def test_every_host_publication_boundary(tmp_path: Path, kind: str, phase: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    boundary = (
        "output-" + ("model.json" if kind == "model" else "FUND.json")
        if phase == "output-json"
        else phase
    )
    process = start(run, kind, boundary)
    try:
        original = state.read(run)["steps"][kind.upper()]
        prefix = (run / "log/rbot.log").read_bytes()
        files = {str(p.relative_to(run)): p.read_bytes() for p in run.glob("fit/*.json")}
        process.kill()
        assert process.wait(timeout=10) == -9
        result = command(run, kind)
        current = state.read(run)["steps"][kind.upper()]
        if phase == "commit":
            assert result.returncode == 1 and current == original
        else:
            assert result.returncode == 0, result.stderr
            assert current["attempts"] == 1 and current["status"] == "accepted"
            evidence = current["host_execution"]
            assert evidence["token"] == original["host_execution"]["token"]
            assert evidence["generated_at"] == original["host_execution"]["generated_at"]
            assert len({i["id"] for i in evidence["invocations"]}) == 2
            prior, active = evidence["invocations"]
            assert "exit" not in prior and prior["completion"] == "interrupted; exit unknown"
            assert active["exit"] == 0 and active["receipt"]["invocation"] == active["id"]
            raw_log = (run / "log/rbot.log").read_bytes()
            assert raw_log.startswith(prefix)
            added_rows = raw_log[len(prefix) :].splitlines()
            assert len(added_rows) == 1 and added_rows[0].endswith(b"\t0")
            assert ("receipt" in prior) == (phase in ("intent", "log"))
            for name, raw in files.items():
                assert (run / name).read_bytes() == raw
    finally:
        finish(process)


@pytest.mark.parametrize("kind", ["model", "fit"])
def test_simultaneous_continuations_admit_one_owner(tmp_path: Path, kind: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    prior = start(run, kind, "build")
    prior.kill()
    assert prior.wait(timeout=10) == -9
    process = start(run, kind, "build")
    try:
        before = (run / state.STATE).read_bytes()
        contender = command(run, kind)
        assert contender.returncode == 1 and "holds" in contender.stderr
        assert (run / state.STATE).read_bytes() == before
        assert process.stdin is not None
        process.stdin.write("continue\n")
        process.stdin.flush()
        stdout, stderr = process.communicate(timeout=20)
        assert process.returncode == 0 and "BUILT" in stdout, stderr
        evidence = state.read(run)["steps"][kind.upper()]["host_execution"]
        assert len(evidence["invocations"]) == 2 and evidence["invocations"][-1]["exit"] == 0
    finally:
        finish(prior)
        finish(process)


@pytest.mark.parametrize(
    "change",
    [
        "token",
        "origin",
        "exclusion",
        "source",
        "lock",
        "log",
        "receipt",
        "entitlement-list",
        "invocation-list",
        "receipt-list",
    ],
)
def test_tampered_continuation_refuses_before_build(tmp_path: Path, change: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    process = start(run, "model", "intent" if change in ("receipt", "receipt-list") else "build")
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        record = state.read(run)
        evidence = record["steps"]["MODEL"]["host_execution"]
        expected = "changed"
        if change in ("token", "origin"):
            evidence[change] = "f" * 32 if change == "token" else "forged"
            if change == "origin":
                evidence["binding"] = host_evidence.binding(evidence)
            expected = "entitlement/origin"
        elif change.endswith("-list"):
            value: object
            target, key, value, expected = {
                "entitlement-list": (record["steps"]["MODEL"], "host_execution", [], "entitlement"),
                "invocation-list": (evidence, "invocations", [[]], "invocation"),
                "receipt-list": (evidence["invocations"][-1], "receipt", [], "receipt intent"),
            }[change]
            target[key] = value
        elif change == "exclusion":
            record["steps"]["CP-1D"]["status"] = "skipped"
        elif change == "source":
            (Path(record["pack_root"]) / "acme_10k.txt").write_bytes(b"changed source")
        elif change == "lock":
            (run / state.LOCK).write_bytes(b"foreign lock")
            expected = "ownership unresolved"
        elif change == "log":
            with (run / "log/rbot.log").open("ab") as stream:
                stream.write(b"foreign\t0\n")
            expected = "log prefix"
        else:
            evidence["invocations"][-1]["receipt"]["row"] = "666f72676564"
            expected = "receipt intent"
        if change in ("token", "origin", "exclusion", "receipt") or change.endswith("-list"):
            (run / state.STATE).write_text(json.dumps(record))
        before = (run / state.STATE).read_bytes()
        result = command(run, "model")
        assert (
            result.returncode == 1
            and "Traceback" not in result.stderr
            and expected in result.stderr
        ), result.stderr
        assert (
            "written; qa_status" not in result.stdout and (run / state.STATE).read_bytes() == before
        )
        with pytest.raises(ValueError, match=expected):
            next_step.select(run, RBOT_ROOT)
    finally:
        finish(process)


@pytest.mark.parametrize("kind", ["model", "fit"])
@pytest.mark.parametrize("phase", ["failure", "correction"])
def test_interrupted_caught_failure_never_rebuilds(tmp_path: Path, kind: str, phase: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    process = start(run, kind, phase)
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        before = state.read(run)["steps"][kind.upper()]
        result = command(run, kind)
        current = state.read(run)["steps"][kind.upper()]
        assert result.returncode == 1 and "persisted terminal failure" in result.stderr
        assert current["status"] == "failed" and current["attempts"] == 1
        assert current["host_execution"]["token"] == before["host_execution"]["token"]
        assert "exit" not in current["host_execution"]["invocations"][0]
        terminal = (run / state.STATE).read_bytes()
        assert command(run, kind).returncode == 1 and (run / state.STATE).read_bytes() == terminal
    finally:
        finish(process)


@pytest.mark.parametrize("kind", ["model", "fit"])
@pytest.mark.parametrize("conflict", ["changed", "extra", "missing"])
def test_partial_output_sets_preserve_or_refuse_foreign_files(
    tmp_path: Path, kind: str, conflict: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT) if kind == "model" else fit_run(tmp_path)
    name = "model.json" if kind == "model" else "fit/FUND.json"
    process = start(run, kind, "output-" + Path(name).name)
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        target = run / name
        if conflict == "missing":
            target.unlink()
        elif conflict == "changed":
            target.write_bytes(b"foreign changed output")
        elif kind == "fit":
            target = run / "fit/foreign.json"
            target.write_bytes(b"foreign extra output")
        else:
            target = run / "handoffs/MODEL.md"
            target.write_bytes(b"foreign extra output")
        result = command(run, kind)
        if conflict == "missing":
            assert result.returncode == 0, result.stderr
            assert state.read(run)["steps"][kind.upper()]["status"] == "accepted"
        else:
            assert result.returncode == 1 and "output" in result.stderr
            assert target.read_bytes().startswith(b"foreign")
            assert state.read(run)["steps"][kind.upper()]["status"] == "running"
    finally:
        finish(process)


def test_caught_failure_is_terminal_after_source_changes(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    process = start(run, "model", "failure")
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        record = state.read(run)
        (Path(record["pack_root"]) / "acme_10k.txt").write_bytes(b"later source correction")
        result = command(run, "model")
        assert result.returncode == 1 and "persisted terminal failure" in result.stderr
        assert state.read(run)["steps"]["MODEL"]["status"] == "failed"
    finally:
        finish(process)


def test_repeated_native_rows_with_same_clock_remain_attributable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import UTC, datetime

    from rbotlib import runlog

    class Clock(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Clock:
            return cls(2026, 10, 13, tzinfo=UTC)

    run = eligible(tmp_path, RBOT_ROOT)
    process = start(run, "model", "log")
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        monkeypatch.setattr(runlog, "datetime", Clock)
        assert cli.main(["next", "--run", str(run)]) == 0
        assert cli.main(["next", "--run", str(run)]) == 0
        result = command(run, "model")
        assert result.returncode == 0, result.stderr
        previous = state.read(run)["steps"]["MODEL"]["host_execution"]["invocations"][0]
        assert len(previous["following_receipts"]) == 2
    finally:
        finish(process)


def test_replaced_owner_after_real_build_cannot_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib.model import qualification
    from rbotlib.model import run as writer
    from rbotlib.model.host import Model

    run = eligible(tmp_path, RBOT_ROOT)
    build = Model.build

    def replaced(
        captured: qualification.Inputs, generated_at: str
    ) -> tuple[writer.Written, dict[str, bytes]]:
        built = build(captured, generated_at)
        lock = run / state.LOCK
        lock.rename(run / "displaced-owner")
        lock.write_bytes((run / "displaced-owner").read_bytes())
        return built

    monkeypatch.setattr(Model, "build", staticmethod(replaced))
    assert cli.main(["model", "--run", str(run)]) == 1
    assert not (run / "model.json").exists() and not (run / "handoffs/MODEL.md").exists()
    assert state.read(run)["steps"]["MODEL"]["status"] == "running"


@pytest.mark.parametrize("change", ["approval", "backend", "handoff"])
def test_continuation_rechecks_origin_and_approved_inputs(tmp_path: Path, change: str) -> None:
    import shutil

    root = shutil.copytree(RBOT_ROOT, tmp_path / "qualified-root")
    run = eligible(tmp_path, root)
    process = start(run, "model", "build", root)
    process.kill()
    assert process.wait(timeout=10) == -9
    try:
        record = state.read(run)
        if change == "approval":
            record["approval"]["analyst"] = "foreign approval"
            (run / state.STATE).write_text(json.dumps(record))
            expected = "Approval"
        elif change == "backend":
            backend = root / "scripts/rbotlib/model/run.py"
            backend.write_text(backend.read_text() + "\n# changed installed backend\n")
            expected = "backend changed"
        else:
            path = run / "handoffs/CP-1.md"
            path.write_bytes(path.read_bytes() + b"\nforeign edit\n")
            expected = "registered inputs"
        before = (run / state.STATE).read_bytes()
        result = command(run, "model", root)
        assert (
            result.returncode == 1
            and "Traceback" not in result.stderr
            and expected in result.stderr
        ), result.stderr
        if change == "handoff":
            current = state.read(run)
            assert current["steps"]["MODEL"] == record["steps"]["MODEL"]
            assert current["steps"]["CP-1"]["note"] == "edited"
            assert current["steps"]["CP-1"]["current_origin"] == record["steps"]["CP-1"]
        else:
            assert (run / state.STATE).read_bytes() == before
        assert not (run / "model.json").exists()
        with pytest.raises(ValueError, match=expected):
            next_step.select(run, root)
    finally:
        finish(process)
