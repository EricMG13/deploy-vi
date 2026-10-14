"""The `rbot-run/1` document: one finished, owned run read into the Report's embedded JSON.

`build` reads `run-state.json` through the state engine, every Handoff the state lists as
accepted or blocked (bytes re-hashed against the step), `validate/<ID>.json`, `run-brief.md`,
`model.json`, `fit/*.json`, `grading.json` and the module contracts. Charts and Front Page
blocks are filled by later steps. Every refusal is a `ReportError` naming the file.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from rbotlib import state
from rbotlib.catalog import load_catalog
from rbotlib.contract import ContractError, load_contract
from rbotlib.handoff import Handoff, HandoffError, parse, unfenced
from rbotlib.inventory import RunError
from rbotlib.report import ReportError
from rbotlib.rules import load_rules

Record = dict[str, Any]
PUBLIC_STEP = (
    "kind",
    "status",
    "qa_status",
    "handoff",
    "sha256",
    "validate_exit",
    "attempts",
    "started_at",
    "finished_at",
    "reason",
    "model",
    "note",
)
UNANCHORED = ("citation_unanchored", "source_unknown")


def public_step(step: Record) -> Record:
    """The twelve public fields of a step; evidence, base64 and history keys never leave."""
    return {k: step[k] for k in PUBLIC_STEP if k in step}


def anchored(validation: Record | None, cid: str, source: str = "") -> bool | None:
    """False when a finding names the citation, True when validated without one, else None."""
    if validation is None:
        return None
    for finding in validation.get("findings", []):
        if finding.get("code") not in UNANCHORED:
            continue
        message = str(finding.get("message", ""))
        if message.startswith(f"{cid}: ") or (source and message.startswith(f"{source!r} ")):
            return False
    return True


def _json(path: Path, label: str) -> Record:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReportError(f"{label}: missing") from exc
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ReportError(f"{label}: not readable JSON") from exc
    if not isinstance(data, dict):
        raise ReportError(f"{label}: expected a JSON object")
    return data


def _optional_json(path: Path, label: str) -> Record | None:
    return _json(path, label) if path.is_file() else None


def _sections(h: Handoff) -> dict[str, str]:
    """Each H2 section's raw body (fenced code kept verbatim), keyed by heading."""
    lines = h.body.splitlines()
    marks = unfenced(h.body).splitlines()
    heads = [(i, m[3:].strip()) for i, m in enumerate(marks) if m.startswith("## ")]
    found: dict[str, str] = {}
    for n, (start, name) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        found.setdefault(name, "\n".join(lines[start + 1 : end]).strip("\n"))
    return found


def _citations(h: Handoff, validation: Record | None) -> list[Record]:
    table = h.tables.get("citations")
    if table is None:
        return []
    index = {c.casefold(): i for i, c in enumerate(table.columns)}
    out: list[Record] = []
    for row in table.rows:
        cell = {k: row[i] if i < len(row) else "" for k, i in index.items()}
        cid, source = cell.get("id", ""), cell.get("source", "")
        out.append(
            {
                "id": cid,
                "source": source,
                "locator": cell.get("locator", ""),
                "excerpt": cell.get("excerpt", ""),
                "anchored": anchored(validation, cid, source),
            }
        )
    return out


def handoff_entry(run: Path, module: str, step: Record, validation: Record | None) -> Record:
    """One accepted or blocked Handoff, embedded whole so a later diff needs no run folder."""
    relative = f"handoffs/{module}.md"
    path = run / relative
    try:
        raw = path.read_bytes() if not path.is_symlink() else b""
    except OSError as exc:
        raise ReportError(f"{relative}: not readable") from exc
    if not raw or hashlib.sha256(raw).hexdigest() != step.get("sha256"):
        raise ReportError(f"{relative} changed since acceptance; run next to re-validate")
    try:
        h = parse(raw.decode("utf-8"))
    except (UnicodeDecodeError, HandoffError) as exc:
        raise ReportError(f"{relative}: not a readable Handoff") from exc
    sections = _sections(h)
    return {
        "sha256": step["sha256"],
        "qa_status": step.get("qa_status", h.front_matter.get("qa_status")),
        "status": step["status"],
        "front_matter": dict(h.front_matter),
        "analysis_md": sections.get("Analysis", ""),
        "gaps_md": sections.get("Gaps", ""),
        "tables": {k: {"columns": t.columns, "rows": t.rows} for k, t in h.tables.items()},
        "citations": _citations(h, validation),
    }


def _brief(run: Path) -> tuple[Record, Handoff]:
    try:
        h = parse((run / "run-brief.md").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, HandoffError) as exc:
        raise ReportError("run-brief.md: not a readable Run Brief") from exc
    tables = {k: {"columns": t.columns, "rows": t.rows} for k, t in h.tables.items()}
    return {"front_matter": dict(h.front_matter), "tables": tables}, h


def _model(run: Path, step: Record | None) -> Record | None:
    path = run / "model.json"
    if step is None or step["status"] not in ("accepted", "blocked"):
        return None
    if step["status"] == "blocked" and not path.is_file():
        return None
    data = _json(path, "model.json")
    if data.get("schema") != "rbot-model/1":
        raise ReportError("model.json: schema is not rbot-model/1")
    return data


