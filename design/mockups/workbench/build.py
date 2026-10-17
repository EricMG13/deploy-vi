#!/usr/bin/env python3
"""Build dist/rbot-workbench.html: one self-contained file (stdlib only).

Order is fixed and documented in README.md:
  CSS: tokens.css, base.css, components.css, charts.css, views.css, frontpages.css, then any other src/*.css alphabetically.
  JS:  core.js, render.js, pages.js, charts.js, views.js, frontpages.js, then any other src/*.js alphabetically, shell.js last.
Embedded: the eight runs as <script type="application/json" class="rbot-run" data-run="<stem>">, the module metadata
as <script type="application/json" id="rbot-modules">, and the logo as a base64 data URI in a CSS variable.
"""
import base64
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = HERE / "src"
DIST = HERE / "dist"
RUNS = ROOT / "design" / "claude-design-handoff" / "data" / "test"
FP_DATA = ROOT / "design" / "claude-design-handoff" / "data" / "front-pages-data.json"
LOGO = ROOT / "brand" / "ssim-logo-horizontal-white.png"
LIMIT = 16 * 1024 * 1024

CSS_FIRST = ["tokens.css", "base.css", "components.css", "charts.css", "views.css", "frontpages.css"]
JS_FIRST = ["core.js", "render.js", "pages.js", "charts.js", "views.js", "frontpages.js"]
JS_LAST = ["shell.js"]
FONTS = (
    "https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@500;600;700"
    "&family=Red+Hat+Text:wght@400;500;600;700&family=Red+Hat+Mono:wght@400;500;600&display=swap"
)


def ordered(pattern, first, last=()):
    found = {p.name: p for p in SRC.glob(pattern)}
    names = [n for n in first if n in found]
    rest = sorted(n for n in found if n not in first and n not in last)
    names += rest + [n for n in last if n in found]
    return [found[n] for n in names]


def safe_script_text(text, label):
    if "</script" in text.lower():
        sys.exit(f"build: {label} contains </script; refusing to inline it")
    return text


def json_for_script(obj):
    # compact JSON; "</" is escaped so the data can never close the script element
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")


def main():
    missing = [p for p in (RUNS, FP_DATA, LOGO) if not p.exists()]
    if missing:
        sys.exit("build: missing input " + ", ".join(str(m) for m in missing))
    css_files = ordered("*.css", CSS_FIRST)
    js_files = ordered("*.js", JS_FIRST, JS_LAST)
    if not css_files or not js_files:
        sys.exit("build: no src files")

    runs = sorted(RUNS.glob("*.run.json"))
    if len(runs) != 8:
        sys.exit(f"build: expected 8 runs in {RUNS}, found {len(runs)}")
    modules_src = json.loads(FP_DATA.read_text(encoding="utf-8"))["modules"]
    modules = {k: {"id": k, "name": v["name"], "question": v["question"]} for k, v in modules_src.items()}
    logo_uri = "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>RBOT Workbench</title>",
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link rel="stylesheet" href="{FONTS}">',
        f'<style id="wb-logo">:root{{--logo-url:url("{logo_uri}")}}</style>',
    ]
    for p in css_files:
        parts.append(f'<style data-src="{p.name}">\n{p.read_text(encoding="utf-8")}\n</style>')
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<noscript>The RBOT Workbench needs JavaScript. It renders the embedded run data in the browser.</noscript>')
    for p in runs:
        stem = p.name[: -len(".run.json")]
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("schema") != "rbot-run/1":
            sys.exit(f"build: {p.name} is not rbot-run/1")
        parts.append(f'<script type="application/json" class="rbot-run" data-run="{stem}">{json_for_script(data)}</script>')
    parts.append(f'<script type="application/json" id="rbot-modules">{json_for_script(modules)}</script>')
    for p in js_files:
        text = safe_script_text(p.read_text(encoding="utf-8"), p.name)
        parts.append(f'<script data-src="{p.name}">\n{text}\n</script>')
    parts.append("</body>")
    parts.append("</html>")

    html = "\n".join(parts) + "\n"
    DIST.mkdir(exist_ok=True)
    out = DIST / "rbot-workbench.html"
    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size
    print(f"css: {', '.join(p.name for p in css_files)}")
    print(f"js:  {', '.join(p.name for p in js_files)}")
    print(f"runs: {len(runs)}  modules: {len(modules)}")
    print(f"wrote {out.relative_to(ROOT)}  {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
    if size > LIMIT:
        sys.exit(f"build: {size:,} bytes exceeds the 16 MB limit")


if __name__ == "__main__":
    main()
