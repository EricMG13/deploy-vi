"""`rbot inventory`: list every file of the Source Pack (interfaces spec section 8.1).

Writes `<RUN>/inventory.json`: per file its path relative to the pack, size, sha256,
extension, detected kind, PDF page count and whether it is an earlier RBOT Report.
Hidden files and folders, Office lock files and symbolic links are skipped and listed
with the reason. `rbot-runs/` is not walked: only another run's `report.html` or
`report.md` is listed, because an earlier Report is a Prior Case candidate. Source
files are only read, never modified.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from rbotlib.corpus import sha256_file

SCHEMA = "rbot-inventory/1"
RUNS = "rbot-runs"
REPORT_MARKER = 'id="rbot-run"'
REPORT_NAMES = ("report.html", "report.md")
KINDS = {
    "pdf": "pdf",
    "xlsx": "xlsx",
    "xlsm": "xlsx",
    "csv": "csv",
    "txt": "txt",
    "md": "md",
    "markdown": "md",
    "html": "html",
    "htm": "html",
    **dict.fromkeys(("png", "jpg", "jpeg", "gif", "bmp", "tif", "tiff", "webp"), "image"),
}


class RunError(ValueError):
    """The run folder cannot be used; the message names why."""


def pack_root(run: Path) -> Path:
    """The Source Pack of a run: `pack_root` in run-state.json, else the folder above rbot-runs/."""
    state = run / "run-state.json"
    if state.is_file():
        try:
            root = Path(json.loads(state.read_text(encoding="utf-8"))["pack_root"])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RunError(f"{state}: no readable pack_root ({exc})") from exc
        if not root.is_absolute():
            raise RunError(f"{state}: pack_root must be an absolute path, not {str(root)!r}")
        if root.resolve() == run.resolve():
            raise RunError(f"{state}: pack_root is the run folder itself")
        return root.resolve()
    if run.parent.name == RUNS:
        return run.parent.parent.resolve()
    raise RunError(f"{run}: no run-state.json and not inside a {RUNS}/ folder")


def kind_of(path: Path) -> str:
    return KINDS.get(path.suffix.lower().lstrip("."), "other")


class _Collect(logging.Handler):
    def __init__(self, seen: list[str]) -> None:
        super().__init__(logging.WARNING)
        self.seen = seen

    def emit(self, record: logging.LogRecord) -> None:
        self.seen.append(record.getMessage())


@contextmanager
def pypdf_warnings() -> Iterator[list[str]]:
    """Keep pypdf's log warnings off the console and hand them back as text."""
    log = logging.getLogger("pypdf")
    seen: list[str] = []
    handler, propagate = _Collect(seen), log.propagate
    log.addHandler(handler)
    log.propagate = False
    try:
        yield seen
    finally:
        log.removeHandler(handler)
        log.propagate = propagate


def output_path(run: Path, relative: str) -> Path:
    """An output below the resolved run, with no symlink in its destination path."""
    parts = Path(relative)
    if parts.is_absolute() or ".." in parts.parts:
        raise RunError(f"output path is outside the run folder: {relative}")
    target = run
    for part in parts.parts:
        target /= part
        if target.is_symlink():
            raise RunError(f"output path is a symlink: {target}")
    if not target.resolve().is_relative_to(run.resolve()):
        raise RunError(f"output path is outside the run folder: {relative}")
    return target


