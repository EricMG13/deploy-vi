# 0007 — pytest-xdist for parallel test runs

**Need:** the full suite takes about 2.5 h serial (report tests about 1 h 27 m, `tests/model` hypothesis about 30 min), which slows every local gate run.

**Order of preference (global rule):** the standard library has no parallel pytest runner. `concurrent.futures` around chunked pytest invocations (the ad-hoc chunked runner) cannot combine coverage into one `--cov-fail-under` total and hides cross-file order defects. No locked dependency does it. So a new dev dependency.

**Choice:** `pytest-xdist` — MIT, maintained by pytest-dev (the org behind pytest and pytest-cov). Alternatives rejected: `pytest-parallel` (unmaintained) and `pytest-run-parallel` (thread-based, not process isolation).

**Version:** `pytest-xdist>=3.8.0`, locked at 3.8.0 (released 2025-07-01, older than 30 days, newest release). Transitive: `execnet` 2.1.2 (released 2025-11-12, no dependencies of its own). `pip-audit --strict` passes.

**Use:** `uv run pytest -n auto` is an accelerator on the owner's machine. `addopts` has no `-n`, so `pytest tests/x.py` and mutmut stay serial. The gate command in CI stays `uv run pytest`. pytest-cov combines worker coverage; `--cov-fail-under` applies to the combined total.

**Limit:** each worker is a separate process, so the session fixtures `corpus_pack` and `prepared_run` run once per worker (materialise, `rbot inventory`, `rbot prepare` repeated per pack a worker touches). The shared pack trees are guarded by a digest check at teardown (`tests/conftest.py`): a test that writes into them fails loudly instead of flaking by worker grouping. Report tests launch headless Chrome; concurrent workers each start a browser, so memory and CPU rise with `-n`.

**Measured** (10-core Mac, `RBOT_REQUIRE_CORPUS=1 uv run pytest -n auto`, 10 workers): serial chunked run at db2d91b, 4198 passed, coverage 95 %, about 2.5 h. Parallel on the pre-Plan-10 tree: 4003 passed in 41 m 04 s (a first run, 34 m 39 s, had 20 two-to-three-second subprocess timeouts and one `build_runtime.sh` SIGPIPE race, fixed by `HANG_TIMEOUT = 30` and archiving to a file). Final, merged onto main bd717eb: 4207 passed, 1 skipped (`test_smoke_transfer`, needs a built package), coverage 94.96 % (floor 80 %), 43 m 19 s, about 3.5x faster. Run times vary 35-43 m with machine load; the floor applies to the combined total.
