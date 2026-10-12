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
from decimal import Decimal
from pathlib import Path
from types import ModuleType

from rbotlib.calc import bond_analytics
from rbotlib.calc.bond_analytics import CalcError
from rbotlib.fsio import write_atomic

CALCULATORS: dict[str, ModuleType] = {"bond_analytics": bond_analytics}


def read_input(path: Path) -> object:
    """The input document; a number keeps its written digits as a Decimal."""
    try:
        data: object = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    except json.JSONDecodeError as exc:
        raise CalcError(f"{path}: not valid JSON: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CalcError(f"{path}: not UTF-8 text ({exc.reason})") from exc
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
