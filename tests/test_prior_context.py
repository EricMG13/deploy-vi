"""Native owned comparison inputs; fixture receipts never qualify live workers."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from test_approve import TARGET, _approve
from test_model_host import with_cp1
from test_next import blocked
from test_prior_approval import doc, ready, snapshot

from conftest import write_module
from rbotlib import cli, prior_context, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, load_rules
from spec_fixture import stand_in


@pytest.fixture
def native(tmp_path: Path) -> tuple[Path, Path]:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    write_module(root, stand_in("CP-8", []), load_rules(root))
    catalog = json.loads((root / "catalog.json").read_text())
    catalog["pathways"][0]["depths"]["full"].append("CP-8")
    (root / "catalog.json").write_text(json.dumps(catalog))
    run = ready(root, tmp_path, {"prior.html": doc()})
    assert _approve(root, run, "--prior-case", "yes") == 0
    run = run.parent / TARGET
    with_cp1(run, root)
    assert cli.main(["--root", str(root), "model", "--run", str(run)]) == 0
    blocked(run, root, "CP-1C")
    for name, step in state.read(run)["steps"].items():
        if name != "CP-8" and step["status"] == "pending":
            state.set_status(run, name, "skipped", "fixture unavailable producer")
    return run, root


def test_native_model_context_is_detached_deterministic_and_read_only(
    native: tuple[Path, Path],
) -> None:
    run, root = native
    before = snapshot(run)
    context = prior_context.capture(run, root)
    assert context == prior_context.capture(run, root, "prior.html")
    assert context == prior_context.capture(run, root, str(run.parent.parent / "prior.html"))
    assert (
        context.prior.metadata is not None and context.prior.metadata["report_date"] == "2026-10-14"
    )
    from rbotlib.diff import compare

    assert context.prior.payload is not None
    assert (
        compare(context.prior.payload, context.current, ["model.house"])["prior"]["run_id"]
        == "earlier"
    )
    current = context.current
    assert current["generated_at"] == state.read(run)["approval"]["approved_at"]
    assert current["generated_at_basis"] == "current Approval approved_at; not Report publication"
    assert "CP-8" not in current["steps"] and "CP-8" not in current["plan"]
    assert current["handoffs"]["CP-1C"]["status"] == "blocked"
    assert "no figures" in current["handoffs"]["CP-1"]["gaps_md"]
    assert current["model"]["schema"] == "rbot-model/1"
    assert {x["kind"] for x in current["limitations"]["unforeseen"]} >= {
        "blocked",
        "failed",
        "skipped",
    }
    assert prior_context.requalify(run, root, json.loads(json.dumps(context.binding))) == context
    current["run_brief"]["front_matter"]["issuer_id"] = "detached"
    assert (
        prior_context.capture(run, root).current["run_brief"]["front_matter"]["issuer_id"] == "ACME"
    )
    assert snapshot(run) == before


@pytest.mark.parametrize(
    "requested", ["../prior.html", "./prior.html", "other.html", "", "/tmp/foreign.html"]
)
def test_exact_approved_path_is_required_before_any_foreign_read(
    native: tuple[Path, Path], requested: str
) -> None:
    run, root = native
    before = snapshot(run)
    with pytest.raises(RunError, match="differs from approved"):
        prior_context.capture(run, root, requested)
    assert snapshot(run) == before


@pytest.mark.parametrize(
    "defect", ["source", "prior", "handoff", "brief", "root", "model", "receipt", "host-state"]
)
def test_source_context_and_host_evidence_fail_closed(
    native: tuple[Path, Path], defect: str
) -> None:
    run, root = native
    paths = {
        "source": run.parent.parent / "acme_10k.txt",
        "prior": run.parent.parent / "prior.html",
        "handoff": run / "handoffs/CP-1C.md",
        "brief": run / "run-brief.md",
        "root": root / "catalog.json",
        "model": run / "model.json",
        "receipt": run / "log/rbot.log",
    }
    if defect == "host-state":
        state.update(run, lambda r: r["steps"]["MODEL"].update(host_execution={}))
    else:
        path = paths[defect]
        path.write_bytes(b"changed" if defect == "receipt" else path.read_bytes() + b"\nchanged\n")
    before = snapshot(run)
    with pytest.raises((RunError, ValueError)):
        prior_context.capture(run, root)
    assert snapshot(run) == before


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "directory", "fifo", "parent"])
def test_original_and_prepared_perimeter_before_reads(
    native: tuple[Path, Path], tmp_path: Path, kind: str
) -> None:
    import os

    run, root = native
    target = run.parent.parent / "prior.html"
    preserved = tmp_path / "preserved"
    preserved.write_bytes(target.read_bytes())
    target.unlink()
    if kind == "symlink":
        target.symlink_to(preserved)
    elif kind == "hardlink":
        target.hardlink_to(preserved)
    elif kind == "directory":
        target.mkdir()
    elif kind == "fifo":
        os.mkfifo(target)
    else:
        prepared = run / "prepared"
        relocated = tmp_path / "relocated"
        prepared.rename(relocated)
        prepared.symlink_to(relocated, target_is_directory=True)
        target.write_bytes(preserved.read_bytes())
    with pytest.raises((RunError, OSError)):
        prior_context.capture(run, root)
    assert preserved.read_bytes() == doc_bytes()


def doc_bytes() -> bytes:
    from rbotlib.report.html_parts import embed_json

    return embed_json(doc()).encode()


def test_cp8_completion_and_volatile_fields_do_not_stale_binding(native: tuple[Path, Path]) -> None:
    from test_diff_cli import publish

    run, root = native
    before = prior_context.capture(run, root)
    assert publish(run, root) == 0
    blocked(run, root, "CP-8")
    state.update(run, lambda r: r.update(volatile_counter=999))
    with (run / "log/rbot.log").open("ab") as log:
        log.write(b"unrelated later log row\n")
    assert prior_context.requalify(run, root, before.binding) == before


def test_current_registered_edit_requires_new_binding(native: tuple[Path, Path]) -> None:
    from rbotlib import current

    run, root = native
    before = prior_context.capture(run, root)
    path = run / "handoffs/CP-1C.md"
    path.write_bytes(path.read_bytes() + b"\nAnalyst clarification.\n")
    with pytest.raises(RunError):
        prior_context.requalify(run, root, before.binding)
    current.reconcile(run, root)
    fresh = prior_context.capture(run, root)
    assert fresh.binding != before.binding
    assert (
        fresh.current["handoffs"]["CP-1C"]["sha256"]
        != before.current["handoffs"]["CP-1C"]["sha256"]
    )
    with pytest.raises(RunError, match="binding changed"):
        prior_context.requalify(run, root, before.binding)


@pytest.mark.parametrize("choice", ["accepted", "declined", "absent", "unapproved"])
def test_pending_predecessor_and_decline_refuse(tmp_path: Path, choice: str) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    run = ready(root, tmp_path, {} if choice == "absent" else {"prior.html": doc()})
    if choice != "unapproved":
        assert _approve(root, run, "--prior-case", "yes" if choice == "accepted" else "no") == 0
        run = run.parent / TARGET
    before = snapshot(run)
    match = "terminal predecessor" if choice == "accepted" else "accepted offered"
    with pytest.raises(RunError, match=match):
        prior_context.capture(run, root)
    assert snapshot(run) == before


def test_capture_has_no_nested_lock(native: tuple[Path, Path]) -> None:
    run, root = native
    with state.publication(run) as checked:
        checked()
        assert prior_context.capture(run, root)
        checked()


def test_registered_cp0_narrative_edit_retains_native_pending_lineage(
    native: tuple[Path, Path],
) -> None:
    from rbotlib import current
    from rbotlib.handoff import parse

    run, root = native
    original = prior_context.capture(run, root)
    path = run / "handoffs/CP-0.md"
    path.write_bytes(path.read_bytes() + b"\nApproved narrative clarification.\n")
    current.reconcile(run, root)
    fresh = prior_context.capture(run, root)
    cp0 = fresh.current["handoffs"]["CP-0"]
    assert cp0["original_front_matter"] == dict(parse(path.read_text()).front_matter)
    assert cp0["front_matter"]["run_id"] == run.name
    assert cp0["native_cp0_lineage"] == state.read(run)["cp0_lineage"]
    assert fresh.binding != original.binding


def test_host_output_change_between_qualification_and_capture_refuses(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib import dispatch
    from rbotlib.contract import Input
    from rbotlib.rules import Rules

    run, root = native
    original = dispatch._handoff_permission
    changed = False

    def replace_after_qualification(
        run: Path, root: Path, need: Input, record: dict[str, object], rules: Rules
    ) -> tuple[str, str]:
        nonlocal changed
        result = original(run, root, need, record, rules)
        if need.values == ("MODEL",) and not changed:
            path = run / "model.json"
            path.write_bytes(path.read_bytes() + b" \n")
            changed = True
        return result

    monkeypatch.setattr(dispatch, "_handoff_permission", replace_after_qualification)
    with pytest.raises(RunError, match="MODEL"):
        prior_context.capture(run, root)
