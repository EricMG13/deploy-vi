"""Check a Handoff against its module's contract and the shared rules.

Exit codes follow Deploy V: 0 valid, 2 malformed, 3 blocked (valid but
qa_status Blocked), 4 identity mismatch. A Handoff over the upstream cap
(spec section 7, caos MAX_UPSTREAM_HANDOFF_BYTES) is malformed: `too_large`. A Blocked
Handoff (qa_status Blocked) keeps every table, column and scale but may leave critical cells at
`—` and tables short of `min_rows`: that is how a module that cannot proceed says so.
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
from typing import Any, NamedTuple

from rbotlib import state
from rbotlib.contract import Column, Contract, TableSpec
from rbotlib.handoff import Handoff, HandoffError, Table, cells, markers, parse, unfenced
from rbotlib.rules import Rules

EXIT_VALID, EXIT_USAGE, EXIT_MALFORMED, EXIT_BLOCKED, EXIT_IDENTITY = 0, 1, 2, 3, 4
MAX_HANDOFF_BYTES = 98_304
ROW_KEYS = {
    "snapshot.recommendation": ("strategy",),
    "snapshot.instrument_recommendation": ("facility_id",),
    "snapshot.instrument_levels": ("facility_id",),
    "snapshot.relative_value": ("block", "name"),
    "snapshot.strengths_weaknesses": ("kind", "label"),
}


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
    return found + _inputs(h.front_matter.get("inputs"), contract)


def _inputs(value: str | None, contract: Contract) -> list[Finding]:
    """`inputs:` is `none` or Handoff ids: a subset of the contract's, every required one in."""
    if not value:
        return []
    allowed, required = contract.handoff_inputs(), set(contract.handoff_inputs(required_only=True))
    named = [] if value == "none" else [v.strip() for v in value.split(",")]
    unknown = [n for n in named if n not in allowed]
    missing = sorted(required - set(named))
    if unknown:
        return [
            Finding("inputs", f"inputs names {unknown}; this module's Handoff inputs: {allowed}")
        ]
    if missing:
        return [Finding("inputs", f"inputs omits the required Handoff input(s) {missing}")]
    return []


def _sections(h: Handoff, rules: Rules) -> list[Finding]:
    if tuple(h.sections) == rules.sections:
        return []
    expected = list(rules.sections)
    return [Finding("sections", f"H2 sections are {h.sections}, expected {expected}")]


def _cell(column: Column, cell: str, where: str, rules: Rules, blocked: bool) -> Finding | None:
    # A scale value is valid even when it reads like a placeholder ("N/A" is a
    # Recommendation); only then do the placeholder and scale rules apply.
    if column.scale and cell in rules.scales[column.scale]:
        return None
    if rules.is_placeholder(cell):
        critical = column.critical and not blocked
        return Finding("critical_placeholder", f"{where}: {cell!r}") if critical else None
    if column.scale:
        return Finding("off_scale", f"{where}: {cell!r}")
    return None


def _cell_findings(spec: TableSpec, table: Table, rules: Rules, blocked: bool) -> list[Finding]:
    found: list[Finding] = []
    index = {name.casefold(): i for i, name in enumerate(table.columns)}
    present = [(c, index[c.name.casefold()]) for c in spec.columns if c.name.casefold() in index]
    for n, row in enumerate(table.rows, 1):
        if len(row) != len(table.columns):
            found.append(Finding("row_shape", f"{spec.id} row {n} has {len(row)} cells"))
            continue
        for column, i in present:
            finding = _cell(column, row[i], f"{spec.id} row {n} {column.name}", rules, blocked)
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
    blocked = h.front_matter.get("qa_status") == "Blocked"
    if len(table.rows) < spec.min_rows and not blocked:
        found.append(
            Finding("too_few_rows", f"{spec.id} has {len(table.rows)} rows, needs {spec.min_rows}")
        )
    return found + _cell_findings(spec, table, rules, blocked) + _row_keys(spec, table, rules)


def _row_keys(spec: TableSpec, table: Table, rules: Rules) -> list[Finding]:
    keys = ROW_KEYS.get(spec.id, ())
    columns = [c.casefold() for c in table.columns]
    if not keys or not all(k in columns for k in keys):
        return []
    positions = [columns.index(k) for k in keys]
    seen: Counter[tuple[str, ...]] = Counter()
    for row in table.rows:
        if len(row) != len(columns):
            continue
        key = _identity_key(row, positions, rules)
        if _unknown_key(key, rules):
            continue
        seen[key] += 1
    return [
        Finding("duplicate_row_key", f"{spec.id}: {keys} {k} appears {n} times")
        for k, n in seen.items()
        if n > 1
    ]


