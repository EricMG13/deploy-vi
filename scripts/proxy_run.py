"""Proxy run on a corpus pack (interfaces spec section 12.6): native continuation.

Step 1 copies and hash-verifies the registered pack, then uses native new-run,
inventory and prepare inside that copy. Native discovery and unfinished-run
refusal govern the result; the removed --date option cannot override its clock.
Step 5 (--approve) requires native CP-0 readiness, builds/edits the cited brief,
shows the installed menu and invokes genuine Approval with simulated analyst
choices. It does not dispatch Modules or produce a scorecard.
Repo tooling: never installed with the skill.
"""

from __future__ import annotations

import argparse
import io
import json
import shlex
import sys
import tomllib
import unicodedata
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

import proxy_continue
import proxy_isolated
from proxy_continue import NativeFailure as NativeFailure

from rbotlib import bootstrap, brief, command_receipts, current, runs, state
from rbotlib.catalog import load_catalog
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
from rbotlib.inventory import output_path
from rbotlib.rules import RBOT_ROOT, load_rules


def _native(run: Path, command: str, extra: list[str] | None = None) -> str:
    argv = ["--root", str(RBOT_ROOT), command, "--run", str(run), *(extra or [])]
    captured = io.StringIO()
    with redirect_stdout(captured):
        code = rbot(argv)
    text = captured.getvalue()
    print(text, end="")
    if code != 0:
        raise NativeFailure(command, code)
    return text


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


def _copy_path(registry: Registry, entry: Pack, out: Path) -> Path:
    """Generated output cannot alias a corpus root or escape its output envelope."""
    if Path(entry.id).name != entry.id or entry.id in ("", ".", ".."):
        raise CorpusError(f"unsafe pack id: {entry.id!r}")
    pack = output_path(out, f"{entry.id}/pack")
    for file in entry.files:
        output_path(pack, file.path)  # all unsafe spellings/links refuse before source reads
    resolved = pack.resolve()
    if any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in str(resolved)):
        raise CorpusError(f"{pack!s}: output path has a control character or line separator")
    for root in resolve_roots(registry).values():
        if resolved.is_relative_to(root.resolve()) or root.resolve().is_relative_to(resolved):
            raise CorpusError(f"{pack}: generated output overlaps corpus root {root}")
    return pack


def _approval_options(run: Path, entry: Pack, args: argparse.Namespace) -> list[str]:
    """Choices use the real installed plan/offers; registry hints grant no prior evidence."""
    grading = json.loads(output_path(run, "grading.json").read_text(encoding="utf-8"))
    selected = next((p for p in grading["pathways"] if p["id"] == args.pathway), None)
    if selected is None or args.depth not in selected["depths"]:
        raise CorpusError(f"{args.pathway}.{args.depth} is unavailable in the installed menu")
    pathway = load_catalog(RBOT_ROOT).pathway(args.pathway)
    if pathway is None or args.depth not in pathway.depths:
        raise CorpusError("the installed menu changed; run grade again")
    steps = pathway.depths[args.depth]
    if type(entry.data.get("primary")) is not bool:
        raise CorpusError(f"pack {entry.id}: primary must be a boolean")
    primary = args.primary or ("yes" if entry.data["primary"] else "no")
    deep = "yes" if "CP-DR" in steps and grading["research_questions"] else "no"
    prior = "yes" if "CP-8" in steps and grading["prior_case"] else "no"
    analyst = brief.previous(run)["analyst"].analyst_value
    options = ["--pathway", args.pathway, "--depth", args.depth, "--primary", primary]
    options += ["--analyst", analyst, "--deep-research", deep]
    options += ["--prior-case", prior]
    if args.acknowledge_blocked:
        blocking = selected["depths"][args.depth]["blocking_modules"]
        print("Simulated analyst acknowledges blocking Modules: " + ", ".join(blocking))
        options += ["--acknowledge-blocked"]
    return options


