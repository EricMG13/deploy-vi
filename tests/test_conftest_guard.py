"""The read-only guard on the shared corpus fixtures: `tree_digest` sees writes, honours `skip`."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import assert_tree_unchanged, tree_digest


def _tree(root: Path) -> None:
    (root / "a.txt").write_text("one", encoding="utf-8")
    (root / "runs").mkdir()
    (root / "runs" / "x.txt").write_text("x", encoding="utf-8")


def test_a_write_changes_the_digest(tmp_path: Path) -> None:
    _tree(tmp_path)
    before = tree_digest(tmp_path)
    (tmp_path / "a.txt").write_text("two", encoding="utf-8")
    assert tree_digest(tmp_path) != before
    (tmp_path / "b.txt").write_text("new", encoding="utf-8")
    with pytest.raises(AssertionError, match=r"changed: a\.txt, b\.txt"):
        assert_tree_unchanged("pack", tmp_path, before, ())


def test_the_skipped_subtree_is_ignored(tmp_path: Path) -> None:
    _tree(tmp_path)
    before = tree_digest(tmp_path, ("runs",))
    assert "runs/x.txt" not in before
    (tmp_path / "runs" / "y.txt").write_text("y", encoding="utf-8")
    assert tree_digest(tmp_path, ("runs",)) == before
    assert_tree_unchanged("pack", tmp_path, before, ("runs",))
