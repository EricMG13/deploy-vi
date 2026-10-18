"""Pure CP4 signed arithmetic; evidence is supplied by the analyst, never verified here.

Input: {tests: [...], baskets: [...] (optional)}; at most 1000 rows per list.
Each test requires test (unique), test_type (Maintenance/Incurrence/Springing), direction
(Ceiling/Floor, mandatory independently of type/name), threshold/current_value (figure/null),
unit_label, basis (governing legal definition), cite; optional period (text).
Ceiling = threshold-current; Floor = current-threshold. Zero alone is Tight.

Optional test.incremental_debt requires governing_ebitda/current_debt (figure/null),
ebitda_denominated (bool), basis, cite (legal formula), ebitda_cite, debt_cite, currency,
unit, perimeter, period (all nonempty text). Only an explicitly EBITDA-denominated Ceiling
with matching governing basis/declared test period, unit_label x and positive EBITDA can compute
threshold*governing_ebitda-current_debt. Input debt is the already governed/netted/pro-forma
numerator, not automatically gross debt. Reported/house EBITDA is never an implicit fallback.

Each optional basket requires basket (unique), capacity/used (nonnegative figure/null),
capacity_type, currency, unit, perimeter, period, basis, cite (legal/input/usage evidence),
independence (Independent/Overlapping/Unknown), independence_cite (text/null).
Capacity is an already sourced amount: arbitrary drafted formula strings are not evaluated.
Remaining = capacity-used, including negative overuse. Aggregate only if every row has
remaining and Independent with an independence citation and identical currency/unit/
perimeter/period/basis/capacity_type. Shared caps/reclassification require Overlapping or
Unknown; metadata and legal independence remain analyst assertions, not documentary proof.

Figures: finite decimal strings, integers or Decimal, never bool/float; <=100 coefficient
digits and exponent magnitude <=1000. Arithmetic uses a fresh fixed Decimal context with
4304 digits, inexact trapped: exact within these bounds including product/subtraction and
1000-row sums; no quantization, clamps, ambient-context dependence or positive Tight band.
Only explicit null means missing. Unknown keys/types, missing fields and duplicate identities
are refused before arithmetic. Output JSON numbers are strings/null with named reasons;
metadata is retained. No fetching, legal opinion, source authority or severity assignment.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Context, Decimal, Inexact, InvalidOperation, Overflow, Underflow, localcontext
from typing import Any

from rbotlib.calc.bond_analytics import CalcError

CONTEXT = Context(
    prec=4304, Emin=-10000, Emax=10000, traps=[Inexact, InvalidOperation, Overflow, Underflow]
)
FIGURE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
TEST = {
    "test",
    "test_type",
    "direction",
    "threshold",
    "current_value",
    "unit_label",
    "basis",
    "cite",
}
DEBT_NUMBERS = {"governing_ebitda", "current_debt"}
DEBT_TEXT = {"basis", "cite", "ebitda_cite", "debt_cite", "currency", "unit", "perimeter", "period"}
ALIGNMENT = ("currency", "unit", "perimeter", "period", "basis", "capacity_type")
BASKET_TEXT = {"basket", "cite", "independence", *ALIGNMENT}
BASKET = BASKET_TEXT | {"capacity", "used", "independence_cite"}
COLUMNS = (
    *("test", "test_type", "direction", "threshold", "current_value", "unit_label", "basis"),
    "headroom",
    "status",
    "cite",
)
LIMITATION = (
    "Arithmetic on supplied governing inputs only; does not verify evidence, legal "
    "applicability, source authority or independence; not legal advice. No severity assigned."
)


def _object(raw: object, required: set[str], optional: set[str], where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CalcError(f"{where}: needs an object")
    unknown, missing = raw.keys() - required - optional, required - raw.keys()
    if unknown or missing:
        raise CalcError(f"{where}: unknown {sorted(map(str, unknown))}; missing {sorted(missing)}")
    return dict(raw)


def _text(raw: object, where: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise CalcError(f"{where}: needs nonempty text")
    return raw.strip()


def _number(raw: object, where: str) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, str | int | Decimal):
        raise CalcError(f"{where}: needs finite decimal string/integer or null")
    try:
        text = str(raw).strip()
        if not FIGURE.fullmatch(text):
            raise CalcError(f"{where}: malformed or nonfinite figure")
        with localcontext(CONTEXT):
            value = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise CalcError(f"{where}: malformed or out-of-bounds figure") from exc
    if len(value.as_tuple().digits) > 100 or abs(int(value.as_tuple().exponent)) > 1000:
        raise CalcError(f"{where}: figure exceeds 100 digits / exponent magnitude 1000")
    return str(value)


def _metadata(item: dict[str, Any], keys: set[str], where: str) -> None:
    for key in keys:
        item[key] = _text(item[key], f"{where}.{key}")


def _choice(item: Mapping[str, Any], key: str, allowed: set[str], where: str) -> None:
    if item[key] not in allowed:
        raise CalcError(f"{where}.{key}: expected {sorted(allowed)}")


def _debt_input(raw: object, where: str) -> dict[str, Any]:
    item = _object(raw, DEBT_TEXT | DEBT_NUMBERS | {"ebitda_denominated"}, set(), where)
    _metadata(item, DEBT_TEXT, where)
    for key in DEBT_NUMBERS:
        item[key] = _number(item[key], f"{where}.{key}")
    if not isinstance(item["ebitda_denominated"], bool):
        raise CalcError(f"{where}.ebitda_denominated: needs bool")
    return item


def _test_input(raw: object, where: str) -> dict[str, Any]:
    item = _object(raw, TEST, {"period", "incremental_debt"}, where)
    _metadata(item, TEST - {"threshold", "current_value"}, where)
    _choice(item, "direction", {"Ceiling", "Floor"}, where)
    _choice(item, "test_type", {"Maintenance", "Incurrence", "Springing"}, where)
    for key in ("threshold", "current_value"):
        item[key] = _number(item[key], f"{where}.{key}")
    if "period" in item:
        item["period"] = _text(item["period"], f"{where}.period")
    if "incremental_debt" in item:
        item["incremental_debt"] = _debt_input(
            item["incremental_debt"], f"{where}.incremental_debt"
        )
    return item


def _basket_input(raw: object, where: str) -> dict[str, Any]:
    item = _object(raw, BASKET, set(), where)
    _metadata(item, BASKET_TEXT, where)
    _choice(item, "independence", {"Independent", "Overlapping", "Unknown"}, where)
    if item["independence_cite"] is not None:
        item["independence_cite"] = _text(item["independence_cite"], f"{where}.independence_cite")
    for key in ("capacity", "used"):
        item[key] = _number(item[key], f"{where}.{key}")
        if item[key] is not None and Decimal(item[key]) < 0:
            raise CalcError(f"{where}.{key}: must be nonnegative")
    return item


def _rows(raw: object, kind: str) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or len(raw) > 1000:
        raise CalcError(f"{kind}: needs a list of at most 1000 rows")
    parse, identity = (_test_input, "test") if kind == "tests" else (_basket_input, "basket")
    rows = [parse(item, f"{kind}[{index}]") for index, item in enumerate(raw)]
    if len({item[identity] for item in rows}) != len(rows):
        raise CalcError(f"{kind}.{identity}: duplicate identity")
    return rows


def _signed(value: Decimal | None, reason: str | None, field: str) -> dict[str, Any]:
    status = (
        "Not computable"
        if value is None
        else ("Headroom" if value > 0 else "Breached" if value < 0 else "Tight")
    )
    return {field: None if value is None else str(value), "status": status, "reason": reason}


def _incremental(item: Mapping[str, Any]) -> dict[str, Any]:
    debt = item["incremental_debt"]
    missing = [key for key in DEBT_NUMBERS if debt[key] is None]
    reason = None
    if item["direction"] != "Ceiling" or item["unit_label"] != "x":
        reason = "incremental debt requires an EBITDA-denominated Ceiling ratio in x"
    elif not debt["ebitda_denominated"] or debt["basis"] != item["basis"]:
        reason = "explicit EBITDA denominator and matching governing legal basis required"
    elif item.get("period", debt["period"]) != debt["period"]:
        reason = "test and incremental debt periods differ"
    elif item["threshold"] is None or missing:
        reason = "missing threshold / " + ", ".join(sorted(missing))
    elif Decimal(debt["governing_ebitda"]) <= 0:
        reason = "governing_ebitda must be positive"
    value = (
        None
        if reason
        else (
            Decimal(item["threshold"]) * Decimal(debt["governing_ebitda"])
            - Decimal(debt["current_debt"])
        )
    )
    return {
        **debt,
        "formula": "threshold * governing_ebitda - current_debt",
        **_signed(value, reason, "capacity"),
    }


def _calculate_test(item: dict[str, Any]) -> dict[str, Any]:
    threshold, current = item["threshold"], item["current_value"]
    missing = [key for key in ("threshold", "current_value") if item[key] is None]
    value = (
        None
        if missing
        else (
            Decimal(threshold) - Decimal(current)
            if item["direction"] == "Ceiling"
            else Decimal(current) - Decimal(threshold)
        )
    )
    output = {
        **item,
        **_signed(value, "missing " + ", ".join(missing) if missing else None, "headroom"),
    }
    if "incremental_debt" in item:
        output["incremental_debt"] = _incremental(item)
    return output


def _calculate_basket(item: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in ("capacity", "used") if item[key] is None]
    value = None if missing else Decimal(item["capacity"]) - Decimal(item["used"])
    return {
        **item,
        **_signed(value, "missing " + ", ".join(missing) if missing else None, "remaining"),
    }


def _aggregate_reason(baskets: list[dict[str, Any]]) -> str | None:
    reason = None
    if not baskets:
        reason = "no baskets supplied"
    elif any(b["remaining"] is None for b in baskets):
        reason = "missing basket capacity or used; no partial aggregate"
    elif any(b["independence"] != "Independent" or not b["independence_cite"] for b in baskets):
        reason = (
            "all routes require explicit independence with legal evidence; overlap/unknown excluded"
        )
    elif len({tuple(b[k] for k in ALIGNMENT) for b in baskets}) != 1:
        reason = "incompatible currency/unit/perimeter/period/basis/capacity_type"
    return reason


def _aggregate(baskets: list[dict[str, Any]]) -> dict[str, Any]:
    reason = _aggregate_reason(baskets)
    value = None if reason else sum((Decimal(b["remaining"]) for b in baskets), Decimal(0))
    return {
        **({k: baskets[0][k] for k in ALIGNMENT} if not reason else {}),
        **_signed(value, reason, "remaining"),
    }


def compute(data: object) -> dict[str, Any]:
    """Validate all rows before exact arithmetic; no I/O or input mutation."""
    top = _object(data, {"tests"}, {"baskets"}, "input")
    tests, baskets = _rows(top["tests"], "tests"), _rows(top.get("baskets", []), "baskets")
    with localcontext(CONTEXT):
        tests = [_calculate_test(item) for item in tests]
        baskets = [_calculate_basket(item) for item in baskets]
        aggregate = _aggregate(baskets)
    return {
        "schema": "rbot-calc-covenant-headroom/1",
        "tests": tests,
        "baskets": baskets,
        "aggregate": aggregate,
        "limitation": LIMITATION,
    }


def _cell(raw: object) -> str:
    return (
        "—" if raw is None else str(raw).replace("|", r"\|").replace("\n", " ").replace("\r", " ")
    )


def markdown(result: Mapping[str, Any]) -> str:
    """Owning covenant table columns plus explicit capacity/evidence/limitation text."""
    lines = [
        "<!-- cp4.covenant_tests -->",
        "| " + " | ".join(COLUMNS) + " |",
        "|" + "---|" * len(COLUMNS),
    ]
    for item in result["tests"]:
        lines.append("| " + " | ".join(_cell(item[k]) for k in COLUMNS) + " |")
        lines.append("Test detail: " + _cell({k: v for k, v in item.items() if k not in COLUMNS}))
    for item in result["baskets"]:
        lines.append("Basket: " + _cell(item))
    lines.extend(["Basket aggregate: " + _cell(result["aggregate"]), result["limitation"]])
    return "\n".join(lines) + "\n"
