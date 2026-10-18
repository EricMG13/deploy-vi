# 0006 — `design/` outside the PR-size count; design sample data in gitleaks

**Need:** the RBOT Report redesign (PR #100) adds the Claude Design hand-off pack, eight `rbot-run/1` test runs, their generator and the interactive Workbench mock under `design/`: 460,633 changed lines, almost all generated data. It cannot pass the 800-line gate in any split, and none of it ships: the renderer lives under `rbot/` and stays gated.

**Owner decision (2026-10-17):** `design/` is outside the PR-size count, alongside `reference/**` and the test document packs. This amends AGENTS.md's "only existing exclusions apply" for `design/` alone. ADR 0001 already keeps `design/` outside ruff, mypy, coverage, bandit, jscpd and the suppression count.

**gitleaks:** four design data files carry `"key"` and `"formula_keys"` fields (metric identifiers and formula text, no hex or base64 values) that trip `generic-api-key`, the same false positive already exempted for `design/mockups/shared/data.js`. `.gitleaks.toml` exempts that one rule in those four paths; every other rule still scans them, and every other file under `design/` is scanned by every rule.

**Limit:** product code, tests and docs outside `design/` keep the 800-line cap. Code that moves from `design/` into `rbot/` is counted when it moves (as in ADR 0005).
