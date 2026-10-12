# Mutation record — Portfolio Fit arithmetic

`scripts/mutation_workspace.py --only "src/rbotlib/fit_arithmetic.py" --tests tests/test_fit_arithmetic.py tests/test_fit.py`, then `mutmut run` (mutmut 3.7.0) in the printed workspace, 2026-10-11: 478 mutants, 477 killed, 1 survived. A survivor of a later run that is not listed is a test gap to kill, never an entry to add.

- **E1** (1), `rating.strip().rstrip("*")` turned `rstrip("XX*XX")` strips `X` as well as `*` from the end of an agency rating; no Moody's, S&P or Fitch rating ends in `X`: `_bucket` 4.
