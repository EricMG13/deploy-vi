"""Isolated Module mode of the proxy runner (interfaces spec section 12.6 step 3).

An isolated run is a fresh, genuine native run in its own pack copy. Upstream Handoff
bytes come from the newest qualifying proxy run of the same pack (or the declared
fixtures) and are imported only through native dispatch-receipt and accept, with the
front-matter run_id line the single rewritten byte range. Nothing else writes run state.
Repo tooling: never installed with the skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import proxy_continue

from rbotlib import approve, fetched, state
from rbotlib.catalog import load_catalog
from rbotlib.corpus import CorpusError, Pack, Registry, repo_root
from rbotlib.fsio import write_atomic
from rbotlib.inventory import output_path
from rbotlib.rules import RBOT_ROOT, load_rules

ISOLATED = "isolated"
FIXTURE_DIR = "tests/fixtures/handoffs"
QUICK_DIR = "quick"
TERMINAL = ("accepted", "blocked")
Native = proxy_continue.Native


def fixture_path(module_id: str, depth: str, folder: Path | None = None) -> Path:
    """The fixture Handoff for a module: `quick/<ID>.md` at quick when it exists, else `<ID>.md`."""
    base = folder if folder is not None else Path(__file__).resolve().parents[1] / FIXTURE_DIR
    if depth == "quick" and (base / QUICK_DIR / f"{module_id}.md").is_file():
        return base / QUICK_DIR / f"{module_id}.md"
    return base / f"{module_id}.md"


@dataclass(frozen=True)
class Source:
    label: str  # source run folder name, or "fixtures"
    where: str  # source run path, or "fixtures"
    folder: Path
    models: dict[str, str]  # module -> recorded model label (runs only)
    depth: str = ""  # fixtures only: picks `quick/<ID>.md` at quick

    def path(self, module: str) -> Path:
        if self.label == "fixtures":
            return fixture_path(module, self.depth, self.folder)
        return output_path(self.folder, f"{module}.md")

    def read(self, module: str) -> bytes:
        return self.path(module).read_bytes()

    def model(self, module: str) -> str | None:
        return self.models.get(module) if self.label != "fixtures" else "fixture"


def plan_dependencies(module: str, pathway: str, depth: str) -> list[str]:
    """Modules the target needs: catalog order before it, plus declared Handoff inputs."""
    if module == "CP-8":
        raise CorpusError(
            "isolated CP-8 requires its own actual approved prior; import unavailable"
        )
    rules = load_rules(RBOT_ROOT)
    selected = load_catalog(RBOT_ROOT).pathway(pathway)
    if selected is None or depth not in selected.depths:
        raise CorpusError(f"{pathway}.{depth} is unavailable in the installed menu")
    steps = list(selected.depths[depth])
    if module not in steps or module in rules.host_producers or steps[0] == module:
        raise CorpusError(f"--module {module!r}: not an upstream-dependent Module of {pathway}")
    # Declared Handoff inputs are always earlier in the plan (check_tree enforces the order).
    return [s for s in steps[: steps.index(module)] if s not in rules.host_producers]


def isolated_root(out: Path, pack_id: str) -> Path:
    return out / pack_id / ISOLATED


def effective_out(out: Path, pack_id: str, run_arg: str | None) -> tuple[Path, bool]:
    """An explicit run inside an isolated pack copy continues in that copy."""
    if run_arg is not None:
        root = isolated_root(out, pack_id).resolve()
        run = Path(run_arg).resolve()
        if run.is_relative_to(root) and run != root:
            return root / run.relative_to(root).parts[0], True
    return out, False


def new_out(out: Path, pack_id: str, module: str) -> Path:
    root = isolated_root(out, pack_id)
    n = 1
    while (root / f"{module}-{n}").exists():
        n += 1
    return root / f"{module}-{n}"


def _switched_off(module: str, step: dict[str, Any]) -> bool:
    """A step approval skipped with its own recorded reason (Deep Research not approved)."""
    return step["status"] == "skipped" and step.get("reason") == approve.SKIPS.get(module)


def _unqualified(run: Path, deps: list[str]) -> tuple[Source | None, list[str]]:
    record = state.read(run)
    if record["approval"] is None:
        return None, ["not approved"]
    missing, models = [], {}
    for module in deps:
        step = record["steps"].get(module)
        if step is not None and _switched_off(module, step):
            continue  # switched off by approval: this source run never needed the module
        path = output_path(run, f"handoffs/{module}.md")
        ok = step is not None and step["status"] in TERMINAL and path.is_file()
        if ok and hashlib.sha256(path.read_bytes()).hexdigest() != step.get("sha256"):
            ok = False  # edited after acceptance: the recorded hash no longer describes it
        if not ok:
            missing.append(module)
        elif step.get("model"):
            models[module] = step["model"]
    if missing:
        return None, missing
    return Source(run.name, str(run), run / "handoffs", models), []


def _fixture_source(registry: Registry, deps: list[str], depth: str) -> Source:
    folder = repo_root(registry) / FIXTURE_DIR
    absent = [m for m in deps if not fixture_path(m, depth, folder).is_file()]
    if absent:
        raise CorpusError(f"no fixture Handoff for: {', '.join(absent)}")
    return Source("fixtures", "fixtures", folder, {}, depth)


def _candidates(envelope: Path, from_run: str | None) -> list[Path]:
    if from_run is not None:
        return [state.run_path(Path(from_run))]
    dated = [
        (state.read(run)["created_at"], run.name, run)
        for run in (envelope.iterdir() if envelope.is_dir() else [])
        if (run / state.STATE).is_file()
    ]
    return [item[2] for item in sorted(dated, reverse=True)]


def find_source(
    registry: Registry, out: Path, pack_id: str, deps: list[str], args: argparse.Namespace
) -> Source:
    if args.fixtures:
        return _fixture_source(registry, deps, args.depth)
    reasons = []
    for run in _candidates(out / pack_id / "pack" / "rbot-runs", args.from_run):
        source, missing = _unqualified(run, deps)
        if source is not None:
            return source
        reasons.append(f"{run.name}: {', '.join(missing)}")
    detail = "; ".join(reasons) or "no proxy run of this pack"
    raise CorpusError(
        f"no qualifying source run for {pack_id}; needs accepted or blocked "
        f"{', '.join(deps)} ({detail}); nothing was substituted"
    )


def usage(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.module is not None and (args.approve or args.continuing):
        parser.error("--module starts its own run; continue it with --continue --run")
    if (args.from_run is not None or args.fixtures) and args.module is None:
        parser.error("--from-run/--fixtures require --module")
    if args.from_run is not None and args.fixtures:
        parser.error("--from-run and --fixtures are exclusive sources")


def rewrite_run_id(raw: bytes, run_id: str) -> bytes:
    """Replace only the front-matter run_id line; every other byte is kept."""
    lines = raw.splitlines(keepends=True)
    if not lines or lines[0].strip() != b"---":
        return raw
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == b"---":
            break
        if line.startswith(b"run_id:"):
            ending = line[len(line.rstrip(b"\r\n")) :]
            lines[i] = b"run_id: " + run_id.encode() + ending
            break
    return b"".join(lines)


def import_fetched(run: Path, source: Source) -> bool:
    """Copy the source run's saved pages byte for byte (a symlinked folder or file is refused);
    True when a `fetched/` folder was copied."""
    folder = Path(source.where) / fetched.FOLDER
    if folder.is_symlink():
        raise CorpusError(f"{folder}: a symlinked fetched/ folder is not imported")
    if not folder.is_dir():
        return False
    target = output_path(run, fetched.FOLDER)
    target.mkdir(exist_ok=True)
    for path in sorted(folder.iterdir()):
        if path.is_symlink():
            raise CorpusError(f"{path}: a symlink in fetched/ is not imported")
        if path.is_file():
            (target / path.name).write_bytes(path.read_bytes())
    return True


def import_module(run: Path, selected: dict[str, Any], source: Source, native: Native) -> str:
    """Write the source bytes as the module's own Handoff, report and accept natively."""
    module = selected["step"]
    if module == "CP-DR" and source.label != "fixtures" and import_fetched(run, source):
        # the message lists the qualified saved pages, so prepare it again with the pages in place
        native(run, "dispatch-message", ["--module", module])
    message = output_path(run, selected["dispatch"]).read_bytes()
    original = source.read(module)
    imported = rewrite_run_id(original, state.read(run)["run_id"])
    output_path(run, "handoffs").mkdir(exist_ok=True)
    output_path(run, f"handoffs/{module}.md").write_bytes(imported)
    reporter = (
        f"proxy_run --module: imported {source.path(module)} "
        f"sha256 {hashlib.sha256(original).hexdigest()}; run_id front matter rewritten"
    )
    flags = [
        "--module",
        module,
        "--receipt",
        f"isolated-import:{source.label}:{module}",
        "--reporter",
        reporter,
        "--message-sha256",
        hashlib.sha256(message).hexdigest(),
    ]
    if source.model(module):
        flags += ["--model", str(source.model(module))]
    native(run, "dispatch-receipt", flags)
    try:
        native(run, "accept", ["--module", module])
    except proxy_continue.NativeFailure as exc:
        if exc.code != 3:  # exit 3 is a Blocked Handoff, still accepted
            raise
    return hashlib.sha256(imported).hexdigest()


