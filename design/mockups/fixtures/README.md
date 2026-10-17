# Fixture generator: API for content modules

Contract: `FIXTURES.md`. Spec read from `inputs/` (never retyped). Standard library only. Run from this folder:

```bash
python3 build-fixtures.py --only czr-full-credit-assessment --check   # incomplete runs are listed, never stubbed
python3 -m unittest discover -s . -p 'test_*.py' && uvx ruff check . && uvx ruff format --check .
```

## A content module

`czr/cp_1.py` (any step: `czr/cp_2a.py`, `czr/cp_l10.py`, `larchmere/cp_4c.py`) exposes `build(ctx, run_id, variant) -> Handoff`.
`czr/run_brief.py` exposes `build(ctx, run_id, variant, pathway=..., depth=...)`. `variant` is the string set in `build-fixtures.py` `RUNS`.
Earlier steps are read with `ctx.get(run_id, "CP-1")` (plan order); the Model is `ctx.models[run_id]`, Fit results `ctx.fits[run_id]`.
`MODEL`, `PROJECTION` and `FIT` are never written by hand: the Run builds them. A projection is requested by
`h.meta["projection"] = [("BASE", [2026, 2027, 2028], drivers), ("DOWNSIDE", ...)]` on the CP-2G handoff (driver keys in `ModelBuilder.add_projection`).
A run's Primary flag (`primary=True` in `RUNS`) is set on the context by the Run (`ctx.primary_runs[run_id]`); modules read it with `czr.cp_3.is_primary(ctx, run_id)`, never from the variant name. Pro forma rows (new tranches) go in CP-1's `cp1.pro_forma_adjustment_register` (`pro_forma_rows` hook) plus a facility row per tranche at the LTM period.

```python
from lib import Handoff, compute, fx, plain, join_marks

h = Handoff(ctx, "CP-1", "CZR", run_id, "2026-10-02", ["CP-0"]).qa("Restricted")
m = h.cite_data("C51")                                    # real base/Front Pages citation -> "[C1]" (verified in the corpus)
m2 = h.cite_doc_find("CZR_FY2025_10K.txt", "Operating income | 1,858")   # a corpus line; cite_doc(file, line, excerpt) is strict
m3 = h.cite_caos("full-credit-assessment-2026-10-06", "CP-1", 4)         # a real CAOS citation
s = h.cite_synthetic("tranche-1", "One sentence: why this invented value is plausible.", "Caesars")
lev, calc = compute("total leverage", "debt / ebitda", 2, "x", debt=11807, ebitda=3592)   # Decimal 3.29, "calc: … = 11807 / 3592 = 3.29x"
h.table("cp1.reconciliation_checks", [{"check_id": "x", "cite": f"{m} {calc}", ...}])   # dicts omit non-critical columns (become —)
h.analysis(f"Answer first, every figure cited {m}.").gaps("- what, why, effect, source that would lift it")
```

## Rules the generator enforces

- Cells are strings: `_x` `"3.29x"`, `_pct` `"12.5%"`, `_bps` `"450"`, `_date` ISO, other figures plain decimals (`-` sign, no commas or brackets), `—` for a gap. Scale columns take the exact `rules.json` words. Placeholders (`tbd`, `n/a`, …) are refused.
- Critical columns are non-blank and `min_rows` holds unless `qa("Blocked")` (the tables and columns must still exist). A `cite` column holds `[C<n>]` markers or `calc: …`.
- Every `[C<n>]` resolves; every citation is cited; synthetic ones are `synthetic: true` with the TEST DATA source. A `compute()` string is recomputed by `check`.
- Sign convention in tables and the Model: outflows negative. `cp2d.bridge`: Delta and Use rows are signed, so Closing = Opening + Σ middle rows. `cp4c.recoveries`: residual = available − allocation; the fulcrum is the first class under 100%.
- `check(run)` also recomputes headroom (`cp4.covenant_tests`, `cp2h.rating_triggers`), funding gaps, runway tie-outs, Fit (§7) and `cp6` caps, the Model identities, real CZR cells against the base data, and requires every §11.4 chart whose tables the run has to carry data (`fixture.n_a_charts` lists the deliberate exceptions). A `RUNS` entry may also set `skip_reasons={step: reason}` for steps the plan skips. When CP-4C's distress gate is Not met, the critical cells of its four register tables may read `Gate not met` (interfaces §2.17; the only format exception).
- RBOT's methodology (interfaces spec) governs content; never reproduce legacy Deploy V registers or QA lists.
