"""Original Report payloads are data, including hostile source text."""

import copy
import json
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rbotlib.inventory import RunError
from rbotlib.prior_report import ComparisonKeyError, inspect_report, keyed_rows, parse_report
from rbotlib.report.html_parts import embed_json
from rbotlib.report.markdown import render_markdown


def document() -> dict[str, Any]:
    return {
        "schema": "rbot-run/1",
        "run_id": "earlier",
        "generated_at": "2026-10-14T23:00:00+01:00",
        "pathway": "FULL_CREDIT_ASSESSMENT",
        "depth": "full",
        "plan": ["MODEL"],
        "steps": {"MODEL": {"status": "accepted"}},
        "modules": {},
        "fetched": [],
        "run_brief": {
            "front_matter": {"run_id": "earlier", "issuer_id": "TEST"},
            "tables": {
                "snapshot.run_header": {
                    "columns": ["run_id", "issuer_id", "report_date"],
                    "rows": [["earlier", "TEST", "—"]],
                }
            },
        },
        "handoffs": {
            "MODEL": {
                "status": "accepted",
                "citations": [],
                "front_matter": {"run_id": "earlier", "issuer_id": "TEST"},
                "tables": {},
            }
        },
        "model": None,
        "fit": [],
        "limitations": {"approval": [], "cp5": [], "unforeseen": []},
        "prior_case": {"diff": None},
    }


def table(doc: dict[str, Any], name: str, columns: list[str], rows: list[list[str]]) -> None:
    doc["handoffs"]["MODEL"]["tables"][name] = {"columns": columns, "rows": rows}


def test_actual_emitters_preserve_untrusted_strings() -> None:
    doc = document()
    hostile = '</script><img src="https://invalid/" onerror="alert(1)">|\n\u2028\u2029<!--'
    table(doc, "model.house", ["item", "value"], [["debt", hostile]])
    assert parse_report(embed_json(doc), "html") == doc
    rendered = render_markdown(doc, [], [])
    assert parse_report(rendered, "md") == {**doc, "charts": [], "front_page_blocks": []}


@pytest.mark.parametrize("kind", ["html", "md"])
@pytest.mark.parametrize("malformed", [False, True])
def test_citations_remain_owned_locally_with_shape_validation(kind: str, malformed: bool) -> None:
    doc = document()
    doc["run_brief"]["tables"]["citations"] = {
        "columns": ["id", "source", "locator", "excerpt"],
        "rows": [["C1", "brief source", "p1", "brief evidence"]],
    }
    table(
        doc,
        "citations",
        ["id", "source", "locator", "excerpt"],
        [["C1"]] if malformed else [["C1", "model source", "p2", "model evidence"]],
    )
    text = embed_json(doc) if kind == "html" else render_markdown(doc, [], [])
    if malformed:
        with pytest.raises(RunError, match="row width"):
            parse_report(text, kind)
    else:
        parsed = parse_report(text, kind)
        assert parsed["run_brief"] == doc["run_brief"] and parsed["handoffs"] == doc["handoffs"]
        assert "citations" not in inspect_report(parsed)[1]


@pytest.mark.parametrize("kind", ["html", "md"])
@pytest.mark.parametrize("defect", ["missing", "blank", "duplicate"])
def test_reader_preserves_rows_while_strict_comparison_declines(kind: str, defect: str) -> None:
    doc = document()
    name = "snapshot.ebitda_adjustments"
    label = "Add-back: Run-rate cost synergies (unrealised), excluded if positive"
    columns = ["line", "kind", "amount"]
    values = [[label, "Add-back", "150"], [label, "Unrealized add-back", "-150"]]
    if defect == "missing":
        columns, values = ["amount"], []
    elif defect == "blank":
        values[0][0] = "—"
    table(doc, name, columns, values)
    raw = doc["handoffs"]["MODEL"]["tables"][name]
    with pytest.raises(ComparisonKeyError):
        keyed_rows(name, raw)
    text = embed_json(doc) if kind == "html" else render_markdown(doc, [], [])
    parsed = parse_report(text, kind)
    assert parsed["handoffs"] == doc["handoffs"]
    assert any(
        name in limitation and "not comparable" in limitation
        for limitation in inspect_report(parsed)[2]
    )


def pending_cp0_document() -> dict[str, Any]:
    doc = document()
    final, pending = "20261018-czr-full-credit-assessment", "20261018-unknown-pending"
    digest = "fac128add85350f0f3cc7bae18e4dfb2a36b5aad0bab4c08c5b205647339db40"
    doc["run_id"] = final
    doc["run_brief"]["front_matter"].update(run_id=final, issuer_id="CZR", cp0_sha256=digest)
    doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][:2] = [final, "CZR"]
    doc["handoffs"] = {
        "CP-0": {
            "status": "accepted",
            "sha256": digest,
            "tables": {},
            "citations": [],
            "front_matter": {"module_id": "CP-0", "run_id": pending, "issuer_id": "CZR"},
        }
    }
    doc["steps"] = {"CP-0": {"status": "accepted", "sha256": digest}}
    return doc


