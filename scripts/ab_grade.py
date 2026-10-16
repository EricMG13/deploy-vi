"""A/B harness for module rewrites (interfaces spec section 12.7; rubric `docs/ab/rubric.md`).

Repo tooling, never installed with the skill. The LLM work (the A and B runs, the graders) is
the controller's; this script does the mechanical parts:

- `to-r14 --in <handoff> --out <file>`: an upstream Handoff in r14's form for side A: r14's six
  H2 sections, `qa_status` Passed/Restricted/Blocked, each table under a heading with r14's
  `<!-- table-id: <id> -->` comment. Known upstream registers use their frozen r14 names
  and headings;
  tables without an r14 counterpart retain their explicit Deploy VI id. Columns and rows
  are preserved without inventing the fields a different r14 schema would require.
- `order --out <order.json> [--x A|B]`: draws which of A and B the graders see as X (`--x`
  fixes it, for dry runs only).
- `measure --module <ID> --handoff <B.md> --run <RUN> [--expectations <json>]`: C (anchored
  citations / citations), F (filled critical cells / the critical cells the pack's expectations
  say the Front Page tables the module owns should hold: `expected_rows` rows of every critical
  column, a missing row counting as unfilled), the gap count and the size.
- `steps --module <ID> --folder <r14 skill folder> --order <order.json> --out <AB>`: writes
  `<AB>/steps-X.md` and `<AB>/steps-Y.md`, the method each side was given (r14's SKILL.md and
  references for A, the module's MODULE.md for B), so the graders can score D1 and cannot tell
  which side is the rewrite from the file names.
- `score --order <order.json> --sheets <g1.md> <g2.md> [<g3.md>] --module <ID> --expectations
  <json> --c-b <ratio> --c-a <ratio> [--f-b <ratio>]`: maps the grader tables back to A and B,
  resolves them (the mean of two; the median of three, needed when two differ by more than 1 on
  a criterion), and applies the pass bar. `--f-b` is required when the module owns Front Page
  tables, and `--c-a` must be measured from A's checked native evidence map. Exit 0
  pass, 1 fail, 2 bad input, 3 when a third grader is needed.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import statistics
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

from ab_evidence import ABError as ABError
from ab_evidence import checked_findings
from ab_evidence import measure_a as measure_a

from rbotlib.contract import Contract, load_contract
from rbotlib.handoff import Handoff, HandoffError, Table, cells, parse
from rbotlib.rules import RBOT_ROOT, Rules, load_rules
from rbotlib.validate import ROW_KEYS, check, normalise, run_findings

CRITERIA = ("D1", "D2", "D3", "D4", "D5", "D6", "G")
DEPTH = CRITERIA[:6]
QA = dict(zip(("Pass", "Restricted", "Blocked"), ("Passed", "Restricted", "Blocked"), strict=True))
R14_SECTIONS = (
    "Audit Summary",
    "Analysis",
    "Evidence Trace",
    "Source Registry",
    "Gaps & Conflicts",
)
EXIT_PASS, EXIT_FAIL, EXIT_THIRD = 0, 1, 3
_TAG = re.compile(r"^<!-- table: (\S+) -->$")

# Register names are from the frozen r14 SKILL/schema references. Mapping changes the
# label only: source columns and rows remain lossless, including extra Deploy VI fields.
R14_REGISTERS = {
    "cp1.model_period_register": ("cp1.model_period_register", "T4.14 — Model Period Register"),
    "cp1.model_account_register": ("cp1.model_account_register", "T4.15 — Model Account Register"),
    "cp1.segment_revenue_schedule": (
        "cp1.segment_revenue_schedule",
        "T4.16 — Segment Revenue Schedule",
    ),
    "cp1.adjusted_ebitda_bridge": ("cp1.adjusted_ebitda_bridge", "T4.17 — Adjusted EBITDA Bridge"),
    "cp1.debt_facility_register": ("cp1.debt_facility_register", "T4.18 — Debt Facility Register"),
    "cp1.reconciliation_checks": (
        "cp1.model_reconciliation_register",
        "T4.19 — Model Reconciliation Register",
    ),
    "cp1b.period_comparison": (
        "cp1b.model_comparator_register",
        "T4.12 — Model Comparator Register",
    ),
    "cp1b.variance_drivers": ("T4.6", "T4.6 — Variance Register"),
    "cp1b.kpi_changes": ("T4.5", "T4.5 — KPI Dashboard"),
    "cp1b.guidance_vs_delivery": ("T4.8", "T4.8 — Comparative Evaluation"),
    "cp1b.signals": ("T4.10", "T4.10 — Monitoring Assessment"),
    "cp1d.cash_conversion": ("T1D.5", "T1D.5 — Cash Conversion Test"),
    "cp1d.debt_like_items": ("T1E.2", "T1E.2 — Debt-Like Assessment"),
    "cp2.drivers": ("T2.10", "T2.10 — Materiality Filter"),
    "cp2.watch_items": ("T2.12", "T2.12 — Monitoring Triggers"),
    "snapshot.relative_value": ("T3.5", "T3.5 — RV Table"),
    "cp3.compensation": ("T3B.7", "T3B.7 — Compensation Cross-Check"),
    "cp3.security_preference": ("T3B.8", "T3B.8 — Preference Decision Table"),
    "cp5.findings": ("T5.9", "T5.9 — Issue Log"),
    "cp5.module_status": ("T5.1", "T5.1 — Input Module Register"),
}


# --- to-r14 ----------------------------------------------------------------------------------


def _sections(body: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    current = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return found


def _tables(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        tag = _TAG.match(line.strip())
        if tag:
            register, title = R14_REGISTERS.get(tag.group(1), (tag.group(1), tag.group(1)))
            out += [f"#### {title}", "", f"<!-- table-id: {register} -->"]
        else:
            out.append(line)
    return out


def _evidence_trace(h: Handoff) -> list[str]:
    """Lossless references for converted stand-ins, using their actual citation rows."""
    table = h.tables.get("citations")
    if table is None:
        return []
    shown = [["id", "source_id", "locator", "excerpt"], ["---"] * 4]
    shown += [[r[0], r[0], r[2], r[3]] for r in table.rows if len(r) == 4]
    return ["| " + " | ".join(c.replace("|", "\\|") for c in row) + " |" for row in shown]


def to_r14(text: str) -> str:
    """The Handoff in r14's canonical Markdown form, its content unchanged."""
    h = parse(text)
    sections = _sections(h.body)
    fm = h.front_matter
    status = QA.get(fm.get("qa_status", ""), fm.get("qa_status", ""))
    front = [
        "---",
        f"module_id: {fm.get('module_id', '')}",
        f"issuer_id: {fm.get('issuer_id', '')}",
    ]
    front += [f"analysis_date: {fm.get('analysis_date', '')}", f"qa_status: {status}", "---", ""]
    summary = f"Upstream Handoff {fm.get('module_id', '')}, converted for the r14 comparison."
    analysis = [
        *sections.get("Analysis", []),
        "",
        "### Analytical appendix — complete canonical registers",
    ]
    analysis += _tables(sections.get("Tables", []))
    parts = {
        "Audit Summary": [summary, f"Inputs: {fm.get('inputs', 'none')}."],
        "Analysis": analysis,
        "Evidence Trace": _evidence_trace(h),
        "Source Registry": _tables(sections.get("Citations", [])),
        "Gaps & Conflicts": sections.get("Gaps", []),
    }
    out = list(front)
    for name in R14_SECTIONS:
        out += [f"## {name}", "", *[line for line in parts[name]], ""]
    out += [
        "## QA Validation",
        "",
        f"qa_status {status}, as the Deploy VI validator accepted it.",
        "",
    ]
    return "\n".join(out)


