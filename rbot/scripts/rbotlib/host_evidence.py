"""Prospective host invocation evidence; interruption is never an invented exit."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rbotlib import dispatch, runlog, state
from rbotlib.inventory import RunError

SCHEMA = "rbot-host-continuation/1"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def context(root: Path, record: state.Record) -> str:
    names = ["rules.json", "catalog.json", "canon.md"]
    names += [str(p.relative_to(root)) for p in (root / "scripts").rglob("*.py")]
    names += [str(p.relative_to(root)) for p in (root / "modules").glob("*/contract.json")]
    return digest(
        {
            "root": str(root),
            "files": {n: dispatch._sha(dispatch._file(root, n)) for n in sorted(names)},
            "state": {
                k: record[k]
                for k in (
                    "run_id",
                    "pack_root",
                    "issuer_id",
                    "as_of_date",
                    "approval",
                    "plan",
                    "pathway",
                    "depth",
                    "primary",
                    "deep_research",
                    "run_brief_sha256",
                )
            },
        }
    )


def match_inputs(
    evidence: state.Record, hashes: dict[str, str | None], missing: str, fingerprint: str
) -> None:
    if (
        evidence["inputs"] != hashes
        or evidence["optional_exclusion"] != missing
        or evidence["context"] != fingerprint
    ):
        raise RunError("host: registered inputs/exclusion/Approval/backend changed")


def binding(evidence: state.Record) -> str:
    return digest({k: v for k, v in evidence.items() if k not in ("binding", "invocations")})


def checked(record: state.Record, module: str, origin: str) -> state.Record:
    current = record["steps"][module]
    evidence: state.Record = current.get("host_execution", {})
    if (
        not isinstance(evidence, dict)
        or current.get("attempts") != 1
        or evidence.get("schema") != SCHEMA
        or evidence.get("origin") != origin
        or evidence.get("ownership") != record.get("ownership")
        or re.fullmatch(r"[0-9a-f]{32}", str(evidence.get("token"))) is None
        or evidence.get("binding") != binding(evidence)
        or evidence.get("generated_at") != current.get("started_at")
        or not state._stamp(evidence.get("generated_at"))
        or not isinstance(evidence.get("invocations"), list)
        or not evidence["invocations"]
    ):
        raise RunError(f"{module}: registered prospective host entitlement/origin differs")
    invocations = evidence["invocations"]
    identities = set()
    for invocation in invocations:
        identifier = invocation.get("id") if isinstance(invocation, dict) else None
        if (
            re.fullmatch(r"[0-9a-f]{32}", str(identifier)) is None
            or identifier in identities
            or not state._stamp(invocation.get("started_at"))
        ):
            raise RunError(f"{module}: invalid host invocation attribution")
        identities.add(identifier)
    return evidence


def _frontier(
    raw: bytes, intent: state.Record, identifier: str, codes: tuple[int, ...] = (0, 1)
) -> str:
    if (
        not isinstance(intent, dict)
        or intent.get("invocation") != identifier
        or type(intent.get("code")) is not int
        or intent.get("code") not in codes
        or type(intent.get("prefix_size")) is not int
        or intent["prefix_size"] < 0
        or not state._sha(intent.get("prefix_sha256"))
        or not isinstance(intent.get("row"), str)
        or intent.get("binding") != digest({k: v for k, v in intent.items() if k != "binding"})
    ):
        raise RunError("host: malformed/forged receipt intent")
    row = bytes.fromhex(intent["row"])
    prefix, suffix = raw[: intent["prefix_size"]], raw[intent["prefix_size"] :]
    if (
        len(prefix) != intent["prefix_size"]
        or hashlib.sha256(prefix).hexdigest() != intent["prefix_sha256"]
        or len(row.split(b"\t")) != 3
        or not row.endswith(b"\t")
        or suffix not in (b"", *(row + f"{code}\n".encode() for code in codes))
    ):
        raise RunError("host: receipt prefix/row changed; evidence preserved")
    return "missing row" if not suffix else f"candidate{suffix[-2:-1].decode()}; exit unknown"


def observe(run: Path, invocation: state.Record) -> str:
    raw = runlog.path(run).read_bytes() if runlog.path(run).exists() else b""
    receipts = invocation.get("following_receipts", [])
    if not isinstance(receipts, list) or any(
        not isinstance(r, dict) or type(r.get("prefix_size")) is not int or r["prefix_size"] < 0
        for r in receipts
    ):
        raise RunError("host: invalid following receipt attribution")
    own = invocation.get("receipt")
    frontier = raw[: receipts[0]["prefix_size"]] if receipts else raw
    if own is not None:
        observation = _frontier(frontier, own, invocation["id"])
    else:
        if invocation.get("log") != {
            "size": len(frontier),
            "sha256": hashlib.sha256(frontier).hexdigest(),
        }:
            raise RunError("host: log prefix changed without persisted receipt; preserved")
        observation = "no persisted receipt intent"
    for index, receipt in enumerate(receipts):
        frontier = raw[: receipts[index + 1]["prefix_size"]] if index + 1 < len(receipts) else raw
        _frontier(frontier, receipt, invocation["id"], tuple(range(5)))
    return observation


def receipt_intent(receipt: runlog.Receipt, identifier: str, code: int) -> state.Record:
    value: state.Record = {
        "invocation": identifier,
        "code": code,
        "prefix_size": len(receipt.prefix),
        "prefix_sha256": hashlib.sha256(receipt.prefix).hexdigest(),
        "row": receipt.row.hex(),
    }
    value["binding"] = digest(value)
    return value


def following(owner: state._Locked, receipt: runlog.Receipt, code: int) -> None:
    """Attribute ordinary rows following an interrupted host before their publication."""
    record = state.read(owner.run)
    changed = False
    for module, current in record["steps"].items():
        evidence = current.get("host_execution", {})
        if not isinstance(evidence, dict):
            raise RunError("host: malformed prospective host entitlement")
        if current["status"] != "running" or evidence.get("schema") != SCHEMA:
            continue
        checked(record, module, f"host-{module.lower()}/1")
        invocation = evidence["invocations"][-1]
        observe(owner.run, invocation)
        receipts = invocation.setdefault("following_receipts", [])
        value = receipt_intent(receipt, invocation["id"], code)
        if receipts and all(
            receipts[-1][k] == value[k] for k in ("row", "prefix_size", "prefix_sha256")
        ):
            receipts[-1] = value
        else:
            receipts.append(value)
        changed = True
    if changed:
        owner.commit(owner.stage(record))


def invocation(record: state.Record, module: str, run: Path) -> None:
    evidence = record["steps"][module]["host_execution"]
    previous = evidence["invocations"][-1] if evidence["invocations"] else None
    observation = observe(run, previous) if previous else "fresh registration"
    if previous is not None:
        previous["completion"] = "interrupted; exit unknown"
        previous["observation"] = observation
    raw = runlog.path(run).read_bytes() if runlog.path(run).exists() else b""
    evidence["invocations"].append(
        {
            "id": uuid4().hex,
            "started_at": datetime.now(UTC).isoformat(),
            "predecessor": observation,
            "log": {"size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
        }
    )


def intent(owner: state._Locked, module: str, receipt: runlog.Receipt, code: int) -> None:
    record = state.read(owner.run)
    current = record["steps"][module]["host_execution"]["invocations"][-1]
    value = receipt_intent(receipt, current["id"], code)
    current["receipt"] = value
    owner.commit(owner.stage(record))


def accepted(record: state.Record, module: str, origin: str, run: Path, root: Path) -> None:
    evidence = checked(record, module, origin)
    if evidence["context"] != context(root, record):
        raise RunError(f"{module}: accepted backend/Approval context changed")
    current = evidence["invocations"][-1]
    intent = current.get("receipt", {})
    raw = runlog.path(run).read_bytes()
    if (
        not isinstance(intent, dict)
        or record["steps"][module]["status"] != "accepted"
        or type(record["steps"][module].get("host_exit")) is not int
        or record["steps"][module].get("host_exit") != 0
        or type(current.get("exit")) is not int
        or current.get("exit") != 0
        or current.get("completion") != "completed"
        or intent.get("code") != 0
        or not state._stamp(current.get("finished_at"))
    ):
        raise RunError(f"{module}: accepted invocation/receipt attribution required")
    # Later ordinary command rows may follow the accepted invocation's exact row.
    size = intent.get("prefix_size", -1)
    row = bytes.fromhex(intent.get("row", ""))
    if type(size) is not int or size < 0 or not raw[size:].startswith(row + b"0\n"):
        raise RunError(f"{module}: accepted receipt changed; acceptance refused")
    _frontier(raw[: size + len(row) + 2], intent, current["id"])
