"""TEST-ONLY numerical witnesses; supplied Primary is truthfully source-limited."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest
from test_cp1c_module import permission_message
from test_liquidity_bridge import payload
from test_modules import contract, fixture

from rbotlib.calc import liquidity_bridge as lb
from rbotlib.catalog import _order, load_catalog, load_contracts
from rbotlib.cli import main
from rbotlib.handoff import parse
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, Rules
from rbotlib.validate import check


def witness(rules: Rules, missing: bool = False) -> str:
    """Calculator output is authored arithmetic, never verified source/host provenance."""
    data = payload()
    data["unit"] = "MILLIONS"
    for row in data["liquidity_sources"] + data["components"]:
        row.update(unit="MILLIONS", cite="calc: TEST-ONLY assertions")
    if missing:
        data["components"][2]["amount"] = None
    out = lb.compute(data)
    text = fixture("CP-2D")
    if not missing:
        text = text.replace("qa_status: Blocked", "qa_status: Restricted")
    rows_by_table = {
        "cp2d.liquidity_sources": [
            dict(r, restriction="TEST-ONLY availability assertion")
            for r in out["liquidity_sources"]
        ],
        "cp2d.cash_uses_12m": [dict(r, use=r["id"]) for r in out["components"][2:]],
        "cp2d.bridge": out["bridge"],
        "cp2d.runway": out["runway"],
    }
    lines = []
    for table in contract("CP-2D", rules).tables:
        columns = [c.name for c in table.columns]
        lines += [
            f"<!-- table: {table.id} -->",
            "| " + " | ".join(columns) + " |",
            "|" + "---|" * len(columns),
        ]
        lines += [
            "| " + " | ".join("—" if r.get(c) is None else str(r[c]) for c in columns) + " |"
            for r in rows_by_table[table.id]
        ]
        lines.append("")
    return (
        text[: text.index("<!-- table: cp2d.liquidity_sources -->")]
        + "\n".join(lines)
        + text[text.index("## Gaps") :]
    )


def test_complete_and_partial_calculator_handoff(rules: Rules) -> None:
    text = witness(rules)
    assert check(text, contract("CP-2D", rules), rules) == (0, [])
    assert check(text.replace("Restricted", "Pass", 1), contract("CP-2D", rules), rules) == (0, [])
    blocked = witness(rules, missing=True)
    assert check(blocked, contract("CP-2D", rules), rules) == (3, [])
    assert (
        check(
            blocked.replace("qa_status: Blocked", "qa_status: Restricted"),
            contract("CP-2D", rules),
            rules,
        )[0]
        == 2
    )
    rows = parse(blocked).tables["cp2d.runway"].rows
    assert [r[1] for r in rows[:4]] == ["250", "—", "—", "—"]
    assert parse(blocked).tables["cp2d.bridge"].rows[-1][2] == "—"


@pytest.mark.parametrize(
    "table,key",
    [
        ("liquidity_sources", "component"),
        ("cash_uses_12m", "use"),
        ("bridge", "step"),
        ("runway", "item"),
    ],
)
def test_duplicate_identity_refuses_even_blocked(table: str, key: str, rules: Rules) -> None:
    text = witness(rules)
    parsed = parse(text).tables["cp2d." + table]
    row = "| " + " | ".join(parsed.rows[0]) + " |"
    alias = list(parsed.rows[0])
    alias[parsed.columns.index(key)] = "  " + alias[parsed.columns.index(key)].upper() + "  "
    text = text.replace(row, row + "\n| " + " | ".join(alias) + " |")
    for status in ("Restricted", "Blocked"):
        code, findings = check(
            text.replace("qa_status: Restricted", f"qa_status: {status}"),
            contract("CP-2D", rules),
            rules,
        )
        assert code == 2 and any(f.code == "duplicate_row_key" for f in findings)


@pytest.mark.parametrize(
    "table,column", [("liquidity_sources", "restriction"), ("cash_uses_12m", "timing")]
)
def test_distinct_access_buckets_and_payment_timings_are_not_duplicate_labels(
    table: str, column: str, rules: Rules
) -> None:
    text = witness(rules)
    parsed = parse(text).tables["cp2d." + table]
    original = "| " + " | ".join(parsed.rows[0]) + " |"
    distinct = list(parsed.rows[0])
    distinct[parsed.columns.index(column)] = "TEST-ONLY separate bucket/schedule"
    text = text.replace(original, original + "\n| " + " | ".join(distinct) + " |")
    assert check(text, contract("CP-2D", rules), rules) == (0, [])


@pytest.mark.parametrize(
    "old,new",
    [
        ("| Opening total |", "| Delta |"),
        ("| Closing total |", "| Use |"),
        ("| Use |", "| Opening total |"),
        ("| Months of runway |", "| Invented metric |"),
        ("<!-- table: cp2d.bridge -->", "<!-- table: missing -->"),
        ("| Accessible liquidity | 250 |", "| Accessible liquidity | — |"),
    ],
)
def test_bridge_order_runway_identity_and_generic_gates(old: str, new: str, rules: Rules) -> None:
    assert check(witness(rules).replace(old, new, 1), contract("CP-2D", rules), rules)[0] == 2


def test_full_runway_required_despite_minimum_four(rules: Rules) -> None:
    text = witness(rules)
    row = "| " + " | ".join(parse(text).tables["cp2d.runway"].rows[-1]) + " |\n"
    assert next(t for t in contract("CP-2D", rules).tables if t.id == "cp2d.runway").min_rows == 4
    assert check(text.replace(row, ""), contract("CP-2D", rules), rules)[0] == 2


@pytest.mark.corpus
def test_primary_blocked_and_source_availability(
    prepared_run: Callable[[str], Path], rules: Rules
) -> None:
    run = prepared_run("czr-2026q2-primary")
    assert check(fixture("CP-2D"), contract("CP-2D", rules), rules, run) == (3, [])
    assert check(fixture("CP-2D"), contract("CP-2D", rules), rules, run / "absent")[0] == 1
    assert (
        check(
            fixture("CP-2D").replace("qa_status: Blocked", "qa_status: Restricted"),
            contract("CP-2D", rules),
            rules,
            run,
        )[0]
        == 2
    )


def test_canonical_grant_and_real_cli(
    tmp_path: Path, rules: Rules, capsys: pytest.CaptureFixture[str]
) -> None:
    msg = permission_message(tmp_path, "CP-2D", rules)
    assert msg["Allowed calculator"] == "liquidity_bridge"
    assert msg["May write only"] == [
        str(tmp_path / p)
        for p in (
            "handoffs/CP-2D.md",
            "calc/CP-2D-liquidity_bridge.json",
            "calc/CP-2D-liquidity_bridge.out.json",
        )
    ]
    source, output = (
        tmp_path / "calc/CP-2D-liquidity_bridge.json",
        tmp_path / "calc/CP-2D-liquidity_bridge.out.json",
    )
    source.parent.mkdir(exist_ok=True)
    source.write_text(json.dumps(payload()))
    assert main(["calc", "liquidity_bridge", "--in", str(source), "--out", str(output)]) == 0
    assert json.loads(output.read_text())["ending_accessible_liquidity"]["value"] == "180"
    assert "Pinch point" in capsys.readouterr().out


@pytest.mark.parametrize(
    "name", ["calc", "calc/CP-2D-liquidity_bridge.json", "calc/CP-2D-liquidity_bridge.out.json"]
)
@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo"])
def test_grant_refuses_unsafe_targets(tmp_path: Path, rules: Rules, name: str, kind: str) -> None:
    path, foreign = tmp_path / name, tmp_path / "foreign"
    foreign.write_text("TEST-ONLY")
    path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "symlink":
        path.symlink_to(foreign)
    elif kind == "hardlink":
        path.hardlink_to(foreign)
    else:
        os.mkfifo(path)
    with pytest.raises(RunError):
        permission_message(tmp_path, "CP-2D", rules)


def test_order_and_method(rules: Rules) -> None:
    pathway = load_catalog(RBOT_ROOT).pathway("FULL_CREDIT_ASSESSMENT")
    assert pathway is not None
    full = pathway.depths["full"]
    assert full[full.index("CP-4") + 1 : full.index("CP-4") + 3] == ("CP-2D", "CP-3")
    assert "CP-2D" not in pathway.depths["quick"]
    contracts = load_contracts(RBOT_ROOT, rules, [])
    assert _order(pathway, full, contracts, rules.host_producers) == []
    bad = ("CP-2D", *(s for s in full if s != "CP-2D"))
    assert any(
        "CP-2D runs before its input MODEL" in p
        for p in _order(pathway, bad, contracts, rules.host_producers)
    )
    prompt = (RBOT_ROOT / "modules/CP-2D/MODULE.md").read_text()
    for retained in (
        "Step 10",
        "burn <=0",
        "all five",
        "ocf_includes=[]",
        "never recompute them",
        "jurisdictional",
        "non-debt funding float",
        "source versus normalized",
        "model-authored assertions",
        "strongest supported counter-case",
        "Not Calculable",
        "execution timing, cost",
        "Reported; Calculated; Provisional",
        "Sponsor support dependence",
    ):
        assert retained in prompt
