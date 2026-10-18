"""Pure CP2D arithmetic on analyst-supplied evidence; no documentary verification.

Strict input keys: currency/unit/perimeter/as_of_date/horizon_end, period_months=12,
burn_basis (source period, recurring/seasonal/distorted caveat), ocf_includes (empty list),
liquidity_sources (1..1000 rows), components (seven named rows below).
Each row requires id, amount (finite decimal string/int/Decimal or null), cite, basis,
currency/unit/perimeter/as_of_date/horizon_end matching the top-level context.
Sources also require component (Cash/Revolver/Other committed/Committed inflow),
availability (Opening/Restricted/Future), accessible (Yes/No). Opening rows exclude No;
Restricted must be No; Future must be Yes and Committed inflow. Committed inflow cannot
be Opening. At least one Opening and one Future row are required (explicit zero/null).
Components require component (one each of COMPONENTS), timing (text), mandatory (Yes/No).
The five USES are positive magnitudes; OCF/WC are signed. Interest/tax/mandatory capex/
maturities must be mandatory Yes. OCF must precede WC/interest/tax: any ocf_includes
entry refuses this bridge rather than deducting included costs again. IDs are globally
unique, including source/component rows; citations and metadata remain assertions.

Opening accessible=sum Opening/Yes; committed inflows=sum Future. Net=OCF+WC-five
uses+inflows. Closing=opening+net. Mandatory uses=sum mandatory USES; headroom=opening
minus mandatory uses (excludes future funding and operating movements). Any null poisons
only dependent results, with named reasons. Bridge order is canonical, not time-resolved.
No dated schedule is accepted: pinch point stays qualitative even when closing is positive.

Money arithmetic is exact in an isolated 4304-digit context: <=100 coefficient digits,
exponent magnitude <=1000, <=1000 sources. Burn=-net/12 and months=opening*12/-net
are evaluated independently from exact money; only their final display is rounded to38
significant digits, half-even, scientific notation allowed, no fixed-decimal underflow.
Nonpositive burn gives null months and a visible explanation; actual opening0 with burn>0
has months0. All figures serialize as strings/null. No I/O, input mutation or ambient context.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from decimal import (
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    DecimalException,
    Inexact,
    InvalidOperation,
    Overflow,
    Underflow,
    localcontext,
)
from typing import Any

from rbotlib.calc.bond_analytics import CalcError

EXACT = Context(
    prec=4304, Emin=-10000, Emax=10000, traps=[Inexact, InvalidOperation, Overflow, Underflow]
)
DISPLAY = Context(
    prec=38,
    Emin=-10000,
    Emax=10000,
    rounding=ROUND_HALF_EVEN,
    traps=[InvalidOperation, Overflow, Underflow],
)
ALIGN = {"currency", "unit", "perimeter", "as_of_date", "horizon_end"}
ROW = ALIGN | {"id", "amount", "cite", "basis"}
COMPONENTS = (
    "operating_cash_flow",
    "working_capital_movement",
    "cash_interest",
    "cash_taxes",
    "mandatory_capex",
    "debt_amortisation_and_maturities",
    "other_cash_uses",
)
USES = COMPONENTS[2:]
FIGURE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
LIMITATION = (
    "Supplied metadata/citations are model-authored assertions, not independent source "
    "proof or verified financing availability. Average burn assumes uniform timing; "
    "seasonality, constraints and one-offs may invalidate that assumption. "
    "No dated complete schedule: earliest shortfall cannot be calculated."
)


def _object(raw: object, keys: set[str], where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CalcError(f"{where}: needs an object")
    if raw.keys() != keys:
        raise CalcError(
            f"{where}: unknown {sorted(map(str, raw.keys() - keys))}; "
            f"missing {sorted(keys - raw.keys())}"
        )
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
            raise CalcError(f"{where}: malformed/nonfinite figure")
        value = Decimal(text)
        if len(value.as_tuple().digits) > 100 or abs(int(value.as_tuple().exponent)) > 1000:
            raise CalcError(f"{where}: exceeds100 digits / exponent magnitude1000")
    except (DecimalException, ValueError) as exc:
        raise CalcError(f"{where}: malformed/out-of-bounds figure") from exc
    return str(value)


def _choice(item: Mapping[str, Any], key: str, values: set[str]) -> None:
    if item[key] not in values:
        raise CalcError(f"{item.get('id', 'input')}.{key}: expected {sorted(values)}")


def _context(top: dict[str, Any]) -> None:
    for key in ALIGN | {"burn_basis"}:
        top[key] = _text(top[key], key)
    try:
        start, end = date.fromisoformat(top["as_of_date"]), date.fromisoformat(top["horizon_end"])
        day = 28 if start.month == 2 and start.day == 29 else start.day
        expected = start.replace(year=start.year + 1, day=day)
    except ValueError as exc:
        raise CalcError("as_of_date/horizon_end: invalid calendar dates") from exc
    if start.isoformat() != top["as_of_date"] or end.isoformat() != top["horizon_end"]:
        raise CalcError("as_of_date/horizon_end: needs ISO YYYY-MM-DD")
    if _number(top["period_months"], "period_months") is None or top["period_months"] is None:
        raise CalcError("period_months: explicit12 required")
    if Decimal(str(top["period_months"])) != 12 or end != expected:
        raise CalcError("period_months/horizon_end: requires12 calendar months")
    if not isinstance(top["ocf_includes"], list) or top["ocf_includes"]:
        raise CalcError(
            "ocf_includes: must be empty; WC/interest/tax already included risks double count"
        )


def _rows(top: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    raw = top[kind]
    if not isinstance(raw, list) or not 1 <= len(raw) <= 1000:
        raise CalcError(f"{kind}: requires1..1000 rows")
    extra = (
        {"component", "availability", "accessible"}
        if kind == "liquidity_sources"
        else {"component", "timing", "mandatory"}
    )
    rows = []
    for index, value in enumerate(raw):
        item = _object(value, ROW | extra, f"{kind}[{index}]")
        for key in (ROW | extra) - {"amount"}:
            item[key] = _text(item[key], f"{kind}[{index}].{key}")
        if any(item[key] != top[key] for key in ALIGN):
            raise CalcError(f"{item['id']}: incompatible currency/unit/perimeter/as-of/horizon")
        item["amount"] = _number(item["amount"], f"{item['id']}.amount")
        rows.append(item)
    return rows


def _sources(rows: list[dict[str, Any]]) -> None:
    for item in rows:
        _choice(item, "availability", {"Opening", "Restricted", "Future"})
        _choice(item, "accessible", {"Yes", "No"})
        _choice(item, "component", {"Cash", "Revolver", "Other committed", "Committed inflow"})
        future = item["availability"] == "Future"
        if future != (item["component"] == "Committed inflow"):
            raise CalcError(f"{item['id']}: committed inflow must be Future, never Opening")
        if (future and item["accessible"] != "Yes") or (
            item["availability"] == "Restricted" and item["accessible"] != "No"
        ):
            raise CalcError(f"{item['id']}: incompatible availability/accessibility")
        if item["amount"] is not None and Decimal(item["amount"]) < 0:
            raise CalcError(f"{item['id']}.amount: source must be nonnegative")
    if not {"Opening", "Future"} <= {item["availability"] for item in rows}:
        raise CalcError("liquidity_sources: explicit Opening and Future rows required (zero/null)")


def _components(rows: list[dict[str, Any]]) -> None:
    if len(rows) != len(COMPONENTS) or {r["component"] for r in rows} != set(COMPONENTS):
        raise CalcError("components: exactly one of each required component")
    for item in rows:
        _choice(item, "mandatory", {"Yes", "No"})
        if item["component"] in USES:
            if item["amount"] is not None and Decimal(item["amount"]) < 0:
                raise CalcError(f"{item['id']}.amount: use must be nonnegative")
            if item["component"] != "other_cash_uses" and item["mandatory"] != "Yes":
                raise CalcError(f"{item['id']}.mandatory: required use must be Yes")


def _sum(rows: list[dict[str, Any]], signed: bool = False) -> tuple[Decimal | None, str | None]:
    missing = [r["id"] for r in rows if r["amount"] is None]
    if missing:
        return None, "missing " + ", ".join(sorted(missing))
    value = sum(
        (Decimal(r["amount"]) * (-1 if signed and r["component"] in USES else 1) for r in rows),
        Decimal(0),
    )
    return value, None


def _metric(value: Decimal | None, reason: str | None) -> dict[str, Any]:
    return {"value": str(value) if value is not None else None, "reason": reason}


def _reasons(*reasons: str | None) -> str | None:
    return "; ".join(reason for reason in reasons if reason) or None


def _runway(
    opening: Decimal | None, net: Decimal | None, reason: str | None
) -> tuple[Decimal | None, Decimal | None, str | None]:
    # Form both numerators in EXACT; display division is the only rounding boundary.
    burn_numerator = None if net is None else -net
    months_numerator = None if opening is None else opening * 12
    months, burn = None, None
    with localcontext(DISPLAY):
        if burn_numerator is not None:
            burn = burn_numerator / 12
            if burn_numerator <= 0:
                reason = _reasons(
                    reason, "no runway to exhaust: cash-generative or flat period (burn <=0)"
                )
            elif months_numerator is not None:
                months = months_numerator / burn_numerator
    return months, burn, reason


def _bridge(
    rows: list[dict[str, Any]],
    common: dict[str, Any],
    opening: dict[str, Any],
    closing: dict[str, Any],
) -> list[dict[str, Any]]:
    bridge = [
        {
            **common,
            "step": "Accessible liquidity",
            "kind": "Opening total",
            "amount": opening["value"],
            "reason": opening["reason"],
        }
    ]
    for item in rows:
        amount = None if item["amount"] is None else Decimal(item["amount"])
        if amount is not None and item["component"] in USES:
            amount = -amount
        bridge.append(
            {
                **common,
                "step": item["id"],
                "kind": "Use" if item["component"] in USES else "Delta",
                "amount": None if amount is None else str(amount),
                "reason": "missing " + item["id"] if amount is None else None,
                "basis": item["basis"],
                "cite": item["cite"],
            }
        )
    bridge.append(
        {
            **common,
            "step": "Ending accessible liquidity",
            "kind": "Closing total",
            "amount": closing["value"],
            "reason": closing["reason"],
        }
    )
    return bridge


def _runway_table(common: dict[str, Any], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        "opening": "Accessible liquidity",
        "mandatory": "Mandatory uses 12m",
        "headroom": "Headroom",
        "months_to_empty": "Months of runway",
    }
    runway = [
        {
            "item": label,
            **metrics[key],
            "unit_label": "months"
            if key == "months_to_empty"
            else common["currency"] + " " + common["unit"],
            "basis": common["basis"],
            "cite": common["cite"],
        }
        for key, label in labels.items()
    ]
    closing = metrics["ending_accessible_liquidity"]["value"]
    pinch = (
        "Closing deficit: funding pressure within horizon; exact pinch date unavailable."
        if closing is not None and Decimal(closing) < 0
        else "Timing unknown: intra-period shortfall cannot be ruled out from annual totals."
    )
    runway.append(
        {
            "item": "Pinch point",
            "value": pinch,
            "unit_label": "text",
            "basis": common["basis"],
            "cite": common["cite"],
            "reason": LIMITATION,
        }
    )
    return runway


def _calculate(
    top: dict[str, Any], sources: list[dict[str, Any]], components: list[dict[str, Any]]
) -> dict[str, Any]:
    opening_rows = [
        r for r in sources if r["availability"] == "Opening" and r["accessible"] == "Yes"
    ]
    future = [r for r in sources if r["availability"] == "Future"]
    opening, opening_reason = _sum(opening_rows)
    net, net_reason = _sum(components + future, signed=True)
    mandatory, mandatory_reason = _sum(
        [r for r in components if r["component"] in USES and r["mandatory"] == "Yes"]
    )
    closing = None if opening is None or net is None else opening + net
    headroom = None if opening is None or mandatory is None else opening - mandatory
    closing_reason = _reasons(opening_reason, net_reason)
    months, burn, reason = _runway(opening, net, closing_reason)
    metrics = {
        "opening": _metric(opening, opening_reason),
        "mandatory": _metric(mandatory, mandatory_reason),
        "headroom": _metric(headroom, _reasons(opening_reason, mandatory_reason)),
        "net_movement": _metric(net, net_reason),
        "ending_accessible_liquidity": _metric(closing, closing_reason),
        "average_monthly_burn": _metric(burn, net_reason),
        "months_to_empty": _metric(months, reason),
    }
    common = {k: top[k] for k in ("currency", "unit")}
    common.update(
        cite="; ".join(sorted({r["cite"] for r in sources + components})),
        basis="12-month signed bridge; " + top["burn_basis"],
    )
    return {
        "schema": "rbot-calc-liquidity-bridge/1",
        "inputs": top,
        "liquidity_sources": sources,
        "components": components,
        **metrics,
        "bridge": _bridge(
            components + future, common, metrics["opening"], metrics["ending_accessible_liquidity"]
        ),
        "runway": _runway_table(common, metrics),
        "limitation": LIMITATION,
    }


def compute(data: object) -> dict[str, Any]:
    """Validate the complete typed basis, then compute without I/O or mutation."""
    top = _object(
        data,
        ALIGN | {"period_months", "burn_basis", "ocf_includes", "liquidity_sources", "components"},
        "input",
    )
    _context(top)
    sources, components = _rows(top, "liquidity_sources"), _rows(top, "components")
    ids = [r["id"] for r in sources + components]
    if len(ids) != len(set(ids)):
        raise CalcError("id: duplicate source/component identity")
    _sources(sources)
    _components(components)
    components.sort(key=lambda item: COMPONENTS.index(item["component"]))
    sources.sort(key=lambda item: item["id"])
    top = {k: v for k, v in top.items() if k not in {"liquidity_sources", "components"}}
    top["period_months"] = "12"
    with localcontext(EXACT):
        return _calculate(top, sources, components)


def _cell(raw: object) -> str:
    return (
        "—" if raw is None else str(raw).replace("|", r"\|").replace("\n", " ").replace("\r", " ")
    )


def markdown(result: Mapping[str, Any]) -> str:
    """Owning §2.9 bridge/runway columns plus dependent reasons and source limitations."""
    lines = []
    for name, columns in (
        ("bridge", ("step", "kind", "amount", "currency", "unit", "basis", "cite")),
        ("runway", ("item", "value", "unit_label", "basis", "cite")),
    ):
        lines.extend(
            [
                f"<!-- cp2d.{name} -->",
                "| " + " | ".join(columns) + " |",
                "|" + "---|" * len(columns),
            ]
        )
        for row in result[name]:
            lines.append("| " + " | ".join(_cell(row[k]) for k in columns) + " |")
            if row["reason"]:
                lines.append("Limitation: " + _cell(row["reason"]))
    lines.append(result["limitation"])
    return "\n".join(lines) + "\n"
