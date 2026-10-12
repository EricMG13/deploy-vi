"""`rbot fit --run <RUN>`: the FIT host step (interfaces spec sections 3.4 and 7).

Reads `run-brief.md` (`snapshot.run_header`, `brief.portfolios`), each portfolio's
`prepared/portfolios/<id>.json`, `handoffs/CP-1.md` (`cp1.model_period_register` for the run's
currency and unit, `cp1.debt_facility_register`, `cp1.instrument_identity`),
`handoffs/CP-1A.md` when present (`snapshot.company_profile`: sector and country) and
`handoffs/CP-3.md`, which must validate against CP-3's contract (exit 0, or 3 when Blocked).
Writes `fit/<portfolio_id>.json` (the rows and every intermediate) and `handoffs/FIT.md` with
`snapshot.portfolio_fit` and `fit.limit_headroom`. Exit 1 names the missing or malformed
input; with no portfolio the Handoff is written with empty tables and `qa_status` Restricted.
The arithmetic is `rbotlib.fit_arithmetic`.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from rbotlib.contract import load_contract
from rbotlib.fit_arithmetic import (
    BREACHED,
    NOT_COMPUTED,
    Fit,
    Headroom,
    Instrument,
    Portfolio,
    Run,
    fit,
)
from rbotlib.handoff import Handoff, HandoffError, Table, parse
from rbotlib.rules import load_rules
from rbotlib.validate import EXIT_BLOCKED, EXIT_VALID, check

GAP = "\N{EM DASH}"
FIT_COLUMNS = (
    "portfolio_id strategy facility_id instrument current_exposure current_exposure_pct_nav_pct "
    "max_size currency unit binding_limit verdict recommendation_cap reason"
).split()
HEADROOM_COLUMNS = (
    "portfolio_id facility_id limit_id category parameter limit_kind limit_value limit_unit "
    "current_value headroom headroom_amount currency unit status source"
).split()


class FitError(ValueError):
    """An input FIT needs is missing or malformed; the message names it."""


def _records(table: Table | None) -> list[dict[str, str]]:
    if table is None:
        return []
    return [dict(zip(table.columns, row, strict=False)) for row in table.rows]


def _read(path: Path) -> Handoff:
    if not path.is_file():
        raise FitError(f"{path.name}: missing; FIT needs it")
    try:
        return parse(path.read_text(encoding="utf-8"))
    except HandoffError as exc:
        raise FitError(f"{path.name}: {exc}") from exc


def _cp3(run: Path, root: Path) -> None:
    """CP-3 must have run: its Handoff validates (exit 0, or 3 when Blocked)."""
    path = run / "handoffs" / "CP-3.md"
    if not path.is_file():
        raise FitError("handoffs/CP-3.md: missing; FIT runs after CP-3")
    rules = load_rules(root)
    contract = load_contract(root / "modules" / "CP-3" / "contract.json", rules)
    code, findings = check(path.read_text(encoding="utf-8"), contract, rules)
    if code not in (EXIT_VALID, EXIT_BLOCKED):
        listed = "; ".join(f"{f.code}: {f.message}" for f in findings)
        raise FitError(f"handoffs/CP-3.md does not validate (exit {code}): {listed}")


def figure(text: str | None) -> Decimal | None:
    if text is None or text.strip() in ("", GAP):
        return None
    try:
        return Decimal(text.strip())
    except InvalidOperation:
        return None


def _day(text: str | None) -> date | None:
    try:
        return date.fromisoformat((text or "").strip())
    except ValueError:
        return None


def _run(brief: Handoff, cp1: Handoff) -> Run:
    header = _records(brief.tables.get("snapshot.run_header"))
    periods = _records(cp1.tables.get("cp1.model_period_register"))
    if len(header) != 1 or not periods:
        raise FitError("run-brief.md needs one snapshot.run_header row and CP-1 a period")
    as_of = _day(header[0].get("as_of_date"))
    if as_of is None:
        raise FitError("run-brief.md: as_of_date is not an ISO date")
    return Run(header[0]["issuer_id"], as_of, periods[0]["currency"], periods[0]["unit"])


def instruments(cp1: Handoff, cp1a: Handoff | None) -> list[Instrument]:
    """Every `cp1.instrument_identity` row, with its terms from the latest facility row."""
    facilities: dict[str, dict[str, str]] = {}
    for row in _records(cp1.tables.get("cp1.debt_facility_register")):
        facilities[row["facility_id"]] = row  # the register's last row per facility
    profile = _records(cp1a.tables.get("snapshot.company_profile")) if cp1a else []
    sector = profile[0].get("sector") if profile else None
    country = profile[0].get("country") if profile else None
    found = []
    for row in _records(cp1.tables.get("cp1.instrument_identity")):
        terms = facilities.get(row["facility_id"], {})
        ratings = tuple(
            r for r in (row.get(f"rating_{a}", GAP) for a in ("moodys", "sp", "fitch")) if r != GAP
        )
        secured = {"SECURED": True, "UNSECURED": False}.get(terms.get("secured_status", ""))
        found.append(
            Instrument(
                row["facility_id"],
                row["instrument_name"],
                row.get("debt_type"),
                secured,
                terms.get("currency"),
                _day(terms.get("maturity_date")),
                ratings,
                sector,
                country,
            )
        )
    if not found:
        raise FitError("handoffs/CP-1.md: cp1.instrument_identity has no row")
    return found


def portfolio(run: Path, prepared_json: str) -> Portfolio:
    path = run / prepared_json
    if not path.is_file():
        raise FitError(f"{prepared_json}: missing; rbot prepare writes it")
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    nav, par = figure(data.get("nav")), figure(data.get("par"))
    if nav is None or nav <= 0 or par is None or par <= 0:
        raise FitError(f"{prepared_json}: NAV and par must be positive figures")
    return Portfolio(
        data["portfolio_id"],
        data["portfolio_name"],
        data["strategy"],
        nav,
        par,
        data["currency"],
        data["unit"],
        tuple(data["positions"]),
        tuple(data["limits"]),
    )


# --- writing ---------------------------------------------------------------------------------


def text(value: Decimal | None) -> str:
    return GAP if value is None else format(value.normalize(), "f")


def percent(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.1')):f}%"


def fit_row(f: Fit, run: Run) -> list[str]:
    p, i = f.portfolio, f.instrument
    return [
        p.portfolio_id,
        p.strategy,
        i.facility_id,
        i.name,
        text(f.current_exposure),
        percent(f.current_exposure_pct_nav),
        text(f.max_size) if f.max_size is not None else "unlimited",
        f.currency,
        f.unit,
        f.binding_limit or "none",
        f.verdict,
        f.recommendation_cap,
        f.reason,
    ]


def headroom_row(f: Fit, h: Headroom, run: Run) -> list[str]:
    limit = h.limit
    return [
        f.portfolio.portfolio_id,
        f.instrument.facility_id,
        str(limit["limit_id"]),
        str(limit["category"]),
        str(limit["parameter"]),
        str(limit["limit_kind"]),
        str(limit["limit_value"]),
        str(limit["unit"]),
        text(h.current_value),
        text(h.headroom),
        text(h.headroom_amount),
        run.currency,
        run.unit,
        h.status,
        str(limit["source"]),
    ]


def _table(table_id: str, columns: list[str], rows: list[list[str]]) -> list[str]:
    head = [f"<!-- table: {table_id} -->", "| " + " | ".join(columns) + " |"]
    body = ["| " + " | ".join(c.replace("|", "\\|") for c in r) + " |" for r in rows]
    return [*head, "|" + "---|" * len(columns), *body, ""]


def _not_computed(fits: list[Fit]) -> list[str]:
    lines = []
    for f in fits:
        missing = ", ".join(str(h.limit["limit_id"]) for h in f.rows if h.status == NOT_COMPUTED)
        if missing:
            where = f"{f.portfolio.portfolio_id} {f.instrument.facility_id}"
            lines.append(f"- {where}: {missing} not computed")
    return lines


def _gaps(fits: list[Fit], unparsed: Mapping[str, list[dict[str, str]]]) -> list[str]:
    """Limits RBOT does not size against, limits it could not compute, uncapped rows."""
    lines = [f"- {pid}: {u['row']}: {u['reason']}" for pid, rows in unparsed.items() for u in rows]
    lines += _not_computed(fits)
    if any(h.headroom_amount is None and h.status != NOT_COMPUTED for f in fits for h in f.rows):
        note = "a limit caps no size (count, maturity, a book statistic)"
        lines.append(f"- `headroom_amount` is `—` where {note}.")
    return lines or ["- None."]


def handoff(front: Mapping[str, str], fits: list[Fit], run: Run, notes: list[str]) -> str:
    worst = sorted({f.verdict for f in fits})
    portfolios = len({f.portfolio.portfolio_id for f in fits})
    analysis = (
        f"Host-computed Portfolio Fit (`rbot fit`) for {portfolios} "
        f"portfolio(s) and {len({f.instrument.facility_id for f in fits})} instrument(s); "
        f"verdicts: {', '.join(worst) or 'none'}. The arithmetic is interfaces spec section 7."
        if fits
        else "No portfolio is attached to this run, so no Portfolio Fit is computed."
    )
    lines = ["---", *(f"{k}: {v}" for k, v in front.items()), "---", "", "## Analysis", ""]
    lines += [analysis, "", "## Tables", ""]
    lines += _table("snapshot.portfolio_fit", FIT_COLUMNS, [fit_row(f, run) for f in fits])
    rows = [headroom_row(f, h, run) for f in fits for h in f.rows]
    lines += _table("fit.limit_headroom", HEADROOM_COLUMNS, rows)
    lines += ["## Gaps", "", *notes, "", "## Citations", ""]
    lines += _table("citations", ["id", "source", "locator", "excerpt"], [])
    return "\n".join(lines)


def fit_json(fits: list[Fit], run: Run) -> dict[str, Any]:
    """Every fit of one portfolio: the rows plus each intermediate."""
    return {
        "schema": "rbot-fit/1",
        "run_currency": run.currency,
        "run_unit": run.unit,
        "as_of": run.as_of.isoformat(),
        "instruments": [
            {
                "row": dict(zip(FIT_COLUMNS, fit_row(f, run), strict=True)),
                "limits": [
                    dict(zip(HEADROOM_COLUMNS, headroom_row(f, h, run), strict=True))
                    for h in f.rows
                ],
                "breached": [str(h.limit["limit_id"]) for h in f.rows if h.status == BREACHED],
            }
            for f in fits
        ],
    }


def run_fit(run: Path, root: Path) -> list[Fit]:
    brief = _read(run / "run-brief.md")
    cp1 = _read(run / "handoffs" / "CP-1.md")
    _cp3(run, root)
    cp1a_path = run / "handoffs" / "CP-1A.md"
    cp1a = _read(cp1a_path) if cp1a_path.is_file() else None
    facts = _run(brief, cp1)
    found = instruments(cp1, cp1a)
    fits, unparsed = [], {}
    for entry in _records(brief.tables.get("brief.portfolios")):
        p = portfolio(run, entry["prepared_json"])
        data = json.loads((run / entry["prepared_json"]).read_text(encoding="utf-8"))
        unparsed[p.portfolio_id] = data.get("unparsed", [])
        mine = [fit(p, i, facts) for i in found]
        (run / "fit").mkdir(exist_ok=True)
        text_json = json.dumps(fit_json(mine, facts), indent=2, ensure_ascii=False) + "\n"
        (run / "fit" / f"{p.portfolio_id}.json").write_text(text_json, encoding="utf-8")
        fits += mine
    notes = (
        _gaps(fits, unparsed)
        if fits
        else ["- No portfolio in the Portfolio Context: FIT computes nothing."]
    )
    restricted = not fits or any(n != "- None." for n in notes)
    inputs = ["CP-1", *(["CP-1A"] if cp1a else []), "CP-3", "RUN_BRIEF"]
    front = {
        "module_id": "FIT",
        "run_id": run.name,
        "issuer_id": facts.issuer_id,
        "analysis_date": facts.as_of.isoformat(),
        "qa_status": "Restricted" if restricted else "Pass",
        "inputs": ", ".join(inputs),
    }
    (run / "handoffs" / "FIT.md").write_text(handoff(front, fits, facts, notes), encoding="utf-8")
    return fits


def run_command(args: argparse.Namespace) -> int:
    try:
        fits = run_fit(Path(args.run_dir), args.root)
    except (FitError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"fit: {exc}")
        return 1
    print(f"handoffs/FIT.md and fit/*.json written; {len(fits)} portfolio x instrument fit(s)")
    for f in fits:
        print(f"{f.portfolio.portfolio_id} {f.instrument.facility_id}: {f.verdict} ({f.reason})")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("fit", help="Portfolio Fit for every portfolio and instrument of a run")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    c.set_defaults(run=run_command)