# --- order -----------------------------------------------------------------------------------


def draw(x: str | None = None) -> dict[str, str]:
    """{"X": "A"|"B", "Y": the other}: a secret draw, or `x` when the caller fixes it (a dry
    run on stand-in Handoffs)."""
    first = x if x in ("A", "B") else secrets.choice("AB")
    return {"X": first, "Y": "B" if first == "A" else "A"}


# --- steps -----------------------------------------------------------------------------------


def method_text(side: str, module_id: str, folder: str | None) -> str:
    """The method a side was given: r14's SKILL.md and references (A) or MODULE.md (B)."""
    if side == "B":
        path = RBOT_ROOT / "modules" / module_id / "MODULE.md"
        if not path.is_file():
            raise ABError(f"{module_id}: no MODULE.md")
        return path.read_text(encoding="utf-8")
    skills = RBOT_ROOT.parent / "reference" / "deploy-v-r14" / "skills"
    root = (skills / (folder or "")).resolve()
    if not folder or not root.is_dir() or not root.is_relative_to(skills.resolve()):
        raise ABError(f"--folder {folder!r} is not an r14 skill folder under {skills}")
    files = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    return "\n\n".join(f"<!-- {f.name} -->\n{f.read_text(encoding='utf-8')}" for f in files)


def write_steps(module_id: str, folder: str, order: dict[str, str], out: Path) -> None:
    texts = {label: method_text(order[label], module_id, folder) for label in ("X", "Y")}
    for label, text in texts.items():  # both read first: a bad folder leaves no half pair
        header = f"# Method given to side {label} ({module_id})\n\n"
        (out / f"steps-{label}.md").write_text(header + text, encoding="utf-8")


