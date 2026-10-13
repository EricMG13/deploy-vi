"""Physical capture is independent of native authority, publication and calculations."""

from __future__ import annotations

import io
import os
from collections.abc import Iterator
from pathlib import Path
from typing import NoReturn

import pytest

from rbotlib import isolation_capture as capture
from rbotlib.inventory import RunError


def file(folder: Path, name: str = "original", raw: bytes = b"same") -> Path:
    path = folder / name
    path.write_bytes(raw)
    return path


def forbidden(*args: object, **kwargs: object) -> NoReturn:
    pytest.fail("forbidden content read")


def test_multifile_empty_reread_verify_and_detached_inventory(tmp_path: Path) -> None:
    session = capture.Capture()
    assert session.inventory() == ()
    session.verify()
    paths = [file(tmp_path, "z", b"\x00\xff\n"), file(tmp_path, "a", b"")]
    for path in paths:
        assert session.read(path) == path.read_bytes()
        assert session.read(path) == path.read_bytes()
    session.verify()
    inventory = session.inventory()
    assert inventory == ((paths[1], b""), (paths[0], b"\x00\xff\n"))
    assert isinstance(inventory, tuple)
    assert all(isinstance(raw, bytes) for _, raw in inventory)
    detached = dict(inventory)
    detached[paths[0]] = b"replaced"
    detached.clear()
    assert session.inventory() == inventory
    session.verify()
    assert sorted(tmp_path.iterdir()) == sorted(paths)


@pytest.mark.parametrize("operation", ["read", "verify"])
@pytest.mark.parametrize("change", ["bytes", "inode", "deleted"])
def test_captured_changes_refuse_without_rebasing(
    tmp_path: Path, operation: str, change: str
) -> None:
    path = file(tmp_path)
    session = capture.Capture()
    session.read(path)
    baseline = session.inventory()
    if change == "bytes":
        path.write_bytes(b"different")
    elif change == "inode":
        file(tmp_path, "replacement").replace(path)
    else:
        path.unlink()
    expected = FileNotFoundError if change == "deleted" else RunError
    match = "identity changed" if change == "inode" else "bytes changed|original"
    with pytest.raises(expected, match=match):
        session.read(path) if operation == "read" else session.verify()
    assert session.inventory() == baseline


@pytest.mark.parametrize(
    "attack", ["leaf", "ancestor", "hardlink", "fifo", "directory", "parent", "relative"]
)
def test_attacks_refuse_before_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    path = file(folder)
    outside = file(tmp_path, "outside")
    if attack == "ancestor":
        link = tmp_path / "link"
        link.symlink_to(folder, target_is_directory=True)
        path = link / path.name
    elif attack == "parent":
        path = folder / ".." / "outside"
    elif attack == "relative":
        path = Path("outside")
    else:
        path.unlink()
        if attack == "leaf":
            path.symlink_to(outside)
        elif attack == "hardlink":
            os.link(outside, path)
        elif attack == "fifo":
            os.mkfifo(path)
        else:
            path.mkdir()
    monkeypatch.setattr(os, "open", forbidden)
    with pytest.raises(RunError):
        capture.Capture().read(path)
    assert outside.read_bytes() == b"same"


@pytest.mark.parametrize("name", ["new\nline", "del\x7f", "back\\slash", "colon:", "null\x00"])
def test_unsafe_components_refuse_before_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    path = tmp_path / name / "file"
    monkeypatch.setattr(os, "open", forbidden)
    with pytest.raises(RunError, match="unsafe"):
        capture.Capture().read(path)


def test_double_root_and_non_directory_ancestor_refuse(tmp_path: Path) -> None:
    with pytest.raises(RunError, match="canonical"):
        capture.admit(Path("//private/tmp"), directory=True)
    path = file(tmp_path)
    with pytest.raises(RunError, match="directory ancestor"):
        capture.admit(path / "child")
    assert capture.admit(tmp_path, directory=True).st_ino == tmp_path.stat().st_ino


@pytest.mark.parametrize("attack", ["replacement", "hardlink"])
def test_admitted_to_opened_race_refuses_and_closes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    path = file(tmp_path)
    replacement = file(tmp_path, "replacement")
    native = os.open
    descriptors: list[int] = []

    def opening(target: Path, flags: int) -> int:
        assert flags & os.O_NOFOLLOW
        if attack == "replacement":
            replacement.replace(path)
        else:
            os.link(path, tmp_path / "added-link")
        descriptor = native(target, flags)
        descriptors.append(descriptor)
        return descriptor

    monkeypatch.setattr(os, "open", opening)
    monkeypatch.setattr(os, "fdopen", forbidden)
    session = capture.Capture()
    with pytest.raises(RunError, match=r"identity changed|single-link"):
        session.read(path)
    assert session.inventory() == ()
    with pytest.raises(OSError):
        os.fstat(descriptors[0])


