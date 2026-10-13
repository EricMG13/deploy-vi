"""Builders for test inputs: tiny real PDFs and run folders inside a Source Pack."""

from __future__ import annotations

from pathlib import Path

FONT = "<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>"


def make_pdf(pages: list[str]) -> bytes:
    """A minimal valid PDF with one Helvetica text line per page ('' = a page without text)."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", ""]
    kids = []
    for text in pages:
        content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET" if text else ""
        objects.append(f"<< /Length {len(content)} >>\nstream\n{content}\nendstream")
        objects.append(
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
            f" /Contents {len(objects)} 0 R /Resources {FONT} >>"
        )
        kids.append(f"{len(objects)} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    out, offsets = b"%PDF-1.4\n", []
    for n, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out + trailer.encode()


def make_run(pack: Path, name: str = "20261011-test-pending", *, managed: bool = False) -> Path:
    """An empty run folder at <pack>/rbot-runs/<name>/ (spec section 8.1)."""
    run = pack / "rbot-runs" / name
    if managed:
        import json

        from rbotlib import runs, state

        allocated = runs.create_run(pack)
        record = state.read(allocated)
        allocated.rename(run)
        record["run_id"] = run.name
        (run / state.STATE).write_text(json.dumps(record))
        state.read(run)
        return run
    run.mkdir(parents=True)
    return run


def prepared_pack(
    root: Path,
    files: dict[str, str | bytes],
    name: str = "20261011-acme-pending",
    *,
    managed: bool = False,
) -> Path:
    """A Source Pack of `files` under `root/pack`, and a run with inventory and prepare done."""
    from rbotlib.cli import main

    pack = root / "pack"
    pack.mkdir()
    for path, content in files.items():
        target = pack / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")
    run = make_run(pack, name, managed=managed)
    for command in ("inventory", "prepare"):
        if main([command, "--run", str(run)]) != 0:
            raise RuntimeError(f"rbot {command} failed for {run}")
    return run
