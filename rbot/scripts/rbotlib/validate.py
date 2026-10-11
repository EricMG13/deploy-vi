"""Check a Handoff against its module's contract and the shared rules.

Exit codes follow Deploy V: 0 valid, 2 malformed, 3 blocked (valid but
qa_status Blocked), 4 identity mismatch. A Handoff over the upstream cap
(spec section 7, caos MAX_UPSTREAM_HANDOFF_BYTES) is malformed: `too_large`.
With a run folder, a citation whose source is not in the run (`source_unknown`) or
whose excerpt is not in that source's prepared text, on the cited page when the
locator names one (`citation_unanchored`), is malformed too. A citation of an
Image-Read source (a screenshot or scan) has no text to anchor and is not checked.
"""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rbotlib.contract import Column, Contract, TableSpec
from rbotlib.handoff import Handoff, HandoffError, Table, cells, markers, parse
from rbotlib.rules import Rules

EXIT_VALID, EXIT_USAGE, EXIT_MALFORMED, EXIT_BLOCKED, EXIT_IDENTITY = 0, 1, 2, 3, 4
MAX_HANDOFF_BYTES = 98_304


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _front_matter(h: Handoff, contract: Contract, rules: Rules) -> list[Finding]:
    found = [
        Finding("front_matter_missing", f"front matter has no {key!r}")
        for key in rules.front_matter
        if not h.front_matter.get(key)
    ]
    module_id = h.front_matter.get("module_id")
    if module_id and module_id != contract.module_id:
        found.append(Finding("identity", f"module_id {module_id!r} is not {contract.module_id!r}"))
    status = h.front_matter.get("qa_status")
    if status and status not in rules.qa_status:
        found.append(Finding("qa_status", f"qa_status {status!r} not in {rules.qa_status}"))
    return found


def _sections(h: Handoff, rules: Rules) -> list[Finding]:
    if tuple(h.sections) == rules.sections:
        return []
    expected = list(rules.sections)
    return [Finding("sections", f"H2 sections are {h.sections}, expected {expected}")]


def _cell(column: Column, cell: str, where: str, rules: Rules) -> Finding | None:
    # A scale value is valid even when it reads like a placeholder ("N/A" is a
    # Recommendation); only then do the placeholder and scale rules apply.
    if column.scale and cell in rules.scales[column.scale]:
        return None
    if rules.is_placeholder(cell):
        return Finding("critical_placeholder", f"{where}: {cell!r}") if column.critical else None
    if column.scale:
        return Finding("off_scale", f"{where}: {cell!r}")
    return None


def _cell_findings(spec: TableSpec, table: Table, rules: Rules) -> list[Finding]:
    found: list[Finding] = []
    index = {name.casefold(): i for i, name in enumerate(table.columns)}
    present = [(c, index[c.name.casefold()]) for c in spec.columns if c.name.casefold() in index]
    for n, row in enumerate(table.rows, 1):
        if len(row) != len(table.columns):
            found.append(Finding("row_shape", f"{spec.id} row {n} has {len(row)} cells"))
            continue
        for column, i in present:
            finding = _cell(column, row[i], f"{spec.id} row {n} {column.name}", rules)
            if finding:
                found.append(finding)
    return found


def _table(spec: TableSpec, h: Handoff, rules: Rules) -> list[Finding]:
    table = h.tables.get(spec.id)
    if table is None:
        return [Finding("table_missing", f"no table tagged {spec.id}")]
    have = {c.casefold() for c in table.columns}
    found = [
        Finding("column_missing", f"{spec.id} has no column {c.name!r}")
        for c in spec.columns
        if c.name.casefold() not in have
    ]
    if len(table.rows) < spec.min_rows:
        found.append(
            Finding("too_few_rows", f"{spec.id} has {len(table.rows)} rows, needs {spec.min_rows}")
        )
    return found + _cell_findings(spec, table, rules)


def _tags(h: Handoff, contract: Contract) -> list[Finding]:
    declared = {t.id for t in contract.tables} | {"citations"}
    found = [Finding("duplicate_table", f"table {t} is tagged twice") for t in h.duplicate_tags]
    found += [Finding("orphan_tag", f"tag {t} has no table under it") for t in h.orphan_tags]
    found += [Finding("invalid_tag", f"tag {t!r} is not a table id") for t in h.invalid_tags]
    found += [
        Finding("undeclared_table", f"table {t} is not in the contract")
        for t in h.tables
        if t not in declared
    ]
    return found


