"""Small readers shared by content modules: numbers out of corpus table rows, CAOS marker remapping, and a table builder."""

from __future__ import annotations

import re
from decimal import Decimal

from core import GAP, Ctx, D, FixtureError, Handoff


def cell_number(s: str) -> Decimal | None:
    """'$4,049' -> 4049; '(285)' -> -285; '19.9%' -> 19.9; '—' / '$—' -> None."""
    t = s.strip().replace("$", "").replace(",", "").rstrip("%")
    if t in ("", "—", "-", "N/A"):
        return None
    t = re.sub(r"\s*pts?$", "", t)
    return D(t)


def doc_row(
    ctx: Ctx, file: str, needle: str, nth: int = 0
) -> tuple[int, str, list[Decimal | None]]:
    """(line, line text, numbers) of the `nth` corpus line containing `needle`; numbers are the ' | ' cells after the label."""
    line = ctx.find_line(file, needle, nth)
    text = ctx.corpus_lines(file)[line - 1].rstrip()
    cells = [c.strip() for c in text.split(" | ")][1:]
    nums: list[Decimal | None] = []
    for c in cells:
        try:
            nums.append(cell_number(c))
        except FixtureError:
            nums.append(None)
    return line, text, nums


def cite_row(
    h: Handoff, ctx: Ctx, file: str, needle: str, nth: int = 0
) -> tuple[str, list[Decimal | None]]:
    """Cite the whole corpus row and return (marker, numbers)."""
    line, text, nums = doc_row(ctx, file, needle, nth)
    return h.cite_doc(file, line, text), nums


def caos_text(h: Handoff, folder: str, module: str, text: str) -> str:
    """Replace '{3,4}' placeholders (CAOS marker numbers) with this handoff's markers: '[C5, C6]'."""

    def sub(m: re.Match[str]) -> str:
        marks = [h.cite_caos(folder, module, int(n)) for n in m.group(1).split(",")]
        return "[" + ", ".join(x.strip("[]") for x in marks) + "]"

    return re.sub(r"\{(\d+(?:\s*,\s*\d+)*)\}", sub, text)


def markers_of(text: str) -> str:
    """The distinct '[C<n>]' markers in `text`, space-joined (for a cite column)."""
    out: list[str] = []
    for m in re.findall(r"C(\d+)", " ".join(re.findall(r"\[(C\d+(?:\s*,\s*C\d+)*)\]", text))):
        mk = f"[C{m}]"
        if mk not in out:
            out.append(mk)
    return " ".join(out)


def join_marks(*marks: str) -> str:
    out: list[str] = []
    for m in marks:
        for x in re.findall(r"\[C\d+\]", m):
            if x not in out:
                out.append(x)
    return "".join(out) if out else GAP
