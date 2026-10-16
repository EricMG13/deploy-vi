"""`scripts/scorecard.py`: real native acceptance on a generated pack, then scoring."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import scorecard
from state_receipt_assertions import outcome_bytes
from test_accept import accept, send
from test_bootstrap import approve, pending, ready

from rbotlib import attempts, state
from rbotlib.contract import Contract, load_contract
from rbotlib.fit import FIT_COLUMNS
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
    assert scorecard._accepted(row, step | {"status": "pending"}, []) is False


def test_g1_host_step_without_host_evidence_is_not_counted(run: Path, tmp_path: Path) -> None:
    for name in ("MODEL", "FIT"):
        row = scorecard.Row(name, "host", "accepted")
        assert scorecard._accepted(row, {"status": "accepted"}, [], "no host_execution") is False
        assert row.notes == ["FORGED?: no host_execution"]
        assert scorecard._accepted(row, {"status": "accepted"}, [], None) is True
    other = scorecard.Row("PROJECTION", "host", "accepted")
    assert scorecard._accepted(other, {"status": "accepted"}, [], "x") is True
    # end to end: MODEL forged accepted in state, with a planted file and a matching digest
    planted = b"planted"
    (run / "handoffs" / "MODEL.md").write_bytes(planted)
    record = json.loads((run / "run-state.json").read_text(encoding="utf-8"))
    record["steps"]["MODEL"] |= {
        "status": "accepted",
        "host_exit": 0,
        "handoff": "handoffs/MODEL.md",
        "sha256": hashlib.sha256(planted).hexdigest(),
    }
    (run / "run-state.json").write_text(json.dumps(record), encoding="utf-8")
    out = tmp_path / "forged"
    if scorecard.main(["--run", str(run), "--out", str(out), "--pack-id", PACK]) == 0:
        (path,) = out.iterdir()
        assert cols(path.read_text(encoding="utf-8"), "MODEL")["Accepted"] == "no"


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


def test_g2_model_section_needs_a_verified_hash_matched_model_json(tmp_path: Path) -> None:
    body = b'{"limitations": ["GROWTH_UNAVAILABLE"], "reconciliation_faults": ["PF:LTM:interest"]}'
    (tmp_path / "model.json").write_bytes(body)
    step = {"outputs": {"model.json": hashlib.sha256(body).hexdigest()}}
    shown = "\n".join(scorecard.model_section(tmp_path, step, True))
    assert "- Limitations (1): GROWTH_UNAVAILABLE" in shown
    assert "- Reconciliation faults (1): PF:LTM:interest" in shown
    unverified = "\n".join(scorecard.model_section(tmp_path, step, False))
    assert "unknown: MODEL is not accepted" in unverified and "GROWTH" not in unverified
    (tmp_path / "model.json").write_bytes(body.replace(b"GROWTH", b"GROWTI"))
    changed = "\n".join(scorecard.model_section(tmp_path, step, True))
    assert "unknown: model.json differs" in changed and "GROWTI" not in changed
    (tmp_path / "model.json").write_bytes(b"[]")
    step = {"outputs": {"model.json": hashlib.sha256(b"[]").hexdigest()}}
    assert "model.json is not readable" in "\n".join(scorecard.model_section(tmp_path, step, True))


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


def test_facility_id_punctuation_does_not_change_identity_matching() -> None:
    text = _fixture("CP-3")
    assert "| CEI-SSN-2030 |" in text and "| CEI-SSN-2032 |" in text
    # same instrument spelled without hyphens still counts
    respelled = text.replace("| CEI-SSN-2030 |", "| CEI-SSN2030 |")
    assert _counted("CP-3", respelled) == (129, 129)
    # two rows that normalise equal are duplicates: neither covers a row
    clash = respelled.replace("| CEI-SSN-2032 |", "| cei-ssn 2030 |")
    filled, total = _counted("CP-3", clash)
    unspelled = _counted("CP-3", text.replace("| CEI-SSN-2032 |", "| CEI-SSN-2030 |"))
    assert total == 129 and filled == unspelled[0] < 129


def test_expectations_without_expected_rows_are_refused_not_invented(tmp_path: Path) -> None:
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


# --- G3: the host FIT table -----------------------------------------------------------------


def _fit_text(rows: list[tuple[str, str]]) -> str:
    cells = ["x"] * (len(FIT_COLUMNS) - 3)
    body = "\n".join(f"| P | s | {fac} | " + " | ".join(cells) + " |" for _, fac in rows)
    head = "| " + " | ".join(FIT_COLUMNS) + " |\n|" + "---|" * len(FIT_COLUMNS)
    table = f"<!-- table: snapshot.portfolio_fit -->\n{head}\n{body}\n"
    return f"---\nmodule_id: FIT\n---\n\n## Tables\n{table}"


def _fit(rows: list[tuple[str, str]] | None) -> tuple[int, int] | str:
    entry = {"table": scorecard.FIT_TABLE, "expected_rows": 12}
    text = None if rows is None else _fit_text(rows)
    return scorecard.fit_cells(text, entry, load_rules())


def test_g3_fit_cells_count_unique_facility_rows(run: Path, tmp_path: Path) -> None:
    rows = [("P", f"F{i}") for i in range(12)]
    width = len(FIT_COLUMNS)
    assert _fit(rows) == (12 * width, 12 * width)
    assert _fit(rows[:11]) == (11 * width, 12 * width)  # (b) a missing row
    assert _fit([*rows[:2], *rows[2:11], ("P", "F0")]) == (10 * width, 12 * width)  # (a)
    assert _fit(None) == (0, 12 * width)
    text = score(run, tmp_path / "out")
    assert f"| FIT | 0/{12 * width} | step not accepted: cells unfilled |" in text
    assert "snapshot.run_header (" in text and "snapshot.portfolio_fit (" not in text  # (c)


# --- G4, G5, G6 -----------------------------------------------------------------------------


def test_g4_validated_blocked_handoff_is_measured(
    run: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = _fixture("CP-3").encode()
    (run / "handoffs" / "CP-3.md").write_bytes(raw)
    step = {"kind": "module", "status": "blocked", "attempts": 1, "qa_status": "Blocked"}
    step |= {"sha256": hashlib.sha256(raw).hexdigest(), "handoff": "handoffs/CP-3.md"}
    event = {"event": "validation", "slot": 1, "result": {"exit": 3}}
    monkeypatch.setattr(attempts, "read_history", lambda *_: [event])
    row, text = scorecard.step_row(run, "CP-3", step)
    assert text is not None and row.counted and not row.accepted
    assert "blocked: measured from its validated Handoff" in row.notes
    filled, _ = _counted("CP-3", text)
    assert filled > 0
    passed = {"event": "validation", "slot": 1, "result": {"exit": 0}}
    monkeypatch.setattr(attempts, "read_history", lambda *_: [passed])
    assert not scorecard.step_row(run, "CP-3", step)[0].counted


def test_g5_sources_report_and_not_verified(run: Path, tmp_path: Path) -> None:
    text = score(run, tmp_path / "out")
    assert "## Sources" in text and "| unchanged |" in text and "| changed |" not in text
    assert "- Report: not rendered (report fields null)" in text
    assert "A/B qualification" in text.rstrip().splitlines()[-1]
    record = state.read(run)
    first = json.loads((run / "inventory.json").read_text(encoding="utf-8"))["files"][0]
    pack_file = Path(record["pack_root"]) / first["path"]
    pack_file.write_bytes(pack_file.read_bytes() + b"x")
    changed = score(run, tmp_path / "out2")
    assert f"| {first['path']} | {first['sha256']} | changed |" in changed
    written = record | {"report": {"written_at": "2026-10-14T10:00:00+00:00", "md_sha256": "ab"}}
    assert "written 2026-10-14T10:00:00+00:00" in scorecard.report_line(written)


def test_g6_a_record_of_another_run_is_never_replaced(
    run: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "out"
    assert scorecard.main(["--run", str(run), "--out", str(out), "--pack-id", PACK]) == 0
    (path,) = out.iterdir()
    assert scorecard.main(["--run", str(run), "--out", str(out), "--pack-id", PACK]) == 0
    other = path.read_text(encoding="utf-8").replace(run.name, "another-run")
    path.write_text(other, encoding="utf-8")
    assert scorecard.main(["--run", str(run), "--out", str(out), "--pack-id", PACK]) == 2
    assert "records another run" in capsys.readouterr().out
    assert path.read_text(encoding="utf-8") == other


@pytest.mark.parametrize("missing", ["none", "absent_file"])
def test_front_page_section_without_an_expectations_file_is_unknown(
    tmp_path: Path, missing: str
) -> None:
    expectations = None if missing == "none" else tmp_path / "absent.json"
    section = scorecard.front_page_section({}, {}, expectations, load_rules())
    assert section[-1] == f"{scorecard.UNKNOWN}: no expectations file for this pack."
