"""The checker-enforced rules shared by every module, read from rbot/rules.json.

Anything a validator enforces lives here, never only in prose: the MODULE.md
generator prints these same values, so a module prompt and its checker cannot
disagree.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

RBOT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Rules:
    front_matter: tuple[str, ...]
    sections: tuple[str, ...]
    qa_status: tuple[str, ...]
    gap_marker: str
    placeholders: frozenset[str]
    citation_columns: tuple[str, ...]
    source_classes: tuple[str, ...]
    host_producers: tuple[str, ...]
    scales: dict[str, tuple[str, ...]]

    def is_placeholder(self, cell: str) -> bool:
        """True for an empty cell, the gap marker or a listed placeholder."""
        value = cell.strip()
        return not value or value == self.gap_marker or value.casefold() in self.placeholders


def load_rules(root: Path = RBOT_ROOT) -> Rules:
    data = json.loads((root / "rules.json").read_text(encoding="utf-8"))
    handoff = data["handoff"]
    return Rules(
        front_matter=tuple(handoff["front_matter"]),
        sections=tuple(handoff["sections"]),
        qa_status=tuple(handoff["qa_status"]),
        gap_marker=data["gap_marker"],
        placeholders=frozenset(p.casefold() for p in data["placeholders"]),
        citation_columns=tuple(data["citation_columns"]),
        source_classes=tuple(data["source_classes"]),
        host_producers=tuple(data["host_producers"]),
        scales={name: tuple(values) for name, values in data["scales"].items()},
    )
