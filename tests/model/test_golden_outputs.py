"""`rbot model`'s three files on two fixed inputs, pinned by digest: the caos
example with a CP-1D Handoff, and the CZR CP-1 fixture (no CP-1D).

A characterisation gate (the mutation gate's findings on the output
modules): any change to a byte of model.json or MODEL.md, or to a value in
model.xlsx (or its number format), fails here. Regenerate a digest only for an intended change and
say in the commit which output changed and why; model.xlsx is compared by
its cell values because openpyxl stamps the file with the time it wrote it.
"""

from __future__ import annotations

import hashlib
import json
from io import BytesIO
from pathlib import Path

import pytest
from credit_model_fixture import example_registers
from ltm_czr_cases import czr_with_synergies, synergy_assessment
from model_handoffs import cp1_handoff, run_brief, run_folder
from openpyxl import load_workbook
from run_cases import cp1d_handoff

from rbotlib.model.run import run_model

FIXTURES = Path(__file__).parent / "fixtures"
AT = "2026-10-11T00:00:00+00:00"


def _digests(run: Path) -> dict[str, str]:
    book = load_workbook(BytesIO((run / "model.xlsx").read_bytes()))
    cells = {
        s.title: [[f"{c.value}|{c.number_format}" for c in row] for row in s.iter_rows()]
        for s in book
    }
    texts = {
        "model.json": (run / "model.json").read_bytes(),
        "MODEL.md": (run / "handoffs" / "MODEL.md").read_bytes(),
        "model.xlsx": json.dumps(cells, sort_keys=True).encode("utf-8"),
    }
    return {name: hashlib.sha256(data).hexdigest() for name, data in texts.items()}


def test_the_example_outputs_are_unchanged(tmp_path: Path) -> None:
    run = run_folder(tmp_path, cp1_handoff(example_registers()), run_brief(), cp1d_handoff())
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "d294d0e97df95cbd51be152e96197c04a46cda8b9fcdad947beea6b108f54049",
        "MODEL.md": "ab2acb6a73b15f38df293af8d213710d3389fa032b12134e7931e31b7009fd0a",
        "model.xlsx": "1a6201992212f06547bf0c355242682001579f159fec622527746586b4521193",
    }


def test_the_czr_outputs_are_unchanged(tmp_path: Path) -> None:
    cp1 = (FIXTURES / "cp1_czr_2026q2.md").read_text(encoding="utf-8")
    brief = (FIXTURES / "run_brief_czr.md").read_text(encoding="utf-8")
    run = run_folder(tmp_path, cp1, brief)
    run_model(run, AT)
    assert _digests(run) == {
        "model.json": "0d381dd9733a88ade20185f68c56f77d0749b605b0290245d403f699c433306a",
        "MODEL.md": "c8cac47ade480d7c38ce82f0243abff19f4d72184642fca787868cf0c483355f",
        "model.xlsx": "eef46f489bb52f1c9c460b8d7bf8148bd215b5f5de2a584288c362bf5718a8f2",
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
                "model.xlsx": "da4de95c99cc65ceea17802820ffc8b9251491cf065761983c7ed24161aded17",
            },
        ),
        (
            "REALIZED",
            "Supported",
            {
                "model.json": "f4d30406a660e3b098617b8cef25a9a529170b856ca71baf755d6b4050dac9ef",
                "MODEL.md": "a0329aafcea953f543082a84920ce2791620cc136498d6a171880e3bcf74d8fb",
                "model.xlsx": "45c79dd3c302100ce70616a57c088d67e3ec6887869ab8dcf5e5823be7eb8298",
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
