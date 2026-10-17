"""The saved-page format of `fetched/` and its qualification (Plan 10, rulings R7 and R9).

A fetched page is `fetched/<nn>-<host>.md`: flat front matter between `---` lines, then the
saved body. `sha256` is the hash of the body bytes, everything after the closing `---` line,
exactly as written, so `qualified` recomputes it from the file alone. `render` is the only
place that lays the file out.

A worker that writes `fetched/` by hand passes qualification, because the hash is
self-attested (R9, accepted limit).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator, Mapping
from datetime import date
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urldefrag

from rbotlib.handoff import HandoffError, parse
from rbotlib.inventory import RunError

FOLDER = "fetched"
NAME = re.compile(r"(\d{2})-([a-z0-9.-]{1,80})\.md")
REQUIRED = ("url", "retrieved", "sha256", "question", "content_type")
OPTIONAL = ("final_url",)
QUESTIONS_TABLE = "brief.research_questions"
BRIEF = "run-brief.md"


class FetchedFile(NamedTuple):
    name: str
    url: str
    retrieved: str
    question: str
    sha256: str


def render(front: Mapping[str, str], body: str) -> str:
    """The whole file: front matter, then `body`, which the `sha256` line covers.

    `front` holds `url`, `retrieved`, `question`, `content_type` and optionally `final_url`
    (written only when it differs from `url`); `sha256` is computed here.
    """
    final = front.get("final_url", front["url"])
    lines = [f"url: {front['url']}"]
    if final != front["url"]:
        lines.append(f"final_url: {final}")
    lines += [
        f"retrieved: {front['retrieved']}",
        f"sha256: {hashlib.sha256(body.encode('utf-8')).hexdigest()}",
        f"question: {front['question']}",
        f"content_type: {front['content_type']}",
    ]
    return "\n".join(["---", *lines, "---", ""]) + body


def approved_questions(run: Path) -> tuple[str, ...]:
    """The `Yes` ids of `brief.research_questions` in `run-brief.md` (none before the Run Brief)."""
    path = run / BRIEF
    if not path.is_file():
        return ()
    try:
        table = parse(path.read_text(encoding="utf-8")).tables.get(QUESTIONS_TABLE)
    except (HandoffError, OSError, UnicodeDecodeError) as exc:
        raise RunError(f"{BRIEF}: not a readable Run Brief") from exc
    return tuple(row[0] for row in table.rows if row[-1] == "Yes") if table else ()


def _read(path: Path) -> tuple[dict[str, str], bytes] | None:
    """The front matter and body bytes of a saved page; None when it is not in this layout.

    An unreadable file is simply not a saved page, so it is never qualified.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None
    end = data.find(b"\n---\n", 3)
    if not data.startswith(b"---\n") or end < 0:
        return None
    try:
        head = data[4:end].decode("utf-8")
    except UnicodeDecodeError:
        return None
    meta: dict[str, str] = {}
    for line in head.split("\n") if head else []:
        key, sep, value = line.partition(":")
        if not sep or key.strip() in meta:
            return None
        meta[key.strip()] = value.strip()
    return meta, data[end + 5 :]


def _candidates(run: Path) -> Iterator[Path]:
    """The regular files named `<nn>-<host>.md` directly in a real `fetched/` folder."""
    folder = run / FOLDER
    if folder.is_symlink() or not folder.is_dir():
        return
    for path in sorted(folder.iterdir()):
        if NAME.fullmatch(path.name) and path.is_file() and not path.is_symlink():
            yield path


def _intact(meta: dict[str, str], body: bytes, approved: tuple[str, ...]) -> bool:
    if set(meta) not in (set(REQUIRED), {*REQUIRED, *OPTIONAL}) or not all(meta.values()):
        return False
    try:
        dated = date.fromisoformat(meta["retrieved"]).isoformat() == meta["retrieved"]
    except ValueError:
        return False
    return (
        dated
        and meta["question"] in approved
        and meta["sha256"] == hashlib.sha256(body).hexdigest()
    )


def qualified(run: Path) -> dict[str, FetchedFile]:
    """The saved pages with a sound layout, hash and approved question, by `fetched/<name>`."""
    approved = approved_questions(run)
    found: dict[str, FetchedFile] = {}
    for path in _candidates(run):
        read = _read(path)
        if read and _intact(*read, approved):
            meta, name = read[0], f"{FOLDER}/{path.name}"
            found[name] = FetchedFile(
                name, meta["url"], meta["retrieved"], meta["question"], meta["sha256"]
            )
    return found


def saved_path(run: Path, url: str) -> Path | None:
    """The saved page whose `url` is this one (fragment ignored), or None."""
    wanted = urldefrag(url).url
    for path in _candidates(run):
        read = _read(path)
        if read and read[0].get("url") == wanted:
            return path
    return None