# --- measure ---------------------------------------------------------------------------------


def _fold(text: str) -> str:
    """Identity key: case-folded, with every non-alphanumeric character dropped."""
    return "".join(ch for ch in text.casefold() if ch.isalnum())


def _matches(record: dict[str, str], identity: dict[str, str]) -> bool:
    return all(_fold(record.get(k.casefold(), "")) == _fold(v) for k, v in identity.items())


def _expected_records(
    records: list[dict[str, str]], expected: list[dict[str, str]]
) -> list[dict[str, str]]:
    matches = [[r for r in records if _matches(r, identity)] for identity in expected]
    picked = [group[0] for group in matches if len(group) == 1]
    return [r for r in picked if sum(r is p for p in picked) == 1]


def _distinct_records(records: list[dict[str, str]], entry: dict[str, Any]) -> list[dict[str, str]]:
    keys = ROW_KEYS.get(entry["table"], ())
    identities = [tuple(_fold(r.get(k, "")) for k in keys) for r in records]
    return [
        r
        for r, key in zip(records, identities, strict=True)
        if not keys or identities.count(key) == 1
    ][: entry["expected_rows"]]


def _filled(table: Table | None, critical: set[str], entry: dict[str, Any], rules: Rules) -> int:
    """Count only uniquely matched expected identities; duplicates do not cover a row."""
    if table is None:
        return 0
    records = [
        dict(zip((c.casefold() for c in table.columns), r, strict=True))
        for r in table.rows
        if len(r) == len(table.columns)
    ]
    expected = entry.get("expected_identities")
    picked = (
        _expected_records(records, expected)
        if expected is not None
        else _distinct_records(records, entry)
    )
    return sum(
        bool(r.get(c, "").strip()) and not rules.is_placeholder(r[c])
        for r in picked
        for c in critical
    )


def owned_front_page_tables(contract: Contract, expectations: Path) -> list[dict[str, Any]]:
    """The expectations' supportable Front Page entries for tables the module owns."""
    try:
        pages = json.loads(expectations.read_text(encoding="utf-8")).get("front_pages", {})
    except UnicodeDecodeError as exc:
        raise ABError(f"{expectations}: not UTF-8 text ({exc.reason})") from exc
    owned = {t.id for t in contract.tables}
    found = [s for page in pages.values() for s in page["supportable"] if s["table"] in owned]
    for entry in found:
        _check_entry(entry, contract, expectations)
    return found


def _check_entry(entry: dict[str, Any], contract: Contract, expectations: Path) -> None:
    rows = entry.get("expected_rows")
    if not isinstance(rows, int) or isinstance(rows, bool) or rows < 1:
        raise ABError(f"{expectations}: {entry['table']} needs expected_rows, a whole number")
    identities = entry.get("expected_identities")
    if identities is None:
        return
    _check_identities(identities, rows, entry["table"])
    table = next(t for t in contract.tables if t.id == entry["table"])
    columns = {normalise(c.name) for c in table.columns}
    if any(normalise(k) not in columns for identity in identities for k in identity):
        raise ABError(f"{entry['table']}: expected identity uses an unknown column")


def _check_identities(identities: object, rows: int, table: str) -> None:
    if not isinstance(identities, list) or len(identities) != rows:
        raise ABError(f"{table}: expected_identities must match expected_rows")
    keys = []
    for identity in identities:
        if (
            not isinstance(identity, dict)
            or not identity
            or not all(
                isinstance(k, str) and isinstance(v, str) and k and v for k, v in identity.items()
            )
        ):
            raise ABError(f"{table}: expected identities need nonempty text keys and values")
        keys.append(tuple(sorted((normalise(k), normalise(v)) for k, v in identity.items())))
    if len(set(keys)) != len(keys):
        raise ABError(f"{table}: an expected identity is duplicated")


def front_page_fill(contract: Contract, h: Handoff, expectations: Path, rules: Rules) -> str | None:
    """Filled / supportable critical cells of the Front Page tables the module owns: a table
    should hold `expected_rows` rows of every critical column; a missing row is unfilled."""
    critical = {t.id: {c.name for c in t.columns if c.critical} for t in contract.tables}
    entries = owned_front_page_tables(contract, expectations)
    if not entries:
        return None
    total = sum(e["expected_rows"] * len(critical[e["table"]]) for e in entries)
    filled = sum(_filled(h.tables.get(e["table"]), critical[e["table"]], e, rules) for e in entries)
    return f"{filled}/{total}"


