"""v1 acceptance (Plan 08 tasks 08.4a, 08.4b): the run bar R1-R8, and the work-PC evidence ingest.

Repo tooling, never installed with the skill. `acceptance.py check --run <run folder>
[--pack-id <id>] [--live]` prints one `ID | PASS/FAIL/NOT MEASURED | measured | evidence` line per
criterion. Exit 0: every row PASS. Exit 1: a row is FAIL or NOT MEASURED (a gap is never a pass).
Exit 2: refused (the run cannot be read, or has no approved Pathway and depth to judge).

It only reads the run. Scoring is `scorecard`'s: `step_row`, the Front Page and Sources sections,
the host evidence check (`_forged`) and `state.read`; nothing is re-scored here. `--live` is for
the owner's live runs: the model label is the owner's picker label and the chat export, which no
run file holds, so R8 reaches at most NOT MEASURED there.

`acceptance.py ingest --evidence <bundle> --manifest <MANIFEST.json> --out <record.md>` turns the
evidence bundle from the work PC (plan section 6.2) into the L1-L11 / R1-R8 record of section 7.
Exit 0: every row PASS. Exit 1: a row is FAIL or NOT MEASURED. Exit 2: bad evidence (a missing or
unknown checklist key, an install of another commit, an unreadable probe, a missing or malformed
`<model>/check.txt` or `<model>/scorecard.md`). The runs are not re-read: `run-state.json`
binds its pack's absolute path, so the owner runs `tools/acceptance.py check --live` and
`tools/scorecard.py` on the work PC (both ship in the package) and returns their output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import scorecard
from ab_evidence import ABError

from rbotlib import attempts, corpus, state
from rbotlib.fsio import write_atomic
from rbotlib.handoff import HandoffError, parse
from rbotlib.inventory import RunError
from rbotlib.report import ReportError, run_json
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import EXIT_BLOCKED

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "NOT MEASURED"
PACK = "czr-2026q2-primary"
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


def _receipts(run: Path, record: state.Record, scored: Scored) -> tuple[list[str], list[str]]:
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
    return lacking, unlabelled


def r8(run: Path, record: state.Record, scored: Scored, live: bool) -> Result:
    lacking, unlabelled = _receipts(run, record, scored)
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


# --- ingest ------------------------------------------------------------------------------------

MODELS = ("claude", "gpt")
YES_NO = ("yes", "no")
COMMON_KEYS = (
    "package_sha256 os editor editor_version copilot_chat_version execution_policy python_cmd "
    "python_version wheels_install install_method"
).split()
MODEL_KEYS = (
    "picker_label context_tokens skills_lists_rbot rbot_invoked turns_before_approval "
    "questions_after_approval subagents report_opened start_utc finish_utc "
    "check_exit scorecard_exit"
).split()
CHOICES = {
    "wheels_install": YES_NO,
    "install_method": ("ps1", "manual"),
    "skills_lists_rbot": YES_NO,
    "rbot_invoked": YES_NO,
    "report_opened": YES_NO,
    "resume_ok": YES_NO,
    "subagents": ("yes", "fallback", "no"),
}
INTEGERS = (
    "context_tokens",
    "turns_before_approval",
    "questions_after_approval",
    "check_exit",
    "scorecard_exit",
)
REQUIRED = [
    *COMMON_KEYS,
    *(f"{m}_{k}" for m in MODELS for k in MODEL_KEYS),
    "claude_resume_ok",
]
PROBE_SECTION = re.compile(r"^## (\d)\. ", re.MULTILINE)
VERSION_LINE = re.compile(r"^rbot \S+ (\S+)\s*$", re.MULTILINE)
CRITERIA = {
    "L1": "Environment recorded",
    "L2": "pip policy",
    "L3": "PowerShell install",
    "L4": "Discovery",
    "L5": "Two-turn cp-start",
    "L6": "Unattended completion",
    "L7": "Resume (Claude run)",
    "L8": "Measured prompt budget",
    "L9": "Spike record",
    "L10": "Report opens on the work PC",
    "L11": "Model comparison",
}
BUDGET_FLOOR = 51200
Row = tuple[str, str, str, str]  # ID, split, status, evidence


def read_text(path: Path) -> str:
    """Windows PowerShell 5.1 `Tee-Object` and editors write UTF-16 or a UTF-8 BOM."""
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig", errors="replace")


def parse_checklist(text: str) -> dict[str, str]:
    """`key: value` lines; an unknown, duplicate, empty or out-of-vocabulary key is bad evidence."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        if key not in REQUIRED:
            raise RunError(f"checklist.txt: unknown key {key!r}")
        if key in found:
            raise RunError(f"checklist.txt: duplicate key {key!r}")
        found[key] = value.strip()
    empty = [k for k in REQUIRED if not found.get(k)]
    if empty:
        raise RunError("checklist.txt: missing or empty: " + ", ".join(empty))
    for key, value in found.items():
        _vocabulary(key, value)
    for m in MODELS:
        if _time(found[f"{m}_finish_utc"]) < _time(found[f"{m}_start_utc"]):
            raise RunError(f"checklist.txt: {m}_finish_utc is before {m}_start_utc")
    return found


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _vocabulary(key: str, value: str) -> None:
    name = key.split("_", 1)[1] if key.startswith(("claude_", "gpt_")) else key
    if name in CHOICES and value not in CHOICES[name]:
        raise RunError(f"checklist.txt: {key} must be one of {', '.join(CHOICES[name])}")
    if name in INTEGERS and not ((value.isdigit() and int(value) > 0) or value == "0"):
        raise RunError(f"checklist.txt: {key} must be a whole number")
    if name == "context_tokens" and int(value) == 0:
        raise RunError(f"checklist.txt: {key} must be positive")
    if name == "python_version" and not re.match(r"\d+\.\d+", value):
        raise RunError("checklist.txt: python_version must look like 3.11.9")
    if name.endswith("_utc"):
        try:
            _time(value)
        except ValueError as exc:
            raise RunError(f"checklist.txt: {key} is not an ISO time ({exc})") from exc


