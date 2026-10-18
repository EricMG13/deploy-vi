"""`rbotlib.fetch.save_page`: file names, allocation and the saved layout."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import pytest
from fetch_server import (
    PAGE,
    Starter,
    get,
    html,
    redirect,
)

from rbotlib import fetch, fetched
from rbotlib.fetch import FetchRefused, Page
from rbotlib.handoff import parse
from rbotlib.inventory import RunError


def test_fetch_records_url_and_date(server: Starter, tmp_path: Path) -> None:
    page = get(server({"/page": html(PAGE)}), "http://pub.example/page#top")
    assert (page.url, page.final_url, page.retrieved) == (
        "http://pub.example/page",
        "http://pub.example/page",
        "2026-10-17",
    )
    path = fetch.save_page(tmp_path, page, "Q1")
    assert path == tmp_path / "fetched" / "01-pub.example.md"
    raw = path.read_bytes()
    front, body = raw[4:].split(b"\n---\n", 1)
    meta = parse(raw.decode()).front_matter
    assert meta == {
        "url": "http://pub.example/page",
        "retrieved": "2026-10-17",
        "sha256": hashlib.sha256(body).hexdigest(),
        "question": "Q1",
        "content_type": "text/html",
    }
    assert front.decode().splitlines()[0] == "url: http://pub.example/page"
    text = body.decode()
    assert text.startswith("# Annual Report\n")
    assert "Revenue grew." in text and "secret" not in text


def test_final_url_is_recorded_when_it_differs(server: Starter, tmp_path: Path) -> None:
    page = get(server({"/": redirect("/b"), "/b": html(PAGE)}), "http://pub.example/")
    meta = parse(fetch.save_page(tmp_path, page, "Q1").read_text()).front_matter
    assert (meta["url"], meta["final_url"]) == ("http://pub.example/", "http://pub.example/b")


def test_save_page_names_and_allocation(tmp_path: Path) -> None:
    def page(url: str) -> Page:
        return Page(url, url, "2026-10-17", "text/plain", "", "text")

    folder = tmp_path / "fetched"
    folder.mkdir()
    (folder / "01-a.example.md").write_text("x")
    (folder / "03-b.example.md").write_text("x")
    (folder / "notes.txt").write_text("x")
    assert fetch.save_page(tmp_path, page("http://c.example/"), "Q1").name == "04-c.example.md"
    idn = fetch.save_page(tmp_path, page("http://BÜCHER.example/"), "Q1")
    assert idn.name == "05-xn--bcher-kva.example.md"
    long_host = "http://" + "a" * 60 + "." + "b" * 60 + ".example/"
    assert len(fetch.save_page(tmp_path, page(long_host), "Q1").name) <= len("00-") + 80 + len(
        ".md"
    )
    with pytest.raises(FetchRefused, match="question"):
        fetch.save_page(tmp_path, page("http://d.example/"), "Q1\nurl: x")


def test_the_same_url_is_not_saved_twice(tmp_path: Path) -> None:
    page = Page("http://a.example/p", "http://a.example/p", "2026-10-17", "text/plain", "", "t")
    first = fetch.save_page(tmp_path, page, "Q1")
    before = first.read_bytes()
    assert fetch.save_page(tmp_path, page._replace(text="other"), "Q2") == first
    assert sorted(p.name for p in (tmp_path / "fetched").iterdir()) == [first.name]
    assert first.read_bytes() == before


def test_the_hundredth_page_is_refused(tmp_path: Path) -> None:
    folder = tmp_path / "fetched"
    folder.mkdir()
    for n in range(1, 100):
        (folder / f"{n:02d}-a.example.md").write_text("x")
    page = Page("http://z.example/", "http://z.example/", "2026-10-17", "text/plain", "", "t")
    with pytest.raises(FetchRefused, match="full"):
        fetch.save_page(tmp_path, page, "Q1")
    assert len(list(folder.iterdir())) == 99


def test_a_symlinked_fetched_folder_is_refused(tmp_path: Path) -> None:
    run, elsewhere = tmp_path / "run", tmp_path / "elsewhere"
    run.mkdir()
    elsewhere.mkdir()
    (run / "fetched").symlink_to(elsewhere)
    page = Page("http://z.example/", "http://z.example/", "2026-10-17", "text/plain", "", "t")
    with pytest.raises(RunError, match="symlink"):
        fetch.save_page(run, page, "Q1")
    assert list(elsewhere.iterdir()) == []


def page_for(url: str) -> Page:
    return Page(url, url, "2026-10-17", "text/plain", "", "text")


def test_the_99th_page_is_saved(tmp_path: Path) -> None:
    folder = tmp_path / "fetched"
    folder.mkdir()
    for n in range(1, 99):
        (folder / f"{n:02d}-a.example.md").write_text("x")
    assert fetch.save_page(tmp_path, page_for("http://z.example/"), "Q1").name == "99-z.example.md"


def test_the_file_is_created_exclusively_without_following_links_or_exec_bits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    flags: list[int] = []
    real = os.open

    def spy(path: Path, flag: int, mode: int = 0o777) -> int:
        flags.append(flag)
        return real(path, flag, mode)

    monkeypatch.setattr(os, "open", spy)
    path = fetch.save_page(tmp_path, page_for("http://z.example/"), "Q1")
    wanted = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    assert flags == [flags[0]] and flags[0] & wanted == wanted
    assert path.stat().st_mode & 0o133 == 0


def test_a_failed_write_leaves_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def full(fd: int, mode: str) -> None:
        os.close(fd)
        raise OSError("disk full")

    monkeypatch.setattr(os, "fdopen", full)
    with pytest.raises(OSError, match="disk full"):
        fetch.save_page(tmp_path, page_for("http://z.example/"), "Q1")
    assert list((tmp_path / "fetched").iterdir()) == []


def test_fetched_as_a_file_is_refused(tmp_path: Path) -> None:
    (tmp_path / "fetched").write_text("x")
    with pytest.raises(FetchRefused, match=r"is not a folder$"):
        fetch.save_page(tmp_path, page_for("http://z.example/"), "Q1")


def test_an_existing_target_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "fetched"
    folder.mkdir()
    (folder / "01-z.example.md").write_text("x")
    monkeypatch.setattr(fetched, "NAME", re.compile(r"never"))
    with pytest.raises(FetchRefused, match=r"^01-z\.example\.md already exists$"):
        fetch.save_page(tmp_path, page_for("http://z.example/"), "Q1")
