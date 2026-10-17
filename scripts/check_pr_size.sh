#!/usr/bin/env bash
# PR size gate (global rule): at most 800 changed lines against the base.
# Lock files, the read-only reference copy, the public golden-pack documents
# and the corpus's synthetic packs are data, not authored code
# (docs/decisions/0001-toolchain.md).
set -euo pipefail
base="${BASE_REF:-origin/main}"
n=$(git diff --numstat "$base...HEAD" -- . ':!*.lock' ':!reference/**' ':!tests/golden/**/documents/**' \
  ':!tests/corpus/synthetic/**')
echo "$n" | awk '{s+=$1+$2} END{print s+0 " changed lines (limit 800)"; exit s>800}'
