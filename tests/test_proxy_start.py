"""Source-backed fixture mechanics only; no model-written or Copilot qualification."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from state_receipt_assertions import outcome_bytes
from test_accept import accept, send
from test_proxy_run import Clock, _args, _base, _registry

import proxy_run
from conftest import CORPUS, corpus_gate
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib import runs, state
from rbotlib.cli import main as native
from rbotlib.corpus import load_registry, resolve_roots, verify
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT


@pytest.fixture(autouse=True)
def clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runs, "datetime", Clock)


def prepared(tmp_path: Path) -> tuple[Path, Path]:
    registry = _registry(tmp_path)
    data = json.loads(registry.read_text())
    source = tmp_path / "repo/tests/corpus/synthetic/p1/SYNTHETIC_10K.txt"
    source.write_text(source.read_text() + "Issuer: Test plc.\n")
    data["packs"][0]["files"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    data["packs"][0]["primary"] = False
    data["packs"][0]["files"][0]["document_type"] = "Other"
    data["packs"][0]["pathways"] = [
        {"id": "FULL_CREDIT_ASSESSMENT", "depth": "full", "fit": "partial"}
    ]
    registry.write_text(json.dumps(data))
    assert proxy_run.main(args(registry)) == 0
    return registry, _base(tmp_path) / "pack/rbot-runs/20261011-test-pending"


def args(registry: Path, *extra: str) -> list[str]:
    argv = _args(registry, *extra)
    argv[argv.index("EARNINGS_UPDATE")] = "FULL_CREDIT_ASSESSMENT"
    argv[argv.index("quick")] = "full"
    return argv


def ready(registry: Path, run: Path, *, blocked: bool = False) -> None:
    pack = load_registry(registry).pack("p1")
    send(run, RBOT_ROOT, name="proxy-source-backed-fixture")
    (run / "handoffs").mkdir(exist_ok=True)
    text = cp0_handoff(
        run, ("Test plc", "TEST"), "2026-01-31", registry_classification(pack), primary=False
    )
    # A sourced field and anchored citation survive simulated analyst edits/Approval.
    text = text.replace(
        "| issuer | — | Test plc | Analyst-asserted | — |",
        "| issuer | — | Test plc | Sourced | [C1] |",
    )
    text += "| C1 | SYNTHETIC_10K.txt | p. 1 | Test plc |\n"
    if blocked:
        text = text.replace("qa_status: Restricted", "qa_status: Blocked")
    (run / "handoffs/CP-0.md").write_text(text)
    assert accept(run) == (3 if blocked else 0)


def test_approval_requires_native_cp0_readiness(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    before = outcome_bytes(run)
    assert proxy_run.main(args(registry, "--approve")) == 1
    assert outcome_bytes(run) == before
    assert not (run / "run-brief.md").exists()


def test_approval_rechecks_registered_copy_before_native_writes(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    (run.parent.parent / "SYNTHETIC_10K.txt").write_text("tampered")
    before = outcome_bytes(run)
    assert proxy_run.main(args(registry, "--approve")) == 1
    assert outcome_bytes(run) == before
    assert not (run / "run-brief.md").exists()


def test_real_menu_blocked_refusal_then_simulated_approval_rename(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    raw = (run / "handoffs/CP-0.md").read_bytes()
    cp0 = state.read(run)["steps"]["CP-0"]
    capsys.readouterr()
    assert proxy_run.main(args(registry, "--approve")) == 1
    menu = capsys.readouterr().out
    assert "# Approval menu" in menu and "Blocked" in menu and "--acknowledge-blocked" in menu
    assert state.read(run)["approval"] is None
    assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 0
    target = run.with_name("20261011-test-full-credit-assessment")
    assert not run.exists() and target.is_dir()
    out = capsys.readouterr().out
    assert f"run folder: {target}" in out and "simulated analyst" in out
    final = state.read(target)
    assert final["approval"]["acknowledged_blocked_modules"]
    assert final["steps"]["CP-0"] == cp0
    assert (target / "handoffs/CP-0.md").read_bytes() == raw
    assert final["report"] == {"written_at": None, "html_sha256": None, "md_sha256": None}
    assert (
        final["plan"] == "CP-0 CP-1 CP-1A CP-DR CP-1B CP-1D MODEL CP-2 CP-3 FIT CP-5 CP-6".split()
    )
    assert final["deep_research"] is False and final["prior_case"]["accepted"] is False
    assert "approve --run" in (target / "log/rbot.log").read_text()
    assert hashlib.sha256(raw).hexdigest() == cp0["sha256"]


@pytest.mark.parametrize("blocked", [False, True])
def test_current_readiness_sources_and_collision_survive_approval(
    tmp_path: Path, blocked: bool
) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run, blocked=blocked)
    source = run.parent.parent / "SYNTHETIC_10K.txt"
    original = tmp_path / "repo/tests/corpus/synthetic/p1/SYNTHETIC_10K.txt"
    source_raw, original_raw = source.read_bytes(), original.read_bytes()
    history = {p.name: p.read_bytes() for p in (run / "validate/history/CP-0").iterdir()}
    handoff = run / "handoffs/CP-0.md"
    handoff.write_text(handoff.read_text().replace("Test fixture:", "Edited test fixture:"))
    raw = handoff.read_bytes()
    target = run.with_name("20261011-test-full-credit-assessment")
    target.mkdir()
    (target / "reservation.txt").write_text("original reservation")
    assert (
        proxy_run.main(
            args(
                registry,
                "--approve",
                "--acknowledge-blocked",
                "--set",
                "issuer=Analyst context",
                "--set",
                "objective=Explicit simulated review",
                "--set",
                "analyst=Explicit fixture analyst",
            )
        )
        == 0
    )
    target = target.with_name(target.name + "-2")
    record = state.read(target)
    assert record["approval"]["analyst"] == "Explicit fixture analyst"
    assert runs.discover_unfinished(source.parent) == target
    assert record["steps"]["CP-0"]["current_edits"][-1]["result"]["exit"] == (3 if blocked else 0)
    fields = {
        r[0]: r[1:]
        for r in parse((target / "run-brief.md").read_text()).tables["brief.run_brief_fields"].rows
    }
    assert fields["issuer"] == ["Test plc", "Sourced", "Analyst context", "[C1]"]
    assert fields["objective"][:2] == ["Explicit simulated review", "Analyst-asserted"]
    assert (target / "handoffs/CP-0.md").read_bytes() == raw
    assert {p.name: p.read_bytes() for p in (target / "validate/history/CP-0").iterdir()} == history
    assert source.read_bytes() == source_raw and original.read_bytes() == original_raw
    before = outcome_bytes(target)
    assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 1
    assert outcome_bytes(target) == before  # no reapproval/rebuild
    assert proxy_run.main(args(registry)) == 1


@pytest.mark.parametrize("bad", ["malformed", "wrong-issuer", "prepared", "history", "log"])
def test_changed_current_context_refuses_before_brief(tmp_path: Path, bad: str) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    handoff = run / "handoffs/CP-0.md"
    if bad == "malformed":
        handoff.write_text("invalid fixture Handoff")
    elif bad == "wrong-issuer":
        handoff.write_text(handoff.read_text().replace("issuer_id: TEST", "issuer_id: WRONG"))
    elif bad == "prepared":
        (run / "prepared/index.json").write_text("{}")
    elif bad == "history":
        (run / "validate/history/CP-0/000001.json").write_text("{}")
    else:
        with (run / "log/rbot.log").open("a") as stream:
            stream.write("foreign row\n")
    history = (run / "validate/history/CP-0/000001.json").read_bytes()
    assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 1
    assert (run / "validate/history/CP-0/000001.json").read_bytes() == history
    assert not (run / "run-brief.md").exists() and state.read(run)["approval"] is None


@pytest.mark.parametrize("relative", ["handoffs/CP-0.md", "prepared/index.json", "grading.json"])
def test_unsafe_run_input_refuses_without_reading_link_target(
    tmp_path: Path, relative: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    destination = run / relative
    destination.unlink(missing_ok=True)
    protected = tmp_path / "protected"
    protected.write_text("never read or write this target")
    destination.symlink_to(protected)
    original_bytes, original_text = Path.read_bytes, Path.read_text

    def guarded_bytes(path: Path) -> bytes:
        assert path != protected and path != destination, "unsafe target read"
        return original_bytes(path)

    def guarded_text(path: Path, encoding: str | None = None, errors: str | None = None) -> str:
        assert path != protected and path != destination, "unsafe target read"
        return original_text(path, encoding, errors)

    monkeypatch.setattr(Path, "read_bytes", guarded_bytes)
    monkeypatch.setattr(Path, "read_text", guarded_text)
    assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 1
    assert destination.is_symlink()
    assert not (run / "run-brief.md").exists()


@pytest.mark.parametrize(
    "kind",
    ["linked-copy", "linked-pack", "hardlink-copy", "escape-id", "escape-file", "source-root"],
)
def test_generated_destination_guards_precede_hash_reads(
    tmp_path: Path, kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, run = prepared(tmp_path)
    copied = run.parent.parent / "SYNTHETIC_10K.txt"
    source = tmp_path / "repo/tests/corpus/synthetic/p1/SYNTHETIC_10K.txt"
    source_raw = source.read_bytes()
    extra: list[str] = []
    if kind == "linked-copy":
        copied.unlink()
        copied.symlink_to(source)
    elif kind == "hardlink-copy":
        copied.unlink()
        os.link(source, copied)
    elif kind == "linked-pack":
        extra = ["--out", str(tmp_path / "linked")]
        (tmp_path / "linked/p1").mkdir(parents=True)
        (tmp_path / "linked/p1/pack").symlink_to(source.parent, target_is_directory=True)
    elif kind.startswith("escape"):
        data = json.loads(registry.read_text())
        if kind == "escape-id":
            data["packs"][0]["id"] = "../p1"
            extra = ["--pack", "../p1"]
        else:
            data["packs"][0]["files"][0]["path"] = "../outside"
        registry.write_text(json.dumps(data))
    else:
        extra = ["--out", str(source.parent)]

    def forbidden(path: Path) -> str:
        pytest.fail(f"hash read preceded unsafe destination refusal: {path}")

    monkeypatch.setattr(proxy_run, "sha256_file", forbidden)
    before = outcome_bytes(run)
    for flags in ([], ["--approve"]):
        assert proxy_run.main(args(registry, *extra, *flags)) == 1
    assert outcome_bytes(run) == before and source.read_bytes() == source_raw


@pytest.mark.parametrize(
    "assignment", ["issuer_id=", "as_of_date=invalid", "pathway=OTHER", "objective=x\nInjected"]
)
def test_native_required_field_edits_refuse_honestly(tmp_path: Path, assignment: str) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    assert proxy_run.main(args(registry, "--approve", "--set", assignment)) == 1
    assert state.read(run)["approval"] is None and not (run / "grading.json").exists()


def test_primary_needs_explicit_native_tranche_and_prior_hint_is_not_evidence(
    tmp_path: Path,
) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    data = json.loads(registry.read_text())
    data["packs"][0]["prior_pack"] = "unavailable-registry-prior"
    registry.write_text(json.dumps(data))
    flags = ["--approve", "--acknowledge-blocked", "--primary", "yes"]
    assert proxy_run.main(args(registry, *flags)) == 1
    assert state.read(run)["approval"] is None
    assert (
        proxy_run.main(
            args(
                registry,
                *flags,
                "--set",
                "primary=Yes",
                "--set-tranche",
                "NEW-1",
                "instrument=Simulated tranche",
            )
        )
        == 0
    )
    target = runs.discover_unfinished(run.parent.parent)
    assert target is not None
    final = state.read(target)
    assert final["primary"] is True and final["prior_case"]["accepted"] is False
    assert "NEW-1.borrower" in json.loads((target / "grading.json").read_text())["brief_gaps"]


def test_uninstalled_registry_pathway_is_not_a_menu_choice(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    data = json.loads(registry.read_text())
    data["packs"][0]["pathways"][0] = {"id": "EARNINGS_UPDATE", "depth": "quick", "fit": "partial"}
    registry.write_text(json.dumps(data))
    assert proxy_run.main(_args(registry, "--approve", "--acknowledge-blocked")) == 1
    assert state.read(run)["approval"] is None


def test_busy_native_owner_prevents_simulated_brief_writes(tmp_path: Path) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    owner = state._Locked(run)
    try:
        before = outcome_bytes(run)
        assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 1
        assert outcome_bytes(run) == before and not (run / "run-brief.md").exists()
    finally:
        assert owner.close() == []


@pytest.mark.parametrize("kind", ["fifo", "directory", "hardlink"])
def test_unsupported_grading_destination_refuses_before_brief(tmp_path: Path, kind: str) -> None:
    registry, run = prepared(tmp_path)
    ready(registry, run)
    target = run / "grading.json"
    if kind == "fifo":
        os.mkfifo(target)
    elif kind == "directory":
        target.mkdir()
    else:
        os.link(run / "handoffs/CP-0.md", target)
    before = outcome_bytes(run)
    assert proxy_run.main(args(registry, "--approve", "--acknowledge-blocked")) == 1
    assert outcome_bytes(run) == before and not (run / "run-brief.md").exists()


def test_start_does_not_silently_discard_simulated_edits(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    with pytest.raises(SystemExit) as stop:
        proxy_run.main(_args(registry, "--set", "objective=review"))
    assert stop.value.code == 2 and not _base(tmp_path).exists()


def test_multiline_output_path_refuses_before_copy(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    out = tmp_path / "multiline\noutput"
    assert proxy_run.main(_args(registry, "--out", str(out))) == 1
    assert not out.exists()


@pytest.mark.corpus
def test_original_primary_corpus_native_start_to_approval(tmp_path: Path) -> None:
    pack = CORPUS.pack("czr-2026q2-primary")
    roots = resolve_roots(CORPUS)
    corpus_gate(verify(CORPUS, pack, roots))
    argv = [
        "--pack",
        pack.id,
        "--pathway",
        "FULL_CREDIT_ASSESSMENT",
        "--depth",
        "full",
        "--out",
        str(tmp_path),
    ]
    assert proxy_run.main(argv) == 0
    run = tmp_path / pack.id / "pack/rbot-runs/20261011-czr-pending"
    copied = {f.path: (run.parent.parent / f.path).read_bytes() for f in pack.files}
    send(run, RBOT_ROOT, name="source-backed-primary-fixture")
    (run / "handoffs").mkdir(exist_ok=True)
    text = cp0_handoff(
        run,
        (pack.data["issuer"]["name"], "CZR"),
        pack.data["as_of"],
        registry_classification(pack),
        primary=True,
    )
    (run / "handoffs/CP-0.md").write_text(text)
    assert accept(run) == 0
    flags = ["--approve", "--set-tranche", "NEW-1", "instrument=Simulated tranche only"]
    assert proxy_run.main([*argv, *flags]) == 0
    target = run.with_name("20261011-czr-full-credit-assessment")
    final = state.read(target)
    assert final["approval"]["pathway_grade"] == "Available" and final["primary"] is True
    assert final["steps"]["FIT"]["status"] == "pending"
    assert all((run.parent.parent / f.path).read_bytes() == copied[f.path] for f in pack.files)
    assert verify(CORPUS, pack, roots) == []
    # Controller selection only; no worker transport or financial output is implied.
    assert native(["next", "--run", str(target)]) == 0
    assert (
        json.loads((target / "run-state.json").read_text())["steps"]["CP-1"]["status"] == "pending"
    )
