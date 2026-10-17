"""Checked r14 qualification maps; no universal native register schema is imposed."""

from __future__ import annotations

import json
import re
from dataclasses import replace
from itertools import groupby
from pathlib import Path
from typing import Any

from rbotlib.handoff import Handoff, Table, _unfenced, cells, parse
from rbotlib.validate import Finding, run_findings


class ABError(ValueError):
    """A qualification input cannot be verified; the message names it."""


R14_SECTIONS = (
    "Audit Summary",
    "Analysis",
    "Evidence Trace",
    "Source Registry",
    "Gaps & Conflicts",
    "QA Validation",
)


def _section(h: Handoff, name: str) -> list[str]:
    lines, active = [], False
    for line in _unfenced(h.body.splitlines()):
        if line.startswith("## "):
            active = line[3:].strip() == name
        elif active:
            lines.append(line)
    return lines


def _table_records(group: list[str], section: str) -> list[dict[str, str]]:
    if len(group) < 2:
        raise ABError(f"{section}: an evidence table has no separator")
    headers, separator = cells(group[0]), cells(group[1])
    if len(set(headers)) != len(headers) or not all(headers):
        raise ABError(f"{section}: evidence columns must be unique and named")
    if len(separator) != len(headers) or not all(c and set(c) <= {"-", ":"} for c in separator):
        raise ABError(f"{section}: an evidence table has no readable separator")
    records = []
    for line in group[2:]:
        row = cells(line)
        if len(row) != len(headers):
            raise ABError(f"{section}: an evidence row has the wrong number of cells")
        records.append(dict(zip(headers, row, strict=True)))
    return records


def _records(lines: list[str], section: str) -> tuple[list[dict[str, str]], str]:
    records, prose = [], []
    for is_table, grouped in groupby(lines, key=lambda s: s.strip().startswith("|")):
        group = list(grouped)
        if is_table:
            records += _table_records(group, section)
        else:
            prose += [line for line in group if line.strip() and not line.startswith(("#", "<!--"))]
    return records, "\n".join(prose)


def _columns(mapping: dict[str, Any], name: str, keys: tuple[str, ...]) -> dict[str, str]:
    configured = mapping.get(name)
    if not isinstance(configured, dict) or not all(
        isinstance(configured.get(k), str) and configured[k].strip() for k in keys
    ):
        raise ABError(f"evidence map: {name} needs column names {keys}")
    return configured


def _value(record: dict[str, str], column: str, where: str) -> str:
    if column not in record or not record[column].strip():
        raise ABError(f"{where}: no nonempty column {column!r}")
    return record[column].strip()


def _registry(h: Handoff, configured: dict[str, str]) -> dict[str, tuple[str, str]]:
    records, _ = _records(_section(h, "Source Registry"), "Source Registry")
    sources = {}
    for record in records:
        sid = _value(record, configured["id"], "Source Registry")
        if sid in sources:
            raise ABError(f"Source Registry: duplicate source id {sid}")
        source = _value(record, configured["file"], f"Source Registry {sid}")
        sources[sid] = (source, " ".join(record.values()))
    if not sources:
        raise ABError("Source Registry: no verifiable source records")
    return sources


def _references(value: str, sources: dict[str, tuple[str, str]], eid: str) -> list[str]:
    if value in sources:
        return [value]
    refs = [r.strip().strip("[]").strip() for r in re.split(r"[,;]", value)]
    if not all(refs) or len(set(refs)) != len(refs):
        raise ABError(f"Evidence Trace {eid}: empty or duplicate source reference")
    unknown = [r for r in refs if r not in sources]
    if unknown:
        raise ABError(f"Evidence Trace {eid}: unknown source references {unknown}")
    return refs


def _extra_references(text: str, refs: list[str], sources: dict[str, tuple[str, str]]) -> bool:
    bracketed = re.findall(r"\[([^]\n]+)\]", text)
    known = [s for s in sources if re.search(rf"(?<![\w.-]){re.escape(s)}(?![\w.-])", text)]
    return any(s not in refs for s in [*bracketed, *known])


def _check_trace_headings(lines: list[str], sources: dict[str, tuple[str, str]]) -> None:
    headings = "\n".join(line for line in lines if line.startswith("#"))
    if _extra_references(headings, [], sources):
        raise ABError("Evidence Trace: source reference in a heading is unverifiable")


