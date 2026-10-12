"""Test fixture: a CP-0 Handoff written from a known classification, standing in for the model.

`cp0_handoff` writes `cp0.source_inventory` from the run's `prepared/index.json` and a
classification per file (class, document type, entity named, entity match), and
`cp0.portfolios` from `prepared/portfolios/`. `registry_classification` takes the
classification from the corpus registry's hand-checked `class`, `document_type` and
`entity`. The Handoff validates against the real CP-0 contract with `--run`.
"""

from __future__ import annotations

import json
from pathlib import Path

from rbotlib.corpus import Pack
from rbotlib.cp0 import empty_text

Classification = dict[str, tuple[str, str, str, str]]
COLUMNS = (
    "file class document_type entity_named entity_match period_covered document_date "
    "readable image_read pages sha256 note"
).split()


def registry_classification(pack: Pack) -> Classification:
    """File -> (class, document type, entity, Yes/No): about the issuer, a comparable or a
    portfolio of the pack; a misfiled issuer document or another fund's file is No."""
    issuer = pack.data["issuer"]["id"]
    portfolios = set(pack.data["portfolios"])
    out: Classification = {}
    for f in pack.files:
        match = f.entity == issuer or f.cls == "market" or f.entity in portfolios
        out[f.path] = (f.cls, f.document_type, f.entity, "Yes" if match else "No")
    return out


def _table(table_id: str, columns: list[str], rows: list[list[str]]) -> list[str]:
    head = [f"<!-- table: {table_id} -->", "| " + " | ".join(columns) + " |"]
    return [*head, "|" + "---|" * len(columns), *("| " + " | ".join(r) + " |" for r in rows), ""]


def _inventory(run: Path, classes: Classification) -> list[list[str]]:
    index = json.loads((run / "prepared" / "index.json").read_text(encoding="utf-8"))
    rows = []
    for record in index["files"]:
        cls, kind, entity, match = classes[record["path"]]
        unusable = record["unreadable"] or record["image_read"] or empty_text(run, record)
        readable = "No" if unusable else "Yes"
        image = "Yes" if record["image_read"] else "No"
        cells = [record["path"], cls, kind, entity, match, "—", "—", readable, image]
        rows.append([*cells, str(record["pages"]), record["sha256"], "—"])
    return rows


def _portfolios(run: Path) -> list[list[str]]:
    rows = []
    for path in sorted((run / "prepared" / "portfolios").glob("*.json")):
        p = json.loads(path.read_text(encoding="utf-8"))
        names = (p["portfolio_id"], p["portfolio_name"], p["strategy"])
        rows.append([*names, p["positions_file"], p["limits_file"], p["as_of"]])
    return rows


def cp0_handoff(
    run: Path, issuer: tuple[str, str], as_of: str, classes: Classification, *, primary: bool
) -> str:
    """A CP-0 Handoff for `run`; `issuer` is (name, id), both Analyst-asserted."""
    name, issuer_id = issuer
    prefill = [
        ["issuer", "—", name, "Analyst-asserted", "—"],
        ["issuer_id", "—", issuer_id, "Analyst-asserted", "—"],
        ["as_of_date", "—", as_of, "Analyst-asserted", "—"],
        ["primary", "—", "Yes" if primary else "—", "Analyst-asserted" if primary else "Gap", "—"],
    ]
    front = ["---", "module_id: CP-0", f"run_id: {run.name}", f"issuer_id: {issuer_id}"]
    front += [f"analysis_date: {as_of}", "qa_status: Restricted", "inputs: none", "---", ""]
    columns = ["field", "tranche_id", "value", "status", "cite"]
    research = "question_id question why_it_matters consumer_module evidence_needed".split()
    prior = "file report_date run_id pathway depth offered".split()
    portfolios = "portfolio_id portfolio_name strategy positions_file limits_file as_of_date"
    lines = [
        *front,
        "## Analysis",
        "",
        "Test fixture: the classification is the corpus registry's, not a model's.",
        "",
        "## Tables",
        "",
        *_table("cp0.source_inventory", COLUMNS, _inventory(run, classes)),
        *_table("cp0.run_brief_prefill", columns, prefill),
        *_table("cp0.research_questions", research, []),
        *_table("cp0.prior_case", prior, []),
        *_table("cp0.portfolios", portfolios.split(), _portfolios(run)),
        "## Gaps",
        "",
        "- The objective and the analyst come from the analyst at turn 1.",
        "",
        "## Citations",
        "",
        *_table("citations", ["id", "source", "locator", "excerpt"], []),
    ]
    return "\n".join(lines)
