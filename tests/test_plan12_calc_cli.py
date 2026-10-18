"""Public calculator CLI trust seam and publication checks with synthetic inputs."""

from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from test_covenant_headroom import row
from test_liquidity_bridge import payload

from rbotlib import calc
from rbotlib.calc.bond_analytics import CalcError
from rbotlib.cli import main
from rbotlib.fsio import write_atomic


@pytest.mark.parametrize(
    ("raw", "field"),
    [
        ('{"tests": [], "tests": []}', "tests"),
        ('{"tests": [{"threshold": 6, "threshold": 5}]}', "threshold"),
        ('{"a": 1, "\\u0061": 2}', "a"),
    ],
)
def test_duplicate_json_fields_refuse_before_compute(tmp_path: Path, raw: str, field: str) -> None:
    source = tmp_path / "duplicate.json"
    source.write_text(raw, encoding="utf-8")
    with pytest.raises(CalcError, match=f"duplicate.*{field}"):
        calc.read_input(source)


def test_public_choices_and_precision(tmp_path: Path) -> None:
    assert calc.CALCULATORS["covenant_headroom"].__name__.endswith(".covenant_headroom")
    assert calc.CALCULATORS["liquidity_bridge"].__name__.endswith(".liquidity_bridge")
    assert {"bond_analytics", "peer_statistics"} <= calc.CALCULATORS.keys()
    source = tmp_path / "exact.json"
    source.write_text('{"n": 1.000000000000000000000000000000000000001, "i": 12345678901234567890}')
    assert calc.read_input(source) == {
        "n": Decimal("1.000000000000000000000000000000000000001"),
        "i": 12345678901234567890,
    }


@pytest.mark.parametrize("name", ["covenant_headroom", "liquidity_bridge"])
@pytest.mark.parametrize("figure", ["5", None, 0])
def test_cli_success_null_zero_and_atomic_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    figure: str | int | None,
) -> None:
    data: dict[str, Any] = (
        {"tests": [row(current_value=figure, test="Crédit 📈")]}
        if name == "covenant_headroom"
        else payload()
    )
    if name == "liquidity_bridge":
        data["components"][3]["amount"] = figure
    source, out = tmp_path / "in.json", tmp_path / "out.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    writes: list[Path] = []

    def observed(path: Path, text: str) -> None:
        writes.append(path)
        write_atomic(path, text)

    monkeypatch.setattr(calc, "write_atomic", observed)
    assert main(["calc", name, "--in", str(source), "--out", str(out)]) == 0
    assert writes == [out] and not list(tmp_path.glob("*.tmp"))
    result = json.loads(out.read_text(encoding="utf-8"))
    text = capsys.readouterr().out
    if name == "covenant_headroom":
        expected = {"5": "1", None: None, 0: "6"}[figure]
        assert result["tests"][0]["headroom"] == expected
        assert "cp4.covenant_tests" in text and "[L1]" in text and "Crédit 📈" in text
        if figure is None:
            assert "current_value" in text and "Not computable" in text
    else:
        expected = {"5": "180", None: None, 0: "185"}[figure]
        assert result["ending_accessible_liquidity"]["value"] == expected
        assert text.index("cp2d.bridge") < text.index("cp2d.runway")
        assert "[S1]" in text and "Timing unknown" in text
        if figure is None:
            assert "missing cash_taxes" in text
    assert main(["calc", name, "--in", str(source)]) == 0
    assert capsys.readouterr().out == text and writes == [out]


