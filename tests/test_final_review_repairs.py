"""Concrete integrated Plan02 review regressions through the production commands."""

import json
import os
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st
from test_corpus import _registry, _roots_env, _sha
from test_portfolio_fixes import AMOUNT, LIM, POS, _json

from builders import make_run
from rbotlib.cli import main
from rbotlib.corpus import ROOTS_ENV, CorpusError, load_registry
from rbotlib.portfolio import Portfolio, read_sheet
from rbotlib.validate import excerpt_found


@pytest.mark.parametrize("column", ["Par", " pAR ", "Issuer ID", "% NAV", "Sector"])
def test_duplicate_position_column_refuses_table(tmp_path: Path, column: str) -> None:
    text = POS.format(unit="")
    if column == "Sector":
        text = text.replace("% NAV\n", "% NAV,Sector\n").replace("0.95%\n", "0.95%,Tech\n")
    lines = text.splitlines()
    lines[-2] += "," + column
    lines[-1] += ",1"
    data, notes = _json(
        tmp_path, {"a.csv": "\n".join(lines), "b.csv": LIM.format(unit="USD") + AMOUNT}
    )
    assert data["P1"]["positions"] == []
    assert any("a.csv" in n and "repeated column" in n for n in data["P1"]["notes"])
    assert any("repeated column" in n for n in notes)


@pytest.mark.parametrize("column", ["Limit", " LIMIT ", "Current Value"])
def test_duplicate_limit_column_refuses_table(tmp_path: Path, column: str) -> None:
    text = LIM.format(unit="USD") + AMOUNT
    lines = text.splitlines()
    lines[-2] += "," + column
    lines[-1] += ",90% NAV"
    data, notes = _json(
        tmp_path, {"a.csv": "\n".join(lines), "b.csv": POS.format(unit="Unit,USD\n")}
    )
    assert data["P1"]["limits"] == [] and any("repeated column" in n for n in notes)
    assert any("a.csv" in n and "repeated column" in n for n in data["P1"]["notes"])


@pytest.mark.parametrize("row", [",Portfolio ID,P2", ",,Portfolio ID,P1", ",As of,2025-12-31"])
def test_padded_identity_metadata_refuses_table(tmp_path: Path, row: str) -> None:
    data, notes = _json(
        tmp_path,
        {"a.csv": row + "\n" + POS.format(unit=""), "b.csv": LIM.format(unit="USD") + AMOUNT},
    )
    assert data["P1"]["positions"] == [] and any("sheet refused" in n for n in notes)
    assert any("a.csv" in n and "sheet refused" in n for n in data["P1"]["notes"])


@pytest.mark.parametrize(
    "prefix", ["-$", "- $", "- US$ ", "( $", "( US$ ", "\u2212 €", "- £", "-¥"]
)
@pytest.mark.parametrize("excerpt", ["5 million for the quarter", "$5 million for the quarter"])
def test_sign_dropped_amount_does_not_anchor(prefix: str, excerpt: str) -> None:
    assert not excerpt_found("Net loss was " + prefix + "5 million for the quarter)", excerpt)
    assert excerpt_found(
        "Net loss was " + prefix + "5 million for the quarter)",
        prefix + "5 million for the quarter)",
    )
    assert excerpt_found(
        "Net loss was " + prefix + "5 million for the quarter). Later 5 million for the quarter",
        "5 million for the quarter",
    )


def test_negative_currency_citation_cli_refuses(
    tmp_path: Path, tree: Path, handoff_text: str, capsys: pytest.CaptureFixture[str]
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "negative.txt").write_text("Net loss was -$5 million for the quarter.\n")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    handoff = run / "CP-X.md"
    handoff.write_text(
        handoff_text.replace(
            "| C1 | TEST_10Q.txt | p.3 | revenue was 100 |",
            "| C1 | negative.txt | p.1 | 5 million for the quarter |",
        )
    )
    assert (
        main(["--root", str(tree), "validate", str(handoff), "--module", "CP-X", "--run", str(run)])
        == 2
    )
    assert "citation_unanchored" in capsys.readouterr().out


