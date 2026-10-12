from __future__ import annotations

import os
from pathlib import Path

import pytest

from rbotlib.fsio import write_atomic


def test_a_failed_replace_leaves_the_old_file_and_no_temporary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "run-brief.md"
    target.write_text("old\n", encoding="utf-8")

    def refuse(src: object, dst: object) -> None:
        raise PermissionError(13, "in use", str(dst))

    monkeypatch.setattr(os, "replace", refuse)
    with pytest.raises(PermissionError):
        write_atomic(target, "new\n")
    monkeypatch.undo()
    assert target.read_text(encoding="utf-8") == "old\n"
    assert [p.name for p in tmp_path.iterdir()] == ["run-brief.md"]
    write_atomic(target, "new\n")
    assert target.read_text(encoding="utf-8") == "new\n"


def test_a_fixed_temporary_symlink_cannot_modify_a_source(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("source evidence\n", encoding="utf-8")
    target = tmp_path / "run-brief.md"
    legacy_temp = tmp_path / ".run-brief.md.tmp"
    legacy_temp.symlink_to(source)
    write_atomic(target, "brief\n")
    assert source.read_text(encoding="utf-8") == "source evidence\n"
    assert target.read_text(encoding="utf-8") == "brief\n"
    assert legacy_temp.is_symlink()
