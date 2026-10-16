# Plan 09 corpus regression — 2026-10-16

Task 09.8, records only. Nothing was pushed.

## Branch stack

- Base `ffc7e06` = build/v1 `d1774df` + plan docs.
- build/09.1-module-gates `0d9a06d`
- build/09.2-cp-l10 `60e33b8`
- build/09.3-validator `1377d50`
- build/09.4-cp6-screening `d625f02`
- build/09.5-quick-catalog `6479fcf`
- build/09.6-topic-chart `1f7904e`
- build/09.7-quick-record `7ffc4f4` (RC rbot tree `d7c0542`; merge `91585ac` of 09.6)
- build/09.8-records (this commit)

## Gates

| Gate | Result |
|---|---|
| `ruff check .`, `ruff format --check .`, `mypy`, `rbot.py check`, `complexipy` (15), `check_suppressions.py` | exit 0 on every task branch (controller re-runs) |
| `uv lock --check` | exit 0 |
| bandit + `check_bandit_floor.py` | exit 0 |
| `pip-audit --strict` | exit 0; no known vulnerabilities |
| `jscpd@5.2.0 --threshold 3 --min-lines 10` | exit 0; 19 clones, under the threshold |
| `corpus verify` | exit 0 |
| `RBOT_REQUIRE_CORPUS=1 pytest -m corpus` (at 09.3) | exit 0; 243 passed |
| full suite `RBOT_REQUIRE_CORPUS=1 pytest` at 91585ac | exit 0; 3988 passed, 1 skipped, 0 failed (counted from the progress output); coverage 94.84% (floor 80); 1 h 54 m 48 s |
| PR size per branch | 09.1 166, 09.2 618, 09.3 253, 09.4 337, 09.5 108, 09.6 312, 09.7 368, 09.8 253 (all ≤ 800) |

## Record run

Pre-RC run 1 at `440819b` found D1 (CP-3 wrote Blocked with two TRACE levels; fixed by validator `blocked_gate`, `d7c0542`). Final run at `d7c0542`: R1 10/10, R2 PASS, R3 FAIL (skipped: FIT), R4 8 measured 0 failing, R5 76/79, R6 12 unchanged, R7 10 limitations, R8 PASS. Owner decision 2026-10-16: a step switched off by approval counts as satisfied for R3; acceptance.py re-check on the same run: R1–R8 PASS, exit 0.

## Known flake

Headless Chrome "Teardown watchdog expired" under machine load (load average up to ~138). Tests retry once on that exact signature (`1f7904e`).

Not verified: live Copilot runs; the owner's R3 decision; ccl-fy2025-lite-full-credit-screen record run (graded only, Plan 19); a quick run with a portfolio.
