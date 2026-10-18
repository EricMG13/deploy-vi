"""`rbot fetch` network core (Plan 10, rulings R1 and R4 to R8): the first network code in rbot.

`http.client` only: no proxy, cookie or implicit redirect behaviour. Every request, the first and
each redirect, goes through the URL policy, then a pinned connection: `connect()` resolves the
host, requires every answer to be a global address and dials the first one by IP, so a rebinding
answer cannot differ between check and connect. No cookies, no credentials, no compression.
Limits (bytes, time, content type, charset) refuse the page; nothing is saved on a refusal.

`resolver`, `connector` and `tls_context` are library-level seams for tests; the command line
exposes none of them.
"""

from __future__ import annotations

import http.client
import io
import ipaddress
import os
import re
import socket
import ssl
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, Protocol, TypedDict, Unpack, cast
from urllib.parse import SplitResult, quote, urljoin, urlsplit

from rbotlib import fetched
from rbotlib.inventory import RunError, output_path

if TYPE_CHECKING:
    from _typeshed import WriteableBuffer


MAX_URL = 2048
_HOST = re.compile(r"[a-z0-9.-]+")
_SKIP = frozenset({"script", "style", "noscript", "template", "svg"})
_CELLS = frozenset({"td", "th"})
_BREAKS = frozenset(
    "p br li tr div ul ol dl dt dd table thead tbody tfoot caption section article header footer "
    "nav aside main blockquote pre hr form fieldset figure figcaption address details summary "
    "h1 h2 h3 h4 h5 h6".split()
)
# IPv6 prefixes that carry an IPv4 address in their last 32 bits (IPv4-compatible, the NAT64
# well-known prefix, IPv4-translated): the embedded IPv4 address is judged, not the IPv6 form.
_EMBEDDED = tuple(
    ipaddress.IPv6Network(prefix) for prefix in ("::/96", "64:ff9b::/96", "::ffff:0:0:0/96")
)


class FetchRefused(RunError):
    """The fetch is refused by policy or a limit, or the network failed; nothing was saved."""


def available(env: Mapping[str, str] = os.environ) -> bool:
    return env.get("RBOT_FETCH") == "1"


def _judged(
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """The address to classify: an IPv4 address inside an IPv6 form is judged as that IPv4."""
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped:
            return ip.ipv4_mapped
        if any(ip in prefix for prefix in _EMBEDDED):
            return ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF)
    return ip


def check_address(address: str) -> None:
    """Refuse an address that is not a public unicast one."""
    try:
        ip = ipaddress.ip_address(address)
    except ValueError as exc:
        raise FetchRefused(f"{address} is not an IP address") from exc
    judged = _judged(ip)
    if not judged.is_global or judged.is_multicast:
        raise FetchRefused(f"address {address} is not a public address")


def _ascii_host(host: str) -> str:
    try:
        ascii_host = host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise FetchRefused(f"host name {host!r} is not valid") from exc
    if not _HOST.fullmatch(ascii_host):
        raise FetchRefused(f"host name {host!r} is not valid")
    return ascii_host


def check_url(url: str) -> SplitResult:
    """The URL without its fragment, or a refusal (R4 URL policy)."""
    if len(url) > MAX_URL:
        raise FetchRefused(f"URL is longer than {MAX_URL} characters")
    if any(ord(char) <= 32 or ord(char) == 127 for char in url):
        raise FetchRefused("URL holds a space or control character")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise FetchRefused(f"URL is not valid: {exc}") from exc
    if parts.scheme not in ("http", "https"):
        raise FetchRefused(f"URL scheme {parts.scheme!r} is not http or https")
    if "@" in parts.netloc:
        raise FetchRefused("URL holds credentials")
    host = parts.hostname or ""
    if "." not in host.rstrip("."):
        raise FetchRefused(f"host {host!r} is not a public DNS name")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise FetchRefused(f"host {host!r} is an IP address")
    _ascii_host(host)
    if port not in (None, 80, 443):
        raise FetchRefused(f"port {port} is not 80 or 443")
    return parts._replace(fragment="")


