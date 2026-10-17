"""`rbotlib.fetch` network core: pinned connection, redirects, limits and the deadline.

No test touches a network: the resolver and connector seams point at `tests/fetch_server.py`
on 127.0.0.1.
"""

from __future__ import annotations

import socket
import time
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from fetch_server import (
    HTML,
    PAGE,
    PUBLIC,
    Route,
    Starter,
    get,
    html,
    redirect,
    resolver,
)

from rbotlib import fetch
from rbotlib.fetch import FetchRefused


def test_every_answer_is_checked() -> None:
    dialed: list[str] = []

    def connector(address: str, port: int, timeout: float) -> socket.socket:
        dialed.append(address)
        raise AssertionError("must not connect")

    with pytest.raises(FetchRefused, match=r"10\.0\.0\.1"):
        fetch.fetch_page(
            "http://pub.example/",
            resolver=lambda host, port: [PUBLIC, "10.0.0.1"],
            connector=connector,
        )
    assert dialed == []


def test_no_answer_is_refused() -> None:
    with pytest.raises(FetchRefused, match=r"^cannot resolve pub.example$"):
        fetch.fetch_page("http://pub.example/", resolver=lambda host, port: [])


def test_redirect_to_private_address_is_refused(server: Starter) -> None:
    srv = server({"/": redirect("http://internal.example/")})
    with pytest.raises(FetchRefused, match=r"10\.0\.0\.5"):
        get(srv, "http://pub.example/", resolver=resolver({"internal.example": "10.0.0.5"}))
    assert srv.dialed == [(PUBLIC, 80)]


def chain(count: int) -> dict[str, Route]:
    routes = {f"/r{i}": redirect(f"/r{i + 1}") for i in range(count)}
    routes[f"/r{count}"] = html(PAGE)
    return routes


def test_five_redirects_are_followed(server: Starter) -> None:
    page = get(server(chain(5)), "http://pub.example/r0")
    assert page.final_url == "http://pub.example/r5"


def test_redirect_limit(server: Starter) -> None:
    with pytest.raises(FetchRefused, match="too many redirects"):
        get(server(chain(6)), "http://pub.example/r0")


@pytest.mark.parametrize(
    "location",
    [
        "http://user:pw@pub.example/x",
        "ftp://pub.example/x",
        "http://127.0.0.1/x",
        "",
    ],
)
def test_bad_redirect_targets_are_refused(server: Starter, location: str) -> None:
    srv = server({"/": redirect(location)})
    with pytest.raises(FetchRefused):
        get(srv, "http://pub.example/")


def test_https_to_http_is_refused(server: Starter) -> None:
    srv = server({"/": redirect("http://pub.example/x")})
    with pytest.raises(FetchRefused, match=r"^redirect from https to http \(downgrade\)$"):
        get(srv, "https://pub.example/", tls_context=PassContext())


def test_a_redirect_without_a_location_is_refused(server: Starter) -> None:
    with pytest.raises(FetchRefused, match=r"^redirect has no Location$"):
        get(server({"/": Route(status=302)}), "http://pub.example/")


@pytest.mark.parametrize("status", [301, 303, 307, 308])
def test_each_redirect_status_is_followed(server: Starter, status: int) -> None:
    srv = server({"/": redirect("/p", status=status), "/p": html(PAGE)})
    assert get(srv, "http://pub.example/").final_url == "http://pub.example/p"


class PassContext:
    """A stand-in TLS context: records the host name it is asked to verify, passes the socket on."""

    def __init__(self) -> None:
        self.hosts: list[str] = []

    def wrap_socket(self, sock: socket.socket, *, server_hostname: str) -> socket.socket:
        self.hosts.append(server_hostname)
        return sock


def test_https_connection_verifies_the_host(server: Starter) -> None:
    context = PassContext()
    srv = server({"/page": html(PAGE)})
    page = get(srv, "https://pub.example/page", tls_context=context)
    assert context.hosts == ["pub.example"]
    assert srv.dialed == [(PUBLIC, 443)]
    assert page.url == "https://pub.example/page"
    assert srv.requests[0][1]["Host"] == "pub.example"


def test_plain_http_never_wraps(server: Starter) -> None:
    context = PassContext()
    get(server({"/": html(PAGE)}), "http://pub.example/", tls_context=context)
    assert context.hosts == []


