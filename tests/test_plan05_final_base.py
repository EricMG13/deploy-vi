"""Real final-base producer/consumer controls; fixture evidence is not model qualification."""

from pathlib import Path

from conftest import FIXTURES
from rbotlib.handoff import parse
from test_cp1 import _model


def test_cp5_closed_ltm_finding_matches_the_actual_model(tmp_path: Path) -> None:
    data = _model(tmp_path, "CP-1", "CP-1D")
    assert data["house"]["structuring_ebitda"]["value"] == "3742"
    assert data["house"]["ssim_ebitda"]["value"] == "3592"
    cp5 = parse((FIXTURES / "handoffs/CP-5.md").read_text("utf-8"))
    table = cp5.tables["cp5.findings"]
    finding = next(
        dict(zip(table.columns, row, strict=True)) for row in table.rows if row[0] == "F-1"
    )
    assert finding["status"] == "Fixed"
    assert "3,742" in finding["description"]
    assert not any(
        "leaves out" in cell for row in cp5.tables["cp5.limitations"].rows for cell in row
    )
    statuses = cp5.tables["cp5.module_status"]
    model = next(
        dict(zip(statuses.columns, row, strict=True)) for row in statuses.rows if row[0] == "MODEL"
    )
    assert model["traceability"] == "Traceable"
    assert "misses" not in model["note"]