def _tidy(raw: str) -> str:
    lines = (" ".join(line.split()) for line in raw.split("\n"))
    return "\n".join(line for line in lines if line)


class _Text(HTMLParser):
    """Visible text and title; script, style, noscript, template, svg and comments are dropped."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title: list[str] = []
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP:
            self._skip += 1
        elif not self._skip:
            self._in_title = self._in_title or tag == "title"
            self.parts.append("\n" if tag in _BREAKS else " " if tag in _CELLS else "")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP:
            self._skip = max(0, self._skip - 1)
        elif not self._skip:
            self._in_title = self._in_title and tag != "title"
            self.parts.append("\n" if tag in _BREAKS else " " if tag in _CELLS else "")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            (self.title if self._in_title else self.parts).append(data)


def html_to_text(markup: str) -> tuple[str, str]:
    """`(title, text)`: block tags end lines, whitespace is collapsed, entities are decoded."""
    parser = _Text()
    parser.feed(markup)
    parser.close()
    return " ".join("".join(parser.title).split()), _tidy("".join(parser.parts))


MAX_BYTES = 2_097_152
MAX_REDIRECTS = 5
TIMEOUT_S = 20
DEADLINE_S = 60
ALLOWED_TYPES = ("text/html", "application/xhtml+xml", "text/plain")
REDIRECTS = (301, 302, 303, 307, 308)
HEADERS = {
    "User-Agent": "rbot-fetch/1",
    "Accept": ", ".join(ALLOWED_TYPES),
    "Accept-Encoding": "identity",
    "Connection": "close",
}
_PATH_SAFE = "/%:@!$&'()*+,;=~-._"

Resolver = Callable[[str, int], list[str]]
Connector = Callable[[str, int, float], socket.socket]


class TlsContext(Protocol):
    def wrap_socket(self, sock: socket.socket, *, server_hostname: str) -> socket.socket: ...


class Page(NamedTuple):
    url: str
    final_url: str
    retrieved: str
    content_type: str
    title: str
    text: str

    @property
    def body(self) -> str:
        """The text that is saved: `# <title>`, a blank line, then the page text."""
        return (f"# {self.title}\n\n" if self.title else "") + self.text + "\n"


def system_resolver(host: str, port: int) -> list[str]:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return list(dict.fromkeys(str(info[4][0]) for info in infos))


def system_connector(address: str, port: int, timeout: float) -> socket.socket:
    return socket.create_connection((address, port), timeout)


def default_tls_context() -> ssl.SSLContext:
    return ssl.create_default_context()


@dataclass
class _Link:
    """How one fetch reaches the network, and the time it has left."""

    resolver: Resolver
    connector: Connector
    tls_context: TlsContext | None
    timeout: float
    end: float
    clock: Callable[[], float]

    def budget(self) -> float:
        """One socket operation's timeout: `timeout`, cut to the time left before the deadline."""
        left = self.end - self.clock()
        if left <= 0:
            raise FetchRefused("fetch exceeded the deadline")
        return min(self.timeout, left)

    def pin(self, host: str, port: int) -> str:
        """The first resolved address, after every answer passed `check_address`."""
        try:
            answers = self.resolver(host, port)
        except OSError as exc:
            raise FetchRefused(f"cannot resolve {host}") from exc
        if not answers:
            raise FetchRefused(f"cannot resolve {host}")
        for answer in answers:
            check_address(answer)
        return answers[0]


