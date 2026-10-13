"""One guarded command row; managed completion may correct only its owned suffix."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rbotlib import ownership, state
from rbotlib.inventory import RunError, output_path
from rbotlib.model.run import stage_file

LOCK = "log/.rbot-log.lock"


def path(run: Path) -> Path:
    destination = output_path(run, "log/rbot.log")
    if destination.parent.exists() and not destination.parent.is_dir():
        raise RunError(f"{destination.parent}: log parent must be a directory")
    if destination.exists() and not destination.is_file():
        raise RunError(f"{destination}: log must be a regular file")
    return destination


def _entitlement(run: Path) -> dict[str, object] | None:
    record = state.write_guard(run)
    expected: dict[str, object] | None = record["ownership"]["log"] if record is not None else None
    return expected


class _StandaloneOwner:
    """Original no-state O_EXCL sentinel and owned cleanup; no stable entitlement."""

    def __init__(self, run: Path) -> None:
        self.run = run
        try:
            fd = os.open(output_path(run, LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise RunError("another command holds the run log lock") from exc
        self.identity = os.fstat(fd)
        os.close(fd)

    def check(self) -> None:
        observed = output_path(self.run, LOCK).lstat()
        if (observed.st_dev, observed.st_ino) != (self.identity.st_dev, self.identity.st_ino):
            raise RunError("log: owned lock identity changed; cleanup refused")

    def close(self) -> None:
        self.check()
        output_path(self.run, LOCK).unlink()


class Receipt:
    """Keep cooperating appenders out until this invocation's row is resolved."""

    def __init__(
        self, run: Path, argv: list[str], state_owner: state._Locked | None = None
    ) -> None:
        self.run = run
        self.invocation = uuid4().hex
        expected = _entitlement(run)
        if state_owner is not None:
            if state_owner.run != run:
                raise RunError("log: borrowed state owner belongs to another run")
            state_owner.owner.check()
        destination = path(run)
        self.state_owner = (
            state._Locked(run) if expected is not None and state_owner is None else None
        )
        self.lock = output_path(run, LOCK)
        try:
            destination.parent.mkdir(exist_ok=True)
            self.owner = (
                ownership.Owner(run, LOCK, expected)
                if expected is not None
                else _StandaloneOwner(run)
            )
        except BaseException:
            if self.state_owner is not None:
                self.state_owner.close()
            raise
        self.identity = (
            os.fstat(self.owner.fd)
            if isinstance(self.owner, ownership.Owner)
            else self.owner.identity
        )
        self.prefix = b""
        self.state = "unobserved"
        stamp = datetime.now(UTC).isoformat(timespec="seconds")
        command = json.dumps(" ".join(argv), ensure_ascii=True)[1:-1]
        self.row = f"{stamp}\t{command}\t".encode()
        try:
            self.prefix = path(run).read_bytes() if destination.exists() else b""
            self.state = "missing"
        except (OSError, ValueError) as capture_error:
            try:
                self.close()
            except (OSError, ValueError) as cleanup_error:
                raise RunError(
                    f"log prefix capture failed: {capture_error}; cleanup failed: {cleanup_error}"
                ) from capture_error
            raise

    def append(self, code: int) -> None:
        self.owner.check()
        actual = path(self.run).read_bytes() if path(self.run).exists() else b""
        if actual != self.prefix:
            raise RunError("log: original prefix changed; append refused")
        if self.state_owner is not None:
            from rbotlib.host_evidence import following

            following(self.state_owner, self, code)
            from rbotlib.command_receipts import begin

            begin(self.state_owner, self, code)
        self.state = f"candidate{code}"
        suffix = self.row + f"{code}\n".encode()
        staged = stage_file(path(self.run), self.prefix + suffix)
        try:
            self.owner.check()
            os.replace(staged, path(self.run))
        finally:
            staged.unlink(missing_ok=True)
        if path(self.run).read_bytes() != self.prefix + suffix:
            raise RunError("log: appended row readback differs")
        self.state = f"row{code}"
        if self.state_owner is not None:
            from rbotlib.command_receipts import finish

            finish(self.state_owner, self)
            self.owner.check()
            if path(self.run).read_bytes() != self.prefix + self.row + f"{code}\n".encode():
                raise RunError("log: final row readback differs")

    def fail(self) -> None:
        """Never append blindly after an ambiguous write or alter another row."""
        self.owner.check()
        if self.state == "unobserved":
            raise RunError("log: prefix ownership was not observed")
        destination = path(self.run)
        actual = destination.read_bytes() if destination.exists() else b""
        if not actual.startswith(self.prefix):
            self.state = "unowned-prefix"
            raise RunError("log: original prefix changed; correction refused")
        suffix = actual[len(self.prefix) :]
        candidates = (self.row + b"0\n", self.row + b"1\n")
        if not any(candidate.startswith(suffix) for candidate in candidates):
            self.state = "unowned-suffix"
            raise RunError("log: unowned suffix; correction refused")
        self.state = {b"": "missing", candidates[0]: "row0", candidates[1]: "row1"}.get(
            suffix, "partial"
        )
        if self.state_owner is not None:
            from rbotlib.host_evidence import following

            following(self.state_owner, self, 1)
            from rbotlib.command_receipts import begin

            begin(self.state_owner, self, 1)
        staged = stage_file(destination, self.prefix + self.row + b"1\n")
        try:
            self.owner.check()
            os.replace(staged, path(self.run))
            self.state = "correction1-unverified"
        finally:
            staged.unlink(missing_ok=True)
        if path(self.run).read_bytes() != self.prefix + self.row + b"1\n":
            raise RunError("log: correction readback differs")
        self.state = "row1"
        if self.state_owner is not None:
            from rbotlib.command_receipts import finish

            finish(self.state_owner, self)
            self.owner.check()
            if path(self.run).read_bytes() != self.prefix + self.row + b"1\n":
                raise RunError("log: final correction readback differs")

    def close(self) -> None:
        try:
            self.owner.close()
        finally:
            if self.state_owner is not None:
                warnings = self.state_owner.close()
                if warnings:
                    raise RunError("; ".join(warnings))


def append(run: Path, argv: list[str], code: int, receipt: Receipt | None = None) -> None:
    if receipt is not None:
        if receipt.run != run:
            raise RunError("log: receipt belongs to another run")
        receipt.append(code)
        return
    owned = Receipt(run, argv)
    try:
        owned.append(code)
    finally:
        owned.close()
