"""The local issuer corpus: `tests/corpus/corpus.json` (interfaces spec section 12).

Each pack lists its files with sha256 under a root. `external` roots resolve through
RBOT_CORPUS_ROOTS (JSON: root name to absolute path); in-repo roots against the repo.
A file naming `external` (`<root>/<path>`) is copied into the pack when materialised.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rbotlib.rules import RBOT_ROOT

REGISTRY = RBOT_ROOT.parent / "tests" / "corpus" / "corpus.json"
ROOTS_ENV = "RBOT_CORPUS_ROOTS"
EXTERNAL = "external"
MISSING, UNRESOLVED = 1, 2


class CorpusError(ValueError):
    """A pack cannot be materialised; the message names every problem."""


@dataclass(frozen=True)
class CorpusFile:
    path: str
    sha256: str
    cls: str
    document_type: str
    entity: str
    external: str | None
    pages: int | None


@dataclass(frozen=True)
class Pack:
    id: str
    root: str
    path: str
    files: tuple[CorpusFile, ...]
    data: dict[str, Any]  # every registry field as written: issuer, as_of, pathways, traps, ...


@dataclass(frozen=True)
class Registry:
    location: Path
    roots: dict[str, str]
    packs: tuple[Pack, ...]

    def pack(self, pack_id: str) -> Pack:
        for p in self.packs:
            if p.id == pack_id:
                return p
        raise CorpusError(f"no pack {pack_id!r} in {self.location}")


@dataclass(frozen=True)
class Problem:
    code: int  # MISSING (file absent or hash differs) or UNRESOLVED (root unknown)
    in_repo: bool
    message: str


def _need(raw: dict[str, Any], keys: tuple[str, ...], where: str) -> list[Any]:
    missing = [k for k in keys if k not in raw]
    if missing:
        raise CorpusError(f"{where}: missing {missing[0]}")
    return [raw[k] for k in keys]


def _file(raw: dict[str, Any], where: str) -> CorpusFile:
    keys = ("path", "sha256", "class", "document_type", "entity")
    path, sha, cls, kind, entity = _need(raw, keys, where)
    return CorpusFile(path, sha, cls, kind, entity, raw.get("external"), raw.get("pages"))


def _pack(raw: dict[str, Any], where: str) -> Pack:
    pack_id, root, path, files = _need(raw, ("id", "root", "path", "files"), where)
    parsed = tuple(_file(f, f"{where}: file {i}") for i, f in enumerate(files))
    return Pack(pack_id, root, path, parsed, raw)


def load_registry(path: Path = REGISTRY) -> Registry:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CorpusError(f"{path}: {exc}") from exc
    if data.get("schema") != "rbot-corpus/1":
        raise CorpusError(f"{path}: schema is {data.get('schema')!r}, expected 'rbot-corpus/1'")
    top = _need(data, ("roots", "packs"), str(path))
    packs = tuple(_pack(p, f"{path}: pack {i}") for i, p in enumerate(top[1]))
    return Registry(path, dict(top[0]), packs)


def repo_root(registry: Registry) -> Path:
    """The repo holding the registry (`<repo>/tests/corpus/corpus.json`)."""
    return registry.location.parents[2]


class Roots(dict[str, Path]):
    """The roots that resolve to a folder; `invalid` holds configured paths that are not one."""

    def __init__(self) -> None:
        super().__init__()
        self.invalid: dict[str, Path] = {}


def resolve_roots(registry: Registry, env: Mapping[str, str] = os.environ) -> Roots:
    """Every root that resolves to a folder; an unresolved root is simply absent."""
    raw = env.get(ROOTS_ENV, "")
    try:
        external = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        raise CorpusError(f"{ROOTS_ENV} is not a JSON object: {exc}") from exc
    if not isinstance(external, dict):
        raise CorpusError(f"{ROOTS_ENV} is not a JSON object")
    for name, value in external.items():
        if not isinstance(value, str):
            raise CorpusError(f"{ROOTS_ENV}: root {name!r} must be a string path")
    roots = Roots()
    for name, value in registry.roots.items():
        if value != EXTERNAL:
            folder = repo_root(registry) / value
        elif name in external:
            folder = Path(external[name])
        else:
            continue
        if folder.is_dir():
            roots[name] = folder
        else:
            roots.invalid[name] = folder
    return roots


def _root_name(pack: Pack, f: CorpusFile) -> str:
    return (f.external or "").partition("/")[0] or pack.root


def locate(pack: Pack, f: CorpusFile, roots: Mapping[str, Path]) -> Path | None:
    """Where the file lives now, or None when its root is unresolved."""
    root, _, rest = (f.external or "").partition("/")
    if f.external:
        return roots[root] / rest if root in roots else None
    return roots[pack.root] / pack.path / f.path if pack.root in roots else None


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _unresolved(
    pack: Pack, roots: Mapping[str, Path], local: bool, lost: dict[str, list[CorpusFile]]
) -> list[Problem]:
    """One problem per root, with its file count (a root is unset or is not a folder)."""
    invalid: Mapping[str, Path] = getattr(roots, "invalid", {})
    problems = []
    for root, files in lost.items():
        if root in invalid:
            why = f"root {root!r} -> {invalid[root]} is not a folder"
        else:
            why = f"root {root!r} is unresolved for {len(files)} file(s); set {ROOTS_ENV}"
        problems.append(Problem(UNRESOLVED, local, f"{pack.id}: {why}"))
    return problems


def _check_file(pack: Pack, f: CorpusFile, where: Path, root: Path) -> str | None:
    """The problem text for one located file, or None when it is the registered bytes."""
    if not where.resolve().is_relative_to(root.resolve()):
        return f"{pack.id}: {f.path}: escapes root {_root_name(pack, f)!r} ({where})"
    if not where.is_file():
        return f"{pack.id}: {f.path}: missing at {where}"
    actual = sha256_file(where)
    if actual != f.sha256:
        return (
            f"{pack.id}: {f.path}: sha256 differs at {where}: "
            f"registry {f.sha256[:12]}, file {actual[:12]}"
        )
    return None


def _check(
    registry: Registry, pack: Pack, roots: Mapping[str, Path]
) -> tuple[list[Problem], dict[str, Path]]:
    problems, found = [], {}
    lost: dict[str, list[CorpusFile]] = {}
    for f in pack.files:
        local = f.external is None and registry.roots.get(pack.root) != EXTERNAL
        where = locate(pack, f, roots)
        if where is None:
            lost.setdefault(_root_name(pack, f), []).append(f)
        elif message := _check_file(pack, f, where, roots[_root_name(pack, f)]):
            problems.append(Problem(MISSING, local, message))
        else:
            found[f.path] = where
    local_pack = registry.roots.get(pack.root) != EXTERNAL
    return problems + _unresolved(pack, roots, local_pack, lost), found


def verify(registry: Registry, pack: Pack, roots: Mapping[str, Path]) -> list[Problem]:
    """Every file of the pack that is unresolved, missing or not the registered bytes."""
    return _check(registry, pack, roots)[0]


def materialise(registry: Registry, pack: Pack, roots: Mapping[str, Path], dest: Path) -> Path:
    """Copy the pack's verified files into `dest` (the Source Pack a test runs on)."""
    problems, found = _check(registry, pack, roots)
    if problems:
        raise CorpusError("; ".join(p.message for p in problems))
    for name, source in found.items():
        target = dest / name
        if not target.resolve().is_relative_to(dest.resolve()):
            raise CorpusError(f"{pack.id}: {name}: would be written outside the destination")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return dest


