"""Model JSON/Markdown fixed-input digests; unchanged calculations and origin."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from credit_model_fixture import example_registers
from ltm_czr_cases import czr_with_synergies, synergy_assessment
from model_handoffs import cp1_handoff, run_brief, run_folder
from run_cases import cp1d_handoff

from rbotlib.model.run import run_model

FIXTURES = Path(__file__).parent / "fixtures"
AT = "2026-10-11T00:00:00+00:00"


def _digests(run: Path) -> dict[str, str]:
    texts = {
        "model.json": (run / "model.json").read_bytes(),
        "MODEL.md": (run / "handoffs" / "MODEL.md").read_bytes(),
    }
    return {name: hashlib.sha256(data).hexdigest() for name, data in texts.items()}


def test_the_example_outputs_are_unchanged(tmp_path: Path) -> None:
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief(), cp1d_handoff())
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "8b1c80a346e2282b00657b596774dec439a1fb57a410359a88286fdd49078ad1",
        "MODEL.md": "fdd663a5b8d902b263a5b1999eb0a5a5d1bf8cd408c01ac3251b0832ae731ad9",
    }


def test_the_czr_outputs_are_unchanged(tmp_path: Path) -> None:
    cp1 = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, cp1, brief)
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "a5dadb6a444f5d30322956114bed7f4fcf2fc1c8e126cf697aaa760a66fc1383",
        "MODEL.md": "e28502639299bd2cc2c034b98432abb98d7c2dc0afc750e0197641b8bc8e5748",
    }


@pytest.mark.parametrize(
    ("status", "verdict", "expected"),
    [
        (
            "UNREALIZED",
            "Challenged",
            {
                "model.json": "2240de32ce0c8797b34d2f6596618848eb6862056242c0eab826986a259f1dc4",
                "MODEL.md": "800871e1c1208cd9d56b0ce04d5377acf9e9ca0c016b2e04991ef2cfc12c361d",
            },
        ),
        (
            "REALIZED",
            "Supported",
            {
                "model.json": "e07877409ef5f7fb38f9351349cbaefae5015395703644b5237e2b2e86f3584d",
                "MODEL.md": "8421f47aedd3bb8c2c73c293a726b880cf178bac17dac66e726fe0e22ebf57c3",
            },
        ),
    ],
)
def test_a14_outputs_pin_both_current_ltm_judgments(
    tmp_path: Path, status: str, verdict: str, expected: dict[str, str]
) -> None:
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, czr_with_synergies(), brief, synergy_assessment(status, verdict))
    run_model(run, AT)
    assert _digests(run) == expected