def measure(module_id: str, text: str, run: Path, expectations: Path | None) -> dict[str, Any]:
    rules = load_rules()
    path = RBOT_ROOT / "modules" / module_id / "contract.json"
    if not path.is_file():
        raise ABError(f"{module_id}: no module contract (the modules are CP-1 ... CP-6)")
    contract = load_contract(path, rules)
    code, findings = check(text, contract, rules, run)
    checked_findings(findings, run)
    try:
        h = parse(text)
    except HandoffError as exc:
        raise ABError(f"{module_id}: the Handoff cannot be read: {exc}") from exc
    citations = h.tables.get("citations")
    total = len(citations.rows) if citations else 0
    anchoring = checked_findings(run_findings(h, run), run)
    bad = sum(f.code in ("citation_unanchored", "source_unknown") for f in anchoring)
    gaps = _sections(h.body).get("Gaps", [])
    result: dict[str, Any] = {"module": module_id, "validate_exit": code}
    result |= {"findings": sorted({f.code for f in findings}), "C": f"{total - bad}/{total}"}
    result |= {
        "gaps": sum(1 for line in gaps if line.startswith("- ")),
        "bytes": len(text.encode()),
    }
    result["qa_status"] = h.front_matter.get("qa_status")
    result["F"] = front_page_fill(contract, h, expectations, rules) if expectations else None
    return result


# --- score -----------------------------------------------------------------------------------


def _scores(row: list[str]) -> tuple[int, int]:
    try:
        return int(row[1]), int(row[2])
    except ValueError:
        raise ABError(f"criterion {row[0]}: scores {row[1]!r}, {row[2]!r} are not 0-3") from None


def sheet(text: str) -> dict[str, tuple[int, int]]:
    """criterion -> (X, Y) from a grader's Markdown table `criterion | X | Y | reason`."""
    found: dict[str, tuple[int, int]] = {}
    for line in text.splitlines():
        row = cells(line) if line.strip().startswith("|") else []
        if len(row) >= 3 and row[0] in CRITERIA:
            if row[0] in found:
                raise ABError(f"criterion {row[0]} is scored twice in one grader sheet")
            found[row[0]] = _scores(row)
    missing = [c for c in CRITERIA if c not in found]
    if missing or any(not 0 <= s <= 3 for pair in found.values() for s in pair):
        raise ABError(f"a grader sheet needs every criterion scored 0-3; missing {missing}")
    return found


def resolve(sheets: list[dict[str, tuple[int, int]]], order: dict[str, str]) -> dict[str, Any]:
    """Per criterion, A's and B's resolved score; `third` when two sheets disagree by > 1."""
    if len(sheets) == 2:
        apart = [
            c for c in CRITERIA if any(abs(sheets[0][c][i] - sheets[1][c][i]) > 1 for i in (0, 1))
        ]
        if apart:
            return {"third": apart}
    pick = statistics.mean if len(sheets) == 2 else statistics.median
    x_side = order["X"]
    scores: dict[str, dict[str, Fraction]] = {"A": {}, "B": {}}
    for c in CRITERIA:
        x = Fraction(pick([Fraction(s[c][0]) for s in sheets]))
        y = Fraction(pick([Fraction(s[c][1]) for s in sheets]))
        scores[x_side][c], scores["B" if x_side == "A" else "A"][c] = x, y
    return {"scores": scores}


def verdict(
    scores: dict[str, dict[str, Fraction]], c_b: Decimal, c_a: Decimal, f_b: Decimal | None
) -> dict[str, Any]:
    a, b = scores["A"], scores["B"]
    lines = {
        "sum_depth": sum(b[c] for c in DEPTH) >= sum(a[c] for c in DEPTH),
        "no_criterion_below_a_minus_1": all(b[c] >= a[c] - 1 for c in DEPTH),
        "citations": c_b >= max(Decimal("0.95"), c_a),
        "gaps": b["G"] >= a["G"],
        "front_page": f_b is None or f_b >= Decimal("0.90"),
    }
    shown = {side: {c: str(v) for c, v in s.items()} for side, s in scores.items()}
    return {"pass": all(lines.values()), "lines": lines, "scores": shown}


