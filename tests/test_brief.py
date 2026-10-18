from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from builders import make_run
from conftest import FIXTURES
from rbotlib.cli import main
from rbotlib.contract import contract_from_dict
from rbotlib.handoff import Handoff, markers, parse
from rbotlib.rules import Rules
from rbotlib.validate import check, run_findings

CP0 = FIXTURES / "handoffs" / "CP-0.md"


def _run(tmp_path: Path, *, managed: bool = False) -> Path:
    if managed:
        (tmp_path / "pack").mkdir()
    run = make_run(tmp_path / "pack", "20261011-czr-pending", managed=managed)
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
def test_brief_citations_anchor_in_the_primary_pack(
    prepared_run: Callable[[str], Path], tmp_path: Path
) -> None:
    run = shutil.copytree(prepared_run("czr-2026q2-primary"), tmp_path / "run")
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


def _cp0(run: Path, *swaps: tuple[str, str]) -> None:
    text = CP0.read_text(encoding="utf-8")
    for old, new in swaps:
        assert old in text, old
        text = text.replace(old, new, 1)
    (run / "handoffs" / "CP-0.md").write_text(text, encoding="utf-8")


def _from(run: Path) -> int:
    return main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])


def test_tranches_with_primary_no_are_refused_by_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    _cp0(run, ("| primary | | Yes | Sourced |", "| primary | | No | Sourced |"))
    assert _from(run) == 1
    out = capsys.readouterr().out
    assert "NEW-1" in out and "primary is 'No'" in out
    assert not (run / "run-brief.md").exists()


def test_the_brief_records_its_hash_and_time_in_the_run_state(tmp_path: Path) -> None:
    run = _run(tmp_path, managed=True)
    state = run / "run-state.json"
    assert _from(run) == 0
    data = json.loads(state.read_text(encoding="utf-8"))
    brief = (run / "run-brief.md").read_bytes()
    assert data["run_brief_sha256"] == hashlib.sha256(brief).hexdigest()
    assert data["updated_at"].startswith("20")
    assert main(["brief", "--run", str(run), "--set", "analyst=A"]) == 0
    again = json.loads(state.read_text(encoding="utf-8"))["run_brief_sha256"]
    assert (
        again
        == hashlib.sha256((run / "run-brief.md").read_bytes()).hexdigest()
        != data["run_brief_sha256"]
    )


@pytest.mark.parametrize(
    ("swap", "message"),
    [
        ("| debt_type | NEW-1 | 1L Term Loan |", "debt_type 'Loan'"),
        ("| use_of_proceeds | NEW-1 | Acquisition |", "use_of_proceeds 'Buyout'"),
        ("| talk_stage | NEW-1 | Initial talk |", "talk_stage 'Early'"),
        ("| unit | NEW-1 | MILLIONS |", "unit 'BILLIONS'"),
    ],
)
def test_prefill_tranche_cells_follow_their_scales(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], swap: str, message: str
) -> None:
    run = _run(tmp_path)
    bad = {"debt_type": "Loan", "use_of_proceeds": "Buyout", "talk_stage": "Early"}
    cell = swap.split("|")[1].strip()
    value = swap.split("|")[3].strip()
    _cp0(run, (swap, swap.replace(value, bad.get(cell, "BILLIONS"))))
    assert _from(run) == 1
    assert message in capsys.readouterr().out


@pytest.mark.parametrize(
    ("swap", "message"),
    [
        ("| as_of_date | | 2026-10-02 |", "as_of_date must be YYYY-MM-DD"),
        ("| primary | | Yes | Sourced |", "primary must be one of"),
        ("| issuer_id | | CZR | Sourced |", "status 'Maybe'"),
    ],
)
def test_prefill_field_values_and_statuses_are_validated(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], swap: str, message: str
) -> None:
    run = _run(tmp_path)
    if swap.startswith("| issuer_id"):
        new = swap.replace("Sourced", "Maybe")
    elif swap.startswith("| primary"):
        new = swap.replace("Yes", "Perhaps")
    else:
        new = swap.replace("2026-10-02", "02/10/2026")
    _cp0(run, (swap, new))
    assert _from(run) == 1
    assert message in capsys.readouterr().out


