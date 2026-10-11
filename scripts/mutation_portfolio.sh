#!/usr/bin/env bash
# Mutation-test rbotlib/portfolio.py and the sheet functions of rbotlib/prepare.py with mutmut.
# mutmut needs a src/<package> layout, so build a scratch tree (copy of the code, rules and
# tests) and run there. Usage: mutation_portfolio.sh DIR   (DIR must be a new folder under a
# temp directory; it is deleted first).
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
work=${1:?scratch directory}
case "$work" in /*) ;; *) work="$PWD/$work" ;; esac
case "$work" in
  */../* | */.. | */./* | */. | "$here" | "$here"/*) echo "refusing $work" >&2; exit 2 ;;
  /tmp/?* | /private/tmp/?* | /var/folders/?* | /private/var/folders/?*) ;;
  *) echo "refusing $work: not under a temp directory" >&2; exit 2 ;;
esac
rm -rf "$work" && mkdir -p "$work/src"
cp "$here"/rbot/{rules.json,catalog.json,canon.md} "$work"/
cp -R "$here/rbot/scripts/rbotlib" "$work/src/"
mkdir "$work/tests" && cp -R "$here"/tests/{conftest.py,builders.py,fixtures} "$work/tests/"
mkdir "$work/tests/corpus" && cp -R "$here"/tests/corpus/{corpus.json,synthetic} "$work/tests/corpus/"
cp "$here"/tests/test_{portfolio,portfolio_properties,portfolio_exact,portfolio_fixes}.py "$work/tests/"
cp "$here"/tests/test_{prepare_fixes,prepare_fix1,sheets}.py "$work/tests/"
cat > "$work/pyproject.toml" <<TOML
[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
markers = ["corpus: local corpus"]
[tool.mutmut]
source_paths = ["src/rbotlib/portfolio.py", "src/rbotlib/prepare.py"]
pytest_add_cli_args_test_selection = ["tests/"]
also_copy = ["src/rbotlib", "rules.json", "catalog.json", "canon.md", "tests"]
pytest_add_cli_args = ["-p", "no:cacheprovider", "-m", "not corpus"]
TOML
# every function of portfolio.py, and the sheet, cell, anchor and PDF-warning functions of prepare.py
prepare_fns="clean_cell cell_text display_scale _scaled_text _section _numeric _trimmed
  _sheet_rows _workbook _sheet_pages _drop_surrogates anchored_text read_pdf _sheet_portfolios"
names=("rbotlib.portfolio.*")
for fn in $prepare_fns; do names+=("rbotlib.prepare.x_${fn}__mutmut_*"); done
cd "$work" && uv run --frozen --project "$here" mutmut run "${names[@]}"
uv run --frozen --project "$here" mutmut results
