"""Native copied-root positives and bounded identity, admission and recheck refusals."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections.abc import Callable
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any, NoReturn, cast

import pytest

from rbotlib import host_evidence, state
from rbotlib import isolation_code_roots as code
from rbotlib.contract import Contract, ContractError, load_contract
from rbotlib.inventory import RunError
from rbotlib.isolation_capture import Capture
from rbotlib.rules import RBOT_ROOT, Rules, load_rules

NATIVE = "scripts/rbotlib/rules.py"
CONTRACT = "modules/CP-1/contract.json"


def copy_root(folder: Path) -> Path:
    return Path(shutil.copytree(RBOT_ROOT, folder, ignore=shutil.ignore_patterns("__pycache__")))


@pytest.fixture
def roots(tmp_path: Path) -> tuple[Path, Path]:
    return copy_root(tmp_path / "source"), copy_root(tmp_path / "target")


def forbidden(*args: object, **kwargs: object) -> NoReturn:
    pytest.fail("unauthorized content read")


def native_names(root: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            ["rules.json", "catalog.json", "canon.md"]
            + [str(p.relative_to(root)) for p in (root / "scripts").rglob("*.py")]
            + [str(p.relative_to(root)) for p in (root / "modules").glob("*/contract.json")]
        )
    )


@pytest.mark.parametrize(
    "target", ["CP-0", "CP-1", "CP-1A", "CP-1B", "CP-1D", "CP-2", "CP-3", "CP-5", "CP-6"]
)
def test_native_identity_context_parity_and_preservation(
    roots: tuple[Path, Path], target: str
) -> None:
    capture = Capture()
    observed = code.observe(*roots, target, capture)
    identity = observed.identity
    assert identity.target == target
    assert identity.roots == (*roots, RBOT_ROOT)
    assert observed.contract == load_contract(
        roots[1] / f"modules/{target}/contract.json", load_rules(roots[1])
    )
    assert identity.rules == (roots[1] / "rules.json").read_bytes()
    assert identity.contract == (roots[1] / f"modules/{target}/contract.json").read_bytes()
    record: state.Record = dict.fromkeys(
        (
            "run_id",
            "pack_root",
            "issuer_id",
            "as_of_date",
            "approval",
            "plan",
            "pathway",
            "depth",
            "primary",
            "deep_research",
            "run_brief_sha256",
        ),
        "fixture",
    )
    for root, context in zip(identity.roots, identity.contexts, strict=True):
        assert tuple(name for name, _ in context) == native_names(root)
        assert all(raw == (root / name).read_bytes() for name, raw in context)
        expected = host_evidence.digest(
            {
                "root": str(root),
                "files": {n: hashlib.sha256(raw).hexdigest() for n, raw in context},
                "state": record,
            }
        )
        assert host_evidence.context(root, record) == expected
    baseline = capture.inventory()
    observed.recheck()
    observed.recheck()
    assert capture.inventory() == baseline
    assert all(path.read_bytes() == raw for path, raw in baseline)
    assert not list(roots[0].rglob("run-state.json"))


@pytest.mark.parametrize("coincident", ["all", "source-target", "target-executing"])
def test_role_slots_survive_coincidence(roots: tuple[Path, Path], coincident: str) -> None:
    source, target = roots
    if coincident == "all":
        source = target = RBOT_ROOT
    elif coincident == "source-target":
        target = source
    else:
        target = RBOT_ROOT
    observed = code.observe(source, target, "CP-1", Capture())
    assert observed.identity.roots == (source, target, RBOT_ROOT)
    assert len(observed.identity.contexts) == 3
    observed.recheck()


@pytest.mark.parametrize("role", [0, 1])
@pytest.mark.parametrize("change", ["code", "rules.json", "catalog.json", "canon.md", CONTRACT])
def test_exact_bytes_refuse(roots: tuple[Path, Path], role: int, change: str) -> None:
    path = roots[role] / (NATIVE if change == "code" else change)
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(RunError, match=r"native code differs|contract context differs"):
        code.observe(*roots, "CP-1", Capture())


@pytest.mark.parametrize("role", [0, 1])
@pytest.mark.parametrize("change", ["add-code", "delete-code", "add-contract", "delete-contract"])
def test_symmetric_names_refuse(roots: tuple[Path, Path], role: int, change: str) -> None:
    root = roots[role]
    if change == "add-code":
        (root / "scripts/extra.py").write_text("# new\n")
    elif change == "delete-code":
        (root / NATIVE).unlink()
    elif change == "add-contract":
        (root / "modules/CP-99").mkdir()
        (root / "modules/CP-99/contract.json").write_bytes(b"{}")
    else:
        (root / "modules/CP-2/contract.json").unlink()
    with pytest.raises(RunError, match=r"membership differs|contract context differs"):
        code.observe(*roots, "CP-1", Capture())


@pytest.mark.parametrize("role", [0, 1])
@pytest.mark.parametrize("absent", [False, True])
def test_exact_observer_exceptions_still_capture_present(
    roots: tuple[Path, Path], role: int, absent: bool
) -> None:
    expected = {
        f"scripts/rbotlib/{name}.py"
        for name in (
            "isolation_inputs",
            "isolation_manifest",
            "isolation_capture",
            "isolation_preparation",
            "isolation_evidence",
            "isolation_code_roots",
        )
    }
    assert code.OBSERVER_PATHS == expected
    for name in expected:
        path = roots[role] / name
        if absent:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(b"# observer difference\n")
    capture = Capture()
    observed = code.observe(*roots, "CP-1", capture)
    context = dict(observed.identity.contexts[role])
    for name in expected:
        assert (name not in context) if absent else context[name] == b"# observer difference\n"
        if not absent:
            assert (roots[role] / name, context[name]) in capture.inventory()
    observed.recheck()


@pytest.mark.parametrize("name", sorted(code.OBSERVER_PATHS))
def test_same_basename_elsewhere_is_native(roots: tuple[Path, Path], name: str) -> None:
    impostor = roots[0] / "scripts" / Path(name).name
    impostor.write_bytes(b"# impostor\n")
    with pytest.raises(RunError, match="native membership differs"):
        code.observe(*roots, "CP-1", Capture())


def test_non_python_context_is_source_target_only(roots: tuple[Path, Path]) -> None:
    for root in roots:
        (root / "canon.md").write_bytes(b"different shared context\n")
    observed = code.observe(*roots, "CP-1", Capture())
    assert dict(observed.identity.contexts[0])["canon.md"] == b"different shared context\n"
    observed.recheck()


@pytest.mark.parametrize("role", [0, 1, 2])
@pytest.mark.parametrize(
    "change",
    ["add", "delete", "bytes", "inode", "rules.json", "catalog.json", "canon.md", CONTRACT],
)
def test_bound_guard_all_roles_and_membership_before_reread(
    roots: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    role: int,
    change: str,
) -> None:
    executing = copy_root(tmp_path / "executing")
    monkeypatch.setattr(code, "RBOT_ROOT", executing)
    capture = Capture()
    observed = code.observe(*roots, "CP-1", capture)
    baseline = capture.inventory()
    root = (*roots, executing)[role]
    path = root / (
        change if change in ("rules.json", "catalog.json", "canon.md", CONTRACT) else NATIVE
    )
    if change == "add":
        (root / "scripts/added.py").write_bytes(b"# added\n")
    elif change == "delete":
        path.unlink()
    elif change == "inode":
        replacement = tmp_path / "replacement"
        replacement.write_bytes(path.read_bytes())
        replacement.replace(path)
    else:
        path.write_bytes(path.read_bytes() + b"\n")
    if change in ("add", "delete"):
        monkeypatch.setattr(capture, "read", forbidden)
    for _ in range(2):
        with pytest.raises(RunError, match=r"membership changed|bytes changed|identity changed"):
            observed.recheck()
    assert capture.inventory() == baseline


@pytest.mark.parametrize("target", ["cp-1", "CP-8", "MODEL", "CP-1/../CP-2", "CP-1\n", "", None, 1])
def test_invalid_target_before_selection(
    roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, target: object
) -> None:
    monkeypatch.setattr(code, "output_path", forbidden)
    with pytest.raises(RunError, match="canonical installed"):
        code.observe(*roots, cast(str, target), Capture())


def test_unknown_target_before_source_or_rules_read(
    roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(code, "load_rules", forbidden)
    with pytest.raises(FileNotFoundError, match="CP-99"):
        code.observe(*roots, "CP-99", Capture())


def test_wrong_target_identity_before_source_selection(
    roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = roots[1] / CONTRACT
    data = json.loads(path.read_text())
    data["module_id"] = "CP-2"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(code, "_runtime_names", forbidden)
    with pytest.raises(RunError, match="target identity differs"):
        code.observe(*roots, "CP-1", Capture())


def test_capture_before_native_load_and_final_guard(
    roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    capture = Capture()
    rules_loader, contract_loader = load_rules, load_contract

    def rules(root: Path = RBOT_ROOT) -> Rules:
        assert (root / "rules.json", (root / "rules.json").read_bytes()) in capture.inventory()
        assert (root / CONTRACT, (root / CONTRACT).read_bytes()) in capture.inventory()
        return rules_loader(root)

    def contract(path: Path, rules: Rules) -> Contract:
        assert (path, path.read_bytes()) in capture.inventory()
        result = contract_loader(path, rules)
        (roots[0] / "scripts/late.py").write_bytes(b"# late\n")
        return result

    monkeypatch.setattr(code, "load_rules", rules)
    monkeypatch.setattr(code, "load_contract", contract)
    with pytest.raises(RunError, match="native membership differs"):
        code.observe(*roots, "CP-1", capture)


@pytest.mark.parametrize("change_kind", ["membership", "bytes"])
def test_return_guard_refuses_late_membership_without_capture(
    roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, change_kind: str
) -> None:
    compatible = code._compatible

    def change(contexts: tuple[code.Context, code.Context, code.Context]) -> None:
        compatible(contexts)
        path = roots[1] / ("scripts/late.py" if change_kind == "membership" else NATIVE)
        path.write_bytes(b"# late\n")

    monkeypatch.setattr(code, "_compatible", change)
    capture = Capture()
    with pytest.raises(RunError, match=r"runtime membership changed|bytes changed"):
        code.observe(*roots, "CP-1", capture)
    assert roots[1] / "scripts/late.py" not in dict(capture.inventory())


def test_immutable_facts_original_capture_and_prior_entries(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prior = tmp_path / "prior-source"
    prior.write_bytes(b"prior")
    capture = Capture()
    capture.read(prior)
    observed = code.observe(*roots, "CP-1", capture)
    identity = observed.identity
    assert all(isinstance(context, tuple) for context in identity.contexts)
    assert all(
        isinstance(n, str) and isinstance(raw, bytes)
        for context in identity.contexts
        for n, raw in context
    )
    assert "prior-source" not in {n for context in identity.contexts for n, _ in context}
    with pytest.raises(FrozenInstanceError):
        cast(Any, identity).roots = (tmp_path, tmp_path, tmp_path)
    with pytest.raises(FrozenInstanceError):
        cast(Any, observed.contract).module_id = "CP-2"
    with pytest.raises(TypeError):
        cast(Callable[..., None], observed.recheck)(Capture())
    with pytest.raises(TypeError):
        cast(Callable[..., code.CodeRootObservation], code.observe)(
            *roots, "CP-1", Capture(), tmp_path
        )
    monkeypatch.setattr(code, "RBOT_ROOT", tmp_path)
    prior.write_bytes(b"changed")
    with pytest.raises(RunError, match="bytes changed"):
        observed.recheck()
    assert observed.identity is identity


@pytest.mark.parametrize(
    "attack",
    [
        "root-link",
        "leaf-link",
        "hardlink",
        "directory",
        "fifo",
        "parent",
        "missing",
        "bounds",
        "io-error",
        "bad-rules",
        "bad-contract",
    ],
)
def test_physical_native_errors_and_no_source_changes(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    source, target = roots
    baseline = {p: p.read_bytes() for p in source.rglob("*") if p.is_file()}
    path = target / CONTRACT
    if attack in ("root-link", "parent"):
        link = tmp_path / "link"
        link.symlink_to(target, target_is_directory=True)
        target = link if attack == "root-link" else target / ".." / target.name
    elif attack == "bounds":
        monkeypatch.setattr("rbotlib.isolation_capture._FILE_LIMIT", 1)
    elif attack == "io-error":

        def failed(path: Path) -> bytes:
            raise PermissionError("denied")

        monkeypatch.setattr(Capture, "read", lambda self, path: failed(path))
    elif attack in ("bad-rules", "bad-contract"):
        (target / "rules.json" if attack == "bad-rules" else path).write_bytes(b"{")
    else:
        raw = path.read_bytes()
        path.unlink()
        if attack == "leaf-link":
            path.symlink_to(source / CONTRACT)
        elif attack == "hardlink":
            os.link(source / CONTRACT, path)
        elif attack in ("directory", "fifo"):
            if attack == "directory":
                path.mkdir()
            else:
                os.mkfifo(path)
        else:
            assert attack == "missing" and raw
    with pytest.raises((RunError, OSError, json.JSONDecodeError, ContractError)):
        code.observe(source, target, "CP-1", Capture())
    assert all(p.read_bytes() == raw for p, raw in baseline.items())
