"""Bounded physical observation of caller-selected files, without read authority.

This observer acquires no lock and writes nothing. Cooperating readers can recheck
identity and bytes; this is not a hostile filesystem snapshot or native qualification.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from rbotlib.inventory import RunError

_FILE_LIMIT = 64 * 1024 * 1024
_TOTAL_LIMIT = 256 * 1024 * 1024


def admit(path: Path, *, directory: bool = False) -> os.stat_result:
    """Admit a canonical absolute physical path; callers still choose authorized paths."""
    if not path.is_absolute() or path.anchor != os.sep or ".." in path.parts:
        raise RunError("isolation: canonical absolute path required")
    for part in reversed((path, *path.parents)):
        info = _component(part, ancestor=part != path)
    valid = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not valid or (not directory and info.st_nlink != 1):
        raise RunError(f"isolation: regular single-link file/directory required: {path}")
    return info


def _component(path: Path, *, ancestor: bool) -> os.stat_result:
    if any(ord(c) < 32 or ord(c) == 127 or c in "\\:" for c in path.name):
        raise RunError(f"isolation: unsafe path {path}")
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        raise RunError(f"isolation: symlink path {path}")
    if ancestor and not stat.S_ISDIR(info.st_mode):
        raise RunError(f"isolation: directory ancestor required: {path}")
    return info


def _walk_error(error: OSError) -> None:
    raise error


def tree(folder: Path) -> tuple[str, ...]:
    """Validate all structural entries, return sorted relative names, read no contents."""
    admit(folder, directory=True)
    names = []
    for base, dirs, files in os.walk(folder, followlinks=False, onerror=_walk_error):
        for name in dirs + files:
            path = Path(base) / name
            admit(path, directory=name in dirs)
            names.append(str(path.relative_to(folder)))
    return tuple(sorted(names))


def _identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _read(path: Path, before: os.stat_result) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(descriptor)
        if _identity(before) != _identity(opened):
            raise RunError(f"isolation: capture identity changed: {path}")
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise RunError(f"isolation: opened regular single-link file required: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as source:
            raw = source.read(_FILE_LIMIT + 1)
        if len(raw) > _FILE_LIMIT:
            raise RunError("isolation: capture exceeds 64 MiB per file")
        return raw
    finally:
        os.close(descriptor)


class Capture:
    """Retain first inode/device and exact bytes; rereads consume the quota once."""

    def __init__(self) -> None:
        self._files: dict[Path, tuple[tuple[int, int], bytes]] = {}

    def read(self, path: Path) -> bytes:
        """Admit before opening, refuse replacement/change, retain only successful reads."""
        before = admit(path)
        prior = self._files.get(path)
        if prior is not None and prior[0] != _identity(before):
            raise RunError(f"isolation: captured identity changed: {path}")
        raw = _read(path, before)
        if prior is not None and prior[1] != raw:
            raise RunError(f"isolation: bytes changed during capture: {path}")
        size = sum(len(entry[1]) for name, entry in self._files.items() if name != path)
        if size + len(raw) > _TOTAL_LIMIT:
            raise RunError("isolation: capture exceeds 256 MiB total")
        if prior is None:
            self._files[path] = _identity(before), raw
        return raw

    def verify(self) -> None:
        """Re-admit and reread every captured file; refuse identity or exact-byte changes."""
        for path in tuple(self._files):
            self.read(path)

    def inventory(self) -> tuple[tuple[Path, bytes], ...]:
        """Detached, sorted exact bytes; this view cannot replace the capture baseline."""
        return tuple((path, entry[1]) for path, entry in sorted(self._files.items()))
