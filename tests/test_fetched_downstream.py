"""Fetched evidence downstream (Plan 10, rulings R9 and R10): dispatch, accept and import."""

from __future__ import annotations

import json
import shlex
import shutil
from pathlib import Path

import proxy_isolated
import pytest
from test_accept import accept, send
from test_approve import PRIOR, _approve, _ready
from test_dispatch import message
from test_dispatch_boundaries import blocked

from rbotlib import dispatch, fetch, fetched, state
from rbotlib.corpus import CorpusError
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT

URL = "http://pub.example/page"
SAVED = "fetched/01-pub.example.md"
BODY = "Pub Example reports demand recovering in the second quarter of 2026.\n"
EXCERPT = "demand recovering in the second quarter"
NO_FETCH = "No fetching is authorized by this installed contract."
PACK_ONLY = "Fetching is not available on this host: work from the Source Pack alone"


def build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    env: str | None = "1",
    questions: bool = True,
) -> tuple[Path, Path]:
    """An approved real-contract run with RQ-1 approved, CP-DR planned and CP-1A accepted."""
    if env is None:
        monkeypatch.delenv("RBOT_FETCH", raising=False)
    else:
        monkeypatch.setenv("RBOT_FETCH", env)
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    run = _ready(root, tmp_path, rows=PRIOR if questions else "")
    assert _approve(root, run) == 0
    run = run.parent / "20261011-acme-full-credit-assessment"
    if questions:
        blocked(run, root, "CP-1A")
    return root, run


def save_page(run: Path, body: str = BODY, question: str = "RQ-1") -> Path:
    front = {
        "url": URL,
        "retrieved": "2026-10-17",
        "question": question,
        "content_type": "text/html",
    }
    path = run / SAVED
    path.parent.mkdir(exist_ok=True)
    path.write_text(fetched.render(front, body), encoding="utf-8")
    return path


def table(name: str, head: str, row: str) -> str:
    bar = "|" + "---|" * (head.count("|") - 1)
    return f"<!-- table: {name} -->\n{head}\n{bar}\n{row}\n"


def cpdr(run: Path, source: str = SAVED, locator: str = f"{URL} retrieved 2026-10-17") -> str:
    cite = "| C1 | " + f"{source} | {locator} | {EXCERPT} |"
    tables = [
        table(
            "cpdr.questions",
            "| question_id | question | consumer_module | status |",
            "| RQ-1 | Is demand recovering? | CP-2 | Answered |",
        ),
        table(
            "cpdr.evidence",
            "| evidence_id | question_id | claim | claim_type | source_type | source_date "
            "| independence | cite |",
            "| E1 | RQ-1 | Demand is recovering in the second quarter of 2026 | fact | Fetched "
            "| 2026-10-17 | Pub Example (publisher) | [C1] |",
        ),
        table(
            "cpdr.answers",
            "| question_id | answer | evidence_ids | contrary_evidence | uncertainty "
            "| consequence_for | cite |",
            "| RQ-1 | Demand is recovering [C1] | E1 | none found: one page read | One page "
            "| CP-2: read demand as recovering | [C1] |",
        ),
        table(
            "cpdr.sector_view",
            "| sector | outlook | drivers | competitors | regulation | risks | cite |",
            "| Casinos | Neutral | Demand recovering [C1] | none stated | none stated "
            "| One source | [C1] |",
        ),
    ]
    front = (
        f"---\nmodule_id: CP-DR\nrun_id: {run.name}\nissuer_id: ACME\nanalysis_date: 2026-10-02\n"
        "qa_status: Pass\ninputs: CP-0, CP-1A\n---\n\n"
    )
    return (
        front
        + "## Analysis\n\nDemand is recovering [C1].\n\n## Tables\n\n"
        + "\n".join(tables)
        + "\n## Gaps\n\n- None.\n\n## Citations\n\n"
        + table("citations", "| id | source | locator | excerpt |", cite)
    )


def write(run: Path, text: str) -> None:
    (run / "handoffs/CP-DR.md").write_text(text, encoding="utf-8")


def fetch_state(run: Path) -> dict[str, str]:
    return dict(state.read(run)["approval"])


def test_accept_cpdr_citing_a_saved_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, run = build(tmp_path, monkeypatch)
    save_page(run)
    write(run, cpdr(run))
    send(run, root, "CP-DR")
    (run / "stray.md").write_text("not detected by accept\n", encoding="utf-8")
    assert accept(run, root, "CP-DR") == 0
    assert state.read(run)["steps"]["CP-DR"]["status"] == "accepted"


def test_accept_refuses_an_edited_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, run = build(tmp_path, monkeypatch)
    page = save_page(run)
    write(run, cpdr(run))
    send(run, root, "CP-DR")
    page.write_text(page.read_text(encoding="utf-8") + "edited\n", encoding="utf-8")
    capsys.readouterr()
    assert accept(run, root, "CP-DR") == 1
    assert SAVED in capsys.readouterr().out
    assert state.read(run)["steps"]["CP-DR"]["status"] != "accepted"


