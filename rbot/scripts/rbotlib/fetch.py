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

import ipaddress
import os
import re
from collections.abc import Mapping
from html.parser import HTMLParser
from urllib.parse import SplitResult, urlsplit

from rbotlib.inventory import RunError

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
