"""Test fixture: the interfaces spec's Pathways (section 5) over stand-in module contracts.

Each stand-in declares the Handoff inputs section 1 gives its module and nothing else, so
`rbot check` ordering (amendment A2) and `rbot grade` can run on the real Pathway lists
before the modules exist. A stand-in is never shipped: the module's own contract replaces
it when its plan lands. CP-0 is the real contract.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from conftest import write_module
from rbotlib.rules import RBOT_ROOT, Rules

# Interfaces spec section 1: module -> (required Handoff inputs, optional Handoff inputs).
INPUTS = {
    "CP-1": ("CP-0", ""),
    "CP-1A": ("CP-0", "CP-1"),
    "CP-1B": ("CP-0 CP-1", "CP-1A"),
    "CP-1C": ("CP-0 CP-1", "MODEL"),
    "CP-1D": ("CP-0 CP-1", "CP-1A CP-1B"),
    "CP-2": ("CP-0 CP-1 CP-1A MODEL", "CP-1B CP-1C CP-1D CP-DR"),
    "CP-2A": ("CP-0 CP-1 CP-2 MODEL", "CP-1A CP-1B CP-DR"),
    "CP-2D": ("CP-0 CP-1 MODEL", "CP-4 CP-2 CP-L10 CP-2A CP-1B"),
    "CP-2E": ("CP-0 CP-1 MODEL", "CP-2 CP-2A"),
    "CP-2G": ("CP-0 CP-1 CP-2 MODEL", "CP-1B CP-1C CP-1D CP-2A CP-2D CP-2E CP-4"),
    "CP-2H": ("CP-0 CP-1A MODEL", "CP-2 CP-L10 CP-2A CP-2D CP-2G PROJECTION"),
    "CP-3": (
        "CP-0 CP-1 MODEL",
        "CP-1A CP-1C CP-1D CP-2 CP-L10 CP-2A CP-2E CP-2G PROJECTION CP-2H CP-3C CP-3D CP-4 "
        "CP-4C CP-DR",
    ),
    "CP-3C": (
        "CP-0 CP-1 CP-4 MODEL",
        "CP-1A CP-2D CP-2 CP-L10 CP-2G PROJECTION CP-2A CP-2E CP-2H",
    ),
    "CP-3D": ("CP-0 CP-1", "CP-2 CP-L10 CP-2H CP-1C"),
    "CP-4": ("CP-0 CP-1 MODEL", "CP-1A CP-1D CP-2 CP-L10"),
    "CP-4C": (
        "CP-0 CP-1 CP-4 MODEL",
        "CP-1A CP-1C CP-1D CP-3C CP-2D CP-2 CP-L10 CP-2A CP-2H CP-3D",
    ),
    "CP-5": (
        "CP-0",
        "CP-1 CP-1A CP-1B CP-1C CP-1D CP-2 CP-2A CP-2D CP-2E CP-2G CP-2H CP-3 CP-3C CP-3D CP-4 "
        "CP-4C CP-L10 CP-DR MODEL PROJECTION FIT",
    ),
    "CP-6": (
        "CP-0 CP-3 CP-5",
        "CP-2 CP-L10 FIT CP-1A CP-1B CP-1C CP-1D CP-2A CP-2D CP-2E CP-2G PROJECTION CP-2H CP-3C "
        "CP-3D CP-4 CP-4C CP-DR",
    ),
    "CP-L10": ("CP-0 CP-1 CP-1A MODEL", "CP-1B"),
    "CP-DR": ("CP-0 CP-1A", "CP-1"),
    "CP-8": (
        "CP-0",
        "CP-1 CP-1A CP-1B CP-1C CP-1D CP-2 CP-2A CP-2D CP-2E CP-2G CP-2H CP-3 CP-3C CP-3D CP-4 "
        "CP-4C CP-6 CP-L10 CP-DR MODEL PROJECTION FIT CP-5",
    ),
}

# Interfaces spec section 5, verbatim: (id, label, front page, full list, quick list).
PATHWAYS = [
    (
        "FULL_CREDIT_ASSESSMENT",
        "Full Credit Assessment",
        "credit_snapshot",
        "CP-0 CP-1 CP-1A CP-DR CP-1B CP-1D MODEL CP-1C CP-2 CP-2A CP-2E CP-4 CP-2D CP-2G "
        "PROJECTION CP-2H CP-3D CP-3C CP-4C CP-3 FIT CP-5 CP-6 CP-8",
        "CP-0 CP-1 CP-1A CP-1B MODEL CP-L10 CP-3 FIT CP-5 CP-6 CP-8",
    ),
    (
        "EARNINGS_UPDATE",
        "Earnings Update",
        "earnings_update",
        "CP-0 CP-1 CP-1A CP-DR CP-1B CP-1D MODEL CP-2 CP-5 CP-8",
        "CP-0 CP-1 CP-1A CP-1B MODEL CP-L10 CP-5 CP-8",
    ),
    (
        "RELATIVE_VALUE",
        "Relative Value",
        "relative_value",
        "CP-0 CP-1 CP-1A CP-DR CP-1D MODEL CP-1C CP-2 CP-2A CP-4 CP-2G PROJECTION CP-3D CP-3 "
        "FIT CP-5 CP-6 CP-8",
        "CP-0 CP-1 CP-1A MODEL CP-1C CP-L10 CP-3D CP-3 FIT CP-5 CP-6 CP-8",
    ),
    (
        "COVENANT_REFINANCING",
        "Covenant & Refinancing",
        "covenant_refinancing",
        "CP-0 CP-1 CP-1A CP-DR CP-1D MODEL CP-2 CP-4 CP-2D CP-3C CP-5 CP-8",
        "CP-0 CP-1 CP-1A MODEL CP-L10 CP-4 CP-2D CP-3C CP-5 CP-8",
    ),
    (
        "DISTRESSED_RESTRUCTURING",
        "Distressed & Restructuring",
        "distressed_restructuring",
        "CP-0 CP-1 CP-1A CP-DR CP-1D MODEL CP-2 CP-2A CP-4 CP-2D CP-2G PROJECTION CP-2H CP-3D "
        "CP-3C CP-4C CP-3 FIT CP-5 CP-6 CP-8",
        "CP-0 CP-1 CP-1A MODEL CP-L10 CP-4 CP-2D CP-2H CP-3C CP-4C CP-3 FIT CP-5 CP-6 CP-8",
    ),
    (
        "PORTFOLIO_DECISION",
        "Portfolio Decision",
        "portfolio_decision",
        "CP-0 CP-1 CP-1A CP-DR CP-1D MODEL CP-2 CP-2A CP-4 CP-3D CP-3 FIT CP-5 CP-6 CP-8",
        "CP-0 CP-1 CP-1A MODEL CP-L10 CP-3 FIT CP-5 CP-6 CP-8",
    ),
]

# Interfaces spec section 4: the Portfolio Fit block of each Front Page and its condition.
FIT_BLOCKS = {
    "earnings_update": None,
    "relative_value": "portfolios",
    "covenant_refinancing": None,
    "distressed_restructuring": "portfolios",
    "portfolio_decision": "always",
}


def stand_in(module_id: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    required, optional = INPUTS[module_id]
    inputs: list[dict[str, Any]] = [
        {"handoff": h, "required": True, "why": "section 1"} for h in required.split()
    ]
    inputs += [{"handoff": h, "required": False, "why": "section 1"} for h in optional.split()]
    return {
        "module_id": module_id,
        "title": f"Stand-in for {module_id}",
        "reader_question": "None: a test stand-in.",
        "inputs": inputs + sources,
        "process": ["None: a test stand-in."],
        "tables": [],
    }


def _front_pages() -> dict[str, Any]:
    real = json.loads((RBOT_ROOT / "catalog.json").read_text(encoding="utf-8"))["front_pages"]
    pages: dict[str, Any] = {"credit_snapshot": real["credit_snapshot"]}
    for page, condition in FIT_BLOCKS.items():
        blocks = [{"id": "header", "tables": ["snapshot.run_header"]}]
        if condition:
            fit = ["snapshot.portfolio_fit"]
            blocks.append({"id": "portfolio_fit", "tables": fit, "condition": condition})
        tables = [t for b in blocks for t in b["tables"]]
        pages[page] = {"title": page, "tables": tables, "blocks": blocks}
    return pages


def build_tree(root: Path, rules: Rules, sources: dict[str, list[dict[str, Any]]]) -> Path:
    """An RBOT folder: real rules, canon and CP-0; stand-ins; the section 5 Pathways."""
    for name in ("rules.json", "canon.md"):
        shutil.copy(RBOT_ROOT / name, root / name)
    shutil.copytree(RBOT_ROOT / "modules" / "CP-0", root / "modules" / "CP-0")
    for module_id in INPUTS:
        write_module(root, stand_in(module_id, sources.get(module_id, [])), rules)
    catalog = json.loads((RBOT_ROOT / "catalog.json").read_text(encoding="utf-8"))
    catalog["front_pages"] = _front_pages()
    catalog["pathways"] = [
        {
            "id": i,
            "label": label,
            "front_page": page,
            "depths": {"full": f.split(), "quick": q.split()},
        }
        for i, label, page, f, q in PATHWAYS
    ]
    (root / "catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return root
