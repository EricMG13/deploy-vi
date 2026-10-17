"""Parse the interfaces spec (Markdown) and rules.json into the lookups the generator needs.

Nothing here is retyped from the spec: table catalogue (§2, §3), Front Page blocks (§4), Pathway plans (§5)
and the chart map (§11.4) are read from `inputs/interfaces-b4f39c3.md`; scales from `inputs/rules-b4f39c3.json`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
INTERFACES = HERE / "inputs" / "interfaces-b4f39c3.md"
RULES = HERE / "inputs" / "rules-b4f39c3.json"

FRONT_PAGE_TITLES = {
    "credit_snapshot": "Credit Snapshot",
    "earnings_update": "Earnings Update",
    "relative_value": "Relative Value",
    "covenant_refinancing": "Covenant & Refinancing",
    "distressed_restructuring": "Distressed",
    "portfolio_decision": "Portfolio Decision",
}


class SpecError(Exception):
    """The spec Markdown no longer has the shape the parser expects."""


def split_row(line: str) -> list[str]:
    """Split a Markdown table row on unescaped pipes outside backticks."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells: list[str] = []
    cur: list[str] = []
    in_code = False
    for ch in body:
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur).strip())
    return cells


def md_tables(text: str) -> list[dict]:
    """Every pipe table in `text`: {heading, header, rows, line}. `heading` is the last Markdown heading."""
    out: list[dict] = []
    heading = ""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"#{1,6} ", line):
            heading = line.lstrip("#").strip()
        if (
            line.startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\|[\s:|-]+\|?\s*$", lines[i + 1])
        ):
            header = split_row(line)
            rows: list[list[str]] = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            out.append({"heading": heading, "header": header, "rows": rows, "line": i + 1})
            i = j
            continue
        i += 1
    return out