class _Guarded:
    """What http.client sees as the socket: every send and every recv first re-arms the socket
    timeout from the link's budget, so `deadline` bounds the whole fetch even against a server
    that drips one byte at a time. The real socket closes when the connection and every reader
    made from it are closed."""

    def __init__(self, sock: socket.socket, link: _Link) -> None:
        self.sock, self._link = sock, link
        self._readers, self._closed = 0, False

    def arm(self) -> None:
        self.sock.settimeout(self._link.budget())

    def sendall(self, data: bytes) -> None:
        self.arm()
        self.sock.sendall(data)

    def makefile(self, mode: str) -> io.BufferedReader:
        self._readers += 1
        return io.BufferedReader(_Reader(self))

    def release(self) -> None:
        self._readers -= 1
        self._shut()

    def close(self) -> None:
        self._closed = True
        self._shut()

    def _shut(self) -> None:
        if self._closed and self._readers <= 0:
            self.sock.close()


class _Reader(io.RawIOBase):
    def __init__(self, guard: _Guarded) -> None:
        super().__init__()
        self._guard = guard

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: WriteableBuffer) -> int:
        self._guard.arm()
        return self._guard.sock.recv_into(buffer)

    def close(self) -> None:
        if not self.closed:
            super().close()
            self._guard.release()


class _Pinned(http.client.HTTPConnection):
    """An HTTP connection whose `connect()` dials a checked address; https verifies the host."""

    def __init__(self, host: str, port: int, link: _Link, *, tls: bool) -> None:
        super().__init__(host, port)
        self.default_port = 443 if tls else 80
        self._link, self._tls = link, tls

    def connect(self) -> None:
        link = self._link
        sock = link.connector(link.pin(self.host, self.port), self.port, link.budget())
        if self._tls:
            context = link.tls_context or default_tls_context()
            sock = context.wrap_socket(sock, server_hostname=self.host)
        self.sock = cast(socket.socket, _Guarded(sock, link))


class _Reply(NamedTuple):
    status: int
    headers: http.client.HTTPMessage
    body: bytes


def _check_headers(headers: http.client.HTTPMessage) -> None:
    if headers.get("Content-Type") is None:
        raise FetchRefused("page has no content type")
    kind = headers.get_content_type()
    if kind not in ALLOWED_TYPES:
        raise FetchRefused(f"unsupported content type {kind}")
    length = headers.get("Content-Length")
    try:
        size = int(length) if length is not None else 0
    except ValueError as exc:
        raise FetchRefused("page has an invalid Content-Length") from exc
    if size > MAX_BYTES:
        raise FetchRefused(f"page is larger than {MAX_BYTES} bytes")


class _Readable(Protocol):
    def read(self, amount: int, /) -> bytes: ...


def _read_body(response: _Readable) -> bytes:
    body = bytearray()
    while chunk := response.read(65536):
        body += chunk
        if len(body) > MAX_BYTES:
            raise FetchRefused(f"page is larger than {MAX_BYTES} bytes")
    return bytes(body)


def _target(parts: SplitResult) -> str:
    query = f"?{quote(parts.query, safe=_PATH_SAFE + '?')}" if parts.query else ""
    return quote(parts.path or "/", safe=_PATH_SAFE) + query


def _hop(url: str, link: _Link) -> _Reply:
    """One request to a checked URL. A 200 is read within the limits; a redirect is not read."""
    parts = check_url(url)
    tls = parts.scheme == "https"
    host = _ascii_host(parts.hostname or "")
    conn = _Pinned(host, parts.port or (443 if tls else 80), link, tls=tls)
    try:
        conn.request("GET", _target(parts), headers=HEADERS)
        response = conn.getresponse()
        body = b""
        if response.status == 200:
            _check_headers(response.headers)
            body = _read_body(response)
        return _Reply(response.status, response.headers, body)
    except (OSError, http.client.HTTPException) as exc:
        if link.clock() >= link.end:  # the socket timed out because the deadline cut it short
            raise FetchRefused("fetch exceeded the deadline") from exc
        raise FetchRefused(f"fetch failed: {type(exc).__name__}: {exc}") from exc
    finally:
        conn.close()


def _redirect_to(current: str, headers: http.client.HTTPMessage) -> str:
    location = headers.get("Location")
    if not location:
        raise FetchRefused("redirect has no Location")
    target = urljoin(current, location)
    if urlsplit(current).scheme == "https" and urlsplit(target).scheme == "http":
        raise FetchRefused("redirect from https to http (downgrade)")
    return check_url(target).geturl()


