from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from test_approve import TARGET, _approve, _ready

import rbotlib.approve as ap
import rbotlib.cp0 as cp0
from rbotlib import brief as rb
from rbotlib.cli import main
from rbotlib.contract import load_contract
from rbotlib.fsio import write_atomic
from rbotlib.handoff import parse
from rbotlib.rules import RBOT_ROOT, Rules, load_rules
from rbotlib.validate import check
from spec_fixture import SOURCES, build_tree
from test_grade import CLO, FILES, SYNTHETIC, _acme, _graded


@pytest.fixture
def root(tmp_path: Path, rules: Rules) -> Path:
    (tmp_path / "rbot").mkdir()
    return build_tree(tmp_path / "rbot", rules, SOURCES)


def test_second_publication_failure_restores_both_files_and_allows_retry(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run = _ready(root, tmp_path)
    before = {name: (run / name).read_bytes() for name in ("run-brief.md", "run-state.json")}
    real = os.replace
    failed = False

    def fail_state(src: object, dst: object) -> None:
        nonlocal failed
        if Path(str(dst)) == run / "run-state.json" and not failed:
            failed = True
            assert rb.approval(run) is not None  # real first publication already happened
            raise PermissionError(13, "state publication refused", str(dst))
        real(str(src), str(dst))

    monkeypatch.setattr(os, "replace", fail_state)
    capsys.readouterr()
    assert _approve(root, run) == 1
    assert capsys.readouterr().out.startswith("could not publish Approval (")
    assert failed
    assert before == {name: (run / name).read_bytes() for name in before}
    assert not [p for p in run.iterdir() if p.name.startswith(".approve-")]
    monkeypatch.undo()
    assert _approve(root, run) == 0
    assert (run.parent / TARGET / "log/rbot.log").read_text().endswith("\t0\n")


def test_second_staging_failure_publishes_nothing_and_allows_retry(
    root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = _ready(root, tmp_path)
    before = {name: (run / name).read_bytes() for name in ("run-brief.md", "run-state.json")}
    real, calls = write_atomic, 0

    def fail_second(path: Path, text: str) -> None:
        nonlocal calls
        calls += 1
        assert path.parent == run
        if calls == 2:
            raise PermissionError(13, "second staging write refused", str(path))
        real(path, text)

    monkeypatch.setattr(ap, "write_atomic", fail_second)
    assert _approve(root, run) == 1
    assert calls == 2
    assert before == {name: (run / name).read_bytes() for name in before}
    assert not [p for p in run.iterdir() if p.name.startswith(".approve-")]
    monkeypatch.undo()
    assert _approve(root, run) == 0


def test_failed_recovery_does_not_claim_nothing_was_approved(
    root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run = _ready(root, tmp_path)
    real, failed = os.replace, False

    def refuse(src: object, dst: object) -> None:
        nonlocal failed
        destination = Path(str(dst))
        if destination == run / "run-state.json":
            failed = True
            raise PermissionError(13, "state publication refused", str(dst))
        if failed and destination == run / "run-brief.md":
            raise PermissionError(13, "brief restoration refused", str(dst))
        real(str(src), str(dst))

    monkeypatch.setattr(os, "replace", refuse)
    capsys.readouterr()
    assert _approve(root, run) == 1
    out = capsys.readouterr().out
    assert out.startswith("could not publish Approval (")
    assert "recovery incomplete" in out and "brief restoration refused" in out
    assert "inspect the pending Run Brief and state before retrying" in out
    assert "nothing was approved" not in out
    assert rb.approval(run) is not None
    assert (run / ".approve.lock").exists()


@pytest.mark.parametrize("name", ["grading.json", "run-state.json"])
def test_approval_names_undecodable_input(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], name: str
) -> None:
    run = _ready(root, tmp_path)
    (run / name).write_bytes(b"\xff")
    capsys.readouterr()
    assert _approve(root, run) == 1
    captured = capsys.readouterr()
    assert f"{run / name}: no readable" in captured.out + captured.err
    assert run.is_dir() and (run / ".approve.lock").exists()


def _damage_inventory(path: Path, damage: str) -> None:
    data: dict[str, Any] = json.loads(path.read_text())
    if damage == "inventory-missing":
        path.unlink()
    elif damage == "inventory-utf8":
        path.write_bytes(b"\xff")
    elif damage == "inventory-list":
        path.write_text("[]")
    else:
        data["files"] = [None]
        path.write_text(json.dumps(data))


def _damage(run: Path, damage: str) -> str:
    index_path = run / "prepared/index.json"
    if damage.startswith("inventory"):
        _damage_inventory(run / "inventory.json", damage)
        return str(run / "inventory.json")
    index: dict[str, Any] = json.loads(index_path.read_text())
    expected = index_path
    if damage == "portfolios-missing":
        del index["portfolios"]
    elif damage == "portfolios-shape":
        index["portfolios"] = [None]
    else:
        record = next(r for r in index["files"] if r["path"] == "acme_credit_agreement.txt")
        if damage == "record-missing":
            index["files"].remove(record)
        elif damage == "record-sha-missing":
            del record["sha256"]
        elif damage == "record-pages-shape":
            record["pages"] = "one"
        elif damage == "text-missing":
            expected = run / record["prepared"]
            expected.unlink()
        else:
            raise AssertionError(damage)
    index_path.write_text(json.dumps(index))
    return str(expected)


@pytest.mark.parametrize(
    "damage",
    [
        "inventory-missing",
        "inventory-utf8",
        "inventory-list",
        "inventory-files-shape",
        "portfolios-missing",
        "portfolios-shape",
        "record-missing",
        "record-sha-missing",
        "record-pages-shape",
        "text-missing",
    ],
)
def test_damaged_cp0_run_inputs_have_named_errors_in_validate_and_grade(
    root: Path, tmp_path: Path, rules: Rules, capsys: pytest.CaptureFixture[str], damage: str
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    source = run / "handoffs/CP-0.md"
    assert parse(source.read_text()).tables["citations"].rows == []
    expected = _damage(run, damage)
    contract = load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules)
    code, found = check(source.read_text(), contract, rules, run)
    assert code == 1 and any(
        f.code == "run_error" and f.message.startswith(expected + ":") for f in found
    )
    capsys.readouterr()
    assert main(["validate", str(source), "--module", "CP-0", "--run", str(run)]) == 1
    assert expected in capsys.readouterr().err
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1
    out = capsys.readouterr().out
    assert expected in out and "Available" not in out


@pytest.mark.parametrize(
    "change",
    [
        "duplicate",
        "missing-field",
        "missing-tranche_id",
        "missing-value",
        "missing-status",
        "missing-cite",
    ],
)
def test_invalid_prefill_is_a_finding_before_brief_creation(
    root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], change: str
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    source = run / "handoffs/CP-0.md"
    text = source.read_text()
    if change == "duplicate":
        row = next(line for line in text.splitlines() if line.startswith("| issuer |"))
        text = text.replace(row, row + "\n" + row)
    else:
        lines = text.splitlines()
        start = lines.index("<!-- table: cp0.run_brief_prefill -->") + 1
        end = next(i for i in range(start, len(lines)) if not lines[i].startswith("|"))
        for n in range(start, end):
            cells = lines[n].split("|")
            del cells[
                parse(text)
                .tables["cp0.run_brief_prefill"]
                .columns.index(change.removeprefix("missing-"))
                + 1
            ]
            lines[n] = "|".join(cells)
        text = "\n".join(lines) + "\n"
    source.write_text(text)
    capsys.readouterr()
    assert main(["validate", str(source), "--module", "CP-0", "--run", str(run)]) == 2
    assert "prefill_invalid" in capsys.readouterr().out
    code, findings = check(
        text,
        load_contract(RBOT_ROOT / "modules/CP-0/contract.json", load_rules()),
        load_rules(),
        run,
    )
    assert code == 2
    reason = "duplicate" if change == "duplicate" else "missing"
    assert any(f.code == "prefill_invalid" and reason in f.message for f in findings)


@pytest.mark.parametrize(
    "field",
    [
        "portfolio_name",
        "strategy",
        "positions_file",
        "limits_file",
        "as_of_date",
        "extra-portfolio",
    ],
)
def test_cp0_copied_portfolio_fields_match_prepared_json(
    root: Path, tmp_path: Path, rules: Rules, capsys: pytest.CaptureFixture[str], field: str
) -> None:
    extra = {name: (SYNTHETIC / name).read_text() for name in CLO}
    classes = FILES | {
        name: ("portfolio", kind, "Test CLO I Ltd", "Yes") for name, kind in CLO.items()
    }
    run = _acme(tmp_path, extra)
    _graded(root, run, classes)
    source = run / "handoffs/CP-0.md"
    text = source.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| TEST_CLO_I |"))
    columns = parse(text).tables["cp0.portfolios"].columns
    cells = row.split("|")
    replacements = {
        "portfolio_name": "Wrong fund",
        "positions_file": "ghost.csv",
        "limits_file": "ghost-limits.csv",
        "as_of_date": "1999-01-01",
        "strategy": next(v for v in rules.scales["strategy"] if v != "CLO"),
    }
    if field == "extra-portfolio":
        source.write_text(text.replace(row, row + "\n" + row.replace("TEST_CLO_I", "UNKNOWN")))
        expected = "portfolio_mismatch: UNKNOWN is in cp0.portfolios"
    else:
        cells[columns.index(field) + 1] = " " + replacements[field] + " "
        source.write_text(text.replace(row, "|".join(cells)))
        expected = f"portfolio_mismatch: TEST_CLO_I: {field}"
    capsys.readouterr()
    assert main(["validate", str(source), "--module", "CP-0", "--run", str(run)]) == 2
    assert expected in capsys.readouterr().out
    assert main(["--root", str(root), "grade", "--run", str(run)]) == 1


def test_both_stages_are_synced_before_first_publication(
    root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = _ready(root, tmp_path)
    real_sync, real_replace = os.fsync, os.replace
    synced: list[tuple[int, int]] = []

    def sync(fd: int) -> None:
        observed = os.fstat(fd)
        assert observed.st_size > 0
        real_sync(fd)
        synced.append((observed.st_dev, observed.st_ino))

    def publish(src: object, dst: object) -> None:
        if Path(str(dst)) == run / "run-brief.md":
            assert len(synced) == 2
        real_replace(str(src), str(dst))

    monkeypatch.setattr(os, "fsync", sync)
    monkeypatch.setattr(os, "replace", publish)
    assert _approve(root, run) == 0
    assert len(synced) == 3
    logged = (run.parent / TARGET / "log/rbot.log").stat()
    assert synced[-1] == (logged.st_dev, logged.st_ino)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("path", None),
        ("sha256", None),
        ("pages", -1),
        ("pages", True),
        ("image_read", "No"),
        ("unreadable", False),
        ("prepared", False),
    ],
)
def test_preparation_metadata_types_have_named_errors(
    root: Path, tmp_path: Path, rules: Rules, field: str, value: object
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    path = run / "prepared/index.json"
    data = json.loads(path.read_text())
    data["files"][0][field] = value
    path.write_text(json.dumps(data))
    source = run / "handoffs/CP-0.md"
    code, found = check(
        source.read_text(),
        load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules),
        rules,
        run,
    )
    assert code == 1 and any(
        f.code == "run_error" and f.message.startswith(str(path) + ":") for f in found
    )


@pytest.mark.parametrize("field", [None, "", "duplicate"])
def test_inventory_keys_fail_closed_with_inventory_path(
    root: Path, tmp_path: Path, rules: Rules, field: str | None
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    path = run / "inventory.json"
    data = json.loads(path.read_text())
    if field == "duplicate":
        data["files"].append(data["files"][0])
    else:
        data["files"][0]["path"] = field
    path.write_text(json.dumps(data))
    source = run / "handoffs/CP-0.md"
    code, found = check(
        source.read_text(),
        load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules),
        rules,
        run,
    )
    assert code == 1 and any(
        f.code == "run_error" and f.message.startswith(str(path) + ":") for f in found
    )


def test_distinct_tranches_are_not_duplicates_but_gap_and_blank_keys_are(
    root: Path, tmp_path: Path, rules: Rules
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    source = run / "handoffs/CP-0.md"
    text = source.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| issuer |"))
    currency = "| currency | NEW-1 | USD | Analyst-asserted | — |"
    valid = text.replace(row, row + "\n" + currency + "\n" + currency.replace("NEW-1", "NEW-2"))
    contract = load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules)
    assert check(valid, contract, rules, run) == (0, [])
    duplicate = text.replace(row, row + "\n" + row.replace("| issuer | — |", "| issuer | |"))
    code, found = check(duplicate, contract, rules, run)
    assert code == 2 and any(
        f.code == "prefill_invalid" and "duplicate" in f.message for f in found
    )


def test_unreadable_prepared_file_can_have_zero_pages(root: Path, tmp_path: Path) -> None:
    run = _acme(tmp_path, {"broken.pdf": "%PDF-1.4\nnot a PDF\n"})
    classes = FILES | {"broken.pdf": ("issuer", "Annual report", "Acme Holdings, Inc.", "Yes")}
    _graded(root, run, classes)
    record = next(
        r
        for r in json.loads((run / "prepared/index.json").read_text())["files"]
        if r["path"] == "broken.pdf"
    )
    assert record["pages"] == 0 and record["prepared"] is None and record["unreadable"]


def test_unknown_prepared_portfolio_date_copies_as_a_gap(
    root: Path, tmp_path: Path, rules: Rules
) -> None:
    extra = {name: (SYNTHETIC / name).read_text().replace("As of,2026-05-29\n", "") for name in CLO}
    classes = FILES | {
        name: ("portfolio", kind, "Test CLO I Ltd", "Yes") for name, kind in CLO.items()
    }
    run = _acme(tmp_path, extra)
    _graded(root, run, classes)
    data = json.loads((run / "prepared/portfolios/TEST_CLO_I.json").read_text())
    assert data["as_of"] == ""
    source = run / "handoffs/CP-0.md"
    text = source.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| TEST_CLO_I |"))
    cells = row.split("|")
    cells[-2] = " — "
    text = text.replace(row, "|".join(cells))
    assert check(
        text, load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules), rules, run
    ) == (0, [])


