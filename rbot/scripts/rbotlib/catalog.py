"""The catalog (Pathways, Front Pages, host-produced tables) and the tree check.

`check_tree` is the ICM-style drift gate: every contract loads, every
MODULE.md is current, every table has a reader that takes its Handoff, every
Pathway runs producers before consumers, every Front Page table has exactly
one owner in its Pathway, and every module fits the size budget.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from rbotlib.contract import Contract, ContractError, load_contract
from rbotlib.render import render_module
from rbotlib.rules import Rules

REPORT = "REPORT"


@dataclass(frozen=True)
class Pathway:
    id: str
    label: str
    front_page: str
    depths: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class Catalog:
    size_budget_bytes: int
    host_tables: dict[str, str]
    front_pages: dict[str, tuple[str, ...]]
    pathways: tuple[Pathway, ...]


def load_catalog(root: Path) -> Catalog:
    data = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    return Catalog(
        size_budget_bytes=int(data["size_budget_bytes"]),
        host_tables=dict(data["host_tables"]),
        front_pages={k: tuple(v["tables"]) for k, v in data["front_pages"].items()},
        pathways=tuple(
            Pathway(
                p["id"], p["label"], p["front_page"], {d: tuple(m) for d, m in p["depths"].items()}
            )
            for p in data["pathways"]
        ),
    )


def load_contracts(root: Path, rules: Rules, problems: list[str]) -> dict[str, Contract]:
    contracts: dict[str, Contract] = {}
    modules = root / "modules"
    if not modules.is_dir():
        return contracts
    for folder in sorted(p for p in modules.iterdir() if p.is_dir()):
        name = folder.name
        path = folder / "contract.json"
        if not path.is_file():
            problems.append(f"{name}: no contract.json")
            continue
        try:
            contract = load_contract(path, rules)
        except (ContractError, ValueError, KeyError) as exc:
            problems.append(f"{name}: {exc}")
            continue
        if contract.module_id != name:
            problems.append(f"{name}: module_id is {contract.module_id!r}")
            continue
        contracts[name] = contract
    return contracts


def _generated(root: Path, contracts: dict[str, Contract], rules: Rules, budget: int) -> list[str]:
    problems = []
    canon = len((root / "canon.md").read_bytes())
    for module_id, contract in contracts.items():
        path = root / "modules" / module_id / "MODULE.md"
        text = path.read_text(encoding="utf-8") if path.exists() else None
        if text != render_module(contract, rules):
            problems.append(
                f"{module_id}: MODULE.md is missing or stale; run render-module --write"
            )
        elif len(text.encode()) + canon > budget:
            problems.append(f"{module_id}: MODULE.md + canon.md exceed {budget} bytes")
    return problems


def _consumers(contracts: dict[str, Contract], rules: Rules) -> list[str]:
    problems = []
    readers = set(rules.host_producers) | {REPORT}
    for producer in contracts.values():
        for spec in producer.tables:
            for consumer in spec.consumers:
                if consumer in readers:
                    continue
                if consumer not in contracts:
                    problems.append(f"{producer.module_id}.{spec.id}: unknown consumer {consumer}")
                elif producer.module_id not in contracts[consumer].handoff_inputs():
                    problems.append(
                        f"{producer.module_id}.{spec.id}: {consumer} does not take "
                        f"{producer.module_id}'s Handoff"
                    )
    return problems


def _order(pathway: Pathway, modules: tuple[str, ...], contracts: dict[str, Contract]) -> list[str]:
    problems = []
    for n, module_id in enumerate(modules):
        contract = contracts.get(module_id)
        if contract is None:
            problems.append(f"{pathway.id}: unknown module {module_id}")
            continue
        earlier = set(modules[:n])
        for needed in contract.handoff_inputs():
            in_pathway = needed in modules
            required = needed in contract.handoff_inputs(required_only=True)
            if (in_pathway or required) and needed not in earlier:
                problems.append(f"{pathway.id}: {module_id} runs before its input {needed}")
    return problems


def _owners(
    pathway: Pathway, modules: tuple[str, ...], catalog: Catalog, contracts: dict[str, Contract]
) -> list[str]:
    owned = [t.id for m in modules if m in contracts for t in contracts[m].tables]
    owned += list(catalog.host_tables)
    problems = []
    for table_id in catalog.front_pages.get(pathway.front_page, ()):
        count = owned.count(table_id)
        if count != 1:
            problems.append(f"{pathway.id}: front-page table {table_id} has {count} owners")
    return problems


def check_tree(root: Path, rules: Rules) -> list[str]:
    problems: list[str] = []
    catalog = load_catalog(root)
    contracts = load_contracts(root, rules, problems)
    problems += _generated(root, contracts, rules, catalog.size_budget_bytes)
    problems += _consumers(contracts, rules)
    module_tables = {t.id for c in contracts.values() for t in c.tables}
    problems += [
        f"host table {t} is also a module table" for t in catalog.host_tables if t in module_tables
    ]
    for pathway in catalog.pathways:
        if pathway.front_page not in catalog.front_pages:
            problems.append(f"{pathway.id}: unknown front page {pathway.front_page}")
        for modules in pathway.depths.values():
            problems += _order(pathway, modules, contracts)
            problems += _owners(pathway, modules, catalog, contracts)
    return problems