def _identity_key(row: list[str], positions: list[int], rules: Rules) -> tuple[str, ...]:
    return tuple("" if rules.is_placeholder(row[i]) else normalise(row[i]) for i in positions)


def _unknown_key(key: tuple[str, ...], rules: Rules) -> bool:
    return any(not k or rules.is_placeholder(k) for k in key)


_PLACEHOLDER = re.compile(r"\[\[[A-Za-z0-9_-]+\]\]")


def _placeholders(h: Handoff) -> list[Finding]:
    """A `[[identifier]]` template token left in the body: the writer never filled it in."""
    tokens = dict.fromkeys(_PLACEHOLDER.findall(h.body))
    return [
        Finding("unresolved_placeholder", f"unresolved template placeholder {t}") for t in tokens
    ]


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
    used = markers(unfenced(_outside_citation_rows(h.body, table)))
    found += [
        Finding("unresolved_citation", f"[{c}] has no citation row") for c in sorted(used - ids)
    ]
    found += [Finding("unused_citation", f"{c} is never cited") for c in sorted(ids - used)]
    return found


# --- `--run`: every citation names a pack file and its excerpt is in that file ---------

_PAGE_WORD = r"\b(?:pp?|pgs?|pages?)(?![A-Za-z_&])\.?"
_PAGE_LOCATOR = re.compile(_PAGE_WORD + r"\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?", re.I)
_PAGE_LIKE = re.compile(_PAGE_WORD, re.I)
_PAGE_LINE = re.compile(r"^<<< page (\d+) >>>$", re.M)
_FRONT_MATTER = re.compile(r"\A---\n.*?\n---(?:\n|\Z)", re.S)
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
MIN_EXCERPT_TOKENS, MIN_EXCERPT_CHARS, MIN_PART_TOKENS = 2, 8, 2
INDEX_KEYS = ("unreadable", "image_read", "prepared", "kind")


class _RunProblem(Exception):
    """The run folder cannot be read; the message is `<path>: <reason>`."""


_LETTER = r"[^\W\d_]"
_BREAK = re.compile(rf"(?<!\w)({_LETTER}+)[-\u00ad\u2010-\u2012\u2212]\s*\n\s*(?={_LETTER})")


_THIN_GROUPS = re.compile(r"(?<!\d)\d{1,3}(?:[\u202f\u2009\u00a0]\d{3})+(?!\d)")
_THIN = re.compile(r"[\u202f\u2009\u00a0]")


def _join_break(match: re.Match[str]) -> str:
    """Keep short uppercase labels (B-, BB-, CCC-, USD-) intact across lines."""
    first = match.group(1)
    return match.group() if len(first) <= 3 and first.isupper() else first


def normalise(text: str) -> str:
    """Compare text as a reader would: NFKC, case-folded, plain quotes and dashes, one space.

    A hyphen (or soft hyphen) at a line break between two letters is joined
    (`inter-\\nnational`); the soft hyphen is dropped elsewhere. A thousands group
    separated by a thin, narrow or no-break space (`11 486`) becomes one number.
    """
    grouped = _THIN_GROUPS.sub(lambda m: _THIN.sub("", m.group()), text)
    joined = unicodedata.normalize("NFKC", grouped)
    while (unbroken := _BREAK.sub(_join_break, joined)) != joined:
        joined = unbroken
    return " ".join(joined.translate(_QUOTES).casefold().split())


def _parts(excerpt: str) -> list[str]:
    return [n for n in (normalise(p) for p in re.split(r"\.\.\.|\u2026", excerpt)) if n]


_SIGNED = re.compile(r"(?:us\$|[$\u00a3\u20ac\u00a5])?\s*\d")
_CUT_AFTER = r"(?!\s?(?:%|x\b|bps?\b))(?!-\d)"
_GRADE_END = re.compile(
    r"(?<!\w)(?:AAA|AA|A|BBB|BB|B|CCC|CC|C|D|SD|RD|NR|WR|Ca|"
    r"(?:Aa|A|Baa|Ba|B|Caa)[123])[+-]?$",
    re.I,
)


