"""`rbotlib.fetched`: the saved-page layout and the qualification of `fetched/` files."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from rbotlib import fetched
from rbotlib.inventory import RunError

BRIEF = """---
run: x
---
<!-- table: brief.research_questions -->
| question_id | question | consumer_module | approved |
| --- | --- | --- | --- |
| Q1 | One? | CP-2 | Yes |
| Q2 | Two? | CP-3 | No |
| Q3 | Three? | CP-6 | Yes |
"""


@pytest.fixture
def run(tmp_path: Path) -> Path:
    (tmp_path / "run-brief.md").write_text(BRIEF, encoding="utf-8")
    (tmp_path / "fetched").mkdir()
    return tmp_path


def front(question: str = "Q1", final_url: str = "http://pub.example/p") -> dict[str, str]:
    return {
        "url": "http://pub.example/p",
        "final_url": final_url,
        "retrieved": "2026-10-17",
        "question": question,
        "content_type": "text/html",
    }


def save(
    run: Path, name: str = "01-pub.example.md", question: str = "Q1", body: str = "# T\n\ntext\n"
) -> Path:
    path = run / "fetched" / name
    path.write_text(fetched.render(front(question), body), encoding="utf-8")
    return path


def test_render_layout_and_hash() -> None:
    plain = {**front(), "url": "http://a.example/", "final_url": "http://a.example/"}
    digest = hashlib.sha256("body é\n".encode()).hexdigest()
    text = fetched.render(plain, "body é\n")
    assert text == (
        "---\nurl: http://a.example/\nretrieved: 2026-10-17\n"
        f"sha256: {digest}\n"
        "question: Q1\ncontent_type: text/html\n---\nbody é\n"
    )
    bare = {k: v for k, v in plain.items() if k != "final_url"}
    assert fetched.render(bare, "body é\n") == text
    other = fetched.render({**plain, "final_url": "http://b.example/"}, "x")
    assert "url: http://a.example/\nfinal_url: http://b.example/\nretrieved:" in other


def test_approved_questions(run: Path, tmp_path: Path) -> None:
    assert fetched.approved_questions(run) == ("Q1", "Q3")
    assert fetched.approved_questions(tmp_path / "nowhere") == ()
    (run / "run-brief.md").write_text("no front matter", encoding="utf-8")
    with pytest.raises(RunError, match=r"run-brief\.md"):
        fetched.approved_questions(run)
    (run / "run-brief.md").write_text("---\nrun: x\n---\nno table\n", encoding="utf-8")
    assert fetched.approved_questions(run) == ()


def test_qualified(run: Path) -> None:
    good = save(run)
    found = fetched.qualified(run)
    assert found == {
        "fetched/01-pub.example.md": fetched.FetchedFile(
            "fetched/01-pub.example.md",
            "http://pub.example/p",
            "2026-10-17",
            "Q1",
            hashlib.sha256(b"# T\n\ntext\n").hexdigest(),
        )
    }
    assert fetched.saved_path(run, "http://pub.example/p#x") == good
    assert fetched.saved_path(run, "http://other.example/") is None
    good.write_text(good.read_text().replace("text", "tex7"))
    assert fetched.qualified(run) == {}


def test_a_final_url_key_is_allowed(run: Path) -> None:
    path = run / "fetched" / "01-pub.example.md"
    path.write_text(fetched.render(front("Q3", "http://pub.example/q"), "b"), encoding="utf-8")
    assert "final_url: http://pub.example/q\n" in path.read_text()
    assert list(fetched.qualified(run)) == ["fetched/01-pub.example.md"]


def test_the_empty_body_still_hashes(run: Path) -> None:
    save(run, body="")
    assert list(fetched.qualified(run)) == ["fetched/01-pub.example.md"]


def drop(run: Path, key: str) -> None:
    path = run / "fetched" / "01-pub.example.md"
    path.write_text("".join(x for x in path.read_text().splitlines(True) if not x.startswith(key)))


@pytest.mark.parametrize("key", ["url", "retrieved", "sha256", "question", "content_type"])
def test_a_missing_front_matter_key_disqualifies(run: Path, key: str) -> None:
    save(run)
    drop(run, key + ":")
    assert fetched.qualified(run) == {}


@pytest.mark.parametrize(
    "edit",
    [
        ("retrieved: 2026-10-17", "retrieved: yesterday"),
        ("retrieved: 2026-10-17", "retrieved: "),
        ("question: Q1", "question: Q2"),
        ("question: Q1", "question: Q9"),
        ("sha256: ", "sha256: 0"),
        ("content_type: text/html", "content_type: text/html\nextra: 1"),
        ("content_type: text/html", "content_type: text/html\nurl: http://x.example/"),
        ("---\nurl", "---\n---\nurl"),
    ],
)
def test_a_bad_front_matter_disqualifies(run: Path, edit: tuple[str, str]) -> None:
    path = save(run)
    path.write_text(path.read_text().replace(*edit, 1))
    assert fetched.qualified(run) == {}


def test_not_a_front_matter_file_disqualifies(run: Path) -> None:
    (run / "fetched" / "01-pub.example.md").write_text("just text\n")
    (run / "fetched" / "02-pub.example.md").write_bytes(b"---\nurl: x\n")
    assert fetched.qualified(run) == {}
    assert fetched.saved_path(run, "x") is None


@pytest.mark.parametrize(
    "name", ["1-pub.example.md", "01-Pub.example.md", "01-pub.example.txt", "notes.md", "01-.md"]
)
def test_a_bad_name_disqualifies(run: Path, name: str) -> None:
    save(run, name)
    assert fetched.qualified(run) == {}


def test_a_subdirectory_disqualifies(run: Path) -> None:
    sub = run / "fetched" / "sub"
    sub.mkdir()
    (sub / "01-pub.example.md").write_text(save(run).read_text())
    (run / "fetched" / "01-pub.example.md").unlink()
    (run / "fetched" / "02-dir.example.md").mkdir()
    assert fetched.qualified(run) == {}


def test_a_symlinked_file_or_folder_disqualifies(run: Path, tmp_path: Path) -> None:
    real = save(run, "09-real.example.md")
    link = run / "fetched" / "01-pub.example.md"
    link.symlink_to(real)
    assert list(fetched.qualified(run)) == ["fetched/09-real.example.md"]
    moved = tmp_path / "moved"
    os.rename(run / "fetched", moved)
    (run / "fetched").symlink_to(moved)
    assert fetched.qualified(run) == {}


def test_a_question_that_is_no_longer_approved_is_dropped(run: Path) -> None:
    save(run)
    (run / "run-brief.md").write_text(
        BRIEF.replace("| Q1 | One? | CP-2 | Yes |", "| Q1 | One? | CP-2 | No |")
    )
    assert fetched.qualified(run) == {}


def test_no_fetched_folder(tmp_path: Path) -> None:
    assert fetched.qualified(tmp_path) == {}
    assert fetched.saved_path(tmp_path, "http://x.example/") is None


def test_a_body_that_holds_a_divider_line_still_qualifies(run: Path) -> None:
    save(run, body="above\n---\nbelow\n")
    assert list(fetched.qualified(run)) == ["fetched/01-pub.example.md"]