def test_downstream_dispatch_lists_the_qualified_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, run = build(tmp_path, monkeypatch)
    page = save_page(run)
    write(run, cpdr(run))
    send(run, root, "CP-DR")
    assert accept(run, root, "CP-DR") == 0
    code, text = message(run, root, "CP-5", capsys)
    assert code == 0
    assert f"Qualified fetched files: {json.dumps([str(page)])}" in text
    # an edited page: the pure qualification refuses, naming the file ...
    page.write_text(page.read_text(encoding="utf-8") + "edited\n", encoding="utf-8")
    with pytest.raises(RunError, match=SAVED):
        dispatch.qualified_message(run, root, "CP-5", state.read(run))
    # ... and the reconciling dispatch fails CP-DR for it and lists no page
    text = dispatch.prepare_message(run, root, "CP-5", None)
    assert "Qualified fetched files: []" in text and '"CP-DR: failed"' in text
    assert SAVED in state.read(run)["steps"]["CP-DR"]["reason"]


def test_a_run_without_cpdr_in_its_plan_gets_no_new_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, run = build(tmp_path, monkeypatch, questions=False)
    assert state.read(run)["steps"]["CP-DR"]["status"] == "skipped"
    code, text = message(run, root, "CP-1", capsys)
    assert code == 0 and "Qualified fetched files" not in text and NO_FETCH in text
    root, run = build(tmp_path / "with", monkeypatch)
    code, text = message(run, root, "CP-DR", capsys)
    assert code == 0 and "Qualified fetched files: []" in text


def test_cpdr_dispatch_holds_the_grant_only_when_recorded_and_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, run = build(tmp_path, monkeypatch)
    assert fetch_state(run)["fetch"] == "on" and fetch.available({"RBOT_FETCH": "1"})
    code, text = message(run, root, "CP-DR", capsys)
    command = f"python {root}/scripts/rbot.py fetch --run {run} --url <URL> --question <id>"
    assert code == 0 and f"Fetch command: {json.dumps(command)}" in text
    assert f"Approved research questions: {json.dumps(['RQ-1'])}" in text
    assert json.dumps(str(run / "fetched")) in text and NO_FETCH not in text
    assert str(run / "handoffs/CP-DR.md") in text
    monkeypatch.delenv("RBOT_FETCH")  # recorded on, but the variable is gone
    code, text = message(run, root, "CP-DR", capsys)
    assert code == 0 and PACK_ONLY in text and "Fetch command" not in text
    assert str(run / "fetched") not in text and NO_FETCH not in text


def test_cpdr_dispatch_with_the_record_off_holds_no_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, run = build(tmp_path, monkeypatch, env=None)
    assert fetch_state(run)["fetch"] == "off"
    monkeypatch.setenv("RBOT_FETCH", "1")  # set now, but the recorded mode is off
    code, text = message(run, root, "CP-DR", capsys)
    assert code == 0 and PACK_ONLY in text and "Fetch command" not in text
    assert str(run / "fetched") not in text


def test_isolated_import_copies_the_fetched_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source = build(tmp_path / "src", monkeypatch)
    save_page(source)
    (source / "fetched/note.txt").write_bytes(b"\xff not a page\n")
    write(source, cpdr(source))
    send(source, root, "CP-DR")
    assert accept(source, root, "CP-DR") == 0
    (tmp_path / "iso").mkdir()
    root2, run = build(tmp_path / "iso", monkeypatch)
    assert message(run, root2, "CP-DR", capsys)[0] == 0
    selected = {"step": "CP-DR", "dispatch": "dispatch/CP-DR.md"}
    src = proxy_isolated.Source(source.name, str(source), source / "handoffs", {})

    def native(target: Path, command: str, flags: list[str] | None) -> str:
        from rbotlib.cli import main

        assert main(["--root", str(root2), command, "--run", str(target), *(flags or [])]) in (0, 3)
        return ""

    proxy_isolated.import_module(run, selected, src, native)
    for name in ("01-pub.example.md", "note.txt"):
        assert (run / "fetched" / name).read_bytes() == (source / "fetched" / name).read_bytes()
    code, text = message(run, root2, "CP-5", capsys)
    assert code == 0 and json.dumps([str(run / SAVED)]) in text


def test_isolated_import_refuses_a_symlinked_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, source = build(tmp_path / "src", monkeypatch)
    save_page(source)
    (source / "fetched").rename(tmp_path / "real-fetched")
    (source / "fetched").symlink_to(tmp_path / "real-fetched", target_is_directory=True)
    run = tmp_path / "dest"
    run.mkdir()
    src = proxy_isolated.Source(source.name, str(source), source / "handoffs", {})
    with pytest.raises(CorpusError, match="symlinked fetched/ folder"):
        proxy_isolated.import_fetched(run, src)
    assert not (run / "fetched").exists()


def test_the_fetch_command_survives_spaces_in_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, run = build(tmp_path / "a b", monkeypatch)
    assert " " in str(root) and " " in str(run)
    text = message(run, root, "CP-DR", capsys)[1]
    line = next(x for x in text.splitlines() if x.startswith("Fetch command: "))
    command = json.loads(line.removeprefix("Fetch command: "))
    assert shlex.split(command.replace("<URL>", URL).replace("<id>", "RQ-1")) == [
        "python", str(root / "scripts/rbot.py"), "fetch", "--run", str(run),
        "--url", URL, "--question", "RQ-1",
    ]  # fmt: skip
