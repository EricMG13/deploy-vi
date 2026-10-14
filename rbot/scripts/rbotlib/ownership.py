"""Stable local process locks; no age, PID or missing-output inference."""

from __future__ import annotations

import errno
import importlib
import os
import re
import stat
from pathlib import Path
from typing import Any
from uuid import uuid4

from rbotlib.inventory import RunError, output_path

MAGIC = b"rbot-owner/1 "
LOG = "log/.rbot-log.lock"


_BUSY = "another state update, Approval or command holds this run (.approve.lock); busy"


def _kernel(descriptor: int) -> None:
    if os.name == "nt":
        msvcrt: Any = importlib.import_module("msvcrt")  # absent from POSIX type stubs
        # The MSVC CRT locks from the current position, so lock byte 0 explicitly.
        os.lseek(descriptor, 0, os.SEEK_SET)
        try:
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EDEADLK):
                raise RunError(_BUSY) from exc
            raise
        return
    if os.name != "posix":
        raise RunError("process ownership unsupported on this platform")
    import fcntl

    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EAGAIN):
            raise RunError(_BUSY) from exc
        raise


class Owner:
    """Retain a non-inheritable descriptor; never remove the reserved legacy fence."""

    def __init__(
        self,
        run: Path,
        name: str,
        expected: dict[str, object] | None,
    ) -> None:
        self.run, self.name = run, name
        if expected is not None and (
            not isinstance(expected, dict)
            or set(expected) != {"bytes", "device", "inode"}
            or not isinstance(expected.get("bytes"), str)
            or type(expected.get("device")) is not int
            or type(expected.get("inode")) is not int
        ):
            raise RunError(f"{name}: malformed ownership entitlement")
        target = output_path(run, name)
        flags = os.O_RDWR | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        if expected is None:
            flags |= os.O_CREAT | os.O_EXCL
        try:
            self.fd = os.open(target, flags, 0o600)
        except FileExistsError as exc:
            raise RunError(
                f"{name}: unknown legacy/initialization sentinel; ownership unresolved"
            ) from exc
        try:
            self.pid = os.getpid()
            os.set_inheritable(self.fd, False)
            _kernel(self.fd)
            if expected is None:
                raw = MAGIC + uuid4().hex.encode() + b"\n"
                os.write(self.fd, raw)
                os.fsync(self.fd)
                identity = os.fstat(self.fd)
                self.entitlement: dict[str, object] = {
                    "bytes": raw.decode(),
                    "device": identity.st_dev,
                    "inode": identity.st_ino,
                }
            else:
                self.entitlement = expected
            self.check()
        except BaseException:
            os.close(self.fd)
            raise

    def check(self) -> None:
        observed = output_path(self.run, self.name).lstat()
        opened = os.fstat(self.fd)
        if not stat.S_ISREG(opened.st_mode):
            raise RunError(f"{self.name}: ownership requires a regular file")
        os.lseek(self.fd, 0, os.SEEK_SET)
        raw = os.read(self.fd, 128)
        if (
            os.getpid() != self.pid
            or not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
            or (observed.st_dev, observed.st_ino) != (opened.st_dev, opened.st_ino)
            or observed.st_dev != self.entitlement.get("device")
            or observed.st_ino != self.entitlement.get("inode")
            or raw.decode("ascii") != self.entitlement.get("bytes")
            or re.fullmatch(re.escape(MAGIC) + rb"[0-9a-f]{32}\n", raw) is None
        ):
            raise RunError(
                f"{self.name}: owned lock identity/protocol changed; publication refused"
            )

    def close(self) -> None:
        try:
            self.check()
        finally:
            os.close(self.fd)


def existing(run: Path, name: str) -> dict[str, object]:
    target = output_path(run, name)
    identity = target.lstat()
    if not stat.S_ISREG(identity.st_mode):
        raise RunError(f"{name}: ownership requires a regular file")
    raw = target.read_bytes()
    if not raw.startswith(MAGIC) or len(raw) != len(MAGIC) + 33:
        raise RunError(f"{name}: unknown legacy sentinel; ownership unresolved")
    return {"bytes": raw.decode("ascii"), "device": identity.st_dev, "inode": identity.st_ino}


def provision(run: Path, lock: str, record: dict[str, Any]) -> Owner:
    """Reserve both sentinel names in the fresh unpublished new-run allocation only."""
    if any(run.iterdir()):
        raise RunError("ownership provisioning requires an empty unpublished allocation")
    owner = Owner(run, lock, None)
    try:
        output_path(run, "log").mkdir(exist_ok=True)
        log = Owner(run, LOG, None)
        try:
            record["ownership"] = {
                "schema": "rbot-process-owner/1",
                "state": owner.entitlement,
                "log": log.entitlement,
            }
        finally:
            log.close()
    except BaseException:
        owner.close()
        raise
    return owner