def _page(url: str, final_url: str, reply: _Reply, today: date | None) -> Page:
    kind = reply.headers.get_content_type()
    charset = reply.headers.get_content_charset() or "utf-8"
    try:
        markup = reply.body.decode(charset)
    except (LookupError, UnicodeDecodeError) as exc:
        raise FetchRefused(f"page cannot be decoded as {charset}") from exc
    title, text = ("", _tidy(markup)) if kind == "text/plain" else html_to_text(markup)
    if not text:
        raise FetchRefused("page has no text")
    retrieved = (today or datetime.now(UTC).date()).isoformat()
    return Page(url, final_url, retrieved, kind, title, text)


class Seams(TypedDict, total=False):
    """The keyword arguments of `fetch_page`; each has a production default."""

    resolver: Resolver
    connector: Connector
    tls_context: TlsContext
    timeout: float
    deadline: float
    today: date
    clock: Callable[[], float]


def fetch_page(url: str, **seams: Unpack[Seams]) -> Page:
    """Fetch one public page: every hop checked and pinned, within the byte, time, type limits.

    Keywords (all optional): `resolver(host, port) -> list[str]`, `connector(address, port,
    timeout) -> socket`, `tls_context` with `wrap_socket(sock, server_hostname=...)`,
    `timeout` per socket operation, `deadline` for the whole fetch, `today`, `clock`.
    """
    clock = seams.get("clock", time.monotonic)
    link = _Link(
        seams.get("resolver", system_resolver),
        seams.get("connector", system_connector),
        seams.get("tls_context"),
        seams.get("timeout", TIMEOUT_S),
        clock() + seams.get("deadline", DEADLINE_S),
        clock,
    )
    first = check_url(url).geturl()
    current = first
    for redirects in range(MAX_REDIRECTS + 1):
        reply = _hop(current, link)
        if reply.status not in REDIRECTS:
            break
        if redirects == MAX_REDIRECTS:
            raise FetchRefused(f"too many redirects (more than {MAX_REDIRECTS})")
        current = _redirect_to(current, reply.headers)
    if reply.status != 200:
        raise FetchRefused(f"page answered with status {reply.status}")
    return _page(first, current, reply, seams.get("today"))


MAX_SAVED = 99
_QUESTION = re.compile(r"[A-Za-z0-9_.-]{1,32}")


def save_page(run: Path, page: Page, question: str) -> Path:
    """Save the page as `fetched/<nn>-<host>.md`.

    A URL already saved returns its existing path and writes nothing.
    """
    if not _QUESTION.fullmatch(question):
        raise FetchRefused(f"question {question!r} is not a question id")
    folder = output_path(run, fetched.FOLDER)
    if (existing := fetched.saved_path(run, page.url)) is not None:
        return existing
    try:
        folder.mkdir(exist_ok=True)
    except FileExistsError as exc:
        raise FetchRefused(f"{folder} is not a folder") from exc
    taken = [int(m[1]) for p in folder.iterdir() if (m := fetched.NAME.fullmatch(p.name))]
    number = max(taken, default=0) + 1
    if number > MAX_SAVED:
        raise FetchRefused(f"fetched/ is full ({MAX_SAVED} pages)")
    host = _ascii_host(urlsplit(page.url).hostname or "")[:80]
    path = output_path(run, f"{fetched.FOLDER}/{number:02d}-{host}.md")
    front = {
        "url": page.url,
        "final_url": page.final_url,
        "retrieved": page.retrieved,
        "question": question,
        "content_type": page.content_type,
    }
    text = fetched.render(front, page.body)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        with os.fdopen(os.open(path, flags, 0o644), "wb") as handle:
            handle.write(text.encode("utf-8"))
    except FileExistsError as exc:
        raise FetchRefused(f"{path.name} already exists") from exc
    except OSError:
        path.unlink(missing_ok=True)
        raise
    return path
