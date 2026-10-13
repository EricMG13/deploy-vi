"""`rbot fit --run <RUN>`: the FIT host step (interfaces spec sections 3.4 and 7).

Reads `run-brief.md` (`snapshot.run_header`, `brief.portfolios`), each portfolio's
`prepared/portfolios/<id>.json`, `handoffs/CP-1.md` (`cp1.model_period_register` for the run's
currency and unit, `cp1.debt_facility_register`, `cp1.instrument_identity`),
`handoffs/CP-1A.md` when present (`snapshot.company_profile`: sector and country) and
`handoffs/CP-3.md`, which must validate against CP-3's contract (exit 0, or 3 when Blocked).
Writes `fit/<portfolio_id>.json` (the rows and every intermediate) and `handoffs/FIT.md` with
`snapshot.portfolio_fit` and `fit.limit_headroom`. A missing or malformed input exits 1
and writes nothing; every fit is computed before the first file is written (each atomically,
`FIT.md` last, files of portfolios no longer attached removed). Paths that leave the run folder,
a symlinked `fit/` or `handoffs/`, and portfolio ids that are not file names are refused. With no
portfolio the Handoff is written with empty tables and `qa_status` Restricted. A portfolio whose
NAV or par is not a positive figure is a Watch with the reason, not an error. The arithmetic is
`rbotlib.fit_arithmetic`.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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
from rbotlib.model import run as writer
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


SAFE_ID = re.compile(r"(?!\.)[A-Za-z0-9_.-]+")  # a portfolio id becomes a file name
UNITS = ("pct_nav", "pct_par", "amount", "count", "years")
KINDS = ("Hard", "Soft")
LIMIT_TEXT = "limit_id category parameter scope limit_kind unit source".split()
LIMIT_FIGURES = ("limit_value", "current_value")


class FitError(ValueError):
    """An input FIT needs is missing or malformed; the message names it."""


def _records(table: Table | None) -> list[dict[str, str]]:
    if table is None:
        return []
    return [dict(zip(table.columns, row, strict=False)) for row in table.rows]


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FitError(f"{path.name}: not UTF-8 text ({exc.reason})") from exc


def _read(path: Path) -> Handoff:
    if not path.is_file():
        raise FitError(f"{path.name}: missing; FIT needs it")
    try:
        return parse(_text(path))
    except HandoffError as exc:
        raise FitError(f"{path.name}: {exc}") from exc


def _inside(run: Path, relative: str, what: str) -> Path:
    """`relative` under the run folder; refused when it, or a link on the way, leaves it."""
    path = (run / relative).resolve()
    if not path.is_relative_to(run.resolve()):
        raise FitError(f"{what}: {relative!r} is outside the run folder")
    return path


def _cp3(run: Path, root: Path) -> None:
    """CP-3 must have run: its Handoff validates (exit 0, or 3 when Blocked)."""
    path = run / "handoffs" / "CP-3.md"
    if not path.is_file():
        raise FitError("handoffs/CP-3.md: missing; FIT runs after CP-3")
    rules = load_rules(root)
    contract = load_contract(root / "modules" / "CP-3" / "contract.json", rules)
    code, findings = check(_text(path), contract, rules)
    if code not in (EXIT_VALID, EXIT_BLOCKED):
        listed = "; ".join(f"{f.code}: {f.message}" for f in findings)
        raise FitError(f"handoffs/CP-3.md does not validate (exit {code}): {listed}")


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
    names = tuple(n for n in (header[0].get("issuer"),) if n and n != GAP)
    return Run(header[0]["issuer_id"], as_of, periods[0]["currency"], periods[0]["unit"], names)


def _latest_terms(cp1: Handoff) -> dict[str, dict[str, str]]:
    """Per facility, its register row of the latest period (by `end_date` in the period
    register; a period the register does not know counts as the oldest, a tie goes to the
    later row). A facility whose rows disagree on currency is refused."""
    ends = {
        r["period_id"]: _day(r.get("end_date")) or date.min
        for r in _records(cp1.tables.get("cp1.model_period_register"))
    }
    latest: dict[str, dict[str, str]] = {}
    for row in _records(cp1.tables.get("cp1.debt_facility_register")):
        seen = latest.get(row["facility_id"])
        if seen and seen["currency"] != row["currency"]:
            raise FitError(
                f"cp1.debt_facility_register: facility {row['facility_id']} has rows in "
                f"{seen['currency']} and {row['currency']}"
            )
        if seen is None or ends.get(row["period_id"], date.min) >= ends.get(
            seen["period_id"], date.min
        ):
            latest[row["facility_id"]] = row
    return latest


def instruments(cp1: Handoff, cp1a: Handoff | None) -> list[Instrument]:
    """Every `cp1.instrument_identity` row, with its terms from the latest facility row."""
    facilities = _latest_terms(cp1)
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


def _decimal(value: object, where: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        raise FitError(f"{where}: {value!r} is not a number")
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation:
        raise FitError(f"{where}: {value!r} is not a number") from None
    if not number.is_finite():
        raise FitError(f"{where}: {value!r} is not a finite number")
    return number


def _objects(data: Mapping[str, Any], key: str, name: str) -> list[dict[str, Any]]:
    rows = data.get(key)
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise FitError(f"{name}: {key} must be a list of objects")
    return rows


def _check_limit(limit: Mapping[str, Any], where: str) -> None:
    for key in LIMIT_TEXT:
        if not isinstance(limit.get(key), str):
            raise FitError(f"{where}: {key} must be text")
    for key in LIMIT_FIGURES:
        _decimal(limit.get(key), f"{where}: {key}")
    if limit["unit"] not in UNITS or limit["limit_kind"] not in KINDS:
        raise FitError(f"{where}: unit or limit_kind is not one the spec names")
    scope_value = limit.get("scope_value")
    if scope_value is not None and not isinstance(scope_value, str):
        raise FitError(f"{where}: scope_value must be text or null")
    listed = limit.get("scope_values", [])
    if not isinstance(listed, list) or not all(isinstance(v, str) for v in listed):
        raise FitError(f"{where}: scope_values must be a list of text")


def _check_prepared(data: object, name: str) -> dict[str, Any]:
    """The prepared portfolio's shape: an object, text fields, readable figures."""
    if not isinstance(data, dict):
        raise FitError(f"{name}: not a JSON object")
    for key in ("portfolio_id", "portfolio_name", "strategy", "currency", "unit"):
        if not isinstance(data.get(key), str):
            raise FitError(f"{name}: {key} must be text")
    if not SAFE_ID.fullmatch(data["portfolio_id"]):
        raise FitError(f"{name}: portfolio_id {data['portfolio_id']!r} is not a file name")
    for n, position in enumerate(_objects(data, "positions", name), 1):
        _decimal(position.get("par"), f"{name}: positions[{n}].par")
    for n, limit in enumerate(_objects(data, "limits", name), 1):
        _check_limit(limit, f"{name}: limits[{n}]")
    unparsed = data.get("unparsed", [])
    if not isinstance(unparsed, list) or not all(
        isinstance(u, dict) and isinstance(u.get("row"), str) and isinstance(u.get("reason"), str)
        for u in unparsed
    ):
        raise FitError(f"{name}: unparsed must be a list of row and reason")
    return data