@pytest.mark.parametrize("kind", ["html", "md"])
@pytest.mark.parametrize("suffix", ["", "-2"])
def test_preserves_bound_native_pending_cp0_identity(kind: str, suffix: str) -> None:
    from rbotlib.prior_report import inspect_report

    doc = pending_cp0_document()
    doc["handoffs"]["CP-0"]["front_matter"]["run_id"] += suffix
    text = embed_json(doc) if kind == "html" else render_markdown(doc, [], [])
    parsed = parse_report(text, kind)
    assert parsed["handoffs"] == doc["handoffs"]
    assert (
        "CP-0 original state/origin lineage cannot be independently reconstructed from Report"
        in inspect_report(parsed)[2]
    )


@pytest.mark.parametrize(
    "defect",
    [
        "owner",
        "module",
        "issuer",
        "name",
        "date",
        "day",
        "missing-entry",
        "missing-step",
        "missing-brief",
        "mismatch",
        "invalid-hash",
    ],
)
def test_refuses_unbound_or_foreign_pending_alias(defect: str) -> None:
    doc = pending_cp0_document()
    entry = doc["handoffs"]["CP-0"]
    if defect == "owner":
        doc["handoffs"]["MODEL"] = doc["handoffs"].pop("CP-0")
        doc["steps"]["MODEL"] = doc["steps"].pop("CP-0")
        entry["front_matter"]["module_id"] = "MODEL"
    elif defect == "module":
        entry["front_matter"].pop("module_id")
    elif defect == "issuer":
        entry["front_matter"]["issuer_id"] = "FOREIGN"
    elif defect in ("name", "date", "day"):
        entry["front_matter"]["run_id"] = {
            "name": "earlier",
            "date": "20260230-unknown-pending",
            "day": "20261017-unknown-pending",
        }[defect]
        if defect == "date":
            final = "20260230-czr-full-credit-assessment"
            doc["run_id"] = doc["run_brief"]["front_matter"]["run_id"] = final
            doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][0] = final
    elif defect.startswith("missing-"):
        target = {
            "missing-entry": entry,
            "missing-step": doc["steps"]["CP-0"],
            "missing-brief": doc["run_brief"]["front_matter"],
        }[defect]
        target.pop("cp0_sha256" if defect == "missing-brief" else "sha256")
    elif defect == "mismatch":
        entry["sha256"] = "b" * 64
    else:
        entry["sha256"] = doc["steps"]["CP-0"]["sha256"] = doc["run_brief"]["front_matter"][
            "cp0_sha256"
        ] = "invalid"
    with pytest.raises(RunError):
        parse_report(embed_json(doc), "html")


@pytest.mark.parametrize("kind", ["html", "md"])
@pytest.mark.parametrize("explicit", [False, True])
def test_matching_and_older_omitted_module_identity_round_trip(kind: str, explicit: bool) -> None:
    doc = document()
    if explicit:
        doc["run_brief"]["front_matter"]["module_id"] = "RUN_BRIEF"
        doc["handoffs"]["MODEL"]["front_matter"]["module_id"] = "MODEL"
    text = embed_json(doc) if kind == "html" else render_markdown(doc, [], [])
    assert parse_report(text, kind)["run_brief"] == doc["run_brief"]
    assert parse_report(text, kind)["handoffs"] == doc["handoffs"]


@pytest.mark.parametrize("owner", ["MODEL", "RUN_BRIEF"])
@pytest.mark.parametrize("kind", ["html", "md"])
def test_refuses_explicit_conflicting_module_identity(owner: str, kind: str) -> None:
    doc = document()
    entry = doc["run_brief"] if owner == "RUN_BRIEF" else doc["handoffs"][owner]
    entry["front_matter"]["module_id"] = "CP-6"
    text = embed_json(doc) if kind == "html" else render_markdown(doc, [], [])
    with pytest.raises(RunError, match=f"{owner}: conflicting module_id"):
        parse_report(text, kind)


@pytest.mark.parametrize(
    "text",
    [
        "",
        '<script id="rbot-run">{}</script>',
        '<script type="application/json" id="rbot-run">[]</script>',
        '<script type="application/json" id="rbot-run">{</script>',
        '<script type="application/json" id="rbot-run" id="other">{}</script>',
    ],
)
def test_refuses_missing_wrong_tag_or_malformed(text: str) -> None:
    with pytest.raises(RunError):
        parse_report(text, "html")


