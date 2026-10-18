"""Exact keyed comparison, independent ordering/precision properties and truthful gaps."""

import copy
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from test_prior_report import document, table

from rbotlib.diff import compare
from rbotlib.inventory import RunError
from rbotlib.prior_report import ComparisonKeyError, keyed_rows


def financial(doc: dict[str, Any], value: str = "100") -> None:
    table(
        doc,
        "snapshot.financial_columns",
        ["slot", "column_id", "period_id", "kind", "end_date"],
        [
            ["FY", "fy25", "FY2025", "FY", "2025-12-31"],
            ["LTM", "ltm26", "LTM2026", "LTM", "2026-06-30"],
        ],
    )
    table(
        doc,
        "snapshot.financials",
        ["line_id", "unit_label", "fy", "ltm", "cite"],
        [["debt", "USD m", "99", value, "calc: model.json line debt"]],
    )


def test_exact_expected_changes_and_limits() -> None:
    prior, current = document(), document()
    columns = ["facility_id", "outstanding", "rank", "currency", "unit", "column_basis"]
    table(
        prior,
        "snapshot.capital_structure",
        columns,
        [["A", "100.01", "1", "USD", "MILLIONS", "LTM"]],
    )
    table(
        current,
        "snapshot.capital_structure",
        columns,
        [["A", "100.02", "1", "USD", "MILLIONS", "LTM"], ["B", "0", "2", "USD", "MILLIONS", "LTM"]],
    )
    for doc in (prior, current):
        financial(doc)
    table(prior, "snapshot.catalysts", ["event", "timing"], [["Sale", "2027"]])
    table(current, "snapshot.catalysts", ["event", "timing"], [])
    table(
        prior,
        "model.house",
        ["item", "value", "unit_label", "column_id"],
        [["debt", "0", "USD m", "ltm26"]],
    )
    table(
        current,
        "model.house",
        ["item", "value", "unit_label", "column_id"],
        [["debt", "1", "USD m", "ltm26"]],
    )
    result = compare(
        prior, current, ["snapshot.capital_structure", "snapshot.catalysts", "model.house"]
    )
    assert result["prior"] == {
        "run_id": "earlier",
        "report_date": "2026-10-14",
        "pathway": prior["pathway"],
        "depth": "full",
    }
    debt = next(
        x
        for x in result["changes"]
        if x["field"] == "outstanding" and x["key"] == {"facility_id": "A"}
    )
    assert debt == {
        "table": "snapshot.capital_structure",
        "key": {"facility_id": "A"},
        "field": "outstanding",
        "prior": "100.01",
        "current": "100.02",
        "kind": "changed",
        "numeric": True,
        "context": debt["context"],
        "reason": None,
    }
    assert any(x["kind"] == "unchanged" for x in result["changes"])
    assert any(x["kind"] == "added" and x["prior"] is None for x in result["changes"])
    assert any(x["kind"] == "removed" and x["current"] is None for x in result["changes"])
    assert next(
        x for x in result["changes"] if x["table"] == "model.house" and x["field"] == "value"
    )["numeric"]
    del current["handoffs"]["MODEL"]["tables"]["snapshot.catalysts"]
    result = compare(prior, current, ["snapshot.catalysts"])
    assert result["changes"] == [] and "snapshot.catalysts" in str(result["limitations"])