def _positive(value: object) -> Decimal | None:
    """A NAV or par: None when missing or not a positive figure (the fit is then a Watch)."""
    try:
        number = _decimal(value, "figure")
    except FitError:
        return None
    return number if number > 0 else None


def portfolio(run: Path, prepared_json: str) -> Portfolio:
    path = _inside(run, prepared_json, "brief.portfolios prepared_json")
    if not path.is_file():
        raise FitError(f"{prepared_json}: missing; rbot prepare writes it")
    try:
        loaded = json.loads(_text(path))
    except json.JSONDecodeError as exc:
        raise FitError(f"{prepared_json}: not JSON ({exc.msg})") from exc
    return portfolio_data(loaded, prepared_json)


def portfolio_data(loaded: object, name: str) -> Portfolio:
    data = _check_prepared(loaded, name)
    return Portfolio(
        data["portfolio_id"],
        data["portfolio_name"],
        data["strategy"],
        _positive(data.get("nav")),
        _positive(data.get("par")),
        data["currency"],
        data["unit"],
        tuple(data["positions"]),
        tuple(data["limits"]),
        tuple(data.get("unparsed", [])),
    )


# --- writing ---------------------------------------------------------------------------------


def text(value: Decimal | None) -> str:
    return GAP if value is None else format(value.normalize(), "f")


