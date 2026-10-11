"""Bandit's verdict with a scan floor.

Run `bandit -r rbot/scripts scripts -f json -o bandit.json` first (its own
exit code is ignored there); this fails on any finding, any file bandit could
not parse, or a scan that covered fewer lines than the floor, so a scan that
silently read nothing never passes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MIN_LOC = 40


def verdict(report: dict[str, Any], min_loc: int = MIN_LOC) -> list[str]:
    problems = [f"bandit could not parse {e.get('filename')}" for e in report.get("errors", [])]
    problems += [
        f"{r['filename']}:{r['line_number']} {r['test_id']} {r['issue_text']}"
        for r in report.get("results", [])
    ]
    loc = int(report.get("metrics", {}).get("_totals", {}).get("loc", 0))
    if loc < min_loc:
        problems.append(f"bandit scanned {loc} lines; the floor is {min_loc}")
    return problems


def main(argv: list[str]) -> int:
    problems = verdict(json.loads(Path(argv[0]).read_text(encoding="utf-8")))
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