@pytest.mark.parametrize("failure", ["issuer", "duplicate", "blank", "unknown", "single"])
def test_identity_refusals(failure: str) -> None:
    prior, current = document(), document()
    name = "model.house"
    table(current, name, ["item", "value"], [["debt", "1"]])
    if failure == "issuer":
        current["run_brief"]["front_matter"]["issuer_id"] = "OTHER"
        current["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][1] = "OTHER"
        current["handoffs"]["MODEL"]["front_matter"]["issuer_id"] = "OTHER"
    elif failure == "unknown":
        name = "new.unknown"
    elif failure == "single":
        name = "snapshot.run_header"
        current["run_brief"]["tables"][name]["rows"] *= 2
    elif failure == "blank":
        table(current, name, ["item", "value"], [["—", "1"]])
    else:
        table(current, name, ["item", "value"], [["debt", "1"], ["debt", "2"]])
    if failure in ("duplicate", "blank"):
        table(prior, name, ["item", "value"], [["debt", "1"]])
        with pytest.raises(ComparisonKeyError):
            keyed_rows(name, current["handoffs"]["MODEL"]["tables"][name])
        result = compare(prior, current, [name])
        assert result["changes"] == []
        assert any(name in v and "comparison declined" in v for v in result["limitations"])
    else:
        with pytest.raises(RunError):
            compare(prior, current, [name])


@pytest.mark.parametrize(
    "value", ["—", "1,000", "1e3", "NaN", "Infinity", "2%", "2026-01-01", "2 units"]
)
def test_non_numeric_and_latest_gap_never_falls_back(value: str) -> None:
    prior, current = document(), document()
    financial(prior, "0")
    financial(current, value)
    change = next(
        x
        for x in compare(prior, current, ["snapshot.financials"])["changes"]
        if x["field"] == "latest"
    )
    assert change["current"] == value and not change["numeric"] and change["reason"]
    assert change["context"]["current"]["column_id"] == "ltm26"


@pytest.mark.parametrize("defect", ["period", "unit", "failed", "blocked"])
def test_non_comparable_context_is_visible(defect: str) -> None:
    prior, current = document(), document()
    financial(prior)
    financial(current, "101")
    if defect == "period":
        current["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]["rows"][1][-1] = (
            "2026-09-30"
        )
    elif defect == "unit":
        current["handoffs"]["MODEL"]["tables"]["snapshot.financials"]["rows"][0][1] = "mystery"
    else:
        current["steps"]["MODEL"]["status"] = defect
        current["handoffs"]["MODEL"]["status"] = defect
    result = compare(prior, current, ["snapshot.financials"])
    assert not any(x["numeric"] for x in result["changes"])
    assert result["limitations"] or any(x["reason"] for x in result["changes"])


@given(st.decimals(allow_nan=False, allow_infinity=False, places=12), st.permutations([0, 1, 2]))
def test_precision_identity_and_column_permutation(value: Decimal, order: list[int]) -> None:
    prior, current = document(), document()
    columns, row = ["item", "value", "formula"], ["debt", format(value, "f"), "original"]
    table(prior, "model.house", columns, [row])
    table(current, "model.house", [columns[i] for i in order], [[row[i] for i in order]])
    result = compare(prior, current, ["model.house"])
    assert all(x["kind"] == "unchanged" for x in result["changes"])
    assert next(x for x in result["changes"] if x["field"] == "value")["prior"] == format(
        value, "f"
    )


@given(st.lists(st.text(alphabet="ABCDEF", min_size=1, max_size=5), unique=True, max_size=10))
def test_row_order_and_add_remove_reverse(keys: list[str]) -> None:
    prior, current = document(), document()
    table(prior, "model.house", ["item", "value"], [[k, "1"] for k in keys])
    table(current, "model.house", ["item", "value"], [[k, "1"] for k in reversed(keys)])
    assert (
        compare(prior, current, ["model.house"])["changes"]
        == compare(prior, prior, ["model.house"])["changes"]
    )
    empty = copy.deepcopy(current)
    empty["handoffs"]["MODEL"]["tables"]["model.house"]["rows"] = []
    added = compare(empty, prior, ["model.house"])["changes"]
    removed = compare(prior, empty, ["model.house"])["changes"]
    assert [(x["key"], x["current"]) for x in added] == [(x["key"], x["prior"]) for x in removed]
    assert all(x["kind"] == "added" for x in added) and all(x["kind"] == "removed" for x in removed)


def test_latest_tie_prefers_ltm_and_projection_does_not_borrow_history() -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc, "—")
        doc["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]["rows"][0][-1] = (
            "2026-06-30"
        )
        table(doc, "model.summary", ["line_id", "unit_label", "pf_ltm"], [["debt", "USD m", "1"]])
    result = compare(prior, current, ["snapshot.financials", "model.summary"])
    latest = next(x for x in result["changes"] if x["field"] == "latest")
    assert latest["prior"] == "—" and latest["context"]["prior"]["slot"] == "LTM"
    assert not next(x for x in result["changes"] if x["field"] == "pf_ltm")["numeric"]