def _tokens(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def parse_column(token: str) -> dict:
    """`name*` / `name* (scale)` / `name` -> {name, critical, scale}."""
    m = re.match(r"^([a-z0-9_]+)(\*)?\s*(?:\(([a-z0-9_]+)\))?$", token.strip())
    if not m:
        raise SpecError(f"unreadable column token: {token!r}")
    return {"name": m.group(1), "critical": bool(m.group(2)), "scale": m.group(3)}


def _section_module(heading: str) -> str | None:
    """'2.7 CP-2' -> 'CP-2'; '3.1 `RUN_BRIEF` -> ...' -> 'RUN_BRIEF'."""
    m = re.match(r"^[23]\.\d+\s+`?([A-Z][A-Z0-9_-]*)`?", heading)
    return m.group(1) if m else None


def parse_tables(md: str) -> tuple[dict, dict]:
    """Table catalogue from §2 and §3 -> ({table_id: spec}, {module: [table_id]})."""
    catalogue: dict[str, dict] = {}
    by_module: dict[str, list[str]] = {}
    for t in md_tables(md):
        module = _section_module(t["heading"])
        head = [h.strip("` ") for h in t["header"]]
        if module is None or not head or head[0] != "id":
            continue
        is_catalogue = head[:3] == ["id", "purpose", "columns"]
        is_host = head[:2] == ["id", "columns"]
        if not (is_catalogue or is_host):
            continue
        sec_no = float(re.match(r"^(\d+\.\d+)", t["heading"]).group(1))  # type: ignore[union-attr]
        for row in t["rows"]:
            ids = _tokens(row[0])
            if not ids:
                continue
            table_id = ids[0]
            col_cell = row[2] if is_catalogue else row[1]
            min_cell = row[3] if is_catalogue else row[2]
            tokens = _tokens(col_cell)
            if tokens:
                columns = [parse_column(x) for x in tokens]
            elif "identical" in col_cell and table_id in catalogue:
                columns = catalogue[table_id]["columns"]
            else:
                raise SpecError(f"{table_id}: no columns in {col_cell!r}")
            min_rows = int(re.match(r"\d+", min_cell).group(0))  # type: ignore[union-attr]
            by_module.setdefault(module, []).append(table_id)
            if table_id not in catalogue:
                catalogue[table_id] = {
                    "id": table_id,
                    "columns": columns,
                    "min_rows": min_rows,
                    "owner": module,
                    "owners": [module],
                    "section": sec_no,
                    "host": is_host,
                }
            else:
                catalogue[table_id]["owners"].append(module)
    return catalogue, by_module


_COND_RULES = [
    (r"unsecured rows hidden", "unsecured_present"),
    (r"PF interest rows shown", "pf_ltm"),
    (r"projected series only", "projection"),
    (r"HY block hidden", "rows_present"),
    (r"rows present", "rows_present"),
    (r"talk rows when", "primary"),
    (r"CR Score when", "primary"),
    (r"`primary`\s*=\s*Yes", "primary"),
    (r"portfolios attached", "portfolios"),
    (r"Prior Case accepted", "prior_case"),
    (r"gate Met or Unclear", "gate_met"),
]


def _condition_key(text: str) -> str:
    t = text.strip()
    if t in ("—", "-", ""):
        return "always"
    for pat, key in _COND_RULES:
        if re.search(pat, t):
            return key
    raise SpecError(f"unmapped Front Page condition: {text!r}")


def parse_front_pages(md: str) -> dict:
    """§4: {front_page_id: {title, blocks: [{n, id, title, tables, owner, feeders, condition, condition_text}]}}."""
    pages: dict[str, dict] = {}
    for t in md_tables(md):
        m = re.match(r"^(4\.\d+)\s+`([a-z_]+)`\s+—\s+\"([^\"]+)\"", t["heading"])
        if not m or t["header"][0] != "#":
            continue
        fp_id = m.group(2)
        blocks = []
        for row in t["rows"]:
            n = int(row[0])
            blocks.append(
                {
                    "n": n,
                    "id": f"{fp_id}.{n}",
                    "title": row[1],
                    "tables": [x for x in _tokens(row[2]) if "." in x],
                    "owner": row[3],
                    "feeders": row[4],
                    "condition": _condition_key(row[5]),
                    "condition_text": row[5],
                }
            )
        pages[fp_id] = {"id": fp_id, "title": m.group(3), "blocks": blocks}
    if len(pages) != 6:
        raise SpecError(f"expected six Front Pages, found {len(pages)}")
    return pages


def parse_pathways(md: str) -> dict:
    """§5: the JSON objects in the fenced block -> {pathway_id: {...}}."""
    start = md.index("## 5. Pathways")
    end = md.index("## 6. Model")
    section = md[start:end]
    fence = re.search(r"```json\n(.*?)```", section, re.S)
    if not fence:
        raise SpecError("§5 has no json fence")
    dec = json.JSONDecoder()
    body = fence.group(1)
    pos, out = 0, {}
    while pos < len(body):
        while pos < len(body) and body[pos].isspace():
            pos += 1
        if pos >= len(body):
            break
        obj, pos = dec.raw_decode(body, pos)
        out[obj["id"]] = obj
    return out


def parse_chart_map(md: str) -> tuple[dict, dict]:
    """§11.4: ({chart_id: {kind_text, reads, where_text, origin_text}}, {front_page_id: [chart_id]})."""
    charts: dict[str, dict] = {}
    for t in md_tables(md):
        if t["header"][:3] != ["chart_id", "caos figure", "Kind"]:
            continue
        for row in t["rows"]:
            ids = _tokens(row[0])
            reads: dict[str, list[str]] = {}
            current: str | None = None
            for tok in _tokens(row[3]):
                if "." in tok or tok == "prior/diff.json":
                    current = tok
                    reads.setdefault(current, [])
                elif current is not None:
                    reads[current].append(tok)
            for cid in ids:
                charts[cid] = {
                    "id": cid,
                    "kind_text": row[2],
                    "reads": reads,
                    "where_text": row[4],
                    "origin_text": row[5],
                }
    sets: dict[str, list[str]] = {}
    names = {
        "Credit Snapshot": "credit_snapshot",
        "Earnings Update": "earnings_update",
        "Relative Value": "relative_value",
        "Covenant & Refinancing": "covenant_refinancing",
        "Distressed": "distressed_restructuring",
        "Portfolio Decision": "portfolio_decision",
    }
    m = re.search(r"Front Page chart sets:(.*?)\n", md, re.S)
    if not m:
        raise SpecError("§11.4 has no Front Page chart sets line")
    for part in m.group(1).split(";"):
        lead, _, ids = part.partition("→")
        key = lead.strip()
        if key not in names:
            raise SpecError(f"unknown Front Page in chart sets: {key!r}")
        sets[names[key]] = [x for x in _tokens(ids) if x.startswith("chart.")]
    return charts, sets


def chart_block(where_text: str, fp_id: str) -> int | None:
    """The Front Page block number a chart sits in, from its 'Where' cell (None when it names none)."""
    title = FRONT_PAGE_TITLES[fp_id]
    m = re.search(re.escape(title) + r"\s+(?:block\s+)?(\d+)", where_text)
    return int(m.group(1)) if m else None


def load_spec() -> dict:
    md = INTERFACES.read_text(encoding="utf-8")
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    tables, by_module = parse_tables(md)
    charts, chart_sets = parse_chart_map(md)
    return {
        "tables": tables,
        "module_tables": by_module,
        "front_pages": parse_front_pages(md),
        "pathways": parse_pathways(md),
        "charts": charts,
        "chart_sets": chart_sets,
        "scales": rules["scales"],
        "rules": rules,
    }


# Source tables a chart can draw without (the strip is historical-only when no PROJECTION ran, e.g. Earnings Update).
OPTIONAL_READS = {"chart.model_strip": {"model.projection_summary"}}


def chart_tables(chart: dict, tables: dict, owners_present: set[str]) -> list[str] | None:
    """The tables a chart needs in a run whose steps are `owners_present`; None when the chart does not apply.

    A chart applies when every non-optional source table has a producer in the run (FIXTURES §5)."""
    need = []
    for tid in chart["reads"]:
        owners = (
            tables[tid]["owners"] if tid in tables else ["PRIOR_CASE"]
        )  # prior/diff.json is not a table
        has = any(o in owners_present for o in owners)
        if not has:
            if tid in OPTIONAL_READS.get(chart["id"], set()):
                continue
            return None
        need.append(tid)
    return need
