"""Read-only selected native code-root compatibility; no run or source authority."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from rbotlib.contract import Contract, load_contract
from rbotlib.inventory import RunError, output_path
from rbotlib.isolation_capture import Capture, admit, tree
from rbotlib.rules import RBOT_ROOT, load_rules

OBSERVER_PATHS = frozenset(
    f"scripts/rbotlib/{name}.py"
    for name in (
        "isolation_inputs",
        "isolation_manifest",
        "isolation_capture",
        "isolation_preparation",
        "isolation_evidence",
        "isolation_code_roots",
    )
)
Context = tuple[tuple[str, bytes], ...]


@dataclass(frozen=True)
class CodeRootIdentity:
    """Detached exact native contexts, preserving source/target/executing role slots."""

    target: str
    roots: tuple[Path, Path, Path]
    contexts: tuple[Context, Context, Context]
    rules: bytes
    contract: bytes


@dataclass(frozen=True)
class CodeRootObservation:
    """A consistency handle, not authentication, historical provenance or a grant.

    Only identity and the parsed native Contract are detached immutable facts.
    The private check retains the caller's live Capture and its original baseline.
    """

    identity: CodeRootIdentity
    contract: Contract
    _check: Callable[[], None] = field(repr=False, compare=False)

    def recheck(self) -> None:
        """Check original memberships first, then all prior caller-captured files."""
        self._check()


def _runtime_names(root: Path) -> tuple[str, ...]:
    admit(root, directory=True)
    tree(root / "scripts")
    tree(root / "modules")
    return tuple(
        sorted(
            ["rules.json", "catalog.json", "canon.md"]
            + [str(p.relative_to(root)) for p in (root / "scripts").rglob("*.py")]
            + [str(p.relative_to(root)) for p in (root / "modules").glob("*/contract.json")]
        )
    )


def _compatible(contexts: tuple[Context, Context, Context]) -> None:
    source, target, executing = (dict(context) for context in contexts)
    native = {name for name in executing if name.endswith(".py")} - OBSERVER_PATHS
    for context in (source, target):
        if {name for name in context if name.endswith(".py")} - OBSERVER_PATHS != native:
            raise RunError("isolation code roots: native membership differs")
        if any(context[name] != executing[name] for name in sorted(native)):
            raise RunError("isolation code roots: native code differs")
    names = {name for name in source if not name.endswith(".py")}
    if names != {name for name in target if not name.endswith(".py")} or any(
        source[name] != target[name] for name in sorted(names)
    ):
        raise RunError("isolation code roots: source/target contract context differs")


def _guard(
    roots: tuple[Path, Path, Path], memberships: tuple[tuple[str, ...], ...], capture: Capture
) -> None:
    for root, names in zip(roots, memberships, strict=True):
        if _runtime_names(root) != names:
            raise RunError("isolation code roots: runtime membership changed during observation")
    capture.verify()


def observe(
    source_root: Path, target_root: Path, canonical_target: str, caller_capture: Capture
) -> CodeRootObservation:
    """Audit only selected code roots and target metadata using native loaders.

    Caller-selected roots stay lexical absolute paths: symlinks are never resolved
    away. The executing root is installed RBOT_ROOT, never a supplied substitute.
    No source run, pack, Handoff, prepared portfolio, log or history is selected.
    """
    if (
        not isinstance(canonical_target, str)
        or re.fullmatch(r"CP-[0-9]+[A-Z]?", canonical_target) is None
        or canonical_target == "CP-8"
    ):
        raise RunError("isolation code roots: canonical installed Module target required")
    roots = (source_root.absolute(), target_root.absolute(), RBOT_ROOT)
    contract_path = output_path(roots[1], f"modules/{canonical_target}/contract.json")
    contract_raw = caller_capture.read(contract_path)
    rules_raw = caller_capture.read(roots[1] / "rules.json")
    rules = load_rules(roots[1])
    contract = load_contract(contract_path, rules)
    if contract.module_id != canonical_target:
        raise RunError("isolation code roots: target identity differs")
    memberships = tuple(_runtime_names(root) for root in roots)
    source, target, executing = (
        tuple((name, caller_capture.read(root / name)) for name in names)
        for root, names in zip(roots, memberships, strict=True)
    )
    contexts = (source, target, executing)
    _compatible(contexts)
    check = partial(_guard, roots, memberships, caller_capture)
    check()
    identity = CodeRootIdentity(canonical_target, roots, contexts, rules_raw, contract_raw)
    return CodeRootObservation(identity, contract, check)
