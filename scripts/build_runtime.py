"""Stamp a Git-exported staging tree; build_runtime.sh captures immutable Git objects.

Build-time only. Committed source bytes are verified before a fresh external output
is created. The installed runtime never imports this repository helper.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path


def git_hash(kind: str, raw: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(raw)}\0".encode() + raw, usedforsecurity=False).hexdigest()


def _version(stage: Path) -> str:
    init = ast.parse((stage / "rbot/scripts/rbotlib/__init__.py").read_bytes())
    versions = [
        ast.literal_eval(node.value)
        for node in init.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets)
    ]
    if len(versions) != 1 or not isinstance(versions[0], str):
        raise ValueError("build runtime: missing/conflicting version")
    return versions[0]


def build(repo: Path, stage: Path, output: Path) -> None:
    repo, stage = repo.resolve(strict=True), stage.resolve(strict=True)
    output = output.absolute()
    if (
        output.exists()
        or output.is_symlink()
        or output.parent.resolve(strict=True).is_relative_to(repo)
    ):
        raise ValueError("build runtime: output must be a fresh directory outside the repository")
    sha, source_tree, runtime_tree = (stage / "identity").read_text().splitlines()
    commit, root = (stage / "commit").read_bytes(), (stage / "root").read_bytes()
    if git_hash("commit", commit) != sha or git_hash("tree", root) != source_tree:
        raise ValueError("build runtime: captured Git object differs")
    manifest = {}
    for entry in filter(None, (stage / "entries").read_bytes().split(b"\0")):
        header, raw_name = entry.split(b"\t", 1)
        mode, kind, blob = header.decode().split()
        name = raw_name.decode()
        if (
            kind != "blob"
            or mode not in ("100644", "100755")
            or any(part in ("", ".", "..", "__pycache__") for part in name.split("/"))
            or "\\" in name
            or name == "runtime.json"
        ):
            raise ValueError(f"build runtime: unsupported committed path {name}")
        path = stage / "rbot" / name
        if path.is_symlink() or git_hash("blob", path.read_bytes()) != blob:
            raise ValueError(f"build runtime: staged source bytes differ: {name}")
        manifest[name] = {"mode": mode, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    data = dict(
        schema="rbot-runtime/1",
        version=_version(stage),
        git_sha=sha,
        source_tree=source_tree,
        runtime_tree=runtime_tree,
        commit_object=commit.hex(),
        root_object=root.hex(),
        files=manifest,
    )
    output.mkdir()
    for name in manifest:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stage / "rbot" / name, target)
        target.chmod(0o755 if manifest[name]["mode"] == "100755" else 0o644)
    (output / "runtime.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "stage", "out"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    try:
        build(args.repo, args.stage, args.out)
    except (OSError, ValueError, KeyError, SyntaxError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
