"""`scripts/acceptance.py check`: the run bar R1-R8 on finished fixture runs (Plan 08 task 08.4a).

The baseline is Plan 07's `complete_run` (hand-written Handoffs through the real native commands,
never live model evidence). `rbot render` is not in this branch, so `report.html` and `report.md`
are written by the fixture (the embedded document is the real `run_json.build`) and the report
fields go through `state.update`: R2 is exercised on those files, not on a real render's output.
Each case flips exactly one row of the baseline, on a fresh copy of the pack put back from a
snapshot; three runs are built once per module (accepted, failed CP-1B, dropped rows).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import acceptance
import pytest
import report_run
from report_run import complete_run

from rbotlib import attempts, dispatch, state
from rbotlib.inventory import RunError
from rbotlib.report import run_json
from rbotlib.report.html_parts import embed_json
from rbotlib.rules import RBOT_ROOT

PACK = "czr-2026q2-primary"
LABEL = "fixture-model"
NOW = "2026-10-14T00:00:00+00:00"
FIT_ROW = "| FIT | minimum limits"
# CP-5's fixture lists limitations for four steps; the other Restricted steps are added so the
# baseline carries every Restricted step on the Limitations tab (R7).
EXTRA_LIMITS = "".join(
    f"| {m} | fixture limitation | none | fixture |\n"
    for m in ("CP-1", "CP-1B", "CP-1D", "CP-2", "CP-6")
)
DROPPED = 5  # of CP-3 instrument_levels' 7 facility rows: 45 of the 335 measured cells
Verdicts = dict[str, tuple[str, str, str]]


def send(run: Path, root: Path, module: str = "CP-0", name: str = "fixture-send") -> None:
    """test_accept.send with a model label on the receipt (proxy runs record one)."""
    text = dispatch.prepare_message(run, root, module, None)
    digest = hashlib.sha256(text.encode()).hexdigest()
    receipt = attempts.DispatchReceipt(name, "fixture-controller", digest, model=LABEL)
    attempts.register_dispatch(run, root, module, receipt)


def drop_first_row(text: str, table: str) -> str:
    lines = text.splitlines(keepends=True)
    at = next(i for i, x in enumerate(lines) if x.strip() == f"<!-- table: {table} -->")
    del lines[at + 3]  # marker, header, separator, then the first data row
    return "".join(lines)


def write_report(run: Path) -> None:
    """report.html and report.md as a render would leave them, plus the state's report fields."""
    page = (
        f"<html><body><main>{embed_json(run_json.build(run, RBOT_ROOT, NOW))}</main></body></html>"
    )
    (run / "report.html").write_text(page, encoding="utf-8")
    (run / "report.md").write_text("# Report\n", encoding="utf-8")

    def change(record: state.Record) -> None:
        record["report"] = {
            "written_at": NOW,
            "html_sha256": hashlib.sha256((run / "report.html").read_bytes()).hexdigest(),
            "md_sha256": hashlib.sha256((run / "report.md").read_bytes()).hexdigest(),
        }

    state.update(run, change)


def finished(
    corpus_pack: Callable[[str], Path],
    tmp: Path,
    fail: str | None = None,
    drop_row_of: str | None = None,
) -> Path:
    original = report_run.fixture_text

    def text(module: str, run: Path) -> str:
        got = original(module, run)
        if module == "CP-5":
            got = got.replace(FIT_ROW, EXTRA_LIMITS + FIT_ROW)
        for _ in range(DROPPED if module == "CP-3" and drop_row_of else 0):
            got = drop_first_row(got, str(drop_row_of))
        return got

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(report_run, "fixture_text", text)
        patch.setattr(report_run, "send", send)
        run = complete_run(corpus_pack, tmp, fail=fail)
    write_report(run)
    return run


def verdicts(run: Path, live: bool = False) -> Verdicts:
    return {i: (v, m, e) for i, v, m, e in acceptance.check(run, PACK, live)}


def cli(run: Path, capsys: pytest.CaptureFixture[str], *extra: str) -> tuple[int, Verdicts]:
    """One `check` through main (its exit code and printed rows): a check costs ~30 s."""
    code = acceptance.main(["check", "--run", str(run), "--pack-id", PACK, *extra])
    rows = [x.split(" | ", 3) for x in capsys.readouterr().out.splitlines()]
    return code, {r[0]: (r[1], r[2], r[3]) for r in rows}


