"""Run scorecard (interfaces spec section 12.6 step 4; Plan 06 tasks 06.14 and 06.15).

Repo tooling, never installed with the skill. `scorecard.py --run <run folder> [--out <dir>]
[--pack-id <id>]` reads one recorded run and writes
`<out>/<date>-<pack_id>-<pathway>-<depth>.md` (default `docs/corpus-runs`). It only reads the run
(state, attempt history, Handoffs, `prepared/index.json`, `model.json`, `fit/`) and the pack's
expectations file; it never writes inside the run, and refuses an `--out` that is inside it.

A step counts as accepted only when `run-state.json` says so, the validation evidence the state
points at exists, and the current Handoff bytes hash to the recorded digest. A value the run does
not record prints `unknown`, never `0`. Image-Read citations are counted on their own and never
as anchored. Front Page completeness is `ab_grade.front_page_fill` per owning module; a module
that is not accepted contributes its supportable cells as unfilled, and an expectations entry
with no `expected_rows` is listed as not measured, never given an invented denominator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ab_evidence import ABError

import ab_grade
from rbotlib import attempts, catalog, current, state
from rbotlib.contract import Contract, load_contract
from rbotlib.fit import FIT_COLUMNS
from rbotlib.fsio import write_atomic
from rbotlib.handoff import Handoff, HandoffError, Table, parse
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, Rules, load_rules
from rbotlib.validate import EXIT_BLOCKED, run_findings

UNKNOWN = "unknown"
HOST_EVIDENCED = ("MODEL", "FIT")
EXPECTATIONS = RBOT_ROOT.parent / "tests" / "corpus" / "expectations"
DEFAULT_OUT = RBOT_ROOT.parent / "docs" / "corpus-runs"
FIT_TABLE = "snapshot.portfolio_fit"
RUN_LINE = re.compile(r"^- Run: ([^;\n]*)", re.MULTILINE)
NOT_VERIFIED = (
    "Not verified: Copilot behaviour (this is a proxy run, never a certification), GPT models, "
    "{fetch}, the provider identity behind model labels "
    "(caller-reported), worker isolation beyond the dispatch message, module A/B qualification "
    "(pending from Plan 05), and report rendering unless the Report line says it was written."
)
FETCH_NOT_VERIFIED = {
    "off": "fetch (fetch was off, so no network fetch was run or measured)",
    "on": "fetched-page quality (fetch was on; pages were saved but not independently checked)",
}


def fetch_mode(record: state.Record) -> str:
    """The mode recorded at Approval (absent reads as off), never the live variable."""
    return str(record["approval"].get("fetch", "off"))


@dataclass
class Citations:
    total: int
    anchored: int
    image_read: int

    def text(self) -> str:
        if self.total == 0:
            return f"{UNKNOWN} (no citation rows)"
        return f"{self.anchored}/{self.total}"


@dataclass
class Row:
    step: str
    kind: str
    status: str
    accepted: bool = False
    counted: bool = False  # accepted, or a validated Blocked Handoff measured as such
    text: str | None = None  # the counted Handoff text
    qa: str = UNKNOWN
    attempts: str = UNKNOWN
    exits: str = UNKNOWN
    citations: str = UNKNOWN
    image_read: str = UNKNOWN
    gaps: str = UNKNOWN
    size: str = UNKNOWN
    started: str = UNKNOWN
    finished: str = UNKNOWN
    duration: str = UNKNOWN
    model: str = UNKNOWN
    notes: list[str] = field(default_factory=list)


def clean(value: object) -> str:
    """One printable table-cell string: a caller or file claim never breaks the table."""
    text = "".join(c if unicodedata.category(c)[0] != "C" else " " for c in str(value))
    return text.replace("|", "\\|").strip() or UNKNOWN


# --- measurements ----------------------------------------------------------------------------


def citations(h: Handoff, run: Path) -> Citations | None:
    """Anchored / total from the native validator; None when the run's sources cannot be read.

    A row the validator flags, a row it cannot read, and an Image-Read row (nothing to anchor)
    are all outside `anchored`; the Image-Read rows are counted on their own."""
    table = h.tables.get("citations")
    rows = table.rows if table else []
    findings = run_findings(h, run)
    if any(f.code == "run_error" for f in findings):
        return None
    try:
        index = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
        records = {r["path"]: r for r in index["files"]}
    except (OSError, ValueError, KeyError, TypeError):
        return None
    flagged = sum(f.code in ("citation_unanchored", "source_unknown") for f in findings)
    unreadable = sum(len(r) < 4 for r in rows)
    image = sum(
        len(r) >= 4
        and r[1] in records
        and bool(records[r[1]].get("image_read"))
        and not records[r[1]].get("unreadable")
        for r in rows
    )
    return Citations(len(rows), max(len(rows) - flagged - unreadable - image, 0), image)


def duration(started: str, finished: str) -> str:
    try:
        seconds = (
            datetime.fromisoformat(finished) - datetime.fromisoformat(started)
        ).total_seconds()
    except ValueError:
        return UNKNOWN
    return f"{seconds:g}s" if seconds >= 0 else UNKNOWN


def front_page_text(
    contract: Contract, text: str | None, expectations: Path, rules: Rules
) -> tuple[int, int] | str | None:
    """(filled, total) cells for the Front Page tables a module owns; None when it owns none;
    a message when the expectations refuse. Without a counted Handoff the cells are unfilled."""
    try:
        if text is None:
            entries = ab_grade.owned_front_page_tables(contract, expectations)
            critical = {t.id: sum(c.critical for c in t.columns) for t in contract.tables}
            total = sum(e["expected_rows"] * critical[e["table"]] for e in entries)
            return (0, total) if entries else None
        fill = ab_grade.front_page_fill(contract, parse(text), expectations, rules)
    except (ABError, HandoffError) as exc:
        return f"refused: {exc}"
    if fill is None:
        return None
    filled, total = fill.split("/")
    return int(filled), int(total)


# --- one step --------------------------------------------------------------------------------


def _handoff_text(run: Path, step: state.Record, row: Row) -> str | None:
    """The current Handoff when it is the recorded accepted one; otherwise None, with the reason."""
    path = run / "handoffs" / f"{row.step}.md"
    recorded = step.get("sha256")
    edits = step.get("current_edits")
    if edits:
        recorded = current.result(step).get("sha256")
        row.notes.append("edited after acceptance (current edit recorded)")
    if recorded is None:
        row.notes.append("no recorded Handoff digest")
        return None
    if path.is_symlink() or not path.is_file():
        row.notes.append("Handoff file missing")
        return None
    raw = path.read_bytes()
    row.size = f"{len(raw)} B"
    if hashlib.sha256(raw).hexdigest() != recorded:
        row.notes.append("MISMATCH: Handoff bytes differ from the recorded digest")
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        row.notes.append("Handoff is not UTF-8")
        return None


def _history(run: Path, row: Row, step: state.Record) -> list[state.Record]:
    if row.kind != "module" or step.get("attempts") in (None, 0):
        return []
    try:
        return attempts.read_history(run, row.step, step)
    except RunError:
        row.notes.append("attempt history unreadable")
        return []


def _evidence(row: Row, step: state.Record, events: list[state.Record]) -> None:
    sent = [e for e in events if e["event"] == "dispatch_report"]
    checks = [e for e in events if e["event"] == "validation"]
    if checks:
        row.exits = ", ".join(f"{e['slot']}:{e['result']['exit']}" for e in checks)
    elif "validate_exit" in step:
        row.exits = f"{step['validate_exit']} (recorded, no attempt history)"
    labels = [e["model"] for e in sent if e.get("model")]
    row.model = clean(labels[-1] if labels else step.get("model", UNKNOWN))
    if sent and not any(e.get("worker_started_at") for e in sent):
        row.notes.append("worker start time unknown")


def _accepted(
    row: Row, step: state.Record, events: list[state.Record], forged: str | None = None
) -> bool:
    """Accepted needs the state's word and, past CP-0's receipt-free completion, a passing
    validation event in the attempt history: a state edit or an existing file is not enough.
    MODEL and FIT also need the host execution evidence (`forged` is its refusal message)."""
    if step["status"] != "accepted":
        return False
    if row.kind == "host":
        if forged is not None and row.step in HOST_EVIDENCED:
            row.notes.append(f"FORGED?: {forged}")
            return False
        return True
    passed = any(e["event"] == "validation" and e["result"]["exit"] == 0 for e in events)
    if passed or (row.step == "CP-0" and step.get("attempts") == 0):
        return True
    row.notes.append("FORGED?: accepted in state with no passing validation evidence")
    return False


def _blocked_counted(step: state.Record, events: list[state.Record]) -> bool:
    return step["status"] == "blocked" and any(
        e["event"] == "validation" and e["result"]["exit"] == EXIT_BLOCKED for e in events
    )


def step_row(
    run: Path, name: str, step: state.Record, forged: str | None = None
) -> tuple[Row, str | None]:
    row = Row(name, step["kind"], step["status"], qa=clean(step.get("qa_status", UNKNOWN)))
    if "attempts" in step:
        row.attempts = str(step["attempts"])
    if step["status"] in ("failed", "skipped") and step.get("reason"):
        row.notes.append(f"reason: {step['reason']}")
    row.started = clean(step.get("started_at", UNKNOWN))
    row.finished = clean(step.get("finished_at", UNKNOWN))
    row.duration = duration(row.started, row.finished)
    events = _history(run, row, step)
    _evidence(row, step, events)
    text = None
    if step["status"] in ("accepted", "blocked"):
        text = _handoff_text(run, step, row)
    row.accepted = _accepted(row, step, events, forged) and text is not None
    row.counted = row.accepted
    if text is not None and not row.accepted and _blocked_counted(step, events):
        row.counted = True
        row.notes.append("blocked: measured from its validated Handoff")
    if text is None:
        return row, None
    _measure(run, row, text)
    return row, text


def _measure(run: Path, row: Row, text: str) -> None:
    try:
        h = parse(text)
    except HandoffError:
        row.notes.append("Handoff cannot be read")
        return
    cited = citations(h, run)
    if cited is None:
        row.notes.append("citations unverifiable: the run's prepared sources cannot be read")
    else:
        row.citations, row.image_read = cited.text(), str(cited.image_read)
    if (RBOT_ROOT / "modules" / row.step / "contract.json").is_file():
        try:
            measured = ab_grade.measure(row.step, text, run, None)
        except ABError:
            row.notes.append("re-validation unverifiable")
        else:
            row.gaps = str(measured["gaps"])
            row.notes.append(f"re-validation exit {measured['validate_exit']}")


# --- sections --------------------------------------------------------------------------------


def _cell(value: object) -> str:
    return clean(value)


def steps_table(rows: list[Row]) -> list[str]:
    head = (
        "Step|Kind|Status|Accepted (verified)|QA|Attempts|Validate exit per attempt|"
        "Citations anchored/total|Image-Read citations|Gaps|Bytes|Started|Finished|Duration|"
        "Model label|Notes"
    ).split("|")
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        cells = [r.step, r.kind, r.status, "yes" if r.accepted else "no", r.qa, r.attempts]
        cells += [r.exits, r.citations, r.image_read, r.gaps, r.size, r.started, r.finished]
        cells += [r.duration, r.model, "; ".join(r.notes) or "-"]
        out.append("| " + " | ".join(_cell(c) for c in cells) + " |")
    return out


def _contracts(plan: list[str], rules: Rules) -> dict[str, Contract]:
    found = {}
    for name in plan:
        path = RBOT_ROOT / "modules" / name / "contract.json"
        if path.is_file():
            found[name] = load_contract(path, rules)
    return found


def owner_line(name: str, result: tuple[int, int] | str, note: str) -> str:
    if isinstance(result, str):
        return f"| {name} | {UNKNOWN} | {clean(result)} |"
    return f"| {name} | {result[0]}/{result[1]} | {note} |"


def unmeasured(
    supportable: list[dict[str, Any]], owned: set[str], cat: catalog.Catalog
) -> list[str]:
    missing = sorted(s["table"] for s in supportable if s["table"] not in owned)
    if not missing:
        return []
    shown = ", ".join(f"{t} ({cat.host_tables.get(t, 'no owner in this plan')})" for t in missing)
    return [
        "Not measured (owned by a host step or no module in this plan, and the "
        f"expectations give no expected_rows denominator; none is invented): {shown}."
    ]


def unique_facilities(table: Table) -> Table:
    """FIT rows whose (portfolio_id, facility_id) occurs once: a duplicated pair covers no row."""
    names = [c.casefold() for c in table.columns]
    if not {"portfolio_id", "facility_id"} <= set(names):
        return table
    at = (names.index("portfolio_id"), names.index("facility_id"))
    rows = [r for r in table.rows if len(r) == len(names)]
    keys = [tuple(r[i] for i in at) for r in rows]
    return Table(table.columns, [r for r, k in zip(rows, keys, strict=True) if keys.count(k) == 1])


def fit_cells(text: str | None, entry: dict[str, Any], rules: Rules) -> tuple[int, int] | str:
    """Filled / expected critical cells of the host FIT table (every FIT column is critical)."""
    total = entry["expected_rows"] * len(FIT_COLUMNS)
    if text is None:
        return 0, total
    try:
        table = parse(text).tables.get(FIT_TABLE)
    except HandoffError as exc:
        return f"refused: {exc}"
    table = unique_facilities(table) if table else None
    return ab_grade._filled(table, set(FIT_COLUMNS), entry, rules), total


def _owner_note(row: Row | None) -> str:
    if row is None or not row.counted:
        return "step not accepted: cells unfilled"
    return "-" if row.accepted else "blocked: measured from its validated Handoff"


def _owner_results(
    plan: list[str],
    rows: dict[str, Row],
    expectations: Path,
    fit: dict[str, Any] | None,
    rules: Rules,
) -> tuple[list[str], list[tuple[int, int]], int, set[str]]:
    lines, counted, refused, owned = [], [], 0, set[str]()
    results = []
    for name, contract in _contracts(plan, rules).items():
        owned |= {t.id for t in contract.tables}
        text = rows[name].text
        results.append((name, front_page_text(contract, text, expectations, rules)))
    if fit:
        owned.add(FIT_TABLE)
        results.append(("FIT", fit_cells(rows["FIT"].text, fit, rules)))
    for name, result in results:
        if result is None:
            continue
        lines.append(owner_line(name, result, _owner_note(rows.get(name))))
        if isinstance(result, str):
            refused += 1
        else:
            counted.append(result)
    return lines, counted, refused, owned


def front_page_section(
    record: state.Record,
    rows: dict[str, Row],
    expectations: Path | None,
    rules: Rules,
) -> list[str]:
    out = ["## Front Page completeness", ""]
    if expectations is None or not expectations.is_file():
        return [*out, f"{UNKNOWN}: no expectations file for this pack."]
    try:
        cat = catalog.load_catalog(RBOT_ROOT)
        pathway = cat.pathway(record["pathway"])
        pages = json.loads(expectations.read_text(encoding="utf-8")).get("front_pages", {})
    except (OSError, ValueError, KeyError) as exc:
        return [*out, f"{UNKNOWN}: expectations or catalog unreadable ({type(exc).__name__})."]
    if pathway is None or pathway.front_page not in pages:
        return [*out, f"{UNKNOWN}: no supportable cells listed for this Pathway's Front Page."]
    out += ["| Owner | Critical cells filled/supportable | Note |", "|---|---|---|"]
    supportable = pages[pathway.front_page]["supportable"]
    fit = next((s for s in supportable if s["table"] == FIT_TABLE and "expected_rows" in s), None)
    if "FIT" not in record["plan"] or cat.host_tables.get(FIT_TABLE) != "FIT":
        fit = None
    lines, counted, refused, owned = _owner_results(record["plan"], rows, expectations, fit, rules)
    cells = f"{sum(f for f, _ in counted)}/{sum(t for _, t in counted)}"
    overall = cells if not refused else f"{UNKNOWN} ({refused} refused)"
    out += [*lines, "", f"Overall measured owners: {overall}.", ""]
    return [*out, *unmeasured(supportable, owned, cat)]


def model_section(run: Path, step: state.Record, verified: bool) -> list[str]:
    """Limitations and faults, read only from a model.json that the verified MODEL step recorded."""
    out = ["## Model", ""]
    path = run / "model.json"
    if not path.is_file():
        return [*out, f"{UNKNOWN}: model.json is not in the run."]
    if not verified:
        return [*out, f"{UNKNOWN}: MODEL is not accepted (verified) in this run."]
    try:
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != step.get("outputs", {}).get("model.json"):
            return [*out, f"{UNKNOWN}: model.json differs from the digest MODEL recorded."]
        model = json.loads(raw)
        limits, faults = model["limitations"], model["reconciliation_faults"]
    except (OSError, ValueError, KeyError, TypeError):
        return [*out, f"{UNKNOWN}: model.json is not readable as an rbot model."]
    shown = ", ".join(clean(x) for x in limits) or "none"
    bad = ", ".join(clean(x) for x in faults) or "none"
    return [
        *out,
        f"- Limitations ({len(limits)}): {shown}",
        f"- Reconciliation faults ({len(faults)}): {bad}",
    ]


def sources_section(run: Path, record: state.Record) -> list[str]:
    out = ["## Sources", ""]
    try:
        files = json.loads((run / "inventory.json").read_text(encoding="utf-8"))["files"]
        out += ["| Path | sha256 | Now |", "|---|---|---|"]
        for f in files:
            out.append(
                f"| {clean(f['path'])} | {clean(f['sha256'])} | {_source_state(record, f)} |"
            )
    except (OSError, ValueError, KeyError, TypeError):
        return [*out, f"{UNKNOWN}: inventory.json is not readable in the run."]
    return out


def _source_state(record: state.Record, f: dict[str, Any]) -> str:
    try:
        now = hashlib.sha256((Path(record["pack_root"]) / f["path"]).read_bytes()).hexdigest()
    except OSError:
        return "changed"
    return "unchanged" if now == f["sha256"] else "changed"


def report_line(record: state.Record) -> str:
    report = record["report"]
    if report.get("written_at") is None:
        return "- Report: not rendered (report fields null)"
    return (
        f"- Report: written {clean(report['written_at'])}; html {clean(report.get('html_sha256'))}"
        f"; md {clean(report.get('md_sha256'))}"
    )


def fit_section(run: Path) -> list[str]:
    files = sorted((run / "fit").glob("*.json")) if (run / "fit").is_dir() else []
    names = ", ".join(f"{clean(p.name)} ({p.stat().st_size} B)" for p in files)
    return [
        "## Fit",
        "",
        f"- fit files: {names}" if files else f"- fit files: {UNKNOWN} (none in the run)",
    ]


# --- the report ------------------------------------------------------------------------------


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def pack_id_of(record: state.Record) -> str:
    """corpus-runs/<pack_id>/pack is where proxy_run puts the pack copy."""
    pack = Path(record["pack_root"])
    return pack.parent.name if pack.name == "pack" else pack.name


def _forged(run: Path, record: state.Record) -> str | None:
    """The read-only host evidence check of MODEL and FIT: its refusal message, else None."""
    try:
        current._host_origins(run, RBOT_ROOT, record)
    except RunError as exc:
        return str(exc)
    return None


def build(run: Path, pack_id: str | None) -> tuple[str, str]:
    """(file name, Markdown) for one run."""
    run = state.run_path(run)
    record = state.read(run)
    if record["pathway"] is None or record["depth"] is None:
        raise RunError("the run has no approved Pathway and depth to score")
    pack = pack_id or pack_id_of(record)
    rules = load_rules()
    rows, forged = [], _forged(run, record)
    for name in record["plan"]:
        row, text = step_row(run, name, record["steps"][name], forged)
        rows.append(row)
        row.text = text if row.counted else None
    accepted = sum(r.accepted for r in rows)
    by_name = {r.step: r.accepted for r in rows}
    head = [
        f"# Scorecard: {clean(record['pathway'])} {clean(record['depth'])} on {clean(pack)}",
        "",
        f"- Run: {clean(record['run_id'])}; created {clean(record['created_at'])}",
        f"- Steps accepted (verified): {accepted}/{len(rows)}",
        report_line(record),
        f"- Fetch: {fetch_mode(record)}",
        "- Source: recorded run evidence only; nothing here was re-run or estimated.",
        "",
        "## Steps",
        "",
    ]
    expectations = EXPECTATIONS / f"{pack}.json"
    body = [
        *steps_table(rows),
        "",
        *front_page_section(record, {r.step: r for r in rows}, expectations, rules),
        "",
        *model_section(run, record["steps"].get("MODEL", {}), by_name.get("MODEL", False)),
        "",
        *sources_section(run, record),
        "",
        *fit_section(run),
        "",
        NOT_VERIFIED.format(fetch=FETCH_NOT_VERIFIED[fetch_mode(record)]),
        "",
    ]
    name = (
        f"{record['created_at'][:10]}-{slug(pack)}-{slug(record['pathway'])}-{record['depth']}.md"
    )
    return name, "\n".join([*head, *body])


def refuse_inside(run: Path, out: Path) -> None:
    if out == run or run in out.parents:
        raise RunError("--out must be outside the run folder")


def refuse_other_run(target: Path, text: str) -> None:
    """A same-day scorecard of another run for the same pack, Pathway and depth is not replaced."""
    if not target.exists():
        return
    old, new = RUN_LINE.search(target.read_text(encoding="utf-8")), RUN_LINE.search(text)
    if old is None or new is None or old.group(1) != new.group(1):
        raise RunError(f"{target} records another run; it is left unchanged")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--run", required=True, help="the run folder")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="the output folder")
    parser.add_argument("--pack-id", help="the pack's corpus id (default: from the run's pack)")
    args = parser.parse_args(argv)
    try:
        run = state.run_path(Path(args.run))
        out = Path(args.out).resolve()
        refuse_inside(run, out)
        name, text = build(run, args.pack_id)
        out.mkdir(parents=True, exist_ok=True)
        refuse_other_run(out / name, text)
        write_atomic(out / name, text)
    except (RunError, ABError, HandoffError, OSError, ValueError) as exc:
        print(f"scorecard: {exc}")
        return 2
    print(out / name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
