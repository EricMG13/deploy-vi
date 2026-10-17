#!/usr/bin/env bash
# Mutation gate for the Model (money code, interfaces spec section 6.1).
# mutmut 3 names a mutant by its file's path from the working directory, so
# it runs in a throwaway workspace where the package sits under src/ exactly
# as the tests import it (rbotlib.model.*). Nothing in the repo is written.
# Usage: bash scripts/mutate_model.sh [mutant glob ...], e.g. "rbotlib.model.house.*".
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)/model"
mkdir -p "$work/src" "$work/docs"
cp -R "$repo/rbot/scripts/rbotlib" "$work/src/rbotlib"
cp -R "$repo/tests" "$work/tests"
cp -R "$repo/docs/model" "$work/docs/model"
# rbotlib.rules.RBOT_ROOT is two folders above the package: the workspace.
cp "$repo/rbot/rules.json" "$repo/rbot/catalog.json" "$repo/rbot/canon.md" "$work/"
cat > "$work/pyproject.toml" <<'TOML'
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "tests"]
addopts = "-q --strict-markers -p no:cacheprovider"
markers = ["corpus: reads the local issuer corpus"]

[tool.mutmut]
source_paths = ["src"]
only_mutate = ["src/rbotlib/model/*.py"]
also_copy = ["docs", "rules.json", "catalog.json", "canon.md"]
pytest_add_cli_args_test_selection = ["tests/model"]
use_git_change_detection = false
TOML
cd "$work"
echo "mutation workspace: $work"
uv run --project "$repo" mutmut run "$@"
uv run --project "$repo" mutmut results