def test_request_carries_no_credentials(server: Starter) -> None:
    srv = server({"/": redirect("/next", cookie="sid=1"), "/next": html(PAGE)})
    get(srv, "http://pub.example/")
    assert len(srv.requests) == 2
    for _, headers in srv.requests:
        assert "Authorization" not in headers
        assert headers["User-Agent"] == "rbot-fetch/1"
        assert headers["Accept-Encoding"] == "identity"
    assert "Cookie" not in srv.requests[1][1]


def test_the_default_context_verifies_certificates() -> None:
    context = fetch.default_tls_context()
    assert context.check_hostname is True
    assert context.verify_mode.name == "CERT_REQUIRED"


def test_text_plain_is_kept(server: Starter) -> None:
    routes = {"/": html("  line one \n\n  line   two\n", "text/plain")}
    page = get(server(routes), "http://pub.example/")
    assert (page.title, page.text, page.content_type) == ("", "line one\nline two", "text/plain")


LIMITS = {
    "content-length": (Route(headers={**HTML, "Content-Length": "2097153"}), "larger than 2097152"),
    "chunked": (Route(headers=HTML, body=b"a" * 2_097_153, chunked=True), "larger than 2097152"),
    "bad-length": (Route(headers={**HTML, "Content-Length": "x"}), "invalid Content-Length$"),
    "pdf": (Route(headers={"Content-Type": "application/pdf"}), "^unsupported content type "),
    "no-type": (Route(body=b"<p>no type</p>"), "^page has no content type$"),
    "charset": (
        Route(headers={**HTML, "Content-Type": "text/html; charset=nope"}, body=b"<p>x</p>"),
        "decoded as nope$",
    ),
    "bad-utf8": (Route(headers=HTML, body=b"<p>\xff\xfe</p>"), "decoded as utf-8$"),
    "script-only": (Route(headers=HTML, body=b"<script>x</script>"), "^page has no text$"),
    "slow": (Route(headers=HTML, body=b"<p>slow</p>", delay=0.6), "^fetch failed: TimeoutError"),
    "404": (
        Route(status=404, headers=HTML, body=b"<p>gone</p>"),
        "^page answered with status 404$",
    ),
}


@pytest.mark.parametrize(("route", "reason"), LIMITS.values(), ids=list(LIMITS))
def test_limits_refuse_and_save_nothing(
    server: Starter, tmp_path: Path, route: Route, reason: str
) -> None:
    with pytest.raises(FetchRefused, match=reason):
        get(server({"/": route}), "http://pub.example/", timeout=0.2)
    assert not (tmp_path / "fetched").exists()


def test_a_body_of_exactly_the_cap_passes(server: Starter) -> None:
    body = b"<p>" + b"a" * (2_097_152 - 3)
    route = Route(headers={"Content-Type": "text/html"}, body=body)
    assert len(get(server({"/": route}), "http://pub.example/").text) > 2_000_000
    chunked = Route(headers={"Content-Type": "text/html"}, body=body, chunked=True)
    assert len(get(server({"/": chunked}), "http://pub.example/").text) > 2_000_000


def test_a_declared_charset_is_used(server: Starter) -> None:
    route = Route(
        headers={"Content-Type": "text/html; charset=iso-8859-1"},
        body="<p>caf\xe9</p>".encode("latin-1"),
    )
    assert get(server({"/": route}), "http://pub.example/").text == "caf\xe9"


def test_a_failed_connection_is_a_refusal() -> None:
    def refuse(address: str, port: int, timeout: float) -> socket.socket:
        raise ConnectionRefusedError("no route")

    with pytest.raises(FetchRefused, match=r"^fetch failed: ConnectionRefusedError: no route$"):
        fetch.fetch_page("http://pub.example/", resolver=resolver(), connector=refuse)


def test_a_resolver_error_is_a_refusal() -> None:
    def broken(host: str, port: int) -> list[str]:
        raise socket.gaierror("nope")

    with pytest.raises(FetchRefused, match="resolve"):
        fetch.fetch_page("http://pub.example/", resolver=broken)


def test_the_deadline_bounds_the_whole_fetch(server: Starter) -> None:
    ticks = iter(range(0, 1000, 10))
    with pytest.raises(FetchRefused, match="deadline"):
        get(server(chain(3)), "http://pub.example/r0", deadline=25, clock=lambda: next(ticks))


