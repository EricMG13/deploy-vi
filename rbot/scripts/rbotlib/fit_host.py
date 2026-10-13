"""FIT-specific current source capture and deterministic complete-set qualification."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from rbotlib import attempts, dispatch, fit, portfolio, prepare, state
from rbotlib import next as next_step
from rbotlib.fit_arithmetic import Portfolio
from rbotlib.inventory import RunError
from rbotlib.model import qualification as model
from rbotlib.model import run as writer
from rbotlib.rules import load_rules


@dataclass(frozen=True, slots=True)
class Inputs:
    cp1: writer.Read
    brief: writer.Read
    cp3: writer.Read
    cp1a: writer.Read | None
    portfolios: tuple[Portfolio, ...]
    fingerprints: dict[str, str | None]
    missing: str

    def hashes(self) -> dict[str, str | None]:
        return dict(self.fingerprints)


def _module(run: Path, root: Path, record: state.Record, module: str) -> writer.Read:
    current = record["steps"].get(module, {})
    if current.get("status") not in ("accepted", "blocked"):
        raise RunError(f"required input {module}: {current.get('status', 'missing')}")
    attempts.read_history(run, module, current)
    dispatch._qualified_module(run, root, module, record, load_rules(root))
    captured = model._capture(run, f"handoffs/{module}.md", current["sha256"])
    if captured.handoff.front_matter.get("analysis_date") != record["as_of_date"]:
        raise RunError(f"{module}: analysis_date differs from approved state")
    return captured


def _source_portfolios(
    record: state.Record, inventory: state.Record
) -> dict[str, portfolio.Portfolio]:
    found: dict[str, portfolio.Portfolio] = {}
    for entry in inventory["files"]:
        if entry["kind"] in ("csv", "xlsx"):
            original = dispatch._file(Path(record["pack_root"]), entry["path"])
            try:
                read = prepare.read(original, entry["kind"])
            except prepare.UnreadableError:
                continue  # as in prepare: no portfolio can originate in an unreadable sheet
            finally:
                if dispatch._sha(original) != entry["sha256"]:
                    raise RunError("FIT: portfolio source changed during capture")
            prepare._sheet_portfolios(entry, read, found)
    return found


def _portfolios(
    run: Path, root: Path, record: state.Record, brief: writer.Read
) -> tuple[tuple[Portfolio, ...], dict[str, str | None]]:
    index = dispatch._json(dispatch._file(run, "prepared/index.json"))
    inventory = dispatch._json(dispatch._file(run, "inventory.json"))
    found = _source_portfolios(record, inventory)
    prepared = {row["portfolio_id"]: row["json"] for row in index["portfolios"]}
    captured, hashes = [], {}
    for entry in fit._records(brief.handoff.tables.get("brief.portfolios")):
        pid, name = entry["portfolio_id"], entry["prepared_json"]
        if (
            name != f"prepared/portfolios/{pid}.json"
            or prepared.get(pid) != name
            or pid not in found
        ):
            raise RunError(f"FIT: {pid}: not a declared prepared source portfolio")
        raw = dispatch._file(run, name).read_bytes()
        data = fit._check_prepared(json.loads(raw, object_pairs_hook=state._pairs), name)
        expected = portfolio.to_json(found[pid], load_rules(root))
        identities = {"as_of_date": "as_of"} | {
            k: k
            for k in ("portfolio_id", "portfolio_name", "strategy", "positions_file", "limits_file")
        }
        if data != expected or any(entry[k] != data[v] for k, v in identities.items()):
            raise RunError(f"FIT: {pid}: prepared identity/date/content differs from source/brief")
        if pid in hashes:
            raise RunError(f"FIT: duplicate portfolio {pid}")
        captured.append(fit.portfolio_data(data, name))
        hashes[pid] = dispatch._sha(dispatch._file(run, name))
        if hashes[pid] != model._hashes({name: raw})[name]:
            raise RunError(f"FIT: {pid}: prepared bytes changed during capture")
    return tuple(captured), {f"portfolio:{pid}": sha for pid, sha in hashes.items()}


class Fit:
    step, origin, handoff = "FIT", "host-fit/1", "handoffs/FIT.md"

    @staticmethod
    def outputs(captured: Inputs) -> tuple[str, ...]:
        return (*(f"fit/{p.portfolio_id}.json" for p in captured.portfolios), "handoffs/FIT.md")

    @staticmethod
    def inputs(run: Path, root: Path, record: state.Record) -> Inputs:
        rules = load_rules(root)
        next_step._dependencies(root, record, rules)
        dispatch._prepared(run, record)
        if record["approval"] is None:
            raise RunError("FIT requires analyst Approval")
        dispatch._context(run, root, record, rules)
        cp1, cp3 = (_module(run, root, record, name) for name in ("CP-1", "CP-3"))
        brief = model._capture(run, "run-brief.md", record["run_brief_sha256"])
        from rbotlib.host_validate import brief_shape

        brief_shape(brief.handoff, record)
        cp1a = None
        status = record["steps"].get("CP-1A", {}).get("status", "missing")
        missing = f"CP-1A: {status}; excluded; sector/country may be unknown"
        if status in ("accepted", "blocked"):
            try:
                cp1a = _module(run, root, record, "CP-1A")
                missing = ""
            except (OSError, ValueError, KeyError, TypeError) as exc:
                missing = f"CP-1A: unqualified ({exc}); excluded; sector/country may be unknown"
        portfolios, hashes = _portfolios(run, root, record, brief)
        if not portfolios:
            raise RunError("FIT: no portfolio context; approved plan must skip FIT")
        captured = Inputs(
            cp1,
            brief,
            cp3,
            cp1a,
            portfolios,
            hashes
            | {
                "CP-1": cp1.sha256,
                "CP-3": cp3.sha256,
                "RUN_BRIEF": brief.sha256,
                "CP-1A": cp1a.sha256 if cp1a else None,
                "inventory": dispatch._sha(dispatch._file(run, "inventory.json")),
                "prepared/index": dispatch._sha(dispatch._file(run, "prepared/index.json")),
            },
            missing,
        )
        for name in (*Fit.outputs(captured), "log/rbot.log"):
            dispatch._target(run, name)
        for path in (run / "fit").glob("*.json"):
            if f"fit/{path.name}" not in Fit.outputs(captured):
                raise RunError("FIT: unregistered portfolio output requires the recovery owner")
        return captured

    @staticmethod
    def build(captured: Inputs, generated_at: str) -> tuple[fit.Written, dict[str, bytes]]:
        written, files = fit.build(
            captured.brief.handoff,
            captured.cp1.handoff,
            captured.cp1a.handoff if captured.cp1a else None,
            captured.portfolios,
            captured.missing,
        )
        for name in (n for n in files if n.endswith(".json")):
            data = json.loads(files[name])
            data |= {
                "run_id": captured.brief.handoff.front_matter["run_id"],
                "generated_at": generated_at,
                "inputs": captured.hashes(),
            }
            files[name] = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()
        return written, files

    @staticmethod
    def validate(
        files: dict[str, bytes], captured: Inputs, record: state.Record, generated_at: str
    ) -> fit.Written:
        written, expected = Fit.build(captured, generated_at)
        if files != expected or captured.brief.handoff.front_matter["run_id"] != record["run_id"]:
            raise RunError("FIT completion: complete JSON/Handoff differs from current host origin")
        return written

    @staticmethod
    def show(written: fit.Written) -> None:
        print(
            f"handoffs/FIT.md and fit/*.json written; {len(written.fits)} "
            "portfolio x instrument fit(s)"
        )
        for f in written.fits:
            print(
                f"{f.portfolio.portfolio_id} {f.instrument.facility_id}: {f.verdict} ({f.reason})"
            )
        sys.stdout.flush()


def qualify(run: Path, root: Path, record: state.Record) -> None:
    current = record["steps"].get("FIT", {})
    evidence = current.get("host_execution", {})
    if (
        not isinstance(evidence, dict)
        or current.get("status") != "accepted"
        or current.get("host_exit") != 0
        or current.get("attempts") != 1
        or evidence.get("origin") != Fit.origin
        or not state._text(evidence.get("token"))
        or not all(
            state._stamp(v)
            for v in (
                current.get("started_at"),
                current.get("finished_at"),
                evidence.get("generated_at"),
            )
        )
    ):
        raise RunError("FIT: accepted checked host execution required")
    captured = Fit.inputs(run, root, record)
    files = {name: dispatch._file(run, name).read_bytes() for name in Fit.outputs(captured)}
    written = Fit.validate(files, captured, record, evidence["generated_at"])
    hashes = model._hashes(files)
    if (
        evidence.get("inputs") != captured.hashes()
        or current.get("outputs") != hashes
        or current.get("sha256") != hashes[Fit.handoff]
        or current.get("handoff") != Fit.handoff
        or current.get("qa_status") != written.qa_status
    ):
        raise RunError("FIT: current inputs/outputs/hash/QA differ from accepted execution")
