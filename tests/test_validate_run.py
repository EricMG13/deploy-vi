from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from builders import make_run
from conftest import FIXTURES, fixture_json
from rbotlib.cli import main
from rbotlib.contract import Contract, contract_from_dict
from rbotlib.handoff import parse
from rbotlib.rules import Rules
from rbotlib.validate import EXIT_MALFORMED, check, excerpt_found, normalise, pages, run_findings

CITATION = "| C1 | TEST_10Q.txt | p.3 | revenue was 100 |"


@pytest.fixture
def contract(rules: Rules) -> Contract:
    return contract_from_dict(fixture_json("contract_cp_x.json"), rules)


@pytest.fixture
def run(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    pack.mkdir()
    text = "Cover page\fNotes\fIn the quarter, Revenue  was 100 (“reported”).\n"
    (pack / "TEST_10Q.txt").write_text(text, encoding="utf-8")
    (pack / "ratios.txt").write_text("Total leverage was 4.55x at quarter end.\n", encoding="utf-8")
    (pack / "fin.csv").write_text('Metric,2025\nNet revenues,"11,486"\n', encoding="utf-8")
    (pack / "levels.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (pack / "broken.pdf").write_bytes(b"%PDF-1.4 not really")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    (run / "fetched").mkdir()
    (run / "fetched" / "01-example.com.md").write_text(
        "---\ntitle: Example note\n---\nGaming revenue grew 4%.\n", encoding="utf-8"
    )
    (run / "handoffs").mkdir()
    (run / "handoffs" / "CP-1.md").write_text("revenue was 100 here\n", encoding="utf-8")
    return run


def _codes(text: str, contract: Contract, rules: Rules, run: Path) -> tuple[int, list[str]]:
    code, findings = check(text, contract, rules, run)
    return code, [f"{f.code}: {f.message}" for f in findings]


def test_a_cited_excerpt_on_its_page_is_anchored(
    handoff_text: str, contract: Contract, rules: Rules, run: Path
) -> None:
    assert check(handoff_text, contract, rules, run) == (0, [])


@pytest.mark.parametrize(
    "case",
    [
        (
            "| C1 | TEST_10Q.txt | p.2 | revenue was 100 |",
            "citation_unanchored: C1: excerpt not found in TEST_10Q.txt p.2: 'revenue was 100'",
        ),
        (
            "| C1 | TEST_10Q.txt | Note 4 | revenue was 200 |",
            "citation_unanchored: C1: excerpt not found in TEST_10Q.txt: 'revenue was 200'",
        ),
        (
            "| C1 | OTHER.txt | p.1 | revenue |",
            "source_unknown: 'OTHER.txt' is not in prepared/index.json or fetched/",
        ),
        (
            "| C1 | broken.pdf | p.1 | revenue |",
            "citation_unanchored: 'broken.pdf' is unreadable: pypdf could not read the PDF",
        ),
    ],
)
def test_unknown_sources_and_unanchored_excerpts_are_malformed(
    handoff_text: str, contract: Contract, rules: Rules, run: Path, case: tuple[str, str]
) -> None:
    row, finding = case
    code, findings = _codes(handoff_text.replace(CITATION, row), contract, rules, run)
    assert code == EXIT_MALFORMED
    assert len(findings) == 1 and findings[0].startswith(finding)


@pytest.mark.parametrize(
    "row",
    [
        '| C1 | TEST_10Q.txt | pp.2-3 | In the quarter ... was 100 ("reported") |',
        "| C1 | fetched/01-example.com.md | section 1 | gaming revenue grew 4% |",
        "| C1 | levels.png | top left | Image-Read: CZR TLB 99.5 |",
    ],
)
def test_ranges_ellipses_fetched_pages_and_image_sources(
    handoff_text: str, contract: Contract, rules: Rules, run: Path, row: str
) -> None:
    assert check(handoff_text.replace(CITATION, row), contract, rules, run) == (0, [])


def test_without_a_citations_table_there_is_nothing_to_anchor(handoff_text: str, run: Path) -> None:
    assert run_findings(parse(handoff_text.split("## Citations")[0]), run) == []


def test_validate_takes_a_run_folder(
    tree: Path, run: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.md"
    text = (FIXTURES / "handoff_cp_x.md").read_text(encoding="utf-8")
    bad.write_text(text.replace("p.3", "p.1"), encoding="utf-8")
    args = ["--root", str(tree), "validate", str(bad), "--module", "CP-X", "--run", str(run)]
    assert main(args) == EXIT_MALFORMED
    assert (
        "citation_unanchored: C1: excerpt not found in TEST_10Q.txt p.1" in capsys.readouterr().out
    )


def test_normalise_and_pages() -> None:
    assert normalise("  “Net”  revenues | 2,993 — Q2 ") == '"net" revenues 2,993 - q2'
    assert excerpt_found("alpha beta gamma delta", "alpha … gamma")
    assert not excerpt_found("alpha beta gamma delta", "gamma ... alpha")
    assert pages("<<< page 1 >>>\none\n<<< page 2 >>>\ntwo\n") == {1: "\none\n", 2: "\ntwo\n"}


def _row(source: str, locator: str, excerpt: str) -> str:
    return f"| C1 | {source} | {locator} | {excerpt} |"


@pytest.mark.parametrize(
    "case",
    [
        (_row("fetched/../handoffs/CP-1.md", "p.1", "revenue was 100 here"), "source_unknown"),
        (_row("fetched/../../other/x.md", "p.1", "revenue was 100 here"), "source_unknown"),
        (_row("TEST_10Q.txt", "page 1", "revenue was 100"), "citation_unanchored"),
        (_row("TEST_10Q.txt", "p. three", "revenue was 100"), "citation_unanchored"),
        (_row("TEST_10Q.txt", "p.3", "revenue was 10"), "citation_unanchored"),
        (_row("ratios.txt", "p.1", "leverage was 4.5x"), "citation_unanchored"),
        (_row("TEST_10Q.txt", "p.3", "..."), "citation_unanchored"),
        (_row("TEST_10Q.txt", "p.3", "the"), "citation_unanchored"),
        (_row("TEST_10Q.txt", "p.3", "4"), "citation_unanchored"),
        (_row("TEST_10Q.txt", "p.3", "a b c"), "citation_unanchored"),
        (_row("TEST_10Q.txt", "s.1", "Cover page ... Notes"), "citation_unanchored"),
        (_row("fetched/01-example.com.md", "s.1", "title: Example note"), "citation_unanchored"),
    ],
)
def test_weak_forged_and_out_of_place_citations_are_findings(
    handoff_text: str, contract: Contract, rules: Rules, run: Path, case: tuple[str, str]
) -> None:
    row, finding = case
    code, findings = _codes(handoff_text.replace(CITATION, row), contract, rules, run)
    assert code == EXIT_MALFORMED and [f.split(":")[0] for f in findings] == [finding]


@pytest.mark.parametrize(
    "row",
    [
        _row("TEST_10Q.txt", "Page 3", "revenue was 100"),
        _row("TEST_10Q.txt", "PG. 3", "revenue was 100"),
        _row("TEST_10Q.txt", "pages 2-3", "revenue was 100"),
        _row("fin.csv", "p.1", r"Net revenues \| 11,486"),
        _row("fetched/01-example.com.md", "s.1", "gaming revenue grew 4%"),
    ],
)
def test_page_forms_sheet_rows_and_fetched_bodies_anchor(
    handoff_text: str, contract: Contract, rules: Rules, run: Path, row: str
) -> None:
    assert check(handoff_text.replace(CITATION, row), contract, rules, run) == (0, [])


def test_a_broken_run_folder_is_an_error_not_a_traceback(
    handoff_text: str, run: Path, tree: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    nowhere = tmp_path / "nowhere"
    no_table = parse(handoff_text.split("## Citations")[0])
    assert [f.code for f in run_findings(no_table, nowhere)] == ["run_error"]
    assert [f.code for f in run_findings(parse(handoff_text), nowhere)] == ["run_error"]
    next((run / "prepared").glob("*10q*")).unlink()
    (run / "fetched" / "01-example.com.md").write_bytes(b"\xff\xfe bad")
    for source, reason in (
        ("TEST_10Q.txt", "No such file"),
        ("fetched/01-example.com.md", "codec"),
    ):
        found = run_findings(parse(handoff_text.replace("TEST_10Q.txt", source)), run)
        assert [f.code for f in found] == ["run_error"] and reason in found[0].message
    (run / "prepared" / "index.json").write_text("{", encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text(handoff_text, encoding="utf-8")
    args = ["--root", str(tree), "validate", str(bad), "--module", "CP-X", "--run", str(run)]
    assert main(args) == 1
    assert f"error: {run / 'prepared' / 'index.json'}:" in capsys.readouterr().err


def test_normalise_joins_and_unifies_what_a_pdf_garbles() -> None:
    assert normalise("inter-\n  national") == normalise("international") == "international"
    assert normalise("soft\u00adhyphen") == "softhyphen"
    assert normalise("a\u2010b a\u2011b a\u2012b a\u2212b") == "a-b a-b a-b a-b"
    assert normalise("it\u02bcs 5\u2032") == "it's 5'"
    assert normalise("well-known  rate") == "well-known rate"


def test_a_repeated_page_anchor_cannot_overwrite_a_page() -> None:
    text = "<<< page 1 >>>\none\n<<< page 1 >>>\nforged\n<<< page 2 >>>\ntwo\n"
    assert pages(text) == {1: "\none\n<<< page 1 >>>\nforged\n", 2: "\ntwo\n"}


@pytest.mark.corpus
def test_citations_anchor_in_real_filings(
    prepared_run: Callable[[str], Path], handoff_text: str, contract: Contract, rules: Rules
) -> None:
    tenk = r"| C1 | CZR_FY2025_10K.txt | p.1 | Net revenues \| 11,486 \| 11,245 \| 11,528 |"
    wrong = tenk.replace("11,528", "11,529")
    run = prepared_run("czr-2026q2")
    assert check(handoff_text.replace(CITATION, tenk), contract, rules, run) == (0, [])
    assert check(handoff_text.replace(CITATION, wrong), contract, rules, run)[0] == EXIT_MALFORMED
    six = "sec.gov_Archives_edgar_data_701374_000155837022001971_six-20220102x10k.htm.pdf"
    cover = f"| C1 | {six} | p.1 | SIX FLAGS ENTERTAINMENT CORPORATION |"
    ford = prepared_run("tid-ford")
    assert check(handoff_text.replace(CITATION, cover), contract, rules, ford) == (0, [])
    moved = handoff_text.replace(CITATION, cover.replace("p.1", "p.2"))
    assert check(moved, contract, rules, ford)[0] == EXIT_MALFORMED