class Bundle:
    """The returned evidence: the three top-level files and, per model, probe, chat and run."""

    def __init__(self, root: Path) -> None:
        self.root = root
        for name in ("checklist.txt", "env.txt", "install.txt"):
            if not (root / name).is_file():
                raise RunError(f"evidence: {name} is missing")
        self.probe: dict[str, Path] = {}
        self.chat: dict[str, Path] = {}
        self.run: dict[str, Path] = {}
        for m in MODELS:
            folder = root / m
            chats = [p for p in (folder / "chat.json", folder / "chat.md") if p.is_file()]
            runs = [p for p in folder.glob("*/rbot-runs/*") if p.is_dir()]
            probe = folder / "rbot-probe-result.md"
            if not probe.is_file() or not chats or len(runs) != 1:
                raise RunError(f"evidence: {m}/ needs rbot-probe-result.md, a chat export, one run")
            self.probe[m], self.chat[m], self.run[m] = probe, chats[0], runs[0]


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise RunError(f"{path}: not a transfer MANIFEST.json")
    if not all(isinstance(data.get(k), str) and data[k] for k in ("commit", "runtime_tree")):
        raise RunError(f"{path}: not a transfer MANIFEST.json")
    return data


def check_install(text: str, manifest: dict[str, Any]) -> None:
    """`version` names the manifest's commit; the runtime tree is recorded beside it."""
    named = VERSION_LINE.findall(text)
    if manifest["commit"] not in named:
        raise RunError(
            f"install.txt: version names {', '.join(named) or 'no commit'}, "
            f"not the manifest's commit {manifest['commit']}"
        )
    if re.search(rf"\b{re.escape(manifest['runtime_tree'])}\b", text) is None:
        raise RunError(f"install.txt: runtime tree {manifest['runtime_tree']} is not recorded")


