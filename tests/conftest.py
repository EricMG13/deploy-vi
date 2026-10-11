"""Shared fixtures: the real rules and the example Handoff."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from rbotlib.rules import Rules, load_rules

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_json(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return data


@pytest.fixture
def rules() -> Rules:
    return load_rules()


@pytest.fixture
def handoff_text() -> str:
    return (FIXTURES / "handoff_cp_x.md").read_text(encoding="utf-8")
