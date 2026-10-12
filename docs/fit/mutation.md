# Mutation record — Portfolio Fit arithmetic

`scripts/mutation_workspace.py --only "src/rbotlib/fit_arithmetic.py" --tests tests/test_fit_arithmetic.py tests/test_fit.py`, then `mutmut run` (mutmut 3.7.0) in the printed workspace, 2026-10-12: 781 mutants, 779 killed, 2 survived. A survivor of a later run that is not listed is a test gap to kill, never an entry to add.

- **E1** (1), the default of a dictionary lookup that is only tested for `None`: `needed = {"pct_nav": nav, "pct_par": par}.get(unit, 1)` turned `.get(unit, 2)`; any default that is not `None` says the same, "this unit needs no NAV or par": `headroom_row` 61.
- **E2** (1), `(r.headroom or 1) < 0` for `(r.headroom or 0) < 0`: a `From file` row always has a Decimal headroom (the limit less the file's current value), never `None`, and `Decimal(0) or 1` is 1, which is not below 0, as 0 is not: `concerns` 33.
