"""Fail when suppression comments rise above the committed baseline.

Counts `noqa`, `type: ignore`, `nosec` and `pragma: no cover` comments in
every Python file outside reference/, design/ and tool caches. The count may
fall, never rise; lower scripts/suppressions_baseline.txt when it falls.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from pathlib import Path

PATTERN = re.compile(r"#\s*(noqa|type:\s*ignore|nosec|pragma:\s*no cover)")
BASELINE = Path(__file__).with_name("suppressions_baseline.txt")
SKIP = {
    ".git",
    ".venv",
    "reference",
    "design",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}


def count(texts: Iterable[str]) -> int:
    return sum(len(PATTERN.findall(text)) for text in texts)


def python_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if not SKIP.intersection(p.relative_to(root).parts)]


def main(root: Path = Path(), baseline: Path = BASELINE) -> int:
    n = count(p.read_text(encoding="utf-8") for p in python_files(root))
    limit = int(baseline.read_text(encoding="utf-8").strip())
    print(f"{n} suppression(s), baseline {limit}")
    return 1 if n > limit else 0


if __name__ == "__main__":
    sys.exit(main())
