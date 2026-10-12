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

from credit_model_fixture import example_registers
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
