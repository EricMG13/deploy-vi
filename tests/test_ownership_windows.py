"""Windows dispatch of the run lock. The msvcrt double proves only the dispatch path."""

import errno
import os
import sys
import types
from collections.abc import Iterator
from pathlib import Path

import pytest

from rbotlib import ownership
from rbotlib.inventory import RunError


class FakeMsvcrt(types.ModuleType):
    LK_NBLCK = 2

    def __init__(self, fail: int | None = None) -> None:
        super().__init__("msvcrt")
        self.fail = fail
        self.calls: list[tuple[int, int, int]] = []

    def locking(self, fd: int, mode: int, nbytes: int) -> None:
        self.calls.append((os.lseek(fd, 0, os.SEEK_CUR), mode, nbytes))
        if self.fail is not None:
            raise OSError(self.fail, "double")


@pytest.fixture
def fd(tmp_path: Path) -> Iterator[int]:
    handle = os.open(tmp_path / "lock", os.O_RDWR | os.O_CREAT)
    os.write(handle, b"abc")  # position is not 0
    yield handle
    os.close(handle)


def use(monkeypatch: pytest.MonkeyPatch, name: str, double: FakeMsvcrt | None) -> None:
    monkeypatch.setattr(os, "name", name)
    if double is not None:
        monkeypatch.setitem(sys.modules, "msvcrt", double)


def test_nt_locks_one_byte_past_the_sentinel(monkeypatch: pytest.MonkeyPatch, fd: int) -> None:
    """Windows byte-range locks are mandatory: the sentinel bytes must stay readable elsewhere."""
    double = FakeMsvcrt()
    use(monkeypatch, "nt", double)
    ownership._kernel(fd)
    assert double.calls == [(ownership.LOCK_OFFSET, FakeMsvcrt.LK_NBLCK, 1)]
    assert ownership.LOCK_OFFSET >= 1 << 30 > len(ownership.MAGIC) + 33
    assert os.lseek(fd, 0, os.SEEK_CUR) == 0  # the sentinel write that follows starts at 0


@pytest.mark.parametrize("code", [errno.EACCES, errno.EDEADLK])
def test_nt_contention_is_busy(monkeypatch: pytest.MonkeyPatch, fd: int, code: int) -> None:
    use(monkeypatch, "nt", FakeMsvcrt(fail=code))
    with pytest.raises(RunError, match="busy"):
        ownership._kernel(fd)


def test_nt_other_oserror_reraises(monkeypatch: pytest.MonkeyPatch, fd: int) -> None:
    use(monkeypatch, "nt", FakeMsvcrt(fail=errno.EBADF))
    with pytest.raises(OSError) as info:
        ownership._kernel(fd)
    assert not isinstance(info.value, RunError)
    assert info.value.errno == errno.EBADF


def test_other_platform_still_refuses(monkeypatch: pytest.MonkeyPatch, fd: int) -> None:
    double = FakeMsvcrt()
    use(monkeypatch, "java", double)
    with pytest.raises(RunError, match="unsupported"):
        ownership._kernel(fd)
    assert double.calls == []


def test_lock_file_opens_binary_where_the_crt_has_text_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Text mode would write the sentinel newline as CRLF and break the length check."""
    flags: list[int] = []
    real = os.open

    def spy(path: str | os.PathLike[str], flag: int, mode: int = 0o777) -> int:
        flags.append(flag)
        return real(path, flag & ~0x8000, mode)

    monkeypatch.setattr(os, "O_BINARY", 0x8000, raising=False)
    monkeypatch.setattr(os, "open", spy)
    ownership.Owner(tmp_path, "lock", None).close()
    assert flags and flags[0] & 0x8000
