"""SYNTHETIC source/calculator witnesses; no analytical or live-method qualification."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from test_cp1c_module import permission_message
from test_modules import contract, fixture

from builders import make_run
from conftest import FIXTURES
from rbotlib.calc import rate_fx_sensitivity as rf
from rbotlib.catalog import _order, check_tree, load_catalog, load_contracts
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check

EXCERPTS = (
    "Debt total 1000; gross floating 500; fixed 500; qualified hedged 300.",
    "Swap1 notional 400, rate 3%, covers Debt; linear protection on qualified 300.",
    "FX transaction net exposure 120; adverse decimal shock 0.10.",
    "Energy annual spend 80; adverse decimal shock 0.25.",
)
SOURCE = "SYNTHETIC_RATE_TERMS.md"


def synthetic_input() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(
        (FIXTURES / "calc/CP-2E-rate_fx_sensitivity.json").read_text()
    )
    return data


def synthetic_handoff(rules: Rules, data: dict[str, Any]) -> str:
    out = rf.compute(data)
    q = data["hedge_qualification"]
    text = """---
module_id: CP-2E
run_id: SYNTHETIC
issuer_id: SYNTHETIC
analysis_date: 2026-01-01
qa_status: Restricted
inputs: CP-0, CP-1, MODEL
---

## Analysis