def flipped(base: Verdicts, got: Verdicts) -> set[str]:
    return {i for i in base if got[i][0] != base[i][0]}


class Built(NamedTuple):
    """A finished run and an untouched copy of its pack, to put back before each case."""

    run: Path
    pristine: Path


def build(
    corpus_pack: Callable[[str], Path], factory: pytest.TempPathFactory, name: str, **kw: str
) -> Built:
    run = finished(corpus_pack, factory.mktemp(name), **kw)
    pristine = factory.mktemp(f"{name}-pristine") / "pack"
    shutil.copytree(run.parent.parent, pristine, symlinks=True)
    return Built(run, pristine)


def reset(built: Built) -> Path:
    """Give the case a fresh copy of the pack: every file is put back from the snapshot and any
    other file removed. A copy at another path is not possible (the host steps' evidence binds
    the pack's absolute path), and `.approve.lock` is left in place (its inode is the run's
    owner identity)."""
    pack = built.run.parent.parent
    want = {p.relative_to(built.pristine) for p in built.pristine.rglob("*") if not p.is_dir()}
    for path in sorted(pack.rglob("*"), reverse=True):
        if path.is_dir() and not (built.pristine / path.relative_to(pack)).is_dir():
            shutil.rmtree(path)
        elif not path.is_dir() and path.relative_to(pack) not in want:
            path.unlink()
    for rel in want:
        if rel.name == ".approve.lock":
            continue
        (pack / rel).parent.mkdir(parents=True, exist_ok=True)
        source = built.pristine / rel
        if not (pack / rel).is_file() or (pack / rel).read_bytes() != source.read_bytes():
            shutil.copy2(source, pack / rel)
    return built.run


