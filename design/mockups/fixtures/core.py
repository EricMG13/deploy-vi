"""Core of the fixture generator: numbers and formatting, the context (base data, Front Pages data, CAOS
runs, corpus), citations and the Handoff builder with table validation. Standard library only."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from decimal import ROUND_HALF_UP, Context, Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import spec as spec_mod

HERE = Path(__file__).resolve().parent
MOCKUPS = HERE.parent
DESIGN = MOCKUPS.parent
HANDOFF_DIR = DESIGN / "claude-design-handoff"
CAOS_DIR = HANDOFF_DIR / "data" / "caos-runs"
OUT_DIR = HANDOFF_DIR / "data" / "test"
CORPUS_DIR = Path(
    "/Users/ericguei/Documents/caos-databricks/qualification/czr-2026q2-full-credit-assessment/documents"
)

GAP = "—"
MCTX = Context(prec=38, rounding=ROUND_HALF_UP)
SYNTHETIC_SOURCE = "TEST DATA — invented for design, not a fact about {issuer}"


class FixtureError(Exception):
    """A fixture could not be built as written (bad input, unverifiable citation, failed validation)."""


# ------------------------------------------------------------------ numbers and formatting
def D(value: Any) -> Decimal:
    """Parse a figure the way the base data prints it: commas, a leading $, parentheses for negatives."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    t = str(value).strip().replace(",", "").replace("$", "")
    if t.startswith("(") and t.endswith(")"):
        t = "-" + t[1:-1]
    t = t.rstrip("x%")
    try:
        return Decimal(t)
    except InvalidOperation as exc:
        raise FixtureError(f"not a number: {value!r}") from exc


def q(d: Decimal, places: int) -> Decimal:
    """Round half up to `places` decimals."""
    return d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP, context=MCTX)


def plain(d: Decimal | int | str, places: int | None = None) -> str:
    """Plain decimal text: `-` sign, `.` point, no thousands separator, no negative zero."""
    v = D(d)
    if places is not None:
        v = q(v, places)
    s = format(v, "f")
    if "." in s and places is None:
        s = s.rstrip("0").rstrip(".")
    if s.startswith("-") and not s.strip("-0."):
        return s[1:] or "0"
    return s or "0"


def fx(d: Decimal | str, places: int = 2) -> str:
    return plain(d, places) + "x"


def fpct(d: Decimal | str, places: int = 1) -> str:
    return plain(d, places) + "%"


def fbps(d: Decimal | str) -> str:
    return plain(d, 0)


def ratio(num: Decimal | None, den: Decimal | None) -> Decimal | None:
    """num / den, or None when either is missing or the denominator is not positive."""
    if num is None or den is None or den <= 0:
        return None
    return MCTX.divide(num, den)


_ALLOWED = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.Add,
    ast.Sub,
)
_ALLOWED += (ast.Mult, ast.Div, ast.USub, ast.UAdd)


def safe_eval(expr: str, names: dict[str, Decimal] | None = None) -> Decimal:
    """Evaluate + - * / and parentheses over Decimals; nothing else is allowed."""
    names = names or {}
    tree = ast.parse(expr.strip(), mode="eval")

    def ev(node: ast.AST) -> Decimal:
        if not isinstance(node, _ALLOWED):
            raise FixtureError(f"expression not allowed: {expr!r}")
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float, str)):
                raise FixtureError(f"constant not allowed in {expr!r}")
            return Decimal(str(node.value))
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise FixtureError(f"unknown name {node.id!r} in {expr!r}")
            return names[node.id]
        if isinstance(node, ast.UnaryOp):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp):
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Add):
                return MCTX.add(a, b)
            if isinstance(node.op, ast.Sub):
                return MCTX.subtract(a, b)
            if isinstance(node.op, ast.Mult):
                return MCTX.multiply(a, b)
            if isinstance(node.op, ast.Div):
                return MCTX.divide(a, b)
        raise FixtureError(f"expression not allowed: {expr!r}")

    return ev(tree)