def approve(run: Path, entry: Pack, args: argparse.Namespace) -> Path:
    """Run native readiness, analyst turns and Approval; return its actual renamed path."""
    for name in ("handoffs/CP-0.md", "run-brief.md", "grading.json"):
        path = output_path(run, name)
        if path.exists() and not path.is_file():
            raise CorpusError(f"{path}: Approval input/output must be a regular file")
    command_receipts.preflight(run)
    if state.read(run)["approval"] is not None:
        raise CorpusError(f"{run}: already approved; use native next for continuation")
    current.reconcile(run, RBOT_ROOT)
    if bootstrap.phase(run, RBOT_ROOT, load_rules(RBOT_ROOT)) != "approval":
        raise CorpusError(f"{run}: native CP-0 readiness required before Approval; run accept")
    _native(run, "brief", ["--from", "handoffs/CP-0.md"])
    edits = [
        "--set",
        f"objective=Simulated proxy {args.pathway} at {args.depth} depth",
        "--set",
        "analyst=proxy-run (simulated analyst)",
    ]
    for assignment in args.set:
        edits += ["--set", assignment]
    for tranche in args.set_tranche:
        edits += ["--set-tranche", *tranche]
    print("Simulated analyst edits: " + shlex.join(edits))
    _native(run, "brief", edits)
    _native(run, "grade")  # prints every installed Pathway/Depth and its limitations
    options = _approval_options(run, entry, args)
    argv = [sys.executable, str(RBOT_ROOT / "scripts/rbot.py"), "--root", str(RBOT_ROOT)]
    print("Simulated Approval: " + shlex.join([*argv, "approve", "--run", str(run), *options]))
    text = _native(run, "approve", options)
    targets = [
        line.removeprefix("approved: ")
        for line in text.splitlines()
        if line.startswith("approved: ")
    ]
    if len(targets) != 1:
        raise CorpusError("native Approval returned no unique renamed run; inspect its output")
    target = state.run_path(Path(targets[0]))
    state.read(target)
    return target


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
    paths = [(f, output_path(pack, f.path)) for f in entry.files]
    bad = [f.path for f, path in paths if not path.is_file() or sha256_file(path) != f.sha256]
    if bad:
        raise CorpusError(f"{pack}: not the registered files: {', '.join(bad)}")


def start(registry: Registry, entry: Pack, args: argparse.Namespace, out: Path) -> Path:
    """Step 1: materialise the pack, create the run folder, inventory and prepare."""
    pack = _copy_path(registry, entry, out)
    if not pack.is_dir():
        materialise(registry, entry, resolve_roots(registry), pack)
    _verify_copy(entry, pack)
    _version(repo_root(registry))  # retain registry-project preflight; state version is native
    run = runs.create_run(pack, entry.data["issuer"]["id"])
    for command in ("inventory", "prepare"):
        _native(run, command)
    return run


