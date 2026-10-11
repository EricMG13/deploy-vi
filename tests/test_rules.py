from __future__ import annotations

import pytest

from rbotlib.rules import Rules


def test_rules_load_the_handoff_shape_and_house_scales(rules: Rules) -> None:
    assert rules.sections == ("Analysis", "Tables", "Gaps", "Citations")
    assert rules.scales["recommendation"][0] == "1 - Strong OW"
    assert rules.scales["valuation"][-1] == "V5 - Very unattractive"
    assert "MODEL" in rules.host_producers


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        ("", True),
        ("   ", True),
        ("—", True),
        ("TBD", True),
        ("n/a", True),
        ("Insufficient Information", True),
        ("100", False),
        ("3 - Fair", False),
    ],
)
def test_is_placeholder(rules: Rules, cell: str, expected: bool) -> None:
    assert rules.is_placeholder(cell) is expected
