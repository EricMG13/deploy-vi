# Mutation record — `rbot calc bond_analytics`

`scripts/mutation_workspace.py --only "src/rbotlib/calc/bond_analytics.py" --tests tests/test_bond_analytics.py tests/test_bond_analytics_detail.py`, then `mutmut run` (mutmut 3.7.0) in the printed workspace, 2026-10-11: 1004 mutants, 989 killed, 3 timed out (killed: each makes the yield bisection loop forever, `solve_yield` 1, 16, 21), 12 survived. Every survivor is below with why it is equivalent; a survivor of a later run that is not listed is a test gap to kill, never an entry to add. Entries read `` `<function>` <mutant numbers> `` (mutmut's `rbotlib.calc.bond_analytics.x_<function>__mutmut_<n>`).

- **E1** (6), `zip(..., strict=...)` over two three-element tuples the function builds itself, so `strict` never decides anything: `_loan_talk` 91, 94, 95; `_bond_talk` 94, 97, 98.
- **E2** (1), `sum` without its `Decimal(0)` start adds the same Decimals to the integer 0, which gives the same Decimal (the cash-flow list is never empty: a redemption date is always after settlement): `present_value` 9.
- **E3** (1), `while dates[-1] >= settle` on a settlement that is a coupon date adds that day as a cash-flow date with a full period's accrued interest; the coupon then appears in both the dirty price and the cash flows at time 0, so the yield is the same: `schedule` 4.
- **E4** (2), the bracket test `<=` turned `<` at either end differs only when the dirty price equals the value at exactly -50% or +500% to 38 digits: `solve_yield` 10, 11.
- **E5** (2), the bisection runs one more halving at a width of exactly the tolerance, or moves a midpoint whose value equals the target to 38 digits; both change the yield below 1e-14, under the 1e-6% the output keeps: `solve_yield` 17, 26.
