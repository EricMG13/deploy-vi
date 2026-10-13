"""`rbot` command line. Each later command lives with its module (`add_command`).

A command given `--run <RUN>` appends one line to `<RUN>/log/rbot.log`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rbotlib import (
    accept,
    approve,
    attempts,
    brief,
    calc,
    corpus,
    dispatch,
    fit,
    grade,
    inventory,
    prepare,
    runlog,
    runs,
    state,
)
from rbotlib import (
    next as next_step,
)
from rbotlib.catalog import check_tree
from rbotlib.contract import ContractError, load_contract
from rbotlib.model.run import add_command as add_model_command
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, load_rules
from rbotlib.validate import check


def _fail(path: Path, exc: Exception) -> int:
    reason = exc.strerror if isinstance(exc, FileNotFoundError) and exc.strerror else exc
    print(f"error: {path}: {reason}", file=sys.stderr)
    return 1


def _validate(args: argparse.Namespace) -> int:
    rules = load_rules(args.root)
    if args.module in rules.host_producers:
        from rbotlib.host_validate import qualify

        try:
            if not args.run_dir:
                raise inventory.RunError(f"{args.module}: --run required for current host origin")
            qualify(Path(args.run_dir), args.root, args.module, Path(args.handoff))
        except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
            return _fail(Path(args.handoff), exc)
        print("exit 0")
        return 0
    path = args.root / "modules" / args.module / "contract.json"
    try:
        contract = load_contract(path, rules)
    except (FileNotFoundError, ContractError) as exc:
        return _fail(path, exc)
    try:
        text = Path(args.handoff).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        return _fail(Path(args.handoff), exc)
    run = Path(args.run_dir) if args.run_dir else None
    code, findings = check(text, contract, rules, run)
    for f in findings:
        if f.code == "run_error":
            print(f"error: {f.message}", file=sys.stderr)
            return code
        print(f"{f.code}: {f.message}")
    print(f"exit {code}")
    return code


def _render(args: argparse.Namespace) -> int:
    rules = load_rules(args.root)
    folder = args.root / "modules" / args.module
    try:
        text = render_module(load_contract(folder / "contract.json", rules), rules)
    except (FileNotFoundError, ContractError) as exc:
        return _fail(folder / "contract.json", exc)
    if args.write:
        (folder / "MODULE.md").write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def _check(args: argparse.Namespace) -> int:
    problems = check_tree(args.root, load_rules(args.root))
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


def _log_path(run: Path) -> Path:
    """Refuse pre-existing unsupported log kinds before command execution."""
    return runlog.path(run)


def _log(run: Path, argv: list[str], code: int, *, receipt: runlog.Receipt | None = None) -> None:
    """Actual logger seam; an owned receipt avoids recursively acquiring its lock."""
    runlog.append(run, argv, code, receipt)


def _finish_log(
    args: argparse.Namespace, log_run: Path | None, argv: list[str] | None, result: int
) -> int:
    created = getattr(args, "created_run_dir", None)
    if created is not None:
        try:
            log_run = state.log_run_path(Path(created))
            args.run_dir = str(log_run)
        except (OSError, ValueError, RecursionError) as exc:
            result = _fail(Path(created), exc)
    if log_run is not None:
        log_run = Path(args.run_dir)
        try:
            state.write_guard(log_run)
            _log(log_run, sys.argv[1:] if argv is None else argv, result)
        except (inventory.RunError, OSError) as exc:
            result = _fail(log_run, exc)
    return result


def _managed_host(args: argparse.Namespace, argv: list[str] | None) -> int | None:
    from rbotlib.model import host, qualification

    try:
        if not qualification.managed(Path(args.run_dir)):
            return None
    except (OSError, ValueError, RecursionError) as exc:
        return _fail(Path(args.run_dir), exc)
    actual = sys.argv[1:] if argv is None else argv

    def append_log(receipt: runlog.Receipt, code: int) -> None:
        _log(receipt.run, actual, code, receipt=receipt)

    if args.command == "fit":
        from rbotlib.fit_host import Fit

        return host.execute(args, actual, append_log, Fit())
    return host.run(args, actual, append_log)


def _inspect_legacy(args: argparse.Namespace) -> bool:
    """Classify before command entry; checked legacy inspection has no logger."""
    if not getattr(args, "run_dir", None):
        return False
    selected = Path(args.run_dir)
    inspection = args.command == "plan" or (args.command == "state" and args.set is None)
    if inspection:
        return "ownership" not in state.read(state.log_run_path(selected))
    state.write_guard(selected)
    return False


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="rbot")
    parser.add_argument("--root", type=Path, default=RBOT_ROOT, help="the RBOT folder")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="check a Handoff against its module contract")
    v.add_argument("handoff")
    v.add_argument("--module", required=True)
    v.add_argument("--run", dest="run_dir", help="also check citations against this run folder")
    v.set_defaults(run=_validate)
    r = sub.add_parser("render-module", help="print or write a module's MODULE.md")
    r.add_argument("module")
    r.add_argument("--write", action="store_true")
    r.set_defaults(run=_render)
    c = sub.add_parser("check", help="contracts, generated modules, Pathways, Front Pages, budget")
    c.set_defaults(run=_check)
    corpus.add_command(sub)
    inventory.add_command(sub)
    prepare.add_command(sub)
    brief.add_command(sub)
    add_model_command(sub)
    grade.add_command(sub)
    approve.add_commands(sub)
    calc.add_command(sub)
    fit.add_command(sub)
    state.add_command(sub)
    runs.add_command(sub)
    dispatch.add_command(sub)
    attempts.add_command(sub)
    accept.add_command(sub)
    next_step.add_command(sub)
    return parser.parse_args(argv)


def _preflight(log_run: Path | None) -> int | None:
    if log_run is None:
        return None
    from rbotlib.command_receipts import preflight

    try:
        preflight(log_run)
    except (OSError, ValueError, RecursionError) as exc:
        return _fail(log_run, exc)
    return None


def main(argv: list[str] | None = None) -> int:
    args = _arguments(argv)
    run_dir = getattr(args, "run_dir", None)
    try:
        legacy_inspection = _inspect_legacy(args)
    except (OSError, ValueError, RecursionError) as exc:
        return _fail(Path(run_dir or "."), exc)
    if args.command in ("model", "fit"):
        if (managed_result := _managed_host(args, argv)) is not None:
            return managed_result
    log_run: Path | None = None
    if run_dir and not legacy_inspection:
        selected = Path(run_dir)
        try:
            guard = getattr(args, "log_run_guard", None)
            if guard is not None:
                selected = guard(selected)
            if selected.is_dir():
                _log_path(selected)
                log_run = selected
        except (OSError, ValueError, RecursionError) as exc:
            return _fail(selected, exc)
    if (refusal := _preflight(log_run)) is not None:
        return refusal
    result = 1  # what the log records when the command raises
    try:
        result = int(args.run(args))
    finally:
        result = _finish_log(args, log_run, argv, result)
    return result
