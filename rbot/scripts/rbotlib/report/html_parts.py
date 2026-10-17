"""The page's small parts: element builder, citation markup, tables, chips, scale badges, JSON.

Every text and attribute value goes through `html.escape`; figures print as served
(`format_number` only adds thousands separators to the money columns a caller names).
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from html import escape
from typing import Any

from rbotlib.report.blocks import GAP, format_number

Record = dict[str, Any]
TOKEN = re.compile(r"\[(C\d+)\]|calc:\s*((?:[^;()\[.]|\.(?=\S)|\([^()]*\))*)")
NUMBER = re.compile(r"^\(?-?[\d,]+(\.\d+)?\)?(x|%|bp|bps)?$")
SCALE = re.compile(r"^(?:V)?(\d) - (.+)$")
SCALE_COLUMNS = dict.fromkeys(("recommendation", "recommendation_cap", "cap", "final"), "rec")
SCALE_COLUMNS |= {"uncapped": "rec", "credit_score": "score", "valuation": "val", "verdict": "val"}
STATUS_WORDS = {"pass", "restricted", "watch", "blocked", "breaches", "breach", "fits"}
STATUS_CLASS = {"breaches": "breach", "fits": "pass", "failed": "na", "skipped": "na"}
STATUS_LABEL = {"restricted": "With limitations"}


def h(tag: str, body: object = "", **attrs: object) -> str:
    """`<tag attrs>body</tag>`; `cls` is `class`, `data_x` is `data-x`, empty values are left out.

    `body` is HTML already; attribute values are escaped here.
    """
    named = {("class" if k == "cls" else k.replace("_", "-")): v for k, v in attrs.items() if v}
    shown = "".join(f' {k}="{escape(str(v))}"' for k, v in named.items())
    return f"<{tag}{shown}>{body}</{tag}>"


def cite_html(
    text: str,
    module: str,
    citations: Mapping[str, Record],
    refs: dict[str, list[str]] | None = None,
) -> str:
    """Escape `text`, link `[C<n>]` to its Evidence row and wrap `calc: ...` in an abbr."""
    out, pos = [], 0
    for found in TOKEN.finditer(text):
        out.append(escape(text[pos : found.start()]))
        cid = found.group(1)
        if cid is None:
            out.append(h("abbr", "calc", cls="calc", title=found.group(2).strip()))
        elif cid not in citations:
            out.append(h("span", f"[{cid}]", cls="cite--unknown"))
        else:
            key = f"{module}:{cid}"
            seen = refs.setdefault(key, []) if refs is not None else []
            seen.append(f"ref-{module}-{cid}-{len(seen) + 1}")
            excerpt = str(citations[cid].get("excerpt", ""))
            out.append(
                h(
                    "a",
                    f"[{cid}]",
                    cls="cite",
                    id=seen[-1],
                    href=f"#ev-{module}-{cid}",
                    data_ref=key,
                    title=excerpt,
                )
            )
        pos = found.end()
    return "".join(out) + escape(text[pos:])


def status_html(word: str, reason: str | None = None) -> str:
    """The status chip: Restricted reads "With limitations", failed and skipped are `na`."""
    low = word.lower()
    css = STATUS_CLASS.get(low, low if low in STATUS_WORDS else "na")
    shown = escape(STATUS_LABEL.get(low, word))
    return h("span", shown, cls=f"status status--{css}", data_status=word, title=reason)


def scale_html(kind: str, value: str) -> str:
    """A house scale cell `3 - MW`, `V2 - Attractive`, `4 - Weak`; anything else is plain text."""
    found = SCALE.match(value.strip())
    if found is None:
        return escape(value)
    pos, word = found.groups()
    shown = escape(value.strip())
    return h("span", shown, cls="scale", data_scale=kind, data_pos=pos, data_word=word)


def dir_html(word: str) -> str:
    low = word.lower()
    tone = "down" if re.search("deteriorating|negative", low) else "flat"
    tone = "up" if re.search("improving|positive", low) else tone
    return h("span", escape(word), cls=f"dir dir--{tone}")


def gap_html(reason: str | None = None) -> str:
    return h("span", "n/a", cls="gap", title=reason)


@dataclass(frozen=True)
class TableOptions:
    """Optional parts of a table: money columns, cell Datums, a citation linker, column kinds."""

    money_columns: Sequence[str] = ()
    datums: Mapping[tuple[int, int], Record] | None = None
    cite: Callable[[str], str] | None = None
    col_kinds: Sequence[str] | None = None


def _plain(column: str, text: str, money: bool, cite: Callable[[str], str]) -> tuple[str, bool]:
    """A plain cell's inner HTML and whether it is a number."""
    shown, kind = text.strip(), SCALE_COLUMNS.get(column)
    if shown in (GAP, ""):
        return gap_html(), False
    if kind and SCALE.match(shown):
        return scale_html("val" if shown.startswith("V") else kind, shown), False
    if column in ("verdict", "fit_verdict") and shown.lower() in STATUS_WORDS:
        return status_html(shown), False
    if NUMBER.match(shown):
        return escape(format_number(shown, money)), True
    return cite(text), False


def _td(datum: Record | None, name: str, text: str, opts: TableOptions) -> tuple[str, bool]:
    money = name in opts.money_columns
    if datum is None:
        inner, num = _plain(name, text, money, opts.cite or escape)
        return h("td", inner, cls="num" if num else ""), num
    num = datum.get("v") is not None
    inner = escape(format_number(str(datum["v"]), money)) if num else gap_html(datum["reason"])
    raw = json.dumps(datum, sort_keys=True)
    return h("td", inner, cls="num" if num else "", data_datum=raw), num


def table_html(
    columns: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    module: str,
    caption: str,
    options: TableOptions | None = None,
) -> str:
    """`table.dt`: `.num` on numeric cells, `td[data-datum]` where a Datum exists, gaps as n/a."""
    opts = options or TableOptions()
    numeric, body = [False] * len(columns), []
    for r, row in enumerate(rows):
        cells = []
        for c, name in enumerate(columns):
            text = row[c] if c < len(row) else GAP
            cell, num = _td((opts.datums or {}).get((r, c)), name, text, opts)
            numeric[c] = numeric[c] or num
            cells.append(cell)
        body.append(h("tr", "".join(cells)))
    kinds, head = opts.col_kinds or [""] * len(columns), []
    for i, name in enumerate(columns):
        label = name.replace("_", " ")
        head.append(
            h(
                "th",
                escape(label[:1].upper() + label[1:]),
                scope="col",
                cls="num" if numeric[i] else "",
                data_col_kind=kinds[i],
            )
        )
    parts = h("caption", escape(caption), cls="vh") + h("thead", h("tr", "".join(head)))
    table = h("table", parts + h("tbody", "".join(body)), cls="dt", data_module=module)
    return h("div", table, cls="table-scroll")


def embed_json(doc: Record) -> str:
    """The run document in a `script#rbot-run`; `</` and U+2028/2029 can never end the script."""
    text = json.dumps(doc, ensure_ascii=False, sort_keys=True)
    text = text.replace("</", "<\\/").replace("<!--", "\\u003c!--")
    text = text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return f'<script type="application/json" id="rbot-run">{text}</script>'
