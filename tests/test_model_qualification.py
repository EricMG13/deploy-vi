"""Exact captured bytes, genuine upstream receipts and real pair origin."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from state_receipt_assertions import outcome_bytes
from test_accept import send
from test_model_completion import invoke
from test_model_host import eligible

from rbotlib import accept, cli, dispatch, state
from rbotlib.contract import load_contract
from rbotlib.inventory import RunError
from rbotlib.model import qualification
from rbotlib.model import run as writer
from rbotlib.rules import RBOT_ROOT, load_rules


def optional_handoff(run: Path, *, judgment_gap: bool = False, debt_gap: bool = False) -> None:
    contract = load_contract(RBOT_ROOT / "modules/CP-1D/contract.json", load_rules())
    text = (
        f"---\nmodule_id: CP-1D\nrun_id: {run.name}\nissuer_id: ACME\n"
        "analysis_date: 2026-10-02\nqa_status: Blocked\ninputs: CP-0, CP-1\n---\n"
        "\n## Analysis\nGenerated controller fixture; gaps.\n\n## Tables\n"
    )
    for table in contract.tables:
        text += f"\n<!-- table: {table.id} -->\n| " + " | ".join(c.name for c in table.columns)
        text += " |\n|" + "---|" * len(table.columns) + "\n"
        if debt_gap and table.id == "cp1d.debt_like_items":
            text += (
                "| Generated unquantified obligation | — | USD | MILLIONS | "
                "FY2025 | Debt-like | Source gap | [C1] |\n"
            )
        if judgment_gap and table.id == "cp1d.addback_assessment":
            text += (
                "| fixture_addback | FY2025 | — | USD | MILLIONS | "
                "Generated gap | UNREALIZED | Rejected | Source gap | No | [C1] |\n"
            )
    text += "\n## Gaps\nNo assessment.\n\n## Citations\n<!-- table: citations -->\n"
    text += "| id | source | locator | excerpt |\n|---|---|---|---|\n"
    if judgment_gap or debt_gap:
        text += "| C1 | acme_10k.txt | p. 1 | Acme Holdings, Inc. |\n"
    (run / "handoffs/CP-1D.md").write_text(text)
    send(run, RBOT_ROOT, "CP-1D", "fixture-optional")
    assert accept.accept(run, RBOT_ROOT, "CP-1D")["exit"] == 3


@pytest.mark.parametrize("qa", ["Pass", "Blocked"])
def test_checked_required_inputs_and_actual_optional_model_consumer(
    tmp_path: Path, qa: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, qa, optional=True)
    optional_handoff(run)
    raw = (run / "handoffs/CP-1D.md").read_bytes()
    assert invoke(run) == 0
    record = state.read(run)
    inputs = json.loads((run / "model.json").read_bytes())["inputs"]
    assert inputs["CP-1D"] == hashlib.sha256(raw).hexdigest()
    message = dispatch.prepare_message(run, RBOT_ROOT, "CP-5")
    assert str(run / "handoffs/MODEL.md") in message
    assert str(run / "handoffs/CP-1D.md") in message
    assert record["steps"]["MODEL"]["host_execution"]["optional_exclusion"] == ""


@pytest.mark.parametrize("kind", ["malformed", "symlink", "fifo"])
def test_failed_cp1d_leftover_is_never_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    leftover = run / "handoffs/CP-1D.md"
    if kind == "malformed":
        leftover.write_bytes(b"\xff malformed")
    elif kind == "symlink":
        leftover.symlink_to(run / "run-brief.md")
    else:
        os.mkfifo(leftover)
    read = Path.read_bytes

    def guarded(path: Path) -> bytes:
        if path == leftover:
            raise AssertionError("excluded optional input was opened")
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    assert invoke(run) == 0
    assert json.loads((run / "model.json").read_bytes())["inputs"]["CP-1D"] is None
    assert "CP-1D: failed; excluded" in (run / "handoffs/MODEL.md").read_text()
    assert leftover.is_symlink() if kind == "symlink" else leftover.exists()


@pytest.mark.parametrize("name", ["handoffs/CP-1.md", "run-brief.md"])
@pytest.mark.parametrize("phase", ["capture", "requalification"])
def test_input_byte_swap_is_refused_against_registered_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, phase: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    target = run / name
    reader, build = qualification._capture, writer.build
    swapped = False

    def changed(selected: Path, selected_name: str, digest: str) -> writer.Read:
        nonlocal swapped
        if selected / selected_name == target and phase == "capture" and not swapped:
            swapped = True
            target.write_bytes(target.read_bytes() + b"\nbyte swap\n")
        return reader(selected, selected_name, digest)

    def during(
        cp1: writer.Read,
        brief: writer.Read,
        cp1d: writer.Read | None,
        generated_at: str,
        missing: str | writer.Options = "",
    ) -> tuple[writer.Written, dict[str, bytes]]:
        nonlocal swapped
        if phase == "requalification" and not swapped:
            swapped = True
            target.write_bytes(target.read_bytes() + b"\nbyte swap\n")
        return build(cp1, brief, cp1d, generated_at, missing)

    monkeypatch.setattr(qualification, "_capture", changed)
    monkeypatch.setattr(writer, "build", during)
    assert invoke(run) == 1 and swapped
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == ("pending" if phase == "capture" else "failed")
    assert not any((run / name).exists() for name in qualification.OUTPUTS)


@pytest.mark.parametrize("cause", ["missing", "malformed", "stale", "identity", "qa"])
def test_current_required_input_refusal_cannot_compute(tmp_path: Path, cause: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    target = run / "handoffs/CP-1.md"
    if cause == "missing":
        target.unlink()
    elif cause == "malformed":
        target.write_bytes(b"\xff")
    else:
        raw = target.read_bytes()
        raw = raw.replace(b"issuer_id: ACME", b"issuer_id: WRONG") if cause == "identity" else raw
        raw = (
            raw.replace(b"qa_status: Blocked", b"qa_status: Pass") if cause == "qa" else raw + b"\n"
        )
        target.write_bytes(raw)
    original = state.read(run)["steps"]["CP-1"]
    if cause == "stale":
        assert invoke(run) == 0
        assert state.read(run)["steps"]["CP-1"]["note"] == "edited"
        assert state.read(run)["steps"]["MODEL"]["host_execution"]["inputs"][
            "CP-1"
        ] == dispatch._sha(target)
    else:
        assert invoke(run) == 1
        current = state.read(run)["steps"]
        assert current["CP-1"]["status"] == "failed"
        assert current["CP-1"]["current_origin"] == original
        assert current["MODEL"]["status"] == "skipped" and "CP-1" in current["MODEL"]["reason"]
        assert "attempts" not in current["MODEL"]
        assert not any((run / name).exists() for name in qualification.OUTPUTS)


@pytest.mark.parametrize(
    "kind",
    [
        "json-scalar",
        "json-identity",
        "json-content",
        "handoff-qa",
        "handoff-content",
    ],
)
def test_corrupt_actual_accepted_pair_cannot_qualify_consumer(tmp_path: Path, kind: str) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    assert invoke(run) == 0
    if kind.startswith("json"):
        path = run / "model.json"
        data = json.loads(path.read_bytes())
        if kind == "json-scalar":
            data = []
        elif kind == "json-identity":
            data["run_id"] = "other"
        else:
            data["limitations"] = []
        path.write_text(json.dumps(data))
    elif kind == "handoff-qa":
        path = run / "handoffs/MODEL.md"
        path.write_text(path.read_text().replace("qa_status: Pass", "qa_status: Blocked"))
    else:
        path = run / "handoffs/MODEL.md"
        path.write_text(path.read_text() + "\nChanged origin\n")
    before = state.read(run)["steps"]["MODEL"]
    assert cli.main(["dispatch-message", "--run", str(run), "--module", "CP-3"]) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed" and current["current_origin"] == before
    assert current["host_execution"] == before["host_execution"]
    assert current["host_exit"] == before["host_exit"] == 0
    with pytest.raises((RunError, ValueError), match=r"MODEL|identity"):
        qualification.qualify(run, RBOT_ROOT, state.read(run))


def test_managed_older_rejected_judgment_names_missing_current_fallback(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT, optional=True, variant="judgment-gap")
    optional_handoff(run, judgment_gap=True)
    assert invoke(run) == 0
    assert "CP1D_CURRENT_JUDGMENT_MISSING" in (run / "handoffs/MODEL.md").read_text()


def test_checked_but_model_unreadable_optional_is_excluded_with_actual_reason(
    tmp_path: Path,
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, optional=True)
    optional_handoff(run, debt_gap=True)
    before = (run / "handoffs/CP-1D.md").read_bytes()
    assert invoke(run) == 0
    assert "CP-1D: unqualified" in (run / "handoffs/MODEL.md").read_text()
    assert "amount" in (run / "handoffs/MODEL.md").read_text()
    assert (run / "handoffs/CP-1D.md").read_bytes() == before


def _corrupt_json(raw: bytes, corruption: str) -> bytes:
    data = json.loads(raw)
    if corruption == "run":
        data["run_id"] = "other"
    elif corruption == "inputs":
        data["inputs"]["CP-1"] = "0" * 64
    else:
        data["lines"][0]["cells"][0]["value"] = "123"
    return json.dumps(data).encode()


@pytest.mark.parametrize(
    "corruption",
    ["run", "inputs", "money", "qa", "handoff", "missing-json", "missing-md", "extra"],
)
def test_wrong_built_pair_cannot_be_initially_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    build = writer.build
    once = False

    def altered(
        cp1: writer.Read,
        brief: writer.Read,
        cp1d: writer.Read | None,
        generated_at: str,
        missing: str | writer.Options = "",
    ) -> tuple[writer.Written, dict[str, bytes]]:
        nonlocal once
        written, files = build(cp1, brief, cp1d, generated_at, missing)
        if not once:
            once = True
            if corruption in ("run", "inputs", "money"):
                files["model.json"] = _corrupt_json(files["model.json"], corruption)
            elif corruption == "qa":
                files["handoffs/MODEL.md"] = files["handoffs/MODEL.md"].replace(
                    b"qa_status: Pass", b"qa_status: Restricted"
                )
            elif corruption.startswith("missing"):
                del files["model.json" if corruption == "missing-json" else "handoffs/MODEL.md"]
            elif corruption == "extra":
                files["model.xlsx"] = b"retired export"
            else:
                files["handoffs/MODEL.md"] += b"\nChanged origin\n"
        return written, files

    monkeypatch.setattr(writer, "build", altered)
    assert invoke(run) == 1
    current = state.read(run)["steps"]["MODEL"]
    assert current["status"] == "failed" and current["host_exit"] == 1
    assert not any((run / name).exists() for name in qualification.OUTPUTS)


def test_blocked_no_stack_observations_never_publish_money_rank_zero(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    assert invoke(run) == 0
    data = json.loads((run / "model.json").read_bytes())
    totals = {row["line"]: row for row in data["capital_structure"]["totals"]}
    assert totals["Total debt"]["amount"] is None and totals["Cash"]["amount"] is None
    for name in ("Senior secured debt", "Unsecured debt"):
        assert totals[name]["amount"] is None
        assert totals[name]["reasons"]["amount"] == "NOT_SOURCED"
    markdown = (run / "handoffs/MODEL.md").read_text()
    assert "| Senior secured debt | — |" in markdown and "| Unsecured debt | — |" in markdown


def test_legacy_three_output_receipt_requires_recovery_without_migration(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    assert invoke(run) == 0
    legacy = run / "model.xlsx"
    legacy.write_bytes(b"retired workbook")

    def legacy_receipt(record: state.Record) -> None:
        record["steps"]["MODEL"]["outputs"]["model.xlsx"] = hashlib.sha256(
            legacy.read_bytes()
        ).hexdigest()

    state.update(run, legacy_receipt)
    before = outcome_bytes(run)
    with pytest.raises(RunError, match="current outputs/hash/QA differ"):
        qualification.qualify(run, RBOT_ROOT, state.read(run))
    assert cli.main(["dispatch-message", "--run", str(run), "--module", "CP-3"]) == 1
    assert outcome_bytes(run) == before
    assert legacy.read_bytes() == b"retired workbook"