def _outside_citation_rows(body: str, table: Table) -> str:
    """The body without the citations table's own rows, so a row cannot cite itself.

    Lines are compared as parsed cells, so an excerpt with an escaped pipe (A8) still matches.
    """
    rows = {tuple(row) for row in table.rows}
    kept = [line for line in body.splitlines() if tuple(cells(line)) not in rows]
    return "\n".join(kept)


def _citations(h: Handoff, rules: Rules) -> list[Finding]:
    table = h.tables.get("citations")
    if table is None:
        return [Finding("table_missing", "no table tagged citations")]
    if [c.casefold() for c in table.columns] != list(rules.citation_columns):
        expected = list(rules.citation_columns)
        return [Finding("column_missing", f"citations columns must be {expected}")]
    found: list[Finding] = []
    seen: Counter[str] = Counter()
    for row in table.rows:
        if len(row) != len(table.columns) or any(not cell.strip() for cell in row):
            found.append(Finding("citation_incomplete", f"citation row {row} has an empty cell"))
            continue
        seen[row[0]] += 1
    ids = set(seen)
    found += [
        Finding("duplicate_citation", f"citation id {c} appears on {n} rows")
        for c, n in seen.items()
        if n > 1
    ]
    used = markers(_outside_citation_rows(h.body, table))
    found += [
        Finding("unresolved_citation", f"[{c}] has no citation row") for c in sorted(used - ids)
    ]
    found += [Finding("unused_citation", f"{c} is never cited") for c in sorted(ids - used)]
    return found


# --- `--run`: every citation names a pack file and its excerpt is in that file ---------

_PAGE_WORD = r"\b(?:pp?|pgs?|pages?)\b\.?"
_PAGE_LOCATOR = re.compile(_PAGE_WORD + r"\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?", re.I)
_PAGE_LIKE = re.compile(_PAGE_WORD, re.I)
_PAGE_LINE = re.compile(r"^<<< page (\d+) >>>$", re.M)
_FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_QUOTES = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u02bc": "'",
        "\u2032": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00ad": None,
        "|": " ",
    }
)
MIN_EXCERPT_TOKENS, MIN_EXCERPT_CHARS = 3, 10


class _RunProblem(Exception):
    """The run folder cannot be read; the message is `<path>: <reason>`."""