def write_record(
    out: Path, run: Path, module: str, source: Source, imported: dict[str, str]
) -> None:
    body = {"module": module, "source": source.where, "imported": imported}
    write_atomic(out / f"{run.name}.json", json.dumps(body, indent=2) + "\n")


def read_record(out: Path, run: Path) -> dict[str, Any] | None:
    path = out / f"{run.name}.json"
    if not path.is_file():
        return None
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


@dataclass
class Isolated:
    module: str
    deps: list[str]
    source: Source
    native: Native
    label: str | None
    imported: dict[str, str]


def drive(run: Path, job: Isolated, save: Callable[[], None]) -> bool:
    """Import every upstream Module natively; True once native next selected the target."""
    reached = []

    def on_module(selected: dict[str, Any]) -> bool:
        step = selected["step"]
        if step == job.module:
            reached.append(step)
            return False
        if step not in job.deps:
            raise CorpusError(f"native selected unexpected Module {step}")
        job.imported[step] = import_module(run, selected, job.source, job.native)
        save()
        return True

    proxy_continue.advance(run, job.label, job.native, on_module)
    return bool(reached)


@dataclass(frozen=True)
class Hooks:
    start: Callable[[Registry, Any, argparse.Namespace, Path], Path]
    approve: Callable[[Path, Any, argparse.Namespace], Path]
    native: Native


