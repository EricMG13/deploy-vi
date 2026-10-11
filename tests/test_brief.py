from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.handoff import Handoff, markers, parse
from rbotlib.validate import run_findings

CP0 = FIXTURES / "handoff_cp0_czr_primary.md"


def _run(tmp_path: Path) -> Path:
    run = make_run(tmp_path / "pack", "20261011-czr-pending")
    (run / "handoffs").mkdir()
    shutil.copy(CP0, run / "handoffs" / "CP-0.md")
    return run


def _brief(run: Path) -> Handoff:
    return parse((run / "run-brief.md").read_text(encoding="utf-8"))


def _fields(h: Handoff) -> dict[str, list[str]]:
    return {row[0]: row[1:] for row in h.tables["brief.run_brief_fields"].rows}


def test_from_cp0_prefills_every_table(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run = _run(tmp_path)
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert capsys.readouterr().out == "run-brief.md: written\n"
    h = _brief(run)
    assert (
        h.front_matter["module_id"] == "RUN_BRIEF" and h.front_matter["qa_status"] == "Restricted"
    )
    assert h.sections == ["Analysis", "Tables", "Gaps", "Citations"]
    header = dict(
        zip(
            h.tables["snapshot.run_header"].columns,
            h.tables["snapshot.run_header"].rows[0],
            strict=True,
        )
    )
    assert (header["run_id"], header["issuer_id"], header["primary"]) == (
        "20261011-czr-pending",
        "CZR",
        "Yes",
    )
    assert (header["pathway"], header["report_date"]) == ("—", "—")
    tranche = dict(
        zip(
            h.tables["snapshot.transaction_summary"].columns,
            h.tables["snapshot.transaction_summary"].rows[0],
            strict=True,
        )
    )
    assert (tranche["tranche_id"], tranche["size"], tranche["status"]) == (
        "NEW-1",
        "3000",
        "Sourced",
    )
    assert (tranche["bloomberg_id"], tranche["cr_score"]) == ("—", "—")
    assert tranche["cite"].split()[:3] == ["[C4]", "[C3]", "[C5]"]
    fields = _fields(h)
    assert fields["issuer"] == ["Caesars Entertainment, Inc.", "Sourced", "—", "[C1]"]
    assert fields["analyst"] == ["—", "Gap", "—", "—"]
    assert h.tables["brief.portfolios"].rows[0][-1] == "prepared/portfolios/TEST_CLO_I.json"
    assert h.tables["brief.research_questions"].rows == [
        ["RQ-1", "How is Las Vegas Strip visitation trending into 2027?", "CP-2", "Yes"]
    ]
    assert h.tables["brief.prior_case"].rows == []
    assert "- `objective`: not found in the Source Pack" in h.body


def test_citations_are_the_cited_cp0_rows_only(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    h = _brief(run)
    ids = [row[0] for row in h.tables["citations"].rows]
    assert ids == [f"C{n}" for n in range(1, 16)]
    assert markers(h.body) == set(ids)


def test_source_wins_and_edits_survive_a_rebuild(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    edits = [
        "issuer=Caesars",
        "analyst=A. Analyst",
        "objective=New issue review",
        "ssim_ev_multiple=8.5x",
    ]
    assert main(["brief", "--run", str(run), *[a for e in edits for a in ("--set", e)]]) == 0
    fields = _fields(_brief(run))
    assert fields["issuer"] == ["Caesars Entertainment, Inc.", "Sourced", "Caesars", "[C1]"]
    assert fields["analyst"] == ["A. Analyst", "Analyst-asserted", "A. Analyst", "—"]
    assert fields["ssim_ev_multiple"][0] == "8.5"
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    h = _brief(run)
    assert _fields(h)["analyst"][0] == "A. Analyst" and h.front_matter["qa_status"] == "Pass"
    assert h.tables["snapshot.run_header"].rows[0][12] == "8.5x"


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        ("pathway=RELATIVE_VALUE", "pathway is set by rbot approve"),
        ("sector=Gaming", "unknown field 'sector'"),
        ("primary=maybe", "primary must be one of ('Yes', 'No')"),
        ("as_of_date=02/10/2026", "as_of_date must be YYYY-MM-DD"),
        ("ssim_ev_multiple=high", "ssim_ev_multiple must be a number"),
        ("analyst", "unknown field 'analyst'"),
    ],
)
def test_refused_edits_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit: str, message: str
) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--set", edit]) == 1
    assert message in capsys.readouterr().out


def test_show_prints_the_brief_and_needs_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    assert main(["brief", "--run", str(run), "--show"]) == 1
    assert (
        "no run-brief.md; run rbot brief --from handoffs/CP-0.md first" in capsys.readouterr().out
    )
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--show"]) == 0
    assert capsys.readouterr().out == (run / "run-brief.md").read_text(encoding="utf-8")


def test_a_bad_prefill_or_missing_cp0_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(CP0.read_text(encoding="utf-8").replace("| oid | NEW-1", "| margin | NEW-1"))
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 1
    assert "'margin' is not a tranche field" in capsys.readouterr().out
    cp0.write_text(CP0.read_text(encoding="utf-8").replace("| issuer_id | |", "| ticker | |"))
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 1
    assert "unknown field 'ticker'" in capsys.readouterr().out
    cp0.unlink()
    assert main(["brief", "--run", str(run), "--set", "analyst=A"]) == 1


@pytest.mark.corpus
def test_brief_citations_anchor_in_the_primary_pack(prepared_run: Callable[[str], Path]) -> None:
    run = prepared_run("czr-2026q2-primary")
    (run / "handoffs").mkdir(exist_ok=True)
    shutil.copy(CP0, run / "handoffs" / "CP-0.md")
    assert run_findings(parse(CP0.read_text(encoding="utf-8")), run) == []
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert run_findings(_brief(run), run) == []


def test_a_pipe_in_a_value_round_trips_escaped(tmp_path: Path) -> None:
    run = _run(tmp_path)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(CP0.read_text(encoding="utf-8").replace("Ba3 / BB-", r"Ba3 \| BB-"))
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert r"| Ba3 \| BB- |" in (run / "run-brief.md").read_text(encoding="utf-8")
    table = _brief(run).tables["snapshot.transaction_summary"]
    assert table.rows[0][table.columns.index("expected_ratings")] == "Ba3 | BB-"
