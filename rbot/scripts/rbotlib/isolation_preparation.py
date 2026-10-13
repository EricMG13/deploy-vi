"""Read-only exact preparation audit; caller owns source selection and run admission.

No owners, writes or native provenance authentication. The shared Capture remains
available for the enclosing observer's final recheck; this is no hostile snapshot.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from rbotlib import dispatch, inventory, prepare, state
from rbotlib.inventory import RunError, output_path
from rbotlib.isolation_capture import Capture, admit


@dataclass(frozen=True)
class PreparationObservation:
    """Detached inventory entries, exact native rows and captured audit files."""

    entries: tuple[dict[str, Any], ...]
    rows: tuple[dict[str, Any], ...]
    files: tuple[tuple[Path, bytes], ...]


def _relative(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or any(ord(c) < 32 or ord(c) == 127 or c in "\\:" for c in value)
    ):
        raise RunError("isolation preparation: invalid relative path")
    path = Path(value)
    if not path.parts or path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise RunError("isolation preparation: noncanonical relative path")
    return value


def _json(path: Path, capture: Capture) -> dict[str, Any]:
    data = json.loads(capture.read(path).decode("utf-8"), object_pairs_hook=state._pairs)
    if not isinstance(data, dict):
        raise RunError("isolation preparation: expected metadata object")
    return data


def _rows(path: Path, data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = dispatch._records(path, data, "files")
    named: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = _relative(row.get("path"))
        if name in named:
            raise RunError("isolation preparation: duplicate source path")
        named[name] = row
    return named


def _registration(row: dict[str, Any], entry: dict[str, Any]) -> None:
    if (
        not state._sha(row.get("sha256"))
        or any(row.get(key) != entry.get(key) for key in ("sha256", "kind"))
        or row.get("kind") != inventory.kind_of(Path(row["path"]))
    ):
        raise RunError("isolation preparation: invalid source sha256/kind")
    if type(row.get("image_read")) is not bool or not isinstance(row.get("unreadable"), str | None):
        raise RunError("isolation preparation: invalid readability")
    if row.get("prepared") is None and row.get("unreadable"):
        return
    if row.get("prepared") != prepare.prepared_name(row):
        raise RunError("isolation preparation: unregistered prepared path")
    _relative(row["prepared"])


def _portfolios(run: Path, index: dict[str, Any]) -> None:
    seen: set[str] = set()
    for row in dispatch._records(run / "prepared/index.json", index, "portfolios"):
        name = _relative(row.get("json"))
        if not name.startswith("prepared/portfolios/") or name in seen:
            raise RunError("isolation preparation: invalid portfolio path")
        seen.add(name)
        admit(dispatch._file(run, name))  # structural admission only; no content read


def _extraction(source: Path, row: dict[str, Any]) -> tuple[dict[str, Any], bytes | None]:
    expected: dict[str, Any] = {key: [] for key in ("entities", "dates", "sheets")}
    expected |= {
        key: {}
        for key in ("sheet_states", "uncached_formulas", "display_scaled", "format_not_applied")
    }
    expected.update({key: row[key] for key in ("path", "sha256", "kind")})
    expected.update(prepared=None, pages=0, excerpt="", image_read=False)
    expected.update(unreadable=None, encoding=None, dropped_surrogates=0)
    try:
        extracted = prepare.read(source, row["kind"])
    except prepare.UnreadableError as exc:
        expected["unreadable"] = str(exc)
        return expected, None
    pages, dropped = prepare._drop_surrogates(extracted.pages)
    first = pages[0] if pages else ""
    metadata = asdict(extracted)
    metadata.update(pages=len(extracted.pages), sheets=[name for name, _ in extracted.sheets])
    for old, new in {
        "uncached": "uncached_formulas",
        "scaled": "display_scaled",
        "not_applied": "format_not_applied",
    }.items():
        metadata[new] = metadata.pop(old)
    expected.update(metadata)
    expected.update(prepared=prepare.prepared_name(row), dropped_surrogates=dropped)
    expected.update(excerpt=" ".join(first.split())[: prepare.EXCERPT_CHARS])
    expected.update(entities=prepare.entities(first[: prepare.SCAN_CHARS]))
    expected.update(dates=prepare.dates(first[: prepare.SCAN_CHARS]))
    return expected, prepare.anchored_text(pages).encode("utf-8")


def _file(run: Path, pack: Path, row: dict[str, Any], capture: Capture) -> set[Path]:
    source = output_path(pack, row["path"])
    raw = capture.read(source)
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise RunError("isolation preparation: original source sha256 changed")
    paths = {source}
    text = None
    if row["prepared"] is not None:
        prepared = output_path(run, row["prepared"])
        text = capture.read(prepared)
        paths.add(prepared)
    expected, rendered = _extraction(source, row)
    # JSON spelling distinguishes bool/int/float as well as every nested field.
    if json.dumps(row, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise RunError("isolation preparation: metadata differs from native extraction")
    if text != rendered:
        raise RunError("isolation preparation: text differs from native extraction")
    return paths


def observe(run: Path, record: state.Record, capture: Capture) -> PreparationObservation:
    """Audit an admitted run using its caller-captured validated native record.

    Registration for every source precedes metadata-selected content I/O. Native
    unreadable rows are evidence; unexpected reader failures propagate. Portfolio
    references are admitted without opening optional portfolio contents.
    """
    record = deepcopy(record)
    pack = Path(record["pack_root"])
    inv_path = output_path(run, "inventory.json")
    idx_path = output_path(run, "prepared/index.json")
    inv, index = _json(inv_path, capture), _json(idx_path, capture)
    if (
        inv.get("schema") != inventory.SCHEMA
        or inv.get("pack_root") != record["pack_root"]
        or index.get("schema") != prepare.SCHEMA
    ):
        raise RunError("isolation preparation: wrong pack root or metadata schema")
    entries, rows = _rows(inv_path, inv), _rows(idx_path, index)
    if entries.keys() != rows.keys():
        raise RunError("isolation preparation: source paths differ from inventory")
    for name, row in rows.items():
        _registration(row, entries[name])
    _portfolios(run, index)
    paths = {inv_path, idx_path}
    for row in rows.values():
        paths |= _file(run, pack, row, capture)
    capture.verify()
    dispatch._prepared(run, record)
    capture.verify()
    files = tuple((path, raw) for path, raw in capture.inventory() if path in paths)
    return PreparationObservation(
        deepcopy(tuple(entries.values())), deepcopy(tuple(rows.values())), files
    )
