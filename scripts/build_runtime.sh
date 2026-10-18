#!/usr/bin/env bash
# Build-time POSIX export only; usage: build_runtime.sh PYTHON REPO COMMIT FRESH_OUTPUT.
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo 'usage: build_runtime.sh PYTHON REPO COMMIT FRESH_OUTPUT' >&2
  exit 1
fi
builder_python="$1"
builder_repo="$(git -C "$2" rev-parse --show-toplevel)"
builder_sha="$(git -C "$builder_repo" rev-parse --verify --end-of-options "$3^{commit}")"
builder_tree="$(git -C "$builder_repo" rev-parse "$builder_sha^{tree}")"
builder_runtime="$(git -C "$builder_repo" rev-parse "$builder_sha:rbot")"
builder_stage="$(mktemp -d "${TMPDIR:-/tmp}/rbot-build.XXXXXXXX")"
trap 'rm -rf -- "$builder_stage"' EXIT
printf '%s\n%s\n%s\n' "$builder_sha" "$builder_tree" "$builder_runtime" > "$builder_stage/identity"
git -C "$builder_repo" cat-file commit "$builder_sha" > "$builder_stage/commit"
git -C "$builder_repo" cat-file tree "$builder_tree" > "$builder_stage/root"
git -C "$builder_repo" ls-tree -rz "$builder_sha:rbot" > "$builder_stage/entries"
# Git attributes may filter/substitute archive bytes; the stamper checks every blob.
# Via a file, not a pipe: tar stops at its end marker and a pipe would SIGPIPE git (exit 141).
git -C "$builder_repo" archive --output "$builder_stage/archive.tar" "$builder_sha" rbot
tar -x -f "$builder_stage/archive.tar" -C "$builder_stage"
rm -f -- "$builder_stage/archive.tar"
builder_here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$builder_python" "$builder_here/build_runtime.py" --repo "$builder_repo" \
  --stage "$builder_stage" --out "$4"
