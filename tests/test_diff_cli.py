"""Native diff publication and read-only full-pair qualification."""

from __future__ import annotations

import copy
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from test_approve import TARGET, _approve
from test_prior_approval import doc, ready, snapshot
from test_prior_context import native as native
from test_prior_report import table

from rbotlib import cli, current, prior_context, state
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT


def publish(run: Path, root: Path, prior: str = "prior.html") -> int:
    return cli.main(["--root", str(root), "diff", "--run", str(run), "--prior", prior])


def pair(run: Path) -> tuple[bytes, bytes]:
    return (run / "prior/diff.json").read_bytes(), (run / "prior/diff.md").read_bytes()


def test_native_pair_is_deterministic_and_qualified_under_held_lock(
    native: tuple[Path, Path],
) -> None:
    from rbotlib.prior_diff import qualified_prior

    run, root = native
    before = state.read(run)
    assert publish(run, root) == 0
    original = pair(run)
    assert publish(run, root, str(run.parent.parent / "prior.html")) == 0
    assert pair(run) == original
    saved = snapshot(run)
    log = (run / "log/rbot.log").read_bytes()
    state_bytes = (run / state.STATE).read_bytes()
    with state.publication(run) as checked:
        prior, result, md = qualified_prior(run, root, state.read(run))
        checked()
    assert prior.source == "prior.html" and json.loads(original[0]) == result
    assert md.encode() == original[1] and snapshot(run) == saved
    assert (run / "log/rbot.log").read_bytes() == log
    assert (run / state.STATE).read_bytes() == state_bytes
    after = state.read(run)
    for record in (before, after):
        record.pop("command_receipts", None)
        record.pop("updated_at", None)
    assert after == before and result["inputs"]["schema"] == "rbot-prior-context/1"
    assert any("skipped" in value for value in result["limitations"])
    assert "Date basis" in md and "sha256" in md


@pytest.mark.parametrize("prior", ["../prior.html", "./prior.html", "other.html", "/tmp/foreign"])
def test_no_prior_override(native: tuple[Path, Path], prior: str) -> None:
    run, root = native
    saved = snapshot(run)
    assert publish(run, root, prior) == 1
    assert snapshot(run) == saved and not (run / "prior").exists()


@pytest.mark.parametrize("choice", ["accepted", "declined", "absent", "unapproved"])
def test_refusals_leave_outputs_absent(tmp_path: Path, choice: str) -> None:
    run = ready(RBOT_ROOT, tmp_path, {} if choice == "absent" else {"prior.html": doc()})
    if choice != "unapproved":
        assert (
            _approve(RBOT_ROOT, run, "--prior-case", "yes" if choice == "accepted" else "no") == 0
        )
        run = run.parent / TARGET
    before = snapshot(run)
    assert publish(run, RBOT_ROOT) == 1
    assert snapshot(run) == before and not (run / "prior").exists()


@pytest.mark.parametrize("edit", ["json", "duplicate", "md", "missing"])
def test_full_pair_integrity(native: tuple[Path, Path], edit: str) -> None:
    from rbotlib.prior_diff import qualified_prior

    run, root = native
    assert publish(run, root) == 0
    target = run / "prior" / ("diff.md" if edit in ("md", "missing") else "diff.json")
    if edit == "missing":
        target.unlink()
    elif edit == "duplicate":
        target.write_text(target.read_text().replace("{", '{"prior":null,', 1))
    else:
        target.write_bytes(target.read_bytes() + b" ")
    before = snapshot(run)
    with pytest.raises(RunError, match=r"diff .*--run.*--prior"):
        qualified_prior(run, root, state.read(run))
    assert snapshot(run) == before


@pytest.mark.parametrize("change", ["source", "current", "record"])
def test_inputs_and_caller_record_must_be_fresh(native: tuple[Path, Path], change: str) -> None:
    from rbotlib.prior_diff import qualified_prior

    run, root = native
    assert publish(run, root) == 0
    record = state.read(run)
    if change == "source":
        target = run.parent.parent / "prior.html"
        target.write_bytes(target.read_bytes() + b"changed")
    elif change == "current":
        target = run / "handoffs/CP-1C.md"
        target.write_bytes(target.read_bytes() + b"\nRegistered clarification.\n")
        current.reconcile(run, root)
    else:
        record["prior_case"]["report"] = "foreign.html"
    with pytest.raises(RunError):
        qualified_prior(run, root, record)
    if change == "current":
        assert publish(run, root) == 0
        assert qualified_prior(run, root, state.read(run))


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "directory", "fifo", "parent"])
def test_both_outputs_preflight_before_replacement(
    native: tuple[Path, Path], tmp_path: Path, kind: str
) -> None:
    from rbotlib.prior_diff import qualified_prior

    run, root = native
    assert publish(run, root) == 0
    old_json, old_md = pair(run)
    target = run / "prior/diff.md"
    target.unlink()
    foreign = tmp_path / "foreign"
    foreign.write_bytes(old_md)
    if kind == "symlink":
        target.symlink_to(foreign)
    elif kind == "hardlink":
        target.hardlink_to(foreign)
    elif kind == "directory":
        target.mkdir()
    elif kind == "fifo":
        os.mkfifo(target)
    else:
        (run / "prior").rename(tmp_path / "moved")
        (run / "prior").symlink_to(tmp_path / "moved", target_is_directory=True)
    assert publish(run, root) == 1
    assert (run / "prior/diff.json").read_bytes() == old_json and foreign.read_bytes() == old_md
    with pytest.raises(RunError):
        qualified_prior(run, root, state.read(run))


