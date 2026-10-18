"""Legal Module seams; synthetic witnesses establish shape/arithmetic, never source authority."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from test_cp1c_module import permission_message
from test_modules import contract, fixture

from rbotlib.calc import covenant_headroom
from rbotlib.catalog import _order, load_catalog, load_contracts
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check


def synthetic_handoff(rules: Rules) -> str:
    """Explicitly fictional legal record with no authentic provenance qualification."""
    text = fixture("CP-4").replace("qa_status: Blocked", "qa_status: Restricted")
    start, end = text.index("<!-- table: cp4.document_register -->"), text.index("## Gaps")
    rows: list[list[str]] = [
        ["TEST indenture", "Indenture", "2026-01-01", "TEST parties", "TEST law", "Executed"],
        [
            "TEST coverage",
            "Incurrence",
            "Floor",
            "2",
            "3",
            "x",
            "TEST legal basis",
            "1",
            "Headroom",
        ],
        [
            "Debt",
            "TEST basket",
            "TEST fixed amount",
            "2",
            "3",
            "USD",
            "MILLIONS",
            "Calculated",
            "Low",
            "TEST risk",
            "TEST implication",
        ],
        ["TEST entity", "Issuer", "Yes", "TEST guarantee", "TEST lien", "TEST only"],
        ["TEST flag", "TEST provision", "TEST risk", "Low", "TEST PD/LGD effect"],
        ["TEST EBITDA", "TEST clause", "TEST condition", "TEST capacity effect"],
        ["TEST protection", "2", "TEST evidence"],
    ]
    lines = []
    for table, row in zip(contract("CP-4", rules).tables, rows, strict=True):
        lines += [
            f"<!-- table: {table.id} -->",
            "| " + " | ".join(c.name for c in table.columns) + " |",
            "|" + "---|" * len(table.columns),
            "| " + " | ".join([*row, "calc: TEST-ONLY fictional record"]) + " |",
            "",
        ]
    return text[:start] + "\n".join(lines) + "\n" + text[end:]


def test_synthetic_positive_shape_is_explicitly_unqualified(rules: Rules) -> None:
    text = synthetic_handoff(rules)
    assert "TEST-ONLY fictional record" in text
    assert check(text, contract("CP-4", rules), rules) == (0, [])


@pytest.mark.parametrize(
    "kind,status",
    [("Indenture", "Draft"), ("Indenture", "Unsigned"), ("Offering memorandum", "Executed")],
)
def test_draft_unsigned_or_om_only_refuses_governing_gate(
    kind: str, status: str, rules: Rules
) -> None:
    text = (
        synthetic_handoff(rules)
        .replace("| Indenture |", f"| {kind} |")
        .replace("| Executed |", f"| {status} |")
    )
    code, found = check(text, contract("CP-4", rules), rules)
    assert code == 2 and any(f.code == "legal_document_gate" for f in found)


@pytest.mark.parametrize("table", ["cp4.covenant_tests", "cp4.capacity_register"])
@pytest.mark.parametrize("status", ["Restricted", "Blocked"])
def test_legal_identities_refuse_case_space_aliases(table: str, status: str, rules: Rules) -> None:
    text = synthetic_handoff(rules).replace("qa_status: Restricted", f"qa_status: {status}")
    row = "| " + " | ".join(parse(text).tables[table].rows[0]) + " |"
    text = text.replace(row, row + "\n" + row.replace("TEST", " test "))
    code, found = check(text, contract("CP-4", rules), rules)
    assert code == 2 and any(f.code == "duplicate_row_key" for f in found)


@pytest.mark.parametrize(
    "change", ["column", "row", "tag", "critical", "document-column", "document-tag"]
)
def test_critical_and_malformed_gates_remain_strict(change: str, rules: Rules) -> None:
    text = synthetic_handoff(rules)
    old, new = {
        "column": ("| direction |", "| wrong |"),
        "row": ("| TEST coverage |", "| TEST coverage | extra |"),
        "tag": ("<!-- table: cp4.covenant_tests -->", "<!-- table: missing -->"),
        "critical": ("| Floor |", "| — |"),
        "document-column": ("| document_type |", "| wrong |"),
        "document-tag": ("<!-- table: cp4.document_register -->", "<!-- table: missing -->"),
    }[change]
    assert check(text.replace(old, new), contract("CP-4", rules), rules)[0] == 2


@pytest.mark.corpus
def test_primary_shortage_blocks_without_fabricated_headroom(
    prepared_run: Callable[[str], Path], rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    text = fixture("CP-4")
    assert check(text, contract("CP-4", rules), rules, run) == (3, [])
    h = parse(text)
    assert not h.tables["citations"].rows
    assert "executed" in text and "current tested legal ratios" in text
    assert "basket utilization" in text and "SSIM" in text
    assert check(text, contract("CP-4", rules), rules, run / "absent")[0] == 1
    promoted = text.replace("qa_status: Blocked", "qa_status: Pass")
    assert check(promoted, contract("CP-4", rules), rules, run)[0] == 2
    forged = synthetic_handoff(rules).replace("calc: TEST-ONLY fictional record", "[C1]")
    forged += (
        "| C1 | CZR_Q2_2026_10Q.txt | note 7 | fabricated current legal denominator witness |\n"
    )
    code, found = check(forged, contract("CP-4", rules), rules, run)
    assert code == 2 and any(f.code == "citation_unanchored" for f in found)


def test_canonical_calc_grant_and_actual_cli(
    tmp_path: Path, rules: Rules, capsys: pytest.CaptureFixture[str]
) -> None:
    message = permission_message(tmp_path, "CP-4", rules)
    assert message["Allowed calculator"] == "covenant_headroom"
    assert message["May write only"] == [
        str(tmp_path / p)
        for p in (
            "handoffs/CP-4.md",
            "calc/CP-4-covenant_headroom.json",
            "calc/CP-4-covenant_headroom.out.json",
        )
    ]
    data: dict[str, Any] = {
        "tests": [
            {
                "test": "TEST coverage",
                "test_type": "Incurrence",
                "direction": "Floor",
                "threshold": "2",
                "current_value": "3",
                "unit_label": "x",
                "basis": "TEST legal basis",
                "cite": "TEST-ONLY fictional record",
            }
        ]
    }
    source, output = tmp_path / "input.json", tmp_path / "output.json"
    source.write_text(json.dumps(data))
    assert main(["calc", "covenant_headroom", "--in", str(source), "--out", str(output)]) == 0
    assert json.loads(output.read_text())["tests"][0]["headroom"] == "1"
    assert "TEST coverage" in capsys.readouterr().out
    data["tests"][0]["direction"] = "Ceiling"
    assert covenant_headroom.compute(data)["tests"][0]["headroom"] == "-1"


def test_full_catalog_order_and_quick_exclusion(rules: Rules) -> None:
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    full = pathway.depths["full"]
    assert full[full.index("CP-2A") + 1] == "CP-4"
    assert full.index("CP-4") < full.index("CP-3")
    assert "CP-4" not in pathway.depths["quick"]
    contracts = load_contracts(RBOT_ROOT, rules, [])
    assert _order(pathway, full, contracts, rules.host_producers) == []
    bad = ("CP-4", *(s for s in full if s != "CP-4"))
    assert any(
        "CP-4 runs before its input MODEL" in p
        for p in _order(pathway, bad, contracts, rules.host_producers)
    )


def test_retained_legal_capacity_structure_and_intercreditor_method() -> None:
    prompt = (RBOT_ROOT / "modules/CP-4/MODULE.md").read_text()
    for term in (
        "executed governing",
        "six-rank",
        "controlling amendments",
        "Standard Finding Format",
        "Maintenance/Incurrence/Springing",
        "Ceiling/Floor",
        "never substitute",
        "SSIM",
        "independence_cite",
        "shared caps",
        "reclassification",
        "current_debt",
        "ebitda_denominated",
        "entity \u00d7 tranche",
        "entity \u00d7 lien",
        "stranded value",
        "standstill",
        "turnover",
        "purchase options",
        "payment priority",
        "sacred rights",
        "strongest supported counter-case",
        "nearest pressure point",
        "Not Scorable",
        "Overall (composite)",
        "supported 1\u20135 score only with at least three scorable areas",
        "highest creditor-adverse severity and most material credit implication",
        "Score Rationale and Status (Completed / Provisional / Not Scorable)",
        "never invent an overall score",
        "never the CR Score",
        "No fetching",
        "does not establish host origin",
        "non-debt funding",
        "Subsequent events",
        "one input",
    ):
        assert term.casefold() in prompt.casefold()


@pytest.mark.parametrize(
    "name", ["calc", "calc/CP-4-covenant_headroom.json", "calc/CP-4-covenant_headroom.out.json"]
)
def test_calc_grant_keeps_path_guards(tmp_path: Path, rules: Rules, name: str) -> None:
    from rbotlib.inventory import RunError

    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(tmp_path / "foreign")
    with pytest.raises(RunError, match="symlink"):
        permission_message(tmp_path, "CP-4", rules)
