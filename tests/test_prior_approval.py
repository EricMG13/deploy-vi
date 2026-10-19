"""Native owned Approval selects only freshly qualified original offered Reports."""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from state_receipt_assertions import artifact_bytes
from test_approve import TARGET, _approve, _brief, _state
from test_prior_cp0 import HEAD
from test_prior_report import document

from cp0_fixture import cp0_handoff
from rbotlib import approve as ap
from rbotlib.cli import main
from rbotlib.prior_report import parse_report
from rbotlib.report.html_parts import embed_json
from rbotlib.report.markdown import render_markdown
from rbotlib.rules import Rules
from spec_fixture import SOURCES, build_tree
from test_grade import ACME, FILES, _acme


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    target = tmp_path / "rbot"
    target.mkdir()
    return build_tree(target, rules, SOURCES)


def doc(run_id: str = "earlier", date: str = "2026-10-14", issuer: str = "ACME") -> dict[str, Any]:
    payload = document()
    payload.update(run_id=run_id, generated_at=date + "T00:00:00+00:00")
    for front in (
        payload["run_brief"]["front_matter"],
        payload["handoffs"]["MODEL"]["front_matter"],
    ):
        front.update(run_id=run_id, issuer_id=issuer)
    payload["run_brief"]["tables"]["snapshot.run_header"]["rows"] = [[run_id, issuer, date]]
    return payload


def ready(root: Path, tmp_path: Path, reports: dict[str, dict[str, Any]]) -> Path:
    originals = {
        name: render_markdown(payload, [], []) if name.endswith(".md") else embed_json(payload)
        for name, payload in reports.items()
    }
    run = _acme(tmp_path, originals, managed=True)
    classes = FILES | {
        name: ("issuer", "RBOT Report", "Acme Holdings, Inc.", "Yes") for name in reports
    }
    rows = []
    for name, payload in reports.items():
        header = payload["run_brief"]["tables"]["snapshot.run_header"]["rows"][0]
        # Planted fixture values, not the production qualification helper, are the oracle.
        date = header[2] if header[2] != "—" else payload["generated_at"].split("T")[0]
        offered = "Yes" if header[1] == "ACME" else "No"
        rows.append(
            f"| {name} | {date} | {header[0]} | FULL_CREDIT_ASSESSMENT | full | {offered} |"
        )
    text = cp0_handoff(run, ACME, "2026-10-02", classes, primary=False)
    (run / "handoffs").mkdir(exist_ok=True)
    (run / "handoffs/CP-0.md").write_text(text.replace(HEAD, HEAD + "\n".join(rows) + "\n"))
    rebuild(root, run)
    return run


def rebuild(root: Path, run: Path, *edits: str) -> None:
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert main(["brief", "--run", str(run), "--set", "objective=Annual review", *edits]) == 0
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 0


def snapshot(run: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(run)): artifact_bytes(run, p.relative_to(run))
        for p in run.rglob("*")
        if p.is_file() and not p.name.startswith(".") and p != run / "log/rbot.log"
    }


def refused(root: Path, run: Path, capsys: pytest.CaptureFixture[str], message: str) -> None:
    before = snapshot(run)
    sources = {
        p: p.read_bytes()
        for p in run.parent.parent.rglob("*")
        if p.is_file() and run not in p.parents
    }
    capsys.readouterr()
    assert _approve(root, run, "--prior-case", "yes") == 1
    assert message in capsys.readouterr().out
    assert snapshot(run) == before
    assert list(run.parent.iterdir()) == [run] and not (run.parent / TARGET).exists()
    assert all(p.read_bytes() == raw for p, raw in sources.items())
    assert not list(run.glob(".approve-*"))


@pytest.mark.parametrize("reverse", [False, True])
def test_newest_is_order_independent_and_uses_original_calendar_date(
    root: Path, tmp_path: Path, reverse: bool
) -> None:
    newer = doc("newer", "2026-10-15")
    newer["generated_at"] = "2026-10-15T00:30:00+01:00"
    newer["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][2] = "—"
    reports = {"old.html": doc(), "new.html": newer}
    run = ready(root, tmp_path, dict(reversed(list(reports.items()))) if reverse else reports)
    assert _approve(root, run, "--prior-case", "yes") == 0
    target = run.parent / TARGET
    assert _state(target)["prior_case"] == {"offered": True, "accepted": True, "report": "new.html"}
    assert [r[0] for r in _brief(target).tables["brief.prior_case"].rows if r[-1] == "Yes"] == [
        "new.html"
    ]


@pytest.mark.parametrize("reverse", [False, True])
def test_equivalent_actual_emitters_dedupe_to_html(
    root: Path, tmp_path: Path, reverse: bool
) -> None:
    payload = doc()
    emitted = parse_report(render_markdown(payload, [], []), "md")
    reports = {"prior.md": emitted, "prior.html": emitted}
    run = ready(root, tmp_path, dict(reversed(list(reports.items()))) if reverse else reports)
    assert _approve(root, run, "--prior-case", "yes") == 0
    assert _state(run.parent / TARGET)["prior_case"]["report"] == "prior.html"


@pytest.mark.parametrize("kind", ["conflict", "tie", "older-conflict"])
@pytest.mark.parametrize("reverse", [False, True])
def test_ambiguity_refuses_before_publication(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], kind: str, reverse: bool
) -> None:
    other = doc("different" if kind == "tie" else "earlier")
    other["limitations"]["approval"] = ["conflicting original"]
    reports = {"a.html": doc(), "b.html": other}
    if kind == "older-conflict":
        reports["new.html"] = doc("new", "2026-10-15")
    run = ready(root, tmp_path, dict(reversed(list(reports.items()))) if reverse else reports)
    refused(root, run, capsys, "tied newest" if kind == "tie" else "conflicting payloads")