@pytest.mark.parametrize(
    "damage", ["missing", "json", "name-type", "id", "index-json-type", "index-id-empty", "symlink"]
)
def test_portfolio_input_errors_name_the_failed_file(
    root: Path, tmp_path: Path, rules: Rules, damage: str
) -> None:
    extra = {name: (SYNTHETIC / name).read_text() for name in CLO}
    classes = FILES | {
        name: ("portfolio", kind, "Test CLO I Ltd", "Yes") for name, kind in CLO.items()
    }
    run = _acme(tmp_path, extra)
    _graded(root, run, classes)
    path = run / "prepared/portfolios/TEST_CLO_I.json"
    data = json.loads(path.read_text())
    expected = path
    if damage == "missing":
        path.unlink()
    elif damage == "json":
        path.write_text("not JSON")
    elif damage == "symlink":
        saved = tmp_path / "saved-portfolio.json"
        saved.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(saved)
    elif damage.startswith("index-"):
        expected = run / "prepared/index.json"
        index = json.loads(expected.read_text())
        index["portfolios"][0]["json" if damage == "index-json-type" else "portfolio_id"] = (
            None if damage == "index-json-type" else ""
        )
        expected.write_text(json.dumps(index))
    else:
        data["portfolio_name" if damage == "name-type" else "portfolio_id"] = (
            None if damage == "name-type" else "OTHER"
        )
        path.write_text(json.dumps(data))
    source = run / "handoffs/CP-0.md"
    code, found = check(
        source.read_text(),
        load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules),
        rules,
        run,
    )
    assert code == 1 and any(
        f.code == "run_error" and f.message.startswith(str(expected) + ":") for f in found
    )