def percent(value: Decimal | None) -> str:
    return GAP if value is None else f"{value.quantize(Decimal('0.1')):f}%"


def size(f: Fit) -> str:
    """`max_size`: a figure, `unlimited` when nothing caps it, `—` when a Hard limit that
    could cap it was not computed."""
    if f.max_size is not None:
        return text(f.max_size)
    return GAP if f.uncomputed_hard else "unlimited"


def reason(f: Fit) -> str:
    if not f.uncomputed_hard:
        return f.reason
    if f.reason == f"limit {f.uncomputed_hard[0]} could not be computed":
        return f"{f.reason}; max_size is an upper bound without it"
    return f"{f.reason}; max_size ignores Hard limit {', '.join(f.uncomputed_hard)} (not computed)"


def fit_row(f: Fit, run: Run) -> list[str]:
    p, i = f.portfolio, f.instrument
    return [
        p.portfolio_id,
        p.strategy,
        i.facility_id,
        i.name,
        text(f.current_exposure),
        percent(f.current_exposure_pct_nav),
        size(f),
        f.currency,
        f.unit,
        f.binding_limit or "none",
        f.verdict,
        f.recommendation_cap,
        reason(f),
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


def _exposure_gaps(fits: list[Fit], run: Run) -> list[str]:
    """Per portfolio, what the exposure rests on when no position or only a name matched."""
    lines, seen = [], set()
    for f in fits:
        p = f.portfolio.portfolio_id
        if p in seen or f.positions_held:
            continue
        seen.add(p)
        names = ", ".join(run.issuer_names) or GAP
        lines.append(
            f"- {p}: no position matched issuer_id {run.issuer_id} or issuer name {names}; "
            "current exposure 0 assumes the issuer is not held."
        )
    return lines


def _gaps(
    fits: list[Fit], unparsed: Mapping[str, Sequence[Mapping[str, str]]], run: Run
) -> list[str]:
    """Limits RBOT does not size against, limits it could not compute, uncapped rows, and what
    the exposure and the ratings rest on."""
    lines = [f"- {pid}: {u['row']}: {u['reason']}" for pid, rows in unparsed.items() for u in rows]
    missing_par = {f.portfolio.portfolio_id for f in fits if f.portfolio.par is None}
    lines += [
        f"- {p}: total par is missing or not positive; only pct_par limits require it."
        for p in sorted(missing_par)
    ]
    lines += _not_computed(fits)
    lines += _exposure_gaps(fits, run)
    lines += [f"- {f.portfolio.portfolio_id} {n}" for f in fits for n in f.notes]
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


def _folder(run: Path, name: str) -> Path:
    """A folder of the run, made when absent; a link or one outside the run is refused."""
    folder = run / name
    if folder.is_symlink() or not folder.resolve().is_relative_to(run.resolve()):
        raise FitError(f"{name}/: a link or outside the run folder")
    return folder


def _write_all(run: Path, per_portfolio: Mapping[str, str], handoff_text: str) -> None:
    """Publish precomputed outputs atomically per file: JSON files, then `FIT.md` last;
    stale JSON is removed. An I/O failure can interrupt this multi-file publication."""
    fit_dir, handoffs = _folder(run, "fit"), _folder(run, "handoffs")
    fit_dir.mkdir(exist_ok=True)
    handoffs.mkdir(exist_ok=True)
    files = {fit_dir / f"{pid}.json": body.encode() for pid, body in per_portfolio.items()}
    files[handoffs / "FIT.md"] = handoff_text.encode()
    writer.write_all(files)
    for old in fit_dir.glob("*.json"):
        if old not in files:
            old.unlink()


def run_fit(run: Path, root: Path) -> list[Fit]:
    brief = _read(run / "run-brief.md")
    cp1 = _read(run / "handoffs" / "CP-1.md")
    _cp3(run, root)
    cp1a_path = run / "handoffs" / "CP-1A.md"
    cp1a = _read(cp1a_path) if cp1a_path.is_file() else None
    portfolios = tuple(
        portfolio(run, entry["prepared_json"])
        for entry in _records(brief.tables.get("brief.portfolios"))
    )
    written, files = build(brief, cp1, cp1a, portfolios)
    bodies = {
        Path(name).stem: raw.decode() for name, raw in files.items() if name.endswith(".json")
    }
    _write_all(run, bodies, files["handoffs/FIT.md"].decode())
    return list(written.fits)


@dataclass(frozen=True, slots=True)
class Written:
    qa_status: str
    fits: tuple[Fit, ...]


def build(
    brief: Handoff,
    cp1: Handoff,
    cp1a: Handoff | None,
    portfolios: tuple[Portfolio, ...],
    missing: str = "",
) -> tuple[Written, dict[str, bytes]]:
    """Pure complete output set; qualified managed callers add provenance fingerprints."""
    facts = _run(brief, cp1)
    found = instruments(cp1, cp1a)
    fits: list[Fit] = []
    unparsed: dict[str, list[Mapping[str, str]]] = {}
    per_portfolio: dict[str, str] = {}
    for p in portfolios:
        if p.portfolio_id in per_portfolio:
            raise FitError(f"brief.portfolios: portfolio {p.portfolio_id} is listed twice")
        unparsed[p.portfolio_id] = list(p.unparsed)
        mine = [fit(p, i, facts) for i in found]
        per_portfolio[p.portfolio_id] = (
            json.dumps(fit_json(mine, facts), indent=2, ensure_ascii=False) + "\n"
        )
        fits += mine
    notes = (
        _gaps(fits, unparsed, facts)
        if fits
        else ["- No portfolio in the Portfolio Context: FIT computes nothing."]
    )
    if missing:
        notes = [n for n in notes if n != "- None."] + [f"- {missing}"]
    restricted = not fits or any(n != "- None." for n in notes)
    inputs = ["CP-1", *(["CP-1A"] if cp1a else []), "CP-3", "RUN_BRIEF"]
    front = {
        "module_id": "FIT",
        "run_id": brief.front_matter["run_id"],
        "issuer_id": facts.issuer_id,
        "analysis_date": facts.as_of.isoformat(),
        "qa_status": "Restricted" if restricted else "Pass",
        "inputs": ", ".join(inputs),
    }
    files = {f"fit/{pid}.json": raw.encode() for pid, raw in per_portfolio.items()}
    files["handoffs/FIT.md"] = handoff(front, fits, facts, notes).encode()
    return Written(front["qa_status"], tuple(fits)), files


def run_command(args: argparse.Namespace) -> int:
    try:
        fits = run_fit(Path(args.run_dir), args.root)
    except FitError as exc:
        print(f"fit: {exc}")
        return 1
    except (
        OSError,
        KeyError,
        ValueError,
    ) as exc:  # a Handoff table that lacks a column, a bad file
        print(f"fit: {type(exc).__name__}: {exc}")
        return 1
    print(f"handoffs/FIT.md and fit/*.json written; {len(fits)} portfolio x instrument fit(s)")
    for f in fits:
        print(f"{f.portfolio.portfolio_id} {f.instrument.facility_id}: {f.verdict} ({f.reason})")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("fit", help="Portfolio Fit for every portfolio and instrument of a run")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    c.set_defaults(run=run_command)
