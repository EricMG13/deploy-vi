"""The frozen Report assets shipped under `rbot/report/`, read once and inlined by the renderer."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from pathlib import Path

from rbotlib.report import ReportError

FONT_FILE = re.compile(r"(?P<family>[a-z][a-z-]*)-(?P<weight>[1-9]00)\.woff2")


@dataclass(frozen=True)
class Assets:
    tokens_css: str
    report_css: str
    charts_js: str
    report_js: str
    logo_data_uri: str
    fonts_css: str


def _read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ReportError(f"{path.name}: report asset is missing or a link")
    return path.read_bytes()


def _text(path: Path) -> str:
    try:
        return _read(path).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReportError(f"{path.name}: report asset is not UTF-8") from exc


def _data_uri(media: str, raw: bytes) -> str:
    return f"data:{media};base64,{base64.b64encode(raw).decode('ascii')}"


def _fonts(folder: Path) -> str:
    """`<family>-<weight>.woff2` becomes one `@font-face`; `inter-tight` is "Inter Tight"."""
    if folder.is_symlink():
        raise ReportError("fonts: report asset is a link")
    if not folder.is_dir():
        return ""
    faces = []
    for path in sorted(folder.iterdir()):
        found = FONT_FILE.fullmatch(path.name)
        if found is None:
            raise ReportError(f"fonts/{path.name}: expected <family>-<weight>.woff2")
        family = found["family"].replace("-", " ").title()
        faces.append(
            f'@font-face{{font-family:"{family}";font-weight:{found["weight"]};'
            f"font-style:normal;font-display:swap;"
            f'src:url({_data_uri("font/woff2", _read(path))}) format("woff2")}}'
        )
    return "\n".join(faces)


def load(root: Path) -> Assets:
    """Read the assets under `root` (the `rbot/report` folder); refuse a missing or linked file."""
    return Assets(
        tokens_css=_text(root / "tokens.css"),
        report_css=_text(root / "report.css"),
        charts_js=_text(root / "charts.js"),
        report_js=_text(root / "report.js"),
        logo_data_uri=_data_uri("image/png", _read(root / "logo.png")),
        fonts_css=_fonts(root / "fonts"),
    )