@pytest.mark.parametrize("error_type", [OSError, UnicodeError])
def test_busy_and_second_write_failure_are_detectable(
    native: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error_type: type[Exception],
) -> None:
    from rbotlib import prior_diff

    run, root = native
    with state.publication(run):
        assert publish(run, root) == 1
    assert not (run / "prior").exists()
    writer = prior_diff.write_atomic

    def fail_md(path: Path, text: str) -> None:
        if path.name == "diff.md":
            raise error_type("injected publication fault")
        writer(path, text)

    monkeypatch.setattr(prior_diff, "write_atomic", fail_md)
    assert publish(run, root) == 1
    assert "diff.md" in capsys.readouterr().err
    assert (run / "prior/diff.json").is_file() and not (run / "prior/diff.md").exists()
    with pytest.raises(RunError):
        prior_diff.qualified_prior(run, root, state.read(run))


def test_fresh_binding_is_checked_immediately_before_publication(
    native: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib import prior_diff

    run, root = native
    assert publish(run, root) == 0
    before = pair(run)
    original = prior_diff._pair

    def change_after_comparison(
        context: prior_context.PriorContext, root: Path
    ) -> tuple[dict[str, Any], str]:
        result = original(context, root)
        target = run / "handoffs/CP-1C.md"
        target.write_bytes(target.read_bytes() + b"\nchanged during build\n")
        return result

    monkeypatch.setattr(prior_diff, "_pair", change_after_comparison)
    assert publish(run, root) == 1 and pair(run) == before


def test_cp8_and_volatile_changes_leave_pair_valid(native: tuple[Path, Path]) -> None:
    from test_next import blocked

    from rbotlib.prior_diff import qualified_prior

    run, root = native
    assert publish(run, root) == 0
    expected = pair(run)
    blocked(run, root, "CP-8")
    state.update(run, lambda record: record.update(volatile_counter=999))
    assert qualified_prior(run, root, state.read(run))
    assert pair(run) == expected


def test_catalog_union_unknown_keys_and_safe_complete_markdown(native: tuple[Path, Path]) -> None:
    from rbotlib.prior_diff import _pair

    run, root = native
    context = prior_context.capture(run, root)
    prior, now = copy.deepcopy(context.prior.payload), copy.deepcopy(context.current)
    assert prior is not None
    prior["front_page"] = "OTHER"
    catalog = json.loads((root / "catalog.json").read_text())
    catalog["front_pages"]["OTHER"] = {"tables": ["model.metrics", "cp8.ignored"]}
    catalog["front_pages"]["credit_snapshot"]["tables"].remove("model.metrics")
    (root / "catalog.json").write_text(json.dumps(catalog))
    hostile = '<script>"|\n**bad**'
    table(prior, "model.house", ["item", "value"], [[hostile, "—"], ["gone", "5"]])
    table(now, "model.house", ["item", "value"], [[hostile, "0"], ["new", "—"]])
    table(prior, "model.metrics", ["metric_id", "ltm"], [["metric", "1"]])
    table(now, "model.metrics", ["metric_id", "ltm"], [["metric", "2"]])
    context = prior_context.PriorContext(
        replace(context.prior, payload=prior), now, context.binding
    )
    result, md = _pair(context, root)
    assert {row["kind"] for row in result["changes"]} >= {"added", "removed", "changed"}
    assert any(row["table"] == "model.metrics" for row in result["changes"])
    assert all(not row["table"].startswith("cp8.") for row in result["changes"])
    assert "<script>" not in md and "&#124;" in md and "\\n" in md
    assert "&#91;missing&#93;" in md and "—" in md and "&lt;script&gt;" in md
    _, unchanged = _pair(prior_context.PriorContext(context.prior, prior, context.binding), root)
    assert "No changed, added or removed comparable fields" in unchanged
    catalog["front_pages"]["OTHER"]["tables"].append("unknown.key")
    (root / "catalog.json").write_text(json.dumps(catalog))
    with pytest.raises(RunError, match="unknown comparison key"):
        _pair(context, root)


@pytest.mark.parametrize(
    "field,value",
    [
        ("limitations", None),
        ("limitations", ["legacy limitation"]),
        ("limitations", {"approval": "legacy limitation"}),
        ("front_page", "unknown"),
        ("front_page", []),
        ("front_page", ""),
    ],
)
def test_malformed_original_extensions_refuse_actionably(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    field: str,
    value: object,
) -> None:
    original = doc()
    original[field] = value
    monkeypatch.setattr("test_prior_context.doc", lambda: original)
    run, root = request.getfixturevalue("native")
    before = snapshot(run)
    assert publish(run, root) == 1
    assert ("limitations" if field == "limitations" else "Front Page") in capsys.readouterr().err
    assert snapshot(run) == before and not (run / "prior").exists()
