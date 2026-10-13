"""Precise host producers use current execution/Approval, never Module contracts."""

from __future__ import annotations

from pathlib import Path

from rbotlib import brief, dispatch, state
from rbotlib.handoff import Handoff
from rbotlib.inventory import RunError
from rbotlib.rules import load_rules


def brief_shape(handoff: Handoff, record: state.Record) -> None:
    from rbotlib.origins import cp0_anchor

    expected = {
        "module_id": "RUN_BRIEF",
        "run_id": record["run_id"],
        "issuer_id": record["issuer_id"],
        "analysis_date": record["as_of_date"],
    }
    columns = brief.COLUMNS | {"citations": ("id", "source", "locator", "excerpt")}
    if (
        any(handoff.front_matter.get(k) != v for k, v in expected.items())
        or handoff.front_matter.get("qa_status") not in ("Pass", "Restricted")
        or handoff.front_matter.get("cp0_sha256") != cp0_anchor(record)
        or handoff.sections != ["Analysis", "Tables", "Gaps", "Citations"]
        or handoff.invalid_tags
        or handoff.orphan_tags
        or handoff.duplicate_tags
        or set(handoff.tables) != set(columns)
        or any(tuple(handoff.tables[k].columns) != v for k, v in columns.items())
    ):
        raise RunError("RUN_BRIEF: current identity/source/Handoff shape/context differs")
    header = handoff.tables["snapshot.run_header"]
    rows = [dict(zip(header.columns, row, strict=True)) for row in header.rows]
    fields_table = handoff.tables["brief.run_brief_fields"]
    fields = {r[0]: r[1] for r in fields_table.rows}
    if (
        len(rows) != 1
        or len(fields) != len(fields_table.rows)
        or rows[0]["run_id"] != record["run_id"]
        or any(rows[0][k] != fields.get(k) for k in rows[0] if k in fields)
    ):
        raise RunError("RUN_BRIEF: header/field origin differs")


def qualify(run: Path, root: Path, module: str, path: Path) -> None:
    run, root = state.run_path(run), dispatch._root(root)
    from rbotlib.current import reconcile

    reconcile(run, root)
    name = "run-brief.md" if module == "RUN_BRIEF" else f"handoffs/{module}.md"
    if path.absolute() != dispatch._file(run, name):
        raise RunError(f"{module}: expected the current registered host path {name}")
    record = state.read(run)
    if module == "MODEL":
        from rbotlib.model.qualification import qualify as model

        model(run, root, record)
    elif module == "FIT":
        from rbotlib.fit_host import qualify as fit

        fit(run, root, record)
    elif module == "RUN_BRIEF":
        if record["approval"] is None:
            raise RunError("RUN_BRIEF: analyst Approval required")
        dispatch._prepared(run, record)
        dispatch._context(run, root, record, load_rules(root))
    else:
        raise RunError(f"{module}: host qualification unavailable")
