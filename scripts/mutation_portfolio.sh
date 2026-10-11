#!/usr/bin/env bash
# Mutation-test rbotlib/portfolio.py with mutmut. mutmut needs a src/<package> layout, so build
# a scratch tree (copy of the code, rules and tests) and run there. Usage: mutation_portfolio.sh DIR
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
work=${1:?scratch directory}
rm -rf "$work" && mkdir -p "$work/src"
cp "$here"/rbot/{rules.json,catalog.json,canon.md} "$work"/
cp -R "$here/rbot/scripts/rbotlib" "$work/src/"
mkdir "$work/tests" && cp -R "$here"/tests/{conftest.py,builders.py,fixtures} "$work/tests/"
mkdir "$work/tests/corpus" && cp "$here/tests/corpus/corpus.json" "$work/tests/corpus/"
cp "$here"/tests/test_{portfolio,portfolio_properties,portfolio_exact,prepare_fixes,sheets}.py "$work/tests/"
cat > "$work/pyproject.toml" <<TOML
[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
markers = ["corpus: local corpus"]
[tool.mutmut]
source_paths = ["src/rbotlib/portfolio.py"]
pytest_add_cli_args_test_selection = ["tests/"]
also_copy = ["src/rbotlib", "rules.json", "catalog.json", "canon.md", "tests"]
pytest_add_cli_args = ["-p", "no:cacheprovider", "-m", "not corpus"]
TOML
cd "$work" && uv run --frozen --project "$here" mutmut run
uv run --frozen --project "$here" mutmut results
