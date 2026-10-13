"""Verify an exported immutable runtime, without Git or repository access.

Hashes bind installed bytes to the recorded Git objects, not to a trusted signer.
The build metadata is generated outside the committed runtime to avoid self-reference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
from pathlib import Path
from typing import Any

from rbotlib import __version__
from rbotlib.rules import RBOT_ROOT

METADATA = "runtime.json"
LIMIT = 2_000_000


def git_hash(kind: str, raw: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(raw)}\0".encode() + raw, usedforsecurity=False).hexdigest()


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"runtime metadata: duplicate key {key}")
        result[key] = value
    return result


def _read_file(path: Path) -> bytes:
    if path.stat().st_size > LIMIT:
        raise ValueError(f"runtime: oversized file {path.name}")
    return path.read_bytes()


def files(root: Path) -> dict[str, bytes]:
    """Refuse links and special files before reading; bytecode caches carry no source."""
    result: dict[str, bytes] = {}

    def visit(folder: Path) -> None:
        for path in sorted(folder.iterdir()):
            mode = path.lstat().st_mode
            name = path.relative_to(root).as_posix()
            if stat.S_ISDIR(mode):
                if path.name != "__pycache__":
                    visit(path)
            elif not stat.S_ISREG(mode):
                raise ValueError(f"runtime: unsafe path {name}")
            elif name != METADATA:
                result[name] = _read_file(path)

    if not stat.S_ISDIR(root.lstat().st_mode):
        raise ValueError("runtime: root must be a real directory")
    visit(root)
    return result


def tree(entries: dict[str, tuple[str, str]]) -> bytes:
    """Git's directory sort order includes a trailing slash on tree entries."""
    children: dict[str, dict[str, tuple[str, str]]] = {}
    rows: dict[str, tuple[str, str]] = {}
    for name, item in entries.items():
        first, separator, rest = name.partition("/")
        if separator:
            children.setdefault(first, {})[rest] = item
        else:
            rows[first] = item
    for name, contents in children.items():
        if name in rows:
            raise ValueError("runtime: conflicting file and directory")
        rows[name] = ("40000", git_hash("tree", tree(contents)))
    return b"".join(
        mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(digest)
        for name, (mode, digest) in sorted(
            rows.items(), key=lambda row: (row[0] + ("/" if row[1][0] == "40000" else "")).encode()
        )
    )


def _identity(data: dict[str, Any], entries: dict[str, tuple[str, str]]) -> None:
    commit, root = bytes.fromhex(data["commit_object"]), bytes.fromhex(data["root_object"])
    if (
        git_hash("commit", commit) != data["git_sha"]
        or commit.splitlines()[0] != f"tree {data['source_tree']}".encode()
        or git_hash("tree", root) != data["source_tree"]
        or git_hash("tree", tree(entries)) != data["runtime_tree"]
    ):
        raise ValueError("runtime: conflicting Git provenance")
    # Root-object records are <mode> <name> NUL <20 raw hash bytes>.
    found: list[bytes] = []
    while root:
        header, separator, tail = root.partition(b"\0")
        if not separator or len(tail) < 20:
            raise ValueError("runtime: malformed source root object")
        if header == b"40000 rbot":
            found.append(tail[:20])
        root = tail[20:]
    if found != [bytes.fromhex(data["runtime_tree"])]:
        raise ValueError("runtime: source root does not bind rbot tree")


def verify(root: Path) -> dict[str, Any]:
    path = root / METADATA
    if not stat.S_ISDIR(root.lstat().st_mode) or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("runtime: metadata/root must be regular and unlinked")
    if path.stat().st_size > LIMIT:
        raise ValueError("runtime: oversized metadata")
    data = json.loads(path.read_bytes(), object_pairs_hook=pairs)
    if (
        not isinstance(data, dict)
        or set(data)
        != {
            "schema",
            "version",
            "git_sha",
            "source_tree",
            "runtime_tree",
            "commit_object",
            "root_object",
            "files",
        }
        or data["schema"] != "rbot-runtime/1"
        or data["version"] != __version__
        or not isinstance(data["files"], dict)
        or not data["files"]
    ):
        raise ValueError("runtime: invalid/conflicting metadata schema or version")
    actual = files(root)
    if set(actual) != set(data["files"]):
        raise ValueError("runtime: missing or extra installed files")
    entries = {}
    for name, item in data["files"].items():
        if (
            any(part in ("", ".", "..") for part in name.split("/"))
            or "\\" in name
            or not isinstance(item, dict)
            or set(item) != {"mode", "sha256"}
            or item["mode"] not in ("100644", "100755")
            or hashlib.sha256(actual[name]).hexdigest() != item["sha256"]
        ):
            raise ValueError(f"runtime: altered/invalid installed file {name}")
        entries[name] = (item["mode"], git_hash("blob", actual[name]))
    _identity(data, entries)
    return data


def _executing(root: Path) -> dict[str, Any]:
    if root.absolute() != RBOT_ROOT:
        raise ValueError("runtime: --root must identify the executing installed runtime")
    return verify(root)


def command(args: argparse.Namespace) -> int:
    try:
        data = _executing(args.root)
    except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
        print(f"error: runtime provenance: {exc}", file=sys.stderr)
        return 1
    print(f"rbot {data['version']} {data['git_sha']}")
    return 0
