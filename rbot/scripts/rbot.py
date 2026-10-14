"""Trusted RBOT entry: bind an installed tree before executing package sources."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.path.pop(0)  # installed entry directory cannot shadow standard dependencies

import argparse
import ast
import hashlib
import json
import stat
from collections.abc import Sequence
from importlib.abc import MetaPathFinder
from importlib.machinery import SOURCE_SUFFIXES, FileFinder, ModuleSpec, SourceFileLoader
from pathlib import Path
from types import CodeType, ModuleType
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
METADATA = "runtime.json"
LIMIT = 2_000_000
_SOURCES: dict[str, bytes] | None = None


def _version(raw: bytes) -> str:
    values = [
        ast.literal_eval(n.value)
        for n in ast.parse(raw).body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in n.targets)
    ]
    if len(values) != 1 or not isinstance(values[0], str):
        raise ValueError("runtime: missing/conflicting source version")
    return values[0]


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


def verify(root: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
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
    if data["version"] != _version(actual["scripts/rbotlib/__init__.py"]):
        raise ValueError("runtime: invalid/conflicting metadata version")
    return data, actual


def _executing(root: Path) -> dict[str, Any]:
    if root.absolute() != ROOT:
        raise ValueError("runtime: --root must identify the executing installed runtime")
    return verify(root)[0]


def command(args: argparse.Namespace) -> int:
    try:
        data = _executing(args.root)
    except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
        print(f"error: runtime provenance: {exc}", file=sys.stderr)
        return 1
    print(f"rbot {data['version']} {data['git_sha']}")
    return 0


class _SourceOnly(SourceFileLoader):
    def get_code(self, fullname: str) -> CodeType:
        source = (
            self.get_data(self.path)
            if _SOURCES is None
            else _SOURCES[Path(self.path).relative_to(ROOT).as_posix()]
        )
        return self.source_to_code(source, self.path)


class _RuntimeFinder(MetaPathFinder):
    def find_spec(
        self, fullname: str, path: Sequence[str] | None, target: ModuleType | None = None
    ) -> ModuleSpec | None:
        if fullname != "rbotlib" and not fullname.startswith("rbotlib."):
            return None
        folder = str(SCRIPTS) if path is None else path[0]
        spec = FileFinder(folder, (_SourceOnly, SOURCE_SUFFIXES)).find_spec(fullname)
        if spec is None:
            raise ImportError(f"runtime source unavailable: {fullname}")
        return spec


def _main() -> int:
    global _SOURCES
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("command", nargs="?")
    args, _ = parser.parse_known_args()
    if args.command == "version":
        return command(args)  # no package imports, including when metadata is missing
    if (ROOT / METADATA).exists() or (ROOT / METADATA).is_symlink():
        try:
            _, _SOURCES = verify(ROOT)
        except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
            print(f"error: runtime provenance: {exc}", file=sys.stderr)
            return 1
    sys.modules["rbot"] = sys.modules[__name__]
    sys.meta_path.insert(0, _RuntimeFinder())
    from rbotlib.cli import main

    return main()


if __name__ == "__main__":
    sys.exit(_main())
