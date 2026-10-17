"""`scripts/mutation_workspace.py`: the throwaway workspace the money-code mutation runs use."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

import mutation_workspace as mw


def test_the_workspace_holds_the_package_the_tree_and_the_tests(tmp_path: Path) -> None:
    only, tests = "src/rbotlib/calc/bond_analytics.py", ["tests/test_bond_analytics.py"]
    work = mw.build(only, tests, tmp_path)
    assert work == tmp_path / "money"
    assert (work / "src" / "rbotlib" / "calc" / "bond_analytics.py").is_file()
    assert (work / "modules" / "CP-0" / "contract.json").is_file()
    assert {p.name for p in work.iterdir()} >= {"rules.json", "catalog.json", "canon.md", "tests"}
    config = tomllib.loads((work / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["tool"]["mutmut"]["only_mutate"] == [only]
    assert config["tool"]["mutmut"]["pytest_add_cli_args_test_selection"] == tests
    assert config["tool"]["pytest"]["ini_options"]["pythonpath"] == ["src", "tests"]


def test_main_prints_the_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("tempfile.mkdtemp", lambda prefix: str(tmp_path))
    assert mw.main(["--only", "src/rbotlib/fit_arithmetic.py", "--tests", "tests/test_fit.py"]) == 0
    assert capsys.readouterr().out.strip() == str(tmp_path / "money")
