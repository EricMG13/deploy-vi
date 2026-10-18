"""A local HTTP server for the fetch tests: a table of path to response, run in a thread.

It listens on 127.0.0.1 only and every test reaches it through the `connector` seam, so no test
touches a real network. It records each request's path and headers for the credential tests.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Unpack

from rbotlib import fetch
from rbotlib.fetch import Page


@dataclass
class Route:
    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    chunked: bool = False
    delay: float = 0.0
    drip: float = 0.0  # seconds between single bytes of the body (or of everything)
    drip_headers: bool = False  # drip the status line and headers too


def html(body: str, content_type: str = "text/html; charset=utf-8") -> Route:
    return Route(headers={"Content-Type": content_type}, body=body.encode("utf-8"))


def redirect(location: str, status: int = 302, cookie: str = "") -> Route:
    headers = {"Location": location, **({"Set-Cookie": cookie} if cookie else {})}
    return Route(status=status, headers=headers)


class _Handler(BaseHTTPRequestHandler):
    server: _Server

    def do_GET(self) -> None:
        try:
            self._answer()
        except (BrokenPipeError, ConnectionResetError):
            return  # a client that refused early closes the socket under the handler

    def _answer(self) -> None:
        self.server.requests.append((self.path, dict(self.headers.items())))
        route = self.server.routes.get(self.path.split("?")[0], Route(status=404))
        time.sleep(route.delay)
        if route.drip:
            return self._dripped(route)
        self.send_response(route.status)
        for name, value in route.headers.items():
            self.send_header(name, value)
        if route.chunked:
            self.send_header("Transfer-Encoding", "chunked")
        elif "Content-Length" not in route.headers:
            self.send_header("Content-Length", str(len(route.body)))
        self.end_headers()
        if route.chunked:
            for start in range(0, len(route.body), 65536):
                piece = route.body[start : start + 65536]
                self.wfile.write(f"{len(piece):x}\r\n".encode() + piece + b"\r\n")
            self.wfile.write(b"0\r\n\r\n")
        else:
            self.wfile.write(route.body)

    def _dripped(self, route: Route) -> None:
        lines = [f"HTTP/1.0 {route.status} OK", f"Content-Length: {len(route.body)}"]
        lines += [f"{name}: {value}" for name, value in route.headers.items()]
        head = ("\r\n".join(lines) + "\r\n\r\n").encode()
        if not route.drip_headers:
            self.wfile.write(head)
            head = b""
        for byte in head + route.body:
            self.wfile.write(bytes([byte]))
            time.sleep(route.drip)

    def log_message(self, format: str, *args: object) -> None:
        return None


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    routes: dict[str, Route]
    requests: list[tuple[str, dict[str, str]]]


class FetchServer:
    """Use `with FetchServer(routes) as server`; `connector` dials it whatever the address."""

    def __init__(self, routes: dict[str, Route]) -> None:
        self._server = _Server(("127.0.0.1", 0), _Handler)
        self._server.routes = routes
        self._server.requests = []
        self.requests = self._server.requests
        self.dialed: list[tuple[str, int]] = []
        self.timeouts: list[float] = []
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return int(self._server.server_address[1])

    def __enter__(self) -> FetchServer:
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()

    def connector(self, address: str, port: int, timeout: float) -> socket.socket:
        self.dialed.append((address, port))
        self.timeouts.append(timeout)
        return socket.create_connection(("127.0.0.1", self.port), timeout)


HTML = {"Content-Type": "text/html"}
Starter = Callable[[dict[str, Route]], FetchServer]

PUBLIC = "93.184.216.34"

TODAY = date(2026, 10, 17)

PAGE = (
    "<html><head><title>Annual Report</title><script>var secret=1;</script></head>"
    "<body><p>Revenue grew.</p></body></html>"
)


def resolver(table: dict[str, str] | None = None) -> Callable[[str, int], list[str]]:
    return lambda host, port: [(table or {}).get(host, PUBLIC)]


def get(srv: FetchServer, url: str, **kw: Unpack[fetch.Seams]) -> Page:
    opts: fetch.Seams = {"resolver": resolver(), "connector": srv.connector, "today": TODAY}
    opts.update(kw)
    return fetch.fetch_page(url, **opts)
