"""Shared fixtures: the real rules, the example contracts, a throwaway RBOT tree and the corpus."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections.abc import Callable, Collection, Iterator
from pathlib import Path
from typing import Any

import pytest

from rbotlib.cli import main
from rbotlib.contract import contract_from_dict
from rbotlib.corpus import Problem, load_registry, materialise, resolve_roots, verify
from rbotlib.render import render_module
from rbotlib.rules import RBOT_ROOT, Rules, load_rules

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_json(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return data


@pytest.fixture
def rules() -> Rules:
    return load_rules()


@pytest.fixture
def handoff_text() -> str:
    return (FIXTURES / "handoff_cp_x.md").read_text(encoding="utf-8")


def write_module(root: Path, data: dict[str, Any], rules: Rules) -> None:
    folder = root / "modules" / data["module_id"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "contract.json").write_text(json.dumps(data), encoding="utf-8")
    text = render_module(contract_from_dict(data, rules), rules)
    (folder / "MODULE.md").write_text(text, encoding="utf-8")


def write_catalog(root: Path, **overrides: object) -> None:
    catalog: dict[str, Any] = {
        "size_budget_bytes": 51200,
        "host_tables": {},
        "front_pages": {"fp": {"tables": ["snapshot.view"]}},
        "pathways": [
            {
                "id": "EXAMPLE",
                "label": "Example",
                "front_page": "fp",
                "depths": {"full": ["CP-X", "CP-Y"]},
            }
        ],
    }
    catalog.update(overrides)
    (root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")


@pytest.fixture
def tree(tmp_path: Path, rules: Rules) -> Path:
    """An RBOT folder with the real rules and the two example modules."""
    shutil.copy(RBOT_ROOT / "rules.json", tmp_path / "rules.json")
    (tmp_path / "canon.md").write_text("# Canon\n", encoding="utf-8")
    write_catalog(tmp_path)
    write_module(tmp_path, fixture_json("contract_cp_x.json"), rules)
    write_module(tmp_path, fixture_json("contract_cp_y.json"), rules)
    return tmp_path


CORPUS = load_registry()
RUNS_DIR = ("rbot-runs",)
REQUIRE_ENV = "RBOT_REQUIRE_CORPUS"
REQUIRE_VALUES = {"", "1", "synthetic"}


def corpus_gate(problems: list[Problem]) -> None:
    """Fail or skip a corpus test whose files are not usable (interfaces spec section 12.3).

    RBOT_REQUIRE_CORPUS=1 fails on any problem (the owner's machine); =synthetic fails
    only on in-repo files and skips the external ones (CI); otherwise the test skips.
    The message names the unresolved root or the mismatched file either way.
    """
    level = os.environ.get(REQUIRE_ENV, "")
    if level not in REQUIRE_VALUES:
        pytest.fail(f"{REQUIRE_ENV} is {level!r}; expected '', '1' or 'synthetic'")
    if not problems:
        return
    message = "; ".join(p.message for p in problems)
    if level == "1" or (level == "synthetic" and any(p.in_repo for p in problems)):
        pytest.fail(message)
    pytest.skip(message)


def tree_digest(root: Path, skip: Collection[str] = ()) -> dict[str, str]:
    """sha256 of every file under `root`, keyed by relative path, leaving out the `skip` subtrees.

    `skip` holds paths relative to `root`; a skipped folder is not read at all.
    """
    digests: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not any(relative.is_relative_to(s) for s in skip):
            digests[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def assert_tree_unchanged(
    label: str, root: Path, before: dict[str, str], skip: Collection[str]
) -> None:
    """Fail naming each file a test added, removed or rewrote in a shared session tree."""
    after = tree_digest(root, skip)
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    assert not changed, (
        f"{label} is shared by every test in the session and must stay read-only; "
        f"changed: {', '.join(changed)}. Copy it to tmp_path first."
    )


@pytest.fixture(scope="session")
def corpus_pack(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Callable[[str], Path]]:
    """Materialise a corpus pack once per session as a throwaway Source Pack (read-only)."""
    made: dict[str, Path] = {}
    digests: dict[str, dict[str, str]] = {}

    def get(pack_id: str) -> Path:
        if pack_id not in made:
            pack = CORPUS.pack(pack_id)
            roots = resolve_roots(CORPUS)
            corpus_gate(verify(CORPUS, pack, roots))
            made[pack_id] = materialise(CORPUS, pack, roots, tmp_path_factory.mktemp(pack_id))
            digests[pack_id] = tree_digest(made[pack_id], RUNS_DIR)
        return made[pack_id]

    yield get
    for pack_id, path in made.items():
        assert_tree_unchanged(f"corpus pack {pack_id}", path, digests[pack_id], RUNS_DIR)


@pytest.fixture(scope="session")
def prepared_run(corpus_pack: Callable[[str], Path]) -> Iterator[Callable[[str], Path]]:
    """A read-only run folder per pack, with `rbot inventory` and `rbot prepare` done once."""
    made: dict[str, Path] = {}
    digests: dict[str, dict[str, str]] = {}

    def get(pack_id: str) -> Path:
        if pack_id not in made:
            run = corpus_pack(pack_id) / "rbot-runs" / f"20261011-{pack_id}-prepared"
            run.mkdir(parents=True)
            assert main(["inventory", "--run", str(run)]) == 0
            assert main(["prepare", "--run", str(run)]) == 0
            made[pack_id] = run
            digests[pack_id] = tree_digest(run)
        return made[pack_id]

    yield get
    for pack_id, path in made.items():
        assert_tree_unchanged(f"prepared run {pack_id}", path, digests[pack_id], ())