def test_the_deadline_bounds_each_read(server: Starter) -> None:
    body = b"<p>" + b"a" * 200_000
    route = Route(headers={"Content-Type": "text/html"}, body=body)
    ticks = iter([0, 1, 2, 3, 100, 101, 102])
    with pytest.raises(FetchRefused, match=r"^fetch exceeded the deadline$"):
        get(server({"/": route}), "http://pub.example/", deadline=50, clock=lambda: next(ticks))


def test_the_resolver_gets_the_host_and_port_and_http_names_no_port(server: Starter) -> None:
    asked: list[tuple[str, int]] = []

    def record(host: str, port: int) -> list[str]:
        asked.append((host, port))
        return [PUBLIC]

    srv = server({"/": html(PAGE)})
    get(srv, "http://pub.example/", resolver=record)
    assert asked == [("pub.example", 80)]
    assert srv.requests[0][1]["Host"] == "pub.example"
    get(srv, "http://pub.example:443/", resolver=record)
    assert srv.requests[1][1]["Host"] == "pub.example:443"


def test_the_request_target_is_quoted_and_never_empty(server: Starter) -> None:
    srv = server({"/": html(PAGE), "/caf%C3%A9": html(PAGE), "/a%20b": html(PAGE)})
    get(srv, "http://pub.example")
    get(srv, "http://pub.example/café?q=a?b&r=a/b&s=x%20y&t=é")
    get(srv, "http://pub.example/a%20b")
    assert [path for path, _ in srv.requests] == [
        "/",
        "/caf%C3%A9?q=a?b&r=a/b&s=x%20y&t=%C3%A9",
        "/a%20b",
    ]


def test_text_plain_is_not_parsed_as_html(server: Starter) -> None:
    route = html("x &amp; y <b>z</b>", "text/plain")
    assert get(server({"/": route}), "http://pub.example/").text == "x &amp; y <b>z</b>"


def test_the_retrieval_date_is_the_given_day_or_today_in_utc(server: Starter) -> None:
    srv = server({"/": html(PAGE)})
    assert get(srv, "http://pub.example/", today=date(2020, 1, 2)).retrieved == "2020-01-02"
    opts: fetch.Seams = {"resolver": resolver(), "connector": srv.connector}
    page = fetch.fetch_page("http://pub.example/", **opts)
    assert page.retrieved == datetime.now(UTC).date().isoformat()


def test_the_production_seams_are_the_defaults(
    server: Starter, monkeypatch: pytest.MonkeyPatch
) -> None:
    srv = server({"/": html(PAGE)})
    monkeypatch.setattr(fetch, "system_resolver", resolver())
    monkeypatch.setattr(fetch, "system_connector", srv.connector)
    assert fetch.fetch_page("http://pub.example/").text == "Revenue grew."
    assert fetch.TIMEOUT_S == 20 and fetch.DEADLINE_S == 60 and fetch.MAX_BYTES == 2_097_152


@pytest.mark.parametrize("in_headers", [True, False], ids=["headers", "body"])
def test_a_slow_drip_cannot_outlast_the_deadline(
    server: Starter, tmp_path: Path, in_headers: bool
) -> None:
    route = Route(headers=HTML, body=b"<p>" + b"a" * 100, drip=0.1, drip_headers=in_headers)
    started = time.monotonic()
    with pytest.raises(FetchRefused, match="deadline"):
        get(server({"/": route}), "http://pub.example/", timeout=0.5, deadline=1.0)
    assert time.monotonic() - started < 1.5
    assert not (tmp_path / "fetched").exists()


def test_the_connector_gets_the_per_operation_timeout(server: Starter) -> None:
    srv = server({"/": html(PAGE)})
    get(srv, "http://pub.example/", timeout=0.5)
    assert srv.timeouts == [0.5]


def test_an_error_at_the_deadline_is_reported_as_the_deadline() -> None:
    def refuse(address: str, port: int, timeout: float) -> socket.socket:
        raise ConnectionRefusedError("no route")

    ticks = iter([0, 5, 10])
    with pytest.raises(FetchRefused, match=r"^fetch exceeded the deadline$"):
        fetch.fetch_page(
            "http://pub.example/",
            resolver=resolver(),
            connector=refuse,
            deadline=10,
            clock=lambda: next(ticks),
        )
