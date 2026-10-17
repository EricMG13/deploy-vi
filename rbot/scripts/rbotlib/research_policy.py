"""CP-DR's table rules (Plan 10, ruling R16): finding `research_policy`, exit 2.

Every question has one answer row; an `Answered` or `Partly answered` question rests on
existing evidence rows (`none` is for `Unanswered` only); a `Fetched` evidence row cites a
`fetched/` page and a `Pack` row does not; with a Run Brief, every question id is approved.
Messages name ids, never source text.
"""

from __future__ import annotations

from pathlib import Path

from rbotlib import fetched
from rbotlib.handoff import Handoff, Table, markers
from rbotlib.inventory import RunError
from rbotlib.validate import Finding

ANSWERED = ("Answered", "Partly answered")


def _records(table: Table | None) -> list[dict[str, str]]:
    if table is None:
        return []
    cols = [c.casefold() for c in table.columns]
    return [dict(zip(cols, row, strict=True)) for row in table.rows if len(row) == len(cols)]


def _ids(cell: str) -> list[str]:
    return [i.strip() for i in cell.split(";") if i.strip()]


def _answer(
    q: dict[str, str], answers: list[dict[str, str]], evidence_ids: set[str]
) -> list[Finding]:
    qid, status = q.get("question_id", ""), q.get("status", "")
    rows = [a for a in answers if a.get("question_id", "") == qid]
    if len(rows) != 1:
        return [
            Finding(
                "research_policy", f"{qid}: needs exactly one cpdr.answers row, has {len(rows)}"
            )
        ]
    given = [i for i in _ids(rows[0].get("evidence_ids", "")) if i != "none"]
    found = [
        Finding("research_policy", f"{qid}: evidence id {i} has no cpdr.evidence row")
        for i in given
        if i not in evidence_ids
    ]
    if status in ANSWERED and not given:
        found.append(Finding("research_policy", f"{qid}: {status} needs evidence rows"))
    return found


def _answers(
    questions: list[dict[str, str]], answers: list[dict[str, str]], evidence_ids: set[str]
) -> list[Finding]:
    return [f for q in questions for f in _answer(q, answers, evidence_ids)]


def _sources(h: Handoff) -> dict[str, str]:
    table = h.tables.get("citations")
    return {row[0]: row[1] for row in table.rows if len(row) > 1} if table else {}


def _evidence(evidence: list[dict[str, str]], sources: dict[str, str]) -> list[Finding]:
    found: list[Finding] = []
    for row in evidence:
        cited = [sources.get(c, "") for c in markers(row.get("cite", ""))]
        has_fetched = any(s.startswith("fetched/") for s in cited)
        kind, eid = row.get("source_type", ""), row.get("evidence_id", "")
        if kind == "Fetched" and not has_fetched:
            found.append(
                Finding("research_policy", f"{eid}: a Fetched row must cite a fetched/ page")
            )
        if kind == "Pack" and has_fetched:
            found.append(Finding("research_policy", f"{eid}: a Pack row must not cite fetched/"))
    return found


def _approved(questions: list[dict[str, str]], run: Path | None) -> list[Finding]:
    """Without a Run Brief in the run there is nothing to compare (older and corpus runs)."""
    if run is None or not (run / fetched.BRIEF).is_file():
        return []
    try:
        approved = set(fetched.approved_questions(run))
    except RunError as exc:
        return [Finding("run_error", str(exc))]
    return [
        Finding("research_policy", f"{q.get('question_id', '')}: not an approved research question")
        for q in questions
        if q.get("question_id", "") not in approved
    ]


def findings(h: Handoff, run: Path | None) -> list[Finding]:
    """The rules above for a CP-DR Handoff; a Blocked one may leave its tables short."""
    if h.front_matter.get("qa_status") == "Blocked":
        return []
    questions = _records(h.tables.get("cpdr.questions"))
    answers = _records(h.tables.get("cpdr.answers"))
    evidence = _records(h.tables.get("cpdr.evidence"))
    ids = {e.get("evidence_id", "") for e in evidence}
    return (
        _answers(questions, answers, ids)
        + _evidence(evidence, _sources(h))
        + _approved(questions, run)
    )
