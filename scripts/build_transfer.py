"""Build the work-PC transfer zip: runtime, installers, probe, pack, wheels, checklist, manifest.

Build-time only (stdlib). Every part comes from the release-candidate commit, the
registered corpus pack or uv.lock-pinned wheels; any hash mismatch refuses the build.
Usage: build_transfer.py --commit RC --out FRESH_DIR [--wheels DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
import urllib.request
import zipfile
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

from proxy_run import _verify_copy
from rbotlib.corpus import REGISTRY, load_registry, materialise, resolve_roots

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

PACK = "czr-2026q2-primary"
PYTHON_PACKAGES = ("openpyxl", "pypdf")  # the runtime's pinned dependencies (pyproject.toml)
CHECKLIST_DOC = "docs/acceptance/work-pc-checklist.md"
SPIKE = ("spike/rbot-probe", "spike/probe-workspace")
FENCE = "```checklist.txt\n"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=120
    ).stdout


def _committed(repo: Path, commit: str, *paths: str) -> dict[str, tuple[bytes, bool]]:
    """Blob bytes and executable bit of every file at/below `paths` in the commit."""
    listing = _git(repo, "ls-tree", "-rz", commit, "--", *paths)
    files = {}
    for entry in filter(None, listing.split(b"\0")):
        header, name = entry.split(b"\t", 1)
        mode, _, blob = header.decode().split()
        files[name.decode()] = (_git(repo, "cat-file", "blob", blob), mode == "100755")
    missing = [p for p in paths if not any(n == p or n.startswith(p + "/") for n in files)]
    if missing:
        raise ValueError(f"build transfer: not committed at {commit[:12]}: {', '.join(missing)}")
    return files


def _wheel_plan(lock_text: str) -> dict[str, tuple[str, str]]:
    """Pure-Python wheels (filename -> (url, sha256)) for the pinned packages and their closure."""
    packages = {p["name"]: p for p in tomllib.loads(lock_text).get("package", [])}
    plan: dict[str, tuple[str, str]] = {}
    pending, seen = list(PYTHON_PACKAGES), set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        if name not in packages:
            raise ValueError(f"build transfer: uv.lock has no package {name}")
        pending += [d["name"] for d in packages[name].get("dependencies", [])]
        wheels = [w for w in packages[name].get("wheels", []) if w["url"].endswith("-none-any.whl")]
        if not wheels:
            raise ValueError(f"build transfer: uv.lock has no pure-Python wheel for {name}")
        for wheel in wheels:
            digest = wheel["hash"].removeprefix("sha256:")
            plan[Path(urlsplit(wheel["url"]).path).name] = (wheel["url"], digest)
    return plan


def _fetch(url: str) -> bytes:
    if urlsplit(url).scheme != "https":
        raise ValueError(f"build transfer: wheel URL is not https: {url}")
    with urllib.request.build_opener().open(url, timeout=120) as response:
        data: bytes = response.read()
    return data


def _wheels(lock_text: str, local: Path | None) -> dict[str, bytes]:
    found = {}
    for name, (url, digest) in sorted(_wheel_plan(lock_text).items()):
        if local is None:
            data = _fetch(url)
        elif (local / name).is_file():
            data = (local / name).read_bytes()
        else:
            raise ValueError(f"build transfer: wheel {name} is not in {local}")
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"build transfer: wheel {name} does not match uv.lock sha256")
        found[name] = data
    return found


def _blank_checklist(doc: str) -> str:
    _, fence, rest = doc.partition(FENCE)
    block, close, _ = rest.partition("\n```")
    if not (fence and close and block.strip()):
        raise ValueError(f"build transfer: {CHECKLIST_DOC} has no ```checklist.txt block")
    return block + "\n"


def _runtime(repo: Path, commit: str, dest: Path) -> str:
    script = HERE / "build_runtime.sh"
    done = subprocess.run(
        ["bash", str(script), sys.executable, str(repo), commit, str(dest)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if done.returncode:
        raise ValueError(f"build transfer: runtime build failed: {done.stderr.strip()}")
    return str(json.loads((dest / "runtime.json").read_text())["runtime_tree"])


class Sources(NamedTuple):
    """Optional overrides: lock text (default the commit's), local wheel folder, corpus registry."""

    lock_text: str | None = None
    wheels: Path | None = None
    registry: Path = REGISTRY


def _collect(
    repo: Path, commit: str, work: Path, sources: Sources
) -> tuple[dict[str, tuple[bytes, bool]], str]:
    """Every package file (bytes, executable) and the runtime tree id."""
    lock = sources.lock_text
    if lock is None:
        lock = _git(repo, "show", f"{commit}:uv.lock").decode()
    wheel_files = _wheels(lock, sources.wheels)
    runtime = work / "rbot"
    tree = _runtime(repo, commit, runtime)
    pack_entry_registry = load_registry(sources.registry)
    entry = pack_entry_registry.pack(PACK)
    pack = work / "pack" / PACK
    materialise(pack_entry_registry, entry, resolve_roots(pack_entry_registry), pack)
    _verify_copy(entry, pack)
    committed = _committed(repo, commit, "install.sh", "install.ps1", CHECKLIST_DOC, *SPIKE)
    doc = committed[CHECKLIST_DOC][0]
    files: dict[str, tuple[bytes, bool]] = {
        "CHECKLIST.md": (doc, False),
        "evidence/checklist.txt": (_blank_checklist(doc.decode()).encode(), False),
    }
    files.update({n: v for n, v in committed.items() if n != CHECKLIST_DOC})
    for root, prefix in ((runtime, "rbot"), (pack.parent, "pack")):
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            files[f"{prefix}/{path.relative_to(root).as_posix()}"] = (
                path.read_bytes(),
                bool(path.stat().st_mode & 0o100),
            )
    files.update({f"wheels/{n}": (d, False) for n, d in wheel_files.items()})
    return files, tree


def build(repo: Path, commit: str, out: Path, sources: Sources | None = None) -> tuple[Path, str]:
    repo, out = repo.resolve(strict=True), out.absolute()
    sources = sources or Sources()
    if out.exists() or out.is_symlink() or out.parent.resolve(strict=True).is_relative_to(repo):
        raise ValueError("build transfer: output must be a fresh directory outside the repository")
    try:
        sha = _git(repo, "rev-parse", "--verify", "--end-of-options", f"{commit}^{{commit}}")
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"build transfer: unknown commit {commit}") from exc
    sha_text = sha.decode().strip()
    with tempfile.TemporaryDirectory(prefix="rbot-transfer.") as scratch:
        files, tree = _collect(repo, sha_text, Path(scratch), sources)
        hashes = {n: hashlib.sha256(d).hexdigest() for n, (d, _) in sorted(files.items())}
        manifest = {"commit": sha_text, "runtime_tree": tree, "files": hashes}
        files["MANIFEST.json"] = ((json.dumps(manifest, indent=2) + "\n").encode(), False)
        out.mkdir()
        archive = out / f"rbot-v1-{sha_text[:12]}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, (data, executable) in sorted(files.items()):
                info = zipfile.ZipInfo(name, ZIP_TIME)
                info.external_attr = (0o755 if executable else 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, data)
    return archive, hashlib.sha256(archive.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wheels", type=Path, help="local wheel folder instead of downloading")
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--lock", type=Path, help="uv.lock override (default: the commit's)")
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    args = parser.parse_args(argv)
    try:
        lock = args.lock.read_text() if args.lock else None
        sources = Sources(lock, args.wheels, args.registry)
        archive, digest = build(args.repo, args.commit, args.out, sources)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{archive}\nsha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
