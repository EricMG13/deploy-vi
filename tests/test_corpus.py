from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

import pytest

from conftest import CORPUS, REQUIRE_ENV, corpus_gate
from rbotlib.cli import main
from rbotlib.corpus import (
    MISSING,
    ROOTS_ENV,
    UNRESOLVED,
    CorpusError,
    Problem,
    load_registry,
    materialise,
    resolve_roots,
    verify,
)
from rbotlib.rules import Rules

PATHWAYS = set(
    "FULL_CREDIT_ASSESSMENT RELATIVE_VALUE COVENANT_REFINANCING DISTRESSED_RESTRUCTURING"
    " EARNINGS_UPDATE PORTFOLIO_DECISION".split()
)
TRAPS = set(
    "entity_mismatch period_mismatch price_talk_not_market_level image_read_only"
    " missing_document_type prior_case_present duplicate_source".split()
)


def _registry(tmp_path: Path, files: dict[str, bytes], listed: dict[str, str]) -> Path:
    """A one-pack registry at <tmp>/repo/tests/corpus/corpus.json over <tmp>/ext/pack/."""
    folder = tmp_path / "ext" / "pack"
    folder.mkdir(parents=True)
    for name, data in files.items():
        (folder / name).write_bytes(data)
    entry = {"class": "issuer", "document_type": "Other", "entity": "TEST"}
    pack: dict[str, Any] = {"id": "p1", "root": "ext", "path": "pack", "period": "FY2025"}
    pack |= {"issuer": {"id": "TEST", "name": "Test plc"}, "pathways": []}
    pack["files"] = [{"path": n, "sha256": d, **entry} for n, d in listed.items()]
    registry = tmp_path / "repo" / "tests" / "corpus" / "corpus.json"
    registry.parent.mkdir(parents=True)
    roots = {"ext": "external", "synthetic": "tests/corpus/synthetic"}
    body = {"schema": "rbot-corpus/1", "roots": roots, "packs": [pack]}
    registry.write_text(json.dumps(body), encoding="utf-8")
    return registry


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_the_registry_is_well_formed(rules: Rules) -> None:
    ids = [p.id for p in CORPUS.packs]
    assert len(ids) == len(set(ids)) == 34
    for pack in CORPUS.packs:
        assert pack.root in CORPUS.roots
        assert {w["id"] for w in pack.data["pathways"]} <= PATHWAYS
        assert {w["fit"] for w in pack.data["pathways"]} <= {"primary", "exercises", "partial"}
        assert {t["kind"] for t in pack.data["traps"]} <= TRAPS
        assert pack.data["prior_pack"] is None or pack.data["prior_pack"] in ids
        names = [f.path for f in pack.files]
        assert len(names) == len(set(names)), pack.id
        for f in pack.files:
            assert re.fullmatch(r"[0-9a-f]{64}", f.sha256), f.path
            assert f.cls in rules.source_classes, f.path
            assert f.document_type in rules.scales["document_type"], f.path
            assert (f.pages is not None) == f.path.lower().endswith(".pdf"), f.path
            for rel in (f.path, pack.path, f.external or ""):
                assert not PurePosixPath(rel).is_absolute(), f.path
                assert ".." not in PurePosixPath(rel).parts, f.path
            if f.external:
                assert f.external.partition("/")[0] in CORPUS.roots, f.path


def test_unresolved_external_roots_are_named(tmp_path: Path) -> None:
    data = b"filing text\n"
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    roots = resolve_roots(registry, {})
    assert "ext" not in roots
    problems = verify(registry, registry.pack("p1"), roots)
    assert [(p.code, p.in_repo) for p in problems] == [(UNRESOLVED, False)]
    message = "p1: root 'ext' is unresolved for 1 file(s); set RBOT_CORPUS_ROOTS"
    assert message in problems[0].message


def test_missing_and_changed_files_are_named(tmp_path: Path) -> None:
    data = b"filing text\n"
    listed = {"a.txt": _sha(b"other bytes"), "b.txt": _sha(data)}
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, listed))
    roots = resolve_roots(registry, {ROOTS_ENV: json.dumps({"ext": str(tmp_path / "ext")})})
    messages = [(p.code, p.message) for p in verify(registry, registry.pack("p1"), roots)]
    assert messages[0][0] == MISSING and "p1: a.txt: sha256 differs at " in messages[0][1]
    assert messages[1][0] == MISSING and messages[1][1].startswith("p1: b.txt: missing at ")


def test_materialise_copies_verified_files_only(tmp_path: Path) -> None:
    data = b"filing text\n"
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    roots = resolve_roots(registry, {ROOTS_ENV: json.dumps({"ext": str(tmp_path / "ext")})})
    pack = materialise(registry, registry.pack("p1"), roots, tmp_path / "copy")
    assert (pack / "a.txt").read_bytes() == data
    with pytest.raises(CorpusError, match="root 'ext' is unresolved"):
        materialise(registry, registry.pack("p1"), {}, tmp_path / "copy2")