def probe_sections(path: Path) -> None:
    parts = PROBE_SECTION.split(read_text(path))
    found = {int(n): body.strip() for n, body in zip(parts[1::2], parts[2::2], strict=True)}
    gaps = [n for n in range(1, 7) if not found.get(n)]
    if gaps:
        raise RunError(f"{path.parent.name}/rbot-probe-result.md: empty or no section {gaps[0]}")


def prompt_files(manifest: dict[str, Any], runs: dict[str, Path]) -> dict[str, int]:
    """Byte sizes of the runtime's SKILL, canon and MODULE files (each proved to be the
    manifest's bytes) and of every dispatch file the returned runs hold."""
    sizes: dict[str, int] = {}
    modules = sorted(
        p.relative_to(RBOT_ROOT).as_posix() for p in RBOT_ROOT.glob("modules/*/MODULE.md")
    )
    for name in ("SKILL.md", "canon.md", *modules):
        raw = (RBOT_ROOT / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest["files"].get(f"rbot/{name}"):
            raise RunError(f"manifest: rbot/{name} differs from this checkout; ingest on the RC")
        sizes[name] = len(raw)
    for m, run in runs.items():
        found = {
            f"{m}/dispatch/{p.name}": p.stat().st_size for p in (run / "dispatch").glob("*.md")
        }
        if not found:
            raise RunError(f"evidence: the {m} run holds no dispatch file")
        sizes.update(found)
    return sizes


def l8(c: dict[str, str], sizes: dict[str, int]) -> tuple[str, str]:
    window = min(int(c[f"{m}_context_tokens"]) for m in MODELS)
    budget = window * 4 // 10
    name, largest = max(sizes.items(), key=lambda kv: kv[1])
    ok = largest <= budget
    text = f"largest {name} {largest} bytes {'<=' if ok else '>'} budget {budget} bytes"
    text += f" (smallest window {window} tokens)"
    if budget < BUDGET_FLOOR:
        text += "; budget below 51,200: catalog.json update due in 08.9"
    return (PASS if ok else FAIL), text


Cards = dict[str, tuple[list[Result], Path]]


def parse_check(text: str, where: str) -> list[Result]:
    """The eight rows `check` printed (`ID | verdict | measured | evidence`), each exactly once."""
    rows = [x.split(" | ", 3) for x in text.splitlines() if x.strip()]
    ids = [r[0] for r in rows]
    if ids != [f"R{n}" for n in range(1, 9)] or any(
        len(r) != 4 or r[1] not in (PASS, FAIL, UNMEASURED) for r in rows
    ):
        raise RunError(
            f"{where}: not the eight R1-R8 rows of `acceptance.py check` ({text[:80]!r})"
        )
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def _model_files(bundle: Bundle, c: dict[str, str], m: str) -> tuple[list[Result], str, str]:
    folder = bundle.root / m
    for name in ("check.txt", "scorecard.md"):
        if not (folder / name).is_file():
            raise RunError(f"evidence: {m}/{name} is missing")
    text, card = read_text(folder / "check.txt"), read_text(folder / "scorecard.md")
    results = parse_check(text, f"{m}/check.txt")
    code = 0 if all(r[1] == PASS for r in results) else 1
    if int(c[f"{m}_check_exit"]) != code or int(c[f"{m}_scorecard_exit"]) != 0:
        raise RunError(f"checklist.txt: {m} check/scorecard exit codes disagree with the files")
    if f"- Run: {bundle.run[m].name};" not in card:
        raise RunError(f"{m}/scorecard.md does not name the run {bundle.run[m].name}")
    return results, text, card


def score(bundle: Bundle, c: dict[str, str], out: Path) -> Cards:
    """Each model's `check --live` rows and scorecard, produced on the work PC (the run binds its
    own absolute path, so they cannot be re-run here); the scorecard must name the run."""
    scored = {}
    for m in MODELS:
        results, text, card = _model_files(bundle, c, m)
        for i, (rid, v, measured, evidence) in enumerate(results):
            if (rid, v) == ("R8", UNMEASURED):  # only the owner's label and chat export were open
                note = f"{evidence}; returned: {bundle.chat[m].name} and the label"
                results[i] = (rid, PASS, measured, note)
        (out / m).mkdir(parents=True, exist_ok=True)
        write_atomic(out / m / "scorecard.md", card)
        write_atomic(out / m / "check.txt", text)
        scored[m] = (results, out / m / "scorecard.md")
    return scored


def _each(c: dict[str, str], key: str) -> str:
    return ", ".join(f"{m} {c[f'{m}_{key}']}" for m in MODELS)


def _every(c: dict[str, str], key: str, want: str, models: tuple[str, ...] = MODELS) -> bool:
    return all(c[f"{m}_{key}"] == want for m in models)


def _environment_rows(bundle: Bundle, c: dict[str, str]) -> dict[str, tuple[bool, str]]:
    env = read_text(bundle.root / "env.txt")
    python = tuple(int(x) for x in c["python_version"].split(".")[:2])
    return {
        "L1": (
            python >= (3, 11) and bool(env.strip()),
            f"python {c['python_version']} (floor 3.11); {c['os']}; {c['editor_version']}; "
            f"Copilot Chat {c['copilot_chat_version']}; policy {c['execution_policy']}; env.txt",
        ),
        "L2": (c["wheels_install"] == "yes", f"wheels_install {c['wheels_install']}; probe 2"),
        "L3": (
            "0 problem(s)" in read_text(bundle.root / "install.txt"),
            f"install_method {c['install_method']}; install.txt: version, check",
        ),
        "L4": (
            _every(c, "skills_lists_rbot", "yes") and _every(c, "rbot_invoked", "yes"),
            f"skills_lists_rbot {_each(c, 'skills_lists_rbot')}; "
            f"rbot_invoked {_each(c, 'rbot_invoked')}",
        ),
        "L5": (
            _every(c, "turns_before_approval", "2") and _every(c, "questions_after_approval", "0"),
            f"turns {_each(c, 'turns_before_approval')}; "
            f"questions {_each(c, 'questions_after_approval')}",
        ),
    }


def l_rows(bundle: Bundle, c: dict[str, str], sizes: dict[str, int], scored: Cards) -> list[Row]:
    def all_pass(*models: str) -> bool:
        return all(v == PASS for m in models for _, v, _, _ in scored[m][0])

    def r2_pass(m: str) -> bool:
        return any(i == "R2" and v == PASS for i, v, _, _ in scored[m][0])

    spans = ", ".join(
        f"{m} {_time(c[f'{m}_finish_utc']) - _time(c[f'{m}_start_utc'])}" for m in MODELS
    )
    budget, budget_text = l8(c, sizes)
    cards = ", ".join(str(scored[m][1]) for m in MODELS)
    both = "R1-R8 on both runs"
    rows = _environment_rows(bundle, c) | {
        "L6": (
            _every(c, "subagents", "yes") and all_pass(*MODELS),
            f"{_each(c, 'subagents')}; {both}",
        ),
        "L7": (
            c["claude_resume_ok"] == "yes" and all_pass("claude"),
            f"claude_resume_ok {c['claude_resume_ok']}; R1-R8 on the claude run",
        ),
        "L8": (budget == PASS, budget_text),
        "L9": (True, "both probe files hold sections 1-6; content: docs/spike/copilot-spike.md"),
        "L10": (
            _every(c, "report_opened", "yes") and all(r2_pass(m) for m in MODELS),
            f"report_opened {_each(c, 'report_opened')}; R2 on both runs",
        ),
        "L11": (all_pass(*MODELS), f"{both}; durations {spans}; scorecards {cards}"),
    }
    return [
        (i, "B", PASS if ok else FAIL, why) for i, (ok, why) in sorted(rows.items(), key=_order)
    ]


def _order(item: tuple[str, object]) -> int:
    return int(item[0][1:])


def render(c: dict[str, str], manifest: dict[str, Any], rows: list[Row], bundle: Path) -> str:
    head = "| ID | Criterion | Split | Status (PASS / FAIL / PENDING OWNER / NOT MEASURED) |"
    lines = [
        f"# v1 work-PC acceptance record ({date.today().isoformat()})",
        "",
        f"- RC commit: {manifest['commit']}",
        f"- Runtime tree: {manifest['runtime_tree']}",
        f"- Package sha256: {c['package_sha256']}",
        f"- Evidence: {bundle.name}",
        "",
        head + " Evidence path |",
        "|---|---|---|---|---|",
    ]
    for i, split, status, evidence in rows:
        name = CRITERIA.get(i, "Run bar " + i[:2])
        lines.append(f"| {i} | {name} | {split} | {status} | {scorecard.clean(evidence)} |")
    lines += [
        "",
        "Rulings: NOT MEASURED is not a pass (exit 1). R8 on a live run is PASS when every module",
        "step has a receipt and an accept event and the label and chat export came back.",
        "L9 records that both probe files hold their six sections; the facts are filled into",
        "docs/spike/copilot-spike.md by the owner.",
        "",
        "Not verified: the content of the probe files and chat exports; the picker labels and "
        "context windows as typed in checklist.txt; the Agent-mode start of /rbot, the two-turn "
        "flow and the resume check beyond the checklist answers; anything on the work PC itself.",
        "",
    ]
    return "\n".join(lines)


def ingest(evidence: Path, manifest_path: Path, out: Path) -> int:
    bundle = Bundle(evidence.resolve())
    if out.resolve().is_relative_to(bundle.root) or out.suffix != ".md":
        raise RunError("--out must be a .md file outside the evidence folder")
    manifest = load_manifest(manifest_path)
    c = parse_checklist(read_text(bundle.root / "checklist.txt"))
    check_install(read_text(bundle.root / "install.txt"), manifest)
    for m in MODELS:
        probe_sections(bundle.probe[m])
    sizes = prompt_files(manifest, bundle.run)
    scored = score(bundle, c, out.with_suffix(""))
    rows = l_rows(bundle, c, sizes, scored)
    for m in MODELS:
        rows += [(f"{i} ({m})", f"B ({m})", v, f"{mm}; {ev}") for i, v, mm, ev in scored[m][0]]
    out.parent.mkdir(parents=True, exist_ok=True)
    write_atomic(out, render(c, manifest, rows, bundle.root))
    print(out)
    return 0 if all(r[2] == PASS for r in rows) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check", help="apply the run bar R1-R8 to a finished run")
    c.add_argument("--run", required=True, help="the run folder")
    c.add_argument("--pack-id", help="the pack's corpus id (default: from the run's pack)")
    c.add_argument("--live", action="store_true", help="a live run: model labels are the owner's")
    i = sub.add_parser("ingest", help="turn the work-PC evidence bundle into the acceptance record")
    i.add_argument("--evidence", required=True, help="the unzipped rbot-v1-evidence-<date> folder")
    i.add_argument("--manifest", required=True, help="MANIFEST.json of the transfer package")
    i.add_argument("--out", required=True, help="the record file; scorecards go beside it")
    args = parser.parse_args(argv)
    try:
        if args.command == "ingest":
            return ingest(Path(args.evidence), Path(args.manifest), Path(args.out))
        results = check(Path(args.run), args.pack_id, args.live)
    except (RunError, HandoffError, OSError, ValueError, ABError, KeyError) as exc:
        print(f"acceptance: {exc}")
        return 2
    for line in results:
        print(" | ".join(scorecard.clean(x) for x in line))
    return 0 if all(r[1] == PASS for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
