"""`validate --run` runs the host's own input qualification (MODEL, FIT) over the candidate."""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
from test_accept import accept, send
from test_bootstrap import approve, ready
from test_host_fit import fit_run
from test_model_host import eligible
from test_model_qualification import optional_handoff

from conftest import FIXTURES
from cp0_fixture import cp0_handoff, registry_classification
from rbotlib import cli, state
from rbotlib.corpus import load_registry
from rbotlib.rules import RBOT_ROOT

BAD_ID = "PF4_SYNERGIES"
REAL_ID = "impairment"


def validate(
    path: Path, module: str, run: Path | None, capsys: pytest.CaptureFixture[str]
) -> tuple[int, str]:
    argv = ["validate", str(path), "--module", module]
    if run is not None:
        argv += ["--run", str(run)]
    capsys.readouterr()
    code = cli.main(argv)
    return code, capsys.readouterr().out


def fixture(module: str, run: Path) -> str:
    text = (FIXTURES / f"handoffs/{module}.md").read_text()
    return text.replace("run_id: 20261011-czr-full-credit-assessment", f"run_id: {run.name}")


def czr_run(corpus_pack: Callable[[str], Path], tmp_path: Path, *modules: str) -> Path:
    """A CZR run whose accepted Handoffs are the named fixture modules, in order."""
    pack = shutil.copytree(corpus_pack("czr-2026q2-primary"), tmp_path / "working pack")
    assert cli.main(["new-run", "--pack", str(pack)]) == 0
    run = next((pack / "rbot-runs").iterdir())
    for command in ("inventory", "prepare"):
        assert cli.main([command, "--run", str(run)]) == 0
    record = load_registry().pack("czr-2026q2-primary")
    (run / "handoffs").mkdir()
    classes = registry_classification(record)
    (run / "handoffs/CP-0.md").write_text(
        cp0_handoff(
            run, ("Caesars Entertainment, Inc.", "CZR"), "2026-10-02", classes, primary=False
        )
    )
    send(run, RBOT_ROOT)
    assert accept(run) == 0
    ready(run, RBOT_ROOT)
    run = approve(run, RBOT_ROOT)
    for module in modules:
        send(run, RBOT_ROOT, module)
        (run / f"handoffs/{module}.md").write_text(fixture(module, run))
        assert accept(run, module=module) == 0
    return run


def with_bad_addback(run: Path, tmp_path: Path) -> Path:
    """The fixture CP-1D with its first assessment row about an add-back CP-1 lacks."""
    candidate = tmp_path / "CP-1D.md"
    text = fixture("CP-1D", run)
    assert f"| {REAL_ID} | FY2025 |" in text
    candidate.write_text(text.replace(f"| {REAL_ID} | FY2025 |", f"| {BAD_ID} | FY2025 |", 1))
    return candidate


