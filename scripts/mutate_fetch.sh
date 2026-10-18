#!/usr/bin/env bash
# Mutation gate for the fetch core (security code, Plan 10): rbotlib/fetch.py and fetched.py.
# mutmut 3 names a mutant by its file's path from the working directory, so
# it runs in a throwaway workspace where the package sits under src/ exactly
# as the tests import it (rbotlib.*). Nothing in the repo is written.
# Usage: bash scripts/mutate_fetch.sh [mutant glob ...], e.g. "rbotlib.fetch.*".
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)/fetch"
mkdir -p "$work/src"
cp -R "$repo/rbot/scripts/rbotlib" "$work/src/rbotlib"
# tests/conftest.py imports rbotlib.cli, which imports the launcher module `rbot`.
cp "$repo/rbot/scripts/rbot.py" "$work/src/rbot.py"
cp -R "$repo/tests" "$work/tests"
# rbotlib.rules.RBOT_ROOT is two folders above the package: the workspace.
cp "$repo/rbot/rules.json" "$repo/rbot/catalog.json" "$repo/rbot/canon.md" "$work/"
# tests/spec_fixture.build_tree (the fetch command tests) copies the real CP-0 module.
mkdir -p "$work/modules"
cp -R "$repo/rbot/modules/CP-0" "$work/modules/CP-0"
cat > "$work/pyproject.toml" <<'TOML'
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "tests"]
addopts = "-q --strict-markers -p no:cacheprovider"
markers = ["corpus: reads the local issuer corpus"]

[tool.mutmut]
source_paths = ["src"]
only_mutate = ["src/rbotlib/fetch.py", "src/rbotlib/fetched.py"]
also_copy = ["rules.json", "catalog.json", "canon.md", "modules"]
pytest_add_cli_args_test_selection = ["tests/test_fetch_policy.py", "tests/test_fetch.py", "tests/test_fetch_save.py", "tests/test_fetch_guard.py", "tests/test_fetched.py", "tests/test_fetch_cli.py"]
use_git_change_detection = false
TOML
cd "$work"
echo "mutation workspace: $work"
uv run --project "$repo" mutmut run "$@"
uv run --project "$repo" mutmut results
