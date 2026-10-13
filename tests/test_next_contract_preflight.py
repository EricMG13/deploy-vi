"""Generated contract replacements prove preflight order without nonregular opens."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from test_next import approved, blocked

from rbotlib import dispatch, state
from rbotlib import next as next_step
from rbotlib.cli import main
from rbotlib.inventory import RunError
from rbotlib.rules import RBOT_ROOT, Rules


def extra_contract(root: Path, name: str = "EXTRA") -> Path:
    target = root / "modules" / name / "contract.json"
    target.parent.mkdir()
    data = json.loads((root / "modules/CP-5/contract.json").read_text())
    data["module_id"] = name
    target.write_text(json.dumps(data))
    return target


def branch_run(tmp_path: Path, root: Path, branch: str) -> Path:
    run = approved(tmp_path, root)
    if branch == "host":
        blocked(run, root, "CP-1")
        for module in ("CP-1A", "CP-1B", "CP-1D"):
            state.set_status(run, module, "failed", "generated optional failure")
    elif branch == "done":
        for module in state.read(run)["plan"][1:]:
            if state.read(run)["steps"][module]["status"] == "pending":
                state.set_status(run, module, "failed", "generated terminal failure")
    return run


@pytest.mark.parametrize("branch", ["module", "host", "done"])
@pytest.mark.parametrize("public", [False, True], ids=["library", "public"])
def test_regular_extra_contract_keeps_exact_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], branch: str, public: bool
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    extra_contract(root)
    run = branch_run(tmp_path, root, branch)
    before = state.read(run)["steps"]
    if public:
        capsys.readouterr()
        assert main(["--root", str(root), "next", "--run", str(run)]) == 0
        out = capsys.readouterr()
        assert not out.err
        selected = json.loads(out.out)
    else:
        selected = next_step.select(run, root)
    assert selected["kind"] == branch
    assert selected["step"] == {"module": "CP-1", "host": "MODEL", "done": None}[branch]
    after = state.read(run)["steps"]
    assert all(after[m] == s for m, s in before.items() if s["status"] != "pending")
    if selected["step"] is not None:
        assert after[selected["step"]] == before[selected["step"]]
    assert (run / state.LOCK).exists()


def replace_contract(target: Path, external: Path, kind: str) -> Path:
    tmp_path = external.parent
    root = target.parents[2]
    if kind == "late":
        target = root / "modules/LATE/contract.json"
        target.parent.mkdir()
    elif kind == "parent":
        folder = target.parent
        folder.rename(tmp_path / "generated-module")
        folder.symlink_to(tmp_path / "generated-module", target_is_directory=True)
    else:
        target.unlink()
    if kind in ("symlink", "internal", "late"):
        target.symlink_to(external)
    elif kind == "hardlink":
        target.hardlink_to(external)
    elif kind == "directory":
        target.mkdir()
    elif kind == "fifo":
        os.mkfifo(target)
    return target


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param((b, p), id=f"{name}-{b}")
        for b in ("module", "host", "done")
        for p, name in ((False, "library"), (True, "public"))
    ],
)
@pytest.mark.parametrize(
    "kind", ["symlink", "internal", "hardlink", "parent", "directory", "fifo", "late"]
)
def test_unsupported_extra_contract_refuses_before_content_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    scenario: tuple[str, bool],
    kind: str,
) -> None:
    branch, public = scenario
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    target = extra_contract(root)
    run = branch_run(tmp_path, root, branch)
    external = (root if kind == "internal" else tmp_path) / "generated-contract.json"
    external_bytes = target.read_bytes()
    external.write_bytes(external_bytes)
    target = replace_contract(target, external, kind)
    before = (run / state.STATE).read_bytes()
    sources = {p: p.read_bytes() for p in run.parent.parent.iterdir() if p.is_file()}
    evidence = {p: p.read_bytes() for p in run.rglob("*") if p.is_file() and "log" not in p.parts}
    reads: list[Path] = []
    actual_read = Path.read_bytes

    def guarded_read(path: Path) -> bytes:
        if path == target:
            reads.append(path)
            if kind in ("directory", "fifo"):
                raise AssertionError("unsupported read sentinel: refused before opening")
        return actual_read(path)

    capsys.readouterr()
    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", guarded_read)
        try:
            if public:
                assert main(["--root", str(root), "next", "--run", str(run)]) == 1
                out = capsys.readouterr()
                assert not out.out and str(target.parent) in out.err
            else:
                with pytest.raises(RunError, match=r"symlink|hard link|regular file"):
                    next_step.select(run, root)
        finally:
            assert not reads, "contract content reached before safe regular-file refusal"
    assert (run / state.STATE).read_bytes() == before
    assert all(p.read_bytes() == data for p, data in evidence.items())
    assert {p for p in run.rglob("*") if p.is_file() and "log" not in p.parts} == set(evidence)
    assert (run / state.LOCK).exists()
    assert all(p.read_bytes() == data for p, data in sources.items())
    assert external.read_bytes() == external_bytes


@pytest.mark.parametrize("branch", ["module", "host", "done"])
def test_complete_lexical_preflight_precedes_phase_under_writer_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, branch: str
) -> None:
    root = shutil.copytree(RBOT_ROOT, tmp_path / "root")
    extra_contract(root)
    run = branch_run(tmp_path, root, branch)
    candidates = {str(p.relative_to(root)) for p in (root / "modules").glob("*/contract.json")}
    guarded: set[str] = set()
    actual_file, actual_phase = dispatch._file, next_step._phase

    def observe_file(folder: Path, name: str) -> Path:
        if folder == root and name in candidates:
            assert (run / state.LOCK).exists()
            guarded.add(name)
        return actual_file(folder, name)

    def observe_phase(run: Path, root: Path, record: state.Record, rules: Rules) -> None:
        assert guarded == candidates and (run / state.LOCK).exists()
        actual_phase(run, root, record, rules)

    monkeypatch.setattr(dispatch, "_file", observe_file)
    monkeypatch.setattr(next_step, "_phase", observe_phase)
    assert next_step.select(run, root)["kind"] == branch
    assert (run / state.LOCK).exists()