def compute(label: str, expr: str, places: int, unit: str = "", **vals: Any) -> tuple[Decimal, str]:
    """Evaluate `expr` over named inputs; return (value rounded half up, 'calc: …' string).

    The string carries the numeric expression, so `check_calc_string` can recompute it later:
    `calc: <label> = <expr with numbers> = <result><unit>`; unit is '', 'x', '%' or 'pp'.
    """
    names = {k: D(v) for k, v in vals.items()}
    value = q(safe_eval(expr, names), places)

    def sub(m: re.Match[str]) -> str:
        v = names[m.group(0)]
        return f"({plain(v)})" if v < 0 else plain(v)

    numeric = re.sub(r"[A-Za-z_]\w*", sub, expr)
    return value, f"calc: {label} = {numeric} = {plain(value, places)}{unit}"


_CALC_RE = re.compile(
    r"^calc: (?P<label>.+?) = (?P<expr>[-+*/().\d\s]+?) = (?P<res>-?\d+(?:\.\d+)?)(?P<unit>x|%|pp)?$"
)


def check_calc_string(s: str) -> str | None:
    """None when `s` is not a machine-checkable calc string or recomputes; else a failure message."""
    m = _CALC_RE.match(s.strip())
    if not m:
        return None
    res = Decimal(m.group("res"))
    places = -res.as_tuple().exponent if res.as_tuple().exponent < 0 else 0  # type: ignore[operator]
    try:
        got = q(safe_eval(m.group("expr")), places)
    except (FixtureError, SyntaxError, ZeroDivisionError, InvalidOperation) as exc:
        return f"calc does not evaluate: {s!r} ({exc})"
    return None if got == res else f"calc differs: {s!r} recomputes to {plain(got)}"


def slug(module_id: str) -> str:
    """'CP-1A' -> 'cp_1a'."""
    return module_id.lower().replace("-", "_")


# ------------------------------------------------------------------ markdown helpers
def load_js(path: Path, prefix: str) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.index(prefix) + len(prefix)
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


MARKER_RE = re.compile(r"\[(C\d+(?:\s*,\s*C\d+)*)\]")


def markers_in(text: str) -> list[int]:
    out: list[int] = []
    for m in MARKER_RE.finditer(text):
        out += [int(x) for x in re.findall(r"C(\d+)", m.group(1))]
    return out


def _norm_line(text: str) -> str:
    """Collapse whitespace and drop a trailing table pipe, so a table row matches with or without it."""
    return re.sub(r"\s+", " ", text.strip().rstrip("|").strip())


