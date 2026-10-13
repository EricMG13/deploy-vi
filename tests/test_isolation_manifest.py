"""Shape tests use supplied installed contracts; no fixture becomes qualified."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from test_accept import send
from test_bootstrap import approve, pending, ready
from test_model_host import with_cp1

from rbotlib import accept, attempts, current, dispatch, host_evidence, origins, state
from rbotlib.contract import Contract, load_contract
from rbotlib.handoff import parse
from rbotlib.isolation_manifest import SCHEMA, ManifestError, validate
from rbotlib.rules import RBOT_ROOT, Rules, load_rules

TARGETS = tuple(sorted(p.parent.name for p in (RBOT_ROOT / "modules").glob("*/contract.json")))
SHA = "a" * 64


def descriptor_hash(value: object) -> str:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def example(contract: Contract, *, provenance: str = "source") -> dict[str, Any]:
    pack = {"id": "pack-original", "sources": [{"path": "documents/a.xlsx", "sha256": SHA}]}
    context: dict[str, Any] = {
        "run_id": "20261011-acme-original",
        "issuer_id": "ACME",
        "analysis_date": "2026-10-11",
        "provenance": provenance,
        "root": {"path": "/original runtime/root", "sha256": SHA},
        "context_sha256": SHA,
        "pack_sha256": descriptor_hash(pack),
    }
    claims = []
    for producer in contract.handoff_inputs():
        original = {
            key: context[key] for key in ("run_id", "issuer_id", "analysis_date", "provenance")
        }
        original.update(
            producer=producer, path=f"handoffs/{producer}.md", sha256=SHA, qa_status="Blocked"
        )
        claims.append(
            {
                "producer": producer,
                "availability": "present",
                "limitation": "Original gaps",
                "original": original,
                "proofs": dict.fromkeys(("run", "current", "host", "receipt")),
                "cp0_lineage": None,
            }
        )
    fields = {name for item in contract.inputs if item.kind == "run_brief" for name in item.values}
    brief = {
        name: {
            "value": "Original exact value\nwith units",
            "status": "Sourced",
            "basis": "Original source basis",
            "citations": ["[C12]"],
        }
        for name in fields
    }
    for field, key in (("issuer_id", "issuer_id"), ("as_of_date", "analysis_date")):
        if field in brief:
            brief[field]["value"] = context[key]
    return {
        "schema": SCHEMA,
        "target": contract.module_id,
        "issuer_id": "ACME",
        "analysis_date": "2026-10-11",
        "pack": pack,
        "source_context": context,
        "inputs": claims,
        "brief": brief,
        "binding_sha256": None,
    }


def installed(target: str = "CP-1") -> tuple[Contract, Rules]:
    rules = load_rules()
    return load_contract(RBOT_ROOT / "modules" / target / "contract.json", rules), rules


def native_bundle(run: Path) -> dict[str, Any]:
    record = state.read(run)
    contract, _ = installed("CP-1B")
    data = example(contract, provenance="fixture")
    rows = dispatch._prepared(run, record)
    data["pack"] = {
        "id": run.parent.parent.name,
        "sources": [{"path": row["path"], "sha256": row["sha256"]} for row in rows],
    }
    context = data["source_context"]
    context.update(
        run_id=record["run_id"],
        issuer_id=record["issuer_id"],
        analysis_date=record["as_of_date"],
        pack_sha256=descriptor_hash(data["pack"]),
        context_sha256=host_evidence.context(RBOT_ROOT, record),
    )
    context["root"] = {"path": str(RBOT_ROOT), "sha256": context["context_sha256"]}
    data.update(issuer_id=record["issuer_id"], analysis_date=record["as_of_date"])
    table = parse((run / "run-brief.md").read_text()).tables["brief.run_brief_fields"]
    row = next(dict(zip(table.columns, r, strict=True)) for r in table.rows if r[0] == "as_of_date")
    data["brief"]["as_of_date"] = dict(
        value=row["value"],
        status=row["status"],
        basis=json.dumps(row, sort_keys=True),
        citations=re.findall(r"\[C[1-9][0-9]*\]", row["cite"]),
    )
    for claim in data["inputs"]:
        module = claim["producer"]
        if module not in {"CP-0", "CP-1"}:
            claim.update(availability="missing", original=None, limitation="Native optional gap")
            continue
        raw = (run / record["steps"][module]["handoff"]).read_bytes()
        front = parse(raw.decode()).front_matter
        claim["original"].update(
            run_id=front["run_id"],
            issuer_id=front["issuer_id"],
            analysis_date=front["analysis_date"],
            qa_status=front["qa_status"],
            sha256=hashlib.sha256(raw).hexdigest(),
        )
        proof = {
            "path": state.STATE,
            "sha256": hashlib.sha256((run / state.STATE).read_bytes()).hexdigest(),
        }
        claim["proofs"]["run"] = proof
        events = attempts.read_history(run, module, record["steps"][module])
        event = next(e for e in events if e["event"] == "validation")
        receipt = attempts.event_path(run, module, event["sequence"])
        claim["proofs"]["receipt"] = {
            "path": str(receipt.relative_to(run)),
            "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
        }
        if module == "CP-0":
            claim["cp0_lineage"] = dict(
                record["cp0_lineage"],
                current_sha256=claim["original"]["sha256"],
                proof=proof,
            )
            if "current_edits" in record["steps"][module]:
                claim["proofs"]["current"] = proof
    return data


@pytest.mark.parametrize("edit", ["none", "before", "after"])
def test_native_mixed_approval_lineage_preserves_original_ids(tmp_path: Path, edit: str) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    pending_id = run.name
    raw = (run / "handoffs/CP-0.md").read_bytes()
    send(run, RBOT_ROOT)
    assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == 0
    if edit == "before":
        (run / "handoffs/CP-0.md").write_bytes(raw + b"\nPre-Approval narrative.\n")
        current.reconcile(run, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    if edit == "after":
        (run / "handoffs/CP-0.md").write_bytes(raw + b"\nPost-Approval narrative.\n")
        current.reconcile(run, RBOT_ROOT)
    with_cp1(run, RBOT_ROOT, qa="Pass")
    record = state.read(run)
    origins.checked_history(run, record)
    message = dispatch.qualified_message(run, RBOT_ROOT, "CP-1B", record)
    assert all(str(run / f"handoffs/{m}.md") in message for m in ("CP-0", "CP-1"))
    before = {str(p): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    contract, rules = installed("CP-1B")
    result = validate(native_bundle(run), contract, rules)
    claims = json.loads(result.canonical_json)["inputs"]
    assert claims[0]["original"]["run_id"] == pending_id != record["run_id"]
    assert claims[1]["original"]["run_id"] == record["run_id"]
    lineage = claims[0]["cp0_lineage"]
    assert lineage["sha256"] == record["approved_origins"]["CP-0"]["sha256"]
    assert lineage["current_sha256"] == record["steps"]["CP-0"]["sha256"]
    assert (lineage["sha256"] != lineage["current_sha256"]) == (edit == "after")
    if edit == "none":
        assert (run / "handoffs/CP-0.md").read_bytes() == raw
    assert {str(p): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def lineage_example(contract: Contract) -> dict[str, Any]:
    data = example(contract)
    claim = next(c for c in data["inputs"] if c["producer"] == "CP-0")
    claim["original"]["run_id"] = "20261011-acme-pending-2"
    proof = {"path": "run-state.json", "sha256": SHA}
    claim["proofs"]["run"] = proof
    claim["cp0_lineage"] = {
        "pending_run_id": claim["original"]["run_id"],
        "issuer_id": "ACME",
        "sha256": SHA,
        "current_sha256": SHA,
        "proof": copy.deepcopy(proof),
    }
    return data


@pytest.mark.parametrize("target", TARGETS)
def test_lineage_contract_projection_is_bounded_to_declared_cp0(target: str) -> None:
    contract, rules = installed(target)
    data = lineage_example(contract) if "CP-0" in contract.handoff_inputs() else example(contract)
    result = validate(data, contract, rules)
    assert json.loads(result.input_shape_json)["handoff_claims"] == sorted(
        data["inputs"], key=lambda c: c["producer"]
    )
    assert validate(json.loads(result.canonical_json), contract, rules) == result


@pytest.mark.parametrize(
    "path,value",
    [
        (("cp0_lineage",), None),
        (("cp0_lineage",), []),
        (("cp0_lineage", "pending_run_id"), "20261011-foreign-pending"),
        (("cp0_lineage", "issuer_id"), "FOREIGN"),
        (("cp0_lineage", "current_sha256"), "b" * 64),
        (("cp0_lineage", "sha256"), "b" * 64),
        (("cp0_lineage", "sha256"), "z" * 64),
        (("cp0_lineage", "proof"), None),
        (("cp0_lineage", "proof", "path"), "other-state.json"),
        (("cp0_lineage", "proof", "sha256"), "b" * 64),
        (("cp0_lineage", "approval"), "forged"),
        (("proofs", "run"), None),
        (("original", "producer"), "CP-1"),
        (("original", "run_id"), "20261011-foreign-pending"),
        (("original", "path"), "handoffs/foreign.md"),
        (("original", "sha256"), "b" * 64),
        (("original", "issuer_id"), "FOREIGN"),
        (("original", "provenance"), "fixture"),
    ],
)
def test_lineage_identity_hash_and_proof_refusals(path: tuple[str, ...], value: object) -> None:
    contract, rules = installed("CP-1B")
    data = lineage_example(contract)
    parent = data["inputs"][0]
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


@pytest.mark.parametrize("pending_id", ["foreign-alias", "20261011-acme-pending-extra", "bad/id"])
def test_lineage_is_native_pending_identity_not_alias_allowlist(pending_id: str) -> None:
    contract, rules = installed()
    data = lineage_example(contract)
    claim = data["inputs"][0]
    claim["original"]["run_id"] = claim["cp0_lineage"]["pending_run_id"] = pending_id
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


def test_lineage_cannot_attach_to_other_or_missing_or_same_run_claim() -> None:
    contract, rules = installed("CP-1B")
    data = lineage_example(contract)
    for attack in ("other", "missing", "same"):
        altered = copy.deepcopy(data)
        cp0, cp1 = altered["inputs"][:2]
        if attack == "other":
            cp1["cp0_lineage"] = cp0["cp0_lineage"]
            cp1["original"]["run_id"] = cp0["original"]["run_id"]
            cp1["proofs"]["run"] = cp0["proofs"]["run"]
            cp1["original"]["path"] = cp0["original"]["path"]
        elif attack == "missing":
            cp0.update(availability="missing", original=None, limitation="Gap")
            cp0["proofs"] = dict.fromkeys(cp0["proofs"])
        else:
            altered["source_context"]["run_id"] = cp0["original"]["run_id"]
            cp1["original"]["run_id"] = cp0["original"]["run_id"]
        with pytest.raises(ManifestError):
            validate(altered, contract, rules)
    data["inputs"][1]["original"]["run_id"] = "20261011-other-pending"
    with pytest.raises(ManifestError, match="original run_id mismatch"):
        validate(data, contract, rules)


def test_edited_lineage_requires_current_state_and_binds_every_new_claim() -> None:
    contract, rules = installed()
    data = lineage_example(contract)
    claim = data["inputs"][0]
    claim["cp0_lineage"]["sha256"] = "b" * 64
    for current_proof in (None, {"path": "current.json", "sha256": SHA}):
        claim["proofs"]["current"] = current_proof
        with pytest.raises(ManifestError, match="current state proof"):
            validate(data, contract, rules)
    claim["proofs"]["current"] = copy.deepcopy(claim["proofs"]["run"])
    result = validate(data, contract, rules)
    for field in ("pending_run_id", "sha256", "proof", "current_sha256"):
        altered = json.loads(result.canonical_json)
        c = altered["inputs"][0]
        lineage = c["cp0_lineage"]
        if field == "pending_run_id":
            lineage[field] = c["original"]["run_id"] = "20261011-acme-pending-3"
        elif field == "proof":
            for proof in (lineage["proof"], c["proofs"]["run"], c["proofs"]["current"]):
                proof["sha256"] = "c" * 64
        elif field == "current_sha256":
            lineage[field] = c["original"]["sha256"] = "c" * 64
        else:
            lineage[field] = "c" * 64
        with pytest.raises(ManifestError, match="binding"):
            validate(altered, contract, rules)
        altered["binding_sha256"] = None
        assert validate(altered, contract, rules).binding_sha256 != result.binding_sha256


def test_preapproval_identity_without_lineage_and_version_boundary(tmp_path: Path) -> None:
    run = pending(tmp_path, RBOT_ROOT)
    send(run, RBOT_ROOT)
    assert accept.accept(run, RBOT_ROOT, "CP-0")["exit"] == 0
    contract, rules = installed()
    data = example(contract, provenance="fixture")
    front = parse((run / "handoffs/CP-0.md").read_text()).front_matter
    for key in ("run_id", "issuer_id", "analysis_date"):
        data["source_context"][key] = data["inputs"][0]["original"][key] = front[key]
    data.update(issuer_id=front["issuer_id"], analysis_date=front["analysis_date"])
    data["brief"]["as_of_date"]["value"] = front["analysis_date"]
    assert state.read(run).get("cp0_lineage") is None
    validate(data, contract, rules)
    data["schema"] = "rbot-isolation-input-shape/1"
    with pytest.raises(ManifestError, match="schema"):
        validate(data, contract, rules)
    data["schema"] = SCHEMA
    del data["inputs"][0]["cp0_lineage"]
    with pytest.raises(ManifestError, match="exact fields"):
        validate(data, contract, rules)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("provenance", ["source", "fixture"])
def test_actual_contract_projection(target: str, provenance: str) -> None:
    contract, rules = installed(target)
    data = example(contract, provenance=provenance)
    result = validate(data, contract, rules)
    shape = json.loads(result.input_shape_json)
    assert shape["groups"] == json.loads(json.dumps([asdict(item) for item in contract.inputs]))
    assert shape["brief_claims"] == data["brief"]
    assert {c["producer"] for c in shape["handoff_claims"]} == set(contract.handoff_inputs())
    assert all(
        c["original"]["run_id"] == data["source_context"]["run_id"] for c in shape["handoff_claims"]
    )
    assert all(c["original"]["provenance"] == provenance for c in shape["handoff_claims"])
    assert all(c["original"]["qa_status"] == "Blocked" for c in shape["handoff_claims"])
    assert validate(json.loads(result.canonical_json), contract, rules) == result
    assert data["binding_sha256"] is None


def test_repeated_source_groups_and_cp0_remain_exact() -> None:
    contract, rules = installed()
    groups = json.loads(validate(example(contract), contract, rules).input_shape_json)["groups"]
    issuer = [g for g in groups if g["kind"] == "sources" and g["values"] == ["issuer"]]
    assert len(issuer) == 2 and issuer[0]["document_types"] == [] and issuer[1]["document_types"]
    assert [g["required"] for g in groups if g["kind"] == "sources"] == [True, True, False]
    cp0, rules = installed("CP-0")
    shape = json.loads(validate(example(cp0), cp0, rules).input_shape_json)
    assert shape["brief_claims"] == {} and shape["handoff_claims"] == []
    assert shape["groups"][0]["values"] == list(rules.source_classes)


@pytest.mark.parametrize("required", [True, False])
def test_missing_claim_is_explicit_not_readiness(required: bool) -> None:
    contract, rules = installed("CP-6")
    data = example(contract)
    producer = next(
        i.values[0] for i in contract.inputs if i.kind == "handoff" and i.required == required
    )
    claim = next(c for c in data["inputs"] if c["producer"] == producer)
    claim.update(availability="missing", original=None, limitation="Not supplied")
    result = validate(data, contract, rules)
    assert "Not supplied" in result.input_shape_json
    claim["limitation"] = None
    with pytest.raises(ManifestError, match="missing claim"):
        validate(data, contract, rules)


@pytest.mark.parametrize(
    "field",
    [
        "status",
        "attempts",
        "model",
        "started_at",
        "finished_at",
        "approval",
        "acceptance",
        "qualified",
    ],
)
@pytest.mark.parametrize("location", ["top", "claim", "original", "context", "proof"])
def test_execution_and_unknown_fields_refuse(field: str, location: str) -> None:
    contract, rules = installed()
    data = example(contract)
    locations = {
        "top": data,
        "claim": data["inputs"][0],
        "original": data["inputs"][0]["original"],
        "context": data["source_context"],
        "proof": data["inputs"][0]["proofs"],
    }
    locations[location][field] = "forged"
    with pytest.raises(ManifestError, match="exact fields"):
        validate(data, contract, rules)


@pytest.mark.parametrize(
    "field", ["producer", "run_id", "issuer_id", "analysis_date", "provenance"]
)
def test_original_identity_and_fixture_promotion_refuse(field: str) -> None:
    contract, rules = installed()
    data = example(contract, provenance="fixture")
    data["inputs"][0]["original"][field] = "source" if field == "provenance" else "different"
    with pytest.raises(ManifestError, match="mismatch"):
        validate(data, contract, rules)


@pytest.mark.parametrize(
    "attack", ["duplicate", "extra", "omitted", "extra_brief", "omitted_brief", "pack_duplicate"]
)
def test_contract_set_boundaries(attack: str) -> None:
    contract, rules = installed()
    data = example(contract)
    if attack == "duplicate":
        data["inputs"].append(copy.deepcopy(data["inputs"][0]))
    elif attack == "extra":
        claim = copy.deepcopy(data["inputs"][0])
        claim["producer"] = claim["original"]["producer"] = "CP-UNDECLARED"
        data["inputs"].append(claim)
    elif attack == "omitted":
        data["inputs"].pop()
    elif attack == "extra_brief":
        data["brief"]["approval"] = next(iter(data["brief"].values()))
    elif attack == "omitted_brief":
        data["brief"].pop(next(iter(data["brief"])))
    else:
        data["pack"]["sources"].append(data["pack"]["sources"][0])
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


@pytest.mark.parametrize(
    "value", [True, False, 0, 1, float("nan"), float("inf"), [], {}, "", "\ud800"]
)
def test_text_and_number_boundaries(value: object) -> None:
    contract, rules = installed()
    data = example(contract)
    data["brief"]["issuer"]["value"] = value
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


@pytest.mark.parametrize(
    "path",
    [
        "../escape",
        "/absolute",
        "a//b",
        "a/./b",
        "a/../b",
        "a\\b",
        "a:b",
        "a\nb",
        "a\x00b",
        "a\x7fb",
    ],
)
def test_lexical_paths_refuse(path: str) -> None:
    contract, rules = installed()
    data = example(contract)
    data["inputs"][0]["original"]["path"] = path
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


def test_null_absent_and_malformed_refs() -> None:
    contract, rules = installed()
    data = example(contract)
    data["brief"]["issuer"] = {
        "value": None,
        "status": "Gap",
        "basis": "Unknown issuer label",
        "citations": [],
    }
    validate(data, contract, rules)
    for path, value in [("sha256", "A" * 64), ("path", "../bad")]:
        broken = copy.deepcopy(data)
        broken["inputs"][0]["proofs"]["host"] = {"path": "host/proof.json", "sha256": SHA}
        broken["inputs"][0]["proofs"]["host"][path] = value
        with pytest.raises(ManifestError):
            validate(broken, contract, rules)
    del data["brief"]["issuer"]["value"]
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


def test_ordering_binding_and_rules_changes() -> None:
    contract, rules = installed("CP-6")
    data = example(contract)
    data["pack"]["sources"].append({"path": "documents/b.pdf", "sha256": SHA})
    data["source_context"]["pack_sha256"] = descriptor_hash(data["pack"])
    result = validate(data, contract, rules)
    data["inputs"].reverse()
    data["pack"]["sources"].reverse()
    assert validate(data, contract, rules) == result
    for field in ["sha256", "path", "qa_status"]:
        altered = json.loads(result.canonical_json)
        altered["inputs"][0]["original"][field] = {
            "sha256": "b" * 64,
            "path": "handoffs/changed.md",
            "qa_status": "Pass",
        }[field]
        with pytest.raises(ManifestError, match="binding"):
            validate(altered, contract, rules)
    changed_rules = replace(rules, gap_marker="missing")
    assert validate(data, contract, changed_rules).binding_sha256 != result.binding_sha256
    changed = replace(contract, inputs=tuple(replace(i, required=False) for i in contract.inputs))
    assert validate(data, changed, rules).binding_sha256 != result.binding_sha256


@given(st.text(alphabet=st.characters(exclude_categories=["Cs"]), min_size=1, max_size=200))
def test_exact_value_binding_property(value: str) -> None:
    contract, rules = installed()
    data = example(contract)
    data["brief"]["issuer"]["value"] = value
    result = validate(data, contract, rules)
    assert json.loads(result.canonical_json)["brief"]["issuer"]["value"] == value
    data["brief"]["issuer"]["value"] += "changed"
    assert validate(data, contract, rules).binding_sha256 != result.binding_sha256


@pytest.mark.parametrize("lineage", [False, True])
def test_no_filesystem_calls_or_input_alias(monkeypatch: pytest.MonkeyPatch, lineage: bool) -> None:
    contract, rules = installed()
    data = lineage_example(contract) if lineage else example(contract)
    before = copy.deepcopy(data)

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("shape validation attempted filesystem access")

    monkeypatch.setattr("builtins.open", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(Path, "stat", forbidden)
    monkeypatch.setattr(Path, "resolve", forbidden)
    result = validate(data, contract, rules)
    assert data == before
    data["inputs"][0]["original"]["sha256"] = "b" * 64
    assert json.loads(result.canonical_json)["inputs"][0]["original"]["sha256"] == SHA


@pytest.mark.parametrize("location", ["provenance", "availability", "qa_status", "brief_status"])
def test_nested_enum_type_refuses_with_manifest_error(location: str) -> None:
    contract, rules = installed()
    data = example(contract)
    if location == "provenance":
        data["source_context"]["provenance"] = []
    elif location == "availability":
        data["inputs"][0]["availability"] = []
    elif location == "qa_status":
        data["inputs"][0]["original"]["qa_status"] = []
    else:
        data["brief"]["issuer"]["status"] = []
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


def test_total_input_budget_refuses_before_schema() -> None:
    contract, rules = installed()
    with pytest.raises(ManifestError, match="budget"):
        validate({"extra": [["x"] * 256 for _ in range(20)]}, contract, rules)


@pytest.mark.parametrize(
    "path,value",
    [
        (("schema",), "wrong"),
        (("target",), "CP-2"),
        (("issuer_id",), None),
        (("analysis_date",), "2026-02-30"),
        (("source_context", "analysis_date"), "2026-02-30"),
        (("source_context", "issuer_id"), "bad/id"),
        (("source_context", "root", "path"), "relative"),
        (("source_context", "pack_sha256"), "b" * 64),
        (("inputs",), {}),
        (("pack", "sources"), {}),
        (("inputs", 0, "original", "sha256"), "z" * 64),
        (("brief", "issuer", "status"), "Gap"),
        (("brief", "issuer", "basis"), None),
        (("brief", "issuer", "citations"), []),
        (("brief", "issuer", "citations"), ["[C0]"]),
        (("brief", "issuer", "citations"), ["[C1]", "[C1]"]),
        (("inputs", 0, "proofs", "receipt"), {"path": "proof.json"}),
    ],
)
def test_other_malformed_claims(path: tuple[str | int, ...], value: object) -> None:
    contract, rules = installed()
    data = example(contract)
    parent: Any = data
    for part in path[:-1]:
        parent = parent[part]
    parent[path[-1]] = value
    with pytest.raises(ManifestError):
        validate(data, contract, rules)


def test_bounds_cycles_and_unknown_context() -> None:
    contract, rules = installed("CP-0")
    data = example(contract)
    for key in ("issuer_id", "analysis_date"):
        data[key] = data["source_context"][key] = None
    assert json.loads(validate(data, contract, rules).canonical_json)["issuer_id"] is None
    cycle: list[object] = []
    cycle.append(cycle)
    for invalid in [
        cycle,
        ["x"] * 257,
        {str(n): "x" for n in range(129)},
        "x" * 4097,
        ["x" * 4096] * 65,
        {"x" * 4096 + str(n): "x" for n in range(65)},
    ]:
        with pytest.raises(ManifestError):
            validate(invalid, contract, rules)


@pytest.mark.parametrize("field", ["issuer_id", "as_of_date"])
def test_brief_identity_claims_must_match_source_context(field: str) -> None:
    contract, rules = installed()
    data = example(contract)
    data["brief"][field]["value"] = "Different identity"
    with pytest.raises(ManifestError, match="brief identity"):
        validate(data, contract, rules)


@pytest.mark.parametrize("kind", ["deep", "cycle", "json_text"])
def test_deep_graph_refuses_before_canonical_recursion(kind: str) -> None:
    contract, rules = installed()
    data: Any = "[" * 10000
    if kind == "cycle":
        data = {}
        data["cycle"] = data
    elif kind == "deep":
        data = None
        for _ in range(10000):
            data = [data]
    with pytest.raises(ManifestError, match=r"nesting|bounded nonempty text"):
        validate(data, contract, rules)