def _list(registry: Registry) -> int:
    for p in registry.packs:
        pathways = "; ".join(f"{w['id']} {w['depth']} {w['fit']}" for w in p.data["pathways"])
        issuer = f"{p.data['issuer']['id']} {p.data['period']}"
        print(f"{p.id}  {p.root}:{p.path}  {issuer}  {len(p.files)} file(s)  {pathways}")
    return 0


def _verify(registry: Registry, pack_id: str | None) -> int:
    roots = resolve_roots(registry)
    packs = [registry.pack(pack_id)] if pack_id else list(registry.packs)
    worst = 0
    for p in packs:
        problems = verify(registry, p, roots)
        for problem in problems:
            print(problem.message)
            worst = max(worst, problem.code)
        if not problems:
            print(f"ok {p.id} ({len(p.files)} files)")
    print(f"exit {worst}")
    return worst


def run_command(args: argparse.Namespace) -> int:
    try:
        registry = load_registry(Path(args.registry))
        if args.action == "list":
            return _list(registry)
        return _verify(registry, args.pack)
    except CorpusError as exc:
        print(f"error: {exc}")
        return 2


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("corpus", help="list the corpus packs or verify their files' sha256")
    c.add_argument("action", choices=["verify", "list"])
    c.add_argument("--pack", help="verify one pack only")
    c.add_argument("--registry", default=str(REGISTRY), help="the corpus.json to read")
    c.set_defaults(run=run_command)
