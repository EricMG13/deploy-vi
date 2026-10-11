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
    (pack / "levels.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (pack / "broken.pdf").write_bytes(b"%PDF-1.4 not really")
    run = make_run(pack)
    assert main(["inventory", "--run", str(run)]) == 0
    assert main(["prepare", "--run", str(run)]) == 0
    (run / "fetched").mkdir()
    (run / "fetched" / "01-example.com.md").write_text(
        "Gaming revenue grew 4%.\n", encoding="utf-8"
    )
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
            "source_unknown: 'OTHER.txt' is not in inventory.json or fetched/",
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
