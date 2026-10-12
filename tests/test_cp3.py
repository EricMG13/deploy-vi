"""CP-3's fixture against the calculator and the primary pack's traps.

Every `yield_or_dm` and `implied_*` figure in `tests/fixtures/handoffs/CP-3.md` is
`rbot calc bond_analytics`'s output for `tests/fixtures/calc/CP-3-bond_analytics.json`, so the
Report can recompute it and mark it host-verified (interfaces spec section 11.4). The new
tranche is at Talk and the existing term loan at Market (registry trap and expectation), and
no figure comes from the levels screenshot (an Image-Read Value).
"""

from __future__ import annotations

import json
from typing import Any

from conftest import CORPUS, FIXTURES
from rbotlib.calc.bond_analytics import compute
from rbotlib.handoff import Handoff, parse

CP3 = parse((FIXTURES / "handoffs" / "CP-3.md").read_text(encoding="utf-8"))


def _rows(h: Handoff, table_id: str) -> dict[str, dict[str, str]]:
    table = h.tables[table_id]
    return {r[0]: dict(zip(table.columns, r, strict=True)) for r in table.rows}


def _calc() -> dict[str, Any]:
    data = json.loads((FIXTURES / "calc" / "CP-3-bond_analytics.json").read_text("utf-8"))
    return compute(data)


def test_levels_and_talk_are_the_calculators_figures() -> None:
    result = _calc()
    levels = _rows(CP3, "snapshot.instrument_levels")
    for row in result["levels"]:
        level = levels[row["facility_id"]]
        assert (level["yield_or_dm"], level["metric_basis"]) == (
            row["yield_or_dm"],
            row["metric_basis"],
        )
        assert level["mid"] == row["price"]
        assert f"calc: bond_analytics {row['facility_id']}" in level["cite"]
    talk = _rows(CP3, "cp3.talk_valuation")
    for row in result["talk"]:
        mine = talk[row["facility_id"]]
        keys = (
            "talk_low",
            "talk_mid",
            "talk_high",
            "oid",
            "implied_low",
            "implied_mid",
            "implied_high",
        )
        assert [mine[k] for k in keys] == [row[k] for k in keys]
        assert levels[row["facility_id"]]["yield_or_dm"] == row["implied_mid"]


def test_the_primary_pack_traps_and_expectations_hold() -> None:
    levels = _rows(CP3, "snapshot.instrument_levels")
    pack = CORPUS.pack("czr-2026q2-primary")
    expected = json.loads(
        (FIXTURES.parent / "corpus" / pack.data["expectations"]).read_text("utf-8")
    )
    for value in (v for v in expected["values"] if v["module"] == "CP-3"):
        assert levels[value["where"]["facility_id"]][value["column"]] == value["value"]
    image = next(t["file"] for t in pack.data["traps"] if t["kind"] == "image_read_only")
    assert image not in {r[1] for r in CP3.tables["citations"].rows}
