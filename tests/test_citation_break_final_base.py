"""Preserve financial rating hyphens while joining genuine line-broken words."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from test_p05_review_followup import _a_evidence

import ab_grade
from conftest import FIXTURES
from rbotlib.contract import load_contract
from rbotlib.handoff import parse
from rbotlib.rules import load_rules
from rbotlib.validate import check, excerpt_found, normalise


@pytest.mark.parametrize("rating", ["B-", "BB-", "CCC-", "AA-"])
def test_short_uppercase_rating_keeps_its_minus_and_next_field(rating: str) -> None:
    text = (
        f"Standard & Poor's rating shown: {rating}\n"
        "Standard & Poor's last-rated date shown: 2024-02-02\nIndustry group shown: OTHF"
    )
    assert excerpt_found(text, f"Standard & Poor's rating shown: {rating}")
    assert excerpt_found(text, "Standard & Poor's last-rated date shown: 2024-02-02")
    assert not excerpt_found(text, "Standard & Poor's rating shown: B+")
    assert f"{rating.lower()} standard" in normalise(text)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("inter-\nnational", "international"),
        ("pre-\ncondition", "precondition"),
        ("INTER-\nNATIONAL", "international"),
        ("infor\u00ad\nmation", "information"),
    ],
)
def test_genuine_broken_words_still_join(text: str, expected: str) -> None:
    assert normalise(text) == expected
    assert excerpt_found("The " + text + " business", expected + " business")


@pytest.mark.parametrize(
    "source,quoted",
    [
        ("inter-\nna-\ntional business", "international business"),
        ("INTER-\nNA-\nTIONAL business", "international business"),
        ("Rating BB-\ninter-\nnational business", "Rating BB- international business"),
    ],
)
def test_multiple_genuine_breaks_and_rating_boundary_reach_public_callers(
    tmp_path: Path, handoff_text: str, source: str, quoted: str
) -> None:
    text, run, mapping = _a_evidence(tmp_path)
    (run / "prepared/SYNTHETIC_annual.txt").write_text(
        "<<< page 1 >>>\nSYNTHETIC\n" + source, "utf-8"
    )
    data = json.loads(mapping.read_text("utf-8"))
    data["citations"][0]["excerpt"] = quoted
    mapping.write_text(json.dumps(data), "utf-8")
    assert ab_grade.measure_a(text.replace("Revenue 100.", quoted), run, mapping)["C"] == "1/1"
    rules = load_rules()
    contract = load_contract(FIXTURES / "contract_cp_x.json", rules)
    old = parse(handoff_text).tables["citations"].rows[0]
    new = [old[0], "SYNTHETIC_annual.txt", "p. 1", quoted]
    b = handoff_text.replace("| " + " | ".join(old) + " |", "| " + " | ".join(new) + " |")
    assert check(b, contract, rules, run) == (0, [])
    assert normalise(source) == normalise(quoted)


@pytest.mark.parametrize("modifier", ["-", "+"])
@pytest.mark.parametrize(
    "prefix",
    [
        "Standard & Poor's rating shown: ",
        "Rating ",
        "Expected facility ratings Ba3 (Moody's) / ",
        "Instrument risk class code ",
    ],
)
def test_actual_public_anchoring_refuses_a_discarded_rating_modifier(
    tmp_path: Path, handoff_text: str, modifier: str, prefix: str
) -> None:
    text, run, mapping = _a_evidence(tmp_path)
    native = prefix + "BB"
    source = native + modifier + "\nStandard & Poor's last-rated date shown: 2024-02-02"
    (run / "prepared/SYNTHETIC_annual.txt").write_text(
        "<<< page 1 >>>\nSYNTHETIC\n" + source, "utf-8"
    )
    data = json.loads(mapping.read_text("utf-8"))
    data["citations"][0]["excerpt"] = native
    mapping.write_text(json.dumps(data), "utf-8")
    poor_native = text.replace("Revenue 100.", native)
    assert ab_grade.measure_a(poor_native, run, mapping)["C"] == "0/1"
    rules = load_rules()
    contract = load_contract(FIXTURES / "contract_cp_x.json", rules)
    old = parse(handoff_text).tables["citations"].rows[0]
    new = [old[0], "SYNTHETIC_annual.txt", "p. 1", native]
    poor_b = handoff_text.replace("| " + " | ".join(old) + " |", "| " + " | ".join(new) + " |")
    assert check(poor_b, contract, rules, run)[0] == 2
    correct = native + modifier
    data["citations"][0]["excerpt"] = correct
    mapping.write_text(json.dumps(data), "utf-8")
    assert ab_grade.measure_a(text.replace("Revenue 100.", correct), run, mapping)["C"] == "1/1"
    assert check(poor_b.replace(native, correct), contract, rules, run) == (0, [])


@pytest.mark.corpus
def test_registered_finra_whole_field_and_modifier_refusal(
    prepared_run: Callable[[str], Path], tmp_path: Path, handoff_text: str
) -> None:
    """Use the real inventory/prepared FINRA observation, without altering its bytes."""
    run = prepared_run("czr-2026q2-primary")
    source = "CZR_FINRA_TRACE_12769GAC4_2026-10-02.txt"
    text, _synthetic_run, mapping = _a_evidence(tmp_path)
    text = text.replace("SYNTHETIC_annual.txt", source)
    rules = load_rules()
    contract = load_contract(FIXTURES / "contract_cp_x.json", rules)
    old = parse(handoff_text).tables["citations"].rows[0]
    for rating, expected in (("BB-", "1/1"), ("BB", "0/1"), ("BB+", "0/1")):
        quoted = "Standard & Poor's rating shown: " + rating
        native = text.replace("Revenue 100.", quoted)
        data = json.loads(mapping.read_text("utf-8"))
        data["citations"][0]["excerpt"] = quoted
        mapping.write_text(json.dumps(data), "utf-8")
        assert ab_grade.measure_a(native, run, mapping)["C"] == expected
        new = [old[0], source, "p. 1", quoted]
        b = handoff_text.replace("| " + " | ".join(old) + " |", "| " + " | ".join(new) + " |")
        assert check(b, contract, rules, run)[0] == (0 if rating == "BB-" else 2)
