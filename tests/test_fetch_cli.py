"""`rbot fetch`: the CLI gate in front of the network (Plan 10, rulings R1 to R3 and P9)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import NoReturn

import pytest
from fetch_server import PAGE, TODAY, FetchServer, Starter, html
from test_approve import PRIOR, _approve, _ready

import rbot
from rbotlib import fetch, state
from rbotlib.cli import _arguments, main
from rbotlib.rules import Rules
from spec_fixture import SOURCES, build_tree

NO_TOOL = "rbot fetch: no fetch tool\n"
URL = "http://pub.example/page"
REAL = fetch.fetch_page


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


@pytest.fixture(autouse=True)
def fetch_off(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.delenv("RBOT_FETCH", raising=False)
    yield


def approved(root: Path, tmp_path: Path, *extra: str) -> Path:
    run = _ready(root, tmp_path, rows=PRIOR)
    assert _approve(root, run, *extra) == 0
    return run.parent / "20261011-acme-full-credit-assessment"


def on(monkeypatch: pytest.MonkeyPatch, root: Path, tmp_path: Path) -> Path:
    """An approved run with Deep Research on and fetch recorded `on`."""
    monkeypatch.setenv("RBOT_FETCH", "1")
    return approved(root, tmp_path)


def cmd(run: Path, url: str = URL, *question: str) -> list[str]:
    return ["fetch", "--run", str(run), "--url", url, *question]


def refuse(run: Path, capsys: pytest.CaptureFixture[str], *question: str, url: str = URL) -> str:
    capsys.readouterr()
    assert main(cmd(run, url, *question)) == 1
    out = capsys.readouterr()
    assert out.out == ""
    return out.err


@pytest.fixture
def unreachable(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[str]]:
    """Any call of the network function fails the test; the list records nothing."""

    def never(*_: object, **__: object) -> NoReturn:
        raise AssertionError("the network was reached")

    monkeypatch.setattr(fetch, "fetch_page", never)
    monkeypatch.setattr(fetch, "system_resolver", never)
    monkeypatch.setattr(fetch, "system_connector", never)
    yield []


def via(monkeypatch: pytest.MonkeyPatch, srv: FetchServer) -> None:
    """Run the command's fetch against the local fixture (the command itself has no seam)."""
    monkeypatch.setattr(
        fetch,
        "fetch_page",
        lambda url, **kw: REAL(
            url,
            resolver=lambda host, port: ["93.184.216.34"],
            connector=srv.connector,
            today=TODAY,
        ),
    )


def test_no_fetch_tool_when_off(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    unreachable: list[str],
) -> None:
    run = approved(root, tmp_path)  # approved with the variable unset: recorded `off`
    assert state.read(run)["approval"]["fetch"] == "off"
    assert refuse(run, capsys, "--question", "RQ-1") == NO_TOOL
    monkeypatch.setenv("RBOT_FETCH", "1")  # set now, but the recorded mode is off
    assert refuse(run, capsys, "--question", "RQ-1") == NO_TOOL
    record = state.read(run)
    del record["approval"]["fetch"]  # an older state with no key reads as off
    (run / "run-state.json").write_text(json.dumps(record), encoding="utf-8")
    assert refuse(run, capsys, "--question", "RQ-1") == NO_TOOL
    for value in ("0", ""):  # the variable is not exactly 1: refused before any file is read
        monkeypatch.setenv("RBOT_FETCH", value)
        capsys.readouterr()
        args = argparse.Namespace(
            run_dir=str(tmp_path / "missing"), root=root, url=URL, question="RQ-1"
        )
        assert fetch.run_command(args) == 1
        assert capsys.readouterr().err == NO_TOOL
    assert not (run / "fetched").exists()


def test_refusals_in_order(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    unreachable: list[str],
) -> None:
    monkeypatch.setenv("RBOT_FETCH", "1")
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "c").mkdir()
    pending = _ready(root, tmp_path / "a", rows=PRIOR)
    assert refuse(pending, capsys, "--question", "RQ-1") == "rbot fetch: the run is not approved\n"
    no_dr = approved(root, tmp_path / "b", "--deep-research", "no")
    assert refuse(no_dr, capsys, "--question", "RQ-1") == (
        "rbot fetch: Deep Research is not approved for this run\n"
    )
    run = approved(root, tmp_path / "c")
    ids = "approved questions: RQ-1\n"
    assert refuse(run, capsys) == f"rbot fetch: --question is required; {ids}"
    unknown = refuse(run, capsys, "--question", "RQ-9")
    assert unknown == f"rbot fetch: 'RQ-9' is not an approved question; {ids}"
    brief = run / "run-brief.md"
    text = brief.read_text(encoding="utf-8")
    row = "| RQ-1 | Is demand recovering? | CP-2 | Yes |"
    assert row in text
    brief.write_text(text.replace(row, row.replace("Yes", "No")), encoding="utf-8")
    unticked = refuse(run, capsys, "--question", "RQ-1")
    assert unticked == "rbot fetch: 'RQ-1' is not an approved question; approved questions: none\n"
    brief.write_text(text, encoding="utf-8")
    bad = refuse(run, capsys, "--question", "RQ-1", url="http://127.0.0.1/")
    assert bad == "host '127.0.0.1' is an IP address\n"
    state.set_status(run, "CP-DR", "skipped", "test")
    skipped = refuse(run, capsys, "--question", "RQ-1")
    assert skipped == "rbot fetch: CP-DR is skipped in this run\n"
    record = state.read(run)
    record["plan"].remove("CP-DR")
    del record["steps"]["CP-DR"]
    (run / "run-state.json").write_text(json.dumps(record), encoding="utf-8")
    assert refuse(run, capsys, "--question", "RQ-1") == (
        "rbot fetch: CP-DR is not in this run's plan\n"
    )