# ------------------------------------------------------------------ context
class Ctx:
    """Everything a content module reads: base data, Front Pages data, CAOS runs, corpus, spec."""

    def __init__(self) -> None:
        self.base = load_js(MOCKUPS / "shared" / "data.js", "window.RBOT_DATA = ")
        self.fp = load_js(MOCKUPS / "front-pages" / "fp-data.js", "window.RBOT_FP = ")
        self.spec = spec_mod.load_spec()
        self._lines: dict[str, list[str]] = {}
        self._sha: dict[str, str] | None = None
        self._caos: dict[tuple[str, str], tuple[str, list[dict]]] = {}
        self.built: dict[
            tuple[str, str], Any
        ] = {}  # (run_id, step) -> Handoff, filled in plan order
        self.models: dict[str, Any] = {}  # run_id -> ModelBuilder
        self.fits: dict[str, list] = {}  # run_id -> [FitResult]
        self.primary_runs: dict[str, bool] = {}  # run_id -> the run's Primary flag (set by the Run)
        dup = set(self.base["citations"]) & set(self.fp["citations"])
        if dup:
            raise FixtureError(f"base and Front Pages citation ids collide: {sorted(dup)[:5]}")

    def get(self, run_id: str, step: str) -> Any:
        """The handoff already built for an earlier plan step of this run (content modules read upstream here)."""
        try:
            return self.built[(run_id, step)]
        except KeyError:
            raise FixtureError(f"{step} has not been built yet for run {run_id}") from None

    # -- base / Front Pages data
    def data_citation(self, ref: str) -> dict:
        for src in (self.base["citations"], self.fp["citations"]):
            if ref in src:
                return src[ref]
        raise FixtureError(f"unknown RBOT_DATA / RBOT_FP citation id {ref!r}")

    def calc_record(self, ref: str) -> dict:
        for src in (self.base["calcs"], self.fp["calcs"]):
            if ref in src:
                return src[ref]
        raise FixtureError(f"unknown calculation id {ref!r}")

    def gap_record(self, ref: str) -> dict:
        for src in (self.base["gaps"], self.fp["gaps"]):
            if ref in src:
                return src[ref]
        raise FixtureError(f"unknown gap id {ref!r}")

    def figure(self, key: str) -> dict:
        for src in (self.base["figures"], self.fp["figures"]):
            if key in src:
                return src[key]
        raise FixtureError(f"unknown figure key {key!r}")

    def val(self, key: str) -> Decimal:
        """Numeric value of a figure (its `raw` when present, else `v`)."""
        f = self.figure(key)
        raw = f.get("raw") if f.get("raw") not in (None, "") else f.get("v")
        if raw in (None, "—"):
            raise FixtureError(f"figure {key!r} has no value")
        return D(raw)

    # -- corpus
    def corpus_lines(self, file: str) -> list[str]:
        if file not in self._lines:
            path = CORPUS_DIR / file
            if not path.is_file():
                raise FixtureError(f"corpus file not found: {path}")
            self._lines[file] = path.read_text(encoding="utf-8", errors="replace").split("\n")
        return self._lines[file]

    def verify_line(self, file: str, line: int, excerpt: str) -> None:
        lines = self.corpus_lines(file)
        if not 1 <= line <= len(lines):
            raise FixtureError(f"{file}: no line {line}")
        if excerpt not in lines[line - 1]:
            raise FixtureError(f"{file}:{line}: excerpt not found: {excerpt!r}")

    def anchor_line(self, file: str, line: int, excerpt: str) -> int:
        """Line of the corpus file that holds `excerpt`: the stated line when it does, else the nearest line
        that does (the base data's line numbers predate the current corpus text). Raises when none does."""
        lines = self.corpus_lines(file)
        if 1 <= line <= len(lines) and excerpt in lines[line - 1]:
            return line
        hits = [i + 1 for i, ln in enumerate(lines) if excerpt in ln]
        if not hits:
            want = _norm_line(excerpt)
            hits = [i + 1 for i, ln in enumerate(lines) if want and want in _norm_line(ln)]
        if not hits:
            raise FixtureError(f"{file}: excerpt not found anywhere: {excerpt!r}")
        return min(hits, key=lambda h: abs(h - line))

    def find_line(self, file: str, needle: str, nth: int = 0) -> int:
        """1-based line of the `nth` line containing `needle` (so content modules need not hard-code lines)."""
        hits = [i + 1 for i, ln in enumerate(self.corpus_lines(file)) if needle in ln]
        if len(hits) <= nth:
            raise FixtureError(
                f"{file}: needle {needle!r} has {len(hits)} hit(s), wanted index {nth}"
            )
        return hits[nth]

    def sha_to_file(self) -> dict[str, str]:
        if self._sha is None:
            self._sha = {}
            for p in sorted(CORPUS_DIR.iterdir()):
                if p.is_file():
                    self._sha[hashlib.sha256(p.read_bytes()).hexdigest()] = p.name
        return self._sha

    # -- CAOS runs
    def caos(self, folder: str, module: str) -> tuple[str, list[dict]]:
        """(markdown, citations) of one real CAOS module output; each citation gains its corpus `source`."""
        key = (folder, module)
        if key not in self._caos:
            base = CAOS_DIR / folder
            md_path, cit_path = base / f"{module}.md", base / f"{module}.citations.json"
            if not md_path.is_file() or not cit_path.is_file():
                raise FixtureError(f"no CAOS output {folder}/{module}")
            cits = json.loads(cit_path.read_text(encoding="utf-8"))
            sha = self.sha_to_file()
            for c in cits:
                if c["document_sha256"] not in sha:
                    raise FixtureError(
                        f"{folder}/{module} marker {c['marker']}: document not in the corpus"
                    )
                c["source"] = sha[c["document_sha256"]]
            self._caos[key] = (md_path.read_text(encoding="utf-8"), cits)
        return self._caos[key]

    def caos_table(self, folder: str, module: str, table_id: str) -> list[dict]:
        """Rows of a CAOS register tagged `<!-- table-id: … -->`, as dicts keyed by header."""
        md, _ = self.caos(folder, module)
        tag = f"<!-- table-id: {table_id} -->"
        pos = md.find(tag)
        if pos < 0:
            raise FixtureError(f"{folder}/{module}: no table {table_id}")
        tables = spec_mod.md_tables(md[pos + len(tag) :])
        if not tables:
            raise FixtureError(f"{folder}/{module}: {table_id} has no table")
        t = tables[0]
        return [dict(zip(t["header"], r, strict=False)) for r in t["rows"]]

    def caos_table_by_heading(self, folder: str, module: str, heading: str) -> list[dict]:
        md, _ = self.caos(folder, module)
        for t in spec_mod.md_tables(md):
            if heading in t["heading"]:
                return [dict(zip(t["header"], r, strict=False)) for r in t["rows"]]
        raise FixtureError(f"{folder}/{module}: no table under heading containing {heading!r}")


