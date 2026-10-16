"""Interfaces spec section 0.1, re-derived (section 12.5 row 05,
`test_pathway_membership_matches_front_pages`).

Quick = the owners of every table on the Front Page, their required Handoff inputs
(transitively) and CP-0, CP-5 and CP-8, with CP-L10 owning the credit-view tables in place of
CP-2. Full = the same with CP-2, plus CP-DR and every feeder: an optional Handoff input of a
block owner. Owners come from the shipped contracts and the catalog's host tables; inputs from
the shipped contracts, or from section 1 (`spec_fixture.INPUTS`) for a module a later plan
ships, and a host step's from `rbotlib.grade.HOST_INPUTS`. PROJECTION runs only after CP-2G,
a Full-depth module, so at Quick it owns nothing (section 5).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from rbotlib.catalog import check_tree, load_catalog, load_contracts
from rbotlib.grade import HOST_INPUTS
from rbotlib.rules import RBOT_ROOT, Rules
from spec_fixture import INPUTS, PATHWAYS

FRONT_PAGE = "credit_snapshot"
CREDIT_VIEW = ("snapshot.credit_view", "snapshot.strengths_weaknesses")
ALWAYS = ("CP-0", "CP-5", "CP-8")
CREDIT_OWNER = {"full": "CP-2", "quick": "CP-L10"}  # one owner per table per depth list


def _inputs(rules: Rules) -> dict[str, tuple[list[str], list[str]]]:
    """Module or host step -> (required, optional) Handoff inputs."""
    found = {m: (r.split(), o.split()) for m, (r, o) in INPUTS.items()}
    for module_id, c in load_contracts(RBOT_ROOT, rules, []).items():
        required = c.handoff_inputs(required_only=True)
        found[module_id] = (required, [h for h in c.handoff_inputs() if h not in required])
    found |= {host: (list(needs), []) for host, needs in HOST_INPUTS.items()}
    return found


def _owners(rules: Rules, depth: str) -> set[str]:
    catalog = load_catalog(RBOT_ROOT)
    credit_owner = CREDIT_OWNER[depth]
    owner = {
        t.id: m
        for m, c in load_contracts(RBOT_ROOT, rules, []).items()
        for t in c.tables
        if t.id not in CREDIT_VIEW or m == credit_owner
    }
    owner |= catalog.host_tables
    tables = {t for b in catalog.blocks[FRONT_PAGE] for t in b.tables}
    owners = {owner[t] for t in tables} - {"RUN_BRIEF"}
    return owners - {"PROJECTION"} if depth == "quick" else owners


def test_the_credit_view_has_one_owner_per_depth_list(rules: Rules) -> None:
    """CP-2 and CP-L10 both declare the credit-view tables; the depth list picks the owner."""
    declared = {
        m
        for m, c in load_contracts(RBOT_ROOT, rules, []).items()
        if {t.id for t in c.tables} >= set(CREDIT_VIEW)
    }
    assert declared == {"CP-2", "CP-L10"}
    assert {"CP-2", "CP-L10"} & _owners(rules, "full") == {"CP-2"}
    assert {"CP-2", "CP-L10"} & _owners(rules, "quick") == {"CP-L10"}


def derive(rules: Rules, depth: str) -> set[str]:
    inputs = _inputs(rules)
    owners = _owners(rules, depth)
    steps = owners | set(ALWAYS)
    if depth == "full":
        steps |= {"CP-DR"} | {f for o in owners for f in inputs[o][1] if f != "CP-L10"}
    frontier = list(steps)
    while frontier:
        for needed in inputs[frontier.pop()][0]:
            if needed not in steps:
                steps.add(needed)
                frontier.append(needed)
    return steps


def _spec_list(depth: str) -> list[str]:
    _, _, _, full, quick = next(p for p in PATHWAYS if p[0] == "FULL_CREDIT_ASSESSMENT")
    return (full if depth == "full" else quick).split()


def test_pathway_membership_matches_front_pages(rules: Rules) -> None:
    for depth in ("full", "quick"):
        assert derive(rules, depth) == set(_spec_list(depth)), depth


def test_the_committed_list_is_the_derived_list_of_built_steps(rules: Rules) -> None:
    contracts = load_contracts(RBOT_ROOT, rules, [])
    hosts = {h for h, needs in HOST_INPUTS.items() if all(n in contracts for n in needs)}
    built = set(contracts) | hosts
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    expected = [s for s in _spec_list("full") if s in derive(rules, "full") and s in built]
    assert list(pathway.depths["full"]) == expected
    quick = derive(rules, "quick")
    assert not quick <= built and "quick" not in pathway.depths  # CP-L10 and CP-8 come later


def test_a_host_table_needs_its_host_step_in_the_pathway(tmp_path: Path, rules: Rules) -> None:
    """Rest review M1: take FIT out of the list and `snapshot.portfolio_fit` has no producer."""
    root = tmp_path / "rbot"
    shutil.copytree(RBOT_ROOT, root, ignore=shutil.ignore_patterns("__pycache__", "scripts"))
    path = root / "catalog.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    full = next(p for p in data["pathways"] if p["id"] == "FULL_CREDIT_ASSESSMENT")
    full["depths"]["full"].remove("FIT")
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    problems = check_tree(root, rules)
    assert any("snapshot.portfolio_fit has 0 owners" in p for p in problems), problems
    assert check_tree(RBOT_ROOT, rules) == []
