"""Native deterministic diff publication and read-only canonical pair qualification."""

from __future__ import annotations

import argparse
import html
import json
import shlex
import sys
from pathlib import Path
from typing import Any

from rbotlib import current, dispatch, prior_context, state
from rbotlib.catalog import Catalog, load_catalog
from rbotlib.diff import compare
from rbotlib.fsio import write_atomic as write_atomic
from rbotlib.inventory import RunError
from rbotlib.isolation_capture import Capture
from rbotlib.prior_candidates import PriorCandidate
from rbotlib.prior_report import inspect_report

Record = dict[str, Any]
NAMES = ("prior/diff.json", "prior/diff.md")
EXTRA = {"model.house", "cp2.watch_items", "cp4.covenant_tests", "cp2h.rating_triggers"}


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _cell(value: object) -> str:
    text = (
        "[missing]" if value is None else value if isinstance(value, str) else _json(value).strip()
    )
    return (
        html.escape(text, quote=True)
        .replace("|", "&#124;")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
        .replace("*", "&#42;")
        .replace("`", "&#96;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
    )


def _markdown(result: Record) -> str:
    prior, now = result["prior"], result["current"]
    lines = [
        "# Prior comparison",
        "",
        f"Prior: {_cell(prior)}",
        f"Current: {_cell(now)}",
        f"Date basis: {_cell(result['date_basis'])}",
        f"Source: {_cell(result['inputs']['prior'])}",
        "Dates use snapshot.run_header.report_date where present. Current fallback uses "
        "Approval time, not publication time.",
        "",
        "| Table | Key | Field | Prior | Current | Change | Context | Reason |",
        "|---|---|---|---|---|---|---|---|",
    ]
    changed = [row for row in result["changes"] if row["kind"] != "unchanged"]
    for row in changed:
        fields = ("table", "key", "field", "prior", "current", "kind", "context", "reason")
        lines.append("| " + " | ".join(_cell(row[key]) for key in fields) + " |")
    if not changed:
        lines += ["", "No changed, added or removed comparable fields."]
    lines += ["", "## Limitations", ""]
    lines += ["- " + _cell(value) for value in result["limitations"]] or ["- None recorded."]
    return "\n".join(lines) + "\n"


def _front_tables(doc: Record, catalog: Catalog) -> tuple[str, ...]:
    pathway = catalog.pathway(doc["pathway"])
    page = (
        doc.get("front_page")
        if "front_page" in doc
        else (pathway.front_page if pathway is not None else None)
    )
    if not isinstance(page, str) or not page or page not in catalog.front_pages:
        raise RunError(f"Prior comparison: unknown/malformed Front Page: {page!r}")
    return catalog.front_pages[page]


def _limitations(doc: Record, side: str) -> list[str]:
    value = doc.get("limitations", {})
    if not isinstance(value, dict) or any(not isinstance(v, list) for v in value.values()):
        raise RunError(f"Prior comparison: {side} Report limitations must be an object of lists")
    return [f"{side} {kind}: {_json(v).strip()}" for kind, rows in value.items() for v in rows]


def _pair(context: prior_context.PriorContext, root: Path) -> tuple[Record, str]:
    prior = context.prior.payload
    if prior is None:
        raise RunError("Prior comparison: original payload missing")
    catalog = load_catalog(root)
    tables = set(EXTRA)
    for doc in (prior, context.current):
        tables.update(_front_tables(doc, catalog))
    result = compare(prior, context.current, sorted(tables))
    result["current"] = inspect_report(context.current)[0]
    result["inputs"] = context.binding
    for side, doc in (("prior", prior), ("current", context.current)):
        result["limitations"].extend(_limitations(doc, side))
    return result, _markdown(result)


def qualified_prior(run: Path, root: Path, record: Record) -> tuple[PriorCandidate, Record, str]:
    """Recompute and verify BOTH full files; safe under an existing caller-held lock."""
    run = state.run_path(run)
    choice = (record.get("prior_case") or {}).get("report")
    command = shlex.join(["rbot", "diff", "--run", str(run), "--prior", str(choice)])
    try:
        if state.write_guard(run) != record:
            raise RunError("caller state differs from current owned record")
        context = prior_context.capture(run, root)
        result, md = _pair(context, root)
        captured = Capture()
        for name, expected in zip(NAMES, (_json(result), md), strict=True):
            if captured.read(dispatch._file(run, name)) != expected.encode("utf-8"):
                raise RunError(f"{name}: canonical bytes differ")
        captured.verify()
        prior_context.requalify(run, root, context.binding)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        raise RunError(f"Prior comparison unavailable: {exc}; regenerate with {command}") from exc
    return context.prior, result, md


def run_command(args: argparse.Namespace) -> int:
    run = Path(args.run_dir)
    try:
        run = state.run_path(run)
        current.reconcile(run, args.root)
        with state.publication(run) as checked:
            context = prior_context.capture(run, args.root, args.prior)
            result, md = _pair(context, args.root)
            texts = (_json(result), md)
            targets = [dispatch._target(run, name) for name in NAMES]
            prior_context.requalify(run, args.root, context.binding)
            checked()
            targets[0].parent.mkdir(exist_ok=True)
            for name, text in zip(NAMES, texts, strict=True):
                target = dispatch._target(run, name)
                try:
                    checked()
                    write_atomic(target, text)
                except (OSError, UnicodeError) as exc:
                    raise RunError(f"{target}: publication failed: {exc}") from exc
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print(f"error: {run}: {exc}", file=sys.stderr)
        return 1
    for name in NAMES:
        print(f"{name}: {run / name}")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = sub.add_parser("diff", help="compare the approved original Prior Case with this run")
    parser.add_argument("--run", dest="run_dir", required=True)
    parser.add_argument("--prior", required=True)
    parser.set_defaults(run=run_command, log_run_guard=state.log_run_path)
