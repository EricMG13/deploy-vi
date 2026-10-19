"""Prior discovery never substitutes prepared text or grants unregistered paths."""

import copy
import hashlib
import itertools
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from test_prior_report import document, table

from rbotlib.inventory import RunError, build
from rbotlib.prior_candidates import (
    PriorCandidate,
    qualify_candidate,
    qualify_candidates,
    select_newest,
)
from rbotlib.prior_report import parse_report
from rbotlib.report.html_parts import embed_json
from rbotlib.report.markdown import render_markdown

NOW = datetime(2026, 10, 18, tzinfo=UTC)


def setup(tmp_path: Path) -> tuple[Path, Path]:
    pack = tmp_path.resolve() / "pack"
    run = pack / "rbot-runs" / "current"
    run.mkdir(parents=True)
    return pack, run


def source(pack: Path, name: str, doc: dict[str, Any] | None = None) -> Path:
    doc = document() if doc is None else doc
    path = pack / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_markdown(doc, [], []) if path.suffix == ".md" else embed_json(doc)
    path.write_text(text, encoding="utf-8")
    return path


def inventory(pack: Path, run: Path) -> dict[str, Any]:
    data = build(pack, run)
    (run / "inventory.json").write_text(json.dumps(data), encoding="utf-8")
    return data


def qualify(pack: Path, run: Path) -> tuple[PriorCandidate, ...]:
    return qualify_candidates(run, pack, "TEST", "current", now=NOW)


@pytest.mark.parametrize("kind", ["html", "md"])
def test_original_emitters_metadata_rows_and_sources(tmp_path: Path, kind: str) -> None:
    pack, run = setup(tmp_path)
    doc = document()
    doc.pop("fetched")
    table(doc, "model.house", ["item", "value"], [["debt", "—"]])
    path = source(pack, "misleading-2099." + kind, doc)
    inventory(pack, run)
    prepared = run / "prepared"
    prepared.mkdir()
    (prepared / "fake.txt").write_text("fake metadata")
    before = {p: p.read_bytes() for p in pack.rglob("*") if p.is_file()}
    (candidate,) = qualify(pack, run)
    assert candidate.source == path.name and candidate.source_path == path
    assert candidate.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert candidate.payload == parse_report(path.read_text(), kind)
    assert candidate.metadata == {
        "run_id": "earlier",
        "issuer_id": "TEST",
        "report_date": "2026-10-14",
        "date_basis": "generated_at",
        "pathway": "FULL_CREDIT_ASSESSMENT",
        "depth": "full",
    }
    assert candidate.offered and candidate.issue is None
    assert candidate.tables["model.house"]["rows"] == [["debt", "—"]]
    assert "older Report omits fetched" in candidate.limitations
    assert before == {p: p.read_bytes() for p in pack.rglob("*") if p.is_file()}
    assert qualify_candidate(run, pack, path.name, ("TEST", "current"), now=NOW) == candidate


def test_foreign_is_truthful_no_and_explicit_header_date(tmp_path: Path) -> None:
    pack, run = setup(tmp_path)
    doc = document()
    doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][2] = "2026-10-16"
    source(pack, "prior.html", doc)
    inventory(pack, run)
    (candidate,) = qualify_candidates(run, pack, "FOREIGN", "current", now=NOW)
    assert not candidate.offered and candidate.payload == doc
    assert candidate.metadata is not None and candidate.metadata["report_date"] == "2026-10-16"
    assert candidate.metadata["date_basis"] == "report_date"
    assert select_newest((candidate,), accepted=True) is None


@pytest.mark.parametrize("defect", ["self", "future"])
def test_own_run_and_future_timestamp_refuse(tmp_path: Path, defect: str) -> None:
    pack, run = setup(tmp_path)
    doc = document()
    if defect == "future":
        doc["generated_at"] = "2026-10-18T02:00:00+01:00"
    source(pack, "prior.html", doc)
    inventory(pack, run)
    with pytest.raises(RunError, match=r"current run|future generated_at"):
        qualify_candidates(run, pack, "TEST", "earlier" if defect == "self" else "current", now=NOW)


