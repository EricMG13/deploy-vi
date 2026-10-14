"""v1 acceptance (Plan 08 task 08.4a): the run bar R1-R8 applied to one finished run.

Repo tooling, never installed with the skill. `acceptance.py check --run <run folder>
[--pack-id <id>] [--live]` prints one `ID | PASS/FAIL/NOT MEASURED | measured | evidence` line per
criterion. Exit 0: every row PASS. Exit 1: a row is FAIL or NOT MEASURED (a gap is never a pass).
Exit 2: refused (the run cannot be read, or has no approved Pathway and depth to judge).

It only reads the run. Scoring is `scorecard`'s: `step_row`, the Front Page and Sources sections,
the host evidence check (`_forged`) and `state.read`; nothing is re-scored here. `--live` is for
the owner's live runs: the model label is the owner's picker label and the chat export, which no
run file holds, so R8 reaches at most NOT MEASURED there.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import scorecard
from ab_evidence import ABError

from rbotlib import attempts, corpus, state
from rbotlib.handoff import HandoffError, parse
from rbotlib.inventory import RunError
from rbotlib.report import ReportError, run_json
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import EXIT_BLOCKED

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "NOT MEASURED"
CITATION_BAR = 0.95
FRONT_PAGE_BAR = 0.90
TERMINAL = ("accepted", "blocked", "failed", "skipped")
EMBED = re.compile(r'<script type="application/json" id="rbot-run">(.*?)</script>', re.DOTALL)
REMOTE = re.compile(
    r"""(?:\b(?:src|href|action|poster|srcset)\s*=\s*|url\(\s*|@import\s+)["']?\s*https?://""",
    re.IGNORECASE,
)
SOURCE_STATES = ("unchanged", "changed")  # the scorecard Sources section's last column
OVERALL = re.compile(r"^Overall measured owners: (\d+)/(\d+)\.$", re.MULTILINE)

Result = tuple[str, str, str, str]
Scored = list[tuple[scorecard.Row, str | None]]


def modules(scored: Scored) -> Scored:
    """The module steps that ended with a Handoff (accepted or blocked). Their text is present
    only when its bytes match the digest the state recorded; whether the step was independently
    accepted is R8's question, not R4's."""
    return [(r, t) for r, t in scored if r.kind == "module" and r.status in ("accepted", "blocked")]


def r1(record: state.Record) -> Result:
    open_steps = [n for n, s in record["steps"].items() if s["status"] not in TERMINAL]
    if open_steps:
        return "R1", FAIL, f"{len(open_steps)} open", "not terminal: " + ", ".join(open_steps)
    count = len(record["steps"])
    return "R1", PASS, f"{count}/{count} terminal", "every step is terminal (next would be done)"


def _file_problem(run: Path, name: str, recorded: object) -> str | None:
    path = run / name
    if path.is_symlink() or not path.is_file():
        return f"{name} is missing"
    if hashlib.sha256(path.read_bytes()).hexdigest() != recorded:
        return f"{name} sha256 differs from run-state.json"
    return None


def r2(run: Path, record: state.Record) -> Result:
    report = record["report"]
    if report.get("written_at") is None:
        return "R2", FAIL, "not rendered", "run-state.json report fields are null"
    problems = [
        p
        for p in (
            _file_problem(run, "report.html", report.get("html_sha256")),
            _file_problem(run, "report.md", report.get("md_sha256")),
        )
        if p
    ]
    if not problems:
        page = (run / "report.html").read_text(encoding="utf-8", errors="replace")
        if len(EMBED.findall(page)) != 1:
            problems.append("report.html does not embed exactly one #rbot-run")
        if REMOTE.search(page):
            problems.append("report.html loads an http(s) resource")
    measured = "files match" if not problems else f"{len(problems)} problem(s)"
    evidence = "; ".join(problems) or (
        "written_at recorded by a successful render; both sha256 match; #rbot-run embedded; "
        "no http(s) resource"
    )
    return "R2", FAIL if problems else PASS, measured, evidence


def r3(scored: Scored) -> Result:
    bad = {
        s: [r.step for r, _ in scored if r.status == s] for s in ("failed", "skipped", "blocked")
    }
    measured = ", ".join(f"{len(v)} {k}" for k, v in bad.items())
    named = "; ".join(f"{k}: {', '.join(v)}" for k, v in bad.items() if v)
    verdict = FAIL if named else PASS
    return "R3", verdict, measured, named or "no failed, skipped or Blocked step"


def r4(run: Path, scored: Scored) -> Result:
    parts, bad = [], []
    for row, text in modules(scored):
        try:
            cited = scorecard.citations(parse(text), run) if text else None
        except HandoffError:
            cited = None
        apart = cited.total - cited.image_read if cited else 0
        if cited is None or apart <= 0:
            bad.append(f"{row.step} unmeasurable")
            continue
        parts.append(f"{row.step} {cited.anchored}/{apart} (image-read {cited.image_read})")
        if cited.anchored < CITATION_BAR * apart:
            bad.append(f"{row.step} below {CITATION_BAR}")
    measured = f"{len(parts)} measured, {len(bad)} failing"
    return "R4", FAIL if bad else PASS, measured, "; ".join(bad or parts) or "no module step"


def r5(record: state.Record, scored: Scored, expectations: Path) -> Result:
    rows = {r.step: r for r, _ in scored}
    for r, t in scored:
        r.text = t if r.counted else None
    section = scorecard.front_page_section(record, rows, expectations, load_rules())
    named = [x for x in section if x.startswith("Not measured")]
    overall = OVERALL.search("\n".join(section))
    if overall is None:
        return "R5", UNMEASURED, scorecard.UNKNOWN, "; ".join(x for x in section if "unknown" in x)
    filled, total = int(overall[1]), int(overall[2])
    if total == 0:
        return "R5", UNMEASURED, "0/0", "the expectations name no supportable cells"
    ok = filled >= FRONT_PAGE_BAR * total
    evidence = " ".join(named) or "every supportable table measured"
    return "R5", PASS if ok else FAIL, f"{filled}/{total}", evidence


def _corpus_exit(pack_id: str) -> tuple[int | None, str]:
    try:
        registry = corpus.load_registry()
        problems = corpus.verify(registry, registry.pack(pack_id), corpus.resolve_roots(registry))
    except corpus.CorpusError as exc:
        return None, str(exc)
    return max((p.code for p in problems), default=0), "; ".join(p.message for p in problems)


def r6(run: Path, record: state.Record, pack_id: str) -> Result:
    section = scorecard.sources_section(run, record)
    files = [x for x in section if x.startswith("| ") and x.split("|")[-2].strip() in SOURCE_STATES]
    changed = [x.split("|")[1].strip() for x in files if x.split("|")[-2].strip() == "changed"]
    if any(x.startswith(scorecard.UNKNOWN) for x in section) or not files:
        return "R6", UNMEASURED, "unknown", "inventory.json is not readable in the run"
    code, why = _corpus_exit(pack_id)
    if changed:
        measured = f"{len(changed)} changed"
        return "R6", FAIL, measured, "changed: " + ", ".join(changed)
    if code is None:
        return "R6", UNMEASURED, f"{len(files)} unchanged", f"corpus verify not run: {why}"
    if code != 0:
        return "R6", FAIL, f"corpus verify exit {code}", why
    return "R6", PASS, f"{len(files)} unchanged", f"corpus verify --pack {pack_id} exit 0"


def _tab(run: Path) -> tuple[dict[str, Any], str]:
    """The Limitations content the Report carries: the embedded document when report.html
    exists, otherwise the one `render` would embed (built from the same run files)."""
    page = run / "report.html"
    if page.is_file() and not page.is_symlink():
        found = EMBED.findall(page.read_text(encoding="utf-8"))
        if len(found) == 1:
            doc: dict[str, Any] = json.loads(found[0])
            return doc["limitations"], "report.html #rbot-run"
    built = run_json.build(run, RBOT_ROOT, "1970-01-01T00:00:00+00:00")
    return built["limitations"], "run_json.build (report.html absent or unreadable)"


def _expected(run: Path, record: state.Record, scored: Scored) -> tuple[list[str], int]:
    """The (step, kind) items the tab must carry as unforeseen, and the CP-5 row count."""
    need = [f"{n}:{s['status']}" for n, s in record["steps"].items() if s["status"] in TERMINAL[1:]]
    cp5 = 0
    for row, text in scored:
        if row.step == "CP-5" and text:
            table = parse(text).tables.get("cp5.limitations")
            cp5 = len(table.rows) if table else 0
    return need, cp5


def _model_lost(run: Path, tab: dict[str, Any]) -> list[str]:
    """Model limitations and reconciliation faults of model.json missing from the tab."""
    path = run / "model.json"
    if not path.is_file():
        return []
    model = json.loads(path.read_text(encoding="utf-8"))
    items = [d["message"] for d in model.get("limitation_details", [])]
    for fault in model.get("reconciliation_faults", []):
        items.append(fault if isinstance(fault, str) else fault.get("message") or fault.get("code"))
    blob = json.dumps(tab, ensure_ascii=False)
    return [str(x)[:60] for x in items if json.dumps(x, ensure_ascii=False)[1:-1] not in blob]


def r7(run: Path, record: state.Record, scored: Scored) -> Result:
    try:
        tab, source = _tab(run)
        lost = [f"model: {x}" for x in _model_lost(run, tab)]
    except (ReportError, RunError, OSError, ValueError, KeyError, TypeError) as exc:
        return "R7", UNMEASURED, "unknown", f"Limitations tab or model.json unreadable: {exc}"
    need, cp5 = _expected(run, record, scored)
    shown = {f"{x.get('step')}:{x.get('kind')}" for x in tab["unforeseen"]}
    lost += [x for x in need if x not in shown]
    listed = {x.get("module_id") for x in tab["cp5"]} | {x.get("module") for x in tab["approval"]}
    listed |= {x.get("step") for x in tab["unforeseen"]}
    lost += [
        f"{r.step}:Restricted" for r, _ in scored if r.qa == "Restricted" and r.step not in listed
    ]
    if len(tab["cp5"]) != cp5:
        lost.append(f"cp5 rows {len(tab['cp5'])} != CP-5 {cp5}")
    count = cp5 + sum(not x.endswith(":blocked") for x in need)
    return "R7", FAIL if lost else PASS, f"{count} limitations", "; ".join(lost) or source


def r8(run: Path, record: state.Record, scored: Scored, live: bool) -> Result:
    lacking, unlabelled = [], []
    for row, _ in modules(scored):
        try:
            events = attempts.read_history(run, row.step, record["steps"][row.step])
        except RunError:
            events = []
        sent = any(e["event"] == "dispatch_report" for e in events)
        accepted = any(
            e["event"] == "validation" and e["result"]["exit"] in (0, EXIT_BLOCKED) for e in events
        )
        if not (sent and accepted):
            lacking.append(f"{row.step} ({'no receipt' if not sent else 'no accept event'})")
        if row.model == scorecard.UNKNOWN:
            unlabelled.append(row.step)
    measured = f"{len(lacking)} without receipt or accept"
    if lacking:
        return "R8", FAIL, measured, "; ".join(lacking)
    if live:
        why = "owner's picker label and chat export are not in the run"
        return "R8", UNMEASURED, measured, why
    if unlabelled:
        return "R8", FAIL, f"{len(unlabelled)} without model label", ", ".join(unlabelled)
    return "R8", PASS, measured, "receipt, accept event and model label on every module step"


def score_steps(run: Path, record: state.Record) -> Scored:
    forged = scorecard._forged(run, record)
    return [scorecard.step_row(run, n, record["steps"][n], forged) for n in record["plan"]]


def check(run: Path, pack_id: str | None, live: bool) -> list[Result]:
    run = state.run_path(run)
    record = state.read(run)
    if record["pathway"] is None or record["depth"] is None:
        raise RunError("the run has no approved Pathway and depth to judge")
    pack = pack_id or scorecard.pack_id_of(record)
    scored = score_steps(run, record)
    expectations = scorecard.EXPECTATIONS / f"{pack}.json"
    return [
        r1(record),
        r2(run, record),
        r3(scored),
        r4(run, scored),
        r5(record, scored, expectations),
        r6(run, record, pack),
        r7(run, record, scored),
        r8(run, record, scored, live),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check", help="apply the run bar R1-R8 to a finished run")
    c.add_argument("--run", required=True, help="the run folder")
    c.add_argument("--pack-id", help="the pack's corpus id (default: from the run's pack)")
    c.add_argument("--live", action="store_true", help="a live run: model labels are the owner's")
    args = parser.parse_args(argv)
    try:
        results = check(Path(args.run), args.pack_id, args.live)
    except (RunError, HandoffError, OSError, ValueError, ABError) as exc:
        print(f"acceptance: {exc}")
        return 2
    for line in results:
        print(" | ".join(scorecard.clean(x) for x in line))
    return 0 if all(r[1] == PASS for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