def _trace(
    h: Handoff, configured: dict[str, str], sources: dict[str, tuple[str, str]]
) -> dict[tuple[str, str], dict[str, str]]:
    lines = _section(h, "Evidence Trace")
    _check_trace_headings(lines, sources)
    records, prose = _records(lines, "Evidence Trace")
    if prose.strip():
        raise ABError("Evidence Trace: prose outside the configured records is unverifiable")
    found, seen = {}, set()
    for record in records:
        eid = _value(record, configured["id"], "Evidence Trace")
        if eid in seen:
            raise ABError(f"Evidence Trace: duplicate evidence id {eid}")
        seen.add(eid)
        refs = _references(
            _value(record, configured["sources"], f"Evidence Trace {eid}"), sources, eid
        )
        rest = " ".join(v for k, v in record.items() if k != configured["sources"])
        if _extra_references(rest, refs, sources):
            raise ABError(
                f"Evidence Trace {eid}: an extra source reference is outside "
                "the configured source column"
            )
        for sid in refs:
            found[eid, sid] = record
    if not found:
        raise ABError("Evidence Trace: no verifiable source references")
    return found


def _entry_key(entry: object, fields: tuple[str, ...]) -> tuple[str, str]:
    if not isinstance(entry, dict) or not all(
        isinstance(entry.get(k), str) and entry[k].strip() for k in fields
    ):
        raise ABError(f"evidence map: each entry needs nonempty {', '.join(fields)}")
    return entry["evidence_id"], entry["source_id"]


def _source_fields(
    mapping: dict[str, Any], traces: dict[tuple[str, str], dict[str, str]]
) -> dict[tuple[str, str], dict[str, str]]:
    entries = mapping.get("source_fields", [])
    if not isinstance(entries, list):
        raise ABError("evidence map: source_fields must be a list")
    selected = {}
    for entry in entries:
        key = _entry_key(entry, ("evidence_id", "source_id", "locator", "excerpt"))
        if key in selected or key not in traces:
            raise ABError(f"duplicate or unknown source field selector {key}")
        selected[key] = entry
    return selected


def _faithful_values(
    entry: dict[str, str], record: dict[str, str], columns: dict[str, str], key: tuple[str, str]
) -> tuple[str, str]:
    locator = _value(record, columns["locator"], f"Evidence Trace {key}")
    excerpt = _value(record, columns["excerpt"], f"Evidence Trace {key}")
    if entry["locator"].strip() != locator or entry["excerpt"].strip() != excerpt:
        raise ABError(
            f"evidence mapping {key}: locator or excerpt is not faithful to its native field"
        )
    return locator, excerpt


def _mapped_rows(
    mapping: dict[str, Any],
    traces: dict[tuple[str, str], dict[str, str]],
    sources: dict[str, tuple[str, str]],
) -> list[list[str]]:
    entries = mapping.get("citations")
    if not isinstance(entries, list):
        raise ABError("evidence map: citations must be a list")
    defaults = _columns(mapping, "evidence_trace", ("id", "sources", "locator", "excerpt"))
    selectors = _source_fields(mapping, traces)
    found = {}
    for entry in entries:
        key = _entry_key(entry, ("evidence_id", "source_id", "locator", "excerpt"))
        if key in found:
            raise ABError(f"duplicate evidence mapping {key}")
        if key not in traces:
            raise ABError(f"unknown evidence mapping {key}")
        locator, excerpt = _faithful_values(entry, traces[key], selectors.get(key, defaults), key)
        found[key] = [f"{key[0]}:{key[1]}", sources[key[1]][0], locator, excerpt]
    missing = [key for key in traces if key not in found]
    if missing:
        raise ABError(f"missing evidence mapping {missing}")
    return list(found.values())


def checked_findings(findings: list[Finding], run: Path) -> list[Finding]:
    """A global source-run failure cannot stand in for one unanchored citation."""
    failures = [f.message for f in findings if f.code == "run_error"]
    if failures:
        raise ABError(f"run_error: {run} is unverifiable: {'; '.join(failures)}")
    return findings


def measure_a(text: str, run: Path, evidence: Path) -> dict[str, Any]:
    """Measure every actual A Evidence Trace source reference using a checked internal map."""
    h = parse(text)
    if tuple(h.sections) != R14_SECTIONS:
        raise ABError(f"A: H2 sections must be the frozen r14 sections {R14_SECTIONS}")
    mapping = json.loads(evidence.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict):
        raise ABError("evidence map: not a JSON object")
    sources = _registry(h, _columns(mapping, "source_registry", ("id", "file")))
    traces = _trace(
        h, _columns(mapping, "evidence_trace", ("id", "sources", "locator", "excerpt")), sources
    )
    rows = _mapped_rows(mapping, traces, sources)
    # Projection of verified native evidence, not invented citation values. Use the shared
    # anchoring implementation, including its page/sign/currency behavior on the final base.
    anchored = replace(h, tables={"citations": Table(["id", "source", "locator", "excerpt"], rows)})
    findings = checked_findings(run_findings(anchored, run), run)
    return {
        "module": h.front_matter.get("module_id"),
        "side": "A",
        "C": f"{len(rows) - len(findings)}/{len(rows)}",
        "findings": sorted({f.code for f in findings}),
        "evidence_references": len(rows),
    }
