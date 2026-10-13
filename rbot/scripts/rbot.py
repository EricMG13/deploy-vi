"""RBOT command line. Run as `python <RBOT>/scripts/rbot.py <command>`."""

import sys

# The entry directory contains RBOT, not replacements for standard dependencies.
sys.path.pop(0)

from collections.abc import Sequence
from importlib.abc import MetaPathFinder
from importlib.machinery import SOURCE_SUFFIXES, FileFinder, ModuleSpec, SourceFileLoader
from pathlib import Path
from types import CodeType, ModuleType

SCRIPTS = Path(__file__).resolve().parent


class _SourceOnly(SourceFileLoader):
    def get_code(self, fullname: str) -> CodeType:
        """Identity describes RBOT source bytes; never execute its unverified caches."""
        return self.source_to_code(self.get_data(self.path), self.path)


class _RuntimeFinder(MetaPathFinder):
    def find_spec(
        self, fullname: str, path: Sequence[str] | None, target: ModuleType | None = None
    ) -> ModuleSpec | None:
        if fullname != "rbotlib" and not fullname.startswith("rbotlib."):
            return None
        folder = str(SCRIPTS) if path is None else path[0]
        spec = FileFinder(folder, (_SourceOnly, SOURCE_SUFFIXES)).find_spec(fullname)
        if spec is None:
            raise ImportError(f"runtime source unavailable: {fullname}")
        return spec


if __name__ == "__main__":
    sys.meta_path.insert(0, _RuntimeFinder())
    from rbotlib.cli import main

    sys.exit(main())
