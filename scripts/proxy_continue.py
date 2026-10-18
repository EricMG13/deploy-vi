"""Native continuation only; worker transport belongs to the external controller."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import sys
import unicodedata
from collections.abc import Callable
from pathlib import Path

from rbotlib import dispatch, fetch, state
from rbotlib.corpus import CorpusError
from rbotlib.rules import RBOT_ROOT

Native = Callable[[Path, str, list[str] | None], str]


class NativeFailure(CorpusError):
    """Preserve the native command's actual exit and already printed diagnostic."""

    def __init__(self, command: str, code: int) -> None:
        super().__init__(f"rbot {command} failed (exit {code})")
        self.code = code


def check_options(args: argparse.Namespace) -> None:
    label = args.model_label
    if label is not None and (
        not label.strip()
        or len(label) > 200
        or any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Zl", "Zp") for c in label)
    ):
        raise CorpusError("model-label: require 1-200 printable characters; caller claim only")
    live = fetch.available()
    if args.fetch and not live:
        raise CorpusError("--fetch requires RBOT_FETCH=1 in the environment; it is never set here")
    if live and not args.fetch:
        raise CorpusError("RBOT_FETCH is set; pass --fetch to run with fetch, or unset it")
    if args.module is not None and not args.module.strip():
        raise CorpusError("--module requires a nonempty Module id")


def existing(pack: Path, explicit: str | None, pathway: str, depth: str) -> Path | None:
    if explicit is None:
        return None
    run = state.run_path(Path(explicit))
    record = state.write_guard(run)
    if record is None or Path(record["pack_root"]) != pack.resolve():
        raise CorpusError("explicit run belongs to a different registered pack copy")
    if record["approval"] is not None and (record["pathway"], record["depth"]) != (pathway, depth):
        raise CorpusError("explicit run has a different approved Pathway/Depth")
    return run


def receipt_options(args: argparse.Namespace) -> list[str]:
    flags = [
        "--module",
        args.reported_module,
        "--receipt",
        args.receipt,
        "--reporter",
        args.reporter,
        "--message-sha256",
        args.message_sha256,
    ]
    if args.model_label is not None:
        flags += ["--model", args.model_label]
    if args.worker_started_at is not None:
        flags += ["--worker-started-at", args.worker_started_at]
    return flags


def worker(run: Path, selected: state.Record, label: str | None) -> None:
    module = selected["step"]
    if selected["dispatch"] != f"dispatch/{module}.md":
        raise CorpusError("native selection returned an unexpected dispatch path")
    raw = dispatch._file(run, selected["dispatch"]).read_bytes()
    record = state.read(run)
    from rbotlib import attempts

    events = attempts.read_history(run, module, record["steps"][module])
    findings = (
        f"validate/{module}.json" if any(e["event"] == "validation" for e in events) else None
    )
    if raw != dispatch.qualified_message(run, RBOT_ROOT, module, record, findings).encode():
        raise CorpusError("persisted dispatch changed since native selection; transport refused")
    print(f"worker required: {module}; selection has not sent a worker")
    print(f"exact dispatch file: {run / selected['dispatch']}")
    print(f"message sha256: {hashlib.sha256(raw).hexdigest()}")
    print("Controller: send exactly those bytes; report actual dispatch with rbot dispatch-receipt")
    print("Receipt needs --module, --receipt, --reporter and --message-sha256; then rbot accept")
    if label is not None:
        print("Requested caller model label (unqualified): " + json.dumps(label))
        print("Attach --model only to the genuine dispatch-receipt; provider/model stays unknown")


def _prior_before_selection(run: Path, native: Native) -> None:
    record = state.read(run)
    if "CP-8" not in record["plan"] or record["steps"]["CP-8"]["status"] not in (
        "pending",
        "running",
    ):
        return
    from rbotlib import current, prior_diff
    from rbotlib import next as selection

    selection._eligible(record)
    current.reconcile(run, RBOT_ROOT)
    record = state.read(run)
    outstanding = next(
        (n for n in record["plan"] if record["steps"][n]["status"] in ("pending", "running")), None
    )
    if outstanding != "CP-8":
        return
    # A persisted selection is already a grant, even before a receipt is reported.
    names = (*prior_diff.NAMES, "dispatch/CP-8.md")
    if any((run / n).exists() or (run / n).is_symlink() for n in names) or record["steps"][
        "CP-8"
    ].get("attempts", 0):
        with state.publication(run) as checked:
            prior_diff.qualified_prior(run, RBOT_ROOT, state.read(run))
            checked()
    else:
        native(run, "diff", ["--prior", record["prior_case"]["report"]])


def advance(
    run: Path,
    label: str | None,
    native: Native,
    on_module: Callable[[state.Record], bool] | None = None,
) -> None:
    if state.read(run)["report"]["written_at"] is not None:
        print(f"report already written: {run / 'report.html'}, {run / 'report.md'}")
        return
    # Each host becomes terminal or returns its genuine refusal/error. Never retry it here.
    for _ in range(len(state.read(run)["plan"]) + 1):
        _prior_before_selection(run, native)
        selected = json.loads(native(run, "next", None))
        if selected["kind"] == "module":
            if on_module is not None and on_module(selected):
                continue  # isolated mode imported this Module natively
            worker(run, selected, label)
            return
        if selected["kind"] == "done":
            native(run, "render", None)  # prints the paths and the summary; failure pauses the run
            return
        if selected["kind"] != "host" or selected["step"] not in ("MODEL", "FIT"):
            raise CorpusError("native selection returned an unsupported host")
        command = selected["step"].lower()
        expected = [
            sys.executable,
            str(RBOT_ROOT / "scripts/rbot.py"),
            "--root",
            str(RBOT_ROOT),
            command,
            "--run",
            str(run),
        ]
        if shlex.split(selected["command"]) != expected:
            raise CorpusError("native host command differs from the selected managed API")
        native(run, command, None)
    raise CorpusError("native continuation made no bounded progress; inspect the run")
