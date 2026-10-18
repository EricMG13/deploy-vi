"""Pure CP-2E arithmetic; figures are Decimal/string/int or null, never floats.

Input keys: basis, rate_exposure_id, gross_floating_rate_debt,
hedged_floating_rate_debt, total_debt, hedge_qualification, fx_exposures,
cost_exposures, channels_nonoverlapping. Basis requires currency, unit, perimeter,
period_start, period_end, cite; optional limitation. All amounts use this basis;
rows/qualification require the same basis (their cites/limitations may differ).
FX rows: exposure_id, net_exposure, adverse_move_pct, basis. Cost rows substitute
annual_spend. Arrays may be null/missing (unassessed), or [] (assessed none).
Positive hedged debt requires hedge_qualification: qualified (bool), hedge_ids,
covered_instruments (includes rate_exposure_id), instrument_type, notional,
rate_or_strike, linear_protection (bool), coverage_start, coverage_end, maturity_date,
basis. Missing
qualification/terms/coverage, false qualification or unsupported nonlinear protection cannot
establish effective protection. Notional never determines the hedged amount.

Exact money arithmetic, unrounded JSON strings; a recurring debt fraction uses
Decimal precision 38, half even. Shocks are signed decimal fractions, abs <= 1.
Positive impact means adverse annual cash cost; negative means cash benefit.
Combined requires every channel known and channels_nonoverlapping explicitly true.
Metadata/qualification are retained model-authored claims, not verified sources.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, DecimalException, Underflow, localcontext
from typing import Any

from .bond_analytics import CONTEXT, CalcError, day, figure

SCHEMA = "rbot-calc-rate-fx-sensitivity/1"
BASIS = {"currency", "unit", "perimeter", "period_start", "period_end", "cite", "limitation"}
DEBT = ("gross_floating_rate_debt", "hedged_floating_rate_debt", "total_debt")
TOP = {
    *DEBT,
    "basis",
    "rate_exposure_id",
    "hedge_qualification",
    "fx_exposures",
    "cost_exposures",
    "channels_nonoverlapping",
}
QUALIFICATION = {
    "qualified",
    "hedge_ids",
    "covered_instruments",
    "instrument_type",
    "notional",
    "rate_or_strike",
    "linear_protection",
    "coverage_start",
    "coverage_end",
    "maturity_date",
    "basis",
}
COLUMNS = ("sensitivity", "shock", "formula", "cash_impact", "currency", "unit", "status", "cite")


def _object(raw: object, allowed: set[str], where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CalcError(f"{where}: needs an object")
    for key in raw:
        if key not in allowed:
            raise CalcError(f"{where}.{key}: unknown field")
    return raw


def _text(raw: object, where: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise CalcError(f"{where}: needs non-empty text")
    return raw


def _basis(raw: object, where: str, common: Mapping[str, Any] | None = None) -> dict[str, Any]:
    obj = _object(raw, BASIS, where)
    result = {k: _text(obj.get(k), f"{where}.{k}") for k in sorted(BASIS - {"limitation"})}
    start, end = (day(result[k], f"{where}.{k}") for k in ("period_start", "period_end"))
    if start > end:
        raise CalcError(f"{where}.period_end: before period_start")
    if "limitation" in obj:
        result["limitation"] = _text(obj["limitation"], f"{where}.limitation")
    if common is not None:
        for key in BASIS - {"cite", "limitation"}:
            if result[key] != common[key]:
                raise CalcError(f"{where}.{key}: differs from common basis")
    return result


def _number(raw: object, where: str, *, nonnegative: bool = False) -> Decimal | None:
    value = None if raw is None else figure(raw, where)
    if value is not None and nonnegative and value < 0:
        raise CalcError(f"{where}: must be nonnegative")
    return value


def _identities(raw: object, where: str) -> list[str]:
    if not isinstance(raw, list) or not raw:
        raise CalcError(f"{where}: needs a non-empty identity list")
    result = [_text(v, where) for v in raw]
    if len(result) != len(set(result)):
        raise CalcError(f"{where}: duplicate identity")
    return result


def _qualification(data: Mapping[str, Any], basis: Mapping[str, Any]) -> tuple[object, str]:
    raw = data.get("hedge_qualification")
    if raw is None:
        return None, "hedge_qualification missing"
    q = _object(raw, QUALIFICATION, "hedge_qualification")
    if not isinstance(q.get("qualified"), bool):
        raise CalcError("hedge_qualification.qualified: needs explicit bool")
    _basis(q.get("basis"), "hedge_qualification.basis", basis)
    _identities(q.get("hedge_ids"), "hedge_qualification.hedge_ids")
    covered = _identities(q.get("covered_instruments"), "hedge_qualification.covered_instruments")
    _text(q.get("instrument_type"), "hedge_qualification.instrument_type")
    if q.get("linear_protection") is not None and not isinstance(q["linear_protection"], bool):
        raise CalcError("hedge_qualification.linear_protection: needs bool or null")
    notional = _number(q.get("notional"), "hedge_qualification.notional", nonnegative=True)
    hedged = _number(data.get(DEBT[1]), DEBT[1], nonnegative=True)
    if notional is not None and hedged is not None and hedged > notional:
        raise CalcError("hedged_floating_rate_debt: exceeds hedge notional")
    if q.get("rate_or_strike") is not None:
        _text(q["rate_or_strike"], "hedge_qualification.rate_or_strike")
    reason = _coverage_reason(q, data, basis, covered, notional)
    return dict(q), reason


def _coverage_reason(
    q: Mapping[str, Any],
    data: Mapping[str, Any],
    basis: Mapping[str, Any],
    covered: list[str],
    notional: Decimal | None,
) -> str:
    dates = {
        k: None if q.get(k) is None else day(q[k], f"hedge_qualification.{k}")
        for k in ("coverage_start", "coverage_end", "maturity_date")
    }
    if not q["qualified"]:
        return "hedge protection not analyst-qualified"
    if q.get("linear_protection") is not True:
        return "unsupported/unknown nonlinear protection; no effectiveness inferred"
    if data["rate_exposure_id"] not in covered:
        return "hedge does not identify rate exposure"
    if (
        notional is None
        or q.get("rate_or_strike") is None
        or any(v is None for v in dates.values())
    ):
        return "hedge notional/terms/coverage missing"
    start, end = day(basis["period_start"], "basis"), day(basis["period_end"], "basis")
    known = {k: v for k, v in dates.items() if v is not None}
    if known["coverage_start"] > start or min(known["coverage_end"], known["maturity_date"]) < end:
        return "hedge expired or coverage does not span sensitivity period"
    return ""


def _arithmetic(
    left: Decimal | None, right: Decimal | None, operation: str, where: str
) -> Decimal | None:
    if left is None or right is None:
        return None
    # Enough precision for exact addition/subtraction/multiplication, even for unlike scales.
    precision = sum(
        len(v.as_tuple().digits) + abs(int(v.as_tuple().exponent)) for v in (left, right)
    )
    try:
        with localcontext(CONTEXT) as context:
            context.prec = 38 if operation == "divide" else max(38, precision + 2)
            context.traps[Underflow] = True
            if operation == "divide":
                return left / right
            if operation == "multiply":
                return left * right
            return left + right if operation == "add" else left - right
    except (DecimalException, ValueError) as exc:
        raise CalcError(
            f"{where}: {operation} exceeds Decimal arithmetic range ({type(exc).__name__})"
        ) from None


def _row(
    labels: tuple[str, str, str], value: Decimal | None, reason: str, basis: Mapping[str, Any]
) -> dict[str, Any]:
    name, shock, formula = labels
    return {
        "sensitivity": name,
        "shock": shock,
        "formula": formula,
        "cash_impact": None if value is None else str(value),
        "currency": basis["currency"],
        "unit": basis["unit"],
        "cite": basis["cite"],
        "status": "Not computable" if value is None else "Calculated",
        "reason": reason,
        "effect": "Unknown" if value is None else "Cash benefit" if value < 0 else "Cash cost",
    }


def _channels(
    data: Mapping[str, Any], channel: str, basis: Mapping[str, Any], seen: set[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    raw = data.get(channel)
    if raw is None:
        return [], [], [f"{channel}: unassessed (missing array)"]
    if not isinstance(raw, list):
        raise CalcError(f"{channel}: needs an array or null")
    amount_key = "net_exposure" if channel == "fx_exposures" else "annual_spend"
    rows, inputs = [], []
    for index, item in enumerate(raw):
        where = f"{channel}[{index}]"
        obj = _object(item, {"exposure_id", amount_key, "adverse_move_pct", "basis"}, where)
        identity = _text(obj.get("exposure_id"), f"{where}.exposure_id")
        if identity in seen:
            raise CalcError(f"{where}.exposure_id: duplicate/overlapping exposure identity")
        seen.add(identity)
        row_basis = _basis(obj.get("basis"), f"{where}.basis", basis)
        row, normalized = _channel_row(obj, amount_key, where, row_basis)
        rows.append(row)
        inputs.append(normalized)
    return rows, inputs, []


def _channel_row(
    obj: Mapping[str, Any], amount_key: str, where: str, basis: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    amount = _number(
        obj.get(amount_key), f"{where}.{amount_key}", nonnegative=amount_key == "annual_spend"
    )
    move = _number(obj.get("adverse_move_pct"), f"{where}.adverse_move_pct")
    if move is not None and move.copy_abs() > 1:
        raise CalcError(f"{where}.adverse_move_pct: decimal fraction required (0.10 = 10%)")
    reason = ", ".join(
        k for k, v in ((amount_key, amount), ("adverse_move_pct", move)) if v is None
    )
    impact = _arithmetic(amount, move, "multiply", f"{where}.cash_impact")
    row = _row(
        (
            obj["exposure_id"],
            "—" if move is None else str(move),
            f"{amount_key} x adverse_move_pct",
        ),
        impact,
        reason,
        basis,
    )
    normalized = dict(obj) | {
        amount_key: None if amount is None else str(amount),
        "adverse_move_pct": None if move is None else str(move),
    }
    return row, normalized


def _debt_values(obj: Mapping[str, Any]) -> list[Decimal | None]:
    numbers = [_number(obj.get(k), k, nonnegative=True) for k in DEBT]
    gross, hedged, total = numbers
    if gross is not None and hedged is not None and hedged > gross:
        raise CalcError("hedged_floating_rate_debt: exceeds gross_floating_rate_debt")
    if gross is not None and total is not None and gross > total:
        raise CalcError("gross_floating_rate_debt: exceeds total_debt")
    return numbers


def _rate(
    numbers: list[Decimal | None], coverage_reason: str
) -> tuple[dict[str, Any], Decimal | None]:
    gross, hedged, total = numbers
    reason = ", ".join(k for k, v in zip(DEBT[:2], numbers[:2], strict=True) if v is None)
    if hedged is not None and hedged > 0 and coverage_reason:
        reason = "; ".join(filter(None, (reason, coverage_reason)))
    unhedged = _arithmetic(
        None if reason else gross, hedged, "subtract", "unhedged_floating_rate_debt"
    )
    fraction = _arithmetic(unhedged, total or None, "divide", "unhedged_debt_percentage")
    rate = _arithmetic(unhedged, Decimal("0.01"), "multiply", "rate.cash_impact")
    metrics = {
        "unhedged_floating_rate_debt": None if unhedged is None else str(unhedged),
        "unhedged_debt_percentage": None if fraction is None else str(fraction),
        "fraction_reason": reason or ("total_debt missing or zero" if fraction is None else ""),
        "rate_reason": reason,
    }
    return metrics, rate


def _combined(
    rows: list[dict[str, Any]], reasons: list[str], nonoverlap: object, basis: Mapping[str, Any]
) -> dict[str, Any]:
    if nonoverlap is not None and not isinstance(nonoverlap, bool):
        raise CalcError("channels_nonoverlapping: needs bool or null")
    reasons += [r["reason"] for r in rows if r["cash_impact"] is None]
    if nonoverlap is not True:
        reasons.append("channels_nonoverlapping: not explicitly qualified")
    combined = None if reasons else Decimal(0)
    if combined is not None:
        for row in rows:
            combined = _arithmetic(
                combined, Decimal(row["cash_impact"]), "add", "Combined.cash_impact"
            )
    return _row(
        ("Combined", "declared shocks", "sum of non-overlapping channels"),
        combined,
        "; ".join(reasons),
        basis,
    )


def compute(data: object) -> dict[str, Any]:
    """JSON-safe deterministic results; CalcError identifies malformed inputs."""
    obj = _object(data, TOP, "input")
    basis = _basis(obj.get("basis"), "basis")
    identity = _text(obj.get("rate_exposure_id"), "rate_exposure_id")
    numbers = _debt_values(obj)
    qualification, coverage_reason = _qualification(obj, basis)
    metrics, rate = _rate(numbers, coverage_reason)
    rows = [
        _row(
            (identity, "+100 bps", "(gross - qualified hedged) x 0.01"),
            rate,
            metrics.pop("rate_reason"),
            basis,
        )
    ]
    seen = {identity}
    fx, fx_inputs, missing_fx = _channels(obj, "fx_exposures", basis, seen)
    costs, cost_inputs, missing_cost = _channels(obj, "cost_exposures", basis, seen)
    rows += fx + costs
    rows.append(
        _combined(rows, missing_fx + missing_cost, obj.get("channels_nonoverlapping"), basis)
    )
    inputs = dict(obj) | dict(
        zip(DEBT, (None if v is None else str(v) for v in numbers), strict=True)
    )
    inputs |= {
        "hedge_qualification": qualification,
        "fx_exposures": None if missing_fx else fx_inputs,
        "cost_exposures": None if missing_cost else cost_inputs,
    }
    if isinstance(qualification, dict) and qualification.get("notional") is not None:
        qualification["notional"] = str(figure(qualification["notional"], "notional"))
    return {
        **metrics,
        "schema": SCHEMA,
        "inputs": inputs,
        "basis": basis,
        "sensitivities": rows,
        "sign_convention": "positive = adverse annual cash cost; negative = cash benefit",
        "provenance": "model-authored input metadata; sources not host-verified",
    }


def markdown(result: Mapping[str, Any]) -> str:
    """Owning table columns, plus explicit reasons, signed effects and source limitations."""
    lines = [
        "<!-- cp2e.sensitivities (calculator columns) -->",
        result["sign_convention"],
        "| " + " | ".join(COLUMNS) + " |",
        "|" + "---|" * len(COLUMNS),
    ]
    for row in result["sensitivities"]:
        cells = ["—" if row[k] is None else str(row[k]) for k in COLUMNS]
        lines.append(
            "| " + " | ".join(v.replace("|", "\\|").replace("\n", " ") for v in cells) + " |"
        )
    for row in result["sensitivities"]:
        lines.append(f"\n{row['sensitivity']}: {row['effect']}. {row['reason']}\n")
    lines += [result["provenance"], "Metadata and coverage limitations: " + str(result["inputs"])]
    return "\n".join(lines) + "\n"