@pytest.mark.parametrize("name", ["covenant_headroom", "liquidity_bridge"])
@pytest.mark.parametrize(
    "bad", ["malformed", "missing", "duplicate", "NaN", "Infinity", "-Infinity", "utf8"]
)
def test_cli_refusal_never_writes_or_clobbers(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    bad: str,
) -> None:
    data = {"tests": [row()]} if name == "covenant_headroom" else payload()
    raw = json.dumps(data)
    if bad == "missing":
        raw = "{}"
    elif bad == "duplicate":
        raw = (
            '{"tests": [], "tests": []}'
            if name == "covenant_headroom"
            else raw.replace('"amount": "5"', '"amount": null, "amount": "5"')
        )
    elif bad in {"NaN", "Infinity", "-Infinity"}:
        raw = (
            raw.replace('"threshold": "6"', f'"threshold": {bad}')
            if name == "covenant_headroom"
            else raw.replace('"amount": "5"', f'"amount": {bad}')
        )
    elif bad == "malformed":
        raw = "{"
    source, out = tmp_path / "in.json", tmp_path / "out.json"
    source.write_bytes(b"\xff" if bad == "utf8" else raw.encode("utf-8"))
    original = b"preserved\x00bytes"
    out.write_bytes(original)
    writes: list[Path] = []
    monkeypatch.setattr(calc, "write_atomic", lambda path, text: writes.append(path))
    assert main(["calc", name, "--in", str(source), "--out", str(out)]) == 1
    assert writes == [] and out.read_bytes() == original
    text = capsys.readouterr().out
    assert text.startswith("error:") and "<!--" not in text
    if bad == "duplicate":
        assert "duplicate field" in text
    elif bad == "utf8":
        assert "not UTF-8" in text


def test_cli_atomic_failure_cleans_temporary_and_suppresses_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    source, out = tmp_path / "in.json", tmp_path / "out.json"
    source.write_text(json.dumps({"tests": [row()]}), encoding="utf-8")
    out.write_bytes(b"unchanged")

    def fail_replace(source: object, target: object) -> None:
        raise OSError("synthetic replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    assert main(["calc", "covenant_headroom", "--in", str(source), "--out", str(out)]) == 1
    assert out.read_bytes() == b"unchanged" and not list(tmp_path.glob("*.tmp"))
    assert capsys.readouterr().out == "error: synthetic replace failure\n"


@pytest.mark.parametrize("case", ["integer-limit", "depth-limit", "decimal-exponent"])
@pytest.mark.parametrize("entry", ["reader", "cli"])
def test_parser_limits_refuse_without_clobber(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], case: str, entry: str
) -> None:
    depth = 10000
    raw = {
        "integer-limit": "1" * 5000,
        "depth-limit": "[" * depth + "0" + "]" * depth,
        "decimal-exponent": "1e" + "9" * 50,
    }[case]
    source, out = tmp_path / "limits.json", tmp_path / "out.json"
    source.write_text(raw, encoding="utf-8")
    out.write_bytes(b"preserved")
    if entry == "reader":
        with pytest.raises(CalcError, match=str(source)):
            calc.read_input(source)
    else:
        assert main(["calc", "covenant_headroom", "--in", str(source), "--out", str(out)]) == 1
        assert str(source) in capsys.readouterr().out
    assert out.read_bytes() == b"preserved" and not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("bad", ["value", "key", "array"])
@pytest.mark.parametrize("with_out", [False, True])
def test_surrogates_refuse_before_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], bad: str, with_out: bool
) -> None:
    data = (
        {"tests": [row(cite="\ud800")]}
        if bad == "value"
        else {"\ud800": 1}
        if bad == "key"
        else ["\ud800"]
    )
    source, out = tmp_path / "unicode.json", tmp_path / "out.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    out.write_bytes(b"preserved")
    with pytest.raises(CalcError, match="Unicode"):
        calc.read_input(source)
    args = ["calc", "covenant_headroom", "--in", str(source)]
    assert main(args + (["--out", str(out)] if with_out else [])) == 1
    text = capsys.readouterr().out
    assert "Unicode" in text and "<!--" not in text
    assert out.read_bytes() == b"preserved" and not list(tmp_path.glob("*.tmp"))


def test_report_caller_refuses_duplicate_calculator_input(tmp_path: Path) -> None:
    from rbotlib.report import charts

    source = tmp_path / charts.CALC_INPUT
    source.parent.mkdir(parents=True)
    fixture = Path(__file__).parent / "fixtures/calc/CP-3-bond_analytics.json"
    source.write_bytes(fixture.read_bytes())
    assert charts._recomputed({"run_dir": tmp_path}, []) == ("host", None)
    source.write_text(source.read_text().replace('"as_of":', '"as_of": "2026-10-02", "as_of":'))
    assert charts._recomputed({"run_dir": tmp_path}, []) == ("model", "calculator input unreadable")
