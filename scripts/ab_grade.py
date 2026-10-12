"""A/B harness for module rewrites (interfaces spec section 12.7; rubric `docs/ab/rubric.md`).

Repo tooling, never installed with the skill. The LLM work (the A and B runs, the graders) is
the controller's; this script does the mechanical parts:

- `to-r14 --in <handoff> --out <file>`: an upstream Handoff in r14's form for side A: r14's six
  H2 sections, `qa_status` Passed/Restricted/Blocked, each table under a heading with r14's
  `<!-- table-id: <id> -->` comment (CP-1's Model tables keep the ids r14 used; other tables
  keep their Deploy VI ids, which no r14 prompt names, so the heading gives the table's title).
- `order --out <order.json> [--x A|B]`: draws which of A and B the graders see as X (`--x`
  fixes it, for dry runs only).
- `measure --module <ID> --handoff <B.md> --run <RUN> [--expectations <json>]`: C (anchored
  citations / citations), F (filled critical cells / supportable critical cells of the Front Page
  tables the module owns, from the pack's expectations), the gap count and the size.
- `score --order <order.json> --sheets <g1.md> <g2.md> [<g3.md>] --c-b <ratio>
  [--c-a <ratio>] [--f-b <ratio>]`: maps the grader tables back to A and B, resolves them (the
  mean of two; the median of three, needed when two differ by more than 1 on a criterion), and
  applies the pass bar. Exit 0 pass, 1 fail, 3 when a third grader is needed.
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

from rbotlib.contract import Contract, load_contract
from rbotlib.handoff import Handoff, cells, parse
from rbotlib.rules import RBOT_ROOT, Rules, load_rules
from rbotlib.validate import check, run_findings

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


class ABError(ValueError):
    """An input the harness cannot read; the message names it."""


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
            out += [f"#### {tag.group(1)}", "", f"<!-- table-id: {tag.group(1)} -->"]
        else:
            out.append(line)
    return out


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
        "Evidence Trace": ["Each `[C<n>]` marker resolves in the Source Registry."],
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


# --- measure ---------------------------------------------------------------------------------


def _critical(h: Handoff, table_id: str, critical: set[str], rules: Rules) -> tuple[int, int]:
    table = h.tables.get(table_id)
    if table is None:
        return 0, 0
    index = [i for i, c in enumerate(table.columns) if c in critical]
    cells_ = [row[i] for row in table.rows for i in index if i < len(row)]
    filled = [c for c in cells_ if c.strip() and not rules.is_placeholder(c)]
    return len(filled), len(cells_)


def front_page_fill(contract: Contract, h: Handoff, expectations: Path, rules: Rules) -> str | None:
    """Filled / supportable critical cells of the Front Page tables the module owns."""
    owned = {t.id: {c.name for c in t.columns if c.critical} for t in contract.tables}
    pages = json.loads(expectations.read_text(encoding="utf-8")).get("front_pages", {})
    wanted = [s["table"] for page in pages.values() for s in page["supportable"]]
    counts = [_critical(h, t, owned[t], rules) for t in wanted if t in owned]
    if not counts:
        return None
    filled, total = map(sum, zip(*counts, strict=True))
    return f"{filled}/{total}"


def measure(module_id: str, text: str, run: Path, expectations: Path | None) -> dict[str, Any]:
    rules = load_rules()
    contract = load_contract(RBOT_ROOT / "modules" / module_id / "contract.json", rules)
    code, findings = check(text, contract, rules, run)
    h = parse(text)
    citations = h.tables.get("citations")
    total = len(citations.rows) if citations else 0
    bad = [f for f in run_findings(h, run) if f.code in ("citation_unanchored", "source_unknown")]
    gaps = _sections(h.body).get("Gaps", [])
    result: dict[str, Any] = {"module": module_id, "validate_exit": code}
    result |= {"findings": sorted({f.code for f in findings}), "C": f"{total - len(bad)}/{total}"}
    result |= {
        "gaps": sum(1 for line in gaps if line.startswith("- ")),
        "bytes": len(text.encode()),
    }
    result["qa_status"] = h.front_matter.get("qa_status")
    result["F"] = front_page_fill(contract, h, expectations, rules) if expectations else None
    return result


# --- score -----------------------------------------------------------------------------------


def sheet(text: str) -> dict[str, tuple[int, int]]:
    """criterion -> (X, Y) from a grader's Markdown table `criterion | X | Y | reason`."""
    found: dict[str, tuple[int, int]] = {}
    for line in text.splitlines():
        row = cells(line) if line.strip().startswith("|") else []
        if len(row) >= 3 and row[0] in CRITERIA:
            try:
                found[row[0]] = (int(row[1]), int(row[2]))
            except ValueError:
                raise ABError(
                    f"criterion {row[0]}: scores {row[1]!r}, {row[2]!r} are not 0-3"
                ) from None
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
    scores: dict[str, dict[str, Fraction]], c_b: Decimal, c_a: Decimal | None, f_b: Decimal | None
) -> dict[str, Any]:
    a, b = scores["A"], scores["B"]
    lines = {
        "sum_depth": sum(b[c] for c in DEPTH) >= sum(a[c] for c in DEPTH),
        "no_criterion_below_a_minus_1": all(b[c] >= a[c] - 1 for c in DEPTH),
        "citations": c_b >= max(Decimal("0.95"), c_a if c_a is not None else Decimal(0)),
        "gaps": b["G"] >= a["G"],
        "front_page": f_b is None or f_b >= Decimal("0.90"),
    }
    shown = {side: {c: str(v) for c, v in s.items()} for side, s in scores.items()}
    return {"pass": all(lines.values()), "lines": lines, "scores": shown}


def _ratio(text: str | None) -> Decimal | None:
    if text is None or text == "na":
        return None
    num, _, den = text.partition("/")
    return Decimal(num) / Decimal(den) if den else Decimal(num)


def _score(args: argparse.Namespace) -> int:
    order = json.loads(Path(args.order).read_text(encoding="utf-8"))
    sheets = [sheet(Path(p).read_text(encoding="utf-8")) for p in args.sheets]
    resolved = resolve(sheets, order)
    if "third" in resolved:
        print(json.dumps({"third_grader_needed": resolved["third"]}))
        return EXIT_THIRD
    c_b = _ratio(args.c_b)
    if c_b is None:
        raise ABError("--c-b is required: B's anchored citations / citations")
    result = verdict(resolved["scores"], c_b, _ratio(args.c_a), _ratio(args.f_b))
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
    s = sub.add_parser("score")
    s.add_argument("--order", required=True)
    s.add_argument("--sheets", nargs="+", required=True)
    s.add_argument("--c-b", dest="c_b", required=True)
    s.add_argument("--c-a", dest="c_a")
    s.add_argument("--f-b", dest="f_b")
    args = parser.parse_args(argv)
    try:
        return _command(args)
    except (ABError, OSError, json.JSONDecodeError) as exc:
        print(f"ab_grade: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