@pytest.mark.parametrize("destination", ["inventory.json", "log/rbot.log"])
def test_hardlinked_output_preserves_source_and_refuses_before_mutation(
    tmp_path: Path, destination: str, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "source.txt"
    original = b"ORIGINAL SOURCE DOCUMENT\n"
    source.write_bytes(original)
    run = make_run(tmp_path)
    target = run / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    os.link(source, target)
    assert main(["inventory", "--run", str(run)]) == 1
    assert source.read_bytes() == original and target.read_bytes() == original
    if destination.startswith("log/"):
        assert not (run / "inventory.json").exists()
    output = capsys.readouterr()
    assert "hard link" in output.out + output.err and "Traceback" not in output.err


@pytest.mark.parametrize(
    "field,value",
    [
        ("roots", []),
        ("packs", [None]),
        ("packs", None),
        ("files", None),
        ("issuer", []),
        ("pathways", None),
        ("path", 5),
        ("roots.ext", None),
        ("files", [None]),
        (
            "files",
            [
                {
                    "path": "a",
                    "sha256": 2,
                    "class": "issuer",
                    "document_type": "Other",
                    "entity": "TEST",
                }
            ],
        ),
        ("pathways", [None]),
        ("pathways", [{"id": "P", "depth": 5, "fit": "primary"}]),
        ("issuer.id", None),
        ("issuer", {}),
        ("pathways", [{}]),
    ],
)
def test_nested_registry_shapes_are_named_usage_errors(
    tmp_path: Path, field: str, value: object, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _registry(tmp_path, {}, {})
    body = json.loads(path.read_text())
    owner = body if field.split(".")[0] in {"roots", "packs"} else body["packs"][0]
    parts = field.split(".")
    for key in parts[:-1]:
        owner = owner[key]
    owner[parts[-1]] = value
    path.write_text(json.dumps(body))
    with pytest.raises(CorpusError, match=str(path)):
        load_registry(path)
    assert main(["corpus", "verify", "--registry", str(path)]) == 2
    output = capsys.readouterr()
    assert str(path) in output.out + output.err and "Traceback" not in output.err


@pytest.mark.parametrize("unsafe", ["../../outside.txt", "/outside.txt"])
def test_escaping_registry_file_is_usage_error(
    tmp_path: Path, unsafe: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _registry(tmp_path, {}, {unsafe: _sha(b"x")})
    monkeypatch.setenv(ROOTS_ENV, _roots_env(tmp_path)[ROOTS_ENV])
    assert main(["corpus", "verify", "--registry", str(path)]) == 2
    output = capsys.readouterr()
    assert "escapes root" in output.out + output.err


@pytest.mark.parametrize(
    "source,excerpt",
    [
        ("Price talk 300 - 325 bps", "325 bps"),
        ("Results Q2 - 2026 were published", "2026 were published"),
    ],
)
def test_spaced_range_and_quarter_boundaries_remain_valid(source: str, excerpt: str) -> None:
    assert excerpt_found(source, excerpt)


def test_inventory_atomic_failure_keeps_previous_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "source.txt").write_text("source\n")
    run = make_run(tmp_path)
    previous = b"previous complete inventory\n"
    target = run / "inventory.json"
    target.write_bytes(previous)

    def fail(*_: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("rbotlib.inventory.os.replace", fail)
    assert main(["inventory", "--run", str(run)]) == 1
    assert target.read_bytes() == previous and not list(run.glob("*.tmp"))


@given(
    padding=st.integers(min_value=1, max_value=12), label=st.sampled_from(["Portfolio ID", "As of"])
)
def test_identity_refusal_is_invariant_under_empty_padding(padding: int, label: str) -> None:
    rows = [line.split(",") for line in POS.format(unit="").splitlines()]
    rows.insert(1, [""] * padding + [label, "P2" if label == "Portfolio ID" else "2025-12-31"])
    found: dict[str, Portfolio] = {}
    notes = read_sheet("padded.csv", rows, found, {})
    assert notes and "sheet refused" in notes[0]
    assert not found["P1"].positions and not found["P1"].files
    assert notes[0] in found["P1"].notes


@given(
    space=st.sampled_from(["", " ", "\t", "\u00a0"]),
    currency=st.sampled_from(["$", "US$", "€", "£", "¥"]),
)
def test_numeric_sign_boundary_survives_whitespace_normalization(space: str, currency: str) -> None:
    text = f"Net loss was -{space}{currency}{space}5 million this quarter"
    assert not excerpt_found(text, "5 million this quarter")
    assert not excerpt_found(text, f"{currency}{space}5 million this quarter")
    assert excerpt_found(text, f"-{space}{currency}{space}5 million this quarter")


def test_unexpected_inventory_error_propagates_and_is_logged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "source.txt").write_text("source\n")
    run = make_run(tmp_path)

    def fail(_: Path) -> None:
        raise RuntimeError("programming failure")

    monkeypatch.setattr("rbotlib.inventory.write", fail)
    with pytest.raises(RuntimeError, match="programming failure"):
        main(["inventory", "--run", str(run)])
    assert (run / "log/rbot.log").read_text().endswith("\t1\n")


@pytest.mark.parametrize("linked", ["a.txt", "b.txt"])
def test_materialise_preflights_all_hardlinks_before_copy(tmp_path: Path, linked: str) -> None:
    from rbotlib.corpus import materialise, resolve_roots

    originals = {"a.txt": b"SOURCE A\n", "b.txt": b"SOURCE B\n"}
    path = _registry(tmp_path, originals, {n: _sha(b) for n, b in originals.items()})
    registry = load_registry(path)
    dest = tmp_path / "copy"
    dest.mkdir()
    other = "b.txt" if linked == "a.txt" else "a.txt"
    os.link(tmp_path / "ext/pack" / other, dest / linked)
    (dest / other).write_bytes(b"old output\n")
    before = {p.name: p.read_bytes() for p in dest.iterdir()}
    with pytest.raises(CorpusError, match="hard link"):
        materialise(
            registry, registry.pack("p1"), resolve_roots(registry, _roots_env(tmp_path)), dest
        )
    assert {n: (tmp_path / "ext/pack" / n).read_bytes() for n in originals} == originals
    assert {p.name: p.read_bytes() for p in dest.iterdir()} == before


@pytest.mark.parametrize(
    "source,excerpt",
    [
        ("-$5 million this quarter", "5 million this quarter"),
        ("- US$ 5 million this quarter", "US$ 5 million this quarter"),
        ("( $5 million this quarter)", "$5 million this quarter"),
        ("A15 million this quarter", "5 million this quarter"),
        ("12.5 million this quarter", "5 million this quarter"),
    ],
)
def test_numeric_prefix_at_start_and_inside_tokens(source: str, excerpt: str) -> None:
    assert not excerpt_found(source, excerpt)


@pytest.mark.parametrize(
    "source", ["Net income ($5 million) in Q2", "Net income ( $5 million) in Q2"]
)
def test_accounting_closing_bracket_policy_is_preserved(source: str) -> None:
    assert excerpt_found(source, "$5 million) in Q2")


@pytest.mark.parametrize("optional,value", [("external", 3), ("pages", "47")])
def test_wrong_optional_corpus_scalar_is_named(
    tmp_path: Path, optional: str, value: object
) -> None:
    path = _registry(tmp_path, {}, {"a.pdf": _sha(b"x")})
    body = json.loads(path.read_text())
    body["packs"][0]["files"][0][optional] = value
    path.write_text(json.dumps(body))
    with pytest.raises(CorpusError, match=str(path) + r".*file 0.*" + optional):
        load_registry(path)


def test_valid_corpus_optional_metadata_survives_loading(tmp_path: Path) -> None:
    path = _registry(tmp_path, {}, {"a.pdf": _sha(b"x")})
    body = json.loads(path.read_text())
    body["packs"][0]["files"][0].update(pages=47, external="ext/pack/a.pdf")
    path.write_text(json.dumps(body))
    item = load_registry(path).pack("p1").files[0]
    assert (item.cls, item.document_type, item.entity, item.pages, item.external) == (
        "issuer",
        "Other",
        "TEST",
        47,
        "ext/pack/a.pdf",
    )


def test_materialise_overwrites_ordinary_outputs_without_changing_sources(tmp_path: Path) -> None:
    from rbotlib.corpus import materialise, resolve_roots

    sources = {"a.txt": b"SOURCE A\n", "b.txt": b"SOURCE B\n"}
    path = _registry(tmp_path, sources, {n: _sha(b) for n, b in sources.items()})
    registry = load_registry(path)
    dest = tmp_path / "copy"
    dest.mkdir()
    for name in sources:
        (dest / name).write_bytes(b"old output\n")
    assert (
        materialise(
            registry, registry.pack("p1"), resolve_roots(registry, _roots_env(tmp_path)), dest
        )
        == dest
    )
    assert {n: (dest / n).read_bytes() for n in sources} == sources
    assert {n: (tmp_path / "ext/pack" / n).read_bytes() for n in sources} == sources