_CTX: Ctx | None = None


def load_ctx() -> Ctx:
    """The shared context (built once per process)."""
    global _CTX
    if _CTX is None:
        _CTX = Ctx()
    return _CTX


def cell_problem(spec: dict, col: dict, v: str) -> str | None:
    """What is wrong with the stored text `v` for spec column `col` (None when it is fine)."""
    name = col["name"]
    scale = spec["scales"].get(col["scale"]) if col["scale"] else None
    if scale is not None:
        return None if (v == GAP or v in scale) else f"{v!r} is not in scale {col['scale']} {scale}"
    if v == GAP:
        return None
    if v.lower() in spec["rules"]["placeholders"]:
        return f"placeholder text {v!r}; use {GAP} for a gap"
    if name.endswith("_x") and not _NUM_X_RE.match(v):
        return f"{v!r} is not a multiple like 4.20x"
    if name.endswith("_pct") and not _NUM_PCT_RE.match(v):
        return f"{v!r} is not a percentage like 12.5%"
    if name.endswith("_bps") and not _INT_RE.match(v):
        return f"{v!r} is not an integer basis-point count"
    if name.endswith("_date") and not _DATE_RE.match(v):
        return f"{v!r} is not an ISO date"
    if _BAD_NUMBER_RE.match(v):
        return f"{v!r} is not a plain decimal (no thousands separator or brackets)"
    if name == "cite" and not (markers_in(v) or "calc:" in v):
        return f"cite must hold [C<n>] markers or 'calc: …', got {v!r}"
    return None


GATE_NOT_MET = "Gate not met"
GATE_TABLES = ("cp4c.claims_register", "cp4c.ev_scenarios", "cp4c.recoveries", "cp4c.paths")


def distress_gate_not_met(tables: dict[str, dict]) -> bool:
    """True when CP-4C's distress gate Overall row reads Not met (interfaces §2.17)."""
    gate = tables.get("cp4c.distress_gate")
    if not gate:
        return False
    cols = gate["columns"]
    rows = [dict(zip(cols, r, strict=True)) for r in gate["rows"]]
    overall = [r for r in rows if r["trigger"].lower().startswith("overall")]
    return bool(overall) and overall[-1]["status"] == "Not met"


def gate_statement(table_id: str, col: dict, v: str) -> bool:
    """The one allowed exception to cell formats: `Gate not met` in a critical cell of a CP-4C register table (the
    caller has already established that the distress gate is Not met)."""
    return table_id in GATE_TABLES and bool(col["critical"]) and v == GATE_NOT_MET


def table_problems(
    spec: dict,
    module_id: str,
    table_id: str,
    table: dict,
    blocked: bool,
    gate_not_met: bool = False,
) -> list[str]:
    """Shape, scale, format, critical-cell and row-count problems of one stored table.

    One exception (interfaces §2.17): when the module's distress gate is Not met, the critical cells of the four CP-4C
    register tables may hold the literal `Gate not met`, whatever the column's scale or `_pct`/figure format."""
    ts = spec["tables"][table_id]
    names = [c["name"] for c in ts["columns"]]
    out: list[str] = []
    if table.get("columns") != names:
        return [
            f"{module_id} {table_id}: columns {table.get('columns')} differ from the spec {names}"
        ]
    if not blocked and len(table["rows"]) < ts["min_rows"]:
        out.append(f"{module_id} {table_id}: {len(table['rows'])} rows, minimum {ts['min_rows']}")
    for i, row in enumerate(table["rows"]):
        if len(row) != len(names):
            out.append(f"{module_id} {table_id} row {i}: {len(row)} cells, expected {len(names)}")
            continue
        for col, cell in zip(ts["columns"], row, strict=True):
            if not isinstance(cell, str):
                out.append(f"{module_id} {table_id} row {i} {col['name']}: cell is not text")
                continue
            if gate_not_met and gate_statement(table_id, col, cell):
                continue
            bad = cell_problem(spec, col, cell)
            if bad:
                out.append(f"{module_id} {table_id} row {i} {col['name']}: {bad}")
            if col["critical"] and cell == GAP and not blocked:
                out.append(f"{module_id} {table_id} row {i}: critical {col['name']} is blank")
    return out


