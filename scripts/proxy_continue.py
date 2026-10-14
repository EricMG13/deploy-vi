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

from rbotlib import dispatch, state
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
    if args.fetch:
        raise CorpusError("Plan10 fetch unavailable; no network fetch performed")
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
    if any(record["report"][key] is not None for key in ("written_at", "html_sha256", "md_sha256")):
        raise CorpusError("complete/partial Report metadata requires its native renderer owner")
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


def advance(
    run: Path,
    label: str | None,
    native: Native,
    on_module: Callable[[state.Record], bool] | None = None,
) -> None:
    # Each host becomes terminal or returns its genuine refusal/error. Never retry it here.
    for _ in range(len(state.read(run)["plan"]) + 1):
        selected = json.loads(native(run, "next", None))
        if selected["kind"] == "module":
            if on_module is not None and on_module(selected):
                continue  # isolated mode imported this Module natively
            worker(run, selected, label)
            return
        if selected["kind"] == "done":
            print("analysis all-terminal; Plan07 renderer unavailable; Report fields remain null")
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