def _transport_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--continue", dest="continuing", action="store_true")
    parser.add_argument("--run", help="explicit existing renamed run; requires --continue")
    parser.add_argument("--module", help="isolated Module: import upstream, stop at its dispatch")
    parser.add_argument("--from-run", help="isolated source run (default: newest qualifying)")
    parser.add_argument("--fixtures", action="store_true", help="isolated source: fixture Handoffs")
    parser.add_argument("--model-label", help="requested caller label; never provider proof")
    parser.add_argument(
        "--fetch", action="store_true", help="needs RBOT_FETCH=1 in the environment"
    )
    parser.add_argument("--reported-module", help="genuine controller dispatch report target")
    parser.add_argument("--receipt")
    parser.add_argument("--reporter")
    parser.add_argument("--message-sha256")
    parser.add_argument("--worker-started-at")
    parser.add_argument("--accept-module", help="explicit controller request to accept own output")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="proxy_run", description=__doc__.splitlines()[0])
    parser.add_argument("--pack", required=True)
    parser.add_argument("--pathway", required=True)
    parser.add_argument("--depth", required=True, choices=["full", "quick"])
    parser.add_argument("--primary", choices=["yes", "no"], help="override the pack's flag")
    parser.add_argument("--approve", action="store_true", help="step 5: simulate native Approval")
    _transport_options(parser)
    parser.add_argument("--set", action="append", default=[], help="simulated brief FIELD=VALUE")
    parser.add_argument("--set-tranche", action="append", nargs=2, default=[])
    parser.add_argument(
        "--acknowledge-blocked", action="store_true", help="simulated acknowledgement"
    )
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--out", help="the corpus-runs folder (default: <repo>/corpus-runs)")
    args = parser.parse_args(argv)
    _usage(parser, args)
    simulated = args.approve or args.module is not None
    if not simulated and (args.set or args.set_tranche or args.acknowledge_blocked):
        parser.error("simulated edits/acknowledgement require --approve")
    try:
        proxy_continue.check_options(args)
        registry = _load(Path(args.registry))
        entry = registry.pack(args.pack)
        _check_pathway(entry, args.pathway, args.depth)
        out = Path(args.out) if args.out else repo_root(registry) / "corpus-runs"
        if args.module is not None:
            return proxy_isolated.run_isolated(
                registry, entry, args, out, proxy_isolated.Hooks(start, approve, _native)
            )
        out, isolated = proxy_isolated.effective_out(out, entry.id, args.run)
        if args.approve or args.continuing:
            return _existing(registry, entry, args, out, isolated)
        run = start(registry, entry, args, out)
        proxy_continue.advance(run, args.model_label, _native)
    except NativeFailure as exc:
        print(exc)
        return exc.code
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        print(exc)
        return 1
    print(f"run folder: {run}")
    print(f"next: CP-0; use rbot next --run {run}")
    return 0


def _existing(
    registry: Registry, entry: Pack, args: argparse.Namespace, out: Path, isolated: bool
) -> int:
    pack = _copy_path(registry, entry, out)
    run = proxy_continue.existing(pack, args.run, args.pathway, args.depth)
    if run is None:
        run = _latest_run(pack.parent)
        proxy_continue.existing(pack, str(run), args.pathway, args.depth)
    _verify_copy(entry, pack)
    if args.continuing:
        return _continue(run, args, proxy_isolated.read_record(out, run) if isolated else None)
    run = approve(run, entry, args)
    print(f"run folder: {run}")
    return 0


def _usage(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    reports = [args.reported_module, args.receipt, args.reporter, args.message_sha256]
    provided = any(value is not None for value in reports)
    if provided and not all(value and value.strip() for value in reports):
        parser.error("dispatch report requires --reported-module/receipt/reporter/message-sha256")
    if args.worker_started_at is not None and not all(reports):
        parser.error("--worker-started-at requires a genuine dispatch report")
    if (args.run is not None or provided or args.accept_module is not None) and not args.continuing:
        parser.error("existing-run/dispatch-report/accept options require --continue")
    if args.continuing and args.approve:
        parser.error("--continue and --approve are separate native phases")
    proxy_isolated.usage(parser, args)
    if any(value is not None and not value.strip() for value in (args.run, args.accept_module)):
        parser.error("--run and --accept-module require nonempty values")


def _continue(run: Path, args: argparse.Namespace, isolated: dict[str, object] | None) -> int:
    print(f"run folder: {run}")
    if args.receipt:
        _native(run, "dispatch-receipt", proxy_continue.receipt_options(args))
    code = 0
    if args.accept_module:
        try:
            _native(run, "accept", ["--module", args.accept_module])
        except NativeFailure as exc:
            if exc.code not in (2, 3):
                raise
            code = exc.code
        step = state.read(run)["steps"][args.accept_module]
        if step["status"] in ("failed", "skipped"):
            return code
        if args.accept_module == "CP-0" and step["status"] in ("accepted", "blocked"):
            print("CP-0 readiness completed; waiting for analyst Approval")
            return code
    if proxy_isolated.stopped(run, isolated):
        return code
    proxy_continue.advance(run, args.model_label, _native)
    return code


if __name__ == "__main__":
    sys.exit(main())
