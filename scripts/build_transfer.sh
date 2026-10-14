#!/usr/bin/env bash
# Build-time POSIX export only; usage: build_transfer.sh PYTHON REPO COMMIT FRESH_OUTPUT [options].
# Exports the commit's transfer inputs and runtime, then runs build_transfer.py on them.
set -euo pipefail
if [ "$#" -lt 4 ]; then
  echo 'usage: build_transfer.sh PYTHON REPO COMMIT FRESH_OUTPUT [--wheels DIR] [--lock FILE]' >&2
  exit 1
fi
py="$1"; out="$4"; commit="$3"; repo_arg="$2"; shift 4
repo="$(git -C "$repo_arg" rev-parse --show-toplevel)"
if ! sha="$(git -C "$repo" rev-parse --verify --end-of-options "$commit^{commit}" 2>/dev/null)"; then
  echo "error: build transfer: unknown commit $commit" >&2
  exit 1
fi
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
stage="$(mktemp -d "${TMPDIR:-/tmp}/rbot-transfer.XXXXXXXX")"
trap 'rm -rf -- "$stage"' EXIT
mkdir "$stage/inputs"
if ! git -C "$repo" archive "$sha" install.sh install.ps1 uv.lock spike/rbot-probe \
  spike/probe-workspace docs/acceptance/work-pc-checklist.md tests/corpus/corpus.json \
  tests/corpus/synthetic | tar -x -C "$stage/inputs"; then
  echo "error: build transfer: required inputs are not committed at ${sha:0:12}" >&2
  exit 1
fi
bash "$here/build_runtime.sh" "$py" "$repo" "$sha" "$stage/runtime"
exec_args=("$here/build_transfer.py" --repo "$repo" --commit "$sha" --out "$out"
  --stage "$stage/inputs" --runtime "$stage/runtime")
"$py" "${exec_args[@]}" "$@"