@pytest.fixture(scope="module")
def accepted(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Built:
    return build(corpus_pack, tmp_path_factory, "accepted")


@pytest.fixture(scope="module")
def failed(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Built:
    return build(corpus_pack, tmp_path_factory, "failed", fail="CP-1B")


@pytest.fixture(scope="module")
def short(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Built:
    return build(corpus_pack, tmp_path_factory, "short", drop_row_of="snapshot.instrument_levels")


@pytest.fixture
def run(accepted: Built) -> Path:
    return reset(accepted)


@pytest.fixture
def failed_run(failed: Built) -> Path:
    return reset(failed)


@pytest.fixture(scope="module")
def base(accepted: Built) -> Verdicts:
    return verdicts(reset(accepted))


def test_baseline_passes_every_row(base: Verdicts) -> None:
    assert {k: v[0] for k, v in base.items()} == dict.fromkeys(
        ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"), "PASS"
    ), base


def test_report_is_a_table_and_exit_is_zero(run: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert acceptance.main(["check", "--run", str(run), "--pack-id", PACK]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [x.split(" | ")[:2] for x in lines] == [[f"R{n}", "PASS"] for n in range(1, 9)]
    assert all(len(x.split(" | ")) == 4 for x in lines)


def test_missing_report_html_fails_only_r2(run: Path, base: Verdicts) -> None:
    page = run / "report.html"
    page.unlink()
    got = verdicts(run)
    assert flipped(base, got) == {"R2"} and "report.html is missing" in got["R2"][2]


@pytest.mark.parametrize(
    "edit,why",
    [
        (lambda t: t.replace('id="rbot-run"', 'id="other"'), "#rbot-run"),
        (lambda t: t.replace("<main>", '<img src="https://x.example/a.png"><main>'), "http(s)"),
        (lambda t: t.replace("<main>", "<main>edited"), "sha256 differs"),
    ],
)
def test_report_html_defects_fail_r2(run: Path, edit: Callable[[str], str], why: str) -> None:
    page = run / "report.html"
    page.write_text(edit(page.read_text(encoding="utf-8")), encoding="utf-8")
    record = state.read(run)
    if why != "sha256 differs":  # keep the recorded digest true so the named defect is the cause
        record["report"]["html_sha256"] = hashlib.sha256(page.read_bytes()).hexdigest()
    result = acceptance.r2(run, record)
    assert result[1] == "FAIL" and why in result[3]


def test_failed_step_fails_r3_and_r7_stays_consistent(
    failed_run: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, got = cli(failed_run, capsys)
    assert code == 1
    assert got["R3"][0] == "FAIL" and "failed: CP-1B" in got["R3"][2]
    assert got["R7"][0] == "PASS"


def test_failed_step_missing_from_limitations_fails_r7(
    failed_run: Path,
) -> None:
    page = failed_run / "report.html"
    doc = run_json.build(failed_run, RBOT_ROOT, NOW)
    doc["limitations"]["unforeseen"] = [
        x for x in doc["limitations"]["unforeseen"] if x.get("step") != "CP-1B"
    ]
    page.write_text(f"<html>{embed_json(doc)}</html>", encoding="utf-8")
    scored = acceptance.score_steps(failed_run, state.read(failed_run))
    result = acceptance.r7(failed_run, state.read(failed_run), scored)
    assert result[1] == "FAIL" and "CP-1B:failed" in result[3]


def test_model_limitations_and_faults_must_be_on_the_tab(run: Path, tmp_path: Path) -> None:
    page = run / "report.html"
    doc = run_json.build(run, RBOT_ROOT, NOW)
    doc["limitations"]["unforeseen"] = []
    page.write_text(f"<html>{embed_json(doc)}</html>", encoding="utf-8")
    result = acceptance.r7(run, state.read(run), acceptance.score_steps(run, state.read(run)))
    assert result[1] == "FAIL" and "model: No projections" in result[3]
    (tmp_path / "model.json").write_text(
        json.dumps({"limitation_details": [], "reconciliation_faults": ["debt does not tie"]}),
        encoding="utf-8",
    )
    assert acceptance._model_lost(tmp_path, {"unforeseen": []}) == ["debt does not tie"]
    assert acceptance._model_lost(tmp_path, {"unforeseen": ["debt does not tie"]}) == []


def test_corrupt_prepared_excerpt_fails_only_r4(run: Path, base: Verdicts) -> None:
    # CP-1's citations name many prepared files; blank every one so the ratio falls under 0.95.
    for path in (run / "prepared").rglob("*.txt"):
        path.write_text("corrupted", encoding="utf-8")
    got = verdicts(run)
    assert flipped(base, got) == {"R4"}, got
    assert "below 0.95" in got["R4"][2]


def test_dropped_facility_row_fails_only_r5(short: Built, base: Verdicts) -> None:
    got = verdicts(short.run)
    assert flipped(base, got) == {"R5"}, got
    before, after = (int(x.split("/")[0]) for x in (base["R5"][1], got["R5"][1]))
    assert after < before and got["R5"][1].split("/")[1] == base["R5"][1].split("/")[1]


def test_altered_pack_byte_fails_only_r6(run: Path, base: Verdicts) -> None:
    pack = Path(state.read(run)["pack_root"])
    first = json.loads((run / "inventory.json").read_text(encoding="utf-8"))["files"][0]["path"]
    source = pack / first  # the inventory's first file: the section parse must not skip it
    source.write_bytes(source.read_bytes() + b" ")
    got = verdicts(run)
    assert flipped(base, got) == {"R6"} and first in got["R6"][2]


def test_stripped_receipt_fails_only_r8(run: Path, base: Verdicts) -> None:
    folder = run / "validate/history/CP-1"
    receipts = [
        p for p in folder.iterdir() if json.loads(p.read_text())["event"] == "dispatch_report"
    ]
    for p in receipts:
        p.unlink()
    got = verdicts(run)
    assert flipped(base, got) == {"R8"}, got
    assert "CP-1 (no receipt)" in got["R8"][2]


def test_live_run_leaves_the_model_label_unmeasured(
    run: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, got = cli(run, capsys, "--live")
    assert got["R8"][0] == "NOT MEASURED" and "chat export" in got["R8"][2] and code == 1


def test_missing_model_label_fails_a_proxy_run_r8(
    run: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(attempts, "read_history", lambda r, m, s: [])
    record = state.read(run)
    assert acceptance.r8(run, record, acceptance.score_steps(run, record), live=False)[1] == "FAIL"


def test_unreadable_run_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    shutil.copytree(RBOT_ROOT / "modules", tmp_path / "not-a-run")
    assert acceptance.main(["check", "--run", str(tmp_path / "not-a-run")]) == 2
    assert capsys.readouterr().out.startswith("acceptance: ")


# --- `ingest` (Plan 08 task 08.4b) -------------------------------------------------------------
# The bundle's claude/ and gpt/ folders are both links to the one finished fixture run (a pack is
# bound to its absolute path, so a second run would cost another ~5 minute build); the cases
# differ in the checklist, install.txt, probes and manifest, which are written per case.

COMMIT = "c0ffee" * 6 + "c0ff"
TREE = "ab" * 20
MODEL_VALUES = {
    "picker_label": "{m} picker",
    "context_tokens": "128000",
    "skills_lists_rbot": "yes",
    "rbot_invoked": "yes",
    "turns_before_approval": "2",
    "questions_after_approval": "0",
    "subagents": "yes",
    "report_opened": "yes",
    "start_utc": "2026-10-14T09:00:00Z",
    "finish_utc": "2026-10-14T10:30:00Z",
}
COMMON_VALUES = {
    "package_sha256": "f" * 64,
    "os": "Windows 11",
    "editor": "VS Code",
    "editor_version": "1.99",
    "copilot_chat_version": "0.30",
    "execution_policy": "RemoteSigned",
    "python_cmd": "py",
    "python_version": "3.11.9",
    "wheels_install": "yes",
    "install_method": "ps1",
}
PROBE = "".join(f"## {n}. Section\nrecorded {n}\n\n" for n in range(1, 7))


def checklist_values(**override: str) -> dict[str, str]:
    values = dict(COMMON_VALUES)
    for model in ("claude", "gpt"):
        values |= {f"{model}_{k}": v.format(m=model) for k, v in MODEL_VALUES.items()}
    values["claude_resume_ok"] = "yes"
    return values | override


def make_bundle(tmp: Path, run_home: Path | None, **override: str) -> tuple[Path, Path]:
    """An evidence folder and a manifest of this checkout's SKILL, canon and MODULE files."""
    root = tmp / "rbot-v1-evidence-2026-10-14"
    root.mkdir()
    values = {k: v for k, v in checklist_values(**override).items() if v != "<absent>"}
    (root / "checklist.txt").write_text("".join(f"{k}: {v}\n" for k, v in values.items()))
    (root / "env.txt").write_text("PSVersion 5.1\n")
    (root / "install.txt").write_text(
        f'rbot 1.0.0 {COMMIT}\n  "runtime_tree": "{TREE}",\n0 problem(s)\n'
    )
    for model in ("claude", "gpt"):
        if run_home is None:  # layout only: the run is never read
            (root / model / "pack/rbot-runs/r1").mkdir(parents=True)
            (root / model / "chat.md").write_text("chat")
            (root / model / "rbot-probe-result.md").write_text(PROBE)
        else:
            root.joinpath(model).symlink_to(run_home, target_is_directory=True)
    if run_home is not None:
        (run_home / "chat.md").write_text("chat")
        (run_home / "rbot-probe-result.md").write_text(PROBE)
    files = [
        "SKILL.md",
        "canon.md",
        *(
            p.relative_to(RBOT_ROOT).as_posix()
            for p in sorted(RBOT_ROOT.glob("modules/*/MODULE.md"))
        ),
    ]
    hashes = {f"rbot/{f}": hashlib.sha256((RBOT_ROOT / f).read_bytes()).hexdigest() for f in files}
    manifest = tmp / "MANIFEST.json"
    manifest.write_text(
        json.dumps({"commit": COMMIT, "runtime_tree": TREE, "files": hashes}), encoding="utf-8"
    )
    return root, manifest


def ingest(
    root: Path, manifest: Path, tmp: Path, capsys: pytest.CaptureFixture[str]
) -> tuple[int, str, dict[str, str]]:
    out = tmp / "docs/v1-work-pc-2026-10-14.md"
    argv = ["ingest", "--evidence", str(root), "--manifest", str(manifest), "--out", str(out)]
    code = acceptance.main(argv)
    printed = capsys.readouterr().out
    rows = {}
    if out.is_file():
        cells = [[c.strip() for c in x.split(" | ")] for x in out.read_text().splitlines()]
        rows = {
            c[0].lstrip("| "): c[3]
            for c in cells
            if len(c) >= 4 and c[0].startswith("| ") and c[0] != "| ID"
        }
    return code, printed, rows


@pytest.mark.parametrize(
    "override,why",
    [
        ({"gpt_subagents": "<absent>"}, "gpt_subagents"),
        ({"claude_resume_ok": "<absent>"}, "claude_resume_ok"),
        ({"gpt_resume_ok": "yes"}, "gpt_resume_ok"),
        ({"claude_context_tokens": "many"}, "claude_context_tokens"),
        ({"gpt_subagents": "maybe"}, "gpt_subagents"),
        ({"os": ""}, "os"),
        ({"claude_finish_utc": "2026-10-14T08:00:00Z"}, "before"),
    ],
)
def test_bad_checklist_is_bad_evidence(
    override: dict[str, str], why: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest = make_bundle(tmp_path, None, **override)
    code, printed, rows = ingest(root, manifest, tmp_path, capsys)
    assert code == 2 and why in printed and not rows


def test_duplicate_checklist_key_is_bad_evidence() -> None:
    text = "".join(f"{k}: {v}\n" for k, v in checklist_values().items())
    with pytest.raises(RunError, match="duplicate key 'os'"):
        acceptance.parse_checklist(text + "os: again\n")
    assert acceptance.parse_checklist(text)["python_cmd"] == "py"


def test_commit_mismatch_is_bad_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest = make_bundle(tmp_path, None)
    (root / "install.txt").write_text(f"rbot 1.0.0 {'1' * 40}\n{TREE}\n0 problem(s)\n")
    code, printed, rows = ingest(root, manifest, tmp_path, capsys)
    assert code == 2 and COMMIT in printed and not rows


def test_utf16_powershell_output_is_read(tmp_path: Path) -> None:
    text = f"rbot 1.0.0 {COMMIT}\r\n0 problem(s)\r\n"
    (tmp_path / "install.txt").write_bytes(b"\xff\xfe" + text.encode("utf-16-le"))
    assert acceptance.read_text(tmp_path / "install.txt") == text
    assert acceptance.VERSION_LINE.findall(text) == [COMMIT]


def test_missing_probe_section_is_bad_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest = make_bundle(tmp_path, None)
    (root / "gpt/rbot-probe-result.md").write_text(PROBE.replace("## 4. Section", "## x"))
    code, printed, _ = ingest(root, manifest, tmp_path, capsys)
    assert code == 2 and "section 4" in printed


@pytest.fixture
def home(accepted: Built) -> Path:
    return reset(accepted).parent.parent.parent


def test_passing_bundle_writes_the_record(
    home: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest = make_bundle(tmp_path, home)
    code, printed, rows = ingest(root, manifest, tmp_path, capsys)
    wanted = [f"L{n}" for n in range(1, 12)] + [
        f"R{n} ({m})" for m in ("claude", "gpt") for n in range(1, 9)
    ]
    assert {k: rows[k] for k in wanted} == dict.fromkeys(wanted, "PASS"), (printed, rows)
    assert code == 0
    record = (tmp_path / "docs/v1-work-pc-2026-10-14.md").read_text()
    assert COMMIT in record and TREE in record and "f" * 64 in record
    assert record.rstrip().splitlines()[-1].startswith("Not verified:")
    for model in ("claude", "gpt"):
        assert list((tmp_path / f"docs/v1-work-pc-2026-10-14/{model}").glob("*.md"))


def test_budget_below_the_dispatch_size_fails_only_l8(
    home: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest = make_bundle(tmp_path, home, gpt_context_tokens="1000")
    code, printed, rows = ingest(root, manifest, tmp_path, capsys)
    assert code == 1, printed
    assert {k for k, v in rows.items() if v != "PASS"} == {"L8"}
    record = (tmp_path / "docs/v1-work-pc-2026-10-14.md").read_text()
    assert "budget 400 bytes" in record and "51,200" in record
