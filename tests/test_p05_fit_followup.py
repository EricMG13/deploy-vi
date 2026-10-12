from dataclasses import replace
from pathlib import Path

import pytest
from test_fit_arithmetic import RUN, limit, loan, portfolio

from rbotlib import fit_arithmetic as fa


@pytest.mark.parametrize("readable", ["B2", "Ba2", "Baa2", "CCC+"])
def test_mixed_unreadable_agency_rating_cannot_clear_ccc(readable: str) -> None:
    row = limit(
        "CCC",
        "rating_bucket",
        "7.5",
        "pct_nav",
        "Hard",
        scope_value="CCC",
        current_value="7.36",
        largest=False,
    )
    f = fa.fit(portfolio(row), loan(ratings=(readable, "RD")), RUN)
    assert len(f.rows) == 1
    assert f.verdict == "Watch" and f.recommendation_cap == "3 - MW"
    assert f.notes and "unreadable" in f.notes[0]
    assert fa.rating_bucket((readable, "NR")) != "Unreadable"


def test_unused_total_par_does_not_cap_a_nav_only_fit() -> None:
    row = limit("C", "issuer", "20", "pct_nav", "Hard")
    p = portfolio(row)
    good = fa.fit(p, loan(), RUN)
    absent = fa.fit(replace(p, par=None), loan(), RUN)
    assert absent.max_size == good.max_size
    assert (absent.verdict, absent.recommendation_cap) == ("Fits", "1 - Strong OW")
    other = limit("P", "asset_type", "10", "pct_par", "Hard", scope_value="Bond", largest=False)
    assert fa.fit(portfolio(row, other, par=None), loan(), RUN).verdict == "Fits"
    needed = limit("P", "issuer", "20", "pct_par", "Hard")
    required = fa.fit(portfolio(needed, par=None), loan(), RUN)
    assert required.rows[0].status == "Not computed" and required.verdict == "Watch"


def test_missing_unused_par_is_published_as_a_gap_without_a_watch_cap(tmp_path: Path) -> None:
    from test_fit import TEST_CLO_I, _fits, _run

    from rbotlib.cli import main
    from rbotlib.handoff import parse

    p = dict(
        TEST_CLO_I,
        par=None,
        limits=TEST_CLO_I["limits"][:1],
        unparsed=[],
        positions=[{"issuer_id": "CZR", "par": "0"}],
    )
    folder = _run(tmp_path, p)
    assert main(["fit", "--run", str(folder)]) == 0
    row = _fits(folder)["CEI-TLB"]
    assert row["verdict"] == "Fits" and row["recommendation_cap"] == "1 - Strong OW"
    text = (folder / "handoffs/FIT.md").read_text()
    assert "total par is missing" in text
    assert parse(text).front_matter["qa_status"] == "Restricted"