def _needle(text: str) -> re.Pattern[str]:
    """The text as a whole-token match that never starts or ends inside a number.

    A leading number or currency amount is not a match when a minus sign (not a
    range hyphen as in `300-325` or `Q2-2026`) or an opening bracket sits before it;
    a trailing number is not a match when a `%`, `x`, `bp(s)` or range follows it.
    """
    before = r"(?<!\w)(?<!\d[.,])"
    if _SIGNED.match(text):
        before += r"(?<!(?<!\w)-)" + (r"(?<!\()" if ")" not in text else "")
    after = r"(?!\w)(?![.,]\d)" + (_CUT_AFTER if text[-1].isdigit() else "")
    if _GRADE_END.search(text):
        after += r"(?![+-])"
    return re.compile(before + re.escape(text) + after)


_SIGN_PREFIX = re.compile(r"(?<!\w)-\s*(?:us\$|[$£€¥])?\s*$")
_RANGE_PREFIX = re.compile(r"\d\s+-\s*$")
_ACCOUNT_PREFIX = re.compile(r"\(\s*(?:us\$|[$£€¥])?\s*$")


def _cut_sign(haystack: str, start: int, needle: str) -> bool:
    """A numeric excerpt cannot discard the source amount's sign/currency prefix.

    Normalized whitespace is one character; eight preceding characters cover a
    sign, optional US$ currency and their spaces, including the range boundary.
    """
    if not _SIGNED.match(needle):
        return False
    prefix = haystack[max(0, start - 8) : start]
    return bool(
        (_SIGN_PREFIX.search(prefix) and not _RANGE_PREFIX.search(prefix))
        or (")" not in needle and _ACCOUNT_PREFIX.search(prefix))
    )


def excerpt_found(text: str, excerpt: str) -> bool:
    """Every part of the excerpt (split at an ellipsis) appears in the text, in order."""
    haystack, at = normalise(text), 0
    for needle in _parts(excerpt):
        hit = next(
            (
                m
                for m in _needle(needle).finditer(haystack, at)
                if not _cut_sign(haystack, m.start(), needle)
            ),
            None,
        )
        if hit is None:
            return False
        at = hit.end()
    return True


def too_short(excerpt: str) -> bool:
    """Under 2 words or 8 characters overall, or an ellipsis part under 2 words, anchors nothing."""
    parts = _parts(excerpt)
    joined = " ".join(parts)
    thin = any(len(p.split()) < MIN_PART_TOKENS for p in parts)
    return thin or len(joined.split()) < MIN_EXCERPT_TOKENS or len(joined) < MIN_EXCERPT_CHARS


def pages(prepared_text: str) -> dict[int, str]:
    """The text of each `<<< page N >>>` section; only the next number opens a page."""
    found: dict[int, list[str]] = {}
    at = 0
    for line in re.split(r"(?<=\n)", prepared_text):  # \n only: other breaks stay in the line
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
    if not source.startswith("fetched/") or any(ord(c) < 32 for c in source):
        return None
    if len(source.encode("utf-8")) > 255:
        return None
    if (run / "fetched").is_symlink():
        return None
    path = (run / source).resolve()
    if path.parent != (run / "fetched").resolve() or not path.is_file():
        return None
    return "<<< page 1 >>>\n" + _FRONT_MATTER.sub("", _read(path), count=1)


class Source(NamedTuple):
    text: str
    rows: bool  # a sheet: an excerpt must anchor within one row


def _source_text(
    run: Path, source: str, records: dict[str, dict[str, Any]]
) -> Source | Finding | None:
    """The text a citation must anchor in; None for an Image-Read source (nothing to anchor)."""
    if (fetched := _fetched(run, source)) is not None:
        return Source(fetched, False)
    record = records.get(source)
    if record is None:
        return Finding("source_unknown", f"{source!r} is not in prepared/index.json or fetched/")
    if record["unreadable"]:
        return Finding("citation_unanchored", f"{source!r} is unreadable: {record['unreadable']}")
    if record["image_read"]:
        return None
    text = _read(run / str(record["prepared"]))
    if record["kind"] in ("csv", "xlsx"):
        return Source(_sheet_rows(text), True)
    return Source(text, False)


def _scope(by_page: dict[int, str], locator: str) -> list[str] | None:
    """The pages a locator names (all pages when it names none); None when unreadable."""
    wanted = _PAGE_LOCATOR.search(locator)
    if wanted:
        first = int(wanted.group(1))
        last = min(int(wanted.group(2) or first), len(by_page))
        return [by_page.get(n, "") for n in range(first, last + 1)]
    return None if _PAGE_LIKE.search(locator) else list(by_page.values())