@pytest.mark.corpus
def test_cp1d_row_for_an_addback_not_in_cp1_is_a_host_input_finding(
    corpus_pack: Callable[[str], Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = czr_run(corpus_pack, tmp_path, "CP-1")
    good = tmp_path / "good.md"
    good.write_text(fixture("CP-1D", run))
    assert validate(good, "CP-1D", run, capsys)[0] == 0
    bad = with_bad_addback(run, tmp_path)
    code, out = validate(bad, "CP-1D", run, capsys)
    assert code == 2
    assert f"host_input: MODEL: cp1d.addback_assessment row 1 column addback_id: {BAD_ID}" in out
    assert validate(bad, "CP-1D", None, capsys)[0] == 0  # no --run: unchanged


@pytest.mark.corpus
def test_cp1_that_drops_an_assessed_addback_is_a_host_input_finding(
    corpus_pack: Callable[[str], Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = czr_run(corpus_pack, tmp_path, "CP-1", "CP-1D")
    path = run / "handoffs/CP-1.md"
    assert validate(path, "CP-1", run, capsys)[0] == 0
    cp1 = path.read_text()
    kept = [ln for ln in cp1.splitlines() if not ln.startswith((f"| {REAL_ID} |", "| C21 |"))]
    assert len(kept) < len(cp1.splitlines())
    candidate = tmp_path / "CP-1.md"
    candidate.write_text("\n".join(kept) + "\n")
    code, out = validate(candidate, "CP-1", run, capsys)
    assert code == 2 and f"cp1d.addback_assessment row 1 column addback_id: {REAL_ID}" in out


@pytest.mark.corpus
def test_unaccepted_upstream_skips_only_the_cross_check(
    corpus_pack: Callable[[str], Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = czr_run(corpus_pack, tmp_path)  # CP-1 not accepted
    assert state.read(run)["steps"]["CP-1"]["status"] == "pending"
    assert validate(with_bad_addback(run, tmp_path), "CP-1D", run, capsys)[0] == 0


@pytest.mark.corpus
def test_changed_upstream_bytes_are_not_an_accepted_upstream(
    corpus_pack: Callable[[str], Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = czr_run(corpus_pack, tmp_path, "CP-1")
    with (run / "handoffs/CP-1.md").open("a") as handle:
        handle.write("\n")
    assert (
        hashlib.sha256((run / "handoffs/CP-1.md").read_bytes()).hexdigest()
        != (state.read(run)["steps"]["CP-1"]["sha256"])
    )
    assert validate(with_bad_addback(run, tmp_path), "CP-1D", run, capsys)[0] == 0


def test_a_blocked_candidate_is_not_host_checked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, "Blocked", optional=True, variant="judgment-gap")
    optional_handoff(run, judgment_gap=True)
    candidate = tmp_path / "CP-1D.md"
    candidate.write_text((run / "handoffs/CP-1D.md").read_text().replace("fixture_addback", BAD_ID))
    assert validate(candidate, "CP-1D", run, capsys)[0] == 3


def test_cp1_entity_in_another_currency_is_a_host_input_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = fit_run(tmp_path)
    path = run / "handoffs/CP-1.md"
    cp1 = path.read_text()
    assert validate(path, "CP-1", run, capsys)[0] == 0
    row = next(ln for ln in cp1.splitlines() if ln.startswith("| Acme Holdings, Inc. | Fixture"))
    candidate = tmp_path / "CP-1.md"
    candidate.write_text(cp1.replace(row, row.replace(" USD ", " EUR ", 1)))
    code, out = validate(candidate, "CP-1", run, capsys)
    assert code == 2
    assert "host_input: MODEL: cp1.entity_profile row 1 column reporting_currency" in out


def test_fit_refuses_a_cp1_facility_in_two_currencies_at_validate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = fit_run(tmp_path)
    path = run / "handoffs/CP-1.md"
    cp1 = path.read_text()
    assert validate(path, "CP-1", run, capsys)[0] == 0
    row = next(ln for ln in cp1.splitlines() if ln.startswith("| FIXTURE | Generated unknown"))
    assert " USD " in row and "TERM LOAN" in row
    candidate = tmp_path / "CP-1.md"
    candidate.write_text(cp1.replace(row + "\n", row + "\n" + row.replace("USD", "EUR", 1) + "\n"))
    code, out = validate(candidate, "CP-1", run, capsys)
    assert code == 2
    assert "host_input: FIT: cp1.debt_facility_register: facility FIXTURE has rows in USD" in out


def test_fit_skipped_for_want_of_a_portfolio_is_not_checked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, "Pass", optional=True)
    assert state.read(run)["steps"]["FIT"]["status"] == "skipped"
    cp1 = (run / "handoffs/CP-1.md").read_text()
    row = next(ln for ln in cp1.splitlines() if ln.startswith("| FIXTURE | Generated unknown"))
    candidate = tmp_path / "CP-1.md"
    candidate.write_text(cp1.replace(row + "\n", row + "\n" + row.replace("USD", "EUR", 1) + "\n"))
    assert "FIT:" not in validate(candidate, "CP-1", run, capsys)[1]
