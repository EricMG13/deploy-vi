# Transfer install.sh, install.ps1 and the exported rbot/ together. Python >=3.11.
# Usage: .\install.ps1 [-Source EXPORTED_RBOT] [-Destination DESTINATION] [-Python PYTHON]
# Default: package beside this script -> ~/.copilot/skills/rbot. No package setup.
# An identical destination is a no-op; any other existing destination refuses.
param(
    [string]$Source = (Join-Path $PSScriptRoot 'rbot'),
    [string]$Destination = (Join-Path $HOME '.copilot/skills/rbot'),
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$installer = @'
import hashlib
import json
import os
import re
import runpy
import shutil
import stat
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Pin the qualified, trusted verifier before loading it; this is content binding,
# not signing. A new entry requires a newly qualified installer. Python is trusted.
ENTRY_SHA256 = "9a6c7757b2f6c40a308c0ee701cd3dcf340d3ce5abac85196610367e2753726b"


def safe_path(value: str) -> Path:
    if not value:
        raise ValueError("empty path")
    path = Path(value).expanduser().absolute()
    if ".." in path.parts:
        raise ValueError("unsafe parent traversal")
    for ancestor in (path, *path.parents):
        attributes = (
            getattr(ancestor.lstat(), "st_file_attributes", 0)
            if ancestor.exists() or ancestor.is_symlink()
            else 0
        )
        if ancestor.is_symlink() or attributes & 0x400:
            raise ValueError("unsafe linked path: " + str(ancestor))
    return path


def regular_tree(root: Path) -> None:
    if not stat.S_ISDIR(root.lstat().st_mode):
        raise ValueError("runtime must be a real directory")
    for folder, directories, names in os.walk(root, followlinks=False):
        for name in directories + names:
            path = Path(folder) / name
            info = path.lstat()
            mode = info.st_mode
            if getattr(info, "st_file_attributes", 0) & 0x400 or not (
                stat.S_ISDIR(mode) or stat.S_ISREG(mode)
            ):
                raise ValueError("unsafe runtime path: " + str(path))


def runtime_only(contents: dict[str, bytes]) -> None:
    required = {
        "SKILL.md",
        "canon.md",
        "catalog.json",
        "rules.json",
        "scripts/rbot.py",
        "scripts/rbotlib/cli.py",
    }
    modules = {
        step
        for pathway in json.loads(contents["catalog.json"])["pathways"]
        for steps in pathway["depths"].values()
        for step in steps
        if step.startswith("CP-")
    }
    required.update(
        f"modules/{module}/{name}" for module in modules for name in ("MODULE.md", "contract.json")
    )
    if not modules or not required.issubset(contents):
        raise ValueError("incomplete runtime skill/contracts")
    if any(
        not (
            (name.startswith("scripts/rbotlib/") and name.endswith(".py"))
            or re.fullmatch(r"report/(fonts/)?[A-Za-z0-9._-]+\.(css|js|png|woff2)", name)
            and (name.endswith(".woff2") == name.startswith("report/fonts/"))
        )
        for name in set(contents) - required
    ):
        raise ValueError("nonruntime content in export")


def install() -> None:
    minimum_python = (3, 11)
    if sys.version_info[:2] < minimum_python:
        raise ValueError("Python 3.11 or later required")
    source, destination = map(safe_path, sys.argv[1:])
    if source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("source and destination overlap")
    regular_tree(source)
    entry = source / "scripts/rbot.py"
    if entry.stat().st_size > 2_000_000:
        raise ValueError("oversized entry")
    if hashlib.sha256(entry.read_bytes()).hexdigest() != ENTRY_SHA256:
        raise ValueError("unqualified runtime entry")
    verify = runpy.run_path(str(entry))["verify"]
    data, contents = verify(source)
    runtime_only(contents)
    contents["runtime.json"] = (source / "runtime.json").read_bytes()
    if destination.exists():
        regular_tree(destination)
        _, existing = verify(destination)
        existing["runtime.json"] = (destination / "runtime.json").read_bytes()
        if existing != contents:
            raise ValueError("destination differs; choose a fresh destination")
        print("Already installed: " + str(destination))
        return
    publish(contents, data, destination, verify)


def publish(
    contents: dict[str, bytes],
    data: dict[str, Any],
    destination: Path,
    verify: Callable[[Path], tuple[dict[str, Any], dict[str, bytes]]],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.parent / ("." + destination.name + "-install.lock")
    lock.mkdir()  # Never remove a lock belonging to another installer.
    stage: Path | None = None
    try:
        stage = Path(tempfile.mkdtemp(prefix=".rbot-install-", dir=destination.parent))
        for name, raw in contents.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            mode = data["files"].get(name, {}).get("mode", "100644")
            target.chmod(0o755 if mode == "100755" else 0o644)
        verify(stage)  # Refuse incomplete/corrupt staging before publication.
        if destination.exists() or destination.is_symlink():
            raise ValueError("destination appeared during installation")
        stage.rename(destination)
        stage = None
        print("Installed: " + str(destination))
    finally:
        if stage is not None:
            shutil.rmtree(stage)
        lock.rmdir()


try:
    install()
except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as error:
    print("error: install: " + str(error), file=sys.stderr)
    sys.exit(1)
'@
$installer | & $Python -I - $Source $Destination
exit $LASTEXITCODE