def test_bad_registries_and_environments_are_refused(tmp_path: Path) -> None:
    path = _registry(tmp_path, {}, {})
    with pytest.raises(CorpusError, match="not a JSON object"):
        resolve_roots(load_registry(path), {ROOTS_ENV: "[1, 2]"})
    with pytest.raises(CorpusError, match="not a JSON object"):
        resolve_roots(load_registry(path), {ROOTS_ENV: "{nope"})
    with pytest.raises(CorpusError, match="no pack 'p9'"):
        load_registry(path).pack("p9")
    path.write_text(json.dumps({"schema": "other/1"}), encoding="utf-8")
    with pytest.raises(CorpusError, match="expected 'rbot-corpus/1'"):
        load_registry(path)


def test_corpus_command_lists_and_verifies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    data = b"filing text\n"
    registry = str(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    assert main(["corpus", "list", "--registry", registry]) == 0
    assert capsys.readouterr().out.startswith("p1  ext:pack  TEST FY2025  1 file(s)")
    monkeypatch.delenv(ROOTS_ENV, raising=False)
    assert main(["corpus", "verify", "--registry", registry]) == UNRESOLVED
    assert capsys.readouterr().out.endswith("exit 2\n")
    monkeypatch.setenv(ROOTS_ENV, json.dumps({"ext": str(tmp_path / "ext")}))
    assert main(["corpus", "verify", "--pack", "p1", "--registry", registry]) == 0
    assert capsys.readouterr().out == "ok p1 (1 files)\nexit 0\n"
    (tmp_path / "ext" / "pack" / "a.txt").write_bytes(b"edited\n")
    assert main(["corpus", "verify", "--registry", registry]) == MISSING


def _roots_env(tmp_path: Path) -> dict[str, str]:
    return {ROOTS_ENV: json.dumps({"ext": str(tmp_path / "ext")})}


@pytest.mark.parametrize("entry", ["../../outside.txt", "OUTSIDE_ABSOLUTE"])
def test_a_registry_entry_cannot_escape_its_root(tmp_path: Path, entry: str) -> None:
    data = b"secret\n"
    outside = tmp_path / "outside.txt"
    outside.write_bytes(data)
    name = str(outside) if entry == "OUTSIDE_ABSOLUTE" else entry
    registry = load_registry(_registry(tmp_path, {}, {name: _sha(data)}))
    roots = resolve_roots(registry, _roots_env(tmp_path))
    problems = verify(registry, registry.pack("p1"), roots)
    assert [(p.code, "escapes root" in p.message) for p in problems] == [(MISSING, True)]
    with pytest.raises(CorpusError, match="escapes root"):
        materialise(registry, registry.pack("p1"), roots, tmp_path / "copy")


def test_materialise_refuses_a_target_outside_the_destination(tmp_path: Path) -> None:
    data = b"sibling\n"
    registry = load_registry(_registry(tmp_path, {}, {"../sibling.txt": _sha(data)}))
    (tmp_path / "ext" / "sibling.txt").write_bytes(data)
    roots = resolve_roots(registry, _roots_env(tmp_path))
    assert verify(registry, registry.pack("p1"), roots) == []
    with pytest.raises(CorpusError, match="outside the destination"):
        materialise(registry, registry.pack("p1"), roots, tmp_path / "copy")
    assert not (tmp_path / "sibling.txt").exists()


def test_a_bad_require_value_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(REQUIRE_ENV, "yes")
    expected = r"RBOT_REQUIRE_CORPUS is 'yes'; expected '', '1' or 'synthetic'"
    with pytest.raises(pytest.fail.Exception, match=expected):
        corpus_gate([])
    with pytest.raises(pytest.fail.Exception, match=expected):
        corpus_gate([Problem(MISSING, True, "p1: a.txt: missing")])


def test_a_root_that_is_not_a_folder_is_named(tmp_path: Path) -> None:
    data = b"filing text\n"
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, {"a.txt": _sha(data)}))
    gone = tmp_path / "nowhere"
    roots = resolve_roots(registry, {ROOTS_ENV: json.dumps({"ext": str(gone)})})
    (problem,) = verify(registry, registry.pack("p1"), roots)
    assert problem.code == UNRESOLVED
    assert f"root 'ext' -> {gone} is not a folder" in problem.message


def test_a_hash_mismatch_names_the_path_and_both_hashes(tmp_path: Path) -> None:
    data = b"filing text\n"
    registry = load_registry(_registry(tmp_path, {"a.txt": data}, {"a.txt": "ab" * 32}))
    roots = resolve_roots(registry, _roots_env(tmp_path))
    (problem,) = verify(registry, registry.pack("p1"), roots)
    where = tmp_path / "ext" / "pack" / "a.txt"
    expected = f"sha256 differs at {where}: registry {'ab' * 6}, file {_sha(data)[:12]}"
    assert expected in problem.message