@pytest.mark.parametrize("foreign", [False, True])
def test_no_eligible_offered_source_refuses(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], foreign: bool
) -> None:
    run = ready(root, tmp_path, {"foreign.html": doc(issuer="OTHER")} if foreign else {})
    refused(root, run, capsys, "no Prior Case was offered")


def test_decline_preserves_offered_flag_and_skipped_reason(root: Path, tmp_path: Path) -> None:
    other = copy.deepcopy(doc())
    other["limitations"]["approval"] = ["conflict explicitly declined"]
    run = ready(root, tmp_path, {"a.html": doc(), "b.html": other})
    assert _approve(root, run, "--prior-case", "no") == 0
    target = run.parent / TARGET
    assert _state(target)["prior_case"] == {"offered": True, "accepted": False, "report": None}
    assert _state(target)["steps"]["CP-8"] == {
        "kind": "module",
        "status": "skipped",
        "reason": "no prior case",
    }
    assert all(r[-1] == "No" for r in _brief(target).tables["brief.prior_case"].rows)


@pytest.mark.parametrize("change", ["source", "payload", "date", "offered", "issuer"])
def test_source_and_claim_changes_refuse_before_publication(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], change: str
) -> None:
    run = ready(root, tmp_path, {"prior.html": doc()})
    if change == "source":
        (run.parent.parent / "prior.html").write_text("edited source")
    elif change == "payload":
        changed = doc()
        changed["limitations"]["approval"] = ["same metadata but edited payload"]
        (run.parent.parent / "prior.html").write_text(embed_json(changed))
    elif change == "issuer":
        rebuild(root, run, "--set", "issuer_id=OTHER")
    else:
        cp0 = run / "handoffs/CP-0.md"
        text = cp0.read_text()
        text = (
            text.replace("| prior.html | 2026-10-14 |", "| prior.html | 2026-10-13 |")
            if change == "date"
            else text.replace("| full | Yes |", "| full | No |")
        )
        cp0.write_text(text)
        assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    message = (
        "confirmed Run Brief"
        if change == "issuer"
        else (
            "changed after rbot grade" if change in ("date", "offered") else "no longer validates"
        )
    )
    refused(root, run, capsys, message)


def test_source_change_after_prepare_refuses_before_publication(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    run = ready(root, tmp_path, {"prior.html": doc()})
    before = snapshot(run)
    original = ap._staged

    @contextmanager
    def stages(path: Path, contents: list[str]) -> Iterator[list[Path]]:
        with original(path, contents) as files:
            (path.parent.parent / "prior.html").write_text("changed after qualification")
            yield files

    monkeypatch.setattr(ap, "_staged", stages)
    capsys.readouterr()
    assert _approve(root, run, "--prior-case", "yes") == 1
    assert "Prior Report" in capsys.readouterr().out
    assert snapshot(run) == before and list(run.parent.iterdir()) == [run]


@pytest.mark.parametrize("defect", ["future", "self"])
def test_current_inventory_does_not_bypass_physical_identity_or_time(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], defect: str
) -> None:
    from rbotlib.inventory import build

    run = ready(root, tmp_path, {"prior.html": doc()})
    changed = doc(run.name) if defect == "self" else doc(date="2099-01-01")
    (run.parent.parent / "prior.html").write_text(embed_json(changed))
    (run / "inventory.json").write_text(json.dumps(build(run.parent.parent, run)))
    refused(root, run, capsys, "current run" if defect == "self" else "future generated_at")


def test_confirmed_existing_issuer_accepts_only_its_own_offered_report(
    root: Path, tmp_path: Path
) -> None:
    run = ready(
        root, tmp_path, {"own.html": doc(), "foreign.html": doc("other", "2026-10-16", "OTHER")}
    )
    assert _state(run)["issuer_id"] is None
    rebuild(root, run, "--set", "issuer_id=ACME")
    assert _approve(root, run, "--prior-case", "yes") == 0
    target = run.parent / TARGET
    assert _state(target)["issuer_id"] == "ACME"
    assert _state(target)["prior_case"]["report"] == "own.html"