def test_timezone_comparison_and_no_analysis_date_gate(tmp_path: Path) -> None:
    pack, run = setup(tmp_path)
    doc = document()
    doc["generated_at"] = "2026-10-18T00:30:00+01:00"
    doc["run_brief"]["front_matter"]["as_of_date"] = "2020-01-01"
    source(pack, "prior.html", doc)
    inventory(pack, run)
    metadata = qualify(pack, run)[0].metadata
    assert metadata is not None and metadata["report_date"] == "2026-10-18"
    with pytest.raises(RunError, match="timezone"):
        qualify_candidates(run, pack, "TEST", "current", now=datetime(2026, 10, 18))


@pytest.mark.parametrize(
    "raw",
    [
        b'<script id="rbot-run">{broken</script>',
        b"```json rbot-run\n{",
        b"```json rbot-run\n\xff\n```",
    ],
)
def test_malformed_marker_has_named_issue_without_invented_metadata(
    tmp_path: Path, raw: bytes
) -> None:
    pack, run = setup(tmp_path)
    path = pack / ("bad.html" if raw.startswith(b"<") else "bad.md")
    path.write_bytes(raw)
    inventory(pack, run)
    (candidate,) = qualify(pack, run)
    assert candidate.issue and path.name in candidate.issue
    assert candidate.metadata is None and candidate.payload is None and not candidate.offered
    assert select_newest((candidate,), accepted=True) is None