def test_cp0_reader_is_explicit_utf8_in_ascii_locale(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("café", encoding="utf-8")
    assert cp0._read(source) == "café"
    env = dict(os.environ, LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0")
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; from rbotlib.cp0 import _read; "
            "import sys; assert _read(Path(sys.argv[1])) == 'caf\\u00e9'",
            str(source),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_run_input_uses_the_declared_portable_index_path(
    root: Path, tmp_path: Path, rules: Rules, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = _acme(tmp_path)
    _graded(root, run, FILES)
    real = Path.read_text

    def read(path: Path, encoding: str | None = None, errors: str | None = None) -> str:
        if path.name.casefold() == "index.json":
            assert path == run / "prepared/index.json"
        return real(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", read)
    assert (
        check(
            (run / "handoffs/CP-0.md").read_text(),
            load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules),
            rules,
            run,
        )[0]
        == 0
    )


@pytest.mark.parametrize("caller", ["check", "validate", "grade"])
def test_nul_portfolio_pointer_is_a_named_run_error(
    root: Path,
    tmp_path: Path,
    rules: Rules,
    capsys: pytest.CaptureFixture[str],
    caller: str,
) -> None:
    extra = {name: (SYNTHETIC / name).read_text() for name in CLO}
    classes = FILES | {
        name: ("portfolio", kind, "Test CLO I Ltd", "Yes") for name, kind in CLO.items()
    }
    run = _acme(tmp_path, extra)
    _graded(root, run, classes)
    source = run / "handoffs/CP-0.md"
    contract = load_contract(RBOT_ROOT / "modules/CP-0/contract.json", rules)
    assert check(source.read_text(), contract, rules, run) == (0, [])
    index_path = run / "prepared/index.json"
    index = json.loads(index_path.read_text())
    relative = "prepared/portfolios/\x00.json"
    index["portfolios"][0]["json"] = relative
    encoded = json.dumps(index)
    assert "\\u0000" in encoded
    index_path.write_text(encoded)
    capsys.readouterr()
    if caller == "check":
        code, found = check(source.read_text(), contract, rules, run)
        assert code == 1 and any(
            f.code == "run_error" and f.message.startswith(str(run / relative) + ":") for f in found
        )
    else:
        args = (
            ["validate", str(source), "--module", "CP-0", "--run", str(run)]
            if caller == "validate"
            else ["--root", str(root), "grade", "--run", str(run)]
        )
        assert main(args) == 1
        output = capsys.readouterr()
        assert str(run / relative) in output.out + output.err
        assert "Available" not in output.out
