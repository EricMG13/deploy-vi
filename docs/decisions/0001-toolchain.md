# 0001 — Toolchain, gates and what they exclude

**Runtime dependencies:** none in Plan 01; RBOT's scripts use the Python standard library only. The PDF library and `openpyxl` get their own records in Plan 02.

**Dev dependencies** (the gate tools ~/.claude/CLAUDE.md section 3 names, plus their runners): `pytest`, `pytest-cov`, `hypothesis` (pre-approved), `mypy`, `ruff`, `bandit`, `pip-audit`, `complexipy`, `pre-commit`, resolved and hashed in `uv.lock`. `jscpd` runs via `npx jscpd@5.2.0` (released 2026-09-08, the newest release older than 30 days on 2026-10-11) so no Node project is added. `mutmut` (pre-approved) arrives with Plan 03, the first money code.

**Python floor:** `requires-python >= 3.11`, ruff `py311`, mypy `3.11`, until the Copilot spike records the work machine's Python; a lower version there changes these three values, never the code style alone.

**Exclusions, all data rather than authored code:**
- `reference/deploy-v-r14/` (read-only Deploy V fork, ADR 0003) is outside ruff, mypy, coverage, bandit, jscpd, the suppression count and the PR-size count; gitleaks scans it in full (it reports no leaks at r14).
- `tests/golden/**/documents/**` (public filings and labelled synthetic test documents, Plan 02) is outside the PR-size count.
- Lock files are outside the PR-size count (the global rule's own exclusion).
- `design/` (design prototypes: report mockups and the script that builds their sample data) is outside ruff, mypy, coverage, bandit, jscpd and the suppression count; the shipping renderer lives under `rbot/` (Plan 07) and is gated. gitleaks scans it in full.

**Bandit floor:** `scripts/check_bandit_floor.py` fails below 40 scanned lines, so a scan that read nothing never passes; raise it as the code grows, never lower it.