@pytest.mark.parametrize(
    "edit",
    [
        *["analyst=", "analyst=   ", "analyst=a\nb", "analyst=a\rb", "analyst=a\x00b"],
        "analyst=a\u2028b",
        *["ssim_ev_multiple=nan", "ssim_ev_multiple=inf", "ssim_ev_multiple=-2"],
        "ssim_ev_multiple=0",
    ],
)
def test_empty_control_and_non_finite_edits_are_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit: str
) -> None:
    run = _run(tmp_path)
    _from(run)
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--set", edit]) == 1
    assert capsys.readouterr().out.strip()


def test_a_multiple_is_written_as_a_plain_decimal(tmp_path: Path) -> None:
    run = _run(tmp_path)
    _from(run)
    assert main(["brief", "--run", str(run), "--set", "ssim_ev_multiple=1E+1x"]) == 0
    assert _fields(_brief(run))["ssim_ev_multiple"][0] == "10"


def test_the_fields_table_follows_the_spec_order(tmp_path: Path) -> None:
    run = _run(tmp_path)
    _from(run)
    assert [r[0] for r in _brief(run).tables["brief.run_brief_fields"].rows[:10]] == [
        "issuer",
        "issuer_id",
        "as_of_date",
        "objective",
        "analyst",
        "primary",
        "pathway",
        "depth",
        "morningstar_issuer_id",
        "ssim_ev_multiple",
    ]


def test_a_failed_write_and_an_undecodable_file_are_errors_not_tracebacks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    _from(run)
    before = (run / "run-brief.md").read_text(encoding="utf-8")

    def refuse(path: Path, text: str) -> None:
        raise PermissionError(13, "Permission denied", str(path))

    monkeypatch.setattr("rbotlib.brief.write_atomic", refuse)
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--set", "analyst=A"]) == 1
    assert f"error: {run / 'run-brief.md'}: Permission denied" in capsys.readouterr().out
    assert (run / "run-brief.md").read_text(encoding="utf-8") == before
    monkeypatch.undo()
    (run / "run-brief.md").write_bytes(b"\xff\xfe bad")
    for args in (["--show"], ["--set", "analyst=A"]):
        assert main(["brief", "--run", str(run), *args]) == 1
        assert f"error: {run / 'run-brief.md'}:" in capsys.readouterr().out