def test_updated_inventory_after_prepare_cannot_replace_approved_payload(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib.inventory import build

    run = ready(root, tmp_path, {"prior.html": doc()})
    expected = {}
    original = ap._staged

    @contextmanager
    def stages(path: Path, contents: list[str]) -> Iterator[list[Path]]:
        with original(path, contents) as files:
            changed = doc()
            changed["limitations"]["approval"] = ["replaced with identical metadata"]
            (path.parent.parent / "prior.html").write_text(embed_json(changed))
            (path / "inventory.json").write_text(json.dumps(build(path.parent.parent, path)))
            expected.update(snapshot(path))
            yield files

    monkeypatch.setattr(ap, "_staged", stages)
    capsys.readouterr()
    assert _approve(root, run, "--prior-case", "yes") == 1
    assert "sources changed during Approval" in capsys.readouterr().out
    assert snapshot(run) == expected and list(run.parent.iterdir()) == [run]


def test_actual_catalog_approval_uses_explicit_report_date_and_pending_lineage(
    tmp_path: Path,
) -> None:
    from rbotlib.rules import RBOT_ROOT

    earlier = doc("old", "2026-10-14")
    newer = doc("new", "2026-10-12")
    newer["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][2] = "2026-10-16"
    run = ready(RBOT_ROOT, tmp_path, {"old.html": earlier, "new.html": newer})
    cp0 = (run / "handoffs/CP-0.md").read_bytes()
    assert _approve(RBOT_ROOT, run, "--prior-case", "yes") == 0
    target = run.parent / TARGET
    assert _state(target)["prior_case"] == {"offered": True, "accepted": True, "report": "new.html"}
    assert _state(target)["cp0_lineage"]["pending_run_id"] == run.name
    assert (target / "handoffs/CP-0.md").read_bytes() == cp0


@pytest.mark.parametrize("suffix", ["", "-2", "-3"])
@pytest.mark.parametrize("choice", ["yes", "no"])
@pytest.mark.parametrize("position", ["selected", "older", "foreign", "foreign-only"])
def test_approved_target_identity_refuses_every_original_before_publication(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    suffix: str,
    choice: str,
    position: str,
) -> None:
    from rbotlib.rules import RBOT_ROOT

    target = TARGET + suffix
    reports = {
        "collision.html": doc(target, issuer="OTHER" if position.startswith("foreign") else "ACME")
    }
    if position in ("older", "foreign"):
        reports["newer.html"] = doc("newer", "2026-10-15")
    run = ready(RBOT_ROOT, tmp_path, reports)
    for occupied in [TARGET, TARGET + "-2"] if suffix == "-3" else [TARGET] if suffix else []:
        (run.parent / occupied).mkdir()
    assert ap.new_name(run, "ACME", "FULL_CREDIT_ASSESSMENT").name == target
    before = snapshot(run)
    sources = {p: p.read_bytes() for p in run.parent.parent.glob("*.html")}
    folders = set(run.parent.iterdir())
    capsys.readouterr()
    assert _approve(RBOT_ROOT, run, "--prior-case", choice) == 1
    assert "approved run" in capsys.readouterr().out
    assert snapshot(run) == before and set(run.parent.iterdir()) == folders
    assert not (run.parent / target).exists() and not list(run.glob(".approve-*"))
    assert all(p.read_bytes() == raw for p, raw in sources.items())


@pytest.mark.parametrize("choice", ["yes", "no"])
def test_occupied_stem_is_not_the_computed_approved_identity(
    root: Path, tmp_path: Path, choice: str
) -> None:
    from rbotlib.prior_candidates import qualify_candidates

    run = ready(root, tmp_path, {"prior.html": doc(TARGET)})
    (run.parent / TARGET).mkdir()
    assert _approve(root, run, "--prior-case", choice) == 0
    target = run.parent / (TARGET + "-2")
    assert _state(target)["prior_case"]["accepted"] == (choice == "yes")
    assert qualify_candidates(target, target.parent.parent, "ACME", target.name)[0].metadata


@pytest.mark.parametrize("case", [(c, r) for c in ("yes", "no") for r in ("identity", "payload")])
def test_declined_and_accepted_originals_are_rechecked_before_first_publication(
    root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    case: tuple[str, str],
) -> None:
    from rbotlib.inventory import build

    choice, replacement = case
    run = ready(root, tmp_path, {"prior.html": doc()})
    expected = {}
    original = ap._staged

    @contextmanager
    def stages(path: Path, contents: list[str]) -> Iterator[list[Path]]:
        with original(path, contents) as files:
            changed = doc(TARGET) if replacement == "identity" else doc()
            changed["limitations"]["approval"] = ["replaced after preparation"]
            (path.parent.parent / "prior.html").write_text(embed_json(changed))
            (path / "inventory.json").write_text(json.dumps(build(path.parent.parent, path)))
            expected.update(snapshot(path))
            yield files

    monkeypatch.setattr(ap, "_staged", stages)
    capsys.readouterr()
    assert _approve(root, run, "--prior-case", choice) == 1
    assert ("approved run" if replacement == "identity" else "sources changed during Approval") in (
        capsys.readouterr().out
    )
    assert snapshot(run) == expected and list(run.parent.iterdir()) == [run]
    assert not list(run.glob(".approve-*"))