def _fit(run: Path, step: Record | None, brief_h: Handoff) -> list[Record]:
    if step is None or step["status"] != "accepted":
        return []
    table = brief_h.tables.get("brief.portfolios")
    ids = [row[0] for row in table.rows] if table else []
    return [_json(run / f"fit/{pid}.json", f"fit/{pid}.json") for pid in ids]


def _modules(root: Path, plan: list[str]) -> Record:
    rules = load_rules(root)
    out: Record = {}
    for module in plan:
        path = root / "modules" / module / "contract.json"
        if not path.is_file():
            continue
        try:
            c = load_contract(path, rules)
        except ContractError as exc:
            raise ReportError(f"modules/{module}/contract.json: not a readable contract") from exc
        out[module] = {
            "title": c.title,
            "question": c.reader_question,
            "tables": [{"id": t.id, "title": t.title} for t in c.tables],
        }
    return out


def _grading_limited(run: Path, record: Record) -> list[str]:
    grading = _optional_json(run / "grading.json", "grading.json")
    for p in (grading or {}).get("pathways", []):
        if p.get("id") == record["pathway"]:
            depth = p.get("depths", {}).get(record["depth"], {})
            return [str(m) for m in depth.get("limited_modules", [])]
    return []


def limitations(
    record: Record,
    brief: Record,
    handoffs: Record,
    model: Record | None,
    limited_modules: list[str] | None = None,
) -> Record:
    """The three Limitations groups (spec 11.2 tab 8): shown at Approval, CP-5, unforeseen."""
    approval = [
        {"kind": "limitation", "text": t} for t in record["approval"]["limitations_shown"]
    ] + [{"kind": "limited_module", "module": m} for m in limited_modules or []]
    cp5: list[Record] = []
    table = handoffs.get("CP-5", {}).get("tables", {}).get("cp5.limitations")
    if table:
        cp5 = [dict(zip(table["columns"], row, strict=False)) for row in table["rows"]]
    unforeseen: list[Record] = []
    for name, step in record["steps"].items():
        if step["status"] in ("failed", "skipped"):
            unforeseen.append(
                {"kind": step["status"], "step": name, "reason": step.get("reason", "")}
            )
        elif step["status"] == "blocked":
            unforeseen.append({"kind": "blocked", "step": name, "reason": step.get("reason", "")})
    for detail in (model or {}).get("limitation_details", []):
        unforeseen.append({"kind": "model", **detail})
    for name, entry in handoffs.items():
        for c in entry["citations"]:
            if c["anchored"] is False:
                unforeseen.append(
                    {
                        "kind": "unanchored_citation",
                        "ref": f"{name}:{c['id']}",
                        "source": c["source"],
                    }
                )
    return {"approval": approval, "cp5": cp5, "unforeseen": unforeseen}


def _owned(run: Path) -> Record:
    try:
        record = state.write_guard(run)
    except (OSError, ValueError, RecursionError) as exc:
        raise ReportError(f"run-state.json: {exc}") from exc
    if record is None:
        raise ReportError("run-state.json: missing; not a native run")
    return record


def _terminal(record: Record) -> None:
    if record["approval"] is None:
        raise ReportError("run-state.json: render requires Approval")
    open_steps = [n for n, s in record["steps"].items() if s["status"] in ("pending", "running")]
    if open_steps:
        raise ReportError(f"run-state.json: render requires every step terminal: {open_steps}")


def build(run: Path, root: Path, generated_at: str) -> Record:
    """The §11.3 document without `charts` and `front_page_blocks`."""
    try:
        run = state.run_path(run)
    except (OSError, RunError) as exc:
        raise ReportError(f"{run}: {exc}") from exc
    record = _owned(run)
    _terminal(record)
    brief, brief_h = _brief(run)
    plan: list[str] = record["plan"]
    handoffs: Record = {}
    for name in plan:
        step = record["steps"][name]
        if step["status"] in ("accepted", "blocked"):
            validation = _optional_json(run / f"validate/{name}.json", f"validate/{name}.json")
            handoffs[name] = handoff_entry(run, name, step, validation)
    model = _model(run, record["steps"].get("MODEL"))
    fit = _fit(run, record["steps"].get("FIT"), brief_h)
    pathway = load_catalog(root).pathway(record["pathway"])
    if pathway is None:
        raise ReportError(f"run-state.json: unknown pathway {record['pathway']!r}")
    return {
        "schema": "rbot-run/1",
        "rbot_version": record["rbot_version"],
        "run_id": record["run_id"],
        "generated_at": generated_at,
        "run_brief": brief,
        "pathway": record["pathway"],
        "depth": record["depth"],
        "primary": record["primary"],
        "front_page": pathway.front_page,
        "plan": list(plan),
        "steps": {n: public_step(s) for n, s in record["steps"].items()},
        "handoffs": handoffs,
        "model": model,
        "fit": fit,
        "modules": _modules(root, plan),
        "limitations": limitations(record, brief, handoffs, model, _grading_limited(run, record)),
        "prior_case": {"report": None, "report_date": None, "diff": None},
    }
