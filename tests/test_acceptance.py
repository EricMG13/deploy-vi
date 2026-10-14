"""`scripts/acceptance.py check`: the run bar R1-R8 on finished fixture runs (Plan 08 task 08.4a).

The baseline is Plan 07's `complete_run` (hand-written Handoffs through the real native commands,
never live model evidence). `rbot render` is not in this branch, so `report.html` and `report.md`
are written by the fixture (the embedded document is the real `run_json.build`) and the report
fields go through `state.update`: R2 is exercised on those files, not on a real render's output.
Each case flips exactly one row of the baseline.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable, Iterator
from pathlib import Path

import acceptance
import pytest
import report_run
from report_run import complete_run

from rbotlib import attempts, dispatch, state
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


def flipped(base: Verdicts, got: Verdicts) -> set[str]:
    return {i for i in base if got[i][0] != base[i][0]}


@pytest.fixture(scope="module")
def run(corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory) -> Path:
    return finished(corpus_pack, tmp_path_factory.mktemp("accepted"))


@pytest.fixture(scope="module")
def base(run: Path) -> Verdicts:
    return verdicts(run)


@pytest.fixture(scope="module")
def failed_run(
    corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory
) -> Path:
    return finished(corpus_pack, tmp_path_factory.mktemp("failed"), fail="CP-1B")


@pytest.fixture
def restore(run: Path) -> Iterator[Callable[[Path], None]]:
    """Remember a file's bytes; put them back after the case (the run is shared)."""
    saved: dict[Path, bytes] = {}

    def keep(path: Path) -> None:
        saved[path] = path.read_bytes()

    yield keep
    for path, data in saved.items():
        path.write_bytes(data)


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
    data = page.read_bytes()
    page.unlink()
    try:
        got = verdicts(run)
    finally:
        page.write_bytes(data)
    assert flipped(base, got) == {"R2"} and "report.html is missing" in got["R2"][2]


@pytest.mark.parametrize(
    "edit,why",
    [
        (lambda t: t.replace('id="rbot-run"', 'id="other"'), "#rbot-run"),
        (lambda t: t.replace("<main>", '<img src="https://x.example/a.png"><main>'), "http(s)"),
        (lambda t: t.replace("<main>", "<main>edited"), "sha256 differs"),
    ],
)
def test_report_html_defects_fail_r2(
    run: Path, restore: Callable[[Path], None], edit: Callable[[str], str], why: str
) -> None:
    page = run / "report.html"
    restore(page)
    page.write_text(edit(page.read_text(encoding="utf-8")), encoding="utf-8")
    record = state.read(run)
    if why != "sha256 differs":  # keep the recorded digest true so the named defect is the cause
        record["report"]["html_sha256"] = hashlib.sha256(page.read_bytes()).hexdigest()
    result = acceptance.r2(run, record)
    assert result[1] == "FAIL" and why in result[3]


def test_failed_step_fails_r3_and_r7_stays_consistent(failed_run: Path) -> None:
    got = verdicts(failed_run)
    assert got["R3"][0] == "FAIL" and "failed: CP-1B" in got["R3"][2]
    assert got["R7"][0] == "PASS"
    assert acceptance.main(["check", "--run", str(failed_run), "--pack-id", PACK]) == 1


def test_failed_step_missing_from_limitations_fails_r7(
    failed_run: Path, restore: Callable[[Path], None]
) -> None:
    page = failed_run / "report.html"
    restore(page)
    doc = run_json.build(failed_run, RBOT_ROOT, NOW)
    doc["limitations"]["unforeseen"] = [
        x for x in doc["limitations"]["unforeseen"] if x.get("step") != "CP-1B"
    ]
    page.write_text(f"<html>{embed_json(doc)}</html>", encoding="utf-8")
    scored = acceptance.score_steps(failed_run, state.read(failed_run))
    result = acceptance.r7(failed_run, state.read(failed_run), scored)
    assert result[1] == "FAIL" and "CP-1B:failed" in result[3]


def test_model_limitations_and_faults_must_be_on_the_tab(
    run: Path, tmp_path: Path, restore: Callable[[Path], None]
) -> None:
    page = run / "report.html"
    restore(page)
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


def test_corrupt_prepared_excerpt_fails_only_r4(
    run: Path, base: Verdicts, restore: Callable[[Path], None]
) -> None:
    # CP-1's citations name many prepared files; blank every one so the ratio falls under 0.95.
    for path in (run / "prepared").rglob("*.txt"):
        restore(path)
        path.write_text("corrupted", encoding="utf-8")
    got = verdicts(run)
    assert flipped(base, got) == {"R4"}, got
    assert "below 0.95" in got["R4"][2]


def test_dropped_facility_row_fails_only_r5(
    corpus_pack: Callable[[str], Path], tmp_path_factory: pytest.TempPathFactory, base: Verdicts
) -> None:
    short = finished(
        corpus_pack, tmp_path_factory.mktemp("short"), drop_row_of="snapshot.instrument_levels"
    )
    got = verdicts(short)
    assert flipped(base, got) == {"R5"}, got
    before, after = (int(x.split("/")[0]) for x in (base["R5"][1], got["R5"][1]))
    assert after < before and got["R5"][1].split("/")[1] == base["R5"][1].split("/")[1]


def test_altered_pack_byte_fails_only_r6(
    run: Path, base: Verdicts, restore: Callable[[Path], None]
) -> None:
    pack = Path(state.read(run)["pack_root"])
    first = json.loads((run / "inventory.json").read_text(encoding="utf-8"))["files"][0]["path"]
    source = pack / first  # the inventory's first file: the section parse must not skip it
    restore(source)
    source.write_bytes(source.read_bytes() + b" ")
    got = verdicts(run)
    assert flipped(base, got) == {"R6"} and first in got["R6"][2]


def test_stripped_receipt_fails_only_r8(run: Path, base: Verdicts) -> None:
    folder = run / "validate/history/CP-1"
    keep = {p: p.read_bytes() for p in folder.iterdir()}
    receipts = [
        p for p in folder.iterdir() if json.loads(p.read_text())["event"] == "dispatch_report"
    ]
    for p in receipts:
        p.unlink()
    try:
        got = verdicts(run)
    finally:
        for p, data in keep.items():
            p.write_bytes(data)
    assert flipped(base, got) == {"R8"}, got
    assert "CP-1 (no receipt)" in got["R8"][2]


def test_live_run_leaves_the_model_label_unmeasured(
    run: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    got = verdicts(run, live=True)
    assert got["R8"][0] == "NOT MEASURED" and "chat export" in got["R8"][2]
    assert acceptance.main(["check", "--run", str(run), "--pack-id", PACK, "--live"]) == 1


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