def normalise(text: str) -> str:
    """Compare text as a reader would: NFKC, case-folded, plain quotes and dashes, one space.

    A hyphen at a line break is joined (`inter-\\nnational`); the soft hyphen is dropped.
    """
    plain = unicodedata.normalize("NFKC", text).translate(_QUOTES)
    return " ".join(re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", plain).casefold().split())


def _parts(excerpt: str) -> list[str]:
    return [n for n in (normalise(p) for p in re.split(r"\.\.\.|\u2026", excerpt)) if n]


def excerpt_found(text: str, excerpt: str) -> bool:
    """Every part of the excerpt (split at an ellipsis) appears in the text, in order."""
    haystack, at = normalise(text), 0
    for needle in _parts(excerpt):
        hit = re.compile(rf"(?<!\w){re.escape(needle)}(?!\w)").search(haystack, at)
        if hit is None:
            return False
        at = hit.end()
    return True


def too_short(excerpt: str) -> bool:
    """An excerpt of fewer than 3 words or 10 characters (ellipsis parts joined) anchors nothing."""
    joined = " ".join(_parts(excerpt))
    return len(joined.split()) < MIN_EXCERPT_TOKENS or len(joined) < MIN_EXCERPT_CHARS


def pages(prepared_text: str) -> dict[int, str]:
    """The text of each `<<< page N >>>` section; only the next number opens a page."""
    found: dict[int, list[str]] = {}
    at = 0
    for line in prepared_text.splitlines(keepends=True):
        m = _PAGE_LINE.match(line.rstrip("\n"))
        if m and int(m.group(1)) == len(found) + 1:
            at = int(m.group(1))
            found[at] = ["\n"]
        elif at:
            found[at].append(line)
    return {n: "".join(parts) for n, parts in found.items()}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _RunProblem(f"{path}: {getattr(exc, 'strerror', None) or exc}") from exc


def _sheet_rows(text: str) -> str:
    """A prepared sheet row by row: each CSV line's cells joined with spaces."""
    out = []
    for n, body in pages(text).items():
        rows = (" ".join(r) for r in csv.reader(io.StringIO(body.lstrip("\n"))))
        out.append(f"<<< page {n} >>>\n" + "\n".join(rows) + "\n")
    return "".join(out)


def _fetched(run: Path, source: str) -> str | None:
    """The body of a flat file directly in fetched/ (front matter stripped), else None."""
    folder = (run / "fetched").resolve()
    path = (run / source).resolve()
    if not source.startswith("fetched/") or path.parent != folder or not path.is_file():
        return None
    return "<<< page 1 >>>\n" + _FRONT_MATTER.sub("", _read(path), count=1)


def _source_text(
    run: Path, source: str, records: dict[str, dict[str, Any]]
) -> str | Finding | None:
    """The text a citation must anchor in; None for an Image-Read source (nothing to anchor)."""
    if (fetched := _fetched(run, source)) is not None:
        return fetched
    record = records.get(source)
    if record is None:
        return Finding("source_unknown", f"{source!r} is not in prepared/index.json or fetched/")
    if record["unreadable"]:
        return Finding("citation_unanchored", f"{source!r} is unreadable: {record['unreadable']}")
    if record["image_read"]:
        return None
    text = _read(run / str(record["prepared"]))
    return _sheet_rows(text) if record["kind"] in ("csv", "xlsx") else text


def _scope(by_page: dict[int, str], locator: str) -> list[str] | None:
    """The pages a locator names (all pages when it names none); None when unreadable."""
    wanted = _PAGE_LOCATOR.search(locator)
    if wanted:
        first = int(wanted.group(1))
        return [by_page.get(n, "") for n in range(first, int(wanted.group(2) or first) + 1)]
    return None if _PAGE_LIKE.search(locator) else list(by_page.values())


def _anchor(row: list[str], text: str) -> Finding | None:
    cid, source, locator, excerpt = row[:4]
    if too_short(excerpt):
        need = f"{MIN_EXCERPT_TOKENS} words and {MIN_EXCERPT_CHARS} characters"
        return Finding("citation_unanchored", f"{cid}: excerpt needs {need}: {excerpt!r}")
    scope = _scope(pages(text), locator)
    if scope is None:
        return Finding("citation_unanchored", f"{cid}: page locator {locator!r} not understood")
    if any(excerpt_found(page, excerpt) for page in scope):
        return None
    where = f"{source} {locator}" if _PAGE_LOCATOR.search(locator) else source
    return Finding("citation_unanchored", f"{cid}: excerpt not found in {where}: {excerpt!r}")


def _run_findings(h: Handoff, run: Path) -> list[Finding]:
    index_path = run / "prepared" / "index.json"
    try:
        records = {r["path"]: r for r in json.loads(_read(index_path))["files"]}
    except (ValueError, KeyError, TypeError) as exc:
        raise _RunProblem(f"{index_path}: not a prepared index ({exc})") from exc
    table = h.tables.get("citations")
    found: list[Finding] = []
    for row in table.rows if table else []:
        if len(row) < 4:
            continue
        text = _source_text(run, row[1], records)
        if isinstance(text, Finding):
            found.append(text)
        elif text is not None:
            found += [f for f in [_anchor(row, text)] if f]
    return found


def run_findings(h: Handoff, run: Path) -> list[Finding]:
    """source_unknown and citation_unanchored per row, or one run_error."""
    try:
        return _run_findings(h, run)
    except _RunProblem as exc:
        return [Finding("run_error", str(exc))]


def check(
    text: str, contract: Contract, rules: Rules, run: Path | None = None
) -> tuple[int, list[Finding]]:
    """Validate a Handoff; with `run`, also check each citation against the run's sources."""
    try:
        h = parse(text)
    except HandoffError as exc:
        return EXIT_MALFORMED, [Finding("not_a_handoff", str(exc))]
    findings = _front_matter(h, contract, rules) + _sections(h, rules) + _tags(h, contract)
    if run is not None:
        cited = run_findings(h, run)
        if [f.code for f in cited] == ["run_error"]:
            return EXIT_USAGE, cited
        findings += cited
    size = len(text.encode("utf-8"))
    if size > MAX_HANDOFF_BYTES:
        findings.append(Finding("too_large", f"{size} bytes; the cap is {MAX_HANDOFF_BYTES}"))
    for spec in contract.tables:
        findings += _table(spec, h, rules)
    findings += _citations(h, rules)
    if any(f.code == "identity" for f in findings):
        return EXIT_IDENTITY, findings
    if findings:
        return EXIT_MALFORMED, findings
    if h.front_matter.get("qa_status") == "Blocked":
        return EXIT_BLOCKED, findings
    return EXIT_VALID, findings