SYNTHETIC mechanical witness only. USD MILLIONS, SYNTHETIC Group, calendar2026.
Qualified protection differs from notional; higher cash cost weakens FCF/liquidity.
This exercises structure, source anchoring and exact calculator transcription only.
"""
    text += "\n" + str(out["sign_convention"]) + "\n\n## Tables\n\n"
    exposures = [
        dict(
            exposure="Debt",
            kind="Rates",
            amount="500",
            hedge_status="Partial",
            transmission="Rate reset raises interest",
            credit_implication="Lower FCF",
            cite="[C1] [C2]",
        ),
        dict(
            exposure="FX",
            kind="FX",
            amount="120",
            hedge_status="Transaction unhedged",
            transmission="Currency shock consumes cash",
            credit_implication="Lower liquidity",
            cite="[C3]",
        ),
        dict(
            exposure="Energy",
            kind="Commodity",
            amount="80",
            hedge_status="No pass-through",
            transmission="Input shock raises costs",
            credit_implication="Lower FCF",
            cite="[C4]",
        ),
    ]
    rows = {
        "cp2e.exposures": [dict(r, currency="USD", unit="MILLIONS") for r in exposures],
        "cp2e.sensitivities": out["sensitivities"],
        "cp2e.hedges": [
            dict(
                hedge="Swap1",
                notional=q["notional"],
                currency="USD",
                unit="MILLIONS",
                covered_instrument="Debt",
                rate_or_strike=q["rate_or_strike"],
                maturity_date=q["maturity_date"],
                cite="[C2]",
            )
        ],
    }
    for table in contract("CP-2E", rules).tables:
        names = [c.name for c in table.columns]
        text += f"<!-- table: {table.id} -->\n| " + " | ".join(names) + " |\n"
        text += "|" + "---|" * len(names) + "\n"
        for row in rows[table.id]:
            text += "| " + " | ".join("—" if row[c] is None else str(row[c]) for c in names)
            text += " |\n"
        text += "\n"
    text += "## Gaps\n\nSYNTHETIC evidence; no real issuer conclusion or host-source proof.\n"
    text += "\n## Citations\n\n<!-- table: citations -->\n| id | source | locator | excerpt |\n"
    text += "|---|---|---|---|\n"
    return text + "".join(
        f"| C{i} | {SOURCE} | p1 | {excerpt} |\n" for i, excerpt in enumerate(EXCERPTS, 1)
    )


@pytest.fixture
def synthetic_run(tmp_path: Path) -> Path:
    pack = tmp_path / "SYNTHETIC-pack"
    pack.mkdir()
    text = "SYNTHETIC mechanical test; no real issuer facts.\n"
    text += "USD MILLIONS; SYNTHETIC Group; period 2026-01-01 to 2026-12-31.\n"
    text += "Swap coverage 2025-01-01 through 2027-12-31; maturity 2027-12-31.\n"
    text += "Debt, FX and Energy cash channels are distinct and non-overlapping.\n"
    text += "No energy pass-through; transaction FX unhedged.\n" + "\n".join(EXCERPTS)
    (pack / SOURCE).write_text(text)
    run = make_run(pack)
    for command in ("inventory", "prepare"):
        assert main([command, "--run", str(run)]) == 0
    return run


def test_synthetic_prepared_positive_restricted_and_source_failures(
    synthetic_run: Path, rules: Rules
) -> None:
    text = synthetic_handoff(rules, synthetic_input())
    for status in ("Restricted", "Pass"):
        assert check(
            text.replace("Restricted", status, 1), contract("CP-2E", rules), rules, synthetic_run
        ) == (0, [])
    bad = text.replace(EXCERPTS[0], "fabricated quote not supplied by this source")
    code, found = check(bad, contract("CP-2E", rules), rules, synthetic_run)
    assert code == 2 and any(f.code == "citation_unanchored" for f in found)
    assert check(text, contract("CP-2E", rules), rules, synthetic_run / "absent")[0] == 1
    assert [r[3] for r in parse(text).tables["cp2e.sensitivities"].rows] == [
        "2.00",
        "12.00",
        "20.00",
        "34.00",
    ]


@pytest.mark.parametrize(
    "field,value",
    [("qualified", False), ("linear_protection", False), ("coverage_end", "2026-06-30")],
)
def test_unqualified_notional_cannot_fill_critical_sensitivity(
    field: str, value: object, rules: Rules
) -> None:
    data = synthetic_input()
    data["hedge_qualification"][field] = value
    result = rf.compute(data)
    assert result["sensitivities"][0]["cash_impact"] is None
    assert result["sensitivities"][0]["reason"]
    assert result["sensitivities"][-1]["cash_impact"] is None
    code, found = check(synthetic_handoff(rules, data), contract("CP-2E", rules), rules)
    assert code == 2 and any(f.code == "critical_placeholder" for f in found)


def test_synthetic_blocked_null_keeps_source_gate(synthetic_run: Path, rules: Rules) -> None:
    data = synthetic_input()
    data["gross_floating_rate_debt"] = None
    text = synthetic_handoff(rules, data).replace("qa_status: Restricted", "qa_status: Blocked")
    text = text.split("| C1 |", 1)[0]
    for i in range(1, 5):
        text = text.replace(f"[C{i}]", "")
    assert check(text, contract("CP-2E", rules), rules, synthetic_run) == (3, [])
    assert check(text, contract("CP-2E", rules), rules, synthetic_run / "absent")[0] == 1


@pytest.mark.parametrize(
    "old,new",
    [
        ("| shock |", "| wrong |"),
        ("| +100 bps |", "| — |"),
        ("| Calculated |", "| Invented |"),
        ("<!-- table: cp2e.exposures -->", "<!-- table: wrong -->"),
    ],
)
def test_malformed_contract_is_refused(old: str, new: str, rules: Rules) -> None:
    text = synthetic_handoff(rules, synthetic_input()).replace(old, new, 1)
    assert check(text, contract("CP-2E", rules), rules)[0] == 2


@pytest.mark.corpus
def test_primary_is_honestly_blocked_with_usable_dated_disclosures(
    prepared_run: Callable[[str], Path], rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    text = fixture("CP-2E")
    assert check(text, contract("CP-2E", rules), rules, run) == (3, [])
    assert "no cash-flow hedges at June30" in text and "USD6.0bn" in text
    assert "10-Q Note2" in text  # Derivative Instruments is in Note2, not Goodwill Note4.
    assert not parse(text).tables["citations"].rows
    assert (
        check(
            text.replace("qa_status: Blocked", "qa_status: Restricted"),
            contract("CP-2E", rules),
            rules,
            run,
        )[0]
        == 2
    )


def test_exact_grant_cli_and_failed_input_preserves_output(
    synthetic_run: Path, rules: Rules, capsys: pytest.CaptureFixture[str]
) -> None:
    msg = permission_message(synthetic_run, "CP-2E", rules)
    assert msg["Allowed calculator"] == "rate_fx_sensitivity"
    assert msg["May write only"] == [
        str(synthetic_run / p)
        for p in (
            "handoffs/CP-2E.md",
            "calc/CP-2E-rate_fx_sensitivity.json",
            "calc/CP-2E-rate_fx_sensitivity.out.json",
        )
    ]
    source, output = (synthetic_run / p for p in msg["May write only"][1:])
    source.parent.mkdir(exist_ok=True)
    source.write_text(json.dumps(synthetic_input()))
    args = ["calc", "rate_fx_sensitivity", "--in", str(source), "--out", str(output)]
    assert main(args) == 0
    before = output.read_bytes()
    assert json.loads(before)["sensitivities"][-1]["cash_impact"] == "34.00"
    assert "positive = adverse annual cash cost" in capsys.readouterr().out
    source.write_text('{"basis":false}')
    assert main(args) == 1 and output.read_bytes() == before


@pytest.mark.parametrize(
    "name",
    ["calc", "calc/CP-2E-rate_fx_sensitivity.json", "calc/CP-2E-rate_fx_sensitivity.out.json"],
)
@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo"])
def test_grant_refuses_foreign_targets(tmp_path: Path, rules: Rules, name: str, kind: str) -> None:
    import os

    target, foreign = tmp_path / name, tmp_path / "foreign"
    foreign.write_text("SYNTHETIC foreign target")
    target.parent.mkdir(parents=True, exist_ok=True)
    if kind == "symlink":
        target.symlink_to(foreign)
    elif kind == "hardlink":
        target.hardlink_to(foreign)
    else:
        os.mkfifo(target)
    with pytest.raises(RunError):
        permission_message(tmp_path, "CP-2E", rules)
    assert foreign.read_text() == "SYNTHETIC foreign target"


def test_activation_order_and_full_method(rules: Rules) -> None:
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    full = pathway.depths["full"]
    assert full[full.index("CP-2A") + 1 : full.index("CP-2A") + 3] == ("CP-2E", "CP-4")
    assert "CP-2E" not in pathway.depths["quick"]
    assert check_tree(RBOT_ROOT, rules) == []
    contracts = load_contracts(RBOT_ROOT, rules, [])
    bad = ("CP-2E", *(m for m in full if m != "CP-2E"))
    assert any(
        "CP-2E runs before its input MODEL" in p
        for p in _order(pathway, bad, contracts, rules.host_producers)
    )
    prompt = (RBOT_ROOT / "modules/CP-2E/MODULE.md").read_text()
    for retained in (
        "macro Step 1",
        "Step 10",
        "sustainability Steps 7\u20139",
        "never recompute them",
        "no fetching",
        "Notional is not effective",
        "Translation exposure versus Transaction exposure",
        "Demand elasticity",
        "channels_nonoverlapping=true",
        "positive result is adverse",
        "KPI definition/ambition",
        "SPT thresholds and test dates",
        "step-up/step-down symmetry",
        "do not assume a green premium",
        "Immaterial to Credit",
        "greenwashing",
        "strongest supported counter-case",
        "Sidecars are model-authored assertions",
        "full-period coverage",
    ):
        assert retained.casefold() in prompt.casefold()