def _anchor(row: list[str], source_text: Source) -> Finding | None:
    cid, source, locator, excerpt = row[:4]
    if too_short(excerpt):
        need = f"{MIN_EXCERPT_TOKENS} words and {MIN_EXCERPT_CHARS} characters"
        joined = " ".join(_parts(excerpt))
        if len(joined.split()) >= MIN_EXCERPT_TOKENS and len(joined) >= MIN_EXCERPT_CHARS:
            need = f"each part between ellipses needs {MIN_PART_TOKENS} words"
        return Finding("citation_unanchored", f"{cid}: excerpt needs {need}: {excerpt!r}")
    scope = _scope(pages(source_text.text), locator)
    if scope is None:
        return Finding("citation_unanchored", f"{cid}: page locator {locator!r} not understood")
    if source_text.rows:
        scope = [line for page in scope for line in page.splitlines()]
    if any(excerpt_found(unit, excerpt) for unit in scope):
        return None
    where = f"{source} {locator}" if _PAGE_LOCATOR.search(locator) else source
    return Finding("citation_unanchored", f"{cid}: excerpt not found in {where}: {excerpt!r}")


def _records(index_path: Path) -> dict[str, dict[str, Any]]:
    """The prepared index by path; a record without a key a citation needs is a run error."""
    try:
        records = {r["path"]: r for r in json.loads(_read(index_path))["files"]}
        bad = [(p, k) for p, r in records.items() for k in INDEX_KEYS if k not in r]
    except (ValueError, KeyError, TypeError) as exc:
        raise _RunProblem(f"{index_path}: not a prepared index ({exc})") from exc
    if bad:
        raise _RunProblem(f"{index_path}: record {bad[0][0]!r} lacks {bad[0][1]!r}")
    return records


def _run_findings(h: Handoff, run: Path) -> list[Finding]:
    records = _records(run / "prepared" / "index.json")
    table = h.tables.get("citations")
    found: list[Finding] = []
    for row in table.rows if table else []:
        if len(row) < 4:
            continue
        source = _source_text(run, row[1], records)
        if isinstance(source, Finding):
            found.append(source)
        elif source is not None:
            found += [f for f in [_anchor(row, source)] if f]
    return found


def run_findings(h: Handoff, run: Path) -> list[Finding]:
    """source_unknown and citation_unanchored per row, or one run_error."""
    try:
        return _run_findings(h, run)
    except _RunProblem as exc:
        return [Finding("run_error", str(exc))]


def _blocked_gate(h: Handoff, rules: Rules) -> list[Finding]:
    """CP-3 step 12: Blocked only with no market level and no talk (else Restricted)."""
    if h.front_matter.get("qa_status") != "Blocked":
        return []
    levels, talk = h.tables.get("snapshot.instrument_levels"), h.tables.get("cp3.talk_valuation")
    held: list[str] = []
    for table, key, col in (
        (levels, "facility_id", "level_basis"),
        (talk, "facility_id", "talk_mid"),
    ):
        if table is None or key not in table.columns or col not in table.columns:
            continue
        at, ident = table.columns.index(col), table.columns.index(key)
        held += [
            row[ident]
            for row in table.rows
            if len(row) == len(table.columns) and not rules.is_placeholder(row[at])
        ]
    if not held:
        return []
    return [
        Finding(
            "blocked_gate",
            f"qa_status is Blocked but {held[0]} holds a market level or talk; the contract "
            "allows Blocked only with no market level and no talk, so a missing "
            "level, call schedule or comparable makes it Restricted",
        )
    ]


def _module_findings(
    h: Handoff, contract: Contract, rules: Rules, run: Path | None
) -> list[Finding]:
    """A module's own checks beyond its tables: CP-0's in `rbotlib.cp0` (Plan 04), CP-3's gate."""
    if contract.module_id == "CP-3":
        return _blocked_gate(h, rules)
    if contract.module_id != "CP-0":
        return []
    from rbotlib import cp0  # imported here: cp0 builds on this module's Finding

    return cp0.findings(h, rules, run)


def _host_findings(
    h: Handoff, contract: Contract, run: Path | None, found: list[Finding]
) -> list[Finding]:
    """What a host step that reads this module would refuse (`rbotlib.host_preflight`);
    asked only of a Handoff in a run that has no other finding."""
    if run is None or found:
        return []
    from rbotlib import host_preflight  # imported here: it builds on this module's Finding

    return host_preflight.findings(h, contract.module_id, run)


# --- depth rules: the §2.20 LITE policy and the run's depth against each `basis` -----------

