# 0005 — Report assets

**Need:** the Report is one self-contained `report.html` in the owner-picked Report A template (Plan 07). Its CSS and chart kit are frozen files; the renderer must ship them, install them, and never fetch anything when the Report is viewed.

**Order of preference (global rule):** stdlib, then an already-pinned dependency, then new code. No dependency is added: assets are plain files read with `pathlib` and inlined with `base64`.

**Choice:**
- `tokens.css`, `report-a.css` (as `report.css`) and `charts.js` move with `git mv` from `design/mockups/` to `rbot/report/`. A rename is 0 lines in `git diff --numstat`; copying 2,370 lines could not pass the 800-line gate (`charts.js` alone is 1,323), and AGENTS.md forbids new cap exemptions. The four mockup HTMLs keep working through updated relative links. `tests/test_report_assets.py` pins the git blob ids of the three files.
- `report-a.js` is a CZR-specific page script and is not shipped; a generic `report.js` is added by Task 07.7.
- The logo is a copy of `brand/ssim-logo-horizontal-white.png` (17 KB) inlined as a data URI.
- Fonts: no Inter or Inter Tight files exist in the repository and the renderer does not fetch, so v1 uses the `system-ui` fallbacks in the CSS stacks. When `rbot/report/fonts/<family>-<weight>.woff2` files exist (owner-supplied, OFL; `inter-400.woff2`, `inter-tight-700.woff2`), `assets.load` inlines each as a base64 `@font-face`.
- Install and runtime export accept `report/<name>.{css,js,png}` and `report/fonts/<name>.woff2` and nothing else under `report/`; `rbot/runtime.json` hashes them with the rest of the tree.

**Failure handling:** a missing, linked or non-UTF-8 asset raises `ReportError` naming the file; a stray file in `fonts/` is refused rather than skipped.
