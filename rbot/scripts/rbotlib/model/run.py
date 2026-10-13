"""`rbot model --run <RUN>`: the MODEL host step (spec §6.8).

Reads `handoffs/CP-1.md` (required), `handoffs/CP-1D.md` (optional) and
`run-brief.md` (required); writes `model.json` and
`handoffs/MODEL.md`. This is the only I/O in `rbotlib.model`; every figure it
writes comes from the pure modules. A malformed input raises
`ModelInputError` naming the file, or the table, row and column (a table
tagged but not readable as a table, or tagged twice, is malformed), and then
nothing is written. The two outputs are staged as temporary files beside
their targets before any publish; staging failure leaves each as it was.
Each publish is an atomic replacement, while a failure between replacements
can leave a partially published set (reported as exit 1). A
link in the run folder is replaced, never followed, and a `handoffs` folder
that resolves outside the run is refused.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from rbotlib.handoff import Handoff, HandoffError, parse
from rbotlib.inventory import RunError
from rbotlib.model.assemble import CreditModel, ModelInputs, credit_model, reconciliation_faults
from rbotlib.model.citations import Citations, citation_rows
from rbotlib.model.history import BALANCE_METRICS, FLOW_METRICS
from rbotlib.model.house import HouseView, house_view, with_debt_like_lines
from rbotlib.model.house_inputs import (
    HouseInputs,
    _ltm_judgments,
    assessment_limitations,
    assessments,
    brief_fields,
    check_entity_profile,
    debt_like_items,
    effective_registers,
    equity_value,
    identities,
)
from rbotlib.model.inputs import cp1_registers
from rbotlib.model.output import (
    MAX_COLUMNS,
    MAX_LINES,
    Built,
    Limitation,
    dumps,
    model_json,
    model_md,
    qa_status,
    sources_cut,
    uncited_figures,
)
from rbotlib.model.reader import ModelInputError
from rbotlib.model.registers import Cp1Registers
from rbotlib.model.snapshot import Context, build_tables, display, limitation_rows, unit_label


@dataclass(frozen=True, slots=True)
class Read:
    handoff: Handoff
    sha256: str


@dataclass(frozen=True, slots=True)
class Written:
    qa_status: str
    limitations: tuple[Limitation, ...]


@dataclass(frozen=True, slots=True)
class Options:
    missing: str = ""
    managed: bool = False


def read_handoff(path: Path) -> Read:
    if not path.exists():
        raise ModelInputError(f"{path.name}: missing; the Model needs it")
    try:
        return captured_handoff(path.read_text(encoding="utf-8").encode("utf-8"), path.name)
    except (OSError, UnicodeDecodeError) as exc:
        raise ModelInputError(f"{path.name}: {exc}") from exc


def captured_handoff(raw: bytes, label: str) -> Read:
    """Parse the exact captured bytes; their digest is never newline-normalized."""
    try:
        handoff = parse(raw.decode("utf-8"))
    except (UnicodeDecodeError, HandoffError) as exc:
        raise ModelInputError(f"{label}: {exc}") from exc
    malformed = handoff.orphan_tags or handoff.invalid_tags
    if malformed:
        raise ModelInputError(f"{label}: table {malformed[0]} is tagged but malformed")
    if handoff.duplicate_tags:
        raise ModelInputError(f"{label}: table {handoff.duplicate_tags[0]} tagged twice")
    return Read(handoff, hashlib.sha256(raw).hexdigest())


def stage_file(target: Path, data: bytes) -> Path:
    """`data` in a new temporary file beside `target`, flushed to disk."""
    descriptor, name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
    staged = Path(name)
    complete = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        staged.chmod(0o644)
        complete = True
        return staged
    finally:
        if not complete:
            staged.unlink(missing_ok=True)


def write_all(files: dict[Path, bytes]) -> None:
    """Stage every file, then replace each target (a link is replaced, not
    followed); no temporary file is left behind."""
    staged: list[tuple[Path, Path]] = []
    for target in files:
        if target.is_dir() and not target.is_symlink():
            raise IsADirectoryError(f"{target} is a folder")
    try:
        for target, data in files.items():
            staged.append((stage_file(target, data), target))
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def _model_limitations(model: CreditModel) -> list[Limitation]:
    codes = (
        ("No projections", "NO_PROJECTIONS"),
        ("PF adjustment to a metric", "PF_NOT_APPLIED"),
        ("PF register states both", "PF_DOUBLE_COUNT"),
    )
    found = []
    for text in model.limitations:
        code = next((c for start, c in codes if text.startswith(start)), "CELL_NOTE")
        found.append(Limitation(code, text))
    for fault in reconciliation_faults(model):
        column_id, _, bridge = fault.rpartition(":")
        found.append(
            Limitation("RECONCILIATION_FAULT", f"{fault} does not close", bridge, column_id)
        )
    return found


def unread_metrics(regs: Cp1Registers) -> list[Limitation]:
    """`UNKNOWN_METRIC` for each account metric no Model line reads (CP-1 also
    feeds other modules, so it is named, not refused: a typo would otherwise
    leave its figure out without a trace)."""
    read = FLOW_METRICS | BALANCE_METRICS
    unread = dict.fromkeys(a.metric_id for a in regs.accounts if a.metric_id not in read)
    return [
        Limitation("UNKNOWN_METRIC", f"{m}: no Model line reads this account metric")
        for m in unread
    ]


def _analysis(view: HouseView) -> str:
    if view.column is None:
        return "Host-computed Model (`rbot model`): no LTM column, so no house view."
    ssim = display(view.item("ssim_ebitda").cell.value, "MONEY")
    structuring = display(view.item("structuring_ebitda").cell.value, "MONEY")
    multiple = display(view.item("ssim_multiple").cell.value, "MULTIPLE")
    return (
        "Host-computed Model (`rbot model`): every figure is arithmetic on CP-1's registers, "
        f"with CP-1D's house view where CP-1D ran. On the {view.column.label} column SSIM "
        f"EBITDA is {ssim}, Structuring EBITDA {structuring} and the SSIM Multiple {multiple}x. "
        "Each cell's passport is in model.json."
    )


def _inputs(
    cp1: Read, brief: Read, cp1d: Read | None
) -> tuple[HouseInputs, Cp1Registers, CreditModel]:
    """The house inputs, CP-1's registers with CP-1D's house statuses, and
    the Model run on them with `exclude_unrealised`."""
    regs = cp1_registers(cp1.handoff.tables)
    check_entity_profile(cp1.handoff.tables, regs)
    tables = cp1d.handoff.tables if cp1d else {}
    inputs = HouseInputs(
        identities(cp1.handoff.tables),
        equity_value(cp1.handoff.tables),
        assessments(tables),
        debt_like_items(tables, regs),
        brief_fields(brief.handoff.front_matter, brief.handoff.tables),
    )
    regs = effective_registers(regs, inputs.assessments)
    model = credit_model(ModelInputs(regs, exclude_unrealised=True))
    model = with_debt_like_lines(model, regs, inputs.debt_like)
    if len(model.columns) > MAX_COLUMNS or len(model.lines) > MAX_LINES:
        raise ModelInputError(
            f"the Model has {len(model.columns)} columns and {len(model.lines)} lines; "
            f"model.json carries at most {MAX_COLUMNS} and {MAX_LINES}"
        )
    return inputs, regs, model


def _judgment_limits(regs: Cp1Registers, inputs: HouseInputs) -> list[Limitation]:
    latest = _ltm_judgments(regs, inputs.assessments)
    newest = max(
        (p.end_date for p in regs.periods if p.period_type == "LTM" and p.end_date is not None),
        default=None,
    )
    return [
        Limitation(
            "CP1D_CURRENT_JUDGMENT_MISSING",
            f"{addback}: no CP-1D judgment for newest registered LTM {newest or 'unavailable'}; "
            "conservative exact-period fallback retained",
        )
        for addback in sorted({b.addback_id for b in regs.addbacks} - latest.keys())
    ]


def build(
    cp1: Read,
    brief: Read,
    cp1d: Read | None,
    generated_at: str,
    missing: str | Options = "",
) -> tuple[Written, dict[str, bytes]]:
    """Render qualified captured inputs without reading or publishing files."""
    options = missing if isinstance(missing, Options) else Options(missing)
    inputs, regs, model = _inputs(cp1, brief, cp1d)
    mixed = assessment_limitations(regs, inputs.assessments)
    view = house_view(model, regs, inputs)
    modules = {"CP-1": citation_rows("CP-1", cp1.handoff.tables.get("citations"))}
    modules["CP-1D"] = citation_rows("CP-1D", cp1d.handoff.tables.get("citations")) if cp1d else {}
    citations = Citations(modules)
    tables, table_limits = build_tables(Context(model, regs, view, inputs, citations))
    limitations = [
        *_model_limitations(model),
        *(Limitation(code, why) for code, why in (*view.limitations, *table_limits, *mixed)),
        *sources_cut(model, citations),
        *unread_metrics(regs),
        *uncited_figures(model, citations),
    ]
    if cp1d is None:
        why = options.missing or "no CP-1D Handoff: add-backs keep CP-1's realization status"
        limitations.append(Limitation("CP1D_NOT_READ", why))
    if options.managed and cp1d is not None:
        limitations.extend(_judgment_limits(regs, inputs))
    tables["model.limitations"] = limitation_rows(
        (x.code, x.message, x.line_id, x.column_id) for x in limitations
    )
    shas = {"CP-1": cp1.sha256, "CP-1D": cp1d.sha256 if cp1d else None}
    built = Built(
        model,
        view,
        inputs,
        tables,
        citations,
        unit_labels={line.line_id: unit_label(line, regs) for line in model.lines},
        shas={**shas, "CP-2G": None, "RUN_BRIEF": brief.sha256},
        limitations=tuple(limitations),
        faults=reconciliation_faults(model),
    )
    data = model_json(built, generated_at)
    front = {
        "module_id": "MODEL",
        "run_id": inputs.brief.run_id,
        "issuer_id": cp1.handoff.front_matter.get("issuer_id", "\N{EM DASH}"),
        "analysis_date": cp1.handoff.front_matter.get("analysis_date", "\N{EM DASH}"),
        "inputs": ", ".join(["CP-1", *(["CP-1D"] if cp1d else []), "RUN_BRIEF"]),
    }
    markdown = model_md(front, tables, citations, limitations, _analysis(view))
    return Written(qa_status(limitations), tuple(limitations)), {
        "model.json": dumps(data).encode("utf-8"),
        "handoffs/MODEL.md": markdown.encode("utf-8"),
    }


def run_model(run: Path, generated_at: str) -> Written:
    """Build the Model for the run folder and write its two files."""
    from rbotlib import state

    state.write_guard(run)
    if not (run / "handoffs").resolve().is_relative_to(run.resolve()):
        raise ModelInputError("handoffs resolves outside the run folder")
    cp1 = read_handoff(run / "handoffs" / "CP-1.md")
    brief = read_handoff(run / "run-brief.md")
    cp1d_path = run / "handoffs" / "CP-1D.md"
    cp1d = read_handoff(cp1d_path) if cp1d_path.exists() else None
    written, files = build(cp1, brief, cp1d, generated_at)
    write_all({run / name: raw for name, raw in files.items()})
    return written


def run_command(args: argparse.Namespace) -> int:
    """`rbot model --run <RUN>`: 0 with the limitations printed, 1 naming the
    malformed input."""
    now = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        written = run_model(Path(args.run_dir), now)
    except (ModelInputError, RunError) as exc:
        print(f"model: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"model: cannot write the outputs: {exc}", file=sys.stderr)
        return 1
    print(f"model.json and handoffs/MODEL.md written; qa_status {written.qa_status}")
    for limitation in written.limitations:
        print(f"{limitation.code}: {limitation.message}")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    m = sub.add_parser("model", help="build model.json and MODEL.md for a run")
    m.add_argument("--run", dest="run_dir", required=True, help="the run folder")
    m.set_defaults(run=run_command)