@pytest.mark.parametrize("defect", ["duplicate", "missing", "blank"])
def test_native_bridge_declines_only_ambiguous_table(defect: str) -> None:
    prior, current = document(), document()
    name = "snapshot.ebitda_adjustments"
    label = "Add-back: Run-rate cost synergies (unrealised), excluded if positive"
    for doc in (prior, current):
        table(
            doc,
            name,
            ["line", "kind", "amount"],
            [[label, "Add-back", "150"], [label, "Unrealized add-back", "-150"]],
        )
        table(doc, "snapshot.catalysts", ["event", "timing"], [["Sale", "2027"]])
    if defect == "missing":
        table(current, name, ["amount"], [])
    elif defect == "blank":
        current["handoffs"]["MODEL"]["tables"][name]["rows"][0][0] = "—"
    with pytest.raises(ComparisonKeyError):
        keyed_rows(name, current["handoffs"]["MODEL"]["tables"][name])
    result = compare(prior, current, [name, "snapshot.catalysts", "cp8.ignored"])
    assert len(result["changes"]) == 1 and result["changes"][0]["table"] == "snapshot.catalysts"
    assert any(name in v and "comparison declined" in v for v in result["limitations"])


@pytest.mark.parametrize("status", ["failed", "skipped", "Blocked", "blocked"])
def test_unavailable_owner_never_establishes_absence(status: str) -> None:
    prior, current = document(), document()
    table(prior, "model.house", ["item", "value"], [["debt", "1"]])
    table(current, "model.house", ["item", "value"], [])
    current["handoffs"]["MODEL"]["status"] = current["steps"]["MODEL"]["status"] = status
    result = compare(prior, current, ["model.house"])
    assert result["changes"] == [] and "owner not accepted" in str(result["limitations"])


