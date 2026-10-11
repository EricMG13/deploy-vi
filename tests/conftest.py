"""Shared fixtures: the real rules, the example contracts, a throwaway RBOT tree and the corpus."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

import pytest

from rbotlib.contract import contract_from_dict
from rbotlib.corpus import Problem, load_registry
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, Rules, load_rules

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_json(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return data


@pytest.fixture
def rules() -> Rules:
    return load_rules()


@pytest.fixture
def handoff_text() -> str:
    return (FIXTURES / "handoff_cp_x.md").read_text(encoding="utf-8")


def write_module(root: Path, data: dict[str, Any], rules: Rules) -> None:
    folder = root / "modules" / data["module_id"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "contract.json").write_text(json.dumps(data), encoding="utf-8")
    text = render_module(contract_from_dict(data, rules), rules)
    (folder / "MODULE.md").write_text(text, encoding="utf-8")


def write_catalog(root: Path, **overrides: object) -> None:
    catalog: dict[str, Any] = {
        "size_budget_bytes": 51200,
        "host_tables": {},
        "front_pages": {"fp": {"tables": ["snapshot.view"]}},
        "pathways": [
            {
                "id": "EXAMPLE",
                "label": "Example",
                "front_page": "fp",
                "depths": {"full": ["CP-X", "CP-Y"]},
            }
        ],
    }
    catalog.update(overrides)
    (root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")


@pytest.fixture
def tree(tmp_path: Path, rules: Rules) -> Path:
    """An RBOT folder with the real rules and the two example modules."""
    shutil.copy(RBOT_ROOT / "rules.json", tmp_path / "rules.json")
    (tmp_path / "canon.md").write_text("# Canon\n", encoding="utf-8")
    write_catalog(tmp_path)
    write_module(tmp_path, fixture_json("contract_cp_x.json"), rules)
    write_module(tmp_path, fixture_json("contract_cp_y.json"), rules)
    return tmp_path


CORPUS = load_registry()
REQUIRE_ENV = "RBOT_REQUIRE_CORPUS"


def corpus_gate(problems: list[Problem]) -> None:
    """Fail or skip a corpus test whose files are not usable (interfaces spec section 12.3).

    RBOT_REQUIRE_CORPUS=1 fails on any problem (the owner's machine); =synthetic fails
    only on in-repo files and skips the external ones (CI); otherwise the test skips.
    The message names the unresolved root or the mismatched file either way.
    """
    if not problems:
        return
    message = "; ".join(p.message for p in problems)
    level = os.environ.get(REQUIRE_ENV, "")
    if level == "1" or (level == "synthetic" and any(p.in_repo for p in problems)):
        pytest.fail(message)
    pytest.skip(message)