def test_an_approved_brief_is_never_silently_reset(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from test_bootstrap import approve, pending, ready

    from rbotlib.rules import RBOT_ROOT

    run = pending(tmp_path, RBOT_ROOT)
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    before = (run / "run-brief.md").read_bytes()
    capsys.readouterr()
    for args in (["--set", "analyst=A"], ["--from", "handoffs/CP-0.md"]):
        assert main(["brief", "--run", str(run), *args]) == 1
        diagnostic = capsys.readouterr().out
        assert "was approved" in diagnostic and "needs a new run" in diagnostic
    assert (run / "run-brief.md").read_bytes() == before


def test_duplicate_prefill_rows_and_dangling_cites_are_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    dup = "| issuer | | Caesars Entertainment, Inc. | Sourced | [C1] |\n"
    _cp0(run, (dup, dup + dup))
    assert _from(run) == 1
    assert "'issuer' appears twice" in capsys.readouterr().out
    _cp0(
        run,
        (
            "| oid | NEW-1 | 99.0\u201399.5 | Sourced | [C10] |",
            "| oid | NEW-1 | 99.0\u201399.5 | Sourced | [C99] |",
        ),
    )
    assert _from(run) == 1
    assert "C99" in capsys.readouterr().out


def test_only_the_runs_cp0_can_be_the_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    other = tmp_path / "other.md"
    shutil.copy(CP0, other)
    assert main(["brief", "--run", str(run), "--from", str(other)]) == 1
    assert "--from must be handoffs/CP-0.md" in capsys.readouterr().out


def test_a_gap_analysis_date_passes_the_front_matter_rules(tmp_path: Path, rules: Rules) -> None:
    run = _run(tmp_path)
    _cp0(run, ("| as_of_date | | 2026-10-02 | Sourced | [C2] |", "| as_of_date | | — | Gap | |"))
    assert _from(run) == 0
    text = (run / "run-brief.md").read_text(encoding="utf-8")
    assert "analysis_date: —" in text
    contract = contract_from_dict(
        {
            "module_id": "RUN_BRIEF",
            "title": "Run Brief",
            "reader_question": "q",
            "inputs": [{"handoff": "CP-0", "why": "pre-fill"}],
            "process": ["p"],
            "tables": [],
            "prohibited": [],
        },
        rules,
    )
    codes = {f.code for f in check(text, contract, rules)[1]}
    assert not codes & {"front_matter_missing", "identity", "qa_status", "inputs", "sections"}


def _set_tranche(run: Path, *edits: tuple[str, str]) -> int:
    return main(["brief", "--run", str(run), *[a for e in edits for a in ("--set-tranche", *e)]])


def _tranche(h: Handoff, tranche_id: str) -> dict[str, str]:
    table = h.tables["snapshot.transaction_summary"]
    row = next(r for r in table.rows if r[0] == tranche_id)
    return dict(zip(table.columns, row, strict=True))


def test_tranche_edits_follow_source_wins_and_survive_a_rebuild(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    assert _set_tranche(run, ("NEW-1", "bloomberg_id=BBG01ABC2345"), ("NEW-1", "size=3500")) == 0
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    h = _brief(run)
    fields = _fields(h)
    assert fields["NEW-1.bloomberg_id"] == [
        "BBG01ABC2345",
        "Analyst-asserted",
        "BBG01ABC2345",
        "[C14]",
    ]
    assert fields["NEW-1.size"] == ["3000", "Sourced", "3500", "[C7]"]
    assert fields["NEW-1.cr_score"] == ["—", "Gap", "—", "[C15]"]
    row = _tranche(h, "NEW-1")
    assert (row["bloomberg_id"], row["size"], row["status"]) == (
        "BBG01ABC2345",
        "3000",
        "Analyst-asserted",
    )
    assert row["analyst_value"] == "size=3500; bloomberg_id=BBG01ABC2345"


def test_tranche_values_are_normalised_to_their_scales(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    edits = [
        ("NEW-2", "debt_type=ss notes"),
        ("NEW-2", "currency=eur"),
        ("NEW-2", "talk_stage=revised GUIDANCE"),
        ("NEW-2", "unit=millions"),
        ("NEW-2", "size= 500.0 "),
        ("NEW-2", "maturity_date=2031-04-15"),
    ]
    assert _set_tranche(run, *edits) == 0
    row = _tranche(_brief(run), "NEW-2")
    assert [row[f] for f in ("debt_type", "currency", "talk_stage", "unit", "size")] == [
        "SS Notes",
        "EUR",
        "Revised guidance",
        "MILLIONS",
        "500.0",
    ]
    assert (row["maturity_date"], row["status"]) == ("2031-04-15", "Gap")
    text = (run / "run-brief.md").read_text(encoding="utf-8")
    assert "- `NEW-2.borrower`: not found in the Source Pack; set it with" in text
    assert "`rbot brief --set-tranche NEW-2 borrower=<value>`." in text
    assert "NEW-2.oid" not in text.split("## Gaps")[1]


@pytest.mark.parametrize(
    ("tranche", "edit", "message"),
    [
        ("NEW-1", "margin=300", "unknown tranche field 'margin'"),
        ("NEW-1", "size", "unknown tranche field 'size'"),
        ("TLB", "size=1", "tranche id 'TLB' is not NEW-<n>"),
        ("NEW-1", "debt_type=Loan", "debt_type must be one of ('RCF', '1L Term Loan'"),
        ("NEW-1", "size=3,000", "size must be a plain decimal, not '3,000'"),
        ("NEW-1", "maturity_date=15/12/2033", "maturity_date must be YYYY-MM-DD"),
        ("NEW-1", "currency=dollars", "currency must be a three-letter ISO code"),
        ("NEW-1", "size=NaN", "size must be a plain decimal, not 'NaN'"),
        ("NEW-1", "size=Infinity", "size must be a plain decimal, not 'Infinity'"),
        ("NEW-1", "size=1e3", "size must be a plain decimal, not '1e3'"),
        ("NEW-1", "size=-5", "size must be a plain decimal, not '-5'"),
        ("NEW-1", "price_talk=S+325\n## Gaps", "price_talk holds a line break or control"),
        ("NEW-1", "borrower=  ", "borrower is empty"),
    ],
)
def test_refused_tranche_edits_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], tranche: str, edit: str, message: str
) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert _set_tranche(run, (tranche, edit)) == 1
    assert message in capsys.readouterr().out


@pytest.mark.parametrize(
    "argv",
    [
        ["--from", "handoffs/CP-0.md", "--set", "analyst=A"],
        ["--show", "--set-tranche", "NEW-1", "oid=99"],
        [],
    ],
)
def test_exactly_one_mode_is_given(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    run = _run(tmp_path)
    assert main(["brief", "--run", str(run), *argv]) == 1
    assert "give --from, or --show, or one or more --set / --set-tranche edits" in (
        capsys.readouterr().out
    )


@pytest.mark.corpus
def test_tranche_edits_keep_the_brief_anchored_in_the_primary_pack(
    prepared_run: Callable[[str], Path], tmp_path: Path
) -> None:
    run = shutil.copytree(prepared_run("czr-2026q2-primary"), tmp_path / "run")
    (run / "handoffs").mkdir(exist_ok=True)
    shutil.copy(CP0, run / "handoffs" / "CP-0.md")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert _set_tranche(run, ("NEW-1", "cr_score=3"), ("NEW-1", "oid=99.25")) == 0
    h = _brief(run)
    assert run_findings(h, run) == []
    assert _fields(h)["NEW-1.oid"] == ["99.0\u201399.5", "Sourced", "99.25", "[C10]"]
    assert _tranche(h, "NEW-1")["cr_score"] == "3"


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            "| debt_type | NEW-1 | 1L Term Loan |",
            "| debt_type | Tranche A | 1L Term Loan |",
            "cp0.run_brief_prefill: tranche id 'Tranche A' is not NEW-<n>",
        ),
        (
            "| debt_type | NEW-1 | 1L Term Loan |",
            "| debt_type | NEW-1 | Senior secured notes |",
            "cp0.run_brief_prefill NEW-1 debt_type: debt_type must be one of",
        ),
        (
            "| size | NEW-1 | 3000 |",
            "| size | NEW-1 | 1,000 million |",
            "cp0.run_brief_prefill NEW-1 size: size must be a plain decimal",
        ),
        (
            "| as_of_date | | 2026-10-02 |",
            "| as_of_date | | 2 October 2026 |",
            "cp0.run_brief_prefill as_of_date: as_of_date must be YYYY-MM-DD",
        ),
    ],
)
def test_the_prefill_is_held_to_the_edit_rules(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], old: str, new: str, message: str
) -> None:
    run = _run(tmp_path)
    cp0 = run / "handoffs" / "CP-0.md"
    cp0.write_text(CP0.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 1
    assert message in capsys.readouterr().out


def test_blank_or_multiline_edits_are_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    capsys.readouterr()
    assert main(["brief", "--run", str(run), "--set", "analyst=  "]) == 1
    assert "analyst is empty" in capsys.readouterr().out
    assert main(["brief", "--run", str(run), "--set", "objective=Review\n## Gaps"]) == 1
    assert "objective holds a line break or control character" in capsys.readouterr().out
    assert parse((run / "run-brief.md").read_text(encoding="utf-8")).sections == [
        "Analysis",
        "Tables",
        "Gaps",
        "Citations",
    ]


OTHER_ISSUER = (
    "| old/other.html | 2026-07-15 | 20260715-zeta-earnings-update | EARNINGS_UPDATE | full | No |"
)
OWN = "| old/own.html | 2026-07-15 | 20260715-czr-earnings-update | EARNINGS_UPDATE | full | Yes |"


def test_a_report_cp0_did_not_offer_is_not_carried(tmp_path: Path) -> None:
    run = _run(tmp_path)
    cp0 = run / "handoffs" / "CP-0.md"
    head = "offered |\n|---|---|---|---|---|---|\n"
    text = CP0.read_text(encoding="utf-8").replace(head, f"{head}{OTHER_ISSUER}\n{OWN}\n")
    cp0.write_text(text, encoding="utf-8")
    assert main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"]) == 0
    assert _brief(run).tables["brief.prior_case"].rows == [
        ["old/own.html", "2026-07-15", "20260715-czr-earnings-update", "No"]
    ]


def test_the_brief_records_the_cp0_it_was_built_from(tmp_path: Path) -> None:
    run = _run(tmp_path)
    main(["brief", "--run", str(run), "--from", "handoffs/CP-0.md"])
    sha = hashlib.sha256((run / "handoffs" / "CP-0.md").read_bytes()).hexdigest()
    assert _brief(run).front_matter["cp0_sha256"] == sha
    main(["brief", "--run", str(run), "--set", "analyst=A"])
    assert _brief(run).front_matter["cp0_sha256"] == sha
