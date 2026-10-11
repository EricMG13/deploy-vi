from __future__ import annotations

import os
import subprocess
from pathlib import Path

import check_bandit_floor
import check_suppressions

NOQA = "#" + " noqa: E501"
IGNORE = "#" + " type: ignore[arg-type]"


def test_count_finds_every_suppression_kind() -> None:
    text = f"a = 1  {NOQA}\nb = 2  {IGNORE}\nc = 3  #{' nosec'}\nd = 4  #{' pragma: no cover'}\n"
    assert check_suppressions.count([text]) == 4


def test_reference_design_and_caches_are_skipped(tmp_path: Path) -> None:
    for skipped in ("reference", "design"):
        (tmp_path / skipped).mkdir()
        (tmp_path / skipped / "old.py").write_text(f"x = 1  {NOQA}\n")
    (tmp_path / "new.py").write_text("x = 1\n")
    assert [p.name for p in check_suppressions.python_files(tmp_path)] == ["new.py"]


def test_main_fails_only_above_the_baseline(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text(f"x = 1  {NOQA}\n")
    baseline = tmp_path / "baseline.txt"
    baseline.write_text("1\n")
    assert check_suppressions.main(tmp_path, baseline) == 0
    baseline.write_text("0\n")
    assert check_suppressions.main(tmp_path, baseline) == 1


def test_bandit_verdict_floor_findings_and_errors() -> None:
    clean = {"errors": [], "results": [], "metrics": {"_totals": {"loc": 500}}}
    assert check_bandit_floor.verdict(clean) == []
    assert check_bandit_floor.verdict({"metrics": {"_totals": {"loc": 10}}}) == [
        "bandit scanned 10 lines; the floor is 40"
    ]
    dirty = {
        "errors": [{"filename": "x.py"}],
        "results": [
            {"filename": "y.py", "line_number": 3, "test_id": "B101", "issue_text": "assert"}
        ],
        "metrics": {"_totals": {"loc": 500}},
    }
    assert check_bandit_floor.verdict(dirty) == [
        "bandit could not parse x.py",
        "y.py:3 B101 assert",
    ]


def test_bandit_main_reads_a_report(tmp_path: Path) -> None:
    report = tmp_path / "bandit.json"
    report.write_text('{"errors": [], "results": [], "metrics": {"_totals": {"loc": 400}}}')
    assert check_bandit_floor.main([str(report)]) == 0


def _git(repo: Path, *args: str) -> None:
    ident = ["-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "-C", str(repo), *ident, *args], check=True, capture_output=True)


def test_pr_size_ignores_the_corpus_synthetic_packs(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "base")
    pack = tmp_path / "tests" / "corpus" / "synthetic" / "pack"
    pack.mkdir(parents=True)
    (pack / "big.md").write_text("line\n" * 900, encoding="utf-8")
    (tmp_path / "small.py").write_text("x = 1\n" * 10, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "work")
    script = Path(__file__).parents[1] / "scripts" / "check_pr_size.sh"
    env = {**os.environ, "BASE_REF": "HEAD~1"}
    result = subprocess.run(["bash", str(script)], cwd=tmp_path, env=env, capture_output=True)
    assert (result.returncode, result.stdout) == (0, b"10 changed lines (limit 800)\n")
