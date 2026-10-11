"""Proxy run on a corpus pack (interfaces spec section 12.6): steps 1 and 5 only.

Step 1 (default): copy the pack into `corpus-runs/<pack_id>/pack/` (external files
resolved), create the run folder `corpus-runs/<pack_id>/<YYYYMMDD>-<issuer>-pending/`
with a pre-Approval `run-state.json`, then run `rbot inventory` and `rbot prepare`.
Step 5 (`--approve`): print the `rbot approve` command the simulated Approval runs,
from the pack's registry fields. Dispatch, accept and the scorecard (steps 2 to 4) and
`rbot new-run`, `rbot next` and `rbot approve` themselves arrive with Plans 04 and 06;
until then step 1 writes the run-state seed itself and step 5 prints the command only.
Repo tooling: never installed with the skill.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

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
)


def run_id(base: Path, issuer_id: str, day: str) -> str:
    """`<YYYYMMDD>-<issuer>-pending`, with -2, -3, ... when that folder exists (spec 8.1)."""
    stem = f"{day}-{issuer_id.lower()}-pending"
    n, candidate = 1, stem
    while (base / candidate).exists():
        n += 1
        candidate = f"{stem}-{n}"
    return candidate


def _version(repo: Path) -> str:
    data = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def seed_state(run: Path, pack: Path, entry: Pack, args: argparse.Namespace, version: str) -> None:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    state: dict[str, Any] = {"schema": "rbot-run-state/1", "rbot_version": version}
    state |= {"run_id": run.name, "pack_root": str(pack), "created_at": now, "updated_at": now}
    state |= {"run_brief": "run-brief.md", "run_brief_sha256": None}
    state |= {"issuer_id": entry.data["issuer"]["id"], "as_of_date": entry.data["as_of"]}
    state |= dict.fromkeys(
        ("pathway", "depth", "primary", "deep_research", "prior_case", "approval")
    )
    state |= {"plan": [], "steps": {}}
    state["report"] = {"written_at": None, "html_sha256": None, "md_sha256": None}
    state["proxy"] = {"pack": entry.id, "pathway": args.pathway, "depth": args.depth}
    (run / "run-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


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
    runs = sorted(p for p in base.glob("*-pending*") if (p / "run-state.json").is_file())
    if not runs:
        raise CorpusError(f"{base}: no pending proxy run; run step 1 first")
    return max(runs, key=lambda p: p.stat().st_mtime)


def start(registry: Registry, entry: Pack, args: argparse.Namespace, out: Path) -> Path:
    """Step 1: materialise the pack, create the run folder, inventory and prepare."""
    base = out / entry.id
    pack = base / "pack"
    if not pack.is_dir():
        materialise(registry, entry, resolve_roots(registry), pack)
    run = base / run_id(base, entry.data["issuer"]["id"], args.date)
    run.mkdir(parents=True)
    seed_state(run, pack, entry, args, _version(repo_root(registry)))
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
    parser.add_argument("--date", default=datetime.now(UTC).strftime("%Y%m%d"))
    args = parser.parse_args(argv)
    try:
        registry = load_registry(Path(args.registry))
        entry = registry.pack(args.pack)
        _check_pathway(entry, args.pathway, args.depth)
        out = Path(args.out) if args.out else repo_root(registry) / "corpus-runs"
        if args.approve:
            print(shlex.join(approve_command(_latest_run(out / entry.id), entry, args)))
            return 0
        run = start(registry, entry, args, out)
    except CorpusError as exc:
        print(exc)
        return 1
    print(f"run folder: {run}")
    print("next: CP-0 (dispatch arrives with Plan 06: rbot next)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