def test_newest_and_equivalent_html_preference_are_permutation_invariant(tmp_path: Path) -> None:
    pack, run = setup(tmp_path)
    doc = document()
    md = source(pack, "new.md", doc)
    source(pack, "new.html", parse_report(md.read_text(), "md"))
    old = copy.deepcopy(doc)
    old["generated_at"] = "2026-10-13T00:00:00+00:00"
    old["run_id"] = old["run_brief"]["front_matter"]["run_id"] = "older"
    old["handoffs"]["MODEL"]["front_matter"]["run_id"] = "older"
    old["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][0] = "older"
    source(pack, "old.html", old)
    inventory(pack, run)
    for ordering in itertools.permutations(qualify(pack, run)):
        chosen = select_newest(ordering, accepted=True)
        assert chosen is not None and chosen.source == "new.html"
        assert select_newest(ordering, accepted=False) is None
    assert select_newest((), accepted=True) is None


@pytest.mark.parametrize("defect", ["same-run", "tied-date", "old-conflict"])
def test_ambiguous_payloads_refuse_in_every_order(tmp_path: Path, defect: str) -> None:
    pack, run = setup(tmp_path)
    doc = document()
    source(pack, "a.html", doc)
    other = copy.deepcopy(doc)
    other["limitations"]["approval"] = ["different payload"]
    if defect == "tied-date":
        other["run_id"] = other["run_brief"]["front_matter"]["run_id"] = "different"
        other["handoffs"]["MODEL"]["front_matter"]["run_id"] = "different"
        other["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][0] = "different"
    source(pack, "b.html", other)
    if defect == "old-conflict":
        newest = copy.deepcopy(doc)
        newest["generated_at"] = "2026-10-17T00:00:00+00:00"
        newest["run_id"] = newest["run_brief"]["front_matter"]["run_id"] = "newest"
        newest["handoffs"]["MODEL"]["front_matter"]["run_id"] = "newest"
        newest["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][0] = "newest"
        source(pack, "c.html", newest)
    inventory(pack, run)
    for ordering in itertools.permutations(qualify(pack, run)):
        with pytest.raises(RunError, match=r"conflicting.*run|tied.*date"):
            select_newest(ordering, accepted=True)
        assert select_newest(ordering, accepted=False) is None


@pytest.mark.parametrize(
    "defect", ["bytes", "hash", "symlink", "parent-link", "hardlink", "unknown"]
)
def test_protected_source_failures_are_not_parse_omissions(tmp_path: Path, defect: str) -> None:
    pack, run = setup(tmp_path)
    path = source(pack, "sub/prior.html")
    data = inventory(pack, run)
    if defect == "bytes":
        path.write_text("replacement")
    elif defect == "hash":
        data["files"][0]["sha256"] = "0" * 64
        (run / "inventory.json").write_text(json.dumps(data))
    elif defect in ("symlink", "hardlink"):
        moved = tmp_path / "moved.html"
        path.rename(moved)
        path.symlink_to(moved) if defect == "symlink" else os.link(moved, path)
    elif defect == "parent-link":
        moved = tmp_path / "moved"
        path.parent.rename(moved)
        path.parent.symlink_to(moved, target_is_directory=True)
    with pytest.raises(RunError, match=r"sha256|symlink|single-link|hard link|registered"):
        qualify_candidate(
            run,
            pack,
            "unknown.html" if defect == "unknown" else "sub/prior.html",
            ("TEST", "current"),
            now=NOW,
        )


@pytest.mark.parametrize(
    "name", ["../secret.html", "/tmp/secret.html", "C:\\secret.html", "sub/../prior.html"]
)
def test_bad_inventory_paths_refuse_before_any_source_read(
    tmp_path: Path, name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack, run = setup(tmp_path)
    source(pack, "prior.html")
    data = inventory(pack, run)
    data["files"][0]["path"] = name
    (run / "inventory.json").write_text(json.dumps(data))
    from rbotlib.isolation_capture import Capture

    original = Capture.read
    opened = []

    def observe(self: Capture, path: Path) -> bytes:
        opened.append(path)
        return original(self, path)

    monkeypatch.setattr(Capture, "read", observe)
    with pytest.raises(RunError, match="relative path"):
        qualify(pack, run)
    assert opened == [run / "inventory.json"]


@pytest.mark.parametrize(
    "defect", ["schema", "root", "duplicate", "kind", "flag", "size", "digest", "state-root"]
)
def test_malformed_inventory_and_pack_binding_refuse(tmp_path: Path, defect: str) -> None:
    pack, run = setup(tmp_path)
    source(pack, "prior.html")
    data = inventory(pack, run)
    if defect in ("schema", "root"):
        data["schema" if defect == "schema" else "pack_root"] = "wrong"
    elif defect == "duplicate":
        data["files"].append(data["files"][0])
    elif defect == "state-root":
        (run / "run-state.json").write_text(json.dumps({"pack_root": str(tmp_path)}))
    else:
        key, value = {
            "kind": ("kind", "txt"),
            "flag": ("rbot_report", "Yes"),
            "size": ("size", True),
            "digest": ("sha256", "bad"),
        }[defect]
        data["files"][0][key] = value
    (run / "inventory.json").write_text(json.dumps(data))
    with pytest.raises(RunError, match=r"inventory|pack_root"):
        qualify(pack, run)


def test_missing_source_refuses_as_qualification_error(tmp_path: Path) -> None:
    pack, run = setup(tmp_path)
    path = source(pack, "prior.html")
    inventory(pack, run)
    path.unlink()
    with pytest.raises(RunError, match=r"prior\.html"):
        qualify(pack, run)


def test_replacement_during_parse_refuses_before_return(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from rbotlib import prior_candidates

    pack, run = setup(tmp_path)
    path = source(pack, "prior.html")
    inventory(pack, run)
    original = parse_report

    def replace(text: str, kind: str) -> dict[str, Any]:
        result = original(text, kind)
        path.write_text("substituted during parse")
        return result

    monkeypatch.setattr(prior_candidates, "parse_report", replace)
    with pytest.raises(RunError, match="bytes changed"):
        qualify(pack, run)


@pytest.mark.parametrize(
    "source_name", ["../secret.html", "/tmp/secret.html", "C:\\secret.html", "prior.html/"]
)
def test_exact_lookup_refuses_noncanonical_or_unregistered_source(
    tmp_path: Path, source_name: str
) -> None:
    pack, run = setup(tmp_path)
    source(pack, "prior.html")
    inventory(pack, run)
    with pytest.raises(RunError, match="relative path"):
        qualify_candidate(run, pack, source_name, ("TEST", "current"), now=NOW)


@pytest.mark.parametrize("filename", ["inventory.json", "run-state.json"])
def test_metadata_link_refuses_before_parsing(tmp_path: Path, filename: str) -> None:
    pack, run = setup(tmp_path)
    source(pack, "prior.html")
    inventory(pack, run)
    path = run / filename
    path.unlink(missing_ok=True)
    path.symlink_to(tmp_path / "ungranted")
    with pytest.raises(RunError, match="symlink"):
        qualify(pack, run)


@pytest.mark.parametrize("raw", [b"{", b"\xff", b"[]", b'{"schema":1,"schema":2}'])
def test_invalid_inventory_json_refuses(tmp_path: Path, raw: bytes) -> None:
    pack, run = setup(tmp_path)
    source(pack, "prior.html")
    (run / "inventory.json").write_bytes(raw)
    with pytest.raises(RunError, match="inventory"):
        qualify(pack, run)
