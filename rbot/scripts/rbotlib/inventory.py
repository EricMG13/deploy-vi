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
import os
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
            return Path(json.loads(state.read_text(encoding="utf-8"))["pack_root"])
        except (json.JSONDecodeError, KeyError) as exc:
            raise RunError(f"{state}: no readable pack_root ({exc})") from exc
    if run.parent.name == RUNS:
        return run.parent.parent
    raise RunError(f"{run}: no run-state.json and not inside a {RUNS}/ folder")


def kind_of(path: Path) -> str:
    return KINDS.get(path.suffix.lower().lstrip("."), "other")


def pdf_pages(path: Path) -> int | None:
    """Page count, or None when pypdf cannot open the file (prepare records why)."""
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:
            reader.decrypt("")
        return len(reader.pages)
    except (PyPdfError, ValueError, KeyError, OSError):
        return None


def _skip_reason(path: Path) -> str | None:
    if path.is_symlink():
        return "symbolic link"
    if path.name.startswith("."):
        return "hidden"
    if path.name.startswith("~$"):
        return "office lock file"
    return None


def _earlier_reports(runs: Path, run_name: str) -> list[Path]:
    """Report files of other runs in the pack's rbot-runs/ folder."""
    if not runs.is_dir():
        return []
    found = [
        runs / d / name for d in sorted(os.listdir(runs)) if d != run_name for name in REPORT_NAMES
    ]
    return [p for p in found if p.is_file() and not p.is_symlink()]


def _walk(pack: Path, run_name: str) -> tuple[list[Path], list[dict[str, str]]]:
    keep: list[Path] = []
    skipped: list[dict[str, str]] = []

    def usable(path: Path) -> bool:
        reason = _skip_reason(path)
        if reason:
            skipped.append({"path": path.relative_to(pack).as_posix(), "reason": reason})
        return reason is None

    for folder, dirs, names in os.walk(pack):
        here = Path(folder)
        dirs[:] = [d for d in sorted(dirs) if usable(here / d) and not (here == pack and d == RUNS)]
        keep += [here / n for n in sorted(names) if usable(here / n)]
    return keep + _earlier_reports(pack / RUNS, run_name), skipped


def _entry(path: Path, rel: str) -> dict[str, Any]:
    kind = kind_of(path)
    report = False
    if kind in ("html", "md"):
        report = REPORT_MARKER in path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": rel,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "extension": path.suffix.lower().lstrip("."),
        "kind": kind,
        "pages": pdf_pages(path) if kind == "pdf" else None,
        "rbot_report": report,
    }


def build(pack: Path, run_name: str) -> dict[str, Any]:
    keep, skipped = _walk(pack, run_name)
    files = [_entry(path, path.relative_to(pack).as_posix()) for path in keep]
    return {
        "schema": SCHEMA,
        "pack_root": str(pack),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "files": sorted(files, key=lambda f: f["path"]),
        "skipped": sorted(skipped, key=lambda f: f["path"]),
    }


def write(run: Path) -> dict[str, Any]:
    if not run.is_dir():
        raise RunError(f"{run}: no such run folder")
    pack = pack_root(run)
    inventory = build(pack, run.name)
    if not inventory["files"]:
        raise RunError(f"{pack}: the Source Pack has no files")
    text = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    (run / "inventory.json").write_text(text, encoding="utf-8")
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
