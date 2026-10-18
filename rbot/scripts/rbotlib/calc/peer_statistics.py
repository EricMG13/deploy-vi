"""Pure CP1C peer statistics; JSON figures are decimal strings or integers, never floats.

Required top keys: metric_id, unit_label (plain text), borrower_value (figure/null),
peers (list, possibly empty). Optional: period, currency, definition_note, cite (text;
currency may be null), borrower_metric (figure/null), multiple_basis (Trading/Transaction).
Each peer requires peer (unique identity), value (figure/null), comparability,
calculation_status, period (text), currency (text/null). Optional peer keys: unit_label,
definition_note, multiple_basis, cite, selection_basis, limitation_note, outlier_reason
(text), outlier (bool, defaults false), age_months (nonnegative figure/null).
Reject unrecognized fields or statuses, ambiguous or nonfinite figures, and malformed metadata.
Only JSON null means unavailable; zero remains a measured value.

Close/Partial/Weak map to Comparable/Comparable with Limitations/Not Comparable; the
four reference comparability labels are also accepted. Calculation statuses are Reported,
Calculated, Derived, Provisional, Not Comparable, Insufficient Information. The last three,
Weak/reference exclusions, data over 18 months old and null values never count.
Assessment/evidence stays analyst-owned; ages over 12 months carry a stale warning.
Units, currencies, periods and declared definitions must agree among included peers and with
any top-level declaration. Omitted peer units inherit top units. Missing definition/borrower
alignment and provenance remain visible cautions; matching labels do not establish evidence.
Trading and Transaction are separate groups, never blended; an undeclared basis is a third
group, and cannot be used for implied EV. Multiples use unit_label 'x'. No currency conversion.

ACTIVE_PROMPT floors: range/min/max 2, median 3, quartiles 4, average 5. Inclusive R type 7
quartiles; even median averages the central pair. Decimal38 half-even, no display quantization.
Both outlier versions retain N/reasons and borrower positioning (Above/In line/Below only
with a median). Optional borrower_metric produces min/median/max implied EV only when positive,
on declared multiple bases; this is indicative context, not valuation/recovery evidence.
No source fetching, automatic comparability/outlier decisions or standard-deviation output.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, DecimalException, Underflow, localcontext
from typing import Any

from rbotlib.calc.bond_analytics import CONTEXT, CalcError, figure

TOP_REQUIRED = {"metric_id", "unit_label", "borrower_value", "peers"}
TOP_FIELDS = TOP_REQUIRED | {
    "period",
    "currency",
    "definition_note",
    "cite",
    "borrower_metric",
    "multiple_basis",
}
PEER_REQUIRED = {"peer", "value", "comparability", "calculation_status", "period", "currency"}
PEER_TEXT = {
    "unit_label",
    "definition_note",
    "multiple_basis",
    "cite",
    "selection_basis",
    "limitation_note",
    "outlier_reason",
}
PEER_FIELDS = PEER_REQUIRED | PEER_TEXT | {"outlier", "age_months"}
COMPARABILITY = {
    "Close": "Comparable",
    "Partial": "Comparable with Limitations",
    "Weak": "Not Comparable",
    **{
        k: k
        for k in (
            "Comparable",
            "Comparable with Limitations",
            "Not Comparable",
            "Insufficient Information",
        )
    },
}
STATUSES = {
    "Reported",
    "Calculated",
    "Derived",
    "Provisional",
    "Not Comparable",
    "Insufficient Information",
}
EXCLUDED = {"Not Comparable", "Insufficient Information", "Provisional"}
FLOORS = {"minimum": 2, "maximum": 2, "range": 2, "median": 3, "q1": 4, "q3": 4, "average": 5}
COLUMNS = (
    "metric_id",
    "unit_label",
    "borrower_value",
    "peer_min",
    "peer_q1",
    "peer_median",
    "peer_q3",
    "peer_max",
    "n",
    "position",
)


def _object(raw: object, allowed: set[str], required: set[str], where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CalcError(f"{where}: needs an object")
    unknown, missing = raw.keys() - allowed, required - raw.keys()
    if unknown or missing:
        raise CalcError(
            f"{where}: unknown keys {sorted(map(str, unknown))!r}; missing keys {sorted(missing)!r}"
        )
    return raw


def _text(raw: object, where: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise CalcError(f"{where}: needs non-empty text")
    return raw.strip()


def _number(raw: object, where: str) -> Decimal | None:
    return None if raw is None else figure(raw, where)


def _basis(raw: object, where: str) -> str:
    value = _text(raw, where)
    if value not in {"Trading", "Transaction"}:
        raise CalcError(f"{where}: needs Trading or Transaction")
    return value


def _peer(raw: object, index: int, top: Mapping[str, Any]) -> dict[str, Any]:
    where = f"peers[{index}]"
    p = dict(_object(raw, PEER_FIELDS, PEER_REQUIRED, where))
    for key in (PEER_REQUIRED - {"value", "currency"}) | (PEER_TEXT & p.keys()):
        p[key] = _text(p[key], f"{where}.{key}")
    if p["currency"] is not None:
        p["currency"] = _text(p["currency"], f"{where}.currency")
    if p["comparability"] not in COMPARABILITY:
        raise CalcError(f"{where}.comparability: unknown status")
    if p["calculation_status"] not in STATUSES:
        raise CalcError(f"{where}.calculation_status: unknown status")
    p["reference_comparability"] = COMPARABILITY[p["comparability"]]
    value = _number(p["value"], f"{where}.value")
    p["value"] = None if value is None else str(value)
    p["outlier"] = p.get("outlier", False)
    if not isinstance(p["outlier"], bool):
        raise CalcError(f"{where}.outlier: needs a bool")
    age = _number(p.get("age_months"), f"{where}.age_months")
    if age is not None and age < 0:
        raise CalcError(f"{where}.age_months: must be nonnegative")
    p["age_months"] = None if age is None else str(age)
    basis = p.get("multiple_basis", top.get("multiple_basis"))
    p["multiple_basis"] = None if basis is None else _basis(basis, f"{where}.multiple_basis")
    p["unit_label"] = p.get("unit_label", top["unit_label"])
    p["exclusion_reason"] = _exclusion(p, value, age)
    return p


def _exclusion(p: Mapping[str, Any], value: Decimal | None, age: Decimal | None) -> str | None:
    reasons = [
        p[key] for key in ("reference_comparability", "calculation_status") if p[key] in EXCLUDED
    ]
    if age is not None and age > 18:
        reasons.append("data over 18 months old")
    if value is None:
        reasons.append("missing value")
    return "; ".join(reasons) or None


def _quantile(ordered: list[Decimal], fraction: Decimal) -> Decimal:
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def _statistics(peers: list[dict[str, Any]]) -> dict[str, Any]:
    values = sorted(Decimal(p["value"]) for p in peers)
    n = len(values)
    result: dict[str, Any] = {"n": n, "reasons": {}}
    for key, floor in FLOORS.items():
        if n < floor:
            result[key] = None
            result["reasons"][key] = f"N={n}; minimum {floor}"
        else:
            result[key] = str(_statistic(key, values))
    return result


def _statistic(key: str, values: list[Decimal]) -> Decimal:
    if key == "minimum":
        return values[0]
    if key == "maximum":
        return values[-1]
    if key == "range":
        return values[-1] - values[0]
    if key == "average":
        return sum(values, Decimal(0)) / len(values)
    return _quantile(
        values, {"q1": Decimal(".25"), "median": Decimal(".5"), "q3": Decimal(".75")}[key]
    )


def _position(top: Mapping[str, Any], stats: Mapping[str, Any]) -> dict[str, Any]:
    borrower, median = top["borrower_value"], stats["median"]
    delta = None if borrower is None or median is None else Decimal(borrower) - Decimal(median)
    return {
        "metric_id": top["metric_id"],
        "unit_label": top["unit_label"],
        "borrower_value": borrower,
        **{
            f"peer_{out}": stats[key]
            for out, key in (
                ("min", "minimum"),
                ("q1", "q1"),
                ("median", "median"),
                ("q3", "q3"),
                ("max", "maximum"),
            )
        },
        "n": stats["n"],
        "delta_to_median": None if delta is None else str(delta),
        "position": None
        if delta is None
        else "Above"
        if delta > 0
        else "Below"
        if delta < 0
        else "In line",
        "reason": "borrower value or permitted median missing" if delta is None else None,
    }


def _ev(
    top: Mapping[str, Any], stats: Mapping[str, Any], basis: str | None
) -> dict[str, Any] | None:
    if "borrower_metric" not in top:
        return None
    metric = _number(top["borrower_metric"], "borrower_metric")
    reason = "positive borrower_metric and declared multiple basis required"
    valid = metric is not None and metric > 0 and basis is not None
    return {
        "borrower_metric": None if metric is None else str(metric),
        "multiple_basis": basis,
        **{
            out: str(Decimal(stats[key]) * metric)
            if valid and metric is not None and stats[key] is not None
            else None
            for out, key in (("low", "minimum"), ("median", "median"), ("high", "maximum"))
        },
        "reason": None if valid else reason,
        "statistic_reasons": stats["reasons"],
        "limitation": "indicative context only; not valuation or recovery evidence; "
        "source, period, denominator and EV perimeter require analyst verification",
    }


def _alignment(top: Mapping[str, Any], peers: list[dict[str, Any]]) -> None:
    for key in ("unit_label", "currency", "period", "definition_note"):
        values = {p[key] for p in peers if key in p}
        if key in top:
            values.add(top[key])
        if len(values) > 1:
            raise CalcError(f"peers.{key}: incompatible values; reconcile before aggregation")


def _group(
    top: Mapping[str, Any], peers: list[dict[str, Any]], basis: str | None
) -> dict[str, Any]:
    included = [p for p in peers if p["exclusion_reason"] is None]
    _alignment(top, included)
    inc = _statistics(included)
    exc = _statistics([p for p in included if not p["outlier"]])
    exc["newly_suppressed_by_exclusion"] = sorted(exc["reasons"].keys() - inc["reasons"].keys())
    cautions = [
        "Comparability, definitions, period alignment and citations are analyst assertions; "
        "this calculation does not verify source evidence."
    ]
    for p in included:
        cautions.extend(_cautions(p))
    if "period" not in top or "definition_note" not in top or "currency" not in top:
        cautions.append("Borrower period/currency/definition alignment metadata incomplete.")
    return {
        "multiple_basis": basis,
        "cautions": cautions,
        "statistics_including_outliers": inc,
        "statistics_excluding_outliers": exc,
        "positioning": _position(top, inc),
        "positioning_excluding_outliers": _position(top, exc),
        "implied_ev": _ev(top, inc, basis),
        "implied_ev_excluding_outliers": _ev(top, exc, basis),
    }


def _cautions(p: Mapping[str, Any]) -> list[str]:
    notes = []
    if p["reference_comparability"] == "Comparable with Limitations":
        notes.append(
            f"{p['peer']}: Partial / Comparable with Limitations; "
            f"{p.get('limitation_note', 'limitation not supplied')}"
        )
    if p["age_months"] is None:
        notes.append(f"{p['peer']}: age not supplied; staleness unverified")
    elif Decimal(p["age_months"]) > 12:
        notes.append(f"{p['peer']}: stale over 12 months ({p['age_months']})")
    if p["outlier"]:
        notes.append(
            f"{p['peer']}: outlier; both versions shown, average may be distorted; "
            f"{p.get('outlier_reason', 'reason not supplied')}"
        )
    for key in ("cite", "definition_note"):
        if key not in p:
            notes.append(f"{p['peer']}: {key} not supplied")
    return notes


def _input(data: object) -> dict[str, Any]:
    top = dict(_object(data, TOP_FIELDS, TOP_REQUIRED, "input"))
    for key in ("metric_id", "unit_label", "period", "definition_note", "cite"):
        if key in top:
            top[key] = _text(top[key], f"input.{key}")
    if top.get("currency") is not None:
        top["currency"] = _text(top["currency"], "input.currency")
    if "multiple_basis" in top:
        top["multiple_basis"] = _basis(top["multiple_basis"], "input.multiple_basis")
    borrower = _number(top["borrower_value"], "input.borrower_value")
    top["borrower_value"] = None if borrower is None else str(borrower)
    if "borrower_metric" in top:
        metric = _number(top["borrower_metric"], "input.borrower_metric")
        top["borrower_metric"] = None if metric is None else str(metric)
    if not isinstance(top["peers"], list):
        raise CalcError("input.peers: needs a list")
    return top


def compute(data: object) -> dict[str, Any]:
    """Validate before arithmetic; output contains only JSON-safe objects."""
    top = _input(data)
    peers = sorted((_peer(p, i, top) for i, p in enumerate(top["peers"])), key=lambda p: p["peer"])
    if len({p["peer"] for p in peers}) != len(peers):
        raise CalcError("peers.peer: duplicate identity")
    by_basis: dict[str | None, list[dict[str, Any]]] = {}
    for p in peers:
        by_basis.setdefault(p["multiple_basis"], []).append(p)
    if not peers:
        by_basis[top.get("multiple_basis")] = []
    bases = set(by_basis)
    if (bases != {None} or "borrower_metric" in top) and top["unit_label"] != "x":
        raise CalcError("input.unit_label: multiple basis / implied EV requires x")
    if "borrower_metric" in top and None in bases:
        raise CalcError("input.multiple_basis: required for implied EV")
    try:
        with localcontext(CONTEXT) as context:
            context.traps[Underflow] = True
            groups = [_group(top, by_basis[b], b) for b in sorted(bases, key=lambda b: b or "")]
    except DecimalException as exc:
        raise CalcError(
            f"input: decimal arithmetic exceeds Decimal38 context ({type(exc).__name__})"
        ) from exc
    return {
        "schema": "rbot-calc-peer-statistics/1",
        "metric_id": top["metric_id"],
        "unit_label": top["unit_label"],
        "borrower_value": top["borrower_value"],
        "input_basis": {k: v for k, v in top.items() if k != "peers"},
        "convention": "inclusive R type 7; Decimal38 half-even; no display quantization",
        "threshold_set": "ACTIVE_PROMPT: min/max/range 2, median 3, quartiles 4, average 5",
        "n_supplied": len(peers),
        "peers": peers,
        "groups": groups,
    }


def _cell(value: object) -> str:
    return (
        "—"
        if value is None
        else str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    )


def markdown(result: Mapping[str, Any]) -> str:
    """Positioning columns and sensitivity/cautions; interpretation stays Module-owned."""
    lines = [result["convention"], result["threshold_set"]]
    for group in result["groups"]:
        for suffix in ("", "_excluding_outliers"):
            lines += [
                "<!-- cp1c.positioning (calculator columns; "
                f"{_cell(group['multiple_basis'])}{suffix}) -->",
                "| " + " | ".join(COLUMNS) + " |",
                "|" + "---|" * len(COLUMNS),
                "| " + " | ".join(_cell(group["positioning" + suffix][c]) for c in COLUMNS) + " |",
            ]
            stats = group[
                "statistics_excluding_outliers" if suffix else "statistics_including_outliers"
            ]
            lines.append("Suppressed: " + _cell(stats["reasons"]))
            ev = group["implied_ev" + suffix]
            if ev is not None:
                lines += [
                    "Implied EV ("
                    + _cell(group["multiple_basis"])
                    + suffix
                    + "): "
                    + "; ".join(f"{key}={_cell(ev[key])}" for key in ("low", "median", "high")),
                    _cell(ev["reason"]),
                    ev["limitation"],
                ]
        lines.extend(_cell(note) for note in group["cautions"])
    lines.extend(
        f"Excluded {_cell(p['peer'])}: {_cell(p['exclusion_reason'])}"
        for p in result["peers"]
        if p["exclusion_reason"]
    )
    return "\n".join(lines) + "\n"
