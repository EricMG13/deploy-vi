"""The catalog (Pathways, Front Pages, host-produced tables) and the tree check.

`check_tree` is the ICM-style drift gate: every contract loads, every
MODULE.md is current, every table has a reader that takes its Handoff, every
Pathway runs producers before consumers, every Front Page table has exactly
one owner in its Pathway, and every module fits the size budget. A depth list may name
a host step (`rules.host_producers`: MODEL, RUN_BRIEF, PROJECTION, FIT) by position, so a
module that takes `handoffs/MODEL.md` is checked to run after it (amendment A2). A Front
Page may carry `blocks`, each with the condition under which it is shown; `rbot grade`
reads them (an unconditional block's owner is one a Pathway cannot do without).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rbotlib.contract import Contract, ContractError, load_contract
from rbotlib.render import render_module
from rbotlib.report.charts import REGISTRY
from rbotlib.rules import Rules

REPORT = "REPORT"
ALWAYS = "always"
CONDITIONS = (
    ALWAYS,
    "primary",
    "unsecured_present",
    "portfolios",
    "prior_case",
    "pf_ltm",
    "projection",
    "rows_present",
    "gate_met",
)


@dataclass(frozen=True)
class Block:
    id: str
    title: str
    tables: tuple[str, ...]
    charts: tuple[str, ...]
    condition: str


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
    blocks: dict[str, tuple[Block, ...]] = field(default_factory=dict)

    def pathway(self, pathway_id: str) -> Pathway | None:
        return next((p for p in self.pathways if p.id == pathway_id), None)


def _block(raw: dict[str, Any]) -> Block:
    return Block(
        str(raw["id"]),
        str(raw.get("title", raw["id"])),
        tuple(raw.get("tables", ())),
        tuple(raw.get("charts", ())),
        str(raw.get("condition", ALWAYS)),
    )


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
        blocks={
            k: tuple(_block(b) for b in v["blocks"])
            for k, v in data["front_pages"].items()
            if "blocks" in v
        },
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


def _without_contract(pathway: Pathway, entry: str, hosts: tuple[str, ...]) -> list[str]:
    """A list entry with no contract: a host step is fine (A2); anything else is named."""
    if entry in hosts:
        return []
    if entry.startswith("CP-"):
        return [f"{pathway.id}: unknown module {entry}"]
    return [f"{pathway.id}: {entry} is not a host producer ({', '.join(hosts)})"]


def _order(
    pathway: Pathway,
    modules: tuple[str, ...],
    contracts: dict[str, Contract],
    hosts: tuple[str, ...],
) -> list[str]:
    """Producers before consumers; a host step needs no contract and counts as run (A2)."""
    problems = []
    for n, module_id in enumerate(modules):
        contract = contracts.get(module_id)
        if contract is None:
            problems += _without_contract(pathway, module_id, hosts)
            continue
        earlier = set(modules[:n])
        for needed in contract.handoff_inputs():
            in_pathway = needed in modules
            required = needed in contract.handoff_inputs(required_only=True)
            if (in_pathway or required) and needed not in earlier:
                problems.append(f"{pathway.id}: {module_id} runs before its input {needed}")
    return problems


ADD_ONS = frozenset({"RUN_BRIEF", "PROJECTION"})


def _owners(
    pathway: Pathway, modules: tuple[str, ...], catalog: Catalog, contracts: dict[str, Contract]
) -> list[str]:
    owned = [t.id for m in modules if m in contracts for t in contracts[m].tables]
    # A host step owns its tables only where the Pathway runs it; the Run Brief is on every run and
    # PROJECTION is an add-on a Full-depth run may append after CP-2G.
    owned += [t for t, host in catalog.host_tables.items() if host in modules or host in ADD_ONS]
    problems = []
    for table_id in catalog.front_pages.get(pathway.front_page, ()):
        count = owned.count(table_id)
        if count != 1:
            problems.append(f"{pathway.id}: front-page table {table_id} has {count} owners")
    return problems


def _conditions(catalog: Catalog) -> list[str]:
    return [
        f"front page {page} block {b.id}: unknown condition {b.condition!r}"
        for page, blocks in catalog.blocks.items()
        for b in blocks
        if b.condition not in CONDITIONS
    ]


def _block_references(catalog: Catalog) -> list[str]:
    """Amendment A6: a block's tables belong to its front page and its charts are registered."""
    problems = []
    for page, blocks in catalog.blocks.items():
        listed = set(catalog.front_pages.get(page, ()))
        for b in blocks:
            problems += [
                f"front page {page} block {b.id}: table {t} not in tables"
                for t in b.tables
                if t not in listed
            ]
            problems += [
                f"front page {page} block {b.id}: unknown chart {c}"
                for c in b.charts
                if c not in REGISTRY
            ]
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
    problems += _conditions(catalog)
    problems += _block_references(catalog)
    for pathway in catalog.pathways:
        if pathway.front_page not in catalog.front_pages:
            problems.append(f"{pathway.id}: unknown front page {pathway.front_page}")
        for modules in pathway.depths.values():
            problems += _order(pathway, modules, contracts, rules.host_producers)
            problems += _owners(pathway, modules, catalog, contracts)
    return problems
