"""Safe metadata-only refusal sentinels and exact raw-digest controls."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from test_model_completion import invoke
from test_model_host import eligible

from rbotlib import state
from rbotlib.model import qualification
from rbotlib.model import run as writer
from rbotlib.model.reader import ModelInputError
from rbotlib.rules import RBOT_ROOT


@pytest.mark.parametrize("kind", ["malformed", "symlink", "hardlink", "directory", "fifo"])
def test_unsafe_managed_state_cannot_downgrade_to_standalone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    path = run / state.STATE
    raw = path.read_bytes()
    path.unlink()
    other = tmp_path / "other"
    other.write_bytes(raw)
    if kind == "malformed":
        path.write_bytes(b"malformed")
    elif kind == "symlink":
        path.symlink_to(other)
    elif kind == "hardlink":
        path.hardlink_to(other)
    elif kind == "directory":
        path.mkdir()
    else:
        os.mkfifo(path)
    text_read = Path.read_text

    def sentinel(selected: Path, *args: object, **kwargs: object) -> str:
        if selected == path and kind != "malformed":
            raise AssertionError("unsupported state content was opened")
        return text_read(selected)  # no unsafe open is reached

    def standalone(*args: object) -> None:
        raise AssertionError("managed state was downgraded")

    monkeypatch.setattr(Path, "read_text", sentinel)
    monkeypatch.setattr(writer, "run_model", standalone)
    assert invoke(run) == 1
    assert other.read_bytes() == raw


@pytest.mark.parametrize("name", ["model.json", "handoffs/MODEL.md", "log/.rbot-log.lock"])
@pytest.mark.parametrize("kind", ["symlink", "hardlink", "directory", "fifo"])
def test_unsupported_owned_path_refuses_without_source_or_state_change(
    tmp_path: Path, name: str, kind: str
) -> None:
    run = eligible(tmp_path, RBOT_ROOT)
    target = run / name
    target.unlink(missing_ok=True)
    outside = tmp_path / "outside"
    outside.write_bytes(b"preserved")
    if kind == "symlink":
        target.symlink_to(outside)
    elif kind == "hardlink":
        target.hardlink_to(outside)
    elif kind == "directory":
        target.mkdir()
    else:
        os.mkfifo(target)
    before = (run / state.STATE).read_bytes()
    assert invoke(run) == 1 and outside.read_bytes() == b"preserved"
    if name != "log/.rbot-log.lock":
        assert (run / state.STATE).read_bytes() == before
    assert (run / state.LOCK).exists()


def test_managed_raw_cp1_crlf_hash_is_retained_while_legacy_text_hash_is_unchanged(
    tmp_path: Path,
) -> None:
    run = eligible(tmp_path, RBOT_ROOT, variant="crlf")
    path = run / "handoffs/CP-1.md"
    raw = path.read_bytes()
    assert b"\r\n" in raw
    before = state.read(run)
    assert before["steps"]["CP-1"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert (
        writer.read_handoff(path).sha256 == hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    )
    assert invoke(run) == 0
    captured = qualification.inputs(run, RBOT_ROOT, state.read(run))
    assert captured.hashes()["CP-1"] == hashlib.sha256(raw).hexdigest()
    assert path.read_bytes() == raw
    assert state.read(run)["steps"]["CP-1"] == before["steps"]["CP-1"]


def test_genuinely_accepted_cp1_wrong_analysis_date_refuses_model(tmp_path: Path) -> None:
    run = eligible(tmp_path, RBOT_ROOT, variant="wrong-date")
    before = (run / state.STATE).read_bytes()
    assert invoke(run) == 1 and (run / state.STATE).read_bytes() == before
    assert not (run / "model.json").exists()


@pytest.mark.parametrize("category", ["orphan", "invalid", "duplicate"])
def test_captured_tags_preserve_actual_first_error_priority(category: str) -> None:
    valid = "<!-- table: duplicate -->\n| value |\n|---|\n| observed |\n"
    blocks = [valid, valid]
    if category != "duplicate":
        blocks.insert(0, "<!-- table: invalid id -->\nnot a table\n")
    if category == "orphan":
        # Orphan category wins even when an invalid tag occurs earlier in the text.
        blocks.append("<!-- table: first.orphan -->\nnot a table\n")
        blocks.append("<!-- table: second.orphan -->\nnot a table\n")
    raw = ("---\nmodule_id: CP-1\n---\n" + "\n".join(blocks)).encode()
    expected = {
        "orphan": "table first.orphan is tagged but malformed",
        "invalid": "table invalid id is tagged but malformed",
        "duplicate": "table duplicate tagged twice",
    }
    with pytest.raises(ModelInputError, match=expected[category]):
        writer.captured_handoff(raw, "owned fixture")