def test_success_prints_the_path(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    server: Starter,
) -> None:
    run = on(monkeypatch, root, tmp_path)
    srv = server({"/page": html(PAGE), "/other": html(PAGE)})
    saved = fetch.execute(
        run,
        root,
        URL,
        "RQ-1",
        env={"RBOT_FETCH": "1"},
        resolver=lambda host, port: ["93.184.216.34"],
        connector=srv.connector,
    )
    assert saved == run / "fetched" / "01-pub.example.md"
    via(monkeypatch, srv)
    capsys.readouterr()
    assert main(cmd(run, "http://pub.example/other", "--question", "RQ-1")) == 0
    assert capsys.readouterr().out == "fetched/02-pub.example.md\n"
    count = len(list((run / "fetched").iterdir()))
    assert main(cmd(run, URL, "--question", "RQ-1")) == 0
    assert capsys.readouterr().out == "fetched/01-pub.example.md\n"
    assert len(list((run / "fetched").iterdir())) == count == 2
    requests = len(srv.requests)
    assert main(cmd(run, URL + "#frag", "--question", "RQ-1")) == 0  # saved: no network
    assert len(srv.requests) == requests


def test_failures_are_one_line_exit_1(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    server: Starter,
) -> None:
    run = on(monkeypatch, root, tmp_path)
    srv = server({})  # every path answers 404
    via(monkeypatch, srv)
    assert refuse(run, capsys, "--question", "RQ-1") == ("page answered with status 404\n")
    monkeypatch.setattr(fetch, "save_page", lambda *a: (_ for _ in ()).throw(OSError("disk")))
    srv = server({"/page": html(PAGE)})
    via(monkeypatch, srv)
    assert refuse(run, capsys, "--question", "RQ-1") == "rbot fetch: disk\n"


def test_log_holds_no_source_text(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    server: Starter,
) -> None:
    run = on(monkeypatch, root, tmp_path)
    srv = server({"/page": html(PAGE)})
    via(monkeypatch, srv)
    assert main(cmd(run, URL, "--question", "RQ-1")) == 0
    log = (run / "log" / "rbot.log").read_text(encoding="utf-8")
    assert log.splitlines()[-1].endswith(f"fetch --run {run} --url {URL} --question RQ-1\t0")
    assert "Revenue grew" not in log and "Annual Report" not in log


def test_cli_exposes_no_test_seam() -> None:
    parser = _arguments(["fetch", "--run", "r", "--url", "http://a.example/"])
    assert parser.command == "fetch"
    top = argparse.ArgumentParser()
    fetch.add_command(top.add_subparsers())
    sub = next(a for a in top._actions if isinstance(a, argparse._SubParsersAction)).choices[
        "fetch"
    ]
    flags = {o for a in sub._actions for o in a.option_strings if o != "-h" and o != "--help"}
    assert flags == {"--run", "--url", "--question"}


def test_real_cli_refuses_loopback(
    root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = on(monkeypatch, root, tmp_path)
    done = subprocess.run(
        [
            sys.executable,
            rbot.__file__,
            *cmd(run, "http://127.0.0.1/", "--question", "RQ-1"),
        ],
        env={**os.environ, "RBOT_FETCH": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 1 and done.stdout == ""
    assert done.stderr == "host '127.0.0.1' is an IP address\n"
    assert not (run / "fetched").exists()


def test_fetch_execute_signature_takes_no_seam_from_the_command(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: dict[str, object] = {}

    def spy(*args: object, **kw: object) -> Path:
        seen["kw"] = kw
        return tmp_path / "fetched" / "01-x.md"

    monkeypatch.setattr(fetch, "execute", spy)
    args = argparse.Namespace(run_dir=str(tmp_path), root=tmp_path, url="u", question="q")
    assert fetch.run_command(args) == 0
    assert seen["kw"] == {}
