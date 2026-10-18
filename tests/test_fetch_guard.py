"""The guarded socket and the bounded body read behind the fetch deadline."""

from __future__ import annotations

import socket

from fetch_server import (
    resolver,
)

from rbotlib import fetch


def test_the_socket_closes_only_when_the_connection_and_every_reader_are_closed() -> None:
    link = fetch._Link(resolver(), fetch.system_connector, None, 1, 100, lambda: 0)
    first, second = socket.socketpair()
    second.close()
    guard = fetch._Guarded(first, link)
    guard.close()
    assert first.fileno() == -1  # no reader: closed at once
    first, second = socket.socketpair()
    second.close()
    guard = fetch._Guarded(first, link)
    one, two = guard.makefile("rb"), guard.makefile("rb")
    guard.close()
    assert first.fileno() != -1
    one.close()
    one.close()  # closing a reader twice releases it once
    assert first.fileno() != -1
    two.close()
    assert first.fileno() == -1


def test_an_open_guard_survives_its_readers() -> None:
    link = fetch._Link(resolver(), fetch.system_connector, None, 1, 100, lambda: 0)
    first, second = socket.socketpair()
    guard = fetch._Guarded(first, link)
    reader = guard.makefile("rb")
    reader.close()
    assert first.fileno() != -1
    guard.close()
    assert first.fileno() == -1
    second.close()


def test_the_body_is_read_in_bounded_pieces() -> None:
    asked: list[int] = []

    class Slow:
        def __init__(self) -> None:
            self.pieces = [b"a", b"b", b""]

        def read(self, amount: int) -> bytes:
            asked.append(amount)
            return self.pieces.pop(0)

    assert fetch._read_body(Slow()) == b"ab"
    assert asked == [65536, 65536, 65536]
