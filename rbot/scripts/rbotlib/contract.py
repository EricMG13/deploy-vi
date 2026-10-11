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
    document_types: tuple[str, ...] = ()


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


def _str_list(value: object, where: str, problems: list[str]) -> tuple[str, ...]:
    """A list of non-empty strings; anything else is a problem, never split or coerced."""
    if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
        problems.append(f"{where} must be a list of non-empty strings")
        return ()
    return tuple(value)


def _dict_items(value: object, where: str, problems: list[str]) -> list[dict[str, Any]]:
    """The dict entries of a list; a non-list or a non-dict entry is a problem."""
    if not isinstance(value, list):
        problems.append(f"{where} must be a list")
        return []
    items = [v for v in value if isinstance(v, dict)]
    if len(items) != len(value):
        problems.append(f"{where} entries must be objects")
    return items


def _input_values(kind: str, raw: dict[str, Any], problems: list[str]) -> tuple[str, ...]:
    value = raw[kind]
    if kind != "handoff":
        return _str_list(value, f"input {kind}", problems)
    if not isinstance(value, str) or not value:
        problems.append("input handoff must be a single non-empty module id string")
        return ()
    return (value,)


def _document_types(
    raw: dict[str, Any], kind: str, rules: Rules, problems: list[str]
) -> tuple[str, ...]:
    """The document types a sources input names (amendment A4); `rbot grade` reads them."""
    if "document_types" not in raw:
        return ()
    if kind != "sources":
        problems.append(f"only a sources input takes document_types: {raw}")
    found = _str_list(raw["document_types"], f"input {kind} document_types", problems)
    scale = rules.scales["document_type"]
    problems += [f"unknown document type {d!r}" for d in found if d not in scale]
    return found


def _input(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Input:
    kinds = [k for k in _INPUT_KINDS if k in raw]
    if len(kinds) != 1:
        problems.append(f"input needs exactly one of {_INPUT_KINDS}: {raw}")
        return Input("handoff", ("?",), False, "")
    kind = kinds[0]
    values = _input_values(kind, raw, problems)
    if kind == "sources":
        for v in values:
            if v not in rules.source_classes:
                problems.append(f"unknown source class {v!r}")
    why = raw.get("why")
    if not isinstance(why, str) or not why:
        problems.append(f"input {kind}={list(values)} has no 'why'")
    required = raw.get("required", kind == "handoff")
    if not isinstance(required, bool):
        problems.append(f"input {kind}={list(values)} 'required' must be true or false")
        required = False
    document_types = _document_types(raw, kind, rules, problems)
    return Input(kind, values, required, why if isinstance(why, str) else "", document_types)


def _column(raw: dict[str, Any], rules: Rules, problems: list[str]) -> Column:
    scale = raw.get("scale")
    if scale is not None and scale not in rules.scales:
        problems.append(f"column {raw.get('name')!r} uses unknown scale {scale!r}")
    name = raw.get("name", "")
    if not isinstance(name, str):
        problems.append(f"column name {name!r} must be a string")
        name = ""
    critical = raw.get("critical", False)
    if not isinstance(critical, bool):
        problems.append(f"column {name!r} 'critical' must be true or false")
        critical = False
    return Column(name, critical, scale)


def _min_rows(raw: dict[str, Any], table_id: str, problems: list[str]) -> int:
    value = raw.get("min_rows", 1)
    if isinstance(value, bool) or not isinstance(value, int):
        problems.append(f"table {table_id!r} min_rows must be an integer")
        return 1
    if value < 0:
        problems.append(f"table {table_id!r} has negative min_rows")
    return value


def _text(raw: dict[str, Any], key: str, default: str, problems: list[str]) -> str:
    """A string field; any other type is a problem, never coerced with str()."""
    value = raw.get(key, default)
    if not isinstance(value, str):
        problems.append(f"table {key} {value!r} must be a string")
        return ""
    return value


def _table(raw: dict[str, Any], rules: Rules, problems: list[str]) -> TableSpec:
    table_id = _text(raw, "id", "", problems)
    if not table_id or table_id in RESERVED_TABLES:
        problems.append(f"table id {table_id!r} is empty or reserved")
    columns = tuple(
        _column(c, rules, problems)
        for c in _dict_items(raw.get("columns", []), f"table {table_id!r} columns", problems)
    )
    names = [c.name for c in columns]
    if not names or len(set(names)) != len(names) or "" in names:
        problems.append(f"table {table_id!r} needs unique, non-empty column names")
    consumers = _str_list(raw.get("consumers", []), f"table {table_id!r} consumers", problems)
    if not consumers:
        problems.append(f"table {table_id!r} has no consumers; nothing reads it")
    min_rows = _min_rows(raw, table_id, problems)
    title = _text(raw, "title", table_id, problems)
    return TableSpec(table_id, title, min_rows, columns, consumers)


def contract_from_dict(data: dict[str, Any], rules: Rules) -> Contract:
    if not isinstance(data, dict):
        raise ContractError("contract must be a JSON object")
    problems: list[str] = []
    for key in ("module_id", "title", "reader_question"):
        if not isinstance(data.get(key), str) or not data[key]:
            problems.append(f"missing {key}")
    inputs = tuple(
        _input(i, rules, problems) for i in _dict_items(data.get("inputs", []), "inputs", problems)
    )
    tables = tuple(
        _table(t, rules, problems) for t in _dict_items(data.get("tables", []), "tables", problems)
    )
    ids = [t.id for t in tables]
    if len(set(ids)) != len(ids):
        problems.append("table ids are not unique")
    process = _str_list(data.get("process", []), "process", problems)
    if not process:
        problems.append("process has no steps")
    prohibited = _str_list(data.get("prohibited", []), "prohibited", problems)
    if problems:
        raise ContractError(f"{data.get('module_id', '?')}: " + "; ".join(problems))
    return Contract(
        module_id=data["module_id"],
        title=data["title"],
        reader_question=data["reader_question"],
        inputs=inputs,
        process=process,
        tables=tables,
        prohibited=prohibited,
    )


def load_contract(path: Path, rules: Rules) -> Contract:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path}: not valid JSON: {exc}") from exc
    return contract_from_dict(data, rules)
