"""Proxy run on a corpus pack (interfaces spec section 12.6): steps 1 and 5 only.

Step 1 copies and hash-verifies the registered pack, then uses native new-run,
inventory and prepare inside that copy. Native discovery and unfinished-run
refusal govern the result; the removed --date option cannot override its clock.
Step 5 (--approve) only prints a simulated Approval invocation. It does not
establish readiness, execute Approval, dispatch Modules or produce a scorecard.
Repo tooling: never installed with the skill.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

from rbotlib import runs, state
from rbotlib.cli import main as rbot
from rbotlib.corpus import (
    REGISTRY,
    CorpusError,
    Pack,
    Registry,
    load_registry,
    materialise,
    repo_root,
    resolve_roots,
    sha256_file,
)
from rbotlib.inventory import RunError


def _version(repo: Path) -> str:
    path = repo / "pyproject.toml"
    try:
        return str(tomllib.loads(path.read_text(encoding="utf-8"))["project"]["version"])
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, KeyError) as exc:
        raise CorpusError(f"{path}: {exc}") from exc


def _load(path: Path) -> Registry:
    try:
        return load_registry(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        raise CorpusError(f"{path}: {exc}") from exc


def approve_command(run: Path, entry: Pack, args: argparse.Namespace) -> list[str]:
    """Step 5: the Approval a proxy run simulates (every Deep Research question approved)."""
    primary = args.primary or ("yes" if entry.data["primary"] else "no")
    prior = "yes" if entry.data["prior_pack"] else "no"
    command = ["python", "rbot/scripts/rbot.py", "approve", "--run", str(run)]
    command += ["--pathway", args.pathway, "--depth", args.depth, "--primary", primary]
    return [*command, "--analyst", "proxy-run", "--deep-research", "yes", "--prior-case", prior]


def _check_pathway(entry: Pack, pathway: str, depth: str) -> None:
    listed = [(w["id"], w["depth"]) for w in entry.data["pathways"]]
    if (pathway, depth) not in listed:
        raise CorpusError(f"pack {entry.id} lists {listed}, not ({pathway!r}, {depth!r})")


def _latest_run(base: Path) -> Path:
    pack = base / "pack"
    run = runs.discover_unfinished(pack) if pack.is_dir() else None
    if run is None:
        raise CorpusError(f"{base}: no unfinished native proxy run; run step 1 first")
    state.write_guard(run)
    return run


def _verify_copy(entry: Pack, pack: Path) -> None:
    """Every registered file of the copy is present and is the registered bytes."""
    bad = [
        f.path
        for f in entry.files
        if not (pack / f.path).is_file() or sha256_file(pack / f.path) != f.sha256
    ]
    if bad:
        raise CorpusError(f"{pack}: not the registered files: {', '.join(bad)}")


def start(registry: Registry, entry: Pack, args: argparse.Namespace, out: Path) -> Path:
    """Step 1: materialise the pack, create the run folder, inventory and prepare."""
    base = out / entry.id
    pack = base / "pack"
    if not pack.is_dir():
        materialise(registry, entry, resolve_roots(registry), pack)
    _verify_copy(entry, pack)
    _version(repo_root(registry))  # retain registry-project preflight; state version is native
    run = runs.create_run(pack, entry.data["issuer"]["id"])
    for command in ("inventory", "prepare"):
        if rbot([command, "--run", str(run)]) != 0:
            raise CorpusError(f"rbot {command} failed for {run}")
    return run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="proxy_run", description=__doc__.splitlines()[0])
    parser.add_argument("--pack", required=True)
    parser.add_argument("--pathway", required=True)
    parser.add_argument("--depth", required=True, choices=["full", "quick"])
    parser.add_argument("--primary", choices=["yes", "no"], help="override the pack's flag")
    parser.add_argument("--approve", action="store_true", help="step 5: print the approval")
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--out", help="the corpus-runs folder (default: <repo>/corpus-runs)")
    args = parser.parse_args(argv)
    try:
        registry = _load(Path(args.registry))
        entry = registry.pack(args.pack)
        _check_pathway(entry, args.pathway, args.depth)
        out = Path(args.out) if args.out else repo_root(registry) / "corpus-runs"
        if args.approve:
            print(shlex.join(approve_command(_latest_run(out / entry.id), entry, args)))
            return 0
        run = start(registry, entry, args, out)
    except (CorpusError, RunError, OSError, RecursionError) as exc:
        print(exc)
        return 1
    print(f"run folder: {run}")
    print(f"next: CP-0; use rbot next --run {run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