DEPTH_BASIS = {"full": "Full", "quick": "Screening"}
SCREEN_TABLE = "cpl10.screen_topics"
SCREEN_COLUMNS = ("topic_id", "family", "materiality", "evidence_status", "disposition")


def _column(table: Table, name: str) -> int | None:
    names = [c.casefold() for c in table.columns]
    return names.index(name) if name in names else None


def _topic_policy(topic: str, materiality: str, evidence: str, disposition: str) -> list[Finding]:
    found: list[Finding] = []
    if (
        materiality == "High"
        and evidence in ("Missing", "Conflicted")
        and disposition != "Gap only"
    ):
        found.append(
            Finding("screen_policy", f"{topic}: High with {evidence} evidence must be Gap only")
        )
    if disposition == "Immaterial" and evidence != "Sufficient":
        found.append(Finding("screen_policy", f"{topic}: Immaterial needs Sufficient evidence"))
    return found


def _screen_policy(h: Handoff, rules: Rules) -> list[Finding]:
    """High with Missing/Conflicted evidence is Gap only, Immaterial needs Sufficient evidence,
    and every screen family has a row. A Blocked Handoff may leave topics short or at `—` (like
    `min_rows`), so it is not held to these. Messages name ids and values, never source text."""
    table = h.tables.get(SCREEN_TABLE)
    at = [_column(table, n) for n in SCREEN_COLUMNS] if table else []
    if table is None or None in at or h.front_matter.get("qa_status") == "Blocked":
        return []  # column_missing is already reported for an absent column
    topic_at, family_at, materiality_at, evidence_at, disposition_at = (i or 0 for i in at)
    rows = [r for r in table.rows if len(r) == len(table.columns)]
    found: list[Finding] = []
    for r in rows:
        found += _topic_policy(r[topic_at], r[materiality_at], r[evidence_at], r[disposition_at])
    present = {r[family_at] for r in rows}
    return found + [
        Finding("screen_policy", f"no screen topic row for the family {f!r}")
        for f in rules.scales["screen_family"]
        if f not in present
    ]


def _run_depth(run: Path | None) -> str | None:
    """The approved depth in the run's state; None without a run, a state file or an approval.

    A state file that exists but cannot be read raises, as every other run-state reader does."""
    if run is None or not (run / state.STATE).is_file():
        return None
    depth = state.read(run)["depth"]
    return depth if isinstance(depth, str) else None


def _basis_depth(spec: TableSpec, h: Handoff, depth: str, rules: Rules) -> list[Finding]:
    table = h.tables.get(spec.id)
    labelled = any(c.name == "basis" and c.scale == "depth_basis" for c in spec.columns)
    at = _column(table, "basis") if table and labelled else None
    if table is None or at is None:
        return []
    want = DEPTH_BASIS[depth]
    return [
        Finding(
            "basis_depth", f"{spec.id} row {n} basis is {row[at]!r}; a {depth} run needs {want!r}"
        )
        for n, row in enumerate(table.rows, 1)
        if len(row) == len(table.columns) and row[at] != want and not rules.is_placeholder(row[at])
    ]


def _depth_findings(
    h: Handoff, contract: Contract, rules: Rules, run: Path | None
) -> list[Finding]:
    found = _screen_policy(h, rules) if any(t.id == SCREEN_TABLE for t in contract.tables) else []
    depth = _run_depth(run)
    for spec in contract.tables if depth else []:
        found += _basis_depth(spec, h, depth or "", rules)
    return found


def check(
    text: str, contract: Contract, rules: Rules, run: Path | None = None
) -> tuple[int, list[Finding]]:
    """Validate a Handoff; with `run`, also check each citation against the run's sources."""
    try:
        h = parse(text)
    except HandoffError as exc:
        return EXIT_MALFORMED, [Finding("not_a_handoff", str(exc))]
    findings = _front_matter(h, contract, rules) + _sections(h, rules) + _tags(h, contract)
    findings += _placeholders(h)
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
    findings += _depth_findings(h, contract, rules, run)
    findings += _module_findings(h, contract, rules, run)
    findings += _host_findings(h, contract, run, findings)
    if any(f.code == "run_error" for f in findings):
        return EXIT_USAGE, findings
    if any(f.code == "identity" for f in findings):
        return EXIT_IDENTITY, findings
    if findings:
        return EXIT_MALFORMED, findings
    if h.front_matter.get("qa_status") == "Blocked":
        return EXIT_BLOCKED, findings
    return EXIT_VALID, findings
