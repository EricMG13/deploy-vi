"""A module's contract: its inputs, process and the tables its Handoff must carry.

`contract.json` is the one source for both the generated MODULE.md and the
validator, so the prompt a model reads and the check its output faces agree.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rbotlib.rules import Rules

RESERVED_TABLES = frozenset({"citations"})


class ContractError(ValueError):
    """A contract.json that breaks the contract format; lists every problem."""


@dataclass(frozen=True)
class Column:
    name: str
    critical: bool = False
    scale: str | None = None


@dataclass(frozen=True)
class TableSpec:
    id: str
    title: str
    min_rows: int
    columns: tuple[Column, ...]
    consumers: tuple[str, ...]


@dataclass(frozen=True)
class Input:
    kind: str  # "handoff" | "sources" | "run_brief"
    values: tuple[str, ...]
    required: bool
    why: str


@dataclass(frozen=True)
class Contract:
    module_id: str
    title: str
    reader_question: str
    inputs: tuple[Input, ...]
    process: tuple[str, ...]
    tables: tuple[TableSpec, ...]
    prohibited: tuple[str, ...]

    def handoff_inputs(self, *, required_only: bool = False) -> list[str]:
        return [
            i.values[0]
            for i in self.inputs
            if i.kind == "handoff" and (i.required or not required_only)
        ]


_INPUT_KINDS = ("handoff", "sources", "run_brief")


def _input(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Input:
    kinds = [k for k in _INPUT_KINDS if k in raw]
    if len(kinds) != 1:
        problems.append(f"input needs exactly one of {_INPUT_KINDS}: {raw}")
        return Input("handoff", ("?",), False, "")
    kind = kinds[0]
    value = raw[kind]
    values = (value,) if isinstance(value, str) else tuple(value)
    if kind == "sources":
        for v in values:
            if v not in rules.source_classes:
                problems.append(f"unknown source class {v!r}")
    if not raw.get("why"):
        problems.append(f"input {kind}={list(values)} has no 'why'")
    required = bool(raw.get("required", kind == "handoff"))
    return Input(kind, values, required, str(raw.get("why", "")))


def _column(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Column:
    scale = raw.get("scale")
    if scale is not None and scale not in rules.scales:
        problems.append(f"column {raw.get('name')!r} uses unknown scale {scale!r}")
    return Column(str(raw.get("name", "")), bool(raw.get("critical", False)), scale)


def _table(raw: dict[str, Any], rules: Rules, problems: list[str]) -> TableSpec:
    table_id = str(raw.get("id", ""))
    if not table_id or table_id in RESERVED_TABLES:
        problems.append(f"table id {table_id!r} is empty or reserved")
    columns = tuple(_column(c, rules, problems) for c in raw.get("columns", []))
    names = [c.name for c in columns]
    if not names or len(set(names)) != len(names) or "" in names:
        problems.append(f"table {table_id!r} needs unique, non-empty column names")
    consumers = tuple(raw.get("consumers", []))
    if not consumers:
        problems.append(f"table {table_id!r} has no consumers; nothing reads it")
    min_rows = int(raw.get("min_rows", 1))
    if min_rows < 0:
        problems.append(f"table {table_id!r} has negative min_rows")
    return TableSpec(table_id, str(raw.get("title", table_id)), min_rows, columns, consumers)


def contract_from_dict(data: dict[str, Any], rules: Rules) -> Contract:
    problems: list[str] = []
    for key in ("module_id", "title", "reader_question"):
        if not data.get(key):
            problems.append(f"missing {key}")
    inputs = tuple(_input(i, rules, problems) for i in data.get("inputs", []))
    tables = tuple(_table(t, rules, problems) for t in data.get("tables", []))
    ids = [t.id for t in tables]
    if len(set(ids)) != len(ids):
        problems.append("table ids are not unique")
    process = tuple(data.get("process", []))
    if not process:
        problems.append("process has no steps")
    if problems:
        raise ContractError(f"{data.get('module_id', '?')}: " + "; ".join(problems))
    return Contract(
        module_id=data["module_id"],
        title=data["title"],
        reader_question=data["reader_question"],
        inputs=inputs,
        process=process,
        tables=tables,
        prohibited=tuple(data.get("prohibited", [])),
    )


def load_contract(path: Path, rules: Rules) -> Contract:
    return contract_from_dict(json.loads(path.read_text(encoding="utf-8")), rules)