# ------------------------------------------------------------------ handoff
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_NUM_X_RE = re.compile(r"^-?\d+(\.\d+)?x$")
_NUM_PCT_RE = re.compile(r"^-?\d+(\.\d+)?%$")
_INT_RE = re.compile(r"^-?\d+$")
_BAD_NUMBER_RE = re.compile(r"^\(?[-+]?\d{1,3}(,\d{3})+(\.\d+)?\)?$|^\([\d.]+\)$")
_QA = ("Pass", "Restricted", "Blocked")


class Handoff:
    """One module's (or host step's) output: front matter, analysis, tables, gaps, citations."""

    def __init__(
        self,
        ctx: Ctx,
        module_id: str,
        issuer_id: str,
        run_id: str,
        analysis_date: str,
        inputs: list[str] | tuple[str, ...] = (),
        fixture_file: str | None = None,
    ) -> None:
        if module_id not in ctx.spec["module_tables"]:
            raise FixtureError(f"unknown module id {module_id!r}")
        self.ctx = ctx
        self.module_id = module_id
        self.issuer_id = issuer_id
        self.run_id = run_id
        self.analysis_date = analysis_date
        self.inputs = list(inputs)
        self.fixture_file = fixture_file or f"{issuer_id.lower()}/{slug(module_id)}.py"
        self.qa_status = "Pass"
        self.analysis_md = ""
        self.gaps_md = ""
        self.tables: dict[str, dict] = {}
        self.citations: list[dict] = []
        self.meta: dict[str, Any] = {}
        self._index: dict[tuple, str] = {}
        self._used: set[int] = set()

    # -- citations
    def _add(self, row: dict) -> str:
        key = (row["source"], row["locator"], row["excerpt"], row["synthetic"])
        if key not in self._index:
            n = len(self.citations) + 1
            self._index[key] = f"[C{n}]"
            self.citations.append({"id": f"C{n}", **row})
        return self._index[key]

    def cite_data(self, ref: str) -> str:
        """A base-data / Front-Pages citation id (C… or S…) -> '[C<n>]' of this handoff."""
        c = self.ctx.data_citation(ref)
        if c.get("synthetic"):
            return self.cite_synthetic(
                f"{ref}",
                f"Synthetic Test CLO I design data, mock row {ref} ({c['file']} line {c['line']}): "
                f"{c['excerpt'][:140]}",
                "Test CLO I Ltd",
                file="shared/data.js",
                origin=f"data:{ref}",
            )
        line = self.ctx.anchor_line(c["file"], c["line"], c["excerpt"])
        return self._add(
            {
                "source": c["file"],
                "locator": re.sub(r"line \d+", f"line {line}", c["locator"]),
                "excerpt": c["excerpt"],
                "anchored": True,
                "synthetic": False,
                "origin": f"data:{ref}",
            }
        )

    def cite_fig(self, key: str) -> str:
        """The citation behind a base/FP figure key (a calculated figure returns its 'calc:' string)."""
        f = self.ctx.figure(key)
        ref = f.get("ref")
        if not ref:
            raise FixtureError(f"figure {key!r} has no citation")
        if ref.startswith("K"):
            return self.cite_calc(ref)
        if ref.startswith("G"):
            raise FixtureError(f"figure {key!r} is a gap ({ref})")
        return self.cite_data(ref)

    def cite_calc(self, ref: str) -> str:
        """A base/FP calculation id (K…) -> 'calc: <formula>' with its inputs cited and re-marked."""
        rec = self.ctx.calc_record(ref)
        formula = rec["formula"]
        if rec.get("synthetic"):
            formula = re.sub(r"\[(?:K|S)\d+\]", "", formula)

        def sub(m: re.Match[str]) -> str:
            rid = m.group(1)
            if rid.startswith("C") or rid.startswith("S"):
                return self.cite_data(rid)
            return self.cite_calc(rid).removeprefix("calc: ")

        out = re.sub(r"\[((?:C|S|K)\d+)\]", sub, formula)
        for inp in rec.get("inputs", []):
            if inp.startswith("C"):
                self.cite_data(inp)
        return f"calc: {rec['label']} = {out} = {rec['value']}"

    def cite_caos(self, folder: str, module: str, marker: int) -> str:
        _, cits = self.ctx.caos(folder, module)
        hit = next((c for c in cits if c["marker"] == marker), None)
        if hit is None:
            raise FixtureError(f"CAOS {folder}/{module}: no marker {marker}")
        text = "\n".join(self.ctx.corpus_lines(hit["source"]))
        if hit["line_text"] not in text:
            raise FixtureError(
                f"CAOS {folder}/{module} marker {marker}: line text not in {hit['source']}"
            )
        return self._add(
            {
                "source": hit["source"],
                "locator": f"p.{hit['page']}",
                "excerpt": hit["line_text"],
                "anchored": True,
                "synthetic": False,
                "origin": f"caos:{folder}/{module}#{marker}",
            }
        )

    def cite_doc(self, file: str, line: int, excerpt: str) -> str:
        self.ctx.verify_line(file, line, excerpt)
        return self._add(
            {
                "source": file,
                "locator": f"line {line}",
                "excerpt": excerpt,
                "anchored": True,
                "synthetic": False,
                "origin": f"doc:{file}:{line}",
            }
        )

    def cite_doc_find(
        self, file: str, needle: str, nth: int = 0, excerpt: str | None = None
    ) -> str:
        """cite_doc on the `nth` line containing `needle`; the excerpt is `needle` unless given."""
        line = self.ctx.find_line(file, needle, nth)
        return self.cite_doc(file, line, excerpt or needle)

    def cite_synthetic(
        self,
        key: str,
        rationale: str,
        issuer: str,
        file: str | None = None,
        origin: str | None = None,
    ) -> str:
        if "\n" in rationale or not rationale.strip():
            raise FixtureError(f"synthetic citation {key!r}: rationale must be one sentence")
        return self._add(
            {
                "source": SYNTHETIC_SOURCE.format(issuer=issuer),
                "locator": f"fixtures/{file or self.fixture_file}#{key}",
                "excerpt": rationale.strip(),
                "anchored": True,
                "synthetic": True,
                "origin": origin or f"synthetic:{self.fixture_file}#{key}",
            }
        )

    def cite_from_source(self, src: dict) -> str:
        """Mechanical copy of a CP-1 citation into a host handoff (origin keeps the module:id namespace)."""
        synthetic = src["source"].startswith("TEST DATA")
        return self._add(
            {
                "source": src["source"],
                "locator": src["locator"],
                "excerpt": src["excerpt"],
                "anchored": True,
                "synthetic": synthetic,
                "origin": f"{src['module']}:{src['citation_id']}",
            }
        )

    @staticmethod
    def calc(formula: str) -> str:
        """`'calc: …'` for a figure derived from cited figures (use `compute()` for a recomputable string)."""
        return formula if formula.startswith("calc:") else f"calc: {formula}"

    def citation(self, marker: str) -> dict:
        """The citation row behind '[C12]'."""
        m = re.fullmatch(r"\[?C(\d+)\]?", marker.strip())
        if not m or not 1 <= int(m.group(1)) <= len(self.citations):
            raise FixtureError(f"{self.module_id}: marker {marker!r} does not resolve")
        return self.citations[int(m.group(1)) - 1]

    # -- content
    def qa(self, status: str) -> Handoff:
        if status not in _QA:
            raise FixtureError(f"qa_status must be one of {_QA}")
        self.qa_status = status
        return self

    def analysis(self, md: str) -> Handoff:
        self.analysis_md = md.strip()
        return self

    def gaps(self, md: str) -> Handoff:
        self.gaps_md = md.strip()
        return self

    def table(self, table_id: str, rows: list) -> Handoff:
        """Store `rows` (dicts keyed by column, or lists in column order) after checking every column."""
        ts = self.ctx.spec["tables"].get(table_id)
        if ts is None:
            raise FixtureError(f"{self.module_id}: unknown table {table_id!r}")
        if self.module_id not in ts["owners"]:
            raise FixtureError(f"{self.module_id}: table {table_id} belongs to {ts['owners']}")
        names = [c["name"] for c in ts["columns"]]
        out: list[list[str]] = []
        for i, row in enumerate(rows):
            if isinstance(row, dict):
                extra = set(row) - set(names)
                if extra:
                    raise FixtureError(f"{table_id} row {i}: unknown columns {sorted(extra)}")
                cells = [row.get(n) for n in names]
            else:
                if len(row) != len(names):
                    raise FixtureError(
                        f"{table_id} row {i}: {len(row)} cells, expected {len(names)}"
                    )
                cells = list(row)
            out.append(
                [self._cell(table_id, i, c, v) for c, v in zip(ts["columns"], cells, strict=True)]
            )
        self.tables[table_id] = {"columns": names, "rows": out}
        return self

    def rows(self, table_id: str) -> list[dict]:
        t = self.tables[table_id]
        return [dict(zip(t["columns"], r, strict=True)) for r in t["rows"]]

    def _cell(self, table_id: str, i: int, col: dict, value: Any) -> str:
        where = f"{self.module_id} {table_id} row {i} column {col['name']}"
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return GAP
        v = (
            plain(value)
            if isinstance(value, (Decimal, int)) and not isinstance(value, bool)
            else value
        )
        if not isinstance(v, str):
            raise FixtureError(
                f"{where}: cell must be text or a number, got {type(value).__name__}"
            )
        v = v.strip()
        gate_ok = gate_statement(table_id, col, v) and distress_gate_not_met(self.tables)
        bad = None if gate_ok else cell_problem(self.ctx.spec, col, v)
        if bad:
            raise FixtureError(f"{where}: {bad}")
        for m in markers_in(v):
            self.citation(f"C{m}")
            self._used.add(m)
        return v

    # -- finish
    def required_tables(self) -> list[str]:
        return list(self.ctx.spec["module_tables"][self.module_id])

    def problems(self) -> list[str]:
        """Everything wrong with this handoff as it stands (empty when it passes validation)."""
        out: list[str] = []
        blocked = self.qa_status == "Blocked"
        for tid in self.required_tables():
            if tid not in self.tables:
                out.append(f"{self.module_id}: missing table {tid}")
            else:
                out += table_problems(
                    self.ctx.spec,
                    self.module_id,
                    tid,
                    self.tables[tid],
                    blocked,
                    distress_gate_not_met(self.tables),
                )
        if not self.analysis_md:
            out.append(f"{self.module_id}: empty analysis")
        for m in markers_in(self.analysis_md) + markers_in(self.gaps_md):
            if not 1 <= m <= len(self.citations):
                out.append(f"{self.module_id}: [C{m}] in text does not resolve")
            self._used.add(m)
        for cell_str in self._all_cells():
            msg = check_calc_string(cell_str)
            if msg:
                out.append(f"{self.module_id}: {msg}")
        unused = [c["id"] for c in self.citations if int(c["id"][1:]) not in self._used]
        if unused:
            out.append(f"{self.module_id}: citations never cited: {unused}")
        return out

    def _all_cells(self) -> list[str]:
        cells = [c for t in self.tables.values() for r in t["rows"] for c in r if "calc:" in c]
        return cells

    def to_json(self) -> dict:
        problems = self.problems()
        if problems:
            raise FixtureError(
                "; ".join(problems[:12])
                + (f" (+{len(problems) - 12} more)" if len(problems) > 12 else "")
            )
        body = {
            "qa_status": self.qa_status,
            "status": "accepted" if self.qa_status != "Blocked" else "blocked",
            "front_matter": {
                "module_id": self.module_id,
                "run_id": self.run_id,
                "issuer_id": self.issuer_id,
                "analysis_date": self.analysis_date,
                "qa_status": self.qa_status,
                "inputs": self.inputs,
            },
            "analysis_md": self.analysis_md,
            "gaps_md": self.gaps_md,
            "tables": self.tables,
            "citations": self.citations,
        }
        sha = hashlib.sha256(
            json.dumps(body, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        return {"sha256": sha, **body}
