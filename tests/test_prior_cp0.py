"""CP-0 claims use original inventory-bound Reports, never prepared metadata."""

import json
from pathlib import Path

import pytest
from test_prior_report import document

from builders import prepared_pack
from cp0_fixture import cp0_handoff
from rbotlib.contract import load_contract
from rbotlib.prior_candidates import qualify_candidates
from rbotlib.report.html_parts import embed_json
from rbotlib.report.markdown import render_markdown
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check

ROW = "| prior.html | 2026-10-14 | earlier | FULL_CREDIT_ASSESSMENT | full | Yes |"
HEAD = "offered |\n|---|---|---|---|---|---|\n"


def ready(tmp_path: Path, *, kind: str = "html", issuer: str = "TEST") -> tuple[Path, str]:
    doc = document()
    raw = embed_json(doc) if kind == "html" else render_markdown(doc, [], [])
    return prepared(tmp_path, raw, kind=kind, issuer=issuer)


def prepared(
    tmp_path: Path, raw: str | bytes, *, kind: str = "html", issuer: str = "TEST"
) -> tuple[Path, str]:
    name = "prior." + kind
    run = prepared_pack(tmp_path, {"issuer.txt": "Issuer annual report", name: raw})
    classes = {
        "issuer.txt": ("issuer", "Annual report", "Test", "Yes"),
        name: ("issuer", "RBOT Report", "Test", "Yes" if issuer == "TEST" else "No"),
    }
    text = cp0_handoff(run, ("Test", issuer), "2026-10-16", classes, primary=False)
    return run, text


def result(run: Path, text: str, rules: Rules) -> tuple[int, list[str]]:
    contract = load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules)
    code, findings = check(text, contract, rules, run)
    return code, [f"{f.code}: {f.message}" for f in findings]


@pytest.mark.parametrize("kind", ["html", "md"])
@pytest.mark.parametrize("issuer", ["TEST", "FOREIGN"])
def test_exact_original_metadata_and_pending_identity(
    tmp_path: Path, rules: Rules, kind: str, issuer: str
) -> None:
    run, text = ready(tmp_path, kind=kind, issuer=issuer)
    row = ROW.replace("prior.html", "prior." + kind)
    if issuer == "FOREIGN":
        row = row.replace("Yes |", "No |")
    assert result(run, text.replace(HEAD, HEAD + row + "\n"), rules) == (0, [])


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("2026-10-14", "2026-10-13"),
        ("earlier", "other"),
        ("FULL_CREDIT_ASSESSMENT", "EARNINGS_UPDATE"),
        ("full", "quick"),
        ("Yes", "No"),
        ("prior.html", "../prior.html"),
        ("prior.html", "issuer.txt"),
    ],
)
def test_false_row_claim_refuses(tmp_path: Path, rules: Rules, old: str, new: str) -> None:
    run, text = ready(tmp_path)
    code, findings = result(run, text.replace(HEAD, HEAD + ROW.replace(old, new) + "\n"), rules)
    assert code == 2 and any(f.startswith("prior_case_mismatch:") for f in findings)


@pytest.mark.parametrize("rows", ["", ROW + "\n" + ROW])
def test_missing_or_duplicate_usable_row_refuses(tmp_path: Path, rules: Rules, rows: str) -> None:
    run, text = ready(tmp_path)
    code, findings = result(run, text.replace(HEAD, HEAD + rows + "\n"), rules)
    assert code == 2 and any(f.startswith("prior_case_mismatch:") for f in findings)


@pytest.mark.parametrize("defect", ["hash", "missing", "symlink", "self", "self-renamed", "future"])
def test_protected_source_failure_is_run_error(tmp_path: Path, rules: Rules, defect: str) -> None:
    run, text = ready(tmp_path)
    if defect == "self-renamed":
        renamed = run.with_name("20261011-test-full-credit-assessment")
        run.rename(renamed)
        run = renamed
    source = run.parent.parent / "prior.html"
    if defect == "hash":
        source.write_text("different bytes")
    elif defect == "missing":
        source.unlink()
    elif defect == "symlink":
        replacement = source.with_suffix(".txt")
        source.rename(replacement)
        source.symlink_to(replacement)
    else:
        doc = document()
        if defect in ("self", "self-renamed"):
            for front in (
                doc["run_brief"]["front_matter"],
                doc["handoffs"]["MODEL"]["front_matter"],
            ):
                front["run_id"] = run.name
            doc["run_id"] = run.name
            doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][0] = run.name
        else:
            doc["generated_at"] = "2099-01-01T00:00:00+00:00"
        source.write_text(embed_json(doc))
        from rbotlib.inventory import build

        (run / "inventory.json").write_text(json.dumps(build(source.parent, run)))
    code, findings = result(run, text.replace(HEAD, HEAD + ROW + "\n"), rules)
    assert code == 1 and any(f.startswith("run_error:") for f in findings)


