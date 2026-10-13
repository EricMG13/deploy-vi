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
        "model.json": "d294d0e97df95cbd51be152e96197c04a46cda8b9fcdad947beea6b108f54049",
        "MODEL.md": "ab2acb6a73b15f38df293af8d213710d3389fa032b12134e7931e31b7009fd0a",
    }


def test_the_czr_outputs_are_unchanged(tmp_path: Path) -> None:
    cp1 = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, cp1, brief)
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "0d381dd9733a88ade20185f68c56f77d0749b605b0290245d403f699c433306a",
        "MODEL.md": "c8cac47ade480d7c38ce82f0243abff19f4d72184642fca787868cf0c483355f",
    }


@pytest.mark.parametrize(
    ("status", "verdict", "expected"),
    [
        (
            "UNREALIZED",
            "Challenged",
            {
                "model.json": "a474171567027750320ab42d471f53dd9b9febc9bb22bccd095fe68e336e67ed",
                "MODEL.md": "925800330923671ef51e42e7c4a17b9fe9472c3baa0ffdd5a13ab26e70c69eca",
            },
        ),
        (
            "REALIZED",
            "Supported",
            {
                "model.json": "f4d30406a660e3b098617b8cef25a9a529170b856ca71baf755d6b4050dac9ef",
                "MODEL.md": "a0329aafcea953f543082a84920ce2791620cc136498d6a171880e3bcf74d8fb",
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
