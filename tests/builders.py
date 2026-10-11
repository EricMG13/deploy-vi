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


def make_run(pack: Path, name: str = "20261011-test-pending") -> Path:
    """An empty run folder at <pack>/rbot-runs/<name>/ (spec section 8.1)."""
    run = pack / "rbot-runs" / name
    run.mkdir(parents=True)
    return run
