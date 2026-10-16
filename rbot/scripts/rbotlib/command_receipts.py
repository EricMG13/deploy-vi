"""Checked prospective ordinary row attribution; row observation is not returned exit."""

from __future__ import annotations

import copy
import hashlib
import re
from collections.abc import Iterator
from pathlib import Path

from rbotlib import host_evidence, runlog, state
from rbotlib.inventory import RunError

KEY = "command_receipts"


def checked(record: state.Record) -> list[state.Record]:
    entries = record.get(KEY, [])
    if not isinstance(entries, list):
        raise RunError("command receipt: expected a list")
    identities = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"intent", "observation", "end"}:
            raise RunError("command receipt: malformed observation")
        intent = entry["intent"]
        row = _intent(intent)
        if intent["invocation"] in identities:
            raise RunError("command receipt: duplicate invocation identity")
        identities.add(intent["invocation"])
        end = entry["end"]
        observations = {"missing row; exit unknown", f"candidate{intent['code']}; exit unknown"}
        if end is None:
            if entry["observation"] != "pending" or index != len(entries) - 1:
                raise RunError("command receipt: only latest intent may be pending")
        elif (
            type(end) is not int
            or end not in (intent["prefix_size"], intent["prefix_size"] + len(row) + 2)
            or entry["observation"] not in observations
        ):
            raise RunError("command receipt: malformed observed frontier")
    return entries


def _intent(intent: state.Record) -> bytes:
    if (
        not isinstance(intent, dict)
        or set(intent) != {"invocation", "code", "prefix_size", "prefix_sha256", "row", "binding"}
        or re.fullmatch(r"[0-9a-f]{32}", str(intent.get("invocation"))) is None
        or type(intent.get("code")) is not int
        or intent["code"] not in range(5)
        or type(intent.get("prefix_size")) is not int
        or intent["prefix_size"] < 0
        or not state._sha(intent.get("prefix_sha256"))
        or intent.get("binding")
        != host_evidence.digest({k: v for k, v in intent.items() if k != "binding"})
        or not isinstance(intent.get("row"), str)
    ):
        raise RunError("command receipt: malformed prospective intent")
    row = bytes.fromhex(intent["row"])
    parts = row.decode("ascii").split("\t")
    if len(parts) != 3 or not state._stamp(parts[0]) or not parts[1] or parts[2]:
        raise RunError("command receipt: malformed command row")
    return row


def _observe(raw: bytes, entry: state.Record) -> None:
    intent = entry["intent"]
    frontier = raw if entry["end"] is None else raw[: entry["end"]]
    observation = host_evidence._frontier(frontier, intent, intent["invocation"], (intent["code"],))
    observation = observation.replace("missing row", "missing row; exit unknown")
    if entry["end"] is not None and observation != entry["observation"]:
        raise RunError("command receipt: registered row observation changed")
    entry.update(
        end=len(frontier),
        observation=observation,
    )


def begin(owner: state._Locked, receipt: runlog.Receipt, code: int) -> None:
    record = state.read(owner.run)
    entries = checked(record)
    raw = runlog.path(owner.run).read_bytes() if runlog.path(owner.run).exists() else b""
    for entry in entries:
        _observe(raw, entry)
    value = dict(
        intent=host_evidence.receipt_intent(receipt, receipt.invocation, code),
        observation="pending",
        end=None,
    )
    if entries and entries[-1]["intent"]["invocation"] == receipt.invocation:
        entries[-1] = value
    else:
        entries.append(value)
    record[KEY] = entries
    owner.commit(owner.stage(record))


def finish(owner: state._Locked, receipt: runlog.Receipt) -> None:
    record = state.read(owner.run)
    entries = checked(record)
    if not entries or entries[-1]["intent"]["invocation"] != receipt.invocation:
        raise RunError("command receipt: current invocation intent changed")
    _observe(runlog.path(owner.run).read_bytes(), entries[-1])
    owner.commit(owner.stage(record))


def verify(run: Path, record: state.Record) -> None:
    raw = runlog.path(run).read_bytes() if runlog.path(run).exists() else b""
    entries = copy.deepcopy(checked(record))
    for entry in entries:
        _observe(raw, entry)
    cursor = entries[-1]["end"] if entries else len(raw)
    while cursor < len(raw):
        ends = []
        for intent, identifier, codes, limit in _host_intents(record, raw):
            if intent.get("prefix_size") != cursor:
                continue
            host_evidence._frontier(raw[:cursor], intent, identifier, codes)
            end = cursor + len(bytes.fromhex(intent["row"])) + 2
            if end > limit:
                continue
            host_evidence._frontier(raw[:end], intent, identifier, codes)
            ends.append(end)
        if len(ends) != 1:
            raise RunError("command receipt: unregistered/ambiguous log suffix; command refused")
        cursor = ends[0]


def _host_intents(
    record: state.Record, raw: bytes
) -> Iterator[tuple[state.Record, str, tuple[int, ...], int]]:
    for module, current in record["steps"].items():
        if not current.get("host_execution"):
            continue
        if current["kind"] != "host" or module not in ("MODEL", "FIT"):
            raise RunError("command receipt: unknown host row producer")
        evidence = host_evidence.checked(record, module, f"host-{module.lower()}/1")
        invocations = evidence["invocations"]
        for index, invocation in enumerate(invocations):
            limit = (
                _invocation_limit(invocations[index + 1], raw)
                if index + 1 < len(invocations)
                else len(raw)
            )
            yield from _invocation_intents(invocation, limit)


def _bound(value: object) -> int:
    if type(value) is not int or value < 0:
        raise RunError("command receipt: malformed host receipt frontier")
    return value


def _invocation_intents(
    invocation: state.Record, limit: int
) -> Iterator[tuple[state.Record, str, tuple[int, ...], int]]:
    following = invocation.get("following_receipts", [])
    if not isinstance(following, list) or any(not isinstance(r, dict) for r in following):
        raise RunError("command receipt: malformed following host receipts")
    own = invocation.get("receipt")
    if own is not None:
        if not isinstance(own, dict):
            raise RunError("command receipt: malformed host receipt intent")
        bound = following[0].get("prefix_size") if following else limit
        yield own, invocation["id"], (0, 1), _bound(bound)
    for position, intent in enumerate(following):
        bound = (
            following[position + 1].get("prefix_size") if position + 1 < len(following) else limit
        )
        yield intent, invocation["id"], tuple(range(5)), _bound(bound)


def _invocation_limit(invocation: state.Record, raw: bytes) -> int:
    log = state._fields(
        invocation.get("log"),
        {"size": lambda v: type(v) is int and v >= 0, "sha256": state._sha},
        "host log frontier",
    )
    size: int = log["size"]
    if size > len(raw) or hashlib.sha256(raw[:size]).hexdigest() != log["sha256"]:
        raise RunError("command receipt: subsequent host invocation log frontier changed")
    return size


def settle(owner: state._Locked) -> None:
    record = state.read(owner.run)
    verify(owner.run, record)
    entries = checked(record)
    if not entries or entries[-1]["end"] is not None:
        return
    _observe(runlog.path(owner.run).read_bytes(), entries[-1])
    owner.commit(owner.stage(record))


def preflight(run: Path) -> None:
    if state.write_guard(run) is None:
        return
    owner = state._Locked(run)
    try:
        verify(owner.run, state.read(owner.run))
        owner.owner.check()
    finally:
        warnings = owner.close()
        if warnings:
            raise RunError("; ".join(warnings))
