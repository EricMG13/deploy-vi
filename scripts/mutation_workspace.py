"""Build the throwaway mutation workspace for Plan 05's money code and print its path.

mutmut 3 names a mutant by its file's path from the working directory, so a run happens in a
workspace where the package sits under `src/` as the tests import it; nothing in the repo is
written. From the repo root:

    WS=$(uv run python scripts/mutation_workspace.py --only "src/rbotlib/calc/*.py" \
        --tests tests/test_bond_analytics.py)
    (cd "$WS" && uv run --project "$OLDPWD" mutmut run && uv run --project "$OLDPWD" mutmut results)
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COPIED = ("rules.json", "catalog.json", "canon.md")


def config(only: str, tests: list[str]) -> str:
    """The workspace's pyproject.toml: pytest paths and the mutmut selection."""
    selection = ", ".join(f'"{t}"' for t in tests)
    copied = ", ".join(f'"{c}"' for c in (*COPIED, "modules"))
    return (
        "[tool.pytest.ini_options]\n"
        'testpaths = ["tests"]\n'
        'pythonpath = ["src", "tests"]\n'
        'addopts = "-q --strict-markers -p no:cacheprovider"\n'
        'markers = ["corpus: reads the local issuer corpus"]\n\n'
        "[tool.mutmut]\n"
        'source_paths = ["src"]\n'
        f'only_mutate = ["{only}"]\n'
        f"also_copy = [{copied}]\n"
        f"pytest_add_cli_args_test_selection = [{selection}]\n"
        "use_git_change_detection = false\n"
    )


def build(only: str, tests: list[str], parent: Path) -> Path:
    """A copy of the package, the RBOT tree's data files and the tests under `parent`."""
    work = parent / "money"
    (work / "src").mkdir(parents=True)
    shutil.copytree(REPO / "rbot" / "scripts" / "rbotlib", work / "src" / "rbotlib")
    shutil.copytree(REPO / "rbot" / "modules", work / "modules")
    shutil.copytree(REPO / "tests", work / "tests")
    for name in COPIED:
        shutil.copy(REPO / "rbot" / name, work / name)
    (work / "pyproject.toml").write_text(config(only, tests), encoding="utf-8")
    return work


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--only", required=True, help="glob of the files to mutate, under src/")
    parser.add_argument("--tests", nargs="+", required=True, help="the test files that judge")
    args = parser.parse_args(argv)
    print(build(args.only, args.tests, Path(tempfile.mkdtemp(prefix="rbot-mutate-"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