def write_atomic(path: Path, text: str) -> None:
    """Write to a unique temp file beside the target, fsync, then `os.replace`: a failed write
    never leaves half a file, and two writers never share a temp name."""
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False
    )
    temp = Path(handle.name)
    try:
        with handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _open_pdf(path: Path) -> tuple[int | None, str | None]:
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and not reader.decrypt(""):
            return None, "encrypted PDF: a password is needed"
        return len(reader.pages), None
    except (PyPdfError, ValueError, KeyError, OSError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def pdf_info(path: Path) -> tuple[int | None, str | None]:
    """(page count or None, problem): why pypdf cannot open the file, else its warnings."""
    with pypdf_warnings() as seen:
        pages, problem = _open_pdf(path)
    return pages, problem or "; ".join(dict.fromkeys(seen)) or None


def _skip_reason(path: Path) -> str | None:
    if path.is_symlink():
        return "symbolic link"
    if path.name.startswith("."):
        return "hidden"
    if path.name.startswith("~$"):
        return "office lock file"
    return None


def _rel(pack: Path, path: Path, reason: str) -> dict[str, str]:
    return {"path": path.relative_to(pack).as_posix(), "reason": reason}


def _reports_in(pack: Path, folder: Path, skipped: list[dict[str, str]]) -> list[Path]:
    """The report files of one other run folder; loose files are ignored, links and
    unreadable folders are skipped with the reason."""
    if folder.is_symlink():
        skipped.append(_rel(pack, folder, "symbolic link"))
    elif folder.is_dir():
        try:
            os.listdir(folder)
        except OSError as exc:
            skipped.append(_rel(pack, folder, f"unreadable: {exc.strerror or exc}"))
            return []
        named = [folder / n for n in REPORT_NAMES]
        skipped += [_rel(pack, p, "symbolic link") for p in named if p.is_symlink()]
        return [p for p in named if p.is_file() and not p.is_symlink()]
    return []


def _earlier_reports(pack: Path, run: Path, skipped: list[dict[str, str]]) -> list[Path]:
    """Report files of other runs in the pack's rbot-runs/ folder (never through a symlink)."""
    runs = pack / RUNS
    if runs.is_symlink() or not runs.is_dir():
        return []
    try:
        names = sorted(os.listdir(runs))
    except OSError as exc:
        skipped.append(_rel(pack, runs, f"unreadable: {exc.strerror or exc}"))
        return []
    found: list[Path] = []
    for d in names:
        if (runs / d).resolve() != run:
            found += _reports_in(pack, runs / d, skipped)
    return found


def _walk(pack: Path, run: Path) -> tuple[list[Path], list[dict[str, str]]]:
    keep: list[Path] = []
    skipped: list[dict[str, str]] = []

    def note(path: Path, reason: str) -> None:
        skipped.append({"path": path.relative_to(pack).as_posix(), "reason": reason})

    def usable(path: Path) -> bool:
        reason = _skip_reason(path)
        if reason:
            note(path, reason)
        return reason is None

    def unreadable(exc: OSError) -> None:
        note(Path(exc.filename or pack), f"unreadable: {exc.strerror or exc}")

    def walked(here: Path, d: str) -> bool:
        return usable(here / d) and not (here == pack and d == RUNS) and (here / d).resolve() != run

    for folder, dirs, names in os.walk(pack, onerror=unreadable):
        here = Path(folder)
        dirs[:] = [d for d in sorted(dirs) if walked(here, d)]
        keep += [here / n for n in sorted(names) if usable(here / n)]
    return keep + _earlier_reports(pack, run, skipped), skipped


def _entry(path: Path, rel: str) -> dict[str, Any]:
    kind = kind_of(path)
    report = False
    if kind in ("html", "md"):
        report = REPORT_MARKER in path.read_text(encoding="utf-8", errors="replace")
    entry: dict[str, Any] = {
        "path": rel,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "extension": path.suffix.lower().lstrip("."),
        "kind": kind,
        "pages": None,
        "rbot_report": report,
    }
    if kind == "pdf":
        entry["pages"], problem = pdf_info(path)
        if problem:
            entry["problem"] = problem
    return entry


def build(pack: Path, run: Path) -> dict[str, Any]:
    keep, skipped = _walk(pack, run)
    files = []
    for path in keep:
        rel = path.relative_to(pack).as_posix()
        try:
            files.append(_entry(path, rel))
        except OSError as exc:
            skipped.append({"path": rel, "reason": f"unreadable: {exc.strerror or exc}"})
    return {
        "schema": SCHEMA,
        "pack_root": str(pack),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "files": sorted(files, key=lambda f: f["path"]),
        "skipped": sorted(skipped, key=lambda f: f["path"]),
    }


def write(run: Path) -> dict[str, Any]:
    run = run.resolve()
    if not run.is_dir():
        raise RunError(f"{run}: no such run folder")
    pack = pack_root(run)
    if not pack.is_dir():
        raise RunError(f"{pack}: no such Source Pack")
    destination = output_path(run, "inventory.json")
    inventory = build(pack, run)
    if not inventory["files"]:
        raise RunError(f"{pack}: the Source Pack has no files")
    text = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    destination.write_text(text, encoding="utf-8")
    return inventory


def load(run: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    return data


def run_command(args: argparse.Namespace) -> int:
    try:
        inventory = write(Path(args.run_dir))
    except RunError as exc:
        print(exc)
        return 1
    n, s = len(inventory["files"]), len(inventory["skipped"])
    print(f"inventory.json: {n} file(s), {s} skipped")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("inventory", help="list every Source Pack file with its sha256 and kind")
    c.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    c.set_defaults(run=run_command)