@pytest.mark.parametrize("kind", ["html", "md"])
def test_refuses_multiple_payloads_and_duplicate_json_keys(kind: str) -> None:
    text = embed_json(document()) if kind == "html" else "```json rbot-run\n{}\n```\n"
    with pytest.raises(RunError, match="one"):
        parse_report(text + text, kind)
    bad = json.dumps(document()).replace('"schema":', '"schema":"rbot-run/1","schema":')
    tagged = f'<script type="application/json" id="rbot-run">{bad}</script>'
    with pytest.raises(RunError, match="duplicate JSON"):
        parse_report(tagged, "html")


@pytest.mark.parametrize(
    "change", ["identity", "timestamp", "columns", "width", "cell", "owner", "NaN"]
)
def test_schema_refusals(change: str) -> None:
    doc = document()
    table(doc, "model.house", ["item", "value"], [["debt", "100"]])
    entry = doc["handoffs"]["MODEL"]
    if change == "identity":
        entry["front_matter"]["issuer_id"] = "FOREIGN"
    elif change == "timestamp":
        doc["generated_at"] = "2026-10-14"
    elif change == "owner":
        doc["handoffs"]["OTHER"] = copy.deepcopy(entry)
        doc["steps"]["OTHER"] = {"status": "accepted"}
    elif change == "NaN":
        doc["extra"] = float("nan")
    else:
        entry["tables"]["model.house"] = {
            "columns": ["item", "item"] if change == "columns" else ["item", "value"],
            "rows": [["debt"]] if change == "width" else [["debt", 1]],
        }
    with pytest.raises(RunError):
        parse_report(embed_json(doc), "html")


@pytest.mark.parametrize("defect", ["overflow", "reserved", "status", "truncated"])
def test_trust_seam_regressions(defect: str) -> None:
    doc = document()
    table(
        doc,
        "model.house",
        ["item", "value"],
        [],
    )
    if defect == "reserved":
        doc["handoffs"]["RUN_BRIEF"] = copy.deepcopy(doc["run_brief"])
    if defect == "status":
        doc["handoffs"]["MODEL"]["status"] = "blocked"
    text = embed_json(doc)
    if defect == "overflow":
        text = text.replace('"schema":', '"overflow":1e9999,"schema":')
    if defect == "truncated":
        text = "```json rbot-run\n" + json.dumps(doc) + "\n```\n```json rbot-run\n{}"
    with pytest.raises(RunError):
        parse_report(text, "md" if defect == "truncated" else "html")


@pytest.mark.parametrize("defect", ["missing-header-id", "date", "nested-fence"])
def test_identity_and_fence_boundaries(defect: str) -> None:
    doc = document()
    if defect == "missing-header-id":
        doc["run_brief"]["tables"]["snapshot.run_header"] = {
            "columns": ["report_date"],
            "rows": [["—"]],
        }
    if defect == "date":
        doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][-1] = "2026-02-30"
    text, kind = embed_json(doc), "html"
    if defect == "nested-fence":
        text, kind = "````text\n```json rbot-run\n" + json.dumps(doc) + "\n```\n````\n", "md"
    with pytest.raises(RunError):
        parse_report(text, kind)


@pytest.mark.parametrize(
    "report_date,basis", [("—", "generated_at"), ("2026-10-15", "report_date")]
)
def test_metadata_preserves_date_basis_and_older_omissions(report_date: str, basis: str) -> None:
    from rbotlib.prior_report import inspect_report

    doc = document()
    doc.pop("modules")
    doc.pop("fetched")
    doc["run_brief"]["tables"]["snapshot.run_header"]["rows"][0][-1] = report_date
    parsed = parse_report(embed_json(doc), "html")
    meta, tables, limitations = inspect_report(parsed)
    assert parsed == doc and meta["date_basis"] == basis
    assert meta["report_date"] == ("2026-10-14" if report_date == "—" else report_date)
    assert tables["snapshot.run_header"]["owner"] == "RUN_BRIEF"
    assert limitations == ["older Report omits modules", "older Report omits fetched"]


def test_unicode_separators_inside_json_are_not_markdown_fences() -> None:
    doc = document()
    table(doc, "model.house", ["item", "value"], [["debt", "before\u0085```\u0085after"]])
    assert parse_report(render_markdown(doc, [], []), "md")["handoffs"] == doc["handoffs"]


@given(st.text())
def test_source_strings_round_trip_without_numeric_or_html_coercion(value: str) -> None:
    doc = document()
    table(doc, "model.house", ["item", "value"], [["debt", value]])
    assert parse_report(embed_json(doc), "html") == doc
    assert parse_report(render_markdown(doc, [], []), "md")["handoffs"] == doc["handoffs"]
