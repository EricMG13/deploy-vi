#!/usr/bin/env bash
# Extracted-install smoke (P2, P3); usage: smoke_transfer.sh ZIP PYTHON311.
# Unzips the transfer package under a path with a space, installs offline, runs the native flow.
# Prints each command with its exit; any failure exits non-zero. Scratch is removed on exit.
set -euo pipefail
if [ "$#" -ne 2 ] || [ ! -f "$1" ]; then
  echo 'usage: smoke_transfer.sh ZIP PYTHON311' >&2
  exit 2
fi
zip="$(cd -- "$(dirname -- "$1")" && pwd)/$(basename -- "$1")"
base_py="$2"
work="$(mktemp -d "${TMPDIR:-/tmp}/rbot smoke.XXXXXXXX")"
work="$(cd -- "$work" && pwd -P)"  # install.sh refuses symlinked paths (macOS /var)
trap 'rm -rf -- "$work"' EXIT
pkg="$work/package dir"; dest="$work/installed skill"; venv="$work/venv"; pack="$work/pack copy"

# step DESCRIPTION CMD...: print the command, run it, print its exit; stop on non-zero.
step() {
  local what="$1" code=0
  shift
  echo "+ [$what] $*"
  "$@" || code=$?
  echo "  exit $code"
  if [ "$code" -ne 0 ]; then
    echo "FAIL: $what" >&2
    exit "$code"
  fi
}
fail() { echo "FAIL: $*" >&2; exit 1; }
rbot() { "$venv/bin/python" "$dest/scripts/rbot.py" "$@"; }

step "unzip to a path with a space" unzip -q "$zip" -d "$pkg"

# Every manifest file hashes as listed and no other file is present.
check_manifest() {
  "$base_py" -I - "$pkg" <<'PY'
import hashlib, json, sys
from pathlib import Path

root = Path(sys.argv[1])
listed = json.loads((root / "MANIFEST.json").read_text())["files"]
found = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} - {"MANIFEST.json"}
bad = sorted(n for n, h in listed.items() if hashlib.sha256((root / n).read_bytes()).hexdigest() != h)
if bad or found != set(listed):
    sys.exit(f"manifest mismatch: changed {bad[:5]}, extra {sorted(found - set(listed))[:5]}")
print(f"{len(listed)} files match MANIFEST.json")
PY
}
step "manifest matches the extracted files" check_manifest

step "build the venv" "$base_py" -m venv "$venv"
step "offline wheel install" "$venv/bin/python" -m pip install -q --no-index \
  --find-links "$pkg/wheels" pypdf==6.19.0 openpyxl==3.1.5
step "run install.sh" bash "$pkg/install.sh" "$pkg/rbot" "$dest" "$venv/bin/python"
second="$(step "repeat install.sh" bash "$pkg/install.sh" "$pkg/rbot" "$dest" "$venv/bin/python")"
echo "$second"
case "$second" in *"Already installed"*) ;; *) fail "second install was not a no-op" ;; esac

for entry in "$dest"/* "$dest"/.[!.]*; do
  [ -e "$entry" ] || continue
  case "${entry##*/}" in
    SKILL.md | canon.md | catalog.json | rules.json | runtime.json | modules | report | scripts) ;;
    *) fail "installed tree holds more than the runtime: ${entry##*/}" ;;
  esac
done

cd /
step "version from /" rbot version
step "check from /" rbot check

cp -R "$pkg/pack/czr-2026q2-primary" "$pack"
newrun="$(step "new-run" rbot new-run --pack "$pack")"
echo "$newrun"
run_dir="$(printf '%s\n' "$newrun" | grep -E '/rbot-runs/' | tail -n 1)"
[ -d "$run_dir" ] || fail "new-run printed no run folder"
step "inventory" rbot inventory --run "$run_dir"
step "prepare" rbot prepare --run "$run_dir"
next="$(step "next" rbot next --run "$run_dir")"
echo "$next"
dispatch="$(printf '%s\n' "$next" | grep '^{' | "$venv/bin/python" -c '
import json, sys
reply = json.loads(sys.stdin.read())
assert reply["step"] == "CP-0" and reply["kind"] == "module", reply
print(reply["dispatch"])')"
[ -f "$run_dir/$dispatch" ] || fail "dispatch file $dispatch is missing"

budget="$("$venv/bin/python" -c 'import json,sys; print(json.load(open(sys.argv[1]))["size_budget_bytes"])' "$dest/catalog.json")"
echo "size_budget_bytes $budget"
for file in "$dest/SKILL.md" "$dest/canon.md" "$dest"/modules/*/MODULE.md "$run_dir/$dispatch"; do
  size="$(wc -c <"$file" | tr -d ' ')"
  echo "  $size bytes  ${file#"$work"/}"
  [ "$size" -le "$budget" ] || fail "$file is $size bytes, over $budget"
done

# The pack copy matches the shipped pack apart from the run folder; the shipped pack is unchanged.
step "pack copy unchanged apart from rbot-runs" diff -r -x rbot-runs "$pkg/pack/czr-2026q2-primary" "$pack"
step "shipped files still match the manifest" check_manifest
echo "SMOKE PASS: $zip"
