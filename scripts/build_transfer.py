"""Build the work-PC transfer zip: runtime, installers, probe, pack, wheels, checklist, manifest.

Build-time only (stdlib). Every part comes from the release-candidate commit, the
registered corpus pack or uv.lock-pinned wheels; any hash mismatch refuses the build.
Run through build_transfer.sh, which exports the commit's inputs (git/shell stay there).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import tomllib
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rbot" / "scripts"))

from proxy_run import _verify_copy
from rbotlib.corpus import load_registry, materialise, resolve_roots

PACK = "czr-2026q2-primary"
PYTHON_PACKAGES = ("openpyxl", "pypdf")  # the runtime's pinned dependencies (pyproject.toml)
CHECKLIST_DOC = "docs/acceptance/work-pc-checklist.md"
FENCE = "```checklist.txt\n"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


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


def _files(root: Path, prefix: str) -> dict[str, tuple[bytes, bool]]:
    return {
        f"{prefix}{p.relative_to(root).as_posix()}": (
            p.read_bytes(),
            bool(p.stat().st_mode & 0o100),
        )
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _collect(args: argparse.Namespace, scratch: Path) -> tuple[dict[str, tuple[bytes, bool]], str]:
    """Every package file (bytes, executable) and the runtime tree id."""
    stage: Path = args.stage
    lock = args.lock.read_text() if args.lock else (stage / "uv.lock").read_text()
    wheel_files = _wheels(lock, args.wheels)
    registry = load_registry(stage / "tests/corpus/corpus.json")
    entry = registry.pack(PACK)
    pack = scratch / PACK
    materialise(registry, entry, resolve_roots(registry), pack)
    _verify_copy(entry, pack)
    doc = (stage / CHECKLIST_DOC).read_bytes()
    files = {
        "CHECKLIST.md": (doc, False),
        "evidence/checklist.txt": (_blank_checklist(doc.decode()).encode(), False),
        **_files(args.runtime, "rbot/"),
        **_files(pack, f"pack/{PACK}/"),
        **{f"wheels/{n}": (d, False) for n, d in wheel_files.items()},
    }
    files.update({n: v for n, v in _files(stage, "").items() if n in ("install.sh", "install.ps1")})
    files.update(_files(stage / "spike", "spike/"))
    tree = str(json.loads((args.runtime / "runtime.json").read_text())["runtime_tree"])
    return files, tree


def build(args: argparse.Namespace) -> tuple[Path, str]:
    repo, out = args.repo.resolve(strict=True), args.out.absolute()
    if out.exists() or out.is_symlink() or out.parent.resolve(strict=True).is_relative_to(repo):
        raise ValueError("build transfer: output must be a fresh directory outside the repository")
    with tempfile.TemporaryDirectory(prefix="rbot-transfer.") as scratch:
        files, tree = _collect(args, Path(scratch))
        hashes = {n: hashlib.sha256(d).hexdigest() for n, (d, _) in sorted(files.items())}
        manifest = {"commit": args.commit, "runtime_tree": tree, "files": hashes}
        files["MANIFEST.json"] = ((json.dumps(manifest, indent=2) + "\n").encode(), False)
        out.mkdir()
        archive = out / f"rbot-v1-{args.commit[:12]}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, (data, executable) in sorted(files.items()):
                info = zipfile.ZipInfo(name, ZIP_TIME)
                info.external_attr = (0o755 if executable else 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, data)
    return archive, hashlib.sha256(archive.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("commit", "repo", "out", "stage", "runtime"):
        parser.add_argument(f"--{name}", required=True, type=str if name == "commit" else Path)
    parser.add_argument("--wheels", type=Path, help="local wheel folder instead of downloading")
    parser.add_argument("--lock", type=Path, help="uv.lock override (default: the commit's)")
    try:
        archive, digest = build(parser.parse_args(argv))
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{archive}\nsha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
