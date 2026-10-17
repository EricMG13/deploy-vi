"""Pure, unexposed input-claim shape support; grants no qualification or read rights.

Accepts already parsed plain JSON data. Duplicate JSON keys discarded by a caller
cannot be detected here. Paths/proofs are inert lexical claims, never opened.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, cast

from rbotlib.brief_schema import COLUMNS, FIELDS, TRANCHE
from rbotlib.contract import Contract
from rbotlib.rules import Rules

SCHEMA = "rbot-isolation-input-shape/3"
TABLES = {
    "transaction_summary": "snapshot.transaction_summary",
    **{name: f"brief.{name}" for name in ("portfolios", "research_questions", "prior_case")},
}


class ManifestError(ValueError):
    """An input claim violates the bounded shape or supplied contract."""


@dataclass(frozen=True)
class ShapeValidatedManifest:
    canonical_json: str
    input_shape_json: str
    binding_sha256: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def _bounded(value: object, depth: int = 0, budget: list[int] | None = None) -> None:
    if budget is None:
        budget = [4096, 262144]
    budget[0] -= 1
    _require(budget[0] >= 0, "manifest node budget exceeded")
    _require(depth <= 8, "manifest nesting exceeds 8")
    if type(value) is dict:
        _require(len(value) <= 128, "object exceeds 128 fields")
        for key, item in value.items():
            _text(key)
            _bounded(key, depth + 1, budget)
            _bounded(item, depth + 1, budget)
    elif type(value) is list:
        _require(len(value) <= 256, "list exceeds 256 items")
        for item in value:
            _bounded(item, depth + 1, budget)
    elif value is not None:
        text = _cell(value)
        budget[1] -= len(text.encode("utf-8"))
        _require(budget[1] >= 0, "manifest text budget exceeded")


def _text(value: object) -> str:
    _require(type(value) is str and 0 < len(value) <= 4096, "expected bounded nonempty text")
    value = cast(str, value)
    _require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), "surrogate text")
    return value


def _object(value: object, fields: set[str]) -> dict[str, Any]:
    _require(
        type(value) is dict and set(value) == fields, f"expected exact fields {sorted(fields)}"
    )
    return cast(dict[str, Any], value)


def _id(value: object) -> str:
    text = _text(value)
    _require(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}", text) is not None, "invalid identity"
    )
    _require(text not in {".", ".."}, "invalid identity")
    return text


def _sha(value: object) -> str:
    text = _text(value)
    _require(re.fullmatch(r"[0-9a-f]{64}", text) is not None, "invalid SHA256")
    return text


def _date(value: object) -> None:
    text = _text(value)
    _require(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text) is not None, "invalid ISO date")
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ManifestError("invalid ISO date") from exc


def _path(value: object, *, absolute: bool = False) -> None:
    text = _text(value)
    _require(len(text) <= 1024 and text.startswith("/") == absolute, "invalid path scope")
    parts = text[1:].split("/") if absolute else text.split("/")
    _require(all(p not in {"", ".", ".."} for p in parts), "noncanonical path")
    _require(not any(ord(c) < 32 or ord(c) == 127 or c in "\\:" for c in text), "unsafe path text")


def _reference(value: object, *, absolute: bool = False) -> None:
    ref = _object(value, {"path", "sha256"})
    _path(ref["path"], absolute=absolute)
    _sha(ref["sha256"])


def _canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )


def _hash(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _groups(contract: Contract, rules: Rules) -> list[dict[str, Any]]:
    _id(contract.module_id)
    _require(len(contract.inputs) <= 128, "too many contract groups")
    groups = [asdict(item) for item in contract.inputs]
    for item in contract.inputs:
        _require(item.kind in {"handoff", "sources", "run_brief"}, "unknown contract input kind")
        _require(type(item.required) is bool, "invalid contract requiredness")
        _require(
            bool(item.values) and len(set(item.values)) == len(item.values), "invalid group values"
        )
        for name in item.values:
            _id(name)
        if item.kind == "handoff":
            _require(len(item.values) == 1, "handoff must name one producer")
        if item.kind == "sources":
            _require(set(item.values) <= set(rules.source_classes), "unknown source class")
        else:
            _require(not item.document_types, "document types on non-source group")
        _require(
            len(set(item.document_types)) == len(item.document_types)
            and set(item.document_types) <= set(rules.scales["document_type"]),
            "invalid document types",
        )
    return groups


def _pack(value: object) -> dict[str, Any]:
    pack = _object(value, {"id", "sources"})
    _id(pack["id"])
    _require(type(pack["sources"]) is list, "sources must be list")
    for item in pack["sources"]:
        _reference(item)
    paths = [item["path"] for item in pack["sources"]]
    _require(len(set(paths)) == len(paths), "duplicate source path")
    return {"id": pack["id"], "sources": sorted(pack["sources"], key=lambda item: item["path"])}


def _context(value: object, pack: dict[str, Any]) -> dict[str, Any]:
    context = _object(
        value,
        {
            "run_id",
            "issuer_id",
            "analysis_date",
            "provenance",
            "root",
            "context_sha256",
            "pack_sha256",
        },
    )
    _id(context["run_id"])
    if context["issuer_id"] is not None:
        _id(context["issuer_id"])
    if context["analysis_date"] is not None:
        _date(context["analysis_date"])
    _require(_text(context["provenance"]) in {"source", "fixture"}, "explicit provenance required")
    _reference(context["root"], absolute=True)
    _sha(context["context_sha256"])
    _require(context["pack_sha256"] == _hash(pack), "declared pack digest mismatch")
    return context


def _cp0_lineage(claim: dict[str, Any], context: dict[str, Any]) -> None:
    """Bind a native CP-0 lineage declaration, without reading/qualifying its state.

    Native lineage.sha256 names the selected Approval origin, not necessarily
    today's bytes. A different current hash requires the same state proof that
    declares the checked edit projection. B must verify both against native state.
    """
    original, proofs = claim["original"], claim["proofs"]
    lineage = claim["cp0_lineage"]
    if lineage is None:
        _require(original["run_id"] == context["run_id"], "original run_id mismatch")
        return
    lineage = _object(lineage, {"pending_run_id", "issuer_id", "sha256", "current_sha256", "proof"})
    _require(claim["producer"] == "CP-0", "lineage requires CP-0 producer")
    pending = _id(lineage["pending_run_id"])
    _require(
        re.fullmatch(r"[0-9]{8}-.+-pending(?:-[0-9]+)?", pending) is not None
        and pending != context["run_id"]
        and pending == original["run_id"],
        "CP-0 pending identity mismatch",
    )
    _require(lineage["issuer_id"] == original["issuer_id"], "CP-0 lineage issuer mismatch")
    _sha(lineage["sha256"])
    _sha(lineage["current_sha256"])
    _require(lineage["current_sha256"] == original["sha256"], "CP-0 current digest mismatch")
    _reference(lineage["proof"])
    _require(
        original["path"] == "handoffs/CP-0.md"
        and lineage["proof"]["path"] == "run-state.json"
        and lineage["proof"] == proofs["run"],
        "CP-0 lineage requires matching native state proof",
    )
    _require(
        lineage["sha256"] == lineage["current_sha256"] or proofs["current"] == lineage["proof"],
        "CP-0 edited bytes require matching current state proof",
    )


def _claim(value: object, context: dict[str, Any], rules: Rules) -> dict[str, Any]:
    claim = _object(
        value, {"producer", "availability", "limitation", "original", "proofs", "cp0_lineage"}
    )
    _id(claim["producer"])
    _require(_text(claim["availability"]) in {"present", "missing"}, "invalid availability")
    if claim["limitation"] is not None:
        _text(claim["limitation"])
    proofs = _object(claim["proofs"], {"run", "current", "host", "receipt"})
    for ref in proofs.values():
        if ref is not None:
            _reference(ref)
    if claim["availability"] == "missing":
        _require(
            claim["original"] is None
            and claim["cp0_lineage"] is None
            and claim["limitation"] is not None
            and all(ref is None for ref in proofs.values()),
            "missing claim requires limitation and no original/proofs",
        )
        return claim
    original = _object(
        claim["original"],
        {
            "producer",
            "run_id",
            "issuer_id",
            "analysis_date",
            "path",
            "sha256",
            "qa_status",
            "provenance",
        },
    )
    _require(original["producer"] == claim["producer"], "producer mismatch")
    for key in ("issuer_id", "analysis_date", "provenance"):
        _require(original[key] == context[key], f"original {key} mismatch")
    _id(original["run_id"])
    _id(original["issuer_id"])
    _date(original["analysis_date"])
    _path(original["path"])
    _sha(original["sha256"])
    _require(_text(original["qa_status"]) in rules.qa_status, "invalid QA claim")
    _cp0_lineage(claim, context)
    return claim


def _cell(value: object) -> str:
    # Native empty analyst/cite cells are meaningful; identities/basis stay nonempty.
    if type(value) is str and value == "":
        return value
    return _text(value)


def _table(value: object, table_id: str) -> list[list[str]]:
    table = _object(value, {"table_id", "columns", "rows"})
    _require(table["table_id"] == table_id, "wrong native table")
    _require(table["columns"] == list(COLUMNS[table_id]), "wrong native columns")
    _require(type(table["rows"]) is list, "rows must be list")
    for row in table["rows"]:
        _require(type(row) is list and len(row) == len(COLUMNS[table_id]), "ragged native row")
        for cell in row:
            _cell(cell)
    return cast(list[list[str]], table["rows"])


def _entry(row: list[str], rules: Rules) -> None:
    _, value, status, _, cite = row
    _require(status in rules.scales["brief_status"], "invalid brief status")
    _require((status == "Gap") == (value == rules.gap_marker), "gap/value mismatch")
    _text(value)
    tokens = [] if cite in {"", rules.gap_marker} else cite.split()
    _require(
        all(re.fullmatch(r"\[C[1-9][0-9]{0,8}\]", token) for token in tokens), "invalid citation"
    )
    if status == "Sourced":
        _require(bool(tokens), "sourced value requires citations")


def _scales(row: list[str], table_id: str, rules: Rules) -> None:
    cells = dict(zip(COLUMNS[table_id], row, strict=True))
    scales = {
        "strategy": "strategy",
        "approved": "yes_no",
        "accepted": "yes_no",
        "status": "brief_status",
        "debt_type": "debt_type",
        "use_of_proceeds": "use_of_proceeds",
        "talk_stage": "price_talk_stage",
        "unit": "unit",
    }
    for field, scale in scales.items():
        if field in cells and (
            field in {"strategy", "approved", "accepted", "status"}
            or cells[field] != rules.gap_marker
        ):
            _require(cells[field] in rules.scales[scale], "invalid native enum")
    for field in ("as_of_date", "report_date", "maturity_date", "commitment_date"):
        if field in cells and cells[field] not in {"", rules.gap_marker}:
            _date(cells[field])


def _transaction(tables: list[object], rules: Rules) -> None:
    rows = _table(tables[0], TABLES["transaction_summary"])
    companions = _table(tables[1], "brief.run_brief_fields")
    ids = [row[0] for row in rows]
    _require(len(set(ids)) == len(ids), "duplicate tranche identity")
    _require(all(re.fullmatch(r"NEW-[1-9][0-9]*", t) for t in ids), "invalid tranche identity")
    expected = {f"{t}.{field}" for t in ids for field in TRANCHE}
    _require(
        len(companions) == len(expected) and {row[0] for row in companions} == expected,
        "companion identity mismatch",
    )
    values = {row[0]: row[1] for row in companions}
    for row in companions:
        _entry(row, rules)
    for row in rows:
        _scales(row, TABLES["transaction_summary"], rules)
        _require(
            all(row[i + 1] == values[f"{row[0]}.{field}"] for i, field in enumerate(TRANCHE)),
            "companion value mismatch",
        )


def _scalar(name: str, table: object, rules: Rules) -> None:
    rows = _table(table, "brief.run_brief_fields")
    _require(len(rows) == 1 and rows[0][0] == name, "scalar identity mismatch")
    _entry(rows[0], rules)
    if name == "primary" and rows[0][2] != "Gap":
        _require(rows[0][1] in rules.scales["yes_no"], "invalid native enum")


def _brief(value: object, fields: set[str], rules: Rules) -> dict[str, Any]:
    _require(fields <= set(FIELDS) | set(TABLES), "unsupported brief permission")
    brief = _object(value, fields)
    for name, raw in brief.items():
        _require(type(raw) is dict, "brief claim must be object")
        kind = raw.get("kind")
        if kind == "missing":
            _text(_object(raw, {"kind", "limitation"})["limitation"])
            continue
        claim = _object(raw, {"kind", "basis", "tables"})
        _require(kind == ("scalar" if name in FIELDS else "table"), "wrong brief kind")
        _text(claim["basis"])
        tables = claim["tables"]
        _require(
            type(tables) is list and len(tables) == (2 if name == "transaction_summary" else 1),
            "wrong brief table count",
        )
        if name == "transaction_summary":
            _transaction(tables, rules)
        elif name in FIELDS:
            _scalar(name, tables[0], rules)
        else:
            for row in _table(tables[0], TABLES[name]):
                _scales(row, TABLES[name], rules)
    return brief


def _brief_identity(brief: dict[str, Any], context: dict[str, Any]) -> None:
    for field, key in (("issuer_id", "issuer_id"), ("as_of_date", "analysis_date")):
        if field in brief and brief[field]["kind"] == "scalar":
            row = brief[field]["tables"][0]["rows"][0]
            if row[2] != "Gap":
                _require(row[1] == context[key], "brief identity mismatch")


def validate(data: object, contract: Contract, rules: Rules) -> ShapeValidatedManifest:
    """Bind declared claims and exact input groups, without qualifying any claim.

    Missing required inputs are representable only with explicit limitations;
    readiness and proof checks belong to later qualification. Null binding requests
    computation; a supplied binding must match. Results contain immutable JSON.
    """
    _bounded(data)
    manifest = _object(
        data,
        {
            "schema",
            "target",
            "issuer_id",
            "analysis_date",
            "pack",
            "source_context",
            "inputs",
            "brief",
            "binding_sha256",
        },
    )
    _require(
        manifest["schema"] == SCHEMA and manifest["target"] == contract.module_id,
        "schema/target mismatch",
    )
    groups = _groups(contract, rules)
    pack = _pack(manifest["pack"])
    context = _context(manifest["source_context"], pack)
    for key in ("issuer_id", "analysis_date"):
        _require(manifest[key] == context[key], f"target/source {key} mismatch")
    _require(type(manifest["inputs"]) is list, "inputs must be list")
    claims = [_claim(item, context, rules) for item in manifest["inputs"]]
    producers = [item["producer"] for item in claims]
    declared = contract.handoff_inputs()
    _require(len(set(declared)) == len(declared), "duplicate contract producer")
    _require(
        len(set(producers)) == len(producers) and set(producers) == set(declared),
        "producer set mismatch",
    )
    fields = {name for item in contract.inputs if item.kind == "run_brief" for name in item.values}
    brief = _brief(manifest["brief"], fields, rules)
    _brief_identity(brief, context)
    normalized = dict(manifest, pack=pack, inputs=sorted(claims, key=lambda item: item["producer"]))
    normalized.pop("binding_sha256")
    rules_data = asdict(rules)
    rules_data["placeholders"] = sorted(rules.placeholders)
    schemas = {
        name: COLUMNS["brief.run_brief_fields" if name in FIELDS else TABLES[name]]
        for name in fields
    }
    if "transaction_summary" in fields:
        schemas["transaction_companions"] = COLUMNS["brief.run_brief_fields"]
    binding = _hash(
        {
            "manifest": normalized,
            "contract": asdict(contract),
            "rules": rules_data,
            "brief_schemas": schemas,
            "tranche_fields": TRANCHE if "transaction_summary" in fields else (),
        }
    )
    supplied = manifest["binding_sha256"]
    if supplied is not None:
        _require(_sha(supplied) == binding, "manifest binding mismatch")
    normalized["binding_sha256"] = binding
    shape = {"groups": groups, "handoff_claims": normalized["inputs"], "brief_claims": brief}
    return ShapeValidatedManifest(_canonical(normalized), _canonical(shape), binding)