def run_isolated(
    registry: Registry, entry: Pack, args: argparse.Namespace, out: Path, hooks: Hooks
) -> int:
    """Fresh native run, native Approval, upstream imports, then stop at the target."""
    deps = plan_dependencies(args.module, args.pathway, args.depth)
    source = find_source(registry, out, entry.id, deps, args)
    iso = new_out(out, entry.id, args.module)
    run = hooks.start(registry, entry, args, iso)
    job = Isolated(args.module, deps, source, hooks.native, args.model_label, {})
    # Approval needs native CP-0 readiness, so CP-0 is imported before the simulated analyst.
    selected = json.loads(hooks.native(run, "next", None))
    if selected.get("kind") != "module" or selected.get("step") != "CP-0":
        raise CorpusError("native next did not select CP-0 before Approval")
    job.imported["CP-0"] = import_module(run, selected, source, hooks.native)
    run = hooks.approve(run, entry, args)

    def save() -> None:
        write_record(iso, run, job.module, source, job.imported)

    save()
    if not drive(run, job, save):
        raise CorpusError(f"native next never selected {job.module}; inspect {run}")
    print(f"run folder: {run}")
    print(f"isolated {job.module}: send the dispatch above, then --continue --run {run}")
    return 0


def stopped(run: Path, record: dict[str, Any] | None) -> bool:
    """An isolated run ends once its target is terminal; downstream is never advanced."""
    if record is None:
        return False
    if state.read(run)["steps"][record["module"]]["status"] not in (*TERMINAL, "failed", "skipped"):
        return False
    print(f"isolated run: stopped after {record['module']}; downstream is not advanced")
    return True
