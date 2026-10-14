"""The frozen Report assets: byte-identical to the template, loaded whole, refusing links."""

from __future__ import annotations

import base64
import hashlib
import os
import re
from pathlib import Path

import pytest

from rbotlib.report import ReportError
from rbotlib.report.assets import load
from rbotlib.report.charts import CHART_IDS, REGISTRY
from rbotlib.rules import RBOT_ROOT

SHIPPED = RBOT_ROOT / "report"
# git blob ids recorded in the Plan 07 pre-flight; the sha256 below pins the same bytes.
FROZEN = {
    "tokens.css": "baf86efa9c04805ebfc1da9dbfc99cfea2876cc2",
    "report.css": "81c23052b9d3c8e84ff58e26e29db3d41100b947",
    "charts.js": "81116c29458486f46cf42bc72e9aaaed8443e525",
}
NAMES = ("tokens.css", "report.css", "charts.js", "report.js", "logo.png")


def blob_id(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw, usedforsecurity=False).hexdigest()


def folder(tmp_path: Path) -> Path:
    root = tmp_path / "report"
    root.mkdir()
    for name in NAMES:
        (root / name).write_bytes(b"x" if name != "logo.png" else b"\x89PNG")
    return root


def test_assets_are_the_frozen_bytes() -> None:
    for name, expected in FROZEN.items():
        assert blob_id((SHIPPED / name).read_bytes()) == expected, name
    assert (SHIPPED / "logo.png").read_bytes() == (
        RBOT_ROOT.parent / "brand/ssim-logo-horizontal-white.png"
    ).read_bytes()


@pytest.mark.parametrize("name", NAMES)
def test_assets_refuse_missing_and_linked(tmp_path: Path, name: str) -> None:
    root = folder(tmp_path)
    (root / name).unlink()
    with pytest.raises(ReportError, match=re.escape(f"{name}: report asset is missing or a link")):
        load(root)
    outside = tmp_path / "elsewhere"
    outside.write_bytes(b"x")
    os.symlink(outside, root / name)
    with pytest.raises(ReportError, match=re.escape(f"{name}: report asset is missing or a link")):
        load(root)


def test_assets_refuse_text_that_is_not_utf8(tmp_path: Path) -> None:
    root = folder(tmp_path)
    (root / "report.css").write_bytes(b"\xff\xfe")
    with pytest.raises(ReportError, match=r"report\.css: report asset is not UTF-8"):
        load(root)


def test_fonts_optional_then_inlined(tmp_path: Path) -> None:
    root = folder(tmp_path)
    loaded = load(root)
    assert loaded.fonts_css == "" and loaded.tokens_css == "x"
    assert loaded.logo_data_uri == "data:image/png;base64," + base64.b64encode(b"\x89PNG").decode()
    (root / "fonts").mkdir()
    (root / "fonts" / "inter-tight-700.woff2").write_bytes(b"wOF2")
    fonts = load(root).fonts_css
    encoded = base64.b64encode(b"wOF2").decode()
    assert 'font-family:"Inter Tight";font-weight:700' in fonts
    assert f'url(data:font/woff2;base64,{encoded}) format("woff2")' in fonts
    (root / "fonts" / "stray.txt").write_bytes(b"x")
    with pytest.raises(ReportError, match=r"fonts/stray.txt: expected <family>-<weight>.woff2"):
        load(root)


def test_the_registry_names_the_ten_charts_and_defers_builders() -> None:
    assert tuple(REGISTRY) == CHART_IDS and len(CHART_IDS) == 10
    with pytest.raises(NotImplementedError, match=r"chart\.rv_hy"):
        REGISTRY["chart.rv_hy"]({})
