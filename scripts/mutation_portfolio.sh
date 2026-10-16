#!/usr/bin/env bash
# Mutation-test rbotlib/portfolio.py and the sheet functions of rbotlib/prepare.py with mutmut.
# mutmut needs a src/<package> layout, so build a scratch tree (copy of the code, rules and
# tests) and run there. Usage: mutation_portfolio.sh [PARENT]. The scratch folder is made by
# `mktemp -d` inside PARENT (default: $TMPDIR) and is the only thing created; nothing is
# ever deleted, remove the folder when done. PARENT must be an existing folder under a temp
# root, never a temp root itself (/tmp, /var/folders, $TMPDIR ...), the repo or inside it.
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd -P)
refuse() { echo "refusing ${1-}: $2" >&2; exit 2; }
tidy() { local p=$1; p=$(printf '%s' "$p" | tr -s /); while [ "${#p}" -gt 1 ] && [ "${p%/}" != "$p" ]; do p=${p%/}; done; printf '%s' "$p"; }
roots="/tmp /private/tmp /var/tmp /private/var/tmp /var/folders /private/var/folders $(tidy "${TMPDIR:-/tmp}")"
check() { # $1 = an absolute path: not a temp root, not the repo, under a temp root
  local under=0 r
  case "$1" in */../* | */.. | */./* | */. | / ) refuse "$1" "not a plain path" ;; esac
  case "$1" in "$here" | "$here"/*) refuse "$1" "the repo" ;; esac
  for r in $roots; do
    [ "$1" = "$r" ] && refuse "$1" "a temp root itself"
    case "$1" in "$r"/?*) under=1 ;; esac
  done
  [ "$under" = 1 ] || refuse "$1" "not under a temp directory"
}
if [ "$#" -gt 0 ]; then
  parent=$1
  [ -n "$parent" ] || refuse "an empty argument" "give a folder or nothing"
  case "$parent" in /*) ;; *) parent="$PWD/$parent" ;; esac
  parent=$(tidy "$parent")
  check "$parent"
  [ -d "$parent" ] || refuse "$parent" "not a folder"
  check "$(cd "$parent" && pwd -P)"
else
  parent=$(tidy "${TMPDIR:-/tmp}")
fi
work=$(mktemp -d "$parent/rbot-mutation.XXXXXX")
echo "scratch folder: $work"
mkdir -p "$work/src"
cp "$here"/rbot/{rules.json,catalog.json,canon.md} "$work"/
cp -R "$here/rbot/scripts/rbotlib" "$work/src/"
mkdir "$work/tests" && cp -R "$here"/tests/{conftest.py,builders.py,fixtures} "$work/tests/"
mkdir "$work/tests/corpus" && cp -R "$here"/tests/corpus/{corpus.json,synthetic} "$work/tests/corpus/"
cp "$here"/tests/test_{portfolio,portfolio_properties,portfolio_exact,portfolio_fixes,portfolio_fix2,portfolio_fix3}.py "$work/tests/"
cp "$here"/tests/test_{prepare,prepare_fixes,prepare_fix1,prepare_fix2,prepare_fix3,prepare_boundary,sheets,cli,inventory}.py "$work/tests/"
cat > "$work/pyproject.toml" <<TOML
[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
markers = ["corpus: local corpus"]
[tool.mutmut]
source_paths = ["src/rbotlib/portfolio.py", "src/rbotlib/prepare.py", "src/rbotlib/inventory.py", "src/rbotlib/cli.py"]
pytest_add_cli_args_test_selection = ["tests/"]
also_copy = ["src/rbotlib", "rules.json", "catalog.json", "canon.md", "tests"]
pytest_add_cli_args = ["-p", "no:cacheprovider", "-m", "not corpus"]
TOML
# every function of portfolio.py, and the sheet, cell, anchor and PDF-warning functions of prepare.py
prepare_fns="clean_cell cell_text display_scale _scaled_text _section _numeric _trimmed _places
  too_precise conditional_format _load_xlsx _xlsx_cells read_xlsx _sheet_rows _workbook _sheet_pages _drop_surrogates _join_pair
  anchored_text prepared_name read_pdf _sheet_portfolios _drop_orphan _sweep write"
names=("rbotlib.portfolio.*")
for fn in $prepare_fns; do names+=("rbotlib.prepare.x_${fn}__mutmut_*"); done
names+=("rbotlib.inventory.x_output_path__mutmut_*" "rbotlib.inventory.x_write__mutmut_*"
  "rbotlib.cli.x__log__mutmut_*" "rbotlib.cli.x_main__mutmut_*")
cd "$work" && uv run --frozen --project "$here" mutmut run "${names[@]}"
uv run --frozen --project "$here" mutmut results
