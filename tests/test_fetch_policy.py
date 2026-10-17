"""`rbotlib.fetch` policy: addresses, URLs, availability and HTML to text. No network."""

from __future__ import annotations

import re

import pytest

from rbotlib import fetch
from rbotlib.fetch import FetchRefused

EMBEDDING = ("::", "64:ff9b::", "::ffff:0:")


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.1",
        "169.254.169.254",
        "192.168.1.1",
        "0.0.0.0",
        "224.0.0.1",
        "::1",
        "fc00::1",
        "fe80::1",
        "::ffff:127.0.0.1",
        "::ffff:10.0.0.1",
        "::",
        *(f"{prefix}{ipv4}" for prefix in EMBEDDING for ipv4 in ("a00:1", "7f00:1")),
    ],
)
def test_check_address_refuses_non_global(address: str) -> None:
    with pytest.raises(FetchRefused, match=re.escape(address)):
        fetch.check_address(address)


@pytest.mark.parametrize(
    "address",
    [
        "93.184.216.34",
        "2606:2800:220:1:248:1893:25c8:1946",
        "64:ff9b::5db8:d822",
        "2606:2800:220:1:248:1893:a00:1",
    ],
)
def test_check_address_passes_global(address: str) -> None:
    fetch.check_address(address)


def test_check_address_refuses_a_non_address() -> None:
    with pytest.raises(FetchRefused, match="not-an-ip"):
        fetch.check_address("not-an-ip")


@pytest.mark.parametrize(
    ("url", "reason"),
    [
        ("ftp://x.example/", "^URL scheme 'ftp' is not http or https$"),
        ("file:///etc/passwd", "scheme 'file'"),
        ("http://user:pw@x.example/", "^URL holds credentials$"),
        ("http://:pw@x.example/", "^URL holds credentials$"),
        ("http://127.0.0.1/", "^host '127.0.0.1' is an IP address$"),
        ("http://[::1]/", "^host '::1' is not a public DNS name$"),
        ("http://localhost/", "^host 'localhost' is not a public DNS name$"),
        ("http://localhost./", "^host 'localhost.' is not a public DNS name$"),
        ("http://x.example:8080/", "^port 8080 is not 80 or 443$"),
        ("http://x.example:bad/", "^URL is not valid: "),
        ("http:///nohost", "^host '' is not a public DNS name$"),
        ("http://x.example/a b", "^URL holds a space or control character$"),
        ("http://x.example/\n", "^URL holds a space or control character$"),
        ("http://x.example/\x7f", "^URL holds a space or control character$"),
        ("http://a..example/", "^host name 'a..example' is not valid$"),
        ("http://under_score.example/", "^host name 'under_score.example' is not valid$"),
        ("http://x.example/" + "a" * 2033, "^URL is longer than 2048 characters$"),
    ],
)
def test_check_url_refuses(url: str, reason: str) -> None:
    with pytest.raises(FetchRefused, match=reason):
        fetch.check_url(url)


def test_check_url_keeps_a_2048_character_url_and_drops_the_fragment() -> None:
    url = "http://x.example/" + "a" * 2031
    assert len(url) == 2048
    assert fetch.check_url(url).geturl() == url
    assert fetch.check_url("http://x.example/p#frag").geturl() == "http://x.example/p"
    assert fetch.check_url("https://x.example:443/p").port == 443
    assert fetch.check_url("http://x.example:80/p").port == 80
    assert fetch.check_url("http://x.example/p#frag").fragment == ""
    assert fetch.check_url("http://x.example/!").path == "/!"
    assert fetch.check_url("http://x.example/\u0080").path == "/\u0080"


def test_available_only_on_one() -> None:
    assert fetch.available({"RBOT_FETCH": "1"}) is True
    assert fetch.available({"RBOT_FETCH": "0"}) is False
    assert fetch.available({"RBOT_FETCH": "11"}) is False
    assert fetch.available({}) is False


def test_html_to_text() -> None:
    markup = (
        "<html><head><title> My  Page </title><style>p{}</style></head><body>"
        "<script>alert(1)</script><noscript>enable js</noscript><!-- hidden -->"
        "<template><p>tpl</p></template><svg><text>icon</text></svg>"
        "<p>Fish &amp; chips</p>one<br>two<ul><li>a   b</li><li>c</li></ul>"
        "<table><tr><td>x</td><td>y</td></tr><tr><td>z</td></tr></table>tail</body></html>"
    )
    title, text = fetch.html_to_text(markup)
    assert title == "My Page"
    assert text.split("\n") == ["Fish & chips", "one", "two", "a b", "c", "x y", "z", "tail"]
    assert fetch.html_to_text("<p>x</p>") == ("", "x")


def test_html_nesting_and_inline_tags() -> None:
    assert fetch.html_to_text("<svg><script>x</script>hidden</svg>shown") == ("", "shown")
    assert fetch.html_to_text("<noscript><template>a</template>b</noscript>c") == ("", "c")
    assert fetch.html_to_text("<p>bo<b>l</b>d</p></script>kept") == ("", "bold\nkept")
    assert fetch.html_to_text("<title>one</title>text") == ("one", "text")