def test_unresolved_roots_are_grouped_per_pack_and_root(tmp_path: Path) -> None:
    listed = {n: _sha(b"x") for n in ("a.txt", "b.txt", "c.txt")}
    registry = load_registry(_registry(tmp_path, {}, listed))
    problems = verify(registry, registry.pack("p1"), resolve_roots(registry, {}))
    assert len(problems) == 1
    message = "p1: root 'ext' is unresolved for 3 file(s); set RBOT_CORPUS_ROOTS"
    assert message in problems[0].message


def test_a_malformed_registry_or_root_value_is_named(tmp_path: Path) -> None:
    path = _registry(tmp_path, {}, {})
    body = json.loads(path.read_text(encoding="utf-8"))
    del body["packs"][0]["root"]
    path.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(CorpusError, match=re.escape(f"{path}: pack 0: missing root")):
        load_registry(path)
    body["packs"][0]["root"] = "ext"
    body["packs"][0]["files"] = [{"path": "a.txt"}]
    path.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(CorpusError, match=re.escape(f"{path}: pack 0: file 0: missing sha256")):
        load_registry(path)
    good = load_registry(_registry(tmp_path / "g", {}, {}))
    with pytest.raises(CorpusError, match="root 'ext' must be a string"):
        resolve_roots(good, {ROOTS_ENV: json.dumps({"ext": 5})})


def test_the_corpus_command_reports_a_bad_registry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "corpus.json"
    bad.write_text(json.dumps({"schema": "other/1"}), encoding="utf-8")
    assert main(["corpus", "list", "--registry", str(bad)]) == 2
    assert "expected 'rbot-corpus/1'" in capsys.readouterr().out
    assert main(["corpus", "list", "--registry", str(tmp_path / "none.json")]) == 2
    assert "none.json" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("level", "in_repo", "outcome"),
    [
        ("1", False, "fail"),
        ("synthetic", True, "fail"),
        ("synthetic", False, "skip"),
        ("", True, "skip"),
    ],
)
def test_the_require_rule(
    monkeypatch: pytest.MonkeyPatch, level: str, in_repo: bool, outcome: str
) -> None:
    monkeypatch.setenv(REQUIRE_ENV, level)
    problems = [Problem(MISSING, in_repo, "p1: a.txt: sha256 differs")]
    expected = pytest.fail.Exception if outcome == "fail" else pytest.skip.Exception
    with pytest.raises(expected, match=re.escape("p1: a.txt: sha256 differs")):
        corpus_gate(problems)
    corpus_gate([])


@pytest.mark.corpus
@pytest.mark.parametrize("pack_id", [p.id for p in CORPUS.packs])
def test_corpus_hashes_match(pack_id: str) -> None:
    pack = CORPUS.pack(pack_id)
    corpus_gate(verify(CORPUS, pack, resolve_roots(CORPUS)))


def test_an_external_file_in_an_in_repo_pack_is_not_in_repo(tmp_path: Path) -> None:
    path = _registry(tmp_path, {}, {"a.txt": _sha(b"x")})
    body = json.loads(path.read_text(encoding="utf-8"))
    body["packs"][0].update(root="synthetic", path="pack")
    body["packs"][0]["files"][0]["external"] = "ext/pack/a.txt"
    path.write_text(json.dumps(body), encoding="utf-8")
    (tmp_path / "repo" / "tests" / "corpus" / "synthetic").mkdir()
    registry = load_registry(path)
    problems = verify(registry, registry.pack("p1"), resolve_roots(registry, {}))
    assert [(p.code, p.in_repo) for p in problems] == [(UNRESOLVED, False)]


def test_a_root_value_or_external_path_cannot_leave_the_repo_or_be_absolute(
    tmp_path: Path,
) -> None:
    path = _registry(tmp_path, {}, {"a.txt": _sha(b"x")})
    body = json.loads(path.read_text(encoding="utf-8"))
    body["roots"]["synthetic"] = "../../../outside"
    path.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(CorpusError, match=r"root 'synthetic'.*escapes the repo"):
        resolve_roots(load_registry(path), {})
    path = _registry(tmp_path / "b", {}, {"a.txt": _sha(b"x")})
    body = json.loads(path.read_text(encoding="utf-8"))
    body["packs"][0]["files"][0]["external"] = "ext//etc/hosts"
    path.write_text(json.dumps(body), encoding="utf-8")
    registry = load_registry(path)
    (problem,) = verify(
        registry, registry.pack("p1"), resolve_roots(registry, _roots_env(tmp_path / "b"))
    )
    assert "absolute path not allowed" in problem.message


def test_a_registry_that_is_an_array_or_lacks_pack_keys_is_named(tmp_path: Path) -> None:
    path = tmp_path / "corpus.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(CorpusError, match="not a JSON object"):
        load_registry(path)
    for key in ("pathways", "issuer", "period"):
        good = _registry(tmp_path / key, {}, {})
        body = json.loads(good.read_text(encoding="utf-8"))
        del body["packs"][0][key]
        good.write_text(json.dumps(body), encoding="utf-8")
        with pytest.raises(CorpusError, match=f"pack 0: missing {key}"):
            load_registry(good)
