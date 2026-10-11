from __future__ import annotations

from pathlib import Path

import pytest

from conftest import FIXTURES
from rbotlib.cli import main


def test_validate_prints_findings_and_returns_the_exit_code(
    tree: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    good = str(FIXTURES / "handoff_cp_x.md")
    assert main(["--root", str(tree), "validate", good, "--module", "CP-X"]) == 0
    assert capsys.readouterr().out == "exit 0\n"
    bad = tmp_path / "bad.md"
    bad.write_text((FIXTURES / "handoff_cp_x.md").read_text().replace("[C1]", ""), encoding="utf-8")
    assert main(["--root", str(tree), "validate", str(bad), "--module", "CP-X"]) == 2
    assert "unused_citation: C1 is never cited" in capsys.readouterr().out


def test_render_module_prints_or_writes(tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tree / "modules" / "CP-Y" / "MODULE.md"
    expected = path.read_text(encoding="utf-8")
    assert main(["--root", str(tree), "render-module", "CP-Y"]) == 0
    assert capsys.readouterr().out == expected
    path.write_text("stale", encoding="utf-8")
    assert main(["--root", str(tree), "render-module", "CP-Y", "--write"]) == 0
    assert path.read_text(encoding="utf-8") == expected


def test_check_returns_1_on_problems(tree: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--root", str(tree), "check"]) == 0
    assert capsys.readouterr().out == "0 problem(s)\n"
    (tree / "modules" / "CP-X" / "MODULE.md").write_text("stale", encoding="utf-8")
    assert main(["--root", str(tree), "check"]) == 1
    assert "1 problem(s)" in capsys.readouterr().out


def test_the_shipped_tree_checks_clean() -> None:
    assert main(["check"]) == 0
