"""`scripts/scorecard.py`: real native acceptance on a generated pack, then scoring."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import scorecard
from state_receipt_assertions import outcome_bytes
from test_accept import accept, send
from test_bootstrap import approve, pending, ready

from rbotlib import state
from rbotlib.contract import Contract, load_contract
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT, load_rules

PACK = "czr-2026q2-primary"
EXPECTATIONS = Path(__file__).parent / "corpus" / "expectations"
HANDOFFS = Path(__file__).parent / "fixtures" / "handoffs"


def snapshot(run: Path) -> dict[str, bytes]:
    return {str(p.relative_to(run)): p.read_bytes() for p in sorted(run.rglob("*")) if p.is_file()}


@pytest.fixture
def run(tmp_path: Path) -> Path:
    """An approved run whose CP-0 was accepted through the real dispatch and accept path."""
    pre = pending(tmp_path, RBOT_ROOT)
    send(pre, RBOT_ROOT)
    assert accept(pre) == 0
    ready(pre, RBOT_ROOT)
    return approve(pre, RBOT_ROOT)


def score(run: Path, out: Path) -> str:
    assert scorecard.main(["--run", str(run), "--out", str(out), "--pack-id", PACK]) == 0
    (path,) = out.iterdir()
    return path.read_text(encoding="utf-8")


def table_row(text: str, step: str) -> list[str]:
    line = next(x for x in text.splitlines() if x.startswith(f"| {step} |"))
    return [c.strip() for c in line.strip("|").split("|")]


COLUMNS = (
    "Step Kind Status Accepted QA Attempts Exits Citations Image Gaps Bytes Started "
    "Finished Duration Model Notes"
).split()


def cols(text: str, step: str) -> dict[str, str]:
    return dict(zip(COLUMNS, table_row(text, step), strict=True))


def test_accepted_run_reports_measured_ratios_and_unknowns(run: Path, tmp_path: Path) -> None:
    text = score(run, tmp_path / "out")
    cp0 = cols(text, "CP-0")
    assert (cp0["Status"], cp0["Accepted"], cp0["Exits"], cp0["Citations"]) == (
        "accepted",
        "yes",
        "1:0",
        "1/1",
    )
    assert cp0["Image"] == "0" and cp0["Model"] == "unknown"
    assert "worker start time unknown" in cp0["Notes"]
    pending_row = cols(text, "CP-1")
    assert pending_row["Status"] == "pending" and pending_row["Accepted"] == "no"
    assert {pending_row[k] for k in ("Attempts", "Citations", "Gaps", "Started", "Model")} == {
        "unknown"
    }
    assert "Steps accepted (verified): 1/11" in text
    assert "| CP-3 | 0/129 | step not accepted: cells unfilled |" in text
    assert "unknown: model.json is not in the run." in text
    assert text.rstrip().splitlines()[-1].startswith("Not verified: Copilot behaviour")
    assert "GPT models" in text and "fetch" in text


def test_output_path_naming_and_default_pack_id(run: Path, tmp_path: Path) -> None:
    out = tmp_path / "docs" / "corpus-runs"
    assert scorecard.main(["--run", str(run), "--out", str(out), "--pack-id", PACK]) == 0
    created = state.read(run)["created_at"][:10]
    assert [p.name for p in out.iterdir()] == [f"{created}-{PACK}-full-credit-assessment-full.md"]
    assert scorecard.pack_id_of({"pack_root": "/x/corpus-runs/p1/pack"}) == "p1"
    assert scorecard.pack_id_of({"pack_root": "/x/mypack"}) == "mypack"


def test_run_folder_is_unchanged_and_an_out_inside_it_is_refused(
    run: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before, state_bytes = snapshot(run), outcome_bytes(run)
    score(run, tmp_path / "out")
    assert snapshot(run) == before and outcome_bytes(run) == state_bytes
    assert scorecard.main(["--run", str(run), "--out", str(run / "handoffs")]) == 2
    assert "--out must be outside the run folder" in capsys.readouterr().out
    assert snapshot(run) == before


def test_handoff_edited_after_acceptance_is_not_counted_accepted(run: Path, tmp_path: Path) -> None:
    path = run / "handoffs" / "CP-0.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nedited after acceptance\n")
    text = score(run, tmp_path / "out")
    cp0 = cols(text, "CP-0")
    assert cp0["Status"] == "accepted" and cp0["Accepted"] == "no"
    assert "MISMATCH: Handoff bytes differ from the recorded digest" in cp0["Notes"]
    assert cp0["Citations"] == "unknown" and "Steps accepted (verified): 0/11" in text


def test_a_deleted_handoff_is_not_counted_accepted(run: Path, tmp_path: Path) -> None:
    (run / "handoffs" / "CP-0.md").unlink()
    cp0 = cols(score(run, tmp_path / "out"), "CP-0")
    assert cp0["Accepted"] == "no" and "Handoff file missing" in cp0["Notes"]


def test_state_edit_without_validation_evidence_cannot_count(run: Path, tmp_path: Path) -> None:
    """A forged terminal state plus a file that exists is not acceptance."""
    step = {"kind": "module", "status": "accepted", "attempts": 1, "qa_status": "Pass"}
    raw = (run / "handoffs" / "CP-0.md").read_bytes()
    step |= {"handoff": "handoffs/CP-1.md", "sha256": hashlib.sha256(raw).hexdigest()}
    step |= {"validate_exit": 0}
    (run / "handoffs" / "CP-1.md").write_bytes(raw)
    row = scorecard.Row("CP-1", "module", "accepted")
    assert scorecard._accepted(row, step, []) is False
    assert "FORGED?" in row.notes[0]
    host = scorecard.Row("MODEL", "host", "accepted")
    assert scorecard._accepted(host, {"status": "accepted"}, []) is True
    assert scorecard._accepted(row, step | {"status": "pending"}, []) is False


def test_a_wrong_citation_changes_the_measured_ratio(run: Path) -> None:
    text = (run / "handoffs" / "CP-0.md").read_text(encoding="utf-8")
    assert "| C1 | acme_10k.txt | p. 1 | Acme Holdings, Inc. |" in text
    good = scorecard.citations(parse(text), run)
    assert good is not None and good.text() == "1/1"
    wrong = text.replace(
        "| C1 | acme_10k.txt | p. 1 | Acme Holdings, Inc. |",
        "| C1 | acme_10k.txt | p. 1 | Beta Corporation never appears here |",
    )
    bad = scorecard.citations(parse(wrong), run)
    assert bad is not None and bad.text() == "0/1" and bad.total == 1
    unknown_source = wrong.replace("acme_10k.txt | p. 1", "nope.txt | p. 1")
    missing = scorecard.citations(parse(unknown_source), run)
    assert missing is not None and missing.anchored == 0


def test_image_read_citations_are_counted_apart_never_as_anchored(
    run: Path, tmp_path: Path
) -> None:
    import json

    index = run / "prepared" / "index.json"
    data = json.loads(index.read_text(encoding="utf-8"))
    for record in data["files"]:
        if record["path"] == "acme_10k.txt":
            record["image_read"] = True
    index.write_text(json.dumps(data), encoding="utf-8")
    text = (run / "handoffs" / "CP-0.md").read_text(encoding="utf-8")
    cited = scorecard.citations(parse(text), run)
    assert cited is not None and (cited.anchored, cited.image_read, cited.total) == (0, 1, 1)
    index.write_text("not json", encoding="utf-8")
    assert scorecard.citations(parse(text), run) is None


def test_unreadable_prepared_sources_make_the_ratio_unknown(run: Path, tmp_path: Path) -> None:
    (run / "prepared" / "index.json").unlink()
    cp0 = cols(score(run, tmp_path / "out"), "CP-0")
    assert cp0["Citations"] == "unknown" and "citations unverifiable" in cp0["Notes"]


def test_unknown_times_are_never_zero() -> None:
    assert scorecard.duration("unknown", "unknown") == "unknown"
    assert scorecard.duration("2026-10-14T10:00:00+00:00", "2026-10-14T09:00:00+00:00") == "unknown"
    assert scorecard.duration("2026-10-14T10:00:00+00:00", "2026-10-14T10:01:30+00:00") == "90s"


def test_model_limitations_and_faults_are_reported(run: Path, tmp_path: Path) -> None:
    (run / "model.json").write_text(
        '{"limitations": ["GROWTH_UNAVAILABLE"], "reconciliation_faults": ["PF:LTM:interest"]}'
    )
    text = score(run, tmp_path / "out")
    assert "- Limitations (1): GROWTH_UNAVAILABLE" in text
    assert "- Reconciliation faults (1): PF:LTM:interest" in text
    (run / "model.json").write_text("[]")
    assert "model.json is not readable" in score(run, tmp_path / "out2")


# --- Front Page coverage (Plan 06.15): row identities, not row counts ----------------------


def _contract(module: str) -> Contract:
    return load_contract(RBOT_ROOT / "modules" / module / "contract.json", load_rules())


def _fill(module: str, text: str | None) -> tuple[int, int] | str | None:
    expectations = EXPECTATIONS / f"{PACK}.json"
    return scorecard.front_page_text(_contract(module), text, expectations, load_rules())


def _counted(module: str, text: str | None) -> tuple[int, int]:
    result = _fill(module, text)
    assert isinstance(result, tuple)
    return result


def _fixture(module: str) -> str:
    return (HANDOFFS / f"{module}.md").read_text(encoding="utf-8")


def test_fixture_handoffs_fill_every_supportable_cell_and_a_missing_one_counts_zero() -> None:
    assert _fill("CP-3", _fixture("CP-3")) == (129, 129)
    assert _fill("CP-6", _fixture("CP-6")) == (15, 15)
    assert _fill("CP-3", None) == (0, 129)  # not accepted: the cells are unfilled
    assert _fill("CP-0", _fixture("CP-0")) is None  # owns no Front Page table


def test_a_duplicated_strategy_row_lowers_coverage() -> None:
    row = (
        "| CLO | 3 - MW | Full | the new first-lien term loan at talk pays for the added "
        "secured debt; existing loans do not | "
        "calc: CP-6 snapshot.instrument_recommendation NEW-1 |"
    )
    text = _fixture("CP-6")
    assert row in text
    # a duplicated CLO row replaces the Indexed Loans row: three rows, one identity missing
    swapped = "\n".join(
        row if line.startswith("| Indexed Loans |") else line for line in text.splitlines()
    )
    filled, total = _counted("CP-6", swapped)
    assert total == 15 and filled < total


def test_a_duplicated_facility_row_lowers_coverage() -> None:
    text = _fixture("CP-3")
    lines = text.splitlines()
    tlb = next(line for line in lines if line.startswith("| CEI-TLB |"))
    other = next(line for line in lines if line.startswith("| CEI-TLB-1 |"))
    filled, total = _counted("CP-3", text.replace(other, tlb))
    assert total == 129 and filled < total


def test_expectations_without_expected_rows_are_refused_not_invented(tmp_path: Path) -> None:
    import json

    data = json.loads((EXPECTATIONS / f"{PACK}.json").read_text(encoding="utf-8"))
    for page in data["front_pages"].values():
        for entry in page["supportable"]:
            entry.pop("expected_rows", None)
            entry.pop("expected_identities", None)
    path = tmp_path / "exp.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    for text in (_fixture("CP-3"), None):
        result = scorecard.front_page_text(_contract("CP-3"), text, path, load_rules())
        assert isinstance(result, str) and result.startswith("refused:")


def test_no_citation_rows_is_an_unknown_ratio_not_zero_over_zero(run: Path) -> None:
    text = (run / "handoffs" / "CP-0.md").read_text(encoding="utf-8")
    cut = "\n".join(line for line in text.splitlines() if not line.startswith("| C1 |"))
    cited = scorecard.citations(parse(cut), run)
    assert cited is not None and cited.total == 0
    assert cited.text() == "unknown (no citation rows)"