@pytest.mark.parametrize(
    "raw",
    [
        b'<script id="rbot-run">{broken</script>',
        b'<script id="rbot-run">\xff</script>',
        embed_json(document() | {"depth": ""}).encode(),
        embed_json(document() | {"generated_at": "2026-99-99"}).encode(),
    ],
)
def test_malformed_metadata_stays_named_gap_without_fabricated_row(
    tmp_path: Path, rules: Rules, raw: bytes
) -> None:
    run, text = prepared(tmp_path, raw)
    candidate = qualify_candidates(run, run.parent.parent, "TEST", run.name)[0]
    assert candidate.metadata is None and candidate.issue
    text = text.replace("## Gaps\n", "## Gaps\n\n- " + candidate.issue + "\n")
    assert result(run, text, rules) == (0, [])
    code, findings = result(run, text.replace(HEAD, HEAD + ROW + "\n"), rules)
    assert code == 2 and any(f.startswith("prior_case_mismatch:") for f in findings)
    code, findings = result(run, text.replace(candidate.issue, "issue omitted"), rules)
    assert code == 2 and any(f.startswith("prior_case_mismatch:") for f in findings)


def test_prepared_decoy_cannot_replace_original_metadata(tmp_path: Path, rules: Rules) -> None:
    run, text = ready(tmp_path)
    index = json.loads((run / "prepared/index.json").read_text())
    record = next(r for r in index["files"] if r["path"] == "prior.html")
    (run / record["prepared"]).write_text("fake metadata: 2025-01-01 not-original quick FOREIGN")
    # Prepared readability changes, so update that separate source claim truthfully.
    inventory_row = next(line for line in text.splitlines() if line.startswith("| prior.html |"))
    text = text.replace(inventory_row, inventory_row.replace("| No | No |", "| Yes | No |"))
    assert result(run, text.replace(HEAD, HEAD + ROW + "\n"), rules) == (0, [])
    assert (
        result(run, text.replace(HEAD, HEAD + ROW.replace("full", "quick") + "\n"), rules)[0] == 2
    )


def test_genuine_blocked_source_gap_retains_exit_three(tmp_path: Path, rules: Rules) -> None:
    run = prepared_pack(tmp_path, {"prior.html": '<script id="rbot-run">{broken</script>'})
    classes = {"prior.html": ("issuer", "RBOT Report", "Not identified", "No")}
    text = cp0_handoff(run, ("Test", "TEST"), "2026-10-16", classes, primary=False)
    candidate = qualify_candidates(run, run.parent.parent, "TEST", run.name)[0]
    assert candidate.issue
    text = text.replace("qa_status: Restricted", "qa_status: Blocked")
    text = text.replace("## Gaps\n", "## Gaps\n\n- " + candidate.issue + "\n")
    assert result(run, text, rules) == (3, [])


def test_issue_hidden_in_fenced_analysis_does_not_count_as_gap(
    tmp_path: Path, rules: Rules
) -> None:
    run, text = prepared(tmp_path, '<script id="rbot-run">{broken</script>')
    candidate = qualify_candidates(run, run.parent.parent, "TEST", run.name)[0]
    assert candidate.issue
    fake_gap = "## Analysis\n\n```text\n## Gaps\n" + candidate.issue + "\n```\n"
    text = text.replace("## Analysis\n", fake_gap)
    assert result(run, text, rules)[0] == 2


def test_explicit_report_date_overrides_generated_calendar(tmp_path: Path, rules: Rules) -> None:
    doc = document()
    doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][2] = "2026-10-15"
    run, text = prepared(tmp_path, embed_json(doc))
    assert result(run, text.replace(HEAD, HEAD + ROW + "\n"), rules)[0] == 2
    row = ROW.replace("2026-10-14", "2026-10-15")
    assert result(run, text.replace(HEAD, HEAD + row + "\n"), rules) == (0, [])


def test_no_report_copied_inventory_keeps_generic_cp0_checks(tmp_path: Path, rules: Rules) -> None:
    import shutil

    run = prepared_pack(tmp_path, {"issuer.txt": "Issuer annual report"})
    classes = {"issuer.txt": ("issuer", "Annual report", "Test", "Yes")}
    text = cp0_handoff(run, ("Test", "TEST"), "2026-10-16", classes, primary=False)
    copied = tmp_path / "copy/rbot-runs/copied"
    shutil.copytree(run, copied)
    assert result(copied, text, rules) == (0, [])
    text = text.replace(HEAD, HEAD + ROW + "\n")
    code, findings = result(copied, text, rules)
    assert code == 1 and any(f.startswith("run_error:") for f in findings)
