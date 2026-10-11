from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from conftest import FIXTURES, fixture_json
from rbotlib.contract import ContractError, contract_from_dict, load_contract
from rbotlib.rules import Rules


def test_example_contract_loads(rules: Rules) -> None:
    c = load_contract(FIXTURES / "contract_cp_x.json", rules)
    assert c.module_id == "CP-X"
    assert [t.id for t in c.tables] == ["cpx.facts", "snapshot.view"]
    assert c.tables[1].columns[0].scale == "credit_score"
    assert c.inputs[0].kind == "sources" and not c.inputs[0].required


def test_handoff_inputs_respect_required(rules: Rules) -> None:
    data = fixture_json("contract_cp_y.json")
    data["inputs"].append({"handoff": "CP-Z", "required": False, "why": "context"})
    c = contract_from_dict(data, rules)
    assert c.handoff_inputs() == ["CP-X", "CP-Z"]
    assert c.handoff_inputs(required_only=True) == ["CP-X"]


_BREAKS: dict[str, Callable[[dict[str, Any]], None]] = {
    "no_title": lambda d: d.pop("title"),
    "unknown_scale": lambda d: d["tables"][0]["columns"][0].update(scale="stars"),
    "unknown_source": lambda d: d["inputs"][0].update(sources=["rumour"]),
    "no_consumers": lambda d: d["tables"][0].update(consumers=[]),
    "reserved_id": lambda d: d["tables"][0].update(id="citations"),
    "duplicate_table": lambda d: d["tables"].append(copy.deepcopy(d["tables"][0])),
    "duplicate_column": lambda d: d["tables"][0]["columns"].append({"name": "fact"}),
    "two_kinds": lambda d: d["inputs"][0].update(handoff="CP-0"),
    "no_why": lambda d: d["inputs"][0].pop("why"),
    "negative_rows": lambda d: d["tables"][0].update(min_rows=-1),
    "no_process": lambda d: d.update(process=[]),
}


def _broken(change: str) -> dict[str, Any]:
    data = copy.deepcopy(fixture_json("contract_cp_x.json"))
    _BREAKS[change](data)
    return data


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("no_title", "missing title"),
        ("unknown_scale", "unknown scale 'stars'"),
        ("unknown_source", "unknown source class 'rumour'"),
        ("no_consumers", "has no consumers"),
        ("reserved_id", "empty or reserved"),
        ("duplicate_table", "table ids are not unique"),
        ("duplicate_column", "unique, non-empty column names"),
        ("two_kinds", "exactly one of"),
        ("no_why", "has no 'why'"),
        ("negative_rows", "negative min_rows"),
        ("no_process", "process has no steps"),
    ],
)
def test_broken_contracts_name_the_problem(rules: Rules, change: str, message: str) -> None:
    with pytest.raises(ContractError, match=message):
        contract_from_dict(_broken(change), rules)


def test_load_contract_reads_a_file(tmp_path: Path, rules: Rules) -> None:
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(fixture_json("contract_cp_y.json")), encoding="utf-8")
    assert load_contract(path, rules).handoff_inputs() == ["CP-X"]