@pytest.mark.parametrize("defect", ["duplicate-slot", "tie", "missing", "unaccepted"])
def test_ambiguous_or_unaccepted_period_context_never_selects(defect: str) -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc)
        columns = doc["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]
        if defect == "duplicate-slot":
            columns["rows"].append(["LTM", "ltm-other", "LTM-other", "LTM", "2026-09-30"])
        elif defect == "tie":
            columns["rows"].append(["YTD", "other", "other", "LTM", "2026-06-30"])
        elif defect == "missing":
            del doc["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]
        else:
            ctx = copy.deepcopy(doc["handoffs"]["MODEL"])
            ctx["status"], ctx["tables"] = "Blocked", {"snapshot.financial_columns": columns}
            doc["handoffs"]["CONTEXT"] = ctx
            doc["steps"]["CONTEXT"] = {"status": "Blocked"}
            del doc["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]
    change = next(
        x
        for x in compare(prior, current, ["snapshot.financials"])["changes"]
        if x["field"] == "latest"
    )
    assert "column_id" not in change["context"]["prior"]
    assert (
        change["prior"] is None
        and not change["numeric"]
        and change["context"]["prior"]["gap_reason"]
    )


def test_actual_pf_slot_never_supplies_historical_summary_context() -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc)
        doc["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]["rows"][1][3] = "PF_LTM"
        table(
            doc,
            "model.summary",
            ["line_id", "unit_label", "ltm", "pf_ltm"],
            [["debt", "USD m", "1", "2"]],
        )
        table(
            doc,
            "model.projection_summary",
            ["case", "fiscal_year", "value", "unit_label"],
            [["BASE", "2027", "3", "USD m"]],
        )
    result = compare(prior, current, ["model.summary", "model.projection_summary"])
    assert not next(x for x in result["changes"] if x["field"] == "ltm")["numeric"]
    assert next(x for x in result["changes"] if x["field"] == "pf_ltm")["numeric"]
    assert not any(
        x["numeric"] for x in result["changes"] if x["table"] == "model.projection_summary"
    )


def test_exact_contract_strategy_sources_null_and_no_input_mutation() -> None:
    prior, current = document(), document()
    prior["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][-1] = "2026-10-13"
    table(
        prior,
        "snapshot.recommendation",
        ["strategy", "recommendation", "cite"],
        [["Carry", "Hold", "[C1]"]],
    )
    table(
        current,
        "snapshot.recommendation",
        ["strategy", "recommendation", "cite", "note"],
        [["Carry", "Buy", "[C2]", "—"]],
    )
    frozen = copy.deepcopy((prior, current))
    context = {"unit": "", "basis": None, "gap_reason": None}
    expected = []
    for field, a, b in (
        ("cite", "[C1]", "[C2]"),
        ("note", None, "—"),
        ("recommendation", "Hold", "Buy"),
    ):
        contexts = {"prior": dict(context), "current": dict(context)}
        if field == "note":
            contexts["prior"]["gap_reason"], contexts["current"]["gap_reason"] = (
                "missing selected value/context",
                "source gap",
            )
        expected.append(
            {
                "table": "snapshot.recommendation",
                "key": {"strategy": "Carry"},
                "field": field,
                "prior": a,
                "current": b,
                "kind": "changed",
                "numeric": False,
                "context": contexts,
                "reason": "not a governed metric field",
            }
        )
    assert compare(prior, current, ["snapshot.recommendation"]) == {
        "prior": {
            "run_id": "earlier",
            "report_date": "2026-10-13",
            "pathway": "FULL_CREDIT_ASSESSMENT",
            "depth": "full",
        },
        "date_basis": {"prior": "report_date", "current": "generated_at"},
        "changes": expected,
        "limitations": [],
    }
    assert (prior, current) == frozen


@pytest.mark.parametrize("defect", ["currency", "scale", "basis", "period-id", "unknown-kind"])
def test_numeric_requires_all_context_dimensions(defect: str) -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc, "-123456789012345678901234567890.000000000001")
    t = current["handoffs"]["MODEL"]["tables"]
    if defect in ("currency", "scale"):
        t["snapshot.financials"]["rows"][0][1] = "EUR m" if defect == "currency" else "USD k"
    elif defect == "basis":
        t["snapshot.financials"]["columns"].append("basis")
        t["snapshot.financials"]["rows"][0].append("unknown")
    else:
        t["snapshot.financial_columns"]["rows"][1][2 if defect == "period-id" else 3] = "unknown"
    latest = next(
        x
        for x in compare(prior, current, ["snapshot.financials"])["changes"]
        if x["field"] == "latest"
    )
    assert not latest["numeric"] and latest["reason"]


@pytest.mark.parametrize("field", ["latest", "rank", "date", "id"])
def test_numeric_looking_descriptive_source_fields_stay_exact(field: str) -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc)
        table(
            doc,
            "snapshot.capital_structure",
            ["facility_id", "unit_label", "column_basis", field],
            [["A", "USD m", "LTM", "123"]],
        )
    change = next(
        x
        for x in compare(prior, current, ["snapshot.capital_structure"])["changes"]
        if x["field"] == field
    )
    assert change["prior"] == "123" and change["current"] == "123" and not change["numeric"]


@pytest.mark.parametrize("kind", ["UNKNOWN", "PROJECTION"])
def test_matching_unknown_period_kinds_never_make_numeric(kind: str) -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc)
        doc["handoffs"]["MODEL"]["tables"]["snapshot.financial_columns"]["rows"][1][3] = kind
    change = next(
        x
        for x in compare(prior, current, ["snapshot.financials"])["changes"]
        if x["field"] == "latest"
    )
    assert change["prior"] == "100" and not change["numeric"] and change["reason"]


def test_exact_decimal_spelling_and_complete_latest_context() -> None:
    prior, current = document(), document()
    financial(prior, "1.0")
    financial(current, "1.00")
    change = next(
        x
        for x in compare(prior, current, ["snapshot.financials"])["changes"]
        if x["field"] == "latest"
    )
    assert (change["prior"], change["current"], change["kind"], change["numeric"]) == (
        "1.0",
        "1.00",
        "changed",
        True,
    )
    assert change["context"]["prior"] == {
        "slot": "LTM",
        "column_id": "ltm26",
        "period_id": "LTM2026",
        "kind": "LTM",
        "end_date": "2026-06-30",
        "unit": "USD m",
        "basis": "LTM",
        "gap_reason": None,
    }


def test_strategy_key_movement_is_exact_addition_and_removal() -> None:
    prior, current = document(), document()
    table(prior, "snapshot.recommendation", ["strategy", "recommendation"], [["Carry", "Hold"]])
    table(current, "snapshot.recommendation", ["strategy", "recommendation"], [["Income", "Buy"]])
    changes = compare(prior, current, ["snapshot.recommendation"])["changes"]
    assert [(x["key"], x["kind"], x["prior"], x["current"]) for x in changes] == [
        ({"strategy": "Carry"}, "removed", "Hold", None),
        ({"strategy": "Income"}, "added", None, "Buy"),
    ]


def test_house_gap_reason_is_visible_when_source_reason_is_gap() -> None:
    prior, current = document(), document()
    for doc in (prior, current):
        financial(doc)
        table(
            doc,
            "model.house",
            ["item", "value", "unit_label", "column_id", "reason"],
            [["debt", "—", "USD m", "ltm26", "—"]],
        )
    value = next(
        x for x in compare(prior, current, ["model.house"])["changes"] if x["field"] == "value"
    )
    assert value["context"]["prior"]["gap_reason"] == "source gap"