@pytest.mark.parametrize("failure", ["open", "fstat", "fdopen", "read", "size"])
def test_errors_close_descriptors_and_do_not_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    path = file(tmp_path)
    native_open, native_fstat = os.open, os.fstat
    descriptors: list[int] = []

    def opening(target: Path, flags: int) -> int:
        if failure == "open":
            raise PermissionError("open denied")
        descriptor = native_open(target, flags)
        descriptors.append(descriptor)
        return descriptor

    def failing(*args: object, **kwargs: object) -> NoReturn:
        raise OSError("injected error")

    class Unreadable(io.BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            raise OSError("read denied")

    monkeypatch.setattr(os, "open", opening)
    if failure == "fstat":
        monkeypatch.setattr(os, "fstat", failing)
    elif failure == "fdopen":
        monkeypatch.setattr(os, "fdopen", failing)
    elif failure == "read":
        monkeypatch.setattr(os, "fdopen", lambda *a, **k: Unreadable())
    elif failure == "size":
        monkeypatch.setattr(capture, "_FILE_LIMIT", 3)
    session = capture.Capture()
    with pytest.raises(RunError if failure == "size" else OSError):
        session.read(path)
    assert session.inventory() == ()
    for descriptor in descriptors:
        with pytest.raises(OSError):
            native_fstat(descriptor)


def test_success_closes_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = file(tmp_path)
    native = os.open
    descriptors: list[int] = []

    def opening(target: Path, flags: int) -> int:
        assert flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND) == 0
        descriptor = native(target, flags)
        descriptors.append(descriptor)
        return descriptor

    monkeypatch.setattr(os, "open", opening)
    assert capture.Capture().read(path) == b"same"
    with pytest.raises(OSError):
        os.fstat(descriptors[0])


def test_exact_default_per_file_boundary(tmp_path: Path) -> None:
    assert capture._FILE_LIMIT == 67108864 and capture._TOTAL_LIMIT == 268435456
    path = file(tmp_path, raw=b"")
    with path.open("wb") as stream:
        stream.truncate(capture._FILE_LIMIT)
    session = capture.Capture()
    assert len(session.read(path)) == capture._FILE_LIMIT
    session.verify()
    excess = file(tmp_path, "excess", b"")
    with excess.open("wb") as stream:
        stream.truncate(capture._FILE_LIMIT + 1)
    with pytest.raises(RunError, match="per file"):
        session.read(excess)
    assert tuple(p for p, _ in session.inventory()) == (path,)


def test_aggregate_exact_excess_reread_and_failed_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(capture, "_FILE_LIMIT", 4)
    monkeypatch.setattr(capture, "_TOTAL_LIMIT", 8)
    session = capture.Capture()
    paths = [file(tmp_path, str(i), b"four") for i in range(2)]
    for path in paths:
        session.read(path)
    baseline = session.inventory()
    session.read(paths[0])
    session.verify()
    excess = file(tmp_path, "excess", b"x")
    with pytest.raises(RunError, match="total"):
        session.read(excess)
    assert session.inventory() == baseline
    excess.write_bytes(b"")
    assert session.read(excess) == b""
    session.verify()


def test_tree_sorted_structure_without_content_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "z").mkdir()
    (tmp_path / "a").mkdir()
    file(tmp_path / "z", "one")
    file(tmp_path, "b")
    monkeypatch.setattr(os, "open", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    assert capture.tree(tmp_path) == ("a", "b", "z", "z/one")
    assert capture.tree(tmp_path / "a") == ()


@pytest.mark.parametrize("attack", ["symlink", "directory-link", "hardlink", "fifo", "control"])
def test_tree_admits_every_entry_before_contents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    folder = tmp_path / "tree"
    folder.mkdir()
    outside = file(tmp_path, "outside")
    path = folder / "entry"
    if attack.startswith("symlink") or attack == "directory-link":
        path.symlink_to(tmp_path if attack == "directory-link" else outside)
    elif attack == "hardlink":
        os.link(outside, path)
    elif attack == "fifo":
        os.mkfifo(path)
    else:
        file(folder, "unsafe\nname")
    monkeypatch.setattr(os, "open", forbidden)
    with pytest.raises(RunError):
        capture.tree(folder)


def test_tree_walk_error_is_explicit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    native = os.scandir

    def scandir(path: Path | str) -> Iterator[os.DirEntry[str]]:
        if Path(path) == nested:
            raise PermissionError("tree denied")
        return native(path)

    monkeypatch.setattr(os, "scandir", scandir)
    with pytest.raises(PermissionError, match="tree denied"):
        capture.tree(tmp_path)
