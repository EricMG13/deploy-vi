"""`rbot calc <name> --in <json> [--out <json>]`: the module calculators (interfaces spec §9).

Each calculator is a module of this package with a pure `compute(data) -> dict` that raises
`CalcError` naming the invalid field, and `markdown(result) -> str` that prints the owning
table's calculator columns. The command reads the input with every JSON number as a Decimal,
prints the Markdown, writes the whole result to `--out` and exits 1 on invalid input. Plans 12
and 13 add their calculators to `CALCULATORS`.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import ModuleType

from rbotlib.calc import (
    bond_analytics,
    covenant_headroom,
    liquidity_bridge,
    peer_statistics,
)
from rbotlib.calc.bond_analytics import CalcError
from rbotlib.fsio import write_atomic

CALCULATORS: dict[str, ModuleType] = {
    "bond_analytics": bond_analytics,
    "covenant_headroom": covenant_headroom,
    "liquidity_bridge": liquidity_bridge,
    "peer_statistics": peer_statistics,
}


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    data: dict[str, object] = {}
    for field, value in pairs:
        if field in data:
            raise CalcError(f"JSON: duplicate field {field!r}")
        data[field] = value
    return data


def _supported_text(data: object) -> None:
    pending: list[tuple[str, object]] = [("input", data)]
    while pending:
        where, value = pending.pop()
        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise CalcError(f"{where}: unsupported Unicode surrogate") from exc
        elif isinstance(value, dict):
            for key, item in value.items():
                pending.extend(((f"{where} key", key), (f"{where}.{key!r}", item)))
        elif isinstance(value, list):
            pending.extend((f"{where}[{i}]", item) for i, item in enumerate(value))


def read_input(path: Path) -> object:
    """The input document; a number keeps its written digits as a Decimal."""
    try:
        data: object = json.loads(
            path.read_text(encoding="utf-8"), parse_float=Decimal, object_pairs_hook=_unique_fields
        )
    except json.JSONDecodeError as exc:
        raise CalcError(f"{path}: not valid JSON: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CalcError(f"{path}: not UTF-8 text ({exc.reason})") from exc
    except CalcError:
        raise
    except (ValueError, RecursionError, InvalidOperation) as exc:
        raise CalcError(f"{path}: unsupported JSON ({exc})") from exc
    _supported_text(data)
    return data


def run_command(args: argparse.Namespace) -> int:
    calculator = CALCULATORS[args.name]
    try:
        result = calculator.compute(read_input(Path(args.in_path)))
        if args.out_path:
            text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
            write_atomic(Path(args.out_path), text)
    except (CalcError, OSError) as exc:
        print(f"error: {exc}")
        return 1
    print(calculator.markdown(result), end="")
    return 0


def add_command(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    c = sub.add_parser("calc", help="run a module calculator on a JSON input")
    c.add_argument("name", choices=sorted(CALCULATORS))
    c.add_argument("--in", dest="in_path", required=True, help="the calculator's JSON input")
    c.add_argument("--out", dest="out_path", help="write the full JSON result here")
    c.set_defaults(run=run_command)