def _ratio(text: str | None, name: str) -> Decimal | None:
    """Finite probability n/d or decimal; fraction denominator must be positive."""
    if text is None or text == "na":
        return None
    num, separator, den = text.partition("/")
    try:
        numerator = Decimal(num)
        denominator = Decimal(den) if separator else Decimal(1)
        if not _ratio_domain(numerator, denominator):
            raise ABError(f"{name}: {text!r} is not a ratio n/d or a decimal between 0 and 1")
        return numerator / denominator
    except ArithmeticError:
        raise ABError(f"{name}: {text!r} is not a ratio n/d or a decimal") from None


def _ratio_domain(numerator: Decimal, denominator: Decimal) -> bool:
    return (
        numerator.is_finite()
        and denominator.is_finite()
        and denominator > 0
        and 0 <= numerator <= denominator
    )


def _contract(module_id: str) -> Contract:
    path = RBOT_ROOT / "modules" / module_id / "contract.json"
    if not path.is_file():
        raise ABError(f"{module_id}: no module contract")
    return load_contract(path, load_rules())


def _score(args: argparse.Namespace) -> int:
    c_a = _ratio(args.c_a, "--c-a")
    if c_a is None:
        raise ABError("--c-a is required: A's checked anchored evidence references / references")
    order = json.loads(Path(args.order).read_text(encoding="utf-8"))
    sheets = [sheet(Path(p).read_text(encoding="utf-8")) for p in args.sheets]
    resolved = resolve(sheets, order)
    if "third" in resolved:
        print(json.dumps({"third_grader_needed": resolved["third"]}))
        return EXIT_THIRD
    c_b = _ratio(args.c_b, "--c-b")
    if c_b is None:
        raise ABError("--c-b is required: B's anchored citations / citations")
    f_b = _ratio(args.f_b, "--f-b")
    owned = owned_front_page_tables(_contract(args.module), Path(args.expectations))
    if owned and f_b is None:
        tables = ", ".join(e["table"] for e in owned)
        raise ABError(f"--f-b is required: {args.module} owns Front Page tables ({tables})")
    result = verdict(resolved["scores"], c_b, c_a, f_b)
    print(json.dumps(result, indent=2))
    return EXIT_PASS if result["pass"] else EXIT_FAIL


def _command(args: argparse.Namespace) -> int:
    if args.command == "to-r14":
        Path(args.out).write_text(to_r14(Path(args.in_path).read_text("utf-8")), "utf-8")
        return 0
    if args.command == "order":
        drawn = draw(args.x)
        Path(args.out).write_text(json.dumps(drawn) + "\n", encoding="utf-8")
        print(f"X={drawn['X']} Y={drawn['Y']}")
        return 0
    if args.command == "steps":
        order = json.loads(Path(args.order).read_text(encoding="utf-8"))
        write_steps(args.module, args.folder, order, Path(args.out))
        return 0
    if args.command == "measure-a":
        text = Path(args.handoff).read_text(encoding="utf-8")
        print(json.dumps(measure_a(text, Path(args.run_dir), Path(args.evidence))))
        return 0
    if args.command == "measure":
        text = Path(args.handoff).read_text(encoding="utf-8")
        exp = Path(args.expectations) if args.expectations else None
        print(json.dumps(measure(args.module, text, Path(args.run_dir), exp)))
        return 0
    return _score(args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("to-r14")
    r.add_argument("--in", dest="in_path", required=True)
    r.add_argument("--out", required=True)
    o = sub.add_parser("order")
    o.add_argument("--out", required=True)
    o.add_argument("--x", choices=["A", "B"])
    m = sub.add_parser("measure")
    m.add_argument("--module", required=True)
    m.add_argument("--handoff", required=True)
    m.add_argument("--run", dest="run_dir", required=True)
    m.add_argument("--expectations")
    a = sub.add_parser("measure-a")
    a.add_argument("--handoff", required=True)
    a.add_argument("--run", dest="run_dir", required=True)
    a.add_argument("--evidence", required=True, help="checked internal r14 qualification map")
    t = sub.add_parser("steps")
    t.add_argument("--module", required=True)
    t.add_argument("--folder", required=True, help="the module's r14 skill folder")
    t.add_argument("--order", required=True)
    t.add_argument("--out", required=True, help="the A/B folder")
    s = sub.add_parser("score")
    s.add_argument("--module", required=True)
    s.add_argument("--expectations", required=True)
    s.add_argument("--order", required=True)
    s.add_argument("--sheets", nargs="+", required=True)
    s.add_argument("--c-b", dest="c_b", required=True)
    s.add_argument("--c-a", dest="c_a")
    s.add_argument("--f-b", dest="f_b")
    args = parser.parse_args(argv)
    try:
        return _command(args)
    except (ABError, HandoffError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"ab_grade: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
